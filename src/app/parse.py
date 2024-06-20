import re
from typing import Any
from collections import namedtuple
if __name__ == '__main__':
    verbose = True
    import bcolors
else:
    import app.bcolors as bcolors
    verbose = False


def verbose_print(*args):
    if verbose:
        print(*args)


'''parse Valve220 quake .map files'''

# TODO make this not terrible

r_num = re.compile(r'-?\b\d+\.?\d*(?:e-\d+)?\b')
r_plane = re.compile(rf'(?P<digit>{r_num.pattern})|(?P<texname>(?<=\) )\b.+?(?= \[))')

r_num_in_key = re.compile(r'(-?\d+\.?\d*(?:e-\d+)?)')
r_tex_name = re.compile(r'(?!\()(?<=\) )(.+?)(?= \[)')
r_plane_in_brush = re.compile(r'\([^{}\n]+[^\n]$', re.MULTILINE)
# r_plane_old = re.compile(r'(?P<digit>(-?\b\d+\.?\d*(?:e-\d+)?)\b)|(?P<texname>(?<=\) )\b.+?(?= \[))')
r_keyval = re.compile(r'\"(.+)\" \"(.+)\"', re.MULTILINE)
r_keyval_alt = r'([^\"]+)\"\s*\"([^\"]*)'
r_brushes_in_ent = re.compile(r'(?<=\{\n)[^\{]+(?=\n\})')

brace_pattern = re.compile(r'({|})')
key_value_pattern = re.compile(r'([^"]+)"\s*"([^"]*)')


def get_num_in_key(string: str, *, place=-1, force_int=True) -> float | int | None:
    m = r_num_in_key.findall(string)
    if m:
        out = m[place]
        return int(out) if force_int else float(out)


Vertex = namedtuple('Vertex', ['x', 'y', 'z'])


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
    def _loads2(string: str):
        numbers = r_num.findall(string)
        p_points = Points(Point(*numbers[0:3]), Point(*numbers[3:6]), Point(*numbers[6:9]))
        p_tex = r_tex_name.findall(string)[0]
        p_uv = UV(UvPoint(Point(*numbers[9:12]), numbers[12], numbers[18]), UvPoint(Point(*numbers[13:16]), numbers[16], numbers[19]))
        return Plane(p_points, p_tex, p_uv, numbers[17])

    @staticmethod
    def loads(string: str):
        searched = r_plane.finditer(string)
        group_list = [re_match.group() for re_match in searched]
        numbers = [float(item) for idx, item in enumerate(group_list) if idx != 9]
        p_tex = group_list[9]
        p_points = Points(Point(*numbers[0:3]), Point(*numbers[3:6]), Point(*numbers[6:9]))
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

    def __repr__(self):
        return str(self.kvdict)

    def dumps(self):
        return '\n'.join([f'"{k}" "{v}"' for k, v in self.kvdict.items()]) + '\n'

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
        # self.children = children

    def dumps(self):
        out = '{\n'
        out += self.kv.dumps()
        if self.brushes:
            out += '\n'.join(brush.dumps() for brush in self.brushes)
        out += '\n}' if self.brushes else '}'
        return out

    @staticmethod
    def loads(string: str):
        kv: KV = KV.loads(string)
        print('loads', kv.kvdict)
        brushes_in_ent = r_brushes_in_ent.findall(string)
        brushes = [possible_brush for brush in brushes_in_ent if (possible_brush := Brush.loads(brush))]
        return Entity(kv, brushes)

    @property
    def classname(self):
        return self.kv.kvdict['classname']

    @property
    def targetname(self):
        return self.kv.kvdict.get('targetname')

    @property
    def target(self):
        return self.kv.kvdict.get('target')

    def iterate(self, key: str, *, val: int = 1, set_to_val: bool = False) -> None:
        PLACEHOLDER = '@🐇@'
        possible_val = self.kv.kvdict.get(key)
        if possible_val:
            num = get_num_in_key(possible_val)
            txt = str(possible_val).replace(str(num), PLACEHOLDER)
            if num:
                print(f'found {num} in {self.kv.kvdict[key]}')
                if set_to_val:
                    num = val
                else:
                    num += val
                self.kv.kvdict[key] = txt.replace(PLACEHOLDER, str(num))


