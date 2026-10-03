"""Prompt 35 wave 6 (lane B): the airborne IFV rebuilt from scratch (spec: Tools/blender/specs/airborne_vehicle.json).

A BMD-4M (the def's modelSize 5.0 x 2.5 x 2.0 m; about 0.8 x the real vehicle): the small aluminium boat hull with
its sharp double-sloped beak, the trim vane folded on the glacis, the two bow machine guns in ball mounts either
side of the driver's hatch and periscopes, the rear hatch and the two water-jet outlets; five road wheels a side,
the rear sprocket, the front idler on its arm, four return rollers and a linked track under thin fender skirts with
mud flaps; the Bakhcha-U turret: a faceted welded shell, the mantlet carrying the 100 mm 2A70 with the 30 mm
2A72 coaxial beside it and the PKT, the gunner's sight head on the right, the commander's panoramic sight on its
post on the left, three smoke dischargers a side, the rear stowage box; jerrycans, a tow cable, a canvas roll,
lamps, hooks, whips and Team bands.

Its own hull and turret (the pallet variant `airborne_vehicle_chute` keeps its old build). Runtime nodes kept:
`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Point_exhaust`, `Point_fire`; new for
the gate: `Mantlet`, `Idlers`, `Skirts`, `Sight`, `MG_bow` (the BMD's bow machine guns), `Smoke_launchers`,
`Stowage`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = .98, .4
WR = .24
WHEELS = (-1.42, -.7, .02, .74, 1.46)
NOSE, TAIL = -2.4, 2.42
DECK = 1.02
HALF = 1.05
TURRET = (0.0, .2, 1.3)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # The boat hull: a long beak (upper glacis + lower nose plate meeting in a sharp edge), straight sides, flat deck.
    prof = [(TAIL, .42), (TAIL + .03, DECK - .08), (TAIL - .1, DECK), (-.9, DECK), (NOSE + .1, .66), (NOSE, .6),
            (NOSE + .55, .3), (TAIL - .25, .3)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.04, corner=.02, taper=(1, 1))
    k.extrude(a.part('Hull_lower', 'Armor'), [(TAIL - .1, .26), (NOSE + .7, .26), (NOSE + .55, .36), (TAIL - .1, .36)],
              1.5, axis='X', chamfer=.02)
    g0, g1 = (NOSE + .1, .66), (-.9, DECK)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    nrm = (0, -math.sin(ang), math.cos(ang))

    def on_glacis(f, x, up=.0):
        y = g0[0] + (g1[0] - g0[0]) * f
        z = g0[1] + (g1[1] - g0[1]) * f
        return (x, y - math.sin(ang) * up, z + math.cos(ang) * up)
    # The folded trim vane: a ribbed plate across the glacis on two arms.
    vane = a.part('Trim_vane', 'Armor')
    k.block(vane, (1.7, .5, .05), loc=on_glacis(.32, 0, .05), rot=(ang, 0, 0), chamfer=.015)
    ribs = a.part('Vane_ribs', 'Steel')
    for x in (-.6, -.2, .2, .6):
        ribs.box((.04, .46, .05), loc=on_glacis(.32, x, .1), rot=(ang, 0, 0), bevel=0)
    for s in (-1, 1):
        ribs.limb(on_glacis(.1, s * .8, .03), on_glacis(.32, s * .8, .08), .05, .05, bevel=0)
    # The driver's hatch and periscopes on the centre line, the two bow machine guns in ball mounts.
    K.hatch_rect(a, on_glacis(.82, 0, .02), size=(.5, .45), normal=nrm)
    for dx in (-.17, 0, .17):
        K.periscope(a, on_glacis(.66, dx, .02), facing=(0, -1, 0), size=(.12, .09, .07))
    for s in (-1, 1):
        c = on_glacis(.62, s * .62, .02)
        k.lathe(a.part('Ball_mounts', 'Armor'), [(.13, 0), (.13, .03), (.09, .1), (0, .12)], loc=c, rot=(ang, 0, 0),
                seg=10)
        k.lathe(a.part('MG_bow', 'Steel'), [(.022, 0), (.022, .35), (0, .36)], loc=(c[0], c[1] - .05, c[2] + .05),
                rot=K.FORWARD, seg=6)
        K.lamp(a, (s * .85, NOSE + .5, .82), (0, -1, .15), r=.055, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .45, NOSE + .25, .42), facing=(0, -1, -.3), size=.07)
    # The engine deck grilles, the rear hatch, the water-jet outlets, tail lamps.
    K.grille(a, (.45, 1.75, DECK + .01), .7, .7, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    K.grille(a, (-.45, 1.75, DECK + .01), .7, .7, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    K.hatch_rect(a, (0, TAIL + .02, .72), size=(.7, .45), normal=(0, 1, 0))
    for s in (-1, 1):
        k.lathe(a.part('Water_jets', 'Undercarriage'), [(.16, 0), (.16, .08), (.12, .1), (0, .1)],
                loc=(s * .68, TAIL - .04, .52), rot=K.BACKWARD, seg=10)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .01, .05), loc=(s * .85, TAIL + .03, .9), bevel=0)
    a.pivot('Point_exhaust', (.8, 2.1, 1.3))
    K.grille(a, (.98, 2.0, .9), .35, .2, facing=(1, 0, 0), slats=3, frame_mat='Armor')
    K.soot(a, (1.05, 2.0, .9), radius=.5, k=.45)
    a.pivot('Point_fire', (0, 0, 1.5))
    K.tow_cable(a.part('Tow_cable', 'Steel'), [(-1.0, -1.4, .98), (-1.04, 0, .98), (-1.0, 1.3, .98)], r=.022)
    for y in (1.1, 1.4):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (-(TX + .02), y + .4, DECK + .02), rot=(0, 0, R90), scale=.85)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, 2.6, .09), loc=(s * (HALF + .006), -.1, .82), bevel=0)


def _skirts(a):
    """Thin fender skirts over the track tops, with mud flaps front and rear."""
    sk = a.part('Skirts', 'Team')
    for s in (-1, 1):
        k.block(sk, (.46, TAIL - NOSE - .45, .03), loc=(s * (TX + .04), (TAIL + NOSE) / 2 + .15, .78), chamfer=0)
        sk.box((.025, TAIL - NOSE - .6, .14), loc=(s * (TX + .26), (TAIL + NOSE) / 2 + .15, .72), bevel=0)
        for y in (NOSE + .5, TAIL - .1):
            P.mudflap(a, (s * (TX + .04), y, .62), w=.42, h=.28)


def _turret(a):
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', 'Team', t)
    rings = []
    for z, f, wf, w, r in ((-.05, -.9, .5, .95, 1.0), (.25, -.98, .55, .98, 1.05), (.42, -.7, .45, .82, .95)):
        rings.append([(-wf, f, z), (wf, f, z), (w, f + .45, z), (w, r - .12, z), (w - .12, r, z), (-w + .12, r, z),
                      (-w, r - .12, z), (-w, f + .45, z)])
    k.sharp_loft(body, rings, chamfer=.03)
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.08), .75, h=.05)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.extrude(arm, [(-.8, -.02), (.6, -.02), (.55, .22), (-.75, .22)], .05, loc=(s * .99, 0, 0), axis='X',
                  chamfer=.015)
    # The mantlet with the 100 mm low-pressure gun, the 30 mm coaxial cannon on its right, the PKT.
    k.block(a.part('Mantlet', 'Armor', t), (.7, .26, .36), loc=(.05, -1.0, .17), chamfer=.04)
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.09, 0), (.09, .2), (.075, .25), (.072, 1.62), (0, 1.62)],
            loc=(0, -1.12, .35), rot=K.FORWARD, seg=12, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.072, 0), (.088, .02), (.088, .16), (.075, .18), (0, .18)],
            loc=(0, -2.77, .35), rot=K.FORWARD, seg=12)
    a.pivot('Muzzle_main', (0, -2.95, .35), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.045, 0), (.045, .2), (.032, .25), (.028, .72), (0, .72)],
            loc=(.35, -1.15, .35), rot=K.FORWARD, seg=8, worn=(1,))
    a.part('Coax_jacket', 'Undercarriage', t).cyl(.04, .3, loc=(.35, -1.55, .35), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (.35, -1.88, .35), t)
    a.part('Coax_pkt', 'Steel', t).cyl(.018, .3, loc=(-.3, -1.25, .3), rot=K.FORWARD, seg=5, bevel=0)
    # The gunner's sight head on the right front, the commander's panoramic sight on its post at the left rear.
    gs = a.part('Sight', 'Armor', t)
    k.block(gs, (.28, .34, .22), loc=(.52, -.52, .44), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.2, .012, .1), loc=(.52, -.695, .54), bevel=0)
    gs.cyl(.06, .12, loc=(-.45, .25, .48), seg=8, bevel=0)
    k.lathe(a.part('Sight_drum', 'Armor', t), [(.15, 0), (.15, .17), (.12, .22), (0, .22)], loc=(-.45, .25, .53),
            seg=10, worn=(1,))
    a.part('Glass', 'Glass', t).box((.18, .012, .08), loc=(-.45, .1, .65), bevel=0)
    K.hatch_round(a, (.4, .3, .42), r=.24, parent=t, periscopes=1, seg=10)
    K.hatch_round(a, (-.4, -.15, .42), r=.22, parent=t, periscopes=0, seg=10)
    for s in (-1, 1):
        K.smoke_dischargers(a, .9, -.55, .3, s, count=3, parent=t)
    # The rear stowage box, whips, Team band.
    k.block(a.part('Stowage', 'Armor', t), (1.4, .32, .3), loc=(0, 1.08, .08), chamfer=.03)
    st = a.part('Stowage_bags', 'Canvas', t)
    k.block(st, (.5, .28, .18), loc=(-.4, 1.08, .4), chamfer=.05, taper=(.9, .85))
    P.canvas_roll(a, (.35, 1.1, .45), .7, r=.08)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (-.7, .8, .42), h=.36, r=.018, lean=.15)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (.7, .8, .42), h=.34, r=.018, lean=.15)
    a.part('Team_band', 'Team', t).box((1.2, .35, .012), loc=(0, -.3, .425), bevel=0)
    K.soot(a, (0, -2.75, 1.65), radius=.4, k=.35)


def airborne_vehicle(a):
    """The airborne IFV: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(2.08, .5, .22), idler=(-2.0, .44, .21),
                rollers=(-1.05, -.33, .38, 1.1), roller_z=.68, wheel_w=.14, disc_mat='Armor', wheel_seg=9)
    _skirts(a)
    _turret(a)
    k.clean(a)


BUILDERS = {
    'airborne_vehicle': (airborne_vehicle, dict(ao_distance=.5, grime_height=.55)),
}
