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


def attack_jet(a):
    """Ground-attack jet (A-10 lineage): straight low wings, two engine pods high on the rear
    fuselage with glowing exhausts, twin fins on the tailplane tips, a big nose cannon and wing
    pylons with rocket pods and missiles. Origin at the fuselage centre (it flies)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    body.loft([
        [(0, -5.85, -.12)],
        _octagon(-5.6, .26, -.34, .1),
        _octagon(-5.0, .5, -.58, .34),
        _octagon(-3.3, .68, -.72, .48),
        _octagon(-1.0, .74, -.74, .5),
        _octagon(1.5, .68, -.68, .46),
        _octagon(3.8, .46, -.44, .4),
        _octagon(5.45, .2, -.14, .22),
    ], bevel=.05, seg=2)
    glass = a.part('Canopy', 'Glass')
    glass.loft([_bubble(-4.85, .16, .26, .4), _bubble(-4.35, .4, .36, .94), _bubble(-3.4, .43, .44, 1.02),
                _bubble(-2.5, .26, .48, .72)], bevel=.03, seg=1)
    _hoop(a.part('Canopy_frames', 'Armor'), _bubble(-4.15, .415, .37, .975), r=.025)
    # GAU-8 style cannon out of the nose: barrel cluster, clamp and a dark muzzle.
    steel.cyl(.13, .5, loc=(0, -5.9, -.16), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    for k in range(5):
        ang = k * math.tau / 5
        steel.cyl(.03, .9, loc=(math.cos(ang) * .065, -6.45, -.16 + math.sin(ang) * .065), rot=FORWARD, seg=6,
                  bevel=0)
    steel.cyl(.12, .08, loc=(0, -6.82, -.16), rot=FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_gun', (0, -6.9, -.16))
    # Straight low wings with trailing-edge flaps, landing-gear fairings under the roots.
    for s in (-1, 1):
        body.prism([(s * .6, -1.35), (s * 6.5, -.7), (s * 6.5, .6), (s * .6, 1.0)], .22, loc=(0, 0, -.5), axis='Z',
                   bevel=.05)
        armor.box((5.4, .3, .03), loc=(s * 3.55, .66, -.385), rot=(0, 0, -s * .068), bevel=.01, seg=1)
        body.box((.46, 2.0, .38), loc=(s * 1.55, -.6, -.74), bevel=.14, taper=(.85, .8))
        a.part('Wing_lights', 'TeamGlow').box((.08, .3, .08), loc=(s * 6.52, -.05, -.5), bevel=.01, seg=1)
    # Engine pods high on the rear fuselage: dark fan faces, glowing exhaust rings.
    glow = a.part('Exhaust_glow', 'Alloy')
    for s in (-1, 1):
        x = s * 1.08
        body.lathe([(.46, -1.25), (.55, -1.0), (.56, .4), (.46, 1.05), (.36, 1.25)], loc=(x, 2.75, .8),
                   rot=BACKWARD, seg=14)
        dark.cyl(.42, .04, loc=(x, 1.48, .8), rot=FORWARD, seg=14, bevel=0)
        steel.cyl(.12, .12, r2=.02, loc=(x, 1.42, .8), rot=FORWARD, seg=8, bevel=0)                  # spinner
        dark.cyl(.3, .04, loc=(x, 3.99, .8), rot=FORWARD, seg=12, bevel=0)
        glow.torus(.3, .06, loc=(x, 4.03, .8), rot=FORWARD, seg=14, ring=4)
        body.limb((s * .22, 2.7, .34), (s * .82, 2.7, .72), .16, 1.5, bevel=.04, seg=1)             # pylon
    # Tailplane with twin rectangular fins on its tips.
    body.prism([(-.3, 4.4), (-2.7, 4.75), (-2.7, 5.55), (-.3, 5.7), (.3, 5.7), (2.7, 5.55), (2.7, 4.75), (.3, 4.4)],
               .12, loc=(0, 0, .2), axis='Z', bevel=.03)
    for s in (-1, 1):
        body.prism([(4.55, -.5), (5.6, -.5), (5.78, 1.62), (4.92, 1.66)], .12, loc=(s * 2.7, 0, 0), bevel=.03)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 4.6, .46), seg=8, rings=5)
    # Pylons: a rocket pod and an air-to-ground missile under each wing.
    pods = a.part('Pods', 'Armor')
    missiles = a.part('Missiles', 'Fuel')
    noses = a.part('Missile_noses', 'Armor')
    fins = a.part('Missile_fins', 'Armor')
    pylons = a.part('Pylons', 'Undercarriage')
    for s in (-1, 1):
        x = s * 2.9
        pylons.box((.1, .9, .24), loc=(x, -.35, -.7), bevel=.02, seg=1)
        pods.cyl(.21, 1.5, loc=(x, -.45, -1.0), rot=FORWARD, seg=12, bevel=.06)
        _tube_mouth(a, None, _frame((x, -1.2, -1.0), FORWARD), .2, protrude=.05, seg=12, name='Pod_tubes')
        x = s * 4.1
        pylons.box((.1, .9, .22), loc=(x, -.2, -.7), bevel=.02, seg=1)
        missiles.cyl(.11, 1.6, loc=(x, -.3, -.93), rot=FORWARD, seg=10, bevel=0)
        noses.cyl(.11, .26, r2=.03, loc=(x, -1.23, -.93), rot=FORWARD, seg=10, bevel=0)
        for k in range(4):
            _fin(fins, (x, .36, -.93), math.pi / 4 + k * R90, .14, .3, .02, .09)
    a.pivot('Muzzle_rocket', (0, -1.25, -1.0))
    a.pivot('Muzzle_missile', (0, -1.38, -.93))


def strike_drone(a):
    """Armed medium-altitude drone (MQ-9 lineage): slender fuselage with a bulbous satcom nose, long
    straight wings, a V-tail over a small ventral fin, a three-blade pusher `Propeller` (spins
    about local Y), a sensor ball under the nose and two missiles under each wing. Origin at the
    fuselage centre (it flies)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    body.loft([
        [(0, -3.25, 0)],
        _ring(-3.1, .2, 0, .16, top=.22),
        _ring(-2.8, .34, 0, .26, top=.4),
        _ring(-2.3, .38, 0, .3, top=.48),
        _ring(-1.7, .34, 0, .3, top=.38),
        _ring(-.6, .31, 0, .29, top=.31),
        _ring(1.2, .27, 0, .25, top=.27),
        _ring(2.5, .18, 0, .16, top=.18),
        _ring(2.95, .1, 0, .09, top=.1),
    ])
    # Long straight wings, a V-tail and a small ventral fin.
    for s in (-1, 1):
        body.prism([(s * .25, -.5), (s * 5.5, -.25), (s * 5.5, .15), (s * .25, .4)], .1, loc=(0, 0, .06), axis='Z',
                   bevel=.03)
        a.part('Wing_lights', 'TeamGlow').box((.06, .16, .05), loc=(s * 5.52, -.05, .06), bevel=.01, seg=1)
        _fin(body, (0, 2.45, .04), R90 - s * .72, 1.3, .52, .05, .1)
    _fin(body, (0, 2.5, -.02), -R90, .5, .44, .05, .1)
    # Sensor ball under the nose; satcom dome and antennas on the spine.
    armor.cyl(.08, .16, loc=(0, -2.55, -.32), seg=8, bevel=0)
    armor.sphere(.2, loc=(0, -2.55, -.44), seg=12, rings=8)
    a.part('Sensor', 'Glass').cyl(.08, .04, loc=(0, -2.74, -.46), rot=FORWARD, seg=10, bevel=0)
    for y in (-.9, .9):
        steel.box((.03, .18, .16), loc=(0, y, .36), rot=(-.3, 0, 0), bevel=0)
    # Pusher propeller behind the tail.
    dark.cyl(.11, .1, loc=(0, 3.0, 0), rot=FORWARD, seg=10, bevel=0)
    p = a.pivot('Propeller', (0, 3.08, 0))
    a.part('Propeller_hub', 'Steel', p).lathe([(.11, -.04), (.11, .06), (.07, .16), (0, .24)], rot=BACKWARD, seg=10)
    blades = a.part('Propeller_blades', 'Armor', p)
    for k in range(3):
        ang = R90 + k * math.tau / 3
        blades.box((.72, .04, .15), loc=(math.cos(ang) * .45, .04, math.sin(ang) * .45), rot=(0, -ang, 0),
                   bevel=.015, seg=1, taper=(.8, 1))
    # Two missiles under each wing, on their own pylons.
    missiles = a.part('Missiles', 'Fuel')
    noses = a.part('Missile_noses', 'Armor')
    fins = a.part('Missile_fins', 'Armor')
    pylons = a.part('Pylons', 'Undercarriage')
    for s in (-1, 1):
        for x in (s * 1.5, s * 2.4):
            pylons.box((.06, .45, .16), loc=(x, -.1, -.05), bevel=.01, seg=1)
            missiles.cyl(.065, 1.0, loc=(x, -.2, -.19), rot=FORWARD, seg=8, bevel=0)
            noses.cyl(.065, .14, r2=.02, loc=(x, -.77, -.19), rot=FORWARD, seg=8, bevel=0)
            for k in range(4):
                _fin(fins, (x, .2, -.19), math.pi / 4 + k * R90, .08, .16, .015, .055)
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
