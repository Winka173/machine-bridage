"""Prompt 15 D: the armour and weapon icon set, drawn from scratch in the kit's line style.

Every icon is on the kit's 24-unit grid (Icons.cs). Long forms (rounds, darts, rockets, missiles) are drawn
along a vertical axis and turned 45 degrees so they point up and right, the way a round flies; shells,
mortar rounds and the ballistic missile stand upright; bombs fall nose down; drones are seen from above.
Nothing is told apart by colour: armour levels fill up like a battery (dashed, thin, double, half, full
with rivets), kinetic rounds show their penetration in the shape (ball, bullet, banded round, dart,
double dart, dart with rings).

Writes Assets/MachineBrigade/Scripts/Game/Hud/Icons.Combat.cs, and with --preview a PNG sheet at the
smallest size (33 px: 18 pt on the reference phone, Kit.PanelPxPerPoint 1.823) and at 96 px.

Run: python Tools/art/combat_icons.py [--preview out.png]
"""
import math
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Scripts', 'Game', 'Hud', 'Icons.Combat.cs')

# ---------------------------------------------------------------- path helpers

TOKEN = re.compile(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def parse(d):
    """Absolute M L H V C Q A Z only -> list of (cmd, [numbers])."""
    toks = TOKEN.findall(d)
    out, i, cmd, cur = [], 0, 'M', (0.0, 0.0)
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
        if cmd != cmd.upper():
            raise ValueError('absolute commands only: ' + d)
        if cmd == 'Z':
            out.append(('Z', [])); continue
        n = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'Q': 4, 'A': 7}[cmd]
        vals = [float(t) for t in toks[i:i + n]]; i += n
        if cmd == 'H':
            out.append(('L', [vals[0], cur[1]])); cur = (vals[0], cur[1])
        elif cmd == 'V':
            out.append(('L', [cur[0], vals[0]])); cur = (cur[0], vals[0])
        else:
            out.append((cmd, vals)); cur = (vals[-2], vals[-1])
        if cmd == 'M':
            cmd = 'L'
    return out


def emit(ops):
    s = []
    for c, v in ops:
        s.append(c + ' '.join(fmt(x) for x in v) if v else c)
    return ''.join(s)


def rot_pt(x, y, deg, cx=12.0, cy=12.0):
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


def rotate(d, deg, cx=12.0, cy=12.0):
    ops = []
    for c, v in parse(d):
        if c == 'A':
            x, y = rot_pt(v[5], v[6], deg, cx, cy)
            ops.append((c, v[:5] + [x, y]))
        else:
            pts = []
            for k in range(0, len(v), 2):
                pts += list(rot_pt(v[k], v[k + 1], deg, cx, cy))
            ops.append((c, pts))
    return emit(ops)


def P(d, **a):
    attrs = ''.join(f' {k}="{v}"' for k, v in a.items())
    return f'<path{attrs} d="{emit(parse(d))}"/>'


def R(d, deg=45, **a):
    return P(rotate(d, deg), **a)


def dot(x, y, r):
    return f'<circle fill="1" stroke="0" cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}"/>'


def ring(x, y, r, **a):
    attrs = ''.join(f' {k}="{v}"' for k, v in a.items())
    return f'<circle{attrs} cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}"/>'


def circle_d(x, y, r):
    """A circle as path data (two arcs), for holes inside even-odd fills."""
    return f'M{fmt(x - r)} {fmt(y)}A{fmt(r)} {fmt(r)} 0 1 0 {fmt(x + r)} {fmt(y)}A{fmt(r)} {fmt(r)} 0 1 0 {fmt(x - r)} {fmt(y)}Z'


def rect_d(x0, y0, x1, y1):
    return f'M{fmt(x0)} {fmt(y0)}H{fmt(x1)}V{fmt(y1)}H{fmt(x0)}Z'


