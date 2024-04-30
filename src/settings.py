from ericw import Compiler
import paths
from pathlib import Path
import tomllib
import re
import subprocess
from bcolors import *


def get_contents(file_path: Path):
    return tomllib.loads(file_path.read_text())


settings_contents: dict = get_contents(paths.SETTINGS)

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
    compile = _get_bind(settings_contents['keybinds'], 'compile')
    launch = _get_bind(settings_contents['keybinds'], 'launch')
    iterate = _get_bind(settings_contents['keybinds'], 'iterate')
    pc_close_loop = _get_bind(settings_contents['keybinds'], 'pc_close_loop')


class Settings:
    name = settings_contents['name']
    trenchbroom = Path(settings_contents['paths'].get('trenchbroom'))
    trenchbroom_exe = trenchbroom / 'trenchbroom.exe'
    trenchbroom_prefs = Path(settings_contents['paths'].get(
        'trenchbroom_preferences'))
    _ericw = settings_contents['paths'].get('ericw')
    _engine_exes: list[Path] = make_listpath(
        settings_contents['paths'].get('engine_exes'))
    engines: list[Engine] = list([Engine(Path(exe)) for exe in _engine_exes])
    configs = Path(settings_contents['paths'].get('configs'))
    maps_path = Path(settings_contents['paths'].get('maps'))
    maps: list[Path] = [p for p in maps_path.iterdir()]
    cfg_whitelist = settings_contents.get('cfg_whitelist') or {}


# class Tool:
#     def __init__(self, exe: Path):
#         self.exe = exe


# https://ericwa.github.io/ericw-tools/doc/qbsp.html
# https://ericwa.github.io/ericw-tools/doc/vis.html
# https://ericwa.github.io/ericw-tools/doc/light.html




class EricwProfile:
    def __init__(self, name: str, qbsp_params: list[str] | None, vis_params: list[str] | None, light_params: list[str] | None):
        self.name = name
        self.qbsp_params = qbsp_params or []
        self.vis_params = vis_params or []
        self.light_params = light_params or []
        print(f'({__name__}), creating profile {self.name}')

    @staticmethod
    def from_dict(d: dict):
        return EricwProfile(d['name'], d.get('qbsp'), d.get('vis'), d.get('light'))




class Ericw:
    bsp_dir: Path = Path(settings_contents['ericw']['bsp'])
    src_dir: Path = Path(settings_contents['ericw']['src'])
    compilers: list[Compiler] = [Compiler(path=comp_path) for comp_path in make_listpath(Settings._ericw)]
    profiles: list[EricwProfile] = [EricwProfile.from_dict(prof) for prof in settings_contents['ericw']['profiles']]


class Submit:
    allowed = settings_contents['submit']['allowed']
    denied = settings_contents['submit']['denied']


SVARS = {
    '{name}': Settings.name
}


def replace_var(what: str):
    output: str = ''
    for k, v in SVARS.items():
        output = what.replace(k, v)
    return output


class Template:
    folders: list[Path] = [Path(replace_var(p)) for p in settings_contents['template']['folders']]
