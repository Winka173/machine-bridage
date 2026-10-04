"""Play-test 14 boss redraw R1 (lane models): the bespoke weapons and command structures of the two Icarus.

Owner (04/10, Docs/prompts/playtest14_vi.txt, last block): Icarus Mk.0's tower "looks exactly like a watchtower";
"đừng reuse gì hết ... súng railgun cũng vậy vẽ lại". Audit: Docs/models/pt14_reuse_audit.md; DECISIONS "Play-test 14
boss redraw R1 (lane models)". Nothing here is shared between the two ships (the prototype and the finished warship
each get their own guns, emitters, bay and engines):
- silver_bug (Icarus): the heavy coilguns (a bore tube through nine accelerator coil drums of falling size, the power
  bus over them, the field-shaping muzzle; capacitor banks either side of a low armoured housing on a faceted
  barbette), the beam turrets (a faceted dome with the emitter of stacked lens rings and the radiator fins), the twin
  40 mm sponson turrets (a sharp-nosed house, perforated barrel jackets, the side ammunition drums), the point-defence
  ball emitters on their low plinths.
- icarus_mk0 (the prototype): the armoured command citadel under construction (a low raked wedge, part plated, its
  frames bare where plates are missing, the armoured bridge slit with its shutters, a sensor dome under a tarp, the
  APS emitter on a test plinth), the open optical-bench laser in its fork, the gimballed test PD emitter on its
  pedestal, the external drop cradle with one pod, three tube-wall test engines with their turbopumps and turbine
  exhaust ducts.
Runtime names are the ones each node had (Mount_gun .. .005 / Muzzle_gun .., Muzzle_b1 / _b2, Pd_laser_l / _r,
Turret > Muzzle_main, Pod_bay > Muzzle_missile, Thruster_main, Mount_APS, Engine_flame ..). Metres, +Z up, -Y front,
+X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


def fwd(part, profile, loc, seg=14):
    """A turned part along -Y: profile [(radius, distance forward)] from loc."""
    k.lathe(part, profile, loc=loc, rot=K.FORWARD, seg=seg)


def aft(part, profile, loc, seg=14):
    """A turned part along +Y: profile [(radius, distance aft)] from loc."""
    k.lathe(part, profile, loc=loc, rot=K.BACKWARD, seg=seg)


def hexagon(r, n=6, rot=0.0):
    return [(math.cos(rot + i * TAU / n) * r, math.sin(rot + i * TAU / n) * r) for i in range(n)]


# ============================================================================= silver_bug (Icarus)
def sb_coilgun(a, H, i, x, y):
    """A heavy coilgun on its shoulder (Mount_gun / .001): the faceted barbette from the hull, the low armoured
    housing with the capacitor banks along both sides and their glow seams, the bore tube running through nine
    accelerator coil drums of falling size, the power bus over the drums with its feeds, the field-shaping muzzle
    ring with its three prongs (Coil_barrels* / Glow_barrels* / Coil_muzzles*, the kick parts); Muzzle_gun at the
    mouth."""
    tag = '' if i == 0 else '_001'
    zs = H.top(x, y)
    k.extrude(a.part('Coilgun_barbettes', 'MetalSheet'), hexagon(1.5, 8, math.pi / 8), .85, loc=(x, y, zs - .02),
              axis='Z', chamfer=.06, taper=.9)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, zs + .45))
    k.ring(a.part('Coilgun_ring' + tag, 'Armor', m), [(1.2, -.02), (1.3, -.02), (1.3, .08), (1.2, .08)], seg=24)
    k.sharp_loft(a.part('Coilgun_housing' + tag, 'Fuel', m), [
        [(-.75, -1.55, .05), (.75, -1.55, .05), (1.15, -.8, .05), (1.15, 1.45, .05), (.7, 1.85, .05),
         (-.7, 1.85, .05), (-1.15, 1.45, .05), (-1.15, -.8, .05)],
        [(-.55, -1.3, .78), (.55, -1.3, .78), (.92, -.6, .9), (.92, 1.3, .9), (.55, 1.62, .85), (-.55, 1.62, .85),
         (-.92, 1.3, .9), (-.92, -.6, .9)]], chamfer=.05)
    # Capacitor banks: tall slabs along both flanks, glow seams between them, the bus bars over them.
    for e in (-1, 1):
        for j in range(5):
            yy = -.75 + j * .5
            k.block(a.part('Coilgun_caps' + tag, 'Undercarriage', m), (.28, .42, .78), loc=(e * 1.27, yy, .5),
                    chamfer=.03)
            if j < 4:
                a.part('Coilgun_seams' + tag, 'Energy', m).box((.2, .05, .6), loc=(e * 1.3, yy + .25, .5), bevel=0)
        a.part('Coilgun_bus' + tag, 'Steel', m).box((.12, 2.4, .1), loc=(e * 1.2, .25, .95), bevel=0)
    k.block(a.part('Coilgun_vents' + tag, 'Undercarriage', m), (1.1, .5, .08), loc=(0, 1.2, .9), chamfer=.02)
    for j in range(4):
        a.part('Coilgun_vents' + tag, 'Steel', m).box((1.0, .04, .05), loc=(0, 1.02 + j * .12, .96), bevel=0)
    # The accelerator: bore tube, the coil drums, glow gaps, the power bus and its feeds, the muzzle.
    zg = .62
    fwd(a.part('Coil_barrels' + tag, 'Steel', m), [(.2, -.2), (.2, 1.2), (.16, 1.3), (.15, 7.4)], (0, -1.2, zg), seg=14)
    for j in range(9):
        d = 1.5 + j * .64
        r = .52 - j * .017
        fwd(a.part('Coil_barrels' + tag, 'Armor', m), [(.17, d), (r * .9, d), (r, d + .05), (r, d + .33),
                                                        (r * .9, d + .38), (.17, d + .38)], (0, -1.2, zg), seg=16)
        fwd(a.part('Glow_barrels' + tag, 'Energy', m), [(.17, d + .4), (r * .78, d + .4), (r * .78, d + .55),
                                                         (.17, d + .55)], (0, -1.2, zg), seg=14)
        a.part('Coil_barrels' + tag, 'Steel', m).limb((0, -1.2 - d - .19, zg + r - .02), (0, -1.2 - d - .19, zg + .62),
                                                      .08, .08, bevel=0)
    a.part('Coil_barrels' + tag, 'Steel', m).box((.18, 6.0, .14), loc=(0, -1.2 - 4.4, zg + .66), bevel=.02)
    a.part('Coil_barrels' + tag, 'Steel', m).box((.12, 6.0, .08), loc=(0, -1.2 - 4.4, zg - .45), bevel=0)
    for j in range(5):
        a.part('Coil_barrels' + tag, 'Steel', m).limb((0, -1.2 - 1.6 - j * 1.25, zg - .45),
                                                      (0, -1.2 - 1.6 - j * 1.25, zg - .15), .06, .06, bevel=0)
    fwd(a.part('Coil_muzzles' + tag, 'Fuel', m), [(.16, 7.35), (.36, 7.4), (.5, 7.62), (.5, 7.7), (.3, 7.72),
                                                   (.16, 7.6)], (0, -1.2, zg), seg=18)
    for j in range(3):
        u = j * TAU / 3 + R90
        a.part('Coil_muzzles' + tag, 'Armor', m).box((.08, .55, .1), loc=(math.cos(u) * .44, -1.2 - 7.85,
                                                                           zg + math.sin(u) * .44),
                                                     rot=(0, -u + R90, 0), bevel=0)
    a.pivot(K.name('Muzzle_gun', i), (0, -1.2 - 8.15, zg), key)
    K.soot(a, (x, y - 9.3, zs + .45 + zg), radius=.6, k=.3)
    K.tone(a, key, k=.9)


def sb_beam_turret(a, loc, gun_index):
    """A beam turret (Mount_gun.002 / .003): the faceted dome on its collar with the slot, the emitter of three
    stacked lens rings growing to the glowing aperture, the two radiator fins swept back, the sensor head;
    Muzzle_gun.00N at the aperture."""
    tag = f'_{gun_index:03d}'
    key = K.name('Mount_gun', gun_index)
    m = a.pivot(key, loc)
    k.lathe(a.part('Director_base' + tag, 'Armor', m), [(.78, -.3), (.78, .02), (.7, .08)], seg=16)
    k.lathe(a.part('Director_dome' + tag, 'Fuel', m), [(.7, .05), (.72, .3), (.62, .62), (.4, .85), (0, .95)], seg=10)
    a.part('Director_slot' + tag, 'Undercarriage', m).box((.36, .5, .5), loc=(0, -.52, .5), rot=(.45, 0, 0), bevel=0)
    zg = .5
    fwd(a.part('Director_tube' + tag, 'Steel', m), [(.16, .2), (.16, 1.0), (.2, 1.05)], (0, 0, zg), seg=12)
    for j, (d, r) in enumerate(((.95, .24), (1.15, .3), (1.35, .36))):
        fwd(a.part('Director_rings' + tag, 'Armor', m), [(.15, d), (r, d), (r, d + .12), (.15, d + .14)], (0, 0, zg),
            seg=14)
    a.part('Director_aperture' + tag, 'Energy', m).cyl(.3, .03, loc=(0, -1.5, zg), rot=(R90, 0, 0), seg=14, bevel=0)
    for e in (-1, 1):
        a.part('Director_fins' + tag, 'Undercarriage', m).box((.04, .9, .55), loc=(e * .62, .35, .6),
                                                              rot=(0, e * .35, 0), bevel=0)
    k.block(a.part('Director_sensor' + tag, 'Fuel', m), (.22, .3, .2), loc=(.35, -.1, .9), chamfer=.02)
    a.part('Glass', 'Glass', m).box((.16, .02, .1), loc=(.35, -.26, .92), bevel=0)
    a.pivot(K.name('Muzzle_gun', gun_index), (0, -1.53, zg), key)
    K.tone(a, key, k=.9)


def sb_twin40(a, H, gun_index, s, y):
    """A twin 40 mm turret on its flank sponson (Mount_gun.004 / .005, the crash turrets): the faceted sponson pod on
    the chine, the ring, the sharp-nosed house, the two barrels in perforated jackets with their flash hiders
    (Gun_barrels* / Gun_muzzles*, the kick parts), the ammunition drums on both cheeks, the sensor; Muzzle_gun.00N
    between the tips and Muzzle_b1 / _b2 at each."""
    w = H.w(y)
    tag = f'_{gun_index:03d}'
    a.part('Sponsons', 'MetalSheet').loft([
        [(s * (w - .4), y - 2.4, -.5), (s * (w + .9), y - 1.6, -.4), (s * (w + .9), y + 1.9, -.4),
         (s * (w - .4), y + 2.6, -.5)],
        [(s * (w - .4), y - 2.1, .55), (s * (w + 1.05), y - 1.3, .6), (s * (w + 1.05), y + 1.6, .6),
         (s * (w - .4), y + 2.3, .55)]], bevel=0)
    a.part('Sponson_tiles', 'Undercarriage').box((1.4, 3.4, .08), loc=(s * (w + .25), y + .15, -.48), bevel=0)
    key = K.name('Mount_gun', gun_index)
    m = a.pivot(key, (s * (w + .3), y, .62))
    k.ring(a.part('Gun_ring' + tag, 'Steel', m), [(.72, 0), (.8, 0), (.8, .08), (.72, .08)], seg=18)
    k.sharp_loft(a.part('Gun_house' + tag, 'Fuel', m), [
        [(0, -1.2, .08), (.55, -.6, .08), (.72, .5, .08), (.45, .9, .08), (-.45, .9, .08), (-.72, .5, .08),
         (-.55, -.6, .08)],
        [(0, -.85, .62), (.4, -.45, .66), (.55, .45, .66), (.32, .75, .62), (-.32, .75, .62), (-.55, .45, .66),
         (-.4, -.45, .66)]], chamfer=.03)
    for e in (-1, 1):
        a.part('Gun_drums' + tag, 'Undercarriage', m).cyl(.2, .55, loc=(e * .78, .15, .38), rot=(R90, 0, 0), seg=12,
                                                          bevel=.02)
        a.part('Gun_feeds' + tag, 'Steel', m).limb((e * .62, -.1, .45), (e * .25, -.55, .4), .08, .06, bevel=0)
    zg = .4
    for dx in (-.2, .2):
        fwd(a.part('Gun_barrels' + tag, 'Steel', m), [(.07, -.1), (.07, 1.9), (.06, 1.95), (.06, 2.15)],
            (dx, -.95, zg), seg=10)
        fwd(a.part('Gun_barrels' + tag, 'Armor', m), [(.105, .05), (.105, 1.0), (.08, 1.05)], (dx, -.95, zg), seg=10)
        for j in range(4):
            a.part('Gun_barrels' + tag, 'Undercarriage', m).box((.03, .1, .03),
                                                                loc=(dx + (.1 if dx > 0 else -.1), -1.15 - j * .22, zg),
                                                                bevel=0)
        fwd(a.part('Gun_muzzles' + tag, 'Armor', m), [(.05, 2.15), (.085, 2.17), (.085, 2.35), (.06, 2.37)],
            (dx, -.95, zg), seg=10)
    k.block(a.part('Gun_sight' + tag, 'Fuel', m), (.24, .3, .2), loc=(-.3, -.15, .72), chamfer=.02)
    a.part('Glass', 'Glass', m).box((.18, .02, .12), loc=(-.3, -.31, .75), bevel=0)
    mz = K.name('Muzzle_gun', gun_index)
    a.pivot(mz, (0, -3.35, zg), key)
    a.pivot(f'Muzzle_b1_gun{tag}', (-.2 if s > 0 else .2, 0, 0), mz)
    a.pivot(f'Muzzle_b2_gun{tag}', (.2 if s > 0 else -.2, 0, 0), mz)
    K.tone(a, key, k=.88)


def sb_pd(a, H, name, x, y, tag):
    """A point-defence emitter (Pd_laser_l / _r): the low faceted plinth from the hull, the collar, the ball emitter
    turning in its fork, the lens stack and the glow."""
    zs = H.top(x, y)
    p = a.pivot(name, (x, y, zs + .45))
    k.extrude(a.part('Pd_tower' + tag, 'MetalSheet', p), hexagon(.8, 6, math.pi / 6), .75, loc=(0, 0, -.42),
              axis='Z', chamfer=.05, taper=.82)
    k.ring(a.part('Pd_band' + tag, 'Team', p), [(.6, -.06), (.66, -.06), (.66, .02), (.6, .02)], seg=14)
    for e in (-1, 1):
        k.block(a.part('Pd_fork' + tag, 'Fuel', p), (.12, .4, .55), loc=(e * .45, 0, .3), chamfer=.02)
    a.part('Pd_dome' + tag, 'Fuel', p).sphere(.36, loc=(0, 0, .38), seg=14, rings=8)
    fwd(a.part('Pd_emitter' + tag, 'Steel', p), [(.12, .2), (.12, .5), (.17, .52), (.17, .62), (.13, .64)],
        (0, 0, .4), seg=10)
    a.part('Pd_glow' + tag, 'Energy', p).cyl(.11, .03, loc=(0, -.65, .4), rot=(R90, 0, 0), seg=10, bevel=0)
    K.tone(a, name, k=.88)


# ============================================================================= icarus_mk0 (the prototype)
def mk_citadel(a):
    """The command citadel under construction on the first tier's roof (z 3.0): a low wedge raked hard at the front,
    the dark inner structure, primer and bare plates fitted over most of it, the frames bare in three bays where
    plates are missing, the armoured bridge slit in the raked front with its shutters (two swung up), the roof
    hatch, a sensor dome half under a strapped tarp, the APS emitter on its test plinth (Mount_APS), work lamps and
    cable runs, a short access ladder from the tier roof."""
    z0, z1 = 3.0, 4.75
    base = [(-2.4, 7.2), (2.4, 7.2), (2.65, 8.3), (2.65, 11.9), (-2.65, 11.9), (-2.65, 8.3)]
    top = [(-1.55, 8.75), (1.55, 8.75), (1.95, 9.35), (1.95, 11.55), (-1.95, 11.55), (-1.95, 9.35)]
    core = a.part('Citadel_core', 'Undercarriage')
    k.sharp_loft(core, [[(x, y, z0) for x, y in base], [(x, y, z1) for x, y in top]], chamfer=.05)

    def on(face, u, v, lift=.035):
        """A point on the citadel's face i (0 front, 1 / 5 cheeks, 2 / 4 sides, 3 rear) at fractions u along, v up."""
        b0, b1 = Vector((*base[face], z0)), Vector((*base[(face + 1) % 6], z0))
        t0, t1 = Vector((*top[face], z1)), Vector((*top[(face + 1) % 6], z1))
        lo, hi = b0.lerp(b1, u), t0.lerp(t1, u)
        p = lo.lerp(hi, v)
        n = (b1 - b0).cross(hi - lo).normalized()
        if n.dot(p - Vector((0, 9.6, 3.8))) < 0:
            n = -n
        return p + n * lift, n

    # Plates: (face, u0, u1, v0, v1, material); the gaps left open show the frames.
    plates = [(0, .02, .3, .05, .55, 'Crate'), (0, .7, .98, .05, .55, 'Crate'), (0, .02, .98, .78, .97, 'MetalSheet'),
              (1, .05, .95, .05, .95, 'Crate'), (5, .05, .95, .05, .95, 'MetalSheet'),
              (2, .02, .3, .05, .95, 'Crate'), (2, .33, .6, .05, .95, 'MetalSheet'),
              (4, .4, .68, .05, .95, 'Crate'), (4, .71, .98, .05, .95, 'MetalSheet'),
              (3, .02, .45, .05, .95, 'Crate')]
    for face, u0, u1, v0, v1, mat in plates:
        q = [on(face, u, v)[0] for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
        n = on(face, (u0 + u1) / 2, .5)[1]
        k.sharp_loft(a.part(f'Citadel_plates_{mat.lower()}', mat), [q, [tuple(p + n * .05) for p in q]], chamfer=.012)
    # Bare frames in the gaps (the right side's front half, the left side's rear, the rear's right half).
    ribs = a.part('Citadel_frames', 'Steel')
    for face, us in ((4, (.06, .14, .22, .3, .38)), (2, (.66, .74, .82, .9)), (3, (.55, .67, .79, .91))):
        for u in us:
            p0, n = on(face, u, 0.0, .06)
            p1, _ = on(face, u, 1.0, .06)
            ribs.limb(tuple(p0), tuple(p1), .1, .1, bevel=0)
        for v in (.35, .7):
            p0, _ = on(face, us[0], v, .06)
            p1, _ = on(face, us[-1], v, .06)
            ribs.limb(tuple(p0), tuple(p1), .07, .07, bevel=0)
    # The armoured bridge slit across the raked front, its shutters (two swung up on their arms).
    p, n = on(0, .5, .66, .06)
    tilt = math.atan2(top[0][1] - base[0][1], z1 - z0)
    a.part('Bridge_windows', 'Lamp').box((3.0, .05, .22), loc=tuple(p), rot=(-tilt, 0, 0), bevel=0)
    for j in range(6):
        u = .2 + j * .12
        q, _ = on(0, u, .66, .1)
        open_ = j in (1, 4)
        a.part('Bridge_shutters', 'Armor').box((.42, .04, .26), loc=tuple(q + Vector((0, -.12, .18)) if open_ else q),
                                               rot=(-tilt + (.9 if open_ else 0), 0, 0), bevel=0)
    # Roof: the plate, the hatch, the sensor dome half under its tarp, the APS on its plinth, lamps, cables.
    k.extrude(a.part('Bridge', 'Concrete'), [(x * .97, y + (.05 if y < 9 else -.03)) for x, y in top], .08,
              loc=(0, 0, z1 + .04), axis='Z', chamfer=.02)
    k.block(a.part('Hatches', 'Armor'), (.7, .6, .08), loc=(-1.0, 10.9, z1 + .12), chamfer=.02)
    k.lathe(a.part('Sensor_dome', 'PlasterWhite'), [(.85, 0), (.88, .2), (.75, .55), (.45, .8), (0, .88)],
            loc=(.6, 10.0, z1 + .08), seg=18)
    a.part('Tarps', 'Canvas').loft([[(-.35, 9.1, z1 + .1), (1.55, 9.1, z1 + .1), (1.55, 9.1, z1 + .2), (-.35, 9.1, z1 + .2)],
                                    [(-.4, 9.75, z1 + .95), (1.6, 9.75, z1 + .98), (1.6, 9.75, z1 + 1.06),
                                     (-.4, 9.75, z1 + 1.03)],
                                    [(-.3, 10.2, z1 + .88), (1.5, 10.2, z1 + .9), (1.5, 10.2, z1 + .98),
                                     (-.3, 10.2, z1 + .96)]], bevel=0)
    for e in (-.05, 1.25):
        a.part('Tarp_straps', 'Hazard').tube([(e, 9.05, z1 + .1), (e, 9.7, z1 + 1.02), (e, 10.25, z1 + .92),
                                              (e, 10.85, z1 + .3)], .03, seg=4)
    k.extrude(a.part('Aps_plinth', 'Crate'), hexagon(.4, 6), .35, loc=(-1.1, 9.4, z1 + .26), axis='Z', chamfer=.03)
    m = a.pivot('Mount_APS', (-1.1, 9.4, z1 + .45))
    k.lathe(a.part('Aps_emitter', 'Armor', m), [(.3, 0), (.3, .12), (.18, .24), (0, .27)], seg=12)
    a.part('Aps_glow', 'Energy', m).sphere(.1, loc=(0, -.06, .25), seg=8, rings=4)
    a.part('Cable_runs', 'Charred').tube([(-1.1, 9.8, z1 + .1), (-1.9, 10.6, z1 + .1), (-2.3, 11.6, z1 - .4),
                                          (-2.5, 11.9, z0 + .1)], .05, seg=4)
    for x in (2.2, -2.2):
        K.lamp(a, (x, 8.9, z1 - .15), facing=(math.copysign(.5, x), -1, -.3), r=.1)
    K.ladder(a.part('Ladders', 'Hazard'), (2.72, 10.6, z0), (2.0, 10.6, z1), width=.45)
    a.part('Team_band', 'Hazard').box((3.0, .5, .02), loc=(0, 11.3, z1 + .085), bevel=0)


def mk_laser(a, H):
    """The prototype's ventral laser (Turret > Muzzle_main): two splayed pylons and the mounting plate under the
    belly, the fork turning on its collar, the trunnion housing with the coolant manifold, the open optical bench
    (four longerons and their frames) carrying four lens stages to the glowing output lens (Main_cannon*, the
    recoil parts), the capacitor pack hung behind the trunnion."""
    zb = H.bot(0, -7.0)
    for e in (-1, 1):
        a.part('Laser_pylons', 'Steel').limb((e * 1.0, -6.0, zb + .15), (e * .45, -6.9, -2.05), .18, .18, bevel=0)
        a.part('Laser_pylons', 'Steel').limb((e * 1.0, -8.0, zb + .15), (e * .45, -7.1, -2.05), .18, .18, bevel=0)
    k.block(a.part('Laser_blister', 'Crate'), (2.3, 2.6, .25), loc=(0, -7.0, zb - .02), chamfer=.04)
    t = a.pivot('Turret', (0, -7.0, -2.8))
    k.lathe(a.part('Turret_collar', 'Steel', t), [(.62, .55), (.62, .8), (.5, .86)], seg=16)
    for e in (-1, 1):
        a.part('Turret_ball', 'Crate', t).limb((e * .6, 0, .6), (e * .6, 0, -.2), .14, .5, bevel=0)
    k.block(a.part('Turret_band', 'Armor', t), (1.05, 1.1, .7), loc=(0, .1, -.12), chamfer=.06, ends=(True, True))
    a.part('Turret_stripe', 'Hazard', t).box((1.07, .1, .72), loc=(0, -.42, -.12), bevel=0)
    for e in (-1, 1):
        a.part('Main_cannon_pipes', 'Pipe', t).tube([(e * .4, .5, .2), (e * .55, .1, .3), (e * .3, -.5, .25),
                                                     (e * .26, -1.4, .18)], .05, seg=6)
    # The bench: four longerons, square frames, the lens stages.
    zc = -.12
    for ex in (-1, 1):
        for ez in (-1, 1):
            a.part('Main_cannon', 'Steel', t).limb((ex * .26, -.45, zc + ez * .26), (ex * .26, -3.55, zc + ez * .26),
                                                   .07, .07, bevel=0)
    for j in range(5):
        yy = -.6 - j * .72
        for ex, ez, w, h in ((0, 1, .6, .06), (0, -1, .6, .06), (1, 0, .06, .6), (-1, 0, .06, .6)):
            a.part('Main_cannon', 'Steel', t).box((w, .06, h), loc=(ex * .26, yy, zc + ez * .26), bevel=0)
    for j, r in enumerate((.17, .2, .22, .25)):
        yy = -.95 - j * .72
        fwd(a.part('Main_cannon_rings', 'Armor', t), [(r * .6, 0), (r, 0), (r, .14), (r * .6, .14)], (0, yy, zc),
            seg=14)
        a.part('Glass', 'Glass', t).cyl(r * .62, .02, loc=(0, yy - .07, zc), rot=(R90, 0, 0), seg=12, bevel=0)
    fwd(a.part('Main_cannon_rings', 'Armor', t), [(.2, 0), (.34, .05), (.34, .3), (.28, .35)], (0, -3.5, zc), seg=16)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.27, .04, loc=(0, -3.87, zc), rot=(R90, 0, 0), seg=16, bevel=0)
    a.pivot('Muzzle_main', (0, -3.92, zc), 'Turret')
    # The capacitor pack behind, strapped, its cables to the housing.
    k.block(a.part('Laser_caps', 'Undercarriage', t), (.9, .8, .55), loc=(0, .95, -.15), chamfer=.04)
    for e in (-1, 1):
        a.part('Laser_cap_straps', 'Hazard', t).box((.95, .06, .58), loc=(0, .95 + e * .25, -.15), bevel=0)
    K.tone(a, 'Turret', k=.88)