def star_d(cx, cy, r_out, r_in, n, start=-90.0):
    pts = []
    for k in range(n * 2):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(start + k * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return 'M' + 'L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts) + 'Z'


# ---------------------------------------------------------------- flattening (clipping and preview)

def flatten(d):
    """Path data -> list of (points, closed)."""
    subs, pts, cur, start = [], None, (0.0, 0.0), (0.0, 0.0)
    for c, v in parse(d):
        if c == 'M':
            pts = [(v[0], v[1])]; subs.append([pts, False]); cur = start = (v[0], v[1])
        elif c == 'L':
            pts.append((v[0], v[1])); cur = (v[0], v[1])
        elif c == 'C':
            for k in range(1, 17):
                t = k / 16; u = 1 - t
                pts.append((u ** 3 * cur[0] + 3 * u * u * t * v[0] + 3 * u * t * t * v[2] + t ** 3 * v[4],
                            u ** 3 * cur[1] + 3 * u * u * t * v[1] + 3 * u * t * t * v[3] + t ** 3 * v[5]))
            cur = (v[4], v[5])
        elif c == 'Q':
            for k in range(1, 13):
                t = k / 12; u = 1 - t
                pts.append((u * u * cur[0] + 2 * u * t * v[0] + t * t * v[2], u * u * cur[1] + 2 * u * t * v[1] + t * t * v[3]))
            cur = (v[2], v[3])
        elif c == 'A':
            pts += arc_points(cur, (v[5], v[6]), v[0], v[3] != 0, v[4] != 0); cur = (v[5], v[6])
        elif c == 'Z':
            subs[-1][1] = True; pts.append(start); cur = start
    return subs


def arc_points(p1, p2, r, large, sweep):
    hx, hy = (p1[0] - p2[0]) / 2, (p1[1] - p2[1]) / 2
    lam = (hx * hx + hy * hy) / (r * r)
    if lam > 1:
        r *= math.sqrt(lam)
    sign = 1 if large != sweep else -1
    num = r ** 4 - r * r * hy * hy - r * r * hx * hx
    den = max(r * r * hy * hy + r * r * hx * hx, 1e-9)
    co = sign * math.sqrt(max(0, num / den))
    cpx, cpy = co * hy, -co * hx
    cx, cy = cpx + (p1[0] + p2[0]) / 2, cpy + (p1[1] + p2[1]) / 2
    a0 = math.atan2(hy - cpy, hx - cpx)
    a1 = math.atan2(-hy - cpy, -hx - cpx)
    da = a1 - a0
    if not sweep and da > 0:
        da -= 2 * math.pi
    if sweep and da < 0:
        da += 2 * math.pi
    n = max(6, int(abs(da) / 0.15))
    return [(cx + r * math.cos(a0 + da * k / n), cy + r * math.sin(a0 + da * k / n)) for k in range(1, n + 1)]


def clip_below(d, y0):
    """The closed outline of d clipped to y >= y0, as path data (a polygon)."""
    poly = flatten(d)[0][0]
    out = []
    for k in range(len(poly) - 1):
        a, b = poly[k], poly[k + 1]
        ina, inb = a[1] >= y0, b[1] >= y0
        if ina:
            out.append(a)
        if ina != inb:
            t = (y0 - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * t, y0))
    return 'M' + 'L'.join(f'{fmt(x)} {fmt(y)}' for x, y in out) + 'Z'


def span_at(d, y):
    """The outline's x extent at height y."""
    poly = flatten(d)[0][0]
    xs = []
    for k in range(len(poly) - 1):
        a, b = poly[k], poly[k + 1]
        if (a[1] - y) * (b[1] - y) <= 0 and a[1] != b[1]:
            xs.append(a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]))
    return min(xs), max(xs)


# ---------------------------------------------------------------- the set

ICONS = {}


def icon(name, *elements):
    if name in ICONS:
        raise ValueError('duplicate ' + name)
    ICONS[name] = ''.join(elements)


