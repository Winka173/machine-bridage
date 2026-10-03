"""Prompt 35 wave 3 (lane B): the HESCO wall segment rebuilt from scratch (spec: Tools/blender/specs/wall_hesco.json).

One logic segment of the base wall (balance.json wall_hesco: length 2, width 12; WallRules tiles the segments end to
end, so the box stays exactly 12.02 x 2.0 x 2.75 m, centred on the origin, the ground at z = 0, running along X with
its front to -Y). A field-built Accord line of HESCO MIL 7-class bastions (2.2 m tall, 1.9 m deep): eight 1.5 m cells
of earth inside welded wire mesh with the geotextile liner showing at the top, the joining coil pins at every cell
junction, the earth fill heaped and sagging between cells with tufts of weed, the liner folded over the rims; a
two-slope earth berm under it; concertina razor wire on angle-iron pickets along the top; the cells' stencilled ID
tags; spilled earth, a shovel and two stray sandbags at the foot; the Team band painted on the liner caps.

Own geometry: nothing is taken from the gun wall (MIL 1 stacked two high round a timber firing step) or the blast
wall (a single row of small MIL 1 cells). Metres, +Z up, -Y front (out of the base), +X along the wall.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
from mb_siege import coil

L = 12.0              # the segment's length along X (WallRules: width 12)
H = 2.2               # the cells' height
D = 1.84              # the cells' depth (Y)
CELLS = 8
CW = L / CELLS


def _berm(a):
    # Two slopes a side (a toe and a steeper shoulder), the full 12 m so segments join without a seam.
    prof = [(-.92, -.02), (.92, -.02), (.84, .045), (.8, .13), (-.8, .13), (-.84, .045)]
    k.extrude(a.part('Base', 'Dirt'), prof, L, axis='X', chamfer=0)
    # Trodden earth spilled along the foot on both sides (irregular low mounds).
    rng = random.Random(3501)
    spill = a.part('Spill', 'Dirt')
    for i, (x, s) in enumerate(((-5.0, 1), (-2.9, -1), (-.4, 1), (1.6, 1), (4.1, -1))):
        x += rng.uniform(-.2, .2)
        k.block(spill, (1.0 + rng.uniform(0, .4), .26, .14), loc=(x, s * .865, .05), rot=(0, 0, rng.uniform(-.02, .02)),
                chamfer=.05, taper=(.55, .5))
    for i in range(9):
        K.dust(a, (-6 + i * 1.5, -1.0, .05), radius=1.1, k=.32)
        K.dust(a, (-6 + i * 1.5, 1.0, .05), radius=1.0, k=.25)


def _cells(a):
    rng = random.Random(3502)
    fill = a.part('Walls', 'Sandbag')        # the cells (the beige geotextile over the earth fill; gate role "walls")
    heap = a.part('Fill_top', 'Dirt')
    liner = a.part('Liner', 'Canvas')
    weeds = a.part('Weeds', 'Grass')
    for i in range(CELLS):
        cx = -L / 2 + CW * (i + .5)
        h = H - .06 + rng.uniform(-.05, .02)
        # The filled liner bulges slightly through the mesh: a chamfered block a hair wider than the mesh line.
        k.block(fill, (CW - .05, D + .02, h), loc=(cx, 0, .13 + h / 2), chamfer=.09)
        # The heaped top, settled low in the middle of some cells.
        k.block(heap, (CW - .25, D - .3, .12), loc=(cx + rng.uniform(-.1, .1), rng.uniform(-.1, .1), .13 + h + .02),
                chamfer=.05, taper=(.7, .7))
        # The liner: the band of geotextile above the fill line on the outer faces, its lip folded over the rim.
        for s in (-1, 1):
            liner.box((CW - .06, .02, .32), loc=(cx, s * (D / 2 + .02), .13 + H - .2), bevel=0)
            liner.box((CW - .06, .14, .02), loc=(cx, s * (D / 2 - .05), .13 + H + .005), rot=(s * -.25, 0, 0), bevel=0)
        for j in range(2 + i % 2):
            weeds.tier(.14 + rng.uniform(0, .08), .16, loc=(cx + rng.uniform(-.5, .5), rng.uniform(-.6, .6),
                                                         .13 + h + .06), seg=5, droop=.2, seed=i * 3 + j)


def _mesh(a):
    """Welded wire mesh on both long faces: horizontal wires the full length, verticals every 0.5 m, the joining coil
    pin at each cell junction, the cross mesh dividing the cells on top."""
    mesh = a.part('Mesh', 'Steel')
    top = .13 + H
    for s in (-1, 1):
        y = s * (D / 2 + .035)
        for z in (.2, .55, .9, 1.25, 1.6, 1.95, top - .02):
            mesh.box((L - .02, .018, .018), loc=(0, y, z), bevel=0)
        for i in range(int(L / .5) + 1):
            x = -L / 2 + .01 + i * (L - .02) / int(L / .5)
            if i % 3 == 0:
                continue                                   # the coil pins stand at the cell junctions
            mesh.box((.016, .016, H - .05), loc=(x, y, .13 + H / 2), bevel=0)
    pins = a.part('Kit_pins', 'Steel')
    for i in range(CELLS + 1):
        x = -L / 2 + i * CW
        x = min(max(x, -L / 2 + .03), L / 2 - .03)
        for s in (-1, 1):
            y = s * (D / 2 + .04)
            pins.cyl(.024, H + .05, loc=(x, y, .13 + H / 2), seg=4, bevel=0)
        mesh.box((.02, D + .07, .02), loc=(x, 0, top - .01), bevel=0)


def _wire(a):
    """Concertina razor wire on angle-iron pickets along the top (the pickets driven into the fill)."""
    wire = a.part('Razor_wire', 'Steel')
    coil(wire, -L / 2 + .01, L / 2 - .01, 0, 2.73 - .27, .26, pitch=.4, pts=6, wire=.016)
    pickets = a.part('Pickets', 'Undercarriage')
    for i in range(6):
        x = -L / 2 + 1.0 + i * 2.0
        pickets.box((.045, .045, .6), loc=(x, .02, .13 + H + .1), rot=(0, 0, .78), bevel=0)
        pickets.box((.36, .02, .02), loc=(x, .02, 2.66), bevel=0)


def _marks(a):
    # The Team band painted across the liner caps, the stencilled ID tags wired to the mesh (plain, no insignia).
    band = a.part('Wall_band', 'Team')
    for s in (-1, 1):
        band.box((L - .12, .02, .2), loc=(0, s * (D / 2 + .045), .13 + H - .22), bevel=0)
    tags = a.part('Stencil', 'Hazard')
    for i in range(0, CELLS, 2):
        cx = -L / 2 + CW * (i + .5)
        tags.box((.28, .015, .18), loc=(cx - .35, -(D / 2 + .05), 1.15), bevel=0)
        tags.box((.28, .015, .18), loc=(cx + .4, D / 2 + .05, 1.15), bevel=0)


def _kit(a):
    # Sandbags weighing the liner down on two cells, a shovel left stuck in a cell's fill, a drainage pipe through
    # the berm.
    bags = a.part('Sandbags', 'Sandbag')
    z = .13 + H + .06
    for x, y, r in ((2.4, .45, .3), (2.85, -.2, -.2), (-3.9, .1, .1)):
        k.block(bags, (.6, .32, .15), loc=(x, y, z + .02), rot=(0, 0, r), chamfer=.06, ends=(True, True))
    tools = a.part('Tools', 'Steel')
    tools.tube([(-1.6, .3, z - .1), (-1.3, .42, z + .22)], .018, seg=4)
    tools.box((.2, .14, .03), loc=(-1.28, .43, z + .24), rot=(.3, .6, 0), bevel=0)
    k.lathe(a.part('Drain', 'Undercarriage'), [(.09, -.99), (.11, -.97), (.11, .97), (.09, .99)],
            loc=(-.75, 0, .1), rot=(math.pi / 2, 0, 0), seg=8)


def wall_hesco(a):
    """The HESCO wall segment: see the module docstring."""
    _berm(a)
    _cells(a)
    _mesh(a)
    _wire(a)
    _marks(a)
    _kit(a)
    k.clean(a)


BUILDERS = {
    'wall_hesco': (wall_hesco, dict(ao_distance=.7, grime_height=.6, ao_strength=.8)),
}
