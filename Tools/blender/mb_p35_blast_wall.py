"""Prompt 35 wave 3 (lane B): the gabion blast wall rebuilt from scratch (spec: Tools/blender/specs/blast_wall.json).

A stepped line of stone-filled wire gabions (the def's modelSize 1.9 x 4.8 x 2.4 m; the box is kept exactly, 4.75 x
1.9 x 2.41, centred on the origin, along X, front to -Y): a bottom course of four 1.19 m baskets the full 1.9 m deep,
a middle course 1.3 m deep set back from the front (the step), three courses of sandbags on top; every basket a
welded mesh frame with its lacing wire and the stones pressing against the mesh, a few loose stones and a split bag
at the foot; the Team bands painted on the middle course's mesh; a tamped earth pad under it with two slopes a side.
Field-built (Accord): stone, wire, sandbags.

Own geometry: not the HESCO wall's fabric cells nor the gun wall's stacked breastwork. Runtime nodes: none (an
obstacle); the old node names `Gabions`, `Frames`, `Team_bands` are kept. Metres, +Z up, -Y front.
"""
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

W = 4.75             # along X
D = 1.9              # along Y
PAD = .06
C1, H1 = D, 1.0      # bottom course: depth, height
C2, H2 = 1.3, 1.04   # middle course
Y2 = (D - C2) / 2    # the middle course sits at the back: its centre line


def _pad(a):
    prof = [(-D / 2, .005), (D / 2, .005), (D / 2 - .05, .035), (D / 2 - .11, PAD), (-D / 2 + .11, PAD),
            (-D / 2 + .05, .035)]
    k.extrude(a.part('Base', 'Dirt'), prof, W, axis='X', chamfer=0)
    for x in (-1.6, 0, 1.6):
        K.dust(a, (x, -D / 2, 0), radius=1.2, k=.3)
        K.dust(a, (x, D / 2, 0), radius=1.0, k=.22)


def _course(a, rng, z0, depth, h, yc, n, tag):
    """One course of n baskets from x = -W/2 to W/2: the stone fill, the welded mesh frame, stones on the faces."""
    fill = a.part('Gabions', 'Rock')
    frame = a.part('Frames', 'Steel')
    bw = W / n
    for i in range(n):
        cx = -W / 2 + bw * (i + .5)
        k.block(fill, (bw - .03, depth - .03, h - .02), loc=(cx, yc, z0 + h / 2), chamfer=.05)
        # The frame: corner posts, rims top and bottom, the mid lacing wire, a diaphragm on top between baskets.
        for sx in (-1, 1):
            for sy in (-1, 1):
                frame.box((.03, .03, h), loc=(cx + sx * (bw / 2 - .015), yc + sy * (depth / 2 - .005), z0 + h / 2),
                          bevel=0)
        for z in (z0 + .02, z0 + h * .5, z0 + h - .015):
            for sy in (-1, 1):
                frame.box((bw - .02, .02, .02), loc=(cx, yc + sy * (depth / 2 - .002), z), bevel=0)
        frame.box((.02, depth, .02), loc=(cx + bw / 2 - .01, yc, z0 + h - .01), bevel=0)
        for f in (-.25, .25):
            frame.box((.014, .014, h - .04), loc=(cx + f * bw, yc - (depth / 2 - .002), z0 + h / 2), bevel=0)
        # Stones pressing against the mesh on the front and back faces (rotated rough blocks).
        st = a.part('Stones', 'Rock')
        for j in range(5):
            sy = -1 if j < 3 else 1
            s = rng.uniform(.1, .17)
            st.box((s, s * .7, s * .8), loc=(cx + rng.uniform(-.45, .45) * bw, yc + sy * (depth / 2 - .08),
                                             z0 + rng.uniform(.15, h - .15)),
                   rot=(rng.uniform(-.5, .5), rng.uniform(-.5, .5), rng.uniform(0, 3)), bevel=0)


def _top(a):
    path = [(-W / 2 + .3, Y2, PAD + H1 + H2), (W / 2 - .9, Y2, PAD + H1 + H2)]       # a gap at the right end
    P.sandbag_run(a, path, courses=2, bag=(.62, .36, .16), part='Sandbags', seed=51)
    # The bags on the step's front edge (one course), so the step reads from the battle camera.
    P.sandbag_run(a, [(-W / 2 + .4, -D / 2 + .3, PAD + H1), (W / 2 - .9, -D / 2 + .3, PAD + H1)], courses=1,
                  bag=(.55, .34, .14), part='Sandbags', seed=52)


def _marks(a, rng):
    band = a.part('Team_bands', 'Team')
    z = PAD + H1 + H2 * .55
    for sy in (-1, 1):
        band.box((W - .1, .012, .18), loc=(0, Y2 + sy * (C2 / 2 + .005), z), bevel=0)
    # Loose stones and a split sandbag at the front foot; a pick leaning on the end basket.
    st = a.part('Stones', 'Rock')
    for j in range(6):
        s = rng.uniform(.08, .15)
        st.box((s, s * .8, s * .6), loc=(rng.uniform(-2.1, 1.8), -D / 2 + .16, PAD + s * .3),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)
    k.block(a.part('Split_bag', 'Sandbag'), (.7, .28, .1), loc=(1.3, -.8, PAD + .05), rot=(0, 0, .03), chamfer=.04,
            taper=(1.1, .8))
    tools = a.part('Tools', 'Steel')
    tools.tube([(W / 2 - .1, -.5, PAD), (W / 2 - .02, -.45, PAD + .85)], .018, seg=4)
    tools.box((.04, .42, .05), loc=(W / 2 - .02, -.45, PAD + .85), rot=(.2, 0, 0), bevel=0)


def blast_wall(a):
    """The gabion blast wall: see the module docstring."""
    rng = random.Random(3541)
    _pad(a)
    _course(a, rng, PAD, C1, H1, 0, 4, 'a')
    _course(a, rng, PAD + H1, C2, H2, Y2, 4, 'b')
    _top(a)
    _marks(a, rng)
    K.tone(a, 'Gabions', k=.72, warm=.04)       # the packed stone reads darker than the loose stones on its faces
    k.clean(a)


BUILDERS = {
    'blast_wall': (blast_wall, dict(ao_distance=.6, grime_height=.6, ao_strength=.8)),
}
