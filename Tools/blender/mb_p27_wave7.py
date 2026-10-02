"""Prompt 27 wave 7 (DECISIONS "27 wave 7a ..."): unarmed statics (structures) on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Lane B of Docs/models/WAVES_4_6_PLAN.md.

Method of wave 6 (mb_p27_wave6): the old builder, a V2 `_up` pass under the same part names, then the branch's own old
edit (mb_tower_branches) so `_a`/`_b` still find the parts they strip. Big hard surfaces become `k.extrude` /
`k.block` with two-step chamfers and `k.inset` panels; the biggest top and side faces are pale (Plaster, PlasterWhite,
Medical). Nodes, pivots and moving parts are untouched; no new moving parts.

Pass 7a: cp_relay, shield_tower, dragons_teeth, minefield, each with `_a` and `_b`.
Pass 7b: barrage_balloon, blast_wall, fire_control_centre, inflatable_decoy, troop_shelter, logistics_station,
radar_site, repair_bay, ammo_dump, targeting_station (no branches). Lead rule: pale sand/concrete, small COLOR_0 gains.
"""
import math
import random

import mb_kit27 as k
import mb_p25_models2
import mb_p25_new
import mb_phase8
import mb_siege
import mb_tower_branches as tb
from frontier_kit import chamfered
from mb_towers3 import _runtime_names

AO = .65


def _build(base, up, mod=None, post=None, ao=AO):
    build, options = tb.BASES[base]

    def run(a):
        build(a)
        up(a)
        if mod:
            mod(a)
        if post:
            post(a)
        k.clean(a)
    return _runtime_names(run), dict(options, ao_strength=ao)


# ============================================================================= cp_relay
def _cp_up(a):
    top = .24
    tb.strip(a, ('Pad', 'Shelter', 'Shelter_roof', 'Footings', 'Aircon'))
    k.extrude(a.part('Pad', 'Plaster'), chamfered(4.0, 4.0, .45), .26, loc=(0, 0, .11), axis='Z', chamfer=.05,
              corner=.04, taper=.99)
    sx, sy = -.75, .7
    sh = a.part('Shelter', 'Team')
    k.block(sh, (2.2, 1.5, 1.35), loc=(sx, sy, top + .655), chamfer=.05, ends=(True, True))
    k.inset(sh, lambda c, n, f: n.y > .8 or n.x > .8 or n.x < -.8, width=.09, depth=-.012)
    k.block(a.part('Shelter_roof', 'PlasterWhite'), (2.34, 1.64, .1), loc=(sx, sy, 1.62), chamfer=.03,
            ends=(True, True))
    mx, my = 1.15, -1.0
    for qx in (-1, 1):
        for qy in (-1, 1):
            k.block(a.part('Footings', 'Concrete'), (.34, .34, .12), loc=(mx + qx * .38, my + qy * .38, top + .06),
                    chamfer=.03)
    air = a.part('Aircon', 'Medical')
    k.block(air, (.24, .7, .55), loc=(sx + 1.21, sy + .1, .75), chamfer=.03, ends=(True, True))


# ============================================================================= shield_tower
def _shield_up(a):
    tb.strip(a, ('Pad', 'Base', 'Pylon'))
    k.extrude(a.part('Pad', 'Plaster'), chamfered(7.2, 7.2, .9), .3, loc=(0, 0, .13), axis='Z', chamfer=.06,
              corner=.04, taper=.99)
    # Base: same ring and taper as the old prism (plates and door sit on its faces), chamfered.
    z0, h = .26, 1.9
    k.extrude(a.part('Base', 'Team'), chamfered(4.6, 4.6, 1.2), h, loc=(0, 0, z0 + h / 2), axis='Z', chamfer=.06,
              taper=.88)
    k.extrude(a.part('Base_roof', 'PlasterWhite'), chamfered(4.12, 4.12, 1.06), .09, loc=(0, 0, 2.2), axis='Z',
              chamfer=.025)
    # Pylon: the old frustum in pale Medical so the tallest big surface is not dark.
    a.part('Pylon', 'Medical').cyl(.85, 5.5, r2=.45, loc=(0, 0, (2.14 + 7.64) / 2), seg=8, bevel=.04)


