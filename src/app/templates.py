keybinds = r'''
# use AHK notation
# https://www.autohotkey.com/docs/v2/Hotkeys.htm#Symbols
# https://www.autohotkey.com/docs/v2/KeyList.htm

compile = '!c'
launch = '!`'
pc_iterate = '!v'
pc_close_loop = '!+v'
'''

settings = r'''
# some values can be lists [] or strings ''
# in the case of ericw, it can be a folder containing different versions...
# ericw = ['I:\Quake\ericw\ericw-tools-2.0.0-alpha7-win64', 'I:\Quake\ericw\ericw-tools-v0.18.1-32-g6660c5f-win64']
# ...or just a string of a folder path containing those folders...
# ericw = 'I:\Quake\ericw'

# used for map names and {name}
# ex: if your name is rabbit, maps will be zipped as ej3_rabbit
# and templates will be generated like gfx/env/rabbit/
name = 'username'

[paths]
trenchbroom = ''
trenchbroom_preferences = ''

# can be list or string
ericw = ''

# can be list or string
engine_exes = []
configs = ''
maps = ''

[cfg_whitelist]
'' = ['']

[submit]
allowed = [
	'mapsrc/*.map',
	'*.wav',
	'*.mp3',
	'maps/*.bsp',
	'maps/*.lit',
	'*.tga',
	'*.txt',
	'*.md',
]
denied = [
	'*.texinfo',
	'*.json',
	'*.log',
	'*.prt',
	'*.zip',
	'*.7z',
	'autosave/*',
]

[template]
folders = [
	'maps',
	'mapsrc',
	'music',
	'gfx/env/{name}',
	'sound/{name}',
	'progs/{name}',
]
'''
