"""Machine Brigade ground vehicles built with frontier_kit.

Conventions (shared with ModelLibrary.cs): metres, +Z up, Blender -Y is the front, origin on the
ground at the hull centre. Each vehicle has a `Turret` empty at the turret ring; turret parts are
authored relative to it. Parts named Main_cannon* / Muzzle_brake* recoil along the barrel. Parts
using the `Team` / `TeamGlow` materials are recoloured per army at runtime.

Weapon empties: `Muzzle_main` sits at the tip of the main weapon (child of Turret). Secondary
weapons add `Muzzle_coax` (beside the main gun), `Muzzle_mg` (roof machine gun on its own
`Mount_mg` yaw pivot) and `Muzzle_missile` (launcher opening). A `Radar` pivot spins about Z.
"""
import math

from mathutils import Euler, Matrix, Vector

from frontier_kit import chamfered

R90 = math.pi / 2
FORWARD = (R90, 0, 0)   # cylinder axis along Y (a cone's narrow end points to the front, -Y)
ACROSS = (0, R90, 0)    # cylinder axis along X


def tracks(a, half_width, length, height, wheel_r, wheels, z, belt_width=.46, wheel_seg=14, lean=False):
    """Track belts with cleats on the exposed curves, fenders and road wheels (after 3d_astra).
    The belt runs from its top at z + height / 2 down to 1 cm below the ground, so the vehicle
    sits on its tracks. lean=True drops the bevels on cleats and hub caps (invisible at RTS
    range) to save triangles."""
    belt = a.part('Tracks', 'Undercarriage')
    wheel = a.part('Wheels', 'Steel')
    fender = a.part('Fenders', 'Armor')
    top, bottom = z + height / 2, -.01
    for s in (-1, 1):
        x = s * half_width
        rb = min(.26, height * .45)
        belt.box((belt_width, length, top - bottom), loc=(x, 0, (top + bottom) / 2), bevel=rb, seg=3)
        for y0 in (-1, 1):
            for zc, angles in ((top - rb, (.5, 1.05)), (bottom + rb, (-.5, -1.05))):
                for phi in angles:
                    radial = (y0 * math.cos(phi), math.sin(phi))
                    belt.box((belt_width + .04, .08, .05),
                             loc=(x, y0 * (length / 2 - rb) + radial[0] * rb, zc + radial[1] * rb),
                             rot=(math.atan2(-radial[0], radial[1]), 0, 0), bevel=0 if lean else .012, seg=1)
        fender.box((belt_width + .14, length * .92, .06), loc=(x, -.03, z + height / 2 + .05), bevel=.02, seg=1,
                   taper=(1, .98))
        for i in range(wheels):
            y = -length / 2 + .5 + i * (length - 1.0) / (wheels - 1)
            wheel.cyl(wheel_r, .08, loc=(x + s * (belt_width / 2 + .02), y, z - .06), rot=ACROSS, seg=wheel_seg,
                      bevel=.02, bseg=1)
            belt.cyl(wheel_r * .4, .1, loc=(x + s * (belt_width / 2 + .04), y, z - .06), rot=ACROSS, seg=8,
                     bevel=0 if lean else .01, bseg=1)


def _barrel(a, turret, start_y, length, radius, height, pitch=0.0, brake=(.26, .28, .24), sleeve=None, x=0.0,
            suffix='', seg=14):
    """Main gun from the mantlet forwards, optionally pitched up; muzzle brake at the tip.
    Returns the centre of the muzzle brake's front face (where `Muzzle_main` goes)."""
    # Rotating local Z by (90 deg - pitch) about X points it along (0, -cos, sin): forward and up.
    rot = (R90 - pitch, 0, 0)
    direction = (0.0, -math.cos(pitch), math.sin(pitch))

    def along(d):
        return (x, start_y + direction[1] * d, height + direction[2] * d)

    cannon = a.part(f'Main_cannon{suffix}', 'Steel', turret)
    cannon.cyl(radius, length, loc=along(length / 2), rot=rot, seg=seg, bevel=.015, bseg=1)
    if sleeve:
        at, sleeve_len, sleeve_r = sleeve
        cannon.cyl(sleeve_r, sleeve_len, loc=along(length * at), rot=rot, seg=seg, bevel=.02)
    a.part(f'Muzzle_brake{suffix}', 'Undercarriage', turret).box(brake, loc=along(length + brake[1] * .4),
                                                                 rot=(-pitch, 0, 0), bevel=.03)
    return along(length + brake[1] * .9)


