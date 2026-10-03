"""Prompt 35 wave 6 (lane B): the hover gunboat rebuilt from scratch (spec: Tools/blender/specs/hover_gunboat.json).

An escort air-cushion gunboat (unit_sheet: a low hovercraft hull, a black rubber skirt round the bottom, two big
pusher fans in guard rings at the stern, a small six-barrel turret forward; teardrop from above; 14.0 x 3.9 x 3.7 m;
Zubr / Tsaplya-class layout at small scale): the teardrop buoyancy hull with its sloped deck edges and bow
rubbing strake, the segmented black skirt with its fingers, the forward AK-630 on its deck mount (`Mount_mg`:
the gun house, six barrels in a casing, the muzzle), the stepped wheelhouse with its window band, roof hatch and
the lattice radar mast (`Radar`, spinning), the two ducted fans at the stern (`Propeller`, `Propeller_2`: four-blade
props on their hubs) in guard rings on pylons with the twin rudder vanes behind each, the engine air intakes, the
lift-fan grilles on the deck, railings, bollards, a life raft canister, the searchlight, beacon and Team bands.

Its own hull: nothing is taken from landing_hovercraft or another craft. Runtime nodes kept: `Mount_mg`, `Muzzle_mg`,
`Radar`, `Propeller`, `Propeller_2`, `Point_exhaust`, `Point_fire`; old part names `Hull`, `Skirt`, `Skirt_band`,
`Fan_ducts`, `Fan_blades`, `CIWS_*`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
L, HB = 13.6, 1.72             # the hull's length and half beam
DECK = 1.25


def _plan(y):
    """The teardrop's half width at y (bow -Y round, the stern straight)."""
    f = (y + L / 2) / L        # 0 bow .. 1 stern
    return HB * (math.sin(min(1.0, f / .32) * R90) ** .6) if f < .32 else HB * (1 - .06 * (f - .32))


def _hull(a):
    hull = a.part('Hull', 'Team')
    rings = []
    ys = [-L / 2 + .02, -6.2, -5.6, -4.6, -3.2, -1.0, 2.0, 4.6, L / 2 - .3]
    for y in ys:
        h = max(_plan(y), .15)
        rings.append([(-h * .92, y, .55), (h * .92, y, .55), (h, y, .85), (h * .86, y, DECK), (-h * .86, y, DECK),
                      (-h, y, .85)])
    rings.append([(p[0] * .97, L / 2, p[2]) for p in rings[-1]])
    k.sharp_loft(hull, rings, chamfer=.04)
    # The skirt: a black bag round the hull bottom with its fingers (segments), the band on top.
    sk = a.part('Skirt', 'Rubber')
    rings = []
    for y in ys + [L / 2 - .05]:
        h = max(_plan(y), .15) + .14
        rings.append([(-h * .85, y, 0.0), (h * .85, y, 0.0), (h, y, .3), (h * .95, y, .6), (-h * .95, y, .6),
                      (-h, y, .3)])
    sk.loft(rings)
    fingers = a.part('Skirt_fingers', 'Rubber')
    for y in [-5.2 + i * .7 for i in range(15)]:
        for s in (-1, 1):
            h = _plan(y) + .16
            fingers.box((.06, .5, .34), loc=(s * h, y, .2), rot=(0, s * -.25, 0), bevel=0)
    band = a.part('Skirt_band', 'Steel')
    for s in (-1, 1):
        band.tube([(s * (_plan(y) + .02), y, .62) for y in ys[1:]], .04, seg=4)
    a.part('Strake', 'Rubber').tube([(-(_plan(y) + .02), y, .85) for y in (-4.6, -5.6, -6.2)] + [(0, -L / 2 - .02, .85)] +
                                    [((_plan(y) + .02), y, .85) for y in (-6.2, -5.6, -4.6)], .06, seg=5)


