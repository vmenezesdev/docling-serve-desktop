# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for creating a portable Docling Serve Desktop executable.

This builds a standalone .exe with all dependencies embedded, including:
- RapidOCR for OCR functionality
- PyWebView for desktop UI
- All required models and artifacts
- Docling and its dependencies

Usage:
    pyinstaller build_portable.spec
"""

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all submodules for key packages
hidden_imports = [
    # Docling core modules
    'docling',
    'docling_core',
    'docling_serve',
    'docling_serve.app',
    'docling_serve.desktop',
    'docling_serve.settings',
    'docling_serve.storage',

    # RapidOCR and dependencies (included by default)
    'rapidocr',
    'rapidocr_onnxruntime',
    'rapidocr_paddle',
    'onnxruntime',

    # FastAPI and web server
    'fastapi',
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.websockets',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'starlette',
    'starlette.routing',
    'starlette.middleware',

    # PyWebView for desktop window
    'webview',
    'webview.platforms',
    'webview.platforms.winforms',

    # Other dependencies
    'pydantic',
    'pydantic_settings',
    'typer',
    'rich',
    'httpx',
    'websockets',
    'multipart',
    'scalar_fastapi',

    # PyTorch (CPU version)
    'torch',
    'torchvision',

    # Gradio UI (optional)
    'gradio',
    'gradio_client',
    'gradio._simple_templates',
    'groovy',
    'safehttpx',

    # Additional Gradio/UI dependencies
    'jinja2',
    'jinja2.ext',
    'markdown_it_py',
    'ffmpy',

    # HTTP/Network
    'httpx',
    'httpcore',
    'httpcore._sync',
    'httpcore._async',
    'h11',

    # Multiprocessing support
    'multiprocessing',
    'multiprocessing.spawn',
    'multiprocessing.pool',
    'multiprocessing.synchronize',
    'multiprocessing.managers',
    'multiprocessing.shared_memory',
]

# Collect additional submodules
hidden_imports += collect_submodules('docling')
hidden_imports += collect_submodules('docling_core')
hidden_imports += collect_submodules('docling_serve')
hidden_imports += collect_submodules('rapidocr')
hidden_imports += collect_submodules('onnxruntime')
hidden_imports += collect_submodules('gradio')
hidden_imports += collect_submodules('httpx')
hidden_imports += collect_submodules('uvicorn')

# Collect data files
# NOTE: Many packages require their data files (version.txt, py.typed, templates, etc.)
# to be explicitly collected for PyInstaller. Missing data files cause FileNotFoundError
# at runtime. Always add packages here if you encounter such errors.
datas = []

# Core application packages
datas += collect_data_files('docling', include_py_files=True)
datas += collect_data_files('docling_core', include_py_files=True)
datas += collect_data_files('docling_serve', include_py_files=True)
datas += collect_data_files('rapidocr', include_py_files=True)
datas += collect_data_files('onnxruntime', include_py_files=True)

# Web framework and API packages
datas += collect_data_files('fastapi', include_py_files=True)
datas += collect_data_files('starlette', include_py_files=True)
datas += collect_data_files('uvicorn', include_py_files=True)
datas += collect_data_files('httpx', include_py_files=True)
datas += collect_data_files('pydantic', include_py_files=True)

# Gradio UI and its dependencies (require version.txt files)
datas += collect_data_files('gradio', include_py_files=True)
datas += collect_data_files('gradio_client', include_py_files=True)
datas += collect_data_files('safehttpx', include_py_files=True)  # Has version.txt
datas += collect_data_files('groovy', include_py_files=True)  # Has version.txt

# UI/Template packages
datas += collect_data_files('jinja2', include_py_files=True)
datas += collect_data_files('rich', include_py_files=True)
datas += collect_data_files('typer', include_py_files=True)
datas += collect_data_files('ffmpy', include_py_files=True)

# ML/AI packages
datas += collect_data_files('huggingface_hub', include_py_files=True)
datas += collect_data_files('transformers', include_py_files=True)

# Binary dependencies (ONNX Runtime, etc.)
binaries = []

a = Analysis(
    ['docling_serve_desktop_launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/runtime_hook_multiprocessing.py'],
    excludes=[
        # Exclude testing and development packages
        'pytest',
        'pytest_asyncio',
        'mypy',
        'ruff',
        'pre_commit',
        # Exclude unnecessary OCR engines to reduce size
        'tesserocr',
        'easyocr',
        # Exclude CUDA/GPU packages (use CPU only)
        'cupy',
        'cupyx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DoclingServeDesktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to True to see logs, False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,  # Disable argv emulation to prevent --multiprocessing-fork issues
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add an icon file path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DoclingServeDesktop',
)