def _antenna(a, turret, x, y, z, height=1.0):
    a.part('Antenna', 'Steel', turret).cyl(.012, height, loc=(x, y, z + height / 2), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow', turret).sphere(.045, loc=(x, y, z + height + .02), seg=8, rings=5)


def _coax(a, turret, x, y, z, length=.4, housing=.26):
    """Coaxial machine gun: a housing whose back half is buried in the turret face at y, and a
    thin barrel forwards. Adds `Muzzle_coax` at the barrel tip."""
    coax = a.part('Coax', 'Steel', turret)
    front = y - housing / 2
    coax.box((.1, housing, .1), loc=(x, y, z), bevel=.02, seg=1)
    coax.cyl(.022, length - .04, loc=(x, front - length / 2 + .04, z), rot=FORWARD, seg=8, bevel=0)
    coax.cyl(.034, .08, loc=(x, front - length + .06, z), rot=FORWARD, seg=8, bevel=0)  # flash hider
    a.pivot('Muzzle_coax', (x, front - length + .02, z), turret)


def _roof_mg(a, parent, loc, length=.8, shield=True):
    """Pintle heavy machine gun on its own `Mount_mg` yaw pivot: receiver, barrel, shield, ammo can."""
    m = a.pivot('Mount_mg', loc, parent)
    mg = a.part('MG', 'Steel', m)
    mg.cyl(.05, .15, loc=(0, 0, .065), seg=8, bevel=.01, bseg=1)             # pintle
    mg.box((.14, .36, .14), loc=(0, .02, .2), bevel=.02, seg=1)               # receiver
    mg.box((.05, .16, .08), loc=(0, .24, .17), rot=(.3, 0, 0), bevel=.01, seg=1)  # grips
    front = .02 - .18
    mg.cyl(.028, length - .05, loc=(0, front - length / 2 + .045, .21), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.042, .12, loc=(0, front - length + .08, .21), rot=FORWARD, seg=8, bevel=0)      # flash hider
    a.part('MG_ammo', 'Armor', m).box((.12, .2, .14), loc=(.14, .04, .19), bevel=.02, seg=1)
    if shield:
        a.part('MG_shield', 'Armor', m).box((.48, .04, .3), loc=(0, -.24, .25), rot=(-.12, 0, 0), bevel=.012,
                                             seg=1, taper=(.8, 1))
    a.pivot('Muzzle_mg', (0, front - length + .02, .21), m)


def _smoke(a, part, x, y, z, s, count=3, gap=.07, r=.04, depth=.14):
    """Smoke-grenade dischargers angled up and outwards on side s."""
    for i in range(count):
        part.cyl(r, depth, loc=(s * (x + i * gap), y, z), rot=(.6, 0, s * .4), seg=8, bevel=0)


def _wheel(a, x, y, r, width, seg=16):
    """Big off-road tyre touching the ground (z = r) with a steel hub and centre cap."""
    a.part('Tyres', 'Rubber').cyl(r, width, loc=(x, y, r), rot=ACROSS, seg=seg, bevel=r * .16, bseg=2)
    hubs = a.part('Hubs', 'Steel')
    hubs.cyl(r * .52, width + .04, loc=(x, y, r), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    hubs.cyl(r * .2, width + .1, loc=(x, y, r), rot=ACROSS, seg=6, bevel=0)


def _frame(loc, rot):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


def _tube_mouth(a, parent, m, r, protrude=.07, seg=10, name='Tubes'):
    """Launcher tube opening facing local +Z of matrix m: a steel lip around a dark bore whose
    recess darkens in the baked AO. The lip starts 3 cm inside the launcher face."""
    loc, rot = m.to_translation(), m.to_euler('XYZ')
    a.part(name, 'Steel', parent).lathe([(r, -.03), (r, protrude), (r * .74, protrude), (r * .74, protrude * .3)],
                                        loc=loc, rot=rot, seg=seg)
    a.part(f'{name}_bore', 'Undercarriage', parent).cyl(r * .7, .02, loc=m @ Vector((0, 0, protrude * .3 + .012)),
                                                        rot=rot, seg=seg, bevel=0)


def _dish(part, loc, rx, rz, depth=.15, seg=12, tilt=0.0):
    """Elliptical search-radar reflector: the back centre sits at loc, the concave side faces -Y
    and is tilted up by `tilt` radians."""
    turn = Matrix.Rotation(-tilt, 3, 'X')
    base = Vector(loc)

    def ring(k, dy):
        return [tuple(base + turn @ Vector((rx * k * math.cos(u), dy, rz * k * math.sin(u))))
                for u in (i * math.tau / seg for i in range(seg))]
    part.loft([[tuple(base)], ring(.55, -depth * .35), ring(1.0, -depth), ring(.96, -depth - .05),
               ring(.5, -depth * .35 - .05), [tuple(base + turn @ Vector((0, -.05, 0)))]])


# ----------------------------------------------------------------------------- tanks
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
        _smoke(a, tsteel, .52, -.42, .42, s, count=2)
    a.part('Periscope', 'Glass', t).box((.1, .05, .06), loc=(-.28, -.3, .53), bevel=.01, seg=1)
    _antenna(a, t, -.45, .62, .5, .9)
    tip = _barrel(a, t, start_y=-.95, length=1.9, radius=.085, height=.25, brake=(.22, .26, .2),
                  sleeve=(.08, .32, .12))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .29, -.8, .31, length=.36, housing=.32)


def main_battle_tank(a):
    # Lean running gear and unbevelled bolts keep the tank inside the 6000-triangle budget with
    # its new coax and roof gun; at RTS range the difference does not show.
    tracks(a, 1.28, 5.8, .9, .3, 7, .5, belt_width=.62, wheel_seg=12, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.0, .58), (-3.0, .86), (-2.1, 1.38), (2.5, 1.38), (2.95, 1.1), (2.95, .58)], 2.0, bevel=.07)
    for s in (-1, 1):
        armor.box((.12, 5.3, .56), loc=(s * 1.63, -.1, 1.0), bevel=.035, taper=(1, .97))
        steel.bolts([(s * 1.7, y, 1.14) for y in (-2.0, -1.0, 0, 1.0, 2.0)], r=.04, h=.04, rot=ACROSS, bevel=0)
        a.part('Lamps', 'Lamp').box((.22, .04, .11), loc=(s * .62, -3.01, .82), bevel=.01, seg=1)
        steel.box((.16, .18, .12), loc=(s * .75, -3.06, .62), bevel=.02, seg=1)
        steel.cyl(.1, .36, loc=(s * .7, 3.02, 1.0), rot=FORWARD, seg=10, bevel=.015, bseg=1)
    for x in (-1.1, -.55, 0, .55, 1.1):  # add-on armour blocks on the glacis
        armor.box((.5, .42, .12), loc=(x, -2.52, 1.14), rot=(-.52, 0, 0), bevel=.02, seg=1)
    deck.grille(1.3, .8, loc=(0, 1.8, 1.39), rot=(-R90, 0, 0), slats=7, depth=.1, thickness=.05)
    steel.cyl(.98, .16, loc=(0, .15, 1.44), seg=24, bevel=.03)
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
        _smoke(a, tsteel, .78, -.7, .56, s, count=3, gap=.09, r=.05, depth=.16)
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
    tip = _barrel(a, t, start_y=-1.38, length=3.0, radius=.11, height=.33, brake=(.26, .24, .26),
                  sleeve=(.45, .5, .165))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .45, -1.17, .44, length=.46, housing=.3)
    _roof_mg(a, t, (.42, .25, .95), length=.85)


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
        armor.box((.1, 5.0, .44), loc=(s * 1.515, 0, .84), bevel=.03)  # 1.5 cm proud of the fenders
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
    tip = _barrel(a, t, start_y=-1.55, length=4.4, radius=.13, height=.7, pitch=.14, brake=(.38, .42, .3),
                  sleeve=(.2, .8, .18))
    a.pivot('Muzzle_main', tip, t)
    _roof_mg(a, t, (.6, .4, 1.46), length=.75)


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
    a.part('Glass', 'Glass').box((1.6, .03, .44), loc=(0, -.38, 1.39), rot=(-.12, 0, 0), bevel=.01, seg=1)
    steel.tube([(-.82, 1.55, 1.12), (-.82, 1.55, 1.78), (.82, 1.55, 1.78), (.82, 1.55, 1.12)], .045, seg=8)
    for sx in (-1, 1):
        a.part('Lamps', 'Lamp').cyl(.1, .06, loc=(sx * .55, -2.02, .98), rot=FORWARD, seg=12, bevel=.01, bseg=1)
    chassis.grille(.72, .26, loc=(0, -2.03, .8), slats=4, depth=.05, thickness=.04)
    steel.box((1.5, .12, .14), loc=(0, -2.05, .6), bevel=.03)  # bumper
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
    a.pivot('Muzzle_main', (0, -1.16, .66), t)  # the pintle machine gun is the jeep's main weapon


# ----------------------------------------------------------------------------- new vehicles
def _hull_section(y, zb, z1, z2, zt, wb, w1, w2, wt):
    """Eight-point hull cross-section: narrow belly, flared lower flank (zb->z1), short upright
    band (z1->z2) and inward-sloped upper flank to the roof (z2->zt)."""
    return [(-wb, y, zb), (wb, y, zb), (w1, y, z1), (w2, y, z2), (wt, y, zt), (-wt, y, zt), (-w2, y, z2),
            (-w1, y, z1)]


