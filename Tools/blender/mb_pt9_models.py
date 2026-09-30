"""Machine Brigade play-test 9 (DECISIONS 23M): Icarus redrawn as a spaceship, and the stealth jet redrawn slim.

  * silver_bug / silver_bug_wreck (Icarus). Play-test 8's orbital platform (mb_pt8_icarus) read as a space station.
    Icarus is a warship again, but a small one: the language of Star Wars' capital ships (a dagger hull with a clear
    bow and stern, a stepped superstructure, a command tower aft, a bank of engines across the stern, a lit trench
    along the sides) drawn at a frigate's scale, with fewer and bigger parts, and mixed with other ships so it reads
    as none of them:
      - the hull: a faceted dagger that swells aft (the Imperial Star Destroyer's and the Venator's plan, shortened to
        a corvette's proportions, 36 x 18 m), with a recessed, window-lit trench along each side;
      - a keel housing under the bow that carries the ventral laser ball, and a ventral hangar blister round the pod
        bay (Halo's UNSC frigates: the keel-mounted gun, the ventral bays; The Expanse's Rocinante: the keel railgun);
      - two long flank pods from the waist aft, with a dark bay mouth at the front (Battlestar Galactica's flight pods;
        Halo frigates' side pods with RCS thrusters and turrets), carrying the coilgun barbettes forward and the crash
        turrets aft;
      - a stepped superstructure on the deck under an aft command tower whose bridge is a wide hammerhead with a
        lit window band (Star Destroyer layout, Tantive IV's hammerhead cockpit, no shield domes);
      - the stern: a Tantive IV-like bank of seven engines (a big drive bell in the middle, The Expanse's drive cone,
        and six round ion engines with glowing faces round it), and two outboard engine nacelles on pylons at the
        stern corners with outward-canted fins (the Normandy SR-2's nacelles and fins);
      - stubby swept arms carrying the forward RCS blocks off the bow (Halo frigates' RCS pods);
      - surface greebles at a small ship's scale: two-tone hull plates, panel lines, trench windows and boxes, vents,
        antennas, bow sensor glass.
    Colours: light grey metal hull (`MetalSheet`) with off-white plates (`Fuel`), gunmetal trench, keel, engine block
    and pods' ends (`Armor`), the side's colour on the flank pods' bands, the nacelle fins, the tower's cheeks and a
    short stripe on each bow flank, the side's glow in the engines. No red deck stripes, no flight-deck doors, no domes.
    Every node keeps its name and place (mb_orbital.NODES), so parts, muzzles and big attacks play as before: `Turret`
    (the ventral laser ball under the keel housing, `Muzzle_main`), `Mount_gun` / `.001` (coilguns on barbettes at the
    front of the flank pods), `Mount_mg` / `.001` (flak on the superstructure's front step and before the tower),
    `Pd_laser_l` / `_r` (on tubs at the front step's shoulders), `Thruster_main` (the engine bank), `Thruster_fl` /
    `_fr` (the bow RCS blocks), `Thruster_rl` / `_rr` (the stern nacelles), `Pod_bay` (`Muzzle_missile`, under the
    hangar blister), `Uplink` (a dish on a mast on the upper step) and the crash turrets `Mount_gun.002` / `.003`
    (40 mm, on the flank pods, woken on the ground). The wreck is the same ship crashed, raised by mb_orbital.LIFT:
    its tower broken off and the bridge lying beside it, a nacelle fin torn off, the back cracked across the waist,
    plates blown off, scorched, the engines dark, in its crater and debris.
  * stealth_fighter ("Stealth jet"). Prompt 17's airframe (mb_p17_temp, detailed by mb_pt5_models) looked fat: a 5 m
    wide, 1.1 m deep lifting body. Redrawn from scratch as a slim fifth-generation fighter, 18.4 x 13.2 m (the same
    size class): a thin chined fuselage 3 m wide and 0.55 m deep that flares into a flat, wide, trapezoid wing
    (F-22: 42 degree leading edge, the trailing edge swept forward, 2D thrust-vectoring nozzles; J-20: the long,
    blade-thin chined nose; YF-23: the flat body section; Su-57: the tandem belly bays between widely spaced engines;
    F-35: the one-piece frameless canopy), caret intakes under the chines, twin tails canted 27 degrees, all-moving
    tailplanes. Dark gunmetal body, the side's colour on the wings and tails. Kept: `Muzzle_missile` between the noses
    of the two missiles on trapezes under the open main bays, `Muzzle_bomb` at the nose of the guided bomb in the
    rear centre bay, `Muzzle_gun` at the cannon on the left (+X) shoulder. It has no high-detail variant.

Conventions are mb_vehicles'/mb_orbital's: metres, +Z up, Blender -Y is the front, +X the vehicle's left. Team /
TeamGlow parts are recoloured per army at runtime. Touching parts overlap or stand at least 1 cm apart.

Headless: blender --background --python Tools/blender/build_assets.py -- silver_bug stealth_fighter
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mb_orbital as orb  # noqa: E402
from mb_air import BACKWARD, FORWARD, R90, _aam, _aam_parts, _dome  # noqa: E402
from mb_p17_temp import _bay_bomb, _hex, _hex_at, _hex_top, _slab  # noqa: E402
from mb_phase2 import _suffixed  # noqa: E402
from mb_phase8 import autocannon  # noqa: E402

ALONG_Y = (R90, 0, 0)    # a cylinder's axis along Y
ALONG_X = (0, R90, 0)    # a cylinder's axis along X

# ============================================================================= Icarus
HULL_MAT = 'MetalSheet'  # light grey metal
PLATE_MAT = 'Fuel'       # off-white plates
DARK_MAT = 'Armor'       # gunmetal trench, keel, engine block

# The hull, bow to stern: (forward, half-width at the side edge, edge height, deck half-width, deck height,
# keel half-width, keel height). Forward is metres towards the bow (Blender -Y).
HULL = [(19.0, .25, .55, .08, .75, .08, .35),
        (17.0, 1.1, .55, .35, 1.0, .3, -.35),
        (14.0, 2.2, .55, .8, 1.5, .6, -1.2),
        (11.0, 3.0, .6, 1.4, 1.85, .9, -1.75),
        (7.0, 3.95, .6, 2.3, 2.02, 1.3, -2.05),
        (3.0, 4.75, .6, 3.1, 2.1, 1.7, -2.2),
        (-1.0, 5.4, .58, 3.7, 2.1, 2.0, -2.22),
        (-5.0, 6.0, .55, 4.2, 2.1, 2.3, -2.22),
        (-9.0, 6.6, .52, 4.6, 2.1, 2.5, -2.15),
        (-12.0, 6.95, .5, 4.8, 2.1, 2.6, -2.0),
        (-13.3, 6.85, .5, 4.7, 2.0, 2.5, -1.85)]
BOW = 19.5               # the prow's point
TRENCH = (.32, .38, .2)  # the side trench: below and above the edge line, and how deep it is recessed
# The superstructure's two steps: (forward, top half-width, top height); the sides slope out 0.45 m (0.3 m).
STEP1 = [(12.8, .15, 2.05), (11.2, .85, 3.0), (7.0, 2.6, 3.0), (5.0, 3.5, 3.0), (1.0, 3.6, 3.0), (-12.8, 4.1, 3.0)]
STEP2 = [(3.2, .4, 3.05), (2.0, 1.7, 3.4), (-12.8, 2.9, 3.4)]
# The keel housing under the bow: (forward, bottom half-width, side half-width, bottom height).
KEEL = [(15.6, .15, .3, -1.05), (13.5, .5, .9, -1.95), (10.5, .9, 1.25, -2.6), (8.9, 1.12, 1.35, -2.72),
        (5.1, 1.12, 1.35, -2.72), (3.0, .9, 1.2, -2.55), (1.0, .5, .75, -2.3)]
# A flank pod: (forward, centre x, half-width, bottom, top).
POD = [(4.4, 5.3, .55, .45, 1.55), (3.6, 5.4, 1.0, -.3, 2.02), (-2.0, 5.85, 1.05, -.35, 2.02),
       (-7.6, 6.35, 1.0, -.3, 2.02), (-8.6, 6.4, .6, .15, 1.5)]


def _P(x, f, z):
    """(x, forward, z) -> Blender (x, y, z)."""
    return (x, -f, z)


def _lerp_table(table, f):
    """A station table's row interpolated at forward f (rows run bow to stern, f falling)."""
    if f >= table[0][0]:
        return list(table[0][1:])
    if f <= table[-1][0]:
        return list(table[-1][1:])
    for a, b in zip(table, table[1:]):
        if a[0] >= f >= b[0]:
            k = (a[0] - f) / (a[0] - b[0])
            return [p + (q - p) * k for p, q in zip(a[1:], b[1:])]
    return list(table[-1][1:])


