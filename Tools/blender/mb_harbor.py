"""Machine Brigade harbour and industrial map pieces built with frontier_kit.

Container docks, a rail yard and a factory district: shipping containers, a rail-mounted gantry
crane, a brick factory with a saw-tooth roof, rail wagons, a dock edge with bollards, an office
block, a street light and a jersey barrier.

Conventions follow mb_town.py: Blender X = width, Y = depth, metres, +Z up; the front faces -Y
and origins sit on the ground at the footprint centre. Touching parts overlap or stand at least
1 cm apart, never face to face (coplanar faces z-fight). Corrugated steel is an open sheet of
trapezoidal ribs 1 cm in front of a closed core, so only the visible faces cost triangles.
Container bodies use one material (ContainerRed) so the game can swap in other colours.
"""
import math
import random

from mb_town import NORMAL, TANGENT, door, fbox, letters, pane, slide, window

R90 = math.pi / 2
ALONG_X = (0, R90, 0)  # cylinder axis along X
ALONG_Y = (R90, 0, 0)  # cylinder axis along Y


# ----------------------------------------------------------------------------- helpers
def _trapezoids(length, pitch, depth):
    """(u, offset) outline of trapezoidal corrugations across `length`, centred on u = 0."""
    n = max(1, round(length / pitch))
    step = length / n
    prof = []
    for i in range(n):
        u = -length / 2 + i * step
        prof += [(u, 0.0), (u + step * .12, depth), (u + step * .5, depth), (u + step * .62, 0.0)]
    return prof + [(length / 2, 0.0)]


