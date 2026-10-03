"""Prompt 35 wave 2 (lane A): the drone hangar and its two branches rebuilt from scratch on one shelter (owner
decision 4), each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)".

The sheet: a low vaulted hangar with a roller door and a drone launch rail (unit_refs: an earth-covered concrete
arch shelter launching FPV drones). An Accord field shelter, 8 x 8 m: a cast apron with joints, the concrete vault
under an earth-and-turf berm (its rear end sloped), the concrete headwall with angled wing walls and sandbag ends, the
roller door with its slats, guides and drum housing, berm vents, a ladder and a railed platform on the berm, the
charging bench under a canvas lean-to with its generator, drone crates, a floodlight and a whip antenna.

- drone_hangar (fpv_hangar): a trestle launch rail on the berm (`Launch_rail`, kept) with an FPV quadcopter ready.
- drone_hangar_a (lancet_hangar): a Lancet pneumatic catapult: a long truss rail raised 15 degrees on two trestles,
  the air bottle and compressor, a Lancet (cruciform X-wings) on the shuttle.
- drone_hangar_b (fpv_hangar_swarm): a swarm launcher on the berm: a rack of eight launch cells with hinged lids
  thrown open, FPV drones in them, the control cabinet and its mast.

Runtime nodes (kept): `Muzzle_main`, `Muzzle_door_l` (root pivots where the drones leave), mesh `Launch_rail`
(drone_hangar). Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and the wave's lean helpers; no other
model's builder. Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
APRON = .1
VY0, VY1 = -1.6, 2.4       # the vault's front and rear
TOP = APRON + 3.65         # berm crown


def _bz(x):
    """The berm's surface height at x (its arch section, constant along the vault)."""
    return APRON + 3.65 * math.sqrt(max(0.0, 1 - (x / 3.2) ** 2))


def _bslope(x):
    """The rotation about Y that lays a flat piece on the berm at x."""
    q = max(.05, 1 - (x / 3.2) ** 2)
    return math.atan(3.65 * x / (3.2 ** 2 * math.sqrt(q)))


