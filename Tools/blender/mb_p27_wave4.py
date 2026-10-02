"""Prompt 27 wave 4 (DECISIONS "27 wave 4a ..."): aircraft rebuilt on the V2 kit (mb_kit27 + mb_parts27), merged last in
build_assets.all_builders() after mb_p27_wave3. Same models as before: every runtime node name, pivot, material,
proportion kept (see Docs/models/WAVES_4_6_PLAN.md and WAVE3_PLAN.md's standing brief). Lane A of the two-lane plan; the
tower builders live in mb_p27_wave6.py.

Pass 4a: scout_heli, gunship_heli, elite_attack_helicopter (on the V2 Apache), swarm_carrier, recon_drone, strike_drone,
wingman_drone, drop_pod. The prompt 29 5.5 flare tubes (mb_p29_details.flare_tubes) are on the FLARE models of the pass
(scout_heli, gunship_heli, swarm_carrier).
"""
import math

from mathutils import Vector

import mb_detail as hd
import mb_kit27 as k
import mb_p25_models as p25
import mb_p25_models2 as m2
import mb_p27_experiment as exp
import mb_p29_details as p29
import mb_parts27 as parts
from mb_air import BACKWARD, FORWARD, LEFT, RIGHT, Planform, _bubble, _dome, _octagon, _surface, _upright
from mb_vehicles import ACROSS, R90

TAU = math.tau


def _flares(a, name, x, y, z, count=4, gap=.06, r=.03, depth=.12, rows_dy=.5):
    """The prompt 29 flare tubes: p29.FLARE_MODELS[name] rows a side, `rows_dy` apart along Y."""
    for row in range(p29.FLARE_MODELS[name]):
        for s in (-1, 1):
            p29.flare_tubes(a, None, x, y + row * rows_dy, z, s, count=count, gap=gap, r=r, depth=depth)


def _barrel(part, x, y, z, length, r, seg=6):
    """A forward-pointing gun barrel from y (its root) with a muzzle ring, one turned surface."""
    k.lathe(part, [(r, 0), (r, length * .9), (r * 1.3, length * .92), (r * 1.3, length), (r * .6, length)],
            loc=(x, y, z), rot=FORWARD, seg=seg, worn=(2,))


def _prop2(a, name, loc, r, blades=3, chord=.08):
    """m2._prop with a turned spinner and chamfered blades; same pivot, same part names."""
    p = a.pivot(name, loc)
    k.lathe(a.part(f'{name}_hub', 'Armor', p), [(r * .2, 0), (r * .2, r * .2), (r * .14, r * .36), (0, r * .46)],
            rot=FORWARD, seg=8, worn=(1,))
    bl = a.part(f'{name}_blades', 'Undercarriage', p)
    for i in range(blades):
        u = i * TAU / blades + .3
        k.block(bl, (chord, .03, r), loc=(math.cos(u) * r / 2, 0, math.sin(u) * r / 2), rot=(0, -u + R90, 0),
                chamfer=0, taper=(.6, 1))
    return p


