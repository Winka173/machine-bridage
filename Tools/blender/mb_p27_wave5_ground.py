"""Prompt 27 wave 5 lane A (DECISIONS "27 wave 5a ..."): the ground bosses on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Docs/models/WAVES_4_6_PLAN.md "Wave 5".

Every boss is its old builder (mb_p20_bosses / mb_bosses2: same nodes, pivots, materials, mounts, muzzles, part
nodes, the variants' keep/drop nodes), then a V2 pass that swaps the big hard surfaces for V2 ones under the SAME part
names and materials: V2 running gear (dished road wheels, toothed sprocket, idler, sagging belt) on every track unit,
`k.sharp_loft` hulls with worn chamfer lines, `k.extrude` turret shells and pod housings, chamfered `k.block` plates,
raised `k.inset` panels on the big decks, seeded `k.greebles` (one seed per ship), library hatches. Weapons stay as
they were (they read already); nothing new hangs on a moving pivot but chamfered copies of what was there, so the
moving parts and the materials on them are unchanged. Sizes stay the old bounds (prompt 26 sizes are the defs' own
`size` multipliers).

Pass 5a: behemoth, behemoth_inferno, behemoth_tempest, fortress_bastion, fortress_hive.
Pass 5b: kronos, moloch, nuke_train, armored_train, earth_borer (the track units on kronos' and moloch's breakable
`Part_track_*` pivots are rebuilt on those pivots; the trains keep their railway bogies).
"""
import math

from mathutils import Euler, Vector

import mb_bosses2 as b2
import mb_detail as hd
import mb_kit27 as k
import mb_p16_arms as p16
import mb_p20_bosses as p20
import mb_parts27 as parts
import mb_phase8 as p8
import mb_vehicles as mv
from mb_bosses import _sec6
from mb_phase2 import _suffixed
from mb_tower_branches import strip
from mb_vehicles import _flank

TAU = math.tau
AO = .72        # AO strength (default .9): V2 bosses a little paler, still dark war machines (card <= ~+20 %)
TRACK_PARTS = ('Tracks', 'Track_shoes', 'Road_wheels', 'Tyres', 'Wheels', 'Hubs', 'Sprockets')


# ============================================================================= shared helpers
def _redo(a, name, build):
    """Drop every part called `name` (any material, any pivot) and rebuild it on the same (material, pivot) with
    build(shape): the V2 copy of a part that sits on a moving pivot keeps its pivot and material."""
    for key in [key for key in a.order if key[0] == name]:
        _, mat, parent = key
        a.shapes.pop(key).bm.free()
        a.order.remove(key)
        build(a.part(name, mat, parent))


def _belt_outline(length, top, wheel_r, rb, return_rollers=3, sag=.04):
    """The V2 belt outline (y, z) of one track unit centred at y = 0 (mb_parts27.track_unit's, with the end radius
    rb): round the end wheels and the first and last road wheels, its top run sagging between the return rollers.
    Returns (outline, first road wheel's |y|)."""
    bottom = -.01
    first = length / 2 - wheel_r - .12
    circles = [(e * (length / 2 - rb), top - rb, rb) for e in (-1, 1)] + \
              [(e * first, bottom + wheel_r, wheel_r) for e in (-1, 1)]
    hull = mv._hull2d([(cy + r * math.cos(i * TAU / 16), cz + r * math.sin(i * TAU / 16))
                       for cy, cz, r in circles for i in range(16)])
    e = length / 2 - rb
    keep = [p for p in hull if not (p[1] > top - 1e-3 and -e + 1e-3 < p[0] < e - 1e-3)]
    i_end = next(i for i, p in enumerate(keep) if abs(p[1] - top) < 1e-3 and p[0] > 0)
    supports = [e - j * 2 * e / (return_rollers + 1) for j in range(return_rollers + 2)]
    run = []
    for ya, yb in zip(supports, supports[1:]):
        for t in (.25, .5, .75, 1.0):
            run.append((ya + (yb - ya) * t, top - (sag * 4 * t * (1 - t) if t < 1 else 0)))
    return keep[:i_end + 1] + run[:-1] + keep[i_end + 1:], first


