import argparse
import enum
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import markdown2
import py7zr

from src.app.bcolors import *
from src.app.settings import Settings

# TODO read bsp and find dependencies
# TODO allow 7z output


class Mode(enum.StrEnum):
    ZIP = "zip"
    SEVEN = "7z"


def create_unique_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def is_path_ok(path: Path, whitelist) -> bool:
    allow = False
    for pattern in whitelist:
        # FIXME this will break with recursive patterns, "**"
        allow = path.match(pattern) and pattern in whitelist
        if allow:
            break

    print(Ind.mark(allow), colorize(path, bcolors.OKBLUE if allow else bcolors.FAIL))
    return allow


def try_md_to_html(
    *,
    file_path: Path,
    convert_markdown: bool,
    root: Path,
    zipper: zipfile.ZipFile | py7zr.SevenZipFile,
):
    if file_path.suffix == ".md" and convert_markdown:
        html = markdown2.markdown_path(str(file_path), extras=["tables"])
        zipper.writestr(str(file_path.relative_to(root).with_suffix(".html")), html)


def compress(
    submission: Path, output_parent: Path, *, convert_markdown=False, mode: Mode
):
    assert mode in Mode

    name = [p for p in submission.rglob("*") if p.suffix == ".bsp"][0].stem
    if not name:
        print("could not find a BSP file, exiting")
        exit()

    ext = ".zip" if mode == Mode.ZIP else ".7z"
    versioned_output: Path = output_parent / Path(
        f"{name}-{create_unique_slug()}"
    ).with_suffix(ext)
    print("output file:", versioned_output)
    ok_files = [
        p
        for p in submission.rglob("*")
        if p.is_file() and is_path_ok(p, Settings.submit_whitelist)
    ]
    zipper = None

    match mode:
        case Mode.ZIP:
            zipper = zipfile.ZipFile(versioned_output, "w", zipfile.ZIP_DEFLATED)
        case Mode.SEVEN:
            zipper = py7zr.SevenZipFile(versioned_output, "w")

    if zipper:
        for file in ok_files:
            try_md_to_html(
                file_path=file,
                zipper=zipper,
                convert_markdown=convert_markdown,
                root=submission,
            )
            zipper.write(file, arcname=str(file.relative_to(submission)))
            print("compressed ->", file.relative_to(submission))
        zipper.close()

    print(f"{Ind.mark()}, zipped {len(ok_files)} files into {versioned_output}")
    return versioned_output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "submission",
        type=Path,
        help="the folder containing the files you want to zip for jam submission",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=Path,
        help="where the zipped folder will be created. if one is not supplied, it will be set to the submission folder",
    )
    parser.add_argument(
        "--md", action="store_true", help="convert markdown files to html"
    )
    parser.add_argument(
        "--mode",
        type=Mode,
        default=Mode.ZIP,
        choices=list(Mode),
        help=f"what mode to use",
    )
    args = parser.parse_args()

    output_parent = args.output_dir or args.submission

    compress(args.submission, output_parent, convert_markdown=args.md, mode=args.mode)