# Armour: the shield (ground), a winged narrow shield (air), a shield with brick courses (structures).
SHIELD = 'M12 2.5L20 5.5V11C20 16 16.4 19.6 12 21.5C7.6 19.6 4 16 4 11V5.5Z'
SHIELD_IN = 'M12 6.1L16.6 7.9V11.2C16.6 14.3 14.6 16.6 12 17.9C9.4 16.6 7.4 14.3 7.4 11.2V7.9Z'
NARROW = 'M12 4L17 6V11C17 14.8 14.7 17.6 12 19C9.3 17.6 7 14.8 7 11V6Z'
NARROW_IN = 'M12 6.9L14.4 8V11.1C14.4 13.1 13.4 14.6 12 15.5C10.6 14.6 9.6 13.1 9.6 11.1V8Z'
WINGS = 'M6.2 7.6H1.2M6.4 10.6H2.4M6.9 13.6H3.9M17.8 7.6H22.8M17.6 10.6H21.6M17.1 13.6H20.1'


def rivets(points, r):
    return ''.join(circle_d(x, y, r) for x, y in points)


def armour_family(prefix, body, inner, holes4, extra='', extra_thin='', half_y=12.0, half_holes='', seam_y=10.1):
    # 0 none: dashed and hollow.
    icon(prefix + '0', P(body, dash='2.1 1.9'), extra_thin)
    # 1 thin: a hairline outline.
    icon(prefix + '1', P(body, sw='1.05'), extra_thin)
    # 2 medium: a double outline.
    icon(prefix + '2', P(body, sw='1.5'), P(inner, sw='1.5'), extra)
    # 3 thick: the lower half filled.
    icon(prefix + '3', P(body), P(clip_below(body, half_y) + half_holes, fill='eo', stroke='0'), extra)
    # 4 very thick: filled, with rivets (or brick joints) as holes.
    icon(prefix + '4', P(body), P(emit(parse(body)) + holes4, fill='eo', stroke='0'), extra)
    # 5 super-heavy (a boss's plate, DECISIONS 21G): level 4 under a heavier rim, with a seam across the plate.
    l, r = span_at(body, seam_y)
    seam = rect_d(l + 1.4, seam_y - 0.45, r - 1.4, seam_y + 0.45)
    icon(prefix + '5', P(body, sw='3.2'), P(emit(parse(body)) + holes4 + seam, fill='eo', stroke='0'), extra)


armour_family('a_g', SHIELD, SHIELD_IN, rivets([(8.2, 7.6), (15.8, 7.6), (8.4, 12.6), (15.6, 12.6), (12, 17)], 1.25))
armour_family('a_a', NARROW, NARROW_IN, rivets([(9.9, 8.6), (14.1, 8.6), (12, 14.2)], 1.05),
              extra=P(WINGS), extra_thin=P(WINGS, sw='1.3'), half_y=11.5, seam_y=11.4)


def bricks_lines():
    """Brick courses drawn as lines (hollow levels)."""
    l1, r1 = span_at(SHIELD, 9.0)
    l2, r2 = span_at(SHIELD, 14.5)
    return (f'M{fmt(l1)} 9H{fmt(r1)}M{fmt(l2)} 14.5H{fmt(r2)}'
            'M8.2 4.4V9M15.8 4.4V9M12 9V14.5M8.6 14.5V18.4M15.4 14.5V18.4')


def bricks_holes(y_from):
    """Brick joints as thin holes (filled levels), kept inside the outline and never crossing each other."""
    w = 0.55
    out = []
    for y in (9.0, 14.5):
        if y + w <= y_from:
            continue
        l, r = span_at(SHIELD, y)
        out.append(rect_d(l + 0.6, y - w, r - 0.6, y + w))
    joints = [(8.2, 4.9, 9.0 - w), (15.8, 4.9, 9.0 - w), (12, 9.0 + w, 14.5 - w), (8.6, 14.5 + w, 18.0), (15.4, 14.5 + w, 18.0)]
    for x, y0, y1 in joints:
        y0 = max(y0, y_from + 0.2)
        if y1 - y0 > 0.8:
            out.append(rect_d(x - w, y0, x + w, y1))
    return ''.join(out)


