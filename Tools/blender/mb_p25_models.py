"""Machine Brigade prompt 25 B2 (DECISIONS 25B2): models rebuilt from the balance sheet's "Hình dạng (cho AI vẽ)" notes
and its drawing guide ("Hướng dẫn vẽ"), at the sheet's target sizes (ground vehicles 0.8 x real, aircraft 0.4 x real).

The guide's rules, as they apply here:
  * silhouette first: every model carries the one or two features its shape note names, big enough to read in a
    black top-down silhouette; the identifying parts (gun, turret, launchers, rotors) are drawn 10-20 % over scale,
    the body is not;
  * sizes are the sheet's, in model units: these models are drawn for a balance.json "scale" of 1.0 (prompt 25 B1
    sets the scales, collision capsules and hull radii from the sizes listed in DECISIONS 25B2);
  * triangle budgets: light vehicles 1,500-3,000, tanks 3,000-5,000, aircraft 2,000-4,000, bosses 15,000-40,000;
    the far detail level (LOD1) is made at runtime (ModelLibrary.Lod), the high-detail `_hd` variants are the same
    builders with detail=True;
  * nothing thinner than 0.1 m that would shimmer on a phone (no whip antennas, grab rails or wire guards);
  * every weapon keeps the pivots and muzzles the game looks up (Turret, Main_cannon*, Muzzle_<slot>, Mount_<slot>,
    Rotor, Tail_rotor ...), and `Point_exhaust` / `Point_fire` empties mark where exhaust smoke and fire belong;
  * Team is the side's colour (and the player's camouflage skin); Armor, Steel and the rest stay neutral; no real
    insignia.

Conventions are mb_vehicles': metres, +Z up, Blender -Y is the front, +X the vehicle's left, origin on the ground at
the hull centre. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).

  * main_battle_tank: a Leopard 2A4 / M1A1-class tank, 7.7 x 3.0 x 2.2 m with its gun forward (hull 5.9 m): a long,
    low hull with a shallow upper glacis, seven road wheels under three-panel side skirts, rear drive; a wide,
    angular turret with arrowhead cheeks, a long bustle and a stowage box; a 120 mm smooth-bore gun reaching
    1.8 m past the nose (a third of the hull), with a thermal sleeve, fume extractor and muzzle collar; the
    commander's panoramic sight, the gunner's sight box, a loader's machine gun, smoke dischargers.

Headless: blender --background --python Tools/blender/build_assets.py -- main_battle_tank
"""
import math

from mathutils import Vector

import mb_detail as hd
import mb_vehicles as mv
from mb_vehicles import ACROSS, R90, TAU


