"""Machine Brigade play-test 5 (DECISIONS 20W): the siege tank redrawn for its two modes (StarCraft 2's siege tank).

Conventions as everywhere: metres, +Z up, Blender -Y is the front (Unity +Z). Team parts are recoloured per army at
runtime. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).

  * siege_tank: a heavy tracked hull (8 m) under a wide turret with two guns. Tank mode: the L7 105 mm on the turret's
    right cheek (`Deploy_gun`, `Muzzle_gun`) fires; the 2B8 240 mm mortar lies level along the roof in its cradle
    (`Main_cannon*`, `Muzzle_main`: the turret's elevating barrel, laid by the view). A roof M2 on a free mount
    (`Mount_mg`, `Muzzle_mg`). Every part that moves when it sieges is a `Deploy_*` pivot (VehicleView.Deploy):
      - `Deploy_brace_l` / `Deploy_brace_r`: hydraulic outriggers hinged on the sponsons behind the front idlers,
        stowed standing up beside the turret; sieging they fold out and down on to the ground (Unity z +140 / -140).
      - `Deploy_spade_l` / `Deploy_spade_r`: rear earth spades, stowed up, swung back and down (Unity x -125).
      - `Deploy_gun`: the 105 mm in its sleeve, slid 0.9 m back into the turret sieged.
      - `Deploy_riser`: the turret's column; `Turret` rides on it and rises 0.45 m sieged.
    Last the mortar swings up to 45-72 degrees on its trunnion at the back of the cradle (the view's Elevate).
"""
import math

from mb_air import ACROSS, FORWARD, R90
from mb_vehicles import (_antenna, _barrel, _glacis, _hatch, _headlight, _periscopes, _pintle, _skirt, _smoke,
                         _sponson_section, _stowage_bin, _taillight, _vent, tracks)

# The sieged pose, shared with VehicleView.Deploy (degrees; model units).
BRACE_FOLD, GUN_RETRACT, LIFT = 140, .9, .45


def _brace(a, s, name):
    """One outrigger, hinged on the sponson edge at (s * 1.84, -2.2, 1.18): a tapered box leg with a ram along it and
    a round foot pad at its end, stowed standing 1.6 m up beside the turret."""
    steel = a.part('Brace_lugs', 'Steel')
    for y in (-2.45, -1.95):
        steel.box((.2, .18, .2), loc=(s * 1.8, y, 1.16), bevel=.02, seg=1)
    p = a.pivot(name, (s * 1.84, -2.2, 1.18))
    a.part(f'{name}_leg', 'Armor', p).box((.22, .34, 1.5), loc=(s * .04, 0, .78), bevel=.03, seg=1, taper=(.8, .85))
    a.part(f'{name}_ram', 'Steel', p).cyl(.05, 1.25, loc=(s * -.1, .12, .72), seg=10, bevel=0)
    a.part(f'{name}_hinge', 'Steel', p).cyl(.09, .62, rot=FORWARD, seg=12, bevel=0)
    # The foot pad lies flat on the ground once the leg has folded out (tilted back by the fold on the move).
    pad = a.part(f'{name}_pad', 'Undercarriage', p)
    pad.cyl(.26, .08, loc=(s * .04, 0, 1.6), rot=(0, -s * math.radians(BRACE_FOLD), 0), seg=16, bevel=.02)
    pad.box((.12, .12, .16), loc=(s * .04, 0, 1.5), bevel=.02, seg=1)
    stripe = a.part(f'{name}_stripe', 'Team', p)
    stripe.box((.23, .35, .18), loc=(s * .04, 0, 1.2), bevel=.01, seg=1)


