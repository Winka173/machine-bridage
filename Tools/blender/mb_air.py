"""Machine Brigade aircraft and munitions built with frontier_kit.

Conventions (shared with ModelLibrary.cs): metres, +Z up, Blender -Y is the nose.
  * attack_helicopter: origin on the ground under the fuselage centre (skids touch z = 0).
    `Rotor` (main rotor hub, blades spin about local Z), `Tail_rotor` (hub on the fin, blades
    spin about local X), `Mount_gun` (chin turret yaw) with `Muzzle_gun`, and `Muzzle_rocket` /
    `Muzzle_missile` centred between the symmetric wing launchers.
  * gunship_heli and scout_heli follow attack_helicopter (origin on the ground, wheels or skids at
    z = 0); scout_heli's side guns are fixed, so its `Muzzle_gun` has no mount.
  * strike_jet: origin at the fuselage centre (it flies). `Bombs` is a pivot at the origin whose
    children are the six wing bombs (hidden together once they drop); `Muzzle_gun` at the chin gun.
  * attack_jet and strike_drone fly like strike_jet. strike_drone's pusher `Propeller` spins about
    local Y (the fuselage axis); `Muzzle_missile` sits between its missile rails and `Muzzle_rocket`
    between the noses of its two guided bombs, which hang on `Pylon_bomb` pylons (not `Bombs`).
  * Munitions: origin at the centre, nose at -Y, emissive `Alloy` motors at the tail.
Team / TeamGlow parts are recoloured per army at runtime. The fixed-wing kit below (airfoil lofts
with control surfaces, skin panels, intakes, nozzles, turbofans, propellers, bombs, missiles and
pylons) is shared with mb_air2.py's premium aircraft.
"""
import math

import bmesh
from mathutils import Vector

import mb_detail as hd
from mb_vehicles import _access_panel, _frame, _tube_mouth

R90 = math.pi / 2
FORWARD = (R90, 0, 0)    # local +Z -> -Y (nose)
BACKWARD = (-R90, 0, 0)  # local +Z -> +Y (tail)
ACROSS = (0, R90, 0)     # local +Z -> +X


def _octagon(y, w, z0, z1, k=.3, flat=.62):
    """Octagonal fuselage section at y: half-width w between belly z0 and spine z1."""
    h = z1 - z0
    return [(-w * flat, y, z0), (w * flat, y, z0), (w, y, z0 + h * k), (w, y, z1 - h * k), (w * flat, y, z1),
            (-w * flat, y, z1), (-w, y, z1 - h * k), (-w, y, z0 + h * k)]


def _bubble(y, w, z0, z1):
    """Canopy section: upright lower sides curving into a narrower roof."""
    zm = z0 + (z1 - z0) * .55
    return [(-w, y, z0), (w, y, z0), (w * .92, y, zm), (w * .5, y, z1), (-w * .5, y, z1), (-w * .92, y, zm)]


def _hoop(part, section, r=.03):
    """Canopy frame following a _bubble section from one sill over the roof to the other."""
    part.tube([section[1], section[2], section[3], section[4], section[5], section[0]], r, seg=6)


def _fin(part, centre, angle, span, chord, thickness, root):
    """Flat fin plate radiating from a body along Y at `angle` around the axis (0 = +X)."""
    d = Vector((math.cos(angle), 0, math.sin(angle)))
    loc = Vector(centre) + d * (root + span / 2)
    part.box((span, chord, thickness), loc=tuple(loc), rot=(0, -angle, 0), bevel=0)


# ----------------------------------------------------------------------------- helicopter kit
BLADE_FOIL = [(-.5, 0), (-.3, .55), (.15, .45), (.5, 0), (.15, -.2), (-.3, -.3)]


def _blade(part, tip_part, d, e, n, r0, r1, chord, t, pitch=.08, stripe=.28, tip=.14, droop=0.0):
    """Rotor blade from radius r0 to r1 along unit d (chord along e, thickness along n, all relative
    to the rotor pivot): a thin twisted airfoil with a root cuff, a yellow tip stripe and a swept tip
    cap. The three lofts meet on shared sections inside the blade."""
    d, e, n = Vector(d), Vector(e), Vector(n)

    def ring(rr, c, th, sweep=0.0):
        b = pitch * (1 - .5 * (rr - r0) / (r1 - r0))
        cv, nv = e * math.cos(b) + n * math.sin(b), -e * math.sin(b) + n * math.cos(b)
        base = d * rr - n * droop * ((rr - r0) / (r1 - r0)) ** 2 + e * sweep
        return [tuple(base + cv * u * c + nv * v * th) for u, v in BLADE_FOIL]
    a0, a1 = r1 - stripe - tip, r1 - tip
    part.loft([ring(r0, chord * .62, t * 2.4), ring(r0 + .3, chord, t), ring(a0, chord, t)], bevel=0)
    tip_part.loft([ring(a0, chord, t), ring(a1, chord, t)], bevel=0)
    part.loft([ring(a1, chord, t), ring(r1, chord * .5, t * .7, sweep=chord * .28)], bevel=0)


def _rotor_head(a, r, blades, R, chord, hub=.3, phase=0.0, t=.05, cap=.25, stripe=.28, droop=.06):
    """Articulated main rotor under pivot r (spins about local Z): stacked hub plates, a hub cap, a
    rotating swashplate with pitch links, blade grips with lead-lag dampers and airfoil blades with
    yellow tip stripes."""
    steel = a.part('Rotor_hub', 'Steel', r)
    grips = a.part('Rotor_grips', 'Armor', r)
    blades_p = a.part('Rotor_blades', 'Armor', r)
    tips = a.part('Rotor_tips', 'Hazard', r)
    steel.cyl(hub, .1, seg=12, bevel=0)
    steel.cyl(hub * .78, .1, loc=(0, 0, .1), seg=12, bevel=0)
    steel.lathe([(hub * .55, .14), (hub * .5, .14 + cap * .45), (hub * .24, .14 + cap), (0, .17 + cap)], seg=10)
    steel.cyl(hub * .8, .05, loc=(0, 0, -.24), seg=12, bevel=0)                          # swashplate
    grip = .5 + hub * .4
    for k in range(blades):
        ang = phase + k * math.tau / blades
        d = Vector((math.cos(ang), math.sin(ang), 0))
        e = Vector((-math.sin(ang), math.cos(ang), 0))
        grips.box((grip, chord * .55, .1), loc=tuple(d * (hub * .6 + grip / 2) + Vector((0, 0, .012))), rot=(0, 0, ang),
                  bevel=0)
        steel.cyl(.034, grip * .7, loc=tuple(d * (hub * .75 + grip * .38) + e * chord * .36 + Vector((0, 0, .02))),
                  rot=(0, R90, ang), seg=5,
                  bevel=0)                                                                  # damper
        steel.cyl(.02, .26, loc=tuple(d * hub * .72 - e * (chord * .275 + .04) + Vector((0, 0, -.12))), seg=5,
                  bevel=0)                                                                  # pitch link
        _blade(blades_p, tips, d, e, (0, 0, 1), hub * .6 + grip - .06, R, chord, t, stripe=stripe, droop=droop)
    if hd.on(a):  # hub and swashplate bolts, grip bolts, pitch horns and the scissor links
        bolts = a.part('Rotor_bolts', 'Steel', r)
        hd.bolt_ring(bolts, hd.frame((0, 0, .05)), hub * .89, 8, r=.018, h=.024)
        hd.bolt_ring(bolts, hd.frame((0, 0, -.215)), hub * .62, 6, r=.014, h=.02)
        for k in range(blades):
            ang = phase + k * math.tau / blades
            d = Vector((math.cos(ang), math.sin(ang), 0))
            e = Vector((-math.sin(ang), math.cos(ang), 0))
            for f in (.3, .72):
                hd.bolt(bolts, tuple(d * (hub * .6 + grip * f) + Vector((0, 0, .062))), r=.016, h=.022)
            bolts.box((.1, .045, .03), loc=tuple(d * hub * .72 - e * (chord * .275 + .01) + Vector((0, 0, .0))),
                      rot=(0, 0, ang), bevel=0)                                         # pitch horn
        for sx in (-1, 1):
            bolts.limb((sx * hub * .52, 0, -.2), (sx * hub * .3, 0, -.06), .03, .03, bevel=0)
            bolts.limb((sx * hub * .3, 0, -.06), (sx * hub * .12, 0, -.04), .03, .03, bevel=0)


def _tail_rotor(a, tr, blades, R, chord, t=.028, phase=0.0, side=-1):
    """Tail rotor under pivot tr (spins about local X, blades in the YZ plane): hub, pitch spider cap
    and airfoil blades with tip stripes. side is the direction (x) the hub faces."""
    hub = a.part('Tail_rotor_hub', 'Steel', tr)
    hub.cyl(R * .1 + .02, .1, rot=ACROSS, seg=10, bevel=.01, bseg=1)
    hub.lathe([(R * .08, 0), (R * .06, .06), (0, .1)], loc=(side * .05, 0, 0), rot=(0, side * R90, 0), seg=8)
    bl = a.part('Tail_rotor_blades', 'Armor', tr)
    tips = a.part('Tail_rotor_tips', 'Hazard', tr)
    for k in range(blades):
        ang = phase + k * math.tau / blades
        d = (0, -math.sin(ang), math.cos(ang))
        e = (0, math.cos(ang), math.sin(ang))
        _blade(bl, tips, d, e, (side, 0, 0), R * .12, R, chord, t, pitch=.2, stripe=R * .16, tip=R * .08, droop=0)
    if hd.on(a):  # bolts round the hub and a pitch link to every blade root
        links = a.part('Tail_rotor_links', 'Steel', tr)
        hd.bolt_ring(links, hd.frame((side * .05, 0, 0), (0, side * R90, 0)), R * .1, 5, r=.012, h=.018)
        for k in range(blades):
            ang = phase + k * math.tau / blades + .35
            tipv = Vector((side * .03, -math.sin(ang) * R * .15, math.cos(ang) * R * .15))
            links.limb((side * .09, 0, 0), tuple(tipv), .016, .016, bevel=0)


def _hellfire(a, x, y, z, length=1.1, r=.08, fins=True):
    """Laser-guided anti-tank missile with its nose tip at y: body, glass seeker, warhead band and
    four wings at the tail."""
    a.part('Missiles', 'Fuel').lathe([(r * .94, .1), (r, .15), (r, length * .97), (r * .78, length)], loc=(x, y, z),
                                     rot=BACKWARD, seg=8)
    a.part('Missile_seekers', 'Glass').lathe([(0, 0), (r * .6, .035), (r * .9, .09), (r * .93, .12)], loc=(x, y, z),
                                             rot=BACKWARD, seg=6)
    a.part('Missile_bands', 'Hazard').cyl(r + .01, .04, loc=(x, y + .32, z), rot=FORWARD, seg=6, bevel=0)
    part = a.part('Missile_fins', 'Armor')
    for k in range(4 if fins else 0):
        _trap_fin(part, (x, y + length * .6, z), math.pi / 4 + k * R90, r * .6, r * 1.1, length * .3, length * .1,
                  length * .2, .012)


def _exhaust_duct(a, loc, yaw, size=(.36, .7, .36), pitch=0.0):
    """Armoured infrared-suppressor duct (rear face towards +Y turned by yaw) with a dark louvred
    outlet."""
    m = _frame(loc, (pitch, 0, yaw))
    a.part('Armor', 'Armor').box(size, loc=loc, rot=(pitch, 0, yaw), bevel=.05, seg=1, taper=(.9, 1))
    outlet = m @ Vector((0, size[1] / 2 + .012, 0))
    a.part('Exhausts', 'Undercarriage').box((size[0] * .78, .02, size[2] * .74), loc=tuple(outlet),
                                            rot=(pitch, 0, yaw), bevel=0)
    a.part('Exhaust_vanes', 'Steel').grille(size[0] * .64, size[2] * .66,
                                            loc=tuple(m @ Vector((0, size[1] / 2 + .035, 0))),
                                            rot=(pitch, 0, yaw + math.pi), slats=4, depth=.05, thickness=.025)
    if hd.on(a):  # stiffening ribs over the duct and a bolted flange at its root
        ribs = a.part('Exhaust_ribs', 'Armor')
        for f in (-.25, .1):
            ribs.box((size[0] * .96, .04, size[2] * 1.03), loc=tuple(m @ Vector((0, size[1] * f, 0))),
                     rot=(pitch, 0, yaw), bevel=0)
        flange = m @ hd.frame((0, -size[1] / 2 + .04, 0), (-R90, 0, 0))
        hd.bolt_ring(a.part('Exhaust_bolts', 'Steel'), flange, size[0] * .48, 6, r=.014, h=.02)


def _ring(y, w, zc, h, top=None, seg=12):
    """Elliptical fuselage ring at y: half-width w, half-height h about zc. `top` replaces h for the
    upper half (a bulged spine or satcom hump)."""
    up = h if top is None else top
    return [(w * math.cos(u), y, zc + (up if math.sin(u) > 0 else h) * math.sin(u))
            for u in (-R90 + i * math.tau / seg for i in range(seg))]


def _arc(y, w, zc, h, a0=-.45, a1=math.pi + .45, n=9):
    """Upper arc of an elliptical ring (closed by its chord): a canopy blister over a _ring."""
    return [(w * math.cos(u), y, zc + h * math.sin(u)) for u in (a0 + (a1 - a0) * i / (n - 1) for i in range(n))]