# ============================================================================= dragons_teeth
def _teeth_up(a):
    tb.strip(a, ('Footing', 'Teeth'))
    k.extrude(a.part('Footing', 'Plaster'), chamfered(5.0, 2.3, .25), .14, loc=(0, 0, 0), axis='Z', chamfer=.03,
              corner=.02)
    teeth = a.part('Teeth', 'Plaster')
    rng = random.Random(366)                       # the old builder's draw order, so every tooth stays put
    rows = ((-.42, (-2.083, -.417, 1.25), .86, .82), (.55, (-1.25, .417, 2.083), .92, 1.06))
    for y, xs, b, hgt in rows:
        for x in xs:
            broken = (x, y) == (-1.25, .55)
            hh = .62 if broken else hgt + rng.uniform(-.06, .05)
            tp = (.6 if broken else .4) + rng.uniform(-.03, .03)
            px, py = x + rng.uniform(-.04, .04), y + rng.uniform(-.04, .04)
            rot = (rng.uniform(-.025, .025), rng.uniform(-.025, .025), rng.uniform(-.14, .14))
            rng.uniform(-.04, .04)
            rng.uniform(-.04, .04)
            k.block(teeth, (b, b, hh), loc=(px, py, .05 + hh / 2),
                    rot=rot, chamfer=.05, taper=(tp, tp), ends=(False, True))
    k.inset(teeth, lambda c, n, f: abs(n.z) < .5 and c.z > .3, width=.08, depth=-.015)


# ============================================================================= minefield
def _mine_up(a):
    tb.strip(a, ('Ground',))
    # Pale sand patch (the old grid, so shading keeps interior vertices) with a low timber kerb round it.
    import math
    from mathutils import Vector, noise
    nx, e = 8, 2.4
    verts, faces = [], []
    for j in range(nx + 1):
        for i in range(nx + 1):
            x, y = -e + 2 * e * i / nx, -e + 2 * e * j / nx
            edge = i in (0, nx) or j in (0, nx)
            if not edge:
                x += .08 * noise.noise(Vector((x, y, 3.0)))
                y += .08 * noise.noise(Vector((x, y, 5.0)))
            z = -.01 if edge else .012 + .012 * noise.noise(Vector((x * 1.3, y * 1.3, 1.0)))
            verts.append((x, y, z))
    for j in range(nx):
        for i in range(nx):
            q = j * (nx + 1) + i
            faces.append((q, q + 1, q + nx + 2, q + nx + 1))
    a.part('Ground', 'Plaster').mesh(verts, faces)
    kerb = a.part('Kerb', 'Wood')
    for s in (-1, 1):
        k.block(kerb, (4.8, .1, .1), loc=(0, s * 2.35, -.01), chamfer=.02, ends=(True, True))
        k.block(kerb, (.1, 4.6, .1), loc=(s * 2.35, 0, -.01), chamfer=.02, ends=(True, True))


BUILDERS = {
    'cp_relay': _build('cp_relay', _cp_up),
    'cp_relay_a': _build('cp_relay', _cp_up, tb.cp_relay_a),
    'cp_relay_b': _build('cp_relay', _cp_up, tb.cp_relay_b),
    'shield_tower': _build('shield_tower', _shield_up),
    'shield_tower_a': _build('shield_tower', _shield_up, tb.shield_tower_a),
    'shield_tower_b': _build('shield_tower', _shield_up, tb.shield_tower_b),
    'dragons_teeth': _build('dragons_teeth', _teeth_up, ao=.6),
    'dragons_teeth_a': _build('dragons_teeth', _teeth_up, tb.dragons_teeth_a, ao=.6),
    'dragons_teeth_b': _build('dragons_teeth', _teeth_up, tb.dragons_teeth_b, ao=.6),
    'minefield': _build('minefield', _mine_up),
    'minefield_a': _build('minefield', _mine_up, tb.minefield_a),
    'minefield_b': _build('minefield', _mine_up, tb.minefield_b),
}


