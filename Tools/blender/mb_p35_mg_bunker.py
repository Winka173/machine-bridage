"""Prompt 35 wave 7 (lane C): the MG bunker and its twin-gun branch rebuilt from scratch (specs:
Tools/blender/specs/mg_bunker.json, mg_bunker_a.json).

Both in the style of lane A's mg_bunker_b (wave 2: a round cast pillbox in an earth mound with a turning cupola), so
the flame branch and the twin branch read as upgrades of the base:

- mg_bunker (bunker_hmg, NSV 12.7 mm): the earth mound with turf and a sandbag course on its rear crest, the cast
  drum with its firing slits, the Team band and the race ring; the turning cast-steel cupola (`Turret`) with its
  embrasure, the NSV on its cradle with the flash hider, a periscope, the hatch and the bolt ring; behind, the
  sandbagged ammunition pit with its boxes, the entry trench with steps down to the door, the vent stack and the
  whip; concertina wire and pickets in front.
- mg_bunker_a (bunker_hmg_twin): the same pillbox with a bolted armour collar on the cupola, the widened embrasure
  with the Team twin mantlet and two jacketed NSV barrels well out of the wall, a second ammunition stack and a
  second sandbag course.

Runtime nodes kept: `Turret`, `Main_cannon` (+ `Main_cannon_2`), `Muzzle_brake` (+ `_2`), `Muzzle_main`, and the old
files' `Mount_missile` / `Muzzle_missile` (plain pivots on the cupola roof; the defs carry no missile). Metres, +Z up,
-Y front, +X left. Each under 6,000 triangles (owner decision 6).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
G = .05
TZ = .97


def _pillbox(a, courses=1, collar=False):
    """The mound, the drum, the race, the cupola shell; returns the Turret pivot."""
    k.lathe(a.part('Berm', 'Dirt'), [(2.2, G), (1.78, .52), (1.58, .6)], seg=18, caps=(False, False), worn=(1,))
    for i, (u, w) in enumerate(((.4, .9), (1.5, .7), (2.5, 1.0), (3.6, .8), (4.7, .9), (5.6, .7))):
        a.part('Berm_turf', 'Grass').box((w, .5, .03), loc=(math.cos(u) * 1.92, math.sin(u) * 1.92, .33),
                                         rot=(0, .68, u), bevel=0)
    W.bags(a, [(math.cos(t) * 1.78, math.sin(t) * 1.78, .53) for t in [math.radians(d) for d in range(30, 151, 20)]],
           layers=courses, bag=(.55, .3, .16), seed=40 + courses)
    k.lathe(a.part('Walls', 'Plaster'), [(1.62, .48), (1.56, .88), (1.5, .92)], seg=18, caps=(False, False),
            worn=(2,))
    a.part('Team_band', 'Team').cyl(1.545, .1, loc=(0, 0, .8), seg=18, bevel=0)
    for d in (-55, 55, 125, 235):
        t = math.radians(d - 90)
        a.part('Slits', 'Undercarriage').box((.36, .06, .09), loc=(math.cos(t) * 1.58, math.sin(t) * 1.58, .68),
                                             rot=(0, 0, t + R90), bevel=0)
    k.ring(a.part('Race', 'Steel'), [(1.3, .9), (1.44, .9), (1.44, .97), (1.3, .97)], seg=18)
    t = a.pivot('Turret', (0, 0, TZ))
    k.lathe(a.part('Turret_body', 'Armor', t), [(1.38, 0), (1.36, .18), (1.18, .42), (.82, .6), (.32, .68), (0, .69)],
            seg=16, caps=(False, True), worn=(1, 3))
    a.part('Turret_band', 'Team', t).cyl(1.28, .08, loc=(0, 0, .28), seg=16, bevel=0)
    bolts = a.part('Kit_bolts', 'Steel', t)
    for i in range(14):
        u = i * TAU / 14
        bolts.cyl(.03, .03, loc=(math.cos(u) * 1.24, math.sin(u) * 1.24, .4), seg=4, bevel=0)
    if collar:
        cl = a.part('Turret_collar', 'Armor', t)
        for i in range(8):
            u = i * TAU / 8 + TAU / 16
            if abs(math.sin(u) + 1) < .35:             # leave the embrasure clear
                continue
            K.plate(cl, (.9, .08, .32), loc=(math.cos(u) * 1.36, math.sin(u) * 1.36, .14), rot=(0, 0, u + R90),
                    chamfer=.012)
            for dz in (.06, .22):
                bolts.cyl(.025, .03, loc=(math.cos(u) * 1.41, math.sin(u) * 1.41, dz), rot=(0, R90, u), seg=4,
                          bevel=0)
    K.periscope(a, (-.45, -.5, .62), facing=(0, -1, 0), parent=t)
    k.lathe(a.part('Hatches', 'Armor', t), [(.36, .62), (.36, .7), (0, .74)], loc=(.2, .35, 0), seg=10)
    K.handle(a.part('Kit_handles', 'Steel', t), (.05, .35, .75), (.35, .35, .75), (0, 0, 1), h=.05)
    # The old files' missile mount pivot on the cupola roof (no missile in the defs).
    m = a.pivot('Mount_missile', (.3, -.58, .7), t)
    a.pivot('Muzzle_missile', (0, -.74, .24), m)
    return t


def _rear(a, stacks=1, concertina=False):
    """The sandbagged ammunition pit, the entry trench and the door, the vent stack, the whip, the yard."""
    k.extrude(a.part('Base', 'Concrete'), [(-1.3, 1.3), (1.3, 1.3), (1.4, 1.95), (-1.4, 1.95)], .1,
              loc=(0, 0, G + .05), axis='Z', corner=.04, caps=(False, True))
    W.bags(a, [(-1.5, 1.25, G), (-1.6, 1.95, G), (1.6, 1.95, G), (1.5, 1.25, G)], layers=2, bag=(.55, .3, .16),
           seed=46)
    W.stack(a, (-.6, 1.62, G + .1), n=3, size=(.55, .3, .22), yaw=.1, seed=47)
    if stacks > 1:
        W.stack(a, (.25, 1.64, G + .1), n=2, size=(.55, .3, .22), yaw=-.2, seed=48)
    k.block(a.part('Door_well', 'Plaster'), (1.0, .55, .8), loc=(1.15, 1.25, .4), rot=(0, 0, -.5), chamfer=.03)
    K.door(a, (1.3, 1.5, .1), (.7, .7), normal=(.48, .88, 0), mat='Armor')
    st = a.part('Steps', 'Concrete')
    for j in range(3):
        st.box((.6, .2, .08), loc=(1.4 + j * .09, 1.6 + j * .13, .1), rot=(0, 0, -.5), bevel=0)
    k.lathe(a.part('Vents', 'Steel'), [(.08, 0), (.08, 1.3), (.17, 1.32), (.17, 1.4), (0, 1.46)],
            loc=(-1.1, .9, .55), seg=8, worn=(3,))
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, 1.3, .6), h=2.6, r=.022)
    K.lamp(a, (.95, 1.0, .85), (.4, .9, -.2), r=.06, guard=True)
    if concertina:
        K.wire_fence(a, [(-1.6, -2.45, G), (0, -2.55, G), (1.6, -2.45, G)], h=.6, post=.8, strands=2, concertina=True)
    else:
        K.wire_fence(a, [(-1.5, -1.95, G), (0, -2.05, G), (1.5, -1.95, G)], h=.55, post=.75, strands=2, concertina=True)
    for i in range(10):
        u = i * TAU / 10 + .3
        a.part('Pickets', 'Wood').cyl(.03, .7, loc=(math.cos(u) * 2.12, math.sin(u) * 2.12, G + .3), seg=4, bevel=0)
    rk = a.part('Stones', 'Rock')
    for i in range(18):
        x = -2.1 + 4.2 * ((i * .618) % 1.0)
        y = -2.4 + 4.6 * ((i * .382 + .13) % 1.0)
        if x * x + y * y < 4.2 and y > -2.0:
            continue
        sz = .1 + (i % 4) * .04
        rk.box((sz, sz * 1.3, sz * .6), loc=(x, y, G + sz * .2), rot=(i * .7, i * .3, i * 1.3), bevel=0)
    # Side firing positions of sandbags, the spare barrel case, the range card board, a jerrycan.
    for s_ in (-1, 1):
        W.bags(a, [(s_ * 2.0, -.9, G), (s_ * 2.15, -.2, G), (s_ * 2.05, .5, G)], layers=1, bag=(.5, .28, .15),
               seed=50 + s_)
    k.block(a.part('Barrel_case', 'Wood'), (.2, 1.3, .16), loc=(-1.0, 1.05, G + .62), rot=(.05, 0, .3), chamfer=.02)
    a.part('Signs', 'PlasterWhite').box((.4, .03, .3), loc=(1.65, -1.2, G + .55), rot=(0, 0, -.6), bevel=0)
    a.part('Sign_posts', 'Wood').cyl(.025, .55, loc=(1.66, -1.18, G + .27), seg=4, bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-1.25, 1.5, G + .1), rot=(0, 0, .3))
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 2.0, math.sin(u) * 2.0, G), radius=1.0, k=.3)


def _nsv(a, t, x, name, brake, length, jacket=False):
    """One NSV barrel out of the embrasure along -Y from the cradle, its flash hider (and a cooling jacket)."""
    y0 = -1.45
    k.lathe(a.part(name, 'Steel', t), [(.045, 0), (.045, .2), (.03, .25), (.026, length), (0, length)],
            loc=(x, y0, .22), rot=K.FORWARD, seg=8, worn=(1,))
    if jacket:
        a.part(f'{name}_jacket', 'Armor', t).cyl(.05, length * .45, loc=(x, y0 - .15 - length * .22, .22),
                                                 rot=K.FORWARD, seg=8, bevel=0)
    k.lathe(a.part(brake, 'Undercarriage', t), [(.026, 0), (.042, .02), (.042, .14), (.03, .16), (0, .16)],
            loc=(x, y0 - length + .02, .22), rot=K.FORWARD, seg=8)
    return (x, y0 - length - .14, .22)


def mg_bunker(a, detail=False):
    """The MG bunker (see the module docstring)."""
    t = _pillbox(a, courses=1)
    k.block(a.part('Embrasure', 'Armor', t), (.62, .45, .42), loc=(0, -1.3, .22), chamfer=.04)
    a.part('Embrasure_slot', 'Undercarriage', t).box((.36, .03, .14), loc=(0, -1.53, .22), bevel=0)
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.24, .2, .2), loc=(0, -1.55, .22), c=.03)
    end = _nsv(a, t, 0, 'Main_cannon', 'Muzzle_brake', .9)
    a.pivot('Muzzle_main', end, t)
    a.part('Ammo_belt', 'Gilded', t).tube([(.08, -1.4, .26), (.18, -1.2, .3), (.25, -1.0, .28)], .025, seg=4)
    _rear(a, stacks=1)
    k.clean(a)


def mg_bunker_a(a, detail=False):
    """The twin MG bunker (see the module docstring)."""
    t = _pillbox(a, courses=2, collar=True)
    k.block(a.part('Embrasure', 'Armor', t), (.9, .45, .45), loc=(0, -1.3, .22), chamfer=.04)
    a.part('Embrasure_slot', 'Undercarriage', t).box((.66, .03, .16), loc=(0, -1.53, .22), bevel=0)
    K.chamfer_box(a.part('Twin_mantlet', 'Team', t), (.66, .3, .3), loc=(0, -1.6, .22), c=.04)
    end = _nsv(a, t, -.17, 'Main_cannon', 'Muzzle_brake', 1.5, jacket=True)
    _nsv(a, t, .17, 'Main_cannon_2', 'Muzzle_brake_2', 1.5, jacket=True)
    a.pivot('Muzzle_main', (0, end[1], end[2]), t)
    belt = a.part('Ammo_belt', 'Gilded', t)
    for s in (-1, 1):
        belt.tube([(s * .28, -1.45, .26), (s * .4, -1.2, .32), (s * .45, -.95, .28)], .025, seg=4)
    K.periscope(a, (.5, -.45, .62), facing=(0, -1, 0), parent=t, size=(.14, .12, .1))
    _rear(a, stacks=2, concertina=True)
    k.clean(a)


BUILDERS = {
    'mg_bunker': (mg_bunker, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
    'mg_bunker_a': (mg_bunker_a, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
}
