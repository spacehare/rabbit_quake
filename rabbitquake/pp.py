"""preprocessor / postprocessor"""

import argparse
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from rabbitquake.app.bcolors import bcolors, colorize
from rabbitquake.app.parse import Brush, Entity, parse_whole_map

# inspired by...
# MESS
# see: https://developer.valvesoftware.com/wiki/MESS_(Macro_Entity_Scripting_System)
# see: https://pwitvoet.github.io/mess/
# see: https://github.com/pwitvoet/mess


CHAR_GENERAL_DEFAULT = "@"
CHAR_VAR_IN_DEFAULT = "${"
CHAR_VAR_OUT_DEFAULT = "}"
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


def find_and_replace(map_string: str, pp_cfg: PPConfig) -> str:
    # a regex pattern like r"%.+?%" could work, but this is simpler i think
    new_str: str = map_string
    print(colorize("FIND-AND-REPLACE VARIABLES", bcolors.UNDERLINE))
    for key, value in pp_cfg.variables.items():
        variable_sandwich = f"{pp_cfg.char_variable_in}{key}{pp_cfg.char_variable_out}"
        new_str = new_str.replace(variable_sandwich, str(value))
        print(f"  {variable_sandwich:<15} {colorize(value, bcolors.OKCYAN)}")
    return new_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", type=Path, help="the full path of the target map file")
    parser.add_argument(
        "output", type=Path, help="the full path of the to-be-created file"
    )
    parser.add_argument(
        "cfg_path", type=Path, nargs="?", help="the full path of the YAML config"
    )
    args = parser.parse_args()

    q_map_path: Path = args.map
    q_output_path: Path = args.output
    q_cfg_path: Path | None = args.cfg_path
    new_map_path = q_output_path

    print("==== STARTING pp.py ====")
    print(new_map_path)

    map_string = q_map_path.read_text()
    entities: list[Entity]
    final_ents: list[Entity] = []
    cfg: PPConfig

    if not map_string:
        raise ValueError("map string is empty")

    if q_cfg_path and q_cfg_path.exists():
        print('found cfg path at "%s"' % q_cfg_path.absolute())
        cfg: PPConfig = PPConfig.loads(q_cfg_path)
        map_string = find_and_replace(map_string, cfg)

        entities = parse_whole_map(map_string)
        # YAML scripts
        for script_path in cfg.scripts:
            # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
            actual_path = (q_cfg_path.parent / script_path).resolve()
            print("running %s" % actual_path)
            if spec := importlib.util.spec_from_file_location(
                actual_path.stem, actual_path
            ):
                module = importlib.util.module_from_spec(spec)
                sys.modules[actual_path.stem] = module
                if spec.loader:
                    spec.loader.exec_module(module)
                context = {"entities": entities, "var_prefix": cfg.char_general}
                output: list[Entity] = module.main(context)
                entities = output

        # in-YAML exec
        for action in cfg.actions:
            if ex := action.get("exec"):
                exec(ex)

    else:
        entities = parse_whole_map(map_string)

    if not entities:
        raise ValueError("output entity list is empty")

    new_map_path.touch()
    new_map_path.write_text("\n".join([ent.dumps() for ent in entities]))

    print("==== ENDING pp.py ====")
