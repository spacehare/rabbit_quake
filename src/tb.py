from subprocess import call, run
from ahk import directives, keys, AHK
import files

a = AHK(version='v2')


def open_trenchbroom(map: str | None):
    run([files.Settings.trenchbroom_exe])


def open_preferences():
    run(['open', files.Settings.trenchbroom_prefs])
