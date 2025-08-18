exit()
from src.app.deps import DependencyPattern, Relationship
from src.app import deps
from src.app import bsp
from src.app.settings import Settings
import src.app.bcolors as bcolors
import zipfile
import py7zr
import argparse
import shutil
from pathlib import Path



_whitelist_map = Settings.jampack_whitelist


def dest_from_whitelist(file: Path):
    for relationship in _whitelist_map:
        for pattern in relationship.patterns:
            if file.match(pattern):
                return relationship.dest


# def file_from_pattern(file: Path, patterns):
#     for pattern in patterns:
#         if file.match(pattern):
#             return file


def get_valid_files(submission_files: list[Path]):
    return
    # TODO i need to get the proper path put into the output folder
    # so ex:
    #   file match: dogjam_rabbit/gfx/env/rabbit/mak_nightsky1_bk.tga
    #   tb key:     rabbit/mak_nightsky1_
    # should go to:
    #   gfx/env/rabbit/mak_nightsky1_bk.tga
    # NOT to:
    #   gfx/env/mak_nightsky1_bk.tga

    bsp_file: Path
    valid_set: set[tuple[Path, Path | None]] = set()
    invalid_set: set[Path] = set()
    dep_patterns = []

    # go through all the files
    for item in submission_files:
        # get dependency patterns from the bsp
        if item.suffix == '.bsp':
            bsp_file = item
            dep_patterns = deps.get_dep_patterns(bsp.read_bsp(bsp_file).entities, Settings.dependency_patterns)

    # find the files from the dependency patterns
    for item in submission_files:
        fail = False
        if item.is_dir():
            continue
        for dp, dest in dep_patterns:
            if item.match(dp):
                valid_set.add((item, dest))  # TODO should probably maybe be a namedtuple? idk figure it out tomorrow. ^^^ read above todo
                print(' dp', dp)
            else:
                fail = True

        if fail:
            invalid_set.add(item)

        desti = dest_from_whitelist(item)
        if desti:
            valid_set.add((item, desti))
            print(' =>', item)

    invalid_set.difference_update(valid_set)
    for thing in valid_set:
        print(' >> -', bcolors.colorize(thing, bcolors.bcolors.OKBLUE))
    for thing in invalid_set:
        print(' >> x', bcolors.colorize(thing, bcolors.bcolors.FAIL))
    return valid_set


def package_submissions(in_folder: Path, out_folder: Path, should_copy: bool):
    return
    submissions = in_folder.glob('*')

    # create folders that don't yet exist
    for relationship in _whitelist_map:
        actual_folder = out_folder / relationship.dest
        if not actual_folder.exists():
            actual_folder.mkdir(parents=True)

    for idx, submission in enumerate(submissions):
        print(f'{idx + 1}.', bcolors.colorize(submission, bcolors.bcolors.OKBLUE))

        if submission.is_dir():
            files = get_valid_files([p for p in submission.rglob('*')])
            for item, dest in files:
                if should_copy:
                    shutil.copy(item, out_folder / item)

        elif submission.suffix == '.zip2':
            # https://stackoverflow.com/questions/4917284/extract-files-from-zip-without-keeping-the-structure-using-python-zipfile
            with zipfile.ZipFile(submission) as archive:
                for member in archive.infolist():
                    path = Path(member.filename)
                    # print('PATH', path.parts[0])
                    if member.is_dir():
                        continue
                    # result = check_whitelist(path)
                    # if result:
                    #     print('  -', path)
                    #     # print('OUT ->', out_folder / result_path)
                    #     # print('??', path.relative_to(submission.stem))
                    #     # member.filename = str(path.relative_to(path.parts[0]))
                    #     member.filename = str(path.name)
                    #     archive.extract(member, out_folder / result)

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
    parser.add_argument('--copy', '-c', action='store_true',
                        help='copy the files to their destinations within the output folder')
    args = parser.parse_args()

    folder = Path(args.folder)
    output = Path(args.output)
    copy = args.copy

    if folder == output:
        print('input cannot be same as output')
        exit()

    package_submissions(folder, output, copy)