# ----------------------------------------------------------------------------- helicopters
def attack_helicopter(a, detail=False):
    """Tandem-seat attack helicopter (AH-64 lineage): gunner low in front, pilot raised behind,
    avionics bays along the cheeks, a TADS/PNVS sensor nose, shoulder engines with infrared
    suppressor exhausts, a mast-mounted radar over an articulated four-blade rotor, stub wings with
    rocket pods and four-round Hellfire racks, and a chin gun on its own yaw mount. Origin on the
    ground under the fuselage centre (skids touch z = 0)."""
    hd.mark(a, detail)
    # Chunky proportions (wide cabin, thick boom, big fin) so it still reads at RTS camera distance.
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    hull = [
        _octagon(-4.55, .24, 1.2, 1.54),
        _octagon(-4.1, .5, .98, 1.8),
        _octagon(-3.2, .66, .9, 1.92),
        _octagon(-1.5, .76, .88, 2.04),
        _octagon(0.0, .8, .9, 2.12),
        _octagon(1.25, .7, 1.0, 2.06),
        _octagon(2.1, .44, 1.36, 2.0),
    ]
    body.loft(hull, bevel=.07, seg=2)
    boom = [_octagon(1.8, .42, 1.4, 2.0), _octagon(4.75, .2, 1.6, 1.9)]
    body.loft(boom, bevel=.04, seg=1)                                                                 # tail boom
    body.prism([(3.85, 1.8), (4.85, 1.7), (5.15, 3.5), (4.6, 3.55)], .16, bevel=.03)                # fin
    body.box((2.2, .62, .09), loc=(0, 4.2, 1.8), bevel=.02, seg=1, taper=(1, .7))                    # stabiliser
    for s in (-1, 1):
        armor.box((.06, .44, .36), loc=(s * 1.1, 4.22, 1.82), bevel=.015, seg=1)                     # end plates
        # Avionics bays along the cheeks, as wide as the stub-wing roots.
        body.box((.34, 2.5, .48), loc=(s * .9, -1.45, 1.22), bevel=.07, seg=1, taper=(.82, .94))
        a.part('Flares', 'Undercarriage').grille(.3, .14, loc=(s * .45, 3.1, 1.8 + .07), rot=(-R90, 0, 0), slats=3,
                                                   depth=.06, thickness=.03)             # flare dispensers
        armor.box((.36, .22, .08), loc=(s * .45, 3.1, 1.82), bevel=.015, seg=1)
    # Tandem cockpit: gunner in front, pilot raised behind; frames over the glass.
    glass.loft([_bubble(-4.05, .32, 1.6, 1.82), _bubble(-3.55, .54, 1.7, 2.26), _bubble(-2.68, .56, 1.76, 2.34)],
               bevel=.03, seg=1)
    glass.loft([_bubble(-2.78, .58, 1.78, 2.44), _bubble(-2.4, .6, 1.8, 2.62), _bubble(-1.35, .58, 1.84, 2.64),
                _bubble(-.95, .46, 1.88, 2.42)], bevel=.03, seg=1)
    frames = a.part('Canopy_frames', 'Armor')
    for section in (_bubble(-3.5, .56, 1.71, 2.28), _bubble(-2.7, .58, 1.77, 2.38), _bubble(-2.35, .62, 1.8, 2.64),
                    _bubble(-1.4, .6, 1.84, 2.66)):
        _hoop(frames, section)
    steel.box((.03, .42, .1), loc=(0, -2.55, 2.66), rot=(-.55, 0, 0), bevel=0, taper=(1, .4))    # wire cutters
    steel.box((.03, .5, .1), loc=(0, -4.0, .95), rot=(.35, 0, 0), bevel=0, taper=(1, .4))
    # Engine nacelles on the shoulders: intake lips and bullets, suppressor exhausts; rotor pylon.
    for s in (-1, 1):
        x = s * .74
        body.cyl(.36, 2.0, loc=(x, .15, 2.18), rot=FORWARD, seg=14, bevel=.08)
        steel.torus(.26, .045, loc=(x, -.86, 2.18), rot=FORWARD, seg=14, ring=4)
        dark.cyl(.25, .06, loc=(x, -.84, 2.18), rot=FORWARD, seg=14, bevel=0)                    # intakes
        steel.cyl(.08, .12, r2=.02, loc=(x, -.9, 2.18), rot=FORWARD, seg=8, bevel=0)
        _exhaust_duct(a, (s * .86, 1.3, 2.2), s * -.3)
    body.box((1.0, 2.0, .56), loc=(0, -.45, 2.26), bevel=.08, taper=(.72, .8))                          # pylon
    steel.cyl(.12, .8, loc=(0, -.6, 2.86), seg=10, bevel=0)                                            # mast
    steel.cyl(.05, .42, loc=(0, -.6, 3.64), seg=8, bevel=0)                                            # radar stalk
    armor.sphere((.4, .4, .15), loc=(0, -.6, 3.84), seg=14, rings=8)                                  # mast radar
    steel.cyl(.04, .3, loc=(0, 1.0, 2.2), seg=6, bevel=0)                                               # IR jammer
    armor.box((.18, .18, .2), loc=(0, 1.0, 2.44), bevel=.03, seg=1)
    a.part('Sensor', 'Glass').box((.2, .2, .1), loc=(0, 1.0, 2.44), bevel=.02, seg=1)
    # Stub wings: rocket pods inboard, four-round Hellfire racks at the tips.
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        body.box((1.8, 1.1, .16), loc=(s * 1.52, .05, 1.52), bevel=.03, seg=1, taper=(1, .9))
        _pylon(pylons, s * 1.5, -.35, .45, 1.48, 1.3, w=.1)
        _rocket_pod(a, s * 1.5, -.75, 1.1, .23, 1.4)
        armor.box((.08, 1.1, .5), loc=(s * 2.35, 0, 1.23), bevel=.02, seg=1)                          # Hellfire rail
        for x in (2.24, 2.46):
            for z in (1.35, 1.1):
                _hellfire(a, s * x, -.71, z, length=1.1, fins=x > 2.4)
        a.part('Wing_lights', 'TeamGlow').box((.06, .12, .06), loc=(s * 2.44, .1, 1.52), bevel=.01, seg=1)
    a.pivot('Muzzle_rocket', (0, -.8, 1.1))
    a.pivot('Muzzle_missile', (0, -.71, 1.225))
    a.pivot('Muzzle_aam', (0, -.62, 1.3))
    # TADS sensor drum under the nose with its side housings and windows, PNVS turret above.
    armor.cyl(.22, .5, loc=(0, -4.62, 1.3), rot=ACROSS, seg=12, bevel=.03, bseg=1)
    sensor = a.part('Sensor', 'Glass')
    for s in (-1, 1):
        armor.box((.1, .34, .32), loc=(s * .29, -4.6, 1.3), bevel=.03, seg=1)
        sensor.box((.06, .04, .12), loc=(s * .29, -4.78, 1.33), bevel=.01, seg=1)
    sensor.box((.16, .04, .12), loc=(-.08, -4.83, 1.32), bevel=.01, seg=1)
    sensor.box((.1, .04, .08), loc=(.12, -4.83, 1.26), bevel=.01, seg=1)
    armor.cyl(.1, .16, loc=(0, -4.38, 1.7), seg=10, bevel=.02, bseg=1)
    sensor.box((.1, .04, .07), loc=(0, -4.48, 1.71), bevel=.01, seg=1)
    a.part('Lamps', 'Lamp').box((.18, .12, .05), loc=(0, -3.9, .96), bevel=.01, seg=1)
    # Skids on arched struts, with steps.
    skids = a.part('Skids', 'Undercarriage')
    for s in (-1, 1):
        x = s * 1.05
        skids.tube([(x, 1.6, .065), (x, -1.8, .065), (x, -2.1, .16), (x, -2.25, .36)], .065, seg=8)
        for y, z in ((-1.1, 1.0), (.95, 1.12)):
            skids.tube([(x, y, .065), (s * 1.0, y, .5), (s * .45, y, z)], .055, seg=6)
        steel.box((.05, .3, .04), loc=(s * 1.02, -.1, .45), rot=(0, s * .3, 0), bevel=0)           # step
    steel.cyl(.015, .6, loc=(0, 3.2, 2.2), seg=5, bevel=0)                                              # antenna
    steel.box((.02, .2, .14), loc=(0, 2.4, 1.43), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 4.92, 3.6), seg=8, rings=5)

    # Chin gun on its own yaw mount: turret, yoke, receiver, jacketed barrel and ammunition chute.
    g = a.pivot('Mount_gun', (0, -3.45, .92))
    turret = a.part('Gun_turret', 'Armor', g)
    turret.cyl(.22, .22, loc=(0, 0, -.08), seg=12, bevel=.04)
    turret.box((.3, .26, .14), loc=(0, -.06, -.2), bevel=.03, seg=1)
    gun = a.part('Gun', 'Steel', g)
    gun.box((.17, .44, .15), loc=(0, -.16, -.16), bevel=.03)
    gun.cyl(.062, .42, loc=(0, -.58, -.16), rot=FORWARD, seg=8, bevel=.01, bseg=1)
    gun.cyl(.038, 1.05, loc=(0, -.85, -.16), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.055, .12, loc=(0, -1.33, -.16), rot=FORWARD, seg=8, bevel=0)
    a.part('Gun_feed', 'Undercarriage', g).tube([(.09, .02, -.14), (.2, .08, -.07), (.22, .22, .02)], .035, seg=6)
    a.pivot('Muzzle_gun', (0, -1.39, -.16), g)

    # Main rotor: four blades on an articulated hub at the mast top.
    r = a.pivot('Rotor', (0, -.6, 3.33))
    _rotor_head(a, r, 4, 4.65, .38, hub=.3, phase=math.pi / 4, cap=.12)
    # Tail rotor on the left of the fin, blades in the YZ plane.
    armor.cyl(.1, .18, loc=(-.15, 4.74, 2.86), rot=ACROSS, seg=10, bevel=.02, bseg=1)                 # gearbox
    tr = a.pivot('Tail_rotor', (-.3, 4.74, 2.86))
    _tail_rotor(a, tr, 4, .8, .16, phase=math.pi / 4, side=-1)
    if detail:
        _attack_helicopter_detail(a, hull, boom, g)


