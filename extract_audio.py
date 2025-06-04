import argparse
import subprocess
import shutil
from pathlib import Path


def find_ffmpeg() -> str:
    """Return path to an ``ffmpeg`` executable preferring bundled copies."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / "ffmpeg",
        here / "ffmpeg.exe",
        here / "ffmpeg" / "ffmpeg",
        here / "ffmpeg" / "ffmpeg.exe",
        here / "ffmpeg" / "bin" / "ffmpeg",
        here / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]
    for path in candidates:
        if path.exists():
            return str(path)

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    raise FileNotFoundError("ffmpeg executable not found")

def extract_audio(
    input_file: Path,
    output_file: Path,
    codec: str = "mp3",
    ffmpeg_path: str | Path | None = None,
    log_file: Path | None = None,
) -> str:
    """Extract audio from a video or audio file using ffmpeg.

    Parameters
    ----------
    input_file: Path
        Source file to extract from.
    output_file: Path
        Path of the resulting audio file.
    codec: str
        Audio codec to use.
    ffmpeg_path: str | Path | None
        Optional explicit path to ffmpeg. If ``None`` a search is performed via
        :func:`find_ffmpeg`.
    log_file: Path | None
        Path to a file where ffmpeg output will be written. Defaults to a ``.txt``
        file alongside ``output_file``.

    Returns
    -------
    str
        ffmpeg's combined standard output and error.
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} does not exist")

    ffmpeg = str(ffmpeg_path or find_ffmpeg())

    if log_file is None:
        log_file = output_file.with_suffix(".txt")

    cmd = [
        ffmpeg,
        "-i",
        str(input_file),
        "-vn",
        "-acodec",
        codec,
        str(output_file),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    with open(log_file, "w", encoding="utf-8") as fh:
        fh.write(result.stdout)
        fh.write(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    return result.stdout + result.stderr

def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract audio from video files")
    parser.add_argument("input", type=Path, help="Input video file")
    parser.add_argument("output", nargs="?", type=Path, help="Output audio file")
    parser.add_argument(
        "--codec",
        default="mp3",
        help="Audio codec to use (default: mp3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to place output file (default: same as input)",
    )
    args = parser.parse_args(argv)

    if args.output and args.output_dir:
        parser.error("Specify either an output file or --output-dir, not both")

    if args.output:
        output_file = args.output
    else:
        directory = args.output_dir or args.input.parent
        output_file = directory / f"{args.input.stem}.{args.codec}"

    extract_audio(args.input, output_file, args.codec)

if __name__ == "__main__":
    main()
