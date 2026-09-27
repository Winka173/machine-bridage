"""Machine Brigade boss "Silver Bug", built with frontier_kit: a what-if of the declassified 1956 USAF
Project 1794 / Avro Canada VZ-9 Avrocar supersonic flying disc, built full size.

Conventions as in mb_air.py: metres, +Z up, Blender -Y is the front, the vehicle's left is +X, and the
origin is at the centre of the disc (it flies). Team / TeamGlow parts are recoloured per army at runtime.
Touching parts overlap or stand at least 1 cm apart, so no two visible faces are coplanar.
  * silver_bug: a bare-aluminium lens 30.2 m across and 7.8 m deep at the centre (canopy to ball turret;
    the hull itself is 4.7 m), skinned in panels of three tones with rivet rows, maintenance hatches,
    stencils, a walkway and USAF-style markings (star-and-bar insignia, lettering and a Day-Glo rim ring
    in the army colour).
      - `Radar` (pivot at the origin) carries the rim that turns round the body: the Day-Glo focusing
        ring and the turbine vanes in front of the glowing exhaust ports. The runtime spins anything
        called Radar slowly about its up axis.
      - `Turret` is the ventral ball turret (a yaw pivot under the centre) with the laser: the lens barrel
        `Main_cannon` (cooling fins `Main_cannon_fins`, lens `Main_cannon_lens`, emitter ring and core
        `Main_cannon_glow` / `Main_cannon_core`) and `Muzzle_main` 3.45 m ahead of the pivot.
      - `Muzzle_gun` at the centre, level with the barrels of the four rim coilgun turrets. The barrels
        are the part `Miniguns` (the runtime's gun-launcher name); the turrets stand at 22.5 + k * 90
        degrees, four-fold symmetric about the centre, so every one has its own position across the
        model and the runtime finds four launchers.
      - `Mount_mg` turns the point-defence flak on the upper deck behind the canopy; `Muzzle_mg` at its
        four barrels.
      - `Muzzle_missile` at the open drone bay under the rear.
    The radiator vents on top (amber glowing slots under louvres) are its weak point. Landing legs sit
    retracted in three ventral fairings.
"""
import math
import random

from mathutils import Euler, Matrix, Vector

from mb_air import FORWARD, R90, _revolve
from mb_air3 import _fpv_drone

TAU = math.tau
RB = 13.3                             # body rim radius; the rotating ring runs outside it to 15.1 m
RT, ZT_IN, ZT_RIM = 5.1, 2.34, .36    # upper skin: inner radius, its height there and at the rim
RL, ZB_IN, ZB_RIM = 4.75, -1.88, -.34  # lower skin
Z_HUB = -2.0                          # flat ventral hub under the ball turret
Z_DECK = 2.66                         # canopy deck
# Section of the rotating rim ring (radius, z), counter-clockwise: a wedge whose top carries on the
# lens's slope out to a rounded leading edge.
RING = [(14.0, -.26), (14.25, -.3), (14.7, -.22), (15.0, -.08), (15.1, 0), (15.0, .09), (14.7, .23), (14.25, .32),
        (14.0, .3)]
GUN_ANGLES = [math.radians(22.5 + 90 * k) for k in range(4)]
RAD_ANGLES = [math.radians(67.5 + 90 * k) for k in range(4)]


# ----------------------------------------------------------------------------- skin geometry
def _u(r, r_in):
    return min(1.0, max(0.0, (RB - r) / (RB - r_in)))


def _zt(r):
    """Height of the upper skin at radius r (a lens: steepest at the rim, level at the hub)."""
    return ZT_RIM + (ZT_IN - ZT_RIM) * (1 - (1 - _u(r, RT)) ** 2)


def _zb(r):
    """Height of the lower skin at radius r."""
    return ZB_RIM + (ZB_IN - ZB_RIM) * (1 - (1 - _u(r, RL)) ** 2)


def _slope(r, lower=False):
    """dz/dr of the upper (or lower) skin at radius r."""
    r_in, z_in, z_rim = (RL, ZB_IN, ZB_RIM) if lower else (RT, ZT_IN, ZT_RIM)
    u = _u(r, r_in)
    return 0.0 if u >= 1.0 else -(z_in - z_rim) * 2 * (1 - u) / (RB - r_in)


def _on(x, y, off=0.0, lower=False):
    """Point on the skin over (x, y), `off` metres proud of it (below it on the lower skin)."""
    r = math.hypot(x, y)
    k = math.sqrt(1 + _slope(r, lower) ** 2)
    return (x, y, _zb(r) - off * k) if lower else (x, y, _zt(r) + off * k)


def _lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def _pol(r, a, z=0.0):
    return (r * math.cos(a), r * math.sin(a), z)


def _mat(loc, rot=(0, 0, 0)):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


def _frame_on(r, a, lower=False, off=0.0):
    """Frame on the skin at polar (r, a): x runs outwards along the slope, y round the disc and z along
    the surface normal (up on the upper skin, down on the lower one)."""
    s = _slope(r, lower)
    er = Vector((math.cos(a), math.sin(a), s)).normalized()
    et = Vector((-math.sin(a), math.cos(a), 0.0))
    if lower:
        et = -et
    m = Matrix((er, et, er.cross(et))).transposed().to_4x4()
    m.translation = Vector(_on(r * math.cos(a), r * math.sin(a), off, lower))
    return m