def _attack_helicopter_detail(a, hull, boom, g):
    """High-detail parts of the attack helicopter (see mb_detail.py): panel lines and rivets on the fuselage,
    boom, fin and wings, latches and doors on the avionics bays, cowl bands and intake screens, access panels
    on the rotor pylon, bolts on the sensor housings, canopy sills, steps, antennas and lights. The rotor
    head, tail rotor and exhaust ducts add their own (see _rotor_head, _tail_rotor, _exhaust_duct)."""
    lines = a.part('Panel_lines', 'Armor')
    rivets = a.part('Rivets', 'Steel')
    steel = a.part('Detail_steel', 'Steel')
    dark = a.part('Detail_dark', 'Undercarriage')
    flats = (.2, .8)
    for y in (-3.6, -2.7, -.15, .9):                                          # frames round the lower fuselage
        _hoop_line(lines, hull, y, [6, 7, 0, 1, 2], us=flats)
    for i in (2, 6):                                                          # seams along both sides
        _seam_line(lines, hull, -4.0, 1.2, i, u=.75 if i == 2 else .25)
        _rivet_row(rivets, hull, -2.6, -.3, i, 14, u=.9 if i == 2 else .1)
    for y in (2.3, 2.9, 3.5, 4.1):                                            # boom frames
        _hoop_line(lines, boom, y, list(range(8)) + [0], r=.008, us=flats)
    for i, u in ((2, .3), (2, .7), (6, .3), (6, .7), (4, .3), (4, .7)):       # boom rivet rows, sides and top
        _rivet_row(rivets, boom, 2.0, 3.8 if i == 4 else 4.6, i, 18, u=u, size=.02)
    for i in (2, 6):
        _seam_line(lines, boom, 1.9, 4.6, i, r=.008)
    # Avionics bays: two doors a side outlined, with latches.
    for s in (-1, 1):
        for y0, y1 in ((-2.6, -1.5), (-1.4, -.3)):
            x0, x1 = s * 1.07, s * 1.048
            lines.tube([(x0, y0, 1.05), (x0, y1, 1.05), (x1, y1, 1.4), (x1, y0, 1.4), (x0, y0, 1.05)], .007, seg=4)
            steel.box((.03, .08, .05), loc=(s * 1.064, y1 - .12, 1.22), bevel=0)
        for y in (-3.02, -2.86):                                              # boarding steps
            dark.box((.03, .12, .06), loc=(s * .675, y, 1.25), bevel=0)
            dark.box((.03, .12, .06), loc=(s * .69, y, 1.5), bevel=0)
    # Engine nacelles: cowl bands with latches, intake screens, rivets along the tops.
    for s in (-1, 1):
        x = s * .74
        for y in (-.35, .55):
            a.part('Cowl_bands', 'Armor').cyl(.366, .03, loc=(x, y, 2.18), rot=FORWARD, seg=14, bevel=0)
        for y in (-.5, .1, .7):
            steel.box((.03, .08, .05), loc=(x + s * .362, y, 2.18), bevel=0)
        steel.box((.46, .02, .02), loc=(x, -.875, 2.18), bevel=0)
        steel.box((.02, .02, .46), loc=(x, -.875, 2.18), bevel=0)
        for k in range(12):
            rivets.box((.02, .02, .012), loc=(x, -.7 + k * .14, 2.542), bevel=0)
    # Rotor pylon: bolted access panels either side of the mast; an anti-collision light behind it.
    for s in (-1, 1):
        _access_panel(a, s * .2, -.05, 2.54, .24, .5, nx=2, ny=3)
    a.part('Beacon_lights', 'Alloy').sphere((.05, .05, .035), loc=(0, .3, 2.535), seg=10, rings=6, cut=0)
    a.part('Beacon_lights', 'Alloy').sphere((.05, .05, .035), loc=(0, .1, .905), rot=(math.pi, 0, 0), seg=10,
                                            rings=6, cut=0)
    # Stub wings: rivet rows and a spar line on top.
    for s in (-1, 1):
        for y in (-.3, .4):
            for k in range(12):
                rivets.box((.02, .02, .012), loc=(s * (.75 + k * .14), y, 1.602), bevel=0)
        lines.tube([(s * .72, .08, 1.604), (s * 2.3, .08, 1.604)], .007, seg=4)
    # Tail: fin panel lines on both sides, stabiliser rivets.
    for sx in (-1, 1):
        lines.tube([(sx * .083, 4.45, 1.95), (sx * .083, 4.83, 3.35)], .007, seg=4)
        lines.tube([(sx * .083, 4.3, 2.6), (sx * .083, 4.98, 2.6)], .007, seg=4)
        for k in range(8):
            rivets.box((.02, .02, .012), loc=(sx * (.3 + k * .1), 4.2, 1.847), bevel=0)
    # Nose: bolts on the sensor housings; canopy sill rails.
    for s in (-1, 1):
        for dy in (-.1, .1):
            for dz in (-.1, .1):
                hd.bolt(steel, (s * .34, -4.6 + dy, 1.3 + dz), hd.side_rot(s), r=.012, h=.018)
    for sections in (((-4.05, .32, 1.6), (-3.55, .54, 1.7), (-2.68, .56, 1.76)),
                     ((-2.78, .58, 1.78), (-2.4, .6, 1.8), (-1.35, .58, 1.84), (-.95, .46, 1.88))):
        for s in (-1, 1):
            a.part('Canopy_frames', 'Armor').tube([(s * (w + .008), y, z0 + .02) for y, w, z0 in sections], .018, seg=4)
    # Skid clamps, antennas and the chin gun's barrel rings.
    for s in (-1, 1):
        for y in (-1.1, .95):
            steel.box((.1, .1, .14), loc=(s * 1.05, y, .09), bevel=0)
    steel.box((.02, .18, .12), loc=(0, 2.6, 2.02), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))
    steel.box((.02, .16, .1), loc=(0, -1.0, .86), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    ring = a.part('Gun_detail', 'Steel', g)
    for y in (-.95, -1.05, -1.15):
        ring.cyl(.047, .025, loc=(0, y, -.16), rot=FORWARD, seg=8, bevel=0)


def gunship_heli(a):
    """Heavy assault gunship (Mi-24 lineage): stepped tandem bubble canopies with sensor blisters
    and an air-data boom, a troop cabin under twin engines with dust filters and infrared
    suppressors, anhedral stub wings with four rocket pods and tube-launched missiles on the tip
    plates, a five-blade articulated rotor and tricycle wheels. Origin on the ground under the cabin."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    body.loft([
        _octagon(-6.35, .2, .98, 1.26),
        _octagon(-6.0, .46, .84, 1.5),
        _octagon(-5.2, .62, .78, 1.62),
        _octagon(-4.55, .72, .78, 1.74),
        _octagon(-3.6, .84, .8, 2.04),
        _octagon(-3.0, .94, .82, 2.34),
        _octagon(.2, .98, .85, 2.42),
        _octagon(1.4, .82, 1.0, 2.38),
        _octagon(2.35, .48, 1.46, 2.24),
    ], bevel=.07, seg=2)
    body.loft([_octagon(2.1, .46, 1.5, 2.24), _octagon(6.5, .22, 1.76, 2.1)], bevel=.04, seg=1)      # tail boom
    body.prism([(5.35, 2.0), (6.55, 1.94), (7.05, 3.7), (6.45, 3.75)], .18, bevel=.03)              # fin
    body.box((2.5, .72, .1), loc=(0, 5.45, 1.96), bevel=.02, seg=1, taper=(1, .7))                  # stabiliser
    # Stepped tandem canopies: the gunner's bubble low in the nose, the pilot's raised behind it.
    glass.loft([_bubble(-6.12, .26, 1.3, 1.5), _bubble(-5.75, .5, 1.4, 1.98), _bubble(-5.0, .56, 1.5, 2.04),
                _bubble(-4.62, .46, 1.56, 1.86)], bevel=.03, seg=1)
    glass.loft([_bubble(-4.78, .56, 1.6, 2.16), _bubble(-4.3, .64, 1.66, 2.58), _bubble(-3.5, .66, 1.8, 2.64),
                _bubble(-3.05, .56, 1.92, 2.44)], bevel=.03, seg=1)
    for section in (_bubble(-5.7, .51, 1.41, 2.0), _bubble(-5.05, .57, 1.5, 2.06), _bubble(-4.3, .655, 1.66, 2.6),
                    _bubble(-3.55, .67, 1.79, 2.66)):
        _hoop(frames, section)
    panels = a.part('Panels', 'Team')
    for s in (-1, 1):
        for y in (-2.5, -1.9, -1.3):                                                              # cabin windows
            w = .94 + (y + 3.0) * .04 / 3.2
            glass.box((.02, .38, .3), loc=(s * (w + .012), y, 1.72), bevel=0)
        armor.box((.04, 1.1, .38), loc=(s * .78, -4.15, 1.32), bevel=.01, seg=1)                    # cockpit armour
        panels.box((.03, 1.3, .58), loc=(s * .985, -.3, 1.64), bevel=.008, seg=1)                    # cabin doors
        # Flare dispensers on the tail boom, lit by their dark tube faces.
        armor.box((.1, .5, .22), loc=(s * .43, 3.3, 1.9), bevel=.02, seg=1)
        dark.grille(.4, .22, loc=(s * .49, 3.3, 1.9), rot=(0, 0, s * R90), slats=3, depth=.03, thickness=.03)
    # Sensor blisters under the gunner's cockpit and the air-data boom on the right of the nose.
    sensor = a.part('Sensor', 'Glass')
    for s, rr in ((-1, .15), (1, .12)):
        armor.cyl(rr, .5, loc=(s * .52, -5.45, 1.06), rot=FORWARD, seg=10, bevel=.03, bseg=1)
        sensor.cyl(rr * .7, .03, loc=(s * .52, -5.71, 1.06), rot=FORWARD, seg=10, bevel=0)
    steel.tube([(.32, -5.9, 1.3), (.36, -6.35, 1.36), (.38, -6.72, 1.4)], .025, seg=6)
    steel.cyl(.05, .1, loc=(.38, -6.5, 1.39), rot=FORWARD, seg=6, bevel=0)
    # Twin engines over the cabin: dust-filter domes on intake rings, suppressor exhausts, gearbox.
    for s in (-1, 1):
        body.cyl(.4, 3.4, loc=(s * .52, -.9, 2.66), rot=FORWARD, seg=14, bevel=.1)
        armor.sphere((.34, .3, .34), loc=(s * .52, -2.6, 2.66), seg=12, rings=6)
        steel.torus(.36, .04, loc=(s * .52, -2.62, 2.66), rot=FORWARD, seg=14, ring=4)
        _exhaust_duct(a, (s * .86, 1.05, 2.7), s * -.35, size=(.36, .8, .4), pitch=.15)
    body.box((.9, 2.4, .5), loc=(0, -.7, 2.78), bevel=.1, taper=(.7, .8))
    steel.cyl(.13, .7, loc=(0, -.7, 3.2), seg=10, bevel=0)
    armor.box((.3, .3, .2), loc=(0, 1.6, 2.5), bevel=.04, seg=1)                                    # IR jammer
    sensor.box((.24, .24, .12), loc=(0, 1.6, 2.64), bevel=.03, seg=1)
    # Anhedral stub wings: two rocket pods each, missile launch tubes on the tip plates.
    pylons = a.part('Pylons', 'Armor')
    tubes = a.part('Launch_tubes', 'Fuel')
    droop = math.tan(.2)

    def wing_z(x):
        return 1.72 - (x - .9) * droop
    for s in (-1, 1):
        body.limb((s * .8, 0, wing_z(.8)), (s * 3.25, 0, wing_z(3.25)), .16, 1.3, bevel=.04, seg=1, taper=(1, .75))
        for x in (1.52, 2.5):
            z = wing_z(x)
            _pylon(pylons, s * x, -.45, .45, z + .02, z - .3, w=.12)
            _rocket_pod(a, s * x, -.9, z - .54, .26, 1.6, tubes=7)
        z = wing_z(3.25)
        armor.box((.1, 1.2, .7), loc=(s * 3.3, -.05, z - .2), bevel=.02, seg=1)                        # tip plate
        for zz in (z - .05, z - .38):
            # The upper tube launches (Launch_tubes); the lower one is drawn the same (Spare_tubes).
            (tubes if zz == z - .05 else a.part('Spare_tubes', 'Fuel')).cyl(.09, 1.25, loc=(s * 3.435, -.18, zz), rot=FORWARD,
                                                                           seg=10, bevel=.015, bseg=1)
            _tube_mouth(a, None, _frame((s * 3.435, -.8, zz), FORWARD), .085, protrude=.04, seg=8, name='Tube_rims')
            a.part('Missile_bands', 'Hazard').cyl(.1, .05, loc=(s * 3.435, .2, zz), rot=FORWARD, seg=10, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .14, .06), loc=(s * 3.36, .5, z + .17), bevel=.01, seg=1)
    a.pivot('Muzzle_rocket', (0, -.97, (wing_z(1.6) + wing_z(2.45)) / 2 - .54))
    a.pivot('Muzzle_missile', (0, -.86, wing_z(3.25) - .05))
    # Door gunners at the troop cabin's windows, left (+X) and right (-X).
    a.pivot('Muzzle_door_l', (1.02, -1.0, 1.62))
    a.pivot('Muzzle_door_r', (-1.02, -1.0, 1.62))
    # Tricycle landing gear (the retractable kind, shown down): twin nose wheels, mains behind the wings.
    gear = a.part('Gear', 'Steel')
    tyres = a.part('Tyres', 'Rubber')
    for x in (-.17, .17):
        tyres.cyl(.26, .14, loc=(x, -4.9, .26), rot=ACROSS, seg=10, bevel=.05, bseg=1)
        gear.cyl(.12, .2, loc=(x * 1.02, -4.9, .26), rot=ACROSS, seg=8, bevel=0)
    gear.cyl(.05, .5, loc=(0, -4.9, .26), rot=ACROSS, seg=6, bevel=0)
    gear.limb((0, -4.9, .26), (0, -4.75, .9), .1, .1, bevel=.02, seg=1)
    for s in (-1, 1):
        tyres.cyl(.36, .24, loc=(s * 1.22, 1.1, .36), rot=ACROSS, seg=12, bevel=.07, bseg=1)
        gear.cyl(.17, .26, loc=(s * 1.22, 1.1, .36), rot=ACROSS, seg=8, bevel=0)
        gear.limb((s * 1.08, 1.1, .36), (s * .76, .9, 1.25), .12, .12, bevel=.02, seg=1)            # oleo
        gear.limb((s * 1.08, 1.1, .36), (s * .72, 1.7, 1.12), .08, .08, bevel=.015, seg=1)          # drag brace
    a.part('Lamps', 'Lamp').box((.2, .14, .06), loc=(0, -4.3, .79), bevel=.01, seg=1)
    steel.cyl(.015, .6, loc=(0, 3.5, 2.36), seg=5, bevel=0)                                           # antenna
    steel.box((.02, .22, .15), loc=(0, -2.0, .8), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 6.72, 3.8), seg=8, rings=5)

    # Four-barrel chin gun on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -5.55, .8))
    a.part('Gun_turret', 'Armor', g).sphere(.3, loc=(0, 0, -.04), seg=12, rings=8)
    gun = a.part('Gun', 'Steel', g)
    gun.cyl(.11, .16, loc=(0, -.32, -.1), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        gun.cyl(.035, 1.0, loc=(math.cos(ang) * .06, -.82, -.1 + math.sin(ang) * .06), rot=FORWARD, seg=6, bevel=0)
    gun.cyl(.1, .08, loc=(0, -.62, -.1), rot=FORWARD, seg=10, bevel=0)
    gun.cyl(.1, .08, loc=(0, -1.22, -.1), rot=FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_gun', (0, -1.34, -.1), g)

    # Five-blade main rotor.
    r = a.pivot('Rotor', (0, -.7, 3.55))
    _rotor_head(a, r, 5, 6.2, .44, hub=.36, phase=R90, t=.06, cap=.24, stripe=.34, droop=.1)
    # Three-blade tail rotor on the right of the fin, blades in the YZ plane.
    armor.cyl(.12, .2, loc=(.17, 6.62, 3.0), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    tr = a.pivot('Tail_rotor', (.32, 6.62, 3.0))
    _tail_rotor(a, tr, 3, 1.08, .2, side=1)


def scout_heli(a):
    """Light scout helicopter (MH-6 lineage): egg-shaped cabin under a glass blister with a FLIR
    ball on the chin, slim tail boom with a T-tail and a tail skid, a six-blade rotor, and a weapon
    plank carrying a six-barrel minigun and a rocket pod on each side. Origin on the ground under
    the cabin (skids at z = 0)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    egg = [(-1.95, .3, 1.12, .34), (-1.7, .52, 1.17, .54), (-1.3, .66, 1.22, .67), (-.8, .73, 1.26, .73),
           (-.2, .73, 1.28, .73), (.4, .64, 1.32, .64), (.9, .46, 1.42, .48), (1.25, .26, 1.52, .3)]
    body.loft([[(0, -2.08, 1.1)]] + [_ring(*e) for e in egg])
    # Glass blister 2 cm proud of the egg's upper front (no z-fighting), framed where it ends.
    glass.loft([_arc(y, w + .02, zc, h + .02) for y, w, zc, h in egg[:4]])
    a.part('Canopy_frames', 'Team').tube(_arc(-.8, .765, 1.26, .765), .035, seg=6)
    a.part('Canopy_frames', 'Team').tube([(0, y, zc + h + .03) for y, w, zc, h in egg[:4]], .025, seg=5)
    # Door frames behind the blister.
    for s in (-1, 1):
        a.part('Canopy_frames', 'Team').tube([(s * .39, .3, .8), (s * .66, .3, 1.33), (s * .39, .3, 1.85)], .03, seg=5)
    body.loft([_ring(1.0, .25, 1.52, .25, seg=8), _ring(5.0, .12, 1.68, .12, seg=8)], bevel=0)      # tail boom
    body.prism([(4.5, 1.62), (5.1, 1.62), (5.25, 2.3), (4.95, 2.32)], .08, bevel=.02)                # upper fin
    body.prism([(4.62, 1.62), (5.02, 1.62), (5.14, 1.12), (4.96, 1.1)], .08, bevel=.02)               # lower fin
    body.box((1.5, .42, .06), loc=(0, 5.12, 2.3), bevel=.02, seg=1, taper=(1, .7))                  # T-tail
    for s in (-1, 1):
        armor.box((.05, .3, .26), loc=(s * .76, 5.12, 2.3), bevel=.01, seg=1)                        # end plates
    steel.tube([(0, 4.9, 1.2), (0, 5.25, .98), (0, 5.4, 1.0)], .018, seg=5)                          # tail skid
    body.box((.62, 1.2, .38), loc=(0, .3, 2.03), bevel=.12, taper=(.8, .8))                         # engine hump
    a.part('Panels', 'Team').box((.24, .6, .04), loc=(0, .4, 2.23), bevel=.01, seg=1)             # engine door
    dark.grille(.3, .12, loc=(0, -.26, 2.08), slats=3, depth=.05, thickness=.03)                   # intake
    steel.lathe([(.11, -.1), (.11, .2), (.08, .2), (.08, -.05)], loc=(0, .95, 1.98), rot=BACKWARD, seg=10)  # exhaust
    dark.cyl(.075, .02, loc=(0, 1.1, 1.98), rot=FORWARD, seg=10, bevel=0)
    steel.cyl(.08, .42, loc=(0, 0, 2.38), seg=10, bevel=0)                                         # mast
    a.part('Lamps', 'Lamp').box((.14, .1, .05), loc=(0, -1.55, .64), bevel=.01, seg=1)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 5.2, 2.36), seg=8, rings=5)
    steel.cyl(.012, .5, loc=(.12, 1.6, 1.95), seg=5, bevel=0)                                       # whip antenna
    # FLIR ball on the chin.
    armor.cyl(.05, .14, loc=(0, -1.98, .78), seg=8, bevel=0)
    armor.sphere(.13, loc=(0, -1.98, .62), seg=12, rings=8)
    a.part('Sensor', 'Glass').cyl(.06, .04, loc=(0, -2.1, .63), rot=FORWARD, seg=10, bevel=0)
    # Skids on arched cross tubes.
    skids = a.part('Skids', 'Undercarriage')
    for s in (-1, 1):
        x = s * .92
        skids.tube([(x, 1.05, .05), (x, -1.45, .05), (x, -1.72, .14), (x, -1.84, .3)], .05, seg=8)
        skids.tube([(x, -.95, .05), (s * .86, -.95, .45), (s * .45, -.95, .72)], .04, seg=6)
        skids.tube([(x, .45, .05), (s * .86, .45, .45), (s * .35, .45, .9)], .04, seg=6)
    # Weapon plank through the cabin: a six-barrel minigun inboard and a rocket pod outboard.
    armor.box((2.7, .24, .12), loc=(0, -.35, .84), bevel=.03, seg=1)
    guns = a.part('Miniguns', 'Steel')
    feed = a.part('Gun_feed', 'Undercarriage')
    for s in (-1, 1):
        x = s * 1.0
        armor.box((.08, .18, .14), loc=(x, -.35, .72), bevel=.01, seg=1)                             # hanger
        guns.box((.17, .52, .19), loc=(x, -.4, .6), bevel=.03, seg=1)                               # motor, feed
        for k in range(6):
            ang = k * math.tau / 6
            guns.cyl(.02, .92, loc=(x + math.cos(ang) * .045, -1.08, .6 + math.sin(ang) * .045), rot=FORWARD, seg=5,
                     bevel=0)
        guns.cyl(.085, .06, loc=(x, -.8, .6), rot=FORWARD, seg=8, bevel=0)                          # barrel clamps
        guns.cyl(.085, .08, loc=(x, -1.46, .6), rot=FORWARD, seg=8, bevel=0)
        feed.tube([(x - s * .05, -.3, .69), (s * .75, -.25, .85), (s * .55, -.2, 1.0)], .04, seg=6)
        x = s * 1.32
        armor.box((.08, .3, .14), loc=(x, -.4, .74), bevel=.01, seg=1)
        _rocket_pod(a, x, -1.05, .6, .17, 1.1)
    a.pivot('Muzzle_gun', (0, -1.54, .6))
    a.pivot('Muzzle_rocket', (0, -1.1, .6))

    # Six-blade main rotor.
    r = a.pivot('Rotor', (0, 0, 2.6))
    _rotor_head(a, r, 6, 4.0, .26, hub=.22, t=.04, cap=.14, stripe=.24, droop=.05)
    # Two-blade tail rotor on the left of the fin.
    armor.cyl(.07, .14, loc=(-.09, 5.0, 1.72), rot=ACROSS, seg=8, bevel=.01, bseg=1)
    tr = a.pivot('Tail_rotor', (-.2, 5.0, 1.72))
    _tail_rotor(a, tr, 2, .6, .12, phase=.3, side=-1)