def _lean_tracks(a, x, length, top, wheel_r, wheels, belt_width, sprocket=1, cleat_pitch=.21, wheel_seg=8, teeth=7):
    """Track units drawn for the triangle budget: the belt (a prism round the idler, sprocket and first and last road
    wheels), cleats on the curved ends only (the runs are under the skirts or under the hull), `wheels` road wheels
    (tyre and painted disc; hubs only at high detail), a toothed drive sprocket at the `sprocket` end and an idler at the other. The belt runs
    from `top` to 1 cm below the ground. x is the belt's centre line."""
    belt = a.part('Tracks', 'Undercarriage')
    drive = a.part('Sprockets', 'Armor')
    bottom = -.01
    rb = min(.25, (top - bottom) * .3)
    first = length / 2 - wheel_r - .12
    circles = [(e * (length / 2 - rb), top - rb, rb) for e in (-1, 1)] + \
              [(e * first, bottom + wheel_r, wheel_r) for e in (-1, 1)]
    outline = mv._hull2d([(cy + r * math.cos(k * TAU / 16), cz + r * math.sin(k * TAU / 16))
                          for cy, cz, r in circles for k in range(16)])
    detail = hd.on(a)
    seg = 14 if detail else wheel_seg
    for s in (-1, 1):
        cx = s * x
        face = cx + s * belt_width / 2
        belt.prism(outline, belt_width, loc=(cx, 0, 0), axis='X', bevel=0)
        for (py, pz), (ty, tz) in mv._perimeter(outline, cleat_pitch, .05):
            if abs(py) < first - .02:
                continue
            ny, nz = tz, -ty
            belt.box((belt_width + .04, .07, .05), loc=(cx, py + ny * .012, pz + nz * .012),
                     rot=(math.atan2(tz, ty), 0, 0), bevel=0)
        for i in range(wheels):
            y = -first + i * 2 * first / (wheels - 1)
            a.part('Tyres', 'Undercarriage').cyl(wheel_r, .09, loc=(face - s * .03, y, bottom + wheel_r), rot=ACROSS,
                                                 seg=seg, bevel=0)
            a.part('Wheels', 'Team').cyl(wheel_r * .72, .03, loc=(face + s * .025, y, bottom + wheel_r), rot=ACROSS,
                                         seg=seg, bevel=0)
            if detail:
                a.part('Hubs', 'Steel').cyl(wheel_r * .26, .03, loc=(face + s * .04, y, bottom + wheel_r), rot=ACROSS,
                                            seg=6, bevel=0)
                hd.bolt_ring(a.part('Wheel_bolts', 'Steel'), hd.frame((face + s * .045, y, bottom + wheel_r),
                                                                      hd.side_rot(s)), wheel_r * .48, 6, r=.016, h=.02)
        for end in (-1, 1):
            cy, cz = end * (length / 2 - rb), top - rb
            if end == sprocket:
                drive.cyl(rb * .88, .08, loc=(face - s * .02, cy, cz), rot=ACROSS, seg=12, bevel=0)
                for k in range(teeth):
                    ang = k * TAU / teeth + .2
                    drive.box((.05, .07, .08), loc=(face - s * .01, cy + math.cos(ang) * (rb * .88 + .02),
                                                    cz + math.sin(ang) * (rb * .88 + .02)),
                              rot=(ang + R90, 0, 0), bevel=0)
            else:
                a.part('Tyres', 'Undercarriage').cyl(rb * .92, .09, loc=(face - s * .03, cy, cz), rot=ACROSS, seg=seg,
                                                     bevel=0)
                drive.cyl(rb * .6, .03, loc=(face + s * .025, cy, cz), rot=ACROSS, seg=seg, bevel=0)
            a.part('Hubs', 'Steel').cyl(rb * .3, .035, loc=(face + s * .04, cy, cz), rot=ACROSS, seg=6, bevel=0)


# ----------------------------------------------------------------------------- main battle tank
MBT_HULL = 5.9          # hull length; the gun reaches 1.8 m past the nose: 7.7 m in all
MBT_TURRET = (0, .3, 1.24)


