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
    parser.add_argument("-o", "--output_folder", type=Path)
    parser.add_argument("stem_without_direction", type=str)
    parser.add_argument("turns", type=int)
    args = parser.parse_args()

    parent_folder: Path = args.parent_folder
    output_folder: Path | None = args.output_folder
    stem_body: str = args.stem_without_direction
    turns: int = args.turns

    if not (0 < turns < 4):
        raise ValueError("turns must be between 1 and 3")

    # rotate yaw
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
                if direction == "up":
                    new_image = rotate_image(img, turns)
                    new_direction = direction
                elif direction == "dn":
                    reverse = {
                        3: 1,
                        2: 2,
                        1: 3,
                    }
                    new_image = rotate_image(img, reverse[turns])
                    new_direction = direction
                else:
                    dir_dict[direction] = items.index(direction)  # ex: lf = 2
                    new_image = img
                    new_direction = faces[dir_dict[direction]]
                new_filename: Path = path.with_stem(f"{path.stem[:-2]}_{turns}_{new_direction}")
                if output_folder:
                    new_filename = output_folder / new_filename.name
                new_image.save(new_filename)

            print("->", direction, new_direction, path)