# ----------------------------------------------------------------------------- fixed-wing kit
def _naca(u):
    """NACA 00xx half-thickness at chord fraction u, normalised to 1 where it is thickest (u = .3)."""
    u = min(1.0, max(0.0, u))
    return 10 * (.2969 * math.sqrt(u) - .126 * u - .3516 * u ** 2 + .2843 * u ** 3 - .1015 * u ** 4)


FOIL_U = (0, .03, .1, .2, .32, .46, .62, .78, .9, 1)


class Planform:
    """Straight-tapered lifting surface between spans s0 and s1: leading edge at y = le, chord c
    running rearwards (+Y), thickness t and chord-line height h (dihedral) at each end."""

    def __init__(self, s0, s1, le0, le1, c0, c1, t0, t1, h0=0.0, h1=None):
        self.s0, self.s1 = s0, s1
        self.v0, self.v1 = (le0, c0, t0, h0), (le1, c1, t1, h0 if h1 is None else h1)

    def at(self, s):
        k = (s - self.s0) / (self.s1 - self.s0)
        return tuple(a + (b - a) * k for a, b in zip(self.v0, self.v1))

    def le(self, s):
        return self.at(s)[0]

    def te(self, s):
        le, c, _, _ = self.at(s)
        return le + c

    def top(self, s, u=.3):
        """Upper-surface height at span s and chord fraction u (for mounting parts on the skin)."""
        _, _, t, h = self.at(s)
        return h + t / 1.72 * _naca(u)

    def bottom(self, s, u=.3):
        _, _, t, h = self.at(s)
        return h - t * .72 / 1.72 * _naca(u)


def _foil(pf, s, ua=0.0, ub=1.0, lower=.72):
    """Airfoil ring (span, y, normal) at span s between chord fractions ua and ub: over the upper
    surface from ub to ua, back along the lower one. A panel cut short at ua > 0 or ub < 1 gets a
    blunt face there (control-surface hinge lines)."""
    le, c, t, h = pf.at(s)
    cut = [ua] + [u for u in FOIL_U if ua + .02 < u < ub - .02] + [ub]
    up, lo = t / (1 + lower), t * lower / (1 + lower)
    ring = [(s, le + u * c, h + max(up * _naca(u), .007)) for u in reversed(cut)]
    ring += [(s, le + u * c, h - max(lo * _naca(u), .007)) for u in (cut[1:] if ua == 0 else cut)]
    return ring


def _surface(part, pf, frame, stations=None, ua=0.0, ub=1.0, lower=.72, bevel=.012, ends=(False, True)):
    """Loft an airfoil panel through span stations (default both ends), mapped into the model by
    frame(s, y, n) -> (x, y, z). ends says which end caps show: a buried root or an internal joint
    keeps its edges unbevelled (bevels there only cost triangles)."""
    rings = [[frame(*p) for p in _foil(pf, s, ua, ub, lower)] for s in (stations or (pf.s0, pf.s1))]
    _loft(part, rings, bevel, ends)


def _loft(part, rings, bevel, ends=(True, True)):
    """Shape.loft whose end-cap edges are bevelled only where `ends` says the cap shows."""
    part.loft(rings, bevel=0)
    if bevel <= 0:
        return
    bm = part.bm
    bm.verts.ensure_lookup_table()
    verts = list(bm.verts)[-sum(len(r) for r in rings):]
    first, last = set(verts[:len(rings[0])]), set(verts[-len(rings[-1]):])
    keep = [v for v in verts if (ends[0] or v not in first) and (ends[1] or v not in last)]
    if not ends[0] and not ends[1]:
        keep = [v for v in verts if v not in first and v not in last] or keep
    edges = {e for v in keep for e in v.link_edges}
    skip = (set() if ends[0] else first) | (set() if ends[1] else last)
    edges = [e for e in edges if not (e.verts[0] in skip and e.verts[1] in skip)
             and e.is_manifold and e.calc_face_angle(0) > math.radians(35)]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, offset_type='OFFSET', segments=1, profile=.5, affect='EDGES',
                        clamp_overlap=True)


def _wing(box, moving, pf, frame, cs=(), gap=.035, lower=.72, bevel=.012, root=False):
    """Lifting surface with control surfaces: cs = [(s0, s1, f)] hinges a surface behind chord
    fraction f between spans s0 and s1, with a `gap` slot all round it; elsewhere the fixed box
    runs to the trailing edge. The root is buried in the body unless root=True."""
    cuts = sorted({pf.s0, pf.s1, *(v for a, b, _ in cs for v in (a, b))})
    runs = []
    for a, b in zip(cuts, cuts[1:]):
        f = next((f for s0, s1, f in cs if s0 - 1e-6 <= a and b <= s1 + 1e-6), 1.0)
        if runs and runs[-1][1] == f:
            runs[-1][0].append(b)
        else:
            runs.append(([a, b], f))
    for i, (stations, f) in enumerate(runs):
        _surface(box, pf, frame, stations, 0.0, f, lower, bevel, (root and i == 0, i == len(runs) - 1))
    for s0, s1, f in cs:
        c = min(pf.at(s0)[1], pf.at(s1)[1])
        _surface(moving, pf, frame, (s0 + gap / 2, s1 - gap / 2), f + gap / c, 1.0, lower, 0, (True, True))


def _skin_offsets(pts, out, inn):
    """Offset an upper-skin polyline [(y, z)...] (running aft) along its normals: returns the outer
    line and the inner line, so a panel stays `out` clear of steep leading-edge facets too."""
    top, bot = [], []
    for i, (y, z) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        dy, dz = b[0] - a[0], b[1] - a[1]
        k = math.hypot(dy, dz) or 1.0
        ny, nz = -dz / k, dy / k
        top.append((y + ny * out, z + nz * out))
        bot.append((y - ny * inn, z - nz * inn))
    return top, bot


def _skin_panel(part, pf, frame, s0, s1, u0, u1, out=.02, inn=.012, lower=.72, stations=None):
    """Access panel standing `out` proud of a surface's upper skin between spans s0..s1 and chord
    fractions u0..u1; its bevelled edge and baked occlusion draw the panel line. `stations` runs a
    long strip through the surface loft's own stations so its facets stay parallel to the skin."""
    loops = []
    us = [u0] + [u for u in FOIL_U if u0 + .02 < u < u1 - .02] + [u1]
    for s in (stations or (s0, s1)):
        le, c, t, h = pf.at(s)
        up = t / (1 + lower)
        top, bot = _skin_offsets([(le + u * c, h + max(up * _naca(u), .007)) for u in us], out, inn)
        loops.append([frame(s, y, z) for y, z in top + bot[::-1]])
    part.loft(loops, bevel=.005, seg=1)


def RIGHT(s, y, n):
    return (s, y, n)


def LEFT(s, y, n):
    return (-s, y, n)


def _upright(x0, z0, cant=0.0):
    """Frame for a fin rising from (x0, z0) and leaning outwards (away from x = 0) by cant radians;
    span s runs up the fin, the airfoil thickness across it."""
    sx = 1.0 if x0 >= 0 else -1.0
    dx, dz = sx * math.sin(cant), math.cos(cant)     # up the fin
    nx, nz = sx * math.cos(cant), -math.sin(cant)    # across it, outwards

    def frame(s, y, n):
        return (x0 + dx * s + nx * n, y, z0 + dz * s + nz * n)
    return frame


def _sec(y, w, zb, zt, zc=None, n=16, pt=2.4, pb=2.8):
    """Superelliptic fuselage section at y: half-width w, belly zb, spine zt, widest at zc (default
    mid-height). pt / pb shape the upper / lower halves (2 = ellipse, higher = boxier). Points start
    under the belly (x = 0) and run through +x."""
    zc = (zb + zt) / 2 if zc is None else zc
    ring = []
    for i in range(n):
        u = -R90 + i * math.tau / n
        c, s = math.cos(u), math.sin(u)
        p = pt if s > 0 else pb
        x = w * math.copysign(abs(c) ** (2 / p), c)
        z = zc + ((zt - zc) if s > 0 else (zc - zb)) * math.copysign(abs(s) ** (2 / p), s)
        ring.append((x, y, z))
    return ring