def _arch(a_, b_, n=10, z0=0.0, a0=0.0, a1=math.pi):
    return [(a_ * math.cos(a0 + (a1 - a0) * i / n), z0 + b_ * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _berm_mesh(part, prof, y0, y1, k1=(1.0, 1.0), cap=False):
    """The berm's skin between y0 and y1 (no underside: it lies on the ground): the arch profile at y0, scaled by k1
    (x, z) at y1, quads between; cap=True closes the y1 end (a fan)."""
    n = len(prof)
    v0 = [(x, y0, APRON + z) for x, z in prof]
    v1 = [(x * k1[0], y1, APRON + z * k1[1]) for x, z in prof]
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    verts = v0 + v1
    if cap:
        verts.append((0, y1, APRON))
        faces += [(n + i + 1, n + i, 2 * n) for i in range(n - 1)]
    part.mesh(verts, faces)


def shelter(a, platform=True):
    """The front apron, the berm over the vault, headwall, door and the yard (common to the three)."""
    # The apron only where it is seen: the yard in front of the headwall (the berm covers the rest).
    k.extrude(a.part('Base', 'Concrete'), [(-4.0, -4.0), (3.2, -4.0), (4.0, -3.2), (4.0, VY0), (-4.0, VY0)], APRON,
              loc=(0, 0, APRON / 2), axis='Z', corner=.05, taper=(.98, .98), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-3, 4):
        j.box((.03, 2.35, .01), loc=(i * 1.1, -2.85, APRON + .003), bevel=0)
    for y in (-3.4, -2.6):
        j.box((7.8, .03, .01), loc=(0, y, APRON + .003), bevel=0)
    st = a.part('Stains', 'Charred')
    st.box((1.2, .8, .008), loc=(.4, -3.3, APRON + .006), rot=(0, 0, .3), bevel=0)
    for dx in (-.9, .9):
        st.box((.3, 1.8, .006), loc=(dx, -3.1, APRON + .006), bevel=0)
    # The earth berm over the vault (its skin only), the rear end drawn in, sod bands, sandbag courses at the feet.
    prof = [(3.85, -.02)] + _arch(3.2, 3.65, 12, a0=.2, a1=math.pi - .2) + [(-3.85, -.02)]
    berm = a.part('Berm', 'Dirt')
    _berm_mesh(berm, prof, VY0 + .05, VY1)
    _berm_mesh(berm, [(x, z) for x, z in prof], VY1, VY1 + 1.0, k1=(.8, .4), cap=True)
    for i, x in enumerate((-2.75, -2.3, -1.85, -1.35, -.85, -.4, .1, .55, 1.0, 1.45, 1.9, 2.35, 2.8)):
        mat = ('Grass', 'FoliageDark', 'FoliageLight')[i % 3]
        a.part(f'Berm_sod_{mat.lower()}', mat).box((.42, 3.6 - abs(x) * .3 - (i % 2) * .6, .03), loc=(x, .35 + (i % 2) * .2,
                                                  _bz(x) - .005), rot=(0, _bslope(x), 0), bevel=0)
    for sx in (-1, 1):
        W.bags(a, [(sx * 3.92, -1.2, APRON), (sx * 3.92, 3.0, APRON)], layers=2, bag=(.55, .3, .17), seed=24 + sx)
    # Stones and clods on the berm, sandbag collars round the vents.
    rk = a.part('Stones', 'Rock')
    for i in range(26):
        u = (i * 0.618) % 1.0
        x = -3.0 + 6.0 * u
        y = VY0 + .3 + ((i * 0.382) % 1.0) * (VY1 - VY0 + .4)
        sz = .12 + (i % 4) * .05
        rk.box((sz, sz * 1.3, sz * .7), loc=(x, y, _bz(x) + sz * .2), rot=(i * .7, _bslope(x), i * 1.3), bevel=0)
    for (x, y) in ((1.6, 1.8), (-1.6, 1.8)):
        ring = [(x + math.cos(t) * .5, y + math.sin(t) * .5, _bz(x) - .05) for t in (j * TAU / 6 for j in range(7))]
        W.bags(a, ring, layers=1, bag=(.4, .22, .14), seed=int(x * 10) + 40)
    # The concrete headwall with lift joints and the Team band, the angled wing walls with sloped tops.
    hw = a.part('Walls', 'Plaster')
    k.extrude(hw, [(-3.9, 0), (3.9, 0), (3.9, .9), (2.9, 2.9), (1.9, 3.8), (-1.9, 3.8), (-2.9, 2.9), (-3.9, .9)], .45,
              loc=(0, VY0 - .2, APRON), axis='Y', chamfer=.04, caps=(True, False))
    for z in (1.0, 2.0, 3.0):
        w = 7.6 if z < 1 else (6.4 if z < 2.5 else 4.2)
        a.part('Lift_joints', 'Undercarriage').box((w, .012, .02), loc=(0, VY0 - .43, APRON + z), bevel=0)
    for s in (-1, 1):
        k.extrude(hw, [(0, 0), (1.1, 0), (1.1, .5), (0, 1.6)], .35, loc=(s * 3.72, VY0 - .95, APRON),
                  rot=(0, 0, math.pi + s * .35), axis='X', chamfer=.03)
    team = a.part('Team_band', 'Team')
    team.box((3.6, .03, .3), loc=(0, VY0 - .435, APRON + 3.35), bevel=0)
    W.bags(a, [(-1.8, VY0 - .2, APRON + 3.8), (1.8, VY0 - .2, APRON + 3.8)], layers=1, bag=(.5, .3, .16), seed=41)
    ab = a.part('Kit_bolts', 'Steel')
    for x in (-3.4, -2.6, 2.6, 3.4):
        for z in (.4, .8):
            ab.cyl(.03, .04, loc=(x, VY0 - .44, APRON + z), rot=(R90, 0, 0), seg=4, bevel=0)
    # The roller door: slatted curtain, guides, the drum housing, hazard edge, a lamp; a wicket hatch.
    dw, dh = 3.6, 2.7
    a.part('Doors', 'Armor').box((dw, .06, dh), loc=(0, VY0 - .45, APRON + dh / 2), bevel=0)
    sl = a.part('Door_slats', 'Undercarriage')
    for i in range(1, 9):
        sl.box((dw - .1, .015, .03), loc=(0, VY0 - .485, APRON + i * dh / 9), bevel=0)
    gr = a.part('Door_guides', 'Steel')
    for s in (-1, 1):
        gr.box((.12, .12, dh + .3), loc=(s * (dw / 2 + .06), VY0 - .5, APRON + (dh + .3) / 2), bevel=0)
    k.block(a.part('Door_drum', 'Armor'), (dw + .4, .45, .45), loc=(0, VY0 - .62, APRON + dh + .1), chamfer=.05)
    a.part('Hazard_marks', 'Hazard').box((dw, .02, .12), loc=(0, VY0 - .49, APRON + .12), bevel=0)
    a.part('Lamps', 'Lamp').box((.24, .06, .12), loc=(0, VY0 - .87, APRON + dh + .2), rot=(-.3, 0, 0), bevel=0)
    a.part('Wicket', 'Undercarriage').box((.7, .02, 1.8), loc=(-1.2, VY0 - .49, APRON + .95), bevel=0)
    # Berm fittings: two mushroom vents, the ladder up the left flank, a whip antenna and its radio box.
    for (x, y) in ((1.6, 1.8), (-1.6, 1.8)):
        k.lathe(a.part('Vents', 'Steel'), [(.12, -.3), (.12, .5), (.28, .52), (.28, .6), (0, .66)],
                loc=(x, y, _bz(x)), seg=8, worn=(3,))
    K.ladder(a.part('Ladders', 'Steel'), (3.75, .6, APRON + .1), (2.0, .6, _bz(2.0) + .35), width=.45, step=.32,
             r=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.8, 2.3, _bz(.8)), h=1.4, r=.025)
    k.block(a.part('Radio_box', 'Armor'), (.3, .25, .3), loc=(-.8, 2.05, _bz(.8) + .12), chamfer=.02)
    if platform:
        k.block(a.part('Roof_deck', 'Steel'), (2.6, 2.4, .1), loc=(-.4, .3, TOP - .05), chamfer=0)
        for x in (-1.6, .8):
            for y in (-.8, 1.4):
                a.part('Deck_legs', 'Steel').box((.08, .08, TOP - _bz(x) + .1), loc=(x, y, (TOP + _bz(x)) / 2 - .1),
                                                 bevel=0)
        K.railing(a.part('Railings', 'Steel'), [(.9, -.9, TOP + .05), (.9, 1.5, TOP + .05), (-1.7, 1.5, TOP + .05)],
                  h=.9, post=.5, r=.018)
    # The yard in front: the charging bench under a canvas lean-to (right), the generator and tool chest, drone
    # crates and a fuel drum under a camouflage net (left), the floodlight, a jerrycan, a wire fence at the rear.
    k.block(a.part('Canopy', 'Canvas'), (1.7, 1.5, .04), loc=(-3.0, -3.25, APRON + 2.1), rot=(-.2, 0, 0), chamfer=0)
    wood = a.part('Canopy_poles', 'Wood')
    for (x, y) in ((-3.8, -3.95), (-2.2, -3.95)):
        wood.cyl(.04, 1.95, loc=(x, y, APRON + .97), seg=5, bevel=0)
    k.block(a.part('Workbench', 'Wood'), (1.5, .6, .08), loc=(-3.0, -3.2, APRON + .85), chamfer=0)
    for x in (-3.65, -2.35):
        a.part('Frame', 'Steel').box((.05, .5, .85), loc=(x, -3.2, APRON + .42), bevel=0)
    for i in range(3):
        a.part('Batteries', 'Fuel').box((.14, .2, .12), loc=(-3.5 + i * .45, -3.2, APRON + .95), bevel=0)
    k.block(a.part('Generator', 'Armor'), (1.1, .7, .7), loc=(-2.85, -2.35, APRON + .35), chamfer=.04)
    K.grille(a, (-2.85, -2.71, APRON + .35), .8, .4, facing=(0, -1, 0), slats=4)
    K.exhaust(a, (-3.25, -2.2, APRON + .7), r=.05, length=.5)
    a.part('Kit_cables', 'Undercarriage').tube([(-2.4, -2.5, APRON + .2), (-2.6, -3.0, APRON + .02),
                                                (-2.9, -3.2, APRON + .8)], .025, seg=4)
    k.block(a.part('Tool_chests', 'BarrelRed'), (.45, .6, .8), loc=(-3.75, -2.3, APRON + .4), chamfer=.03)
    for jj in range(3):
        a.part('Kit_handles', 'Steel').box((.02, .5, .02), loc=(-3.52, -2.3, APRON + .2 + jj * .22), bevel=0)
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    for (x, y, z, r) in ((2.9, -3.3, 0, .1), (2.9, -3.3, .35, -.1), (2.85, -2.45, 0, .2)):
        K.crate(crates, straps, (.8, .6, .35), (x, y, APRON + z), rot=(0, 0, r), bands=1)
    K.fuel_drum(a.part('Fuel_drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (3.65, -2.5, APRON), r=.27, h=.85)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (2.2, -2.3, APRON), rot=(0, 0, .5))
    poles = [(2.2, -3.95, 2.1), (3.95, -3.6, 1.9), (3.95, -2.1, 1.8), (2.2, -2.1, 2.0)]
    for (x, y, h) in poles:
        a.part('Net_poles', 'Wood').cyl(.04, h, loc=(x, y, APRON + h / 2), seg=5, bevel=0)
    pts = [(x, y, APRON + h) for (x, y, h) in poles]
    mid = (3.05, -2.95, APRON + 1.55)
    net = a.part('Camo_net', 'Canvas')
    tris = []
    for i in range(4):
        tris += [pts[i], pts[(i + 1) % 4], mid]
    net.mesh(tris, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(4)])
    net.mesh(tris, [(3 * i, 3 * i + 2, 3 * i + 1) for i in range(4)])
    garn = a.part('Camo_garnish', 'Foliage')
    for (x, y) in ((2.6, -3.5), (3.5, -3.1), (2.7, -2.4), (3.5, -2.4)):
        garn.box((.5, .4, .03), loc=(x, y, APRON + 1.75), rot=(.15, .1, x), bevel=0)
    K.floodlight(a, (-1.9, -3.95, APRON), facing=(.2, 1, -.4), pole=2.6)
    K.wire_fence(a, [(-2.9, 3.95, APRON), (2.4, 3.95, APRON)], h=1.3, post=.9, strands=3, concertina=False)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 3.5, -2.8 + math.sin(u) * 1.0, APRON), radius=1.3, k=.3)
    K.dust(a, (0, -3.0, APRON), radius=2.0, k=.35)


