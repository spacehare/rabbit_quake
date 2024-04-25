from subprocess import call, run
from ahk import directives, keys, AHK
import settings

a = AHK(version='v2')
TB_AHK_TITLE = 'ahk_exe TrenchBroom.exe'
TB_KEYS_MOD = '_tb_mod'

print(a.win_is_active(TB_AHK_TITLE))


def if_tb_open(func):
    if a.win_is_active(TB_AHK_TITLE):
        func()
    else:
        print(f'attempted to run {func}, but trenchbroom was not the active window')


def open_trenchbroom(map: str | None):
    run([settings.Settings.trenchbroom_exe])


def open_preferences():
    run(['open', settings.Settings.trenchbroom_prefs])


@if_tb_open
def ex():
    pass