BRICK = bricks_lines()
icon('a_s0', P(SHIELD, dash='2.1 1.9'), P(BRICK, sw='1.05'))
icon('a_s1', P(SHIELD, sw='1.05'), P(BRICK, sw='1.05'))
icon('a_s2', P(SHIELD, sw='1.5'), P(SHIELD_IN, sw='1.5'), P('M7.4 12.2H16.6M12 7.4V12.2M9.8 12.2V17M14.2 12.2V17', sw='1.05'))
icon('a_s3', P(SHIELD), P('M' + fmt(span_at(SHIELD, 9.0)[0]) + ' 9H' + fmt(span_at(SHIELD, 9.0)[1]) + 'M8.2 4.4V9M15.8 4.4V9M12 9V12', sw='1.05'),
     P(clip_below(SHIELD, 12.0) + bricks_holes(12.0), fill='eo', stroke='0'))
icon('a_s4', P(SHIELD), P(emit(parse(SHIELD)) + bricks_holes(0.0), fill='eo', stroke='0'))
icon('a_s5', P(SHIELD, sw='3.2'), P(emit(parse(SHIELD)) + bricks_holes(0.0), fill='eo', stroke='0'))

# ---- weapon forms: kinetic, penetration growing with the shape
icon('w_mg_light', dot(16.4, 7.6, 2.7), P('M13.8 10.2L5.4 18.6M11.3 8.9L7.4 12.8M15.1 12.7L11.2 16.6'))
icon('w_mg_heavy', R('M12 4.5C13.6 6.2 14.2 8.1 14.2 10V18.5H9.8V10C9.8 8.1 10.4 6.2 12 4.5Z'))
icon('w_autocannon', R('M12 2.2C13.4 3.6 14 5.1 14 6.8V10.4H10V6.8C10 5.1 10.6 3.6 12 2.2Z'),
     R('M9.9 8.4H14.1'), R('M9.2 10.4H14.8V19.6H9.2Z'), R('M8.4 21.2H15.6'))
icon('w_dart', R('M12 5.6V19.2M9.6 7.2L12 2.6L14.4 7.2M12 15.4L9.2 21.2H14.8Z'))
icon('w_dart_heavy', R('M12 3V19.2M9.6 6.6L12 2.2L14.4 6.6M9.6 10.2L12 5.8L14.4 10.2M12 15.4L9.2 21.2H14.8Z'))
icon('w_rail', R('M12 5.4V20.4M9.9 6.8L12 2.6L14.1 6.8M12 17.6L10 21.4H14Z'),
     R('M7.6 10C7.6 9.2 9.6 8.6 12 8.6C14.4 8.6 16.4 9.2 16.4 10C16.4 10.8 14.4 11.4 12 11.4C9.6 11.4 7.6 10.8 7.6 10Z', sw='1.3'),
     R('M7.6 14.6C7.6 13.8 9.6 13.2 12 13.2C14.4 13.2 16.4 13.8 16.4 14.6C16.4 15.4 14.4 16 12 16C9.6 16 7.6 15.4 7.6 14.6Z', sw='1.3'))

# ---- high explosive, fragmentation
icon('w_shell', P('M10.8 3.2H13.2C14.9 5.3 15.6 7.6 15.6 9.9V20.8H8.4V9.9C8.4 7.6 9.1 5.3 10.8 3.2Z'),
     P('M9.6 6.4H14.4M8.4 16.6H15.6M8.4 18.6H15.6', sw='1.3'))
icon('w_mortar', R('M12 1.6C14.8 2.4 16.2 5 16.2 8C16.2 11.2 14.5 13.8 13.2 15.8H10.8C9.5 13.8 7.8 11.2 7.8 8C7.8 5 9.2 2.4 12 1.6Z'),
     R('M8.2 6.6H15.8', sw='1.2'), R('M8.2 22L10.8 17.6H13.2L15.8 22ZM12 17.6V22M10.8 15.8V17.6M13.2 15.8V17.6', sw='1.5'))
icon('w_airburst', R('M12 11.6C13.2 12.8 13.7 14.1 13.7 15.4V21H10.3V15.4C10.3 14.1 10.8 12.8 12 11.6Z'),
     dot(15.2, 8.8, 1.3), dot(18.9, 8.9, 1.2), dot(15.1, 5.1, 1.2), dot(19.8, 4.2, 1.1), dot(21.2, 12, 1), dot(12, 3.2, 1))