def fpv(a, loc, yaw=0.0, parent=None, tag=''):
    """An FPV quadcopter: the body with its camera and battery, four arms, four motors with prop discs."""
    x, y, z = loc
    c, s = math.cos(yaw), math.sin(yaw)
    a.part(f'Drones{tag}', 'Armor', parent).box((.12, .22, .05), loc=(x, y, z), rot=(0, 0, yaw), bevel=0)
    a.part(f'Drone_batteries{tag}', 'Fuel', parent).box((.08, .14, .05), loc=(x, y, z + .05), rot=(0, 0, yaw),
                                                         bevel=0)
    for u in (.78, 2.36, 3.93, 5.5):
        dx, dy = math.cos(u + yaw) * .17, math.sin(u + yaw) * .17
        a.part(f'Drone_arms{tag}', 'Undercarriage', parent).box((.03, .24, .02), loc=(x + dx / 2, y + dy / 2, z),
                                                                 rot=(0, 0, u + yaw - R90), bevel=0)
        a.part(f'Drone_props{tag}', 'Steel', parent).cyl(.08, .01, loc=(x + dx, y + dy, z + .03), seg=8, bevel=0)


def _muzzles(a, p):
    a.pivot('Muzzle_main', p)
    a.pivot('Muzzle_door_l', p)


