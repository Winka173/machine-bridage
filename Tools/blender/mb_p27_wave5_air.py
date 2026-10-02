"""Prompt 27 wave 5, lane B (DECISIONS "27 wave 5c ..."): the flying and naval bosses on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Lane B of Docs/models/WAVES_4_6_PLAN.md "Wave 5"; the ground bosses
(lane A) live in mb_p27_wave5_ground.py.

Method (wave 6's, which keeps every node): each boss is its current builder (same nodes, pivots, materials, part
names, `Part_*` / `Mount_*` / `Muzzle_*` / `Propeller*` / `Pd_laser_*` / `Pod_bay_*` / `Thruster_main`), then a V2
pass that swaps its big hard surfaces for V2 ones under the SAME part names (`k.sharp_loft` hulls on the old rings,
chamfered `k.block` superstructure with `k.inset` panels, turned `k.lathe` barbettes, bells and barrels, seeded
`k.greebles`, the library rotor head), then `k.clean`. Lofted aircraft skins (Sky Fortress's shared C-130 airframe,
Morrigan's stealth body) follow the jet rule: `k.clean` and V2 weapon housings only.

Pass 5c: command_airship, drone_mothership, mega_gunship, sky_fortress, daedalus, morrigan.
"""
import math

from mathutils import Vector

import mb_bosses2 as b2
import mb_kit27 as k
import mb_p20_bosses as p20
import mb_p22_content as p22
import mb_p25_models as p25
import mb_p25_models2 as m2
import mb_parts27 as parts
import mb_tower_branches as tb
from mb_phase2 import _suffixed, dotted
from mb_vehicles import ACROSS, R90

TAU = math.tau
FORWARD, BACKWARD = (R90, 0, 0), (-R90, 0, 0)


def _wrap(old, up, ao=None):
    """(builder, options): the boss's current builder, then its V2 pass, then k.clean."""
    build, options = old

    def run(a):
        # Suffixed pivots (Mount_gun__001) get their runtime names (Mount_gun.001) at finish, also for the bosses
        # whose old builder relied on mb_round6's own build loop for it (mega_gunship); idempotent.
        _suffixed(a)
        build(a)
        up(a)
        k.clean(a)
    run.__name__ = getattr(build, '__name__', 'boss')
    run.__doc__ = (build.__doc__ or '') + '\n\nPrompt 27 wave 5c: V2 pass ' + (up.__doc__ or '')
    return run, (dict(options, ao_strength=ao) if ao is not None else dict(options))


def _turned_barrel(part, x, y, z, length, r, seg=8, rot=FORWARD):
    """A barrel from its root at (x, y, z) along rot's +Z with a muzzle collar: one turned surface."""
    k.lathe(part, [(r * 1.15, 0), (r, length * .08), (r, length * .9), (r * 1.3, length * .92), (r * 1.3, length),
                   (r * .55, length)], loc=(x, y, z), rot=rot, seg=seg, worn=(3,))


def _drum(part, r, z0, z1, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, lip=.05):
    """A barbette / tub from z0 to z1: a turned drum with a worn chamfered rim (no recess)."""
    k.lathe(part, [(0, z0), (r, z0), (r, z1 - lip), (r - lip * .6, z1 - lip * .25), (r - lip, z1), (0, z1)],
            loc=loc, rot=rot, seg=seg, worn=(3,))


