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


class GroupTags(StrEnum):
    SAME_KEY = 'same_key'
    IN_ENT = 'in_ent'


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


@dataclass
class Check:
    c_type: GroupTypes
    tags: list[GroupTags]
    patterns: list[Pattern]

    def check(self, ent: Entity) -> bool:
        filter_keys: list[str] = []

        for pattern in self.patterns:
            keys = pattern.get_keys_from_entity(ent)
            filter_keys.extend(keys)

            print(keys)

        match self.c_type:
            case GroupTypes.ALL:
                pass
            case GroupTypes.ANY:
                pass

        # tags = check.get('tags')
        # if tags:
        #     # same_key
        #     same_key = filter_keys.count(filter_keys[0]) == len(filter_keys)

        #     # in_ent
        #     in_ent = len(filter_keys) == len(group_patterns)

        return False

    @staticmethod
    def from_dict(d: dict) -> 'Check':
        return Check(
            c_type=GroupTypes(d['type']),
            tags=[GroupTags(t) for t in d['tags']],
            patterns=[Pattern(**p['pattern']) for p in d['patterns']]
        )


@dataclass(kw_only=True)
class Master:
    '''holds other patterns, and decides what to do with those patterns'''
    name: str
    destination: str
    output_patterns: list[Pattern]
    checks: list[Check] | None = None

    @staticmethod
    def from_dict(d: dict) -> 'Master':
        checks = [Check.from_dict(c) for c in d.get('checks', [])]
        name = d.get('name', 'unnamed pattern')
        dest: str = d['destination']
        outputs = [Pattern(**p['pattern']) for p in d['outputs']]

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

        if self.checks:
            print('found checks')
            results: list[bool] = []

            for check in self.checks:
                v = check.check(ent)

            # if the checks fail
            if not all(results):
                return None

        # find outputs
        for pattern in self.output_patterns:
            print(pattern)
            keys = pattern.get_keys_from_entity(ent)
            output_keys.extend(keys)

        return output_keys
