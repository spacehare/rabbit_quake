import app.settings
from app.parse import parse
from pathlib import Path

file: Path = Path("I:\Quake\Dev\maps\_ignore\mpj2_yo\mapsrc\mpj2_yo.map")
string_data: str = file.read_text()
map_data = parse(string_data)
print(map_data)