def _band(hw, ze):
    """The trench's bottom and top heights and its depth at a station (thinner towards the prow)."""
    k = min(1.0, hw / 2.0)
    return ze - TRENCH[0] * k, ze + TRENCH[1] * k, min(TRENCH[2], hw * .08)


def _top_z(f, x):
    """Height of the hull's upper surface (deck, then the upper flank down to the trench) at forward f, |x|."""
    hw, ze, rw, zt, _kw, _zb = _lerp_table(HULL, f)
    _lo, hi, _d = _band(hw, ze)
    x = abs(x)
    if x <= rw:
        return zt
    if x >= hw:
        return hi
    return zt + (hi - zt) * (x - rw) / (hw - rw)


def _surface_z(f, x):
    """Height of the ship's top at forward f, |x|: the upper step, the front step or the hull."""
    x = abs(x)
    for table, z, lo in ((STEP2, 3.4, 3.2), (STEP1, 3.0, 12.8)):
        if table[-1][0] <= f <= table[0][0] and f <= lo and x <= _lerp_table(table, f)[0]:
            return z
    return _top_z(f, x)


def _yaw(sx, fa, fb, xa, xb):
    """Yaw (about Z) that lays a part's local Y along the line from (sx * xa, fa) to (sx * xb, fb)."""
    dx, dy = sx * (xb - xa), -(fb - fa)
    if dy < 0:
        dx, dy = -dx, -dy
    return math.atan2(-dx, dy)


def _hull_ring(f, lift, sag=0.0):
    hw, ze, rw, zt, kw, zb = _lerp_table(HULL, f)
    lo, hi, d = _band(hw, ze)
    half = [(kw, zb), (hw, lo), (hw - d, lo + .1 * min(1, hw)), (hw - d, hi - .1 * min(1, hw)), (hw, hi), (rw, zt - sag)]
    return [_P(x, f, z + lift) for x, z in half] + [_P(-x, f, z + lift) for x, z in reversed(half)]