def _dome(y, w, z0, z1, n=9, p=2.3):
    """Upper half of a superellipse from the right sill over the crown to the left one (closed along
    its base): canopies, spine fairings, sensor blisters."""
    out = []
    for i in range(n):
        u = math.pi * i / (n - 1)
        c, s = math.cos(u), math.sin(u)
        out.append((w * math.copysign(abs(c) ** (2 / p), c), y, z0 + (z1 - z0) * abs(s) ** (2 / p)))
    return out


def _ring_at(rings, y):
    """Loft ring at y, interpolated between stations (constant-y rings of equal size)."""
    ys = [r[0][1] for r in rings]
    for a, b, ya, yb in zip(rings, rings[1:], ys, ys[1:]):
        if ya - 1e-6 <= y <= yb + 1e-6:
            k = (y - ya) / (yb - ya)
            return [tuple(p + (q - p) * k for p, q in zip(pa, pb)) for pa, pb in zip(a, b)]
    raise ValueError(f'y = {y} outside the loft ({ys[0]} .. {ys[-1]})')


def _skin_z(rings, y, x):
    """Height of the loft's upper skin at (x, y)."""
    ring = _ring_at(rings, y)
    zc = sum(p[2] for p in ring) / len(ring)
    upper = sorted((p for p in ring if p[2] >= zc), key=lambda p: p[0])
    for p, q in zip(upper, upper[1:]):
        if p[0] <= x <= q[0]:
            k = (x - p[0]) / ((q[0] - p[0]) or 1e-9)
            return p[2] + (q[2] - p[2]) * k
    return upper[-1][2] if x > 0 else upper[0][2]


def _patch(part, rings, y0, y1, i0, i1, out=.016, inn=.014, bevel=.006):
    """Thin panel hugging a lofted body: ring points i0..i1 (inclusive, wrapping) of every station
    between y0 and y1, offset `out` proud of the skin. Anti-glare panels, air brakes, walkways."""
    ys = [r[0][1] for r in rings]
    sel = [_ring_at(rings, y0)] + [r for r, y in zip(rings, ys) if y0 + .02 < y < y1 - .02] + [_ring_at(rings, y1)]
    loops = []
    for ring in sel:
        n = len(ring)
        cx, cz = sum(p[0] for p in ring) / n, sum(p[2] for p in ring) / n
        outer, inner = [], []
        for i in ((i0 + k) % n for k in range((i1 - i0) % n + 1)):
            p = Vector(ring[i])
            t = Vector(ring[(i + 1) % n]) - Vector(ring[i - 1])
            nrm = Vector((t.z, 0, -t.x)).normalized()
            if nrm.dot(Vector((p.x - cx, 0, p.z - cz))) < 0:
                nrm = -nrm
            outer.append(tuple(p + nrm * out))
            inner.append(tuple(p - nrm * inn))
        loops.append(outer + inner[::-1])
    part.loft(loops, bevel=bevel, seg=1)


def _canopy(glass, frames, stations, bows=(), r=.024, n=9):
    """Glass bubble lofted through (y, half-width, sill z, crown z) stations, framed by hoops at the
    listed y and sill rails along both lower edges."""
    glass.loft([_dome(y, w, z0, z1, n) for y, w, z0, z1 in stations], bevel=.02, seg=1)
    rings = [_dome(y, w + .004, z0, z1 + .004, n) for y, w, z0, z1 in stations]
    for y in bows:
        frames.tube(_ring_at(rings, y), r, seg=6)
    for i in (0, n - 1):
        frames.tube([ring[i] for ring in rings], r * .9, seg=6)


# ----------------------------------------------------------------------------- high-detail kit
# Panel lines, rivets and small fittings for the `_hd` aircraft (see mb_detail.py). Lines are thin dark
# tubes standing just proud of the skin; rivets are tiny flat plates. Nothing here is added to a part the
# runtime measures (Pods, Missiles ...), and all of it stays inside the model's bounds.
def _skin_point(rings, y, i, u=0.0, out=0.0):
    """Point on a loft (constant-y rings) at station y, a fraction u from ring point i towards i + 1,
    pushed `out` along the outward normal; returns (point, normal)."""
    ring = _ring_at(rings, y)
    n = len(ring)
    cx, cz = sum(q[0] for q in ring) / n, sum(q[2] for q in ring) / n
    p0, p1 = Vector(ring[i % n]), Vector(ring[(i + 1) % n])
    p = p0.lerp(p1, u)
    t = p1 - p0 if u else Vector(ring[(i + 1) % n]) - Vector(ring[(i - 1) % n])
    nrm = Vector((t.z, 0, -t.x)).normalized()
    if nrm.dot(Vector((p.x - cx, 0, p.z - cz))) < 0:
        nrm = -nrm
    return p + nrm * out, nrm


def _hoop_line(part, rings, y, idx, r=.009, out=.003, us=(0.0,)):
    """Panel line round a loft at station y through ring points idx (each at the fractions us towards
    the next point: (.2, .8) keeps a line on the flats of a heavily bevelled loft)."""
    pts = [tuple(_skin_point(rings, y, i, u, out + r * .4)[0]) for i in idx for u in us]
    part.tube(pts, r, seg=4)


def _seam_line(part, rings, y0, y1, i, u=.5, r=.009, out=.003):
    """Panel line along a loft from station y0 to y1, a fraction u between ring points i and i + 1."""
    ys = [y0] + [q[0][1] for q in rings if y0 + .02 < q[0][1] < y1 - .02] + [y1]
    part.tube([tuple(_skin_point(rings, y, i, u, out + r * .4)[0]) for y in ys], r, seg=4)


def _rivet_row(part, rings, y0, y1, i, n, u=.5, size=.022, out=.002):
    """n flush rivet heads along a loft between y0 and y1, a fraction u between ring points i and i + 1
    (out lifts them onto a panel standing proud of the skin)."""
    for k in range(n):
        y = y0 + (y1 - y0) * (k + .5) / n
        p, nrm = _skin_point(rings, y, i, u, out)
        part.box((size, size, .012), loc=tuple(p), rot=Vector((0, 0, 1)).rotation_difference(nrm).to_euler('XYZ'),
                 bevel=0)


def _foil_z(pf, s, u, side=1, lower=.72):
    le, c, t, h = pf.at(s)
    up, lo = t / (1 + lower), t * lower / (1 + lower)
    return le + u * c, (h + max(up * _naca(u), .007)) if side > 0 else (h - max(lo * _naca(u), .007))


def _wing_line(part, pf, frame, s0, s1, u, side=1, lower=.72, r=.008, out=.003):
    """Spanwise panel line on a lifting surface's upper (side 1) or lower (-1) skin at chord fraction u."""
    pts = []
    for sp in (s0, s1):
        y, z = _foil_z(pf, sp, u, side, lower)
        pts.append(frame(sp, y, z + side * (out + r * .4)))
    part.tube(pts, r, seg=4)


def _wing_rib(part, pf, frame, sp, u0, u1, side=1, lower=.72, r=.007, out=.003):
    """Chordwise panel line (a rib line) at span sp from chord fraction u0 to u1."""
    us = [u0] + [u for u in FOIL_U if u0 + .02 < u < u1 - .02] + [u1]
    pts = []
    for u in us:
        y, z = _foil_z(pf, sp, u, side, lower)
        pts.append(frame(sp, y, z + side * (out + r * .4)))
    part.tube(pts, r, seg=4)


def _wing_rivets(part, pf, frame, s0, s1, u, n, lower=.72, size=.02):
    """n rivet heads along the upper skin of a (roughly horizontal) surface at chord fraction u."""
    for k in range(n):
        sp = s0 + (s1 - s0) * (k + .5) / n
        y, z = _foil_z(pf, sp, u, 1, lower)
        part.box((size, size, .012), loc=frame(sp, y, z + .002), bevel=0)


def _dischargers(part, pf, frame, spans, length=.13):
    """Static discharger wicks trailing from the trailing edge at the given spans."""
    for sp in spans:
        le, c, t, h = pf.at(sp)
        part.tube([frame(sp, le + c - .03, h), frame(sp, le + c + length, h)], .006, seg=4)


def _squircle(w, h, n=12):
    """Rounded-rectangle outline (superellipse, exponent 4) starting at +x, counter-clockwise."""
    return [(w * math.copysign(abs(math.cos(u)) ** .5, math.cos(u)),
             h * math.copysign(abs(math.sin(u)) ** .5, math.sin(u)))
            for u in (i * math.tau / n for i in range(n))]


def _duct(xc, y, zc, w, h, n=12):
    """Intake trunk ring at y matching _squircle's point order (x across, z up)."""
    return [(xc + px, y, zc + pz) for px, pz in _squircle(w, h, n)]


def _intake(a, body, lip, dark, centre, w, h, rake, rings, depth=.32, wall=.055, n=12):
    """Raked air intake: an open lip duct `depth` long in front of a trunk lofted through `rings`
    (_duct rings) rearwards, with a dark compressor face inside. centre = (x, y, z) of the mouth's
    back plane; rake tilts the mouth so the upper lip leads."""
    outline = _squircle(w, h, n)
    rot = (R90 + rake, 0, 0)
    m = _frame(centre, rot)
    first = [tuple(m @ Vector((px, py, 0))) for px, py in outline]
    body.loft([first] + rings, bevel=.03, seg=1)
    lip.shell(outline, depth, wall, loc=centre, rot=rot, bevel=.012, seg=1)
    dark.box((w * 1.6, h * 1.6, .03), loc=tuple(m @ Vector((0, 0, .03))), rot=rot, bevel=0)


def _nozzle(a, x, y, z, r, length, seg=16, glow=True):
    """Afterburning nozzle from y (its root buried in the body) rearwards: steel shroud with a
    lip, dark liner and glowing flame-holder rings deep inside."""
    a.part('Nozzles', 'Steel').lathe([(r * 1.04, -.15), (r, length * .3), (r * .86, length), (r * .8, length),
                                      (r * .8, length * .3)], loc=(x, y, z), rot=BACKWARD, seg=seg)
    # Dark petal sleeve over the converging section; it ends 1.5 cm behind the shroud lip.
    ro0, ro1 = r * .976, r * .86
    _revolve(a.part('Nozzle_petals', 'Armor'), [(ro0 + .012, length * .42), (ro1 + .012, length + .015),
                                                (ro1 - .012, length + .015), (ro0 - .012, length * .42)],
             (x, y, z), BACKWARD, seg)
    a.part('Nozzle_liners', 'Undercarriage').lathe([(r * .75, length * .34), (r * .75, length - .02),
                                                     (r * .69, length - .02), (r * .69, length * .5), (0, length * .5)],
                                                    loc=(x, y, z), rot=BACKWARD, seg=seg)
    if glow:
        g = a.part('Exhaust_glow', 'Alloy')
        g.torus(r * .45, r * .07, loc=(x, y + length * .5 + .02, z), rot=FORWARD, seg=seg, ring=4)
        g.cyl(r * .16, .04, loc=(x, y + length * .5 + .03, z), rot=FORWARD, seg=8, bevel=0)
    if hd.on(a):  # petal seams over the sleeve and actuator rods on the shroud
        seams = a.part('Nozzle_seams', 'Undercarriage')
        acts = a.part('Nozzle_actuators', 'Steel')
        for k in range(seg):
            u = (k + .5) * math.tau / seg
            c, sn = math.cos(u), math.sin(u)
            seams.tube([(x + c * (r * .976 + .014), y + length * .44, z + sn * (r * .976 + .014)),
                        (x + c * (r * .86 + .014), y + length + .005, z + sn * (r * .86 + .014))], .007, seg=4)
            if k % 4 == 1:
                acts.tube([(x + c * (r * 1.03), y + length * .08, z + sn * (r * 1.03)),
                           (x + c * (r * .985), y + length * .38, z + sn * (r * .985))], .014, seg=4)


def _revolve(part, loop, loc, rot, seg=16):
    """Watertight ring revolved about local Z from a closed (radius, z) loop, with no end caps:
    nozzle petal sleeves, cowl bands, lip rings."""
    m = _frame(loc, rot)
    bm = part.bm
    rings = [[bm.verts.new(tuple(m @ Vector((r * math.cos(u), r * math.sin(u), z)))) for r, z in loop]
             for u in (i * math.tau / seg for i in range(seg))]
    n, faces = len(loop), []
    for i in range(seg):
        a, b = rings[i], rings[(i + 1) % seg]
        faces += [bm.faces.new((a[j], b[j], b[(j + 1) % n], a[(j + 1) % n])) for j in range(n)]
    bmesh.ops.recalc_face_normals(bm, faces=faces)


def _trap_fin(part, root, phi, r0, span, c0, c1, sweep, thick):
    """Trapezoidal fin on a body lying along Y: root chord c0 at radius r0 with its leading edge at
    y = root[1], tip chord c1 `span` further out and swept back by `sweep`; phi is the angle around
    the body axis from +Z (towards +X)."""
    x, y, z = root
    prof = [(y, r0), (y + sweep, r0 + span), (y + sweep + c1, r0 + span), (y + c0, r0)]
    part.prism(prof, thick, loc=(x, 0, z), rot=(0, phi, 0), bevel=0)


