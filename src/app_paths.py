from pathlib import Path

CFG = Path('../cfg')
SETTINGS = Path(CFG / 'settings.toml')
KEYBINDS = Path(CFG / 'keybinds.toml')

all_paths = [CFG, SETTINGS, KEYBINDS]

for path in all_paths:
    if path.is_symlink():
        continue
    elif path.is_dir():
        path.mkdir(parents=True)
    elif path.is_file():
        pass
    if not path.exists():
        raise FileNotFoundError()
