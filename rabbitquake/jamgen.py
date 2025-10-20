import argparse
import shutil
from pathlib import Path

import rabbitquake.app.settings as settings


def gen(target_folder: Path, create: bool = True) -> None:
    if not target_folder.exists() and create:
        target_folder.mkdir()

    print("-- create --")
    for item in settings.template.touch:
        item_path: Path = Path(item.replace("{mapstem}", target_folder.stem))
        path: Path = target_folder / item_path
        print(f"\t-> {path}")

        if create:
            if path.is_file():
                path.touch()
            else:
                path.mkdir(parents=True)

    print("-- copy --")
    for pair in settings.template.copy_pairs:
        dest = target_folder / str(pair.destination).replace(
            "{mapstem}", target_folder.stem
        )
        print(f"\t-> {dest}")

        if create:
            shutil.copyfile(pair.file, dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "parent_folder", type=Path, help="the folder to put all the new files into."
    )
    parser.add_argument(
        "--fake", action="store_true", help=f"don't actually copy or create any files."
    )
    args = parser.parse_args()

    if args.fake:
        print("debug run; not creating or copying files.")

    gen(args.parent_folder, not args.fake)
