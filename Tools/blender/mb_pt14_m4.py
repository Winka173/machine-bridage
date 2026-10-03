"""Play-test 14 model wave M4 (lane A): the base buildings redrawn (owner, Docs/prompts/playtest14_vi.txt: "ngoai drone
hangar nen them hangar cho xe tang va may bay, nho ve lai toan bo 3 hangar", "guard tower va laser anti drone station nen
ve lai", "mg bunker nen co them sung, bunker von co nhieu sung may o trong ban ra"; DECISIONS "Play-test 14 model wave
M4 (lane A)").

- mg_bunker / mg_bunker_a / mg_bunker_b: a hexagonal cast-concrete pillbox (pointed bow) half buried in an earth berm.
  Four embrasures with splayed concrete hoods on the two bow faces and the two flank faces, each with a 7.62 mm PKM in
  a steel ball mount on its own yaw pivot (`Mount_mg` ... `Mount_mg.003`, drawn along its firing arc's centre, the
  runtime turns it within the arc; `Muzzle_mg[.NNN]` at each flash hider); the turning cupola on the roof (`Turret`,
  `Elevation`) carries the main gun: one NSV (base), twin NSVs (_a, the .twin branch) or the flame gun (_b, the .flame
  branch; its embrasures are shut by armoured shutters, the branch has no port guns). Rear: the entry with its blast
  wall, the vent stack, the ammunition pit; wire in front.
- guard_tower / guard_tower_a: a modern steel guard tower: four raked legs with X bracing on concrete piers, the
  caged ladder, the deck with a railed walkway, an armoured cab with sloped armoured windows behind an RPG screen,
  the roof ring mount (`Turret`) with the M2 HMG on its `Elevation` cradle behind a shield; _a (the .watch branch)
  adds the telescopic sensor mast with the turning radar panel (`Radar`) and the EO ball.
- laser_ad_station (Laser Defence Tower): a fixed high-energy laser tower: the clad steel tower with four fixed radar
  panels, the platform with its railing and the beam director (`Turret`, `Elevation`, the aperture's `Muzzle_main`) on
  top; the power and cooling module behind it (chillers, cable riser), the APS sensor pod (`Mount_APS`).
- drone_hangar / drone_hangar_a / drone_hangar_b: a drone operations post of two ISO containers roofed over into a
  bay with a roller door, the launch deck on top under an anti-drone net; the FPV launch rail (`Launch_rail`, the
  drones leave at `Muzzle_main` / `Muzzle_door_l` on its end), the Lancet catapult (_a) or the swarm launch cells (_b).
- vehicle_hangar_base (balance vehicle_hangar's own model; the map prop vehicle_hangar keeps its file): a steel
  portal-frame motor-pool shed, corrugated cladding, the sectional door rolled up, a vehicle lift and benches inside,
  the office lean-to.
- aircraft_hangar: a tension-fabric helicopter hangar on steel arches with its doors drawn open, the helipad apron in
  front (circle and H), edge lights, a windsock, the fuel point.

Every round leaves from a barrel or a rail with its Muzzle_* point at the mouth (owner 03/10). Built from frontier_kit /
mb_kit27 / mb_kit35 primitives only. Metres, +Z up, -Y front, +X left. Headings in degrees as the Sim's (0 the front,
+ to the right).
"""
import math
import random

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
G = .05


# ============================================================================= shared
def _rotatable(a):
    """Lets a pivot carry a yaw: the kit's world matrix (shading) follows the pivot's rotation too. Used for the port
    guns, drawn along their firing arc's centre (the runtime sets the mount's yaw itself, so the rest pose is only
    what the model shows standing)."""
    if getattr(a, '_m4_rot', False):
        return
    a._m4_rot = True

    def world(parent):
        m = Matrix.Identity(4)
        o = a.pivots[parent] if parent else None
        while o is not None:
            m = Matrix.Translation(o.location) @ o.rotation_euler.to_matrix().to_4x4() @ m
            o = o.parent
        return m
    a._world = world


def _dir(h, r=1.0):
    """(x, y) at distance r along heading h (degrees; 0 the front, + right)."""
    t = math.radians(h)
    return (-math.sin(t) * r, -math.cos(t) * r)


def _yaw(h):
    """The Z rotation turning local -Y (the front) to heading h."""
    return -math.radians(h)


def _poly(r, headings):
    """Polygon vertices at the headings (counter-clockwise seen from above)."""
    pts = [_dir(h, r) for h in headings]
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


def _face_frame(h, dist, z):
    """(matrix, rot) of a wall face at heading h: local x across, y up, z out."""
    dx, dy = _dir(h)
    rot = K.rot_to((dx, dy, 0))
    return K.frame((dx * dist, dy * dist, z), rot), rot


def _pad(shape, size, loc, chamfer=.02, taper=(1, 1)):
    """A block standing on the ground (or on a body) with no bottom face: never seen, and it would only add area."""
    sx, sy, sz = size
    c = min(chamfer, sx * .3, sy * .3, sz * .3)
    k.extrude(shape, [(-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)], sz, loc=loc,
              axis='Z', chamfer=c, corner=c, taper=tuple(taper), ends=(False, True), caps=(False, True))
    return shape


def _stones(a, n, r0, r1, seed, z=G, skip=None):
    rng = random.Random(seed)
    rk = a.part('Stones', 'Rock')
    for _ in range(n):
        u = rng.uniform(0, TAU)
        r = rng.uniform(r0, r1)
        x, y = math.cos(u) * r, math.sin(u) * r
        if skip and skip(x, y):
            continue
        s = rng.uniform(.08, .2)
        rk.box((s, s * 1.3, s * .6), loc=(x, y, z + s * .2), rot=(rng.uniform(0, 1), rng.uniform(0, 1), u), bevel=0)


def _concertina(a, path, r=.22, pitch=.4, posts=.9, seed=0):
    """A concertina coil along a polyline on the ground (a helix tube, 3 sides) on angle-iron pickets."""
    pts = [Vector(p) for p in path]
    coil = []
    for p, t in k.along([tuple(p) for p in pts], pitch=pitch / 5):
        coil.append((p, t))
    side = a.part('Kit_fence', 'Steel')
    helix = []
    for i, (p, t) in enumerate(coil):
        u = i * TAU / 5
        n = Vector((-t.y, t.x, 0)).normalized()
        helix.append(tuple(p + n * math.cos(u) * r + Vector((0, 0, r + math.sin(u) * r))))
    side.tube(helix, .009, seg=3, caps=False)
    for p, t in k.along([tuple(p) for p in pts], pitch=posts):
        side.box((.035, .035, .6), loc=(p.x, p.y, p.z + .28), rot=(0, 0, math.atan2(t.y, t.x)), bevel=0)


# ============================================================================= mg bunker family
BR = 1.78                         # wall circumradius (hexagon, a vertex at the bow)
BAP = BR * math.cos(math.pi / 6)  # wall apothem
WZ1 = 1.45                        # wall top
RZ0, RZ1 = 1.45, 1.75             # roof slab
PZ = .9                           # embrasure centre height
PORTS = (-30, 30, -90, 90)        # Mount_mg, .001, .002, .003 headings (data secondary order)
PORT_HALF = 40                    # each port's arc half width (data "arc")
DOOR = -150                       # the entry face (rear left)
HEX = (0, 60, 120, 180, 240, 300)


def _bunker_shell(a):
    """Plinth, walls, roof slab, Team band, pour lines, roof parapet bags."""
    k.extrude(a.part('Base', 'Concrete'), _poly(1.92, HEX), .12, loc=(0, 0, .06), axis='Z', chamfer=.03,
              corner=.1)
    walls = a.part('Walls', 'Concrete')
    k.extrude(walls, _poly(BR, HEX), WZ1 - G + .02, loc=(0, 0, (WZ1 + G) / 2), axis='Z', chamfer=.03, corner=.09)
    roof = a.part('Roof', 'Concrete')
    k.extrude(roof, _poly(1.98, HEX), RZ1 - RZ0, loc=(0, 0, (RZ0 + RZ1) / 2), axis='Z', chamfer=.06, corner=.12,
              taper=(.97, .97))
    # Pour lines and form-tie holes on each face; the Team band under the roof's drip edge.
    lines = a.part('Pour_lines', 'Concrete')
    band = a.part('Team_band', 'Team')
    for hc in (30, 90, 150, 210, 270, 330):
        m, rot = _face_frame(hc, BAP, 0)
        band.box((1.55, .1, .02), loc=tuple(m @ Vector((0, 1.32, .012))), rot=rot, bevel=0)
        lines.box((1.6, .025, .02), loc=tuple(m @ Vector((0, .62, .008))), rot=rot, bevel=0)


def _berm(a, courses=1):
    """The earth berm round the walls (open at the entry face), turf, the roof parapet bags."""
    path = [(*_dir(h, 1.8), G) for h in range(-118, 179, 12)]
    k.sweep(a.part('Berm', 'Dirt'), [(.3, 0), (-.42, 0), (-.18, .3), (.08, .52), (.3, .54)], path, caps=True,
            worn=(2, 3), v_up=True)
    turf = a.part('Berm_turf', 'Grass')
    rng = random.Random(14)
    for h in range(-110, 175, 26):
        x, y = _dir(h + rng.uniform(-6, 6), 1.95)
        turf.box((.36, .5 + rng.uniform(0, .3), .03), loc=(x, y, .3), rot=(0, .6, math.atan2(y, x)), bevel=0)
    for h in range(-110, 180, 40):
        K.dust(a, (*_dir(h, 2.1), G), radius=1.0, k=.28)
    # A course of bags along the roof's bow edge (the cupola fires over them).
    W.bags(a, [(*_dir(h, 1.62), RZ1) for h in range(-56, 57, 16)], layers=courses, bag=(.5, .28, .15), seed=41,
           name='Parapet')


def _embrasure(a, h, z=PZ):
    """A splayed concrete hood round a port on the face at heading h, its dark recess and steel collar."""
    m, rot = _face_frame(h, BAP, z)
    emb = a.part('Embrasure', 'Concrete')
    k.block(emb, (1.0, .17, .38), loc=tuple(m @ Vector((0, .27, .17))), rot=rot, chamfer=.03)
    emb.box((1.0, .13, .3), loc=tuple(m @ Vector((0, -.27, .13))), rot=rot, bevel=0)
    for s in (-1, 1):
        emb.box((.14, .41, .34), loc=tuple(m @ Vector((s * .47, 0, .15))), rot=rot, bevel=0)
    a.part('Embrasure_slot', 'Undercarriage').box((.8, .38, .02), loc=tuple(m @ Vector((0, 0, .012))), rot=rot,
                                                  bevel=0)
    a.part('Port_collars', 'Steel').cyl(.17, .04, loc=tuple(m @ Vector((0, 0, .03))), rot=rot, seg=8, bevel=0)
    return m


def _port_gun(a, i, h, z=PZ):
    """Port gun i at heading h: a PKM in a ball mount on its own yaw pivot, drawn along the arc's centre."""
    _rotatable(a)
    K.suffixed(a)
    x, y = _dir(h, BAP + .05)
    mount = a.pivot(K.name('Mount_mg', i), (x, y, z))
    a.pivots[mount].rotation_euler = (0, 0, _yaw(h))
    tag = '' if i == 0 else f'_{i}'
    ball = a.part(f'Port_balls{tag}', 'Armor', mount)
    ball.sphere(.105, loc=(0, 0, 0), seg=8, rings=5)
    ball.cyl(.07, .1, loc=(0, -.1, 0), rot=K.FORWARD, seg=8, bevel=0)
    gun = a.part(f'Port_barrels{tag}', 'Steel', mount)
    L = .66
    k.lathe(gun, [(.03, 0), (.03, .08), (.017, .11), (.016, L - .1), (.024, L - .09), (.024, L), (0, L)],
            loc=(0, -.14, 0), rot=K.FORWARD, seg=6, worn=(5,))
    gun.box((.018, .4, .022), loc=(0, -.36, -.04), bevel=0)              # gas tube
    gun.box((.012, .03, .05), loc=(0, -.74, .03), bevel=0)               # front sight
    a.pivot(K.name('Muzzle_mg', i), (0, -.14 - L - .005, 0), mount)
    K.soot(a, (x + _dir(h)[0] * .3, y + _dir(h)[1] * .3, z), radius=.35, k=.35)


def _port_shutter(a, h, z=PZ):
    """An armoured shutter closing a port (the flame branch has no port guns)."""
    m, rot = _face_frame(h, BAP, z)
    K.plate(a.part('Port_shutters', 'Armor'), (.74, .36, .045), loc=tuple(m @ Vector((0, 0, .05))), rot=rot,
            chamfer=.012)
    a.part('Slits', 'Undercarriage').box((.36, .035, .02), loc=tuple(m @ Vector((0, .06, .078))), rot=rot, bevel=0)
    hg = a.part('Kit_hinges', 'Steel')
    for s in (-1, 1):
        hg.box((.14, .04, .04), loc=tuple(m @ Vector((s * .25, .19, .075))), rot=rot, bevel=0)
    K.handle(a.part('Kit_handles', 'Steel'), tuple(m @ Vector((-.08, -.1, .075))),
             tuple(m @ Vector((.08, -.1, .075))), (*_dir(h), 0), h=.04)


