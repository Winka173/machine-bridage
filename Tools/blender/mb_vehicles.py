"""Machine Brigade vehicles built with frontier_kit.

Conventions (shared with ModelLibrary.cs): metres, +Z up, Blender -Y is the front, origin on the
ground at the hull centre. Each vehicle has a `Turret` empty at the turret ring; turret parts are
authored relative to it. Parts named Main_cannon / Muzzle_brake recoil along the barrel. Parts
using the `Team` / `TeamGlow` materials are recoloured per army at runtime.
"""
import math

R90 = math.pi / 2
FORWARD = (R90, 0, 0)   # cylinder axis along Y (a cone's narrow end points to the front, -Y)
ACROSS = (0, R90, 0)    # cylinder axis along X


def tracks(a, half_width, length, height, wheel_r, wheels, z, belt_width=0.46):
    """Track belts with cleats on the exposed curves, fenders and road wheels (after 3d_astra)."""
    belt = a.part('Tracks', 'Undercarriage')
    wheel = a.part('Wheels', 'Steel')
    fender = a.part('Fenders', 'Armor')
    for s in (-1, 1):
        x = s * half_width
        rb = min(.26, height * .45)
        belt.box((belt_width, length, height), loc=(x, 0, z), bevel=rb, seg=3)
        for y0 in (-1, 1):
            for zc, angles in ((z + height / 2 - rb, (.5, 1.05)), (z - height / 2 + rb, (-.5, -1.05))):
                for phi in angles:
                    radial = (y0 * math.cos(phi), math.sin(phi))
                    belt.box((belt_width + .04, .08, .05),
                             loc=(x, y0 * (length / 2 - rb) + radial[0] * rb, zc + radial[1] * rb),
                             rot=(math.atan2(-radial[0], radial[1]), 0, 0), bevel=.012, seg=1)
        fender.box((belt_width + .14, length * .92, .06), loc=(x, -.03, z + height / 2 + .05), bevel=.02, seg=1,
                   taper=(1, .98))
        for i in range(wheels):
            y = -length / 2 + .5 + i * (length - 1.0) / (wheels - 1)
            wheel.cyl(wheel_r, .08, loc=(x + s * (belt_width / 2 + .02), y, z - .06), rot=ACROSS, seg=14, bevel=.02,
                      bseg=1)
            belt.cyl(wheel_r * .4, .1, loc=(x + s * (belt_width / 2 + .04), y, z - .06), rot=ACROSS, seg=8,
                     bevel=.01, bseg=1)


def _barrel(a, turret, start_y, length, radius, height, pitch=0.0, brake=(.26, .28, .24), sleeve=None):
    """Main gun from the mantlet forwards, optionally pitched up; muzzle brake at the tip."""
    # Rotating local Z by (90 deg - pitch) about X points it along (0, -cos, sin): forward and up.
    rot = (R90 - pitch, 0, 0)
    direction = (0.0, -math.cos(pitch), math.sin(pitch))
    centre = (0, start_y + direction[1] * length / 2, height + direction[2] * length / 2)
    cannon = a.part('Main_cannon', 'Steel', turret)
    cannon.cyl(radius, length, loc=centre, rot=rot, seg=14, bevel=.015, bseg=1)
    if sleeve:
        at, sleeve_len, sleeve_r = sleeve
        mid = (0, start_y + direction[1] * length * at, height + direction[2] * length * at)
        cannon.cyl(sleeve_r, sleeve_len, loc=mid, rot=rot, seg=14, bevel=.02)
    tip = (0, start_y + direction[1] * (length + brake[1] * .4), height + direction[2] * (length + brake[1] * .4))
    a.part('Muzzle_brake', 'Undercarriage', turret).box(brake, loc=tip, rot=(-pitch, 0, 0), bevel=.03)