class QuakeMap(QProp):
    def __init__(self, kv: KV, brushes: list[Brush] | None, entities: list[Entity] | None):
        self.kv = kv
        self.brushes = brushes
        self.entities = entities

    @property
    def wad(self):
        return self.kv.kvdict['wad']

    @property
    def mod(self) -> str:
        return self.kv.kvdict['_tb_mod']

    @property
    def message(self):
        return self.kv.kvdict['message']

    @property
    def mapversion(self):
        return self.kv.kvdict['mapversion']

    @staticmethod
    def loads(string: str):
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
        return self.kv.get('classname')

    def __repr__(self):
        return f'{self.kv.get('classname')} ~ children: {len(self.children)}'


def parse(text: str) -> list[TBObject]:
    LINES = text.splitlines()
    root_level_objects: list[TBObject] = []
    stack = []
    current: TBObject | None = None
    for line in LINES:
        verbose_print('\t', bcolors.colorize(line, bcolors.bcolors.OKBLUE))
        match line[:1]:
            # entering an object
            case '{':
                new = TBObject()

                if current:
                    current.children.append(new)
                    stack.append(current)

                current = new

            # exiting an object
            case '}':
                if stack:
                    current = stack.pop()
                else:
                    if current:
                        root_level_objects.append(current)
                        current = None

            case '"':
                if current:
                    for k, v in key_value_pattern.findall(line):
                        current.kv[k] = v

            case '(':
                if current:
                    m = r_plane.search(line)
                    if m:
                        current.planes.append(Plane.loads(m.string))

            # case '/':
            #     if current:
            #         current.comment = line[3:]

    return root_level_objects


if __name__ == '__main__':
    ex = '''
// entity 0
{
"mapversion" "220"
"wad" "I:/Quake/Dev/wad/prototype_1_3.wad;I:/Quake/Dev/wad/makkon_trim_guide.wad;I:/Quake/Dev/wad/makkon_tech.wad;I:/Quake/Dev/wad/makkon_industrial.wad;I:/Quake/Dev/wad/makkon_concrete.wad;I:/Quake/Game/quakespasm-0.95.0_win64/rm1.1/rm_mechanics.wad"
"classname" "worldspawn"
"_tb_def" "external:I:/Quake/Game/quakespasm-0.95.0_win64/remobilize_test15/remobilize.fgd"
"message" "nascent myopia"
"style" "1"
"_wateralpha" ".4"
"reset_items" "2"
"_tb_mod" "remobilize_test15"
"worldtype" "2"
"_bounce" "1"
"_bouncescale" "1"
"_bouncecolorscale" "1"
"light" "60"
"_minlight_color" "255 237 255"
"_surflightsubdivision" "8"
// brush 0
{
( -640 128 160 ) ( -640 129 160 ) ( -640 128 161 ) 128_grey_1 [ 0 1 0 0 ] [ 0 0 -1 0 ] 0 1 1
( -640 64 160 ) ( -640 64 161 ) ( -639 64 160 ) 128_grey_1 [ 1.0000000000000002 0 0 64 ] [ 0 0 -1.0000000000000002 0 ] 0 1 1
( -640 128 160 ) ( -639 128 160 ) ( -640 129 160 ) 128_grey_1 [ 0 1.0000000000000002 0 0 ] [ -1.0000000000000002 0 0 -32 ] 0 1 1
( -448 384 192 ) ( -448 385 192 ) ( -447 384 192 ) 128_grey_1 [ 0 1.0000000000000002 0 0 ] [ 1.0000000000000002 0 0 64 ] 0 1 1
( -448 384 192 ) ( -447 384 192 ) ( -448 384 193 ) 128_grey_1 [ -1.0000000000000002 0 0 0 ] [ 0 0 -1.0000000000000002 0 ] 0 1 1
( -272 384 192 ) ( -272 384 193 ) ( -272 385 192 ) 128_grey_1 [ 0 1 0 0 ] [ 0 0 -1 0 ] 0 1 1
}
}

'''

    o = parse(ex)
    verbose_print(o)
