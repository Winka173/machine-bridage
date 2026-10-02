"""Prompt 27 experiment 1 (DECISIONS "27 experiment 1"): the four experiment models rebuilt with the improved kit, one
variable at a time, merged last in build_assets.all_builders() so these builders win (reverting is one line there).

    MB_P27_VARIANT=v0  the original builders (the control: the baseline files)
    MB_P27_VARIANT=v1  V1: the new kit primitives (mb_kit27) inside the builders' own geometry
    MB_P27_VARIANT=v2  V2 (the default, the shipped models): V1 plus the shared parts library (mb_parts27) for the
                       sub-assemblies (running gear, hatches, barrel, MG mount, smoke launchers, antennas, rotor heads,
                       nozzles and engines, pylons, rails and racks, canopy frames)

Every model keeps its node names, moving parts, materials, the COLOR_0 bake, its proportions and its `_hd` twin
(main_battle_tank_hd, fighter_jet_hd, attack_helicopter_hd are these builders with detail=True). Icarus (silver_bug,
shared by hyperion and icarus_mk0) keeps Mount_gun / Mount_gun.001-.003 and every part node; its wreck keeps the
original builder (not in the experiment).

Headless: MB_P27_VARIANT=v1 blender --background --python Tools/blender/build_assets.py -- main_battle_tank
"""
import math
import os

from mathutils import Vector

import mb_detail as hd
import mb_kit27 as k
import mb_p25_models as p25
import mb_parts27 as parts
import mb_vehicles as mv
from mb_vehicles import ACROSS, FORWARD, R90

VARIANT = os.environ.get('MB_P27_VARIANT', 'v2').strip().lower()


def _level():
    return {'v0': 0, 'v1': 1, 'v2': 2}.get(VARIANT, 2)


# ============================================================================= main battle tank
def main_battle_tank(a, detail=False):
    """Main battle tank (mb_p25_models.main_battle_tank) on the improved kit; see the module notes."""
    if _level() == 0:
        return p25.main_battle_tank(a, detail)
    _mbt(a, detail, _level() >= 2)
    k.clean(a)


