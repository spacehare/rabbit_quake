from pathlib import Path
import argparse
from PIL import Image, ImageColor, ImagePalette, ImageFilter
from PIL.Image import Dither
from bcolors import *
import re

# TODO give warning when image is not div by 16
# TODO see wadcleaver
# TODO add max-string name check


def palette_from_tuples(p: list):
    w = len(p)
    h = 1
    img = Image.new('P', (w, h))
    for x in range(w):
        for y in range(h):
            img.putpixel((x, y), p[x])
    return img


PLACEHOLDER_RGB = (0, 255, 0)
PLACEHOLDER_RGBA_255 = (0, 255, 0, 255)
PLACEHOLDER_RGBA_0 = (0, 255, 0, 0)
TRANS_RGB = (159, 91, 83)
QUAKE_PALETTE_LIST = [
    (0, 0, 0),
    (15, 15, 15),
    (31, 31, 31),
    (47, 47, 47),
    (63, 63, 63),
    (75, 75, 75),
    (91, 91, 91),
    (107, 107, 107),
    (123, 123, 123),
    (139, 139, 139),
    (155, 155, 155),
    (171, 171, 171),
    (187, 187, 187),
    (203, 203, 203),
    (219, 219, 219),
    (235, 235, 235),
    (15, 11, 7),
    (23, 15, 11),
    (31, 23, 11),
    (39, 27, 15),
    (47, 35, 19),
    (55, 43, 23),
    (63, 47, 23),
    (75, 55, 27),
    (83, 59, 27),
    (91, 67, 31),
    (99, 75, 31),
    (107, 83, 31),
    (115, 87, 31),
    (123, 95, 35),
    (131, 103, 35),
    (143, 111, 35),
    (11, 11, 15),
    (19, 19, 27),
    (27, 27, 39),
    (39, 39, 51),
    (47, 47, 63),
    (55, 55, 75),
    (63, 63, 87),
    (71, 71, 103),
    (79, 79, 115),
    (91, 91, 127),
    (99, 99, 139),
    (107, 107, 151),
    (115, 115, 163),
    (123, 123, 175),
    (131, 131, 187),
    (139, 139, 203),
    (1, 1, 0),
    (7, 7, 0),
    (11, 11, 0),
    (19, 19, 0),
    (27, 27, 1),
    (35, 35, 1),
    (43, 43, 7),
    (47, 47, 7),
    (55, 55, 7),
    (63, 63, 7),
    (71, 71, 7),
    (75, 75, 11),
    (83, 83, 11),
    (91, 91, 11),
    (99, 99, 11),
    (107, 107, 15),
    (7, 0, 0),
    (15, 0, 0),
    (23, 0, 0),
    (31, 0, 0),
    (39, 0, 0),
    (47, 0, 0),
    (55, 0, 0),
    (63, 0, 0),
    (71, 0, 0),
    (79, 0, 0),
    (87, 0, 0),
    (95, 0, 0),
    (103, 0, 0),
    (111, 0, 0),
    (119, 0, 0),
    (127, 0, 0),
    (19, 19, 0),
    (27, 27, 0),
    (35, 35, 0),
    (47, 43, 0),
    (55, 47, 0),
    (67, 55, 0),
    (75, 59, 7),
    (87, 67, 7),
    (95, 71, 7),
    (107, 75, 11),
    (119, 83, 15),
    (131, 87, 19),
    (139, 91, 19),
    (151, 95, 27),
    (163, 99, 31),
    (175, 103, 35),
    (35, 19, 7),
    (47, 23, 11),
    (59, 31, 15),
    (75, 35, 19),
    (87, 43, 23),
    (99, 47, 31),
    (115, 55, 35),
    (127, 59, 43),
    (143, 67, 51),
    (159, 79, 51),
    (175, 99, 47),
    (191, 119, 47),
    (207, 143, 43),
    (223, 171, 39),
    (239, 203, 31),
    (255, 243, 27),
    (11, 7, 0),
    (27, 19, 0),
    (43, 35, 15),
    (55, 43, 19),
    (71, 51, 27),
    (83, 55, 35),
    (99, 63, 43),
    (111, 71, 51),
    (127, 83, 63),
    (139, 95, 71),
    (155, 107, 83),
    (167, 123, 95),
    (183, 135, 107),
    (195, 147, 123),
    (211, 163, 139),
    (227, 179, 151),
    (171, 139, 163),
    (159, 127, 151),
    (147, 115, 135),
    (139, 103, 123),
    (127, 91, 111),
    (119, 83, 99),
    (107, 75, 87),
    (95, 63, 75),
    (87, 55, 67),
    (75, 47, 55),
    (67, 39, 47),
    (55, 31, 35),
    (43, 23, 27),
    (35, 19, 19),
    (23, 11, 11),
    (15, 7, 7),
    (187, 115, 159),
    (175, 107, 143),
    (163, 95, 131),
    (151, 87, 119),
    (139, 79, 107),
    (127, 75, 95),
    (115, 67, 83),
    (107, 59, 75),
    (95, 51, 63),
    (83, 43, 55),
    (71, 35, 43),
    (59, 31, 35),
    (47, 23, 27),
    (35, 19, 19),
    (23, 11, 11),
    (15, 7, 7),
    (219, 195, 187),
    (203, 179, 167),
    (191, 163, 155),
    (175, 151, 139),
    (163, 135, 123),
    (151, 123, 111),
    (135, 111, 95),
    (123, 99, 83),
    (107, 87, 71),
    (95, 75, 59),
    (83, 63, 51),
    (67, 51, 39),
    (55, 43, 31),
    (39, 31, 23),
    (27, 19, 15),
    (15, 11, 7),
    (111, 131, 123),
    (103, 123, 111),
    (95, 115, 103),
    (87, 107, 95),
    (79, 99, 87),
    (71, 91, 79),
    (63, 83, 71),
    (55, 75, 63),
    (47, 67, 55),
    (43, 59, 47),
    (35, 51, 39),
    (31, 43, 31),
    (23, 35, 23),
    (15, 27, 19),
    (11, 19, 11),
    (7, 11, 7),
    (255, 243, 27),
    (239, 223, 23),
    (219, 203, 19),
    (203, 183, 15),
    (187, 167, 15),
    (171, 151, 11),
    (155, 131, 7),
    (139, 115, 7),
    (123, 99, 7),
    (107, 83, 0),
    (91, 71, 0),
    (75, 55, 0),
    (59, 43, 0),
    (43, 31, 0),
    (27, 15, 0),
    (11, 7, 0),
    (0, 0, 255),
    (11, 11, 239),
    (19, 19, 223),
    (27, 27, 207),
    (35, 35, 191),
    (43, 43, 175),
    (47, 47, 159),
    (47, 47, 143),
    (47, 47, 127),
    (47, 47, 111),
    (47, 47, 95),
    (43, 43, 79),
    (35, 35, 63),
    (27, 27, 47),
    (19, 19, 31),
    (11, 11, 15),
    (43, 0, 0),
    (59, 0, 0),
    (75, 7, 0),
    (95, 7, 0),
    (111, 15, 0),
    (127, 23, 7),
    (147, 31, 7),
    (163, 39, 11),
    (183, 51, 15),
    (195, 75, 27),
    (207, 99, 43),
    (219, 127, 59),
    (227, 151, 79),
    (231, 171, 95),
    (239, 191, 119),
    (247, 211, 139),
    (167, 123, 59),
    (183, 155, 55),
    (199, 195, 55),
    (231, 227, 87),
    (127, 191, 255),
    (171, 231, 255),
    (215, 255, 255),
    (103, 0, 0),
    (139, 0, 0),
    (179, 0, 0),
    (215, 0, 0),
    (255, 0, 0),
    (255, 243, 147),
    (255, 247, 199),
    (255, 255, 255),
    (159, 91, 83),
]
NO_BRIGHTS = QUAKE_PALETTE_LIST[:224]
NO_BRIGHTS_WITH_TRANS = NO_BRIGHTS + [TRANS_RGB]