def mk_pd(a, H, name, x, y, z):
    """The prototype's PD test emitter (Pd_laser_l, its pivot at the finished ship's height z): the octagonal
    pedestal from the hull, the gimbal ring, the emitter can with its heat-sink fin stack and lens, the test
    cable."""
    zs = H.top(x, y)
    p = a.pivot(name, (x, y, z))
    zl = zs - z
    k.extrude(a.part('Pd_tower' + '', 'Crate', p), hexagon(.5, 8, math.pi / 8), -zl + .1, loc=(0, 0, (zl - .1) / 2),
              axis='Z', chamfer=.04, taper=.85)
    k.ring(a.part('Pd_band', 'Hazard', p), [(.42, -.02), (.5, -.02), (.5, .06), (.42, .06)], seg=12)
    a.part('Pd_dome', 'Steel', p).torus(.4, .05, loc=(0, 0, .35), rot=(0, R90, 0), seg=16, ring=5)
    for e in (-1, 1):
        a.part('Pd_dome', 'Steel', p).limb((e * .4, 0, .05), (e * .4, 0, .35), .08, .08, bevel=0)
    a.part('Pd_emitter', 'MetalSheet', p).cyl(.24, .7, loc=(0, -.1, .35), rot=(R90, 0, 0), seg=12, bevel=.02)
    for j in range(6):
        a.part('Pd_fins', 'Undercarriage', p).box((.62, .03, .62), loc=(0, .1 + j * .07, .35), bevel=0)
    a.part('Pd_emitter', 'Steel', p).cyl(.14, .12, loc=(0, -.5, .35), rot=(R90, 0, 0), seg=10, bevel=0)
    a.part('Pd_glow', 'Energy', p).cyl(.1, .02, loc=(0, -.57, .35), rot=(R90, 0, 0), seg=10, bevel=0)
    a.part('Pd_cables', 'Charred', p).tube([(.2, .45, .3), (.45, .6, 0), (.55, .55, zl + .05)], .04, seg=4)