def corrugated_wall(part, face, p, length, z0, z1, pitch=.4, depth=.05):
    """Open sheet of vertical corrugations on a wall. p = (x, y) is the middle of the sheet's back
    plane; the ribs stand out along the face's outward normal. Only the outer faces are built."""
    nx, ny = NORMAL[face]
    tx, ty = TANGENT[face]
    verts = []
    for u, o in _trapezoids(length, pitch, depth):
        x, y = p[0] + tx * u + nx * o, p[1] + ty * u + ny * o
        verts += [(x, y, z0), (x, y, z1)]
    part.mesh(verts, [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(len(verts) // 2 - 1)])


def corrugated_roof(part, x0, x1, y0, y1, z, pitch=.5, depth=.035):
    """Open horizontal sheet facing up, its corrugations running along Y."""
    verts = []
    for u, o in _trapezoids(x1 - x0, pitch, depth):
        x = (x0 + x1) / 2 + u
        verts += [(x, y0, z + o), (x, y1, z + o)]
    part.mesh(verts, [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(len(verts) // 2 - 1)])


def yz_slab(part, a, b, length, thick, lift=0.0, cx=0.0, bevel=0.0, seg=1):
    """Box `length` long along X over the (y, z) segment a -> b, `thick` thick on the segment's
    left side (the outside when a -> b runs with the outside on the left) and `lift` off it."""
    dy, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dy, dz)
    ny, nz = -dz / L, dy / L
    k = thick / 2 + lift
    part.box((length, L, thick), loc=(cx, (a[0] + b[0]) / 2 + ny * k, (a[1] + b[1]) / 2 + nz * k),
             rot=(math.atan2(dz, dy), 0, 0), bevel=bevel, seg=seg)


def lerp2(a, b, t):
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


# ----------------------------------------------------------------------------- containers
def container_body(a, mat, z0=0.0, dx=0.0, flip=False, tag=''):
    """ISO 20 ft box (6.0 x 2.44 x 2.62 m), doors at the +X end (-X when flipped): corrugated
    sides, end, doors and roof around a closed core, frame rails and corner posts, dark corner
    castings and steel locking bars. Everything painted is `mat`."""
    body = a.part('Body' + tag, mat)
    cast = a.part('Castings' + tag, 'Armor')
    gear = a.part('Door_gear' + tag, 'Steel')
    H, hl, hw = 2.62, 3.0, 1.22
    fx = -1 if flip else 1

    def bx(part, size, x, y, z):
        part.box(size, loc=(dx + fx * x, y, z0 + z), bevel=0)

    back, front = ('+x', '-x') if flip else ('-x', '+x')
    bx(body, (5.8, 2.2, 2.32), 0, 0, 1.31)  # core: x +-2.90, y +-1.10, z .15 .. 2.47
    for s in (-1, 1):
        corrugated_wall(body, '+y' if s > 0 else '-y', (dx, s * 1.11), 5.74, z0 + .19, z0 + 2.46)
    corrugated_wall(body, back, (dx - fx * 2.91, 0), 2.2, z0 + .19, z0 + 2.46, pitch=.37)
    corrugated_roof(body, dx - 2.9, dx + 2.9, -1.1, 1.1, z0 + 2.48, pitch=.55)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx(body, (.15, .13, H - .24), sx * (hl - .085), sy * (hw - .075), H / 2)  # corner posts
            for z in (.065, H - .065):
                bx(cast, (.18, .16, .13), sx * (hl - .09), sy * (hw - .08), z)
    for s in (-1, 1):
        bx(body, (5.78, .11, .19), 0, s * (hw - .075), .115)  # side rails, 1 cm inside the posts
        bx(body, (5.78, .11, .16), 0, s * (hw - .075), H - .1)
        bx(body, (.115, 2.17, .19), s * (hl - .0775), 0, .115)  # end rails
        bx(body, (.115, 2.17, .16), s * (hl - .0775), 0, H - .1)
    # Doors: two corrugated leaves with four locking bars and their handles.
    for s in (-1, 1):
        bx(body, (.05, 1.09, 2.25), hl - .065, s * .55, 1.325)
        corrugated_wall(body, front, (dx + fx * (hl - .03), s * .5475), 1.0, z0 + .26, z0 + 2.38, pitch=.25,
                        depth=.025)
    for y in (-.8, -.3, .3, .8):
        bx(gear, (.04, .04, 2.16), hl - .01, y, 1.32)
        bx(gear, (.04, .3, .05), hl + .02, y - math.copysign(.14, y), 1.15)


def container(a):
    """Standard 20 ft shipping container (6 x 2.5 m, 2.62 m)."""
    container_body(a, 'ContainerRed')


def container_stack(a):
    """Two containers stacked (6 x 2.5 m, 5.25 m): red below, blue above, doors at opposite ends."""
    container_body(a, 'ContainerRed')
    container_body(a, 'ContainerBlue', z0=2.63, dx=.06, flip=True, tag='_top')


# ----------------------------------------------------------------------------- gantry crane
def gantry_crane(a):
    """Rail-mounted gantry crane (18 x 10 m, 18.7 m): two portal frames on four bogies carry twin
    box girders; a trolley with a side cab lowers a container spreader (its underside at 7.5 m). No
    structure spans between the legs below 10 m, so vehicles pass under the crane both ways; striped
    leg bases mark the four blockers."""
    yellow = a.part('Frame', 'CraneYellow')
    dark = a.part('Machinery', 'Armor')
    steel = a.part('Rails', 'Steel')
    under = a.part('Bogies', 'Undercarriage')
    wheel = a.part('Wheels', 'Armor')
    stripe = a.part('Leg_paint', 'SafetyStripe')
    black = a.part('Leg_bands', 'Charred')
    LX, LY = 8.55, 3.9  # leg foot centres
    # Rails on concrete beds under each leg line: the crane travels along Y.
    for sx in (-1, 1):
        a.part('Rail_beds', 'Concrete').box((1.1, 10.8, .08), loc=(sx * LX, 0, .04), bevel=.02, seg=1)
        steel.box((.14, 10.7, .14), loc=(sx * LX, 0, .14), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * LX, sy * LY
            under.box((.36, 2.7, .62), loc=(x, y, .95), bevel=.03, seg=1)
            for dy in (-.85, .85):
                wheel.cyl(.42, .8, loc=(x, y + dy, .625), rot=ALONG_X, seg=10, bevel=0)
            yellow.box((1.05, 1.5, .5), loc=(x, y, 1.45), bevel=.04, seg=1)
            # Striped pedestal, then a tapered box leg leaning in towards the portal centre.
            stripe.box((.92, 1.12, 2.6), loc=(x, y, 2.98), bevel=.04, seg=1)
            for k in range(3):
                black.box((.95, 1.15, .36), loc=(x, y, 2.05 + k * .8), bevel=0)
            yellow.limb((x, y, 4.2), (x, sy * 3.5, 13.66), .82, 1.0, bevel=.05, seg=2, taper=(1.22, 1.3))
            yellow.limb((x, sy * 3.35, 10.4), (x, sy * 1.3, 13.8), .5, .45, bevel=.03, seg=1)  # knee brace
    for sx in (-1, 1):
        yellow.box((1.2, 8.8, 1.3), loc=(sx * LX, 0, 14.25), bevel=.06, seg=2)  # portal sill z 13.6 .. 14.9
        yellow.box((.5, 2.2, 1.2), loc=(sx * 8.98, 0, 15.75), bevel=.03, seg=1)  # girder end tie
    walk = a.part('Walkways', 'Armor')
    for sy in (-1, 1):
        yellow.box((18.5, .9, 1.7), loc=(0, sy * 1.5, 15.7), bevel=.06, seg=2)  # girder z 14.85 .. 16.55
        steel.box((16.2, .14, .14), loc=(1.0, sy * 1.5, 16.61), bevel=0)  # trolley rail
        walk.box((17.4, .9, .06), loc=(0, sy * 2.39, 14.97), bevel=0)
        for i in range(9):
            yellow.box((.05, .05, 1.12), loc=(-8.6 + i * 2.15, sy * 2.8, 15.54), bevel=0)
        yellow.box((17.3, .07, .06), loc=(0, sy * 2.8, 16.08), bevel=0)
        yellow.box((17.3, .07, .05), loc=(0, sy * 2.8, 15.55), bevel=0)
    lamp = a.part('Floodlights', 'Lamp')
    for sy in (-1, 1):
        for x in (-5.5, 0, 5.5):
            lamp.box((.5, .36, .14), loc=(x, sy * 1.5, 14.8), bevel=.02, seg=1)
    # Trolley: frame on four wheels, machinery house, exposed hoist drum.
    tx = 2.4
    for dx in (-1.1, 1.1):
        for sy in (-1, 1):
            wheel.cyl(.22, .16, loc=(tx + dx, sy * 1.5, 16.89), rot=ALONG_Y, seg=10, bevel=0)
    yellow.box((3.1, 4.3, .45), loc=(tx, 0, 17.2), bevel=.04, seg=1)  # z 16.975 .. 17.425
    yellow.box((2.8, 3.3, 1.05), loc=(tx - .1, .3, 17.94), bevel=.05, seg=2)  # house z 17.415 .. 18.465
    a.part('Trolley_roof', 'Corrugated').box((3.0, 3.5, .08), loc=(tx - .1, .3, 18.49), bevel=.02, seg=1)
    dark.cyl(.34, 2.3, loc=(tx, -1.75, 17.77), rot=ALONG_X, seg=12, bevel=.02, bseg=1)
    for sx in (-1, 1):
        dark.box((.12, .8, .5), loc=(tx + sx * 1.23, -1.75, 17.65), bevel=0)  # drum bearings
    fbox(dark, '-y', (tx - .9, -1.35, 17.95), (.8, .06, .9), out=.02)  # house door
    fbox(a.part('Vents', 'Steel'), '+x', (tx + 1.3, .3, 17.95), (1.6, .06, .5), out=.02)
    for x, y in ((tx - 1.45, -1.3), (tx + 1.25, 1.9)):
        a.part('Beacons', 'Alloy').box((.14, .14, .16), loc=(x, y, 18.6), bevel=.03, seg=1)
    # Hoist ropes down between the girders to the headblock and a container spreader.
    ropes = a.part('Ropes', 'Undercarriage')
    for dx in (-.8, .8):
        for dy in (-.45, .45):
            ropes.box((.05, .05, 8.45), loc=(tx + dx, dy, 12.8), bevel=0)  # z 8.575 .. 17.025
    yellow.box((1.9, 1.2, .5), loc=(tx, 0, 8.35), bevel=.04, seg=1)  # headblock z 8.1 .. 8.6
    for dx in (-.8, .8):
        dark.cyl(.3, .14, loc=(tx + dx, 0, 8.6), rot=ALONG_Y, seg=10, bevel=0)  # sheaves
    yellow.box((.7, 6.0, .42), loc=(tx, 0, 7.92), bevel=.03, seg=1)  # telescopic beam z 7.71 .. 8.13
    for sy in (-1, 1):
        yellow.box((2.44, .4, .4), loc=(tx, sy * 2.85, 7.9), bevel=.03, seg=1)
        for sx in (-1, 1):
            dark.box((.3, .3, .32), loc=(tx + sx * 1.08, sy * 2.92, 7.62), bevel=.02, seg=1)  # twistlocks
    # Operator cab hung outside the front girder from two outriggers.
    cx, cy = tx + .4, -3.85
    for dx in (-.6, .6):
        yellow.box((.25, 2.0, .3), loc=(cx + dx, -3.0, 17.2), bevel=.02, seg=1)
        yellow.box((.2, .2, .95), loc=(cx + dx, cy, 16.755), bevel=0)
    yellow.box((1.8, 1.7, 2.0), loc=(cx, cy, 15.3), bevel=.06, seg=2)  # z 14.3 .. 16.3, y -4.7 .. -3.0
    dark.box((1.9, 1.8, .1), loc=(cx, cy, 16.33), bevel=.02, seg=1)
    glass = a.part('Cab_glass', 'Glass')
    fbox(glass, '-y', (cx, cy - .85, 15.45), (1.5, .04, 1.1), out=.015)
    for face, sx in (('-x', -1), ('+x', 1)):
        fbox(glass, face, (cx + sx * .9, cy, 15.45), (1.3, .04, 1.1), out=.015)
    # Electrical house on the far end of the girders.
    ex = -8.2
    a.part('E_house', 'MetalSheet').box((2.0, 4.4, 2.1), loc=(ex, 0, 17.55), bevel=.04, seg=1)  # z 16.5 .. 18.6
    a.part('E_house_roof', 'Corrugated').box((2.2, 4.6, .08), loc=(ex, 0, 18.62), bevel=.02, seg=1)
    fbox(dark, '+x', (ex + 1.0, -1.1, 17.55), (.9, .06, 1.9), out=.02)
    fbox(a.part('Vents', 'Steel'), '+x', (ex + 1.0, .9, 17.9), (1.4, .06, .6), out=.02)
    fbox(a.part('Vents', 'Steel'), '-y', (ex, -2.2, 17.9), (1.2, .06, .6), out=.02)
    # Access ladder up the front of the front-right leg to the sill.
    for dx in (-.22, .22):
        yellow.limb((LX + dx, -4.68, 1.8), (LX + dx, -4.56, 15.6), .05, .05, bevel=0)
    for i in range(18):
        z = 2.2 + i * .74
        yellow.box((.44, .04, .04), loc=(LX, -4.68 + .12 * (z - 1.8) / 13.8, z), bevel=0)
    for z in (5.0, 9.0, 12.5):
        ladder_y = -4.68 + .12 * (z - 1.8) / 13.8
        leg_face = -(3.9 - .4 * (z - 4.2) / 9.46) - (.5 + .15 * (z - 4.2) / 9.46) + .03
        yellow.box((.44, leg_face - ladder_y, .06), loc=(LX, (leg_face + ladder_y) / 2, z), bevel=0)  # stand-offs


# ----------------------------------------------------------------------------- factory
def factory(a):
    """Brick industrial hall (16 x 12 m) under a four-bay saw-tooth north-light roof whose glazed
    faces look to the front, a 20 m round brick chimney at the back-right corner, big sliding
    doors, steel windows, a boiler tank and steam pipes along the right gable."""
    rng = random.Random(151)
    x0, x1, y0, y1 = -7.9, 6.1, -5.5, 5.5
    w, cx = x1 - x0, (x0 + x1) / 2
    H, n, h, s = 6.2, 4, 1.9, .3
    t = (y1 - y0) / n
    brick = a.part('Walls', 'Brick')
    conc = a.part('Trim', 'Concrete')
    conc.box((w + .16, y1 - y0 + .16, .5), loc=(cx, 0, .25), bevel=.04)
    prof = [(y0, 0), (y1, 0), (y1, H)]
    for k in reversed(range(n)):
        yk = y0 + k * t
        prof += [(yk + s, H + h), (yk, H)]
    brick.prism(prof, w, loc=(cx, 0, 0), axis='X', bevel=.05)
    # Roof: a corrugated slab per tooth with standing seams, glazed steep faces, valley gutters.
    roof = a.part('Roof', 'Corrugated')
    seams = a.part('Roof_seams', 'Steel')
    frame = a.part('Glazing_frames', 'Armor')
    gutter = a.part('Gutters', 'Asphalt')
    for k in range(n):
        yk = y0 + k * t
        ridge, valley = (yk + s, H + h), (yk + t, H)
        L = math.hypot(t - s, h)
        a0 = lerp2(ridge, valley, -.1 / L)
        a1 = lerp2(ridge, valley, 1 + (.35 if k == n - 1 else -.06) / L)
        yz_slab(roof, a0, a1, w + .3, .12, lift=-.02, cx=cx, bevel=.02)
        for i in range(10):
            yz_slab(seams, lerp2(a0, a1, .02), lerp2(a0, a1, .98), .06, .05, lift=.09, cx=x0 + .6 + i * (w - 1.2) / 9)
        # Steep face from (yk, H) to the ridge: frame band and panes (some lit).
        b0, b1 = lerp2((yk, H), ridge, .12), lerp2((yk, H), ridge, .93)
        yz_slab(frame, b0, b1, w - .7, .05, lift=.005, cx=cx)
        pw = (w - 1.0) / 6
        for i in range(6):
            yz_slab(pane(a, rng, .08), lerp2(b0, b1, .06), lerp2(b0, b1, .94), pw - .14, .04, lift=.045,
                    cx=x0 + .5 + (i + .5) * pw)
        if k:
            gutter.box((w + .1, .5, .2), loc=(cx, yk - .08, H + .06), bevel=.02, seg=1)
    conc.box((w + .24, .5, .26), loc=(cx, y0 + .12, H - .05), bevel=.03, seg=1)  # front cornice
    a.part('Gutters', 'Steel').box((w + .4, .22, .18), loc=(cx, y1 + .5, H - .32), bevel=.02, seg=1)
    # Corner piers and pilasters.
    for px, py in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        brick.box((.7, .7, H + .3), loc=(px, py, (H + .3) / 2), bevel=.04)
        conc.box((.86, .86, .16), loc=(px, py, H + .33), bevel=0)
    for face, p in (('-y', (-1.55, y0)), ('-y', (1.15, y0)), ('-y', (3.815, y0)), ('+y', (-4.7, y1)),
                    ('+y', (-1.9, y1)), ('+y', (.9, y1)), ('+y', (3.525, y1)), ('+x', (x1, -2.4)), ('+x', (x1, .6)),
                    ('-x', (x0, -3.05)), ('-x', (x0, 1.55))):
        fbox(brick, face, (p[0], p[1], H / 2), (.55, .22, H - .1), out=.08)

    def tall_window(face, p, zc=3.3, wd=1.7, ht=3.1):
        window(a, rng, face, (p[0], p[1], zc), w=wd, h=ht, frame='Armor', lit=.25, mullion=2)
        fbox(conc, face, (p[0], p[1], zc + ht / 2 + .2), (wd + .5, .16, .26), out=.07)

    for x in (-.3, 2.6):
        tall_window('-y', (x, y0))
    for x in (-6.1, -3.3, -.5, 2.3, 4.75):
        tall_window('+y', (x, y1))
    for y in (-3.9, -.9):
        tall_window('+x', (x1, y), zc=3.7, ht=2.6)
    tall_window('+x', (x1, 2.05), wd=1.4)
    for y in (-4.3, 2.8):
        tall_window('-x', (x0, y))
    door(a, '-y', (5.0, y0, .5), w=1.1, h=2.2, mat='Steel', frame='Concrete', lamp=False)

    def big_door(face, p, wd, ht):
        fbox(a.part('Big_doors', 'RoofGreen'), face, (p[0], p[1], ht / 2), (wd, .08, ht), out=.06)
        for j in range(5):
            fbox(a.part('Door_ribs', 'Armor'), face, (p[0], p[1], .6 + j * (ht - 1.0) / 4), (wd - .04, .04, .08),
                 out=.11)
        for sd in (-1, 1):
            fbox(a.part('Jambs', 'Hazard'), face, slide(face, (p[0], p[1], ht / 2), sd * (wd / 2 + .12)), (.24, .14, ht),
                 out=.05)
        fbox(conc, face, (p[0], p[1], ht + .2), (wd + .7, .18, .4), out=.07, bevel=.02)
        fbox(a.part('Door_track', 'Armor'), face, (p[0], p[1], ht + .5), (wd + .6, .12, .12), out=.1)
        fbox(a.part('Door_lamp', 'Lamp'), face, slide(face, (p[0], p[1], ht + .75), wd / 2 - .3), (.3, .14, .18),
             out=.1, bevel=.03)

    big_door('-y', (-4.4, y0), 4.4, 4.6)
    big_door('-x', (x0, -.7), 3.4, 4.2)
    # Round brick chimney on a square base at the back-right corner.
    chx, chy = 7.0, 4.35
    conc.box((2.2, 2.2, .4), loc=(chx, chy, .2), bevel=.03)
    brick.box((2.0, 2.0, 3.6), loc=(chx, chy, 1.8), bevel=.04)
    conc.box((2.2, 2.2, .25), loc=(chx, chy, 3.66), bevel=.03, seg=1)
    brick.lathe([(.92, 3.5), (.62, 19.35), (.75, 19.45), (.75, 19.95), (.66, 20.0)], loc=(chx, chy, 0), seg=12)
    for z in (7.0, 11.0, 15.0):
        r = .92 + (.62 - .92) * (z - 3.5) / 15.85
        a.part('Chimney_bands', 'Armor').cyl(r + .02, .14, loc=(chx, chy, z), seg=12, bevel=0)
    soot = a.part('Soot', 'Charred')
    soot.cyl(.765, .45, loc=(chx, chy, 19.72), seg=12, bevel=0)
    soot.cyl(.5, .03, loc=(chx, chy, 20.01), seg=12, bevel=0)  # flue opening
    fbox(a.part('Chimney_door', 'Armor'), '+x', (chx + 1.0, chy - .2, .95), (.8, .06, 1.1), out=.02)
    # Boiler tank on saddles against the right gable, with steam pipes into the hall and chimney.
    tank_y = -2.5
    a.part('Boiler', 'Fuel').lathe([(0, -2.1), (.5, -2.05), (.72, -1.9), (.75, -1.7), (.75, 1.7), (.72, 1.9), (.5, 2.05),
                                    (0, 2.1)], loc=(7.1, tank_y, 1.25), rot=ALONG_Y, seg=14)
    for y in (tank_y - 1.1, tank_y + 1.1):
        conc.box((1.4, .4, .62), loc=(7.1, y, .31), bevel=.03, seg=1)
    pipes = a.part('Pipes', 'Steel')
    pipes.tube([(7.1, tank_y - .6, 1.9), (7.1, tank_y - .6, 4.65), (6.02, tank_y - .6, 4.65)], .12, seg=8)
    pipes.tube([(6.6, -4.9, .02), (6.6, -4.9, 5.25), (6.6, 3.5, 5.25)], .09, seg=8)
    pipes.tube([(6.7, tank_y + .8, 1.8), (6.7, tank_y + .8, 2.6), (6.7, .9, 2.6), (6.7, .9, .02)], .07, seg=6)
    for y in (-3.9, -1.4, 1.1, 2.9):
        a.part('Pipe_brackets', 'Armor').box((.57, .08, .08), loc=(6.335, y, 5.25), bevel=0)
    a.part('Valve', 'BarrelRed').torus(.18, .03, loc=(7.1, tank_y - .78, 3.4), rot=ALONG_Y, seg=10, ring=4)
    # Roof ventilators near the ridges.
    for x, k in ((-4.6, 1), (.4, 2), (3.8, 0)):
        yk = y0 + k * t
        vy, vz = lerp2((yk + s, H + h), (yk + t, H), .35)
        pipes.cyl(.22, .9, loc=(x, vy, vz + .35), seg=8, bevel=0)
        pipes.cyl(.34, .3, loc=(x, vy, vz + .9), r2=.08, seg=8, bevel=0)


# ----------------------------------------------------------------------------- rail wagons
def wagon_underframe(a, L=10.3):
    """Underframe on two bogies (x = +-3.45) for an 11 m wagon laid along X: sole bars and red
    headstocks at buffer height, buffers and couplers at both ends, brake cylinder, steps."""
    under = a.part('Underframe', 'Undercarriage')
    wheel = a.part('Wheels', 'Armor')
    steel = a.part('Buffers', 'Steel')
    hl = L / 2
    for bx in (-3.45, 3.45):
        for ax in (-.9, .9):
            for sy in (-1, 1):
                wheel.cyl(.46, .14, loc=(bx + ax, sy * .75, .46), rot=ALONG_Y, seg=12, bevel=0)
                under.box((.34, .2, .3), loc=(bx + ax, sy * .95, .5), bevel=0)  # axle boxes
        for sy in (-1, 1):
            under.box((2.6, .12, .4), loc=(bx, sy * 1.02, .62), bevel=.02, seg=1)  # bogie side frames
            under.box((.46, .16, .3), loc=(bx, sy * 1.1, .72), bevel=0)  # spring nest
        under.box((.5, 2.1, .3), loc=(bx, 0, .84), bevel=0)  # bolster
        under.box((.42, 2.4, .3), loc=(bx, 0, 1.09), bevel=0)  # body cross member
    for sy in (-1, 1):
        under.box((L - .04, .22, .38), loc=(0, sy * 1.25, 1.06), bevel=.02, seg=1)  # sole bars z .87 .. 1.25
    head = a.part('Headstocks', 'BarrelRed')
    for sx in (-1, 1):
        head.box((.24, 2.9, .42), loc=(sx * (hl - .12), 0, 1.06), bevel=.03, seg=1)
        for sy in (-1, 1):
            steel.cyl(.12, .34, loc=(sx * (hl + .15), sy * .88, 1.06), rot=ALONG_X, seg=8, bevel=0)
            steel.cyl(.21, .06, loc=(sx * (hl + .33), sy * .88, 1.06), rot=ALONG_X, seg=10, bevel=0)
            steel.box((.3, .22, .04), loc=(sx * (hl - .35), sy * 1.38, .52), bevel=0)  # step
            steel.box((.04, .04, .36), loc=(sx * (hl - .35), sy * 1.46, .71), bevel=0)
        a.part('Couplers', 'Armor').box((.4, .16, .16), loc=(sx * (hl + .14), 0, 1.0), bevel=.02, seg=1)
    under.cyl(.22, 1.1, loc=(0, .45, .72), rot=ALONG_X, seg=10, bevel=0)  # brake cylinder
    under.cyl(.28, 1.4, loc=(-1.1, -.4, .72), rot=ALONG_X, seg=10, bevel=0)  # air reservoir


def rail_tanker(a):
    """Railway tank wagon (11 x 3 m, 4.6 m): silver tank on saddles with straps, top dome and
    railed walkway, yellow ladders up both sides and hazard placards."""
    wagon_underframe(a)
    zc, r = 2.6, 1.25
    a.part('Tank', 'Fuel').lathe([(0, -4.8), (.75, -4.74), (1.1, -4.55), (r, -4.3), (r, 4.3), (1.1, 4.55), (.75, 4.74),
                                  (0, 4.8)], loc=(0, 0, zc), rot=ALONG_X, seg=20)
    under = a.part('Underframe', 'Undercarriage')
    straps = a.part('Tank_straps', 'Armor')
    for x in (-3.45, 3.45):
        under.box((.4, 1.4, .42), loc=(x, 0, 1.41), bevel=.02, seg=1)  # saddles
        straps.cyl(r + .03, .14, loc=(x, 0, zc), rot=ALONG_X, seg=20, bevel=0)
    a.part('Tank', 'Fuel').cyl(.42, .4, loc=(0, 0, zc + r + .15), seg=12, bevel=.02, bseg=1)  # dome
    a.part('Dome_lid', 'Steel').cyl(.47, .06, loc=(0, 0, zc + r + .37), seg=12, bevel=0)
    a.part('Outlet', 'Steel').cyl(.12, .3, loc=(0, 0, zc - r - .05), seg=8, bevel=0)
    a.part('Walkway', 'Armor').box((2.2, 1.1, .05), loc=(0, 0, zc + r + .05), bevel=0)
    rail = a.part('Handrails', 'Hazard')
    zw = zc + r + .075
    for sx in (-1, 1):
        for sy in (-1, 1):
            rail.box((.03, .03, .65), loc=(sx * 1.06, sy * .52, zw + .32), bevel=0)
        rail.box((.05, 1.12, .05), loc=(sx * 1.06, 0, zw + .63), bevel=0)
    for sy in (-1, 1):
        rail.box((2.13, .05, .05), loc=(0, sy * .52, zw + .64), bevel=0)
        # Ladder: upright beside the tank from the sole bar, then leaning in to the walkway.
        for dx in (-.2, .2):
            rail.limb((.7 + dx, sy * 1.42, 1.25), (.7 + dx, sy * 1.42, 3.3), .045, .045, bevel=0)
            rail.limb((.7 + dx, sy * 1.42, 3.3), (.7 + dx, sy * .62, zw), .025, .045, bevel=0)
        for i in range(6):
            rail.box((.4, .025, .025), loc=(.7, sy * 1.42, 1.55 + i * .33), bevel=0)
        for f in (.35, .7):
            rail.box((.4, .025, .025), loc=(.7, sy * (1.42 - .8 * f), 3.3 + (zw - 3.3) * f), bevel=0)
        placard = a.part('Placards', 'BarrelRed')
        placard.box((.4, .03, .4), loc=(-3.0, sy * (r + .005), zc + .1), rot=(0, math.pi / 4, 0), bevel=0)
        a.part('Placard_plates', 'PlasterWhite').box((.5, .03, .2), loc=(-3.0, sy * (math.sqrt(r * r - .25) + .01),
                                                                          zc - .5), rot=(-sy * .42, 0, 0), bevel=0)


def rail_boxcar(a):
    """Railway boxcar (11 x 3 m, 4.25 m): ribbed oxide-red body under a galvanised arched roof, a
    sliding door on each side (the front one half open), corner ladders."""
    wagon_underframe(a)
    body = a.part('Body', 'RailBrown')
    body.box((10.3, 2.9, 2.75), loc=(0, 0, 2.595), bevel=.04, seg=1)  # z 1.22 .. 3.97, y +-1.45
    arc = [(1.5, .08), (1.1, .2), (.55, .28), (0, .3), (-.55, .28), (-1.1, .2), (-1.5, .08)]
    a.part('Roof', 'MetalSheet').prism([(-1.5, 0), (1.5, 0)] + arc, 10.42, loc=(0, 0, 3.94), axis='X', bevel=.02)
    ribs = a.part('Ribs', 'RailBrown')
    for sy, face in ((-1, '-y'), (1, '+y')):
        for x in (1.7, 2.55, 3.4, 4.25, 4.95):
            for sx in (-1, 1):
                fbox(ribs, face, (sx * x, sy * 1.45, 2.6), (.1, .08, 2.6), out=.03)
    for sx, face in ((-1, '-x'), (1, '+x')):
        for z in (1.9, 2.6, 3.3):
            fbox(ribs, face, (sx * 5.15, 0, z), (2.7, .08, .14), out=.03)
    # Sliding doors: dark opening, door panel on an outer track (front half open, back closed).
    for sy, face, dx in ((-1, '-y', 1.1), (1, '+y', 0.0)):
        y = sy * 1.45
        fbox(a.part('Door_opening', 'Charred'), face, (0, y, 2.575), (2.8, .02, 2.45), out=.015)
        door_part = a.part('Doors', 'RailBrown')
        fbox(door_part, face, (dx, y, 2.55), (2.85, .06, 2.55), out=.105, bevel=.015)
        for u in (-.9, 0, .9):
            fbox(door_part, face, (dx + u, y, 2.55), (.12, .04, 2.5), out=.14)
        fbox(a.part('Door_gear', 'Steel'), face, (dx - 1.25, y, 2.4), (.06, .05, 1.8), out=.15)
        track = a.part('Door_track', 'Armor')
        fbox(track, face, (.6, y, 3.93), (5.8, .12, .1), out=.07)
        fbox(track, face, (.6, y, 1.27), (5.8, .1, .08), out=.06)
        fbox(a.part('Data_panel', 'PlasterWhite'), face, (-sy * 3.85, y, 3.3), (.62, .02, .38), out=.015)
        fbox(a.part('Data_panel', 'PlasterWhite'), face, (-sy * 3.85, y, 2.0), (.5, .02, .22), out=.015)
        fbox(a.part('Data_panel', 'Hazard'), face, (sy * 3.0, y, 3.3), (.5, .02, .2), out=.015)
    # Ladders at two diagonal corners.
    lad = a.part('Ladders', 'Steel')
    for sy, sx in ((-1, 1), (1, -1)):
        for d in (-.2, .2):
            lad.box((.04, .04, 2.7), loc=(sx * 4.6 + d, sy * 1.53, 2.55), bevel=0)
            for z in (1.4, 3.7):
                lad.box((.02, .12, .02), loc=(sx * 4.6 + d, sy * 1.5, z), bevel=0)
        for i in range(7):
            lad.box((.42, .02, .02), loc=(sx * 4.6, sy * 1.53, 1.45 + i * .38), bevel=0)


# ----------------------------------------------------------------------------- dock and street
def dock_bollards(a):
    """Quay edge strip (6 x 1 m): chamfered concrete capping kerb with painted dashes and rubber
    fenders on the water side (-Y), an apron with two tee-head bollards and a coiled mooring rope,
    its tail looped round the right bollard."""
    conc = a.part('Kerb', 'Concrete')
    conc.prism([(-.42, 0), (-.12, 0), (-.12, .32), (-.17, .38), (-.37, .38), (-.42, .32)], 6.0, axis='X', bevel=.02,
               seg=1)
    conc.box((5.98, .63, .1), loc=(0, .185, .05), bevel=.02, seg=1)
    for x in (-2.25, -.75, .75, 2.25):
        a.part('Kerb_paint', 'SafetyStripe').box((.75, .18, .02), loc=(x, -.27, .385), bevel=0)
    for x in (-2.2, 0, 2.2):
        a.part('Fenders', 'Rubber').box((.45, .09, .3), loc=(x, -.455, .17), bevel=0)
    iron = a.part('Bollards', 'Undercarriage')
    by = .2
    for x in (-1.9, 1.9):
        iron.lathe([(.27, .09), (.27, .16), (.16, .22), (.15, .5), (.24, .56), (.24, .66), (0, .68)], loc=(x, by, 0),
                   seg=10)
    rope = a.part('Rope', 'Sandbag')
    for R, z, ox in ((.25, .15, 0), (.23, .24, .02), (.245, .33, -.02)):
        rope.torus(R, .045, loc=(-.1 + ox, by, z - .005), seg=10, ring=4)
    bx = 1.9
    rope.tube([(.12, by - .02, .34), (.45, .1, .14), (1.2, .06, .14), (1.62, .05, .3), (bx, by - .2, .32),
               (bx + .2, by, .33), (bx, by + .2, .34), (bx - .2, by, .35), (bx - .02, by - .2, .37)], .04, seg=5)


def lamp_post(a):
    """Street light (7.2 m): concrete footing (0.5 x 0.5 m), tapered pole with a yellow guard band,
    curved arm and a cobra-head luminaire over the road (-Y) whose lens glows."""
    a.part('Footing', 'Concrete').box((.5, .5, .32), loc=(0, 0, .16), bevel=.03, seg=1)
    pole = a.part('Pole', 'Armor')
    pole.cyl(.15, .1, loc=(0, 0, .36), seg=8, bevel=.01, bseg=1)
    pole.cyl(.085, 6.5, loc=(0, 0, 3.6), r2=.055, seg=8, bevel=0)  # z .35 .. 6.85
    a.part('Pole_band', 'SafetyStripe').cyl(.0945, .5, loc=(0, 0, .75), r2=.0925, seg=8, bevel=0)
    pole.box((.1, .03, .32), loc=(0, -.08, 1.35), bevel=0)  # service hatch
    pole.tube([(0, 0, 6.6), (0, -.03, 6.86), (0, -.14, 7.02), (0, -.34, 7.1), (0, -.72, 7.13)], .045, seg=6)
    pole.box((.3, .62, .14), loc=(0, -.92, 7.12), bevel=.03, seg=1, taper=(.75, .88))
    a.part('Lamp', 'Lamp').box((.22, .5, .035), loc=(0, -.94, 7.0525), bevel=0)


def jersey_barrier(a):
    """Concrete jersey barrier segment (4 x 0.8 m, 0.86 m): lifting loops, forklift slots,
    reflectors and steel end connectors."""
    prof = [(-.39, 0), (.39, 0), (.39, .075), (.19, .3), (.12, .86), (-.12, .86), (-.19, .3), (-.39, .075)]
    a.part('Barrier', 'Concrete').prism(prof, 3.96, axis='X', bevel=.03, seg=2)
    for x in (-1.0, 1.0):
        a.part('Slots', 'Charred').box((.45, .8, .1), loc=(x, 0, .06), bevel=0)
    tilt = math.atan2(.07, .56)
    for sy in (-1, 1):
        for x in (-1.4, 1.4):
            ny, nz = sy * math.cos(tilt), math.sin(tilt)
            y, z = sy * (.19 - .07 * (.62 - .3) / .56), .62
            a.part('Reflectors', 'SafetyStripe').box((.4, .02, .12), loc=(x, y + ny * .005, z + nz * .005),
                                                     rot=(sy * tilt, 0, 0), bevel=0)
    for x in (-1.2, 1.2):
        a.part('Lifting_loops', 'Steel').tube([(x - .1, 0, .84), (x - .1, 0, .93), (x, 0, .97), (x + .1, 0, .93),
                                               (x + .1, 0, .84)], .018, seg=4)
    for sx in (-1, 1):
        a.part('Connectors', 'Armor').box((.04, .14, .7), loc=(sx * 1.99, 0, .43), bevel=0)


def office_block(a):
    """Four-storey concrete office block (10 x 10 m, 16.6 m): ribbon windows between spandrel
    bands, corner piers, a glazed entrance porch, and on the flat roof a stair house, air
    conditioners and a lit sign on a steel frame."""
    rng = random.Random(131)
    w, d, cy = 9.2, 8.4, .45
    base, storey, floors = .3, 3.2, 4
    top = base + floors * storey  # 13.1
    y0, y1 = cy - d / 2, cy + d / 2
    conc = a.part('Walls', 'Concrete')
    conc.box((w + .3, d + .3, base), loc=(0, cy, base / 2), bevel=.03)
    conc.box((w, d, top - base), loc=(0, cy, (base + top) / 2), bevel=.04)
    for px in (-1, 1):
        for py in (-1, 1):
            conc.box((.62, .62, top - base + .08), loc=(px * w / 2, cy + py * d / 2, (base + top + .08) / 2),
                     bevel=.03, seg=1)
    spans = [(base, base + .95)] + [(base + f * storey - .75, base + f * storey + .95) for f in range(1, floors)]
    spans.append((top - .75, top + .1))
    for za, zb in spans:
        a.part('Spandrels', 'PlasterWhite').box((w + .2, d + .2, zb - za), loc=(0, cy, (za + zb) / 2), bevel=.03, seg=1)
    faces = (('-y', (0, y0), w), ('+y', (0, y1), w), ('-x', (-w / 2, cy), d), ('+x', (w / 2, cy), d))
    band = a.part('Window_bands', 'Armor')
    for f in range(floors):
        zm = base + f * storey + .95 + .75
        for face, p, L in faces:
            fbox(band, face, (p[0], p[1], zm), (L - .5, .04, 1.52), out=.01)
            pw = (L - .8) / 5
            for i in range(5):
                q = slide(face, (p[0], p[1], zm), -(L - .8) / 2 + (i + .5) * pw)
                fbox(pane(a, rng, .28), face, q, (pw - .1, .04, 1.34), out=.045)
    # Entrance porch with glazed doors under a canopy.
    for sx in (-1, 1):
        conc.box((.3, 1.05, 3.2), loc=(sx * 1.75, y0 - .45, 1.6), bevel=.03, seg=1)
    conc.box((4.0, 1.3, .3), loc=(0, y0 - .58, 3.35), bevel=.04)
    conc.box((3.2, 1.0, .32), loc=(0, y0 - .5, .16), bevel=.02, seg=1)  # porch floor
    glass = a.part('Entrance', 'Glass')
    fbox(glass, '-y', (0, y0 - .75, 1.55), (3.24, .06, 2.52), out=0)
    fr = a.part('Entrance_frame', 'Steel')
    for u in (-1.55, 0, 1.55):
        fbox(fr, '-y', (u, y0 - .75, 1.55), (.1 if u == 0 else .08, .06, 2.5), out=.03)
    fbox(fr, '-y', (0, y0 - .75, 2.1), (3.2, .06, .06), out=.04)
    conc.box((3.6, .4, .15), loc=(0, y0 - 1.18, .075), bevel=.02, seg=1)
    fbox(a.part('Door_lamp', 'Lamp'), '-y', (0, y0 - 1.15, 3.2), (1.6, .1, .06), out=0)
    # Roof: parapet with coping, bitumen deck, stair house, air conditioners.
    pz = top + .08

    def rect(hx, hy):
        return [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    conc.shell(rect(w / 2 + .09, d / 2 + .09), .72, .3, loc=(0, cy, pz))
    a.part('Coping', 'Steel').shell(rect(w / 2 + .12, d / 2 + .12), .06, .36, loc=(0, cy, pz + .71), bevel=0)
    deck = top + .14
    a.part('Roof_deck', 'Asphalt').box((w - .1, d - .1, .1), loc=(0, cy, deck - .05), bevel=0)
    hx, hy = -2.4, cy + 2.4
    conc.box((3.0, 2.6, 2.8), loc=(hx, hy, deck + 1.4), bevel=.04)
    conc.box((3.3, 2.9, .16), loc=(hx, hy, deck + 2.86), bevel=.03, seg=1)
    door(a, '-y', (hx + .4, hy - 1.3, deck), w=.9, h=2.0, mat='Steel', frame='Concrete', step=None)
    for x, y in ((1.6, cy + 2.7), (3.4, cy + 2.7), (2.5, cy + .7)):
        a.part('Roof_AC', 'MetalSheet').box((1.5, 1.0, .8), loc=(x, y, deck + .39), bevel=.04)
        a.part('AC_fan', 'Rubber').cyl(.32, .04, loc=(x + .25, y, deck + .81), seg=12, bevel=0)
    a.part('Ducts', 'Steel').box((2.9, .4, .4), loc=(0, cy + 2.7, deck + .25), bevel=.02, seg=1)
    # Sign board on a steel frame at the front edge, lit from above.
    steel = a.part('Sign_frame', 'Steel')
    sy0 = y0 + .75
    for x in (-3.0, 0, 3.0):
        steel.box((.12, .12, 3.4), loc=(x, sy0 + .11, deck + 1.7), bevel=0)
        steel.limb((x, sy0 + .12, deck + 3.1), (x, sy0 + 1.9, deck), .08, .08, bevel=0)
    steel.box((6.4, .1, .1), loc=(0, sy0 + .11, deck + 1.35), bevel=0)
    a.part('Sign', 'PlasterWhite').box((7.2, .12, 1.7), loc=(0, sy0, deck + 2.35), bevel=.03, seg=1)
    letters(a, rng, '-y', (0, sy0 - .06, deck + 2.35), 6.6, h=1.0, mat='ContainerBlue', out=.02)
    for x in (-2.4, 0, 2.4):
        steel.limb((x, sy0 - .05, deck + 3.2), (x, sy0 - .55, deck + 3.4), .04, .04, bevel=0)
        a.part('Sign_lamps', 'Lamp').box((.34, .16, .1), loc=(x, sy0 - .6, deck + 3.4), bevel=.02, seg=1)


BUILDERS = {
    'container': (container, dict(ao_distance=.6, grime_height=.5)),
    'container_stack': (container_stack, dict(ao_distance=.7, grime_height=.6)),
    'gantry_crane': (gantry_crane, dict(ao_distance=1.6, ao_strength=.8, grime_height=1.2)),
    'factory': (factory, dict(ao_distance=2.0, grime_height=1.0)),
    'rail_tanker': (rail_tanker, dict(ao_distance=.8, grime_height=.7)),
    'rail_boxcar': (rail_boxcar, dict(ao_distance=.8, grime_height=.7)),
    'dock_bollards': (dock_bollards, dict(ao_distance=.35, grime_height=.25)),
    'office_block': (office_block, dict(ao_distance=1.8, grime_height=1.0)),
    'lamp_post': (lamp_post, dict(ao_distance=.4, grime_height=.4)),
    'jersey_barrier': (jersey_barrier, dict(ao_distance=.5, grime_height=.3)),
}