def _cupola(a, collar=False):
    """The turning cast cupola on the roof (`Turret`), periscope, hatch, bolts; returns the Turret pivot."""
    k.ring(a.part('Race', 'Steel'), [(.78, 0), (.95, 0), (.95, .07), (.78, .07)], loc=(0, .15, RZ1 - .02), seg=14)
    t = a.pivot('Turret', (0, .15, RZ1 + .05))
    k.lathe(a.part('Turret_body', 'Armor', t), [(.9, 0), (.89, .12), (.78, .3), (.55, .44), (.22, .5), (0, .51)],
            seg=14, caps=(False, True), worn=(1, 2))
    a.part('Turret_band', 'Team', t).cyl(.86, .07, loc=(0, 0, .17), seg=14, bevel=0)
    bolts = a.part('Kit_bolts', 'Steel', t)
    for i in range(10):
        u = i * TAU / 10
        bolts.cyl(.026, .03, loc=(math.cos(u) * .8, math.sin(u) * .8, .28), seg=4, bevel=0)
    if collar:
        cl = a.part('Turret_collar', 'Armor', t)
        for i in range(7):
            u = i * TAU / 8 + TAU / 16 + R90
            cl.box((.62, .07, .26), loc=(math.cos(u) * .93, math.sin(u) * .93, .13), rot=(0, 0, u + R90), bevel=0)
    K.periscope(a, (.38, -.42, .43), facing=(0, -1, 0), parent=t, size=(.15, .13, .12))
    k.lathe(a.part('Hatches', 'Armor', t), [(.3, .47), (.3, .54), (0, .58)], loc=(-.15, .3, 0), seg=10)
    K.handle(a.part('Kit_handles', 'Steel', t), (-.3, .3, .6), (0, .3, .6), (0, 0, 1), h=.05)
    # The embrasure boss on the cupola's face.
    k.block(a.part('Embrasure', 'Armor', t), (.56, .34, .34), loc=(0, -.76, .2), rot=K.FORWARD, chamfer=.04)
    return t


def _nsv(a, el, x, name, brake, length, jacket=False):
    """One NSV barrel along -Y on the Elevation pivot, its flash hider (and a cooling jacket); returns the tip."""
    k.lathe(a.part(name, 'Steel', el), [(.045, 0), (.045, .18), (.03, .22), (.026, length), (0, length)],
            loc=(x, -.1, 0), rot=K.FORWARD, seg=8, worn=(1,))
    if jacket:
        a.part(f'{name}_jacket', 'Armor', el).cyl(.05, length * .42, loc=(x, -.3 - length * .2, 0), rot=K.FORWARD,
                                                  seg=8, bevel=0)
    k.lathe(a.part(brake, 'Undercarriage', el), [(.026, 0), (.042, .02), (.042, .14), (.03, .16), (0, .16)],
            loc=(x, -.1 - length + .02, 0), rot=K.FORWARD, seg=8)
    return (x, -.1 - length - .14, 0)


def _bunker_rear(a, stacks=1, flame=False):
    """The entry (door, blast wall, steps), the vent stack, the ammunition pit, antenna, lamp, wire and pickets."""
    m, rot = _face_frame(DOOR, BAP, G)
    K.door(a, tuple(m @ Vector((0, 0, .02))), size=(.72, 1.18), normal=_dir(DOOR) + (0,), mat='Armor')
    dw = a.part('Door_well', 'Concrete')
    for s in (-1, 1):
        k.block(dw, (.16, .66, .62), loc=tuple(m @ Vector((s * .55, .3, .33))), rot=rot, chamfer=.03)
    a.part('Base', 'Concrete').box((1.3, .06, .9), loc=tuple(m @ Vector((0, .0, .45))), rot=rot, bevel=.01)
    # The blast wall of bags across the entry, a dog-leg.
    dx, dy = _dir(DOOR)
    ox, oy = dx * 2.15, dy * 2.15
    px, py = -dy, dx
    W.bags(a, [(ox + px * .7, oy + py * .7, G), (ox - px * .55, oy - py * .55, G)], layers=3, bag=(.55, .3, .16),
           seed=46)
    lamp_at = tuple(m @ Vector((.5, 1.35, .05)))
    K.lamp(a, lamp_at, facing=_dir(DOOR) + (-.3,), r=.06, guard=True)
    # The vent stack on the rear-right face, the ammunition pit beside it.
    vx, vy = _dir(160, BAP + .1)
    k.lathe(a.part('Vents', 'Steel'), [(.08, 0), (.08, 1.95), (.16, 1.97), (.16, 2.06), (0, 2.12)],
            loc=(vx, vy, G), seg=8, worn=(3,))
    sx, sy = _dir(140, 2.05)
    W.bags(a, [(sx + .5, sy - .3, G), (sx - .2, sy + .5, G)], layers=2, bag=(.5, .28, .15), seed=47)
    W.stack(a, (sx - .25, sy - .25, G), n=3, size=(.5, .28, .2), yaw=.7, seed=48)
    if stacks > 1:
        W.stack(a, (sx + .3, sy + .2, G), n=2, size=(.5, .28, .2), yaw=.4, seed=49)
    if not flame:
        k.block(a.part('Barrel_case', 'Wood'), (.2, 1.25, .16), loc=(sx + .05, sy + .55, G + .08), rot=(0, 0, .9),
                chamfer=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (*_dir(185, 1.45), RZ1), h=1.6, r=.02)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (*_dir(-125, 2.0), G), rot=(0, 0, .4))
    jx, jy = _dir(-120, 2.0)
    K.clutter(a, 'Cases', 'Crate', jx - .1, jx + .5, jy - .6, jy + .1, G, 3, seed=52, size=(.15, .35), height=(.1, .3))
    # Wire in front: a concertina on pickets.
    _concertina(a, [(*_dir(h, 2.12), G) for h in range(-72, 73, 12)])
    _stones(a, 16, 1.95, 2.25, seed=50, skip=lambda x, y: y < -1.2)
    # Pickets and range stakes round the berm's toe (varied heights, the gunners' range marks).
    pk = a.part('Pickets', 'Wood')
    rng = random.Random(53)
    for h in range(-110, 181, 26):
        if -178 < h < -122:
            continue
        x, y = _dir(h, 2.18)
        ht = rng.choice((.5, .6, .7, .8, .95))
        pk.box((.04, .04, ht), loc=(x, y, G + ht / 2 - .05), rot=(0, 0, rng.uniform(0, 1)), bevel=0)
    a.part('Sign_posts', 'Wood').box((.05, .05, 1.0), loc=(*_dir(-100, 2.05), G + .45), bevel=0)
    a.part('Signs', 'PlasterWhite').box((.4, .03, .28), loc=(*_dir(-100, 2.05), G + .85), rot=(0, 0, .3), bevel=0)


def _bunker_base(a, courses=1):
    _bunker_shell(a)
    _berm(a, courses)


def mg_bunker(a, detail=False):
    """The MG bunker: one NSV in the cupola, a PKM in each of the four ports (module docstring)."""
    _bunker_base(a)
    for i, h in enumerate(PORTS):
        _embrasure(a, h)
        _port_gun(a, i, h)
    t = _cupola(a)
    el = a.pivot('Elevation', (0, -.8, .2), t)
    K.chamfer_box(a.part('Mantlet', 'Armor', el), (.28, .2, .22), loc=(0, -.05, 0), c=.03)
    end = _nsv(a, el, 0, 'Main_cannon', 'Muzzle_brake', .92)
    a.pivot('Muzzle_main', end, el)
    a.part('Ammo_belt', 'Gilded', el).tube([(.08, .05, .04), (.16, .2, .08), (.22, .35, .05)], .022, seg=4)
    _bunker_rear(a)
    k.clean(a)


def mg_bunker_a(a, detail=False):
    """The twin MG bunker (the .twin branch): the collared cupola with twin jacketed NSVs, the four port PKMs."""
    _bunker_base(a, courses=2)
    for i, h in enumerate(PORTS):
        _embrasure(a, h)
        _port_gun(a, i, h)
    t = _cupola(a, collar=True)
    el = a.pivot('Elevation', (0, -.8, .2), t)
    K.chamfer_box(a.part('Twin_mantlet', 'Team', el), (.62, .26, .28), loc=(0, -.06, 0), c=.04)
    end = _nsv(a, el, -.17, 'Main_cannon', 'Muzzle_brake', 1.3, jacket=True)
    _nsv(a, el, .17, 'Main_cannon_2', 'Muzzle_brake_2', 1.3, jacket=True)
    a.pivot('Muzzle_main', (0, end[1], end[2]), el)
    belt = a.part('Ammo_belt', 'Gilded', el)
    for s in (-1, 1):
        belt.tube([(s * .3, .02, .05), (s * .4, .2, .1), (s * .45, .38, .06)], .022, seg=4)
    _bunker_rear(a, stacks=2)
    k.clean(a)


def mg_bunker_b(a, detail=False):
    """The flame bunker (the .flame branch): the flame gun in the cupola, the ports shut, the fuel tanks behind."""
    _bunker_base(a)
    for h in PORTS:
        _embrasure(a, h)
        _port_shutter(a, h)
    t = _cupola(a)
    el = a.pivot('Elevation', (0, -.8, .2), t)
    fg = a.part('Flame_gun', 'Steel', el)
    k.lathe(fg, [(.09, 0), (.09, .25), (.065, .3), (.06, 1.0), (.075, 1.02), (.075, 1.1), (0, 1.1)],
            loc=(0, -.05, 0), rot=K.FORWARD, seg=10, worn=(1, 4))
    for y in (-.45, -.75):
        fg.cyl(.072, .04, loc=(0, y, 0), rot=K.FORWARD, seg=10, bevel=0)
    a.part('Igniter', 'Armor', el).box((.07, .2, .08), loc=(0, -1.0, -.1), bevel=.01)
    k.ring(a.part('Nozzle_soot', 'Charred', el), [(.06, 0), (.08, 0), (.08, .05), (.06, .05)], loc=(0, -1.13, 0),
           rot=K.FORWARD, seg=10)
    a.pivot('Muzzle_main', (0, -1.18, 0), el)
    K.soot(a, (0, -1.6, RZ1 + .2), radius=.6, k=.4)
    _bunker_rear(a, flame=True)
    # The fuel tanks on their cradle behind, the hose up the wall to the race, gas bottles, marks.
    tx, ty = _dir(125, 2.25)
    ft = a.part('Fuel_tanks', 'BarrelRed')
    cr = a.part('Tank_cradle', 'Steel')
    for dy in (-.3, .3):
        k.lathe(ft, [(.24, 0), (.27, .05), (.27, 1.15), (.24, 1.2), (0, 1.2)], loc=(tx - .6, ty + dy, G + .4),
                rot=(0, R90, 0), seg=10, worn=(1, 2))
    for xx in (-.45, .45):
        cr.box((.08, .9, .3), loc=(tx + xx, ty, G + .15), bevel=0)
    hx, hy = _dir(175, BAP + .06)
    a.part('Hoses', 'Rubber').tube([(tx - .3, ty, G + .55), (hx, hy + .1, .6), (hx, hy, RZ0 - .1),
                                    (hx * .7, hy * .7, RZ1 + .03)], .035, seg=6)
    gb = a.part('Gas_bottles', 'Hazard')
    for j in range(2):
        k.lathe(gb, [(.1, 0), (.1, .75), (.05, .85), (0, .86)], loc=(tx + .75, ty - .25 + j * .24, G), seg=8)
    vp = a.part('Tank_vents', 'Steel')
    for dy, h in ((-.3, .55), (.3, .7)):
        vp.cyl(.02, h, loc=(tx + .45, ty + dy, G + .66 + h / 2), seg=4, bevel=0)
        vp.box((.08, .05, .05), loc=(tx + .45, ty + dy, G + .68 + h), bevel=0)
    rp = a.part('Range_post', 'Wood')
    for h, (hd, r) in zip((.7, .9, 1.1), ((-40, 2.1), (8, 2.18), (52, 2.1))):
        rp.box((.05, .05, h), loc=(*_dir(hd, r), G + h / 2), bevel=0)
        a.part('Range_marks', 'Hazard').box((.12, .02, .08), loc=(*_dir(hd, r), G + h - .06), rot=(0, 0, .4),
                                            bevel=0)
    m, rot = _face_frame(-150, BAP, 1.0)
    a.part('Hazard_marks', 'Hazard').box((.42, .3, .01), loc=tuple(m @ Vector((-.62, .1, .01))), rot=rot, bevel=0)
    k.clean(a)


# ============================================================================= guard tower family
GP = 1.36          # pier centres (x, y = +-GP)
GZ0 = .42          # leg feet (pier tops)
GD = 7.5           # deck top
GT = .98           # leg tops (x, y = +-GT)
CAB = 1.12         # cab half width (octagon)
CZ1, CZ2 = 8.45, 9.3   # cab: armour wall top, glass top
RF = 9.58          # roof top


def _oct(r, chamf=.32):
    """An octagon (a square of half side r with its corners cut by chamf), counter-clockwise."""
    c = r - chamf
    return [(r, -c), (r, c), (c, r), (-c, r), (-r, c), (-r, -c), (-c, -r), (c, -r)]


def _leg_r(z):
    return GP + (GT - GP) * (z - GZ0) / (GD - GZ0)


