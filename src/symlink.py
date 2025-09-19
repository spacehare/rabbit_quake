from .app import settings
from pathlib import Path
import argparse


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dev_folder', type=Path)
    ap.add_argument('mod_folder', type=Path)
    args = ap.parse_args()

    dev_folder: Path = args.dev_folder
    mod_folder: Path = args.mod_folder

    for item in settings.symlinks:
        for path in dev_folder.rglob(item.target):
            print('target', path)
            print('destination', item.destination)

            new_path: Path = Path(mod_folder / item.destination / path.name)

            print('link', new_path)
            print('-----')
            new_path.symlink_to(
                target=path,
                target_is_directory=path.is_dir()
            )
