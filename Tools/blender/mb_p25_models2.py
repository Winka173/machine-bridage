"""Machine Brigade prompt 25 B2, part 2 (DECISIONS 25B2 "Part 2"): the rest of the models rebuilt from the balance
sheet's "Hình dạng (cho AI vẽ)" notes and drawing guide, at the sheet's target sizes (ground 0.8 x real, aircraft
0.4 x real), drawn for a balance.json "scale" of 1.0 (the data's `modelSize` fits any model's length to the sheet).

The rules are part 1's (mb_p25_models' module notes): silhouette first, the identifying parts 10-20 % over scale,
the triangle budgets (light 1,500-3,000, tanks 3,000-5,000, aircraft 2,000-4,000), nothing thinner than 0.1 m that
would shimmer, every node, mount and muzzle name the game looks up kept, `Point_exhaust` / `Point_fire` empties, Team
as the side's colour. Conventions are mb_vehicles': metres, +Z up, -Y the front, +X the vehicle's left, the origin on
the ground at the hull centre.

Headless: blender --background --python Tools/blender/build_assets.py -- supply_truck
"""
import math

from mathutils import Vector

import mb_detail as hd
import mb_vehicles as mv
from mb_p25_models import _lean_tracks, _scale_asset  # noqa: F401  (shared with part 1)
from mb_vehicles import ACROSS, FORWARD, R90, TAU  # noqa: F401


def _wheels(a, xs, ys, r, width, z=None, seg=10, disc='Armor', hubs=False):
    """Big exposed wheels: a bevelled tyre and a painted disc on each (x, y) (a hub too with hubs=True); z is the
    axle height (r)."""
    z = r if z is None else z
    tyres = a.part('Tyres', 'Rubber')
    discs = a.part('Wheels', disc)
    for x in xs:
        for y in ys:
            tyres.cyl(r, width, loc=(x, y, z), rot=ACROSS, seg=seg, bevel=min(.05, r * .12), bseg=1)
            discs.cyl(r * .56, width + .02, loc=(x, y, z), rot=ACROSS, seg=8, bevel=0)
            if hubs:
                a.part('Hubs', 'Steel').cyl(r * .2, width + .04, loc=(x, y, z), rot=ACROSS, seg=6, bevel=0)


def _lights(a, xs, y, z, facing=-1, size=(.2, .04, .14), lamp='Lamp'):
    """Flush light lenses (a lens in a dark rim) at each x on a face at y looking along `facing`."""
    rim = a.part('Light_rims', 'Undercarriage')
    lens = a.part('Lamps' if lamp == 'Lamp' else 'Tail_lamps', lamp)
    for x in xs:
        rim.box((size[0] + .04, size[1], size[2] + .04), loc=(x, y + facing * .01, z), bevel=0)
        lens.box(size, loc=(x, y + facing * .025, z), bevel=0)


def _ring_gun(a, loc, length=.6, ring=.34):
    """A machine gun on a cab-roof ring mount that turns as the vehicle's `Turret`: the ring, a pintle, the gun
    (`Main_cannon`, drawn 0.12 m thick) with its ammunition can, and `Muzzle_main` at the flash hider."""
    t = a.pivot('Turret', loc)
    a.part('Ring', 'Armor', t).cyl(ring, .08, loc=(0, 0, .04), seg=12, bevel=.02, bseg=1)
    a.part('Mount', 'Steel', t).box((.1, .1, .18), loc=(0, .05, .16), bevel=0)
    gun = a.part('Main_cannon', 'Steel', t)
    gun.box((.14, .4, .15), loc=(0, .05, .3), bevel=.02, seg=1)
    gun.cyl(.06, length, loc=(0, -.15 - length / 2, .31), rot=FORWARD, seg=8, bevel=0)
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.075, .12, loc=(0, -.15 - length - .04, .31), rot=FORWARD, seg=8,
                                                   bevel=0)
    a.part('Ammo_box', 'Armor', t).box((.16, .2, .16), loc=(.16, .08, .26), bevel=.02, seg=1)
    a.pivot('Muzzle_main', (0, -.15 - length - .12, .31), t)
    return t


# ----------------------------------------------------------------------------- HEMTT pair (supply, ammunition)
HEMTT_AXLES = (-3.12, -1.95, 1.2, 2.4)


