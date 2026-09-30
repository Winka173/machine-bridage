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
from mb_vehicles import ACROSS, FORWARD, R90, TAU


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
    _battle_tank(a, detail)


TWIN_K = 1.15           # the twin-gun tank: the main battle tank's hull 15 % larger all round (the sheet)


def twin_tank(a, detail=False):
    """Twin-gun tank, 9.0 x 3.5 x 2.6 m: the main battle tank's hull and running gear 15 % larger (the sheet: 'larger
    than the MBT by about 15 %'), under a turret 18 % wider carrying two 120 mm guns side by side behind one broad
    mantlet, the coaxial gun between them: from above, the two long parallel barrels are the silhouette.
    `Main_cannon` / `Main_cannon_2` and `Muzzle_brake` / `_2` recoil in turn; `Muzzle_main` sits between the tips."""
    _battle_tank(a, detail, twin=True)
    _scale_asset(a, TWIN_K)


def _battle_tank(a, detail=False, twin=False):
    """The main battle tank; twin=True gives the twin-gun tank's wide turret and guns (twin_tank scales it)."""
    hd.mark(a, detail)
    w = 1.18 if twin else 1
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
    if twin:  # wider, and a broad flat front across both guns
        outline = [(x * w + (.3 * (1 if x > 0 else -1) if abs(x) < .5 else 0), y) for x, y in outline]
    turret.prism(outline, .68, loc=(0, 0, .37), axis='Z', bevel=.05, seg=1, taper=.93)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.36 if twin else .66, .34, .46), loc=(0, -1.52, .38), bevel=.04, seg=1, taper=(.92, .9))   # mantlet
    for s in (-1, 1):                                                                            # cheek add-on plates
        tarm.box((.62, .1, .44), loc=(s * .72 * w * (1.2 if twin else 1), -1.3, .37), rot=(0, 0, s * .54), bevel=.02,
                 seg=1)
    # Bustle stowage box with a rolled tarpaulin, bins on the bustle sides.
    tarm.box((1.62 * w, .34, .42), loc=(0, 2.05, .36), bevel=.03, seg=1)
    a.part('Tarp', 'Canvas', t).cyl(.13, 1.3 * w, loc=(0, 2.02, .7), rot=ACROSS, seg=8, bevel=0)
    for s in (-1, 1):
        tarm.box((.18, 1.1, .4), loc=(s * (1.36 if twin else 1.3), 1.0, .28), bevel=.03, seg=1)  # bustle bins
        mv._smoke(a, a.part('Smoke', 'Steel', t), 1.07 * w, -.5, .58, s, count=3, gap=.08, r=.05, depth=.15)
    # The commander's panoramic sight (right rear), the gunner's sight box (right front), the loader's hatch.
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.15, .16, loc=(-.62 * w, .2, .78), seg=12, bevel=.02, bseg=1)
    tarm.box((.34, .3, .17), loc=(-.62 * w, .2, .92), bevel=.03, seg=1)
    glass = a.part('Sight', 'Glass', t)
    glass.box((.24, .03, .1), loc=(-.62 * w, .04, .93), bevel=0)
    tarm.box((.36, .42, .24), loc=(-.66 * w, -.95, .8), bevel=.03, seg=1)
    glass.box((.26, .03, .13), loc=(-.66 * w, -1.17, .82), bevel=0)
    mv._hatch(a, .55 * w, .45, .72, .27, parent=t, seg=10)
    mv._periscopes(a, [(.55 * w, .08, .72, 0)], parent=t)
    # 120 mm smooth-bore gun: 1.8 m past the nose, drawn 15 % thick.
    y0, length, z = -1.66, 3.26, .38
    for x, suffix in (((-.38, ''), (.38, '_2')) if twin else ((0, ''),)):
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        gun.cyl(.085, length, loc=(x, y0 - length / 2, z), rot=(R90, 0, 0), seg=10, bevel=0)
        gun.cyl(.105, length * .62, loc=(x, y0 - length * .36, z), rot=(R90, 0, 0), seg=12, bevel=0)   # thermal sleeve
        gun.cyl(.14, .42, loc=(x, y0 - length * .4, z), rot=(R90, 0, 0), seg=12, bevel=.02, bseg=1)    # fume extractor
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).cyl(.11, .16, loc=(x, y0 - length - .06, z),
                                                                rot=(R90, 0, 0), seg=10, bevel=.012, bseg=1)  # collar
    a.pivot('Muzzle_main', (0, y0 - length - .15, z), t)
    if twin:
        mv._coax(a, t, 0, -1.6, .56, length=.4, housing=.26)
    else:
        mv._coax(a, t, .42, -1.46, .5, length=.4, housing=.26)
    mv._roof_mg(a, t, (.55 * w, .45, .74), length=.8, shield=False)
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


# ----------------------------------------------------------------------------- C-130 airframe (mothership, AC-130)
C130_WING = dict(root_le=-1.0, tip_le=-.62, root_c=1.96, tip_c=1.0, span=8.08, z=.98)
C130_ENGINES = ((-3.96, 'Propeller'), (-1.96, 'Propeller_2'), (1.96, 'Propeller_3'), (3.96, 'Propeller_4'))
RAMP = (2.9, -.82, math.tan(.17), .17)     # hinge y, hinge z, slope, angle: lowered 10 degrees below level


