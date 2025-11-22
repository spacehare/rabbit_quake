# from PIL import Image
import argparse
from collections import deque
from pathlib import Path

from PIL import Image


def stem_direction(path: Path) -> str:
    return path.stem[-2:]


rotations = {
    1: Image.Transpose.ROTATE_270,
    2: Image.Transpose.ROTATE_180,
    3: Image.Transpose.ROTATE_90,
}


def rotate_image(image: Image.Image, turns: int) -> Image.Image:
    return image.transpose(rotations[turns])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_folder", type=Path)
    parser.add_argument("stem_without_direction", type=str)
    parser.add_argument("turns", type=int)
    args = parser.parse_args()

    parent_folder: Path = args.parent_folder
    stem_body: str = args.stem_without_direction
    turns: int = args.turns

    if not (0 < turns < 4):
        raise ValueError("turns must be between 1 and 3")

    # rotate yaw
    rotate_me = ["up", "dn"]
    dir_dict: dict[str, int] = {}
    faces = ["ft", "rt", "bk", "lf"]
    items = deque(faces)
    items.rotate(turns)

    for path in parent_folder.glob("*"):
        if path.stem.startswith(stem_body):
            new_image: Image.Image
            direction = stem_direction(path)
            new_direction: str

            with Image.open(path) as img:
                if direction in rotate_me:
                    new_image = rotate_image(img, turns)
                    new_direction = direction
                else:
                    dir_dict[direction] = items.index(direction)  # ex: lf = 2
                    new_image = img
                    new_direction = faces[dir_dict[direction]]
                new_filename: Path = path.with_stem(
                    f"{path.stem[:-2]}_{turns}_{new_direction}"
                )
                new_image.save(new_filename)

            print("->", direction, new_direction, path)