def _hull(a, lift, wreck, rng):
    """The dagger hull, its trench, keel housing, hangar blister, plates, panel lines, windows and bow stripes."""
    hull = a.part('Hull', HULL_MAT, flat=True)
    stations = [row[0] for row in HULL]
    # The wreck broke its back across the waist: the deck sags there.
    sag = {3.0: .22, -1.0: .3} if wreck else {}
    rings = [[_P(0, BOW, .55 + lift)]] + [_hull_ring(f, lift, sag.get(f, 0.0)) for f in stations]
    hull.loft(rings, bevel=.04, seg=1)
    # The keel housing (its top buried in the hull) and the hangar blister round the pod bay.
    keel = a.part('Keel_housing', DARK_MAT, flat=True)
    krings = []
    for f, bw, w, zb in KEEL:
        top = _lerp_table(HULL, f)[5] + .3
        half = [(bw, zb), (w, zb + .3), (w * .85, top)]
        krings.append([_P(x, f, z + lift) for x, z in half] + [_P(-x, f, z + lift) for x, z in reversed(half)])
    keel.loft(krings, bevel=.03, seg=1)
    a.part('Keel_sensor', 'Glass').box((.5, .5, .12), loc=_P(0, 15.2, -1.05 + lift), rot=(-.5, 0, 0), bevel=0)
    keel.box((4.2, 4.8, .5), loc=_P(0, -4.0, -2.2 + lift), bevel=.1, seg=1)
    dark = a.part('Hull_dark', 'Undercarriage')
    for f in (8.5, 5.5):
        dark.box((1.2, .7, .03), loc=_P(0, f, -2.72 + lift - .005), bevel=0)
    # Heat-sink fins along the keel housing's sides.
    fins = a.part('Keel_fins', 'Steel')
    for sx in (-1, 1):
        for f in (12.4, 11.6, 10.8, 3.6, 2.8):
            bw, w, zb = _lerp_table(KEEL, f)
            fins.box((.05, .5, .34), loc=_P(sx * (w + .01), f, zb + .3 + lift), bevel=0)
    # Plates on the upper flanks: raised off-white panels a few centimetres proud, some gone on the wreck.
    plates = a.part('Hull_plates', 'Armor' if wreck else PLATE_MAT, flat=True)
    lines = a.part('Panel_lines', 'Undercarriage')
    for sx in (-1, 1):
        f = 15.5
        while f > -12.2:
            length = min(rng.uniform(1.4, 2.6), f + 13.1)
            fc = f - length / 2
            hw, ze, rw, zt, _kw, _zb = _lerp_table(HULL, fc)
            _lo, hi, _d = _band(hw, ze)
            span = hw - rw
            ang = math.atan2(zt - hi, span)
            for u0, u1 in ((.08, .46), (.54, .9)):
                if rng.random() < .35:
                    continue
                u = (u0 + u1) / 2
                x = rw + span * u
                z = zt - (zt - hi) * u + lift
                w = span * (u1 - u0) / math.cos(ang)
                nx, nz = math.sin(ang), math.cos(ang)
                loc = (sx * (x + nx * .03), -fc, z + nz * .03)
                fa, fb = f, f - length
                ea, eb = _lerp_table(HULL, fa), _lerp_table(HULL, fb)
                xa, xb = ea[2] + (ea[0] - ea[2]) * u, eb[2] + (eb[0] - eb[2]) * u
                target = a.part('Plate_holes', 'Charred', flat=True) if (wreck and rng.random() < .25) else plates
                target.box((w, length - .12, .05), loc=loc, rot=(0, sx * ang, _yaw(sx, fa, fb, xa, xb)), bevel=0)
            # A panel line across the flank at the end of each plate run.
            xe = rw + span * .5
            ze2 = zt - (zt - hi) * .5 + lift
            lines.box((span / math.cos(ang) * .95, .05, .03), loc=(sx * xe, -(f - length), ze2 + .005),
                      rot=(0, sx * ang, 0), bevel=0)
            f -= length
    # Deck plates between the superstructure and the deck edge, forward of it on the bow.
    for f0, f1 in ((16.4, 14.6), (14.3, 13.0)):
        fc = (f0 + f1) / 2
        rw = _lerp_table(HULL, fc)[2]
        tilt = math.atan2(_top_z(f1, 0) - _top_z(f0, 0), f0 - f1)
        plates.box((rw * 1.5, f0 - f1 - .1, .05), loc=_P(0, fc, _top_z(fc, 0) + .02 + lift), rot=(tilt, 0, 0), bevel=0)
    # The trench: gunmetal lining, lit windows in two rows, boxes and pipes (the ship's scale).
    lining = a.part('Trench', DARK_MAT, flat=True)
    lamps = a.part('Trench_windows', 'Lamp')
    for sx in (-1, 1):
        for i in range(len(stations) - 3):
            f0, f1 = stations[i + 1], stations[i + 2]
            for k in range(3):
                fa = f0 + (f1 - f0) * k / 3
                fb = f0 + (f1 - f0) * (k + 1) / 3
                fc = (fa + fb) / 2
                hw, ze, _rw, _zt, _kw, _zb = _lerp_table(HULL, fc)
                lo, hi, d = _band(hw, ze)
                ea, eb = _lerp_table(HULL, fa), _lerp_table(HULL, fb)
                yaw = _yaw(sx, fa, fb, ea[0] - _band(*ea[:2])[2], eb[0] - _band(*eb[:2])[2])
                lining.box((.04, abs(fb - fa) / math.cos(yaw) - .1, hi - lo - .22),
                           loc=_P(sx * (hw - d + .01), fc, (lo + hi) / 2 + lift), rot=(0, 0, yaw), bevel=0)
                n = max(1, int(abs(fb - fa) / .55))
                for j in range(n):
                    fj = fa + (fb - fa) * (j + .5) / n
                    for zz in (ze - .07, ze + .12):
                        if rng.random() < (.65 if wreck else .2):
                            continue
                        hj = _lerp_table(HULL, fj)[0]
                        lamps.box((.04, .22, .07), loc=_P(sx * (hj - _band(hj, ze)[2] + .03), fj, zz + lift), rot=(0, 0, yaw),
                                  bevel=0)
            if i % 2 == 0:
                fc = (f0 + f1) / 2
                hw, ze, _rw, _zt, _kw, _zb = _lerp_table(HULL, fc)
                lo, hi, d = _band(hw, ze)
                hb = _lerp_table(HULL, fc + .8)[0]
                yb = _yaw(sx, fc + 1.2, fc + .4, _lerp_table(HULL, fc + 1.2)[0], _lerp_table(HULL, fc + .4)[0])
                lining.box((.16, .7, .18), loc=_P(sx * (hb - _band(hb, ze)[2] + .06), fc + .8, lo + .14 + lift),
                           rot=(0, 0, yb), bevel=.02, seg=1)
    # The side's colour: a short stripe along each bow flank, just above the trench.
    team = a.part('Bow_stripes', 'Charred' if wreck else 'Team', flat=True)
    for sx in (-1, 1):
        for f0, f1 in ((16.2, 13.2), (12.9, 10.4)):
            fc = (f0 + f1) / 2
            hw, ze, rw, zt, _kw, _zb = _lerp_table(HULL, fc)
            _lo, hi, _d = _band(hw, ze)
            u = .2
            ang = math.atan2(zt - hi, hw - rw)
            x = hw - (hw - rw) * u
            z = hi + (zt - hi) * u + lift
            ea, eb = _lerp_table(HULL, f0), _lerp_table(HULL, f1)
            yaw = _yaw(sx, f0, f1, ea[0] - (ea[0] - ea[2]) * u, eb[0] - (eb[0] - eb[2]) * u)
            team.box((.35, (f0 - f1) / math.cos(yaw), .04), loc=(sx * (x + math.sin(ang) * .045), -fc, z + math.cos(ang) * .045),
                     rot=(0, sx * ang, yaw), bevel=0)
    # Bow sensor glass on the prow's sides.
    glass = a.part('Bow_glass', 'Glass')
    for sx in (-1, 1):
        hw, ze, _rw, _zt, _kw, _zb = _lerp_table(HULL, 17.8)
        glass.box((.03, .9, .12), loc=_P(sx * (hw * .98), 17.8, ze + .15 + lift), rot=(0, 0, sx * -.4), bevel=0)
    if wreck:
        # The crack across the waist and scorch over the hull.
        crack = a.part('Crack', 'Charred', flat=True)
        for sx in (-1, 1):
            for k in range(7):
                x = sx * (k * .75 + .2)
                f = 1.4 + math.sin(k * 1.7) * .35
                crack.box((.8, .28, .1), loc=_P(x, f, _surface_z(f, x) - .02 + lift), rot=(0, sx * .2, math.sin(k) * .3),
                          bevel=0)
        scorch = a.part('Scorch', 'Charred', flat=True)
        for i in range(16):
            f = rng.uniform(-12.0, 16.0)
            x = rng.uniform(-1, 1) * _lerp_table(HULL, f)[0] * .7
            scorch.ico((rng.uniform(.4, .8), rng.uniform(.5, 1.0), .1), loc=_P(x, f, _surface_z(f, x) + lift), sub=1, jitter=.45,
                       seed=i * 2.3)


