"""Machine Brigade play-test 6 (DECISIONS 21H): the siege tank redrawn after StarCraft 2's Crucio siege tank.

Conventions as everywhere: metres, +Z up, Blender -Y is the front (Unity +Z). Team parts are recoloured per army at
runtime. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).

  * siege_tank: a low, wide hull (8 m) between four armoured track pods, under a broad turret with two ends. The
    turret is drawn in its sieged heading: the siege cannon (the 240 mm, `Main_cannon*`, `Muzzle_brake*`,
    `Muzzle_main`: the elevating barrel) at its -Y end, telescoped in, and the twin 105 mm (`Deploy_gun`,
    `Muzzle_gun`) at its +Y end. ModelLibrary turns the turret round on the template (`RestTurretYaw`), so the model
    spawns in tank mode, twin guns forward and the stubby siege cannon over the engine deck. A roof M2 on a free
    mount (`Mount_mg`, `Muzzle_mg`). Every part that moves when it sieges is a `Deploy_*` pivot (VehicleView.Deploy):
      - `Deploy_brace_l` / `_r` (front) and `Deploy_leg_l` / `_r` (rear): hydraulic legs hinged on the four pods'
        tops, folded along the hull; sieging they swing out (Unity yaw +-120) and tilt 25 degrees down;
      - `Deploy_braceknee_*` / `Deploy_legknee_*`: the ram housing at each leg's tip, kept upright;
      - `Deploy_braceram_*` / `Deploy_legram_*`: the ram and its foot pad, driven down on to the ground and on to lift
        the hull 0.25 m;
      - `Deploy_spade_l` / `_r`: rear stabiliser spades, swung down;
      - `Deploy_gun`: the twin 105 mm, slid 0.9 m back into the turret;
      - `Deploy_riser`: the turret ring; `Turret` rides on it, unlocking 0.15 m up before the turret swings round.
    Last the siege cannon runs out 1.9 m (`Main_cannon_tube`, `Muzzle_brake*`, `Muzzle_main` slide along it), its
    lock collar seats against the sleeve's mouth, and it is laid (the view's Elevate).
"""
import math

from mb_air import ACROSS, FORWARD, R90
from mb_vehicles import (_antenna, _hatch, _headlight, _periscopes, _pintle, _sponson_section, _stowage_bin,
                         _taillight, _vent, tracks)

# The sieged pose, shared with VehicleView.Deploy (model units).
LEG_HINGE_Z, LEG_LENGTH, PAD_UNDER = 1.2, 1.45, .07
GUN_RETRACT, BARREL_RUN = .9, 1.9


def _leg(a, root, sx, sy):
    """One hydraulic leg on a pod's top: hinged at the pod's outer end (sy: -1 front, 1 rear), folded towards the
    middle of the hull; a ram housing at its tip holds the ram and its foot pad."""
    lr = 'l' if sx > 0 else 'r'
    hinge = (sx * 1.55, sy * 2.6, LEG_HINGE_Z)
    a.part('Leg_lugs', 'Steel').box((.44, .36, .12), loc=(hinge[0], hinge[1], 1.08), bevel=.02, seg=1)
    p = a.pivot(f'Deploy_{root}_{lr}', hinge)
    arm = a.part(f'Deploy_{root}_{lr}_arm', 'Armor', p)
    arm.box((.3, LEG_LENGTH, .26), loc=(0, -sy * LEG_LENGTH / 2, 0), bevel=.03, seg=1, taper=(.85, .96))
    arm.box((.36, .3, .32), loc=(0, -sy * (LEG_LENGTH - .12), 0), bevel=.03, seg=1)                # tip block
    a.part(f'Deploy_{root}_{lr}_stripe', 'Team', p).box((.24, .5, .05), loc=(0, -sy * .82, .13), bevel=.01, seg=1)
    steel = a.part(f'Deploy_{root}_{lr}_steel', 'Steel', p)
    steel.cyl(.17, .42, seg=14, bevel=.02)                                                         # hinge knuckle
    steel.cyl(.05, 1.0, loc=(0, -sy * .66, .18), rot=FORWARD, seg=8, bevel=0)                     # actuator
    steel.box((.1, .1, .1), loc=(0, -sy * .14, .18), bevel=0)
    k = a.pivot(f'Deploy_{root}knee_{lr}', (0, -sy * LEG_LENGTH, 0), p)
    a.part(f'Deploy_{root}knee_{lr}_housing', 'Steel', k).cyl(.15, .64, loc=(0, 0, .3), seg=14, bevel=.02)
    a.part(f'Deploy_{root}knee_{lr}_collar', 'Armor', k).cyl(.19, .1, loc=(0, 0, .6), seg=14, bevel=.02)
    r = a.pivot(f'Deploy_{root}ram_{lr}', (0, 0, 0), k)
    a.part(f'Deploy_{root}ram_{lr}_rod', 'Steel', r).cyl(.08, .85, loc=(0, 0, .44), seg=12, bevel=.01)
    pad = a.part(f'Deploy_{root}ram_{lr}_pad', 'Undercarriage', r)
    pad.cyl(.3, .1, loc=(0, 0, -PAD_UNDER + .05), seg=18, bevel=.02)
    pad.cyl(.14, .08, loc=(0, 0, .06), seg=12, bevel=.01)
    claws = a.part(f'Deploy_{root}ram_{lr}_claws', 'Steel', r)
    for dx, dy in ((.27, 0), (-.27, 0), (0, .27), (0, -.27)):
        claws.box((.1, .1, .1), loc=(dx, dy, -.04), bevel=0, taper=(.5, .5))


