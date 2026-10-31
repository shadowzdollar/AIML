# Mediastage — a small, custom-built media player

A fully self-contained desktop player for video and audio, built directly
on FFmpeg's C libraries (`libavformat`, `libavcodec`, `libswscale`,
`libswresample`) via **PyAV** — the same architecture real players use —
with a custom-designed GUI. No command line needed to use it: open it,
drag files in or click a button, and every control lives in the window.

## What's in this folder

| File | Purpose |
|---|---|
| `app.py` | The application — GUI, controls, playlist, drag & drop. **Run this.** |
| `engine.py` | Decode + audio/video sync engine (PyAV + sounddevice). No GUI code. |
| `test_engine.py` | Headless test of the engine (no display/audio device required). |
| `run.pyw` | Windows launcher — double-click, no console window appears. |
| `run.command` | macOS launcher — double-click in Finder. |
| `mediastage.desktop` | Linux desktop entry, for app menus / file manager double-click. |
| `build_exe.py` | Packages everything into one standalone `.exe` with PyInstaller. |

## Using the app

- **Launch it** — double-click `run.pyw` (Windows) or `run.command` (macOS),
  or run `python app.py` from anywhere. No arguments, no setup file needed.
- **Load media** — drag video/audio files (or a whole folder) onto the
  window, or click **Open Files** / **Open Folder** in the sidebar.
- **Everything else is on-screen**: play/pause, seek bar, next/previous,
  mute, volume, and the playlist panel (click any row to jump to it, click
  the chevron to collapse the sidebar).
- **Keyboard**: `Space` play/pause · `M` mute · `←`/`→` seek 5s · `B` toggle
  sidebar.

## Design

The interface is a deliberate departure from the generic dark-UI template —
brass/amber as the primary accent (an analog studio-hardware reference
point, not the usual neon-on-black look), teal for the now-playing
indicator, custom vector-drawn icons (no image assets, no emoji), and a
glowing circular transport button as the one signature element. Sidebar,
transport bar, and empty/drop states are all custom-drawn and themed
consistently — see the `# Design tokens` block at the top of `app.py` if
you want to retheme it (colors, fonts, spacing are all defined there).

## Setup

```bash
pip install -r requirements.txt
```

FFmpeg's shared libraries are required (PyAV links against them):
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: PyAV's wheels usually bundle the needed DLLs already

Then just run `python app.py` — or use one of the double-click launchers
above once you've confirmed it runs.

## Packaging as a true standalone executable

If you want something you (or someone else) can run without Python
installed at all:

```bash
pip install pyinstaller
python build_exe.py
```

This produces a single-file, windowed (no console) executable in `dist/`.
`--collect-all av` in the build script makes sure PyAV's bundled FFmpeg
libraries get included, so it works on a machine with no FFmpeg installed
either.

## Architecture notes

`engine.py` runs a demux/decode thread that fills bounded video/audio
queues, an audio callback (via `sounddevice`) that plays samples and
advances a shared clock, and treats that **audio clock as the sync master**
— video frames are shown once their timestamp is due and dropped if
they're already late, keeping video locked to audio instead of drifting.
If no audio output device is available, it falls back to a wall-clock-based
timer automatically rather than crashing.

`app.py` is the GUI: layout, drawing, input handling, and file dialogs
(via a hidden `tkinter` root, used only for native Open File/Folder
dialogs — everything else is drawn by pygame).

## Known limitations / good next steps
- No subtitle rendering (PyAV can decode subtitle streams; would need text
  overlay rendering added to `app.py`).
- No hardware-accelerated decode (portable by default; could be added via
  PyAV's `HWAccel` support).
- Playlist is session-only — no saved playlists / recent files yet.











in the schedule remove Morning agent setup and add that time to the next action which is ai/ml self study


remove also get ready/travel and add its' time to the next actionw which is java backend study


split the lunch time into 12:10-12:40 fro lunch and from 12:40-13:30 ai/ml self study


and that are applied to the days from mon-friday only and then after feed jarvis new schedule and and reload it  to take it