import argparse
import shutil
from pathlib import Path
import src.app.settings as settings
import src.app.bcolors as bcolors


def gen(where: Path, prefix: str, name: str = ''):
    stem = f'{prefix}_{name or settings.Settings.name}'
    complete_out = where / stem

    for folder in settings.Template.folders:
        (complete_out / folder).mkdir(parents=True)

    for rel in settings.Template.copy_list:
        for file in rel.files:
            shutil.copyfile(file, Path(complete_out / file.with_stem(stem).name))

    print(bcolors.Ind.mark(True), complete_out)
    return complete_out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out', type=Path,
                        help='where to make the new folder')
    parser.add_argument('prefix', type=str,
                        help=f'the prefix before the map name. ex: qbj, ej3, sm225 = qbj_{settings.Settings.name}, ej3_{settings.Settings.name}, sm225_{settings.Settings.name}')
    parser.add_argument('--name', '-n', type=str,
                        help=f'name of the map')
    args = parser.parse_args()
    gen(args.out, args.prefix, args.name or '')
