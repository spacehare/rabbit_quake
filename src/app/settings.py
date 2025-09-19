import tomllib
import yaml
import re
from pathlib import Path
from src.app.bcolors import *
from src.app.parse import Entity
from .deps import Master
from dataclasses import dataclass, field


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


class Settings:
    # TODO this is so fucking ugly to look at. it does not spark joy
    _ericw = _contents['paths'].get('ericw')
    _engine_exes: list[Path] = make_listpath(
        _contents['paths'].get('engine_exes'))
    _raw_jampack_whitelist: list[dict] = _contents['jampack']['allow']
    jampack: dict = _contents['jampack']

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


S_MASTERS: list[Master] = [mas for d in _contents['dependencies'] if (mas := Master.from_dict(d))]


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


@dataclass
class Symlink:
    target: str
    destination: Path

    @staticmethod
    def from_dict(d: dict) -> 'Symlink':
        return Symlink(
            replace_var(d['target']),
            Path(replace_var(d['destination'])),
        )


symlinks: list[Symlink] = [Symlink.from_dict(item) for item in _contents['symlink']]


class TemplateCopyPair:
    def __init__(self, files: list[Path | str], dest: Path):
        self.files: list[Path] = [Path(f) for f in files]
        self.dest: Path = Path(dest)


class Template:
    copy_list: list[TemplateCopyPair] = []
    for i in _contents['template'].get('copy'):
        copy_list.append(TemplateCopyPair(i['files'], Path(i['destination'])))
    folders: list[Path] = [Path(replace_var(p)) for p in _contents['template']['folders']]
