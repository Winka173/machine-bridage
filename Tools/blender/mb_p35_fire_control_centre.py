"""Prompt 35 wave 3 (lane B): the fire-control centre rebuilt from scratch (spec:
Tools/blender/specs/fire_control_centre.json).

A field fire-direction centre (FDC) dug in by the Accord (the def's modelSize 6.0 x 6.0 x 5.5 m): a half-buried
command dug-out with log walls showing above an earth berm, a log roof under a layer of earth and two courses of
sandbags, vision slits and a stove pipe, the entrance trench at the back revetted with planks and steps down; beside it
the canvas operations tent on its frame (the plotting room) with guy ropes; at the rear corner a guyed lattice mast
with the turning surveillance radar on top (`Radar`, it spins as before) and a VHF dipole; whip antennas on the roof,
the generator on its skid with its exhaust, cable reels and the cables to the dug-out; a small camouflage net over
the roof's front left corner.

Its own body: not the troop shelter's (a cast concrete bunker) nor the bunker shelter tower's (a corrugated-steel arch).
Runtime node kept: `Radar`; old part names `Base`, `Berm`, `Bunker`, `Roof`, `Roof_deck`, `Sandbags`, `Embrasures`,
`Shelter`, `Shelter_ribs`, `Shelter_doors`, `Mast`, `Radar_array`, `Antenna`, `Generator`, `Generator_skid`,
`Generator_stack`, `Generator_vents`, `Camo_net`, `Vents`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
PAD = 0.0                                  # the ground (no pad: the site is dug into the terrain)
BX, BY, BW, BD = .7, -.75, 3.6, 3.0       # the dug-out's centre and size (X, Y)
WALL = 1.0                                 # log wall showing above the pad
RZ = PAD + WALL                            # the roof logs' underside


def _ground(a, rng):
    # Duckboards (the site's floor) from the tent to the dug-out's trench and to the mast.
    duck = a.part('Floor', 'Wood')
    for (x0, y0, x1, y1) in ((-1.6, .5, BX - .3, 1.3), (BX + .5, 1.5, 2.2, 2.2)):
        n = int(math.hypot(x1 - x0, y1 - y0) / .3)
        ang = math.atan2(y1 - y0, x1 - x0)
        for i in range(n):
            f = (i + .5) / n
            duck.box((.12, .6, .04), loc=(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, .03), rot=(0, 0, ang), bevel=0)
        duck.box(((n * .3), .05, .04), loc=((x0 + x1) / 2, (y0 + y1) / 2, .01), rot=(0, 0, ang), bevel=0)
    # The berm heaped against the dug-out's three outer walls (sloped: the gate's body).
    berm = a.part('Berm', 'Dirt')
    for (x, y, w, d, r) in ((BX, BY - BD / 2 - .35, BW + .9, .75, 0), (BX + BW / 2 + .35, BY, BD, .75, R90),
                            (BX - BW / 2 - .35, BY - .4, BD - .8, .75, R90)):
        k.block(berm, (w, d, WALL * .7), loc=(x, y, PAD + WALL * .35), rot=(0, 0, r), chamfer=.1, taper=(.95, .4))
    st = a.part('Stones', 'Rock')
    for j in range(16):
        z = rng.uniform(.05, .12)
        st.box((z * 1.3, z, z * .7), loc=(rng.uniform(-2.8, 2.8), rng.uniform(-2.8, 2.8), PAD + z * .15),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)
    for i in range(8):
        K.dust(a, (rng.uniform(-2.6, 2.6), rng.uniform(-2.6, 2.6), PAD), radius=1.3, k=.25)


def _dugout(a, rng):
    logs = a.part('Bunker', 'LogWood')
    x0, x1, y0, y1 = BX - BW / 2, BX + BW / 2, BY - BD / 2, BY + BD / 2
    # Log walls: four courses on each side (cut a little differently), the rear wall broken by the door.
    for j in range(4):
        z = PAD + .12 + j * .24
        for (p, q) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x0, y0), (x0, y1)), ((x0, y1), (BX - .45, y1)),
                       ((BX + .45, y1), (x1, y1))):
            L = math.hypot(q[0] - p[0], q[1] - p[1]) + .2 + rng.uniform(-.08, .08)
            ang = math.atan2(q[1] - p[1], q[0] - p[0])
            logs.cyl(.12 + rng.uniform(-.01, .01), L, loc=((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, z),
                     rot=(0, R90, ang), seg=6, bevel=0)
    # The roof: logs laid across, a layer of earth, sandbags on it; the vision slits in the front wall.
    roof = a.part('Roof', 'LogWood')
    n = 12
    for i in range(n):
        y = y0 + .1 + i * (BD - .2) / (n - 1)
        roof.cyl(.11, BW + .5 + rng.uniform(-.1, .1), loc=(BX, y, RZ + .11), rot=(0, R90, 0), seg=6, bevel=0)
    k.block(a.part('Roof_deck', 'Dirt'), (BW + .3, BD + .2, .22), loc=(BX, BY, RZ + .22 + .11), chamfer=.08,
            taper=(.92, .9))
    top = RZ + .44
    P.sandbag_run(a, [(x0 + .2, y0 + .25, top), (x1 - .2, y0 + .25, top), (x1 - .2, y1 - .25, top),
                      (x0 + .2, y1 - .25, top)], courses=1, bag=(.62, .36, .17), part='Sandbags', seed=121,
                  closed=True, lean=True)
    P.sandbag_run(a, [(x0 + .6, BY - .3, top), (x1 - .6, BY - .3, top)], courses=2, bag=(.62, .36, .17),
                  part='Sandbags', seed=122, lean=True)
    slit = a.part('Embrasures', 'Undercarriage')
    for x in (BX - .8, BX + .8):
        slit.box((.7, .06, .14), loc=(x, y0 - .13, PAD + .78), bevel=0)
        a.part('Slit_frames', 'Wood').box((.82, .08, .04), loc=(x, y0 - .14, PAD + .87), bevel=0)
    # The stove pipe through the roof, its cap; the entrance trench at the back with plank revetment and steps.
    k.lathe(a.part('Vents', 'Steel'), [(.07, 0), (.07, .9), (.12, .92), (.12, .98), (0, 1.0)],
            loc=(x1 - .5, y1 - .6, top), seg=8)
    K.soot(a, (x1 - .5, y1 - .6, top + 1.0), radius=.3, k=.45)
    plank = a.part('Trench_planks', 'Wood')
    for s in (-1, 1):
        for j in range(3):
            plank.box((.04, 1.3, .22), loc=(BX + s * .5, y1 + .7, PAD + .12 + j * .24), bevel=0)
    st = a.part('Steps', 'Wood')
    for j in range(3):
        st.box((.85, .3, .06), loc=(BX, y1 + 1.2 - j * .32, PAD + .55 - j * .2), bevel=0)
    K.door(a, (BX, y1 + .02, PAD), size=(.8, .95), normal=(0, 1, 0), mat='Wood')


def _tent(a):
    """The canvas operations tent on its frame (rear right of the site)."""
    tx, ty = -1.6, 1.65
    w, d, h0, h1 = 2.0, 2.2, 1.6, 2.3
    shel = a.part('Shelter', 'Canvas')
    rings = []
    for y in (ty - d / 2, ty + d / 2):
        rings.append([(tx - w / 2, y, PAD), (tx - w / 2, y, PAD + h0), (tx, y, PAD + h1), (tx + w / 2, y, PAD + h0),
                      (tx + w / 2, y, PAD)])
    shel.loft(rings, bevel=0)
    ribs = a.part('Shelter_ribs', 'Undercarriage')
    for y in (ty - d / 2 + .02, ty, ty + d / 2 - .02):
        ribs.tube([(tx - w / 2 - .02, y, PAD), (tx - w / 2 - .02, y, PAD + h0), (tx, y, PAD + h1 + .02),
                   (tx + w / 2 + .02, y, PAD + h0), (tx + w / 2 + .02, y, PAD)], .025, seg=4)
    k.extrude(a.part('Shelter_doors', 'Canvas'), [(-.4, 0), (.4, 0), (.4, 1.5), (0, 1.75), (-.4, 1.5)], .03,
              loc=(tx, ty - d / 2 - .03, PAD), rot=(R90, 0, 0), axis='Z', chamfer=0)
    ropes = a.part('Guy_ropes', 'Undercarriage')
    for sx in (-1, 1):
        for y in (ty - d / 2 + .1, ty + d / 2 - .1):
            ropes.tube([(tx + sx * w / 2, y, PAD + h0), (tx + sx * (w / 2 + .35), y, PAD + .05)], .008, seg=3)
            a.part('Stakes', 'Wood').box((.04, .04, .2), loc=(tx + sx * (w / 2 + .37), y, PAD + .08), bevel=0)
    a.part('Team_band', 'Team').box((w + .02, .02, .25), loc=(tx, ty - d / 2 - .015, PAD + 1.2), bevel=0)


def _mast(a):
    mx, my = 2.35, 2.35
    mast = a.part('Mast', 'Steel')
    H = 4.6
    for (dx, dy) in ((-.12, -.12), (.12, -.12), (.12, .12), (-.12, .12)):
        mast.box((.035, .035, H), loc=(mx + dx, my + dy, PAD + H / 2), bevel=0)
    for j in range(8):
        z = PAD + .3 + j * .55
        for (p, q) in (((-.12, -.12), (.12, .12)), ((.12, -.12), (-.12, .12))):
            mast.limb((mx + p[0], my + p[1], z), (mx + q[0], my + q[1], z + .5), .015, .015, bevel=0)
    guys = a.part('Guy_wires', 'Undercarriage')
    for (gx, gy) in ((-1.5, -.3), (.35, -1.6), (.5, .45)):
        guys.tube([(mx, my, PAD + H * .8), (mx + gx, my + gy, PAD + .02)], .007, seg=3)
    # The surveillance radar on top, spinning (`Radar`): its drive, the bar antenna, the feed.
    k.lathe(a.part('Radar_drive', 'Armor'), [(.18, 0), (.18, .15), (.1, .2), (0, .2)], loc=(mx, my, PAD + H), seg=10)
    r = a.pivot('Radar', (mx, my, PAD + H + .2))
    k.block(a.part('Radar_array', 'Team', r), (1.4, .16, .36), loc=(0, 0, .25), chamfer=.03)
    a.part('Radar_face', 'Undercarriage', r).box((1.3, .01, .3), loc=(0, -.085, .25), bevel=0)
    a.part('Radar_hub', 'Armor', r).cyl(.05, .1, loc=(0, 0, .05), seg=6, bevel=0)
    # The VHF dipole on a side arm.
    mast.box((.6, .03, .03), loc=(mx - .3, my, PAD + H - .5), bevel=0)
    a.part('Antenna', 'Steel').box((.02, .02, 1.0), loc=(mx - .6, my, PAD + H - .5), bevel=0)


def _kit(a):
    # Whip antennas on the dug-out roof, the generator skid, cable reels, the cables.
    ant = a.part('Antenna', 'Steel')
    for (x, y, h) in ((BX - 1.4, BY - .2, 2.2), (BX + 1.5, BY + .9, 1.8), (BX - 1.2, BY + 1.0, 1.6)):
        K.whip_antenna(ant, (x, y, RZ + .62), h=h, r=.022, lean=.05)
    gx, gy = 2.3, .2
    k.block(a.part('Generator_skid', 'Undercarriage'), (.7, 1.3, .1), loc=(gx, gy, PAD + .05), chamfer=.02)
    k.block(a.part('Generator', 'Armor'), (.62, 1.15, .7), loc=(gx, gy, PAD + .45), chamfer=.04)
    vents = a.part('Generator_vents', 'Undercarriage')
    for j in range(4):
        vents.box((.012, .8, .04), loc=(gx - .315, gy, PAD + .3 + j * .1), bevel=0)
    a.part('Generator_stack', 'Steel').cyl(.05, .5, loc=(gx + .15, gy + .35, PAD + 1.05), seg=8, bevel=0)
    K.soot(a, (gx + .15, gy + .35, PAD + 1.3), radius=.3, k=.4)
    reel = a.part('Cable_reels', 'Wood')
    for (x, y) in ((-.3, 2.6), (.15, 2.7)):
        for s in (-1, 1):
            reel.cyl(.22, .03, loc=(x + s * .12, y, PAD + .22), rot=(0, R90, 0), seg=10, bevel=0)
        a.part('Cable_coils', 'Undercarriage').cyl(.16, .22, loc=(x, y, PAD + .22), rot=(0, R90, 0), seg=10, bevel=0)
    cab = a.part('Kit_cables', 'Undercarriage')
    cab.tube([(gx - .3, gy + .5, PAD + .1), (BX + BW / 2 + .3, BY + 1.2, PAD + .05), (BX + .6, BY + BD / 2 + .2,
                                                                                    PAD + .3)], .025, seg=4)
    cab.tube([(2.35, 2.2, PAD + .3), (1.0, 1.9, PAD + .03), (BX + .3, BY + BD / 2 + .2, PAD + .3)], .02, seg=4)
    cab.tube([(-1.75, .5, PAD + .05), (-.6, .9, PAD + .03), (BX - .3, BY + BD / 2 + .2, PAD + .3)], .02, seg=4)
    # A sandbagged slit trench at the front left (the sentry's), crates of field telephones at the rear right.
    P.sandbag_run(a, [(-2.75, -2.3, 0), (-1.3, -2.3, 0), (-1.3, -1.1, 0), (-2.75, -1.1, 0)], courses=2,
                  bag=(.55, .32, .16), part='Sandbags', seed=124, closed=True, lean=True)
    k.block(a.part('Trench_floor', 'Charred'), (1.0, .7, .02), loc=(-2.1, -1.75, .01), chamfer=0)
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    for j, (x, y, z, r) in enumerate(((1.75, 1.35, 0, .1), (1.75, 1.35, .32, .25), (1.3, .95, 0, -.2))):
        K.crate(crates, straps, (.7, .45, .32), (x, y, z), rot=(0, 0, r), bands=1)
    # A small camouflage net over the dug-out's front left corner only (the roof's sandbags stay visible).
    x0, y0 = BX - BW / 2, BY - BD / 2
    P.camo_net(a, [(x0 - .25, y0 - .45, 1.45), (x0 + 1.3, y0 - .45, 1.5), (x0 + 1.2, y0 + .9, 1.75),
                   (x0 - .2, y0 + .9, 1.7)], .12, PAD, garnish=8, seed=123)


def fire_control_centre(a):
    """The fire-control centre: see the module docstring."""
    rng = random.Random(3611)
    _ground(a, rng)
    _dugout(a, rng)
    _tent(a)
    _mast(a)
    _kit(a)
    k.clean(a)


BUILDERS = {
    'fire_control_centre': (fire_control_centre, dict(ao_distance=.6, grime_height=.6)),
}