def _spade(a, s, name):
    """A rear stabiliser spade, stowed standing up against the tail plate; its pivot is the hinge axis (X)."""
    x = s * .72
    armor = a.part('Spade_lugs', 'Armor')
    for dx in (-.36, .36):
        armor.box((.14, .22, .22), loc=(x + dx, 3.86, .66), bevel=.02, seg=1)
    p = a.pivot(name, (x, 3.93, .66))
    a.part(f'{name}_blade', 'Armor', p).box((.86, .08, 1.1), loc=(0, .09, .6), bevel=.02, seg=1)
    a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .56, rot=ACROSS, seg=10, bevel=0)
    a.part(f'{name}_stripe', 'Team', p).box((.87, .02, .16), loc=(0, .14, .9), bevel=0)
    teeth = a.part(f'{name}_teeth', 'Steel', p)
    for dx in (-.3, -.1, .1, .3):
        teeth.box((.14, .06, .16), loc=(dx, .09, 1.2), bevel=0, taper=(.4, 1))


def _pod(a, s, front):
    """An armoured track pod over one end of a track: a wedge housing with a trim band, an outer plate and a vent."""
    k = -1 if front else 1
    profile = [(k * 3.98, .62), (k * 3.76, 1.1), (k * 1.5, 1.1), (k * 1.38, .92), (k * 1.38, .5), (k * 3.7, .42)]
    if not front:
        profile.reverse()
    a.part('Pods', 'Team').prism(profile, .76, loc=(s * 1.55, 0, 0), axis='X', bevel=.04, seg=1)
    trim = a.part('Pod_trim', 'Armor')
    trim.box((.8, 1.9, .08), loc=(s * 1.55, k * 2.6, 1.12), bevel=.02, seg=1)
    trim.box((.08, 2.0, .3), loc=(s * 1.95, k * 2.5, .72), bevel=.02, seg=1)
    a.part('Pod_vents', 'Undercarriage').grille(.44, .5, loc=(s * 1.55, k * 3.35, 1.17), rot=(-R90, 0, 0), slats=4,
                                                 depth=.04, thickness=.03)


