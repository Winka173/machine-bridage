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
Pass 5d (DECISIONS "27 wave 5d"): leviathan, caspian, typhon, landing_hovercraft, supreme_command.
"""
import math

from mathutils import Vector

import mb_bosses2 as b2
import mb_kit27 as k
import mb_naval as nv
import mb_p16_arms as p16
import mb_p20_bosses as p20
import mb_p22_content as p22
import mb_p25_models as p25
import mb_p25_models2 as m2
import mb_parts27 as parts
import mb_phase8 as p8
import mb_redesign_20y as r20
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
    run.__doc__ = (build.__doc__ or '') + '\n\nPrompt 27 wave 5: V2 pass ' + (up.__doc__ or '')
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


# ============================================================================= leviathan
def _lev_turret(a, mount, part, rise, w, d, h, barrel, r, gap):
    """One of mb_naval._triple's turrets in V2: a turned barbette, the gunhouse as a sharp loft of the old box (same
    taper and aft shift) with chamfered corners and roof edge and recessed side panels, turned barrels (sleeve, muzzle
    swell, a bored muzzle) from the same roots. Pivots, the sloped face plate, roof, blast bags and bores stay."""
    tag = mount[6:].replace('.', '_')
    m = dotted(mount)
    tb.strip(a, (f'Barbette_{tag}', f'Gunhouse_{tag}', f'Barrels_{tag}'))
    _drum(a.part(f'Barbette_{tag}', 'Armor', dotted(part)), w * .46, -.3, rise, seg=24, lip=.08)
    yc, c = .2, min(.18, h * .08)

    def rect(t, inset=0.0):
        hx = w / 2 * (1 - .1 * t) - inset
        hy = d / 2 * (1 - .2 * t) - inset
        y, z = yc + .5 * t, .12 + h * t
        return [(hx, y - hy, z), (hx, y + hy, z), (-hx, y + hy, z), (-hx, y - hy, z)]
    gh = a.part(f'Gunhouse_{tag}', 'Team', m)
    k.sharp_loft(gh, [rect(0), rect(1 - c / h), rect(1, c)], chamfer=c * 1.3)
    k.inset(gh, lambda cc, n, f: abs(n.x) > .8, width=.1 * w / 3.6, depth=-.02)
    yb, yt = yc - d / 2, yc - d / 2 * .8 + .5
    y0 = yb + (yt - yb) * .45
    zb = .12 + h * .45
    sleeve = barrel * .3
    steel = a.part(f'Barrels_{tag}', 'Steel', m)
    for x in (-gap, 0.0, gap):
        k.lathe(steel, [(r * 1.45, 0), (r * 1.3, sleeve), (r, sleeve), (r * .86, barrel * .94), (r * .98, barrel * .96),
                        (r * .98, barrel), (r * .55, barrel), (r * .55, barrel - r * .8)],
                loc=(x, y0 - .5, zb), rot=FORWARD, seg=12, worn=(1, 5))


def _leviathan_up(a):
    """hull as a sharp loft on the same sections (deck edge chamfered) with recessed belt panels, the superstructure
    levels, tower, bridge and director as chamfered blocks with recessed side panels, every main and secondary turret
    in V2 (turned barbette, lofted chamfered gunhouse with side panels, turned barrels), chamfered launch-cell blocks."""
    tb.strip(a, ('Hull', 'Superstructure', 'Vls_block'))
    rings = []
    for y, hd, hw, zd, rake in nv.LEV_SECTIONS:
        hm = nv._flare(hd, hw)
        side = [(hd, y, zd), (hm, y + rake * .2, zd * .5), (hw, y + rake * .5, .3),
                (hw * .93, y + rake * .8, nv.LEV_KEEL * .55), (hw * .4, y + rake, nv.LEV_KEEL)]
        rings.append(side + [(-x, yy, z) for x, yy, z in reversed(side)])
    hull = a.part('Hull', 'Armor')
    k.sharp_loft(hull, rings, chamfer=.16, corners=(0, 9))
    k.inset(hull, lambda c, n, f: abs(n.x) > .85 and .45 < c.z < 2.0 and -24 < c.y < 31, width=.2, depth=-.02)
    z01 = nv.deck(1.7)
    z02 = z01 + 1.8
    z03 = z02 + 1.7
    ztop = z03 + 7.5
    zaft = nv.deck(15.0) + 2.4
    sup = a.part('Superstructure', 'Team')
    for size, loc, taper, ch in (((10.2, 22.6, 2.2), (0, 1.7, z01 + .7), (.98, .99), .12),
                                 ((8.6, 15.5, 1.7), (0, .5, z02 + .85), (.97, .98), .12),
                                 ((4.6, 5.6, 7.5), (0, -1.0, z03 + 3.75), (.8, .82), .14),
                                 ((6.0, 4.0, 1.6), (0, -1.5, ztop + .8), (.92, .9), .12),
                                 ((3.2, 3.0, 1.8), (0, -1.0, ztop + 2.5), (.9, .9), .1),
                                 ((6.0, 5.0, 2.8), (0, 15.0, nv.deck(15.0) + 1.0), (.95, .95), .12),
                                 ((3.0, 2.8, 3.0), (0, 14.2, zaft + 1.5), (.9, .9), .1)):
        k.block(sup, size, loc=loc, chamfer=ch, taper=taper)
    k.inset(sup, lambda c, n, f: abs(n.x) > .8 and abs(n.z) < .35, width=.16, depth=-.02)
    main = dict(w=6.6, d=7.2, h=2.5, barrel=9.6, r=.27, gap=1.7)
    sec = dict(w=3.6, d=4.4, h=1.6, barrel=5.6, r=.12, gap=.62)
    for mount, part, rise, p in (('Mount_gun', 'Part_gun', .6, main), ('Mount_gun.001', 'Part_gun.001', 2.6, main),
                                 ('Mount_gun.002', 'Part_gun.002', .7, main),
                                 ('Mount_gun.003', 'Part_sec_f', z03 - z02 + 2.1, sec),
                                 ('Mount_gun.004', 'Part_sec_a', 3.0, sec)):
        _lev_turret(a, mount, part, rise, **p)
    vls = a.part('Vls_block', 'Armor', 'Part_vls')
    for s in (-1, 1):
        k.block(vls, (2.0, 5.0, .6), loc=(s * 3.15, 0, .3), chamfer=.06)


# ============================================================================= caspian
def _caspian_up(a):
    """hull as a sharp loft on the same sections (top shoulders chamfered) with recessed side panels, the eight
    turbofans as turned nacelles, the six anti-ship canisters turned with end bands, chamfered launcher fairing and
    endplate floats, seeded gear on the back (seed 5301)."""
    prof = [(-25.5, .3, 4.2, .5), (-24.0, 1.6, 5.6, 1.4), (-21.0, 2.8, 6.4, 1.0), (-15.0, 3.0, 6.6, .8), (0.0, 3.0, 6.5, .8),
            (4.0, 2.9, 6.4, 1.1), (12.0, 2.6, 6.3, 1.6), (20.0, 2.0, 6.2, 2.4), (24.5, 1.1, 6.1, 3.6), (26.0, .3, 5.9, 4.6)]
    tb.strip(a, ('Hull', 'Jets', 'Launch_canisters', 'Launcher_fairing', 'Float_wing_l', 'Float_wing_r'))
    rings = []
    for y, hw, zt, zk in prof:
        rings.append([(hw * .6, y, zt), (hw, y, zt - .9), (hw, y, zk + 1.2), (hw * .55, y, zk + .25), (0, y, zk),
                      (-hw * .55, y, zk + .25), (-hw, y, zk + 1.2), (-hw, y, zt - .9), (-hw * .6, y, zt)])
    hull = a.part('Hull', 'Team')
    k.sharp_loft(hull, rings, chamfer=.18, corners=(0, 1, 7, 8))
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and -22 < c.y < 22, width=.15, depth=-.015)
    jets = a.part('Jets', 'Steel', 'Part_engines')
    for i in range(4):
        for s in (-1, 1):
            k.lathe(jets, [(.44, 0), (.6, .06), (.64, .45), (.62, 2.7), (.55, 3.35), (.5, 3.6), (.44, 3.6)],
                    loc=(s * (1.7 + i * 1.55), 1.8, 1.95), rot=FORWARD, seg=14, worn=(2, 4))
    tubes = a.part('Launch_canisters', 'Team', 'Part_launcher')
    for row in range(3):
        for s in (-1, 1):
            k.lathe(tubes, [(.7, -3.5), (.75, -3.42), (.75, -2.6), (.8, -2.55), (.8, -2.2), (.75, -2.15), (.75, 3.42),
                            (.7, 3.5)], loc=(s * .95, -3.0 + row * 3.0, .9 + row * .5), rot=(R90 - .15, 0, 0), seg=14,
                    worn=(3, 6))
    k.block(a.part('Launcher_fairing', 'Armor', 'Part_launcher'), (4.6, 10.0, .5), loc=(0, -.5, .2), chamfer=.15,
            ends=(True, True))
    for s, name in ((1, 'Part_wing_l'), (-1, 'Part_wing_r')):
        k.block(a.part(f'Float_{name[5:]}', 'Armor', name), (1.2, 8.0, 2.2), loc=(s * 7.9, -.6, -.6), chamfer=.25,
                taper=(.8, .8), ends=(True, True))
    k.greebles(a.part('Deck_gear', 'Steel'), (0, 10.5, 6.31), (1, 0, 0), (0, 1, 0), (2.2, 7.0), 6, seed=5301,
               height=(.06, .2), chamfer=.015)


# ============================================================================= typhon
def _typhon_up(a):
    """the missile hump as a sharp loft with sloped ends and chamfered shoulders, turned launch-door lids, chamfered
    bow and sail planes and tail fins (the anechoic hull, sail and sonar dome untouched)."""
    tb.strip(a, ('Missile_hump', 'Bow_planes', 'Sail_planes', 'Rudder_fins', 'Doors_doors_l', 'Doors_doors_r'))

    def hump(y, xb, xt, zt, zb=3.1):
        return [(xb, y, zb), (xt, y, zt), (-xt, y, zt), (-xb, y, zb)]
    k.sharp_loft(a.part('Missile_hump', 'Undercarriage'),
                 [hump(-1.0, 2.4, 2.0, 3.5), hump(0.0, 3.1, 2.8, 3.74), hump(12.0, 3.1, 2.8, 3.74),
                  hump(13.0, 2.4, 2.0, 3.5)], chamfer=.25, corners=(1, 2))
    k.block(a.part('Bow_planes', 'Armor'), (12.4, 1.6, .25), loc=(0, -20.0, 1.2), chamfer=.08, taper=(.8, 1),
            ends=(True, True))
    k.block(a.part('Sail_planes', 'Armor', 'Part_sail'), (9.0, 1.8, .3), loc=(0, -1.2, 3.4), chamfer=.09,
            taper=(.8, 1), ends=(True, True))
    fins = a.part('Rudder_fins', 'Armor', 'Part_rudder')
    k.block(fins, (.4, 3.4, 5.6), loc=(0, -.2, 1.6), chamfer=.1, taper=(1, .6), ends=(True, True))
    k.block(fins, (.4, 3.0, 3.2), loc=(0, -.2, -2.2), chamfer=.1, taper=(1, .6), ends=(True, True))
    k.block(fins, (8.6, 2.8, .35), loc=(0, 0, -.2), chamfer=.1, taper=(.9, .8), ends=(True, True))
    for name in ('Part_doors_l', 'Part_doors_r'):
        lids = a.part(f'Doors_{name[5:]}', 'Armor', name)
        for i in range(5):
            _drum(lids, .8, -.08, .08, loc=(0, -4.0 + i * 2.0, 0), seg=16, lip=.04)


# ============================================================================= landing_hovercraft
def _hovercraft_up(a):
    """chamfered buoyancy hull, side structures (recessed panels on the outer walls), sloped bows and control cabin;
    seeded gear on the side-structure roofs (seeds 5401-5403). Skirt, ducts, fans and weapons untouched."""
    tb.strip(a, ('Hull', 'Side_structures', 'Cabin'))
    k.block(a.part('Hull', 'Armor'), (13.8, 25.0, 1.0), loc=(0, 0, 1.5), chamfer=.1, ends=(True, True))
    team = a.part('Side_structures', 'Team')
    for s in (-1, 1):
        k.block(team, (3.0, 20.5, 2.3), loc=(s * 5.3, -.25, 3.15), chamfer=.09, taper=(.96, .98))
    k.inset(team, lambda c, n, f: n.x * c.x > 0 and abs(n.x) > .8, width=.14, depth=-.02)
    for s in (-1, 1):
        x0, x1 = sorted((s * 3.75, s * 6.85))
        tb.strip(a, ('Armor',), inside=((x0, -11.65, 1.95), (x1, -10.25, 4.3)))
        k.extrude(a.part('Armor', 'Armor'), [(-11.6, 2.0), (-11.6, 2.6), (-10.6, 4.25), (-10.3, 4.25), (-10.3, 2.0)],
                  3.0, loc=(s * 5.3, 0, 0), axis='X', chamfer=.06, corner=.05)
    k.block(a.part('Cabin', 'Team'), (2.8, 2.8, 1.5), loc=(-5.3, -8.8, 5.05), chamfer=.07, taper=(.94, .94))
    gear = a.part('Deck_gear', 'Steel')
    for cx, cy, sv, n, seed in ((5.3, -8.7, 1.8, 4, 5401), (5.3, -3.9, 1.6, 3, 5402), (-5.3, -5.5, 2.2, 4, 5403)):
        k.greebles(gear, (cx, cy, 4.3), (1, 0, 0), (0, 1, 0), (2.2, sv), n, seed=seed, height=(.06, .2), chamfer=.015)


# ============================================================================= supreme_command
def _truck_wheel(a, x, y, r, w, s, seg=18):
    """A big off-road tyre (turned, rounded shoulders) with a dished steel hub on its outer face (side s)."""
    h = w / 2
    rot = parts.side_rot(s)
    k.lathe(a.part('Tyres', 'Rubber'), [(r * .58, -h), (r * .9, -h), (r, -h * .55), (r, h * .55), (r * .9, h),
                                        (r * .58, h)], loc=(x, y, r), rot=rot, seg=seg, worn=(2, 3))
    k.lathe(a.part('Hubs', 'Steel'), [(r * .56, h - .02), (r * .56, h + .02), (r * .5, h + .04), (r * .3, h + .012),
                                      (r * .22, h + .07), (0, h + .07)], loc=(x, y, r), rot=rot, seg=12, worn=(2,))


def _supreme_up(a):
    """turned tyres with dished hubs, the faceted cab as a chamfered extrusion, chamfered citadel, war room, skirts and
    generator, seeded gear on the war-room roof (seed 5501)."""
    tb.strip(a, ('Tyres', 'Hubs', 'Cab', 'Citadel', 'War_room', 'Generator'))
    for y in p8.SC_AXLES:
        for s in (-1, 1):
            _truck_wheel(a, s * 1.62, y, .95, .7, s)
    k.extrude(a.part('Cab', 'Armor'), [(-7.15, 2.0), (-7.35, 2.55), (-6.45, 3.78), (-4.2, 3.95), (-4.2, 2.0)], 4.16,
              axis='X', chamfer=.08, corner=.06)
    team = a.part('Citadel', 'Team')
    for s in (-1, 1):
        k.block(team, (.12, 2.9, .95), loc=(s * 1.98, -.2, 1.5), chamfer=.03, ends=(True, True))
    k.block(team, (4.2, 1.1, .5), loc=(0, -4.75, 3.72), chamfer=.05)
    k.block(team, (4.1, 11.1, 2.1), loc=(0, 1.25, 3.05), chamfer=.08)
    k.block(team, (3.4, 6.4, .1), loc=(0, -.1, 5.52), chamfer=0)
    k.block(a.part('War_room', 'Team'), (3.5, 6.6, 1.4), loc=(0, -.1, 4.8), chamfer=.07, taper=(.95, .96))
    k.block(a.part('Generator', 'Armor'), (1.8, 1.0, 1.1), loc=(.9, 6.4, 4.65), chamfer=.05)
    k.greebles(a.part('Deck_gear', 'Steel'), (0, 0, 5.57), (1, 0, 0), (0, 1, 0), (2.8, 1.2), 5, seed=5501,
               height=(.05, .16), chamfer=.012)


BUILDERS = {
    'command_airship': _wrap(p20.BUILDERS['command_airship'], _airship_up, ao=.75),
    'drone_mothership': _wrap(p20.BUILDERS['drone_mothership'], _mothership_up, ao=.75),
    'mega_gunship': _wrap(b2.BUILDERS['mega_gunship'], _gunship_up, ao=.75),
    'sky_fortress': _wrap(m2.BUILDERS['sky_fortress'], _fortress_up, ao=.75),
    'daedalus': _wrap(p25.BUILDERS['daedalus'], _daedalus_up, ao=.75),
    'morrigan': _wrap(p22.BUILDERS['morrigan'], _morrigan_up, ao=.7),
    # Pass 5d.
    'leviathan': _wrap(nv.BUILDERS['leviathan'], _leviathan_up, ao=.75),
    'caspian': _wrap(r20.BUILDERS['caspian'], _caspian_up, ao=.75),
    'typhon': _wrap(r20.BUILDERS['typhon'], _typhon_up, ao=.7),
    'landing_hovercraft': _wrap(p16.BUILDERS['landing_hovercraft'], _hovercraft_up, ao=.7),
    'supreme_command': _wrap(p8.BUILDERS['supreme_command'], _supreme_up, ao=.75),
}
