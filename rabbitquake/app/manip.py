import re

from .parse import Entity

PATTERN_NUMBER = re.compile(r"-?\b\d+\.?\d*(?:e-\d+)?\b")
PATTERN_NUMBER_IN_KEY = re.compile(r"(-?\d+\.?\d*(?:e-\d+)?)")
PATTERN_PLANE_IN_BRUSH = re.compile(r"\([^{}\n]+[^\n]$", re.MULTILINE)
PATTERN_KEY_VALUE_LINE = re.compile(r'^"(.*)" "(.*)"$', re.MULTILINE)
PATTERN_BRUSHES_IN_ENT = re.compile(r"(?<=\{\n)[^\{]+(?=\n\})")


def get_num_in_key(string: str, *, place=-1, force_int=True) -> float | int | None:
    m = PATTERN_NUMBER_IN_KEY.findall(string)
    if m:
        out = m[place]
        return int(out) if force_int else float(out)


def iterate(ent: Entity, key: str, *, val: int = 1, set_to_val: bool = False) -> None:
    PLACEHOLDER = "@🐇@"
    possible_val = ent.kv.get(key)
    if possible_val:
        num = get_num_in_key(possible_val)
        txt = str(possible_val).replace(str(num), PLACEHOLDER)
        if num:
            print(f"found {num} in {ent.kv[key]}")
            if set_to_val:
                num = val
            else:
                num += val
            ent.kv[key] = txt.replace(PLACEHOLDER, str(num))
