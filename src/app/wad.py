# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm
# https://developer.valvesoftware.com/wiki/WAD

import struct
from pathlib import Path
from shared import convert_size
from PIL import Image
import palette


class WAD:
    id = 0
    numentries = 0
    dir_offs = 0

    def __init__(self, file_path):
        self.file_path = file_path
        self.entries: list[Entry] = []

    @staticmethod
    def from_file(path: Path | str):
        new_wad = WAD(path)
        with open(path, 'rb') as f:
            header = f.read(12)
            id, numentries, dir_offs = struct.unpack('4sll', header)
            new_wad.id = id
            new_wad.numentries = numentries
            new_wad.dir_offs = dir_offs
            if id != b'WAD2':
                raise ValueError(f'file needs to be wad2 format, but is {id}')

            f.seek(dir_offs)
            for _ in range(numentries):
                lump = f.read(32)

                # https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm
                # https://developer.valvesoftware.com/wiki/WAD
                # https://docs.python.org/3/library/struct.html#format-characters
                offs: int  # position of entry in WAD
                dsize: int  # size of entry in WAD
                size: int  # size of entry in memory
                entry_type: bytes  # type of entry
                cmprs: int  # compression; 0 if none
                raw_name: bytes  # 1-16 characters, \0 padded

                offs, dsize, size, entry_type, cmprs, _, raw_name = struct.unpack('lllcch16s', lump)

                new_entry = Entry(wad=new_wad,
                                  offs=offs,
                                  disk_size=dsize,
                                  size=size,
                                  entry_type=entry_type.decode(),
                                  cmprs=cmprs,
                                  name=raw_name.decode()
                                  )

                new_wad.entries.append(new_entry)
        return new_wad


class Entry:
    def __init__(self, *, wad, offs: int, disk_size: int, size: int, entry_type: str, cmprs, name: str):
        self.wad = wad
        self.offs = offs
        self.dsize = disk_size
        self.size = size
        self.entry_type = entry_type
        self.cmprs = cmprs
        self.name = name


class MipMap:
    def __init__(self, width: int, height: int, data):
        self.width = width
        self.height = height
        self.data = data


class Texture:
    # https://developer.valvesoftware.com/wiki/Miptex

    mipmaps: list[MipMap] = []  # max 4
    # each mipmap is /2 of the previous
    mip_offs: list[int] = []

    def __init__(self, name: str, width: int, height: int, offs: int):
        self.name = name  # max 16 characters
        self.width = width
        self.height = height
        self.offs = offs


if __name__ == '__main__':
    print('~~~')
    w = WAD.from_file(r"I:\Quake\Dev\wad\rabbit_june.wad")

    with open(w.file_path, 'rb') as f:
        f.read(12)
        f.seek(w.dir_offs)
        entry = w.entries[4]

        print(entry.name)
        f.seek(entry.offs)
        # r = f.read(entry.size)  # this is a bunch of hex values pointing to palette indexes
        name = f.read(16).split(b'\0', 1)[0].decode()
        print(name)
        w, h = struct.unpack('II', f.read(8))
        print(w, h)
        mip_offs = struct.unpack('4I', f.read(16))
        print(mip_offs)

        # alt way to write, idk which i like better yet
        # # this is a bunch of hex values pointing to palette indexes

        # up = struct.unpack('16sII4I', f.read(40))

        # name = up[0].split(b'\0', 1)[0].decode()
        # w, h = up[1:3]
        # mip_offs = up[3:7]

        # print(w, h)
        # print(name)
        # print(mip_offs)

        mips = []
        for i in range(4):
            f.seek(mip_offs[i])
            data = f.read(w * h // (4 ** i))
            mips.append(data)

        print(mips)

    # Image.frombytes('rgb', entry.size, )
