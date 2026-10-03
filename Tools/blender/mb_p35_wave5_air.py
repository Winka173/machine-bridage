"""Prompt 35 wave 5 (lane A): the wave's aircraft rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library. DECISIONS "Prompt 35 wave 5 (lane A)".

- stealth_bomber: B-2 Spirit at 0.4 x: the flying wing lofted span-wise through airfoil sections, the W saw-tooth
  trailing edge, the cockpit hump with its four panes, the dorsal intakes and the exhaust troughs, the split drag
  rudders at the tips, two bomb bays open on the rotary launcher with JDAMs, the JASSMs (Muzzle_rocket).
- wingman_drone: XQ-58 Valkyrie at 0.4 x: the chined trapezoid fuselage, the dorsal S-duct intake, the swept wing,
  the V-tail, the recovery parachute bay, two AIM-9s under the wings.
- recon_jet: SR-71 Blackbird at 0.4 x: the long chined fuselage, the two nacelles at mid-wing with their spike
  inlets and canted fins, the delta wing, the tandem cockpit.
- sky_gunship (AC-130U) and sky_fortress (the AC-130J-type boss), morrigan (the Su-57-type boss) and
  elite_attack_helicopter (AH-64E): see their sections. The two gunships share no fuselage: each lofts its own,
  with its own propellers (four blades on the U, six on the J), gun deck and fittings.

Runtime nodes are the old models' (wrappers still add Part_wing, Mount_Flare_* and per-barrel muzzles).
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau
ACROSS = (0, R90, 0)


def span_loft(part, stations, foil=None):
    """A wing or flying-wing body lofted across the span: stations [(x, lead_y, trail_y, z, t)] from one tip to the
    other, each an airfoil section from its leading edge (lead_y, front is -Y) to its trailing edge, t thickness
    over chord."""
    foil = foil or K.FOIL
    rings = []
    for x, lead, trail, z, t in stations:
        chord = trail - lead
        rings.append([(x, lead + chord * (1 - u) / 2, z + v * t * chord * .5) for u, v in foil])
    part.loft(rings, bevel=0)


def body_loft(part, stations, smooth=0):
    """A fuselage through stations [(y, half_width, z_bottom, z_top, chine)] front to back: an eight-point section
    with chines at `chine` (0..1 up the side) - the flat-sided, sharp-edged stealth and Blackbird bodies.
    `smooth` > 0 inserts a mid point on every facet pushed out by that share of the local radius (a rounder body,
    the chine points stay sharp)."""
    rings = []
    for y, w, zb, zt, c in stations:
        zc = zb + (zt - zb) * c
        pts = [(0, zb), (w * .55, zb + (zc - zb) * .25), (w, zc), (w * .55, zt - (zt - zc) * .3), (0, zt),
               (-w * .55, zt - (zt - zc) * .3), (-w, zc), (-w * .55, zb + (zc - zb) * .25)]
        if smooth:
            cz = (zb + zt) / 2
            out = []
            for i, (x0, z0) in enumerate(pts):
                x1, z1 = pts[(i + 1) % len(pts)]
                mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
                dx, dz = mx, mz - cz
                n = math.hypot(dx, dz) or 1.0
                r = max(w, (zt - zb) / 2)
                out += [(x0, z0), (mx + dx / n * r * smooth, mz + dz / n * r * smooth)]
            pts = out
        rings.append([(x, y, z) for x, z in pts])
    part.loft(rings, bevel=0)


FOIL14 = [(1.0, 0.0), (.8, .35), (.55, .62), (.3, .85), (.05, 1.0), (-.3, .9), (-.65, .55), (-1.0, 0.0),
          (-.65, -.4), (-.3, -.6), (.05, -.7), (.3, -.6), (.55, -.45), (.8, -.25)]


# ============================================================================= stealth_bomber
def stealth_bomber(a):
    """B-2 Spirit: see the module docstring. Runtime: Muzzle_missile (the bay, the main payload), Muzzle_rocket /
    .001 (JASSM), Bombs (the payload), Point_fire, Point_exhaust; mb_p34_parts cuts Part_wing out of the left
    wing."""
    K.suffixed(a)
    body = a.part('Fuselage', 'Team')
    # Plan form (x >= 0): leading edge from the nose at y -4.2 to the tip at (10.5, 2.75); the saw-tooth trailing
    # edge (10.5, 3.25) -> (6.6, 1.0) -> (4.3, 3.4) -> (2.2, 2.0) -> (0, 4.2).
    te = [(0.0, 4.2), (2.2, 2.0), (4.3, 3.4), (6.6, 1.0), (10.5, 3.25)]

    def trail(x):
        for (x0, y0), (x1, y1) in zip(te, te[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return te[-1][1]
    xs = [0.0, .35, .7, 1.05, 1.4, 1.8, 2.2, 2.7, 3.2, 3.75, 4.3, 4.85, 5.4, 6.0, 6.6, 7.3, 8.0, 8.7, 9.4, 10.0, 10.5]
    st = []
    for x in [-v for v in reversed(xs[1:])] + xs:
        ax = abs(x)
        lead = -4.2 + ax * .66
        tr = trail(ax)
        t = .19 if ax < 1.0 else .15 if ax < 2.4 else .1 if ax < 5 else .075
        z = .05 + (.0 if ax < 6 else (ax - 6) * .015)
        st.append((x, lead, max(tr, lead + .35), z, t))
    span_loft(body, st, foil=FOIL14)
    # Trailing-edge strips along the saw-teeth (the darker edge treatment) and the darker panels over the bays.
    tes = a.part('Trailing_edges', 'Armor')
    for s in (-1, 1):
        for (x0, y0), (x1, y1) in zip(te, te[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            tes.box((L * .96, .3, .03), loc=(s * (x0 + x1) / 2, (y0 + y1) / 2 - .15, .1 - max(x0, x1) * .006),
                    rot=(0, 0, s * math.atan2(y1 - y0, x1 - x0)), bevel=0)
    for (x, y, w, l) in ((0, -.2, 1.4, 2.2), (2.6, 1.3, 1.0, 1.0), (-2.6, 1.3, 1.0, 1.0)):
        a.part('Access_panels', 'Armor').box((w, l, .02), loc=(x, y, .3 - abs(x) * .03), bevel=0)
    # Leading-edge strips (the darker edge material), saw-tooth outlines round the doors and panels.
    le = a.part('Leading_edges', 'Armor')
    for s in (-1, 1):
        for j in range(5):
            x0, x1 = 1.0 + j * 1.9, 2.9 + j * 1.9
            y0, y1 = -4.2 + x0 * .66, -4.2 + x1 * .66
            le.box((math.hypot(x1 - x0, y1 - y0), .18, .03), loc=(s * (x0 + x1) / 2, (y0 + y1) / 2 + .08, .07),
                   rot=(0, 0, s * math.atan2(y1 - y0, x1 - x0)), bevel=0)
        for (x, y, w, l) in ((1.2, -1.8, .5, .7), (2.6, -.6, .7, .5), (3.6, .6, .5, .9), (5.2, .2, .8, .6)):
            pp = a.part('Access_panels', 'Armor')
            pp.box((w, l, .02), loc=(s * x, y, .2 - x * .02), rot=(0, 0, s * .785), bevel=0)
    # The cockpit hump with its four panes, the dorsal intakes (saw-tooth lips, splitter plates), exhaust troughs.
    hump = a.part('Fuselage_hump', 'Team')
    k.sharp_loft(hump, [[(-.75, -3.2, .25), (.75, -3.2, .25), (.95, -1.6, .25), (-.95, -1.6, .25)],
                        [(-.4, -2.9, .78), (.4, -2.9, .78), (.55, -1.8, .72), (-.55, -1.8, .72)]], chamfer=.03)
    gl = a.part('Canopy', 'Glass')
    for s in (-1, 1):
        gl.mesh([(s * .1, -3.08, .66), (s * .62, -3.0, .5), (s * .72, -2.55, .62), (s * .14, -2.75, .82)],
                [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        gl.mesh([(s * .72, -2.5, .62), (s * .82, -1.95, .55), (s * .58, -1.85, .72), (s * .5, -2.4, .76)],
                [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
    intk = a.part('Intakes', 'Team')
    dark = a.part('Intake_ducts', 'Undercarriage')
    for s in (-1, 1):
        x = s * 1.6
        k.sharp_loft(intk, [[(x - .55, -1.2, .14), (x + .55, -1.2, .14), (x + .55, .6, .14), (x - .55, .6, .14)],
                            [(x - .45, -.95, .42), (x + .45, -.95, .42), (x + .4, .4, .3), (x - .4, .4, .3)]],
                     chamfer=.02)
        dark.box((.82, .02, .18), loc=(x, -.97, .3), rot=(-.6, 0, 0), bevel=0)
        a.part('Intake_splitters', 'Armor').box((1.0, .5, .02), loc=(x, -1.3, .2), rot=(.2, 0, 0), bevel=0)
        # The exhaust troughs over the trailing edge between the saw-teeth, the nozzles' glow inside.
        tr_ = a.part('Exhausts', 'Armor')
        tr_.box((.9, 1.6, .06), loc=(s * 1.9, 2.0, .2), rot=(-.08, 0, 0), bevel=0)
        a.part('Exhaust_glow', 'LavaGlow').box((.7, .03, .12), loc=(s * 1.9, 1.15, .24), bevel=0)
        # Split drag rudders at the tips (the B-2's yaw control) and the elevons along the trailing edge.
        a.part('Rudders', 'Armor').box((1.8, .5, .03), loc=(s * 9.4, 2.85, .2), rot=(-.25, 0, s * .52), bevel=0)
        a.part('Rudders', 'Armor').box((1.8, .5, .03), loc=(s * 9.4, 2.85, .05), rot=(.25, 0, s * .52), bevel=0)
        ev = a.part('Elevons', 'Armor')
        for (x0, y0), (x1, y1) in ((te[1], te[2]), (te[3], te[4])):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ev.box((math.hypot(x1 - x0, y1 - y0) * .8, .4, .03), loc=(s * mx, my - .2, .07),
                   rot=(0, 0, s * math.atan2(y1 - y0, x1 - x0)), bevel=0)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.15, .3, .05), loc=(s * 10.3, 2.75, .1),
                                                                          bevel=0)
    # Underside: two bomb bays open, their doors hanging, the rotary launcher with four JDAMs each, the gear doors.
    bd = a.part('Bay_doors', 'Armor')
    for s in (-1, 1):
        x = s * .9
        a.part('Bay_liners', 'Undercarriage').box((1.1, 2.6, .02), loc=(x, -.6, -.08), bevel=0)
        for d in (-1, 1):
            bd.box((.03, 2.5, .5), loc=(x + d * .56, -.6, -.32), bevel=0)
        a.part('Rack_launcher', 'Steel').cyl(.12, 2.4, loc=(x, -.6, -.3), rot=K.FORWARD, seg=8, bevel=0)
        for j in range(4):
            u = j * R90 + TAU / 8
            K.store(a, (x + math.cos(u) * .22, .5, -.3 + math.sin(u) * .22), .1, 2.0, body='Bombs', body_mat='Armor',
                    fins='Bomb_fins', kind='bomb')
        K.store(a, (s * 3.0, 2.6, -.32), .1, 2.4, body='Standoff_missile', body_mat='Armor', fins='Missile_fins')
        a.part('Pylons', 'Armor').box((.08, 1.3, .12), loc=(s * 3.0, 1.4, -.2), bevel=0)
        for y in (-2.6, .9):
            a.part('Gear_doors', 'Undercarriage').box((.6, 1.2, .015), loc=(s * 2.1, y, -.06), bevel=0)
    a.part('Team_accents', 'Team').box((3.0, .5, .01), loc=(0, -.4, .3), bevel=0)
    a.pivot('Muzzle_missile', (0, 0, -.5))
    a.pivot('Muzzle_rocket', (-3.0, 1.28, -.32))
    a.pivot(K.name('Muzzle_rocket', 1), (3.0, 1.28, -.32))
    a.pivot('Point_fire', (0, .5, .7))
    a.pivot('Point_exhaust', (2.0, 2.2, .2))
    k.clean(a)


# ============================================================================= wingman_drone
def wingman_drone(a):
    """XQ-58 Valkyrie: see the module docstring. Runtime: Muzzle_missile / .001 (the AIM-9s), Point_fire,
    Point_exhaust."""
    K.suffixed(a)
    fus = a.part('Fuselage', 'Team')
    body_loft(fus, [(-1.75, .02, .02, .06, .5), (-1.72, .05, 0, .08, .48), (-1.68, .08, -.03, .1, .47),
                    (-1.62, .11, -.06, .115, .46), (-1.55, .14, -.08, .13, .45), (-1.45, .17, -.1, .15, .44),
                    (-1.35, .2, -.12, .17, .43), (-1.1, .26, -.15, .2, .42), (-.75, .31, -.16, .22, .41),
                    (-.4, .34, -.17, .23, .4), (0.0, .35, -.17, .23, .4), (.4, .34, -.16, .23, .4),
                    (.8, .31, -.14, .22, .41), (1.2, .28, -.12, .2, .42), (1.45, .23, -.1, .17, .44),
                    (1.65, .18, -.08, .14, .45), (1.76, .12, -.05, .1, .5)], smooth=.05)
    # The dorsal S-duct intake behind the nose, its lip, the dark mouth; the nozzle at the tail.
    k.sharp_loft(a.part('Intake', 'Team'), [[(-.18, -.75, .2), (.18, -.75, .2), (.2, .2, .22), (-.2, .2, .22)],
                                           [(-.14, -.6, .34), (.14, -.6, .34), (.12, .2, .3), (-.12, .2, .3)]],
                 chamfer=.01)
    a.part('Intake_dark', 'Undercarriage').box((.26, .02, .1), loc=(0, -.61, .28), rot=(-.5, 0, 0), bevel=0)
    k.lathe(a.part('Exhaust', 'Steel'), [(.1, 1.55), (.11, 1.72), (.09, 1.78), (.07, 1.78)], rot=(-R90, 0, 0), seg=10)
    a.part('Exhaust_glow', 'LavaGlow').cyl(.07, .02, loc=(0, 1.77, .02), rot=K.FORWARD, seg=10, bevel=0)
    # Swept wing, the V-tail, the panel lines, the recovery parachute bay and the skids.
    wg = a.part('Wings', 'Team')
    for s in (-1, 1):
        span_loft(wg, [(s * (.32 + 1.32 * f), -.25 + .8 * f, -.25 + .8 * f + 1.0 - .62 * f, .02 - .04 * f, .07)
                       for f in ((0, .12, .25, .37, .5, .62, .75, .87, 1.0) if s > 0 else
                                 (1.0, .87, .75, .62, .5, .37, .25, .12, 0))], foil=FOIL14)
    for sx in (-1, 1):
        rings = []
        for f in (0, .25, .5, .75, 1.0):
            lead, chord = .95 + .4 * f, .7 - .38 * f
            zz, xx = .18 + .4 * f * math.cos(.65), sx * (.16 + .4 * f * math.sin(.65))
            rings.append([(xx + v * .07 * chord * .5 * math.cos(.65), lead + chord * (1 - u) / 2,
                           zz - sx * v * .07 * chord * .5 * math.sin(.65) * 0) for u, v in FOIL14])
        a.part('Fins', 'Team').loft(rings, bevel=0)
    pl = a.part('Panel_lines', 'Armor')
    for y in (-1.2, -.6, .05, .7, 1.3):
        pl.box((.5, .02, .01), loc=(0, y, .245), bevel=0)
    pl.box((.32, .5, .01), loc=(0, .8, .235), bevel=0)
    for s in (-1, 1):
        pl.box((.6, .25, .01), loc=(s * .9, .2, .07), rot=(0, 0, s * .35), bevel=0)
        a.part('Ailerons', 'Armor').box((.5, .12, .02), loc=(s * 1.2, .5, .03), rot=(0, 0, s * .1), bevel=0)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .1, .03), loc=(s * 1.64, .45, .02),
                                                                          bevel=0)
    a.part('Chute_bay', 'Hazard').box((.2, .3, .01), loc=(0, .3, .24), bevel=0)
    sk = a.part('Skids', 'Steel')
    for s in (-1, 1):
        sk.box((.04, .6, .05), loc=(s * .18, .1, -.19), bevel=0)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -.25, .24), h=.1, chord=.12)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .2, -.16), h=.08, chord=.1, normal=(0, 0, -1))
    a.part('Sensor_window', 'Glass').box((.16, .2, .01), loc=(0, -1.2, -.12), bevel=0)
    # The EO / IR sensor ball under the nose (the ISR fit) on its fairing.
    k.lathe(a.part('Sensor', 'Armor'), [(.0, -.02), (.09, -.01), (.11, .04), (.1, .1), (.06, .13)],
            loc=(0, -1.0, -.14), rot=(math.pi, 0, 0), seg=16)
    a.part('Sensor_glass', 'Glass').sphere(.045, loc=(0, -1.02, -.17), seg=12, rings=8)
    for yy in (1.6, 1.68):
        a.part('Exhaust_rings', 'Armor').cyl(.115, .02, loc=(0, yy, .02), rot=K.FORWARD, seg=16, bevel=0)
    # The two AIM-9s on pylons under the wings.
    for i, s in enumerate((-1, 1)):
        x = s * .75
        a.part('Pylons', 'Armor').box((.05, .45, .1), loc=(x, -.05, -.04), bevel=0)
        a.part('Missile_rails', 'Steel').box((.04, .7, .03), loc=(x, -.05, -.1), bevel=0)
        K.store(a, (x, .38, -.14), .032, .65, body='Missiles', body_mat='Fuel', fins='Missile_fins', seg=24)
        for dy in (-.15, .2):
            a.part('Rail_shoes', 'Steel').box((.03, .05, .03), loc=(x, dy, -.12), bevel=0)
        a.part('Missile_seekers', 'Glass').cyl(.02, .02, loc=(x, -.27, -.14), rot=K.FORWARD, seg=6, bevel=0)
        a.pivot(K.name('Muzzle_missile', i), (x, -.27, -.14))
    a.pivot('Point_fire', (0, .2, .15))
    a.pivot('Point_exhaust', (0, 1.75, 0))
    k.clean(a)


# ============================================================================= recon_jet
def recon_jet(a):
    """SR-71 Blackbird: see the module docstring. Runtime: Muzzle_main (the nose; the def is unarmed), Point_fire,
    Point_exhaust (added); mb_p34_parts cuts Part_wing out of the left wing."""
    fus = a.part('Fuselage', 'Team')
    body_loft(fus, [(-7.2, .02, .3, .32, .5), (-6.9, .1, .22, .4, .48), (-6.5, .2, .12, .5, .45),
                    (-5.9, .35, .03, .63, .41), (-5.2, .48, -.03, .74, .38), (-4.4, .62, -.08, .8, .36),
                    (-3.4, .76, -.11, .84, .34), (-2.2, .86, -.13, .86, .32), (-.8, .9, -.15, .86, .3),
                    (.8, .9, -.15, .85, .3), (2.2, .82, -.13, .8, .3), (3.4, .7, -.11, .72, .31),
                    (4.5, .55, -.08, .62, .32), (5.3, .38, -.04, .52, .36), (5.9, .2, .02, .42, .4)], smooth=.05)
    # The chines from the nose out to the wing, the tandem cockpit, the sensor bays in the chines.
    ch = a.part('Chines', 'Team')
    for s in (-1, 1):
        ch.mesh([(s * .2, -6.0, .3), (s * 1.0, -2.6, .3), (s * 1.4, -.4, .26), (s * .85, -.4, .3), (s * .5, -2.6, .34)],
                [(0, 1, 2, 3, 4) if s > 0 else (4, 3, 2, 1, 0)])
        ch.mesh([(s * .2, -6.0, .28), (s * .5, -2.6, .24), (s * .85, -.4, .24), (s * 1.4, -.4, .24), (s * 1.0, -2.6, .26)],
                [(0, 1, 2, 3, 4) if s > 0 else (4, 3, 2, 1, 0)])
        a.part('Sensor_bays', 'Armor').box((.25, 1.6, .03), loc=(s * .75, -3.0, .33), rot=(0, 0, s * .2), bevel=0)
    k.sharp_loft(a.part('Canopy', 'Glass'), [[(-.32, -4.9, .7), (.32, -4.9, .7), (.36, -3.0, .82), (-.36, -3.0, .82)],
                                             [(-.16, -4.6, .98), (.16, -4.6, .98), (.2, -3.3, 1.02),
                                              (-.2, -3.3, 1.02)]], chamfer=.01)
    a.part('Canopy_frames', 'Team').box((.5, .05, .25), loc=(0, -3.95, .95), bevel=0)
    # The delta wing, the nacelles with their spike inlets and canted fins, the exhaust nozzles.
    wg = a.part('Wings', 'Team')
    K.wing(wg, (-2.8, 6.8), (2.8, 1.4), 2.55, x0=.85, z=.3, t=.035)
    for s in (-1, 1):
        x = s * 2.0
        k.lathe(a.part('Nacelles', 'Team'), [(.35, -3.0), (.45, -2.7), (.52, -2.4), (.56, -1.8), (.58, -1.0),
                                             (.58, 1.0), (.58, 3.0), (.54, 3.8), (.5, 4.5), (.45, 4.9)],
                loc=(x, 0, .3), rot=(-R90, 0, 0), seg=20)
        k.lathe(a.part('Spikes', 'Armor'), [(0, -4.1), (.06, -3.9), (.12, -3.6), (.2, -3.3), (.28, -3.0),
                                           (.32, -2.7)], loc=(x, 0, .3), rot=(-R90, 0, 0), seg=16)
        for yy in (-.5, 1.6, 3.4):
            a.part('Nacelle_rings', 'Armor').cyl(.6, .06, loc=(x, yy, .3), rot=K.FORWARD, seg=20, bevel=0)
        cor = a.part('Wing_corrugations', 'Armor')
        for j in range(7):
            yy = -.6 + j * .62
            x0 = s * 1.0
            cor.box((.75, .04, .02), loc=(s * 1.45, yy, .34), bevel=0)
        a.part('Intakes', 'Undercarriage').cyl(.36, .02, loc=(x, -2.95, .3), rot=K.FORWARD, seg=14, bevel=0)
        k.lathe(a.part('Nozzles', 'Steel'), [(.45, 4.85), (.48, 5.3), (.46, 5.75), (.42, 5.85)], loc=(x, 0, .3),
                rot=(-R90, 0, 0), seg=20)
        a.part('Exhaust_glow', 'LavaGlow').cyl(.38, .02, loc=(x, 5.8, .3), rot=K.FORWARD, seg=16, bevel=0)
        K.fin(a.part('Fins', 'Team'), (2.6, 2.2), (3.9, 1.0), 1.15, x=x, z0=.78, t=.05, cant=-s * .26)
        # Outer wing panels beyond the nacelles, a nav light at each tip, bypass doors on the nacelles.
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.12, .2, .05), loc=(s * 3.38, 1.6, .3),
                                                                          bevel=0)
        for y in (-1.6, -1.1):
            a.part('Bypass_doors', 'Armor').box((.02, .3, .2), loc=(x + s * .58, y, .3), bevel=0)
    a.part('Team_band', 'Team').box((.6, 2.0, .01), loc=(0, 1.0, .86), bevel=0)
    a.part('Refuel_door', 'Armor').box((.25, .4, .01), loc=(0, -1.6, .87), bevel=0)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, 1.5, -.15), h=.2, chord=.3, normal=(0, 0, -1))
    a.part('Sensor_bays', 'Armor').box((.5, 1.2, .02), loc=(0, -.2, -.16), bevel=0)
    a.pivot('Muzzle_main', (0, -7.2, .3))
    a.pivot('Point_fire', (0, .5, .7))
    a.pivot('Point_exhaust', (2.0, 5.3, .3))
    k.clean(a)


# ============================================================================= sky_gunship
def _c130_wing(a, part, span, root, tip, z, t=.13):
    """A C-130-type straight tapered high wing across the span (both halves in one loft), its dihedral slight."""
    st = []
    for f in (-1.0, -.75, -.5, -.3, -.12, 0.0, .12, .3, .5, .75, 1.0):
        x = f * span / 2
        lead_r, chord_r = root
        lead_t, chord_t = tip
        g = abs(f)
        lead, chord = lead_r + (lead_t - lead_r) * g, chord_r + (chord_t - chord_r) * g
        st.append((x, lead, lead + chord, z + g * span * .5 * .03, t))
    span_loft(part, st, foil=FOIL14)


def _gunship_prop(a, name, loc, R, blades, phase=0.0):
    """A turboprop's propeller on its spinning pivot (Propeller / Propeller_2 ..): the spinner and the blades."""
    p = a.pivot(name, loc)
    bl = a.part('Prop_blades', 'Undercarriage', p)
    for j in range(blades):
        u = j * TAU / blades + phase
        bl.box((R * .16, .05, R * .9), loc=(math.cos(u) * R * .5, 0, math.sin(u) * R * .5), rot=(.3, -u + R90, 0),
               bevel=0, taper=(.55, 1))
    k.lathe(a.part('Spinners', 'Steel', p), [(0, -.3), (.08, -.25), (.14, -.1), (.15, .05)], rot=K.FORWARD, seg=10)


