import argparse
import markdown2
import zipfile as zf
from pathlib import Path
from datetime import datetime, timezone
from src.app.bcolors import *
from src.app.settings import Settings

# TODO read bsp and find dependencies
# TODO allow 7z output


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


def compress(submission: Path, output_parent: Path, *, convert_markdown=False):
    name = [p for p in submission.rglob('*') if p.suffix == '.bsp'][0].stem
    if not name:
        print('could not find a BSP file, exiting')
        exit()

    versioned_output: Path = output_parent / Path(f'{name}-{create_unique_slug()}.zip')
    print('output file:', versioned_output)
    ok_files = [p for p in submission.rglob('*') if p.is_file() and is_path_ok(p, Settings.submit_whitelist)]

    with zf.ZipFile(versioned_output, 'w', zf.ZIP_DEFLATED) as zip_file:
        for file in ok_files:
            if file.suffix == '.md' and convert_markdown:
                html = markdown2.markdown_path(file, extras=['tables'])
                zip_file.writestr(str(file.relative_to(submission).with_suffix('.html')), html)

            zip_file.write(file, file.relative_to(submission))
            print('->', file.relative_to(submission))

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
    args = parser.parse_args()

    output_parent = args.output_dir or args.submission

    compress(args.submission, output_parent, convert_markdown=args.md)
