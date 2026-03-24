"""Standalone entry point for PyInstaller builds."""
import sys
import os

# When running from PyInstaller bundle, add the bundle dir to path
if getattr(sys, '_MEIPASS', None):
    sys.path.insert(0, sys._MEIPASS)

from src.main import main
main()
