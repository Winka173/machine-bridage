"""Prompt 27 wave 8, lane B (Docs/models/WAVE8_PLAN.md): props, scenery and town on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Props are drawn many times per map: lean (<= 1.3x triangles),
no new materials, no new moving parts, scenery stays natural.

Pass 8b1 (mb_props): house_small, house_large, wall, fuel_tank, barrel, ammo_crate on chamfered `k.block` /
`k.extrude` / `k.lathe`; bush, rock_a/b/c lightly refined (one extra pebble, one extra clump). tree, pine, birch, tree_broad, tree_dead,
tree_round and the rubble_* keep their old models (natural scenery, already organic: no visible gain for the cost).
"""
import math
import random

import mb_kit27 as k
import mb_props as props

R90 = math.pi / 2


# ============================================================================= houses
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
    k.block(trim, (w + .24, d + .24, base), loc=(0, 0, base / 2), chamfer=.06, ends=(False, True))
    k.block(plaster, (w, d, wall_h), loc=(0, 0, base + wall_h / 2), chamfer=.08, ends=(False, True))
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.block(trim, (.32, .32, wall_h), loc=(sx * (w / 2 - .1), sy * (d / 2 - .1), base + wall_h / 2),
                    chamfer=.04, ends=(False, True))
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
    if w >= d:
        k.extrude(roof, [(-d / 2 - .45, 0), (d / 2 + .45, 0), (0, rise)], w + .6, loc=(0, 0, top), axis='X',
                  chamfer=.06, corner=.02)
        ridge = ((w + .5, .22, .16), (0, 0, top + rise - .02))
    else:
        k.extrude(roof, [(-w / 2 - .45, 0), (w / 2 + .45, 0), (0, rise)], d + .6, loc=(0, 0, top), axis='Y',
                  chamfer=.06, corner=.02)
        ridge = ((.22, d + .5, .16), (0, 0, top + rise - .02))
    trim.box(ridge[0], loc=ridge[1], bevel=.03, seg=1)
    chimney_x = w * .25 * (1 if rng.random() < .5 else -1)
    k.block(trim, (.6, .6, rise + .9), loc=(chimney_x, d * .18, top + (rise + .9) / 2), chamfer=.05,
            ends=(False, True))
    a.part('Chimney_cap', 'Armor').box((.74, .74, .1), loc=(chimney_x, d * .18, top + rise + .95), bevel=.02, seg=1)
    if floors > 1:
        a.part('Tank', 'Steel').cyl(.45, .9, loc=(-chimney_x, -d * .15, top + rise * .5 + .45), seg=14, bevel=.03)


# ============================================================================= wall, tank, barrel, crate
def wall(a):
    concrete = a.part('Barrier', 'Concrete')
    hazard = a.part('Hazard_band', 'Hazard')
    profile = [(-.5, 0), (.5, 0), (.22, .32), (.16, 1.05), (-.16, 1.05), (-.22, .32)]
    for i in range(4):
        x = -3 + i * 2.0
        k.extrude(concrete, profile, 1.9, loc=(x, 0, 0), axis='X', chamfer=.05, corner=.025)
        hazard.box((.3, .36, .2), loc=(x + (.82 if i % 2 else -.82), 0, .82), bevel=.02, seg=1)


def fuel_tank(a):
    k.block(a.part('Pad', 'Concrete'), (4.0, 4.0, .25), loc=(0, 0, .125), chamfer=.07, ends=(False, True))
    k.lathe(a.part('Body', 'Fuel'), [(1.6, .25), (1.72, .33), (1.72, 3.35), (1.66, 3.45), (1.5, 3.8), (.9, 4.05),
                                     (0, 4.15)], seg=28, caps=(True, False))
    a.part('Stripe', 'Hazard').cyl(1.75, .3, loc=(0, 0, 2.6), seg=28, bevel=.02, bseg=1)
    steel = a.part('Steel', 'Steel')
    for z in (1.0, 3.2):
        steel.torus(1.76, .035, loc=(0, 0, z), seg=28, ring=6)
    for kk in range(4):
        ang = kk * math.tau / 4 + math.pi / 4
        steel.box((.18, .18, .5), loc=(math.cos(ang) * 1.55, math.sin(ang) * 1.55, .45), bevel=.02, seg=1)
    for side in (-.22, .22):
        steel.box((.05, .05, 3.3), loc=(side, -1.8, 1.9), bevel=.01, seg=1)
    for i in range(10):
        steel.box((.44, .04, .04), loc=(0, -1.8, .5 + i * .32), bevel=0)
    steel.tube([(1.2, -1.2, .35), (1.8, -1.8, .35), (1.8, -1.8, 1.2), (1.45, -1.45, 1.2)], .09, seg=10)
    a.part('Valve', 'BarrelRed').cyl(.16, .1, loc=(1.8, -1.8, .8), rot=(0, R90, math.pi / 4), seg=12, bevel=.02)
    a.part('Warning_lamp', 'Alloy').sphere(.08, loc=(0, 0, 4.2), seg=8, rings=5)