QUAKE_PALETTE_LIST = palette_from_tuples(QUAKE_PALETTE_LIST)
NO_BRIGHTS = palette_from_tuples(NO_BRIGHTS)
NO_BRIGHTS_WITH_TRANS = palette_from_tuples(NO_BRIGHTS_WITH_TRANS)

TEX_MAX_CHARS = 16
TEX_SIZE_MOD = 16
PRE_TRANS = '{'
PRE_WATER = '*'
PRE_ANIMATED = '+'
PRE_TOGGLE = '+A'
PRE_SKY = 'sky'
R_NUM_STEM_SUFFIX = re.compile(r'(.*?)(\d+$)')


def get_files(path: Path):
    return [f for f in path.iterdir() if f.is_file()]


def alpha_to_pink(img: Image.Image, alpha_cutoff=254):
    w, h = img.size
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.getpixel((x, y))
            if a < alpha_cutoff:
                img.putpixel((x, y), TRANS_RGB + (a,))
    return img


def palettize(img: Image.Image, palette: Image.Image):
    img = img.convert('RGB')
    colors = palette.getcolors()
    if colors:
        img = img.quantize(colors=len(colors), palette=palette, dither=Dither.NONE)
    return img


def split_pink(img: Image.Image):
    '''takes 1 RGB image, returns 2 RGBA images'''
    if img.mode != 'RGB':
        raise TypeError('image must be RGB')
    img_ex: Image.Image = Image.new('RGBA', img.size, color=PLACEHOLDER_RGBA_0)
    img_opaque: Image.Image = img_ex.copy()
    img_trans: Image.Image = img_ex.copy()

    w, h = img.size
    for x in range(w):
        for y in range(h):
            pixel = img.getpixel((x, y))
            (img_trans if pixel == TRANS_RGB else img_opaque).putpixel((x, y), pixel)

    return img_opaque, img_trans


