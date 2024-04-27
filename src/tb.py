'''WINDOWS ONLY'''

import ahk
from ahk import directives, keys, AHK
from ahk.keys import KEYS
import settings
from settings import Settings
import subprocess
import os
import re
from pathlib import Path
import parse
from bcolors import *

# TODO add features from these:
# PUBLIC  https://github.com/spacehare/AHK_public
# PRIVATE https://github.com/spacehare/trenchbroom_pyahk
a = AHK(version='v2')
TB_AHK_TITLE = 'ahk_exe TrenchBroom.exe'
current_map = ''


def copy() -> str:
    a.send('^{c}')
    a.clip_wait()
    return a.get_clipboard()


def paste(text: str = ''):
    if text:
        a.set_clipboard(text)
        a.clip_wait()
    a.send('^{v}')


def if_tb_open(func):
    if a.win_is_active(TB_AHK_TITLE):
        if callable(func):
            func()
    else:
        print(f'attempted to run {func.__name__}, but trenchbroom was not the active window')


def open_trenchbroom(map: str = ''):
    args: list = [Settings.trenchbroom_exe]
    if map:
        args.append(map)
    subprocess.run(args)


def open_preferences():
    os.startfile(Settings.trenchbroom_prefs)


def compile():
    pass


def launch():
    pass


@if_tb_open
def ex():
    pass


def find_map_from_tb_title() -> str | None:
    tb = a.find_window_by_title(TB_AHK_TITLE)
    qmap_matches: list[Path] = []

    if tb:
        tb_qmap_name_search = re.search(r'.+\.map', tb.title)
        if tb_qmap_name_search:
            tb_qmap_name = tb_qmap_name_search.group()
            print('name from TrenchBroom window title:', colorize(tb_qmap_name, bcolors.HEADER))
            for qmap_dir in Settings.maps:
                rglob = qmap_dir.rglob('*')
                for item in rglob:
                    if tb_qmap_name == item.name:
                        print('found', colorize(item, bcolors.OKBLUE))
                        qmap_matches.append(item)

        if qmap_matches:
            print('using', colorize(qmap_matches[0], bcolors.BOLD))
            with open(qmap_matches[0], encoding='utf-8') as f:
                return f.read()
    return


if __name__ == '__main__':
    x = find_map_from_tb_title()
    if x:
        m = parse.QuakeMap.loads(x)
        print(colorize(f'found map!', bcolors.OKBLUE))
    else:
        print(colorize('could not find map from title', bcolors.FAIL))
    a.start_hotkeys()
    a.block_forever()
