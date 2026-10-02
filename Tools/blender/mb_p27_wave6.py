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
Pass 6b: gun_turret, mg_bunker, rocket_turret, each with `_a` and `_b`.
Pass 6c: atgm_tower, c_ram, each with `_a` and `_b`; gun_pit.
Pass 6d: drone_hangar, ew_tower, each with `_a` and `_b`.
"""
import math
import random

import mb_kit27 as k
from mathutils import Euler, Vector
import mb_tower_branches as tb
from frontier_kit import chamfered
from mb_siege import _circle
from mb_towers3 import _runtime_names
from mb_vehicles import ACROSS, R90
from mb_vehicles2 import _axis

AO = .65        # AO strength: V2 towers read paler (wave 3 lesson: a brighter COLOR_0 does not guarantee a brighter card)


def _rect(x0, x1, y0, y1, z):
    return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]


def _build(base, up, mod=None, post=None, ao=AO):
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
    return _runtime_names(run), dict(options, ao_strength=ao)


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


# ============================================================================= gun_turret (120 mm, concrete ring)
def _gun_up(a):
    t = 'Turret'
    tb.strip(a, ('Emplacement', 'Buttresses', 'Turret_body'))
    conc = a.part('Emplacement', 'Concrete')
    k.extrude(conc, chamfered(5.0, 5.0, 1.1), .34, loc=(0, 0, .15), axis='Z', chamfer=.06, corner=.04, taper=.985)
    k.lathe(conc, [(2.2, .28), (2.2, .34), (2.14, .62), (2.12, .66), (2.04, 1.16), (0, 1.16)], seg=24)
    k.block(conc, (1.5, .9, .82), loc=(0, 2.1, .7), chamfer=.05)                                  # ammunition porch
    k.block(conc, (1.62, .98, .1), loc=(0, 2.1, 1.07), chamfer=.03, ends=(True, True))             # porch lintel
    buttress = a.part('Buttresses', 'Concrete')
    for i in range(8):
        ang = i * math.tau / 8 + math.tau / 16
        k.block(buttress, (.62, .5, .86), loc=(2.2 * math.cos(ang), 2.2 * math.sin(ang), .72), rot=(0, 0, ang),
                chamfer=.05, taper=(.55, .9))
    # Turret body: a sharp loft of the old faceted outline (same taper), cheek and side plates stay.
    outline = [(-.95, -1.72), (.95, -1.72), (1.52, -.95), (1.6, .95), (1.38, 2.05), (-1.38, 2.05), (-1.6, .95),
               (-1.52, -.95)]
    z0, H, tp = .12, .95, .86
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(x, y, z0) for x, y in outline], [(x * tp, y * tp, z0 + H) for x, y in outline]], chamfer=.06)
    k.inset(body, lambda c, n, f: abs(n.z) < .45 and c.z > .3 and c.z < .9 and abs(n.y) > .85, width=.07, depth=-.012)
    k.greebles(a.part('Turret_armor', 'Armor', t), (0, .3, z0 + H + .02), (1, 0, 0), (0, 1, 0), (1.4, .7), 3,
               seed=2901, height=(.03, .07), chamfer=.012, avoid=(((.6, .35, 0), .6), ((-.6, .55, 0), .5),
                                                                   ((0, 1.2, 0), .45), ((-.72, -.72, 0), .45)))


# ============================================================================= mg_bunker (mushroom pillbox)
def _mg_up(a):
    tb.strip(a, ('Pillbox', 'Roof'))
    conc = a.part('Pillbox', 'Concrete')
    slit0, slit1 = .95, 1.35
    # Battered wall with a plinth and one formwork ridge, a flared central column.
    k.lathe(conc, [(1.9, -.02), (1.9, .1), (1.84, .17), (1.82, .5), (1.85, .53), (1.83, .58), (1.72, slit0),
                   (0, slit0)], seg=24)
    k.lathe(conc, [(0, slit0 - .04), (.36, slit0 - .04), (.3, slit0 + .04), (.3, slit1 - .04), (.36, slit1 + .04),
                   (0, slit1 + .04)], seg=12)
    roof = a.part('Roof', 'Concrete')
    k.lathe(roof, [(1.66, slit1), (1.77, slit1 + .03), (1.79, slit1 + .07), (1.79, 1.6), (1.75, 1.66), (1.58, 1.84),
                   (1.0, 1.86), (0, 1.88)], seg=24)
    # Rear steps and a door lintel as chamfered blocks.
    tb.strip(a, ('Steps',))
    k.block(a.part('Steps', 'Concrete'), (.9, .5, .08), loc=(0, 2.08, .03), chamfer=.025)
    k.block(a.part('Steps', 'Concrete'), (1.0, .26, .12), loc=(0, 1.78, .93), chamfer=.03, ends=(True, True))


# ============================================================================= rocket_turret (box launcher)
def _rocket_up(a):
    t = 'Turret'
    tb.strip(a, ('Pad', 'Blast_wall', 'Launcher_base', 'Launcher_box'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(4.5, 4.5, .6), .3, loc=(0, 0, .13), axis='Z', chamfer=.05,
              corner=.04, taper=.99)
    wall = a.part('Blast_wall', 'Concrete')
    ring = chamfered(4.36, 4.36, .9)
    for i in range(len(ring)):
        p, q = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        if p.y > 1.9 and q.y > 1.9:
            continue
        mid, d = (p + q) / 2, q - p
        k.block(wall, (d.length + .02, .32, .62), loc=(mid.x, mid.y, .56), rot=(0, 0, math.atan2(d.y, d.x)),
                chamfer=.05, taper=(1, .7))
    for x, y in ((-1.4, 2.18), (1.4, 2.18)):
        k.block(wall, (.62, .34, .7), loc=(x * .92, y - .02, .6), chamfer=.05, taper=(1, .7))
    k.inset(wall, lambda c, n, f: abs(n.z) < .3 and c.z > .4 and c.z < .8, width=.07, depth=-.01)
    base = a.part('Launcher_base', 'Team', t)
    k.block(base, (1.5, 1.8, .62), loc=(0, .25, .42), chamfer=.05, taper=(.9, .92))
    k.inset(base, lambda c, n, f: abs(n.x) > .8 and c.z > .3, width=.08, depth=-.012)
    pitch = math.radians(30)
    rot = (-pitch, 0, 0)
    hinge = Vector((0, .75, 1.0))
    L, W, Hb = 2.5, 1.9, 1.0
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = hinge - turn @ Vector((0, L / 2 - .25, -Hb / 2 - .05))
    lb = a.part('Launcher_box', 'Team', t)
    k.block(lb, (W, L, Hb), loc=tuple(mid), rot=rot, chamfer=.05, ends=(True, True))
    k.inset(lb, lambda c, n, f: abs(n.x) > .8 and abs(c.y - mid.y) < 1.2, width=.1, depth=-.014)
    k.greebles(a.part('Turret_armor', 'Armor', t), (0, 1.0, .46), (1, 0, 0), (0, 1, 0), (1.4, .36), 3, seed=2911,
               height=(.03, .06), chamfer=.012)


BUILDERS.update({
    'gun_turret': _build('gun_turret', _gun_up),
    'gun_turret_a': _build('gun_turret', _gun_up, tb.gun_turret_a),
    'gun_turret_b': _build('gun_turret', _gun_up, tb.gun_turret_b),
    'mg_bunker': _build('mg_bunker', _mg_up),
    'mg_bunker_a': _build('mg_bunker', _mg_up, tb.mg_bunker_a),
    'mg_bunker_b': _build('mg_bunker', _mg_up, tb.mg_bunker_b),
    'rocket_turret': _build('rocket_turret', _rocket_up),
    'rocket_turret_a': _build('rocket_turret', _rocket_up, tb.rocket_turret_a),
    'rocket_turret_b': _build('rocket_turret', _rocket_up, tb.rocket_turret_b),
})


# ============================================================================= atgm_tower (Kornet-class launcher)
def _atgm_up(a):
    t = 'Turret'
    tb.strip(a, ('Pad', 'Tower', 'Fascia', 'Launcher_sight', 'Base_housing'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(5.2, 5.2, .7), .26, loc=(0, 0, .11), axis='Z', chamfer=.05,
              corner=.03, taper=.99)
    conc = a.part('Tower', 'Plaster')            # pale body: Concrete (#8d8a7e) read dark from the card's high view (6c)
    base = chamfered(3.4, 3.4, .55)
    z0, H, TP = .2, 2.8, .9
    k.sharp_loft(conc, [[(x * (1 - (1 - TP) * f), y * (1 - (1 - TP) * f), z0 + H * f) for x, y in base]
                        for f in (0, 1)], chamfer=.05)                                      # same outline as the old loft
    k.extrude(conc, chamfered(3.56, 3.56, .6), .12, loc=(0, 0, .26), axis='Z', chamfer=.03, corner=.02)  # plinth
    k.extrude(a.part('Roof_slab', 'PlasterWhite'), chamfered(3.7, 3.7, .6), .3, loc=(0, 0, 3.12), axis='Z', chamfer=.04,
              corner=.03)                                                                        # roof slab, palest
    k.extrude(a.part('Fascia', 'Team'), chamfered(3.78, 3.78, .62), .18, loc=(0, 0, 3.12), axis='Z', chamfer=.025,
              corner=.02)
    hous = a.part('Base_housing', 'Team', t)
    k.block(hous, (.92, .82, .3), loc=(0, .02, .23), chamfer=.04, taper=(.92, .9), ends=(True, True))
    k.inset(hous, lambda c, n, f: abs(n.x) > .8, width=.06, depth=-.01)
    sight = a.part('Launcher_sight', 'Armor', t)
    zt_ = .95
    k.block(sight, (.36, .7, .48), loc=(0, -.12, zt_ + .1), chamfer=.04, ends=(True, True))
    k.inset(sight, lambda c, n, f: abs(n.x) > .8, width=.07, depth=-.012)
    sight.box((.4, .12, .04), loc=(0, -.5, zt_ + .31), bevel=0)                                   # sun hood
    k.greebles(a.part('Turret_armor', 'Armor', t), (0, .52, .43), (1, 0, 0), (0, 1, 0), (.4, .2), 2, seed=3001,
               height=(.02, .05), chamfer=.01)


# ============================================================================= c_ram (Phalanx on a trailer)
def _cram_up(a):
    tb.strip(a, ('Pad', 'Trailer_deck', 'Power_cabinet', 'Cabinet_roof', 'Base_plate', 'Pedestal', 'Tool_boxes',
                 'Mast_footing'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(5.6, 5.6, .7), .18, loc=(0, 0, .07), axis='Z', chamfer=.04,
              corner=.03, taper=.99)
    dz = 1.04
    deck = a.part('Trailer_deck', 'Team')
    k.block(deck, (2.3, 4.2, .14), loc=(0, 0, .97), chamfer=.03, ends=(True, True))
    cab = a.part('Power_cabinet', 'Team')
    cy_ = 1.65
    k.block(cab, (1.7, .7, .72), loc=(0, cy_, dz + .36), chamfer=.05, ends=(True, True))
    k.inset(cab, lambda c, n, f: n.y > .8 or (n.y < -.8 and c.x < 0), width=.07, depth=-.012)
    k.block(a.part('Cabinet_roof', 'Armor'), (1.76, .76, .05), loc=(0, cy_, dz + .74), chamfer=.015)
    for s in (-1, 1):
        k.block(a.part('Tool_boxes', 'Armor'), (.3, .7, .34), loc=(s * .8, -1.5, .68), chamfer=.03,
                ends=(True, True))
    mx, my = 0.0, .2
    k.block(a.part('Base_plate', 'Armor'), (1.3, 1.3, .2), loc=(mx, my, dz + .09), chamfer=.04, ends=(True, True))
    k.lathe(a.part('Pedestal', 'Medical'), [(0, dz + .19), (.56, dz + .19), (.58, dz + .22), (.58, dz + .45),
                                          (.6, dz + .48), (.6, dz + .52), (.56, dz + .57), (0, dz + .57)],
            loc=(mx, my, 0), seg=18)
    k.block(a.part('Mast_footing', 'Concrete'), (.5, .5, .2), loc=(2.15, 2.15, .25), chamfer=.04)
    k.greebles(deck, (0, -.3, dz + .02), (1, 0, 0), (0, 1, 0), (1.8, 1.4), 3, seed=3011, height=(.02, .05),
               chamfer=.01, avoid=(((0, .2, 0), .9), ((0, 1.65, 0), 1.0)))


# ============================================================================= gun_pit (lift gun)
def _pit_up(a):
    tb.strip(a, ('Revetment', 'Lift_table', 'Mantlet', 'Turret_armor'))
    wall = a.part('Revetment', 'Wood')
    n, hr, rp = 20, .88, 2.02
    gap = .3
    a0, a1 = R90 + gap, R90 + math.tau - gap
    step = (a1 - a0) / n
    for i in range(n):
        u = a0 + (i + .5) * step
        chord = 2 * rp * math.sin(step / 2) + .02
        k.block(wall, (chord, .13, hr), loc=(rp * math.cos(u), rp * math.sin(u), hr / 2), rot=(0, 0, u + R90),
                chamfer=.03, taper=(.97, .9))
    t = 'Turret'
    steel = a.part('Lift_table', 'Steel', t)
    k.extrude(steel, _circle(1.22, 24), .12, loc=(0, 0, -.07), axis='Z', chamfer=.025)
    steel.cyl(.2, 1.72, loc=(0, 0, -.13 - .86), seg=12, bevel=0)                                   # ram
    zc = .4
    mant = a.part('Mantlet', 'Armor', t)
    k.block(mant, (.6, .34, .44), loc=(0, -.93, zc), chamfer=.06, ends=(True, True))
    mant.cyl(.15, .16, loc=(0, -1.12, zc), rot=(math.pi / 2, 0, 0), seg=12, bevel=.02, bseg=1)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.22, .3, .2), loc=(.46, -.5, .6), chamfer=.03, ends=(True, True))
    k.block(tarm, (.84, .44, .32), loc=(0, 1.02, .3), chamfer=.04, ends=(True, True))
    k.inset(tarm, lambda c, n, f: n.y > .8 or abs(n.x) > .8, width=.06, depth=-.01)
    tarm.cyl(.28, .2, loc=(-.38, .12, .67), seg=14, bevel=.03, bseg=1)


# ============================================================================= ew_tower (jamming mast)
def _ew_up(a):
    tb.strip(a, ('Pad', 'Footings', 'Base_plates', 'Platform', 'Shelter_blocks', 'Shelter', 'Shelter_roof', 'Aircon'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(4.0, 4.0, .45), .26, loc=(0, 0, .11), axis='Z', chamfer=.05,
              corner=.03, taper=.99)
    top = .24
    mx, my, hw0, z1 = .3, -.25, .6, 6.6
    bolts = a.part('Base_plates', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = mx + sx * hw0, my + sy * hw0
            k.block(a.part('Footings', 'Concrete'), (.46, .46, .14), loc=(x, y, top + .04), chamfer=.035,
                    ends=(True, True))
            bolts.bolts([(x + dx, y + dy, top + .11) for dx in (-.15, .15) for dy in (-.15, .15)], r=.025, h=.03,
                        seg=6, bevel=0)
    k.block(a.part('Platform', 'Armor'), (1.3, 1.3, .13), loc=(mx, my, z1 + .045), chamfer=.03, ends=(True, True))
    sx_, sy_, sw, sd, sh = -.62, 1.3, 1.9, 1.05, 1.3
    for x in (-1, 1):
        k.block(a.part('Shelter_blocks', 'Concrete'), (.3, sd + .1, .14), loc=(sx_ + x * (sw / 2 - .25), sy_, top + .05),
                chamfer=.03, ends=(True, True))
    zs = top + .11
    sh_ = a.part('Shelter', 'Team')
    k.block(sh_, (sw, sd, sh), loc=(sx_, sy_, zs + sh / 2), chamfer=.05, ends=(True, True))
    k.inset(sh_, lambda c, n, f: n.y > .8 or n.x > .8, width=.08, depth=-.012)
    roof = a.part('Shelter_roof', 'Medical')                                                    # pale top
    k.block(roof, (sw + .06, sd + .06, .13), loc=(sx_, sy_, zs + sh), chamfer=.035, ends=(True, True))
    ac = a.part('Aircon', 'Fuel')
    k.block(ac, (.36, .7, .62), loc=(sx_ - sw / 2 - .15, sy_, zs + .6), chamfer=.04)
    k.inset(ac, lambda c, n, f: n.y > .8 or n.y < -.8, width=.05, depth=-.01)


# ============================================================================= drone_hangar (arch shelter, roof deck)
def _hangar_up(a):
    tb.strip(a, ('Pad', 'Headwall', 'Headwall_cap', 'Fascia', 'Door_box', 'Container', 'Container_blocks', 'Deck',
                 'Hangar'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(8.0, 8.0, .9), .22, loc=(0, 0, .09), axis='Z', chamfer=.05,
              corner=.04, taper=.995)
    top = .2
    hx, A, B, th = -.55, 2.45, 2.8, .32
    yf, yb = -2.25, 2.5
    n = 12
    from mb_towers3 import _arch
    outer = _arch(hx, A, B, top, 0, math.pi, n)
    inner = _arch(hx, A - th, B - th * .95, top, math.pi, 0, n)
    ring = outer + inner
    k.sharp_loft(a.part('Hangar', 'Concrete'), [[(x, y, z) for x, z in ring] for y in (yf, -1.0, .25, 1.5, yb)],
                 chamfer=.05)
    # Headwall: chamfered piers and lintel with panels on the back, a thicker Team fascia, a lipped cap.
    hw = a.part('Headwall', 'Concrete')
    y0_, y1_ = -2.8, -2.2
    yc_, dp = (y0_ + y1_) / 2, y1_ - y0_
    dw, dh, H = 1.1, 2.1, 3.25
    k.block(hw, (2.75 - dw, dp, H), loc=(hx - (2.75 + dw) / 2, yc_, top + H / 2), chamfer=.05, ends=(True, True))
    k.block(hw, (2.75 - dw, dp, H), loc=(hx + (2.75 + dw) / 2, yc_, top + H / 2), chamfer=.05, ends=(True, True))
    k.block(hw, (2 * dw + .1, dp, H - dh), loc=(hx, yc_, top + dh + (H - dh) / 2), chamfer=.05, ends=(True, True))
    k.inset(hw, lambda c, nn, f: nn.y > .8, width=.12, depth=-.02)
    k.block(a.part('Fascia', 'Team'), (5.56, .13, .32), loc=(hx, y0_ - .045, top + H - .26), chamfer=.025)
    k.block(a.part('Headwall_cap', 'Concrete'), (5.6, dp + .1, .13), loc=(hx, yc_, top + H + .045), chamfer=.035,
            ends=(True, True))
    k.block(a.part('Door_box', 'Team'), (2 * dw + .3, .36, .42), loc=(hx, y0_ - .17, top + dh + .24), chamfer=.04)
    # Roof deck: chamfered plate (top at zd as before).
    zd = top + B + .45
    dx, dy = hx, .7
    k.block(a.part('Deck', 'Armor'), (2.5, 3.2, .13), loc=(dx, dy, zd - .065), chamfer=.03, ends=(True, True))
    # Ground-control container: chamfered body with panels on the back and the far side, roof blocks.
    gx, gy, gw, gd, gh = 2.85, .3, 1.25, 2.6, 1.25
    for sy in (-1, 1):
        k.block(a.part('Container_blocks', 'Concrete'), (gw + .1, .3, .14), loc=(gx, gy + sy * (gd / 2 - .3), top + .05),
                chamfer=.03, ends=(True, True))
    zg = top + .1
    cont = a.part('Container', 'Team')
    k.block(cont, (gw, gd, gh), loc=(gx, gy, zg + gh / 2), chamfer=.05, ends=(True, True))
    k.inset(cont, lambda c, nn, f: nn.x < -.8, width=.09, depth=-.012)


BUILDERS.update({
    'atgm_tower': _build(tb.BASES['atgm_tower'], _atgm_up, ao=.5),
    'atgm_tower_a': _build(tb.BASES['atgm_tower'], _atgm_up, tb.atgm_tower_a, ao=.5),
    'atgm_tower_b': _build(tb.BASES['atgm_tower'], _atgm_up, tb.atgm_tower_b, ao=.5),
    'c_ram': _build(tb.BASES['c_ram'], _cram_up),
    'c_ram_a': _build(tb.BASES['c_ram'], _cram_up, tb.c_ram_a),
    'c_ram_b': _build(tb.BASES['c_ram'], _cram_up, tb.c_ram_b),
    'gun_pit': _build(tb.BASES['gun_pit'], _pit_up),
    'ew_tower': _build('ew_tower', _ew_up),
    'ew_tower_a': _build('ew_tower', _ew_up, tb.ew_tower_a),
    'ew_tower_b': _build('ew_tower', _ew_up, tb.ew_tower_b),
    'drone_hangar': _build('drone_hangar', _hangar_up),
    'drone_hangar_a': _build('drone_hangar', _hangar_up, tb.drone_hangar_a),
    'drone_hangar_b': _build('drone_hangar', _hangar_up, tb.drone_hangar_b),
})
