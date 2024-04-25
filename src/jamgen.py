import appsettings
import argparse
from pathlib import Path
import bcolors

parser = argparse.ArgumentParser()
parser.add_argument('out', type=Path,
                    help='where to make the new folder')
parser.add_argument('prefix', type=str,
                    help=f'the prefix before the map name. ex: qbj, ej3, sm225 =  qbj_{appsettings.Settings.name}, ej3_{appsettings.Settings.name}, sm225_{appsettings.Settings.name}')
args = parser.parse_args()


def gen(where: Path = args.out):
    complete_out = where / f'{args.prefix}_{appsettings.Settings.name}'
    for folder in appsettings.Template.folders:
        (complete_out / folder).mkdir(parents=True)
    print(bcolors.Ind.mark(True), complete_out)


if __name__ == '__main__':
    gen()
