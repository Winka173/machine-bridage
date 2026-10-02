"""Prompt 27 wave 6 (DECISIONS "27 wave 6a ..."): armed statics (towers) on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Lane B of Docs/models/WAVES_4_6_PLAN.md.

Every tower is the old builder (mb_siege / mb_tower_branches: same nodes, pivots, materials, part names) with its big
hard surfaces swapped for V2 ones: `mb_kit27.extrude` pads, `k.block` plates with two-step chamfers, `k.sharp_loft` gun
houses, `k.inset` panels, seeded `k.greebles`, bolts; the weapon on top is untouched (it reads at 40 px already).
A branch (`_a`, `_b`) runs the base's V2 upgrade, then its own old modification (`mb_tower_branches`), then its own
post-upgrade where the modification added a big surface, so a base and its branches stay in step. The V2 parts keep the
names the branch edits (`strip`, `stretch`) look for, and nothing new hangs on a moving pivot but chamfered copies of
what was there.

Pass 6a: aa_turret, artillery_emplacement, guard_tower, each with `_a` and `_b`.
"""
import math
import random

import mb_kit27 as k
import mb_tower_branches as tb
from frontier_kit import chamfered
from mb_siege import _circle
from mb_towers3 import _runtime_names
from mb_vehicles import ACROSS, R90
from mb_vehicles2 import _axis

AO = .65        # AO strength: V2 towers read paler (wave 3 lesson: a brighter COLOR_0 does not guarantee a brighter card)


def _rect(x0, x1, y0, y1, z):
    return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]


def _build(base, up, mod=None, post=None):
    """(builder, options): the tower's old builder, the V2 upgrade, then the branch's own edit and post-upgrade."""
    build, options = tb.BASES[base] if isinstance(base, str) else base

    def run(a):
        build(a)
        up(a)
        if mod:
            mod(a)
        if post:
            post(a)
        k.clean(a)
    return _runtime_names(run), dict(options, ao_strength=AO)


