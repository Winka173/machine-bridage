"""Play-test 14 boss redraw R3 (lane models): the bespoke weapons, sensors and hatches of the five ground bosses.

Owner (04/10, Docs/prompts/playtest14_vi.txt, last block): "đừng reuse gì hết, tất cả boss khi vẽ lại đều vẽ lại từ
đầu". The ground bosses drew every gun from one shared barrel kit (K.gun_barrel: collar, thermal sleeve, fume extractor,
the same baffle brake), the same turret race (K.turret_ring), smoke launchers, periscopes and hatches, so their guns
looked alike. Audit: Docs/models/pt14_reuse_audit.md; DECISIONS "Play-test 14 boss redraw R3 (lane models)".

Every function here draws for one boss only (no other model calls it), from geometry primitives, at that boss's
scale, read from a real weapon so each machine has its own gun style:
- Jotunn (mobile_fortress): a 2A44-read 203 mm L/55 (no brake, muzzle swell, two recoil cylinders over an open
  cradle) in a raked gun house with a rear loading platform; a B-4-read short hooped 203 mm on the roof; AK-230-read
  domed twin 30 mm cupolas (finned jackets, braced barrels, flash cones); a Strela-10-read four-container SAM; a
  2A46-read 125 mm smoothbore in the bow ball (clamped thermal sleeve, extractor, muzzle reference sensor); a
  Smerch-read open bundle of twelve 300 mm tubes per launcher; an orange-peel EMP reflector on a lattice mast.
- Fortress Bastion: a 2B8 / Tyulpan-read 240 mm breech-loading mortar in a low cast turret; D-10-read twin 100 mm
  (bore evacuator near the muzzle, no brake) in rounded cast sponsons; Bofors L/60-read 40 mm (recoil spring, cone
  flash hider, top clip guide) in faceted shield houses; an M284-read 155 mm with a slab double-baffle brake in the
  bow ball; a ZU-23-2 read with its box magazines and slotted flash hiders; a Kornet-EM read twin launcher.
- Bastion Mk.0: a riveted M1-240 mm-read banded howitzer tube on an open pedestal with handwheels and an arc; early
  long 100 mm twins with slotted cylindrical brakes and exposed recoil cylinders in riveted drums.
- Fenrir: a Gepard-read faceted flak house, twin 35 mm KDA-read guns outside its cheeks (slim brakes, muzzle-velocity
  coils), front tracking dish, rear search antenna; MLRS-read boxed launch pods (ribbed walls, frangible caps); a
  lattice-backed planar target radar on a telescopic mast.
- Inferno (the Behemoth design): M67-read shrouded flame projectors (finned tube, igniter box, nozzle cone, pilot jet,
  armoured braided hose), a Nona-read stubby 125 mm with a pepperpot brake in a welded wedge turret, a ZPU-2-read
  twin 14.5 mm with perforated jackets on the roof.

Runtime names are the ones each mount had (Turret / Main_cannon* / Muzzle_brake* / Mount_* / Muzzle_* / Part_* /
Radar). The barrels a free mount kicks are its pivot's `<word>_barrels` / `<word>_muzzles` parts
(ModelLibrary.IsMountBarrel); turret guns kick through Main_cannon* / Muzzle_brake*. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= small helpers (geometry only)
def sfx(index):
    return '' if index == 0 else f'_{index:03d}'


def tag_of(slot, index):
    return slot if index == 0 else f'{slot}_{index:03d}'


def per_barrel(a, muzzle, tag, xs):
    """Muzzle_b<k>_<tag> under the pivot `muzzle`, one per barrel at the x offsets `xs` (left to right)."""
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def fwd(part, profile, loc, seg=14, worn=()):
    """A turned part along -Y (the front): profile [(radius, distance forward)] from loc."""
    k.lathe(part, profile, loc=loc, rot=K.FORWARD, seg=seg, worn=worn)


def fwd_ring(part, loop, loc, seg=14):
    """An open turned ring along -Y (a tube wall, a band): loop [(radius, distance forward)] closed."""
    k.ring(part, loop, loc=loc, rot=K.FORWARD, seg=seg)


def along_x(part, profile, loc, seg=12):
    k.lathe(part, profile, loc=loc, rot=(0, R90, 0), seg=seg)


def frame(loc, elevation=0.0):
    """A frame at loc whose -Y axis points forward and up by `elevation` (radians)."""
    return Matrix.Translation(Vector(loc)) @ Matrix.Rotation(-elevation, 4, 'X')


def at(m, v):
    return tuple(m @ Vector(v))


def fwd_rot(m):
    """The Euler rotation that turns a lathe's +Z onto the frame's forward (-Y) axis."""
    return tuple((m.to_3x3() @ Matrix.Rotation(R90, 3, 'X')).to_euler('XYZ'))


def box_rot(m):
    return tuple(m.to_3x3().to_euler('XYZ'))


def lathe_on(part, m, profile, d0=0.0, x=0.0, z=0.0, seg=14, worn=()):
    """A turned part along frame m's forward axis, its profile [(radius, distance)] starting `d0` forward of the
    frame's origin, offset x / z in the frame."""
    k.lathe(part, profile, loc=at(m, (x, -d0, z)), rot=fwd_rot(m), seg=seg, worn=worn)


def ring_on(part, m, loop, d0=0.0, x=0.0, z=0.0, seg=14):
    k.ring(part, loop, loc=at(m, (x, -d0, z)), rot=fwd_rot(m), seg=seg)


def bolts_round(part, centre, radius, n, normal_axis='Z', r=.025, h=.03, phase=0.0, seg=6):
    """n bolt heads on a circle round `centre` in the plane normal to the given axis."""
    cx, cy, cz = centre
    for i in range(n):
        u = phase + i * TAU / n
        if normal_axis == 'Z':
            part.cyl(r, h, loc=(cx + math.cos(u) * radius, cy + math.sin(u) * radius, cz), seg=seg, bevel=0)
        elif normal_axis == 'Y':
            part.cyl(r, h, loc=(cx + math.cos(u) * radius, cy, cz + math.sin(u) * radius), rot=(R90, 0, 0), seg=seg,
                     bevel=0)
        else:
            part.cyl(r, h, loc=(cx, cy + math.cos(u) * radius, cz + math.sin(u) * radius), rot=(0, R90, 0), seg=seg,
                     bevel=0)


def handwheel(part, loc, r, rot=(0, R90, 0), spokes=4, t=.018):
    """A handwheel: the rim, the hub, the spokes (in the plane the rotation puts its local XY in)."""
    m = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rot[0], 4, 'X') @ Matrix.Rotation(rot[1], 4, 'Y') @ \
        Matrix.Rotation(rot[2], 4, 'Z')
    part.torus(r, t, loc=loc, rot=rot, seg=14, ring=4)
    part.cyl(t * 2.2, t * 3, loc=loc, rot=rot, seg=8, bevel=0)
    for i in range(spokes):
        u = i * TAU / spokes
        part.limb(at(m, (0, 0, 0)), at(m, (math.cos(u) * r, math.sin(u) * r, 0)), t * 1.2, t * 1.2, bevel=0)


def ellipse(cx, cy, rx, ry, n=16, phase=0.0):
    return [(cx + math.cos(phase + i * TAU / n) * rx, cy + math.sin(phase + i * TAU / n) * ry) for i in range(n)]


def slab_grid(part, fn, us, vs, t, flip=False):
    """A curved plate `t` thick: fn(u, v) -> (point, normal) over the grid us x vs, front and back skins and the rim."""
    front, back = [], []
    for v in vs:
        rf, rb = [], []
        for u in us:
            p, n = fn(u, v)
            p, n = Vector(p), Vector(n).normalized()
            rf.append(tuple(p + n * (t / 2)))
            rb.append(tuple(p - n * (t / 2)))
        front.append(rf)
        back.append(rb)
    nu, nv = len(us), len(vs)
    verts = [p for row in front for p in row] + [p for row in back for p in row]
    off = nu * nv
    faces = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a0, a1, a2, a3 = j * nu + i, j * nu + i + 1, (j + 1) * nu + i + 1, (j + 1) * nu + i
            f = (a0, a1, a2, a3)
            b = (off + a3, off + a2, off + a1, off + a0)
            faces += [f[::-1], b[::-1]] if flip else [f, b]
    rim = [j * nu for j in range(nv)][::-1] + list(range(nu)) + [j * nu + nu - 1 for j in range(nv)] + \
        [(nv - 1) * nu + i for i in range(nu)][::-1]
    loop = []
    for idx in rim:
        if not loop or loop[-1] != idx:
            loop.append(idx)
    if loop[0] == loop[-1]:
        loop.pop()
    for i in range(len(loop)):
        p, q = loop[i], loop[(i + 1) % len(loop)]
        f = (p, q, off + q, off + p)
        faces.append(f if flip else f[::-1])
    part.mesh(verts, faces)


# ============================================================================= Jotunn (mobile_fortress)
JT_TURRET = (0, 1.0, 6.25)


def jt_hatch(a, loc, parent=None, w=.78, d=.62):
    """Jotunn's square crew hatch: the raised coaming, the lid with two stiffener ribs, a locking handwheel, the hinge
    barrel along the rear edge."""
    x, y, z = loc
    lid = a.part('Hatches', 'Armor', parent)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    k.extrude(lid, [(-w / 2 - .06, -d / 2 - .06), (w / 2 + .06, -d / 2 - .06), (w / 2 + .06, d / 2 + .06),
                    (-w / 2 - .06, d / 2 + .06)], .07, loc=(x, y, z + .035), axis='Z', chamfer=.02)
    k.extrude(lid, [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], .05, loc=(x, y, z + .095),
              axis='Z', chamfer=.015, taper=(.96, .94))
    for dx in (-w * .22, w * .22):
        steel.box((.05, d * .86, .04), loc=(x + dx, y, z + .135), bevel=0)
    handwheel(steel, (x, y - d * .15, z + .19), .1, rot=(0, 0, 0), spokes=3, t=.014)
    steel.cyl(.016, .07, loc=(x, y - d * .15, z + .15), seg=6, bevel=0)
    along_x(steel, [(.04, -w * .42), (.04, w * .42)], (x, y + d / 2 + .07, z + .08), seg=8)


def dir_rot(d):
    """The Euler rotation that turns local +Z onto direction d."""
    return tuple(Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_euler('XYZ'))


def jt_smoke(a, x, y, z, s, parent):
    """902B-read smoke grenade bank: four 81 mm tubes fanned outward and up on a curved bracket, their caps."""
    br = a.part('Smoke_launchers', 'Armor', parent)
    tubes = a.part('Smoke_tubes', 'Steel', parent)
    br.box((.12, .95, .08), loc=(s * x, y, z - .02), bevel=.01)
    for i in range(4):
        f = (i - 1.5) / 1.5
        d = Vector((s * .75, -.35 + f * .35, .55))
        p = Vector((s * (x + .03), y + f * .34, z + .03))
        k.lathe(tubes, [(.05, 0), (.05, .3), (.058, .31), (.058, .34), (.04, .34), (.04, .31), (0, .31)],
                loc=tuple(p), rot=dir_rot(d), seg=8)
        br.box((.07, .07, .08), loc=(s * (x - .02), y + f * .34, z + .03), bevel=0)


