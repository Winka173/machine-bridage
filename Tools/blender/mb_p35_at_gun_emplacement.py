"""Prompt 35 wave 3 (lane B): the anti-tank gun emplacement rebuilt from scratch (spec:
Tools/blender/specs/at_gun_emplacement.json).

A towed MT-12 Rapira 100 mm anti-tank gun dug in by the Accord (the def's modelSize 5.8 x 4.2 x 2.0 m, about 0.6 x
the real gun's 9.65 m with its barrel): a shallow earth pad, a low horseshoe of sandbags in front of the shield with an
earth parapet behind it, the split trails spread back with their spades dug in, the two road wheels on the axle
(fixed: the gun traverses 45 degrees on its carriage); on the upper carriage (`Turret`) the flat shield with its
folded top and the sight window, the cradle with the recoil and recuperator cylinders over the barrel, the long
smoothbore with its pepperpot muzzle brake, the breech with the loading tray, the gunner's telescope and the
elevation handwheel; ammunition crates with rounds, a field radio with its whip, aiming stakes, a rolled net.

Its own body: no shape is shared with the other gun towers (the heavy flak's KS-19, the AA gun's Bofors).
Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`; old part names `Cradle`, `Hubs`,
`Sandbags`, `Shield`, `Trails`, `Tyres`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
PAD = .12
AXLE_Y = .55
WR = .4                   # road wheel radius
TZ = PAD + .55            # the upper carriage's pivot height
ELEV = math.radians(3)


def _emplacement(a, rng):
    outline = [(-2.05, -2.0), (-.6, -2.25), (.9, -2.15), (2.1, -1.6), (2.05, .8), (1.7, 2.7), (.2, 2.95),
               (-1.5, 2.75), (-2.1, 1.2)]
    P.earth_pad(a, outline, PAD, taper=.93)
    # The low horseshoe of sandbags in front of the shield (two courses), an earth parapet heaped behind it.
    R = 1.75
    path = [(math.sin(t) * R, AXLE_Y - .2 - math.cos(t) * R, PAD) for t in [math.radians(d) for d in range(-80, 81, 16)]]
    P.sandbag_run(a, path, courses=3, bag=(.6, .34, .17), part='Sandbags', seed=71, lean=True)
    # Low runs along both rear sides (one course), sheltering the crew's ammunition niche.
    for s in (-1, 1):
        P.sandbag_run(a, [(s * 1.95, .9, PAD), (s * 1.9, 2.4, PAD)], courses=1 if s > 0 else 2, bag=(.6, .34, .17),
                      part='Sandbags', seed=73 + s, lean=True)
    # The ammunition niche: a timber-lined slot in the left rear berm.
    niche = a.part('Niche', 'Wood')
    for dy in (-.35, .35):
        niche.box((.5, .06, .45), loc=(-1.55, 1.95 + dy, PAD + .22), bevel=0)
    niche.box((.55, .8, .05), loc=(-1.55, 1.95, PAD + .47), bevel=0)
    berm = a.part('Berm', 'Dirt')
    for t in (-55, -20, 20, 55):
        u = math.radians(t)
        k.block(berm, (1.0, .5, .32), loc=(math.sin(u) * (R + .38), AXLE_Y - .2 - math.cos(u) * (R + .38), PAD + .1),
                rot=(0, 0, u), chamfer=.1, taper=(.7, .5))
    for i in range(8):
        u = i * math.tau / 8
        K.dust(a, (math.cos(u) * 1.8, AXLE_Y + math.sin(u) * 1.8, PAD), radius=1.0, k=.28)
    # Stones turned up by the digging, scattered on the pad.
    st = a.part('Stones', 'Rock')
    for j in range(12):
        z = rng.uniform(.06, .12)
        st.box((z * 1.3, z, z * .7), loc=(rng.uniform(-1.9, 1.9), rng.uniform(-1.9, 2.6), PAD + z * .2),
               rot=(rng.uniform(-.3, .3), rng.uniform(-.3, .3), rng.uniform(0, 3)), bevel=0)


def _carriage(a):
    """The lower carriage: axle, two road wheels, the split trails spread back with spades dug in."""
    ax = a.part('Axles', 'Undercarriage')
    ax.cyl(.07, 1.6, loc=(0, AXLE_Y, PAD + WR), rot=(0, R90, 0), seg=8, bevel=0)
    k.block(a.part('Carriage', 'Armor'), (.7, .55, .25), loc=(0, AXLE_Y, PAD + WR + .05), chamfer=.04)
    for s in (-1, 1):
        x = s * .8
        k.lathe(a.part('Tyres', 'Rubber'), [(WR * .7, -.12), (WR * .95, -.12), (WR, -.08), (WR, .08), (WR * .95, .12),
                                            (WR * .7, .12)], loc=(x, AXLE_Y, PAD + WR), rot=(0, R90, 0), seg=14)
        k.lathe(a.part('Wheels', 'Armor'), [(WR * .7, .1), (WR * .55, .13), (WR * .2, .14), (0, .14)],
                loc=(x, AXLE_Y, PAD + WR), rot=(0, s * R90, 0), seg=10, worn=(0,))
        k.lathe(a.part('Hubs', 'Steel'), [(.08, .13), (.06, .19), (0, .2)], loc=(x, AXLE_Y, PAD + WR),
                rot=(0, s * R90, 0), seg=6)
        for j in range(6):
            u = j * math.tau / 6
            a.part('Wheel_nuts', 'Steel').cyl(.02, .03, loc=(x + s * .145, AXLE_Y + math.cos(u) * .13,
                                                             PAD + WR + math.sin(u) * .13), rot=(0, R90, 0), seg=5,
                                              bevel=0)
        # Torsion arm to the wheel, the trail leg spread 25 degrees, its spade and the towing eye.
        a.part('Suspension', 'Undercarriage').limb((s * .3, AXLE_Y, PAD + WR + .05), (x - s * .1, AXLE_Y, PAD + WR),
                                                   .1, .1, bevel=0)
        u = s * math.radians(25)
        end = (s * .25 + math.sin(u) * 2.05, AXLE_Y + math.cos(u) * 2.05, PAD + .08)
        a.part('Trails', 'Team').limb((s * .25, AXLE_Y + .2, PAD + WR), end, .16, .14, bevel=0, taper=(.8, .8))
        k.extrude(a.part('Spades', 'Steel'), [(-.25, 0), (.25, 0), (.18, -.25), (-.18, -.25)], .04,
                  loc=(end[0], end[1] + .05, PAD + .1), rot=(R90 - .3, 0, u), axis='Z', chamfer=.008)
        K.handle(a.part('Kit_handles', 'Steel'), (end[0] - .12, end[1] - .1, PAD + .22), (end[0] + .12, end[1] - .1,
                                                                                    PAD + .22), (0, 0, 1), h=.07)
        for f in (.25, .5, .75):
            px = s * .25 + (end[0] - s * .25) * f
            py = AXLE_Y + .2 + (end[1] - AXLE_Y - .2) * f
            pz = PAD + WR + (end[2] - PAD - WR) * f
            a.part('Kit_bolts', 'Steel').cyl(.025, .2, loc=(px, py, pz + .07), seg=5, bevel=0)
    a.part('Kit_hooks', 'Steel').torus(.06, .015, loc=(0, AXLE_Y + 2.1, PAD + .15), rot=(R90, 0, 0), seg=8, ring=4)


def _gun(a):
    t = a.pivot('Turret', (0, AXLE_Y, TZ))
    up = a.part('Upper_carriage', 'Team', t)
    k.extrude(up, [(-.35, 0), (.4, 0), (.3, .42), (-.2, .5)], .5, loc=(0, -.05, 0), axis='X', chamfer=.03)
    g = P.Elev((0, -.15, .55), ELEV)
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.3, 1.6, .26), loc=g.at(.2), rot=g.box_rot, chamfer=.04)
    # The recoil and recuperator cylinders over the barrel, the breech and loading tray behind.
    cyl = a.part('Recuperators', 'Steel', t)
    for dx in (-.07, .07):
        k.lathe(cyl, [(.07, 0), (.07, 1.45), (.05, 1.5)], loc=g.at(-.4, dx, up=.2), rot=g.lathe_rot, seg=8)
    br = a.part('Breech', 'Undercarriage', t)
    k.block(br, (.3, .42, .3), loc=g.at(-.75), rot=g.box_rot, chamfer=.03)
    a.part('Loading_tray', 'Steel', t).box((.22, .55, .03), loc=g.at(-1.15, up=-.1), rot=g.box_rot, bevel=0)
    # The smoothbore: collar, the long tube, the pepperpot brake (ports round its body).
    bp = a.part('Main_cannon', 'Steel', t)
    k.lathe(bp, [(.08, 0), (.08, .35), (.06, .4), (.05, 1.2), (.045, 2.4), (0, 2.4)], loc=g.at(.6), rot=g.lathe_rot,
            seg=10, worn=(1,))
    mb = a.part('Muzzle_brake', 'Undercarriage', t)
    k.lathe(mb, [(.045, 0), (.07, .02), (.07, .34), (.055, .36), (0, .36)], loc=g.at(2.95), rot=g.lathe_rot, seg=10)
    ports = a.part('Brake_ports', 'Charred', t)
    for j in range(4):
        for s in (-1, 1):
            ports.box((.01, .05, .035), loc=g.at(3.03 + j * .07, s * .071), rot=g.box_rot, bevel=0)
    a.pivot('Muzzle_main', g.at(3.32), t)
    # The shield: the flat main plate with the barrel cut-out, its folded top, the sight window, side wings.
    sh = a.part('Shield', 'Team', t)
    for s in (-1, 1):
        k.extrude(sh, [(-.45, 0), (.45, 0), (.45, .9), (-.45, .9)], .03, loc=(s * .55, -.42, .12),
                  rot=(R90 - .08, 0, 0), axis='Z', chamfer=.006)
        k.extrude(sh, [(-.4, 0), (.4, 0), (.38, .3), (-.38, .3)], .03, loc=(s * .55, -.35, 1.02),
                  rot=(R90 + .5, 0, 0), axis='Z', chamfer=.006)
    k.extrude(sh, [(-.12, 0), (.12, 0), (.12, .35), (-.12, .35)], .03, loc=(0, -.42, .78), rot=(R90 - .08, 0, 0),
              axis='Z', chamfer=.006)
    a.part('Sight_window', 'Glass', t).box((.12, .01, .08), loc=(.35, -.455, .85), bevel=0)
    for s in (-1, 1):
        K.handle(a.part('Kit_handles', 'Steel', t), (s * .75, -.36, .7), (s * .75, -.36, .95), (0, 1, 0), h=.05,
                 r=.012)
    rv = a.part('Kit_rivets', 'Steel', t)
    for s in (-1, 1):
        for j in range(5):
            rv.cyl(.016, .025, loc=(s * (.15 + j * .2), -.445, .16), rot=(R90, 0, 0), seg=5, bevel=0)
    # The gunner's telescope and the elevation / traverse handwheels on the left.
    sight = a.part('Sights', 'Armor', t)
    k.lathe(sight, [(.035, 0), (.035, .35), (.05, .38), (.05, .45)], loc=(.35, -.1, .85), rot=K.FORWARD, seg=8)
    sight.box((.06, .06, .3), loc=(.35, -.05, .68), bevel=0)
    for z, y in ((.45, .1), (.3, -.05)):
        k.lathe(a.part('Handwheels', 'Steel', t), [(.1, -.012), (.1, .012)], loc=(.48, y, z), rot=(0, R90, 0), seg=10)
    return t


def _kit(a, rng):
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    rounds = a.part('Rounds', 'Hazard')
    for (x, y, r) in ((1.35, 1.6, .2), (1.4, 2.25, -.1), (-1.35, 1.9, .15)):
        K.crate(crates, straps, (.95, .35, .22), (x, y, PAD), rot=(0, 0, r), bands=1)
    # An open crate with two rounds showing, two rounds laid on a tarp.
    for j in range(2):
        k.lathe(rounds, [(.05, 0), (.05, .55), (.035, .62), (.02, .85), (0, .88)], loc=(-1.6 + j * .14, 1.0, PAD + .07),
                rot=(R90, 0, .1), seg=8)
    k.block(a.part('Tarp', 'Canvas'), (.9, .6, .03), loc=(-1.5, 1.05, PAD + .015), chamfer=0)
    # The field radio with its whip, aiming stakes (striped), a rolled camouflage net.
    k.block(a.part('Radio', 'Armor'), (.35, .25, .4), loc=(1.7, .3, PAD + .2), chamfer=.03)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.75, .35, PAD + .4), h=1.4, r=.02, lean=.1)
    post = a.part('Aiming_posts', 'Hazard')
    band = a.part('Aiming_bands', 'Charred')
    for x, y in ((-1.9, -1.7), (-1.6, -2.0)):
        post.cyl(.025, 1.3, loc=(x, y, PAD + .55), seg=5, bevel=0)
        band.cyl(.028, .15, loc=(x, y, PAD + .8), seg=5, bevel=0)
    # A camouflage net on four poles over the crew's corner (rear left), scrim tufts on its edges.
    P.camo_net(a, [(.35, 1.25, 1.5), (1.9, 1.15, 1.45), (1.75, 2.75, 1.2), (.25, 2.7, 1.15)], .25, PAD, garnish=10,
               seed=72)
    # Spent cases thrown behind the breech, a jerrycan, helmets on a crate.
    cases = a.part('Spent_cases', 'Hazard')
    for j in range(5):
        cases.cyl(.05, .5, loc=(rng.uniform(-.8, .8), rng.uniform(1.3, 2.3), PAD + .05),
                  rot=(R90, 0, rng.uniform(0, 3)), seg=6, bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-1.65, .2, PAD), rot=(0, 0, .4))
    for x in (1.2, 1.45):
        a.part('Helmets', 'Crate').sphere(.13, loc=(x, 1.6, PAD + .22), seg=8, rings=6, cut=0)


def at_gun_emplacement(a):
    """The anti-tank gun emplacement: see the module docstring."""
    rng = random.Random(3561)
    _emplacement(a, rng)
    _carriage(a)
    _gun(a)
    _kit(a, rng)
    k.clean(a)


BUILDERS = {
    'at_gun_emplacement': (at_gun_emplacement, dict(ao_distance=.5, grime_height=.5)),
}
