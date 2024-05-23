import argparse
import wave
import pydub
from pathlib import Path
import subprocess

# ffmpeg -i input.mp3 output.wav
# ffmpeg -i input.mp3 -ac 1 -ar 44100 -sample_fmt s16 output.wav


def convert_with_ffmpeg(file: Path, output_parent: Path):
    subprocess.run([
        'ffmpeg',
        '-i', file,
        '-ac', '1',
        '-ar', '44100',
        '-sample_fmt', 's16',
        output_parent / file.with_suffix('.wav').name
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', type=Path)
    parser.add_argument('output_path', type=Path)
    args = parser.parse_args()

    input_path: Path = args.input_path
    output_path: Path = args.output_path

    if input_path.is_file():
        convert_with_ffmpeg(input_path, output_path)
    else:
        for file in input_path.rglob('*'):
            if file.is_file():
                convert_with_ffmpeg(file, output_path)
