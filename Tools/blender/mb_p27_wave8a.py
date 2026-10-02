"""Prompt 27 wave 8, lane A (DECISIONS "27 wave 8a1 ..."): the remaining munitions, props and unlisted units, merged last
in build_assets.all_builders() so these builders win. Plan: Docs/models/WAVE8_PLAN.md.

Pass 8a2 (second half: heat_round ... tos_rocket, same method; see NAMES2). Pass 8a1 (first half of the generated "not found by the static scan" row; aim120 and aim9 keep their old files: their
COLOR_0 is already at the ceiling and any added part lowers the mean): apfsds, atgm_ataka, atgm_kornet,
atgm_tow, bomb_fab, bomb_mk84, buk, debris_concrete/leaves/metal/plaster/roof/wood, flak_round, gbu12, gbu39, gmlrs, grad,
grad_cluster, griffin.

Method: the current builders (mb_munitions, mb_props) unchanged in silhouette and nodes, plus a few small real-world details
(hanger lugs, guide studs, arming vanes) and a lighter ambient-occlusion bake (`ao_strength`) so the round
reads brighter at 40 px. Names of existing parts are reused, so no runtime node changes.
"""
import math

from mathutils import Euler, Matrix, Vector

import mb_air
import mb_detail as hd
import mb_kit27 as kit27
import mb_parts27 as parts
import mb_munitions as mu
import mb_new_trucks
import mb_air3
import mb_new_tracked
import mb_round6
import mb_p25_models2 as m2
import mb_orbital
import mb_pt5_models
import mb_props as pr
import mb_support
import mb_vehicles
import mb_vehicles3
from frontier_kit import chamfered
from mb_artillery import PITCH, _along, _box_section, _skirt_panels
from mb_p27_wave3 import _hatch
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _basket, _cable, _coax, _face_box, _face_frame,
                         _flank, _frame, _glacis, _grille_frame, _headlight, _jerrycans, _periscopes, _rail, _roll,
                         _roof_mg, _rws, _shackle, _shovel, _exhaust, _pick, _skirt, _sponson_section, _slats, _smoke, _eyes, _vent, _hull_section, _stowage_bin, _taillight, _track_links, _tube_mouth, _wheel)
from mb_new_tracked import _bucket, _rws_mg
from mb_air import BACKWARD, _bubble, _exhaust_duct, _hoop, _octagon, _pylon, _rocket_pod, _sec, _skin_z
from mb_air3 import ICBM_LENGTH, _icbm
from mb_p27_wave1c import _rotor_head_as
from mb_round6 import flip_spinner, pivot
from mb_p25_models import C130_ENGINES, C130_WING, RAMP
from mb_pt5_models import TAU, _along as _seg
from mb_support import _beacon, _plane, _ram, _rod, _rws_turret, _stripes
from mb_vehicles2 import _axis
from mb_vehicles3 import _heavy_mg

LEN = {'hellfire': 1.4, 'hellfire_longbow': 1.4, 'igla': 1.3, 'stinger': 1.3, 'r60': 1.6, 'maverick': 2.0, 'kh29l': 1.95,
       'mam_l': 1.0, 'patriot': 3.4, 'jdam': 2.7, 'hydra': 1.0, 's8': 1.2, 'tos_rocket': 2.4, 'shahed': 2.6,
       'shorad_dart': 2.2, 'lancet': 1.4, 'aim120': 2.6, 'aim9': 2.2, 'atgm_ataka': 1.5, 'atgm_kornet': 1.3, 'atgm_tow': 1.3, 'bomb_fab': 1.8,
       'bomb_mk84': 2.7, 'buk': 3.6, 'gbu12': 2.2, 'gmlrs': 2.8, 'grad': 2.2, 'grad_cluster': 2.2, 'griffin': 1.0}
RADIUS = {'hellfire': .077, 'hellfire_longbow': .077, 'igla': .037, 'stinger': .037, 'r60': .053, 'maverick': .1225,
          'kh29l': .11, 'mam_l': .085, 'patriot': .12, 'jdam': .27, 'hydra': .04, 's8': .038, 'tos_rocket': .074,
          'shahed': .11, 'shorad_dart': .066, 'lancet': .05, 'aim120': .07, 'aim9': .055, 'atgm_ataka': .058, 'atgm_kornet': .08, 'atgm_tow': .066, 'bomb_fab': .15,
          'bomb_mk84': .27, 'buk': .13, 'gbu12': .11, 'gmlrs': .081, 'grad': .052, 'grad_cluster': .052, 'griffin': .064}


def _lugs(name, ts, size=(.04, .07, .04)):
    def add(m, r):
        for t in ts:
            m.box('Lugs', mu.LIGHT_GREY, size, m.at(r + .008, t))
    return add


def _studs(ts):
    """Guide studs: small steel pins on the underside (they ride the launch rail)."""
    def add(m, r):
        for t in ts:
            m.box('Studs', mu.LIGHT_GREY, (.02, .04, .03), m.at(r + .004, t, 3.14159))
    return add


def _vane(m, r):
    """Arming vane: a short two-blade propeller on the fuze tip."""
    m.box('Arming_vane', mu.STEEL, (1.4 * r, .012, .03), m.at(0, .04))


DETAIL = {
    'atgm_ataka': _studs((.55, 1.0)),
    'atgm_kornet': _studs((.55, 1.0)),
    'atgm_tow': _studs((.60, 1.0)),
    'griffin': _studs((.40, .72)),
    'gmlrs': _studs((1.0, 1.9)),
    'grad': _studs((.9,)),
    'grad_cluster': _studs((.9,)),
    'buk': _lugs('buk', (1.6, 2.7), (.06, .12, .06)),
    'gbu12': _lugs('gbu12', (.90, 1.30), (.04, .07, .04)),
    'bomb_fab': _vane,
    'bomb_mk84': _vane,
    # pass 8a2
    'hellfire': _studs((.50, .95)),
    'hellfire_longbow': _studs((.50, .95)),
    'igla': _studs((.55,)),
    'stinger': _studs((.55,)),
    'r60': _studs((.70, 1.05)),
    'maverick': _lugs('maverick', (.65, 1.20), (.05, .09, .05)),
    'kh29l': _lugs('kh29l', (.70, 1.30), (.05, .09, .05)),
    'mam_l': _lugs('mam_l', (.45,), (.04, .07, .04)),
    'patriot': _studs((1.2, 2.6)),
    'jdam': _vane,
    'hydra': _studs((.5,)),
    's8': _studs((.55,)),
    'tos_rocket': _studs((1.0, 1.9)),
    'shorad_dart': _studs((.9,)),
}


def _wrap(name, fn):
    detail = DETAIL.get(name)

    def build(a):
        fn(a)
        if detail:
            m = mu.Round(a, LEN[name])
            detail(m, RADIUS[name])
    return build


LOW_AO = ('buk', 'gmlrs', 'maverick', 'kh29l', 'patriot', 'jdam')  # near the top of the tone range: the lugs' own vertices need a lighter bake
NAMES2 = ('heat_round', 'hellfire', 'hellfire_longbow', 'hydra', 'igla', 'jassm', 'jdam', 'kh29l', 'lancet', 'mam_l',
          'maverick', 'mortar_bomb', 'patriot', 'r60', 'rail_slug', 'rocket_107', 's8', 'shahed', 'shell_155',
          'shorad_dart', 'stinger', 'tos_rocket')
NAMES = NAMES2 + ('apfsds', 'atgm_ataka', 'atgm_kornet', 'atgm_tow', 'bomb_fab', 'bomb_mk84', 'buk', 'flak_round',
         'gbu12', 'gbu39', 'gmlrs', 'grad', 'grad_cluster', 'griffin')
BUILDERS = {n: (_wrap(n, mu.BUILDERS[n][0]), dict(mu.BUILDERS[n][1], ao_strength=0 if n in LOW_AO else .5)) for n in NAMES}


def _debris(kind):
    fn, options = pr.BUILDERS[f'debris_{kind}']

    return fn, dict(options, ao_strength=.8)


BUILDERS.update({f'debris_{k}': _debris(k) for k in ('concrete', 'leaves', 'metal', 'plaster', 'roof', 'wood')})


# ----------------------------------------------------------------------------- pass 8a3: mb_air / mb_vehicles3 / mb_support rounds and drops
# (aps_tank, atgm_carrier, howitzer are units: see the V2 section below.) Same method as 8a1/8a2: the old builder,
# a few small real details on the existing names and a lighter AO bake.
def _studs3(a, ys, z, size=(.02, .04, .03)):
    """Launch-rail studs on the belly of a round that lies along Y."""
    for y in ys:
        a.part('Studs', mu.LIGHT_GREY).box(size, loc=(0, y, z), bevel=0)


def _missile3(a):
    mb_air.missile(a)
    _studs3(a, (-.12, .2), -.055)


def _rocket3(a):
    mb_air.rocket(a)
    _studs3(a, (.0,), -.04, (.015, .035, .02))


def _bomb3(a):
    mb_air.bomb(a)
    a.part('Arming_vane', mu.STEEL).box((.1, .012, .03), loc=(0, -.79, 0), bevel=0)


def _cruise3(a):
    mb_air.cruise_missile(a)
    _studs3(a, (-.5, .35), -.265, (.05, .1, .04))


def _ballistic3(a):
    mb_vehicles3.ballistic_missile(a)
    for y in (-1.0, .9):
        a.part('Lugs', mu.LIGHT_GREY).box((.12, .24, .08), loc=(0, y, .455), bevel=0)


def _heavy_rocket3(a):
    mb_vehicles3.heavy_rocket(a)
    _studs3(a, (-.5, .6), -.152, (.04, .08, .05))


def _mine3(a):
    mb_support.mine(a)
    a.part('Mine_ring', mu.STEEL).torus(.2, .012, loc=(0, 0, .1), seg=12, ring=4)
    a.part('Mine_handle', mu.STEEL).box((.1, .02, .03), loc=(.255, 0, .06), bevel=0)


ROUNDS3 = {
    'missile': (_missile3, .45), 'rocket': (_rocket3, .6), 'bomb': (_bomb3, .5), 'cruise_missile': (_cruise3, .5),
    'ballistic_missile': (_ballistic3, .5), 'heavy_rocket': (_heavy_rocket3, .5), 'mine': (_mine3, .6),
    'supply_crate': (mb_support.supply_crate, .6), 'repair_crate': (mb_support.repair_crate, .6),
}
_OLD3 = {**mb_air.BUILDERS, **mb_vehicles3.BUILDERS, **mb_support.BUILDERS}
BUILDERS.update({n: (fn, dict(_OLD3[n][1], ao_strength=ao)) for n, (fn, ao) in ROUNDS3.items()})


