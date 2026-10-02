"""Prompt 27 wave 8, lane B (Docs/models/WAVE8_PLAN.md): props, scenery and town on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Props are drawn many times per map: lean (<= 1.3x triangles),
no new materials, no new moving parts, scenery stays natural.

Pass 8b1 (mb_props): house_small, house_large, wall, fuel_tank, barrel, ammo_crate on chamfered `k.block` /
`k.extrude` / `k.lathe`; bush, rock_a/b/c lightly refined (one extra pebble, one extra clump). tree, pine, birch, tree_broad, tree_dead,
tree_round and the rubble_* keep their old models (natural scenery, already organic: no visible gain for the cost).

Pass 8b2 (mb_mapkit): checkpoint, barricade, supply_pile, telegraph_pole on the V2 kit (chamfered `k.block` volumes,
lathe drums and pole); helpers and small parts come from mb_mapkit. The other seventeen map-kit models (wrecks,
earthworks, tent, net, bladder, pylon, mast, bridge, ruins, dead tree) keep their old models: bespoke builds with
hand-made detail, no visible gain for the cost.
"""
import math
import random

import mb_kit27 as k
import mb_props as props
import mb_mapkit as mk
import mb_town as town
import mb_themes as themes
import mb_themes2 as themes2
from mathutils import Vector
from mb_siege import bag_run, coil, shells

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


# ============================================================================= map kit (pass 8b2)
def _kb(part, m, size, off=(0, 0, 0), chamfer=.04, taper=(1, 1), ends=(True, True)):
    """Chamfered block in frame m, centred at off (m's coordinates)."""
    k.block(part, size, loc=m @ Vector(off), rot=m.to_euler('XYZ'), chamfer=chamfer, taper=taper, ends=ends)


def _crate(a, loc, size, yaw=0.0, band=True):
    w, d, h = size
    m = mk._frame(loc, (0, 0, yaw))
    _kb(a.part('Crates', 'Crate'), m, size, (0, 0, h / 2), chamfer=.04)
    cleat = a.part('Crate_cleats', 'Wood')
    for s in (-1, 1):
        _kb(cleat, m, (.06, d + .025, h + .02), (s * (w / 2 - .09), 0, h / 2), chamfer=.012)
    if band:
        _kb(a.part('Crate_bands', 'Hazard'), m, (w * .3, d + .03, .06), (0, 0, h * .66), chamfer=.01)


def _drum(a, loc, mat='Crate', lying=None):
    x, y, z = loc
    if lying is None:
        k.lathe(a.part('Drums', mat), [(.27, 0), (.29, .03), (.29, .85), (.27, .88)], loc=(x, y, z), seg=10)
        hoops = a.part('Drum_hoops', mat)
        for h in (.3, .58):
            hoops.torus(.29, .016, loc=(x, y, z + h), seg=10, ring=3)
        a.part('Drum_bungs', 'Steel').cyl(.04, .03, loc=(x + .15, y + .05, z + .885), seg=6, bevel=0)
    else:
        d = Vector((math.cos(lying), math.sin(lying), 0))
        rot = (0, R90, lying)
        k.lathe(a.part('Drums', mat), [(0, -.44), (.27, -.44), (.29, -.41), (.29, .41), (.27, .44), (0, .44)],
                loc=(x, y, z + .29), rot=rot, seg=10, caps=(False, False))
        for h in (-.14, .14):
            a.part('Drum_hoops', mat).torus(.29, .016, loc=Vector((x, y, z + .29)) + d * h, rot=rot, seg=10, ring=3)


