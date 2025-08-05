'''preprocessor / postprocessor'''

from app.parse import parse, TBObject
from app.bcolors import colorize, bcolors
from dataclasses import dataclass
import yaml
from pathlib import Path
import argparse
# import app.parse as p
# p.verbose = True

# TODO
# variables as KV pairs ex: $blue_light = 0 50 150
# autoclip illusionaries with like a "@clip 1" KV or something
# instanced vars within groups

# inspired by...
# MESS
# see: https://developer.valvesoftware.com/wiki/MESS_(Macro_Entity_Scripting_System)
# see: https://pwitvoet.github.io/mess/
# see: https://github.com/pwitvoet/mess


CHAR_GENERAL_DEFAULT = '@'
CHAR_VAR_IN_DEFAULT = '${'
CHAR_VAR_OUT_DEFAULT = '}'
CHAR_DICT_DEFAULT = {
    'general': CHAR_GENERAL_DEFAULT,
    'variable_in': CHAR_VAR_IN_DEFAULT,
    'variable_out': CHAR_VAR_OUT_DEFAULT,
}


@dataclass
class PPConfig:
    version: int = -1
    variables = {}
    '''key-value pairs to find-and-replace'''
    char_general: str = CHAR_GENERAL_DEFAULT
    char_variable_in: str = CHAR_VAR_IN_DEFAULT
    char_variable_out: str = CHAR_VAR_OUT_DEFAULT

    @staticmethod
    def loads(yaml_path: Path):
        loaded: dict = yaml.safe_load(yaml_path.open())
        new_pp = PPConfig()
        new_pp.version = loaded['version']
        new_pp.variables = loaded.get('variables')
        prefix: dict = loaded.get('prefix', CHAR_DICT_DEFAULT)
        new_pp.char_general = prefix.get('general', CHAR_GENERAL_DEFAULT)
        new_pp.char_variable_in = prefix.get('variable_in', CHAR_VAR_IN_DEFAULT)
        new_pp.char_variable_out = prefix.get('variable_out', CHAR_VAR_OUT_DEFAULT)
        return new_pp


def find_and_replace(map_string: str, pp_cfg: PPConfig):
    # a regex pattern like r"%.+?%" could work, but this is simpler i think
    new_str = map_string
    print(colorize('FIND AND REPLACE VARIABLES', bcolors.UNDERLINE))
    for kv in pp_cfg.variables.items():
        variable_sandwich = f'{pp_cfg.char_variable_in}{kv[0]}{pp_cfg.char_variable_out}'
        new_str = new_str.replace(variable_sandwich, kv[1])
        print(f'{variable_sandwich:<15} {colorize(kv[1], bcolors.OKCYAN)}')
    return new_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('map', type=Path,
                        help='the full path of the target map file')
    parser.add_argument('output', type=Path,
                        help='the full path of the to-be-created file')
    parser.add_argument('cfg_path', type=Path, help='the full path of the YAML config')
    args = parser.parse_args()

    q_map_path: Path = args.map
    q_output: Path = args.output
    q_cfg: Path = args.cfg_path
    new_map_path = q_output
    print(new_map_path)

    cfg: PPConfig = PPConfig.loads(q_cfg)
    map_string = q_map_path.read_text()

    quake_map = parse(map_string)
    for o in quake_map:
        print('--->', colorize(o, bcolors.OKBLUE))

    if cfg.variables:
        map_string = find_and_replace(map_string, cfg)

        new_map_path.touch()
        new_map_path.write_text(map_string)
