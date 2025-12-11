#!/usr/bin/env python3
"""
Build script for creating a portable Docling Serve Desktop executable.

This script:
1. Checks if PyInstaller is installed
2. Installs RapidOCR and dependencies if not present
3. Builds the executable using PyInstaller
4. Creates a portable distribution folder

Usage:
    python build_portable.py [--clean] [--no-upx]
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller installed")


def check_rapidocr():
    """Check if RapidOCR is installed."""
    try:
        import rapidocr
        print(f"✓ RapidOCR found")
        return True
    except ImportError:
        print("✗ RapidOCR not found")
        return False


def install_rapidocr():
    """Install RapidOCR and dependencies."""
    print("Installing RapidOCR and dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "rapidocr>=3.3,<4.0.0",
        "onnxruntime>=1.7.0,<2.0.0"
    ])
    print("✓ RapidOCR and ONNX Runtime installed")


def install_desktop_dependencies():
    """Install desktop dependencies."""
    print("Installing desktop dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "-e", ".[desktop,rapidocr,ui]"
    ])
    print("✓ Desktop dependencies installed")


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    dirs_to_remove = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_name}/")

    # Remove .spec related files
    for spec_file in Path(".").glob("*.spec.bak"):
        spec_file.unlink()
        print(f"  Removed {spec_file}")

    print("✓ Build artifacts cleaned")


def build_executable(use_upx=True):
    """Build the executable using PyInstaller."""
    print("\nBuilding portable executable...")
    print("This may take several minutes...\n")

    cmd = [sys.executable, "-m", "PyInstaller", "build_portable.spec"]

    if not use_upx:
        cmd.append("--noupx")

    try:
        subprocess.check_call(cmd)
        print("\n✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error code {e.returncode}")
        return False


def create_portable_package():
    """Create a portable package with README."""
    print("\nCreating portable package...")

    dist_dir = Path("dist/DoclingServeDesktop")
    if not dist_dir.exists():
        print("✗ Distribution directory not found")
        return False

    # Create README for portable version
    readme_content = """# Docling Serve Desktop - Portable Edition

This is a portable version of Docling Serve Desktop with all dependencies embedded.

## What's Included

- Docling document processing engine
- RapidOCR for optical character recognition (OCR)
- Web UI powered by Gradio
- Desktop application wrapper
- All required models and dependencies

## How to Run

1. Navigate to this folder
2. Double-click `DoclingServeDesktop.exe` or run from command line:
   ```
   DoclingServeDesktop.exe desktop
   ```

## Command Line Options

To see all available options:
```
DoclingServeDesktop.exe --help
```

### Desktop Mode (Default)
```
DoclingServeDesktop.exe desktop
```

Optional parameters:
- `--host 127.0.0.1` - Host address (default: 127.0.0.1)
- `--port 5001` - Port number (default: 5001)
- `--window-title "My Title"` - Custom window title
- `--width 1200` - Window width in pixels
- `--height 800` - Window height in pixels

### Server Mode
Run as a server without desktop window:
```
DoclingServeDesktop.exe run --port 8080
```

## Troubleshooting

### Application won't start
- Check if port 5001 is already in use
- Try running from command line to see error messages
- Check Windows Firewall settings

### OCR not working
- RapidOCR is included by default and should work out of the box
- Check console output for error messages

### Models not loading
- The first run may take longer as models are initialized
- Ensure you have enough disk space (at least 5GB free)
- Check internet connectivity for initial model downloads

## Technical Details

- **OCR Engine**: RapidOCR (ONNX Runtime)
- **Python Version**: {python_version}
- **Build Date**: {build_date}
- **Version**: 1.9.0

## License

MIT License - See main project repository for details.

## Support

For issues and support, visit:
https://github.com/docling-project/docling-serve

---
Generated with Docling Serve Portable Builder
"""

    import datetime
    readme_content = readme_content.format(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        build_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    readme_path = dist_dir / "README.txt"
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"  Created {readme_path}")

    # Create a simple batch file launcher
    launcher_content = """@echo off
echo Starting Docling Serve Desktop...
echo.
DoclingServeDesktop.exe desktop
pause
"""

    launcher_path = dist_dir / "Start Docling Desktop.bat"
    launcher_path.write_text(launcher_content, encoding="utf-8")
    print(f"  Created {launcher_path}")

    print("\n✓ Portable package created successfully!")
    print(f"\nLocation: {dist_dir.absolute()}")
    print("\nYou can now:")
    print(f"  1. Copy the entire '{dist_dir.name}' folder anywhere")
    print(f"  2. Run 'Start Docling Desktop.bat' or 'DoclingServeDesktop.exe'")
    print(f"  3. No installation or additional downloads required!")

    return True


def main():
    parser = argparse.ArgumentParser(description="Build portable Docling Serve Desktop")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts before building")
    parser.add_argument("--no-upx", action="store_true", help="Disable UPX compression")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    args = parser.parse_args()

    print("=" * 70)
    print("Docling Serve Desktop - Portable Build Script")
    print("=" * 70)
    print()

    # Clean if requested
    if args.clean:
        clean_build()
        print()

    # Check and install dependencies
    if not args.skip_deps:
        print("Checking dependencies...")
        print()

        if not check_pyinstaller():
            install_pyinstaller()

        if not check_rapidocr():
            install_rapidocr()

        print("\nInstalling/updating desktop dependencies...")
        install_desktop_dependencies()
        print()

    # Build executable
    if not build_executable(use_upx=not args.no_upx):
        sys.exit(1)

    # Create portable package
    if not create_portable_package():
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Build completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
