"""Machine Brigade desert and snow map props built with frontier_kit.

Desert (oasis town and oil refinery): adobe houses, a market stall, date palms, saguaros, a
pumpjack, a distillation column, a storage tank, an elevated pipeline and a sandstone mesa.
Snow (mountain village and radar station): snowy pines, a log cabin, snow-capped boulders, a
radar station and a wooden watchtower.

Same conventions as mb_props and mb_town: metres, +Z up, Blender X = width, Y = depth, the front
faces -Y and origins sit on the ground at the footprint centre. Parts that touch are pushed 1-2 cm
into or away from each other so no two visible faces are coplanar (they z-fight in game).

Moving parts: the `Pump_beam` pivot (pumpjack walking beam, horse head, bridle and pitman arms)
rocks about its local Y axis (Unity Z); the `Radar` pivot (radar dish) spins about local Z.
Trees and cacti stay under 400 triangles and rocks under 600 because maps place thousands.
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector, noise

from mb_terrain import _outline, _split
from mb_town import door, fbox, pane, roof_shell, slide, window
from mb_vehicles import _dish

R90 = math.pi / 2
TAU = math.tau


# ----------------------------------------------------------------------------- shared helpers
def rod(part, p0, p1, r, seg=6, r2=None, bevel=0.0):
    """Cylinder from p0 to p1 (logs, posts, pipes); r2 is the radius at p1."""
    p0, p1 = Vector(p0), Vector(p1)
    v = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(v.normalized()).to_euler('XYZ')
    part.cyl(r, v.length, loc=(p0 + p1) / 2, rot=rot, seg=seg, r2=r2, bevel=bevel)


def loft_along(part, spine, side, sections):
    """Skin cross-sections along a polyline. sections[i] is a list of (u, v) offsets in the plane
    across the spine at station i (u along `side`, v perpendicular to it), or [] for a pointed tip."""
    pts = [Vector(p) for p in spine]
    n = len(pts)
    side = Vector(side).normalized()
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        s = (side - t * side.dot(t)).normalized()
        w = t.cross(s)
        if not sections[i]:
            rings.append([tuple(p)])
        else:
            rings.append([tuple(p + s * u + w * v) for u, v in sections[i]])
    part.loft(rings)


def star(r, ribs, depth=.14, twist=0.0):
    """Ribbed cross-section: 2 * ribs points alternating between r and r * (1 - depth)."""
    return [((r if k % 2 == 0 else r * (1 - depth)) * math.cos(twist + k * math.pi / ribs),
             (r if k % 2 == 0 else r * (1 - depth)) * math.sin(twist + k * math.pi / ribs)) for k in range(2 * ribs)]


def rim(part, x0, x1, y0, y1, z, h, t, gaps=(), bevel=.06, seg=1):
    """Four boxes `t` thick and `h` tall standing on the rectangle's edges from height z (parapets,
    plinth skirts). gaps [(side, a, b)] leave openings: side '-y'/'+y' cut along X, '-x'/'+x'
    along Y. The side boxes butt against the front and back ones."""
    sides = (('-y', (x0, x1), y0 + t / 2), ('+y', (x0, x1), y1 - t / 2),
             ('-x', (y0 + t, y1 - t), x0 + t / 2), ('+x', (y0 + t, y1 - t), x1 - t / 2))
    for side, (lo, hi), c in sides:
        segs = [(lo, hi)]
        for gs, ga, gb in gaps:
            if gs == side:
                segs = [q for s0, s1 in segs for q in ((s0, min(s1, ga)), (max(s0, gb), s1)) if q[1] - q[0] > .05]
        for s0, s1 in segs:
            m, L = (s0 + s1) / 2, s1 - s0
            if side in ('-y', '+y'):
                part.box((L, t, h), loc=(m, c, z + h / 2), bevel=bevel, seg=seg)
            else:
                part.box((t, L, h), loc=(c, m, z + h / 2), bevel=bevel, seg=seg)


def ring_rail(part, cx, cy, z, r, h=1.0, posts=8, pts=16, post=.05, rail=.03):
    """Handrail on posts around a circle of radius r standing on z."""
    for k in range(posts):
        a = k * TAU / posts
        part.box((post, post, h), loc=(cx + r * math.cos(a), cy + r * math.sin(a), z + h / 2), bevel=0)
    line = [(cx + r * math.cos(TAU * j / pts), cy + r * math.sin(TAU * j / pts), z + h) for j in range(pts + 1)]
    part.tube(line, rail, seg=4, caps=False)


def ladder(part, p0, z1, along, width=.44, step=.4, rail=.05, rung=.035):
    """Vertical ladder standing at p0 = (x, y, z0) up to z1; `along` is the angle (radians) of the
    rung direction in the XY plane."""
    x, y, z0 = p0
    c, s = math.cos(along), math.sin(along)
    for k in (-1, 1):
        part.box((rail, rail, z1 - z0), loc=(x + k * c * width / 2, y + k * s * width / 2, (z0 + z1) / 2),
                 rot=(0, 0, along), bevel=0)
    n = max(1, int((z1 - z0 - .2) / step))
    for i in range(n):
        part.box((width, rung, rung), loc=(x, y, z0 + .3 + i * step), rot=(0, 0, along), bevel=0)


def flame(part, loc, r, h):
    """Teardrop flame (flare stack pilot) standing on loc."""
    part.lathe([(r * .55, 0), (r, h * .22), (r * .8, h * .5), (r * .35, h * .8), (0, h)], loc=loc, seg=8)


# ----------------------------------------------------------------------------- adobe helpers
def deep_window(a, rng, face, p, w=.62, h=.78, depth=.2, lit=.12):
    """Small window deep in a thick mud wall; p = centre of the opening on the wall surface. A pane
    sits 2 cm proud of the wall between reveal blocks that stand `depth` proud (sunk 10 cm into the
    wall), so it reads recessed; a rough wooden lintel spans the head and a sill the foot."""
    t = .16
    rv = a.part('Reveals', 'AdobeTrim')
    fbox(pane(a, rng, lit), face, p, (w + .02, .1, h + .02), out=-.03)
    for s in (-1, 1):
        fbox(rv, face, slide(face, p, s * (w / 2 + t / 2)), (t, depth + .1, h), out=depth / 2 - .05)
    fbox(rv, face, slide(face, p, 0, -h / 2 - .05), (w + 2 * t + .08, depth + .14, .1), out=(depth + .14) / 2 - .05)
    fbox(a.part('Lintels', 'Wood'), face, slide(face, p, 0, h / 2 + .09), (w + 2 * t + .3, depth + .06, .18),
         out=(depth + .06) / 2 - .05)


def adobe_door(a, face, p, w=1.0, h=2.1, depth=.22, mat='Wood'):
    """Plank door deep in a mud wall (p = middle of the threshold on the wall surface), with iron
    straps, reveals, a wooden lintel and a threshold step."""
    t = .18
    rv = a.part('Reveals', 'AdobeTrim')
    fbox(a.part('Door', mat), face, slide(face, p, 0, h / 2), (w + .02, .1, h), out=-.03, bevel=.015)
    straps = a.part('Straps', 'Armor')
    for dz in (.45, h - .5):
        fbox(straps, face, slide(face, p, 0, dz), (w - .12, .03, .08), out=.035)
    for s in (-1, 1):
        fbox(rv, face, slide(face, p, s * (w / 2 + t / 2), h / 2), (t, depth + .1, h), out=depth / 2 - .05)
    fbox(a.part('Lintels', 'Wood'), face, slide(face, p, 0, h + .1), (w + 2 * t + .4, depth + .06, .2),
         out=(depth + .06) / 2 - .05)
    fbox(rv, face, slide(face, p, 0, -.04), (w + 2 * t + .3, .55, .2), out=.22)


def adobe_block(a, x0, x1, y0, y1, z0, H, gaps=(), ph=.55, pt=.26, bevel=.14):
    """Mud-brick block with soft rounded corners, a rounded parapet and a sunken roof deck.
    Returns the height of the deck surface (z0 + H + .08)."""
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a.part('Walls', 'Adobe').box((w, d, H + .02), loc=(cx, cy, z0 + (H + .02) / 2), bevel=bevel, seg=2)
    top = z0 + H
    rim(a.part('Parapet', 'Adobe'), x0 + .01, x1 - .01, y0 + .01, y1 - .01, top - .02, ph, pt, gaps, bevel=.08,
        seg=1)
    a.part('Roof_deck', 'AdobeTrim').box((w - 2 * pt, d - 2 * pt, .1), loc=(cx, cy, top + .03), bevel=0)
    return top + .08


def adobe_stair(a, xc, width, y_foot, y_land, z_top, steps, outer=1):
    """Solid mud stair against a wall running along Y: `steps` steps from y_foot climbing towards
    +Y up to z_top, then a landing to y_land, with a rounded balustrade on its outer side
    (outer = +1: the +X side). Returns where the landing starts."""
    rise = z_top / steps
    run = (y_land - y_foot - .6) / steps
    prof = [(y_foot, 0.0)]
    for k in range(steps):
        y = y_foot + k * run
        prof += [(y, (k + 1) * rise), (y + run, (k + 1) * rise)]
    landing = y_foot + (steps - 1) * run
    prof[-1] = (y_land, z_top)
    prof.append((y_land, 0.0))
    part = a.part('Stair', 'Adobe')
    part.prism(prof, width, loc=(xc, 0, 0), axis='X', bevel=0)
    part.prism([(y_foot, 0), (y_foot, rise + .45), (landing, z_top + .45), (y_land, z_top + .45), (y_land, 0)], .16,
               loc=(xc + outer * (width / 2 + .02), 0, 0), axis='X', bevel=.05, seg=1)
    return landing


def vigas(a, xs, y_face, z, sign, rng, r=.085):
    """Round roof beams poking out of a wall at y_face (sign = outward direction along Y)."""
    part = a.part('Vigas', 'Wood')
    for x in xs:
        out = rng.uniform(.34, .5)
        rod(part, (x, y_face - sign * .3, z), (x, y_face + sign * out, z), r * rng.uniform(.9, 1.1), seg=5)


def canal(a, face, p, length=.55):
    """Wooden drain spout through a parapet; p is on the parapet's outer face at deck level."""
    fbox(a.part('Canales', 'Wood'), face, p, (.2, length + .3, .14), out=length / 2 - .15)


def pot(part, x, y, z=0.0, s=1.0, seg=7):
    """Clay water jar."""
    part.lathe([(.14 * s, 0), (.25 * s, .2 * s), (.23 * s, .44 * s), (.11 * s, .58 * s), (.13 * s, .68 * s),
                (0, .68 * s)], loc=(x, y, z), seg=seg)