# ============================================================================= command_airship
def _airship_up(a):
    """spine hull as a sharp loft (same sections) with recessed side panels, chamfered bridge tiers and command deck
    with panels, chamfered gun pods with side panels, turned barbettes, seeded deck greebles."""
    from mb_phase8 import CA_DECK, CA_KEEL
    D = CA_DECK

    def sec(y, kk=1.0, top=D):
        w, wb = 2.6 * kk, 1.2 * kk
        return [(-wb, y, CA_KEEL * (.6 + .4 * kk)), (wb, y, CA_KEEL * (.6 + .4 * kk)), (w, y, -.6), (w, y, top),
                (-w, y, top), (-w, y, -.6)]
    tb.strip(a, ('Spine', 'Bridge', 'Command_deck'))
    hull = a.part('Spine', 'Armor')
    k.sharp_loft(hull, [sec(-21.8, .12, D + .6), sec(-20.0, .5, D + .35), sec(-17.5, .92), sec(-15.5, 1.0),
                        sec(15.0, 1.0), sec(17.5, .7, D - .2), sec(18.6, .35, D - .5)], chamfer=.14)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and -.3 < c.z < 2.0, width=.12, depth=-.018)
    br = a.part('Bridge', 'Armor')
    k.block(br, (4.2, 6.0, 1.6), loc=(0, -4.0, D + .8), chamfer=.1, taper=(.95, .95))
    k.block(br, (3.6, 4.8, 1.5), loc=(0, -3.8, D + 2.3), chamfer=.09, taper=(.95, .95))
    k.inset(br, lambda c, n, f: abs(n.x) > .8 and abs(n.z) < .3, width=.1, depth=-.015)
    k.block(a.part('Command_deck', 'Armor'), (3.2, 3.6, 1.3), loc=(0, -3.6, D + 3.7), chamfer=.08,
            taper=(.92, .92))
    # The 105 mm gun pods slung either side (p20's), chamfered with recessed side panels.
    for s, mount in ((1, 'Mount_gun.002'), (-1, 'Mount_gun.003')):
        name = f'Pod_{p20._tag(mount)}'
        tb.strip(a, (name,))
        pod = a.part(name, 'Team')
        k.block(pod, (1.8, 4.4, 1.6), loc=(s * 7.5, 0, -3.0), chamfer=.3, ends=(True, True))
        k.inset(pod, lambda c, n, f: abs(n.x) > .9, width=.12, depth=-.016)
    # Turned barbettes under the bow and stern turrets (on their Part_gun pivots).
    for name in ('Part_gun', 'Part_gun.001'):
        tag = name[5:].replace('.', '_')
        tb.strip(a, (f'Barbette_{tag}',))
        _drum(a.part(f'Barbette_{tag}', 'Armor', dotted(name)), .95, -.89, .01, seg=20, lip=.06)
    # Seeded deck gear fore, amidships and aft (clear of the turrets, the bridge, the radar and the flag).
    gear = a.part('Deck_gear', 'Steel')
    top = D + .045
    for (cy, sy, n, seed) in ((-17.2, 2.6, 4, 5101), (-9.9, 3.4, 4, 5102), (4.0, 7.0, 6, 5103), (13.6, 2.6, 3, 5104)):
        k.greebles(gear, (0, cy, top), (1, 0, 0), (0, 1, 0), (3.4, sy), n, seed=seed, height=(.06, .2), chamfer=.015)


# ============================================================================= drone_mothership
def _mothership_up(a):
    """gondola as a sharp loft on the old six-point sections, chamfered turret and gun armour, the quad flak
    guns' bodies and shields as chamfered blocks on a turned base, the second drone bay's frame chamfered."""
    from mb_bosses import _sec6
    tb.strip(a, ('Gondola',))
    k.sharp_loft(a.part('Gondola', 'Team'),
                 [_sec6(-7.5, .5, -4.7, 1.05, -4.25, 1.0, -3.3), _sec6(-6.9, .95, -5.35, 1.4, -4.45, 1.25, -3.3),
                  _sec6(-2.0, .95, -5.35, 1.4, -4.45, 1.25, -3.3), _sec6(-1.3, .7, -5.0, 1.2, -4.4, 1.1, -3.3)],
                 chamfer=.09)
    tb.strip(a, ('Turret_armor',))
    k.block(a.part('Turret_armor', 'Armor', 'Turret'), (.8, .5, .46), loc=(0, -.55, -.38), chamfer=.05,
            ends=(True, True))
    tb.strip(a, ('Gondola_gun_armor',))
    k.block(a.part('Gondola_gun_armor', 'Armor', dotted('Mount_main.001')), (.66, .42, .36), loc=(0, -.46, -.3),
            chamfer=.04, ends=(True, True))
    tb.strip(a, ('Bay2_frame',))
    k.block(a.part('Bay2_frame', 'Armor', dotted('Mount_missile.001')), (3.0, 3.4, .6), loc=(0, 0, 0), chamfer=.1,
            ends=(True, True))
    tb.strip(a, ('Flak_body', 'Flak_shield'))
    for m in ('Mount_mg', dotted('Mount_mg.001')):
        fb = a.part('Flak_body', 'Team', m)
        _drum(fb, 1.05, 0, .26, seg=18, lip=.05)
        k.block(fb, (1.35, 1.2, .66), loc=(0, .08, .58), chamfer=.07, taper=(.85, .9))
        k.inset(fb, lambda c, n, f: abs(n.x) > .8 and c.z > .35, width=.06, depth=-.01)
        k.block(a.part('Flak_shield', 'Armor', m), (1.75, .13, .74), loc=(0, -.62, .64), rot=(-.25, 0, 0),
                chamfer=.03, taper=(.85, 1), ends=(True, True))