def _c130(a, detail=False, ramp_open=False):
    """The shared four-turboprop transport airframe (C-130 class) of the drone mothership and the AC-130, 11.9 x
    16.2 x 4.6 m: a round fuselage with a radome nose and a band of flight-deck windows, gear sponsons, a high
    straight wing on a root fairing, four nacelles slung under it with four-blade `Propeller`..`Propeller_4` (drawn
    10 % large: with the long straight wing they are the silhouette), an upswept tail with a tall fin (10 % tall)
    and the tailplane. ramp_open lowers the cargo ramp under the tail and shows the dark hold above it. Origin at
    the fuselage centre (it flies). Returns the wing planform."""
    from mb_air import LEFT, RIGHT, Planform, _dome, _sec, _surface, _upright
    hd.mark(a, detail)
    n = 14 if detail else 12
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    dark = a.part('Undercarriage', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Wing_lights', 'TeamGlow')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=n, pt=2.4, pb=3.2)
    hull = [sec(-5.78, .36, -.46, .16), sec(-5.4, .7, -.78, .5), sec(-4.85, .86, -.9, .8), sec(2.5, .86, -.9, .82),
            sec(3.45, .84, -.56, .82), sec(4.7, .56, .1, .8), sec(5.75, .2, .48, .72)]
    body.loft([[(0, -5.96, -.16)]] + hull + [[(0, 5.96, .62)]], bevel=.02 if detail else 0, seg=1)
    armor.loft([[(0, -5.97, -.16)], sec(-5.9, .2, -.34, .04), sec(-5.72, .4, -.52, .22)], bevel=0)   # radome
    # Flight-deck windows: a glass band round the top of the nose, framed by the skin either side.
    a.part('Canopy', 'Glass').loft([_dome(y, w, z0, z1, 7) for y, w, z0, z1 in
                                    ((-5.52, .5, .12, .38), (-5.25, .74, .3, .62), (-4.95, .8, .42, .78))], bevel=0)
    for s in (-1, 1):                                                                            # gear sponsons
        armor.box((.42, 2.8, .6), loc=(s * .78, -.3, -.74), bevel=.06 if detail else .04, seg=1, taper=(.75, .95))
        steel.box((.24, .7, .2), loc=(s * .8, -.2, -1.0), bevel=0)                               # stowed wheels
    # High straight wing on its root fairing.
    w = C130_WING
    wing = Planform(0, w['span'], w['root_le'], w['tip_le'], w['root_c'], w['tip_c'], .36, .15, w['z'], w['z'] + .08)
    body.box((1.3, 2.4, .34), loc=(0, w['root_le'] + 1.05, .86), bevel=.06, seg=1, taper=(.8, .92))
    for frame in (RIGHT, LEFT):
        _surface(body, wing, frame, bevel=.012 if detail else 0)
    for s in (-1, 1):
        glow.box((.1, .22, .08), loc=(s * (w['span'] + .02), wing.le(w['span']) + .3, wing.at(w['span'])[3]), bevel=0)
    # Nacelles under the wing, the turboprops at their fronts.
    for x, name in C130_ENGINES:
        le = wing.le(abs(x))
        zc = wing.bottom(abs(x)) - .12
        nac = [(le - 1.15, .19, .2), (le - .75, .25, .27), (le + .3, .24, .27), (le + 1.4, .16, .16), (le + 2.1, .07, .08)]
        rings = [[(x + px, y, zc + pz) for px, _, pz in _sec(0, hw, -hh, hh, n=8 if not detail else 10, pt=2.2, pb=2.2)]
                 for y, hw, hh in nac]
        body.loft(rings + [[(x, le + 2.35, zc)]], bevel=0)
        armor.cyl(.2, .06, loc=(x, le - 1.17, zc), rot=(R90, 0, 0), seg=10, bevel=0)             # intake ring
        dark.box((.16, .12, .06), loc=(x, le - 1.1, zc - .17), bevel=0)                         # oil-cooler scoop
        dark.cyl(.06, .3, loc=(x + (.2 if x > 0 else -.2), le + .1, zc + .05), rot=(R90, 0, 0), seg=6, bevel=0)  # exhaust
        p = a.pivot(name, (x, le - 1.28, zc))
        spinner = a.part('Spinners', 'Armor', p)
        spinner.cyl(.12, .3, r2=.03, loc=(0, -.06, 0), rot=(R90, 0, 0), seg=8, bevel=0)
        blades = a.part('Prop_blades', 'Undercarriage', p)
        for k in range(4):
            u = k * math.tau / 4 + .4
            blades.box((.17, .05, .82), loc=(math.cos(u) * .5, .04, math.sin(u) * .5), rot=(0, -u + R90, 0), bevel=0,
                       taper=(.7, 1))
    # Upswept tail: the tall fin (10 % tall) and the tailplane.
    fin = Planform(0, 2.75, 3.3, 4.85, 2.35, 1.1, .3, .12)
    _surface(body, fin, _upright(0, .74, 0), lower=1.0, bevel=.012 if detail else 0)
    stab = Planform(.15, 3.1, 4.25, 4.95, 1.45, .7, .18, .08, .74, .8)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame, bevel=.012 if detail else 0)
    a.part('Beacon', 'TeamGlow').sphere(.09, loc=(0, 4.85 + 1.0, .74 + 2.76), seg=6, rings=4)
    if ramp_open:
        # Cargo ramp lowered under the upswept tail, the dark hold above it, the upper door raised inside.
        dark.box((1.3, 2.1, .3), loc=(0, 3.8, -.36), rot=(.49, 0, 0), bevel=0)
        ramp = a.part('Ramp', 'Armor')
        ramp.box((1.3, 1.8, .08), loc=(0, RAMP[0] + .9, RAMP[1] - .9 * RAMP[2] - .04), rot=(-RAMP[3], 0, 0), bevel=.02,
                 seg=1)
        steel.box((1.1, .1, .06), loc=(0, RAMP[0] + 1.8, RAMP[1] - 1.8 * RAMP[2] - .03), rot=(-RAMP[3], 0, 0),
                  bevel=0)                                                                     # ramp toe
        for sx in (-1, 1):
            steel.box((.06, 1.7, .08), loc=(sx * .5, RAMP[0] + .9, RAMP[1] - .9 * RAMP[2] + .02),
                      rot=(-RAMP[3], 0, 0), bevel=0)                                           # drone rails
    else:
        armor.box((1.2, 1.9, .05), loc=(0, 4.05, -.33), rot=(-.36, 0, 0), bevel=0)             # ramp outline
    a.pivot('Point_exhaust', (C130_ENGINES[0][0], wing.le(3.96) + .3, wing.bottom(3.96) - .07))
    a.pivot('Point_fire', (0, -.2, .95))
    return wing


