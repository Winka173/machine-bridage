"""Prompt 35 wave 11 (lane C): Hyperion rebuilt from scratch (spec: Tools/blender/specs/hyperion.json).

Aurel's orbital mirror station (the variant of silver_bug without its crash turrets and uplink; the def's modelSize
67.2 x 43.7 x 20 m; the origin at the landing pods' feet), drawn on the patterns of the Znamya 2 space mirror and
the ISS's integrated truss: a hexagonal ring of square lattice trusses (four longerons, battens, diagonals) carrying
rows of white mirror facets on gimbals tilted towards the core; six tubular spokes with radiator panels; the core, a
stack of turned modules (habitat drum, equipment rings, the docking adapter, the comms mast and dish) with the
sun-beam emitter slung under it on its gimbal yoke (`Turret`: the lens barrel with its glowing aperture, cooling
fins); two long trusses fore and aft carrying four solar array wings with their cell grids; the main engine on the
core's aft side (`Thruster_main`: bell, glowing throat, propellant tanks); an RCS pod with nozzle quads and
propellant spheres on each of the ring's four outer corners (`Thruster_fl` / `_fr` / `_rl` / `_rr`); two point-
defence laser turrets (`Pd_laser_l` / `_r` with their turning heads `Mount_mg` / `.001`); two coilguns on the front
corners (`Mount_gun` / `.001`: coil rings, capacitor housings) and two 40 mm turrets aft (`Mount_gun.002` / `.003`);
the pod bay under the aft spoke with its two landing pods (`Pod_bay`, `Muzzle_missile`); the APS emitter on the core's
crown (`Mount_APS`, new: the def has APS); navigation lights, beacons, team bands.

Runtime nodes kept where they were (every old pivot, checked against the old file); `Mount_APS` added. Metres, +Z up,
-Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
RING_R = 20.0
RING_Z = 10.4
TH, TW = 1.1, 1.0        # the ring truss's height and width
HEX = [(RING_R * math.cos(i * TAU / 6), RING_R * math.sin(i * TAU / 6)) for i in range(6)]


def _truss(a, p0, p1, z, h=TH, w=TW, bays=7, part='Hull', mat='Team', diag='Truss_diagonals'):
    """A square lattice truss from p0 to p1 (x, y) centred at height z: four longerons, a batten frame at each bay,
    one diagonal per bay on each face."""
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    lon = a.part(part, mat)
    dg = a.part(diag, 'Steel')
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]

    def pt(f, c):
        return (x0 + ux * L * f + nx * c[0], y0 + uy * L * f + ny * c[0], z + c[1])
    for c in corners:
        lon.limb(pt(0, c), pt(1, c), .16, .16, bevel=0)
    for b in range(bays + 1):
        f = b / bays
        for c0, c1 in zip(corners, corners[1:] + corners[:1]):
            dg.limb(pt(f, c0), pt(f, c1), .08, .08, bevel=0)
    for b in range(bays):
        f0, f1 = b / bays, (b + 1) / bays
        for j, (c0, c1) in enumerate(zip(corners, corners[1:] + corners[:1])):
            if (b + j) % 2:
                dg.limb(pt(f0, c0), pt(f1, c1), .07, .07, bevel=0)
            else:
                dg.limb(pt(f0, c1), pt(f1, c0), .07, .07, bevel=0)


def _ring(a):
    """The hexagonal ring of trusses, the mirror facets on their gimbals, corner nodes, navigation lights."""
    nodes = a.part('Ring_nodes', 'Armor')
    for i in range(6):
        p0, p1 = HEX[i], HEX[(i + 1) % 6]
        _truss(a, p0, p1, RING_Z)
        k.extrude(nodes, [(-.9, -.9), (.9, -.9), (.9, .9), (-.9, .9)], TH + .4, loc=(p0[0], p0[1], RING_Z),
                  rot=(0, 0, i * TAU / 6), axis='Z', chamfer=.12, corner=.15, ends=(True, True))
        # Mirror facets along the side, tilted towards the core.
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        inward = math.atan2(-mid[1], -mid[0])
        fac = a.part('Mirrors', 'Medical')
        frm = a.part('Mirror_frames', 'Steel')
        for j in range(5):
            f = (j + .9) / 6.8
            cx, cy = p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f
            cz = RING_Z + TH / 2 + 1.1
            tilt = math.radians(38)
            rot = (0, tilt, inward)
            k.block(fac, (2.6, 2.6, .08), loc=(cx, cy, cz), rot=rot, chamfer=0)
            frm.box((2.7, .1, .1), loc=(cx, cy, cz - .06), rot=rot, bevel=0)
            frm.limb((cx, cy, RING_Z + TH / 2), (cx, cy, cz - .1), .14, .14, bevel=0)
    lights = a.part('Nav_lights', 'LavaGlow')
    green = a.part('Nav_lights_green', 'SignalGreen')
    for i, (x, y) in enumerate(HEX):
        (green if x > 0 else lights).sphere(.25, loc=(x, y, RING_Z + TH / 2 + .5), seg=8, rings=5)


def _spokes(a):
    """Six spokes from the core to the ring's corners, each two tubes with braces and a radiator panel."""
    sp = a.part('Spokes', 'Steel')
    rad = a.part('Radiators', 'Plaster')
    for i, (x, y) in enumerate(HEX):
        u = i * TAU / 6
        c, s = math.cos(u), math.sin(u)
        for dz in (-.35, .35):
            sp.tube([(c * 2.6, s * 2.6, 9.4 + dz), (x * .96, y * .96, RING_Z + dz)], .2, seg=8)
        for f in (.25, .5, .75):
            px, py = c * (2.6 + (RING_R - 2.6) * f), s * (2.6 + (RING_R - 2.6) * f)
            pz = 9.4 + (RING_Z - 9.4) * f
            sp.limb((px, py, pz - .35), (px, py, pz + .35), .1, .1, bevel=0)
        if i % 3 != 1:      # not under the pods' or the engine's spoke: a radiator panel on the others
            px, py = c * 9.0, s * 9.0
            k.block(rad, (6.0, 2.2, .06), loc=(px, py, 9.85), rot=(R90 * .0, 0, u), chamfer=0)
            for j in range(5):
                a.part('Radiator_ribs', 'Steel').box((.06, 2.2, .1), loc=(px + c * (-2.4 + j * 1.2) - s * 0,
                                                                         py + s * (-2.4 + j * 1.2), 9.9),
                                                     rot=(0, 0, u), bevel=0)


