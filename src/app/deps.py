from pathlib import Path
from typing import NamedTuple, Literal
from collections import namedtuple
from dataclasses import dataclass, field
from src.app.parse import Entity, KV
from enum import StrEnum
from src.app.bcolors import colorize, bcolors


@dataclass(kw_only=True)
class Master:
    '''holds other patterns, and decides what to do with those patterns'''
    name: str
    destination: str
    str_eval: str = ""
    str_exec: str = ""

    @staticmethod
    def from_dict(d: dict) -> 'Master':
        return Master(
            name=d.get('name', 'unnamed pattern'),
            destination=d['destination'],
            str_eval=d.get('eval', ""),
            str_exec=d.get('exec', ""),
        )

    def check(self, entity: Entity) -> list[str] | str | None:
        context = {"entity": entity}
        assert not (self.str_eval and self.str_exec)

        if self.str_eval:
            return eval(self.str_eval, context)
        if self.str_exec:
            namespace = {}
            exec(self.str_exec, context, namespace)
            return namespace.get('output')
