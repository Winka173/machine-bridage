"""Prompt 27 wave 2 pass A (DECISIONS "27 wave 2 pass A (lead pass, 2026-10-02)"): the validator's flagged models,
fixed with the smallest change, merged last in build_assets.all_builders().

  headquarters, helipad, helipad_a, helipad_b   the original builder, then `k.clean` (zero-area triangles)
  mobile_fortress                               the original builder plus the two part nodes the def's parts need:
                                                `Mount_gun` (a roof howitzer on the turret, with `Muzzle_gun`) and
                                                `Mount_missile.001` (a compact SAM battery on the rear deck, with
                                                `Muzzle_missile.001`) + an empty `Mount_missile` at the silo, so the
                                                k-th mount still pairs with the k-th `Muzzle_missile*`

The proportion fixes (heavy_flak_tower, at_gun_emplacement, laser_ad_station, visual_jammer) are minimal edits in
mb_p25_new.py. Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front.
"""
import math

from mathutils import Vector

import mb_bosses2
import mb_kit27 as k
import mb_p25_models2
import mb_phase2
import mb_siege
from mb_phase2 import _suffixed
from mb_bosses2 import FORWARD, _frame, _tube_mouth, pivot


def _cleaned(build):
    def wrapped(a):
        build(a)
        k.clean(a)
    return wrapped


def _roof_howitzer(a):
    """A second, compact howitzer on the main turret's roof (`Mount_gun` + `Muzzle_gun`, parent `Turret`)."""
    m = pivot(a, 'Mount_gun', (0, 1.0, 1.19), 'Turret')
    a.part('Gun2_base', 'Steel', m).cyl(.5, .14, loc=(0, 0, .07), seg=16, bevel=.02, bseg=1)
    a.part('Gun2_house', 'Armor', m).box((.8, .9, .34), loc=(0, 0, .31), bevel=.05, seg=1, taper=(.9, .9))
    a.part('Gun2_sleeve', 'Team', m).cyl(.15, .8, loc=(0, -.9, .42), rot=FORWARD, seg=12, bevel=.02)
    a.part('Gun2_barrel', 'Steel', m).cyl(.085, 2.2, loc=(0, -1.9, .42), rot=FORWARD, seg=10, bevel=0)
    a.part('Gun2_brake', 'Undercarriage', m).cyl(.14, .3, loc=(0, -3.1, .42), rot=FORWARD, seg=10, bevel=.02)
    pivot(a, 'Muzzle_gun', (0, -3.28, .42), 'Mount_gun')


def _deck_sam(a, name, x, y, z):
    """A compact SAM battery on its own mount `name` (smaller than mb_bosses2._sam_battery, to fit between the
    superstructure and the rear rocket battery): base, yoke, a 2 x 2 canister box raised 30 degrees, a radar plate;
    `Muzzle_missile*` at the canister face."""
    m = pivot(a, name, (x, y, z))
    a.part('Sam_base', 'Steel', m).cyl(.5, .1, loc=(0, 0, .05), seg=14, bevel=.02, bseg=1)
    arm = a.part('Sam_armor', 'Armor', m)
    arm.box((.6, .6, .34), loc=(0, .1, .27), bevel=.04, seg=1)
    for s in (-1, 1):
        arm.box((.1, .45, .5), loc=(s * .45, .1, .6), bevel=.02, seg=1)
    pitch = math.radians(30)
    lrot = (-pitch, 0, 0)
    c = Vector((0, .05, .82))
    box = _frame(c, lrot)
    a.part('Sam_box', 'Team', m).box((.8, 1.2, .7), loc=c, rot=lrot, bevel=.04, seg=1)
    for cx in (-.19, .19):
        for cz in (-.16, .16):
            _tube_mouth(a, m, box @ _frame((cx, -.61, cz), FORWARD), .14, protrude=.04, seg=8, name='Launcher_tubes')
    a.part('Sam_radar', 'Armor', m).box((.5, .07, .36), loc=(0, .55, 1.0), rot=(.3, 0, 0), bevel=.02, seg=1)
    pivot(a, name.replace('Mount_', 'Muzzle_'), tuple(box @ Vector((0, -.66, 0))), name)


def mobile_fortress(a):
    _suffixed(a)                      # Mount_mg__001 -> Mount_mg.001 when the plain finish() runs
    mb_bosses2.mobile_fortress(a)
    _roof_howitzer(a)
    _deck_sam(a, 'Mount_missile.001', -2.9, 5.0, 4.3)
    pivot(a, 'Mount_missile', (0, 6.05, 4.62))
    k.clean(a)


def _opts(module, name):
    """The original options with a softer ambient occlusion (the fixes lost a little COLOR_0 to the cleaned slivers)."""
    return dict(module.BUILDERS[name][1], ao_strength=.7)


BUILDERS = {
    'headquarters': (_cleaned(mb_phase2.headquarters), _opts(mb_phase2, 'headquarters')),
    'helipad': (_cleaned(mb_siege.helipad), _opts(mb_siege, 'helipad')),
    'helipad_a': (_cleaned(mb_p25_models2.helipad_a), _opts(mb_p25_models2, 'helipad_a')),
    'helipad_b': (_cleaned(mb_p25_models2.helipad_b), _opts(mb_p25_models2, 'helipad_b')),
    'mobile_fortress': (mobile_fortress, _opts(mb_bosses2, 'mobile_fortress')),
}