def _guard_frame(a):
    """Piers, gravel pad, the four raked legs, X bracing in three tiers, girts, the deck, its joists and rail."""
    base = a.part('Base', 'Concrete')
    _pad(base, (3.4, 3.4, .06), loc=(0, 0, .03), chamfer=.02)
    plates = a.part('Base_plates', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.block(base, (.64, .64, GZ0), loc=(sx * GP, sy * GP, GZ0 / 2), chamfer=.04, taper=(.85, .85))
            plates.box((.36, .36, .03), loc=(sx * GP, sy * GP, GZ0 + .015), bevel=0)
    fr = a.part('Tower_frame', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            fr.limb((sx * GP, sy * GP, GZ0), (sx * GT, sy * GT, GD - .1), .17, .17, bevel=0)
    tiers = (GZ0 + .1, 2.8, 5.15, GD - .14)
    br = a.part('Tower_braces', 'Steel')
    for z0, z1 in zip(tiers, tiers[1:]):
        for face in range(4):
            u = face * R90
            c, s_ = math.cos(u), math.sin(u)

            def at(t, z):
                r = _leg_r(z)
                return (c * r - s_ * r * t, s_ * r + c * r * t, z)
            br.limb(at(-1, z0), at(1, z1), .07, .05, bevel=0)
            br.limb(at(1, z0), at(-1, z1), .07, .05, bevel=0)
            br.limb(at(-1, z1), at(1, z1), .09, .07, bevel=0)
    deck = a.part('Walkway', 'Steel')
    k.block(deck, (3.1, 3.1, .12), loc=(0, 0, GD - .06), chamfer=.02)
    a.part('Walkway_grate', 'Undercarriage').box((2.9, 2.9, .01), loc=(0, 0, GD + .002), bevel=0)
    js = a.part('Walkway_joists', 'Steel')
    for x in (-1.0, 0, 1.0):
        js.box((.1, 3.0, .18), loc=(x, 0, GD - .21), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            js.limb((sx * _leg_r(GD - .8), sy * _leg_r(GD - .8), GD - .8), (sx * 1.45, sy * 1.45, GD - .14), .06,
                    .06, bevel=0)
    # The rail round the deck, open at the ladder's head (rear, x .55); the Team kick plates.
    e = 1.5
    K.railing(a.part('Railing', 'Steel'), [(.22, e, GD), (-e, e, GD), (-e, -e, GD), (e, -e, GD), (e, e, GD),
                                           (.88, e, GD)], h=1.0, post=1.0, r=.022)
    kp = a.part('Kick_plates', 'Team')
    kp.box((3.0, .02, .12), loc=(0, -e, GD + .06), bevel=0)
    for s_ in (-1, 1):
        kp.box((.02, 3.0, .12), loc=(s_ * e, 0, GD + .06), bevel=0)


def _guard_ladder(a):
    """The caged ladder up the rear from the ground to the deck's gap."""
    x, y = .55, 1.62
    K.ladder(a.part('Ladder', 'Steel'), (x, y, .05), (x, y, GD + 1.0), width=.46, step=.32, r=.02, facing=(0, 1))
    cage = a.part('Ladder_cage', 'Steel')
    for z in (2.6, 3.6, 4.6, 5.6, 6.6):
        pts = [(x + .3 * math.cos(u), y + .38 * math.sin(u), z) for u in [i * math.pi / 5 for i in range(6)]]
        cage.tube(pts, .014, seg=3, caps=False)
    for dx, dy in ((-.26, .2), (0, .38), (.26, .2)):
        cage.tube([(x + dx, y + dy, 2.6), (x + dx, y + dy, GD - .15)], .012, seg=3, caps=False)


def _guard_cab(a):
    """The armoured cab: armour wall, the sloped glass band and mullions, fascia and roof, parapet, door, the RPG
    screen, the aircon unit, lamp, sign, searchlight, antenna, beacon."""
    cab = a.part('Cabin', 'Team')
    k.extrude(cab, _oct(CAB), CZ1 - GD, loc=(0, 0, (GD + CZ1) / 2), axis='Z', chamfer=.02, taper=(1.03, 1.03))
    gl = a.part('Cabin_glass', 'Glass')
    k.extrude(gl, _oct(CAB * 1.02, .33), CZ2 - CZ1, loc=(0, 0, (CZ1 + CZ2) / 2), axis='Z', taper=(1.09, 1.09),
              caps=(False, False))
    mul = a.part('Mullions', 'Steel')
    for x, y in _oct(CAB * 1.02, .33):
        mul.limb((x, y, CZ1), (x * 1.09, y * 1.09, CZ2), .06, .06, bevel=0)
    k.extrude(a.part('Cabin_fascia', 'Team'), _oct(CAB * 1.16, .38), RF - CZ2 - .1, loc=(0, 0, CZ2 + (RF - CZ2 - .1) / 2),
              axis='Z', chamfer=.03)
    k.extrude(a.part('Roof', 'Armor'), _oct(CAB * 1.24, .42), .1, loc=(0, 0, RF - .05), axis='Z', chamfer=.03)
    par = a.part('Parapet', 'Armor')
    for u in range(4):
        c, s_ = math.cos(u * R90), math.sin(u * R90)
        r = CAB * 1.18
        par.box((.05, 1.3, .34), loc=(c * r, s_ * r, RF + .17), rot=(0, 0, u * R90), bevel=0)
    sea = a.part('Fittings', 'Steel')
    for u in range(4):
        c, s_ = math.cos(u * R90), math.sin(u * R90)
        sea.box((.03, 1.2, .03), loc=(c * (CAB + .03), s_ * (CAB + .03), GD + .45), rot=(0, 0, u * R90), bevel=0)
    K.door(a, (0, CAB + .02, GD + .02), size=(.7, 1.72), normal=(0, 1, 0), mat='Armor')
    # The RPG screen: a bar grille on outriggers in front of the cab's front and both sides.
    scr = a.part('Slat_screen', 'Steel')
    o = CAB + .48
    for p0, p1, n in (((-o, -o), (o, -o), (0, -1)), ((o, -o), (o, o - .6), (1, 0)), ((-o, -o), (-o, o - .6), (-1, 0))):
        p0, p1 = Vector(p0), Vector(p1)
        span = p1 - p0
        cnt = int(span.length / .3)
        for i in range(cnt + 1):
            p = p0 + span * (i / cnt)
            scr.box((.025, .025, 1.25), loc=(p.x, p.y, GD + .82), bevel=0)
        c = (p0 + p1) / 2
        for z in (GD + .2, GD + .62, GD + 1.04, GD + 1.42):
            scr.box((abs(span.x) + .03, abs(span.y) + .03, .035), loc=(c.x, c.y, z), bevel=0)
        for f in (.06, .94):
            p = p0 + span * f
            scr.limb((p.x - n[0] * .46, p.y - n[1] * .46, GD + .12), (p.x, p.y, GD + .2), .04, .04, bevel=0)
    k.block(a.part('Aircon', 'PlasterWhite'), (.24, .62, .42), loc=(-(CAB + .14), .5, GD + .5), chamfer=.02)
    a.part('Aircon_fan', 'Undercarriage').cyl(.15, .02, loc=(-(CAB + .265), .5, GD + .52), rot=(0, R90, 0), seg=8,
                                               bevel=0)
    K.lamp(a, (.55, CAB + .05, GD + 1.85), facing=(0, 1, -.4), r=.06, guard=True)
    a.part('Stencil', 'PlasterWhite').box((.5, .015, .28), loc=(-.4, -(CAB + .035), GD + .5), bevel=0)
    sx, sy = CAB * .82, CAB * .82
    a.part('Searchlight_post', 'Steel').cyl(.04, .4, loc=(sx, sy, RF + .2), seg=6, bevel=0)
    yk = a.part('Searchlight_yoke', 'Steel')
    for s_ in (-1, 1):
        yk.box((.03, .05, .26), loc=(sx + s_ * .17, sy, RF + .5), rot=(0, 0, .6), bevel=0)
    srot = (R90 - .25, 0, math.pi * .75)
    k.lathe(a.part('Searchlight', 'Armor'), [(.13, -.16), (.15, -.12), (.15, .12), (.17, .14), (.17, .18)],
            loc=(sx, sy, RF + .55), rot=srot, seg=10)
    lens = Matrix.Translation((sx, sy, RF + .55)) @ Matrix.Rotation(srot[2], 4, 'Z') @ Matrix.Rotation(srot[0], 4, 'X')
    a.part('Searchlight_lens', 'Lamp').cyl(.14, .02, loc=tuple(lens @ Vector((0, 0, .17))), rot=srot, seg=10, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-CAB * .8, CAB * .8, RF), h=2.0, r=.018)
    K.beacon(a, (-CAB * .8, -CAB * .75, RF), r=.08)


def _guard_turret(a):
    """The roof ring mount (`Turret`) with the M2 on its cradle (`Elevation`) behind a shield."""
    k.ring(a.part('Race', 'Steel'), [(.5, 0), (.62, 0), (.62, .08), (.5, .08)], loc=(0, -.1, RF), seg=12)
    t = a.pivot('Turret', (0, -.1, RF + .08))
    tb = a.part('Turret_ring', 'Armor', t)
    k.ring(tb, [(.5, 0), (.6, 0), (.6, .12), (.5, .12)], seg=12)
    tb.box((.08, 1.0, .05), loc=(0, 0, .1), bevel=0)
    k.lathe(a.part('MG_post', 'Steel', t), [(.06, .1), (.06, .62), (.09, .64), (.09, .72), (0, .72)],
            loc=(0, .05, 0), seg=8, worn=(2,))
    # The shield on the yaw (the gun elevates behind it): a raked plate with wings and a sight window.
    sh = a.part('MG_shield', 'Armor', t)
    k.extrude(sh, [(-.36, -.25), (.36, -.25), (.32, .25), (-.32, .25)], .035, loc=(0, -.42, .87),
              rot=(R90 - .12, 0, 0), axis='Z', chamfer=.01, corner=.02)
    for s_ in (-1, 1):
        sh.box((.035, .3, .46), loc=(s_ * .41, -.32, .85), rot=(0, 0, s_ * .5), bevel=0)
    a.part('Shield_slot', 'Undercarriage').box((.22, .02, .06), loc=(0, -.465, 1.02), rot=(-.12, 0, 0), bevel=0)
    el = a.pivot('Elevation', (0, .05, .82), t)
    mg = a.part('MG', 'Steel', el)
    k.block(mg, (.13, .62, .16), loc=(0, .08, -.08), chamfer=.015)
    for s_ in (-1, 1):
        mg.limb((s_ * .05, .38, 0), (s_ * .07, .5, -.03), .03, .03, bevel=0)
    k.lathe(a.part('Main_cannon', 'Steel', el), [(.045, 0), (.045, .32), (.024, .36), (.022, 1.08), (0, 1.08)],
            loc=(0, -.22, 0), rot=K.FORWARD, seg=8, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', el), [(.022, 0), (.036, .02), (.036, .12), (0, .12)],
            loc=(0, -1.27, 0), rot=K.FORWARD, seg=8)
    a.pivot('Muzzle_main', (0, -1.4, 0), el)
    k.block(a.part('MG_ammo', 'Armor', el), (.12, .26, .17), loc=(.16, .06, -.16), chamfer=.015)
    K.soot(a, (0, -1.6, RF + .9), radius=.3, k=.3)
    return t


def _guard_ground(a):
    """Sandbags between the front and left piers, the generator box with its exhaust and cable, dust."""
    W.bags(a, [(-1.0, -GP - .05, .06), (1.0, -GP - .05, .06)], layers=2, bag=(.52, .3, .15), seed=60)
    W.bags(a, [(GP + .05, -.9, .06), (GP + .05, .6, .06)], layers=2, bag=(.52, .3, .15), seed=61)
    k.block(a.part('Generator', 'Armor'), (.9, .6, .7), loc=(-.4, .45, .41), chamfer=.03)
    K.grille(a, (-.4, .14, .45), .6, .4, facing=(0, -1, 0), slats=4)
    K.exhaust(a, (-.7, .6, .76), r=.04, length=.35)
    a.part('Kit_cables', 'Rubber').tube([(-.4, .75, .6), (-.1, 1.05, .7), (GT * .3, _leg_r(4.0), 4.0),
                                         (.0, 1.25, GD - .15)], .02, seg=4)
    for x, y in ((1.5, 1.5), (-1.5, 1.5), (1.5, -1.5), (-1.5, -1.5)):
        K.dust(a, (x, y, 0), radius=1.3, k=.3)


def _watch_mast(a):
    """The .watch branch's telescopic sensor mast: three tube stages, the EO ball, the turning radar panel."""
    x, y, z = -CAB * .78, CAB * .55, RF
    k.lathe(a.part('Watch_mast', 'Steel'), [(.09, 0), (.09, 1.3), (.07, 1.32), (.07, 2.5), (.055, 2.52), (.055, 3.4),
                                            (0, 3.42)], loc=(x, y, z), seg=8, worn=(1, 3))
    a.part('Watch_band', 'Team').cyl(.1, .14, loc=(x, y, z + .9), seg=8, bevel=0)
    a.part('Watch_cap', 'Armor').box((.22, .3, .2), loc=(x, y, z + .2), bevel=.01)
    eo = a.part('EO_ball', 'Armor')
    eo.sphere(.17, loc=(x, y - .22, z + 2.75), seg=10, rings=6)
    eo.box((.06, .2, .06), loc=(x, y - .1, z + 2.75), bevel=0)
    a.part('Glass', 'Glass').box((.14, .02, .1), loc=(x, y - .39, z + 2.77), bevel=0)
    a.pivot('Radar', (x, y, z + 3.42))
    k.block(a.part('Radar_mount', 'Steel', 'Radar'), (.16, .16, .14), loc=(0, 0, .07), chamfer=.01)
    k.block(a.part('Radar_face', 'Armor', 'Radar'), (1.2, .1, .34), loc=(0, -.05, .32), rot=(-.25, 0, 0), chamfer=.02)
    a.part('Radar_bar', 'Undercarriage', 'Radar').box((1.1, .02, .26), loc=(0, -.11, .32), rot=(-.25, 0, 0), bevel=0)
    K.beacon(a, (x + .5, y + .3, z), r=.07)


def _guard_tower(a, watch=False):
    _guard_frame(a)
    _guard_ladder(a)
    _guard_cab(a)
    _guard_turret(a)
    _guard_ground(a)
    if watch:
        _watch_mast(a)
    k.clean(a)


def guard_tower(a, detail=False):
    """The guard tower (module docstring)."""
    _guard_tower(a)


def guard_tower_a(a, detail=False):
    """The guard tower's .watch branch: the tower with the telescopic sensor mast and turning radar."""
    _guard_tower(a, watch=True)


# ============================================================================= laser defence tower
LT_Y = -1.55               # tower centre y
LT_B, LT_T = 1.08, .8      # tower half width at the foot and at the top
LT_Z0, LT_Z1 = .15, 5.0
LD = LT_Z1 + .12           # platform top
MOD_Y0, MOD_Y1 = -.35, 2.85
MOD_X = 1.18
MOD_Z1 = 2.35


def _lt_r(z):
    return LT_B + (LT_T - LT_B) * (z - LT_Z0) / (LT_Z1 - LT_Z0)


def _laser_tower_body(a):
    """The pad, the clad tapered tower, seams, Team band, corner angles, door, the four fixed radar panels, the
    platform, railing, ladders, cable riser, obstruction lamps."""
    _pad(a.part('Base', 'Concrete'), (3.95, 6.0, .15), loc=(0, 0, .075), chamfer=.03, taper=(.93, .95))
    jb = a.part('Junction_boxes', 'Steel')
    for i, (z, w, h) in enumerate(((1.0, .3, .4), (1.6, .22, .3), (2.2, .35, .25))):
        jb.box((.12, w, h), loc=(-_lt_r(z) - .06, LT_Y - .3 + i * .25, z), bevel=0)
    a.part('Conduit', 'Steel').tube([(-_lt_r(.4) - .05, LT_Y + .45, .2), (-_lt_r(2.4) - .05, LT_Y + .45, 2.4),
                                     (-_lt_r(4.6) - .05, LT_Y + .45, 4.6)], .03, seg=4)
    K.clutter(a, 'Cases', 'Team', .3, 1.85, -2.85, -2.3, .15, 3, seed=71, size=(.2, .5), height=(.15, .4))
    K.clutter(a, 'Roof_fittings', 'Steel', -1.0, 1.0, -.25, .9, MOD_Z1, 6, seed=72, size=(.1, .35),
              height=(.06, .3))
    K.clutter(a, 'Platform_boxes', 'Armor', -.95, .95, LT_Y + .55, LT_Y + .95, LD, 3, seed=73, size=(.1, .3),
              height=(.1, .35))
    bolts = a.part('Kit_bolts', 'Steel')
    for u in range(4):
        c, s_ = math.cos(u * R90), math.sin(u * R90)
        for z in (.5, 1.9, 2.3):
            r = _lt_r(z) + .015
            for t in (-.7, -.35, 0, .35, .7):
                t2 = t * r / LT_B
                bolts.box((.03, .04, .04), loc=(c * r - s_ * t2, LT_Y + s_ * r + c * t2, z), rot=(0, 0, u * R90),
                          bevel=0)
    clamps = a.part('Cable_clamps', 'Steel')
    for i, z in enumerate((.8, 1.6, 2.4, 3.2, 3.9)):
        clamps.box((.1, .06 + i * .01, .05 + (i % 2) * .02), loc=(-_lt_r(z) - .05, LT_Y + .45, z), bevel=0)
    a.part('Pad_joints', 'Undercarriage').box((3.9, .03, .01), loc=(0, -.5, .152), bevel=0)
    k.extrude(a.part('Walls', 'Armor'), [(-LT_B, -LT_B), (LT_B, -LT_B), (LT_B, LT_B), (-LT_B, LT_B)], LT_Z1 - LT_Z0,
              loc=(0, LT_Y, (LT_Z0 + LT_Z1) / 2), axis='Z', chamfer=.04, corner=.08,
              taper=(LT_T / LT_B, LT_T / LT_B))
    tilt = math.atan((LT_B - LT_T) / (LT_Z1 - LT_Z0))
    sea = a.part('Seams', 'Undercarriage')
    band = a.part('Team_band', 'Team')
    for u in range(4):
        c, s_ = math.cos(u * R90), math.sin(u * R90)
        for z, part, hgt in ((1.4, sea, .025), (2.6, sea, .025), (3.15, band, .24)):
            r = _lt_r(z) + .012
            part.box((.02, 2 * r - .12, hgt), loc=(c * r, LT_Y + s_ * r, z), rot=(0, 0, u * R90), bevel=0)
    ang = a.part('Corner_angles', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            ang.limb((sx * (LT_B - .03), LT_Y + sy * (LT_B - .03), LT_Z0),
                     (sx * (LT_T - .03), LT_Y + sy * (LT_T - .03), LT_Z1), .1, .1, bevel=0)
    K.door(a, (_lt_r(.15) + .01, LT_Y + .1, LT_Z0), size=(.7, 1.8), normal=(1, 0, 0), mat='Armor')
    zc = 4.15
    for u in range(4):
        au = u * R90
        n = Vector((math.cos(au), math.sin(au), math.tan(tilt))).normalized()
        rot = K.rot_to(tuple(n))
        r = _lt_r(zc)
        c = Vector((math.cos(au) * (r + .06), LT_Y + math.sin(au) * (r + .06), zc))
        K.plate(a.part('Search_panel', 'Steel'), (1.22, 1.1, .1), loc=tuple(c), rot=rot, chamfer=.02)
        m = K.frame(tuple(c), rot)
        a.part('Panel_face', 'Undercarriage').box((1.08, .96, .02), loc=tuple(m @ Vector((0, 0, .055))), rot=rot,
                                                   bevel=0)
        gr = a.part('Panel_grid', 'Steel')
        for i in (-1, 0, 1):
            gr.box((.012, .96, .01), loc=tuple(m @ Vector((i * .27, 0, .068))), rot=rot, bevel=0)
        gr.box((1.08, .012, .01), loc=tuple(m @ Vector((0, 0, .068))), rot=rot, bevel=0)
    k.block(a.part('Roof_deck', 'Steel'), (2.25, 2.25, .12), loc=(0, LT_Y, LD - .06), chamfer=.02)
    br = a.part('Deck_brackets', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            br.limb((sx * _lt_r(LT_Z1 - .5), LT_Y + sy * _lt_r(LT_Z1 - .5), LT_Z1 - .5),
                    (sx * 1.06, LT_Y + sy * 1.06, LD - .12), .06, .06, bevel=0)
    e = 1.08
    K.railing(a.part('Railings', 'Steel'), [(.28, LT_Y + e, LD), (e, LT_Y + e, LD), (e, LT_Y - e, LD),
                                            (-e, LT_Y - e, LD), (-e, LT_Y + e, LD), (-.28, LT_Y + e, LD)],
              h=.95, post=1.0, r=.02)
    lad = a.part('Ladders', 'Steel')
    K.ladder(lad, (0, LT_Y + _lt_r(MOD_Z1) + .22, MOD_Z1), (0, LT_Y + _lt_r(MOD_Z1) + .22, LD + .9), width=.44,
             step=.32, r=.02, facing=(0, 1))
    K.ladder(lad, (-MOD_X - .1, 1.6, .15), (-MOD_X - .1, 1.6, MOD_Z1 + .9), width=.44, step=.32, r=.02,
             facing=(-1, 0))
    tr = a.part('Cable_trough', 'Steel')
    tr.limb((.55, LT_Y + _lt_r(MOD_Z1) + .06, MOD_Z1 - .3), (.48, LT_Y + _lt_r(LT_Z1 - .3) + .06, LT_Z1 - .3), .2,
            .1, bevel=0)
    tr.box((.2, abs(MOD_Y0 - (LT_Y + _lt_r(MOD_Z1))) + .3, .1), loc=(.55, (MOD_Y0 + LT_Y + _lt_r(MOD_Z1)) / 2 + .1,
                                                                    MOD_Z1 - .3), bevel=0)
    for x, y in ((e - .05, LT_Y - e + .05), (-e + .05, LT_Y - e + .05)):
        k.lathe(a.part('Obstruction_lamps', 'LavaGlow'), [(.05, 0), (.05, .06), (0, .1)], loc=(x, y, LD + .95),
                seg=6)


def _laser_director(a):
    """The beam director: the turning drum (`Turret`), the yoke and trunnions, the director housing on `Elevation`
    with its aperture (`Muzzle_main`), the tracking sensor pod."""
    t = a.pivot('Turret', (0, LT_Y, LD))
    k.lathe(a.part('Turret_body', 'Armor', t), [(.62, 0), (.62, .22), (.55, .3), (.5, .38), (0, .38)], seg=14,
            caps=(False, True), worn=(1, 2))
    a.part('Turret_band', 'Team', t).cyl(.6, .06, loc=(0, 0, .14), seg=14, bevel=0)
    yk = a.part('Yoke', 'Armor', t)
    for s_ in (-1, 1):
        k.extrude(yk, [(-.22, .3), (.22, .3), (.14, 1.08), (-.14, 1.08)], .12, loc=(s_ * .56, 0, 0), axis='X',
                  chamfer=.02, corner=.03)
    trn = a.part('Trunnions', 'Steel', t)
    for s_ in (-1, 1):
        trn.cyl(.1, .1, loc=(s_ * .64, 0, .95), rot=(0, R90, 0), seg=10, bevel=0)
    el = a.pivot('Elevation', (0, 0, .95), t)
    k.lathe(a.part('Director', 'PlasterWhite', el), [(.3, -.55), (.42, -.45), (.45, -.2), (.45, .4), (.4, .58), (0, .62)],
            rot=K.FORWARD, seg=16, caps=(False, True), worn=(1, 4))
    k.ring(a.part('Aperture_rim', 'Steel', el), [(.3, 0), (.36, 0), (.36, .08), (.3, .08)], loc=(0, -.6, 0),
           rot=K.FORWARD, seg=16)
    a.part('Aperture', 'Glass', el).cyl(.31, .03, loc=(0, -.57, 0), rot=K.FORWARD, seg=16, bevel=0)
    a.part('Director_stripe', 'Team', el).cyl(.455, .1, loc=(0, -.05, 0), rot=K.FORWARD, seg=16, bevel=0)
    fins = a.part('Director_fins', 'Steel', el)
    for s_ in (-1, 1):
        fins.box((.03, .6, .08), loc=(s_ * .2, .1, .44), bevel=0)
    sp = a.part('Sensor_pod', 'Armor', el)
    k.lathe(sp, [(.13, -.25), (.13, .2), (0, .24)], loc=(0, -.1, .58), rot=K.FORWARD, seg=10)
    sp.box((.08, .2, .1), loc=(0, 0, .48), bevel=0)
    a.part('Sensor_lens', 'Glass', el).cyl(.09, .02, loc=(0, -.36, .58), rot=K.FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_main', (0, -.62, 0), el)


def _laser_module(a):
    """The power and cooling module behind the tower: ribbed shelter, rear doors and bars, chillers and fans, the
    APS sensor mast (`Mount_APS`), antennas, extinguisher, coolant bottles, pickets and tape, sandbags."""
    yc, ln = (MOD_Y0 + MOD_Y1) / 2, MOD_Y1 - MOD_Y0
    zc = (MOD_Z1 + .15) / 2
    k.block(a.part('Shelter', 'Corrugated'), (2 * MOD_X, ln, MOD_Z1 - .15), loc=(0, yc, zc), chamfer=.03)
    rb = a.part('Shelter_ribs', 'Steel')
    for i in range(7):
        y = MOD_Y0 + .2 + i * (ln - .4) / 6
        for s_ in (-1, 1):
            rb.box((.04, .05, MOD_Z1 - .25), loc=(s_ * (MOD_X + .02), y, zc), bevel=0)
    a.part('Shelter_band', 'Team').box((2 * MOD_X + .06, .3, .22), loc=(0, MOD_Y0 + .5, MOD_Z1 - .35), bevel=0)
    cc = a.part('Corner_castings', 'Steel')
    for sx in (-1, 1):
        for sy in (MOD_Y0, MOD_Y1):
            for z in (.2, MOD_Z1 - .05):
                cc.box((.16, .16, .1), loc=(sx * (MOD_X - .06), sy, z), bevel=0)
    dr = a.part('Shelter_doors', 'Corrugated')
    bars = a.part('Kit_bars', 'Steel')
    for s_ in (-1, 1):
        dr.box((MOD_X - .06, .05, MOD_Z1 - .3), loc=(s_ * MOD_X / 2, MOD_Y1 + .03, zc), bevel=0)
        for x in (.25, .75):
            bars.box((.035, .04, MOD_Z1 - .35), loc=(s_ * x * MOD_X, MOD_Y1 + .08, zc), bevel=0)
    k.block(a.part('Coolers', 'Steel'), (1.9, 1.5, .5), loc=(0, 1.75, MOD_Z1 + .25), chamfer=.03)
    for x in (-.45, .45):
        k.ring(a.part('Cooler_fans', 'Steel'), [(.3, 0), (.34, 0), (.34, .06), (.3, .06)], loc=(x, 1.75, MOD_Z1 + .5),
               seg=12)
        a.part('Fan_grilles', 'Undercarriage').cyl(.3, .02, loc=(x, 1.75, MOD_Z1 + .51), seg=12, bevel=0)
    K.grille(a, (.96, 1.75, MOD_Z1 + .25), 1.3, .36, facing=(1, 0, 0), slats=4)
    K.grille(a, (-.96, 1.75, MOD_Z1 + .25), 1.3, .36, facing=(-1, 0, 0), slats=4)
    mx, my = -MOD_X + .25, MOD_Y1 - .25
    a.part('Mast', 'Steel').cyl(.05, 1.4, loc=(mx, my, MOD_Z1 + .7), seg=6, bevel=0)
    a.pivot('Mount_APS', (mx, my, MOD_Z1 + 1.52))
    k.block(a.part('APS_sensor', 'Armor'), (.3, .22, .24), loc=(mx, my, MOD_Z1 + 1.52), chamfer=.02)
    a.part('Glass', 'Glass').box((.2, .02, .1), loc=(mx, my - .12, MOD_Z1 + 1.55), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (MOD_X - .2, MOD_Y1 - .2, MOD_Z1), h=1.8, r=.018)
    K.whip_antenna(a.part('Antennas', 'Steel'), (MOD_X - .2, .3, MOD_Z1), h=1.3, r=.018)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.08, 0), (.08, .5), (.04, .58), (0, .6)],
            loc=(MOD_X + .25, -.1, .15), seg=8)
    gb = a.part('Gas_bottles', 'Steel')
    for j in range(3):
        k.lathe(gb, [(.1, 0), (.1, .9), (.05, 1.0), (0, 1.01)], loc=(MOD_X + .3, .6 + j * .23, .15), seg=8)
    pk = a.part('Pickets', 'Wood')
    fence = [(-1.9, -.4, .8), (-1.85, -2.85, .8), (0, -2.95, .8), (1.85, -2.85, .8), (1.9, -.4, .8)]
    for x, y, _ in fence:
        pk.cyl(.025, .8, loc=(x, y, .5), seg=4, bevel=0)
    a.part('Tape', 'Hazard').tube(fence, .015, seg=3, caps=False)
    W.bags(a, [(-MOD_X - .45, 2.9, .15), (-MOD_X - .45, 2.1, .15)], layers=2, bag=(.5, .28, .15), seed=70)
    for x, y in ((1.6, 2.6), (-1.6, -2.6), (1.6, -2.6)):
        K.dust(a, (x, y, 0), radius=1.4, k=.3)


def laser_ad_station(a, detail=False):
    """The Laser Defence Tower (module docstring)."""
    _laser_tower_body(a)
    _laser_director(a)
    _laser_module(a)
    k.clean(a)

# ============================================================================= drone hangar family
CW = 2.44          # ISO container width
CL = 6.06          # length
CH = 2.59          # height
CX = 1.2 + CW / 2  # container centre x (the bay between them is 2.4 wide)
CY = .45           # containers' centre y
AP = .1            # apron top
DK = AP + CH       # deck underside
DKT = DK + .14     # deck top
CY0, CY1 = CY - CL / 2, CY + CL / 2


def _container(a, x):
    """One 20-foot container on the apron: the box, side corrugation ribs, corner castings, the end doors with
    their locking bars at the front, the Team stripe."""
    zc = AP + CH / 2
    _pad(a.part('Walls', 'Corrugated'), (CW, CL, CH), loc=(x, CY, zc), chamfer=.03)
    rb = a.part('Wall_ribs', 'Corrugated')
    s = 1 if x > 0 else -1
    for i in range(16):
        y = CY0 + .3 + i * (CL - .6) / 15
        rb.box((.05, .1, CH - .2), loc=(x + s * (CW / 2 + .02), y, zc), bevel=0)
    cc = a.part('Corner_castings', 'Steel')
    for sx in (-1, 1):
        for y in (CY0, CY1):
            for z in (AP + .06, AP + CH - .06):
                cc.box((.18, .18, .12), loc=(x + sx * (CW / 2 - .07), y, z), bevel=0)
    dr = a.part('Doors', 'Corrugated')
    bars = a.part('Kit_bars', 'Steel')
    for sx in (-1, 1):
        dr.box((CW / 2 - .1, .05, CH - .3), loc=(x + sx * CW / 4, CY0 - .03, zc), bevel=0)
        for f in (.25, .75):
            bars.box((.035, .05, CH - .35), loc=(x + sx * f * CW / 2, CY0 - .08, zc), bevel=0)
    a.part('Team_band', 'Team').box((.02, CL - .5, .3), loc=(x + s * (CW / 2 + .05), CY, AP + CH - .45), bevel=0)


def _drone_post(a):
    """Apron, the two containers, the bay roof deck and its roller door, the railing, the anti-drone net over the
    rear half, the antenna mast, generator, sandbags and crates. Returns nothing; the launcher is the caller's."""
    base = a.part('Base', 'Concrete')
    _pad(base, (7.6, CL + .4, AP), loc=(0, CY, AP / 2), chamfer=.02, taper=(.94, .92))
    k.extrude(base, [(-3.0, -3.95), (3.0, -3.95), (3.6, -3.4), (3.6, CY0 - .1), (-3.6, CY0 - .1), (-3.6, -3.4)], AP,
              loc=(0, 0, AP / 2), axis='Z', chamfer=.02)
    a.part('Base_joints', 'Undercarriage').box((7.8, .03, .01), loc=(0, -2.9, AP + .002), bevel=0)
    for x in (-CX, CX):
        _container(a, x)
    # The bay between them: back wall, a dark interior, the roller door half up under its drum.
    bay = a.part('Bay_walls', 'Corrugated')
    bay.box((2.4, .08, CH), loc=(0, CY1 - .05, AP + CH / 2), bevel=0)
    a.part('Interior', 'Undercarriage').box((2.36, .02, 1.5), loc=(0, CY0 + 1.4, AP + .76), bevel=0)
    k.block(a.part('Door_drum', 'Steel'), (2.5, .42, .42), loc=(0, CY0 - .12, DK - .22), chamfer=.03)
    sl = a.part('Door_slats', 'MetalSheet')
    for i in range(5):
        sl.box((2.36, .04, .18), loc=(0, CY0 + .02, DK - .53 - i * .19), bevel=0)
    gd = a.part('Door_guides', 'Steel')
    for sx in (-1, 1):
        gd.box((.08, .1, CH - .1), loc=(sx * 1.2, CY0 + .02, AP + CH / 2), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((2.4, .02, .1), loc=(0, CY0 - .02, AP + .06), bevel=0)
    # Drone racks seen inside the bay.
    rk = a.part('Racks', 'Steel')
    for x in (-.8, .8):
        rk.box((.5, .4, 1.3), loc=(x, CY0 + 1.2, AP + .65), bevel=0)
    for x in (-.8, .8):
        for z in (.45, .8, 1.15):
            a.part('Drone_boxes', 'Crate').box((.44, .36, .2), loc=(x, CY0 + 1.0, AP + z), bevel=0)
    # The roof deck over everything, its railing, the stair-ladder.
    _pad(a.part('Roof_deck', 'Armor'), (2 * (CX + CW / 2) + .1, CL + .1, .14), loc=(0, CY, DK + .07), chamfer=.02)
    mats = a.part('Deck_mats', 'Rubber')
    for x, y in ((-1.5, CY0 + 1.3), (1.6, CY0 + 1.0), (0, CY + 1.9)):
        mats.box((1.6, 1.1, .015), loc=(x, y, DKT + .008), bevel=0)
    W.bags(a, [(CX + CW / 2 - .25, CY0 + .3, DKT), (-CX - CW / 2 + .25, CY0 + .3, DKT)], layers=1, bag=(.55, .3, .16), seed=85,
           name='Parapet')
    e, f0, f1 = CX + CW / 2, CY0, CY1
    K.railing(a.part('Railings', 'Steel'), [(e - .7, f1, DKT), (e, f1, DKT), (e, f0, DKT), (-e, f0, DKT),
                                            (-e, f1, DKT), (e - 1.3, f1, DKT)], h=.95, post=1.2, r=.02)
    K.ladder(a.part('Ladders', 'Steel'), (e - 1.0, f1 + .5, AP), (e - 1.0, f1 + .05, DKT + .9), width=.5, step=.3,
             r=.02)
    # The anti-drone net over the deck's rear half on six poles.
    K.camo_net(a, [(-e + .1, .2, 1.95), (e - .1, .2, 1.95), (-e + .1, f1 - .1, 1.75), (e - .1, f1 - .1, 1.75),
                   (0, .2, 2.0), (0, f1 - .1, 1.8)], .12, DKT, part='Roof_net', garnish=8, seed=81)
    # Operators' gear under it: the ground station, the charging bench and batteries.
    k.block(a.part('Radio_box', 'Armor'), (.8, .5, .7), loc=(-1.6, 2.0, DKT + .35), chamfer=.03)
    a.part('Glass', 'Glass').box((.5, .02, .3), loc=(-1.6, 1.74, DKT + .5), bevel=0)
    k.block(a.part('Workbench', 'Wood'), (1.6, .6, .08), loc=(1.4, 2.4, DKT + .8), chamfer=.01)
    lg = a.part('Bench_legs', 'Steel')
    for dx in (-.7, .7):
        lg.box((.05, .5, .8), loc=(1.4 + dx, 2.4, DKT + .4), bevel=0)
    bt = a.part('Batteries', 'EliteBlack')
    for i in range(4):
        bt.box((.22, .15, .12), loc=(.9 + i * .32, 2.4, DKT + .9), bevel=0)
    # The antenna mast at the rear left corner, panel antennas and a whip.
    mx, my = e - .25, f1 - .25
    a.part('Antennas', 'Steel').cyl(.045, 2.6, loc=(mx, my, DKT + 1.3), seg=6, bevel=0)
    for u in (0, 3.1):
        K.mesh_antenna(a.part('Antennas', 'Steel'), (mx + math.sin(u) * .14, my - math.cos(u) * .14, DKT + 2.3),
                       w=.3, h=.45, normal=(math.sin(u), -math.cos(u), 0), bars=3)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-e + .3, f1 - .3, DKT), h=1.8, r=.018)
    # Ground: generator by the right container, sandbags at the front corners, jerrycans, crates, a floodlight.
    k.block(a.part('Generator', 'Armor'), (1.0, .65, .75), loc=(-.3, 3.05, DKT + .375), chamfer=.03)
    K.grille(a, (-.3, 2.715, DKT + .4), .7, .45, facing=(0, -1, 0), slats=4)
    K.exhaust(a, (-.65, 3.15, DKT + .75), r=.04, length=.4)
    for s_ in (-1, 1):
        W.bags(a, [(s_ * (e - .3), CY0 - .55, AP), (s_ * (e - 1.4), CY0 - .55, AP)], layers=2, bag=(.52, .3, .15),
               seed=82 + s_)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.0, -3.55, AP), rot=(0, 0, .2))
    K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.6, .4, .4), (1.8, -3.6, AP),
            rot=(0, 0, .2))
    K.lamp(a, (1.0, CY0 - .02, DK - .5), facing=(0, -1, -.4), r=.07, guard=True)
    # Equipment cases on the deck under the net, spares by the containers' sides.
    K.clutter(a, 'Cases', 'Team', -3.4, -.4, 2.3, 3.5, DKT, 5, seed=86, size=(.25, .6), height=(.15, .45))
    K.clutter(a, 'Deck_fittings', 'Steel', -3.3, 3.3, -.4, 1.4, DKT, 6, seed=89, size=(.1, .3), height=(.05, .25))
    bl = a.part('Kit_bolts', 'Steel')
    for x in (-CX, CX):
        for y in (CY0 + .6, CY0 + 2.0, CY0 + 3.4, CY0 + 4.8):
            for z in (AP + .5, AP + 1.4, AP + 2.2):
                bl.box((.06, .04, .06), loc=(x + (CW / 2 + .045) * (1 if x > 0 else -1), y, z), bevel=0)
    K.clutter(a, 'Spares', 'Crate', e + .06, e + .3, -2.2, 1.2, AP, 4, seed=87, size=(.2, .25), height=(.2, .6))
    K.clutter(a, 'Cable_reels', 'Undercarriage', -e - .3, -e - .06, -2.0, 2.4, AP, 4, seed=88, size=(.2, .25),
              height=(.2, .5))
    for x, y in ((3.5, -3.6), (-3.5, -3.6), (3.5, 3.6), (-3.5, 3.6)):
        K.dust(a, (x, y, 0), radius=1.6, k=.25)