def _mbt(a, detail, v2):
    hd.mark(a, detail)
    half = p25.MBT_HULL / 2
    if v2:
        parts.track_unit(a, 1.18, 5.72, .86, .27, 7, .5, sprocket_end=1)
    else:
        p25._lean_tracks(a, 1.18, 5.72, .86, .27, 7, .5, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    # Lower hull and upper hull: the same side profiles, extruded with chamfered ends and rounded profile corners.
    k.extrude(armor, [(-2.55, .4), (-2.97, .8), (-2.9, .95), (2.88, .95), (2.9, .5), (2.62, .4)], 1.84, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-half - .02, .84), (-2.05, 1.18), (2.78, 1.21), (half, 1.08), (half, .88)], 2.9, axis='X',
              chamfer=.06, corner=.04)
    # Panel insets: an appliqué plate on the upper glacis and the rear plate.
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.0, width=.07, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.04, depth=.01)
    # The engine-deck grille sits in a recess cut into the deck (a cheap, clean boolean on one closed plate).
    k.cut(hull, lambda tool: k.block(tool, (1.56, .96, .14), loc=(0, 1.92, 1.225), chamfer=0))
    for s in (-1, 1):
        mv._skirt(a, s, 1.47, -2.82, -1.52, .5, 1.17, 1, thick=.1, bolts=False)
        mv._skirt(a, s, 1.46, -1.49, 2.55, .56, 1.17, 2, thick=.07, bolts=False)
        mv._headlight(a, s * 1.12, -2.72, 1.1, guard=False)
        mv._taillight(a, s * 1.1, half + .02, 1.0)
        mv._exhaust(a, s * .5, half + .02, .72, .5, .22)
    with k.mirrored(steel):
        k.block(steel, (.16, .16, .12), loc=(.42, -2.99, .66), chamfer=.02)                     # tow hooks
    if v2:
        parts.hatch(a, -.45, -1.72, 1.18, .24, handle=False)
    else:
        mv._hatch(a, -.45, -1.72, 1.18, .24, handle=False)
    mv._periscopes(a, [(-.45 + dx, -2.05, 1.18, 0) for dx in (-.17, 0, .17)])
    deck = a.part('Deck', 'Undercarriage')
    deck.grille(1.5, .9, loc=(0, 1.92, 1.19), rot=(-R90, 0, 0), slats=6, depth=.1, thickness=.05)
    mv._grille_frame(a, 0, 1.92, 1.21, 1.5, .9)
    with k.mirrored(armor):
        k.block(armor, (.46, .95, .2), loc=(1.18, 1.95, 1.29), chamfer=.03)                    # fender bins
        k.block(armor, (.36, .3, .1), loc=(.75, .95, 1.24), chamfer=.02)                       # deck fillers
    steel.cyl(1.02, .1, loc=(p25.MBT_TURRET[0], p25.MBT_TURRET[1], 1.21), seg=16, bevel=0)     # turret ring
    a.pivot('Point_exhaust', (0, half + .1, .75))
    a.pivot('Point_fire', (0, 1.92, 1.25))

    t = a.pivot('Turret', p25.MBT_TURRET)
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.3, -1.5), (.3, -1.5), (1.12, -1.02), (1.2, -.85), (1.2, 1.05), (1.08, 1.72), (.92, 1.9),
               (-.92, 1.9), (-1.08, 1.72), (-1.2, 1.05), (-1.2, -.85), (-1.12, -1.02)]
    # A sharp-edged loft: the same plan and taper, chamfered vertical corners and a chamfered roof edge.

    def ring(z, scale, off=0.0):
        pts = [(x * scale, y * scale) for x, y in outline]
        if off:
            pts = k.offset2d(pts, off)
        return [(x, y, z) for x, y in pts]
    k.sharp_loft(turret, [ring(.03, 1.0), ring(.66, .935), ring(.71, .93, .05)], chamfer=.045)
    k.inset(turret, lambda c, n, f: n.z > .95, width=.08, depth=.012)                          # roof plate
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.66, .34, .46), loc=(0, -1.52, .38), chamfer=.04, taper=(.92, .9))           # mantlet
    for s in (-1, 1):                                                                            # cheek add-on plates
        k.block(tarm, (.62, .1, .44), loc=(s * .72, -1.3, .37), rot=(0, 0, s * .54), chamfer=.02)
    k.block(tarm, (1.62, .34, .42), loc=(0, 2.05, .36), chamfer=.03)                             # bustle box
    a.part('Tarp', 'Canvas', t).cyl(.13, 1.3, loc=(0, 2.02, .7), rot=ACROSS, seg=8, bevel=0)
    for s in (-1, 1):
        k.block(tarm, (.18, 1.1, .4), loc=(s * 1.3, 1.0, .28), chamfer=.03)                      # bustle bins
        if v2:
            parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.07, -.5, .58, s, count=3, gap=.08, r=.05,
                                 depth=.15)
        else:
            mv._smoke(a, a.part('Smoke', 'Steel', t), 1.07, -.5, .58, s, count=3, gap=.08, r=.05, depth=.15)
    # Greebles on the bustle roof behind the hatches: stowage blocks, deterministic.
    k.greebles(tarm, (0, 1.35, .72), (1, 0, 0), (0, 1, 0), (1.1, .5), 4, seed=2701, height=(.05, .11),
               chamfer=.012)
    tsteel = a.part('Turret_steel', 'Steel', t)
    k.lathe(tsteel, [(.15, -.08), (.15, .06), (.13, .08)], loc=(-.62, .2, .78), seg=12, worn=(1,))
    k.block(tarm, (.34, .3, .17), loc=(-.62, .2, .92), chamfer=.03)
    glass = a.part('Sight', 'Glass', t)
    glass.box((.24, .03, .1), loc=(-.62, .04, .93), bevel=0)
    k.block(tarm, (.36, .42, .24), loc=(-.66, -.95, .8), chamfer=.03)
    glass.box((.26, .03, .13), loc=(-.66, -1.17, .82), bevel=0)
    if v2:
        parts.hatch(a, .55, .45, .72, .27, parent=t, seg=10)
    else:
        mv._hatch(a, .55, .45, .72, .27, parent=t, seg=10)
    mv._periscopes(a, [(.55, .08, .72, 0)], parent=t)
    # 120 mm smooth-bore gun, 1.8 m past the nose.
    y0, length, z = -1.66, 3.26, .38
    if v2:
        parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .085, seg=16 if detail else 12, sleeve=1.235,
                     extractor=(.4, 1.65, .42), brake_name='Muzzle_brake', brake='collar')
    else:
        L = length
        k.lathe(a.part('Main_cannon', 'Steel', t),
                [(.105, -.02), (.105, L * .4 - .25), (.14, L * .4 - .19), (.14, L * .4 + .19), (.105, L * .4 + .25),
                 (.105, L * .67), (.085, L * .67 + .03), (.085, L)], loc=(0, y0, z), rot=FORWARD, seg=12, worn=(2, 3))
        k.ring(a.part('Muzzle_brake', 'Undercarriage', t), [(.07, L - .02), (.11, L - .02), (.11, L + .14),
                                                             (.07, L + .14)],
               loc=(0, y0, z), rot=FORWARD, seg=10, worn=(2,))
    a.pivot('Muzzle_main', (0, y0 - length - .15, z), t)
    mv._coax(a, t, .42, -1.46, .5, length=.4, housing=.26)
    if v2:
        parts.mg_mount(a, t, (.55, .45, .74), length=.8, shield=False)
        ant = a.part('Antennas', 'Steel', t)
        for s in (-1, 1):
            parts.antenna(ant, (s * .82, 1.6, .72), h=.22, r=.05)   # short: the hull height stays the baseline's
    else:
        mv._roof_mg(a, t, (.55, .45, .74), length=.8, shield=False)
    if detail:
        for u in (.08, .92):
            mv._glacis_bolts(a, (-half - .02, .84), (-2.05, 1.18), u, -1.3, 1.3, 11)
        for s in (-1, 1):
            mv._shackle(a, s * .42, -3.07, .56)
            mv._filler(a, s * .75, 1.2, 1.21)
        mv._eyes(a, [(s * 1.25, -1.9, 1.19, 0) for s in (-1, 1)] + [(s * 1.25, 2.5, 1.21, R90) for s in (-1, 1)])
        mv._eyes(a, [(-.95, 1.5, .72, 0), (.95, 1.5, .72, 0), (.85, -.7, .72, -.5)], parent=t)
        mv._vent(a, .1, 1.1, .72, parent=t)
        bolts = a.part('Turret_bolts', 'Steel', t)
        for dx in (-.24, .24):
            for dz in (-.15, .15):
                hd.bolt(bolts, (dx, -1.69, .38 + dz), hd.FRONT, r=.02, h=.026)
        hd.bolt_ring(bolts, hd.frame((-.62, .2, 1.0)), .17, 8, r=.012, h=.018)
        a.part('Turret_seams', 'Armor', t).box((2.0, .025, .014), loc=(0, -.1, .735), bevel=0)


# ============================================================================= Su-27
def fighter_jet(a, detail=False):
    """Air-superiority fighter (mb_p25_models.fighter_jet) on the improved kit; see the module notes."""
    if _level() == 0:
        return p25.fighter_jet(a, detail)
    _fighter(a, detail, _level() >= 2)
    k.clean(a)


