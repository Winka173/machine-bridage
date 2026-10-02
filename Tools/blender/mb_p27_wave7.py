"""Prompt 27 wave 7 (DECISIONS "27 wave 7a ..."): unarmed statics (structures) on the V2 kit, merged last in
build_assets.all_builders() so these builders win. Lane B of Docs/models/WAVES_4_6_PLAN.md.

Method of wave 6 (mb_p27_wave6): the old builder, a V2 `_up` pass under the same part names, then the branch's own old
edit (mb_tower_branches) so `_a`/`_b` still find the parts they strip. Big hard surfaces become `k.extrude` /
`k.block` with two-step chamfers and `k.inset` panels; the biggest top and side faces are pale (Plaster, PlasterWhite,
Medical). Nodes, pivots and moving parts are untouched; no new moving parts.

Pass 7a: cp_relay, shield_tower, dragons_teeth, minefield, each with `_a` and `_b`.
"""
import random

import mb_kit27 as k
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
