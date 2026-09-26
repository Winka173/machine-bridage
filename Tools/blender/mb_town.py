"""Machine Brigade town buildings, field barriers and civilian vehicles built with frontier_kit.

Footprints follow the art brief (Blender X = width, Y = depth, metres). The street side and the
entrance face -Y; origins sit on the ground at the footprint centre. Every building shares one
detail language with mb_props.house(): bevelled wall blocks on a plinth, framed windows with a
random share of lit panes, and roofs that are thick shells with real eaves and verges.

Parts that touch are pushed into each other (never laid face to face) because coplanar faces
z-fight in game: wall blocks rise 2 cm into their roofs, frames sit 3 cm proud of the wall and
panes 1.5 cm proud of their frames.
"""
import math
import random

import bmesh
from mathutils import Matrix

R90 = math.pi / 2
# Outward normal and the facade's "along" direction for each wall orientation.
NORMAL = {'-y': (0, -1), '+y': (0, 1), '-x': (-1, 0), '+x': (1, 0)}
TANGENT = {'-y': (1, 0), '+y': (-1, 0), '-x': (0, -1), '+x': (0, 1)}


# ----------------------------------------------------------------------------- facade helpers
def fbox(part, face, p, size, out=0.0, bevel=0.0, seg=1):
    """Box on a facade. p is a point on the wall surface, size = (along, off the wall, height)
    and out moves the box centre off the wall along its outward normal."""
    nx, ny = NORMAL[face]
    su, sn, sz = size
    dims = (su, sn, sz) if nx == 0 else (sn, su, sz)
    part.box(dims, loc=(p[0] + nx * out, p[1] + ny * out, p[2]), bevel=bevel, seg=seg)
    return part


def slide(face, p, du=0.0, dz=0.0):
    tx, ty = TANGENT[face]
    return p[0] + tx * du, p[1] + ty * du, p[2] + dz


def pane(a, rng, lit):
    return a.part('Lit_windows', 'Lamp') if rng.random() < lit else a.part('Windows', 'Glass')


def window(a, rng, face, p, w=.9, h=1.2, frame='Wood', lit=.22, mullion=2, sill='Concrete', shutters=None):
    """Framed window centred on wall point p. mullion: 0 none, 1 upright bar, 2 cross."""
    fr = a.part('Frames', frame)
    fbox(fr, face, p, (w + .16, .1, h + .16), out=.03)
    fbox(pane(a, rng, lit), face, p, (w, .06, h), out=.065)
    if mullion:
        fbox(fr, face, p, (.06, .05, h - .02), out=.1)
    if mullion > 1:
        fbox(fr, face, slide(face, p, 0, h * .18), (w - .02, .05, .06), out=.11)
    if sill:
        fbox(a.part('Sills', sill), face, slide(face, p, 0, -h / 2 - .1), (w + .3, .19, .08), out=.085)
    if shutters:
        sh = a.part('Shutters', shutters)
        for s in (-1, 1):
            fbox(sh, face, slide(face, p, s * (w / 2 + .1 + w * .25)), (w * .5, .05, h + .06), out=.035)


def door(a, face, p, w=1.0, h=2.1, mat='Wood', frame='PlasterWhite', step='Concrete', lamp=True, glazed=False):
    """Recessed door; p is the wall point at the middle of the threshold."""
    fr = a.part('Door_frame', frame)
    for s in (-1, 1):
        fbox(fr, face, slide(face, p, s * (w / 2 + .07), h / 2 + .02), (.14, .14, h + .04), out=.04)
    fbox(fr, face, slide(face, p, 0, h + .09), (w + .32, .14, .18), out=.05)
    fbox(a.part('Door', mat), face, slide(face, p, 0, h / 2), (w, .08, h), out=.01, bevel=.015)
    if glazed:
        fbox(a.part('Windows', 'Glass'), face, slide(face, p, 0, h * .68), (w * .62, .03, h * .34), out=.055)
    if step and p[2] > .05:
        fbox(a.part('Steps', step), face, (p[0], p[1], p[2] / 2 - .01), (w + .7, .55, p[2] - .02), out=.25,
             bevel=.03)
    if lamp:
        fbox(a.part('Door_lamp', 'Lamp'), face, slide(face, p, w / 2 + .42, h + .15), (.16, .12, .18), out=.07,
             bevel=.03)


def head(part, face, p, half, rise, depth, out):
    """Triangular gable head (pointed window or door top) standing on wall point p."""
    nx, ny = NORMAL[face]
    tri = [(-half, 0), (half, 0), (0, rise)]
    loc = (p[0] + nx * out, p[1] + ny * out, p[2])
    part.prism(tri, depth, loc=loc, axis='Y' if nx == 0 else 'X', bevel=0)


def lancet(a, rng, face, p, w, h, frame='Concrete', lit=.15, glass=None):
    """Pointed-arch window: a framed rectangle with a triangular head (p = rectangle centre)."""
    fr = a.part('Frames', frame)
    gl = a.part('Openings', glass) if glass else pane(a, rng, lit)
    fbox(fr, face, p, (w + .2, .1, h + .1), out=.03)
    fbox(gl, face, p, (w, .06, h), out=.065)
    top = slide(face, p, 0, h / 2)
    head(fr, face, top, w / 2 + .1, (w / 2 + .1) * 1.5, .12, .03)
    head(gl, face, top, w / 2, w / 2 * 1.5, .08, .065)


def oculus(a, rng, face, p, r, frame='Concrete', lit=.5):
    """Round window with a stone ring and cross tracery."""
    nx, ny = NORMAL[face]
    rot = (R90, 0, 0) if nx == 0 else (0, R90, 0)
    at = lambda o: (p[0] + nx * o, p[1] + ny * o, p[2])  # noqa: E731
    a.part('Frames', frame).cyl(r + .16, .12, loc=at(.04), rot=rot, seg=16, bevel=.02, bseg=1)
    pane(a, rng, lit).cyl(r, .06, loc=at(.11), rot=rot, seg=16, bevel=0)
    fr = a.part('Frames', frame)
    fbox(fr, face, p, (2 * r, .04, .07), out=.14)
    fbox(fr, face, p, (.07, .04, 2 * r), out=.155)


def gabled_walls(part, w, d, H, rise, ridge, centre=(0, 0), base=0.0, bevel=.05):
    """House-shaped wall block: w x d x H with gable triangles under a ridge along X or Y."""
    h = (d if ridge == 'x' else w) / 2
    prof = [(-h, 0), (h, 0), (h, H), (0, H + rise), (-h, H)]
    part.prism(prof, w if ridge == 'x' else d, loc=(centre[0], centre[1], base), axis='X' if ridge == 'x' else 'Y',
               bevel=bevel)


def roof_shell(part, prof, length, ridge='x', t=.18, centre=(0, 0), bevel=.03):
    """Roof of thickness t whose underside follows prof [(u, z)...] from the eave (u < 0) up to the
    ridge (u = 0), mirrored across the ridge. One prism with exact mitres; eaves end in vertical
    fascias. ridge 'x' runs the ridge along X (u is Y), 'y' along Y (u is X)."""
    inner = [tuple(q) for q in prof] + [(-u, z) for u, z in reversed(prof[:-1])]
    normals = []
    for (u0, z0), (u1, z1) in zip(inner, inner[1:]):
        L = math.hypot(u1 - u0, z1 - z0)
        normals.append((-(z1 - z0) / L, (u1 - u0) / L))
    outer = []
    for i, (u, z) in enumerate(inner):
        if i in (0, len(inner) - 1):
            nz = normals[0][1] if i == 0 else normals[-1][1]
            outer.append((u, z + t / nz))
        else:
            n0, n1 = normals[i - 1], normals[i]
            k = t / (1 + n0[0] * n1[0] + n0[1] * n1[1])
            outer.append((u + (n0[0] + n1[0]) * k, z + (n0[1] + n1[1]) * k))
    part.prism(inner + outer[::-1], length, loc=(centre[0], centre[1], 0), axis='X' if ridge == 'x' else 'Y',
               bevel=bevel)
    return outer


def gable_roof(a, mat, w, d, top, k, ridge, centre=(0, 0), eave=.4, verge=.3, t=.18, cap='Concrete'):
    """Pitched roof over a w x d wall block whose eaves are at height top; k = rise / half-span."""
    half = (d if ridge == 'x' else w) / 2
    length = (w if ridge == 'x' else d) + 2 * verge
    roof_shell(a.part('Roof', mat), [(-half - eave, top - eave * k), (0, top + half * k)], length, ridge, t=t,
               centre=centre)
    zr = top + half * k + t * math.sqrt(1 + k * k)
    if cap:
        size = (length - .1, .3, .14) if ridge == 'x' else (.3, length - .1, .14)
        a.part('Ridge', cap).box(size, loc=(centre[0], centre[1], zr - .03), bevel=.03, seg=1)
    return zr


def dormer(a, rng, face, p, w, h, depth, roof, walls, k=.8, frame='Wood', lit=.22):
    """Gabled dormer. p = bottom centre of its front wall where it meets the main roof's underside."""
    nx, ny = NORMAL[face]
    cx, cy = p[0] - nx * depth / 2, p[1] - ny * depth / 2
    ridge = 'x' if nx else 'y'
    zb = p[2] - .25
    Hd = h + .25
    gabled_walls(a.part('Walls', walls), depth if nx else w, w if nx else depth, Hd + .02, w / 2 * k, ridge, (cx, cy),
                 zb, bevel=.03)
    top = zb + Hd
    roof_shell(a.part('Roof', roof), [(-w / 2 - .15, top - .15 * k), (0, top + w / 2 * k)], depth + .15, ridge, t=.12,
               centre=(cx + nx * .075, cy + ny * .075))
    window(a, rng, face, (p[0], p[1], p[2] + .2 + h * .36), w=w * .56, h=h * .56, frame=frame, lit=lit, sill=None)


def chimney(a, x, y, z0, z1, w=.65, d=.65, mat='Brick'):
    a.part('Chimney', mat).box((w, d, z1 - z0), loc=(x, y, (z0 + z1) / 2), bevel=.04)
    a.part('Chimney_cap', 'Concrete').box((w + .16, d + .16, .12), loc=(x, y, z1 + .05), bevel=.02, seg=1)
    a.part('Chimney_pot', 'Armor').cyl(.09, .3, loc=(x + w * .2, y, z1 + .25), seg=8, bevel=0)