def apc(a):
    """8x8 wheeled armoured personnel carrier with a wedge nose and a 30 mm turret."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.3, -1.12, .82, 2.0):
        for s in (-1, 1):
            _wheel(a, s * 1.15, y, .56, .44)
    hull.loft([
        _hull_section(-3.42, .86, .95, 1.03, 1.12, .62, .8, .82, .66),
        _hull_section(-2.75, .48, 1.02, 1.28, 1.5, .9, 1.2, 1.24, .96),
        _hull_section(-1.9, .45, 1.05, 1.35, 2.0, .9, 1.24, 1.28, 1.0),
        _hull_section(3.2, .45, 1.05, 1.35, 2.0, .9, 1.24, 1.28, 1.0),
        _hull_section(3.4, .58, 1.05, 1.33, 1.93, .86, 1.2, 1.24, .96),
    ], bevel=.06, seg=2)
    # Bolted add-on armour on the sloped upper flanks (rotated onto the 23-degree slope).
    slope = math.atan2(1.28 - 1.0, 2.0 - 1.35)
    for s in (-1, 1):
        for y in (-1.25, .15, 1.55):
            armor.box((.06, 1.3, .52), loc=(s * (1.14 + .018), y, 1.683), rot=(0, -s * slope, 0), bevel=.015, seg=1)
        a.part('Lamps', 'Lamp').box((.2, .07, .1), loc=(s * .42, -3.43, .99), bevel=.01, seg=1)
        steel.box((.12, .2, .12), loc=(s * .5, -3.3, .78), bevel=.02, seg=1)                # tow hooks
        a.part('Tail_lights', 'Alloy').box((.14, .06, .1), loc=(s * .9, 3.4, 1.62), bevel=.01, seg=1)
        steel.box((.1, .12, .08), loc=(s * .47, 3.44, 1.66), bevel=.01, seg=1)             # door hinges
        steel.box((.1, .12, .08), loc=(s * .47, 3.44, .9), bevel=.01, seg=1)
        armor.box((.75, 1.15, .06), loc=(s * .45, 2.35, 2.01), bevel=.015, seg=1)          # troop hatches
    # Trim vane folded on the upper glacis, driver hatch and vision blocks.
    armor.box((1.1, .06, .34), loc=(0, -3.0, 1.37), rot=(-1.04, 0, 0), bevel=.015, seg=1)
    armor.cyl(.28, .08, loc=(-.52, -1.55, 2.01), seg=14, bevel=.02, bseg=1)
    glass = a.part('Vision_blocks', 'Glass')
    for dx in (-.16, 0, .16):
        glass.box((.12, .05, .07), loc=(-.52 + dx, -1.92, 1.99), rot=(-.53, 0, 0), bevel=.01, seg=1)
    a.part('Deck', 'Undercarriage').grille(.72, .7, loc=(.48, -1.3, 2.01), rot=(-R90, 0, 0), slats=6, depth=.07,
                                           thickness=.04)
    armor.box((1.0, .08, 1.0), loc=(0, 3.42, 1.25), bevel=.02, seg=1)                  # rear door
    steel.box((.3, .06, .05), loc=(.25, 3.47, 1.3), bevel=.01, seg=1)                   # door handle
    dark.box((1.2, .3, .08), loc=(0, 3.47, .6), bevel=.02, seg=1)                       # rear step
    steel.cyl(.62, .1, loc=(0, -.55, 2.02), seg=20, bevel=.02, bseg=1)                  # turret ring
    _antenna(a, None, -.85, 3.0, 1.95, 1.3)

    t = a.pivot('Turret', (0, -.55, 2.06))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.55, .62), (.55, .62), (.66, .12), (.55, -.42), (.3, -.66), (-.3, -.66), (-.55, -.42), (-.66, .12)]
    turret.prism(outline, .5, loc=(0, 0, .27), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.36, .24, .3), loc=(0, -.72, .28), bevel=.035)                           # mantlet
    tarm.box((.9, .3, .3), loc=(0, .7, .25), bevel=.035, taper=(.95, .9))              # bustle
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.box((.26, .26, .22), loc=(.3, .1, .6), bevel=.035)                          # commander sight
    a.part('Sight', 'Glass', t).box((.18, .04, .11), loc=(.3, -.03, .62), bevel=.01, seg=1)
    for s in (-1, 1):
        _smoke(a, tsteel, .44, -.4, .44, s, count=2, gap=.07)
    # Twin ATGM launcher box on an arm off the left side.
    tsteel.box((.34, .22, .12), loc=(-.72, .02, .38), bevel=.02, seg=1)
    launcher = a.part('Launcher', 'Armor', t)
    launcher.box((.3, 1.0, .46), loc=(-.95, .02, .42), bevel=.04)
    for z in (.31, .53):
        _tube_mouth(a, t, _frame((-.95, -.47, z), FORWARD), .085, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-.95, -.53, .42), t)
    tip = _barrel(a, t, start_y=-.84, length=1.95, radius=.05, height=.28, brake=(.11, .2, .11),
                  sleeve=(.1, .34, .075), seg=10)
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .25, -.69, .33, length=.32, housing=.3)


def mlrs(a):
    """6x6 armoured truck carrying a trainable 12-round rocket pod."""
    cab = a.part('Cab', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.55, 1.2, 2.55):
        for s in (-1, 1):
            _wheel(a, s * 1.02, y, .55, .42)
    for s in (-1, 1):
        dark.box((.2, 6.9, .3), loc=(s * .46, -.15, .8), bevel=.03, seg=1)              # frame rails
    dark.box((1.5, 1.6, .48), loc=(0, -2.85, .92), bevel=.05)                           # engine block
    dark.grille(1.1, .3, loc=(0, -3.66, .97), slats=4, depth=.06, thickness=.05)
    steel.box((2.3, .2, .22), loc=(0, -3.72, .72), bevel=.04)                           # bumper
    cab.prism([(-3.66, 1.1), (-3.72, 1.72), (-3.38, 2.62), (-2.0, 2.7), (-1.92, 1.1)], 2.36, bevel=.07)
    glass = a.part('Windows', 'Glass')
    (wy, wz), rx = (-3.72 + .34 * .55, 1.72 + .9 * .55), -math.atan2(.34, .9)
    ny, nz = -math.cos(rx), -math.sin(rx)  # windshield outward normal (forwards and up)
    for s in (-1, 1):
        glass.box((.86, .04, .4), loc=(s * .5, wy + ny * .012, wz + nz * .012), rot=(rx, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .7, .34), loc=(s * 1.19, -2.72, 2.22), bevel=.01, seg=1)
        a.part('Lamps', 'Lamp').box((.24, .06, .14), loc=(s * .82, -3.7, 1.34), bevel=.01, seg=1)
        armor.box((.54, 1.3, .07), loc=(s * 1.02, -2.55, 1.15), bevel=.02, seg=1)        # front fenders
        armor.box((.48, .07, .34), loc=(s * 1.02, -1.93, .97), bevel=.02, seg=1)         # mud flaps
        a.part('Tail_lights', 'Alloy').box((.14, .06, .1), loc=(s * .98, 3.64, 1.24), bevel=.01, seg=1)
        # Stabiliser jacks at the rear corners, pads stowed just above the ground.
        armor.box((.26, .26, .46), loc=(s * .95, 3.42, 1.0), bevel=.03, seg=1)
        steel.cyl(.07, .6, loc=(s * .95, 3.42, .55), seg=10, bevel=0)
        steel.cyl(.2, .07, loc=(s * .95, 3.42, .25), seg=12, bevel=.02, bseg=1)
        armor.box((.14, .9, .5), loc=(s * .9, -.7, .9), bevel=.03)                       # stowage lockers
    armor.cyl(.26, .07, loc=(.45, -2.6, 2.69), seg=12, bevel=.02, bseg=1)                # cab hatch
    steel.cyl(.07, 1.5, loc=(.95, -1.9, 2.02), seg=8, bevel=0)                          # exhaust stack
    steel.cyl(.1, .18, loc=(.95, -1.9, 2.72), seg=8, bevel=0)
    for z in (1.6, 2.3):
        steel.box((.06, .12, .06), loc=(.95, -1.97, z), bevel=0)                         # stack brackets
    armor.box((2.3, 5.25, .2), loc=(0, 1.0, 1.24), bevel=.04)                           # launcher bed
    _antenna(a, None, -.9, -2.1, 2.66, 1.2)

    t = a.pivot('Turret', (0, 1.55, 1.34))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.85, .14, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                    # turntable
    tarm.box((1.5, 1.6, .4), loc=(0, .1, .3), bevel=.05, taper=(.9, .92))
    pitch, length, height, width = .35, 3.5, 1.12, 1.95
    hinge = Vector((0, .95, .52))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    centre = hinge - turn @ Vector((0, length / 2, -height / 2))
    pod = _frame(centre, rot)
    a.part('Pod', 'Team', t).box((width, length, height), loc=centre, rot=rot, bevel=.06)
    frame = a.part('Pod_frame', 'Armor', t)
    for y in (-length / 2 + .12, length / 2 - .12):  # reinforcing bands at both ends
        frame.box((width + .06, .16, height + .06), loc=pod @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
    tsteel.cyl(.12, 1.7, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)             # elevation hinge
    for s in (-1, 1):
        tarm.box((.14, .5, .5), loc=(s * .8, .95, .4), bevel=.02, seg=1)                  # hinge cheeks
        tsteel.limb((s * .5, -.35, .42), tuple(pod @ Vector((s * .5, -.55, -height / 2 + .02))), .12, .12,
                    bevel=.02)                                                           # elevation rams
    for row in (-.36, 0, .36):
        for col in (-.66, -.22, .22, .66):
            _tube_mouth(a, t, pod @ _frame((col, -length / 2, row), FORWARD), .15, protrude=.07, seg=10)
    a.pivot('Muzzle_main', tuple(pod @ Vector((0, -length / 2 - .07, 0))), t)


def aa_vehicle(a):
    """Tracked self-propelled anti-aircraft gun: twin 35 mm cannons, search radar and a SAM box."""
    tracks(a, 1.02, 4.6, .72, .25, 5, .42, belt_width=.5, wheel_seg=12, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.4, .5), (-2.4, .74), (-1.65, 1.12), (2.05, 1.12), (2.35, .92), (2.35, .5)], 1.62, bevel=.06)
    for s in (-1, 1):
        armor.box((.1, 4.2, .4), loc=(s * 1.3, -.05, .8), bevel=.03, taper=(1, .97))
        steel.bolts([(s * 1.36, y, .92) for y in (-1.5, 0, 1.5)], r=.035, h=.04, rot=ACROSS, bevel=0)
        a.part('Lamps', 'Lamp').box((.2, .04, .1), loc=(s * .5, -2.41, .72), bevel=.01, seg=1)
        steel.box((.14, .16, .1), loc=(s * .62, -2.46, .54), bevel=.02, seg=1)
        steel.cyl(.08, .3, loc=(s * .55, 2.42, .84), rot=FORWARD, seg=10, bevel=.015, bseg=1)
    deck.grille(1.0, .5, loc=(0, 1.72, 1.13), rot=(-R90, 0, 0), slats=5, depth=.08, thickness=.04)
    armor.box((.8, .45, .06), loc=(0, -1.45, 1.14), bevel=.015, seg=1)
    steel.cyl(.8, .12, loc=(0, .15, 1.16), seg=20, bevel=.03)

    t = a.pivot('Turret', (0, .15, 1.2))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.74, .98), (.74, .98), (.8, .3), (.74, -.55), (.42, -.92), (-.42, -.92), (-.74, -.55), (-.8, .3)]
    turret.prism(outline, .72, loc=(0, 0, .38), axis='Z', bevel=.05, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tips = []
    for s, suffix in ((-1, '_L'), (1, '_R')):
        tarm.box((.3, 1.3, .5), loc=(s * .92, -.12, .42), bevel=.04, taper=(.9, .95))      # gun housings
        tsteel.box((.2, .7, .26), loc=(s * .74, .05, .42), bevel=.02, seg=1)                # trunnion arms
        tips.append(_barrel(a, t, start_y=-.76, length=2.25, radius=.055, height=.44, brake=(.13, .24, .13),
                            sleeve=(.07, .34, .09), x=s * .92, suffix=suffix, seg=10))
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    # 4-cell SAM box on the roof, front left; tracking sensor front right.
    launcher = a.part('Launcher', 'Armor', t)
    launcher.box((.56, 1.0, .56), loc=(-.36, -.08, .99), bevel=.04)
    for x in (-.49, -.23):
        for z in (.86, 1.12):
            _tube_mouth(a, t, _frame((x, -.58, z), FORWARD), .1, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-.36, -.64, .99), t)
    tsteel.box((.42, .36, .3), loc=(.36, -.42, .86), bevel=.04)
    a.part('Sight', 'Glass', t).box((.3, .04, .14), loc=(.36, -.6, .88), bevel=.01, seg=1)
    # Search radar pedestal at the rear; the dish spins on its own pivot.
    tsteel.cyl(.14, .3, loc=(0, .72, .86), seg=12, bevel=.02, bseg=1)
    r = a.pivot('Radar', (0, .72, 1.0), t)
    mast = a.part('Radar_mast', 'Steel', r)
    mast.cyl(.07, .46, loc=(0, 0, .23), seg=8, bevel=0)
    mast.box((.1, .24, .12), loc=(0, -.08, .48), bevel=.02, seg=1)             # yoke to the dish back
    mast.limb((0, -.22, .5), (0, -.52, .56), .035, .035, bevel=0)             # feed horn
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.18, .5), .6, .26, depth=.14, tilt=.25)
    _antenna(a, t, .6, .7, .7, .9)


def flame_tank(a):
    """Medium tank with a short, fat flame projector and armoured fuel tanks on the rear deck."""
    tracks(a, 1.12, 4.8, .78, .27, 6, .45, belt_width=.54, wheel_seg=12, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    fuel = a.part('Fuel_tanks', 'Fuel')
    hazard = a.part('Hazard_bands', 'Hazard')
    hull.prism([(-2.5, .52), (-2.5, .78), (-1.7, 1.2), (2.2, 1.2), (2.5, .98), (2.5, .52)], 1.76, bevel=.06)
    for s in (-1, 1):
        armor.box((.1, 4.4, .44), loc=(s * 1.42, -.05, .86), bevel=.03, taper=(1, .97))    # side skirts
        steel.bolts([(s * 1.48, y, .98) for y in (-1.6, -.5, .6, 1.7)], r=.035, h=.04, rot=ACROSS, bevel=0)
        a.part('Lamps', 'Lamp').box((.2, .04, .1), loc=(s * .55, -2.51, .74), bevel=.01, seg=1)
        steel.box((.14, .16, .1), loc=(s * .65, -2.56, .56), bevel=.02, seg=1)
        steel.cyl(.08, .28, loc=(s * .6, 2.52, .86), rot=FORWARD, seg=10, bevel=.015, bseg=1)
        # Fuel tanks lying along the rear deck in armoured cradles.
        x = s * .45
        fuel.cyl(.3, 1.5, loc=(x, 1.52, 1.53), rot=FORWARD, seg=14, bevel=.1)
        for y in (1.02, 2.02):
            hazard.cyl(.315, .1, loc=(x, y, 1.53), rot=FORWARD, seg=14, bevel=0)
            armor.box((.58, .16, .2), loc=(x, y, 1.26), bevel=.02, seg=1)                  # cradles
        steel.tube([(x, .72, 1.5), (x * .7, .5, 1.36), (x * .45, .28, 1.28)], .045, seg=6)  # feed pipes
        steel.cyl(.06, .08, loc=(x, .74, 1.53), rot=FORWARD, seg=8, bevel=0)
    armor.box((1.62, .12, .5), loc=(0, .66, 1.44), rot=(.35, 0, 0), bevel=.03)             # blast shield
    armor.box((1.66, .1, .56), loc=(0, 2.32, 1.36), bevel=.03, seg=1)                      # rear guard
    for s in (-1, 1):                                                                        # tub side plates
        armor.box((.08, 1.62, .42), loc=(s * .82, 1.52, 1.4), bevel=.02, seg=1, taper=(1, .96))
    armor.box((.8, .45, .06), loc=(0, -1.4, 1.21), bevel=.015, seg=1)
    steel.cyl(.74, .12, loc=(0, -.45, 1.24), seg=20, bevel=.03)

    t = a.pivot('Turret', (0, -.45, 1.3))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.6, .66), (.6, .66), (.74, .2), (.66, -.42), (.36, -.74), (-.36, -.74), (-.66, -.42), (-.74, .2)]
    turret.prism(outline, .56, loc=(0, 0, .28), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.52, .3, .42), loc=(0, -.82, .3), bevel=.05)                                  # mantlet
    tarm.box((.9, .36, .34), loc=(0, .72, .26), bevel=.04, taper=(.95, .9))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.22, .12, loc=(-.28, .16, .6), seg=12, bevel=.03, bseg=1)                   # hatch
    for s in (-1, 1):
        _smoke(a, tsteel, .54, -.42, .44, s, count=2)
    a.part('Periscope', 'Glass', t).box((.12, .05, .07), loc=(.3, -.34, .57), bevel=.01, seg=1)
    _antenna(a, t, .45, .56, .52, .9)
    # Flame projector: fat barrel with cooling rings and a tapered nozzle; a pilot light glows below.
    cannon = a.part('Main_cannon', 'Steel', t)
    y0, h, length = -.96, .3, 1.0
    cannon.cyl(.14, length, loc=(0, y0 - length / 2, h), rot=FORWARD, seg=14, bevel=.02, bseg=1)
    cannon.cyl(.2, .44, loc=(0, y0 - .2, h), rot=FORWARD, seg=14, bevel=.03)
    for y in (-.62, -.8):
        cannon.cyl(.165, .06, loc=(0, y0 + y, h), rot=FORWARD, seg=14, bevel=.01, bseg=1)
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.17, .26, r2=.11, loc=(0, y0 - length - .1, h), rot=FORWARD,
                                                   seg=14, bevel=.02)
    a.part('Muzzle_brake_glow', 'Alloy', t).sphere(.04, loc=(0, y0 - length - .16, h - .14), seg=8, rings=5)
    a.pivot('Muzzle_main', (0, y0 - length - .23, h), t)
    _coax(a, t, .34, -.72, .4, length=.34, housing=.34)


# ----------------------------------------------------------------------------- roster v3
def _flank(bottom, top, t, out=.02):
    """Point a fraction t up a sloped hull flank running from `bottom` to `top` ((x, z) on the +X
    side), pushed `out` along its outward normal, and the flank's lean from vertical. A box laid
    on side s uses loc=(s * x, y, z) and rot=(0, -s * lean, 0)."""
    (x0, z0), (x1, z1) = bottom, top
    dx, dz = x1 - x0, z1 - z0
    n = math.hypot(dx, dz)
    return x0 + dx * t + dz / n * out, z0 + dz * t - dx / n * out, math.atan2(-dx, dz)


def _glacis(front, back, t, out=.02):
    """Point a fraction t along a sloped front plate from `front` to `back` ((y, z), rising towards
    the back), pushed `out` along its normal, and the X rotation that lays a box flat on it."""
    (y0, z0), (y1, z1) = front, back
    dy, dz = y1 - y0, z1 - z0
    n = math.hypot(dy, dz)
    return y0 + dy * t - dz / n * out, z0 + dz * t + dy / n * out, math.atan2(dz, dy)


def _rws(a, parent, loc, length=.85):
    """Remote weapon station on its own `Mount_mg` yaw pivot: armoured cradle, sensor head and a
    heavy machine gun, with `Muzzle_mg` at the barrel tip."""
    m = a.pivot('Mount_mg', loc, parent)
    body = a.part('RWS', 'Armor', m)
    body.cyl(.2, .1, loc=(0, 0, .05), seg=12, bevel=.02, bseg=1)
    body.box((.4, .56, .3), loc=(0, .06, .25), bevel=.04, seg=1)               # cradle
    body.box((.22, .3, .26), loc=(-.32, .02, .3), bevel=.03, seg=1)             # sensor head
    body.box((.16, .3, .2), loc=(.3, .14, .25), bevel=.03, seg=1)               # ammo box
    a.part('RWS_sensor', 'Glass', m).box((.16, .04, .14), loc=(-.32, -.14, .31), bevel=.01, seg=1)
    gun = a.part('RWS_gun', 'Steel', m)
    gun.box((.13, .4, .13), loc=(.08, -.3, .3), bevel=.02, seg=1)             # receiver
    front = -.5
    gun.cyl(.03, length, loc=(.08, front - length / 2 + .02, .3), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.046, .12, loc=(.08, front - length + .06, .3), rot=FORWARD, seg=8, bevel=0)  # flash hider
    a.pivot('Muzzle_mg', (.08, front - length, .3), m)


# Mudguard arch (y offset, z) over a 0.52 m wheel: outer edge forwards, inner edge back.
ARCH = [(-.54, .9), (-.38, 1.14), (.38, 1.14), (.54, .9), (.48, .9), (.34, 1.09), (-.34, 1.09), (-.48, .9)]


def armored_car(a):
    """6x6 wheeled armoured car: a narrow wedge hull between six big outboard wheels under separate
    mudguards (the 8x8 APC hides its wheels under a wide hull), and a small 30 mm turret."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.05, -.15, 1.75):
        for s in (-1, 1):
            _wheel(a, s * 1.09, y, .52, .4)
            armor.prism([(y + dy, z) for dy, z in ARCH], .46, loc=(s * 1.09, 0, 0), bevel=0)  # mudguards
            dark.box((.26, .18, .14), loc=(s * .9, y, .52), bevel=.02, seg=1)                # hub carriers
    full = (.44, .78, 1.2, 1.56, .7, .88, .88, .7)
    hull.loft([
        _hull_section(-3.15, .74, .8, .86, .92, .5, .64, .64, .52),
        _hull_section(-2.7, .5, .78, 1.1, 1.2, .66, .86, .86, .68),
        _hull_section(-1.45, *full),
        _hull_section(2.9, *full),
        _hull_section(3.15, .58, .8, 1.18, 1.5, .66, .86, .86, .68),
    ], bevel=.06, seg=2)
    for s in (-1, 1):
        for y in (-1.1, .8):                                                             # side bins
            armor.box((.08, .8, .32), loc=(s * .9, y, .98), bevel=.015, seg=1)
        armor.box((.08, .9, .32), loc=(s * .9, 2.72, .98), bevel=.015, seg=1)
        a.part('Lamps', 'Lamp').box((.18, .06, .08), loc=(s * .4, -3.16, .86), bevel=.01, seg=1)
        steel.box((.12, .2, .1), loc=(s * .26, -3.18, .76), bevel=.02, seg=1)             # tow hooks
        a.part('Tail_lights', 'Alloy').box((.12, .06, .1), loc=(s * .66, 3.16, 1.32), bevel=.01, seg=1)
        dark.grille(.34, .26, loc=(s * .58, 3.17, .98), rot=(0, 0, math.pi), slats=3, depth=.05, thickness=.04)
        dark.grille(.5, .55, loc=(s * .32, 2.2, 1.57), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
    armor.box((.46, .06, .56), loc=(0, 3.17, 1.04), bevel=.015, seg=1)                    # rear door
    steel.box((.2, .05, .05), loc=(.12, 3.21, 1.08), bevel=.01, seg=1)
    # Driver hatch and vision blocks on the glacis.
    armor.cyl(.24, .06, loc=(-.36, -1.25, 1.57), seg=14, bevel=.02, bseg=1)
    glass = a.part('Vision_blocks', 'Glass')
    gy, gz, grot = _glacis((-2.7, 1.2), (-1.45, 1.56), .86, .012)
    for dx in (-.14, 0, .14):
        glass.box((.12, .07, .05), loc=(-.36 + dx, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    steel.cyl(.66, .1, loc=(0, -.15, 1.58), seg=20, bevel=.02, bseg=1)                   # turret ring

    t = a.pivot('Turret', (0, -.15, 1.63))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.62, .72), (.62, .72), (.78, .18), (.66, -.46), (.36, -.8), (-.36, -.8), (-.66, -.46), (-.78, .18)]
    turret.prism(outline, .46, loc=(0, 0, .23), axis='Z', bevel=.05, taper=.8)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.44, .26, .32), loc=(0, -.88, .24), bevel=.035)                           # mantlet
    tarm.box((1.0, .34, .3), loc=(0, .82, .21), bevel=.035, taper=(.94, .9))             # bustle
    tsteel = a.part('Turret_steel', 'Steel', t)
    sight = a.part('Sight', 'Glass', t)
    tsteel.box((.26, .26, .22), loc=(-.3, .12, .55), bevel=.035)                        # commander sight
    sight.box((.18, .04, .11), loc=(-.3, -.01, .57), bevel=.01, seg=1)
    tsteel.box((.22, .2, .16), loc=(.34, -.3, .5), bevel=.03)                           # gunner sight
    sight.box((.16, .04, .08), loc=(.34, -.41, .5), bevel=.01, seg=1)
    for s in (-1, 1):
        _smoke(a, tsteel, .5, -.34, .38, s, count=3, gap=.07)
    a.part('Hatch', 'Armor', t).cyl(.2, .05, loc=(.3, .32, .47), seg=12, bevel=.015, bseg=1)
    _antenna(a, t, -.46, .6, .42, 1.1)
    tip = _barrel(a, t, start_y=-.98, length=2.35, radius=.05, height=.25, brake=(.11, .22, .11),
                  sleeve=(.1, .46, .085), seg=10)
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .3, -.74, .32, length=.3, housing=.26)


