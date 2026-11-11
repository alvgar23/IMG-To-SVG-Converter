# -*- coding: utf-8 -*-
"""
svg_to_stl_converter_advanced.py
--------------------------------

An adaptive, fault-tolerant converter that transforms halftone SVG files
directly into high-quality STL 3D reliefs without using OpenSCAD.

This version is compatible with both <circle> and Cairo-style <path> elements
and includes an adaptive geometry algorithm that adjusts height and radius
based on local density and contrast.

Author: Avtomat Agentics
Version: 2.1 (Scaled & Optimized Edition)
Python 3.8+
"""

## =====================================================
## SVG TO STL ADAPTIVE HALFTONE CONVERTER
## -----------------------------------------------------
## Detects halftone geometry in SVG files,
## extracts circle or path-based dots, and generates
## detailed 3D STL reliefs using Trimesh.
##
## Adaptive logic analyzes local dot density and radius
## variation to create realistic depth and smooth transitions.
## Now includes unit scaling and mesh simplification.
## =====================================================

from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import os
import math

## ==========================================
## DYNAMIC PATH CONFIGURATION
## ==========================================

BASE_DIR = Path(__file__).resolve().parent
SVG_DIR = BASE_DIR / "SVG"
STL_DIR = BASE_DIR / "STL_3D"

os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(STL_DIR, exist_ok=True)

## ==========================================
## GLOBAL PARAMETERS
## ==========================================

PX_TO_MM = 0.26458333   # SVG pixel to millimeter conversion
H_BASE = 0.4            # Base thickness (mm)
H_MAX_BASE = 5           # Maximum relief height (mm)
EXTRUDE_BASE = True      # Add a solid backing plane
MIN_RADIUS = 0.15        # Prevent zero-radius artifacts
DENSITY_RADIUS = 10      # Distance (in SVG units) for local density evaluation
SIMPLIFY_TARGET = 300000 # Target faces after decimation (approx)

## ==========================================
## HELPER FUNCTIONS
## ==========================================

def extract_circles_from_svg(svg_file):
    """
    Extracts circles and Cairo-style paths from an SVG file.
    Returns a list of tuples (cx, cy, r) already scaled to mm.
    """
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
    except Exception as e:
        print(f"  Failed to parse {svg_file.name}: {e}")
        return []

    circles = []

    # --- 1. Standard <circle> elements ---
    for element in root.iter():
        if element.tag.endswith("circle"):
            try:
                cx = float(element.attrib["cx"]) * PX_TO_MM
                cy = float(element.attrib["cy"]) * PX_TO_MM
                r = float(element.attrib["r"]) * PX_TO_MM
                circles.append((cx, cy, r))
            except Exception:
                continue

    # --- 2. Cairo-style <path> elements ---
    if not circles:
        for element in root.iter():
            if element.tag.endswith("path"):
                d = element.attrib.get("d", "")
                try:
                    tokens = d.replace("M", " ").replace("C", " ").split()
                    nums = [float(x) for x in tokens if x.replace(".", "", 1).replace("-", "", 1).isdigit()]
                    if len(nums) >= 6:
                        cx, cy = nums[0] * PX_TO_MM, nums[1] * PX_TO_MM
                        r_est = (abs(nums[0] - nums[2]) or abs(nums[1] - nums[3])) * PX_TO_MM
                        if r_est > 0:
                            circles.append((cx, cy, r_est))
                except Exception:
                    continue

    return circles


def compute_local_density(circles, cx, cy, radius_scale=1.0):
    """
    Estimates local density around (cx, cy).
    Returns value 0–1 where 1 = high density.
    """
    nearby = sum(1 for (x, y, _) in circles if (x - cx) ** 2 + (y - cy) ** 2 < (DENSITY_RADIUS * radius_scale) ** 2)
    max_ref = 50
    return min(1.0, nearby / max_ref)


def adaptive_height_and_radius(r, r_max, density):
    """
    Computes adaptive height and radius scaling
    depending on the relative radius and local density.
    """
    gamma = 0.75 + 0.3 * (1 - density)
    H_MAX = H_MAX_BASE * (0.8 + 0.3 * (1 - density))
    height = H_BASE + H_MAX * (r / r_max) ** gamma
    scaled_r = max(r * (1.0 + 0.25 * (1 - density)), MIN_RADIUS)
    return height, scaled_r

## ==========================================
## MAIN CONVERSION FUNCTION
## ==========================================

def convert_svg_to_stl(svg_file: Path):
    """
    Converts one SVG halftone file into an STL 3D relief mesh.
    Includes automatic scaling to mm and optional mesh simplification.
    """
    print(f"\nProcessing SVG file: {svg_file.name}")

    circles = extract_circles_from_svg(svg_file)

    if not circles:
        print("  No circle-like geometry found - skipping this file.")
        return

    xs, ys, rs = zip(*circles)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    r_max = max(rs)

    cx_center = (min_x + max_x) / 2
    cy_center = (min_y + max_y) / 2

    meshes = []

    for cx, cy, r in circles:
        density = compute_local_density(circles, cx, cy)
        h, r_scaled = adaptive_height_and_radius(r, r_max, density)
        tx, ty = cx - cx_center, cy - cy_center
        try:
            cyl = trimesh.creation.cylinder(radius=r_scaled, height=h, sections=24)
            cyl.apply_translation([tx, ty, h / 2])
            meshes.append(cyl)
        except Exception:
            continue

    if not meshes:
        print("  No valid geometry created - skipping export.")
        return

    combined = trimesh.util.concatenate(meshes)

    if EXTRUDE_BASE:
        width = (max_x - min_x)
        height_box = (max_y - min_y)
        base = trimesh.creation.box(extents=[width, height_box, H_BASE])
        base.apply_translation([0, 0, H_BASE / 2])
        combined = trimesh.util.concatenate([base, combined])

    # Optional mesh simplification
    try:
        if len(combined.faces) > SIMPLIFY_TARGET:
            print("  Simplifying mesh...")
            combined = combined.simplify_quadratic_decimation(SIMPLIFY_TARGET)
            print("  Simplification complete.")
    except Exception:
        print("  Simplification skipped (unsupported environment).")

    # Export STL
    stl_path = STL_DIR / f"{svg_file.stem}.stl"
    try:
        combined.export(stl_path)
        print(f"  STL generated: {stl_path.name}")
    except Exception as e:
        print(f"  Failed to export STL: {e}")
        return

    # Report model properties
    try:
        print(f"  Bounding box (mm): {combined.bounds}")
        print(f"  Watertight: {combined.is_watertight}")
        print(f"  Faces: {len(combined.faces)}")
    except Exception:
        pass

    # Mark source SVG as converted
    converted_path = svg_file.with_name(svg_file.stem + "_converted.svg")
    try:
        svg_file.rename(converted_path)
        print(f"  Marked as converted: {converted_path.name}")
    except Exception:
        print("  Could not rename source file (likely open elsewhere).")

## ==========================================
## MAIN EXECUTION
## ==========================================

def main():
    print("===============================================")
    print("   HALFTONE SVG -> STL 3D CONVERTER v2.1       ")
    print("         Scaled & Optimized Edition            ")
    print("===============================================\n")

    svg_files = list(SVG_DIR.glob("*.svg"))

    if not svg_files:
        print("No SVG files found in SVG directory.\n")
        return

    for svg_file in svg_files:
        if svg_file.name.endswith("_converted.svg"):
            continue
        convert_svg_to_stl(svg_file)

    print("\nAll available SVG files have been processed.")
    print(f"Output STL files stored in: {STL_DIR.resolve()}")

if __name__ == "__main__":
    main()