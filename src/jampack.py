import argparse
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import py7zr

from .app.bcolors import bcolors, colorize
from .app.deps import DependencyData
from .app.settings import jampack


def unpack_submissions(root: Path, output_parent: Path) -> list[Path]:
    submissions: list[Path] = []

    for item in root.glob("*"):
        if item.is_dir():
            submissions.append(item)
        else:
            zipper = None

            if item.suffix == ".zip":
                zipper = zipfile.ZipFile(item, "r")
            elif item.suffix == ".7z":
                zipper = py7zr.SevenZipFile(item, "r")

            if zipper:
                new_path = output_parent / item.name
                with zipper as zip_file:
                    zip_file.extractall(new_path)
                    submissions.append(new_path)

    return submissions


def package_submission(submission_path: Path, output_path: Path):
    for path in submission_path.rglob("*"):
        if any(pattern.check(path) for pattern in jampack.deny):
            print("\tskipping", path)
            continue

        for pattern_parent in jampack.allow:
            for pattern in pattern_parent.patterns:
                if pattern.check(path):
                    print("\tadding", path)
                    dest = pattern_parent.destination
                    full_dest = output_path / Path(dest) / path.name
                    print("\t\t->", colorize(full_dest, bcolors.OKBLUE))
                    full_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, full_dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder",
        type=Path,
        help="the folder containing submissions, can be zip files, 7z files, or subfolders",
    )
    parser.add_argument("output", type=Path, help="...")
    args = parser.parse_args()

    input_folder = Path(args.folder)
    output_folder = Path(args.output)

    if input_folder == output_folder:
        print("input cannot be same as output")
        exit()

    print("finding and unzipping submissions")
    submissions = unpack_submissions(input_folder, output_folder)
    for submission in submissions:
        print("sub:", submission)
        package_submission(submission, output_folder)