def drone_hangar(a):
    """drone_hangar: the trestle launch rail with an FPV ready (see the module docstring)."""
    shelter(a)
    rail = a.part('Launch_rail', 'Steel')
    p0, p1 = (-.9, 1.4, TOP + .35), (-.9, .2, 4.72)
    for s in (-1, 1):
        rail.tube([(p0[0] + s * .12, p0[1], p0[2]), (p1[0] + s * .12, p1[1], p1[2])], .03, seg=4)
    for f in (.2, .5, .8):
        q = [p0[i] + (p1[i] - p0[i]) * f for i in range(3)]
        rail.box((.3, .04, .04), loc=tuple(q), bevel=0)
    tr = a.part('Trestle', 'Steel')
    for (y, z) in ((1.3, p0[2]), (.3, p1[2] - .05)):
        for s in (-1, 1):
            tr.tube([(-.9 + s * .25, y, TOP + .05), (-.9 + s * .12, y, z)], .025, seg=4)
    fpv(a, (-.9, .45, 4.78))
    W.stack(a, (.3, 1.2, TOP + .05), n=2, size=(.5, .32, .2), yaw=.2, name='Drone_boxes', seed=21)
    _muzzles(a, (-.9, .33, 4.78))
    k.clean(a)


def drone_hangar_a(a):
    """drone_hangar_a: the Lancet pneumatic catapult (see the module docstring)."""
    shelter(a)
    el = math.radians(15)
    y0, y1 = 1.6, -1.5
    z0 = TOP + .45
    z1 = z0 + (y0 - y1) * math.tan(el)
    rail = a.part('Catapult_rail', 'Team')
    L = math.hypot(y0 - y1, z1 - z0)
    k.block(rail, (.32, L, .16), loc=(-.2, (y0 + y1) / 2, (z0 + z1) / 2 - .08), rot=(-el, 0, 0), chamfer=.02)
    tr = a.part('Catapult_truss', 'Steel')
    for f in (.15, .4, .65, .9):
        q = (y0 + (y1 - y0) * f, z0 + (z1 - z0) * f - .17)
        for s in (-1, 1):
            tr.tube([(-.2 + s * .3, q[0], TOP + .05), (-.2 + s * .14, q[0], q[1])], .025, seg=4)
        tr.tube([(-.5, q[0], TOP + .3), (.1, q[0], TOP + .3)], .018, seg=3)
    # The air bottle and compressor beside the rail, the hose to the shuttle.
    k.lathe(a.part('Air_bottle', 'Fuel'), [(.2, -.8), (.24, -.7), (.24, .7), (.2, .8)], loc=(-1.1, .9, TOP + .3),
            rot=(R90, 0, 0), seg=10, worn=(1, 2))
    k.block(a.part('Compressor', 'Armor'), (.6, .5, .45), loc=(-1.1, -.2, TOP + .27), chamfer=.03)
    a.part('Hoses', 'Rubber').tube([(-1.1, .1, TOP + .3), (-.6, .4, TOP + .5), (-.25, .9, z0 + .1)], .03, seg=4)
    # The Lancet on the shuttle at the rail's front end: body, nose, two X-wing sets, the pusher prop.
    d = (0, -math.cos(el), math.sin(el))
    c = (-.2, -1.0, z0 + (y0 + 1.0) * math.tan(el) + .2)
    rot = (R90 - el, 0, 0)
    k.lathe(a.part('Lancet', 'Armor'), [(0, -.65), (.07, -.6), (.08, .45), (.05, .65), (0, .7)], loc=c, rot=rot,
            seg=8)
    wings = a.part('Lancet_wings', 'Team')
    for f, span in ((.3, .55), (-.4, .5)):
        p = (c[0], c[1] + d[1] * f, c[2] + d[2] * f)
        for u in (.78, 2.36):
            wings.box((span * 2, .22, .015), loc=p, rot=(-el, 0, u), bevel=0)
    a.part('Lancet_prop', 'Steel').box((.4, .02, .04), loc=(c[0], c[1] - d[1] * .7, c[2] - d[2] * .7), bevel=0)
    W.stack(a, (.8, 1.0, TOP + .05), n=2, size=(1.1, .35, .3), yaw=0, name='Drone_boxes', seed=22)
    _muzzles(a, (-.2, -1.5, 5.12))
    k.clean(a)