def _bomb(p, loc, length=1.6, r=.17, seg=10, guided=False, band=True, kit=None, lean=False):
    """Low-drag general-purpose bomb (nose at -Y) on parts p = dict(body=, band=, steel=, glass=):
    ogive nose with fuze, parallel body, boat tail with four fins, a yellow nose band, lugs on top.
    guided=True adds a laser seeker with canards; kit='jdam' a tail kit with strakes; lean=True
    drops the lugs and some sections (bombs packed on a bay rack)."""
    x, y, z = loc
    h = length / 2
    prof = ([(r * .36, -h * .98), (r * .7, -h * .5), (r, -h * .2), (r, h * .3), (r * .62, h * .8), (r * .2, h)] if lean
            else [(r * .36, -h * .98), (r * .42, -h * .86), (r * .7, -h * .5), (r, -h * .2), (r, h * .3),
                  (r * .88, h * .56), (r * .6, h * .8), (r * .3, h * .94), (r * .18, h)])
    p['body'].lathe(prof, loc=loc, rot=FORWARD, seg=seg)
    fin_len = length * (.26 if kit == 'jdam' else .22)
    for k in range(4):
        _trap_fin(p['body'], (x, y + h - fin_len - .02, z), math.pi / 4 + k * R90, r * .3, r * .78, fin_len,
                  fin_len * .55, fin_len * .4, .018)
    if band:
        p['band'].cyl(r + .012, length * .04, loc=(x, y - h * .38, z), rot=FORWARD, seg=seg, bevel=0)
    if kit == 'jdam':
        for s in (-1, 1):  # body strakes of the guidance kit
            p['body'].box((.06, length * .3, .016), loc=(x + s * (r + .01), y - h * .05, z), bevel=0)
    if guided:
        p['glass'].sphere(r * .3, loc=(x, y - h - r * .05, z), seg=8, rings=5)
        p['steel'].cyl(r * .34, r * .5, loc=(x, y - h + r * .12, z), rot=FORWARD, seg=seg, bevel=0)
        for k in range(4):
            _trap_fin(p['body'], (x, y - h + r * .45, z), math.pi / 4 + k * R90, r * .3, r * .5, r * .9, r * .45,
                      r * .35, .016)
    else:
        p['steel'].cyl(r * .17, r * .4, r2=r * .08, loc=(x, y - h - r * .12, z), rot=FORWARD, seg=6, bevel=0)
    for dy in (() if lean else (-length * .16, length * .16)):
        p['steel'].box((.04, .07, .05), loc=(x, y + dy, z + r + .012), bevel=0)


def _aam(p, loc, length=2.0, r=.065, seg=8, canards=True, fin=2.1):
    """Air-to-air missile (nose at -Y) on parts p = dict(body=, fins=, nose=, band=): body, seeker
    dome, mid canards, tail fins and a warhead band."""
    x, y, z = loc
    h = length / 2
    p['body'].lathe([(r * .8, h), (r, h * .94), (r, -h * .78), (r * .82, -h * .9)], loc=loc, rot=BACKWARD, seg=seg)
    p['nose'].lathe([(r * .83, -h * .88), (r * .55, -h * .97), (0, -h)], loc=loc, rot=BACKWARD, seg=seg)
    p['band'].cyl(r + .011, length * .035, loc=(x, y - h * .62, z), rot=FORWARD, seg=seg, bevel=0)
    for k in range(4):
        phi = math.pi / 4 + k * R90
        _trap_fin(p['fins'], (x, y + h * .72, z), phi, r * .6, r * fin, length * .13, length * .06, length * .07, .014)
        if canards:
            _trap_fin(p['fins'], (x, y - h * .62, z), phi, r * .6, r * 1.3, length * .07, length * .03, length * .04,
                      .012)


def _pylon(part, x, y0, y1, ztop, zbot, w=.08):
    """Streamlined store pylon from the skin (ztop, buried) down to zbot, chord y0..y1."""
    part.prism([(y0 + .12, ztop), (y0, zbot + .04), (y0 + .1, zbot), (y1 - .15, zbot), (y1, ztop)], w,
               loc=(x, 0, 0), bevel=0)


# ----------------------------------------------------------------------------- jets
def _store_parts(a, parent=None, prefix='Bomb'):
    return dict(body=a.part(f'{prefix}_bodies', 'Armor', parent), band=a.part(f'{prefix}_bands', 'Hazard', parent),
                steel=a.part(f'{prefix}_fuzes', 'Steel', parent), glass=a.part(f'{prefix}_seekers', 'Glass', parent))


def _aam_parts(a, name='Missiles'):
    return dict(body=a.part(name, 'Fuel'), fins=a.part(f'{name[:-1]}_fins', 'Armor'),
                nose=a.part(f'{name[:-1]}_seekers', 'Glass'), band=a.part(f'{name[:-1]}_bands', 'Hazard'))


