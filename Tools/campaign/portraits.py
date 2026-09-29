"""Draws the campaign's portraits: flat vector busts in one style, readable at 48 px.

    python Tools/campaign/portraits.py [--sheet <png>] [--only brandt,orlov]

Writes Assets/MachineBrigade/Resources/UI/Portraits/<speaker>.png (256 px, drawn at 4x and scaled
down). Allied officers stand on a teal ground, Hegemon's on a dark red one; each has its own
headgear, insignia and one feature to know them by at a glance.
"""

import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'UI', 'Portraits'))
S = 4  # supersampling
W = 256 * S

BONE = (232, 224, 204)
AMBER = (242, 163, 58)
GRAPHITE = (30, 34, 40)
INK = (18, 20, 24)
OURS = ((44, 74, 72), (30, 52, 52))
THEIRS = ((86, 40, 40), (52, 26, 28))
NEUTRAL = ((52, 58, 66), (34, 38, 44))

SKIN = {'light': (236, 200, 170), 'mid': (214, 170, 132), 'warm': (196, 146, 108), 'deep': (150, 104, 76), 'pale': (238, 214, 196)}


def s(v):
    return int(v * S)


def box(cx, cy, w, h):
    return [s(cx - w / 2), s(cy - h / 2), s(cx + w / 2), s(cy + h / 2)]


def poly(points):
    return [(s(x), s(y)) for x, y in points]


class Face:
    def __init__(self, d, skin):
        self.d, self.skin = d, skin

    def base(self, uniform, collar=None, neck_w=34):
        d = self.d
        # Shoulders and chest.
        d.polygon(poly([(28, 256), (40, 206), (84, 184), (172, 184), (216, 206), (228, 256)]), fill=uniform)
        if collar:
            d.polygon(poly([(100, 184), (128, 222), (156, 184)]), fill=collar)
        # Neck, then the head.
        d.rectangle(box(128, 176, neck_w, 30), fill=shade(self.skin, 0.85))
        d.ellipse(box(128, 122, 88, 104), fill=self.skin)
        # Ears.
        d.ellipse(box(84, 126, 14, 22), fill=shade(self.skin, 0.9))
        d.ellipse(box(172, 126, 14, 22), fill=shade(self.skin, 0.9))

    def eyes(self, y=124, gap=19, brows=True, brow_tilt=0, colour=INK, brow_colour=None):
        d = self.d
        for side in (-1, 1):
            x = 128 + side * gap
            d.ellipse(box(x, y, 9, 7), fill=colour)
            if brows:
                bc = brow_colour or colour
                d.line([(s(x - 9), s(y - 11 - side * brow_tilt)), (s(x + 9), s(y - 11 + side * brow_tilt))], fill=bc, width=s(4))

    def mouth(self, y=152, w=22, smile=0, colour=None):
        c = colour or shade(self.skin, 0.55)
        if smile:
            self.d.arc(box(128, y - 6, w, 14 + smile * 2), 20, 160, fill=c, width=s(4))
        else:
            self.d.line([(s(128 - w / 2), s(y)), (s(128 + w / 2), s(y))], fill=c, width=s(4))

    def nose(self, y=138):
        self.d.line([(s(128), s(y - 12)), (s(124), s(y)), (s(131), s(y))], fill=shade(self.skin, 0.72), width=s(3))


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(poly(pts), fill=fill)


def canvas(ground):
    img = Image.new('RGB', (W, W), ground[1])
    d = ImageDraw.Draw(img)
    # A flat ground with a lighter disc behind the head and a hairline frame.
    d.ellipse(box(128, 118, 210, 210), fill=ground[0])
    d.rectangle([s(3), s(3), W - s(3), W - s(3)], outline=shade(BONE, 0.55), width=s(3))
    return img, d