# ============================================================================= pass 7b
def _plain(base, up, ao=.9):
    """A model without branches: its own old builder, then the V2 pass."""
    build, options = base

    def run(a):
        build(a)
        up(a)
        k.clean(a)
    return _runtime_names(run), dict(options, ao_strength=ao)


def _walls(shape, sel=None, width=.09, depth=-.014):
    """Recessed panels on the vertical faces of a block (not its chamfer facets)."""
    k.inset(shape, lambda c, n, f: (abs(n.x) > .95 or abs(n.y) > .95) and (sel is None or sel(c, n)),
            width=width, depth=depth)


def _slab(a, name, mat, w, d, h, z, cut=.3, c=.03):
    k.extrude(a.part(name, mat), chamfered(w, d, cut), h, loc=(0, 0, z), axis='Z', chamfer=c, corner=.02)


def _blast_up(a):
    tb.strip(a, ('Gabions',))
    fill = a.part('Gabions', 'Sandbag')
    for i in range(5):
        x = (i - 2) * .95
        for y, z in ((-.47, .58), (.47, .58), (0, 1.78)):
            k.block(fill, (.92, .92, 1.15), loc=(x, y, z), chamfer=.07, taper=(.96, .96), ends=(False, True))


def _decoy_up(a):
    tb.strip(a, ('Blower',))
    bl = a.part('Blower', 'Armor')
    k.block(bl, (.6, .5, .5), loc=(2.2, -1.2, .25), chamfer=.05, ends=(False, True))
    _walls(bl, width=.07, depth=-.012)
    stakes = a.part('Stakes', 'Concrete')
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        k.block(stakes, (.16, .16, .14), loc=(sx * 2.2, sy * 2.1, .07), chamfer=.03)


def _fcc_up(a):
    tb.strip(a, ('Pad', 'Shelters', 'Generator'))
    k.extrude(a.part('Pad', 'Plaster'), chamfered(5.8, 5.8, .5), .12, loc=(0, 0, .06), axis='Z', chamfer=.03,
              corner=.03)
    sh = a.part('Shelters', 'Team')
    k.block(sh, (2.4, 4.2, 2.3), loc=(-1.3, 0, 1.27), chamfer=.07, ends=(False, True))
    k.block(sh, (2.0, 3.0, 2.0), loc=(1.2, .5, 1.12), chamfer=.07, ends=(False, True))
    g = a.part('Generator', 'Armor')
    k.block(g, (1.0, 1.3, .9), loc=(1.8, -1.8, .57), chamfer=.05, ends=(False, True))
    _walls(g, width=.07, depth=-.012)


def _troop_up(a):
    tb.strip(a, ('Berm', 'Roof', 'Ramp'))
    k.extrude(a.part('Berm', 'Dirt'), [(-3.0, 0), (-2.0, 1.6), (2.0, 1.6), (3.0, 0)], 5.0, axis='X', chamfer=.12,
              corner=.1)
    roof = a.part('Roof', 'Rock')
    k.block(roof, (4.2, 4.0, .4), loc=(0, 0, 1.75), chamfer=.07, ends=(True, True))
    _walls(roof, width=.07, depth=-.012)
    k.block(a.part('Ramp', 'Concrete'), (1.8, 1.0, .12), loc=(0, 3.0, .15), rot=(-.25, 0, 0), chamfer=.03,
            ends=(True, True))


def _balloon_up(a):
    tb.strip(a, ('Winch',))
    w = a.part('Winch', 'Armor')
    k.block(w, (2.4, 3.0, .9), loc=(0, 0, .55), chamfer=.08, ends=(True, True))
    _walls(w, lambda c, n: c.z > .3, width=.09, depth=-.014)
    _slab(a, 'Pad', 'Plaster', 3.2, 4.0, .08, .02, cut=.4, c=.02)