def mk_pod_rig(a, H):
    """The prototype's external drop cradle (Pod_bay; no bay in the hull yet): four struts down from the belly to
    two rails, one pod held between them by its clamps and the release arms, the umbilical, hazard chevrons on the
    rails; Muzzle_missile under the pod."""
    y = 4.0
    zb = H.bot(0, y)
    p = a.pivot('Pod_bay', (0, y, -2.6))
    zl = zb - (-2.6)
    for e in (-1, 1):
        for dy in (-1.4, 1.4):
            a.part('Bay_struts', 'Steel', p).limb((e * .9, dy, zl + .1), (e * .75, dy * .85, .15), .12, .12, bevel=0)
        a.part('Bay_rails', 'Crate', p).box((.16, 3.4, .22), loc=(e * .75, 0, .1), bevel=.02)
        for j in range(4):
            a.part('Bay_chevrons', 'Hazard', p).box((.17, .3, .02), loc=(e * .75, -1.2 + j * .8, .22),
                                                    rot=(0, 0, .6 * e), bevel=0)
        for dy in (-.6, .6):
            a.part('Bay_clamps', 'Steel', p).limb((e * .75, dy, .05), (e * .38, dy, -.35), .08, .1, bevel=0)
        a.part('Bay_rams', 'Steel', p).limb((e * .75, 1.3, .0), (e * .5, .9, -.25), .05, .05, bevel=0)
    k.lathe(a.part('Bay_pods', 'Team', p), [(0, -1.25), (.3, -1.15), (.5, -.75), (.55, -.25), (.5, .02), (.3, .12),
                                            (0, .14)], loc=(0, 0, -.25), seg=14)
    a.part('Bay_pod_glow', 'Energy', p).torus(.53, .035, loc=(0, 0, -.5), seg=14, ring=4)
    for u in range(3):
        v = u * TAU / 3
        a.part('Bay_pod_fins', 'Armor', p).box((.04, .32, .3), loc=(math.cos(v) * .42, math.sin(v) * .42, -1.1),
                                               rot=(0, 0, v + R90), bevel=0)
    a.part('Bay_umbilical', 'Charred', p).tube([(0, .4, -.05), (.3, .9, .3), (.4, 1.2, zl)], .05, seg=4)
    a.pivot('Muzzle_missile', (0, 0, -1.6), 'Pod_bay')
    K.tone(a, 'Pod_bay', k=.88)