def _siege_cannon(a, t):
    """The 240 mm siege cannon at the turret's -Y end, telescoped in: a heavy cradle on trunnions, an outer sleeve and
    the inner tube with its lock collar and a big muzzle brake (the tube and brake run out BARREL_RUN sieged)."""
    z = .78
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((1.25, 1.7, .6), loc=(0, -1.05, z), bevel=.05, seg=1, taper=(.9, .95))
    for s in (-1, 1):
        cradle.cyl(.2, .16, loc=(s * .66, -.45, z), rot=ACROSS, seg=16, bevel=.02)                  # trunnions
        cradle.limb((s * .32, -1.3, z - .22), (s * .28, -3.1, z - .2), .09, .09, bevel=0, seg=1)     # recuperators
    sleeve = a.part('Main_cannon_sleeve', 'Steel', t)
    sleeve.cyl(.27, 1.8, loc=(0, -2.7, z), rot=FORWARD, seg=20, bevel=.02)
    for y in (-2.2, -3.0):
        sleeve.cyl(.29, .07, loc=(0, y, z), rot=FORWARD, seg=20, bevel=0)                           # bands
    sleeve.cyl(.31, .1, loc=(0, -3.56, z), rot=FORWARD, seg=20, bevel=.02)                          # mouth ring
    a.part('Main_cannon_sleeve_team', 'Team', t).cyl(.28, .3, loc=(0, -2.6, z), rot=FORWARD, seg=20, bevel=0)
    tube = a.part('Main_cannon_tube', 'Steel', t)
    tube.cyl(.19, 3.6, loc=(0, -1.8, z), rot=FORWARD, seg=18, bevel=.01)
    tube.cyl(.24, .14, loc=(0, -1.8, z), rot=FORWARD, seg=18, bevel=.02)                            # lock collar
    tube.cyl(.21, .06, loc=(0, -2.9, z), rot=FORWARD, seg=18, bevel=0)
    brake = a.part('Muzzle_brake', 'Armor', t)
    brake.box((.62, .62, .48), loc=(0, -3.92, z), bevel=.04, seg=1)
    brake.cyl(.25, .08, loc=(0, -4.24, z), rot=FORWARD, seg=18, bevel=.02)
    ports = a.part('Muzzle_brake_ports', 'Undercarriage', t)
    for s in (-1, 1):
        for y in (-3.78, -4.02):
            ports.box((.04, .14, .3), loc=(s * .31, y, z), bevel=0)
    a.pivot('Muzzle_main', (0, -4.3, z), t)


def _twin_guns(a, t):
    """The twin 105 mm at the turret's +Y end, on a mantlet that slides GUN_RETRACT back into the turret sieged; one
    muzzle empty on the right barrel's brake."""
    p = a.pivot('Deploy_gun', (0, 1.6, .42), t)
    a.part('Gun105_mantlet', 'Armor', p).box((1.0, .5, .46), loc=(0, .05, 0), bevel=.04, seg=1, taper=(.9, .9))
    tubes = a.part('Gun105_tubes', 'Steel', p)
    brakes = a.part('Gun105_brakes', 'Undercarriage', p)
    for x in (-.22, .22):
        tubes.cyl(.075, 2.9, loc=(x, 1.55, 0), rot=FORWARD, seg=12, bevel=.01, bseg=1)
        tubes.cyl(.1, 1.0, loc=(x, .8, 0), rot=FORWARD, seg=12, bevel=.015)
        brakes.cyl(.1, .28, loc=(x, 3.06, 0), rot=FORWARD, seg=12, bevel=.01)
    a.part('Gun105_bridge', 'Armor', p).box((.62, .14, .12), loc=(0, 2.2, 0), bevel=.02, seg=1)
    a.pivot('Muzzle_gun', (-.22, 3.22, 0), p)