def _track_pair(a, x, y0, length, top, wheel_r, wheels, belt_width, rb, sprocket_end, cleat_pitch=.3, wheel_seg=10,
                teeth=9, return_rollers=3, sag=.04):
    """Both track units of one axle pair (left and right at |x|, centred at y0): mb_parts27.track_unit with the end
    radius `rb` of the old boss units (the library caps it at .25 m, a tank's) and an offset along the hull, so a
    boss with four separate units keeps their places. Same part names and materials as the library's."""
    belt = a.part('Tracks', 'Undercarriage')
    bottom = -.01
    outline, first = _belt_outline(length, top, wheel_r, rb, return_rollers, sag)
    for s in (-1, 1):
        cx = s * x
        face = cx + s * belt_width / 2
        k.extrude(belt, outline, belt_width, loc=(cx, y0, 0), axis='X', chamfer=0)
        for (py, pz), (ty, tz) in mv._perimeter(outline, cleat_pitch, .05):
            if abs(py) < first - .02 or pz < .06:      # the ends only, none under the ground line
                continue
            k.block(belt, (belt_width + .04, .07, .05), loc=(cx, y0 + py + tz * .012, pz - ty * .012),
                    rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
        for i in range(wheels):
            y = -first + i * 2 * first / (wheels - 1)
            parts.road_wheel(a, (face - s * .03, y0 + y, bottom + wheel_r), wheel_r, .14, s, seg=wheel_seg)
        for end in (-1, 1):
            cy, cz = end * (length / 2 - rb), top - rb
            if end == sprocket_end:
                parts.sprocket(a, (face - s * .02, y0 + cy, cz), rb * .96, teeth, .12, s)
            else:
                parts.idler(a, (face - s * .03, y0 + cy, cz), rb * .92, .14, s, seg=wheel_seg)


def _faceted(outline, depth, z, taper, chamfer, corner=.04):
    """A faceted turret house (old `prism` on axis Z) as a chamfered extrude: build(shape)."""
    def build(shape):
        k.extrude(shape, outline, depth, loc=(0, 0, z), axis='Z', chamfer=chamfer, corner=corner, taper=taper,
                  ends=(False, True))
    return build


def _blocked(size, loc, rot=(0, 0, 0), chamfer=.05, taper=(1, 1), ends=(True, True)):
    def build(shape):
        k.block(shape, size, loc=loc, rot=rot, chamfer=chamfer, taper=taper, ends=ends)
    return build


def _gun_house(w, d, h, chamfer=.04):
    """mb_phase8.autocannon's faceted house (a loft of two eight-sided rings) as a sharp loft: build(shape)."""
    bottom = [(-w / 2 + .12, -d / 2), (w / 2 - .12, -d / 2), (w / 2, -d / 2 + .3), (w / 2, d / 2 - .1),
              (w / 2 - .1, d / 2), (-w / 2 + .1, d / 2), (-w / 2, d / 2 - .1), (-w / 2, -d / 2 + .3)]
    top = [(x * .78, y * .8 + .06) for x, y in bottom]

    def build(shape):
        k.sharp_loft(shape, [[(x, y, .06) for x, y in bottom], [(x, y, h) for x, y in top]], chamfer=chamfer)
    return build


def _hinged_box(W, L, H, pitch, hinge, chamfer):
    """A launcher box hinged along its rear bottom edge at `hinge`, raised `pitch` (mb_bosses / mb_p16_arms Rocket_box
    and Sam_box) as a chamfered block in the same place: build(shape)."""
    lrot = (-pitch, 0, 0)
    centre = Vector(hinge) - Euler(lrot, 'XYZ').to_matrix() @ Vector((0, L / 2, -H / 2))
    return _blocked((W, L, H), tuple(centre), rot=lrot, chamfer=chamfer)


def _wheel_on(tyres, discs, centre, r, w, s, seg=10):
    """mb_parts27.road_wheel's tyre and dished disc into given parts (a wheel on a breakable pivot)."""
    rot = parts.side_rot(s)
    k.lathe(tyres, [(r * .8, -w / 2), (r, -w / 2 + .02), (r, w / 2 - .02), (r * .8, w / 2)], loc=centre, rot=rot,
            seg=seg, worn=(2,))
    k.lathe(discs, [(0, w / 2 + .03), (r * .26, w / 2 + .03), (r * .6, w / 2 - .004), (r * .74, w / 2 + .02),
                    (r * .8, w / 2 - .03)], loc=centre, rot=rot, seg=seg, worn=(3,))


def _pivot_track(a, pivot, s, length, top, width, wheel_r, wheels, rb, sprocket_end, cleat_pitch=.45, teeth=12,
                 seg=10):
    """One mb_p20_bosses.track_unit on its breakable pivot `pivot` (origin on the ground at the unit's centre) on the
    V2 kit: the sagging belt with cleats on the ends, dished road wheels, a toothed sprocket and an idler on the
    outer face (side s), the guard as a chamfered plate. Part names are the old unit's (`Tr_belt_`, `Tr_wheels_`,
    `Tr_guard_<pivot>`, plus `Tr_discs_<pivot>`), materials the old ones' (Undercarriage, Rubber, Armor)."""
    belt = a.part(f'Tr_belt_{pivot}', 'Undercarriage', pivot)
    tyres = a.part(f'Tr_wheels_{pivot}', 'Rubber', pivot)
    discs = a.part(f'Tr_discs_{pivot}', 'Armor', pivot)
    outline, first = _belt_outline(length, top, wheel_r, rb, return_rollers=4, sag=.07)
    k.extrude(belt, outline, width, axis='X', chamfer=0)
    for (py, pz), (ty, tz) in mv._perimeter(outline, cleat_pitch, .05):
        if abs(py) < first - .02 or pz < .08:
            continue
        k.block(belt, (width + .04, .1, .07), loc=(0, py + tz * .02, pz - ty * .02), rot=(math.atan2(tz, ty), 0, 0),
                chamfer=0)
    face = s * width / 2
    bottom = -.01
    for i in range(wheels):
        y = -first + i * 2 * first / (wheels - 1)
        _wheel_on(tyres, discs, (face - s * .04, y, bottom + wheel_r), wheel_r, .2, s, seg)
    for end in (-1, 1):
        cy, cz = end * (length / 2 - rb), top - rb
        if end == sprocket_end:
            p = TAU / teeth
            gear = []
            for i in range(teeth):
                u = i * p
                for du, rr in ((-.42 * p, rb * .82), (-.18 * p, rb * 1.0), (.18 * p, rb * 1.0), (.42 * p, rb * .82)):
                    gear.append((math.cos(u + du) * rr, math.sin(u + du) * rr))
            k.extrude(discs, gear, .18, loc=(face - s * .02, cy, cz), axis='X', chamfer=0)
        else:
            _wheel_on(tyres, discs, (face - s * .04, cy, cz), rb * .9, .2, s, seg)
    k.block(a.part(f'Tr_guard_{pivot}', 'Armor', pivot), (width + .2, length * .96, .16), loc=(0, 0, top + .07),
            chamfer=.04, ends=(True, True))


# ============================================================================= behemoth family
BH_TX, BH_TY, BH_TL = 2.62, 3.0, 5.2


def _bh_up(a, seed, bustle=True):
    """The behemoth chassis and main turret (mb_bosses2._behemoth_chassis / _behemoth_turret) on the V2 kit."""
    hd.mark(a, False)
    strip(a, TRACK_PARTS + ('Fenders', 'Hull', 'Turret_body', 'Hatch'))
    # Running gear: four V2 units, the sprockets at the outer ends (front pair forward, rear pair aft) as before.
    for sy in (-1, 1):
        _track_pair(a, BH_TX, sy * BH_TY, BH_TL, 1.5, .4, 5, 1.0, .5, sy)
    fender = a.part('Fenders', 'Team')
    for sx in (-1, 1):
        for sy in (-1, 1):
            y0 = sy * BH_TY
            k.block(fender, (1.2, BH_TL + .2, .13), loc=(sx * BH_TX, y0, 1.6), chamfer=.03)
            for end in (-1, 1):
                fender.box((1.2, .5, .08), loc=(sx * BH_TX, y0 + end * (BH_TL / 2 + .15), 1.43), rot=(end * .75, 0, 0),
                           bevel=.02, seg=1)
    # Hull: the same sections as sharp lofts (worn chamfer lines on every long edge), a raised deck panel.
    hull = a.part('Hull', 'Team')
    full = (1.95, .45, 2.05, 2.3, 1.9, 2.55)
    k.sharp_loft(hull, [_sec6(-6.3, .95, 1.05, 1.25, 1.45, 1.1, 1.62), _sec6(-5.3, 1.55, .5, 1.95, 1.75, 1.75, 2.22),
                        _sec6(-4.35, *full), _sec6(5.35, *full), _sec6(5.95, 1.85, .7, 2.05, 2.2, 1.85, 2.45)],
                 chamfer=.07)
    k.inset(hull, lambda c, n, f: n.z > .95 and abs(c.z - 2.55) < .05, width=.12, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8 and c.z > 1.0, width=.08, depth=.01)

    def sec(y, z1, w1, z0=2.53, w0=1.84):
        return [(-w0, y, z0), (w0, y, z0), (w1, y, z1), (-w1, y, z1)]
    snap = k.snapshot(hull)
    k.sharp_loft(hull, [sec(-2.2, 2.66, 1.8), sec(-1.45, 3.35, 1.6), sec(3.6, 3.35, 1.6), sec(4.2, 2.92, 1.72)],
                 chamfer=.06)
    k.inset(hull, lambda c, n, f: abs(n.y) > .5 and n.z > .3, width=.08, depth=.01, since=snap)
    # Front deck: a few seeded fittings either side of the forward mount (clear of its ring and the hatches).
    armor = a.part('Armor', 'Armor')
    avoid = (((0, -3.45, 2.55), 1.1), ((.9, -3.3, 2.55), .7), ((-.9, -3.3, 2.55), .7))
    for i, s in enumerate((-1, 1)):
        k.greebles(armor, (s * 1.5, -2.8, 2.55), (1, 0, 0), (0, 1, 0), (.6, .8), 3, seed=seed + i, height=(.05, .12),
                   chamfer=.015, avoid=avoid)
    # Turret: the faceted shell and bustle as chamfered extrudes, the library hatch behind the cupola.
    t = 'Turret'
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.55, 2.25), (1.55, 2.25), (1.95, 1.35), (1.95, -.85), (1.25, -1.85), (-1.25, -1.85), (-1.95, -.85),
               (-1.95, 1.35)]
    k.extrude(turret, outline, 1.0, loc=(0, 0, .51), axis='Z', chamfer=.07, corner=.06, taper=.88, ends=(False, True))
    k.block(turret, (3.3, 1.2, .82), loc=(0, 2.75, .47), chamfer=.06, taper=(.93, .9))
    k.inset(turret, lambda c, n, f: abs(n.x) > .9 and c.y < 1.3, width=.07, depth=.01)
    parts.hatch(a, 0, 1.05, 1.01, .3, parent=t, seg=12)
    if not bustle:              # the Inferno's pressure bottles lie on its bustle
        return
    k.greebles(a.part('Turret_armor', 'Armor', t), (0, 2.75, .88), (1, 0, 0), (0, 1, 0), (2.4, .7), 4, seed=seed + 5,
               height=(.04, .09), chamfer=.012, avoid=(((0, 2.85, .88), .75), ((-1.45, 3.1, .88), .2),
                                                       ((1.45, 3.1, .88), .2), ((0, 2.9, .88), .3)))


