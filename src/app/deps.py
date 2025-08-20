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


class GroupTypes(StrEnum):
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


# @dataclass
# class PatternGroup:
#     group_type: GroupTypes
#     patterns: list[Pattern]


@dataclass(kw_only=True)
class Master:
    '''holds other patterns, and decides what to do with those patterns'''
    name: str
    destination: str
    output_patterns: list[Pattern]
    checks: list | None = None

    @staticmethod
    def from_dict(d: dict):
        checks: list = d.get('checks', [])
        name = d.get('name', 'unnamed pattern')
        dest: str = d['destination']
        outputs = [Pattern(**p['pattern']) for p in d['outputs']]

        if not any([checks, name, outputs]):
            print('could not create Master from dict')
            return
        else:
            return Master(
                name=name,
                destination=dest,
                output_patterns=outputs,
                checks=checks,
            )

    def get_keys_from_entity(self, ent: Entity, depth=0) -> list[str] | None:
        print('master:', self.name)

        output_keys = []

        if not self.output_patterns:
            print('master pattern needs at least one "output" pattern')

        for pattern in self.output_patterns:
            print(pattern)
            output_keys.extend(pattern.get_keys_from_entity(ent))

        if self.checks:
            print('found checks')
            results: list[bool] = []

            for check in self.checks:
                filter_keys: list[str] = []

                group_type: str = check['type']
                group_tags: list[str] = check['tags']
                group_patterns: list[Pattern] = [Pattern(**p['pattern']) for p in check['patterns']]

                for pattern in group_patterns:
                    keys = pattern.get_keys_from_entity(ent)
                    filter_keys.extend(keys)
                    print(keys)

                match group_type:
                    case GroupTypes.ALL:
                        pass
                    case GroupTypes.ANY:
                        pass

            # if the checks fail
            if not all(results):
                return None

        return output_keys
