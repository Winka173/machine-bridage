"""Machine Brigade aircraft and munitions built with frontier_kit.

Conventions (shared with ModelLibrary.cs): metres, +Z up, Blender -Y is the nose.
  * attack_helicopter: origin on the ground under the fuselage centre (skids touch z = 0).
    `Rotor` (main rotor hub, blades spin about local Z), `Tail_rotor` (hub on the fin, blades
    spin about local X), `Mount_gun` (chin turret yaw) with `Muzzle_gun`, and `Muzzle_rocket` /
    `Muzzle_missile` centred between the symmetric wing launchers.
  * gunship_heli and scout_heli follow attack_helicopter (origin on the ground, wheels or skids at
    z = 0); scout_heli's side guns are fixed, so its `Muzzle_gun` has no mount.
  * strike_jet: origin at the fuselage centre (it flies). `Bombs` is one part holding the four
    wing bombs (hidden once they drop); `Muzzle_gun` at the nose cannon.
  * attack_jet and strike_drone fly like strike_jet. strike_drone's pusher `Propeller` spins about
    local Y (the fuselage axis).
  * Munitions: origin at the centre, nose at -Y, emissive `Alloy` motors at the tail.
Team / TeamGlow parts are recoloured per army at runtime.
"""
import math

import bmesh
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
    # Chunky proportions (wide cabin, thick boom, big fin) so it still reads at RTS camera distance.
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    body.loft([
        _octagon(-4.55, .24, 1.2, 1.54),
        _octagon(-4.1, .5, .98, 1.8),
        _octagon(-3.2, .66, .9, 1.92),
        _octagon(-1.5, .76, .88, 2.04),
        _octagon(0.0, .8, .9, 2.12),
        _octagon(1.25, .7, 1.0, 2.06),
        _octagon(2.1, .44, 1.36, 2.0),
    ], bevel=.07, seg=2)
    body.loft([_octagon(1.8, .42, 1.4, 2.0), _octagon(4.75, .2, 1.6, 1.9)], bevel=.04, seg=1)      # tail boom
    body.prism([(3.85, 1.8), (4.85, 1.7), (5.15, 3.5), (4.6, 3.55)], .16, bevel=.03)                # fin
    body.box((2.2, .62, .09), loc=(0, 4.2, 1.8), bevel=.02, seg=1, taper=(1, .7))                    # stabiliser
    for s in (-1, 1):
        armor.box((.06, .44, .36), loc=(s * 1.1, 4.22, 1.82), bevel=.015, seg=1)                     # end plates
    # Tandem cockpit: gunner in front, pilot raised behind; frames over the glass.
    glass.loft([_bubble(-4.05, .32, 1.6, 1.82), _bubble(-3.55, .54, 1.7, 2.26), _bubble(-2.68, .56, 1.76, 2.34)],
               bevel=.03, seg=1)
    glass.loft([_bubble(-2.78, .58, 1.78, 2.44), _bubble(-2.4, .6, 1.8, 2.62), _bubble(-1.35, .58, 1.84, 2.64),
                _bubble(-.95, .46, 1.88, 2.42)], bevel=.03, seg=1)
    frames = a.part('Canopy_frames', 'Armor')
    for section in (_bubble(-3.5, .56, 1.71, 2.28), _bubble(-2.7, .58, 1.77, 2.38), _bubble(-2.35, .62, 1.8, 2.64),
                    _bubble(-1.4, .6, 1.84, 2.66)):
        _hoop(frames, section)
    # Engine nacelles on the shoulders with intakes and exhausts; rotor pylon between them.
    for s in (-1, 1):
        body.cyl(.36, 2.0, loc=(s * .74, .15, 2.18), rot=FORWARD, seg=12, bevel=.08)
        dark.cyl(.24, .06, loc=(s * .74, -.86, 2.18), rot=FORWARD, seg=12, bevel=0)                    # intakes
        dark.cyl(.25, .44, loc=(s * .8, 1.26, 2.2), rot=(R90 + .25, 0, s * -.3), seg=10, bevel=.02, bseg=1)
    body.box((1.0, 2.0, .56), loc=(0, -.45, 2.26), bevel=.08, taper=(.72, .8))                          # pylon
    steel.cyl(.12, .8, loc=(0, -.6, 2.86), seg=10, bevel=0)                                            # mast
    # Stub wings: rocket pods inboard, ATGM rails at the tips.
    pods = a.part('Pods', 'Armor')
    missiles = a.part('Missiles', 'Fuel')
    noses = a.part('Missile_noses', 'Armor')
    for s in (-1, 1):
        body.box((1.8, 1.1, .16), loc=(s * 1.52, .05, 1.52), bevel=.03, seg=1, taper=(1, .9))
        armor.box((.1, .5, .24), loc=(s * 1.5, .05, 1.36), bevel=.02, seg=1)                          # pod pylon
        pods.cyl(.23, 1.4, loc=(s * 1.5, -.05, 1.1), rot=FORWARD, seg=12, bevel=.06)
        _tube_mouth(a, None, _frame((s * 1.5, -.75, 1.1), FORWARD), .22, protrude=.05, seg=12, name='Pod_tubes')
        for k in range(6):  # rocket noses peeking out of the pod
            ang = k * math.tau / 6
            a.part('Pod_tubes', 'Steel').cyl(.03, .09, r2=.005, loc=(s * 1.5 + math.cos(ang) * .1, -.78,
                                                                      1.1 + math.sin(ang) * .1),
                                             rot=FORWARD, seg=5, bevel=0)
        armor.box((.08, 1.1, .5), loc=(s * 2.35, 0, 1.23), bevel=.02, seg=1)                          # ATGM rail
        for z in (1.35, 1.1):
            missiles.cyl(.08, 1.0, loc=(s * 2.46, -.05, z), rot=FORWARD, seg=8, bevel=0)
            noses.cyl(.08, .16, r2=.025, loc=(s * 2.46, -.63, z), rot=FORWARD, seg=8, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .12, .06), loc=(s * 2.44, .1, 1.52), bevel=.01, seg=1)
    a.pivot('Muzzle_rocket', (0, -.8, 1.1))
    a.pivot('Muzzle_missile', (0, -.71, 1.225))
    # Nose sensor turret and landing light.
    armor.box((.46, .38, .44), loc=(0, -4.6, 1.34), bevel=.06)
    a.part('Sensor', 'Glass').box((.32, .04, .14), loc=(0, -4.8, 1.37), bevel=.01, seg=1)
    a.part('Lamps', 'Lamp').box((.18, .12, .05), loc=(0, -3.9, .96), bevel=.01, seg=1)
    # Skids on arched struts.
    skids = a.part('Skids', 'Undercarriage')
    for s in (-1, 1):
        x = s * 1.05
        skids.tube([(x, 1.6, .065), (x, -1.8, .065), (x, -2.1, .16), (x, -2.25, .36)], .065, seg=8)
        for y, z in ((-1.1, 1.0), (.95, 1.12)):
            skids.tube([(x, y, .065), (s * 1.0, y, .5), (s * .45, y, z)], .055, seg=6)
    steel.cyl(.015, .6, loc=(0, 3.2, 2.2), seg=5, bevel=0)                                              # antenna
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 4.92, 3.6), seg=8, rings=5)

    # Chin gun on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -3.45, .92))
    a.part('Gun_turret', 'Armor', g).cyl(.22, .22, loc=(0, 0, -.08), seg=12, bevel=.04)
    gun = a.part('Gun', 'Steel', g)
    gun.box((.17, .44, .15), loc=(0, -.16, -.16), bevel=.03)
    gun.cyl(.038, 1.05, loc=(0, -.85, -.16), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.055, .12, loc=(0, -1.33, -.16), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, -1.39, -.16), g)

    # Main rotor: four blades on a hub at the mast top.
    r = a.pivot('Rotor', (0, -.6, 3.33))
    hub = a.part('Rotor_hub', 'Steel', r)
    hub.cyl(.32, .16, seg=12, bevel=.03)
    hub.cyl(.17, .2, loc=(0, 0, .16), seg=10, bevel=.04)
    blades = a.part('Rotor_blades', 'Armor', r)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        d = Vector((math.cos(ang), math.sin(ang), 0))
        blades.box((.38, 4.4, .05), loc=tuple(d * 2.45), rot=(0, 0, ang - R90), bevel=.02, seg=1, taper=(.85, 1))
        hub.box((.22, .5, .1), loc=tuple(d * .44), rot=(0, 0, ang - R90), bevel=.02, seg=1)             # grips
    # Tail rotor on the left of the fin, blades in the YZ plane.
    armor.cyl(.1, .18, loc=(-.15, 4.74, 2.86), rot=ACROSS, seg=10, bevel=.02, bseg=1)                 # gearbox
    tr = a.pivot('Tail_rotor', (-.3, 4.74, 2.86))
    a.part('Tail_rotor_hub', 'Steel', tr).cyl(.075, .1, rot=ACROSS, seg=8, bevel=.01, bseg=1)
    tblades = a.part('Tail_rotor_blades', 'Armor', tr)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        tblades.box((.03, .16, .72), loc=(0, -math.sin(ang) * .42, math.cos(ang) * .42), rot=(ang, 0, 0),
                    bevel=.01, seg=1)


