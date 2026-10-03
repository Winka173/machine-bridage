"""Prompt 35 wave 3 (lane B): the gun wall segment rebuilt from scratch (spec: Tools/blender/specs/wall_gun.json).

One logic segment of the base wall (balance.json wall_gun: length 2, width 12; WallRules tiles the segments end to end,
so the box stays 12.02 x 2.16 x 2.75 m, centred on the origin, ground at z = 0, along X, the front to -Y). A
field-built Accord fighting wall: either side of the middle, HESCO MIL 1-class cells (1 m) stacked two tiers high at
the front and one tier at the back, so the back row is a fire step with duckboards behind a 2.2 m breastwork; in the
middle a 4 m timber crib firing platform (the deck at 1.28 m, where one of the base's small towers stands, as
before) with plank decking, a two-course sandbag parapet at its front, corrugated revetment sheets on its sides and a
timber ladder at the back; concertina wire on the upper tier; ammunition boxes and a water can on the platform's rear
corners; the Team band on the platform's front.

Own geometry: nothing is taken from the HESCO wall (MIL 7 single row) or the blast wall. Metres, +Z up, -Y front.
"""
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P
from mb_siege import coil

L = 12.0
B = .13               # top of the berm
T = 1.1               # one tier of cells
DECK = 1.28           # the platform's deck top (as the old segment: the tower stands at the same height)
PX = 2.05             # the platform's half width along X


def _berm(a):
    prof = [(-1.0, -.02), (1.0, -.02), (.9, .05), (.86, B), (-.86, B), (-.9, .05)]
    k.extrude(a.part('Base', 'Dirt'), prof, L, axis='X', chamfer=0)
    for x in (-5.0, -3.0, 3.0, 5.0):
        K.dust(a, (x, -1.0, .05), radius=1.3, k=.3)
        K.dust(a, (x, 1.0, .05), radius=1.1, k=.25)
    K.dust(a, (0, 1.0, .05), radius=1.6, k=.3)


def _bay(a, x0, x1, rng):
    """One side bay from x0 to x1: the front row two tiers high, the back row one tier (the fire step)."""
    cells = a.part('Walls', 'Sandbag')
    tops = a.part('Fill_top', 'Dirt')
    n = round(abs(x1 - x0))
    w = (x1 - x0) / n
    for i in range(n):
        cx = x0 + w * (i + .5)
        for y, z0, h in ((-.5, B, T), (.5, B, T), (-.5, B + T, T - .02)):
            k.block(cells, (abs(w) - .04, .97, h - .02), loc=(cx, y, z0 + h / 2), chamfer=.07)
        k.block(tops, (abs(w) - .2, .7, .08), loc=(cx + rng.uniform(-.08, .08), -.5, B + 2 * T + .02), chamfer=.03,
                taper=(.7, .7))
    mesh = a.part('Mesh', 'Steel')
    xm, lx = (x0 + x1) / 2, abs(x1 - x0) - .02
    # Horizontal wires on the front face (two tiers), the back row's face and the upper tier's back face.
    for y, zs in ((-1.005, (B + .25, B + .7, B + T - .05, B + T + .3, B + T + .75, B + 2 * T - .05)),
                  (1.005, (B + .3, B + .75, B + T - .05)), (.005, (B + T + .35, B + 2 * T - .05))):
        for z in zs:
            mesh.box((lx, .016, .016), loc=(xm, y, z), bevel=0)
    for i in range(n + 1):
        x = x0 + w * i
        x = max(min(x, L / 2 - .02), -L / 2 + .02)
        mesh.box((.022, .022, 2 * T), loc=(x, -1.005, B + T), bevel=0)
        mesh.box((.022, .022, T), loc=(x, 1.005, B + T / 2), bevel=0)
        mesh.box((.022, .022, T), loc=(x, .005, B + T * 1.5), bevel=0)
        if i < n:
            for f in (.33, .67):
                xx = x + w * f
                mesh.box((.014, .014, 2 * T - .05), loc=(xx, -1.005, B + T), bevel=0)
    # The fire step: duckboards laid on the back row's tops.
    duck = a.part('Duckboards', 'Wood')
    for i in range(int(abs(x1 - x0) / 1.3)):
        cx = min(x0, x1) + .7 + i * 1.3
        for dy in (-.25, 0, .25):
            duck.box((1.2, .2, .03), loc=(cx, .5 + dy, B + T + .03), bevel=0)
        duck.box((.06, .7, .04), loc=(cx - .5, .5, B + T + .01), bevel=0)
    wire = a.part('Razor_wire', 'Steel')
    coil(wire, min(x0, x1) + .02, max(x0, x1) - .02, -.5, B + 2 * T + .2, .19, pitch=.36, pts=6, wire=.015)


