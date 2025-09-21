"""parse Valve220 quake .map files"""
# https://quakewiki.org/wiki/Quake_Map_Format
# https://developer.valvesoftware.com/wiki/MAP_(file_format)

import re
from typing import Any
from dataclasses import dataclass, field
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


class Point(QProp):
    """X Y Z"""

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def dumps(self):
        return " ".join([str(p) for p in self])

    @staticmethod
    def loads(string: str):
        points = PATTERN_NUMBER.findall(string)
        if len(points) == 3:
            return Point(*points)


class UvPoint:
    def __init__(self, point: Point, offset: float, scale: float):
        self.point = point
        self.offset = offset
        self.scale = scale


class UV:
    def __init__(self, u: UvPoint, v: UvPoint):
        self.u = u
        self.v = v

    def __iter__(self):
        yield self.u
        yield self.v


class Points:
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.c

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

    def dumps(self):
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
        return "{\n" + "\n".join(str(plane.dumps()) for plane in self.planes) + "\n}"

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
class KV(QProp, dict[str, Any]):
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


# used in tb.py
class QuakeMap(QProp):
    def __init__(
        self, kv: KV, brushes: list[Brush] | None, entities: list[Entity] | None
    ):
        self.kv = kv
        self.brushes = brushes
        self.entities = entities

    @property
    def wad(self):
        return self.kv["wad"]

    @property
    def mod(self) -> str:
        return self.kv["_tb_mod"]

    @property
    def message(self):
        return self.kv["message"]

    @property
    def mapversion(self):
        return self.kv["mapversion"]

    @staticmethod
    def loads(string: str) -> "QuakeMap":
        kv: KV = KV.loads(string)
        return QuakeMap(kv, [], [])


class TBObject:
    def __init__(self, kv: dict = {}, children: list = [], planes: list[Plane] = []):
        self.kv = kv or {}
        self.children = children or []
        self.planes = planes or []
        # self.comment = comment or ''

    @property
    def classname(self):
        return self.kv.get("classname", "Brush?")

    def __str__(self):
        return f"{self.classname} ({len(self.children)})"


def parse(text: str) -> list[TBObject]:
    LINES = text.splitlines()
    root_level_objects: list[TBObject] = []
    stack = []
    current = None

    for line in LINES:
        verbose_print("\t", bcolors.colorize(line, bcolors.bcolors.OKBLUE))
        match line[:1]:
            # entering an object
            case "{":
                new = TBObject()

                if current:
                    current.children.append(new)
                    stack.append(current)

                current = new

            # exiting an object
            case "}":
                if stack:
                    current = stack.pop()
                else:
                    if current:
                        root_level_objects.append(current)
                        current = None

            case '"':
                if current:
                    for k, v in PATTERN_KEY_VALUE_LINE.findall(line):
                        current.kv[k] = v

            case "(":
                if current:
                    current.planes.append(Plane.deconstruct_line(line))

            # case '/':
            #     if current:
            #         current.comment = line[3:]

    return root_level_objects


def parse_whole_map(text: str) -> list[Entity]:
    LINES = text.splitlines()
    root_entities: list[Entity] = []
    current_ent: Entity | None = None
    current_brush: Brush | None = None
    depth = 0

    count = 0
    for line in LINES:
        count += 1
        verbose_print(
            " ", f"{count: 5d}", depth, bcolors.colorize(line, bcolors.bcolors.OKBLUE)
        )
        match line[:1]:
            # entering an object
            case "{":
                depth += 1

                if depth == 1:
                    current_ent = Entity()
                elif depth == 2:
                    current_brush = Brush()

            # exiting an object
            case "}":
                depth -= 1

                if current_brush and current_ent:
                    current_ent.brushes.append(current_brush)

                if depth == 0 and current_ent:
                    root_entities.append(current_ent)
                    current_ent = None

                current_brush = None

            case '"':
                if current_ent:
                    for k, v in PATTERN_KEY_VALUE_LINE.findall(line):
                        current_ent.kv[k] = v

            case "(":
                if current_brush:
                    current_brush.planes.append(Plane.deconstruct_line(line))

    return root_entities