def _fighter(a, detail, v2):
    from mb_air import (BACKWARD, LEFT, RIGHT, Planform, _aam, _aam_parts, _canopy, _dome, _intake, _nozzle, _patch,
                        _pylon, _sec, _skin_z, _surface, _upright, _wing)
    from mb_air3 import _fighter_jet_detail, _sq
    hd.mark(a, detail)
    n = 16 if detail else 12
    bv = 1.0 if detail else 0.0
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    glow = a.part('Wing_lights', 'TeamGlow')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=n, pt=2.4, pb=2.8)
    hull = [sec(-7.6, .43, -.42, .38), sec(-6.6, .53, -.5, .5), sec(-5.4, .6, -.54, .56), sec(-4.2, .66, -.56, .58),
            sec(-3.0, .76, -.55, .55), sec(-1.8, 1.12, -.5, .5), sec(-.4, 1.58, -.45, .46), sec(1.5, 1.8, -.42, .44),
            sec(4.0, 1.95, -.36, .38), sec(6.0, 1.85, -.28, .32), sec(7.2, 1.15, -.2, .24)]
    body.loft(hull, bevel=.02 * bv, seg=1)
    armor.loft([[(0, -9.4, -.03)], sec(-9.0, .16, -.16, .1), sec(-8.4, .3, -.3, .24), sec(-7.55, .425, -.415, .372)])
    zi = _skin_z(hull, -7.15, -.17)
    armor.cyl(.1, .12, loc=(-.17, -7.15, zi), seg=8, bevel=0)
    a.part('Sensor', 'Glass').sphere(.11, loc=(-.17, -7.17, zi + .07), seg=6, rings=4)
    glass = a.part('Canopy', 'Glass')
    st = [(-6.95, .14, .64), (-6.55, .34, .88), (-6.0, .43, 1.02), (-5.3, .45, 1.07), (-4.6, .4, 1.0),
          (-4.1, .27, .87), (-3.75, .13, .72)]
    stations = [(y, w, _skin_z(hull, y, w) - .03, z1) for y, w, z1 in st]
    if v2 and detail:
        # The library canopy: the glass, a sill frame swept round its base and the windscreen bow.
        parts.canopy(glass, a.part('Canopy_frames', 'Armor'), [_dome(y, w, z0, z1, 9) for y, w, z0, z1 in stations],
                     sill=.09, bows=(1,), bow_r=.04)
    elif detail:
        _canopy(glass, a.part('Canopy_frames', 'Armor'), stations, bows=(-6.5,))
    else:
        glass.loft([_dome(y, w, z0, z1, 7) for y, w, z0, z1 in stations], bevel=0)
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1, 9 if detail else 7) for y, w, z1 in
             ((-4.3, .34, .92), (-3.2, .42, .8), (-1.4, .46, .68), (1.2, .46, .62), (3.8, .4, .56), (6.2, .3, .44))]
    body.loft(spine + [[(0, 7.3, .3)]], bevel=.02 * bv, seg=1)
    # Panel insets on the dorsal spine between the cockpit and the tail (raised panels, their frames the lines).
    # (Panel insets on this lofted skin were tried: +400 triangles, COLOR_0 -0.7 %, nothing visible on the card;
    # dropped. The close-up variant draws its own panel lines, mb_air3._fighter_jet_detail.)
    _patch(armor, spine, -3.0, -1.7, 1, 5)
    lerx = Planform(.45, 2.6, -6.4, -.52, 6.9, 2.0, .14, .08, .06, .04)
    wing = Planform(.9, 6.1, -2.17, 2.51, 5.4, 1.45, .3, .1, .02, -.08)
    for frame in (RIGHT, LEFT):
        _surface(body, lerx, frame, bevel=.01 * bv)
        if detail:
            _wing(body, moving, wing, frame, cs=[(1.95, 3.9, .75), (3.9, 5.75, .74)])
        else:
            _surface(body, wing, frame, bevel=0)
    lips = a.part('Intake_lips', 'Team')
    m = 10 if detail else 8
    for s in (-1, 1):
        x = s * 1.12
        trunk = [_sq(x, -2.6, -.6, .31, .41, n=m), _sq(x, .5, -.62, .33, .42, p=3.5, n=m),
                 _sq(x, 4.5, -.6, .36, .42, p=3, n=m), _sq(x, 6.6, -.55, .43, .43, p=2.4, n=m),
                 _sq(x, 7.3, -.52, .45, .45, p=2.2, n=m)]
        if detail:
            _intake(a, body, lips, dark, (x, -3.4, -.58), .3, .4, .25, trunk, depth=.3, wall=.07, n=m)
        else:
            from mb_air import _squircle
            rot = (R90 + .25, 0, 0)
            fm = hd.frame((x, -3.4, -.58), rot)
            outline = _squircle(.3, .4, m)
            body.loft([[tuple(fm @ Vector((px, py, 0))) for px, py in outline]] + trunk, bevel=0)
            lips.shell(outline, .3, .07, loc=(x, -3.4, -.58), rot=rot, bevel=0)
            dark.box((.48, .64, .03), loc=tuple(fm @ Vector((0, 0, .03))), rot=rot, bevel=0)
        k.block(armor, (.06, 1.0, .5), loc=(s * .8, -3.2, -.42), chamfer=.012)                  # splitter
        if v2:
            parts.jet_nozzle(a, x, 7.3, -.52, .42, 1.05, seg=14 if detail else 10, glow=detail)
        else:
            _nozzle(a, x, 7.3, -.52, .42, 1.05, seg=14 if detail else 8, glow=detail)
        if not detail:
            a.part('Exhaust_glow', 'Alloy').cyl(.26, .04, loc=(x, 7.3 + .55, -.52), rot=FORWARD, seg=8, bevel=0)
    fin = Planform(0, 3.45, 4.3, 7.0, 2.9, 1.0, .13, .05)
    stab = Planform(1.95, 5.0, 6.3, 7.9, 2.1, .95, .12, .05, -.03)
    ventral = Planform(0, .75, 5.5, 6.1, 1.2, .6, .1, .05)
    for s in (-1, 1):
        x = s * 1.95
        boom = [_sec(y, w, zb, zt, n=10 if detail else 8) for y, w, zb, zt in
                ((2.8, .12, -.12, .1), (3.6, .22, -.25, .2), (7.4, .22, -.25, .2), (8.4, .16, -.16, .12))]
        body.loft([[(x, 2.2, -.02)]] + [[(x + p[0], p[1], p[2]) for p in r] for r in boom] + [[(x, 8.9, -.02)]],
                  bevel=.01 * bv, seg=1)
        frame = _upright(x, .14, .06)
        if detail:
            _wing(body, moving, fin, frame, cs=[(.35, 3.2, .68)], lower=1.0)
        else:
            _surface(body, fin, frame, lower=1.0, bevel=0)
        tip = Vector(frame(3.45, 7.1, 0))
        k.lathe(armor, [(0, -.32), (.05, -.26), (.07, -.15), (.07, .3)], loc=tuple(tip + Vector((0, .1, 0))),
                rot=BACKWARD, seg=6, worn=(1, 2))                                                               # fin-tip fairing
        glow.box((.08, .16, .08), loc=tuple(tip + Vector((0, .44, 0))), bevel=0)
        _surface(body, ventral, _upright(x, -.2, math.pi - .3), lower=1.0, bevel=.012 * bv)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame, bevel=.012 * bv)
    body.loft([sec(6.5, .45, -.22, .3), sec(8.0, .28, -.14, .2), sec(8.9, .15, -.08, .1), [(0, 9.4, .0)]],
              bevel=.01 * bv, seg=1)
    a.part('Beacon', 'TeamGlow').sphere(.08, loc=(0, 9.38, 0), seg=6, rings=4)
    k.block(armor, (.24, 1.3, .16), loc=(-.86, -3.05, .15), chamfer=.03, taper=(.7, .9))          # gun fairing
    k.lathe(steel, [(.06, -.22), (.06, .18), (.08, .19), (.08, .26)], loc=(-.86, -3.82, .15), rot=FORWARD, seg=6,
            worn=(2,))                                                                          # cannon, muzzle ring
    a.pivot('Muzzle_gun', (-.86, -4.1, .15))
    tips = _aam_parts(a, 'Wingtip_missiles')
    for s in (-1, 1):
        x = s * 6.12
        if v2:
            parts.launch_rail(armor, x, 2.25, 3.95, -.01, w=.14, h=.14)
        else:
            k.block(armor, (.14, 1.7, .14), loc=(x, 3.1, -.08), chamfer=.02)
        _aam(tips, (s * 6.24, 2.75, -.2), length=2.3, r=.1, seg=6, canards=False, fin=1.3)
        glow.box((.08, .16, .08), loc=(x, 2.2, -.08), bevel=0)
    aams = _aam_parts(a)
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        for x in (s * 2.75, s * 4.3):
            zb = wing.bottom(abs(x)) + .05
            zp = zb - .38
            if v2:
                parts.pylon(pylons, x, -.1 + abs(x) * .2, 1.7 + abs(x) * .2, zb, zp + .1, w=.14)
            else:
                _pylon(pylons, x, -.1 + abs(x) * .2, 1.7 + abs(x) * .2, zb, zp + .1, w=.14)
            _aam(aams, (x, .45 + abs(x) * .2, zp), length=3.0, r=.12, seg=6, canards=False, fin=1.2)
    zp = wing.bottom(3.5) + .05 - .38
    a.pivot('Muzzle_missile', (0, -.55, zp))
    a.pivot('Muzzle_aam', (0, 2.75 - 1.2, -.2))
    a.pivot('Point_exhaust', (0, 8.4, -.52))
    a.pivot('Point_fire', (0, 1.5, .2))
    if detail:
        _fighter_jet_detail(a, hull, spine, lerx, wing, Planform(0, 3.0, 4.3, 6.75, 2.9, 1.05, .13, .05), stab)
    p25._scale_asset(a, p25.FIGHTER_K)


