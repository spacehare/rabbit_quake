import app.settings as settings
import argparse
from pathlib import Path
import app.bcolors as bcolors


def gen(where: Path, prefix: str):
    complete_out = where / f'{prefix}_{settings.Settings.name}'
    for folder in settings.Template.folders:
        (complete_out / folder).mkdir(parents=True)
    print(bcolors.Ind.mark(True), complete_out)
    return complete_out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out', type=Path,
                        help='where to make the new folder')
    parser.add_argument('prefix', type=str,
                        help=f'the prefix before the map name. ex: qbj, ej3, sm225 =  qbj_{settings.Settings.name}, ej3_{settings.Settings.name}, sm225_{settings.Settings.name}')
    args = parser.parse_args()
    gen(args.out, args.prefix)