def _put(m, loc=(0, 0, 0), rot=(0, 0, 0)):
    """World (loc, rot) of a primitive placed at loc / rot in frame m."""
    mm = m @ _mat(loc, rot)
    return tuple(mm.translation), tuple(mm.to_euler('XYZ'))


def _fbox(part, m, size, loc=(0, 0, 0), rot=(0, 0, 0), **kw):
    p, e = _put(m, loc, rot)
    part.box(size, loc=p, rot=e, **kw)


def _fcyl(part, m, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), **kw):
    p, e = _put(m, loc, rot)
    part.cyl(r, depth, loc=p, rot=e, **kw)


def _plane(rc, ac):
    """(u, v) -> (x, y) in the plane at radius rc, angle ac: u outwards, v round the disc."""
    c, s = math.cos(ac), math.sin(ac)
    return lambda u, v: (rc * c + u * c - v * s, rc * s + u * s + v * c)


def _polar(r, a):
    return (r * math.cos(a), r * math.sin(a))


def _drape(part, pt, us, vs, out=.02, inn=.04, lower=False):
    """Plate hugging the skin: pt(u, v) -> (x, y) over the stations us x vs, `out` proud of the skin
    and sunk `inn` into it."""
    rings = [[_on(*pt(u, v), out, lower) for v in vs] + [_on(*pt(u, v), -inn, lower) for v in reversed(vs)]
             for u in us]
    part.loft(rings, bevel=0)


def _sector(part, r0, r1, a0, a1, out=.02, inn=.04, lower=False, step=1.0):
    """Skin panel between radii r0..r1 and angles a0..a1."""
    nr = max(2, int(math.ceil((r1 - r0) / step)) + 1)
    na = max(2, int(math.ceil(abs(a1 - a0) * r1 / step)) + 1)
    _drape(part, _polar, _lin(r0, r1, nr), _lin(a0, a1, na), out, inn, lower)


def _decal(part, poly, pt, off=.045, lower=False, rings=2):
    """Flat marking on the skin: a star-shaped outline [(u, v)...] (counter-clockwise in pt's plane),
    fanned from its centroid through `rings` concentric steps so it follows the curve."""
    n = len(poly)
    cu, cv = sum(p[0] for p in poly) / n, sum(p[1] for p in poly) / n
    verts = [_on(*pt(cu, cv), off, lower)]
    for k in range(1, rings + 1):
        t = k / rings
        verts += [_on(*pt(cu + (u - cu) * t, cv + (v - cv) * t), off, lower) for u, v in poly]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((0, 1 + i, 1 + j))
        for k in range(1, rings):
            a0, b0 = 1 + (k - 1) * n, 1 + k * n
            faces.append((a0 + i, b0 + i, b0 + j, a0 + j))
    part.mesh(verts, [tuple(reversed(f)) for f in faces] if lower else faces)


def _strip(part, pt, u0, u1, v0, v1, off=.045, lower=False, step=.8):
    """Rectangular marking from (u0, v0) to (u1, v1) in pt's plane, cut every `step` along its length."""
    along_u = abs(u1 - u0) >= abs(v1 - v0)
    n = max(1, int(math.ceil(max(abs(u1 - u0), abs(v1 - v0)) / step)))
    if along_u:
        side_a = [(u0 + (u1 - u0) * i / n, v0) for i in range(n + 1)]
        side_b = [(u0 + (u1 - u0) * i / n, v1) for i in range(n + 1)]
    else:
        side_a = [(u1, v0 + (v1 - v0) * i / n) for i in range(n + 1)]
        side_b = [(u0, v0 + (v1 - v0) * i / n) for i in range(n + 1)]
    verts = [_on(*pt(u, v), off, lower) for u, v in side_a + side_b]
    faces = [(i, i + 1, n + 2 + i, n + 1 + i) for i in range(n)]
    # Wind counter-clockwise seen from outside.
    p0, p1, p2 = (Vector(verts[k]) for k in faces[0][:3])
    up = (p1 - p0).cross(p2 - p0).z
    if (up < 0) != lower:
        faces = [tuple(reversed(f)) for f in faces]
    part.mesh(verts, faces)


RIVET = [(math.cos(k * TAU / 3 + R90), math.sin(k * TAU / 3 + R90)) for k in range(3)]


def _rivets(part, pts, base=0.0, lower=False, size=.07, h=.022):
    """Rivet heads (low three-sided pyramids) at [(x, y)...] on the skin; base is the height of the plate
    they sit on above the skin."""
    d = size / 2
    for x, y in pts:
        verts = [_on(x + d * cx, y + d * cy, base - .012, lower) for cx, cy in RIVET] + [_on(x, y, base + h, lower)]
        faces = [(i, (i + 1) % 3, 3) for i in range(3)]
        part.mesh(verts, [tuple(reversed(f)) for f in faces] if lower else faces)