def roof_tank(a, x, y, z, r=.5, h=1.0, mat='PlasterBlue', leg=.7):
    """Water tank on a four-legged steel stand standing on a roof at height z."""
    steel = a.part('Tank_stand', 'Steel')
    k = r * .8
    for sx in (-1, 1):
        for sy in (-1, 1):
            steel.box((.06, .06, leg), loc=(x + sx * k, y + sy * k, z + leg / 2 - .02), bevel=0)
    steel.box((2 * k + .12, 2 * k + .12, .07), loc=(x, y, z + leg - .02), bevel=0)
    a.part('Water_tank', mat).cyl(r, h, loc=(x, y, z + leg + h / 2 - .01), seg=12, bevel=.05, bseg=1)
    a.part('Tank_lid', 'Steel').cyl(r * .36, .1, loc=(x, y, z + leg + h + .02), seg=8, bevel=0)


# ----------------------------------------------------------------------------- desert buildings
def adobe_house(a):
    """Flat-roofed mud-brick house (7 x 7 m): rounded parapet, deep little windows, a plank door,
    protruding vigas, drain spouts, an outside stair to the roof and a roof water tank."""
    rng = random.Random(201)
    x0, x1, y0, y1, H = -3.45, 2.55, -3.0, 3.0, 3.1
    cx = (x0 + x1) / 2
    door_x = -1.35
    rim(a.part('Plinth', 'AdobeTrim'), x0 - .05, x1 + .05, y0 - .05, y1 + .05, 0.0, .45, .12,
        gaps=(('-y', door_x - .7, door_x + .7),), bevel=0)
    # Outside stair up the east wall to a gap in the parapet.
    landing = adobe_stair(a, x1 + .43, .9, -1.9, y1 - .27, H + .08, 10)
    deck = adobe_block(a, x0, x1, y0, y1, 0.0, H, gaps=(('+x', landing, y1),))
    xs = [cx + x for x in (-2.3, -1.15, 0, 1.15, 2.3)]
    vigas(a, xs, y0, H - .28, -1, rng)
    vigas(a, xs, y1, H - .28, 1, rng)
    adobe_door(a, '-y', (door_x, y0, .1), w=1.0, h=2.05)
    deep_window(a, rng, '-y', (1.0, y0, 1.75))
    for x in (-1.9, .7):
        deep_window(a, rng, '+y', (x, y1, 1.75))
    for y in (-1.3, 1.3):
        deep_window(a, rng, '-x', (x0, y, 1.75))
    deep_window(a, rng, '+x', (x1, -2.25, 2.0), w=.46, h=.56)
    for face, p in (('-y', (-.2, y0 + .01, deck + .05)), ('+y', (-2.6, y1 - .01, deck + .05))):
        canal(a, face, p)
    # Roof: water tank on a steel stand, a little clay chimney.
    roof_tank(a, cx - 1.3, 1.25, deck, r=.55, h=1.05)
    trim = a.part('Chimney', 'AdobeTrim')
    trim.box((.5, .5, .8), loc=(cx + 1.6, -1.6, deck + .38), bevel=.08, seg=1)
    trim.box((.66, .66, .08), loc=(cx + 1.6, -1.6, deck + .82), bevel=0)
    # Jars and a bench by the door.
    jars = a.part('Jars', 'Brick')
    pot(jars, -2.6, y0 - .45, s=1.0)
    pot(jars, -3.05, y0 - .35, s=.8)
    bench = a.part('Bench', 'Wood')
    bench.box((1.1, .36, .1), loc=(1.0, y0 - .38, .45), bevel=.02, seg=1)
    for sx in (-1, 1):
        bench.box((.1, .3, .42), loc=(1.0 + sx * .45, y0 - .38, .2), bevel=0)


def adobe_large(a):
    """Two-level adobe building (12 x 9 m): a stepped upper storey and tower room on a terraced
    ground floor, an arched portal with a lime-washed moulding, a canvas awning over the shop
    window, a wooden oriel, an outside stair, a ladder, vigas and roof tanks."""
    rng = random.Random(211)
    x0, x1, y0, y1, H1 = -4.75, 5.75, -3.4, 4.0, 3.4
    portal_x = .6
    rim(a.part('Plinth', 'AdobeTrim'), x0 - .05, x1 + .05, y0 - .05, y1 + .05, 0.0, .45, .12,
        gaps=(('-y', portal_x - 1.4, portal_x + 1.4),), bevel=0)
    landing = adobe_stair(a, x0 - .43, .9, -2.9, y1 - .27, H1 + .08, 11, outer=-1)
    deck1 = adobe_block(a, x0, x1, y0, y1, 0.0, H1, gaps=(('-x', landing, y1),))
    # Upper storey, set back behind the terrace, and a small tower room on top of it.
    ux0, ux1, uy0, uy1, H2 = -4.1, 1.5, -.6, 3.4, 2.9
    deck2 = adobe_block(a, ux0, ux1, uy0, uy1, deck1 - .02, H2, pt=.24, ph=.5)
    tx0, tx1, ty0, ty1, H3 = -3.8, -1.4, 1.0, 3.1, 2.3
    deck3 = adobe_block(a, tx0, tx1, ty0, ty1, deck2 - .02, H3, pt=.22, ph=.45)
    vigas(a, (-3.9, -2.4, 2.6, 4.0, 5.2), y0, H1 - .28, -1, rng)
    vigas(a, (-3.9, -2.2, -.5, 1.2, 2.9, 4.6), y1, H1 - .28, 1, rng)
    vigas(a, (-3.4, -2.1, -.8, .5), uy0, deck1 + H2 - .3, -1, rng)
    vigas(a, (-3.2, -2.0), ty0, deck2 + H3 - .28, -1, rng)
    # Arched portal: a raised panel, a dark recess, the double door and a lime-washed moulding.
    panel_out, pw, phh = .32, 3.1, H1 + .85
    fbox(a.part('Portal', 'AdobeTrim'), '-y', (portal_x, y0, phh / 2), (pw, panel_out + .1, phh),
         out=panel_out / 2 - .05, bevel=.1)
    yp = y0 - panel_out
    dw, spring = 1.7, 2.05

    def arch_poly(half, z_spring, n=8):
        pts = [(half, 0.0)]
        pts += [(half * math.cos(math.pi * i / n), z_spring + half * math.sin(math.pi * i / n)) for i in range(n + 1)]
        pts.append((-half, 0.0))
        return pts

    a.part('Portal_recess', 'Charred').prism(arch_poly(dw / 2 + .16, spring), .06, loc=(portal_x, yp - .01, .12),
                                             axis='Y', bevel=0)
    a.part('Door', 'Wood').prism(arch_poly(dw / 2, spring), .06, loc=(portal_x, yp - .03, .12), axis='Y', bevel=0)
    straps = a.part('Straps', 'Armor')
    straps.box((.05, .03, spring + dw / 2 - .1), loc=(portal_x, yp - .075, .12 + (spring + dw / 2) / 2), bevel=0)
    for dz in (.6, 1.6):
        straps.box((dw - .12, .03, .07), loc=(portal_x, yp - .075, .12 + dz), bevel=0)
    rm = dw / 2 + .3
    mould = [(portal_x + rm, yp - .06, 0.0)]
    mould += [(portal_x + rm * math.cos(math.pi * i / 10), yp - .06, .12 + spring + rm * math.sin(math.pi * i / 10))
              for i in range(11)]
    mould.append((portal_x - rm, yp - .06, 0.0))
    a.part('Moulding', 'PlasterWhite').tube(mould, .1, seg=5)
    fbox(a.part('Reveals', 'AdobeTrim'), '-y', (portal_x, yp, .07), (pw + .2, .7, .14), out=.3)
    # Ground floor windows; the shop window under the awning.
    for x in (-3.6, -1.9, 2.75):
        deep_window(a, rng, '-y', (x, y0, 1.8))
    deep_window(a, rng, '-y', (4.4, y0, 1.55), w=1.5, h=1.3, lit=.6)
    for x in (-3.2, .3, 3.5):
        deep_window(a, rng, '+y', (x, y1, 1.8))
    for y in (-1.8, .8):
        deep_window(a, rng, '+x', (x1, y, 1.8))
    deep_window(a, rng, '-x', (x0, -1.5, 1.9), w=.46, h=.56)
    # Upper floors.
    zu = deck1 + 1.5
    deep_window(a, rng, '-y', (-3.0, uy0, zu), w=.6, h=.8, lit=.25)
    deep_window(a, rng, '+y', (-.5, uy1, zu), w=.6, h=.8, lit=.25)
    deep_window(a, rng, '+x', (ux1, 1.4, zu), w=.6, h=.8, lit=.25)
    deep_window(a, rng, '-x', (ux0, .6, zu), w=.6, h=.8, lit=.25)
    deep_window(a, rng, '-y', (-2.6, ty0, deck2 + 1.2), w=.5, h=.6, lit=.3)
    deep_window(a, rng, '+x', (tx1, 2.1, deck2 + 1.2), w=.5, h=.6, lit=.3)
    adobe_door(a, '-y', (.35, uy0, deck1), w=.9, h=1.95)
    # Wooden oriel (mashrabiya) on the upper front.
    ox, oz = -1.35, deck1 + 1.55
    wood = a.part('Oriel', 'Wood')
    fbox(wood, '-y', (ox, uy0, oz), (1.3, .6, 1.45), out=.25, bevel=.03)
    fbox(wood, '-y', (ox, uy0, oz + .8), (1.5, .75, .16), out=.3, bevel=.02)
    fbox(wood, '-y', (ox, uy0, oz - .78), (1.45, .7, .12), out=.28, bevel=.02)
    fbox(a.part('Oriel_screen', 'Charred'), '-y', (ox, uy0, oz), (1.0, .03, 1.15), out=.56)
    for i in range(4):
        fbox(wood, '-y', (ox - .375 + i * .25, uy0, oz), (.05, .03, 1.15), out=.58)
    for j in range(4):
        fbox(wood, '-y', (ox, uy0, oz - .43 + j * .29), (1.0, .03, .05), out=.6)
    # Canvas awning on wooden poles over the shop window.
    ax, aw, ad = 4.4, 2.5, 1.35
    z_wall, z_front = 2.75, 2.2
    L = math.hypot(ad, z_wall - z_front)
    ang = math.atan2(z_wall - z_front, ad)
    cloth = a.part('Awning', 'Canvas')
    cloth.box((aw, L + .05, .05), loc=(ax, y0 - ad / 2, (z_wall + z_front) / 2), rot=(ang, 0, 0), bevel=0)
    cloth.box((aw, .03, .26), loc=(ax, y0 - ad - .02, z_front - .12), bevel=0)
    poles = a.part('Poles', 'Wood')
    for sx in (-1, 1):
        poles.cyl(.05, z_front, loc=(ax + sx * (aw / 2 - .08), y0 - ad + .05, z_front / 2), seg=6, bevel=0)
    poles.box((aw, .08, .08), loc=(ax, y0 - ad + .05, z_front - .06), bevel=0)
    # Ladder from the terrace to the upper roof, poking above the parapet.
    lad = a.part('Ladder', 'Wood')
    lx, ly, ztop = 1.0, uy0 - .45, deck2 + 1.1
    for sx in (-1, 1):
        lad.limb((lx + sx * .25, ly, deck1 - .02), (lx + sx * .25, ly + .38, ztop), .07, .07, bevel=0)
    for i in range(7):
        z = deck1 + .35 + i * .45
        lad.box((.5, .05, .05), loc=(lx, ly + .38 * (z - deck1) / (ztop - deck1), z), bevel=0)
    # Drain spouts, roof tanks, a chimney, jars and crates.
    for face, p in (('-y', (-.7, y0 + .01, deck1 + .05)), ('+y', (2.4, y1 - .01, deck1 + .05)),
                    ('-y', (-.6, uy0 + .01, deck2 + .05))):
        canal(a, face, p)
    for tx in (-.3, .75):
        roof_tank(a, tx, 1.9, deck2, r=.44, h=.95, mat='Fuel', leg=.6)
    trim = a.part('Chimney', 'AdobeTrim')
    trim.box((.5, .5, .9), loc=(-2.1, 1.6, deck3 + .43), bevel=.08, seg=1)
    trim.box((.66, .66, .08), loc=(-2.1, 1.6, deck3 + .92), bevel=0)
    jars = a.part('Jars', 'Brick')
    pot(jars, -1.4, y0 - .45, s=1.0)
    pot(jars, 2.45, y0 - .4, s=.85)
    crates = a.part('Crates', 'Wood')
    for z, turn in ((.25, .1), (.73, -.15)):
        crates.box((.6, .5, .48), loc=(5.2, y0 - .55, z), rot=(0, 0, turn), bevel=.02, seg=1)
    a.part('Produce', 'Hazard').box((.5, .4, .06), loc=(5.2, y0 - .55, .98), rot=(0, 0, -.15), bevel=.02, seg=1)