def _fpv(a, loc, yaw=0.0, scale=1.0, tag=''):
    """An FPV quadcopter: the frame, four arms, motors, props, the battery."""
    x, y, z = loc
    sc = scale
    fr = a.part(f'Drones{tag}', 'EliteBlack')
    fr.box((.12 * sc, .2 * sc, .04 * sc), loc=(x, y, z), rot=(0, 0, yaw), bevel=0)
    a.part(f'Drone_batteries{tag}', 'Hazard').box((.07 * sc, .12 * sc, .04 * sc), loc=(x, y, z + .04 * sc),
                                                    rot=(0, 0, yaw), bevel=0)
    arms = a.part(f'Drone_arms{tag}', 'Steel')
    props = a.part(f'Drone_props{tag}', 'Undercarriage')
    for u in (.785, 2.356, 3.927, 5.498):
        ux, uy = math.cos(u + yaw) * .17 * sc, math.sin(u + yaw) * .17 * sc
        arms.limb((x, y, z), (x + ux, y + uy, z), .03 * sc, .02 * sc, bevel=0)
        props.cyl(.09 * sc, .005, loc=(x + ux, y + uy, z + .035 * sc), seg=6, bevel=0)


def _launch_points(a, p):
    a.pivot('Muzzle_main', p)
    a.pivot('Muzzle_door_l', p)


