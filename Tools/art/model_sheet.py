"""Lays out a model's before/after shots (Tools/blender/model_shots.py) on one sheet.

  python Tools/art/model_sheet.py <shots_dir> <out.png> <name> [<title>]

Reads <name>_before_top.png, <name>_after_top.png, <name>_before_game.png and <name>_after_game.png from shots_dir
(a missing "before" is drawn as an empty panel: a model that did not exist yet) and writes a 2 x 2 sheet: top-down
silhouettes above, the battle camera below, before on the left.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANEL = 420
BAR = 26


def font(size):
    for name in ('arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    shots, out, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    title = sys.argv[4] if len(sys.argv) > 4 else name
    sheet = Image.new('RGB', (PANEL * 2, PANEL * 2 + BAR * 2), (24, 28, 30))
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 5), title, fill=(230, 235, 232), font=font(15))
    for col, tag in enumerate(('before', 'after')):
        draw.text((col * PANEL + PANEL - 60, 5), tag, fill=(170, 200, 185), font=font(15))
        for row, view in enumerate(('top', 'game')):
            path = shots / f'{name}_{tag}_{view}.png'
            x, y = col * PANEL, BAR + row * (PANEL + BAR)
            if path.exists():
                sheet.paste(Image.open(path).convert('RGB').resize((PANEL, PANEL)), (x, y))
            else:
                draw.rectangle((x, y, x + PANEL - 1, y + PANEL - 1), outline=(80, 80, 80))
                draw.text((x + 12, y + 12), 'no model before', fill=(160, 160, 160), font=font(14))
        draw.text((8, BAR + PANEL + 5), 'battle camera (52 deg, orthographic)', fill=(170, 200, 185), font=font(13))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, optimize=True)
    print('SHEET', out)


main()