def market_stall(a):
    """Market stall (4 x 3 m): a wooden frame under a striped cloth canopy, a counter of produce
    crates, sacks and jars, and a rug hanging at the back."""
    rng = random.Random(221)
    wood = a.part('Frame', 'Wood')
    xs, yf, yb = 1.85, -1.3, 1.3
    zf, zb = 2.3, 2.62
    for x in (-xs, xs):
        wood.box((.1, .1, zf), loc=(x, yf, zf / 2), bevel=.015, seg=1)
        wood.box((.1, .1, zb), loc=(x, yb, zb / 2), bevel=.015, seg=1)
        wood.limb((x, yf, zf - .05), (x, yb, zb - .05), .08, .1, bevel=0)
    wood.box((2 * xs + .1, .09, .1), loc=(0, yf, zf - .05), bevel=0)
    wood.box((2 * xs + .1, .09, .1), loc=(0, yb, zb - .05), bevel=0)
    # Canopy: white cloth with red stripes 1.2 cm proud, and a scalloped front valance.
    k = (zb - zf) / (yb - yf)
    y0, y1 = yf - .2, yb + .15
    z0, z1 = zf + .03 - k * .2, zb + .03 + k * .15
    L = math.hypot(y1 - y0, z1 - z0)
    ang = math.atan2(z1 - z0, y1 - y0)
    ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
    n, sw = 8, .52
    white = a.part('Canopy', 'PlasterWhite')
    stripes = a.part('Canopy_stripes', 'WoodRed')
    white.box((n * sw, L, .04), loc=(0, ym, zm), rot=(ang, 0, 0), bevel=0)
    ny, nz = -math.sin(ang) * .012, math.cos(ang) * .012
    for i in range(0, n, 2):
        x = -n * sw / 2 + (i + .5) * sw
        stripes.box((sw, L - .02, .04), loc=(x, ym + ny, zm + nz), rot=(ang, 0, 0), bevel=0)
    for i in range(n):
        x = -n * sw / 2 + (i + .5) * sw
        red = i % 2 == 0
        (stripes if red else white).prism([(-sw / 2, 0), (sw / 2, 0), (sw / 2 - .02, -.22), (0, -.32),
                                           (-sw / 2 + .02, -.22)], .03,
                                          loc=(x, y0 - .02 - (.012 if red else 0), z0 + .01), axis='Y', bevel=0)
    # Counter with produce crates.
    wood.box((3.5, .7, .08), loc=(0, yf + .15, .9), bevel=.02, seg=1)
    wood.box((3.5, .05, .82), loc=(0, yf - .17, .45), bevel=.01, seg=1)
    for x in (-1.6, 1.6):
        wood.box((.07, .07, .86), loc=(x, yf + .44, .43), bevel=0)
    crates = a.part('Crates', 'Crate')
    produce = ('FoliageLight', 'Hazard', 'BarrelRed', 'Brick', 'FoliageLight')
    for i, mat in enumerate(produce):
        x = -1.4 + i * .7
        tilt = rng.uniform(-.06, .06)
        crates.box((.62, .5, .2), loc=(x, yf + .12, 1.04), rot=(0, 0, tilt), bevel=.015, seg=1)
        if i == 0:
            for j in range(3):
                a.part('Melons', mat, flat=True).ico(.14, loc=(x - .17 + j * .17, yf + .12, 1.2), sub=1, jitter=.1,
                                                      seed=j)
        else:
            a.part('Produce', mat).box((.54, .42, .08), loc=(x, yf + .12, 1.14), rot=(0, 0, tilt), bevel=.03, seg=1)
    # Stock behind the counter: stacked crates, sacks and jars.
    for x, y, z, turn in ((-1.4, .75, .22, .1), (-1.35, .8, .66, -.1), (1.45, .8, .22, .05)):
        crates.box((.62, .5, .44), loc=(x, y, z), rot=(0, 0, turn), bevel=.02, seg=1)
    sacks = a.part('Sacks', 'Sandbag')
    for x, y, turn in ((-.5, .85, .2), (.2, .9, -.15), (.85, .7, .4)):
        sacks.box((.5, .38, .62), loc=(x, y, .3), rot=(0, 0, turn), bevel=.12, seg=1, taper=(.8, .8))
    jars = a.part('Jars', 'Brick')
    pot(jars, 2.25, -.9, s=.9)
    pot(jars, 2.3, -.25, s=.7)
    # Rug hanging from the back beam: red field, ochre border.
    a.part('Rug_border', 'Hazard').box((2.0, .03, 1.3), loc=(0, yb + .07, zb - .85), bevel=0)
    a.part('Rug', 'BarrelRed').box((1.8, .03, 1.1), loc=(0, yb + .055, zb - .85), bevel=0)


def palm_tree(a, seed, height=7.6, lean=(.8, .25), fronds=11, dry=2):
    """Date palm: a leaning, curved trunk ringed with old leaf bases, a crown of arching and
    drooping fronds (the lowest ones dry) and a date cluster."""
    rng = random.Random(seed)
    stations = 9
    spine, rings = [], []
    for i in range(stations):
        t = i / (stations - 1)
        spine.append((lean[0] * t ** 1.7, lean[1] * t ** 1.7, -.05 + (height + .05) * t))
        r = .42 if i == 0 else (.29 - .08 * t) * (1.0 if i % 2 == 0 else .83)
        turn = i * math.pi / 5
        rings.append([(r * math.cos(turn + k * TAU / 5), r * math.sin(turn + k * TAU / 5)) for k in range(5)])
    loft_along(a.part('Trunk', 'Bark'), spine, (-lean[1], lean[0], 0), rings)
    top = Vector(spine[-1])
    a.part('Crown', 'Bark', flat=True).ico((.42, .42, .5), loc=top + Vector((0, 0, .05)), sub=1, jitter=.15,
                                            seed=seed)
    for k in range(fronds):
        upper = k >= fronds - 4
        yaw = (k * 1.6 + .8) if upper else (k * 2.4 + rng.uniform(-.2, .2))
        d = Vector((math.cos(yaw), math.sin(yaw), 0))
        if upper:
            L, rise, droop, mat = rng.uniform(2.4, 2.9), 1.25, .9, 'FoliageLight'
        elif k < dry:
            L, rise, droop, mat = rng.uniform(2.6, 3.0), -.2, 1.4, 'Sandbag'
        else:
            L, rise, droop, mat = rng.uniform(3.1, 3.6), .45, 1.05, 'Foliage' if k % 2 else 'FoliageLight'
        spine_f, secs = [], []
        for s, wk in ((0, .08), (.28, .42), (.55, .46), (.8, .3), (1.0, 0)):
            spine_f.append(top + d * (.15 + L * s) + Vector((0, 0, .1 + L * (rise * s - droop * s * s))))
            secs.append([(-wk, 0), (0, .1 * min(1, wk * 4)), (wk, 0)] if wk else [])
        loft_along(a.part('Fronds', mat), spine_f, (-d.y, d.x, 0), secs)
    yaw = rng.uniform(0, TAU)
    a.part('Dates', 'Brick', flat=True).ico((.22, .22, .3), loc=top + Vector((math.cos(yaw) * .42,
                                                                               math.sin(yaw) * .42, -.35)),
                                            sub=1, jitter=.2, seed=seed + 3)


def palm(a):
    """Date palm, about 8.6 m."""
    palm_tree(a, 4)


def cactus(a):
    """Saguaro (3.6 m): a ribbed column with a rounded crown and two upturned arms."""
    body = a.part('Body', 'Foliage')
    zs, rs = (-.05, .6, 2.7, 3.28, 3.52), (.34, .33, .31, .25, .13)
    loft_along(body, [(0, 0, z) for z in zs] + [(0, 0, 3.62)], (0, 1, 0), [star(r, 8) for r in rs] + [[]])
    for yaw, z0, reach, top in ((.35, 1.25, .78, 2.75), (math.pi + .5, 1.8, .62, 2.95)):
        c, s = math.cos(yaw), math.sin(yaw)
        path = [(.1, z0), (.5, z0 + .03), (reach, z0 + .32), (reach + .04, top - .35), (reach + .02, top - .1),
                (reach, top)]
        radii = (.2, .19, .18, .17, .12)
        loft_along(body, [(c * u, s * u, z) for u, z in path], (-s, c, 0), [star(r, 5, .16) for r in radii] + [[]])