def checkpoint(a):
    rng = random.Random(95)
    bx, by, hw = 2.1, .6, .82
    bags = a.part('Sandbags', 'Sandbag')
    size = (.62, .34, .24)
    courses = 5
    for kk in range(courses):
        z = .12 - .01 + kk * .215
        half = kk % 2 == 1
        bag_run(bags, rng, (bx - hw, by - hw), (bx + hw, by - hw), z, size, half=half)
        bag_run(bags, rng, (bx + hw, by - hw + .17), (bx + hw, by + hw), z, size, half=not half)
        bag_run(bags, rng, (bx - hw, by + hw), (bx - hw, by - hw + .17), z, size, half=not half)
        bag_run(bags, rng, (bx + hw - .17, by + hw), (bx + .15, by + hw), z, size, half=half)
    wood = a.part('Posts', 'LogWood')
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.block(wood, (.12, .12, 2.15), loc=(bx + sx * (hw - .02), by + sy * (hw - .02), 1.07), chamfer=.02)
    k.block(a.part('Roof', 'Corrugated'), (2.1, 2.1, .07), loc=(bx, by, 2.18), rot=(.06, 0, 0), chamfer=.025)
    for x, y in ((-.55, -.5), (.5, .55), (-.4, .6)):
        bag_run(a.part('Roof_bags', 'Sandbag'), rng, (bx + x - .3, by + y), (bx + x + .3, by + y),
                2.17 + .12 - y * .06, size)
    a.part('Floodlight', 'Armor').box((.3, .2, .22), loc=(bx - hw + .05, by - hw - .05, 2.0), rot=(.4, 0, .5),
                                      bevel=.025, seg=1)
    a.part('Floodlight_lens', 'Lamp').box((.24, .03, .16), loc=(bx - hw + .005, by - hw - .135, 1.97),
                                          rot=(.4, 0, .5), bevel=0)
    a.part('Telephone', 'Crate').box((.26, .18, .16), loc=(bx + .2, by - hw, .11 + (courses - 1) * .215 + .19),
                                     bevel=.02, seg=1)
    k.block(a.part('Barrier_post', 'Concrete'), (.38, .38, 1.0), loc=(1.1, -.55, .5), chamfer=.05)
    a.part('Hinge', 'Steel').cyl(.09, .5, loc=(1.1, -.55, 1.05), rot=mk.FORWARD, seg=8, bevel=0)
    mk._stripes(a, (1.1, -.75, 1.05), (-2.55, -.75, 1.05), 8)
    k.block(a.part('Counterweight', 'Concrete'), (.45, .3, .3), loc=(1.55, -.75, 1.05), chamfer=.04, ends=(True, True))
    a.part('Barrier_steel', 'Steel').cyl(.04, .5, loc=(1.33, -.75, 1.05), rot=mk.ACROSS, seg=6, bevel=0)
    rest = a.part('Rest', 'Steel')
    rest.box((.08, .08, .95), loc=(-2.4, -.75, .47), bevel=0)
    for s in (-1, 1):
        rest.box((.04, .04, .22), loc=(-2.4, -.75 + s * .1, 1.03), bevel=0)
    rest.box((.1, .28, .04), loc=(-2.4, -.75, .94), bevel=0)
    conc = a.part('Blocks', 'Concrete')
    for x, y, yaw in ((-1.95, -1.65, .04), (.15, -1.7, -.06), (-1.0, 1.55, .08)):
        k.block(conc, (1.3, .6, .8), loc=(x, y, .4), rot=(0, 0, yaw), chamfer=.07, taper=(.85, .93), ends=(True, True))
        m = mk._frame((x, y, .8), (0, 0, yaw))
        for s in (-.35, .35):
            a.part('Lifting_eyes', 'Rust').tube([tuple(m @ Vector((s - .08, 0, -.02))),
                                                 tuple(m @ Vector((s - .06, 0, .1))),
                                                 tuple(m @ Vector((s + .06, 0, .1))),
                                                 tuple(m @ Vector((s + .08, 0, -.02)))], .02, seg=4)
    for sx in (-.4, .4):
        k.block(a.part('Sign_posts', 'Steel'), (.07, .07, 1.7), loc=(-2.55 + sx, -1.81, .85), chamfer=.012)
    a.part('Sign', 'BarrelRed').box((1.1, .05, .6), loc=(-2.55, -1.86, 1.45), bevel=.02, seg=1)
    a.part('Sign_band', 'PlasterWhite').box((.85, .03, .16), loc=(-2.55, -1.9, 1.45), bevel=0)
    _drum(a, (2.55, -1.4, 0), 'Rust')
    a.part('Embers', 'LavaGlow').cyl(.26, .03, loc=(2.55, -1.4, .87), seg=10, bevel=0)
    a.part('Stove_grill', 'Charred').cyl(.27, .04, loc=(2.55, -1.4, .9), seg=10, bevel=0)


