"""Machine Brigade prompt 22 E (DECISIONS 22E): Morrigan, Wolff's own stealth fighter (a mini boss on the aircraft frame).

Conventions as everywhere: metres, +Z up, Blender -Y is the front (Unity +Z), +X the pilot's left. Team / TeamGlow parts
are recoloured per army at runtime. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).

  * morrigan: 20.6 x 13.4 m, origin at the fuselage centre (it flies; balance.json scales it by 0.62). References: the
    Northrop YF-23 Black Widow II (the diamond wing with its leading edge swept back and trailing edge swept forward at
    40 degrees, the two all-moving tails canted out at 50 degrees, the engines' exhaust troughs over the rear deck, the
    long flat-sided nose) with the Su-57's internal bay layout (two main bays in tandem under the belly between the
    intakes) and a raven's look: a blade-thin nose, a dark body with the army's colour on the wings and tails only, and a
    serrated trailing edge like primary feathers. Boss parts (their `node`s in balance.json): `Part_bay_l` / `Part_bay_r`,
    the two main weapons bays (doors open, an air-to-air missile each on its trapeze, `Muzzle_missile` and
    `Muzzle_missile.001` at the missiles' noses), `Part_bomb_bay` behind them (the guided bomb, `Muzzle_bomb`) and
    `Part_engines` (the two exhaust troughs and nozzles over the rear deck). The cannon is on the left shoulder
    (`Muzzle_gun`).

Headless: blender --background --python Tools/blender/build_assets.py -- morrigan
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from mb_air import FORWARD, _aam, _dome, _upright  # noqa: E402
from mb_p17_temp import _bay_bomb, _hex, _hex_top, _slab  # noqa: E402
from mb_phase2 import _suffixed  # noqa: E402
from mb_phase8 import pv  # noqa: E402

# The chined body: (y, belly half-width, belly z, chine half-width, chine z, spine half-width, spine z), nose to tail.
MG = [(-10.3, .08, -.14, .24, -.04, .06, .1),
      (-8.6, .3, -.34, .7, -.08, .22, .32),
      (-6.4, .55, -.46, 1.15, -.1, .34, .54),
      (-4.0, .92, -.52, 1.9, -.12, .5, .62),
      (-1.0, 1.25, -.52, 2.55, -.12, .74, .58),
      (3.0, 1.35, -.48, 2.7, -.1, .9, .52),
      (6.6, 1.12, -.4, 2.2, -.08, .82, .44),
      (9.4, .8, -.3, 1.45, -.06, .52, .3)]
BAY_Y = -1.3        # the main bays' middle (each 3.6 m long)
BOMB_Y = 2.5        # the centre bay's middle
TAN40 = math.tan(math.radians(40.0))


def _missile_parts(a, parent, tag):
    return dict(body=a.part(f'Aam_{tag}', 'Fuel', parent), fins=a.part(f'Aam_fins_{tag}', 'Armor', parent),
                nose=a.part(f'Aam_seeker_{tag}', 'Glass', parent), band=a.part(f'Aam_band_{tag}', 'Hazard', parent))


def morrigan(a):
    """Morrigan (see the module note): a chined dark body, the diamond wing and canted tails in the army's colour, a long
    blade nose and frameless canopy, caret intakes under the chines, the two main bays open under the belly with a
    missile each, the centre bay with its guided bomb, the exhaust troughs over the rear deck."""
    _suffixed(a)
    body = a.part('Fuselage', 'Armor', flat=True)
    skin = a.part('Wings', 'Team', flat=True)
    dark = a.part('Undercarriage', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Wing_lights', 'TeamGlow')
    body.loft([[(0, -11.2, -.05)]] + [_hex(*r) for r in MG], bevel=0)
    # The diamond wing: leading edge 40 degrees back, trailing edge 40 degrees forward; a feathered trailing edge.
    root_le, root_te, s0, s1 = -4.6, 7.4, 2.0, 6.7
    tip_le = root_le + (s1 - s0) * TAN40
    tip_te = root_te - (s1 - s0) * TAN40
    for sg in (-1, 1):
        _slab(skin, lambda s, y, n, sg=sg: (sg * s, y, -.12 - (s - s0) * .015 + n),
              [(s0, root_le, root_te - root_le, .3), (s1, tip_le, max(1.2, tip_te - tip_le), .06)])
        for k in range(3):                                      # three primary "feathers" at the trailing edge
            s = s0 + 1.1 + k * 1.15
            te = root_te - (s - s0) * TAN40
            skin.box((.55, .9, .05), loc=(sg * s, te + .3, -.14 - (s - s0) * .015), rot=(0, 0, sg * .7), bevel=0,
                     taper=(.3, 1))
        # The all-moving tails canted out 50 degrees (the YF-23's), their roots on the rear deck.
        fin = _upright(sg * 1.25, .3, math.radians(50.0))
        _slab(skin, fin, [(0, 5.7, 3.6, .14), (3.3, 8.3, 1.3, .05)])
        glow.box((.05, .3, .04), loc=(sg * (s1 + .02), tip_le + .7, -.2), bevel=0)
        glow.box((.04, .2, .04), loc=tuple(fin(3.32, 8.8, 0)), bevel=0)
    # The frameless canopy far forward, and the blade nose's sensor window.
    st = [(-8.1, .1, .36), (-7.4, .34, .66), (-6.4, .42, .84), (-5.4, .38, .8), (-4.6, .22, .66), (-4.1, .1, .6)]
    a.part('Canopy', 'Glass').loft([_dome(y, w, _hex_top(MG, y, w) - .06, z1, n=7) for y, w, z1 in st], bevel=0)
    a.part('Sensor', 'Glass', flat=True).box((.18, .34, .08), loc=(0, -9.2, -.26), bevel=0, taper=(.7, .7))
    # Caret intakes under the chines (dark faces 1.5 cm inside their mouths).
    for sg in (-1, 1):
        def rect(y, x0, x1, z0, z1, sg=sg):
            return [(sg * x0, y, z0), (sg * x1, y, z0), (sg * x1, y, z1), (sg * x0, y, z1)]
        body.loft([rect(-4.9, .95, 1.8, -.66, -.16), rect(-2.2, .95, 1.75, -.64, -.14), rect(.4, 1.0, 1.7, -.52, -.16)],
                  bevel=0)
        dark.box((.83, .02, .48), loc=(sg * 1.375, -4.925, -.41), bevel=0)

    # The main bays, each a part: a dark liner, its doors hanging open, a missile on an extended trapeze.
    for sg, name, tag, muzzle in ((1, 'Part_bay_l', 'l', 'Muzzle_missile'), (-1, 'Part_bay_r', 'r', 'Muzzle_missile.001')):
        x = sg * .45
        p = pv(a, name, (x, BAY_Y, -.6))
        a.part(f'Bay_liner_{tag}', 'Undercarriage', p).box((.62, 3.6, .02), loc=(0, 0, .03), bevel=0)
        doors = a.part(f'Bay_door_{tag}', 'Armor', p, flat=True)
        doors.box((.03, 3.4, .52), loc=(sg * .35, 0, -.22), bevel=0)
        rails = a.part(f'Bay_trapeze_{tag}', 'Steel', p)
        for dy in (-.6, .6):
            rails.limb((0, dy, .06), (0, dy, -.3), .05, .05, bevel=0)
        _aam(_missile_parts(a, p, tag), (0, 0, -.38), length=3.0, r=.085, canards=False, fin=1.7)
        pv(a, muzzle, (0, -1.51, -.38), name)
    body.box((.1, 3.6, .1), loc=(0, BAY_Y, -.58), bevel=0)             # the keel between the bays
    # The centre bay: a guided bomb on its rack between two open doors.
    pb = pv(a, 'Part_bomb_bay', (0, BOMB_Y, -.56))
    a.part('Bomb_liner', 'Undercarriage', pb).box((.74, 2.4, .02), loc=(0, 0, .01), bevel=0)
    bdoors = a.part('Bomb_doors', 'Armor', pb, flat=True)
    for sg in (-1, 1):
        bdoors.box((.03, 2.2, .45), loc=(sg * .4, 0, -.2), bevel=0)
    a.part('Bomb_rack', 'Steel', pb).limb((0, 0, .04), (0, 0, -.14), .06, .06, bevel=0)
    _bay_bomb(a.part('Bay_stores', 'Armor', pb), (0, 0, -.25))
    pv(a, 'Muzzle_bomb', (0, -.91, -.25), 'Part_bomb_bay')

    # The engines: two exhaust troughs over the rear deck (the YF-23's), their dark liners and hot throats.
    pe = pv(a, 'Part_engines', (0, 7.9, .3))
    trough = a.part('Troughs', 'Steel', pe, flat=True)
    liner = a.part('Trough_liners', 'Undercarriage', pe)
    hot = a.part('Exhaust_glow', 'Alloy', pe)
    for sg in (-1, 1):
        x = sg * .78
        trough.box((.9, 2.6, .14), loc=(x, 0, .1), bevel=0, taper=(1.15, 1))
        for side in (-1, 1):
            trough.box((.05, 2.6, .24), loc=(x + side * .46, 0, .19), bevel=0)
        liner.box((.8, 2.5, .02), loc=(x, 0, .18), bevel=0)
        hot.box((.62, .05, .1), loc=(x, -1.1, .24), bevel=0)
        # The engine humps the troughs sit on.
        body.loft([[(x - .55, 5.2, _hex_top(MG, 5.2, x) - .08), (x + .55, 5.2, _hex_top(MG, 5.2, x) - .08),
                    (x + .5, 5.2, .52), (x - .5, 5.2, .52)],
                   [(x - .5, 6.6, .28), (x + .5, 6.6, .28), (x + .45, 6.6, .5), (x - .45, 6.6, .5)]], bevel=0)

    # The cannon on the left shoulder (+X): fairing, barrel and muzzle ring.
    gx, gy = 1.4, -4.6
    gz = _hex_top(MG, gy, gx) + .1
    body.box((.24, 1.2, .2), loc=(gx, -4.0, _hex_top(MG, -4.0, gx)), bevel=0, taper=(.6, .9))
    steel.cyl(.04, .55, loc=(gx, gy - .1, gz), rot=FORWARD, seg=8, bevel=0)
    steel.cyl(.055, .08, loc=(gx, gy - .36, gz), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (gx, gy - .41, gz))
    a.part('Beacon', 'TeamGlow').sphere(.045, loc=(0, 9.46, .12), seg=8, rings=5)


BUILDERS = {
    'morrigan': (morrigan, dict(ao_distance=.7, ground=False)),
}
