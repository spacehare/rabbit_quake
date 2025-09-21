import argparse
import shutil
from pathlib import Path
import src.app.settings as settings
import src.app.bcolors as bcolors


def gen(parent_folder: Path, stem: str, create: bool = True):
    if not parent_folder.exists():
        parent_folder.mkdir()

    print('-- create --')
    for item in settings.template.touch:
        item_path: Path = Path(item.replace("{mapstem}", stem))
        path: Path = parent_folder / item_path
        print(f'\t-> {path}')

        if create:
            if path.is_file():
                path.touch()
            else:
                path.mkdir(parents=True)

    print('-- copy --')
    for pair in settings.template.copy_pairs:
        dest = parent_folder / str(pair.destination).replace("{mapstem}", stem)
        print(f'\t-> {dest}')

        if create:
            shutil.copyfile(pair.file, dest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('new_folder', type=Path,
                        help="the new folder's path")
    parser.add_argument('stem', type=str,
                        help=f"the stem of the map. ex: qbj_rabbit, rm_myopia")
    parser.add_argument('--fake', action='store_true',
                        help=f"don't actually copy or create any files.")
    args = parser.parse_args()

    if args.fake:
        print('debug run; not creating or copying files.')

    gen(args.new_folder, args.stem, not args.fake)
