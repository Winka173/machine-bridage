"""The shop's coin pack pictures (Field Command 2.0): piles of coins, bigger for bigger packs.

    python Tools/art/shop_art.py

Writes Assets/MachineBrigade/Resources/UI/Shop/coins_1.png ... coins_6.png, 480 x 300, transparent:
flat coins in the coin token's colour (#e8c15a) with a darker rim and an inner ring, stacked in
columns seen slightly from above, with a soft shadow. (The crate pictures are renders of the crate
models, from MachineBrigade.Editor.CardRenders.RenderShopArt.)
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'UI', 'Shop')
W, H = 480, 300
SS = 3
FACE = (232, 193, 90)
RIM = (176, 136, 52)
DARK = (122, 92, 32)
LIGHT = (246, 222, 150)


def coin_stack(d, cx, base_y, count, r):
    """A column of coins: each an ellipse face on a rim band, the top one with its ring."""
    thick = r * 0.22
    ry = r * 0.42
    for i in range(count):
        y = base_y - i * thick
        d.ellipse([cx - r, y - ry + thick, cx + r, y + ry + thick], fill=DARK)
        d.rectangle([cx - r, y, cx + r, y + thick], fill=RIM)
        d.ellipse([cx - r, y - ry, cx + r, y + ry], fill=FACE)
        d.arc([cx - r, y - ry, cx + r, y + ry], 200, 340, fill=RIM, width=max(2, int(r * 0.06)))
    top = base_y - (count - 1) * thick
    d.ellipse([cx - r * 0.66, top - ry * 0.66, cx + r * 0.66, top + ry * 0.66], outline=RIM, width=max(2, int(r * 0.07)))
    d.ellipse([cx - r * 0.5, top - ry * 0.6, cx - r * 0.1, top - ry * 0.25], fill=LIGHT)


def pack(level):
    img = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    shadow = Image.new('L', (W * SS, H * SS), 0)
    sd = ImageDraw.Draw(shadow)
    d = ImageDraw.Draw(img)
    rnd = random.Random(level)
    # Columns: more and taller with the pack.
    columns = [1, 2, 3, 4, 6, 8][level - 1]
    tallest = [4, 6, 8, 10, 12, 14][level - 1]
    r = [58, 54, 50, 46, 42, 40][level - 1] * SS
    positions = []
    for c in range(columns):
        row = c // 4
        col = c % 4
        per_row = min(4, columns - row * 4)
        x = W * SS / 2 + (col - (per_row - 1) / 2) * r * 1.9 + (rnd.random() - 0.5) * r * 0.3
        y = H * SS * 0.78 - row * r * 0.55
        positions.append((x, y, max(2, tallest - rnd.randint(0, tallest // 2) - row * 2)))
    positions.sort(key=lambda p: p[1])
    for x, y, n in positions:
        sd.ellipse([x - r * 1.1, y - r * 0.2, x + r * 1.1, y + r * 0.62], fill=110)
    for x, y, n in positions:
        coin_stack(d, x, y, n, r)
    # A few loose coins in front for the bigger packs.
    for i in range(max(0, level - 2)):
        x = W * SS * (0.2 + 0.6 * rnd.random())
        y = H * SS * 0.9
        sd.ellipse([x - r * 0.9, y - r * 0.2, x + r * 0.9, y + r * 0.45], fill=90)
        coin_stack(d, x, y, 1, r * 0.8)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * SS))
    base = Image.new('RGBA', img.size, (0, 0, 0, 0))
    base.putalpha(shadow)
    base.alpha_composite(img)
    return base.resize((W, H), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for level in range(1, 7):
        path = os.path.join(OUT, f'coins_{level}.png')
        pack(level).save(path)
        print('wrote', path)


if __name__ == '__main__':
    main()
