import argparse
import enum
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import markdown2
import py7zr

from rabbitquake.app.bcolors import *
from rabbitquake.app.settings import Settings

# TODO read bsp and find dependencies


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


def compress(submission: Path, output_parent: Path, *, convert_markdown=False, mode: Mode) -> Path:
    assert mode in Mode

    name = [p for p in submission.rglob("*") if p.suffix == ".bsp"][0].stem
    if not name:
        print("could not find a BSP file, exiting")
        exit()

    ok_files = [p for p in submission.rglob("*") if p.is_file() and is_path_ok(p, Settings.submit_whitelist)]
    versioned_output: Path = output_parent / Path(f"{name}-{create_unique_slug()}")

    zipper = None
    sevenzipper = None
    match mode:
        case Mode.ZIP:
            versioned_output = versioned_output.with_suffix(".zip")
            zipper = zipfile.ZipFile(versioned_output, "w", zipfile.ZIP_DEFLATED)
        case Mode.SEVEN:
            versioned_output = versioned_output.with_suffix(".7z")
            sevenzipper = py7zr.SevenZipFile(versioned_output, "w")

    print("output file:", versioned_output)

    for file in ok_files:
        relative = file.relative_to(submission)

        html = None
        if file.suffix == ".md" and convert_markdown:
            html = markdown2.markdown_path(str(file), extras=["tables"])
            html_path = relative.with_suffix(".html")

        if zipper:
            if html and html_path:
                zipper.writestr(str(html_path), html)
            zipper.write(filename=file, arcname=relative)

        elif sevenzipper:
            if html and html_path:
                sevenzipper.writestr(html, str(html_path))
            sevenzipper.write(file=file, arcname=str(relative))

        print("compressed ->", relative)

    if zipper:
        zipper.close()
    elif sevenzipper:
        sevenzipper.close()

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
    parser.add_argument("--md", action="store_true", help="convert markdown files to html")
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