def barricade(a):
    rng = random.Random(96)
    tyres = a.part('Tyres', 'Rubber')
    for kk in range(3):
        tyres.torus(.3, .12, loc=(-2.35 + kk * .02, .1 - kk * .03, .12 + kk * .235), rot=(0, 0, kk), seg=12, ring=5)
    tyres.torus(.3, .12, loc=(-1.85, -.38, .38), rot=(1.2, .1, .3), seg=12, ring=5)
    tyres.torus(.3, .12, loc=(-2.8, -.35, .36), rot=(1.1, -.2, -.4), seg=12, ring=5)
    planks = a.part('Planks', 'Wood')
    for p0, p1 in (((-2.0, .25, .05), (-.4, .2, 1.05)), ((-2.0, .3, 1.0), (-.35, .28, .1)),
                   ((-1.9, .38, .55), (-.3, .36, .62)), ((-1.2, .5, .05), (-1.0, .5, 1.25))):
        planks.limb(p0, p1, .2, .04, bevel=0)
    a.part('Planks_dark', 'LogWood').limb((-.6, .45, .05), (-.25, .1, 1.1), .14, .05, bevel=0)
    m = mk._frame((-1.15, -.05, 0), (-.32, 0, .08))
    door = a.part('Door', 'Charred')
    _kb(door, m, (1.05, .07, .52), (0, 0, .28), chamfer=.025)
    _kb(door, m, (1.0, .08, .06), (-.02, 0, .95), chamfer=.015)
    _kb(door, m, (.06, .05, .41), (.5, 0, .75), chamfer=.01)
    door.limb(tuple(m @ Vector((-.5, 0, .52))), tuple(m @ Vector((-.28, 0, .96))), .06, .04, bevel=0)
    mk._box_on(a.part('Door_rust', 'Rust'), m, (.5, .03, .28), off=(.15, -.04, .3))
    mk._box_on(a.part('Door_handle', 'Steel'), m, (.14, .04, .03), off=(.35, -.05, .45))
    bags = a.part('Sandbags', 'Sandbag')
    size = (.68, .36, .24)
    for kk, (ys, z) in enumerate((((-.2, .2), .11), ((-.2, .2), .325), ((0.0,), .54))):
        for y in ys:
            bag_run(bags, rng, (-.2, y), (2.95, y), z, size, half=(kk % 2 == 1) ^ (y > 0))
    coil(a.part('Barbed_wire', 'Steel'), .1, 2.8, 0, .9, .26, pitch=.3, pts=6, wire=.012)
    _drum(a, (1.3, -.62, 0), 'Rust', lying=.15)
    frame = a.part('Bed_frame', 'Steel')
    fm = mk._frame((.3, .62, 0), (-.25, 0, -.05))
    for s in (-1, 1):
        frame.limb(tuple(fm @ Vector((s * .45, 0, 0))), tuple(fm @ Vector((s * .45, 0, 1.25))), .04, .04, bevel=0)
    for zz in (.25, .6, .95, 1.22):
        frame.limb(tuple(fm @ Vector((-.47, 0, zz))), tuple(fm @ Vector((.47, 0, zz + (.05 if zz > 1 else 0)))),
                   .03, .03, bevel=0)
    mk._chunks([a.part('Bricks', 'Brick', flat=True), a.part('Rubble', 'Concrete', flat=True)], rng, 2.3, -.5, .35,
               .2, 6, size=(.1, .2), seed=3.0)