def _flat_rivets(part, pts, size=.07, h=.022, down=False):
    """Rivet heads at [(x, y, z)...] on a level surface (facing down if `down`)."""
    d = size / 2
    s = -1 if down else 1
    for x, y, z in pts:
        verts = [(x + d * cx, y + d * cy, z - s * .012) for cx, cy in RIVET] + [(x, y, z + s * h)]
        faces = [(i, (i + 1) % 3, 3) for i in range(3)]
        part.mesh(verts, [tuple(reversed(f)) for f in faces] if down else faces)


def _band(part, pts, q0, q1, steps=1, out=.02, inn=.015):
    """Band from angle q0 to q1 over a (radius, z) polyline of a surface of revolution (a part of its
    section, counter-clockwise, so the outside is to the right of the direction of travel), `out`
    proud of it and sunk `inn` into it: joints and markings on the rim ring, warning bands."""
    n = len(pts)
    top, bot = [], []
    for i, (r, z) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        t = Vector((b[0] - a[0], b[1] - a[1])).normalized()
        nr, nz = t.y, -t.x
        top.append((r + nr * out, z + nz * out))
        bot.append((r - nr * inn, z - nz * inn))
    loop = top + bot[::-1]
    part.loft([[_pol(r, q0 + (q1 - q0) * k / steps, z) for r, z in loop] for k in range(steps + 1)], bevel=0)


def _ring_band(part, pts, q, width, out=.02, inn=.015):
    """Band `width` metres wide (at the section's first point) centred on angle q."""
    half = width / 2 / pts[0][0]
    _band(part, pts, q - half, q + half, 1, out, inn)


def _ring_pts(r, n):
    """n points evenly round the circle of radius r (rivet rows)."""
    return [_polar(r, (i + .5) * TAU / n) for i in range(n)]


def _stencil(part, pt, u0, v0, rows, width, rng, h=.07, gap=.05, off=.045, lower=False):
    """Rows of word-sized dashes reading as stencilled text, from (u0, v0) along +u in pt's plane,
    each row below the last (towards -v)."""
    for row in range(rows):
        v = v0 - row * (h + gap)
        u, end = u0, u0 + width * (1.0 if row == 0 else rng.uniform(.45, .9))
        while u < end - .05:
            w = min(end - u, rng.uniform(.12, .38))
            _strip(part, pt, u, u + w, v - h, v, off, lower)
            u += w + rng.uniform(.05, .09)


# ----------------------------------------------------------------------------- markings
def _star(cu, cv, r_out, r_in, rot=R90):
    return [(cu + (r_out if i % 2 == 0 else r_in) * math.cos(rot + i * math.pi / 5),
             cv + (r_out if i % 2 == 0 else r_in) * math.sin(rot + i * math.pi / 5)) for i in range(10)]


def _circle(cu, cv, r, n=24):
    return [(cu + r * math.cos(i * TAU / n), cv + r * math.sin(i * TAU / n)) for i in range(n)]


def _insignia(a, pt, size=1.25, lower=False, up=R90, base=.045):
    """USAF star-and-bar: an army-colour roundel with a white star, white bars either side with an
    army-colour stripe and outline. `up` is the direction (in pt's plane) the star's top points."""
    team, white = a.part('Insignia', 'Team'), a.part('Insignia_white', 'Medical')
    R = size
    c, s = math.cos(up - R90), math.sin(up - R90)

    def q(u, v):  # insignia space (u along the bars, v up the star) -> pt's plane
        return pt(u * c - v * s, u * s + v * c)
    for sx in (-1, 1):
        inner, outer = sx * R * .85, sx * R * 2.05
        _strip(team, q, inner, outer + sx * .07, -R * .36, R * .36, off=base, lower=lower)
        _strip(white, q, inner, outer, -R * .29, R * .29, off=base + .012, lower=lower)
        _strip(team, q, inner, outer - sx * .1, -R * .09, R * .09, off=base + .024, lower=lower)
    _decal(team, _circle(0, 0, R), q, off=base + .024, lower=lower)
    _decal(white, _star(0, 0, R * .94, R * .36), q, off=base + .036, lower=lower)


LETTERS = {  # strokes (u0, v0, u1, v1) in a 1 x 1.4 box
    'U': [(0, 0, .26, 1.4), (.74, 0, 1, 1.4), (.26, 0, .74, .26)],
    'S': [(0, 1.14, 1, 1.4), (0, .57, .26, 1.14), (0, .57, 1, .83), (.74, .26, 1, .57), (0, 0, 1, .26)],
    'A': [(0, 0, .26, 1.4), (.74, 0, 1, 1.4), (.26, 1.14, .74, 1.4), (.26, .57, .74, .83)],
    'F': [(0, 0, .26, 1.4), (.26, 1.14, 1, 1.4), (.26, .57, .8, .83)],
}


def _lettering(part, pt, text, u0, v0, h, off=.045, lower=False):
    """Block capitals `h` tall from (u0, v0) (bottom left) along +u in pt's plane."""
    k = h / 1.4
    u = u0
    for ch in text:
        for a0, b0, a1, b1 in LETTERS[ch]:
            _strip(part, pt, u + a0 * k, u + a1 * k, v0 + b0 * k, v0 + b1 * k, off, lower, step=.5)
        u += 1.35 * k


