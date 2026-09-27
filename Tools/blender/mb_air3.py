"""Machine Brigade third air wing and two more bosses, built with frontier_kit and the aircraft kits of
mb_air.py / mb_air2.py (airfoil lofts, control surfaces, skin panels, intakes, nozzles, turbofans,
propellers, rotors, rocket pods and missiles) and the railway kit of mb_bosses.py.

Conventions as in mb_air.py and mb_bosses.py: metres, +Z up, Blender -Y is the nose / front. Team /
TeamGlow parts are recoloured per army at runtime. Touching parts overlap or stand at least 1 cm
apart, so no two visible faces are coplanar.
  * fighter_jet: air-superiority fighter (Su-27 / F-15 lineage), origin at the fuselage centre (it
    flies). `Muzzle_gun` at the cannon in the right wing root; `Muzzle_missile` between the four
    air-to-air missiles on the wing pylons' shoulder rails.
  * tank_buster: ground-attack jet (A-10 lineage), origin at the fuselage centre. `Muzzle_gun` at the
    seven-barrel nose gatling, `Muzzle_rocket` between the rocket pods, `Muzzle_missile` between the
    triple Maverick-style launchers.
  * recon_drone: MALE reconnaissance drone (TB2 lineage), origin at the fuselage centre. Twin tail
    booms carry an inverted V-tail; the two-blade pusher `Propeller` spins about local Y;
    `Muzzle_missile` between the two small underwing missiles.
  * heavy_attack_heli: heavy assault gunship (Mi-24 / Mi-35 lineage), origin on the ground under the
    cabin (wheels on z = 0). `Rotor` (five blades, spins about Z), `Tail_rotor` (X-shaped, left side,
    spins about X), a twin-barrel chin turret on `Mount_gun` with `Muzzle_gun`, `Muzzle_rocket`
    between the four rocket pods and `Muzzle_missile` between the wingtip missile launchers.
  * drone_mothership (boss): armoured airship that launches FPV drones, origin at the envelope
    centre (it flies). Ducted `Propeller` (front left, +X), `Propeller_2` (front right), `Propeller_3`
    (rear left), `Propeller_4` (rear right) spin about local Y. Twin autocannon `Turret` under the
    nose (Main_cannon / Main_cannon_2 recoil, `Muzzle_main` between the tips), a flak gun on the
    back on `Mount_mg` with `Muzzle_mg`, and `Muzzle_missile` at the drone bay under the hull.
  * nuke_train (boss): armoured locomotive coupled to a missile wagon as one rigid model on 1.435 m
    gauge wheelsets (origin on the ground at the footprint centre). A twin flak `Turret` on the
    locomotive roof (`Muzzle_main`), an MG cupola on `Mount_mg` (`Muzzle_mg`), and the `Erector`
    pivot at the wagon's rear hinge: it rotates about local X, rests lowered (missile horizontal,
    nose to the front), and -90 degrees about X stands the missile nose-up. The missile sits under
    `Icbm_payload` (child of `Erector`, at the missile's centre) so the game can hide it and launch the
    `icbm` projectile from there. frontier_kit treats Erector like the other moving pivots (no baked
    shadow on the wagon).
  * icbm: the same missile as a projectile (nose at -Y, origin at its centre).
"""
import math

from mathutils import Vector

from mb_air import (ACROSS, BACKWARD, FORWARD, LEFT, R90, RIGHT, Planform, _aam, _aam_parts, _blade, _bubble,
                    _canopy, _dome, _exhaust_duct, _hoop, _intake, _nozzle, _octagon, _patch, _prop_blade, _pylon,
                    _revolve, _ring_at, _rocket_pod, _rotor_head, _sec, _skin_panel, _skin_z, _surface, _trap_fin,
                    _upright, _wing)
from mb_bosses import _bogie, _headlamp, _plate_bolts, _sec6, _underframe
from mb_town import fbox
from mb_vehicles import _antenna, _dish, _flank, _frame, _glacis
from mb_vehicles2 import _gun


def _sq(x, y, zc, w, h, p=4.0, n=12):
    """Superellipse ring at y (x across, z up) with exponent p (2 = ellipse, 4 = squircle), starting
    at +x and running counter-clockwise, in the point order of mb_air's _duct rings."""
    pts = []
    for i in range(n):
        u = i * math.tau / n
        c, s = math.cos(u), math.sin(u)
        pts.append((x + w * math.copysign(abs(c) ** (2 / p), c), y, zc + h * math.copysign(abs(s) ** (2 / p), s)))
    return pts


# ----------------------------------------------------------------------------- fighter jet
def fighter_jet(a):
    """Air-superiority fighter (Su-27 / F-15 lineage), 13 x 19 m: a long radome nose with a pitot boom
    and an IRST ball, a bubble canopy far forward on a dorsal spine with an air brake, leading-edge
    root extensions blending into a 42-degree wing with flaperons and ailerons, a broad lifting
    body over two widely spaced engine nacelles with raked intakes, tail booms carrying twin fins with
    rudders, all-moving stabilisers and canted ventral fins, afterburning nozzles either side of a
    tail stinger. The cannon sits in the right wing root; four air-to-air missiles hang on the wing
    pylons' shoulder rails and one more on each wingtip rail."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=16, pt=2.4, pb=2.8)
    # Forward fuselage, then the flat lifting body over the engines, tapering to the nozzles.
    hull = [sec(-7.6, .43, -.42, .38), sec(-6.6, .53, -.5, .5), sec(-5.4, .6, -.54, .56), sec(-4.2, .66, -.56, .58),
            sec(-3.0, .76, -.55, .55), sec(-1.8, 1.12, -.5, .5), sec(-.4, 1.58, -.45, .46), sec(1.5, 1.8, -.42, .44),
            sec(4.0, 1.95, -.36, .38), sec(6.0, 1.85, -.28, .32), sec(7.2, 1.15, -.2, .24)]
    body.loft(hull, bevel=.02, seg=1)
    # Dark radome; its back ring sits inside the fuselage, whose front face shows as a seam.
    armor.loft([[(0, -9.3, -.03)], sec(-9.0, .155, -.16, .1), sec(-8.4, .3, -.3, .24), sec(-7.55, .425, -.415, .372)])
    steel.cyl(.022, .5, loc=(0, -9.5, -.03), rot=FORWARD, seg=6, bevel=0)                  # pitot boom
    steel.cyl(.035, .08, loc=(0, -9.32, -.03), rot=FORWARD, seg=6, bevel=0)
    _patch(armor, hull, -7.45, -6.95, 6, 10)                                                # anti-glare panel
    zi = _skin_z(hull, -7.15, -.17)
    armor.cyl(.07, .1, loc=(-.17, -7.15, zi), seg=10, bevel=0)                             # IRST ball (right)
    a.part('Sensor', 'Glass').sphere(.085, loc=(-.17, -7.17, zi + .06), seg=10, rings=6)
    # Bubble canopy far forward, a dorsal spine behind it with the air brake.
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    st = [(-6.95, .14, .64), (-6.55, .34, .88), (-6.0, .43, 1.02), (-5.3, .45, 1.07), (-4.6, .4, 1.0), (-4.1, .27, .87),
          (-3.75, .13, .72)]
    _canopy(glass, frames, [(y, w, _skin_z(hull, y, w) - .03, z1) for y, w, z1 in st], bows=(-6.5,))
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in
             ((-4.3, .34, .92), (-3.2, .42, .8), (-1.4, .46, .68), (1.2, .46, .62), (3.8, .4, .56), (6.2, .3, .44))]
    body.loft(spine + [[(0, 7.3, .3)]], bevel=.02, seg=1)
    _patch(armor, spine, -3.0, -1.7, 2, 6)                                                  # air brake
    for y, t in ((-.4, -.35), (4.6, -.35)):                                                  # blade aerials
        steel.box((.02, .22, .16), loc=(0, y, _skin_z(spine, y, 0) + .05), rot=(t, 0, 0), bevel=0, taper=(1, .5))
    steel.box((.02, .22, .16), loc=(0, -4.6, -.6), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    # Leading-edge root extensions from the cockpit sides into the wing.
    lerx = Planform(.45, 2.6, -6.4, -.52, 6.9, 2.0, .14, .08, .06, .04)
    for frame in (RIGHT, LEFT):
        _surface(body, lerx, frame, bevel=.01)
    # 42-degree wing: flaperons inboard, ailerons outboard, fuel-bay panels.
    wing = Planform(.9, 6.1, -2.17, 2.51, 5.4, 1.45, .3, .1, .02, -.08)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(1.95, 3.9, .75), (3.9, 5.75, .74)])
        _skin_panel(panels, wing, frame, 2.3, 3.6, .2, .55)
        _skin_panel(panels, wing, frame, 4.1, 5.4, .22, .56)
    for i0, i1 in ((5, 7), (9, 11)):                                                        # engine bay doors
        _patch(panels, hull, 1.4, 3.9, i0, i1, out=.018, inn=.012, bevel=.005)
    # Engine nacelles under the lifting body: raked intakes under the root extensions, splitter plates.
    lips = a.part('Intake_lips', 'Team')
    for s in (-1, 1):
        x = s * 1.12
        trunk = [_sq(x, -2.6, -.6, .31, .41, n=10), _sq(x, .5, -.62, .33, .42, p=3.5, n=10),
                 _sq(x, 4.5, -.6, .36, .42, p=3, n=10), _sq(x, 6.6, -.55, .43, .43, p=2.4, n=10),
                 _sq(x, 7.3, -.52, .45, .45, p=2.2, n=10)]
        _intake(a, body, lips, dark, (x, -3.4, -.58), .3, .4, .25, trunk, depth=.3, wall=.05, n=10)
        armor.box((.03, 1.0, .5), loc=(s * .8, -3.2, -.42), bevel=0)                          # splitter
        glow.box((.02, .5, .04), loc=(s * 1.465, -1.0, -.62), bevel=0)                        # formation lights
        _nozzle(a, x, 7.3, -.52, .42, 1.05, seg=14)
    # Tail booms beside the nacelles: fins with rudders on top, stabilisers and ventral fins.
    fin = Planform(0, 3.0, 4.3, 6.75, 2.9, 1.05, .13, .05)
    stab = Planform(1.95, 5.0, 6.3, 7.9, 2.1, .95, .12, .05, -.03)
    ventral = Planform(0, .75, 5.5, 6.1, 1.2, .6, .07, .03)
    for s in (-1, 1):
        x = s * 1.95
        boom = [_sec(y, w, zb, zt, n=10) for y, w, zb, zt in
                ((2.8, .12, -.12, .1), (3.6, .22, -.25, .2), (7.4, .22, -.25, .2), (8.4, .16, -.16, .12))]
        body.loft([[(x, 2.2, -.02)]] + [[(x + p[0], p[1], p[2]) for p in r] for r in boom] + [[(x, 8.9, -.02)]],
                  bevel=.01, seg=1)
        frame = _upright(x, .14, .06)
        _wing(body, moving, fin, frame, cs=[(.35, 2.75, .68)], lower=1.0)
        tip = Vector(frame(3.0, 6.9, 0))
        armor.cyl(.05, .6, loc=tuple(tip + Vector((0, .1, 0))), rot=BACKWARD, seg=8, bevel=.015, bseg=1)
        glow.box((.04, .1, .05), loc=tuple(tip + Vector((0, .42, 0))), bevel=0)
        glow.box((.02, .6, .04), loc=tuple(Vector(frame(1.5, 5.4, .06))), rot=(0, -s * .06, 0), bevel=0)
        _surface(body, ventral, _upright(x, -.2, math.pi - .3), lower=1.0)
        a.part('Flares', 'Undercarriage').grille(.18, .5, loc=(x, 7.9, .19), rot=(-R90, 0, 0), slats=3, depth=.04,
                                                 thickness=.025)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame)
        _skin_panel(panels, stab, frame, 2.4, 4.4, .2, .6, out=.012, inn=.01)
    # Tail stinger between the nozzles (brake-chute housing) with the tail beacon.
    body.loft([sec(6.5, .45, -.22, .3), sec(8.0, .28, -.14, .2), sec(8.9, .15, -.08, .1), [(0, 9.4, .0)]], bevel=.01,
              seg=1)
    armor.loft([sec(8.3, .235, -.12, .17), sec(8.55, .2, -.1, .145)], bevel=0)             # chute band
    a.part('Beacon', 'TeamGlow').sphere(.045, loc=(0, 9.39, 0), seg=8, rings=5)
    # Cannon in the right wing root (the pilot's right is -X): fairing, barrel and muzzle ring.
    armor.box((.2, 1.3, .14), loc=(-.86, -3.05, .15), bevel=.03, seg=1, taper=(.7, .9))
    steel.cyl(.035, .45, loc=(-.86, -3.82, .15), rot=FORWARD, seg=8, bevel=0)
    steel.cyl(.05, .07, loc=(-.86, -4.03, .15), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (-.86, -4.08, .15))
    # Stores. Wingtip rails with short-range missiles and nav lights.
    aams = _aam_parts(a)
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        x = s * 6.12
        armor.box((.08, 1.7, .1), loc=(x, 3.1, -.08), bevel=.02, seg=1)
        _aam(aams, (s * 6.21, 2.75, -.15), length=2.3, r=.065)
        glow.box((.05, .14, .05), loc=(x, 2.28, -.08), bevel=0)
    # Wing pylons, each with a missile on both shoulder rails (Muzzle_missile between the four noses).
    zp = wing.bottom(3.6) - .32
    for s in (-1, 1):
        x = s * 3.6
        _pylon(pylons, x, .0, 2.2, wing.bottom(3.6) + .05, zp + .06, w=.1)
        pylons.box((.46, 1.3, .06), loc=(x, .9, zp + .06), bevel=.01, seg=1)                 # shoulder beam
        for dx in (-.2, .2):
            _aam(aams, (x + dx, .6, zp), length=3.0, r=.085, canards=False, fin=1.7)
    a.pivot('Muzzle_missile', (0, .6 - 1.5, zp))


# ----------------------------------------------------------------------------- tank buster
def _side_x(rings, y, z):
    """Half-width of a lofted body at (y, z) on its +X side."""
    ring = sorted((q for q in _ring_at(rings, y) if q[0] > 0), key=lambda q: q[2])
    for q0, q1 in zip(ring, ring[1:]):
        if q0[2] <= z <= q1[2]:
            k = (z - q0[2]) / ((q1[2] - q0[2]) or 1e-9)
            return q0[0] + (q1[0] - q0[0]) * k
    return max(q[0] for q in ring)


def _mav(p, x, y, z, length=2.1, r=.135, seg=8):
    """Air-to-ground missile with its nose at y on parts p = dict(body=, nose=, band=, fins=): a glass
    seeker dome, a yellow warhead band and long wings set as a + (so the rounds of a triple launcher
    clear each other). Lighter than mb_air's _maverick."""
    p['body'].lathe([(r * .92, length * .06), (r, length * .12), (r, length * .95), (r * .7, length)], loc=(x, y, z),
                    rot=BACKWARD, seg=seg)
    p['nose'].lathe([(0, 0), (r * .72, length * .025), (r * .9, length * .08)], loc=(x, y, z), rot=BACKWARD, seg=seg)
    p['band'].cyl(r + .011, .06, loc=(x, y + length * .3, z), rot=FORWARD, seg=seg, bevel=0)
    for k in range(4):
        _trap_fin(p['fins'], (x, y + length * .42, z), k * R90, r * .6, r * 1.1, length * .5, length * .12,
                  length * .36, .016)