# ============================================================================= mega_gunship
def _gunship_up(a):
    """the library rotor heads on both tandem rotors (same blade count, radius, chord and phase), turned tyres."""
    tb.strip(a, parents=('Rotor', 'Rotor_rear'))
    parts.rotor_head(a, 'Rotor', 3, 7.5, .64, hub=.4, phase=R90, t=.07, cap=.25, stripe=.42, droop=.05)
    parts.rotor_head(a, 'Rotor_rear', 3, 7.5, .64, hub=.4, phase=R90 + math.pi / 3, t=.07, cap=.25, stripe=.42,
                     droop=.05)
    # The library names its parts Rotor_*: the rear head's take the old Rotor_rear_* names (unique mesh names).
    for i, key in enumerate(a.order):
        name, mat, parent = key
        if parent == 'Rotor_rear' and name.startswith('Rotor_') and not name.startswith('Rotor_rear'):
            new = ('Rotor_rear_' + name[len('Rotor_'):], mat, parent)
            a.shapes[new] = a.shapes.pop(key)
            a.order[i] = new
    tb.strip(a, ('Tyres',))
    tyres = a.part('Tyres', 'Rubber')

    def tyre(x, y, r, w):
        h = w / 2
        k.lathe(tyres, [(r * .55, -h), (r * .9, -h), (r, -h * .5), (r, h * .5), (r * .9, h), (r * .55, h)],
                loc=(x, y, r), rot=ACROSS, seg=14, worn=(2, 3))
    for s in (-1, 1):
        for dx in (-.16, .16):
            tyre(s * 1.45 + dx, -3.25, .38, .2)
        tyre(s * 1.62, 4.1, .42, .24)


# ============================================================================= sky_fortress
def _fortress_up(a):
    """(jet rule on the shared C-130 airframe) chamfered gun-port housings and breeches, turned barrels."""
    tb.strip(a, ('Gun_ports', 'Gun_breeches', 'Gun_barrels'))
    ports = a.part('Gun_ports', 'EliteBlack')
    for name, (x, y, z), length, tilt, r, housing in (
            ('Mount_mg', (1.33, -4.29, 0.0), 1.15, .14, .09, (.5, .9, .7)),
            ('Mount_gun', (1.33, -1.23, .06), 1.6, .2, .11, (.55, 1.2, .9)),
            (dotted('Mount_gun.001'), (1.33, .97, .06), 1.6, .2, .11, (.55, 1.2, .9)),
            ('Mount_main', (1.33, 3.7, .03), 2.3, .14, .16, (.7, 1.6, 1.1))):
        hx, hy, hz = housing
        k.block(ports, housing, loc=(x - .1, y, z), chamfer=.06, ends=(True, True))
        k.block(a.part('Gun_breeches', 'EliteBlack', name), (.4, hy * .6, hz * .6), loc=(.05, 0, 0), chamfer=.03,
                ends=(True, True))
        # The barrel along +X tilted down by `tilt` (the old cylinder's axis), from the mount out.
        _turned_barrel(a.part('Gun_barrels', 'Steel', name), 0, 0, 0, length - .1, r, seg=10, rot=(0, R90 + tilt, 0))


