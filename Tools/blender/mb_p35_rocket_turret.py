"""Prompt 35 pilot 3: the rocket turret rebuilt from scratch (spec: Tools/blender/specs/rocket_turret.json).

A field-built Accord emplacement (4.7 x 4.7 x 3.4 m): a timber-framed earth pad, a horseshoe blast wall of sandbags
open at the rear for the crew, and on a race ring in the middle the turning launcher: a deck carrying the cradle, the
elevating ram and a BM-21-class pack of 40 tubes (4 rows of 10) raised 35 degrees, the operator's seat and shield, a
pintle MG for the crew. Behind the launcher: the reload rack with spare rockets, rocket crates, a jerrycan, a work
lamp on a post, a short whip and a rolled camouflage net on the wall.

Runtime nodes (kept from the old model): `Turret` (the yaw pivot; turret_rockets fires from `Muzzle_main` at the
pack's mouth), `Mount_mg` / `Muzzle_mg` (the crew MG), `Turret_armor` / `Turret_steel` meshes.

Wave 1 (owner decisions 4 and 6, the roof-gun rule): the two branches are built here on the same emplacement with
launchers of their own, so the three read apart at the default zoom: rocket_turret_a (the cluster branch) a 9P140
Uragan-class pack of 16 fat 220 mm tubes (4 x 4), rocket_turret_b (the guided branch) two GMLRS launch pod boxes
(6 cells each, frangible covers) with a sensor mast for the guidance. The tower stays under 1.5 x the class maximum
(6,000 triangles): exposed tubes without caps, two courses of bigger sandbags. The crew MG stands on a pintle post.
Built only from frontier_kit / mb_kit27 primitives and the mb_kit35 library. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
PAD = .3                  # top of the earth pad
ELEV = math.radians(-35)  # the pack's elevation (a negative turn about X raises the front)
PACK = (0.0, -.15, 1.9)  # the pack's centre, relative to the Turret pivot
COLS, ROWS, PITCH = 10, 4, .19
LENGTH = 2.5


def _emplacement(a):
    # Round 4: a dug earth pad of irregular outline (a field earthwork, not a cast slab), sloped sides, the timber
    # sleepers along its front and left edges, stakes holding them.
    outline = [(-2.25, -2.1), (-.6, -2.3), (1.3, -2.2), (2.3, -1.6), (2.25, .6), (2.35, 2.3), (.2, 2.35),
               (-1.7, 2.2), (-2.3, 1.1), (-2.2, -.8)]
    k.extrude(a.part('Base', 'Dirt'), outline, PAD, loc=(0, 0, PAD / 2), axis='Z', chamfer=.08, corner=.12,
              taper=(.96, .96))
    timbers = a.part('Base_timbers', 'Wood')
    for p0, p1 in ((outline[0], outline[2]), (outline[0], outline[8])):
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0))
        c = Vector(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, PAD * .55))
        k.block(timbers, (d.length, .2, .2), loc=tuple(c), rot=(0, 0, math.atan2(d.y, d.x)), chamfer=.03)
        for f in (.2, .8):
            q = Vector(p0) + (Vector(p1) - Vector(p0)) * f
            timbers.cyl(.045, .45, loc=(q.x, q.y, PAD * .5), seg=6, bevel=0)
    # The blast wall: a horseshoe of sandbags round the front and both sides, open at the rear.
    R = 2.0
    path = [(math.sin(t) * R, -math.cos(t) * R, PAD) for t in [math.radians(d) for d in range(-118, 119, 12)]]
    K.sandbag_wall(a, path, layers=2, bag=(1.1, .44, .27), round_both=False)
    # The wall's ends: timber posts holding the last bags, the rolled net on the left end.
    wood = a.part('Wall_timbers', 'Wood')
    for s in (-1, 1):
        x, y = s * math.sin(math.radians(118)) * R, -math.cos(math.radians(118)) * R
        wood.cyl(.07, .9, loc=(x, y + .25, PAD + .45), seg=6, bevel=0)
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (1.4, -.9, PAD + .68), length=1.4,
               r=.14, axis='Y')
    # Reload: the rack with spare rockets, crates, a jerrycan, the work lamp, the whip, a cable to the launcher.
    rack = a.part('Rocket_rack', 'Wood')
    for x in (-.9, .9):
        for y in (1.5, 2.0):
            rack.box((.08, .08, .55), loc=(x, y, PAD + .27), bevel=0)
        rack.box((.08, .7, .06), loc=(x, 1.75, PAD + .5), bevel=0)
    for i in range(2):
        k.lathe(a.part('Spare_rockets', 'Fuel'), [(0, -1.0), (.05, -.95), (.06, -.8), (.06, .95), (.05, .97), (0, .99)],
                loc=(0, 1.5 + i * .13, PAD + .59), rot=(0, R90, 0), seg=6, worn=(2,))
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(crates, straps, (.9, .4, .3), (-1.45, 1.2, PAD), rot=(0, 0, .2))
    K.crate(crates, straps, (.9, .4, .3), (-1.45, 1.2, PAD + .3), rot=(0, 0, .14), bands=1)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.0, 1.9, PAD), rot=(0, 0, .5))
    K.floodlight(a, (-1.9, 1.5, PAD), facing=(.4, -1, -.4), pole=1.6)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.75, .9, PAD + .6), h=.5, r=.04)
    # Round 2: dust trodden round the pad, aiming posts (striped) for laying the launcher, duckboards at the open
    # rear, tools on the wall, a field telephone on a post, an extinguisher, a tarp over a crate stack.
    for i in range(8):
        u = i * math.tau / 8
        K.dust(a, (math.cos(u) * 2.1, math.sin(u) * 2.1, PAD), radius=1.1, k=.3)
    K.dust(a, (0, 1.8, PAD), radius=1.0, k=.25)
    K.dust(a, (0, 0, PAD), radius=3.2, k=.2)
    # Round 3: a camouflage net on four poles over the reload corner (rear right), more rocket crates.
    poles = [(.6, 1.0), (2.15, 1.0), (2.15, 2.2), (.6, 2.2)]
    for (x, y), hgt in zip(poles, (1.7, 1.55, 1.45, 1.6)):
        wood.cyl(.04, hgt, loc=(x, y, PAD + hgt / 2), seg=5, bevel=0)
    net = a.part('Camo_net', 'Canvas')
    pts = [(x, y, PAD + hgt) for (x, y), hgt in zip(poles, (1.7, 1.55, 1.45, 1.6))]
    mid = (1.37, 1.6, PAD + 1.3)
    net.mesh([pts[0], pts[1], mid, pts[1], pts[2], mid, pts[2], pts[3], mid, pts[3], pts[0], mid],
             [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11)])
    net.mesh([pts[0], mid, pts[1], pts[1], mid, pts[2], pts[2], mid, pts[3], pts[3], mid, pts[0]],
             [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11)])
    for (sx, sy, sz), loc in (((.6, .3, .25), (.9, 2.1, PAD)), ((.5, .35, .3), (-.4, 2.2, PAD))):
        K.crate(crates, straps, (sx, sy, sz), loc, rot=(0, 0, .1 * sx), bands=1)
    post = a.part('Aiming_posts', 'Hazard')
    band = a.part('Aiming_bands', 'Charred')
    for x, y, h in ((-2.05, -2.05, 2.3), (-1.55, -2.15, 1.9)):
        post.cyl(.03, h, loc=(x, y, PAD + h / 2 - .1), seg=5, bevel=0)
        for j in range(2):
            band.cyl(.034, .18, loc=(x, y, PAD + h * (.4 + j * .3)), seg=5, bevel=0)
    tools = a.part('Tools', 'Steel')
    tools.tube([(1.95, -.2, PAD + .05), (1.85, -.35, PAD + 1.05)], .018, seg=4)          # shovel shaft
    tools.box((.2, .03, .26), loc=(1.97, -.17, PAD + .14), rot=(-.15, 0, 0), bevel=0)
    tools.tube([(1.9, .2, PAD + .05), (1.82, .1, PAD + .95)], .018, seg=4)               # pick
    tools.box((.42, .04, .05), loc=(1.82, .1, PAD + .95), rot=(0, .2, 0), bevel=0)
    wood.cyl(.04, 1.0, loc=(-1.2, 1.95, PAD + .5), seg=6, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.24, .12, .2), loc=(-1.2, 1.88, PAD + .9), chamfer=.015)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .38), (.04, .44), (0, .46)], loc=(-.9, 1.3, PAD),
            seg=8, worn=(1,))
    k.block(a.part('Tarp', 'Canvas'), (1.0, .5, .65), loc=(1.5, 1.35, PAD + .33), chamfer=.08, taper=(.9, .85))
    a.part('Kit_cables', 'Undercarriage').tube([(-1.85, 1.5, PAD + .05), (-1.1, .9, PAD + .03), (-.6, .3, PAD + .03)],
                                               .02, seg=4)


def _deck(a):
    """The turning deck every branch shares: the race, the Turret pivot, the deck disc and its skirt plates."""
    K.turret_ring(a.part('Race', 'Steel'), (0, 0, PAD), 1.1, h=.12)
    t = a.pivot('Turret', (0, 0, PAD + .1))
    deck = a.part('Turret_deck', 'Team', t)
    k.lathe(deck, [(1.15, 0), (1.18, .04), (1.18, .14), (1.12, .18), (0, .18)], seg=20, worn=(2, 3))
    arm = a.part('Turret_armor', 'Armor', t)
    for i in range(6):
        u = i * math.tau / 6 + .3
        k.block(arm, (.7, .05, .22), loc=(math.sin(u) * 1.19, -math.cos(u) * 1.19, .08), rot=(0, 0, u), chamfer=0)
    return t, arm


def _crew(a):
    """The operator's station behind the wall (seat, control box) and the crew MG on the wall's left end, on a
    pintle post (the roof-gun rule)."""
    seats = a.part('Seats', 'Canvas')
    K.chamfer_box(seats, (.4, .38, .08), loc=(1.35, .95, PAD + .42), c=.015)
    K.chamfer_box(seats, (.4, .06, .4), loc=(1.35, 1.14, PAD + .62), c=.015)
    a.part('Seat_post', 'Steel').cyl(.05, .38, loc=(1.35, .95, PAD + .19), seg=6, bevel=0)
    k.block(a.part('Control_box', 'Armor'), (.3, .2, .3), loc=(1.35, .62, PAD + .5), chamfer=.02)
    K.pintle_mg(a, None, (-1.75, .95, PAD + .55), index=0, scale=1.0, slot='mg', post=.5)


def _cradle(a, t, m, length, half_w):
    """Two side plates rising to the trunnion at the pack's rear, the elevating ram under the pack (any pack)."""
    tst = a.part('Turret_steel', 'Steel', t)
    trunnion = m @ Vector((0, length * .35, -.45))
    cradle = a.part('Launcher_cradle', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cradle, [(.55, .18), (-.35, .18), (trunnion.y - .2, trunnion.z - .1), (trunnion.y + .25,
                                                                                       trunnion.z + .05),
                           (.75, .5)], .08, loc=(s * (half_w + .12), 0, 0), axis='X', chamfer=.02)
        K.bolt_ring(tst, (s * (half_w + .17), trunnion.y, trunnion.z), (s, 0, 0), .1, 6, r=.022, h=.03)
    k.lathe(tst, [(.06, -(half_w + .2)), (.06, half_w + .2)], loc=tuple(trunnion), rot=(0, R90, 0), seg=8)
    ram_base = Vector((0, -.6, .2))
    ram_top = m @ Vector((0, -length * .1, -.42))
    tst.limb(tuple(ram_base), tuple(ram_base + (ram_top - ram_base) * .55), .14, .14, bevel=0)
    tst.limb(tuple(ram_base + (ram_top - ram_base) * .5), tuple(ram_top), .09, .09, bevel=0)
    a.part('Hoses', 'Rubber', t).tube([(.1, -.6, .3), (.35, -.4, .2), (.5, .1, .2)], .025, seg=5)
    a.part('Hoses', 'Rubber', t).tube([(-.1, -.6, .35), (-.4, -.3, .21), (-.55, .2, .21)], .022, seg=5)
    return tst


