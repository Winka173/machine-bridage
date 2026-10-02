"""Prompt 35: compose render_angles.py pictures into one sheet (a row per state: before, after).

    python Tools/models/sheet.py <out.png> <title> <label>=<dir> [<label>=<dir> ...] [--cell 320]

Each row: front, rear, side, top, 3/4 front, 3/4 rear, then the battle-angle shot at the default zoom's scale,
enlarged x2 (nearest) so its real pixel count shows (fitted to the cell when it is bigger).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ORDER = ('front', 'rear', 'side', 'top', 'front34', 'rear34', 'battle')
LABELS = ('front', 'rear', 'side', 'top', '3/4 front', '3/4 rear', 'battle zoom x2')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    cell = 320
    if '--cell' in sys.argv:
        cell = int(sys.argv[sys.argv.index('--cell') + 1])
        args = [a for a in args if a != str(cell)]
    out, title, rows = Path(args[0]), args[1], [a.split('=', 1) for a in args[2:]]
    head, side = 28, 70
    img = Image.new('RGB', (side + cell * len(ORDER), head + 18 + cell * len(rows)), (34, 36, 38))
    d = ImageDraw.Draw(img)
    d.text((8, 6), title, fill=(230, 230, 230))
    for i, lab in enumerate(LABELS):
        d.text((side + i * cell + 6, head), lab, fill=(200, 200, 200))
    for r, (label, folder) in enumerate(rows):
        y = head + 18 + r * cell
        d.text((6, y + cell // 2), label, fill=(230, 230, 230))
        for i, view in enumerate(ORDER):
            p = Path(folder) / f'{view}.png'
            if not p.exists():
                continue
            im = Image.open(p).convert('RGB')
            if view == 'battle':
                if im.width * 2 <= cell:
                    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
                else:                     # bigger than the cell already: fit it (a boss at the default zoom)
                    im = im.resize((cell, cell), Image.LANCZOS)
                canvas = Image.new('RGB', (cell, cell), (34, 36, 38))
                canvas.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2))
                im = canvas
            else:
                im = im.resize((cell, cell), Image.LANCZOS)
            img.paste(im, (side + i * cell, y))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print('sheet', out, img.size)


if __name__ == '__main__':
    main()
