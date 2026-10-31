"""
Double-click this file on Windows to launch Mediastage with no console
window (Windows associates .pyw files with pythonw.exe, which has no
terminal attached).

If double-clicking doesn't work, right-click -> Open with -> Python (pythonw).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import main

if __name__ == "__main__":
    main()