def _turbofan_lite(a, x, y, z, r, length, seg=14, blades=8):
    """mb_air's _turbofan with fewer sides and no exhaust glow: a Team cowl from the intake lip at y
    rearwards, a dark fan face with spinner and blades, a dark exhaust and a core plug."""
    L = length
    _revolve(a.part('Nacelles', 'Team'), [(r * .8, .34), (r * .84, 0), (r * .95, .025), (r, .3), (r, L * .72),
                                          (r * .84, L), (r * .76, L), (r * .76, L * .72), (r * .8, L * .4)],
             (x, y, z), BACKWARD, seg)
    dark = a.part('Fan_faces', 'Undercarriage')
    dark.cyl(r * .78, .06, loc=(x, y + .38, z), rot=FORWARD, seg=seg - 2, bevel=0)
    dark.cyl(r * .74, .05, loc=(x, y + L * .8, z), rot=FORWARD, seg=seg - 2, bevel=0)
    steel = a.part('Fan_blades', 'Steel')
    steel.cyl(r * .24, r * .45, r2=.01, loc=(x, y + .32 - r * .2, z), rot=FORWARD, seg=8, bevel=0)   # spinner
    for k in range(blades):
        phi = k * math.tau / blades
        steel.box((r * .54, .1, .018), loc=(x + math.cos(phi) * r * .5, y + .3, z + math.sin(phi) * r * .5),
                  rot=(.55, -phi, 0), bevel=0)
    steel.cyl(r * .42, .5, r2=r * .08, loc=(x, y + L - .05, z), rot=BACKWARD, seg=10, bevel=0)       # core plug