def _deck(a):
    # The lift-fan grilles, deck hatches, bollards, railings, a life raft canister, Team bands.
    for x, y in ((-.8, -2.6), (.8, -2.6)):
        K.grille(a, (x, y, DECK + .01), 1.0, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.hatch_rect(a, (0, 3.3, DECK), size=(.7, .7))
    bol = a.part('Bollards', 'Steel')
    for s in (-1, 1):
        for y in (-4.4, 4.0):
            bol.cyl(.08, .22, loc=(s * 1.3, y, DECK + .1), seg=8, bevel=0)
        K.railing(a.part('Railings', 'Steel'), [(s * 1.55, -3.6, DECK), (s * 1.65, -1.0, DECK), (s * 1.65, 3.6, DECK)],
                  h=.6, post=1.3, r=.02)
        a.part('Team_band', 'Team').box((.012, 6.0, .14), loc=(s * (HB + .006), .3, .95), bevel=0)
    k.lathe(a.part('Life_rafts', 'Medical'), [(.22, -.4), (.24, -.36), (.24, .36), (.22, .4)], loc=(1.2, 2.6, DECK + .25),
            rot=K.FORWARD, seg=10)
    a.part('Kit_straps', 'Undercarriage').box((.5, .05, .5), loc=(1.2, 2.6, DECK + .25), bevel=0)


def _wheelhouse(a):
    wh = a.part('Wheelhouse', 'Team')
    rings = []
    for z, y0, y1, h in ((DECK, -1.6, 2.4, 1.25), (2.05, -1.2, 2.3, 1.15), (2.35, -.8, 2.2, 1.0)):
        rings.append([(-h, y0, z), (h, y0, z), (h, y1, z), (-h, y1, z)])
    k.sharp_loft(wh, rings, chamfer=.04)
    glass = a.part('Glass', 'Glass')
    # The window band: three raked front panes and side windows.
    for x in (-.75, 0, .75):
        c = [(x + .32, -1.36, 1.75), (x - .32, -1.36, 1.75), (x - .3, -1.02, 2.25), (x + .3, -1.02, 2.25)]
        glass.mesh([(p[0], p[1] - .01, p[2]) for p in c], [(0, 1, 2, 3)])
    for s in (-1, 1):
        for y in (-.4, .4, 1.2):
            glass.box((.012, .55, .3), loc=(s * 1.215, y, 1.9), rot=(0, s * .1, 0), bevel=0)
        a.part('Door_panels', 'Undercarriage').box((.012, .6, 1.0), loc=(s * 1.25, 1.85, 1.65), bevel=0)
    K.hatch_round(a, (.5, 1.6, 2.35), r=.25, periscopes=0, seg=10)
    # The lattice radar mast on the roof with the spinning radar (`Radar`), whips, the searchlight, beacon.
    st = a.part('Mast', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            st.tube([(sx * .25, .2 + sy * .25, 2.35), (sx * .08, .2 + sy * .08, 3.3)], .025, seg=4)
    st.tube([(-.2, .0, 2.8), (.2, .4, 2.8)], .015, seg=3)
    st.tube([(.2, .0, 2.8), (-.2, .4, 2.8)], .015, seg=3)
    r = a.pivot('Radar', (0, .2, 3.55))
    k.block(a.part('Radar_bar', 'Armor', r), (1.4, .14, .12), loc=(0, 0, -.12), chamfer=.02)
    a.part('Radar_face', 'Undercarriage', r).box((1.3, .02, .08), loc=(0, -.08, -.06), bevel=0)
    a.part('Radar_pedestal', 'Steel', r).cyl(.06, .2, loc=(0, 0, -.2), seg=8, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, 2.1, 2.35), h=1.1, r=.018, lean=.08)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.9, 2.1, 2.35), h=.9, r=.018, lean=.08)
    k.lathe(a.part('Searchlight', 'Armor'), [(.12, 0), (.14, .05), (.14, .2), (0, .2)], loc=(-.6, -.6, 2.4),
            rot=K.FORWARD, seg=10)
    a.part('Lamps', 'Lamp').cyl(.12, .01, loc=(-.6, -.81, 2.4), rot=K.FORWARD, seg=10, bevel=0)
    K.beacon(a, (.0, -.4, 2.35))
    a.pivot('Point_fire', (0, -.5, 2.6))


