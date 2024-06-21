from pathlib import Path
import argparse
from PIL import Image, ImageColor, ImagePalette, ImageFilter
from PIL.Image import Dither
from app.bcolors import *
import re
import app.palette as pal
from app.palette import palette_image_from_tuples

# TODO give warning when image is not div by 16
# TODO see wadcleaver
# TODO add max-string name check


PLACEHOLDER_RGB = (0, 255, 0)
PLACEHOLDER_RGBA_255 = (0, 255, 0, 255)
PLACEHOLDER_RGBA_0 = (0, 255, 0, 0)
TRANS_RGB = (159, 91, 83)
QUAKE_PALETTE_LIST = pal.QUAKE_RGB_TUPLES
NO_BRIGHTS_LIST = QUAKE_PALETTE_LIST[:224]
NO_BRIGHTS_WITH_TRANS_LIST = NO_BRIGHTS_LIST + [TRANS_RGB]

QUAKE_PALETTE_IMG = palette_image_from_tuples(QUAKE_PALETTE_LIST)
NO_BRIGHTS_IMG = palette_image_from_tuples(NO_BRIGHTS_LIST)
NO_BRIGHTS_WITH_TRANS_IMG = palette_image_from_tuples(NO_BRIGHTS_WITH_TRANS_LIST)

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

        img_opaque = palettize(img_opaque, NO_BRIGHTS_IMG)
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
