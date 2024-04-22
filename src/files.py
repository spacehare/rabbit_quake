# import tomllib
from typing import Any
import app_paths
from pathlib import Path
import tomllib
from enum import StrEnum


def get_contents(file_path: Path):
    return tomllib.loads(file_path.read_text())


settings_contents: dict = get_contents(app_paths.SETTINGS)
keybinds_contents: dict = get_contents(app_paths.KEYBINDS)


# https://github.com/spyoungtech/ahk/blob/main/ahk/keys.py
# https://www.autohotkey.com/docs/v2/Hotkeys.htm#Symbols
# https://www.autohotkey.com/docs/v2/KeyList.htm
DEFAULTS = {
    'compile': '!c',
    'launch': '!`',
    'pc_iterate': '!v',
    'pc_close_loop': '!+v'
}


def _get_bind(dictionary: dict, key: str):
    return dictionary.get(key) or DEFAULTS[key]


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
    def _get(self, what):
        return keybinds_contents.get(what)

    compile = _get_bind(settings_contents, 'compile')
    launch = _get_bind(settings_contents, 'launch')
    pc_iterate = _get_bind(settings_contents, 'pc_iterate')
    pc_close_loop = _get_bind(settings_contents, 'pc_close_loop')


class Settings:
    trenchbroom = Path(settings_contents['paths'].get('trenchbroom'))
    trenchbroom_exe = trenchbroom / 'trenchbroom.exe'
    trenchbroom_prefs = Path(settings_contents['paths'].get(
        'trenchbroom_preferences'))
    _ericw = settings_contents['paths'].get('ericw')
    _engine_exes: list[Path] = make_listpath(
        settings_contents['paths'].get('engine_exes'))
    engines = set([Engine(Path(exe)) for exe in _engine_exes])
    configs = Path(settings_contents['paths'].get('configs'))
    cfg_whitelist = settings_contents.get('cfg_whitelist')


class Ericw:
    light = Path('bin/light.exe')
    qbsp = Path('bin/qbsp.exe')
    vis = Path('bin/vis.exe')
    compilers: list[Path] = make_listpath(Settings._ericw)