# ============================================================================= scout helicopter (MH-6)
def scout_heli(a):
    """Light scout helicopter (m2.scout_heli) on the V2 kit: the same egg cabin and boom lofts, a framed bubble canopy,
    chamfered skids and struts, a turned mast, the V2 rotors, turned minigun barrels and V2 rocket pods, flare tubes on
    the boom; same nodes and pivots."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    body = a.part('Fuselage', 'Team')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    armor = a.part('Armor', 'Armor')
    m2._fuselage(body, ((-.8, .3, .44, .98), (-.45, .44, .36, 1.12), (0, .46, .38, 1.14), (.45, .4, .46, 1.06),
                        (.75, .2, .64, .96)), nose=(0, -.98, .68), tail=(0, .86, .8), n=12, pt=2.2, pb=2.2)
    parts.canopy(a.part('Canopy', 'Glass'), a.part('Canopy_frames', 'Armor'),
                 [_dome(y, w, z0, z1, 7) for y, w, z0, z1 in
                  ((-.95, .14, .6, .76), (-.8, .3, .5, .98), (-.5, .42, .6, 1.1), (-.2, .44, .78, 1.13))],
                 sill=.03, bows=(1, 2), bow_r=.016)
    m2._fuselage(body, ((.7, .1, .72, .92), (2.35, .05, .8, .88)), n=8)                              # tail boom
    k.extrude(body, [(2.13, .82), (2.47, .82), (2.4, 1.3), (2.24, 1.3)], .04, axis='X')              # fin
    k.block(body, (.7, .18, .03), loc=(0, 2.28, 1.3), chamfer=0)                                       # T-tail
    skid = [(-1.06, .17), (-.98, .06), (-.92, .005), (.8, .005), (.86, .075), (-.88, .075), (-1.0, .17)]
    for s in (-1, 1):
        k.extrude(steel, skid, .07, loc=(s * .44, -.1 + .1, 0), axis='X')
        for y in (-.45, .35):
            k.block(steel, (.06, .06, .4), loc=(s * .37, y, .24), rot=(0, -s * .36, 0), chamfer=0)    # struts
    k.block(steel, (1.9, .12, .06), loc=(0, -.1, .5), chamfer=.01)                                    # the plank
    k.block(dark, (.36, .3, .2), loc=(0, .5, 1.12), chamfer=.03)                                       # engine
    k.lathe(steel, [(.09, -.02), (.06, .03), (.05, .24), (.07, .27)], loc=(0, -.05, 1.1), seg=8, worn=(1,))
    r = a.pivot('Rotor', (0, -.05, 1.34))
    parts.rotor_head(a, r, 5, 1.65, .13, hub=.1, phase=.3, t=.02, cap=.05, stripe=.18, droop=.03)
    tr = a.pivot('Tail_rotor', (-.06, 2.36, .95))
    parts.tail_rotor(a, tr, 2, .3, .06, t=.015, side=-1)
    guns = a.part('Miniguns', 'Steel')
    for s in (-1, 1):
        _barrel(guns, s * .85, -.075, .44, .57, .045)
        k.block(a.part('Minigun_housings', 'Armor'), (.12, .24, .12), loc=(s * .85, -.02, .46), chamfer=0)
        parts.rocket_pod(a, s * .6, -.42, .38, .07, .5, s, seg=8)
    m2._launch_muzzles(a, 'gun', [(s * .85, -.645, .44) for s in (-1, 1)])
    m2._launch_muzzles(a, 'rocket', [(s * .6, -.44, .38) for s in (-1, 1)])
    parts.antenna(a.part('Antennas', 'Steel'), (0, .78, .945), h=.2, r=.03, seg=6)
    a.part('Beacon', 'TeamGlow').box((.06, .06, .05), loc=(0, .6, 1.22), bevel=0)
    _flares(a, 'scout_heli', .09, 1.5, .8, count=3, gap=.06, r=.025, depth=.1)
    a.pivot('Point_exhaust', (0, .7, 1.1))
    a.pivot('Point_fire', (0, .1, 1.1))
    k.clean(a)


# ============================================================================= assault gunship (Mi-24)
def gunship_heli(a):
    """Assault gunship (m2.gunship_heli) on the V2 kit: the same body lofts, framed stepped canopies, V2 nacelles,
    airfoil stub wings with V2 rocket pods and turned ATGM rails, door guns, a turned chin gun, the V2 rotors, chamfered
    gear, flare tubes on the boom; same nodes and pivots."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    body = a.part('Fuselage', 'Team')
    steel = a.part('Steel', 'Steel')
    armor = a.part('Armor', 'Armor')
    dark = a.part('Undercarriage', 'Undercarriage')
    m2._fuselage(body, ((-3.3, .14, .5, .76), (-2.9, .3, .38, .92), (-1.8, .44, .3, 1.02), (-.4, .6, .28, 1.12),
                        (.9, .56, .34, 1.14), (1.5, .3, .62, 1.12)), nose=(0, -3.5, .6), n=12)
    m2._fuselage(body, ((1.4, .24, .7, 1.1), (3.3, .1, .86, 1.04)), n=8)                              # tail boom
    k.extrude(body, [(2.9, 1.0), (3.45, .98), (3.62, 1.9), (3.3, 1.92)], .1, axis='X', chamfer=.015, corner=.03)
    k.block(body, (1.0, .32, .05), loc=(0, 3.1, .92), chamfer=0)                                       # stabilator
    glass, frames = a.part('Canopy', 'Glass'), a.part('Canopy_frames', 'Armor')
    parts.canopy(glass, frames, [_bubble(-3.2, .16, .72, .86), _bubble(-2.9, .26, .82, 1.06),
                                 _bubble(-2.55, .26, .88, 1.08)], sill=.035, bows=(1,), bow_r=.02, sills=(1, 0),
                 arch=(1, 2, 3, 4, 5, 0))
    parts.canopy(glass, frames, [_bubble(-2.4, .3, .96, 1.14), _bubble(-2.1, .34, 1.0, 1.3), _bubble(-1.7, .33, 1.02, 1.3),
                                 _bubble(-1.45, .28, 1.04, 1.18)], sill=.035, bows=(1, 2), bow_r=.02, sills=(1, 0),
                 arch=(1, 2, 3, 4, 5, 0))
    foil = [(-.3, 0), (-.24, .045), (.02, .06), (.3, .016), (.3, -.016), (.02, -.05), (-.24, -.04)]
    tubes = a.part('Launch_tubes', 'Fuel')
    pods_at = (1.05, 1.35)
    for s in (-1, 1):
        parts.engine_nacelle(body, dark, (s * .38, .1, 1.26), .2, 1.3, rot=FORWARD, seg=10)
        a.part('Windows', 'Glass').box((.03, .7, .24), loc=(s * .6, -.3, .8), bevel=0)               # cabin windows
        k.extrude(body, foil, 1.3, loc=(s * 1.0, -.25, .78), rot=(0, s * .2, 0), axis='X', chamfer=.012)
        for x in pods_at:
            parts.rocket_pod(a, s * x, -.65, .56 - (x - .6) * .2, .12, .75, s)
        for dz in (-.07, .07):
            k.lathe(tubes, [(.05, 0), (.05, .7), (.062, .72), (.062, .75)], loc=(s * 1.66, -.955, .64 + dz),
                    rot=BACKWARD, seg=6, caps=(True, True), worn=(2,))
        k.block(steel, (.06, .3, .4), loc=(s * .45, -1.9, .22), chamfer=0)                           # nose gear
        tyres = a.part('Tyres', 'Rubber')
        k.lathe(tyres, [(.1, -.05), (.14, -.05), (.145, -.02), (.145, .02), (.14, .05), (.1, .05)],
                loc=(s * .5, -1.9, .14), rot=ACROSS, seg=10, worn=(2, 3))
        k.lathe(tyres, [(.11, -.05), (.16, -.05), (.165, -.02), (.165, .02), (.16, .05), (.11, .05)],
                loc=(s * .75, .6, .16), rot=ACROSS, seg=10, worn=(2, 3))
        k.block(steel, (.06, .06, .3), loc=(s * .62, .6, .28), rot=(0, -s * .62, 0), chamfer=0)       # main strut
        _barrel(steel, s * .65, -.34, .75, .17, .03)                                                   # door guns
        k.block(armor, (.1, .16, .1), loc=(s * .6, -.3, .74), chamfer=0)
    m2._launch_muzzles(a, 'rocket', [(s * 1.2, -.67, .44) for s in (-1, 1)])
    m2._launch_muzzles(a, 'missile', [(s * 1.66, -.97, .64) for s in (-1, 1)])
    a.pivot('Muzzle_door_l', (.65, -.5, .75))
    a.pivot('Muzzle_door_r', (-.65, -.5, .75))
    k.lathe(steel, [(.12, -.02), (.08, .04), (.07, .3), (.1, .34)], loc=(0, -.55, 1.4), seg=8, worn=(1,))   # mast
    r = a.pivot('Rotor', (0, -.55, 1.72))
    parts.rotor_head(a, r, 5, 3.45, .26, hub=.18, phase=.2, t=.035, cap=.08, stripe=.24, droop=.06)
    tr = a.pivot('Tail_rotor', (.14, 3.4, 1.5))
    parts.tail_rotor(a, tr, 3, .6, .1, t=.02, side=1)
    g = a.pivot('Mount_gun', (0, -3.1, .42))
    k.lathe(armor, [(0, .14), (.1, .1), (.14, 0), (.1, -.1), (0, -.14)], loc=(0, -3.1, .4), seg=10)
    gun = a.part('Gun', 'Steel', g)
    k.block(gun, (.1, .2, .09), loc=(0, -.1, -.02), chamfer=.01)
    _barrel(gun, 0, -.02, -.02, .58, .04)
    a.pivot('Muzzle_gun', (0, -.6, -.02), g)
    ant = a.part('Antennas', 'Steel')
    parts.antenna(ant, (0, 1.2, 1.12), h=.24, r=.04, seg=6)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 3.5, 1.92), seg=6, rings=4)
    _flares(a, 'gunship_heli', .2, 1.9, .8, count=4, gap=.07, r=.032, depth=.12)
    a.pivot('Point_exhaust', (.45, .2, 1.26))
    a.pivot('Point_fire', (0, -.3, 1.2))
    k.clean(a)


