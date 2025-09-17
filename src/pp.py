'''preprocessor / postprocessor'''

import copy
import argparse
from pathlib import Path
import yaml
from dataclasses import dataclass
from src.app.bcolors import colorize, bcolors
from src.app.parse import parse_whole_map, Brush, Entity

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
    print(colorize('FIND-AND-REPLACE VARIABLES', bcolors.UNDERLINE))
    for key, value in pp_cfg.variables.items():
        variable_sandwich = f'{pp_cfg.char_variable_in}{key}{pp_cfg.char_variable_out}'
        new_str = new_str.replace(variable_sandwich, value)
        print(f'{variable_sandwich:<15} {colorize(value, bcolors.OKCYAN)}')
    return new_str


# TODO: make this work with notrace too
# TODO: make this more generic. instead of "clip" make a more general function
# instead of "@clip: 1" it could be like "@add: clip" maybe
def clip(ent: Entity):
    output_brushes: list[Brush] = []
    for brush in ent.brushes:
        clone = copy.deepcopy(brush)
        for l in clone.planes:
            l.texture_name = 'clip'
        output_brushes.append(clone)
    return output_brushes


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
    map_string = find_and_replace(map_string, cfg)

    ents: list[Entity] = parse_whole_map(map_string)
    new_ents: list[Entity] = []
    new_str = ''
    for ent in ents:
        for key, value in ent.kv.items():
            if key.startswith('@') and int(value) == 1:
                if key == cfg.char_general + 'clip':
                    print(f'clipping {ent.classname}')
                    new_brushes = clip(ent)
                    print(len(new_ents[0].brushes))
                    new_ents[0].brushes.extend(new_brushes)
                    print(len(new_ents[0].brushes))
                if (key == cfg.char_general + 'delete') and int(value) == 1:
                    print(f'deleting {ent.classname}')
                    break
        else:
            new_ents.append(ent)

    for ent in new_ents:
        new_str += ent.dumps() + '\n'

    new_map_path.touch()
    new_map_path.write_text(new_str)
