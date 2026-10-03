"""Prompt 35 wave 12 (lane C): the electronic-warfare tower and its radar-spoofer branch rebuilt from scratch (specs:
Tools/blender/specs/ew_tower.json, ew_tower_b.json).

Both stand on the same site, laid out as the old tower family (ew_tower_a, trimmed in wave 2, keeps the old build:
its pad, mast axis, platform height, shelter, generator, drums and reel are where this site has them, so the three
read as one tower and its branches):

- the 4 x 4 m cast pad with a chamfered edge, slab joints, a chequer-plate cable trench and the earthing rod;
- a galvanised four-legged lattice mast (angle legs on bolted base plates over concrete pedestals, K / X bracing in
  five bays, horizontal struts), the climbing ladder with its safety-cage hoops, the cable ladder up one face with
  its feeder bundle, mid-height and top red obstruction lights;
- the head platform: grating deck with toe boards (Team), railing, the bearing housing under the turning head;
- the equipment shelter (corner posts, Team skin with ribbed panels, a pale roof with its seams, the door with
  hinges and handle, window, wall lamp, stencil), the air conditioner with its fan guard, the gland plate and the
  cable run to the mast; a skid diesel generator (louvres, Team service doors, exhaust stack with rain cap, control
  panel); two fuel drums, a cable reel, the warning sign, an extinguisher, grass.

The heads turn on `Radar` (the old pivot, (0.3, -0.25, 7.07)), with `Muzzle_main` on the face that jams / spoofs:

- ew_tower (Pole-21 / R-934-style sector jammer): three directional panel arrays round a steel column (white radome
  faces with their element seams, Team back boxes with cooling fins, the cable glands), the biggest facing -Y with
  `Muzzle_main` at its face; two datalink dishes on arms, the log-periodic antenna on top, a GNSS puck, a whip with
  the red light;
- ew_tower_b (DRFM radar spoofer): one big planar array leaning back on a trunnion yoke (4 x 3 tiles, each a white
  radome in its frame), the back with the electronics box, cooling fans and the elevation jack, the two side
  horns that receive the radar, the sun shade over the top edge.

Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
TOP = .24                    # the pad's top
MX, MY = .3, -.25            # the mast axis (the old file's)
HW0, HW1, Z1 = .6, .28, 6.6  # leg half-spread at the foot / top, the platform level
ZR = Z1 + .47                # the Radar pivot (the old file's 7.07)
SX, SY, SW, SD, SH = -.62, 1.3, 1.9, 1.05, 1.3   # the shelter (centre, width, depth, height)


def _leg(sx, sy, z):
    f = (z - TOP) / (Z1 - TOP)
    h = HW0 + (HW1 - HW0) * f
    return (MX + sx * h, MY + sy * h, z)


def _pad(a):
    k.extrude(a.part('Pad', 'Concrete'), [(-2.0, -1.55), (-1.55, -2.0), (1.55, -2.0), (2.0, -1.55), (2.0, 1.55),
                                          (1.55, 2.0), (-1.55, 2.0), (-2.0, 1.55)], .3, loc=(0, 0, TOP - .15),
              axis='Z', chamfer=.05, corner=.04, taper=(.985, .985))
    j = a.part('Pad_joints', 'Undercarriage')
    for x in (-.9, 1.25):
        j.box((.025, 3.9, .008), loc=(x, 0, TOP + .002), bevel=0)
    j.box((3.9, .025, .008), loc=(0, .35, TOP + .002), bevel=0)
    # The cable trench from the shelter to the mast: chequer plates on a steel edge.
    tr = a.part('Trench_plates', 'Steel')
    for i in range(4):
        tr.box((.36, .4, .02), loc=(.05 + i * .0, .55 - i * .42, TOP + .01), bevel=0)
    a.part('Trench_edge', 'Undercarriage').box((.42, 1.7, .012), loc=(.05, -.08, TOP + .004), bevel=0)
    # The earthing rod beside a leg with its copper strap.
    ex, ey = MX + HW0 + .3, MY - HW0 - .1
    a.part('Earth_rod', 'Gilded').cyl(.02, .25, loc=(ex, ey, TOP + .1), seg=6, bevel=0)
    a.part('Earth_rod', 'Gilded').tube([(ex, ey, TOP + .2), (MX + HW0, MY - HW0, TOP + .25)], .012, seg=4)


def _mast(a):
    legs = a.part('Mast', 'Steel')
    br = a.part('Mast_braces', 'Steel')
    bolts = a.part('Kit_bolts', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = MX + sx * HW0, MY + sy * HW0
            k.block(a.part('Footings', 'Concrete'), (.44, .44, .2), loc=(x, y, TOP + .06), chamfer=.03,
                    taper=(.85, .85))
            a.part('Base_plates', 'Steel').box((.26, .26, .03), loc=(x, y, TOP + .175), bevel=0)
            bolts.bolts([(x + sx * .09, y - sy * .09, TOP + .2), (x - sx * .09, y + sy * .09, TOP + .2)], r=.024, h=.035,
                        seg=6, bevel=0)
            # The angle leg: an L section climbing the taper, its heel outwards.
            p0, p1 = _leg(sx, sy, TOP + .18), _leg(sx, sy, Z1 + .02)
            legs.limb(p0, p1, .08, .08, bevel=0)
            legs.limb((p0[0] - sx * .03, p0[1], p0[2]), (p1[0] - sx * .03, p1[1], p1[2]), .02, .1, bevel=0)
    zs = [TOP + .3, 1.6, 2.85, 4.0, 5.05, Z1 - .05]
    faces = (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1)))
    for b, (z0, z1) in enumerate(zip(zs, zs[1:])):
        for (ax, ay), (bx, by) in faces:
            if b < 2:          # the lower bays: K bracing to the strut's middle
                pa, pb = _leg(ax, ay, z0), _leg(bx, by, z0)
                mid = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, z0)
                br.limb(_leg(ax, ay, z1), mid, .045, .045, bevel=0)
                br.limb(_leg(bx, by, z1), mid, .045, .045, bevel=0)
            else:              # the upper bays: X bracing
                br.limb(_leg(ax, ay, z0), _leg(bx, by, z1), .04, .04, bevel=0)
                br.limb(_leg(bx, by, z0), _leg(ax, ay, z1), .04, .04, bevel=0)
            br.limb(_leg(ax, ay, z1), _leg(bx, by, z1), .05, .05, bevel=0)
    # The ladder up the rear face (+Y) with its safety-cage hoops; the cable ladder up the left face with feeders.
    ly = MY + HW0 + .12
    K.ladder(a.part('Mast_ladder', 'Steel'), (MX, ly, TOP + .2), (MX, MY + HW1 + .12, Z1 - .02), width=.36, step=.48)
    cage = a.part('Ladder_cage', 'Steel')
    for i in range(5):
        z = 2.2 + i * .9
        f = (z - TOP) / (Z1 - TOP)
        y = ly + (MY + HW1 + .12 - ly) * f
        cage.tube([(MX - .22, y, z), (MX - .3, y + .3, z), (MX, y + .42, z), (MX + .3, y + .3, z), (MX + .22, y, z)],
                  .012, seg=3, caps=False)
    for dx in (-.28, .28):
        y0 = ly + .32
        f = (Z1 - .4 - 2.2) / (Z1 - TOP)
        cage.tube([(MX + dx, y0, 2.2), (MX + dx, y0 + (MY + HW1 - MY - HW0) * f, Z1 - .45)], .01, seg=3, caps=False)
    cx = .12
    a.part('Cable_ladder', 'Steel').tube([(_leg(1, 1, TOP + .3)[0] + cx, MY + .1, TOP + .3),
                                          (_leg(1, 1, Z1)[0] + cx, MY + .1, Z1 - .1)], .02, seg=4)
    a.part('Cable_run', 'Rubber').tube([(.1, .6, TOP + .05), (_leg(1, 1, TOP + .3)[0] + cx + .05, MY + .15, TOP + .4),
                                        (_leg(1, 1, Z1)[0] + cx + .05, MY + .15, Z1 - .15), (MX + .2, MY, Z1 + .3)],
                                       .04, seg=5)
    for z in (1.4, 2.8, 4.2, 5.6):
        f = (z - TOP) / (Z1 - TOP)
        x = MX + HW0 + (HW1 - HW0) * f + cx + .05
        a.part('Cable_clamps', 'Steel').box((.09, .14, .04), loc=(x, MY + .13, z), bevel=0)
    # Obstruction lights: one at mid height, two on the platform corners.
    red = a.part('Obstruction_lights', 'LavaGlow')
    p = _leg(1, -1, 3.45)
    a.part('Light_brackets', 'Steel').box((.14, .14, .05), loc=(p[0] + .07, p[1] - .07, 3.4), rot=(0, 0, .78), bevel=0)
    red.sphere(.06, loc=(p[0] + .1, p[1] - .1, 3.47), seg=6, rings=4)


def _platform(a):
    e = .62
    k.block(a.part('Platform', 'Armor'), (2 * e + .06, 2 * e + .06, .1), loc=(MX, MY, Z1 + .05), chamfer=.02)
    g = a.part('Grating', 'Undercarriage')
    for i in range(6):
        g.box((2 * e - .1, .04, .012), loc=(MX, MY - e + .12 + i * .2, Z1 + .105), bevel=0)
    K.railing(a.part('Railing', 'Steel'), [(MX - e, MY - e, Z1 + .1), (MX + e, MY - e, Z1 + .1),
                                           (MX + e, MY + e, Z1 + .1), (MX - e + .45, MY + e, Z1 + .1)],
              h=.8, post=.62, r=.022)
    K.railing(a.part('Railing', 'Steel'), [(MX - e, MY + e - .05, Z1 + .1), (MX - e, MY - e, Z1 + .1)],
              h=.8, post=.62, r=.022)
    kick = a.part('Kick_plates', 'Team')
    for (x0, y0, x1, y1) in ((-e, -e, e, -e), (e, -e, e, e), (-e, -e, -e, e)):
        L = math.hypot(x1 - x0, y1 - y0)
        kick.box((.02 if x0 == x1 else L, L if x0 == x1 else .02, .12),
                 loc=(MX + (x0 + x1) / 2, MY + (y0 + y1) / 2, Z1 + .16), bevel=0)
    red = a.part('Obstruction_lights', 'LavaGlow')
    for sx, sy in ((-1, -1), (1, 1)):
        a.part('Light_brackets', 'Steel').cyl(.03, .12, loc=(MX + sx * e, MY + sy * e, Z1 + .96), seg=6, bevel=0)
        red.sphere(.065, loc=(MX + sx * e, MY + sy * e, Z1 + 1.06), seg=6, rings=4)
    # The bearing housing under the turning head and its bolted ring.
    k.lathe(a.part('Bearing', 'Armor'), [(.36, 0), (.36, .08), (.3, .1), (.3, .32), (.34, .34), (.34, .37), (0, .37)],
            loc=(MX, MY, Z1 + .1), seg=12, worn=(1, 4, 5))


def _shelter(a):
    zs = TOP + .11
    for x in (-1, 1):
        a.part('Shelter_blocks', 'Concrete').box((.3, SD + .1, .14), loc=(SX + x * (SW / 2 - .25), SY, TOP + .05),
                                                 bevel=0)
    sh = a.part('Shelter', 'Team')
    k.block(sh, (SW, SD, SH), loc=(SX, SY, zs + SH / 2), chamfer=.04, ends=(True, True))
    rib = a.part('Shelter_ribs', 'Team')
    for i in range(5):
        x = SX - SW / 2 + .25 + i * .36
        rib.box((.05, .02, SH - .3), loc=(x, SY + SD / 2 + .01, zs + SH / 2), bevel=0)
    for i in range(3):
        y = SY - SD / 2 + .2 + i * .32
        rib.box((.02, .05, SH - .3), loc=(SX + SW / 2 + .01, y, zs + SH / 2), bevel=0)
    fr = a.part('Shelter_frame', 'Armor')
    for x in (-1, 1):
        for y in (-1, 1):
            fr.box((.09, .09, SH + .04), loc=(SX + x * (SW / 2 - .02), SY + y * (SD / 2 - .02), zs + SH / 2), bevel=0)
            fr.box((.13, .13, .08), loc=(SX + x * (SW / 2 - .02), SY + y * (SD / 2 - .02), zs + SH + .02), bevel=0)
    roof = a.part('Shelter_roof', 'Medical')
    k.block(roof, (SW + .06, SD + .06, .1), loc=(SX, SY, zs + SH + .01), chamfer=.025)
    for f in (-.33, 0, .33):
        roof.box((.035, SD + .07, .025), loc=(SX + f * SW, SY, zs + SH + .07), bevel=0)
    fy = SY - SD / 2
    k.block(a.part('Shelter_door', 'Armor'), (.68, .04, 1.08), loc=(SX - .45, fy - .012, zs + .56), chamfer=.01)
    hg = a.part('Kit_hinges', 'Steel')
    for z in (.3, .85):
        hg.box((.04, .04, .12), loc=(SX - .8, fy - .03, zs + z), bevel=0)
    K.handle(a.part('Kit_handles', 'Steel'), (SX - .2, fy - .04, zs + .55), (SX - .2, fy - .04, zs + .7), (0, -1, 0),
             h=.05, r=.012)
    a.part('Shelter_step', 'Steel').box((.8, .34, .05), loc=(SX - .45, fy - .2, TOP + .04), bevel=0)
    a.part('Wall_lamp_base', 'Steel').box((.16, .06, .2), loc=(SX + .12, fy - .03, zs + 1.15), bevel=0)
    a.part('Wall_lamp', 'Lamp').box((.12, .05, .12), loc=(SX + .12, fy - .07, zs + 1.13), bevel=0)
    gl = a.part('Shelter_window', 'Glass')
    gl.box((.42, .02, .26), loc=(SX + .55, fy - .012, zs + .82), bevel=0)
    a.part('Shelter_frame', 'Armor').box((.5, .03, .34), loc=(SX + .55, fy - .004, zs + .82), bevel=0)
    a.part('Shelter_stencil', 'Hazard').box((.5, .012, .12), loc=(SX + .55, fy - .012, zs + 1.13), bevel=0)
    # The air conditioner on the -X end: its case, the fan guard, the condensate pipe.
    ax = SX - SW / 2 - .19
    k.block(a.part('Aircon', 'Fuel'), (.34, .72, .62), loc=(ax, SY, zs + .55), chamfer=.03)
    k.lathe(a.part('Aircon_grille', 'Undercarriage'), [(.2, 0), (.22, .02), (.22, .04), (0, .04)],
            loc=(ax - .17, SY, zs + .6), rot=(0, -R90, 0), seg=12)
    fan = a.part('Aircon_fan', 'Steel')
    for i in range(4):
        u = i * TAU / 4
        fan.box((.01, .36, .018), loc=(ax - .19, SY, zs + .6), rot=(u, 0, 0), bevel=0)
    a.part('Kit_cables', 'Rubber').tube([(ax, SY + .3, zs + .25), (ax - .05, SY + .32, TOP + .02)], .012, seg=4)
    # The gland plate on the +X end with the cable run to the mast trench.
    a.part('Cable_entry', 'Armor').box((.05, .4, .32), loc=(SX + SW / 2 + .04, SY - .2, zs + .45), bevel=0)
    a.part('Cable_run', 'Rubber').tube([(SX + SW / 2 + .07, SY - .3, zs + .4), (.1, .78, TOP + .05),
                                        (.1, .6, TOP + .05)], .04, seg=5)
    K.whip_antenna(a.part('Antennas', 'Steel'), (SX - .7, SY + .3, zs + SH + .06), h=1.1, r=.018)
    K.beacon(a, (SX + .75, SY + .3, zs + SH + .06), r=.07)


def _yard(a):
    # The skid diesel generator at the front left.
    gx, gy, gw, gd, gh = -1.15, -1.3, 1.25, .7, .78
    sk = a.part('Generator_skid', 'Steel')
    for s in (-1, 1):
        sk.box((gw + .1, .08, .1), loc=(gx, gy + s * (gd / 2 - .06), TOP + .05), bevel=0)
    gen = a.part('Generator', 'Armor')
    k.block(gen, (gw, gd, gh), loc=(gx, gy, TOP + .1 + gh / 2), chamfer=.04, ends=(True, True))
    k.extrude(gen, [(-gd / 2, 0), (gd / 2, 0), (gd / 2 - .08, .08), (-gd / 2 + .08, .08)], gw - .1,
              loc=(gx, gy, TOP + .1 + gh), axis='X', chamfer=.01)
    for dx in (-.3, .3):
        k.block(a.part('Generator_doors', 'Team'), (.5, .02, gh - .2), loc=(gx + dx, gy - gd / 2 - .005, TOP + .1 + gh / 2),
                chamfer=.006)
        a.part('Kit_handles', 'Steel').box((.03, .03, .12), loc=(gx + dx + .18, gy - gd / 2 - .02, TOP + .56), bevel=0)
    K.grille(a, (gx - gw / 2 - .01, gy, TOP + .1 + gh / 2), .5, .5, facing=(-1, 0, 0), slats=5)
    lv = a.part('Generator_louvres', 'Undercarriage')
    for i in range(4):
        lv.box((.02, .5, .05), loc=(gx + gw / 2 + .01, gy, TOP + .3 + i * .12), rot=(0, .5, 0), bevel=0)
    K.exhaust(a, (gx + .35, gy + .15, TOP + .18 + gh), r=.045, length=.4, direction=(0, 0, 1), muffler=False)
    K.soot(a, (gx + .35, gy + .15, TOP + .6 + gh), radius=.35, k=.4)
    a.part('Generator_panel', 'Undercarriage').box((.3, .02, .22), loc=(gx - .3, gy - gd / 2 - .02, TOP + gh - .05),
                                                   bevel=0)
    a.part('Generator_stripe', 'Hazard').box((gw + .12, .012, .06), loc=(gx, gy - gd / 2 + .02, TOP + .05), bevel=0)
    a.part('Cable_run', 'Rubber').tube([(gx + gw / 2, gy + .2, TOP + .3), (-.2, -.95, TOP + .04), (.05, -.5, TOP + .04),
                                        (.05, .3, TOP + .04)], .035, seg=5)
    # Fuel drums on the -X edge, the cable reel by the shelter, the warning sign, an extinguisher, grass.
    for x, y in ((-1.62, -.3), (-1.55, .32)):
        k.lathe(a.part('Drums', 'BarrelRed'), [(.25, 0), (.26, .02), (.26, .82), (.25, .84), (0, .84)],
                loc=(x, y, TOP), seg=10, worn=(1, 2))
        a.part('Drum_rims', 'Steel').cyl(.265, .03, loc=(x, y, TOP + .55), seg=10, bevel=0)
        a.part('Drum_rims', 'Steel').cyl(.045, .03, loc=(x + .13, y, TOP + .85), seg=6, bevel=0)
    reel = a.part('Cable_reel', 'Wood')
    for dy in (-.2, .2):
        reel.cyl(.42, .05, loc=(1.35, 1.3 + dy, TOP + .43), rot=K.FORWARD, seg=10, bevel=0)
    a.part('Cable_reel_core', 'Rubber').cyl(.3, .36, loc=(1.35, 1.3, TOP + .43), rot=K.FORWARD, seg=10, bevel=0)
    a.part('Cable_reel_hub', 'Steel').cyl(.07, .52, loc=(1.35, 1.3, TOP + .43), rot=K.FORWARD, seg=6, bevel=0)
    a.part('Sign_posts', 'Steel').cyl(.03, .95, loc=(1.6, -1.55, TOP + .47), seg=6, bevel=0)
    k.extrude(a.part('Signs', 'Hazard'), [(-.22, 0), (0, -.22), (.22, 0), (0, .22)], .02, loc=(1.6, -1.585, TOP + .9),
              axis='Y', chamfer=0)
    a.part('Sign_marks', 'Undercarriage').box((.04, .012, .17), loc=(1.6, -1.6, TOP + .92), bevel=0)
    k.lathe(a.part('Extinguisher', 'BarrelRed'), [(.09, 0), (.09, .45), (.05, .52), (0, .54)],
            loc=(SX + .65, SY - SD / 2 - .15, TOP), seg=10, worn=(1,))
    grass = a.part('Tufts', 'Grass', flat=True)
    for i in range(5):
        u = i * 1.37 + .4
        x, y = 1.85 * math.cos(u), 1.85 * math.sin(u)
        grass.cyl(.08, .16, loc=(x, y, TOP + .05), rot=(0, 0, u), seg=4, r2=.01, bevel=0)
    K.dust(a, (0, 0, TOP), radius=2.6, k=.15)


def _site(a):
    _pad(a)
    _mast(a)
    _platform(a)
    _shelter(a)
    _yard(a)


def _array(a, r, centre, yaw, w, h, d, big=False):
    """One sector panel: the Team back box with cooling fins, the white radome face with element seams, glands."""
    rot = (0, 0, yaw)
    m = K.frame(centre, rot)
    k.block(a.part('Array_back', 'Team', r), (w, d, h), loc=centre, rot=rot, chamfer=.03)
    fins = a.part('Array_fins', 'Armor', r)
    for i in range(4 if big else 3):
        z = -h / 2 + (i + 1) * h / (5 if big else 4)
        fins.box((w * .86, .06, .02), loc=K._at(m, (0, d / 2 + .03, z)), rot=rot, bevel=0)
    face = K._at(m, (0, -d / 2 - .02, 0))
    k.block(a.part('Array_radome', 'Medical', r), (w * .94, .04, h * .94), loc=face, rot=rot, chamfer=.015)
    seams = a.part('Array_seams', 'Plaster', r)
    cols = 3 if big else 2
    for i in range(1, cols):
        seams.box((.012, .01, h * .9), loc=K._at(m, (-w * .47 + i * w * .94 / cols, -d / 2 - .045, 0)), rot=rot,
                  bevel=0)
    for j in range(1, 3):
        seams.box((w * .9, .01, .012), loc=K._at(m, (0, -d / 2 - .045, -h * .47 + j * h * .94 / 3)), rot=rot, bevel=0)
    a.part('Array_plugs', 'Undercarriage', r).cyl(.035, .08, loc=K._at(m, (0, d / 2 - .1, -h / 2 - .04)), seg=6,
                                                  bevel=0)
    return face


def ew_tower(a, detail=False):
    """The sector jammer (see the module docstring)."""
    _site(a)
    r = a.pivot('Radar', (MX, MY, ZR))
    head = a.part('Head_steel', 'Steel', r)
    k.lathe(head, [(.36, 0), (.36, .06), (.16, .1), (.16, .22), (.1, .26), (.1, 2.0), (0, 2.0)], seg=12, worn=(1, 3))
    R, d, zc = .3, .14, 1.15
    arm = a.part('Head_arms', 'Armor', r)
    for kk in range(3):
        yaw = kk * TAU / 3
        n = (math.sin(yaw), -math.cos(yaw))
        big = kk == 0
        w, h = (.96, 1.12) if big else (.72, .92)
        for z in (zc - h / 2 + .12, zc + h / 2 - .12):
            arm.limb((0, 0, z), (n[0] * (R + .02), n[1] * (R + .02), z), .06, .06, bevel=0)
        face = _array(a, r, (n[0] * (R + d / 2 + .02), n[1] * (R + d / 2 + .02), zc), yaw, w, h, d, big)
        if big:
            a.pivot('Muzzle_main', (face[0] + n[0] * .03, face[1] + n[1] * .03, face[2]), r)
    # Two datalink dishes on arms between the arrays, facing the rear left and rear right.
    for yaw in (math.pi - .9, math.pi + .9):
        n = (math.sin(yaw), -math.cos(yaw))
        p = (n[0] * .66, n[1] * .66, 1.86)
        arm.limb((0, 0, 1.8), (n[0] * .55, n[1] * .55, 1.84), .06, .06, bevel=0)
        K.dish(a.part('Dishes', 'Medical', r), a.part('Dish_feeds', 'Armor', r), p, r=.26, normal=(n[0], n[1], .15),
               seg=12)
    # The log-periodic antenna on top of the column, the GNSS puck, a whip with the top light.
    zl = 2.04
    head.box((.06, 1.0, .06), loc=(0, -.24, zl), bevel=0)
    k.block(head, (.15, .15, .12), loc=(0, 0, zl - .02), chamfer=.015)
    lp = a.part('LPDA_elements', 'Steel', r)
    for i in range(6):
        half = .5 * .8 ** i
        lp.box((2 * half, .022, .022), loc=(0, .22 - i * .15, zl + (.035 if i % 2 else -.035)), bevel=0)
    k.lathe(a.part('Gnss_puck', 'Medical', r), [(.07, 0), (.07, .02), (.04, .05), (0, .055)], loc=(.12, .1, zl + .03),
            seg=10)
    a.part('Head_whip', 'Steel', r).cyl(.014, .8, loc=(-.08, .14, zl + .44), seg=5, bevel=0)
    a.part('Head_light', 'LavaGlow', r).sphere(.065, loc=(-.08, .14, zl + .87), seg=8, rings=5)
    a.part('Head_cables', 'Rubber', r).tube([(0, .1, .3), (-.2, .18, .7), (-.18, .2, zc - .4)], .025, seg=4)
    k.clean(a)


def ew_tower_b(a, detail=False):
    """The radar spoofer (see the module docstring)."""
    _site(a)
    r = a.pivot('Radar', (MX, MY, ZR))
    head = a.part('Head_steel', 'Steel', r)
    k.lathe(head, [(.36, 0), (.36, .06), (.18, .1), (.18, .22), (.12, .26), (.12, .62), (0, .62)], seg=12,
            worn=(1, 3))
    # The trunnion yoke: two arms up from the turntable to the array's side bearings.
    yoke = a.part('Array_yoke', 'Armor', r)
    zt = 1.25
    for s in (-1, 1):
        yoke.limb((s * .2, 0, .55), (s * 1.34, .05, zt - .25), .14, .12, bevel=0)
        yoke.limb((s * 1.34, .05, zt - .3), (s * 1.34, .05, zt), .14, .14, bevel=0)
        k.lathe(a.part('Array_bearings', 'Steel', r), [(.1, -.08), (.12, -.06), (.12, .06), (.1, .08)],
                loc=(s * 1.34, .05, zt), rot=(0, R90, 0), seg=10)
    k.block(yoke, (2.0, .3, .12), loc=(0, 0, .58), chamfer=.03)
    tilt = math.radians(15)
    rot = (-tilt, 0, 0)
    c = (0, .02, zt + .25)
    m = K.frame(c, rot)
    W, H, D = 2.5, 1.9, .2
    k.block(a.part('Array_panel', 'Team', r), (W, D, H), loc=c, rot=rot, chamfer=.04, ends=(True, True))
    frame = a.part('Array_frame', 'Armor', r)
    tiles = a.part('Array_tiles', 'Medical', r)
    for i in range(4):
        for j in range(3):
            p = K._at(m, (-.9 + i * .6, -D / 2 - .02, -.6 + j * .6))
            k.block(tiles, (.54, .04, .54), loc=p, rot=rot, chamfer=.012)
    for i in range(5):
        frame.box((.03, .03, H - .04), loc=K._at(m, (-1.2 + i * .6, -D / 2 - .03, 0)), rot=rot, bevel=0)
    for j in range(4):
        frame.box((W - .04, .03, .03), loc=K._at(m, (0, -D / 2 - .03, -.9 + j * .6)), rot=rot, bevel=0)
    # The sun shade over the top edge, the two receiving horns on the sides.
    k.block(a.part('Array_shade', 'Armor', r), (W + .1, .34, .04), loc=K._at(m, (0, -.1, H / 2 + .04)),
            rot=(-tilt + .25, 0, 0), chamfer=.01)
    for s in (-1, 1):
        hp = K._at(m, (s * (W / 2 + .14), -.05, .45))
        k.lathe(a.part('Array_horns', 'Medical', r), [(.05, 0), (.06, .06), (.14, .3), (.13, .31), (0, .31)], loc=hp,
                rot=(R90 - tilt, 0, 0), seg=8)
        frame.limb(K._at(m, (s * W / 2, 0, .45)), hp, .05, .05, bevel=0)
    # The back: the electronics box, two cooling fans, the elevation jack to the yoke, cable loops.
    bk = K._at(m, (0, D / 2 + .17, -.25))
    k.block(a.part('Array_box', 'Armor', r), (1.0, .32, .7), loc=bk, rot=rot, chamfer=.03)
    for s in (-1, 1):
        fp = K._at(m, (s * .26, D / 2 + .34, -.2))
        k.lathe(a.part('Array_fans', 'Undercarriage', r), [(.13, 0), (.14, .02), (.14, .04), (0, .04)], loc=fp,
                rot=(-R90 - tilt, 0, 0), seg=10)
        a.part('Array_fan_guard', 'Steel', r).box((.26, .01, .02), loc=K._at(m, (s * .26, D / 2 + .385, -.2)), rot=rot,
                                                  bevel=0)
    a.part('Array_brace', 'Steel', r).limb((0, .1, .62), K._at(m, (0, D / 2 + .1, -.62)), .09, .09, bevel=0)
    a.part('Array_brace', 'Steel', r).limb((0, .1, .62), K._at(m, (0, D / 2 + .06, -.4)), .05, .05, bevel=0)
    a.part('Head_cables', 'Rubber', r).tube([(0, .15, .3), (.2, .3, .5), K._at(m, (.3, D / 2 + .2, -.6))], .03, seg=4)
    a.part('Array_band', 'Team', r).box((.5, .015, .12), loc=K._at(m, (0, D / 2 + .335, .05)), rot=rot, bevel=0)
    a.pivot('Muzzle_main', K._at(m, (0, -D / 2 - .06, 0)), r)
    k.clean(a)


BUILDERS = {
    'ew_tower': (ew_tower, dict(ao_distance=.7, grime_height=.6)),
    'ew_tower_b': (ew_tower_b, dict(ao_distance=.7, grime_height=.6)),
}