def behemoth(a):
    """The V2 behemoth: p20's behemoth (flank 120 mm guns `Mount_gun.001` / `.002`, rocket pod `Mount_rocket`) on the
    V2 chassis and turret, its sponsons and side-gun houses chamfered."""
    p20.behemoth(a)
    _bh_up(a, 2901)
    for s, mount in ((1, 'Mount_gun.001'), (-1, 'Mount_gun.002')):
        tag = p20._tag(mount)
        _redo(a, f'Sponson_{tag}', _blocked((1.4, 2.6, 1.2), (s * 3.4, -1.0, 2.2), chamfer=.08))
        _redo(a, f'T_house_{tag}', _blocked((1.4, 1.8, .8), (0, .1, .45), chamfer=.07, taper=(.82, .86),
                                            ends=(False, True)))
    _redo(a, 'R_box_Mount_rocket', _blocked((1.6, 2.0, 1.0), (0, 0, .9), rot=(.12, 0, 0), chamfer=.06))
    _redo(a, 'Gun_turret', _faceted([(-.6, .76), (.6, .76), (.84, .3), (.84, -.3), (.5, -.8), (-.5, -.8), (-.84, -.3),
                                     (-.84, .3)], .56, .3, .84, .05))
    k.clean(a)


def behemoth_inferno(a):
    """The V2 Inferno: the flame-thrower behemoth on the V2 chassis and turret, its rocket box chamfered."""
    _suffixed(a)                # Mount_*__001 -> Mount_*.001 at finish (build_assets has no round6 finish)
    b2.behemoth_inferno(a)
    _bh_up(a, 2911, bustle=False)
    lrot = (-math.radians(10), 0, 0)
    _redo(a, 'Rocket_box', _blocked((1.3, 1.9, .7), (0, -.05, .66), rot=lrot, chamfer=.05))
    k.clean(a)


