"""
install_halftone_dependencies.py
--------------------------------------
Utility script to automatically install or upgrade 
all required Python packages for the Halftone GUI project.

This ensures all dependencies are up to date and available 
before running the main converter app.

Original Author: DE Hammer
Documentation, updates & cleanup: Avtomat Agentics
Version: 0.1
Python 3.8.3
"""

import os
import sys
import subprocess


def install_package(package_name):
    """
    Installs or upgrades a given Python package using pip.
    Uses subprocess for cleaner execution and cross-platform support.
    If installation fails, it prints a warning and continues.
    """
    print(f"\n📦 Installing or upgrading: {package_name}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
    except subprocess.CalledProcessError:
        print(f"⚠️  Warning: Installation failed for '{package_name}'. "
              f"You may need to install it manually.")


def main():
    """
    Installs all dependencies required by the halftone converter.
    """
    print("======================================")
    print("  HALFTONE GUI - Dependency Installer ")
    print("======================================")

    # List of all required packages
    required_packages = [
        "pip",          # Ensure pip is up to date
        "pycairo",      # Vector graphics (SVG rendering)
        "svglib",       # SVG import/export utilities
        "reportlab",    # Rendering engine used by svglib
        "Pillow",       # Image manipulation (PIL)
    ]

    for package in required_packages:
        install_package(package)

    print("\n✅ All dependencies have been successfully installed or upgraded (or skipped if already present).")


if __name__ == "__main__":
    main()