def _small_drone(a, x, y, z, k=0):
    """An FPV drone at the battle scale (0.5 m across, drawn large enough to read), nose to -Y."""
    frame = a.part('Drone_frames', 'Undercarriage')
    frame.box((.12, .2, .07), loc=(x, y, z), bevel=0)
    for s in (-1, 1):
        frame.box((.52, .05, .03), loc=(x, y, z + .01), rot=(0, 0, s * math.pi / 4 + .02 * k), bevel=0)
    motors = a.part('Drone_motors', 'Steel')
    for dx, dy in ((.18, .18), (-.18, .18), (.18, -.18), (-.18, -.18)):
        motors.cyl(.05, .05, loc=(x + dx, y + dy, z + .03), seg=6, bevel=0)
    a.part('Drone_warheads', 'Hazard').cyl(.04, .2, r2=.015, loc=(x, y - .14, z - .06), rot=(R90, 0, 0), seg=6, bevel=0)
    a.part('Drone_lights', 'TeamGlow').box((.05, .05, .03), loc=(x, y + .08, z + .045), bevel=0)


def swarm_carrier(a):
    """Drone mothership (C-130 class), the AC-130's airframe at its size (_c130) with the cargo ramp lowered: two
    rows of FPV drones on rails on the ramp, the hold dark behind them. `Muzzle_drone` at the ramp's toe."""
    _c130(a, ramp_open=True)
    for i, (x, y) in enumerate(((-.3, 3.25), (.3, 3.6), (-.3, 4.0), (.3, 4.35))):
        _small_drone(a, x, y, RAMP[1] - (y - RAMP[0]) * RAMP[2] + .12, k=i)
    a.pivot('Muzzle_drone', (0, RAMP[0] + 1.9, RAMP[1] - 1.9 * RAMP[2] - .05))


def sky_gunship(a, detail=False):
    """AC-130 gunship: the mothership's airframe (_c130, ramp shut) with the left-side battery drawn big enough to
    read at battle zoom: the 25 mm gatling in a blister behind the crew door (`Muzzle_mg`), the 40 mm Bofors behind
    its mantlet aft of the wing (`Muzzle_gun`), the 105 mm howitzer in a bulged fairing further aft with its muzzle
    brake (`Muzzle_main`); a sensor ball under the nose and a second behind the crew door; gun-deck windows."""
    from mb_air2 import _side_gun
    _c130(a, detail=detail)
    guns = a.part('Guns', 'Steel')
    ports = a.part('Gun_ports', 'Armor')
    dark = a.part('Gun_bores', 'Undercarriage')
    seg = 12 if detail else 8
    at, rot = _side_gun((.8, -2.9, -.05), tilt=.16)                                             # 25 mm GAU-12
    ports.sphere((.3, .55, .36), loc=(.76, -2.9, -.05), seg=10, rings=6)
    guns.cyl(.12, .2, loc=at(.2), rot=rot, seg=seg, bevel=0)
    guns.cyl(.075, .42, loc=at(.42), rot=rot, seg=seg, bevel=0)
    guns.cyl(.095, .06, loc=at(.6), rot=rot, seg=seg, bevel=0)
    dark.cyl(.05, .02, loc=at(.635), rot=rot, seg=6, bevel=0)
    a.pivot('Muzzle_mg', at(.65))
    at, rot = _side_gun((.8, 1.55, .02), tilt=.14)                                              # 40 mm Bofors
    ports.box((.32, .9, .7), loc=(.8, 1.55, .04), bevel=.05, seg=1)
    ports.box((.12, .62, .54), loc=(.98, 1.55, .03), bevel=0)                                   # mantlet
    guns.cyl(.13, .28, loc=at(.2), rot=rot, seg=seg, bevel=0)
    guns.cyl(.07, .6, loc=at(.48), rot=rot, seg=seg, bevel=0)
    guns.cyl(.1, .16, r2=.075, loc=at(.78), rot=rot, seg=seg, bevel=0)                          # flash hider
    dark.cyl(.045, .02, loc=at(.865), rot=rot, seg=6, bevel=0)
    a.pivot('Muzzle_gun', at(.88))
    at, rot = _side_gun((.8, 3.05, .0), tilt=.12)                                               # 105 mm howitzer
    ports.sphere((.36, 1.0, .55), loc=(.7, 3.05, .02), seg=10, rings=6)
    ports.box((.12, .8, .72), loc=(1.04, 3.05, .0), bevel=0)                                    # gun shield
    guns.cyl(.18, .46, loc=at(.4), rot=rot, seg=seg + 2, bevel=0)                               # recoil sleeve
    guns.cyl(.105, .58, loc=at(.8), rot=rot, seg=seg + 2, bevel=0)
    brake = a.part('Howitzer_brake', 'Armor')
    brake.box((.28, .32, .3), loc=at(1.07), rot=(0, .12, 0), bevel=.03, seg=1)
    dark.cyl(.065, .02, loc=at(1.22), rot=rot, seg=8, bevel=0)
    a.pivot('Muzzle_main', at(1.24))
    glass = a.part('Gun_deck_windows', 'Glass')
    for y in (-2.3, -1.8, 2.15, 2.5):
        glass.box((.03, .28, .18), loc=(.86, y, .45), bevel=0)
    armor = a.part('Sensor_turrets', 'Armor')
    lens = a.part('Sensor', 'Glass')
    for (x, y, z), rr in (((.44, -4.15, -.93), .3), ((.66, -1.7, -.8), .23)):
        armor.cyl(rr * .5, .24, loc=(x, y, z + rr * .95), seg=8, bevel=0)
        armor.sphere(rr, loc=(x, y, z), seg=10 if not detail else 14, rings=6 if not detail else 9)
        lens.cyl(rr * .45, .05, loc=(x + rr - .015, y, z - rr * .12), rot=ACROSS, seg=8, bevel=0)
    if detail:  # bolts round the three gun ports' faces
        for yc, zc, face, dy, dz in ((-2.9, -.05, 1.06, .18, .14), (1.55, .03, 1.045, .26, .22), (3.05, 0, 1.105, .33, .3)):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    hd.bolt(guns, (face, yc + sy * dy, zc + sz * dz), hd.RIGHT_X, r=.016, h=.024)


