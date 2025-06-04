import argparse
import subprocess
import sys
from pathlib import Path

def extract_audio(input_file: Path, output_file: Path, codec: str = "mp3") -> None:
    """Extracts audio from a video file using ffmpeg."""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} does not exist")
    cmd = [
        "ffmpeg",
        "-i",
        str(input_file),
        "-vn",
        "-acodec",
        codec,
        str(output_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError("ffmpeg failed")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract audio from video files")
    parser.add_argument("input", type=Path, help="Input video file")
    parser.add_argument(
        "output",
        type=Path,
        help="Output audio file. Extension determines format",
    )
    parser.add_argument(
        "--codec",
        default="mp3",
        help="Audio codec to use (default: mp3)",
    )
    args = parser.parse_args(argv)
    extract_audio(args.input, args.output, args.codec)

if __name__ == "__main__":
    main()
