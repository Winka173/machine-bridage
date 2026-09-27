"""High-detail kit for the `<id>_hd` model variants (the high graphics tiers load them instead of `<id>`
when they exist; see ModelLibrary.HighDetail).

A builder that supports it takes `detail=False`; `detail=True` runs the very same code and then adds what
only reads at a close camera: bolt and rivet rows, hinges, lifting eyes, handles, track links, wheel nuts,
tread, panel lines. The builder marks the asset with `mark(a, detail)` first, so the shared helpers
(tracks, wheels, hatches, bins, lights ... in mb_vehicles / mb_air) add their own small parts too; with
detail off nothing here runs and the normal model is built exactly as before.

Rules that keep the game logic unchanged (checked by comparing each `_hd` GLB with its normal GLB):
  * No pivot is added, moved or renamed, and every normal part keeps its name.
  * Nothing is added to the parts the runtime measures: the aim/recoil rig and the elevation group
    (Main_cannon*, Muzzle_brake*, Coax*, Launcher*, Tubes*, Pod* under the Turret) and the launcher
    groups (Pods, Missiles, Tubes_bore ...), so the trunnion, muzzle and launch points stay put.
  * Detail stays inside the normal model's bounds, and the hull footprint does not change.
  * New part names never start with a runtime pattern (Turret, Main_cannon, Muzzle, Mount_, Rotor ...
    unless they are unique rotor parts, Tubes, Pod, Launcher, Coax, Barrel, Cannon).
Small repeated parts are never bevelled and sink 1 cm into the surface they sit on.
"""
import math

from mathutils import Euler, Matrix, Vector

R90 = math.pi / 2
TAU = math.tau
# Local Z of a cylinder / bolt turned to face these directions.
UP = (0, 0, 0)
FRONT = (R90, 0, 0)      # -Y
BACK = (-R90, 0, 0)      # +Y
RIGHT_X = (0, R90, 0)    # +X
LEFT_X = (0, -R90, 0)    # -X


def mark(a, detail):
    """Flag the asset so shared helpers add their high-detail parts; returns detail."""
    a.hd = bool(detail)
    return a.hd


def on(a):
    """Whether this asset is being built as a high-detail variant."""
    return getattr(a, 'hd', False)


def frame(loc, rot=(0, 0, 0)):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


def side_rot(s):
    """Rotation facing a bolt out of the +X (s = 1) or -X (s = -1) side."""
    return RIGHT_X if s > 0 else LEFT_X


def bolt(part, p, rot=UP, r=.02, h=.025, seg=6):
    """One hex bolt head on a surface point p whose outward normal is local Z of rot; it stands
    h - 1 cm proud."""
    m = frame(p, rot)
    part.cyl(r, h, loc=tuple(m @ Vector((0, 0, h / 2 - .01))), rot=rot, seg=seg, bevel=0)


def bolt_line(part, p0, p1, n, rot=UP, r=.02, h=.025, seg=6, inset=0.0):
    """n bolt heads evenly from p0 to p1 (inset metres in from both ends)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length > 1e-6 and inset:
        u = d.normalized()
        p0, p1 = p0 + u * inset, p1 - u * inset
    for i in range(n):
        k = .5 if n == 1 else i / (n - 1)
        bolt(part, tuple(p0.lerp(p1, k)), rot, r, h, seg)


def bolt_ring(part, m, R, n, r=.018, h=.022, seg=6, phase=0.0):
    """n bolt heads on a circle of radius R in the local XY plane of frame m (bolts face local +Z)."""
    rot = m.to_euler('XYZ')
    for k in range(n):
        u = phase + k * TAU / n
        p = m @ Vector((R * math.cos(u), R * math.sin(u), h / 2 - .01))
        part.cyl(r, h, loc=tuple(p), rot=rot, seg=seg, bevel=0)


def plate_bolts(part, m, w, h, nx, ny, r=.018, hh=.022, inset=.06):
    """Bolts round the edge of a w x h rectangle in the local XY plane of frame m: nx along the long
    edges, ny along the short ones (corners shared)."""
    rot = m.to_euler('XYZ')
    x0, y0 = w / 2 - inset, h / 2 - inset
    pts = set()
    for i in range(nx):
        x = -x0 + 2 * x0 * (i / max(1, nx - 1))
        pts.add((round(x, 5), y0))
        pts.add((round(x, 5), -y0))
    for j in range(ny):
        y = -y0 + 2 * y0 * (j / max(1, ny - 1))
        pts.add((x0, round(y, 5)))
        pts.add((-x0, round(y, 5)))
    for x, y in sorted(pts):
        part.cyl(r, hh, loc=tuple(m @ Vector((x, y, hh / 2 - .01))), rot=rot, seg=6, bevel=0)


def lifting_eye(part, loc, yaw=0.0, size=.09, rot=None):
    """Lifting eye on a surface at loc: a base pad and a hoop standing up (across local X after yaw)."""
    rot = rot if rot is not None else (0, 0, yaw)
    m = frame(loc, rot)
    part.box((size * 1.1, size * .6, .03), loc=tuple(m @ Vector((0, 0, .005))), rot=rot, bevel=0)
    w, h = size * .42, size * .85
    part.tube([tuple(m @ Vector(p)) for p in ((-w, 0, 0), (-w, 0, h * .7), (-w * .5, 0, h), (w * .5, 0, h),
                                                  (w, 0, h * .7), (w, 0, 0))], size * .12, seg=4)


def hinge(part, p0, p1, r=.028, knuckles=3, seg=8):
    """Piano hinge from p0 to p1: `knuckles` barrels with gaps and a pin through them."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler('XYZ')
    L = d.length
    step = L / knuckles
    for i in range(knuckles):
        part.cyl(r, step * .8, loc=tuple(p0 + d * ((i + .5) / knuckles)), rot=rot, seg=seg, bevel=0)
    part.cyl(r * .45, L + .04, loc=tuple((p0 + p1) / 2), rot=rot, seg=6, bevel=0)


def handle(part, p0, p1, up, h=.07, r=.013):
    """Bent grab handle between p0 and p1 standing `h` off the surface along `up`."""
    p0, p1, u = Vector(p0), Vector(p1), Vector(up).normalized()
    part.tube([tuple(p0 - u * .01), tuple(p0 + u * h), tuple(p1 + u * h), tuple(p1 - u * .01)], r, seg=4)
