"""Machine Brigade aircraft and munitions built with frontier_kit.

Conventions (shared with ModelLibrary.cs): metres, +Z up, Blender -Y is the nose.
  * attack_helicopter: origin on the ground under the fuselage centre (skids touch z = 0).
    `Rotor` (main rotor hub, blades spin about local Z), `Tail_rotor` (hub on the fin, blades
    spin about local X), `Mount_gun` (chin turret yaw) with `Muzzle_gun`, and `Muzzle_rocket` /
    `Muzzle_missile` centred between the symmetric wing launchers.
  * strike_jet: origin at the fuselage centre (it flies). `Bombs` is one part holding the four
    wing bombs (hidden once they drop); `Muzzle_gun` at the nose cannon.
  * Munitions: origin at the centre, nose at -Y, emissive `Alloy` motors at the tail.
Team / TeamGlow parts are recoloured per army at runtime.
"""
import math

from mathutils import Vector

from mb_vehicles import _frame, _tube_mouth

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


def _bomb(part, loc, length=1.6, r=.17, seg=10):
    """Low-drag bomb body with four tail fins, nose at -Y (one material)."""
    x, y, z = loc
    h = length / 2
    part.lathe([(r * .38, -h), (r * .62, -h * .72), (r, -h * .3), (r, h * .42), (r * .72, h * .78), (r * .2, h * .98),
                (0, h)], loc=loc, rot=FORWARD, seg=seg)
    for k in range(4):
        _fin(part, (x, y + h * .78, z), math.pi / 4 + k * R90, r * .9, length * .2, .02, r * .35)