def _ring(y, w, zc, h, top=None, seg=12):
    """Elliptical fuselage ring at y: half-width w, half-height h about zc. `top` replaces h for the
    upper half (a bulged spine or satcom hump)."""
    up = h if top is None else top
    return [(w * math.cos(u), y, zc + (up if math.sin(u) > 0 else h) * math.sin(u))
            for u in (-R90 + i * math.tau / seg for i in range(seg))]


def _arc(y, w, zc, h, a0=-.45, a1=math.pi + .45, n=9):
    """Upper arc of an elliptical ring (closed by its chord): a canopy blister over a _ring."""
    return [(w * math.cos(u), y, zc + h * math.sin(u)) for u in (a0 + (a1 - a0) * i / (n - 1) for i in range(n))]


def gunship_heli(a):
    """Heavy assault gunship (Mi-24 lineage): stepped tandem bubble canopies, a troop cabin under
    twin engines, anhedral stub wings with four rocket pods and two ATGM rails, a five-blade rotor
    and tricycle wheels. Origin on the ground under the cabin."""
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
    for s in (-1, 1):
        for y in (-2.5, -1.9, -1.3):                                                              # cabin windows
            w = .94 + (y + 3.0) * .04 / 3.2
            glass.box((.02, .38, .3), loc=(s * (w + .012), y, 1.72), bevel=.005, seg=1)
        armor.box((.04, 1.1, .38), loc=(s * .78, -4.15, 1.32), bevel=.01, seg=1)                    # cockpit armour
    # Twin engines over the cabin with dust-filter domes, gearbox fairing and mast.
    for s in (-1, 1):
        body.cyl(.4, 3.4, loc=(s * .52, -.9, 2.66), rot=FORWARD, seg=12, bevel=.1)
        armor.sphere((.34, .3, .34), loc=(s * .52, -2.6, 2.66), seg=10, rings=6)
        dark.cyl(.26, .5, loc=(s * .72, .92, 2.72), rot=(R90 + .25, 0, s * -.3), seg=10, bevel=.02, bseg=1)
    body.box((.9, 2.4, .5), loc=(0, -.7, 2.78), bevel=.1, taper=(.7, .8))
    steel.cyl(.13, .7, loc=(0, -.7, 3.2), seg=10, bevel=0)
    # Anhedral stub wings: two rocket pods each, ATGM launchers on the tip plates.
    pods = a.part('Pods', 'Armor')
    missiles = a.part('Missiles', 'Fuel')
    noses = a.part('Missile_noses', 'Armor')
    droop = math.tan(.2)

    def wing_z(x):
        return 1.72 - (x - .9) * droop
    for s in (-1, 1):
        body.limb((s * .8, 0, wing_z(.8)), (s * 3.25, 0, wing_z(3.25)), .16, 1.3, bevel=.04, seg=1, taper=(1, .75))
        for x in (1.6, 2.45):
            z = wing_z(x)
            armor.box((.12, .6, .34), loc=(s * x, -.05, z - .22), bevel=.02, seg=1)                  # pylon
            pods.cyl(.26, 1.6, loc=(s * x, -.1, z - .54), rot=FORWARD, seg=12, bevel=.07, bseg=1)
            _tube_mouth(a, None, _frame((s * x, -.9, z - .54), FORWARD), .25, protrude=.05, seg=12, name='Pod_tubes')
        z = wing_z(3.25)
        armor.box((.1, 1.2, .7), loc=(s * 3.3, -.05, z - .2), bevel=.02, seg=1)                        # tip plate
        for zz in (z - .05, z - .38):
            missiles.cyl(.085, 1.1, loc=(s * 3.435, -.1, zz), rot=FORWARD, seg=8, bevel=0)
            noses.cyl(.085, .18, r2=.03, loc=(s * 3.435, -.74, zz), rot=FORWARD, seg=8, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .14, .06), loc=(s * 3.36, .5, z + .17), bevel=.01, seg=1)
    a.pivot('Muzzle_rocket', (0, -.97, (wing_z(1.6) + wing_z(2.45)) / 2 - .54))
    a.pivot('Muzzle_missile', (0, -.86, wing_z(3.25) - .215))
    # Tricycle landing gear (the retractable kind, shown down): twin nose wheels, mains behind the wings.
    gear = a.part('Gear', 'Steel')
    tyres = a.part('Tyres', 'Rubber')
    for x in (-.17, .17):
        tyres.cyl(.26, .14, loc=(x, -4.9, .26), rot=ACROSS, seg=10, bevel=.05, bseg=1)
    gear.cyl(.05, .5, loc=(0, -4.9, .26), rot=ACROSS, seg=6, bevel=0)
    gear.limb((0, -4.9, .26), (0, -4.75, .9), .1, .1, bevel=.02, seg=1)
    for s in (-1, 1):
        tyres.cyl(.36, .24, loc=(s * 1.22, 1.1, .36), rot=ACROSS, seg=12, bevel=.07, bseg=1)
        gear.limb((s * 1.08, 1.1, .36), (s * .76, .9, 1.25), .12, .12, bevel=.02, seg=1)            # oleo
        gear.limb((s * 1.08, 1.1, .36), (s * .72, 1.7, 1.12), .08, .08, bevel=.015, seg=1)          # drag brace
    a.part('Lamps', 'Lamp').box((.2, .14, .06), loc=(0, -4.3, .79), bevel=.01, seg=1)
    steel.cyl(.015, .6, loc=(0, 3.5, 2.36), seg=5, bevel=0)                                           # antenna
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 6.72, 3.8), seg=8, rings=5)

    # Four-barrel chin gun on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -5.55, .8))
    a.part('Gun_turret', 'Armor', g).sphere(.3, loc=(0, 0, -.04), seg=12, rings=8)
    gun = a.part('Gun', 'Steel', g)
    gun.cyl(.11, .16, loc=(0, -.32, -.1), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        gun.cyl(.035, 1.0, loc=(math.cos(ang) * .06, -.82, -.1 + math.sin(ang) * .06), rot=FORWARD, seg=6, bevel=0)
    gun.cyl(.1, .08, loc=(0, -1.22, -.1), rot=FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_gun', (0, -1.34, -.1), g)

    # Five-blade main rotor.
    r = a.pivot('Rotor', (0, -.7, 3.55))
    hub = a.part('Rotor_hub', 'Steel', r)
    hub.cyl(.38, .18, seg=12, bevel=.03, bseg=1)
    hub.cyl(.2, .24, loc=(0, 0, .18), seg=10, bevel=.04, bseg=1)
    blades = a.part('Rotor_blades', 'Armor', r)
    for k in range(5):
        ang = R90 + k * math.tau / 5
        d = Vector((math.cos(ang), math.sin(ang), 0))
        blades.box((.44, 5.8, .06), loc=tuple(d * 3.3), rot=(0, 0, ang - R90), bevel=.02, seg=1, taper=(.85, 1))
        hub.box((.24, .6, .12), loc=tuple(d * .52), rot=(0, 0, ang - R90), bevel=.02, seg=1)
    # Three-blade tail rotor on the right of the fin, blades in the YZ plane.
    armor.cyl(.12, .2, loc=(.17, 6.62, 3.0), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    tr = a.pivot('Tail_rotor', (.32, 6.62, 3.0))
    a.part('Tail_rotor_hub', 'Steel', tr).cyl(.09, .12, rot=ACROSS, seg=8, bevel=.01, bseg=1)
    tblades = a.part('Tail_rotor_blades', 'Armor', tr)
    for k in range(3):
        ang = k * math.tau / 3
        tblades.box((.04, .2, .95), loc=(0, -math.sin(ang) * .6, math.cos(ang) * .6), rot=(ang, 0, 0), bevel=.01,
                    seg=1)


def scout_heli(a):
    """Light scout helicopter (MH-6 lineage): egg-shaped cabin under a glass blister, slim tail
    boom with a T-tail, and a weapon plank carrying a minigun and a rocket pod on each side.
    Origin on the ground under the cabin (skids at z = 0)."""
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
    body.loft([_ring(1.0, .25, 1.52, .25, seg=8), _ring(5.0, .12, 1.68, .12, seg=8)], bevel=0)      # tail boom
    body.prism([(4.5, 1.62), (5.1, 1.62), (5.25, 2.3), (4.95, 2.32)], .08, bevel=.02)                # upper fin
    body.prism([(4.62, 1.62), (5.02, 1.62), (5.14, 1.12), (4.96, 1.1)], .08, bevel=.02)               # lower fin
    body.box((1.5, .42, .06), loc=(0, 5.12, 2.3), bevel=.02, seg=1, taper=(1, .7))                  # T-tail
    for s in (-1, 1):
        armor.box((.05, .3, .26), loc=(s * .76, 5.12, 2.3), bevel=.01, seg=1)                        # end plates
    body.box((.62, 1.2, .38), loc=(0, .3, 2.03), bevel=.12, taper=(.8, .8))                         # engine hump
    dark.cyl(.1, .3, loc=(0, .95, 1.98), rot=FORWARD, seg=10, bevel=.01, bseg=1)                    # exhaust
    steel.cyl(.08, .42, loc=(0, 0, 2.38), seg=10, bevel=0)                                         # mast
    a.part('Lamps', 'Lamp').box((.14, .1, .05), loc=(0, -1.55, .64), bevel=.01, seg=1)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 5.2, 2.36), seg=8, rings=5)
    # Skids on arched cross tubes.
    skids = a.part('Skids', 'Undercarriage')
    for s in (-1, 1):
        x = s * .92
        skids.tube([(x, 1.05, .05), (x, -1.45, .05), (x, -1.72, .14), (x, -1.84, .3)], .05, seg=8)
        skids.tube([(x, -.95, .05), (s * .86, -.95, .45), (s * .45, -.95, .72)], .04, seg=6)
        skids.tube([(x, .45, .05), (s * .86, .45, .45), (s * .35, .45, .9)], .04, seg=6)
    # Weapon plank through the cabin: a minigun inboard and a rocket pod outboard on each side.
    armor.box((2.7, .24, .12), loc=(0, -.35, .84), bevel=.03, seg=1)
    guns = a.part('Miniguns', 'Steel')
    pods = a.part('Pods', 'Armor')
    for s in (-1, 1):
        x = s * 1.0
        armor.box((.08, .18, .14), loc=(x, -.35, .72), bevel=.01, seg=1)                             # hanger
        guns.box((.17, .52, .19), loc=(x, -.4, .6), bevel=.03, seg=1)                               # motor, feed
        guns.cyl(.075, .92, loc=(x, -1.08, .6), rot=FORWARD, seg=8, bevel=0)                         # barrels
        guns.cyl(.095, .1, loc=(x, -1.48, .6), rot=FORWARD, seg=8, bevel=0)                          # clamp
        x = s * 1.32
        armor.box((.08, .3, .14), loc=(x, -.4, .74), bevel=.01, seg=1)
        pods.cyl(.17, 1.1, loc=(x, -.5, .6), rot=FORWARD, seg=10, bevel=.05)
        _tube_mouth(a, None, _frame((x, -1.05, .6), FORWARD), .16, protrude=.04, seg=10, name='Pod_tubes')
    a.pivot('Muzzle_gun', (0, -1.54, .6))
    a.pivot('Muzzle_rocket', (0, -1.1, .6))

    # Six-blade main rotor.
    r = a.pivot('Rotor', (0, 0, 2.6))
    hub = a.part('Rotor_hub', 'Steel', r)
    hub.cyl(.24, .12, seg=12, bevel=.02)
    hub.cyl(.12, .16, loc=(0, 0, .12), seg=10, bevel=.03)
    blades = a.part('Rotor_blades', 'Armor', r)
    for k in range(6):
        ang = k * math.tau / 6
        d = Vector((math.cos(ang), math.sin(ang), 0))
        blades.box((.26, 3.6, .04), loc=tuple(d * 2.2), rot=(0, 0, ang - R90), bevel=.015, seg=1, taper=(.85, 1))
    # Two-blade tail rotor on the left of the fin.
    armor.cyl(.07, .14, loc=(-.09, 5.0, 1.72), rot=ACROSS, seg=8, bevel=.01, bseg=1)
    tr = a.pivot('Tail_rotor', (-.2, 5.0, 1.72))
    a.part('Tail_rotor_hub', 'Steel', tr).cyl(.05, .08, rot=ACROSS, seg=8, bevel=.01, bseg=1)
    a.part('Tail_rotor_blades', 'Armor', tr).box((.025, .12, 1.2), rot=(.3, 0, 0), bevel=.008, seg=1)


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


def _skin_panel(part, pf, frame, s0, s1, u0, u1, out=.013, inn=.012, lower=.72):
    """Access panel standing `out` proud of a surface's upper skin between spans s0..s1 and chord
    fractions u0..u1; its bevelled edge and baked occlusion draw the panel line."""
    loops = []
    for s in (s0, s1):
        le, c, t, h = pf.at(s)
        up = t / (1 + lower)
        us = [u0] + [u for u in FOIL_U if u0 + .02 < u < u1 - .02] + [u1]
        top = [(s, le + u * c, h + max(up * _naca(u), .007) + out) for u in us]
        bot = [(s, le + u * c, h + max(up * _naca(u), .007) - inn) for u in reversed(us)]
        loops.append([frame(*q) for q in top + bot])
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


def _squircle(w, h, n=12):
    """Rounded-rectangle outline (superellipse, exponent 4) starting at +x, counter-clockwise."""
    return [(w * math.copysign(abs(math.cos(u)) ** .5, math.cos(u)), h * math.copysign(abs(math.sin(u)) ** .5, math.sin(u)))
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


def _bomb(p, loc, length=1.6, r=.17, seg=10, guided=False, band=True, kit=None):
    """Low-drag general-purpose bomb (nose at -Y) on parts p = dict(body=, band=, steel=, glass=):
    ogive nose with fuze, parallel body, boat tail with four fins, a yellow nose band, lugs on top.
    guided=True adds a laser seeker with canards; kit='jdam' a tail kit with strakes."""
    x, y, z = loc
    h = length / 2
    p['body'].lathe([(r * .36, -h * .98), (r * .42, -h * .86), (r * .7, -h * .5), (r, -h * .2), (r, h * .3),
                     (r * .88, h * .56), (r * .6, h * .8), (r * .3, h * .94), (r * .18, h)], loc=loc, rot=FORWARD,
                    seg=seg)
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
    for dy in (-length * .16, length * .16):
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
    armor.loft([[(0, -5.84, -.04)], _sec(-5.6, .11, -.13, .06), _sec(-5.3, .19, -.2, .13), _sec(-4.9, .275, -.26, .205)])
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
        _patch(panels, hull, 2.9, 4.45, i0, i1, out=.014, inn=.012, bevel=.005)
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
        glow.box((.06, .16, .06), loc=(x, 1.36, .03), bevel=.01, seg=1)
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
            racks.box((.05, .12, .1), loc=(x + dx, .8, zt - .31), bevel=0)
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


def _rocket_pod(a, x, y, z, r, length, tubes=7, part='Pods'):
    """Rocket pod (front at y) with a ring of dark tube mouths on its face and a pointed tail."""
    pods = a.part(part, 'Armor')
    pods.lathe([(r * .55, length), (r * .85, length * .9), (r, length * .65), (r, .04), (r * .92, 0)], loc=(x, y, z),
               rot=BACKWARD, seg=12)
    a.part('Pod_bands', 'Hazard').cyl(r + .012, .05, loc=(x, y + length * .22, z), rot=FORWARD, seg=12, bevel=0)
    bores = a.part('Pod_tubes_bore', 'Undercarriage')
    pts = [(0.0, 0.0)] + [(math.cos(k * math.tau / (tubes - 1)) * r * .56, math.sin(k * math.tau / (tubes - 1)) * r * .56)
                          for k in range(tubes - 1)]
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


def attack_jet(a):
    """Ground-attack jet (A-10 lineage): boxy armoured fuselage around a seven-barrel nose cannon,
    a bubble canopy, straight wings with gear pods at the roots, drooped tips and split ailerons,
    two turbofans high on the rear fuselage and a twin-fin tailplane. Pylons carry bombs, rocket
    pods, air-to-ground and air-to-air missiles. Origin at the fuselage centre (it flies)."""
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
        steel.cyl(.028, .82, loc=(math.cos(ang) * .075, -6.46, -.16 + math.sin(ang) * .075), rot=FORWARD, seg=6, bevel=0)
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
        _skin_panel(panels, outer, frame, 3.0, 4.3, .22, .56)
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
        glow.box((.04, .12, .04), loc=(s * 2.74, 5.65, 1.66), bevel=0)
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
    part.loft([ring(r0, c0, t0, pitch0), ring((r0 + r1) / 2, (c0 + c1) / 2 * 1.08, (t0 + t1) / 2, (pitch0 + pitch1) / 2),
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
    # Stores: a laser-guided bomb inboard and a twin missile rail outboard under each wing.
    stores = _store_parts(a, None, 'Ordnance')
    pylons = a.part('Pylons', 'Armor')
    mis = dict(body=a.part('Missiles', 'Fuel'), fins=a.part('Missile_fins', 'Armor'),
               nose=a.part('Missile_seekers', 'Glass'), band=a.part('Missile_bands', 'Hazard'))
    for s in (-1, 1):
        x = s * 1.45
        zt = wing.bottom(1.45)
        _pylon(pylons, x, -.5, .2, zt + .04, zt - .1, w=.06)
        _bomb(stores, (x, -.3, zt - .1 - .12 - .015), length=1.3, r=.12, seg=8, guided=True)
        x = s * 2.45
        zt = wing.bottom(2.45)
        _pylon(pylons, x, -.45, .15, zt + .04, -.105, w=.06)
        pylons.box((.26, .7, .04), loc=(x, -.35, -.115), bevel=.01, seg=1)                    # launcher rail
        for dx in (-.085, .085):
            _aam(mis, (x + dx, -.86 + .475, -.19), length=.95, r=.055, seg=8, canards=False, fin=1.4)
    a.pivot('Muzzle_missile', (0, -.86, -.19))


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
    'gunship_heli': (gunship_heli, dict(ao_distance=.7, grime_height=.4)),
    'scout_heli': (scout_heli, dict(ao_distance=.5, grime_height=.35)),
    'attack_jet': (attack_jet, dict(ao_distance=.6, ground=False)),
    'strike_drone': (strike_drone, dict(ao_distance=.4, ground=False)),
    'missile': (missile, dict(ao_distance=.12, ground=False)),
    'rocket': (rocket, dict(ao_distance=.1, ground=False)),
    'bomb': (bomb, dict(ao_distance=.2, ground=False)),
    'cruise_missile': (cruise_missile, dict(ao_distance=.4, ground=False)),
}
