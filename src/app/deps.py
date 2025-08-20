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

    def get_truth_from_pair(self, key: str, value: str) -> bool:
        '''for a single key-value pair, check against a pattern'''
        # check if we are matching against a key or a value
        which = None
        match self.which:
            case 'key':
                which = key
            case 'value':
                which = value
            case _:
                return False

        # check if string
        if isinstance(self.what, str):
            match self.condition:
                case Conditions.STARTSWITH:
                    return which.startswith(self.what)
                case Conditions.ENDSWITH:
                    return which.endswith(self.what)
                case Conditions.EQUALS:
                    return which == self.what

        # check if list
        elif isinstance(self.what, list):
            match self.condition:
                case Conditions.STARTSWITH:
                    return which.startswith(tuple(self.what))
                case Conditions.ENDSWITH:
                    return which.endswith(tuple(self.what))
                case Conditions.EQUALS:
                    return which in self.what

        return False

    def get_keys_from_entity(self, ent: Entity) -> list[str]:
        '''for a whole entity, find a list of matching keys'''
        results: list[str] = []
        for key, value in ent.kv.items():
            if self.get_truth_from_pair(key, value):
                results.append(key)
        return results


@dataclass(kw_only=True)
class Master:
    name: str
    destination: str
    checks: dict

    def get_keys_from_entity(self, ent: Entity, depth=0) -> list[str] | None:
        print('master:', self.name)

        matches = []
        output_dict: dict | None = None
        output_pattern: Pattern | None = None
        # output_result_key: str | None = None

        output_dict = self.checks.get('output')
        if output_dict:
            output_pattern = Pattern(**output_dict.get('pattern'))

        if not output_pattern:
            print('each master pattern must have an "output" pattern')
            return

        keys = output_pattern.get_keys_from_entity(ent)

        return keys
        # return output_result_key
