# -*- coding: utf-8 -*-
"""
halftone_gui_converter.py
--------------------------------------
A Tkinter-based GUI tool that converts JPG/PNG images 
into vector halftone (dot pattern) SVGs.

Original Author: DE Hammer
Documentation, updates & cleanup: Avtomat Agentics
Version: 0.1
Python 3.8.3
"""


## Half Tone GUI (0.1) turns PNG & JPG into Half  Tone SVG files
## Written by DE Hammer
## This is the first version and is still a work in progress
## The folder must be on the Desktop to work or all the file locations need to be changed in the script below
## The new Avtomat Agentics version corrects this limitation to be launched in any folder
## The JPG/PNG file you are converting can be stored anywhere on your computer
## Video for how to set up and use this is at https://youtu.be/NS3nP_qvrsw
## If you like to help support this project you can email @ deepellumhammer@yahoo.com
## or you can contribute via paypal @dehammermaker
## or you can Subscribe to my youtube channel https://www.youtube.com/c/DEHammerMaker


from tkinter import *
from PIL import ImageTk, Image, ImageOps, ImageStat
from tkinter import filedialog
from pathlib import Path
import os
import json
import cairo
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import math
import cv2
import numpy as np


# ==========================================
#  DYNAMIC PATH CONFIGURATION (cross-folder)
# ==========================================

# Base directory of the script (no matter where it is)
BASE_DIR = Path(__file__).resolve().parent

# Define all subfolders relative to the script
IMAGE_DIR = BASE_DIR / "IMAGE"
SAVE_DIR  = BASE_DIR / "SAVE FOLDER"
JSON_DIR  = BASE_DIR / "JSON"
SVG_DIR   = BASE_DIR / "SVG"

# Make sure folders exist
for folder in [IMAGE_DIR, SAVE_DIR, JSON_DIR, SVG_DIR]:
    os.makedirs(folder, exist_ok=True)

# Define placeholder images for GUI
i_s = IMAGE_DIR / "IMPORT IMAGE.png"
s_s = IMAGE_DIR / "SVG IMAGE.png"


## ======================
##   GLOBAL DICTIONARIES
## ======================

info_l = {}     # Holds metadata and paths for current image
gs_dic = {}     # Grayscale pixel dictionary: (x,y) -> grayscale value
quad_dic = {}   # Dictionary mapping each "quad" (block) to its pixels
quad_gs = {}    # Average grayscale values for each quad
center = []     # Temporary holder for geometric center calculations


## ======================
##   GLOBAL VARIABLES
## ======================

px_mm = 0.26458333   # Pixel-to-mm conversion factor
max_circle_size = 0
max_gs_value = 255
smallest_circle = 0.01 * px_mm
num_col = 0
num_row = 0
spacing_perc = 0.1


## ======================
##   HELPER FUNCTIONS
## ======================

def json_data(ji):
    """
    Returns the full path to a JSON file inside the JSON folder.
    """
    return JSON_DIR / ji


def resize_for_gui(im_load):
    """
    Resizes an image proportionally to fit within 600x600px for display in the GUI.
    """
    max_width = 600
    max_height = 600

    im = Image.open(im_load)
    width, height = im.size

    # Maintain aspect ratio when resizing
    if width == height:
        wpercent = (max_width / float(width))
        hsize = int((float(height) * float(wpercent)))
        im_width = max_width        

    if width >= height + 1:
        wpercent = (max_width / float(width))
        hsize = int((float(height) * float(wpercent)))
        im_width = max_width
        
    if height >= width + 1:
        wpercent = (max_height / float(height))
        im_width = int((float(width) * float(wpercent)))
        hsize = max_height

    return im_width, hsize


def new_image(i_s):
    """
    Loads an image for GUI display (left side). 
    Resizes it to fit preview window.
    """
    im_load = i_s
    imp_im = Image.open(im_load)

    im_width, hsize = resize_for_gui(im_load)
    im_re = imp_im.resize((im_width, hsize), Image.Resampling.LANCZOS)
    import_image = ImageTk.PhotoImage(im_re)

    return import_image    


