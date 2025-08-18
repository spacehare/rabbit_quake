from pathlib import Path
from typing import NamedTuple, Literal
from collections import namedtuple
from dataclasses import dataclass, field
from src.app.parse import Entity, KV
from enum import StrEnum


class Conditions(StrEnum):
    STARTSWITH = 'startswith'
    ENDSWITH = 'endswith'
    EQUALS = 'equals'


class PatternTypes(StrEnum):
    AND = 'and'
    OR = 'or'


@dataclass(kw_only=True)
class Pattern:
    which: str = ''
    condition: Conditions | str
    what: str | list[str] = ''
    patterns: list['Pattern'] = field(default_factory=list)
    pattern_type: PatternTypes | str = ''
    destination: str | None = None
    in_entity: bool = False


@dataclass
class MatchOutput:
    key: str
    value: str
    entity: Entity


def deal_with_subpatterns(ent: Entity, pattern: Pattern):
    in_ent: bool = pattern.in_entity

    if pattern.patterns:
        pattern_type = pattern.pattern_type
        value_list = []
        ok: bool = False

        for p_pattern in pattern.patterns:
            mt = find_match(ent, p_pattern)
            value_list.append(mt)
            if mt:
                print(mt.key, mt.value)

        match pattern_type:
            case PatternTypes.AND:
                ok = all(value_list)
            case PatternTypes.OR:
                ok = any(value_list)

        print('ok', ok)

        return value_list[0] if ok else None


def find_true(key: str, value: str, pattern: Pattern) -> bool:
    '''for a key-value pair, check against a pattern'''

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


def find_match(ent: Entity, pattern: Pattern) -> MatchOutput | None:
    subpattern_output = deal_with_subpatterns(ent, pattern)
    if subpattern_output:
        return subpattern_output

    for k, v in ent.kv.items():
        outcome = find_true(k, v, pattern)
        if outcome:
            return MatchOutput(k, v, ent)

    return None
