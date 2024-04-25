import zipfile as zf
from pathlib import Path
from datetime import datetime
import argparse
import settings
from bcolors import *
from settings import Settings


def create_unique_suffix() -> str:
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    vers = f'{now}'
    return vers


def is_path_ok(path: Path) -> bool:
    allow = False
    for pattern in settings.Submit.allowed + settings.Submit.denied:
        matched = path.match(pattern)
        if matched:
            if pattern in settings.Submit.allowed:
                allow = True
            elif pattern in settings.Submit.denied:
                allow = False
    print(Ind.mark(allow), path)
    return allow


def zip(submission: Path, output_path: Path):
    possible_name = f'_{Settings.name}' if Settings.name not in submission.stem else ''
    versioned_output: Path = Path(f'{output_path}/{submission.stem}{possible_name}_{create_unique_suffix()}.zip')
    with zf.ZipFile(versioned_output, 'w', zf.ZIP_DEFLATED) as zip_file:
        for item in [Path(p) for p in submission.rglob('*')]:
            ok = is_path_ok(item)
            if ok:
                zip_file.write(versioned_output, arcname=item.relative_to(submission))
    print(f'{Ind.mark()}, zipped {versioned_output}')
    return versioned_output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('submission', type=Path,
                        help='the folder containing the files you want to zip for jam submission')
    parser.add_argument('--output_dir', '-o', type=Path,
                        help='where the zipped folder will be created. if one is not supplied, it will be set to the submission folder')
    args = parser.parse_args()

    true_output = args.output_dir or args.submission
    output_file = true_output / Path(rf'{args.submission.stem}.zip')

    zip(args.submission, output_file)
