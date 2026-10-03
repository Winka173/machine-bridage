"""Prompt 35 wave 3 (lane B): the laser anti-drone station rebuilt from scratch (spec:
Tools/blender/specs/laser_ad_station.json).

A fixed high-energy laser site of the Iron Beam / DragonFire kind as the Accord sets one up (the def's modelSize
6.0 x 4.0 x 4.6 m): a gravel pad, the power and cooling shelter (a ribbed 20-foot-class container with its rear doors,
locking bars, vents and a camouflage net over its back half), and on a raised pedestal at its front end the beam
director (`Turret`, it turns at 180 degrees a second): the yoke and the round director housing with its big dark
aperture (`Muzzle_main`) and the tracking sensor beside it; on the shelter's roof the chiller with its two fans and
fins; at the rear corner a mast with the search radar panel and the APS sensor pod (`Mount_APS`); the generator skid
alongside with its exhaust stack, the cable trough to the shelter; sandbags round the generator, a fire extinguisher,
a fence of pickets and tape at the front.

Its own body: no shape is shared with the iron_beam vehicle or the other towers.
Runtime nodes kept: `Turret`, `Muzzle_main`, `Mount_APS`; old part names `Base`, `Shelter`, `Shelter_ribs`,
`Shelter_doors`, `Roof`, `Pedestal`, `Yoke`, `Director`, `Aperture`, `Sensor_pod`, `Sensor_lens`, `Coolers`,
`Cooler_fans`, `Fins`, `Mast`, `Search_panel`, `Generator`, `Generator_skid`, `Generator_stack`, `Generator_vents`,
`Cable_trough`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
PAD = .1
SX, SY0, SY1 = 1.1, -1.6, 2.6      # the shelter's half width and its front / rear ends
SH = 2.0                           # the shelter's height above the pad
TOPZ = PAD + SH
TT = (0, -1.0, TOPZ + .55)         # the director's yaw pivot


def _pad(a, rng):
    P.earth_pad(a, [(-1.95, -2.95), (1.9, -2.9), (2.0, 2.9), (-2.0, 2.95)], PAD, mat='Rock', taper=.95,
                bottom=False)
    st = a.part('Stones', 'Rock')
    for j in range(22):
        z = rng.uniform(.05, .1)
        st.box((z * 1.3, z, z * .6), loc=(rng.uniform(-1.8, 1.8), rng.uniform(-2.8, 2.8), PAD + z * .15),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)
    for i in range(8):
        K.dust(a, (rng.uniform(-1.8, 1.8), rng.uniform(-2.7, 2.7), PAD), radius=1.2, k=.25)


def _shelter(a):
    sh = a.part('Shelter', 'Team')
    k.extrude(sh, [(-SX, SY0), (SX, SY0), (SX, SY1), (-SX, SY1)], SH, loc=(0, 0, PAD + SH / 2), axis='Z',
              chamfer=.04, caps=(False, True))
    # Laser-hazard placards on the sides and the doors, a handrail round the roof, the roof ladder at the rear.
    plac = a.part('Placards', 'Hazard')
    for x, y, rz in ((SX + .045, -1.0, R90), (-SX - .045, -1.0, R90), (SX + .045, 2.0, R90), (.45, SY1 + .045, 0)):
        plac.box((.35, .01, .28), loc=(x, y, PAD + 1.55), rot=(0, 0, rz), bevel=0)
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        K.railing(rail, [(s * (SX - .06), SY0 + .9, TOPZ + .06), (s * (SX - .06), SY1 - .1, TOPZ + .06)], h=.6,
                  post=.9, r=.018)
    K.ladder(a.part('Ladders', 'Steel'), (-.6, SY1 + .1, PAD), (-.6, SY1 + .1, TOPZ + .55), width=.4, step=.3)
    # Corrugation ribs down both long sides, the corner castings, the roof panel.
    ribs = a.part('Shelter_ribs', 'Armor')
    n = 14
    for s in (-1, 1):
        for i in range(n):
            y = SY0 + .2 + i * (SY1 - SY0 - .4) / (n - 1)
            ribs.box((.04, .1, SH - .2), loc=(s * (SX + .02), y, PAD + SH / 2), bevel=0)
    cast = a.part('Corner_castings', 'Steel')
    for sx in (-1, 1):
        for y in (SY0 + .08, SY1 - .08):
            for z in (PAD + .08, TOPZ - .08):
                cast.box((.18, .18, .16), loc=(sx * (SX - .07), y, z), bevel=0)
    k.block(a.part('Roof', 'Armor'), (2 * SX - .1, SY1 - SY0 - .1, .06), loc=(0, (SY0 + SY1) / 2, TOPZ + .03),
            chamfer=0)
    # The rear doors with their four locking bars and handles.
    doors = a.part('Shelter_doors', 'Armor')
    for s in (-1, 1):
        K.plate(doors, (SX - .06, .04, SH - .16), loc=(s * SX / 2, SY1 + .02, PAD + SH / 2))
    bars = a.part('Kit_bars', 'Steel')
    for x in (-.8, -.3, .3, .8):
        bars.cyl(.025, SH - .1, loc=(x, SY1 + .06, PAD + SH / 2), seg=6, bevel=0)
        K.handle(bars, (x, SY1 + .07, PAD + 1.0), (x + .15, SY1 + .07, PAD + 1.0), (0, 1, 0), h=.04, r=.01)
    # Side vents and a personnel door with steps on the left side.
    K.grille(a, (SX + .03, .9, PAD + 1.4), .6, .4, facing=(1, 0, 0), slats=4, frame_mat='Armor')
    K.grille(a, (-SX - .03, 1.6, PAD + 1.4), .6, .4, facing=(-1, 0, 0), slats=4, frame_mat='Armor')
    K.door(a, (SX + .03, 0, PAD), size=(.8, 1.75), normal=(1, 0, 0))
    st = a.part('Steps', 'Steel')
    for j in range(2):
        st.box((.4, .8, .04), loc=(SX + .3 - j * .1, 0, PAD + .12 + j * .18), bevel=0)
    a.part('Shelter_band', 'Armor').box((.012, SY1 - SY0 - .3, .25), loc=(-SX - .045, (SY0 + SY1) / 2, PAD + .5),
                                    bevel=0)
    # The camouflage net over the shelter's back half.
    P.camo_net(a, [(-SX - .25, .7, SH + .35), (SX + .25, .7, SH + .35), (SX + .3, SY1 + .2, SH + .2),
                   (-SX - .3, SY1 + .2, SH + .2)], .12, PAD, garnish=10, seed=111, pole_part='Net_poles')


def _cooler(a):
    co = a.part('Coolers', 'Armor')
    k.block(co, (1.7, 1.1, .55), loc=(0, .1, TOPZ + .06 + .275), chamfer=.04)
    fans = a.part('Cooler_fans', 'Undercarriage')
    for x in (-.42, .42):
        k.ring(fans, [(.3, 0), (.36, 0), (.36, .06), (.3, .06)], loc=(x, .1, TOPZ + .61), seg=14)
        for j in range(3):
            fans.box((.58, .05, .015), loc=(x, .1, TOPZ + .66), rot=(0, 0, j * math.pi / 3), bevel=0)
    fins = a.part('Fins', 'Steel')
    for j in range(7):
        fins.box((.012, 1.0, .42), loc=(.875, -.35 + j * .15, TOPZ + .33), rot=(0, 0, R90), bevel=0)
    a.part('Cable_trough', 'Steel').box((.2, 1.8, .1), loc=(-.7, 1.5, TOPZ + .11), bevel=0)
    # Clamps along the trough, lifting lugs on the roof corners.
    for j in range(7):
        a.part('Kit_clamps', 'Undercarriage').box((.26, .04, .05), loc=(-.7, .7 + j * .27, TOPZ + .16), bevel=0)
    for sx in (-1, 1):
        for y in (SY0 + .25, SY1 - .25):
            a.part('Kit_lugs', 'Steel').box((.06, .12, .1), loc=(sx * (SX - .2), y, TOPZ + .11), bevel=0)


def _director(a):
    ped = a.part('Pedestal', 'Armor')
    k.lathe(ped, [(.7, 0), (.7, .06), (.45, .14), (.38, .5), (.5, .55), (0, .55)], loc=(TT[0], TT[1], TOPZ),
            seg=16, worn=(1, 4))
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (TT[0], TT[1], TOPZ + .07), (0, 0, 1), .62, 12, r=.025, h=.03)
    t = a.pivot('Turret', TT)
    yoke = a.part('Yoke', 'Armor', t)
    k.lathe(yoke, [(.55, 0), (.55, .1), (0, .12)], seg=16)
    for s in (-1, 1):
        k.extrude(yoke, [(-.35, .08), (.35, .08), (.2, 1.05), (-.2, 1.05)], .12, loc=(s * .78, 0, 0), axis='X',
                  chamfer=.03)
    # The director: a drum on trunnions, the big aperture in its face, the tracking sensor beside it.
    d = a.part('Director', 'Team', t)
    k.lathe(d, [(.5, -.55), (.62, -.45), (.66, -.2), (.66, .3), (.6, .5), (.5, .55)], loc=(0, 0, .95),
            rot=K.FORWARD, seg=18, worn=(2, 4))
    k.ring(a.part('Aperture_rim', 'Steel', t), [(.36, 0), (.46, 0), (.46, .05), (.36, .05)], loc=(0, -.55, .95),
           rot=K.FORWARD, seg=18)
    a.part('Aperture', 'Glass', t).cyl(.37, .02, loc=(0, -.56, .95), rot=K.FORWARD, seg=18, bevel=0)
    a.pivot('Muzzle_main', (0, -.6, .95), t)
    for s in (-1, 1):
        a.part('Trunnions', 'Steel', t).cyl(.12, .14, loc=(s * .7, 0, .95), rot=(0, R90, 0), seg=10, bevel=0)
    sp = a.part('Sensor_pod', 'Armor', t)
    k.block(sp, (.3, .45, .3), loc=(.5, -.25, 1.72), chamfer=.03)
    a.part('Sensor_lens', 'Glass', t).cyl(.08, .02, loc=(.5, -.48, 1.74), rot=K.FORWARD, seg=10, bevel=0)
    a.part('Director_stripe', 'Armor', t).box((.02, .6, .2), loc=(-.665, 0, .95), bevel=0)
    rv = a.part('Kit_rivets', 'Steel', t)
    for j in range(10):
        u = j * math.tau / 10
        rv.cyl(.02, .03, loc=(math.cos(u) * .53, -.565, .95 + math.sin(u) * .53), rot=(R90, 0, 0), seg=5, bevel=0)
    K.handle(a.part('Kit_handles', 'Steel', t), (.3, .3, 1.6), (-.3, .3, 1.6), (0, 0, 1), h=.06, r=.012)
    return t


def _mast(a):
    """The search radar panel and the APS sensor on a mast at the shelter's rear corner."""
    x, y = -SX + .25, SY1 - .25
    mast = a.part('Mast', 'Steel')
    mast.cyl(.07, 1.9, loc=(x, y, TOPZ + .95), seg=8, bevel=0)
    for i in range(3):
        u = i * math.tau / 3
        mast.limb((x + math.cos(u) * .4, y + math.sin(u) * .4, TOPZ + .06), (x, y, TOPZ + .9), .03, .03, bevel=0)
    k.block(a.part('Search_panel', 'Armor'), (.9, .12, .7), loc=(x, y - .1, TOPZ + 2.1), rot=(-.3, 0, -.4),
            chamfer=.02)
    a.part('Panel_face', 'Undercarriage').box((.8, .01, .6), loc=(x - .025, y - .17, TOPZ + 2.08), rot=(-.3, 0, -.4),
                                              bevel=0)
    aps = a.pivot('Mount_APS', (x + .45, y - .1, TOPZ + 1.55))
    k.block(a.part('APS_sensor', 'Armor', aps), (.26, .26, .22), loc=(0, 0, 0), chamfer=.03)
    a.part('Glass', 'Glass', aps).box((.18, .01, .1), loc=(0, -.135, .02), bevel=0)
    a.part('Mast', 'Steel').box((.5, .05, .05), loc=(x + .22, y - .1, TOPZ + 1.45), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (x + .2, y + .15, TOPZ + .06), h=1.5, r=.02)
    for dz in (1.0, 2.55):
        a.part('Obstruction_lamps', 'LavaGlow').box((.08, .08, .08), loc=(x, y, TOPZ + dz), bevel=0)


