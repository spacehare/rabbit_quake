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
    ELSEWHERE_IN_ENT = 'elsewhere_in_ent'


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
        groups = [p.get_keys_from_entity(ent) for p in self.patterns]
        print('GROUPS:', groups)

        ok = []

        if self.tags:
            for tag in self.tags:
                match tag:
                    case GroupTags.SAME_KEY:
                        if len(groups) > 1:
                            counts: list[int] = [0] * len(groups[0])

                            for idx, key in enumerate(groups[0]):
                                print('~~>', key)
                                for group in groups[1:]:
                                    for k in group:
                                        if k == key:
                                            counts[idx] += 1

                            print('cts', counts)
                            count_matches_group_size: bool = False
                            for count in counts:
                                if count == len(groups[0]):
                                    count_matches_group_size = True
                                    break
                            ok.append(count_matches_group_size)
                        else:
                            ok.append(True)
                    case GroupTags.ELSEWHERE_IN_ENT:
                        result = len(groups) == len(self.patterns)
                        ok.append(result)

        match self.c_type:
            case GroupTypes.ALL:
                ok.append(all(groups))
            case GroupTypes.ANY:
                ok.append(any(groups))

        print('ok_list:', ok)
        return all(ok)

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

        if not self.output_patterns:
            print('master pattern needs at least one "output" pattern')

        if self.checks:
            results: list[bool] = [c.check(ent) for c in self.checks]

            # if the checks fail
            if not all(results):
                return None

        output_keys = []
        # find outputs
        for pattern in self.output_patterns:
            keys = pattern.get_keys_from_entity(ent)
            output_keys.extend(keys)

        return output_keys