# ============================================================================= attack helicopter
def attack_helicopter(a, detail=False):
    """Attack helicopter (mb_p25_models.attack_helicopter) on the improved kit; see the module notes."""
    if _level() == 0:
        return p25.attack_helicopter(a, detail)
    _apache(a, detail, _level() >= 2)
    k.clean(a)


def _apache(a, detail, v2):
    from mb_air import (BACKWARD, _bubble, _exhaust_duct, _hellfire, _octagon, _pylon, _rotor_head, _tail_rotor)
    hd.mark(a, detail)
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    hull = [_octagon(-3.0, .12, .56, .8), _octagon(-2.75, .23, .45, .95), _octagon(-2.2, .27, .42, 1.0),
            _octagon(-1.2, .3, .42, 1.02), _octagon(-.2, .32, .45, 1.1), _octagon(.6, .28, .5, 1.08),
            _octagon(1.0, .18, .7, 1.03)]
    # Sharp-edged lofts: the Apache's flat-panel fuselage and boom with two-step chamfers on every chine.
    k.sharp_loft(body, hull, chamfer=.035 if detail else .03)
    boom = [_octagon(.9, .17, .72, 1.02), _octagon(2.8, .08, .82, .98)]
    k.sharp_loft(body, boom, chamfer=.02)
    k.extrude(body, [(2.3, .95), (2.85, .93), (3.02, 1.78), (2.74, 1.8)], .08, axis='X', chamfer=.015, corner=.03)
    k.block(body, (.95, .3, .04), loc=(0, 2.6, .8), chamfer=.01, taper=(1, .75))                     # stabilator
    for s in (-1, 1):
        before = k.snapshot(body)
        k.block(body, (.17, 1.45, .3), loc=(s * .33, -1.3, .72), chamfer=.04, taper=(.8, .94))         # avionics bays
        k.inset(body, lambda c, n, f, s=s: n.x * s > .9, width=.05, depth=-.012, since=before)           # bay doors
    if v2 and detail:
        frames = a.part('Canopy_frames', 'Armor')
        parts.canopy(glass, frames, [_bubble(-2.55, .17, .93, 1.0), _bubble(-2.3, .25, .98, 1.18),
                                     _bubble(-1.98, .26, 1.0, 1.21)],
                     sill=.04, bows=(2,), bow_r=.02, sills=(1, 0), arch=(1, 2, 3, 4, 5, 0))
        parts.canopy(glass, frames, [_bubble(-2.0, .27, 1.0, 1.28), _bubble(-1.72, .28, 1.02, 1.4),
                                     _bubble(-1.2, .27, 1.04, 1.41), _bubble(-.95, .21, 1.06, 1.28)],
                     sill=.04, bows=(0, 3), bow_r=.02, sills=(1, 0), arch=(1, 2, 3, 4, 5, 0))
    else:
        glass.loft([_bubble(-2.55, .17, .93, 1.0), _bubble(-2.3, .25, .98, 1.18), _bubble(-1.98, .26, 1.0, 1.21)],
                   bevel=0)
        glass.loft([_bubble(-2.0, .27, 1.0, 1.28), _bubble(-1.72, .28, 1.02, 1.4), _bubble(-1.2, .27, 1.04, 1.41),
                    _bubble(-.95, .21, 1.06, 1.28)], bevel=0)
    for s in (-1, 1):
        x = s * .34
        if v2:
            parts.engine_nacelle(body, dark, (x, .45, 1.12), .15, 1.0, rot=FORWARD, seg=12 if detail else 10)
        else:
            k.lathe(body, [(.12, 0), (.15, .06), (.15, .94), (.135, 1.0)], loc=(x, .45, 1.12), rot=FORWARD,
                    seg=10, worn=(1, 2))
            dark.cyl(.11, .03, loc=(x, -.56, 1.12), rot=FORWARD, seg=10, bevel=0)
        _exhaust_duct(a, (s * .4, .6, 1.13), s * -.3, size=(.18, .34, .18))
    k.block(body, (.42, .95, .26), loc=(0, -.45, 1.2), chamfer=.04, taper=(.72, .8))                  # pylon
    k.greebles(armor, (0, .45, 1.09), (1, 0, 0), Vector((0, 1, -.06)).normalized(), (.2, .5), 3, seed=2703,
               height=(.03, .06), chamfer=.01)
    steel.cyl(.06, .36, loc=(0, -.45, 1.4), seg=8, bevel=0)
    r = a.pivot('Rotor', (0, -.45, 1.58))
    if v2:
        parts.rotor_head(a, r, 4, 3.0, .26, hub=.18, phase=math.pi / 4, t=.035, cap=.08, stripe=.22, droop=.05)
    else:
        _rotor_head(a, r, 4, 3.0, .26, hub=.18, phase=math.pi / 4, t=.035, cap=.08, stripe=.22, droop=.05)
    steel.cyl(.04, .12, loc=(0, -.45, 1.83), seg=6, bevel=0)
    armor.sphere((.22, .22, .08), loc=(0, -.45, 1.94), seg=10, rings=6)
    k.lathe(armor, [(.12, -.15), (.12, .15)], loc=(0, -2.95, .6), rot=ACROSS, seg=10, worn=())        # TADS drum
    sensor = a.part('Sensor', 'Glass')
    for s in (-1, 1):
        k.block(armor, (.06, .2, .2), loc=(s * .17, -2.94, .6), chamfer=.012)
        sensor.box((.04, .03, .08), loc=(s * .17, -3.05, .62), bevel=0)
    sensor.box((.1, .03, .08), loc=(0, -3.08, .6), bevel=0)
    armor.cyl(.06, .1, loc=(0, -2.85, .93), seg=8, bevel=0)
    pylons = a.part('Pylons', 'Armor')
    stingers = a.part('Stinger_tubes', 'Fuel')
    wing_foil = [(-.23, 0), (-.18, .035), (.02, .045), (.23, .012), (.23, -.012), (.02, -.035), (-.18, -.03)]
    for s in (-1, 1):
        k.extrude(body, wing_foil, 1.0, loc=(s * .78, -.3, .82), rot=(0, s * -.05, 0), axis='X', chamfer=.012)
        if v2:
            parts.pylon(pylons, s * .62, -.48, -.12, .8, .7, w=.07)
            parts.rocket_pod(a, s * .62, -.72, .56, .12, .66, s)
            parts.hellfire_rack(a, 0, -.64, 0, s, detail=detail)
        else:
            _pylon(pylons, s * .62, -.48, -.12, .8, .7, w=.07)
            a.part('Pods', 'Armor').lathe([(.066, .66), (.1, .6), (.12, .43), (.12, .03), (.11, 0)],
                                          loc=(s * .62, -.72, .56), rot=BACKWARD, seg=10)
            a.part('Pod_bands', 'Hazard').cyl(.126, .04, loc=(s * .62, -.58, .56), rot=FORWARD, seg=10, bevel=0)
            a.part('Pod_face', 'Undercarriage').cyl(.09, .02, loc=(s * .62, -.726, .56), rot=FORWARD, seg=10, bevel=0)
            k.block(armor, (.05, .56, .28), loc=(s * 1.08, -.34, .6), chamfer=.01)
            for x in (1.02, 1.14):
                for z in (.66, .52):
                    if detail:
                        _hellfire(a, s * x, -.64, z, length=.66, r=.045, fins=x > 1.1)
                    else:
                        a.part('Missiles', 'Fuel').cyl(.045, .6, loc=(s * x, -.64 + .36, z), rot=FORWARD, seg=6,
                                                       bevel=0)
                        a.part('Missile_seekers', 'Glass').cyl(.045, .08, r2=.015, loc=(s * x, -.64 + .04, z),
                                                               rot=FORWARD, seg=6, bevel=0)
        for dz in (-.035, .035):
            stingers.cyl(.035, .5, loc=(s * 1.32, -.42, .82 + dz), rot=FORWARD, seg=6, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.05, .1, .05), loc=(s * 1.29, -.12, .83), bevel=0)
    a.pivot('Muzzle_rocket', (0, -.72, .56))
    a.pivot('Muzzle_missile', (0, -.64, .59))
    a.pivot('Muzzle_aam', (0, -.68, .82))
    tyres = a.part('Tyres', 'Rubber')
    for s in (-1, 1):
        k.block(steel, (.06, .08, .34), loc=(s * .42, -1.55, .3), rot=(0, s * .35, 0), chamfer=.012)
        k.lathe(tyres, [(.09, -.04), (.125, -.04), (.13, -.02), (.13, .02), (.125, .04), (.09, .04)],
                loc=(s * .5, -1.55, .13), rot=ACROSS, seg=10, worn=(2, 3))
    k.block(steel, (.05, .3, .06), loc=(0, 2.45, .72), rot=(.9, 0, 0), chamfer=.01)
    tyres.cyl(.09, .06, loc=(0, 2.55, .09), rot=ACROSS, seg=8, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 2.9, 1.82), seg=6, rings=4)
    if v2:
        ant = a.part('Antennas', 'Steel')
        for y in (1.35, 2.0):
            zt = 1.02 + (.98 - 1.02) * (y - .9) / 1.9
            parts.antenna(ant, (0, y, zt - .01), h=.24, r=.04, seg=6)
    g = a.pivot('Mount_gun', (0, -2.3, .38))
    k.lathe(a.part('Gun_turret', 'Armor', g), [(.1, -.03), (.1, .05), (.085, .07)], seg=10, worn=(1,))
    gun = a.part('Gun', 'Steel', g)
    k.block(gun, (.1, .26, .09), loc=(0, -.08, -.06), chamfer=.012)
    k.lathe(gun, [(.035, -.06), (.035, .48), (.045, .5), (.045, .56), (.025, .56), (.025, .53), (0, .53)],
            loc=(0, -.2, -.06), rot=FORWARD, seg=6)
    a.pivot('Muzzle_gun', (0, -.76, -.06), g)
    armor.cyl(.06, .1, loc=(-.08, 2.82, 1.45), rot=ACROSS, seg=8, bevel=0)
    tr = a.pivot('Tail_rotor', (-.16, 2.82, 1.45))
    if v2:
        parts.tail_rotor(a, tr, 4, .56, .1, t=.02, phase=math.pi / 4, side=-1)
    else:
        _tail_rotor(a, tr, 4, .56, .1, t=.02, phase=math.pi / 4, side=-1)
    a.pivot('Point_exhaust', (.45, .8, 1.13))
    a.pivot('Point_fire', (0, -.2, 1.1))
    if detail:
        rivets = a.part('Rivets', 'Steel')
        for s in (-1, 1):
            hd.bolt_line(rivets, (s * .42, -1.95, .87), (s * .42, -.65, .87), 8, rot=hd.side_rot(s), r=.012, h=.018)
            hd.bolt_line(rivets, (s * .15, -2.6, .88), (s * .15, -2.2, .96), 3, r=.01, h=.016)