# ----------------------------------------------------------------------------- helicopter
def attack_helicopter(a):
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    body.loft([
        _octagon(-4.5, .2, 1.24, 1.52),
        _octagon(-4.05, .42, 1.02, 1.76),
        _octagon(-3.2, .55, .94, 1.86),
        _octagon(-1.5, .62, .92, 1.98),
        _octagon(0.0, .66, .95, 2.06),
        _octagon(1.25, .58, 1.05, 2.0),
        _octagon(2.05, .36, 1.42, 1.96),
    ], bevel=.07, seg=2)
    body.loft([_octagon(1.8, .33, 1.45, 1.94), _octagon(4.72, .13, 1.62, 1.86)], bevel=.04, seg=1)  # tail boom
    body.prism([(3.95, 1.8), (4.82, 1.72), (5.08, 3.36), (4.64, 3.4)], .12, bevel=.03)               # fin
    body.box((1.7, .5, .07), loc=(0, 4.25, 1.78), bevel=.02, seg=1, taper=(1, .7))                    # stabiliser
    for s in (-1, 1):
        armor.box((.06, .4, .32), loc=(s * .86, 4.28, 1.8), bevel=.015, seg=1)                          # end plates
    # Tandem cockpit: gunner in front, pilot raised behind; frames over the glass.
    glass.loft([_bubble(-4.02, .28, 1.6, 1.8), _bubble(-3.55, .48, 1.7, 2.22), _bubble(-2.68, .5, 1.76, 2.3)],
               bevel=.03, seg=1)
    glass.loft([_bubble(-2.78, .52, 1.78, 2.4), _bubble(-2.4, .54, 1.8, 2.58), _bubble(-1.35, .52, 1.84, 2.58),
                _bubble(-.95, .4, 1.88, 2.36)], bevel=.03, seg=1)
    frames = a.part('Canopy_frames', 'Armor')
    for section in (_bubble(-3.5, .5, 1.71, 2.24), _bubble(-2.7, .52, 1.77, 2.34), _bubble(-2.35, .56, 1.8, 2.6),
                    _bubble(-1.4, .54, 1.84, 2.6)):
        _hoop(frames, section)
    # Engine nacelles on the shoulders with intakes and exhausts; rotor pylon between them.
    for s in (-1, 1):
        body.cyl(.3, 1.9, loc=(s * .64, .15, 2.1), rot=FORWARD, seg=12, bevel=.08)
        dark.cyl(.2, .06, loc=(s * .64, -.82, 2.1), rot=FORWARD, seg=12, bevel=0)                       # intakes
        dark.cyl(.22, .4, loc=(s * .68, 1.2, 2.12), rot=(R90 + .25, 0, s * -.3), seg=10, bevel=.02, bseg=1)
    body.box((.86, 1.9, .5), loc=(0, -.45, 2.2), bevel=.08, taper=(.72, .8))                            # pylon
    steel.cyl(.11, .8, loc=(0, -.6, 2.8), seg=10, bevel=0)                                              # mast
    # Stub wings: rocket pods inboard, ATGM rails at the tips.
    pods = a.part('Pods', 'Armor')
    missiles = a.part('Missiles', 'Fuel')
    noses = a.part('Missile_noses', 'Armor')
    for s in (-1, 1):
        body.box((1.56, .95, .12), loc=(s * 1.4, .05, 1.5), bevel=.03, seg=1, taper=(1, .9))
        armor.box((.1, .5, .22), loc=(s * 1.35, .05, 1.35), bevel=.02, seg=1)                          # pod pylon
        pods.cyl(.2, 1.3, loc=(s * 1.35, -.05, 1.1), rot=FORWARD, seg=12, bevel=.06)
        _tube_mouth(a, None, _frame((s * 1.35, -.7, 1.1), FORWARD), .19, protrude=.05, seg=12, name='Pod_tubes')
        for k in range(6):  # rocket noses peeking out of the pod
            ang = k * math.tau / 6
            a.part('Pod_tubes', 'Steel').cyl(.028, .09, r2=.005, loc=(s * 1.35 + math.cos(ang) * .085, -.73,
                                                                       1.1 + math.sin(ang) * .085),
                                             rot=FORWARD, seg=5, bevel=0)
        armor.box((.08, 1.1, .5), loc=(s * 2.02, 0, 1.21), bevel=.02, seg=1)                          # ATGM rail
        for z in (1.33, 1.08):
            missiles.cyl(.075, 1.0, loc=(s * 2.125, -.05, z), rot=FORWARD, seg=8, bevel=0)
            noses.cyl(.075, .16, r2=.025, loc=(s * 2.125, -.63, z), rot=FORWARD, seg=8, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .12, .06), loc=(s * 2.19, .1, 1.5), bevel=.01, seg=1)
    a.pivot('Muzzle_rocket', (0, -.75, 1.1))
    a.pivot('Muzzle_missile', (0, -.71, 1.205))
    # Nose sensor turret and landing light.
    armor.box((.42, .36, .4), loc=(0, -4.52, 1.34), bevel=.06)
    a.part('Sensor', 'Glass').box((.3, .04, .13), loc=(0, -4.71, 1.37), bevel=.01, seg=1)
    a.part('Lamps', 'Lamp').box((.16, .12, .05), loc=(0, -3.9, 1.0), bevel=.01, seg=1)
    # Skids on arched struts.
    skids = a.part('Skids', 'Undercarriage')
    for s in (-1, 1):
        x = s * .95
        skids.tube([(x, 1.55, .06), (x, -1.75, .06), (x, -2.05, .15), (x, -2.2, .34)], .06, seg=8)
        for y, z in ((-1.1, 1.0), (.95, 1.12)):
            skids.tube([(x, y, .06), (s * .9, y, .5), (s * .4, y, z)], .05, seg=6)
    steel.cyl(.015, .6, loc=(0, 3.2, 2.18), seg=5, bevel=0)                                             # antenna
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 4.86, 3.42), seg=8, rings=5)

    # Chin gun on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -3.45, .96))
    a.part('Gun_turret', 'Armor', g).cyl(.2, .22, loc=(0, 0, -.08), seg=12, bevel=.04)
    gun = a.part('Gun', 'Steel', g)
    gun.box((.16, .42, .14), loc=(0, -.16, -.16), bevel=.03)
    gun.cyl(.035, 1.05, loc=(0, -.85, -.16), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.05, .12, loc=(0, -1.33, -.16), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, -1.39, -.16), g)

    # Main rotor: four blades on a hub at the mast top.
    r = a.pivot('Rotor', (0, -.6, 3.25))
    hub = a.part('Rotor_hub', 'Steel', r)
    hub.cyl(.3, .16, seg=12, bevel=.03)
    hub.cyl(.16, .2, loc=(0, 0, .16), seg=10, bevel=.04)
    blades = a.part('Rotor_blades', 'Armor', r)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        d = Vector((math.cos(ang), math.sin(ang), 0))
        blades.box((.34, 4.2, .05), loc=tuple(d * 2.35), rot=(0, 0, ang - R90), bevel=.02, seg=1, taper=(.85, 1))
        hub.box((.2, .5, .1), loc=tuple(d * .42), rot=(0, 0, ang - R90), bevel=.02, seg=1)             # grips
    # Tail rotor on the left of the fin, blades in the YZ plane.
    armor.cyl(.1, .16, loc=(-.13, 4.74, 2.86), rot=ACROSS, seg=10, bevel=.02, bseg=1)                 # gearbox
    tr = a.pivot('Tail_rotor', (-.25, 4.74, 2.86))
    a.part('Tail_rotor_hub', 'Steel', tr).cyl(.07, .1, rot=ACROSS, seg=8, bevel=.01, bseg=1)
    tblades = a.part('Tail_rotor_blades', 'Armor', tr)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        tblades.box((.03, .14, .68), loc=(0, -math.sin(ang) * .4, math.cos(ang) * .4), rot=(ang, 0, 0),
                    bevel=.01, seg=1)


