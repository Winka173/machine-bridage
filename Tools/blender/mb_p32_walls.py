"""Prompt 32 L3: the base wall segments on the V2 kit (DECISIONS "Prompt 32 L3 / L7 / L9").

One logic segment is 12 x 2 m (balance.json wall_hesco / wall_t / wall_gun: length 2, width 12), built here as its
visual pieces: three 4 m HESCO bays, five 2.4 m concrete T-wall panels, or two HESCO bays either side of a raised
firing platform (the gun wall, where one of the base's small towers stands). The wall runs along X (the segment's
width), its front faces -Y (out of the base), both ends flush at x = +-6 m so segments line up. A fallen segment is
drawn by the view as a slumped, burnt ruin (VehicleView.BecomeWreck for a fixed defence): no rubble model.

    blender --background --python Tools/blender/build_assets.py -- wall_hesco wall_t_ wall_gun
"""
import random

import mb_kit27 as k
from mb_p27_wave8b import _v2
from mb_siege import coil

L = 12.0


def _hesco_bay(a, x0, x1, h, rng, tag=''):
    """One run of gabion cells from x0 to x1, h tall, 1.6 m deep: wire-mesh posts and rims round an earth fill."""
    mesh = a.part('Mesh' + tag, 'Steel')
    fill = a.part('Fill' + tag, 'Dirt')
    liner = a.part('Liner' + tag, 'Canvas')
    cells = max(1, round((x1 - x0) / 1.0))
    w = (x1 - x0) / cells
    for i in range(cells):
        cx = x0 + w * (i + .5)
        sag = rng.uniform(-.04, .03)
        fill.box((w - .06, 1.5, h - .12 + sag), loc=(cx, 0, (h - .12 + sag) / 2), bevel=.05, seg=1)
        liner.box((w - .02, 1.56, .5), loc=(cx, 0, h - .32), bevel=0)
    for i in range(cells + 1):
        x = x0 + w * i
        for y in (-.8, .8):
            mesh.box((.05, .05, h), loc=(x, y, h / 2), bevel=0)
    for z in (.02, h * .5, h - .02):
        for y in (-.8, .8):
            mesh.box((x1 - x0, .04, .04), loc=((x0 + x1) / 2, y, z), bevel=0)
    for i in range(cells + 1):
        mesh.box((.04, 1.6, .04), loc=(x0 + w * i, 0, h - .02), bevel=0)


def wall_hesco(a, detail=False):
    """HESCO segment (12 x 2 m, 2.2 m): three bays of earth-filled gabions on a dirt berm, a Team band on the liner
    caps, a concertina coil along the top."""
    rng = random.Random(32)
    h = 2.2
    a.part('Berm', 'Dirt').prism([(-1.0, -.02), (1.0, -.02), (.82, .16), (-.82, .16)], L, axis='X', bevel=0)
    for b in range(3):
        _hesco_bay(a, -L / 2 + b * 4 + .03, -L / 2 + (b + 1) * 4 - .03, h, rng, tag='' if b == 0 else f'_{b}')
    band = a.part('Wall_band', 'Team')
    for y in (-.81, .81):
        band.box((L - .1, .02, .22), loc=(0, y, h - .55), bevel=0)
    wire = a.part('Razor_wire', 'Steel')
    coil(wire, -L / 2, L / 2, 0, h + .26, .25, pitch=.42, pts=8, wire=.018)
    for x in (-4.0, 0.0, 4.0):
        a.part('Stencil', 'Hazard').box((.5, .02, .3), loc=(x - 1.2, -.82, 1.1), bevel=0)


