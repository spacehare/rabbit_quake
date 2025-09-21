import math
import argparse

# makkon textures are 512 x 512


class RightTriangle:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.c = math.sqrt(a**2 + b**2)

    def __str__(self):
        return f"{self.a}, {self.b}, {self.c}"


class Shape:
    def __init__(self, objects: list):
        self.objects = objects
        self.sides: list = []
        for o in self.objects:
            if isinstance(o, RightTriangle):
                self.sides.append(o.c)
            elif type(o) is int or type(o) is float:
                self.sides.append(o)
        self.perimeter = sum(self.sides)

    def get_x_scale(self, texture_width: int, truncate=True):
        scale = self.perimeter / texture_width
        return f"{scale:.6f}" if truncate else scale


if __name__ == "__main__":
    # czg8s_128u = Shape([*[RightTriangle(16, 48)] * 8])
    # czg12s_128u = Shape([*[32] * 4,
    #                     *[RightTriangle(16, 32)] * 8])
    # czg12s_256u = Shape([*[64] * 4,
    #                     *[RightTriangle(32, 64)] * 8])  # 1.118033988749895, 71.55417527999327
    # czg24s_512u = Shape([*[64] * 4,  # 1
    #                     *[RightTriangle(16, 64)] * 8,  # 1.0307764064044151
    #                     *[RightTriangle(32, 64)] * 8,  # 1.118033988749895
    #                     *[RightTriangle(48, 48)] * 4,  # 1.0606601717798212
    #                      ])

    def display(text, shape: Shape, width):
        print(
            text,
            len(shape.sides),
            "x scale",
            shape.get_x_scale(width),
            f"div: {width}",
            sep="\t",
        )

    # display('czg8s_128u', czg8s_128u, 512)  # seamless
    # display('czg12s_128u', czg12s_128u, 512)  # seamless
    # display('czg12s_256u', czg12s_256u, 1024)  # seamless
    # display('czg12s_256u', czg12s_256u, 64 * 13)  # closer to 1
    # display('czg24s_512u', czg24s_512u, 64 * 24)  # seamless, 1.059713

    parser = argparse.ArgumentParser()
    parser.add_argument("--texture-res", "-r", type=int)
    parser.add_argument("--triangles", "-t", help="[a, b, number of sides]", nargs="+")
    parser.add_argument("--flats", "-f", help="[a, number of sides]", nargs="+")
    args = parser.parse_args()
    texture_res: int = args.texture_res

    raw_tris = list(zip(*(iter(args.triangles or []),) * 3))
    raw_flats = list(zip(*(iter(args.flats or []),) * 2))

    triangles = []
    flats = []

    for tri in raw_tris:
        a = int(tri[0])
        b = int(tri[1])
        num = int(tri[2])

        for i in range(num):
            triangles.append(RightTriangle(a, b))

    for flat in raw_flats:
        a = int(flat[0])
        num = int(flat[1])

        for i in range(num):
            flats.append(a)

    shape = Shape(triangles + flats)

    display("->", shape, args.texture_res or 512)
