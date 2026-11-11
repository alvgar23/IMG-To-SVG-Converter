# -*- coding: utf-8 -*-

"""
create_halftone_folders.py
--------------------------------------
Utility script to set up the folder structure required 
for the Halftone GUI converter.

This dynamic version automatically creates the necessary 
directories relative to the script location (instead of 
forcing them onto the Desktop).

Original Author: DE Hammer
Documentation, updates & cleanup: Avtomat Agentics
Version: 0.1
Python 3.8.3
"""

import os
from pathlib import Path


def create_folders():
    """
    Creates all the subfolders needed by the halftone GUI project
    in the same directory where this script is located.
    """

    # Get the base directory where the script is located
    base_dir = Path(__file__).resolve().parent
    print(f"Base directory: {base_dir}")

    # Define required subfolders (relative to this base path)
    main_folder   = base_dir
    save_folder   = base_dir / "SAVE FOLDER"
    json_folder   = base_dir / "JSON"
    svg_folder    = base_dir / "SVG"
    image_folder  = base_dir / "IMAGE"
    python_folder = base_dir / "PYTHON"

    # Group all folder paths in a list
    folders = [main_folder, save_folder, json_folder, svg_folder, image_folder, python_folder]

    # Create each folder if it doesn’t exist
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    print("✅ Folder structure ready!")


# Run the folder creation function
if __name__ == "__main__":
    create_folders()
