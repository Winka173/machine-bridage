"""Prompt 25 F2 batch C (DECISIONS 25F2-C): one low-poly round per new ordnance weapon, built the same way as
mb_munitions.py (its Round/rev/fins/motor helpers and house colours, reused here rather than copied).

Lengths are drawn at a size close to the game's roundLength (balance.json: 0.8 x real for a ground-launched
round, 0.5 x real for an air-launched one, 0.8 m at least); the in-game view rescales whichever model flies a
weapon to its own roundLength, so the build length only has to look right next to the existing munitions.

Headless, from the repository root:
  blender --background --python Tools/blender/mb_p25_rounds.py
  blender --background --python Tools/blender/mb_p25_rounds.py -- cbu_97 harm
"""
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import mb_munitions as mu  # noqa: E402

Round = mu.Round
OLIVE, GREY_GREEN, WHITE = mu.OLIVE, mu.GREY_GREEN, mu.WHITE
LIGHT_GREY, MID_GREY, DARK_GREY = mu.LIGHT_GREY, mu.MID_GREY, mu.DARK_GREY
YELLOW, BROWN, RED, COPPER, BLACK, STEEL, GLASS = mu.YELLOW, mu.BROWN, mu.RED, mu.COPPER, mu.BLACK, mu.STEEL, mu.GLASS
X4 = mu.X4
inner = mu.inner


def cbu_97(a):
    """tl02: CBU-97 Sensor Fuzed Weapon canister (2.33 m; drawn 1.4 m): a grey-green dispenser body with a
    blunt nose, the red cluster band and a finned tail, no motor (it free-falls)."""
    m, r, s = Round(a, 1.4), .19, 8
    m.rev('Body', GREY_GREEN, [(0, 0), (.05, .03), (.12, .12), (r, .30)], s, caps=(False, False))
    m.rev('Band', RED, [(r, .30), (r, .35)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .35), (r, 1.18), (.1, 1.32), (.07, 1.4)], s, caps=(False, True))
    m.fins('Fins', GREY_GREEN, 4, X4, .075, 1.24, .18, .10, .13, .04)


def gbu_28(a):
    """tl03: GBU-28 bunker buster (5.84 m; drawn 2.9 m): a slim olive penetrator body, a steel nose, a yellow
    band and a small tail kit with four control fins; no motor."""
    m, r, s = Round(a, 2.9), .12, 8
    m.rev('Tip', STEEL, [(0, 0), (.02, .02), (.045, .12)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(.045, .12), (.09, .3), (r, .55)], s, caps=(True, False))
    m.rev('Band', YELLOW, [(r, .55), (r, .62)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .62), (r, 2.6), (.09, 2.82), (.07, 2.9)], s, caps=(False, True))
    m.fins('Fins', LIGHT_GREY, 4, X4, .1, 2.68, .3, .16, .22, .1)


def odab_500(a):
    """tl04: ODAB-500 thermobaric bomb (2.45 m; drawn 1.8 m): a red-orange body (the thermobaric mark) with a
    steel fuze, a black warning band and a boxed tail of four fins; no motor."""
    m, r, s = Round(a, 1.8), .15, 8
    m.rev('Fuze', STEEL, [(0, 0), (.02, .005), (.024, .04)], 6, caps=(False, False))
    m.rev('Body', RED, [(.05, .04), (.12, .15), (r, .34), (r, 1.25), (.12, 1.45), (.07, 1.62)], s, caps=(True, True))
    m.rev('Band', BLACK, [(r, .58), (r, .64)], s, caps=(False, False))
    m.fins('Fins', RED, 4, X4, .075, 1.5, .2, .1, .13, .06)


def harm(a):
    """tl05: AGM-88 HARM anti-radar missile (4.17 m; drawn 2.1 m): a white seeker nose, an olive body, a
    yellow band, four mid fins and a motor glow at the tail."""
    m, r, s = Round(a, 2.1), .056, 8
    m.rev('Seeker', GLASS, [(0, 0), (.018, .02), (.03, .07)], s, caps=(False, False))
    m.rev('Body', WHITE, [(.03, .07), (.042, .18), (r, .4)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .4), (r, .46)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .46), (r, 2.0), (.04, 2.1)], s, caps=(False, False))
    m.motor(.04, 2.1, .028, s)
    m.fins('Fins', OLIVE, 4, X4, r * .95, .95, .22, .12, .16, .05)


def apkws(a):
    """tl06: APKWS (a laser-guided Hydra 70): as hydra() with a laser seeker dome bolted on the nose instead of
    the plain point, 1.06 m, drawn 1.0 m."""
    m, r, s = Round(a, 1.0), .04, 6
    m.rev('Seeker', GLASS, [(0, 0), (.018, .015), (.026, .045)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(.026, .045), (.032, .16), (r, .25)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .25), (r, .29)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .29), (r, .97), (.036, 1.0)], s, caps=(False, False))
    m.motor(.036, 1.0, .024, s)
    m.wrap('Fins', OLIVE, 4, X4, inner(r, s), .88, .10, .065, curl=1.2)


