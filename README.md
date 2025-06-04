# Music-Extractor

A simple Python script to extract audio from video files using `ffmpeg`.
If an `ffmpeg` executable is placed alongside the Python files it will be used
automatically, otherwise the system `ffmpeg` on `PATH` is required.

## Requirements
- Python 3.10+
- `ffmpeg` available either in the project folder or on the system PATH
- Install Python dependencies with `pip install -r requirements.txt`

## Usage
Run the script specifying an input video file. By default the audio will be
written to the same folder using the selected codec. You may pass an explicit
output file or a target directory with `--output-dir`. The output file
extension determines the format. Optionally set the codec via `--codec`.

```bash
python extract_audio.py input.mp4
```

Explicit output location:

```bash
python extract_audio.py input.mov --output-dir /tmp --codec vorbis
```

Example with explicit codec:
```bash
python extract_audio.py input.mov output.ogg --codec vorbis

## Graphical Interface

Run `python music_extractor_gui.py` for a minimal desktop interface. Use the
buttons to pick input files and optionally an output folder, choose the output
format, and click **Run Extraction** to process each file. Progress messages and
the full ffmpeg log for each file will appear in the log window as well as in a
`.txt` file alongside the extracted audio.
