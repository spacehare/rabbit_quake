from pathlib import Path
import zipfile
import py7zr
import app.paths as paths
import app.settings as settings
import argparse
from app.settings import Settings
import app.bcolors as bc
import shutil
import struct
import app.parse as parse

# https://github.com/matthewearl/pyquake/tree/master/pyquake

# https://quakewiki.org/wiki/.pak
# http://justsolve.archiveteam.org/wiki/Quake_PAK

# https://quakewiki.org/wiki/Quake_BSP_Format
# https://quakewiki.org/wiki/BSP2

whitelist_map = Settings.jampack_whitelist


def ex(bsp_path: Path):
    with open(bsp_path, 'rb') as f:
        f.read(4)
        header = f.read(48)
        lumps = struct.unpack('12I', header)
        # print(lumps)

        offset = lumps[0]
        length = lumps[1]

        f.seek(offset)
        data = f.read(length)

        text: str = data.decode('utf-8')

        for line in text.split('\n'):
            if 'sounds' in line:
                print(line)
        exit()
    # bsp = bsp_tool.load_bsp(str(bsp_path))
    # print(bsp_path)
    # print(bsp)

    # entities: bsp_tool.QuakeBsp = bsp.headers['ENTITIES']
    # print(bsp.headers['ENTITIES'].as_tuple())
    # print(dir(bsp.headers['ENTITIES']))
    # exit()


def check(file: Path):
    for relationship in whitelist_map:
        for pattern in relationship.patterns:
            if file.match(pattern):
                return relationship.dest


def get_submissions(in_folder: Path, out_folder: Path):
    submissions = in_folder.glob('*')

    # create folders that don't yet exist
    for relationship in whitelist_map:
        actual_folder = out_folder / relationship.dest
        if not actual_folder.exists():
            actual_folder.mkdir(parents=True)

    for idx, submission in enumerate(submissions):
        print(f'{idx + 1}.', bc.colorize(submission, bc.bcolors.OKBLUE))

        if submission.is_dir():
            for item in submission.rglob('*'):
                if item.is_dir():
                    continue
                print('  -', item)
                if item.suffix == '.bsp':
                    ex(item)
                result = check(item)
                if result:
                    print(item)
                    # shutil.copy(item, out_folder / result)
        elif submission.suffix == '.zip':
            # https://stackoverflow.com/questions/4917284/extract-files-from-zip-without-keeping-the-structure-using-python-zipfile
            with zipfile.ZipFile(submission) as archive:
                for member in archive.infolist():
                    path = Path(member.filename)
                    # print('PATH', path.parts[0])
                    if member.is_dir():
                        continue
                    result = check(path)
                    if result:
                        print('  -', path)
                        # print('OUT ->', out_folder / result_path)
                        # print('??', path.relative_to(submission.stem))
                        # member.filename = str(path.relative_to(path.parts[0]))
                        member.filename = str(path.name)
                        archive.extract(member, out_folder / result)

                    else:
                        print('  x', path)

        elif submission.suffix == '.7z':
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path,
                        help='the folder containing submissions, can be zip files, 7z files, or subfolders')
    parser.add_argument('output', type=Path,
                        help='...')
    args = parser.parse_args()

    folder = args.folder
    output = args.output

    if folder == output:
        print('input cannot be same as output')
        exit()

    get_submissions(folder, output)