# ============================================================================= Icarus (silver_bug)
def silver_bug(a):
    """Icarus (mb_pt9_models.silver_bug) on the improved kit: the original builder with its hull, superstructure,
    greebles and pods (V1) and engines, bridge masts and flak barrels (V2) swapped for the kit's versions for the
    duration of the call. Every node keeps its name and place."""
    import mb_orbital as orb
    import mb_pt9_models as pt9
    if _level() == 0:
        return pt9.silver_bug(a)
    swaps = {(pt9, '_hull'): _ic_hull(pt9._hull), (pt9, '_superstructure'): _ic_superstructure(pt9._superstructure),
             (pt9, '_greebles'): _ic_greebles, (pt9, '_pods'): _ic_pods}
    if _level() >= 2:
        swaps.update({(pt9, '_engines'): _ic_engines, (pt9, '_bridge'): _ic_bridge, (orb, '_build_flak'): _ic_flak})
    saved = {key: getattr(*key) for key in swaps}
    try:
        for (mod, name), fn in swaps.items():
            setattr(mod, name, fn)
        pt9.silver_bug(a)
    finally:
        for (mod, name), fn in saved.items():
            setattr(mod, name, fn)
    k.clean(a)


def _ic_hull(original):
    def run(a, lift, wreck, rng):
        import mb_pt9_models as pt9
        original(a, lift, wreck, rng)
        # Raised deck plates in the hull's deck facets (the bow deck ahead of the superstructure shows them).
        k.inset(a.part('Hull', pt9.HULL_MAT, flat=True), lambda c, n, f: n.z > .97, width=.3, depth=.03)
    return run