def _core(a):
    """The stack of turned modules, the docking adapter, the comms mast and dish, team bands, the APS crown."""
    core = a.part('Body', 'Team')
    k.lathe(core, [(1.6, 3.0), (2.4, 3.6), (2.6, 4.2), (2.6, 7.0), (2.9, 7.3), (2.9, 8.1), (2.6, 8.4), (2.6, 11.6),
                   (2.2, 12.2), (1.6, 12.6), (1.6, 13.6), (1.2, 14.0), (0, 14.05)], seg=16, worn=(2, 5, 8))
    eq = a.part('Core_rings', 'Armor')
    for z in (5.0, 10.0):
        k.ring(eq, [(2.58, -.25), (2.78, -.25), (2.78, .25), (2.58, .25)], loc=(0, 0, z), seg=16, worn=(1, 2))
    for i in range(4):
        u = i * R90 + .4
        k.lathe(a.part('Docking_ports', 'Steel'), [(.8, 0), (.8, .9), (.95, .95), (.95, 1.1), (.6, 1.12)],
                loc=(math.cos(u) * 2.55, math.sin(u) * 2.55, 6.0), rot=K.rot_to((math.cos(u), math.sin(u), 0)),
                seg=12, worn=(3,))
    win = a.part('Glass', 'Glass')
    for i in range(10):
        u = i * TAU / 10
        win.box((.5, .06, .35), loc=(math.cos(u) * 2.62, math.sin(u) * 2.62, 11.0), rot=(0, 0, u + R90), bevel=0)
    for z in (7.7, 4.3):
        a.part('Team_band', 'Team').cyl(2.92 if z > 7 else 2.62, .3, loc=(0, 0, z), seg=16, bevel=0)
    # The comms mast and dish to the top of the station.
    mast = a.part('Comms_mast', 'Steel')
    mast.cyl(.18, 4.8, loc=(0, 0, 16.4), seg=8, bevel=0)
    for z in (15.0, 17.0):
        for i in range(3):
            u = i * TAU / 3
            mast.limb((0, 0, z), (math.cos(u) * .9, math.sin(u) * .9, z - 1.2), .08, .08, bevel=0)
    K.dish(a.part('Comms_dish', 'Plaster'), a.part('Comms_feed', 'Steel'), (1.2, 0, 17.6), r=1.5,
           normal=(1, -.4, .5), seg=14)
    K.beacon(a, (0, 0, 18.8), r=.35)
    a.part('Beacon_tip', 'Lamp').sphere(.2, loc=(0, 0, 19.6), seg=8, rings=5)
    # The APS crown on the core's top.
    aps = a.pivot('Mount_APS', (0, 0, 14.1))
    k.lathe(a.part('Aps_emitter', 'Armor', aps), [(1.0, 0), (1.0, .3), (.7, .6), (0, .65)], seg=12, worn=(1,))
    a.part('Aps_glow', 'Energy', aps).sphere(.3, loc=(.0, -.75, .35), seg=8, rings=5)


