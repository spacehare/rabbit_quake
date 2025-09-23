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


def package_submission(submission_path: Path, output_path: Path, fake: bool):
    is_zip_file = output_path.suffix == ".zip"
    zip_file = None

    if is_zip_file:
        zip_file = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)

    for path in submission_path.rglob("*"):
        path_dealt_with = False

        if any(pattern.check(path) for pattern in jampack.deny):
            print("\tskipping", colorize(path, bcolors.WARNING))
            path_dealt_with = True
            continue

        for pattern_parent in jampack.allow:
            for pattern in pattern_parent.patterns:
                if pattern.check(path):
                    print("\tadding", colorize(path, bcolors.OKBLUE))
                    dest = pattern_parent.destination
                    full_dest = output_path / Path(dest) / path.name

                    if not fake and not path_dealt_with:
                        if zip_file:
                            zip_file.write(path, Path(dest) / path.name)
                        else:
                            full_dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(path, full_dest)

                    path_dealt_with = True

        if not path_dealt_with:
            print("\tno match:", colorize(path, bcolors.FAIL))

    if zip_file:
        zip_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder",
        type=Path,
        help="the folder containing submissions, can be zip files, 7z files, or subfolders",
    )
    parser.add_argument(
        "output", type=Path, help="can be a folder to create, or .zip path to create"
    )
    parser.add_argument(
        "--fake", action="store_true", help=f"don't actually copy or create any files."
    )
    args = parser.parse_args()

    input_folder = Path(args.folder)
    output_folder = Path(args.output)

    if input_folder == output_folder:
        print("input cannot be same as output")
        exit()

    print("finding and unzipping submissions")
    submissions = unpack_submissions(input_folder, output_folder)
    for submission in submissions:
        print("submission:", submission)
        package_submission(submission, output_folder, args.fake)