def _ic_superstructure(original):
    def run(a, lift, wreck):
        import mb_pt9_models as pt9
        original(a, lift, wreck)
        # Raised plates in the steps' top facets, the frames the panel lines.
        k.inset(a.part('Superstructure', pt9.HULL_MAT, flat=True), lambda c, n, f: n.z > .97, width=.32, depth=.03)
    return run


def _ic_greebles(a, lift, wreck, rng):
    """Deck gear on the steps (the kit's greebles): equipment blocks and slatted vents along the front step's
    outboard strips, vents and comms masts (V2: library antennas) on the upper step."""
    import mb_pt9_models as pt9
    gear = a.part('Deck_gear', pt9.DARK_MAT, flat=True)
    bare = a.part('Deck_gear_steel', 'Steel')
    vents = a.part('Deck_vents', 'Undercarriage')
    top = 3.0 + .03 + lift                       # the raised step plates' top
    for sx in (-1, 1):
        f = 1.6
        seed = 2704 if sx > 0 else 2705
        while f > -12.0:
            f1 = max(-12.0, f - 2.6)
            fc = (f + f1) / 2
            inner = pt9._lerp_table(pt9.STEP2, fc)[0] + .45
            outer = pt9._lerp_table(pt9.STEP1, fc)[0] - .25
            if outer - inner > .6:
                x = sx * (inner + outer) / 2
                k.greebles(gear, pt9._P(x, fc, top), (1, 0, 0), (0, 1, 0), (outer - inner, f - f1), 3, seed=seed,
                           height=(.12, .36), fill=.75, chamfer=.03, vents=vents)
            seed += 7
            f = f1
        k.block(vents, (.8, 1.4, .03), loc=pt9._P(sx * 1.1, -6.2, 3.4 + .03 + .01 + lift), chamfer=0)
        k.block(vents, (.6, 1.0, .03), loc=pt9._P(sx * .9, .4, 3.4 + .03 + .01 + lift), chamfer=0)
        if not wreck:
            if _level() >= 2:
                parts.antenna(bare, pt9._P(sx * 1.4, -1.4, 3.4 + .03 + lift), h=1.25, r=.06, seg=8)
            else:
                bare.cyl(.05, 1.3, loc=pt9._P(sx * 1.4, -1.4, 3.4 + .65 + lift), seg=6, bevel=0)


