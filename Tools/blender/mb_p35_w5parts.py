"""Prompt 35 wave 5 (lane A): lean helpers the wave's builders share (DECISIONS "Prompt 35 wave 5 (lane A)").

Kit-level pieces with every size a parameter (prompt 35 section 1 allows a parametric component library): a tracked
running gear (belt outline round the wheels, links on the visible runs, road wheels, sprocket, idler, return rollers),
a welded hull plate set from a side profile, a sloped polygon turret, a bolted armour panel row, a cable run. No
model's hull, turret, wing or superstructure comes from here: each builder draws its own.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_parts27 as p27
import mb_vehicles as mv

R90 = math.pi / 2
TAU = math.tau


def running_gear(a, tx, tw, wr, wheels, idler, sprocket, rollers=(), roller_z=None, disc_mat='Armor', seg=10,
                 link_pitch=.24, top_hidden=None, wheel_w=.2, teeth=10, sides=(-1, 1), tag='', dust=.28):
    """Both tracks at |x| = tx (belt tw wide): road wheels of radius wr at the y's in `wheels`, idler and sprocket
    as (y, z, r), return rollers at `rollers` (y's) at roller_z. The belt is the convex outline of the wheels; links
    run round it except along the top run when `top_hidden` (z above which a skirt hides it) is given."""
    belt = a.part('Tracks' + tag, 'Undercarriage')
    links = a.part('Track_links' + tag, 'Undercarriage')
    iy, iz, ir = idler
    sy, sz, sr = sprocket
    pts = []
    for cy, cz, r in ((iy, iz, ir + .02), (sy, sz, sr + .02)) + tuple((y, wr, wr + .04) for y in wheels):
        for i in range(20):
            u = i * TAU / 20
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    outline = mv._hull2d(pts)
    face = tw / 2 - .14
    for s in sides:
        k.extrude(belt, outline, tw, loc=(s * tx, 0, 0), axis='X', chamfer=0)
        for (py, pz), (ty, tz) in mv._perimeter(outline, link_pitch, .0):
            if top_hidden is not None and pz > top_hidden and min(wheels) < py < max(wheels):
                continue
            ny, nz = tz, -ty
            k.block(links, (tw + .04, .07, .04), loc=(s * tx, py + ny * .014, pz + nz * .014),
                    rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
        for y in wheels:
            p27.road_wheel(a, (s * (tx + face), y, wr), wr, wheel_w, s, seg=seg, disc_mat=disc_mat)
        p27.sprocket(a, (s * (tx + face), sy, sz), sr, teeth, wheel_w * .7, s)
        k.lathe(a.part('Idlers' + tag, disc_mat), [(0, .1), (ir * .4, .1), (ir * .45, .08), (ir * .9, .08),
                                                   (ir, .05), (ir, -.07), (ir * .85, -.08), (0, -.08)],
                loc=(s * (tx + face), iy, iz), rot=p27.side_rot(s), seg=seg, worn=(4,))
        for y in rollers:
            K.return_roller(a, (s * (tx + face - .02), y, roller_z if roller_z is not None else wr * 2.3), .09,
                            .11, s)
        if dust:
            K.dust(a, (s * tx, (iy + sy) / 2, .1), radius=abs(sy - iy) * .4, k=dust)


def side_hull(part, profile, width, chamfer=.05, corner=.03, x=0.0):
    """A hull block from its side profile [(y, z) ...] (counter-clockwise seen from +X), `width` across."""
    k.extrude(part, profile, width, loc=(x, 0, 0), axis='X', chamfer=chamfer, corner=corner)


def poly_turret(part, rings, chamfer=.04):
    """A faceted turret from horizontal sections [(z, [(x, y) ...]) ...], every section the same point count."""
    k.sharp_loft(part, [[(x, y, z) for x, y in pts] for z, pts in rings], chamfer=chamfer)


def bolted_row(a, part_name, mat, p0, p1, n, size, normal, parent=None, rivet=.2):
    """n bolted panels of `size` (w, h) evenly from p0 to p1 lying on a face with `normal` (applique armour)."""
    p0, p1 = Vector(p0), Vector(p1)
    for i in range(n):
        f = (i + .5) / n
        K.panel(a, a.part(part_name, mat, parent), size, tuple(p0 + (p1 - p0) * f), normal, t=.05, rivet=rivet,
                parent=parent)


def cable(part, points, r=.02):
    part.tube(points, r, seg=5)


def lifting_eyes(part, points, r=.05):
    """Lifting eyes (a torus standing on a small plate) at points, turned across the vehicle."""
    for p in points:
        part.torus(r, r * .3, loc=p, rot=(0, R90, 0), seg=8, ring=4)


def tow_set(a, y, z, half, facing):
    """Two tow hooks at the hull's end plate and a tow cable looped between them across the plate."""
    hooks = a.part('Kit_tow', 'Steel')
    for s in (-1, 1):
        K.tow_hook(hooks, (s * half, y, z), facing=facing, size=.11)
    d = facing[1]
    K.tow_cable(a.part('Kit_cables', 'Steel'), [(-half, y + d * .05, z + .18), (-half * .4, y + d * .08, z + .3),
                                                (half * .4, y + d * .08, z + .3), (half, y + d * .05, z + .18)],
                r=.022)
