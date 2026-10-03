"""Prompt 35 wave 6 (lane B): the next-generation tank rebuilt from scratch (spec: Tools/blender/specs/next_gen_tank.json).

A T-14 Armata (the def's modelSize 7.79 x 3.07 x 2.3 m with the gun; the hull 0.72 x the real one): the long low
hull with its flat upper glacis and the driver's capsule hatch in the middle, seven road wheels a side, the
rear sprocket and the front idler, a linked track; side skirts with reactive bricks over the front half and hinged
plates behind, the slat cage over the rear and the engine deck with its grilles; the unmanned turret set well back:
a faceted low box with a chisel front, the slim mantlet and the 125 mm gun in its thermal sleeve with the coax
beside it, the four AESA radar panels on the turret corners (Afghanit), the five-tube hard-kill launchers low on
both turret sides and the soft-kill grenade launchers on the roof, the commander's panoramic sight mast, the
gunner's sight head, the remote 12.7 mm station on a raised ring (`Mount_mg`, MODEL_STANDARD "Roof guns"), the
turret bustle box with its stowage net; tow cable, toolboxes, lamps, hooks, whips, Team bands.

Its own hull and turret: nothing is taken from another tracked model. Runtime nodes kept: `Turret`, `Main_cannon`,
`Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Mount_mg`, `Muzzle_mg`, `Point_exhaust`, `Point_fire`; new:
`Mount_APS` (the def's built-in APS), `Mantlet`, `Idlers`, `Smoke_launchers`, `Stowage`. Metres, +Z up, -Y front,
+X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = 1.2, .5
WR = .3
WHEELS = (-1.82, -1.12, -.42, .28, .98, 1.68, 2.38)
NOSE, TAIL = -2.42, 3.88
DECK = 1.2                       # the hull roof (turret ring height)
HALF = 1.32                      # the upper hull's half width
TURRET = (0.0, .9, DECK)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Side profile (y, z): the long flat upper glacis, the short lower nose plate, the stepped rear.
    prof = [(TAIL, .55), (TAIL + .02, DECK - .08), (TAIL - .1, DECK), (-.9, DECK), (NOSE + .25, .98),
            (NOSE, .86), (NOSE + .45, .42), (TAIL - .3, .42)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.05, corner=.02)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(TAIL - .1, .36), (NOSE + .6, .36), (NOSE + .45, .5), (TAIL - .1, .5)], 1.9, axis='X', chamfer=.02)
    # The engine deck behind the turret: two grille banks, the access panels, the fan cover.
    K.grille(a, (.55, 2.9, DECK + .01), .9, .7, facing=(0, 0, 1), slats=7, frame_mat='Armor')
    K.grille(a, (-.55, 2.9, DECK + .01), .9, .7, facing=(0, 0, 1), slats=7, frame_mat='Armor')
    deck = a.part('Deck_plates', 'Armor')
    for x, y, w, d in ((0, 2.15, 2.3, .55), (.75, 3.55, .8, .45), (-.75, 3.55, .8, .45)):
        deck.box((w, d, .03), loc=(x, y, DECK + .015), bevel=0)
    K.rivet_line(a.part('Kit_rivets', 'Steel'), (-1.15, 1.85, DECK + .03), (1.15, 1.85, DECK + .03), (0, 0, 1),
                 pitch=.22)
    # The driver's capsule hatch in the middle of the glacis, his three periscopes, the glacis' bolt rows.
    g0, g1 = (NOSE + .25, .98), (-.9, DECK)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])

    def on_glacis(f, x, up=.0):
        y = g0[0] + (g1[0] - g0[0]) * f
        z = g0[1] + (g1[1] - g0[1]) * f
        return (x, y - math.sin(ang) * up, z + math.cos(ang) * up)
    nrm = (0, -math.sin(ang), math.cos(ang))
    K.hatch_rect(a, on_glacis(.55, 0, .02), size=(.6, .55), normal=nrm)
    for dx in (-.24, 0, .24):
        K.periscope(a, on_glacis(.3, dx, .02), facing=(0, -1, 0), size=(.14, .1, .08))
    for s in (-1, 1):
        K.lamp(a, (s * 1.12, NOSE + .2, .95), (0, -1, .1), r=.07, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .6, NOSE + .08, .62), facing=(0, -1, 0), size=.09)
        # Front mudguards with their rubber flaps.
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .1, NOSE + .75, .98, .55, s, lip=.04)
        P.mudflap(a, (s * (TX + .02), NOSE + .12, .72), w=.5, h=.3)
    # The rear plate: exhaust louvres on the left, the tail lamps, a tow cable and the jerrycan racks.
    K.grille(a, (.7, TAIL + .03, .92), .7, .28, facing=(0, 1, 0), slats=4, frame_mat='Armor')
    a.pivot('Point_exhaust', (0.0, TAIL + .02, .9))
    K.soot(a, (.7, TAIL + .1, .92), radius=.7, k=.45)
    a.pivot('Point_fire', (0, 2.6, 1.3))
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.12, .01, .07), loc=(s * 1.1, TAIL + .03, 1.1), bevel=0)
    K.tow_cable(a.part('Tow_cable', 'Steel'), [(-1.3, -.3, 1.08), (-1.33, 1.2, 1.08), (-1.3, 2.6, 1.05)], r=.03)
    for y in (2.15, 2.45):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (-(TX + .12), y, DECK + .02), rot=(0, 0, R90))
    # Toolboxes on the rear fenders, Team bands on the hull sides.
    for s in (-1, 1):
        P.toolbox(a, (s * (TX + .1), 3.15, DECK + .14), (.4, .7, .28), mat='Armor')
        a.part('Team_band', 'Team').box((.012, 3.2, .12), loc=(s * (HALF + .006), .4, 1.07), bevel=0)
    # The slat cage over the rear plate and the engine compartment's rear corners.
    K.slat_cage(a, (-1.3, TAIL, 0), (1.3, TAIL, 0), .45, .7, (0, 1, 0), pitch=.2, standoff=.12)


def _skirts(a):
    """Skirts: reactive-brick panels over the front four wheels, hinged rubber-edged plates behind."""
    for s in (-1, 1):
        K.side_skirt(a, TX + .3, .55, TAIL - .15, 1.12, .55, s, panels=3, t=.05, mat='Team', bolts=False, hinged=False)
        sk = a.part('Skirts', 'Team')
        k.block(sk, (.06, 2.95, .6), loc=(s * (TX + .3), -.95, .83), chamfer=0)
        era = a.part('Era_bricks', 'Armor')
        for i in range(9):
            for j in range(2):
                era.box((.07, .3, .24), loc=(s * (TX + .37), -2.24 + i * .32, .72 + j * .27), bevel=0)
        a.part('Skirt_edge', 'Rubber').box((.04, 2.9, .08), loc=(s * (TX + .3), -.95, .5), bevel=0)


def _turret(a):
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', 'Team', t)
    rings = []
    # A faceted low box: chisel front (the faces meet in a blunt wedge), sloped sides, flat rear.
    for z, f, wf, w, r in ((0, -1.55, .55, 1.12, 1.45), (.38, -1.7, .62, 1.22, 1.55), (.6, -1.25, .5, 1.05, 1.45)):
        rings.append([(-wf, f, z), (wf, f, z), (w, f + .7, z), (w, r - .15, z), (w - .12, r, z), (-w + .12, r, z),
                      (-w, r - .15, z), (-w, f + .7, z)])
    k.sharp_loft(body, rings, chamfer=.04)
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), .95, h=.06)
    # Bolted cheek modules and the roof's panel seams.
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.extrude(arm, [(-1.45, .05), (-.9, .05), (-.75, .5), (-1.4, .48)], .09, loc=(s * .98, 0, 0), axis='X',
                  chamfer=.02)
    dark = a.part('Turret_dark', 'Undercarriage', t)
    for y in (-.4, .5):
        dark.box((1.9, .02, .012), loc=(0, y, .605), bevel=0)
    # The mantlet: a slim armoured box round the gun's root, its gaiter.
    k.block(a.part('Mantlet', 'Armor', t), (.46, .32, .34), loc=(0, -1.72, .14), chamfer=.04)
    k.lathe(a.part('Mantlet_gaiter', 'Rubber', t), [(.16, 0), (.19, .06), (.16, .12), (.18, .18)],
            loc=(0, -1.9, .3), rot=K.FORWARD, seg=10)
    # The 125 mm gun: the thermal sleeve with its clamps, the muzzle reference collar (no brake on the 2A82).
    k.lathe(a.part('Main_cannon', 'Armor', t), [(.1, 0), (.1, .2), (.085, .25), (.085, 2.5), (.075, 2.55),
                                               (.07, 2.6), (0, 2.6)], loc=(0, -2.05, .3), rot=K.FORWARD, seg=12,
            worn=(1, 4))
    clamps = a.part('Barrel_clamps', 'Steel', t)
    for y in (-2.55, -3.2, -3.85):
        clamps.cyl(.094, .05, loc=(0, y, .3), rot=K.FORWARD, seg=12, bevel=0)
    k.lathe(a.part('Muzzle_brake', 'Steel', t), [(.068, 0), (.08, .02), (.08, .14), (.065, .16), (0, .16)],
            loc=(0, -4.6, .3), rot=K.FORWARD, seg=12)
    a.pivot('Muzzle_main', (0, -4.79, .3), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.03, 0), (.03, .35), (0, .36)], loc=(.36, -1.42, .3), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (.36, -1.77, .3), t)
    # The four AESA radar panels on the turret's corners (the APS's eyes) and the APS pivot on the roof.
    rp = a.part('Aps_panels', 'Armor', t)
    face = a.part('Aps_faces', 'Glass', t)
    for (x, y, nx, ny) in ((.95, -1.0, .8, -.6), (-.95, -1.0, -.8, -.6), (1.0, 1.3, .8, .6), (-1.0, 1.3, -.8, .6)):
        rot = K.rot_to((nx, ny, .15))
        k.block(rp, (.36, .3, .06), loc=(x, y, .42), rot=rot, chamfer=.015)
        m = K.frame((x, y, .42), rot)
        face.box((.3, .24, .012), loc=tuple(m @ Vector((0, 0, .035))), rot=rot, bevel=0)
    a.pivot('Mount_APS', (0, .2, .66), t)
    # Afghanit hard-kill launchers: five tubes a side low on the turret flank, angled out.
    ap = a.part('Aps_cluster', 'Armor', t)
    bores = a.part('Aps_cluster_panels', 'Undercarriage', t)
    for s in (-1, 1):
        k.block(ap, (.22, 1.0, .2), loc=(s * 1.22, .05, .08), chamfer=.02)
        for i in range(5):
            y = -.36 + i * .18
            ap.cyl(.055, .3, loc=(s * 1.3, y, .16), rot=(0, s * .9, 0), seg=6, bevel=0)
            bores.cyl(.04, .02, loc=(s * 1.42, y, .24), rot=(0, s * .9, 0), seg=6, bevel=0)
    # Soft-kill grenade launchers on the roof's rear corners (the smoke role).
    for s in (-1, 1):
        K.smoke_dischargers(a, .75, 1.1, .6, s, count=3, parent=t)
    # The commander's panoramic sight on its mast, the gunner's sight head, two hatches (maintenance).
    sm = a.part('Sight_mast', 'Armor', t)
    sm.cyl(.08, .2, loc=(-.5, .55, .7), seg=10, bevel=0)
    k.lathe(a.part('Sight_drum', 'Armor', t), [(.2, 0), (.2, .24), (.16, .3), (0, .3)], loc=(-.5, .55, .78), seg=12,
            worn=(1,))
    a.part('Sight_glass', 'Glass', t).box((.24, .02, .12), loc=(-.5, .35, .9), bevel=0)
    gs = a.part('Sight', 'Armor', t)
    k.block(gs, (.36, .42, .26), loc=(.55, -.85, .6), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.28, .012, .14), loc=(.55, -1.065, .72), bevel=0)
    K.hatch_round(a, (-.1, .15, .6), r=.28, parent=t, periscopes=0, seg=10)
    # The bustle box at the rear with its stowage net and a tarp roll.
    bx = a.part('Stowage', 'Canvas', t)
    rack = a.part('Racks', 'Steel', t)
    k.block(a.part('Bustle', 'Armor', t), (1.9, .45, .42), loc=(0, 1.72, .12), chamfer=.04)
    for (x, w) in ((-.55, .6), (.2, .55), (.72, .35)):
        k.block(bx, (w, .36, .24), loc=(x, 1.72, .56), chamfer=.06, taper=(.92, .88))
    rack.tube([(-.95, 1.5, .55), (-.95, 1.95, .55), (.95, 1.95, .55), (.95, 1.5, .55)], .018, seg=4)
    P.canvas_roll(a, (0, 1.95, .72), 1.5, r=.08)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (-.9, 1.4, .6), h=.38, r=.02, lean=.15)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (.9, 1.4, .6), h=.36, r=.02, lean=.15)
    a.part('Team_band', 'Team', t).box((1.6, .5, .015), loc=(0, -.5, .605), bevel=0)
    # The remote 12.7 mm station on a raised ring (the roof-gun rule), its muzzle near the old one.
    P.raised_gun(a, (.55, .85, .6), parent=t, pivot='Mount_mg', barrel='MG', brake='MG_flash', muzzle='Muzzle_mg',
                 riser=.06, ring_r=.24, post=.12, length=.62, shield=False, ring=True, mat='Armor', tag='_rws')
    K.soot(a, (0, -4.79, 1.46), radius=.5, k=.35)


def next_gen_tank(a):
    """The next-generation tank: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(3.18, .62, .28), idler=(-2.45, .55, .27), rollers=(),
                roller_z=.86, wheel_w=.17, hide_top=(-2.3, 3.0, .75), disc_mat='Armor', wheel_seg=9)
    _skirts(a)
    _turret(a)
    k.clean(a)


BUILDERS = {
    'next_gen_tank': (next_gen_tank, dict(ao_distance=.5, grime_height=.6)),
}