def main_battle_tank(a, detail=False):
    """Main battle tank (Leopard 2A4 / M1A1 class), 7.7 x 3.0 x 2.2 m: see the module notes."""
    hd.mark(a, detail)
    half = MBT_HULL / 2
    _lean_tracks(a, 1.18, 5.72, .86, .27, 7, .5, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    # Lower hull between the tracks, and the upper hull over them: a long shallow glacis, a flat deck, a steep rear.
    armor.prism([(-2.55, .4), (-2.97, .8), (-2.9, .95), (2.88, .95), (2.9, .5), (2.62, .4)], 1.84, bevel=.04, seg=1)
    hull.prism([(-half - .02, .84), (-2.05, 1.18), (2.78, 1.21), (half, 1.08), (half, .88)], 2.9, bevel=.05, seg=1)
    # Three-panel side skirts over the upper run and the tops of the wheels; the first plate is the thick one.
    for s in (-1, 1):
        mv._skirt(a, s, 1.47, -2.82, -1.52, .5, 1.17, 1, thick=.1, bolts=False)
        mv._skirt(a, s, 1.46, -1.49, 2.55, .56, 1.17, 2, thick=.07, bolts=False)
        steel.box((.16, .16, .12), loc=(s * .42, -2.99, .66), bevel=.02, seg=1)                  # tow hooks
        mv._headlight(a, s * 1.12, -2.72, 1.1, guard=False)
        mv._taillight(a, s * 1.1, half + .02, 1.0)
        mv._exhaust(a, s * .5, half + .02, .72, .5, .22)
    # Driver's hatch and vision blocks behind the glacis; the engine deck with its grille, fender bins, rear lights.
    mv._hatch(a, -.45, -1.72, 1.18, .24, handle=False)   # low: the bustle sweeps over it
    mv._periscopes(a, [(-.45 + dx, -2.05, 1.18, 0) for dx in (-.17, 0, .17)])
    deck = a.part('Deck', 'Undercarriage')
    deck.grille(1.5, .9, loc=(0, 1.92, 1.23), rot=(-R90, 0, 0), slats=6, depth=.1, thickness=.05)
    mv._grille_frame(a, 0, 1.92, 1.21, 1.5, .9)
    for s in (-1, 1):
        armor.box((.46, .95, .2), loc=(s * 1.18, 1.95, 1.29), bevel=.03, seg=1)                   # fender bins
        armor.box((.36, .3, .1), loc=(s * .75, .95, 1.24), bevel=.02, seg=1)                     # deck fillers
    steel.cyl(1.02, .1, loc=(MBT_TURRET[0], MBT_TURRET[1], 1.21), seg=16, bevel=0)                # turret ring
    a.pivot('Point_exhaust', (0, half + .1, .75))
    a.pivot('Point_fire', (0, 1.92, 1.25))

    t = a.pivot('Turret', MBT_TURRET)
    turret = a.part('Turret_body', 'Team', t)
    # Plan view: arrowhead cheeks either side of the gun, straight sides, a long bustle.
    outline = [(-.3, -1.5), (.3, -1.5), (1.12, -1.02), (1.2, -.85), (1.2, 1.05), (1.08, 1.72), (.92, 1.9),
               (-.92, 1.9), (-1.08, 1.72), (-1.2, 1.05), (-1.2, -.85), (-1.12, -1.02)]
    turret.prism(outline, .68, loc=(0, 0, .37), axis='Z', bevel=.05, seg=1, taper=.93)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.66, .34, .46), loc=(0, -1.52, .38), bevel=.04, seg=1, taper=(.92, .9))            # gun mantlet
    for s in (-1, 1):                                                                            # cheek add-on plates
        tarm.box((.62, .1, .44), loc=(s * .72, -1.3, .37), rot=(0, 0, s * .54), bevel=.02, seg=1)
    # Bustle stowage box with a rolled tarpaulin, bins on the bustle sides.
    tarm.box((1.62, .34, .42), loc=(0, 2.05, .36), bevel=.03, seg=1)
    a.part('Tarp', 'Canvas', t).cyl(.13, 1.3, loc=(0, 2.02, .7), rot=ACROSS, seg=8, bevel=0)
    for s in (-1, 1):
        tarm.box((.18, 1.1, .4), loc=(s * 1.3, 1.0, .28), bevel=.03, seg=1)                     # bustle bins
        mv._smoke(a, a.part('Smoke', 'Steel', t), 1.07, -.5, .58, s, count=3, gap=.08, r=.05, depth=.15)
    # The commander's panoramic sight (right rear), the gunner's sight box (right front), the loader's hatch.
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.15, .16, loc=(-.62, .2, .78), seg=12, bevel=.02, bseg=1)
    tarm.box((.34, .3, .17), loc=(-.62, .2, .92), bevel=.03, seg=1)
    glass = a.part('Sight', 'Glass', t)
    glass.box((.24, .03, .1), loc=(-.62, .04, .93), bevel=0)
    tarm.box((.36, .42, .24), loc=(-.66, -.95, .8), bevel=.03, seg=1)
    glass.box((.26, .03, .13), loc=(-.66, -1.17, .82), bevel=0)
    mv._hatch(a, .55, .45, .72, .27, parent=t, seg=10)
    mv._periscopes(a, [(.55, .08, .72, 0)], parent=t)
    # 120 mm smooth-bore gun: 1.8 m past the nose, drawn 15 % thick.
    gun = a.part('Main_cannon', 'Steel', t)
    y0, length, z = -1.66, 3.26, .38
    gun.cyl(.085, length, loc=(0, y0 - length / 2, z), rot=(R90, 0, 0), seg=10, bevel=0)
    gun.cyl(.105, length * .62, loc=(0, y0 - length * .36, z), rot=(R90, 0, 0), seg=12, bevel=0)   # thermal sleeve
    gun.cyl(.14, .42, loc=(0, y0 - length * .4, z), rot=(R90, 0, 0), seg=12, bevel=.02, bseg=1)    # fume extractor
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.11, .16, loc=(0, y0 - length - .06, z), rot=(R90, 0, 0), seg=10,
                                                   bevel=.012, bseg=1)                           # muzzle collar
    a.pivot('Muzzle_main', (0, y0 - length - .15, z), t)
    mv._coax(a, t, .42, -1.46, .5, length=.4, housing=.26)
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
        a.part('Turret_seams', 'Armor', t).box((2.0, .025, .014), loc=(0, -.1, .72), bevel=0)


# ----------------------------------------------------------------------------- scaling
def _scale_asset(a, k):
    """Scales everything built so far about the origin by k: the shapes (whose vertices sit in their parent pivot's
    space) and the pivots' offsets (pivots only translate). A builder drawn at another size calls it last."""
    import bmesh
    for shape in a.shapes.values():
        bmesh.ops.scale(shape.bm, vec=(k, k, k), verts=list(shape.bm.verts))
    for o in a.pivots.values():
        o.location = o.location * k