def _gun(a):
    """The AK-630 forward on its deck mount (`Mount_mg`): base, the gun house, six barrels in a casing, Muzzle_mg."""
    k.lathe(a.part('CIWS_base', 'Armor'), [(.6, 0), (.6, .1), (.5, .2), (0, .2)], loc=(0, -4.4, DECK), seg=14,
            worn=(1,))
    m = a.pivot('Mount_mg', (0, -4.4, 1.45))
    k.extrude(a.part('CIWS_mount', 'Team', m), [(-.5, 0), (.5, 0), (.42, .55), (.12, .7), (-.12, .7), (-.42, .55)],
              1.2, loc=(0, .1, .02), axis='Y', chamfer=.04, corner=.03)
    k.lathe(a.part('CIWS_mantle', 'Armor', m), [(.2, 0), (.2, .25), (.15, .3), (0, .3)], loc=(0, -.5, .45),
            rot=K.FORWARD, seg=10)
    bar = a.part('CIWS_barrels', 'Steel', m)
    for i in range(6):
        u = i * TAU / 6
        bar.cyl(.022, 1.15, loc=(math.cos(u) * .07, -1.3, .58 + math.sin(u) * .07), rot=K.FORWARD, seg=5, bevel=0)
    bar.cyl(.13, .08, loc=(0, -1.85, .58), rot=K.FORWARD, seg=10, bevel=0)
    bar.cyl(.13, .08, loc=(0, -1.1, .58), rot=K.FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.9, .58), m)
    K.soot(a, (0, -6.3, 2.03), radius=.5, k=.35)


def _fans(a):
    """The two ducted fans at the stern: guard rings on pylons, four-blade props (`Propeller`, `Propeller_2`), rudders."""
    for name, x in (('Propeller', .95), ('Propeller_2', -.95)):
        y, z = 5.25, 2.35
        k.ring(a.part('Fan_ducts', 'Team'), [(.86, -.3), (.93, -.3), (.95, -.1), (.95, .3), (.86, .3)],
               loc=(x, y, z), rot=(R90, 0, 0), seg=20, worn=(2,))
        guard = a.part('Fan_guards', 'Steel')
        for i in range(6):
            u = i * TAU / 6
            guard.tube([(x, y - .32, z), (x + math.cos(u) * .88, y - .32, z + math.sin(u) * .88)], .012, seg=3)
        a.part('Duct_pylons', 'Armor').limb((x, y + .1, DECK), (x, y + .1, z - .82), .2, .14, bevel=0)
        p = a.pivot(name, (x, y, z))
        hubs = a.part('Fan_hubs', 'Steel', p)
        k.lathe(hubs, [(0, -.25), (.14, -.18), (.16, 0), (.12, .2), (0, .22)], rot=(R90, 0, 0), seg=10)
        bl = a.part('Fan_blades', 'Undercarriage', p)
        for i in range(4):
            u = i * TAU / 4 + .3
            bl.box((.72, .03, .18), loc=(math.cos(u) * .47, 0, math.sin(u) * .47), rot=(.35, -u, 0), bevel=0)
        # Twin rudder vanes behind the duct.
        for dx in (-.4, .4):
            k.block(a.part('Rudders', 'Armor'), (.05, .45, 1.7), loc=(x + dx, y + .6, z - .85), chamfer=0)
    # The engine air intakes either side of the fans, the exhaust between them.
    for s in (-1, 1):
        K.intake(a.part('Intakes', 'Armor'), a.part('Intake_dark', 'Undercarriage'), (s * 1.45, 4.2, DECK + .3), .35,
                 .45, .4, facing=(0, -1, 0))
    K.exhaust(a, (0, 5.6, DECK), r=.08, length=.6, direction=(0, .3, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (0, 5.9, 2.3))
    K.soot(a, (0, 5.75, 1.85), radius=.6, k=.5)


def hover_gunboat(a):
    """The hover gunboat: see the module docstring."""
    _hull(a)
    _deck(a)
    _wheelhouse(a)
    _gun(a)
    _fans(a)
    k.clean(a)


BUILDERS = {
    'hover_gunboat': (hover_gunboat, dict(ao_distance=.7, grime_height=.5)),
}
