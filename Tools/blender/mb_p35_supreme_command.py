"""Prompt 35 wave 9 (lane C): the Supreme Command boss rebuilt from scratch (spec:
Tools/blender/specs/supreme_command.json).

"Tổng Tư Lệnh", a super-heavy four-axle armoured command post (unit_refs: the MZKT-7930 chassis, an armoured mobile
command post; the old file's 14.6 x 5.0 x 11.2 m kept, its height the telescopic mast): the armoured cab-forward
cab with slit windows behind armoured shutters, the bull bar and the searchlights; the long frame on four axles of
big lugged tyres under armoured wheel arches with skirts; the tall command module with sloped armoured sides
(riveted plates, the team band, vision blocks, doors with steps and the rear ladder), the roof with its railings,
the two boss 12.7 mm turrets forward (`Part_mg`, `Part_mg.001`, each with `Mount_mg` / `Muzzle_mg`: the def's
main and secondary boss_hmg), the satellite dishes on their posts, the generator and air-conditioning housings,
the flag on its pole; the telescopic antenna mast at the rear with its yards and guy wires (`Part_antenna`, the
breakable antenna that stops the aura); smoke dischargers, jerrycans, spare wheels, cable reels, crates.

Runtime nodes kept: `Part_mg`, `Part_mg.001`, `Mount_mg`, `Mount_mg.001`, `Muzzle_mg`, `Muzzle_mg.001`,
`Part_antenna` (boss parts and their positions as in balance.json). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
WR = .95
AXLES = (-4.7, -2.75, 2.3, 4.25)
TX = 1.92
FZ = 1.65            # frame top
ROOF = 5.25          # the command module's roof
NOSE, TAIL = -7.3, 7.3


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE, [(0, FZ - .3), (2.05, FZ - .3), (2.1, 2.6), (1.95, 2.75), (0, 2.75)]),
        (NOSE + .7, [(0, FZ - .3), (2.15, FZ - .3), (2.2, 2.8), (1.75, 4.3), (0, 4.35)]),
        (NOSE + 3.1, [(0, FZ - .3), (2.15, FZ - .3), (2.2, 2.8), (1.8, 4.4), (0, 4.42)]),
    ])
    # Slit windows behind armoured shutters, the cab doors, the bull bar, searchlights, lamps.
    sh = a.part('Shutters', 'Armor')
    for x in (-1.1, -.37, .37, 1.1):
        a.part('Glass', 'Glass').box((.6, .02, .14), loc=(x, NOSE + .45, 3.65), rot=(-.37, 0, 0), bevel=0)
        K.plate(sh, (.66, .05, .3), loc=(x, NOSE + .36, 3.88), rot=(-1.0, 0, 0), chamfer=.01)
    for s in (-1, 1):
        for y in (NOSE + 1.4, NOSE + 2.5):
            a.part('Glass', 'Glass').box((.02, .6, .14), loc=(s * 2.03, y, 3.65), rot=(0, s * .3, 0), bevel=0)
        K.door(a, (s * 2.21, NOSE + 1.9, FZ + .1), size=(.9, 1.5), normal=(s, 0, 0), mat='Team')
        st = a.part('Steps', 'Steel')
        for i in range(2):
            st.box((.2, .7, .05), loc=(s * 2.15, NOSE + 1.9, .7 + i * .4), bevel=0)
        K.lamp(a, (s * 1.5, NOSE - .02, 2.2), (0, -1, 0), r=.13, guard=True)
        k.lathe(a.part('Searchlights', 'Armor'), [(.2, 0), (.22, .1), (.22, .3), (.18, .34)], loc=(s * 1.4, NOSE + .9, 4.32),
                rot=(R90 + .15, 0, 0), seg=10)
        a.part('Lamps', 'Lamp').cyl(.18, .02, loc=(s * 1.4, NOSE + .58, 4.38), rot=(R90 + .15, 0, 0), seg=10, bevel=0)
    K.grille(a, (0, NOSE - .01, 2.2), 2.0, .7, facing=(0, -1, 0), slats=8, frame_mat='Steel')
    bb = a.part('Bull_bar', 'Steel')
    bb.tube([(-1.9, NOSE - .1, FZ - .5), (-1.9, NOSE - .35, 2.6), (1.9, NOSE - .35, 2.6), (1.9, NOSE - .1, FZ - .5)],
            .07, seg=6, caps=False)
    for x in (-1.0, 0, 1.0):
        bb.limb((x, NOSE - .35, 2.6), (x, NOSE - .2, FZ - .4), .05, .05, bevel=0)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .8, NOSE - .15, FZ - .55), facing=(0, -1, 0), size=.14)
    for x in (-.6, .6):
        C.hatch(a, (x, NOSE + 1.9, 4.42), r=.32)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.3, 14.2, .5), loc=(s * .8, 0, FZ - .25), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .2, r=.13)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .62, s, seg=14)
    for y0, y1 in ((AXLES[0], AXLES[1]), (AXLES[2], AXLES[3])):
        for s in (-1, 1):
            arch = a.part('Wheel_arches', 'Armor')
            K.plate(arch, (.75, y1 - y0 + 2.2, .08), loc=(s * (TX + .05), (y0 + y1) / 2, WR * 2 + .15), chamfer=.015)
            sk = a.part('Skirts', 'Armor')
            for j in range(3):
                sk.box((.05, (y1 - y0 + 2.0) / 3 - .05, .5), loc=(s * (TX + .4), y0 - 1.0 + (j + .5) * (y1 - y0 + 2.0) / 3,
                                                                  WR * 2 - .15), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.2, .03, .12), loc=(s * 1.9, TAIL - .02, FZ + .2), bevel=0)
        C.stowage_box(a, (.5, 1.6, .5), (s * 2.05, -.2, FZ - .75), mat='Team', latches=3)
    K.tread_wheel(a, (2.15, 1.05, FZ - .1), .8, .45, 1, seg=12, tyre='Spare_wheel', rim='Spare_wheel_rim')
    K.tread_wheel(a, (-2.15, 1.05, FZ - .1), .8, .45, -1, seg=12, tyre='Spare_wheel', rim='Spare_wheel_rim')
    K.exhaust(a, (1.95, NOSE + 3.4, 3.2), r=.12, length=1.4, direction=(0, 0, 1))


def _module(a):
    """The command module: sloped armoured sides, plates and band, vision blocks, doors, ladder, roof fittings."""
    y0, y1 = NOSE + 3.3, TAIL - .1
    body = a.part('Hull', 'Team')
    C.slab_loft(body, C.octagon(4.4, y1 - y0, .2, y0=(y0 + y1) / 2), C.octagon(3.4, y1 - y0 - .5, .3,
                                                                             y0=(y0 + y1) / 2 + .1),
                FZ, ROOF, mid=(C.octagon(4.4, y1 - y0, .2, y0=(y0 + y1) / 2), FZ + 1.6))
    pl = a.part('Armor_plates', 'Armor')
    for s in (-1, 1):
        for i in range(5):
            y = y0 + .9 + i * 2.15
            K.armour_plate(a, pl, (1.0, 1.8, .06), (s * 2.23, y, FZ + .8), rot=K.rot_to((s, 0, 0)), rivet=.35)
        a.part('Team_band', 'Team').box((.03, 10.5, .25), loc=(s * 2.215, (y0 + y1) / 2, FZ + 1.5), bevel=0)
        for y in (-2.0, .5, 3.0, 5.5):
            a.part('Visors', 'Glass').box((.02, .3, .1), loc=(s * 1.98, y, ROOF - 1.1), rot=(0, s * .55, 0), bevel=0)
        K.smoke_dischargers(a, s * 1.9, y0 + .3, ROOF - .5, s, count=4)
    K.door(a, (2.22, 1.1, FZ + .15), size=(.9, 1.6), normal=(1, 0, 0), mat='Team')
    K.door(a, (0, y1 + .01, FZ + .15), size=(1.0, 1.7), normal=(0, 1, 0), mat='Team')
    K.ladder(a.part('Ladders', 'Steel'), (-1.2, y1 + .08, FZ + .1), (-1.2, y1 + .08, ROOF), width=.5, step=.35)
    # Roof: railings, hatches, generator and air-con housings, crates, the cable reel, the flag.
    rl = a.part('Railings', 'Steel')
    pts = [(-1.6, -2.0), (-1.6, 6.5), (1.6, 6.5), (1.6, -2.0)]
    rl.tube([(x, y, ROOF + .45) for x, y in pts], .03, seg=4, caps=False)
    for x, y in pts + [(-1.6, 2.2), (1.6, 2.2)]:
        rl.limb((x, y, ROOF), (x, y, ROOF + .45), .025, .025, bevel=0)
    for x, y in ((.0, -.6), (.0, 4.8)):
        C.hatch(a, (x, y, ROOF), r=.35)
    for i, (x, y) in enumerate(((-.9, 1.6), (.9, 1.6))):
        k.block(a.part('Air_con', 'Armor'), (1.1, .9, .45), loc=(x, y, ROOF + .225), chamfer=.04)
        K.grille(a, (x, y, ROOF + .46), .8, .6, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    k.block(a.part('Generator', 'Armor'), (1.4, 1.1, .6), loc=(.6, 6.1, ROOF + .3), chamfer=.05)
    K.exhaust(a, (1.1, 6.4, ROOF + .6), r=.06, length=.4, direction=(0, 0, 1))
    for j, (x, y) in enumerate(((-1.1, 3.4), (-1.1, 4.0), (1.1, 3.6))):
        K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.7, .5, .4), (x, y, ROOF), bands=1)
    C.cable_reel(a, (1.05, -1.4, ROOF + .3), r=.3, w=.45, axis='X')
    C.jerry_rack(a, (1.9, 5.8, FZ + .2), count=3, axis='Y')
    fp = a.part('Flag_pole', 'Steel')
    fp.cyl(.04, 2.2, loc=(1.4, 6.9, ROOF + 1.1), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.02, 1.0, .65), loc=(1.4, 7.42, ROOF + 1.85), bevel=0)
    # The satellite dishes on their posts.
    dp = a.part('Dish_posts', 'Steel')
    for x, y, r in ((-1.0, 5.6, .55), (.0, 3.0, .45)):
        dp.cyl(.06, .7, loc=(x, y, ROOF + .35), seg=6, bevel=0)
        K.dish(a.part('Dishes', 'PlasterWhite'), a.part('Dish_feeds', 'Steel'), (x, y, ROOF + .85), r=r,
               normal=(.3, -.5, .8), seg=14)


def _guns(a):
    """The two boss 12.7 mm turrets on the roof's front (boss parts mg_l / mg_r)."""
    for i, s in enumerate((1, -1)):
        loc = (s * 1.15, -2.75, 5.57)
        k.lathe(a.part('Gun_ring', 'Armor'), [(.62, ROOF), (.66, ROOF + .1), (.58, loc[2])], loc=(loc[0], loc[1], 0),
                seg=12)
        p = a.pivot(K.name('Part_mg', i), loc)
        m = a.pivot(K.name('Mount_mg', i), (0, 0, 0), p)
        tag = '' if i == 0 else '_r'
        sh = a.part(f'Gun_house{tag}', 'Team', m)
        C.slab_loft(sh, C.octagon(1.0, 1.1, .25, y0=.05), C.octagon(.7, .75, .18, y0=.1), 0, .5)
        a.part(f'Gun_shield{tag}', 'Armor', m).box((.8, .05, .36), loc=(0, -.5, .26), rot=(-.4, 0, 0), bevel=0)
        g = a.part(f'MG{tag}', 'Steel', m)
        for dx in (-.09, .09):
            k.lathe(g, [(.05, 0), (.05, .3), (.035, .35), (.03, 1.1), (0, 1.1)], loc=(dx, -.25, .46), rot=(R90 - .4, 0, 0),
                    seg=8, worn=(1,))
        k.block(a.part(f'MG_ammo{tag}', 'Crate', m), (.22, .35, .25), loc=(.3, .2, .5), chamfer=.02)
        K.periscope(a, (-.25, -.25, .5), facing=(0, -1, 0), parent=m, size=(.12, .1, .08))
        a.pivot(K.name('Muzzle_mg', i), (0, -1.14, .46), m)


