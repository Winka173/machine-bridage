"""Prompt 35 wave 3 (lane B): the bunker shelter tower rebuilt from scratch (spec:
Tools/blender/specs/bunker_shelter_tower.json).

The medium-slot troop shelter (Strings: the same shelter as the small-slot card, a wider cover; the def's modelSize
6.0 x 5.0 x 2.2 m) as a field-built Accord arch shelter of the Elephant / Nissen kind: a corrugated steel half-arch
lying front to back on sleeper sills, its ribs showing over the top, earth heaped against both flanks in two slopes,
two sandbag rows along the crest; the front end closed by a curved wall of sandbags; at the back a plank end wall with
the door and an entrance porch of sandbag walls under a corrugated sheet roof, a door lamp and an amber beacon; a
stove pipe and a ventilation cowl through the arch, a whip antenna, crates and a water drum by the porch.

Its own body: not the troop shelter's (a cast concrete box) nor the fire-control dug-out's (logs and earth).
Old part names kept: `Slab`, `Roof`, `Berm`, `Sandbags`, `Walls`, `Porch`, `Porch_roof`, `Door_lamp`, `Vents`,
`Antennas`, `Team_bands`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
R = 1.5                  # the arch's radius
SILL = .2                # the arch springs from the sills at this height
Y0, Y1 = -2.75, 1.75     # the arch's front and rear ends
SEG = 14


def _arc(r, n=SEG):
    return [(math.cos(math.pi * i / n) * r, SILL + math.sin(math.pi * i / n) * r) for i in range(n + 1)]


def _arch(a, rng):
    sill = a.part('Slab', 'LogWood')
    for s in (-1, 1):
        k.block(sill, (.24, Y1 - Y0 + .3, SILL), loc=(s * R, (Y0 + Y1) / 2, SILL / 2), chamfer=.03)
    for y in (Y0 + .2, (Y0 + Y1) / 2, Y1 - .2):
        sill.box((2 * R + .2, .2, .12), loc=(0, y, .06), bevel=0)
    # The arch: a half-cylinder shell (outer surface), its rib arcs every 0.3 m, the sheet seams.
    prof = _arc(R) + list(reversed(_arc(R - .05)))
    k.extrude(a.part('Roof', 'MetalSheet'), [(x, z) for x, z in prof], Y1 - Y0, loc=(0, (Y0 + Y1) / 2, 0), axis='Y',
              chamfer=0)
    ribs = a.part('Roof_ribs', 'Steel')
    n = int((Y1 - Y0) / .3)
    for i in range(n + 1):
        y = Y0 + .05 + i * (Y1 - Y0 - .1) / n
        ribs.tube([(x, y, z) for x, z in _arc(R + .015, 8)], .018, seg=3)
    seams = a.part('Roof_seams', 'Undercarriage')
    for j in (3, 7, 11):
        u = math.pi * j / SEG
        seams.box((.03, Y1 - Y0, .02), loc=(math.cos(u) * (R + .01), (Y0 + Y1) / 2, SILL + math.sin(u) * (R + .01)),
                  rot=(0, -(u - R90), 0), bevel=0)
    K.tone(a, 'Roof_seams', k=.8)
    # Earth heaped against both flanks: a lower toe and a steeper shoulder; two sandbag rows on the crest.
    berm = a.part('Berm', 'Dirt')
    for s in (-1, 1):
        k.block(berm, (.95, Y1 - Y0 + .2, 1.15), loc=(s * (R + .25), (Y0 + Y1) / 2, .575), chamfer=.1,
                taper=(.35, .97))
        k.block(berm, (.55, Y1 - Y0 + .5, .35), loc=(s * (R + .8), (Y0 + Y1) / 2, .175), chamfer=.06,
                taper=(.4, .97))
    top = SILL + R
    for dx in (-.33, .33):
        P.sandbag_run(a, [(dx, Y0 + .3, top - .06), (dx, Y1 - .3, top - .06)], courses=1, bag=(.6, .34, .17),
                      part='Sandbags', seed=141 + int(dx * 10), lean=True)
    st = a.part('Stones', 'Rock')
    for j in range(12):
        z = rng.uniform(.05, .12)
        st.box((z * 1.3, z, z * .7), loc=(rng.uniform(-2.3, 2.3), rng.uniform(-2.9, 2.9), z * .2),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)
    for i in range(8):
        K.dust(a, (rng.uniform(-2.3, 2.3), rng.uniform(-2.8, 2.8), 0), radius=1.3, k=.25)


def _front(a):
    """The front end closed by a curved wall of sandbags, stepped to the arch's curve."""
    for c in range(9):
        z = .02 + c * .17
        half = math.sqrt(max(.01, R * R - max(0, z + .17 - SILL) ** 2)) - .1
        if half < .3:
            break
        P.sandbag_run(a, [(-half, Y0 - .15, z), (half, Y0 - .15, z)], courses=1, bag=(.58, .34, .17),
                      part='Sandbags', seed=150 + c, lean=True)