def ac_unit(a, face, p, out=.21, mat='Fuel'):
    """Wall air conditioner with a dark fan disc."""
    fbox(a.part('AC', mat), face, p, (.8, .42, .55), out=out, bevel=.03)
    nx, ny = NORMAL[face]
    rot = (R90, 0, 0) if nx == 0 else (0, R90, 0)
    c = out + .22
    a.part('AC_fan', 'Rubber').cyl(.17, .03, loc=slide(face, (p[0] + nx * c, p[1] + ny * c, p[2]), .12), rot=rot,
                                   seg=10, bevel=0)


def letters(a, rng, face, p, width, h=.42, mat='Armor', out=.1):
    """A row of dark blocks of varying width that reads as sign lettering."""
    part = a.part('Letters', mat)
    widths = []
    while sum(widths) + .1 * len(widths) < width - .5:
        widths.append(rng.uniform(.18, .4))
    x = -(sum(widths) + .1 * (len(widths) - 1)) / 2
    for i, lw in enumerate(widths):
        gap = .1 if (i + 1) % 4 else .28
        fbox(part, face, slide(face, p, x + lw / 2), (lw, .03, h * rng.uniform(.85, 1.0)), out=out)
        x += lw + gap * .6


# ----------------------------------------------------------------------------- houses
def cottage(a):
    """One-storey cottage (7 x 6 m): steep slate gable, dormer, brick chimney, gabled porch."""
    rng = random.Random(21)
    w, d, cy, base, H, k = 6.2, 4.4, .35, .3, 2.7, 1.2
    top, hd = base + H, d / 2
    y0, y1 = cy - hd, cy + hd
    walls = a.part('Walls', 'PlasterWhite')
    wood = a.part('Timber', 'Wood')
    a.part('Plinth', 'Concrete').box((w + .16, d + .16, base), loc=(0, cy, base / 2), bevel=.04)
    gabled_walls(walls, w, d, H + .02, hd * k, 'x', (0, cy), base)
    for sx in (-1, 1):
        for sy in (-1, 1):
            wood.box((.2, .2, H), loc=(sx * (w / 2 - .07), cy + sy * (hd - .07), base + H / 2), bevel=.02, seg=1)
    gable_roof(a, 'RoofSlate', w, d, top, k, 'x', centre=(0, cy), eave=.45, verge=.25, t=.2)
    zw = base + 1.5
    for x in (-1.95, 1.95):
        window(a, rng, '-y', (x, y0, zw), w=.9, h=1.1, frame='Wood', shutters='Wood' if x < 0 else None)
    for x in (-1.6, 1.6):
        window(a, rng, '+y', (x, y1, zw), w=.9, h=1.1, frame='Wood')
    for face, x in (('-x', -w / 2), ('+x', w / 2)):
        window(a, rng, face, (x, cy, zw), w=.9, h=1.1, frame='Wood')
        window(a, rng, face, (x, cy, top + 1.0), w=.55, h=.7, frame='Wood', mullion=1, sill=None)
    door(a, '-y', (0, y0, base), w=1.0, h=2.05, mat='WoodRed', frame='Wood', step=None)
    # Porch: plank deck, two posts, a beam and a small gabled roof tucked under the eaves.
    wood.box((2.5, 1.15, .26), loc=(0, y0 - .5, .13), bevel=.03, seg=1)
    for sx in (-1, 1):
        wood.box((.14, .14, 2.12), loc=(sx * 1.05, y0 - .93, .26 + 1.06), bevel=.02, seg=1)
    wood.box((2.4, .16, .18), loc=(0, y0 - .93, 2.45), bevel=.02, seg=1)
    roof_shell(a.part('Roof', 'RoofSlate'), [(-1.3, 2.5), (0, 2.5 + 1.3 * .62)], 1.3, 'y', t=.14,
               centre=(0, y0 - .47))
    walls.prism([(-1.15, 0), (1.15, 0), (0, 1.15 * .62)], .08, loc=(0, y0 - .93, 2.54), axis='Y', bevel=0)
    dormer(a, rng, '-y', (-1.9, cy - (hd - .8), top + .8 * k), 1.15, 1.35, 1.6, 'RoofSlate', 'PlasterWhite')
    chimney(a, 1.7, cy + .9, top + 1.2, top + hd * k + .75, w=.7, d=.7)
    # Wood pile against the east gable.
    logs = a.part('Logs', 'Wood')
    for i in range(3):
        for j in range(3 - i):
            logs.cyl(.12, 1.3, loc=(w / 2 + .15 + (j + i * .5) * .23, cy - 1.25, .12 + i * .21), rot=(R90, 0, 0), seg=7,
                     bevel=0)