# ----------------------------------------------------------------------------- jet
def strike_jet(a):
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    # Dark radome; its back ring sits 2 cm inside the fuselage, whose front face shows as a seam.
    armor.loft([[(0, -5.75, -.03)], _octagon(-5.3, .18, -.14, .1), _octagon(-4.84, .3, -.23, .19)], bevel=.03,
               seg=1)
    body.loft([
        _octagon(-4.86, .31, -.24, .2),
        _octagon(-3.9, .48, -.4, .36),
        _octagon(-2.4, .6, -.5, .5),
        _octagon(-.5, .66, -.52, .52),
        _octagon(1.5, .8, -.5, .5),
        _octagon(3.8, .84, -.45, .42),
        _octagon(5.12, .74, -.38, .32),
    ], bevel=.05, seg=2)
    # Canopy and frame.
    glass = a.part('Canopy', 'Glass')
    glass.loft([_bubble(-4.25, .14, .12, .28), _bubble(-3.6, .34, .24, .74), _bubble(-2.6, .36, .34, .82),
                _bubble(-1.6, .22, .42, .6)], bevel=.03, seg=1)
    _hoop(a.part('Canopy_frames', 'Armor'), _bubble(-3.45, .36, .25, .77), r=.025)
    # Swept wings, stabilisers and twin canted fins.
    for s in (-1, 1):
        body.prism([(s * .5, -1.6), (s * 4.9, .9), (s * 4.9, 1.8), (s * .5, 2.5)], .16, loc=(0, 0, -.12),
                   axis='Z', bevel=.04)
        body.prism([(s * .55, 3.7), (s * 2.55, 4.9), (s * 2.55, 5.4), (s * .55, 5.3)], .1, loc=(0, 0, .02),
                   axis='Z', bevel=.03)
        body.prism([(3.2, .1), (5.25, .1), (5.55, 2.05), (4.8, 2.1)], .12, loc=(s * .62, 0, 0), rot=(0, s * .3, 0),
                   bevel=.03)
        a.part('Wing_lights', 'TeamGlow').box((.06, .3, .08), loc=(s * 4.9, 1.3, -.12), bevel=.01, seg=1)
        armor.box((3.3, .34, .03), loc=(s * 2.75, 1.93, -.03), rot=(0, 0, -s * .158), bevel=.01, seg=1)  # flaps
        # Side intakes: raked team-coloured ducts with dark inlets.
        body.prism([(-1.65, -.34), (-1.3, .2), (.9, .2), (.9, -.34)], .38, loc=(s * .74, 0, 0), bevel=.05)
        dark.box((.28, .04, .42), loc=(s * .74, -1.52, -.07), rot=(-.58, 0, 0), bevel=.01, seg=1)
        armor.box((.06, 1.9, .06), loc=(s * .93, -.4, .06), bevel=.015, seg=1)                   # duct seam
    # Twin exhaust nozzles with glowing rings.
    glow = a.part('Exhaust_glow', 'Alloy')
    for s in (-1, 1):
        x = s * .38
        dark.lathe([(.32, -.1), (.3, .4), (.25, .4), (.25, .12)], loc=(x, 5.05, -.04), rot=BACKWARD, seg=12)
        glow.torus(.21, .045, loc=(x, 5.4, -.04), rot=FORWARD, seg=12, ring=4)
        dark.cyl(.2, .02, loc=(x, 5.2, -.04), rot=FORWARD, seg=10, bevel=0)
    # Nose cannon under the nose, in a fairing.
    armor.box((.16, .8, .14), loc=(0, -4.8, -.2), bevel=.04)
    steel.cyl(.045, 1.0, loc=(0, -5.5, -.2), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, -6.0, -.2))
    # Wing bombs on pylons (one part so the runtime can hide them after the drop).
    bombs = a.part('Bombs', 'Armor')
    pylons = a.part('Pylons', 'Undercarriage')
    for s in (-1, 1):
        for x, y in ((1.9, .74), (3.1, .98)):
            pylons.box((.08, .7, .2), loc=(s * x, y, -.285), bevel=.02, seg=1)
            _bomb(bombs, (s * x, y, -.52))