def new_svg(s_s):
    """
    Loads the generated SVG (converted to PNG) for GUI display (right side).
    """
    im_load = s_s
    imp_im = Image.open(im_load)

    im_width, hsize = resize_for_gui(im_load)
    im_re = imp_im.resize((im_width, hsize), Image.Resampling.LANCZOS)
    svg_image = ImageTk.PhotoImage(im_re)

    return svg_image    



def auto_suggest_settings(image_path):
    """
    Analyzes the imported image and suggests optimal default parameters
    for halftone generation. Enhanced version specialized for photographs:
    combines tonal range, edge density, and local texture variance to
    better handle portraits and smooth surfaces with subtle details.
    """

    import cv2
    import numpy as np
    from PIL import Image

    # --- Load image and convert to grayscale ---
    im = Image.open(image_path).convert("L")
    width_px, height_px = im.size
    np_img = np.array(im)

    # --- 1. Suggest physical size (mm) based on resolution ---
    aspect_ratio = width_px / height_px
    if height_px > 2000:
        base_height = 150  # mm
    elif height_px < 600:
        base_height = 250
    else:
        base_height = 200
    base_width = int(base_height * aspect_ratio)

    # --- 2. Tonal analysis (percentiles for dynamic range) ---
    p10, p50, p90 = np.percentile(np_img, [10, 50, 90])
    tonal_range = p90 - p10
    median_brightness = p50
    bright_ratio = np.mean(np_img > 128)

    # --- 3. Structural and texture analysis ---
    # Edge density (Canny)
    edges = cv2.Canny(np_img, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    # Local variance of intensity (texture richness)
    var_map = cv2.Laplacian(np_img, cv2.CV_64F).var()

    # Combine both as texture score (balanced between edges and microtexture)
    texture_score = 0.5 * edge_density + 0.5 * (var_map / 500.0)

    # --- 4. Compute "detail" and "spacing" adaptively ---
    # Default base values from texture score
    if texture_score > 0.12:          # highly detailed (complex scenes)
        detail = 6
        spacing = 0.22
    elif texture_score > 0.06:        # medium detail (normal photo)
        detail = 8
        spacing = 0.28
    else:                             # low detail (flat or soft portrait)
        detail = 10
        spacing = 0.33

    # --- Portrait bias correction ---
    # If mostly bright (white background) but central area has texture, assume portrait
    h, w = np_img.shape
    central = np_img[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]
    central_var = cv2.Laplacian(central, cv2.CV_64F).var()

    if bright_ratio > 0.6 and central_var > 150:
        # likely portrait with white background → finer detail
        detail = max(5, detail - 2)
        spacing = max(0.18, spacing * 0.8)

    # --- Fine-tune spacing by tonal range ---
    if tonal_range < 40:
        spacing *= 0.9
    elif tonal_range > 90:
        spacing *= 1.1
    spacing = float(max(0.15, min(spacing, 0.45)))  # clamp safely

    # --- 5. Decide perceptual color mode ---
    if bright_ratio > 0.65:
        color_mode = 2  # bright → black dots / white background
    elif bright_ratio < 0.35:
        color_mode = 1  # dark → white dots / black background
    else:
        color_mode = 2 if median_brightness > 110 else 1

    # --- 6. Return final suggestion set ---
    return {
        "stock_width": base_width,
        "stock_height": base_height,
        "border": 10,
        "detail": int(detail),
        "spacing": round(spacing, 3),
        "color_mode": color_mode
    }



## ==========================================
##   STYLE PROFILE SYSTEM (Level 5A)
## ==========================================
##
## This module introduces automatic style detection and
## adaptive profile selection for halftone generation.
## It classifies the image type based on brightness,
## contrast, and texture, then applies a corresponding
## visual pattern style.
##
## Author: Avtomat Agentics
## Version: 0.2 (Experimental Artistic Module)
##

def detect_image_style(image_path):
    """
    Analyze an image and return a string label indicating
    the most suitable style profile.
    Possible results: 'portrait', 'pop_art', 'technical'
    """


    im = Image.open(image_path).convert("L")
    np_img = np.array(im)

    # --- Compute base metrics ---
    brightness = np.mean(np_img)
    contrast = np.std(np_img)
    edges = cv2.Canny(np_img, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    # --- Simple rule-based classifier ---
    if brightness > 160 and contrast < 45:
        # Bright and soft → portrait
        style = "portrait"
    elif contrast > 70 and edge_density > 0.05:
        # High contrast, many edges → pop art style
        style = "pop_art"
    else:
        # Default technical or low-contrast drawing
        style = "technical"

    print(f"Detected style: {style}  (brightness={brightness:.1f}, contrast={contrast:.1f}, edges={edge_density:.3f})")
    return style


def get_style_profile(style_label):
    STYLE_PROFILES = {
        "portrait": {
            "detail": 6,
            "spacing": 0.20,
            "color_mode": 2,
            "description": "Smooth halftone optimized for portraits."
        },
        "pop_art": {
            "detail": 8,
            "spacing": 0.30,
            "color_mode": 1,
            "description": "Bold, high-contrast halftone inspired by comic prints."
        },
        "technical": {
            "detail": 7,
            "spacing": 0.22,
            "color_mode": 2,
            "description": "Structured, precise halftone suitable for technical or engraved looks."
        },
        "soft_art": {
            "detail": 5,
            "spacing": 0.18,
            "color_mode": 2,
            "description": "Soft artistic tone balance between realism and stylization."
        }
    }
    return STYLE_PROFILES.get(style_label, STYLE_PROFILES["technical"])


def auto_style_suggestion(image_path):
    """
    Combines the automatic analysis from auto_suggest_settings()
    with style classification. The detected style adjusts the
    final spacing, detail, and color mode parameters.
    """
    base = auto_suggest_settings(image_path)
    style = detect_image_style(image_path)
    profile = get_style_profile(style)

    # Merge adaptive style parameters
    base["detail"] = profile["detail"]
    base["spacing"] = profile["spacing"]
    base["color_mode"] = profile["color_mode"]
    base["style_label"] = style

    print(f"Applied style profile: {style} - {profile['description']}")
    return base



def update_dic(info_l):
    """
    Updates info_l dictionary with paths for grayscale, resized, 
    and SVG output files, based on the chosen input image.
    """
    inam = info_l['inam']
    ftyp = info_l['ftyp']

    # Define save paths for different processing stages
    gnam = f"/{inam}_greys.{ftyp}"
    grey_file = SAVE_DIR / f"{inam}_grey.{ftyp}"
    rnam = SAVE_DIR / f"{inam}_resize.{ftyp}"

    info_l['gnam'] = gnam
    info_l['grey_file'] = grey_file
    info_l['rnam'] = rnam

    # Define other folders used in the process
    info_l['sfol'] = SAVE_DIR
    info_l['tfol'] = JSON_DIR
    info_l['vfol'] = SVG_DIR

    return info_l


def i_image():
    """
    Opens file dialog to let the user select an input image (JPG/PNG).
    Updates info_l with the file’s metadata and shows it in GUI preview.
    """
    nroot = Tk()
    nroot.withdraw()
    image_select = filedialog.askopenfilenames()
    i_s = image_select[0]

    base_name = os.path.basename(i_s)
    inam = base_name.split('.')[0]
    ftyp = base_name.split('.')[1]
    ifol = os.path.dirname(i_s)

    global info_l
    info_l = {'full_path': i_s, 'base_name': base_name, 'inam': inam, 'ftyp': ftyp, 'ifol': ifol}
    update_dic(info_l)

    # import_image = new_image(i_s)
    # label.configure(image=import_image)
    # label.image = import_image
    
    # Auto-fill GUI fields with suggested parameters
    suggestions = auto_style_suggestion(i_s)
    stock_width_g.delete(0, END)
    stock_width_g.insert(0, suggestions["stock_width"])

    stock_height_g.delete(0, END)
    stock_height_g.insert(0, suggestions["stock_height"])

    stock_boarder_g.delete(0, END)
    stock_boarder_g.insert(0, suggestions["border"])

    max_px_box_g.delete(0, END)
    max_px_box_g.insert(0, suggestions["detail"])

    spacing_perc_g.delete(0, END)
    spacing_perc_g.insert(0, suggestions["spacing"])

    # var.set(suggestions["color_mode"])



def convert_grey():
    """
    Converts the selected image to grayscale and saves it to the SAVE FOLDER.
    """
    print('Converting Image to Grey Scale')

    ifol = info_l['ifol']
    inam = info_l['inam']
    ftyp = info_l['ftyp']
    grey_file = info_l['grey_file']

    cg_path = Path(ifol) / f"{inam}.{ftyp}"

    im = Image.open(cg_path)
    width, height = im.size
    
    gs_im = ImageOps.grayscale(im)
    gs_im.save(grey_file)


def v_h(width, height, stock_width, stock_height, sbw):
    """
    Calculates proportional resizing to fit image within stock material size (mm).
    """
    max_width = (stock_width - sbw) / px_mm
    max_height = (stock_height - sbw) / px_mm

    if width == height:
        wpercent = (max_width / float(width))
        hsize = int((float(height) * float(wpercent)))
        im_width = max_width
        return (im_width, hsize)        

    if width >= height + 1:
        wpercent = (max_width / float(width))
        hsize = int((float(height) * float(wpercent)))
        im_width = max_width
        return (im_width, hsize)

    if height >= width + 1:
        wpercent = (max_height / float(height))
        im_width = int((float(width) * float(wpercent)))
        hsize = max_height
        return (im_width, hsize)


def resize():
    """
    Resizes the grayscale image to match the desired physical stock size 
    input by the user (in mm).
    """
    print('\nRESIZING IMAGE')
    print('\nINPUT STOCK MATERIAL SIZE TO RESIZE IMAGE TO FIT')

    # Read user-entered size parameters
    stock_width = int(stock_width_g.get())
    stock_height = int(stock_height_g.get())
    stock_boarder = int(stock_boarder_g.get())
    max_px_box = int(max_px_box_g.get())
    spacing_per = float(spacing_perc_g.get())

    sbw = int(stock_boarder * 2)
    new_width = (stock_width - sbw) / px_mm
    
    gnam = info_l['gnam']
    rnam = info_l['rnam']
    grey_file = info_l['grey_file']

    im = Image.open(grey_file)
    width, height = im.size

    # Compute new dimensions maintaining aspect ratio
    rc = v_h(width, height, stock_width, stock_height, sbw)
    new_width = rc[0]
    hsize = rc[1]

    print('\nORIGINAL IMAGE IN MM - WIDTH = %s    HEIGHT = %s' % (width*px_mm, height*px_mm))
    print('AFTER RESIZE IN MM WIDTH = %s   HEIGHT = %s' % (new_width*px_mm, hsize*px_mm))

    im = im.resize((int(new_width), int(hsize)), Image.Resampling.LANCZOS)
    im.save(rnam)


def g_pixel():
    """
    Extracts grayscale pixel values from the resized image.
    """
    rnam = info_l['rnam']
    im = Image.open(rnam)
    pixel_values = list(im.getdata())
    return pixel_values


def g_pixel_dic():
    """
    Builds a dictionary mapping each pixel coordinate to its grayscale value.
    Also saves this as a JSON file for reference.
    """
    print('\nPIXEL DICTIONARY')

    pv = g_pixel()
    tfol = info_l['tfol']
    rnam = info_l['rnam']

    row_on = 0
    col_on = 0

    im = Image.open(rnam)
    width, height = im.size

    # Loop through all pixels and record coordinates with grayscale value
    for x in pv:
        if col_on <= (width - 1):
            p = ('%s,%s' % (row_on, col_on))
            gs_dic[p] = x
            col_on += 1
        else:
            col_on = 0
            row_on += 1
            p = ('%s,%s' % (row_on, col_on))
            gs_dic[p] = x
            col_on += 1

    # Use Path for saving JSON file safely
    json_path = tfol / "pv.json"
    with open(json_path, 'w') as outfile:
        json.dump(gs_dic, outfile)


def build_quads():
    """
    Divides the image into square blocks ("quads") based on the detail setting.
    Each quad groups several pixels to be represented by one halftone circle.
    """
    print('\nBUILDING QUADS')

    blocks_list = []

    tfol = info_l['tfol']
    rnam = info_l['rnam']
    max_px_box = int(max_px_box_g.get())

    im = Image.open(rnam)
    width, height = im.size

    total_pixels = width * height
    t_num_col = width // max_px_box
    t_num_row = height // max_px_box
    t_quads = int(t_num_col * t_num_row)
    height = round(height)
    width = round(width)
    
    global num_col
    num_col = t_num_col
    global num_row
    num_row = t_num_row

    on_quad = 0
    on_col = 0
    on_row = 0
    col_add = 0
    row_add = 0

    # Loop to assemble pixel coordinates for each block
    for tq in range(t_quads):
        cur_blocks = []
        for y in range(max_px_box):
            for x in range(max_px_box):
                if on_row == 1:
                    c = x + (col_add + 1)
                    r = y + 1
                    j = ('%s,%s' % (r, c))
                    cur_blocks.append(j)
                if on_row != 1:
                    c = x + (col_add)
                    r = y + (row_add)
                    j = ('%s,%s' % (r, c))
                    cur_blocks.append(j)

        blocks_list.append(cur_blocks)
        qq = ('%s,%s' % (on_row, on_col))
        quad_dic[qq] = cur_blocks

        if on_col <= t_num_col:
            on_col += 1
            col_add = col_add + max_px_box
        if on_col == t_num_col:
            on_col = 0
            on_row += 1
            col_add = 0
            row_add = row_add + max_px_box

        on_quad += 1

    # Save quads JSON file using Path
    json_quads = tfol / "quad_dic.json"
    with open(json_quads, 'w') as outfile:
        json.dump(quad_dic, outfile)


def avg_quad_gs(color_list):
    """
    Returns the average grayscale value from a list of pixel grayscale values.
    """
    num = len(color_list)
    t = 0
    for x in color_list:
        t = t + x
    avg = t / num
    return avg


def avg_gs():
    """
    Calculates and stores average grayscale for each quad.
    """
    for x in quad_dic:
        color_list = []
        cor = quad_dic[x]
        for y in cor:
            try:
                pv = gs_dic[y]
                color_list.append(pv)
                avg = avg_quad_gs(color_list)
                quad_gs[x] = avg
            except:
                p = 0


def find_center(r, c, max_box_side):
    """
    Calculates the geometric center of a quad, to position its circle.
    """
    r_box_in = (r + 1) * max_box_side
    c_box_in = (c + 1) * max_box_side
    half_box = (max_box_side * 0.5)
    x_a = (c_box_in - half_box)
    y_a = (r_box_in - half_box)
    center = [x_a, y_a]
    return center


def find_radius(s, max_circle_size):
    """
    Determines the circle radius based on grayscale value and user color mode.
    Darker areas → larger circles.
    """
    color = var.get()

    if color == 1:
        fr = ((max_circle_size * s) / max_gs_value) / 2
        fr = round(fr, 4)

    if color == 2:
        fr = ((max_circle_size * s) / max_gs_value)
        fr = (max_circle_size - fr) / 2
        fr = round(fr, 4)

    return fr


def draw_shape_for_style(context, style_label, x, y, r):
    """
    Draws a specific shape based on the detected style.
    Each shape is centered at (x, y) and scaled by radius r.
    """
    if style_label == "portrait":
        # Circle – smooth and classical
        context.arc(x, y, r, 0, 2 * math.pi)
        context.fill()

    elif style_label == "pop_art":
        # Square – bold, graphic
        context.rectangle(x - r, y - r, 2 * r, 2 * r)
        context.fill()

    elif style_label == "technical":
        # Cross – structured, precise
        line_w = r * 0.2
        # vertical bar
        context.rectangle(x - line_w / 2, y - r, line_w, 2 * r)
        context.fill()
        # horizontal bar
        context.rectangle(x - r, y - line_w / 2, 2 * r, line_w)
        context.fill()

    elif style_label == "soft_art":
        # Diamond – rotated square
        context.move_to(x, y - r)
        context.line_to(x + r, y)
        context.line_to(x, y + r)
        context.line_to(x - r, y)
        context.close_path()
        context.fill()

    else:
        # Fallback: circle
        context.arc(x, y, r, 0, 2 * math.pi)
        context.fill()



def create_paths():
    """
    Generates the SVG drawing by creating circles at each quad center.
    Circle radius depends on the average grayscale value of that quad.
    """
    print('\nDRAWING A LOT OF CIRCLES PLEASE BE PATIENT')

    tfol = info_l['tfol']
    inam = info_l['inam']
    rnam = info_l['rnam']
    vfol = info_l['vfol']
    sfol = info_l['sfol']
    max_px_box = int(max_px_box_g.get())
    color = var.get()

    # Open file for optional coordinate debug data
    fileA = open(tfol / "cor.json", 'w')

    im = Image.open(rnam)
    width, height = im.size

    # Compute geometry of circle grid
    max_box_side = int(width / num_col)
    perc = max_box_side * spacing_perc
    max_circle_size = max_box_side - perc
    n_height = int(max_box_side * num_row)
    n_width = int(max_box_side * num_col)
    max_diameter = 0
    color_max = 0

    # Scale factor for Cairo (inverse of px-to-mm conversion)
    pixel_scale = 0.7354

    # Color scheme depending on user choice
    if color == 1:
        rr, rg, rb = 0, 0, 0
        cr, cg, cb = 1, 1, 1
        color_s = 'wb'
    elif color == 2:
        rr, rg, rb = 1, 1, 1
        cr, cg, cb = 0, 0, 0
        color_s = 'bw'
    else:
        rr, rg, rb = 1, 1, 1
        cr, cg, cb = 0, 0, 0
        color_s = 'bw'

    # Define output file paths using Path objects
    svg_im = vfol / f"{inam}_DETAIL_{max_px_box}_W{int(n_width*px_mm)}_H{int(n_height*px_mm)}_{color_s}.svg"
    s_s_path = sfol / f"{inam}_DETAIL_{max_px_box}_W{int(n_width*px_mm)}_H{int(n_height*px_mm)}_{color_s}.png"

    # Begin drawing with Cairo
    with cairo.SVGSurface(str(svg_im), int(n_width * pixel_scale), int(n_height * pixel_scale)) as surface:
        context = cairo.Context(surface)
        context.scale(pixel_scale, pixel_scale)
        context.set_line_width(0.1)

        # Fill background rectangle
        context.rectangle(0, 0, int(n_width), int(n_height))
        context.set_source_rgb(rr, rg, rb)
        context.fill()
        
        style_label = info_l.get("style_label", "portrait")
        
        # Draw one circle per quad
        for x in quad_gs:
            r = int(x.split(',')[0])
            c = int(x.split(',')[1])
            s = int(quad_gs[x])

            fc = find_center(r, c, max_box_side)
            fr = find_radius(s, max_circle_size)
            d = fr * 2

            if d >= max_diameter:
                max_diameter = d
                color_max = s

            # Write circle data to debug JSON
            jt = f"fc = {fc}  fr = {fr}  d = {d}  s = {s}"
            fileA.write(f"{jt}\n")

            # Draw the circle if it's above minimum radius
            if fr >= smallest_circle:
                context.set_source_rgb(cr, cg, cb)
                draw_shape_for_style(context, info_l.get("style_label", "portrait"), fc[0], fc[1], fr)

            # Clear temp list used for center calculation
            center.clear()

    # Adjust max diameter slightly (empirical correction factor)
    max_diameter *= 0.980554

    # Convert SVG to PNG for preview display
    drawing = svg2rlg(str(svg_im))
    renderPM.drawToFile(drawing, str(s_s_path), fmt='png')

    print(f'\nMax Diameter PIXEL = {max_diameter}   Max Diameter MM = {max_diameter * px_mm}')
    print(f'\nSVG SAVED TO: {svg_im}')

    # Update right-side preview in GUI
    # import_image = new_svg(s_s_path)
    # s_label.configure(image=import_image)
    # s_label.image = import_image


def convert_image():
    """
    Master function that executes the full halftone conversion process
    in proper order: grayscale -> resize -> pixel mapping -> quads -> 
    averaging -> circle drawing (SVG creation).
    """
    convert_grey()
    resize()
    g_pixel_dic()
    build_quads()
    avg_gs()
    create_paths()


def open_svg():
    """
    Opens the SVG output folder in the system file explorer.
    """
    vfol = info_l['vfol']
    print(vfol)
    os.startfile(vfol)


####################################
##           GUI SETUP            ##
####################################

# Initial row reference offset for layout
ir = 2

# Create main GUI window
root = Tk()
root.title("HALF TONE")
# root.configure(bg='blue')  # (optional background color)

# Define GUI window size
root.geometry('600x300')

# Variable to store selected radio button (color mode)
var = IntVar()

# # =====================
# #   LEFT IMAGE PREVIEW
# # =====================
# # Load default placeholder image (import preview)
# import_image = new_image(i_s)
# label = Label(image=import_image)
# label.grid(row=2, column=0, columnspan=3, rowspan=20)

# # Add empty spacer label to help grid spacing
# Label(root, text='          ').grid(row=0, column=15)

# # =====================
# #  RIGHT IMAGE PREVIEW
# # =====================
# # Load default placeholder SVG image
# svg_image = new_svg(s_s)
# s_label = Label(image=svg_image)
# s_label.grid(row=2, column=20, columnspan=3, rowspan=20)

# =====================
#     INPUT FIELDS
# =====================
stock_width_g = Entry(root)
stock_height_g = Entry(root)
stock_boarder_g = Entry(root)
max_px_box_g = Entry(root)
spacing_perc_g = Entry(root)

Label(root, text='ALL MEASUREMENTS ARE IN MM:').grid(row=1, column=9, columnspan=5)
Label(root, text='STOCK WIDTH:').grid(row=ir, column=9, sticky=E)
stock_width_g.grid(row=ir, column=10)

Label(root, text='STOCK HEIGHT:').grid(row=ir+1, column=9)
stock_height_g.grid(row=ir+1, column=10)

Label(root, text='BOARDER TO ADD (1 SIDE):').grid(row=ir+2, column=9)
stock_boarder_g.grid(row=ir+2, column=10)

Label(root, text='DETAIL (LOWER IS HIGHER) (1-20):').grid(row=ir+3, column=9)
max_px_box_g.grid(row=ir+3, column=10)

Label(root, text='SPACING (.1-.9) LOWER IS LESS SPACING:').grid(row=ir+4, column=9)
spacing_perc_g.grid(row=ir+4, column=10)

# =====================
#  COLOR MODE SELECTION
# =====================
wb = Radiobutton(root, text='WHITE CIRCLES/BLACK BG', variable=var, value=1)
bw = Radiobutton(root, text='BLACK CIRCLES/WHITE BG', variable=var, value=2)
wb.grid(row=ir+5, column=9)
bw.grid(row=ir+5, column=10)

# =====================
#     ACTION BUTTONS
# =====================
button_import = Button(root, text='IMPORT IMAGE', command=i_image)
button_convert = Button(root, text='CONVERT IMAGE', command=convert_image)
button_svg_folder = Button(root, text='OPEN SVG FOLDER', command=open_svg)

button_import.grid(row=25, column=0, columnspan=3)
button_convert.grid(row=ir+6, column=9, columnspan=2)
button_svg_folder.grid(row=ir+7, column=9, columnspan=2)

# =====================
#     MAIN LOOP
# =====================
root.mainloop()