def _generator(a):
    gx, gy = 1.55, 1.7
    k.block(a.part('Generator_skid', 'Undercarriage'), (.75, 1.5, .12), loc=(gx, gy, PAD + .06), chamfer=.02)
    gen = a.part('Generator', 'Armor')
    k.block(gen, (.68, 1.35, .8), loc=(gx, gy, PAD + .52), chamfer=.04)
    vents = a.part('Generator_vents', 'Undercarriage')
    for j in range(4):
        vents.box((.012, .9, .04), loc=(gx - .345, gy, PAD + .35 + j * .1), bevel=0)
    a.part('Generator_stack', 'Steel').cyl(.06, .6, loc=(gx + .15, gy + .4, PAD + 1.2), seg=8, bevel=0)
    K.soot(a, (gx + .15, gy + .4, PAD + 1.5), radius=.3, k=.4)
    a.part('Kit_cables', 'Undercarriage').tube([(gx - .3, gy - .6, PAD + .2), (SX + .3, 1.0, PAD + .05),
                                                (SX + .02, 1.0, PAD + .5)], .03, seg=4)
    # Sandbags round the generator's open sides (one course), an extinguisher, a fence of pickets and tape in front.
    P.sandbag_run(a, [(gx + .5, gy - .9, PAD), (gx + .5, gy + .9, PAD), (gx - .1, gy + 1.0, PAD)], courses=2,
                  bag=(.55, .3, .15), part='Sandbags', seed=112, lean=True)
    # A sandbag course along the shelter's front and left foot, coolant gas bottles chained to the left side.
    P.sandbag_run(a, [(-SX - .3, 1.0, PAD), (-SX - .3, SY0 - .3, PAD), (SX + .2, SY0 - .3, PAD)], courses=1,
                  bag=(.55, .3, .15), part='Sandbags', seed=113, lean=True)
    for j in range(3):
        k.lathe(a.part('Gas_bottles', 'Fuel'), [(.1, 0), (.1, .95), (.07, 1.02), (.03, 1.06), (0, 1.07)],
                loc=(-SX - .2, 1.5 + j * .24, PAD), seg=8, worn=(1,))
    a.part('Kit_chains', 'Steel').box((.03, .75, .03), loc=(-SX - .08, 1.74, PAD + .8), bevel=0)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .38), (.04, .44), (0, .46)], loc=(1.5, -.4, PAD),
            seg=8, worn=(1,))
    pick = a.part('Pickets', 'Undercarriage')
    tape = a.part('Tape', 'Hazard')
    pts = []
    for j in range(5):
        x = -1.7 + j * .85
        pick.box((.04, .04, .9), loc=(x, -2.75, PAD + .45), bevel=0)
        pts.append((x, -2.75, PAD + .8))
    tape.tube(pts, .012, seg=3)


def laser_ad_station(a):
    """The laser anti-drone station: see the module docstring."""
    rng = random.Random(3601)
    _pad(a, rng)
    _shelter(a)
    _cooler(a)
    _director(a)
    _mast(a)
    _generator(a)
    k.clean(a)


BUILDERS = {
    'laser_ad_station': (laser_ad_station, dict(ao_distance=.6, grime_height=.6)),
}