def _rear(a):
    """The plank end wall with the door, the porch of sandbag walls under a corrugated sheet roof."""
    wall = a.part('Walls', 'Wood')
    for i in range(11):
        x = -R + .14 + i * (2 * R - .28) / 10
        h = SILL + math.sqrt(max(0, R * R - x * x)) - .05
        wall.box((.26, .06, h), loc=(x, Y1 + .02, h / 2), bevel=0)
    K.door(a, (0, Y1 + .06, .05), size=(.85, 1.6), normal=(0, 1, 0), mat='Wood')
    K.lamp(a, (.6, Y1 + .08, 1.75), (0, 1, 0), r=.06, mat='Armor', guard=True)
    a.part('Door_lamp', 'Lamp').box((.06, .02, .06), loc=(.6, Y1 + .14, 1.75), bevel=0)
    # The porch: two sandbag walls forward of the door, the sheet roof on them, the beacon on it.
    for s in (-1, 1):
        P.sandbag_run(a, [(s * .75, Y1 + .2, 0), (s * .75, Y1 + 1.1, 0)], courses=5, bag=(.5, .32, .16),
                      part='Porch', seed=160 + s, lean=True)
    pr = a.part('Porch_roof', 'Corrugated')
    k.block(pr, (1.9, 1.2, .04), loc=(0, Y1 + .7, .82), rot=(-.08, 0, 0), chamfer=0)
    for j in range(7):
        a.part('Porch_ribs', 'Steel').box((.03, 1.2, .03), loc=(-.85 + j * .283, Y1 + .7, .86), rot=(-.08, 0, 0),
                                          bevel=0)
    K.beacon(a, (-.55, Y1 + .9, .87), r=.07)
    a.part('Team_bands', 'Team').box((1.9, .02, .12), loc=(0, Y1 + 1.31, .78), bevel=0)


def _kit(a):
    k.lathe(a.part('Vents', 'Steel'), [(.07, 0), (.07, .5), (.12, .52), (.12, .58), (0, .6)],
            loc=(.6, Y1 - 1.0, SILL + R - .15), seg=8)
    K.soot(a, (.6, Y1 - 1.0, SILL + R + .45), radius=.3, k=.45)
    k.lathe(a.part('Vents', 'Steel'), [(.12, 0), (.12, .25), (.2, .3), (.05, .38), (0, .38)],
            loc=(-.55, Y0 + 1.1, SILL + R - .1), seg=8)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.0, Y1 - .3, SILL + R * .7), h=1.0, r=.02, lean=.1)
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(crates, straps, (.7, .45, .32), (1.55, Y1 + .9, 0), rot=(0, 0, .15), bands=1)
    K.crate(crates, straps, (.7, .45, .32), (1.6, Y1 + .9, .32), rot=(0, 0, .3), bands=1)
    K.fuel_drum(a.part('Drums', 'BarrelRed'), a.part('Drum_bands', 'Steel'), (-1.5, Y1 + .8, 0), r=.28, h=.85)
    u = math.radians(60)                               # a Team band painted across the arch's left flank
    a.part('Team_bands', 'Team').box((.3, 2.0, .02), loc=(math.cos(u) * (R + .02), (Y0 + Y1) / 2 - .3,
                                                          SILL + math.sin(u) * (R + .02)), rot=(0, -(u - R90), 0),
                                     bevel=0)


def bunker_shelter_tower(a):
    """The bunker shelter tower: see the module docstring."""
    rng = random.Random(3631)
    _arch(a, rng)
    _front(a)
    _rear(a)
    _kit(a)
    k.clean(a)


BUILDERS = {
    'bunker_shelter_tower': (bunker_shelter_tower, dict(ao_distance=.6, grime_height=.5)),
}
