import zipfile as zf
from pathlib import Path
from datetime import datetime
import argparse
import settings
from bcolors import *
from settings import Settings
import markdown2


def create_unique_suffix() -> str:
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def is_path_ok(path: Path) -> bool:
    allow = False
    for pattern in settings.Submit.allowed:
        matched = path.match(pattern)
        if matched:
            if pattern in settings.Submit.allowed:
                allow = True

    print(Ind.mark(allow), colorize(path, bcolors.OKBLUE if allow else bcolors.FAIL))
    return allow


def zip(submission: Path, output_parent: Path, *, convert_markdown=False):
    possible_name = f'_{Settings.name}' if Settings.name not in submission.stem else ''
    versioned_output: Path = output_parent / Path(f'{submission.stem}{possible_name}_{create_unique_suffix()}.zip')
    print('output file:', versioned_output)
    ok_files = [p for p in submission.rglob('*') if p.is_file() and is_path_ok(p)]

    with zf.ZipFile(versioned_output, 'w', zf.ZIP_DEFLATED) as zip_file:
        for file in ok_files:
            if file.suffix == '.md':
                html = markdown2.markdown_path(file)
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

    zip(args.submission, output_parent, convert_markdown=args.md)
