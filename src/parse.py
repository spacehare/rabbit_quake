import re
from typing import Any

'''parse Valve220 quake .map files'''


# https://github.com/joshuaskelly/vgio/blob/master/vgio/quake/map.py
# https://developer.valvesoftware.com/wiki/MAP_(file_format)
r_num = re.compile(r'\b(-?\d+\.?\d*(?:e-\d+)?)\b')
r_tex_name = re.compile(r'(?!\()(?<=\) )(.+?)(?= \[)')
r_plane_in_brush = re.compile(r'\([^{}\n]+[^\n]$', re.MULTILINE)
r_plane = re.compile(r'# (?P<digit>\b-?\d+\d*\b)|(?P<texname>(?<=\) )\b.+?(?= \[))')
r_keyval = re.compile(r'\"(.+)\" \"(.+)\"$', re.MULTILINE)
r_brushes_in_ent = re.compile(r'(?<=\{\n)[^\{]+(?=\n\})')


class QProp:
    def dumps(self) -> str:
        return ''

    @staticmethod
    def loads(string: str) -> Any:
        return QProp()

    def __repr__(self):
        return self.dumps()


class Point(QProp):
    '''X Y Z'''

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
        return (' '.join([str(p) for p in self]))

    @staticmethod
    def loads(string: str):
        points = r_num.findall(string)
        if len(points) == 3:
            return (Point(*points))


class UvPoint():
    def __init__(self, point: Point, offset: float, scale: float):
        self.point = point
        self.offset = offset
        self.scale = scale


class UV():
    def __init__(self, u: UvPoint, v: UvPoint):
        self.u = u
        self.v = v

    def __iter__(self):
        yield self.u
        yield self.v


class Points():
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.c

    def __repr__(self):
        return f'{self.a} {self.b} {self.c}'


class Plane(QProp):
    def __init__(self, points: Points, texture_name: str, uv: UV, rotation: float):
        self.points = points
        self.texture_name = texture_name
        self.uv = uv
        self.rotation = rotation

    def __repr__(self):
        return f'Plane(Points({self.points}), {self.texture_name}, {self.uv}, {self.rotation})'

    def dumps(self):
        return f'( {self.points.a.dumps()} ) ( {self.points.b.dumps()} ) ( {self.points.c.dumps()} ) {self.texture_name} [ {self.uv.u.point.dumps()} {self.uv.u.offset} ] [ {self.uv.v.point.dumps()} {self.uv.v.offset} ] {self.rotation} {self.uv.u.scale} {self.uv.v.scale}'

    @staticmethod
    def loads(string: str):
        numbers = r_num.findall(string)
        p_points = Points(Point(*numbers[0:3]), Point(*numbers[3:6]), Point(*numbers[6:9]))
        p_tex = r_tex_name.findall(string)[0]
        p_uv = UV(UvPoint(Point(*numbers[9:12]), numbers[12], numbers[18]), UvPoint(Point(*numbers[13:16]), numbers[16], numbers[19]))
        return Plane(p_points, p_tex, p_uv, numbers[17])


class Brush(QProp):
    def __init__(self, planes: list[Plane]):
        self.planes = planes

    def dumps(self):
        return '{\n' + '\n'.join(str(plane.dumps()) for plane in self.planes) + '\n}'

    @staticmethod
    def loads(string: str):
        plane_strings: list[str] = r_plane_in_brush.findall(string)
        planes: list[Plane] = [possible_plane for ps in plane_strings if (possible_plane := Plane.loads(ps))]
        if planes:
            return Brush(planes)


class KV(QProp):
    def __init__(self, kvdict: dict):
        self.kvdict = kvdict

    def dumps(self):
        return '\n'.join([f'"{k}" "{v}"' for k, v in self.kvdict.items()])

    def __repr__(self):
        return str(self.kvdict)

    @staticmethod
    def loads(string: str):
        found = r_keyval.finditer(string)
        kvdict = {}
        for m in found:
            groups = m.groups()
            kvdict |= {groups[0]: groups[1]}
        return KV(kvdict)


class Entity(QProp):
    def __init__(self, kv: KV, brushes: list[Brush] | None = None):
        self.kv = kv
        self.brushes = brushes

    def dumps(self):
        out = '{\n'
        out += self.kv.dumps()
        if self.brushes:
            out += '\n'.join(brush.dumps() for brush in self.brushes)
        out += '\n}'
        return out

    @staticmethod
    def loads(string: str):
        kv: KV = KV.loads(string)
        brushes_in_ent = r_brushes_in_ent.findall(string)
        brushes = [possible_brush for brush in brushes_in_ent if (possible_brush := Brush.loads(brush))]
        return Entity(kv, brushes)