def behemoth_tempest(a):
    """The V2 Tempest: the railgun behemoth on the V2 chassis and turret, coilgun houses and capacitor banks
    chamfered."""
    _suffixed(a)                # Mount_*__001 -> Mount_*.001 at finish (build_assets has no round6 finish)
    b2.behemoth_tempest(a)
    _bh_up(a, 2921)
    _redo(a, 'Coil_turret', _faceted([(-.5, .6), (.5, .6), (.66, .2), (.66, -.3), (.4, -.62), (-.4, -.62),
                                      (-.66, -.3), (-.66, .2)], .5, .27, .84, .04))

    def banks(shape):
        for s in (-1, 1):
            k.block(shape, (.9, 3.6, .8), loc=(s * BH_TX, 3.0, 2.06), chamfer=.06)
        k.inset(shape, lambda c, n, f: n.z > .9, width=.08, depth=.012)
    _redo(a, 'Capacitor_banks', banks)
    k.clean(a)


# ============================================================================= mobile fortress family
FT_PX, FT_PY, FT_PL = 3.4, 5.2, 4.8


def _ft_up(a, seed, roof_greebles=True):
    """The mobile fortress crawler (mb_bosses2._fortress_chassis) on the V2 kit."""
    hd.mark(a, False)
    strip(a, TRACK_PARTS + ('Pods_housing', 'Hull'))
    for sy in (-1, 1):
        _track_pair(a, FT_PX, sy * FT_PY, FT_PL, 1.8, .44, 4, 1.9, .6, sy, cleat_pitch=.34)
    pods = a.part('Pods_housing', 'Team')
    for sx in (-1, 1):
        for sy in (-1, 1):
            y = sy * FT_PY
            prof = [(y + p, z) for p, z in ((-2.62, 1.35), (-2.62, 1.85), (-2.25, 2.3), (2.25, 2.3), (2.62, 1.85),
                                             (2.62, 1.35))]
            k.extrude(pods, prof, 2.14, loc=(sx * FT_PX, 0, 0), axis='X', chamfer=.06, corner=.05)
    k.inset(pods, lambda c, n, f: n.z > .9, width=.1, depth=.012)
    hull = a.part('Hull', 'Team')
    k.extrude(hull, [(-6.7, 3.0), (-7.3, 3.45), (-6.6, 4.3), (6.6, 4.3), (7.3, 3.5), (6.8, 3.0)], 7.2, axis='X',
              chamfer=.07, corner=.06)
    k.inset(hull, lambda c, n, f: n.z > .95 and c.z > 4.2, width=.15, depth=.012)

    def sec(y, z1, w1, z0=4.28, w0=2.9):
        return [(-w0, y, z0), (w0, y, z0), (w1, y, z1), (-w1, y, z1)]
    snap = k.snapshot(hull)
    k.sharp_loft(hull, [sec(-5.2, 4.62, 2.85), sec(-4.55, 5.5, 2.62), sec(4.35, 5.5, 2.62), sec(4.75, 5.1, 2.75)],
                 chamfer=.06)
    k.inset(hull, lambda c, n, f: n.z > .95, width=.14, depth=.012, since=snap)

    def bsec(y, z1, w1):
        return [(-2.3, y, 5.48), (2.3, y, 5.48), (w1, y, z1), (-w1, y, z1)]
    k.sharp_loft(hull, [bsec(-4.3, 5.55, 2.28), bsec(-3.85, 6.45, 2.05), bsec(-1.75, 6.45, 2.05),
                        bsec(-1.5, 6.1, 2.12)], chamfer=.05)
    armor = a.part('Armor', 'Armor')
    k.greebles(armor, (0, -5.9, 4.3), (1, 0, 0), (0, 1, 0), (3.4, .8), 5, seed=seed, height=(.06, .14), chamfer=.015,
               avoid=(((3.2, -6.0, 4.3), 1.0), ((-3.2, -6.0, 4.3), 1.0)))
    if roof_greebles:
        for i, s in enumerate((-1, 1)):
            k.greebles(armor, (s * 2.2, .7, 5.5), (1, 0, 0), (0, 1, 0), (.6, 1.5), 3, seed=seed + 1 + i,
                       height=(.05, .12), chamfer=.015, avoid=(((0, 1.0, 5.5), 2.05),))