def _sponson_section(y, zb, zs, zt, wb, ws, wt):
    """Ten-point hull section with sponsons over the tracks: belly between the belts (wb), a flat
    sponson floor at zs out to ws, a short upright edge, then a sloped flank up to the roof."""
    return [(-wb, y, zb), (wb, y, zb), (wb, y, zs), (ws, y, zs), (ws, y, zs + .08), (wt, y, zt), (-wt, y, zt),
            (-ws, y, zs + .08), (-ws, y, zs), (-wb, y, zs)]


def tank_destroyer(a):
    """Low tank destroyer: sloped sponson hull with bolt-on plates, an open-top turret and a very
    long 105 mm gun with a double-baffle muzzle brake."""
    tracks(a, 1.22, 6.2, .8, .28, 7, .45, belt_width=.56, wheel_seg=12, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.46, .96, 1.36, .95, 1.52, 1.16)
    hull.loft([
        _sponson_section(-3.5, .62, .96, 1.1, .9, 1.4, 1.24),
        _sponson_section(-2.1, *body),
        _sponson_section(3.25, *body),
        _sponson_section(3.5, .56, .96, 1.28, .92, 1.48, 1.14),
    ], bevel=.05, seg=2)
    x, z, lean = _flank((1.52, 1.04), (1.16, 1.36), .5, .02)
    for s in (-1, 1):
        for y in (-1.55, -.2, 1.15, 2.5):                                               # bolt-on plates
            armor.box((.06, 1.1, .34), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=.015, seg=1)
        a.part('Lamps', 'Lamp').box((.2, .05, .1), loc=(s * .75, -3.51, .92), bevel=.01, seg=1)
        steel.box((.14, .2, .12), loc=(s * .55, -3.56, .72), bevel=.02, seg=1)             # tow hooks
        steel.cyl(.1, .5, loc=(s * .55, 3.55, .95), rot=FORWARD, seg=10, bevel=.015, bseg=1)  # exhausts
        a.part('Tail_lights', 'Alloy').box((.14, .05, .1), loc=(s * 1.05, 3.5, 1.12), bevel=.01, seg=1)
        armor.cyl(.26, .06, loc=(s * .55, -1.85, 1.37), seg=14, bevel=.02, bseg=1)         # driver hatches
        a.part('Vision_blocks', 'Glass').box((.14, .06, .08), loc=(s * .55, -2.14, 1.39), bevel=.01, seg=1)
    gy, gz, grot = _glacis((-3.5, 1.1), (-2.1, 1.36), .45, .015)
    for x in (-.8, -.4, 0, .4, .8):                                                      # spare track links
        deck.box((.34, .24, .05), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    deck.grille(1.5, .9, loc=(0, 2.4, 1.37), rot=(-R90, 0, 0), slats=7, depth=.08, thickness=.04)
    steel.cyl(1.02, .1, loc=(0, -.3, 1.38), seg=24, bevel=.03)                          # turret ring
    _antenna(a, None, -1.0, 3.0, 1.36, 1.2)

    t = a.pivot('Turret', (0, -.3, 1.43))
    outline = [(-.5, -1.25), (.5, -1.25), (1.02, -.6), (1.08, .8), (.84, 1.08), (-.84, 1.08), (-1.08, .8),
               (-1.02, -.6)]
    a.part('Turret_body', 'Team', t).shell(outline, .72, .07, taper=.9, floor=.08, bevel=.02)
    a.part('Turret_floor', 'Undercarriage', t).prism([(x * .9, y * .9) for x, y in outline], .02, loc=(0, 0, .1),
                                                     axis='Z', bevel=0)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((.72, .4, .5), loc=(0, -1.3, .42), bevel=.04, taper=(.9, .9))              # mantlet
    tarm.box((1.3, .4, .36), loc=(0, 1.16, .36), bevel=.03)                             # rear stowage
    tsteel.box((.32, .8, .32), loc=(0, -.72, .44), bevel=.03)                           # breech
    tarm.box((1.3, .22, .4), loc=(0, .86, .31), bevel=.02, seg=1)                       # ready rack
    for x in (-.5, -.25, 0, .25, .5):
        tsteel.cyl(.05, .04, loc=(x, .74, .38), rot=FORWARD, seg=8, bevel=0)             # shell bases
    for s in (-1, 1):
        a.part('Seats', 'Canvas', t).box((.34, .34, .3), loc=(s * .55, .15, .27), bevel=.05)
    tsteel.box((.2, .26, .2), loc=(-.46, -.95, .8), bevel=.03)                          # gun sight
    a.part('Sight', 'Glass', t).box((.14, .04, .1), loc=(-.46, -1.08, .8), bevel=.01, seg=1)
    tip = _barrel(a, t, start_y=-1.46, length=5.0, radius=.085, height=.44, brake=(.26, .32, .22),
                  sleeve=(.42, .5, .125), seg=12)
    a.part('Muzzle_brake', 'Undercarriage', t).box((.24, .12, .2), loc=(0, tip[1] + .43, .44), bevel=.025)
    a.pivot('Muzzle_main', tip, t)
    _roof_mg(a, t, (.93, .5, .72), length=.8, shield=False)


def heavy_tank(a):
    """Super-heavy tank: eight-wheel running gear under a deck as wide as the tracks, heavy
    skirts, reactive armour and a massive angular turret with a 152 mm gun."""
    # Seven lean 10-sided road wheels: the skirts hide their upper halves.
    tracks(a, 1.32, 7.4, 1.0, .33, 7, .55, belt_width=.66, wheel_seg=10, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.95, .6), (-4.15, 1.2), (4.1, 1.2), (4.1, .6)], 2.0, bevel=.05)       # belly
    front, back = (-4.28, 1.3), (-3.0, 1.68)
    hull.prism([(-4.2, 1.14), front, back, (3.9, 1.68), (4.24, 1.44), (4.24, 1.14)], 3.42, bevel=.07)
    for s in (-1, 1):
        for i in range(4):                                                                # skirt panels
            hull.box((.12, 1.86, .84), loc=(s * 1.8, -2.82 + i * 1.9, .94), bevel=.03, seg=1)
        a.part('Lamps', 'Lamp').box((.24, .05, .1), loc=(s * 1.25, -4.25, 1.22), bevel=.01, seg=1)
        steel.box((.16, .2, .14), loc=(s * .7, -4.08, .82), bevel=.02, seg=1)             # tow hooks
        a.part('Tail_lights', 'Alloy').box((.16, .05, .1), loc=(s * 1.4, 4.25, 1.3), bevel=.01, seg=1)
        deck.grille(1.1, .9, loc=(s * .72, 3.35, 1.69), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        armor.box((.5, .9, .3), loc=(s * 1.38, 3.35, 1.82), bevel=.03, seg=1)             # rear stowage
        armor.box((.5, .8, .3), loc=(s * 1.38, -2.5, 1.82), bevel=.03, seg=1)             # front stowage
    for row, u in enumerate((.3, .74)):                                                   # reactive armour
        gy, gz, grot = _glacis(front, back, u, .035)
        for x in ((-1.2, -.4, .4, 1.2) if row else (-1.3, -.65, 0, .65, 1.3)):
            armor.box((.72 if row else .58, .44, .1), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    armor.cyl(.3, .06, loc=(0, -2.72, 1.69), seg=14, bevel=.02, bseg=1)                  # driver hatch
    gy, gz, grot = _glacis(front, back, .96, .012)
    a.part('Vision_blocks', 'Glass').box((.5, .07, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    steel.cyl(1.25, .12, loc=(0, .45, 1.68), seg=24, bevel=.03)                          # turret ring

    t = a.pivot('Turret', (0, .45, 1.72))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.2, 1.5), (1.2, 1.5), (1.45, .9), (1.45, -.6), (.95, -1.5), (-.95, -1.5), (-1.45, -.6),
               (-1.45, .9)]
    turret.prism(outline, .9, loc=(0, 0, .45), axis='Z', bevel=.07, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):                                                                     # wedge cheeks
        tarm.prism([(s * .3, -1.3), (s * 1.44, -.5), (s * 1.44, -.95), (s * .34, -2.0)], .7, loc=(0, 0, .45),
                   axis='Z', bevel=.04, taper=.9)
        tarm.box((.16, 1.2, .44), loc=(s * 1.4, .55, .42), bevel=.03, seg=1)             # side bins
        _smoke(a, tsteel, 1.16, -.2, .74, s, count=3, gap=.09, r=.05, depth=.16)
    tarm.box((.56, .5, .6), loc=(0, -1.62, .44), bevel=.05, seg=1)                       # mantlet
    tarm.box((2.3, 1.0, .7), loc=(0, 1.9, .42), bevel=.05, seg=1, taper=(.92, .9))      # bustle
    tsteel.cyl(.16, .3, loc=(-.62, .1, 1.0), seg=12, bevel=.02, bseg=1)                 # panoramic sight
    tsteel.box((.3, .3, .2), loc=(-.62, .1, 1.2), bevel=.04)
    a.part('Sight', 'Glass', t).box((.22, .04, .1), loc=(-.62, -.06, 1.21), bevel=.01, seg=1)
    tsteel.box((.36, .34, .24), loc=(.5, -.82, .98), bevel=.04)                         # gunner sight
    a.part('Sight', 'Glass', t).box((.26, .04, .12), loc=(.5, -1.0, 1.0), bevel=.01, seg=1)
    a.part('Hatch', 'Armor', t).cyl(.28, .06, loc=(-.62, .7, .91), seg=14, bevel=.02, bseg=1)
    _antenna(a, t, -1.0, 1.35, .88, 1.4)
    _antenna(a, t, 1.0, 1.35, .88, 1.1)
    tip = _barrel(a, t, start_y=-1.85, length=4.2, radius=.15, height=.44, brake=(.46, .46, .4),
                  sleeve=(.42, .8, .22), seg=14)
    a.part('Muzzle_brake', 'Undercarriage', t).box((.42, .18, .36), loc=(0, tip[1] + .6, .44), bevel=.04)
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .2, -1.8, .3, length=.4, housing=.26)
    _rws(a, t, (.55, .35, .9))


def sam_launcher(a):
    """Tracked surface-to-air missile launcher: two 4-cell missile boxes raised 35 degrees on a
    trainable launcher, and a search radar panel spinning on its own mast beside the cab."""
    tracks(a, 1.18, 5.6, .8, .27, 6, .45, belt_width=.54, wheel_seg=12, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.05, .52), (-3.1, .84), (-2.4, 1.3), (2.85, 1.3), (3.1, 1.08), (3.1, .52)], 2.34, bevel=.06)
    for s in (-1, 1):
        armor.box((.08, 4.9, .42), loc=(s * 1.56, -.05, .78), bevel=.025, taper=(1, .97))  # side skirts
        a.part('Lamps', 'Lamp').box((.2, .05, .1), loc=(s * .75, -3.1, .74), bevel=.01, seg=1)
        steel.box((.14, .18, .12), loc=(s * .45, -3.12, .6), bevel=.02, seg=1)             # tow hooks
        a.part('Tail_lights', 'Alloy').box((.14, .05, .1), loc=(s * .95, 3.11, .98), bevel=.01, seg=1)
        armor.box((.5, .5, .32), loc=(s * .82, 2.72, 1.45), bevel=.03)                    # rear lockers
    deck.grille(.9, .6, loc=(-.45, -.95, 1.31), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
    # Driver cab on the front left.
    armor.box((1.0, 1.1, .46), loc=(-.58, -1.9, 1.5), bevel=.05, taper=(.9, .8))
    a.part('Visor', 'Glass').box((.7, .04, .14), loc=(-.58, -2.39, 1.58), rot=(-.234, 0, 0), bevel=.01, seg=1)
    armor.cyl(.22, .05, loc=(-.58, -1.78, 1.745), seg=12, bevel=.015, bseg=1)             # cab hatch
    # Radar mast on the front right; the panel spins on its own pivot.
    armor.box((.62, .62, .32), loc=(.55, -2.0, 1.44), bevel=.04, taper=(.8, .8))
    steel.cyl(.13, 1.0, loc=(.55, -2.0, 1.95), seg=10, bevel=0)
    steel.cyl(.2, .12, loc=(.55, -2.0, 1.66), seg=10, bevel=.02, bseg=1)                   # mast collar
    r = a.pivot('Radar', (.55, -2.0, 2.45))
    rm = a.part('Radar_mast', 'Steel', r)
    rm.cyl(.15, .16, loc=(0, 0, .08), seg=12, bevel=.02, bseg=1)                         # bearing
    rm.box((.18, .3, .44), loc=(0, .08, .36), bevel=.03)                                  # yoke
    rot = (-.3, 0, 0)
    face = _frame((0, -.08, .66), rot)
    a.part('Radar_panel', 'Team', r).box((1.7, .14, .95), loc=face.to_translation(), rot=rot, bevel=.04)
    a.part('Radar_array', 'Armor', r).box((1.54, .04, .8), loc=face @ Vector((0, -.08, 0)), rot=rot, bevel=.01,
                                          seg=1)
    a.part('Radar_back', 'Armor', r).box((.5, .2, .42), loc=face @ Vector((0, .16, 0)), rot=rot, bevel=.03)
    for z in (-.27, -.09, .09, .27):                                                      # array ribs
        rm.box((1.5, .03, .04), loc=face @ Vector((0, -.105, z)), rot=rot, bevel=0)
    _antenna(a, None, -.95, 2.5, 1.3, 1.3)

    t = a.pivot('Turret', (0, 1.2, 1.3))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.0, .12, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                    # turntable
    tarm.box((1.5, 1.9, .5), loc=(0, .15, .36), bevel=.05, taper=(.9, .92))              # launcher base
    pitch, length, height, width = math.radians(35), 2.6, .86, .86
    hinge = Vector((0, .95, .72))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = hinge - turn @ Vector((0, length / 2, -height / 2))
    for s in (-1, 1):
        centre = mid + Vector((s * .56, 0, 0))
        box = _frame(centre, rot)
        a.part('Missile_box', 'Team', t).box((width, length, height), loc=centre, rot=rot, bevel=.05)
        frame = a.part('Box_frame', 'Armor', t)
        for y in (-length / 2 + .1, length / 2 - .12):
            frame.box((width + .05, .14, height + .05), loc=box @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
        for cx in (-.2, .2):
            for cz in (-.2, .2):
                _tube_mouth(a, t, box @ _frame((cx, -length / 2, cz), FORWARD), .16, protrude=.06, seg=10)
        tarm.box((.14, .46, .5), loc=(s * 1.07, .95, .68), bevel=.02, seg=1)             # hinge cheeks
        tsteel.limb((s * .56, -.55, .5), tuple(box @ Vector((0, -.25, -height / 2 + .02))), .12, .12, bevel=.02)
    spine = _frame(mid, rot)
    tsteel.box((.24, length * .9, .24), loc=spine @ Vector((0, 0, -.22)), rot=rot, bevel=.03)  # cradle
    tsteel.cyl(.11, 2.2, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)             # elevation hinge
    a.pivot('Muzzle_main', tuple(spine @ Vector((0, -length / 2 - .06, 0))), t)


def mortar_carrier(a):
    """Boxy tracked carrier (M113 lineage) with a 120 mm mortar firing through the open roof hatch."""
    tracks(a, 1.08, 4.4, .72, .25, 5, .42, belt_width=.5, wheel_seg=12, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.25, .44), (-2.42, .95), (2.38, .95), (2.38, .44)], 1.7, bevel=.05)        # belly
    nose, brow = (-2.56, 1.22), (-1.95, 1.84)
    hull.prism([(-2.46, .88), nose, brow, (2.45, 1.84), (2.45, .88)], 2.64, bevel=.06)
    gy, gz, grot = _glacis(nose, brow, .42, .02)
    armor.box((2.1, .5, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.015, seg=1)      # trim vane
    for s in (-1, 1):
        gy, gz, grot = _glacis(nose, brow, .82, .03)
        a.part('Lamps', 'Lamp').box((.16, .06, .1), loc=(s * 1.05, gy - .03, gz + .03), bevel=.01, seg=1)
        steel.box((.12, .2, .12), loc=(s * .6, -2.5, .95), bevel=.02, seg=1)              # tow hooks
        a.part('Tail_lights', 'Alloy').box((.14, .06, .1), loc=(s * 1.12, 2.46, 1.62), bevel=.01, seg=1)
        a.part('Jerrycans', 'Hazard').box((.16, .3, .4), loc=(s * 1.41, 2.1, 1.3), bevel=.03)
        steel.box((.1, .12, .08), loc=(s * .8, 2.49, 1.7), bevel=.01, seg=1)             # ramp hinges
    armor.box((1.9, .06, .96), loc=(0, 2.46, 1.3), bevel=.02, seg=1)                     # rear ramp
    # Driver hatch and vision blocks, commander's cupola with the pintle gun.
    armor.cyl(.28, .06, loc=(-.6, -1.55, 1.85), seg=14, bevel=.02, bseg=1)
    for dx in (-.16, 0, .16):
        a.part('Vision_blocks', 'Glass').box((.12, .06, .07), loc=(-.6 + dx, -1.92, 1.87), bevel=.01, seg=1)
    armor.cyl(.34, .22, loc=(.6, -1.05, 1.93), seg=14, bevel=.03)
    glass = a.part('Periscopes', 'Glass')
    for k in range(5):
        ang = -R90 + (k - 2) * .6
        glass.box((.1, .05, .07), loc=(.6 + math.cos(ang) * .34, -1.05 + math.sin(ang) * .34, 1.98),
                  rot=(0, 0, ang + R90), bevel=.01, seg=1)
    _roof_mg(a, None, (.6, -1.05, 2.04), length=.9)
    _antenna(a, None, -1.1, 2.2, 1.84, 1.3)
    # Open mortar hatch: raised coaming around a dark well, both leaves folded up and out.
    hy = .8
    armor.shell(chamfered(1.5, 1.9, .22), .15, .07, loc=(0, hy, 1.82), bevel=.015)
    dark.prism(chamfered(1.38, 1.78, .19), .02, loc=(0, hy, 1.86), axis='Z', bevel=0)
    lean = math.radians(28)
    for s in (-1, 1):
        hull.box((.06, 1.8, .74), loc=(s * (.8 + .37 * math.sin(lean)), hy, 1.97 + .37 * math.cos(lean)),
                 rot=(0, s * lean, 0), bevel=.02, seg=1)
        steel.box((.1, .16, .08), loc=(s * .79, hy - .6, 1.98), bevel=.01, seg=1)          # leaf hinges
        steel.box((.1, .16, .08), loc=(s * .79, hy + .6, 1.98), bevel=.01, seg=1)

    t = a.pivot('Turret', (0, .9, 1.87))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.56, .06, loc=(0, 0, .04), seg=18, bevel=.015, bseg=1)                   # turntable
    tarm.box((.56, .52, .28), loc=(0, .36, .2), bevel=.04)                              # breech mount
    pitch, length = math.radians(55), 1.9
    rot = (R90 - pitch, 0, 0)
    d = Vector((0, -math.cos(pitch), math.sin(pitch)))
    base = Vector((0, .4, .3))
    tube = a.part('Mortar_tube', 'Steel', t)
    tube.cyl(.1, length, loc=base + d * (length / 2), rot=rot, seg=14, bevel=.015, bseg=1)
    tube.cyl(.15, .3, loc=base + d * .12, rot=rot, seg=14, bevel=.04)                    # breech cap
    tube.cyl(.13, .14, loc=base + d * (length - .1), rot=rot, seg=14, bevel=.02)         # blast ring
    collar = base + d * 1.0
    tarm.cyl(.15, .3, loc=collar, rot=rot, seg=12, bevel=.03)                            # recoil collar
    for s in (-1, 1):
        tsteel.limb(tuple(collar + Vector((s * .1, 0, -.06))), (s * .45, -.3, .08), .06, .06, bevel=0)  # bipod
    tsteel.limb((0, -.05, .07), tuple(collar + Vector((0, .05, -.14))), .07, .07, bevel=0)  # elevation screw
    tarm.box((.16, .2, .16), loc=(-.24, -.1, .72), bevel=.02, seg=1)                     # sight
    a.part('Sight', 'Glass', t).box((.1, .04, .08), loc=(-.24, -.21, .74), bevel=.01, seg=1)
    tsteel.limb((-.24, -.1, .64), tuple(collar + Vector((-.1, 0, 0))), .04, .04, bevel=0)
    a.pivot('Muzzle_main', tuple(base + d * length), t)