def strike_jet(a):
    """Twin-engine strike fighter (F-15E lineage): radome and chin gun, tandem bubble canopy on a
    dorsal spine, raked box intakes, a cropped-delta wing with flaps and ailerons, canted twin fins
    with rudders, all-moving stabilisers and afterburning nozzles. Wingtip missiles stay; the
    `Bombs` pivot holds the six bombs on the wing pylons (hidden once they drop). Origin at the
    fuselage centre (it flies), nose at -Y."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    glow = a.part('Wing_lights', 'TeamGlow')
    # Fuselage: radome, cockpit, a broad body between the engines.
    hull = [_sec(-4.95, .29, -.27, .22), _sec(-4.4, .38, -.35, .31), _sec(-3.6, .47, -.42, .38),
            _sec(-2.7, .53, -.46, .42), _sec(-1.8, .58, -.48, .44), _sec(-.6, .66, -.48, .43),
            _sec(.8, .78, -.46, .4), _sec(2.4, .84, -.44, .36), _sec(3.8, .83, -.41, .32), _sec(4.75, .78, -.38, .28)]
    body.loft(hull, bevel=.02, seg=1)
    # Dark radome; its back ring sits inside the fuselage, whose front face shows as a seam.
    armor.loft([[(0, -5.84, -.04)], _sec(-5.6, .11, -.13, .06), _sec(-5.3, .19, -.2, .13),
                _sec(-4.9, .275, -.26, .205)])
    _patch(armor, hull, -4.95, -4.05, 6, 10)                                             # anti-glare panel
    # Chin gun: fairing and barrel under the radome.
    armor.box((.18, .9, .15), loc=(0, -5.0, -.24), bevel=.04, seg=1, taper=(.8, 1))
    steel.cyl(.04, .7, loc=(0, -5.64, -.2), rot=FORWARD, seg=8, bevel=0)
    steel.cyl(.055, .08, loc=(0, -5.96, -.2), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, -6.0, -.2))
    # Tandem canopy on a dorsal spine that runs back to the air brake.
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    cz = [(y, w, _skin_z(hull, y, w) - .03) for y, w in ((-4.45, .13), (-4.1, .3), (-3.5, .37), (-2.8, .38),
                                                         (-2.15, .34), (-1.65, .24))]
    crown = (.36, .64, .84, .88, .8, .62)
    _canopy(glass, frames, [(y, w, z0, z1) for (y, w, z0), z1 in zip(cz, crown)], bows=(-3.98, -2.95))
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in
             ((-2.0, .27, .64), (-1.0, .31, .6), (.4, .3, .5), (1.8, .22, .4))]
    body.loft(spine + [[(0, 2.7, .33)]], bevel=.02, seg=1)
    _patch(armor, spine, -.6, .9, 2, 6)                                                    # air brake
    steel.box((.02, .22, .16), loc=(0, -.9, .63), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))  # blade aerials
    steel.box((.02, .18, .13), loc=(0, 2.5, .38), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))
    steel.box((.02, .2, .14), loc=(0, -1.2, -.52), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    # Raked box intakes beside the cockpit, trunks running back into the wing roots.
    lips = a.part('Intake_lips', 'Team')
    for s in (-1, 1):
        x = s * .86
        trunk = [_duct(x, -1.6, -.16, .27, .3), _duct(x, -.3, -.155, .26, .285), _duct(x - s * .06, 1.1, -.14, .2, .24)]
        _intake(a, body, lips, dark, (x, -2.38, -.16), .27, .3, .3, trunk)
        glow.box((.02, .5, .04), loc=(s * 1.135, -1.2, -.02), bevel=0)                   # formation lights
    # Cropped-delta wings: flaps inboard, ailerons outboard, missile rails on the tips.
    wing = Planform(.62, 4.55, -1.655, 1.5, 4.29, 1.25, .257, .08, .063, .03)
    panels = a.part('Panels', 'Team')
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(1.08, 2.8, .74), (2.8, 4.15, .74)])
        _skin_panel(panels, wing, frame, 1.25, 2.3, .22, .56)                             # fuel bays
        _skin_panel(panels, wing, frame, 2.75, 3.75, .28, .6)
    stab = Planform(.7, 2.7, 3.55, 4.85, 1.9, .62, .1, .045, -.08)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame)
    for i0, i1 in ((5, 7), (9, 11)):                                                        # engine bay doors
        _patch(panels, hull, 2.4, 3.8, i0, i1, out=.018, inn=.012, bevel=.005)
    # Canted twin fins with rudders, tip fairings and lights.
    fin = Planform(0, 1.95, 3.0, 4.55, 2.05, .8, .11, .05)
    for s in (-1, 1):
        frame = _upright(s * .55, .22, .3)
        _wing(body, moving, fin, frame, cs=[(.3, 1.6, .68)], lower=1.0)
        tip = Vector(frame(1.95, 4.6, 0))
        armor.cyl(.05, .55, loc=tuple(tip + Vector((0, .15, 0))), rot=BACKWARD, seg=8, bevel=.015, bseg=1)
        glow.box((.04, .1, .05), loc=tuple(tip + Vector((0, .47, 0))), bevel=0)
    # Afterburning nozzles with a tail stinger between them.
    for s in (-1, 1):
        _nozzle(a, s * .42, 4.62, -.06, .33, .8)
    armor.loft([_sec(4.6, .075, -.2, .08, n=8), _sec(5.2, .06, -.16, .04, n=8), [(0, 5.62, -.06)]], bevel=.01)
    a.part('Beacon', 'TeamGlow').sphere(.045, loc=(0, 5.6, -.06), seg=8, rings=5)
    # Wingtip rails with air-to-air missiles, nav lights.
    aams = _aam_parts(a)
    for s in (-1, 1):
        x = s * 4.62
        armor.box((.08, 1.5, .1), loc=(x, 2.1, .02), bevel=.02, seg=1)
        _aam(aams, (s * 4.72, 2.0, -.04), length=2.1, r=.065)
        glow.box((.1, .16, .05), loc=(x, 1.3, .03), bevel=.01, seg=1)
    # Wing pylons: a guided 2000 lb bomb inboard, twin 500 lb bombs on a rack outboard.
    b = a.pivot('Bombs', (0, 0, 0))
    bombs = _store_parts(a, b)
    pylons = a.part('Pylons', 'Armor')
    racks = a.part('Racks', 'Undercarriage')
    for s in (-1, 1):
        x = s * 1.85
        zt = wing.bottom(1.85)
        _pylon(pylons, x, -.75, .55, zt + .05, zt - .26)
        _bomb(bombs, (x, -.2, zt - .47), length=1.9, r=.19, guided=True, kit='jdam')
        x = s * 3.05
        zt = wing.bottom(3.05)
        _pylon(pylons, x, .35, 1.45, zt + .05, zt - .22)
        racks.box((.48, .7, .08), loc=(x, .8, zt - .25), bevel=.02, seg=1)
        for dx in (-.19, .19):
            racks.box((.05, .12, .1), loc=(x + dx, .55, zt - .31), bevel=0)
            _bomb(bombs, (x + dx, .55, zt - .45), length=1.45, r=.13, seg=8)


def _turbofan(a, x, y, z, r, length, blades=10, glow=True, cowl='Nacelles'):
    """Turbofan nacelle from its intake lip at y rearwards (Team cowl): dark fan face with a spinner
    and blades behind the lip, a core plug and a glowing ring in the exhaust."""
    L = length
    _revolve(a.part(cowl, 'Team'), [(r * .8, .34), (r * .84, 0), (r * .95, .025), (r, .3), (r, L * .72), (r * .84, L),
                                    (r * .76, L), (r * .76, L * .72), (r * .8, L * .4)], (x, y, z), BACKWARD, 16)
    dark = a.part('Fan_faces', 'Undercarriage')
    dark.cyl(r * .78, .06, loc=(x, y + .38, z), rot=FORWARD, seg=16, bevel=0)
    dark.cyl(r * .74, .05, loc=(x, y + L * .8, z), rot=FORWARD, seg=14, bevel=0)
    steel = a.part('Fan_blades', 'Steel')
    steel.cyl(r * .24, r * .45, r2=.01, loc=(x, y + .32 - r * .2, z), rot=FORWARD, seg=10, bevel=0)   # spinner
    for k in range(blades):
        phi = k * math.tau / blades
        rm = r * .5
        steel.box((r * .54, .1, .018), loc=(x + math.cos(phi) * rm, y + .3, z + math.sin(phi) * rm), rot=(.55, -phi, 0),
                  bevel=0)
    steel.cyl(r * .42, .5, r2=r * .08, loc=(x, y + L - .05, z), rot=BACKWARD, seg=12, bevel=0)       # core plug
    if glow:
        a.part('Exhaust_glow', 'Alloy').torus(r * .6, r * .05, loc=(x, y + L - .1, z), rot=FORWARD, seg=16, ring=4)
    if hd.on(a):  # a second stage of fan blades, cowl panel bands with latches, the core's exhaust vanes
        for k in range(blades):
            phi = (k + .5) * math.tau / blades
            steel.box((r * .5, .08, .016), loc=(x + math.cos(phi) * r * .48, y + .36, z + math.sin(phi) * r * .48),
                      rot=(-.5, -phi, 0), bevel=0)
        bands = a.part('Cowl_bands', 'Armor')
        for f in (.36, .62):
            bands.cyl(r * 1.006, .035, loc=(x, y + L * f, z), rot=FORWARD, seg=16, bevel=0)
            for k in range(3):
                phi = .5 + k * 1.05
                bands.box((.06, .08, .03), loc=(x + math.cos(phi) * r * 1.01, y + L * f + .06, z + math.sin(phi) * r * 1.01),
                          rot=(0, -phi + R90, 0), bevel=0)
        for k in range(6):
            phi = k * math.tau / 6
            steel.box((r * .3, .1, .012), loc=(x + math.cos(phi) * r * .58, y + L - .12, z + math.sin(phi) * r * .58),
                      rot=(0, -phi, 0), bevel=0)


def _rocket_pod(a, x, y, z, r, length, tubes=7, part='Pods'):
    """Rocket pod (front at y) with a ring of dark tube mouths on its face and a pointed tail."""
    pods = a.part(part, 'Armor')
    pods.lathe([(r * .55, length), (r * .85, length * .9), (r, length * .65), (r, .04), (r * .92, 0)], loc=(x, y, z),
               rot=BACKWARD, seg=12)
    a.part('Pod_bands', 'Hazard').cyl(r + .012, .05, loc=(x, y + length * .22, z), rot=FORWARD, seg=12, bevel=0)
    bores = a.part('Pod_tubes_bore', 'Undercarriage')
    ring = [k * math.tau / (tubes - 1) for k in range(tubes - 1)]
    pts = [(0.0, 0.0)] + [(math.cos(u) * r * .56, math.sin(u) * r * .56) for u in ring]
    for px, pz in pts:
        bores.cyl(r * .22, .03, loc=(x + px, y - .005, z + pz), rot=FORWARD, seg=6, bevel=0)


def _maverick(a, x, y, z, length=1.6, r=.11):
    """Air-to-ground missile (nose at y) with long delta wings and a glass seeker."""
    body = a.part('Missiles', 'Fuel')
    h = length / 2
    body.lathe([(r * .7, length), (r, length * .95), (r, length * .12), (r * .9, length * .06)], loc=(x, y, z),
               rot=BACKWARD, seg=10)
    a.part('Missile_seekers', 'Glass').sphere(r * .9, loc=(x, y + length * .06, z), seg=10, rings=6)
    a.part('Missile_bands', 'Hazard').cyl(r + .011, .05, loc=(x, y + length * .3, z), rot=FORWARD, seg=10, bevel=0)
    fins = a.part('Missile_fins', 'Armor')
    for k in range(4):
        _trap_fin(fins, (x, y + length * .42, z), math.pi / 4 + k * R90, r * .6, r * 1.3, length * .5, length * .12,
                  length * .36, .016)
    return y + length * .06 - r * .9


def attack_jet(a, detail=False):
    """Ground-attack jet (A-10 lineage): boxy armoured fuselage around a seven-barrel nose cannon,
    a bubble canopy, straight wings with gear pods at the roots, drooped tips and split ailerons,
    two turbofans high on the rear fuselage and a twin-fin tailplane. Pylons carry bombs, rocket
    pods, air-to-ground and air-to-air missiles. Origin at the fuselage centre (it flies)."""
    hd.mark(a, detail)
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    hull = [_sec(-5.92, .27, -.37, .06, pt=3, pb=3), _sec(-5.35, .52, -.62, .32, pt=3, pb=3),
            _sec(-4.45, .65, -.74, .46, pt=3, pb=3), _sec(-3.3, .7, -.76, .52, pt=3, pb=3),
            _sec(-2.0, .72, -.76, .53, pt=3, pb=3), _sec(-.5, .7, -.72, .52, pt=3, pb=3),
            _sec(1.2, .62, -.62, .5, pt=3, pb=3), _sec(2.8, .48, -.46, .46, pt=2.6, pb=2.6),
            _sec(4.2, .32, -.26, .38), _sec(5.25, .15, -.06, .3)]
    body.loft(hull + [[(0, 5.62, .16)]], bevel=.02, seg=1)
    _patch(armor, hull, -5.35, -4.55, 6, 10)                                               # anti-glare panel
    armor.cyl(.07, .03, loc=(0, -5.1, _skin_z(hull, -5.1, 0) + .005), seg=10, bevel=0)     # refuelling slot
    for i0, i1 in ((5, 6), (10, 11)):                                                      # armour side plates
        _patch(panels, hull, -4.3, -1.2, i0, i1, out=.014, inn=.012, bevel=.005)
    # Seven-barrel cannon out of the nose: housing, barrel cluster and muzzle clamp.
    steel.cyl(.15, .3, loc=(0, -5.98, -.16), rot=FORWARD, seg=12, bevel=.02, bseg=1)
    for k in range(7):
        ang = k * math.tau / 7
        steel.cyl(.028, .88, loc=(math.cos(ang) * .075, -6.46, -.16 + math.sin(ang) * .075), rot=FORWARD, seg=6,
                  bevel=0)
    steel.cyl(.12, .06, loc=(0, -6.45, -.16), rot=FORWARD, seg=12, bevel=0)
    steel.cyl(.125, .07, loc=(0, -6.84, -.16), rot=FORWARD, seg=12, bevel=0)
    a.pivot('Muzzle_gun', (0, -6.9, -.16))
    # Bubble canopy high on the nose, a spine fairing behind it.
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    st = [(-4.8, .2, .58), (-4.45, .38, .96), (-3.8, .44, 1.12), (-3.1, .43, 1.1), (-2.55, .33, .92), (-2.2, .18, .7)]
    _canopy(glass, frames, [(y, w, _skin_z(hull, y, w) - .03, z1) for y, w, z1 in st], bows=(-4.35, -3.4))
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in ((-2.45, .27, .82), (-1.4, .34, .74),
                                                                         (.2, .3, .62))]
    body.loft(spine + [[(0, 1.6, .5)]], bevel=.02, seg=1)
    steel.box((.02, .24, .18), loc=(0, -1.0, .78), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))  # blade aerials
    steel.box((.02, .2, .15), loc=(0, 3.6, .45), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))
    # Straight low wings: a flat centre panel, dihedral outer panels and drooped tips.
    inner = Planform(.55, 2.6, -1.42, -1.35, 2.47, 2.3, .3, .27, -.55)
    outer = Planform(2.6, 6.2, -1.35, -1.02, 2.3, 1.42, .27, .14, -.55, -.55 + 3.6 * math.tan(.12))
    tip = Planform(6.2, 6.5, -1.02, -.96, 1.42, 1.28, .14, .08, outer.at(6.2)[3], outer.at(6.2)[3] - .2)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, inner, frame, cs=[(.9, 2.6, .72)])
        _wing(body, moving, outer, frame, cs=[(2.6, 4.2, .72), (4.2, 6.05, .7)])
        _surface(body, tip, frame, ends=(False, True))
        _skin_panel(panels, inner, frame, 1.9, 2.5, .2, .55)
        _skin_panel(panels, outer, frame, 2.62, 4.18, .22, .56)
    for s in (-1, 1):
        glow.box((.05, .16, .06), loc=(s * 6.44, -.97, tip.at(6.44)[3]), bevel=.01, seg=1)
        # Main gear pods at the wing roots with the tyres showing, as on the real thing.
        x = s * 1.36
        gear = [_sec(-1.95, .2, -.95, -.62, pt=2.2, pb=2.2), _sec(-1.4, .27, -1.05, -.5, pt=2.2, pb=2.2),
                _sec(.3, .27, -1.03, -.5, pt=2.2, pb=2.2), _sec(1.0, .14, -.86, -.6)]
        body.loft([[(x, -2.3, -.8)]] + [[(x + px, py, pz) for px, py, pz in ring] for ring in gear], bevel=.02, seg=1)
        a.part('Tyres', 'Rubber').cyl(.3, .2, loc=(x, -1.65, -.98), rot=ACROSS, seg=12, bevel=.05, bseg=1)
        steel.cyl(.14, .22, loc=(x, -1.65, -.98), rot=ACROSS, seg=8, bevel=0)
    # Turbofans high on the rear fuselage on stub pylons.
    for s in (-1, 1):
        x = s * 1.12
        _turbofan(a, x, 1.62, .82, .56, 2.35)
        body.limb((s * .22, 2.75, .36), (s * .86, 2.75, .62), .16, 1.4, bevel=.04, seg=1)
        glow.box((.03, .5, .04), loc=(x + s * .565, 2.9, .82), bevel=0)                    # formation lights
    # Tailplane with elevators; twin fins on its tips with rudders, reaching below it too.
    stab = Planform(0, 2.72, 4.35, 4.6, 1.3, 1.05, .12, .09, .22)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.25, 2.6, .68)])
    fin = Planform(0, 2.2, 4.3, 4.6, 1.42, 1.08, .12, .09)
    for s in (-1, 1):
        frame = _upright(s * 2.74, -.52, 0.0)
        _wing(body, moving, fin, frame, cs=[(.3, 2.05, .66)], lower=1.0, root=True)
        glow.box((.04, .12, .04), loc=(s * 2.74, 5.65, 1.69), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 5.6, .2), seg=8, rings=5)
    # Stores: bombs inboard, rocket pods, air-to-ground missiles on rails, wingtip air-to-air missiles.
    stores = _store_parts(a, None, 'Ordnance')
    pylons = a.part('Pylons', 'Armor')
    aams = _aam_parts(a, 'Sidewinders')
    for s in (-1, 1):
        x = s * 2.05
        zt = inner.bottom(2.05)
        _pylon(pylons, x, -1.25, .1, zt + .05, zt - .18)
        _bomb(stores, (x, -.75, zt - .18 - .16 - .02), length=1.5, r=.16, seg=10)
        x = s * 2.95
        zt = outer.bottom(2.95)
        _pylon(pylons, x, -1.0, .3, zt + .05, -.81)
        _rocket_pod(a, x, -1.2, -1.0, .21, 1.55)
        x = s * 4.1
        zt = outer.bottom(4.1)
        _pylon(pylons, x, -1.05, .2, zt + .05, -.79)
        pylons.box((.1, 1.0, .06), loc=(x, -.55, -.8), bevel=.01, seg=1)                   # launch rail
        _maverick(a, x, -1.38 + .11 * .9 - 1.6 * .06, -.93)
        x = s * 5.35
        zt = outer.bottom(5.35)
        _pylon(pylons, x, -.9, .2, zt + .05, zt - .14)
        _aam(aams, (x, -.6, zt - .14 - .055), length=1.9, r=.062)
    a.pivot('Muzzle_rocket', (0, -1.25, -1.0))
    a.pivot('Muzzle_missile', (0, -1.38, -.93))
    a.pivot('Muzzle_aam', (0, -1.55, zt - .25))
    if detail:
        _attack_jet_detail(a, hull, st, inner, outer, stab, fin)


def _attack_jet_detail(a, hull, st, inner, outer, stab, fin):
    """High-detail parts of the attack jet (see mb_detail.py): frames, seams and rivet rows over the
    fuselage and the riveted armour bathtub, spar and rib lines with rivets on the wings and tail, static
    dischargers, a third canopy bow, gear-door lines, sway braces on the pylons, pitot tubes, aerials and
    anti-collision lights. The turbofans add their own (see _turbofan)."""
    lines = a.part('Panel_lines', 'Armor')
    rivets = a.part('Rivets', 'Steel')
    steel = a.part('Detail_steel', 'Steel')
    for y in (-5.0, -4.0, -2.6, -1.0, .6, 2.2, 3.4, 4.6):                  # frames, clear of canopy and spine
        i0, i1 = (11, 5) if -4.8 < y < -2.2 else (10, 6)
        _hoop_line(lines, hull, y, [(i0 + k) % 16 for k in range((i1 - i0) % 16 + 1)])
    for i in (4, 12):
        _seam_line(lines, hull, -5.6, 5.0, i, u=0.0)
    for i in (6, 9):
        _seam_line(lines, hull, -2.2, 4.4, i, u=.5)
    for i in (5, 10):                                                       # the armour bathtub's rivets
        for u in (.12, .88):
            _rivet_row(rivets, hull, -4.25, -1.25, i, 16, u=u, size=.02, out=.016)
    for i in (5, 10):
        _rivet_row(rivets, hull, -1.0, 4.4, i, 26, u=.5, size=.02)
    for i in (7, 8):
        _rivet_row(rivets, hull, 1.7, 4.8, i, 14, u=.5, size=.02)
    # Wings: spar and rib lines with rivet rows, dischargers on the ailerons.
    for frame in (RIGHT, LEFT):
        for u in (.15, .62):
            _wing_line(lines, inner, frame, .62, 2.55, u)
            _wing_line(lines, outer, frame, 2.65, 6.15, u)
            _wing_rivets(rivets, inner, frame, .62, 2.55, u + .04, 12)
            _wing_rivets(rivets, outer, frame, 2.65, 6.1, u + .04, 22)
        for sp in (1.1, 1.7):
            _wing_rib(lines, inner, frame, sp, .06, .7)
        for sp in (4.5, 5.2, 5.9):
            _wing_rib(lines, outer, frame, sp, .06, .66)
        _dischargers(steel, outer, frame, (5.3, 5.85))
        for u in (.15, .6):
            _wing_line(lines, stab, frame, .35, 2.65, u)
        _wing_rivets(rivets, stab, frame, .35, 2.6, .2, 14)
    for s in (-1, 1):
        frame = _upright(s * 2.74, -.52, 0.0)
        for side in (1, -1):
            for u in (.15, .6):
                _wing_line(lines, fin, frame, .05, 2.15, u, side=side, lower=1.0)
            for sp in (.4, 1.3):
                _wing_rib(lines, fin, frame, sp, .05, .64, side=side, lower=1.0)
    # A third canopy bow.
    rings = [_dome(y, w + .004, _skin_z(hull, y, w) - .03, z1 + .004, 9) for y, w, z1 in st]
    a.part('Canopy_frames', 'Armor').tube(_ring_at(rings, -2.8), .02, seg=6)
    # Gear pods: door hinge lines either side of the wheel well.
    for s in (-1, 1):
        x = s * 1.36
        gear = [[(x + px, py, pz) for px, py, pz in ring] for ring in
                (_sec(-1.95, .2, -.95, -.62, pt=2.2, pb=2.2), _sec(-1.4, .27, -1.05, -.5, pt=2.2, pb=2.2),
                 _sec(.3, .27, -1.03, -.5, pt=2.2, pb=2.2), _sec(1.0, .14, -.86, -.6))]
        for i in (2, 13):
            _seam_line(lines, gear, -1.3, .25, i, u=.5, r=.008)
    # Pylons: sway braces round each store.
    for x, pf, y0, y1, drop in ((2.05, inner, -1.25, .1, .18), (2.95, outer, -1.0, .3, None),
                                (4.1, outer, -1.05, .2, None), (5.35, outer, -.9, .2, .14)):
        zb = pf.bottom(x) - drop if drop else (-.81 if x < 3 else -.79)
        for s in (-1, 1):
            for dy in (.3, .7):
                for dx in (-.065, .065):
                    steel.box((.03, .05, .06), loc=(s * x + dx, y0 + (y1 - y0) * dy, zb - .01), bevel=0)
    # Nose pitot tubes, aerials and anti-collision lights.
    for s in (-1, 1):
        steel.tube([(s * .45, -5.2, .05), (s * .45, -5.62, .05)], .014, seg=4)
    steel.box((.02, .2, .14), loc=(0, 2.2, _skin_z(hull, 2.2, 0) + .06), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))
    steel.box((.02, .18, .12), loc=(0, -2.8, -.83), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    beacon = a.part('Beacon_lights', 'Alloy')
    beacon.sphere((.05, .05, .035), loc=(0, .1, .615), seg=10, rings=6, cut=0)
    beacon.sphere((.05, .05, .035), loc=(0, .3, -.715), rot=(math.pi, 0, 0), seg=10, rings=6, cut=0)


def _prop_blade(part, phi, r0, r1, c0, c1, t0, t1, pitch0, pitch1, axis_y=0.0, sense=1):
    """Twisted propeller blade radiating at angle phi in the XZ plane (the disc of a propeller that
    spins about Y) from radius r0 to r1: chord c, thickness t and pitch taper from root to tip.
    Coordinates are relative to the Propeller pivot; axis_y shifts the blade along the axis."""
    d = Vector((math.cos(phi), 0, math.sin(phi)))
    e = Vector((-math.sin(phi), 0, math.cos(phi))) * sense
    y = Vector((0, 1, 0))
    foil = [(-.5, 0), (-.28, .5), (.2, .42), (.5, 0), (.2, -.22), (-.28, -.3)]

    def ring(r, c, t, b):
        cv, nv = e * math.cos(b) + y * math.sin(b), -e * math.sin(b) + y * math.cos(b)
        return [tuple(d * r + cv * u * c + nv * v * t + y * axis_y) for u, v in foil]
    part.loft([ring(r0, c0, t0, pitch0),
               ring((r0 + r1) / 2, (c0 + c1) / 2 * 1.08, (t0 + t1) / 2, (pitch0 + pitch1) / 2),
               ring(r1, c1, t1, pitch1)], bevel=0)


def strike_drone(a):
    """Armed medium-altitude drone (MQ-9 lineage): slender fuselage with a bulbous satcom nose,
    long straight wings with flaps and ailerons, a Y-tail (V-tail with ruddervators over a ventral
    fin), a four-blade pusher `Propeller` (spins about local Y), a sensor turret under the nose, a
    guided bomb and a twin missile rail under each wing. Origin at the fuselage centre (it flies)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    glow = a.part('Wing_lights', 'TeamGlow')
    hull = [_sec(-3.12, .15, -.13, .15, n=12), _sec(-2.85, .29, -.23, .34, n=12), _sec(-2.4, .36, -.27, .45, n=12),
            _sec(-1.85, .34, -.28, .38, n=12), _sec(-.8, .3, -.28, .3, n=12), _sec(.6, .28, -.26, .27, n=12),
            _sec(1.9, .21, -.2, .21, n=12), _sec(2.8, .12, -.12, .12, n=12)]
    body.loft([[(0, -3.26, .0)]] + hull, bevel=.015, seg=1)
    _patch(a.part('Panels', 'Team'), hull, -2.75, -1.95, 4, 8, out=.013, inn=.012, bevel=.004)   # satcom dome cover
    zs = _skin_z(hull, .88, 0)
    armor.box((.22, .56, .1), loc=(0, .88, zs + .01), bevel=.02, seg=1, taper=(.9, .9))       # dorsal intake
    dark.box((.15, .04, .05), loc=(0, .59, zs + .025), bevel=0)
    for s in (-1, 1):                                                                         # engine exhausts
        steel.cyl(.045, .3, loc=(s * .2, 2.3, .02), rot=(-R90 + .2, 0, -s * .5), seg=8, bevel=0)
    for y, z, t in ((-1.2, .31, -.35), (.2, .29, -.35), (-.4, -.28, .35)):                   # blade aerials
        steel.box((.02, .16, .14), loc=(0, y, z + (.05 if z > 0 else -.05)), rot=(t, 0, 0), bevel=0, taper=(1, .5))
    steel.cyl(.012, .3, loc=(0, -3.3, -.02), rot=FORWARD, seg=5, bevel=0)                      # pitot
    # Long straight wings, a V-tail with ruddervators and a ventral fin.
    wing = Planform(.2, 5.5, -.52, -.26, .95, .42, .13, .05, .07, .14)
    panels = a.part('Panels', 'Team')
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(.55, 2.7, .72), (2.7, 5.2, .72)], bevel=0)
        _skin_panel(panels, wing, frame, .8, 1.9, .2, .55, out=.011, inn=.01)
    for s in (-1, 1):
        glow.box((.05, .14, .05), loc=(s * 5.52, -.2, .14), bevel=.01, seg=1)
    tail = Planform(0, 1.35, 2.05, 2.42, .62, .32, .06, .03)
    for s in (-1, 1):
        _wing(body, moving, tail, _upright(s * .08, .1, .78), cs=[(.12, 1.25, .62)], lower=1.0, bevel=0)
    _surface(body, Planform(0, .55, 2.12, 2.34, .5, .3, .05, .03), _upright(0, -.05, math.pi), lower=1.0, bevel=0)
    # Sensor turret under the nose: yoke, ball and windows.
    armor.cyl(.09, .14, loc=(0, -2.5, -.3), seg=10, bevel=.01, bseg=1)
    armor.sphere(.2, loc=(0, -2.5, -.46), seg=12, rings=8)
    sensor = a.part('Sensor', 'Glass')
    sensor.cyl(.075, .05, loc=(-.06, -2.68, -.47), rot=FORWARD, seg=10, bevel=0)
    sensor.cyl(.04, .05, loc=(.09, -2.67, -.45), rot=FORWARD, seg=8, bevel=0)
    # Four-blade pusher propeller behind the tail.
    dark.cyl(.12, .14, loc=(0, 2.93, 0), rot=FORWARD, seg=12, bevel=.01, bseg=1)
    p = a.pivot('Propeller', (0, 3.08, 0))
    a.part('Propeller_hub', 'Steel', p).lathe([(.12, -.06), (.12, .05), (.08, .15), (0, .25)], rot=BACKWARD, seg=12)
    blades = a.part('Propeller_blades', 'Armor', p)
    for k in range(4):
        _prop_blade(blades, math.pi / 4 + k * R90, .08, .8, .16, .08, .04, .014, .7, .25, axis_y=.02)
    # Stores: a laser-guided bomb inboard (the second weapon, slot rocket) and a twin missile rail outboard
    # under each wing. The bombs are long enough that the seeker, canards and nose band stand well ahead
    # of the leading edge and the tail fins behind the trailing edge, so they read from above; their
    # pylons are Pylon_bomb (never Bombs: that pivot is hidden after a drop).
    stores = _store_parts(a, None, 'Ordnance')
    pylons = a.part('Pylons', 'Armor')
    mis = dict(body=a.part('Missiles', 'Fuel'), fins=a.part('Missile_fins', 'Armor'),
               nose=a.part('Missile_seekers', 'Glass'), band=a.part('Missile_bands', 'Hazard'))
    rb, lb, yb = .15, 2.1, -.45                                                       # bomb radius, length, centre
    for s in (-1, 1):
        x = s * 1.45
        zt = wing.bottom(1.45)
        _pylon(a.part('Pylon_bomb', 'Armor'), x, -.55, .28, zt + .04, zt - .1, w=.07)
        _bomb(stores, (x, yb, zt - .1 - rb - .015), length=lb, r=rb, seg=10, guided=True)
        x = s * 2.45
        zt = wing.bottom(2.45)
        _pylon(pylons, x, -.45, .15, zt + .04, -.105, w=.06)
        pylons.box((.6, .7, .04), loc=(x, -.35, -.115), bevel=.01, seg=1)                     # launcher rail
        for dx in (-.24, .24):
            _aam(mis, (x + dx, -.86 + .475, -.19), length=.95, r=.055, seg=8, canards=False, fin=1.4)
    a.pivot('Muzzle_missile', (0, -.86, -.19))
    # Muzzle_rocket: centred between the two bomb noses (like Muzzle_missile between the rails).
    a.pivot('Muzzle_rocket', (0, yb - lb / 2 - rb * .35, wing.bottom(1.45) - .1 - rb - .015))


