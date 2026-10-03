"""Prompt 35 wave 1 (lane B): the smoke carrier rebuilt from scratch (spec: Tools/blender/specs/smoke_carrier.json).

An M58 Wolf: the M113A3 hull with a smoke generator system (0.87 x real: the def's modelSize 4.21 x 2.24 x 2.64 m):
the low box hull with its long sloped glacis carrying the folded trim vane, the upper hull overhanging the tracks as
sponsons, the driver's hatch with its periscopes on the front left and the engine grilles and exhaust on the front
right; the cylindrical smoke generator on its frame on the rear roof with the fog-oil tank and the bent exhaust
outlet; the commander's cupola with the M2 standing on its raised ring behind a shield; four-tube smoke grenade
dischargers on both glacis corners; the M113A3's armoured external fuel tanks flanking the rear ramp; five road
wheels a side, the front sprocket, the rear idler and a track with links all round (no skirts on an M113: the
sponson's lower edge, `Skirt_edge`, covers the top run).

Its own hull: nothing is taken from the mortar carrier (another M113, with the mortar hatch).
Runtime nodes kept: `Turret` (the cupola ring's yaw pivot: the main weapon is the M2), `Main_cannon`, `Muzzle_brake`,
`Muzzle_main`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P
import mb_parts27 as p27

R90 = math.pi / 2
HALF = 1.1           # hull half width (the sponsons over the tracks)
LOWER = .64          # the lower hull's half width between the tracks
TX, TW = .87, .38    # track centre line and belt width
WR = .27             # road wheel radius
ROOF = 1.58
SPONSON = .84        # the sponson's lower edge
WHEELS = (-1.3, -.66, -.02, .62, 1.26)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Side profile of the upper hull: lower nose, the long glacis, the flat roof, the upright rear (ramp).
    prof = [(2.02, SPONSON), (-1.7, SPONSON), (-2.1, .9), (-2.1, 1.0), (-1.32, ROOF), (2.0, ROOF), (2.02, ROOF - .04)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.1, corner=.03)      # the M113's radiused plate edges
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(2.0, .4), (-1.55, .4), (-2.05, .7), (-2.08, SPONSON + .02), (2.0, SPONSON + .02)], LOWER * 2,
              axis='X', chamfer=.03, corner=.02)
    # The sponson's lower lip along both sides (it hides the top run of the track).
    lip = a.part('Skirt_edge', 'Armor')
    for s in (-1, 1):
        lip.box((.04, 3.6, .1), loc=(s * (HALF - .02), .15, SPONSON - .04), bevel=0)
        a.part('Team_band', 'Team').box((.012, 3.4, .1), loc=(s * (HALF + .006), .2, ROOF - .25), bevel=0)
    # Rivet / weld lines along the roof edges and the glacis joint.
    K.weld(a.part('Kit_welds', 'Steel'), [(-HALF + .05, -1.32, ROOF + .003), (HALF - .05, -1.32, ROOF + .003)], r=.012)


def _running_gear(a):
    belt = a.part('Tracks', 'Undercarriage')
    links = a.part('Track_links', 'Undercarriage')
    sprocket_y, idler_y = -1.84, 1.86
    sz, iz = .58, .46
    rs, ri = .25, .24
    # The belt round sprocket, idler and the road wheels (outline of their circles, the top run straight).
    pts = []
    for cy, cz, r in ((sprocket_y, sz, rs + .04), (idler_y, iz, ri + .04)) + tuple((y, WR, WR + .035) for y in WHEELS):
        for i in range(20):
            u = i * math.tau / 20
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    import mb_vehicles as mv
    outline = mv._hull2d(pts)
    for s in (-1, 1):
        k.extrude(belt, outline, TW, loc=(s * TX, 0, 0), axis='X', chamfer=0)
        # Track links: a cleat every 0.17 m all round the belt.
        for (py, pz), (ty, tz) in mv._perimeter(outline, .24, .0):
            ny, nz = tz, -ty
            k.block(links, (TW + .03, .06, .035), loc=(s * TX, py + ny * .012, pz + nz * .012),
                    rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
        for y in WHEELS:
            p27.road_wheel(a, (s * (TX + TW / 2 - .1), y, WR), WR, .14, s, seg=10, disc_mat='Armor')
        p27.sprocket(a, (s * (TX + TW / 2 - .1), sprocket_y, sz), rs, 10, .12, s)
        # The idler: a spoked disc on its swing arm (the track tensioner).
        k.lathe(a.part('Idlers', 'Armor'), [(0, .09), (ri * .3, .09), (ri * .4, .07), (ri * .85, .07), (ri, .04),
                                            (ri, -.06), (ri * .85, -.07), (0, -.07)],
                loc=(s * (TX + TW / 2 - .1), idler_y, iz), rot=p27.side_rot(s), seg=10, worn=(4,))
        a.part('Idlers', 'Armor').limb((s * (TX - .05), idler_y, iz), (s * (TX - .05), idler_y - .35, iz + .2), .06,
                                       .08, bevel=0)
        K.dust(a, (s * TX, 0, .1), radius=1.6, k=.3)
    a.pivot('Point_fire', (0, .4, 1.4))


def _front(a):
    # The trim vane folded on the glacis, its hinges along the nose.
    g0, g1 = Vector((0, -2.1, 1.0)), Vector((0, -1.32, ROOF))
    d = (g1 - g0).normalized()
    n = Vector((0, -d.z, d.y))
    ang = math.atan2(d.z, -d.y)
    c = g0 + d * .45 + n * .04
    vane = a.part('Trim_vane', 'Armor')
    K.plate(vane, (HALF * 2 - .2, .7, .04), loc=tuple(c), rot=(ang, 0, 0), chamfer=.012)
    for f in (-.33, 0, .33):
        vane.box((.04, .66, .03), loc=tuple(c + n * .03 + Vector((f * 2 * (HALF - .1), 0, 0))), rot=(ang, 0, 0),
                 bevel=0)
    hin = a.part('Kit_hinges', 'Steel')
    for x in (-.7, .7):
        K.hinge(hin, (x - .12, -2.12, .96), (x + .12, -2.12, .96), r=.022, knuckles=2)
    # Headlamp clusters with guards on the lower nose corners, tow hooks.
    for s in (-1, 1):
        K.lamp(a, (s * .85, -2.13, .86), (0, -1, 0), r=.06, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .45, -2.1, .62), facing=(0, -1, 0), size=.07)
    # Smoke grenade dischargers on both upper glacis corners (four tubes each).
    for s in (-1, 1):
        K.smoke_dischargers(a, HALF - .3, -1.42, ROOF - .08, s, count=3)
    # The driver's hatch and periscopes (front left), the engine grilles and exhaust (front right).
    K.hatch_round(a, (.55, -1.0, ROOF), r=.3, periscopes=2)
    K.grille(a, (-.55, -.95, ROOF + .02), .7, .55, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    K.exhaust(a, (-HALF - .05, -1.15, 1.2), r=.06, length=.45, direction=(0, 0, 1), muffler=False, cap=False)
    a.part('Exhaust_shields', 'MetalSheet').box((.05, .28, .5), loc=(-HALF - .11, -1.15, 1.42), bevel=0)
    a.pivot('Point_exhaust', (-HALF - .05, -1.15, 1.7))


def _rear(a):
    # The ramp: its frame seam, the door in it with a handle, the hinges at its foot.
    dark = a.part('Hull_dark', 'Undercarriage')
    for x in (-.62, .62):
        dark.box((.02, .012, 1.0), loc=(x, 2.025, .98), bevel=0)
    dark.box((1.24, .012, .02), loc=(0, 2.025, 1.48), bevel=0)
    door = a.part('Hatches', 'Armor')
    K.plate(door, (.45, .04, .8), loc=(.2, 2.03, 1.0))
    K.handle(a.part('Kit_handles', 'Steel'), (.36, 2.05, .95), (.36, 2.05, 1.08), (0, 1, 0), h=.04, r=.01)
    for x in (-.45, .45):
        K.hinge(a.part('Kit_hinges', 'Steel'), (x - .1, 2.06, .5), (x + .1, 2.06, .5), r=.025, knuckles=2)
    # The M113A3's armoured external fuel tanks either side of the ramp.
    tanks = a.part('Fuel_tanks', 'Armor')
    for s in (-1, 1):
        K.chamfer_box(tanks, (.36, .28, .9), loc=(s * .87, 2.16, 1.02), c=.04)
        a.part('Fuel_caps', 'Steel').cyl(.05, .04, loc=(s * .87, 2.16, 1.49), seg=8, bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .06), loc=(s * .87, 2.305, 1.3), bevel=0)
    K.tow_hook(a.part('Kit_hooks', 'Steel'), (0, 2.03, .55), facing=(0, 1, 0), size=.07)


def _smoke_system(a):
    """The smoke generator on the rear roof: its frame, the generator drum with cooling fins, the fog-oil tank,
    the exhaust outlet bent up and back, the feed hoses."""
    fr = a.part('Smoke_frame', 'Steel')
    y0 = 1.15
    for x in (-.75, .75):
        fr.box((.06, .8, .06), loc=(x, y0, ROOF + .05), bevel=0)
        for dy in (-.3, .3):
            fr.box((.05, .05, .25), loc=(x, y0 + dy, ROOF + .18), bevel=0)
    gen = a.part('Smoke_generator', 'Armor')
    k.lathe(gen, [(.18, -.68), (.26, -.62), (.27, -.5), (.27, .5), (.26, .62), (.18, .68)], loc=(0, y0, ROOF + .55),
            rot=(0, R90, 0), seg=14, worn=(2, 3))
    fins = a.part('Smoke_fins', 'Steel')
    for x in (-.3, 0, .3):
        fins.cyl(.29, .025, loc=(x, y0, ROOF + .55), rot=(0, R90, 0), seg=14, bevel=0)
    # The exhaust outlet: an elbow out of the drum's right end, up and back.
    out = a.part('Smoke_outlet', 'Steel')
    out.tube([(-.7, y0, ROOF + .55), (-.86, y0 + .1, ROOF + .58), (-.88, y0 + .45, ROOF + .78),
              (-.84, y0 + .7, ROOF + .92)], .1, seg=10)
    k.ring(out, [(.1, 0), (.135, 0), (.135, .08), (.1, .08)], loc=(-.84, y0 + .7, ROOF + .92), rot=(-1.0, 0, 0),
           seg=10)
    K.soot(a, (-.84, y0 + .75, ROOF + .95), radius=.45, k=.5)
    # The fog-oil tank lying on the roof's left rear corner, its filler, the hoses to the generator.
    K.chamfer_box(a.part('Smoke_tank', 'Fuel'), (.5, .6, .32), loc=(.55, 1.7, ROOF + .16), c=.04)
    a.part('Fuel_caps', 'Steel').cyl(.06, .05, loc=(.55, 1.55, ROOF + .34), seg=8, bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(.4, 1.5, ROOF + .2), (.25, 1.35, ROOF + .3), (.15, y0, ROOF + .3)],
                                               .022, seg=5)
    # Stowage forward of it: a jerrycan rack, a rolled net, a crate.
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-.55, .3, ROOF), rot=(0, 0, R90))
    P.canvas_roll(a, (.35, .45, ROOF + .1), 1.0, r=.1, mat='Canvas')


def _cupola(a):
    """The commander's cupola: the hatch ring with periscopes, the M2 on its raised ring behind the shield (`Turret`)."""
    loc = (0, -.38, ROOF)
    cup = a.part('Cupola', 'Armor')
    k.ring(cup, [(.4, 0), (.5, 0), (.5, .12), (.44, .16), (.4, .16)], loc=loc, seg=16, worn=(2,))
    glass = a.part('Periscopes', 'Glass')
    for i in range(5):
        u = i * math.tau / 5 + .3
        x, y = loc[0] + math.cos(u) * .47, loc[1] + math.sin(u) * .47
        cup.box((.13, .09, .09), loc=(x, y, ROOF + .1), rot=(0, 0, u + R90), bevel=0)
        glass.box((.1, .01, .045), loc=(x + math.cos(u) * .05, y + math.sin(u) * .05, ROOF + .11), rot=(0, 0, u + R90),
                  bevel=0)
    t = P.raised_gun(a, (0, -.38, ROOF + .16), pivot='Turret', riser=.06, ring_r=.42, post=.18, length=1.15,
                     shield_k=.95)
    belt = a.part('MG_belt', 'Crate', t)
    for j in range(3):
        belt.box((.03, .06, .035), loc=(.1 - j * .025, .02, .38 + j * .012), rot=(0, -.5, 0), bevel=0)


def smoke_carrier(a):
    """The smoke carrier: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _front(a)
    _rear(a)
    _smoke_system(a)
    _cupola(a)
    k.clean(a)


BUILDERS = {
    'smoke_carrier': (smoke_carrier, dict(ao_distance=.45, grime_height=.55)),
}