def _ic_pods(a, lift, wreck):
    """mb_pt9_models._pods with the bay mouths cut into the pods' fronts (a boolean recess, a dark back plate at its
    bottom) instead of a dark plate on the face."""
    import mb_orbital as orb
    import mb_pt9_models as pt9
    P, POD, lerp = pt9._P, pt9.POD, pt9._lerp_table
    body = a.part('Flank_pods', pt9.HULL_MAT, flat=True)
    band = a.part('Pod_bands', 'Charred' if wreck else 'Team', flat=True)
    dark = a.part('Pod_dark', 'Undercarriage')
    lamp = a.part('Pod_lamps', 'Lamp')
    arm = a.part('Pod_barbettes', pt9.DARK_MAT)

    def ring(f, xc, w, zb, zt, sx, grow=0.0):
        h = zt - zb
        w += grow
        zb, zt = zb - grow, zt + grow
        pts = [(xc - w * .6, zb), (xc + w * .6, zb), (xc + w, zb + h * .28), (xc + w, zt - h * .22), (xc + w * .7, zt),
               (xc - w * .7, zt), (xc - w, zt - h * .22), (xc - w, zb + h * .28)]
        return [P(sx * x, f, z + lift) for x, z in pts]
    for sx in (-1, 1):
        body.loft([ring(*row, sx) for row in POD], bevel=.04, seg=1)
    k.inset(body, lambda c, n, f: n.z > .97, width=.25, depth=.025)                     # raised plates on the tops
    f, xc, w, zb, zt = POD[0]
    mouth = (w * 1.3, (zt - zb) * .5)
    zc = (zb + zt) / 2 - .05 + lift

    def cutters(tool):
        for sx in (-1, 1):
            k.block(tool, (mouth[0], .7, mouth[1]), loc=P(sx * xc, f - .2, zc), chamfer=0)
    cut = k.cut(body, cutters)
    for sx in (-1, 1):
        for f0 in (1.4, -4.4):
            rows = [[f0] + lerp(POD, f0), [f0 - .5] + lerp(POD, f0 - .5)]
            band.loft([ring(*r, sx, grow=.02) for r in rows], bevel=0)
        # The dark plate at the recess's bottom, or (when the solver gave nothing back) on the face as before.
        dark.box((mouth[0] + .02, .03, mouth[1] + .02), loc=P(sx * xc, f - .52 if cut else f + .03, zc), bevel=0)
        lamp.box((w * 1.1, .03, .06), loc=P(sx * xc, f + .03, zt - .15 + lift), bevel=0)
        for fv in (-.6, -1.4, -3.4):
            xv = lerp(POD, fv)[0]
            dark.box((.8, .35, .03), loc=P(sx * xv, fv, 2.02 + .025 + .01 + lift), bevel=0)
    for name in ('Mount_gun', 'Mount_gun.001'):
        x, y, z = orb._node(name, lift)
        arm.cyl(.62, .84, loc=(x, y, z - .68), seg=18, bevel=.03, bseg=1)
    for mount in ('Mount_gun.002', 'Mount_gun.003'):
        x, y, z = orb._node(mount, lift) if mount in orb.NODES else pt9._crash_loc(mount, lift)
        arm.cyl(.58, .2, loc=(x, y, z - .1), seg=14, bevel=.02, bseg=1)