def drone_hangar(a, detail=False):
    """The drone hangar (fpv_hangar): the post with the FPV launch rail at the deck's front (module docstring)."""
    _drone_post(a)
    # The trestle rail at the deck's front right, raised 20 degrees, an FPV on its sled.
    rail = a.part('Launch_rail', 'Steel')
    x, y0, y1 = -1.5, CY0 + 2.2, CY0 + .35
    z0, z1 = DKT + .45, DKT + .45 + (y0 - y1) * math.tan(.35)
    for s_ in (-1, 1):
        rail.tube([(x + s_ * .12, y0, z0), (x + s_ * .12, y1, z1)], .025, seg=4)
    for t in (.15, .5, .85):
        yy, zz = y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        rail.box((.3, .04, .04), loc=(x, yy, zz), bevel=0)
    tr = a.part('Trestle', 'Steel')
    for yy, zz in ((y0 - .1, z0), (y1 + .25, z1 - .08)):
        for s_ in (-1, 1):
            tr.limb((x + s_ * .3, yy, DKT), (x + s_ * .12, yy, zz - .02), .04, .04, bevel=0)
    _fpv(a, (x, y0 + (y1 - y0) * .55, z0 + (z1 - z0) * .55 + .06), yaw=R90)
    _fpv(a, (1.2, 1.9, DKT + .9), yaw=.4, tag='')
    K.clutter(a, 'Drone_cases', 'Crate', -.6, .9, -1.4, -.5, DKT, 4, seed=90, size=(.2, .45), height=(.1, .3))
    K.clutter(a, 'Rail_spares', 'Steel', -3.3, -2.3, -1.6, -.6, DKT, 4, seed=91, size=(.08, .3), height=(.05, .2))
    _launch_points(a, (x, y1 - .1, z1 + .05))
    k.clean(a)


