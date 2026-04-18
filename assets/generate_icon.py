#!/usr/bin/env python3
"""Generate the Claude Log pixel-art icon (256x256 PNG)."""
from PIL import Image, ImageDraw
import os

OUT = os.path.join(os.path.dirname(__file__), "icon.png")
SIZE = 256

BG      = (14, 14, 14, 255)
FRAME   = (50, 50, 50, 255)
AMBER   = (200, 145, 90, 255)
AMBER_D = (120, 83, 48, 255)
BLUE    = (85, 136, 204, 255)
GREY    = (80, 80, 80, 255)
DARK    = (20, 20, 20, 255)


def px(img, x, y, color, scale=1):
    draw = ImageDraw.Draw(img)
    draw.rectangle([x*scale, y*scale, (x+1)*scale-1, (y+1)*scale-1], fill=color)


def main():
    scale = 8
    grid = 32
    img = Image.new("RGBA", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)

    # Terminal window frame (rounded-ish rectangle in pixel art)
    margin = 2
    d.rectangle(
        [margin*scale, margin*scale, (grid-margin)*scale-1, (grid-margin)*scale-1],
        outline=FRAME, width=scale,
    )

    # Title bar
    d.rectangle(
        [margin*scale, margin*scale, (grid-margin)*scale-1, 6*scale-1],
        fill=(20, 20, 20, 255),
        outline=FRAME, width=scale//2,
    )

    # Title bar dots (traffic lights pixel style)
    dot_y = 4
    for i, c in enumerate([(180, 80, 80, 255), (180, 160, 60, 255), AMBER]):
        cx = (4 + i*2) * scale
        d.ellipse([cx, dot_y*scale, cx+scale-1, (dot_y+1)*scale-1], fill=c)

    # "CL" text as pixel blocks in title bar
    # C block
    cl_x, cl_y = 14, 3
    blocks_C = [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,2)]  # C shape
    blocks_L = [(0,0),(0,1),(0,2),(1,2),(2,2)]              # L shape
    for bx, by in blocks_C:
        px(img, cl_x+bx, cl_y+by, AMBER, scale)
    for bx, by in blocks_L:
        px(img, cl_x+4+bx, cl_y+by, AMBER, scale)

    # Log lines in terminal body
    line_color_map = [AMBER, GREY, BLUE, GREY, AMBER_D, GREY]
    line_widths    = [18, 12, 20, 8, 14, 10]
    for i, (lc, lw) in enumerate(zip(line_color_map, line_widths)):
        lx = 4
        ly = 8 + i * 3
        d.rectangle(
            [lx*scale, ly*scale, (lx+lw)*scale-scale//2, ly*scale+scale//2],
            fill=lc,
        )

    # Cursor blinking block at end of last line
    cur_x = 4 + 10
    cur_y = 8 + 5 * 3
    d.rectangle(
        [cur_x*scale, cur_y*scale, (cur_x+1)*scale-1, (cur_y+1)*scale-1],
        fill=AMBER,
    )

    img.save(OUT)
    print(f"Icon written to {OUT}")


if __name__ == "__main__":
    main()
