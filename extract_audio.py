import argparse
import os
import subprocess
import sys
from pathlib import Path
import shutil

def _find_ffmpeg() -> str:
    """Return path to ffmpeg, checking environment and local copies first."""
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path:
        return env_path

    script_dir = Path(__file__).resolve().parent
    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    local_ffmpeg = script_dir / exe_name
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    return shutil.which("ffmpeg") or "ffmpeg"


def extract_audio(input_file: Path, output_file: Path, codec: str = "mp3", log_file: Path | None = None) -> None:
    """Extracts audio from a video file using ffmpeg.

    If ``log_file`` is provided, ffmpeg's combined stdout/stderr will be written
    to that file in addition to being forwarded to stdout.
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} does not exist")

    ffmpeg_bin = _find_ffmpeg()
    cmd = [
        ffmpeg_bin,
        "-i",
        str(input_file),
        "-vn",
        "-acodec",
        codec,
        str(output_file),
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.stdout is not None
    log_handle = open(log_file, "w", encoding="utf-8") if log_file else None
    try:
        for line in proc.stdout:
            if log_handle:
                log_handle.write(line)
            print(line, end="")
        proc.wait()
    finally:
        if log_handle:
            log_handle.close()

    if proc.returncode != 0:
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
    parser.add_argument(
        "--log",
        type=Path,
        help="Optional path to write ffmpeg output",
    )
    args = parser.parse_args(argv)
    extract_audio(args.input, args.output, args.codec, args.log)

if __name__ == "__main__":
    main()