# ----------------------------------------------------------------------------- munitions
def missile(a):
    h = .6
    a.part('Body', 'Fuel').lathe([(.04, -h), (.05, -h + .05), (.05, .36), (.04, .44)], rot=FORWARD, seg=10)
    a.part('Seeker', 'Armor').lathe([(.049, .34), (.04, .46), (.022, .56), (0, h)], rot=FORWARD, seg=10)
    fins = a.part('Fins', 'Armor')
    for k in range(4):
        ang = math.pi / 4 + k * R90
        _fin(fins, (0, h - .09, 0), ang, .09, .14, .012, .045)
        _fin(fins, (0, -.26, 0), ang, .04, .08, .01, .045)
    a.part('Motor', 'Alloy').cyl(.034, .04, loc=(0, h + .005, 0), rot=FORWARD, seg=10, bevel=0)


def rocket(a):
    h = .45
    a.part('Body', 'Armor').lathe([(.028, -h), (.035, -h + .04), (.035, .22), (.03, .26)], rot=FORWARD, seg=8)
    a.part('Warhead', 'Hazard').lathe([(.034, .2), (.03, .3), (.016, .4), (0, h)], rot=FORWARD, seg=8)
    fins = a.part('Fins', 'Armor')
    for k in range(4):
        _fin(fins, (0, h - .06, 0), k * R90, .05, .1, .008, .032)
    a.part('Motor', 'Alloy').cyl(.026, .04, loc=(0, h + .005, 0), rot=FORWARD, seg=8, bevel=0)


def bomb(a):
    _bomb(a.part('Body', 'Armor'), (0, 0, 0), seg=12)
    a.part('Nose_band', 'Hazard').cyl(.182, .06, loc=(0, -.36, 0), rot=FORWARD, seg=12, bevel=0)
    lugs = a.part('Lugs', 'Steel')
    for y in (-.2, .2):
        lugs.box((.05, .08, .06), loc=(0, y, .18), bevel=0)


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
    'missile': (missile, dict(ao_distance=.12, ground=False)),
    'rocket': (rocket, dict(ao_distance=.1, ground=False)),
    'bomb': (bomb, dict(ao_distance=.2, ground=False)),
    'cruise_missile': (cruise_missile, dict(ao_distance=.4, ground=False)),
}