def _ic_engines(a, lift, wreck):
    """mb_pt9_models._engines with the six round ion engines from the parts library (shroud, cooling band, worn lip,
    a dark throat with the glow at its bottom) round the original drive bell."""
    import mb_orbital as orb
    import mb_pt9_models as pt9
    from mb_air import BACKWARD
    right, forward, up = orb.NODES['Thruster_main']
    t = a.pivot('Thruster_main', orb._pos(right, forward, up + lift))
    block = a.part('Engine_block', pt9.DARK_MAT, t, flat=True)
    block.box((9.0, 2.4, 3.6), loc=(0, -1.75, .15), bevel=.14, seg=1, taper=(.92, .9))
    a.part('Engine_block_plates', pt9.PLATE_MAT, t, flat=True).box((6.0, 1.6, .05), loc=(0, -1.85, 1.96), bevel=0)
    shell = a.part('Engine_shrouds', 'Steel', t)
    glow = a.part('Engine_glow', 'TeamGlow', t)
    bands = a.part('Engine_bands', pt9.DARK_MAT, t)
    shell.lathe([(1.0, 0), (.9, .4), (1.05, 1.0), (1.35, 1.7), (1.5, 2.1), (1.46, 2.14), (1.3, 1.7), (1.0, 1.0), (.85, .4),
                 (.9, .02)], loc=(0, -.75, 0), rot=BACKWARD, seg=24)
    bands.cyl(1.12, .3, loc=(0, -.45, 0), rot=pt9.ALONG_Y, seg=24, bevel=.02, bseg=1)
    glow.cyl(.84, .04, loc=(0, -.28, 0), rot=pt9.ALONG_Y, seg=20, bevel=0)
    for x, z, r in ((2.05, .85, .76), (2.05, -.85, .76), (3.6, 0, .66), (-2.05, .85, .76), (-2.05, -.85, .76),
                    (-3.6, 0, .66)):
        parts.engine_bell(shell, bands, glow, (x, -.75, z), r, 1.3, rot=BACKWARD, seg=18, throat=.86)


def _ic_bridge(a, loc, rot, team, wreck):
    """mb_pt9_models._bridge with library antennas for the sensor masts."""
    import mb_pt9_models as pt9
    body = a.part('Bridge' if not wreck else 'Bridge_fallen', 'Armor' if wreck else pt9.HULL_MAT, flat=True)
    prof = [(-.45, 0), (-1.1, .58), (-.75, 1.05), (1.1, 1.0), (1.1, 0)]
    body.prism(prof, 6.3, loc=loc, rot=rot, axis='X', bevel=.04, seg=1)
    if wreck:
        return
    x, y, z = loc
    a.part('Bridge_windows', 'Lamp').box((5.8, .06, .11), loc=(x, y - 1.08, z + .6), bevel=0)
    a.part('Bridge_glass', 'Glass').box((5.5, .05, .22), loc=(x, y - .925, z + .83), rot=(-.64, 0, 0), bevel=0)
    for sx in (-1, 1):
        team.box((.05, 1.5, .6), loc=(sx * 3.17, y + .2, z + .5), bevel=0)
    gear = a.part('Bridge_gear', 'Steel')
    parts.antenna(gear, (x + .8, y + .3, z + 1.0), h=1.35, r=.08, seg=8)
    parts.antenna(gear, (x - .5, y + .5, z + 1.0), h=.85, r=.06, seg=8)
    gear.box((.9, .05, .05), loc=(x + .8, y + .3, z + 2.15), bevel=0)
    a.part('Sensor_ball', 'Medical').sphere(.36, loc=(x - 1.6, y + .35, z + 1.1), seg=12, rings=7, cut=-.3)


def _ic_flak(a, mount, muzzle, tag, loc, deployed=False):
    """mb_orbital._build_flak with library barrels (sleeve, extractor, a double-baffle muzzle brake, a dark bore)
    along the same lines to the same muzzle point."""
    from mb_phase2 import dotted
    m = a.pivot(dotted(mount), loc)
    a.part('Flak_base' + tag, 'Armor', m).cyl(.5, .14, loc=(0, 0, .06), seg=18, bevel=.03, bseg=2)
    fb = a.part('Flak_body' + tag, 'Steel', m)
    fb.cyl(.42, .18, loc=(0, 0, .2), seg=18, bevel=.03, bseg=2)
    fb.box((.68, .62, .34), loc=(0, .04, .42), bevel=.06, seg=2, taper=(.82, .86))
    a.part('Flak_sight' + tag, 'Glass', m).box((.14, .06, .1), loc=(.24, -.3, .5), bevel=0)
    tilt = math.radians(55 if deployed else 15)
    d = Vector((0, -math.cos(tilt), math.sin(tilt)))
    tips = []
    for x in (-.13, .13):
        p0 = Vector((x, -.02, .42))
        p1 = p0 + d * 1.05
        parts.barrel(a, 'Flak_guns' + tag, m, x, p0.y, p0.z, .75, .036, seg=8, sleeve=1.2, extractor=(.35, 1.45, .16),
                     brake_name='Flak_brakes' + tag, brake='baffle', brake_mat='Steel', rot=(R90 - tilt, 0, 0))
        tips.append(p1)
    a.pivot(dotted(muzzle), tuple((tips[0] + tips[1]) / 2), m)


BUILDERS = {
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
    'fighter_jet': (fighter_jet, dict(ao_distance=.35, ground=False)),
    'attack_helicopter': (attack_helicopter, dict(ao_distance=.4, grime_height=.3)),
    'silver_bug': (silver_bug, dict(ao_distance=.6, ground=False)),
}
