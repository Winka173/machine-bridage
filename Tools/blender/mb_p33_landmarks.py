"""Prompt 33 L3 (view side): the landmark models the maps' "landmarks" data names but no map prop is
(Docs/ai/LOCAL_TODO.md "landmarks the view must stand"; DECISIONS "Prompt 33 L2 view / L7").

Decoration only: Surroundings.Landmarks.cs stands each where Tools/maps/map_dressing.py found room for it (map_dressing.json
"landmarks"): no collider, no sight blocking, never in the simulation. Built to read from the widest zoom: big plain
silhouettes, one strong colour accent each, few parts (each part is one draw).

* dress_landmark_palace_dome (Capital): a domed palace, colonnade and pediment (24 x 18 m, dome to 21 m).
* dress_landmark_station_clock (Capital): a railway station hall with its clock tower (22 x 12 m, tower 21 m).
* dress_landmark_cooling_tower (Ember Ridge): a geothermal plant's cooling tower (22 m across, 30 m).
* dress_landmark_dam_wall (Hollow Dam): the dam's upstream face along local X (64 m) with its parapet at z = 0 and the
  face falling into the reservoir towards local +Z, spillway gates and intake bays.
* dress_landmark_survey_beacon (Salt Flats): a survey beacon, a braced tripod mast with a striped target (15 m).
* dress_landmark_clock_tower (Veyra Old Quarter): the old square's clock tower (6 m square, 24 m).
* dress_landmark_harbour_light (Ironport): a lighthouse on a breakwater head out at sea, for the line "the whole wall to
  the lighthouse" (c4m12.05): stood beyond the map on its SEA side.

    blender --background --python Tools/blender/build_assets.py -- dress_landmark_
"""
import math

import mb_kit27 as k

R90 = math.pi / 2


def B(x, z, y=0.0):
    """Unity-local (x across, z out to the model's back, y up) to Blender (the import turns Blender (x, y) by 180 deg)."""
    return (-x, -z, y)


def palace_dome(a):
    """A domed palace: the main block, two lower wings, a six-column portico with its pediment, the drum and a green
    copper dome with a gilded lantern."""
    wall = a.part('Walls', 'PlasterWhite')
    wall.box((14, 14, 9), loc=B(0, 0, 4.5), bevel=.1)
    for x in (-9.5, 9.5):
        wall.box((5, 12, 6.5), loc=B(x, .5, 3.25), bevel=.1)
    wall.box((14.6, 14.6, .6), loc=B(0, 0, 9.2), bevel=0)
    for i in range(6):
        wall.cyl(.45, 6.6, loc=B(-5 + i * 2, -8.6, 3.6), seg=8, bevel=0)
    wall.box((12.4, 3.0, .6), loc=B(0, -8.6, .3), bevel=0)
    wall.box((12.4, 3.0, .7), loc=B(0, -8.6, 7.25), bevel=0)
    wall.prism([(-6.3, 0), (6.3, 0), (0, 2.3)], 3.0, loc=B(0, -8.6, 7.6), axis='Y', bevel=0)
    wall.cyl(5.2, 3.2, loc=B(0, 0, 11.1), seg=16, bevel=0)
    dome = a.part('Dome', 'RoofGreen')
    k.lathe(dome, [(5.6, 12.7), (5.4, 14.2), (4.6, 16.0), (3.2, 17.6), (1.4, 18.6), (.01, 18.8)], seg=16)
    for x in (-9.5, 9.5):
        dome.box((5.4, 12.4, .5), loc=B(x, .5, 6.75), bevel=0)
    gold = a.part('Lantern', 'Gilded')
    gold.cyl(.9, 1.8, loc=B(0, 0, 19.6), seg=8, bevel=0)
    gold.cyl(.12, 2.2, loc=B(0, 0, 21.6), seg=6, bevel=0)
    a.part('Windows', 'Glass').box((14.1, 14.1, 1.3), loc=B(0, 0, 6.0), bevel=0)


