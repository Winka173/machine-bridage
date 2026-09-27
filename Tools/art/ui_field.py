"""Menu skin, "Field Command" (flat, tactical): white shapes and fades the stylesheet tints.

Everything is drawn white (or black for the scrims) on transparent, at twice the size it is
shown (USS -unity-slice-scale: 0.5px), and 9-sliced or stretched by Hud.uss ("menu v5"):

  ui_cta_fill      128x96 the main action: a flat face with its top-left and bottom-right corners cut (36 px)
  ui_chamfer_fill  64x64  the same cut (16 px) for headers and featured tiles
  ui_chamfer_line  64x64  a 2 px outline of ui_chamfer_fill
  ui_brackets      48x48  L-shaped corner ticks (2 px, 14 px long): the tactical frame for focus and Back
  ui_line_fade     256x4  a hairline fading out to the right (section headers)
  ui_scrim_top     4x256  black, alpha 0.72 at the top to 0 (under the top bar)
  ui_scrim_side    256x4  black, alpha 0.78 at the right edge to 0 (behind the home column)
  ui_scrim_bottom  4x256  black, alpha 0 at the top to 0.8 at the bottom
  ui_vignette      512x288 black corners at alpha 0.5
  ui_hatch         16x16  45-degree hatch, tiling (bar tracks, the CTA's right end)
  ui_fade_card     4x128  black fading in towards the bottom of a card (names over art)
  ui_shine         128x256 a soft diagonal band for the CTA's shine sweep

Run: python Tools/art/ui_field.py
"""
import math
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'UI', 'Skin')
SS = 4  # supersampling for clean diagonals


def save(im, name):
    im.save(os.path.join(OUT, name + '.png'))
    print('wrote', name, im.size)


def chamfer_poly(w, h, cut):
    """Rectangle with the top-left and bottom-right corners cut at 45 degrees."""
    return [(cut, 0), (w, 0), (w, h - cut), (w - cut, h), (0, h), (0, cut)]


def chamfer(w, h, cut, line=0):
    big = Image.new('L', (w * SS, h * SS), 0)
    d = ImageDraw.Draw(big)
    d.polygon([(x * SS, y * SS) for x, y in chamfer_poly(w, h, cut)], fill=255)
    if line:
        # Punch the inside out, leaving an outline `line` px wide (the cut edges too).
        inset = line
        cut_in = cut - inset * (math.sqrt(2) - 1)
        inner = [(cut_in + inset, inset), (w - inset, inset), (w - inset, h - cut_in - inset),
                 (w - cut_in - inset, h - inset), (inset, h - inset), (inset, cut_in + inset)]
        d.polygon([(x * SS, y * SS) for x, y in inner], fill=0)
    mask = big.resize((w, h), Image.LANCZOS)
    im = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    im.putalpha(mask)
    return im


def brackets(size=48, length=14, width=2):
    im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    s = size - 1
    for (x, y, dx, dy) in [(0, 0, 1, 1), (s, 0, -1, 1), (0, s, 1, -1), (s, s, -1, -1)]:
        for (ex, ey) in [(dx * (length - 1), dy * (width - 1)), (dx * (width - 1), dy * (length - 1))]:
            x0, x1 = sorted((x, x + ex))
            y0, y1 = sorted((y, y + ey))
            d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 255))
    return im


def fade(w, h, alpha, colour=(255, 255, 255)):
    """alpha(t) for t along the long side, 0..1."""
    im = Image.new('RGBA', (w, h))
    px = im.load()
    horizontal = w >= h
    n = w if horizontal else h
    for i in range(n):
        a = int(round(255 * max(0.0, min(1.0, alpha(i / (n - 1))))))
        for j in range(h if horizontal else w):
            x, y = (i, j) if horizontal else (j, i)
            px[x, y] = colour + (a,)
    return im


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def vignette(w=512, h=288):
    im = Image.new('RGBA', (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            u = (x / (w - 1)) * 2 - 1
            v = (y / (h - 1)) * 2 - 1
            r = math.sqrt(u * u * 0.8 + v * v * 1.1)
            px[x, y] = (0, 0, 0, int(255 * 0.5 * smooth((r - 0.55) / 0.75)))
    return im


def hatch(size=16):
    big = Image.new('L', (size * SS, size * SS), 0)
    d = ImageDraw.Draw(big)
    step = size * SS // 2
    for k in range(-2, 4):
        o = k * step
        d.line([(o, size * SS), (o + size * SS, 0)], fill=255, width=SS * 2)
    mask = big.resize((size, size), Image.LANCZOS).point(lambda a: int(a * 0.35))
    im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    im.putalpha(mask)
    return im


def shine(w=128, h=256):
    im = Image.new('RGBA', (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            # Distance from the diagonal through the centre, slanted like the chamfers.
            d = abs((x - w / 2) + (y - h / 2) * 0.35) / (w / 2)
            px[x, y] = (255, 255, 255, int(255 * max(0.0, 1 - d) ** 2))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    save(chamfer(128, 96, 36), 'ui_cta_fill')
    save(chamfer(64, 64, 16), 'ui_chamfer_fill')
    save(chamfer(64, 64, 16, line=2), 'ui_chamfer_line')
    save(brackets(), 'ui_brackets')
    save(fade(256, 4, lambda t: 1 - smooth(t)), 'ui_line_fade')
    save(fade(4, 256, lambda t: 0.72 * (1 - smooth(t)), (0, 0, 0)), 'ui_scrim_top')
    save(fade(256, 4, lambda t: 0.78 * smooth(t), (0, 0, 0)), 'ui_scrim_side')
    save(fade(4, 256, lambda t: 0.8 * smooth(t), (0, 0, 0)), 'ui_scrim_bottom')
    save(vignette(), 'ui_vignette')
    save(hatch(), 'ui_hatch')
    save(fade(4, 128, lambda t: 0.85 * smooth(t), (0, 0, 0)), 'ui_fade_card')
    save(shine(), 'ui_shine')


if __name__ == '__main__':
    main()