def _hemtt(a):
    """The M977 HEMTT 8x8 both logistics trucks ride, 8.2 x 2.0 m at 0.8 x (10.2 x 2.44 m real): a flat-fronted
    forward-control cab over the two steered front axles, its big grille below the windscreen, the engine box and
    exhaust stack behind it, a frame to the tail, four axles of big single tyres (two forward, a tandem aft), the
    cab-roof ring gun (`Turret`, `Muzzle_main`). Returns the load bed's floor height."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    dark.box((1.1, 7.9, .3), loc=(0, .05, .72), bevel=0)                                          # frame rails
    _wheels(a, (-.79, .79), HEMTT_AXLES, .48, .36)
    for s in (-1, 1):
        armor.box((.44, 1.95, .08), loc=(s * .79, -2.54, 1.02), bevel=.02, seg=1)                   # front fenders
        armor.box((.44, 2.1, .08), loc=(s * .79, 1.8, 1.02), bevel=.02, seg=1)                      # rear fenders
        steel.box((.14, .5, .14), loc=(s * .88, -.5, .86), bevel=0)                                 # fuel / air tanks
        a.part('Tanks', 'Armor').cyl(.22, 1.0, loc=(s * .74, -.35, .72), rot=FORWARD, seg=8, bevel=0)
        a.part('Glass', 'Glass').box((.03, .7, .42), loc=(s * .985, -3.25, 1.72), bevel=0)          # door windows
        steel.box((.2, .42, .06), loc=(s * .9, -3.6, .78), bevel=0)                                 # cab step
    # Flat-fronted cab above the front wheels, the nose and grille between them, a bumper.
    body.prism([(-4.06, 1.02), (-4.1, 1.45), (-3.98, 2.04), (-2.45, 2.06), (-2.4, 1.02)], 1.98, bevel=.05, seg=1)
    body.box((1.2, .9, .5), loc=(0, -3.62, .8), bevel=.03, seg=1)                                  # nose
    dark.grille(1.0, .34, loc=(0, -4.08, .82), slats=4, depth=.05, thickness=.05)
    dark.grille(1.3, .3, loc=(0, -4.1, 1.26), slats=3, depth=.05, thickness=.05)                   # cab grille
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.84, .04, .48), loc=(s * .45, -4.03, 1.76), rot=(-.2, 0, 0), bevel=0)
    steel.box((2.0, .16, .22), loc=(0, -4.16, .66), bevel=.03, seg=1)                              # bumper
    _lights(a, (-.72, .72), -4.1, .98)
    _lights(a, (-.8, .8), 4.08, 1.0, facing=1, size=(.16, .04, .1), lamp='Alloy')
    armor.box((1.6, .1, .08), loc=(0, -3.99, 2.04), rot=(-.2, 0, 0), bevel=0)                      # visor
    # The engine box behind the cab, the exhaust stack on its left, the air intake on its right.
    armor.box((1.5, .4, .95), loc=(0, -2.2, 1.45), bevel=.04, seg=1)
    steel.cyl(.08, 1.0, loc=(.62, -2.2, 1.9), seg=8, bevel=0)
    armor.box((.3, .3, .5), loc=(-.62, -2.2, 2.05), bevel=.03, seg=1)
    _ring_gun(a, (-.42, -3.3, 2.06))
    a.pivot('Point_exhaust', (.62, -2.2, 2.42))
    a.pivot('Point_fire', (0, -3.2, 2.1))
    return 1.12


def _crate_stack(a, x0, x1, y0, y1, z0, tiers, cols, rows, mat='Crate', lids='Armor', gap=.06):
    """Ammunition crates in a grid, `tiers` high, filling x0..x1 by y0..y1 from z0: from above, a grid of lids."""
    crates = a.part('Crates', mat)
    tops = a.part('Crate_lids', lids)
    w = (x1 - x0 - gap * (cols - 1)) / cols
    d = (y1 - y0 - gap * (rows - 1)) / rows
    h = .3
    for k in range(tiers):
        for i in range(cols):
            for j in range(rows):
                if k == tiers - 1 and (i + j) % 4 == 3:
                    continue     # a gap in the top tier: the stack reads as crates, not a block
                x = x0 + w / 2 + i * (w + gap)
                y = y0 + d / 2 + j * (d + gap)
                crates.box((w, d, h - .02), loc=(x, y, z0 + h / 2 + k * h), bevel=0)
                if k == tiers - 1:
                    tops.box((w * .7, d * .7, .03), loc=(x, y, z0 + (k + 1) * h - .005), bevel=0)


def supply_truck(a):
    """Supply truck (M977 HEMTT cargo truck), 8.2 x 2.0 x 2.1 m: the HEMTT (_hemtt) with a drop-side cargo bed two
    thirds of its length under a tarpaulin on its bows, and the open tail of the bed showing its load (ammunition
    boxes and crates, the sheet: they must show from above), the tailgate down; the cab-roof machine gun."""
    z = _hemtt(a)
    armor = a.part('Armor', 'Armor')
    a.part('Bed', 'Team').box((1.98, 6.1, .14), loc=(0, 1.0, z + .07), bevel=.02, seg=1)
    for s in (-1, 1):
        armor.box((.06, 6.1, .42), loc=(s * .97, 1.0, z + .35), bevel=.01, seg=1)                  # drop sides
    armor.box((1.98, .06, .42), loc=(0, -2.03, z + .35), bevel=.01, seg=1)                        # headboard
    # The tarpaulin over the front two thirds: a rounded canvas cover on bows, straps down its sides.
    tarp = a.part('Tarp', 'Canvas')
    prof = [(-.99, z + .5), (-.99, 1.86), (-.8, 2.02), (-.3, 2.08), (.3, 2.08), (.8, 2.02), (.99, 1.86), (.99, z + .5)]
    tarp.prism(prof, 4.0, loc=(0, -.02, 0), axis='Y', bevel=.03, seg=1)
    straps = a.part('Straps', 'Undercarriage')
    for y in (-1.3, -.3, .7, 1.7):
        straps.box((2.02, .1, .06), loc=(0, y, 2.07), bevel=0)
    # The open tail: ammunition boxes and crates, the tailgate lowered.
    _crate_stack(a, -.86, .86, 2.1, 3.85, z + .14, 2, 3, 3)
    a.part('Ammo_boxes', 'Armor').box((.5, .34, .28), loc=(-.55, 2.35, z + .9), bevel=.02, seg=1)
    a.part('Fuel_cans', 'Hazard').box((.3, .5, .36), loc=(.62, 3.6, z + .79), bevel=.03, seg=1)
    armor.box((1.9, .06, .42), loc=(0, 4.1, z - .2), bevel=.01, seg=1)                            # tailgate, down


def ammo_carrier(a):
    """Ammunition carrier (HEMTT with a load-handling bed, M1120 LHS / M985 class), 8.2 x 2.0 x 2.1 m: the HEMTT
    (_hemtt) with an open steel ammunition rack of square posts and rails over the bed, olive crates stacked in
    three tiers inside it (from above, a grid of crates), and the small knuckle crane folded at the tail: its
    pedestal, slewing column and boom lying forward over the load, the hook block."""
    z = _hemtt(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Bed', 'Team').box((1.98, 5.4, .14), loc=(0, .65, z + .07), bevel=.02, seg=1)
    rack = a.part('Rack', 'Armor')
    for s in (-1, 1):
        for y in (-1.95, -.6, .75, 2.1, 3.3):
            rack.box((.1, .1, .82), loc=(s * .93, y, z + .55), bevel=0)                            # posts
        for zz in (.5, .95):
            rack.box((.1, 5.35, .1), loc=(s * .93, .67, z + zz), bevel=0)                          # rails
    rack.box((1.96, .1, .1), loc=(0, -1.95, z + .95), bevel=0)
    _crate_stack(a, -.84, .84, -1.85, 3.2, z + .14, 3, 3, 5)
    # The small knuckle crane at the tail, folded forward over the load.
    armor.box((1.7, .6, .4), loc=(0, 3.72, z + .2), bevel=.04, seg=1)                             # pedestal
    a.part('Crane', 'Hazard').cyl(.24, .7, loc=(.45, 3.72, z + .75), seg=10, bevel=.03, bseg=1)   # column
    boom = a.part('Crane_boom', 'Hazard')
    boom.box((.22, 2.8, .24), loc=(.45, 2.3, z + 1.16), rot=(-.06, 0, 0), bevel=.03, seg=1)
    boom.box((.2, .5, .3), loc=(.45, 3.62, z + 1.2), bevel=.03, seg=1)                            # knuckle
    steel.box((.16, .16, .2), loc=(.45, .95, z + 1.02), bevel=0)                                  # hook block
    for s in (-1, 1):                                                                             # outriggers
        steel.box((.14, .2, .5), loc=(s * .92, 3.72, z - .1), bevel=0)


# name: (builder, Asset options).
BUILDERS = {
    'supply_truck': (supply_truck, dict(ao_distance=.5, grime_height=.5)),
    'ammo_carrier': (ammo_carrier, dict(ao_distance=.5, grime_height=.5)),
}
