"""Machine Brigade equipment icons, second set: one picture per gear item id, in the same look as
mb_gear_icons.py (frontier kit parts, bevels, baked occlusion and materials, the same lights and 3/4
camera, transparent background). The rarity frame is drawn by the game, so only the object is rendered.

Rebuild everything (from the repository root, C:/Users/Winka/Projects/MachineBrigade):

  "C:/Users/Winka/Tools/blender-4.5.14-windows-x64/blender.exe" --background --python Tools/blender/mb_gear_icons2.py

or only some ids:

  ... --python Tools/blender/mb_gear_icons2.py -- long_barrel drone_escort

Writes Assets/MachineBrigade/Resources/UI/Gear/<id>.png (256 x 256 RGBA). Ids whose picture already
exists in the first set (REUSED below) are copied from that file instead of rendered; the ten
gear_*.png originals are never touched. Every render is framed on its projected silhouette so each
object fills the same share of the tile and sits in its centre.
"""
import ast
import math
import random
import shutil
import sys
import types
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frontier_kit as fk  # noqa: E402


def _load_first_set():
    """mb_gear_icons.py renders its ten pictures as soon as it runs; load its helpers (scene setup,
    team paint, axis constants, builders) without that final main() call."""
    path = HERE / 'mb_gear_icons.py'
    tree = ast.parse(path.read_text(encoding='utf-8'), str(path))
    tree.body = [n for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                                              and getattr(n.value.func, 'id', None) == 'main')]
    module = types.ModuleType('mb_gear_icons')
    module.__file__ = str(path)
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module


gi = _load_first_set()
OUT = gi.OUT
R90, ALONG_X, ALONG_Y = gi.R90, gi.ALONG_X, gi.ALONG_Y
TAU = math.tau
UP = Vector((0, 0, 1))
FILL = 0.88  # the object's larger projected side, as a share of the picture
CAM_DIR = Vector((0.75, -1.0, 0.72)).normalized()  # object -> camera, the first set's view
CAM_RIGHT = (-CAM_DIR).cross(UP).normalized()
CAM_UP = CAM_RIGHT.cross(-CAM_DIR).normalized()

# Pictures the first set already draws for these ids.
REUSED = {
    'carousel_autoloader': 'gear_loader',
    'toolbox': 'gear_repair',
    'reactive_armor': 'gear_reactivearmor',
    'auto_repair': 'gear_autorepair',
    'veteran_crew': 'gear_veterancrew',
    'smoke_discharger': 'gear_smokedischarger',
}

# Icon-only accents, added to the kit at run time (the kit file is shared with every model).
fk.MATERIALS.update({
    'LensTeal': ('#1fd8c6', 0.2, 0.16, 1.1),     # optics lenses and screens
    'Titanium': ('#aab6c2', 0.85, 0.3, 0.0),
    'Kevlar': ('#e9bf36', 0.0, 0.78, 0.0),
    'Copper': ('#d97c45', 0.9, 0.3, 0.0),         # coils, driving bands, bullet jackets
    'ClothRed': ('#d93a2c', 0.0, 0.7, 0.0),
    'ShieldGlow': ('#4fe3ff', 0.0, 0.2, 1.8),
    'ShieldGlass': ('#5fe8ff', 0.0, 0.1, 0.6),    # made translucent after the build
    # Kit glows (EliteGlow, Alloy, Energy) tone-map to pink and white at icon size. These are lit by their
    # emission alone (see GLOW_ONLY), so they keep their hue.
    'Flare': ('#ffc21a', 0.0, 0.6, 1.3),          # burning flare heads, flame cores
    'SignalRed': ('#ff1a0e', 0.0, 0.6, 1.0),      # lasers, buttons, reticles, radar
    'Amber': ('#ff9212', 0.0, 0.6, 1.0),
    'FlameOrange': ('#ff4e0a', 0.0, 0.6, 1.0),
    'ChargeBlue': ('#2a86ff', 0.0, 0.6, 1.4),
})
GLOW_ONLY = {'Flare', 'SignalRed', 'Amber', 'FlameOrange', 'ChargeBlue'}
fk.GLOWING.update({'LensTeal', 'ShieldGlow', 'ShieldGlass', 'Flare', 'SignalRed', 'Amber', 'FlameOrange', 'ChargeBlue'})


# ----------------------------------------------------------------------------- helpers
def _m(loc, rot):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