def _slabs(a):
    """fortress_bastion's slab armour (mb_bosses2.fortress_bastion) as chamfered blocks in the same places."""
    px, pz, plean = _flank((2.9, 4.28), (2.62, 5.5), .5, .08)

    def build(shape):
        for s in (-1, 1):
            for y in (-3.3, -1.1, 1.1, 3.3):
                k.block(shape, (.18, 2.05, 1.05), loc=(s * px, y, pz), rot=(0, -s * plean, 0), chamfer=.04,
                        ends=(True, True))
            for y in (-4.6, -1.55, 1.55, 4.6):
                k.block(shape, (.2, 2.9, 1.1), loc=(s * 3.72, y, 3.72), chamfer=.045, ends=(True, True))
        k.inset(shape, lambda c, n, f: abs(n.x) > .9, width=.09, depth=.012)
    _redo(a, 'Slab_armor', build)


def fortress_bastion(a):
    """The V2 Bastion: p20's fortress_bastion (155 mm casemate `Mount_gun.004`, ZU-23 `Mount_mg` / `.001`, the Kornet
    `Part_missile`) on the V2 crawler, its slab armour, casemate and corner turrets chamfered."""
    p20.fortress_bastion(a)
    _ft_up(a, 2931)
    _slabs(a)
    _redo(a, 'Gun_turret', _faceted([(-.55, .55), (.55, .55), (.7, .15), (.7, -.3), (.45, -.62), (-.45, -.62),
                                     (-.7, -.3), (-.7, .15)], .55, .29, .85, .05))
    _redo(a, 'Casemate', _blocked((3.2, 3.0, 2.4), (0, -7.6, 3.4), chamfer=.09, taper=(.85, .8), ends=(False, True)))
    _redo(a, 'T_house_Mount_gun_004', _blocked((1.8, 1.8, 1.0), (0, .1, .55), chamfer=.08, taper=(.82, .86),
                                               ends=(False, True)))
    k.clean(a)


def fortress_hive(a):
    """The V2 Hive: the drone-carrier fortress on the V2 crawler, its SAM box and launch ramps chamfered."""
    _suffixed(a)                # Mount_*__001 -> Mount_*.001 at finish (build_assets has no round6 finish)
    b2.fortress_hive(a)
    _ft_up(a, 2941)
    pitch = math.radians(30)
    _redo(a, 'Sam_box', _blocked((1.1, 1.5, .95), (0, .05, 1.0), rot=(-pitch, 0, 0), chamfer=.05))
    _redo(a, 'Rack_ramp', _blocked((.9, 2.6, .13), (0, 0, 1.05), rot=(-math.radians(20), 0, 0), chamfer=.03))
    k.clean(a)


# ============================================================================= pass 5b: kronos and moloch
def kronos(a):
    """The V2 Kronos: p20's bucket-wheel excavator; the four track units rebuilt on their `Part_track_*` pivots, the
    turntable, superstructure (sloped roof shoulders), frame, counterweight, armour, cab and bucket blocks
    chamfered with raised panels, seeded fittings on the roof, the gun houses and rocket box chamfered."""
    p20.kronos(a)
    hd.mark(a, False)
    strip(a, ('Tr_*',))
    for pivot, s in (('Part_track_fl', 1), ('Part_track_fr', -1), ('Part_track_rl', 1), ('Part_track_rr', -1)):
        _pivot_track(a, pivot, s, 9.0, 2.45, 3.0, .62, 5, .95, -1 if pivot.endswith(('fl', 'fr')) else 1)

    def frame(shape):
        k.block(shape, (13.0, 22.0, 1.4), loc=(0, 0, 3.2), chamfer=.12, ends=(True, True))
        k.inset(shape, lambda c, n, f: abs(n.x) > .9, width=.1, depth=.01)
    _redo(a, 'Undercarriage_frame', frame)

    def body(shape):
        k.lathe(shape, [(0, -.6), (6.88, -.6), (7.0, -.48), (7.0, .48), (6.88, .6), (0, .6)], loc=(0, 0, 4.4), seg=32)
        k.extrude(shape, [(-5.5, 5.0), (5.5, 5.0), (5.5, 9.15), (5.05, 9.6), (-5.05, 9.6), (-5.5, 9.15)], 20.0,
                  loc=(0, 2.0, 0), axis='Y', chamfer=.12, corner=.1)
        k.inset(shape, lambda c, n, f: n.z > .95 and c.z > 9.5, width=.25, depth=.012)
        k.inset(shape, lambda c, n, f: abs(n.x) > .95 and c.z > 5.5, width=.2, depth=.012)
    _redo(a, 'Body', body)

    def armour(shape):
        k.block(shape, (11.6, 1.0, 3.4), loc=(0, -8.0, 7.0), chamfer=.1, ends=(True, True))
        for y in (-3.0, 3.0, 9.0):
            k.block(shape, (11.4, .6, .4), loc=(0, y, 9.7), chamfer=.05, ends=(True, True))
        k.greebles(shape, (2.6, -5.0, 9.6), (1, 0, 0), (0, 1, 0), (3.4, 2.8), 5, seed=2951, height=(.08, .2),
                   chamfer=.02)
        k.greebles(shape, (0, 5.6, 9.6), (1, 0, 0), (0, 1, 0), (5.0, 2.6), 5, seed=2952, height=(.08, .2),
                   chamfer=.02, avoid=(((4.0, 2.0, 9.6), 1.4), ((-4.0, 2.0, 9.6), 1.6), ((0, 9.0, 9.6), 1.2)))
    _redo(a, 'Body_armor', armour)

    def counterweight(shape):
        k.block(shape, (6.0, 5.0, 3.6), loc=(0, 17.0, 9.0), chamfer=.15, ends=(True, True))
        k.inset(shape, lambda c, n, f: abs(n.x) > .9 or n.y > .9, width=.2, depth=.012)
    _redo(a, 'Counterweight', counterweight)
    _redo(a, 'Cab_box', _blocked((3.0, 3.2, 2.6), (0, 0, 1.3), chamfer=.12, taper=(.94, 1), ends=(False, True)))

    def buckets(shape):
        for i in range(12):
            ang = i * TAU / 12
            k.block(shape, (2.6, 1.6, 1.4), loc=(0, 6.1 * math.sin(ang), 6.1 * math.cos(ang)), rot=(-ang, 0, 0),
                    chamfer=.12, ends=(True, True))
    _redo(a, 'Wheel_buckets', buckets)
    parts.hatch(a, -.6, -6.6, 9.6, .4)
    _redo(a, 'T_house_Turret', _blocked((1.8, 2.2, .9), (0, .1, .5), chamfer=.07, taper=(.82, .86),
                                        ends=(False, True)))
    _redo(a, 'Gun_house_gun', _gun_house(1.6, 1.9, .8))
    _redo(a, 'R_box_Mount_rocket', _blocked((1.6, 2.0, 1.0), (0, 0, .9), rot=(.12, 0, 0), chamfer=.06))
    k.clean(a)


