"""
Runtime hook for PyInstaller to fix multiprocessing issues.
This runs before the main script when frozen.
"""

import sys
import os

# Fix for PyInstaller multiprocessing
if sys.platform == 'win32':
    import multiprocessing
    import multiprocessing.spawn

    # Force spawn mode on Windows to avoid fork-related issues
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # Already set, ignore
        pass

    # NOTE: Do NOT clean sys.argv here. 
    # Cleaning arguments here removes the --multiprocessing-fork flag
    # which prevents multiprocessing.freeze_support() from detecting child processes,
    # causing an infinite loop of spawned processes.
    # Argument cleaning is handled in docling_serve_desktop_launcher.py AFTER freeze_support().

# Set environment variable to indicate frozen mode
os.environ['PYINSTALLER_FROZEN'] = '1'