def drone_hangar_a(a, detail=False):
    """drone_hangar_a (lancet_hangar): the post with the Lancet pneumatic catapult on the deck."""
    _drone_post(a)
    rail = a.part('Launch_rail', 'Steel')
    x = -1.3
    y0, y1 = CY + 1.6, CY0 + .2
    z0, z1 = DKT + .35, DKT + .35 + (y0 - y1) * math.tan(.26)
    for s_ in (-1, 1):
        rail.tube([(x + s_ * .14, y0, z0), (x + s_ * .14, y1, z1)], .03, seg=4)
        rail.tube([(x + s_ * .1, y0, z0 - .22), (x + s_ * .1, y1, z1 - .22)], .02, seg=4)
    n = 7
    for i in range(n + 1):
        t = i / n
        yy, zz = y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        rail.limb((x - .12, yy, zz), (x + .1, yy + .25, zz - .22 + .06), .02, .02, bevel=0)
        rail.box((.3, .03, .03), loc=(x, yy, zz - .11), bevel=0)
    tr = a.part('Trestle', 'Steel')
    for t, h in ((.15, z0 - .2), (.75, z0 + (z1 - z0) * .75 - .2)):
        yy = y0 + (y1 - y0) * t
        for s_ in (-1, 1):
            tr.limb((x + s_ * .4, yy, DKT), (x + s_ * .12, yy, h), .05, .05, bevel=0)
    # The air bottle and compressor beside the rail's foot.
    k.lathe(a.part('Air_bottles', 'Hazard'), [(.16, 0), (.16, 1.1), (.08, 1.2), (0, 1.22)], loc=(x + .55, y0 - .3,
                                                                                                  DKT + .2),
            rot=(R90, 0, 0), seg=10)
    k.block(a.part('Compressor', 'Armor'), (.5, .6, .45), loc=(x + .65, y0 + .2, DKT + .22), chamfer=.02)
    a.part('Kit_cables', 'Rubber').tube([(x + .5, y0 + .1, DKT + .3), (x + .1, y0, z0 - .1)], .02, seg=4)
    # The Lancet on its shuttle: the body, the X-wings fore and aft.
    t = .35
    p = Vector((x, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t + .12))
    d = Vector((0, y1 - y0, z1 - z0)).normalized()
    body = a.part('Drones', 'Armor')
    rot = K.rot_to(tuple(-d))
    body.cyl(.07, 1.3, loc=tuple(p), rot=rot, seg=8, bevel=0)
    a.part('Drone_boxes', 'Undercarriage').cyl(.07, .12, loc=tuple(p + d * .7), rot=rot, seg=8, r2=.02, bevel=0)
    wings = a.part('Drone_arms', 'Steel')
    for off, span in ((.35, .5), (-.45, .4)):
        c = p + d * off
        for u in (.785, 2.356):
            m = Matrix.Translation(c) @ Matrix.Rotation(-math.atan2(d.z, -d.y), 4, 'X') @ Matrix.Rotation(u, 4, 'Y')
            wings.box((span * 2, .2, .015), loc=tuple(c), rot=m.to_euler('XYZ'), bevel=0)
    _launch_points(a, (x, y1 - .1, z1 + .05))
    k.clean(a)


def drone_hangar_b(a, detail=False):
    """drone_hangar_b (fpv_hangar_swarm): the post with the swarm launch cells (lids open, FPVs inside)."""
    _drone_post(a)
    cells = a.part('Launch_rail', 'Steel')
    lids = a.part('Cell_lids', 'Armor')
    x0, y0 = -1.9, CY0 + .55
    for i in range(3):
        for j in range(2):
            cx, cy = x0 + j * .62, y0 + .2 + i * .58
            cells.box((.56, .5, .32), loc=(cx, cy, DKT + .16), bevel=0)
            a.part('Cell_bores', 'Undercarriage').box((.46, .4, .01), loc=(cx, cy, DKT + .325), bevel=0)
            lids.box((.5, .03, .44), loc=(cx, cy + .27, DKT + .5), rot=(-.25, 0, 0), bevel=0)
            _fpv(a, (cx, cy, DKT + .28), yaw=.3 * i, scale=.9)
    k.block(a.part('Control_cabinet', 'Armor'), (.5, .4, 1.0), loc=(x0 + 1.4, y0 + .3, DKT + .5), chamfer=.02)
    a.part('Glass', 'Glass').box((.3, .02, .2), loc=(x0 + 1.4, y0 + .09, DKT + .75), bevel=0)
    a.part('Antennas', 'Steel').cyl(.03, 1.4, loc=(x0 + 1.5, y0 + .4, DKT + 1.7), seg=6, bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (x0 + 1.5, y0 + .3, DKT + 2.3), w=.35, h=.35, normal=(0, -1, 0),
                   bars=3)
    a.part('Kit_cables', 'Rubber').tube([(x0 + 1.2, y0 + .3, DKT + .2), (x0 + .9, y0 + .8, DKT + .05),
                                         (x0 + .3, y0 + 1.0, DKT + .05)], .02, seg=4)
    _launch_points(a, (x0 + .31, y0 + .8, DKT + .45))
    k.clean(a)


# ============================================================================= vehicle hangar (motor pool shed)
VX = 3.15          # shed half width
VY0, VY1 = -3.55, 3.5
VE, VR = 3.4, 4.45  # eave, ridge


def _gable(x):
    """Roof height at x."""
    return VE + (VR - VE) * (1 - abs(x) / VX)


def vehicle_hangar_base(a, detail=False):
    """The vehicle hangar (balance vehicle_hangar's model): a steel portal-frame motor-pool shed (module docstring)."""
    base = a.part('Base', 'Concrete')
    _pad(base, (6.7, 7.5, .12), loc=(0, 0, .06), chamfer=.02)
    _pad(base, (5.2, .5, .1), loc=(0, VY0 - .25, .05), chamfer=.02, taper=(1, .7))
    fl = a.part('Floor_lines', 'Hazard')
    for x in (-1.6, 1.6):
        fl.box((.08, 6.2, .01), loc=(x, -.3, .125), bevel=0)
    fl.box((3.2, .08, .01), loc=(0, VY0 - .1, .125), bevel=0)
    a.part('Oil_stains', 'Charred').cyl(.6, .01, loc=(.3, -.8, .123), seg=10, bevel=0)
    # Portal frames: columns and rafters at four bays.
    pf = a.part('Portal_frame', 'Steel')
    for y in (VY0, -1.2, 1.2, VY1):
        for s_ in (-1, 1):
            pf.box((.2, .22, VE), loc=(s_ * (VX - .1), y, .12 + VE / 2), bevel=0)
            pf.limb((s_ * (VX - .1), y, VE + .02), (0, y, VR - .05), .18, .22, bevel=0)
    # Cladding: side walls (corrugated with ribs), the rear wall, the front gable over the door.
    wl = a.part('Walls', 'Corrugated')
    for s_ in (-1, 1):
        wl.box((.06, VY1 - VY0, VE - .1), loc=(s_ * VX, (VY0 + VY1) / 2, .12 + (VE - .1) / 2), bevel=0)
    k.extrude(wl, [(-VX, .12), (VX, .12), (VX, VE), (0, VR), (-VX, VE)], .06, loc=(0, VY1, 0), axis='Y')
    k.extrude(wl, [(-VX, 3.25), (VX, 3.25), (VX, VE), (0, VR), (-VX, VE)], .06, loc=(0, VY0, 0), axis='Y')
    for s_ in (-1, 1):
        wl.box((VX - 2.2, .06, 3.2), loc=(s_ * (VX + 2.2) / 2, VY0, .12 + 1.6), bevel=0)
    rib = a.part('Wall_ribs', 'MetalSheet')
    for s_ in (-1, 1):
        for i in range(12):
            y = VY0 + .3 + i * (VY1 - VY0 - .6) / 11
            rib.box((.04, .06, VE - .2), loc=(s_ * (VX + .04), y, .12 + VE / 2), bevel=0)
    # The roof: two sheeted slopes with an overhang, the ridge cap, two turbine vents, gutters.
    rf = a.part('Roof', 'MetalSheet')
    pitch = math.atan((VR - VE) / VX)
    slope = math.hypot(VX, VR - VE) + .35
    for s_ in (-1, 1):
        rf.box((slope, VY1 - VY0 + .5, .06), loc=(s_ * (VX / 2 + .14), (VY0 + VY1) / 2, (VE + VR) / 2 + .06),
               rot=(0, s_ * pitch, 0), bevel=0)
    a.part('Ridge_cap', 'Steel').box((.24, VY1 - VY0 + .5, .06), loc=(0, (VY0 + VY1) / 2, VR + .11), bevel=0)
    # Roof sheet laps (ribs down the slope) and three skylight strips a side.
    lap = a.part('Roof_ribs', 'Steel')
    sky = a.part('Skylights', 'Glass')
    for s_ in (-1, 1):
        cx, cz = s_ * (VX / 2 + .14), (VE + VR) / 2 + .06
        nx, nz = -s_ * math.sin(pitch), math.cos(pitch)
        for i in range(12):
            y = VY0 - .2 + i * (VY1 - VY0 + .4) / 11
            lap.box((slope, .05, .03), loc=(cx + nx * .04, y, cz + nz * .04), rot=(0, s_ * pitch, 0), bevel=0)
        for y in (-2.3, .1, 2.3):
            sky.box((slope * .45, .75, .02), loc=(cx + nx * .035 - s_ * .25, y, cz + nz * .035 + .2), rot=(0, s_ * pitch, 0),
                    bevel=0)
    K.grille(a, (0, VY0 - .04, 3.85), .7, .35, facing=(0, -1, 0), slats=4)
    K.grille(a, (0, VY1 + .04, 3.85), .7, .35, facing=(0, 1, 0), slats=4)
    for y in (-1.2, 1.4):
        k.lathe(a.part('Ventilators', 'Steel'), [(.1, 0), (.1, .15), (.2, .2), (.22, .38), (.12, .46), (0, .48)],
                loc=(.6, y, _gable(.6) + .05), seg=8)
    gt = a.part('Gutters', 'Steel')
    for s_ in (-1, 1):
        gt.box((.12, VY1 - VY0 + .5, .1), loc=(s_ * (VX + .45), (VY0 + VY1) / 2, VE - .05), bevel=0)
        gt.box((.08, .08, VE - .1), loc=(s_ * (VX + .45), VY1 + .15, .12 + VE / 2), bevel=0)
    # The sectional door rolled up under its drum; the door opening's frame; the faction sign above.
    k.block(a.part('Door_drum', 'Steel'), (4.6, .45, .45), loc=(0, VY0 - .25, 3.0), chamfer=.03)
    dfr = a.part('Door_frames', 'Steel')
    for s_ in (-1, 1):
        dfr.box((.12, .14, 3.1), loc=(s_ * 2.22, VY0 - .06, .12 + 1.55), bevel=0)
    k.block(a.part('Sign', 'Team'), (1.4, .05, .5), loc=(0, VY0 - .05, 3.75), rot=K.FORWARD, chamfer=.01)
    a.part('Sign_mark', 'PlasterWhite').box((.6, .02, .1), loc=(0, VY0 - .09, 3.75), rot=(0, 0, 0), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((.1, .02, 1.2), loc=(2.3, VY0 - .14, .72), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((.1, .02, 1.2), loc=(-2.3, VY0 - .14, .72), bevel=0)
    # Inside: the dark back, the two-post lift with a jeep-sized load bay, the bench and cabinets, tyres, drums, hoist.
    a.part('Interior', 'Undercarriage').box((6.1, .02, 3.0), loc=(0, VY1 - .1, 1.6), bevel=0)
    lift = a.part('Vehicle_lift', 'CraneYellow')
    for s_ in (-1, 1):
        lift.box((.22, .3, 2.6), loc=(s_ * 1.45, .9, .12 + 1.3), bevel=.01)
        lift.box((.1, 1.2, .08), loc=(s_ * 1.0, .9, .9), bevel=0)
    lift.box((3.1, .2, .14), loc=(0, .9, 2.75), bevel=0)
    k.block(a.part('Bench_top', 'Wood'), (.7, 2.2, .08), loc=(2.6, 1.6, 1.0), chamfer=.01)
    bl = a.part('Bench_legs', 'Steel')
    for y in (.6, 2.6):
        bl.box((.6, .05, 1.0), loc=(2.6, y, .6), bevel=0)
    tc = a.part('Tool_cabinets', 'Team')
    for y in (-.4, .3):
        k.block(tc, (.55, .6, 1.5), loc=(2.75, y, .87), chamfer=.02)
    a.part('Bench_tools', 'Steel').box((.4, 1.4, .12), loc=(2.55, 1.6, 1.1), bevel=.01)
    ty = a.part('Tyres', 'Rubber')
    for i in range(2):
        k.ring(ty, [(.22, 0), (.38, 0), (.4, .1), (.38, .22), (.22, .22)], loc=(-2.55, 2.4, .12 + i * .23), seg=8)
    dr = a.part('Drums', 'BarrelRed')
    bd = a.part('Drum_bands', 'Steel')
    for i, (x, y) in enumerate(((-2.65, .9), (-2.1, .6))):
        K.fuel_drum(dr, bd, (x, y, .12))
    a.part('Hoist', 'Steel').box((.18, 4.5, .14), loc=(-1.0, .2, 3.25), bevel=0)
    a.part('Hoist_hook', 'CraneYellow').box((.12, .14, .5), loc=(-1.0, -.5, 2.9), bevel=.01)
    a.part('Hoist_chain', 'Steel').cyl(.012, .5, loc=(-1.0, -.5, 3.4 - .25), seg=4, bevel=0)
    # The office lean-to on the left side, its window and door, the whip on its roof.
    ox0, ox1 = VX + .06, VX + .82
    k.block(a.part('Office', 'Plaster'), (ox1 - ox0, 3.0, 2.5), loc=((ox0 + ox1) / 2, .4, .12 + 1.25), chamfer=.03)
    k.block(a.part('Office_roof', 'MetalSheet'), (ox1 - ox0 + .2, 3.2, .08), loc=((ox0 + ox1) / 2 + .05, .4, 2.66),
            rot=(0, -.12, 0), chamfer=.01)
    a.part('Glass', 'Glass').box((.02, 1.0, .6), loc=(ox1 + .01, 1.0, 1.6), bevel=0)
    a.part('Window_frames', 'Steel').box((.03, 1.1, .06), loc=(ox1 + .015, 1.0, 1.27), bevel=0)
    K.door(a, (ox1 + .01, -.5, .12), size=(.75, 1.95), normal=(1, 0, 0), mat='Armor')
    a.part('Antennas', 'Steel').cyl(.04, 2.6, loc=(ox1 - .2, 1.6, 2.7 + 1.3), seg=6, bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (ox1 - .2, 1.45, 4.6), w=.35, h=.5, normal=(0, -1, 0), bars=3)
    K.whip_antenna(a.part('Antennas', 'Steel'), (ox1 - .2, -.8, 2.7), h=1.8, r=.018)
    _shed_kit(a)
    # Outside: floodlights on the front columns, jerrycans, a tow bar, wheel chocks.
    for s_ in (-1, 1):
        K.lamp(a, (s_ * (VX - .1), VY0 - .15, 3.2), facing=(0, -1, -.5), r=.09, guard=False)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-VX - .35, -1.8, .12), rot=(0, 0, R90))
    a.part('Tow_bar', 'Steel').box((.1, 1.6, .08), loc=(-VX - .45, 1.2, .16), rot=(0, 0, .1), bevel=0)
    for x, y in ((3.6, -3.8), (-3.6, -3.8), (0, -3.9)):
        K.dust(a, (x, y, 0), radius=1.8, k=.3)
    k.clean(a)


