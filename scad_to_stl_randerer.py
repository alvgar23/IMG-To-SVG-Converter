# -*- coding: utf-8 -*-
"""
scad_to_stl_renderer.py
------------------------

A Python-based batch renderer that converts OpenSCAD .scad files
into 3D printable .stl models.

This script scans the SCAD directory for unprocessed files,
renders them automatically using the OpenSCAD command-line interface,
and stores the resulting .stl files in the STL folder.

Each processed SCAD file is renamed with "_converted" to prevent
reprocessing.

Author: Avtomat Agentics
Version: 1.0
Python 3.8+
"""

## =====================================================
## SCAD TO STL RENDERER (Professional Edition)
## -----------------------------------------------------
## This script automates OpenSCAD rendering operations
## for halftone or procedural .scad models. It converts
## all pending SCAD files to STL meshes ready for
## slicing or physical production.
##
## Requires OpenSCAD installed and accessible in PATH.
## =====================================================

from pathlib import Path
import subprocess
import os

## ==========================================
## DYNAMIC PATH CONFIGURATION (cross-folder)
## ==========================================

# Base directory of the script (runs from any location)
BASE_DIR = Path(__file__).resolve().parent

# Define folders relative to base directory
SCAD_DIR = BASE_DIR / "SCAD"
STL_DIR  = BASE_DIR / "STL"

# Ensure folders exist
os.makedirs(SCAD_DIR, exist_ok=True)
os.makedirs(STL_DIR, exist_ok=True)

## ==========================================
## OPERATIONAL PARAMETERS
## ==========================================

# Path to OpenSCAD executable (use absolute path if not in PATH)
OPENSCAD_CMD = r"C:\Program Files\OpenSCAD\openscad.exe"

# Optional: rendering resolution and performance settings
OPENSCAD_ARGS = [
    "--hardwarnings",
]

## ==========================================
## CORE FUNCTION: SCAD TO STL CONVERSION
## ==========================================

def convert_scad_to_stl(scad_file: Path):
    """
    Converts a .scad model into an .stl mesh using OpenSCAD CLI.
    """
    print(f"\nProcessing SCAD file: {scad_file.name}")

    stl_path = STL_DIR / f"{scad_file.stem}.stl"

    try:
        # Execute OpenSCAD via subprocess
        result = subprocess.run(
            [OPENSCAD_CMD, "-o", str(stl_path)] + OPENSCAD_ARGS + [str(scad_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  STL file generated: {stl_path.name}")

    except subprocess.CalledProcessError as e:
        print(f"  Rendering failed for {scad_file.name}")
        print(f"  Error: {e.stderr.strip()}")
        return
    except FileNotFoundError:
        print("  OpenSCAD executable not found. Please check OPENSCAD_CMD path.")
        return

    # Rename the SCAD file to mark it as processed
    converted_path = scad_file.with_name(scad_file.stem + "_converted.scad")
    try:
        scad_file.rename(converted_path)
        print(f"  Marked as converted: {converted_path.name}")
    except Exception as e:
        print(f"  Could not rename SCAD file: {e}")

## ==========================================
## MAIN EXECUTION LOOP
## ==========================================

def main():
    """
    Main control function that scans the SCAD directory,
    renders all unprocessed SCAD files, and exports them
    as STL models.
    """
    print("===============================================")
    print("        SCAD TO STL RENDERER v1.0              ")
    print("===============================================\n")

    scad_files = list(SCAD_DIR.glob("*.scad"))

    if not scad_files:
        print("No SCAD files found in the SCAD directory.\n")
        return

    for scad_file in scad_files:
        if scad_file.name.endswith("_converted.scad"):
            continue
        convert_scad_to_stl(scad_file)

    print("\nAll available SCAD files have been processed.\n")
    print(f"Output STL files stored in: {STL_DIR.resolve()}")

## ==========================================
## ENTRY POINT
## ==========================================

if __name__ == "__main__":
    main()