def _antenna(a, turret, x, y, z, height=1.0):
    a.part('Antenna', 'Steel', turret).cyl(.012, height, loc=(x, y, z + height / 2), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow', turret).sphere(.045, loc=(x, y, z + height + .02), seg=8, rings=5)


def light_tank(a):
    tracks(a, 1.02, 4.4, .72, .25, 5, .42, belt_width=.5)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.3, .5), (-2.3, .74), (-1.55, 1.12), (1.95, 1.12), (2.25, .92), (2.25, .5)], 1.62, bevel=.06)
    for s in (-1, 1):
        armor.box((.1, 4.0, .4), loc=(s * 1.3, -.05, .8), bevel=.03, taper=(1, .97))
        steel.bolts([(s * 1.36, y, .92) for y in (-1.5, -.75, 0, .75, 1.5)], r=.035, h=.04, rot=ACROSS)
        a.part('Lamps', 'Lamp').box((.2, .04, .1), loc=(s * .5, -2.31, .72), bevel=.01, seg=1)
        steel.cyl(.08, .3, loc=(s * .55, 2.32, .84), rot=FORWARD, seg=10, bevel=.015, bseg=1)
        steel.box((.14, .16, .1), loc=(s * .62, -2.36, .54), bevel=.02, seg=1)
    deck.grille(1.0, .6, loc=(0, 1.35, 1.13), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
    steel.cyl(.72, .14, loc=(0, -.1, 1.17), seg=24, bevel=.03)
    armor.box((.8, .45, .06), loc=(0, -1.35, 1.14), bevel=.015, seg=1)

    t = a.pivot('Turret', (0, -.1, 1.24))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.62, .7), (.62, .7), (.74, .15), (.62, -.5), (.28, -.8), (-.28, -.8), (-.62, -.5), (-.74, .15)]
    turret.prism(outline, .5, loc=(0, 0, .25), axis='Z', bevel=.05, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.1, .45, .34), loc=(0, .85, .24), bevel=.04, taper=(.95, .9))
    tarm.box((.42, .24, .34), loc=(0, -.84, .25), bevel=.04)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.2, .12, loc=(.3, .18, .56), seg=12, bevel=.03, bseg=1)
    for s in (-1, 1):
        for i in range(2):
            tsteel.cyl(.04, .14, loc=(s * (.52 + i * .07), -.42, .42), rot=(.6, 0, s * .4), seg=8, bevel=0)
    a.part('Periscope', 'Glass', t).box((.1, .05, .06), loc=(-.28, -.3, .53), bevel=.01, seg=1)
    _antenna(a, t, -.45, .62, .5, .9)
    _barrel(a, t, start_y=-.95, length=1.9, radius=.085, height=.25, brake=(.22, .26, .2),
            sleeve=(.08, .32, .12))