class Frame:
    """A local frame: F(loc, rot) gives the loc/rot keywords of a primitive placed in it, F.p a point."""

    def __init__(self, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
        self.m = (parent.m if parent else Matrix.Identity(4)) @ _m(loc, rot)

    def __call__(self, loc=(0, 0, 0), rot=(0, 0, 0)):
        m = self.m @ _m(loc, rot)
        return {'loc': m.to_translation(), 'rot': m.to_euler('XYZ')}

    def p(self, point):
        return self.m @ Vector(point)

    def v(self, vec):
        return self.m.to_3x3() @ Vector(vec)


def aim(d):
    """Rotation turning local +X along d with local +Z kept as near to up as possible."""
    return Vector(d).normalized().to_track_quat('X', 'Z').to_euler()


def facing(d=CAM_DIR):
    """Rotation turning local +Z along d (dials, rings and discs that face the camera)."""
    return Vector(d).normalized().to_track_quat('Z', 'Y').to_euler()


def vtube(shape, points, radii, seg=10, caps=True):
    """Shape.tube with a radius per point (snail housings, smoke trails)."""
    pts = [Vector(p) for p in points]
    radii = [radii] * len(pts) if isinstance(radii, (int, float)) else list(radii)
    tangents = [(pts[min(len(pts) - 1, i + 1)] - pts[max(0, i - 1)]).normalized() for i in range(len(pts))]
    normal = tangents[0].cross(UP if abs(tangents[0].z) < 0.9 else Vector((1, 0, 0))).normalized()
    rings = []
    for i, (p, t) in enumerate(zip(pts, tangents)):
        if i:
            axis = tangents[i - 1].cross(t)
            if axis.length > 1e-6:
                normal = Matrix.Rotation(tangents[i - 1].angle(t), 3, axis.normalized()) @ normal
        normal = (normal - t * normal.dot(t)).normalized()
        binormal = t.cross(normal).normalized()
        rings.append([shape.bm.verts.new(p + (normal * math.cos(a) + binormal * math.sin(a)) * radii[i])
                      for a in (j * TAU / seg for j in range(seg))])
    shape._faces(rings, caps, caps)
    return shape


def arc3(c, u, v, r, a0, a1, n=14):
    c, u, v = Vector(c), Vector(u), Vector(v)
    return [c + (u * math.cos(a) + v * math.sin(a)) * r for a in (a0 + (a1 - a0) * i / n for i in range(n + 1))]


def gear_outline(r_root, r_tip, teeth, phase=0.0):
    """(x, y) outline of a toothed wheel; with r_tip < r_root the teeth point inwards (ring gears)."""
    p = TAU / teeth
    pts = []
    for i in range(teeth):
        a = phase + i * p
        for f, r in ((0.0, r_root), (0.16, r_tip), (0.44, r_tip), (0.6, r_root)):
            pts.append((r * math.cos(a + f * p), r * math.sin(a + f * p)))
    return pts


def spur(shape, r, teeth, depth, loc, rot=(0, 0, 0), tooth=None, phase=0.0):
    """Spur gear of tip radius r, axle along local Z."""
    tooth = tooth or r * 0.17
    return shape.prism(gear_outline(r - tooth, r, teeth, phase), depth, loc=loc, rot=rot, axis='Z', bevel=0.012, seg=1)


def ring_gear(shape, r_out, r_root, r_tip, teeth, depth, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Flat annulus with teeth on its inner edge (r_root == r_tip gives a plain ring)."""
    inner = gear_outline(r_root, r_tip, teeth)
    outer = [(r_out * math.cos(math.atan2(y, x)), r_out * math.sin(math.atan2(y, x))) for x, y in inner]
    bm, h = shape.bm, depth / 2
    ob = [bm.verts.new((x, y, -h)) for x, y in outer]
    ot = [bm.verts.new((x, y, h)) for x, y in outer]
    it = [bm.verts.new((x, y, h)) for x, y in inner]
    ib = [bm.verts.new((x, y, -h)) for x, y in inner]
    shape._faces([ob, ot, it, ib, ob], cap_start=False, cap_end=False)
    shape._finish(ob + ot + it + ib, loc, rot, 0.012, 1)
    return shape


def sheet(shape, fn, nu, nv, thick):
    """Closed thin slab through a surface fn(u, v) -> (point, normal): flags, cloth."""
    bm = shape.bm
    rings = []
    for i in range(nu + 1):
        col = [fn(i / nu, j / nv) for j in range(nv + 1)]
        rings.append([bm.verts.new(p - n * thick / 2) for p, n in col] +
                     [bm.verts.new(p + n * thick / 2) for p, n in reversed(col)])
    shape._faces(rings)
    return shape


def zigzag(a, b, n, amp, seed):
    """Lightning: a jagged polyline from a to b, jagging across the view so it reads."""
    rng = random.Random(seed)
    a, b = Vector(a), Vector(b)
    d = b - a
    side = d.cross(CAM_DIR).normalized()
    pts = [a]
    for i in range(1, n):
        pts.append(a + d * (i / n) + side * amp * (1 if i % 2 else -1) * rng.uniform(0.5, 1.0))
    pts.append(b)
    return pts


def catmull(points, per=8):
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for k in range(per):
            t = k / per
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


def resample(poly, step):
    out, carry = [poly[0].copy()], 0.0
    for a, b in zip(poly, poly[1:]):
        seg = (b - a).length
        d = step - carry
        while d <= seg:
            out.append(a + (b - a) * (d / seg))
            d += step
        carry = seg - (d - step)
    return out


def rot_to(n):
    """Rotation turning local +Z along n."""
    return Vector((0, 0, 1)).rotation_difference(Vector(n).normalized()).to_euler()


def along_x(z):
    """Placement for parts of a shell/bomb built along local X (lathe profiles run along Z)."""
    return (z, 0, 0), ALONG_X


# ----------------------------------------------------------------------------- weapon slot
def long_barrel(a):
    """Long barrel: a slender gun tube in its olive thermal sleeve, clamp bands, a fat fume extractor
    two-thirds of the way out and the muzzle reference sensor."""
    F = Frame(rot=aim((0.42, 0.62, 0.66)))
    breech, sleeve, band, tip, bore = (a.part('Breech', 'Armor'), a.part('Sleeve', 'Team'), a.part('Bands', 'Steel'),
                                       a.part('Crown', 'Steel'), a.part('Bore', 'Undercarriage'))
    L = 3.9
    breech.box((0.8, 0.8, 0.8), bevel=0.12, **F((0, 0, 0)))
    breech.cyl(0.32, 0.3, seg=22, **F((0.5, 0, 0), ALONG_X))
    sleeve.cyl(0.19, L - 0.6, seg=22, **F((0.6 + (L - 0.6) / 2, 0, 0), ALONG_X))
    for x in (1.1, 1.65, 3.4):
        band.cyl(0.23, 0.1, seg=22, bevel=0.02, **F((x, 0, 0), ALONG_X))
    sleeve.cyl(0.19, 0.2, r2=0.36, seg=24, **F((2.15, 0, 0), ALONG_X))
    sleeve.cyl(0.36, 0.62, seg=24, bevel=0.04, **F((2.56, 0, 0), ALONG_X))
    sleeve.cyl(0.36, 0.2, r2=0.19, seg=24, **F((2.97, 0, 0), ALONG_X))
    for x in (2.3, 2.82):
        band.cyl(0.375, 0.07, seg=24, bevel=0.015, **F((x, 0, 0), ALONG_X))
    tip.cyl(0.24, 0.26, seg=22, bevel=0.04, **F((L + 0.11, 0, 0), ALONG_X))
    tip.box((0.26, 0.16, 0.16), bevel=0.03, **F((L - 0.2, 0, 0.28)))
    bore.cyl(0.12, 0.02, seg=16, bevel=0, **F((L + 0.245, 0, 0), ALONG_X))


def tungsten_penetrator(a):
    """Tungsten penetrator: the long APFSDS dart with its dark tungsten nose and swept fins, the three
    olive sabot petals peeling away and a red tracer in its tail."""
    F = Frame(rot=aim((0.42, 0.62, 0.66)))
    rod, tip, fins, sabot, tracer = (a.part('Rod', 'Steel'), a.part('Tungsten', 'Obsidian'), a.part('Fins', 'Steel'),
                                     a.part('Sabot', 'Team'), a.part('Tracer', 'LavaGlow'))
    rod.cyl(0.085, 2.7, seg=14, **F((-0.15, 0, 0), ALONG_X))
    tip.cyl(0.095, 0.55, seg=14, **F((1.45, 0, 0), ALONG_X))
    tip.cyl(0.095, 0.45, r2=0.012, seg=14, **F((1.95, 0, 0), ALONG_X))
    for k in range(6):
        t = k * TAU / 6 + 0.3
        rc = 0.22
        fins.box((0.62, 0.04, 0.28), taper=(0.45, 1), shift=(-0.14, 0), bevel=0.012,
                 **F((-1.2, -math.sin(t) * rc, math.cos(t) * rc), (t, 0, 0)))
    tracer.cyl(0.07, 0.12, seg=12, **F((-1.55, 0, 0), ALONG_X))
    for k in range(3):
        t0 = k * TAU / 3 + 0.12
        t1 = t0 + TAU / 3 - 0.24
        outer = [(math.cos(t0 + (t1 - t0) * i / 7) * 0.4, math.sin(t0 + (t1 - t0) * i / 7) * 0.4) for i in range(8)]
        inner = [(math.cos(t1 - (t1 - t0) * i / 4) * 0.1, math.sin(t1 - (t1 - t0) * i / 4) * 0.1) for i in range(5)]
        mid, off = (t0 + t1) / 2, 0.09
        sabot.prism(outer + inner, 1.15, axis='X', bevel=0.025, **F((0.05, math.cos(mid) * off, math.sin(mid) * off)))


def he_frag_filler(a):
    """HE-FRAG filler: an olive high-explosive shell with its yellow band, copper driving band, steel
    fuze and brass case, leaning to one side."""
    F = Frame(rot=aim((0.5, 0.45, 0.74)))
    case, body, band, drive, fuze = (a.part('Case', 'Gilded'), a.part('Shell', 'Team'), a.part('HEBand', 'SafetyStripe'),
                                     a.part('Drive', 'Copper'), a.part('Fuze', 'Steel'))

    def X(z):
        loc, rot = along_x(z)
        return F(loc, rot)
    case.lathe([(0.0, 0.0), (0.47, 0.0), (0.47, 0.09), (0.43, 0.12), (0.43, 1.02), (0.41, 1.06)], seg=28, **X(0))
    body.lathe([(0.41, 1.0), (0.43, 1.08), (0.43, 1.95), (0.4, 2.25), (0.32, 2.55), (0.21, 2.78), (0.13, 2.9)], seg=28, **X(0))
    drive.cyl(0.45, 0.1, seg=28, bevel=0.02, **X(1.2))
    band.cyl(0.44, 0.24, seg=28, bevel=0.02, **X(1.72))
    fuze.lathe([(0.13, 2.88), (0.145, 2.96), (0.1, 3.12), (0.0, 3.2)], seg=24, **X(0))


def proximity_fuze(a):
    """Proximity fuze: a shell nose fuze, threads below, olive body, ivory radome, its glowing antenna
    ring and the radio waves it sends ahead."""
    thread, body, nose, ring, waves = (a.part('Thread', 'Steel'), a.part('Body', 'Team'), a.part('Radome', 'Medical'),
                                       a.part('Antenna', 'Amber'), a.part('Waves', 'Amber'))
    thread.lathe([(0.44 if k % 2 == 0 else 0.5, k * 0.05) for k in range(8)], seg=28)
    body.lathe([(0.46, 0.34), (0.58, 0.38), (0.6, 0.44), (0.6, 0.66), (0.56, 0.92), (0.47, 1.2), (0.36, 1.46)], seg=28)
    nose.lathe([(0.36, 1.45), (0.31, 1.62), (0.22, 1.8), (0.1, 1.95), (0.0, 1.99)], seg=28)
    ring.torus(0.535, 0.055, loc=(0, 0, 1.06), seg=32, ring=8)
    tip = Vector((0, 0, 2.05))
    for r in (0.34, 0.6, 0.86):
        vtube(waves, arc3(tip, CAM_RIGHT, UP, r, math.radians(35), math.radians(145), 16), 0.05, seg=8)


def bunker_buster(a):
    """Bunker buster: a fat penetrator bomb, its hardened steel nose buried in a cracked concrete slab."""
    slab, crack, rubble = a.part('Slab', 'Concrete'), a.part('Cracks', 'Charred'), a.part('Rubble', 'Concrete')
    slab.box((2.0, 1.6, 0.4), loc=(0.35, -0.1, 0.2), bevel=0.06)
    impact = Vector((0.35, -0.15, 0.4))
    rng = random.Random(4)
    for k in range(6):
        t = k * TAU / 6 + rng.uniform(-0.3, 0.3)
        mid = impact + Vector((math.cos(t), math.sin(t), 0)) * rng.uniform(0.3, 0.4)
        end = mid + Vector((math.cos(t + 0.4), math.sin(t + 0.4), 0)) * rng.uniform(0.15, 0.3)
        for p, q in ((impact, mid), (mid, end)):
            crack.limb(p + Vector((0, 0, 0.005)), q + Vector((0, 0, 0.005)), 0.05, 0.05, bevel=0.0)
    for k in range(7):
        t = k * TAU / 7 + 0.4
        rubble.ico(rng.uniform(0.09, 0.15), loc=impact + Vector((math.cos(t) * 0.42, math.sin(t) * 0.42, 0.04)),
                   sub=1, jitter=0.35, seed=k * 1.7)
    # The bomb is built nose-first along local +X, the frame's origin at the buried nose tip.
    F = Frame(impact + Vector((0, 0, -0.3)), aim((-0.75, -0.1, 0.65)))
    nose, body, band, fins = a.part('Nose', 'Steel'), a.part('Bomb', 'Armor'), a.part('Band', 'SafetyStripe'), a.part('Fins', 'Armor')

    def X(z):
        loc, rot = along_x(z)
        return F(loc, rot)
    nose.lathe([(0.0, 0.0), (0.1, 0.06), (0.24, 0.25), (0.36, 0.5), (0.45, 0.8), (0.49, 0.96)], seg=28, **X(0))
    body.lathe([(0.49, 0.94), (0.52, 1.1), (0.52, 2.5), (0.48, 2.85), (0.38, 3.2), (0.3, 3.32)], seg=28, **X(0))
    band.cyl(0.53, 0.16, seg=28, bevel=0.02, **X(1.28))
    band.cyl(0.53, 0.08, seg=28, bevel=0.01, **X(1.52))
    for k in range(4):
        t = math.pi / 4 + k * R90
        rc = 0.58
        fins.box((0.7, 0.05, 0.46), taper=(0.6, 1), shift=(0.1, 0), bevel=0.015,
                 **F((3.05, -math.sin(t) * rc, math.cos(t) * rc), (t, 0, 0)))


def hypervelocity_charge(a):
    """Hypervelocity charge: a bottlenecked brass propellant cartridge, its mouth packed with glowing
    blue charge, blue bands round its body and blue streaks trailing it."""
    F = Frame(rot=aim((0.67, 0.44, 0.61)))
    case, glow, primer, streak = (a.part('Case', 'Gilded'), a.part('Charge', 'ChargeBlue'), a.part('Primer', 'Copper'),
                                  a.part('Streaks', 'ChargeBlue'))

    def X(z):
        loc, rot = along_x(z)
        return F(loc, rot)
    case.lathe([(0.0, 0.0), (0.52, 0.0), (0.52, 0.1), (0.44, 0.13), (0.44, 0.19), (0.5, 0.24), (0.47, 1.65), (0.42, 1.8),
                (0.3, 2.0), (0.29, 2.4), (0.25, 2.42)], seg=32, **X(0))
    glow.sphere((0.25, 0.25, 0.14), seg=20, rings=10, cut=0.0, **X(2.4))
    for z in (0.75, 1.2):
        glow.cyl(0.505, 0.13, seg=32, bevel=0.02, **X(z))
    primer.cyl(0.14, 0.02, seg=16, bevel=0, **X(-0.005))
    for k, t in enumerate((1.9, 3.3, 4.6)):
        off = Vector((0, math.cos(t), math.sin(t))) * 0.72
        pts = [F.p(Vector((x, 0, 0)) + off) for x in (-0.2, -0.75, -1.3)]
        vtube(streak, pts, [0.06, 0.045, 0.012], seg=8)


def heavy_barrel(a):
    """Heavy barrel: a thick artillery tube in its cradle, recuperators riding on top and a big
    double-baffle muzzle brake."""
    F = Frame(rot=aim((-0.8, -0.28, 0.53)))
    cradle, barrel, brake, bore, recup = (a.part('Cradle', 'Team'), a.part('Tube', 'Armor'), a.part('Brake', 'Steel'),
                                          a.part('Bore', 'Undercarriage'), a.part('Recuperators', 'Steel'))
    cradle.box((1.1, 1.05, 1.05), bevel=0.12, **F((0, 0, 0)))
    cradle.cyl(0.5, 0.4, seg=24, bevel=0.05, **F((0.7, 0, 0), ALONG_X))
    cradle.box((0.16, 0.8, 0.6), bevel=0.03, **F((1.55, 0, 0.36)))
    for y in (-0.27, 0.27):
        recup.cyl(0.14, 1.4, seg=14, bevel=0.03, **F((0.9, y, 0.64), ALONG_X))
        recup.cyl(0.17, 0.12, seg=14, **F((1.62, y, 0.64), ALONG_X))
    barrel.cyl(0.36, 2.0, seg=26, **F((1.85, 0, 0), ALONG_X))
    barrel.cyl(0.41, 0.3, seg=26, bevel=0.04, **F((2.8, 0, 0), ALONG_X))
    brake.box((0.9, 0.66, 0.78), bevel=0.07, **F((3.38, 0, 0)))
    for x in (3.14, 3.62):
        brake.box((0.18, 1.4, 0.92), bevel=0.05, **F((x, 0, 0)))
    brake.cyl(0.4, 0.1, seg=26, bevel=0.02, **F((3.85, 0, 0), ALONG_X))
    bore.cyl(0.21, 0.02, seg=18, bevel=0, **F((3.91, 0, 0), ALONG_X))


# ----------------------------------------------------------------------------- loader slot
def extended_ammo_rack(a):
    """Extended ammo rack: a long olive rack holding two rows of six rounds behind retaining rails."""
    tray, rail, case, tip_he, tip_ap = (a.part('Rack', 'Team'), a.part('Rails', 'Armor'), a.part('Cases', 'Gilded'),
                                        a.part('TipsHE', 'BarrelRed'), a.part('TipsAP', 'Steel'))
    tray.box((2.8, 1.05, 0.2), loc=(0, 0, 0.1), bevel=0.05)
    for x in (-1.42, 1.42):
        tray.box((0.14, 1.05, 1.05), loc=(x, 0, 0.52), bevel=0.04)
    for y in (-0.56, 0.56):
        rail.box((2.9, 0.08, 0.11), loc=(0, y, 0.74), bevel=0.02)
    for i in range(6):
        for j in range(2):
            x, y = -1.05 + i * 0.42, -0.23 + j * 0.46
            case.cyl(0.18, 0.95, loc=(x, y, 0.67), seg=16, bevel=0.02)
            (tip_he if j == 0 else tip_ap).cyl(0.18, 0.42, r2=0.04, loc=(x, y, 1.355), seg=16, bevel=0.01)


def belt_feed(a):
    """Belt feed: an open olive ammo can, a belt of linked brass rounds arching out over its lip."""
    can, latch, case, bullet, link = (a.part('Can', 'Team'), a.part('Latch', 'Steel'), a.part('Cases', 'Gilded'),
                                      a.part('Bullets', 'Copper'), a.part('Links', 'Undercarriage'))
    can.box((1.2, 0.72, 0.85), loc=(0, 0, 0.425), bevel=0.06)
    can.box((1.26, 0.78, 0.08), loc=(0, 0, 0.8), bevel=0.03)
    ang = -1.95
    hinge = Vector((0, 0.36, 0.86))
    y, z = -0.39, 0.04
    lid = hinge + Vector((0, y * math.cos(ang) - z * math.sin(ang), y * math.sin(ang) + z * math.cos(ang)))
    can.box((1.26, 0.78, 0.08), loc=lid, rot=(ang, 0, 0), bevel=0.03)
    latch.box((0.08, 0.3, 0.22), loc=(0.63, 0, 0.6), bevel=0.02)
    latch.tube([(-0.3, 0.44, 1.35), (-0.3, 0.52, 1.52), (0.3, 0.52, 1.52), (0.3, 0.44, 1.35)], 0.04, seg=8)
    path = catmull([(0.1, 0, 0.5), (0.25, 0, 0.95), (0.55, 0, 1.22), (0.9, 0, 1.22), (1.2, 0, 0.98),
                    (1.4, 0, 0.6), (1.52, 0, 0.24), (1.75, 0, 0.08), (2.15, 0, 0.07)], per=10)
    pts = resample(path, 0.135)
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        case.cyl(0.062, 0.3, loc=(p.x, 0.04, p.z), rot=ALONG_Y, seg=12, bevel=0.01)
        bullet.cyl(0.06, 0.16, r2=0.015, loc=(p.x, -0.19, p.z), rot=ALONG_Y, seg=12, bevel=0.005)
        beta = -math.atan2(t.z, t.x)
        for ly in (0.13, -0.05):
            link.box((0.15, 0.05, 0.1), loc=(p.x, ly, p.z), rot=(0, beta, 0), bevel=0.01)


def salvo_rack(a):
    """Salvo rack: a cylindrical rocket pod, seven red-nosed rockets ready in its tubes."""
    F = Frame((0, 0, 0.75), (-0.3, 0, 0.45))
    pod, ring, mouth, nose, lug = (a.part('Pod', 'Team'), a.part('Fairing', 'Steel'), a.part('Tubes', 'Undercarriage'),
                                   a.part('Rockets', 'BarrelRed'), a.part('Lugs', 'Armor'))
    pod.cyl(0.62, 1.7, seg=32, bevel=0.05, **F((0, 0.05, 0), ALONG_Y))
    pod.cyl(0.36, 0.4, r2=0.62, seg=32, bevel=0.04, **F((0, 1.1, 0), ALONG_Y))
    ring.cyl(0.66, 0.16, seg=32, bevel=0.04, **F((0, -0.78, 0), ALONG_Y))
    mouth.cyl(0.57, 0.02, seg=32, bevel=0, **F((0, -0.865, 0), ALONG_Y))
    for x, z in [(0, 0)] + [(0.37 * math.cos(k * TAU / 6), 0.37 * math.sin(k * TAU / 6)) for k in range(6)]:
        ring.torus(0.15, 0.028, seg=16, ring=6, **F((x, -0.875, z), (R90, 0, 0)))
        nose.cyl(0.125, 0.26, r2=0.02, seg=14, bevel=0.01, **F((x, -0.99, z), ALONG_Y))
    for y in (-0.35, 0.45):
        lug.box((0.22, 0.3, 0.26), bevel=0.04, **F((0, y, 0.68)))


def hair_trigger(a):
    """Hair trigger: the gunner's firing grip on its base with a big red button on top, a steel trigger,
    and the copper firing solenoid wired beside it."""
    base, grip, cap, collar, button, trig, coil, ends, wire = (
        a.part('Base', 'Armor'), a.part('Grip', 'Rubber'), a.part('Cap', 'Team'), a.part('Collar', 'Hazard'),
        a.part('Button', 'SignalRed'), a.part('Trigger', 'Steel'), a.part('Coil', 'Copper'), a.part('CoilEnds', 'Steel'),
        a.part('Wire', 'BarrelRed'))
    base.box((1.6, 1.1, 0.24), loc=(0, 0, 0.12), bevel=0.07)
    gx = -0.3
    grip.limb((gx, 0.08, 0.2), (gx, -0.04, 1.2), 0.4, 0.48, bevel=0.15, taper=(0.9, 0.85))
    cap.box((0.62, 0.64, 0.3), loc=(gx, -0.08, 1.33), rot=(0.18, 0, 0), bevel=0.1)
    collar.cyl(0.24, 0.07, loc=(gx, -0.11, 1.5), rot=(0.18, 0, 0), seg=24, bevel=0.02)
    button.cyl(0.18, 0.14, loc=(gx, -0.125, 1.57), rot=(0.18, 0, 0), seg=24, bevel=0.05)
    trig.limb((gx, -0.27, 1.05), (gx, -0.44, 0.92), 0.12, 0.1, bevel=0.03)
    trig.limb((gx, -0.44, 0.92), (gx, -0.36, 0.72), 0.12, 0.1, bevel=0.03)
    coil.cyl(0.22, 0.5, loc=(0.42, 0.1, 0.46), rot=ALONG_X, seg=22, bevel=0.03)
    for x in (0.14, 0.7):
        ends.cyl(0.25, 0.06, loc=(x, 0.1, 0.46), rot=ALONG_X, seg=22, bevel=0.015)
    ends.cyl(0.06, 0.3, loc=(0.85, 0.1, 0.46), rot=ALONG_X, seg=10)
    ends.box((0.6, 0.4, 0.1), loc=(0.42, 0.1, 0.27), bevel=0.02)
    wire.tube([(0.14, 0.2, 0.62), (0.0, 0.32, 0.72), (gx + 0.1, 0.3, 0.6), (gx + 0.1, 0.25, 0.4)], 0.04, seg=8)


# ----------------------------------------------------------------------------- armour slot
def composite_addon(a):
    """Composite add-on: a thick sloped module, its cut side showing the steel, ceramic and rubber
    layers, bolted on through its olive face."""
    F = Frame((0, 0, 0), (-0.38, 0, -0.42))
    layers = (('Team', 0.3), ('Concrete', 0.26), ('Rubber', 0.13), ('Concrete', 0.26), ('Steel', 0.2), ('Team', 0.25))
    depth = sum(th for _, th in layers)
    y = -depth / 2
    for i, (mat, th) in enumerate(layers):
        a.part(f'Layer{i}', mat).box((1.5, th, 1.3), bevel=0.035, **F((0, y + th / 2, 0.65)))
        y += th
    bolts, washers, lugs = a.part('Bolts', 'Steel'), a.part('Washers', 'Armor'), a.part('Lugs', 'Steel')
    for x in (-0.45, 0.45):
        for z in (0.3, 1.0):
            washers.cyl(0.16, 0.04, seg=16, bevel=0.01, **F((x, -depth / 2 - 0.015, z), (R90, 0, 0)))
            bolts.cyl(0.11, 0.1, seg=6, bevel=0.015, **F((x, -depth / 2 - 0.06, z), (R90, 0, 0)))
    for x in (-0.45, 0.45):
        lugs.torus(0.13, 0.045, seg=16, ring=6, **F((x, 0, 1.38), (R90, 0, R90)))


def spall_liner(a):
    """Spall liner: a quilted yellow kevlar panel, diamond-stitched, with a darker piped edge."""
    F = Frame((0, 0, 0.9), (-0.35, 0, 0.3))
    back, quilt, edge = a.part('Backing', 'Kevlar'), a.part('Quilt', 'Kevlar'), a.part('Piping', 'AdobeTrim')
    back.box((2.0, 0.1, 1.5), bevel=0.04, **F((0, 0.06, 0)))
    s = 0.24
    for i in range(-3, 4):
        for j in range(-2, 3):
            if (i + j) % 2:
                continue
            quilt.box((0.31, 0.15, 0.31), bevel=0.08, **F((i * s, -0.02, j * s), (0, math.pi / 4, 0)))
    corners = [(-1.0, 0.02, -0.75), (1.0, 0.02, -0.75), (1.0, 0.02, 0.75), (-1.0, 0.02, 0.75), (-1.0, 0.02, -0.75)]
    vtube(edge, [F.p(c) for c in corners], 0.075, seg=8)


def applique_steel(a):
    """Applique steel: a bare riveted steel plate bent round a hull corner, a weld bead down the bend."""
    plate, rivet, weld = a.part('Plate', 'MetalSheet'), a.part('Rivets', 'Steel'), a.part('Weld', 'Rust')
    W, D, H, T = 1.9, 1.1, 1.45, 0.16
    plate.box((W, T, H), loc=(0, 0, H / 2), bevel=0.04)
    plate.box((T, D, H), loc=(W / 2 - T / 2, T / 2 + D / 2 - 0.001, H / 2), bevel=0.04)
    front = [(x, z) for x in (-0.8, -0.4, 0.0, 0.4) for z in (0.14, H - 0.14)] + [(-0.8, 0.5), (-0.8, 0.95)]
    front += [(x, H / 2) for x in (-0.4, 0.0, 0.4)]
    for x, z in front:
        rivet.sphere(0.065, loc=(x, -T / 2, z), rot=(R90, 0, 0), seg=10, rings=6, cut=0.0)
    for yy in (0.3, 0.65, 1.0):
        for z in (0.14, H / 2, H - 0.14):
            rivet.sphere(0.065, loc=(W / 2, yy, z), rot=(0, R90, 0), seg=10, rings=6, cut=0.0)
    weld.tube([(W / 2 + 0.005, -T / 2 - 0.005, 0.06), (W / 2 + 0.005, -T / 2 - 0.005, H - 0.06)], 0.045, seg=8)


def fire_retardant_hull(a):
    """Fire-retardant hull: a red halon bottle strapped into a hull corner, its pipe feeding a nozzle
    that sprays white suppressant."""
    hull, bottle, label, strap, valve, pipe, mist = (a.part('Hull', 'Team'), a.part('Bottle', 'BarrelRed'),
                                                     a.part('Label', 'PlasterWhite'), a.part('Straps', 'Steel'),
                                                     a.part('Valve', 'Steel'), a.part('Pipe', 'Pipe'), a.part('Mist', 'Snow'))
    hull.box((2.3, 1.5, 0.16), loc=(0, 0, 0.08), bevel=0.04)
    hull.box((2.3, 0.16, 1.3), loc=(0, 0.67, 0.65), bevel=0.04)
    r, cy, cz = 0.4, 0.2, 0.57
    bottle.lathe([(0.0, 0.0), (0.24, 0.02), (0.35, 0.1), (r, 0.28), (r, 1.25), (0.35, 1.42), (0.24, 1.5), (0.0, 1.52)],
                 loc=(-1.0, cy, cz), rot=ALONG_X, seg=28)
    label.cyl(r + 0.005, 0.1, loc=(-0.1, cy, cz), rot=ALONG_X, seg=28, bevel=0.01)
    for x in (-0.6, 0.2):
        strap.cyl(r + 0.02, 0.08, loc=(x, cy, cz), rot=ALONG_X, seg=28, bevel=0.01)
        strap.box((0.1, 0.9, 0.06), loc=(x, cy, 0.19), bevel=0.01)
    valve.cyl(0.12, 0.2, loc=(0.6, cy, cz), rot=ALONG_X, seg=14)
    valve.box((0.22, 0.24, 0.24), loc=(0.78, cy, cz), bevel=0.03)
    valve.torus(0.15, 0.035, loc=(0.78, cy, cz + 0.24), seg=16, ring=6)
    valve.cyl(0.03, 0.14, loc=(0.78, cy, cz + 0.17), seg=8)
    pipe.tube([(0.89, cy, cz), (1.02, cy, cz), (1.02, 0.42, cz), (1.02, 0.42, 0.74)], 0.055, seg=10)
    valve.cyl(0.07, 0.2, r2=0.11, loc=(1.02, 0.42, 0.82), seg=12)
    for k, (p, r) in enumerate((((1.02, 0.4, 1.0), 0.1), ((0.94, 0.34, 1.2), 0.15), ((1.13, 0.37, 1.26), 0.13),
                                ((1.0, 0.28, 1.44), 0.19), ((1.2, 0.32, 1.5), 0.17), ((1.06, 0.26, 1.68), 0.15))):
        mist.ico(r, loc=p, sub=2, jitter=0.15, seed=k + 1.0)


def armoured_tub(a):
    """Armoured tub: a titanium bathtub of armour round a pilot's seat, rivets along its rim."""
    tub, seat, stick, knob, rivet = (a.part('Tub', 'Titanium'), a.part('Seat', 'Suit'), a.part('Stick', 'Rubber'),
                                     a.part('Knob', 'BarrelRed'), a.part('Rivets', 'Steel'))
    outline = fk.chamfered(1.6, 2.0, 0.42)
    H, taper = 1.05, 1.12
    tub.shell(outline, H, 0.15, taper=taper, floor=0.15, bevel=0.03)
    seat.box((0.66, 0.66, 0.16), loc=(0, 0.25, 0.42), bevel=0.05)
    seat.box((0.66, 0.16, 0.9), loc=(0, 0.64, 0.86), rot=(-0.22, 0, 0), bevel=0.06)
    seat.box((0.42, 0.14, 0.24), loc=(0, 0.76, 1.42), rot=(-0.22, 0, 0), bevel=0.05)
    stick.limb((0, -0.3, 0.2), (0, -0.36, 0.8), 0.08, 0.08, bevel=0.02)
    knob.sphere(0.08, loc=(0, -0.36, 0.84), seg=12, rings=8)
    z = H - 0.14
    k = 1 + (taper - 1) * z / H
    pts = [Vector((x * k, y * k, z)) for x, y in outline]
    for p, q in zip(pts, pts[1:] + pts[:1]):
        n = Vector((q.y - p.y, -(q.x - p.x), 0)).normalized()  # outward for a counter-clockwise outline
        steps = max(1, int((q - p).length / 0.3))
        for i in range(steps):
            c = p + (q - p) * ((i + 0.5) / steps)
            rivet.sphere(0.05, loc=c + n * 0.005, rot=rot_to(n), seg=8, rings=5, cut=0.0)


def monolith_plate(a):
    """Monolith plate: a huge, thick armour slab standing on end, lifting eyes on top, bolted face
    panels and a yellow-and-black hazard band round its foot."""
    F = Frame((0, 0, 0), (-0.06, 0, 0.1))
    slab, face, bolts, eyes, yellow, black = (a.part('Slab', 'Armor'), a.part('Face', 'Team'), a.part('Bolts', 'Steel'),
                                              a.part('Eyes', 'Steel'), a.part('Stripe', 'SafetyStripe'),
                                              a.part('StripeDark', 'Charred'))
    W, D, H = 1.5, 0.85, 2.3
    slab.box((W, D, H), bevel=0.14, **F((0, 0, H / 2)))
    face.box((1.24, 0.06, 1.75), bevel=0.04, **F((0, -D / 2 - 0.01, 1.3)))
    face.box((0.06, 0.6, 1.75), bevel=0.04, **F((W / 2 + 0.01, 0, 1.3)))
    for x in (-0.5, 0.5):
        for z in (0.55, 2.05):
            bolts.cyl(0.085, 0.08, seg=6, bevel=0.012, **F((x, -D / 2 - 0.05, z), (R90, 0, 0)))
        eyes.torus(0.16, 0.055, seg=18, ring=8, **F((x * 0.9, 0, H + 0.12), (R90, 0, 0)))
        eyes.box((0.2, 0.2, 0.08), bevel=0.02, **F((x * 0.9, 0, H + 0.02)))
    n = 6
    for i in range(n):
        part = yellow if i % 2 == 0 else black
        part.box((W / n, 0.04, 0.26), bevel=0.0, **F((-W / 2 + (i + 0.5) * W / n, -D / 2 - 0.005, 0.2)))
    for i in range(4):
        part = black if i % 2 == 0 else yellow
        part.box((0.04, D / 4, 0.26), bevel=0.0, **F((W / 2 + 0.005, -D / 2 + (i + 0.5) * D / 4, 0.2)))


def frontal_wedge(a):
    """Frontal wedge: a pointed wedge of add-on armour, its two sloped faces bolted on and a steel
    ridge along the prow."""
    wedge, ridge, bolts, mount = a.part('Wedge', 'Team'), a.part('Ridge', 'Armor'), a.part('Bolts', 'Steel'), a.part('Mount', 'Armor')
    base = [(0, -1.25), (1.1, -0.1), (1.1, 0.55), (-1.1, 0.55), (-1.1, -0.1)]
    top = [(x * 0.55, y * 0.55 + 0.35) for x, y in base]
    h = 0.95
    wedge.loft([[(x, y, 0) for x, y in base], [(x, y, h) for x, y in top]], bevel=0.05)
    ridge.limb((0, -1.25, 0.02), (0, top[0][1], h), 0.13, 0.13, bevel=0.03)
    for s in (1, -1):
        p00, p10 = Vector((0, -1.25, 0)), Vector((s * 1.1, -0.1, 0))
        p01, p11 = Vector((0, top[0][1], h)), Vector((s * top[1][0], top[1][1], h))
        n = (p10 - p00).cross(p01 - p00).normalized()
        if n.y > 0:
            n = -n
        for u, v in ((0.35, 0.3), (0.72, 0.3), (0.5, 0.68)):
            p = p00.lerp(p10, u).lerp(p01.lerp(p11, u), v)
            bolts.cyl(0.075, 0.07, loc=p + n * 0.02, rot=rot_to(n), seg=6, bevel=0.01)
    mount.box((2.3, 0.14, 0.7), loc=(0, 0.66, 0.38), bevel=0.04)


def slat_cage(a):
    """Slat cage: bar armour, a steel frame of posts and rails carrying thick olive slats."""
    F = Frame((0, 0, 0), (0, 0, -0.2))
    frame, slat, bracket = a.part('Frame', 'Armor'), a.part('Slats', 'Team'), a.part('Brackets', 'Steel')
    for x in (-1.2, 0.0, 1.2):
        frame.box((0.14, 0.14, 1.75), bevel=0.03, **F((x, 0.05, 0.875)))
        bracket.box((0.1, 0.5, 0.1), bevel=0.02, **F((x, 0.35, 1.45)))
        bracket.box((0.1, 0.5, 0.1), bevel=0.02, **F((x, 0.35, 0.35)))
    for z in (0.07, 1.68):
        frame.box((2.54, 0.14, 0.14), bevel=0.03, **F((0, 0.05, z)))
    for k in range(5):
        slat.box((2.5, 0.24, 0.13), bevel=0.03, **F((0, -0.08, 0.36 + k * 0.26)))


def overhead_screen(a):
    """Overhead screen: a cope cage, a steel roof grid on slanted posts sheltering a turret."""
    turret, gun, post, frame, grid = (a.part('Hull', 'Armor'), a.part('Gun', 'Armor'), a.part('Posts', 'Steel'),
                                      a.part('Frame', 'Team'), a.part('Grid', 'Steel'))
    turret.prism(fk.chamfered(1.4, 1.6, 0.42), 0.5, loc=(0, 0.05, 0.25), axis='Z', taper=0.82, bevel=0.05)
    turret.cyl(0.16, 0.12, loc=(0.35, 0.35, 0.55), seg=14)
    gun.cyl(0.1, 1.1, loc=(0, -1.0, 0.3), rot=ALONG_Y, seg=14)
    gun.box((0.42, 0.25, 0.3), loc=(0, -0.72, 0.28), bevel=0.05)
    top = 1.35
    hx, hy = 0.95, 1.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            post.limb((sx * 0.5, sy * 0.55 + 0.05, 0.45), (sx * hx, sy * hy, top), 0.07, 0.07, bevel=0.015)
    corners = [(-hx, -hy, top), (hx, -hy, top), (hx, hy, top), (-hx, hy, top), (-hx, -hy, top)]
    frame.tube(corners, 0.06, seg=8)
    for i in range(1, 5):
        x = -hx + i * 2 * hx / 5
        grid.box((0.05, 2 * hy, 0.05), loc=(x, 0, top), bevel=0.0)
        y = -hy + i * 2 * hy / 5
        grid.box((2 * hx, 0.05, 0.05), loc=(0, y, top + 0.03), bevel=0.0)


def mine_rollers(a):
    """Mine rollers: two banks of heavy toothed roller wheels on push arms from a mounting beam."""
    disc, teeth, hub, arm, beam = (a.part('Discs', 'Armor'), a.part('Teeth', 'Steel'), a.part('Hubs', 'Steel'),
                                   a.part('Arms', 'Team'), a.part('Beam', 'Team'))
    R = 0.44
    for xb in (-0.8, 0.8):
        c = Vector((xb, -0.85, R))
        hub.cyl(0.1, 0.95, loc=c, rot=ALONG_X, seg=12)
        for i in range(4):
            x = xb - 0.33 + i * 0.22
            disc.cyl(R, 0.13, loc=(x, c.y, c.z), rot=ALONG_X, seg=24, bevel=0.03)
            for k in range(10):
                t = k * TAU / 10 + i * 0.3
                teeth.box((0.1, 0.1, 0.1), loc=(x, c.y + math.cos(t) * (R + 0.03), c.z + math.sin(t) * (R + 0.03)),
                          rot=(t, 0, 0), bevel=0.015)
        for s in (-1, 1):
            side = xb + s * 0.5
            arm.box((0.08, 0.36, 0.36), loc=(side, c.y, c.z), bevel=0.03)
            arm.limb((side, c.y + 0.05, c.z + 0.05), (xb * 0.75 + s * 0.3, 0.55, 0.78), 0.14, 0.14, bevel=0.03)
    beam.box((2.4, 0.26, 0.26), loc=(0, 0.6, 0.8), bevel=0.05)
    for x in (-1.0, 1.0):
        hub.box((0.2, 0.3, 0.4), loc=(x, 0.78, 0.8), bevel=0.04)


# ----------------------------------------------------------------------------- engine slot
def _volute(shape, F, y, r0, r1, R0, flip=1, turns=0.9, steps=34, seg=14):
    """Snail housing: a spiral tube growing from r0 to r1 round a hub, ending in a straight outlet
    that leaves upwards. Returns the outlet end and its direction."""
    span = turns * TAU
    pts, radii = [], []
    for i in range(steps + 1):
        f = i / steps
        t = -span * (1 - f)
        r = r0 + (r1 - r0) * f
        R = R0 + r * 0.7
        pts.append(Vector((flip * R * math.cos(t), y, R * math.sin(t))))
        radii.append(r)
    d = (pts[-1] - pts[-2]).normalized()
    for k in (1, 2):
        pts.append(pts[-1] + d * 0.22)
        radii.append(r1)
    vtube(shape, [F.p(p) for p in pts], radii, seg=seg)
    return F.p(pts[-1]), F.v(d)


def turbocharger(a):
    """Turbocharger: the aluminium compressor snail and the hot iron turbine snail back to back on the
    bearing housing, the compressor inlet facing out."""
    F = Frame((0, 0, 0.95), (0, 0, 0.5))
    comp, turb, bear, dark, flange, oil = (a.part('Compressor', 'Steel'), a.part('Turbine', 'Rust'), a.part('Bearing', 'Armor'),
                                           a.part('Inlet', 'Undercarriage'), a.part('Flanges', 'Armor'), a.part('Oil', 'Pipe'))
    comp.cyl(0.5, 0.36, seg=32, bevel=0.06, **F((0, -0.36, 0), ALONG_Y))
    end, d = _volute(comp, F, -0.36, 0.08, 0.27, 0.42)
    flange.cyl(0.33, 0.07, seg=22, bevel=0.015, loc=end, rot=rot_to(d))
    comp.cyl(0.3, 0.34, r2=0.34, seg=28, bevel=0.03, **F((0, -0.72, 0), ALONG_Y))
    dark.cyl(0.25, 0.02, seg=28, bevel=0, **F((0, -0.895, 0), ALONG_Y))
    comp.cyl(0.07, 0.12, r2=0.02, seg=10, **F((0, -0.86, 0), ALONG_Y))
    bear.cyl(0.27, 0.36, seg=24, bevel=0.04, **F((0, 0.02, 0), ALONG_Y))
    oil.tube([F.p((0, 0.02, 0.26)), F.p((0, 0.02, 0.55)), F.p((0.3, 0.1, 0.75))], 0.045, seg=8)
    turb.cyl(0.48, 0.36, seg=32, bevel=0.06, **F((0, 0.4, 0), ALONG_Y))
    end, d = _volute(turb, F, 0.4, 0.08, 0.25, 0.4, flip=-1)
    flange.cyl(0.31, 0.07, seg=22, bevel=0.015, loc=end, rot=rot_to(d))
    turb.cyl(0.3, 0.3, seg=24, bevel=0.03, **F((0, 0.72, 0), ALONG_Y))
    flange.cyl(0.36, 0.06, seg=24, bevel=0.015, **F((0, 0.88, 0), ALONG_Y))


def turret_drive(a):
    """Turret drive: the turret ring's internal gear on its bearing race, the traverse motor driving it
    through a brass pinion, and the red hand wheel for manual traverse."""
    ring, race, bolts, pinion, gbox, motor, fins, wheel, cable = (
        a.part('Ring', 'Steel'), a.part('Race', 'Armor'), a.part('Bolts', 'Steel'), a.part('Pinion', 'Gilded'),
        a.part('Reduction', 'Armor'), a.part('Motor', 'Team'), a.part('MotorFins', 'Team'), a.part('Handwheel', 'BarrelRed'),
        a.part('Cable', 'Rubber'))
    ring_gear(ring, 1.2, 1.0, 0.9, 40, 0.2, loc=(0, 0, 0.3))
    ring_gear(race, 1.4, 1.17, 1.17, 30, 0.16, loc=(0, 0, 0.12))
    for k in range(18):
        t = k * TAU / 18
        bolts.cyl(0.04, 0.05, loc=(1.29 * math.cos(t), 1.29 * math.sin(t), 0.215), seg=6, bevel=0.008)
    c = Vector((0, -0.72, 0))
    spur(pinion, 0.23, 10, 0.2, loc=(c.x, c.y, 0.3))
    gbox.box((0.52, 0.52, 0.36), loc=(c.x, c.y, 0.6), bevel=0.06)
    motor.cyl(0.26, 0.7, loc=(c.x, c.y, 1.12), seg=24, bevel=0.05)
    for z in (0.95, 1.08, 1.21, 1.34):
        fins.cyl(0.3, 0.04, loc=(c.x, c.y, z), seg=24, bevel=0.01)
    bolts.cyl(0.18, 0.08, loc=(c.x, c.y, 1.5), seg=20, bevel=0.02)
    w = Vector((c.x + 0.42, c.y, 0.62))
    wheel.torus(0.24, 0.04, loc=w, rot=(0, R90, 0), seg=24, ring=8)
    for k in range(3):
        t = k * TAU / 3
        wheel.limb(w, w + Vector((0, math.cos(t) * 0.24, math.sin(t) * 0.24)), 0.04, 0.04, bevel=0.01)
    bolts.cyl(0.05, 0.16, loc=(w.x - 0.1, w.y, w.z), rot=ALONG_X, seg=10)
    wheel.cyl(0.035, 0.16, loc=(w.x + 0.08, w.y + 0.18, w.z + 0.1), rot=ALONG_X, seg=8)
    cable.tube([(c.x, c.y + 0.1, 1.55), (c.x, c.y + 0.3, 1.7), (c.x, 0.1, 1.5), (0.0, 0.3, 0.45)], 0.045, seg=8)


def transit_gearbox(a):
    """Transit gearbox: a ribbed housing with three meshing gears, one brass, turning on its face and
    the output flange on its side."""
    F = Frame((0, 0, 0), (0, 0, 0.3))
    house, gear_s, gear_b, hub, holes, flange = (a.part('Housing', 'Armor'), a.part('Gears', 'Steel'), a.part('BrassGear', 'Gilded'),
                                                 a.part('Hubs', 'Undercarriage'), a.part('Holes', 'Undercarriage'),
                                                 a.part('Flange', 'Steel'))
    house.box((1.9, 0.9, 1.5), bevel=0.1, **F((0, 0.15, 0.75)))
    for x in (-0.6, 0.0, 0.6):
        house.box((0.1, 1.0, 0.12), bevel=0.02, **F((x, 0.15, 1.52)))
    y = -0.38
    g1, g2 = Vector((-0.42, y, 0.68)), None
    r1, r2, r3 = 0.6, 0.41, 0.29
    g2 = g1 + Vector((0.9 * math.cos(math.radians(-5)), 0, 0.9 * math.sin(math.radians(-5))))
    g3 = g2 + Vector((0, 0, 0.63))
    spur(gear_s, r1, 22, 0.14, **F(g1, (R90, 0, 0)))
    spur(gear_b, r2, 15, 0.14, phase=0.1, **F(g2, (R90, 0, 0)))
    spur(gear_s, r3, 11, 0.14, phase=0.15, **F(g3, (R90, 0, 0)))
    for g, r in ((g1, r1), (g2, r2), (g3, r3)):
        hub.cyl(r * 0.24, 0.2, seg=16, **F(g + Vector((0, -0.04, 0)), (R90, 0, 0)))
    for k in range(4):
        t = k * TAU / 4 + 0.4
        holes.cyl(0.1, 0.02, seg=14, bevel=0, **F(g1 + Vector((math.cos(t) * 0.33, -0.075, math.sin(t) * 0.33)), (R90, 0, 0)))
    flange.cyl(0.32, 0.14, seg=24, bevel=0.03, **F((1.02, 0.15, 0.7), ALONG_X))
    flange.cyl(0.14, 0.3, seg=16, **F((1.2, 0.15, 0.7), ALONG_X))
    for k in range(6):
        t = k * TAU / 6
        hub.cyl(0.035, 0.05, seg=6, **F((1.1, 0.15 + math.cos(t) * 0.24, 0.7 + math.sin(t) * 0.24), ALONG_X))


def overtuned_engine(a):
    """Overtuned engine: an inline block with a red rocker cover, a chrome blower and black scoop on top,
    and four exhaust stacks spitting fire."""
    block, pan, cover, blower, scoop, pipe, hot, flame, pulley = (
        a.part('Block', 'Armor'), a.part('Pan', 'Undercarriage'), a.part('Cover', 'BarrelRed'), a.part('Blower', 'Steel'),
        a.part('Scoop', 'Charred'), a.part('Stacks', 'Steel'), a.part('Hot', 'LavaGlow'), a.part('Flames', 'FlameOrange'),
        a.part('Pulley', 'Undercarriage'))
    core = a.part('FlameCore', 'Flare')
    pan.box((1.6, 0.7, 0.22), loc=(0, 0, 0.11), bevel=0.05)
    block.box((1.8, 0.85, 0.78), loc=(0, 0, 0.6), bevel=0.08)
    cover.box((1.7, 0.62, 0.24), loc=(0, 0.02, 1.1), bevel=0.08)
    blower.box((1.0, 0.52, 0.42), loc=(0, 0.02, 1.42), bevel=0.15)
    for x in (-0.36, -0.12, 0.12, 0.36):
        blower.box((0.05, 0.56, 0.3), loc=(x, 0.02, 1.42), bevel=0.01)
    scoop.box((0.72, 0.6, 0.26), loc=(0, 0.0, 1.76), taper=(0.9, 0.85), bevel=0.06)
    pulley.cyl(0.24, 0.1, loc=(0.96, 0, 0.55), rot=ALONG_X, seg=22, bevel=0.02)
    pulley.cyl(0.16, 0.1, loc=(0.96, 0, 1.2), rot=ALONG_X, seg=20, bevel=0.02)
    for i, x in enumerate((-0.6, -0.2, 0.2, 0.6)):
        top = 1.5 + (0.08 if i % 2 else 0.0)
        pipe.tube([(x, -0.4, 0.62), (x, -0.62, 0.62), (x, -0.74, 0.82), (x, -0.76, top)], 0.075, seg=10)
        hot.cyl(0.09, 0.12, loc=(x, -0.76, top + 0.04), seg=14)
        flame.lathe([(0.0, 0.0), (0.11, 0.04), (0.15, 0.14), (0.13, 0.28), (0.08, 0.44), (0.0, 0.6 + 0.08 * (i % 2))],
                    loc=(x, -0.76, top + 0.06), seg=12)
        core.lathe([(0.0, 0.0), (0.07, 0.04), (0.09, 0.12), (0.06, 0.24), (0.0, 0.36)], loc=(x, -0.79, top + 0.06), seg=10)


# ----------------------------------------------------------------------------- repair slot
def crew_drills(a):
    """Crew drills: a clipboard of ticked drill cards and a stopwatch standing against it."""
    F = Frame((0, 0, 0), (0, 0, -0.35))
    board, paper, ink, tick, clip = (a.part('Board', 'Wood'), a.part('Paper', 'PlasterWhite'), a.part('Ink', 'Charred'),
                                     a.part('Ticks', 'SignalGreen'), a.part('Clip', 'Steel'))
    board.box((1.35, 1.8, 0.07), bevel=0.03, **F((-0.25, 0.1, 0.035)))
    paper.box((1.18, 1.5, 0.02), bevel=0.005, **F((-0.25, 0.02, 0.08)))
    for k in range(5):
        y = 0.55 - k * 0.28
        ink.box((0.6, 0.05, 0.012), bevel=0, **F((-0.08, y, 0.095)))
        ink.box((0.13, 0.13, 0.012), bevel=0, **F((-0.62, y, 0.095)))
        if k < 4:
            p0, p1, p2 = F.p((-0.67, y + 0.02, 0.11)), F.p((-0.62, y - 0.05, 0.11)), F.p((-0.52, y + 0.1, 0.11))
            tick.limb(p0, p1, 0.04, 0.04, bevel=0.0)
            tick.limb(p1, p2, 0.04, 0.04, bevel=0.0)
    clip.box((0.62, 0.22, 0.12), bevel=0.03, **F((-0.25, 0.9, 0.12)))
    clip.torus(0.08, 0.025, seg=12, ring=6, **F((-0.25, 1.0, 0.2), (R90, 0, 0)))
    S = Frame((0.5, -0.5, 0.6), facing(Vector((0.55, -1.0, 0.45))))
    body, face, marks, hand, crown, push = (a.part('Watch', 'Steel'), a.part('Dial', 'PlasterWhite'), a.part('Marks', 'Charred'),
                                            a.part('Hand', 'BarrelRed'), a.part('Crown', 'Steel'), a.part('Pusher', 'BarrelRed'))
    body.cyl(0.52, 0.2, seg=32, bevel=0.06, **S())
    face.cyl(0.43, 0.02, seg=32, bevel=0, **S((0, 0, 0.105)))
    for k in range(12):
        t = k * TAU / 12
        marks.box((0.035, 0.1 if k % 3 == 0 else 0.06, 0.012), bevel=0, **S((math.cos(t) * 0.35, math.sin(t) * 0.35, 0.118), (0, 0, t - R90)))
    t = math.radians(40)
    hand.box((0.04, 0.34, 0.014), bevel=0, **S((math.cos(t) * 0.14, math.sin(t) * 0.14, 0.125), (0, 0, t - R90)))
    marks.cyl(0.04, 0.02, seg=10, bevel=0, **S((0, 0, 0.13)))
    crown.cyl(0.07, 0.14, seg=12, **S((0, 0.58, 0), (-R90, 0, 0)))
    push.cyl(0.1, 0.07, seg=14, **S((0, 0.67, 0), (-R90, 0, 0)))
    crown.torus(0.1, 0.028, seg=14, ring=6, **S((0, 0.78, 0), (0, R90, 0)))
    crown.cyl(0.05, 0.1, seg=10, **S((0.4, 0.4, 0), (-R90, 0, -math.pi / 4)))


def fire_extinguisher(a):
    """Fire extinguisher: a red hand extinguisher with its white label, steel valve and levers, gauge
    and black hose and horn."""
    F = Frame((0, 0, 0), (0.0, 0.14, 0.2))
    body, label, steel, lever, gauge, hose, horn = (a.part('Body', 'BarrelRed'), a.part('Label', 'PlasterWhite'),
                                                    a.part('Valve', 'Steel'), a.part('Levers', 'Undercarriage'),
                                                    a.part('Gauge', 'PlasterWhite'), a.part('Hose', 'Rubber'),
                                                    a.part('Horn', 'Undercarriage'))
    body.lathe([(0.0, 0.0), (0.37, 0.0), (0.42, 0.06), (0.42, 1.55), (0.39, 1.72), (0.29, 1.85), (0.14, 1.93), (0.0, 1.94)],
               seg=28, **F())
    label.cyl(0.425, 0.42, seg=28, bevel=0.01, **F((0, 0, 0.8)))
    steel.cyl(0.13, 0.2, seg=16, **F((0, 0, 2.0)))
    steel.box((0.3, 0.24, 0.22), bevel=0.04, **F((0, 0, 2.18)))
    lever.limb(F.p((-0.08, 0, 2.3)), F.p((0.5, 0, 2.42)), 0.12, 0.06, bevel=0.02)
    lever.limb(F.p((-0.02, 0, 2.1)), F.p((0.48, 0, 1.98)), 0.12, 0.06, bevel=0.02)
    gauge.cyl(0.09, 0.04, seg=16, **F((0.0, -0.14, 2.2), (R90, 0, 0)))
    steel.torus(0.095, 0.02, seg=16, ring=6, **F((0.0, -0.16, 2.2), (R90, 0, 0)))
    hose.tube([F.p(p) for p in ((-0.1, -0.1, 2.18), (-0.3, -0.35, 2.1), (-0.5, -0.45, 1.8), (-0.55, -0.45, 1.1),
                                (-0.5, -0.4, 0.7))], 0.055, seg=10)
    horn.cyl(0.07, 0.4, r2=0.13, seg=14, **F((-0.48, -0.38, 0.5), (0.0, 0.08, 0)))


# ----------------------------------------------------------------------------- optics slot
def laser_rangefinder(a):
    """Laser rangefinder: an olive rangefinder box, its big teal receiver lens beside the red emitter
    firing its beam, a rubber eyepiece at the back."""
    body, bezel, lens, emitter, beam, eye, steel = (a.part('Body', 'Team'), a.part('Bezel', 'Armor'), a.part('Lens', 'LensTeal'),
                                                    a.part('Emitter', 'SignalRed'), a.part('Beam', 'SignalRed'),
                                                    a.part('Eyepiece', 'Rubber'), a.part('Trim', 'Steel'))
    body.box((1.2, 1.5, 0.8), loc=(0, 0, 0.45), bevel=0.1)
    bezel.box((1.24, 0.14, 0.86), loc=(0, -0.78, 0.45), bevel=0.05)
    lens.cyl(0.29, 0.06, loc=(-0.22, -0.86, 0.46), rot=ALONG_Y, seg=28, bevel=0.02)
    steel.torus(0.31, 0.045, loc=(-0.22, -0.87, 0.46), rot=(R90, 0, 0), seg=28, ring=8)
    emitter.cyl(0.13, 0.06, loc=(0.33, -0.86, 0.52), rot=ALONG_Y, seg=20, bevel=0.02)
    steel.torus(0.15, 0.035, loc=(0.33, -0.87, 0.52), rot=(R90, 0, 0), seg=20, ring=6)
    beam.cyl(0.04, 1.3, loc=(0.33, -1.53, 0.52), rot=ALONG_Y, seg=10, bevel=0)
    eye.cyl(0.2, 0.3, loc=(0, 0.85, 0.5), rot=ALONG_Y, seg=20, bevel=0.05)
    steel.tube([(-0.35, -0.3, 0.85), (-0.35, -0.3, 1.05), (0.35, -0.3, 1.05), (0.35, -0.3, 0.85)], 0.05, seg=8)
    emitter.box((0.12, 0.12, 0.05), loc=(0.35, 0.35, 0.87), bevel=0.02)


def gun_stabiliser(a):
    """Gun stabiliser: a gimballed gyroscope, its spinning rotor rimmed in glowing teal inside brass
    and steel gimbal rings on a pedestal."""
    base, post, outer, inner, rotor, rim, axle = (a.part('Base', 'Armor'), a.part('Post', 'Steel'), a.part('Outer', 'Steel'),
                                                  a.part('Inner', 'Gilded'), a.part('Rotor', 'Team'), a.part('Rim', 'LensTeal'),
                                                  a.part('Axle', 'Steel'))
    base.cyl(0.62, 0.2, loc=(0, 0, 0.1), seg=32, bevel=0.05)
    base.cyl(0.3, 0.12, loc=(0, 0, 0.26), seg=24, bevel=0.03)
    C, Ro, Ri = Vector((0, 0, 1.35)), 0.88, 0.72
    post.cyl(0.08, C.z - Ro - 0.2, loc=(0, 0, (C.z - Ro + 0.2) / 2 + 0.1), seg=12)
    A = Vector((0.45, -0.62, 0.66)).normalized()
    P = A.cross(UP).normalized()
    N1, N2 = A.cross(P).normalized(), P.cross(UP).normalized()
    outer.torus(Ro, 0.06, loc=C, rot=facing(N2), seg=40, ring=8)
    inner.torus(Ri, 0.055, loc=C, rot=facing(N1), seg=40, ring=8)
    rotor.cyl(0.52, 0.18, loc=C, rot=facing(A), seg=32, bevel=0.04)
    rim.torus(0.52, 0.055, loc=C, rot=facing(A), seg=32, ring=8)
    axle.cyl(0.05, 2 * Ri, loc=C, rot=facing(A), seg=10)
    axle.cyl(0.12, 0.24, loc=C, rot=facing(A), seg=16, bevel=0.03)
    for s in (-1, 1):
        axle.cyl(0.06, 0.2, loc=C + P * s * (Ri + 0.08), rot=facing(P), seg=10)
    axle.sphere(0.08, loc=C + UP * (Ro + 0.05), seg=12, rings=8)


def commanders_periscope(a):
    """Commander's periscope: a cupola ring with its vision blocks and the tall periscope head, its big
    prism window glowing teal."""
    cup, blocks, glass, shaft, head, hood = (a.part('Cupola', 'Team'), a.part('Blocks', 'Armor'), a.part('Glass', 'LensTeal'),
                                             a.part('Shaft', 'Armor'), a.part('Head', 'Team'), a.part('Hood', 'Armor'))
    cup.cyl(0.95, 0.36, loc=(0, 0, 0.18), seg=36, bevel=0.08)
    for k in range(7):
        t = math.radians(-160 + k * 40)
        p = Vector((math.cos(t), math.sin(t), 0))
        rz = t + R90
        blocks.box((0.34, 0.16, 0.22), loc=p * 0.9 + Vector((0, 0, 0.42)), rot=(0, 0, rz), bevel=0.03)
        glass.box((0.24, 0.03, 0.12), loc=p * 0.985 + Vector((0, 0, 0.42)), rot=(0, 0, rz), bevel=0.01)
    H = Frame((0, 0, 0.36), (0, 0, 0.62))
    shaft.cyl(0.32, 0.14, seg=24, **H((0, 0, 0.07)))
    shaft.box((0.44, 0.44, 1.05), bevel=0.05, **H((0, 0.05, 0.6)))
    head.box((0.66, 0.8, 0.6), bevel=0.07, **H((0, -0.08, 1.35)))
    head.box((0.66, 0.4, 0.3), taper=(1, 0.45), shift=(0, 0.1), bevel=0.05, **H((0, -0.08, 1.8)))
    glass.box((0.5, 0.05, 0.38), bevel=0.02, **H((0, -0.5, 1.35), (-0.3, 0, 0)))
    hood.box((0.72, 0.34, 0.06), bevel=0.02, **H((0, -0.56, 1.62), (0.25, 0, 0)))
    for s in (-1, 1):
        hood.box((0.05, 0.3, 0.4), bevel=0.01, **H((s * 0.34, -0.52, 1.38)))


def camouflage_net(a):
    """Camouflage net: a rolled net bundle tufted with foliage, strapped with teal-buckled straps, one
    corner of netting spilling out on the ground."""
    roll, leaves, strap, buckle, cord = (a.part('Roll', 'FoliageDark'), a.part('Leaves', 'FoliageLight'), a.part('Straps', 'Rubber'),
                                         a.part('Buckles', 'LensTeal'), a.part('Cords', 'Canvas'))
    blotch = [a.part('Blotch0', 'Foliage'), a.part('Blotch1', 'Sandbag'), a.part('Blotch2', 'Dirt')]
    R, cz = 0.5, 0.55
    roll.cyl(R, 2.1, loc=(0, 0, cz), rot=ALONG_X, seg=28, bevel=0.2)
    rng = random.Random(7)
    for k in range(34):
        x = rng.uniform(-0.92, 0.92)
        if min(abs(x - 0.55), abs(x + 0.55)) < 0.14:
            continue
        t = rng.uniform(-0.9, math.pi + 0.9)
        n = Vector((0, math.cos(t), math.sin(t)))
        p = Vector((x, 0, cz)) + n * (R - 0.06)
        blotch[k % 3].ico(rng.uniform(0.16, 0.24), loc=p, sub=1, jitter=0.35, seed=k * 1.3)
    for k in range(16):
        x = rng.uniform(-1.0, 1.0)
        if min(abs(x - 0.55), abs(x + 0.55)) < 0.14:
            continue
        t = rng.uniform(0.2, math.pi - 0.2)
        n = Vector((0, math.cos(t), math.sin(t)))
        leaves.ico(rng.uniform(0.12, 0.17), loc=Vector((x, 0, cz)) + n * (R + 0.04), sub=1, jitter=0.4, seed=k * 2.1 + 9)
    for x in (-0.55, 0.55):
        strap.cyl(R + 0.05, 0.13, loc=(x, 0, cz), rot=ALONG_X, seg=28, bevel=0.02)
        buckle.box((0.18, 0.08, 0.16), loc=(x, -(R + 0.07), cz + 0.05), bevel=0.02)
    o = Vector((-0.15, -0.42, 0.22))
    ux, vy = Vector((1.15, 0, 0)), Vector((0.1, -0.85, -0.2))

    def q(u, v):
        return o + ux * u + vy * v
    for c in [i * 0.2 - 0.8 for i in range(9)]:
        v0, v1 = max(0.0, -c), min(1.0, 1.0 - c)
        if v1 - v0 > 0.05:
            cord.tube([q(v0 + c, v0), q(v1 + c, v1)], 0.03, seg=6)
    for c in [i * 0.2 + 0.2 for i in range(9)]:
        v0, v1 = max(0.0, c - 1.0), min(1.0, c)
        if v1 - v0 > 0.05:
            cord.tube([q(c - v0, v0), q(c - v1, v1)], 0.03, seg=6)
    for k, (u, v) in enumerate(((0.3, 0.55), (0.75, 0.3), (0.6, 0.85))):
        blotch[k].ico(0.14, loc=q(u, v) + Vector((0, 0, 0.03)), sub=1, jitter=0.35, seed=40 + k)


def signal_relay(a):
    """Signal relay: an olive field radio with a teal screen and dials, a tall whip antenna and teal
    radio waves spreading from its tip."""
    box, panel, screen, knobs, handle, base, whip, waves = (
        a.part('Radio', 'Team'), a.part('Panel', 'Armor'), a.part('Screen', 'LensTeal'), a.part('Knobs', 'Steel'),
        a.part('Handle', 'Steel'), a.part('AntennaBase', 'Rubber'), a.part('Whip', 'Undercarriage'), a.part('Waves', 'LensTeal'))
    box.box((1.35, 0.8, 1.0), loc=(0, 0, 0.5), bevel=0.08)
    panel.box((1.15, 0.05, 0.8), loc=(0, -0.41, 0.5), bevel=0.02)
    screen.box((0.52, 0.04, 0.3), loc=(-0.24, -0.44, 0.64), bevel=0.01)
    for x, z in ((0.22, 0.66), (0.44, 0.66), (0.22, 0.34), (0.44, 0.34), (-0.4, 0.3), (-0.12, 0.3)):
        knobs.cyl(0.07, 0.08, loc=(x, -0.46, z), rot=ALONG_Y, seg=12, bevel=0.015)
    handle.tube([(-0.4, 0.0, 1.0), (-0.4, 0.0, 1.16), (0.2, 0.0, 1.16), (0.2, 0.0, 1.0)], 0.045, seg=8)
    base.cyl(0.1, 0.24, loc=(0.46, 0.18, 1.12), seg=14, bevel=0.03)
    whip.cyl(0.035, 1.6, loc=(0.46, 0.18, 2.02), seg=8, bevel=0.0)
    whip.sphere(0.06, loc=(0.46, 0.18, 2.83), seg=10, rings=6)
    tip = Vector((0.46, 0.18, 2.55))
    for r in (0.3, 0.52):
        for mid in (0.0, math.pi):
            vtube(waves, arc3(tip, CAM_RIGHT, CAM_UP, r, mid - 0.7, mid + 0.7, 12), 0.045, seg=8)


# ----------------------------------------------------------------------------- special slot
def trophy_aps(a):
    """Trophy APS: an active protection kit, the flat radar panel sweeping red radar waves and the
    rotating interceptor launcher beside it on their mount."""
    base, panel, face, dots, leg, turn, launcher, tubes, waves = (
        a.part('Mount', 'Armor'), a.part('Panel', 'Team'), a.part('Face', 'EliteBlack'), a.part('Emitters', 'SignalRed'),
        a.part('Leg', 'Steel'), a.part('Turntable', 'Armor'), a.part('Launcher', 'Team'), a.part('Tubes', 'Undercarriage'),
        a.part('Waves', 'SignalRed'))
    base.box((2.2, 1.2, 0.14), loc=(0.1, 0.05, 0.07), bevel=0.04)
    P = Frame((-0.45, -0.05, 0.14), (-0.22, 0, 0.3))
    panel.box((1.15, 0.2, 1.15), bevel=0.06, **P((0, 0, 0.72)))
    face.box((0.95, 0.04, 0.95), bevel=0.02, **P((0, -0.115, 0.72)))
    for i in range(3):
        for j in range(3):
            dots.box((0.14, 0.03, 0.14), bevel=0.01, **P((-0.28 + i * 0.28, -0.14, 0.44 + j * 0.28)))
    leg.limb((-0.45, 0.45, 0.14), P.p((0, 0.1, 0.9)), 0.12, 0.12, bevel=0.02)
    c = P.p((0, -0.2, 0.72))
    for r in (0.8, 1.05, 1.3):
        vtube(waves, arc3(c, CAM_RIGHT, CAM_UP, r, math.pi - 0.5, math.pi + 0.5, 12), 0.045, seg=8)
    T = Frame((0.7, 0.1, 0.14), (0, 0, 0.5))
    turn.cyl(0.34, 0.16, seg=28, bevel=0.03, **T((0, 0, 0.08)))
    for s in (-1, 1):
        leg.box((0.06, 0.2, 0.4), bevel=0.01, **T((s * 0.33, 0, 0.35)))
    launcher.box((0.58, 0.62, 0.42), bevel=0.06, **T((0, 0, 0.5), (-0.3, 0, 0)))
    L = Frame(parent=T, loc=(0, 0, 0.5), rot=(-0.3, 0, 0))
    for x in (-0.13, 0.13):
        for z in (-0.09, 0.09):
            tubes.cyl(0.08, 0.02, seg=14, bevel=0, **L((x, -0.315, z), ALONG_Y))


def flare_dispenser(a):
    """Flare dispenser: a cell pod firing a fan of blazing flares on curling white smoke trails."""
    D = Frame((0, 0, 0.32), (-0.3, 0, 0.3))
    pod, cells, feet, trail, flare, burst = (a.part('Pod', 'Team'), a.part('Cells', 'Undercarriage'), a.part('Feet', 'Armor'),
                                             a.part('Trails', 'Snow'), a.part('Flares', 'Flare'), a.part('Burst', 'FlameOrange'))
    pod.box((1.2, 0.8, 0.5), bevel=0.06, **D())
    for i in range(4):
        for j in range(2):
            cells.box((0.2, 0.22, 0.03), bevel=0.0, **D((-0.42 + i * 0.28, -0.15 + j * 0.3, 0.25)))
    for x in (-0.45, 0.45):
        feet.box((0.2, 0.7, 0.3), bevel=0.03, loc=(x, 0.05, 0.12))
    for i, x in enumerate((-0.42, -0.14, 0.14, 0.42)):
        start = D.p((x, -0.15, 0.27))
        v = D.v((x * 2.4, -0.35, 1.0)).normalized() * 1.6
        n = 14
        pts = [start + v * (k / n) + Vector((0, 0, -0.55 * (k / n) ** 2)) * (1 + 0.2 * i) for k in range(n + 1)]
        # Smoke has spread behind the flare: fat near the pod, thin at the burning head.
        vtube(trail, pts, [0.05 + 0.07 * math.sin(math.pi * min(1.0, 0.15 + 0.85 * k / n)) ** 0.5 * (1 - 0.75 * k / n)
                           for k in range(n + 1)], seg=10)
        burst.ico(0.21, loc=pts[-1], sub=1, jitter=0.55, seed=i * 3.3)
        flare.sphere(0.14, loc=pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.04, seg=14, rings=10)


def drone_escort(a):
    """Drone escort: a small FPV quadcopter, carbon arms, red props, a yellow battery strapped on top
    and its camera pod looking ahead."""
    D = Frame((0, 0, 0.5), (0.22, -0.1, 0.45))
    arms, body, battery, strap, cam, lens, motors, props, green, red, whip = (
        a.part('Arms', 'EliteBlack'), a.part('Body', 'Team'), a.part('Battery', 'SafetyStripe'), a.part('Strap', 'Rubber'),
        a.part('Camera', 'Rubber'), a.part('Lens', 'LensTeal'), a.part('Motors', 'Steel'), a.part('Props', 'CarRed'),
        a.part('LedGreen', 'SignalGreen'), a.part('LedRed', 'SignalRed'), a.part('Whip', 'Undercarriage'))
    for t in (math.pi / 4, -math.pi / 4):
        arms.box((2.45, 0.2, 0.07), bevel=0.03, **D((0, 0, 0), (0, 0, t)))
    body.box((0.62, 0.82, 0.24), bevel=0.07, **D((0, 0, 0.14)))
    battery.box((0.42, 0.64, 0.24), bevel=0.05, **D((0, 0.06, 0.38)))
    strap.box((0.46, 0.09, 0.27), bevel=0.02, **D((0, 0.06, 0.385)))
    cam.box((0.3, 0.24, 0.28), bevel=0.05, **D((0, -0.5, 0.16), (-0.35, 0, 0)))
    lens.cyl(0.1, 0.06, seg=18, bevel=0.015, **D((0, -0.63, 0.2), (R90 - 0.35, 0, 0)))
    tip = 2.45 / 2 * math.cos(math.pi / 4)
    for k, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        px, py = sx * tip, sy * tip
        motors.cyl(0.13, 0.17, seg=16, bevel=0.03, **D((px, py, 0.1)))
        motors.cyl(0.04, 0.08, seg=8, **D((px, py, 0.22)))
        for b in range(3):
            t = b * TAU / 3 + k * 0.5
            props.box((0.5, 0.12, 0.025), bevel=0.01, **D((px + math.cos(t) * 0.26, py + math.sin(t) * 0.26, 0.23), (0.1, 0, t)))
        (red if sy < 0 else green).sphere(0.05, seg=10, rings=6, **D((px * 0.72, py * 0.72, -0.05)))
    whip.tube([D.p((0, 0.4, 0.2)), D.p((0, 0.62, 0.38)), D.p((0, 0.72, 0.6))], 0.025, seg=6)


def emp_payload(a):
    """EMP payload: a pulse device on an octagonal base, a copper coil round its core and a steel toroid
    on top crackling with blue arcs."""
    base, tier, caps, capt, core, coil, toroid, orb, arcs = (
        a.part('Base', 'Armor'), a.part('Tier', 'Team'), a.part('Capacitors', 'Team'), a.part('CapTops', 'Hazard'),
        a.part('Core', 'Steel'), a.part('Coil', 'Copper'), a.part('Toroid', 'Steel'), a.part('Orb', 'Energy'),
        a.part('Arcs', 'Energy'))
    base.cyl(0.82, 0.3, loc=(0, 0, 0.15), seg=8, bevel=0.05)
    tier.cyl(0.58, 0.24, loc=(0, 0, 0.42), seg=8, bevel=0.04)
    for k in range(4):
        t = math.pi / 4 + k * R90
        p = Vector((math.cos(t) * 0.62, math.sin(t) * 0.62, 0))
        caps.cyl(0.12, 0.4, loc=p + Vector((0, 0, 0.5)), seg=14, bevel=0.03)
        capt.cyl(0.13, 0.06, loc=p + Vector((0, 0, 0.72)), seg=14, bevel=0.02)
    core.cyl(0.17, 1.3, loc=(0, 0, 1.18), seg=18)
    for k in range(8):
        coil.torus(0.29, 0.065, loc=(0, 0, 0.66 + k * 0.13), seg=24, ring=8)
    toroid.torus(0.44, 0.16, loc=(0, 0, 1.92), seg=32, ring=12)
    orb.sphere(0.2, loc=(0, 0, 1.96), seg=16, rings=10)
    T = Vector((0, 0, 1.92))
    for k, b in enumerate((-35, 15, 150, 205)):
        w = CAM_RIGHT * math.cos(math.radians(b)) + UP * math.sin(math.radians(b)) * 0.6
        w.normalize()
        start, end = T + w * 0.6, T + w * 1.35 + Vector((0, 0, -0.25 if k % 2 == 0 else 0.1))
        vtube(arcs, zigzag(start, end, 6, 0.1, seed=k + 3), 0.035, seg=6)


def mine_dispenser(a):
    """Mine dispenser: a scatter canister in its cradle, olive disc mines with red pressure caps
    tumbling out of its mouth."""
    C = Frame((-0.5, 0.25, 0.62), (0, -0.28, -0.35))
    can, rim, dark, band, endcap, cradle = (a.part('Canister', 'Armor'), a.part('Rim', 'Steel'), a.part('Mouth', 'Undercarriage'),
                                            a.part('Band', 'SafetyStripe'), a.part('EndCap', 'Team'), a.part('Cradle', 'Team'))
    can.cyl(0.42, 1.5, seg=28, bevel=0.04, **C((0, 0, 0), ALONG_X))
    rim.torus(0.42, 0.045, seg=28, ring=8, **C((0.75, 0, 0), (0, R90, 0)))
    dark.cyl(0.37, 0.02, seg=28, bevel=0, **C((0.755, 0, 0), ALONG_X))
    for x in (-0.3, -0.52):
        band.cyl(0.43, 0.12, seg=28, bevel=0.01, **C((x, 0, 0), ALONG_X))
    endcap.cyl(0.44, 0.1, seg=28, bevel=0.03, **C((-0.78, 0, 0), ALONG_X))
    for x in (-0.45, 0.4):
        p = C.p((x, 0, -0.3))
        cradle.box((0.22, 0.8, p.z + 0.05), loc=(p.x, p.y, (p.z + 0.05) / 2), rot=(0, 0, -0.35), bevel=0.03)
    body, cap, ring = a.part('Mines', 'Team'), a.part('Caps', 'BarrelRed'), a.part('MineBands', 'SafetyStripe')

    def mine(M):
        body.lathe([(0.0, 0.0), (0.28, 0.0), (0.3, 0.04), (0.3, 0.09), (0.24, 0.14), (0.1, 0.16), (0.0, 0.16)], seg=24, **M())
        ring.cyl(0.305, 0.03, seg=24, bevel=0.005, **M((0, 0, 0.065)))
        cap.cyl(0.08, 0.06, seg=14, bevel=0.015, **M((0, 0, 0.18)))
    mine(Frame(parent=C, loc=(0.78, 0.05, -0.1), rot=(0, R90 * 0.75, 0)))
    for loc, rot in (((0.75, -0.6, 0.0), (0, 0, 0)), ((1.25, -0.05, 0.1), (0.35, 0.2, 0)), ((0.2, -0.95, 0.0), (0, 0, 0)),
                     ((1.35, -0.8, 0.07), (-0.25, 0.3, 0))):
        mine(Frame(loc, rot))


def war_profiteer(a):
    """War profiteer: an open wooden ammo crate heaped with gold coins, a gold bar and spilled coins."""
    crate, batten, bracket, rope, coins = (a.part('Crate', 'Wood'), a.part('Battens', 'LogWood'), a.part('Brackets', 'Steel'),
                                           a.part('Rope', 'Canvas'), a.part('Coins', 'Gilded'))
    W, D, H = 1.5, 0.9, 0.7
    crate.shell([(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)], H, 0.07, floor=0.07, bevel=0.02)
    for x in (-W / 2 + 0.12, W / 2 - 0.12):
        batten.box((0.12, D + 0.04, H), loc=(x, 0, H / 2), bevel=0.02)
    batten.box((W + 0.02, 0.04, 0.1), loc=(0, -D / 2 - 0.02, 0.35), bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bracket.box((0.1, 0.1, 0.12), loc=(sx * (W / 2 - 0.02), sy * (D / 2 - 0.02), H - 0.08), bevel=0.02)
    rope.tube([(W / 2 + 0.02, -0.2, 0.5), (W / 2 + 0.1, -0.15, 0.38), (W / 2 + 0.1, 0.15, 0.38), (W / 2 + 0.02, 0.2, 0.5)], 0.035, seg=8)
    ang = -1.95
    hinge = Vector((0, D / 2, H + 0.02))
    y, z = -D / 2, 0.04
    lid = hinge + Vector((0, y * math.cos(ang) - z * math.sin(ang), y * math.sin(ang) + z * math.cos(ang)))
    crate.box((W, D, 0.08), loc=lid, rot=(ang, 0, 0), bevel=0.02)
    coins.sphere((0.7, 0.4, 0.22), loc=(0, 0, 0.6), seg=24, rings=12, cut=0.0)
    rng = random.Random(11)
    for k in range(80):
        x, y = rng.uniform(-0.62, 0.62), rng.uniform(-0.33, 0.33)
        h = 0.22 * max(0.0, 1 - (x / 0.72) ** 2) * max(0.0, 1 - (y / 0.42) ** 2) ** 0.5
        coins.cyl(0.12, 0.035, loc=(x, y, 0.6 + h + rng.uniform(-0.01, 0.03)),
                  rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0), seg=16, bevel=0.01)
    for k in range(7):
        coins.cyl(0.12, 0.035, loc=(0.98 + rng.uniform(-0.02, 0.02), -0.62 + rng.uniform(-0.02, 0.02), 0.02 + k * 0.04), seg=16, bevel=0.01)
    for p in ((0.65, -0.78, 0.02), (1.25, -0.3, 0.02), (0.35, -0.72, 0.02)):
        coins.cyl(0.12, 0.035, loc=p, rot=(rng.uniform(-0.1, 0.1), 0, 0), seg=16, bevel=0.01)
    coins.cyl(0.12, 0.035, loc=(1.28, -0.72, 0.13), rot=(0, 1.2, 0.4), seg=16, bevel=0.01)
    coins.box((0.52, 0.26, 0.16), loc=(-0.98, -0.6, 0.08), rot=(0, 0, 0.35), taper=(0.78, 0.7), bevel=0.02)


def rally_horn(a):
    """Rally horn: a vehicle loudspeaker horn on its pole, its bell turned to the crowd, with a red flag
    flying from the pole top."""
    pole, horn, driver, bracket, flag, ball = (a.part('Pole', 'Steel'), a.part('Horn', 'Team'), a.part('Driver', 'Armor'),
                                               a.part('Bracket', 'Steel'), a.part('Flag', 'ClothRed'), a.part('Finial', 'Gilded'))
    top = Vector((-0.3, 0.25, 2.5))
    pole.cyl(0.055, 2.5, loc=(top.x, top.y, 1.25), seg=12)
    pole.cyl(0.3, 0.12, loc=(top.x, top.y, 0.06), seg=20, bevel=0.03)
    ball.sphere(0.1, loc=top + Vector((0, 0, 0.08)), seg=14, rings=8)
    Hf = Frame((top.x + 0.25, top.y - 0.25, 1.3), facing(Vector((0.35, -1.0, 0.22))))
    horn.lathe([(0.1, 0.0), (0.16, 0.3), (0.26, 0.6), (0.45, 0.86), (0.66, 1.0), (0.62, 1.03), (0.42, 0.9), (0.23, 0.66),
                (0.12, 0.38), (0.0, 0.34)], seg=32, **Hf())
    driver.cyl(0.25, 0.36, seg=24, bevel=0.05, **Hf((0, 0, -0.15)))
    bracket.limb(Hf.p((0, 0, -0.25)), Vector((top.x, top.y, 1.3)), 0.1, 0.1, bevel=0.02)
    bracket.cyl(0.09, 0.2, loc=(top.x, top.y, 1.3), seg=12)
    e = -CAM_RIGHT
    n = e.cross(UP).normalized()
    L, Hh = 1.2, 0.75

    def fn(u, v):
        p = top + e * (u * L + 0.05) + UP * (-v * Hh - 0.02 - 0.12 * u * u) + n * (0.13 * math.sin(u * 5.2 + v * 0.6) * u)
        return p, n
    sheet(flag, fn, 16, 3, 0.035)


def aegis_dome(a):
    """Aegis dome: a shield generator, its emitter orb on a stepped hexagonal pedestal projecting a
    translucent dome laced with glowing ribs."""
    ped, tier, spire, orb, nodes, ribs = (a.part('Pedestal', 'Armor'), a.part('Tier', 'Team'), a.part('Spire', 'Steel'),
                                          a.part('Emitter', 'ShieldGlow'), a.part('Nodes', 'ShieldGlow'), a.part('Ribs', 'ShieldGlow'))
    # Named Bombs_* so the kit treats it as loose: the shell must not darken the generator inside it.
    shell = a.part('Bombs_shield', 'ShieldGlass')
    ped.cyl(0.8, 0.26, loc=(0, 0, 0.13), seg=6, bevel=0.04)
    tier.cyl(0.55, 0.3, loc=(0, 0, 0.41), seg=6, bevel=0.04)
    spire.cyl(0.14, 0.55, r2=0.07, loc=(0, 0, 0.83), seg=12)
    orb.sphere(0.2, loc=(0, 0, 1.2), seg=18, rings=12)
    for k in range(3):
        t = k * TAU / 3 + 0.3
        p = Vector((math.cos(t) * 0.3, math.sin(t) * 0.3, 0.56))
        spire.limb(p, Vector((math.cos(t) * 0.12, math.sin(t) * 0.12, 1.28)), 0.05, 0.05, bevel=0.01)
    for k in range(6):
        t = k * TAU / 6
        nodes.sphere(0.06, loc=(math.cos(t) * 0.72, math.sin(t) * 0.72, 0.28), seg=10, rings=6)
    Rd, c = 1.5, Vector((0, 0, 0.02))
    for k in range(4):
        t = k * math.pi / 4
        vtube(ribs, arc3(c, Vector((math.cos(t), math.sin(t), 0)), UP, Rd, 0.0, math.pi, 28), 0.035, seg=6)
    for e in (0.0, math.radians(32), math.radians(62)):
        ribs.torus(Rd * math.cos(e), 0.035, loc=c + UP * (Rd * math.sin(e)), seg=48, ring=6)
    shell.sphere(Rd - 0.01, loc=c, seg=40, rings=20, cut=0.0)


def decoy_launcher(a):
    """Decoy launcher: a launch canister spilling its folded fabric through a hose into the inflatable
    decoy tank it has blown up, all puffed-out seams."""
    D = Frame((0.4, 0.3, 0), (0, 0, -0.4))
    hull, track, gun, can, band, rim, fabric, hose, valve = (
        a.part('Decoy', 'Team'), a.part('Tracks', 'Undercarriage'), a.part('DecoyGun', 'Team'), a.part('Canister', 'Armor'),
        a.part('Band', 'SafetyStripe'), a.part('Rim', 'Steel'), a.part('Fabric', 'Canvas'), a.part('Hose', 'Rubber'),
        a.part('Valve', 'Steel'))
    for y in (-0.74, 0.74):
        track.box((2.4, 0.5, 0.6), bevel=0.24, **D((0, y, 0.31)))
    hull.box((2.3, 1.26, 0.62), bevel=0.29, **D((0, 0, 0.77)))
    hull.sphere((0.68, 0.6, 0.37), seg=24, rings=12, **D((-0.14, 0, 1.18)))
    gun.lathe([(0.0, 0.0), (0.11, 0.02), (0.15, 0.1), (0.15, 1.2), (0.11, 1.28), (0.0, 1.3)], seg=16, **D((0.36, 0, 1.22), (0, R90, 0)))
    valve.cyl(0.08, 0.12, seg=12, **D((-1.16, -0.4, 0.75), (0, -R90, 0)))
    C = Frame((-1.6, -0.7, 0), (0.15, -0.18, 0))
    can.cyl(0.36, 0.9, seg=24, bevel=0.04, **C((0, 0, 0.45)))
    band.cyl(0.37, 0.14, seg=24, bevel=0.01, **C((0, 0, 0.66)))
    rim.torus(0.36, 0.04, seg=24, ring=6, **C((0, 0, 0.9)))
    fabric.ico((0.34, 0.34, 0.22), sub=2, jitter=0.25, seed=2.0, **C((0, 0, 0.94)))
    fabric.ico((0.22, 0.2, 0.14), sub=2, jitter=0.3, seed=5.0, **C((0.2, -0.1, 1.08)))
    hose.tube([C.p((0.3, 0.1, 0.25)), C.p((0.55, 0.2, 0.12)), D.p((-1.6, -0.3, 0.1)), D.p((-1.24, -0.4, 0.75))], 0.06, seg=10)


def uplink_barrage(a):
    """Uplink barrage: a satellite uplink dish on its mount beaming up to a floating red target reticle."""
    ped, mast, dish, hub, strut, feed, ret, beam = (
        a.part('Pedestal', 'Armor'), a.part('Mast', 'Team'), a.part('Dish', 'PlasterWhite'), a.part('Hub', 'Team'),
        a.part('Struts', 'Steel'), a.part('Feed', 'Undercarriage'), a.part('Reticle', 'SignalRed'), a.part('Beam', 'SignalRed'))
    b = Vector((-0.45, 0.35, 0))
    ped.box((1.0, 1.0, 0.3), loc=b + Vector((0, 0, 0.15)), bevel=0.06)
    mast.cyl(0.15, 0.6, loc=b + Vector((0, 0, 0.6)), seg=16, bevel=0.03)
    mast.box((0.5, 0.22, 0.3), loc=b + Vector((0, 0, 0.95)), bevel=0.05)
    S = Frame(b + Vector((0, 0, 1.12)), facing(Vector((0.3, -0.55, 0.78))))
    dish.lathe([(0.0, 0.0), (0.4, 0.05), (0.75, 0.18), (1.02, 0.36), (1.06, 0.41), (0.75, 0.25), (0.4, 0.12), (0.0, 0.08)],
               seg=40, **S())
    hub.cyl(0.24, 0.24, seg=20, bevel=0.04, **S((0, 0, -0.08)))
    f = S.p((0, 0, 0.95))
    for k in range(3):
        t = math.radians(90 + k * 120)
        strut.limb(S.p((0.98 * math.cos(t), 0.98 * math.sin(t), 0.39)), f, 0.05, 0.05, bevel=0.01)
    strut.cyl(0.09, 0.18, seg=14, **S((0, 0, 0.95)))
    feed.cyl(0.07, 0.04, seg=14, bevel=0, **S((0, 0, 0.86)))
    R = Vector((0.75, -0.55, 2.35))
    rr = facing(CAM_DIR)
    ret.torus(0.44, 0.045, loc=R, rot=rr, seg=36, ring=8)
    F = Frame(R, rr)
    for t in (0, R90, math.pi, 3 * R90):
        ret.box((0.26, 0.06, 0.06), bevel=0.01, **F((math.cos(t) * 0.44, math.sin(t) * 0.44, 0), (0, 0, t)))
    ret.sphere(0.06, loc=R, seg=12, rings=8)
    for k in range(1, 6):
        beam.sphere(0.04, loc=f.lerp(R, k / 6), seg=10, rings=6)


ITEMS = {
    # weapon
    'long_barrel': long_barrel, 'tungsten_penetrator': tungsten_penetrator, 'he_frag_filler': he_frag_filler,
    'proximity_fuze': proximity_fuze, 'bunker_buster': bunker_buster, 'hypervelocity_charge': hypervelocity_charge,
    'heavy_barrel': heavy_barrel,
    # loader
    'extended_ammo_rack': extended_ammo_rack, 'belt_feed': belt_feed, 'salvo_rack': salvo_rack, 'hair_trigger': hair_trigger,
    # armour
    'composite_addon': composite_addon, 'spall_liner': spall_liner, 'applique_steel': applique_steel,
    'fire_retardant_hull': fire_retardant_hull, 'armoured_tub': armoured_tub, 'monolith_plate': monolith_plate,
    'frontal_wedge': frontal_wedge, 'slat_cage': slat_cage, 'overhead_screen': overhead_screen, 'mine_rollers': mine_rollers,
    # engine
    'turbocharger': turbocharger, 'turret_drive': turret_drive, 'transit_gearbox': transit_gearbox,
    'overtuned_engine': overtuned_engine,
    # repair
    'crew_drills': crew_drills, 'fire_extinguisher': fire_extinguisher,
    # optics
    'laser_rangefinder': laser_rangefinder, 'gun_stabiliser': gun_stabiliser, 'commanders_periscope': commanders_periscope,
    'camouflage_net': camouflage_net, 'signal_relay': signal_relay,
    # special
    'trophy_aps': trophy_aps, 'flare_dispenser': flare_dispenser, 'drone_escort': drone_escort, 'emp_payload': emp_payload,
    'mine_dispenser': mine_dispenser, 'war_profiteer': war_profiteer, 'rally_horn': rally_horn, 'aegis_dome': aegis_dome,
    'decoy_launcher': decoy_launcher, 'uplink_barrage': uplink_barrage,
}


# ----------------------------------------------------------------------------- rendering
def glow_only(mat):
    """Black diffuse under the emission: the sun no longer adds white on top of the glow's hue."""
    for n in mat.node_tree.nodes:
        if n.type == 'MIX':
            next(s for s in n.inputs if s.identifier == 'B_Color').default_value = (0, 0, 0, 1)
        elif n.type == 'BSDF_PRINCIPLED':
            n.inputs['Roughness'].default_value = 0.8


def translucent(mat, alpha):
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Alpha'].default_value = alpha
    if hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'BLENDED'
    else:
        mat.blend_method = 'BLEND'


def frame_camera(co, objects, fill=FILL):
    """Point the first set's camera along its usual direction, then pull it in or out and shift the lens
    until the silhouette's larger side fills `fill` of the picture, centred."""
    pts = [o.matrix_world @ v.co for o in objects for v in o.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) / 2
    cam = co.data
    cam.shift_x = cam.shift_y = 0.0
    tan_half = 18 / cam.lens
    rot = (-CAM_DIR).to_track_quat('-Z', 'Y')
    inv = rot.to_matrix().transposed()
    dist = (hi - lo).length / 2 / math.sin(math.atan(tan_half))

    def project(d):
        loc = centre + CAM_DIR * d
        us, vs = [], []
        for p in pts:
            q = inv @ (p - loc)
            us.append(q.x / (-q.z * tan_half))
            vs.append(q.y / (-q.z * tan_half))
        return loc, us, vs
    for _ in range(8):
        _, us, vs = project(dist)
        dist *= max(max(us) - min(us), max(vs) - min(vs)) / (2 * fill)
    loc, us, vs = project(dist)
    co.location = loc
    co.rotation_euler = rot.to_euler()
    cam.shift_x = (max(us) + min(us)) / 4
    cam.shift_y = (max(vs) + min(vs)) / 4


def render(scene, co, name, build):
    root = fk.workspace()
    a = fk.Asset(f'gear2_{name}', root, ground=False)
    build(a)
    a.finish()
    objects = [o for o in a.collection.objects if o.type == 'MESH']
    for o in objects:
        for slot in o.material_slots:
            mat = slot.material
            if mat and mat.name.startswith('Team'):
                gi.paint_team(mat)
            if mat and mat.get('frontier_kit') == 'ShieldGlass':
                translucent(mat, 0.2)
            if mat and mat.get('frontier_kit') in GLOW_ONLY:
                glow_only(mat)
    bpy.context.view_layer.update()
    frame_camera(co, objects)
    OUT.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(OUT / f'{name}.png')
    bpy.ops.render.render(write_still=True)
    print('ICON_WRITTEN', scene.render.filepath)
    fk.clear_workspace(root)


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    unknown = [n for n in args if n not in ITEMS and n not in REUSED]
    if unknown:
        raise SystemExit(f'unknown gear ids: {unknown}')
    for name, source in REUSED.items():
        if not args or name in args:
            shutil.copyfile(OUT / f'{source}.png', OUT / f'{name}.png')
            print('ICON_COPIED', source, '->', name)
    todo = [(n, b) for n, b in ITEMS.items() if not args or n in args]
    if not todo:
        return
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    scene, co = gi.setup_scene()
    for name, build in todo:
        render(scene, co, name, build)


main()
