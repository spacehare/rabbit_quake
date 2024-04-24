import zipfile as zf
from pathlib import Path
from datetime import datetime
import argparse
import appsettings
from bcolors import *


def create_unique_suffix() -> str:
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    vers = f'{now}'
    return vers


parser = argparse.ArgumentParser()
parser.add_argument('submission', type=Path,
                    help='the folder containing the files you want to zip for jam submission')
parser.add_argument('--output_dir', '-o', type=Path,
                    help='where the zipped folder will be created. if one is not supplied, it will be set to the submission folder')
args = parser.parse_args()

true_output = args.output_dir or args.submission
output_file = true_output / Path(rf'{args.submission.stem}_{create_unique_suffix()}.zip')


def is_path_ok(path: Path) -> bool:
    allow = False
    for pattern in appsettings.Submit.allowed + appsettings.Submit.denied:
        matched = path.match(pattern)
        if matched:
            if pattern in appsettings.Submit.allowed:
                allow = True
            elif pattern in appsettings.Submit.denied:
                allow = False
    print(Ind.mark(allow), path)
    return allow


print('- - -\n', args.submission, '\n- - -')


def zip():
    with zf.ZipFile(output_file, 'w', zf.ZIP_DEFLATED) as zip_file:
        for item in [Path(p) for p in args.submission.rglob('*')]:
            ok = is_path_ok(item)
            if ok:
                zip_file.write(output_file, arcname=item.relative_to(args.submission))


if __name__ == '__main__':
    zip()
