"""parse Valve220 quake .map files"""
# https://quakewiki.org/wiki/Quake_Map_Format
# https://developer.valvesoftware.com/wiki/MAP_(file_format)

import re
from dataclasses import dataclass, field
from typing import Any, NamedTuple

import src.app.bcolors as bcolors

verbose = False


def verbose_print(*args):
    if verbose:
        print(*args)


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


class QProp:
    def dumps(self) -> str:
        return ""

    @staticmethod
    def loads(string: str) -> Any:
        return QProp()

    def __repr__(self):
        return self.dumps()


class Point(NamedTuple):
    """X Y Z"""
    x: float
    y: float
    z: float

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def dumps(self):
        return " ".join([str(p) for p in self])

    @staticmethod
    def loads(string: str):
        points = PATTERN_NUMBER.findall(string)
        if len(points) == 3:
            return Point(*points)


@dataclass
class UvPoint:
    point: Point
    offset: float
    scale: float


class UV(NamedTuple):
    u: UvPoint
    v: UvPoint


class Points(NamedTuple):
    a: Point
    b: Point
    c: Point

    def __repr__(self):
        return f"{self.a} {self.b} {self.c}"


class Plane(QProp):
    def __init__(self, points: Points, texture_name: str, uv: UV, rotation: float):
        self.points = points
        self.texture_name = texture_name
        self.uv = uv
        self.rotation = rotation

    def __repr__(self):
        return f"Plane(Points({self.points}), {self.texture_name}, {self.uv}, {self.rotation})"

    def dumps(self) -> str:
        return f"( {self.points.a.dumps()} ) ( {self.points.b.dumps()} ) ( {self.points.c.dumps()} ) {self.texture_name} [ {self.uv.u.point.dumps()} {self.uv.u.offset} ] [ {self.uv.v.point.dumps()} {self.uv.v.offset} ] {self.rotation} {self.uv.u.scale} {self.uv.v.scale}"

    @staticmethod
    def loads(string: str) -> "Plane":
        return Plane.deconstruct_line(string)

    @staticmethod
    def deconstruct_line(line: str) -> "Plane":
        items = line.split()
        p_points = Points(
            Point(*[float(i) for i in items[1:4]]),
            Point(*[float(i) for i in items[6:9]]),
            Point(*[float(i) for i in items[11:14]]),
        )
        p_tex: str = items[15]
        p_uv = UV(
            UvPoint(
                Point(*[float(i) for i in items[17:20]]),
                float(items[20]),
                float(items[29]),
            ),
            UvPoint(
                Point(*[float(i) for i in items[23:26]]),
                float(items[26]),
                float(items[30]),
            ),
        )
        p_rotation = float(items[28])
        return Plane(points=p_points, texture_name=p_tex, uv=p_uv, rotation=p_rotation)


class Brush(QProp):
    def __init__(self, planes: list[Plane] = []):
        self.planes: list[Plane] = planes or []

    def dumps(self):
        return "{\n" + "\n".join(plane.dumps() for plane in self.planes) + "\n}"

    @staticmethod
    def loads(string: str) -> "Brush | None":
        plane_strings: list[str] = PATTERN_PLANE_IN_BRUSH.findall(string)
        planes: list[Plane] = [
            possible_plane
            for ps in plane_strings
            if (possible_plane := Plane.loads(ps))
        ]
        if planes:
            return Brush(planes)

    def __str__(self):
        return f"brush with {len(self.planes)} planes"


@dataclass
class KV(QProp, dict[str, str]):
    def dumps(self):
        return "\n".join([f'"{k}" "{v}"' for k, v in self.items()]) + "\n"

    @staticmethod
    def loads(string: str) -> "KV":
        found = PATTERN_KEY_VALUE_LINE.finditer(string)
        kvdict = KV()
        for m in found:
            groups = m.groups()
            kvdict |= {groups[0]: groups[1]}
        return kvdict


@dataclass
class Entity(QProp):
    brushes: list[Brush] = field(default_factory=list)
    kv: KV = field(default_factory=KV)

    def dumps(self):
        out = "{\n"
        if self.kv:
            out += self.kv.dumps()
        if self.brushes:
            out += "\n".join(brush.dumps() for brush in self.brushes)
        out += "\n}" if self.brushes else "}"
        return out

    @staticmethod
    def loads(string: str) -> "Entity":
        kv: KV = KV.loads(string)
        brushes_in_ent = PATTERN_BRUSHES_IN_ENT.findall(string)
        brushes = [
            possible_brush
            for brush in brushes_in_ent
            if (possible_brush := Brush.loads(brush))
        ]
        return Entity(kv=kv, brushes=brushes)

    @property
    def classname(self):
        return self.kv["classname"]

    @property
    def targetname(self):
        return self.kv.get("targetname")

    @property
    def target(self):
        return self.kv.get("target")

    # TODO move this out of this class
    def iterate(self, key: str, *, val: int = 1, set_to_val: bool = False) -> None:
        PLACEHOLDER = "@🐇@"
        possible_val = self.kv.get(key)
        if possible_val:
            num = get_num_in_key(possible_val)
            txt = str(possible_val).replace(str(num), PLACEHOLDER)
            if num:
                print(f"found {num} in {self.kv[key]}")
                if set_to_val:
                    num = val
                else:
                    num += val
                self.kv[key] = txt.replace(PLACEHOLDER, str(num))

    def __eq__(self, value: object) -> bool:
        return super().__eq__(value)


def parse_whole_map(text: str) -> list[Entity]:
    lines = text.splitlines()
    current_brush: Brush | None = None
    entities: list[Entity] = []
    depth = 0

    count = 0
    for line in lines:
        count += 1
        verbose_print(
            " ", f"{count: 5d}", depth, bcolors.colorize(line, bcolors.bcolors.OKBLUE)
        )
        match line[:1]:
            # entering an object
            case "{":
                depth += 1

                if depth == 1:
                    entities.append(Entity())
                elif depth == 2:
                    current_brush = Brush()

            # exiting an object
            case "}":
                depth -= 1
                if current_brush:
                    entities[-1].brushes.append(current_brush)

                current_brush = None

            case '"':
                k, v = line.split('"')[1::2]
                entities[-1].kv[k] = v

            case "(":
                if current_brush:
                    current_brush.planes.append(Plane.deconstruct_line(line))

    return entities