def _step_ring(f, tw, zt, spread, zb, lift):
    half = [(tw + spread, zb), (tw, zt)]
    return [_P(x, f, z + lift) for x, z in half] + [_P(-x, f, z + lift) for x, z in reversed(half)]


def _superstructure(a, lift, wreck):
    """The two steps on the deck (the front step's glacis with the side's chevron, windows in the steps' faces)."""
    body = a.part('Superstructure', HULL_MAT, flat=True)
    body.loft([_step_ring(f, tw, zt, .45, 1.2, lift) for f, tw, zt in STEP1], bevel=.04, seg=1)
    body.loft([_step_ring(f, tw, zt, .3, 2.8, lift) for f, tw, zt in STEP2], bevel=.03, seg=1)
    plates = a.part('Step_plates', 'Armor' if wreck else PLATE_MAT, flat=True)
    for f0, f1, w in ((9.8, 7.8, 1.5), (6.8, 3.6, 2.4), (-1.0, -5.0, .7), (-6.0, -9.6, .7)):
        fc = (f0 + f1) / 2
        tw = _lerp_table(STEP1, fc)[0]
        for sx in ((0,) if w > 1 else (-1, 1)):
            x = sx * (tw - w / 2 - .25)
            plates.box((w, f0 - f1, .05), loc=_P(x, fc, 3.0 + .02 + lift), bevel=0)
    lamps = a.part('Step_windows', 'Lamp')
    lines = a.part('Step_lines', 'Undercarriage')
    for sx in (-1, 1):
        # A window row along each side of the front step, a panel line along the upper step's.
        for k in range(14):
            f = 6.0 - k * 1.3
            if wreck and k % 3:
                continue
            tw = _lerp_table(STEP1, f)[0]
            lamps.box((.04, .5, .08), loc=_P(sx * (tw + .105), f, 2.62 + lift), rot=(0, sx * -.245, 0), bevel=0)
        lines.limb(_P(sx * (_lerp_table(STEP2, .5)[0] + .1), .5, 3.2 + lift),
                   _P(sx * (_lerp_table(STEP2, -12.3)[0] + .1), -12.3, 3.2 + lift), .03, .03, bevel=0)


def _greebles(a, lift, wreck, rng):
    """Small gear on the steps' tops at a small ship's scale: equipment blocks and vents along the front step's
    outboard strips, vents and comms masts on the upper step."""
    gear = a.part('Deck_gear', DARK_MAT, flat=True)
    bare = a.part('Deck_gear_steel', 'Steel')
    vents = a.part('Deck_vents', 'Undercarriage')
    for sx in (-1, 1):
        f = 1.6
        while f > -12.0:
            inner = _lerp_table(STEP2, f)[0] + .45
            outer = _lerp_table(STEP1, f)[0] - .25
            if outer - inner > .5:
                w, d, h = rng.uniform(.3, .7), rng.uniform(.4, 1.1), rng.uniform(.12, .38)
                x = rng.uniform(inner + w / 2, outer - w / 2)
                if rng.random() < .3:
                    vents.box((w, d, .03), loc=_P(sx * x, f, 3.0 + .01 + lift), bevel=0)
                elif rng.random() < .2:
                    bare.cyl(w * .35, h * 1.4, loc=_P(sx * x, f, 3.0 + h * .7 + lift), seg=8, bevel=0)
                else:
                    gear.box((w, d, h), loc=_P(sx * x, f, 3.0 + h / 2 - .01 + lift), bevel=.02, seg=1)
            f -= rng.uniform(.9, 1.6)
        vents.box((.8, 1.4, .03), loc=_P(sx * 1.1, -6.2, 3.4 + .01 + lift), bevel=0)
        vents.box((.6, 1.0, .03), loc=_P(sx * .9, .4, 3.4 + .01 + lift), bevel=0)
        if not wreck:
            bare.cyl(.05, 1.3, loc=_P(sx * 1.4, -1.4, 3.4 + .65 + lift), seg=6, bevel=0)


def _tower(a, lift, wreck):
    """The command tower aft: a raked neck up from the upper step, the hammerhead bridge with its lit window band,
    antennas and a sensor ball. On the wreck the neck is snapped and the bridge lies on the ground to port."""
    neck = a.part('Tower', HULL_MAT, flat=True)

    def ring(z, f0, f1, w):
        c = .3
        pts = [(w, f0 - c), (w, f1 + c), (w - c, f1), (-w + c, f1), (-w, f1 + c), (-w, f0 - c), (-w + c, f0), (w - c, f0)]
        return [_P(x, f, z + lift) for x, f in pts]
    top = 5.1 if wreck else 6.5
    if wreck:
        rings = [ring(3.3, -9.9, -12.75, 1.7), ring(4.2, -10.3, -12.85, 1.5), ring(top, -10.7, -12.95, 1.3)]
    else:
        rings = [ring(3.3, -9.9, -12.75, 1.7), ring(4.8, -10.5, -12.9, 1.35), ring(top, -11.1, -13.0, 1.0)]
    neck.loft(rings, bevel=.04, seg=1)
    if wreck:
        jag = a.part('Tower_break', 'Charred', flat=True)
        for k in range(5):
            jag.box((.7, .8, .5), loc=_P(-1.0 + k * .5, -11.8 + (k % 2) * .5, top + .1 + lift), rot=(.3 * (k % 2), .4, k * .5),
                    bevel=0)
        # The bridge lying on the ground off the port side, tipped over.
        _bridge(a, (-6.8, 18.2, .9), rot=(1.75, .12, .5), team=None, wreck=True)
        return
    _bridge(a, (0, 11.9, top - .05 + lift), rot=(0, 0, 0), team=a.part('Tower_cheeks', 'Team', flat=True), wreck=False)


def _bridge(a, loc, rot, team, wreck):
    """The hammerhead bridge centred at loc (its underside): a wide block with a raked, kinked front and a lit
    window band, sensor mast and a sensor ball on top."""
    body = a.part('Bridge' if not wreck else 'Bridge_fallen', 'Armor' if wreck else HULL_MAT, flat=True)
    # Side profile (y, z) relative to the block's centre bottom, front at -y.
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
    gear.cyl(.07, 1.4, loc=(x + .8, y + .3, z + 1.7), seg=6, bevel=0)
    gear.cyl(.05, .9, loc=(x - .5, y + .5, z + 1.45), seg=6, bevel=0)
    gear.box((.9, .05, .05), loc=(x + .8, y + .3, z + 2.15), bevel=0)
    a.part('Sensor_ball', 'Medical').sphere(.36, loc=(x - 1.6, y + .35, z + 1.1), seg=12, rings=7, cut=-.3)


