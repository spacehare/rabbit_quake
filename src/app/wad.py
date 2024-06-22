# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm
# https://developer.valvesoftware.com/wiki/WAD

import struct
from pathlib import Path
from PIL import Image
if __name__ == '__main__':
    import palette as pal
else:
    import app.palette as pal


class WAD:
    STRUCT_HEADER = struct.Struct('4sll')
    wad_id: bytes  # ex: b'WAD2'
    dir_offset: int = -1

    def __init__(self):
        self.entries: list[Entry] = []
        self.textures: list[MipTex] = []

    @property
    def header_bytes(self) -> bytes:
        return self.STRUCT_HEADER.pack(self.wad_id, len(self.entries), self.dir_offset)

    @property
    def entries_bytes(self) -> bytes:
        return bytes()

    def write_to_file(self, path: Path):
        buffer = bytearray()

        # reserve header space
        # header = b'\x00' * 12
        # buffer.extend(header)
        pass

    @staticmethod
    def from_images(images: list[Image.Image]):
        pass

    @staticmethod
    def from_folder(folder: Path):
        new_wad = WAD()
        image_paths = [f for f in folder.rglob('*') if f.is_file()]
        dir_offs = WAD.STRUCT_HEADER.size

        current_entry_offset = WAD.STRUCT_HEADER.size
        for path in image_paths:
            print('->', path)
            name = path.stem
            with Image.open(path) as img:
                mipmaps: list[MipMap] = []

                for i in range(4):
                    w = img.width // (2 ** i)
                    h = img.height // (2 ** i)
                    downscaled_img = img.resize((w, h), Image.Resampling.NEAREST)
                    indexes = bytes(pal.image_to_palette_indexes(downscaled_img))
                    mipmaps.append(MipMap(w, h, indexes))

                current_mipmap_offset = MipTex.STRUCT_NO_MIPMAPS.size
                mip_offs = [current_mipmap_offset]
                for i in mipmaps:
                    current_mipmap_offset += len(i.data)
                    if i != mipmaps[3]:
                        mip_offs.append(current_mipmap_offset)
                tex: MipTex = MipTex(name.encode(), img.width, img.height, mip_offs, mipmaps)
                dir_offs += tex.size_in_wad
                entry: Entry = Entry(current_entry_offset, current_mipmap_offset, current_mipmap_offset, 'D', 0, name.encode())
                current_entry_offset += current_mipmap_offset
                new_wad.entries.append(entry)
                new_wad.textures.append(tex)

        new_wad.wad_id = b'WAD2'
        new_wad.dir_offset = dir_offs
        return new_wad

    @staticmethod
    def from_wad_file(path: Path | str):
        new_wad = WAD()
        with open(path, 'rb') as f:
            id, numentries, dir_offs = WAD.STRUCT_HEADER.unpack(f.read(WAD.STRUCT_HEADER.size))
            new_wad.wad_id = id
            new_wad.dir_offset = dir_offs
            if id != b'WAD2':
                raise ValueError(f'file needs to be wad2 format, but is {id}')

            f.seek(dir_offs)
            for _ in range(numentries):
                original_pos = f.tell()
                lump = f.read(Entry.STRUCT.size)

                # get Entry data
                entry = Entry.from_lump(lump)
                new_wad.entries.append(entry)

                # get texture data
                f.seek(entry.offset)
                texture_name = f.read(16)  # '16s'
                width, height = struct.unpack('II', f.read(8))
                mip_offsets = struct.unpack('4I', f.read(16))  # offset from start of texture file

                # this gets us the data for each mipmap, which are just hex values pointing at palette indexes
                # ex: so x07 is 7, which points at index 7, which is the 8th color, which is (107, 107, 107) in Quake's palette
                mipmaps: list[MipMap] = []
                for i in range(4):
                    f.seek(entry.offset + mip_offsets[i])
                    mipsize = (width * height) // (4 ** i)
                    data = f.read(mipsize)
                    mipmaps.append(MipMap(width // (2 ** i), height // (2 ** i), data))

                new_tex = MipTex(texture_name, width, height, mip_offsets, mipmaps)
                new_wad.textures.append(new_tex)
                f.seek(original_pos + Entry.STRUCT.size)

        return new_wad

    def __eq__(self, value: object) -> bool:
        if isinstance(value, WAD):
            checks = [
                self.wad_id == value.wad_id,
                self.dir_offset == value.dir_offset,
                self.textures == value.textures,
            ]
            return all(checks)
        return False


class Entry:
    STRUCT = struct.Struct('lllcch16s')

    def __init__(self, offset: int, disk_size: int, size: int, entry_type: str, compression, raw_name: bytes):
        self.offset = offset  # position of entry in WAD
        self.disk_size = disk_size  # size of entry in WAD
        self.size = size  # size of entry in memory
        self.entry_type = entry_type  # type of entry
        self.compression = compression  # compression; 0 if none
        self.raw_name = raw_name

    @property
    def name(self):
        return self.raw_name.decode()

    @staticmethod
    def from_lump(lump: bytes):
        raw_name: bytes  # 1-16 characters, \0 padded
        # _ is a dummy short, we can just ignore it when reading the file
        offset, disk_size, size, entry_type, compression, _, raw_name = Entry.STRUCT.unpack(lump)

        new_entry = Entry(offset=offset,
                          disk_size=disk_size,
                          size=size,
                          entry_type=entry_type.decode(),
                          compression=compression,
                          raw_name=raw_name
                          )
        return new_entry

    def to_bytes(self) -> bytes:
        return Entry.STRUCT.pack(
            self.offset,
            self.disk_size,
            self.size,
            self.entry_type,
            self.compression,
            0,  # dummy short
            self.raw_name)


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
        return [pal.QUAKE_RGB_TUPLES[i] for i in self.data_as_ints]

    def to_image(self, mode: str = 'p') -> Image.Image:
        mode = mode.upper()
        img = Image.new(mode, (self.width, self.height))
        if mode == 'P':
            img.putpalette(pal.tuples_as_flat_list(pal.QUAKE_RGB_TUPLES))
            img.putdata(self.data)
        elif mode == 'RGB':
            img.putdata(self.data_as_colors)
        else:
            raise ValueError('image mode must be P or RGB')

        return img

    def __str__(self) -> str:
        return f'({self.width}, {self.height}), {len(self.data)}'

    # def __repr__(self) -> str:
    #     return f'MipMap(width={self.width}, height={self.height}, data={self.data})'

    def __eq__(self, value: object) -> bool:
        if isinstance(value, MipMap):
            checks = [
                self.width == value.width,
                self.height == value.height,
                self.data == value.data
            ]
            return all(checks)
        return False


class MipTex:
    STRUCT_NO_MIPMAPS = struct.Struct('16sII4I')

    def __init__(self, raw_name: bytes, width: int, height: int, mip_offsets: list[int] | tuple, mipmaps: list[MipMap]):
        self.raw_name = raw_name  # max 16 characters
        self.width = width  # should be divisble by 16
        self.height = height  # should be divisible by 16
        self.mip_offsets = mip_offsets
        self.mipmaps = mipmaps  # max 4, each mipmap is /2 w and h of the previous

    def __repr__(self) -> str:
        return (f"MipTex(name='{self.name}', width={self.width}, height={self.height}, "
                f"mip_offsets={self.mip_offsets}, mipmaps={self.mipmaps})")

    def __str__(self) -> str:
        return f'{self.name} {self.width} {self.height}'

    @property
    def name(self):
        return self.raw_name.split(b'\0', 1)[0].decode()

    @property
    def size_in_wad(self):
        return MipTex.STRUCT_NO_MIPMAPS.size + sum([m.height * m.width for m in self.mipmaps])

    # @staticmethod
    # def from_lump(lump: bytes):
    #     return

    @property
    def to_bytes(self) -> bytes:
        return self.STRUCT_NO_MIPMAPS.pack(self.name, self.width, self.height, *self.mip_offsets)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, MipTex):
            checks = [
                self.name == value.name,
                self.width == value.width,
                self.height == value.height,
                list(self.mip_offsets) == list(value.mip_offsets),
                self.mipmaps == value.mipmaps,
            ]
            return all(checks)
        return False


if __name__ == '__main__':
    print('####### wad folder ##########')
    wadfolder = WAD.from_folder(Path(r'I:\TEX\june'))

    print('####### wad file ##########')
    wadfile = WAD.from_wad_file(r"I:\Quake\Dev\wad\rabbit_june.wad")  # 424 bytes

    print('####### wad for loop ##########')
    for n, w in [('folder', wadfolder), ('wad', wadfile)]:
        w: WAD = w
        print('-----', n)
        print(f'dir_offs: {w.dir_offset} - entries: {len(w.entries)} - textures: {len(w.textures)}')
        print('  entries:')
        for e in w.entries:
            print(f'    - {e.name} -',  'offs:', e.offset, '- sizes:', e.disk_size, e.size)
        print('  textures:')
        for t in w.textures:
            print(f'    - {t.name} -',  'wh:', t.width, t.height, '- mm_offs:', t.mip_offsets)

    print(wadfile == wadfolder)