def barrel(a):
    k.lathe(a.part('Drum', 'BarrelRed'), [(.34, 0), (.4, .04), (.4, .96), (.34, 1.0)], seg=18, caps=(True, True))
    steel = a.part('Ribs', 'Steel')
    for z in (.32, .68):
        steel.torus(.41, .025, loc=(0, 0, z), seg=18, ring=4)
    a.part('Lid', 'Armor').cyl(.36, .03, loc=(0, 0, 1.01), seg=18, bevel=.01, bseg=1)
    a.part('Cap', 'Steel').cyl(.06, .05, loc=(.18, .08, 1.04), seg=8, bevel=.01, bseg=1)
    a.part('Label', 'Hazard').box((.3, .02, .22), loc=(0, -.405, .5), bevel=.005, seg=1)


def ammo_crate(a):
    for i, (z, turn) in enumerate(((0, 0.0), (.62, .35))):
        body = a.part('Body', 'Crate')
        k.block(body, (1.1, .8, .6), loc=(0, 0, z + .3), rot=(0, 0, turn), chamfer=.045, ends=(True, True))
        k.inset(body, lambda c, n, f: n.z > .95, width=.07, depth=-.012)
        c, s = math.cos(turn), math.sin(turn)
        steel = a.part('Frame', 'Steel')
        for x in (-.52, .52):
            steel.box((.08, .84, .64), loc=(x * c, x * s, z + .31), rot=(0, 0, turn), bevel=.015, seg=1)
        a.part('Band', 'Hazard').box((1.12, .82, .08), loc=(0, 0, z + .46), rot=(0, 0, turn), bevel=.015, seg=1)


# ============================================================================= scenery (natural, light touch)
def bush(a):
    for i, (x, y, r) in enumerate(((-.38, .05, .62), (.35, .12, .56), (0, -.28, .5), (.05, .3, .44),
                                   (-.05, .02, .4))):
        a.part('Leaves', 'Foliage' if i % 2 == 0 else 'FoliageLight').ico(
            (r, r * .95, r * .78), loc=(x, y, r * .62 + (.35 if i == 4 else 0)), sub=1, jitter=.2, seed=i * 2.3)


def rock(a, seed, size):
    stone = a.part('Rock', 'Rock', flat=True)
    stone.ico(size, loc=(0, 0, size[2] * .5), sub=3, jitter=.3, seed=seed)
    stone.ico((.46, .4, .32), loc=(.78, .38, .14), sub=1, jitter=.32, seed=seed + 2)
    stone.ico((.32, .28, .22), loc=(-.7, -.52, .08), sub=1, jitter=.32, seed=seed + 5)
    stone.ico((.24, .2, .15), loc=(-.05, .7, .06), sub=1, jitter=.32, seed=seed + 8)


def _wrap(fn, opts, ao):
    def run(a):
        fn(a)
        k.clean(a)
    return run, dict(opts, ao_strength=ao)


def _o(name):
    return props.BUILDERS[name][1]


BUILDERS = {
    'house_small': _wrap(lambda a: house(a, 8.0, 8.0, 1, 3), _o('house_small'), .8),
    'house_large': _wrap(lambda a: house(a, 12.0, 10.0, 2, 7), _o('house_large'), .85),
    'wall': _wrap(wall, _o('wall'), .65),
    'fuel_tank': _wrap(fuel_tank, _o('fuel_tank'), .9),
    'barrel': _wrap(barrel, _o('barrel'), .55),
    'ammo_crate': _wrap(ammo_crate, _o('ammo_crate'), .6),
    'bush': _wrap(bush, _o('bush'), .9),
    'rock_a': _wrap(lambda a: rock(a, 1.3, (1.0, .9, .62)), _o('rock_a'), .85),
    'rock_b': _wrap(lambda a: rock(a, 4.7, (.95, .82, .78)), _o('rock_b'), .8),
    'rock_c': _wrap(lambda a: rock(a, 8.2, (.9, 1.0, .5)), _o('rock_c'), .88),
}
