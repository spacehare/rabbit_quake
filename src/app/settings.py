import tomllib
import re
import app.paths as paths
from pathlib import Path
from app.bcolors import *
from app.parse import TBObject


def get_contents(file_path: Path):
    return tomllib.loads(file_path.read_text())


_contents: dict = get_contents(paths.SETTINGS)

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


class JampackRelationship:
    def __init__(self, *, dest: Path, patterns: list[str], except_patterns=None, except_regexs=None):
        self.dest = dest
        self.patterns = patterns
        self.except_patterns = except_patterns
        self.except_regexs = except_regexs


class JampackDependencyPattern:
    # TODO this class doesn't make sense being here, but i also don't want a circular import
    def __init__(self, *,
                 classnames: list[str] | None = None,
                 keys: list[str] | None = None,
                 keys_regexs: list[str] | None = None,
                 value_patterns: list[str] | None = None,
                 value_regexs: str | None = None,
                 stem_append: str | None = None,
                 stem_prepend: str | None = None,
                 dest: Path | None = None
                 ):
        # if no keys to filter, search every entity
        self.keys = keys
        self.keys_regex = keys_regexs
        self.value_patterns = value_patterns
        self.stem_append = stem_append
        self.stem_prepend = stem_prepend
        self.value_regex = value_regexs
        self.classnames = classnames
        self.dest = dest

    def get_dependency_patterns(self, tb_object: TBObject):
        dependency_patterns: list[str] = []
        self.stem_append = self.stem_append or ''
        self.stem_prepend = self.stem_prepend or ''

        # dependencies will be found in the values of the key/value pairs
        for k, v in tb_object.kv.items():
            ok_keys = self.keys == None
            ok_value_patterns = self.value_patterns == None

            # classname
            if not (self.classnames == None or bool(self.classnames and tb_object.classname in self.classnames)):
                return

            # keys
            if self.keys:
                if k in self.keys:  # don't break, one entity might have multiple key matches. like a monster with a custom .mdl and .wav
                    ok_keys = True

            if self.value_patterns:
                for pattern in self.value_patterns:
                    if Path(v).match(pattern):
                        ok_value_patterns = True

            if all([ok_keys, ok_value_patterns]):
                p = Path(v)
                out_path = f'{self.stem_prepend}{p.stem}{self.stem_append}{p.suffix}'
                dependency_patterns.append(str(p.parent / out_path))

        if dependency_patterns:
            # print(colorize(set(dependency_patterns), bcolors.OKGREEN))
            return set(dependency_patterns)


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
    jampack_whitelist: list[JampackRelationship] = []
    for i in _raw_jampack_whitelist:
        jampack_whitelist.append(JampackRelationship(
            dest=i['destination'],
            patterns=i['patterns'],
            except_patterns=i.get('except_patterns'),
            except_regexs=i.get('except_regexs')),
        )
    jampack_patterns: list[JampackDependencyPattern] = []
    for p in _contents['jampack']['dependencies']:
        p = dict(p)
        new = JampackDependencyPattern(
            keys=p.get('keys'),
            keys_regexs=p.get('keys_regexs'),
            value_patterns=p.get('value_patterns'),
            value_regexs=p.get('value_regexs'),
            stem_append=p.get('stem_append'),
            stem_prepend=p.get('stem_prepend'),
            classnames=p.get('classnames'),
            dest=p.get('destination'),
        )
        jampack_patterns.append(new)


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
    def __init__(self, files: list[Path], dest: Path):
        self.files: list[Path] = [Path(f) for f in files]
        self.dest: Path = Path(dest)


class Template:
    copy_list: list[TemplateCopyPair] = []
    for i in _contents['template'].get('copy'):
        copy_list.append(TemplateCopyPair(i['files'], i['destination']))
    folders: list[Path] = [Path(replace_var(p)) for p in _contents['template']['folders']]
