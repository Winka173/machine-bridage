"""Play-test 14 wave R4 (lane models): Hyperion redrawn from scratch as a heavy space cruiser, and its two mini-boss
variants, Theia (an escort carrier with drone bays) and Coeus (a gunship / artillery cruiser), each its own model.

Owner (04/10, Docs/prompts/playtest14_vi.txt, block "Bổ sung 04/10 sau khi thử lane H"): "hyperion nên vẽ lại từ đầu,
theo mẫu cruiser của starcraft, thêm 2 miniboss là biến thể của nó, budget tam giác cao như các tàu boss khác". The
read is the heavy capital cruiser of that genre (a long armoured hammerhead prow, a stepped superstructure, a broad
engine block, gun batteries under the hull, one huge forward main weapon), drawn as an original design: no copied
logos, marks or panels. DECISIONS "Play-test 14 wave R4 (lane models)".

Hyperion (67.2 m, the def's modelSize length; +-Y from -33.6 at the prow to +33.6 at the nozzles):
- `Turret` (main_laser, the sun beam's part): the chin projector slung under the hammerhead's tip, a drum turret with
  gimbal cheeks and the projector barrel (`Main_cannon`: focusing rings, conduits, the crown) with its lens
  (`Main_cannon_lens`) and `Muzzle_main` level with the prow; it hangs below the hull so it turns all round.
- `Mount_gun` / `.001`: twin-rail coilgun turrets on the hammerhead's shoulders (Coil_barrels* / Coil_muzzles*).
- `Mount_gun.002` / `.003`: the ventral laser batteries under the midships (Las_barrels* / Las_muzzles*), visible now
  (the def's hiddenNodes go: the two mounts fire, so their rounds leave from drawn emitters).
- `Pd_laser_l` / `_r` > `Mount_mg` / `.001` > `Muzzle_mg` / `.001`: point-defence turrets on the flank sponsons.
- `Thruster_main` (main_engine): the engine block's five bells with `Engine_flame` .. `.004`.
- `Thruster_fl` / `_fr`: RCS pods on the hammerhead's cheeks; `Thruster_rl` / `_rr`: the outboard engine nacelles
  (`Engine_flame.005` / `.006`, so a broken nacelle's flame goes out).
- `Pod_bay` > `Muzzle_missile`: the ventral drop bay under the engine block with a pod in its cradle.
- `Mount_APS` on the sensor mast.

Theia (40.3 m): own hull (a wedge prow with a launch mouth, two flank hangar pods with drones on their rails, a low
island aft, three bells): `Turret` (a dorsal dome laser turret, main_laser), `Pod_bay` > `Muzzle_missile` (the ventral
drone and pod bay: the drone swarm leaves from it), `Pd_laser_l` / `_r` on the hangar pods, `Thruster_main`,
`Mount_APS`.
Coeus (40.3 m): own hull (a slab-sided armoured gunship, a raised dorsal barbette, sponson casemates, a spotting mast,
twin outboard engines): `Turret` (the coil artillery turret, main_laser's node: its main weapon is the heavy coilgun),
`Mount_gun` / `.001` (ventral twin laser batteries), `Thruster_main`, `Thruster_rl` / `_rr` (the outboard engines).

Every function draws for one ship only, except the geometry primitives at the top (sections, loft, panel grid,
window strips). Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau
AFT = (-R90, 0, 0)       # local +Z -> +Y (the back)


# ============================================================================= geometry primitives (all three ships)
def sec(y, hw, z0, z1, ct, cb, bul=0.0, zm=None):
    """A ten-point hull section at y: flat top and keel, chamfered shoulders and bilges, a belt `bul` proud at zm."""
    zm = (z0 + z1) / 2 if zm is None else zm
    bul = bul if abs(bul) > .02 else .02       # never three points in a line (the end caps' triangulation)
    return [(hw - ct, y, z1), (hw, y, z1 - ct), (hw + bul, y, zm), (hw, y, z0 + cb), (hw - cb, y, z0),
            (-(hw - cb), y, z0), (-hw, y, z0 + cb), (-hw - bul, y, zm), (-hw, y, z1 - ct), (-(hw - ct), y, z1)]


def interp(table, y):
    """The key row of `table` [(y, hw, z0, z1, ct, cb, bul, zm)] at y (linear between keys, clamped)."""
    if y <= table[0][0]:
        return table[0]
    for r0, r1 in zip(table, table[1:]):
        if r0[0] <= y <= r1[0]:
            f = (y - r0[0]) / max(1e-6, r1[0] - r0[0])
            return tuple(a + (b - a) * f for a, b in zip(r0, r1))
    return table[-1]


def stations(table, step):
    """The key rows plus rows every `step` m between them (so the panel insets make a plate grid)."""
    out = []
    for r0, r1 in zip(table, table[1:]):
        n = max(1, int(round((r1[0] - r0[0]) / step)))
        for i in range(n):
            f = i / n
            out.append(tuple(a + (b - a) * f for a, b in zip(r0, r1)))
    out.append(table[-1])
    return out


def loft(part, table, step=2.4, chamfer=.14, inset=(.16, -.035), sel=None, dx=0.0):
    """The hull lofted through `table` (its centreline at x = dx), every face big enough given a recessed plate
    seam."""
    k.sharp_loft(part, [[(x + dx, y, z) for x, y, z in sec(*row)] for row in stations(table, step)], chamfer=chamfer)
    if inset:
        k.inset(part, sel or (lambda c, n, f: True), width=inset[0], depth=inset[1])
    return part


def windows(a, name, x, y0, y1, z, pitch, normal_x, h=.22, w=.5, mat='Lamp', parent=None):
    """A row of lit windows along y on a wall facing +-X (normal_x)."""
    p = a.part(name, mat, parent)
    n = max(1, int((y1 - y0) / pitch))
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        p.box((.04, w, h), loc=(x + normal_x * .01, y, z), bevel=0)


def band(part, pts, w, t):
    """A flat strip along the polyline pts (x, y, z), `w` wide in z, `t` thick: trims and seams."""
    for p0, p1 in zip(pts, pts[1:]):
        part.limb(p0, p1, t, w, bevel=0)


# ============================================================================= Hyperion
HP = [  # y, hw, z0, z1, ct, cb, bul, zm
    (-28.6, 8.6, 6.8, 13.6, 1.5, 1.7, .3, 10.2),
    (-27.0, 11.2, 5.7, 14.6, 2.1, 2.0, .6, 10.1),
    (-21.4, 11.4, 5.7, 14.7, 2.2, 2.1, .65, 10.1),
    (-19.2, 9.6, 6.3, 14.2, 2.0, 1.9, .45, 10.2),
    (-17.0, 6.6, 7.0, 13.4, 1.6, 1.6, .25, 10.2),
    (-8.0, 6.7, 6.9, 13.5, 1.6, 1.6, .3, 10.1),
    (0.0, 7.8, 6.5, 13.7, 1.8, 1.8, .5, 10.0),
    (8.0, 8.8, 6.0, 14.0, 2.0, 2.0, .55, 9.9),
    (11.4, 12.0, 5.0, 15.0, 2.4, 2.3, .6, 9.9),
    (29.6, 12.4, 5.0, 15.1, 2.4, 2.3, .6, 9.9),
    (31.6, 11.0, 5.6, 14.4, 2.4, 2.2, .3, 9.9),
]
HP_PRONG = [  # each of the two forward prongs either side of the projector's notch (centred at x = +-HP_PRONG_X)
    (-33.5, 2.0, 8.4, 12.0, .8, 1.0, 0, 10.2),
    (-32.6, 3.4, 7.2, 13.5, 1.2, 1.4, .2, 10.2),
    (-29.6, 3.9, 6.3, 14.3, 1.4, 1.6, .3, 10.1),
    (-26.4, 3.9, 6.0, 14.5, 1.4, 1.6, .3, 10.1),
]
HP_PRONG_X = 7.6
HP_SPINE = [  # the raised brow behind the notch running back as the dorsal spine to the engine block
    (-28.4, 2.6, 13.0, 14.8, .8, .05, 0, 13.9),
    (-27.4, 4.4, 13.0, 16.2, 1.3, .05, 0, 14.6),
    (-21.6, 4.6, 13.0, 16.2, 1.4, .05, 0, 14.6),
    (-17.6, 4.0, 12.6, 15.8, 1.3, .05, 0, 14.2),
    (-13.0, 5.0, 12.6, 15.3, 1.0, .05, .15, 14.0),
    (10.5, 5.6, 12.6, 15.6, 1.0, .05, .15, 14.1),
    (28.6, 4.4, 14.4, 15.8, .9, .05, 0, 15.1),
    (30.4, 3.0, 14.4, 15.2, .6, .05, 0, 14.8),
]
HP_SP = [  # the flank sponsons (gun galleries) either side of the neck and midships
    (-15.8, 6.2, 8.6, 11.2, .7, .8, 0, 10.0),
    (-14.2, 8.8, 8.0, 12.0, .8, 1.0, .15, 10.0),
    (5.6, 9.4, 7.6, 12.2, .8, 1.0, .2, 9.9),
    (9.8, 7.2, 8.4, 11.4, .7, .8, 0, 9.9),
]
HP_TURRET = (0, -25.4, 5.62)          # the chin projector's pivot (under the hammerhead's keel)
HP_COIL = [(7.3, -22.6), (-7.3, -22.6)]
HP_PD = [(8.2, -5.4), (-8.2, -5.4)]
HP_VLAS = [(3.75, -3.0), (-3.75, -3.0)]
HP_POD = (0, 15.2, 5.0)
HP_MAIN = (0, 31.7, 9.9)


def _hp_hull(a):
    """The hammerhead prow, the neck, the midships and the engine block in one plated loft; the raised brow and
    dorsal spine; the flank sponsons; the keel; the cheek slabs and ram plates on the hammerhead."""
    loft(a.part('Hull', 'Team'), HP, step=2.3)
    loft(a.part('Hull_spine', 'Armor'), HP_SPINE, step=2.2, inset=(.13, -.03))
    # The forked prow: two armoured prongs either side of the notch the sun-beam projector fires along.
    pr = a.part('Hull_prongs', 'Team')
    for s in (-1, 1):
        rows = [sec(*r) for r in stations(HP_PRONG, 1.6)]
        k.sharp_loft(pr, [[(x + s * HP_PRONG_X, y, z) for x, y, z in ring] for ring in rows], chamfer=.14)
    k.inset(pr, lambda c, n, f: True, width=.15, depth=-.035)
    # The notch: glowing focusing strips down the prongs' inner faces and on its back wall.
    glow = a.part('Prow_slits', 'Energy')
    for s in (-1, 1):
        for z in (8.6, 10.2, 11.8):
            glow.box((.06, 5.4, .12), loc=(s * (HP_PRONG_X - 3.9 - .32), -30.2, z), bevel=0)
    for z in (8.8, 10.4, 12.0):
        glow.box((6.0, .06, .12), loc=(0, -28.64, z), bevel=0)
    loft(a.part('Hull_sponsons', 'Team'), HP_SP, step=2.0, inset=(.12, -.03))
    # Keel: a long ventral spine with its own plates, ending in a raked fin under the engine block.
    loft(a.part('Hull_keel', 'Armor'), [(-17.0, .6, 6.3, 7.4, .3, .3, 0, 6.8), (-15.6, 1.6, 6.0, 7.4, .4, .4, 0, 6.6),
                                       (9.0, 1.6, 5.6, 6.6, .4, .4, 0, 6.1), (10.6, .7, 5.2, 6.0, .3, .3, 0, 5.6)],
         step=2.6, chamfer=.08, inset=(.1, -.02))
    ar = a.part('Armour_plates', 'Armor')
    tr = a.part('Hull_trim', 'Undercarriage')
    for s in (-1, 1):
        # Cheek slab: a thick plate on the hammerhead's flank, raked at the front, set in from both ends.
        ch = a.part('Hull_cheeks', 'Team')
        k.sharp_loft(ch, [[(s * 11.8, -29.6, 7.0), (s * 11.8, -29.6, 13.2), (s * 12.3, -29.0, 12.9),
                           (s * 12.3, -29.0, 7.3)],
                          [(s * 12.0, -22.2, 6.6), (s * 12.0, -22.2, 13.4), (s * 12.45, -22.6, 13.1),
                           (s * 12.45, -22.6, 6.9)]], chamfer=.06)
        k.inset(ch, lambda c, n, f: abs(n.x) > .8, width=.12, depth=-.03)
        # The brow's armour strips (where the brow meets the shoulders) and the shoulder plates.
        band(ar, [(s * 4.62, -32.0, 14.55), (s * 4.82, -21.6, 14.9), (s * 4.2, -17.6, 14.5), (s * 5.2, -13.0, 14.0)],
             .5, .14)
        k.block(ar, (2.4, 7.6, .2), loc=(s * 10.0, -26.2, 14.25), rot=(0, s * -.5, 0), chamfer=.05)
        # Ram plates: stacked wedges on the face either side of the centre.
        for j, z in enumerate((8.9, 10.2, 11.5)):
            k.block(ar, (2.6 - j * .3, .4, 1.05), loc=(s * HP_PRONG_X, -33.35 + j * .12, z), chamfer=.08,
                    taper=(.9, .7))
        # Armour ridge along each prong's top.
        k.sharp_loft(ar, [[(s * HP_PRONG_X + 1.8, -32.4, 13.4), (s * HP_PRONG_X, -32.4, 13.9),
                           (s * HP_PRONG_X - 1.8, -32.4, 13.4), (s * HP_PRONG_X, -32.4, 13.35)],
                          [(s * HP_PRONG_X + 2.4, -27.0, 14.45), (s * HP_PRONG_X, -27.0, 15.2),
                           (s * HP_PRONG_X - 2.4, -27.0, 14.45), (s * HP_PRONG_X, -27.0, 14.4)],
                          [(s * HP_PRONG_X + 2.4, -24.2, 14.65), (s * HP_PRONG_X, -24.2, 15.0),
                           (s * HP_PRONG_X - 2.4, -24.2, 14.65), (s * HP_PRONG_X, -24.2, 14.6)]], chamfer=.06)
        # The prongs' observation slits.
        a.part('Windows', 'Lamp').box((2.4, .06, .2), loc=(s * HP_PRONG_X, -33.42, 12.45), bevel=0)
    # The brow's face over the notch: a raked armour shield with its sensor slit.
    k.block(ar, (4.6, .8, 2.2), loc=(0, -28.5, 14.0), rot=(.4, 0, 0), chamfer=.08, taper=(.8, 1))
    a.part('Prow_slits', 'Energy').box((2.8, .06, .14), loc=(0, -28.88, 14.25), rot=(.4, 0, 0), bevel=0)
    # Dark seams where the hammerhead meets the neck and the engine block begins, the belt line.
    for y in (-21.5, -17.1, 11.3, 29.5):
        r = interp(HP, y)
        hw, z0, z1, ct, cb, bul, zm = r[1:]
        for s in (-1, 1):
            tr.box((.3, .3, z1 - z0 - ct - cb), loc=(s * (hw + bul + .02), y, (z0 + z1) / 2), bevel=0)
    for s in (-1, 1):
        band(tr, [(s * (r[1] + r[6] + .05), r[0], r[7]) for r in stations(HP, 3.0)][1:-1], .22, .1)


def _hp_superstructure(a):
    """The stepped superstructure on the spine: three tiers rising aft to the bridge (raked faces, plate grids, lit
    windows), the bridge glazing, the swept radiator fins, the sensor mast, dome and dishes, Mount_APS on top."""
    loft(a.part('Superstructure', 'Team'), [(-5.0, 3.8, 15.0, 15.6, .4, .05, 0, 15.3),
                                            (-2.6, 5.2, 15.0, 17.4, .8, .05, 0, 16.0),
                                            (13.8, 5.0, 15.0, 17.4, .8, .05, 0, 16.0),
                                            (16.2, 3.8, 15.0, 16.0, .6, .05, 0, 15.5)], step=2.2, inset=(.12, -.03))
    loft(a.part('Superstructure_t2', 'Team'), [(1.2, 3.0, 17.2, 17.6, .3, .05, 0, 17.4),
                                               (2.8, 4.0, 17.2, 19.0, .6, .05, 0, 17.9),
                                               (12.6, 3.7, 17.2, 19.0, .6, .05, 0, 17.9),
                                               (14.4, 2.8, 17.0, 17.9, .4, .05, 0, 17.4)], step=2.0, inset=(.1, -.025))
    loft(a.part('Bridge', 'Team'), [(3.0, 2.0, 18.7, 19.0, .25, .05, 0, 18.9), (4.4, 3.0, 18.7, 20.4, .45, .05, 0, 19.5),
                                     (11.0, 2.8, 18.7, 20.4, .45, .05, 0, 19.5), (12.2, 2.2, 18.7, 19.6, .35, .05, 0, 19.2)],
         step=1.6, inset=(.08, -.02))
    gl = a.part('Glass', 'Glass')
    # The bridge glazing: a band across the raked face and wrapping round the front corners.
    gl.limb((2.35, 3.62, 19.6), (-2.35, 3.62, 19.6), .55, .07, bevel=0)
    for s in (-1, 1):
        gl.limb((s * 2.5, 3.75, 19.65), (s * 3.02, 5.2, 19.85), .45, .06, bevel=0)
    for x in (-1.6, -.55, .55, 1.6):
        a.part('Bridge_mullions', 'Undercarriage').box((.08, .12, .6), loc=(x, 3.56, 19.6), rot=(-.78, 0, 0),
                                                         bevel=0)
    for s in (-1, 1):
        windows(a, 'Windows', s * 5.05, -1.8, 13.0, 16.35, 1.1, s, h=.2, w=.55)
        windows(a, 'Windows', s * 3.95, 3.4, 12.0, 18.1, .95, s, h=.18, w=.45)
        windows(a, 'Windows', s * 2.95, 5.2, 10.4, 19.85, .7, s, h=.15, w=.35)
    # The swept radiator fins over the tower's back, plates and glowing heat slots.
    fin = a.part('Fins', 'Team')
    hot = a.part('Fin_glow', 'TeamGlow')
    for s in (-1, 1):
        k.extrude(fin, [(11.5, 15.4), (18.8, 15.4), (18.8, 16.2), (16.8, 21.0), (15.4, 21.5), (14.2, 21.3)], .36,
                  loc=(s * 3.4, 0, 0), axis='X', chamfer=.06)
        k.inset(fin, lambda c, n, f: abs(n.x) > .9, width=.1, depth=-.02)
        for j in range(4):
            hot.box((.05, .45, .8), loc=(s * (3.4 + .19), 14.6 + j * .9, 17.9 + j * .62), rot=(-.45, 0, 0), bevel=0)
        k.block(a.part('Fin_caps', 'Armor'), (.52, 2.4, .18), loc=(s * 3.4, 15.4, 21.4), rot=(.25, 0, 0), chamfer=.04)
    # Sensor mast on the bridge roof, a dome behind it, two dishes, whip antennas, Mount_APS on the mast's crown.
    ms = a.part('Masts', 'Armor')
    k.sharp_loft(ms, [[(.7, 6.6, 20.3), (-.7, 6.6, 20.3), (-.7, 8.8, 20.3), (.7, 8.8, 20.3)],
                      [(.35, 7.2, 21.5), (-.35, 7.2, 21.5), (-.35, 8.2, 21.5), (.35, 8.2, 21.5)]], chamfer=.05)
    k.lathe(a.part('Sensor_dome', 'PlasterWhite'), [(1.0, 0), (1.02, .22), (.86, .62), (.5, .9), (0, 1.0)],
            loc=(0, 10.0, 20.35), seg=20)
    k.lathe(a.part('Dishes', 'Steel'), [(.0, 0), (.85, .15), (.9, .19), (.0, .1)], loc=(2.0, 5.6, 20.9),
            rot=(R90 * .6, 0, .6), seg=16)
    k.lathe(a.part('Dishes', 'Steel'), [(.0, 0), (.65, .12), (.7, .16), (.0, .08)], loc=(-1.9, 5.3, 20.8),
            rot=(R90 * .5, 0, -.8), seg=14)
    for x, y in ((2.0, 5.6), (-1.9, 5.3)):
        a.part('Masts', 'Armor').limb((x * .6, y + .4, 20.35), (x, y, 20.85), .12, .12, bevel=0)
    for x, y, h in ((.4, 8.0, 1.5), (-.4, 8.0, 1.1), (1.4, 10.6, 1.0)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, 21.5 if y < 9 else 20.35), h=h, r=.03)
    m = a.pivot('Mount_APS', (0, 7.7, 21.52))
    k.lathe(a.part('Aps_emitter', 'Steel', m), [(.32, 0), (.32, .12), (.22, .2), (0, .24)], seg=12)
    a.part('Aps_lens', 'Energy', m).cyl(.12, .04, loc=(0, 0, .25), seg=10, bevel=0)
    g = a.part('Superstructure_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    k.greebles(g, (0, 5.0, 17.41), (1, 0, 0), (0, 1, 0), (8.6, 17.0), 18, 41, height=(.1, .3), vents=v,
               avoid=[((0, 6.5, 17.2), 4.6), ((3.4, 15.0, 17.2), 1.0), ((-3.4, 15.0, 17.2), 1.0)])
    k.greebles(g, (0, -9.0, 15.61), (1, 0, 0), (0, 1, 0), (8.0, 7.0), 10, 42, height=(.1, .3), vents=v)
    for s in (-1, 1):
        K.beacon(a, (s * 2.4, 11.6, 20.4), r=.12)


def _hp_engines(a):
    """The engine block's rear: the armoured aft face, five bells (Thruster_main, Engine_flame .. .004) with their
    glowing throats, collars and actuators; the radiator banks down the block's flanks; the dorsal intakes."""
    pm = a.pivot('Thruster_main', HP_MAIN)
    face = a.part('Engine_face', 'Armor', pm)
    k.block(face, (21.0, 8.2, .4), loc=(0, .1, -.1), rot=(R90, 0, 0), chamfer=.1, ends=(True, True))
    bells = [(7.0, 1.55, 2.05), (0, 1.55, 2.05), (-7.0, 1.55, 2.05), (3.7, -2.35, 1.7), (-3.7, -2.35, 1.7)]
    for i, (x, z, r) in enumerate(bells):
        loc = (x, .3, z)
        k.ring(a.part('Engine_collars', 'Armor', pm), [(r * 1.08, 0), (r * 1.22, 0), (r * 1.22, .35), (r * 1.08, .4)],
               loc=loc, rot=AFT, seg=24)
        k.lathe(a.part('Nozzles', 'Steel', pm), [(r * .78, .2), (r * .8, .45), (r * .92, .85), (r * 1.04, 1.35),
                                                 (r * 1.08, 1.5), (r * 1.04, 1.55), (r * .97, 1.4), (r * .84, .9),
                                                 (r * .7, .5)], loc=loc, rot=AFT, seg=24, caps=(False, False))
        a.part('Nozzle_glow', 'Energy', pm).cyl(r * .72, .05, loc=(x, .85, z), rot=(R90, 0, 0), seg=20, bevel=0)
        k.lathe(a.part('Nozzle_glow', 'Energy', pm), [(r * .2, .5), (r * .5, .62), (0, .75)], loc=loc, rot=AFT,
                seg=12)
        for j in range(4):
            u = j * TAU / 4 + TAU / 8
            a.part('Nozzle_actuators', 'Undercarriage', pm).limb(
                (x + math.cos(u) * r * 1.2, .4, z + math.sin(u) * r * 1.2),
                (x + math.cos(u) * r * 1.0, 1.2, z + math.sin(u) * r * 1.0), .12, .12, bevel=0)
        K.engine_flame(a, i, (x, 1.85, z), r * 1.02, parent=pm)
    rad = a.part('Radiators', 'Steel')
    rib = a.part('Radiator_ribs', 'Armor')
    for s in (-1, 1):
        x = s * (12.4 + .6 + .02)
        a.part('Radiator_backing', 'Undercarriage').box((.06, 13.0, 2.4), loc=(x, 21.0, 11.8), bevel=0)
        for j in range(27):
            rad.box((.38, .12, 2.3), loc=(x + s * .18, 14.7 + j * .48, 11.8), bevel=0)
        for y in (14.4, 21.0, 27.6):
            rib.box((.55, .3, 2.7), loc=(x + s * .2, y, 11.8), bevel=.03)
    # Dorsal intakes / heat exchangers on the block's roof either side of the spine.
    for s in (-1, 1):
        dk = a.part('Intakes', 'Team')
        k.sharp_loft(dk, [[(s * 5.2, 15.0, 14.9), (s * 9.6, 15.0, 14.9), (s * 9.6, 15.0, 15.0), (s * 5.2, 15.0, 15.0)],
                          [(s * 5.2, 17.6, 14.9), (s * 9.6, 17.6, 14.9), (s * 9.4, 17.6, 16.3), (s * 5.4, 17.6, 16.3)],
                          [(s * 5.2, 27.5, 14.9), (s * 9.6, 27.5, 14.9), (s * 9.4, 27.5, 16.3), (s * 5.4, 27.5, 16.3)],
                          [(s * 5.2, 29.0, 14.9), (s * 9.6, 29.0, 14.9), (s * 9.5, 29.0, 15.4), (s * 5.3, 29.0, 15.4)]],
                     chamfer=.08)
        k.inset(dk, lambda c, n, f: n.z > .5, width=.14, depth=-.03)
        a.part('Intake_mouths', 'Undercarriage').box((3.7, .1, 1.1), loc=(s * 7.4, 15.82, 15.6), rot=(-.55, 0, 0),
                                                       bevel=0)
        for j in range(6):
            a.part('Intake_vanes', 'Steel').box((.06, .5, 1.0), loc=(s * (5.75 + j * .62), 15.9, 15.55),
                                                rot=(-.55, 0, 0), bevel=0)
        for j in range(5):
            a.part('Intake_vanes', 'Steel').box((3.8, .1, .06), loc=(s * 7.4, 19.2 + j * 1.8, 16.33), bevel=0)
    g = a.part('Engine_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    for s in (-1, 1):
        k.greebles(g, (s * 11.0, 21.0, 15.11), (1, 0, 0), (0, 1, 0), (1.6, 13.0), 8, 51 + s, height=(.12, .35),
                   vents=v)
        k.greebles(g, (s * 13.03, 21.0, 7.6), (0, -s, 0), (0, 0, 1), (13.0, 2.4), 12, 53 + s, height=(.08, .25))


def _hp_nacelles(a):
    """The outboard engine nacelles (Thruster_rl at +X, Thruster_rr at -X): a turned body with its intake cone and
    ring, armour strakes, the bell with its glowing throat (Engine_flame.005 / .006), two pylons to the block (on the
    hull, so a broken nacelle leaves their stubs)."""
    for i, (name, s) in enumerate((('Thruster_rl', 1), ('Thruster_rr', -1))):
        x = s * 14.6
        p = a.pivot(name, (x, 22.0, 9.6))
        tag = '_l' if s > 0 else '_r'
        k.lathe(a.part('Engines' + tag, 'Team', p), [(0, -9.0), (.5, -8.9), (1.25, -8.0), (1.75, -6.4), (1.95, -4.0),
                                                     (1.95, 6.8), (1.8, 8.4), (1.55, 9.2)], rot=AFT, seg=24)
        k.inset(a.part('Engines' + tag, 'Team', p), lambda c, n, f: abs(n.y) < .5, width=.1, depth=-.025)
        k.ring(a.part('Engine_rings' + tag, 'Armor', p), [(1.96, -.4), (2.12, -.4), (2.12, .4), (1.96, .4)],
               loc=(0, -3.6, 0), rot=AFT, seg=24)
        k.ring(a.part('Engine_rings' + tag, 'Armor', p), [(1.96, -.3), (2.08, -.3), (2.08, .3), (1.96, .3)],
               loc=(0, 5.4, 0), rot=AFT, seg=24)
        k.lathe(a.part('Engine_intake' + tag, 'Undercarriage', p), [(0, -9.35), (.45, -9.0), (.9, -8.3)], rot=AFT,
                seg=16)
        k.lathe(a.part('Nozzles' + tag, 'Steel', p), [(1.2, 9.0), (1.3, 9.6), (1.48, 10.4), (1.52, 10.6),
                                                      (1.42, 10.5), (1.0, 9.6)], rot=AFT, seg=20, caps=(False, False))
        a.part('Nozzle_glow' + tag, 'Energy', p).cyl(1.0, .05, loc=(0, 9.7, 0), rot=(R90, 0, 0), seg=18, bevel=0)
        K.engine_flame(a, 5 + i, (0, 10.6, 0), 1.45, parent=p)
        st = a.part('Engine_strakes' + tag, 'Armor', p)
        for u in (R90 * .5, R90 * 1.5, -R90 * .5, -R90 * 1.5):
            st.limb((math.cos(u) * 1.9, -5.8, math.sin(u) * 1.9), (math.cos(u) * 1.9, 6.0, math.sin(u) * 1.9),
                    .3, .3, bevel=.04)
        K.lamp(a, (s * 1.95, -6.0, .0), facing=(s, 0, 0), r=.16, parent=p, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')
        # Pylons (on the hull).
        pyl = a.part('Pylons', 'Armor')
        for y0, y1 in ((15.0, 18.6), (25.0, 28.4)):
            k.sharp_loft(pyl, [[(s * 12.9, y0, 8.9), (s * 12.9, y1, 8.9), (s * 12.9, y1, 10.3), (s * 12.9, y0, 10.3)],
                               [(s * 12.9 + s * 1.0, y0 + .3, 9.0), (s * 12.9 + s * 1.0, y1 - .3, 9.0),
                                (s * 12.9 + s * 1.0, y1 - .3, 10.2), (s * 12.9 + s * 1.0, y0 + .3, 10.2)]],
                         chamfer=.05)
            k.sharp_loft(pyl, [[(s * 13.85, y0 + .3, 9.0), (s * 13.85, y1 - .3, 9.0), (s * 13.85, y1 - .3, 10.2),
                                (s * 13.85, y0 + .3, 10.2)],
                               [(s * 12.95 + s * 1.0 + s * .9, y0 + .7, 9.2), (s * 12.95 + s * 1.9, y1 - .7, 9.2),
                                (s * 12.95 + s * 1.9, y1 - .7, 10.0), (s * 12.95 + s * 1.9, y0 + .7, 10.0)]],
                         chamfer=.04)


def _hp_rcs(a):
    """RCS pods on the hammerhead's cheeks (Thruster_fl at +X, _fr at -X): an armoured block, four nozzle quads
    (out, up, down, forward), propellant spheres behind, a nav light."""
    for name, s in (('Thruster_fl', 1), ('Thruster_fr', -1)):
        p = a.pivot(name, (s * 12.45, -26.4, 10.0))
        tag = '_l' if s > 0 else '_r'
        k.block(a.part('Rcs_pod' + tag, 'Team', p), (1.1, 3.2, 2.4), loc=(s * .55, 0, 0), chamfer=.12,
                ends=(True, True))
        k.inset(a.part('Rcs_pod' + tag, 'Team', p), lambda c, n, f: abs(n.x) > .6, width=.1, depth=-.02)
        nz = a.part('Rcs_nozzles' + tag, 'Steel', p)
        for dy, dz, d in ((-.9, .55, (s, 0, 0)), (.9, .55, (s, 0, 0)), (-.9, -.55, (s, 0, 0)), (.9, -.55, (s, 0, 0)),
                          (0, 1.18, (0, 0, 1)), (0, -1.18, (0, 0, -1)), (-1.58, 0, (0, -1, 0))):
            base = Vector((s * (1.08 if d[0] else .55), dy, dz))
            k.lathe(nz, [(.12, 0), (.16, .1), (.24, .32), (.2, .34), (.1, .12)], loc=tuple(base), rot=K.rot_to(d),
                    seg=10, caps=(True, False))
        a.part('Rcs_tanks' + tag, 'PlasterWhite', p).sphere(.62, loc=(s * .45, 1.75, 0), seg=14, rings=10)
        K.lamp(a, (s * 1.12, 1.1, .75), facing=(s, 0, 0), r=.14, parent=p, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')


def _hp_sunbeam(a):
    """Turret: the sun-beam projector slung under the hammerhead's tip. The drum (armoured, plated, capacitor banks
    round its back), the gimbal cheeks, the projector barrel (Main_cannon: a stepped housing, five focusing rings,
    four conduits, the flared crown), the glowing lens (Main_cannon_lens) and Muzzle_main level with the prow."""
    t = a.pivot('Turret', HP_TURRET)
    k.ring(a.part('Turret_race', 'Steel'), [(3.25, -.02), (3.45, -.02), (3.45, .12), (3.25, .14)],
           loc=(HP_TURRET[0], HP_TURRET[1], HP_TURRET[2] - .1), rot=(math.pi, 0, 0), seg=32)
    drum = a.part('Turret_drum', 'Armor', t)
    k.lathe(drum, [(3.15, 0), (3.2, -.25), (3.35, -.5), (3.35, -1.65), (3.0, -2.25), (2.2, -2.75), (1.2, -3.05),
                   (0, -3.15)], seg=32, worn=(2, 3))
    k.inset(drum, lambda c, n, f: abs(n.z) < .5, width=.12, depth=-.03)
    tb = a.part('Turret_bands', 'Steel', t)
    k.ring(tb, [(3.36, -.62), (3.46, -.62), (3.46, -.78), (3.36, -.78)], seg=32)
    k.ring(tb, [(3.36, -1.45), (3.46, -1.45), (3.46, -1.58), (3.36, -1.58)], seg=32)
    # Capacitor banks round the drum's back half, with their bus bars.
    cap = a.part('Turret_capacitors', 'Steel', t)
    bus = a.part('Turret_bus', 'TeamGlow', t)
    for j in range(7):
        u = R90 * .35 + j * (math.pi * .9) / 6
        x, y = math.cos(u) * 3.5, math.sin(u) * 3.5
        cap.cyl(.32, 1.4, loc=(x, y, -1.1), seg=10, bevel=.04)
        bus.box((.1, .1, 1.0), loc=(x * .93, y * .93, -1.1), rot=(0, 0, u), bevel=0)
    # Gimbal cheeks either side of the barrel's breech, the trunnion caps.
    for s in (-1, 1):
        k.sharp_loft(a.part('Turret_cheeks', 'Team', t), [
            [(s * 2.0, -3.3, -.3), (s * 2.0, .6, -.3), (s * 2.0, .6, -2.9), (s * 2.0, -2.7, -3.2)],
            [(s * 2.7, -3.0, -.4), (s * 2.7, .3, -.4), (s * 2.7, .3, -2.75), (s * 2.7, -2.5, -3.0)]],
            chamfer=.08)
        k.lathe(a.part('Turret_trunnions', 'Steel', t), [(.0, 0), (.62, 0), (.62, .2), (.4, .3), (0, .32)],
                loc=(s * 2.7, -1.3, -1.85), rot=(0, s * R90, 0), seg=16)
    zc = -1.85
    mc = a.part('Main_cannon', 'Team', t)
    fwd = (R90, 0, 0)
    k.lathe(mc, [(0, 1.0), (1.6, .9), (1.72, .4), (1.72, -1.2), (1.48, -1.5), (1.42, -4.6), (1.56, -4.8),
                 (1.56, -5.3), (1.32, -5.5), (1.3, -6.0)], loc=(0, -1.3, zc), rot=AFT, seg=32)
    k.inset(mc, lambda c, n, f: abs(n.y) < .3, width=.08, depth=-.02)
    rings = a.part('Main_cannon_rings', 'Steel', t)
    for y in (-2.9, -3.5, -4.1, -4.7):
        k.ring(rings, [(1.43, .18), (1.92, .1), (1.92, -.1), (1.43, -.18)], loc=(0, y, zc), rot=(R90, 0, 0),
               seg=32)
    crown = a.part('Main_cannon_crown', 'Armor', t)
    k.lathe(crown, [(1.25, 0), (1.85, .1), (2.05, .45), (2.0, .75), (1.5, .8), (1.2, .55)],
            loc=(0, -7.25, zc), rot=fwd, seg=32)
    for j in range(6):
        u = j * TAU / 6
        crown.box((.26, .7, .36), loc=(math.cos(u) * 1.92, -7.65, zc + math.sin(u) * 1.62), rot=(0, -u, 0),
                  bevel=.03)
    cond = a.part('Main_cannon_conduits', 'Undercarriage', t)
    for j in range(4):
        u = j * TAU / 4 + TAU / 8
        cx, cz = math.cos(u) * 1.55, math.sin(u) * 1.55
        cond.limb((cx, -1.9, zc + cz), (cx, -4.5, zc + cz), .2, .2, bevel=.04)
    lens = a.part('Main_cannon_lens', 'Energy', t)
    k.lathe(lens, [(0, .3), (.85, .15), (1.15, 0)], loc=(0, -7.35, zc), rot=fwd, seg=28)
    a.pivot('Muzzle_main', (0, -8.1, zc), t)
    K.soot(a, (0, HP_TURRET[1] - 7.8, HP_TURRET[2] + zc), radius=1.4, k=.25)


def _hp_coilgun(a, i, x, y):
    """A twin-rail coilgun turret on the hammerhead (Mount_gun at +X, .001 at -X): the barbette and race on the hull,
    the low faceted house (sloped glacis, side capacitor lockers, a rangefinder head, roof hatch, rear power
    trunk), two rail barrels in their coil jackets (Coil_barrels*: box rails, eleven coil rings each, field
    shapers) and the field-shaping crowns (Coil_muzzles*); Muzzle_gun[.001] between the crowns, per-barrel muzzles."""
    tag = '' if i == 0 else f'_{i:03d}'
    z0 = interp(HP, y)[3]
    bar = a.part('Coil_barbette' + tag, 'Armor')
    k.lathe(bar, [(2.15, -.1), (2.15, .3), (2.0, .42), (1.9, .45)], loc=(x, y, z0), seg=28)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z0 + .43), (0, 0, 1), 2.02, 20, r=.05, h=.05)
    m = a.pivot(K.name('Mount_gun', i), (x, y, z0 + .46))
    house = a.part('Coil_house' + tag, 'Team', m)
    k.sharp_loft(house, [
        [(-1.55, -2.0, 0), (1.55, -2.0, 0), (2.0, -1.0, 0), (2.0, 2.4, 0), (1.6, 2.8, 0), (-1.6, 2.8, 0),
         (-2.0, 2.4, 0), (-2.0, -1.0, 0)],
        [(-1.3, -1.25, 1.05), (1.3, -1.25, 1.05), (1.8, -.6, 1.25), (1.8, 2.25, 1.3), (1.45, 2.6, 1.3),
         (-1.45, 2.6, 1.3), (-1.8, 2.25, 1.3), (-1.8, -.6, 1.25)],
        [(-1.0, -.7, 1.45), (1.0, -.7, 1.45), (1.4, -.3, 1.55), (1.4, 2.0, 1.55), (1.15, 2.3, 1.55),
         (-1.15, 2.3, 1.55), (-1.4, 2.0, 1.55), (-1.4, -.3, 1.55)]], chamfer=.06)
    k.inset(house, lambda c, n, f: c.z > .2, width=.08, depth=-.02)
    for s in (-1, 1):
        lk = a.part('Coil_lockers' + tag, 'Armor', m)
        k.block(lk, (.5, 2.4, .9), loc=(s * 2.15, .9, .5), chamfer=.05)
        for j in range(3):
            a.part('Coil_locker_lines' + tag, 'Undercarriage', m).box((.03, .05, .7), loc=(s * 2.41, .2 + j * .7, .5),
                                                                      bevel=0)
    k.block(a.part('Coil_rangefinder' + tag, 'Armor', m), (.6, .7, .45), loc=(-.75, .6, 1.55), chamfer=.06,
            taper=(.8, .8))
    a.part('Glass', 'Glass', m).box((.4, .02, .16), loc=(-.75, .24, 1.8), bevel=0)
    k.block(a.part('Coil_hatch' + tag, 'Steel', m), (.7, .7, .06), loc=(.6, 1.2, 1.56), chamfer=.02)
    k.block(a.part('Coil_trunk' + tag, 'Undercarriage', m), (1.4, .8, .7), loc=(0, 2.9, .3), chamfer=.06)
    zg, gap, L = .7, .62, 7.0
    y0 = -1.6
    xs = (-gap, gap)
    for bx in xs:
        brl = a.part('Coil_barrels' + tag, 'Steel', m)
        brl.box((.42, L, .5), loc=(bx, y0 - L / 2, zg), bevel=.05)
        coil = a.part('Coils_barrels' + tag, 'Undercarriage', m)
        for j in range(11):
            yy = y0 - .5 - j * .58
            coil.box((.62, .26, .7), loc=(bx, yy, zg), bevel=.04)
        a.part('Glow_barrels' + tag, 'TeamGlow', m).box((.64, 5.9, .06), loc=(bx, y0 - 3.4, zg + .2), bevel=0)
        cr = a.part('Coil_muzzles' + tag, 'Armor', m)
        k.block(cr, (.75, .9, .82), loc=(bx, y0 - L - .25, zg), chamfer=.08, ends=(True, True))
        cr.box((.2, .95, .2), loc=(bx, y0 - L - .25, zg), bevel=0)
    # The yoke between the barrels.
    a.part('Yoke_barrels' + tag, 'Armor', m).box((gap * 2 - .4, 2.6, .36), loc=(0, y0 - 1.6, zg - .1), bevel=.04)
    mz = a.pivot(K.name('Muzzle_gun', i), (0, y0 - L - .75, zg), m)
    for j, bx in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{j + 1}_gun{tag}', (bx, 0, 0), mz)
    K.soot(a, (x, y + y0 - L, z0 + .46 + zg), radius=.6, k=.25)


def _hp_ventral(a, i, x, y):
    """A ventral laser battery under the midships (Mount_gun.002 at +X, .003 at -X), hanging from its race: the
    domed house with its plated skirt, the sloped face, two emitter barrels with cooling jackets and lens crowns
    (Las_barrels* / Las_muzzles*), the sensor blister, the power trunk; Muzzle_gun.00N between the lenses,
    per-barrel muzzles."""
    tag = f'_{i:03d}'
    q = 1.3
    z0 = interp(HP, y)[2]
    k.ring(a.part('Las_race' + tag, 'Steel'), [(1.5 * q, .02), (1.66 * q, .02), (1.66 * q, -.12), (1.5 * q, -.14)],
           loc=(x, y, z0), seg=28)
    m = a.pivot(K.name('Mount_gun', i), (x, y, z0 - .1))
    house = a.part('Las_house' + tag, 'Armor', m)
    k.lathe(house, [(1.45 * q, 0), (1.5 * q, -.3 * q), (1.42 * q, -.8 * q), (1.1 * q, -1.25 * q), (.55 * q, -1.5 * q),
                    (0, -1.56 * q)], seg=28, worn=(2,))
    k.inset(house, lambda c, n, f: n.z > -.7, width=.08, depth=-.02)
    k.block(a.part('Las_face' + tag, 'Team', m), (1.9 * q, .5 * q, .9 * q), loc=(0, -1.25 * q, -1.15 * q),
            rot=(-.3, 0, 0), chamfer=.06)
    k.block(a.part('Las_trunk' + tag, 'Undercarriage', m), (1.0, .9, .6), loc=(0, 1.55 * q, -.75), chamfer=.05)
    zg, gap = -.95 * q, .42 * q
    xs = (-gap, gap)
    for bx in xs:
        k.lathe(a.part('Las_barrels' + tag, 'Steel', m), [(.0, -1.2 * q), (.2 * q, -1.2 * q), (.2 * q, -2.2 * q),
                                                          (.26 * q, -2.3 * q), (.26 * q, -3.2 * q),
                                                          (.18 * q, -3.3 * q), (.16 * q, -4.1 * q), (0, -4.1 * q)],
                loc=(bx, 0, zg), rot=AFT, seg=14)
        for j in range(4):
            a.part('Lbands_barrels' + tag, 'Undercarriage', m).cyl(.29 * q, .08 * q, loc=(bx, (-2.4 - j * .22) * q, zg),
                                                                rot=(R90, 0, 0), seg=14, bevel=0)
        k.lathe(a.part('Las_muzzles' + tag, 'Armor', m), [(.15 * q, 0), (.26 * q, .1 * q), (.26 * q, .38 * q),
                                                         (.18 * q, .42 * q)],
                loc=(bx, -4.05 * q, zg), rot=(R90, 0, 0), seg=14)
        a.part('Lens_muzzles' + tag, 'Energy', m).cyl(.15 * q, .03, loc=(bx, -4.46 * q, zg), rot=(R90, 0, 0), seg=12,
                                                     bevel=0)
    mz = a.pivot(K.name('Muzzle_gun', i), (0, -4.55 * q, zg), m)
    for j, bx in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{j + 1}_gun{tag}', (bx, 0, 0), mz)
    k.lathe(a.part('Las_blister' + tag, 'Glass', m), [(0, -.25), (.22, -.2), (.28, 0), (.22, .2), (0, .25)],
            loc=(.9 * q, -.5 * q, -1.1 * q), rot=(R90, 0, 0), seg=10)


def _hp_pd(a, name, mount, muzzle, x, y, tag):
    """A point-defence laser turret on a flank sponson (Pd_laser_l / _r): the pedestal with its cooling skirt, the
    yoke (Mount_mg[.001]) with the ball emitter and its lens barrel; Muzzle_mg[.001] at the lens."""
    z = interp(HP_SP, y)[3]
    p = a.pivot(name, (x, y, z))
    k.lathe(a.part('Pd_pedestal' + tag, 'Armor', p), [(.95, 0), (.95, .2), (.7, .35), (.55, .9), (.6, 1.0)], seg=16)
    for j in range(8):
        u = j * TAU / 8
        a.part('Pd_fins' + tag, 'Steel', p).box((.06, .35, .55), loc=(math.cos(u) * .72, math.sin(u) * .72, .55),
                                               rot=(0, 0, u + R90), bevel=0)
    m = a.pivot(mount, (0, 0, 1.0), p)
    yk = a.part('Pd_yoke' + tag, 'Team', m)
    for s in (-1, 1):
        k.block(yk, (.2, .7, .75), loc=(s * .55, 0, .0), chamfer=.04)
    k.lathe(a.part('Pd_ball' + tag, 'Steel', m), [(0, -.5), (.32, -.42), (.48, -.1), (.48, .1), (.32, .42),
                                                 (0, .5)], loc=(0, 0, .5), rot=(0, R90, 0), seg=14)
    k.lathe(a.part('Pd_barrels' + tag, 'Armor', m), [(.2, 0), (.2, .8), (.26, .85), (.26, 1.25), (.18, 1.3)],
            loc=(0, -.3, .5), rot=(R90, 0, 0), seg=12)
    a.part('Pd_lens' + tag, 'Energy', m).cyl(.15, .03, loc=(0, -1.6, .5), rot=(R90, 0, 0), seg=10, bevel=0)
    a.pivot(muzzle, (0, -1.65, .5), m)


def _hp_podbay(a):
    """Pod_bay: the ventral drop bay under the engine block: the coaming, the dark well, two doors hinged open, the
    cradle arms, a drop pod (heat shield, body, fins, hatch) in the cradle; Muzzle_missile under it."""
    p = a.pivot('Pod_bay', HP_POD)
    co = a.part('Bay_coaming', 'Armor', p)
    k.extrude(co, [(-2.6, -3.4), (2.6, -3.4), (2.6, 3.4), (-2.6, 3.4)], .3, loc=(0, 0, -.1), axis='Z', chamfer=.06)
    a.part('Bay_well', 'Charred', p).box((4.6, 6.2, .06), loc=(0, 0, -.27), bevel=0)
    for s in (-1, 1):
        d = a.part('Bay_doors', 'Team', p)
        d.box((2.3, 6.2, .14), loc=(s * (2.6 + .25), 0, -1.1), rot=(0, s * 1.15, 0), bevel=.04)
        a.part('Kit_hinges', 'Steel', p).cyl(.09, 6.0, loc=(s * 2.55, 0, -.25), rot=(R90, 0, 0), seg=8, bevel=0)
        for j in range(3):
            a.part('Bay_arms', 'Steel', p).limb((s * 1.6, -2.0 + j * 2.0, -.25), (s * .9, -2.0 + j * 2.0, -1.4),
                                                .16, .16, bevel=.03)
    pod = a.part('Pods', 'PlasterWhite', p)
    k.lathe(pod, [(0, -3.0), (.6, -2.95), (1.05, -2.7), (1.15, -2.4), (1.0, -1.2), (.85, -.5), (.6, -.3)], seg=18)
    k.lathe(a.part('Pod_shield', 'Charred', p), [(0, -3.05), (.62, -3.0), (1.1, -2.72), (1.18, -2.45),
                                                 (1.0, -2.45)], seg=18)
    for j in range(4):
        u = j * TAU / 4 + TAU / 8
        a.part('Pod_fins', 'Armor', p).box((.08, .6, .9), loc=(math.cos(u) * 1.0, math.sin(u) * 1.0, -1.1),
                                           rot=(0, 0, u + R90), bevel=0)
    a.part('Pod_hatch', 'Team', p).box((.5, .06, .7), loc=(0, -1.06, -1.7), rot=(.12, 0, 0), bevel=0)
    a.pivot('Muzzle_missile', (0, 0, -3.1), p)


def _hp_plating(a):
    """The heavy plating that gives the hull its scale: segmented armour plates down the dorsal spine with heat-sink
    grilles between them, buttress ribs on the tiers' flanks, the bridge's visor overhang, armour ribs on the
    prongs and the engine block, a row of dorsal launch hatches behind the brow."""
    ar = a.part('Spine_plates', 'Armor')
    gr = a.part('Spine_grilles', 'Undercarriage')
    slat = a.part('Spine_slats', 'Steel')
    for j, (y0, y1) in enumerate(((-16.6, -13.4), (-13.0, -9.8), (-9.4, -6.2))):
        r = interp(HP_SPINE, (y0 + y1) / 2)
        w = 2 * (r[1] - r[4]) - .6
        k.block(ar, (w, y1 - y0 - .25, .22), loc=(0, (y0 + y1) / 2, r[3] + .1), chamfer=.06, taper=(.94, .96))
        gr.box((w * .6, .32, .05), loc=(0, y1 + .2, r[3] + .02), bevel=0)
        for i in range(7):
            slat.box((.05, .3, .07), loc=(-w * .27 + i * w * .09, y1 + .2, r[3] + .05), bevel=0)
    # Launch hatches: two rows of square lids on the spine behind the brow.
    lids = a.part('Spine_hatches', 'Team')
    for i in range(4):
        for sx in (-1, 1):
            y = -20.6 + i * .95
            k.block(lids, (.8, .8, .08), loc=(sx * .95, y, interp(HP_SPINE, y)[3] + .03), chamfer=.02)
    # Buttress ribs down the first tier's flanks.
    rib = a.part('Tier_ribs', 'Armor')
    for sx in (-1, 1):
        for i in range(8):
            y = -1.4 + i * 2.0
            rib.limb((sx * 5.25, y, 15.05), (sx * 4.75, y, 17.3), .32, .5, bevel=.04)
        for i in range(5):
            y = 3.6 + i * 2.0
            rib.limb((sx * 4.05, y, 17.25), (sx * 3.65, y, 18.95), .26, .4, bevel=.04)
    # The bridge visor: an overhang over the glazing with its cheek fins.
    vis = a.part('Bridge_visor', 'Team')
    k.sharp_loft(vis, [[(3.3, 2.6, 20.42), (-3.3, 2.6, 20.42), (-3.3, 2.6, 20.62), (3.3, 2.6, 20.62)],
                       [(3.2, 5.2, 20.42), (-3.2, 5.2, 20.42), (-3.2, 5.2, 20.74), (3.2, 5.2, 20.74)]], chamfer=.05)
    for sx in (-1, 1):
        k.extrude(vis, [(2.7, 18.8), (5.2, 18.8), (5.2, 20.5), (2.7, 20.5)], .16, loc=(sx * 3.25, 0, 0), axis='X',
                  chamfer=.03)
    # Armour ribs on the prongs' outer faces and down the engine block's flanks under the radiators.
    rib2 = a.part('Hull_ribs', 'Armor')
    for sx in (-1, 1):
        for y in (-32.0, -30.4, -28.8):
            r = interp(HP_PRONG, y)
            x = sx * (HP_PRONG_X + r[1] + r[6] + .02)
            rib2.box((.18, .34, (r[3] - r[2]) * .55), loc=(x, y, r[7] + .3), bevel=.03)
        for i in range(9):
            y = 12.6 + i * 2.1
            r = interp(HP, y)
            rib2.box((.2, .36, 3.6), loc=(sx * (r[1] + r[6] + .03), y, 7.8), bevel=.03)


def _hp_detail(a):
    """Lit windows along the sponsons and the hammerhead's cheeks, nav lights, beacons, greebles on the shoulders,
    the sponson tops and the underside, the docking hatches, faction stripes on the brow (no insignia)."""
    win = a.part('Windows', 'Lamp')
    for s in (-1, 1):
        # Sponson gallery windows, each on the sponson's belt where it is at that station.
        for j in range(17):
            y = -13.2 + j * 1.1
            r = interp(HP_SP, y)
            win.box((.04, .5, .24), loc=(s * (r[1] + r[6] * .55 + .01), y, r[7] + .55), bevel=0)
        for j in range(7):
            win.box((.04, .42, .2), loc=(s * 12.42, -28.2 + j * .85, 12.0), bevel=0)
        K.beacon(a, (s * 9.6, -20.2, 14.6), r=.16)
        K.lamp(a, (s * 9.62, 8.2, 10.2), facing=(s, 0, 0), r=.16, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')
        a.part('Team_stripes', 'TeamGlow').box((.14, 6.0, .05), loc=(s * 2.4, -23.6, 16.22), bevel=0)
        for y in (-10.0, 1.0):
            r = interp(HP_SP, y)
            K.hatch_rect(a, (s * (r[1] + r[6] * .55 + .02), y, r[7] - .9), size=(1.2, 1.4), normal=(s, 0, 0))
    g = a.part('Hull_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    avoid = [((x, y, 14.7), 2.6) for x, y in HP_COIL]
    for s in (-1, 1):
        k.greebles(g, (s * 7.0, -21.2, 14.71), (1, 0, 0), (0, 1, 0), (3.6, 3.0), 5, 61 + s, height=(.12, .35),
                   vents=v, avoid=avoid)
        k.greebles(g, (s * 8.4, -4.8, 12.21), (1, 0, 0), (0, 1, 0), (.9, 18.0), 10, 63 + s, height=(.1, .3),
                   avoid=[((x, y, 12.2), 1.4) for x, y in HP_PD])
        # Underside greebles on the hammerhead and the engine block.
        k.greebles(g, (s * 7.0, -26.0, 5.64), (1, 0, 0), (0, -1, 0), (4.0, 8.0), 10, 65 + s, height=(.1, .3),
                   avoid=[((0, -25.4, 5.6), 4.0)])
        k.greebles(g, (s * 7.2, 22.0, 4.99), (1, 0, 0), (0, -1, 0), (5.6, 14.0), 14, 67 + s, height=(.1, .35),
                   avoid=[(HP_POD, 3.6)])
    for x, y in ((.8, 2.0), (-.8, 3.2), (.0, 5.0)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, 5.2), h=1.2, r=.03, lean=math.pi)


def hyperion(a, detail=False):
    """Hyperion, the heavy cruiser: see the module docstring."""
    K.suffixed(a)
    _hp_hull(a)
    _hp_superstructure(a)
    _hp_plating(a)
    _hp_engines(a)
    _hp_nacelles(a)
    _hp_rcs(a)
    _hp_sunbeam(a)
    for i, (x, y) in enumerate(HP_COIL):
        _hp_coilgun(a, i, x, y)
    for j, (x, y) in enumerate(HP_VLAS):
        _hp_ventral(a, 2 + j, x, y)
    for (x, y), name, mount, muzzle, tag in zip(HP_PD, ('Pd_laser_l', 'Pd_laser_r'), ('Mount_mg', 'Mount_mg__001'),
                                                ('Muzzle_mg', 'Muzzle_mg__001'), ('_l', '_r')):
        _hp_pd(a, name, mount, muzzle, x, y, tag)
    _hp_podbay(a)
    _hp_detail(a)
    K.tone(a, 'Pod_bay', k=.9)
    K.tone(a, 'Thruster_rl', k=.92)
    K.tone(a, 'Thruster_rr', k=.92)
    k.clean(a)


# ============================================================================= Theia (escort carrier, 40.3 m)
TH = [  # y, hw, z0, z1, ct, cb, bul, zm
    (-16.6, 4.6, 4.6, 8.8, 1.0, 1.0, .1, 6.6),
    (-15.6, 5.8, 4.0, 9.3, 1.2, 1.2, .25, 6.5),
    (-6.0, 5.5, 4.0, 9.3, 1.2, 1.2, .25, 6.5),
    (2.0, 6.0, 3.8, 9.5, 1.3, 1.3, .3, 6.5),
    (6.4, 7.2, 3.4, 9.8, 1.5, 1.4, .35, 6.5),
    (17.8, 7.4, 3.4, 9.8, 1.5, 1.4, .35, 6.5),
    (18.8, 6.6, 3.8, 9.4, 1.4, 1.3, .2, 6.5),
]
TH_PRONG = [  # the two short prongs either side of the launch notch (centred at x = +-TH_PRONG_X)
    (-19.95, 1.0, 5.2, 8.0, .5, .6, 0, 6.6),
    (-19.2, 1.9, 4.6, 8.8, .7, .8, .1, 6.6),
    (-15.8, 2.1, 4.2, 9.2, .8, .9, .15, 6.6),
]
TH_PRONG_X = 3.6
TH_SPINE_F = [(-16.5, 1.6, 8.9, 9.7, .4, .05, 0, 9.3), (-15.4, 2.6, 8.9, 10.0, .6, .05, 0, 9.4),
              (-12.9, 2.6, 8.9, 10.0, .6, .05, 0, 9.4), (-12.3, 1.8, 8.9, 9.6, .4, .05, 0, 9.3)]
TH_SPINE_A = [(2.6, 2.0, 9.2, 9.9, .4, .05, 0, 9.5), (3.6, 3.2, 9.2, 10.3, .6, .05, 0, 9.7),
              (16.4, 3.4, 9.2, 10.4, .6, .05, 0, 9.8), (18.0, 2.4, 9.2, 10.0, .45, .05, 0, 9.6)]
TH_BAY = [  # each flank hangar pod (centred at x = +-TH_BAY_X)
    (-12.6, 1.2, 4.9, 7.9, .5, .5, 0, 6.4),
    (-11.8, 1.85, 4.5, 8.5, .6, .6, .1, 6.5),
    (6.6, 1.85, 4.5, 8.5, .6, .6, .1, 6.5),
    (8.6, 1.2, 5.0, 8.0, .5, .5, 0, 6.5),
]
TH_BAY_X = 8.3
TH_TURRET = (0, -9.8, 9.3)
TH_POD = (0, 2.0, 3.8)
TH_MAIN = (0, 18.8, 6.6)


def _th_hull(a):
    """Theia's hull: the short forked prow with the launch notch between its prongs (the runway plate, chevrons,
    approach lights, the lit tunnel mouth in the notch's back wall), the long body, the wide engine block, the dark
    spine fore and aft, the recovery deck aft of the turret, the keel, plate seams and greebles."""
    loft(a.part('Hull', 'Team'), TH, step=1.8, inset=(.12, -.03))
    pr = a.part('Hull_prongs', 'Team')
    for s in (-1, 1):
        rows = [sec(*r) for r in stations(TH_PRONG, 1.2)]
        k.sharp_loft(pr, [[(x + s * TH_PRONG_X, y, z) for x, y, z in ring] for ring in rows], chamfer=.1)
    k.inset(pr, lambda c, n, f: True, width=.1, depth=-.025)
    loft(a.part('Hull_spine', 'Armor'), TH_SPINE_F, step=1.4, inset=(.08, -.02))
    loft(a.part('Hull_spine', 'Armor'), TH_SPINE_A, step=1.8, inset=(.1, -.025))
    loft(a.part('Hull_keel', 'Armor'), [(-12.0, .5, 3.4, 4.2, .2, .2, 0, 3.8), (-10.8, 1.1, 3.1, 4.2, .3, .3, 0, 3.6),
                                       (-2.0, 1.1, 3.1, 4.0, .3, .3, 0, 3.5), (-1.0, .5, 3.4, 4.0, .2, .2, 0, 3.7)],
         step=1.8, chamfer=.06, inset=(.08, -.02))
    # The launch notch: the runway plate between the prongs, chevrons, edge lights; the tunnel mouth in the wall.
    rw = a.part('Runway', 'Armor')
    k.block(rw, (3.1, 3.6, .2), loc=(0, -18.3, 4.8), chamfer=.04)
    chev = a.part('Mouth_chevrons', 'Hazard')
    for i in range(3):
        chev.box((.9, .28, .02), loc=(-.45, -19.3 + i * 1.0, 4.91), rot=(0, 0, .6), bevel=0)
        chev.box((.9, .28, .02), loc=(.45, -19.3 + i * 1.0, 4.91), rot=(0, 0, -.6), bevel=0)
    lights = a.part('Mouth_lights', 'Lamp')
    for i in range(5):
        for s in (-1, 1):
            lights.cyl(.06, .03, loc=(s * 1.4, -19.8 + i * .8, 4.92), seg=6, bevel=0)
    fr = a.part('Mouth_frame', 'Armor')
    k.extrude(fr, [(-1.4, 4.9), (1.4, 4.9), (1.4, 8.2), (-1.4, 8.2)], .3, loc=(0, -16.6, 0), axis='Y', chamfer=.04)
    a.part('Mouth', 'Charred').box((2.5, .06, 3.0), loc=(0, -16.78, 6.55), bevel=0)
    lights.box((2.4, .05, .08), loc=(0, -16.82, 7.95), bevel=0)
    for s in (-1, 1):
        a.part('Prow_slits', 'Energy').box((.06, 3.0, .1), loc=(s * (TH_PRONG_X - 2.1 - .17), -17.8, 7.6), bevel=0)
        a.part('Windows', 'Lamp').box((1.4, .06, .16), loc=(s * TH_PRONG_X, -19.97, 7.3), bevel=0)
    # Armour ridges on the prongs, shoulder plates behind them.
    ar = a.part('Armour_plates', 'Armor')
    for s in (-1, 1):
        k.sharp_loft(ar, [[(s * TH_PRONG_X + 1.0, -19.5, 8.25), (s * TH_PRONG_X, -19.5, 8.6),
                           (s * TH_PRONG_X - 1.0, -19.5, 8.25), (s * TH_PRONG_X, -19.5, 8.2)],
                          [(s * TH_PRONG_X + 1.5, -15.4, 9.3), (s * TH_PRONG_X, -15.4, 9.8),
                           (s * TH_PRONG_X - 1.5, -15.4, 9.3), (s * TH_PRONG_X, -15.4, 9.25)]], chamfer=.04)
        k.block(ar, (1.4, 4.8, .16), loc=(s * 4.7, -13.0, 9.25), rot=(0, s * -.35, 0), chamfer=.04)
    # The recovery deck aft of the turret: a flat pad with a hazard edge and deck lights.
    pad = a.part('Deck', 'Armor')
    k.block(pad, (6.0, 8.4, .14), loc=(0, -2.0, 9.46), chamfer=.04)
    hz = a.part('Deck_hazard', 'Hazard')
    for s in (-1, 1):
        hz.box((.16, 8.0, .02), loc=(s * 2.8, -2.0, 9.54), bevel=0)
    for i in range(3):
        hz.box((2.4, .12, .02), loc=(0, -5.4 + i * 3.4, 9.54), bevel=0)
    dl = a.part('Deck_lights', 'Lamp')
    for i in range(6):
        for s in (-1, 1):
            dl.cyl(.07, .03, loc=(s * 2.8, -5.9 + i * 1.55, 9.56), seg=6, bevel=0)
    tr = a.part('Hull_trim', 'Undercarriage')
    for s in (-1, 1):
        band(tr, [(s * (r[1] + r[6] + .04), r[0], r[7]) for r in stations(TH, 2.5)][1:-1], .16, .08)
    win = a.part('Windows', 'Lamp')
    for s in (-1, 1):
        for j in range(10):
            y = 7.4 + j * 1.0
            r = interp(TH, y)
            win.box((.04, .42, .18), loc=(s * (r[1] + r[6] * .3 + .25), y, r[7] + 2.1), bevel=0)
    g = a.part('Hull_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    for s in (-1, 1):
        k.greebles(g, (s * 5.2, 12.6, 9.81), (1, 0, 0), (0, 1, 0), (2.0, 10.0), 10, 71 + s, height=(.08, .25), vents=v)
        k.greebles(g, (s * 3.6, 9.0, 3.39), (1, 0, 0), (0, -1, 0), (2.4, 14.0), 10, 73 + s, height=(.08, .22),
                   avoid=[(TH_POD, 2.8)])


def _th_bays(a):
    """The two flank hangar pods (the drone bays): a plated pod on two pylons, the open bay mouth at its front with
    its frame, lit strip and three drones on the launch rail, the side hangar doors with lit seams, the PD laser on
    each pod's back (Pd_laser_l / _r > Mount_mg / .001 > Muzzle_mg / .001)."""
    for s, name, mount, muzzle, tag in ((1, 'Pd_laser_l', 'Mount_mg', 'Muzzle_mg', '_l'),
                                        (-1, 'Pd_laser_r', 'Mount_mg__001', 'Muzzle_mg__001', '_r')):
        x0 = s * TH_BAY_X
        rows = [sec(*r) for r in stations(TH_BAY, 1.6)]
        pod = a.part('Hangar_pods', 'Team')
        k.sharp_loft(pod, [[(x + x0, y, z) for x, y, z in ring] for ring in rows], chamfer=.1)
        k.inset(pod, lambda c, n, f: True, width=.1, depth=-.025)
        # Pylons to the hull.
        pyl = a.part('Pylons', 'Armor')
        for y0, y1 in ((-9.0, -6.0), (1.0, 4.0)):
            k.sharp_loft(pyl, [[(s * 5.9, y0, 5.8), (s * 5.9, y1, 5.8), (s * 5.9, y1, 7.4), (s * 5.9, y0, 7.4)],
                               [(s * 6.7, y0 + .3, 5.9), (s * 6.7, y1 - .3, 5.9), (s * 6.7, y1 - .3, 7.2),
                                (s * 6.7, y0 + .3, 7.2)]], chamfer=.04)
        # The bay mouth: frame, dark interior, lit strip, the launch rail and three drones on it.
        fr = a.part('Bay_frames', 'Armor')
        k.extrude(fr, [(-1.4, 4.7), (1.4, 4.7), (1.4, 8.3), (-1.4, 8.3)], .3, loc=(x0, -12.15, 0), axis='Y',
                  chamfer=.04)
        a.part('Bay_mouths', 'Charred').box((2.3, .06, 3.0), loc=(x0, -12.32, 6.5), bevel=0)
        a.part('Bay_lights', 'Lamp').box((2.2, .05, .08), loc=(x0, -12.36, 7.9), bevel=0)
        a.part('Bay_rails', 'Steel').box((.18, 2.2, .1), loc=(x0, -13.2, 5.0), bevel=0)
        dr = a.part('Drones', 'Undercarriage')
        wing = a.part('Drone_wings', 'Team')
        for j in range(3):
            dy = -13.9 + j * .7
            k.lathe(dr, [(0, -.35), (.12, -.25), (.14, .2), (.08, .35)], loc=(x0, dy, 5.25), rot=K.FORWARD, seg=8)
            wing.box((.9, .18, .03), loc=(x0, dy + .05, 5.28), bevel=0)
        # Side hangar doors with lit seams.
        for j in range(4):
            y = -8.6 + j * 3.6
            a.part('Hangar_doors', 'Armor').box((.08, 3.0, 2.6), loc=(s * (TH_BAY_X + 1.95), y, 6.5), bevel=.02)
            a.part('Bay_lights', 'Lamp').box((.05, .06, 2.4), loc=(s * (TH_BAY_X + 2.0), y + 1.58, 6.5), bevel=0)
        K.lamp(a, (s * (TH_BAY_X + 1.9), 7.6, 7.6), facing=(s, 0, 0), r=.13, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')
        # PD laser on the pod's back: a low drum, the turning head with its twin lens tubes.
        p = a.pivot(name, (x0, -3.0, 8.5))
        k.lathe(a.part('Pd_drum' + tag, 'Armor', p), [(.75, 0), (.75, .3), (.55, .45)], seg=16)
        m = a.pivot(mount, (0, 0, .45), p)
        k.sharp_loft(a.part('Pd_head' + tag, 'Team', m), [
            [(-.45, -.5, 0), (.45, -.5, 0), (.5, .5, 0), (-.5, .5, 0)],
            [(-.32, -.35, .5), (.32, -.35, .5), (.38, .4, .5), (-.38, .4, .5)]], chamfer=.04)
        for bx in (-.17, .17):
            k.lathe(a.part('Pd_barrels' + tag, 'Steel', m), [(.09, 0), (.09, .9), (.12, .95), (.12, 1.15)],
                    loc=(bx, -.45, .28), rot=K.FORWARD, seg=10)
            a.part('Pd_lens' + tag, 'Energy', m).cyl(.08, .02, loc=(bx, -1.61, .28), rot=(R90, 0, 0), seg=8, bevel=0)
        a.pivot(muzzle, (0, -1.65, .28), m)


def _th_turret(a):
    """Turret (main_laser): a dorsal dome turret ahead of the recovery deck: the barbette ring, the faceted dome
    with its sensor head, two laser emitters (Main_cannon: cooling jackets, focusing collars) with their lenses
    (Main_cannon_lens), Muzzle_main between them."""
    x, y, z = TH_TURRET
    k.lathe(a.part('Turret_barbette', 'Armor'), [(2.0, -.1), (2.0, .12), (1.85, .2)], loc=(x, y, z), seg=28)
    t = a.pivot('Turret', (x, y, z + .2))
    dome = a.part('Turret_dome', 'Team', t)
    k.sharp_loft(dome, [
        [(-1.2, -1.6, 0), (1.2, -1.6, 0), (1.8, -.6, 0), (1.8, 1.4, 0), (1.2, 1.9, 0), (-1.2, 1.9, 0), (-1.8, 1.4, 0),
         (-1.8, -.6, 0)],
        [(-.9, -1.1, .9), (.9, -1.1, .9), (1.4, -.4, 1.05), (1.4, 1.2, 1.05), (.95, 1.55, 1.05), (-.95, 1.55, 1.05),
         (-1.4, 1.2, 1.05), (-1.4, -.4, 1.05)],
        [(-.5, -.5, 1.35), (.5, -.5, 1.35), (.8, -.1, 1.4), (.8, .9, 1.4), (.5, 1.1, 1.4), (-.5, 1.1, 1.4),
         (-.8, .9, 1.4), (-.8, -.1, 1.4)]], chamfer=.05)
    k.inset(dome, lambda c, n, f: c.z > .15, width=.07, depth=-.015)
    k.lathe(a.part('Turret_sensor', 'Steel', t), [(0, -.25), (.2, -.2), (.26, 0), (.2, .2), (0, .25)],
            loc=(-.85, -.3, 1.25), rot=K.FORWARD, seg=10)
    a.part('Glass', 'Glass', t).cyl(.12, .02, loc=(-.85, -.57, 1.25), rot=(R90, 0, 0), seg=8, bevel=0)
    zg = .62
    for bx in (-.55, .55):
        k.lathe(a.part('Main_cannon', 'Steel', t), [(.0, -.6), (.26, -.6), (.26, .9), (.32, 1.0), (.32, 2.2),
                                                    (.22, 2.3), (.2, 3.6), (0, 3.6)], loc=(bx, -1.0, zg),
                rot=K.FORWARD, seg=14)
        for j in range(3):
            a.part('Main_cannon_rings', 'Undercarriage', t).cyl(.35, .1, loc=(bx, -2.2 - j * .35, zg),
                                                                rot=(R90, 0, 0), seg=14, bevel=0)
        k.lathe(a.part('Main_cannon_crown', 'Armor', t), [(.18, 0), (.3, .1), (.3, .35), (.22, .4)],
                loc=(bx, -4.55, zg), rot=K.FORWARD, seg=14)
        a.part('Main_cannon_lens', 'Energy', t).cyl(.18, .03, loc=(bx, -4.96, zg), rot=(R90, 0, 0), seg=12, bevel=0)
    a.pivot('Muzzle_main', (0, -5.05, zg), t)
    for j, bx in enumerate((-.55, .55)):
        a.pivot(f'Muzzle_b{j + 1}_main', (bx, 0, 0), 'Muzzle_main')


def _th_island(a):
    """The island aft on the spine: two stepped tiers and the bridge (lit windows, glazing under a visor), two swept
    fins, a mast with its dish and whip, Mount_APS on top, a beacon."""
    loft(a.part('Superstructure', 'Team'), [(5.0, 2.2, 10.2, 10.6, .3, .05, 0, 10.4), (6.2, 3.0, 10.2, 11.8, .5, .05, 0, 10.8),
                                            (13.6, 2.9, 10.2, 11.8, .5, .05, 0, 10.8),
                                            (15.0, 2.2, 10.2, 11.0, .4, .05, 0, 10.6)], step=1.4, inset=(.08, -.02))
    loft(a.part('Bridge', 'Team'), [(7.6, 1.5, 11.7, 11.9, .2, .05, 0, 11.8), (8.6, 2.1, 11.7, 12.9, .3, .05, 0, 12.2),
                                    (12.2, 2.0, 11.7, 12.9, .3, .05, 0, 12.2), (13.0, 1.6, 11.7, 12.3, .25, .05, 0, 12.0)],
         step=1.2, inset=(.06, -.015))
    a.part('Glass', 'Glass').limb((1.6, 8.08, 12.4), (-1.6, 8.08, 12.4), .42, .05, bevel=0)
    vis = a.part('Bridge_visor', 'Armor')
    k.sharp_loft(vis, [[(2.3, 7.6, 12.92), (-2.3, 7.6, 12.92), (-2.3, 7.6, 13.06), (2.3, 7.6, 13.06)],
                       [(2.2, 9.4, 12.92), (-2.2, 9.4, 12.92), (-2.2, 9.4, 13.12), (2.2, 9.4, 13.12)]], chamfer=.03)
    for s in (-1, 1):
        windows(a, 'Windows', s * 3.05, 6.8, 13.0, 11.1, .75, s, h=.16, w=.38)
    fin = a.part('Fins', 'Team')
    for s in (-1, 1):
        k.extrude(fin, [(11.6, 11.6), (15.6, 11.0), (15.6, 11.5), (14.6, 13.8), (13.8, 14.1), (13.2, 13.9)], .22,
                  loc=(s * 2.0, 0, 0), axis='X', chamfer=.04)
        a.part('Fin_glow', 'TeamGlow').box((.04, .3, .5), loc=(s * 2.12, 13.6, 12.6), rot=(-.45, 0, 0), bevel=0)
    ms = a.part('Masts', 'Armor')
    k.sharp_loft(ms, [[(.4, 9.6, 12.85), (-.4, 9.6, 12.85), (-.4, 11.0, 12.85), (.4, 11.0, 12.85)],
                      [(.2, 10.0, 14.0), (-.2, 10.0, 14.0), (-.2, 10.6, 14.0), (.2, 10.6, 14.0)]], chamfer=.03)
    k.lathe(a.part('Dishes', 'Steel'), [(.0, 0), (.55, .1), (.58, .13), (.0, .07)], loc=(1.2, 11.6, 13.2),
            rot=(R90 * .6, 0, .7), seg=14)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, 11.6, 12.9), h=1.1, r=.025)
    m = a.pivot('Mount_APS', (0, 10.3, 14.02))
    k.lathe(a.part('Aps_emitter', 'Steel', m), [(.22, 0), (.22, .1), (.15, .16), (0, .19)], seg=10)
    a.part('Aps_lens', 'Energy', m).cyl(.08, .03, loc=(0, 0, .2), seg=8, bevel=0)
    K.beacon(a, (0, 14.6, 11.0), r=.1)


def _th_engines(a):
    """Thruster_main: three bells in the aft face (Engine_flame .. .002), the face plate, collars, glowing throats;
    radiator vanes on the engine block's flanks."""
    pm = a.pivot('Thruster_main', TH_MAIN)
    k.block(a.part('Engine_face', 'Armor', pm), (12.6, 5.2, .3), loc=(0, .05, 0), rot=(R90, 0, 0), chamfer=.08,
            ends=(True, True))
    for i, x in enumerate((3.6, 0, -3.6)):
        r = 1.45 if x else 1.6
        loc = (x, .2, 0)
        k.ring(a.part('Engine_collars', 'Armor', pm), [(r * 1.08, 0), (r * 1.2, 0), (r * 1.2, .3), (r * 1.08, .32)],
               loc=loc, rot=AFT, seg=22)
        k.lathe(a.part('Nozzles', 'Steel', pm), [(r * .8, .15), (r * .86, .5), (r * 1.0, 1.0), (r * 1.06, 1.2),
                                                 (r * .98, 1.12), (r * .84, .7), (r * .72, .4)], loc=loc, rot=AFT,
                seg=22, caps=(False, False))
        a.part('Nozzle_glow', 'Energy', pm).cyl(r * .72, .05, loc=(x, .62, 0), rot=(R90, 0, 0), seg=18, bevel=0)
        K.engine_flame(a, i, (x, 1.42, 0), r, parent=pm)
    rad = a.part('Radiators', 'Steel')
    for s in (-1, 1):
        x = s * (7.4 + .35 + .02)
        a.part('Radiator_backing', 'Undercarriage').box((.05, 9.0, 1.6), loc=(x, 13.0, 7.9), bevel=0)
        for j in range(19):
            rad.box((.3, .1, 1.5), loc=(x + s * .14, 8.7 + j * .48, 7.9), bevel=0)


def _th_podbay(a):
    """Pod_bay: the wide ventral drone and pod bay: coaming, dark well, doors folded down, a launch rack of six
    drones and a drop pod in its cradle; Muzzle_missile under it (the drone swarm leaves from here)."""
    p = a.pivot('Pod_bay', TH_POD)
    k.extrude(a.part('Bay_coaming', 'Armor', p), [(-2.2, -3.6), (2.2, -3.6), (2.2, 3.6), (-2.2, 3.6)], .26,
              loc=(0, 0, -.08), axis='Z', chamfer=.05)
    a.part('Bay_well', 'Charred', p).box((3.9, 6.8, .05), loc=(0, 0, -.22), bevel=0)
    for s in (-1, 1):
        a.part('Bay_doors', 'Team', p).box((1.9, 6.8, .12), loc=(s * 2.55, 0, -.85), rot=(0, s * 1.2, 0), bevel=.03)
        a.part('Kit_hinges', 'Steel', p).cyl(.07, 6.6, loc=(s * 2.2, 0, -.2), rot=(R90, 0, 0), seg=8, bevel=0)
    rack = a.part('Bay_rack', 'Steel', p)
    rack.box((.2, 6.0, .15), loc=(-1.0, 0, -.45), bevel=0)
    rack.box((.2, 6.0, .15), loc=(1.0, 0, -.45), bevel=0)
    dr = a.part('Drones', 'Undercarriage', p)
    wing = a.part('Drone_wings', 'Team', p)
    for j in range(3):
        for bx in (-1.0, 1.0):
            dy = -2.6 + j * 1.0
            k.lathe(dr, [(0, -.38), (.13, -.27), (.15, .22), (.09, .38)], loc=(bx, dy, -.68), rot=K.FORWARD, seg=8)
            wing.box((1.0, .2, .03), loc=(bx, dy + .05, -.64), bevel=0)
    pod = a.part('Pods', 'PlasterWhite', p)
    k.lathe(pod, [(0, -2.5), (.5, -2.45), (.85, -2.25), (.92, -2.0), (.82, -1.0), (.68, -.45), (.5, -.25)],
            loc=(0, 1.9, 0), seg=16)
    k.lathe(a.part('Pod_shield', 'Charred', p), [(0, -2.55), (.52, -2.5), (.88, -2.27), (.95, -2.04), (.82, -2.04)],
            loc=(0, 1.9, 0), seg=16)
    a.pivot('Muzzle_missile', (0, -1.0, -1.2), p)


def _th_detail(a):
    """Theia's small parts: armour ribs down the flanks, RCS quads at the four corners, docking hatches, nav lights,
    an asymmetric comms boom on the right hangar pod (mast, two dishes, whips), a tug and a parked drone on the
    recovery deck, raised plates and vents on the engine block, belly antennas."""
    rib = a.part('Hull_ribs', 'Armor')
    for s in (-1, 1):
        for y in (-14.4, -11.6, -8.8, 7.6, 10.4, 13.2, 16.0):
            r = interp(TH, y)
            rib.box((.16, .3, (r[3] - r[2]) * .5), loc=(s * (r[1] + r[6] + .02), y, r[7] + .2), bevel=.03)
        for y in (-17.4, 17.2):
            r = interp(TH, y)
            p = (s * (r[1] + r[6] + .05), y, r[7] + 1.0)
            k.block(a.part('Rcs_pods', 'Armor'), (.5, 1.2, .9), loc=(p[0] + s * .2, p[1], p[2]), chamfer=.05,
                    ends=(True, True))
            for dz in (-.25, .25):
                k.lathe(a.part('Rcs_nozzles', 'Steel'), [(.06, 0), (.08, .05), (.12, .16), (.1, .17)],
                        loc=(p[0] + s * .45, p[1], p[2] + dz), rot=K.rot_to((s, 0, 0)), seg=8, caps=(True, False))
        for y in (-14.6, 12.0):
            r = interp(TH, y)
            K.hatch_rect(a, (s * (r[1] + r[6] * .6 + .03), y, r[7] - .6), size=(.9, 1.0), normal=(s, 0, 0))
        K.lamp(a, (s * 7.6, 17.0, 8.6), facing=(s, 0, 0), r=.12, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')
    # Comms boom on the right hangar pod (asymmetric).
    x0 = -TH_BAY_X
    mast = a.part('Masts', 'Armor')
    mast.limb((x0, 4.4, 8.4), (x0, 4.4, 10.6), .22, .22, bevel=.03)
    mast.limb((x0, 4.4, 10.4), (x0 - 1.0, 4.4, 10.4), .14, .14, bevel=0)
    k.lathe(a.part('Dishes', 'Steel'), [(0, 0), (.5, .09), (.53, .12), (0, .06)], loc=(x0 - 1.05, 4.4, 10.4),
            rot=(0, -R90 * .8, 0), seg=14)
    k.lathe(a.part('Dishes', 'Steel'), [(0, 0), (.32, .06), (.34, .08), (0, .04)], loc=(x0, 4.4, 10.7),
            rot=(R90 * .3, 0, 0), seg=12)
    for dy in (-1.0, 1.0):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x0 + .4, 4.4 + dy, 8.45), h=1.4, r=.025)
    # A deck tug and a parked drone on the recovery deck.
    tug = a.part('Deck_tug', 'Hazard')
    k.block(tug, (.9, 1.5, .4), loc=(1.4, -4.8, 9.75), chamfer=.06, ends=(True, True))
    a.part('Glass', 'Glass').box((.6, .04, .16), loc=(1.4, -5.56, 9.85), bevel=0)
    dr = a.part('Drones', 'Undercarriage')
    k.lathe(dr, [(0, -.6), (.2, -.42), (.24, .35), (.14, .6)], loc=(-1.0, -.6, 9.8), rot=(R90, 0, .4), seg=10)
    a.part('Drone_wings', 'Team').box((1.6, .3, .04), loc=(-1.0, -.6, 9.84), rot=(0, 0, .4), bevel=0)
    # Raised plates and vents on the engine block, belly antennas.
    pl = a.part('Engine_plates', 'Armor')
    for s in (-1, 1):
        for y in (8.4, 11.0, 13.6, 16.2):
            k.block(pl, (1.6, 2.2, .14), loc=(s * 5.2, y, 9.86), chamfer=.04)
    for x, y in ((.7, -6.0), (-.7, -4.6), (.0, 12.0)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, 3.4 if y > 0 else 3.1), h=1.0, r=.025, lean=math.pi)
    g = a.part('Hull_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    for s in (-1, 1):
        k.greebles(g, (s * 4.4, -9.6, 9.31), (1, 0, 0), (0, 1, 0), (1.6, 5.0), 6, 77 + s, height=(.08, .22), vents=v,
                   avoid=[(TH_TURRET, 2.3)])
        k.greebles(g, (s * 8.3, -2.0, 8.51), (1, 0, 0), (0, 1, 0), (1.6, 14.0), 10, 79 + s, height=(.06, .2), vents=v,
                   avoid=[((s * 8.3, -3.0, 8.5), 1.2), ((-TH_BAY_X, 4.4, 8.5), .8)])


def theia(a, detail=False):
    """Theia, the escort carrier (Hyperion's mini-boss variant): see the module docstring."""
    K.suffixed(a)
    _th_hull(a)
    _th_bays(a)
    _th_turret(a)
    _th_island(a)
    _th_engines(a)
    _th_podbay(a)
    _th_detail(a)
    K.tone(a, 'Pod_bay', k=.9)
    k.clean(a)


# ============================================================================= Coeus (gunship / artillery, 40.3 m)
CO = [  # y, hw, z0, z1, ct, cb, bul, zm
    (-19.9, 4.4, 5.2, 8.6, .9, 1.0, 0, 6.8),
    (-19.0, 7.4, 4.4, 9.6, 1.3, 1.3, .3, 6.8),
    (-13.6, 8.4, 4.0, 10.0, 1.6, 1.5, .5, 6.8),
    (-10.6, 8.4, 4.1, 10.0, 1.6, 1.5, .5, 6.8),
    (-8.6, 6.4, 4.4, 9.8, 1.4, 1.4, .3, 6.8),
    (3.0, 6.6, 4.2, 9.9, 1.4, 1.4, .35, 6.8),
    (6.6, 7.8, 3.6, 10.2, 1.6, 1.5, .45, 6.8),
    (16.8, 7.8, 3.6, 10.2, 1.6, 1.5, .45, 6.8),
    (18.6, 6.4, 4.2, 9.6, 1.4, 1.3, .2, 6.9),
]
CO_CASE = [  # the armoured citadel under the artillery turret
    (-12.4, 3.6, 9.6, 10.4, .5, .05, 0, 10.0),
    (-10.6, 4.8, 9.6, 11.3, .7, .05, 0, 10.4),
    (-.6, 4.8, 9.6, 11.3, .7, .05, 0, 10.4),
    (.8, 3.8, 9.6, 10.7, .5, .05, 0, 10.2),
]
CO_TURRET = (0, -5.4, 11.3)
CO_VLAS = [(3.3, -4.0), (-3.3, -4.0)]
CO_MAIN = (0, 18.6, 6.9)


def _co_hull(a):
    """Coeus's hull: a heavy armoured gunship (a broad ram-faced hammerhead, a narrower neck, the wide engine block),
    belt armour plates in two rows, the armoured citadel the turret stands on, the stub wings to the outboard
    engines, the keel aft, plate seams, windows and greebles."""
    loft(a.part('Hull', 'Team'), CO, step=1.8, inset=(.12, -.03))
    loft(a.part('Hull_citadel', 'Armor'), CO_CASE, step=1.6, inset=(.1, -.025))
    ar = a.part('Armour_plates', 'Armor')
    for s in (-1, 1):
        for y in (-17.2, -14.4, -11.6, -5.6, -2.6, .4, 9.0, 12.0, 15.0):
            r = interp(CO, y)
            x = s * (r[1] + r[6] + .08)
            k.block(ar, (.22, 2.6, 1.6), loc=(x, y, r[7] + 1.0), rot=(0, s * .12, 0), chamfer=.05, ends=(True, True))
            k.block(ar, (.22, 2.6, 1.1), loc=(x - s * .06, y, r[7] - .75), rot=(0, -s * .2, 0), chamfer=.05,
                    ends=(True, True))
        # Hammerhead shoulder plates and the brow strips.
        k.block(ar, (2.2, 6.0, .2), loc=(s * 6.6, -15.6, 9.95), rot=(0, s * -.4, 0), chamfer=.05)
    # Ram prow: a stack of angled plates on the face, the sensor slit over it.
    for j, z in enumerate((5.7, 6.7, 7.7)):
        k.block(ar, (6.4 - j * .6, .5, .95), loc=(0, -19.95 + j * .1, z), chamfer=.06, taper=(.9, .7))
    a.part('Prow_slits', 'Energy').box((4.0, .06, .12), loc=(0, -19.95, 8.45), bevel=0)
    for s in (-1, 1):
        a.part('Windows', 'Lamp').box((1.6, .06, .18), loc=(s * 4.8, -19.25, 8.7), rot=(0, 0, s * .45), bevel=0)
    # Stub wings to the outboard engines (Wings).
    wg = a.part('Wings', 'Team')
    for s in (-1, 1):
        k.sharp_loft(wg, [[(s * 8.1, 8.6, 6.3), (s * 8.1, 14.6, 6.3), (s * 8.1, 14.6, 7.3), (s * 8.1, 8.6, 7.3)],
                          [(s * 9.5, 10.0, 6.4), (s * 9.5, 13.8, 6.4), (s * 9.5, 13.8, 7.1), (s * 9.5, 10.0, 7.1)]],
                     chamfer=.05)
    loft(a.part('Hull_keel', 'Armor'), [(1.6, .6, 3.5, 4.2, .2, .2, 0, 3.8), (2.8, 1.3, 3.1, 4.2, .3, .3, 0, 3.6),
                                       (14.0, 1.3, 3.1, 3.9, .3, .3, 0, 3.5), (15.4, .6, 3.4, 3.9, .2, .2, 0, 3.7)],
         step=2.0, chamfer=.06, inset=(.08, -.02))
    tr = a.part('Hull_trim', 'Undercarriage')
    for s in (-1, 1):
        band(tr, [(s * (r[1] + r[6] + .03), r[0], r[7] + .12) for r in stations(CO, 2.5)][1:-1], .14, .1)
    g = a.part('Hull_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    for s in (-1, 1):
        k.greebles(g, (s * 5.2, 10.6, 10.21), (1, 0, 0), (0, 1, 0), (2.6, 11.0), 14, 81 + s, height=(.1, .3), vents=v)
        k.greebles(g, (s * 3.6, -16.4, 10.01), (1, 0, 0), (0, 1, 0), (2.2, 4.4), 6, 83 + s, height=(.08, .25),
                   vents=v)
        k.greebles(g, (s * 4.4, 10.0, 3.59), (1, 0, 0), (0, -1, 0), (2.4, 12.0), 10, 85 + s, height=(.08, .25))
        k.greebles(g, (s * 4.6, -15.0, 3.99), (1, 0, 0), (0, -1, 0), (3.0, 7.0), 8, 87 + s, height=(.08, .25))
    win = a.part('Windows', 'Lamp')
    for s in (-1, 1):
        for i in range(10):
            y = 6.6 + i * 1.1
            r = interp(CO, y)
            win.box((.04, .4, .18), loc=(s * (r[1] + r[6] * .3 + .3), y, r[7] + 2.4), bevel=0)


CO_TOWER_X = -1.8      # the spotting tower stands off the centreline to the right (the gun's arc stays clear)


def _co_tower(a):
    """The spotting tower aft, off the centreline to the right: an armoured citadel with vision slits, the bridge,
    the rotating fire-control array (Radar), the rangefinder arms, whip antennas, beacons; deck plates and greebles
    on the hammerhead and the engine block."""
    dx = CO_TOWER_X
    loft(a.part('Superstructure', 'Team'), [(4.6, 2.2, 10.0, 10.6, .3, .05, 0, 10.2), (6.0, 3.2, 10.0, 12.4, .55, .05, 0, 11.0),
                                            (12.6, 3.0, 10.0, 12.4, .55, .05, 0, 11.0),
                                            (14.0, 2.2, 10.0, 11.2, .4, .05, 0, 10.6)], step=1.4, inset=(.08, -.02),
         dx=dx)
    loft(a.part('Bridge', 'Armor'), [(6.6, 1.8, 12.3, 12.5, .2, .05, 0, 12.4), (7.6, 2.4, 12.3, 13.3, .3, .05, 0, 12.8),
                                     (11.4, 2.3, 12.3, 13.3, .3, .05, 0, 12.8), (12.2, 1.8, 12.3, 12.8, .25, .05, 0, 12.5)],
         step=1.2, inset=(.06, -.015), dx=dx)
    a.part('Glass', 'Glass').limb((dx + 2.0, 7.12, 12.85), (dx - 2.0, 7.12, 12.85), .2, .05, bevel=0)
    for s in (-1, 1):
        a.part('Glass', 'Glass').limb((dx + s * 3.25, 6.6, 11.8), (dx + s * 3.15, 11.6, 11.8), .05, .18, bevel=0)
    ms = a.part('Masts', 'Armor')
    k.sharp_loft(ms, [[(dx + .6, 8.8, 13.2), (dx - .6, 8.8, 13.2), (dx - .6, 10.8, 13.2), (dx + .6, 10.8, 13.2)],
                      [(dx + .35, 9.3, 14.6), (dx - .35, 9.3, 14.6), (dx - .35, 10.3, 14.6), (dx + .35, 10.3, 14.6)]],
                 chamfer=.04)
    rp = a.pivot('Radar', (dx, 9.8, 14.62))
    ra = a.part('Radar_array', 'Steel', rp)
    k.block(ra, (3.2, .22, 1.1), loc=(0, 0, .7), chamfer=.03, ends=(True, True))
    a.part('Radar_face', 'Undercarriage', rp).box((3.0, .03, .95), loc=(0, -.13, .7), bevel=0)
    k.lathe(a.part('Radar_base', 'Armor', rp), [(.3, 0), (.3, .12), (.2, .16)], seg=10)
    for s in (-1, 1):
        a.part('Masts', 'Armor').limb((dx + s * 2.3, 8.0, 12.4), (dx + s * 3.5, 7.4, 12.7), .16, .16, bevel=0)
        k.lathe(a.part('Rangefinder', 'Steel'), [(0, -.2), (.16, -.18), (.18, .18), (0, .22)],
                loc=(dx + s * 3.65, 7.4, 12.75), rot=(0, R90, 0), seg=10)
        K.whip_antenna(a.part('Antennas', 'Steel'), (dx + s * 1.6, 12.6, 12.4), h=1.3, r=.025)
        K.beacon(a, (dx + s * 2.4, 13.4, 12.4), r=.1)
    for s in (-1, 1):
        windows(a, 'Windows', dx + s * 3.22, 8.0, 12.0, 11.2, .8, s, h=.15, w=.35)
    # Deck plates on the hammerhead and the engine block's left (the tower's other side).
    pl = a.part('Deck_plates', 'Armor')
    for y in (-17.0, -14.6):
        k.block(pl, (3.4, 2.1, .12), loc=(0, y, 10.05), chamfer=.03)
    for y in (5.6, 8.2, 10.8, 13.4, 16.0):
        k.block(pl, (2.2, 2.3, .12), loc=(3.6, y, 10.25), chamfer=.03)
    hz = a.part('Deck_hazard', 'Hazard')
    for y in (4.4, 17.2):
        hz.box((2.4, .14, .02), loc=(3.6, y, 10.22), bevel=0)
    g = a.part('Hull_greebles', 'Team')
    v = a.part('Vents', 'Undercarriage')
    k.greebles(g, (3.6, 10.8, 10.32), (1, 0, 0), (0, 1, 0), (2.0, 11.0), 12, 91, height=(.08, .3), vents=v)
    for s in (-1, 1):
        k.greebles(g, (s * 6.4, -15.0, 10.01), (1, 0, 0), (0, 1, 0), (1.4, 6.0), 6, 93 + s, height=(.08, .25),
                   avoid=[((-5.6, -12.4, 10.0), 1.0)])


def _co_artillery(a):
    """Turret (main_laser's node; Coeus's main weapon is the heavy coilgun): the barbette ring, a wide low house
    (sloped glacis, cheek lockers, the gunner's cupola, the rear capacitor bustle with its grille), the long coil
    barrel (Main_cannon: a square rail housing in fourteen coil collars, glowing field slots, the field-shaping
    crown) in its mantlet, and Muzzle_main at the crown."""
    x, y, z = CO_TURRET
    q = 1.2
    k.lathe(a.part('Turret_barbette', 'Armor'), [(2.7 * q, -.1), (2.7 * q, .2), (2.55 * q, .3)], loc=(x, y, z), seg=32)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .3), (0, 0, 1), 2.6 * q, 28, r=.05, h=.05)
    t = a.pivot('Turret', (x, y, z + .3))
    house = a.part('Turret_house', 'Team', t)
    rings = [
        (0, [(-1.8, -2.6), (1.8, -2.6), (2.6, -1.2), (2.6, 2.8), (2.1, 3.4), (-2.1, 3.4), (-2.6, 2.8), (-2.6, -1.2)]),
        (1.3, [(-1.5, -1.7), (1.5, -1.7), (2.3, -.8), (2.3, 2.6), (1.85, 3.1), (-1.85, 3.1), (-2.3, 2.6), (-2.3, -.8)]),
        (1.75, [(-1.1, -1.0), (1.1, -1.0), (1.8, -.4), (1.8, 2.3), (1.45, 2.7), (-1.45, 2.7), (-1.8, 2.3),
                (-1.8, -.4)])]
    k.sharp_loft(house, [[(px * q, py * q, pz * q) for px, py in pts] for pz, pts in rings], chamfer=.07)
    k.inset(house, lambda c, n, f: c.z > .2, width=.09, depth=-.02)
    for s in (-1, 1):
        k.block(a.part('Turret_lockers', 'Armor', t), (.5, 3.2, 1.1), loc=(s * 2.6 * q + s * .2, 1.2, .62),
                chamfer=.05, ends=(True, True))
        for j in range(3):
            a.part('Turret_locker_lines', 'Undercarriage', t).box((.03, .05, .9), loc=(s * (2.6 * q + .46),
                                                                                       .2 + j * 1.0, .62), bevel=0)
    k.lathe(a.part('Turret_cupola', 'Armor', t), [(.55, 0), (.55, .3), (.42, .44), (0, .48)], loc=(1.2, 2.0, 1.75 * q),
            seg=14)
    for j in range(5):
        u = -R90 + (j - 2) * .5
        a.part('Turret_periscopes', 'Steel', t).box((.12, .1, .12), loc=(1.2 + math.cos(u) * .46,
                                                                        2.0 + math.sin(u) * .46, 1.75 * q + .3),
                                                    rot=(0, 0, u), bevel=0)
    k.block(a.part('Turret_bustle', 'Undercarriage', t), (4.0, 1.5, 1.4), loc=(0, 3.4 * q + .6, .8), chamfer=.08,
            ends=(True, True))
    K.grille(a, (0, 3.4 * q + 1.37, .85), 3.0, .9, facing=(0, 1, 0), slats=7, parent=t, frame_mat='Armor')
    zg, L = 1.1, 10.8
    y0 = -2.6 * q + .2
    mc = a.part('Main_cannon', 'Steel', t)
    mc.box((1.0, L, 1.0), loc=(0, y0 - L / 2, zg), bevel=.08)
    coil = a.part('Main_cannon_coils', 'Undercarriage', t)
    for j in range(14):
        coil.box((1.42, .34, 1.42), loc=(0, y0 - .9 - j * .72, zg), bevel=.06)
    glow = a.part('Main_cannon_glow', 'TeamGlow', t)
    for s in (-1, 1):
        glow.box((.04, L - 1.8, .14), loc=(s * .52, y0 - L / 2 - .3, zg), bevel=0)
        glow.box((.14, L - 1.8, .04), loc=(0, y0 - L / 2 - .3, zg + s * .52), bevel=0)
    k.block(a.part('Main_cannon_mantlet', 'Armor', t), (2.2, 1.0, 1.9), loc=(0, y0 + .2, zg), chamfer=.08,
            ends=(True, True))
    crown = a.part('Main_cannon_crown', 'Armor', t)
    k.block(crown, (1.6, 1.0, 1.6), loc=(0, y0 - L - .3, zg), chamfer=.1, ends=(True, True))
    for s in (-1, 1):
        crown.box((.26, 1.1, .55), loc=(s * .92, y0 - L - .3, zg), bevel=.03)
        crown.box((.55, 1.1, .26), loc=(0, y0 - L - .3, zg + s * .92), bevel=.03)
    a.part('Main_cannon_lens', 'Energy', t).box((.55, .04, .55), loc=(0, y0 - L - .82, zg), bevel=0)
    a.pivot('Muzzle_main', (0, y0 - L - .9, zg), t)
    K.soot(a, (x, y + y0 - L, z + .3 + zg), radius=.8, k=.25)