def _shed_kit(a):
    """The motor-pool shed's fittings: floodlight poles, the roof's solar panels, faction panel, heater stack and
    roof walkway; AC units, the electrical cabinet and conduit, the gas cage, the oil tank, the pallet stack, spare
    tyres outside; the parts shelving and the engine stand inside."""
    for s_ in (-1, 1):
        K.floodlight(a, (s_ * 3.6, VY0 - .3, 0), facing=(-s_ * .3, -1, -.5), pole=4.6)
    pitch = math.atan((VR - VE) / VX)
    sol = a.part('Solar_panels', 'EliteBlack')
    sfr = a.part('Solar_frames', 'Steel')
    for i, y in enumerate((-2.6, -1.4, -.2)):
        x = -1.55
        z = _gable(x) + .14
        sol.box((1.5, 1.05, .03), loc=(x, y, z), rot=(0, -pitch, 0), bevel=0)
        sfr.box((1.56, .05, .06), loc=(x, y - .54, z - .01), rot=(0, -pitch, 0), bevel=0)
    a.part('Roof_mark', 'Team').box((1.3, 1.3, .02), loc=(1.6, 1.8, _gable(1.6) + .13), rot=(0, pitch, 0), bevel=0)
    a.part('Roof_mark_bar', 'PlasterWhite').box((.9, .22, .02), loc=(1.6, 1.8, _gable(1.6) + .15), rot=(0, pitch, .7),
                                                bevel=0)
    k.lathe(a.part('Heater_stack', 'Steel'), [(.09, 0), (.09, 1.3), (.18, 1.32), (.18, 1.42), (0, 1.5)],
            loc=(-2.3, 2.6, _gable(-2.3)), seg=8, worn=(3,))
    K.soot(a, (-2.3, 2.6, _gable(-2.3) + 1.45), radius=.35, k=.4)
    wk = a.part('Roof_walkway', 'Steel')
    for y in (-3.0, -1.5, 0, 1.5, 3.0):
        wk.box((.5, 1.2 + (y % 1.0) * .1, .04), loc=(.32, y, _gable(.32) + .17), rot=(0, pitch, 0), bevel=0)
    # The right wall: AC units, the electrical cabinet, conduit, the gas bottle cage.
    ac = a.part('Aircon', 'PlasterWhite')
    for y, w in ((-2.3, .8), (-1.2, .65)):
        k.block(ac, (.4, w, .55), loc=(-VX - .26, y, .45), chamfer=.02)
        a.part('Aircon_fan', 'Undercarriage').cyl(.2, .02, loc=(-VX - .47, y, .48), rot=(0, R90, 0), seg=8, bevel=0)
    k.block(a.part('Electric_cabinet', 'Armor'), (.25, .7, 1.1), loc=(-VX - .15, .4, 1.1), chamfer=.02)
    a.part('Hazard_marks', 'Hazard').box((.02, .25, .2), loc=(-VX - .28, .4, 1.4), bevel=0)
    a.part('Conduit', 'Steel').tube([(-VX - .12, .4, 1.65), (-VX - .12, .4, 3.1), (-VX - .12, 2.6, 3.1)], .03, seg=4)
    cage = a.part('Gas_cage', 'Steel')
    cage.box((.7, 1.0, .05), loc=(-VX - .45, 2.6, 1.6), bevel=0)
    for dx, dy in ((-.3, -.45), (.3, -.45), (-.3, .45), (.3, .45)):
        cage.box((.04, .04, 1.5), loc=(-VX - .45 + dx, 2.6 + dy, .85), bevel=0)
    gb = a.part('Gas_bottles', 'Hazard')
    for j, dy in enumerate((-.25, .05, .32)):
        k.lathe(gb, [(.1, 0), (.1, .95 + j * .06), (.05, 1.05 + j * .06), (0, 1.06 + j * .06)],
                loc=(-VX - .45, 2.6 + dy, .12), seg=8)
    # The rear: the oil tank on its stand, the pallet stack with varied crates, spare tyres leaning on the wall.
    k.lathe(a.part('Oil_tank', 'Fuel'), [(.38, 0), (.42, .05), (.42, 1.55), (.38, 1.6), (0, 1.6)],
            loc=(-.8 - 1.0, VY1 + .45, .85), rot=(0, R90, 0), seg=10, worn=(1, 2))
    st = a.part('Tank_stand', 'Steel')
    for x in (-1.6, -.4):
        st.box((.08, .7, .5), loc=(x, VY1 + .45, .35), bevel=0)
    K.clutter(a, 'Crates', 'Crate', .4, 2.6, VY1 + .12, VY1 + .48, .12, 5, seed=91, size=(.25, .6), height=(.2, .6))
    a.part('Pallets', 'Wood').box((2.2, .4, .1), loc=(1.5, VY1 + .3, .06), bevel=0)
    ty = a.part('Tyres', 'Rubber')
    for i, x in enumerate((2.8, 2.95)):
        k.ring(ty, [(.24, -.11), (.4, -.11), (.42, 0), (.4, .11), (.24, .11)], loc=(x, -2.0 + i * .5, .5),
               rot=(0, R90 - .25, 0), seg=8)
    # Inside: the parts shelving with bins of every size, the engine on its stand.
    sh = a.part('Shelving', 'Steel')
    for z in (.5, 1.1, 1.7, 2.3):
        sh.box((.5, 2.4, .04), loc=(-2.75, -1.6, z), bevel=0)
    for y in (-2.75, -.45):
        sh.box((.5, .05, 2.3), loc=(-2.75, y, 1.27), bevel=0)
    for z in (.52, 1.12, 1.72):
        K.clutter(a, 'Bins', 'Crate', -2.98, -2.52, -2.7, -.5, z, 4, seed=int(z * 10), size=(.2, .45), height=(.15, .4))
    k.block(a.part('Engine', 'Undercarriage'), (.6, .8, .55), loc=(-.9, -2.2, .7), chamfer=.04)
    K.clutter(a, 'Bench_parts', 'Steel', 2.35, 2.85, .65, 2.55, 1.04, 6, seed=93, size=(.08, .25), height=(.04, .16))
    K.clutter(a, 'Wall_boxes', 'Team', -3.08, -2.98, 2.7, 3.3, 1.2, 1, seed=94, size=(.1, .1), height=(.3, .3))
    K.clutter(a, 'Floor_kit', 'Crate', -1.6, -.3, 2.2, 3.3, .12, 5, seed=95, size=(.15, .45), height=(.1, .4))
    tags = a.part('Bay_marks', 'PlasterWhite')
    for i, x in enumerate((-1.2, -.4, .4, 1.2)):
        tags.box((.3 + i * .04, .12, .01), loc=(x, VY0 + .3, .125), bevel=0)
    bolts = a.part('Kit_bolts', 'Steel')
    for y in (VY0, -1.2, 1.2, VY1):
        for s_ in (-1, 1):
            for dx in (-.08, .08):
                bolts.box((.04, .04, .05), loc=(s_ * (VX - .1) + dx, y - .14, .15), bevel=0)
    es = a.part('Engine_stand', 'CraneYellow')
    es.box((.08, .9, .08), loc=(-.9, -2.2, .38), bevel=0)
    es.box((.7, .08, .08), loc=(-.9, -2.6, .16), bevel=0)
    es.box((.7, .08, .08), loc=(-.9, -1.8, .16), bevel=0)


# ============================================================================= aircraft hangar (helicopter shelter)
HX = 3.5           # arch half span
HZ = 4.2           # arch crown
HY0, HY1 = -.7, 3.95


def _arch(r_scale=1.0, n=10):
    """The arch line (x, z) from the left foot to the right foot: vertical legs, then a pointed-round crown."""
    pts = []
    for i in range(n + 1):
        u = math.pi * i / n
        x = math.cos(u) * HX * r_scale
        z = .1 + 1.4 + math.sin(u) * (HZ - 1.5) * r_scale
        pts.append((x, z))
    return [(HX * r_scale, .1)] + pts + [(-HX * r_scale, .1)]


