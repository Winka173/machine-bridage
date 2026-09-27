"""Button skin for the menus: one 9-slice overlay that makes any flat face look finished.

The overlay is drawn over a button's own background colour (so every colour and state keeps
working): a white gloss over the top, a thin bright line along the very top edge, and a soft
darkening towards the bottom. It is mostly transparent, so it reads the same on green, amber,
steel or grey faces. Slices (USS): left/right 12, top 22, bottom 14.

Run: python Tools/art/ui_skin.py  (writes Assets/MachineBrigade/Resources/UI/Skin/gloss.png)
"""
import os
from PIL import Image

W, H = 48, 48
RADIUS = 10
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'UI', 'Skin')


def inside_alpha(x, y):
    """Coverage of a pixel inside the rounded rectangle (soft edge)."""
    dx = max(RADIUS - x - 0.5, x + 0.5 - (W - RADIUS), 0)
    dy = max(RADIUS - y - 0.5, y + 0.5 - (H - RADIUS), 0)
    d = (dx * dx + dy * dy) ** 0.5 - RADIUS
    return max(0.0, min(1.0, 0.5 - d))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def main():
    os.makedirs(OUT, exist_ok=True)
    im = Image.new('RGBA', (W, H))
    px = im.load()
    for y in range(H):          # y = 0 is the top row
        for x in range(W):
            a = inside_alpha(x, y)
            if a <= 0:
                px[x, y] = (0, 0, 0, 0)
                continue
            # Top gloss: strongest just under the edge, gone by 22 px down.
            gloss = 0.26 * (1 - smooth(y / 22.0))
            # A one-pixel bright rim along the top edge.
            if 1 <= y <= 2:
                gloss = max(gloss, 0.42)
            # Bottom shade: the lower 14 px darken towards the bottom edge.
            shade = 0.24 * smooth((y - (H - 14)) / 14.0)
            if gloss >= shade:
                px[x, y] = (255, 255, 255, int(255 * gloss * a))
            else:
                px[x, y] = (0, 0, 0, int(255 * shade * a))
    im.save(os.path.join(OUT, 'gloss.png'))
    print('wrote', os.path.abspath(os.path.join(OUT, 'gloss.png')))


if __name__ == '__main__':
    main()