def oil_pump(a):
    """Pumpjack (5 x 2.5 m). The walking beam, horse head, equalizer and pitman arms hang from the
    `Pump_beam` pivot on the samson post's saddle bearing and rock about its local Y axis; the
    gearbox, cranks and counterweights stay put (at RTS range the pitman arms read as riding the
    cranks). The horse head's arc is centred on the axle, so the static bridle hanging from its
    front stays tangent to it at any rocking angle up to about 20 degrees."""
    conc = a.part('Base', 'Concrete')
    conc.box((4.0, 1.9, .2), loc=(.45, 0, .1), bevel=.04)
    conc.box((.9, .9, .24), loc=(-2.0, 0, .12), bevel=.04)
    skid = a.part('Skid', 'Rust')
    for y in (-.42, .42):
        skid.box((3.7, .16, .3), loc=(.45, y, .35), bevel=.02, seg=1)
    for x in (-1.2, .3, 1.6, 2.2):
        skid.box((.14, .7, .1), loc=(x, 0, .45), bevel=0)
    # Samson post: two A-frames meeting under the saddle bearing; the beam pivots on its axle.
    px, pv = -.1, 3.12
    frame = a.part('Samson_post', 'Armor')
    for y in (-1, 1):
        for x in (-.95, .6):
            frame.limb((x, y * .42, .45), (px + (x - px) * .06, y * .15, pv - .15), .14, .14, bevel=.02, seg=1)
        frame.limb((-.62, y * .36, 1.6), (.3, y * .36, 1.6), .08, .08, bevel=0)
    frame.limb((-.35, -.26, 2.4), (-.35, .26, 2.4), .08, .08, bevel=0)
    frame.box((.42, .44, .2), loc=(px, 0, pv - .12), bevel=.03, seg=1)
    a.part('Samson_post', 'Steel').cyl(.08, .56, loc=(px, 0, pv), rot=(R90, 0, 0), seg=10, bevel=.01, bseg=1)
    # Walking beam, horse head, equalizer and pitman arms, authored in pivot space.
    a.pivot('Pump_beam', (px, 0, pv))
    zb = .3
    beam = a.part('Beam', 'Hazard', 'Pump_beam')
    beam.box((3.65, .1, .44), loc=(.15, 0, zb), bevel=.015, seg=1)
    for z in (-.24, .24):
        beam.box((3.65, .34, .06), loc=(.15, 0, zb + z), bevel=.015, seg=1)
    R = 1.9
    arc = [(R * math.cos(math.radians(t)), R * math.sin(math.radians(t))) for t in range(158, 203, 11)]
    beam.prism([(-1.45, .62)] + arc + [(-1.45, -.5)], .46, axis='Y', bevel=.03)
    beam.box((.28, .5, .3), loc=(1.95, 0, zb - .16), bevel=.02, seg=1)
    steel = a.part('Beam_steel', 'Steel', 'Pump_beam')
    steel.box((.36, .4, .14), loc=(0, 0, .02), bevel=.02, seg=1)
    steel.box((.18, 1.56, .14), loc=(1.95, 0, -.03), bevel=.02, seg=1)
    # Bridle, carrier bar and polished rod (static): the cables leave the arc at its tangent point.
    bridle = a.part('Bridle', 'Steel')
    bx = px - R - .03
    for y in (-.1, .1):
        bridle.tube([(bx, y, pv), (bx, y, pv - 1.55)], .022, seg=4)
    bridle.box((.14, .42, .1), loc=(bx, 0, pv - 1.57), bevel=0)
    bridle.cyl(.035, .72, loc=(bx, 0, pv - 1.57 - .36), seg=6, bevel=0)
    shaft = Vector((2.0, 1.45))
    crank_dir = Vector((math.cos(math.radians(215)), math.sin(math.radians(215))))
    pin = shaft + crank_dir * .45
    pitman = a.part('Pitman', 'Armor', 'Pump_beam')
    for y in (-.74, .74):
        pitman.limb((1.95, y, -.03), (pin.x - px, y, pin.y - pv), .12, .1, bevel=.015)
    # Gearbox, cranks and counterweights.
    gear = a.part('Gearbox', 'Armor')
    gear.box((.9, .7, .3), loc=(2.0, 0, .65), bevel=.02, seg=1)
    gear.box((.82, .62, .82), loc=(2.0, 0, 1.2), bevel=.06)
    pins = a.part('Crank_shaft', 'Steel')
    pins.cyl(.09, 1.35, loc=(2.0, 0, shaft.y), rot=(R90, 0, 0), seg=10, bevel=.01, bseg=1)
    weights = a.part('Counterweights', 'BarrelRed')
    ang = math.radians(215)
    for y in (-.53, .53):
        gear.limb((shaft.x, y, shaft.y), (shaft.x + crank_dir.x * .6, y, shaft.y + crank_dir.y * .6), .16, .12,
                  bevel=.02)
        pts = []
        for r, t in ((.5, -24), (1.0, -24), (1.02, 0), (1.0, 24), (.5, 24)):
            aa = ang + math.radians(t)
            pts.append((shaft.x + r * math.cos(aa), shaft.y + r * math.sin(aa)))
        weights.prism(pts, .22, loc=(0, y + (.02 if y > 0 else -.02), 0), axis='Y', bevel=.03)
        pins.cyl(.06, .3, loc=(pin.x, y * 1.2, pin.y), rot=(R90, 0, 0), seg=8, bevel=0)
    # Motor beside the gearbox and the belt guard between their pulleys.
    a.part('Motor', 'Steel').cyl(.2, .44, loc=(2.22, -.93, .74), rot=(R90, 0, 0), seg=12, bevel=.03)
    a.part('Motor', 'Armor').box((.44, .46, .2), loc=(2.22, -.93, .45), bevel=.02, seg=1)
    a.part('Belt_guard', 'Hazard').limb((2.24, -.73, .7), (2.08, -.73, 1.3), .36, .08, bevel=.03)
    pins.cyl(.05, .44, loc=(2.08, -.5, 1.3), rot=(R90, 0, 0), seg=8, bevel=0)
    # Wellhead: casing, stuffing box, valves and a flow line.
    well = a.part('Wellhead', 'Steel')
    well.cyl(.18, .45, loc=(-2.0, 0, .45), seg=10, bevel=.02, bseg=1)
    well.cyl(.24, .08, loc=(-2.0, 0, .7), seg=10, bevel=.01, bseg=1)
    well.cyl(.11, .3, loc=(-2.0, 0, .88), seg=8, bevel=.01, bseg=1)
    well.tube([(-2.0, -.1, .55), (-2.0, -.75, .55), (-2.0, -.95, .12), (-1.2, -1.05, .12)], .06, seg=6)
    wheels = a.part('Valves', 'BarrelRed')
    wheels.torus(.12, .02, loc=(-2.0, -.45, .74), seg=10, ring=4)
    wheels.torus(.1, .02, loc=(-2.3, 0, .55), rot=(0, R90, 0), seg=10, ring=4)
    well.cyl(.03, .3, loc=(-2.15, 0, .55), rot=(0, R90, 0), seg=6, bevel=0)
    well.cyl(.03, .18, loc=(-2.0, -.45, .64), seg=6, bevel=0)
    # Electrical box and a safety rail around the cranks.
    a.part('Control_box', 'Armor').box((.5, .22, .62), loc=(-1.05, 1.02, 1.05), bevel=.03, seg=1)
    a.part('Control_box', 'Steel').box((.07, .07, 1.3), loc=(-1.05, .88, .65), bevel=0)
    rail = a.part('Rail', 'Hazard')
    for x in (1.05, 2.42):
        for y in (-1.21, 1.21):
            rail.box((.06, .06, 1.1), loc=(x, y, .65), bevel=0)
    for y in (-1.21, 1.21):
        for z in (.6, 1.12):
            rail.tube([(1.05, y, z), (2.42, y, z)], .025, seg=4)
    for z in (.6, 1.12):
        rail.tube([(2.42, -1.21, z + .012), (2.42, 1.21, z + .012)], .025, seg=4)


def refinery_tower(a):
    """Distillation column (6 x 6 m, 16 m) with four ringed platforms, ladders, process pipes, a
    reboiler exchanger and a separate flare stack (18 m) burning at the back right."""
    a.part('Pad', 'Concrete').box((5.9, 5.9, .28), loc=(0, 0, .14), bevel=.05)
    cx, cy = -.75, -.35
    prof = [(1.36, .26), (1.36, 1.25), (1.19, 1.4), (1.15, 1.45), (1.15, 5.6), (1.165, 5.62), (1.165, 5.72),
            (1.15, 5.74), (1.15, 9.4), (.88, 10.4), (.88, 13.2), (.895, 13.22), (.895, 13.32), (.88, 13.34),
            (.88, 15.3), (.8, 15.62), (.56, 15.88), (.2, 16.0), (0, 16.02)]
    a.part('Column', 'MetalSheet').lathe(prof, loc=(cx, cy, 0), seg=16)
    a.part('Skirt', 'Armor').cyl(1.39, .95, loc=(cx, cy, .26 + .47), seg=16, bevel=.02, bseg=1)

    def col_r(z):
        return 1.15 if z < 9.4 else (.88 if z > 10.4 else 1.15 - .27 * (z - 9.4))

    grate = a.part('Platforms', 'Armor')
    rail = a.part('Railings', 'Hazard')
    for z in (3.8, 7.6, 11.6, 14.9):
        r0 = col_r(z)
        grate.lathe([(r0 - .06, z - .1), (r0 + .95, z - .1), (r0 + .95, z), (r0 - .06, z)], loc=(cx, cy, 0), seg=16)
        ring_rail(rail, cx, cy, z, r0 + .9, h=1.0, posts=10, pts=20)
        for k in range(4):
            t = k * TAU / 4 + TAU / 8
            grate.limb((cx + math.cos(t) * r0, cy + math.sin(t) * r0, z - .75),
                       (cx + math.cos(t) * (r0 + .8), cy + math.sin(t) * (r0 + .8), z - .1), .08, .08, bevel=0)
    steel = a.part('Ladders', 'Steel')
    for (za, zb), t in zip(((0.28, 3.8), (3.8, 7.6), (7.6, 11.6), (11.6, 14.9)), (-1.0, .9, 2.8, -1.0)):
        r = max(col_r(za), col_r(zb)) + .32
        ladder(steel, (cx + math.cos(t) * r, cy + math.sin(t) * r, za), zb + 1.05, t + R90, step=.45)
    # Process pipes: the overhead vapour line down to the exchanger, feed lines up the column.
    pipe = a.part('Pipes', 'Pipe')
    top = 16.0
    pipe.tube([(cx, cy, top - .1), (cx, cy, top + .55), (1.0, cy, top + .55), (1.0, cy, 2.3), (1.0, cy - 1.6, 2.3),
               (1.0, cy - 1.6, 1.6)], .16, seg=8)
    for t, z_in in ((2.2, 5.0), (2.55, 11.9)):
        c, s = math.cos(t), math.sin(t)
        r_in, r_out = col_r(z_in) - .05, col_r(z_in) + .45
        pipe.tube([(cx + c * r_in, cy + s * r_in, z_in), (cx + c * r_out, cy + s * r_out, z_in),
                   (cx + c * r_out, cy + s * r_out, .55), (cx + c * r_out, 2.75, .55)], .1, seg=6)
    pipe.tube([(cx - .9, cy - .7, 1.0), (cx - 1.55, cy - 1.6, 1.0), (cx - 1.55, -2.75, 1.0)], .12, seg=6)
    valves = a.part('Valves', 'BarrelRed')
    flanges = a.part('Flanges', 'Steel')
    for p in ((1.0, cy - .8, 2.3), (cx - 1.55, -2.1, 1.0)):
        valves.torus(.2, .03, loc=(p[0], p[1], p[2] + .45), seg=10, ring=4)
        flanges.cyl(.26, .2, loc=p, rot=(R90, 0, 0), seg=10, bevel=.02, bseg=1)
        flanges.cyl(.04, .45, loc=(p[0], p[1], p[2] + .22), seg=6, bevel=0)
    # Reboiler exchanger on concrete saddles at the front right.
    ey = cy - 1.6
    ex = a.part('Exchanger', 'Fuel')
    ex.cyl(.55, 2.3, loc=(1.6, ey, 1.25), rot=(0, R90, 0), seg=14, bevel=.05)
    ex.sphere((.2, .55, .55), loc=(2.75, ey, 1.25), seg=14, rings=6)
    for x in (1.0, 2.2):
        flanges.cyl(.62, .1, loc=(x, ey, 1.25), rot=(0, R90, 0), seg=14, bevel=.02, bseg=1)
        a.part('Saddles', 'Concrete').box((.3, .9, .7), loc=(x + .3, ey, .55), bevel=.03, seg=1)
    # Flare stack with red and white bands, a pilot flame, guy wires and a knock-out drum.
    fx, fy, fh = 2.15, 2.15, 18.2
    a.part('Flare_stack', 'Armor').cyl(.24, fh - .28, loc=(fx, fy, .28 + (fh - .28) / 2), r2=.2, seg=10, bevel=0)
    a.part('Flare_base', 'Concrete').box((.9, .9, .4), loc=(fx, fy, .45), bevel=.04, seg=1)
    for i, mat in enumerate(('BarrelRed', 'PlasterWhite', 'BarrelRed', 'PlasterWhite')):
        z = fh - 3.2 + i * .75
        rr = .24 - .04 * (z - .28) / (fh - .28) + .015
        a.part('Flare_bands', mat).cyl(rr, .75, loc=(fx, fy, z + .375), seg=10, bevel=0)
    a.part('Flare_tip', 'Steel').cyl(.3, .7, loc=(fx, fy, fh + .3), r2=.34, seg=10, bevel=.02, bseg=1)
    flame(a.part('Flame', 'Alloy'), (fx, fy, fh + .62), .3, 1.5)
    cable = a.part('Guys', 'Steel')
    for gx, gy in ((.3, 2.85), (2.85, .3), (2.85, 2.85)):
        cable.tube([(fx, fy, 12.5), (gx, gy, .3)], .02, seg=3)
    a.part('Knockout_drum', 'Fuel').cyl(.45, 1.5, loc=(.5, 2.2, .95), rot=(0, R90, 0), seg=12, bevel=.04)
    for x in (.05, .95):
        a.part('Saddles', 'Concrete').box((.25, .7, .5), loc=(x, 2.2, .45), bevel=.03, seg=1)
    pipe.tube([(1.25, 2.2, .95), (fx - .1, 2.2, .95)], .1, seg=6)
    pipe.tube([(.5, 2.2, 1.35), (.5, 2.2, 2.4), (cx + .8, 2.2, 2.4), (cx + .8, .4, 2.4)], .1, seg=6)