def main_battle_tank(a):
    tracks(a, 1.28, 5.8, .9, .3, 7, .5, belt_width=.62)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.0, .58), (-3.0, .86), (-2.1, 1.38), (2.5, 1.38), (2.95, 1.1), (2.95, .58)], 2.0, bevel=.07)
    for s in (-1, 1):
        armor.box((.12, 5.3, .56), loc=(s * 1.63, -.1, 1.0), bevel=.035, taper=(1, .97))
        steel.bolts([(s * 1.7, y, 1.14) for y in (-2.0, -1.0, 0, 1.0, 2.0)], r=.04, h=.04, rot=ACROSS)
        a.part('Lamps', 'Lamp').box((.22, .04, .11), loc=(s * .62, -3.01, .82), bevel=.01, seg=1)
        steel.box((.16, .18, .12), loc=(s * .75, -3.06, .62), bevel=.02, seg=1)
        steel.cyl(.1, .36, loc=(s * .7, 3.02, 1.0), rot=FORWARD, seg=10, bevel=.015, bseg=1)
    for x in (-1.1, -.55, 0, .55, 1.1):  # add-on armour blocks on the glacis
        armor.box((.5, .42, .12), loc=(x, -2.52, 1.14), rot=(-.52, 0, 0), bevel=.02, seg=1)
    deck.grille(1.3, .8, loc=(0, 1.8, 1.39), rot=(-R90, 0, 0), slats=7, depth=.1, thickness=.05)
    steel.cyl(.98, .16, loc=(0, .15, 1.44), seg=28, bevel=.03)
    armor.box((.9, .5, .07), loc=(0, -1.75, 1.4), bevel=.015, seg=1)

    t = a.pivot('Turret', (0, .15, 1.52))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.95, 1.05), (.95, 1.05), (1.12, .25), (.95, -.72), (.42, -1.18), (-.42, -1.18), (-.95, -.72),
               (-1.12, .25)]
    turret.prism(outline, .66, loc=(0, 0, .33), axis='Z', bevel=.06, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.6, .7, .5), loc=(0, 1.35, .32), bevel=.05, taper=(.95, .9))
    tarm.box((.62, .34, .5), loc=(0, -1.22, .33), bevel=.05)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):  # stowage baskets
        tsteel.box((.08, 1.0, .3), loc=(s * 1.08, .75, .42), bevel=.015, seg=1)
        for i in range(3):
            tsteel.cyl(.05, .16, loc=(s * (.78 + i * .09), -.7, .56), rot=(.6, 0, s * .4), seg=8, bevel=0)
    tsteel.cyl(.3, .22, loc=(.42, .25, .77), seg=16, bevel=.04)
    a.part('Cupola_top', 'Armor', t).cyl(.26, .08, loc=(.42, .25, .92), seg=16, bevel=.02, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(4):
        ang = k * math.tau / 4 + .4
        glass.box((.1, .05, .07), loc=(.42 + math.cos(ang) * .29, .25 + math.sin(ang) * .29, .8),
                  rot=(0, 0, ang + R90), bevel=.01, seg=1)
    tsteel.box((.34, .3, .26), loc=(-.55, -.5, .76), bevel=.04)  # sight box
    a.part('Sight', 'Glass', t).box((.24, .04, .14), loc=(-.55, -.66, .78), bevel=.01, seg=1)
    _antenna(a, t, -.7, .95, .66, 1.2)
    _barrel(a, t, start_y=-1.38, length=3.0, radius=.11, height=.33, brake=(.26, .24, .26),
            sleeve=(.45, .5, .165))


def artillery(a):
    tracks(a, 1.2, 5.4, .8, .28, 6, .45, belt_width=.56)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.8, .52), (-2.8, .82), (-2.1, 1.14), (2.75, 1.14), (2.75, .52)], 1.9, bevel=.06)
    armor.box((1.5, 1.0, .42), loc=(0, -1.75, 1.34), bevel=.05, taper=(.9, .8))  # driver cab
    a.part('Visor', 'Glass').box((1.1, .04, .14), loc=(0, -2.2, 1.38), rot=(-.4, 0, 0), bevel=.01, seg=1)
    for s in (-1, 1):
        armor.box((.1, 5.0, .44), loc=(s * 1.5, 0, .84), bevel=.03)
        a.part('Lamps', 'Lamp').box((.2, .04, .1), loc=(s * .6, -2.81, .76), bevel=.01, seg=1)
        armor.box((.5, .12, .7), loc=(s * .7, 2.95, .55), rot=(.5, 0, 0), bevel=.03)  # recoil spades
    deck.grille(.9, .5, loc=(0, -.85, 1.15), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)

    t = a.pivot('Turret', (0, .8, 1.14))
    turret = a.part('Turret_body', 'Team', t)
    turret.box((2.2, 2.7, 1.25), loc=(0, .15, .64), bevel=.07, taper=(.94, .96))
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((2.26, 2.0, .12), loc=(0, .35, 1.3), bevel=.03, seg=1)
    for s in (-1, 1):
        tarm.box((.08, .9, .7), loc=(s * 1.12, .45, .6), bevel=.02, seg=1)  # side doors
        a.part('Ammo', 'Hazard', t).box((.5, .3, .3), loc=(s * .55, 1.62, .36), bevel=.03)
    a.part('Vents', 'Undercarriage', t).grille(.8, .5, loc=(0, 1.51, .75), slats=5, depth=.06, thickness=.04)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.box((.7, .5, .9), loc=(0, -1.32, .66), bevel=.05)  # cradle
    tsteel.cyl(.22, .14, loc=(.6, .4, 1.4), seg=12, bevel=.03, bseg=1)
    _antenna(a, t, -.8, 1.2, 1.3, 1.1)
    _barrel(a, t, start_y=-1.55, length=4.4, radius=.13, height=.7, pitch=.14, brake=(.38, .42, .3),
            sleeve=(.2, .8, .18))


