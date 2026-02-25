"""preprocessor / postprocessor"""

import argparse
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from rabbitquake.app.bcolors import bcolors, colorize
from rabbitquake.app.parse import Entity, dumps, loads

# inspired by...
# MESS
# see: https://developer.valvesoftware.com/wiki/MESS_(Macro_Entity_Scripting_System)
# see: https://pwitvoet.github.io/mess/
# see: https://github.com/pwitvoet/mess


CHAR_GENERAL_DEFAULT = "@"
CHAR_VAR_IN_DEFAULT = "%"
CHAR_VAR_OUT_DEFAULT = "%"
CHAR_DICT_DEFAULT = {
    "general": CHAR_GENERAL_DEFAULT,
    "variable_in": CHAR_VAR_IN_DEFAULT,
    "variable_out": CHAR_VAR_OUT_DEFAULT,
}


@dataclass
class PPConfig:
    version: int = -1
    variables = {}
    """key-value pairs to find-and-replace"""
    char_general: str = CHAR_GENERAL_DEFAULT
    char_variable_in: str = CHAR_VAR_IN_DEFAULT
    char_variable_out: str = CHAR_VAR_OUT_DEFAULT
    actions: list[dict] = field(default_factory=list)
    scripts: list[Path] = field(default_factory=list[Path])

    @staticmethod
    def loads(yaml_path: Path) -> "PPConfig":
        loaded: dict = yaml.safe_load(yaml_path.open())
        new_pp = PPConfig()
        new_pp.version = loaded["config_version"]
        new_pp.variables = loaded.get("variables")
        prefix: dict = loaded.get("prefix", CHAR_DICT_DEFAULT)
        new_pp.char_general = prefix.get("general", CHAR_GENERAL_DEFAULT)
        new_pp.char_variable_in = prefix.get("variable_in", CHAR_VAR_IN_DEFAULT)
        new_pp.char_variable_out = prefix.get("variable_out", CHAR_VAR_OUT_DEFAULT)
        new_pp.actions = loaded.get("actions", [])
        new_pp.scripts = [Path(i) for i in loaded.get("scripts", [])]
        return new_pp


def run_script(path: Path, context: dict) -> list[Entity]:
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    print("running %s" % path.resolve())
    if (spec := importlib.util.spec_from_file_location(path.stem, path)) and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        output: list[Entity] = module.main(context)
        return output
    else:
        raise ValueError("spec failed to load!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", type=Path, help="path to input .map file")
    parser.add_argument("output", type=Path, help="path to output .map file")
    parser.add_argument("--cfg", type=Path, help="path to the config")
    parser.add_argument("--script", type=Path, help="path to main script")
    args = parser.parse_args()

    q_map_path: Path = args.map
    q_output_path: Path = args.output
    q_cfg_path: Path = args.cfg
    q_script_path: Path = args.script

    print("==== STARTING pp.py ====")

    map_string = q_map_path.read_text()
    entities: list[Entity]
    cfg: PPConfig | None = None

    if not map_string:
        raise ValueError("map string is empty")

    # external YAML config
    if q_cfg_path.exists():
        print('found cfg path at "%s"' % q_cfg_path.resolve())
        cfg = PPConfig.loads(q_cfg_path)

    entities = loads(map_string)
    worldspawn = entities[0]
    assert worldspawn.classname == "worldspawn"
    sym_gen_prefix = cfg.char_general if cfg else worldspawn.kv.get("__general_prefix") or CHAR_GENERAL_DEFAULT
    sym_var_prefix = cfg.char_variable_in if cfg else worldspawn.kv.get("__variable_prefix") or CHAR_VAR_IN_DEFAULT
    sym_var_suffix = cfg.char_variable_out if cfg else worldspawn.kv.get("__variable_suffix") or CHAR_VAR_IN_DEFAULT
    variables: dict = cfg.variables if cfg else {}

    # replace variables
    for key in worldspawn.kv:
        if key.startswith(sym_var_prefix):
            variables[key[1:-1]] = worldspawn.kv[key]
            print(f"  {key[1:-1]} = {worldspawn.kv[key]}")
    for ent in entities:
        for key in ent.kv:
            for var in variables:
                ent.kv[key] = ent.kv[key].replace(sym_var_prefix + var + sym_var_suffix, variables[var])

    ctx = {"entities": entities, "var_prefix": sym_gen_prefix}

    # run script from args
    if q_script_path.exists():
        run_script(q_script_path, ctx)

    # load script from path in worldspawn key
    elif script := worldspawn.kv.get("__script"):
        print("found script reference in worldspawn: %s" % script)
        script_path = Path(script)
        actual_path = (q_map_path.parent / script_path).resolve()
        run_script(actual_path, ctx)

    # assume filename based on stem
    elif (assumed_script := q_map_path.with_suffix(".py")) and assumed_script.exists():
        run_script(assumed_script, ctx)

    # clean up: delete keys to get rid of `developer 1` warnings
    for ent in entities:
        trash_list = [key for key in ent.kv if key.startswith(sym_gen_prefix)]
        for key in trash_list:
            del ent.kv[key]

    if not entities:
        raise ValueError("output entity list is empty")

    q_output_path.touch()
    q_output_path.write_text(dumps(entities))

    print("==== ENDING pp.py ====")