def _pods(a, lift, wreck):
    """The flank pods, the coilgun barbettes at their fronts, the crash-turret pylons, bay mouths, bands, vents."""
    body = a.part('Flank_pods', HULL_MAT, flat=True)
    band = a.part('Pod_bands', 'Charred' if wreck else 'Team', flat=True)
    dark = a.part('Pod_dark', 'Undercarriage')
    lamp = a.part('Pod_lamps', 'Lamp')
    arm = a.part('Pod_barbettes', DARK_MAT)

    def ring(f, xc, w, zb, zt, sx, grow=0.0):
        h = zt - zb
        w += grow
        zb, zt = zb - grow, zt + grow
        pts = [(xc - w * .6, zb), (xc + w * .6, zb), (xc + w, zb + h * .28), (xc + w, zt - h * .22), (xc + w * .7, zt),
               (xc - w * .7, zt), (xc - w, zt - h * .22), (xc - w, zb + h * .28)]
        return [_P(sx * x, f, z + lift) for x, z in pts]
    for sx in (-1, 1):
        body.loft([ring(*row, sx) for row in POD], bevel=.04, seg=1)
        for f0 in (1.4, -4.4):
            rows = [[f0] + _lerp_table(POD, f0), [f0 - .5] + _lerp_table(POD, f0 - .5)]
            band.loft([ring(*r, sx, grow=.02) for r in rows], bevel=0)
        # The bay mouth in the pod's front face, a lamp strip over it.
        f, xc, w, zb, zt = POD[0]
        dark.box((w * 1.3, .03, (zt - zb) * .5), loc=_P(sx * xc, f + .03, (zb + zt) / 2 - .05 + lift), bevel=0)
        lamp.box((w * 1.1, .03, .06), loc=_P(sx * xc, f + .03, zt - .15 + lift), bevel=0)
        # Vents on the pod's top.
        for f in (-.6, -1.4, -3.4):
            xc = _lerp_table(POD, f)[0]
            dark.box((.8, .35, .03), loc=_P(sx * xc, f, 2.02 - .005 + lift + .01), bevel=0)
    for name in ('Mount_gun', 'Mount_gun.001'):
        x, y, z = orb._node(name, lift)
        arm.cyl(.62, .84, loc=(x, y, z - .68), seg=18, bevel=.03, bseg=1)    # 1.3 to 2.14 m, into the hull and pod
    for mount in ('Mount_gun.002', 'Mount_gun.003'):
        x, y, z = orb._node(mount, lift) if mount in orb.NODES else _crash_loc(mount, lift)
        arm.cyl(.58, .2, loc=(x, y, z - .1), seg=14, bevel=.02, bseg=1)


def _crash_loc(mount, lift):
    """The crash turrets' places (balance.json's crash_turret_l / _r: right -6.5 / 6.5, forward -6, up 2.2)."""
    right = -6.5 if mount.endswith('002') else 6.5
    return orb._pos(right, -6.0, 2.2 + lift)


def _engines(a, lift, wreck):
    """The engine bank on `Thruster_main`: an armoured block across the stern, the big drive bell in the middle and
    six round ion engines with glowing faces round it (one torn out on the wreck)."""
    right, forward, up = orb.NODES['Thruster_main']
    t = a.pivot('Thruster_main', orb._pos(right, forward, up + lift))
    block = a.part('Engine_block', DARK_MAT, t, flat=True)
    block.box((9.0, 2.4, 3.6), loc=(0, -1.75, .15), bevel=.14, seg=1, taper=(.92, .9))
    a.part('Engine_block_plates', 'Charred' if wreck else PLATE_MAT, t, flat=True).box((6.0, 1.6, .05), loc=(0, -1.85, 1.96),
                                                                                    bevel=0)
    shell = a.part('Engine_shrouds', 'Charred' if wreck else 'Steel', t)
    glow = a.part('Engine_glow', 'Charred' if wreck else 'TeamGlow', t)
    bands = a.part('Engine_bands', DARK_MAT, t)
    dark = a.part('Engine_dark', 'Undercarriage', t)
    # The drive bell.
    shell.lathe([(1.0, 0), (.9, .4), (1.05, 1.0), (1.35, 1.7), (1.5, 2.1), (1.46, 2.14), (1.3, 1.7), (1.0, 1.0), (.85, .4),
                 (.9, .02)], loc=(0, -.75, 0), rot=BACKWARD, seg=24)
    bands.cyl(1.12, .3, loc=(0, -.45, 0), rot=ALONG_Y, seg=24, bevel=.02, bseg=1)
    glow.cyl(.84, .04, loc=(0, -.28, 0), rot=ALONG_Y, seg=20, bevel=0)
    for i, (x, z, r) in enumerate(((2.05, .85, .76), (2.05, -.85, .76), (3.6, 0, .66),
                                   (-2.05, .85, .76), (-2.05, -.85, .76), (-3.6, 0, .66))):
        if wreck and i == 4:
            dark.cyl(r * .9, .06, loc=(x, -.53, z), rot=ALONG_Y, seg=12, bevel=0)
            continue
        shell.lathe([(r, 0), (r, 1.3), (r * .86, 1.3), (r * .86, 1.0), (0, 1.0)], loc=(x, -.75, z), rot=BACKWARD, seg=18)
        bands.cyl(r + .05, .22, loc=(x, -.25, z), rot=ALONG_Y, seg=18, bevel=.02, bseg=1)
        glow.cyl(r * .84, .03, loc=(x, .28, z), rot=ALONG_Y, seg=16, bevel=0)
    if wreck:
        chunks = a.part('Engine_debris', 'Rust', t, flat=True)
        rng = random.Random(909)
        for i in range(6):
            chunks.ico((.35, .3, .22), loc=(rng.uniform(-3.5, 3.5), rng.uniform(-.2, 1.2), rng.uniform(-1.2, 1.2)), sub=1,
                       jitter=.4, seed=i * 2.1)