def khai(d):
    f = Face(d, SKIN['mid'])
    f.base((74, 88, 62), collar=(56, 68, 48))
    # Grey temples, short hair.
    d.chord(box(128, 104, 90, 70), 180, 360, fill=(70, 70, 72))
    d.rectangle(box(88, 114, 8, 18), fill=(150, 150, 150))
    d.rectangle(box(168, 114, 8, 18), fill=(150, 150, 150))
    # Beret with a star, pulled to one side.
    d.chord([s(76), s(56), s(186), s(112)], 160, 360, fill=(40, 52, 40))
    d.ellipse(box(150, 78, 60, 26), fill=(40, 52, 40))
    star(d, 104, 90, 9, AMBER)
    f.eyes(brow_tilt=1)
    f.nose()
    f.mouth(smile=0)
    # Colonel: three stars on the collar tabs.
    for x in (70, 82, 94):
        star(d, x, 214, 5, AMBER)
    for x in (162, 174, 186):
        star(d, x, 214, 5, AMBER)


def mai(d):
    f = Face(d, SKIN['light'])
    f.base((66, 84, 96), collar=(50, 64, 74))
    # Hair in a short bob.
    d.chord(box(128, 110, 100, 96), 170, 370, fill=(34, 26, 22))
    d.rectangle(box(82, 136, 14, 40), fill=(34, 26, 22))
    d.rectangle(box(174, 136, 14, 40), fill=(34, 26, 22))
    # Welding goggles pushed up on the forehead.
    d.rectangle(box(128, 92, 96, 10), fill=(60, 60, 60))
    for x in (108, 148):
        d.ellipse(box(x, 92, 30, 24), fill=(90, 90, 90))
        d.ellipse(box(x, 92, 20, 15), fill=AMBER)
    f.eyes(brow_tilt=0)
    f.nose()
    f.mouth(smile=1)
    # A spanner badge.
    d.rectangle(box(168, 222, 30, 8), fill=BONE)
    d.ellipse(box(184, 222, 14, 14), fill=BONE)


def dieuhau(d):
    f = Face(d, SKIN['warm'])
    f.base((92, 98, 70), collar=(70, 76, 54))
    # Flight helmet, visor up.
    d.chord(box(128, 112, 108, 118), 180, 360, fill=(190, 196, 188))
    d.rectangle(box(128, 112, 108, 10), fill=(190, 196, 188))
    d.rectangle(box(128, 80, 70, 16), fill=AMBER)
    d.rectangle(box(78, 132, 12, 34), fill=(170, 176, 168))
    d.rectangle(box(178, 132, 12, 34), fill=(170, 176, 168))
    f.eyes(brow_tilt=-2)
    f.nose()
    f.mouth(smile=2)
    # Wings badge.
    d.polygon(poly([(150, 220), (196, 214), (188, 224)]), fill=BONE)
    d.polygon(poly([(150, 220), (104, 214), (112, 224)]), fill=BONE)
    d.ellipse(box(150, 220, 12, 12), fill=AMBER)


def linh(d):
    f = Face(d, SKIN['light'])
    f.base((58, 70, 60), collar=(44, 54, 46))
    # Long hair tied back.
    d.chord(box(128, 108, 96, 92), 175, 365, fill=(20, 18, 18))
    d.ellipse(box(176, 150, 22, 60), fill=(20, 18, 18))
    # Headset.
    d.arc(box(128, 110, 104, 100), 190, 350, fill=(60, 64, 70), width=s(7))
    d.ellipse(box(80, 128, 18, 26), fill=(60, 64, 70))
    d.line([(s(82), s(140)), (s(104), s(156))], fill=(60, 64, 70), width=s(4))
    d.ellipse(box(106, 157, 8, 8), fill=AMBER)
    f.eyes(brow_tilt=1)
    f.nose()
    f.mouth(smile=0, w=18)
    # Lieutenant: one bar.
    d.rectangle(box(184, 216, 22, 7), fill=AMBER)


