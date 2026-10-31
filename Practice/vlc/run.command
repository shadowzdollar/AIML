#!/bin/bash
# Double-click this file in Finder to launch Mediastage.
# (First time only: right-click -> Open, to bypass Gatekeeper's
# "unidentified developer" warning for unsigned scripts.)
cd "$(dirname "$0")"
pythonw app.py 2>/dev/null || python3 app.py