def _tube_pack(a, t, m, cols, rows, pitch, r, length, bands=(-.32, .05, .4)):
    """A pack of exposed launch tubes in a Team frame (top and bottom frames, corner posts, bands): every tube an open
    cylinder with its mouth ring and the dark bore at the front (no caps: the frame hides the ends, so the tower
    stays under its triangle cap)."""
    pack = a.part('Tubes', 'Team', t)
    w, h = cols * pitch + .08, rows * pitch + .08
    rot = tuple(m.to_euler('XYZ'))
    for zz in (-h / 2, h / 2):
        k.block(pack, (w, length * .96, .04), loc=tuple(m @ Vector((0, 0, zz))), rot=rot, chamfer=0)
    for xx in (-w / 2, w / 2):
        for f in (-.45, .45):
            pack.box((.05, .08, h), loc=tuple(m @ Vector((xx, f * length, 0))), rot=rot, bevel=0)
    tubes = a.part('Tube_bodies', 'Steel', t)
    mouths = a.part('Tube_mouths', 'Undercarriage', t)
    fm = m @ Matrix.Rotation(R90, 4, 'X')            # local +Z of a lathe -> the pack's -Y (forward)
    frot = tuple(fm.to_euler('XYZ'))
    for i in range(cols):
        for j in range(rows):
            x = (i - (cols - 1) / 2) * pitch
            z = (j - (rows - 1) / 2) * pitch
            k.lathe(tubes, [(r, -length / 2), (r, length / 2)], loc=tuple(m @ Vector((x, 0, z))), rot=frot, seg=6,
                    caps=(False, False), worn=(1,))
            c = m @ Vector((x, -length / 2 + .03, z))
            ring = [c + fm.to_3x3() @ Vector((math.cos(u) * r * .95, math.sin(u) * r * .95, 0))
                    for u in (i6 * math.tau / 6 for i6 in range(6))]
            mouths.mesh([tuple(v) for v in ring], [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)])
            mouths.mesh([tuple(v) for v in ring], [(0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 5, 4)])
    for f in bands:
        a.part('Pack_bands', 'Armor', t).box((w + .03, .07, h + .03), loc=tuple(m @ Vector((0, f * length, 0))),
                                             rot=rot, bevel=0)
    a.part('Pack_hazard', 'SafetyStripe', t).box((w, .05, .06), loc=tuple(m @ Vector((0, -length / 2 + .1, h / 2 + .02))),
                                                 rot=rot, bevel=0)
    return w, h