# ----------------------------------------------------------------------------- munitions
def missile(a):
    """Air-to-surface missile (nose at -Y): white body, glass seeker in an armoured collar, a yellow
    warhead band, canards and swept tail fins, a glowing motor inside a steel nozzle lip."""
    h = .6
    a.part('Body', 'Fuel').lathe([(.042, -h), (.05, -h + .04), (.05, .34), (.047, .42)], rot=FORWARD, seg=10)
    a.part('Collar', 'Armor').lathe([(.049, .4), (.043, .5)], rot=FORWARD, seg=10)
    a.part('Seeker', 'Glass').lathe([(.041, .48), (.033, .54), (.018, .58), (0, h)], rot=FORWARD, seg=10)
    a.part('Band', 'Hazard').cyl(.061, .04, loc=(0, -.2, 0), rot=FORWARD, seg=10, bevel=0)
    fins = a.part('Fins', 'Armor')
    for k in range(4):
        ang = math.pi / 4 + k * R90
        _trap_fin(fins, (0, .36, 0), ang, .03, .075, .22, .08, .12, .012)
        _trap_fin(fins, (0, -.34, 0), ang, .03, .045, .09, .04, .04, .01)
    a.part('Nozzle', 'Steel').torus(.037, .009, loc=(0, h + .012, 0), rot=FORWARD, seg=10, ring=3)
    a.part('Motor', 'Alloy').cyl(.032, .04, loc=(0, h + .005, 0), rot=FORWARD, seg=10, bevel=0)


def rocket(a):
    h = .45
    a.part('Body', 'Armor').lathe([(.028, -h), (.035, -h + .04), (.035, .22), (.03, .26)], rot=FORWARD, seg=8)
    a.part('Warhead', 'Hazard').lathe([(.034, .2), (.03, .3), (.016, .4), (0, h)], rot=FORWARD, seg=8)
    fins = a.part('Fins', 'Armor')
    for k in range(4):
        _fin(fins, (0, h - .06, 0), k * R90, .05, .1, .008, .032)
    a.part('Motor', 'Alloy').cyl(.026, .04, loc=(0, h + .005, 0), rot=FORWARD, seg=8, bevel=0)


def bomb(a):
    """Low-drag 500 lb bomb (nose at -Y): ogive nose with a steel fuze, a yellow nose band,
    boat tail with four swept fins and suspension lugs on top."""
    _bomb(dict(body=a.part('Body', 'Armor'), band=a.part('Nose_band', 'Hazard'), steel=a.part('Lugs', 'Steel'),
               glass=a.part('Seeker', 'Glass')), (0, 0, 0), seg=12)
    a.part('Tail_band', 'Hazard').cyl(.182, .03, loc=(0, .1, 0), rot=FORWARD, seg=12, bevel=0)


def cruise_missile(a):
    h, r = 2.0, .26
    a.part('Body', 'Fuel').lathe([(r * .7, -h), (r, -h + .25), (r, 1.3), (r * .82, 1.62), (r * .45, 1.86), (0, h)],
                                 rot=FORWARD, seg=12)
    wings = a.part('Wings', 'Armor')
    for s in (-1, 1):  # pop-out wings on the back, slightly swept
        wings.box((1.1, .36, .04), loc=(s * .7, -.05, .14), rot=(0, 0, s * .22), bevel=0)
    for k in range(4):
        _fin(wings, (0, h - .3, 0), math.pi / 4 + k * R90, .3, .45, .03, .18)
    a.part('Intake', 'Undercarriage').box((.26, .6, .16), loc=(0, 1.2, -.27), bevel=.03, seg=1)
    a.part('Motor', 'Alloy').cyl(.15, .05, loc=(0, h + .01, 0), rot=FORWARD, seg=12, bevel=0)


# name: (builder, Asset options). Flying models skip ground occlusion and grime.
BUILDERS = {
    'attack_helicopter': (attack_helicopter, dict(ao_distance=.6, grime_height=.4)),
    'strike_jet': (strike_jet, dict(ao_distance=.6, ground=False)),
    'gunship_heli': (gunship_heli, dict(ao_distance=.7, grime_height=.4)),
    'scout_heli': (scout_heli, dict(ao_distance=.5, grime_height=.35)),
    'attack_jet': (attack_jet, dict(ao_distance=.6, ground=False)),
    'strike_drone': (strike_drone, dict(ao_distance=.4, ground=False)),
    'missile': (missile, dict(ao_distance=.12, ground=False)),
    'rocket': (rocket, dict(ao_distance=.1, ground=False)),
    'bomb': (bomb, dict(ao_distance=.2, ground=False)),
    'cruise_missile': (cruise_missile, dict(ao_distance=.4, ground=False)),
}