def _emitter(a):
    """The sun-beam emitter under the core on its gimbal yoke (Turret)."""
    t = a.pivot('Turret', (0, 0, 2.3))
    yoke = a.part('Laser_mount', 'Armor', t)
    k.lathe(yoke, [(1.6, .55), (1.6, .75), (1.2, .85)], seg=14)
    for s in (-1, 1):
        k.extrude(yoke, [(-.6, -1.0), (.6, -1.0), (.4, .6), (-.4, .6)], .3, loc=(s * 1.45, 0, 0), axis='X',
                  chamfer=.04)
    d = (0, -3.9, -.9)
    L = math.sqrt(3.9 ** 2 + .9 ** 2)
    rot = K.rot_to((0, -3.9 / L, -.9 / L))
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.0, -1.6), (.9, -1.5), (1.15, -1.1), (1.15, 1.6), (1.35, 2.0),
                                                 (1.35, 2.6), (1.0, 2.7)], rot=rot, seg=16, worn=(3, 5))
    fins = a.part('Laser_fins', 'Steel', t)
    m = K.frame((0, 0, 0), rot)
    for i in range(6):
        k.ring(fins, [(1.15, 0), (1.5, 0), (1.5, .08), (1.15, .08)], loc=K._at(m, (0, 0, -1.0 + i * .4)), rot=rot,
               seg=14)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.95, .06, loc=K._at(m, (0, 0, 2.66)), rot=rot, seg=16, bevel=0)
    a.pivot('Muzzle_main', d, t)


def _engine(a):
    """The main engine on the core's aft side (Thruster_main)."""
    th = a.pivot('Thruster_main', (0, 4.6, 9.4))
    k.block(a.part('Engine_mount', 'Armor', th), (2.6, 2.6, 2.4), loc=(0, -1.3, 0), chamfer=.15, ends=(True, True))
    k.lathe(a.part('Engine_bell', 'Steel', th), [(.6, 0), (.75, .5), (1.2, 1.6), (1.55, 2.4), (1.5, 2.45),
                                                  (1.1, 1.6), (.5, .4)], loc=(0, 0, 0), rot=K.BACKWARD, seg=16,
            worn=(3,), caps=(False, False))
    a.part('Engine_glow', 'Energy', th).cyl(.65, .05, loc=(0, .45, 0), rot=K.BACKWARD, seg=12, bevel=0)
    for s in (-1, 1):
        a.part('Engine_tanks', 'Plaster', th).sphere(.9, loc=(s * 1.7, -1.4, .4), seg=12, rings=8)
    K.soot(a, (0, 7.0, 9.4), radius=2.0, k=.3)