icon('w_grenade', R('M8.4 10.8C8.4 7.2 9.9 5.2 12 5.2C14.1 5.2 15.6 7.2 15.6 10.8Z'), R('M8.4 10.8H15.6V16.2H8.4Z'), R('M7.2 18.2H16.8', sw='2.2'))

# ---- rockets
icon('w_rocket', R('M12 4.6L13.4 7.4V15.8H10.6V7.4Z'), R('M10.6 12.8L8.4 16.8V18.4L10.6 16.6M13.4 12.8L15.6 16.8V18.4L13.4 16.6'))
icon('w_rocket_heavy', R('M12 1.6C13.3 2.8 14 4.4 14 5.8V19.2H10V5.8C10 4.4 10.7 2.8 12 1.6Z'),
     R('M10 8.6H14M10 11H14', sw='1.2'), R('M10 15.4L7.4 19.6V21.8L10 19.6M14 15.4L16.6 19.6V21.8L14 19.6'))

# ---- missiles, one shape each
icon('w_atgm', R('M8.8 9.4H15.2V17.4H8.8Z'), R('M8.8 9.4L12 3.2L15.2 9.4'), R('M8.8 14.6L6.2 18.8L8.8 17.4M15.2 14.6L17.8 18.8L15.2 17.4'))
icon('w_sam', R('M12 1.6L13.1 4.4V20.4H10.9V4.4Z'), R('M10.9 8.4L7.2 13.6H10.9M13.1 8.4L16.8 13.6H13.1'),
     R('M10.9 17.8L9 20.6H10.9M13.1 17.8L15 20.6H13.1'))
icon('w_cruise', R('M10.8 5C10.8 3.4 11.3 2.4 12 2.4C12.7 2.4 13.2 3.4 13.2 5V20H10.8Z'),
     R('M10.8 10.4L3.6 11.2V12.6L10.8 12.6M13.2 10.4L20.4 11.2V12.6L13.2 12.6'), R('M10.8 17.6L8.4 20.4M13.2 17.6L15.6 20.4'))
icon('w_ballistic', P('M8.6 9.2C8.6 6.4 10.2 3.6 12 1.8C13.8 3.6 15.4 6.4 15.4 9.2V19.4H8.6Z'),
     P('M8.6 12.6H15.4', sw='1.3'), P('M8.6 15.2L5.6 21.4H8.6M15.4 15.2L18.4 21.4H15.4'))

# ---- bombs, nose down
BOMB = 'M12 3.2C14.2 3.2 15.2 5.6 15.2 8.4V13.2C15.2 15 14 16.6 13 17.6H11C10 16.6 8.8 15 8.8 13.2V8.4C8.8 5.6 9.8 3.2 12 3.2Z'
BOMB_FINS = 'M11 17.6L8.4 21.2H15.6L13 17.6'


def shifted(d, dx, dy):
    ops = []
    for c, v in parse(d):
        if c == 'A':
            ops.append((c, v[:5] + [v[5] + dx, v[6] + dy]))
        else:
            ops.append((c, [x + (dx if k % 2 == 0 else dy) for k, x in enumerate(v)]))
    return emit(ops)


def rdot(x, y, r, deg=135):
    rx, ry = rot_pt(x, y, deg)
    return dot(rx, ry, r)


icon('w_bomb', R(BOMB, 135), R(BOMB_FINS, 135))
icon('w_bomb_guided', R(shifted(BOMB, 0, 3.4), 135, sw='1.6'), R(shifted(BOMB_FINS, 0, 3.4), 135, sw='1.6'),
     P('M20.8 6.6C22.6 11.8 20.4 17.6 15.4 20.8M17.6 21.6L15.2 20.9L15.8 18.4', sw='1.6'))
