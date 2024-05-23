'''split a skybox image into 6 TGA images'''

from PIL import Image
import os
from pathlib import Path
import argparse

path2___ = os.path.abspath("") + "/"


def processImage(path: Path, iwidth=4, iheight=3):
    img = Image.open(path)
    if not (img.size[0] % 2 == 0 & img.size[1] % 2 == 0):
        print('image size not divisble by 2')
        return
    width: int = int(img.size[0] / iwidth)
    height: int = int(img.size[1] / iheight)
    tilesize: int = width
    print('width', width, 'height', height)

    splitAndSave(img, 2, 0, tilesize, append_direction_str(path, "_up"))
    splitAndSave(img, 2, 3, tilesize, append_direction_str(path, "_dn"))
    splitAndSave(img, 3, 2, tilesize, append_direction_str(path, "_ft"))
    splitAndSave(img, 1, 2, tilesize, append_direction_str(path, "_bk"))
    splitAndSave(img, 2, 2, tilesize, append_direction_str(path, "_rt"))
    splitAndSave(img, 4, 2, tilesize, append_direction_str(path, "_lf"))


def append_direction_str(path: Path, direction):
    return path.with_name(path.stem + direction).with_suffix('.tga')


def splitAndSave(img: Image.Image, x, y, tilesize: int, name):
    if x != 0:
        x -= 1
    if y != 0:
        y -= 1
    area = (tilesize * x,
            tilesize * y,
            tilesize * x + tilesize,
            tilesize * y + tilesize)
    saveImage(img.crop(area), path2___, name)


def saveImage(img: Image.Image, path, name):
    img.save(os.path.join(path, name), format='tga')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    args = parser.parse_args()
    processImage(args.image)