def _platform(a):
    """The timber crib firing platform in the middle: sleeper crib, plank deck, parapet, revetment sheets, ladder."""
    crib = a.part('Platform', 'LogWood')
    # Crib of sleepers laid crosswise in alternate courses (the visible outer ones), the core filled with earth.
    k.block(a.part('Platform_fill', 'Dirt'), (2 * PX - .3, 1.75, DECK - B - .1), loc=(0, 0, B + (DECK - B - .1) / 2),
            chamfer=0)
    z = B
    course = 0
    while z < DECK - .14:
        if course % 2 == 0:
            for y in (-.92, .92):
                k.block(crib, (2 * PX, .18, .16), loc=(0, y, z + .08), chamfer=0)
        else:
            for x in (-PX + .09, PX - .09, -.7, .7):
                k.block(crib, (.18, 2.0, .16), loc=(x, 0, z + .08), chamfer=0)
        z += .16
        course += 1
    deck = a.part('Deck', 'Wood')
    for i in range(9):
        y = -.92 + i * .23
        deck.box((2 * PX + .02, .21, .05), loc=(0, y, DECK - .025), bevel=0)
    for x in (-1.4, 0, 1.4):
        deck.box((.08, 2.0, .04), loc=(x, 0, DECK + .02), bevel=0)        # batten strips nailed across
    # Corrugated revetment sheets on both sides of the platform (where it meets the bays).
    sheet = a.part('Revetment', 'Corrugated')
    for s in (-1, 1):
        for i in range(5):
            y = -.8 + i * .4
            sheet.box((.02, .06, DECK - B - .1), loc=(s * (PX - .005), y - .2, B + (DECK - B) / 2), bevel=0)
            sheet.box((.012, .38, DECK - B - .12), loc=(s * (PX + .006), y, B + (DECK - B) / 2), bevel=0)
    # Sandbag parapet: two courses across the front, one turned up at each front corner.
    P.sandbag_run(a, [(-PX + .25, -.86, DECK), (PX - .25, -.86, DECK)], courses=2, bag=(.62, .34, .16),
                  part='Parapet', seed=35)
    for s in (-1, 1):
        P.sandbag_run(a, [(s * (PX - .25), -.55, DECK), (s * (PX - .25), -.1, DECK)], courses=1, bag=(.62, .34, .16),
                      part='Parapet', seed=36 + s)
    a.part('Wall_band', 'Team').box((2 * PX - .1, .02, .22), loc=(0, -1.012, DECK - .3), bevel=0)
    # The timber ladder at the back, leaning on the deck edge.
    lad = a.part('Ladder', 'Wood')
    for x in (-.28, .28):
        lad.limb((x, 1.08, .02), (x, .96, DECK + .3), .06, .05, bevel=0)
    for i in range(4):
        f = (i + .7) / 5
        lad.box((.56, .04, .04), loc=(0, 1.08 - .12 * f, .02 + (DECK + .28) * f), bevel=0)
    # Ammunition boxes and a water can on the deck's rear corners.
    for x in (-1.5, 1.35):
        P.ammo_box(a, (x, .62, DECK), size=(.5, .3, .26))
    P.ammo_box(a, (-1.5, .62, DECK + .26), size=(.5, .3, .26), rot=(0, 0, .2))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.6, .25, DECK), rot=(0, 0, 1.2))


def wall_gun(a):
    """The gun wall segment: see the module docstring."""
    rng = random.Random(3521)
    _berm(a)
    _bay(a, -L / 2, -PX, rng)
    _bay(a, PX, L / 2, rng)
    _platform(a)
    k.clean(a)


BUILDERS = {
    'wall_gun': (wall_gun, dict(ao_distance=.7, grime_height=.6, ao_strength=.8)),
}