def supply_pile(a):
    z = .14

    def pallet(x, y, yaw=0.0, w=1.2, d=1.0):
        m = mk._frame((x, y, 0), (0, 0, yaw))
        _kb(a.part('Pallets', 'Wood'), m, (w, d, .06), (0, 0, .11), chamfer=.015)
        for kk in (-1, 0, 1):
            a.part('Pallet_skids', 'LogWood').box((w - .04, .12, .1), loc=m @ Vector((0, kk * (d / 2 - .08), .04)), rot=m.to_euler('XYZ'), bevel=0)
        return m
    m = pallet(-1.3, .65, .05, w=1.3, d=1.1)
    base = m @ mk._frame((0, 0, z), (0, 0, 0))
    w, d, h = 1.25, 1.05, .95
    tarp = a.part('Tarp', 'Canvas')
    _kb(tarp, base, (w + .08, d + .08, h), (0, 0, h / 2), chamfer=.1, taper=(.95, .95))
    yaw = base.to_euler('XYZ').z
    for s in (-1, 1):
        tarp.box((w + .02, .03, .32), loc=base @ Vector((0, s * (d / 2 + .08), .15)), rot=(s * .22, 0, yaw), bevel=0)
    rope = a.part('Ropes', 'Rubber')
    for u in (-w / 4, w / 4):
        pts = [(u, -d / 2 - .1, .02), (u, -d / 2 - .04, h * .9), (u, -d / 2 + .1, h + .005), (u, d / 2 - .1, h + .005),
               (u, d / 2 + .04, h * .9), (u, d / 2 + .1, .02)]
        rope.tube([tuple(base @ Vector(p)) for p in pts], .016, seg=4)
    m = pallet(.3, .75, -.06)
    for j in (-.26, .26):
        _crate(a, tuple(m @ Vector((0, j, z))), (1.1, .48, .36), yaw=-.06)
    for i in (-.27, .27):
        _crate(a, tuple(m @ Vector((i, 0, z + .36))), (.98, .48, .34), yaw=-.06 + R90, band=i > 0)
    _crate(a, tuple(m @ Vector((.05, .02, z + .7))), (.7, .38, .3), yaw=.35)
    for x, y, mat in ((1.65, .95, 'Crate'), (1.65, .3, 'BarrelRed'), (1.1, -.2, 'Crate')):
        _drum(a, (x, y, 0), mat)
    _drum(a, (.35, -.95, 0), 'Crate', lying=.25)
    mk._jerrycans(a, (-1.4, -.85, 0), 4, axis='x')
    box = mk._frame((1.35, -.95, 0), (0, 0, -.3))
    a.part('Shell_box', 'Wood').shell([(-.42, -.22), (.42, -.22), (.42, .22), (-.42, .22)], .28, .03,
                                      loc=box.to_translation(), rot=(0, 0, -.3), floor=.03)
    shells(a, tuple(box @ Vector((0, 0, .03))), 4, 2, r=.07, h=.5, pitch=.19, yaw=-.3)
    a.part('Shell_box_lid', 'Wood').box((.86, .46, .03), loc=box @ Vector((0, -.5, .05)), rot=(.06, 0, -.3), bevel=0)