icon('w_bomb_cluster', R('M8.8 10.6V13.2C8.8 15 10 16.6 11 17.6H13C14 16.6 15.2 15 15.2 13.2V10.6', 135), R(BOMB_FINS, 135),
     rdot(12, 8.2, 1.35), rdot(9.2, 6.8, 1.3), rdot(14.8, 6.8, 1.3), rdot(10.6, 3.8, 1.3), rdot(13.4, 3.8, 1.3), rdot(7.4, 3.6, 1.1), rdot(16.6, 3.6, 1.1))
icon('w_bomb_heavy', R('M12 2.4C15 2.4 16.6 5 16.6 8V13C16.6 14.8 15.5 16 14.3 16.8H9.7C8.5 16 7.4 14.8 7.4 13V8C7.4 5 9 2.4 12 2.4Z', 135),
     R('M8.4 16.8H15.6V21.6H8.4Z', 135), R('M10.8 16.8V21.6M13.2 16.8V21.6M8.4 19.2H15.6M7.4 9.6H16.6', 135, sw='1.2'))
icon('w_napalm', R(shifted('M9.2 9C9.2 7.5 10.5 6.4 12 6.4C13.5 6.4 14.8 7.5 14.8 9V14.6C14.8 16.1 13.5 17.2 12 17.2C10.5 17.2 9.2 16.1 9.2 14.6Z', 0, 5.4), 135),
     P('M17.6 10.4C18.3 12.6 21.8 14.4 21.8 18A4.4 4.4 0 0 1 13 18C13 15.8 14.8 14.9 15.1 13C16 13.8 16.4 14.6 16.4 15.6C17.4 14.2 17.8 12.6 17.6 10.4Z'))

# ---- drones, from above
icon('w_fpv', P('M8.2 8.2L15.8 15.8M15.8 8.2L8.2 15.8'), P('M10.4 10.4H13.6V13.6H10.4Z', fill='1'),
     ring(5.6, 5.6, 3.1, sw='1.4'), ring(18.4, 5.6, 3.1, sw='1.4'), ring(5.6, 18.4, 3.1, sw='1.4'), ring(18.4, 18.4, 3.1, sw='1.4'))
icon('w_shahed', P('M12 2.4C12.8 2.4 13.2 3.4 13.2 5V19.6H10.8V5C10.8 3.4 11.2 2.4 12 2.4Z'),
     P('M10.8 8.4L2.8 18.4V19.6H10.8M13.2 8.4L21.2 18.4V19.6H13.2'), P('M2.8 16.2V21.4M21.2 16.2V21.4', sw='1.4'))
icon('w_lancet', P('M11 4.2C11 3 11.4 2 12 2C12.6 2 13 3 13 4.2V21.6H11Z'),
     P('M7.4 4.6L16.6 11M16.6 4.6L7.4 11M6.2 13.6L17.8 21M17.8 13.6L6.2 21'))

# ---- fire, energy
icon('w_flame', P('M3.2 18.6L6.6 22L10.2 18.4L6.8 15Z'), P('M8.6 16.8L10.4 15'),
     P('M10.6 14.2C12.4 9.6 16.2 5.8 21.6 2.6C20.8 8.2 17.4 12.4 10.6 14.2Z'), P('M13.4 12.6C15 10.4 16.6 8.8 18.6 7.4', sw='1.2'))
icon('w_beam', P('M3 18.2L5.8 21L8.2 18.6L5.4 15.8Z'), P('M7.2 16.8L15.4 8.6', sw='2.2'), dot(17.2, 6.8, 2.1),
     P('M17.2 1.6V3.2M17.2 10.4V12M22.4 6.8H20.8M13.6 6.8H12M20.9 3.1L19.8 4.2M14.6 9.4L13.5 10.5M20.9 10.5L19.8 9.4M14.6 4.2L13.5 3.1', sw='1.3'))

# ---- boss and special weapons
icon('w_blade', P('M2.8 7.4C8 5.8 16 5.8 21.2 7.4V14.6C16 13 8 13 2.8 14.6Z'),
     P('M5 14V17.2M8.6 13.4V16.6M12 13.2V16.4M15.4 13.4V16.6M19 14V17.2M8 6.4V2.8M16 6.4V2.8', sw='1.4'))