def hung(d):
    f = Face(d, SKIN['deep'])
    f.base((70, 82, 58), collar=(54, 64, 44))
    # Peaked cap with gold braid.
    d.rectangle(box(128, 80, 104, 32), fill=(58, 72, 50))
    d.chord(box(128, 70, 110, 40), 180, 360, fill=(58, 72, 50))
    d.rectangle(box(128, 96, 108, 8), fill=AMBER)
    d.chord(box(128, 102, 96, 22), 0, 180, fill=INK)
    star(d, 128, 80, 9, AMBER)
    f.eyes(brow_tilt=2)
    f.nose()
    # A heavy moustache.
    d.chord(box(128, 150, 44, 18), 180, 360, fill=(40, 34, 30))
    # General: two big stars and a row of medals.
    star(d, 74, 214, 7, AMBER)
    star(d, 182, 214, 7, AMBER)
    for i, c in enumerate([(200, 60, 50), AMBER, (60, 120, 200), BONE]):
        d.rectangle(box(100 + i * 12, 236, 9, 12), fill=c)


def varga(d):
    f = Face(d, SKIN['pale'])
    f.base((58, 58, 60), collar=(44, 44, 46), neck_w=44)
    # Tank crew helmet with earphones.
    d.chord(box(128, 108, 104, 100), 180, 360, fill=(40, 40, 42))
    d.ellipse(box(80, 128, 20, 30), fill=(40, 40, 42))
    d.ellipse(box(176, 128, 20, 30), fill=(40, 40, 42))
    d.rectangle(box(128, 80, 60, 8), fill=(80, 80, 82))
    f.eyes(brow_tilt=3)
    f.nose()
    f.mouth(w=26)
    # A scar across the cheek, and a heavy jaw shadow.
    d.line([(s(142), s(128)), (s(160), s(150))], fill=(170, 90, 90), width=s(3))
    d.chord(box(128, 150, 70, 40), 0, 180, fill=shade(SKIN['pale'], 0.9))
    f.mouth(y=156, w=26)
    # Hegemon eagle-less insignia: a red chevron.
    d.polygon(poly([(172, 214), (190, 226), (208, 214), (208, 222), (190, 234), (172, 222)]), fill=(200, 60, 50))


def orlov(d):
    f = Face(d, SKIN['pale'])
    f.base((72, 70, 64), collar=(56, 54, 50))
    # Fur hat.
    d.rounded_rectangle(box(128, 80, 110, 44), radius=s(14), fill=(110, 96, 80))
    d.rectangle(box(128, 98, 112, 10), fill=(90, 78, 64))
    d.rectangle(box(80, 124, 16, 40), fill=(110, 96, 80))
    d.rectangle(box(176, 124, 16, 40), fill=(110, 96, 80))
    d.ellipse(box(128, 80, 14, 14), fill=(200, 60, 50))
    # Round glasses.
    for x in (109, 147):
        d.ellipse(box(x, 124, 26, 22), outline=INK, width=s(3))
    d.line([(s(122), s(124)), (s(134), s(124))], fill=INK, width=s(3))
    f.eyes(brows=False)
    d.line([(s(96), s(110)), (s(120), s(110))], fill=INK, width=s(3))
    d.line([(s(136), s(110)), (s(160), s(110))], fill=INK, width=s(3))
    f.nose()
    f.mouth(w=18)
    # Crossed gun barrels.
    d.line([(s(172), s(210)), (s(204), s(234))], fill=BONE, width=s(5))
    d.line([(s(204), s(210)), (s(172), s(234))], fill=BONE, width=s(5))