def storage_tank(a):
    """Crude storage tank (10 x 10 m, 7.8 m): welded shell courses with a red band and a hazard
    diamond, a cone roof ringed by a railing, a spiral stair, nozzles with valves and roof vents.
    The roof is its own mesh (`Roof`) so an explosion can throw it."""
    Rt, top = 4.3, 7.0
    a.part('Foundation', 'Concrete').cyl(4.96, .3, loc=(0, 0, .15), seg=32, bevel=.04, bseg=1)
    courses = (.28, 1.95, 3.6, 5.3, top)
    prof = []
    for i, (za, zb) in enumerate(zip(courses, courses[1:])):
        r = Rt + .03 - i * .01
        prof += [(r, za + (.02 if i else 0)), (r, zb)]
    a.part('Shell', 'Fuel').lathe(prof + [(Rt - .02, top + .02)], seg=32)
    a.part('Band', 'BarrelRed').cyl(Rt + .02, .9, loc=(0, 0, 5.85), seg=32, bevel=0)
    a.part('Band_edge', 'PlasterWhite').cyl(Rt + .01, 1.02, loc=(0, 0, 5.85), seg=32, bevel=0)
    # Hazard diamond on the front.
    for size, mat, out in ((.9, 'PlasterWhite', .015), (.72, 'BarrelRed', .03)):
        a.part('Marking', mat).box((size, .02, size), loc=(0, -(Rt + .02 + out), 3.0), rot=(0, math.pi / 4, 0),
                                   bevel=0)
    a.part('Marking', 'Armor').box((.3, .02, .13), loc=(0, -(Rt + .02 + .045), 3.0), bevel=0)
    # Cone roof with a rim angle, vents and a hatch.
    a.part('Roof', 'MetalSheet').lathe([(Rt + .06, top - .06), (Rt + .06, top + .06), (.7, top + .66),
                                        (.7, top + .72), (0, top + .74)], seg=32)
    steel = a.part('Roof_steel', 'Steel')
    for vx, vy in ((1.6, .9), (-1.9, -.6)):
        z = top + .06 + .6 * (1 - math.hypot(vx, vy) / Rt)
        steel.cyl(.16, .5, loc=(vx, vy, z + .2), seg=8, bevel=0)
        steel.cyl(.26, .1, loc=(vx, vy, z + .47), seg=8, bevel=.02, bseg=1)
    steel.cyl(.4, .25, loc=(0, 0, top + .8), seg=10, bevel=.03, bseg=1)
    rail = a.part('Railing', 'Hazard')
    ring_rail(rail, 0, 0, top + .02, Rt - .15, h=1.0, posts=16, pts=32)
    # Spiral stair: steps between the shell and an outer stringer with a handrail on posts.
    a0, sweep, n = -R90 - .35, math.radians(150), 24
    r_in, r_out = Rt - .02, 4.93
    rm = (r_in + r_out) / 2
    rise = (top + .04 - .28) / n
    steps = a.part('Stair', 'Armor')
    for k in range(n):
        th = a0 + (k + .5) * sweep / n
        z = .28 + (k + 1) * rise - .03
        steps.box((r_out - r_in, sweep / n * rm * .92, .05), loc=(rm * math.cos(th), rm * math.sin(th), z),
                  rot=(0, 0, th), bevel=0)
    landing = a0 + sweep + .12
    steps.box((r_out - r_in, .9, .06), loc=(rm * math.cos(landing), rm * math.sin(landing), top + .01),
              rot=(0, 0, landing), bevel=0)
    helix = [(a0 + sweep * j / 12, .28 + (top + .04 - .28) * j / 12) for j in range(13)]
    rr = r_out - .03
    steps.tube([(rr * math.cos(th), rr * math.sin(th), z - .16) for th, z in helix], .05, seg=4)
    rail.tube([(rr * math.cos(th), rr * math.sin(th), z + .95) for th, z in helix] +
              [(rr * math.cos(landing + .12), rr * math.sin(landing + .12), top + 1.0)], .03, seg=4)
    for j in range(0, 13, 2):
        th, z = helix[j]
        rail.box((.05, .05, .98), loc=(rr * math.cos(th), rr * math.sin(th), z + .46), bevel=0)
    # Nozzles with flanged valves, and a manway.
    pipe = a.part('Pipes', 'Pipe')
    flanges = a.part('Flanges', 'Steel')
    valves = a.part('Valves', 'BarrelRed')
    for th, zc in ((-.35, .75), (math.pi + .5, .75)):
        c, s = math.cos(th), math.sin(th)
        pipe.tube([(c * (Rt - .1), s * (Rt - .1), zc), (c * 4.75, s * 4.75, zc), (c * 4.75, s * 4.75, -.05)], .16,
                  seg=8)
        for rad in (Rt + .12, 4.45):
            flanges.cyl(.24, .08, loc=(c * rad, s * rad, zc), rot=(0, R90, th), seg=10, bevel=.01, bseg=1)
        flanges.cyl(.04, .5, loc=(c * 4.45, s * 4.45, zc + .25), seg=6, bevel=0)
        valves.torus(.18, .03, loc=(c * 4.45, s * 4.45, zc + .52), seg=10, ring=4)
    th = -2.2
    flanges.cyl(.42, .1, loc=(math.cos(th) * (Rt + .06), math.sin(th) * (Rt + .06), 1.0), rot=(0, R90, th), seg=12,
                bevel=.02, bseg=1)


def pipeline(a):
    """Elevated pipe run (8 x 1.2 m): a main line and a smaller rusty line on three steel H-frame
    supports with concrete footings, flanges at both ends for tiling, a gate valve and a ball valve."""
    main_y, main_z, main_r = -.18, 1.32, .3
    small_y, small_z, small_r = .36, 1.18, .13
    a.part('Main_pipe', 'Pipe').cyl(main_r, 7.97, loc=(0, main_y, main_z), rot=(0, R90, 0), seg=14, bevel=.02,
                                    bseg=1)
    a.part('Small_pipe', 'Rust').cyl(small_r, 8.0, loc=(0, small_y, small_z), rot=(0, R90, 0), seg=10, bevel=.01,
                                     bseg=1)
    flanges = a.part('Flanges', 'Steel')
    for x in (-3.94, 3.94):
        flanges.cyl(main_r + .09, .12, loc=(x, main_y, main_z), rot=(0, R90, 0), seg=12, bevel=0)
        flanges.cyl(small_r + .06, .1, loc=(x, small_y, small_z), rot=(0, R90, 0), seg=10, bevel=0)
    frame = a.part('Supports', 'Armor')
    conc = a.part('Footings', 'Concrete')
    clamps = a.part('Clamps', 'Steel')
    for x in (-2.67, 0.0, 2.67):
        conc.box((.7, 1.2, .3), loc=(x, 0, .13), bevel=.04, seg=1)
        for y in (-.48, .48):
            frame.box((.14, .14, .75), loc=(x, y, .64), bevel=0)
        frame.box((.16, 1.2, .16), loc=(x, 0, .99), bevel=.015, seg=1)
        frame.box((.3, .34, .06), loc=(x, main_y, 1.08), bevel=0)
        clamps.tube([(x, main_y - main_r - .02, 1.08), (x, main_y - main_r - .02, main_z),
                     (x, main_y, main_z + main_r + .03), (x, main_y + main_r + .02, main_z),
                     (x, main_y + main_r + .02, 1.08)], .025, seg=4)
    # Gate valve on the main line: flanged body, bonnet, stem and handwheel.
    vx = -1.33
    body = a.part('Valve_body', 'Steel')
    for dx in (-.3, .3):
        body.cyl(main_r + .1, .1, loc=(vx + dx, main_y, main_z), rot=(0, R90, 0), seg=12, bevel=0)
    body.cyl(main_r + .06, .5, loc=(vx, main_y, main_z), rot=(0, R90, 0), seg=12, bevel=.02, bseg=1)
    body.box((.4, .34, .5), loc=(vx, main_y, main_z + .4), bevel=.04, seg=1)
    body.cyl(.035, .6, loc=(vx, main_y, main_z + .9), seg=6, bevel=0)
    valves = a.part('Valves', 'BarrelRed')
    valves.torus(.24, .03, loc=(vx, main_y, main_z + 1.15), seg=12, ring=4)
    valves.box((.46, .04, .04), loc=(vx, main_y, main_z + 1.15), bevel=0)
    # Ball valve with a lever on the small line.
    bx = 1.33
    body.sphere(small_r + .09, loc=(bx, small_y, small_z), seg=8, rings=5)
    for dx in (-.2, .2):
        body.cyl(small_r + .06, .08, loc=(bx + dx, small_y, small_z), rot=(0, R90, 0), seg=10, bevel=0)
    body.cyl(.03, .18, loc=(bx, small_y, small_z + .28), seg=6, bevel=0)
    valves.box((.5, .06, .05), loc=(bx + .2, small_y, small_z + .38), bevel=.01, seg=1)
    # Pressure gauge on a tapping.
    body.cyl(.025, .25, loc=(1.9, main_y, main_z + main_r + .1), seg=6, bevel=0)
    a.part('Gauge', 'PlasterWhite').cyl(.1, .05, loc=(1.9, main_y - .02, main_z + main_r + .28), rot=(R90, 0, 0),
                                        seg=10, bevel=.01, bseg=1)