def _rcs_block(a, name, lift, wreck):
    """A forward RCS block on its node, off the bow on a stubby swept arm (the arm fixed to the hull)."""
    right, forward, up = orb.NODES[name]
    sx = 1 if right < 0 else -1                    # right < 0 is Blender +X
    p = a.pivot(name, orb._pos(right, forward, up + lift))
    a.part('Rcs_block', HULL_MAT, p, flat=True).box((.95, 1.9, .8), loc=(0, 0, 0), bevel=.1, seg=1, taper=(.8, .85))
    a.part('Rcs_block_cap', DARK_MAT, p, flat=True).box((.8, .5, .7), loc=(0, -1.0, -.02), bevel=.08, seg=1, taper=(.7, .8))
    nozzles = a.part('Rcs_nozzles', 'Steel', p)
    glow = a.part('Rcs_glow', 'Charred' if wreck else 'TeamGlow', p)
    for dy in (-.45, .45):
        nozzles.cyl(.11, .2, r2=.16, loc=(sx * .5, dy, 0), rot=(0, sx * R90, 0), seg=8, bevel=0)
        glow.cyl(.1, .02, loc=(sx * .62, dy, 0), rot=(0, R90, 0), seg=8, bevel=0)
    nozzles.cyl(.13, .22, r2=.18, loc=(0, 1.02, 0), rot=BACKWARD, seg=8, bevel=0)
    glow.cyl(.12, .02, loc=(0, 1.15, 0), rot=ALONG_Y, seg=8, bevel=0)
    # The arm from the hull's trench to the block (static: it stays when the block is shot off).
    x, y, z = orb._pos(right, forward, up + lift)
    hw = _lerp_table(HULL, forward)[0]
    arm = a.part('Rcs_arms', HULL_MAT, flat=True)
    _slab(arm, lambda s, yy, n: (sx * s, yy, z - .05 + n), [(hw - .3, y - 1.1, 2.6, .34), (abs(x) - .2, y - .5, 1.4, .26)],
          apex=.4)


def _nacelle(a, name, lift, wreck, rng):
    """A stern engine nacelle on its node, on a pylon from the hull, with an outward-canted fin (torn off on the
    wreck's port nacelle, lying on the ground)."""
    right, forward, up = orb.NODES[name]
    sx = 1 if right < 0 else -1
    p = a.pivot(name, orb._pos(right, forward, up + lift))
    body = a.part('Nacelle', HULL_MAT, p, flat=True)
    body.lathe([(.3, 0), (.5, .12), (.68, .55), (.74, 1.3), (.74, 3.2), (.66, 3.55), (.001, 3.56)], loc=(0, -2.2, 0),
               rot=BACKWARD, seg=12)
    a.part('Nacelle_intake', 'Undercarriage', p).cyl(.28, .03, loc=(0, -2.215, 0), rot=ALONG_Y, seg=10, bevel=0)
    a.part('Nacelle_nozzle', 'Steel', p).lathe([(.6, 0), (.62, .6), (.54, .6), (.54, .35), (0, .35)], loc=(0, 1.25, 0),
                                               rot=BACKWARD, seg=12)
    a.part('Nacelle_glow', 'Charred' if wreck else 'TeamGlow', p).cyl(.5, .02, loc=(0, 1.62, 0), rot=ALONG_Y, seg=12,
                                                                        bevel=0)
    a.part('Nacelle_band', 'Charred' if wreck else 'Team', p).cyl(.77, .3, loc=(0, -.9, 0), rot=ALONG_Y, seg=12, bevel=.02,
                                                                   bseg=1)
    x = orb._pos(right, forward)[0]
    hw = _lerp_table(HULL, forward)[0]
    a.part('Nacelle_pylon', DARK_MAT, p, flat=True).box((abs(x) - hw + .9, 2.4, .34), loc=(-sx * (abs(x) - hw + .9) / 2 + sx * .45,
                                                                                        -.3, 0), bevel=.04, seg=1)
    cant = math.radians(35)

    def fin(s, y, n):
        return (sx * (math.sin(cant) * s + math.cos(cant) * n), y, .6 + math.cos(cant) * s - math.sin(cant) * n)
    stations = [(0, -1.1, 2.6, .16), (1.9, .6, 1.1, .06)]
    if wreck and sx > 0:
        # Torn off, lying on the ground beside the nacelle.
        wx, wy, _wz = orb._pos(right, forward)
        _slab(a.part('Fin_fallen', 'Charred', flat=True), lambda s, y, n: (wx + 1.9 + s * .9, wy + y + 1.5, .12 + n * 1.5 + s * .15),
              stations)
        return
    _slab(a.part('Nacelle_fin', 'Charred' if wreck else 'Team', p, flat=True), fin, stations)


def _plinth(a, name, lift, below, width=.3):
    """A short column under a mount, from `below` up to just under the mount's own base."""
    x, y, z = orb._node(name, lift)
    top = z - .01
    if top - below > .02:
        a.part('Plinths', DARK_MAT).cyl(width, top - below, loc=(x, y, (top + below) / 2), seg=12, bevel=.02, bseg=1)


def _ship(a, lift, wreck):
    _suffixed(a)
    rng = random.Random(2309)
    _hull(a, lift, wreck, rng)
    _superstructure(a, lift, wreck)
    _greebles(a, lift, wreck, rng)
    _tower(a, lift, wreck)
    _pods(a, lift, wreck)
    _engines(a, lift, wreck)
    for name in ('Thruster_fl', 'Thruster_fr'):
        _rcs_block(a, name, lift, wreck)
    for name in ('Thruster_rl', 'Thruster_rr'):
        _nacelle(a, name, lift, wreck, rng)
    orb._build_main_turret(a, orb._node('Turret', lift))
    orb._build_coilgun(a, 'Mount_gun', 'Muzzle_gun', '', orb._node('Mount_gun', lift), deployed=wreck)
    orb._build_coilgun(a, 'Mount_gun.001', 'Muzzle_gun.001', '_001', orb._node('Mount_gun.001', lift), deployed=wreck)
    orb._build_flak(a, 'Mount_mg', 'Muzzle_mg', '', orb._node('Mount_mg', lift), deployed=wreck)
    orb._build_flak(a, 'Mount_mg.001', 'Muzzle_mg.001', '_001', orb._node('Mount_mg.001', lift), deployed=wreck)
    orb._build_pd_laser(a, 'Pd_laser_l', orb._node('Pd_laser_l', lift))
    orb._build_pd_laser(a, 'Pd_laser_r', orb._node('Pd_laser_r', lift))
    orb._build_pod_bay(a, orb._node('Pod_bay', lift))
    orb._build_uplink(a, orb._node('Uplink', lift))
    # Tubs under the point-defence lasers (on the front step's shoulders), a mast under the uplink.
    for name in ('Pd_laser_l', 'Pd_laser_r'):
        _plinth(a, name, lift, 3.0 + lift - .03, width=.34)
    ux, uy, uz = orb._node('Uplink', lift)
    b, t = 3.4 + lift - .03, uz - .58
    a.part('Plinths', DARK_MAT).cyl(.3, t - b, loc=(ux, uy, (t + b) / 2), seg=10, bevel=.02, bseg=1)
    for mount, loc in (('Mount_gun.002', _crash_loc('Mount_gun.002', lift)), ('Mount_gun.003', _crash_loc('Mount_gun.003', lift))):
        autocannon(a, mount, loc, length=2.4, size=(1.3, 1.5, .62))
    if wreck:
        orb._crater_ring(a)
        for i, (right, forward, w, d) in enumerate(orb.DEBRIS):
            x, y, _z = orb._pos(right, forward)
            orb._debris_pile(a, x, y, w, d, 1.8, seed=400 + i)