def _logi_up(a):
    tb.strip(a, ('Pad', 'Containers_ContainerRed', 'Containers_ContainerBlue', 'Containers_Team', 'Office',
                 'Office_roof'))
    k.extrude(a.part('Pad', 'Rock'), chamfered(8.0, 10.0, .8), .1, loc=(0, 0, .03), axis='Z', chamfer=.03,
              corner=.03)
    z = .1
    for x, y, yaw, mat, tier in ((-2.4, -3.2, 0, 'ContainerRed', 2), (-2.4, -1.9, 0, 'ContainerBlue', 2),
                                 (-2.4, -.6, 0, 'Team', 1), (1.6, -3.2, 0, 'Team', 2),
                                 (1.6, -1.9, 0, 'ContainerRed', 1), (-2.4, 2.8, math.pi / 2, 'ContainerBlue', 1)):
        for t in range(tier):
            m = mat if t == 0 else ('ContainerBlue' if mat != 'ContainerBlue' else 'ContainerRed')
            p = a.part(f'Containers_{m}', m)
            k.block(p, (2.4, 1.0, 1.05), loc=(x, y, z + t * 1.07 + .525), rot=(0, 0, yaw), chamfer=.04,
                    ends=(False, True))
            k.inset(p, lambda c, n, f: abs(n.z) < .3 and abs(n.y) > .95 and abs(c.x - x) < 1.0 and
                    abs(c.y - y) > .3, width=.1, depth=-.012)
    off = a.part('Office', 'MetalSheet')
    k.block(off, (2.2, 1.5, 2.2), loc=(2.6, 3.6, z + 1.1), chamfer=.04, ends=(False, True))
    k.block(a.part('Office_roof', 'Team'), (2.4, 1.7, .12), loc=(2.6, 3.6, z + 2.26), chamfer=.03,
            ends=(True, True))


def _radar_up(a):
    tb.strip(a, ('Pad', 'Shelter', 'Generator'))
    k.extrude(a.part('Pad', 'Plaster'), chamfered(8.1, 7.9, .7), .1, loc=(0, 0, .03), axis='Z', chamfer=.03,
              corner=.03)
    z = .1
    sh = a.part('Shelter', 'Team')
    k.block(sh, (3.2, 2.2, 2.3), loc=(-2.0, -2.4, z + 1.15), chamfer=.06, ends=(False, True))
    k.inset(sh, lambda c, n, f: abs(n.x) > .95 or n.y > .95, width=.11, depth=-.014)
    k.block(a.part('Shelter_roof', 'PlasterWhite'), (3.3, 2.3, .08), loc=(-2.0, -2.4, z + 2.34), chamfer=.02,
            ends=(True, True))
    g = a.part('Generator', 'Armor')
    k.block(g, (1.6, 1.0, 1.0), loc=(-2.4, 2.6, z + .5), chamfer=.05, ends=(False, True))
    _walls(g, width=.08, depth=-.012)


def _bay_up(a):
    tb.strip(a, ('Pad', 'Walls', 'Roof', 'Vehicle_in_bay', 'Repair_hull', 'Repair_turret'))
    k.extrude(a.part('Pad', 'Concrete'), chamfered(10.1, 14.2, .9), .1, loc=(0, 0, .03), axis='Z', chamfer=.03,
              corner=.03)
    z = .1
    walls = a.part('Walls', 'Concrete')
    for y in (-6.9, 6.9):
        k.block(walls, (4.8, .25, 4.0), loc=(2.55, y, z + 2.0), chamfer=.04, ends=(False, True))
    k.block(walls, (.25, 13.9, 4.0), loc=(4.9, 0, z + 2.0), chamfer=.04, ends=(False, True))
    k.block(walls, (.5, .5, 4.0), loc=(.4, 0, z + 2.0), chamfer=.04, ends=(False, True))
    roof = a.part('Roof', 'Corrugated')
    for sx, rot in ((1.4, .32), (3.75, -.32)):
        k.block(roof, (2.6, 14.4, .12), loc=(sx, 0, z + 4.45), rot=(0, rot, 0), chamfer=.04, ends=(False, True))
    veh = a.part('Vehicle_in_bay', 'Armor')
    k.block(veh, (2.3, 4.6, 1.4), loc=(2.6, 3.3, z + .8), chamfer=.1, ends=(False, True))
    hull = a.part('Repair_hull', 'Team')
    k.block(hull, (2.6, 5.4, 1.1), loc=(-2.4, -.5, z + .75), chamfer=.09, ends=(False, True))
    _walls(hull, lambda c, n: c.z > .5, width=.12, depth=-.014)
    k.block(a.part('Repair_turret', 'Armor'), (1.8, 2.0, .6), loc=(-2.4, -3.8, z + .32), chamfer=.07,
            ends=(False, True))