def brandt(d):
    # Prompt 20: Major Brandt, the coastal garrison: a grey peaked cap, a moustache, a fortress badge.
    f = Face(d, SKIN['mid'])
    f.base((70, 74, 66), collar=(52, 56, 50))
    d.rectangle(box(128, 84, 104, 24), fill=(84, 88, 80))
    d.chord(box(128, 76, 114, 32), 180, 360, fill=(84, 88, 80))
    d.rectangle(box(128, 98, 106, 8), fill=INK)
    d.chord(box(128, 103, 92, 18), 0, 180, fill=INK)
    d.rectangle(box(128, 86, 14, 12), fill=(200, 60, 50))
    f.eyes(brow_tilt=2)
    f.nose()
    d.rectangle(box(128, 146, 40, 7), fill=(70, 50, 40))
    f.mouth(y=156, w=18)
    # A tower with battlements.
    d.rectangle(box(190, 224, 26, 22), fill=BONE)
    for x in (180, 190, 200):
        d.rectangle(box(x, 210, 6, 8), fill=BONE)


def kessler(d):
    f = Face(d, SKIN['light'])
    f.base((30, 36, 58), collar=(236, 236, 236))
    # White naval cap.
    d.rectangle(box(128, 82, 106, 26), fill=(236, 236, 236))
    d.chord(box(128, 74, 116, 34), 180, 360, fill=(236, 236, 236))
    d.rectangle(box(128, 97, 108, 8), fill=INK)
    d.chord(box(128, 102, 96, 20), 0, 180, fill=INK)
    d.ellipse(box(128, 84, 16, 14), fill=AMBER)
    f.eyes(brow_tilt=1)
    f.nose()
    # A trimmed grey beard.
    d.chord(box(128, 150, 80, 64), 0, 180, fill=(160, 160, 160))
    f.mouth(y=150, w=20, colour=(90, 90, 90))
    # Admiral: gold rings on the sleeve, an anchor.
    for i in range(3):
        d.rectangle(box(56, 226 + i * 8, 34, 4), fill=AMBER)
    d.line([(s(190), s(208)), (s(190), s(236))], fill=AMBER, width=s(4))
    d.arc(box(190, 228, 26, 18), 0, 180, fill=AMBER, width=s(4))


def sen(d):
    f = Face(d, SKIN['light'])
    f.base((226, 228, 224), collar=(90, 40, 40))
    # Hair in a high bun.
    d.chord(box(128, 108, 96, 90), 175, 365, fill=(28, 24, 24))
    d.ellipse(box(128, 62, 40, 32), fill=(28, 24, 24))
    d.line([(s(112), s(58)), (s(146), s(70))], fill=AMBER, width=s(3))
    # Square glasses.
    for x in (109, 147):
        d.rectangle(box(x, 124, 26, 18), outline=INK, width=s(3))
    d.line([(s(122), s(124)), (s(134), s(124))], fill=INK, width=s(3))
    f.eyes(brows=False)
    f.nose()
    f.mouth(w=16)
    # A small drone on the lab coat.
    d.rectangle(box(180, 222, 16, 6), fill=INK)
    for x in (170, 190):
        d.ellipse(box(x, 216, 12, 5), fill=INK)


def quaden(d):
    f = Face(d, SKIN['mid'])
    f.base((26, 28, 32), collar=(16, 18, 20))
    # Black flight helmet, dark visor down over the eyes.
    d.chord(box(128, 112, 110, 118), 180, 360, fill=(22, 22, 26))
    d.rectangle(box(128, 112, 110, 10), fill=(22, 22, 26))
    d.rectangle(box(78, 134, 12, 36), fill=(22, 22, 26))
    d.rectangle(box(178, 134, 12, 36), fill=(22, 22, 26))
    d.chord(box(128, 126, 92, 40), 180, 360, fill=(52, 60, 78))
    d.rectangle(box(128, 128, 92, 8), fill=(52, 60, 78))
    d.line([(s(96), s(118)), (s(150), s(112))], fill=(120, 130, 150), width=s(3))
    f.nose(y=148)
    f.mouth(y=160, w=22)
    # The crow: a black bird on a red disc.
    d.ellipse(box(128, 82, 26, 26), fill=(200, 60, 50))
    d.polygon(poly([(116, 84), (128, 76), (140, 84), (128, 88)]), fill=INK)
    d.polygon(poly([(160, 216), (196, 208), (182, 226)]), fill=(200, 60, 50))