def telegraph_pole(a):
    lean = (.015, -.02, 0)
    m = mk._frame((0, 0, 0), lean)
    k.lathe(a.part('Pole', 'LogWood'), [(0, -.1), (.145, -.1), (.145, 0), (.135, 3.0), (.12, 5.5), (.11, 7.2),
                                        (.08, 7.27), (0, 7.27)],
            loc=(0, 0, 0), rot=lean, seg=10, caps=(False, False))
    a.part('Collar', 'Dirt', flat=True).ico((.3, .3, .12), loc=(0, 0, .02), sub=1, jitter=.25, seed=2.0)
    _kb(a.part('Cap', 'Steel'), m, (.26, .26, .05), (0, 0, 7.24), chamfer=.015)
    arms = a.part('Cross_arms', 'Wood')
    braces = a.part('Braces', 'Steel')
    insul = a.part('Insulators', 'Medical')
    for z, half, n in ((6.75, .8, 4), (6.25, .55, 2)):
        _kb(arms, m, (2 * half, .1, .1), (0, -.14, z), chamfer=.02)
        for s in (-1, 1):
            braces.limb(tuple(m @ Vector((s * half * .6, -.14, z - .05))), tuple(m @ Vector((0, -.12, z - .55))),
                        .04, .012, bevel=0)
        xs = [-half + .08 + (2 * half - .16) * kk / (n - 1) for kk in range(n)]
        for x in xs:
            p = m @ Vector((x, -.14, z + .05))
            a.part('Pins', 'Steel').cyl(.015, .12, loc=(p.x, p.y, p.z + .05), seg=4, bevel=0)
            insul.lathe([(.05, 0), (.06, .035), (.045, .08), (.02, .11)], loc=(p.x, p.y, p.z + .07), seg=8)
            mk._stubs(a, Vector((p.x, p.y, p.z + .15)), length=1.1, sag=.12)
    steps = a.part('Step_bolts', 'Steel')
    for kk in range(8):
        z = 2.4 + kk * .45
        ang = (kk % 2) * math.pi
        p = m @ Vector((math.cos(ang) * .12, math.sin(ang) * .12 + .02, z))
        steps.cyl(.012, .22, loc=tuple(p), rot=mk.ACROSS, seg=4, bevel=0)
    mk._box_on(a.part('Number_plate', 'Hazard'), m @ mk._basis((0, -.14, 2.0), (1, 0, 0), (0, -1, 0)), (.14, .2, .02))
    top, anchor = Vector(m @ Vector((-.1, 0, 5.5))), Vector((-1.7, 0, .06))
    a.part('Stay', 'Steel').tube([tuple(top), tuple(anchor)], .012, seg=3)
    dv = anchor - top
    insul.cyl(.04, .16, loc=top + dv * .3, rot=mk._along(dv), seg=6, bevel=0)
    a.part('Stay_guard', 'Hazard').cyl(.03, 1.6, loc=anchor - dv.normalized() * .82, rot=mk._along(dv), seg=6,
                                       bevel=0)
    k.block(a.part('Anchor', 'Concrete'), (.34, .34, .14), loc=(-1.72, 0, .06), rot=(0, 0, .2), chamfer=.03)


# ----- pass 8b2, second part: the bespoke map-kit builders re-run with V2 edge treatment. Every square-edged box
# (bevel 0) of at least BOX_MIN in its thinnest side gets a one-step chamfer (a block plate, not a razor edge) and
# every square cylinder a light one; the shapes, nodes, materials and random draws stay the same.
import frontier_kit as fk
from contextlib import contextmanager


@contextmanager
def _v2(box_min=.15, ratio=.12, cyl_min=.12, seg_add=0, dens=1.0):
    ob, oc, ot, od, ol = fk.Shape.box, fk.Shape.cyl, fk.Shape.torus, mk._densify, fk.Shape.lathe

    def box(self, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.04, seg=2, taper=(1, 1), shift=(0, 0)):
        t = min(size)
        if bevel == 0 and t >= box_min:
            bevel, seg = t * ratio, 1
        return ob(self, size, loc, rot, bevel, seg, taper, shift)

    def cyl(self, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, r2=None, bevel=0.02, bseg=2):
        if bevel == 0 and min(r, depth / 2) >= cyl_min:
            bevel, bseg = min(r, depth / 2) * .1, 1
        if seg_add and seg >= 8 and r >= cyl_min:
            seg += seg_add
        return oc(self, r, depth, loc, rot, seg, r2, bevel, bseg)

    def torus(self, R, r, loc=(0, 0, 0), rot=(0, 0, 0), seg=24, ring=8):
        return ot(self, R, r, loc, rot, seg + seg_add if R >= cyl_min else seg, ring)

    def lathe(self, profile, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, **kw):
        return ol(self, profile, loc, rot, seg + (seg_add if seg >= 6 else 0), **kw)

    def densify(path, step, clear=0.0):
        return od(path, step * dens, clear)
    fk.Shape.box, fk.Shape.cyl, fk.Shape.torus, mk._densify, fk.Shape.lathe = box, cyl, torus, densify, lathe
    try:
        yield
    finally:
        fk.Shape.box, fk.Shape.cyl, fk.Shape.torus, mk._densify, fk.Shape.lathe = ob, oc, ot, od, ol


