from pathlib import Path
import re
import argparse

PATTERN_TEXTURE = re.compile(r".+\) (.+?) \[")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('map', type=Path, help='the full path of the target map file')
    args = parser.parse_args()
    file: Path = args.map

    matches = PATTERN_TEXTURE.findall(file.read_text(encoding='utf-8'))

    unique = sorted(set(matches))

    for item in unique:
        print(item)