# ============================================================================= aa_turret (twin 35 mm flak)
def _aa_up(a):
    t = 'Turret'
    tb.strip(a, ('Pad', 'SAM_box'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(4.5, 4.5, .5), .32, loc=(0, 0, .14), axis='Z', chamfer=.06,
              corner=.04)
    # Gun house body (pods and trunnions at |x| >= .6 stay): a sharp loft with the old box's taper and shift.
    tb.strip(a, ('Gun_house',), inside=((-.54, -1.5, .5), (.54, 1.5, 3.0)))
    house = a.part('Gun_house', 'Team', t)
    k.sharp_loft(house, [_rect(-.52, .52, -.6, .9, .55), _rect(-.468, .468, -.415, .875, 1.45)], chamfer=.05)
    k.inset(house, lambda c, n, f: abs(n.x) > .85 and c.z > .7, width=.06, depth=-.012)
    armor = a.part('Turret_armor', 'Armor', t)
    k.greebles(armor, (0, .95, 1.07), (1, 0, 0), (0, 1, 0), (.7, .36), 3, seed=2801, height=(.04, .09), chamfer=.012)
    # SAM box on its arm: chamfered block with side panels (same place and pitch as the old box).
    pitch, length = math.radians(20), 1.5
    at = _axis((1.45, .8, 1.1), pitch)
    box = a.part('SAM_box', 'Team', t)
    k.block(box, (.3, length, .5), loc=tuple(at(length / 2 - .15)), rot=(-pitch, 0, 0), chamfer=.04,
            ends=(True, True))
    k.inset(box, lambda c, n, f: abs(n.x) > .8, width=.06, depth=-.01)


def _aa_b_post(a):
    """The SAM post's revetment as chamfered blocks with panel recesses."""
    tb.strip(a, ('Revetment',))
    wall = a.part('Revetment', 'Concrete')
    k.block(wall, (4.0, .4, .72), loc=(0, -1.8, .66), chamfer=.05, taper=(1, .85))
    for sx in (-1, 1):
        k.block(wall, (.4, 2.6, .72), loc=(sx * 1.8, -.3, .66), chamfer=.05, taper=(.85, 1))
    k.inset(wall, lambda c, n, f: abs(n.z) < .3 and c.z > .4, width=.06, depth=-.012)


# ============================================================================= artillery_emplacement (152 mm)
def _art_up(a):
    t = 'Turret'
    tb.strip(a, ('Platform', 'Gun_shield'))
    k.extrude(a.part('Platform', 'Wood'), _circle(2.55, 24), .08, loc=(0, 0, .03), axis='Z', chamfer=.02)
    # Gun shield: two thick sloped plates either side of the barrel slot, wings, bridge and apron.
    sh = a.part('Gun_shield', 'Team', t)
    lean = (-.14, 0, 0)
    for s in (-1, 1):
        k.block(sh, (.95, .13, .82), loc=(s * .66, -.56, 1.3), rot=lean, chamfer=.035, taper=(.94, 1),
                ends=(True, True))
        k.block(sh, (.5, .13, .66), loc=(s * 1.3, -.42, 1.24), rot=(-.14, 0, s * .55), chamfer=.03,
                ends=(True, True))
    sh.box((.42, .07, .3), loc=(0, -.54, 1.04), rot=lean, bevel=.015, seg=1)
    sh.box((1.9, .06, .3), loc=(0, -.5, .56), rot=(.12, 0, 0), bevel=.015, seg=1)
    k.inset(sh, lambda c, n, f: n.y < -.6, width=.06, depth=.014)
    # Wheel hub nuts and a few fittings on the carriage.
    steel = a.part('Gun_steel', 'Steel', t)
    for s in (-1, 1):
        steel.bolts([(s * 1.352, .15 + .22 * math.cos(u), .56 + .22 * math.sin(u))
                     for u in (i * math.tau / 6 for i in range(6))], r=.034, h=.03, rot=(0, R90, 0), seg=6, bevel=0)
    k.greebles(a.part('Gun_armor', 'Armor', t), (0, .15, .77), (1, 0, 0), (0, 1, 0), (1.8, .4), 4, seed=2811,
               height=(.04, .09), chamfer=.012,
               avoid=(((0, .1, .77), .45), ((-.52, .7, .78), .15), ((.52, .7, .78), .15)))


def _art_a_post(a):
    tb.strip(a, ('Radar_trailer',))
    k.block(a.part('Radar_trailer', 'Team'), (1.0, 1.3, .36), loc=(-2.75, -2.55, .5), chamfer=.04, ends=(True, True))


# ============================================================================= guard_tower
ZW = 7.5       # walkway height of the old builder


def _guard_up(a):
    zw = ZW
    tb.strip(a, ('Blockhouse', 'Walkway', 'Cabin', 'Roof'))
    conc = a.part('Blockhouse', 'Concrete')
    k.extrude(conc, chamfered(3.5, 3.5, .35), .32, loc=(0, 0, .14), axis='Z', chamfer=.05, corner=.03)
    k.block(conc, (2.5, 2.5, 2.6), loc=(0, 0, 1.55), chamfer=.06, taper=(.95, .95))
    for sx in (-1, 1):                                                                       # corner pilasters
        for sy in (-1, 1):
            k.block(conc, (.3, .3, 2.45), loc=(sx * 1.2, sy * 1.2, 1.545), chamfer=.04)
    k.block(conc, (2.7, 2.7, .16), loc=(0, 0, 2.86), chamfer=.04, ends=(True, True))         # cornice
    # Legs: anchor bolts on the base plates, gussets where the bracing meets each leg.
    bolts = a.part('Base_plates', 'Steel')
    b0, b1, z0 = 1.5, 1.3, .28
    for sx in (-1, 1):
        for sy in (-1, 1):
            bolts.bolts([(sx * b0 + dx, sy * b0 + dy, .35) for dx in (-.12, .12) for dy in (-.12, .12)], r=.03, h=.03,
                        seg=6, bevel=0)
    gus = a.part('Leg_gussets', 'Steel')
    for z in (3.0, 5.2, zw - .35):
        r = b0 + (b1 - b0) * (z - z0) / (zw - z0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                k.block(gus, (.34, .34, .16), loc=(sx * r, sy * r, z), chamfer=.025, ends=(True, True))
    # Walkway deck with joists under it.
    k.block(a.part('Walkway', 'Armor'), (3.5, 3.5, .14), loc=(0, 0, zw + .07), chamfer=.035, ends=(True, True))
    joist = a.part('Walkway_joists', 'Steel')
    for y in (-.6, 0, .6):
        joist.box((3.2, .1, .2), loc=(0, y, zw - .09), bevel=0)
    # Cabin: chamfered skirt with recessed panels, corner posts, roof lip.
    cz0, cz1 = zw + .14, zw + 2.3
    cab = a.part('Cabin', 'Team')
    k.block(cab, (2.5, 2.5, .9), loc=(0, 0, cz0 + .45), chamfer=.04)
    k.inset(cab, lambda c, n, f: abs(n.z) < .2, width=.07, depth=-.012)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        k.block(cab, (.2, .2, cz1 - cz0), loc=(sx * 1.16, sy * 1.16, (cz0 + cz1) / 2), chamfer=.03)
    k.block(cab, (2.56, 2.56, .36), loc=(0, 0, cz1 - .18), chamfer=.04, ends=(True, True))
    # Roof deck with a few vents and boxes clear of the gun, searchlight, launcher and aircon.
    roof = a.part('Roof', 'Armor')
    k.block(roof, (2.8, 2.8, .16), loc=(0, 0, cz1 + .06), chamfer=.04, ends=(True, True))
    k.greebles(roof, (.1, .15, cz1 + .14), (1, 0, 0), (0, 1, 0), (1.6, 1.4), 4, seed=2821, height=(.05, .1),
               chamfer=.015, avoid=(((-.45, -.45, 0), .35), ((.8, .8, 0), .35), ((.95, -.95, 0), .4),
                                    ((-.8, 1.02, 0), .5)))


def _nest_up(a):
    """guard_tower_b, the low gun nest: extruded pad and a thick shield with raised panels."""
    tb.strip(a, ('Pad', 'Gun_shield'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(3.5, 3.5, .5), .24, loc=(0, 0, .1), axis='Z', chamfer=.05,
              corner=.03)
    sh = a.part('Gun_shield', 'Team', 'Turret')
    k.block(sh, (1.24, .13, .66), loc=(0, -.46, .92), rot=(-.2, 0, 0), chamfer=.03, taper=(.8, 1), ends=(True, True))
    k.inset(sh, lambda c, n, f: n.y < -.6, width=.06, depth=.012)


BUILDERS = {
    'aa_turret': _build('aa_turret', _aa_up),
    'aa_turret_a': _build('aa_turret', _aa_up, tb.aa_turret_a),
    'aa_turret_b': _build('aa_turret', _aa_up, tb.aa_turret_b, _aa_b_post),
    'artillery_emplacement': _build('artillery_emplacement', _art_up),
    'artillery_emplacement_a': _build('artillery_emplacement', _art_up, tb.artillery_emplacement_a, _art_a_post),
    'artillery_emplacement_b': _build('artillery_emplacement', _art_up, tb.artillery_emplacement_b),
    'guard_tower': _build('guard_tower', _guard_up),
    'guard_tower_a': _build('guard_tower', _guard_up, tb.guard_tower_a),
    'guard_tower_b': _build(tb.BUILDERS['guard_tower_b'], _nest_up),
}