def jt_main_turret(a):
    """The 2A44-read 203 mm in its raked gun house on Turret (see the module docstring): Main_cannon (the long tube,
    its breech ring and bore), Muzzle_brake (the muzzle swell: the 2A44 has no brake), Muzzle_main; the open cradle
    with two recoil cylinders over the barrel and the recuperator under it; the rear loading platform with its rammer
    and shells; the commander's cupola, hatch, rangefinder housing, charge lockers, smoke banks."""
    t = a.pivot('Turret', JT_TURRET)
    steel = a.part('Turret_steel', 'Steel', t)
    armor = a.part('Turret_armor', 'Armor', t)
    dark = a.part('Turret_dark', 'Undercarriage', t)
    # The race: a stepped bolted ring under the house.
    k.ring(steel, [(2.2, -.12), (2.42, -.12), (2.42, .02), (2.32, .06), (2.2, .06)], seg=32)
    bolts_round(a.part('Kit_bolts', 'Steel', t), (0, 0, -.04), 2.44, 24, normal_axis='Y', r=.0, h=0) \
        if False else None
    kb = a.part('Kit_bolts', 'Steel', t)
    for i in range(28):
        u = (i + .5) * TAU / 28
        kb.cyl(.035, .04, loc=(math.cos(u) * 2.36, math.sin(u) * 2.36, .08), seg=6, bevel=0)
    # The house: vertical walls up to the belt, then a strongly raked front and gently sloped sides to the roof.
    H = 1.25
    base = [(-1.6, -2.3), (1.6, -2.3), (2.25, -1.45), (2.25, 2.45), (1.95, 2.85), (-1.95, 2.85), (-2.25, 2.45),
            (-2.25, -1.45)]
    belt = [(-1.58, -2.42), (1.58, -2.42), (2.3, -1.5), (2.3, 2.5), (2.0, 2.92), (-2.0, 2.92), (-2.3, 2.5),
            (-2.3, -1.5)]
    roof = [(-1.15, -1.5), (1.15, -1.5), (2.02, -.92), (2.02, 2.32), (1.78, 2.68), (-1.78, 2.68), (-2.02, 2.32),
            (-2.02, -.92)]
    house = a.part('Turret_body', 'Team', t)
    k.sharp_loft(house, [[(x, y, 0.0) for x, y in base], [(x, y, .62) for x, y in belt],
                         [(x, y, H) for x, y in roof]], chamfer=.07)
    k.inset(house, lambda c, n, f: abs(n.z) < .5 and c.z > .7 and n.y > -.3, width=.12, depth=-.03)
    # Roof plate with seams and the team band.
    k.extrude(armor, [(x * .96, y * .96 + .05) for x, y in roof], .06, loc=(0, 0, H + .03), axis='Z', chamfer=.02)
    for y in (-.4, 1.2):
        steel.box((3.6, .04, .025), loc=(0, y, H + .07), bevel=0)
    a.part('Team_band', 'Team', t).box((3.2, .5, .02), loc=(0, 2.2, H + .07), bevel=0)
    # The embrasure: a cast wedge with the cradle slot, its cheek yokes and trunnion caps.
    k.extrude(armor, [(-2.2, .2), (-1.75, .2), (-1.6, 1.08), (-2.15, 1.18)], 1.25, loc=(0, 0, 0), axis='X',
              chamfer=.05, corner=.04)
    dark.box((.62, .1, .62), loc=(0, -2.62, .74), rot=(-.08, 0, 0), bevel=0)
    for s in (-1, 1):
        k.extrude(armor, [(-3.05, .45), (-2.1, .45), (-2.1, 1.12), (-2.75, 1.02)], .14, loc=(s * .42, 0, 0),
                  axis='X', chamfer=.025, corner=.03)
        along_x(steel, [(0, -.08), (.13, -.08), (.15, -.03), (.15, .03), (.13, .08), (0, .08)],
                (s * .5, -2.55, .78), seg=12)
    # The cradle round the barrel root, two recoil cylinders above, the recuperator below.
    k.block(armor, (.58, 1.35, .44), loc=(0, -3.18, .78), chamfer=.04)
    for s in (-1, 1):
        fwd(steel, [(0, -.05), (.1, -.05), (.1, 1.45), (.085, 1.5), (.05, 1.62), (0, 1.62)], (s * .17, -2.55, 1.07),
            seg=12)
        steel.box((.05, .05, .32), loc=(s * .17, -3.9, .92), bevel=0)
    fwd(steel, [(0, 0), (.12, 0), (.12, 1.3), (.09, 1.36), (0, 1.36)], (0, -2.55, .42), seg=12)
    # The tube: thick breech end, a jacket step, a long gentle taper, the swell at the muzzle (no brake).
    L = 5.0
    y0 = -2.75
    zg = .78
    fwd(a.part('Main_cannon', 'Steel', t), [(0, -.75), (.3, -.72), (.32, -.42), (.27, -.38), (.22, -.32), (.22, .2),
                                           (.205, .26), (.2, 1.55), (.215, 1.6), (.215, 1.7), (.19, 1.76),
                                           (.172, 3.2), (.16, L - .42), (.16, L - .4)], (0, y0, zg), seg=18,
        worn=(4, 9))
    fwd(a.part('Muzzle_brake', 'Steel', t), [(.15, L - .43), (.19, L - .36), (.2, L - .1), (.188, L - .02),
                                            (.12, L - .02), (.12, L - .05), (0, L - .05)], (0, y0, zg), seg=18)
    fwd(a.part('Main_cannon_bore', 'Undercarriage', t), [(.115, L - .045), (.115, L - .035), (0, L - .035)],
        (0, y0, zg), seg=14)
    a.pivot('Muzzle_main', (0, y0 - L - .02, zg), t)
    # Rangefinder housing on the right roof edge, sights forward.
    along_x(armor, [(0, -.62), (.16, -.6), (.2, -.5), (.2, .5), (.16, .6), (0, .62)], (-1.25, -.75, H + .24), seg=12)
    for sx in (-1.87, -.63):
        k.block(armor, (.2, .3, .3), loc=(sx, -.75, H + .2), chamfer=.03)
        a.part('Glass', 'Glass', t).box((.05, .02, .12), loc=(sx, -.92, H + .27), bevel=0)
    # Commander's cupola (vision blocks round it) and the loader's hatch.
    cup = a.part('Cupola', 'Armor', t)
    k.lathe(cup, [(.55, 0), (.55, .18), (.5, .24), (.46, .3), (.46, .38), (.36, .44), (0, .46)],
            loc=(1.25, 1.55, H + .06), seg=18, worn=(2,))
    for j in range(6):
        u = j * TAU / 6 + .3
        k.block(cup, (.18, .1, .13), loc=(1.25 + math.cos(u) * .5, 1.55 + math.sin(u) * .5, H + .2),
                rot=(0, 0, u + R90), chamfer=0)
        a.part('Glass', 'Glass', t).box((.14, .015, .06), loc=(1.25 + math.cos(u) * .56, 1.55 + math.sin(u) * .56,
                                                              H + .27), rot=(0, 0, u + R90), bevel=0)
    jt_hatch(a, (-1.1, 1.6, H + .06), parent=t)
    for x, y in ((.2, 2.3), (-1.55, .3)):
        k.lathe(steel, [(.14, 0), (.14, .2), (.24, .23), (.24, .29), (.1, .32), (0, .32)], loc=(x, y, H + .06),
                seg=10)
    K.whip_antenna(a.part('Antenna', 'Steel', t), (-1.85, 2.35, H + .06), h=1.3, lean=.12)
    # Charge lockers on the cheeks, the smoke banks.
    for s in (-1, 1):
        for j in range(3):
            k.block(a.part('Charge_lockers', 'Crate', t), (.22, .55, .5), loc=(s * 2.38, -.35 + j * .62, .4),
                    chamfer=.02)
            steel.box((.03, .12, .06), loc=(s * 2.5, -.35 + j * .62, .45), bevel=0)
        jt_smoke(a, 2.0, -1.05, .66, s, t)
    # The rear loading platform: a grating deck on brackets, its railing, the rammer tray and the shells.
    plat = a.part('Loading_platform', 'Steel', t)
    plat.box((3.6, .9, .06), loc=(0, 3.4, .28), bevel=0)
    for i in range(9):
        a.part('Platform_grating', 'Undercarriage', t).box((3.5, .03, .02), loc=(0, 3.0 + i * .1, .32), bevel=0)
    for x in (-1.5, 0, 1.5):
        plat.limb((x, 2.9, -.1), (x, 3.75, .25), .06, .08, bevel=0)
    rail = a.part('Railings', 'Steel', t)
    rail.tube([(-1.8, 2.95, .3), (-1.8, 3.85, .3), (-1.8, 3.85, 1.1), (1.8, 3.85, 1.1), (1.8, 3.85, .3),
               (1.8, 2.95, .3)], .03, seg=6)
    rail.tube([(-1.8, 3.85, .7), (1.8, 3.85, .7)], .025, seg=6)
    for x in (-.9, 0, .9):
        rail.tube([(x, 3.85, .3), (x, 3.85, 1.1)], .025, seg=6)
    k.block(armor, (.7, .9, .55), loc=(0, 3.1, .3), chamfer=.03)
    steel.box((.4, 1.2, .05), loc=(0, 2.75, .9), rot=(-.12, 0, 0), bevel=0)
    for i in range(4):
        k.lathe(a.part('Ready_shells', 'Gilded', t), [(0, -.55), (.09, -.5), (.13, -.36), (.13, .4), (.1, .45),
                                                    (0, .46)], loc=(-1.25 + i * .3 if i < 2 else .65 + (i - 2) * .3,
                                                                    3.45, .52), rot=(R90, 0, 0), seg=10)
    K.soot(a, (0, JT_TURRET[1] + y0 - L, JT_TURRET[2] + zg), radius=1.2, k=.45)
    K.tone(a, 'Turret', k=.95)


def jt_roof_gun(a):
    """The B-4-read short 203 mm on the turret roof (Mount_gun, howitzer_2): a low welded box house on its race, the
    half-drum mantlet, the hooped heavy tube with a lifting band and a plain crown (no brake: Gun_barrels /
    Gun_muzzles kick), Muzzle_gun."""
    m = a.pivot('Mount_gun', (0, 1.1, 1.25), 'Turret')
    steel = a.part('Roofgun_steel', 'Steel', m)
    k.ring(steel, [(.6, -.04), (.72, -.04), (.72, .05), (.6, .07)], seg=18)
    house = a.part('Roofgun_house', 'Armor', m)
    k.extrude(house, [(-.62, .05), (.78, .05), (.78, .62), (.05, .68), (-.4, .52)], 1.12, axis='X', chamfer=.035,
              corner=.04)
    k.inset(house, lambda c, n, f: abs(n.x) > .9, width=.07, depth=-.02)
    along_x(a.part('Roofgun_mantlet', 'Armor', m), [(0, -.38), (.3, -.36), (.32, -.3), (.32, .3), (.3, .36),
                                                    (0, .38)], (0, -.62, .36), seg=16)
    zg = .36
    y0 = -.72
    L = 2.35
    bar = a.part('Gun_barrels', 'Steel', m)
    fwd(bar, [(0, -.1), (.18, -.08), (.18, .7), (.155, .74), (.15, 1.2), (.138, L - .3), (.138, L - .02),
              (.08, L - .02), (.08, L - .06), (0, L - .06)], (0, y0, zg), seg=16, worn=(2, 5))
    for d in (.12, .34, .56):
        fwd_ring(bar, [(.17, d), (.205, d), (.205, d + .1), (.17, d + .1)], (0, y0, zg), seg=16)
    fwd_ring(a.part('Gun_muzzles', 'Steel', m), [(.13, L - .32), (.162, L - .3), (.162, L - .16), (.13, L - .14)],
             (0, y0, zg), seg=16)
    for s in (-1, 1):
        a.part('Gun_muzzles', 'Steel', m).box((.05, .08, .06), loc=(s * .17, y0 - L + .23, zg), bevel=0)
    a.pivot('Muzzle_gun', (0, y0 - L - .02, zg), m)
    k.block(a.part('Roofgun_sight', 'Armor', m), (.18, .26, .2), loc=(.4, -.32, .74), chamfer=.02)
    a.part('Glass', 'Glass', m).box((.12, .015, .07), loc=(.4, -.455, .72), bevel=0)
    for x in (-.35, .15):
        steel.box((.04, .5, .04), loc=(x, .45, .7), bevel=0)
    K.tone(a, 'Mount_gun', k=.9)


