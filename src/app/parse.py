"""parse Valve220 quake .map files"""
# https://quakewiki.org/wiki/Quake_Map_Format
# https://developer.valvesoftware.com/wiki/MAP_(file_format)

from dataclasses import dataclass, field
from typing import NamedTuple


def to_number_string(f: float) -> str:
    return str(int(f) if f.is_integer() else f)


class Point(NamedTuple):
    """X Y Z"""
    x: float
    y: float
    z: float

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def dumps(self):
        return " ".join([to_number_string(p) for p in self])


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


class Plane:
    def __init__(self, points: Points, texture_name: str, uv: UV, rotation: float):
        self.points = points
        self.texture_name = texture_name
        self.uv = uv
        self.rotation = rotation

    def __repr__(self):
        return f"Plane(Points({self.points}), {self.texture_name}, {self.uv}, {self.rotation})"

    def dumps(self) -> str:
        a = self.points.a.dumps()
        b = self.points.b.dumps()
        c = self.points.c.dumps()
        return f"( {a} ) ( {b} ) ( {c} ) {self.texture_name} [ {self.uv.u.point.dumps()} {to_number_string(self.uv.u.offset)} ] [ {self.uv.v.point.dumps()} {to_number_string(self.uv.v.offset)} ] {to_number_string(self.rotation)} {to_number_string(self.uv.u.scale)} {to_number_string(self.uv.v.scale)}"

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

    loads = deconstruct_line


class Brush:
    def __init__(self, planes: list[Plane] = []):
        self.planes: list[Plane] = planes or []

    def dumps(self):
        return "{\n" + "\n".join(plane.dumps() for plane in self.planes) + "\n}"

    def __str__(self):
        return f"brush with {len(self.planes)} planes"


@dataclass
class KV(dict[str, str]):
    def dumps(self):
        return "\n".join([f'"{k}" "{v}"' for k, v in self.items()]) + "\n"


@dataclass
class Entity:
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
        return parse_whole_map(string)[0]

    @property
    def classname(self):
        return self.kv["classname"]

    @property
    def targetname(self):
        return self.kv.get("targetname")

    @property
    def target(self):
        return self.kv.get("target")

    def __eq__(self, value: object) -> bool:
        return super().__eq__(value)


def parse_whole_map(text: str) -> list[Entity]:
    lines = text.splitlines()
    current_brush: Brush | None = None
    entities: list[Entity] = []
    depth = 0

    for line in lines:
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

            # key-value pairs
            case '"':
                k, v = line.split('"')[1::2]
                entities[-1].kv[k] = v

            # planes
            case "(":
                if current_brush:
                    current_brush.planes.append(Plane.deconstruct_line(line))

    return entities
