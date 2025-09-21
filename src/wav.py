import argparse
import subprocess
from pathlib import Path

# ffmpeg -i input.mp3 output.wav
# ffmpeg -i input.mp3 -ac 1 -ar 44100 -sample_fmt s16 output.wav


def ffmpeg_is_audio_file(file: Path) -> bool:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "default=noprint_wrappers=1",
            file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "codec_type=audio" in line:
            return True
    return False


def ffmpeg_convert(file: Path, output_parent: Path):
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            file,
            "-ac",
            "1",
            "-ar",
            "44100",
            "-sample_fmt",
            "s16",
            output_parent / file.with_suffix(".wav").name,
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument(
        "--check", action="store_true", help="check if files are convertable first"
    )
    args = parser.parse_args()

    input_path: Path = args.input_path
    output_path: Path = args.output_path
    check: bool = args.check

    # TODO rewrite
    for file in (input_path,) if input_path.is_file() else input_path.rglob("*"):
        ok = True
        if check:
            ok = ffmpeg_is_audio_file(file)
        if ok and file.is_file():
            # dump everything into one folder
            ffmpeg_convert(file, output_path)

            # preserve folder structure
            # if input_path.is_dir():
            #     idx = file.parts.index(input_path.name)
            #     final = output_path / Path('/'.join(file.parts[idx:]))
            #     final.parent.mkdir(parents=True, exist_ok=True)
            #     ffmpeg_convert(file, final.parent)
