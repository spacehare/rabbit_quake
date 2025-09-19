from .app import settings
from pathlib import Path
from .app.bcolors import bcolors, colorize
import argparse


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dev_folder', type=Path)
    ap.add_argument('mod_folder', type=Path)
    args = ap.parse_args()

    dev_folder: Path = args.dev_folder
    mod_folder: Path = args.mod_folder

    print('creating symlinks')
    for item in settings.symlinks:
        for path in dev_folder.rglob(item.target):
            new_path: Path = Path(mod_folder / item.destination / path.name)

            print(colorize(path, bcolors.UNDERLINE))
            print('\ttarget =', colorize(path, bcolors.OKBLUE))
            print('\tdestination =', colorize(item.destination, bcolors.OKBLUE))
            print('\tlink =', colorize(new_path, bcolors.OKBLUE))

            if new_path.exists():
                print(colorize(f"\t\"{new_path}\" already exists, skipping.", bcolors.WARNING))
            else:
                new_path.symlink_to(
                    target=path,
                    target_is_directory=path.is_dir()
                )