def siege_tank(a):
    """Siege tank, 8.0 x 4.2 m: a low hull between four track pods, the legs folded on the pods, a broad turret with
    the twin 105 mm at one end and the telescoped siege cannon at the other (see the module notes)."""
    tracks(a, 1.5, 7.3, .8, .3, 7, .44, belt_width=.62, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.36, .95, 1.38, 1.05, 1.18, 1.12)
    hull.loft([_sponson_section(-4.0, .55, .95, 1.05, .9, 1.12, 1.0), _sponson_section(-3.2, *body),
               _sponson_section(3.3, *body), _sponson_section(3.85, .45, .95, 1.32, 1.0, 1.15, 1.08)],
              bevel=.05, seg=2)
    # Glacis add-on plate and the nose.
    slope = math.atan2(1.38 - 1.05, .8)
    armor.box((1.9, .88, .08), loc=(0, -3.6, 1.25), rot=(slope, 0, 0), bevel=.02, seg=1)
    for s in (-1, 1):
        steel.box((.16, .2, .16), loc=(s * .7, -4.05, .8), bevel=.02, seg=1)                          # tow hooks
        _headlight(a, s * .78, -3.98, 1.0)
        _taillight(a, s * .85, 3.88, 1.18)
        for front in (True, False):
            _pod(a, s, front)
    _pintle(a, 0, 3.86, .8, facing=1)
    _periscopes(a, [(dx, -3.18, 1.38, 0) for dx in (-.25, 0, .25)])
    _hatch(a, -.55, -2.7, 1.38, .26)
    # Engine deck: a wide grille, two big exhaust stacks on the tail corners, vents and bins.
    deck.grille(1.6, 1.2, loc=(0, 2.9, 1.39), rot=(-R90, 0, 0), slats=8, depth=.08, thickness=.04)
    for s in (-1, 1):
        steel.cyl(.15, .7, loc=(s * .82, 3.55, 1.6), seg=14, bevel=.02)
        a.part('Exhaust_caps', 'Undercarriage').cyl(.12, .06, loc=(s * .82, 3.55, 1.96), seg=14, bevel=0)
        armor.box((.36, .36, .14), loc=(s * .82, 3.55, 1.28), bevel=.02, seg=1)
        _stowage_bin(a, (s * .78, 1.95, 1.38), (.5, .7, .3))
        _vent(a, s * .5, -2.3, 1.38)
    # The turret ring in the roof.
    steel.cyl(1.05, .1, loc=(0, .1, 1.385), seg=28, bevel=.03)

    for s in (1, -1):
        _leg(a, 'brace', s, -1)
        _leg(a, 'leg', s, 1)
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        _spade(a, s, name)

    r = a.pivot('Deploy_riser', (0, .1, 1.42))
    a.part('Deploy_riser_column', 'Steel', r).cyl(.95, .3, loc=(0, 0, -.12), seg=24, bevel=.02)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.98, .06, loc=(0, 0, -.06), seg=24, bevel=0)

    t = a.pivot('Turret', (0, 0, .04), r)
    outline = [(-1.1, -1.6), (1.1, -1.6), (1.45, -.8), (1.45, 1.2), (1.1, 1.75), (-1.1, 1.75), (-1.45, 1.2),
               (-1.45, -.8)]
    a.part('Turret_body', 'Team', t).prism(outline, .7, loc=(0, 0, .35), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        tarm.box((.55, .9, .5), loc=(s * 1.02, 1.32, .36), rot=(0, 0, s * .5), bevel=.03, seg=1, taper=(.9, .85))
        tarm.box((.3, 1.6, .36), loc=(s * 1.42, .2, .32), bevel=.03, seg=1)                          # side plates
        tsteel.box((.16, .5, .12), loc=(s * 1.2, -.9, .74), bevel=.02, seg=1)                          # lifting eyes
    tsteel.box((.24, .28, .24), loc=(-.95, .95, .82), bevel=.03)                                       # sight
    a.part('Sight', 'Glass', t).box((.18, .04, .1), loc=(-.95, 1.1, .84), bevel=.01, seg=1)
    _hatch(a, .7, .45, .7, .3, parent=t)
    _antenna(a, t, -1.05, -1.1, .7, 1.4)
    tarm.box((1.2, .5, .1), loc=(0, .1, .74), bevel=.02, seg=1)                                        # roof plate

    _siege_cannon(a, t)
    _twin_guns(a, t)

    # Roof M2 on a free mount.
    m = a.pivot('Mount_mg', (.95, -.35, .72), t)
    mg = a.part('MG_mount', 'Steel', m)
    mg.cyl(.1, .16, loc=(0, 0, .08), seg=10, bevel=.01)
    mg.box((.14, .5, .14), loc=(0, -.2, .25), bevel=.02, seg=1)
    mg.cyl(.03, .7, loc=(0, -.75, .25), rot=FORWARD, seg=8, bevel=0)
    a.part('MG_shield', 'Armor', m).box((.5, .05, .32), loc=(0, -.42, .32), bevel=.01, seg=1)
    a.pivot('Muzzle_mg', (0, -1.12, .25), m)


BUILDERS = {
    'siege_tank': (siege_tank, dict(ao_distance=.7, grime_height=.6)),
}
