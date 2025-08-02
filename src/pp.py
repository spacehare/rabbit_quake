'''preprocessor / postprocessor'''

from app.parse import parse, TBObject
from dataclasses import dataclass
import yaml
from pathlib import Path
import argparse

# TODO
# variables as KV pairs ex: $blue_light = 0 50 150
# autoclip illusionaries with like a "@clip 1" KV or something
# instanced vars within groups

FILENAME = 'pp.yaml'
PREFIX_GENERAL_DEFAULT = '@'
PREFIX_VARIABLE_DEFAULT = '$'


@dataclass
class PP:
    version: int = -1
    variables = {}
    '''key-value pairs to find-and-replace'''
    prefix_general: str = PREFIX_GENERAL_DEFAULT
    prefix_variable: str = PREFIX_VARIABLE_DEFAULT

    @staticmethod
    def loads(yaml_path: Path):
        loaded: dict = yaml.safe_load(yaml_path.open())
        print(loaded)
        new_pp = PP()
        new_pp.version = loaded['version']
        new_pp.variables = loaded.get('variables')
        return new_pp


def find_and_replace(map_string: str, pp_cfg: PP):
    new_str = map_string
    for kv in pp_cfg.variables.items():
        print(kv[0], kv[1], sep=' = ')
        new_str = new_str.replace(pp_cfg.prefix_variable + kv[0], kv[1])
    return new_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('map', type=Path,
                        help='the original map file')
    parser.add_argument('output_dir', type=Path,
                        help='where to put the new processed map file')
    args = parser.parse_args()

    q_map_path: Path = args.map
    q_dir_path: Path = args.output_dir
    new_map_path = q_dir_path / q_map_path.name
    print(new_map_path)

    cfg: PP = PP.loads(q_map_path.parent / FILENAME)
    map_string = q_map_path.read_text()

    processed_map_string = find_and_replace(map_string, cfg)

    new_map_path.touch()
    new_map_path.write_text(processed_map_string)
