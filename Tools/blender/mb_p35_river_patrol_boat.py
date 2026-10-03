"""Prompt 35 wave 4 (lane C): the river patrol boat rebuilt from scratch (spec: Tools/blender/specs/river_patrol_boat.json).

A riverine patrol boat in the PBR Mk II / SURC pattern, short and beamy to the def's modelSize 4.78 x 2.08 x 1.49 m
(confidence ban_dau_doan: no unit_refs row): the deep-V glass-fibre hull with two chines and spray strakes, the
rubbing strake round the gunwale, the flat foredeck with the bow gun tub; the open well with the centre console
wheelhouse (windscreen, side windows, a hard top with the radar dome, the whip aerials and the navigation lights),
ballistic panels along the gunwales, crew seats; two outboard motors on the transom; the 12.7 mm on its raised
pedestal in the bow tub behind a shield (the main weapon, on `Turret`), the 40 mm grenade launcher on its pintle aft
(`Mount_mg`); ammunition boxes, life ring, bollards and fenders.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`, `Point_exhaust`,
`Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
DECK = .62
BOW, STERN = -2.2, 2.05


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Sections bow to stern: keel, two chines, the gunwale (half outlines, keel -> deck centre).
    def sec(keel, c1, c2, w, top):
        return [(0, keel), (c1[0], c1[1]), (c2[0], c2[1]), (w, top - .05), (w - .02, top), (0, top)]
    C.section_loft(hull, [
        (BOW, sec(.55, (.04, .58), (.08, .66), .1, DECK + .12)),
        (BOW + .45, sec(.2, (.3, .32), (.62, .45), .78, DECK + .08)),
        (-1.0, sec(.04, (.4, .14), (.82, .3), 1.0, DECK + .04)),
        (1.0, sec(0.0, (.42, .1), (.86, .26), 1.02, DECK)),
        (STERN, sec(.02, (.42, .1), (.86, .26), 1.0, DECK)),
    ])
    # The rubbing strake round the gunwale, spray strakes along the bottom, the boot-top line.
    rs = a.part('Rubbing_strake', 'Rubber')
    k.sweep(rs, [(-.03, -.04), (.05, -.04), (.05, .04), (-.03, .04)],
            [(0, BOW - .02, DECK + .1), (.55, BOW + .4, DECK + .06), (.95, -1.0, DECK + .02), (1.0, 1.0, DECK - .02),
             (.98, STERN, DECK - .02), (-.98, STERN, DECK - .02), (-1.0, 1.0, DECK - .02), (-.95, -1.0, DECK + .02),
             (-.55, BOW + .4, DECK + .06)], closed=True)
    for s in (-1, 1):
        sp = a.part('Spray_strakes', 'Team')
        sp.limb((s * .32, -1.6, .25), (s * .5, 1.8, .16), .03, .03, bevel=0)
        a.part('Boot_top', 'Undercarriage').box((.01, 3.2, .06), loc=(s * .88, .4, .3), rot=(0, s * -.55, 0), bevel=0)
        a.part('Team_band', 'Team').box((.01, 2.6, .1), loc=(s * 1.0, .3, DECK - .15), bevel=0)
    # The deck: the foredeck plate, the well's sole, the transom with the motor well.
    dk = a.part('Deck', 'Armor')
    k.block(dk, (1.5, 1.2, .03), loc=(0, -1.4, DECK + .04), chamfer=0)
    k.block(dk, (1.8, 3.0, .03), loc=(0, .75, DECK - .2), chamfer=0)
    k.block(a.part('Transom', 'Team'), (1.9, .08, .3), loc=(0, STERN - .04, DECK - .3), chamfer=.01)
    # Ballistic panels along the gunwales, bollards, the life ring, fenders.
    bp = a.part('Ballistic_panels', 'Armor')
    for s in (-1, 1):
        for y in (-.5, .2, .9, 1.6):
            K.plate(bp, (.04, .65, .32), loc=(s * .95, y, DECK + .02))
        a.part('Kit_steel', 'Steel').cyl(.04, .12, loc=(s * .8, STERN - .15, DECK + .06), seg=8, bevel=0)
        a.part('Kit_steel', 'Steel').cyl(.04, .12, loc=(s * .45, BOW + .55, DECK + .14), seg=8, bevel=0)
        a.part('Fenders', 'Rubber').cyl(.06, .3, loc=(s * 1.06, .5, DECK - .2), seg=8, bevel=0)
    a.part('Life_ring', 'Hazard').torus(.18, .04, loc=(-.95, 1.3, DECK + .25), rot=(0, R90, 0), seg=12, ring=6)
    a.pivot('Point_fire', (0, .5, DECK + .3))


def _console(a):
    """The centre console wheelhouse with its hard top, radar dome, aerials and lights; the crew seats."""
    cab = a.part('Wheelhouse', 'Team')
    C.slab_loft(cab, [(-.55, -.25), (.55, -.25), (.55, .65), (-.55, .65)], [(-.5, -.05), (.5, -.05), (.5, .6), (-.5, .6)],
                DECK - .2, DECK + .3)
    K.windscreen(a, [(-.5, -.24, DECK + .32), (.5, -.24, DECK + .32), (.48, -.02, DECK + .62), (-.48, -.02, DECK + .62)],
                 frame_mat='Steel', wipers=2)
    gl = a.part('Windows', 'Glass')
    for s in (-1, 1):
        gl.box((.02, .5, .3), loc=(s * .52, .35, DECK + .46), bevel=0)
    fr = a.part('Hard_top_frame', 'Steel')
    for x in (-.52, .52):
        for y in (-.02, .62):
            fr.box((.04, .04, .32), loc=(x, y, DECK + .46), bevel=0)
    k.block(a.part('Hard_top', 'Armor'), (1.2, 1.0, .06), loc=(0, .3, DECK + .62), chamfer=.015)
    k.lathe(a.part('Radar_dome', 'Armor'), [(.2, 0), (.2, .05), (.16, .12), (0, .14)], loc=(0, .4, DECK + .68), seg=12)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.5, .7, DECK + .68), h=.15, lean=.1)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.5, .7, DECK + .68), h=.12, lean=.1)
    for s in (-1, 1):
        a.part('Nav_lights', 'LavaGlow' if s < 0 else 'SignalGreen').box((.05, .08, .05),
                                                                          loc=(s * .58, .1, DECK + .62), bevel=0)
    seats = a.part('Seats', 'Canvas')
    for x in (-.32, .32):
        k.block(seats, (.4, .4, .3), loc=(x, 1.0, DECK - .18), chamfer=.04)
        seats.box((.4, .08, .3), loc=(x, 1.22, DECK + .2), bevel=.02)
    C.ammo_tins(a, (0, 1.65, DECK - .17), n=3, size=(.14, .32, .2))


def _motors(a):
    for x in (-.45, .45):
        m = a.part('Outboards', 'Undercarriage')
        k.block(m, (.36, .5, .5), loc=(x, STERN + .22, DECK - .15), chamfer=.06)
        m.box((.1, .16, .5), loc=(x, STERN + .26, DECK - .37), bevel=0)
        a.part('Outboard_cowls', 'Team').box((.37, .2, .08), loc=(x, STERN + .15, DECK + .3), bevel=.02)
        a.part('Kit_steel', 'Steel').cyl(.08, .04, loc=(x, STERN + .3, .1), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Point_exhaust', (0, STERN + .3, DECK))


def _weapons(a):
    # The bow gun tub and the 12.7 mm on its raised pedestal (`Turret`, the main weapon).
    k.ring(a.part('Gun_tub', 'Armor'), [(.4, 0), (.46, 0), (.46, .35), (.4, .35)], loc=(0, -1.3, DECK + .05), seg=14)
    C.roof_gun(a, (0, -1.3, DECK + .05), pivot='Turret', post=.3, length=1.1, scale=.9)
    # The 40 mm grenade launcher on its pintle aft (`Mount_mg`).
    K.pintle_mg(a, None, (0, 1.75, DECK - .05), post=.3, length=.7, scale=1.1)


def river_patrol_boat(a, detail=False):
    """The river patrol boat: see the module docstring."""
    _hull(a)
    _console(a)
    _motors(a)
    _weapons(a)
    K.dust(a, (0, 0, .1), radius=2.5, k=.12)
    k.clean(a)


BUILDERS = {
    'river_patrol_boat': (river_patrol_boat, dict(ao_distance=.4, grime_height=.25)),
}
