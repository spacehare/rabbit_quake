import argparse
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import py7zr

from .app import bsp
from .app.bcolors import bcolors, colorize
from .app.settings import S_MASTERS, Settings


class Pair(NamedTuple):
    key: str
    dest: Path


def get_deps(parent: Path):
    paths: list[Path] = list(parent.rglob("*"))
    bsp_paths: list[Path] = []
    for path in paths:
        if path.suffix == ".bsp":
            bsp_paths.append(path)


def filter_deps():
    d = Settings.jampack
    deny = d.get("deny")
    allow = d.get("allow")


def package_submission(submission_path: Path):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder",
        type=Path,
        help="the folder containing submissions, can be zip files, 7z files, or subfolders",
    )
    parser.add_argument("output", type=Path, help="...")
    parser.add_argument(
        "--copy",
        "-c",
        action="store_true",
        help="copy the files to their destinations within the output folder",
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    output = Path(args.output)
    copy = args.copy

    if folder == output:
        print("input cannot be same as output")
        exit()

    # package_submissions(folder, output, copy)