# ----------------------------------------------------------------------------- fighter (Su-27)
FIGHTER_K = 8.8 / 19.2     # drawn in the 19.2 m frame of mb_air3's fighter, then scaled to the sheet's 8.8 m


def fighter_jet(a, detail=False):
    """Air-superiority fighter (Su-27 Flanker class), 8.8 x 5.9 x 2.1 m, clearly longer than the attack jet (6.2 m):
    a long pointed radome with the IRST ball, a bubble canopy far forward, leading-edge root extensions blending
    into a cropped-delta wing, a flat lifting body over two widely spaced engines with raked intakes and
    afterburning nozzles, tail booms carrying the twin fins (drawn 15 % tall: the silhouette's second feature),
    all-moving stabilisers, the tail stinger. Four air-to-air missiles under the wings on separate pylons (the
    `Missiles` the launch points are found from, far enough apart to read as four), two short-range ones on the
    wingtip rails, the cannon in the right wing root. Drawn in mb_air3's 19.2 m frame and scaled by FIGHTER_K; the
    high-detail variant keeps its finer sections, control surfaces and panel lines (mb_air3._fighter_jet_detail)."""
    from mb_air import (BACKWARD, FORWARD, LEFT, RIGHT, Planform, _aam, _aam_parts, _canopy, _dome, _intake,
                        _nozzle, _patch, _pylon, _sec, _skin_z, _surface, _upright, _wing)
    from mb_air3 import _fighter_jet_detail, _sq
    hd.mark(a, detail)
    n = 16 if detail else 12
    bv = 1.0 if detail else 0.0     # bevels are 1 cm or less at this size: only the close-up variant keeps them
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
    armor.cyl(.1, .12, loc=(-.17, -7.15, zi), seg=8, bevel=0)                                  # IRST ball (right)
    a.part('Sensor', 'Glass').sphere(.11, loc=(-.17, -7.17, zi + .07), seg=6, rings=4)
    # Bubble canopy far forward (frameless here: its thin frames would shimmer), the dorsal spine behind it.
    glass = a.part('Canopy', 'Glass')
    st = [(-6.95, .14, .64), (-6.55, .34, .88), (-6.0, .43, 1.02), (-5.3, .45, 1.07), (-4.6, .4, 1.0),
          (-4.1, .27, .87), (-3.75, .13, .72)]
    stations = [(y, w, _skin_z(hull, y, w) - .03, z1) for y, w, z1 in st]
    if detail:
        _canopy(glass, a.part('Canopy_frames', 'Armor'), stations, bows=(-6.5,))
    else:
        glass.loft([_dome(y, w, z0, z1, 7) for y, w, z0, z1 in stations], bevel=0)
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1, 9 if detail else 7) for y, w, z1 in
             ((-4.3, .34, .92), (-3.2, .42, .8), (-1.4, .46, .68), (1.2, .46, .62), (3.8, .4, .56), (6.2, .3, .44))]
    body.loft(spine + [[(0, 7.3, .3)]], bevel=.02 * bv, seg=1)
    _patch(armor, spine, -3.0, -1.7, 1, 5)                                                     # air brake
    # Leading-edge root extensions into the cropped-delta wing.
    lerx = Planform(.45, 2.6, -6.4, -.52, 6.9, 2.0, .14, .08, .06, .04)
    wing = Planform(.9, 6.1, -2.17, 2.51, 5.4, 1.45, .3, .1, .02, -.08)
    for frame in (RIGHT, LEFT):
        _surface(body, lerx, frame, bevel=.01 * bv)
        if detail:
            _wing(body, moving, wing, frame, cs=[(1.95, 3.9, .75), (3.9, 5.75, .74)])
        else:
            _surface(body, wing, frame, bevel=0)
    # Engine nacelles under the lifting body: raked intakes under the root extensions, nozzles.
    lips = a.part('Intake_lips', 'Team')
    m = 10 if detail else 8
    for s in (-1, 1):
        x = s * 1.12
        trunk = [_sq(x, -2.6, -.6, .31, .41, n=m), _sq(x, .5, -.62, .33, .42, p=3.5, n=m),
                 _sq(x, 4.5, -.6, .36, .42, p=3, n=m), _sq(x, 6.6, -.55, .43, .43, p=2.4, n=m),
                 _sq(x, 7.3, -.52, .45, .45, p=2.2, n=m)]
        if detail:
            _intake(a, body, lips, dark, (x, -3.4, -.58), .3, .4, .25, trunk, depth=.3, wall=.07, n=m)
        else:  # the same duct without its bevels
            from mb_air import _squircle
            rot = (R90 + .25, 0, 0)
            fm = hd.frame((x, -3.4, -.58), rot)
            outline = _squircle(.3, .4, m)
            body.loft([[tuple(fm @ Vector((px, py, 0))) for px, py in outline]] + trunk, bevel=0)
            lips.shell(outline, .3, .07, loc=(x, -3.4, -.58), rot=rot, bevel=0)
            dark.box((.48, .64, .03), loc=tuple(fm @ Vector((0, 0, .03))), rot=rot, bevel=0)
        armor.box((.06, 1.0, .5), loc=(s * .8, -3.2, -.42), bevel=0)                          # splitter
        _nozzle(a, x, 7.3, -.52, .42, 1.05, seg=14 if detail else 8, glow=detail)
        if not detail:
            a.part('Exhaust_glow', 'Alloy').cyl(.26, .04, loc=(x, 7.3 + .55, -.52), rot=FORWARD, seg=8, bevel=0)
    # Tail booms carrying the twin fins (15 % tall), stabilisers and ventral fins.
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
        armor.cyl(.07, .6, loc=tuple(tip + Vector((0, .1, 0))), rot=BACKWARD, seg=6, bevel=0)  # fin-tip fairing
        glow.box((.08, .16, .08), loc=tuple(tip + Vector((0, .44, 0))), bevel=0)
        _surface(body, ventral, _upright(x, -.2, math.pi - .3), lower=1.0, bevel=.012 * bv)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame, bevel=.012 * bv)
    body.loft([sec(6.5, .45, -.22, .3), sec(8.0, .28, -.14, .2), sec(8.9, .15, -.08, .1), [(0, 9.4, .0)]],
              bevel=.01 * bv, seg=1)                                                           # tail stinger
    a.part('Beacon', 'TeamGlow').sphere(.08, loc=(0, 9.38, 0), seg=6, rings=4)
    # Cannon in the right wing root (the pilot's right is -X): fairing, barrel, muzzle ring.
    armor.box((.24, 1.3, .16), loc=(-.86, -3.05, .15), bevel=.03, seg=1, taper=(.7, .9))
    steel.cyl(.06, .45, loc=(-.86, -3.82, .15), rot=FORWARD, seg=6, bevel=0)
    steel.cyl(.08, .08, loc=(-.86, -4.04, .15), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_gun', (-.86, -4.1, .15))
    # Wingtip rails with the short-range missiles (a part of their own, not Missiles: they are the aam slot).
    tips = _aam_parts(a, 'Wingtip_missiles')
    for s in (-1, 1):
        x = s * 6.12
        armor.box((.14, 1.7, .14), loc=(x, 3.1, -.08), bevel=.02, seg=1)
        _aam(tips, (s * 6.24, 2.75, -.2), length=2.3, r=.1, seg=6, canards=False, fin=1.3)
        glow.box((.08, .16, .08), loc=(x, 2.2, -.08), bevel=0)
    # Four medium-range missiles under the wings, one per pylon (Muzzle_missile between their noses).
    aams = _aam_parts(a)
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        for x in (s * 2.75, s * 4.3):
            zb = wing.bottom(abs(x)) + .05
            zp = zb - .38
            _pylon(pylons, x, -.1 + abs(x) * .2, 1.7 + abs(x) * .2, zb, zp + .1, w=.14)
            _aam(aams, (x, .45 + abs(x) * .2, zp), length=3.0, r=.12, seg=6, canards=False, fin=1.2)
    zp = wing.bottom(3.5) + .05 - .38
    a.pivot('Muzzle_missile', (0, -.55, zp))      # just ahead of the noses, clear of the belly light (_hd)
    a.pivot('Muzzle_aam', (0, 2.75 - 1.2, -.2))
    a.pivot('Point_exhaust', (0, 8.4, -.52))
    a.pivot('Point_fire', (0, 1.5, .2))
    if detail:
        _fighter_jet_detail(a, hull, spine, lerx, wing, Planform(0, 3.0, 4.3, 6.75, 2.9, 1.05, .13, .05), stab)
    _scale_asset(a, FIGHTER_K)


# name: (builder, Asset options).
BUILDERS = {
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
    'fighter_jet': (fighter_jet, dict(ao_distance=.35, ground=False)),
}