# ----------------------------------------------------------------------------- the boss
def silver_bug(a):
    """Project 1794 flying disc: see the module docstring."""
    rng = random.Random(1794)
    skin = a.part('Hull', 'Steel')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    sheet = a.part('Panels', 'MetalSheet')
    light = a.part('Panels_light', 'Fuel')
    rivet = a.part('Rivets', 'MetalSheet')
    black = a.part('Stencils', 'Undercarriage')
    team = a.part('Markings', 'Team')

    # ---- the lens: one lathe from the ventral hub round the rim to the canopy deck.
    prof = [(0, Z_HUB), (4.3, Z_HUB), (4.6, -1.92)]
    prof += [(r, _zb(r)) for r in _lin(RL, 13.15, 8)]
    prof += [(13.3, -.3), (13.4, -.16), (13.43, 0), (13.4, .17), (13.3, .31)]
    prof += [(r, _zt(r)) for r in _lin(13.15, RT, 8)]
    prof += [(5.02, 2.4), (4.92, 2.45), (4.84, 2.36), (4.84, 2.0), (3.34, 2.0), (3.34, 2.5), (3.0, 2.6), (2.7, Z_DECK),
             (0, Z_DECK)]
    skin.lathe(prof, seg=44)

    # ---- panel patchwork on the upper skin: three belts of panels in three tones; the 5 cm gaps
    # between them show the hull as panel lines.
    belts = ((5.3, 7.45, 16, 0.0), (7.55, 10.25, 16, math.pi / 16), (10.35, 12.95, 24, 0.0))
    for r0, r1, n, phase in belts:
        for i in range(n):
            a0 = phase + i * TAU / n
            a1 = a0 + TAU / n
            g = .05 / ((r0 + r1) / 2)
            pick = rng.random()
            if pick < .3:
                continue                                           # bare hull panel
            part = light if pick < .6 else sheet
            _sector(part, r0, r1, a0 + g / 2, a1 - g / 2, out=.025, inn=.045, step=1.4)
    # Lower skin: every other panel of two belts in the other tones (the hull shows between them).
    for r0, r1, n, phase, part in ((4.9, 8.6, 12, 0.0, light), (8.7, 12.9, 16, math.pi / 16, sheet)):
        for i in range(0, n, 2):
            a0 = phase + i * TAU / n
            _sector(part, r0, r1, a0, a0 + TAU / n, out=.03, inn=.045, lower=True, step=1.6)
    # Rivet rows along the belt seams and round the rim.
    for r, n in ((7.5, 72), (10.3, 90), (13.02, 96)):
        _rivets(rivet, _ring_pts(r, n), base=.0)

    # ---- canopy: a framed glass dome on the deck, an escape hatch and beacon on top.
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    A, C, zc = 2.55, 1.28, Z_DECK - .03
    glass.sphere((A, A, C), loc=(0, 0, zc), seg=32, rings=12, cut=0)
    frames.torus(A + .02, .1, loc=(0, 0, zc + .06), seg=32, ring=4)
    t_top = math.acos(.5 / (A + .03))
    for k in range(8):
        q = k * TAU / 8 + TAU / 16
        frames.tube([((A + .03) * math.cos(t) * math.cos(q), (A + .03) * math.cos(t) * math.sin(q),
                      zc + (C + .03) * math.sin(t)) for t in _lin(.05, t_top, 6)], .055, seg=4)
    t = .62                                                                                   # hoop
    hoop = (A + .03) * math.cos(t)
    frames.tube([(hoop * math.cos(q), hoop * math.sin(q), zc + (C + .03) * math.sin(t))
                 for q in (i * TAU / 28 for i in range(29))], .045, seg=4, caps=False)
    steel.cyl(.56, .16, loc=(0, 0, zc + C - .02), seg=16, bevel=.03, bseg=1)                 # escape hatch
    a.part('Beacon', 'TeamGlow').sphere(.13, loc=(0, 0, zc + C + .1), seg=8, rings=5)
    _flat_rivets(rivet, [(2.86 * math.cos(q), 2.86 * math.sin(q), 2.64) for q in (i * TAU / 40 for i in range(40))])
    # Yellow rescue arrow pointing at the canopy's escape hatch, and warning bands on the intake lip.
    haz = a.part('Warnings', 'Hazard')
    ar = _plane(0, math.radians(228))
    _strip(haz, ar, 6.1, 7.3, -.09, .09, step=.6)
    _decal(haz, [(5.35, 0), (6.15, -.36), (6.15, .36)], ar, rings=1)
    _stencil(black, ar, 6.3, -.2, 1, .7, rng)
    lip = [(RT, ZT_IN), (5.02, 2.4), (4.92, 2.45), (4.84, 2.36)]
    for k in range(4):
        q = math.radians(45 + 90 * k)
        _band(haz, lip, q - .16, q + .16, 3, out=.015)
    team.lathe([(3.02, 2.595), (3.02, 2.615), (2.72, 2.678), (2.72, 2.66)], seg=36)            # Day-Glo collar

    # ---- central turbo-rotor intake round the canopy: dark floor, stator vanes and a grille ring.
    _revolve(dark, [(3.36, 2.005), (4.82, 2.005), (4.82, 2.03), (3.36, 2.03)], (0, 0, 0), (0, 0, 0), seg=36)
    vanes = a.part('Intake_vanes', 'Steel')
    for k in range(24):
        q = k * TAU / 24
        vanes.box((1.5, .05, .38), loc=_pol(4.09, q, 2.19), rot=(.45, 0, q), bevel=0)
    _revolve(vanes, [(4.05, 2.33), (4.13, 2.33), (4.13, 2.39), (4.05, 2.39)], (0, 0, 0), (0, 0, 0), seg=28)
    blades = a.part('Intake_blades', 'Armor')
    for k in range(20):
        q = (k + .5) * TAU / 20
        blades.box((1.45, .32, .03), loc=_pol(4.09, q, 2.07), rot=(-.6, 0, q), bevel=0)

    # ---- rim: the body's wall with 24 glowing exhaust ports, a glowing nozzle throat under the vanes,
    # and the rotating ring (`Radar`): Day-Glo focusing ring, turbine vanes, clamps and joints.
    ports = a.part('Exhaust_ports', 'Undercarriage')
    glow = a.part('Exhaust_glow', 'TeamGlow')
    port_frames = a.part('Port_frames', 'Steel')
    for k in range(24):
        q = (k + .5) * TAU / 24
        ports.box((.2, 1.3, .32), loc=_pol(13.36, q, 0), rot=(0, 0, q), bevel=0)
        glow.box((.02, 1.14, .2), loc=_pol(13.465, q, 0), rot=(0, 0, q), bevel=0)
        port_frames.box((.26, .12, .5), loc=_pol(13.36, q + TAU / 48, 0), rot=(0, 0, q + TAU / 48), bevel=0)
    _revolve(glow, [(13.24, -.31), (14.1, -.31), (14.1, -.28), (13.24, -.28)], (0, 0, 0), (0, 0, 0), seg=48)
    rim = a.pivot('Radar', (0, 0, 0))
    ring = a.part('Rim_ring', 'Team', rim)
    _revolve(ring, RING, (0, 0, 0), (0, 0, 0), seg=56)
    rim_vanes = a.part('Rim_vanes', 'Armor', rim)
    for k in range(54):
        q = k * TAU / 54
        rim_vanes.box((.64, .06, .5), loc=_pol(13.83, q, .0), rot=(.6, 0, q), bevel=0)
    joints = a.part('Rim_joints', 'Undercarriage', rim)
    clamps = a.part('Rim_clamps', 'Steel', rim)
    marks = a.part('Rim_marks', 'Hazard', rim)
    for k in range(8):
        q = k * TAU / 8
        _ring_band(joints, RING[4:], q + TAU / 16, .06)
        if k % 2:
            for z in (.31, -.29):
                clamps.box((.45, .38, .1), loc=_pol(14.45, q, z), rot=(0, 0, q), bevel=0)
        else:
            _ring_band(marks, RING[2:7], q, .9, out=.012)

    # ---- radiators (the weak point): louvred housings with glowing amber slots.
    rad_frame = a.part('Radiator_frames', 'Armor')
    rad_bed = a.part('Radiator_beds', 'Undercarriage')
    rad_glow = a.part('Radiator_glow', 'Alloy')
    louvres = a.part('Radiator_louvres', 'Steel')
    for q in RAD_ANGLES:
        m = _frame_on(8.6, q)
        L, W = 3.3, 2.3
        rad_bed.box((L, W, .3), loc=tuple(m @ Vector((0, 0, -.03))), rot=tuple(m.to_euler('XYZ')), bevel=0)
        for sy in (-1, 1):
            _fbox(rad_frame, m, (L + .24, .14, .36), loc=(0, sy * (W / 2 + .05), .02), bevel=0)
        for sx in (-1, 1):
            _fbox(rad_frame, m, (.14, W + .1, .36), loc=(sx * (L / 2 + .05), 0, .02), bevel=0)
        for i in range(7):
            x = -L / 2 + .3 + i * (L - .6) / 6
            _fbox(rad_glow, m, (.16, W - .3, .04), loc=(x, 0, .125), bevel=0)
            _fbox(louvres, m, (.1, W - .16, .04), loc=(x + .12, 0, .17), rot=(0, -.5, 0), bevel=0)
        pts = [tuple(m @ Vector((x, sy * (W / 2 + .05), .205))) for sy in (-1, 1) for x in _lin(-L / 2, L / 2, 9)]
        _flat_rivets(rivet, pts, size=.05)

    # ---- engine-bay hatches inboard of each coilgun: raised panels, a hinge rail, latches, a grille.
    hatch = a.part('Hatches', 'Steel')
    hinge = a.part('Hatch_hinges', 'Armor')
    for q in GUN_ANGLES:
        w = .85
        pt = _plane(0, q)
        _drape(hatch, pt, _lin(5.9, 10.6, 6), _lin(-w, w, 3), out=.045, inn=.04)
        hinge.tube([_on(*pt(u, w + .03), .07) for u in _lin(6.0, 10.5, 6)], .045, seg=5)
        for u in _lin(6.3, 10.2, 6):
            _strip(black, pt, u - .07, u + .07, -w + .05, -w + .2, off=.058)
        for i in range(5):
            _strip(dark, pt, 9.4 + i * .2, 9.5 + i * .2, -.45, .45, off=.058, step=.5)           # exhaust grille
        _rivets(rivet, [pt(u, v) for u in _lin(6.0, 10.5, 10) for v in (-w + .06, w - .06)], base=.045)
        _stencil(black, pt, 6.2, .55, 2, 1.2, rng, off=.058)

    # ---- coilgun turrets on the rim: a plinth, a domed housing with a cradle, a capacitor bank behind,
    # and twin coil-wound rails pointing outwards over the rotating ring.
    rg, top = 11.9, 1.45
    zg = top + .32
    plinth = a.part('Coilgun_mounts', 'Armor')
    housing = a.part('Coilgun_housings', 'Steel')
    guns = a.part('Miniguns', 'Steel')
    coils = a.part('Coilgun_coils', 'Gilded')
    tips = a.part('Coilgun_glow', 'TeamGlow')
    caps = a.part('Coilgun_capacitors', 'Armor')
    for q in GUN_ANGLES:
        c, s = math.cos(q), math.sin(q)
        lo = _zt(rg + 1.1) - .12
        plinth.cyl(1.1, top - lo, loc=_pol(rg, q, (top + lo) / 2), seg=14, bevel=0)
        housing.sphere((.94, .94, .55), loc=_pol(rg, q, top - .02), seg=14, rings=6, cut=0)
        housing.box((1.15, 1.3, .55), loc=_pol(rg + .2, q, zg), rot=(0, 0, q), bevel=.1, seg=1)
        caps.box((.78, .9, .46), loc=_pol(rg - .8, q, top + .12), rot=(0, 0, q), bevel=.06, seg=1)
        a.part('Coilgun_marks', 'Hazard').box((.08, .92, .24), loc=_pol(rg - 1.2, q, top + .12), rot=(0, 0, q),
                                             bevel=0)
        for side in (-1, 1):
            o = Vector((-s, c, 0)) * .27 * side
            p0, p1 = Vector(_pol(rg + .5, q, zg)) + o, Vector(_pol(15.4, q, zg)) + o
            # Stations every 0.3 m: the runtime groups launcher vertices across the model by x with
            # 0.35 m gaps, so each turret's rails must not break into pieces.
            guns.tube([tuple(p0 + (p1 - p0) * i / 10) for i in range(11)], .085, seg=5)
            for i in range(4):
                p = p0 + (p1 - p0) * (.2 + i * .17)
                coils.cyl(.16, .17, loc=tuple(p), rot=(0, R90, q), seg=6, bevel=0)
            tips.cyl(.1, .05, loc=tuple(p1 + (p1 - p0).normalized() * .01), rot=(0, R90, q), seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, 0, zg))

    # ---- point-defence flak on the upper deck behind the canopy, on its own mount.
    yf = 6.4
    zf = _zt(yf)
    base_lo = _zt(yf + 1.05) - .1
    armor.cyl(1.05, zf + .26 - base_lo, loc=(0, yf, (zf + .26 + base_lo) / 2), seg=18, bevel=.04, bseg=1)
    m = a.pivot('Mount_mg', (0, yf, zf + .26))
    fb = a.part('Flak_body', 'Steel', m)
    fb.cyl(.9, .22, loc=(0, 0, .1), seg=18, bevel=.04, bseg=1)
    fb.box((1.3, 1.25, .62), loc=(0, .1, .5), bevel=.08, seg=1, taper=(.82, .88))
    a.part('Flak_shield', 'Armor', m).box((1.6, .1, .72), loc=(0, -.58, .52), rot=(-.28, 0, 0), bevel=.025, seg=1,
                                           taper=(.84, 1))
    a.part('Flak_sight', 'Glass', m).box((.24, .12, .14), loc=(.42, -.6, .82), rot=(-.28, 0, 0), bevel=0)
    fg = a.part('Flak_guns', 'Steel', m)
    for x in (-.24, .24):
        for z in (.4, .64):
            fg.cyl(.045, 1.9, loc=(x, -1.45, z), rot=FORWARD, seg=6, bevel=0)
            fg.cyl(.07, .22, loc=(x, -2.36, z), rot=FORWARD, seg=6, bevel=0)
    for sx in (-1, 1):
        a.part('Flak_drums', 'Armor', m).cyl(.26, .3, loc=(sx * .78, .15, .55), rot=(0, R90, 0), seg=12, bevel=.03,
                                             bseg=1)
    a.pivot('Muzzle_mg', (0, -2.5, .52), m)

    # ---- markings: star-and-bar insignia left and right, USAF lettering at the front, a walkway,
    # stencils and nav lights (red on the left, green on the right, white at the tail).
    for q in (0.0, math.pi):
        _insignia(a, _plane(10.95, q), size=1.2, up=0.0)
    _lettering(team, lambda u, v: (u, v), 'USAF', -2.05, -10.35, 1.15)
    wq = math.radians(315)
    wp = _plane(0, wq)
    _strip(a.part('Walkway', 'Armor'), wp, 5.35, 9.3, -.5, .5, step=.7)
    for v in (-.55, .55):
        _strip(black, wp, 5.3, 9.35, v - .05, v + .05, step=.7)
    for u in (5.3, 9.35):
        _strip(black, wp, u - .05, u + .05, -.5, .5, off=.058)
    _stencil(black, wp, 6.2, 1.0, 1, .8, rng)
    _stencil(black, wp, 6.2, -.8, 1, .8, rng)
    for q in RAD_ANGLES:
        pt = _plane(0, q)
        _stencil(black, pt, 7.0, 1.55, 2, 1.4, rng)
        _stencil(a.part('Warnings', 'Hazard'), pt, 10.6, .5, 1, .9, rng, h=.11)
    for q in (math.radians(160), math.radians(190), math.radians(250)):
        _stencil(black, _plane(0, q), 11.2, .3, 2, 1.0, rng)
    for name, mat, q in (('Nav_red', 'LavaGlow', 0.0), ('Nav_green', 'SignalGreen', math.pi),
                         ('Tail_light', 'Lamp', R90)):
        m = _frame_on(12.95, q)
        a.part(name, mat).sphere((.32, .26, .11), loc=tuple(m.translation), rot=tuple(m.to_euler('XYZ')), seg=10,
                                 rings=6)

    # ---- instrumentation boom at the front (1950s test aircraft), over the rotating ring.
    m = _frame_on(11.7, -R90)
    _fbox(steel, m, (2.4, .7, .5), loc=(0, 0, .02), bevel=.14, seg=2, taper=(.8, .7))
    zb0 = 1.0
    steel.cyl(.12, 5.2, r2=.07, loc=(0, -14.8, zb0), rot=FORWARD, seg=10, bevel=0)
    steel.limb((0, -11.6, _zt(11.6)), (0, -12.4, zb0), .2, .3, bevel=.04, seg=1)
    steel.cyl(.07, .6, r2=.02, loc=(0, -17.65, zb0), rot=FORWARD, seg=8, bevel=0)
    for y in (-13.6, -14.8, -16.0):
        team.cyl(.13, .5, loc=(0, y, zb0), rot=FORWARD, seg=10, bevel=0)
    for side in (-1, 1):
        armor.box((.03, .22, .14), loc=(side * .1, -17.0, zb0), bevel=0)
    armor.box((.22, .22, .03), loc=(0, -16.7, zb0 + .1), bevel=0)

    # ---- antenna whips and blade aerials.
    whip = a.part('Antennas', 'Steel')
    rake = .14
    for q, r, h in ((0.0, 6.2, 2.8), (math.pi, 6.2, 2.8), (math.radians(100), 11.0, 2.0)):
        x, y = _polar(r, q)
        z = _zt(r)
        armor.cyl(.12, .3, loc=(x, y, z + .1), seg=8, bevel=0)
        whip.cyl(.025, h, loc=(x, y + math.sin(rake) * h / 2, z + .2 + math.cos(rake) * h / 2), rot=(-rake, 0, 0),
                 seg=5, bevel=0)
        a.part('Beacon', 'TeamGlow').sphere(.06, loc=(x, y + math.sin(rake) * h, z + .2 + h * math.cos(rake)), seg=6,
                                            rings=4)
    for q in (math.radians(135), math.radians(45)):
        x, y = _polar(7.0, q)
        steel.box((.04, .5, .34), loc=(x, y, _zt(7.0) + .15), rot=(-.35, 0, q), bevel=0, taper=(1, .5))

    # ---- underside: ventral hub, ball-turret bay, landing-gear fairings, drone bay, aerials.
    _revolve(armor, [(1.38, Z_HUB + .02), (2.05, Z_HUB + .02), (2.05, Z_HUB - .08), (1.38, Z_HUB - .08)], (0, 0, 0),
             (0, 0, 0), seg=40)
    _flat_rivets(rivet, [(2.35 * math.cos(q), 2.35 * math.sin(q), Z_HUB) for q in (i * TAU / 36 for i in range(36))],
                 down=True)
    _revolve(sheet, [(3.0, Z_HUB + .02), (4.2, Z_HUB + .02), (4.2, Z_HUB - .03), (3.0, Z_HUB - .03)], (0, 0, 0),
             (0, 0, 0), seg=40)
    fair = a.part('Gear_fairings', 'Steel')
    pads = a.part('Gear_pads', 'Undercarriage')
    for q in (math.radians(270), math.radians(30), math.radians(150)):
        m = _frame_on(8.4, q, lower=True)
        e = tuple(m.to_euler('XYZ'))
        fair.sphere((2.0, .95, .62), loc=tuple(m @ Vector((0, 0, .02))), rot=e, seg=12, rings=8)
        _fcyl(pads, m, .55, .1, loc=(.3, 0, .6), bevel=0, seg=14)
        for sy in (-1, 1):                                                                    # door seams
            pts = []
            for x in _lin(-1.75, 1.75, 6):
                k = 1 - (x / 2.0) ** 2 - (.45 / .95) ** 2
                pts.append(tuple(m @ Vector((x, sy * .45, .02 + .62 * math.sqrt(max(0.0, k)) + .008))))
            dark.tube(pts, .022, seg=4)
    # Drone bay under the rear: a shallow housing, dark opening, open doors, hazard sills, drones.
    m = _frame_on(7.6, R90, lower=True)
    e = tuple(m.to_euler('XYZ'))
    bay = a.part('Bay', 'MetalSheet')
    bay.box((4.6, 3.8, .8), loc=tuple(m @ Vector((0, 0, .05))), rot=e, bevel=.1, seg=2)
    _fbox(dark, m, (4.0, 3.1, .04), loc=(0, 0, .45), bevel=0)
    sills = a.part('Bay_sills', 'Hazard')
    for sy in (-1, 1):
        _fbox(sills, m, (4.2, .14, .06), loc=(0, sy * 1.62, .45), bevel=0)
        _fbox(sills, m, (.14, 3.4, .06), loc=(sy * 2.07, 0, .45), bevel=0)
    doors = a.part('Bay_doors', 'Steel')
    for sy in (-1, 1):
        th = .6
        _fbox(doors, m, (3.9, .04, 1.4), loc=(0, sy * (1.6 + .7 * math.sin(th)), .45 + .7 * math.cos(th)),
              rot=(-sy * th, 0, 0), bevel=.01, seg=1)
    racks = a.part('Bay_racks', 'Steel')
    _fbox(racks, m, (3.7, .1, .08), loc=(0, 0, .5), bevel=0)
    for i, x in enumerate((-.8, .8)):
        p = m @ Vector((x, 0, .62))
        _fpv_drone(a, p.x, p.y, p.z, i)
    a.pivot('Muzzle_missile', tuple(m @ Vector((0, 0, .9))))
    # Lower markings and aerials.
    _insignia(a, _plane(10.6, 0.0), size=1.1, lower=True, up=0.0, base=.05)
    _lettering(team, lambda u, v: (u, -v), 'USAF', -10.7, -.5, 1.0, off=.05, lower=True)
    for q in (math.radians(250), math.radians(290)):
        x, y = _polar(11.0, q)
        z = _zb(11.0)
        whip.cyl(.025, 1.8, loc=(x, y + .2, z - .85), rot=(-.2, 0, 0), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.12, loc=(0, 4.6, Z_HUB - .06), seg=8, rings=5)

    # ---- ventral ball turret with the laser.
    t = a.pivot('Turret', (0, 0, Z_HUB))
    a.part('Turret_collar', 'Armor', t).cyl(1.34, .16, loc=(0, 0, -.06), seg=24, bevel=.03, bseg=1)
    a.part('Turret_ball', 'Steel', t).sphere(1.06, loc=(0, 0, -.8), seg=20, rings=12)
    ta = a.part('Turret_armor', 'Armor', t)
    ta.box((1.2, .5, 1.0), loc=(0, -.86, -.84), bevel=.08, seg=1)
    for sx in (-1, 1):                                                                        # trunnions
        ta.cyl(.38, .3, loc=(sx * .98, 0, -.8), rot=(0, R90, 0), seg=12, bevel=0)
        ta.cyl(.2, .1, loc=(sx * 1.16, 0, -.8), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Turret_sight', 'Glass', t).box((.22, .06, .16), loc=(.42, -1.12, -.5), bevel=0)
    zc = -.86
    a.part('Main_cannon', 'Steel', t).lathe([(0, .5), (.44, .5), (.44, 2.8), (.62, 2.9), (.62, 3.2), (.5, 3.24),
                                            (.5, 3.2)], loc=(0, 0, zc), rot=FORWARD, seg=20)
    fins = a.part('Main_cannon_fins', 'Armor', t)
    for i in range(6):
        fins.cyl(.72, .05, loc=(0, -(1.15 + i * .27), zc), rot=FORWARD, seg=16, bevel=0)
    for k in range(4):
        q = k * TAU / 4 + TAU / 8
        fins.box((.08, 1.7, .08), loc=(.62 * math.cos(q), -1.87, zc + .62 * math.sin(q)), bevel=0)
    a.part('Main_cannon_lens', 'Glass', t).sphere((.47, .47, .14), loc=(0, -3.2, zc), rot=FORWARD, seg=20, rings=8,
                                                  cut=0)
    a.part('Main_cannon_glow', 'TeamGlow', t).torus(.52, .04, loc=(0, -3.24, zc), rot=FORWARD, seg=20, ring=4)
    a.part('Main_cannon_core', 'TeamGlow', t).cyl(.14, .04, loc=(0, -3.345, zc), rot=FORWARD, seg=12, bevel=0)
    a.pivot('Muzzle_main', (0, -3.45, zc), t)


# name: (builder, Asset options). It flies: no ground occlusion or grime.
BUILDERS = {
    'silver_bug': (silver_bug, dict(ao_distance=.35, ground=False)),
}
