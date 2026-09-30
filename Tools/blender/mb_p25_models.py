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


# name: (builder, Asset options).
BUILDERS = {
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
}