def _rcs(a, name, loc):
    th = a.pivot(name, loc)
    tag = name.split('_')[-1]
    body = a.part('Rcs_' + tag, 'Armor', th)
    k.block(body, (1.6, 1.6, 1.3), loc=(0, 0, 0), chamfer=.12, ends=(True, True))
    noz = a.part('Rcs_nozzles_' + tag, 'Steel', th)
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)):
        p = (d[0] * .85, d[1] * .85, d[2] * .7)
        k.lathe(noz, [(.12, 0), (.2, .25), (.17, .26)], loc=p, rot=K.rot_to(d), seg=8, caps=(True, False))
    a.part('Rcs_tanks_' + tag, 'Plaster', th).sphere(.45, loc=(0, 0, -.95), seg=10, rings=6)


def _weapons(a):
    """Point-defence lasers, coilguns, 40 mm turrets."""
    for side, x in (('l', 14.6), ('r', -14.6)):
        pd = a.pivot(f'Pd_laser_{side}', (x, -8.4, 10.8))
        k.lathe(a.part(f'Pd_base_{side}', 'Armor', pd), [(1.0, -.3), (1.0, .1), (.7, .4), (.6, .5)], seg=12,
                worn=(1,))
        mname = 'Mount_mg' if side == 'l' else 'Mount_mg__001'
        m = a.pivot(mname, (0, 0, .5), pd)
        head = a.part(f'Pd_head_{side}', 'Team', m)
        k.extrude(head, [(-.5, -.45), (.5, -.45), (.4, .4), (-.4, .4)], .7, loc=(0, 0, .2), axis='Y', chamfer=.05,
                  corner=.04)
        k.lathe(a.part(f'Pd_emitter_{side}', 'Steel', m), [(.16, 0), (.16, 1.1), (.24, 1.2), (.24, 1.4), (0, 1.42)],
                loc=(0, -.25, .45), rot=K.FORWARD, seg=10)
        a.part(f'Pd_glow_{side}', 'Energy', m).cyl(.18, .03, loc=(0, -1.67, .45), rot=K.FORWARD, seg=8, bevel=0)
        a.pivot(mname.replace('Mount', 'Muzzle'), (0, -1.45, .45), mname)
    for name, x in (('Mount_gun', 9.62), ('Mount_gun__001', -9.62)):
        m = a.pivot(name, (x, -16.67, 10.4))
        tag = '_' + name.split('__')[-1] if '__' in name else ''
        house = a.part('Coil_house' + tag, 'Team', m)
        k.extrude(house, [(-.8, 0), (.8, 0), (.6, .7), (-.6, .7)], 2.4, loc=(0, .4, .0), axis='Y', chamfer=.06,
                  corner=.05)
        rail = a.part('Coil_rails' + tag, 'Steel', m)
        for dx in (-.18, .18):
            rail.box((.12, 5.2, .2), loc=(dx, -2.9, .49), bevel=0)
        coils = a.part('Coil_rings' + tag, 'Energy', m)
        for j in range(6):
            k.ring(coils, [(.32, -.08), (.42, -.08), (.42, .08), (.32, .08)], loc=(0, -1.4 - j * .8, .49),
                   rot=K.FORWARD, seg=10)
        a.part('Capacitors' + tag, 'Armor', m).box((1.4, 1.0, .5), loc=(0, 1.2, .95), bevel=.05)
        a.pivot(name.replace('Mount', 'Muzzle'), (0, -5.9, .49), name)
    for name, x in (('Mount_gun__002', 14.0), ('Mount_gun__003', -14.0)):
        m = a.pivot(name, (x, 12.4, 10.5))
        tag = '_' + name.split('__')[-1]
        k.lathe(a.part('Gun_ring' + tag, 'Steel', m), [(.9, -.2), (.9, .05), (.75, .1)], seg=12)
        house = a.part('Gun_house' + tag, 'Team', m)
        k.extrude(house, [(-.7, 0), (.7, 0), (.55, .65), (-.5, .7)], 1.8, loc=(0, .3, 0), axis='Y', chamfer=.05,
                  corner=.04)
        C.gun_tube(a, 'Gun_barrel' + tag, m, (0, -.6, .31), 2.75, .1, seg=10, sleeve=2, brake='pepper',
                   brake_name='Gun_brake' + tag)
        a.pivot(name.replace('Mount', 'Muzzle'), (0, -3.5, .31), name)