def scout_jeep(a):
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    chassis = a.part('Chassis', 'Undercarriage')
    rubber = a.part('Tyres', 'Rubber')
    chassis.box((1.45, 3.7, .26), loc=(0, 0, .55), bevel=.04)
    for sx in (-1, 1):
        for y in (-1.25, 1.2):
            rubber.cyl(.42, .34, loc=(sx * .86, y, .42), rot=ACROSS, seg=18, bevel=.07, bseg=2)
            steel.cyl(.22, .36, loc=(sx * .86, y, .42), rot=ACROSS, seg=10, bevel=.02, bseg=1)
            body.box((.46, 1.05, .1), loc=(sx * .9, y, .92), bevel=.03, taper=(1, .8))
    body.prism([(-2.0, .62), (-2.0, .96), (-1.1, 1.12), (-.36, 1.14), (-.36, .62)], 1.7, bevel=.05)
    body.box((1.72, 2.3, .52), loc=(0, .8, .88), bevel=.05)
    a.part('Seats', 'Canvas').box((1.3, .6, .35), loc=(0, .15, 1.28), bevel=.06)
    frame = [(-.82, -.36, 1.12), (-.82, -.36, 1.66), (.82, -.36, 1.66), (.82, -.36, 1.12)]
    steel.tube(frame, .035, seg=8)
    a.part('Glass', 'Glass').box((1.56, .03, .44), loc=(0, -.38, 1.39), rot=(-.12, 0, 0), bevel=.01, seg=1)
    steel.tube([(-.82, 1.55, 1.12), (-.82, 1.55, 1.78), (.82, 1.55, 1.78), (.82, 1.55, 1.12)], .045, seg=8)
    for sx in (-1, 1):
        a.part('Lamps', 'Lamp').cyl(.1, .06, loc=(sx * .55, -2.02, .98), rot=FORWARD, seg=12, bevel=.01, bseg=1)
    chassis.grille(.72, .26, loc=(0, -2.03, .8), slats=4, depth=.05, thickness=.04)
    steel.box((1.5, .12, .14), loc=(0, -2.1, .58), bevel=.03)  # bumper
    rubber.cyl(.36, .22, loc=(0, 2.03, 1.02), rot=FORWARD, seg=18, bevel=.06)
    a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(.58, 2.0, 1.05), bevel=.03)
    steel.cyl(.012, 1.1, loc=(.72, 1.75, 1.7), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.045, loc=(.72, 1.75, 2.27), seg=8, rings=5)

    t = a.pivot('Turret', (0, .72, 1.14))
    a.part('Mount', 'Steel', t).cyl(.07, .52, loc=(0, 0, .26), seg=10, bevel=.01)
    a.part('Gun_shield', 'Armor', t).box((.66, .06, .42), loc=(0, -.22, .66), bevel=.02, taper=(.9, 1))
    cannon = a.part('Main_cannon', 'Steel', t)
    cannon.box((.14, .42, .16), loc=(0, 0, .64), bevel=.02)
    cannon.cyl(.035, 1.0, loc=(0, -.66, .66), rot=FORWARD, seg=8, bevel=0)
    a.part('Ammo_box', 'Armor', t).box((.2, .18, .16), loc=(.16, .05, .56), bevel=.02)


# name: (builder, Asset options). Vehicles use tight contact AO like 3d_astra's units.
BUILDERS = {
    'scout_jeep': (scout_jeep, dict(ao_distance=.5, grime_height=.45)),
    'light_tank': (light_tank, dict(ao_distance=.55, grime_height=.5)),
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
    'artillery': (artillery, dict(ao_distance=.6, grime_height=.55)),
}