# ============================================================================= elite attack helicopter
def _elite_apache_v2(a):
    """The V2 Apache (mb_p27_experiment) with the elite's gold marks (m2._elite_heli_upgrade)."""
    exp.attack_helicopter(a)
    m2._elite_heli_upgrade(a)


# ============================================================================= drone mothership (C-130 class)
def _fpv(a, x, y, z, i=0):
    """An FPV drone at the battle scale (0.5 m across, drawn large enough to read), nose to -Y: a chamfered frame, turned
    motors, a tapered warhead."""
    frame = a.part('Drone_frames', 'Undercarriage')
    k.block(frame, (.12, .2, .07), loc=(x, y, z), chamfer=0)
    for s in (-1, 1):
        k.block(frame, (.52, .05, .03), loc=(x, y, z + .01), rot=(0, 0, s * math.pi / 4 + .02 * i), chamfer=0)
    motors = a.part('Drone_motors', 'Steel')
    for dx, dy in ((.18, .18), (-.18, .18), (.18, -.18), (-.18, -.18)):
        k.lathe(motors, [(.05, 0), (.05, .06), (.035, .075)], loc=(x + dx, y + dy, z + .0), seg=5, worn=(1,))
    k.lathe(a.part('Drone_warheads', 'Hazard'), [(0, 0), (.04, .02), (.04, .13), (.015, .2)], loc=(x, y - .14, z - .06),
            rot=FORWARD, seg=6)
    a.part('Drone_lights', 'TeamGlow').box((.05, .05, .03), loc=(x, y + .08, z + .045), bevel=0)


