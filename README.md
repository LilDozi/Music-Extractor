# Music-Extractor

A simple Python script to extract audio from video files using `ffmpeg`.

## Requirements
- Python 3.10+
- `ffmpeg` installed and available on the system PATH
- Install Python dependencies with `pip install -r requirements.txt`

## Usage
Run the script specifying an input video file and the desired output audio file.
The output file extension determines the format. Optionally set the codec via
`--codec`.

```bash
python extract_audio.py input.mp4 output.mp3
```

Example with explicit codec:
```bash
python extract_audio.py input.mov output.ogg --codec vorbis
```