def pad_zeroes_in_stem_int(img_path: Path, zero_count: int = 3):
    search = re.search(R_NUM_STEM_SUFFIX, img_path.stem)
    groups = search.groups() if search else None
    if groups:
        padded = f'{groups[0]}{groups[1].zfill(zero_count)}'
        return Path(img_path.parent, padded + img_path.suffix)
    return img_path


def is_img_quake_trans(img: Image.Image):
    colors = img.getcolors()
    if colors:
        for color in colors:
            if img.mode == 'RGB':
                if color[1] == TRANS_RGB:
                    return True
            else:
                raise TypeError('image must be RGB')

    return False


def prepend_trans(img_path: Path, img: Image.Image):
    if img_path.is_file() and not img_path.name.startswith(PRE_TRANS):
        return Path(img_path.parent, PRE_TRANS + img_path.name)
    return img_path


def prepend(file: Path, prefix: str):
    underscore = '_' if not prefix.endswith('_') else ''
    return Path(file.parent, f'{prefix}{underscore}{file.name}')


def batch_rm_dupes(folder: Path):
    for file in get_files(folder):
        print(file)


def remove_alpha_channel(img: Image.Image):
    return img.convert('RGB')


def resize(img: Image.Image, scale=2):
    return img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)


def wadpack():
    pass


def fix(img_path: Path, out_img_folder: Path, prefix: str = '', *, zeroes=3, alpha_cutoff):
    with Image.open(img_path) as img:
        name = out_img_folder / img_path.name

        # alter image
        img = img.convert('RGBA')
        img = alpha_to_pink(img, alpha_cutoff)
        img = remove_alpha_channel(img)

        img_opaque, img_trans = split_pink(img)
        # img_trans.save(name.parent / (name.stem + '_TRANS' + name.suffix))
        # img_opaque.save(name.parent / (name.stem + '_OPAQUE' + name.suffix))

        img_opaque = palettize(img_opaque, NO_BRIGHTS)
        img_trans = img_trans.convert('RGBA')
        img_opaque = img_opaque.convert('RGBA')

        img = Image.alpha_composite(img_opaque, img_trans)
        img = remove_alpha_channel(img)

        # TODO i dont need to save BEFORE renaming, just do the operations on the stem and then save
        # alter image file path name
        img.save(name)

        new_name = name
        if prefix:
            new_name = prepend(new_name, prefix)
        if is_img_quake_trans(img):
            print('TRANS!!!!!!!')
            # TODO prepend_trans isnt working :( :(
            new_name = prepend_trans(new_name, img)
        new_name = pad_zeroes_in_stem_int(new_name, zeroes)
        return name.rename(new_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', type=Path)
    parser.add_argument('output_path', type=Path)
    parser.add_argument('--prepend', action='store_true')
    parser.add_argument('--rmdupes', action='store_true')
    parser.add_argument('--rmalpha', action='store_true')
    parser.add_argument('--add_trans_prefix', action='store_true')
    parser.add_argument('--fix', '-f', action='store_true')
    parser.add_argument('--prefix', '-p', help='prefix to prepend to each image')
    parser.add_argument('--scale', type=int, help='scale image by this multiplier')
    parser.add_argument('--zeroes', '-z', type=int, help='how many zeroes to prepend to numbers')
    parser.add_argument('--alpha_cutoff', '-a', type=int, help='below this alpha value will turn pink')
    args = parser.parse_args()

    input = args.input_path
    output = args.output_path

    print('INPUT ', colorize(input, bcolors.OKBLUE))
    print('OUTPUT', colorize(output, bcolors.OKBLUE))
    if input.is_dir():
        for f in get_files(input):
            if args.scale:
                fimg = Image.open(f)
                result = resize(fimg, args.scale)
                result.save(output / f.name)
                fimg.close()

    if args.fix:
        # if args.fix.is_file():
        #     fix(input, output)
        if input.is_dir():
            for file in get_files(input):
                print(file)
                finished = fix(file, output, prefix=args.prefix, zeroes=args.zeroes or 3, alpha_cutoff=254)
                print(Ind.mark(), finished)