def mesa(a):
    """Sandstone mesa (16 x 12 m, 9 m): a flat-topped butte of stacked strata over a talus apron.
    Hard beds stand out as ledges, soft beds between them are eroded back, and gullies cut the
    walls; bands alternate Sandstone and SandstoneDark."""
    rng = random.Random(17)
    H, seg = 9.0, 18
    edge = _outline(rng, ((2, 3, .13), (4, 6, .08), (7, 9, .035)))
    gully = [rng.uniform(-.06, .05) for _ in range(seg)]
    for i in rng.sample(range(seg), 3):
        gully[i] = -.1  # deep gullies cut through every bed
    # (height fraction, inset, ledge jitter): a talus apron, then near-vertical cliff bands with
    # thin notches between them and a cap rock with a chamfered rim.
    levels = [(-.012, 1.05, 0), (.1, .95, 0), (.22, .85, .01), (.24, .82, 0), (.4, .815, 0), (.43, .79, .01),
              (.47, .8, .02), (.62, .795, 0), (.64, .775, .01), (.8, .77, 0), (.83, .76, .01), (.97, .755, 0),
              (1.0, .72, 0)]
    rings = []
    for k, (f, s, lj) in enumerate(levels):
        ring = []
        for i in range(seg):
            th = i * TAU / seg + (k % 2) * .06
            r = s * edge(th) * (1 + gully[i] * (0 if k < 2 else 1) + rng.uniform(-.015, .015) + rng.uniform(-lj, lj))
            z = H * f + (rng.uniform(-.14, .14) if 0 < k < len(levels) - 1 else 0)
            ring.append((r * math.cos(th), r * math.sin(th), z))
        rings.append(ring)
    base = rings[0]
    minx, maxx = min(p[0] for p in base), max(p[0] for p in base)
    miny, maxy = min(p[1] for p in base), max(p[1] for p in base)
    kx, ky = 16.0 / (maxx - minx), 12.0 / (maxy - miny)
    ox, oy = (minx + maxx) / 2, (miny + maxy) / 2
    verts = [((x - ox) * kx, (y - oy) * ky, z) for ring in rings for x, y, z in ring]
    verts.append((-ox * kx, -oy * ky, H * 1.012))
    centre = len(verts) - 1
    faces = []
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            a0, a1 = k * seg + i, k * seg + j
            b0, b1 = a0 + seg, a1 + seg
            faces += [(a0, a1, b1), (a0, b1, b0)] if (i + k) % 2 else [(a0, a1, b0), (a1, b1, b0)]
    last = (len(rings) - 1) * seg
    faces += [(last + i, last + (i + 1) % seg, centre) for i in range(seg)]
    bands = ((.23, 'Sandstone'), (.42, 'SandstoneDark'), (.63, 'Sandstone'), (.815, 'SandstoneDark'),
             (.84, 'Sandstone'), (2.0, 'SandstoneDark'))

    def pick(c, n):
        if n.z > .72:
            return 'Sandstone'
        f = c.z / H
        return next(m for lim, m in bands if f < lim)
    _split(a, verts, faces, pick, 'Mesa', rewind=False)
    # Fallen blocks and a small eroded spire at the foot.
    scree = a.part('Scree', 'SandstoneDark', flat=True)
    scree.ico((1.1, .9, .7), loc=(3.2, -4.9, .5), sub=1, jitter=.3, seed=2.2)
    scree.ico((.8, .7, .5), loc=(-5.4, -3.2, .38), sub=1, jitter=.3, seed=5.1)
    spire = []
    for z, r in ((-.1, .75), (1.6, .6), (2.1, .42), (3.0, .45), (3.3, .3)):
        spire.append([(7.1 + r * math.cos(k * TAU / 6 + z), -4.5 + r * math.sin(k * TAU / 6 + z), z) for k in range(6)])
    a.part('Spire', 'Sandstone', flat=True).loft(spire)


# ----------------------------------------------------------------------------- snow
def snow_pine(a):
    """Snowy spruce (about 10 m): the pine's five lean tiers, each carrying a ragged snow cone
    that sits 10 cm above its needles."""
    a.part('Trunk', 'Bark').cyl(.24, 3.2, loc=(0, 0, 1.6), r2=.1, seg=7, bevel=0)
    tiers = ((2.0, 3.0, 3.2), (1.7, 2.7, 4.6), (1.4, 2.4, 6.0), (1.08, 2.1, 7.4), (.78, 2.2, 8.9))
    for i, (r, h, z) in enumerate(tiers):
        seed = i * 2.3 + .7
        a.part('Crown', 'FoliageDark' if i % 2 == 0 else 'Foliage').tier(r, h, loc=(0, 0, z), seg=10,
                                                                          droop=.22 - i * .025, jitter=.14, seed=seed)
        # Each tier only shows its outer ring under the next one, so the snow reaches 93% of it.
        k, lift = .93, .1
        a.part('Snow', 'SnowCap').tier(r * k, h * k, loc=(0, 0, z + h / 2 + lift - k * h / 2), seg=10, droop=.2,
                                       jitter=.17, seed=seed + 1.9)


def log_cabin(a):
    """Log cabin (7 x 6 m): saddle-notched log walls with protruding ends, plank gables, a steep
    slate roof under a thick snow layer, a fieldstone chimney, a porch with a snowy lean-to roof,
    red shutters and a snow-capped woodpile."""
    rng = random.Random(231)
    w, d, cy = 5.2, 4.0, .48
    x0, x1, y0, y1 = -w / 2, w / 2, cy - d / 2, cy + d / 2
    r, s, courses, base, over = .16, .29, 9, .25, .32
    a.part('Footing', 'Concrete').box((w + .3, d + .3, base + .02), loc=(0, cy, (base + .02) / 2 - .02), bevel=.04)
    logs = a.part('Logs', 'LogWood')
    for i in range(courses):
        zf, zs = base + r + i * s, base + r + (i + .5) * s
        for y in (y0, y1):
            logs.cyl(r * rng.uniform(.96, 1.04), w + 2 * over + rng.uniform(-.06, .06),
                     loc=(rng.uniform(-.03, .03), y, zf), rot=(0, R90, 0), seg=6, bevel=0)
        for x in (x0, x1):
            logs.cyl(r * rng.uniform(.96, 1.04), d + 2 * over + rng.uniform(-.06, .06),
                     loc=(x, cy + rng.uniform(-.03, .03), zs), rot=(0, R90, R90), seg=6, bevel=0)
    for x in (x0, x1):  # sill logs under the side walls
        logs.box((.26, d + .1, .2), loc=(x, cy, base + .09), bevel=0)
    top, k = base + r + (courses - .5) * s + .12, 1.05
    for y in (y0, y1):  # top plates close the gap under the eaves
        logs.box((w + .2, .3, .14), loc=(0, y, top - .045), bevel=0)
    half = d / 2 + r
    # Plank gables under the roof; their sloped edges run 5 cm into the roof.
    for x in (x0, x1):
        a.part('Gables', 'Wood').prism([(-(half + .15), 0), (half + .15, 0), (0, half * k + .15)], .22,
                                       loc=(x, cy, top - .1), axis='X', bevel=.02)
    eave, verge, t = .42, .18, .2
    length = w + 2 * over + 2 * verge
    roof_shell(a.part('Roof', 'RoofSlate'), [(-half - eave, top - eave * k), (0, top + half * k)], length, 'x', t=t,
               centre=(0, cy))
    dz = (t + .02) * math.sqrt(1 + k * k)
    roof_shell(a.part('Roof_snow', 'SnowCap'), [(-half - eave + .06, top - (eave - .06) * k + dz),
                                                 (0, top + half * k + dz)], length - .14, 'x', t=.22, centre=(0, cy),
               bevel=.07)
    # Fieldstone chimney on the east gable, capped with snow.
    zr = top + half * k + dz + .22
    stone = a.part('Chimney', 'Concrete')
    stone.box((.9, 1.0, 2.1), loc=(x1 + .45, cy, 1.05), bevel=.06, taper=(.8, .85))
    stone.box((.66, .8, zr + .7 - 1.9), loc=(x1 + .42, cy, (zr + .7 + 1.9) / 2), bevel=.05)
    a.part('Chimney_snow', 'SnowCap').box((.78, .92, .16), loc=(x1 + .42, cy, zr + .75), bevel=.06, seg=1)
    a.part('Chimney_pot', 'Armor').cyl(.1, .35, loc=(x1 + .46, cy + .1, zr + .95), seg=8, bevel=0)
    # Door, windows with red shutters.
    wy0, wy1 = y0 - .14, y1 + .14
    door(a, '-y', (-.2, wy0, base), w=1.0, h=2.05, mat='Wood', frame='Wood', step=None, lamp=True)
    for x in (-1.75, 1.45):
        window(a, rng, '-y', (x, wy0, base + 1.45), w=.8, h=.95, frame='Wood', sill='Wood', shutters='WoodRed', lit=.35)
    window(a, rng, '+y', (.6, wy1, base + 1.45), w=.8, h=.95, frame='Wood', sill='Wood', shutters='WoodRed', lit=.35)
    window(a, rng, '-x', (x0 - .14, cy - .4, base + 1.45), w=.8, h=.95, frame='Wood', sill='Wood', lit=.35)
    window(a, rng, '+x', (x1 + .14, cy - 1.25, base + 1.45), w=.6, h=.8, frame='Wood', sill='Wood', lit=.35)
    for x in (x0 - .12, x1 + .12):
        window(a, rng, '-x' if x < 0 else '+x', (x, cy - .9 if x > 0 else cy, top + .9), w=.5, h=.55, frame='Wood',
               mullion=1, sill=None, lit=.3)
    # Porch: plank deck, log posts, rails and a lean-to roof tucked under the eave, snow on its outer part.
    wood = a.part('Porch', 'Wood')
    wall_y = y0 - r
    py0 = wall_y - 1.1
    wood.box((w - .3, wall_y + .05 - py0, .2), loc=(0, (py0 + wall_y + .05) / 2, base - .11), bevel=.03, seg=1)
    wood.box((1.2, .3, .12), loc=(-.2, py0 - .15, .06), bevel=.02, seg=1)
    front = py0 - .25
    z_wall, slope = 2.5, .2
    ang = math.atan(slope)

    def z_top(y):
        return z_wall - (wall_y - y) * slope

    L = (wall_y - front) / math.cos(ang)
    ym = (wall_y + front) / 2
    a.part('Porch_roof', 'RoofSlate').box((w + .1, L, .12), loc=(0, ym, z_top(ym) - .06 / math.cos(ang)),
                                          rot=(ang, 0, 0), bevel=.02, seg=1)
    eave_y = cy - half - eave - .08
    sy0, sy1 = front + .04, eave_y
    ys = (sy0 + sy1) / 2
    nrm = Vector((0, -math.sin(ang), math.cos(ang)))
    c = Vector((0, ys, z_top(ys))) + nrm * .1
    a.part('Porch_snow', 'SnowCap').box((w - .02, (sy1 - sy0) / math.cos(ang), .16), loc=c, rot=(ang, 0, 0), bevel=.06,
                                         seg=1)
    posts = a.part('Porch_posts', 'LogWood')
    yp = py0 + .12
    zb = z_top(yp) - .12 / math.cos(ang) - .1
    for x in (-2.35, .75, 2.35):
        posts.cyl(.1, zb - base + .02, loc=(x, yp, (zb + base - .02) / 2), seg=6, bevel=0)
    posts.cyl(.11, w - .2, loc=(0, yp, zb), rot=(0, R90, 0), seg=6, bevel=0)
    for x0r, x1r in ((-2.35, -.85), (.45, 2.35)):
        wood.box((x1r - x0r, .07, .08), loc=((x0r + x1r) / 2, yp, base + .9), bevel=0)
    # Woodpile against the west gable, under a snow cap.
    pile = a.part('Woodpile', 'Wood')
    for row, count in enumerate((6, 5, 4)):
        for j in range(count):
            y = cy - .75 + (j + row * .5) * .27
            pile.cyl(.125, .62, loc=(x0 - .5, y, .13 + row * .225), rot=(0, R90, 0), seg=5, bevel=0)
    a.part('Woodpile_snow', 'SnowCap').box((.6, 1.05, .14), loc=(x0 - .5, cy - .08, .72), bevel=.06, seg=1,
                                            taper=(.8, .8))
    a.part('Chopping_block', 'LogWood').cyl(.24, .45, loc=(x0 - .55, cy + 1.45, .22), seg=7, bevel=0)
    # Snow drifts along the walls.
    drift = a.part('Drifts', 'SnowCap', flat=True)
    for x, y, rx, ry, rz in ((-2.2, y1 + .25, .9, .38, .32), (1.7, y1 + .22, 1.1, .38, .28),
                             (x1 + .45, cy + 1.45, .42, .7, .3)):
        drift.sphere((rx, ry, rz), loc=(x, y, -.02), seg=8, rings=6, cut=0.0)