def _crate_v2(a, loc, size=(1.1, .5, .38), yaw=0.0, parent=None, band=True, mat='Crate'):
    w, d, h = size
    m = mb_siege._frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    body = a.part('Crates', mat, parent)
    k.block(body, (w, d, h), loc=m @ mb_siege.Vector((0, 0, h / 2)), rot=rot, chamfer=.035, ends=(True, True))
    k.inset(body, lambda c, n, f: n.z > .95, width=.06, depth=-.01)
    cleat = a.part('Crate_cleats', 'Wood', parent)
    for s in (-1, 1):
        cleat.box((.06, d + .025, h + .02), loc=m @ mb_siege.Vector((s * (w / 2 - .09), 0, h / 2)), rot=rot,
                  bevel=0)
    if band:
        a.part('Crate_bands', 'Hazard', parent).box((w * .3, d + .03, .06),
                                                    loc=m @ mb_siege.Vector((0, 0, h * .66)), rot=rot, bevel=0)


def _ammo_build(a):
    old = mb_siege.crate
    mb_siege.crate = _crate_v2
    try:
        mb_siege.ammo_dump(a)
    finally:
        mb_siege.crate = old


def _ammo_up(a):
    _slab(a, 'Ground', 'Rock', 5.4, 4.6, .06, .01, cut=.5, c=.02)


def _target_up(a):
    tb.strip(a, ('Pad', 'Cabin', 'Cabin_roof'))
    k.extrude(a.part('Pad', 'Plaster'), chamfered(8.0, 6.5, .7), .3, loc=(0, 0, .1), axis='Z', chamfer=.04,
              corner=.04)
    cx, cy, cw, cd, ch, z0 = -1.6, .2, 3.4, 2.8, 2.6, .25
    k.block(a.part('Cabin', 'Team'), (cw, cd, ch), loc=(cx, cy, z0 + ch / 2), chamfer=.07, ends=(False, True))
    k.block(a.part('Cabin_roof', 'Team'), (cw + .3, cd + .3, .14), loc=(cx, cy, z0 + ch + .05), chamfer=.04,
            ends=(True, True))


BUILDERS.update({
    'blast_wall': _plain(mb_p25_new.BUILDERS['blast_wall'], _blast_up, ao=.8),
    'inflatable_decoy': _plain(mb_p25_new.BUILDERS['inflatable_decoy'], _decoy_up, ao=0.85),
    'fire_control_centre': _plain(mb_p25_new.BUILDERS['fire_control_centre'], _fcc_up),
    'troop_shelter': _plain(mb_p25_new.BUILDERS['troop_shelter'], _troop_up),
    'barrage_balloon': _plain(mb_p25_new.BUILDERS['barrage_balloon'], _balloon_up, ao=0.8),
    'logistics_station': _plain(mb_p25_models2.BUILDERS['logistics_station'], _logi_up, ao=1.0),
    'radar_site': _plain(mb_p25_models2.BUILDERS['radar_site'], _radar_up, ao=0.85),
    'repair_bay': _plain(mb_p25_models2.BUILDERS['repair_bay'], _bay_up, ao=1.0),
    'ammo_dump': _plain((_ammo_build, mb_siege.BUILDERS['ammo_dump'][1]), _ammo_up),
    'targeting_station': _plain(mb_phase8.BUILDERS['targeting_station'], _target_up),
})