def tank_buster(a):
    """Heavy ground-attack jet (A-10 lineage), 17 x 17 m: an armoured nose round a huge seven-barrel
    gatling, a bubble canopy over a bolted titanium cockpit tub, straight wings with gear pods at the
    roots, split ailerons and drooped tips, two turbofans high on the rear fuselage and twin fins on
    the tailplane tips. Stores: triple launchers of Maverick-style missiles inboard, rocket pods, and
    outboard an air-to-air missile pair (left wing) and an ECM pod (right).
    Origin at the fuselage centre (it flies)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    hull = [_sec(-7.7, .36, -.5, .08, pt=3, pb=3), _sec(-6.95, .68, -.8, .42, pt=3, pb=3),
            _sec(-5.8, .85, -.96, .6, pt=3, pb=3), _sec(-4.3, .91, -.99, .68, pt=3, pb=3),
            _sec(-2.6, .94, -.99, .69, pt=3, pb=3), _sec(-.65, .91, -.94, .68, pt=3, pb=3),
            _sec(1.56, .81, -.81, .65, pt=3, pb=3), _sec(3.64, .62, -.6, .6, pt=2.6, pb=2.6), _sec(5.46, .42, -.34, .49),
            _sec(6.83, .2, -.08, .39)]
    body.loft(hull + [[(0, 7.3, .21)]], bevel=.02, seg=1)
    _patch(armor, hull, -6.95, -6.0, 6, 10)                                                # anti-glare panel
    armor.cyl(.09, .03, loc=(0, -6.7, _skin_z(hull, -6.7, 0) + .006), seg=10, bevel=0)     # refuelling slot
    # Bolted titanium tub round the cockpit: three plates a side, bolts at their corners.
    bolts = a.part('Bolts', 'Steel')
    for y0, y1 in ((-6.5, -5.55), (-5.45, -4.45), (-4.35, -3.3)):
        for i0, i1, sx in ((3, 5, 1), (11, 13, -1)):
            _patch(armor, hull, y0, y1, i0, i1, out=.02, inn=.012, bevel=.006)
            for y in (y0 + .12, y1 - .12):
                for zz in (.12,):
                    bolts.box((.05, .05, .05), loc=(sx * (_side_x(hull, y, zz) + .035), y, zz), bevel=0)
    # Seven-barrel gatling under the nose, offset left (+X) so the firing barrel is on the centreline.
    gx, gz = .1, -.24
    steel.cyl(.21, .5, loc=(gx, -7.85, gz), rot=FORWARD, seg=12, bevel=.02, bseg=1)       # housing
    armor.box((.5, .8, .34), loc=(gx, -7.45, gz - .02), bevel=.05, seg=1, taper=(.9, 1))    # gun fairing
    for k in range(7):
        ang = k * math.tau / 7
        steel.cyl(.036, 1.62, loc=(gx + math.cos(ang) * .105, -8.9, gz + math.sin(ang) * .105), rot=FORWARD, seg=6,
                  bevel=0)
    steel.cyl(.165, .09, loc=(gx, -8.5, gz), rot=FORWARD, seg=12, bevel=0)               # mid clamp
    steel.cyl(.17, .12, loc=(gx, -9.62, gz), rot=FORWARD, seg=12, bevel=0)               # muzzle clamp
    a.part('Gun_bore', 'Undercarriage').cyl(.12, .02, loc=(gx, -9.685, gz), rot=FORWARD, seg=12, bevel=0)
    a.pivot('Muzzle_gun', (gx, -9.72, gz))
    # Bubble canopy high on the nose, a spine fairing behind it.
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    st = [(-6.24, .26, .75), (-5.79, .49, 1.25), (-4.94, .57, 1.46), (-4.03, .56, 1.43), (-3.32, .43, 1.2),
          (-2.86, .23, .91)]
    _canopy(glass, frames, [(y, w, _skin_z(hull, y, w) - .03, z1) for y, w, z1 in st], bows=(-5.66,), r=.03)
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in ((-3.19, .35, 1.07), (-1.82, .44, .96),
                                                                         (.26, .39, .81))]
    body.loft(spine + [[(0, 2.08, .65)]], bevel=.02, seg=1)
    for y, z, t in ((-1.3, 1.0, -.35), (4.7, .58, -.35), (-2.0, -1.0, .35)):              # blade aerials
        steel.box((.025, .3, .22), loc=(0, y, z), rot=(t, 0, 0), bevel=0, taper=(1, .5))
    # Straight low wings: a flat centre panel, dihedral outer panels and drooped tips.
    inner = Planform(.72, 3.38, -1.85, -1.76, 3.21, 2.99, .39, .35, -.72)
    outer = Planform(3.38, 8.06, -1.76, -1.33, 2.99, 1.85, .35, .18, -.72, -.155)
    tip = Planform(8.06, 8.45, -1.33, -1.25, 1.85, 1.66, .18, .1, -.155, -.415)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, inner, frame, cs=[(1.17, 3.38, .72)])
        _wing(body, moving, outer, frame, cs=[(3.38, 5.46, .72), (5.46, 7.87, .7)])
        _surface(body, tip, frame, ends=(False, True))
        _skin_panel(panels, inner, frame, 2.4, 3.25, .2, .55)
        _skin_panel(panels, outer, frame, 3.42, 5.4, .22, .56)
    for s in (-1, 1):
        glow.box((.06, .2, .08), loc=(s * 8.4, -1.27, tip.at(8.4)[3]), bevel=.01, seg=1)
        # Main gear pods at the wing roots with the tyres showing.
        x = s * 1.77
        gear = [_sec(-2.54, .26, -1.24, -.81, pt=2.2, pb=2.2), _sec(-1.82, .35, -1.37, -.65, pt=2.2, pb=2.2),
                _sec(.39, .35, -1.34, -.65, pt=2.2, pb=2.2), _sec(1.3, .18, -1.12, -.78)]
        body.loft([[(x, -2.99, -1.04)]] + [[(x + px, py, pz) for px, py, pz in ring] for ring in gear], bevel=.02,
                  seg=1)
        a.part('Tyres', 'Rubber').cyl(.39, .26, loc=(x, -2.15, -1.27), rot=ACROSS, seg=12, bevel=.06, bseg=1)
        steel.cyl(.18, .28, loc=(x, -2.15, -1.27), rot=ACROSS, seg=8, bevel=0)
    # Turbofans high on the rear fuselage on stub pylons.
    for s in (-1, 1):
        x = s * 1.46
        _turbofan_lite(a, x, 2.11, 1.07, .73, 3.06)
        body.limb((s * .29, 3.58, .47), (s * 1.12, 3.58, .81), .21, 1.82, bevel=.05, seg=1)
        glow.box((.04, .65, .05), loc=(x + s * .735, 3.8, 1.07), bevel=0)                  # formation lights
    # Tailplane with elevators; twin fins on its tips with rudders, reaching below it too.
    stab = Planform(0, 3.54, 5.66, 5.98, 1.69, 1.37, .16, .12, .29)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.33, 3.38, .68)])
    fin = Planform(0, 2.86, 5.59, 5.98, 1.85, 1.4, .16, .12)
    for s in (-1, 1):
        frame = _upright(s * 3.56, -.68, 0.0)
        _wing(body, moving, fin, frame, cs=[(.39, 2.67, .66)], lower=1.0, root=True)
        glow.box((.05, .15, .05), loc=(s * 3.56, 7.35, 2.19), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.065, loc=(0, 7.28, .26), seg=8, rings=5)
    # Stores. Triple Maverick-style launchers inboard.
    pylons = a.part('Pylons', 'Armor')
    mav = dict(body=a.part('Missiles', 'Fuel'), nose=a.part('Missile_seekers', 'Glass'),
               band=a.part('Missile_bands', 'Hazard'), fins=a.part('Missile_fins', 'Armor'))
    zm = inner.bottom(2.67) - .5
    ym = -2.3
    for s in (-1, 1):
        x = s * 2.67
        _pylon(pylons, x, -1.8, .3, inner.bottom(2.67) + .05, zm + .2, w=.12)
        pylons.box((.3, 1.9, .34), loc=(x, ym + 1.05, zm + .03), bevel=.02, seg=1)           # launcher body
        for dx, dz in ((-.25, 0), (.25, 0), (0, -.34)):
            _mav(mav, x + dx, ym, zm + dz)
    a.pivot('Muzzle_missile', (0, ym - .02, zm - .113))
    # Rocket pods.
    zr = outer.bottom(3.84) - .52
    for s in (-1, 1):
        x = s * 3.84
        _pylon(pylons, x, -1.45, .35, outer.bottom(3.84) + .06, zr + .2, w=.12)
        _rocket_pod(a, x, -1.9, zr, .28, 2.05)
    a.pivot('Muzzle_rocket', (0, -1.93, zr))
    # Outboard: an air-to-air missile pair on the left wing (+X), an ECM pod on the right.
    x = 6.96
    zt = outer.bottom(x)
    _pylon(pylons, x, -1.1, .2, zt + .06, zt - .16, w=.1)
    pylons.box((.46, 1.0, .07), loc=(x, -.45, zt - .17), bevel=.01, seg=1)
    aams = _aam_parts(a, 'Sidewinders')
    for dx in (-.2, .2):
        _aam(aams, (x + dx, -.5, zt - .27), length=2.2, r=.07, canards=False)
    x = -6.96
    _pylon(pylons, x, -1.1, .2, zt + .06, zt - .16, w=.1)
    ecm = a.part('ECM_pod', 'Armor')
    ecm.lathe([(.05, 0), (.14, .18), (.2, .5), (.2, 2.3), (.15, 2.7), (.06, 2.85)], loc=(x, -1.7, zt - .36),
              rot=BACKWARD, seg=10)
    for sx in (-1, 1):
        a.part('ECM_windows', 'Undercarriage').box((.03, .7, .16), loc=(x + sx * .195, -.6, zt - .36), bevel=0)


# ----------------------------------------------------------------------------- recon drone
def recon_drone(a):
    """Medium-altitude long-endurance reconnaissance drone (TB2 lineage), 12 x 7 m: a slim fuselage
    with a big sensor ball under the nose, a long shoulder wing with flaps and ailerons, twin tail
    booms ending in an inverted V-tail with ruddervators, a two-blade pusher `Propeller` (spins
    about local Y) between the booms, fixed tricycle gear and one small missile under each wing.
    Origin at the fuselage centre (it flies)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=16, pt=2.3, pb=2.6)
    hull = [sec(-3.15, .14, -.13, .1), sec(-2.8, .25, -.25, .22), sec(-2.2, .3, -.29, .29), sec(-1.0, .31, -.3, .32),
            sec(.4, .3, -.29, .3), sec(1.6, .25, -.24, .24), sec(2.5, .17, -.16, .16), sec(2.85, .11, -.1, .1)]
    body.loft([[(0, -3.35, -.02)]] + hull, bevel=.012, seg=1)
    _patch(panels, hull, -2.1, -1.2, 5, 11, out=.013, inn=.011, bevel=.004)                  # avionics hatch
    _patch(panels, hull, 1.0, 2.0, 5, 11, out=.013, inn=.011, bevel=.004)                    # engine cowl
    for i0, i1 in ((2, 4), (12, 14)):                                                        # side access panels
        _patch(panels, hull, -.6, .3, i0, i1, out=.012, inn=.011, bevel=.004)
    # Engine air scoop and cooling louvres on the back, twin exhausts under the tail.
    zs = _skin_z(hull, .95, 0)
    armor.box((.2, .5, .1), loc=(0, .95, zs + .02), bevel=.02, seg=1, taper=(.9, .8))
    dark.box((.14, .04, .05), loc=(0, .69, zs + .03), bevel=0)
    for s in (-1, 1):
        dark.grille(.3, .08, loc=(s * .2, 1.9, _skin_z(hull, 1.9, .2) - .005), rot=(-R90, 0, s * .6), slats=3,
                    depth=.03, thickness=.018)
        steel.cyl(.035, .26, loc=(s * .1, 2.55, -.15), rot=(-R90 + .25, 0, 0), seg=8, bevel=0)
    for y, z, t in ((-1.6, .31, -.35), (.9, -.3, .35), (2.2, .2, -.35)):                   # blade aerials
        steel.box((.018, .15, .13), loc=(0, y, z + (.05 if z > 0 else -.05)), rot=(t, 0, 0), bevel=0, taper=(1, .5))
    for y in (-.5, -1.1):                                                                    # GPS / datalink domes
        armor.sphere((.07, .07, .035), loc=(0, y, _skin_z(hull, y, 0) - .005), seg=10, rings=5)
    steel.cyl(.012, .32, loc=(.12, -3.2, -.06), rot=FORWARD, seg=5, bevel=0)                 # pitot
    # Shoulder wing with flaps and ailerons.
    wing = Planform(0, 6.0, -.5, -.28, 1.0, .5, .13, .055, .3, .45)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(1.25, 3.2, .72), (3.2, 5.7, .72)], bevel=0)
        _skin_panel(panels, wing, frame, 1.4, 2.9, .18, .55, out=.01, inn=.009)
        _skin_panel(panels, wing, frame, 3.5, 5.2, .2, .56, out=.01, inn=.009)
    for s in (-1, 1):
        glow.box((.05, .14, .05), loc=(s * 6.01, -.27, .45), bevel=.01, seg=1)
    body.loft([_dome(y, w, wing.top(0, (y + .5) / 1.0) - .03, z1) for y, w, z1 in
               ((-.55, .12, .36), (-.3, .26, .45), (.2, .26, .44), (.55, .12, .36))], bevel=.01, seg=1)
    # Twin tail booms under the wing, ending in an inverted V-tail (ruddervators).
    tail = Planform(0, 1.25, 2.66, 3.0, .7, .38, .065, .03)
    for s in (-1, 1):
        x = s * 1.05
        zb = wing.bottom(1.05) - .04
        boom = [(-.7, .035), (-.45, .07), (2.6, .07), (3.35, .05)]
        body.loft([[(x, -.85, zb)]] + [[(x + q[0], q[1], q[2]) for q in _sec(y, r, zb - r, zb + r, n=10)]
                                        for y, r in boom] + [[(x, 3.55, zb)]], bevel=0)
        _wing(body, moving, tail, _upright(x, zb - .02, 3 * math.pi / 4), cs=[(.1, 1.18, .6)], lower=1.0, bevel=0)
        glow.box((.03, .12, .03), loc=(x, 3.5, zb + .06), bevel=0)
        tipv = Vector(_upright(x, zb - .02, 3 * math.pi / 4)(1.25, 3.2, 0))
        glow.box((.04, .1, .04), loc=tuple(tipv), bevel=0)
    # Two-blade pusher propeller at the tail between the booms.
    dark.cyl(.1, .12, loc=(0, 2.9, 0), rot=FORWARD, seg=10, bevel=.01, bseg=1)
    p = a.pivot('Propeller', (0, 3.02, 0))
    a.part('Propeller_hub', 'Steel', p).lathe([(.1, -.05), (.1, .05), (.07, .14), (0, .22)], rot=BACKWARD, seg=10)
    blades = a.part('Propeller_blades', 'Armor', p)
    for k in range(2):
        _prop_blade(blades, R90 + k * math.pi, .07, .74, .15, .07, .04, .014, .75, .28, axis_y=.02)
    # Big sensor ball under the nose: yoke, ball and windows.
    armor.cyl(.09, .16, loc=(0, -2.35, -.33), seg=10, bevel=.01, bseg=1)
    armor.sphere(.24, loc=(0, -2.35, -.56), seg=14, rings=9)
    sensor = a.part('Sensor', 'Glass')
    sensor.cyl(.09, .05, loc=(-.07, -2.56, -.58), rot=FORWARD, seg=10, bevel=0)
    sensor.cyl(.05, .05, loc=(.11, -2.555, -.54), rot=FORWARD, seg=8, bevel=0)
    sensor.cyl(.035, .05, loc=(.1, -2.56, -.66), rot=FORWARD, seg=8, bevel=0)
    # Fixed tricycle gear: nose leg under the nose, bow-spring main legs to the sides.
    gear, tyres = a.part('Gear', 'Steel'), a.part('Tyres', 'Rubber')
    gear.limb((0, -2.8, -.2), (0, -2.85, -.72), .05, .05, bevel=0)
    tyres.cyl(.12, .07, loc=(0, -2.85, -.8), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    gear.cyl(.03, .12, loc=(0, -2.85, -.8), rot=ACROSS, seg=6, bevel=0)
    for s in (-1, 1):
        gear.tube([(s * .15, .25, -.25), (s * .45, .25, -.55), (s * .7, .25, -.72)], .03, seg=6)
        tyres.cyl(.14, .08, loc=(s * .77, .25, -.8), rot=ACROSS, seg=10, bevel=.02, bseg=1)
        gear.cyl(.035, .12, loc=(s * .77, .25, -.8), rot=ACROSS, seg=6, bevel=0)
    a.part('Lamps', 'Lamp').box((.08, .03, .05), loc=(0, -2.83, -.43), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.035, loc=(0, 1.3, _skin_z(hull, 1.3, 0) + .005), seg=8, rings=5)
    # One small missile under each wing, outboard of the booms.
    mis = dict(body=a.part('Missiles', 'Fuel'), fins=a.part('Missile_fins', 'Armor'),
               nose=a.part('Missile_seekers', 'Glass'), band=a.part('Missile_bands', 'Hazard'))
    pylons = a.part('Pylons', 'Armor')
    zm = wing.bottom(2.25) - .2
    for s in (-1, 1):
        x = s * 2.25
        _pylon(pylons, x, -.42, .25, wing.bottom(2.25) + .04, zm + .08, w=.05)
        pylons.box((.07, .8, .04), loc=(x, -.15, zm + .075), bevel=0)                          # launch rail
        _aam(mis, (x, -.2, zm), length=1.1, r=.06, seg=8, canards=True, fin=1.5)
    a.pivot('Muzzle_missile', (0, -.75, zm))


# ----------------------------------------------------------------------------- heavy attack helicopter
def _x_tail_rotor(a, tr, R, chord, side=1, t=.034, gap=.09):
    """X-shaped (scissor) tail rotor under pivot tr, spinning about local X with its blades in the YZ
    plane: two stacked two-blade pairs 55 degrees apart on one hub. side is the direction (x) the hub
    faces."""
    hub = a.part('Tail_rotor_hub', 'Steel', tr)
    hub.cyl(R * .1 + .03, .1 + gap, loc=(side * gap / 2, 0, 0), rot=ACROSS, seg=10, bevel=.01, bseg=1)
    hub.lathe([(R * .08, 0), (R * .06, .06), (0, .11)], loc=(side * (gap + .05), 0, 0), rot=(0, side * R90, 0), seg=8)
    bl = a.part('Tail_rotor_blades', 'Armor', tr)
    tips = a.part('Tail_rotor_tips', 'Hazard', tr)
    for ang, dx in ((0.0, 0.0), (math.pi, 0.0), (.96, gap), (.96 + math.pi, gap)):
        d = (side * dx, -math.sin(ang), math.cos(ang))
        e = (0, math.cos(ang), math.sin(ang))
        _blade(bl, tips, Vector(d), e, (side, 0, 0), R * .13, R, chord, t, pitch=.2, stripe=R * .16, tip=R * .08)


def heavy_attack_heli(a):
    """Heavy assault gunship (Mi-24 / Mi-35 lineage), 17 m with the rotor: stepped tandem canopies of
    flat armoured glass panels, the gunner low in the nose over a twin-barrel chin turret and the pilot
    raised behind, a sensor turret and a missile-guidance pod under the nose, a troop cabin under two
    engines with dust filters and box exhaust suppressors, an IR jammer, anhedral stub wings with four
    big rocket pods and 2 x 2 anti-tank missile tubes on each tip plate, a five-blade rotor, an
    X-shaped tail rotor on the left of the fin and tricycle wheels. Origin on the ground under the
    cabin (the wheels stand on z = 0)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass', flat=True)
    frames = a.part('Canopy_frames', 'Armor')
    panels = a.part('Panels', 'Team')
    body.loft([
        _octagon(-7.62, .24, 1.18, 1.51),
        _octagon(-7.2, .55, 1.01, 1.8),
        _octagon(-6.24, .74, .94, 1.94),
        _octagon(-5.46, .86, .94, 2.09),
        _octagon(-4.32, 1.01, .96, 2.45),
        _octagon(-3.6, 1.13, .98, 2.81),
        _octagon(.24, 1.18, 1.02, 2.9),
        _octagon(1.68, .98, 1.2, 2.86),
        _octagon(2.82, .58, 1.75, 2.69),
    ], bevel=.08, seg=2)
    body.loft([_octagon(2.52, .55, 1.8, 2.69), _octagon(7.8, .26, 2.11, 2.52)], bevel=.05, seg=1)      # tail boom
    body.prism([(6.42, 2.4), (7.86, 2.33), (8.46, 4.44), (7.74, 4.5)], .22, bevel=.035)                # fin
    body.box((3.1, .86, .12), loc=(0, 6.54, 2.35), bevel=.025, seg=1, taper=(1, .7))                  # stabiliser
    # Stepped tandem canopies of flat armoured panels: the gunner low in front, the pilot raised behind.
    gunner = [_bubble(-7.34, .31, 1.56, 1.8), _bubble(-6.85, .6, 1.68, 2.38), _bubble(-5.95, .67, 1.8, 2.46),
              _bubble(-5.5, .55, 1.87, 2.24)]
    pilot = [_bubble(-5.72, .67, 1.92, 2.6), _bubble(-5.1, .77, 1.99, 3.1), _bubble(-4.15, .79, 2.16, 3.18),
             _bubble(-3.62, .67, 2.3, 2.93)]
    for stations in (gunner, pilot):
        glass.loft(stations, bevel=0)
        for i in (2, 3, 4, 5):                                                            # panel frames
            frames.tube([tuple(Vector(q[i]) + Vector((0, 0, .012))) for q in stations[1:]], .03, seg=5)
        for sec in stations[1:3]:
            _hoop(frames, sec, r=.035)
    for s in (-1, 1):
        # Bolted armour plates on the cockpit sides, following the taper of the nose.
        for y, w, yaw, z, length in ((-6.55, .672, .195, 1.43, .8), (-5.0, .92, .13, 1.58, 1.1)):
            m = _frame((s * (w + .02), y, z), (0, 0, -s * yaw))
            armor.box((.05, length, .34), loc=m.to_translation(), rot=(0, 0, -s * yaw), bevel=.012, seg=1)
            for dy in (-length / 2 + .08, length / 2 - .08):
                for dz in (-.11, .11):
                    steel.box((.03, .05, .05), loc=m @ Vector((s * .03, dy, dz)), rot=(0, 0, -s * yaw), bevel=0)
        # Troop cabin: three windows and the upper door leaf on each side.
        for y in (-3.0, -2.28, -1.56):
            glass.box((.02, .46, .36), loc=(s * 1.152, y, 2.06), bevel=0)
        panels.box((.036, 1.56, .7), loc=(s * 1.18, -.36, 1.97), bevel=.008, seg=1)
        steel.box((.03, .5, .04), loc=(s * 1.2, -.36, 1.58), bevel=0)                    # step / grab bar
        # Flare dispensers on the tail boom.
        armor.box((.12, .6, .26), loc=(s * .5, 3.95, 2.28), bevel=.02, seg=1)
        dark.grille(.48, .26, loc=(s * .57, 3.95, 2.28), rot=(0, 0, s * R90), slats=3, depth=.03, thickness=.03)
    # Under the nose: a sensor turret on the left (+X), the missile-guidance pod on the right.
    sensor = a.part('Sensor', 'Glass')
    armor.cyl(.08, .2, loc=(.55, -6.45, 1.0), seg=8, bevel=0)
    armor.sphere(.21, loc=(.55, -6.45, .86), seg=12, rings=8)
    sensor.cyl(.09, .04, loc=(.55, -6.64, .87), rot=FORWARD, seg=10, bevel=0)
    armor.cyl(.15, .6, loc=(-.58, -6.55, 1.08), rot=FORWARD, seg=10, bevel=.03, bseg=1)
    sensor.cyl(.11, .03, loc=(-.58, -6.86, 1.08), rot=FORWARD, seg=10, bevel=0)
    steel.tube([(.34, -7.1, 1.55), (.38, -7.6, 1.62), (.4, -8.05, 1.66)], .028, seg=6)       # air-data boom
    steel.cyl(.055, .12, loc=(.4, -7.8, 1.65), rot=FORWARD, seg=6, bevel=0)
    # Twin engines over the cabin: dust filters on the intakes, box exhaust suppressors, gearbox, IR jammer.
    for s in (-1, 1):
        x = s * .62
        body.cyl(.48, 4.1, loc=(x, -1.08, 3.19), rot=FORWARD, seg=14, bevel=.12)
        armor.cyl(.5, .62, loc=(x, -3.34, 3.19), rot=FORWARD, seg=14, bevel=.05, bseg=1)            # dust filter
        armor.sphere((.42, .26, .42), loc=(x, -3.62, 3.19), seg=12, rings=6)
        steel.torus(.5, .035, loc=(x, -3.1, 3.19), rot=FORWARD, seg=14, ring=4)
        dark.grille(.5, .3, loc=(x + s * .47, -3.34, 3.19), rot=(0, 0, s * R90), slats=3, depth=.04, thickness=.03)
        _exhaust_duct(a, (s * 1.03, 1.28, 3.25), s * -.35, size=(.44, 1.0, .5), pitch=.18)
    body.box((1.08, 2.88, .6), loc=(0, -.84, 3.34), bevel=.12, taper=(.7, .8))
    steel.cyl(.16, .84, loc=(0, -.84, 3.84), seg=10, bevel=0)                                          # mast
    armor.cyl(.24, .5, loc=(0, 1.95, 3.0), seg=12, bevel=.02, bseg=1)                                  # IR jammer
    sensor.cyl(.26, .16, loc=(0, 1.95, 3.14), seg=12, bevel=0)
    armor.cyl(.27, .06, loc=(0, 1.95, 3.25), seg=12, bevel=.015, bseg=1)
    # Anhedral stub wings: two big rocket pods each, a 2 x 2 missile-tube launcher on each tip plate.
    pylons = a.part('Pylons', 'Armor')
    tubes = a.part('Launch_tubes', 'Fuel')
    droop = math.tan(.2)

    def wing_z(x):
        return 2.06 - (x - 1.08) * droop
    for s in (-1, 1):
        body.limb((s * .96, 0, wing_z(.96)), (s * 3.9, 0, wing_z(3.9)), .19, 1.56, bevel=.04, seg=1, taper=(1, .75))
        for x in (1.92, 2.94):
            z = wing_z(x)
            _pylon(pylons, s * x, -.54, .54, z + .02, z - .34, w=.14)
            _rocket_pod(a, s * x, -1.08, z - .67, .33, 1.92, tubes=7)
        z = wing_z(3.9)
        armor.box((.12, 1.44, .84), loc=(s * 3.96, -.06, z - .24), bevel=.02, seg=1)                   # tip plate
        for dx in (.17, .41):
            for zz in (z, z - .28):
                tubes.cyl(.1, 1.5, loc=(s * (3.96 + dx), -.2, zz), rot=FORWARD, seg=8, bevel=.012, bseg=1)
                dark.cyl(.075, .02, loc=(s * (3.96 + dx), -.955, zz), rot=FORWARD, seg=8, bevel=0)         # bore
        a.part('Missile_bands', 'Hazard').box((.5, .07, .5), loc=(s * 4.25, .3, z - .14), bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .16, .07), loc=(s * 4.03, .55, z + .2), bevel=.01, seg=1)
    a.pivot('Muzzle_rocket', (0, -1.16, (wing_z(1.92) + wing_z(2.94)) / 2 - .67))
    a.pivot('Muzzle_missile', (0, -.99, wing_z(3.9) - .14))
    # Tricycle landing gear (retractable, shown down): twin nose wheels, mains behind the wings.
    gear = a.part('Gear', 'Steel')
    tyres = a.part('Tyres', 'Rubber')
    for x in (-.2, .2):
        tyres.cyl(.31, .17, loc=(x, -5.88, .31), rot=ACROSS, seg=10, bevel=.05, bseg=1)
        gear.cyl(.14, .23, loc=(x * 1.02, -5.88, .31), rot=ACROSS, seg=8, bevel=0)
    gear.cyl(.06, .6, loc=(0, -5.88, .31), rot=ACROSS, seg=6, bevel=0)
    gear.limb((0, -5.88, .31), (0, -5.7, 1.08), .12, .12, bevel=.02, seg=1)
    for s in (-1, 1):
        tyres.cyl(.43, .29, loc=(s * 1.46, 1.32, .43), rot=ACROSS, seg=12, bevel=.07, bseg=1)
        gear.cyl(.2, .31, loc=(s * 1.46, 1.32, .43), rot=ACROSS, seg=8, bevel=0)
        gear.limb((s * 1.3, 1.32, .43), (s * .91, 1.08, 1.5), .14, .14, bevel=.02, seg=1)              # oleo
        gear.limb((s * 1.3, 1.32, .43), (s * .86, 2.04, 1.34), .1, .1, bevel=.015, seg=1)             # drag brace
    a.part('Lamps', 'Lamp').box((.24, .17, .07), loc=(0, -5.16, .95), bevel=.01, seg=1)
    steel.cyl(.018, .7, loc=(0, 4.2, 2.83), seg=5, bevel=0)                                               # antennas
    steel.box((.025, .26, .18), loc=(0, -2.4, .92), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    a.part('Beacon', 'TeamGlow').sphere(.08, loc=(0, 8.08, 4.56), seg=8, rings=5)
    # Twin-barrel chin turret on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -6.66, .96))
    a.part('Gun_turret', 'Armor', g).sphere(.36, loc=(0, 0, -.05), seg=12, rings=8)
    gun = a.part('Gun', 'Steel', g)
    gun.box((.34, .5, .22), loc=(0, -.4, -.12), bevel=.03, seg=1)
    for x in (-.08, .08):
        gun.cyl(.042, 1.1, loc=(x, -1.1, -.12), rot=FORWARD, seg=8, bevel=0)
        gun.cyl(.06, .14, loc=(x, -1.62, -.12), rot=FORWARD, seg=8, bevel=0)
    a.part('Gun_feed', 'Undercarriage', g).tube([(.14, -.3, -.06), (.28, -.1, .02), (.3, .12, .1)], .04, seg=6)
    a.pivot('Muzzle_gun', (0, -1.7, -.12), g)
    # Five-blade main rotor; X-shaped tail rotor on the left (+X) of the fin.
    r = a.pivot('Rotor', (0, -.84, 4.26))
    _rotor_head(a, r, 5, 7.3, .52, hub=.42, phase=R90, t=.07, cap=.28, stripe=.4, droop=.12)
    armor.cyl(.14, .24, loc=(.2, 7.94, 3.6), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    tr = a.pivot('Tail_rotor', (.4, 7.94, 3.6))
    _x_tail_rotor(a, tr, 1.3, .24, side=1)


# ----------------------------------------------------------------------------- drone mothership
# Envelope profile (radius, y) from the nose to the tail, revolved about Y.
ENVELOPE = [(0, -13.6), (1.3, -13.3), (2.2, -12.5), (2.9, -11.1), (3.35, -9.5), (3.62, -7.2), (3.72, -4.6),
            (3.72, -1.0), (3.6, 2.6), (3.3, 5.7), (2.8, 8.5), (2.1, 10.9), (1.3, 12.7), (.6, 13.6)]


def _env_r(y, prof=ENVELOPE):
    """Envelope radius at y (linear between profile stations, like the lathe's own faces)."""
    for (r0, y0), (r1, y1) in zip(prof, prof[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / (y1 - y0)
    return 0.0


def _env_plate(part, y0, y1, a0, a1, out=.06, inn=.03, na=5, bevel=.012, prof=ENVELOPE):
    """Curved armour plate on the envelope between y0 and y1 and angles a0..a1 around Y (0 = top,
    positive towards +X), standing `out` proud of the skin; stations follow the profile's own."""
    ys = [y0] + [y for _, y in prof if y0 + .05 < y < y1 - .05] + [y1]
    loops = []
    for y in ys:
        r = _env_r(y, prof)
        ang = [a0 + (a1 - a0) * i / (na - 1) for i in range(na)]
        outer = [((r + out) * math.sin(u), y, (r + out) * math.cos(u)) for u in ang]
        inner = [((r - inn) * math.sin(u), y, (r - inn) * math.cos(u)) for u in reversed(ang)]
        loops.append(outer + inner)
    part.loft(loops, bevel=bevel, seg=1)


def _searchlight(a, loc, yaw=0.0, pitch=0.0, r=.2, parent=None, up=True):
    """Searchlight drum facing -Y turned by yaw (about Z) and tipped down by pitch: armoured drum,
    Lamp lens and a mounting bracket above it (below it if up is False)."""
    rot = (R90 + pitch, 0, yaw)
    m = _frame(loc, rot)
    a.part('Searchlights', 'Armor', parent).cyl(r + .04, r * 1.4, loc=loc, rot=rot, seg=10, bevel=.02, bseg=1)
    a.part('Lamps', 'Lamp', parent).cyl(r, .04, loc=tuple(m @ Vector((0, 0, r * .7 + .01))), rot=rot, seg=10, bevel=0)
    a.part('Searchlights', 'Armor', parent).box((.08, .08, .3),
                                                loc=tuple(Vector(loc) + Vector((0, 0, (r + .15) * (1 if up else -1)))),
                                                bevel=0)


def _fpv_drone(a, x, y, z, k=0):
    """FPV strike drone hanging under a rail at (x, y, z) (its body centre), nose to -Y: carbon X
    frame, four motors with two-blade props, an RPG-style warhead slung under the body, a team
    status light and the rack clamp."""
    carbon = a.part('Drone_frames', 'Undercarriage')
    carbon.box((.22, .36, .1), loc=(x, y, z), bevel=.02, seg=1)
    for s in (-1, 1):
        carbon.box((1.0, .06, .035), loc=(x, y, z + .01 + (s + 1) * .006), rot=(0, 0, s * math.pi / 4), bevel=0)
    motors = a.part('Drone_motors', 'Steel')
    props = a.part('Drone_props', 'Armor')
    for i, (dx, dy) in enumerate(((.33, .33), (-.33, .33), (.33, -.33), (-.33, -.33))):
        motors.cyl(.045, .07, loc=(x + dx, y + dy, z + .05), seg=6, bevel=0)
        props.box((.46, .045, .012), loc=(x + dx, y + dy, z + .092), rot=(0, 0, .5 + i * 1.1 + k * .7), bevel=0)
    war = a.part('Drone_warheads', 'Armor')
    war.cyl(.05, .26, loc=(x, y - .08, z - .1), rot=FORWARD, seg=6, bevel=0)
    war.cyl(.07, .2, r2=.02, loc=(x, y - .3, z - .1), rot=FORWARD, seg=6, bevel=0)
    a.part('Drone_bands', 'Hazard').cyl(.074, .04, loc=(x, y - .215, z - .1), rot=FORWARD, seg=6, bevel=0)
    a.part('Drone_lights', 'TeamGlow').box((.06, .06, .03), loc=(x, y + .12, z + .055), bevel=0)
    a.part('Drone_clamps', 'Steel').box((.06, .14, .14), loc=(x, y, z + .11), bevel=0)


def drone_mothership(a):
    """Armoured airship that carries and launches FPV drones, 28 m long: a rigid envelope clad with a
    dark armoured spine, team-painted flank plates and side armour belts, a cruciform tail with
    rudders and elevators, four ducted propellers on outriggers (`Propeller` front left,
    `Propeller_2` front right, `Propeller_3` rear left, `Propeller_4` rear right; left is +X), a
    glazed command gondola with searchlights, and behind it the drone bay: open doors under a rack of
    ten FPV drones (`Muzzle_missile` at the opening). A twin autocannon `Turret` hangs under the
    nose on a pylon, a quad flak gun turns on `Mount_mg` on the back. Origin at the envelope centre
    (it flies)."""
    skin = a.part('Envelope', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    plates = a.part('Plates', 'Team')
    skin.lathe(ENVELOPE, rot=BACKWARD, seg=32)
    # Nose cap with the mooring spike; tail cone with the stern light.
    armor.lathe([(0, -13.68), (.32, -13.56), (1.36, -13.3), (1.7, -13.0), (1.62, -12.94), (0, -12.94)], rot=BACKWARD,
                seg=20)
    steel.cyl(.12, .5, r2=.04, loc=(0, -13.85, 0), rot=FORWARD, seg=8, bevel=0)
    armor.lathe([(.66, 13.4), (.62, 13.75), (.3, 14.05), (0, 14.1)], rot=BACKWARD, seg=12)
    a.part('Tail_light', 'TeamGlow').sphere(.1, loc=(0, 14.1, 0), seg=8, rings=5)
    # Armour: a dark spine of plates along the top, team-painted flank plates, dark side belts.
    step = 2.45
    for i in range(8):
        y0 = -10.4 + i * step
        _env_plate(armor, y0, y0 + step - .08, -.46, .46, na=5)
        for s in (-1, 1):
            _env_plate(plates, y0 + step / 2, min(y0 + step * 1.5 - .08, 10.2), s * .56, s * 1.08, na=4)
    for i in range(6):
        y0 = -9.0 + i * 2.7
        for s in (-1, 1):
            _env_plate(armor, y0, y0 + 2.62, s * 1.2, s * 1.72, na=4, out=.07, inn=.035)
    # Cruciform tail: side fins with elevators, top and bottom fins with rudders.
    fin = Planform(0, 5.6, 7.0, 10.4, 6.2, 2.6, .42, .14)
    moving = a.part('Control_surfaces', 'Armor')
    for frame in (RIGHT, LEFT):
        _wing(skin, moving, fin, frame, cs=[(3.3, 5.4, .7)], lower=1.0, bevel=.02)
    for up in (0.0, math.pi):
        _wing(skin, moving, fin, _upright(0, 0, up), cs=[(3.3, 5.4, .7)], lower=1.0, bevel=.02)
    glow = a.part('Nav_lights', 'TeamGlow')
    for s in (-1, 1):
        glow.box((.08, .3, .1), loc=(s * 5.62, 11.7, 0), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.12, loc=(0, 11.8, 5.64), seg=8, rings=5)
    # Four ducted propellers on outriggers.
    for pivot, x, y in (('Propeller', 5.6, -3.5), ('Propeller_2', -5.6, -3.5), ('Propeller_3', 5.6, 6.0),
                        ('Propeller_4', -5.6, 6.0)):
        _ducted_fan(a, pivot, x, y, -.8)
    # Command gondola under the front of the envelope: bridge windscreen, side windows, armour.
    hull = a.part('Gondola', 'Team')
    rings = [_sec6(-7.5, .5, -4.7, 1.05, -4.25, 1.0, -3.3), _sec6(-6.9, .95, -5.35, 1.4, -4.45, 1.25, -3.3),
             _sec6(-2.0, .95, -5.35, 1.4, -4.45, 1.25, -3.3), _sec6(-1.3, .7, -5.0, 1.2, -4.4, 1.1, -3.3)]
    hull.loft(rings, bevel=.05, seg=1)
    glass = a.part('Windows', 'Glass')
    glass.box((1.7, .03, .32), loc=(0, -7.51, -3.98), bevel=0)                                 # bridge windscreen
    frame = a.part('Window_frames', 'Armor')
    for x in (-.45, .45):
        frame.box((.06, .07, .4), loc=(x, -7.52, -3.98), bevel=0)
    frame.box((1.9, .05, .06), loc=(0, -7.54, -3.78), bevel=0)                                 # visor brow
    fx, fz, lean = _flank((1.4, -4.45), (1.25, -3.3), .3, .012)
    px, pz, plean = _flank((.95, -5.35), (1.4, -4.45), .52, .025)
    for s in (-1, 1):
        glass.box((.03, .5, .3), loc=(s * 1.24, -7.2, -3.98), rot=(0, 0, s * -.62), bevel=0)  # bridge corners
        for y in (-6.3, -5.55, -4.8, -4.05, -3.3, -2.55):
            glass.box((.03, .52, .26), loc=(s * fx, y, fz), rot=(0, -s * lean, 0), bevel=0)
        for y, L in ((-5.4, 2.6), (-2.75, 1.5)):                                              # lower armour
            armor.box((.06, L, .56), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.015, seg=1)
            steel.bolts([(s * (px + .035), y + d, pz + dz) for d in (-L / 2 + .12, L / 2 - .12) for dz in (-.18, .18)],
                        r=.03, h=.03, rot=(0, R90, 0), seg=6, bevel=0)
        steel.tube([(s * 1.46, -6.6, -4.42), (s * 1.46, -2.2, -4.42)], .025, seg=5)           # handrail
        _searchlight(a, (s * .72, -7.2, -5.1), yaw=s * -.25, pitch=.3, r=.18)
    armor.cyl(.08, .16, loc=(0, -6.6, -5.38), seg=8, bevel=0)                                  # sensor ball
    armor.sphere(.22, loc=(0, -6.6, -5.55), seg=12, rings=8)
    a.part('Sensor', 'Glass').cyl(.09, .04, loc=(0, -6.8, -5.57), rot=FORWARD, seg=10, bevel=0)
    steel.box((.16, 4.4, .1), loc=(0, -3.9, -5.38), bevel=0)                                   # keel skid
    a.part('Lamps', 'Lamp').box((.34, .04, .08), loc=(0, -7.53, -4.45), bevel=0)
    steel.cyl(.012, 1.2, loc=(.55, -2.3, -5.9), seg=5, bevel=0)                                # trailing aerial
    # Drone bay behind the gondola: walls, dark roof, open doors, hazard-striped sills, drone racks.
    bay = a.part('Bay', 'Armor')
    yb = 2.3
    for s in (-1, 1):
        bay.box((.1, 6.4, 1.9), loc=(s * 1.6, yb, -3.65), bevel=.02, seg=1)
    for y in (yb - 3.2, yb + 3.2):
        bay.box((3.2, .1, 1.9), loc=(0, y, -3.65), bevel=.02, seg=1)
    dark.box((3.1, 6.2, .04), loc=(0, yb, -3.85), bevel=0)
    stripe = a.part('Bay_sills', 'SafetyStripe')
    bars = a.part('Bay_sill_bars', 'Charred')
    doors = a.part('Bay_doors', 'Team')
    for s in (-1, 1):
        stripe.box((.14, 6.42, .12), loc=(s * 1.6, yb, -4.62), bevel=0)
        for k in range(8):
            bars.box((.16, .12, .15), loc=(s * 1.6, yb - 3.0 + k * .85, -4.62), rot=(.6, 0, 0), bevel=0)
        c = Vector((s * 1.66, yb, -4.62)) + Vector((s * math.sin(.35), 0, -math.cos(.35))) * .62
        doors.box((.05, 6.2, 1.2), loc=tuple(c), rot=(0, -s * .35, 0), bevel=.01, seg=1)
    for y in (yb - 3.2, yb + 3.2):
        stripe.box((3.4, .14, .12), loc=(0, y, -4.6), bevel=0)
    rails = a.part('Racks', 'Steel')
    for x in (-.78, .78):
        rails.box((.1, 6.1, .1), loc=(x, yb, -3.92), bevel=0)
        for k in range(5):
            _fpv_drone(a, x, yb + (k - 2) * 1.2, -4.16, k)
    a.pivot('Muzzle_missile', (0, yb, -4.62))
    _searchlight(a, (0, yb + 3.36, -4.35), yaw=math.pi, pitch=.3, r=.16)
    # Twin autocannon turret under the nose, on a pylon low enough to clear the envelope all round.
    yt = -10.8
    armor.prism([(yt - .7, -2.6), (yt + .7, -2.6), (yt + .4, -3.5), (yt - .4, -3.5)], .5, bevel=.03)   # pylon
    steel.cyl(.62, .1, loc=(0, yt, -3.5), seg=16, bevel=0)                                        # turret ring
    t = a.pivot('Turret', (0, yt, -3.55))
    tb = a.part('Turret_body', 'Team', t)
    tb.cyl(.72, .5, r2=.6, loc=(0, 0, -.28), rot=(math.pi, 0, 0), seg=16, bevel=.05)
    tb.sphere((.58, .58, .25), loc=(0, 0, -.5), seg=16, rings=6, rot=(math.pi, 0, 0), cut=0)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.8, .5, .46), loc=(0, -.55, -.38), bevel=.05, seg=1)                                # mantlet
    a.part('Turret_sight', 'Glass', t).box((.2, .04, .1), loc=(.3, -.81, -.2), bevel=0)
    tips = []
    for x, suffix in ((-.2, ''), (.2, '_2')):
        tips.append(_gun(a, t, x, -.72, -.38, 1.7, .065, suffix=suffix, seg=10, sleeves=((.35, .2, .09),),
                         brake=(.36, .09, 2), brake_seg=10))
    a.pivot('Muzzle_main', tuple((Vector(tips[0]) + Vector(tips[1])) / 2), t)
    # Quad flak gun on the back, on its own mount.
    zt = _env_r(-4.8)
    armor.cyl(1.2, .2, loc=(0, -4.8, zt + .08), seg=18, bevel=.03, bseg=1)                        # mount base
    m = a.pivot('Mount_mg', (0, -4.8, zt + .19))
    fb = a.part('Flak_body', 'Team', m)
    fb.cyl(1.05, .26, loc=(0, 0, .13), seg=18, bevel=.04, bseg=1)
    fb.box((1.35, 1.2, .66), loc=(0, .08, .58), bevel=.07, seg=1, taper=(.85, .9))
    a.part('Flak_shield', 'Armor', m).box((1.75, .1, .74), loc=(0, -.62, .64), rot=(-.25, 0, 0), bevel=.025, seg=1,
                                           taper=(.85, 1))
    a.part('Flak_sight', 'Glass', m).box((.22, .14, .12), loc=(.45, -.62, .88), rot=(-.25, 0, 0), bevel=0)
    flak = a.part('Flak_guns', 'Steel', m)
    for x in (-.3, .3):
        for z in (.5, .76):
            flak.cyl(.045, 2.0, loc=(x, -1.45, z), rot=FORWARD, seg=6, bevel=0)
            flak.cyl(.065, .2, loc=(x, -2.43, z), rot=FORWARD, seg=6, bevel=0)
    for s in (-1, 1):
        a.part('Flak_ammo', 'Crate', m).box((.3, .6, .4), loc=(s * .8, .25, .55), bevel=.03, seg=1)
    a.pivot('Muzzle_mg', (0, -2.55, .63), m)
    # Dorsal details: handrails along the armoured spine, searchlights, antennas, a hatch.
    ys = [-10.4] + [y for _, y in ENVELOPE if -10.4 < y < 9.2] + [9.2]
    for s in (-1, 1):
        steel.tube([(s * (_env_r(y) + .45) * math.sin(.5), y, (_env_r(y) + .45) * math.cos(.5)) for y in ys], .025,
                   seg=4)
        for i in range(9):
            y = -10.4 + i * 2.45 - .04 if i < 8 else 9.2
            r = _env_r(y)
            steel.limb((s * (r + .02) * math.sin(.5), y, (r + .02) * math.cos(.5)),
                       (s * (r + .46) * math.sin(.5), y, (r + .46) * math.cos(.5)), .04, .04, bevel=0)
        _searchlight(a, (s * .9, -8.2, _env_r(-8.2) * math.cos(.25) + .2), yaw=s * .3, pitch=.15, r=.18, up=False)
    for y in (1.2, 6.5):
        _antenna(a, None, .3, y, _env_r(y) + .02, 1.4)
    a.part('Hatch', 'Armor').cyl(.35, .1, loc=(0, 3.6, _env_r(3.6) + .09), seg=12, bevel=.02, bseg=1)
    # Armour ring round the nose and plates between the tail fins.
    for k in range(4):
        a0 = -2.2 + k * 1.1
        _env_plate(armor, -12.3, -10.55, a0 + .04, a0 + 1.06, na=4, out=.07, inn=.04)
    for a0, a1 in ((.18, 1.39), (1.75, 2.96)):
        for s in (-1, 1):
            _env_plate(plates, 10.45, 12.0, s * a0, s * a1, na=4, out=.06, inn=.03)


def _ducted_fan(a, pivot, x, y, z, r=1.2):
    """Engine pod on an outrigger at (x, y, z): a Team nacelle with an exhaust, a ducted five-blade
    pusher propeller on `pivot` (spins about local Y) with stators behind it, a strut and a brace
    back to the envelope."""
    s = 1 if x > 0 else -1
    nac = a.part('Nacelles', 'Team')
    nac.lathe([(0, y - 1.5), (.3, y - 1.35), (.45, y - 1.0), (.48, y - .2), (.4, y + .6), (.3, y + 1.3)],
              loc=(x, 0, z), rot=BACKWARD, seg=12)
    a.part('Exhaust_glow', 'Alloy').cyl(.1, .06, loc=(x + s * .44, y - .4, z + .12), rot=(0, s * R90, 0), seg=8,
                                        bevel=0)
    a.part('Exhaust_stubs', 'Steel').cyl(.14, .16, loc=(x + s * .4, y - .4, z + .12), rot=(0, s * R90, 0), seg=8,
                                         bevel=0)
    a.part('Nacelle_scoops', 'Armor').box((.36, .5, .2), loc=(x, y - .75, z + .4), bevel=.04, seg=1, taper=(.9, .8))
    a.part('Undercarriage', 'Undercarriage').box((.26, .04, .1), loc=(x, y - 1.0, z + .42), bevel=0)
    _revolve(a.part('Nacelle_bands', 'Armor'), [(.46, -.08), (.505, -.07), (.505, .07), (.46, .08)], (x, y - .35, z),
             BACKWARD, 12)
    _revolve(a.part('Ducts', 'Armor'), [(r + .06, -.55), (r + .2, -.45), (r + .2, .45), (r + .06, .55)],
             (x, y + .85, z), BACKWARD, 20)
    _revolve(a.part('Duct_bands', 'Hazard'), [(r + .18, -.06), (r + .22, -.06), (r + .22, .06), (r + .18, .06)],
             (x, y + .5, z), BACKWARD, 20)
    stat = a.part('Stators', 'Steel')
    for k in range(4):
        ang = math.pi / 4 + k * R90
        stat.box((r - .2, .08, .05), loc=(x + math.cos(ang) * (r / 2 + .16), y + 1.25, z + math.sin(ang) * (r / 2 + .16)),
                 rot=(0, -ang, 0), bevel=0)
    root = _env_r(y) * .8
    a.part('Outriggers', 'Armor').limb((s * root, y, z), (x - s * .3, y, z), .22, .9, bevel=.04, seg=1)
    a.part('Outriggers', 'Armor').limb((s * root * .85, y + .3, z - 1.4), (x - s * .25, y - .2, z - .25), .12, .12,
                                       bevel=0)
    p = a.pivot(pivot, (x, y + .85, z))
    a.part(f'{pivot}_hub', 'Steel', p).lathe([(.3, -.2), (.3, .1), (.2, .3), (0, .45)], rot=BACKWARD, seg=10)
    bl = a.part(f'{pivot}_blades', 'Armor', p)
    for k in range(5):
        _prop_blade(bl, k * math.tau / 5, .22, r - .03, .34, .22, .08, .03, .8, .35)


# ----------------------------------------------------------------------------- nuke train and icbm
ICBM_LENGTH, ICBM_R = 9.7, .75


def _cyl_decal_ring(r, yc, ac, u, v, rad):
    """Point of a decal drawn in a flat (u along Y, v round the body) plane, wrapped onto a body of
    revolution about Y at radius `rad`; the decal is centred at y = yc and angle ac (0 = top,
    positive towards +X)."""
    ang = ac + v / r
    return (rad * math.sin(ang), yc + u, rad * math.cos(ang))


def _trefoil_wrapped(sign, blades, r, yc, ac, size, parent_out=.03, seg=4, na=5):
    """Radiation sign wrapped onto a body of radius r about Y: a yellow square plate standing
    `parent_out` proud and three black trefoil blades with a centre dot raised 1 cm on it."""
    h = size / 2
    _env_plate(sign, yc - h, yc + h, ac - h / r, ac + h / r, out=parent_out, inn=.015, na=na, bevel=0,
               prof=[(r, yc - 50), (r, yc + 50)])
    top, bot = r + parent_out + .012, r + parent_out - .005
    rin, rout = size * .12, size * .42
    for k in range(3):
        t0 = math.pi / 2 + k * math.tau / 3 - math.pi / 6
        rings = []
        for i in range(seg + 1):
            t = t0 + (math.pi / 3) * i / seg
            ring = []
            for rho, rad in ((rin, top), (rout, top), (rout, bot), (rin, bot)):
                ring.append(_cyl_decal_ring(r, yc, ac, rho * math.sin(t), rho * math.cos(t), rad))
            rings.append(ring)
        blades.loft(rings, bevel=0)
    blades.cyl(size * .08, .04, loc=_cyl_decal_ring(r, yc, ac, 0, 0, r + parent_out), rot=(0, ac, 0), seg=8, bevel=0)


def _trefoil_flat(sign, blades, loc, face, size):
    """Radiation sign on a flat wall at x facing +X or -X (face = 1 / -1): a yellow square plate half
    sunk in the wall and black trefoil blades with a centre dot standing 1 cm proud of it."""
    x, y, z = loc
    sign.box((.05, size, size), loc=(x, y, z), bevel=0)
    rin, rout = size * .12, size * .42
    for k in range(3):
        t0 = math.pi / 2 + k * math.tau / 3 - math.pi / 6
        arc = [t0 + (math.pi / 3) * i / 4 for i in range(5)]
        prof = [(y + rout * math.cos(t), z + rout * math.sin(t)) for t in arc]
        prof += [(y + rin * math.cos(t), z + rin * math.sin(t)) for t in reversed(arc)]
        blades.prism(prof, .02, loc=(x + face * .03, 0, 0), axis='X', bevel=0)
    blades.cyl(size * .08, .03, loc=(x + face * .035, y, z), rot=ACROSS, seg=8, bevel=0)


def _icbm(a, parent=None, seg=20, detail=True):
    """ICBM-style missile centred on the origin (of `parent`), nose at -Y: a red warhead shroud over
    the white stage stack, yellow interstage bands between black rings, radiation signs on both
    flanks, a cable raceway, four small tail fins round the flared aft skirt and a nozzle bell in
    the base."""
    L, r = ICBM_LENGTH, ICBM_R
    h = L / 2
    a.part('Icbm_warhead', 'BarrelRed', parent).lathe(
        [(0, -h), (.18, -h + .15), (.38, -h + .5), (.56, -h + 1.0), (.68, -h + 1.55), (.74, -h + 2.05), (r, -h + 2.3)],
        rot=BACKWARD, seg=seg)
    body = a.part('Icbm_body', 'Fuel', parent)
    body.lathe([(r, -h + 2.3), (r, h - .9)], rot=BACKWARD, seg=seg)
    a.part('Icbm_skirt', 'Armor', parent).lathe([(r, h - .9), (.8, h - .55), (.84, h), (.5, h)], rot=BACKWARD,
                                                 seg=seg)
    bands = a.part('Icbm_bands', 'Hazard', parent)
    rings = a.part('Icbm_rings', 'Charred', parent)
    for y in ((-h + 2.35, .2, 2.9) if detail else (.2,)):
        _revolve(bands, [(r - .02, y - .16), (r + .018, y - .15), (r + .018, y + .15), (r - .02, y + .16)], (0, 0, 0),
                 BACKWARD, seg)
        for dy in ((-.2, .2) if detail and y > -1 else ()):
            _revolve(rings, [(r - .03, y + dy - .035), (r + .026, y + dy - .03), (r + .026, y + dy + .03),
                             (r - .03, y + dy + .035)], (0, 0, 0), BACKWARD, seg)
    sign, blades = a.part('Icbm_signs', 'SafetyStripe', parent), a.part('Icbm_trefoils', 'Charred', parent)
    for ac in (R90, -R90):
        _trefoil_wrapped(sign, blades, r, -1.1, ac, .8, seg=4 if detail else 1, na=5 if detail else 3)
    if detail:
        _env_plate(a.part('Icbm_raceway', 'Armor', parent), -h + 2.6, h - 1.1, -.07, .07, out=.04, inn=.02, na=3,
                   bevel=0, prof=[(r, -h), (r, h)])
    fins = a.part('Icbm_fins', 'Armor', parent)
    for k in range(4):
        _trap_fin(fins, (0, h - 1.15, 0), math.pi / 4 + k * R90, r * .9, .42, 1.0, .5, .45, .05)
    if detail:
        a.part('Icbm_base', 'Undercarriage', parent).cyl(.52, .04, loc=(0, h - .03, 0), rot=FORWARD, seg=seg, bevel=0)
    a.part('Icbm_nozzle', 'Steel', parent).lathe([(.3, h - .2), (.34, h - .01), (.44, h + .12), (.4, h + .12),
                                                  (.28, h + .02)], rot=BACKWARD, seg=max(10, seg // 2))


def icbm(a):
    """The nuke train's missile as a projectile (nose at -Y, origin at its centre) with a glowing
    motor in the nozzle."""
    _icbm(a, None, seg=12, detail=False)
    h = ICBM_LENGTH / 2
    a.part('Motor', 'Alloy').cyl(.3, .04, loc=(0, h + .03, 0), rot=FORWARD, seg=12, bevel=0)


def nuke_train(a):
    """Armoured diesel locomotive (front) coupled to a missile wagon as one rigid model, 22 m over the
    buffers, on 1.435 m gauge wheelsets. The locomotive has a V plough, twin headlamps, a wedge cab
    with vision slits, an MG cupola on the cab roof (`Mount_mg`) and a twin flak `Turret` on the hood.
    The wagon carries a launch-control cabin and, in an armoured trough, one huge ICBM-style missile
    on an erector (`Erector`, hinged at the rear, rotating about local X; rest pose lowered) with the
    missile under `Icbm_payload`. Hazard chevrons and radiation signs on the wagon and missile."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    glass = a.part('Vision_slits', 'Glass')
    # ---- locomotive: y -10.62 .. -1.58 over the headstocks.
    for y in (-8.55, -3.65):
        _bogie(a, y, 3, 1.1, .5, 3.2)
    _underframe(a, -10.62, -1.58)
    hull.loft([_sec6(-10.45, 1.5, 1.34, 1.5, 1.85, .9, 2.25), _sec6(-9.7, 1.62, 1.34, 1.62, 2.05, 1.2, 2.95),
               _sec6(-9.0, 1.62, 1.34, 1.62, 2.25, 1.22, 3.45), _sec6(-7.3, 1.62, 1.34, 1.62, 2.25, 1.22, 3.45),
               _sec6(-7.0, 1.62, 1.34, 1.62, 2.1, 1.18, 3.05), _sec6(-2.3, 1.62, 1.34, 1.62, 2.1, 1.18, 3.05),
               _sec6(-1.75, 1.57, 1.34, 1.57, 2.05, 1.1, 2.75)], bevel=.06, seg=2)
    armor.loft([[(-.35, -10.99, .15), (.35, -10.99, .15), (1.3, -10.69, .15), (1.4, -10.42, .15), (-1.4, -10.42, .15),
                 (-1.3, -10.69, .15)],
                [(-.3, -10.67, .95), (.3, -10.67, .95), (1.2, -10.52, .95), (1.35, -10.37, .95), (-1.35, -10.37, .95),
                 (-1.2, -10.52, .95)]], bevel=.03, seg=1)                                         # V plough
    for s in (-1, 1):
        _headlamp(a, (s * .78, -10.46, 1.68), r=.15)
        a.part('Lamps', 'Lamp').box((.14, .04, .1), loc=(s * 1.05, -10.465, 1.95), bevel=0)
    gy, gz, grot = _glacis((-9.7, 2.95), (-9.0, 3.45), .55, .012)
    for x in (-.72, 0, .72):
        glass.box((.5, .1, .04), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
    gy, gz, grot = _glacis((-9.7, 2.95), (-9.0, 3.45), .82, .03)
    armor.box((2.2, .2, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)                  # slit brow
    gy, gz, grot = _glacis((-10.45, 2.25), (-9.7, 2.95), .5, .012)
    glass.box((.7, .1, .04), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=0)                            # driver slit
    fx, fz, flean = _flank((1.62, 2.25), (1.22, 3.45), .6, .012)
    for s in (-1, 1):
        for y in (-8.55, -7.75):
            glass.box((.03, .5, .1), loc=(s * fx, y, fz), rot=(0, -s * flean, 0), bevel=0)
        fbox(armor, '+x' if s > 0 else '-x', (s * 1.62, -7.9, 1.72), (.62, .05, .7), out=.02, bevel=.01)  # cab door
        steel.box((.04, .04, .5), loc=(s * 1.68, -7.5, 1.8), bevel=0)
        for y in (-8.55, -3.65):                                                               # bogie skirts
            armor.box((.06, 3.3, .8), loc=(s * 1.665, y, 1.1), bevel=.015, seg=1)
            _plate_bolts(steel, s * 1.7, [y + d for d in (-1.4, -.7, 0, .7, 1.4)], 1.4, r=.028)
        for y in (-6.9, -4.2):
            armor.box((.04, .07, .64), loc=(s * 1.635, y, 1.7), bevel=0)                        # plate seams
        dark.grille(1.1, .5, loc=(s * 1.64, -5.55, 1.72), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
        dark.grille(1.1, .5, loc=(s * 1.64, -2.9, 1.72), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
        px, pz, plean = _flank((1.62, 2.1), (1.18, 3.05), .64, .025)
        for y in (-6.3, -5.0, -3.7, -2.4):                                                    # hood plates
            armor.box((.06, 1.2, .5), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.015, seg=1)
            _plate_bolts(steel, s * (px + .03), (y - .5, y + .5), pz + .2, r=.025, h=.03)
        hx, hz, _ = _flank((1.62, 2.1), (1.18, 3.05), .3, .09)
        steel.tube([(s * hx, -6.8, hz), (s * hx, -2.0, hz)], .025, seg=5)
        for y in (-6.5, -4.4, -2.3):
            steel.box((.03, .03, .1), loc=(s * (hx - .04), y, hz - .03), bevel=0)
    # Hood roof: radiator grilles over fans ahead of and behind the turret, exhaust stacks, horn.
    for y, d in ((-6.6, .6), (-2.9, .5)):
        a.part('Fans', 'Rubber').cyl(d * .45, .04, loc=(0, y, 3.07), seg=14, bevel=0)
        dark.grille(1.3, d, loc=(0, y, 3.1), rot=(-R90, 0, 0), slats=4, depth=.07, thickness=.035)
    for s in (-1, 1):
        steel.cyl(.12, .45, loc=(s * .6, -2.35, 3.2), seg=10, bevel=0)                          # z 2.98 .. 3.43
        a.part('Soot', 'Charred').cyl(.135, .05, loc=(s * .6, -2.35, 3.42), seg=10, bevel=0)
    steel.box((.06, .06, .1), loc=(-.55, -9.3, 3.49), bevel=0)
    steel.cyl(.05, .3, loc=(-.55, -9.3, 3.56), rot=FORWARD, r2=.09, seg=8, bevel=0)                 # horn
    armor.box((.7, .5, .1), loc=(-.5, -7.6, 3.48), bevel=.02, seg=1)                              # cab roof hatch
    _antenna(a, None, -1.4, -2.6, 2.55, 1.2)                                               # clear of the flak sweep
    # Twin flak turret on the hood; each barrel is the highest thing in its sweep (tips 4.4 m).
    armor.cyl(1.25, .14, loc=(0, -4.9, 3.06), seg=24, bevel=.02, bseg=1)                          # ring z 2.99 .. 3.13
    t = a.pivot('Turret', (0, -4.9, 3.13))
    tb = a.part('Turret_body', 'Team', t)
    outline = [(-.9, 1.2), (.9, 1.2), (1.15, .6), (1.15, -.55), (.75, -1.05), (-.75, -1.05), (-1.15, -.55), (-1.15, .6)]
    tb.prism(outline, .85, loc=(0, 0, .45), axis='Z', bevel=.06, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.1, .42, .62), loc=(0, -1.05, .52), rot=(-.21, 0, 0), bevel=.05, seg=1)           # mantlet
    tips = []
    for x, suffix in ((-.3, ''), (.3, '_2')):
        tips.append(_gun(a, t, x, -1.2, .55, 2.8, .075, pitch=.21, suffix=suffix, seg=10,
                         sleeves=((.2, .35, .12), (.62, .06, .09)), brake=(.45, .11, 3), brake_seg=10))
    a.pivot('Muzzle_main', tuple((Vector(tips[0]) + Vector(tips[1])) / 2), t)
    for s in (-1, 1):
        a.part('Ammo_drums', 'Crate', t).box((.3, .8, .46), loc=(s * 1.2, .15, .48), bevel=.04, seg=1)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.06, .5, loc=(-.5, .8, 1.1), seg=8, bevel=0)                                        # dish mast
    _dish(a.part('Fire_control_dish', 'Armor', t), (-.5, .75, 1.45), .38, .3, depth=.14, seg=12, tilt=.3)
    a.part('Hatch', 'Armor', t).cyl(.26, .06, loc=(.45, .5, .9), seg=14, bevel=.02, bseg=1)
    a.part('Sight', 'Glass', t).box((.26, .04, .12), loc=(.62, -.77, .95), bevel=0)
    tsteel.box((.34, .3, .22), loc=(.62, -.62, .95), bevel=.03)
    # MG cupola on the cab roof, on its own mount (top 3.95 m, under the flak barrels).
    armor.cyl(.56, .1, loc=(.45, -8.3, 3.48), seg=16, bevel=.02, bseg=1)
    m = a.pivot('Mount_mg', (.45, -8.3, 3.53))
    cup = a.part('MG_cupola', 'Team', m)
    cup.cyl(.46, .26, loc=(0, 0, .14), seg=16, bevel=.04)
    cup.sphere((.4, .4, .16), loc=(0, 0, .26), seg=16, rings=8, cut=0)
    a.part('MG_armor', 'Armor', m).box((.32, .24, .2), loc=(0, -.4, .16), bevel=.03, seg=1)
    a.part('MG_glass', 'Glass', m).box((.16, .05, .06), loc=(.2, -.38, .32), rot=(0, 0, .45), bevel=0)
    mg = a.part('MG_gun', 'Steel', m)
    mg.cyl(.032, .72, loc=(0, -.85, .16), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.045, .12, loc=(0, -1.18, .16), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.25, .16), m)

    # ---- missile wagon: y -0.82 .. 10.62 over the headstocks.
    for y in (1.3, 8.5):
        _bogie(a, y, 2, 1.8, .46, 2.7)
    _underframe(a, -.82, 10.62)
    steel.box((.1, .5, .08), loc=(0, -1.2, 1.1), bevel=0)                                          # screw coupling
    trough = [(-1.6, 1.34), (1.6, 1.34), (1.62, 2.2), (1.35, 2.7), (1.02, 2.7), (1.02, 2.05), (-1.02, 2.05),
              (-1.02, 2.7), (-1.35, 2.7), (-1.62, 2.2)]
    hull.loft([[(x, y, z) for x, z in trough] for y in (-.65, 10.45)], bevel=.04, seg=1)
    dark.box((2.0, 10.3, .04), loc=(0, 4.9, 2.06), bevel=0)                                        # trough liner
    fx, fz, flean = _flank((1.62, 2.2), (1.35, 2.7), .5, .015)
    stripe, bars = a.part('Chevrons', 'SafetyStripe'), a.part('Chevron_bars', 'Charred')
    sign, blades = a.part('Signs', 'SafetyStripe'), a.part('Trefoils', 'Charred')
    for s in (-1, 1):
        for y in (1.3, 8.5):                                                                  # bogie skirts
            armor.box((.06, 2.9, .8), loc=(s * 1.665, y, 1.1), bevel=.015, seg=1)
            _plate_bolts(steel, s * 1.7, [y + d for d in (-1.2, -.4, .4, 1.2)], 1.4, r=.028)
        # Hazard chevrons along the upper chamfer, radiation signs on the side walls.
        for y0, y1 in ((.1, 3.4), (6.6, 10.1)):
            stripe.box((.04, y1 - y0, .3), loc=(s * fx, (y0 + y1) / 2, fz), rot=(0, -s * flean, 0), bevel=0)
            n = int((y1 - y0) / .5)
            for k in range(n):
                yk = y0 + (k + .5) * (y1 - y0) / n
                bars.box((.04, .12, .34), loc=(s * (fx + .012), yk, fz + .003), rot=(.6 * s, -s * flean, 0),
                         bevel=0)
        _trefoil_flat(sign, blades, (s * 1.62, 5.0, 1.78), s, .72)
        for y in (4.1, 5.9):                                                                  # side armour seams
            armor.box((.04, .07, .8), loc=(s * 1.635, y, 1.76), bevel=0)
        a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.3, 10.465, 2.3), bevel=0)
    # Launch-control cabin at the front of the wagon: vents, slits, datalink dish, beacons.
    cab = a.part('Control_cabin', 'Team')
    cab.box((3.1, 1.25, 2.05), loc=(0, -.1, 2.35), bevel=.06, seg=1, taper=(1, .7), shift=(0, -.18))
    for s in (-1, 1):
        glass.box((.03, .45, .1), loc=(s * 1.56, -.2, 2.95), bevel=0)
        a.part('Warning_lights', 'Alloy').cyl(.09, .14, loc=(s * 1.1, -.35, 3.43), seg=8, bevel=0)
    dark.grille(1.4, .5, loc=(0, -.73, 2.3), slats=4, depth=.05, thickness=.035)
    _dish(a.part('Datalink', 'Steel'), (.55, -.4, 3.55), .3, .3, depth=.1, seg=10, tilt=.6)
    steel.cyl(.05, .25, loc=(.55, -.35, 3.43), seg=6, bevel=0)
    _antenna(a, None, -.6, -.5, 3.38, 1.2)
    _trefoil_flat(sign, blades, (1.55, -.05, 2.2), 1, .5)
    _trefoil_flat(sign, blades, (-1.55, -.05, 2.2), -1, .5)
    # Erector: hinge brackets and pin at the rear (static), the cradle and missile on `Erector`.
    for s in (-1, 1):
        armor.box((.18, .8, .75), loc=(s * .92, 10.2, 2.35), bevel=.03, seg=1)                     # z 1.98 .. 2.73
    steel.cyl(.12, 2.06, loc=(0, 10.25, 2.4), rot=ACROSS, seg=10, bevel=0)                         # hinge pin
    e = a.pivot('Erector', (0, 10.25, 2.4))
    cradle = a.part('Erector_frame', 'Steel', e)
    for x in (-.42, .42):
        cradle.box((.14, 9.3, .22), loc=(x, -4.7, .22), bevel=.02, seg=1)                       # strongback
    cradle.box((1.5, .5, .5), loc=(0, -.1, .18), bevel=.04, seg=1)                              # hinge knuckle
    ecl = a.part('Erector_clamps', 'Armor', e)
    for y in (-8.3, -5.9, -3.4, -1.6):
        ecl.box((1.4, .3, .32), loc=(0, y, .26), bevel=.03, seg=1)                                 # saddles
    for y in (-6.25, -3.25):
        ecl.cyl(ICBM_R + .05, .22, loc=(0, y, .9), rot=FORWARD, seg=20, bevel=.02, bseg=1)         # clamp bands
    p = a.pivot('Icbm_payload', (0, -ICBM_LENGTH / 2, .9), e)
    _icbm(a, p, seg=20, detail=True)


# name: (builder, Asset options). Aircraft and the airship fly: no ground occlusion or grime.
BUILDERS = {
    'fighter_jet': (fighter_jet, dict(ao_distance=.7, ground=False)),
    'tank_buster': (tank_buster, dict(ao_distance=.7, ground=False)),
    'recon_drone': (recon_drone, dict(ao_distance=.4, ground=False)),
    'heavy_attack_heli': (heavy_attack_heli, dict(ao_distance=.8, grime_height=.5)),
    'drone_mothership': (drone_mothership, dict(ao_distance=1.2, ground=False)),
    'nuke_train': (nuke_train, dict(ao_distance=.8, grime_height=.7)),
    'icbm': (icbm, dict(ao_distance=.3, ground=False)),
}
