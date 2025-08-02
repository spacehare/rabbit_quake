from pathlib import Path
import app.bcolors as bcolors

CFG = Path('./cfg')
TEMP = Path('./.temp').resolve()
all_paths = [CFG, TEMP]

for path in [p.absolute() for p in all_paths]:
    print(f'({__name__}) path found', bcolors.colorize(path, bcolors.bcolors.OKCYAN))
    if path.exists() or path.is_symlink():
        continue
    else:
        path.mkdir(parents=True)
        # path.touch()
    if not path.exists():
        print('\n', path)
        raise FileNotFoundError()
