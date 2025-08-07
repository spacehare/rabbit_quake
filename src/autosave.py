from pathlib import Path
import src.app.settings as settings
from src.app.bcolors import *
import argparse
import src.app.shared as shared

autosave_path: Path = Path('autosave')
autosave_str = 'autosave'
where = settings.Settings.maps_path


def get_all_autosaves():
    all_saves: list[Path] = []
    for folder in where.rglob('*'):
        if folder.match(autosave_str):
            saves = [qmap for qmap in folder.glob('*.map')]
            size = 0
            for save in saves:
                size += save.stat().st_size
            print(colorize(folder, bcolors.OKCYAN), f'{"%3d" % len(saves)} saves', shared.convert_size(size), sep='\t')
            all_saves += saves
    return all_saves


def delete_autosaves():
    all_autosaves = get_all_autosaves()
    if not all_autosaves:
        print(colorize('no autosaves found', bcolors.WARNING))
    for autosave in all_autosaves:
        print('DELETING', autosave)
        autosave.unlink()
        print(Ind.mark(True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--delete', '-d', action='store_true', help='delete all autosaves')
    parser.add_argument('--list', '-l', action='store_true', help='print all autosaves')
    args = parser.parse_args()

    if args.delete:
        delete_autosaves()
    if args.list:
        get_all_autosaves()