def jt_flak(a, index, s):
    """An AK-230-read twin 30 mm cupola on Mount_mg[.NNN] at a front deck corner: the bolted deck ring, the cast dome
    with its flat armoured face and two gun slots, the sight dome, the rear vent hood; the two barrels with finned
    cooling jackets, a mid-length brace and flash cones (Flak_barrels / Flak_muzzles kick), Muzzle_mg and the
    per-barrel muzzles."""
    J_DECK = 4.0
    x, y = s * 3.3, -6.15
    key = K.name('Mount_mg', index)
    tg = sfx(index)
    ring = a.part('Cupola_ring', 'Steel')
    k.ring(ring, [(.8, 0), (.92, 0), (.92, .2), (.86, .3), (.8, .3)], loc=(x, y, J_DECK), seg=20)
    for i in range(12):
        u = (i + .5) * TAU / 12
        a.part('Kit_bolts', 'Steel').cyl(.025, .03, loc=(x + math.cos(u) * .97, y + math.sin(u) * .97, J_DECK + .01),
                                         seg=6, bevel=0)
    m = a.pivot(key, (x, y, J_DECK + .32))
    dome = a.part('Flak_dome' + tg, 'Team', m)
    k.lathe(dome, [(.8, -.02), (.82, .08), (.8, .3), (.7, .5), (.5, .66), (.25, .74), (0, .76)], seg=22, worn=(2, 4))
    face = a.part('Flak_face' + tg, 'Armor', m)
    k.extrude(face, [(-.86, -.02), (-.62, -.02), (-.6, .55), (-.78, .45)], .9, axis='X', chamfer=.03, corner=.03)
    dark = a.part('Flak_dark' + tg, 'Undercarriage', m)
    for bx in (-.17, .17):
        dark.box((.12, .06, .2), loc=(bx, -.84, .3), bevel=0)
    k.lathe(a.part('Flak_sight' + tg, 'Armor', m), [(.17, 0), (.17, .08), (.13, .16), (0, .19)],
            loc=(.32 * s, .1, .68), seg=12)
    a.part('Glass', 'Glass', m).box((.12, .02, .05), loc=(.32 * s, -.06, .76), rot=(-.4, 0, 0), bevel=0)
    k.block(a.part('Flak_face' + tg, 'Armor', m), (.42, .3, .2), loc=(0, .62, .42), rot=(.35, 0, 0), chamfer=.03)
    for j in range(4):
        dark.box((.34, .02, .02), loc=(0, .76 + j * .0, .5 + j * .035), rot=(.35, 0, 0), bevel=0)
    # Barrels.
    zg, y0, L = .3, -.8, 1.95
    bar = a.part('Flak_barrels' + tg, 'Steel', m)
    for bx in (-.17, .17):
        prof = [(0, -.05), (.06, -.05), (.06, .02)]
        for j in range(7):
            d = .06 + j * .12
            prof += [(.06, d), (.072, d + .02), (.072, d + .06), (.06, d + .08)]
        prof += [(.06, .92), (.036, .96), (.033, L), (0, L)]
        fwd(bar, prof, (bx, y0, zg), seg=10)
        fwd(a.part('Flak_muzzles' + tg, 'Steel', m), [(.03, L - .02), (.04, L), (.06, L + .22), (.052, L + .24),
                                                       (.03, L + .24), (0, L + .23)], (bx, y0, zg), seg=10)
    bar.box((.46, .07, .07), loc=(0, y0 - 1.45, zg), bevel=.01)
    mk = a.pivot(K.name('Muzzle_mg', index), (0, y0 - L - .25, zg), key)
    per_barrel(a, mk, tag_of('mg', index), (-.17, .17))
    K.tone(a, key, k=.93)


def jt_sam(a):
    """A Strela-10-read SAM on the bridge roof (Mount_missile.001): the pedestal and turntable, the sensor box with
    its glass, two arms each holding a pair of rectangular launch containers (front caps dark), Muzzle_missile.001
    with a muzzle at each container's mouth."""
    J_DECK = 4.0
    key = K.name('Mount_missile', 1)
    sm = a.pivot(key, (-1.25, -5.5, J_DECK + 1.68))
    steel = a.part('Sam_steel', 'Steel', sm)
    k.lathe(steel, [(.5, 0), (.52, .04), (.52, .12), (.3, .16), (.22, .2), (.22, .5), (.3, .54), (.3, .6)], seg=16)
    box = a.part('Sam_sensor', 'Armor', sm)
    k.block(box, (.5, .6, .5), loc=(0, .02, .58), chamfer=.04, taper=(.9, .85))
    a.part('Glass', 'Glass', sm).box((.34, .02, .16), loc=(0, -.29, .84), rot=(-.25, 0, 0), bevel=0)
    a.part('Glass', 'Glass', sm).cyl(.07, .02, loc=(.14, -.27, .66), rot=K.FORWARD, seg=10, bevel=0)
    e = .32
    M = frame((0, .05, .9), e)
    along_x(steel, [(0, -.86), (.06, -.86), (.06, .86), (0, .86)], (0, .05, .9), seg=8)
    cont = a.part('Sam_containers', 'Team', sm)
    caps = a.part('Sam_caps', 'Undercarriage', sm)
    xs = (-.75, -.48, .48, .75)
    for x in xs:
        k.block(cont, (.24, 1.55, .24), loc=at(M, (x, -.05, 0)), rot=box_rot(M), chamfer=.02)
        caps.box((.2, .03, .2), loc=at(M, (x, -.84, 0)), rot=box_rot(M), bevel=0)
        for d in (-.55, .45):
            steel.box((.26, .04, .26), loc=at(M, (x, d, 0)), rot=box_rot(M), bevel=0)
    for s in (-1, 1):
        steel.limb((s * .26, .05, .9), (s * .62, .05, .9), .08, .1, bevel=0)
    mz = a.pivot(K.name('Muzzle_missile', 1), at(M, (0, -.87, 0)), key)
    per_barrel(a, mz, tag_of('missile', 1), xs)
    K.tone(a, key, k=.92)


def jt_bow_gun(a):
    """The 2A46-read 125 mm smoothbore in the bow ball (Mount_missile, aimed with the hull): the cast ball with its
    bolted collar, the tube with a clamped thermal sleeve, the fume extractor, the muzzle reference sensor and the
    crown (Bow_barrels / Bow_muzzles kick), Muzzle_missile."""
    gm = a.pivot('Mount_missile', (0, -8.45, 3.3))
    ball = a.part('Bow_mantlet', 'Armor', gm)
    fwd(ball, [(0, -.45), (.4, -.42), (.55, -.25), (.58, 0), (.52, .2), (.4, .33), (.22, .38), (0, .4)], (0, 0, 0),
        seg=18)
    fwd_ring(a.part('Bow_collar', 'Steel', gm), [(.2, .34), (.26, .34), (.26, .46), (.2, .46)], (0, 0, 0), seg=16)
    kb = a.part('Kit_bolts', 'Steel', gm)
    for i in range(10):
        u = i * TAU / 10
        kb.cyl(.022, .03, loc=(math.cos(u) * .45, -.32, math.sin(u) * .45), rot=(R90, 0, 0), seg=6, bevel=0)
    y0, L = -.44, 2.75
    bar = a.part('Bow_barrels', 'Steel', gm)
    fwd(bar, [(0, -.05), (.125, -.05), (.125, .14), (.105, .18), (.105, .95), (.15, 1.02), (.155, 1.1),
              (.155, 1.48), (.105, 1.56), (.105, 2.1), (.09, 2.15), (.085, L - .02), (.06, L - .02), (.06, L - .06),
              (0, L - .06)], (0, y0, 0), seg=14, worn=(5, 9))
    for d in (.42, .78, 1.8):
        fwd_ring(bar, [(.104, d), (.118, d), (.118, d + .05), (.104, d + .05)], (0, y0, 0), seg=14)
    mu = a.part('Bow_muzzles', 'Steel', gm)
    fwd_ring(mu, [(.084, L - .18), (.097, L - .17), (.097, L - .02), (.084, L - .01)], (0, y0, 0), seg=14)
    k.block(mu, (.08, .14, .07), loc=(0, y0 - L + .12, .085), chamfer=.01)
    a.pivot('Muzzle_missile', (0, y0 - L - .02, 0), gm)
    K.soot(a, (0, -8.45 + y0 - L, 3.3), radius=.5, k=.3)


def jt_radar(a):
    """The EMP emitter (Radar spins): a lattice mast on the core roof, the drive and yoke, an orange-peel reflector
    (an elliptical paraboloid section) tilted up, its back truss, the feed horn on a tripod with the emitter glow."""
    mast = a.part('Radar_mast', 'Steel')
    top = 7.38
    legs = [(math.cos(u) * .45, 4.25 + math.sin(u) * .45) for u in (R90, R90 + TAU / 3, R90 + 2 * TAU / 3)]
    for x, y in legs:
        mast.tube([(x * 1.6, 4.25 + (y - 4.25) * 1.6, 6.2), (x * .5, 4.25 + (y - 4.25) * .5, top)], .05, seg=6)
    for z0, z1, f0, f1 in ((6.25, 6.85, 1.55, 1.0), (6.85, 7.35, 1.0, .55)):
        for i in range(3):
            (x0, y0), (x1, y1) = legs[i], legs[(i + 1) % 3]
            mast.tube([(x0 * f0, 4.25 + (y0 - 4.25) * f0, z0), (x1 * f1, 4.25 + (y1 - 4.25) * f1, z1)], .025, seg=4)
    k.lathe(mast, [(.3, top - .02), (.3, top + .05), (.18, top + .08)], seg=14)
    r = a.pivot('Radar', (0, 4.25, 7.48))
    drive = a.part('Radar_drive', 'Armor', r)
    k.lathe(drive, [(.28, -.04), (.28, .12), (.2, .18), (.12, .22), (.12, .4)], seg=14)
    k.block(drive, (.26, .32, .22), loc=(.3, .05, -.02), chamfer=.02)
    steel = a.part('Radar_steel', 'Steel', r)
    for s in (-1, 1):
        steel.limb((0, 0, .3), (s * .9, .08, .55), .07, .07, bevel=0)
    W, Hh, f = 1.35, .55, 1.15
    tilt = -.3

    def surf(u, v):
        x, z = u * W, v * Hh
        dep = (x * x + z * z) / (4 * f)
        p = Vector((x, dep, z))
        n = Vector((-x / (2 * f), 1, -z / (2 * f)))
        rm = Matrix.Rotation(tilt, 3, 'X')
        p = rm @ p + Vector((0, .25, .78))
        return p, rm @ n
    us = [i / 8 - 1 for i in range(17)]
    vs = [j / 4 - 1 for j in range(9)]
    slab_grid(a.part('Radar_dish', 'Medical', r), surf, us, vs, .04)
    for u in (-.75, -.25, .25, .75):
        p0, _ = surf(u, -1)
        p1, _ = surf(u, 1)
        steel.tube([tuple(p0 + Vector((0, .06, 0))), (u * W * .6, .55, .78), tuple(p1 + Vector((0, .06, 0)))],
                   .02, seg=4)
    steel.tube([tuple(surf(-1, 0)[0] + Vector((0, .05, 0))), tuple(surf(1, 0)[0] + Vector((0, .05, 0)))], .025, seg=4)
    focus = Matrix.Rotation(tilt, 3, 'X') @ Vector((0, -f + .1, 0)) + Vector((0, .25, .78))
    for u, v in ((-.6, -.8), (.6, -.8), (0, .85)):
        p, _ = surf(u, v)
        steel.tube([tuple(p), tuple(focus + Vector((0, .1, 0)))], .02, seg=4)
    horn = a.part('Radar_feed', 'Steel', r)
    k.block(horn, (.22, .26, .2), loc=tuple(focus + Vector((0, .05, -.1))), rot=(tilt, 0, 0), chamfer=.015,
            taper=(1.4, 1.4))
    a.part('Radar_emitter', 'Energy', r).box((.2, .02, .16), loc=tuple(focus + Vector((0, .2, .02))), rot=(tilt, 0, 0),
                                             bevel=0)


