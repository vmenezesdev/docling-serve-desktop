#!/usr/bin/env python3
"""
Build script for creating the Docling Serve Desktop installer using Inno Setup.

This script:
1. Checks if Inno Setup is installed
2. Builds the portable executable if needed
3. Runs Inno Setup to create the installer

Usage:
    python build_installer.py [--skip-build] [--clean]

Options:
    --skip-build    Skip building the portable executable (use existing build)
    --clean         Clean previous build artifacts before building
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def find_inno_setup():
    """Find the Inno Setup compiler (ISCC.exe) on the system."""
    # Common installation paths
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Try to find it in PATH
    try:
        result = subprocess.run(
            ["where", "ISCC.exe"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n')[0]
    except subprocess.CalledProcessError:
        pass

    return None


def check_build_exists():
    """Check if the portable build exists."""
    dist_dir = Path("dist/DoclingServeDesktop")
    exe_path = dist_dir / "DoclingServeDesktop.exe"
    return exe_path.exists()


def build_portable(clean=False):
    """Build the portable executable using build_portable.py."""
    print("Building portable executable...")

    cmd = [sys.executable, "build_portable.py"]
    if clean:
        cmd.append("--clean")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("ERROR: Failed to build portable executable")
        return False

    return True


def build_installer(iscc_path):
    """Build the installer using Inno Setup."""
    print(f"\nBuilding installer with Inno Setup...")
    print(f"Using ISCC at: {iscc_path}")

    # Run Inno Setup compiler
    result = subprocess.run([iscc_path, "installer.iss"])

    if result.returncode != 0:
        print("ERROR: Failed to build installer")
        return False

    print("\n" + "="*60)
    print("SUCCESS! Installer created successfully.")
    print("="*60)

    installer_path = Path("installer_output/DoclingServeDesktop-Setup.exe")
    if installer_path.exists():
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        print(f"\nInstaller location: {installer_path.absolute()}")
        print(f"Installer size: {size_mb:.1f} MB")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Build the Docling Serve Desktop installer"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building the portable executable (use existing build)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean previous build artifacts before building"
    )

    args = parser.parse_args()

    print("="*60)
    print("Docling Serve Desktop - Installer Builder")
    print("="*60)

    # Check if Inno Setup is installed
    iscc_path = find_inno_setup()
    if not iscc_path:
        print("\nERROR: Inno Setup not found!")
        print("\nPlease install Inno Setup from:")
        print("https://jrsoftware.org/isdl.php")
        print("\nDownload and install 'Inno Setup 6' (or later)")
        return 1

    print(f"\nFound Inno Setup at: {iscc_path}")

    # Build portable executable if needed
    if not args.skip_build:
        if not build_portable(clean=args.clean):
            return 1
    else:
        # Check if build exists
        if not check_build_exists():
            print("\nERROR: Portable build not found!")
            print("Please run without --skip-build to build first, or")
            print("run: python build_portable.py")
            return 1
        print("\nUsing existing portable build...")

    # Build installer
    if not build_installer(iscc_path):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