def _redo(name, ao=.9, subs=(), **kw):
    old = mk.BUILDERS[name]
    if subs:
        import inspect
        src = inspect.getsource(old[0])
        for x, y in subs:
            assert x in src, x
            src = src.replace(x, y)
        ns = {}
        exec(src, vars(mk), ns)
        old = (ns[name], old[1])

    def run(a):
        with _v2(**kw):
            old[0](a)
        k.clean(a)
    return run, dict(old[1], ao_strength=ao)


def _town(name, ao=.9, **kw):
    old = town.BUILDERS[name]

    def run(a):
        with _v2(**kw):
            old[0](a)
        k.clean(a)
    return run, dict(old[1], ao_strength=ao)


def _theme(name, ao=.8, **kw):
    old = themes.BUILDERS[name]

    def run(a):
        with _v2(**kw):
            old[0](a)
        k.clean(a)
    return run, dict(old[1], ao_strength=ao)


def _theme2(name, ao=.8, **kw):
    old = themes2.BUILDERS[name]

    def run(a):
        with _v2(**kw):
            old[0](a)
        k.clean(a)
    return run, dict(old[1], ao_strength=ao)


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
    'checkpoint': _wrap(checkpoint, mk.BUILDERS['checkpoint'][1], .8),
    'barricade': _wrap(barricade, mk.BUILDERS['barricade'][1], .8),
    'supply_pile': _wrap(supply_pile, mk.BUILDERS['supply_pile'][1], .8),
    'telegraph_pole': _wrap(telegraph_pole, mk.BUILDERS['telegraph_pole'][1], .7),
    'wreck_tank': _redo('wreck_tank', 0.7, seg_add=2),
    'wreck_truck': _redo('wreck_truck', 0.6, box_min=.3),
    'wreck_car': _redo('wreck_car', 0.7, seg_add=2),
    'trench_straight': _redo('trench_straight', .9, dens=.7, seg_add=2),
    'trench_corner': _redo('trench_corner', .9, dens=.7, seg_add=2),
    'foxhole': _redo('foxhole', 0.75, seg_add=2),
    'crater_large': _redo('crater_large', .9, seg_add=2),
    'tank_ditch': _redo('tank_ditch', .9, subs=((' rows = 21', ' rows = 27'), ('range(8)', 'range(10)')), seg_add=2),
    'command_tent': _redo('command_tent', .9, seg_add=2),
    'camo_net': _redo('camo_net', 0.7, seg_add=2),
    'fuel_bladder': _redo('fuel_bladder', .9, seg_add=2, cyl_min=.06),
    'power_pylon': _redo('power_pylon', 0.6, seg_add=2),
    'radio_mast': _redo('radio_mast', 0.6, seg_add=4, cyl_min=.06),
    'bridge_road': _redo('bridge_road', 0.65, seg_add=2),
    'ruin_house': _redo('ruin_house', 0.75, seg_add=2),
    'ruin_tower': _redo('ruin_tower', 0.75, seg_add=2),
    'dead_tree': _redo('dead_tree', 0.6, box_min=.25),
    'apartment': _town('apartment', .8, seg_add=2),
    'barn': _town('barn', .8, seg_add=2),
    'car': _town('car', .8, seg_add=2),
    'church': _town('church', .8, seg_add=2),
    'cottage': _town('cottage', .8, seg_add=2),
    'fence': _town('fence', .8, seg_add=2),
    'garage': _town('garage', .8, seg_add=2),
    'hedge': _town('hedge', .8, seg_add=2),
    'ruin': _town('ruin', .8, seg_add=2),
    'shop': _town('shop', .8, seg_add=2),
    'silo': _town('silo', .8, seg_add=2),
    'stone_wall': _town('stone_wall', .8, seg_add=2),
    'townhouse': _town('townhouse', .8, seg_add=2),
    'truck': _town('truck', .8, seg_add=2),
    'warehouse': _town('warehouse', .8, seg_add=2),
    'water_tower': _town('water_tower', .8, seg_add=2),
    'adobe_house': _theme('adobe_house', .8, box_min=.2),
    'adobe_large': _theme('adobe_large', .8, box_min=.2),
    'cactus': _theme('cactus', .8, seg_add=2),
    'log_cabin': _theme('log_cabin', .8, box_min=.45, cyl_min=.18),
    'market_stall': _theme('market_stall', .8, seg_add=2),
    'mesa': _theme('mesa', .7, seg_add=2),
    'oil_pump': _theme('oil_pump', .8, seg_add=2),
    'palm': _theme('palm', .8, seg_add=2),
    'pipeline': _theme('pipeline', .8, seg_add=2),
    'radar_station': _theme('radar_station', .8, seg_add=2),
    'refinery_tower': _theme('refinery_tower', .8, seg_add=2),
    'snow_pine': _theme('snow_pine', .3, seg_add=2),
    'snow_rock': _theme('snow_rock', .8, seg_add=2),
    'storage_tank': _theme('storage_tank', .8, seg_add=2),
    'watchtower': _theme('watchtower', .8, seg_add=2),
    'bamboo_clump': _theme2('bamboo_clump', .8, seg_add=2),
    'basalt_rock_a': _theme2('basalt_rock_a', .8, seg_add=2),
    'basalt_rock_b': _theme2('basalt_rock_b', .8, seg_add=2),
    'basalt_rock_c': _theme2('basalt_rock_c', .8, seg_add=2),
    'billboard': _theme2('billboard', .8, seg_add=2),
    'bus': _theme2('bus', .8, seg_add=2),
    'charred_tree': _theme2('charred_tree', .8, seg_add=2),
    'control_tower': _theme2('control_tower', .8, seg_add=2),
    'fern_bush': _theme2('fern_bush', .8, seg_add=2),
    'fuel_truck': _theme2('fuel_truck', .8, seg_add=2),
    'hangar': _theme2('hangar', .8, seg_add=2),
    'highrise_a': _theme2('highrise_a', .8, seg_add=2),
    'highrise_b': _theme2('highrise_b', .8, box_min=.3, seg_add=2),
    'jungle_tree_a': _theme2('jungle_tree_a', .8, seg_add=2),
    'jungle_tree_b': _theme2('jungle_tree_b', .8, seg_add=2),
    'jungle_tree_c': _theme2('jungle_tree_c', .8, seg_add=2),
    'lava_vent': _theme2('lava_vent', .8, seg_add=2),
    'obsidian_spire': _theme2('obsidian_spire', .8, seg_add=2),
    'parked_jet': _theme2('parked_jet', .8, seg_add=2),
    'parking_garage': _theme2('parking_garage', .8, seg_add=2),
    'radar_dome': _theme2('radar_dome', .8, seg_add=2),
    'revetment': _theme2('revetment', .8, seg_add=2),
    'runway_light': _theme2('runway_light', .8, seg_add=2),
    'skyscraper': _theme2('skyscraper', .8, seg_add=2),
    'stilt_hut': _theme2('stilt_hut', .8, seg_add=2),
    'temple_ruin': _theme2('temple_ruin', .8, box_min=.4, seg_add=2),
    'traffic_light': _theme2('traffic_light', .8, seg_add=2),
    'volcanic_cliff': _theme2('volcanic_cliff', .8, seg_add=2),
}
