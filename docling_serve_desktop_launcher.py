#!/usr/bin/env python3
"""
Launcher script for Docling Serve Desktop portable executable.

This wrapper handles PyInstaller-specific issues like multiprocessing fork mode
and ensures the application runs correctly as a frozen executable.
"""

import sys
import os
import multiprocessing

def main():
    # Clean up any PyInstaller-related arguments before passing to the app
    # This must happen BEFORE any other processing
    cleaned_argv = [sys.argv[0]]  # Keep the executable name

    for arg in sys.argv[1:]:
        # Skip PyInstaller internal arguments
        if arg.startswith('--multiprocessing'):
            continue
        # Skip parent_pid and other internal multiprocessing arguments
        if '=' in arg and not arg.startswith('--'):
            # This catches arguments like "parent_pid=12345" that aren't CLI options
            # Valid CLI options should start with -- (like --port=8080)
            continue
        cleaned_argv.append(arg)

    # If no command was provided (only the executable name remains), add 'desktop'
    if len(cleaned_argv) == 1:
        cleaned_argv.append('desktop')

    # Replace sys.argv with cleaned version
    sys.argv = cleaned_argv

    # Set the base path to the executable directory
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        os.environ['DOCLING_SERVE_BASE_PATH'] = sys._MEIPASS

    # Ensure multiprocessing uses spawn instead of fork on Windows
    if sys.platform == 'win32':
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            # Already set, ignore
            pass

    # Now import and run the main application
    from docling_serve.__main__ import main as docling_main

    docling_main()

if __name__ == '__main__':
    # CRITICAL: This protection prevents multiprocessing from re-executing the main code
    # when creating child processes in frozen executables
    multiprocessing.freeze_support()
    main()