def silver_bug(a):
    """Icarus, the orbital warship: see the module docstring."""
    _ship(a, 0.0, False)


def silver_bug_wreck(a):
    """Icarus crashed, for its ground phase: see the module docstring."""
    _ship(a, orb.LIFT, True)


# ============================================================================= stealth jet
# The chined fuselage, nose to tail: (y, belly half-width, belly z, chine half-width, chine z, spine half-width,
# spine z), as mb_p17_temp's _hex. 3.1 m across the chines at most, 0.55 m deep.
SJ = [(-8.8, .08, -.17, .24, -.1, .05, -.02),
      (-7.6, .18, -.25, .5, -.12, .12, .08),
      (-6.2, .28, -.3, .74, -.13, .18, .16),
      (-4.6, .4, -.32, 1.0, -.13, .25, .2),
      (-3.0, .58, -.33, 1.42, -.12, .38, .22),
      (-1.0, .72, -.33, 1.62, -.11, .52, .22),
      (2.0, .8, -.32, 1.62, -.1, .6, .21),
      (4.6, .78, -.28, 1.48, -.08, .6, .19),
      (6.6, .72, -.24, 1.3, -.07, .54, .16),
      (7.8, .64, -.2, 1.1, -.06, .48, .13)]
SJ_NOSE = -9.6
# Lifting surfaces: (span from the centreline, leading edge y, chord, thickness).
SJ_WING = [(1.35, -2.8, 6.9, .13), (6.6, 1.95, 1.25, .035)]
SJ_STAB = [(1.0, 4.3, 3.0, .08), (3.7, 6.35, 1.05, .03)]
SJ_FIN = [(0, 3.5, 3.1, .09), (2.35, 5.45, 1.25, .03)]
SJ_CANT = math.radians(27)


def _sj_belly(y):
    return _hex_at(SJ, y)[1]


def _sj_top(y, x):
    return _hex_top(SJ, y, x)


def _wing_z(s):
    return -.1 - (s - 1.35) * .05          # 3 degrees of anhedral


def _sj_line(part, pts, lift=.012, r=.011, step=.3):
    """A panel line over the upper skin through [(x, y)...], subdivided so it follows the facets."""
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            path.append((x, y, _sj_top(y, x) + lift))
    path.append((pts[-1][0], pts[-1][1], _sj_top(pts[-1][1], pts[-1][0]) + lift))
    part.tube(path, r, seg=4)


def _saw(x0, x1, y, teeth, depth):
    return [(x0 + (x1 - x0) * k / (teeth * 2), y + (depth if k % 2 else 0.0)) for k in range(teeth * 2 + 1)]