def jt_rockets(a, index, s):
    """A Smerch-read launcher on Mount_rocket[.NNN]: the deck ring, the turntable, the elevating side girders and
    rams, and the open bundle of twelve 300 mm tubes (3 x 4) held by three band frames, dark bores at the mouths;
    Muzzle_rocket at the bundle's front."""
    J_DECK = 4.0
    key = K.name('Mount_rocket', index)
    x0, y0 = s * 2.15, 6.0
    tg = sfx(index)
    k.ring(a.part('Launcher_base', 'Steel'), [(.72, 0), (.86, 0), (.86, .2), (.8, .28), (.72, .28)],
           loc=(x0, y0, J_DECK), seg=20)
    m = a.pivot(key, (x0, y0, J_DECK + .3))
    tt = a.part('Launcher_turntable' + tg, 'Armor', m)
    k.lathe(tt, [(.78, -.04), (.78, .1), (.66, .18), (0, .2)], seg=20)
    steel = a.part('Launcher_steel' + tg, 'Steel', m)
    e = .42
    M = frame((0, .2, 1.3), e)
    for sx in (-1, 1):
        k.extrude(tt, [(-.6, .15), (.95, .15), (.85, .62), (.3, 1.25), (-.1, 1.25)], .12, loc=(sx * .72, 0, 0),
                  axis='X', chamfer=.02, corner=.03)
        along_x(steel, [(0, -.07), (.14, -.07), (.14, .07), (0, .07)], (sx * .8, .3, 1.15), seg=10)
        steel.tube([(sx * .5, .95, .25), at(M, (sx * .5, .7, -.5))], .075, seg=8)
        a.part('Launcher_rams' + tg, 'Undercarriage', m).tube([(sx * .5, .95, .25), (sx * .5, .85, .55)], .1, seg=8)
    tube = a.part('Pod_tubes' + tg, 'Team', m)
    bore = a.part('Tubes_bore' + tg, 'Undercarriage', m)
    Lt = 2.85
    pitch = .31
    cols = [(-1.5 + i) * pitch for i in range(4)]
    rows = [(-1 + j) * pitch for j in range(3)]
    for cx in cols:
        for rz in rows:
            ring_on(tube, M, [(.12, -Lt / 2), (.145, -Lt / 2), (.145, Lt / 2), (.12, Lt / 2)], 0, cx, rz, seg=12)
            lathe_on(bore, M, [(.122, Lt / 2 - .2), (0, Lt / 2 - .2)], 0, cx, rz, seg=10)
            ring_on(steel, M, [(.144, Lt / 2 - .1), (.16, Lt / 2 - .08), (.16, Lt / 2), (.144, Lt / 2)], 0, cx, rz,
                    seg=12)
    W, Hh = 4 * pitch + .08, 3 * pitch + .08
    for d in (-1.0, 0.0, 1.0):
        for zz in (-Hh / 2, Hh / 2):
            steel.box((W, .1, .05), loc=at(M, (0, d, zz)), rot=box_rot(M), bevel=0)
        for xx in (-W / 2, W / 2):
            steel.box((.05, .1, Hh), loc=at(M, (xx, d, 0)), rot=box_rot(M), bevel=0)
    a.part('Pod_hazard' + tg, 'SafetyStripe', m).box((W - .1, .02, .1), loc=at(M, (0, 1.0, Hh / 2 + .04)),
                                                    rot=box_rot(M), bevel=0)
    a.pivot(K.name('Muzzle_rocket', index), at(M, (0, -Lt / 2 - .03, 0)), key)
    K.tone(a, key, k=.93)


# ============================================================================= Fortress Bastion
BS_CIT = 5.95


def bs_hatch(a, loc, r=.44, parent=None):
    """Bastion's round split-leaf hatch: the cast coaming with its bolt ring, two half-disc leaves meeting on a seam,
    their grab arcs, the hinge blocks at both sides."""
    x, y, z = loc
    lid = a.part('Hatches', 'Armor', parent)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    k.ring(lid, [(r * .96, -.02), (r * 1.18, -.02), (r * 1.18, .06), (r * 1.08, .1), (r * .96, .1)], loc=loc, seg=18)
    for s in (-1, 1):
        half = [(s * .012, -r * .95)] + [(s * (.012 + math.sin(u) * r * .94), -math.cos(u) * r * .95)
                                         for u in [i * math.pi / 8 for i in range(1, 8)]] + [(s * .012, r * .95)]
        if s < 0:
            half = half[::-1]
        k.extrude(lid, half, .06, loc=(x, y, z + .11), axis='Z', chamfer=.012)
        steel.tube([(x + s * r * .25, y - r * .3, z + .14), (x + s * r * .35, y - r * .3, z + .2),
                    (x + s * r * .35, y + r * .3, z + .2), (x + s * r * .25, y + r * .3, z + .14)], .015, seg=5)
        k.block(steel, (.1, .22, .1), loc=(x + s * r * 1.12, y, z + .05), chamfer=.01)
    for i in range(10):
        u = (i + .5) * TAU / 10
        steel.cyl(.018, .025, loc=(x + math.cos(u) * r * 1.07, y + math.sin(u) * r * 1.07, z + .1), seg=6, bevel=0)


def bs_periscope(a, loc, facing_y=-1, parent=None, w=.36):
    """Bastion's vision block: a cast hood with a raked top, the glass, the rain guard over it."""
    x, y, z = loc
    k.block(a.part('Periscopes', 'Armor', parent), (w, .3, .24), loc=(x, y, z + .12), chamfer=.02, taper=(.92, .6))
    a.part('Glass', 'Glass', parent).box((w * .75, .02, .07), loc=(x, y + facing_y * .145, z + .13), bevel=0)
    a.part('Periscopes', 'Steel', parent).box((w * .85, .08, .02), loc=(x, y + facing_y * .15, z + .22), bevel=0)


def bs_smoke(a, x, y, z, s):
    """Bastion's smoke launchers: a square armoured box of four cells raked forward and out, dark cell mouths."""
    m = Matrix.Translation(Vector((s * x, y, z))) @ Matrix.Rotation(-s * .5, 4, 'Z') @ Matrix.Rotation(.6, 4, 'X')
    box = a.part('Smoke_launchers', 'Armor')
    k.block(box, (.42, .44, .42), loc=at(m, (0, 0, 0)), rot=box_rot(m), chamfer=.03)
    for cx in (-.1, .1):
        for cz in (-.1, .1):
            a.part('Smoke_cells', 'Undercarriage').box((.15, .02, .15), loc=at(m, (cx, -.225, cz)), rot=box_rot(m),
                                                       bevel=0)
    a.part('Smoke_launchers', 'Steel').box((.46, .06, .06), loc=at(m, (0, .1, -.22)), rot=box_rot(m), bevel=0)


def bs_mortar_turret(a):
    """The 2B8 / Tyulpan-read 240 mm breech-loading mortar in a low cast turret (Turret): the cast dome with its raked
    front and the roof slot, the cradle cheeks and trunnions, the long tube with the thickened crown (Main_cannon),
    the breech ring and block (Main_cannon_breech), two recoil cylinders (Main_cannon_buffer), the bore; Muzzle_main.
    The loading tray, the bomb rack with 240 mm rounds, the hatch and vision blocks."""
    t = a.pivot('Turret', (0, .6, BS_CIT))
    steel = a.part('Turret_steel', 'Steel', t)
    armor = a.part('Turret_armor', 'Armor', t)
    k.ring(steel, [(1.78, -.08), (1.98, -.08), (1.98, .04), (1.9, .08), (1.78, .08)], seg=32)
    dome = a.part('Turret_body', 'Team', t)
    k.lathe(dome, [(1.86, 0), (1.9, .12), (1.86, .34), (1.7, .5), (1.4, .62), (.9, .68), (0, .7)], seg=32,
            worn=(2, 4))
    # The raked cast front and the roof slot the mortar rises through.
    k.extrude(armor, [(-1.95, .02), (-1.2, .02), (-.95, .62), (-1.55, .55)], 2.4, axis='X', chamfer=.05, corner=.05)
    dark = a.part('Turret_dark', 'Undercarriage', t)
    dark.box((.95, 1.9, .04), loc=(0, -.25, .7), bevel=0)
    for s in (-1, 1):
        k.extrude(armor, [(-1.3, .55), (1.0, .55), (.75, 1.55), (-.15, 1.75), (-.65, 1.3)], .22, loc=(s * .6, 0, 0),
                  axis='X', chamfer=.03, corner=.05)
        along_x(steel, [(0, -.1), (.2, -.1), (.22, -.04), (.22, .04), (.2, .1), (0, .1)], (s * .75, .3, 1.15), seg=14)
        for j in range(3):
            steel.cyl(.03, .03, loc=(s * .73, -.6 + j * .45, 1.05 + j * .1), rot=(0, R90, 0), seg=6, bevel=0)
    e = math.radians(60)
    M = frame((0, .3, 1.15), e)
    k.block(a.part('Mortar_cradle', 'Armor', t), (.86, 1.5, .62), loc=at(M, (0, -.25, 0)), rot=box_rot(M),
            chamfer=.05)
    L = 3.55
    lathe_on(a.part('Main_cannon', 'Steel', t), M, [(.27, -.2), (.27, .55), (.235, .62), (.23, 1.6), (.215, L - .4),
                                                   (.25, L - .34), (.27, L - .25), (.27, L), (.19, L), (.19, L - .08),
                                                   (0, L - .08)], seg=20, worn=(3, 6))
    for s in (-1, 1):
        a.part('Main_cannon', 'Steel', t).box((.06, .1, .12), loc=at(M, (s * .27, -(L - .6), 0)), rot=box_rot(M),
                                             bevel=0)
    lathe_on(a.part('Main_cannon_breech', 'Armor', t), M, [(0, -1.3), (.34, -1.28), (.4, -1.18), (.42, -.6),
                                                          (.36, -.5), (.3, -.2)], seg=18)
    k.block(a.part('Main_cannon_lever', 'Steel', t), (.16, .2, .3), loc=at(M, (.4, 1.0, -.15)), rot=box_rot(M),
            chamfer=.02)
    for sx in (-1, 1):
        lathe_on(a.part('Main_cannon_buffer', 'Steel', t), M, [(0, -.9), (.1, -.88), (.1, .7), (.07, .74), (0, .74)],
                 0, sx * .36, .2, seg=12)
    lathe_on(a.part('Main_cannon_bore', 'Undercarriage', t), M, [(.19, L - .08), (.19, L - .06), (0, L - .06)],
             seg=16)
    a.pivot('Muzzle_main', at(M, (0, -L, 0)), 'Turret')
    # The loading tray with its crane on the turret's back, the rack of 240 mm rounds.
    tray = a.part('Loader_tray', 'Steel', t)
    tray.box((.55, 1.5, .06), loc=(0, 1.75, .78), rot=(.3, 0, 0), bevel=0)
    for sx in (-1, 1):
        tray.box((.05, 1.5, .16), loc=(sx * .28, 1.75, .84), rot=(.3, 0, 0), bevel=0)
    rack = a.part('Bomb_rack', 'Armor', t)
    rack.box((2.4, .42, .08), loc=(0, 2.0, .2), bevel=.01)
    for i in range(3):
        x = -.85 + i * .85
        k.lathe(a.part('Ready_bombs', 'Fuel', t), [(0, -.6), (.1, -.55), (.16, -.35), (.17, .25), (.12, .45),
                                                  (.06, .55), (0, .58)], loc=(x, 2.0, .42), rot=(R90, 0, 0), seg=12)
        for f in range(4):
            u = f * R90 + .78
            a.part('Ready_bombs', 'Steel', t).box((.015, .22, .26), loc=(x + math.cos(u) * .1, 2.62,
                                                                        .42 + math.sin(u) * .1),
                                                  rot=(0, u, 0), bevel=0)
    bs_hatch(a, (1.15, -.8, .52), r=.36, parent=t)
    bs_periscope(a, (-1.15, -.95, .5), parent=t)
    bs_periscope(a, (-1.4, .3, .45), parent=t, w=.3)
    tip = at(M, (0, -L, 0))
    K.soot(a, (0, .6 + tip[1], BS_CIT + tip[2]), radius=1.0, k=.45)
    K.tone(a, 'Turret', k=.95)