def _heli_kit(a):
    """The helicopter shelter's fittings: the maintenance stand in the mouth, tool chests, the tow tug on the pad's
    edge, the light mast with its floods, cones, sandbag corners, the rear vent panel."""
    # The rolling maintenance stand: a deck on four legs with a stair and rails.
    ms = a.part('Work_stand', 'CraneYellow')
    x0, y0 = -1.9, .4
    ms.box((1.4, 1.0, .06), loc=(x0, y0, 1.8), bevel=0)
    for dx in (-.65, .65):
        for dy in (-.45, .45):
            ms.box((.06, .06, 1.75), loc=(x0 + dx, y0 + dy, .95), bevel=0)
    K.railing(a.part('Work_stand_rails', 'Steel'), [(x0 - .7, y0 - .5, 1.83), (x0 + .7, y0 - .5, 1.83),
                                                    (x0 + .7, y0 + .5, 1.83)], h=.8, post=.7, r=.018)
    stp = a.part('Work_stand_steps', 'Steel')
    for i in range(6):
        stp.box((.55, .2, .03), loc=(x0 + .1, y0 + .65 + i * .22, 1.62 - i * .27), bevel=0)
    K.clutter(a, 'Tool_chests', 'Team', 1.2, 3.1, 2.0, 3.6, .1, 5, seed=97, size=(.3, .7), height=(.4, 1.0))
    K.clutter(a, 'Spares', 'Crate', -3.2, -1.2, 1.8, 3.0, .1, 4, seed=98, size=(.25, .6), height=(.15, .45))
    # The tow tug on the pad's right edge: body, cab rail, four wheels, the tow bar.
    tg = a.part('Tug', 'CraneYellow')
    k.block(tg, (.9, 1.5, .5), loc=(-2.9, -2.8, .45), chamfer=.04)
    k.block(tg, (.7, .5, .35), loc=(-2.9, -2.25, .87), chamfer=.03)
    a.part('Glass', 'Glass').box((.6, .02, .2), loc=(-2.9, -2.51, .9), bevel=0)
    tw = a.part('Tyres', 'Rubber')
    for dy in (-.5, .5):
        for s_ in (-1, 1):
            tw.cyl(.2, .14, loc=(-2.9 + s_ * .48, -2.8 + dy, .3), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Tow_bar', 'Steel').box((.08, .7, .06), loc=(-2.9, -3.75, .3), rot=(.1, 0, 0), bevel=0)
    # The light mast at the rear left corner with two floods, the cones on the pad's edge, sandbag corners.
    K.floodlight(a, (3.8, 3.85, .1), facing=(-.4, -1, -.6), pole=5.2)
    cones = a.part('Cones', 'Hazard')
    for x, y in ((3.6, -4.0), (-.9, -4.0), (.9, -4.0)):
        k.lathe(cones, [(.14, 0), (.14, .03), (.04, .5), (0, .5)], loc=(x, y, .1), seg=6)
    for s_ in (-1, 1):
        W.bags(a, [(s_ * 3.85, HY1 - .3, .1), (s_ * 3.85, HY1 - 1.4, .1)], layers=2, bag=(.5, .28, .15), seed=99 + s_)
    K.clutter(a, 'Small_parts', 'Steel', -.9, .9, 2.6, 3.6, .1, 6, seed=96, size=(.1, .3), height=(.05, .25))
    tie = a.part('Tie_downs', 'Steel')
    for i in range(8):
        u = i * TAU / 8 + .2
        tie.box((.08 + (i % 3) * .02, .08, .04), loc=(math.cos(u) * 1.9, -2.45 + math.sin(u) * 1.9 * .75, .12),
                bevel=0)
    el = a.part('Edge_lights', 'SignalGreen')
    for x in (-2.4, -1.2, 0, 1.2, 2.4):
        el.box((.08, .08, .08), loc=(x, -4.0, .14), bevel=0)
    a.part('Front_band', 'Team').tube([(x * 1.012, HY0 - .09, z + .03) for x, z in _arch(1.0)[2:-2]], .05, seg=4,
                                      caps=False)
    K.floodlight(a, (-3.85, -.4, .1), facing=(.5, -1, -.6), pole=4.4)
    K.grille(a, (1.6, HY1 + .06, 3.0), .9, .5, facing=(0, 1, 0), slats=4)
    K.grille(a, (-1.6, HY1 + .06, 3.0), .9, .5, facing=(0, 1, 0), slats=4)


def aircraft_hangar(a, detail=False):
    """The aircraft hangar: a tension-fabric helicopter shelter and its helipad apron (module docstring)."""
    base = a.part('Base', 'Concrete')
    _pad(base, (7.3, HY1 - HY0 + .3, .1), loc=(0, (HY0 + HY1) / 2, .05), chamfer=.02)
    k.extrude(base, [(-3.5, -4.0), (3.5, -4.0), (3.9, -3.3), (3.9, HY0 - .15), (-3.9, HY0 - .15), (-3.9, -3.3)], .1,
              loc=(0, 0, .05), axis='Z', chamfer=.02)
    # The fabric shell: the arch profile (outer and inner lines) swept along Y; steel ribs; the closed rear end.
    outer = _arch(1.0)
    inner = [(x * .985, .1 + (z - .1) * .985) for x, z in outer]
    prof = outer + inner[::-1]
    k.extrude(a.part('Roof', 'Canvas'), [(x, z) for x, z in prof], HY1 - HY0, loc=(0, (HY0 + HY1) / 2, 0), axis='Y')
    ribs = a.part('Arch_ribs', 'Steel')
    for y in (HY0 - .04, .5, 1.6, 2.75, HY1 + .02):
        ribs.tube([(x * 1.01, y, z + (.03 if z > .2 else 0)) for x, z in outer], .06, seg=4)
    k.extrude(a.part('Walls', 'Canvas'), outer, .05, loc=(0, HY1, 0), axis='Y')
    a.part('Interior', 'Undercarriage').box((6.6, .02, 3.6), loc=(0, HY1 - .08, 1.9), bevel=0)
    pur = a.part('Purlins', 'Steel')
    for i in (2, 4, 6, 8):
        x, z = outer[i]
        pur.tube([(x * 1.012, HY0 - .04, z + .03), (x * 1.012, HY1 + .02, z + .03)], .025, seg=4, caps=False)
    _heli_kit(a)
    # The front doors drawn open: two fabric-covered frames folded back along the sides.
    dr = a.part('Doors', 'Canvas')
    dfr = a.part('Door_frames', 'Steel')
    for s_ in (-1, 1):
        dr.box((.06, 1.3, 3.2), loc=(s_ * (HX + .12), HY0 + .7, .1 + 1.6), bevel=0)
        dfr.box((.08, 1.38, .08), loc=(s_ * (HX + .14), HY0 + .7, 3.32), bevel=0)
        dfr.box((.08, .08, 3.2), loc=(s_ * (HX + .14), HY0 + .02, 1.7), bevel=0)
        a.part('Door_guides', 'Steel').box((.12, .5, .08), loc=(s_ * (HX + .05), HY0 + .2, 3.38), bevel=0)
    # Anchors (ground plates and straps) along the sides; a Team band along the fabric.
    an = a.part('Anchors', 'Steel')
    for s_ in (-1, 1):
        for y in (HY0 + .1, .85, 2.4, HY1):
            an.box((.3, .3, .06), loc=(s_ * (HX + .12), y, .13), bevel=0)
    tb = a.part('Team_band', 'Team')
    for s_ in (-1, 1):
        tb.box((.03, HY1 - HY0 - .2, .35), loc=(s_ * (HX + .015), (HY0 + HY1) / 2, 2.2), bevel=0)
    # Inside: the rotor blade rack and a tool cart; the light over the door.
    rk = a.part('Blade_rack', 'Steel')
    for x in (-2.6, -1.7):
        rk.box((.06, .06, 1.3), loc=(x, 3.4, .75), bevel=0)
    for z in (.7, 1.0, 1.3):
        a.part('Rotor_blades', 'Armor').box((1.4, .26, .04), loc=(-2.15, 3.3, z), rot=(.0, .0, .05), bevel=0)
    k.block(a.part('Tool_cart', 'Team'), (.6, .45, .8), loc=(2.4, 2.9, .5), chamfer=.02)
    # Tie-down straps from the ribs to the anchors; the side personnel door; the ground power unit by the pad.
    st = a.part('Kit_straps', 'Hazard')
    for s_ in (-1, 1):
        for y in (.85, 2.4):
            st.limb((s_ * (HX + .12), y - .7, .16), (s_ * (HX - .25), y, 2.6), .04, .02, bevel=0)
            st.limb((s_ * (HX + .12), y + .7, .16), (s_ * (HX - .25), y, 2.6), .04, .02, bevel=0)
    a.part('Side_door', 'Armor').box((.06, .8, 1.9), loc=(HX + .03, 3.2, 1.05), bevel=.01)
    a.part('Door_frames', 'Steel').box((.08, .95, .08), loc=(HX + .05, 3.2, 2.05), bevel=0)
    gpu = a.part('Ground_power', 'Team')
    k.block(gpu, (.6, .9, .6), loc=(2.75, -1.55, .5), chamfer=.03)
    K.grille(a, (2.44, -1.55, .55), .6, .35, facing=(-1, 0, 0), slats=4)
    wh = a.part('Tyres', 'Rubber')
    for dy in (-.35, .35):
        for s_ in (-1, 1):
            wh.cyl(.13, .08, loc=(2.75 + s_ * .33, -1.55 + dy, .23), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Kit_cables', 'Rubber').tube([(2.45, -1.9, .4), (2.0, -2.2, .12), (1.2, -2.45, .12)], .025, seg=4)
    K.lamp(a, (0, HY0 - .05, 3.9), facing=(0, -1, -.6), r=.08, guard=True)
    # The pad: a white circle and H, the touchdown box, edge lights.
    py = -2.45
    k.ring(a.part('Pad_marks', 'PlasterWhite'), [(1.3, .1), (1.5, .1), (1.5, .115), (1.3, .115)], loc=(0, py, 0),
           seg=24)
    pm = a.part('Pad_marks', 'PlasterWhite')
    for s_ in (-1, 1):
        pm.box((.16, .9, .012), loc=(s_ * .32, py, .108), bevel=0)
    pm.box((.5, .16, .012), loc=(0, py, .108), bevel=0)
    pe = a.part('Pad_edge', 'Hazard')
    for s_ in (-1, 1):
        pe.box((.1, 3.0, .01), loc=(s_ * 3.7, py + .1, .106), bevel=0)
    lights = a.part('Edge_lights', 'SignalGreen')
    for x in (-3.7, 3.7):
        for y in (-3.9, -2.45, -1.0):
            lights.cyl(.05, .08, loc=(x, y, .14), seg=6, bevel=0)
    # The windsock mast at the front left corner, the antenna at the rear right; the fuel point at the front right.
    a.part('Mast', 'Steel').cyl(.045, 3.2, loc=(3.75, -3.85, 1.7), seg=6, bevel=0)
    k.lathe(a.part('Windsock', 'Hazard'), [(.16, 0), (.11, .5), (.07, 1.0), (0, 1.0)], loc=(3.75, -3.85, 3.15),
            rot=(R90 - .3, 0, -2.2), seg=8, caps=(False, False))
    K.whip_antenna(a.part('Antennas', 'Steel'), (-3.75, 3.9, .1), h=3.4, r=.025)
    a.part('Antennas', 'Steel').box((.25, .25, .25), loc=(-3.75, 3.9, .22), bevel=.01)
    ft = a.part('Fuel_tank', 'Fuel')
    k.lathe(ft, [(.32, 0), (.36, .05), (.36, 1.25), (.32, 1.3), (0, 1.3)], loc=(-3.45, -3.0, .5), rot=(R90, 0, 0),
            seg=10, worn=(1, 2))
    cr = a.part('Tank_cradle', 'Steel')
    for y in (-3.3, -2.0):
        cr.box((.6, .1, .4), loc=(-3.45, y, .3), bevel=0)
    k.lathe(a.part('Hose_reel', 'BarrelRed'), [(.25, -.06), (.25, .06)], loc=(-3.1, -1.6, .4), rot=(0, R90, 0), seg=10)
    a.part('Kit_cables', 'Rubber').tube([(-3.1, -1.75, .3), (-2.6, -2.0, .12), (-1.8, -2.1, .12)], .025, seg=4)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.12, 0), (.12, .7), (.06, .8), (0, .82)], loc=(3.2, -.95, .1),
            seg=8)
    chk = a.part('Chocks', 'CraneYellow')
    for x in (-.7, .7):
        chk.box((.3, .2, .12), loc=(x, -1.2, .16), bevel=.01)
    for x, y in ((3.0, -3.6), (-3.0, -3.6), (0, -1.0)):
        K.dust(a, (x, y, 0), radius=1.7, k=.25)
    k.clean(a)


BUILDERS = {
    'mg_bunker': (mg_bunker, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
    'mg_bunker_a': (mg_bunker_a, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
    'mg_bunker_b': (mg_bunker_b, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
    'guard_tower': (guard_tower, dict(ao_distance=.8, grime_height=.8, ao_strength=.7)),
    'guard_tower_a': (guard_tower_a, dict(ao_distance=.8, grime_height=.8, ao_strength=.7)),
    'laser_ad_station': (laser_ad_station, dict(ao_distance=.7, grime_height=.6, ao_strength=.7)),
    'drone_hangar': (drone_hangar, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'drone_hangar_a': (drone_hangar_a, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'drone_hangar_b': (drone_hangar_b, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'vehicle_hangar_base': (vehicle_hangar_base, dict(ao_distance=1.0, grime_height=.6, ao_strength=.7)),
    'aircraft_hangar': (aircraft_hangar, dict(ao_distance=1.0, grime_height=.6, ao_strength=.7)),
}
