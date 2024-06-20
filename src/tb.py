'''WINDOWS ONLY'''

import subprocess
import os
import re
import platform
import app.ericw as ericw
from ahk import directives, keys, AHK
from ahk.keys import KEYS
from pathlib import Path
from app.parse import Entity, Brush, QuakeMap
from app.settings import Settings, Keybinds
from app.bcolors import *

if platform.system() != 'Windows':
    print(colorize('this script is Windows only', bcolors.FAIL))
    exit()

# TODO add features from these:
# PUBLIC  https://github.com/spacehare/AHK_public
# PRIVATE https://github.com/spacehare/trenchbroom_pyahk
a = AHK(version='v2')
TB_AHK_TITLE = 'ahk_exe TrenchBroom.exe'

current_map: Path | None = None
current_mod: str = ''
current_mod_folder: Path | None = None
current_engine = Settings.engines[0]
current_profile: ericw.Profile = ericw.profiles[0]
current_compiler: ericw.Compiler = ericw.compilers[0]

enable_qbsp = True
enable_vis = True
enable_light = True


def copy() -> str:
    a.set_clipboard('')
    a.send('^c')
    a.clip_wait(1)
    # print('CLIPBOARD', a.get_clipboard())
    return a.get_clipboard()


def paste(text: str = ''):
    if text:
        a.set_clipboard(text)
        a.clip_wait(1)
    a.send('^v')


def delete():
    pass


def if_tb_open(func):
    def wrapper(*args):
        if a.win_is_active(TB_AHK_TITLE):
            if callable(func):
                func(*args)
        else:
            print(f'attempted to run {func.__name__}, but trenchbroom was not the active window')
    return wrapper


def open_trenchbroom(map: str = ''):
    args: list = [Settings.trenchbroom_exe]
    if map:
        args.append(map)
    subprocess.run(args)


def open_preferences():
    os.startfile(Settings.trenchbroom_prefs)


@if_tb_open
def ex():
    print('aaa')


class MapData:
    def __init__(self, filepath: Path, data: str):
        self.filepath = filepath
        self.data = data


def find_map_from_tb_title():
    print(colorize('searching for map based on window title', bcolors.HEADER))
    tb = a.find_window_by_title(TB_AHK_TITLE)
    qmap_path_matches: list[Path] = []
    tb_qmap_path: Path | None = None

    if tb:
        tb_qmap_name_search = re.search(r'.+\.map', tb.title)
        if tb_qmap_name_search:
            tb_qmap_name = tb_qmap_name_search.group()
            print('name from TrenchBroom window title:', colorize(tb_qmap_name, bcolors.OKCYAN))
            for qmap_dir in Settings.maps:
                rglob = qmap_dir.rglob('*')
                for item in rglob:
                    if tb_qmap_name == item.name:
                        tb_qmap_path = item
                        print('found', colorize(item, bcolors.OKBLUE))
                        qmap_path_matches.append(item)

            if qmap_path_matches and tb_qmap_path:
                print('using', colorize(qmap_path_matches[0], bcolors.OKGREEN))
                with open(qmap_path_matches[0]) as f:
                    return MapData(qmap_path_matches[0], f.read())

    print(colorize('could not find map from title', bcolors.FAIL))
    exit()


@if_tb_open
def iterate(close_loop=False):
    print(colorize('iterating', bcolors.HEADER))
    ent = Entity.loads(copy())
    ent.iterate('targetname')
    ent.iterate('target', set_to_val=close_loop)
    paste(ent.dumps())


def compile_and_transfer(profile, compiler, qbsp, vis, light):
    if current_map:
        print(qbsp, vis, light)
        ret = ericw.compile(profile, compiler, current_map, qbsp=qbsp, vis=vis, light=light)
        transfer()
        return ret


def transfer():
    if current_map and current_mod_folder:
        print(current_map.parent / 'maps')
        print(current_mod_folder / 'maps')
        for f in [f for f in (current_map.parent / 'maps').iterdir()]:
            if f.suffix == '.bsp' or f.suffix == '.lit':
                ericw.transfer_or_link(f, current_mod_folder / 'maps')


def compile_then_launch(qbsp, vis, light):
    if current_map and current_mod:
        if compile_and_transfer(current_profile, current_compiler, qbsp, vis, light):
            launch(mod=current_mod, map_name=current_map.stem)


def launch(*, engine=Settings.engines[0], mod='', map_name=''):
    params: list = [engine.exe]
    if mod:
        params += ['-game', mod]
    if map_name:
        params += ['+map', map_name]
    print('launching...', colorize(' '.join([str(p) for p in params]), bcolors.OKBLUE))
    process = subprocess.run(params, cwd=engine.folder)
    a.win_activate(f'ahk_exe {engine.exe}')
    return process


def yes_or_no(text: str) -> bool:
    return 'y' in text.lower()


if __name__ == '__main__':
    print('🐇 program start')
    qmap_full = find_map_from_tb_title()
    if qmap_full:
        qmap = QuakeMap.loads(qmap_full.data)
        current_map = qmap_full.filepath
        current_mod = qmap.mod
        current_mod_folder = current_engine.folder / current_mod
        print('current mod:', colorize(current_mod, bcolors.OKCYAN))

    # what_profile = input('what profile?')
    # what_compiler = input('what compiler?')
    # what_qbsp = input('enable qbsp?')
    # what_vis = input('enable vis?')
    # what_light = input('enable light?')

    # current_profile = ericw.profiles[int(what_profile)]
    # current_compiler = ericw.compilers[int(what_compiler)]
    # enable_qbsp = yes_or_no(what_qbsp)
    # enable_vis = yes_or_no(what_vis)
    # enable_light = yes_or_no(what_light)
    # print(current_profile, current_compiler, enable_qbsp, enable_vis, enable_light)

    a.add_hotkey(Keybinds.iterate, lambda: iterate())
    a.add_hotkey(Keybinds.pc_close_loop, lambda: iterate(True))
    a.add_hotkey(Keybinds.compile, lambda: compile_and_transfer(current_profile, current_compiler, enable_qbsp, enable_vis, enable_light))
    a.add_hotkey('!b', lambda: compile_then_launch(enable_qbsp, enable_vis, enable_light))

    if current_map and current_mod:
        x = current_map
        a.add_hotkey(Keybinds.launch, lambda: launch(mod=current_mod, map_name=x.stem))

    a.start_hotkeys()
    print(Ind.mark())
    a.block_forever()