def townhouse(a):
    """Two-storey town house (6 x 9 m) with its gable to the street, balcony and green shutters."""
    rng = random.Random(33)
    w, d, cy, base, storey, k = 5.4, 8.0, .3, .3, 3.0, 1.0
    H = 2 * storey
    top, hw = base + H, w / 2
    y0, y1 = cy - d / 2, cy + d / 2
    walls = a.part('Walls', 'PlasterOchre')
    trim = a.part('Trim', 'PlasterWhite')
    a.part('Plinth', 'Concrete').box((w + .16, d + .16, base), loc=(0, cy, base / 2), bevel=.04)
    gabled_walls(walls, w, d, H + .02, hw * k, 'y', (0, cy), base)
    trim.box((w + .1, d + .1, .16), loc=(0, cy, base + storey), bevel=.02, seg=1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            trim.box((.3, .3, H), loc=(sx * (hw - .11), cy + sy * (d / 2 - .11), base + H / 2), bevel=.03, seg=1)
    gable_roof(a, 'Roof', w, d, top, k, 'y', centre=(0, cy), eave=.35, verge=.25)
    sh = 'RoofGreen'
    # Street gable: door and shop-sized window below, balcony door above, attic window in the gable.
    door(a, '-y', (-1.25, y0, base), w=1.0, h=2.2, mat='Wood', frame='PlasterWhite', glazed=True)
    window(a, rng, '-y', (1.15, y0, base + 1.55), w=1.2, h=1.4, frame='PlasterWhite', shutters=sh)
    zf = base + storey
    window(a, rng, '-y', (0, y0, zf + .15 + 1.05), w=.95, h=2.1, frame='PlasterWhite', mullion=1, sill=None,
           shutters=sh)
    for x in (-1.95, 1.95):
        window(a, rng, '-y', (x, y0, zf + 1.55), w=.55, h=1.2, frame='PlasterWhite', mullion=1)
    window(a, rng, '-y', (0, y0, top + 1.0), w=.6, h=.8, frame='PlasterWhite', sill='PlasterWhite')
    # Balcony: slab on brackets with a wrought-iron railing.
    conc = a.part('Balcony', 'Concrete')
    conc.box((2.5, .86, .16), loc=(0, y0 - .42, zf + .1), bevel=.03, seg=1)
    for x in (-1.0, 1.0):
        conc.prism([(y0 + .02, 0), (y0 - .7, 0), (y0 + .02, -.55)], .14, loc=(x, 0, zf + .02), axis='X', bevel=0)
    iron = a.part('Railing', 'Armor')
    ztop = zf + .18
    iron.box((2.47, .05, .06), loc=(0, y0 - .8, ztop + .95), bevel=0)
    for sx in (-1, 1):
        iron.box((.05, .8, .06), loc=(sx * 1.22, y0 - .41, ztop + .935), bevel=0)
        for yy in (-.3, -.6):
            iron.box((.03, .03, .95), loc=(sx * 1.22, y0 + yy, ztop + .47), bevel=0)
    for i in range(1, 8):
        iron.box((.035, .035, .95), loc=(-1.2 + i * .3, y0 - .8, ztop + .47), bevel=0)
    for sx in (-1, 1):
        iron.box((.03, .03, .95), loc=(sx * 1.22, y0 - .8, ztop + .47), bevel=0)
    # Long sides and back.
    for face, x in (('-x', -hw), ('+x', hw)):
        for f in range(2):
            for yy in (-2.6, 0, 2.6):
                window(a, rng, face, (x, cy + yy, base + f * storey + 1.55), w=.8, h=1.3, frame='PlasterWhite',
                       mullion=1, shutters=sh)
    for f in range(2):
        for x in (-1.25, 1.25):
            if f == 0 and x < 0:
                door(a, '+y', (x, y1, base), w=.9, h=2.1, mat='Wood', lamp=False)
            else:
                window(a, rng, '+y', (x, y1, base + f * storey + 1.55), w=.8, h=1.3, frame='PlasterWhite',
                       shutters=sh)
    for face, sx in (('-x', -1), ('+x', 1)):
        dormer(a, rng, face, (sx * (hw - .9), cy + .6, top + .9 * k), 1.0, 1.3, 1.4, 'Roof', 'PlasterOchre',
               frame='PlasterWhite')
    chimney(a, 0, cy + 2.7, top + 2.0, top + hw * k + .9, w=.6, d=.9)


def apartment(a):
    """Three-storey brick apartment block (14 x 10 m): flat roof behind a parapet, stair house,
    water tank, wall air conditioners, balconies and an entrance canopy."""
    rng = random.Random(47)
    w, d, cy, base, storey = 13.2, 9.0, .35, .4, 3.0
    H = 3 * storey
    top = base + H
    y0, y1 = cy - d / 2, cy + d / 2
    brick = a.part('Walls', 'Brick')
    conc = a.part('Trim', 'Concrete')
    conc.box((w + .16, d + .16, base), loc=(0, cy, base / 2), bevel=.04)
    brick.box((w, d, H), loc=(0, cy, base + H / 2), bevel=.05)
    for f in (1, 2):
        conc.box((w + .1, d + .1, .18), loc=(0, cy, base + f * storey), bevel=.02, seg=1)
    conc.box((w + .2, d + .2, .24), loc=(0, cy, top), bevel=.03, seg=1)
    pt, ph, pz = .3, .75, top + .1
    for sy in (-1, 1):
        brick.box((w, pt, ph), loc=(0, cy + sy * (d / 2 - pt / 2), pz + ph / 2), bevel=.02, seg=1)
        conc.box((w + .08, pt + .1, .1), loc=(0, cy + sy * (d / 2 - pt / 2), pz + ph + .03), bevel=.02, seg=1)
    for sx in (-1, 1):
        brick.box((pt, d - 2 * pt, ph), loc=(sx * (w / 2 - pt / 2 - .01), cy, pz + ph / 2), bevel=.02, seg=1)
        conc.box((pt + .1, d - 2 * pt - .1, .1), loc=(sx * (w / 2 - pt / 2), cy, pz + ph + .03), bevel=.02, seg=1)
    deck = top + .16
    a.part('Roof_deck', 'RoofSlate').box((w - 2 * pt + .04, d - 2 * pt + .04, .12), loc=(0, cy, deck - .06), bevel=0)
    cols = (-5.2, -2.6, 0, 2.6, 5.2)
    win = dict(w=1.2, h=1.5, frame='PlasterWhite', mullion=1)
    for f in range(3):
        zf = base + f * storey
        for x in cols:
            if f == 0 and x == 0:
                continue
            if f and abs(x) == 2.6:
                window(a, rng, '-y', (x, y0, zf + .2 + 1.05), w=1.0, h=2.1, frame='PlasterWhite', mullion=1, sill=None)
                conc.box((2.0, .9, .16), loc=(x, y0 - .42, zf + .08), bevel=.03, seg=1)
                panel = a.part('Balcony_panels', 'PlasterWhite')
                panel.box((2.0, .06, .95), loc=(x, y0 - .84, zf + .16 + .47), bevel=.02, seg=1)
                for sx in (-1, 1):
                    panel.box((.06, .8, .95), loc=(x + sx * .96, y0 - .42, zf + .16 + .47), bevel=.02, seg=1)
                continue
            window(a, rng, '-y', (x, y0, zf + 1.6), **win)
        for x in cols:
            window(a, rng, '+y', (x, y1, zf + 1.6), **win)
        for face, x in (('-x', -w / 2), ('+x', w / 2)):
            for yy in (-2.8, 0, 2.8):
                window(a, rng, face, (x, cy + yy, zf + 1.6), **win)
    # Entrance: glazed double door under a cantilevered canopy on two posts.
    window(a, rng, '-y', (0, y0, base + 1.25), w=1.8, h=2.4, frame='Steel', mullion=1, sill=None, lit=0)
    conc.box((3.4, 1.0, .2), loc=(0, y0 - .45, base + 2.95), bevel=.04)
    for sx in (-1, 1):
        a.part('Posts', 'Steel').cyl(.06, base + 2.85, loc=(sx * 1.55, y0 - .85, (base + 2.85) / 2), seg=8, bevel=0)
    conc.box((2.8, .9, .2), loc=(0, y0 - .45, .1), bevel=.03, seg=1)
    conc.box((2.8, .5, .18), loc=(0, y0 - .25, .29), bevel=.03, seg=1)
    fbox(a.part('Door_lamp', 'Lamp'), '-y', (1.3, y0, base + 2.5), (.18, .12, .2), out=.07, bevel=.03)
    for x, f in ((-4.06, 1), (4.06, 2), (-1.14, 2), (1.14, 1), (3.9, 0), (-3.9, 0)):
        ac_unit(a, '-y', (x, y0, base + f * storey + .6))
    for yy, f in ((-1.4, 1), (1.4, 2)):
        ac_unit(a, '+x', (w / 2, cy + yy, base + f * storey + .6))
    for x, f in ((-3.9, 0), (1.3, 1), (3.9, 2)):
        ac_unit(a, '+y', (x, y1, base + f * storey + .6))
    # Drain pipes.
    for sx in (-1, 1):
        a.part('Pipes', 'Steel').cyl(.07, top, loc=(sx * (w / 2 + .1), y0 + .35, top / 2), seg=6, bevel=0)
    # Roof: stair house, water tank on a stand, air conditioners, vents and an aerial.
    hx, hy = -3.6, cy + 1.7
    brick.box((3.0, 2.6, 2.4), loc=(hx, hy, deck + 1.2), bevel=.04)
    conc.box((3.3, 2.9, .16), loc=(hx, hy, deck + 2.48), bevel=.03, seg=1)
    door(a, '-y', (hx, hy - 1.3, deck), w=.9, h=2.0, mat='Steel', frame='Concrete', step=None)
    steel = a.part('Roof_steel', 'Steel')
    tx, ty = 3.8, cy + 2.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            steel.box((.1, .1, 1.1), loc=(tx + sx * .6, ty + sy * .6, deck + .55), bevel=0)
    steel.box((1.6, 1.6, .1), loc=(tx, ty, deck + 1.1), bevel=.02, seg=1)
    a.part('Tank', 'Fuel').cyl(.8, 1.7, loc=(tx, ty, deck + 1.15 + .85), seg=14, bevel=.04)
    a.part('Tank_lid', 'Armor').cyl(.84, .1, loc=(tx, ty, deck + 2.05), r2=.5, seg=14, bevel=0)
    for x, y in ((0, cy - 2.0), (4.0, cy - 1.9)):
        a.part('Roof_AC', 'MetalSheet').box((1.3, .9, .7), loc=(x, y, deck + .35), bevel=.04)
        a.part('AC_fan', 'Rubber').cyl(.3, .04, loc=(x + .25, y, deck + .71), seg=12, bevel=0)
    for x, y in ((-.9, cy + 2.4), (1.6, cy + .6), (-5.4, cy - 1.8)):
        steel.cyl(.11, .8, loc=(x, y, deck + .4), seg=8, bevel=0)
        steel.cyl(.17, .08, loc=(x, y, deck + .84), seg=8, bevel=0)
    steel.limb((hx + .9, hy + .8, deck + 2.5), (hx + .9, hy + .8, deck + 5.2), .05, .05, bevel=0)
    for z, half in ((deck + 4.4, .7), (deck + 4.9, .5)):
        steel.limb((hx + .9 - half, hy + .76, z), (hx + .9 + half, hy + .76, z), .035, .035, bevel=0)


def shop(a):
    """Corner shop (9 x 7 m): false front with a sign board, striped awning and big windows."""
    rng = random.Random(58)
    w, d, cy, base, H = 8.6, 6.0, .5, .2, 3.8
    top = base + H
    y0, y1 = cy - d / 2, cy + d / 2
    walls = a.part('Walls', 'PlasterBlue')
    trim = a.part('Trim', 'PlasterWhite')
    a.part('Plinth', 'Concrete').box((w + .12, d + .12, base), loc=(0, cy, base / 2), bevel=.03)
    walls.box((w, d, H), loc=(0, cy, base + H / 2), bevel=.05)
    trim.box((w + .18, d + .18, .22), loc=(0, cy, top), bevel=.03, seg=1)
    pt = .25
    for sx in (-1, 1):
        walls.box((pt, d - .3 - pt, .5), loc=(sx * (w / 2 - pt / 2), cy + .15 - pt / 2, top + .33), bevel=.02,
                  seg=1)
    walls.box((w - .02, pt, .5), loc=(0, y1 - pt / 2, top + .33), bevel=.02, seg=1)
    for sx in (-1, 1):
        trim.box((pt + .08, d - .4 - pt, .08), loc=(sx * (w / 2 - pt / 2), cy + .1 - pt / 2, top + .6), bevel=.01,
                 seg=1)
    trim.box((w, pt + .08, .08), loc=(0, y1 - pt / 2, top + .6), bevel=.01, seg=1)
    # False front with a raised centre, cornices and the sign board.
    walls.box((w, .3, 1.4), loc=(0, y0 + .15, top + .8), bevel=.03)
    walls.box((3.4, .28, .55), loc=(0, y0 + .15, top + 1.7), bevel=.03)
    trim.box((w + .12, .44, .14), loc=(0, y0 + .15, top + 1.5), bevel=.02, seg=1)
    trim.box((3.52, .44, .14), loc=(0, y0 + .15, top + 2.0), bevel=.02, seg=1)
    fbox(a.part('Sign', 'Hazard'), '-y', (0, y0, top + .82), (5.2, .1, .95), out=.03, bevel=.02)
    letters(a, rng, '-y', (0, y0, top + .82), 4.6, out=.09)
    a.part('Roof_deck', 'RoofSlate').box((w - 2 * pt + .04, d - .5, .1), loc=(0, cy + .1, top + .12), bevel=0)
    # Shop front: two big windows over wooden bulkheads, glazed door between them.
    for x in (-2.45, 2.45):
        window(a, rng, '-y', (x, y0, 1.85), w=2.6, h=2.0, frame='Armor', mullion=1, sill=None, lit=.45)
        fbox(a.part('Bulkhead', 'Wood'), '-y', (x, y0, .5), (2.74, .12, .6), out=.05, bevel=.02)
    door(a, '-y', (0, y0, base), w=1.2, h=2.45, mat='Glass', frame='Armor', lamp=False)
    # Striped awning on steel arms.
    sw, n = .7, 12
    y_front, z_wall, z_front = y0 - .95, 3.3, 2.75
    L = math.hypot(.95, z_wall - z_front)
    ang = math.atan2(z_wall - z_front, .95)
    zm = (z_wall + z_front) / 2
    cloth = a.part('Awning', 'PlasterWhite')
    cloth.box((n * sw + .02, L + .06, .05), loc=(0, y0 - .475, zm), rot=(ang, 0, 0), bevel=0)
    cloth.box((n * sw, .03, .3), loc=(0, y_front - .03, z_front - .12), bevel=0)
    # Red stripes lie 1.2 cm proud of the white cloth, so no two stripes share a face.
    stripe = a.part('Awning_stripes', 'WoodRed')
    ny, nz = -math.sin(ang) * .012, math.cos(ang) * .012
    for i in range(0, n, 2):
        x = -n * sw / 2 + (i + .5) * sw
        stripe.box((sw, L + .04, .05), loc=(x, y0 - .475 + ny, zm + nz), rot=(ang, 0, 0), bevel=0)
        stripe.box((sw - .02, .03, .28), loc=(x, y_front - .042, z_front - .12), bevel=0)
    for sx in (-1, 1):
        a.part('Awning_arms', 'Steel').limb((sx * 4.1, y0, 2.35), (sx * 4.1, y_front + .05, z_front), .04, .04,
                                            bevel=0)
    # Produce crates by the left window.
    crate = a.part('Crates', 'Wood')
    for i, (x, z, top_mat) in enumerate(((-3.55, .2, 'FoliageLight'), (-2.8, .2, 'Hazard'), (-3.2, .6, 'BarrelRed'))):
        crate.box((.66, .5, .4), loc=(x, y0 - .45, z), bevel=.02, seg=1)
        a.part('Produce', top_mat).box((.56, .4, .06), loc=(x, y0 - .45, z + .2), bevel=.02, seg=1)
    # Sides, back door and a rooftop air conditioner.
    for face, x in (('-x', -w / 2), ('+x', w / 2)):
        window(a, rng, face, (x, cy + .6, 2.0), w=1.0, h=1.2, frame='PlasterWhite')
    door(a, '+y', (-2.5, y1, base), w=.95, h=2.1, mat='Steel', frame='Concrete')
    window(a, rng, '+y', (2.0, y1, 2.0), w=1.0, h=1.0, frame='PlasterWhite')
    a.part('Roof_AC', 'MetalSheet').box((1.4, 1.0, .8), loc=(2.2, cy + 1.3, top + .55), bevel=.04)
    a.part('AC_fan', 'Rubber').cyl(.32, .04, loc=(2.45, cy + 1.3, top + .96), seg=12, bevel=0)
    a.part('Vent', 'Steel').cyl(.12, .7, loc=(-2.5, cy + 1.6, top + .5), seg=8, bevel=0)


# ----------------------------------------------------------------------------- landmarks
def church(a):
    """Village church (10 x 18 m): slate nave with buttresses and lancet windows, stone bell
    tower with a copper spire at the street end, rose window, apse at the back."""
    rng = random.Random(64)
    w, base, H, k = 9.0, .4, 4.6, 1.0
    y0, y1 = -5.4, 6.2
    d, cy = y1 - y0, (y0 + y1) / 2
    top, hw = base + H, w / 2
    white = a.part('Walls', 'PlasterWhite')
    stone = a.part('Stone', 'Concrete')
    stone.box((w + .2, d + .2, base), loc=(0, cy, base / 2), bevel=.04)
    gabled_walls(white, w, d, H + .02, hw * k, 'y', (0, cy), base)
    gable_roof(a, 'RoofSlate', w, d, top, k, 'y', centre=(0, cy), eave=.35, verge=.25, t=.2)
    for sx in (-1, 1):
        for i in range(5):
            y = y0 + .45 + i * 2.65
            stone.box((.5, .6, base + 3.4), loc=(sx * (hw + .2), y, (base + 3.4) / 2), taper=(.5, 1),
                      shift=(-sx * .125, 0), bevel=.03)
        face = '-x' if sx < 0 else '+x'
        for i in range(4):
            lancet(a, rng, face, (sx * hw, y0 + 1.775 + i * 2.65, base + 2.0), .8, 2.2)
    for x in (-3.2, 3.2):
        lancet(a, rng, '-y', (x, y0, base + 2.0), .6, 1.8)
    # Apse.
    white.cyl(2.7, H - .4, loc=(0, y1, base + (H - .4) / 2), seg=14, bevel=.03)
    stone.cyl(2.8, base - .02, loc=(0, y1, (base - .02) / 2), seg=14, bevel=.03)
    a.part('Roof', 'RoofSlate').cyl(3.0, 2.4, loc=(0, y1, base + H - .4 + 1.1), r2=.05, seg=14, bevel=0)
    for th in (-.9, 0, .9):
        n = (math.sin(th), math.cos(th))
        for r, size, part in ((2.72, (.72, .1, 1.9), a.part('Frames', 'Concrete')),
                              (2.77, (.52, .06, 1.7), pane(a, rng, .2))):
            part.box(size, loc=(n[0] * r, y1 + n[1] * r, base + 2.1), rot=(0, 0, -th), bevel=0)
    # Tower: stone shaft, narrower belfry stage, pinnacles, spire and cross.
    tw, ty0 = 3.8, -9.0
    tcy = ty0 + tw / 2
    stone.box((tw + .2, tw + .2, .5), loc=(0, tcy, .25), bevel=.04)
    shaft = 8.4
    stone.box((tw, tw, shaft - .4), loc=(0, tcy, (shaft + .4) / 2), bevel=.05)
    stone.box((tw + .24, tw + .24, .22), loc=(0, tcy, 5.4), bevel=.03, seg=1)
    stone.box((tw + .3, tw + .3, .26), loc=(0, tcy, shaft), bevel=.03, seg=1)
    bw, belfry = 3.5, 3.2
    stone.box((bw, bw, belfry), loc=(0, tcy, shaft + belfry / 2), bevel=.05)
    stone.box((bw + .36, bw + .36, .3), loc=(0, tcy, shaft + belfry), bevel=.03, seg=1)
    hb = bw / 2
    for face, p in (('-y', (0, tcy - hb)), ('+y', (0, tcy + hb)), ('-x', (-hb, tcy)), ('+x', (hb, tcy))):
        for s in (-1, 1):
            lancet(a, rng, face, slide(face, (p[0], p[1], shaft + 1.45), s * .7), .6, 1.4, glass='Charred')
    oculus(a, rng, '-y', (0, ty0, 6.9), .75)
    door(a, '-y', (0, ty0, .5), w=1.3, h=2.5, mat='Wood', frame='Concrete', lamp=False)
    head(stone, '-y', (0, ty0, .5 + 2.68), .9, .75, .14, .04)
    spire_base, spire_h = shaft + belfry + .15, 3.7
    a.part('Spire', 'RoofGreen').cyl(1.55, spire_h, loc=(0, tcy, spire_base + spire_h / 2), r2=.04, seg=8,
                                     rot=(0, 0, math.pi / 8), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            stone.cyl(.24, 1.1, loc=(sx * 1.6, tcy + sy * 1.6, spire_base + .55), r2=0, seg=4, rot=(0, 0, math.pi / 4),
                      bevel=0)
    gold = a.part('Cross', 'Hazard')
    zt = spire_base + spire_h
    gold.box((.09, .09, .62), loc=(0, tcy, zt + .27), bevel=.01, seg=1)
    gold.box((.4, .07, .09), loc=(0, tcy, zt + .42), bevel=.01, seg=1)


def barn(a):
    """Red plank barn (12 x 9 m): gambrel roof, sliding double doors, hay loft, ridge cupola."""
    rng = random.Random(72)
    w, d, base, H = 11.2, 8.4, .3, 3.4
    top, hw, hd = base + H, w / 2, d / 2
    kx, kdz, rdz = 3.8, 2.4, 3.6  # knee half-width, knee and ridge heights above the eaves
    red = a.part('Walls', 'WoodRed')
    white = a.part('Trim', 'PlasterWhite')
    a.part('Footing', 'Concrete').box((w + .12, d + .12, base), loc=(0, 0, base / 2), bevel=.03)
    red.prism([(-hw, 0), (hw, 0), (hw, H + .02), (kx, H + kdz + .02), (0, H + rdz + .02), (-kx, H + kdz + .02),
               (-hw, H + .02)], d, loc=(0, 0, base), axis='Y', bevel=.04)
    k1 = kdz / (hw - kx)
    roof_shell(a.part('Roof', 'MetalSheet'), [(-hw - .4, top - .4 * k1), (-kx, top + kdz), (0, top + rdz)], d + .6, 'y',
               t=.16)

    def wall_top(x):  # gable wall height above the plinth at x
        ax = abs(x)
        if ax >= kx:
            return H + (hw - ax) * k1
        return H + kdz + (kx - ax) * (rdz - kdz) / kx

    battens = a.part('Battens', 'WoodRed')

    def batten(face, p, z0, z1):
        if z1 - z0 > .15:
            fbox(battens, face, (p[0], p[1], (z0 + z1) / 2), (.08, .05, z1 - z0), out=.015)

    for face, y in (('-y', -hd), ('+y', hd)):
        for i in range(14):
            x = -5.2 + i * .8
            zt = base + wall_top(x) - .12
            if face == '-y' and abs(x) < 2.1:
                if abs(x) < 1.0:
                    batten(face, (x, y), base + 3.75, base + 4.25)
                    batten(face, (x, y), base + 5.85, zt)
                else:
                    batten(face, (x, y), base + 3.75, zt)
            else:
                batten(face, (x, y), base + .05, zt)
    for face, x in (('-x', -hw), ('+x', hw)):
        for i in range(11):
            y = -4.0 + i * .8
            if abs(abs(y) - 2.2) < .7:
                batten(face, (x, y), base + .05, base + 1.2)
                batten(face, (x, y), base + 2.45, top - .08)
            else:
                batten(face, (x, y), base + .05, top - .08)
    for sx in (-1, 1):
        for sy in (-1, 1):
            white.box((.22, .22, H), loc=(sx * (hw - .08), sy * (hd - .08), base + H / 2), bevel=.02, seg=1)
    # Sliding double doors with white frames and cross braces on a steel track.
    zc = base + 1.6
    for s in (-1, 1):
        x = s * .9
        fbox(red, '-y', (x, -hd, zc), (1.76, .06, 3.2), out=.03, bevel=.02)
        for dz in (-1.53, 1.53):
            fbox(white, '-y', (x, -hd, zc + dz), (1.76, .06, .14), out=.07)
        for dx in (-.81, .81):
            fbox(white, '-y', (x + dx, -hd, zc), (.14, .06, 2.92), out=.07)
        for a0, a1, dy in (((-.74, -1.46), (.74, 1.46), 0), ((-.74, 1.46), (.74, -1.46), .012)):
            white.limb((x + a0[0], -hd - .1 - dy, zc + a0[1]), (x + a1[0], -hd - .1 - dy, zc + a1[1]), .14, .05,
                       bevel=0)
    fbox(white, '-y', (0, -hd, base + 3.35), (4.0, .1, .2), out=.05)
    fbox(a.part('Track', 'Armor'), '-y', (0, -hd, base + 3.62), (4.4, .1, .1), out=.09)
    # Hay loft: dark opening with hay, open loft door, hoist beam with a rope.
    lz = base + 5.05
    fbox(a.part('Loft', 'Charred'), '-y', (0, -hd, lz), (1.7, .06, 1.4), out=.02)
    for dz in (-.76, .76):
        fbox(white, '-y', (0, -hd, lz + dz), (1.94, .07, .14), out=.07)
    for dx in (-.9, .9):
        fbox(white, '-y', (dx, -hd, lz), (.14, .07, 1.38), out=.07)
    hay = a.part('Hay', 'Sandbag')
    for x, z, turn in ((-.38, lz - .5, .06), (.36, lz - .5, -.08), (-.02, lz - .1, .1)):
        hay.box((.68, .5, .38), loc=(x, -hd - .05, z), rot=(0, 0, turn), bevel=.05, seg=1)
    fbox(red, '-y', (-1.45, -hd, lz), (.8, .06, 1.4), out=.06)
    white.limb((-1.8, -hd - .1, lz - .6), (-1.1, -hd - .1, lz + .6), .12, .04, bevel=0)
    beam_z = base + wall_top(0) - .35
    a.part('Hoist', 'Wood').box((.18, 1.05, .2), loc=(0, -hd - .35, beam_z), bevel=.02, seg=1)
    a.part('Pulley', 'Steel').cyl(.1, .06, loc=(0, -hd - .75, beam_z - .15), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Rope', 'Canvas').tube([(0, -hd - .75, beam_z - .2), (0, -hd - .75, lz + .9)], .02, seg=4)
    for face, x in (('-x', -hw), ('+x', hw)):
        for y in (-2.2, 2.2):
            window(a, rng, face, (x, y, base + 1.85), w=.9, h=.9, frame='PlasterWhite', sill=None, lit=.1)
    door(a, '+y', (2.6, hd, base), w=1.1, h=2.2, mat='WoodRed', frame='PlasterWhite', step=None, lamp=True)
    # Ridge cupola with louvres, a pyramid cap and a weather vane.
    zr = top + rdz
    red.box((1.1, 1.1, 1.0), loc=(0, 0, zr + .4), bevel=.03)
    for face, p in (('-y', (0, -.55)), ('+y', (0, .55)), ('-x', (-.55, 0)), ('+x', (.55, 0))):
        fbox(a.part('Loft', 'Charred'), face, (p[0], p[1], zr + .5), (.62, .04, .5), out=.015)
        for j in range(3):
            fbox(white, face, (p[0], p[1], zr + .32 + j * .17), (.7, .05, .05), out=.05)
    a.part('Cupola_roof', 'MetalSheet').cyl(1.0, .75, loc=(0, 0, zr + .9 + .37), r2=.03, seg=4, rot=(0, 0, math.pi / 4),
                                            bevel=0)
    vane = a.part('Vane', 'Armor')
    vane.box((.03, .03, .8), loc=(0, 0, zr + 1.95), bevel=0)
    vane.box((.7, .03, .12), loc=(.05, .03, zr + 2.2), bevel=0)
    vane.box((.34, .03, .03), loc=(0, 0, zr + 2.0), rot=(0, 0, R90 * .5), bevel=0)


def silo(a):
    """Grain silo (4 x 4 m, 10.6 m): ribbed sheet-metal drum with a domed top and a caged ladder."""
    a.part('Base', 'Concrete').cyl(1.95, .4, loc=(0, 0, .2), seg=18, bevel=.04)
    prof = [(1.75, .3)]
    for z in (1.5, 2.8, 4.1, 5.4, 6.7, 8.0):
        prof += [(1.75, z - .07), (1.81, z), (1.75, z + .07)]
    prof += [(1.75, 8.6), (1.68, 9.0), (1.45, 9.45), (1.05, 9.85), (.52, 10.1), (.32, 10.15)]
    a.part('Body', 'MetalSheet').lathe(prof, seg=18)
    steel = a.part('Steel', 'Steel')
    steel.cyl(.38, .35, loc=(0, 0, 10.3), seg=10, bevel=.02, bseg=1)
    steel.cyl(.48, .28, loc=(0, 0, 10.6), r2=.04, seg=10, bevel=0)
    # Ladder up the -Y side with a safety cage, carried on over the shoulder of the dome.
    ly = -1.96
    for sx in (-.22, .22):
        steel.box((.05, .05, 8.3), loc=(sx, ly, .4 + 4.15), bevel=0)
        steel.limb((sx, ly, 8.5), (sx, -1.3, 9.62), .03, .03, bevel=0)
    for i in range(20):
        steel.box((.44, .035, .035), loc=(0, ly, .75 + i * .4), bevel=0)
    for z in (2.0, 4.2, 6.4):
        for sx in (-.22, .22):
            steel.box((.04, .2, .04), loc=(sx, ly + .12, z), bevel=0)
    cage_y = ly - .02
    for z in (2.6, 3.7, 4.8, 5.9, 7.0, 8.1):
        pts = [(.3 * math.cos(t), cage_y - .3 * math.sin(t), z) for t in (j * math.pi / 4 for j in range(5))]
        steel.tube(pts, .02, seg=4)
    for t in (math.pi / 4, R90, 3 * math.pi / 4):
        steel.box((.03, .03, 5.6), loc=(.3 * math.cos(t), cage_y - .3 * math.sin(t), 5.35), bevel=0)
    # Discharge hopper and chute on the +X side.
    hopper = a.part('Hopper', 'Steel')
    hopper.prism([(-.35, 0), (.35, 0), (.18, -.45), (-.18, -.45)], .6, loc=(1.95, 0, 1.25), axis='X', bevel=0)
    hopper.limb((1.6, 0, 1.9), (1.95, 0, 1.3), .2, .2, bevel=0)
    hopper.cyl(.08, .5, loc=(1.95, 0, .6), seg=8, bevel=0)


def warehouse(a):
    """Industrial shed (16 x 12 m): sheet-metal walls on a concrete base, arched green roof with
    skylights and vents, two roller doors on a full-width loading dock."""
    rng = random.Random(91)
    w, y0, y1, H = 15.4, -4.6, 5.6, 5.0
    d, cy = y1 - y0, (y0 + y1) / 2
    hd, rise = d / 2, 2.3
    R = (hd * hd + rise * rise) / (2 * rise)
    zc = H + rise - R
    tw = math.asin(hd / R)
    arc = [(-R * math.sin(tw * (1 - i / 6)), zc + R * math.cos(tw * (1 - i / 6))) for i in range(7)]
    eu = -(hd + .45)
    prof = [(eu, zc + math.sqrt(R * R - eu * eu))] + arc
    sheet = a.part('Walls', 'MetalSheet')
    wall = [(-hd, 0), (hd, 0)] + [(-u, z + .02) for u, z in arc] + [(u, z + .02) for u, z in reversed(arc[:-1])]
    sheet.prism(wall, w, loc=(0, cy, 0), axis='X', bevel=.05)
    a.part('Base', 'Concrete').box((w + .04, d + .04, 1.2), loc=(0, cy, .6), bevel=.03)
    t = .14
    outer = roof_shell(a.part('Roof', 'RoofGreen'), prof, w + .5, 'x', t=t, centre=(0, cy))
    steel = a.part('Steel', 'Steel')
    # Columns.
    for x in (-7.7, -6.6, 6.6, 7.7):
        fbox(steel, '-y', (x, y0, 3.1), (.28, .16, H - 1.2), out=.07)
    for x in (-7.7, -3.85, 0, 3.85, 7.7):
        fbox(steel, '+y', (x, y1, 3.1), (.28, .16, H - 1.2), out=.07)
    for face, x in (('-x', -w / 2), ('+x', w / 2)):
        for yy in (-hd, hd):
            fbox(steel, face, (x, cy + yy * .985, 3.095), (.28, .16, H - 1.21), out=.07)
    # Clerestory windows on the back wall.
    for x in (-5.8, -1.9, 1.9, 5.8):
        window(a, rng, '+y', (x, y1, 4.1), w=2.6, h=.7, frame='Steel', mullion=1, sill=None, lit=.25)
    # Roller doors on the dock.
    for sx in (-1, 1):
        x = sx * 3.9
        for dx in (-1.9, 1.9):
            fbox(a.part('Jambs', 'Hazard'), '-y', (x + dx, y0, 2.85), (.2, .14, 3.4), out=.06)
        fbox(steel, '-y', (x, y0, 4.6), (4.06, .14, .2), out=.07)
        fbox(a.part('Roller_door', 'MetalSheet'), '-y', (x, y0, 2.85), (3.6, .06, 3.3), out=.03)
        for j in range(8):
            fbox(a.part('Slats', 'Armor'), '-y', (x, y0, 1.4 + j * .4), (3.6, .03, .05), out=.07)
        fbox(a.part('Housing', 'Armor'), '-y', (x, y0, 4.87), (3.9, .4, .36), out=.2, bevel=.03)
    door(a, '-y', (0, y0, 1.17), w=.95, h=2.1, mat='Steel', frame='Steel', step=None)
    fbox(a.part('Sign', 'PlasterWhite'), '-y', (0, y0, 3.95), (3.2, .08, .85), out=.05, bevel=.02)
    letters(a, rng, '-y', (0, y0, 3.95), 2.8, h=.4, out=.1)
    # Loading dock with a hazard edge, bumpers, levellers, steps and some freight.
    dock = a.part('Dock', 'Concrete')
    dh = 1.17
    dock.box((w - 1.1, 1.45, dh), loc=(.35, y0 - .7, dh / 2), bevel=.04)
    a.part('Dock_edge', 'Hazard').box((w - 1.1, .08, .1), loc=(.35, y0 - 1.44, dh - .08), bevel=.01, seg=1)
    for i in range(4):
        dock.box((.18, 1.4, (i + 1) * dh / 4), loc=(.35 - (w - 1.1) / 2 - .18 * (3.5 - i), y0 - .7, (i + 1) * dh / 8),
                 bevel=.02, seg=1)
    for sx in (-1, 1):
        for dx in (-1.2, 1.2):
            a.part('Bumpers', 'Rubber').box((.26, .14, .42), loc=(sx * 3.9 + dx, y0 - 1.48, .78), bevel=.03, seg=1)
        steel.box((2.6, 1.0, .03), loc=(sx * 3.9, y0 - .55, dh + .015), bevel=0)
    crate = a.part('Crates', 'Crate')
    for x, z, turn in ((-6.4, dh + .35, .1), (-5.7, dh + .35, -.05), (-6.05, dh + 1.05, .3)):
        crate.box((.7, .7, .7), loc=(x, y0 - .75, z), rot=(0, 0, turn), bevel=.03, seg=1)
    for x in (6.2, 6.85):
        a.part('Barrels', 'BarrelRed').cyl(.3, .9, loc=(x, y0 - .7, dh + .45), seg=10, bevel=.02, bseg=1)
    a.part('Pallet', 'Wood').box((1.1, 1.0, .14), loc=(-1.6, y0 - .75, dh + .07), bevel=.01, seg=1)
    # Gable ends: louvres, office windows, a side door under a canopy.
    for face, x in (('-x', -w / 2), ('+x', w / 2)):
        fbox(steel, face, (x, cy, 6.1), (1.9, .08, 1.0), out=.04)
        s = 1 if face == '+x' else -1
        steel.grille(1.6, .8, loc=(x + s * .1, cy, 6.1), rot=(0, 0, R90 if s > 0 else -R90), slats=5)
        for yy in (-2.4, 2.4):
            window(a, rng, face, (x, cy + yy, 2.3), w=1.4, h=1.0, frame='Steel', mullion=1, lit=.3)
    door(a, '+x', (w / 2, cy, 0), w=1.0, h=2.2, mat='Steel', frame='Steel', step=None)
    fbox(a.part('Canopy', 'MetalSheet'), '+x', (w / 2, cy, 2.62), (1.6, .9, .1), out=.45, bevel=.02)
    # Roof ribs, skylights and turbine vents.
    ribs = a.part('Roof_ribs', 'Steel')
    full = outer
    for x in (-3.85, 0, 3.85):
        ribs.tube([(x, cy + u, z + .03) for u, z in full], .05, seg=4)
    glass = a.part('Skylights', 'Glass')
    (u0, z0), (u1, z1) = arc[3], arc[4]
    ang = math.atan2(z1 - z0, u1 - u0)
    L = math.hypot(u1 - u0, z1 - z0)
    nu, nz = -math.sin(ang), math.cos(ang)
    mu, mz = (u0 + u1) / 2 + nu * (t + .04), (z0 + z1) / 2 + nz * (t + .04)
    for x in (-5.8, -1.9, 1.9, 5.8):
        for side in (-1, 1):
            glass.box((2.4, L * .8, .05), loc=(x, cy + (mu if side < 0 else -mu), mz), rot=(-side * ang, 0, 0), bevel=0)
    for x in (-5.8, -1.9, 1.9, 5.8):
        steel.cyl(.26, .4, loc=(x, cy, H + rise + t + .15), seg=10, bevel=0)
        steel.sphere(.3, loc=(x, cy, H + rise + t + .35), seg=10, rings=6, cut=0)


def garage(a):
    """Brick garage (5 x 5 m) with a mono-pitch sheet roof and a green roller door."""
    rng = random.Random(15)
    w, d, cy, base = 4.6, 4.4, .1, .15
    hf, hb = 2.95, 2.45
    y0, y1 = cy - d / 2, cy + d / 2
    a.part('Slab', 'Concrete').box((w + .12, d + .12, base), loc=(0, cy, base / 2), bevel=.03)
    a.part('Walls', 'Brick').prism([(-d / 2, 0), (d / 2, 0), (d / 2, hb + .02), (-d / 2, hf + .02)], w,
                                   loc=(0, cy, base), axis='X', bevel=.04)
    # Mono-pitch roof falling to the back, with standing-seam ribs.
    of, ob, t = .35, .3, .12
    ang = math.atan2(hf - hb, d)
    L = (d + of + ob) / math.cos(ang)
    ym = cy + (ob - of) / 2
    zm = base + (hf + hb) / 2 + (of - ob) / 2 * math.tan(ang) + t / 2 / math.cos(ang)
    a.part('Roof', 'MetalSheet').box((w + .4, L, t), loc=(0, ym, zm), rot=(-ang, 0, 0), bevel=.02, seg=1)
    ribs = a.part('Roof_ribs', 'Steel')
    for i in range(9):
        ribs.box((.05, L, .05), loc=(-2.2 + i * .55, ym - math.sin(ang) * .08, zm + math.cos(ang) * .08),
                 rot=(-ang, 0, 0), bevel=0)
    # Roller door in a concrete frame.
    x, dw, dh = -.35, 2.7, 2.25
    conc = a.part('Frame', 'Concrete')
    fbox(conc, '-y', (x, y0, base + dh + .14), (dw + .44, .16, .28), out=.05, bevel=.02)
    for s in (-1, 1):
        fbox(conc, '-y', (x + s * (dw / 2 + .11), y0, base + dh / 2), (.22, .14, dh), out=.04, bevel=.02)
    fbox(a.part('Roller_door', 'RoofGreen'), '-y', (x, y0, base + dh / 2), (dw, .06, dh), out=.02)
    for j in range(6):
        fbox(a.part('Slats', 'Armor'), '-y', (x, y0, base + .3 + j * .36), (dw, .03, .04), out=.06)
    fbox(a.part('Handle', 'Steel'), '-y', (x, y0, base + .35), (.4, .05, .06), out=.08)
    fbox(a.part('Door_lamp', 'Lamp'), '-y', (1.55, y0, base + 2.35), (.16, .12, .18), out=.07, bevel=.03)
    window(a, rng, '+x', (w / 2, cy + .8, base + 1.6), w=.9, h=.6, frame='Wood', mullion=1)
    door(a, '-x', (-w / 2, cy + .9, base), w=.85, h=2.0, mat='Wood', frame='Concrete', step=None, lamp=False)
    # Gutter and downpipe at the back eave.
    zg = base + hb - ob * math.tan(ang) - .05
    steel = a.part('Gutter', 'Steel')
    steel.box((w + .3, .14, .12), loc=(0, y1 + ob - .02, zg), bevel=.02, seg=1)
    steel.cyl(.05, zg, loc=(w / 2 + .05, y1 + ob - .02, zg / 2), seg=6, bevel=0)


def water_tower(a):
    """Water tower (4 x 4 m, 11 m): white tank with a green cone roof on four braced steel legs."""
    steel = a.part('Frame', 'Steel')
    conc = a.part('Footings', 'Concrete')
    lb, lt, z0, z1 = 1.6, 1.05, .4, 7.25

    def leg(z):
        return lb + (lt - lb) * (z - z0) / (z1 - z0)

    for sx in (-1, 1):
        for sy in (-1, 1):
            conc.box((.55, .55, .45), loc=(sx * lb, sy * lb, .2), bevel=.04)
            steel.limb((sx * lb, sy * lb, z0), (sx * lt, sy * lt, z1), .16, .16, bevel=.02)
    levels = (z0 + .2, 2.7, 4.95, z1 - .2)
    for s in (-1, 1):
        for i, z in enumerate(levels[1:-1]):
            p = leg(z)
            steel.limb((-p, s * p, z), (p, s * p, z), .07, .07, bevel=0)
            steel.limb((s * p, -p, z + .012), (s * p, p, z + .012), .07, .07, bevel=0)
        for za, zb in zip(levels, levels[1:]):
            pa, pb = leg(za), leg(zb)
            for q in (-1, 1):
                o = .012 if q > 0 else 0.0
                steel.limb((-q * pa, s * (pa + o), za), (q * pb, s * (pb + o), zb), .06, .06, bevel=0)
                steel.limb((s * (pa + o), -q * pa, za), (s * (pb + o), q * pb, zb), .06, .06, bevel=0)
    steel.cyl(.2, 6.2, loc=(0, 0, .4 + 3.1), seg=8, bevel=0)
    a.part('Tank', 'Fuel').lathe([(.22, 6.4), (1.0, 6.72), (1.55, 7.05), (1.75, 7.35), (1.75, 10.0)], seg=16)
    a.part('Band', 'RoofGreen').cyl(1.77, .25, loc=(0, 0, 9.55), seg=16, bevel=0)
    a.part('Roof', 'RoofGreen').lathe([(1.92, 9.97), (1.92, 10.07), (.05, 11.05)], seg=16)
    steel.sphere(.12, loc=(0, 0, 11.12), seg=8, rings=5)
    # Catwalk with a railing, and ladders up the leg frame and the tank.
    walk = a.part('Catwalk', 'Steel')
    walk.lathe([(1.6, 7.28), (1.98, 7.28), (1.98, 7.36), (1.6, 7.36)], seg=16)
    for i in range(12):
        t = i * math.tau / 12 + math.pi / 12
        walk.box((.04, .04, .9), loc=(1.94 * math.cos(t), 1.94 * math.sin(t), 7.36 + .45), bevel=0)
    walk.tube([(1.94 * math.cos(t), 1.94 * math.sin(t), 8.26) for t in (j * math.tau / 16 for j in range(17))], .025,
              seg=4, caps=False)
    for x0, y, za, zb, n in ((0, -1.96, 0, 7.28, 17), (0, -1.8, 7.36, 9.95, 6)):
        for sx in (-.2, .2):
            steel.box((.045, .045, zb - za), loc=(x0 + sx, y, (za + zb) / 2), bevel=0)
        for i in range(n):
            steel.box((.4, .03, .03), loc=(x0, y, za + .35 + i * (zb - za - .5) / max(1, n - 1)), bevel=0)


def ruin(a):
    """Shell of a bombed house (8 x 8 m): broken brick walls with plaster fallen away, charred
    interior, a surviving chimney stack, a hanging floor slab, burnt beams and rubble heaps."""
    rng = random.Random(101)
    base, th, half = .25, .3, 3.8
    a.part('Plinth', 'Concrete').box((7.9, 7.9, base), loc=(0, 0, base / 2), bevel=.04)
    a.part('Scorch', 'Charred').box((6.4, 6.2, .02), loc=(.1, .2, base + .01), bevel=0)
    core = a.part('Walls', 'Brick', flat=True)
    skin = a.part('Plaster', 'Plaster', flat=True)
    soot = a.part('Soot', 'Charred', flat=True)
    walls = (
        # face, centre offset, length, height controls, openings (u0, u1, sill, lintel)
        ('-y', -half + th / 2, 2 * half, [(-3.8, 5.7), (-2.4, 5.1), (-1.2, 3.4), (.4, 2.2), (2.0, 1.5), (3.8, .9)],
         [(-.5, .55, 0, 2.2), (-2.9, -1.9, 1.0, 2.3), (-3.1, -2.3, 3.9, 5.0), (2.0, 3.0, 1.0, 2.3)]),
        ('-x', -half + th / 2, 2 * (half - th), [(-3.5, 5.6), (-1.2, 4.6), (.8, 3.0), (3.5, 1.9)],
         [(-2.5, -1.5, 1.0, 2.3), (1.0, 2.0, 1.0, 2.3), (-2.5, -1.6, 3.9, 5.0)]),
        ('+y', half - th / 2, 2 * half, [(-3.8, 1.9), (-1.5, 1.2), (0, .6), (1.8, 1.5), (3.8, 2.5)],
         [(-2.6, -1.6, 1.0, 2.3), (1.3, 2.3, 1.0, 2.3)]),
        ('+x', half - th / 2, 2 * (half - th), [(-3.5, 1.0), (-1.2, .5), (1.0, 1.9), (3.5, 2.7)],
         [(-.5, .5, 1.0, 2.3)]),
    )

    def profile(controls, u):
        for (ua, ha), (ub, hb) in zip(controls, controls[1:]):
            if ua <= u <= ub:
                return ha + (hb - ha) * (u - ua) / (ub - ua)
        return controls[0][1] if u < controls[0][0] else controls[-1][1]

    def wobble(L, amp):
        """Piecewise-linear noise along a wall, sharp at the sample points (the broken edge)."""
        n = max(4, int(L / .32))
        vals = [rng.uniform(-amp, amp) for _ in range(n + 1)]

        def f(u):
            t = min(float(n), max(0.0, (u + L / 2) / L * n))
            i = min(n - 1, int(t))
            return vals[i] + (vals[i + 1] - vals[i]) * (t - i)
        return f

    def pieces(L, height, openings, grow=0.0):
        """Polygons (u, z) of a broken wall. The wall is cut into columns at the opening edges;
        each column keeps the solid spans between its openings (so windows can stack) and its
        top span ends in the broken edge. Spans the break has already eaten are dropped."""
        n = max(4, int(L / .32))
        us = [-L / 2 + L * i / n for i in range(n + 1)]
        top = lambda u: max(.15, height(u))  # noqa: E731
        ops = [(u0 - grow, u1 + grow, zb - grow, zt + grow) for u0, u1, zb, zt in openings]
        cuts = sorted({-L / 2, L / 2} | {max(-L / 2, min(L / 2, c)) for o in ops for c in o[:2]})
        out = []
        for ua, ub in zip(cuts, cuts[1:]):
            if ub - ua < .02:
                continue
            mid = (ua + ub) / 2
            spans, z = [], 0.0
            for zb, zt in sorted((zb, zt) for u0, u1, zb, zt in ops if u0 <= mid <= u1):
                if zb > z + .05:
                    spans.append((z, zb))
                z = max(z, zt)
            spans.append((z, math.inf))
            tops = [(ua, top(ua))] + [(u, top(u)) for u in us if ua < u < ub] + [(ub, top(ub))]
            for za, zb in spans:
                if max(h for _, h in tops) < za + .12 or (za > 0 and min(h for _, h in tops) < za + .1):
                    continue  # the break has eaten this span (a lintel with a gap becomes a notch)
                edge = [(u, min(zb, max(za + .03, h))) for u, h in tops]
                out.append([(ua, za), (ub, za)] + edge[::-1])
        return out

    def extrude(part, face, offset, polys, depth):
        nx, ny = NORMAL[face]
        for poly in polys:
            if nx == 0:
                part.prism(poly, depth, loc=(0, offset, base), axis='Y', bevel=0)
            else:
                part.prism(poly, depth, loc=(offset, 0, base), axis='X', bevel=0)

    for face, off, L, controls, openings in walls:
        noise, drop = wobble(L, .28), wobble(L, .25)
        jag = lambda u, c=controls, nz=noise: profile(c, u) + nz(u)  # noqa: E731
        extrude(core, face, off, pieces(L, jag, openings), th)
        # Plaster (outside) and soot (inside) skins stop 2 cm short of the corners.
        outer_top = lambda u, j=jag, dr=drop: j(u) - .5 - dr(u)  # noqa: E731
        sgn = 1 if face in ('+y', '+x') else -1
        extrude(skin, face, off + sgn * (th / 2 + .005), pieces(L - .04, outer_top, openings, grow=.12), .05)
        soot_top = lambda u, j=jag: min(j(u) - .15, 1.6 + .5 * math.sin(u * 2.3))  # noqa: E731
        extrude(soot, face, off - sgn * (th / 2 + .005), pieces(L - .04, soot_top, openings, grow=.05), .05)
    # Soot above the tall openings of the front and west walls.
    for face, p in (('-y', (-2.4, -half - .03, base + 2.8)), ('-x', (-half - .03, -2.0, base + 2.8))):
        fbox(soot, face, p, (1.2, .02, .8), out=.02)
    # Chimney stack left standing in the west wall.
    core.box((.7, .62, 6.3), loc=(-3.38, .9, base + 3.15), bevel=0)
    core.box((.5, .5, .5), loc=(-3.35, .95, base + 6.5), rot=(.12, -.1, .3), bevel=0)
    # Broken first floor hanging from the front-west corner.
    yaw, pitch, length = math.radians(45), math.radians(40), 3.4
    run = (math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), -math.sin(pitch))
    start = (-3.1, -3.1, base + 3.05)
    a.part('Slab', 'Concrete', flat=True).box((length, 1.9, .22),
                                               loc=tuple(s + r * length / 2 for s, r in zip(start, run)),
                                               rot=(0, pitch, yaw), bevel=0)
    beams = a.part('Beams', 'Charred')
    for p0, p1, s in (((-3.45, -.7, base + 4.3), (.7, 1.5, base + .4), .22),
                      ((-3.4, 3.0, base + 1.8), (-1.2, 1.5, base + .3), .2),
                      ((-.8, 2.4, base + .3), (1.9, .6, base + 1.1), .18),
                      ((2.2, -2.6, base + .2), (3.3, -.4, base + 1.2), .16)):
        beams.limb(p0, p1, s, s * .9, bevel=0)
    # Rubble heaps of brick, plaster and concrete, with roof tiles and planks.
    mats = [('Brick', core), ('Plaster', skin), ('Concrete', a.part('Chunks', 'Concrete', flat=True))]
    for hx, hy, hr, hh, n in ((.9, 1.2, 2.3, 1.4, 16), (-1.9, -1.3, 1.5, .9, 9), (.1, -3.0, .8, .35, 4)):
        for i in range(n):
            r = hr * math.sqrt(rng.random())
            t = rng.uniform(0, math.tau)
            x, y = hx + r * math.cos(t), hy + r * math.sin(t)
            h = hh * (1 - (r / hr) ** 2)
            s = rng.uniform(.3, .75) * (.6 + .4 * h / hh)
            _, part = mats[i % 3]
            part.ico((s, s * rng.uniform(.7, 1.1), s * rng.uniform(.45, .7)), loc=(x, y, base + h * .75), sub=1,
                     jitter=.3, seed=i * 1.37 + hx)
    tiles = a.part('Tiles', 'Roof')
    for i in range(10):
        tiles.box((rng.uniform(.5, 1.0), rng.uniform(.35, .6), .07),
                  loc=(rng.uniform(-2.8, 2.8), rng.uniform(-2.6, 2.8), base + rng.uniform(.2, .9)),
                  rot=(rng.uniform(-.5, .5), rng.uniform(-.5, .5), rng.uniform(0, math.tau)), bevel=0)
    planks = a.part('Planks', 'Wood')
    for i in range(4):
        x, y, t = rng.uniform(-2.5, 2.5), rng.uniform(-2.3, 2.5), rng.uniform(0, math.tau)
        planks.box((.14, rng.uniform(1.4, 2.4), .06), loc=(x, y, base + rng.uniform(.3, .8)),
                   rot=(rng.uniform(-.3, .3), rng.uniform(-.3, .3), t), bevel=0)


# ----------------------------------------------------------------------------- barriers
def fence(a):
    """Picket fence segment (4 x 0.3 m): white pickets on two rails between weathered posts."""
    rng = random.Random(4)
    wood = a.part('Posts', 'Wood')
    for x in (-1.925, 0, 1.925):
        wood.box((.15, .2, 1.25), loc=(x, .05, .625), bevel=.02, seg=1)
        wood.cyl(.13, .12, loc=(x, .05, 1.31), r2=0, seg=4, rot=(0, 0, math.pi / 4), bevel=0)
    for z in (.3, .85):
        wood.box((3.9, .07, .09), loc=(0, -.075, z), bevel=0)
    pick = a.part('Pickets', 'PlasterWhite')
    for i in range(16):
        x = -1.875 + i * .25
        if abs(x) < .09:
            continue
        tilt = rng.uniform(-.05, .05) if i != 11 else .22
        h = 1.05 + rng.uniform(-.03, .03) if i != 5 else .72
        prof = [(-.05, 0), (.05, 0), (.05, h - .1), (0, h), (-.05, h - .1)]
        pick.prism(prof, .045, loc=(x, -.1225 - (.012 if i == 11 else 0), .04), rot=(0, tilt, 0), axis='Y',
                   bevel=0)


def stone_wall(a):
    """Dry-stone field wall (6 x 0.8 m, 1 m tall): a tapered core faced with rough stones."""
    rng = random.Random(5)
    rock = a.part('Stones', 'Rock', flat=True)
    rock.prism([(-.28, 0), (.28, 0), (.17, .8), (-.17, .8)], 5.8, axis='X', bevel=0)
    for side in (-1, 1):
        for n, z, rxs, ry, rz in ((4, .26, (.66, .76), .19, .27), (5, .63, (.5, .6), .18, .23)):
            step = 5.8 / n
            for i in range(n):
                x = -2.9 + (i + .5) * step + rng.uniform(-.08, .08) + (side * .12 if n == 5 else 0)
                face_y = .28 - .11 * z / .8
                rock.ico((rng.uniform(*rxs), ry, rz), loc=(x, side * (face_y - .03), z), sub=1, jitter=.28,
                         seed=side * 3.1 + n * 1.7 + i * .9)
    for i in range(6):
        x = -2.45 + i * .98 + rng.uniform(-.06, .06)
        rock.ico((.5, .27, .15), loc=(x, 0, .86), rot=(0, 0, rng.uniform(-.15, .15)), sub=1, jitter=.22,
                 seed=20 + i * 1.3)


def hedge(a):
    """Hedgerow (6 x 1.2 m, 1.6 m tall) of lumpy, faceted foliage."""
    rng = random.Random(8)
    # A long low mass ties the clumps into one hedge; clumps and tufts break up its top.
    a.part('Leaves', 'FoliageDark', flat=True).ico((2.75, .5, .62), loc=(0, 0, .56), sub=2, jitter=.12, seed=1.1)
    for i in range(5):
        x = -2.24 + i * 1.12 + rng.uniform(-.08, .08)
        a.part('Leaves', 'Foliage' if i % 2 == 0 else 'FoliageDark', flat=True).ico(
            (.72, .56, .66), loc=(x, rng.uniform(-.04, .04), .86), sub=2, jitter=.2, seed=i * 2.1 + .5)
    for i, x in enumerate((-1.7, .55, 2.0)):
        a.part('Leaves', 'FoliageDark' if i % 2 else 'Foliage', flat=True).ico(
            (.4, .34, .3), loc=(x + rng.uniform(-.1, .1), rng.choice((-.16, .16)), 1.3), sub=1, jitter=.25,
            seed=i * 3.3 + 7)


# ----------------------------------------------------------------------------- civilian vehicles
# The brief gives the vehicle props as width x depth (4.2 x 1.8, 7 x 2.5): they stand parked along
# the street, length on X. They are modelled nose to -Y like the army's vehicles, then turned so
# the nose points to +X and the kerb side faces -Y.
def _turn(a, angle):
    """Rotate every part built so far about the vertical axis through the origin."""
    m = Matrix.Rotation(angle, 4, 'Z')
    for shape in a.shapes.values():
        bmesh.ops.transform(shape.bm, matrix=m, verts=list(shape.bm.verts))
        shape.bm.normal_update()


def _wheels(a, positions, r, width, hub=.52):
    for x, y in positions:
        a.part('Wheels', 'Rubber').cyl(r, width, loc=(x, y, r), rot=(0, R90, 0), seg=12, bevel=.03, bseg=1)
        s = 1 if x > 0 else -1
        a.part('Hubs', 'Steel').cyl(r * hub, .03, loc=(x + s * (width / 2 + .005), y, r), rot=(0, R90, 0), seg=8,
                                    bevel=0)


def _arches(a, x, ys, z, r):
    """Dark wheel-arch patches on a body side at |x|."""
    part = a.part('Arches', 'Rubber')
    for sx in (-1, 1):
        for y in ys:
            prof = [(y + r * math.cos(t), z + r * .8 * math.sin(t)) for t in (j * math.pi / 6 for j in range(7))]
            part.prism(prof, .03, loc=(sx * (x + .01), 0, 0), axis='X', bevel=0)


def car(a):
    """Small civilian hatchback (4.2 x 1.8 m). The body is one material (CarRed) so the runtime can
    recolour each car."""
    paint = a.part('Body', 'CarRed')
    W = 1.72
    paint.prism([(-2.1, .42), (2.08, .42), (2.1, .98), (1.96, 1.03), (-.95, 1.0), (-2.0, .86), (-2.12, .62)], W,
                axis='X', bevel=.07, seg=2)
    a.part('Glass', 'Glass').prism([(-.98, .96), (1.97, .96), (1.74, 1.43), (-.2, 1.46)], 1.5, axis='X', bevel=.02,
                                   seg=1)
    paint.prism([(-.3, 1.42), (1.78, 1.42), (1.72, 1.5), (-.2, 1.52)], 1.56, axis='X', bevel=.02, seg=1)
    for sx in (-1, 1):
        paint.limb((sx * .76, -.97, .98), (sx * .75, -.23, 1.45), .07, .07, bevel=0)
        paint.limb((sx * .72, 1.97, .98), (sx * .7, 1.74, 1.44), .12, .07, bevel=0)
        paint.box((.1, .1, .12), loc=(sx * .9, -.82, 1.06), bevel=.02, seg=1)
    paint.box((1.55, .12, .46), loc=(0, .5, 1.2), bevel=0)
    a.part('Underbody', 'Undercarriage').box((1.5, 3.4, .16), loc=(0, 0, .36), bevel=0)
    rubber = a.part('Bumpers', 'Rubber')
    for y in (-2.12, 2.11):
        rubber.box((1.76, .16, .2), loc=(0, y, .48), bevel=.04, seg=1)
    for sx in (-1, 1):
        a.part('Headlights', 'Lamp').box((.32, .05, .12), loc=(sx * .56, -2.13, .66), bevel=.02, seg=1)
        a.part('Taillights', 'BarrelRed').box((.26, .05, .18), loc=(sx * .62, 2.115, .84), bevel=.02, seg=1)
    a.part('Grille', 'Armor').box((.7, .04, .1), loc=(0, -2.13, .66), bevel=0)
    a.part('Plate', 'PlasterWhite').box((.46, .03, .12), loc=(0, 2.2, .52), bevel=0)
    _wheels(a, [(sx * .75, y) for sx in (-1, 1) for y in (-1.32, 1.32)], .31, .2)
    _arches(a, .86, (-1.32, 1.32), .42, .37)
    _turn(a, R90)


def truck(a):
    """Civilian box truck (7 x 2.5 m): cab-over cab (CarRed, recoloured at runtime) and a cargo box."""
    paint = a.part('Cab', 'CarRed')
    a.part('Chassis', 'Undercarriage').box((1.0, 6.6, .28), loc=(0, .05, .72), bevel=.02, seg=1)
    paint.prism([(-3.48, .82), (-1.55, .82), (-1.55, 2.95), (-3.18, 2.95), (-3.45, 2.3), (-3.5, 1.6)], 2.3, axis='X',
                bevel=.08, seg=2)
    glass = a.part('Glass', 'Glass')
    p0, p1 = (-3.45, 2.33), (-3.19, 2.9)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    n = (-math.sin(ang), math.cos(ang))
    glass.limb((0, p0[0] + n[0] * .03, p0[1] + n[1] * .03), (0, p1[0] + n[0] * .03, p1[1] + n[1] * .03), 2.0, .04,
               bevel=0)
    for face, x in (('-x', -1.15), ('+x', 1.15)):
        fbox(glass, face, (x, -2.6, 2.35), (1.0, .04, .72), out=.01)
    armor = a.part('Trim', 'Armor')
    armor.box((2.4, .22, .32), loc=(0, -3.56, .86), bevel=.04, seg=1)
    fbox(armor, '-y', (0, -3.49, 1.35), (1.4, .05, .45), out=.02)
    for sx in (-1, 1):
        a.part('Headlights', 'Lamp').box((.3, .05, .2), loc=(sx * .85, -3.51, 1.3), bevel=.02, seg=1)
        armor.limb((sx * 1.12, -3.15, 2.25), (sx * 1.32, -3.25, 2.25), .04, .04, bevel=0)
        armor.box((.06, .16, .36), loc=(sx * 1.33, -3.28, 2.12), bevel=.01, seg=1)
        armor.box((.14, .5, .08), loc=(sx * 1.18, -2.55, .95), bevel=0)
    for x in (-.5, 0, .5):
        a.part('Marker_lights', 'Alloy').box((.12, .06, .06), loc=(x, -3.1, 2.98), bevel=0)
    # Cargo box with ribs, rails and rear doors.
    box = a.part('Cargo', 'Fuel')
    box.box((2.44, 4.95, 2.6), loc=(0, .98, 2.2), bevel=.05, seg=1)
    steel = a.part('Ribs', 'Steel')
    for sx in (-1, 1):
        for y in (-.9, .1, 1.1, 2.1, 3.1):
            steel.box((.04, .08, 2.34), loc=(sx * 1.235, y, 2.25), bevel=0)
        steel.box((.06, 4.95, .08), loc=(sx * 1.22, .98, 3.47), bevel=0)
        armor.box((.04, 3.0, .1), loc=(sx * 1.18, .1, .78), bevel=0)
    armor.box((2.5, 5.0, .18), loc=(0, .98, .98), bevel=.02, seg=1)
    for x in (-.6, 0, .6):
        steel.box((.05, .04, 2.5), loc=(x, 3.47, 2.2), bevel=0)
    armor.box((2.2, .12, .15), loc=(0, 3.5, .62), bevel=.02, seg=1)
    for sx in (-1, 1):
        a.part('Taillights', 'BarrelRed').box((.25, .05, .15), loc=(sx * 1.0, 3.5, .8), bevel=.01, seg=1)
    a.part('Plate', 'PlasterWhite').box((.46, .03, .12), loc=(0, 3.58, .62), bevel=0)
    a.part('Fuel_tank', 'Steel').cyl(.26, 1.0, loc=(-.85, -.9, .72), rot=(R90, 0, 0), seg=10, bevel=.02, bseg=1)
    armor.box((.5, .6, .45), loc=(.85, -.9, .75), bevel=.02, seg=1)
    _wheels(a, [(sx * .98, -2.55) for sx in (-1, 1)], .48, .3, hub=.45)
    _wheels(a, [(sx * x, 2.3) for sx in (-1, 1) for x in (.72, 1.04)], .48, .3, hub=.45)
    _arches(a, 1.15, (-2.55,), .82, .56)
    _turn(a, R90)


BUILDERS = {
    'cottage': (cottage, dict(ao_distance=1.4, grime_height=.8)),
    'townhouse': (townhouse, dict(ao_distance=1.6, grime_height=.9)),
    'apartment': (apartment, dict(ao_distance=1.8, grime_height=1.0)),
    'shop': (shop, dict(ao_distance=1.5, grime_height=.8)),
    'church': (church, dict(ao_distance=2.0, grime_height=1.0)),
    'barn': (barn, dict(ao_distance=1.6, grime_height=.9)),
    'silo': (silo, dict(ao_distance=1.2, grime_height=.8)),
    'warehouse': (warehouse, dict(ao_distance=2.0, grime_height=1.0)),
    'garage': (garage, dict(ao_distance=1.2, grime_height=.6)),
    'water_tower': (water_tower, dict(ao_distance=1.0, grime_height=.6)),
    'ruin': (ruin, dict(ao_distance=1.2, grime_height=.6)),
    'fence': (fence, dict(ao_distance=.4, grime_height=.3)),
    'stone_wall': (stone_wall, dict(ao_distance=.6, grime_height=.3)),
    'hedge': (hedge, dict(ao_distance=.7, grime_height=.4)),
    'car': (car, dict(ao_distance=.5, grime_height=.4)),
    'truck': (truck, dict(ao_distance=.6, grime_height=.5)),
}