def rocket_technical(a):
    """Civilian pickup turned rocket artillery: team paint over a tired body, canvas and rust, and
    a twelve-tube rocket launcher on a turntable in the bed."""
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    chassis = a.part('Chassis', 'Undercarriage')
    rust = a.part('Rust', 'Roof')
    chassis.box((1.24, 4.6, .22), loc=(0, .05, .56), bevel=.04)                           # ladder frame
    for sx in (-1, 1):
        for y in (-1.6, 1.5):
            a.part('Tyres', 'Rubber').cyl(.4, .3, loc=(sx * .8, y, .4), rot=ACROSS, seg=16, bevel=.06, bseg=2)
            steel.cyl(.22, .32, loc=(sx * .8, y, .4), rot=ACROSS, seg=10, bevel=.02, bseg=1)
            chassis.tube([(sx * .93, y + .5 * math.cos(u), .4 + .5 * math.sin(u))
                          for u in (i * math.pi / 6 for i in range(7))], .045, seg=6)       # arch flares
    body.prism([(-2.5, .7), (-2.58, 1.0), (-2.48, 1.14), (-1.3, 1.22), (-.74, 1.76), (.28, 1.8), (.36, 1.76),
                (.36, .7)], 1.78, bevel=.06)
    body.shell(chamfered(1.78, 2.1, .05), .46, .06, loc=(0, 1.5, .72), floor=.08, bevel=.02)  # bed
    glass = a.part('Windows', 'Glass')
    glass.box((1.5, .03, .64), loc=(0, -1.03, 1.5), rot=(-.804, 0, 0), bevel=.01, seg=1)
    glass.box((1.2, .02, .3), loc=(0, .38, 1.52), bevel=.005, seg=1)
    for s in (-1, 1):
        glass.box((.02, .76, .36), loc=(s * .91, -.24, 1.5), bevel=.005, seg=1)
        a.part('Lamps', 'Lamp').box((.26, .06, .1), loc=(s * .62, -2.57, .98), bevel=.01, seg=1)
        a.part('Tail_lights', 'Alloy').box((.1, .06, .16), loc=(s * .8, 2.56, 1.02), bevel=.01, seg=1)
        steel.box((.05, .1, .14), loc=(s * .98, -.78, 1.42), bevel=.01, seg=1)            # mirrors
    chassis.grille(1.0, .22, loc=(0, -2.57, .86), slats=3, depth=.05, thickness=.04)
    rust.box((1.84, .16, .16), loc=(0, -2.62, .66), bevel=.03)                            # bumpers
    rust.box((1.84, .14, .14), loc=(0, 2.62, .64), bevel=.03)
    rust.box((.9, .02, .22), loc=(-.25, 2.57, .98), bevel=0)                              # tailgate rust
    steel.tube([(-.82, .56, 1.18), (-.82, .56, 1.98), (.82, .56, 1.98), (.82, .56, 1.18)], .045, seg=8)  # roll bar
    for x in (-.4, 0, .4):
        a.part('Lamps', 'Lamp').box((.16, .08, .08), loc=(x, .5, 2.06), bevel=.01, seg=1)
    a.part('Tarp', 'Canvas').cyl(.13, 1.5, loc=(0, .05, 1.93), rot=ACROSS, seg=10, bevel=.04)
    a.part('Crates', 'Crate').box((.42, .32, .3), loc=(.55, .72, .96), bevel=.03)
    a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(-.55, .66, 1.01), bevel=.03)
    a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(-.55, .85, 1.01), bevel=.03)
    _antenna(a, None, .7, .15, 1.79, 1.4)

    t = a.pivot('Turret', (0, 1.62, .81))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.46, .07, loc=(0, 0, .045), seg=16, bevel=.015, bseg=1)                  # turntable
    tarm.box((.36, .36, .5), loc=(0, 0, .32), bevel=.03)                                # pedestal
    tarm.box((1.16, .3, .12), loc=(0, -.1, .6), bevel=.02, seg=1)                       # yoke bar
    for s in (-1, 1):
        tarm.box((.08, .44, .44), loc=(s * .54, -.1, .82), bevel=.02, seg=1)             # yoke arms
    pitch, length = .22, 1.5
    rot = (-pitch, 0, 0)
    centre = Vector((0, -.1, .92))
    pod = _frame(centre, rot)
    tsteel.cyl(.06, 1.2, loc=centre, rot=ACROSS, seg=8, bevel=0)                        # trunnion
    tubes = a.part('Rocket_tubes', 'Armor', t)
    for row in (-.2, 0, .2):
        for col in (-.3, -.1, .1, .3):
            tubes.cyl(.085, length, loc=pod @ Vector((col, 0, row)), rot=(R90 - pitch, 0, 0), seg=10, bevel=.01,
                      bseg=1)
            _tube_mouth(a, t, pod @ _frame((col, -length / 2, row), FORWARD), .085, protrude=.03, seg=10)
    for y in (-length / 2 + .22, length / 2 - .2):
        a.part('Pod_bands', 'Team', t).box((.88, .1, .68), loc=pod @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
    a.pivot('Muzzle_main', tuple(pod @ Vector((0, -length / 2 - .03, 0))), t)


# name: (builder, Asset options). Vehicles use tight contact AO like 3d_astra's units.
BUILDERS = {
    'scout_jeep': (scout_jeep, dict(ao_distance=.5, grime_height=.45)),
    'light_tank': (light_tank, dict(ao_distance=.55, grime_height=.5)),
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
    'artillery': (artillery, dict(ao_distance=.6, grime_height=.55)),
    'apc': (apc, dict(ao_distance=.6, grime_height=.55)),
    'mlrs': (mlrs, dict(ao_distance=.6, grime_height=.55)),
    'aa_vehicle': (aa_vehicle, dict(ao_distance=.55, grime_height=.5)),
    'flame_tank': (flame_tank, dict(ao_distance=.55, grime_height=.5)),
    'armored_car': (armored_car, dict(ao_distance=.6, grime_height=.55)),
    'tank_destroyer': (tank_destroyer, dict(ao_distance=.6, grime_height=.55)),
    'heavy_tank': (heavy_tank, dict(ao_distance=.65, grime_height=.6)),
    'sam_launcher': (sam_launcher, dict(ao_distance=.6, grime_height=.55)),
    'mortar_carrier': (mortar_carrier, dict(ao_distance=.55, grime_height=.5)),
    'rocket_technical': (rocket_technical, dict(ao_distance=.5, grime_height=.45)),
}