def _co_ventral(a, i, x, y):
    """A ventral twin laser battery (Mount_gun at +X, .001 at -X): the race, the faceted house hanging under the
    keel line, two emitters with cooling fins and lens crowns (Las_barrels* / Las_muzzles*); Muzzle_gun[.001]
    between the lenses, per-barrel muzzles."""
    tag = '' if i == 0 else f'_{i:03d}'
    z0 = interp(CO, y)[2]
    k.ring(a.part('Las_race' + tag, 'Steel'), [(1.4, .02), (1.55, .02), (1.55, -.1), (1.4, -.12)], loc=(x, y, z0),
           seg=24)
    m = a.pivot(K.name('Mount_gun', i), (x, y, z0 - .08))
    house = a.part('Las_house' + tag, 'Team', m)
    k.sharp_loft(house, [
        [(-1.0, -1.3, 0), (1.0, -1.3, 0), (1.4, -.5, 0), (1.4, 1.1, 0), (-1.4, 1.1, 0), (-1.4, -.5, 0)],
        [(-.75, -1.0, -1.1), (.75, -1.0, -1.1), (1.1, -.4, -1.2), (1.1, .9, -1.2), (-1.1, .9, -1.2),
         (-1.1, -.4, -1.2)]], chamfer=.05)
    k.inset(house, lambda c, n, f: n.z > -.9, width=.07, depth=-.015)
    zg = -.65
    xs = (-.42, .42)
    for bx in xs:
        k.lathe(a.part('Las_barrels' + tag, 'Steel', m), [(0, -1.0), (.19, -1.0), (.19, -3.6), (0, -3.6)],
                loc=(bx, 0, zg), rot=AFT, seg=12)
        for j in range(5):
            a.part('Lbands_barrels' + tag, 'Undercarriage', m).box((.5, .06, .5), loc=(bx, -1.6 - j * .35, zg), bevel=0)
        k.lathe(a.part('Las_muzzles' + tag, 'Armor', m), [(.14, 0), (.27, .08), (.27, .4), (.17, .45)],
                loc=(bx, -3.55, zg), rot=(R90, 0, 0), seg=12)
        a.part('Lens_muzzles' + tag, 'Energy', m).cyl(.14, .03, loc=(bx, -4.0, zg), rot=(R90, 0, 0), seg=10, bevel=0)
    mz = a.pivot(K.name('Muzzle_gun', i), (0, -4.08, zg), m)
    for j, bx in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{j + 1}_gun{tag}', (bx, 0, 0), mz)