def coyote_block2(a):
    """tl07: Coyote Block 2 drone interceptor (0.91 m; drawn 0.9 m): a small grey-green dart with a proximity
    fuze, a black band and four flip-out tail fins; no motor glow (it is a short-lived sprint)."""
    m, r, s = Round(a, .9), .03, 6
    m.rev('Fuze', BLACK, [(0, 0), (.012, .01), (.018, .05)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.018, .05), (.026, .16), (r, .3)], s, caps=(False, False))
    m.rev('Band', BLACK, [(r, .3), (r, .34)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .34), (r, .86), (.02, .9)], s, caps=(False, True))
    m.fins('Fins', GREY_GREEN, 4, X4, inner(r, s), .8, .1, .04, .07, .03)


def smart_155(a):
    """tl09: SMArt 155 top-attack artillery shell (0.94 m; drawn 1.1 m, the game's 155 mm scale): as shell_155
    but with a small parachute housing at the tail instead of a boat tail."""
    m, r, s = Round(a, 1.1), .099, 8
    m.rev('Fuze', STEEL, [(0, 0), (.016, .03), (.026, .11)], 6, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.028, .11), (.07, .25), (r, .48)], s, caps=(True, False))
    m.rev('Band', RED, [(r, .48), (r, .53)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .53), (r, .88)], s, caps=(False, False))
    m.rev('Rotating_band', COPPER, [(r, .88), (r, .93)], s, caps=(False, False))
    m.rev('Chute_housing', DARK_GREY, [(r, .93), (r * .7, 1.04), (r * .7, 1.1)], s, caps=(False, True))


def switchblade_300(a):
    """tl13: Switchblade 300 loitering munition (0.61 m; drawn 0.9 m, thickened for a tube-launched round): a
    grey tube with a camera nose, two folding cruciform wings and a small pusher propeller."""
    m, r, s = Round(a, .9), .035, 8
    m.rev('Camera', GLASS, [(0, 0), (.018, .004), (.028, .015)], s, caps=(False, False))
    m.rev('Body', LIGHT_GREY, [(.028, .015), (r, .04), (r, .78), (.028, .86), (.016, .88)], s, caps=(False, True))
    m.rev('Spinner', BLACK, [(.014, .88), (.011, .895), (0, .9)], 6, caps=(True, False))
    m.fins('Wings', MID_GREY, 4, X4, r * .95, .2, .08, .4, .06, .015)
    m.box('Propeller_blades', BLACK, (.22, .01, .025), m.at(0, .885), rot=(0, 0, 0))


def nsm_oniks(a):
    """tl14: NSM/P-800 Oniks anti-ship missile (3.96 m; drawn 3.2 m): a grey-green sea-skimming body with a
    faceted nose, mid-body cropped-delta wings, a tail fin cross and a motor glow."""
    m, r, s = Round(a, 3.2), .12, 8
    m.rev('Nose', DARK_GREY, [(0, 0), (.03, .1), (.07, .3)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.07, .3), (r, .6), (r, 2.7), (.08, 2.95), (.06, 3.2)], s, caps=(False, True))
    m.motor(.06, 3.2, .04, s)
    m.fins('Wings', GREY_GREEN, 4, X4, r * .95, 1.5, .5, .3, .4, .08)
    m.fins('Fins', GREY_GREEN, 4, X4, r * .95, 2.75, .2, .14, .16, .05)


# name: (builder, Asset options). They all fly: no ground occlusion or grime.
BUILDERS = {name: (fn, dict(ao_distance=ao, ground=False)) for name, fn, ao in (
    ('cbu_97', cbu_97, .2), ('gbu_28', gbu_28, .25), ('odab_500', odab_500, .2), ('harm', harm, .15),
    ('apkws', apkws, .08), ('coyote_block2', coyote_block2, .08), ('smart_155', smart_155, .1),
    ('switchblade_300', switchblade_300, .08), ('nsm_oniks', nsm_oniks, .25),
)}

OUT = HERE.parents[1] / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'


def build(filters=(), out=OUT):
    """Build and export the rounds whose names contain one of the filters (all without filters)."""
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o)
    root = mu.kit.workspace()
    mu.kit.clear_workspace(root)
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, (fn, options) in BUILDERS.items():
        if filters and not any(f in name for f in filters):
            continue
        asset = mu.kit.Asset(name, root, **options)
        fn(asset)
        asset.finish()
        asset.export(out / f'{name}.glb')
        counts[name] = asset.triangles()
        print(f'BUILT {name}: {counts[name]} triangles')
        mu.kit.clear_workspace(root)
    return counts


if __name__ == '__main__':
    build(tuple(sys.argv[sys.argv.index('--') + 1:]) if '--' in sys.argv else ())
    print('MB_P25_ROUNDS_COMPLETE')