def bs_sponson_house(a, index, s, key, twin):
    """The turning part of a Bastion sponson on Mount_gun[.NNN]. Front pair (twin): a rounded cast house, a flat
    face plate, the half-drum mantlet and twin D-10-read 100 mm barrels (bore evacuator near the muzzle, a thin crown,
    no brake). Rear pair: a faceted shield house and a Bofors L/60-read 40 mm (recoil spring round the breech end, the
    cone flash hider, the top clip guide with its rounds). Gun_barrels / Gun_muzzles kick; Muzzle_gun[.NNN] and the
    per-barrel muzzles. Returns the barrel tip's y and height in the mount."""
    tg = sfx(index)
    steel = a.part('Gun_steel' + tg, 'Steel', key)
    k.ring(steel, [(.92, -.04), (1.06, -.04), (1.06, .06), (.98, .1), (.92, .1)], seg=22)
    if twin:
        k.lathe(a.part('Gun_house' + tg, 'Team', key), [(1.0, 0), (1.04, .28), (1.0, .58), (.86, .84), (.6, 1.0),
                                                       (.3, 1.07), (0, 1.08)], seg=24, worn=(2, 4))
        k.extrude(a.part('Gun_face' + tg, 'Armor', key), [(-1.05, .08), (-.82, .08), (-.62, .98), (-.86, .9)], 1.3,
                  axis='X', chamfer=.03, corner=.03)
        along_x(a.part('Gun_mantlet' + tg, 'Armor', key), [(0, -.62), (.32, -.6), (.34, -.55), (.34, .55), (.32, .6),
                                                          (0, .62)], (0, -1.0, .55), seg=16)
        y0, zg, L = -1.12, .55, 3.3
        bar = a.part('Gun_barrels' + tg, 'Steel', key)
        for bx in (-.26, .26):
            fwd(bar, [(0, -.05), (.11, -.05), (.11, .16), (.09, .2), (.085, 1.2), (.075, L - 1.0), (.08, L - .98),
                      (.112, L - .9), (.115, L - .55), (.08, L - .47), (.072, L - .45), (.07, L), (0, L)],
                (bx, y0, zg), seg=12, worn=(3, 6))
            fwd_ring(a.part('Gun_muzzles' + tg, 'Steel', key), [(.06, L - .12), (.082, L - .1), (.082, L + .02),
                                                                (.06, L + .02)], (bx, y0, zg), seg=12)
        mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .04, zg), key)
        per_barrel(a, mz, tag_of('gun', index), (-.26, .26))
        bs_periscope(a, (-.35 * s, -.45, 1.0), parent=key, w=.26)
        bs_hatch(a, (.3 * s, .3, 1.02), r=.3, parent=key)
        tip = y0 - L
        top = 1.08
    else:
        ring = [(-.5, -.82), (.5, -.82), (.88, -.3), (.88, .7), (-.88, .7), (-.88, -.3)]
        roof = [(-.36, -.62), (.36, -.62), (.68, -.2), (.68, .58), (-.68, .58), (-.68, -.2)]
        k.sharp_loft(a.part('Gun_house' + tg, 'Team', key), [[(x, y, 0.0) for x, y in ring],
                                                           [(x * 1.02, y * 1.02, .5) for x, y in ring],
                                                           [(x, y, .86) for x, y in roof]], chamfer=.04)
        dark = a.part('Gun_dark' + tg, 'Undercarriage', key)
        dark.box((.24, .06, .3), loc=(0, -.83, .45), bevel=0)
        y0, zg, L = -.8, .45, 2.75
        bar = a.part('Gun_barrels' + tg, 'Steel', key)
        fwd(bar, [(0, -.05), (.1, -.05), (.1, .12), (.06, .16), (.05, .8), (.046, L), (0, L)], (0, y0, zg), seg=10)
        for j in range(8):
            bar.torus(.072, .014, loc=(0, y0 - .2 - j * .075, zg), rot=(R90, 0, 0), seg=12, ring=4)
        fwd(a.part('Gun_muzzles' + tg, 'Steel', key), [(.042, L - .02), (.05, L), (.09, L + .34), (.08, L + .36),
                                                       (.05, L + .36), (0, L + .34)], (0, y0, zg), seg=12)
        # The clip guide over the breech: two rails, four rounds standing in it.
        for sx in (-.09, .09):
            steel.box((.03, .05, .5), loc=(sx, -.25, 1.05), bevel=0)
        for j in range(4):
            k.lathe(a.part('Gun_clips' + tg, 'Gilded', key), [(0, 0), (.035, 0), (.035, .3), (.025, .38), (0, .42)],
                    loc=(0, -.38 + j * .09, .86), seg=8)
        k.block(steel, (.22, .12, .06), loc=(0, -.25, 1.28), chamfer=0)
        bs_periscope(a, (.4 * s, -.3, .86), parent=key, w=.22)
        a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .36, zg), key)
        tip = y0 - L - .36
        top = .86
    K.lamp(a, (.7 * s, -.75, .7), (0, -1, 0), r=.07, parent=key)
    for i in range(8):
        u = i * TAU / 8 + .2
        steel.cyl(.028, .03, loc=(math.cos(u) * .82, math.sin(u) * .86, top * .62), seg=6, bevel=0)
    K.tone(a, key, k=.92)
    return tip, zg


def bs_bow_gun(a):
    """The M284-read 155 mm in the bow (Mount_gun.004): a conical cast mantlet with stepped collars, the tube with a
    mid-length bore evacuator, the slab double-baffle brake (Bow_barrels / Bow_muzzles kick), Muzzle_gun.004."""
    key = K.name('Mount_gun', 4)
    bm = a.pivot(key, (0, -8.72, 3.2))
    fwd(a.part('Bow_mantlet', 'Armor', bm), [(0, -.55), (.66, -.5), (.76, -.25), (.72, .06), (.56, .3), (.44, .36),
                                            (.4, .5), (0, .52)], (0, 0, 0), seg=20)
    for d, r in ((.36, .5), (.48, .36)):
        fwd_ring(a.part('Bow_collar', 'Steel', bm), [(r - .05, d), (r + .02, d), (r + .02, d + .06), (r - .05, d + .06)],
                 (0, 0, 0), seg=18)
    y0, L = -.52, 4.55
    bar = a.part('Bow_barrels', 'Steel', bm)
    fwd(bar, [(0, -.05), (.17, -.05), (.17, .14), (.14, .2), (.132, 1.7), (.15, 1.78), (.185, 1.9), (.185, 2.45),
              (.15, 2.56), (.125, 2.62), (.115, L), (0, L)], (0, y0, 0), seg=16, worn=(4, 8))
    br = a.part('Bow_muzzles', 'Undercarriage', bm)
    fwd(br, [(.12, L - .1), (.15, L - .08), (.15, L + .6), (.09, L + .6), (.09, L + .56), (0, L + .56)], (0, y0, 0),
        seg=16)
    for dd in (.12, .4):
        k.block(br, (.62, .12, .36), loc=(0, y0 - L - dd, 0), chamfer=.015)
    for zz in (-.2, .2):
        br.box((.62, .52, .05), loc=(0, y0 - L - .28, zz), bevel=.01)
    a.pivot(K.name('Muzzle_gun', 4), (0, y0 - L - .62, 0), key)
    K.soot(a, (0, -8.72 + y0 - L, 3.2), radius=.6, k=.3)


def bs_kornet(a):
    """A Kornet-EM-read twin launcher on the citadel roof (Part_missile, Mount_missile): the octagonal plinth, the
    elevating post, two transport-launch containers with their rimmed caps, flared rear ends and bands, the 1P45-read
    sight block between them with its two lenses; Muzzle_missile with per-tube muzzles."""
    pm = a.pivot('Part_missile', (1.42, 2.75, BS_CIT))
    k.lathe(a.part('Kornet_base', 'Armor', pm), [(.5, 0), (.5, .14), (.42, .24), (.2, .28), (.2, .4)], seg=8)
    km = a.pivot('Mount_missile', (0, 0, .45), 'Part_missile')
    steel = a.part('Kornet_steel', 'Steel', km)
    k.lathe(steel, [(.16, -.06), (.16, .05), (.1, .1), (.1, .3)], seg=10)
    e = .22
    M = frame((0, .1, .4), e)
    along_x(steel, [(0, -.32), (.05, -.32), (.05, .32), (0, .32)], (0, .1, .4), seg=8)
    tubes = a.part('Kornet_tubes', 'Team', km)
    xs = (-.26, .26)
    for x in xs:
        lathe_on(tubes, M, [(0, -.7), (.07, -.72), (.115, -.62), (.095, -.55), (.088, -.5), (.088, .62), (.1, .64),
                            (.1, .74), (.075, .74), (0, .73)], 0, x, 0, seg=14)
        for d in (-.3, .3):
            ring_on(steel, M, [(.088, d), (.1, d), (.1, d + .05), (.088, d + .05)], 0, x, 0, seg=14)
        steel.box((.06, .08, .14), loc=at(M, (x * .6, 0, -.05)), rot=box_rot(M), bevel=0)
    sight = a.part('Kornet_sight', 'Armor', km)
    k.block(sight, (.26, .34, .26), loc=at(M, (0, .05, .02)), rot=box_rot(M), chamfer=.02)
    for dx in (-.06, .06):
        lathe_on(a.part('Glass', 'Glass', km), M, [(.045, .2), (.045, .22), (0, .22)], 0, dx, .17, seg=10)
    k.block(sight, (.3, .12, .04), loc=at(M, (0, -.16, .28)), rot=box_rot(M), chamfer=0)
    mzk = a.pivot('Muzzle_missile', at(M, (0, -.76, 0)), 'Mount_missile')
    per_barrel(a, mzk, 'missile', xs)
    K.tone(a, 'Part_missile', k=.9)


def bs_zu23(a, index, s, x, y, z):
    """A ZU-23-2 read on its gallery (Mount_mg[.NNN]): the three-leg ring base (static), on the pivot the cradle,
    two 2A14 receivers, the long barrels with their jackets and slotted cone flash hiders (Zu_barrels / Zu_muzzles
    kick), the box magazines outboard, the two seats, the ZAP-23 sight, the elevation handwheel; per-barrel muzzles."""
    base = a.part('Zu_pedestals', 'Steel')
    for i in range(3):
        u = i * TAU / 3 + .3
        base.limb((x + math.cos(u) * .5, y + math.sin(u) * .5, z), (x, y, z + .42), .08, .1, bevel=0)
        base.cyl(.1, .04, loc=(x + math.cos(u) * .52, y + math.sin(u) * .52, z + .02), seg=8, bevel=0)
    k.lathe(base, [(.3, .38), (.3, .46), (.26, .52), (.26, .55)], loc=(x, y, z), seg=14)
    key = K.name('Mount_mg', index)
    zm = a.pivot(key, (x, y, z + .67))
    tg = sfx(index)
    car = a.part('Zu_carriage' + tg, 'Armor', zm)
    k.block(car, (.86, 1.0, .12), loc=(0, .1, -.12), chamfer=.02)
    for sx in (-1, 1):
        k.extrude(car, [(-.3, -.02), (.45, -.02), (.3, .32), (-.15, .32)], .07, loc=(sx * .3, 0, 0), axis='X',
                  chamfer=.01)
    steel = a.part('Zu_steel' + tg, 'Steel', zm)
    bar = a.part('Zu_barrels' + tg, 'Steel', zm)
    zg, y0, L = .3, -.15, 2.25
    for sx in (-1, 1):
        k.block(steel, (.13, .62, .2), loc=(sx * .13, .12, zg), chamfer=.015)
        fwd(bar, [(0, -.02), (.05, -.02), (.05, .3), (.04, .34), (.036, L), (0, L)], (sx * .13, y0, zg), seg=10)
        fwd(a.part('Zu_muzzles' + tg, 'Steel', zm), [(.034, L - .02), (.045, L), (.05, L + .05), (.042, L + .06),
                                                     (.054, L + .1), (.046, L + .11), (.058, L + .16), (.06, L + .2),
                                                     (.05, L + .22), (.034, L + .22), (0, L + .2)],
            (sx * .13, y0, zg), seg=10)
        k.block(a.part('Zu_magazines' + tg, 'Crate', zm), (.14, .44, .34), loc=(sx * .32, .1, zg - .05),
                rot=(0, sx * .15, 0), chamfer=.015)
        k.block(a.part('Zu_seats' + tg, 'Canvas', zm), (.26, .24, .07), loc=(sx * .52, .55, .1), chamfer=.015)
        steel.tube([(sx * .45, .55, -.05), (sx * .52, .55, .1)], .02, seg=5)
    handwheel(steel, (-.5 * s, .2, .2), .1)
    steel.cyl(.02, .3, loc=(.0, .35, .45), seg=6, bevel=0)
    k.block(a.part('Zu_sight' + tg, 'Armor', zm), (.14, .18, .14), loc=(0, .32, .6), chamfer=.015)
    a.part('Glass', 'Glass', zm).box((.08, .015, .05), loc=(0, .22, .68), bevel=0)
    mk = a.pivot(K.name('Muzzle_mg', index), (0, y0 - L - .23, zg), key)
    per_barrel(a, mk, tag_of('mg', index), (-.13, .13))
    K.tone(a, key, k=.92)


# ============================================================================= Bastion Mk.0
M0_TOP = 5.3


def m0_hatch(a, loc, size=(.9, .9), parent=None):
    """Mk.0's riveted plate hatch: a flat lid on an angle-iron coaming, rivets round its edge, two long strap hinges
    across it, the drop-bolt handle."""
    x, y, z = loc
    w, d = size
    lid = a.part('Hatches', 'Armor', parent)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    lid.box((w + .1, d + .1, .06), loc=(x, y, z + .03), bevel=.01)
    lid.box((w, d, .04), loc=(x, y, z + .08), bevel=.008)
    for dx in (-w * .28, w * .28):
        steel.box((.08, d * .8, .025), loc=(x + dx, y + d * .08, z + .11), bevel=0)
        along_x(steel, [(.035, -.06), (.035, .06)], (x + dx, y + d / 2 + .03, z + .08), seg=6)
    steel.tube([(x - .12, y - d * .38, z + .1), (x - .12, y - d * .38, z + .17), (x + .12, y - d * .38, z + .17),
                (x + .12, y - d * .38, z + .1)], .016, seg=5)
    for i in range(16):
        f = i / 16
        if f < .25:
            px, py = x - w / 2 + .04 + f * 4 * (w - .08), y - d / 2 + .04
        elif f < .5:
            px, py = x + w / 2 - .04, y - d / 2 + .04 + (f - .25) * 4 * (d - .08)
        elif f < .75:
            px, py = x + w / 2 - .04 - (f - .5) * 4 * (w - .08), y + d / 2 - .04
        else:
            px, py = x - w / 2 + .04, y + d / 2 - .04 - (f - .75) * 4 * (d - .08)
        steel.cyl(.016, .02, loc=(px, py, z + .1), seg=6, bevel=0)


