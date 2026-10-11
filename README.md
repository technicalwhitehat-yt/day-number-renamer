# Day Number Renamer

A lightweight Windows-friendly GUI utility that moves a `Day N` marker to the beginning of video filenames, helping File Explorer sort lessons numerically. It preserves the rest of the title and the file extension.

**No AI, API key, third-party packages, or internet connection required.**

## Demo video

<p align="center">
  <a href="./video.mp4">
    <img src="./thumbnail.png" alt="Day Number Renamer Demo Thumbnail" width="100%">
  </a>
</p>

<p align="center">
  ▶️ <strong>Click the thumbnail to watch the demo!</strong>
</p>

## Example

Before:

```text
Variables and Data Types in Python_Python Tutorial - Day_6(1080P_HD).mp4
Our First Python Program_Python Tutorial - Day_4(1080P_HD).mp4
Recursion in Python_Python Tutorial - Day_30(1080P_HD).mp4
```

After:

```text
Day 006 Variables and Data Types in Python_Python Tutorial (1080P_HD).mp4
Day 004 Our First Python Program_Python Tutorial (1080P_HD).mp4
Day 030 Recursion in Python_Python Tutorial (1080P_HD).mp4
```

The tool removes only the detected `Day N` marker from its old position, puts it first with three-digit padding, and normalizes separator whitespace. Other title words and the extension are preserved.

## Features

- Simple graphical interface with folder picker.
- Preview proposed names before applying changes.
- Supports common video formats: MP4, MKV, MOV, AVI, WMV, FLV, WebM, M4V, MPG, MPEG, TS, M2TS, 3GP, OGV and VOB.
- Detects variants such as `Day_6`, `Day 6`, and `Day-006` (case-insensitive).
- Skips files without a detected Day number.
- Checks for existing-name conflicts before renaming.
- Processes only files directly inside the selected folder; subfolders are not changed.
- Uses Python's standard library only.

## Requirements

- Python 3.10 or newer recommended.
- Windows, macOS, or Linux with Tkinter available. The app is designed with Windows in mind.
- No `pip install` step is needed.

## Run

1. Install Python from [python.org](https://www.python.org/downloads/) if needed. On Windows, enable **Add Python to PATH** during installation.
2. Download or clone this repository.
3. Run:

   ```bash
   python day_number_renamer.py
   ```

4. Click **Browse folder…** and select your video folder.
5. Review the preview.
6. Click **Apply rename** and confirm.

## Safety notes

- Always test on a copy of important files first.
- The app displays a preview and requires confirmation before changing filenames.
- Files with conflicting target names are skipped; the program does not intentionally overwrite existing files.
- This changes filenames only, not video contents.
- It scans one folder level only; it does not recurse into subfolders.

## How it works

A regular expression detects `Day` followed by a number. The last matching Day marker in a filename is moved to the front, formatted as `Day 001`, `Day 002`, and so on. This zero-padding makes alphabetical sorting follow numerical order up to 999 days.

## Contributing

Issues and pull requests are welcome. If you find a filename pattern that is not detected correctly, open an issue with a sample filename (avoid sharing private files).

## License

MIT. See [`LICENSE`](LICENSE).