def stealth_fighter(a):
    """The slim fifth-generation stealth jet: see the module docstring."""
    body = a.part('Fuselage', 'Armor', flat=True)
    skin = a.part('Wings', 'Team', flat=True)
    dark = a.part('Undercarriage', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Wing_lights', 'TeamGlow')
    edges = a.part('Detail_edges', 'Armor', flat=True)
    lines = a.part('Panel_lines', 'Undercarriage')
    glass = a.part('Detail_glass', 'Glass')
    body.loft([[(0, SJ_NOSE, -.1)]] + [_hex(*r) for r in SJ], bevel=0)
    for sg in (-1, 1):
        _slab(skin, lambda s, y, n, sg=sg: (sg * s, y, _wing_z(s) + n), SJ_WING)                    # trapezoid wing
        _slab(skin, lambda s, y, n, sg=sg: (sg * s, y, -.09 + n), SJ_STAB)                          # all-moving tailplanes
        x0 = sg * 1.05
        z0 = _sj_top(4.6, 1.05) + .02
        dx, dz = sg * math.sin(SJ_CANT), math.cos(SJ_CANT)
        nx, nz = sg * math.cos(SJ_CANT), -math.sin(SJ_CANT)
        fin = (lambda s, y, n, x0=x0, z0=z0, dx=dx, dz=dz, nx=nx, nz=nz: (x0 + dx * s + nx * n, y, z0 + dz * s + nz * n))
        _slab(skin, fin, SJ_FIN)                                                                  # twin tails, canted
        tip = SJ_WING[-1]
        glow.box((.05, .3, .03), loc=(sg * (tip[0] - .02), tip[1] + .35, _wing_z(tip[0])), bevel=0)  # wingtip lights
        glow.box((.04, .2, .04), loc=fin(SJ_FIN[-1][0] + .01, SJ_FIN[-1][1] + .8, 0), bevel=0)
    # One-piece frameless canopy on the spine, a thin frame round its base and a seat and HUD inside.
    st = [(-7.3, .08, .2), (-6.7, .3, .42), (-5.8, .37, .54), (-5.0, .34, .52), (-4.3, .22, .42), (-3.8, .08, .3)]
    a.part('Canopy', 'Glass').loft([_dome(y, w, _sj_top(y, w) - .05, z1, n=7) for y, w, z1 in st], bevel=0)
    for sg in (-1, 1):
        a.part('Canopy_frames', 'Armor').tube([(sg * w, y, _sj_top(y, w) + .02) for y, w, _z in st], .025, seg=5)
    a.part('Seat', 'Rubber').box((.3, .28, .36), loc=(0, -5.3, _sj_top(-5.3, 0) + .18), rot=(.25, 0, 0), bevel=.03, seg=1)
    glass.box((.14, .02, .1), loc=(0, -6.3, _sj_top(-6.3, 0) + .26), rot=(-.5, 0, 0), bevel=0)
    a.part('Sensor', 'Glass', flat=True).box((.18, .3, .08), loc=(0, -7.9, _sj_belly(-7.9) - .02), bevel=0, taper=(.7, .7))
    # Caret intakes under the chines: a raked mouth (the top edge forward), a lip round it and a dark face.
    for sg in (-1, 1):
        def rect(y, x0, x1, z0, z1, rake=0.0, sg=sg):
            return [(sg * x0, y + rake * .5, z0), (sg * x1, y + rake, z0), (sg * x1, y, z1), (sg * x0, y - rake * .5, z1)]
        mouth = rect(-4.35, .42, 1.2, -.36, -.12, rake=.3)
        body.loft([mouth, rect(-2.6, .5, 1.44, -.36, -.1), rect(-.6, .6, 1.52, -.34, -.1)], bevel=0)
        face = [(x, y - .015, z) for x, y, z in mouth]
        dark.mesh(face, [(0, 1, 2, 3)])
        dark.mesh(face, [(3, 2, 1, 0)])
        edges.tube(mouth + [mouth[0]], .022, seg=4)
        dark.box((.6, .4, .16), loc=(sg * .8, -4.05, -.24), bevel=0)                              # the duct
    # Twin 2D thrust-vectoring nozzles, a flat tail between them.
    noz = a.part('Nozzles', 'Steel', flat=True)
    for sg in (-1, 1):
        x = sg * .55

        def box_ring(y, w, h, x=x):
            return [(x - w, y, -.08 - h), (x + w, y, -.08 - h), (x + w, y, -.08 + h), (x - w, y, -.08 + h)]
        noz.loft([box_ring(7.2, .42, .24), box_ring(8.0, .41, .22), box_ring(8.6, .37, .15)], bevel=0)
        dark.box((.62, .02, .22), loc=(x, 8.61, -.08), bevel=0)
        a.part('Exhaust_glow', 'TeamGlow').box((.5, .02, .1), loc=(x, 8.62, -.08), bevel=0)
    body.box((.34, 1.2, .07), loc=(0, 8.1, -.1), bevel=0, taper=(.6, 1))
    # Main bays in tandem between the engines: dark liners, a keel between them, doors hanging open at the outer
    # edges, one missile each on an extended trapeze. Muzzle_missile between the two noses.
    doors = a.part('Bay_doors', 'Armor', flat=True)
    zb = _sj_belly(-1.2)
    zm = zb - .38
    for sg in (-1, 1):
        x = sg * .35
        dark.box((.52, 3.6, .02), loc=(x, -1.2, zb), bevel=0)
        doors.box((.03, 3.4, .45), loc=(sg * .66, -1.2, zb - .225), bevel=0)
        for dy in (-.6, .6):
            steel.limb((x, -1.2 + dy, zb + .02), (x, -1.2 + dy, zm + .08), .05, .05, bevel=0)
    body.box((.1, 3.6, .1), loc=(0, -1.2, zb - .03), bevel=0)
    aams = _aam_parts(a)
    for sg in (-1, 1):
        _aam(aams, (sg * .35, -1.2, zm), length=3.0, r=.085, canards=False, fin=1.7)
    a.pivot('Muzzle_missile', (0, -2.7, zm))
    # The centre bay behind them: a guided bomb on a rack between two open doors; Muzzle_bomb at its nose.
    zc = _sj_belly(2.1)
    dark.box((.7, 2.4, .02), loc=(0, 2.1, zc), bevel=0)
    for sg in (-1, 1):
        doors.box((.03, 2.2, .4), loc=(sg * .38, 2.1, zc - .2), bevel=0)
    steel.limb((0, 2.1, zc + .02), (0, 2.1, zc - .14), .06, .06, bevel=0)
    _bay_bomb(a.part('Bay_stores', 'Armor'), (0, 2.1, zc - .25))
    a.pivot('Muzzle_bomb', (0, 2.1 - .9 - .01, zc - .25))
    # The cannon on the left shoulder (+X, the pilot's left): fairing, barrel and muzzle ring.
    gx, gy = 1.0, -3.7
    gz = _sj_top(gy, gx) + .08
    body.box((.22, 1.1, .16), loc=(gx, -3.2, _sj_top(-3.2, gx) + .02), bevel=0, taper=(.6, .9))
    steel.cyl(.04, .55, loc=(gx, gy - .1, gz), rot=FORWARD, seg=8, bevel=0)
    steel.cyl(.055, .08, loc=(gx, gy - .36, gz), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (gx, gy - .41, gz))
    a.part('Beacon', 'TeamGlow').sphere(.04, loc=(0, 8.72, -.08), seg=8, rings=5)
    # Surface detail: a spine panel with a sawtooth access door, the refuelling door, blade antennas, sawtooth panel
    # lines at the nose join and round the bays, hinge lines on the wings and tailplanes.
    _sj_line(lines, _saw(-.4, .4, -1.2, 3, .2) + [(.4, .9)] + list(reversed(_saw(-.4, .4, .9, 3, -.2))) + [(-.4, -1.2)])
    dark.box((.3, .45, .02), loc=(0, -2.7, _sj_top(-2.7, 0) + .005), bevel=0)                       # refuelling door
    for y, up in ((-1.8, 1), (3.2, 1), (-.4, -1)):
        zz = (_sj_top(y, 0) + .07) if up > 0 else _sj_belly(y) - .07
        a.part('Antennas', 'Armor').box((.02, .3, .12), loc=(0, y, zz), rot=(-.3 * up, 0, 0), bevel=0, taper=(1, .45))
    _sj_line(lines, _saw(-.62, .62, -6.9, 3, .22))
    _sj_line(lines, _saw(-1.3, 1.3, -3.1, 5, .25))
    _sj_line(lines, _saw(-1.2, 1.2, 5.4, 4, -.25))
    for sg in (-1, 1):
        _sj_line(lines, [(sg * .22, -8.6), (sg * .4, -7.0), (sg * .55, -5.2), (sg * .66, -3.4), (sg * .7, 4.8)])
        glass.box((.02, .2, .09), loc=(sg * .6, -6.3, _sj_top(-6.3, .6) - .02), rot=(0, 0, sg * -.3), bevel=0)  # EODAS
        s0, s1 = 2.6, 6.0
        for u in (.8,):
            pts = []
            for s in (s0, (s0 + s1) / 2, s1):
                k = (s - SJ_WING[0][0]) / (SJ_WING[1][0] - SJ_WING[0][0])
                le = SJ_WING[0][1] + (SJ_WING[1][1] - SJ_WING[0][1]) * k
                c = SJ_WING[0][2] + (SJ_WING[1][2] - SJ_WING[0][2]) * k
                t = SJ_WING[0][3] + (SJ_WING[1][3] - SJ_WING[0][3]) * k
                pts.append((sg * s, le + c * u, _wing_z(s) + t / 2 * (1 - u) / .58 + .008))
            lines.tube(pts, .011, seg=4)
    for (x, y, w, l) in ((.35, -1.2, .56, 3.7), (-.35, -1.2, .56, 3.7), (0, 2.1, .74, 2.5)):
        zz = _sj_belly(y) - .012
        for dy in (-l / 2, l / 2):
            lines.box((w, .03, .02), loc=(x, y + dy, zz), bevel=0)


# name: (builder, Asset options).
BUILDERS = {
    'silver_bug': (silver_bug, dict(ao_distance=.6, ground=False)),
    'silver_bug_wreck': (silver_bug_wreck, dict(ao_distance=1.1, grime_height=1.2)),
    'stealth_fighter': (stealth_fighter, dict(ao_distance=.7, ground=False)),
}