def aurel(d):
    f = Face(d, SKIN['pale'])
    # A suit, a white shirt and a tie: no uniform, no rank.
    d.polygon(poly([(28, 256), (40, 206), (84, 184), (172, 184), (216, 206), (228, 256)]), fill=(40, 42, 50))
    d.polygon(poly([(100, 184), (128, 236), (156, 184)]), fill=(236, 236, 236))
    d.polygon(poly([(122, 196), (134, 196), (138, 236), (128, 248), (118, 236)]), fill=(150, 30, 36))
    d.rectangle(box(128, 176, 34, 30), fill=shade(SKIN['pale'], 0.85))
    d.ellipse(box(128, 122, 86, 102), fill=SKIN['pale'])
    d.ellipse(box(85, 126, 14, 22), fill=shade(SKIN['pale'], 0.9))
    d.ellipse(box(171, 126, 14, 22), fill=shade(SKIN['pale'], 0.9))
    # Slicked-back hair.
    d.chord(box(128, 100, 90, 60), 180, 360, fill=(200, 196, 186))
    d.polygon(poly([(84, 104), (172, 104), (160, 94), (96, 94)]), fill=(200, 196, 186))
    f.eyes(brow_tilt=-1)
    f.nose()
    f.mouth(smile=1, w=18)
    # The Hegemon pin.
    d.polygon(poly([(176, 206), (186, 200), (196, 206), (196, 218), (186, 224), (176, 218)]), fill=AMBER)


def hq(d):
    # Brigade HQ: a radio set and its antenna, no face.
    d.rounded_rectangle(box(128, 150, 120, 80), radius=s(8), fill=(74, 88, 62))
    d.rectangle(box(128, 136, 96, 18), fill=INK)
    for i, x in enumerate((96, 116, 136, 156)):
        d.ellipse(box(x, 172, 14, 14), fill=AMBER if i == 1 else BONE)
    d.line([(s(170), s(110)), (s(196), s(40))], fill=BONE, width=s(5))
    for r in (18, 32, 46):
        d.arc(box(196, 40, r * 2, r * 2), 300, 60, fill=AMBER, width=s(4))
    star(d, 72, 70, 14, AMBER)


PORTRAITS = [
    ('khai', OURS, khai), ('mai', OURS, mai), ('dieuhau', OURS, dieuhau), ('linh', OURS, linh), ('hung', OURS, hung),
    ('brandt', THEIRS, brandt), ('varga', THEIRS, varga), ('orlov', THEIRS, orlov), ('kessler', THEIRS, kessler), ('sen', THEIRS, sen),
    ('quaden', THEIRS, quaden), ('aurel', THEIRS, aurel), ('hq', NEUTRAL, hq),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = []
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    for name, ground, draw in PORTRAITS:
        if only and name not in only:
            continue
        img, d = canvas(ground)
        draw(d)
        img = img.resize((256, 256), Image.LANCZOS)
        img.save(os.path.join(OUT, name + '.png'), optimize=True)
        tiles.append(img)
    if '--sheet' in sys.argv:
        path = sys.argv[sys.argv.index('--sheet') + 1]
        sheet = Image.new('RGB', (6 * 264, 2 * 264 + 2 * 60), (17, 20, 24))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % 6) * 264 + 4, (i // 6) * 264 + 4))
            small = t.resize((48, 48), Image.LANCZOS)
            sheet.paste(small, ((i % 6) * 264 + 4, 2 * 264 + 6 + (i // 6) * 60))
        sheet.save(path)
    print('portraits:', ', '.join(p[0] for p in PORTRAITS))


if __name__ == '__main__':
    main()
