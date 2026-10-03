"""Prompt 35 wave 1 (lane B): the elite battle tank rebuilt from scratch (spec: Tools/blender/specs/elite_mbt.json).

Its own tank, not the main battle tank with paint (the old builder called the V2 MBT's): a T-90M (unit_refs:
"T-90M (2A46M-5 125 mm)"; 0.93 x real, the def's modelSize 8.96 x 3.53 x 2.64 m). The low hull with the long shallow
glacis under a V of Relikt reactive bricks and the splash board, the self-entrenching blade under the nose, the
driver's hatch in the middle; rubber side skirts with reactive armour boxes over the front half; six large road
wheels, three return rollers, the front idler and rear sprocket, a linked track; slat armour round the engine deck
and the rear; the unditching log across the rear. The flat welded turret with its wedge of reactive armour over both
front cheeks, the gun mantlet under its dust cover, the 125 mm gun with thermal sleeve and fume extractor, the coaxial
machine gun, the gunner's sight box, the commander's panoramic sight and his remote weapon station with a 12.7 mm gun
standing on its post (MODEL_STANDARD "Roof guns"), smoke grenade launchers on both sides, the big ammunition bustle
inside a slat cage, the snorkel tube stowed on it. Elite marks (DECISIONS 25B2): black paint, gold bands and
chevrons, red-glowing sights.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Mount_mg`,
`Muzzle_mg`, `Point_exhaust`, `Point_fire`. Named for the gate: `Mantlet`, `Idlers`, `Sprockets`, `Skirts`.
Metres, +Z up, -Y front, +X left (the commander sits on the right, -X).
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P
import mb_parts27 as p27
import mb_vehicles as mv

R90 = math.pi / 2
PAINT = 'EliteBlack'         # the elite's black armour (DECISIONS 25B2: Armor -> EliteBlack)
BODY = 'Team'                # hull and turret paint: the team colour, as on every elite
TX, TW = 1.33, .54          # track centre line, belt width
WR = .37                    # road wheel radius
WHEELS = (-2.12, -1.3, -.48, .34, 1.16, 1.98)
HULL_TOP = 1.36
NOSE, TAIL = -3.18, 3.2
TURRET = (0, .3, 1.42)


def _hull(a):
    hull = a.part('Hull', BODY)
    # Upper hull over the tracks: lower nose plate, the long glacis, the flat deck, the sloped rear plate.
    prof = [(TAIL, .95), (TAIL + .05, 1.15), (TAIL - .1, HULL_TOP), (-1.55, HULL_TOP), (NOSE, .86), (NOSE + .02, .74),
            (NOSE + .3, .62)]
    k.extrude(hull, prof, 3.3, axis='X', chamfer=.06, corner=.03)
    low = a.part('Hull_lower', PAINT)
    k.extrude(low, [(TAIL - .05, .42), (NOSE + .5, .42), (NOSE + .3, .66), (TAIL - .05, .66)], 1.9, axis='X',
              chamfer=.03)
    # Fenders along both sides, team bands on the hull sides above the skirts.
    fen = a.part('Fenders', BODY)
    for s in (-1, 1):
        K.fender(fen, TX + .08, NOSE + .25, TAIL - .1, .98, .72, s, lip=.03)
    # The glacis: the splash board's V, the Relikt brick V on its lower part, the driver's hatch and periscope.
    g0, g1 = Vector((0, NOSE, .86)), Vector((0, -1.55, HULL_TOP))
    d = (g1 - g0).normalized()
    n = Vector((0, -d.z, d.y))
    for s in (-1, 1):
        ang = s * .3                                  # the two blocks meet in a V pointing up the glacis
        u = (Vector((1, 0, 0)) * math.cos(ang) + d * math.sin(ang)).normalized()
        v = n.cross(u)
        o = g0 + d * .62 + n * .05 + Vector((s * .62, 0, 0))
        rot = Matrix((u, v, n)).transposed().to_euler('XYZ')
        bricks = a.part('Era_bricks', PAINT)
        for i in range(3):
            for j in range(2):
                c = o + u * ((i - 1) * .32) + v * ((j - .5) * .28)
                bricks.box((.3, .26, .08), loc=tuple(c), rot=tuple(rot), bevel=0)
    board = a.part('Era_bricks', PAINT)                  # the splash board, welded with the bricks
    for s in (-1, 1):
        c = g0 + d * 1.05 + n * .05
        board.box((1.1, .05, .1), loc=(s * .5, c.y + .14, c.z + .05), rot=(math.atan2(d.z, -d.y), 0, -s * .35),
                  bevel=0)
    hc = g1 + d * -.18 + Vector((0, 0, .02))
    k.ring(a.part('Hatches', PAINT), [(.24, 0), (.3, 0), (.3, .06), (.24, .06)], loc=tuple(hc), seg=12)
    k.lathe(a.part('Hatches', PAINT), [(0, .09), (.2, .085), (.25, .06), (.25, .02)], loc=tuple(hc), seg=12)
    K.periscope(a, tuple(hc + Vector((0, -.32, -.04))), facing=(0, -1, 0), size=(.2, .1, .08), mat=PAINT)
    # The self-entrenching blade under the nose.
    blade = a.part('Dozer_blade', 'Armor')
    k.extrude(blade, [(-.12, -.1), (.04, -.12), (.08, .12), (-.02, .14)], 2.1, loc=(0, NOSE + .1, .5), axis='X',
              chamfer=.02)
    for s in (-1, 1):
        K.lamp(a, (s * 1.25, NOSE + .45, 1.05), (0, -1, .1), r=.07, mat=PAINT, guard=False)
    # The engine deck: grilles, the exhaust louvre on the left side, the access plates.
    K.grille(a, (0, 2.35, HULL_TOP + .02), 1.6, .8, facing=(0, 0, 1), slats=6, frame_mat=PAINT)
    K.grille(a, (1.66, 2.1, 1.15), .7, .2, facing=(1, 0, 0), slats=3, frame_mat=PAINT)
    a.pivot('Point_exhaust', (1.75, 2.1, 1.15))
    a.pivot('Point_fire', (0, 1.6, 1.6))
    # The unditching log across the rear with its chains; slat armour round the rear hull.
    k.lathe(a.part('Log', 'Wood'), [(.1, -1.5), (.13, -1.47), (.13, 1.47), (.1, 1.5)], loc=(0, TAIL + .05, 1.45),
            rot=(0, R90, 0), seg=8)
    for x in (-1.0, 1.0):
        a.part('Kit_latches', 'Steel').cyl(.14, .04, loc=(x, TAIL + .05, 1.45), rot=(0, R90, 0), seg=8, bevel=0)
    for s in (-1, 1):
        K.slat_cage(a, (s * (TX + .38), 1.0, 0), (s * (TX + .38), TAIL - .1, 0), .7, .6, (s, 0, 0), pitch=.34,
                    standoff=.05)
    K.slat_cage(a, (-1.5, TAIL + .1, 0), (1.5, TAIL + .1, 0), .55, .45, (0, 1, 0), pitch=.28, standoff=.12)
    # Fender furniture, as on the T-72 family: external fuel cells on the right fender, stowage boxes and the
    # tool box on the left.
    cells = a.part('Fuel_cells', PAINT)
    for y in (-.2, .45):
        K.chamfer_box(cells, (.5, .6, .36), loc=(-(TX + .02), y, 1.17), c=.04)
        a.part('Kit_latches', 'Steel').cyl(.05, .04, loc=(-(TX + .02), y - .15, 1.37), seg=8, bevel=0)
    a.part('Grilles', 'Undercarriage').tube([(-(TX + .02), -.45, 1.3), (-(TX - .3), -.6, HULL_TOP + .02)], .025,
                                               seg=5)
    P.toolbox(a, (TX + .02, -.3, 1.15), (.45, .9, .32), mat=PAINT)
    K.crate(a.part('Stowage', PAINT), a.part('Kit_latches', 'Steel'), (.45, .5, .28), (TX + .02, .55, .99), bands=1)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, 2.6, .1), loc=(s * (TX + .38 + .03), -1.0, 1.2), bevel=0)
        a.part('Tail_lamps', 'EliteGlow').box((.1, .02, .06), loc=(s * 1.3, TAIL - .02, 1.25), bevel=0)


def _running_gear(a):
    belt = a.part('Tracks', 'Undercarriage')
    links = a.part('Track_links', 'Undercarriage')
    idler_y, sprocket_y = -2.82, 2.78
    iz, sz = .62, .66
    pts = []
    for cy, cz, r in ((idler_y, iz, .3), (sprocket_y, sz, .33)) + tuple((y, WR, WR + .04) for y in WHEELS):
        for i in range(20):
            u = i * math.tau / 20
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    outline = mv._hull2d(pts)
    for s in (-1, 1):
        k.extrude(belt, outline, TW, loc=(s * TX, 0, 0), axis='X', chamfer=0)
        # Links all round the visible part: the lower run and both ends (the skirt hides the top run).
        for (py, pz), (ty, tz) in mv._perimeter(outline, .26, .0):
            if pz > .78 and -2.5 < py < 2.5:
                continue
            ny, nz = tz, -ty
            k.block(links, (TW + .04, .07, .04), loc=(s * TX, py + ny * .014, pz + nz * .014),
                    rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
        for y in WHEELS:
            p27.road_wheel(a, (s * (TX + TW / 2 - .14), y, WR), WR, .2, s, seg=10, disc_mat=PAINT)
        p27.sprocket(a, (s * (TX + TW / 2 - .14), sprocket_y, sz), .3, 10, .14, s)
        k.lathe(a.part('Idlers', PAINT), [(0, .1), (.1, .1), (.12, .08), (.25, .08), (.28, .05), (.28, -.07),
                                          (.24, -.08), (0, -.08)], loc=(s * (TX + TW / 2 - .14), idler_y, iz),
                rot=p27.side_rot(s), seg=10, worn=(4,))
        for y in (-1.2, .9):
            K.return_roller(a, (s * (TX + TW / 2 - .16), y, .88), .1, .12, s)
        K.dust(a, (s * TX, 0, .1), radius=2.0, k=.3)


def _skirts(a):
    """Rubber side skirts the full length, Relikt boxes bolted over their front half."""
    for s in (-1, 1):
        skirt = a.part('Skirts', 'Rubber')
        L = (TAIL - .5 - NOSE - .4) / 5
        for i in range(5):
            yc = NOSE + .4 + (i + .5) * L
            skirt.box((.04, L - .03, .5), loc=(s * (TX + .3), yc, .73), bevel=0)
        for i in range(4):
            y = NOSE + .75 + i * .62
            a.part('Skirt_era', PAINT).box((.12, .56, .46), loc=(s * (TX + .38), y, .74), bevel=0)


def _turret(a):
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', BODY, t)
    # Horizontal sections: a wide flat turret, its front narrowing to the mantlet, the bustle squared at the rear.
    rings = []
    for z, f, w, r in ((0, -1.45, 1.2, 1.55), (.36, -1.5, 1.22, 1.6), (.6, -1.25, 1.1, 1.5)):
        rings.append([(-w * .45, f, z), (w * .45, f, z), (w, f + .55, z), (w, r - .2, z), (w - .12, r, z),
                      (-w + .12, r, z), (-w, r - .2, z), (-w, f + .55, z)])
    k.sharp_loft(body, rings, chamfer=.05)
    k.ring(a.part('Turret_steel', 'Steel', t), [(.95, -.06), (1.05, -.06), (1.05, .04), (.95, .04)], seg=20)
    # The reactive-armour wedge over each front cheek (the T-90M's brow), its top plates.
    era = a.part('Turret_armor', PAINT, t)
    for s in (-1, 1):
        q = [(s * .36, -1.95, .05), (s * 1.28, -.95, .05), (s * 1.28, -.95, .58), (s * .36, -1.85, .58)]
        c = [Vector(p) for p in q]
        nrm = (c[1] - c[0]).cross(c[3] - c[0]).normalized() * (-s)
        verts = [tuple(p) for p in c] + [tuple(p - nrm * .28) for p in c]
        faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        era.mesh(verts, faces if s > 0 else [tuple(reversed(f)) for f in faces])
        for i in range(3):
            f = (i + .5) / 3
            p = c[0] + (c[1] - c[0]) * f + Vector((0, 0, .6))
            era.box((.3, .3, .04), loc=tuple(p + Vector((0, 0, .0))), rot=(0, 0, -s * .82), bevel=0)
    # Mantlet and its dust cover, the gun, the gold band, the coax.
    K.chamfer_box(a.part('Mantlet', PAINT, t), (.66, .3, .44), loc=(0, -1.6, .3), c=.05)
    k.lathe(a.part('Mantlet_cover', 'Canvas', t), [(.22, 0), (.26, .06), (.24, .14), (.16, .22)],
            loc=(0, -1.75, .3), rot=K.FORWARD, seg=10)
    L = 4.0
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.95, .3, L, .085, seg=12, extractor=(.45, 1.7, .5),
                 brake_name='Muzzle_brake', brake='collar', sleeve=1.25)
    a.part('Main_cannon_gilt', 'Gilded', t).cyl(.115, .1, loc=(0, -1.95 - L * .72, .3), rot=K.FORWARD, seg=12,
                                                bevel=0)
    a.pivot('Muzzle_main', (0, -1.95 - L - .16, .3), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.025, 0), (.025, .35), (0, .36)], loc=(-.36, -1.7, .26), rot=K.FORWARD,
            seg=6)
    a.pivot('Muzzle_coax', (-.36, -2.07, .26), t)
    # The gunner's sight box (left front), the commander's panoramic sight (right), hatches, smoke launchers.
    gs = a.part('Sight', PAINT, t)
    K.chamfer_box(gs, (.4, .45, .34), loc=(.62, -.85, .78), c=.04)
    a.part('Glass', 'Glass', t).box((.3, .01, .16), loc=(.62, -1.08, .82), bevel=0)
    a.part('Sight_glow', 'EliteGlow', t).box((.24, .01, .1), loc=(.62, -1.09, .82), bevel=0)
    K.periscope(a, (-.25, -.45, .6), facing=(0, -1, 0), parent=t, size=(.24, .22, .22), mat=PAINT)
    a.part('Sight_glow', 'EliteGlow', t).box((.18, .01, .1), loc=(-.25, -.57, .77), bevel=0)
    k.ring(a.part('Hatches', PAINT, t), [(.26, 0), (.32, 0), (.32, .07), (.26, .07)], loc=(.55, .15, .6), seg=12)
    k.lathe(a.part('Hatches', PAINT, t), [(0, .1), (.22, .095), (.27, .07), (.27, .02)], loc=(.55, .15, .6), seg=12)
    k.ring(a.part('Hatches', PAINT, t), [(.3, 0), (.36, 0), (.36, .08), (.3, .08)], loc=(-.6, .1, .6), seg=12)
    for s in (-1, 1):
        K.smoke_dischargers(a, .85, -1.05, .5, s, count=3, parent=t)
    # The ammunition bustle box at the rear inside its slat cage; the snorkel tube stowed on it.
    K.chamfer_box(a.part('Bustle', PAINT, t), (2.0, .7, .5), loc=(0, 1.75, .33), c=.05)
    K.slat_cage(a, (-1.25, 1.35, 0), (-1.25, 2.3, 0), .08, .55, (-1, 0, 0), pitch=.24, standoff=.12, parent=t)
    K.slat_cage(a, (1.25, 1.35, 0), (1.25, 2.3, 0), .08, .55, (1, 0, 0), pitch=.24, standoff=.12, parent=t)
    K.slat_cage(a, (-1.1, 2.15, 0), (1.1, 2.15, 0), .08, .55, (0, 1, 0), pitch=.26, standoff=.14, parent=t)
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.12, -.9), (.12, .9)], loc=(0, 2.0, .7), rot=(0, R90, 0), seg=10)
    # Stowage boxes on the turret sides, team panel on the roof, gold chevrons, the antennas.
    for s in (-1, 1):
        K.crate(a.part('Stowage', PAINT, t), a.part('Kit_latches', 'Steel', t), (.18, .7, .3), (s * 1.3, .55, .15),
                bands=1)
    a.part('Team_band', 'Team', t).box((1.0, .6, .015), loc=(0, .95, .605), bevel=0)
    gilt = a.part('Chevrons', 'Gilded', t)
    for s in (-1, 1):
        for i in range(2):
            for d in (-1, 1):
                gilt.box((.012, .28, .06), loc=(s * 1.226, .25 + i * .2 + d * .07, .35 + d * .0),
                         rot=(d * .6, 0, 0), bevel=0)
    ant = a.part('Turret_steel', 'Steel', t)
    K.whip_antenna(ant, (.95, 1.3, .6), h=.55, r=.02, lean=.15)


def _rws(a):
    """The commander's remote weapon station over his hatch: the post, the cradle with the 12.7 mm gun, its ammunition
    box and the sensor head (MODEL_STANDARD "Roof guns": it stands clear of the roof)."""
    m = P.raised_gun(a, (-.6, .1, .7), parent='Turret', pivot='Mount_mg', barrel='MG', brake='MG_flash',
                     muzzle='Muzzle_mg', riser=.18, ring_r=.3, post=.22, length=1.1, shield=False, ring=False,
                     mat=PAINT, tag='_rws')
    sens = a.part('Rws_sensor', PAINT, m)
    K.chamfer_box(sens, (.18, .26, .2), loc=(-.2, -.05, .38), c=.025)
    a.part('Sight_glow', 'EliteGlow', m).box((.12, .01, .08), loc=(-.2, -.185, .4), bevel=0)


def elite_mbt(a):
    """The elite battle tank: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _skirts(a)
    _turret(a)
    _rws(a)
    k.clean(a)


BUILDERS = {
    'elite_mbt': (elite_mbt, dict(ao_distance=.5, grime_height=.6)),
}