def _spade(a, s, name):
    """A rear earth spade, stowed standing up behind the tail plate; its pivot is the hinge axis (X)."""
    x = s * .85
    armor = a.part('Spade_lugs', 'Armor')
    for dx in (-.4, .4):
        armor.box((.16, .2, .22), loc=(x + dx, 3.72, .74), bevel=.02, seg=1)
    p = a.pivot(name, (x, 3.78, .74))
    a.part(f'{name}_blade', 'Armor', p).box((.95, .08, 1.2), loc=(0, .1, .64), bevel=.02, seg=1)
    a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .6, rot=ACROSS, seg=10, bevel=0)
    ribs = a.part(f'{name}_ribs', 'Armor', p)
    for dx in (-.3, .3):
        ribs.box((.06, .1, .95), loc=(dx, .17, .58), bevel=0)
    teeth = a.part(f'{name}_teeth', 'Steel', p)
    for dx in (-.35, -.12, .12, .35):
        teeth.box((.14, .06, .16), loc=(dx, .1, 1.29), bevel=0, taper=(.4, 1))


def _tank_gun(a, t):
    """The L7 105 mm on the turret's right cheek, in a sleeve it slides back into when the tank sieges."""
    p = a.pivot('Deploy_gun', (-.78, -1.45, .42), t)
    steel = a.part('Gun105_tube', 'Steel', p)
    steel.cyl(.07, 3.2, loc=(0, -1.6, 0), rot=FORWARD, seg=12, bevel=.01, bseg=1)
    steel.cyl(.1, .9, loc=(0, -1.4, 0), rot=FORWARD, seg=12, bevel=.015)       # thermal sleeve
    for y in (-.7, -2.1, -2.7):
        steel.cyl(.082, .05, loc=(0, y, 0), rot=FORWARD, seg=12, bevel=0)      # sleeve bands
    a.part('Gun105_brake', 'Undercarriage', p).cyl(.1, .24, loc=(0, -3.28, 0), rot=FORWARD, seg=12, bevel=.01)
    a.part('Gun105_mantlet', 'Armor', p).box((.46, .5, .42), loc=(0, .05, 0), bevel=.03, seg=1, taper=(.9, .9))
    a.pivot('Muzzle_gun', (0, -3.42, 0), p)


