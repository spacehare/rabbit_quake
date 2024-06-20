# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm
# https://developer.valvesoftware.com/wiki/WAD

import struct
from pathlib import Path
from PIL import Image
if __name__ == '__main__':
    import palette
else:
    import app.palette as palette


class WAD:
    id = 0
    numentries = 0
    dir_offs = 0

    def __init__(self, file_path):
        self.file_path = file_path
        self.entries: list[Entry] = []
        self.textures: list[MipTex] = []

    @staticmethod
    def from_file(path: Path | str):
        new_wad = WAD(path)
        with open(path, 'rb') as f:
            # print(f.read())

            header = f.read(12)
            id, numentries, dir_offs = struct.unpack('4sll', header)
            new_wad.id = id
            new_wad.numentries = numentries
            new_wad.dir_offs = dir_offs
            if id != b'WAD2':
                raise ValueError(f'file needs to be wad2 format, but is {id}')

            f.seek(dir_offs)
            for _ in range(numentries):
                orig = f.tell()
                lump = f.read(32)

                offset: int  # position of entry in WAD
                disk_size: int  # size of entry in WAD
                size: int  # size of entry in memory
                entry_type: bytes  # type of entry
                compression: int  # compression; 0 if none
                raw_name: bytes  # 1-16 characters, \0 padded

                # _ is a "dummy" short, we can just ignore it when reading the file
                offset, disk_size, size, entry_type, compression, _, raw_name = struct.unpack('lllcch16s', lump)

                new_entry = Entry(wad=new_wad,
                                  offset=offset,
                                  disk_size=disk_size,
                                  size=size,
                                  entry_type=entry_type.decode(),
                                  compression=compression,
                                  name=raw_name.decode()
                                  )
                new_wad.entries.append(new_entry)

                f.seek(offset)
                # '16sII4I' 40
                texture_name = f.read(16).split(b'\0', 1)[0].decode()  # '16s'
                width, height = struct.unpack('II', f.read(8))
                mip_offsets = struct.unpack('4I', f.read(16))  # offset from start of texture file

                # this gets us the data for each mipmap, which are just hex values pointing at palette indexes
                # ex: so x07 is 7, which points at index 7, which is the 8th color, which is (107, 107, 107) in Quake's palette
                mips: list[MipMap] = []
                for i in range(4):
                    f.seek(offset + mip_offsets[i])
                    mipsize = (width * height) // (4 ** i)
                    data = f.read(mipsize)
                    mips.append(MipMap(width // (2 ** i), height // (2 ** i), data))

                new_tex = MipTex(texture_name, width, height, mip_offsets, mips)
                new_wad.textures.append(new_tex)
                f.seek(orig + 32)

        return new_wad


class Entry:
    def __init__(self, *, wad, offset: int, disk_size: int, size: int, entry_type: str, compression, name: str):
        self.wad = wad
        self.offset = offset
        self.disk_size = disk_size
        self.size = size
        self.entry_type = entry_type
        self.compression = compression
        self.name = name


class MipMap:
    def __init__(self, width: int, height: int, data: bytes):
        self.width = width
        self.height = height
        self.data = data

    @property
    def data_as_ints(self) -> list[int]:
        return list(self.data)

    @property
    def data_as_colors(self) -> list[tuple[int, int, int]]:
        return [palette.QUAKE[i] for i in self.data_as_ints]

    def to_image(self) -> Image.Image:
        img = Image.new('RGB', (self.width, self.height))
        img.putdata(self.data_as_colors)
        return img

    def __str__(self) -> str:
        return f'({self.width}, {self.height})'


class MipTex:
    mipmaps: list[MipMap] = []  # max 4, each mipmap is /2 w and h of the previous
    mip_offsets = (-1,) * 4

    def __init__(self, name: str, width: int, height: int, mip_offsets: list[int] | tuple, mipmaps: list[MipMap]):
        self.name = name  # max 16 characters
        self.width = width
        self.height = height
        self.mip_offsets = mip_offsets
        self.mipmaps = mipmaps

    def __repr__(self) -> str:
        return (f"MipTex(name='{self.name}', width={self.width}, height={self.height}, "
                f"mip_offsets={self.mip_offsets}, mipmaps={self.mipmaps})")

    def __str__(self) -> str:
        return f'{self.name} {self.width} {self.height}'


if __name__ == '__main__':
    print('~~~')
    w = WAD.from_file(r"I:\Quake\Dev\wad\rabbit_june.wad")
    w.textures[0].mipmaps[0].to_image()
    for x in w.textures:
        print(x)