def swarm_carrier(a):
    """Drone mothership (p25._c130 with the ramp lowered) with the V2 FPV drones on the rails, the prompt 29 flare tubes
    (two rows a side, on the rear fuselage) and `k.clean` (the jet rule); the airframe, props and nodes are the old ones."""
    p25._c130(a, ramp_open=True)
    for i, (x, y) in enumerate(((-.3, 3.25), (.3, 3.6), (-.3, 4.0), (.3, 4.35))):
        _fpv(a, x, y, p25.RAMP[1] - (y - p25.RAMP[0]) * p25.RAMP[2] + .12, i)
    a.pivot('Muzzle_drone', (0, p25.RAMP[0] + 1.9, p25.RAMP[1] - 1.9 * p25.RAMP[2] - .05))
    _flares(a, 'swarm_carrier', .76, 2.0, -.2, count=3, gap=.12, r=.045, depth=.16, rows_dy=.7)
    k.clean(a)


# ============================================================================= recon drone (TB2)
def recon_drone(a):
    """Recon drone (m2.recon_drone) on the V2 kit: a sharp-chined body, an airfoil tapered wing, chamfered booms and
    inverted V, a turned pusher propeller, V2 pylons; same nodes and pivots."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    body = a.part('Fuselage', 'Team')
    wing = a.part('Wings', 'Fuel')
    rings = [_octagon(y, w, zb, zt) for y, w, zb, zt in ((-1.1, .1, -.1, .08), (-.7, .14, -.14, .13),
                                                         (.3, .13, -.12, .12), (1.0, .07, -.05, .06))]
    k.sharp_loft(body, [[(0, -1.28, -.02)]] + rings + [[(0, 1.12, 0)]], chamfer=.025)
    pf = Planform(0, 2.4, -.27, -.24, .34, .3, .06, .035, .15, .15)
    for frame in (RIGHT, LEFT):
        _surface(wing, pf, frame, bevel=0)
    for s in (-1, 1):
        k.block(wing, (.06, .06, 1.5), loc=(s * .6, .55, .1), rot=(R90, 0, 0), chamfer=0)             # tail booms
        k.block(wing, (.62, .22, .03), loc=(s * .3, 1.28, -.06), rot=(0, s * .6, 0), chamfer=0)       # inverted V
        a.part('Wing_lights', 'TeamGlow').box((.05, .08, .04), loc=(s * 2.39, -.05, .15), bevel=0)
    k.lathe(a.part('Sensor_mount', 'Armor'), [(.08, 0), (.08, -.1), (.1, -.14)], loc=(0, -.95, -.1), seg=8)
    a.part('Sensor', 'Glass').sphere(.1, loc=(0, -.95, -.2), seg=8, rings=5)
    _prop2(a, 'Propeller', (0, 1.16, 0), .34, blades=2)
    aams = m2._aam_parts(a)
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        parts.pylon(pylons, s * .85, -.25, .05, .13, -.03, w=.05)
        m2._aam(aams, (s * .85, -.1, -.1), length=.5, r=.04, seg=6, canards=False, fin=1.4)
    m2._launch_muzzles(a, 'missile', [(s * .85, -.37, -.1) for s in (-1, 1)])
    a.pivot('Muzzle_gun', (0, -1.07, -.22))
    a.pivot('Point_exhaust', (0, 1.0, .05))
    a.pivot('Point_fire', (0, 0, .15))
    k.clean(a)


# ============================================================================= wingman drone (XQ-58)
def wingman_drone(a):
    """Loyal-wingman drone (m2.wingman_drone) on the V2 kit: a sharp-chined body, the cranked wing and V tail as before,
    a chamfered dorsal intake, a turned exhaust; same nodes and pivots."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    body = a.part('Fuselage', 'Team')
    rings = [_octagon(y, w, zb, zt, k=.35) for y, w, zb, zt in ((-1.3, .12, -.08, .06), (-.7, .26, -.14, .14),
                                                                (.2, .3, -.14, .16), (1.3, .2, -.08, .1))]
    k.sharp_loft(body, [[(0, -1.75, -.02)]] + rings + [[(0, 1.72, 0)]], chamfer=.03)
    wing = Planform(.25, 1.65, -.1, .75, 1.35, .4, .08, .03)
    for frame in (RIGHT, LEFT):
        _surface(body, wing, frame, bevel=0)
    fin = Planform(0, .55, .95, 1.3, .6, .3, .05, .02)
    for s in (-1, 1):
        _surface(body, fin, _upright(s * .22, .1, .6), lower=1.0, bevel=0)
    k.block(a.part('Intake', 'Undercarriage'), (.3, .5, .12), loc=(0, -.35, .2), chamfer=.03, taper=(.7, 1))
    k.lathe(a.part('Exhaust_glow', 'Alloy'), [(.1, 0), (.1, .04), (.07, .04)], loc=(0, 1.72, 0), rot=BACKWARD,
            seg=8, caps=(True, True), worn=(1,))
    aams = m2._aam_parts(a)
    for s in (-1, 1):
        m2._aam(aams, (s * .75, .1, -.14), length=.7, r=.045, seg=6, canards=False)
        a.part('Wing_lights', 'TeamGlow').box((.05, .08, .04), loc=(s * 1.64, .95, 0), bevel=0)
        parts.launch_rail(a.part('Pylons', 'Armor'), s * .75, -.1, .35, -.1, w=.04, h=.04)
    m2._launch_muzzles(a, 'missile', [(s * .75, -.27, -.14) for s in (-1, 1)])
    a.pivot('Point_exhaust', (0, 1.75, 0))
    a.pivot('Point_fire', (0, .2, .15))
    k.clean(a)