def m0_periscope(a, loc, u, parent=None):
    """A Mk.0 vision slot box: a plain riveted box with a slit and a hinged cover plate propped open."""
    x, y, z = loc
    k.block(a.part('Periscopes', 'Armor', parent), (.18, .14, .13), loc=(x, y, z + .065), rot=(0, 0, u), chamfer=0)
    a.part('Glass', 'Glass', parent).box((.12, .015, .03), loc=(x + math.sin(u) * .075, y - math.cos(u) * .075,
                                                              z + .08), rot=(0, 0, u), bevel=0)
    a.part('Periscopes', 'Steel', parent).box((.16, .1, .015), loc=(x + math.sin(u) * .1, y - math.cos(u) * .1,
                                                                   z + .15), rot=(.5, 0, u), bevel=0)


def m0_sponson(a, index, s, key):
    """The turning part of a Mk.0 front sponson on Mount_gun[.NNN]: a twelve-sided riveted drum with a lipped cap,
    the flat riveted gun shield with two ports, two long early 100 mm barrels with slotted cylindrical brakes
    (Gun_barrels / Gun_muzzles kick) over exposed recoil cylinders, the vision slit box; Muzzle_gun[.NNN] and the
    per-barrel muzzles."""
    tg = sfx(index)
    drum = a.part('Gun_house' + tg, 'Team', key)
    k.lathe(drum, [(.98, 0), (1.0, .04), (1.0, 1.12), (1.05, 1.15), (1.05, 1.2), (.9, 1.24), (.5, 1.3), (0, 1.31)],
            seg=12, worn=(2, 4))
    steel = a.part('Gun_steel' + tg, 'Steel', key)
    for zz in (.15, .6, 1.05):
        for i in range(12):
            u = (i + .5) * TAU / 12
            steel.cyl(.024, .03, loc=(math.cos(u) * 1.01, math.sin(u) * 1.01, zz), rot=(0, R90, u), seg=6, bevel=0)
    shield = a.part('Gun_shield' + tg, 'Armor', key)
    k.block(shield, (1.5, .16, 1.12), loc=(0, -1.0, .6), chamfer=.03)
    dark = a.part('Gun_dark' + tg, 'Undercarriage', key)
    for bx in (-.27, .27):
        dark.box((.2, .03, .2), loc=(bx, -1.085, .62), bevel=0)
    for i in range(7):
        for zz in (.1, 1.06):
            steel.cyl(.02, .03, loc=(-.66 + i * .22, -1.085, zz), rot=(R90, 0, 0), seg=6, bevel=0)
    y0, zg, L = -1.08, .62, 2.85
    bar = a.part('Gun_barrels' + tg, 'Steel', key)
    for bx in (-.27, .27):
        fwd(bar, [(0, -.05), (.09, -.05), (.09, .25), (.08, .28), (.075, 1.4), (.068, 1.42), (.064, L), (0, L)],
            (bx, y0, zg), seg=12)
        fwd(a.part('Gun_muzzles' + tg, 'Undercarriage', key),
            [(.06, L - .02), (.095, L), (.095, L + .07), (.08, L + .08), (.08, L + .12), (.095, L + .13),
             (.095, L + .2), (.08, L + .21), (.08, L + .25), (.095, L + .26), (.095, L + .34), (.05, L + .34),
             (0, L + .33)], (bx, y0, zg), seg=12)
        fwd(steel, [(0, -.02), (.045, -.02), (.045, .85), (.03, .9), (0, .9)], (bx, y0, zg - .14), seg=8)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .36, zg), key)
    per_barrel(a, mz, tag_of('gun', index), (-.27, .27))
    m0_periscope(a, (.42 * s, -.75, 1.3), 0, parent=key)
    K.tone(a, key, k=.9)
    return y0 - L - .36, zg


def m0_mortar(a):
    """The M1-240 mm-read banded howitzer tube on Mk.0's open pedestal (Turret): the riveted turntable, two open side
    frames with lightening holes, the toothed elevating arc, handwheels, the angled splinter shield; the tube with its
    breech hoops and the muzzle bell (Main_cannon), the interrupted-screw breech (Main_cannon_breech), the recoil
    cylinders (Main_cannon_buffer); Muzzle_main; ready bombs."""
    t = a.pivot('Turret', (0, .55, M0_TOP))
    steel = a.part('Turret_steel', 'Steel', t)
    tt = a.part('Turret_armor', 'Armor', t)
    k.lathe(tt, [(1.45, 0), (1.5, .05), (1.5, .18), (1.38, .22), (0, .23)], seg=24, worn=(2,))
    for i in range(20):
        u = (i + .5) * TAU / 20
        steel.cyl(.022, .03, loc=(math.cos(u) * 1.4, math.sin(u) * 1.4, .23), seg=6, bevel=0)
    dark = a.part('Turret_dark', 'Undercarriage', t)
    for s in (-1, 1):
        k.extrude(a.part('Mortar_frames', 'Armor', t), [(-.75, .23), (.95, .23), (.75, 1.45), (.1, 1.62), (-.3, 1.4)],
                  .12, loc=(s * .56, 0, 0), axis='X', chamfer=.02, corner=.04)
        for (yy, zz, r) in ((.45, .65, .2), (-.3, .62, .16)):
            dark.cyl(r, .13, loc=(s * .56, yy, zz), rot=(0, R90, 0), seg=12, bevel=0)
        along_x(steel, [(0, -.07), (.14, -.07), (.15, -.03), (.15, .03), (.14, .07), (0, .07)], (s * .66, .25, 1.15),
                seg=12)
    # The toothed elevating arc on the left frame and its pinion, two handwheels.
    for i in range(11):
        u = math.radians(-10 + i * 7)
        p = (.69, .25 + math.cos(u) * .62, 1.15 - math.sin(u) * .62)
        steel.box((.05, .06, .07), loc=p, rot=(-u, 0, 0), bevel=0)
    handwheel(steel, (.82, .7, .62), .16)
    handwheel(steel, (-.82, .55, .7), .14)
    k.block(a.part('Mortar_shield', 'Armor', t), (1.8, .1, .95), loc=(0, -1.0, .68), rot=(-.28, 0, 0), chamfer=.02)
    dark.box((.22, .03, .16), loc=(.55, -1.08, 1.0), rot=(-.28, 0, 0), bevel=0)
    for i in range(6):
        steel.cyl(.018, .03, loc=(-.75 + i * .3, -1.07, .3), rot=(R90 - .28, 0, 0), seg=6, bevel=0)
    e = math.radians(55)
    M = frame((0, .25, 1.15), e)
    L = 3.0
    lathe_on(a.part('Main_cannon', 'Steel', t), M, [(.33, -.55), (.33, -.4), (.36, -.38), (.36, -.25), (.33, -.23),
                                                   (.33, .1), (.36, .12), (.36, .25), (.33, .27), (.3, .6),
                                                   (.33, .62), (.33, .74), (.29, .76), (.25, 1.4), (.24, L - .4),
                                                   (.27, L - .3), (.31, L - .08), (.31, L), (.21, L), (.21, L - .1),
                                                   (0, L - .1)], seg=18, worn=(4, 12))
    lathe_on(a.part('Main_cannon_breech', 'Armor', t), M, [(0, -.92), (.3, -.9), (.34, -.86), (.34, -.6), (.3, -.55)],
             seg=16)
    for j in range(6):
        u = j * TAU / 6
        a.part('Main_cannon_breech', 'Armor', t).box((.12, .08, .1), loc=at(M, (math.cos(u) * .3, .78,
                                                                               math.sin(u) * .3)),
                                                    rot=box_rot(M), bevel=0)
    for sx in (-1, 1):
        lathe_on(a.part('Main_cannon_buffer', 'Steel', t), M, [(0, -.7), (.085, -.68), (.085, .8), (.06, .83),
                                                              (0, .83)], 0, sx * .2, -.36, seg=10)
    a.pivot('Muzzle_main', at(M, (0, -L, 0)), 'Turret')
    for i in range(2):
        k.lathe(a.part('Ready_bombs', 'Fuel', t), [(0, -.5), (.11, -.4), (.14, -.18), (.14, .32), (.09, .45),
                                                   (0, .5)], loc=(-.5 + i * 1.0, 1.25, .45), rot=(R90, 0, 0), seg=10)
    tip = at(M, (0, -L, 0))
    K.soot(a, (0, .55 + tip[1], M0_TOP + tip[2]), radius=.9, k=.45)


# ============================================================================= Fenrir
FN_DECK = 2.42


def fn_hatch(a, loc, r=.36, parent=None):
    """Fenrir's insulated roof hatch: a low coaming, the domed padded lid with its rubber seal, the quick-release
    lever, a small vent cap."""
    x, y, z = loc
    k.ring(a.part('Hatches', 'Armor', parent), [(r * .95, -.02), (r * 1.12, -.02), (r * 1.12, .05), (r * .95, .05)],
           loc=loc, seg=16)
    a.part('Hatch_seal', 'Rubber', parent).torus(r * .98, .025, loc=(x, y, z + .06), seg=16, ring=4)
    k.lathe(a.part('Hatches', 'Team', parent), [(r * .94, .05), (r * .94, .1), (r * .75, .16), (r * .4, .19), (0, .2)],
            loc=loc, seg=16)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    steel.limb((x - r * .5, y - r * .2, z + .2), (x + r * .4, y - r * .45, z + .2), .04, .03, bevel=0)
    steel.cyl(.05, .06, loc=(x - r * .5, y - r * .2, z + .2), seg=8, bevel=0)
    k.lathe(steel, [(.05, 0), (.05, .05), (.08, .06), (0, .09)], loc=(x + r * .3, y + r * .4, z + .17), seg=8)
    along_x(steel, [(.035, -r * .4), (.035, r * .4)], (x, y + r * 1.08, z + .05), seg=6)


