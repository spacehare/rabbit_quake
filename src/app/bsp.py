import struct
from struct import Struct
from pathlib import Path
from src.app.parse import Entity, Brush, parse_whole_map
from dataclasses import dataclass, field

# TODO make sure this works with bsp and bsp2 files
# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm


@dataclass
class Entry:
    STRUCT = Struct("2l")
    offset: int
    size: int

    @staticmethod
    def from_lump(lump: bytes):
        offset, size = Entry.STRUCT.unpack(lump)
        return Entry(offset=offset, size=size)


@dataclass
class BSP:
    version = None
    entries: list[Entry] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)


ST_VERSION = Struct("l")
ST_ENTRY = Struct("2l")
ST_VERSION = Struct("l")


def read_bsp(bsp_path: Path) -> BSP:
    print("reading bsp %s" % bsp_path)
    nbsp = BSP()
    with open(bsp_path, "rb") as f:
        version = ST_VERSION.unpack(f.read(ST_VERSION.size))
        entries: list[Entry] = []
        for _ in range(15):
            entry = Entry.from_lump(f.read(ST_ENTRY.size))
            entries.append(entry)

        for entry in entries:
            f.seek(entry.offset)
            data = f.read(entry.size)
            if entry == entries[0]:
                text: str = data.decode("utf-8", "backslashreplace")
                qmap = parse_whole_map(text)
                nbsp.entities = qmap

    return nbsp


def read_bsp_entities(bsp_path: Path) -> list[Entity]:
    """legacy version, just gets entities"""
    with open(bsp_path, "rb") as f:
        f.read(4)
        header = f.read(48)
        lumps = struct.unpack("12l", header)
        offset = lumps[0]
        length = lumps[1]
        f.seek(offset)
        data = f.read(length)
        text = data.decode("utf-8")
        ents = parse_whole_map(text)
        return ents