def mk_engines(a):
    """Three tube-wall test engines on the open thrust frame (Thruster_main): each bell with its coolant tubes
    running down it and the manifold band at the lip, the gimbal block, the turbopump beside it with the turbine
    exhaust duct and its small nozzle, the propellant lines; Engine_flame on each exit plane."""
    t = a.pivot('Thruster_main', (0, 15.5, .6))
    for s in (-1, 1):
        a.part('Thrust_frame', 'Steel', t).limb((s * 3.6, -2.9, 1.2), (s * 3.6, -.6, -.4), .14, .14, bevel=0)
        a.part('Thrust_frame', 'Steel', t).limb((s * 3.6, -2.9, -1.6), (s * 3.6, -.6, -.4), .14, .14, bevel=0)
        a.part('Thrust_frame', 'Steel', t).limb((s * 3.6, -.6, -.4), (0, -.6, -.4), .12, .12, bevel=0)
    k.block(a.part('Engine_block', 'Crate', t), (8.4, .5, 2.8), loc=(0, -2.85, -.1), chamfer=.08)
    feed = a.part('Feed_lines', 'Pipe', t)
    for z in (1.0, -1.15):
        feed.tube([(-3.2, -1.6, z), (3.2, -1.6, z)], .1, seg=8)
    for i, (x, z) in enumerate(((-2.5, -.2), (0, .2), (2.5, -.2))):
        L, rt, re = 2.4, .4, 1.05
        k.block(a.part('Engine_gimbals', 'Armor', t), (.7, .6, .7), loc=(x, -2.25, z - .35), chamfer=.05)
        aft(a.part('Engine_chambers', 'Steel', t), [(.55, 0), (.55, .45), (rt, .75), (rt, .85)], (x, -1.95, z), seg=18)
        prof = [(rt + (re - rt) * (1 - (1 - f) ** 1.8), .85 + L * f) for f in (0, .2, .4, .6, .8, 1.0)]
        inner = [(r - .045, d) for r, d in reversed(prof)]
        k.lathe(a.part('Engine_bells', 'MetalSheet', t), prof + inner, loc=(x, -1.95, z), rot=K.BACKWARD, seg=28,
                caps=(False, False))
        for j in range(20):
            u = j * TAU / 20
            pts = [(x + math.cos(u) * (r + .02), -1.95 + d, z + math.sin(u) * (r + .02)) for r, d in prof[:-1]]
            a.part('Engine_tubes', 'Pipe', t).tube(pts, .022, seg=3)
        k.ring(a.part('Engine_bands', 'Armor', t), [(re + .01, -.06), (re + .07, -.06), (re + .07, .04),
                                                     (re + .01, .04)], loc=(x, -1.95 + .85 + L - .05, z),
               rot=K.BACKWARD, seg=28)
        # The turbopump beside the chamber, its turbine exhaust duct out along the bell.
        sx = 1 if x <= 0 else -1
        a.part('Engine_pumps', 'Undercarriage', t).cyl(.26, .7, loc=(x + sx * .75, -1.85, z + .45), rot=(R90, 0, 0),
                                                       seg=12, bevel=.03)
        a.part('Engine_ducts', 'Steel', t).tube([(x + sx * .75, -1.5, z + .45), (x + sx * .7, -.8, z + .95),
                                                 (x + sx * .6, .15, z + 1.25)], .1, seg=8)
        aft(a.part('Engine_ducts', 'Steel', t), [(.1, 0), (.16, .25), (.16, .3)], (x + sx * .6, .1, z + 1.25), seg=10)
        a.part('Engine_glow', 'LavaGlow', t).cyl(rt * 1.05, .03, loc=(x, -1.95 + 1.1, z), rot=(R90, 0, 0), seg=14,
                                                 bevel=0)
        ex = (x, 15.5 + -1.95 + .85 + L, z + .6)
        K.engine_flame(a, i, (x, -1.95 + .85 + L + .01, z), re, parent='Thruster_main')
        K.soot(a, (x, ex[1] - L * .4, z + 1.2), radius=re * 1.1, k=.35)
    K.tone(a, 'Thruster_main', k=.88)
