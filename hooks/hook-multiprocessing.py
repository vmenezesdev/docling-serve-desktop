"""
PyInstaller hook for multiprocessing to prevent --multiprocessing-fork errors.
"""

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('multiprocessing')