def moloch(a):
    """The V2 Moloch: p20's mobile factory; both track units rebuilt on their `Part_track_l/r` pivots, the hull,
    glacis, workshop, rib plates and doors chamfered with raised panels, seeded fittings on the front deck and the
    workshop roof, the four 120 mm houses and the flak house chamfered."""
    p20.moloch(a)
    hd.mark(a, False)
    strip(a, ('Tr_*',))
    for pivot, s in (('Part_track_l', 1), ('Part_track_r', -1)):
        _pivot_track(a, pivot, s, 23.0, 2.65, 2.4, .62, 11, 1.0, -1)

    def hull(shape):
        k.block(shape, (9.4, 22.4, 3.2), loc=(0, 0, 3.4), chamfer=.15, taper=(.96, .98), ends=(True, True))
        k.inset(shape, lambda c, n, f: abs(n.x) > .9, width=.2, depth=.012)
    _redo(a, 'Hull', hull)

    def armour(shape):
        k.extrude(shape, [(-11.8, 2.0), (-11.8, 3.6), (-10.2, 5.2), (-8.5, 5.2), (-8.5, 2.0)], 9.8, axis='X',
                  chamfer=.08, corner=.06)
        k.inset(shape, lambda c, n, f: n.y < -.5 and n.z > .5, width=.15, depth=.012)
        k.block(shape, (8.8, 1.0, 1.0), loc=(0, -3.6, 5.3), chamfer=.08, ends=(True, True))
        for y in (-2.0, 1.0, 4.0, 7.0):
            k.block(shape, (9.6, .5, .3), loc=(0, y, 5.05), chamfer=.04, ends=(True, True))
        k.greebles(shape, (0, -6.1, 5.0), (1, 0, 0), (0, 1, 0), (5.2, 2.6), 6, seed=2961, height=(.08, .2),
                   chamfer=.02, avoid=(((4.4, -7.6, 5.0), 1.7), ((-4.4, -7.6, 5.0), 1.7)))
        k.greebles(shape, (0, 1.9, 8.6), (1, 0, 0), (0, 1, 0), (6.2, 3.2), 5, seed=2962, height=(.08, .18),
                   chamfer=.02, avoid=(((0, -1.4, 8.6), 1.3), ((4.4, 4.6, 8.6), 1.7), ((-4.4, 4.6, 8.6), 1.7)))
    _redo(a, 'Hull_armor', armour)

    def workshop(shape):
        k.block(shape, (8.2, 13.0, 3.6), loc=(0, 3.2, 6.8), chamfer=.15, ends=(True, True))
        k.inset(shape, lambda c, n, f: n.z > .95, width=.25, depth=.012)
        k.inset(shape, lambda c, n, f: abs(n.x) > .9 or n.y > .9, width=.2, depth=.012)
    _redo(a, 'Workshop', workshop)
    for door in ('Part_door_l', 'Part_door_r'):
        _redo(a, f'Door_{door}', _blocked((3.4, .3, 3.6), (0, .15, 1.8), chamfer=.06))
    for mount, w, d in (('Turret', 2.8, 3.4), ('Mount_gun', 2.8, 3.4), ('Mount_gun.001', 2.6, 3.2),
                        ('Mount_gun.002', 2.6, 3.2)):
        _redo(a, f'T_house_{p20._tag(mount)}', _blocked((w, d, 1.2), (0, .1, .65), chamfer=.08, taper=(.82, .86),
                                                        ends=(False, True)))
    _redo(a, 'Gun_house_mg', _gun_house(1.5, 1.7, .7))
    k.clean(a)


