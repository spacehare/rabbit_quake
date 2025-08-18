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
    ENTITY_HAS_PATTERNS = 'entity_has_patterns'


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


@dataclass
class Dependency:
    pattern: Pattern
    destination: Path


def find_value(ent: Entity | dict, pattern: Pattern) -> str | None:
    print('-----')

    search_ent: bool = pattern.condition == Conditions.ENTITY_HAS_PATTERNS
    keyvalues = ent.kv.items() if isinstance(ent, Entity) else ent.items()

    for k, v in keyvalues:

        # if there are sub-patterns
        if pattern.patterns:
            pattern_type = pattern.pattern_type
            value_list = []
            ok: bool = False
            for p_pattern in pattern.patterns:
                p_value = find_value(ent, p_pattern)
                value_list.append(p_value)
                print(p_pattern)
                print(p_value)

            match pattern_type:
                case PatternTypes.AND:
                    ok = all(value_list)
                case PatternTypes.OR:
                    ok = any(value_list)

            print('ok', ok)

            if ok:
                return value_list[0]

        # check key or value
        which = None
        if pattern.which == 'key':
            which = k
        elif pattern.which == 'value':
            which = v
        if not which:
            return None

        # check string
        if isinstance(pattern.what, str):
            match pattern.condition:
                case Conditions.STARTSWITH:
                    if which.startswith(pattern.what):
                        return v
                case Conditions.ENDSWITH:
                    if which.endswith(pattern.what):
                        return v
                case Conditions.EQUALS:
                    if which == pattern.what:
                        return v

        # check list
        elif isinstance(pattern.what, list):
            match pattern.condition:
                case Conditions.STARTSWITH:
                    if which.startswith(tuple(pattern.what)):
                        return v
                case Conditions.ENDSWITH:
                    if which.endswith(tuple(pattern.what)):
                        return v
                case Conditions.EQUALS:
                    if which in pattern.what:
                        return v