def drone_hangar_b(a):
    """drone_hangar_b: the swarm launch cells with their lids open (see the module docstring)."""
    shelter(a, platform=False)
    k.block(a.part('Roof_deck', 'Steel'), (2.8, 2.4, .12), loc=(-.4, .3, TOP - .05), chamfer=0)
    for x in (-1.7, .9):
        for y in (-.8, 1.4):
            a.part('Deck_legs', 'Steel').box((.08, .08, TOP - _bz(x) + .1), loc=(x, y, (TOP + _bz(x)) / 2 - .1),
                                             bevel=0)
    cells = a.part('Launch_cells', 'Team')
    lids = a.part('Cell_lids', 'Armor')
    z = TOP + .07
    for i in range(4):
        for jj in range(2):
            x, y = -1.35 + i * .62, -.2 + jj * .9
            W.slab(cells, (.56, .8, .35), (x, y, z), caps=(False, True), chamfer=.02)
            a.part('Cell_bores', 'Undercarriage').box((.46, .7, .01), loc=(x, y, z + .355), bevel=0)
            lids.box((.56, .03, .78), loc=(x, y + .42, z + .35 + .36), rot=(-.25, 0, 0), bevel=0)
            if (i + jj) % 2 == 0:
                fpv(a, (x, y, z + .4))
    k.block(a.part('Control_cabinet', 'Armor'), (.5, .4, .9), loc=(1.3, 1.1, _bz(1.3) + .35), chamfer=.03)
    a.part('Mast', 'Steel').cyl(.04, 1.4, loc=(1.3, 1.3, _bz(1.3) + .6), seg=6, bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (1.3, 1.25, _bz(1.3) + 1.15), w=.5, h=.4, normal=(0, -1, 0))
    K.railing(a.part('Railings', 'Steel'), [(-1.85, -.95, TOP + .05), (-1.85, 1.5, TOP + .05), (1.0, 1.5, TOP + .05)],
              h=.9, post=.5, r=.018)
    _muzzles(a, (-.55, .25, 5.25))
    k.clean(a)


BUILDERS = {
    'drone_hangar': (drone_hangar, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'drone_hangar_a': (drone_hangar_a, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'drone_hangar_b': (drone_hangar_b, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
}