def siege_tank(a):
    """Siege tank, 8.0 x 3.5 m: tracked hull, braces and spades stowed, a wide turret carrying the 240 mm mortar on its
    roof and the 105 mm on its right cheek (see the module notes for the sieged pose)."""
    tracks(a, 1.4, 7.1, .95, .31, 7, .5, belt_width=.62, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.5, 1.1, 1.72, 1.02, 1.8, 1.42)
    hull.loft([_sponson_section(-3.85, .64, 1.1, 1.16, 1.0, 1.74, 1.22), _sponson_section(-2.7, *body),
               _sponson_section(3.4, *body), _sponson_section(3.66, .62, 1.1, 1.64, .98, 1.76, 1.36)], bevel=.05, seg=2)
    for s in (-1, 1):
        _skirt(a, s, 1.83, -2.95, 3.2, .62, 1.08, 6)
        _taillight(a, s * 1.5, 3.67, 1.28)
        _headlight(a, s * 1.25, -3.3, 1.3)
        steel.cyl(.1, .34, loc=(s * 1.0, 3.72, 1.38), rot=FORWARD, seg=10, bevel=.015, bseg=1)   # exhausts
        _stowage_bin(a, (s * 1.35, 2.6, 1.9), (.55, 1.2, .34))
    # Glacis: a thick add-on plate and a dozer-less nose with tow hooks.
    gy, gz, grot = _glacis((-3.85, 1.16), (-2.7, 1.72), .5, .02)
    armor.box((2.5, 1.05, .09), loc=(0, gy, gz + .04), rot=(grot, 0, 0), bevel=.02, seg=1)
    for s in (-1, 1):
        steel.box((.16, .2, .16), loc=(s * .9, -3.9, .92), bevel=.02, seg=1)
    _pintle(a, 0, 3.66, .95, facing=1)
    _periscopes(a, [(dx, -2.72, 1.72, 0) for dx in (-.25, 0, .25)])
    _hatch(a, .7, -2.35, 1.72, .26)
    deck.grille(1.7, 1.1, loc=(0, 2.7, 1.73), rot=(-R90, 0, 0), slats=8, depth=.08, thickness=.04)
    for x in (-.55, .55):
        _vent(a, x, 1.65, 1.72)
    # The column's well in the roof.
    steel.cyl(.95, .1, loc=(0, -.2, 1.715), seg=28, bevel=.03)
    armor.cyl(.82, .06, loc=(0, -.2, 1.78), seg=28, bevel=.02)

    for s, name in ((1, 'Deploy_brace_l'), (-1, 'Deploy_brace_r')):
        _brace(a, s, name)
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        _spade(a, s, name)

    r = a.pivot('Deploy_riser', (0, -.2, 1.74))
    a.part('Deploy_riser_column', 'Steel', r).cyl(.75, .6, loc=(0, 0, -.28), seg=24, bevel=.02)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.78, .07, loc=(0, 0, -.16), seg=24, bevel=0)

    t = a.pivot('Turret', (0, 0, .04), r)
    outline = [(-1.0, -1.6), (1.0, -1.6), (1.45, -1.0), (1.5, 1.1), (1.2, 1.7), (-1.2, 1.7), (-1.5, 1.1),
               (-1.45, -1.0)]
    a.part('Turret_body', 'Team', t).prism(outline, .7, loc=(0, 0, .35), axis='Z', bevel=.05, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):                                                                     # cheek blocks
        tarm.box((.5, .9, .46), loc=(s * 1.1, -1.05, .34), rot=(0, 0, -s * .5), bevel=.03, seg=1, taper=(.9, .85))
    tarm.box((2.3, .45, .4), loc=(0, 1.72, .34), bevel=.03, seg=1)                          # bustle rack
    tsteel.box((.22, .26, .22), loc=(1.0, -.9, .82), bevel=.03)                             # commander's sight
    a.part('Sight', 'Glass', t).box((.16, .04, .1), loc=(1.0, -1.04, .84), bevel=.01, seg=1)
    _hatch(a, .75, .5, .72, .3, parent=t)
    for s in (-1, 1):
        _smoke(a, tsteel, 1.3, -.6, .72, s, count=3, gap=.08, r=.045, depth=.16)
    _antenna(a, t, -1.1, 1.3, .72, 1.3)

    # The 240 mm mortar in its cradle on the roof: the cradle's back (the trunnion) over the turret's rear.
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((.9, 1.5, .42), loc=(0, .55, .95), bevel=.04, seg=1, taper=(.9, .95))
    cradle.box((1.1, .5, .5), loc=(0, 1.2, .92), bevel=.04, seg=1)                            # breech and trunnions
    for s in (-1, 1):
        cradle.cyl(.16, .14, loc=(s * .6, 1.2, .9), rot=ACROSS, seg=14, bevel=.02)
        cradle.limb((s * .35, .9, .74), (s * .3, -.4, 1.02), .09, .09, bevel=0, seg=1)       # recuperators
    tip = _barrel(a, t, start_y=.2, length=3.3, radius=.16, height=1.05, brake=(.4, .36, .4),
                  sleeve=(.3, 1.3, .24), seg=18, style='collar', bands=(.15, .55, .8))
    a.pivot('Muzzle_main', tip, t)
    # Travel lock on the glacis side of the turret front, holding the tube level on the move.
    tsteel.box((.34, .16, .3), loc=(0, -1.62, .82), bevel=.02, seg=1)

    _tank_gun(a, t)

    # Roof M2 on a free mount, left rear.
    m = a.pivot('Mount_mg', (.95, .95, .74), t)
    mg = a.part('MG_mount', 'Steel', m)
    mg.cyl(.1, .16, loc=(0, 0, .08), seg=10, bevel=.01)
    mg.box((.14, .5, .14), loc=(0, -.2, .25), bevel=.02, seg=1)
    mg.cyl(.03, .7, loc=(0, -.75, .25), rot=FORWARD, seg=8, bevel=0)
    a.part('MG_shield', 'Armor', m).box((.5, .05, .32), loc=(0, -.42, .32), bevel=.01, seg=1)
    a.pivot('Muzzle_mg', (0, -1.12, .25), m)


BUILDERS = {
    'siege_tank': (siege_tank, dict(ao_distance=.7, grime_height=.6)),
}