def fn_flak(a):
    """The Gepard-read flak turret on Mount_mg (front unit): the octagonal barbette (static), the turret race, the
    faceted house with its nose tracking dish and the folding search antenna aft, the two gun pods outside the
    cheeks with KDA-read 35 mm barrels (jackets, slim slotted brakes, muzzle-velocity coils: Flak_barrels /
    Flak_muzzles kick), the feed chutes, sights and hatch; Muzzle_mg with the per-barrel muzzles."""
    k.lathe(a.part('Barbette', 'Armor'), [(1.0, 0), (1.0, .36), (.9, .44)], loc=(0, -2.55, FN_DECK), seg=8, worn=(1,))
    key = 'Mount_mg'
    m = a.pivot(key, (0, -2.55, FN_DECK + .44))
    steel = a.part('Flak_steel', 'Steel', m)
    k.ring(steel, [(.8, -.03), (.92, -.03), (.92, .06), (.86, .09), (.8, .09)], seg=20)
    base = [(-.5, -.92), (.5, -.92), (.82, -.5), (.82, .7), (.7, .95), (-.7, .95), (-.82, .7), (-.82, -.5)]
    mid = [(-.48, -1.0), (.48, -1.0), (.84, -.55), (.84, .75), (.72, 1.0), (-.72, 1.0), (-.84, .75), (-.84, -.55)]
    roof = [(-.36, -.72), (.36, -.72), (.66, -.38), (.66, .7), (.56, .88), (-.56, .88), (-.66, .7), (-.66, -.38)]
    house = a.part('Flak_house', 'Team', m)
    k.sharp_loft(house, [[(x, y, 0.0) for x, y in base], [(x, y, .5) for x, y in mid],
                         [(x, y, .9) for x, y in roof]], chamfer=.04)
    k.inset(house, lambda c, n, f: abs(n.x) > .8 and c.z > .1, width=.06, depth=-.015)
    # The tracking radar dish on the nose (a shallow dish behind its rim, the dark face).
    fwd(a.part('Flak_dish', 'Medical', m), [(0, -.06), (.34, -.04), (.36, .02), (.3, .06), (0, .08)], (0, -.98, .55),
        seg=18)
    fwd(a.part('Flak_dark', 'Undercarriage', m), [(.26, .07), (.26, .085), (0, .085)], (0, -.98, .55), seg=14)
    steel.box((.12, .2, .12), loc=(0, -.92, .3), bevel=0)
    # The folding search antenna aft: the hinge post, the long flat array, its drive.
    steel.cyl(.06, .4, loc=(0, .65, 1.1), seg=8, bevel=0)
    k.block(a.part('Flak_search', 'Medical', m), (1.25, .12, .32), loc=(0, .68, 1.28), rot=(.15, 0, 0), chamfer=.02)
    a.part('Flak_dark', 'Undercarriage', m).box((1.12, .02, .2), loc=(0, .61, 1.45), rot=(.15, 0, 0), bevel=0)
    # Gun pods outside the cheeks, the trunnion shafts, the feed chutes over the house shoulders.
    for s in (-1, 1):
        pod = a.part('Flak_pods', 'Armor', m)
        k.extrude(pod, [(-.62, .02), (.5, .02), (.58, .3), (.4, .5), (-.45, .5), (-.62, .3)], .3, loc=(s * 1.02, 0, 0),
                  axis='X', chamfer=.025, corner=.03)
        along_x(steel, [(0, -.12), (.1, -.12), (.1, .12), (0, .12)], (s * .9, -.05, .35), seg=10)
        steel.tube([(s * .62, .3, .82), (s * .82, .25, .9), (s * 1.0, .1, .55)], .06, seg=8)
        a.part('Glass', 'Glass', m).box((.2, .02, .08), loc=(s * .3, -.74, .86), rot=(-.5, 0, 0), bevel=0)
    y0, zg, L = -.6, .3, 2.05
    bar = a.part('Flak_barrels', 'Steel', m)
    mu = a.part('Flak_muzzles', 'Undercarriage', m)
    for s in (-1, 1):
        x = s * 1.0
        fwd(bar, [(0, -.03), (.075, -.03), (.075, .22), (.058, .26), (.056, .95), (.044, 1.0), (.04, L), (0, L)],
            (x, y0, zg), seg=10)
        fwd_ring(bar, [(.04, .55), (.07, .56), (.07, .7), (.04, .71)], (x, y0, zg), seg=10)
        fwd(mu, [(.04, L - .02), (.06, L), (.06, L + .05), (.05, L + .06), (.05, L + .09), (.06, L + .1),
                 (.06, L + .15), (.05, L + .16), (.05, L + .19), (.06, L + .2), (.06, L + .25), (.03, L + .25),
                 (0, L + .24)], (x, y0, zg), seg=10)
        fwd_ring(mu, [(.042, L - .3), (.075, L - .28), (.075, L - .14), (.042, L - .12)], (x, y0, zg), seg=10)
    mk = a.pivot('Muzzle_mg', (0, y0 - L - .26, zg), key)
    per_barrel(a, mk, 'mg', (-1.0, 1.0))
    fn_hatch(a, (.35, .3, .9), r=.26, parent=m)
    K.tone(a, key, k=.93)


def fn_rockets(a, index, s):
    """An MLRS-read launch pod on Mount_rocket[.NNN] (rear unit): the turntable, the launcher cage (side rails and
    cross frames), the boxed pod with its stiffener ribs and grid rear face, six frangible caps on the front face,
    the elevating ram, snow on top; Muzzle_rocket at the front face."""
    key = K.name('Mount_rocket', index)
    x0, y0 = s * 1.22, 3.8
    tg = sfx(index)
    k.ring(a.part('Launcher_base', 'Steel'), [(.56, 0), (.68, 0), (.68, .16), (.62, .22), (.56, .22)],
           loc=(x0, y0, FN_DECK), seg=18)
    m = a.pivot(key, (x0, y0, FN_DECK + .22))
    tt = a.part('Launcher_turntable' + tg, 'Armor', m)
    k.lathe(tt, [(.6, -.04), (.6, .08), (.52, .14), (0, .16)], seg=18)
    k.block(tt, (.7, .5, .32), loc=(0, .95, .1), chamfer=.03)
    steel = a.part('Launcher_steel' + tg, 'Steel', m)
    e = .35
    M = frame((0, .15, .85), e)
    pod = a.part('Pod_box' + tg, 'Team', m)
    k.block(pod, (1.0, 3.0, .72), loc=at(M, (0, 0, 0)), rot=box_rot(M), chamfer=.03)
    for j in range(9):
        d = -1.2 + j * .3
        for sx in (-1, 1):
            pod.box((.03, .05, .7), loc=at(M, (sx * .515, d, 0)), rot=box_rot(M), bevel=0)
        pod.box((.96, .05, .03), loc=at(M, (0, d, .37)), rot=box_rot(M), bevel=0)
    for sx in (-1, 1):
        steel.box((.06, 3.1, .1), loc=at(M, (sx * .56, 0, -.36)), rot=box_rot(M), bevel=0)
        steel.limb((sx * .4, .9, .25), at(M, (sx * .56, .9, -.36)), .06, .06, bevel=0)
    for d in (-1.0, 1.0):
        steel.box((1.18, .08, .06), loc=at(M, (0, d, -.4)), rot=box_rot(M), bevel=0)
    face = a.part('Pod_face' + tg, 'Armor', m)
    face.box((1.04, .05, .76), loc=at(M, (0, -1.515, 0)), rot=box_rot(M), bevel=.01)
    caps = a.part('Pod_caps' + tg, 'Canvas', m)
    for ix in range(3):
        for iz in range(2):
            p = (-.31 + ix * .31, -1.54, -.17 + iz * .34)
            lathe_on(caps, M, [(.13, 0), (.13, .015), (.1, .03), (.05, .035), (0, .035)], -p[1] - .0, p[0], p[2],
                     seg=12)
    grid = a.part('Pod_grid' + tg, 'Undercarriage', m)
    grid.box((.94, .02, .66), loc=at(M, (0, 1.51, 0)), rot=box_rot(M), bevel=0)
    for ix in (-.16, .16):
        steel.box((.03, .04, .68), loc=at(M, (ix, 1.52, 0)), rot=box_rot(M), bevel=0)
    steel.box((.96, .04, .03), loc=at(M, (0, 1.52, 0)), rot=box_rot(M), bevel=0)
    a.part('Launcher_rams' + tg, 'Undercarriage', m).tube([(0, .95, .26), (0, .55, .55)], .09, seg=8)
    steel.tube([(0, .55, .55), at(M, (0, .5, -.38))], .055, seg=8)
    a.part('Pod_snow' + tg, 'Snow', m).box((.9, 2.2, .06), loc=at(M, (0, .2, .4)), rot=box_rot(M), taper=(.85, .9),
                                           bevel=.02)
    a.pivot(K.name('Muzzle_rocket', index), at(M, (0, -1.6, 0)), key)
    K.tone(a, key, k=.93)


def fn_radar(a):
    """The target-marking radar at the stern: the base box, a three-stage telescopic mast with collars, its fold
    hinge and strut; on Radar the drive, a lattice frame carrying the planar array (element rows on the face) and the
    IFF strip on top."""
    k.block(a.part('Mast_base', 'Armor'), (1.0, 1.0, .5), loc=(0, 6.75, FN_DECK + .25), chamfer=.05)
    mast = a.part('Mast', 'Steel')
    z = FN_DECK + .5
    k.lathe(mast, [(.17, 0), (.17, .8), (.21, .82), (.21, .9), (.14, .92), (.14, 1.5), (.18, 1.52), (.18, 1.6),
                   (.11, 1.62), (.11, 2.1), (.15, 2.12), (.15, 2.18)], loc=(0, 6.75, z), seg=10)
    along_x(mast, [(0, -.25), (.09, -.25), (.09, .25), (0, .25)], (0, 6.75, z + .1), seg=8)
    mast.tube([(0, 7.2, z), (0, 6.85, z + 1.2)], .045, seg=6)
    r = a.pivot('Radar', (0, 6.75, FN_DECK + 2.75))
    k.lathe(a.part('Radar_drive', 'Armor', r), [(.2, -.12), (.2, .02), (.14, .06), (.1, .1)], seg=10)
    fr = a.part('Radar_frame', 'Steel', r)
    for x in (-.85, -.3, .3, .85):
        fr.box((.05, .05, .66), loc=(x, .1, .3), bevel=0)
    for zz in (0.0, .62):
        fr.box((1.8, .05, .05), loc=(0, .1, zz), bevel=0)
    for x0, x1 in ((-.85, -.3), (-.3, .3), (.3, .85)):
        fr.limb((x0, .12, 0), (x1, .12, .62), .03, .03, bevel=0)
    fr.limb((0, 0, .02), (0, .1, .02), .1, .08, bevel=0)
    k.block(a.part('Radar_array', 'Armor', r), (1.8, .12, .7), loc=(0, -.02, .27), chamfer=.03)
    face = a.part('Radar_face', 'Undercarriage', r)
    for j in range(7):
        face.box((1.65, .02, .04), loc=(0, -.085, .03 + j * .085), bevel=0)
    k.block(a.part('Radar_iff', 'Medical', r), (1.5, .1, .1), loc=(0, -.02, .68), chamfer=.015)


# ============================================================================= Inferno (behemoth_inferno)
IN_T = (0.0, .4, 3.05)


def in_hatch(a, loc, parent=None, rx=.38, ry=.3, u=0.0):
    """Inferno's oval hatch: a flat oval lid on a raised oval rim, two hinge knuckles at the back, a T handle."""
    x, y, z = loc
    lid = a.part('Hatches', 'Armor', parent)
    k.extrude(lid, ellipse(0, 0, rx * 1.15, ry * 1.18, n=18), .06, loc=(x, y, z + .03), rot=(0, 0, u), axis='Z',
              chamfer=.015)
    k.extrude(lid, ellipse(0, 0, rx, ry, n=18), .05, loc=(x, y, z + .085), rot=(0, 0, u), axis='Z', chamfer=.012,
              taper=(.94, .92))
    steel = a.part('Hatch_fittings', 'Steel', parent)
    cu, su = math.cos(u), math.sin(u)
    for dx in (-rx * .45, rx * .45):
        px, py = x + dx * cu - (ry + .04) * su, y + dx * su + (ry + .04) * cu
        steel.cyl(.04, .14, loc=(px, py, z + .08), rot=(0, R90, u), seg=8, bevel=0)
    steel.limb((x - .1 * cu + ry * .4 * su, y - .1 * su - ry * .4 * cu, z + .14),
               (x + .1 * cu + ry * .4 * su, y + .1 * su - ry * .4 * cu, z + .14), .03, .03, bevel=0)


def in_periscope(a, loc, parent=None):
    """Inferno's driver / commander vision block: a low wedge housing with a wide glass and a sunshade lip."""
    x, y, z = loc
    k.extrude(a.part('Periscopes', 'Armor', parent), [(-.15, 0), (.12, 0), (.1, .16), (-.08, .2)], .32,
              loc=(x, y, z), axis='X', chamfer=.015)
    a.part('Glass', 'Glass', parent).box((.26, .02, .07), loc=(x, y - .13, z + .1), rot=(-.25, 0, 0), bevel=0)
    a.part('Periscopes', 'Steel', parent).box((.3, .08, .015), loc=(x, y - .14, z + .19), bevel=0)


def in_smoke(a, x, y, z, s, parent):
    """Inferno's smoke launchers: a three-tube cluster of 76 mm tubes in an armoured cowl on the turret side."""
    cowl = a.part('Smoke_launchers', 'Armor', parent)
    k.extrude(cowl, [(-.32, -.05), (.25, -.05), (.25, .28), (-.2, .32)], .2, loc=(s * x, y, z), axis='X', chamfer=.02)
    tubes = a.part('Smoke_tubes', 'Steel', parent)
    for i in range(3):
        d = Vector((s * .45, -.75, .45 + i * .12))
        p = Vector((s * (x + .02), y - .18 + i * .14, z + .14))
        k.lathe(tubes, [(.06, 0), (.06, .26), (.07, .27), (.07, .3), (.05, .3), (.05, .27), (0, .27)], loc=tuple(p),
                rot=dir_rot(d), seg=10)