def _launcher(a):
    """rocket_turret: the BM-21-class pack of 40 tubes (4 rows of 10) raised 35 degrees."""
    t, arm = _deck(a)
    m = Matrix.Translation(Vector(PACK)) @ Matrix.Rotation(ELEV, 4, 'X')
    tst = _cradle(a, t, m, LENGTH, COLS * PITCH / 2)
    w, h = _tube_pack(a, t, m, COLS, ROWS, PITCH, .075, LENGTH)
    for f in (-.25, .25):
        K.handle(tst, tuple(m @ Vector((-w / 2 - .02, f * LENGTH - .1, .1))),
                 tuple(m @ Vector((-w / 2 - .02, f * LENGTH + .1, .1))), (-1, 0, 0), h=.06, r=.015)
    K.chamfer_box(arm, (.45, .3, .25), loc=(.6, .65, .3), c=.02)
    mouth = m @ Vector((0, -LENGTH / 2 - .05, 0))
    a.pivot('Muzzle_main', tuple(mouth), t)
    K.soot(a, (0, mouth.y, mouth.z + PAD + .1), radius=.6, k=.3)


def _launcher_cluster(a):
    """rocket_turret_a (the cluster branch): a 9P140 Uragan-class pack of 16 fat 220 mm tubes (4 x 4), longer and
    higher than the base pack, the fuzing cable trunk along its left side, lifting lugs."""
    t, arm = _deck(a)
    length, pitch = 3.1, .34
    m = Matrix.Translation(Vector((0.0, -.25, 2.0))) @ Matrix.Rotation(math.radians(-32), 4, 'X')
    tst = _cradle(a, t, m, length, 4 * pitch / 2)
    w, h = _tube_pack(a, t, m, 4, 4, pitch, .135, length, bands=(-.38, -.05, .3))
    rot = tuple(m.to_euler('XYZ'))
    # The fuzing cable trunk and its junction box (the cluster warheads are set before launch), lifting lugs.
    k.block(a.part('Fuze_trunk', 'Armor', t), (.12, length * .8, .12), loc=tuple(m @ Vector((w / 2 + .08, 0, .2))),
            rot=rot, chamfer=.02)
    K.chamfer_box(a.part('Fuze_box', 'Armor', t), (.22, .3, .3),
                  loc=tuple(m @ Vector((w / 2 + .14, length * .38, -.05))), rot=rot, c=.02)
    for f in (-.3, .3):
        K.hd.lifting_eye(tst, tuple(m @ Vector((0, f * length, h / 2 + .03))), yaw=0, size=.09)
    K.chamfer_box(arm, (.5, .34, .3), loc=(-.6, .7, .32), c=.02)
    mouth = m @ Vector((0, -length / 2 - .05, 0))
    a.pivot('Muzzle_main', tuple(mouth), t)
    K.soot(a, (0, mouth.y, mouth.z + PAD + .1), radius=.8, k=.32)