# ============================================================================= daedalus
def _daedalus_up(a):
    """upper wedge as a sharp loft (top shoulders chamfered), chamfered dorsal ridge and command tower with
    recessed panels, V2 twin turbolaser turrets (turned base, chamfered house, turned barrels), seeded greebles on
    the upper deck instead of the 46 plain boxes, chamfered keel plates and turned landing feet, chamfered drop-bay
    frames, the engine housing chamfered with turned bells, turned point-defence tubs."""
    from mb_p25_models import DAEDALUS_UPPER, _daedalus_upper
    from mb_redesign_20y import ACC, _sd_at, _sd_surface
    tb.strip(a, ('Upper_hull', 'Spine', 'Turbolasers', 'Turbolaser_barrels', 'Upper_greebles', 'Keel'))
    rings = []
    for y, hw, zt in DAEDALUS_UPPER:
        foot = min(_sd_surface(hw, y, ACC), _sd_surface(0, y, ACC)) - .15
        rings.append([(hw, y, foot), (hw * .84, y, zt), (-hw * .84, y, zt), (-hw, y, foot), (-hw * .5, y, foot - .4),
                      (hw * .5, y, foot - .4)])
    k.sharp_loft(a.part('Upper_hull', 'Fuel'), rings, chamfer=.14, corners=(1, 2))
    spine = a.part('Spine', 'MetalSheet')
    k.block(spine, (2.6, 19.0, 1.0), loc=(0, 3.0, _daedalus_upper(3.0)[1] + .4), chamfer=.12, taper=(.7, .96))
    z = _daedalus_upper(11.5)[1]
    k.block(spine, (3.4, 3.2, 2.4), loc=(0, 11.6, z + 1.1), chamfer=.12, taper=(.75, .85))
    k.block(spine, (2.2, 2.2, 1.6), loc=(0, 11.6, z + 2.9), chamfer=.1, taper=(.8, .85))
    k.block(spine, (7.0, 2.3, 1.2), loc=(0, 11.6, z + 4.2), chamfer=.12, taper=(.95, .78), ends=(True, True))
    k.inset(spine, lambda c, n, f: abs(n.x) > .6 and abs(n.z) < .7 and c.z < z + 3.5, width=.12, depth=-.02)
    # Twin turbolaser turrets on the step (same places as before).
    tur = a.part('Turbolasers', 'Armor')
    guns = a.part('Turbolaser_barrels', 'Steel')
    for sx in (-1, 1):
        for y in (-9.0, -2.0, 1.5, 5.0, 8.5, 12.5):
            hw, _ = _daedalus_upper(y)
            x = sx * (hw + 1.0)
            if abs(y + 5.0) < 1.5:
                continue
            base = _sd_surface(x, y, ACC)
            _drum(tur, .75, base - .05, base + .45, loc=(x, y, 0), seg=12, lip=.06)
            k.block(tur, (1.1, 1.2, .5), loc=(x, y, base + .6), chamfer=.08, taper=(.8, .75))
            for o in (-.24, .24):
                _turned_barrel(guns, x + o, y - .45, base + .66, 1.9, .09, seg=6)
    # Seeded gear on the upper deck (a different seed per patch), clear of the stripes, the ridge and the tower.
    greeble = a.part('Upper_greebles', 'Armor')

    def patch(cx, cy, su, sv, n, seed, top=None):
        zt = _daedalus_upper(cy)[1] if top is None else top
        slope = 0.0 if top is not None else (_daedalus_upper(cy + .5)[1] - _daedalus_upper(cy - .5)[1])
        v = Vector((0, 1, slope)).normalized()
        k.greebles(greeble, (cx, cy, zt), (1, 0, 0), v, (su, sv), n, seed=seed, height=(.1, .3), chamfer=.02)
    for sx, seed in ((-1, 5201), (1, 5202)):
        patch(sx * 2.85, 9.2, 1.3, 3.4, 5, seed)
        patch(sx * 2.85, 13.9, 1.2, 1.6, 3, seed + 10)
    patch(0, -8.4, 1.2, 2.0, 3, 5221)
    patch(0, 1.5, 1.3, 11.0, 6, 5222, top=_daedalus_upper(3.0)[1] + .9)
    # Keel plates and landing feet.
    keel = a.part('Keel', 'Armor')
    for y in (-10.0, -4.0, 9.0, 13.0):
        hw, _, zb = _sd_at(y, ACC)
        k.block(keel, (hw * .9, 1.2, .3), loc=(0, y, zb - .1), chamfer=.06, taper=(.85, .9), ends=(True, True))
    for x, y in ((5.0, 11.0), (-5.0, 11.0), (1.8, -9.0), (-1.8, -9.0)):
        _, _, zb = _sd_at(y, ACC)
        k.lathe(keel, [(0, -.225), (.6, -.225), (.7, -.15), (.7, .225), (0, .225)], loc=(x, y, zb - .12), seg=10,
                worn=(1,))
    # Drop-bay frames, the engine bank, the point-defence tubs.
    for i in range(3):
        name = f'Bay_frame_{i + 1}'
        tb.strip(a, (name,))
        k.block(a.part(name, 'Armor', f'Pod_bay_{i + 1}'), (3.2, 3.8, .55), loc=(0, 0, 0), chamfer=.1,
                ends=(True, True))
    tb.strip(a, ('Engine_housing', 'Engine_nozzles', 'Pd_base'))
    t = 'Thruster_main'
    house = a.part('Engine_housing', 'Armor', t)
    k.block(house, (14.0, 2.2, 4.0), loc=(0, 1.3, .2), chamfer=.18, taper=(.9, .88), ends=(True, True))
    k.inset(house, lambda c, n, f: n.z > .8 or abs(n.x) > .8, width=.16, depth=-.02)
    nozzle = a.part('Engine_nozzles', 'Steel', t)
    for x, r, zz in ((2.3, 1.55, .3), (-2.3, 1.55, .3), (5.6, 1.0, .9), (-5.6, 1.0, .9), (5.6, .8, -.9),
                     (-5.6, .8, -.9)):
        k.lathe(nozzle, [(0, -.6), (r, -.6), (r * 1.12, .6), (r * 1.0, .6), (r * .92, .4), (0, .4)],
                loc=(x, 2.9, zz), rot=BACKWARD, seg=18 if r > 1.2 else 14, worn=(2, 3))
    for name in ('Pd_laser_l', 'Pd_laser_r'):
        _drum(a.part('Pd_base', 'Armor', name), .85, -.345, .105, seg=14, lip=.05)


# ============================================================================= morrigan
def _morrigan_up(a):
    """(jet rule) the shoulder cannon as one turned barrel with its muzzle ring."""
    from mb_p22_content import MG
    from mb_p17_temp import _hex_top
    tb.strip(a, ('Steel',))
    gx, gy = 1.4, -4.6
    gz = _hex_top(MG, gy, gx) + .1
    _turned_barrel(a.part('Steel', 'Steel'), gx, gy + .175, gz, .64, .04, seg=8)


BUILDERS = {
    'command_airship': _wrap(p20.BUILDERS['command_airship'], _airship_up, ao=.75),
    'drone_mothership': _wrap(p20.BUILDERS['drone_mothership'], _mothership_up, ao=.75),
    'mega_gunship': _wrap(b2.BUILDERS['mega_gunship'], _gunship_up, ao=.75),
    'sky_fortress': _wrap(m2.BUILDERS['sky_fortress'], _fortress_up, ao=.75),
    'daedalus': _wrap(p25.BUILDERS['daedalus'], _daedalus_up, ao=.75),
    'morrigan': _wrap(p22.BUILDERS['morrigan'], _morrigan_up, ao=.7),
}