# ============================================================================= strike drone (MQ-9)
def strike_drone(a):
    """Strike drone (m2.strike_drone) on the V2 kit: the same airfoil wing and Y tail, a sharp-chined body with the
    bulged radar nose, a turned pusher propeller, V2 pylons and bombs, a sensor turret; same nodes and pivots."""
    from mb_air import _bomb, _store_parts
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    body = a.part('Fuselage', 'Team')
    m2._fuselage(body, ((-1.8, .2, -.2, .22), (-1.3, .26, -.24, .26), (.2, .22, -.2, .18), (1.7, .1, -.08, .08)),
                 nose=(0, -2.15, 0), tail=(0, 1.95, 0), n=10)
    wing = Planform(.18, 4.0, -.3, -.12, .6, .28, .09, .04, .1, .16)
    for frame in (RIGHT, LEFT):
        _surface(body, wing, frame, bevel=0)
    fin = Planform(0, .75, 1.35, 1.7, .5, .3, .05, .02)
    for s in (-1, 1):
        _surface(body, fin, _upright(s * .06, .08, .7), lower=1.0, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .1, .05), loc=(s * 3.99, -.1, .17), bevel=0)
    _surface(body, Planform(0, .5, 1.4, 1.65, .4, .28, .05, .02), _upright(0, -.08, math.pi), lower=1.0, bevel=0)
    _prop2(a, 'Propeller', (0, 2.0, 0), .5, blades=3)
    aams = m2._aam_parts(a)
    bombs = _store_parts(a, prefix='Ordnance')
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        for x in (s * 1.6, s * 1.95):
            parts.pylon(pylons, x, -.35, 0, .12, -.04, w=.05)
            m2._aam(aams, (x, -.25, -.12), length=.6, r=.04, seg=6, canards=False, fin=1.4)
        parts.pylon(pylons, s * .9, -.4, .05, .12, -.06, w=.06)
        _bomb(bombs, (s * .9, -.2, -.2), length=.8, r=.07, seg=8, guided=True, lean=True)
    m2._launch_muzzles(a, 'missile', [(s * 1.78, -.56, -.12) for s in (-1, 1)])
    m2._launch_muzzles(a, 'rocket', [(s * .9, -.62, -.2) for s in (-1, 1)])
    k.lathe(a.part('Sensor_mount', 'Armor'), [(.1, 0), (.1, -.14), (.13, -.2)], loc=(0, -1.55, -.17), seg=8)
    a.part('Sensor', 'Glass').sphere(.12, loc=(0, -1.55, -.28), seg=8, rings=5)
    parts.antenna(a.part('Antennas', 'Steel'), (0, .3, .2), h=.14, r=.03, seg=6)
    a.pivot('Point_exhaust', (0, 1.8, .05))
    a.pivot('Point_fire', (0, 0, .2))
    k.clean(a)


