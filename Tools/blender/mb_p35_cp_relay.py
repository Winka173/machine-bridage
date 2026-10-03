"""Prompt 35 wave 10 (lane B): the CP relay post and its supply variant rebuilt from scratch on one compound, matching
the wave 2 salvage relay (cp_relay_b: a 4 x 4 m pad, HESCO cells, a wire fence, a Team-banded store), each from its
own spec (Tools/blender/specs/cp_relay.json, cp_relay_a.json). DECISIONS "Prompt 35 wave 10 (lane B)".

unit_refs cp_relay: a field radio relay station, a lattice mast with two dishes (trạm tiếp sóng thông tin dã chiến).
The compound (common): the cast pad with its joints, three HESCO cells across the front and two down the right, a wire
fence round the left and rear with its gate posts, the prefabricated comms shelter (roof, door, air-conditioner,
Team band, cable tray to the mast), the guyed three-legged lattice mast 7.3 m high with its climbing rungs, two
microwave dishes facing opposite ways, a sector antenna, the whip and the red obstruction beacon on top, guy wires to
ground anchors, the generator with its exhaust and fuel drums, a flag pole.

- cp_relay: ammunition and ration crates under a tarp by the shelter, a field telephone post.
- cp_relay_a (the supply relay of the old files): the crates give way to a second comms container with a big dish on
  its roof and a second whip.

No runtime node (the old files had none; the def is unarmed). Built only from frontier_kit / mb_kit27 primitives,
mb_kit35 and the wave 2 helpers (mb_p35_w2parts); no other model's builder. Metres, +Z up, -Y front, +X left. Each
under 6,000 triangles (towers seen in numbers).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
G = .1                 # pad height
MX, MY = -.95, .55     # mast foot (right rear quarter)
MH = 7.3               # mast height above the pad


def _compound(a):
    k.extrude(a.part('Base', 'Concrete'), [(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-1.1, 2.0), (-2.0, 1.1)], G, loc=(0, 0, G / 2),
              axis='Z', corner=.05, taper=(.97, .97), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for v in (-1.0, 0, 1.0):
        j.box((3.9, .03, .01), loc=(0, v, G + .003), bevel=0)
        j.box((.03, 3.9, .01), loc=(v, 0, G + .003), bevel=0)
    # HESCO across the front and down the right side; a wire fence round the left and rear with gate posts.
    for i in range(3):
        K.hesco(a, (-1.0 + i * 1.0, -1.62, G), size=(.95, .7, 1.0))
    for i in range(2):
        K.hesco(a, (-1.68, -.55 + i * .95, G), size=(.62, .9, .9))
    K.wire_fence(a, [(1.95, -1.2, G), (1.95, 1.95, G), (-.2, 1.95, G)], h=1.4, post=.8, strands=3, concertina=False)
    gp = a.part('Gate_posts', 'Steel')
    for x in (-.5, -1.4):
        gp.box((.08, .08, 1.5), loc=(x, 1.95, G + .75), bevel=0)
    a.part('Gate_chain', 'Steel').tube([(-.5, 1.95, G + 1.2), (-.95, 1.98, G + 1.05), (-1.4, 1.95, G + 1.2)], .01,
                                       seg=3, caps=False)
    _mast(a)
    _shelter(a)
    _generator(a)
    for i in range(8):
        u = i * TAU / 8
        K.dust(a, (math.cos(u) * 1.8, math.sin(u) * 1.8, G), radius=1.0, k=.28)


def _mast(a):
    """The guyed lattice mast: three tapering legs, horizontal and diagonal bracing, rungs, dishes, beacon."""
    legs = [(-.32, -.28), (.32, -.28), (0, .36)]
    ms = a.part('Mast', 'Steel')
    top_f = .45
    for dx, dy in legs:
        ms.tube([(MX + dx, MY + dy, G), (MX + dx * top_f, MY + dy * top_f, G + MH)], .035, seg=4)
        k.block(a.part('Footings', 'Concrete'), (.25, .25, .12), loc=(MX + dx, MY + dy, G + .06), chamfer=.02)
    levels = [G + .6 + i * .95 for i in range(8)]
    for zi, z in enumerate(levels):
        f = 1 - (1 - top_f) * (z - G) / MH
        pts = [(MX + dx * f, MY + dy * f, z) for dx, dy in legs]
        ms.tube(pts + pts[:1], .014, seg=3, caps=False)
        if zi + 1 < len(levels):
            z2 = levels[zi + 1]
            f2 = 1 - (1 - top_f) * (z2 - G) / MH
            for i in range(3):
                p = legs[i]
                q = legs[(i + 1) % 3]
                a.part('Mast_bracing', 'Steel').tube([(MX + p[0] * f, MY + p[1] * f, z),
                                                      (MX + q[0] * f2, MY + q[1] * f2, z2)], .01, seg=3, caps=False)
    a.part('Team_band', 'Team').box((.5, .5, .25), loc=(MX, MY + .02, G + 3.3), bevel=0)
    # The climbing rungs up the rear leg and the rest platform.
    for z in levels[:-1]:
        a.part('Ladders', 'Steel').box((.3, .03, .03), loc=(MX, MY + .38 * (1 - (1 - top_f) * (z + .45 - G) / MH)
                                                            + .04, z + .45), bevel=0)
    k.lathe(a.part('Mast_platform', 'Steel'), [(.55, -.05), (.55, .02), (0, .02)], loc=(MX, MY, G + 4.85), seg=8)
    K.railing(a.part('Railings', 'Steel'), [(MX + .5 * math.cos(u), MY + .5 * math.sin(u), G + 4.87)
                                            for u in (i * TAU / 8 for i in range(7))], h=.6, post=.5, r=.012)
    # Two microwave dishes facing opposite ways, a sector panel, the whip and the beacon on the top.
    K.dish(a.part('Dish', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (MX + .28, MY - .35, G + 5.8), r=.45,
           normal=(.35, -1, .05), seg=14)
    K.dish(a.part('Dish', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (MX - .25, MY + .3, G + 6.6), r=.36,
           normal=(-.4, 1, 0), seg=12)
    for dx, dy, nx in ((.3, .05, 1), (-.3, .05, -1)):
        k.block(a.part('Sector_panels', 'PlasterWhite'), (.06, .2, .9), loc=(MX + dx, MY + dy, G + 6.0), chamfer=.01)
    a.part('Dish_mounts', 'Steel').box((.5, .05, .05), loc=(MX, MY, G + 6.0), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (MX, MY, G + MH), h=.35, r=.02)
    a.part('Obstruction_light', 'BarrelRed').sphere(.07, loc=(MX + .1, MY, G + MH + .02), seg=8, rings=4)
    for (x, y) in ((-1.95, -1.3), (1.5, 1.9), (-1.75, 1.0)):
        a.part('Guy_wires', 'Steel').tube([(MX, MY, G + 6.2), (x, y, G + .05)], .006, seg=3)
        a.part('Guy_anchors', 'Steel').box((.12, .12, .08), loc=(x, y, G + .04), bevel=0)
    # Feeder cables down the front leg.
    a.part('Kit_cables', 'Undercarriage').tube([(MX - .1, MY - .2, G + 5.6), (MX - .22, MY - .25, G + 1.0),
                                                (MX + .2, MY - .5, G + .9)], .02, seg=3)


def _shelter(a):
    """The prefabricated comms shelter at the left rear: walls, roof, door, A/C unit, cable tray, Team band."""
    sx, sy = .95, 1.05
    W.slab(a.part('Shelter', 'Plaster'), (1.7, 1.3, 1.45), (sx, sy, G), caps=(False, False))
    k.block(a.part('Roof', 'Armor'), (1.85, 1.45, .1), loc=(sx, sy, G + 1.5), chamfer=.03, taper=(.96, .96))
    K.door(a, (sx + .3, sy - .66, G + .05), (.7, 1.2), normal=(0, -1, 0), mat='Armor')
    a.part('Team_band', 'Team').box((1.72, 1.32, .14), loc=(sx, sy, G + 1.25), bevel=0)
    k.block(a.part('Ac_unit', 'PlasterWhite'), (.15, .6, .45), loc=(sx + .93, sy, G + .8), chamfer=.015)
    K.grille(a, (sx + 1.01, sy, G + .8), .5, .35, facing=(1, 0, 0), slats=4)
    a.part('Cable_trays', 'Steel').box((1.6, .2, .05), loc=(sx - .9, sy - .25, G + 1.3), rot=(0, 0, -.2), bevel=0)
    for x in (-.6, .1):
        a.part('Cable_trays', 'Steel').box((.04, .04, 1.25), loc=(sx + x - .45, sy - .1, G + .65), bevel=0)
    k.lathe(a.part('Vents', 'Steel'), [(.08, 0), (.08, .2), (.14, .22), (0, .28)], loc=(sx - .4, sy + .3, G + 1.55),
            seg=8)
    K.whip_antenna(a.part('Antennas', 'Steel'), (sx + .7, sy + .5, G + 1.55), h=1.1, r=.02)
    K.lamp(a, (sx + .3, sy - .66, G + 1.35), facing=(0, -1, -.3), r=.06)
    K.rivet_line(a.part('Kit_rivets', 'Steel'), (sx - .82, sy - .66, G + .2), (sx - .82, sy - .66, G + 1.4),
                 (0, -1, 0), pitch=.25, r=.014)


def _generator(a):
    gx, gy = 1.35, -.65
    k.block(a.part('Generator', 'Armor'), (.65, .95, .55), loc=(gx, gy, G + .3), chamfer=.03)
    K.grille(a, (gx, gy - .485, G + .32), .5, .3, facing=(0, -1, 0), slats=4)
    K.exhaust(a, (gx - .2, gy + .3, G + .58), r=.035, length=.35)
    a.part('Generator_skid', 'Undercarriage').box((.75, 1.05, .06), loc=(gx, gy, G + .03), bevel=0)
    for i, (x, y) in enumerate(((1.65, .35), (1.3, .5))):
        K.fuel_drum(a.part('Fuel_drums', 'BarrelRed' if i else 'Armor'), a.part('Drum_bands', 'Steel'),
                    (x, y, G), r=.25, h=.8)
    a.part('Kit_cables', 'Undercarriage').tube([(gx - .3, gy + .4, G + .2), (.6, .4, G + .05), (.3, .45, G + .3)],
                                               .02, seg=3)
    a.part('Flag_pole', 'Steel').cyl(.025, 3.2, loc=(1.85, -1.85, G + 1.6), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.03, .65, .42), loc=(1.85, -1.52, G + 2.95), rot=(0, 0, .12), bevel=0)


MERGE = {n: 'Mast' for n in ('Mast_bracing', 'Gate_posts', 'Gate_chain', 'Guy_wires', 'Guy_anchors', 'Dish_mounts',
                              'Cable_trays', 'Drum_bands', 'Flag_pole', 'Mast_platform', 'Dish_post', 'Locking_bars')}
MERGE.update({n: 'Base_joints' for n in ('Generator_skid',)})
MERGE.update({n: 'Dish' for n in ('Sector_panels', 'Ac_unit', 'Dish_big')})
MERGE.update({n: 'Base' for n in ('Footings',)})


def cp_relay(a):
    """cp_relay: the compound plus crates under a tarp and a field telephone post (module docstring)."""
    _compound(a)
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    for (x, y, z, r) in ((.25, -.65, 0, .1), (.25, -.65, .36, -.12), (-.35, -.75, 0, .4)):
        K.crate(crates, straps, (.75, .5, .36), (x, y, G + z), rot=(0, 0, r), bands=1)
    k.extrude(a.part('Tarp', 'Canvas'), [(-.45, 0), (.45, 0), (.4, .3), (-.4, .3)], .7, loc=(.25, -.65, G + .72),
              axis='X', chamfer=.02)
    W.stack(a, (.45, .25, G), n=2, size=(.5, .3, .22), yaw=.3, seed=51)
    a.part('Phone_post', 'Wood').cyl(.04, 1.2, loc=(-.2, -1.15, G + .6), seg=5, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.22, .12, .2), loc=(-.2, -1.2, G + 1.0), chamfer=.01)
    P.merge_parts(a, MERGE)
    k.clean(a)


def cp_relay_a(a):
    """cp_relay_a: the compound plus a second comms container with the big dish and a second whip."""
    _compound(a)
    cx, cy = .1, -.55
    W.slab(a.part('Shelter', 'ContainerBlue'), (2.0, 1.0, 1.0), (cx, cy, G), caps=(False, True), rot=(0, 0, .05))
    for i in range(5):
        x = -.85 + i * .42
        a.part('Container_ribs', 'Undercarriage').box((.04, 1.02, .95), loc=(cx + x, cy + x * .05, G + .5),
                                                      rot=(0, 0, .05), bevel=0)
    a.part('Doors', 'ContainerBlue').box((.03, .9, .9), loc=(cx + 1.01, cy + .05, G + .5), rot=(0, 0, .05), bevel=0)
    for y in (-.2, .25):
        a.part('Locking_bars', 'Steel').cyl(.018, .9, loc=(cx + 1.04, cy + y + .05, G + .5), seg=4, bevel=0)
    a.part('Team_band', 'Team').box((2.0, .02, .14), loc=(cx, cy - .51, G + .8), rot=(0, 0, .05), bevel=0)
    a.part('Dish_post', 'Steel').cyl(.06, .45, loc=(cx - .3, cy, G + 1.22), seg=8, bevel=0)
    K.dish(a.part('Dish_big', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (cx - .3, cy, G + 1.55), r=.62,
           normal=(.2, -.8, .9), seg=16)
    K.whip_antenna(a.part('Antennas', 'Steel'), (cx + .8, cy + .3, G + 1.0), h=1.6, r=.022)
    P.merge_parts(a, MERGE)
    k.clean(a)


BUILDERS = {
    'cp_relay': (cp_relay, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
    'cp_relay_a': (cp_relay_a, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
}