# ============================================================================= pass 5b: the trains
TROUGH = [(-1.6, 1.34), (1.6, 1.34), (1.62, 2.0), (1.42, 2.22), (1.3, 2.22), (1.3, 1.62), (-1.3, 1.62), (-1.3, 2.22),
          (-1.42, 2.22), (-1.62, 2.0)]    # mb_p16_arms._flatcar's open body


def _hull_panels(shape, since=None):
    """Raised panels on a train hull's roofs and vertical sides (clear of the bolted-on plates and grilles)."""
    k.inset(shape, lambda c, n, f: n.z > .95, width=.1, depth=.008, since=since)
    k.inset(shape, lambda c, n, f: abs(n.x) > .95 and c.z > 1.5, width=.08, depth=.008, since=since)


def _car_bodies(a, spans):
    """mb_p16_arms._flatcar's open bodies (headstock faces y0, y1) as chamfered extrudes of the same section."""
    def build(shape):
        for y0, y1 in spans:
            k.extrude(shape, TROUGH, y1 - y0 - .34, loc=(0, (y0 + y1) / 2, 0), axis='Y', chamfer=.03, corner=.02)
        k.inset(shape, lambda c, n, f: abs(n.x) > .99 and abs(c.x) > 1.55, width=.06, depth=.008)
    _redo(a, 'Car_body', build)


def armored_train(a):
    """The V2 armoured train: p16's locomotive, gun wagon and mortar car; the locomotive and wagon hulls as sharp
    lofts on the old sections with raised roof and side panels, the mortar car's body, the turret shell and the
    rocket box chamfered, a few seeded fittings on the wagon roof. Bogies, weapons and mounts as they were."""
    p16.armored_train(a)
    hd.mark(a, False)

    def hull(shape):
        k.sharp_loft(shape, [_sec6(-9.4, 1.5, 1.34, 1.5, 1.9, 1.0, 2.3), _sec6(-8.75, 1.6, 1.34, 1.6, 2.05, 1.25, 2.85),
                             _sec6(-8.2, 1.6, 1.34, 1.6, 2.2, 1.2, 3.35), _sec6(-6.5, 1.6, 1.34, 1.6, 2.2, 1.2, 3.35),
                             _sec6(-6.2, 1.6, 1.34, 1.6, 2.05, 1.15, 2.95), _sec6(-1.1, 1.6, 1.34, 1.6, 2.05, 1.15, 2.95),
                             _sec6(-.6, 1.55, 1.34, 1.55, 2.0, 1.1, 2.7)], chamfer=.06)
        wagon = (1.6, 1.34, 1.6, 2.0, 1.3, 2.62)
        k.sharp_loft(shape, [_sec6(.6, 1.55, 1.34, 1.55, 1.95, 1.2, 2.45), _sec6(1.1, *wagon), _sec6(8.9, *wagon),
                             _sec6(9.4, 1.55, 1.34, 1.55, 1.95, 1.2, 2.45)], chamfer=.06)
        _hull_panels(shape)
    _redo(a, 'Hull', hull)
    _car_bodies(a, [(9.55 + p16.COUPLE, 9.55 + p16.COUPLE + 4.45)])
    _redo(a, 'Turret_body', _faceted([(-1.2, 1.7), (1.2, 1.7), (1.5, .9), (1.5, -.7), (.9, -1.45), (-.9, -1.45),
                                      (-1.5, -.7), (-1.5, .9)], 1.0, .51, .86, .06))
    _redo(a, 'Rocket_box', _hinged_box(1.3, 1.4, .42, math.radians(8), (0, .5, .27), .04))
    k.greebles(a.part('Armor', 'Armor'), (0, 5.2, 2.62), (1, 0, 0), (0, 1, 0), (2.0, .8), 3, seed=2981,
               height=(.05, .1), chamfer=.015, avoid=(((0, 3.2, 2.62), 1.6), ((0, 6.35, 2.62), .8)))
    k.clean(a)


