from pathlib import Path
import appsettings
from bcolors import *

autosave_path: Path = Path('autosave')
autosave_str = 'autosave'
where = appsettings.Settings.maps

for folder in where.rglob('*'):
    if folder.match(autosave_str):
        saves = [qmap for qmap in folder.glob('*.map')]
        print(colorize(folder, bcolors.OKCYAN), len(saves))
