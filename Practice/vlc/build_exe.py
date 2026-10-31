"""
build_exe.py — Package Mediastage into a single standalone executable
with PyInstaller (no Python installation required on the target machine,
and no terminal window ever appears).

Usage:
    pip install pyinstaller
    python build_exe.py

Output: dist/Mediastage(.exe)
"""
import subprocess
import sys

def main():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",          # no terminal window
        "--onefile",            # single executable
        "--name", "Mediastage",
        "--collect-all", "av",  # bundle PyAV's FFmpeg shared libraries
        "app.py",
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\nDone. Find your executable in the dist/ folder.")

if __name__ == "__main__":
    main()