def snowy_rock(rock, snow, radius, loc, sub, jitter, seed, turn=0.0, cover=.5, lift=.035):
    """Faceted boulder with a snow patch on its upward-facing upper facets, lifted `lift` off the
    rock along the vertex normals."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    rx, ry, rz = radius
    off = Vector((seed * 3.1, seed * 1.7, seed * 2.3))
    m = Matrix.Rotation(turn, 3, 'Z')
    for v in bm.verts:
        n = v.co.normalized()
        k = 1 + jitter * noise.noise(n * 1.9 + off)
        v.co = m @ Vector((n.x * rx * k, n.y * ry * k, n.z * rz * k)) + Vector(loc)
    bm.normal_update()
    bm.verts.index_update()
    rock.mesh([tuple(v.co) for v in bm.verts], [[v.index for v in f.verts] for f in bm.faces])
    zlo = min(v.co.z for v in bm.verts)
    zhi = max(v.co.z for v in bm.verts)
    cut = zhi - (zhi - zlo) * cover
    chosen = [f for f in bm.faces if f.normal.z > .62 and f.calc_center_median().z > cut]
    used = sorted({v.index for f in chosen for v in f.verts})
    remap = {j: i for i, j in enumerate(used)}
    bm.verts.ensure_lookup_table()
    verts = [tuple(bm.verts[j].co + bm.verts[j].normal * lift + Vector((0, 0, lift * .5))) for j in used]
    snow.mesh(verts, [[remap[v.index] for v in f.verts] for f in chosen])
    bm.free()


def snow_rock(a):
    """Cluster of snow-capped boulders, about 5 x 4 m."""
    rock = a.part('Rock', 'Rock', flat=True)
    snow = a.part('Snow', 'SnowCap', flat=True)
    stones = (((-.3, .25), (1.35, 1.1, 1.0), 2, .3), ((1.35, .8), (.85, .75, .75), 2, 1.1),
              ((-1.6, -.75), (.75, .7, .55), 2, 2.0), ((.65, -1.25), (.65, .55, .5), 2, .7),
              ((1.9, -.85), (.38, .34, .28), 1, 0.0), ((-2.0, 1.2), (.4, .34, .3), 1, 1.3),
              ((.45, 1.72), (.36, .3, .25), 1, .5))
    for k, ((x, y), rad, sub, turn) in enumerate(stones):
        snowy_rock(rock, snow, rad, (x, y, rad[2] * .7), sub, .28, k * 2.3 + .7, turn=turn, cover=.36)


def radar_station(a):
    """Radar station (8 x 8 m): a snow-roofed concrete block with a radome, and a 12 m red and
    white lattice mast whose search radar dish spins on the `Radar` pivot (about local Z)."""
    rng = random.Random(241)
    a.part('Pad', 'Concrete').box((7.8, 7.8, .2), loc=(0, 0, .1), bevel=.04, seg=1)
    bx0, bx1, by0, by1, H, z0 = -3.6, .9, -3.55, .15, 3.0, .18
    conc = a.part('Walls', 'Concrete')
    conc.box((bx1 - bx0, by1 - by0, H + .02), loc=((bx0 + bx1) / 2, (by0 + by1) / 2, z0 + (H + .02) / 2), bevel=.06)
    top = z0 + H
    rim(a.part('Parapet', 'Concrete'), bx0 - .04, bx1 + .04, by0 - .04, by1 + .04, top - .02, .42, .22, bevel=.03)
    a.part('Roof_snow', 'SnowCap').box((bx1 - bx0 - .36, by1 - by0 - .36, .2),
                                       loc=((bx0 + bx1) / 2, (by0 + by1) / 2, top + .06), bevel=.06, seg=1)
    door(a, '-y', (-2.55, by0, z0 + .02), w=1.0, h=2.1, mat='Steel', frame='Armor', step=None, lamp=True)
    window(a, rng, '-y', (-.9, by0, 1.95), w=1.3, h=.8, frame='Steel', mullion=1, lit=.5)
    window(a, rng, '-x', (bx0, -1.8, 1.95), w=1.1, h=.8, frame='Steel', mullion=1, lit=.4)
    window(a, rng, '+y', (-2.0, by1, 1.95), w=1.1, h=.8, frame='Steel', mullion=1, lit=.4)
    fbox(a.part('Vent', 'Steel'), '+x', (bx1, -2.6, 2.5), (1.0, .06, .6), out=.03)
    a.part('Vent', 'Steel').grille(.9, .5, loc=(bx1 + .08, -2.6, 2.5), rot=(0, 0, R90), slats=4)
    fbox(a.part('AC', 'Fuel'), '+x', (bx1, -1.0, 1.1), (.9, .5, .7), out=.27, bevel=.03)
    fbox(a.part('AC_fan', 'Rubber'), '+x', (bx1, -1.0, 1.1), (.5, .04, .5), out=.54)
    fbox(a.part('Sign', 'Hazard'), '-y', (-.9, by0, 2.75), (1.6, .05, .3), out=.03)
    # Radome on the roof.
    rx, ry = -2.3, -1.9
    a.part('Radome_base', 'Concrete').cyl(1.05, .5, loc=(rx, ry, top + .28), seg=16, bevel=.03, bseg=1)
    a.part('Radome', 'Medical').sphere(1.15, loc=(rx, ry, top + .72), seg=16, rings=10, cut=-.2)
    a.part('Beacon', 'Alloy').sphere(.07, loc=(rx, ry, top + 1.9), seg=6, rings=4)
    # Aerial on the roof.
    steel = a.part('Aerial', 'Steel')
    steel.cyl(.035, 2.6, loc=(-.1, -.5, top + 1.3), seg=6, bevel=0)
    for z, hw_ in ((top + 2.0, .45), (top + 2.4, .3)):
        steel.box((2 * hw_, .03, .03), loc=(-.1, -.5, z), bevel=0)
    # Lattice mast: five sections alternating red and white, X-braced on every face.
    mx, my = 2.2, 2.2
    levels = (.2, 2.6, 5.0, 7.3, 9.6, 11.8)

    def hw(z):
        return 1.15 + (.5 - 1.15) * (z - .2) / (11.8 - .2)

    def corners(z):
        h = hw(z)
        return [(mx - h, my - h), (mx + h, my - h), (mx + h, my + h), (mx - h, my + h)]

    for i, (za, zb) in enumerate(zip(levels, levels[1:])):
        part = a.part('Mast_red' if i % 2 == 0 else 'Mast_white', 'BarrelRed' if i % 2 == 0 else 'PlasterWhite')
        ca, cb = corners(za), corners(zb)
        for q in range(4):
            part.limb((*ca[q], za), (*cb[q], zb), .13, .13, bevel=0)
        for q in range(4):
            q2 = (q + 1) % 4
            mid = ((ca[q][0] + ca[q2][0]) / 2 - mx, (ca[q][1] + ca[q2][1]) / 2 - my)
            ln = math.hypot(*mid)
            o = (mid[0] / ln * .02, mid[1] / ln * .02)
            part.limb((*ca[q], za + .05), (*cb[q2], zb - .05), .05, .05, bevel=0)
            part.limb((ca[q2][0] + o[0], ca[q2][1] + o[1], za + .05), (cb[q][0] + o[0], cb[q][1] + o[1], zb - .05),
                      .05, .05, bevel=0)
            part.limb((*cb[q], zb), (*cb[q2], zb), .06, .06, bevel=0)
    for fx, fy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        a.part('Footings', 'Concrete').box((.5, .5, .3), loc=(mx + fx * 1.15, my + fy * 1.15, .3), bevel=.03, seg=1)
    ladder(a.part('Mast_ladder', 'Steel'), (mx, my - .2, .2), levels[-1] + .1, 0.0, width=.4, step=.5)
    # Top platform with a railing, the radar pedestal and an obstruction light.
    ztop = levels[-1]
    a.part('Platform', 'Armor').box((2.0, 2.0, .12), loc=(mx, my, ztop + .06), bevel=.02, seg=1)
    rail = a.part('Platform_rail', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            rail.box((.05, .05, 1.0), loc=(mx + sx * .96, my + sy * .96, ztop + .6), bevel=0)
    rail.tube([(mx - .96, my - .96, ztop + 1.1), (mx + .96, my - .96, ztop + 1.1), (mx + .96, my + .96, ztop + 1.1),
               (mx - .96, my + .96, ztop + 1.1), (mx - .96, my - .96, ztop + 1.1)], .03, seg=4, caps=False)
    a.part('Pedestal', 'Steel').cyl(.26, .6, loc=(mx, my, ztop + .42), seg=12, bevel=.02, bseg=1)
    a.part('Obstruction_light', 'Alloy').sphere(.09, loc=(mx + .96, my + .96, ztop + 1.2), seg=6, rings=4)
    r = a.pivot('Radar', (mx, my, ztop + .72))
    a.part('Radar_turntable', 'Armor', r).cyl(.36, .14, loc=(0, 0, .07), seg=12, bevel=.02, bseg=1)
    frame = a.part('Radar_frame', 'Steel', r)
    frame.box((.34, .34, .7), loc=(0, .12, .45), bevel=.03, seg=1)
    frame.box((.9, .5, .45), loc=(0, .62, .5), bevel=.04)
    _dish(a.part('Radar_dish', 'Medical', r), (0, .3, 1.0), 1.75, .72, depth=.42, seg=14, tilt=.2)
    for sx in (-1, 1):
        frame.limb((sx * 1.6, -.08, 1.0), (0, -1.3, 1.25), .05, .05, bevel=0)
    frame.limb((0, -.25, 1.7), (0, -1.3, 1.25), .05, .05, bevel=0)
    a.part('Radar_horn', 'Armor', r).box((.24, .28, .22), loc=(0, -1.35, 1.25), bevel=.03, seg=1)
    # Cable tray from the building to the mast, generator and fuel drums.
    t0, t1 = Vector((.3, by1 - .1)), Vector((mx - .95, my - .95))
    tv = t1 - t0
    a.part('Cable_tray', 'Steel').box((tv.length, .3, .08), loc=((t0.x + t1.x) / 2, (t0.y + t1.y) / 2, 2.75),
                                      rot=(0, 0, math.atan2(tv.y, tv.x)), bevel=0)
    gen = a.part('Generator', 'Armor')
    gen.box((1.8, 1.0, 1.1), loc=(2.3, -2.6, .75), bevel=.05)
    fbox(a.part('Generator_stripe', 'Hazard'), '-y', (2.3, -3.1, .7), (1.8, .04, .14), out=.01)
    gen.grille(.8, .5, loc=(2.55, -3.14, .95), slats=4)
    a.part('Exhaust', 'Steel').cyl(.07, .9, loc=(1.65, -2.4, 1.6), seg=8, bevel=0)
    a.part('Generator_snow', 'SnowCap').box((1.7, .9, .1), loc=(2.35, -2.6, 1.34), bevel=.04, seg=1)
    for x, y in ((3.35, -1.2), (3.3, -.5)):
        a.part('Drums', 'BarrelRed').cyl(.3, .9, loc=(x, y, .65), seg=10, bevel=.02, bseg=1)
        a.part('Drums_snow', 'SnowCap').cyl(.26, .06, loc=(x, y, 1.12), seg=10, bevel=.02, bseg=1)


def watchtower(a):
    """Wooden guard tower (4 x 4 m, about 9.5 m): four log legs leaning in, X-braced, a plank
    cabin with half walls, a snowy hipped roof, a ladder up the front and a searchlight."""
    logw = a.part('Legs', 'LogWood')
    wood = a.part('Planks', 'Wood')
    b, t, zp = 1.75, 1.3, 6.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Footings', 'Concrete').box((.5, .5, .3), loc=(sx * b, sy * b, .12), bevel=.03, seg=1)
            rod(logw, (sx * b, sy * b, .05), (sx * t, sy * t, zp), .14, seg=6, r2=.12)
            rod(logw, (sx * t, sy * t, zp - .1), (sx * t, sy * t, 8.05), .11, seg=6)

    def leg(z):
        return b + (t - b) * z / zp

    # X-braces and girts on every face; the second diagonal sits 1.5 cm further out.
    for s in (-1, 1):
        for za, zb in ((.4, 3.1), (3.1, 5.75)):
            pa, pb = leg(za), leg(zb)
            o1, o2 = s * .04, s * .07
            wood.limb((-pa, s * pa + o1, za), (pb, s * pb + o1, zb), .12, .05, bevel=0)
            wood.limb((pa, s * pa + o2, za), (-pb, s * pb + o2, zb), .12, .05, bevel=0)
            wood.limb((-pb, s * pb + o1, zb), (pb, s * pb + o1, zb), .14, .06, bevel=0)
            wood.limb((s * pa + o1, -pa, za), (s * pb + o1, pb, zb), .05, .12, bevel=0)
            wood.limb((s * pa + o2, pa, za), (s * pb + o2, -pb, zb), .05, .12, bevel=0)
            wood.limb((s * pb + o1, -pb, zb), (s * pb + o1, pb, zb), .06, .14, bevel=0)
    # Platform: joists on the top girts, a plank floor overhanging the legs, half walls with a gap
    # at the front for the ladder.
    for x in (-.7, 0, .7):
        wood.box((.14, 3.0, .2), loc=(x, 0, zp - .1), bevel=0)
    fl = 1.72
    wood.box((2 * fl, 2 * fl, .14), loc=(0, 0, zp + .07), bevel=.02, seg=1)
    wall_h = 1.05
    walls = a.part('Cabin_walls', 'Wood')
    caps = a.part('Wall_caps', 'LogWood')
    zw = zp + .14 + wall_h / 2
    zc = zp + .14 + wall_h
    for s in (-1, 1):
        walls.box((.07, 2 * fl - .14, wall_h), loc=(s * (fl - .05), 0, zw), bevel=0)
        caps.box((.14, 2 * fl, .1), loc=(s * (fl - .05), 0, zc + .04), bevel=0)
    walls.box((2 * fl, .07, wall_h), loc=(0, fl - .05, zw), bevel=0)
    caps.box((2 * fl - .3, .14, .1), loc=(0, fl - .05, zc + .05), bevel=0)
    for s in (-1, 1):
        walls.box((fl - .45, .07, wall_h), loc=(s * (fl + .45) / 2, -(fl - .05), zw), bevel=0)
        caps.box((fl - .45, .14, .1), loc=(s * (fl + .45) / 2, -(fl - .05), zc + .05), bevel=0)
    battens = a.part('Battens', 'LogWood')
    for s in (-1, 1):
        for u in (-1.0, 0.0, 1.0):
            battens.box((.03, .1, wall_h - .1), loc=(s * (fl - .005), u, zw), bevel=0)
    for u in (-1.0, 0.0, 1.0):
        battens.box((.1, .03, wall_h - .1), loc=(u, fl - .005, zw), bevel=0)
    for u in (-1.2, 1.2):
        battens.box((.1, .03, wall_h - .1), loc=(u, -(fl - .005), zw), bevel=0)
    # Hipped roof with a snow cap sitting 7 cm above the slates.
    zr, rr, rh = 8.05, 2.75, 1.25
    roof = a.part('Roof', 'RoofSlate')
    roof.cyl(rr, rh, loc=(0, 0, zr + rh / 2), r2=.05, seg=4, rot=(0, 0, math.pi / 4), bevel=0)
    roof.cyl(rr, .1, loc=(0, 0, zr - .04), seg=4, rot=(0, 0, math.pi / 4), bevel=0)
    face_slope = rh / (rr * math.cos(math.pi / 4))
    lift = .07 / math.cos(math.atan(face_slope))
    ks = 2.3 / rr
    a.part('Roof_snow', 'SnowCap').tier(rr * ks, rh * ks, loc=(0, 0, zr + rh + lift - rh * ks / 2), seg=4, droop=.08,
                                        jitter=.06, seed=math.pi / 4)
    a.part('Finial', 'Armor').cyl(.04, .5, loc=(0, 0, zr + rh + .1), seg=6, bevel=0)
    # Ladder up the front to the gap in the half wall.
    lad = a.part('Ladder', 'Wood')
    ya, yb, zt = -2.05, -fl - .02, zp + 1.0
    for sx in (-.3, .3):
        lad.limb((sx, ya, .02), (sx, yb, zt), .07, .07, bevel=0)
    for i in range(16):
        z = .35 + i * .4
        lad.box((.6, .05, .05), loc=(0, ya + (yb - ya) * z / zt, z), bevel=0)
    # Searchlight on the front right corner.
    lx, ly, lz = fl - .2, -fl + .05, zc + .1
    light = a.part('Searchlight', 'Armor')
    light.cyl(.06, .25, loc=(lx, ly, lz + .12), seg=6, bevel=0)
    light.cyl(.2, .4, loc=(lx, ly - .05, lz + .38), rot=(R90 + .25, 0, 0), seg=10, bevel=.02, bseg=1)
    a.part('Searchlight_lens', 'Lamp').cyl(.17, .04, loc=(lx, ly - .26, lz + .43), rot=(R90 + .25, 0, 0), seg=10,
                                            bevel=0)
    # Snow drifts around three of the footings.
    drift = a.part('Drifts', 'SnowCap', flat=True)
    for x, y in ((-1.55, 1.55), (1.55, 1.55), (1.55, -1.55)):
        drift.sphere((.45, .42, .22), loc=(x, y, -.02), seg=8, rings=6, cut=0.0)


# name: (builder, Asset options)
BUILDERS = {
    'adobe_house': (adobe_house, dict(ao_distance=1.5, grime_height=.8)),
    'adobe_large': (adobe_large, dict(ao_distance=1.8, grime_height=.9)),
    'market_stall': (market_stall, dict(ao_distance=.8, grime_height=.4)),
    'palm': (palm, dict(ao_distance=1.2, grime_height=.6)),
    'cactus': (cactus, dict(ao_distance=.7, grime_height=.4)),
    'oil_pump': (oil_pump, dict(ao_distance=.9, grime_height=.5)),
    'refinery_tower': (refinery_tower, dict(ao_distance=1.6, grime_height=1.0)),
    'storage_tank': (storage_tank, dict(ao_distance=1.8, grime_height=1.0)),
    'pipeline': (pipeline, dict(ao_distance=.7, grime_height=.5)),
    'mesa': (mesa, dict(ao_distance=3.0, ao_strength=.75, grime_height=1.5)),
    'snow_pine': (snow_pine, dict(ao_distance=1.2, grime_height=.6)),
    'log_cabin': (log_cabin, dict(ao_distance=1.4, grime_height=.8)),
    'snow_rock': (snow_rock, dict(ao_distance=1.0, grime_height=.3)),
    'radar_station': (radar_station, dict(ao_distance=1.4, grime_height=.8)),
    'watchtower': (watchtower, dict(ao_distance=1.0, grime_height=.6)),
}
