# Python SVG Half Tone Image Converter

**Original Author:** [DE Hammer](https://www.thingiverse.com/dehammer)
**Original Thingiverse post:** [https://www.thingiverse.com/thing:5183381](https://www.thingiverse.com/thing:5183381)
**Updated & documented by:** Avtomat Agentics (2025)

---

## Summary

This Python tool converts **JPG** and **PNG** images into **vector halftone SVGs** — perfect for laser engraving, CNC, or 3D printing.
The program builds a grid of circles whose sizes represent local brightness, creating a clean halftone pattern.

Originally created by DE Hammer (2021), this version has been updated to work in any folder, include auto-parameter suggestions, and feature improved organization and stability.

---

## What's New in This Version

* Works from **any directory** (no longer requires Desktop placement)
* **Auto-suggests parameters** (stock size, detail, spacing, etc.) based on image brightness and contrast
* Cleaner, more compact **Tkinter GUI** layout
* Simplified path management using Python’s `pathlib`
* Compatible with **Python ≥ 3.8**
* More readable structure and added inline documentation

---

## How It Works

1. Import a JPG or PNG image.
2. The program analyzes it and pre-fills suggested halftone parameters (you can edit them).
3. Choose the color mode:

   * **White circles on black background**
   * **Black circles on white background**
4. Click **Convert Image** to generate your halftone SVG.
5. The resulting SVG and PNG previews are saved to the `SVG` folder.

---

## Requirements

* **Python 3.8+** (recommended)
* Required libraries:

  ```bash
  pip install pillow svglib reportlab cairocffi
  ```

  *(If ReportLab gives a render error, install rlPyCairo as well.)*

---

## Usage

1. Run `halftone_gui_converter.py`
2. Click **Import Image** and choose your file.
3. Adjust the suggested parameters if needed:

   * Stock Width / Height (mm)
   * Border (mm)
   * Detail (1–20, lower = larger circles)
   * Spacing (0.1–0.9)
4. Select color mode.
5. Click **Convert Image**.
6. Find your SVG in the `SVG` folder or open it directly with **Open SVG Folder**.

---

## Example Output

| Input Image                        | Generated Halftone (SVG)         |
| ---------------------------------- | -------------------------------- |
| ![input](IMAGE/IMPORT%20IMAGE.png) | ![output](IMAGE/SVG%20IMAGE.png) |

---

## License

This project is distributed under the
**Creative Commons Attribution–ShareAlike 4.0 International (CC BY-SA 4.0)** license.

Based on the original work by **DE Hammer**, modified and updated by **Avtomat Agentics**.

More info: [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)