def nuke_train(a):
    """The V2 nuke train: p20's locomotive, missile wagon and four flatcars; the locomotive hull as a sharp loft on the
    old sections and the missile wagon's open body as a chamfered extrude, raised roof and side panels, the flatcar
    bodies, flak turret shell, 152 mm and flak houses, rocket and SAM boxes chamfered. Bogies, the erector and its
    ICBM, weapons and mounts as they were."""
    p20.nuke_train(a)
    hd.mark(a, False)

    def hull(shape):
        k.sharp_loft(shape, [_sec6(-10.45, 1.5, 1.34, 1.5, 1.85, .9, 2.25), _sec6(-9.7, 1.62, 1.34, 1.62, 2.05, 1.2, 2.95),
                             _sec6(-9.0, 1.62, 1.34, 1.62, 2.25, 1.22, 3.45), _sec6(-7.3, 1.62, 1.34, 1.62, 2.25, 1.22, 3.45),
                             _sec6(-7.0, 1.62, 1.34, 1.62, 2.1, 1.18, 3.05), _sec6(-2.3, 1.62, 1.34, 1.62, 2.1, 1.18, 3.05),
                             _sec6(-1.75, 1.57, 1.34, 1.57, 2.05, 1.1, 2.75)], chamfer=.06)
        _hull_panels(shape)
        trough = [(-1.6, 1.34), (1.6, 1.34), (1.62, 2.2), (1.35, 2.7), (1.02, 2.7), (1.02, 2.05), (-1.02, 2.05),
                  (-1.02, 2.7), (-1.35, 2.7), (-1.62, 2.2)]
        snap = k.snapshot(shape)
        k.extrude(shape, trough, 11.1, loc=(0, 4.9, 0), axis='Y', chamfer=.04, corner=.03)
        k.inset(shape, lambda c, n, f: abs(n.x) > .99 and abs(c.x) > 1.55, width=.08, depth=.008, since=snap)
    _redo(a, 'Hull', hull)
    y0 = 10.62 + p16.COUPLE
    y2 = y0 + 4.05 + p16.COUPLE
    _car_bodies(a, [(y0, y0 + 4.05), (y2, y2 + 4.05), (21.0, 25.05), (25.81, 29.86)])
    _redo(a, 'Turret_body', _faceted([(-.9, 1.2), (.9, 1.2), (1.15, .6), (1.15, -.55), (.75, -1.05), (-.75, -1.05),
                                      (-1.15, -.55), (-1.15, .6)], .85, .45, .86, .06))
    _redo(a, 'T_house_Mount_gun', _blocked((2.2, 2.8, 1.1), (0, .1, .6), chamfer=.08, taper=(.82, .86),
                                           ends=(False, True)))
    _redo(a, 'Gun_house_mg_002', _gun_house(1.5, 1.7, .7))
    _redo(a, 'Rocket_box', _hinged_box(1.3, 1.4, .42, math.radians(8), (0, .5, .27), .04))
    _redo(a, 'Sam_box', _hinged_box(1.1, 2.5, .95, math.radians(35), (0, .6, .55), .05))
    k.clean(a)


# ============================================================================= pass 5b: earth_borer
def earth_borer(a):
    """The V2 Earth Worm: mb_phase8's boring machine; V2 running gear on all six track units, the Team armour plates
    along the segments as chamfered plates with raised panels (2 cm thicker, so the chamfer shows), the engine deck,
    its bulkhead and the 57 mm houses chamfered, seeded fittings on the middle segment's spine plate."""
    p8.earth_borer(a)
    hd.mark(a, False)
    strip(a, TRACK_PARTS)
    for y0, y1 in p8.EB_SEGMENTS:
        _track_pair(a, 1.55, (y0 + y1) / 2, y1 - y0 - .6, 1.35, .3, 5, .85, .42, -1, cleat_pitch=.28)
    zc = p8.EB_ZC

    def plates(shape):
        t = .12
        for i, (y0, y1) in enumerate(p8.EB_SEGMENTS):
            p0, p1 = (y0 + 1.4, y0 + 3.1) if i == 0 else (y0 + .45, y1 - .35)
            for deg in (-60, -40, -20, 0, 20, 40, 60):
                u = math.radians(deg)
                rr = 2.25 + t / 2 - .02
                k.block(shape, (.72, p1 - p0, t), loc=(math.sin(u) * rr, (p0 + p1) / 2, zc + math.cos(u) * rr),
                        rot=(0, u, 0), chamfer=.035, ends=(True, True))
        k.inset(shape, lambda c, n, f: Vector((c.x, 0, c.z - zc)).normalized().dot(n) > .97, width=.05, depth=.008)
    _redo(a, 'Hull', plates)
    _redo(a, 'Engine_deck', _blocked((2.6, 4.2, .85), (0, 0, .425), chamfer=.06, taper=(.96, .98), ends=(False, True)))
    _redo(a, 'Engine_armor', _blocked((2.8, .3, .5), (0, -2.0, .55), chamfer=.04))
    for tag in ('gun', 'gun_001'):
        _redo(a, f'Gun_house_{tag}', _gun_house(1.1, 1.2, .58))
    k.greebles(a.part('Armor', 'Armor'), (0, 1.6, zc + 2.35), (1, 0, 0), (0, 1, 0), (.5, 3.0), 4, seed=2991,
               height=(.04, .1), chamfer=.012, avoid=(((1.3, -.2, zc + 2.35), 1.0), ((-1.3, 3.2, zc + 2.35), 1.0)))
    k.clean(a)


def _opts(old, ao=AO):
    return dict(old, ao_strength=ao)


BUILDERS = {
    'behemoth': (behemoth, _opts(p20.BUILDERS['behemoth'][1])),
    'behemoth_inferno': (behemoth_inferno, _opts(b2.BUILDERS['behemoth_inferno'][1])),
    'behemoth_tempest': (behemoth_tempest, _opts(b2.BUILDERS['behemoth_tempest'][1])),
    'fortress_bastion': (fortress_bastion, _opts(p20.BUILDERS['fortress_bastion'][1])),
    'fortress_hive': (fortress_hive, _opts(b2.BUILDERS['fortress_hive'][1])),
    'kronos': (kronos, _opts(p20.BUILDERS['kronos'][1])),
    'moloch': (moloch, _opts(p20.BUILDERS['moloch'][1])),
    'nuke_train': (nuke_train, _opts(p20.BUILDERS['nuke_train'][1])),
    'armored_train': (armored_train, _opts(p16.BUILDERS['armored_train'][1])),
    'earth_borer': (earth_borer, _opts(p8.BUILDERS['earth_borer'][1])),
}