# ----------------------------------------------------------------------------- attack helicopter (Apache)
def attack_helicopter(a, detail=False):
    """Attack helicopter (AH-64D Apache Longbow class), 6.0 m fuselage under a 6.0 m four-blade rotor, 1.9 m to the
    top of the mast radar: a narrow fuselage with the avionics bays along its cheeks, the stepped tandem canopy
    (gunner low in front, pilot raised behind), the TADS/PNVS sensor nose, shoulder engines with infrared
    suppressors, stub wings drawn 20 % long (with the rotor they are the silhouette's cross) carrying a rocket pod
    inboard and a four-round Hellfire rack outboard each side, Stinger tubes on the wingtips, the chin gun on its own
    yaw mount (`Mount_gun`), wheels (the Apache has no skids), the tail boom with its fin, stabilator and the
    X-shaped tail rotor. Origin on the ground under the fuselage (the wheels touch z = 0)."""
    from mb_air import (BACKWARD, FORWARD, _bubble, _exhaust_duct, _hellfire, _octagon, _pylon, _rocket_pod,
                        _rotor_head, _tail_rotor)
    hd.mark(a, detail)
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    bv = .03 if detail else .02
    hull = [_octagon(-3.0, .12, .56, .8), _octagon(-2.75, .23, .45, .95), _octagon(-2.2, .27, .42, 1.0),
            _octagon(-1.2, .3, .42, 1.02), _octagon(-.2, .32, .45, 1.1), _octagon(.6, .28, .5, 1.08),
            _octagon(1.0, .18, .7, 1.03)]
    body.loft(hull, bevel=bv, seg=1)
    boom = [_octagon(.9, .17, .72, 1.02), _octagon(2.8, .08, .82, .98)]
    body.loft(boom, bevel=bv * .6, seg=1)
    body.prism([(2.3, .95), (2.85, .93), (3.02, 1.78), (2.74, 1.8)], .08, bevel=.015, seg=1)       # fin
    body.box((.95, .3, .04), loc=(0, 2.6, .8), bevel=0, taper=(1, .75))                            # stabilator
    for s in (-1, 1):
        body.box((.17, 1.45, .3), loc=(s * .33, -1.3, .72), bevel=.04, seg=1, taper=(.8, .94))     # avionics bays
    # Stepped tandem canopy.
    glass.loft([_bubble(-2.55, .17, .93, 1.0), _bubble(-2.3, .25, .98, 1.18), _bubble(-1.98, .26, 1.0, 1.21)],
               bevel=0)
    glass.loft([_bubble(-2.0, .27, 1.0, 1.28), _bubble(-1.72, .28, 1.02, 1.4), _bubble(-1.2, .27, 1.04, 1.41),
                _bubble(-.95, .21, 1.06, 1.28)], bevel=0)
    # Shoulder engines with their suppressors, the rotor pylon and mast, the mast-mounted radar.
    for s in (-1, 1):
        x = s * .34
        body.cyl(.15, 1.0, loc=(x, -.05, 1.12), rot=FORWARD, seg=10, bevel=.02, bseg=1)
        dark.cyl(.11, .03, loc=(x, -.56, 1.12), rot=FORWARD, seg=10, bevel=0)                    # intakes
        _exhaust_duct(a, (s * .4, .6, 1.13), s * -.3, size=(.18, .34, .18))
    body.box((.42, .95, .26), loc=(0, -.45, 1.2), bevel=.04, seg=1, taper=(.72, .8))                # pylon
    steel.cyl(.06, .36, loc=(0, -.45, 1.4), seg=8, bevel=0)                                          # mast
    r = a.pivot('Rotor', (0, -.45, 1.58))
    _rotor_head(a, r, 4, 3.0, .26, hub=.18, phase=math.pi / 4, t=.035, cap=.08, stripe=.22, droop=.05)
    steel.cyl(.04, .12, loc=(0, -.45, 1.83), seg=6, bevel=0)                                         # radar stalk
    armor.sphere((.22, .22, .08), loc=(0, -.45, 1.94), seg=10, rings=6)                              # Longbow radar
    # TADS drum and PNVS turret at the nose, the landing light.
    armor.cyl(.12, .3, loc=(0, -2.95, .6), rot=ACROSS, seg=10, bevel=0)
    sensor = a.part('Sensor', 'Glass')
    for s in (-1, 1):
        armor.box((.06, .2, .2), loc=(s * .17, -2.94, .6), bevel=0)
        sensor.box((.04, .03, .08), loc=(s * .17, -3.05, .62), bevel=0)
    sensor.box((.1, .03, .08), loc=(0, -3.08, .6), bevel=0)
    armor.cyl(.06, .1, loc=(0, -2.85, .93), seg=8, bevel=0)
    # Stub wings: a rocket pod inboard and a Hellfire rack outboard each side, Stinger tubes on the tips.
    pylons = a.part('Pylons', 'Armor')
    stingers = a.part('Stinger_tubes', 'Fuel')
    for s in (-1, 1):
        body.box((1.0, .46, .08), loc=(s * .78, -.3, .82), rot=(0, s * -.05, 0), bevel=.015, seg=1, taper=(1, .9))
        _pylon(pylons, s * .62, -.48, -.12, .8, .7, w=.07)
        a.part('Pods', 'Armor').lathe([(.066, .66), (.1, .6), (.12, .43), (.12, .03), (.11, 0)], loc=(s * .62, -.72, .56),
                                      rot=BACKWARD, seg=10)                                    # 19-shot rocket pod
        a.part('Pod_bands', 'Hazard').cyl(.126, .04, loc=(s * .62, -.58, .56), rot=FORWARD, seg=10, bevel=0)
        a.part('Pod_face', 'Undercarriage').cyl(.09, .02, loc=(s * .62, -.726, .56), rot=FORWARD, seg=10, bevel=0)
        armor.box((.05, .56, .28), loc=(s * 1.08, -.34, .6), bevel=0)                               # Hellfire rail
        for x in (1.02, 1.14):
            for z in (.66, .52):
                if detail:
                    _hellfire(a, s * x, -.64, z, length=.66, r=.045, fins=x > 1.1)
                else:  # body and seeker cone only
                    a.part('Missiles', 'Fuel').cyl(.045, .6, loc=(s * x, -.64 + .36, z), rot=FORWARD, seg=6, bevel=0)
                    a.part('Missile_seekers', 'Glass').cyl(.045, .08, r2=.015, loc=(s * x, -.64 + .04, z), rot=FORWARD,
                                                           seg=6, bevel=0)
        for dz in (-.035, .035):
            stingers.cyl(.035, .5, loc=(s * 1.32, -.42, .82 + dz), rot=FORWARD, seg=6, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.05, .1, .05), loc=(s * 1.29, -.12, .83), bevel=0)
    a.pivot('Muzzle_rocket', (0, -.72, .56))
    a.pivot('Muzzle_missile', (0, -.64, .59))
    a.pivot('Muzzle_aam', (0, -.68, .82))
    # Wheels on short legs (main gear forward, a tail wheel).
    tyres = a.part('Tyres', 'Rubber')
    for s in (-1, 1):
        steel.box((.06, .08, .34), loc=(s * .42, -1.55, .3), rot=(0, s * .35, 0), bevel=0)         # legs
        tyres.cyl(.13, .08, loc=(s * .5, -1.55, .13), rot=ACROSS, seg=10, bevel=0)
    steel.box((.05, .3, .06), loc=(0, 2.45, .72), rot=(.9, 0, 0), bevel=0)
    tyres.cyl(.09, .06, loc=(0, 2.55, .09), rot=ACROSS, seg=8, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 2.9, 1.82), seg=6, rings=4)
    # Chin gun (M230, drawn thick) on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -2.3, .38))
    a.part('Gun_turret', 'Armor', g).cyl(.1, .1, loc=(0, 0, .02), seg=10, bevel=0)
    gun = a.part('Gun', 'Steel', g)
    gun.box((.1, .26, .09), loc=(0, -.08, -.06), bevel=0)
    gun.cyl(.035, .55, loc=(0, -.46, -.06), rot=FORWARD, seg=6, bevel=0)
    gun.cyl(.045, .06, loc=(0, -.72, -.06), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_gun', (0, -.76, -.06), g)
    # X-shaped tail rotor on the right of the fin.
    armor.cyl(.06, .1, loc=(-.08, 2.82, 1.45), rot=ACROSS, seg=8, bevel=0)                           # gearbox
    tr = a.pivot('Tail_rotor', (-.16, 2.82, 1.45))
    _tail_rotor(a, tr, 4, .56, .1, t=.02, phase=math.pi / 4, side=-1)
    a.pivot('Point_exhaust', (.45, .8, 1.13))
    a.pivot('Point_fire', (0, -.2, 1.1))
    if detail:
        rivets = a.part('Rivets', 'Steel')
        for s in (-1, 1):
            hd.bolt_line(rivets, (s * .42, -1.95, .87), (s * .42, -.65, .87), 8, rot=hd.side_rot(s), r=.012, h=.018)
            hd.bolt_line(rivets, (s * .15, -2.6, .88), (s * .15, -2.2, .96), 3, r=.01, h=.016)


# ----------------------------------------------------------------------------- Daedalus (boss)
# The upper hull of the Acclamator-style two-tier wedge: (y, half-width, top z), nose (-y) to stern.
DAEDALUS_UPPER = [(-14.5, .35, 1.25), (-10.0, 1.3, 2.25), (-5.0, 2.25, 2.95), (1.0, 3.2, 3.3), (8.0, 4.2, 3.45),
                  (13.5, 4.7, 3.45), (15.6, 4.5, 3.2)]


def _daedalus_upper(y):
    """(half-width, top z) of the upper hull at y."""
    s = DAEDALUS_UPPER
    if y <= s[0][0]:
        return s[0][1:]
    for p, q in zip(s, s[1:]):
        if y <= q[0]:
            t = (y - p[0]) / (q[0] - p[0])
            return p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t
    return s[-1][1:]


def daedalus(a):
    """Daedalus, Aurel's assault landing ship (Acclamator class, Star Wars: Attack of the Clones), 36.4 x 20.4 m as
    before (its part nodes stay where the boss data puts them). Prompt 25 B2 turns 20Y's single wedge into the
    Acclamator's two tiers: the lower wedge with its lit side trench (mb_redesign_20y._sd_hull), and on it a narrower
    upper wedge in off-white plates, lit windows along the step, a long dorsal ridge and the command tower aft; the
    side's colour in two long stripes down the upper wedge's shoulders (the Acclamator's red lines) and a band on the
    tower. Twelve twin turbolaser turrets on the step and a stern engine bank of two big and four smaller bells drawn
    over size (the silhouette's notched stern) read at battle zoom; the point-defence turrets (`Pd_laser_l` / `_r`,
    destructible) are drawn three times their old size on pylons at the step's shoulders, so they can be seen and
    aimed at. Unchanged nodes: `Pod_bay_1` .. `_3` (the drop bays under the belly), `Mount_gun` / `.001` (the 30 mm
    guns hanging under the nose), `Thruster_main` (the engine bank)."""
    import random

    import mb_orbital as orb
    from mb_p20_bosses import hanging_gun
    from mb_phase2 import _suffixed
    from mb_phase8 import pv
    from mb_redesign_20y import ACC, _sd_at, _sd_greebles, _sd_hull, _sd_surface
    _suffixed(a)
    rng = random.Random(1952)
    _sd_hull(a, 0.0, False, rng, prof=ACC, doors=False, hangar=False)
    # The upper wedge: a trapezoid section whose foot is buried in the lower hull.
    rings = []
    for y, hw, zt in DAEDALUS_UPPER:
        foot = min(_sd_surface(hw, y, ACC), _sd_surface(0, y, ACC)) - .15
        rings.append([(hw, y, foot), (hw * .84, y, zt), (-hw * .84, y, zt), (-hw, y, foot), (-hw * .5, y, foot - .4),
                      (hw * .5, y, foot - .4)])
    a.part('Upper_hull', 'Fuel').loft(rings, bevel=.06, seg=1)
    # Lit windows along the step, the plating lines across the upper deck.
    windows = a.part('Step_windows', 'Lamp')
    lines = a.part('Deck_lines', 'Armor')
    for sx in (-1, 1):
        y = -12.0
        while y < 15.0:
            hw, zt = _daedalus_upper(y)
            base = min(_sd_surface(hw, y, ACC), _sd_surface(0, y, ACC))
            z = base + (zt - base) * .45
            windows.box((.08, .5, .14), loc=(sx * (hw * (1 - .16 * .45) + .03), y, z), bevel=0)
            y += 1.4
    for y in (-8.0, -3.0, 2.0, 7.0, 12.0):
        hw, zt = _daedalus_upper(y)
        lines.box((hw * 1.6, .12, .05), loc=(0, y, zt + .01), bevel=0)
    # The side's colour: two long stripes down the upper wedge's shoulders, a band on the tower.
    stripes = a.part('Aurel_stripes', 'Team')
    for sx in (-1, 1):
        pts = [(sx * _daedalus_upper(y)[0] * .72, y, _daedalus_upper(y)[1] + .03) for y in (-13.0, -6.0, 1.0, 6.5)]
        for p, q in zip(pts, pts[1:]):
            stripes.limb(p, q, .7, .04, bevel=0)
    # Dorsal ridge and the command tower aft, with its bridge.
    spine = a.part('Spine', 'MetalSheet')
    spine.box((2.6, 19.0, 1.0), loc=(0, 3.0, _daedalus_upper(3.0)[1] + .4), bevel=.12, seg=1, taper=(.7, .96))
    z = _daedalus_upper(11.5)[1]
    spine.box((3.4, 3.2, 2.4), loc=(0, 11.6, z + 1.1), bevel=.12, seg=1, taper=(.75, .85))
    spine.box((2.2, 2.2, 1.6), loc=(0, 11.6, z + 2.9), bevel=.1, seg=1, taper=(.8, .85))
    spine.box((7.0, 2.3, 1.2), loc=(0, 11.6, z + 4.2), bevel=.12, seg=1, taper=(.95, .78))
    stripes.box((3.5, 3.3, .3), loc=(0, 11.6, z + 1.9), bevel=0, taper=(.95, .95))
    a.part('Bridge_windows', 'Lamp').box((6.2, .05, .22), loc=(0, 10.46, z + 4.25), bevel=0)
    a.part('Spine_lights', 'Lamp').box((1.8, .05, .12), loc=(0, -6.52, _daedalus_upper(-6.5)[1] + .6), bevel=0)
    dishes = a.part('Tower_dishes', 'Medical')
    for sx in (-1, 1):
        a.part('Dish_posts', 'Steel').cyl(.18, .6, loc=(sx * 2.6, 12.0, z + 5.05), seg=8, bevel=0)
        dishes.sphere((.8, .8, .3), loc=(sx * 2.6, 12.0, z + 5.35), seg=12, rings=6, cut=0)
    # Twelve twin turbolaser turrets on the step, their barrels forward.
    tur = a.part('Turbolasers', 'Armor')
    guns = a.part('Turbolaser_barrels', 'Steel')
    for sx in (-1, 1):
        for y in (-9.0, -2.0, 1.5, 5.0, 8.5, 12.5):
            hw, _ = _daedalus_upper(y)
            x = sx * (hw + 1.0)
            if abs(y + 5.0) < 1.5:
                continue   # the point-defence turret stands there
            base = _sd_surface(x, y, ACC)
            tur.cyl(.75, .5, loc=(x, y, base + .2), seg=10, bevel=.06, bseg=1)
            tur.box((1.1, 1.2, .5), loc=(x, y, base + .6), bevel=.08, seg=1, taper=(.8, .75))
            for o in (-.24, .24):
                guns.cyl(.09, 1.9, loc=(x + o, y - 1.4, base + .66), rot=(R90, 0, 0), seg=6, bevel=0)
    _sd_greebles(a, 0.0, rng, ACC, 130)
    # Two-tone plates on the lower wedge's sloped flanks, dark hangar recesses in the step, the belly's keel plates
    # and the landing feet the ship sets down on.
    plates = a.part('Flank_plates', 'Fuel')
    for sx in (-1, 1):
        for k in range(16):
            y = -12.5 + k * 1.75
            hw, zt, _ = _sd_at(y, ACC)
            u = .56 + .16 * (k % 2)
            x0 = hw * u
            z0 = _sd_surface(x0, y, ACC)
            slope = math.atan2(zt * .45, hw * .28)
            plates.box((hw * .12, 1.5, .08), loc=(sx * (x0 + hw * .04), y, z0 + .02), rot=(0, sx * slope, 0),
                       bevel=.03, seg=1)
    recess = a.part('Step_recesses', 'Undercarriage')
    for sx in (-1, 1):
        for y in (-7.5, 3.3, 6.8, 10.5):
            hw, zt = _daedalus_upper(y)
            base = min(_sd_surface(hw, y, ACC), _sd_surface(0, y, ACC))
            recess.box((.1, 1.4, (zt - base) * .5), loc=(sx * (hw * .95 + .02), y, base + (zt - base) * .35),
                       bevel=0)
    keel = a.part('Keel', 'Armor')
    for y in (-10.0, -4.0, 9.0, 13.0):
        hw, _, zb = _sd_at(y, ACC)
        keel.box((hw * .9, 1.2, .3), loc=(0, y, zb - .1), bevel=.06, seg=1, taper=(.85, .9))
    for x, y in ((5.0, 11.0), (-5.0, 11.0), (1.8, -9.0), (-1.8, -9.0)):
        _, _, zb = _sd_at(y, ACC)
        keel.cyl(.7, .45, loc=(x, y, zb - .12), seg=10, bevel=.05, bseg=1)                        # landing feet
    greeble = a.part('Upper_greebles', 'Armor')
    for i in range(46):
        y = rng.uniform(-9.0, 14.0)
        hw, zt = _daedalus_upper(y)
        x = rng.uniform(-hw * .75, hw * .75)
        if abs(x) < 1.5 or abs(y - 11.6) < 2.0:
            continue
        w, d, h = rng.uniform(.4, 1.2), rng.uniform(.4, 1.5), rng.uniform(.1, .3)
        greeble.box((w, d, h), loc=(x, y, zt + h / 2 - .02), bevel=0)
    # Point-defence turrets (destructible parts): big tubs with a dome and an emitter on pylons at the shoulders.
    pylons = a.part('Pylons', 'Armor')
    for name in ('Pd_laser_l', 'Pd_laser_r'):
        x, y, zz = orb._node(name, 0.0)
        p = a.pivot(name, (x, y, zz))
        a.part('Pd_base', 'Armor', p).cyl(.85, .45, loc=(0, 0, -.12), seg=14, bevel=.05, bseg=1)
        a.part('Pd_dome', 'Steel', p).sphere(.68, loc=(0, 0, .12), seg=14, rings=8, cut=-.1)
        a.part('Pd_emitter', 'Glass', p).cyl(.2, .5, loc=(0, -.62, .24), rot=(R90, 0, 0), seg=10, bevel=0)
        a.part('Pd_glow', 'TeamGlow', p).cyl(.13, .03, loc=(0, -.88, .24), rot=(R90, 0, 0), seg=10, bevel=0)
        base = _sd_surface(x, y, ACC)
        pylons.cyl(.45, zz - base - .3, loc=(x, y, (zz - .32 + base) / 2), seg=10, bevel=.03, bseg=1)
    # The engine bank: two big bells and four smaller, drawn over size, standing out behind the stern.
    right, forward, up = orb.NODES['Thruster_main']
    t = a.pivot('Thruster_main', orb._pos(right, forward, up))
    a.part('Engine_housing', 'Armor', t).box((14.0, 2.2, 4.0), loc=(0, 1.3, .2), bevel=.18, seg=1, taper=(.9, .88))
    nozzle = a.part('Engine_nozzles', 'Steel', t)
    glow = a.part('Engine_glow', 'TeamGlow', t)
    for x, r, z in ((2.3, 1.55, .3), (-2.3, 1.55, .3), (5.6, 1.0, .9), (-5.6, 1.0, .9), (5.6, .8, -.9), (-5.6, .8, -.9)):
        nozzle.cyl(r, 1.2, r2=r * 1.12, loc=(x, 2.9, z), rot=(-R90, 0, 0), seg=18 if r > 1.2 else 14, bevel=.05, bseg=1)
        glow.cyl(r * .78, .04, loc=(x, 3.45, z), rot=(R90, 0, 0), seg=16 if r > 1.2 else 12, bevel=0)
    # The three drop bays under the belly and the two guns under the nose, where the boss data puts them.
    for i, (x, y) in enumerate(((4.0, 2.0), (0.0, 5.0), (-4.0, 2.0))):
        p = pv(a, f'Pod_bay_{i + 1}', (x, y, -2.0))
        a.part(f'Bay_frame_{i + 1}', 'Armor', p).box((3.2, 3.8, .55), loc=(0, 0, 0), bevel=.1, seg=1)
        a.part(f'Bay_ring_{i + 1}', 'Team', p).cyl(1.25, .12, loc=(0, 0, -.3), seg=16, bevel=0)
        a.part(f'Bay_pod_{i + 1}', 'MetalSheet', p).cyl(1.0, 1.6, loc=(0, 0, -.85), seg=14, r2=.7, bevel=.05, bseg=1)
        a.part(f'Bay_glow_{i + 1}', 'Energy', p).cyl(.5, .05, loc=(0, 0, -1.67), seg=12, bevel=0)
    hanging_gun(a, 'Mount_gun', 'Muzzle_gun', (2.4, -6.0, -1.4))
    hanging_gun(a, 'Mount_gun.001', 'Muzzle_gun.001', (-2.4, -6.0, -1.4))
    a.pivot('Point_exhaust', (0, 19.0, .6))
    a.pivot('Point_fire', (0, 3.0, 3.6))


# ----------------------------------------------------------------------------- scout jeep
JEEP_K = 2.7 / 4.37     # mb_vehicles' jeep is drawn 4.37 m long; the sheet's is 2.7 m (0.8 x an M151)


def _crew(a, loc, parent=None, gunner=False):
    """A seated crewman seen from above: helmet, shoulders and arms (the sheet: the driver and the gunner show)."""
    x, y, z = loc
    h = .42 if gunner else .3     # the driver sits low, under the gun's sweep
    a.part('Crew', 'Suit', parent).box((.5, .3, h), loc=(x, y, z + h / 2), bevel=.06, seg=1, taper=(.85, .8))
    a.part('Helmets', 'Armor', parent).sphere((.17, .19, .13), loc=(x, y - .02, z + h + .1), seg=8, rings=5)
    arms = a.part('Crew', 'Suit', parent)
    for sx in (-1, 1):
        arms.box((.1, .34 if gunner else .3, .1), loc=(x + sx * .2, y - .2, z + h - .08), rot=(.3, 0, 0), bevel=0)


def scout_jeep(a, detail=False):
    """Scout jeep (M151 / Land Rover class), 2.7 x 1.4 x 1.4 m: the smallest vehicle in the game. mb_vehicles' open
    4x4 (flat hood, flat fenders, fold-down windscreen, roll bar, the machine gun on its pintle behind the seats,
    spare wheel and jerrycans at the back) drawn lean for the light-vehicle budget, with the driver and the gunner
    seated (the sheet: both must show from above); the gunner turns with the gun (`Turret`). Nothing thinner than
    0.1 m: the roll bar and the windscreen frame are square bars, no mirrors, whip or brush guard. Drawn at mb_vehicles'
    size and scaled by JEEP_K; the high-detail variant is mb_vehicles' own detailed jeep, scaled the same."""
    if detail:
        mv.scout_jeep(a, detail=True)
        _crew(a, (-.38, -.02, 1.18))
        _crew(a, (0, .55, .5), parent='Turret', gunner=True)
        a.pivot('Point_exhaust', (.6, 2.0, .55))
        a.pivot('Point_fire', (0, -1.2, 1.15))
        _scale_asset(a, JEEP_K)
        return
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    armor = a.part('Armor', 'Armor')
    chassis = a.part('Chassis', 'Undercarriage')
    rubber = a.part('Tyres', 'Rubber')
    seats = a.part('Seats', 'Canvas')
    chassis.box((1.45, 3.7, .26), loc=(0, 0, .55), bevel=0)
    for sx in (-1, 1):
        for y in (-1.25, 1.2):
            rubber.cyl(.42, .34, loc=(sx * .86, y, .42), rot=ACROSS, seg=12, bevel=.05, bseg=1)
            armor.cyl(.24, .37, loc=(sx * .86, y, .42), rot=ACROSS, seg=8, bevel=0)                 # wheel discs
            body.box((.46, 1.05, .1), loc=(sx * .9, y, .92), bevel=.03, seg=1, taper=(1, .8))        # fenders
        steel.box((.14, 1.3, .06), loc=(sx * .9, -.05, .64), bevel=0)                               # side steps
    body.prism([(-2.0, .62), (-2.0, .96), (-1.1, 1.12), (-.36, 1.14), (-.36, .62)], 1.7, bevel=.05, seg=1)
    body.box((1.72, 2.3, .52), loc=(0, .8, .88), bevel=.05, seg=1)
    chassis.grille(.7, .45, loc=(0, -.78, 1.15), rot=(-R90, 0, 0), slats=4, depth=.06, thickness=.04)   # louvres
    for x, y in ((-.38, -.05), (.38, -.05), (-.48, 1.0), (.48, 1.0)):
        seats.box((.44, .44, .12), loc=(x, y, 1.19), bevel=.03, seg=1)
        seats.box((.44, .1, .4), loc=(x, y + .25, 1.4), rot=(-.12, 0, 0), bevel=0)
    # Windscreen frame and roll bar as square bars (0.1 m or more).
    for x0, x1, y, h in ((-.82, .82, -.36, .54), (-.82, .82, 1.55, .66)):
        for x in (x0, x1):
            steel.box((.1, .1, h), loc=(x, y, 1.12 + h / 2), bevel=0)
        steel.box((x1 - x0 + .1, .1, .1), loc=(0, y, 1.12 + h), bevel=0)
    a.part('Glass', 'Glass').box((1.54, .03, .42), loc=(0, -.38, 1.39), rot=(-.12, 0, 0), bevel=0)
    for sx in (-1, 1):
        mv._headlight(a, sx * .55, -2.0, .8, guard=False)
        a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(sx * .58, 2.0, 1.05), bevel=.03, seg=1)
        mv._taillight(a, sx * .72, 1.95, .72)
    chassis.grille(.64, .26, loc=(0, -2.03, .8), slats=3, depth=.05, thickness=.05)
    steel.box((1.5, .12, .14), loc=(0, -2.05, .6), bevel=.03, seg=1)                                # bumper
    rubber.cyl(.36, .22, loc=(0, 2.03, 1.02), rot=FORWARD, seg=12, bevel=0)                         # spare wheel
    armor.cyl(.2, .25, loc=(0, 2.03, 1.02), rot=FORWARD, seg=8, bevel=0)
    armor.box((.4, .34, .3), loc=(.55, 1.65, 1.26), bevel=.02, seg=1)                               # radio
    a.part('Ammo_boxes', 'Crate').box((.4, .3, .24), loc=(-.52, 1.65, 1.23), bevel=.02, seg=1)
    a.part('Beacon', 'TeamGlow').box((.1, .1, .08), loc=(.72, 1.75, 1.45), bevel=0)
    _crew(a, (-.38, -.02, 1.18))                                                                    # the driver
    t = a.pivot('Turret', (0, .72, 1.14))
    a.part('Mount', 'Steel', t).cyl(.08, .52, loc=(0, 0, .26), seg=8, bevel=0)
    a.part('Gun_shield', 'Armor', t).box((.66, .08, .42), loc=(0, -.22, .66), bevel=.02, seg=1, taper=(.9, 1))
    cannon = a.part('Main_cannon', 'Steel', t)
    cannon.box((.16, .44, .18), loc=(0, 0, .64), bevel=.02, seg=1)
    cannon.cyl(.06, 1.0, loc=(0, -.66, .66), rot=FORWARD, seg=8, bevel=0)      # drawn 0.12 m thick to read
    cannon.cyl(.08, .12, loc=(0, -1.11, .66), rot=FORWARD, seg=8, bevel=0)     # flash hider
    a.part('Ammo_box', 'Armor', t).box((.2, .18, .16), loc=(.18, .05, .56), bevel=.02, seg=1)
    a.pivot('Muzzle_main', (0, -1.16, .66), t)
    _crew(a, (0, .55, .5), parent='Turret', gunner=True)                                          # the gunner
    a.pivot('Point_exhaust', (.6, 2.0, .55))
    a.pivot('Point_fire', (0, -1.2, 1.15))
    _scale_asset(a, JEEP_K)


# name: (builder, Asset options).
BUILDERS = {
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
    'twin_tank': (twin_tank, dict(ao_distance=.6, grime_height=.55)),
    'fighter_jet': (fighter_jet, dict(ao_distance=.35, ground=False)),
    'swarm_carrier': (swarm_carrier, dict(ao_distance=.9, ground=False)),
    'sky_gunship': (sky_gunship, dict(ao_distance=.9, ground=False)),
    'attack_helicopter': (attack_helicopter, dict(ao_distance=.4, grime_height=.3)),
    'daedalus': (daedalus, dict(ao_distance=.6, ground=False)),
    'scout_jeep': (scout_jeep, dict(ao_distance=.3, grime_height=.3)),
}