def _co_engines(a):
    """Thruster_main: two bells in the aft face (Engine_flame, .001); Thruster_rl / _rr: the outboard engines on the
    stub wings, each a turned nacelle with its intake ring, armour collar and bell (Engine_flame .002 / .003)."""
    pm = a.pivot('Thruster_main', CO_MAIN)
    k.block(a.part('Engine_face', 'Armor', pm), (10.4, 4.6, .3), loc=(0, .05, 0), rot=(R90, 0, 0), chamfer=.08,
            ends=(True, True))
    for i, x in enumerate((2.5, -2.5)):
        r = 1.65
        loc = (x, .2, 0)
        k.ring(a.part('Engine_collars', 'Armor', pm), [(r * 1.08, 0), (r * 1.2, 0), (r * 1.2, .3), (r * 1.08, .32)],
               loc=loc, rot=AFT, seg=22)
        k.lathe(a.part('Nozzles', 'Steel', pm), [(r * .8, .15), (r * .86, .5), (r * 1.0, 1.0), (r * 1.06, 1.25),
                                                 (r * .98, 1.15), (r * .84, .7), (r * .72, .4)], loc=loc, rot=AFT,
                seg=22, caps=(False, False))
        a.part('Nozzle_glow', 'Energy', pm).cyl(r * .72, .05, loc=(x, .62, 0), rot=(R90, 0, 0), seg=18, bevel=0)
        K.engine_flame(a, i, (x, 1.45, 0), r, parent=pm)
    for j, (name, s) in enumerate((('Thruster_rl', 1), ('Thruster_rr', -1))):
        p = a.pivot(name, (s * 9.9, 12.0, 6.7))
        tag = '_l' if s > 0 else '_r'
        k.lathe(a.part('Engines' + tag, 'Team', p), [(0, -6.4), (.45, -6.3), (1.0, -5.6), (1.4, -4.2), (1.5, -2.0),
                                                     (1.5, 4.6), (1.38, 5.6), (1.2, 6.2)], rot=AFT, seg=22)
        k.inset(a.part('Engines' + tag, 'Team', p), lambda c, n, f: abs(n.y) < .5, width=.08, depth=-.02)
        k.ring(a.part('Engine_rings' + tag, 'Armor', p), [(1.51, -.35), (1.64, -.35), (1.64, .35), (1.51, .35)],
               loc=(0, -1.6, 0), rot=AFT, seg=22)
        k.lathe(a.part('Engine_intake' + tag, 'Undercarriage', p), [(0, -6.7), (.4, -6.4), (.75, -5.8)], rot=AFT,
                seg=14)
        k.lathe(a.part('Nozzles' + tag, 'Steel', p), [(.95, 6.0), (1.05, 6.5), (1.18, 7.1), (1.1, 7.05), (.8, 6.4)],
                rot=AFT, seg=18, caps=(False, False))
        a.part('Nozzle_glow' + tag, 'Energy', p).cyl(.8, .05, loc=(0, 6.3, 0), rot=(R90, 0, 0), seg=16, bevel=0)
        K.engine_flame(a, 2 + j, (0, 7.1, 0), 1.15, parent=p)
        K.lamp(a, (s * 1.5, -3.0, 0), facing=(s, 0, 0), r=.13, parent=p, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')


def _co_detail(a):
    """Coeus's small parts: armour ribs on the engine block, RCS quads at the corners, docking hatches, nav lights,
    an asymmetric ammunition hoist and crane on the citadel's left, a spotting radome on the right shoulder, an
    antenna farm aft on the right, vents and plates on the engine block, belly antennas."""
    rib = a.part('Hull_ribs', 'Armor')
    for s in (-1, 1):
        for y in (7.8, 10.0, 12.2, 14.4, 16.4):
            r = interp(CO, y)
            rib.box((.18, .32, (r[3] - r[2]) * .45), loc=(s * (r[1] + r[6] + .05), y, r[7] - 1.2), bevel=.03)
        for y in (-17.6, 17.4):
            r = interp(CO, y)
            p = (s * (r[1] + r[6] + .05), y, r[7] + 1.4)
            k.block(a.part('Rcs_pods', 'Armor'), (.5, 1.3, .9), loc=(p[0] + s * .2, p[1], p[2]), chamfer=.05,
                    ends=(True, True))
            for dz in (-.25, .25):
                k.lathe(a.part('Rcs_nozzles', 'Steel'), [(.06, 0), (.08, .05), (.12, .16), (.1, .17)],
                        loc=(p[0] + s * .45, p[1], p[2] + dz), rot=K.rot_to((s, 0, 0)), seg=8, caps=(True, False))
        K.hatch_rect(a, (s * 7.0, -6.6, 8.2), size=(.9, 1.0), normal=(s, 0, 0))
        K.lamp(a, (s * 8.3, -16.0, 8.8), facing=(s, 0, 0), r=.12, guard=False,
               glow='LavaGlow' if s > 0 else 'SignalGreen')
    # The ammunition sponson on the left flank (asymmetric): a plated box with its hoist door and lit slit, the crane
    # on top swung out over the side.
    sp = a.part('Hoist', 'Team')
    k.sharp_loft(sp, [[(6.2, -7.4, 6.4), (6.2, -7.4, 9.0), (7.4, -7.0, 8.8), (7.6, -7.0, 6.7)],
                      [(6.2, -.6, 6.4), (6.2, -.6, 9.0), (7.4, -1.0, 8.8), (7.6, -1.0, 6.7)]], chamfer=.06)
    k.inset(sp, lambda c, n, f: n.x > .5, width=.08, depth=-.02)
    a.part('Hoist_door', 'Undercarriage').box((.04, 1.6, 1.2), loc=(7.56, -4.0, 7.6), bevel=0)
    a.part('Windows', 'Lamp').box((.04, 2.4, .12), loc=(7.5, -4.0, 8.55), bevel=0)
    cr = a.part('Crane', 'Hazard')
    cr.cyl(.18, 1.2, loc=(6.8, -2.0, 9.5), seg=10, bevel=0)
    cr.limb((6.8, -2.0, 10.0), (9.2, -4.6, 10.6), .16, .16, bevel=0)
    a.part('Crane_hook', 'Steel').limb((9.2, -4.6, 10.6), (9.2, -4.6, 9.4), .03, .03, bevel=0)
    # Spotting radome on the right shoulder; antenna farm aft on the right.
    a.part('Radome_base', 'Armor').cyl(.45, .4, loc=(-5.6, -12.4, 10.2), seg=14, bevel=.03)
    k.lathe(a.part('Radome', 'PlasterWhite'), [(.62, 0), (.64, .2), (.5, .55), (.25, .72), (0, .76)],
            loc=(-5.6, -12.4, 10.4), seg=18)
    for dx, dy, h in ((0, 0, 1.6), (.6, .8, 1.2), (-.5, 1.5, 1.4), (.3, 2.3, 1.0)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (-5.4 + dx, 14.0 + dy, 10.2), h=h, r=.025)
    k.lathe(a.part('Dishes', 'Steel'), [(0, 0), (.45, .08), (.48, .11), (0, .05)], loc=(-4.4, 16.4, 10.6),
            rot=(R90 * .5, 0, -.6), seg=14)
    a.part('Masts', 'Armor').limb((-4.4, 16.4, 10.2), (-4.4, 16.4, 10.6), .12, .12, bevel=0)
    pl = a.part('Engine_plates', 'Armor')
    for s in (-1, 1):
        for y in (8.0, 10.6, 13.2):
            k.block(pl, (1.4, 2.2, .14), loc=(s * 5.6, y, 10.26), chamfer=.04)
    for x, y in ((.8, 5.0), (-.8, 6.4), (0, -12.0)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, 3.2 if y > 2 else 3.85), h=1.0, r=.025, lean=math.pi)


def coeus(a, detail=False):
    """Coeus, the gunship / artillery cruiser (Hyperion's mini-boss variant): see the module docstring."""
    K.suffixed(a)
    _co_hull(a)
    _co_tower(a)
    _co_artillery(a)
    for i, (x, y) in enumerate(CO_VLAS):
        _co_ventral(a, i, x, y)
    _co_engines(a)
    _co_detail(a)
    K.tone(a, 'Thruster_rl', k=.92)
    K.tone(a, 'Thruster_rr', k=.92)
    k.clean(a)


BUILDERS = {
    'hyperion': (hyperion, dict(ao_distance=1.4, ao_strength=.55, grime_height=.0, ground=False)),
    'theia': (theia, dict(ao_distance=1.0, ao_strength=.55, grime_height=.0, ground=False)),
    'coeus': (coeus, dict(ao_distance=1.0, ao_strength=.55, grime_height=.0, ground=False)),
}