def wall_t(a, detail=False):
    """T-wall segment (12 x 2 m, 3.6 m): five precast concrete T-wall panels on their wide feet, lifting eyes,
    a Team stripe across the faces, a hazard-banded end on each panel and a wire strand on top."""
    n, gap = 5, .03
    lp = (L - gap * (n - 1)) / n
    h = 3.6
    for i in range(n):
        x = -L / 2 + lp / 2 + i * (lp + gap)
        a.part('Panels', 'Concrete').prism([(-.16, .55), (.16, .55), (.12, h), (-.12, h)], lp, loc=(x, 0, 0), axis='X', bevel=.03, seg=1)
        a.part('Feet', 'Concrete').prism([(-.95, 0), (.95, 0), (.95, .25), (.2, .58), (-.2, .58), (-.95, .25)], lp, loc=(x, 0, 0), axis='X',
                                        bevel=.03, seg=1)
        a.part('Wall_band', 'Team').box((lp - .06, .34, .3), loc=(x, 0, h - .9), bevel=0)
        for s in (-1, 1):
            a.part('Eyes', 'Steel').cyl(.05, .1, loc=(x + s * .5, 0, h + .04), rot=(1.5708, 0, 0), seg=8)
        a.part('Hazard', 'Hazard').box((.08, .36, .9), loc=(x + lp / 2 - .06, 0, 1.4), bevel=0)
    a.part('Wire', 'Steel').tube([(-L / 2, 0, h + .3), (L / 2, 0, h + .3)], .012, seg=3, caps=False)
    for i in range(n + 1):
        x = -L / 2 + i * (L / n)
        a.part('Wire_posts', 'Steel').box((.04, .04, .34), loc=(min(max(x, -L / 2 + .05), L / 2 - .05), 0, h + .15), bevel=0)


def wall_gun(a, detail=False):
    """Gun wall segment (12 x 2 m): HESCO bays either side of a 4 m concrete firing platform (1.2 m deck, sandbagged
    parapet, steel ladder at the back) on which one of the base's small towers stands."""
    rng = random.Random(33)
    h = 2.2
    a.part('Berm', 'Dirt').prism([(-1.0, -.02), (1.0, -.02), (.82, .16), (-.82, .16)], L, axis='X', bevel=0)
    _hesco_bay(a, -L / 2 + .03, -2.03, h, rng)
    _hesco_bay(a, 2.03, L / 2 - .03, h, rng, tag='_1')
    deck = 1.2
    a.part('Platform', 'Concrete').box((4.0, 2.0, deck), loc=(0, 0, deck / 2), bevel=.04, seg=1)
    a.part('Deck', 'Armor').box((3.9, 1.9, .08), loc=(0, 0, deck + .04), bevel=0)
    bags = a.part('Parapet', 'Sandbag')
    for i in range(5):
        bags.box((.74, .4, .26), loc=(-1.55 + i * .78, -.85, deck + .21), bevel=.06, seg=1)
        if i % 2 == 0:
            bags.box((.74, .4, .26), loc=(-1.55 + i * .78, -.85, deck + .47), bevel=.06, seg=1)
    a.part('Wall_band', 'Team').box((4.02, .02, .25), loc=(0, -1.01, deck - .35), bevel=0)
    ladder = a.part('Ladder', 'Steel')
    for x in (-.25, .25):
        ladder.box((.05, .05, deck + .3), loc=(x, 1.08, (deck + .3) / 2), bevel=0)
    for i in range(4):
        ladder.box((.5, .04, .04), loc=(0, 1.08, .25 + i * .3), bevel=0)
    wire = a.part('Razor_wire', 'Steel')
    for x0, x1 in ((-L / 2, -2.0), (2.0, L / 2)):
        coil(wire, x0, x1, 0, h + .26, .25, pitch=.42, pts=8, wire=.018)


def _gen(fn, ao=.7, **kw):
    def run(a):
        with _v2(**kw):
            fn(a)
        k.clean(a)
    return run, dict(ao_distance=.7, grime_height=.5, ao_strength=ao)


BUILDERS = {
    'wall_hesco': _gen(wall_hesco, .75),
    'wall_t': _gen(wall_t, .7, box_min=.3, seg_add=2),
    'wall_gun': _gen(wall_gun, .75),
}
