"""Field Command 2.0 kit skin: white shapes the stylesheet tints (Resources/UI/Tokens.uss).

Drawn at twice the size they are shown (USS -unity-slice-scale: 0.5px) and 9-sliced:

  fc_primary  160x160  the main button's face: top-left and bottom-right corners cut at 45 degrees,
                       40 px here = 20 panel px (18 px at the brief's 1400 px reference width)

Run: python Tools/art/ui_kit.py
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'UI', 'Skin')
SS = 4  # supersampling for clean diagonals


def chamfer(size, cut):
    big = Image.new('L', (size * SS, size * SS), 0)
    d = ImageDraw.Draw(big)
    poly = [(cut, 0), (size, 0), (size, size - cut), (size - cut, size), (0, size), (0, cut)]
    d.polygon([(x * SS, y * SS) for x, y in poly], fill=255)
    mask = big.resize((size, size), Image.LANCZOS)
    im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    im.putalpha(mask)
    return im


def main():
    im = chamfer(160, 40)
    path = os.path.join(OUT, 'fc_primary.png')
    im.save(path)
    print('wrote', path, im.size)


if __name__ == '__main__':
    main()
