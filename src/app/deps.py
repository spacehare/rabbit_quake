from pathlib import Path
from typing import NamedTuple, Literal
from collections import namedtuple
from dataclasses import dataclass, field
from src.app.parse import Entity, KV
from enum import StrEnum
from src.app.bcolors import colorize, bcolors


class Conditions(StrEnum):
    STARTSWITH = 'startswith'
    ENDSWITH = 'endswith'
    EQUALS = 'equals'


class PatternTypes(StrEnum):
    # AND = 'and'
    # OR = 'or'
    ANY = 'any'
    ALL = 'all'


@dataclass(kw_only=True)
class Pattern:
    which: str = ''
    condition: Conditions | str
    what: str | list[str] = ''

    def match(self, key: str, value: str):
        return match_pattern(key, value, self)


@dataclass(kw_only=True)
class Master:
    name: str
    destination: str
    checks: dict


def match_pattern(key: str, value: str, pattern: Pattern) -> bool:
    '''for a single key-value pair, check against a pattern'''

    # check if we are matching against a key or a value
    which = None
    match pattern.which:
        case 'key':
            which = key
        case 'value':
            which = value
        case _:
            return False

    # check if string
    if isinstance(pattern.what, str):
        match pattern.condition:
            case Conditions.STARTSWITH:
                return which.startswith(pattern.what)
            case Conditions.ENDSWITH:
                return which.endswith(pattern.what)
            case Conditions.EQUALS:
                return which == pattern.what

    # check if list
    elif isinstance(pattern.what, list):
        match pattern.condition:
            case Conditions.STARTSWITH:
                return which.startswith(tuple(pattern.what))
            case Conditions.ENDSWITH:
                return which.endswith(tuple(pattern.what))
            case Conditions.EQUALS:
                return which in pattern.what

    return False


def get_key(ent: Entity, master: Master, depth=0) -> str | None:
    matches = []
    output_result = None
    output_dict = None
    output_pattern: Pattern | None = None

    print('master:', master.name)
    output_dict = master.checks.get('output')
    if output_dict:
        output_pattern = Pattern(**output_dict.get('pattern'))

    if not output_pattern:
        print('each master pattern must have an "output" pattern')
        return

    for key, value in ent.kv.items():
        is_match = match_pattern(key, value, output_pattern)
        if is_match:
            output_result = key

    return output_result
