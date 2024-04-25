from pathlib import Path
import bcolors

CFG = Path('./cfg')
TEMP = Path('./.temp').resolve()
SETTINGS = Path(CFG / 'settings.toml')
KEYBINDS = Path(CFG / 'keybinds.toml')

all_paths = [CFG, TEMP, SETTINGS, KEYBINDS]

for path in [p.absolute() for p in all_paths]:
    print(bcolors.colorize(path, bcolors.bcolors.OKCYAN))
    if path.exists() or path.is_symlink():
        continue
    else:
        path.mkdir(parents=True)
        # path.touch()
    if not path.exists():
        print('\n', path)
        raise FileNotFoundError()
