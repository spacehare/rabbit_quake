import tomllib
import yaml
import re
from pathlib import Path
from src.app.bcolors import *
from src.app.parse import Entity
from src.app import deps


def get_cfg_file_contents():
    possible_cfgs = Path('cfg/').glob('settings.*')
    file_path: Path = (*possible_cfgs,)[0]
    print('found settings file at %s' % file_path)
    if file_path.suffix == '.toml':
        return tomllib.loads(file_path.read_text())
    elif file_path.suffix == '.yaml':
        return yaml.safe_load(file_path.open())

    exit()


_contents: dict = get_cfg_file_contents()

banned_chars = re.compile(r'[<>:"\\\/|?*]')

# https://github.com/spyoungtech/ahk/blob/main/ahk/keys.py
# https://www.autohotkey.com/docs/v2/Hotkeys.htm#Symbols
# https://www.autohotkey.com/docs/v2/KeyList.htm
AHK_KEY_DEFAULTS = {
    'compile': '!c',
    'launch': '!`',
    'iterate': '!v',
    'pc_close_loop': '!+v'
}


def _get_bind(dictionary: dict, key: str) -> str:
    return dictionary.get(key) or AHK_KEY_DEFAULTS[key]


def make_listpath(what) -> list[Path]:
    if type(what) is list:
        return [Path(d) for d in what]
    elif type(what) is str:
        return [*Path(what).iterdir()]
    else:
        raise TypeError(f'{what} of type {type(what)} is not list or str')


class Engine:
    def __init__(self, exe: Path):
        self.exe = exe
        self.folder = exe.parent
        self.name = self.folder.name
        self.mods = [item for item in self.folder.iterdir() if item.is_dir()]


class Keybinds:
    compile = _get_bind(_contents['keybinds'], 'compile')
    launch = _get_bind(_contents['keybinds'], 'launch')
    iterate = _get_bind(_contents['keybinds'], 'iterate')
    pc_close_loop = _get_bind(_contents['keybinds'], 'pc_close_loop')


def make_dependency_pattern(d: dict):
    # TODO this doesn't work recursively
    pass
    # if d.get('subpatterns'):
    #     which = d.get('which', '')
    #     condition = d.get('condition', '')
    #     what = d.get('what', '')
    #     _subpatterns_raw = d.get('subpatterns', [])
    #     patterns = [make_dependency_pattern(p) for p in _subpatterns_raw]
    #     pattern_type = d.get('subpattern_type', '')
    #     destination = d.get('destination')
    #     subpattern_anywhere_in_entity = d.get('subpattern_anywhere_in_entity', False)
    #     name = d.get('name', '')

    #     new_pattern = deps.Pattern(
    #         which=which,
    #         condition=condition,
    #         what=what,
    #         subpatterns=patterns,
    #         subpattern_type=pattern_type,
    #         destination=destination,
    #         subpattern_anywhere_in_entity=subpattern_anywhere_in_entity,
    #         name=name,
    #     )
    #     return new_pattern
    # else:
    #     return deps.Pattern(**d)


class Settings:
    # TODO this is so fucking ugly to look at. it does not spark joy
    _ericw = _contents['paths'].get('ericw')
    _engine_exes: list[Path] = make_listpath(
        _contents['paths'].get('engine_exes'))
    _raw_jampack_whitelist: list[dict] = _contents['jampack']['allow']

    name = _contents['name']
    trenchbroom = Path(_contents['paths'].get('trenchbroom'))
    trenchbroom_exe = trenchbroom / 'trenchbroom.exe'
    trenchbroom_prefs = Path(_contents['paths'].get(
        'trenchbroom_preferences'))
    engines: list[Engine] = list([Engine(Path(exe)) for exe in _engine_exes])
    configs = Path(_contents['paths'].get('configs'))
    maps_path = Path(_contents['paths'].get('maps'))
    maps: list[Path] = [p for p in maps_path.iterdir()]
    cfg_whitelist = _contents.get('cfg_whitelist') or {}
    submit_whitelist = _contents['submit']['allowed']
    # jampack_whitelist: list[Relationship] = []
    # for i in _raw_jampack_whitelist:
    #     jampack_whitelist.append(Relationship(
    #         dest=Path(i['destination']),
    #         patterns=i['patterns'],
    #         except_patterns=i.get('except_patterns', []),
    #         except_regexs=i.get('except_regexs', [])),
    #     )
    # dependencies = [deps.Pattern(**dict(p)) for p in _contents['dependencies']]
    # dependencies = []
    # for i in _contents['dependencies']:
    #     dependencies.append(make_dependency_pattern(i))


# https://ericwa.github.io/ericw-tools/doc/qbsp.html
# https://ericwa.github.io/ericw-tools/doc/vis.html
# https://ericwa.github.io/ericw-tools/doc/light.html
SVARS = {
    '{name}': Settings.name
}


def replace_var(what: str):
    output: str = ''
    for k, v in SVARS.items():
        output = what.replace(k, v)
    return output


class TemplateCopyPair:
    def __init__(self, files: list[Path | str], dest: Path):
        self.files: list[Path] = [Path(f) for f in files]
        self.dest: Path = Path(dest)


class Template:
    copy_list: list[TemplateCopyPair] = []
    for i in _contents['template'].get('copy'):
        copy_list.append(TemplateCopyPair(i['files'], Path(i['destination'])))
    folders: list[Path] = [Path(replace_var(p)) for p in _contents['template']['folders']]
