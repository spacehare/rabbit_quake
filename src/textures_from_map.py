from pathlib import Path
import re

file_path = Path(r"I:\Quake\Dev\maps\maps\mcj_rabbit\mcj_rabbit.map")
txt = file_path.read_text(encoding='utf-8')
r = re.compile(r"[^\W]+(?= \[)")

matches = r.findall(txt)

unique = sorted(set(matches))

for item in unique:
    print(item)