def in_turret_fittings(a):
    """On Turret (the Behemoth house is the model's own): the race ring, the twin ball mantlet, the two M67-read
    flame projectors (Main_cannon[_2]: the finned projector tube; _jacket: the bolted armoured shroud; _hose: the
    braided fuel hose with its ferrules; Muzzle_brake[_2]: the nozzle cone with the igniter box; _glow: the nozzle and
    pilot glow; _pilot: the pilot jet tube), Muzzle_main between them; the cupola with its vision blocks, the oval
    hatch, the armoured sight with its doors, the smoke clusters."""
    t = 'Turret'
    steel = a.part('Turret_steel', 'Steel', t)
    k.ring(steel, [(1.82, -.14), (2.02, -.14), (2.02, -.04), (1.94, 0), (1.82, 0)], seg=32)
    for i in range(24):
        u = (i + .5) * TAU / 24
        steel.cyl(.03, .04, loc=(math.cos(u) * 1.98, math.sin(u) * 1.98, -.01), seg=6, bevel=0)
    mant = a.part('Gun_mantlet', 'Armor', t)
    k.extrude(mant, [(-2.66, .12), (-2.25, .12), (-2.2, .86), (-2.55, .82)], 1.7, axis='X', chamfer=.04, corner=.04)
    y0, y1, z = -2.68, -5.9, .5
    for x, n in ((-.45, ''), (.45, '_2')):
        fwd(mant, [(0, -.3), (.24, -.28), (.27, -.12), (.26, .04), (.2, .12), (0, .14)], (x, y0 + .1, z), seg=16)
        L = y0 - y1
        tube = a.part(f'Main_cannon{n}', 'Steel', t)
        fwd(tube, [(0, -.05), (.12, -.05), (.12, .1), (.095, .14), (.09, L - 1.1), (.1, L - 1.08), (.1, L - .12),
                   (.115, L - .1), (.115, L), (0, L)], (x, y0, z), seg=14, worn=(4,))
        for f in range(6):
            u = f * TAU / 6 + TAU / 12
            tube.box((.02, .95, .08), loc=(x + math.cos(u) * .13, y0 - L + .6, z + math.sin(u) * .13),
                     rot=(0, -u, 0), bevel=0)
        jac = a.part(f'Main_cannon{n}_jacket', 'Armor', t)
        fwd(jac, [(0, -.02), (.2, -.02), (.2, .06), (.165, .1), (.165, 1.15), (.13, 1.28), (.1, 1.3), (0, 1.3)],
            (x, y0, z), seg=14, worn=(3,))
        for d in (.35, .85):
            fwd_ring(jac, [(.164, d), (.185, d), (.185, d + .07), (.164, d + .07)], (x, y0, z), seg=14)
        for i in range(8):
            u = i * TAU / 8
            jac.cyl(.022, .03, loc=(x + math.cos(u) * .18, y0 - .02, z + math.sin(u) * .18), rot=(R90, 0, 0), seg=6,
                    bevel=0)
        hose = a.part(f'Main_cannon{n}_hose', 'Rubber', t)
        path = [(x * 1.3, y0 + .12, z - .2), (x * 1.3, y0 - .2, z - .24), (x * 1.05, y0 - 1.3, z - .2),
                (x, y1 + .82, z - .17)]
        hose.tube(path, .05, seg=8)
        for p in path[1:]:
            hose.cyl(.07, .12, loc=p, rot=K.FORWARD, seg=8, bevel=0)
        noz = a.part(f'Muzzle_brake{n}', 'Charred', t)
        fwd(noz, [(.1, 0), (.14, .04), (.16, .18), (.15, .26), (.11, .34), (.08, .37), (.06, .37), (.06, .33),
                  (0, .33)], (x, y1, z), seg=14)
        k.block(noz, (.12, .2, .12), loc=(x, y1 - .12, z + .17), chamfer=.015)
        noz.tube([(x, y1 - .04, z + .2), (x, y1 + .3, z + .19), (x * 1.05, y1 + .7, z + .1)], .018, seg=5)
        glow = a.part(f'Muzzle_brake{n}_glow', 'LavaGlow', t)
        fwd_ring(glow, [(.055, .345), (.075, .35), (.075, .36), (.055, .36)], (x, y1, z), seg=12)
        glow.cyl(.03, .04, loc=(x, y1 - .14, z - .17), rot=K.FORWARD, seg=6, bevel=0)
        pilot = a.part(f'Muzzle_brake{n}_pilot', 'Steel', t)
        pilot.tube([(x, y1 + .9, z - .17), (x, y1 - .1, z - .17)], .025, seg=6)
        k.block(pilot, (.08, .12, .08), loc=(x, y1 + .35, z - .17), chamfer=0)
        for f in (.35, .65):
            a.part('Heat_shields', 'Steel', t).box((.3, .5, .025), loc=(x, y1 + (y0 - y1) * f, z + .11), bevel=0)
    a.pivot('Muzzle_main', (0, y1 - .38, z), t)
    # The cupola (vision blocks round it), the loader's oval hatch, the armoured sight with its doors.
    cup = a.part('Cupola', 'Armor', t)
    k.lathe(cup, [(.46, 0), (.46, .14), (.42, .2), (.42, .3), (.32, .34), (0, .36)], loc=(.95, .65, .95), seg=16)
    for j in range(5):
        u = -R90 + (j - 2) * .6
        k.block(cup, (.15, .08, .1), loc=(.95 + math.cos(u) * .43, .65 + math.sin(u) * .43, 1.17),
                rot=(0, 0, u + R90), chamfer=0)
        a.part('Glass', 'Glass', t).box((.11, .015, .05), loc=(.95 + math.cos(u) * .475, .65 + math.sin(u) * .475,
                                                              1.18), rot=(0, 0, u + R90), bevel=0)
    in_hatch(a, (.05, 1.45, .95), parent=t)
    sight = a.part('Sight', 'Armor', t)
    k.block(sight, (.4, .45, .34), loc=(1.15, -1.25, 1.12), chamfer=.04, taper=(.9, .8))
    a.part('Glass', 'Glass', t).box((.28, .015, .12), loc=(1.15, -1.48, 1.14), bevel=0)
    for s in (-1, 1):
        steel.box((.15, .03, .16), loc=(1.15 + s * .2, -1.5, 1.14), rot=(0, 0, -s * .7), bevel=0)
        in_smoke(a, 2.0, .15, .55, s, t)


def in_zpu(a):
    """A ZPU-2-read twin 14.5 mm on the turret roof (Mount_mg): the pedestal, the cradle, two KPV barrels with
    perforated cooling jackets and cone flash hiders (Kpv_barrels / Kpv_muzzles kick), the outboard ammunition boxes,
    the curved two-panel shield, the sight post; Muzzle_mg with the per-barrel muzzles."""
    key = 'Mount_mg'
    m = a.pivot(key, (-.85, .7, .95), 'Turret')
    steel = a.part('Kpv_steel', 'Steel', m)
    k.lathe(a.part('Kpv_mount', 'Armor', m), [(.36, 0), (.36, .06), (.2, .1), (.16, .2), (.2, .24), (.2, .28)],
            seg=14)
    k.block(steel, (.34, .5, .1), loc=(0, .05, .32), chamfer=.01)
    zg, y0, L = .42, -.15, 1.32
    bar = a.part('Kpv_barrels', 'Steel', m)
    for bx in (-.1, .1):
        k.block(steel, (.1, .55, .14), loc=(bx, .18, zg), chamfer=.01)
        prof = [(0, -.02), (.05, -.02)]
        for j in range(10):
            d = .02 + j * .09
            prof += [(.05, d), (.044, d + .02), (.044, d + .05), (.05, d + .07)]
        prof += [(.05, .95), (.03, .98), (.028, L), (0, L)]
        fwd(bar, prof, (bx, y0, zg), seg=10)
        fwd(a.part('Kpv_muzzles', 'Steel', m), [(.028, L - .02), (.035, L), (.05, L + .18), (.042, L + .2),
                                                (.028, L + .2), (0, L + .18)], (bx, y0, zg), seg=10)
    for s in (-1, 1):
        k.block(a.part('Kpv_ammo', 'Crate', m), (.16, .36, .28), loc=(s * .3, .1, zg - .02), chamfer=.015)
        k.block(a.part('Kpv_shield', 'Team', m), (.34, .05, .4), loc=(s * .2, -.32, zg + .1), rot=(-.15, 0, s * .35),
                chamfer=.012)
    steel.cyl(.015, .28, loc=(0, -.1, zg + .3), seg=6, bevel=0)
    steel.torus(.05, .01, loc=(0, -.1, zg + .45), rot=(R90, 0, 0), seg=10, ring=4)
    mk = a.pivot('Muzzle_mg', (0, y0 - L - .21, zg), key)
    per_barrel(a, mk, 'mg', (-.1, .1))


def in_thermo(a):
    """The Nona-read 125 mm thermobaric gun on the glacis (Mount_rocket, part thermo): the hexagonal barbette and its
    bolts (static), the welded wedge turret with its bustle and hazard band, the box mantlet, the stubby tube with a
    heavy sleeve and a pepperpot brake (Thermo_barrels / Thermo_muzzles kick), the sight; Muzzle_rocket at the brake."""
    k.lathe(a.part('Gun_barbette', 'Armor'), [(.86, -.02), (.86, .36), (.8, .42)], loc=(0, -3.4, 1.96), seg=6,
            worn=(1,))
    for i in range(12):
        u = (i + .5) * TAU / 12
        a.part('Gun_barbette_bolts', 'Steel').cyl(.022, .03, loc=(math.cos(u) * .72, -3.4 + math.sin(u) * .72, 2.38),
                                                  seg=6, bevel=0)
    m = a.pivot('Mount_rocket', (0, -3.4, 2.38))
    steel = a.part('Thermo_steel', 'Steel', m)
    k.ring(steel, [(.66, -.03), (.76, -.03), (.76, .05), (.7, .07), (.66, .07)], seg=18)
    base = [(-.5, -.72), (.5, -.72), (.78, -.2), (.78, .58), (-.78, .58), (-.78, -.2)]
    roof = [(-.32, -.5), (.32, -.5), (.58, -.12), (.58, .5), (-.58, .5), (-.58, -.12)]
    k.sharp_loft(a.part('Thermo_house', 'Team', m), [[(x, y, 0.0) for x, y in base],
                                                    [(x * 1.02, y * 1.02, .26) for x, y in base],
                                                    [(x, y, .55) for x, y in roof]], chamfer=.035)
    k.block(a.part('Thermo_bustle', 'Armor', m), (.95, .5, .36), loc=(0, .82, .22), chamfer=.03)
    a.part('Thermo_hazard', 'SafetyStripe', m).box((.8, .02, .07), loc=(0, 1.075, .3), bevel=0)
    k.block(a.part('Thermo_mantlet', 'Armor', m), (.55, .3, .4), loc=(0, -.78, .3), chamfer=.04, taper=(.9, .85))
    y0, zg, L = -.92, .3, 1.35
    bar = a.part('Thermo_barrels', 'Steel', m)
    fwd(bar, [(0, -.03), (.16, -.03), (.16, .5), (.13, .56), (.12, L), (0, L)], (0, y0, zg), seg=16)
    fwd_ring(bar, [(.155, .2), (.175, .2), (.175, .28), (.155, .28)], (0, y0, zg), seg=16)
    mu = a.part('Thermo_muzzles', 'Undercarriage', m)
    fwd(mu, [(.12, L - .02), (.16, L), (.16, L + .4), (.11, L + .42), (.08, L + .42), (0, L + .4)], (0, y0, zg),
        seg=16)
    for j in range(3):
        d = L + .08 + j * .11
        for i in range(8):
            u = i * TAU / 8 + j * .4
            mu.cyl(.03, .02, loc=(math.cos(u) * .163, y0 - d, zg + math.sin(u) * .163),
                   rot=dir_rot((math.cos(u), 0, math.sin(u))), seg=6, bevel=0)
    a.pivot('Muzzle_rocket', (0, y0 - L - .44, zg), 'Mount_rocket')
    k.block(a.part('Thermo_sight', 'Armor', m), (.2, .28, .18), loc=(.32, -.25, .62), chamfer=.02)
    a.part('Glass', 'Glass', m).box((.15, .012, .09), loc=(.32, -.395, .64), bevel=0)
    in_hatch(a, (-.25, .15, .55), parent=m, rx=.24, ry=.2)
    K.soot(a, (0, -3.4 + y0 - L, 2.68), radius=.45, k=.35)
    K.tone(a, 'Mount_rocket', k=.9)
