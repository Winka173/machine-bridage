"""Machine Brigade map props, rubble and debris built with frontier_kit.

Footprints match balance.json (Blender X = prop width, Blender Y = prop depth, metres). Origins sit
on the ground at the footprint centre. Trees, bushes and the crate follow 3d_astra's scenery
builders; buildings, barriers, fuel tanks, barrels, rubble and debris are Machine Brigade's own.
"""
import math
import random

R90 = math.pi / 2
FORWARD = (R90, 0, 0)
ACROSS = (0, R90, 0)


def house(a, w, d, floors, seed):
    rng = random.Random(seed)
    storey = 3.0
    wall_h = storey * floors
    base = .35
    plaster = a.part('Walls', 'Plaster')
    trim = a.part('Trim', 'Concrete')
    glass = a.part('Windows', 'Glass')
    lit = a.part('Lit_windows', 'Lamp')
    frames = a.part('Frames', 'Wood')
    trim.box((w + .24, d + .24, base), loc=(0, 0, base / 2), bevel=.04)
    plaster.box((w, d, wall_h), loc=(0, 0, base + wall_h / 2), bevel=.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            trim.box((.32, .32, wall_h), loc=(sx * (w / 2 - .1), sy * (d / 2 - .1), base + wall_h / 2), bevel=.03)
    for f in range(1, floors):
        trim.box((w + .08, d + .08, .16), loc=(0, 0, base + f * storey), bevel=.02, seg=1)

    def facade(length, axis, sign):
        count = max(2, int(length // 2.4))
        for f in range(floors):
            z = base + f * storey + 1.55
            for i in range(count):
                u = -length / 2 + (i + .5) * length / count
                if f == 0 and axis == 'y' and sign < 0 and i == count // 2:
                    continue  # door goes here
                window = lit if rng.random() < .22 else glass
                if axis == 'y':
                    y = sign * (d / 2 + .01)
                    frames.box((.95, .1, 1.15), loc=(u, y, z), bevel=.02, seg=1)
                    window.box((.75, .06, .92), loc=(u, y + sign * .03, z), bevel=.01, seg=1)
                    trim.box((1.05, .22, .08), loc=(u, y + sign * .06, z - .62), bevel=.015, seg=1)
                else:
                    x = sign * (w / 2 + .01)
                    frames.box((.1, .95, 1.15), loc=(x, u, z), bevel=.02, seg=1)
                    window.box((.06, .75, .92), loc=(x + sign * .03, u, z), bevel=.01, seg=1)
                    trim.box((.22, 1.05, .08), loc=(x + sign * .06, u, z - .62), bevel=.015, seg=1)

    facade(w, 'y', -1)
    facade(w, 'y', 1)
    facade(d, 'x', -1)
    facade(d, 'x', 1)
    frames.box((1.2, .14, 2.2), loc=(0, -d / 2 - .02, base + 1.1), bevel=.03)
    a.part('Door', 'Wood').box((1.0, .08, 2.0), loc=(0, -d / 2 - .06, base + 1.0), bevel=.02, seg=1)
    trim.box((1.8, .9, .18), loc=(0, -d / 2 - .45, .09), bevel=.03)  # doorstep
    a.part('Door_lamp', 'Lamp').box((.16, .1, .16), loc=(.85, -d / 2 - .06, base + 2.35), bevel=.03, seg=1)

    roof = a.part('Roof', 'Roof')
    rise = min(w, d) * .32
    top = base + wall_h
    # Pitched roof along the longer side, with overhanging eaves.
    if w >= d:
        roof.prism([(-d / 2 - .45, 0), (d / 2 + .45, 0), (0, rise)], w + .6, loc=(0, 0, top), axis='X', bevel=.05)
        ridge = ((w + .5, .22, .16), (0, 0, top + rise - .02))
    else:
        roof.prism([(-w / 2 - .45, 0), (w / 2 + .45, 0), (0, rise)], d + .6, loc=(0, 0, top), axis='Y', bevel=.05)
        ridge = ((.22, d + .5, .16), (0, 0, top + rise - .02))
    trim.box(ridge[0], loc=ridge[1], bevel=.03, seg=1)
    chimney_x = w * .25 * (1 if rng.random() < .5 else -1)
    trim.box((.6, .6, rise + .9), loc=(chimney_x, d * .18, top + (rise + .9) / 2), bevel=.04)
    a.part('Chimney_cap', 'Armor').box((.74, .74, .1), loc=(chimney_x, d * .18, top + rise + .95), bevel=.02, seg=1)
    if floors > 1:  # rooftop water tank on the big building
        a.part('Tank', 'Steel').cyl(.45, .9, loc=(-chimney_x, -d * .15, top + rise * .5 + .45), seg=14, bevel=.03)


def house_small(a):
    house(a, 8.0, 8.0, 1, seed=3)


def house_large(a):
    house(a, 12.0, 10.0, 2, seed=7)


def wall(a):
    """Four concrete jersey barriers (8 m x 1 m) with hazard ends."""
    concrete = a.part('Barrier', 'Concrete')
    hazard = a.part('Hazard_band', 'Hazard')
    profile = [(-.5, 0), (.5, 0), (.22, .32), (.16, 1.05), (-.16, 1.05), (-.22, .32)]
    for i in range(4):
        x = -3 + i * 2.0
        concrete.prism(profile, 1.9, loc=(x, 0, 0), axis='X', bevel=.04)
        hazard.box((.3, .36, .2), loc=(x + (.82 if i % 2 else -.82), 0, .82), bevel=.02, seg=1)


def fuel_tank(a):
    """Vertical fuel storage tank on a concrete pad (4 x 4 m)."""
    a.part('Pad', 'Concrete').box((4.0, 4.0, .25), loc=(0, 0, .125), bevel=.05)
    body = a.part('Body', 'Fuel')
    body.cyl(1.72, 3.2, loc=(0, 0, 1.85), seg=28, bevel=.06)
    body.lathe([(1.72, 0), (1.5, .35), (.9, .6), (0, .7)], loc=(0, 0, 3.45), seg=28)
    a.part('Stripe', 'Hazard').cyl(1.75, .3, loc=(0, 0, 2.6), seg=28, bevel=.02, bseg=1)
    steel = a.part('Steel', 'Steel')
    for z in (1.0, 3.2):
        steel.torus(1.76, .035, loc=(0, 0, z), seg=28, ring=6)
    for k in range(4):
        ang = k * math.tau / 4 + math.pi / 4
        steel.box((.18, .18, .5), loc=(math.cos(ang) * 1.55, math.sin(ang) * 1.55, .45), bevel=.02, seg=1)
    for side in (-.22, .22):  # ladder
        steel.box((.05, .05, 3.3), loc=(side, -1.8, 1.9), bevel=.01, seg=1)
    for i in range(10):
        steel.box((.44, .04, .04), loc=(0, -1.8, .5 + i * .32), bevel=0)
    steel.tube([(1.2, -1.2, .35), (1.8, -1.8, .35), (1.8, -1.8, 1.2), (1.45, -1.45, 1.2)], .09, seg=10)
    a.part('Valve', 'BarrelRed').cyl(.16, .1, loc=(1.8, -1.8, .8), rot=(0, R90, math.pi / 4), seg=12, bevel=.02)
    a.part('Warning_lamp', 'Alloy').sphere(.08, loc=(0, 0, 4.2), seg=8, rings=5)


def barrel(a):
    a.part('Drum', 'BarrelRed').cyl(.4, 1.0, loc=(0, 0, .5), seg=18, bevel=.03)
    steel = a.part('Ribs', 'Steel')
    for z in (.32, .68):
        steel.torus(.41, .025, loc=(0, 0, z), seg=18, ring=5)
    a.part('Lid', 'Armor').cyl(.36, .03, loc=(0, 0, 1.01), seg=18, bevel=.01, bseg=1)
    a.part('Cap', 'Steel').cyl(.06, .05, loc=(.18, .08, 1.04), seg=8, bevel=.01, bseg=1)
    a.part('Label', 'Hazard').box((.3, .02, .22), loc=(0, -.405, .5), bevel=.005, seg=1)


def ammo_crate(a):
    """Two stacked ammunition crates (after 3d_astra's crate)."""
    for i, (z, turn) in enumerate(((0, 0.0), (.62, .35))):
        body = a.part('Body', 'Crate')
        body.box((1.1, .8, .6), loc=(0, 0, z + .3), rot=(0, 0, turn), bevel=.04)
        c, s = math.cos(turn), math.sin(turn)
        steel = a.part('Frame', 'Steel')
        for x in (-.52, .52):
            steel.box((.08, .84, .64), loc=(x * c, x * s, z + .31), rot=(0, 0, turn), bevel=.015, seg=1)
        a.part('Band', 'Hazard').box((1.12, .82, .08), loc=(0, 0, z + .46), rot=(0, 0, turn), bevel=.015, seg=1)


def tree(a):
    """Conifer (3d_astra's tree)."""
    a.part('Trunk', 'Bark').cyl(.2, 2.6, loc=(0, 0, 1.3), r2=.08, seg=8, bevel=0)
    for i in range(4):
        mat = 'Foliage' if i % 2 == 0 else 'FoliageLight'
        a.part('Crown', mat).tier(1.4 - i * .26, 1.45 - i * .12, loc=(0, 0, 1.95 + i * .64), seg=12,
                                  droop=.16 - i * .02, seed=i * 1.7)


def tree_broad(a):
    """Broadleaf tree: a leaning trunk with clustered crowns."""
    a.part('Trunk', 'Bark').limb((0, 0, 0), (.15, .1, 2.4), .34, .3, bevel=.05, taper=(.6, .6))
    a.part('Branch', 'Bark').limb((.1, .05, 1.7), (.7, .35, 2.5), .14, .12, bevel=.02, taper=(.6, .6))
    crowns = ((0, 0, 3.1, 1.35), (.75, .35, 2.75, .9), (-.55, -.3, 2.7, .95), (.1, -.1, 3.9, .95))
    for i, (x, y, z, r) in enumerate(crowns):
        a.part('Leaves', 'Foliage' if i % 2 == 0 else 'FoliageLight', flat=True).ico(
            (r, r * .95, r * .82), loc=(x, y, z), sub=2, jitter=.18, seed=i * 2.9 + 1)


def bush(a):
    """3d_astra's bush."""
    for i, (x, y, r) in enumerate(((-.38, .05, .62), (.35, .12, .56), (0, -.28, .5), (.05, .3, .44))):
        a.part('Leaves', 'Foliage' if i % 2 == 0 else 'FoliageLight').ico(
            (r, r * .95, r * .78), loc=(x, y, r * .62), sub=1, jitter=.2, seed=i * 2.3)


def rubble(a, w, d, seed):
    """Collapsed building: broken slabs, roof tiles and beams inside the old footprint."""
    rng = random.Random(seed)
    slabs = a.part('Slabs', 'Concrete', flat=True)
    plaster = a.part('Plaster_chunks', 'Plaster', flat=True)
    tiles = a.part('Tiles', 'Roof')
    beams = a.part('Beams', 'Wood')
    count = int(w * d / 2.2)
    for i in range(count):
        x, y = rng.uniform(-w / 2, w / 2) * .9, rng.uniform(-d / 2, d / 2) * .9
        r = rng.uniform(.35, .95)
        target = slabs if i % 3 else plaster
        target.ico((r, r * rng.uniform(.7, 1.1), r * rng.uniform(.35, .6)), loc=(x, y, r * .2), sub=1, jitter=.3,
                   seed=i * 1.37 + seed)
    for i in range(int(count * .4)):
        x, y = rng.uniform(-w / 2, w / 2) * .8, rng.uniform(-d / 2, d / 2) * .8
        tiles.box((rng.uniform(.6, 1.3), rng.uniform(.4, .9), .08), loc=(x, y, rng.uniform(.3, .8)),
                  rot=(rng.uniform(-.5, .5), rng.uniform(-.5, .5), rng.uniform(0, math.tau)), bevel=.02, seg=1)
    for i in range(int(count * .25)):
        x, y = rng.uniform(-w / 2, w / 2) * .7, rng.uniform(-d / 2, d / 2) * .7
        ang = rng.uniform(0, math.tau)
        length = rng.uniform(1.5, 3.2)
        beams.limb((x, y, .1), (x + math.cos(ang) * length, y + math.sin(ang) * length, rng.uniform(.4, 1.4)),
                   .16, .14, bevel=.02)
    # Stumps of the corner walls stay standing.
    for sx in (-1, 1):
        for sy in (-1, 1):
            if rng.random() < .6:
                plaster.box((.4, .4, rng.uniform(.6, 2.2)), loc=(sx * (w / 2 - .2), sy * (d / 2 - .2), .6), bevel=.03)


def rubble_small(a):
    rubble(a, 8.0, 8.0, seed=11)


def rubble_large(a):
    rubble(a, 12.0, 10.0, seed=13)


def debris(a, kind, seed):
    """Small chunk thrown by a destroyed prop; centred on its own origin so it tumbles."""
    rng = random.Random(seed)
    if kind == 'concrete':
        a.part('Chunk', 'Concrete', flat=True).ico((.45, .38, .3), sub=1, jitter=.35, seed=seed)
    elif kind == 'plaster':
        a.part('Chunk', 'Plaster', flat=True).ico((.4, .34, .22), sub=1, jitter=.35, seed=seed)
    elif kind == 'roof':
        a.part('Chunk', 'Roof').box((.9, .6, .09), rot=(rng.uniform(-.3, .3), 0, 0), bevel=.02, seg=1)
    elif kind == 'wood':
        a.part('Chunk', 'Wood').box((.16, 1.3, .14), bevel=.02, seg=1)
    elif kind == 'metal':
        a.part('Chunk', 'Armor').box((.7, .5, .06), rot=(.2, .3, 0), bevel=.01, seg=1)
        a.part('Chunk_edge', 'Steel').box((.72, .06, .12), loc=(0, .25, .03), bevel=.01, seg=1)
    elif kind == 'leaves':
        a.part('Chunk', 'Foliage', flat=True).ico((.45, .42, .35), sub=1, jitter=.25, seed=seed)


BUILDERS = {
    'house_small': (house_small, dict(ao_distance=1.6, grime_height=.9)),
    'house_large': (house_large, dict(ao_distance=1.6, grime_height=.9)),
    'wall': (wall, dict(ao_distance=.8, grime_height=.4)),
    'fuel_tank': (fuel_tank, dict(ao_distance=1.0, grime_height=.6)),
    'barrel': (barrel, dict(ao_distance=.4, grime_height=.3)),
    'ammo_crate': (ammo_crate, dict(ao_distance=.6, grime_height=.3)),
    'tree': (tree, dict(ao_distance=1.2, grime_height=.6)),
    'tree_broad': (tree_broad, dict(ao_distance=1.2, grime_height=.6)),
    'bush': (bush, dict(ao_distance=.7, grime_height=.3)),
    'rubble_small': (rubble_small, dict(ao_distance=.9, grime_height=.4)),
    'rubble_large': (rubble_large, dict(ao_distance=.9, grime_height=.4)),
    **{f'debris_{kind}': ((lambda k, s: (lambda a: debris(a, k, s)))(kind, i + 1), dict(ao_distance=.3,
                                                                                        grime_height=.1))
       for i, kind in enumerate(('concrete', 'plaster', 'roof', 'wood', 'metal', 'leaves'))},
}