def station_clock(a):
    """A railway station: the hall with its barrel roof and glazed front, a clock tower at one end with four faces."""
    brick = a.part('Brick', 'Brick')
    brick.box((16, 12, 7), loc=B(-3, 0, 3.5), bevel=.08)
    brick.box((5, 5, 17), loc=B(8.5, -2.5, 8.5), bevel=.08)
    brick.box((5.6, 5.6, .5), loc=B(8.5, -2.5, 17.2), bevel=0)
    roof = a.part('Roof', 'RoofSlate')
    arch = [(-6.2 * math.cos(t), 3.8 * math.sin(t)) for t in (i / 8 * math.pi for i in range(9))]
    roof.prism([(y, z) for y, z in arch], 16.4, loc=B(-3, 0, 7), axis='X', bevel=0)
    k.lathe(roof, [(3.6, 17.4), (.01, 21.0)], loc=B(8.5, -2.5), seg=4, rot=(0, 0, math.pi / 4))
    a.part('Glass', 'Glass').box((12, .3, 4.5), loc=B(-3, -6.05, 3.2), bevel=0)
    face = a.part('Clock', 'PlasterWhite')
    for dx, dz, rx in ((0, -2.55, R90), (0, 2.55, R90), (-2.55, 0, 0), (2.55, 0, 0)):
        rot = (R90, 0, 0) if rx else (0, R90, 0)
        face.cyl(1.5, .2, loc=B(8.5 + dx, -2.5 + dz, 14.2), rot=rot, seg=12, bevel=0)
    hands = a.part('Hands', 'EliteBlack')
    hands.box((.18, .3, 1.2), loc=B(8.5, -5.18, 14.6), bevel=0)
    hands.box((.9, .3, .18), loc=B(8.8, -5.18, 14.2), bevel=0)


def cooling_tower(a):
    """A cooling tower: the concrete hyperboloid shell (open dark top), a red warning band and a pump house."""
    shell = a.part('Shell', 'Concrete')
    k.lathe(shell, [(11, 0), (10.0, 6), (8.6, 14), (7.7, 22), (7.8, 27), (8.3, 30)], seg=20, caps=(False, False))
    k.lathe(shell, [(8.0, 30), (7.5, 29.6), (7.4, 22), (8.3, 14), (9.6, 6), (10.6, 0)], seg=20, caps=(False, False))
    a.part('Inside', 'EliteBlack').cyl(7.4, .2, loc=B(0, 0, 24), seg=16, bevel=0)
    k.lathe(a.part('Band', 'BarrelRed'), [(8.12, 27.4), (8.32, 28.9)], seg=20, caps=(False, False))
    house = a.part('House', 'Corrugated')
    house.box((8, 5, 4), loc=B(0, -14.5, 2), bevel=0)
    a.part('Pipe', 'Pipe').cyl(.7, 4.5, loc=B(0, -10.5, 1.2), rot=(R90, 0, 0), seg=8, bevel=0)


def dam_wall(a):
    """A dam's upstream face (64 m along local X): the parapet at z = 0, the concrete face falling towards local +Z into
    the reservoir, five spillway gates in their piers and two intake bays."""
    conc = a.part('Face', 'Concrete')
    conc.prism([(0, 1.3), (.9, 1.3), (6.5, -3.0), (0, -3.0)], 64, loc=B(0, 0, 0), axis='X', bevel=0)
    for i in range(6):
        x = -20 + i * 8
        conc.box((1.4, 6.5, 3.6), loc=B(x, 2.2, .3), bevel=0)
    for x in (-27, 27):
        conc.box((5, 5, 5.5), loc=B(x, 2.0, .6), bevel=0)
    steel = a.part('Gates', 'Steel')
    for i in range(5):
        steel.box((6.4, .5, 2.6), loc=B(-16 + i * 8, 3.8, -.4), rot=(-.6, 0, 0), bevel=0)
    a.part('Parapet', 'PlasterWhite').box((64, .5, .8), loc=B(0, -.25, 1.7), bevel=0)
    lamp = a.part('Lamps', 'Lamp')
    for x in (-27, 27):
        lamp.box((1.2, 1.2, .6), loc=B(x, 2.0, 3.6), bevel=0)


def survey_beacon(a):
    """A survey beacon: three braced legs to a mast head, a red and white target on it, a concrete pad and a small
    solar panel; thin, so the field shows through it."""
    steel = a.part('Mast', 'Steel')
    feet = [(2.6 * math.cos(t), 2.6 * math.sin(t)) for t in (i * math.tau / 3 + R90 for i in range(3))]
    for x, z in feet:
        steel.limb(B(x, z, 0), B(0, 0, 11.5), .18, .18, bevel=0)
    for (x0, z0), (x1, z1) in zip(feet, feet[1:] + feet[:1]):
        for h in (3.0, 7.0):
            f = 1 - h / 11.5
            steel.limb(B(x0 * f, z0 * f, h), B(x1 * f, z1 * f, h), .1, .1, bevel=0)
    steel.cyl(.12, 4, loc=B(0, 0, 13.4), seg=6, bevel=0)
    a.part('Target', 'SafetyStripe').box((2.4, .2, 2.4), loc=B(0, 0, 12.8), rot=(0, 0, .3), bevel=0)
    a.part('Top', 'BarrelRed').cyl(.6, .9, loc=B(0, 0, 15.0), seg=8, r2=.05, bevel=0)
    a.part('Pad', 'Concrete').cyl(3.4, .3, loc=B(0, 0, .15), seg=12, bevel=0)
    a.part('Panel', 'Glass').box((1.6, .1, 1.0), loc=B(1.4, -1.2, 1.4), rot=(.6, 0, 0), bevel=0)