def _mast(a):
    """The telescopic antenna mast at the rear (boss part antenna): sections, yards, aerials, guy wires."""
    p = a.pivot('Part_antenna', (-.6, 4.9, 4.1))
    k.block(a.part('Mast_base', 'Armor'), (.8, .8, .5), loc=(-.6, 4.9, ROOF), chamfer=.04)
    ms = a.part('Masts', 'Steel', p)
    sec = ((.16, 1.15, 3.0), (.12, 3.0, 5.2), (.09, 5.2, 7.0))
    for r, z0, z1 in sec:
        ms.cyl(r, z1 - z0 + .1, loc=(0, 0, (z0 + z1) / 2), seg=8, bevel=0)
        ms.cyl(r * 1.35, .1, loc=(0, 0, z1), seg=8, bevel=0)
    yd = a.part('Antennas', 'Steel', p)
    for z, w in ((4.6, 1.6), (6.2, 1.2)):
        yd.box((w, .06, .06), loc=(0, 0, z), bevel=0)
        for sx in (-1, 1):
            K.whip_antenna(yd, (sx * w / 2, 0, z), h=.7, r=.012)
    K.mesh_antenna(yd, (0, -.2, 6.6), w=.7, h=.5, normal=(0, -1, 0), bars=4)
    K.beacon(a, (0, 0, 7.05), parent=p, r=.08)
    guy = a.part('Kit_cables', 'Undercarriage')
    for gx, gy in ((-1.6, 3.6), (1.0, 3.8), (-1.5, 6.6), (.9, 6.7)):
        guy.tube([(-.6, 4.9, 4.1 + 4.4), (gx, gy, ROOF + .05)], .008, seg=3)


def supreme_command(a, detail=False):
    """The Supreme Command boss: see the module docstring."""
    K.suffixed(a)
    _cab(a)
    _chassis(a)
    _module(a)
    _guns(a)
    _mast(a)
    K.dust(a, (0, 0, .4), radius=7.0, k=.14)
    k.clean(a)


BUILDERS = {
    'supreme_command': (supreme_command, dict(ao_distance=1.0, grime_height=1.2)),
}
