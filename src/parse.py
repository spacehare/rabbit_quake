import re
from typing import Any

'''parse Valve220 quake .map files'''

_ex_brush_str = '''
{
( -1024 696 16 ) ( -1024 696 17 ) ( -1024 695 16 ) clip [ -1.8369701987210297e-16 1 0 8 ] [ 0 0 -1 8 ] 180 1 1
( -1024 772 16 ) ( -1025 772 16 ) ( -1024 772 17 ) clip [ -1 -1.8369701987210297e-16 0 -32 ] [ 0 0 -1 8 ] 0 1 1
( -1016 840 8 ) ( -1017 840 8 ) ( -1016 839 8 ) clip [ -1.8369701987210297e-16 1 0 8 ] [ 1 1.8369701987210297e-16 0 32 ] 270 1 1
( -1024 696 124 ) ( -1024 695 124 ) ( -1025 696 124 ) clip [ 1.8369701987210297e-16 -1 0 -8 ] [ 1 1.8369701987210297e-16 0 32 ] 90 1 1
( -1016 828 8 ) ( -1016 828 9 ) ( -1017 828 8 ) clip [ 1 1.8369701987210297e-16 0 32 ] [ 0 0 -1 8 ] 0 1 1
( -1020 840 8 ) ( -1020 839 8 ) ( -1020 840 9 ) clip [ 1.8369701987210297e-16 -1 0 -8 ] [ 0 0 -1 8 ] 180 1 1
}
'''

# https://github.com/joshuaskelly/vgio/blob/master/vgio/quake/map.py
# https://developer.valvesoftware.com/wiki/MAP_(file_format)
r_num = re.compile(r'\b(-?\d+\.?\d*(?:e-\d+)?)\b')
r_tex = re.compile(r'(?!\()(?<=\) )(.+?)(?= \[) \[ (.+?) \] \[ (.+?) \] (.+)')
r_plane_in_brush = re.compile(r'^[^{}\n]+$', re.MULTILINE)
r_plane = re.compile(r'# (?P<digit>\b-?\d+\d*\b)|(?P<texname>(?<=\) )\b.+?(?= \[))')


class QProp:
    def dumps(self) -> str:
        return ''

    @staticmethod
    def loads(string: str) -> Any:
        return QProp()


class QFloat:
    def __init__(self, value: float):
        self._value = round(value, 6)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = round(new_value, 6)


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


class UV(QProp):
    def __init__(self, point: Point, offset: float):
        self.point = point
        self.offset = offset

    def dumps(self):
        return f'[ {self.point.dumps()} {self.offset} ]'

    @staticmethod
    def loads(string: str):
        values = r_num.findall(string)
        if len(values) == 4:
            return UV(Point(*values[0:3]), values[3])


class Face(QProp):
    '''x1, y1, z1, x2, etc'''

    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def __repr__(self):
        return f"Face({self.a}, {self.b}, {self.c})"

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.c

    def dumps(self):
        return f'( {self.a.dumps()} ) ( {self.b.dumps()} ) ( {self.c.dumps()} )'

    @staticmethod
    def loads(string: str):
        values = r_num.findall(string)
        a = values[:3]
        b = values[3:6]
        c = values[6:9]
        return Face(Point(*a), Point(*b), Point(*c))


class Scale():
    def __init__(self, u: float, v: float):
        pass


class Texture(QProp):
    def __init__(self, name: str, u: UV, v: UV, rot_scale: Point):
        self.name = name
        self.u = u
        self.v = v
        self.rotation = rot_scale.x
        self.scale = [rot_scale.y, rot_scale.z]

    def dumps(self):
        return f'{self.name} [ {self.u} ] [ {self.v} ] {self.rotation} {self.scale[0]} {self.scale[1]}'

    @staticmethod
    def loads(string: str):
        m = r_tex.search(string)
        if m:
            groups = m.groups()
            name = groups[0]
            u = UV.loads(groups[1])
            v = UV.loads(groups[2])
            rot_scale = Point.loads(groups[3])
            if name and u and v and rot_scale:
                return Texture(name, u, v, rot_scale)


class Plane(QProp):
    def __init__(self, face: Face, texture: Texture):
        self.face = face
        self.texture = texture

    def __repr__(self):
        return f'Plane({self.face}, {self.texture})'

    def dumps(self):
        return f'{self.face.dumps()} {self.texture.dumps()}'

    @staticmethod
    def loads(string: str):
        face = Face.loads(string)
        texture = Texture.loads(string)
        if face and texture:
            return Plane(face=face, texture=texture)


class Brush(QProp):
    def __init__(self, planes: list[Plane]):
        self.planes = planes

    def dumps(self):
        out: str = '{\n'
        for plane in self.planes:
            out += str(plane)
        out += '\n}'
        return out

    def __repr__(self):
        return f'Brush([{self.planes}])'

    @staticmethod
    def loads(string: str):
        plane_strings: list[str] = r_plane_in_brush.findall(string)
        planes: list[Plane] = [o for p in plane_strings if (o := Plane.loads(p))]
        if planes:
            return Brush(planes)


class Entity(QProp):
    pass


if __name__ == '__main__':
    a = Brush.loads(_ex_brush_str)
    if a:
        print(a, '\n', a.dumps())