def _solar(a):
    """Two trusses fore and aft, four solar array wings with their cell grids."""
    for sy in (-1, 1):
        y0, y1 = sy * 20.0, sy * 32.8
        _truss(a, (0, sy * 2.8), (0, y1), RING_Z + .2, h=.8, w=.8, bays=9, part='Solar_truss', mat='Steel',
               diag='Solar_truss_diagonals')
        for f in (.45, .85):
            y = y0 + (y1 - y0) * f
            for s in (-1, 1):
                cells = a.part('Solar_cells', 'Glass')
                frame = a.part('Solar_frames', 'Alloy')
                x0, x1 = s * .6, s * 8.0
                k.block(cells, (abs(x1 - x0), 3.2, .05), loc=((x0 + x1) / 2, y, RING_Z + .2), chamfer=0)
                frame.box((abs(x1 - x0), .12, .12), loc=((x0 + x1) / 2, y - 1.65, RING_Z + .2), bevel=0)
                frame.box((abs(x1 - x0), .12, .12), loc=((x0 + x1) / 2, y + 1.65, RING_Z + .2), bevel=0)
                for j in range(7):
                    xx = x0 + (x1 - x0) * j / 6
                    frame.box((.08, 3.3, .08), loc=(xx, y, RING_Z + .24), bevel=0)
        k.block(a.part('Solar_caps', 'Armor'), (1.4, 1.4, 1.4), loc=(0, y1 + sy * .5, RING_Z + .2), chamfer=.1,
                ends=(True, True))


def _pods(a):
    """The pod bay under the aft spoke and its two landing pods."""
    pb = a.pivot('Pod_bay', (0, 9.0, 4.4))
    dock = a.part('Pod_dock', 'Armor', pb)
    k.block(dock, (5.0, 2.4, .6), loc=(0, 0, .3), chamfer=.08, ends=(True, True))
    dock.limb((0, 0, .6), (0, -4.0, 5.0), .4, .4, bevel=0)
    for j, x in enumerate((-1.5, 1.5)):
        pod = a.part(f'Pod_{2 * j}', 'Team', pb)
        k.lathe(pod, [(0, -4.4), (.7, -4.3), (1.0, -3.6), (1.0, -1.2), (.7, -.6), (.35, -.2), (.35, 0)],
                loc=(x, 0, 0), seg=12, worn=(2, 3))
        a.part(f'Pod_glass_{2 * j}', 'Glass', pb).box((.5, .06, .3), loc=(x, -1.0, -2.0), bevel=0)
        for i in range(3):
            u = i * TAU / 3 + .5
            a.part('Pod_legs', 'Steel', pb).limb((x + math.cos(u) * .8, math.sin(u) * .8, -3.5),
                                                 (x + math.cos(u) * 1.25, math.sin(u) * 1.25, -4.4), .08, .08,
                                                 bevel=0)
    a.pivot('Muzzle_missile', (0, -1.4, -2.0), pb)


def hyperion(a, detail=False):
    """Hyperion, the orbital mirror station: see the module docstring."""
    K.suffixed(a)
    _ring(a)
    _spokes(a)
    _core(a)
    _emitter(a)
    _engine(a)
    for name, loc in (('Thruster_fl', (10.02, -17.36, 11.0)), ('Thruster_fr', (-10.02, -17.36, 11.0)),
                      ('Thruster_rl', (10.02, 17.36, 11.0)), ('Thruster_rr', (-10.02, 17.36, 11.0))):
        _rcs(a, name, loc)
    _weapons(a)
    _solar(a)
    _pods(a)
    k.clean(a)


BUILDERS = {
    'hyperion': (hyperion, dict(ao_distance=1.2, ao_strength=.5, grime_height=.0, ground=False)),
}