icon('w_drill', R('M8.8 7.6H15.2L12 22Z'), R('M10.4 7.6V3.6H13.6V7.6'), R('M9.4 10.6L14.6 12.2M10.2 14L13.8 15.2M11 17.4L13 18.2', sw='1.2'))
icon('w_supergun', R('M10.9 2.6H13.1C14.6 4.4 15.4 6.4 15.4 8.6V15.8H8.6V8.6C8.6 6.4 9.4 4.4 10.9 2.6Z'),
     R('M8.6 12H15.4M8.6 13.9H15.4', sw='1.2'), R('M7.2 18.2C9.4 19.6 14.6 19.6 16.8 18.2M5.4 21C8.4 23 15.6 23 18.6 21', sw='1.4'))
icon('w_charge', P('M6.2 9.2H9.6V20.6H6.2ZM10.3 9.2H13.7V20.6H10.3ZM14.4 9.2H17.8V20.6H14.4Z'), P('M5.4 13.6H18.6', sw='1.3'),
     P('M12 9.2C12 6 14 4.4 17 4'), P(star_d(19.2, 3.6, 2.4, 0.9, 4, -90), fill='1', stroke='0'))

# ---- damage-type marks (drawn for about 10 pt: bold, mostly filled)
icon('d_shaped', P('M2.8 12L13.4 5V19Z', fill='1'), P('M16.4 8.2L21 6.2M16.8 12H21.8M16.4 15.8L21 17.8', sw='2'))
icon('d_he', P(star_d(12, 12, 10.2, 4.4, 8, -90), fill='1', stroke='0'))
icon('d_thermo', P(star_d(12, 12, 6.2, 2.7, 8, -67.5), fill='1', stroke='0'), ring(12, 12, 9.6, sw='2'))
icon('d_fire', P('M12 1.8C13.2 5.6 18 8.2 18 14.2A6 6 0 0 1 6 14.2C6 10.4 8.8 9.2 9.3 6C10.9 7.4 11.6 8.6 11.6 10.4C13 8.2 13 5.2 12 1.8Z', fill='1', stroke='0'))
icon('d_frag', dot(12, 12, 2.2), dot(12, 4.2, 2), dot(18.8, 8.1, 2), dot(18.8, 15.9, 2), dot(12, 19.8, 2), dot(5.2, 15.9, 2), dot(5.2, 8.1, 2))
icon('d_energy', P('M3.4 20.6L13.2 10.8', sw='2.4'), P(star_d(16.6, 7.4, 6.6, 1.7, 4, -90), fill='1', stroke='0'))

# ---- extra marks (detail page and tooltips only)
icon('x_top', P('M12 1.8V11.6M7.6 7.4L12 11.8L16.4 7.4', sw='2'), P('M3.6 21.6H20.4L18.6 17.6H5.4ZM8.8 17.6C8.8 15.6 10.2 14.4 12 14.4C13.8 14.4 15.2 15.6 15.2 17.6', sw='1.6'))
icon('x_guided', P('M3.4 20.6C3.4 13 12 15.6 12 9.4C12 5.4 14.8 3.6 19.8 3.6', sw='2'), P('M16.6 1L19.8 3.6L17 6.4', sw='2'))
icon('x_splash', ring(12, 12, 7.8, sw='2'), dot(12, 12, 2.4))

# ---- verdict marks for the enemy tooltip (the fonts have no check or cross)
icon('m_good', P('M3.8 12.8L9.4 18.2L20.4 5.8', sw='2.6'))
icon('m_poor', P('M3.2 14.2C5.6 9.4 8.4 9.2 12 12C15.6 14.8 18.4 14.6 20.8 9.8', sw='2.6'))
icon('m_none', P('M6.2 6.2L17.8 17.8M17.8 6.2L6.2 17.8', sw='2.6'))


# ---------------------------------------------------------------- output

