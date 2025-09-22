import re
import tomllib
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import yaml

from src.app.bcolors import *
from src.app.parse import Entity

from .deps import DependencyData


def get_cfg_file_contents():
    possible_cfgs = Path("cfg/").glob("settings.*")
    file_path: Path = (*possible_cfgs,)[0]
    print("found settings file at %s" % file_path)
    if file_path.suffix == ".toml":
        return tomllib.loads(file_path.read_text())
    elif file_path.suffix == ".yaml":
        return yaml.safe_load(file_path.open())

    exit()


_contents: dict = get_cfg_file_contents()


def _get_bind(dictionary: dict, key: str) -> str:
    return dictionary.get(key) or AHK_KEY_DEFAULTS[key]


def make_listpath(what) -> list[Path]:
    if type(what) is list:
        return [Path(d) for d in what]
    elif type(what) is str:
        return [*Path(what).iterdir()]
    else:
        raise TypeError(f"{what} of type {type(what)} is not list or str")


class Engine:
    def __init__(self, exe: Path):
        self.exe = exe
        self.folder = exe.parent
        self.name = self.folder.name
        self.mods = [item for item in self.folder.iterdir() if item.is_dir()]


class Keybinds:
    compile = _get_bind(_contents["keybinds"], "compile")
    launch = _get_bind(_contents["keybinds"], "launch")
    iterate = _get_bind(_contents["keybinds"], "iterate")
    pc_close_loop = _get_bind(_contents["keybinds"], "pc_close_loop")


class Settings:
    # TODO this is so fucking ugly to look at. it does not spark joy
    _ericw = _contents["paths"].get("ericw")
    _engine_exes: list[Path] = make_listpath(_contents["paths"].get("engine_exes"))
    _raw_jampack_whitelist: list[dict] = _contents["jampack"]["allow"]
    jampack: dict = _contents["jampack"]

    name = _contents["name"]
    trenchbroom = Path(_contents["paths"].get("trenchbroom"))
    trenchbroom_exe = trenchbroom / "trenchbroom.exe"
    trenchbroom_prefs = Path(_contents["paths"].get("trenchbroom_preferences"))
    engines: list[Engine] = list([Engine(Path(exe)) for exe in _engine_exes])
    configs = Path(_contents["paths"].get("configs"))
    maps_path = Path(_contents["paths"].get("maps"))
    maps: list[Path] = [p for p in maps_path.iterdir()]
    cfg_whitelist = _contents.get("cfg_whitelist") or {}
    submit_whitelist = _contents["submit"]["allowed"]


SVARS = {"{name}": Settings.name}


def replace_var(what: str, replacements: dict = SVARS):
    output: str = ""
    for k, v in replacements.items():
        output = what.replace(k, v)
    return output


@dataclass
class Symlink:
    target: str
    destination: Path

    @staticmethod
    def from_dict(d: dict) -> "Symlink":
        return Symlink(
            replace_var(d["target"]),
            Path(replace_var(d["destination"])),
        )


@dataclass
class TemplateCopyPair:
    file: Path
    destination: Path

    @staticmethod
    def from_dict(d: dict) -> "TemplateCopyPair":
        file = Path(replace_var(d["file"]))
        destination = Path(replace_var(d["destination"]))

        return TemplateCopyPair(file, destination)


@dataclass
class Template:
    touch: list[str] = field(default_factory=list)
    copy_pairs: list[TemplateCopyPair] = field(default_factory=list)

    @staticmethod
    def from_dict(d: dict) -> "Template":
        touch = [replace_var(e) for e in d.get("touch", [])]
        copy_pairs = [TemplateCopyPair.from_dict(e) for e in d.get("copy", [])]

        return Template(touch, copy_pairs)


class PatternMode(StrEnum):
    PATH = "path"
    REGEX = "regex"


@dataclass
class Pattern:
    mode: PatternMode
    text: str

    @staticmethod
    def from_pair(d: dict) -> "Pattern | None":
        for k, v in d.items():
            return Pattern(PatternMode(k), v)

    def check(self, path: Path) -> bool:
        match self.mode:
            case PatternMode.PATH:
                result = path.match(self.text)
                return result
            case PatternMode.REGEX:
                result = re.search(self.text, str(path))
                return bool(result)


@dataclass
class PatternParent:
    patterns: list[Pattern]
    destination: str

    @staticmethod
    def from_dict(d: dict) -> "PatternParent":
        dest = d["destination"]
        patterns = [
            pattern for pair in d["patterns"] if (pattern := Pattern.from_pair(pair))
        ]
        return PatternParent(patterns, dest)


@dataclass
class Jampack:
    deny: list[Pattern]
    allow: list[PatternParent]

    @staticmethod
    def from_dict(d: dict) -> "Jampack":
        deny = [pattern for entry in d["deny"] if (pattern := Pattern.from_pair(entry))]
        allow = []
        for parent in d["allow"]:
            patterns = [
                pattern
                for pair in parent["patterns"]
                if (pattern := Pattern.from_pair(pair))
            ]
            pattern_parent = PatternParent(patterns, parent["destination"])
            allow.append(pattern_parent)

        if allow and deny:
            return Jampack(deny=deny, allow=allow)
        else:
            raise ValueError("invalid Jampack data.")


# https://github.com/spyoungtech/ahk/blob/main/ahk/keys.py
# https://www.autohotkey.com/docs/v2/Hotkeys.htm#Symbols
# https://www.autohotkey.com/docs/v2/KeyList.htm
AHK_KEY_DEFAULTS = {
    "compile": "!c",
    "launch": "!`",
    "iterate": "!v",
    "pc_close_loop": "!+v",
}
banned_chars = re.compile(r'[<>:"\\\/|?*]')
symlinks: list[Symlink] = [Symlink.from_dict(item) for item in _contents["symlink"]]
template: Template = Template.from_dict(_contents["template"])
jampack: Jampack = Jampack.from_dict(_contents["jampack"])
S_MASTERS: list[DependencyData] = [
    mas for d in _contents["dependencies"] if (mas := DependencyData.from_dict(d))
]
