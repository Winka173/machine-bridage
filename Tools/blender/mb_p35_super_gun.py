"""Prompt 35 wave 3 (lane B): the fortress super-gun rebuilt from scratch (spec: Tools/blender/specs/super_gun.json).

The fortress's giant twin gun (Strings note.super_gun: one huge shell on the attackers' thickest knot on a countdown;
the GLB 10.4 x 8.0 x 5.2 m, drawn at scale 1.8): a cast concrete citadel drum on an octagonal blast apron with
hazard-striped kerbs, a parapet ring with sandbags along its crest, the loading door in the citadel; on the turret
ring the armoured gun house (`Turret`, it turns at 12 degrees a second) with the two huge barrels raised 28 degrees
(`Main_cannon`, `Main_cannon_2`, each with its collars, recuperators and multi-baffle brake, `Muzzle_brake`,
`Muzzle_brake_2`), the commander's cupola, the stereoscopic rangefinder's arms out of both cheeks, hatches, vents,
antennas and lamps; beside the citadel the shell hoist house, the rails with a trolley carrying two giant shells,
and the gantry crane with its hook block; a beacon on the hoist roof. The fortress's own work: concrete and armour,
with the garrison's sandbags and nets.

Its own body: not the rail supergun's (on a railway carriage) nor the heavy turret family's.
Runtime nodes kept: `Turret`, `Main_cannon`, `Main_cannon_2`, `Muzzle_brake`, `Muzzle_brake_2`, `Muzzle_main`; the
old part names `Blast_apron`, `Apron_kerbs`, `Citadel`, `Turret_ring`, `Race`, `Gun_house`, `Cradle`, `Recuperators`,
`Collar_band`, `Cupola`, `Cupola_glass`, `Rangefinder`, `Rangefinder_glass`, `Hatches`, `Vents`, `Roof_kit`,
`Antennas`, `Lamps`, `Loading_door`, `Door_hazard`, `Hoist_door`, `Hoist_roof`, `Rails`, `Trolley`, `Shells`,
`Shell_bands`, `Crane`, `Crane_cable`, `Hook_block`, `Beacon`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
AP = .18                  # the apron's top
CR, CH = 2.55, 1.35       # the citadel's radius and height above the apron
CZ = AP + CH
TT = (0, .4, CZ + .12)    # the gun house's yaw pivot
ELEV = math.radians(28)
GAP = .62                 # the barrels' half spacing


def _apron(a, rng):
    oct_ = [(math.cos(u) * 3.95, .4 + math.sin(u) * 3.95) for u in [i * math.tau / 8 + math.tau / 16 for i in range(8)]]
    k.extrude(a.part('Blast_apron', 'Concrete'), oct_, AP, loc=(0, 0, AP / 2), axis='Z', chamfer=.06,
              caps=(False, True), taper=(.98, .98))
    kerbs = a.part('Apron_kerbs', 'Hazard')
    stripes = a.part('Kerb_stripes', 'Charred')
    for i in range(8):
        p, q = oct_[i], oct_[(i + 1) % 8]
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        c = ((p[0] + q[0]) / 2 * .97, .4 + ((p[1] + q[1]) / 2 - .4) * .97)
        kerbs.box((L - .3, .18, .12), loc=(c[0], c[1], AP + .06), rot=(0, 0, ang), bevel=0)
        for j in range(2):
            f = (j + .5) / 2 - .5
            stripes.box((.18, .19, .125), loc=(c[0] + math.cos(ang) * f * (L - .5), c[1] + math.sin(ang) * f * (L - .5),
                                                AP + .06), rot=(0, 0, ang + .5), bevel=0)
    # Expansion joints in the apron, scorch from the muzzle blast in front.
    joints = a.part('Apron_joints', 'Undercarriage')
    for x in (-1.9, 1.9):
        joints.box((.03, 7.0, .01), loc=(x, .4, AP + .004), bevel=0)
    for j in range(5):
        K.soot(a, (rng.uniform(-2.5, 2.5), -3.0 + rng.uniform(-.5, .5), AP), radius=1.4, k=.35)


def _citadel(a):
    cit = a.part('Citadel', 'Concrete')
    k.lathe(cit, [(CR + .25, 0), (CR + .1, .25), (CR, CH - .1), (CR - .05, CH)], loc=(0, .4, AP), seg=24,
            worn=(1, 3))
    ties = a.part('Form_ties', 'Steel')
    for i in range(10):
        u = i * math.tau / 10
        for z in (.45, .95):
            ties.cyl(.03, .04, loc=(math.cos(u) * (CR + .06), .4 + math.sin(u) * (CR + .06), AP + z),
                     rot=(0, R90, u), seg=5, bevel=0)
    # The parapet ring on the citadel's rim (gate role "walls") and the sandbags on its crest, open at the hoist.
    par = a.part('Walls', 'Concrete')
    for i in range(20):
        u0, u1 = i * math.tau / 20, (i + 1) * math.tau / 20
        if 4 <= i <= 5:
            continue                                       # the gap over the hoist (rear left)
        um = (u0 + u1) / 2
        k.block(par, (2 * (CR - .12) * math.sin(math.pi / 20) + .02, .3, .45),
                loc=(math.cos(um) * (CR - .15), .4 + math.sin(um) * (CR - .15), CZ + .225), rot=(0, 0, um + R90),
                chamfer=0)
    path = [(math.cos(u) * (CR - .15), .4 + math.sin(u) * (CR - .15), CZ + .45)
            for u in [math.radians(d) for d in range(130, 360 + 40, 16)]]
    P.sandbag_run(a, path, courses=1, bag=(.62, .36, .17), part='Sandbags', seed=171, lean=True)
    k.ring(a.part('Turret_ring', 'Steel'), [(1.75, -.05), (1.95, -.05), (1.95, .12), (1.75, .12)], loc=(0, .4, CZ),
           seg=22)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (0, .4, CZ + .12), (0, 0, 1), 1.85, 12, r=.04, h=.04)
    k.lathe(a.part('Race', 'Concrete'), [(1.75, 0), (1.75, .02), (0, .02)], loc=(0, .4, CZ - .01), seg=22)
    # The loading door in the citadel's rear, its hazard frame, the door lamp.
    u = math.radians(70)
    dx, dy = math.cos(u) * (CR + .02), .4 + math.sin(u) * (CR + .02)
    K.door(a, (dx, dy, AP), size=(1.1, 1.05), normal=(math.cos(u), math.sin(u), 0))
    a.part('Loading_door', 'Armor').box((1.0, .04, .95), loc=(dx + math.cos(u) * .04, dy + math.sin(u) * .04,
                                                               AP + .5), rot=(0, 0, u + R90), bevel=0)
    a.part('Door_hazard', 'Hazard').box((1.35, .05, .14), loc=(dx + math.cos(u) * .06, dy + math.sin(u) * .06,
                                                                AP + 1.12), rot=(0, 0, u + R90), bevel=0)
    K.lamp(a, (dx + math.cos(u) * .1 + .6, dy + math.sin(u) * .1, AP + 1.0), (math.cos(u), math.sin(u), 0), r=.07,
           mat='Armor', guard=True)


def _gun_house(a):
    t = a.pivot('Turret', TT)
    gh = a.part('Gun_house', 'Team', t)
    # Horizontal sections: a sloped front glacis, the slab sides leaning in, a long rear bustle.
    rings = []
    for z, f, w, r in ((0, -1.5, 1.85, 2.1), (.9, -1.35, 1.75, 2.05), (1.45, -.75, 1.5, 1.85)):
        rings.append([(-w * .6, f, z), (w * .6, f, z), (w, f + .55, z), (w, r - .3, z), (w - .25, r, z),
                      (-w + .25, r, z), (-w, r - .3, z), (-w, f + .55, z)])
    k.sharp_loft(gh, rings, chamfer=.06)
    # Rivetted armour seams on the cheeks.
    rv = a.part('Kit_rivets', 'Steel', t)
    for s in (-1, 1):
        for j in range(8):
            rv.cyl(.035, .04, loc=(s * 1.82, -.6 + j * .32, .55), rot=(0, R90, 0), seg=5, bevel=0)
    g0 = P.Elev((GAP, -1.35, .65), ELEV)
    g1 = P.Elev((-GAP, -1.35, .65), ELEV)
    # The cradle (mantlet block) carrying both barrels.
    k.block(a.part('Cradle', 'Armor', t), (2.2, .7, .9), loc=(0, -1.45, .65), rot=(-ELEV * .5, 0, 0), chamfer=.08)
    for g, name, brake in ((g0, 'Main_cannon', 'Muzzle_brake'), (g1, 'Main_cannon_2', 'Muzzle_brake_2')):
        bp = a.part(name, 'Steel', t)
        k.lathe(bp, [(.3, 0), (.3, .6), (.24, .75), (.2, 1.5), (.17, 4.1), (0, 4.1)], loc=g.at(0), rot=g.lathe_rot,
                seg=14, worn=(1,))
        band = a.part('Collar_band', 'Steel', t)
        for z in (.9, 2.3, 3.5):
            band.cyl(.22, .1, loc=g.at(z), rot=g.lathe_rot, seg=14, bevel=0)
        rec = a.part('Recuperators', 'Steel', t)
        k.lathe(rec, [(.11, 0), (.11, 1.3), (.07, 1.36)], loc=g.at(-.2, up=.38), rot=g.lathe_rot, seg=8)
        mb = a.part(brake, 'Undercarriage', t)
        prof = [(.17, 0)]
        for j in range(4):
            z = .08 + j * .15
            prof += [(.3, z), (.3, z + .09), (.22, z + .1)]
        prof += [(.22, .7), (0, .7)]
        k.lathe(mb, prof, loc=g.at(4.08), rot=g.lathe_rot, seg=12)
    a.pivot('Muzzle_main', g0.at(4.8), t)
    # The cupola with its vision blocks, the rangefinder's arms out of both cheeks, hatches, vents, the roof kit.
    cup = a.part('Cupola', 'Armor', t)
    k.lathe(cup, [(.45, 0), (.45, .35), (.35, .45), (0, .47)], loc=(-.8, .6, 1.45), seg=14)
    glass = a.part('Cupola_glass', 'Glass', t)
    for i in range(6):
        u = i * math.tau / 6
        glass.box((.16, .02, .08), loc=(-.8 + math.cos(u) * .455, .6 + math.sin(u) * .455, 1.7), rot=(0, 0, u + R90),
                  bevel=0)
    rf = a.part('Rangefinder', 'Armor', t)
    for s in (-1, 1):
        k.lathe(rf, [(.16, 0), (.16, .7), (.2, .74), (.2, .92), (0, .92)], loc=(s * 1.7, -.2, 1.15),
                rot=(0, s * R90, 0), seg=10)
        a.part('Rangefinder_glass', 'Glass', t).cyl(.12, .02, loc=(s * 2.63, -.2, 1.15), rot=(0, R90, 0), seg=10,
                                                    bevel=0)
    for (x, y) in ((.6, .3), (.5, 1.25)):
        k.ring(a.part('Hatches', 'Armor', t), [(.3, 0), (.36, 0), (.36, .07), (.3, .07)], loc=(x, y, 1.45), seg=12)
        k.lathe(a.part('Hatches', 'Armor', t), [(0, .1), (.28, .095), (.32, .07), (.32, .02)], loc=(x, y, 1.45),
                seg=12)
        K.handle(a.part('Hatch_fittings', 'Steel', t), (x - .1, y, 1.56), (x + .1, y, 1.56), (0, 0, 1), h=.05)
    vents = a.part('Vents', 'Steel', t)
    for x in (-1.1, -.4):
        k.lathe(vents, [(.16, 0), (.16, .2), (.24, .24), (.24, .3), (0, .32)], loc=(x, 1.55, 1.45), seg=10)
    k.block(a.part('Roof_kit', 'Armor', t), (.8, .5, .3), loc=(.2, 1.8, 1.6), chamfer=.04)
    ant = a.part('Antennas', 'Steel', t)
    for x in (1.3, -1.4):
        K.whip_antenna(ant, (x, 1.9, 1.45), h=1.6, r=.03, lean=.1)
    for s in (-1, 1):
        K.lamp(a, (s * 1.35, -1.25, 1.3), (0, -1, 0), r=.09, parent=t, mat='Armor', guard=True)
    a.part('Team_band', 'Team', t).box((3.3, 2.0, .02), loc=(0, .8, 1.46), bevel=0)
    return t


def _hoist(a, rng):
    """The shell hoist house at the rear left, the rails with the trolley and two shells, the gantry crane."""
    hx, hy = 2.5, 3.0
    hh = a.part('Hoist_house', 'Concrete')
    k.block(hh, (1.8, 1.6, 1.9), loc=(hx, hy, AP + .95), chamfer=.06)
    k.block(a.part('Hoist_roof', 'Armor'), (2.0, 1.8, .14), loc=(hx, hy, AP + 1.97), chamfer=.03)
    a.part('Hoist_door', 'Armor').box((.04, 1.1, 1.4), loc=(hx - .92, hy, AP + .75), bevel=0)
    a.part('Fascia', 'Hazard').box((.05, 1.3, .16), loc=(hx - .93, hy, AP + 1.55), bevel=0)
    K.beacon(a, (hx + .5, hy + .4, AP + 2.04), r=.1)
    # Rails from the hoist to the citadel's door, the trolley on them, two giant shells with driving bands.
    rails = a.part('Rails', 'Steel')
    sleepers = a.part('Rail_sleepers', 'LogWood')
    for s in (-1, 1):
        rails.box((.06, 2.4, .08), loc=(hx - 1.05 + s * .35, hy - .55, AP + .04), rot=(0, 0, .35), bevel=0)
    for j in range(6):
        sleepers.box((1.0, .16, .05), loc=(hx - 1.45 + j * .17, hy - 1.5 + j * .38, AP + .02), rot=(0, 0, .35),
                     bevel=0)
    tr = a.part('Trolley', 'Armor')
    tx, ty = hx - 1.15, hy - .8
    k.block(tr, (.9, 1.3, .18), loc=(tx, ty, AP + .2), rot=(0, 0, .35), chamfer=.03)
    for (dx, dy) in ((-.3, -.45), (.3, -.45), (-.3, .45), (.3, .45)):
        tr.cyl(.1, .06, loc=(tx + dx, ty + dy, AP + .1), rot=(0, R90, .35), seg=8, bevel=0)
    shells = a.part('Shells', 'Steel')
    bands = a.part('Shell_bands', 'Gilded')
    for dx in (-.2, .2):
        c = (tx + dx * math.cos(.35), ty + dx * math.sin(.35), AP + .47)
        k.lathe(shells, [(.17, -.6), (.17, .25), (.12, .5), (.04, .62), (0, .64)], loc=c, rot=(R90, 0, .35 + math.pi),
                seg=10)
        bands.cyl(.18, .06, loc=c, rot=(R90, 0, .35), seg=10, bevel=0)
    # The gantry crane over the trolley: legs, beam, the hook block on its cable.
    cr = a.part('Crane', 'Team')
    for (dx, dy) in ((-.75, -.25), (.75, -.25)):
        cr.limb((tx + dx, ty + dy - .5, AP), (tx + dx * .9, ty + dy - .5, AP + 2.5), .1, .1, bevel=0)
        cr.limb((tx + dx, ty + dy + .9, AP), (tx + dx * .9, ty + dy + .5, AP + 2.5), .1, .1, bevel=0)
    k.block(cr, (1.6, .2, .2), loc=(tx, ty - .25, AP + 2.55), chamfer=.03)
    a.part('Crane_cable', 'Undercarriage').tube([(tx, ty - .25, AP + 2.45), (tx, ty - .25, AP + 1.3)], .015, seg=3)
    k.block(a.part('Hook_block', 'Armor'), (.18, .14, .22), loc=(tx, ty - .25, AP + 1.2), chamfer=.02)
    # Garrison clutter: a sandbag niche, shell crates.
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    for (x, y, r) in ((-2.6, 2.6, .2), (-2.9, 2.0, -.3)):
        K.crate(crates, straps, (.9, .45, .4), (x, y, AP), rot=(0, 0, r), bands=2)


def super_gun(a):
    """The fortress super-gun: see the module docstring."""
    rng = random.Random(3661)
    _apron(a, rng)
    _citadel(a)
    _gun_house(a)
    _hoist(a, rng)
    k.clean(a)


BUILDERS = {
    'super_gun': (super_gun, dict(ao_distance=.9, grime_height=.6)),
}
