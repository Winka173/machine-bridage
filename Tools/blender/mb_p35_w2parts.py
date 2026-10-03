"""Prompt 35 wave 2 (lane A): lean parametric helpers for the wave's towers (DECISIONS "Prompt 35 wave 2 (lane A)").

Not a model: generic sub-assemblies called with each tower's own sizes (prompt 35 section 1 allows a component
library; bodies, launchers, turrets stay in each tower's own builder). Written for the 6,000-triangle tower cap (owner
decision 6): pieces seen at the battle camera's 28.4 px per metre, without the faces it never sees.

* bags: a sandbag course along a polyline, every bag a pillow of six-sided cross-section (20 triangles; kit35's
  chamfered bag is about 60).
* slab: a box without the faces that rest on something or sit under a roof (caps chosen by the caller).
* lift_lines: the dark formwork joints of a cast wall (thin strips just proud of a face).
* bolt_grid: a grid of hex bolt heads on a plate (anchor bolts, base plates).
* stack: a stack of ammunition boxes with lids and latches.

Conventions: frontier_kit's (metres, +Z up, -Y the front, +X the left side).
"""
import math
import random

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


def bags(a, path, layers=1, bag=(.6, .3, .17), parent=None, mat='Sandbag', name='Sandbags', seed=0, closed=False):
    """Sandbags along a polyline (z of each point = the course's base), `layers` courses offset by half a bag; each
    bag a pillow: a six-sided section (flat bottom, bulging sides, rounded top) extruded along the bag, its ends
    pinched in a little. Deterministic jitter (seed)."""
    part = a.part(name, mat, parent)
    rng = random.Random(seed * 7919 + len(path) * 31 + layers)
    L, W, H = bag
    prof = [(-W * .42, 0), (W * .42, 0), (W * .5, H * .45), (W * .3, H), (-W * .3, H), (-W * .5, H * .45)]
    pts = path + path[:1] if closed else path
    for course in range(layers):
        start = L / 2 * (course % 2)
        for p, t in k.along(pts, pitch=L * .97, start=start):
            yaw = math.atan2(t.y, t.x)
            j = rng.uniform(-.04, .04)
            k.extrude(part, [(x * (1 + j), z * (1 - j * .5)) for x, z in prof], L * (.95 + j), loc=(p.x, p.y, p.z +
                      course * H * .9), rot=(0, 0, yaw + rng.uniform(-.06, .06)), axis='X', chamfer=0,
                      taper=(.82, .9))
    return part


def slab(part, size, loc, caps=(False, True), chamfer=.04, taper=(1, 1), rot=(0, 0, 0)):
    """A box on its base (loc = the centre of its bottom face) with the vertical corners chamfered; caps=(bottom,
    top) leaves out the faces that are never seen (resting on a pad, under a roof)."""
    w, d, h = size
    c = min(chamfer, w * .3, d * .3)
    prof = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    x, y, z = loc
    k.extrude(part, prof, h, loc=(x, y, z + h / 2), rot=rot, axis='Z', chamfer=0, corner=c, taper=taper, caps=caps)
    return part


def lift_lines(a, face_centre, along, length, heights, normal, parent=None, w=.03):
    """Dark formwork lift joints on a cast face: horizontal strips `length` long at the given heights (z offsets
    from face_centre), lying along `along` ('x' or 'y'), just proud of the face (normal: its outward axis sign)."""
    part = a.part('Lift_joints', 'Undercarriage', parent)
    x, y, z = face_centre
    for h in heights:
        if along == 'x':
            part.box((length, .012, w * .7), loc=(x, y + normal * .006, z + h), bevel=0)
        else:
            part.box((.012, length, w * .7), loc=(x + normal * .006, y, z + h), bevel=0)


def bolt_grid(part, centre, nx, ny, pitch, r=.025, h=.03, seg=6):
    x, y, z = centre
    for i in range(nx):
        for j in range(ny):
            part.cyl(r, h, loc=(x + (i - (nx - 1) / 2) * pitch, y + (j - (ny - 1) / 2) * pitch, z + h / 2), seg=seg,
                     bevel=0)


def stack(a, loc, n=3, size=(.55, .3, .22), yaw=0.0, parent=None, mat='Crate', name='Ammo_boxes', seed=0):
    """A stack of ammunition boxes: each a box with a lid lip and a latch, the stack slightly staggered."""
    rng = random.Random(seed)
    w, d, h = size
    x, y, z = loc
    part = a.part(name, mat, parent)
    lat = a.part('Kit_latches', 'Steel', parent)
    for i in range(n):
        dx, dy = rng.uniform(-.04, .04), rng.uniform(-.03, .03)
        r = yaw + rng.uniform(-.08, .08)
        c, s_ = math.cos(r), math.sin(r)
        cz = z + i * h
        part.box((w, d, h * .86), loc=(x + dx, y + dy, cz + h * .43), rot=(0, 0, r), bevel=0)
        part.box((w * 1.02, d * 1.04, h * .14), loc=(x + dx, y + dy, cz + h * .93), rot=(0, 0, r), bevel=0)
        ox, oy = -s_ * (d / 2 + .01), c * (d / 2 + .01)
        lat.box((.05, .02, .05), loc=(x + dx - ox, y + dy - oy, cz + h * .8), rot=(0, 0, r), bevel=0)
    return part


def guard_posts(part, points, h=.9, r=.05, seg=6):
    """Bollards / short posts at the given ground points."""
    for (x, y, z) in points:
        part.cyl(r, h, loc=(x, y, z + h / 2), seg=seg, bevel=0)


def along_y_tube(part, x, y0, y1, z, r, seg=8, caps=(True, True)):
    """A plain cylinder along Y from y0 to y1 at (x, z)."""
    L = abs(y1 - y0)
    k.lathe(part, [(r, -L / 2), (r, L / 2)], loc=(x, (y0 + y1) / 2, z), rot=(R90, 0, 0), seg=seg, caps=caps)