def sky_gunship(a, detail=False):
    """AC-130U Spooky at 0.4 x: the C-130 fuselage (lofted round section, upswept tail with the ramp), the high wing
    with four turboprop nacelles and four-blade propellers (Propeller .. Propeller_4), the tall fin and tailplane,
    the left-side gun deck (M102 105 mm aft, Bofors 40 mm, GAU-12 25 mm forward, their ports), the sensor turrets
    (nose radar blister, IR / TV balls), landing-gear sponsons, flare dispensers, the cockpit glazing. `detail` is
    the PC High twin's flag (the same model). Runtime: Muzzle_main, Muzzle_gun, Muzzle_mg (the left side),
    Propeller .. Propeller_4, Point_fire, Point_exhaust; mb_flare_mounts adds Mount_Flare_*, mb_p34_parts
    Part_wing."""
    fus = a.part('Fuselage', 'Team')
    rings = []
    for y, r, zc, zsq in ((-5.95, .1, .1, 1.0), (-5.7, .45, .05, 1.0), (-5.2, .72, .1, 1.0), (-4.4, .86, .25, 1.0),
                          (-3.0, .88, .35, 1.0), (1.5, .88, .35, 1.0), (2.6, .82, .5, .95), (3.8, .62, .78, .85),
                          (4.9, .38, 1.1, .8), (5.8, .14, 1.4, .8)):
        rings.append([(math.cos(u) * r, y, zc + math.sin(u) * r * zsq) for u in (i * TAU / 16 for i in range(16))])
    fus.loft(rings, bevel=0)
    # Cockpit glazing, the nose radome line, the side door, the ramp lines, the gear sponsons.
    gl = a.part('Canopy', 'Glass')
    for s in (-1, 1):
        gl.mesh([(s * .2, -5.32, .62), (s * .62, -5.0, .6), (s * .64, -4.78, .78), (s * .22, -5.05, .86)],
                [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        gl.mesh([(s * .68, -4.75, .52), (s * .8, -4.3, .52), (s * .8, -4.3, .72), (s * .68, -4.75, .72)],
                [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
    sp = a.part('Undercarriage', 'Armor')
    for s in (-1, 1):
        k.sharp_loft(sp, [[(s * .7, -1.3, -.42), (s * 1.08, -1.2, -.42), (s * 1.08, 1.2, -.42), (s * .7, 1.3, -.42)],
                          [(s * .7, -1.1, .1), (s * 1.0, -1.0, .05), (s * 1.0, 1.0, .05), (s * .7, 1.1, .1)]],
                     chamfer=.03)
    a.part('Ramp_lines', 'Armor').box((1.0, 1.6, .02), loc=(0, 4.2, .25), rot=(.42, 0, 0), bevel=0)
    a.part('Doors', 'Armor').box((.02, .5, .9), loc=(-.88, -3.6, .3), bevel=0)
    # High wing, the four nacelles, the propellers.
    wing = a.part('Wings', 'Team')
    _c130_wing(a, wing, 16.3, (-1.0, 1.95), (-.62, 1.05), 1.18)
    for i, x in enumerate((-4.7, -2.4, 2.4, 4.7)):
        k.lathe(a.part('Nacelles', 'Team'), [(.1, -1.75), (.24, -1.6), (.3, -1.2), (.32, .2), (.24, .9), (.1, 1.2)],
                loc=(x, 0, 1.0), rot=(-R90, 0, 0), seg=12)
        a.part('Intakes', 'Undercarriage').box((.22, .05, .12), loc=(x, -1.6, .82), bevel=0)
        a.part('Exhaust', 'Steel').cyl(.06, .3, loc=(x + .22, .4, 1.15), rot=K.FORWARD, seg=6, bevel=0)
        _gunship_prop(a, 'Propeller' if i == 0 else f'Propeller_{i + 1}', (x, -1.85, 1.0), .82, 4, phase=i * .3)
    # Tall fin, tailplane, the dorsal fillet.
    K.fin(a.part('Fins', 'Team'), (3.6, 2.2), (5.2, 1.0), 2.95, z0=1.0, t=.1)
    # External fuel tanks on pylons between the inner and outer engines (the C-130's 1,360-gallon tanks).
    for s in (-1, 1):
        a.part('Pylons', 'Armor').box((.08, .9, .3), loc=(s * 3.55, -.4, .93), bevel=0)
        K.drop_tank(a.part('Drop_tanks', 'Team'), (s * 3.55, -.45, .62), .2, 2.4)
    K.wing(a.part('Tailplanes', 'Team'), (4.4, 1.5), (5.2, .7), 2.6, x0=.15, z=1.45, t=.1)
    # The gun deck on the left (+X): M102 105 mm aft, Bofors 40 mm, GAU-12 25 mm forward, ports, a blast panel.
    gd = a.part('Gun_ports', 'Undercarriage')
    guns = a.part('Guns', 'Steel')
    for (y, z, r, L, tip) in ((3.05, -.15, .07, 1.25, 2.03), (1.55, -.1, .04, .95, 1.67), (-2.9, -.15, .03, .7, 1.44)):
        gd.box((.04, .6, .45), loc=(.86, y, z), bevel=0)
        k.lathe(guns, [(r * 1.6, 0), (r * 1.6, .25), (r, .3), (r, L - .12), (r * 1.4, L - .1), (r * 1.4, L)],
                loc=(tip - L, y, z), rot=(0, R90, 0), seg=8)
    k.lathe(a.part('Howitzer_brake', 'Armor'), [(.11, 0), (.11, .16), (0, .16)], loc=(1.88, 3.05, -.15),
            rot=(0, R90, 0), seg=8)
    a.part('Gun_bores', 'Undercarriage').cyl(.05, .01, loc=(2.04, 3.05, -.15), rot=ACROSS, seg=8, bevel=0)
    K.panel(a, a.part('Armor', 'Armor'), (1.2, .8), (.86, 2.3, .2), (1, 0, 0), t=.03, rivet=.25)
    a.part('Gun_deck_windows', 'Glass').box((.02, .3, .2), loc=(.87, -1.6, .45), bevel=0)
    # Sensor turrets: the nose radar blister (left), IR / TV balls under the forward fuselage, the ALLTV pod.
    k.lathe(a.part('Sensor', 'PlasterWhite'), [(0, -.4), (.25, -.3), (.3, .1), (.25, .35)], loc=(.55, -5.0, .1),
            rot=K.FORWARD, seg=10)
    st_ = a.part('Sensor_turrets', 'Armor')
    for (x, y) in ((.35, -3.9), (.5, -.8)):
        k.lathe(st_, [(0, 0), (.16, -.02), (.18, -.12), (.14, -.24), (0, -.26)], loc=(x, y, -.48), seg=10)
    # Flare dispensers on the rear fuselage, antennas, beacon, wing lights.
    for s in (-1, 1):
        K.flare_dispenser(a, (s * .62, 3.1, -.1), normal=(s, 0, -.4), cols=4, rows=2, cell=.06)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.1, .15, .05), loc=(s * 8.1, -.6, 1.4),
                                                                          bevel=0)
    for y in (-2.0, 0.5):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, 1.23), h=.18, chord=.2)
    K.beacon(a, (0, 1.8, 1.24), r=.07)
    a.part('Team_band', 'Team').box((.02, 4.0, .18), loc=(-.88, 0.0, .65), bevel=0)
    a.pivot('Muzzle_main', (2.03, 3.05, -.15))
    a.pivot('Muzzle_gun', (1.67, 1.55, -.1))
    a.pivot('Muzzle_mg', (1.44, -2.9, -.15))
    a.pivot('Point_fire', (0, -.2, .95))
    a.pivot('Point_exhaust', (-3.96, -.51, .84))
    k.clean(a)
    W.merge_static(a)


BUILDERS = {
    'stealth_bomber': (stealth_bomber, dict(ao_distance=.6, grime_height=0, ground=False)),
    'wingman_drone': (wingman_drone, dict(ao_distance=.25, grime_height=0, ground=False)),
    'recon_jet': (recon_jet, dict(ao_distance=.5, grime_height=0, ground=False)),
    'sky_gunship': (sky_gunship, dict(ao_distance=.5, grime_height=0, ground=False)),
}