# ----------------------------------------------------------------------------- pass 8a3 units (V2 kit, wave 3 rules)
def howitzer(a):
    """Tracked 155 mm self-propelled howitzer (PzH 2000 / M109A7 lineage): a long, low front hull with a
    shallow glacis, the driver's hatch and engine grilles at the front and an A-frame travel lock folded on
    the glacis; seven road wheels behind bolted skirts. A large slab-sided turret stands well back and
    overhangs the tail, with a rear ammunition door, side bins, add-on roof armour, smoke dischargers, a
    panoramic sight and the commander's cupola with its machine gun. The very long L52 gun has a big
    mantlet, a fume extractor, thermal-sleeve clamps and a pepperpot muzzle brake 3.3 m past the bow."""
    parts.track_unit(a, 1.3, 7.0, .975, .32, 7, .6, sprocket_end=-1, cleat_pitch=.3, wheel_seg=7, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    kit27.extrude(hull, [(-3.45, .56), (-3.78, 1.12), (3.72, 1.12), (3.72, .56)], 1.9, axis='X', chamfer=0)       # belly
    nose, brow = (-3.9, 1.3), (-2.7, 1.7)
    kit27.extrude(hull, [(-3.8, 1.065), nose, brow, (3.66, 1.7), (3.8, 1.6), (3.8, 1.065)], 3.28, axis='X', chamfer=.06, corner=.04)
    gy, gz, grot = _glacis(nose, brow, .52, 0)
    for s in (-1, 1):
        _skirt_panels(a, s, 1.72, -3.3, 3.45, .66, 1.4, 4)
        a.part('Skirt_flaps', 'Rubber').box((.04, .42, .56), loc=(s * 1.72, -3.56, 1.1), rot=(.3, 0, 0), bevel=0)
        hy, hz, hrot = _glacis(nose, brow, .12, .03)
        armor.box((.36, .2, .16), loc=(s * 1.28, hy, hz), rot=(hrot, 0, 0), bevel=.02, seg=1)   # lamp housings
        ly, lz, _ = _glacis(nose, brow, .045, .045)
        a.part('Lamps', 'Lamp').box((.24, .03, .09), loc=(s * 1.28, ly, lz), rot=(hrot, 0, 0), bevel=0)
        steel.box((.16, .2, .14), loc=(s * .75, -3.72, .95), bevel=.02, seg=1)                 # tow hooks
        steel.box((.16, .2, .14), loc=(s * .75, 3.86, .95), bevel=.02, seg=1)
        _taillight(a, s * 1.35, 3.8, 1.42)
        steel.box((.08, .1, .16), loc=(-.55, 3.83, .95 + (s + 1) * .21), bevel=.01, seg=1)     # door hinges
        _track_links(a, _frame((s * .95, gy, gz), (grot, 0, 0)), 2, width=.44)
    # Folded travel lock on the glacis: an A-frame lying flat with the barrel cradle at its head.
    lock = a.part('Travel_lock', 'Steel')
    y0, z0, rot0 = _glacis(nose, brow, .16, .06)
    y1, z1, _ = _glacis(nose, brow, .86, .06)
    for s in (-1, 1):
        lock.limb((s * .42, y0, z0), (s * .14, y1, z1), .08, .07, bevel=0)
        hy, hz, _ = _glacis(nose, brow, .16, .04)
        armor.box((.14, .22, .16), loc=(s * .56, hy, hz), rot=(rot0, 0, 0), bevel=0)             # hinge lugs
    lock.box((1.0, .1, .09), loc=(0, y0, z0), rot=(rot0, 0, 0), bevel=0)                        # hinge bar
    y2, z2, _ = _glacis(nose, brow, .9, .1)
    lock.box((.44, .16, .16), loc=(0, y2, z2), rot=(rot0, 0, 0), bevel=.02, seg=1)              # cradle
    for s in (-1, 1):
        y3, z3, _ = _glacis(nose, brow, .9, .22)
        lock.box((.06, .14, .16), loc=(s * .17, y3, z3), rot=(rot0, 0, 0), bevel=0)             # jaws
    # Front deck: engine grilles on the right, the driver's hatch and vision blocks on the left, the
    # exhaust on the right flank.
    for y, d in ((-2.2, .7), (-1.35, .6)):
        deck.grille(1.1, d, loc=(.75, y, 1.71), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
        _grille_frame(a, .75, y, 1.69, 1.1, d, t=.04)
    _hatch(a, -.8, -2.1, 1.69, .28)
    _periscopes(a, [(-.8 + dx, -2.46, 1.69, 0) for dx in (-.17, 0, .17)])
    armor.box((.1, .9, .34), loc=(1.66, -1.6, 1.38), bevel=.015, seg=1)                          # exhaust cowl
    deck.grille(.8, .24, loc=(1.72, -1.6, 1.38), rot=(0, 0, R90), slats=3, depth=.05, thickness=.035)
    _cable(a, [(-1.5, -2.5, 1.725), (-1.5, -.9, 1.725)])
    _shovel(a, (1.45, -2.45, 1.715), yaw=0, length=1.0)
    # Rear: hull door with hinges and a handle.
    armor.box((.9, .06, .66), loc=(-.1, 3.82, 1.2), bevel=.02, seg=1)
    steel.box((.26, .05, .05), loc=(.18, 3.86, 1.22), bevel=0)
    steel.cyl(1.3, .1, loc=(0, 1.5, 1.72), seg=24, bevel=.02, bseg=1)                           # turret ring

    t = a.pivot('Turret', (0, 1.5, 1.72))
    H = 1.16
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.02, -2.2), (1.02, -2.2), (1.5, -1.62), (1.52, 2.5), (1.34, 2.7), (-1.34, 2.7), (-1.52, 2.5),
               (-1.5, -1.62)]
    kit27.sharp_loft(turret, [[(x, y, 0) for x, y in outline], [(x * .95, y * .95, H) for x, y in outline]], chamfer=.05)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    # Add-on roof armour: a grid of bolted plates (the cupola takes the front-right one).
    for x in (-.78, 0, .78):
        for y in (-1.2, -.35, .5):
            if x > 0 and y < 0:
                continue
            turret.box((.72, .78, .06), loc=(x, y, H + .01), bevel=.015, seg=1)
    # Side bins on the rear half and side doors ahead of them; smoke dischargers at the front corners;
    # rails along the roof edges.
    for s in (-1, 1):
        side = ((1.5, -1.62), (1.52, 2.5)) if s > 0 else ((-1.52, 2.5), (-1.5, -1.62))

        def at_side(y, z):
            u = (y + 1.62) / 4.12 if s > 0 else (2.5 - y) / 4.12
            return _face_frame(*side, H, .95, u=u, v=z / H)
        _face_box(a, 'Turret_bins', 'Armor', at_side(1.55, .28), (1.7, .52, .26), parent=t)
        _face_box(a, 'Turret_bins', 'Armor', at_side(1.55, .82), (1.74, .05, .29), parent=t, bevel=0, sink=.02)
        for y in (1.0, 2.1):
            _face_box(a, 'Turret_steel', 'Steel', at_side(y, .7), (.05, .1, .31), parent=t, bevel=0)
        _face_box(a, 'Turret_armor', 'Armor', at_side(-.3, .5), (.9, .76, .05), parent=t)       # side door
        _face_box(a, 'Turret_steel', 'Steel', at_side(-.05, .55), (.2, .05, .09), parent=t, bevel=0, sink=-.035)
        tarm.box((.36, .5, .16), loc=(s * 1.26, -1.62, H - .2), bevel=.02, seg=1)             # discharger base
        for k in range(4):                                                                     # smoke dischargers
            tsteel.cyl(.055, .2, loc=(s * (1.16 + k * .07), -1.8 + k * .12, H - .08), rot=(.6, 0, s * .5), seg=8,
                       bevel=0)
        _rail(a, [(s * 1.28, .2, H - .02), (s * 1.28, .2, H + .06), (s * 1.3, 2.1, H + .06), (s * 1.3, 2.1, H - .02)],
              parent=t)
    # Rear: the ammunition door (hinged, with a handle), jerrycans and lights either side of it.
    ry, rz, rrot = _glacis((2.7 * .95, H), (2.7, 0), .52, .025)
    tarm.box((1.16, .76, .06), loc=(0, ry, rz), rot=(rrot, 0, 0), bevel=.02, seg=1)
    for z in (.3, .82):
        tsteel.box((.1, .08, .14), loc=(-.62, 2.69 - .05 * z, z), bevel=0)                      # hinges
    hy, hz, _ = _glacis((2.7 * .95, H), (2.7, 0), .5, .065)
    tsteel.box((.3, .05, .05), loc=(.3, hy, hz), rot=(rrot, 0, 0), bevel=0)                     # handle
    for s in (-1, 1):
        cy, cz, _ = _glacis((2.7 * .95, H), (2.7, 0), .55, .085)
        a.part('Jerrycans', 'Crate', t).box((.26, .15, .44), loc=(s * .95, cy, cz), rot=(rrot, 0, 0), bevel=.02,
                                            seg=1)
    # Front: muzzle-velocity radar and an NBC box either side of the mantlet.
    tarm.box((.4, .3, .22), loc=(.74, -2.12, H - .16), bevel=.03, seg=1)
    a.part('Radar_face', 'Glass', t).box((.3, .03, .14), loc=(.74, -2.28, H - .16), bevel=0)
    tarm.box((.36, .3, .26), loc=(-.74, -2.1, H - .2), bevel=.03, seg=1)
    # Roof: commander's cupola with the machine gun (right), panoramic sight (left), loader's hatch,
    # vents, a tarp roll and antennas.
    tsteel.cyl(.33, .12, loc=(.78, -.35, H + .05), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.28, .05, loc=(.78, -.35, H + .12), seg=16, bevel=.015, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(4):
        ang = -R90 + (k - 1.5) * .7
        glass.box((.1, .05, .07), loc=(.78 + math.cos(ang) * .33, -.35 + math.sin(ang) * .33, H + .07),
                  rot=(0, 0, ang + R90), bevel=0)
    _roof_mg(a, t, (.78, -.35, H + .145), length=.9)
    tsteel.cyl(.13, .22, loc=(-.8, -1.35, H + .1), seg=10, bevel=.02, bseg=1)                    # panoramic sight
    tsteel.box((.32, .32, .22), loc=(-.8, -1.35, H + .3), bevel=.04, seg=1)
    a.part('Sight', 'Glass', t).box((.24, .04, .1), loc=(-.8, -1.52, H + .31), bevel=0)
    _hatch(a, -.7, .5, H + .04, .28, parent=t)
    a.part('Vents', 'Undercarriage', t).grille(.9, .5, loc=(0, 1.55, H + .01), rot=(-R90, 0, 0), slats=5,
                                               depth=.07, thickness=.04)
    _roll(a, (0, 2.3, H + .12), 1.8, r=.12, parent=t)
    for x, height in ((-1.2, 1.3), (1.2, 1.0)):
        tsteel.box((.1, .1, .07), loc=(x, 2.2, H), bevel=0)
        _antenna(a, t, x, 2.2, H + .02, height)
    # The gun, laid 10 degrees up. The mantlet turns with it; a breech block hidden inside the turret sets
    # the game's elevation pivot on the trunnion.
    T = (0, -1.98, .62)
    at = _axis(T, PITCH)
    crot, brot = _along(PITCH)
    mant = a.part('Main_cannon_mantlet', 'Armor', t)
    mant.box((1.06, .64, .84), loc=at(.02), rot=brot, bevel=.05, seg=1)
    mant.box((.56, .36, .5), loc=at(.46), rot=brot, bevel=.04, seg=1)                          # gun collar
    for side in (-.4, .4):
        mant.box((.14, .2, .5), loc=at(.4, 0, side), rot=brot, bevel=0)                         # collar ribs
    a.part('Main_cannon_breech', 'Steel', t).box((.5, .2, .6), loc=at(-.38, -.24), rot=brot, bevel=0)
    base = at(.6)
    parts.barrel(a, 'Main_cannon', t, 0, base.y, base.z, 5.8, .105, seg=12, sleeve=1.25, extractor=(.6, 1.6, .55),
                 brake_name='Muzzle_brake', brake='baffle', rot=crot)
    a.pivot('Muzzle_main', tuple(at(.6 + 5.8 + .3)), t)
    kit27.clean(a)



def atgm_carrier(a):
    """8x8 wheeled anti-tank missile carrier (M1134 Stryker ATGM lineage): a slab-sided hull with a blunt
    wedge nose and bolted applique armour tiles on its sides and upper flanks, the driver's hatch and
    periscopes front left, the engine grille and exhaust on the right, guarded lamps, a rear ramp with
    its door, and a remote weapon station behind the driver. On the roof a small turret raises its
    missile arm: the pod of 2x2 missile tubes (with its sight) sits on top and elevates on the arm's
    hinge."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.32, -1.12, .92, 2.12):
        for s in (-1, 1):
            _wheel(a, s * 1.12, y, .54, .4, seg=14)
            dark.box((.3, .2, .16), loc=(s * .86, y, .54), bevel=.02, seg=1)                     # hub carriers
    full = (.5, 1.14, 1.72, 2.08, .8, 1.36, 1.08)
    kit27.sharp_loft(hull, [
        _box_section(-3.48, .95, 1.14, 1.2, 1.3, .78, 1.2, 1.0),
        _box_section(-2.95, .52, 1.14, 1.58, 1.76, .8, 1.36, 1.1),
        _box_section(-2.45, *full),
        _box_section(3.3, *full),
        _box_section(3.46, .62, 1.14, 1.7, 2.02, .78, 1.33, 1.05),
    ], chamfer=.05)
    # Applique tiles: a row along each vertical side, a row on each upper flank, a band on the glacis.
    x, z, lean = _flank((1.36, 1.72), (1.08, 2.08), .5, .015)
    tiles = a.part('Tiles', 'Team')
    bolts = a.part('Tile_bolts', 'Steel')
    for s in (-1, 1):
        for i in range(8):
            y = -2.3 + i * .72
            tiles.box((.04, .66, .5), loc=(s * 1.37, y, 1.44), bevel=0)
            tiles.box((.04, .66, .36), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=0)
            bolts.box((.03, .05, .05), loc=(s * 1.395, y - .24, 1.64), bevel=0)
            bolts.box((.03, .05, .05), loc=(s * 1.395, y + .24, 1.26), bevel=0)
    gy, gz, grot = _glacis((-3.48, 1.3), (-2.95, 1.76), .5, .015)
    for xx in (-.66, 0, .66):
        tiles.box((.6, .5, .04), loc=(xx, gy, gz), rot=(grot, 0, 0), bevel=0)
    # Nose: lamps with brush guards, tow eyes, a winch fairlead.
    for s in (-1, 1):
        _headlight(a, s * .92, -3.47, 1.08, guard=True)
        steel.box((.14, .18, .14), loc=(s * .45, -3.5, .98), bevel=.02, seg=1)
        a.part('Marker_lights', 'Alloy').box((.1, .05, .06), loc=(s * 1.18, -3.47, 1.18), bevel=0)
        # Smoke dischargers on the front roof corners, mirrors on arms.
        for k in range(4):
            steel.cyl(.05, .18, loc=(s * (1.0 - k * .08), -2.5, 2.12), rot=(.7, 0, s * .6), seg=8, bevel=0)
        steel.tube([(s * 1.3, -2.7, 1.9), (s * 1.38, -2.88, 1.95)], .016, seg=4)
        armor.box((.05, .16, .26), loc=(s * 1.4, -2.92, 1.9), bevel=.01, seg=1)
        _taillight(a, s * .98, 3.46, 1.82)
        steel.box((.12, .12, .08), loc=(s * .55, 3.53, 1.04), bevel=0)                            # ramp hinges
        a.part('Mud_flaps', 'Rubber').box((.4, .04, .34), loc=(s * 1.12, 2.8, .72), bevel=0)
    dark.box((.5, .1, .14), loc=(0, -3.46, .98), bevel=.02, seg=1)
    # Driver front left: raised hatch ring with periscopes. Engine grille and exhaust on the right.
    armor.cyl(.34, .1, loc=(-.55, -2.1, 2.1), seg=14, bevel=.02, bseg=1)
    _hatch(a, -.55, -2.1, 2.15, .27)
    _periscopes(a, [(-.55 + math.cos(ang) * .36, -2.1 + math.sin(ang) * .36, 2.12, ang + R90)
                    for ang in (-R90, -R90 - .7, -R90 + .7)], size=(.1, .06, .07))
    dark.grille(.8, .7, loc=(.5, -2.05, 2.09), rot=(-R90, 0, 0), slats=6, depth=.07, thickness=.04)
    _grille_frame(a, .5, -2.05, 2.07, .8, .7, t=.04)
    armor.box((.1, .6, .26), loc=(1.39, -1.6, 1.52), bevel=.015, seg=1)                            # exhaust
    dark.grille(.5, .16, loc=(1.445, -1.6, 1.52), rot=(0, 0, R90), slats=2, depth=.04, thickness=.03)
    # Roof: the remote weapon station behind the driver, a rear troop hatch, antennas, a tow cable.
    armor.cyl(.26, .06, loc=(-.5, -1.2, 2.09), seg=12, bevel=0)
    _rws(a, None, (-.5, -1.2, 2.1))
    armor.box((1.0, .8, .06), loc=(0, 2.7, 2.09), bevel=.015, seg=1)                              # troop hatch
    steel.box((.8, .06, .05), loc=(0, 2.32, 2.12), bevel=0)
    for xx, h in ((-.85, 1.4), (.85, 1.1)):
        steel.box((.1, .1, .07), loc=(xx, 3.1, 2.08), bevel=0)
        _antenna(a, None, xx, 3.1, 2.1, h)
    _cable(a, [(-.95, -1.9, 2.1), (-.95, .0, 2.1), (-.95, 1.9, 2.1)])
    _stowage_bin(a, (.72, 2.2, 2.07), (.5, .8, .24), latch_side=0)
    for s in (-1, 1):                                                  # vision blocks along the roof edges
        _periscopes(a, [(s * .98, y, 2.07, s * R90) for y in ((-.6, 1.8, 2.6) if s > 0 else (2.85, 3.22))])
        _rail(a, [(s * .9, -.2, 2.07), (s * .9, -.2, 2.14), (s * .9, .5, 2.14), (s * .9, .5, 2.07)])  # grab rails
    _stowage_bin(a, (-.72, 2.2, 2.07), (.5, .8, .24), latch_side=0)
    for y in (-.45, 1.75):                                             # roof plate seams
        armor.box((1.9, .04, .03), loc=(0, y, 2.085), bevel=0)
    gy, gz, grot = _glacis((-2.95, 1.76), (-2.45, 2.08), .5, .01)
    armor.box((2.0, .04, .03), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=0)                    # glacis seam
    # Rear: ramp with a personnel door, handle, step and a jerrycan either side.
    armor.box((1.5, .07, 1.0), loc=(0, 3.47, 1.55), bevel=.02, seg=1)
    armor.box((.6, .06, .8), loc=(-.28, 3.5, 1.55), bevel=.015, seg=1)
    steel.box((.2, .05, .05), loc=(-.05, 3.54, 1.55), bevel=0)
    steel.box((1.0, .26, .05), loc=(0, 3.58, .98), bevel=0)
    for s in (-1, 1):
        _jerrycans(a, (s * 1.08, 3.56, 1.3), 1, axis='x', bracket=False)
    a.part('Jerrycan_rack', 'Steel').box((2.2, .05, .05), loc=(0, 3.65, 1.55), bevel=0)
    steel.cyl(.62, .08, loc=(0, .8, 2.1), seg=20, bevel=.02, bseg=1)                              # turret ring

    # Turret: a low base, the missile arm and the elevating pod on its hinge.
    t = a.pivot('Turret', (0, .8, 2.12))
    tteam = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tteam.prism(chamfered(1.3, 1.5, .3), .34, loc=(0, 0, .17), axis='Z', bevel=.04, taper=.9)       # base
    _hatch(a, -.3, .3, .34, .22, parent=t)
    tarm.box((.36, .4, .22), loc=(.35, .45, .44), bevel=.03, seg=1)                                 # electronics
    L, W, H = 1.75, .72, .68
    px, y0, zb = .12, -1.02, .98                                                                     # pod centre x, front, bottom
    hinge = Vector((px, y0 + L - .06 * L, zb + .3 * H))                                              # the game's pivot
    arm = a.part('Missile_arm', 'Armor', t)
    ax = px - W / 2 - .1
    arm.box((.18, .46, hinge.z - .2), loc=(ax, hinge.y - .05, (hinge.z + .2) / 2 + .02), bevel=.03, seg=1)
    arm.box((.2, .3, .3), loc=(ax, hinge.y - .05, .38), bevel=.03, seg=1)                            # arm root
    tsteel.limb((ax + .02, -.25, .36), (ax + .02, hinge.y - .28, hinge.z - .35), .08, .08, bevel=0)  # ram
    tsteel.cyl(.1, .16, loc=(ax + .06, hinge.y, hinge.z), rot=ACROSS, seg=10, bevel=0)                # hinge boss
    pod = a.part('Launcher', 'Team', t)
    pod.box((W, L, H), loc=(px, y0 + L / 2, zb + H / 2), bevel=.04, seg=1)
    frame = a.part('Launcher_frame', 'Armor', t)
    for y in (y0 + .12, y0 + L - .14):
        frame.box((W + .05, .1, H + .05), loc=(px, y, zb + H / 2), bevel=.012, seg=1)
    frame.box((.08, L - .5, .06), loc=(px, y0 + L / 2 + .05, zb + H + .02), bevel=0)               # top rail
    for cx in (-.17, .17):
        for cz in (-.17, .17):
            _tube_mouth(a, t, _frame((px + cx, y0, zb + H / 2 + cz), FORWARD), .12, protrude=.06, seg=10,
                        name='Launcher_tubes')
    frame.box((.16, .3, .24), loc=(px + W / 2 + .07, y0 + .3, zb + H / 2 + .08), bevel=.02, seg=1)  # sight
    a.part('Launcher_sight', 'Glass', t).box((.12, .03, .14), loc=(px + W / 2 + .07, y0 + .145, zb + H / 2 + .09),
                                              bevel=0)
    # Muzzle_main on the pod's front face at the hinge's height, so the game reads the pod as level (a
    # direct-fire weapon rests at 0 degrees and must not droop).
    a.pivot('Muzzle_main', (px, y0 - .065, hinge.z), t)
    kit27.clean(a)




def _turret_section(y, zb, zm, zt, wb, ws, wt):
    """Six-point turret section: floor (wb), side top at zm (ws), roof edge (wt at zt)."""
    return [(-wb, y, zb), (wb, y, zb), (ws, y, zm), (wt, y, zt), (-wt, y, zt), (-ws, y, zm)]


def _aps_radar(a, parent, loc, yaw):
    """Flat radar panel of the active protection system: a thick frame with a dark antenna face looking
    along -Y rotated by yaw, on a bracket."""
    m = _frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Aps_radar', 'Armor', parent).box((.72, .1, .54), loc=loc, rot=rot, bevel=.02, seg=1)
    a.part('Aps_radar_face', 'Undercarriage', parent).box((.6, .03, .42), loc=m @ Vector((0, -.055, 0)), rot=rot,
                                                           bevel=0)
    a.part('Aps_radar', 'Armor', parent).box((.14, .18, .34), loc=m @ Vector((0, .12, -.06)), rot=rot, bevel=0)


def aps_tank(a):
    """Main battle tank with an active protection system (Merkava Mk4 with Trophy lineage): front engine
    and a long shallow glacis with the driver's hatch at its head, air intakes and exhaust on the right,
    six road wheels behind heavy skirts with a saw-tooth lower edge, the rear door and rear baskets.
    Its own low wedge turret is set back on the hull: two long armour cheeks close to a point either side
    of the gun slot, the bustle overhangs with a ball-and-chain curtain under it and a basket behind it.
    The protection system is plain to see: four flat radar panels on the turret faces (two looking
    forward-out, two back-out) and a launcher head on each turret side (`Aps_left` / `Aps_right` at
    their openings). Smooth-bore 120 mm gun with a thermal sleeve, coaxial and roof machine guns."""
    parts.track_unit(a, 1.33, 6.9, .975, .32, 6, .64, sprocket_end=-1, cleat_pitch=.3, wheel_seg=7, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    kit27.extrude(hull, [(-3.4, .56), (-3.72, 1.12), (3.7, 1.12), (3.7, .56)], 1.96, axis='X', chamfer=0)          # belly
    nose, brow = (-3.85, 1.12), (-1.95, 1.72)
    kit27.extrude(hull, [(-3.72, 1.02), nose, brow, (3.55, 1.72), (3.8, 1.55), (3.8, 1.02)], 3.36, axis='X', chamfer=.07, corner=.04)
    # Heavy skirts: five plates a side whose lower front corners are cut away (the saw-tooth edge).
    skirt = a.part('Skirts', 'Team')
    lip = a.part('Skirt_edge', 'Armor')
    for s in (-1, 1):
        y0 = -3.3
        for i in range(5):
            ya, yb = y0 + i * 1.36, y0 + i * 1.36 + 1.32
            skirt.prism([(ya, 1.5), (ya, .82), (ya + .32, .6), (yb, .6), (yb, 1.5)], .12, loc=(s * 1.79, 0, 0),
                        bevel=.025, seg=1)
            lip.box((.15, 1.34, .05), loc=(s * 1.79, (ya + yb) / 2, 1.495), bevel=0)
        gy, gz, grot = _glacis(nose, brow, .1, .03)
        armor.box((.34, .2, .16), loc=(s * 1.3, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)     # lamp housings
        ly, lz, _ = _glacis(nose, brow, .045, .045)
        a.part('Lamps', 'Lamp').box((.24, .03, .09), loc=(s * 1.3, ly, lz), rot=(grot, 0, 0), bevel=0)
        steel.box((.16, .2, .14), loc=(s * .7, -3.76, .98), bevel=.02, seg=1)                   # tow hooks
        steel.box((.16, .2, .14), loc=(s * .9, 3.86, .98), bevel=.02, seg=1)
        _taillight(a, s * 1.45, 3.8, 1.36)
        # Rear baskets at the hull corners.
        _basket(a, s * .75 - .45, s * .75 + .45, 3.0, 3.72, 1.71, .28, contents=False)
    # Glacis: add-on armour plates and the driver's hatch with vision blocks at its head.
    for row, u in enumerate((.3, .62)):
        gy, gz, grot = _glacis(nose, brow, u, .035)
        for x in ((-1.1, -.37, .37, 1.1) if row else (-1.2, -.6, 0, .6, 1.2)):
            armor.box((.66 if row else .54, .5, .08), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
    _hatch(a, -.72, -1.72, 1.71, .26, handle=False)
    gy, gz, grot = _glacis(nose, brow, .93, .015)
    a.part('Vision_blocks', 'Glass').box((.5, .07, .05), loc=(-.72, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    # Engine air intakes on the right of the deck, exhaust louvres on the right flank.
    for y in (-1.55, -.95):
        deck.grille(.9, .45, loc=(.95, y, 1.73), rot=(-R90, 0, 0), slats=4, depth=.06, thickness=.04)
    _grille_frame(a, .95, -1.25, 1.71, .9, 1.05, t=.04)
    armor.box((.1, .9, .3), loc=(1.7, -1.0, 1.6), bevel=.015, seg=1)
    deck.grille(.8, .2, loc=(1.755, -1.0, 1.6), rot=(0, 0, R90), slats=2, depth=.04, thickness=.03)
    _cable(a, [(-1.45, -1.9, 1.745), (-1.45, .2, 1.745), (-1.45, 2.6, 1.745)])
    # Rear door in the middle of the tail, hinged on the left, with a handle and a step.
    armor.box((.95, .07, .52), loc=(0, 3.8, 1.25), bevel=.02, seg=1)
    for z in (1.08, 1.42):
        steel.box((.08, .1, .1), loc=(-.5, 3.84, z), bevel=0)
    steel.box((.24, .05, .05), loc=(.3, 3.855, 1.25), bevel=0)
    steel.box((.9, .2, .05), loc=(0, 3.86, .9), bevel=0)
    steel.cyl(1.3, .1, loc=(0, .7, 1.75), seg=24, bevel=.02, bseg=1)                             # turret ring

    t = a.pivot('Turret', (0, .7, 1.75))
    turret = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    kit27.sharp_loft(turret, [
        _turret_section(-1.62, .02, .52, .78, 1.2, 1.26, 1.0),
        _turret_section(1.2, .02, .58, .84, 1.52, 1.58, 1.3),
        _turret_section(1.62, .22, .58, .84, 1.5, 1.56, 1.28),
        _turret_section(2.4, .28, .56, .78, 1.38, 1.44, 1.18),
    ], chamfer=.05)
    # Two long armour cheeks close to a point either side of the gun slot.
    for s in (-1, 1):
        def sec(y, xo, zb, zt, ch):
            pts = [(xo, y, zb), (.27, y, zb), (.27, y, zt), (xo - ch, y, zt), (xo, y, zt - ch)]
            return [(s * px, py, pz) for px, py, pz in pts]
        kit27.sharp_loft(turret, [sec(-1.5, 1.22, .03, .77, .2), sec(-2.35, .8, .1, .6, .14), sec(-3.05, .42, .22, .44, .06)],
                         chamfer=.03)
    tarm.box((.5, .42, .44), loc=(0, -1.66, .46), bevel=.04, seg=1)                             # mantlet
    # Ball-and-chain curtain under the bustle, a basket behind it.
    chains = a.part('Chains', 'Steel', t)
    for i in range(14):
        x = -1.04 + i * .16
        chains.box((.025, .025, .22), loc=(x, 2.9, .19), bevel=0)
        chains.box((.07, .07, .07), loc=(x, 2.9, .07), bevel=0)
    _basket(a, -1.1, 1.1, 2.36, 2.95, .3, .3, parent=t)
    # Protection system: four radar panels on the turret faces and a launcher head on each side.
    for s in (-1, 1):
        _aps_radar(a, t, (s * 1.2, -1.25, .98), s * .75)
        _aps_radar(a, t, (s * 1.38, 1.74, .98), s * (math.pi - .75))
        tsteel.cyl(.1, .2, loc=(s * 1.42, .55, .82), seg=10, bevel=0)                             # launcher mount
        head = a.part('Aps_launcher', 'Armor', t)
        m = _frame((s * 1.42, .55, 1.06), (0, 0, s * .7))
        head.box((.34, .42, .3), loc=m.to_translation(), rot=(0, 0, s * .7), bevel=.03, seg=1)
        _tube_mouth(a, t, m @ _frame((0, -.21, 0), FORWARD), .1, protrude=.05, seg=10, name='Aps_tube')
        a.pivot('Aps_left' if s < 0 else 'Aps_right', tuple(m @ Vector((0, -.27, 0))), t)
        # Smoke dischargers on the cheeks, a rail along the roof edge.
        for k in range(3):
            tsteel.cyl(.05, .18, loc=(s * (1.0 + k * .08), -.7 + k * .1, .82), rot=(.6, 0, s * .5), seg=8, bevel=0)
    # Roof: commander's cupola with the machine gun (right), loader's hatch and the 60 mm mortar (left),
    # the gunner's sight on the right cheek, wind sensor and antennas.
    tsteel.cyl(.33, .14, loc=(.6, .3, .88), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.28, .06, loc=(.6, .3, .97), seg=16, bevel=.015, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(5):
        ang = -R90 + (k - 2) * .62
        glass.box((.1, .05, .07), loc=(.6 + math.cos(ang) * .33, .3 + math.sin(ang) * .33, .9),
                  rot=(0, 0, ang + R90), bevel=0)
    _roof_mg(a, t, (.6, .3, 1.0), length=.9)
    _hatch(a, -.6, .45, .85, .26, parent=t)
    tsteel.cyl(.07, .7, loc=(-.95, .9, 1.0), rot=(-.5, 0, 0), seg=8, bevel=0)                     # mortar
    tarm.box((.3, .3, .24), loc=(.55, -1.1, .82), bevel=.03, seg=1)                              # gunner's sight
    a.part('Sight', 'Glass', t).box((.22, .03, .12), loc=(.55, -1.26, .84), bevel=0)
    tsteel.cyl(.02, .3, loc=(0, 1.6, 1.0), seg=5, bevel=0)                                        # wind sensor
    tsteel.box((.08, .08, .1), loc=(0, 1.6, 1.18), bevel=0)
    for x, h in ((-1.0, 1.4), (1.0, 1.1)):
        tsteel.box((.09, .09, .06), loc=(x, 2.05, .83), bevel=0)
        _antenna(a, t, x, 2.05, .84, h)
    parts.barrel(a, 'Main_cannon', t, 0, -1.8, .46, 4.3, .11, seg=10, sleeve=1.3, extractor=(.5, 1.45, .14),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -1.8 - 4.3 - .14, .46), t)
    _coax(a, t, .19, -1.79, .6, length=.4, housing=.26)
    kit27.clean(a)


def siege_mortar(a):
    """Tracked 240 mm self-propelled mortar (Tyulpan lineage): a low chassis with seven road wheels and
    return rollers, spare links and guarded lamps on the glacis, engine grilles, a commander's cupola
    with the machine gun, and a huge short mortar at the rear on a trainable mount: breech drum and
    base plate hanging over the tail, a cradle between tall trunnion brackets, recuperators and an
    elevation ram, laid 60 degrees up over the hull. A recoil spade folds up under the tail."""
    parts.track_unit(a, 1.22, 6.5, .87, .29, 7, .54, sprocket_end=-1, cleat_pitch=.3, wheel_seg=7, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    kit27.extrude(hull, [(-3.1, .5), (-3.5, 1.02), (3.45, 1.02), (3.35, .5)], 1.8, axis='X', chamfer=0)             # belly
    nose, brow = (-3.72, 1.14), (-2.45, 1.55)
    kit27.extrude(hull, [(-3.58, .97), nose, brow, (3.45, 1.55), (3.6, 1.38), (3.6, .97)], 3.0, axis='X', chamfer=.06, corner=.04)
    for s in (-1, 1):
        # Guarded headlights on the glacis corners, tow hooks, spare track links.
        gy, gz, grot = _glacis(nose, brow, .2, .04)
        armor.box((.32, .2, .16), loc=(s * 1.2, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
        ly, lz, _ = _glacis(nose, brow, .126, .05)
        a.part('Lamps', 'Lamp').box((.2, .03, .09), loc=(s * 1.2, ly, lz), rot=(grot, 0, 0), bevel=0)
        gy, gz, grot = _glacis(nose, brow, .55, 0)
        _track_links(a, _frame((s * .62, gy, gz), (grot, 0, 0)), 3, width=.46)
        steel.box((.14, .2, .14), loc=(s * .6, -3.34, .78), bevel=.02, seg=1)
        steel.box((.14, .2, .14), loc=(s * .6, 3.44, .78), bevel=.02, seg=1)
        _taillight(a, s * 1.25, 3.6, 1.2)
        # Side stowage: bins on the hull flanks and a tow cable along the deck edge.
        for y, d in ((-2.0, 1.0), (-.75, 1.0), (1.25, 1.2)):
            armor.box((.14, d, .34), loc=(s * 1.55, y, 1.3), bevel=.02, seg=1)
            steel.box((.03, .06, .08), loc=(s * 1.625, y, 1.38), bevel=0)
        _cable(a, [(s * 1.38, -2.1, 1.575), (s * 1.38, -.4, 1.575), (s * 1.36, .7, 1.575)])
    # Front deck: engine grilles and exhaust on the right, driver's hatch and the cupola on the left.
    for y, d in ((-2.0, .7), (-1.1, .6)):
        deck.grille(1.0, d, loc=(.72, y, 1.56), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
        _grille_frame(a, .72, y, 1.54, 1.0, d, t=.04)
    deck.grille(.6, .2, loc=(1.505, .15, 1.3), rot=(0, 0, R90), slats=2, depth=.05, thickness=.04)  # exhaust
    _hatch(a, -.75, -2.1, 1.54, .26)
    _periscopes(a, [(-.75 + dx, -2.42, 1.54, 0) for dx in (-.17, 0, .17)])
    armor.cyl(.38, .26, loc=(-.75, -1.2, 1.64), seg=16, bevel=.03, bseg=1)                       # cupola
    glass = a.part('Periscopes', 'Glass')
    for k in range(5):
        ang = -R90 + (k - 2) * .62
        glass.box((.1, .05, .07), loc=(-.75 + math.cos(ang) * .38, -1.2 + math.sin(ang) * .38, 1.7),
                  rot=(0, 0, ang + R90), bevel=0)
    _heavy_mg(a, None, (-.75, -1.2, 1.76))
    _hatch(a, .6, .35, 1.54, .28)                                                                 # crew hatches
    _hatch(a, -.6, .35, 1.54, .28)
    for x in (-.45, .45):
        a.part('Ammo_boxes', 'Crate').box((.42, .3, .24), loc=(x, -.35, 1.66), bevel=.02, seg=1)
    _antenna(a, None, 1.3, -.25, 1.54, 1.3)
    for s in (-1, 1):                                                                             # ready rounds
        for y in (.85, 1.5):
            a.part('Ammo_boxes', 'Crate').box((.46, .68, .34), loc=(s * 1.25, y, 1.71), bevel=.02, seg=1)
            steel.box((.5, .06, .06), loc=(s * 1.25, y, 1.86), bevel=0)
    # Recoil spade folded up under the tail.
    lean = .38
    spade = a.part('Spade', 'Armor')
    spade.box((2.3, .12, .75), loc=(0, 3.86, .82), rot=(lean, 0, 0), bevel=.03, seg=1)
    for x in (-.7, 0, .7):
        spade.box((.08, .14, .62), loc=(x, 3.79, .84), rot=(lean, 0, 0), bevel=0)
    for x in (-.8, -.27, .27, .8):
        steel.box((.14, .1, .14), loc=(x, 4.02, .47), rot=(lean, 0, 0), bevel=0)
    for s in (-1, 1):
        steel.limb((s * .9, 3.36, .72), (s * .9, 3.84, .76), .12, .12, bevel=.02)
    steel.cyl(.06, 2.0, loc=(0, 3.82, .74), rot=ACROSS, seg=8, bevel=0)
    steel.cyl(.95, .08, loc=(0, 2.5, 1.56), seg=20, bevel=.02, bseg=1)                           # turret ring

    t = a.pivot('Turret', (0, 2.5, 1.58))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.9, .08, loc=(0, 0, .02), seg=20, bevel=.02, bseg=1)                            # turntable
    tarm.box((1.5, 1.65, .44), loc=(0, .075, .24), bevel=.05, seg=1, taper=(.92, .92))             # mount base
    pitch = math.radians(60)
    at = _axis((0, 1.0, 1.05), pitch)                                                               # breech end
    rot = (R90 - pitch, 0, 0)
    tilt = Euler(rot, 'XYZ').to_matrix()
    L = 3.0
    tube = a.part('Mortar_tube', 'Team', t)
    tube.lathe([(.31, -.05), (.28, L - .36), (.36, L - .32), (.36, L), (.23, L), (.23, L - .3)], loc=at(0), rot=rot,
               seg=16)
    a.part('Mortar_bore', 'Undercarriage', t).cyl(.22, .02, loc=at(L - .28), rot=rot, seg=14, bevel=0)
    tube.cyl(.315, .14, loc=at(L * .6), rot=rot, seg=16, bevel=0)                                  # band
    breech = a.part('Mortar_breech', 'Armor', t)
    breech.cyl(.44, .6, loc=at(.1), rot=rot, seg=16, bevel=.04)
    breech.cyl(.62, .12, loc=at(-.26), rot=rot, seg=16, bevel=.03)                                 # base plate
    for k in range(4):                                                                             # plate ribs
        rib = (tilt @ Euler((0, 0, k * math.pi / 4), 'XYZ').to_matrix()).to_euler('XYZ')
        breech.box((1.12, .07, .12), loc=at(-.37 + k * .015), rot=tuple(rib), bevel=0)
    tarm.cyl(.4, .9, loc=at(.95), rot=rot, seg=16, bevel=.03)                                     # cradle
    tsteel.cyl(.12, 1.44, loc=at(.95), rot=ACROSS, seg=10, bevel=0)                               # trunnions
    ty, tz = at(.95).y, at(.95).z
    for s in (-1, 1):
        tarm.box((.16, .6, tz + .24 - .42), loc=(s * .62, ty, (tz + .24 + .42) / 2), bevel=.03, seg=1)  # brackets
        tsteel.cyl(.18, .06, loc=(s * .72, ty, tz), rot=ACROSS, seg=10, bevel=0)                  # trunnion caps
    rec = a.part('Recuperators', 'Steel', t)
    for side in (-.18, .18):
        rec.cyl(.08, 1.1, loc=at(1.3, -.44, side), rot=rot, seg=10, bevel=0)
        rec.cyl(.095, .06, loc=at(1.85, -.44, side), rot=rot, seg=10, bevel=0)
    tsteel.limb((0, -.55, .44), tuple(at(1.3, -.48)), .16, .16, bevel=.02, seg=1)                   # elevation ram
    tarm.box((.18, .22, .18), loc=(-.62, ty - .41, 1.55), bevel=.02, seg=1)                         # sight
    a.part('Sight', 'Glass', t).box((.12, .04, .1), loc=(-.62, ty - .53, 1.57), bevel=.01, seg=1)
    a.pivot('Muzzle_main', tuple(at(L + .02)), t)
    kit27.clean(a)


import mb_artillery  # noqa: E402

UNITS3 = {'howitzer': howitzer, 'atgm_carrier': atgm_carrier, 'aps_tank': aps_tank, 'siege_mortar': siege_mortar}
_UOPT = {**mb_artillery.BUILDERS, **mb_vehicles3.BUILDERS}
BUILDERS.update({n: (fn, dict(_UOPT[n][1], ao_strength=.5 if n == 'atgm_carrier' else .65)) for n, fn in UNITS3.items()})


# ----------------------------------------------------------------------------- pass 8a4: unlisted units (V2 kit, wave 3 rules)
def apc(a, detail=False):
    """8x8 wheeled armoured personnel carrier (Stryker / Boxer lineage) with a wedge nose and a 30 mm turret: a
    chamfered hull, bolted add-on armour on the sloped flanks, hub carriers over the tyres, mud flaps, troop hatches
    with vision blocks, roof bins, slat armour flanking the rear door and a bedroll on the roof. The turret is a
    sharp-edged loft with the library hatch; the gun is a one-surface barrel with a collar muzzle."""
    hd.mark(a, detail)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.3, -1.12, .82, 2.0):
        for s in (-1, 1):
            _wheel(a, s * 1.15, y, .56, .44, seg=18)
            dark.box((.26, .2, .16), loc=(s * .9, y, .56), bevel=.02, seg=1)                     # hub carriers
            a.part('Mud_flaps', 'Rubber').box((.4, .04, .3), loc=(s * 1.15, y + .56, .74), bevel=0)
    kit27.sharp_loft(hull, [
        _hull_section(-3.42, .86, .95, 1.03, 1.12, .62, .8, .82, .66),
        _hull_section(-2.75, .48, 1.02, 1.28, 1.5, .9, 1.2, 1.24, .96),
        _hull_section(-1.9, .45, 1.05, 1.35, 2.0, .9, 1.24, 1.28, 1.0),
        _hull_section(3.2, .45, 1.05, 1.35, 2.0, .9, 1.24, 1.28, 1.0),
        _hull_section(3.4, .58, 1.05, 1.33, 1.93, .86, 1.2, 1.24, .96),
    ], chamfer=.05)
    slope = math.atan2(1.28 - 1.0, 2.0 - 1.35)
    for s in (-1, 1):
        for y in (-1.25, .15, 1.55):
            armor.box((.06, 1.3, .52), loc=(s * (1.14 + .018), y, 1.683), rot=(0, -s * slope, 0), bevel=.015, seg=1)
        _headlight(a, s * .45, -3.42, .99)
        steel.box((.12, .2, .12), loc=(s * .5, -3.3, .78), bevel=.02, seg=1)                # tow hooks
        _taillight(a, s * .9, 3.4, 1.62)
        steel.box((.1, .12, .08), loc=(s * .47, 3.45, 1.66), bevel=.01, seg=1)             # door hinges
        steel.box((.1, .12, .08), loc=(s * .47, 3.45, .9), bevel=.01, seg=1)
        armor.box((.75, 1.15, .06), loc=(s * .45, 2.35, 2.01), bevel=.015, seg=1)          # troop hatches
        steel.box((.06, 1.0, .05), loc=(s * .12, 2.35, 2.04), bevel=0)
        _rail(a, [(s * .62, 2.2, 2.03), (s * .62, 2.2, 2.09), (s * .62, 2.5, 2.09), (s * .62, 2.5, 2.03)])
        _periscopes(a, [(s * .45, 1.66, 1.99, 0)])
        _periscopes(a, [(s * .93, y, 1.99, s * R90) for y in (.2, .9)])
        _stowage_bin(a, (s * 1.33, -.15, 1.06), (.14, .7, .28), latch_side=s)
        _slats(a, _frame((s * .9, 3.56, 1.0), (0, 0, 0)), .55, .56, 5)
        for dx in (-.24, .24):
            steel.box((.04, .18, .04), loc=(s * .9 + dx, 3.48, 1.2), bevel=0)
    armor.box((1.1, .06, .34), loc=(0, -3.0, 1.37), rot=(-1.04, 0, 0), bevel=.015, seg=1)  # trim vane
    _hatch(a, -.52, -1.55, 1.99, .28)
    glass = a.part('Vision_blocks', 'Glass')
    for dx in (-.16, 0, .16):
        glass.box((.12, .05, .07), loc=(-.52 + dx, -1.92, 1.99), rot=(-.53, 0, 0), bevel=.01, seg=1)
    a.part('Deck', 'Undercarriage').grille(.72, .7, loc=(.48, -1.3, 2.01), rot=(-R90, 0, 0), slats=6, depth=.07,
                                           thickness=.04)
    _grille_frame(a, .48, -1.3, 1.99, .72, .7, t=.04)
    armor.box((1.0, .08, 1.0), loc=(0, 3.42, 1.25), bevel=.02, seg=1)                  # rear door
    steel.box((.3, .06, .05), loc=(.25, 3.48, 1.3), bevel=.01, seg=1)
    dark.box((1.2, .3, .08), loc=(0, 3.47, .6), bevel=.02, seg=1)                       # rear step
    steel.cyl(.62, .1, loc=(0, -.55, 2.02), seg=20, bevel=.02, bseg=1)                  # turret ring
    for y in (-.3, 1.7):                                                               # roof plate seams
        armor.box((1.9, .04, .03), loc=(0, y, 1.995), bevel=0)
    _roll(a, (0, 3.05, 2.08), 1.3, r=.1)
    for s in (-1, 1):
        _stowage_bin(a, (s * .45, 1.15, 1.99), (.56, .62, .22), latch_side=0)
    _cable(a, [(1.03, -1.7, 1.985), (1.03, .9, 1.985), (1.03, 3.0, 1.97)])
    _antenna(a, None, -.85, 3.0, 1.95, 1.3)

    t = a.pivot('Turret', (0, -.55, 2.06))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.55, .62), (.55, .62), (.66, .12), (.55, -.42), (.3, -.66), (-.3, -.66), (-.55, -.42), (-.66, .12)]
    kit27.sharp_loft(turret, [[(x, y, .02) for x, y in outline],
                              [(x * .93, y * .93, .3) for x, y in outline],
                              [(x * .86, y * .86, .52) for x, y in outline]], chamfer=.045)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.36, .24, .3), loc=(0, -.72, .28), bevel=.035)                           # mantlet
    tarm.box((.9, .3, .3), loc=(0, .7, .25), bevel=.035, taper=(.95, .9))              # bustle
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.box((.26, .26, .22), loc=(.3, .1, .6), bevel=.035)                          # commander sight
    a.part('Sight', 'Glass', t).box((.18, .04, .11), loc=(.3, -.03, .62), bevel=.01, seg=1)
    for s in (-1, 1):
        _smoke(a, tsteel, .44, -.4, .44, s, count=2, gap=.07)
    _hatch(a, -.22, .22, .5, .19, parent=t)
    tsteel.box((.34, .22, .12), loc=(-.72, .02, .38), bevel=.02, seg=1)
    launcher = a.part('Launcher', 'Armor', t)
    launcher.box((.3, 1.0, .46), loc=(-.95, .02, .42), bevel=.04)
    for z in (.31, .53):
        _tube_mouth(a, t, _frame((-.95, -.47, z), FORWARD), .085, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-.95, -.53, .42), t)
    parts.barrel(a, 'Main_cannon', t, 0, -.84, .28, 1.95, .05, seg=10, sleeve=1.5, extractor=(.55, 1.45, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -.84 - 1.95 - .17, .28), t)
    _coax(a, t, .25, -.69, .33, length=.32, housing=.3)
    if detail:
        bolts = a.part('Hull_bolts', 'Steel')
        for s in (-1, 1):
            plate = hd.frame((s * (1.14 + .018), 0, 1.683), (0, -s * slope, 0))
            brot = (plate.to_3x3() @ Euler(hd.side_rot(s), 'XYZ').to_matrix()).to_euler('XYZ')
            for y in (-1.25, .15, 1.55):
                for dy in (-.56, .56):
                    for dz in (-.2, .2):
                        hd.bolt(bolts, tuple(plate @ Vector((s * .03, y + dy, dz))), tuple(brot), r=.017, h=.024)
            for y0, y1, n in ((-1.8, -.65, 4), (.35, 3.1, 9)):
                hd.bolt_line(bolts, (s * 1.262, y0, 1.2), (s * 1.262, y1, 1.2), n, rot=hd.side_rot(s), r=.016, h=.024)
            _shackle(a, s * .5, -3.32, .72)
        a.part('Vision_blocks', 'Glass').box((.16, .03, .08), loc=(-.22, 3.465, 1.58), bevel=0)
        armor.box((.24, .06, .03), loc=(-.22, 3.47, 1.64), bevel=0)
        hd.handle(steel, (.4, 3.46, 1.05), (.4, 3.46, 1.4), (0, 1, 0), h=.06)
        hd.bolt_line(bolts, (-.36, 3.46, .82), (-.36, 3.46, 1.45), 4, rot=hd.BACK, r=.015, h=.022)
        tb = a.part('Turret_bolts', 'Steel', t)
        for dx in (-.12, .12):
            for dz in (-.09, .09):
                hd.bolt(tb, (dx, -.84, .28 + dz), hd.FRONT, r=.014, h=.022)
        hd.bolt_line(tb, (-.35, .842, .3), (.35, .842, .3), 5, rot=hd.BACK, r=.013, h=.02)
        _eyes(a, [(.42, .42, .52, 0), (-.4, .46, .52, 0), (0, -.42, .52, 0)], parent=t, size=.075)
        _vent(a, .1, .35, .52, parent=t, r=.075)
        tarm.box((.3, .08, .025), loc=(.3, -.05, .72), bevel=0)
        for dx in (-.1, .1):
            for dy in (-.07, .07):
                hd.bolt(tb, (-.72 + dx, .02 + dy, .44), r=.013, h=.02)
    kit27.clean(a)


UNITS4 = {'apc': apc}
_OPT4 = {'apc': mb_vehicles.BUILDERS['apc'][1]}


def armed_truck(a):
    """Army cargo truck (6x4, Ural / Kamaz lineage) for the ammunition carrier and the supply truck: a cab-over cab
    in team paint on a chamfered extrusion with a raked windscreen, wipers, door lines, guarded lamps, a front
    bumper with tow hooks and a roof visor; a cargo box on ribs with a stripe, rear doors and lock bars, underrun
    guards, mud flaps, a fuel tank; a ring-mounted machine gun over the cab on the `Turret` pivot
    (its flash hider's face `Muzzle_main`). The ring sits far enough forward for the barrel to clear the box."""
    from mb_town import _arches, _wheels, fbox
    paint = a.part('Cab', 'Team')
    a.part('Chassis', 'Undercarriage').box((1.0, 6.6, .28), loc=(0, .05, .72), bevel=.02, seg=1)
    kit27.extrude(paint, [(-3.48, .82), (-1.55, .82), (-1.55, 2.95), (-3.18, 2.95), (-3.45, 2.3), (-3.5, 1.6)], 2.3,
                  axis='X', chamfer=.06, corner=.05)
    glass = a.part('Glass', 'Glass')
    p0, p1 = (-3.45, 2.33), (-3.19, 2.9)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    n = (-math.sin(ang), math.cos(ang))
    glass.limb((0, p0[0] + n[0] * .03, p0[1] + n[1] * .03), (0, p1[0] + n[0] * .03, p1[1] + n[1] * .03), 2.0, .04,
               bevel=0)
    for face, x in (('-x', -1.15), ('+x', 1.15)):
        fbox(glass, face, (x, -2.6, 2.35), (1.0, .04, .72), out=.01)
    dark = a.part('Rubber_trim', 'Rubber')
    for t0 in (-.55, .35):                                                   # wipers
        q0 = [c0 + (c1 - c0) * .1 + nc * .055 for c0, c1, nc in zip(p0, p1, n)]
        q1 = [c0 + (c1 - c0) * .55 + nc * .055 for c0, c1, nc in zip(p0, p1, n)]
        dark.limb((t0, q0[0], q0[1]), (t0 + .3, q1[0], q1[1]), .03, .02, bevel=0)
    paint.box((2.1, .3, .05), loc=(0, -3.28, 2.92), bevel=.01, seg=1)       # sun visor
    armor = a.part('Trim', 'Armor')
    steel = a.part('Ribs', 'Steel')
    armor.box((2.4, .22, .32), loc=(0, -3.56, .86), bevel=.04, seg=1)       # bumper
    fbox(armor, '-y', (0, -3.49, 1.35), (1.4, .05, .45), out=.02)           # grille
    for k in range(5):                                                       # grille slats
        steel.box((1.3, .03, .04), loc=(0, -3.57, 1.18 + k * .08), bevel=0)
    for sx in (-1, 1):
        a.part('Headlights', 'Lamp').box((.3, .05, .2), loc=(sx * .85, -3.51, 1.3), bevel=.02, seg=1)
        steel.box((.36, .06, .04), loc=(sx * .85, -3.55, 1.44), bevel=0)    # lamp brow
        armor.limb((sx * 1.12, -3.15, 2.25), (sx * 1.32, -3.25, 2.25), .04, .04, bevel=0)     # mirror arms
        armor.box((.06, .16, .36), loc=(sx * 1.33, -3.28, 2.12), bevel=.01, seg=1)
        armor.box((.14, .5, .08), loc=(sx * 1.18, -2.55, .95), bevel=0)                         # cab step
        steel.box((.1, .16, .1), loc=(sx * .5, -3.62, .76), bevel=.01, seg=1)                   # tow hooks
        for y in (-3.15, -2.05):                                                 # door shut lines
            dark.box((.02, .03, 1.45), loc=(sx * 1.155, y, 2.025), bevel=0)
        a.part('Handles', 'Steel').box((.03, .14, .05), loc=(sx * 1.165, -2.2, 1.85), bevel=0)
        a.part('Marker_lights', 'Alloy').box((.1, .05, .08), loc=(sx * 1.07, -3.51, 1.3), bevel=0)
    a.part('Plate', 'PlasterWhite').box((.46, .03, .12), loc=(0, -3.685, .86), bevel=0)
    for x in (-.5, 0, .5):
        a.part('Marker_lights', 'Alloy').box((.12, .06, .06), loc=(x, -3.1, 2.98), bevel=0)
    # Exhaust stack behind the cab, on the right.
    steel.tube([(1.0, -1.45, .9), (1.0, -1.45, 3.1)], .06, seg=8)
    steel.cyl(.09, .1, loc=(1.0, -1.45, 3.15), seg=8, bevel=0)
    # Cargo box with ribs, rails and rear doors.
    box = a.part('Cargo', 'Fuel')
    kit27.extrude(box, [(-1.495, 0.9), (3.455, 0.9), (3.455, 3.5), (-1.495, 3.5)], 2.44, axis='X', chamfer=.05,
                  corner=.05)
    for sx in (-1, 1):
        for y in (-.9, .1, 1.1, 2.1, 3.1):
            steel.box((.04, .08, 2.34), loc=(sx * 1.235, y, 2.25), bevel=0)
        steel.box((.06, 4.95, .08), loc=(sx * 1.22, .98, 3.47), bevel=0)
        a.part('Stripe', 'Team').box((.055, 4.75, .2), loc=(sx * 1.2175, .98, 2.9), bevel=0)
        for y in (-1.0, 2.6):
            a.part('Marker_lights', 'Alloy').box((.03, .1, .06), loc=(sx * 1.235, y, 1.14), bevel=0)
        for z in (.62, .84):                                                     # underrun guards
            steel.box((.04, 3.7, .06), loc=(sx * 1.2, -.12, z), bevel=0)
        for z in (1.2, 1.8, 2.4, 3.0):                                           # rear door hinges
            steel.box((.08, .05, .12), loc=(sx * 1.17, 3.48, z), bevel=0)
        steel.tube([(sx * .3, 3.51, 1.1), (sx * .3, 3.51, 3.3)], .025, seg=6)   # lock bars
        steel.box((.14, .05, .04), loc=(sx * .36, 3.53, 1.9), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.62, .03, .45), loc=(sx * .88, 2.85, .62), bevel=0)
        steel.box((.05, 1.2, .05), loc=(sx * 1.26, 2.4, 3.2), bevel=0)           # tarp-bow brackets
    armor.box((2.5, 5.0, .18), loc=(0, .98, .98), bevel=.02, seg=1)
    for x in (-.6, 0, .6):
        steel.box((.05, .04, 2.5), loc=(x, 3.47, 2.2), bevel=0)
    armor.box((2.2, .12, .15), loc=(0, 3.5, .62), bevel=.02, seg=1)
    for sx in (-1, 1):
        a.part('Taillights', 'BarrelRed').box((.25, .05, .15), loc=(sx * 1.0, 3.5, .8), bevel=.01, seg=1)
    a.part('Plate', 'PlasterWhite').box((.46, .03, .12), loc=(0, 3.58, .62), bevel=0)
    a.part('Fuel_tank', 'Steel').cyl(.26, 1.0, loc=(-.85, -.9, .72), rot=(R90, 0, 0), seg=12, bevel=.02, bseg=1)
    armor.box((.5, .6, .45), loc=(.85, -.9, .75), bevel=.02, seg=1)
    _wheels(a, [(sx * .98, -2.55) for sx in (-1, 1)], .48, .3, hub=.45)
    _wheels(a, [(sx * x, 2.3) for sx in (-1, 1) for x in (.72, 1.04)], .48, .3, hub=.45)
    _arches(a, 1.15, (-2.55,), .82, .56)
    steel = a.part('Ring_mount', 'Steel')
    steel.cyl(.36, .06, loc=(0, -2.75, 2.97), seg=16, bevel=.015, bseg=1)             # ring on the cab roof
    for s in (-1, 1):
        steel.box((.05, .05, .1), loc=(s * .3, -2.75, 2.97), bevel=0)                    # ring brackets
    _rws_turret(a, (0, -2.75, 3.0), length=.85, sensor=False, shield=True)
    kit27.clean(a)


UNITS4['armed_truck'] = armed_truck
_OPT4['armed_truck'] = mb_new_trucks.BUILDERS['armed_truck'][1]


def sapper(a):
    """Combat engineer vehicle (Terrier / Kodiak lineage): a heavy sponson hull on V2 running gear with a crew cab front
    left, a raised dozer blade, an excavator arm folded along the right and a rear deck with welding kit, crane and
    winch. Chamfered lofts for the hull and cab, an extruded blade, the library hatches."""
    parts.track_unit(a, 1.32, 6.6, .96, .31, 7, .6, sprocket_end=1, cleat_pitch=.24, wheel_seg=10, teeth=7)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    full = (.5, 1.0, 1.62, 1.02, 1.66, 1.36)
    front, back = (-3.62, 1.14), (-2.55, 1.62)                     # upper glacis (y, z)
    kit27.sharp_loft(hull, [
        _sponson_section(-3.62, .72, 1.0, 1.14, .96, 1.58, 1.3),
        _sponson_section(-2.55, *full),
        _sponson_section(3.2, *full),
        _sponson_section(3.48, .62, 1.0, 1.48, .98, 1.64, 1.32),
    ], chamfer=.05)
    # Heavy side skirts over the tracks, bolt-on plates on the sloped flanks above them.
    fx, fz, lean = _flank((1.66, 1.08), (1.36, 1.62), .5, .025)
    for s in (-1, 1):
        _skirt(a, s, 1.72, -3.25, 3.3, .56, 1.18, 5, thick=.1, bolts=True)
        for y in (-2.1, -.9, .35, 1.6, 2.75):
            armor.box((.06, 1.1, .4), loc=(s * fx, y, fz), rot=(0, -s * lean, 0), bevel=0)
    # Crew cab on the front left: a steep front plate with vision blocks, inward-sloped sides.
    x0, x1 = -.05, 1.42

    def cab_ring(y, zt, inset):
        return [(x0, y, 1.56), (x1, y, 1.56), (x1 - inset, y, zt), (x0 + inset, y, zt)]
    kit27.sharp_loft(a.part('Cab', 'Team'), [cab_ring(-2.56, 1.84, .05), cab_ring(-2.14, 2.44, .15), cab_ring(-.5, 2.44, .15),
                                cab_ring(-.36, 2.32, .1)], chamfer=.04)
    zr = 2.44
    cab_front = ((-2.56, 1.84), (-2.14, zr))
    gy, gz, grot = _glacis(*cab_front, .62, .012)
    glass = a.part('Vision_blocks', 'Glass')
    for dx in (-.17, 0, .17):
        glass.box((.13, .07, .06), loc=(.95 + dx, gy, gz), rot=(grot, 0, 0), bevel=0)
    glass.box((.3, .07, .08), loc=(.25, gy, gz), rot=(grot, 0, 0), bevel=0)
    for dy in (-1.7, -1.1):                                                                   # side vision blocks
        glass.box((.05, .2, .08), loc=(x1 - .085, dy, 2.18), rot=(0, -.17, 0), bevel=0)
    armor.box((.06, .7, .6), loc=(x1 - .06, -1.3, 1.92), rot=(0, -.17, 0), bevel=0)            # side door
    steel.box((.05, .16, .04), loc=(x1 - .02, -1.05, 1.9), bevel=0)
    _hatch(a, .3, -.85, zr, .25)
    _hatch(a, 1.05, -.85, zr, .23, hinge=-1)
    _periscopes(a, [(.3, -1.95, zr - .01, 0), (1.05, -1.95, zr - .01, 0), (1.25, -1.3, zr - .01, -R90)])
    for x in (.05, 1.3):                                                                      # warning beacons
        _beacon(a, x, -.55, zr - .01, mat='TeamGlow', r=.085)
    lights = a.part('Light_housing', 'Armor')
    for x in (.25, 1.15):                                                                      # work lights
        lights.box((.2, .12, .15), loc=(x, -2.16, zr + .06), bevel=0)
        a.part('Lamps', 'Lamp').box((.15, .03, .1), loc=(x, -2.225, zr + .06), bevel=0)
    for k in range(3):                                                                         # smoke dischargers
        steel.cyl(.045, .16, loc=(1.3 - k * .09, -2.28, 2.36), rot=(.6, 0, .5), seg=8, bevel=0)
        steel.cyl(.045, .16, loc=(.07 + k * .09, -2.28, 2.36), rot=(.6, 0, -.5), seg=8, bevel=0)
    _antenna(a, None, 1.25, -.5, zr - .01, 1.3)
    _rws_mg(a, (.68, -1.45, zr + .01))
    steel.cyl(.33, .05, loc=(.68, -1.45, zr + .005), seg=14, bevel=0)                          # RWS race

    # Glacis: headlights, tow hooks, spare track links on the right.
    for s in (-1, 1):
        gy, gz, grot = _glacis(front, back, .3, .02)
        _headlight(a, s * 1.18, gy - .02, gz + .08, guard=False)
        steel.box((.16, .2, .14), loc=(s * .5, -3.66, .86), bevel=.02, seg=1)
    gy, gz, grot = _glacis(front, back, .55, 0)
    _track_links(a, _frame((-.62, gy, gz), (grot, 0, 0)), 3, width=.46)
    _track_links(a, _frame((.72, gy, gz), (grot, 0, 0)), 2, width=.46)

    # Dozer blade: a wide concave moldboard raised for travel, cutting edge and top lip, end plates and
    # back ribs, push arms into the lower hull and two lift rams from the glacis; hazard band on top.
    by = .1                                                                 # blade profile authored 10 cm forward
    blade = [(y + by, z) for y, z in ((-4.18, .24), (-4.08, .44), (-4.03, .68), (-4.03, .98), (-4.08, 1.18),
                                      (-4.16, 1.3), (-4.06, 1.32), (-3.98, 1.18), (-3.94, .98), (-3.94, .68),
                                      (-3.98, .44), (-4.08, .24))]
    kit27.extrude(a.part('Blade', 'Team'), blade, 3.6, axis='X', chamfer=.03)
    steel.box((3.62, .12, .08), loc=(0, -4.16 + by, .26), rot=(.5, 0, 0), bevel=0)             # cutting edge
    steel.box((3.62, .12, .05), loc=(0, -4.1 + by, 1.31), bevel=0)                              # top lip
    for s in (-1, 1):
        armor.prism([(y + by, z) for y, z in ((-4.21, .22), (-4.12, 1.34), (-3.92, 1.3), (-3.92, .28))], .06,
                    loc=(s * 1.81, 0, 0), bevel=0)                                              # end plates
    for x in (-1.4, -.7, 0, .7, 1.4):                                                           # back ribs
        armor.prism([(y + by, z) for y, z in ((-3.96, .3), (-3.93, .6), (-3.92, .96), (-3.96, 1.2), (-3.8, 1.12),
                                              (-3.78, .4))], .07, loc=(x, 0, 0), bevel=0)
    for s in (-1, 1):
        armor.limb((s * .95, -3.84 + by, .5), (s * .95, -3.3, .64), .16, .18, bevel=0)          # push arms
        armor.box((.24, .3, .3), loc=(s * .95, -3.3, .66), bevel=.02, seg=1)
        _ram(a, (s * .5, -3.25, 1.3), (s * .5, -3.86 + by, 1.1), .07)                         # lift rams
        armor.box((.14, .2, .14), loc=(s * .5, -3.2, 1.33), bevel=0)
    _stripes(a, _plane((0, -4.1 + by, 1.16), (1, 0, 0), (0, .25, 1)), 3.5, .2, pitch=.4)

    # Excavator arm folded along the right side: slewing base at the front right, a bent boom rising back
    # to the elbow on an A-frame rest, the stick folded down behind it and the bucket curled in on the rear
    # deck; boom, stick and bucket rams and hoses.
    ax = -.88
    steel.cyl(.5, .1, loc=(ax, -1.95, 1.64), seg=16, bevel=.02, bseg=1)
    arm = a.part('Arm', 'Team')
    arm.box((.78, .7, .42), loc=(ax, -1.9, 1.88), bevel=.04, seg=1, taper=(.85, .9))            # slewing housing
    for s in (-1, 1):
        armor.box((.06, .42, .36), loc=(ax + s * .2, -1.9, 2.12), bevel=0)                        # foot cheeks
    steel.cyl(.07, .5, loc=(ax, -1.95, 2.18), rot=ACROSS, seg=8, bevel=0)                      # foot pin
    F, K, E = Vector((ax, -1.95, 2.18)), Vector((ax, -.35, 2.92)), Vector((ax, 1.3, 2.88))
    S = Vector((ax, 2.5, 2.32))
    arm.limb(tuple(F), tuple(K), .3, .38, bevel=.03, seg=1)                                     # boom
    arm.limb(tuple(K + Vector((0, -.08, -.02))), tuple(E), .28, .34, bevel=.03, seg=1)
    arm.limb(tuple(E + Vector((0, -.05, .02))), tuple(S), .22, .28, bevel=.025, seg=1)           # stick
    lever = E + Vector((0, -.12, .3))
    armor.limb(tuple(E), tuple(lever), .24, .16, bevel=0)                                        # stick lever
    steel.cyl(.07, .4, loc=E, rot=ACROSS, seg=8, bevel=0)                                        # elbow pin
    steel.cyl(.05, .34, loc=lever, rot=ACROSS, seg=8, bevel=0)
    _bucket(a, ax, S.y, S.z, f=-1)
    for s in (-1, 1):
        _ram(a, (ax + s * .22, -1.55, 1.98), (ax + s * .22, -.9, 2.5), .065)                     # boom rams
    _ram(a, (ax, -.55, 3.08), tuple(lever), .06)                                                 # stick ram
    _ram(a, (ax, 1.45, 3.02), (ax, 2.35, 2.52), .05)                                             # bucket ram
    armor.box((.3, .3, .12), loc=(ax, -.55, 3.04), bevel=0)                                      # ram lug
    hoses = a.part('Hoses', 'Rubber')
    for dx in (-.17, .17):
        hoses.tube([(ax + dx, -1.7, 2.3), (ax + dx, -.35, 3.06), (ax + dx, 1.2, 3.02), (ax + dx, 2.3, 2.46)], .022,
                   seg=4)
    for dx in (-.24, .24):                                                                       # A-frame rest
        armor.limb((ax + dx * 1.4, .45, 1.6), (ax + dx * .5, .45, 2.66), .07, .07, bevel=0)
    armor.box((.4, .16, .06), loc=(ax, .45, 2.68), bevel=0)
    _stripes(a, _plane(K + Vector((0, .5, .17)), (0, 1, -.02), (1, 0, 0)), .9, .3, pitch=.2, lean=.6)

    # Rear deck: welding kit (gas bottles in a rack, a welder box with cable reels) behind the cab, a small
    # jib crane with a hook at the left rear, engine grilles, the recovery winch and tool boxes.
    for x, mat in ((.35, 'Fuel'), (.6, 'Fuel'), (.85, 'BarrelRed')):
        a.part(f'Gas_bottles_{mat}', mat).lathe([(.11, 1.6), (.11, 2.28), (.075, 2.37), (.035, 2.41), (.035, 2.45)],
                                                loc=(x, -.12, 0), seg=8)
        steel.cyl(.045, .06, loc=(x, -.12, 2.47), seg=6, bevel=0)
    for z in (1.85, 2.15):
        steel.box((.78, .03, .05), loc=(.6, -.005, z), bevel=0)
    for x in (.18, 1.02):
        steel.box((.04, .28, .7), loc=(x, -.12, 1.95), bevel=0)
    armor.box((.62, .52, .44), loc=(.72, .62, 1.84), bevel=.03, seg=1)                          # welder
    a.part('Welder_panel', 'Glass').box((.3, .02, .12), loc=(.72, .355, 1.92), bevel=0)
    for dx in (-.16, .16):
        a.part('Cable_reels', 'Rubber').cyl(.15, .12, loc=(.72 + dx, .98, 1.8), rot=ACROSS, seg=10, bevel=0)
    steel.cyl(.04, .44, loc=(.72, .98, 1.8), rot=ACROSS, seg=6, bevel=0)
    a.part('Hoses', 'Rubber').tube([(.72, .36, 1.7), (.6, .1, 1.66), (.5, -.1, 1.66), (.4, -.12, 1.72)], .02,
                                   seg=4)
    for x in (.1, .85):
        deck.grille(.66, .8, loc=(x, 2.05, 1.64), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        _grille_frame(a, x, 2.05, 1.62, .66, .8, t=.04)
    wx, wy = .2, 2.95
    armor.box((1.0, .6, .1), loc=(wx, wy, 1.64), bevel=0)
    for s in (-1, 1):
        armor.box((.08, .5, .5), loc=(wx + s * .46, wy, 1.9), bevel=0)
    a.part('Winch_drum', 'Steel').cyl(.22, .76, loc=(wx, wy, 1.92), rot=ACROSS, seg=12, bevel=0)
    for dx in (-.38, .38):
        a.part('Winch_flanges', 'Armor').cyl(.28, .04, loc=(wx + dx, wy, 1.92), rot=ACROSS, seg=12, bevel=0)
    steel.box((.5, .16, .16), loc=(wx, 3.44, 1.36), bevel=0)                                   # fairlead
    _cable(a, [(wx, wy + .12, 1.72), (wx, 3.4, 1.46), (wx, 3.52, 1.3), (wx, 3.56, 1.1)], r=.028)
    # Jib crane on the left rear corner: post, jib and a hook block on its cable.
    cx, cy = 1.05, 2.9
    crane = a.part('Crane', 'Hazard')
    steel.cyl(.14, .1, loc=(cx, cy, 1.66), seg=10, bevel=0)
    crane.cyl(.09, .9, loc=(cx, cy, 2.1), seg=10, bevel=0)                                     # post
    tipc = Vector((cx + .3, cy + .55, 2.62))
    crane.limb((cx, cy - .05, 2.5), tuple(tipc), .12, .14, bevel=0)                               # jib
    _ram(a, (cx, cy + .02, 1.9), (cx + .17, cy + .36, 2.47), .04)
    steel.cyl(.07, .1, loc=tipc + Vector((0, 0, -.06)), rot=ACROSS, seg=8, bevel=0)             # sheave
    _rod(steel, tipc + Vector((0, .04, -.1)), tipc + Vector((0, .04, -.62)), .012, seg=4)
    a.part('Hook_block', 'Hazard').box((.14, .1, .14), loc=tipc + Vector((0, .04, -.68)), bevel=0)
    steel.torus(.05, .014, loc=tipc + Vector((0, .04, -.8)), rot=(0, R90, 0), seg=8, ring=4)
    _beacon(a, cx, cy, 2.55, mat='TeamGlow', r=.07)
    # Lane-marking dispensers at the rear corners.
    for x in (-1.22, 1.3):
        a.part('Lane_markers', 'Hazard').cyl(.1, .42, loc=(x, 3.28, 1.8), seg=10, bevel=0)
        for dx in (-.04, .04):
            steel.cyl(.012, .5, loc=(x + dx, 3.28, 2.2), seg=4, bevel=0)
    # Right side: a tool box in front of the bucket and a tool chest; left edge: jerrycans, shovel and pick;
    # tow cables.
    _stowage_bin(a, (-1.12, 1.2, 1.61), (.34, .8, .3), latch_side=-1)
    a.part('Tool_chest', 'Crate').box((.52, .62, .34), loc=(-.28, 1.1, 1.78), bevel=.02, seg=1)
    steel.box((.3, .04, .04), loc=(-.28, .78, 1.88), bevel=0)
    _jerrycans(a, (1.2, 1.25, 1.61), 3)
    _shovel(a, (1.2, .1, 1.64), length=1.0)
    _pick(a, (-1.2, -.2, 1.645), length=.9)
    for s in (-1, 1):
        _cable(a, [(s * 1.3, -2.3, 1.645), (s * 1.3, -.5, 1.645), (s * 1.3, .6, 1.645)])
        _taillight(a, s * 1.2, 3.48, 1.3)
        steel.box((.16, .2, .14), loc=(s * .75, 3.54, .82), bevel=.02, seg=1)                  # rear tow hooks
        _exhaust(a, s * .7, 3.48, 1.02, .34, .2)
    # Spare track links on the rear plate.
    _track_links(a, _frame((0, 3.5, 1.02), (-R90, 0, 0)), 3, width=.42)
    kit27.clean(a)


UNITS4['sapper'] = sapper
_OPT4['sapper'] = mb_new_tracked.BUILDERS['sapper'][1]


def fpv_drone(a):
    """FPV kamikaze quadcopter (flies along -Y, origin at its centre), 0.69 m prop tip to prop tip across the
    diagonal: the old frame, motors, props and RPG-7 charge, plus a speed-controller board, and motor wires (pass 8a4)."""
    carbon = a.part('Drone_frame', 'Undercarriage')
    steel = a.part('Drone_motors', 'Steel')
    bells = a.part('Drone_bells', 'Armor')
    props = a.part('Drone_props', 'BarrelRed')
    alloy = a.part('Drone_standoffs', 'Alloy')
    # Bottom plate and four tapered arms (true X), motor mounts at their tips.
    carbon.box((.1, .15, .006), loc=(0, 0, .006), bevel=0)
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        ang = math.atan2(sy, sx)
        mid = Vector((sx * .08, sy * .08, .007))
        carbon.box((.2, .036, .007), loc=tuple(mid), rot=(0, 0, ang), bevel=0, taper=(1, .75))
        carbon.cyl(.022, .007, loc=(sx * .16, sy * .16, .007), seg=8, bevel=0)                   # motor mount
        # Motor: stator base, bell, shaft and prop nut.
        bells.cyl(.023, .012, loc=(sx * .16, sy * .16, .017), seg=8, bevel=0)
        steel.cyl(.024, .02, loc=(sx * .16, sy * .16, .033), seg=10, bevel=0)
        steel.cyl(.005, .016, loc=(sx * .16, sy * .16, .05), seg=6, bevel=0)
        bells.cyl(.008, .008, loc=(sx * .16, sy * .16, .058), seg=6, bevel=0)
        # Tri-blade prop, each blade tapered and pitched, spun a little differently on each motor.
        props.cyl(.012, .008, loc=(sx * .16, sy * .16, .052), seg=6, bevel=0)
        for k in range(3):
            phi = i * .7 + k * TAU / 3
            c = Vector((sx * .16, sy * .16, .053)) + Vector((math.cos(phi), math.sin(phi), 0)) * .066
            props.box((.12, .024, .004), loc=tuple(c), rot=(.22 * (1 if (sx * sy) > 0 else -1), 0, phi), bevel=0,
                      taper=(.55, .7))
    # Top plate on four alloy standoffs; the flight stack between the plates.
    for sx in (-1, 1):
        for sy in (-1, 1):
            alloy.cyl(.005, .03, loc=(sx * .032, sy * .045, .025), seg=6, bevel=0)
    carbon.box((.078, .118, .005), loc=(0, 0, .042), bevel=0)
    a.part('Drone_stack', 'Rubber').box((.05, .05, .018), loc=(0, .01, .022), bevel=0)
    # Battery strapped on top, its lead and plug hanging off the back.
    a.part('Drone_battery', 'Team').box((.066, .12, .034), loc=(0, .01, .063), bevel=.005, seg=1)
    straps = a.part('Drone_straps', 'Rubber')
    for y in (-.02, .045):
        straps.box((.072, .014, .042), loc=(0, y, .063), bevel=0)
    a.part('Drone_plug', 'Hazard').box((.018, .02, .012), loc=(0, .082, .05), bevel=0)
    # Camera pod at the nose: a printed mount with side plates, the camera tilted 25 degrees up, its lens.
    pod = a.part('Drone_pod', 'Armor')
    tilt = (-.44, 0, 0)
    pod.box((.044, .04, .036), loc=(0, -.078, .03), rot=tilt, bevel=.004, seg=1)
    for sx in (-1, 1):
        carbon.box((.004, .05, .04), loc=(sx * .026, -.07, .028), bevel=0)
    lens_at = Vector((0, -.078, .03)) + Matrix.Rotation(-.44, 3, 'X') @ Vector((0, -.027, 0))
    pod.cyl(.013, .016, loc=tuple(lens_at), rot=(R90 - .44, 0, 0), seg=10, bevel=0)
    a.part('Drone_lens', 'Glass').cyl(.009, .006, loc=tuple(lens_at + Matrix.Rotation(-.44, 3, 'X') @ Vector((0, -.009, 0))),
                                      rot=(R90 - .44, 0, 0), seg=10, bevel=0)
    # Video antenna (a stubby pagoda on a mast) at the back, two receiver whips in a V.
    loc, rot, length = _seg((0, .07, .046), (0, .1, .1))
    steel.cyl(.003, length, loc=loc, rot=rot, seg=5, bevel=0)
    a.part('Drone_antenna', 'Rubber').cyl(.012, .016, loc=(0, .103, .106), rot=(-.5, 0, 0), seg=8, bevel=0)
    for sx in (-1, 1):
        loc, rot, length = _seg((sx * .03, .06, .045), (sx * .07, .12, .07))
        a.part('Drone_whips', 'Undercarriage').cyl(.002, length, loc=loc, rot=rot, seg=4, bevel=0)
    a.part('Drone_led', 'TeamGlow').box((.04, .006, .008), loc=(0, .077, .012), bevel=0)
    # The RPG-7 warhead slung under the nose along -Y: booster, band, body, ogive and piezo fuse, zip-tied on.
    charge = a.part('Drone_charge', 'Armor')
    profile = [(.022, .16), (.03, .12), (.03, .06), (.044, .03), (.046, -.03), (.04, -.08), (.028, -.12), (.012, -.15),
               (.004, -.16)]
    charge.lathe([(r, -z) for r, z in reversed(profile)], loc=(0, -.035, -.03), rot=FORWARD, seg=10)
    a.part('Drone_band', 'Hazard').cyl(.047, .018, loc=(0, -.055, -.03), rot=FORWARD, seg=10, bevel=0)
    steel.cyl(.007, .03, loc=(0, -.2, -.03), rot=FORWARD, seg=6, bevel=0)                          # fuse
    fins = a.part('Drone_fins', 'Undercarriage')
    for k in range(4):
        phi = k * R90 + math.pi / 4
        fins.box((.003, .03, .02), loc=(math.cos(phi) * .026, .12, -.03 + math.sin(phi) * .026), rot=(0, -phi, 0), bevel=0)
    for y in (-.02, .04):
        straps.box((.06, .008, .03), loc=(0, y, -.008), bevel=0)
    # Speed-controller board between the plates, motor wires along the arms.
    a.part('Drone_plug', 'Hazard').box((.06, .07, .004), loc=(0, .0, .033), bevel=0)
    wires = straps
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        wires.tube([(sx * .02, sy * .02, .036), (sx * .15, sy * .15, .022)], .003, seg=3)
    kit27.clean(a)


# ----------------------------------------------------------------------------- bunker emplacement


UNITS4['fpv_drone'] = fpv_drone
_OPT4['fpv_drone'] = mb_pt5_models.BUILDERS['fpv_drone'][1]


def bug_satellite(a):
    """A small military recon satellite, about 5 m across: a bus, two solar wings, a dish and a rod
    magazine. Origin at its centre; it flies."""
    kit27.block(a.part('Bus', 'Armor'), (.9, 1.1, 1.5), loc=(0, 0, 0), chamfer=.06, ends=(True, True))
    kit27.block(a.part('Bus_band', 'Team'), (.94, .2, 1.54), loc=(0, 0, .1), chamfer=.03, ends=(True, True))
    a.part('Panels', 'Steel').box((.7, .9, .06), loc=(0, 0, .78), bevel=.02, seg=1)
    rivet = a.part('Rivets', 'MetalSheet')
    for sx in (-1, 1):
        for sz in (-.55, -.15, .3, .65):
            rivet.cyl(.025, .02, loc=(sx * .47, .3, sz), rot=(0, R90, 0), seg=5, bevel=0)
            rivet.cyl(.025, .02, loc=(sx * .47, -.3, sz), rot=(0, R90, 0), seg=5, bevel=0)
    thr = a.part('Rcs', 'Armor')
    glow = a.part('Rcs_glow', 'TeamGlow')
    for sx in (-1, 1):
        for sy in (-1, 1):
            thr.cyl(.08, .18, loc=(sx * .46, sy * .56, -.7), rot=(0, R90, 0), seg=8, bevel=.01, bseg=1)
            glow.cyl(.05, .02, loc=(sx * .56, sy * .56, -.7), rot=(0, R90, 0), seg=8, bevel=0)
    wing = a.part('Solar_wing', 'Glass')
    frame = a.part('Solar_frame', 'Steel')
    cell = a.part('Solar_cell', 'Steel')
    for sx in (-1, 1):
        wing.box((1.9, .85, .03), loc=(sx * 1.55, 0, 0), bevel=0, seg=1)
        frame.box((1.95, .06, .05), loc=(sx * 1.55, .42, .03), bevel=0, seg=1)
        frame.box((1.95, .06, .05), loc=(sx * 1.55, -.42, .03), bevel=0, seg=1)
        frame.box((.1, .9, .1), loc=(sx * .58, 0, 0), bevel=.02, seg=1)
        for i in range(7):
            cell.box((.02, .74, .01), loc=(sx * (.65 + i * .25), 0, .022), bevel=0, seg=1)
    a.part('Sensor_boom', 'Steel').cyl(.03, .9, loc=(0, .3, 1.2), rot=FORWARD, seg=6, bevel=0)
    kit27.block(a.part('Sensor_head', 'Glass'), (.14, .14, .14), loc=(0, -.15, 1.2), chamfer=.02, ends=(True, True))
    a.part('Dish_arm', 'Steel').cyl(.05, .5, loc=(0, -.65, .5), rot=FORWARD, seg=8, bevel=0)
    a.part('Dish', 'Medical').sphere((.4, .4, .18), loc=(0, -.95, .68), rot=FORWARD, seg=18, rings=10, cut=.5)
    a.part('Dish_feed', 'Steel').cyl(.03, .16, loc=(0, -.87, .68), rot=FORWARD, seg=8, bevel=0)
    mag = a.part('Rod_magazine', 'Gilded')
    mag.cyl(.22, 1.6, loc=(0, .3, -.95), rot=(0, R90, 0), seg=10, bevel=.03, bseg=1)
    tips = a.part('Rod_tips', 'Steel')
    for i in range(6):
        tips.cyl(.05, .12, loc=(-.75 + i * .3, .3, -.95), rot=(0, R90, 0), seg=6, bevel=0)
    a.part('Antenna', 'Steel').cyl(.02, .9, loc=(.2, .3, .95), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(.2, .3, 1.42), seg=6, rings=4)
    # Wing hinge brackets and diagonal ribs, a star tracker on the roof and a bus thermal-blanket seam.
    for sx in (-1, 1):
        frame.box((.12, .3, .16), loc=(sx * .5, 0, .0), bevel=0)
        frame.limb((sx * .65, -.42, .03), (sx * 2.45, .42, .03), .03, .03, bevel=0)
    a.part('Star_tracker', 'Glass').box((.18, .18, .12), loc=(-.22, -.3, .84), bevel=0)
    a.part('Bus_blanket', 'Gilded').box((.92, .5, .04), loc=(0, .2, .6), bevel=0)
    kit27.clean(a)


UNITS4['bug_satellite'] = bug_satellite
_OPT4['bug_satellite'] = mb_orbital.BUILDERS['bug_satellite'][1]


def _c130_v2(a, detail=False, ramp_open=False):
    """The shared four-turboprop transport airframe (C-130 class) of the drone mothership and the AC-130, 11.9 x
    16.2 x 4.6 m: a round fuselage with a radome nose and a band of flight-deck windows, gear sponsons, a high
    straight wing on a root fairing, four nacelles slung under it with four-blade `Propeller`..`Propeller_4` (drawn
    10 % large: with the long straight wing they are the silhouette), an upswept tail with a tall fin (10 % tall)
    and the tailplane. ramp_open lowers the cargo ramp under the tail and shows the dark hold above it. Origin at
    the fuselage centre (it flies). Returns the wing planform."""
    from mb_air import LEFT, RIGHT, Planform, _dome, _sec, _surface, _upright
    hd.mark(a, detail)
    n = 14 if detail else 12
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    dark = a.part('Undercarriage', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Wing_lights', 'TeamGlow')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=n, pt=2.4, pb=3.2)
    hull = [sec(-5.78, .36, -.46, .16), sec(-5.4, .7, -.78, .5), sec(-4.85, .86, -.9, .8), sec(2.5, .86, -.9, .82),
            sec(3.45, .84, -.56, .82), sec(4.7, .56, .1, .8), sec(5.75, .2, .48, .72)]
    body.loft([[(0, -5.96, -.16)]] + hull + [[(0, 5.96, .62)]], bevel=.02 if detail else 0, seg=1)
    armor.loft([[(0, -5.97, -.16)], sec(-5.9, .2, -.34, .04), sec(-5.72, .4, -.52, .22)], bevel=0)   # radome
    # Flight-deck windows: a glass band round the top of the nose, framed by the skin either side.
    a.part('Canopy', 'Glass').loft([_dome(y, w, z0, z1, 7) for y, w, z0, z1 in
                                    ((-5.52, .5, .12, .38), (-5.25, .74, .3, .62), (-4.95, .8, .42, .78))], bevel=0)
    for s in (-1, 1):                                                                            # gear sponsons
        kit27.block(armor, (.42, 2.8, .6), loc=(s * .78, -.3, -.74), chamfer=.06, taper=(.75, .95), ends=(True, True))
        steel.box((.24, .7, .2), loc=(s * .8, -.2, -1.0), bevel=0)                               # stowed wheels
    # High straight wing on its root fairing.
    w = C130_WING
    wing = Planform(0, w['span'], w['root_le'], w['tip_le'], w['root_c'], w['tip_c'], .36, .15, w['z'], w['z'] + .08)
    body.box((1.3, 2.4, .34), loc=(0, w['root_le'] + 1.05, .86), bevel=.06, seg=1, taper=(.8, .92))
    for frame in (RIGHT, LEFT):
        _surface(body, wing, frame, bevel=.012 if detail else 0)
    for s in (-1, 1):
        glow.box((.1, .22, .08), loc=(s * (w['span'] + .02), wing.le(w['span']) + .3, wing.at(w['span'])[3]), bevel=0)
    # Nacelles under the wing, the turboprops at their fronts.
    for x, name in C130_ENGINES:
        le = wing.le(abs(x))
        zc = wing.bottom(abs(x)) - .12
        nac = [(le - 1.15, .19, .2), (le - .75, .25, .27), (le + .3, .24, .27), (le + 1.4, .16, .16), (le + 2.1, .07, .08)]
        rings = [[(x + px, y, zc + pz) for px, _, pz in _sec(0, hw, -hh, hh, n=8 if not detail else 10, pt=2.2, pb=2.2)]
                 for y, hw, hh in nac]
        body.loft(rings + [[(x, le + 2.35, zc)]], bevel=0)
        armor.cyl(.2, .06, loc=(x, le - 1.17, zc), rot=(R90, 0, 0), seg=10, bevel=0)             # intake ring
        dark.box((.16, .12, .06), loc=(x, le - 1.1, zc - .17), bevel=0)                         # oil-cooler scoop
        dark.cyl(.06, .3, loc=(x + (.2 if x > 0 else -.2), le + .1, zc + .05), rot=(R90, 0, 0), seg=6, bevel=0)  # exhaust
        p = a.pivot(name, (x, le - 1.28, zc))
        spinner = a.part('Spinners', 'Armor', p)
        spinner.cyl(.12, .3, r2=.03, loc=(0, -.06, 0), rot=(R90, 0, 0), seg=8, bevel=0)
        blades = a.part('Prop_blades', 'Undercarriage', p)
        for k in range(4):
            u = k * math.tau / 4 + .4
            blades.box((.17, .05, .82), loc=(math.cos(u) * .5, .04, math.sin(u) * .5), rot=(0, -u + R90, 0), bevel=0,
                       taper=(.7, 1))
    # Upswept tail: the tall fin (10 % tall) and the tailplane.
    fin = Planform(0, 2.75, 3.3, 4.85, 2.35, 1.1, .3, .12)
    _surface(body, fin, _upright(0, .74, 0), lower=1.0, bevel=.012 if detail else 0)
    stab = Planform(.15, 3.1, 4.25, 4.95, 1.45, .7, .18, .08, .74, .8)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame, bevel=.012 if detail else 0)
    a.part('Beacon', 'TeamGlow').sphere(.09, loc=(0, 4.85 + 1.0, .74 + 2.76), seg=6, rings=4)
    if ramp_open:
        # Cargo ramp lowered under the upswept tail, the dark hold above it, the upper door raised inside.
        dark.box((1.3, 2.1, .3), loc=(0, 3.8, -.36), rot=(.49, 0, 0), bevel=0)
        ramp = a.part('Ramp', 'Armor')
        ramp.box((1.3, 1.8, .08), loc=(0, RAMP[0] + .9, RAMP[1] - .9 * RAMP[2] - .04), rot=(-RAMP[3], 0, 0), bevel=.02,
                 seg=1)
        steel.box((1.1, .1, .06), loc=(0, RAMP[0] + 1.8, RAMP[1] - 1.8 * RAMP[2] - .03), rot=(-RAMP[3], 0, 0),
                  bevel=0)                                                                     # ramp toe
        for sx in (-1, 1):
            steel.box((.06, 1.7, .08), loc=(sx * .5, RAMP[0] + .9, RAMP[1] - .9 * RAMP[2] + .02),
                      rot=(-RAMP[3], 0, 0), bevel=0)                                           # drone rails
    else:
        armor.box((1.2, 1.9, .05), loc=(0, 4.05, -.33), rot=(-.36, 0, 0), bevel=0)             # ramp outline
    # Paratroop doors and cargo-door seams on the fuselage, a spine antenna fairing with two blade antennas, wing-root
    # fairing seams and landing-gear door lines (pass 8a4).
    for s in (-1, 1):
        armor.box((.03, .95, 1.2), loc=(s * .862, 1.35, .05), bevel=0)
        steel.box((.04, .06, .1), loc=(s * .868, 1.0, .1), bevel=0)
        dark.box((.03, 1.7, .05), loc=(s * .805, -.3, -.98), bevel=0)
        armor.box((.03, .4, .22), loc=(s * .35, -4.1, .86), bevel=0)
    armor.box((.26, .7, .14), loc=(0, -2.2, .9), bevel=.02, seg=1)
    for y in (-2.6, 2.0):
        steel.box((.03, .24, .22), loc=(0, y, .98), bevel=0)
    for y in (-3.4, -.2, 3.0):
        dark.box((1.5, .03, .03), loc=(0, y, .62), bevel=0)
    a.pivot('Point_exhaust', (C130_ENGINES[0][0], wing.le(3.96) + .3, wing.bottom(3.96) - .07))
    a.pivot('Point_fire', (0, -.2, .95))
    kit27.clean(a)
    return wing


def transport_plane(a):
    """Airdrop transport (C-130 class), the shared four-turboprop airframe at its pass 8a4 rebuild: chamfered gear
    sponsons, paratroop doors, a spine antenna fairing and panel seams on top of the old fuselage, wing, nacelles,
    `Propeller` .. `Propeller_4`, tail and ramp (shut)."""
    _c130_v2(a)


UNITS4['transport_plane'] = transport_plane
_OPT4['transport_plane'] = m2.BUILDERS['transport_plane'][1]


def icbm(a):
    """The nuke train's missile as a projectile (nose at -Y, origin at its centre) with a glowing motor in the
    nozzle, on finer rings (16 sides) since it is seen big on its way up."""
    _icbm(a, None, seg=16, detail=False)
    h = ICBM_LENGTH / 2
    a.part('Motor', 'Alloy').cyl(.3, .04, loc=(0, h + .03, 0), rot=FORWARD, seg=12, bevel=0)
    kit27.clean(a)


UNITS4['icbm'] = icbm
_OPT4['icbm'] = mb_air3.BUILDERS['icbm'][1]


def heavy_attack_heli(a):
    """Coaxial-rotor attack helicopter (Ka-52 "Alligator" lineage), 15.8 m over the rotors: a radar
    nose, a wide side-by-side cockpit under a framed canopy with big bulged side windows, engine
    nacelles with dust-filter caps and outward exhausts high on the sides, a tall coaxial mast with
    two stacked three-blade rotors, stub wings with a rocket pod and an anti-tank missile pack each and
    countermeasure pods with twin Igla launchers at the tips, the 30 mm cannon on the right side, a
    long boom ending in a stabiliser with twin end-plate fins and a small central fin, and tricycle
    wheels. Origin on the ground under the cabin (wheels on z = 0). Pass 8a4: sharp-edged lofts and blocks, the library
    rotor heads, chaff and antenna details."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    hull = [
        _octagon(-7.85, .26, 1.5, 1.94),
        _octagon(-7.45, .46, 1.32, 2.04),
        _octagon(-7.0, .62, 1.2, 2.14),
        _octagon(-6.4, .8, 1.06, 2.22),
        _octagon(-5.6, .96, .98, 2.27),
        _octagon(-4.2, 1.03, .96, 2.32),
        _octagon(-3.0, 1.03, .98, 2.62),
        _octagon(-.8, .98, 1.02, 2.76),
        _octagon(1.0, .82, 1.15, 2.7),
        _octagon(2.4, .52, 1.55, 2.56),
    ]
    kit27.sharp_loft(body, [[(0, -8.12, 1.72)]] + hull, chamfer=.05)                                      # radar nose
    boom = [_octagon(2.2, .52, 1.58, 2.56), _octagon(5.4, .34, 1.86, 2.4), _octagon(7.0, .2, 1.98, 2.3)]
    kit27.sharp_loft(body, boom + [[(0, 7.35, 2.14)]], chamfer=.04)
    armor.lathe([(0, -8.16), (.1, -8.08), (.22, -7.9), (.27, -7.78)], loc=(0, 0, 1.72), rot=BACKWARD, seg=10)  # radome cap
    # Side-by-side cockpit: a framed canopy wider than the fuselage, bulged side windows, a centre post.
    st = [(-6.78, .52, 1.95, 2.24), (-6.25, .86, 1.88, 2.86), (-5.3, 1.0, 1.88, 3.06), (-4.3, 1.05, 1.9, 3.03),
          (-3.82, .94, 1.94, 2.8)]
    glass.loft([_bubble(y, w, z0, z1) for y, w, z0, z1 in st], bevel=.02, seg=1)
    secs = [_bubble(y, w + .012, z0, z1 + .012) for y, w, z0, z1 in st]
    for sec in secs[1:4]:
        _hoop(frames, sec, r=.035)
    for i in (2, 3, 4, 5):                                                                       # canopy rails
        frames.tube([tuple(Vector(q[i]) + Vector((0, 0, .01))) for q in secs[1:]], .03, seg=5)
    frames.tube([(0, -6.3, 2.88), (0, -5.3, 3.08), (0, -4.3, 3.05)], .035, seg=5)                 # centre spine
    for s in (-1, 1):
        frames.tube([(s * 1.02, -5.25, 1.93), (s * .98, -5.1, 2.9)], .03, seg=5)                  # door frames
        armor.box((.05, 1.3, .36), loc=(s * 1.03, -4.9, 1.62), bevel=.012, seg=1)                 # cockpit armour
        steel.bolts([(s * 1.06, y, z) for y in (-5.45, -4.35) for z in (1.5, 1.74)], r=.03, h=.03, rot=ACROSS,
                    seg=6, bevel=0)
    # Cheek sensor ball under the nose; air-data boom; lamps.
    armor.cyl(.1, .2, loc=(0, -6.55, 1.02), seg=8, bevel=0)
    armor.sphere(.3, loc=(0, -6.55, .86), seg=12, rings=8)
    sensor = a.part('Sensor', 'Glass')
    sensor.cyl(.14, .05, loc=(0, -6.83, .86), rot=FORWARD, seg=10, bevel=0)
    sensor.cyl(.06, .05, loc=(.17, -6.79, .96), rot=FORWARD, seg=8, bevel=0)
    steel.tube([(.3, -7.5, 1.96), (.32, -8.1, 2.0), (.33, -8.6, 2.02)], .025, seg=6)              # air-data boom
    a.part('Lamps', 'Lamp').box((.22, .15, .06), loc=(0, -5.0, .95), bevel=.01, seg=1)
    # Engine deck: nacelles on the upper sides, dust-filter caps, outward exhausts; gearbox fairing.
    for s in (-1, 1):
        x = s * 1.02
        body.cyl(.46, 3.3, loc=(x, -1.1, 2.62), rot=FORWARD, seg=14, bevel=.1)
        armor.cyl(.5, .5, loc=(x, -2.85, 2.62), rot=FORWARD, seg=14, bevel=.04, bseg=1)               # filter drum
        armor.sphere((.46, .3, .46), loc=(x, -3.1, 2.62), seg=12, rings=6)                            # filter cap
        dark.grille(.5, .32, loc=(x + s * .49, -2.85, 2.62), rot=(0, 0, s * R90), slats=3, depth=.04, thickness=.03)
        _exhaust_duct(a, (s * 1.38, .85, 2.78), s * -.55, size=(.4, .9, .44), pitch=-.15)
        panels.box((.04, 1.4, .4), loc=(x + s * .44, -1.0, 2.62), bevel=.01, seg=1)                  # cowl doors
    kit27.block(body, (1.2, 3.6, .7), loc=(0, -1.05, 2.95), chamfer=.1, taper=(.7, .82), ends=(True, True))                 # z 2.6 .. 3.3
    armor.cyl(.34, .12, loc=(0, -.95, 3.32), seg=14, bevel=.02, bseg=1)                              # mast base
    steel.cyl(.2, .5, loc=(0, -.95, 3.52), seg=12, bevel=0)                                          # z 3.27 .. 3.77
    steel.cyl(.15, 1.2, loc=(0, -.95, 4.3), seg=10, bevel=0)                                         # inter-rotor mast
    for zz in (3.62, 4.62):
        steel.cyl(.3, .05, loc=(0, -.95, zz), seg=12, bevel=0)                                       # swashplates
        for k in range(3):
            ang = k * math.tau / 3 + .4
            steel.cyl(.02, .2, loc=(math.cos(ang) * .22, -.95 + math.sin(ang) * .22, zz + .12), seg=4, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, .8, _skin_z(hull, .8, 0) + .02), seg=8, rings=5)
    steel.cyl(.015, .8, loc=(-.3, 2.3, 2.95), seg=5, bevel=0)                                        # antennas
    steel.box((.025, .3, .2), loc=(0, -2.6, .92), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    # Tail: stabiliser with twin end-plate fins, a small central fin, tail bumper.
    body.box((3.4, .9, .12), loc=(0, 6.1, 2.28), bevel=.03, seg=1, taper=(1, .7))
    for s in (-1, 1):
        body.prism([(5.62, 1.72), (6.62, 1.82), (6.95, 3.22), (6.35, 3.25)], .1, loc=(s * 1.72, 0, 0), bevel=.025)
        glow.box((.05, .14, .06), loc=(s * 1.78, 6.9, 3.1), bevel=0)
    body.prism([(6.2, 2.3), (7.2, 2.22), (7.35, 3.05), (6.95, 3.08)], .14, bevel=.03)                # central fin
    steel.limb((0, 6.6, 1.9), (0, 6.75, 1.45), .08, .08, bevel=0)                                    # tail bumper
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 7.35, 2.2), seg=8, rings=5)
    for s in (-1, 1):                                                                                # flare dispensers
        armor.box((.1, .6, .24), loc=(s * .44, 3.6, 2.35), bevel=.02, seg=1)
        dark.grille(.5, .22, loc=(s * .5, 3.6, 2.35), rot=(0, 0, s * R90), slats=3, depth=.03, thickness=.03)
    # Stub wings: inner pylon a 20-tube rocket pod, outer a six-round missile pack, a countermeasure pod
    # with twin Igla launchers at each tip.
    pylons = a.part('Pylons', 'Armor')
    tubes = a.part('Launch_tubes', 'Fuel')
    zw = 2.08
    for s in (-1, 1):
        kit27.block(body, (2.75, 1.35, .2), loc=(s * 2.3, -1.2, zw), chamfer=.04, taper=(1, .92), ends=(True, True))
        # Inner: rocket pod.
        x = s * 1.78
        _pylon(pylons, x, -1.75, -.55, zw - .05, zw - .38, w=.14)
        _rocket_pod(a, x, -2.3, zw - .7, .3, 1.95, tubes=9)
        # Outer: missile pack, two rows of three tubes in a frame.
        x = s * 2.82
        _pylon(pylons, x, -1.7, -.6, zw - .05, zw - .3, w=.12)
        armor.box((.62, 1.6, .06), loc=(x, -1.25, zw - .32), bevel=0)                               # launcher beam
        for dx in (-.18, 0, .18):
            for dz in (-.47, -.64):
                tubes.cyl(.085, 2.0, loc=(x + dx, -1.25, zw + dz), rot=FORWARD, seg=8, bevel=.012, bseg=1)
                dark.cyl(.062, .02, loc=(x + dx, -2.255, zw + dz), rot=FORWARD, seg=8, bevel=0)
        for yy in (-1.95, -.6):
            armor.box((.66, .12, .44), loc=(x, yy, zw - .56), bevel=.015, seg=1)                    # frame bands
        a.part('Missile_bands', 'Hazard').box((.67, .06, .45), loc=(x, -1.1, zw - .56), bevel=0)
        # Wingtip: countermeasure pod, its windows, and twin Igla launchers under it.
        x = s * 3.72
        cm = a.part('CM_pods', 'Armor')
        cm.lathe([(0, 0), (.1, .08), (.2, .3), (.2, 1.3), (.14, 1.55), (0, 1.62)], loc=(x, -2.1, zw), rot=BACKWARD,
                 seg=10)
        sensor.box((.05, .14, .1), loc=(x + s * .19, -1.8, zw + .03), bevel=0)
        sensor.box((.05, .14, .1), loc=(x + s * .19, -.72, zw + .03), bevel=0)
        glow.box((.05, .14, .06), loc=(x + s * .18, -1.2, zw + .14), bevel=0)
        pylons.box((.08, .9, .12), loc=(x, -1.3, zw - .22), bevel=0)
        igla = a.part('Igla_tubes', 'Fuel')
        for dx in (-.08, .08):
            igla.cyl(.055, 1.7, loc=(x + dx, -1.35, zw - .34), rot=FORWARD, seg=8, bevel=0)
            dark.cyl(.04, .02, loc=(x + dx, -2.205, zw - .34), rot=FORWARD, seg=8, bevel=0)
        a.part('Igla_bands', 'Hazard').box((.28, .06, .13), loc=(x, -2.0, zw - .34), bevel=0)
    a.pivot('Muzzle_rocket', (0, -2.32, zw - .7))
    a.pivot('Muzzle_missile', (0, -2.27, zw - .555))
    a.pivot('Muzzle_aam', (3.72 - .08, -2.23, zw - .34))
    # The 30 mm cannon on the right (-X) of the fuselage under the wing root, on its own mount.
    armor.box((.3, 1.4, .5), loc=(-1.0, -1.55, 1.45), bevel=.06, seg=1, taper=(.9, .9))            # gun fairing
    g = pivot(a, 'Mount_gun', (-1.18, -1.7, 1.42))
    gm = a.part('Gun_mount', 'Armor', g)
    gm.box((.26, .9, .34), loc=(0, .1, 0), bevel=.04, seg=1)                                         # cradle
    gm.box((.3, .5, .3), loc=(-.1, .4, .02), bevel=.03, seg=1)                                       # ammo box
    gun = a.part('Gun', 'Steel', g)
    gun.box((.18, .9, .2), loc=(0, -.6, 0), bevel=.02, seg=1)                                        # receiver
    gun.cyl(.075, .6, loc=(0, -1.3, 0), rot=FORWARD, seg=10, bevel=0)                                # jacket
    gun.cyl(.05, 2.1, loc=(0, -2.5, 0), rot=FORWARD, seg=8, bevel=0)                                 # barrel
    gun.cyl(.08, .3, loc=(0, -3.6, 0), rot=FORWARD, seg=10, bevel=0)                                 # muzzle brake
    a.part('Gun_bore', 'Undercarriage', g).cyl(.045, .02, loc=(0, -3.755, 0), rot=FORWARD, seg=8, bevel=0)
    pivot(a, 'Muzzle_gun', (0, -3.77, 0), 'Mount_gun')
    # Tricycle gear: twin nose wheels, main wheels on struts from the lower sides.
    gear = a.part('Gear', 'Steel')
    tyres = a.part('Tyres', 'Rubber')
    for x in (-.17, .17):
        tyres.cyl(.27, .15, loc=(x, -5.25, .27), rot=ACROSS, seg=10, bevel=.04, bseg=1)
        gear.cyl(.12, .2, loc=(x * 1.02, -5.25, .27), rot=ACROSS, seg=8, bevel=0)
    gear.cyl(.05, .5, loc=(0, -5.25, .27), rot=ACROSS, seg=6, bevel=0)
    gear.limb((0, -5.25, .27), (0, -5.1, 1.02), .11, .11, bevel=.02, seg=1)
    for s in (-1, 1):
        body.loft([[(s * .96 + q[0], q[1], q[2]) for q in _sec(y, w, .72, 1.3, n=10)] for y, w in
                   ((-.55, .12), (-.2, .26), (.9, .26), (1.35, .12))], bevel=.02, seg=1)             # gear sponsons
        tyres.cyl(.36, .24, loc=(s * 1.3, .45, .36), rot=ACROSS, seg=12, bevel=.06, bseg=1)
        gear.cyl(.17, .27, loc=(s * 1.3, .45, .36), rot=ACROSS, seg=8, bevel=0)
        gear.limb((s * 1.2, .45, .36), (s * 1.0, .3, 1.0), .12, .12, bevel=.02, seg=1)
    # Coaxial rotors: upper `Rotor`, lower `Rotor_2` (counter-rotating), blades 60 degrees apart.
    parts.rotor_head(a, a.pivot('Rotor', (0, -.95, 4.95)), 3, 7.5, .5, hub=.34, phase=0.0, t=.06, cap=.02, stripe=.42,
                     droop=.1)
    _rotor_head_as(a, a.pivot('Rotor_2', (0, -.95, 3.82)), 'Rotor_2', 3, 7.5, .5, hub=.34, phase=math.pi / 3, t=.06,
                   cap=.02, stripe=.42, droop=.1)
    # Details: a tail-boom spine ridge, blade antennas, chaff cartridges in the flare dispensers' lee, a boom strake.
    body.box((.1, 5.0, .08), loc=(0, 4.6, 2.62), bevel=0, taper=(1, .6))
    for y in (-3.6, 3.2):
        steel.box((.03, .3, .22), loc=(0, y, 3.0 if y < 0 else 2.78), bevel=0)
    for s in (-1, 1):
        steel.box((.06, .5, .05), loc=(s * .3, 4.4, 2.5), bevel=0)
        steel.box((.1, .12, .12), loc=(s * 1.05, -4.6, 2.28), bevel=0)     # cockpit step grabs
    kit27.clean(a)
    a.post = [lambda a_: flip_spinner(a_, 'Rotor_2')]


# ----------------------------------------------------------------------------- Su-25


UNITS4['heavy_attack_heli'] = heavy_attack_heli
_OPT4['heavy_attack_heli'] = mb_round6.BUILDERS['heavy_attack_heli'][1]


BUILDERS.update({n: (fn, dict(_OPT4[n], ao_strength=.65)) for n, fn in UNITS4.items()})
