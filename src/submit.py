import argparse
import markdown2
import py7zr
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from src.app.bcolors import *
from src.app.settings import Settings
import enum

# TODO read bsp and find dependencies
# TODO allow 7z output


class Mode(enum.StrEnum):
    ZIP = 'zip'
    SEVEN = '7z'


def create_unique_slug() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def is_path_ok(path: Path, whitelist) -> bool:
    allow = False
    for pattern in whitelist:
        allow = path.match(pattern) and pattern in whitelist
        if allow:
            break

    print(Ind.mark(allow),
          colorize(path, bcolors.OKBLUE if allow else bcolors.FAIL))
    return allow


def try_md_to_html(*, afile: Path, convert_markdown: bool, root: Path, zipper: zipfile.ZipFile | py7zr.SevenZipFile):
    if afile.suffix == '.md' and convert_markdown:
        html = markdown2.markdown_path(afile, extras=['tables'])
        zipper.writestr(str(afile.relative_to(root).with_suffix('.html')), html)


def compress(submission: Path, output_parent: Path, *, convert_markdown=False, mode: Mode):
    assert mode in Mode

    name = [p for p in submission.rglob('*') if p.suffix == '.bsp'][0].stem
    if not name:
        print('could not find a BSP file, exiting')
        exit()

    ext = '.zip' if mode == Mode.ZIP else '.7z'
    versioned_output: Path = output_parent / Path(f'{name}-{create_unique_slug()}{ext}')
    print('output file:', versioned_output)
    ok_files = [p for p in submission.rglob('*') if p.is_file() and is_path_ok(p, Settings.submit_whitelist)]

    match mode:
        case Mode.ZIP:
            with zipfile.ZipFile(versioned_output, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in ok_files:
                    try_md_to_html(afile=file, zipper=zip_file, convert_markdown=convert_markdown, root=submission)

                    zip_file.write(file, arcname=file.relative_to(submission))
                    print('ZIP ->', file.relative_to(submission))
        case Mode.SEVEN:
            with py7zr.SevenZipFile(versioned_output, 'w') as seven_zip_file:
                for file in ok_files:
                    try_md_to_html(afile=file, zipper=seven_zip_file, convert_markdown=convert_markdown, root=submission)

                    seven_zip_file.writeall(file, arcname=str(file.relative_to(submission)))
                    print(' 7Z ->', file.relative_to(submission))

    print(f'{Ind.mark()}, zipped {len(ok_files)} files into {versioned_output}')
    return versioned_output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('submission', type=Path,
                        help='the folder containing the files you want to zip for jam submission')
    parser.add_argument('output_dir', nargs='?', type=Path,
                        help='where the zipped folder will be created. if one is not supplied, it will be set to the submission folder')
    parser.add_argument('--md', action='store_true',
                        help='convert markdown files to html')
    parser.add_argument('--mode', type=Mode, default=Mode.ZIP, choices=list(Mode),
                        help=f"what mode to use")
    args = parser.parse_args()

    output_parent = args.output_dir or args.submission

    compress(args.submission, output_parent, convert_markdown=args.md, mode=args.mode)
