"""Prompt 35 wave 4 (lane C): the amphibious light vehicle rebuilt from scratch
(spec: Tools/blender/specs/amphib_light_vehicle.json).

An amphibious tracked carrier in the AAV-7A1 pattern, shortened to the def's modelSize 5.48 x 3.02 x 2.5 m (the
real AAV is longer and narrower; confidence ban_dau_doan): the boat hull with slab sides overhanging the tracks,
the long planing bow rising from the waterline with the bow plane folded on it, the headlights recessed in the
bow, six road wheels a side with the front sprocket and rear idler under the hull side, the big rear ramp with
its troop door, the water-jet ducts and their deflector doors either side of the ramp; the roof with the four
cargo hatches over the troop space, the driver's and commander's cupolas on the front left; the one-man turret on
the front right with the 25 mm cannon and the coaxial MG (as on the up-gunned AAV and the LAV-25's turret), smoke
dischargers on its cheeks.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Point_exhaust`,
`Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.1, .5
WR = .27
WHEELS = (-1.55, -.95, -.35, .25, .85, 1.45)
TOP = 1.82
NOSE, TAIL = -2.72, 2.4
HALF = 1.46
TUR = (-.55, -.95, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Boat sections: the bow rises in a long planing ramp from the waterline; slab sides over the tracks with a
    # chine, the roof edges chamfered.
    def sec(wb, zb, wc, zc, ws, zt):
        return [(0, zb), (wb, zb), (wc, zc), (ws, zc + .15), (ws, zt - .12), (ws - .1, zt), (0, zt)]
    C.section_loft(hull, [
        (NOSE, sec(.9, .78, 1.0, .82, 1.0, .9)),
        (NOSE + .25, sec(1.0, .6, 1.25, .72, 1.3, 1.2)),
        (-1.75, sec(.82, .62, HALF - .04, .72, HALF, TOP)),
        (TAIL - .1, sec(.82, .62, HALF - .04, .72, HALF, TOP)),
        (TAIL, sec(.8, .66, HALF - .06, .74, HALF - .02, TOP - .04)),
    ])
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .5, .66), (-2.0, .36), (2.2, .36), (2.3, .7)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    for s in (-1, 1):
        a.part('Skirt_edge', 'Armor').box((.04, 4.6, .08), loc=(s * (HALF - .02), -.15, .74), bevel=0)
        a.part('Team_band', 'Team').box((.012, 3.2, .1), loc=(s * (HALF + .006), .2, 1.5), bevel=0)
        K.rivet_line(a.part('Kit_steel', 'Steel'), (s * (HALF + .01), -1.6, 1.2), (s * (HALF + .01), 2.2, 1.2), (s, 0, 0),
                     pitch=.3, r=.016)
    # The bow plane folded on the bow ramp, the recessed headlights, tow eyes, the bilge pump outlets.
    bp = a.part('Bow_plane', 'Armor')
    K.plate(bp, (2.3, .7, .04), loc=(0, -2.35, 1.03), rot=(-1.0, 0, 0), chamfer=.012)
    for x in (-.8, 0, .8):
        bp.box((.05, .66, .03), loc=(x, -2.33, 1.05), rot=(-1.0, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 1.1, -2.48, 1.1), (0, -1, .3), r=.07, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .7, NOSE - .02, .84), facing=(0, -1, 0), size=.08)
        a.part('Bilge_outlets', 'Undercarriage').cyl(.05, .04, loc=(s * (HALF + .01), -1.2, 1.0), rot=(0, R90, 0),
                                                     seg=8, bevel=0)
    # The rear: the ramp with its troop door, hinges at its foot; the water-jet ducts with deflector doors.
    ramp = a.part('Ramp', 'Armor')
    K.plate(ramp, (1.7, .05, 1.0), loc=(0, TAIL + .03, 1.12))
    door = a.part('Hatches', 'Armor')
    K.plate(door, (.6, .04, .75), loc=(.35, TAIL + .07, 1.12))
    st = a.part('Kit_steel', 'Steel')
    K.handle(st, (.55, TAIL + .1, 1.1), (.55, TAIL + .1, 1.25), (0, 1, 0), h=.04, r=.012)
    for x in (-.6, .6):
        K.hinge(st, (x - .12, TAIL + .07, .65), (x + .12, TAIL + .07, .65), r=.03, knuckles=2)
    for s in (-1, 1):
        jet = a.part('Waterjets', 'Armor')
        k.extrude(jet, [(-.25, -.2), (.25, -.2), (.25, .2), (-.25, .2)], .45, loc=(s * 1.15, TAIL + .1, .95),
                  axis='Y', chamfer=.04, corner=.04)
        a.part('Waterjets_dark', 'Undercarriage').box((.36, .01, .3), loc=(s * 1.15, TAIL + .33, .95), bevel=0)
        K.plate(a.part('Jet_doors', 'Armor'), (.48, .03, .38), loc=(s * 1.15, TAIL + .36, .95))
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.15, TAIL + .03, 1.55), bevel=0)
    # The engine grilles on the front right deck, the exhaust; the four cargo hatches; the cupolas.
    K.grille(a, (-.45, -1.6, TOP + .01), .7, .6, facing=(0, 0, 1), slats=5, frame_mat='Team')
    K.grille(a, (-HALF - .01, -1.4, 1.45), .5, .3, facing=(-1, 0, 0), slats=3, frame_mat='Team')
    a.pivot('Point_exhaust', (-HALF - .05, -1.4, 1.5))
    hp = a.part('Hatches', 'Armor')
    for x in (-.45, .45):
        for y in (.35, 1.35):
            K.plate(hp, (.8, .9, .04), loc=(x, y, TOP + .01))
            K.hinge(st, (x * 2 - x * 1.0, y - .35, TOP + .04), (x * 2 - x * 1.0, y + .35, TOP + .04), r=.02,
                    knuckles=3)
    for loc in ((.75, -1.8, TOP), (.75, -1.05, TOP)):
        k.ring(a.part('Cupola', 'Armor'), [(.26, 0), (.32, 0), (.32, .12), (.27, .15)], loc=loc, seg=12, worn=(2,))
        C.hatch(a, (loc[0], loc[1], TOP + .12), r=.24)
        for i in range(3):
            u = -R90 + (i - 1) * .7
            K.periscope(a, (loc[0] + math.cos(u) * .32, loc[1] + math.sin(u) * .32, TOP + .06),
                        facing=(math.cos(u), math.sin(u), 0), size=(.09, .07, .06))
    C.jerry_rack(a, (-1.0, 1.9, TOP), count=2, axis='Y', rot=(0, 0, R90))
    C.stowage_box(a, (.5, .6, .25), (-1.0, .9, TOP), mat='Armor', latches=1)
    a.pivot('Point_fire', (0, .8, TOP + .3))


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(-2.1, .52, .25), idler=(2.05, .48, .24),
                       rollers=[], pitch=.22, hide_top=(-2.2, 2.2, .6), disc_mat='Armor', wheel_w=.18, seg=8,
                       teeth=11)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .6, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.3, -.75), (.3, -.75), (.68, -.4), (.7, .6), (.5, .78), (-.5, .78), (-.7, .6), (-.68, -.4)]
    top = [(-.22, -.55), (.22, -.55), (.55, -.3), (.56, .52), (.4, .68), (-.4, .68), (-.56, .52), (-.55, -.3)]
    C.slab_loft(body, bot, top, 0, .48)
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.12, -.15), (.1, -.16), (.13, .15), (-.1, .16)], .34, loc=(0, -.76, .26), axis='X',
              chamfer=.02, corner=.02)
    gun = a.part('Main_cannon', 'Steel', t)
    k.lathe(gun, [(.05, 0), (.05, .25), (.032, .3), (.028, 1.0), (0, 1.0)], loc=(0, -.86, .26), rot=K.FORWARD,
            seg=8, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.028, 0), (.045, .03), (.045, .16), (0, .16)],
            loc=(0, -1.84, .26), rot=K.FORWARD, seg=8, worn=(1,))
    a.pivot('Muzzle_main', (0, -2.02, .26), t)
    co = a.pivot('Coax', (.2, -.8, .28), t)
    a.part('MG_coax', 'Steel', co).cyl(.018, .35, loc=(0, -.17, 0), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_coax', (0, -.36, 0), co)
    K.periscope(a, (-.3, -.35, .48), facing=(0, -1, 0), parent=t, size=(.18, .12, .1))
    C.hatch(a, (.15, .2, .48), r=.22, parent=t)
    for s in (-1, 1):
        K.smoke_dischargers(a, .6, -.2, .3, s, count=3, parent=t)
    a.part('Team_band', 'Team', t).box((1.0, .01, .07), loc=(0, .74, .22), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.45, .5, .48), h=.2)


def amphib_light_vehicle(a, detail=False):
    """The amphibious light vehicle: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=2.6, k=.14)
    k.clean(a)


BUILDERS = {
    'amphib_light_vehicle': (amphib_light_vehicle, dict(ao_distance=.5, grime_height=.6)),
}