def _launcher_guided(a):
    """rocket_turret_b (the guided branch): two GMLRS launch pod boxes side by side (6 cells each, 3 x 2, behind
    frangible covers), latches and lifting points, and the guidance mast on the deck's rear: a datalink whip and a
    sensor head (vision 95 in the data)."""
    t, arm = _deck(a)
    length = 2.7
    m = Matrix.Translation(Vector((0.0, -.15, 1.85))) @ Matrix.Rotation(math.radians(-28), 4, 'X')
    tst = _cradle(a, t, m, length, .95)
    rot = tuple(m.to_euler('XYZ'))
    pods = a.part('Tubes', 'Team', t)
    faces = a.part('Pod_covers', 'Canvas', t)
    seams = a.part('Pod_seams', 'Undercarriage', t)
    ribs = a.part('Pod_ribs', 'Armor', t)
    for s in (-1, 1):
        cx = s * .47
        k.block(pods, (.86, length, .74), loc=tuple(m @ Vector((cx, 0, 0))), rot=rot, chamfer=.04)
        for f in (-.42, .0, .42):
            ribs.box((.9, .06, .78), loc=tuple(m @ Vector((cx, f * length, 0))), rot=rot, bevel=0)
        for i in range(3):
            for j in range(2):
                c = m @ Vector((cx + (i - 1) * .26, -length / 2 - .005, (j - .5) * .32))
                faces.box((.22, .02, .27), loc=tuple(c), rot=rot, bevel=0)
                for d in (.78,):
                    q = (m @ Matrix.Rotation(d, 4, 'Y')).to_euler('XYZ')
                    seams.box((.24, .025, .015), loc=tuple(c - (m.to_3x3() @ Vector((0, .006, 0)))), rot=tuple(q),
                              bevel=0)
        K.hd.lifting_eye(tst, tuple(m @ Vector((cx, 0, .39))), yaw=0, size=.08)
        K.handle(tst, tuple(m @ Vector((cx - .2, length / 2 + .01, .2))),
                 tuple(m @ Vector((cx + .2, length / 2 + .01, .2))), (0, 1, 0), h=.05, r=.015)
    a.part('Pack_hazard', 'SafetyStripe', t).box((1.8, .05, .06), loc=tuple(m @ Vector((0, -length / 2 + .12, .39))),
                                                 rot=rot, bevel=0)
    # The guidance mast behind the pods: a mast, the datalink whip, a sensor ball.
    a.part('Mast', 'Steel', t).cyl(.05, 1.5, loc=(-.75, .85, .9), seg=8, bevel=0)
    K.chamfer_box(arm, (.36, .3, .3), loc=(-.75, .85, .3), c=.02)
    k.lathe(a.part('Sensor_head', 'Armor', t), [(0, -.14), (.13, -.12), (.15, 0), (.13, .12), (0, .14)],
            loc=(-.75, .85, 1.75), seg=10)
    a.part('Sensor_glass', 'Glass', t).cyl(.07, .02, loc=(-.75, .71, 1.75), rot=K.FORWARD, seg=8, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.75, .95, 1.65), h=.7, r=.02)
    mouth = m @ Vector((0, -length / 2 - .05, 0))
    a.pivot('Muzzle_main', tuple(mouth), t)
    K.soot(a, (0, mouth.y, mouth.z + PAD + .1), radius=.7, k=.25)


def rocket_turret(a):
    """The rocket turret: see the module docstring."""
    _emplacement(a)
    _launcher(a)
    _crew(a)
    k.clean(a)


def rocket_turret_a(a):
    """The cluster branch: the same emplacement, the Uragan-class pack."""
    _emplacement(a)
    _launcher_cluster(a)
    _crew(a)
    k.clean(a)


def rocket_turret_b(a):
    """The guided branch: the same emplacement, the GMLRS pod boxes and the guidance mast."""
    _emplacement(a)
    _launcher_guided(a)
    _crew(a)
    k.clean(a)


BUILDERS = {
    'rocket_turret': (rocket_turret, dict(ao_distance=.6, grime_height=1.0)),
    'rocket_turret_a': (rocket_turret_a, dict(ao_distance=.6, grime_height=1.0)),
    'rocket_turret_b': (rocket_turret_b, dict(ao_distance=.6, grime_height=1.0)),
}