def clock_tower(a):
    """The old square's clock tower: a plastered square shaft with cornices, four clock faces, an open belfry and a
    slate pyramid with a spire."""
    wall = a.part('Shaft', 'PlasterOchre')
    wall.box((6, 6, 17), loc=B(0, 0, 8.5), bevel=.08)
    wall.box((6.8, 6.8, .6), loc=B(0, 0, 17.2), bevel=0)
    wall.box((5.4, 5.4, 4), loc=B(0, 0, 19.5), bevel=.06)
    wall.box((6.2, 6.2, .5), loc=B(0, 0, 21.7), bevel=0)
    wall.box((7.0, 7.0, 1.2), loc=B(0, 0, .6), bevel=0)
    a.part('Belfry', 'EliteBlack').box((5.5, 5.5, 2.2), loc=B(0, 0, 19.6), bevel=0)
    face = a.part('Clock', 'PlasterWhite')
    for dx, dz in ((0, -3.05), (0, 3.05), (-3.05, 0), (3.05, 0)):
        rot = (R90, 0, 0) if dx == 0 else (0, R90, 0)
        face.cyl(1.6, .2, loc=B(dx, dz, 14.0), rot=rot, seg=12, bevel=0)
    hands = a.part('Hands', 'EliteBlack')
    hands.box((.2, .3, 1.3), loc=B(0, -3.2, 14.45), bevel=0)
    hands.box((1.0, .3, .2), loc=B(.4, -3.2, 14.0), bevel=0)
    roof = a.part('Roof', 'RoofSlate')
    k.lathe(roof, [(4.4, 21.9), (.01, 26.0)], seg=4, rot=(0, 0, math.pi / 4))
    a.part('Spire', 'Gilded').cyl(.1, 2.4, loc=B(0, 0, 27.0), seg=5, bevel=0)


def harbour_light(a):
    """A lighthouse on a breakwater head out at sea: a rock mound, the concrete head, a white tower with red bands, its
    gallery, the lantern and a red cap (18 m)."""
    a.part('Rock', 'Rock', flat=True).ico((7.5, 6.5, 2.6), loc=B(0, 0, -.6), sub=2, jitter=.25, seed=3.1)
    a.part('Head', 'Concrete').box((7, 7, 1.6), loc=B(0, 0, 1.6), bevel=.1)
    tower = a.part('Tower', 'PlasterWhite')
    k.lathe(tower, [(1.9, 2.4), (1.4, 14.5), (1.5, 14.6), (.01, 14.7)], seg=12)
    bands = a.part('Bands', 'ContainerRed')
    for y in (6.0, 10.5):
        bands.cyl(1.72 - (y - 6) * .04, 1.4, loc=B(0, 0, y), seg=12, r2=1.68 - (y - 6) * .04, bevel=0)
    k.lathe(bands, [(1.2, 16.6), (.01, 17.8)], seg=12)
    a.part('Gallery', 'Steel').cyl(2.1, .25, loc=B(0, 0, 14.8), seg=12, bevel=0)
    a.part('Lantern', 'Lamp').cyl(1.0, 1.7, loc=B(0, 0, 15.8), seg=10, bevel=0)


def _gen(fn, ao=.85, dist=1.2):
    def run(a):
        fn(a)
        k.clean(a)
    return run, dict(ao_distance=dist, grime_height=.5, ao_strength=ao)


BUILDERS = {
    'dress_landmark_palace_dome': _gen(palace_dome, .85, 2.0),
    'dress_landmark_station_clock': _gen(station_clock, .85, 2.0),
    'dress_landmark_cooling_tower': _gen(cooling_tower, .7, 3.0),
    'dress_landmark_dam_wall': _gen(dam_wall, .8, 2.0),
    'dress_landmark_survey_beacon': _gen(survey_beacon, .6, .8),
    'dress_landmark_clock_tower': _gen(clock_tower, .85, 1.5),
    'dress_landmark_harbour_light': _gen(harbour_light, .8, 1.5),
}

# The landmarks data's "model" -> the decoration model drawn for it (map_dressing.py reads this table).
MODEL_OF = {name[len('dress_landmark_'):]: name for name in BUILDERS}
