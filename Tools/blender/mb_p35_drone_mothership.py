"""Prompt 35 wave 12 (lane C): the drone mothership (Matriarch) rebuilt from scratch (spec:
Tools/blender/specs/drone_mothership.json).

An armoured rigid airship that carries and launches drones: the USS Akron / Macon "flying aircraft carrier" (the
internal hangar and the trapeze that launched and recovered its Sparrowhawk fighters) crossed with a modern
X-tailed rigid hull (Zeppelin NT / Airlander tail and vectoring ducted fans). Origin at the envelope centre (it flies;
built without a ground plane). 28.3 x 14 x 11.9 m as the old file.

- The rigid envelope (Team) with its longitudinal girders standing out as strakes, the nose battens and mooring
  spike, the armoured nose cap and tail cone; the dark spine of riveted armour plates along the top and the flank
  belts, the general's stripe round the bow; X tail with rudder-vators, nav lights, the tail light.
- Four vectoring ducted fans on outrigger struts (`Propeller` front left, `Propeller_2` front right, `Propeller_3`
  rear left, `Propeller_4` rear right; each its hub and five blades, spinning about Y): ducts with stator vanes and
  the motor nacelles behind them.
- Under the bow the twin 30 mm chin turret (`Turret`, `Main_cannon` / `_2`, `Muzzle_brake` / `_2`, `Muzzle_main`
  between the tips) on its pylon; the command gondola with the bridge glazing, side windows, the armour skirt,
  searchlights, the sensor ball and the bomb bay doors in its belly (bomb_bay); the twin cannon ball under its stern
  (`Mount_main.001`, `Muzzle_main.001`); the two hanging 30 mm gun pods on pylons (`Mount_gun` / `.001`,
  `Muzzle_gun` / `.001`).
- Behind the gondola, the keel corridor; the drone hangar (drone_bay: the bay box, its two doors hanging open, the
  launch rail with six FPV drones, `Muzzle_missile` at the opening); the rotary drop launcher (`Mount_missile.001`,
  six tubes pointing down, `Muzzle_missile.001`); the trapeze lowered with a recon UAV on its hook (uav_bay).
- On the back two quad flak turrets (`Mount_mg` forward, `Mount_mg.001` aft, each `Muzzle_mg` at the four tips) and
  between them the shield-generator belt round the hull (shield: the raised band, the glowing coil and its emitter
  studs, low enough to clear the aft turret's barrels); the dorsal hatch, antennas, beacons, flare dispensers.

The breakable systems without a node (bay, hangar, trapeze, shield, bomb bay) are separate panels one shade off the
hull (COLOR_0 tone). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
ENV = [(0, -13.75), (.95, -13.5), (1.85, -12.95), (2.6, -12.05), (3.15, -10.85), (3.5, -9.25), (3.7, -7.2),
       (3.78, -4.6), (3.78, -1.0), (3.66, 2.4), (3.38, 5.4), (2.9, 8.2), (2.25, 10.6), (1.5, 12.4), (.8, 13.5),
       (.35, 14.0)]


def env_r(y):
    """The envelope's radius at y (linear between the profile stations)."""
    for (r0, y0), (r1, y1) in zip(ENV, ENV[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / (y1 - y0)
    return 0.0


def surf(y, a, out=0.0):
    """A point on the envelope at y, angle a from the top towards +X, `out` metres proud of it."""
    r = env_r(y) + out
    return (r * math.sin(a), y, r * math.cos(a))


def _patch(part, y0, y1, a0, a1, out=.05, inn=.0, nu=4, nv=3):
    """A curved plate on the envelope between y0..y1 and angles a0..a1: outer and inner skins and the four edges."""
    verts, faces = [], []
    grid = [[(y0 + (y1 - y0) * j / nv, a0 + (a1 - a0) * i / nu) for i in range(nu + 1)] for j in range(nv + 1)]
    for o in (out, inn):
        for row in grid:
            for y, a in row:
                verts.append(surf(y, a, o))
    W = nu + 1
    N = (nv + 1) * W
    for j in range(nv):
        for i in range(nu):
            q = j * W + i
            faces.append((q, q + 1, q + W + 1, q + W))
            faces.append((N + q + W, N + q + W + 1, N + q + 1, N + q))
    rim = [j * W for j in range(nv + 1)] + [nv * W + i for i in range(1, nu + 1)] + \
          [j * W + nu for j in range(nv - 1, -1, -1)] + [i for i in range(nu - 1, 0, -1)]
    for p, q in zip(rim, rim[1:] + rim[:1]):
        faces.append((q, p, N + p, N + q))
    part.mesh(verts, faces)


def _envelope(a):
    k.lathe(a.part('Envelope', 'Team'), ENV, rot=K.BACKWARD, seg=32)
    # Longitudinal girders standing out of the skin as strakes (every 30 degrees but the flak lines).
    st = a.part('Strakes', 'Team')
    for i in range(12):
        u = (i + .5) * TAU / 12
        pts = [surf(y, u, .03) for y in (-12.6, -10.85, -9.25, -7.2, -4.6, -1.0, 2.4, 5.4, 8.2, 10.6, 12.2)]
        st.tube(pts, .035, seg=3, caps=False)
    # The nose: armoured cap, twelve battens over it, the mooring spike; the tail cone with its light.
    k.lathe(a.part('Armor', 'Armor'), [(0, -13.82), (.98, -13.55), (1.9, -12.98), (1.9, -12.9), (0, -12.9)],
            rot=K.BACKWARD, seg=24, worn=(1, 2))
    bat = a.part('Nose_battens', 'Steel')
    for i in range(12):
        u = i * TAU / 12
        bat.tube([surf(y, u, .07) for y in (-13.5, -12.95, -12.05, -10.85)], .04, seg=3, caps=False)
    k.lathe(a.part('Steel', 'Steel'), [(.13, 0), (.04, .55), (0, .56)], loc=(0, -13.8, 0), rot=K.FORWARD, seg=8)
    k.lathe(a.part('Armor', 'Armor'), [(.86, 13.38), (.8, 13.7), (.4, 14.05), (0, 14.12)], rot=K.BACKWARD, seg=16)
    a.part('Tail_light', 'TeamGlow').sphere(.11, loc=(0, 14.15, 0), seg=8, rings=5)
    # The armour: the dark spine plates along the top, the flank belts, riveted; the general's stripe round the bow.
    arm = a.part('Plates', 'Armor')
    riv = a.part('Kit_rivets', 'Steel')
    step = 2.3
    for i in range(8):
        y0 = -10.6 + i * step
        _patch(arm, y0, y0 + step - .1, -.4, .4, out=.06, nu=4, nv=2)
        for f in (.15, .85):
            for u in (-.32, .32):
                riv.cyl(.04, .03, loc=surf(y0 + (step - .1) * f, u, .085), rot=(0, u, 0), seg=6, bevel=0)
    for i in range(6):
        y0 = -8.4 + i * 2.6
        for s in (-1, 1):
            a0, a1 = s * 1.62, s * 2.02
            _patch(arm, y0, y0 + 2.5, min(a0, a1), max(a0, a1), out=.08, nu=2, nv=2)
            for f in (.12, .88):
                riv.cyl(.04, .03, loc=surf(y0 + 2.5 * f, s * 1.82, .105), rot=(0, s * 1.82, 0), seg=6, bevel=0)
    k.ring(a.part('General_stripe', 'Team'), [(env_r(-9.0) - .02, -.4), (env_r(-9.0) + .07, -.38),
                                              (env_r(-9.6) + .07, .2), (env_r(-9.6) - .02, .22)],
           loc=(0, -9.1, 0), rot=K.BACKWARD, seg=32)
    # Ring frames standing out of the skin between the gas cells.
    fr = a.part('Ring_frames', 'Undercarriage')
    for y in (-6.0, -1.6, 5.4, 8.6, 11.0):
        r = env_r(y)
        k.ring(fr, [(r - .02, -.05), (r + .045, -.04), (r + .045, .04), (r - .02, .05)], loc=(0, y, 0),
               rot=K.BACKWARD, seg=32)
    k.ring(a.part('Stripe_trim', 'PlasterWhite'), [(env_r(-8.4) - .02, -.07), (env_r(-8.4) + .06, -.06),
                                                   (env_r(-8.4) + .06, .06), (env_r(-8.4) - .02, .07)],
           loc=(0, -8.4, 0), rot=K.BACKWARD, seg=32)


def _tail(a):
    """X tail: four fins at 45 degrees with their rudder-vators, nav lights at the tips."""
    skin = a.part('Fins', 'Team')
    cs = a.part('Control_surfaces', 'Armor')
    for i in range(4):
        ang = TAU / 8 + i * TAU / 4
        k.extrude(skin, [(8.3, 1.6), (13.3, .9), (13.15, 4.85), (11.3, 5.15)], .22, rot=(0, ang, 0), axis='X',
                  chamfer=.04)
        k.extrude(cs, [(13.32, 2.0), (13.95, 2.1), (13.8, 4.75), (13.17, 4.8)], .12, rot=(0, ang, 0), axis='X',
                  chamfer=.02)
        tip = (math.sin(ang) * 5.2, 12.2, math.cos(ang) * 5.2)
        a.part('Nav_lights', 'LavaGlow' if math.sin(ang) < 0 else 'SignalGreen').box((.1, .3, .1), loc=tip,
                                                                                      rot=(0, ang, 0), bevel=0)


def _fan(a, pivot, x, y, z):
    """One vectoring ducted fan: the duct ring with stator vanes, the motor nacelle, the outrigger struts; the
    hub and five blades spin on the pivot."""
    side = 1 if x > 0 else -1
    k.ring(a.part('Ducts', 'Armor'), [(1.24, -.5), (1.36, -.46), (1.42, -.2), (1.4, .38), (1.3, .5), (1.2, .46),
                                      (1.18, -.4)], loc=(x, y, z), rot=K.BACKWARD, seg=20, worn=(2, 3))
    k.ring(a.part('Duct_bands', 'Team'), [(1.425, -.05), (1.45, -.03), (1.45, .15), (1.425, .17)], loc=(x, y, z),
           rot=K.BACKWARD, seg=20)
    stv = a.part('Stators', 'Steel')
    for i in range(4):
        u = TAU / 8 + i * TAU / 4
        stv.box((1.0, .06, .04), loc=(x + math.cos(u) * .7, y + .3, z + math.sin(u) * .7), rot=(0, -u, 0), bevel=0)
    k.lathe(a.part('Nacelles', 'Armor'), [(0, -.1), (.3, .0), (.34, .3), (.3, .9), (.14, 1.2), (0, 1.25)],
            loc=(x, y + .25, z), rot=K.BACKWARD, seg=12, worn=(2,))
    # Outrigger struts from the hull's flank to the duct's inboard side (two, a little apart in y), a fairing.
    hx = env_r(y) * .97
    strut = a.part('Outriggers', 'Steel')
    for dy, dz in ((-.25, .1), (.3, -.15)):
        strut.limb((side * (hx - .2), y + dy, z + dz + .1), (x - side * 1.3, y + dy, z + dz), .16, .1, bevel=0)
    k.block(a.part('Outriggers', 'Armor'), (.5, .9, .5), loc=(side * (hx - .05), y, z + .05), chamfer=.06)
    p = a.pivot(pivot, (x, y, z))
    k.lathe(a.part(f'{pivot}_hub', 'Steel', p), [(0, -.32), (.2, -.25), (.24, 0), (.2, .1), (0, .12)],
            rot=K.BACKWARD, seg=10)
    bl = a.part(f'{pivot}_blades', 'Undercarriage', p)
    for i in range(5):
        u = i * TAU / 5
        bl.box((1.0, .05, .22), loc=(math.cos(u) * .68, 0, math.sin(u) * .68), rot=(.45, -u, 0), bevel=0)


def _gondola(a):
    g = a.part('Gondola', 'Team')

    def sec(y, wb, zb, wm, zm, wt, zt):
        return [(-wb, y, zb), (wb, y, zb), (wm, y, zm), (wt, y, zt), (-wt, y, zt), (-wm, y, zm)]
    k.sharp_loft(g, [sec(-7.75, .55, -4.75, 1.0, -4.3, .95, -3.35), sec(-7.1, .95, -5.35, 1.4, -4.45, 1.25, -3.3),
                     sec(-2.0, .95, -5.35, 1.4, -4.45, 1.25, -3.3), sec(-1.25, .7, -5.0, 1.15, -4.4, 1.05, -3.3)],
                 chamfer=.05)
    gl = a.part('Windows', 'Glass')
    fr = a.part('Window_frames', 'Armor')
    # The bridge glazing: a sloped band across the nose, its mullions and the visor; the side windows.
    gl.box((1.6, .32, .02), loc=(0, -7.5, -3.95), rot=(math.atan2(.45, .9), 0, 0), bevel=0)
    for x in (-.5, 0, .5):
        fr.box((.05, .36, .05), loc=(x, -7.52, -3.95), rot=(math.atan2(.45, .9), 0, 0), bevel=0)
    fr.box((1.9, .1, .06), loc=(0, -7.55, -3.72), bevel=0)
    for s in (-1, 1):
        for y in (-6.4, -5.65, -4.9, -4.15, -3.4, -2.65):
            gl.box((.02, .5, .26), loc=(s * 1.335, y, -3.9), rot=(0, -s * .12, 0), bevel=0)
            fr.box((.03, .06, .32), loc=(s * 1.34, y + .28, -3.9), rot=(0, -s * .12, 0), bevel=0)
        # The armour skirt along the lower flank, bolted; the handrail; searchlights under the nose.
        a.part('Gondola_armor', 'Armor').box((.06, 5.0, .55), loc=(s * 1.2, -4.6, -4.9), rot=(0, s * .9, 0),
                                             bevel=.012)
        a.part('Kit_rivets', 'Steel').bolts([(s * 1.24, -6.8 + i * .7, -4.68) for i in range(8)], r=.03, h=.03,
                                            rot=(0, R90, 0), seg=6, bevel=0)
        a.part('Steel', 'Steel').tube([(s * 1.47, -6.7, -4.42), (s * 1.47, -2.2, -4.42)], .025, seg=4)
        k.block(a.part('Searchlights', 'Armor'), (.36, .44, .36), loc=(s * .7, -7.25, -5.05), rot=(.35, 0, s * .2),
                chamfer=.04)
        a.part('Lamps', 'Lamp').cyl(.15, .02, loc=(s * .7 - s * .045, -7.48, -5.13), rot=(R90 + .35, 0, s * .2),
                                    seg=10, bevel=0)
    k.lathe(a.part('Sensor_ball', 'Armor'), [(0, 0), (.22, .05), (.26, .2), (.2, .36), (0, .4)],
            loc=(0, -6.7, -5.75), seg=12)
    a.part('Sensor_ball', 'Glass').box((.16, .02, .12), loc=(0, -6.96, -5.55), bevel=0)
    # The bomb bay in the belly (bomb_bay): two doors, their hinges, the hazard border; one shade off.
    for s in (-1, 1):
        k.block(a.part('Bombbay_doors', 'Armor'), (.8, 2.2, .06), loc=(s * .42, -5.5, -5.38), chamfer=.012)
        a.part('Bombbay_hinges', 'Steel').cyl(.03, 2.1, loc=(s * .86, -5.5, -5.36), rot=K.FORWARD, seg=6, bevel=0)
    a.part('Bombbay_frame', 'Hazard').box((1.86, 2.34, .03), loc=(0, -5.5, -5.355), bevel=0)
    K.tone(a, 'Bombbay', k=.85)


def _chin_turret(a):
    """The twin 30 mm chin turret under the bow on its pylon (Turret)."""
    k.lathe(a.part('Pylon', 'Armor'), [(.5, 0), (.48, .3), (.6, .5), (0, .5)], loc=(0, -10.8, -3.62), seg=14,
            worn=(2,))
    t = a.pivot('Turret', (0, -10.8, -3.55))
    body = a.part('Turret_body', 'Team', t)
    k.lathe(body, [(0, -.85), (.42, -.8), (.6, -.6), (.64, -.3), (.58, -.05), (.5, 0), (0, 0)], seg=16, worn=(2, 3))
    k.block(a.part('Turret_armor', 'Armor', t), (.8, .4, .5), loc=(0, -.62, -.38), chamfer=.06)
    for s in (-1, 1):
        x = s * .22
        k.lathe(a.part('Main_cannon' if s < 0 else 'Main_cannon_2', 'Steel', t),
                [(.075, 0), (.075, .3), (.058, .36), (.052, 2.0), (0, 2.0)], loc=(x, -.75, -.38), rot=K.FORWARD,
                seg=10, worn=(1,))
        k.lathe(a.part('Muzzle_brake' if s < 0 else 'Muzzle_brake_2', 'Undercarriage', t),
                [(.055, 0), (.085, .03), (.085, .22), (.065, .25), (0, .25)], loc=(x, -2.56, -.38), rot=K.FORWARD,
                seg=10)
    a.pivot('Muzzle_main', (0, -2.76, -.38), t)
    k.block(a.part('Turret_sight', 'Glass', t), (.2, .1, .14), loc=(.32, -.7, -.05), chamfer=.02)
    a.part('Turret_armor', 'Armor', t).bolts([(s * .3, -.83, -.2 + dz) for s in (-1, 1) for dz in (0, -.3)],
                                             r=.03, h=.03, rot=K.FORWARD, seg=6, bevel=0)
    K.soot(a, (0, -13.5, -3.93), radius=.5, k=.35)


def _gondola_gun(a):
    """The twin cannon ball under the gondola's stern (Mount_main.001)."""
    m = a.pivot('Mount_main__001', (0, -2.2, -5.38))
    k.lathe(a.part('Gondola_gun_body', 'Team', m), [(.35, 0), (.42, -.12), (.46, -.3), (.4, -.5), (.2, -.62),
                                                     (0, -.64)], seg=14, worn=(2,))
    k.block(a.part('Gondola_gun_armor', 'Armor', m), (.6, .3, .4), loc=(0, -.42, -.3), chamfer=.05)
    for s in (-1, 1):
        k.lathe(a.part('Gondola_guns', 'Steel', m), [(.05, 0), (.05, .25), (.038, .3), (.034, 1.65), (0, 1.65)],
                loc=(s * .16, -.55, -.3), rot=K.FORWARD, seg=8)
        a.part('Gondola_gun_brakes', 'Undercarriage', m).cyl(.055, .18, loc=(s * .16, -2.14, -.3), rot=K.FORWARD,
                                                             seg=8, bevel=0)
    a.pivot('Muzzle_main__001', (0, -2.22, -.3), m)


def _gun_pods(a):
    """The two hanging 30 mm gun pods on pylons off the gondola's sides (Mount_gun / .001)."""
    for s, mount, muzzle in ((1, 'Mount_gun', 'Muzzle_gun'), (-1, 'Mount_gun__001', 'Muzzle_gun__001')):
        x = s * 2.2
        a.part('Pod_pylons', 'Armor').limb((s * 1.3, -6.0, -4.55), (x, -6.0, -4.95), .14, .5, bevel=.02)
        p = a.pivot(mount, (x, -6.0, -5.2))
        k.lathe(a.part('Pod_body', 'Team', p),
                [(0, -.9), (.18, -.85), (.24, -.5), (.24, .55), (.16, .85), (0, .9)], loc=(0, .1, -.2),
                rot=K.FORWARD, seg=12, worn=(2, 3))
        k.lathe(a.part('Pod_barrels', 'Steel', p), [(.05, 0), (.05, .2), (.035, .25), (.032, 1.75), (0, 1.75)],
                loc=(0, -.8, -.45 + .2), rot=K.FORWARD, seg=8)
        a.part('Pod_brakes', 'Undercarriage', p).cyl(.05, .16, loc=(0, -2.6, -.25), rot=K.FORWARD, seg=8, bevel=0)
        a.pivot(muzzle, (0, -2.7, -.45), p)
        a.part('Pod_bands', 'Hazard', p).cyl(.245, .06, loc=(0, .5, -.2), rot=K.FORWARD, seg=12, bevel=0)


def _keel_and_bays(a):
    """The keel corridor, the drone hangar (drone_bay), the rotary drop launcher, the UAV trapeze (uav_bay)."""
    keel = a.part('Keel', 'Armor')
    for y0, y1 in ((-1.25, .2), (4.4, 7.4)):
        zb = -env_r((y0 + y1) / 2) - .12
        k.block(keel, (.9, y1 - y0, .45), loc=(0, (y0 + y1) / 2, zb + .1), chamfer=.06)
    # The drone hangar: the bay box, the open doors hanging from their hinges, the rail of six FPV drones.
    bay = a.part('Bay', 'Armor')
    k.block(bay, (2.7, 4.2, .75), loc=(0, 2.3, -3.85), chamfer=.08, ends=(True, True))
    a.part('Bay_well', 'Undercarriage').box((2.3, 3.8, .04), loc=(0, 2.3, -4.235), bevel=0)
    for s in (-1, 1):
        k.block(a.part('Bay_doors', 'Armor'), (.06, 3.8, 1.1), loc=(s * 1.55, 2.3, -4.7), rot=(0, s * .35, 0),
                chamfer=.015)
        a.part('Bay_hinges', 'Steel').cyl(.04, 3.7, loc=(s * 1.36, 2.3, -4.2), rot=K.FORWARD, seg=6, bevel=0)
        a.part('Bay_door_bands', 'Hazard').box((.02, 3.6, .1), loc=(s * (1.55 + .2 * s * .35 + .03 * s), 2.3, -5.15),
                                               rot=(0, s * .35, 0), bevel=0)
    a.part('Bay_rail', 'Steel').box((.12, 3.6, .1), loc=(0, 2.3, -4.3), bevel=0)
    for i in range(6):
        _fpv(a, (0.0, .6 + i * .66, -4.55), i)
    a.pivot('Muzzle_missile', (0, 2.3, -4.62))
    K.tone(a, 'Bay', k=.88)
    # The rotary drop launcher: a turret ring under the keel, the drum of six tubes pointing down.
    m = a.pivot('Mount_missile__001', (0, 6.0, -4.2))
    k.lathe(a.part('Launcher_ring', 'Steel', m), [(.6, .55), (.62, .45), (.62, .35), (.5, .3), (0, .3)], seg=14)
    k.lathe(a.part('Launcher_drum', 'Team', m), [(0, .3), (.55, .3), (.6, .1), (.6, -.4), (.5, -.48), (0, -.48)],
            seg=14, worn=(2, 3))
    tubes = a.part('Launcher_tubes', 'Undercarriage', m)
    for i in range(6):
        u = i * TAU / 6
        tubes.cyl(.11, .06, loc=(math.cos(u) * .33, math.sin(u) * .33, -.5), seg=8, bevel=0)
    a.part('Launcher_drum', 'Undercarriage', m).cyl(.12, .06, loc=(0, 0, -.5), seg=8, bevel=0)
    a.pivot('Muzzle_missile__001', (0, 0, -.5), m)
    # The trapeze lowered with a recon UAV on its hook (uav_bay).
    tz = -env_r(8.5)
    trap = a.part('Uav_trapeze', 'Steel')
    for s in (-1, 1):
        trap.tube([(s * .5, 8.0, tz + .05), (s * .35, 8.6, tz - .85)], .045, seg=4)
        trap.tube([(s * .5, 9.2, tz + .05), (s * .35, 8.6, tz - .85)], .045, seg=4)
    trap.tube([(-.4, 8.6, tz - .85), (.4, 8.6, tz - .85)], .05, seg=4)
    k.block(a.part('Uav_trapeze', 'Armor'), (1.2, 1.6, .2), loc=(0, 8.6, tz + .02), chamfer=.04)
    _uav(a, (0, 8.6, tz - 1.15))
    K.tone(a, 'Uav', k=.88)


def _fpv(a, loc, i):
    """An FPV drone hanging under the bay rail: the X frame, four motors and prop discs, the battery and warhead."""
    x, y, z = loc
    fr = a.part('Drone_frames', 'Undercarriage')
    for u in (TAU / 8, 3 * TAU / 8):
        fr.box((.62, .05, .03), loc=(x, y, z), rot=(0, 0, u), bevel=0)
    mot = a.part('Drone_motors', 'Steel')
    props = a.part('Drone_props', 'Glass')
    for j in range(4):
        u = TAU / 8 + j * TAU / 4
        px, py = x + math.cos(u) * .26, y + math.sin(u) * .26
        mot.cyl(.04, .06, loc=(px, py, z + .03), seg=6, bevel=0)
        props.cyl(.13, .008, loc=(px, py, z + .065), seg=8, bevel=0)
    a.part('Drone_bodies', 'Team').box((.12, .2, .07), loc=(x, y, z - .02), bevel=0)
    a.part('Drone_warheads', 'BarrelRed').cyl(.04, .16, loc=(x, y - .17, z - .03), rot=K.FORWARD, seg=6, bevel=0)
    a.part('Drone_clamps', 'Steel').box((.04, .04, .22), loc=(x, y, z + .14), bevel=0)


def _uav(a, c):
    """A recon UAV (Shadow-class): fuselage, wing, twin booms with the inverted-V tail, the pusher prop."""
    x, y, z = c
    k.lathe(a.part('Uav_body', 'Team'), [(0, -1.0), (.12, -.9), (.17, -.5), (.17, .4), (.1, .8), (0, .85)],
            loc=(x, y, z), rot=K.BACKWARD, seg=10, worn=(2,))
    k.extrude(a.part('Uav_wing', 'Team'), [(-1.6, -.18), (1.6, -.18), (1.5, .12), (-1.5, .12)], .05,
              loc=(x, y - .1, z + .1), axis='Z', chamfer=.01)
    bm = a.part('Uav_booms', 'Armor')
    for s in (-1, 1):
        bm.tube([(x + s * .55, y - .1, z + .1), (x + s * .55, y + 1.4, z + .15)], .035, seg=5)
        k.extrude(a.part('Uav_wing', 'Team'), [(1.25, 0), (1.6, 0), (1.62, .38), (1.4, .38)], .03,
                  loc=(x + s * .55, y, z + .15), rot=(0, s * .7, 0), axis='X', chamfer=0)
    a.part('Uav_prop', 'Undercarriage').box((.7, .03, .06), loc=(x, y + .9, z), bevel=0)
    a.part('Uav_sensor', 'Glass').sphere(.08, loc=(x, y - .75, z - .14), seg=8, rings=5)
    a.part('Uav_hook', 'Steel').box((.04, .04, .3), loc=(x, y, z + .3), bevel=0)


def _flak(a, mount, muzzle, loc, ring_z):
    """A quad flak turret on the back: the ring, the armoured house, four barrels with brakes (muzzle at the tips)."""
    x, y, z = loc
    k.lathe(a.part('Flak_ring', 'Steel'), [(.95, ring_z - z - .05), (.95, 0), (.82, .05), (0, .05)],
            loc=(x, y, z), seg=16, worn=(1,))
    m = a.pivot(mount, loc)
    house = a.part('Flak_body', 'Team', m)
    k.sharp_loft(house, [[(-.85, -.8, .05), (.85, -.8, .05), (.9, .85, .05), (-.9, .85, .05)],
                         [(-.68, -.62, .66), (.68, -.62, .66), (.75, .8, .68), (-.75, .8, .68)]], chamfer=.05)
    k.block(a.part('Flak_shield', 'Armor', m), (1.5, .14, .62), loc=(0, -.82, .4), rot=(.25, 0, 0), chamfer=.03)
    a.part('Flak_band', 'Team', m).box((1.52, .02, .12), loc=(0, -.9, .55), rot=(.25, 0, 0), bevel=0)
    for s in (-1, 1):
        for dz in (-.13, .13):
            bx = s * .2
            k.lathe(a.part('Flak_guns', 'Steel', m), [(.06, 0), (.06, .22), (.045, .28), (.04, 1.65), (0, 1.65)],
                    loc=(bx, -.85, .63 + dz), rot=K.FORWARD, seg=8)
            a.part('Flak_brakes', 'Undercarriage', m).cyl(.058, .2, loc=(bx, -2.44, .63 + dz), rot=K.FORWARD,
                                                         seg=8, bevel=0)
    a.part('Flak_ammo', 'Armor', m).box((.22, .6, .34), loc=(1.0, .1, .3), bevel=.02)
    a.part('Flak_ammo', 'Armor', m).box((.22, .6, .34), loc=(-1.0, .1, .3), bevel=.02)
    k.block(a.part('Flak_sight', 'Glass', m), (.16, .12, .12), loc=(.4, -.45, .7), chamfer=.015)
    a.pivot(muzzle, (0, -2.55, .63), m)


def _shield(a):
    """The shield-generator belt round the hull at y 2.35 (shield): the raised band, the coil, the emitter studs."""
    y = 2.35
    r = env_r(y)
    k.ring(a.part('Shield_band', 'Armor'), [(r - .03, -.32), (r + .14, -.26), (r + .14, .26), (r - .03, .32)],
           loc=(0, y, 0), rot=K.BACKWARD, seg=32, worn=(1, 2))
    k.ring(a.part('Shield_coil', 'TeamGlow'), [(r + .14, -.09), (r + .21, -.07), (r + .21, .07), (r + .14, .09)],
           loc=(0, y, 0), rot=K.BACKWARD, seg=32)
    em = a.part('Shield_emitters', 'Steel')
    glow = a.part('Shield_tips', 'TeamGlow')
    for i in range(12):
        u = i * TAU / 12 + TAU / 24
        if abs(math.cos(u)) > .97:
            continue                                  # keep the top and the keel clear
        p0, p1 = surf(y, u, .12), surf(y, u, .42)
        em.limb(p0, p1, .1, .1, bevel=0)
        glow.sphere(.07, loc=surf(y, u, .47), seg=6, rings=4)
    K.tone(a, 'Shield_band', k=.88)


def _back(a):
    """The dorsal hatch, antennas, beacons, flare dispensers."""
    k.block(a.part('Hatch', 'Armor'), (.8, .9, .12), loc=surf(-.5, 0, .1), chamfer=.03)
    K.whip_antenna(a.part('Antennas', 'Steel'), surf(-1.6, -.3, .02), h=1.4, r=.03)
    K.blade_antenna(a.part('Antennas', 'Steel'), surf(6.5, 0, .02), h=.4, chord=.4)
    K.dish(a.part('Datalink', 'Medical'), a.part('Datalink', 'Armor'), surf(-8.0, 0, .3), r=.4, normal=(0, -.4, 1),
           seg=12)
    a.part('Beacon', 'TeamGlow').sphere(.13, loc=surf(9.5, 0, .1), seg=8, rings=5)
    a.part('Beacon', 'LavaGlow').sphere(.12, loc=surf(-3.0, math.pi, .05), seg=8, rings=5)
    fl = a.part('Flares', 'Armor')
    for s in (-1, 1):
        u = s * 2.2
        c = surf(5.0, u, .06)
        fl.box((.12, .9, .4), loc=c, rot=(0, u, 0), bevel=0)
        for j in range(3):
            for kk in range(2):
                a.part('Flare_holes', 'Undercarriage').cyl(.05, .02, loc=surf(4.72 + j * .28, u - .05 + kk * .1, .13),
                                                           rot=(0, u, 0), seg=6, bevel=0)


def drone_mothership(a, detail=False):
    """The drone mothership: see the module docstring."""
    _envelope(a)
    _tail(a)
    for pivot, x, y in (('Propeller', 5.6, -2.65), ('Propeller_2', -5.6, -2.65), ('Propeller_3', 5.6, 6.85),
                        ('Propeller_4', -5.6, 6.85)):
        _fan(a, pivot, x, y, -.8)
    _gondola(a)
    _chin_turret(a)
    _gondola_gun(a)
    _gun_pods(a)
    _keel_and_bays(a)
    _flak(a, 'Mount_mg', 'Muzzle_mg', (0, -4.8, 3.9), env_r(-4.8))
    _flak(a, 'Mount_mg__001', 'Muzzle_mg__001', (0, 3.4, 3.71), env_r(3.4))
    _shield(a)
    _back(a)
    k.clean(a)
    K.suffixed(a)


BUILDERS = {
    'drone_mothership': (drone_mothership, dict(ao_distance=1.2, ground=False)),
}
