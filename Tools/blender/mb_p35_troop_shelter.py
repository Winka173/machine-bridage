"""Prompt 35 wave 3 (lane B): the troop shelter rebuilt from scratch (spec: Tools/blender/specs/troop_shelter.json).

A half-buried concrete bunker with an earth berm (Strings note.troop_shelter; the def's modelSize 6.0 x 5.0 x 2.2 m,
the long side front to back as the data has it: the old file lay across): the cast concrete box showing 1.1 m above
the ground with its form-tie marks, the thick roof slab with chamfered edges under an earth cover and a ring of
sandbags, two mushroom ventilation stacks and a periscope hood on the roof; the earth berm heaped against the front
and both sides in two slopes; at the back the entrance ramp down to a steel door, the concrete apron, an L-shaped
sandbag blast baffle in front of the door, the door lamp; the Team band on the slab's edge; a whip antenna, water
cans, ammunition boxes and a duckboard walk. Concrete cast by the engineers, the earth and sandbags the Accord's.

Its own body: not the bunker shelter tower's (a corrugated steel arch under earth) nor the fire-control dug-out's.
Old part names kept where they still mean the same: `Base`, `Berm`, `Roof`, `Roof_ribs` (now the slab's edge beams),
`Sandbags`, `Vents`, `Ramp`, `Doorway`, `Coping`, `Antenna`, `Ammo_boxes`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
BW, BD = 3.0, 3.4            # the concrete box's width (X) and depth (Y)
BY = -.4                     # its centre line
WALLH = 1.15                 # the box showing above the ground
SLAB = .32                   # the roof slab's thickness
RZ = WALLH + SLAB            # top of the slab


def _bunker(a, rng):
    box = a.part('Bunker', 'Concrete')
    k.extrude(box, [(-BW / 2, BY - BD / 2), (BW / 2, BY - BD / 2), (BW / 2, BY + BD / 2), (-BW / 2, BY + BD / 2)],
              WALLH, loc=(0, 0, WALLH / 2), axis='Z', chamfer=.03, caps=(False, True))
    ties = a.part('Form_ties', 'Steel')
    for s in (-1, 1):
        for j in range(5):
            y = BY - BD / 2 + .4 + j * (BD - .8) / 4
            for z in (.35, .85):
                ties.cyl(.025, .03, loc=(s * (BW / 2 + .01), y, z), rot=(0, R90, 0), seg=5, bevel=0)
    # The roof slab, its edge beams (the old Roof_ribs) and the coping strip.
    k.block(a.part('Roof', 'Concrete'), (BW + .5, BD + .5, SLAB), loc=(0, BY, WALLH + SLAB / 2), chamfer=.07)
    for s in (-1, 1):
        a.part('Roof_ribs', 'Concrete').box((.2, BD + .5, .12), loc=(s * (BW / 2 + .15), BY, WALLH - .06), bevel=0)
    a.part('Coping', 'Charred').box((BW + .52, .04, .06), loc=(0, BY + BD / 2 + .25, RZ - .1), bevel=0)
    # The earth cover on the slab and the sandbag ring round it.
    k.block(a.part('Roof_deck', 'Dirt'), (BW + .1, BD + .1, .22), loc=(0, BY, RZ + .11), chamfer=.08, taper=(.85, .85))
    path = [(-BW / 2 - .02, BY - BD / 2 + .05, RZ), (BW / 2 + .02, BY - BD / 2 + .05, RZ),
            (BW / 2 + .02, BY + BD / 2 - .05, RZ), (-BW / 2 - .02, BY + BD / 2 - .05, RZ)]
    P.sandbag_run(a, path, courses=1, bag=(.62, .36, .18), part='Sandbags', seed=131, closed=True, lean=True)
    # Sandbags laid across the middle of the cover (two courses), weeds grown on the earth.
    P.sandbag_run(a, [(-BW / 2 + .5, BY + .2, RZ + .1), (BW / 2 - .5, BY + .2, RZ + .1)], courses=2,
                  bag=(.6, .34, .17), part='Sandbags', seed=133, lean=True)
    weeds = a.part('Weeds', 'Grass')
    for j in range(9):
        weeds.tier(.15 + rng.uniform(0, .1), .16, loc=(rng.uniform(-1.2, 1.2), BY + rng.uniform(-1.4, 1.4),
                                                      RZ + .2), seg=5, droop=.2, seed=40 + j)
    # Two mushroom ventilation stacks and the periscope hood.
    for (x, y) in ((-.8, BY + .9), (.9, BY - 1.0)):
        k.lathe(a.part('Vents', 'Steel'), [(.1, 0), (.1, .45), (.24, .5), (.24, .56), (.1, .62), (0, .62)],
                loc=(x, y, RZ + .15), seg=10, worn=(2,))
    k.block(a.part('Periscope', 'Armor'), (.2, .25, .35), loc=(.2, BY - 1.5, RZ + .3), chamfer=.03)
    a.part('Glass', 'Glass').box((.14, .01, .07), loc=(.2, BY - 1.63, RZ + .4), bevel=0)
    a.part('Team_band', 'Team').box((BW + .54, .02, .14), loc=(0, BY - BD / 2 - .26, RZ - .14), bevel=0)


def _berm(a, rng):
    """The earth heaped against the front and both sides: a toe and a steeper shoulder."""
    berm = a.part('Berm', 'Dirt')
    y0, y1 = BY - BD / 2, BY + BD / 2
    k.block(berm, (BW + 1.4, .7, WALLH + .05), loc=(0, y0 - .35, (WALLH + .05) / 2), chamfer=.1, taper=(.9, .35))
    for s in (-1, 1):
        k.block(berm, (.7, BD + .2, WALLH + .05), loc=(s * (BW / 2 + .35), BY + .1, (WALLH + .05) / 2), chamfer=.1,
                taper=(.35, .95))
    toe = a.part('Berm_toe', 'Dirt')
    k.block(toe, (BW + 1.9, .35, .3), loc=(0, y0 - .8, .15), chamfer=.08, taper=(.95, .4))
    for s in (-1, 1):
        k.block(toe, (.35, BD + .6, .3), loc=(s * (BW / 2 + .8), BY - .2, .15), chamfer=.08, taper=(.4, .95))
    grass = a.part('Weeds', 'Grass')
    for j in range(10):
        s = rng.choice((-1, 1))
        grass.tier(.14 + rng.uniform(0, .1), .16, loc=(s * (BW / 2 + rng.uniform(.3, .6)), BY + rng.uniform(-1.8, 1.8),
                                                      rng.uniform(.4, .8)), seg=5, droop=.2, seed=j)
    st = a.part('Stones', 'Rock')
    for j in range(12):
        z = rng.uniform(.05, .12)
        st.box((z * 1.3, z, z * .7), loc=(rng.uniform(-2.3, 2.3), rng.uniform(-2.8, 2.8), z * .2),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)
    for i in range(8):
        K.dust(a, (rng.uniform(-2.4, 2.4), rng.uniform(-2.8, 2.8), 0), radius=1.3, k=.25)


def _entrance(a, rng):
    y1 = BY + BD / 2
    # The ramp down to the door (a sloped slab), its side walls, the concrete apron (the base) at the door.
    ramp = a.part('Ramp', 'Concrete')
    k.extrude(ramp, [(y1, 0), (y1 + 1.25, 0), (y1 + 1.25, .04), (y1, .3)], 1.3, axis='X', chamfer=.02)
    for s in (-1, 1):
        k.extrude(a.part('Ramp_walls', 'Concrete'), [(y1, 0), (y1 + 1.25, 0), (y1 + 1.25, .2), (y1, .85)], .16,
                  loc=(s * .73, 0, 0), axis='X', chamfer=.02)
    k.block(a.part('Base', 'Concrete'), (1.5, .4, .3), loc=(0, y1 + .1, .15), chamfer=.03)
    a.part('Doorway', 'Undercarriage').box((1.0, .04, .85), loc=(0, y1 + .005, .72), bevel=0)
    K.door(a, (0, y1 + .03, .3), size=(.8, .8), normal=(0, 1, 0))
    K.lamp(a, (.65, y1 + .04, 1.0), (0, 1, 0), r=.06, mat='Armor', guard=True)
    # The L-shaped sandbag blast baffle in front of the door.
    P.sandbag_run(a, [(-.9, y1 + 1.45, 0), (.9, y1 + 1.45, 0), (.9, y1 + 1.1, 0)], courses=3, bag=(.55, .32, .16),
                  part='Sandbags', seed=132, lean=True)


def _kit(a):
    K.whip_antenna(a.part('Antenna', 'Steel'), (-1.3, BY + BD / 2 + .3, 0), h=2.0, r=.022, lean=.05)
    for x in (1.25, 1.55):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (x, BY + BD / 2 + .45, 0), rot=(0, 0, .2))
    for j, (x, y) in enumerate(((-1.35, BY + BD / 2 + .65), (-1.35, BY + BD / 2 + 1.0))):
        P.ammo_box(a, (x, y, 0), size=(.5, .3, .26), rot=(0, 0, .1 * j))
    duck = a.part('Duckboards', 'Wood')
    for j in range(5):
        duck.box((.6, .12, .04), loc=(1.4, BY + BD / 2 + .85 + j * .2, .03), bevel=0)


def troop_shelter(a):
    """The troop shelter: see the module docstring."""
    rng = random.Random(3621)
    _bunker(a, rng)
    _berm(a, rng)
    _entrance(a, rng)
    _kit(a)
    k.clean(a)


BUILDERS = {
    'troop_shelter': (troop_shelter, dict(ao_distance=.6, grime_height=.5)),
}