# ============================================================================= drop pod
def drop_pod(a):
    """Drop pod (mb_orbital.drop_pod) on the V2 kit: a turned capsule hull with worn seam rings, the scorched heat shield,
    a retro-rocket ring with turned bells, chamfered fins and struts, the hatch with its coaming; same parts and size."""
    hull = a.part('Hull', 'Armor')
    k.lathe(hull, [(1.55, -3.0), (1.6, -2.8), (1.45, -1.5), (1.25, 0.2), (0.95, 1.6), (0.5, 2.5), (0.0, 3.0)],
            seg=26, worn=(1, 2))
    k.lathe(a.part('Heat_shield', 'Charred', flat=True), [(0, -3.1), (1.5, -2.98), (1.58, -2.82), (1.4, -2.68), (0, -2.8)],
            seg=26, worn=(1, 2))
    k.ring(a.part('Stripe', 'Team'), [(1.42, -.2), (1.57, -.2), (1.57, .35), (1.42, .35)], seg=26)
    seams = a.part('Seams', 'Undercarriage')
    for z, r in ((-1.0, 1.4), (.7, 1.13)):                                                   # panel seams
        k.ring(seams, [(r + .005, z - .025), (r + .03, z - .02), (r + .03, z + .02), (r + .005, z + .025)], seg=26)
    rivet = a.part('Rivets', 'MetalSheet')
    for z in (-1.7, -0.4, 1.0):
        for i in range(12):
            q = i * TAU / 12
            r = 1.3 + 0.25 * (1 - abs(z) / 3.0)
            rivet.cyl(.03, .02, loc=(r * math.cos(q), r * math.sin(q), z), seg=4, bevel=0)
    hatch = a.part('Access_hatch', 'Steel')
    k.lathe(hatch, [(.32, -.04), (.32, .04), (.24, .06), (0, .06)], loc=(1.3 * math.cos(.3), 1.3 * math.sin(.3), .5),
            rot=(0, R90, 0), seg=12, worn=(1,))
    ring = a.part('Retro_ring', 'Steel')
    nozzle = a.part('Retro_glow', 'TeamGlow')
    for i in range(9):
        q = i * TAU / 9
        x, y = 1.5 * math.cos(q), 1.5 * math.sin(q)
        k.lathe(ring, [(.13, -.25), (.13, .2), (.1, .25), (0, .25)], loc=(x, y, -2.55), seg=8, worn=(1,))
        nozzle.cyl(.09, .05, loc=(x, y, -2.82), seg=8, bevel=0)
    struts = a.part('Fin_struts', 'Steel')
    fins = a.part('Fins', 'Armor')
    for i in range(4):
        q = i * TAU / 4 + TAU / 8
        x, y = math.cos(q), math.sin(q)
        a0, b0 = Vector((x * 1.45, y * 1.45, -1.9)), Vector((x * 1.55, y * 1.55, -.3))
        struts.limb(tuple(a0), tuple(b0), .1, .06, bevel=0, seg=1)
        k.block(fins, (.06, 1.0, 2.0), loc=(x * 1.55, y * 1.55, -1.2), rot=(0, 0, q), chamfer=.02, taper=(.35, 1))
    k.lathe(a.part('Hatch', 'Steel'), [(1.05, 2.9), (1.05, 2.98), (.9, 3.02), (0, 3.02)], seg=16, worn=(1,))
    a.part('Hatch_seam', 'Undercarriage').torus(1.05, .02, loc=(0, 0, 2.98), seg=16, ring=4)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 0, 3.15), seg=6, rings=4)
    k.clean(a)


def _opts(name):
    if name == 'swarm_carrier':
        return p25.BUILDERS[name][1]
    if name == 'drop_pod':
        import mb_orbital
        return mb_orbital.BUILDERS[name][1]
    return m2.BUILDERS[name][1]


BUILDERS = {
    'scout_heli': (scout_heli, dict(_opts('scout_heli'), ao_strength=.65)),
    'gunship_heli': (gunship_heli, dict(_opts('gunship_heli'), ao_strength=.65)),
    'elite_attack_helicopter': (m2._elite_on(_elite_apache_v2, glow=('Sensor',), scale=1.1),
                                _opts('elite_attack_helicopter')),
    'swarm_carrier': (swarm_carrier, _opts('swarm_carrier')),
    'recon_drone': (recon_drone, dict(_opts('recon_drone'), ao_strength=.65)),
    'strike_drone': (strike_drone, dict(_opts('strike_drone'), ao_strength=.65)),
    'wingman_drone': (wingman_drone, dict(_opts('wingman_drone'), ao_strength=.65)),
    'drop_pod': (drop_pod, dict(_opts('drop_pod'), ao_strength=.65)),
}
