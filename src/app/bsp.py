import struct
from pathlib import Path
import app.parse as parse

# TODO make sure this works with bsp and bsp2 files


def read_bsp(bsp_path: Path):
    with open(bsp_path, 'rb') as f:
        x = f.read(4)  # idk why i need to do this, but i do
        print(x)
        # TODO FOR FUTURE RABBIT: the above 4 bytes are being read and then passed over, try printing them !!!!!
        header = f.read(48)
        lumps = struct.unpack('12I', header)

        offset = lumps[0]
        length = lumps[1]

        f.seek(offset)
        data = f.read(length)

        text: str = data.decode('utf-8')

        tb_objects = parse.parse(text)
        return tb_objects
