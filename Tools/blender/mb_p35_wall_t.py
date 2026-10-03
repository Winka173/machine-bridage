"""Prompt 35 wave 3 (lane B): the T-wall segment rebuilt from scratch (spec: Tools/blender/specs/wall_t.json).

One logic segment of the base wall (balance.json wall_t: length 2, width 12; WallRules tiles the segments end to end,
so the box stays 12.0 x 1.9 x 3.92 m, centred on the origin, ground at z = 0, along X, front to -Y). Eight precast
Bremer-class T-wall panels (1.5 m wide, 3.6 m tall: the stem tapering from 0.3 m to 0.2 m, fillets into a 1.3 m foot
with forklift slots) standing on a two-slope gravel bed; on each panel two cast lifting loops, chipped arrises, the
stencilled panel number; a Team stripe sprayed across the faces; a concertina coil clipped along the top; on the inner
side sandbags packed into the joints at the foot, a cable run on stakes; a hazard chevron board on the end panel.
The concrete panels are precast; the field work round them (sandbags, wire, sprayed marks) is the Accord's.

Own geometry: no shape is shared with the HESCO, gun or blast walls. Metres, +Z up, -Y front (out of the base).
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P
from mb_siege import coil

L = 12.0
N = 8
PW = L / N            # a panel's width along X
GAP = .03
HT = 3.6              # panel height
BED = .1              # top of the gravel bed


def _bed(a):
    prof = [(-.95, 0), (.95, 0), (.91, .04), (.71, BED), (-.71, BED), (-.91, .04)]
    k.extrude(a.part('Base', 'Rock'), prof, L, axis='X', chamfer=0)
    for i in range(7):
        K.dust(a, (-6 + i * 2, -.95, 0), radius=1.4, k=.3)
        K.dust(a, (-5 + i * 2, .95, 0), radius=1.2, k=.25)


def _panel(a, x, rng, i):
    """One T-wall panel standing on the bed at x (its centre)."""
    w = PW - GAP
    # The cross-section: the foot (1.3 m deep), the fillets, the stem tapering up to the cap.
    prof = [(-.65, 0), (.65, 0), (.65, .2), (.5, .26), (.17, .42), (.15, .62), (.1, HT), (-.1, HT), (-.15, .62),
            (-.17, .42), (-.5, .26), (-.65, .2)]
    # Panels from two casting batches: every other one a shade darker (COLOR_0 tone below).
    k.extrude(a.part('Panels' if i % 2 == 0 else 'Panels_b', 'Concrete'), prof, w, loc=(x, 0, BED), axis='X',
              chamfer=.035)
    # Rain streaks running down the front face from the cap, and mud splashed up the foot.
    streak = a.part('Streaks', 'Dirt')
    for j in range(2 + i % 2):
        dx = rng.uniform(-.55, .55)
        ln = rng.uniform(.5, 1.3)
        z = BED + HT - .05 - ln / 2
        t = .1 + .05 * (1 - (z - BED - .62) / (HT - .62))
        streak.box((.05 + rng.uniform(0, .05), .01, ln), loc=(x + dx, -t - .004, z), rot=(-.017, 0, 0), bevel=0)
    # Forklift slots through the foot, both faces.
    slot = a.part('Panel_slots', 'Undercarriage')
    for dx in (-.35, .35):
        for s in (-1, 1):
            slot.box((.22, .02, .08), loc=(x + dx, s * .653, BED + .08), bevel=0)
    # Lifting loops on the cap (cast steel bows).
    loops = a.part('Kit_loops', 'Steel')
    for dx in (-.42, .42):
        loops.tube([(x + dx - .07, 0, BED + HT - .02), (x + dx - .05, 0, BED + HT + .07),
                    (x + dx + .05, 0, BED + HT + .07), (x + dx + .07, 0, BED + HT - .02)], .016, seg=4)
    # Chipped arrises: a few dark spalls on the stem's edges (Charred), placed per panel.
    chips = a.part('Spalls', 'Charred')
    for j in range(2):
        z = BED + rng.uniform(.8, 3.2)
        sx = rng.choice((-1, 1))
        t = .1 + (.15 - .1) * (1 - (z - BED - .62) / (HT - .62))
        chips.box((.07, .02, .1 + rng.uniform(0, .08)), loc=(x + sx * (w / 2 - .03), -t - .005, z), bevel=0)
    # The stencilled panel number on the front face (a plain plate, no insignia).
    a.part('Stencil', 'Charred').box((.34, .012, .22), loc=(x - .3, -.14, BED + 1.25), rot=(-.014, 0, 0), bevel=0)


def _marks(a):
    # The Team stripe sprayed across all the panels, both faces (following the stem's taper).
    band = a.part('Wall_band', 'Team')
    z = BED + 2.55
    t = .1 + .05 * (1 - (2.55 - .62) / (HT - .62)) + .006
    for s in (-1, 1):
        for i in range(N):
            x = -L / 2 + PW * (i + .5)
            band.box((PW - GAP - .02, .012, .32), loc=(x, s * t, z), rot=(s * -.014, 0, 0), bevel=0)
    # A hazard chevron board bolted on the last panel's front.
    x = L / 2 - PW / 2
    a.part('Hazard', 'Hazard').box((.7, .02, .45), loc=(x + .2, -.155, BED + .95), rot=(-.014, 0, 0), bevel=0)
    stripes = a.part('Hazard_stripes', 'Charred')
    for j in range(3):
        stripes.box((.08, .012, .5), loc=(x + .2 - .22 + j * .22, -.168, BED + .95), rot=(-.014, 0, .6), bevel=0)


def _wire(a):
    wire = a.part('Razor_wire', 'Steel')
    coil(wire, -L / 2 + .01, L / 2 - .01, 0, 3.92 - .16, .145, pitch=.42, pts=6, wire=.014)
    clips = a.part('Wire_clips', 'Undercarriage')
    for i in range(N):
        x = -L / 2 + PW * (i + .5)
        clips.box((.05, .24, .06), loc=(x, 0, BED + HT + .02), bevel=0)


def _field(a, rng):
    # Sandbags packed into the joints at the inner foot, two high.
    for i in range(1, N):
        x = -L / 2 + PW * i
        P.sandbag_run(a, [(x, .45, BED + .2), (x, .72, BED + .2)], courses=2 if i % 3 else 1, bag=(.5, .28, .13),
                      part='Sandbags', seed=40 + i)
    # A field telephone cable on short stakes along the inner foot.
    stakes = a.part('Stakes', 'Wood')
    pts = []
    for i in range(7):
        x = -5.4 + i * 1.8
        stakes.box((.04, .04, .45), loc=(x, .82, BED + .2), bevel=0)
        pts.append((x, .82, BED + .38 - .05 * (i % 2)))
    a.part('Kit_cables', 'Undercarriage').tube(pts, .012, seg=3)


def wall_t(a):
    """The T-wall segment: see the module docstring."""
    rng = random.Random(3531)
    _bed(a)
    for i in range(N):
        _panel(a, -L / 2 + PW * (i + .5), rng, i)
    _marks(a)
    _wire(a)
    _field(a, rng)
    K.tone(a, 'Panels_b', k=.84, warm=.03)
    k.clean(a)


BUILDERS = {
    'wall_t': (wall_t, dict(ao_distance=.7, grime_height=.8, ao_strength=.75)),
}