def write_cs():
    lines = [
        '// Generated by Tools/art/combat_icons.py (prompt 15 D): the armour and weapon icon set. Do not edit by hand.',
        'using System.Collections.Generic;',
        '',
        'namespace MachineBrigade.Game.Hud',
        '{',
        '    public static partial class Icons',
        '    {',
        '        /// <summary>a_g/a_a/a_s + level: ground, air and structure armour; w_: weapon forms; d_: damage-type',
        '        /// marks; x_: extra marks; m_: the enemy tooltip\'s verdicts. See CombatIcons for the mapping.</summary>',
        '        private static readonly Dictionary<string, string> CombatSvg = new()',
        '        {',
    ]
    for k, v in ICONS.items():
        lines.append(f'            ["{k}"] = "{v.replace(chr(34), chr(92) + chr(34))}",')
    lines += ['        };', '    }', '}', '']
    with open(OUT, 'wb') as f:
        f.write('\r\n'.join(lines).encode('utf-8'))
    print('wrote', OUT, len(ICONS), 'icons')


ELEM = re.compile(r'<(path|circle)\s([^>]*)/>')
ATTR = re.compile(r'([a-z]+)="([^"]*)"')


def render(svg, size, stroke=1.8, ss=6):
    from PIL import Image, ImageDraw, ImageChops
    big = size * ss
    k = big / 24.0
    ink = Image.new('L', (big, big), 0)
    for m in ELEM.finditer(svg):
        a = dict(ATTR.findall(m.group(2)))
        if m.group(1) == 'circle':
            d = circle_d(float(a['cx']), float(a['cy']), float(a['r']))
        else:
            d = a['d']
        subs = flatten(d)
        fill = a.get('fill')
        if fill in ('1', 'eo'):
            layer = Image.new('L', (big, big), 0)
            for pts, _ in subs:
                poly = Image.new('L', (big, big), 0)
                ImageDraw.Draw(poly).polygon([(x * k, y * k) for x, y in pts], fill=255)
                layer = ImageChops.logical_xor(layer.convert('1'), poly.convert('1')).convert('L') if fill == 'eo' else ImageChops.lighter(layer, poly)
            ink = ImageChops.lighter(ink, layer)
        if a.get('stroke', '1') != '0':
            w = float(a.get('sw', stroke)) * k
            dash = a.get('dash')
            dr = ImageDraw.Draw(ink)
            for pts, _ in subs:
                segs = dash_points(pts, dash) if dash else [pts]
                for sp in segs:
                    sp = [(x * k, y * k) for x, y in sp]
                    if len(sp) > 1:
                        dr.line(sp, fill=255, width=max(1, int(round(w))), joint='curve')
                    for x, y in (sp[0], sp[-1]):
                        dr.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=255)
    return ink.resize((size, size), Image.LANCZOS)


def dash_points(pts, dash):
    on, off = (float(x) for x in dash.split())
    out, cur, drawing, left = [], [pts[0]], True, on
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b); w = 0.0
        while L - w > left:
            w += left
            p = (a[0] + (b[0] - a[0]) * w / L, a[1] + (b[1] - a[1]) * w / L)
            if drawing:
                cur.append(p); out.append(cur)
            else:
                cur = [p]
            drawing = not drawing
            left = on if drawing else off
        left -= L - w
        if drawing:
            cur.append(b)
    if drawing and len(cur) > 1:
        out.append(cur)
    return out


def preview(path):
    from PIL import Image, ImageDraw
    names = list(ICONS)
    cols = 12
    small, large, pad = 33, 96, 10
    cell = large + small + pad * 3
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell, rows * (large + pad * 2 + 14)), (24, 27, 31))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        x, y = (i % cols) * cell, (i // cols) * (large + pad * 2 + 14)
        for sz, ox in ((large, pad), (small, pad * 2 + large)):
            im = render(ICONS[n], sz)
            col = Image.new('RGB', (sz, sz), (232, 234, 236))
            sheet.paste(col, (x + ox, y + pad), im)
        d.text((x + pad, y + large + pad + 2), n, fill=(160, 168, 176))
    sheet.save(path)
    print('preview', path)


if __name__ == '__main__':
    write_cs()
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
