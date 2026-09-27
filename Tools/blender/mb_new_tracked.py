"""New Machine Brigade tracked vehicles (round 5), built with frontier_kit.

Conventions and helpers are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front, the
vehicle's left is +X, origin on the ground under the hull centre, turret parts authored relative to
the `Turret` empty. Touching parts overlap or stand at least 1 cm apart, never face to face.

  * turtle_tank: the improvised "turtle" / Tsar Mangal tank: a T-72 hull under a hip-roofed shed
    of corrugated sheets (painted, bare, galvanised and rusted panels, welded patch plates) on an
    angle-iron frame, whose side walls hang past the tracks as skirts with chain and mesh fringes.
    The gun pokes out through a slot in the front slope; openings in the roof and walls show the
    dark inside. Two drone jammers and whip antennas on the roof, and a KMT mine roller (two toothed
    roller gangs on push arms, a dog-bone chain between them) in front. `Turret` is the T-72 turret
    inside the shed (it cannot really turn); `Main_cannon` / `Muzzle_main` are its 125 mm gun and
    `Muzzle_coax` the coaxial machine gun, whose piped barrel pokes out of the slot beside the gun.
    Shed panels are mostly Team (painted sheet) mixed with Armor, Corrugated and Rust.
  * bmpt: BMPT "Terminator" tank support vehicle on a T-72 hull: a low turret with twin 30 mm
    autocannons (`Main_cannon`, `Main_cannon_2`, `Muzzle_main` between the two tips), a coaxial
    machine gun (`Muzzle_coax`) and an armoured ATGM box of two tubes on each turret side, fixed to
    the turret (`Muzzle_missile` centred between the four tube mouths; the tube lips are
    `Launch_tubes`, one group per side). Two 30 mm grenade launchers in armoured sponsons on the
    front fenders are fixed to the hull: `Muzzle_agl_l` (left, +X) and `Muzzle_agl_r` (right, -X),
    each turned a little outwards (the empties carry that yaw). Reactive armour on the glacis and
    skirts, slat armour at the rear of the skirts and a dozer blade under the nose. The ATGM boxes and
    tube parts use names outside ModelLibrary's barrel pattern, so they turn with the turret but do
    not elevate with the cannons.
  * sapper: combat engineer vehicle (Terrier / Kodiak / IMR-3M lineage): an angular armoured hull
    with bolt-on flank plates and a crew cab on the front left, a wide hazard-striped dozer blade on
    push arms and lift rams, an excavator arm along the right side (-X) with its boom rising back to
    the elbow and the stick folded down to a toothed bucket curled in on the rear deck, a small jib
    crane with a hook, a welding kit, spare track links, tool boxes, lane-marking dispensers, a rear
    winch and TeamGlow warning beacons. `Turret` is the cab-roof remote weapon station; its 12.7 mm
    machine gun is `Main_cannon` (with `Muzzle_brake`, so it recoils and elevates) and `Muzzle_main`
    sits at the flash hider.
"""
import math
import random

from mathutils import Vector

from mb_support import _beacon, _plane, _ram, _rod, _stripes
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _barrel, _cable, _coax, _era, _exhaust, _face_frame, _flank,
                         _frame, _glacis, _grille_frame, _hatch, _headlight, _jerrycans, _periscopes, _pick, _rail,
                         _roll, _shovel, _skirt, _slats, _smoke, _sponson_section, _stowage_bin, _taillight,
                         _track_links, _tube_mouth, tracks)

TAU = math.tau


# ----------------------------------------------------------------------------- helpers
class _Face:
    """A planar face: origin o, unit axes u (s) and v (r) in its plane and the normal n on the side
    of `out`. at(s, r, h) is the point s along u, r along v and h out of the face."""

    def __init__(self, o, u, v, out):
        self.o, self.u, self.v = Vector(o), Vector(u).normalized(), Vector(v).normalized()
        n = self.u.cross(self.v).normalized()
        self.n = n if n.dot(Vector(out)) > 0 else -n

    def at(self, s, r, h=0.0):
        return self.o + self.u * s + self.v * r + self.n * h


def _clip(poly, lo, hi, axis=0):
    """Clip a convex polygon [(s, r)...] to lo <= coordinate `axis` <= hi."""
    def cut(pts, keep, edge):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            pin, qin = keep(p), keep(q)
            if pin:
                out.append(p)
            if pin != qin:
                t = (edge - p[axis]) / (q[axis] - p[axis])
                out.append(tuple(p[k] + (q[k] - p[k]) * t for k in range(2)))
        return out
    poly = cut(poly, lambda p: p[axis] >= lo - 1e-9, lo)
    return cut(poly, lambda p: p[axis] <= hi + 1e-9, hi) if len(poly) >= 3 else []


def _span(poly, s):
    """The r range of a convex (s, r) polygon along the line s = const, or None."""
    rs = []
    for i in range(len(poly)):
        (s0, r0), (s1, r1) = poly[i], poly[(i + 1) % len(poly)]
        if s0 != s1 and min(s0, s1) - 1e-9 <= s <= max(s0, s1) + 1e-9:
            rs.append(r0 + (r1 - r0) * (s - s0) / (s1 - s0))
    return (min(rs), max(rs)) if len(rs) >= 2 else None


def _slab(part, f, poly, h0, h1):
    """Plate over the convex (s, r) polygon of face f, from h0 to h1 out of the face."""
    part.loft([[tuple(f.at(s, r, h0)) for s, r in poly], [tuple(f.at(s, r, h1)) for s, r in poly]])


def _sheet(a, f, poly, mat, pitch=.24, lift=0.0, t=.03, rib=(.12, .05), ribs=True):
    """Corrugated sheet on face f: a slab `t` thick over the convex (s, r) polygon, `lift` off the
    face, with triangular ribs every `pitch` running along r (they sink 8 mm into the slab)."""
    if len(poly) < 3:
        return
    _slab(a.part(f'Shed_{mat}', mat), f, poly, lift, lift + t)
    if not ribs:
        return
    part = a.part(f'Shed_ribs_{mat}', mat)
    w, h = rib
    base = lift + t
    s_lo, s_hi = min(p[0] for p in poly), max(p[0] for p in poly)
    count = max(1, int((s_hi - s_lo - w) / pitch))
    start = (s_lo + s_hi) / 2 - (count - 1) * pitch / 2
    for i in range(count):
        s = start + i * pitch
        lo = _span(poly, s - w / 2)
        hi = _span(poly, s + w / 2)
        if not lo or not hi:
            continue
        r0, r1 = max(lo[0], hi[0]) + .04, min(lo[1], hi[1]) - .04
        if r1 - r0 < .12:
            continue

        def ring(r):
            return [tuple(f.at(s - w / 2, r, base - .008)), tuple(f.at(s + w / 2, r, base - .008)),
                    tuple(f.at(s, r, base + h))]
        part.loft([ring(r0), ring(r1)])


def _patch(a, f, c, size, lift, mat='Rust', seed=0, name='Shed_patches'):
    """Welded patch plate: an irregular four- or five-sided plate about `size` (s, r) across, centred
    on c and turned a little."""
    rng = random.Random(seed)
    n = rng.choice((4, 5))
    turn = rng.uniform(-.5, .5)
    pts = []
    for k in range(n):
        ang = turn + k * TAU / n + rng.uniform(-.3, .3)
        k_r = rng.uniform(.8, 1.0)
        pts.append((c[0] + math.cos(ang) * size[0] / 2 * k_r, c[1] + math.sin(ang) * size[1] / 2 * k_r))
    _slab(a.part(f'{name}_{mat}', mat), f, pts, lift, lift + .015)


def _beam(part, p0, p1, w=.08, d=None):
    """Angle-iron / box beam from p0 to p1."""
    part.limb(tuple(p0), tuple(p1), w, d or w, bevel=0)


def _toothed_disc(part, x, y, z, r, width, teeth=10, depth=.07):
    """Heavy mine-roller disc across X with a serrated rim."""
    pts = []
    for k in range(teeth * 2):
        ang = k * TAU / (teeth * 2)
        rr = r if k % 2 == 0 else r - depth
        pts.append((math.cos(ang) * rr, math.sin(ang) * rr))
    part.prism(pts, width, loc=(x, y, z), axis='X', bevel=0)


# ----------------------------------------------------------------------------- turtle tank
# Shed: side walls at |x| = XE from ZS up to the eaves at ZE, hip roof up to a flat top (|x| <= XT, ZT).
XE, ZS, ZE, XT, ZT = 1.8, .8, 1.66, .95, 2.95
YFE, YFT, YRE, YRT = -3.32, -2.15, 3.55, 3.0          # front / rear eave and top edges


def _shed(a):
    rng = random.Random(7)
    mats = ['Team', 'Team', 'Armor', 'Team', 'Corrugated', 'Rust', 'Team', 'Armor', 'Rust', 'Team', 'Corrugated']
    pick = iter(mats * 8)
    trim = a.part('Shed_frame', 'Armor')
    patches = []
    L = math.hypot(XE - XT, ZT - ZE)                  # side slope length
    LF = math.hypot(YFT - YFE, ZT - ZE)               # front slope length
    LR = math.hypot(YRE - YRT, ZT - ZE)               # rear slope length

    for s in (-1, 1):
        # Side slope: s along Y (front to rear), r up the slope from the eave. Two rows of sheets, a
        # couple of openings.
        side = _Face((s * XE, 0, ZE), (0, 1, 0), (s * (XT - XE), 0, ZT - ZE), (s, 0, 1))
        roof = [(YFE, 0), (YRE, 0), (YRT, L), (YFT, L)]
        mid = L * .52
        rows = ((0, mid - .02, [YFE, -2.05, -.75, .55, 1.85, YRE]),
                (mid + .02, L, [YFE, -1.35, -.05, 1.3, 2.3, YRE]))
        for k, (r0, r1, cuts) in enumerate(rows):
            band = _clip(roof, r0, r1, axis=1)
            for i in range(len(cuts) - 1):
                poly = _clip(band, cuts[i] + .01, cuts[i + 1] - .01)
                if (s, k, i) in ((1, 0, 1), (-1, 0, 3)):         # openings: driver's side window, engine vent
                    hole = (cuts[i] + .25, cuts[i + 1] - .25, .18, mid - .14)
                    for piece in (_clip(poly, -9, hole[0]), _clip(poly, hole[1], 9),
                                  _clip(_clip(poly, hole[0], hole[1]), -9, hole[2], axis=1),
                                  _clip(_clip(poly, hole[0], hole[1]), hole[3], 9, axis=1)):
                        _sheet(a, side, piece, next(pick), lift=(i % 2) * .012)
                    for p0, p1 in (((hole[0], hole[2]), (hole[1], hole[2])), ((hole[0], hole[3]), (hole[1], hole[3])),
                                   ((hole[0], hole[2]), (hole[0], hole[3])), ((hole[1], hole[2]), (hole[1], hole[3]))):
                        _beam(trim, side.at(*p0, .08), side.at(*p1, .08), .05)
                    continue
                _sheet(a, side, poly, next(pick), lift=(i % 2) * .012)
                if rng.random() < .45:
                    patches.append((side, poly))
        _beam(trim, side.at(YFE + (YFT - YFE) * mid / L, mid, .09), side.at(YRE - (YRE - YRT) * mid / L, mid, .065),
              .05)                                                                                  # purlin
        # Side wall (skirt) hanging past the tracks: s along Y, r up from the bottom edge.
        wall = _Face((s * XE, 0, ZS), (0, 1, 0), (0, 0, 1), (s, 0, 0))
        cuts = [YFE, -1.95, -.55, .85, 2.2, YRE]
        for i in range(len(cuts) - 1):
            if (s, i) in ((-1, 2), (1, 3)):          # missing sheets: the track's top run shows through
                continue
            _sheet(a, wall, [(cuts[i] + .01, 0), (cuts[i + 1] - .01, 0), (cuts[i + 1] - .01, ZE - ZS - .02),
                             (cuts[i] + .01, ZE - ZS - .02)], next(pick), lift=(i % 2) * .012)
        for y in cuts[1:-1]:                                                    # wall posts
            _beam(trim, (s * (XE + .07), y, ZS - .02), (s * (XE + .07), y, ZE + .02), .06)
        _beam(trim, (s * (XE + .07), YFE, ZS), (s * (XE + .07), YRE, ZS), .06)         # bottom rail
        _beam(trim, (s * (XE + .06), YFE, ZE), (s * (XE + .06), YRE, ZE), .07)          # eave beam
        _beam(trim, (s * (XT + .03), YFT, ZT + .04), (s * (XT + .03), YRT, ZT + .04), .065)   # top edges
        _beam(trim, (s * (XE + .05), YFE - .05, ZE + .02), (s * (XT + .03), YFT - .03, ZT + .04), .065)  # hips
        _beam(trim, (s * (XE + .05), YRE + .05, ZE + .02), (s * (XT + .03), YRT + .03, ZT + .04), .065)
        for y in (YFE, YRE):
            _beam(trim, (s * (XE + .07), y, ZS - .02), (s * (XE + .07), y, ZE + .02), .06)

    # Front slope with the gun slot in the middle, and an apron under the front eave.
    front = _Face((0, YFE, ZE), (1, 0, 0), (0, YFT - YFE, ZT - ZE), (0, -1, 1))
    poly = [(-XE, 0), (XE, 0), (XT, LF), (-XT, LF)]
    slot = (-.3, .3, .62)                           # the slot runs from the eave up to r = .62
    for lo, hi in ((-XE, -.95), (-.95, slot[0]), (slot[1], .95), (.95, XE)):
        piece = _clip(poly, lo + .01, hi - .01)
        _sheet(a, front, piece, next(pick))
        if lo == -.95:
            patches.append((front, piece))
    _sheet(a, front, _clip(_clip(poly, slot[0] + .01, slot[1] - .01), slot[2], 9, axis=1), 'Armor', lift=.012)
    for x in slot[:2]:
        _beam(trim, front.at(x, 0, .06), front.at(x, slot[2], .06), .05)
    _beam(trim, front.at(slot[0], slot[2], .06), front.at(slot[1], slot[2], .06), .05)
    _beam(trim, (-XT, YFT - .03, ZT + .04), (XT, YFT - .03, ZT + .04), .065)
    _beam(trim, (-XE, YFE - .06, ZE + .02), (XE, YFE - .06, ZE + .02), .07)
    apron = _Face((0, YFE, 1.2), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    for lo, hi in ((-XE, -.7), (-.7, .6), (.6, XE)):
        _sheet(a, apron, [(lo + .01, 0), (hi - .01, 0), (hi - .01, ZE - 1.22), (lo + .01, ZE - 1.22)], next(pick),
               lift=.012 if lo == -.7 else 0)
    _beam(trim, (-XE, YFE - .06, 1.2), (XE, YFE - .06, 1.2), .06)

    # Rear slope.
    rear = _Face((0, YRE, ZE), (-1, 0, 0), (0, YRT - YRE, ZT - ZE), (0, 1, 1))
    poly = [(-XE, 0), (XE, 0), (XT, LR), (-XT, LR)]
    for lo, hi in ((-XE, -.4), (-.4, .5), (.5, XE)):
        _sheet(a, rear, _clip(poly, lo + .01, hi - .01), next(pick))
    _beam(trim, (-XT, YRT + .03, ZT + .04), (XT, YRT + .03, ZT + .04), .065)
    _beam(trim, (-XE, YRE + .06, ZE + .02), (XE, YRE + .06, ZE + .02), .07)

    # Flat top: two columns of sheets with ribs across the vehicle; a hatch opening over the
    # commander's cupola (right side).
    top = _Face((0, 0, ZT), (0, 1, 0), (1, 0, 0), (0, 0, 1))
    cuts = [YFT, -1.0, .1, 1.1, YRT]
    for i in range(len(cuts) - 1):
        for lo, hi in ((-XT, 0), (0, XT)):
            poly = [(cuts[i] + .01, lo + .01), (cuts[i + 1] - .01, lo + .01), (cuts[i + 1] - .01, hi - .01),
                    (cuts[i] + .01, hi - .01)]
            if i == 1 and lo < 0:
                hole = (-.25, .65, -.8, -.12)             # (y0, y1, x0, x1)
                for piece in (_clip(poly, -9, hole[0]), _clip(poly, hole[1], 9),
                              _clip(_clip(poly, hole[0], hole[1]), -9, hole[2], axis=1),
                              _clip(_clip(poly, hole[0], hole[1]), hole[3], 9, axis=1)):
                    _sheet(a, top, piece, 'Team', lift=.012)
                for y in hole[:2]:
                    _beam(trim, (hole[2], y, ZT + .08), (hole[3], y, ZT + .08), .05)
                for x in hole[2:]:
                    _beam(trim, (x, hole[0], ZT + .08), (x, hole[1], ZT + .08), .05)
                continue
            _sheet(a, top, poly, next(pick), lift=.012 * ((i + (lo < 0)) % 2))
            if rng.random() < .5:
                patches.append((top, poly))
    _beam(trim, (0, YFT, ZT + .07), (0, YRT, ZT + .07), .05)                 # centre seam

    # Welded patch plates over the ribs, mostly rust, a few bare steel.
    for n, (f, poly) in enumerate(patches):
        s0, s1 = min(p[0] for p in poly), max(p[0] for p in poly)
        span = _span(poly, (s0 + s1) / 2)
        if not span:
            continue
        c = (s0 + (s1 - s0) * rng.uniform(.3, .7), span[0] + (span[1] - span[0]) * rng.uniform(.3, .7))
        size = (min(.75, (s1 - s0) * .6), min(.6, (span[1] - span[0]) * .6))
        _patch(a, f, c, size, .09, mat='Rust' if n % 3 else 'Armor', seed=n)


def _chains(a, x0, x1, y0, y1, z, length, pitch=.3, name='Chains'):
    """A curtain of hanging chains from (x0, y0) to (x1, y1) at height z, about `length` long, every
    other one with a weight at its end."""
    part = a.part(name, 'Undercarriage')
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / pitch))
    for i in range(n + 1):
        k = i / n
        x, y = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        ln = length * (.75 + .25 * math.sin(i * 1.7))
        part.box((.035, .035, ln), loc=(x, y, z - ln / 2), rot=(0, 0, .5), bevel=0)
        if i % 2 == 0:
            part.box((.08, .08, .08), loc=(x, y, z - ln), rot=(0, 0, .6), bevel=0)


def _mesh_curtain(a, face_x, y0, y1, z0, z1, cols, rows, name='Mesh'):
    """Hanging wire mesh at x = face_x between y0..y1 and z0..z1."""
    part = a.part(name, 'Armor')
    for i in range(cols + 1):
        y = y0 + (y1 - y0) * i / cols
        part.box((.02, .025, z1 - z0), loc=(face_x, y, (z0 + z1) / 2), bevel=0)
    for j in range(rows + 1):
        z = z0 + (z1 - z0) * j / rows
        part.box((.02, y1 - y0, .025), loc=(face_x, (y0 + y1) / 2, z), bevel=0)


def _mine_roller(a, y_mount):
    """KMT-7 style mine roller: in front of each track a gang of three heavy toothed discs on an axle,
    held at its ends by a yoke whose two push arms run back to brackets on the lower glacis; a heavy
    cross beam with weights behind the discs and a dog-bone chain between the gangs."""
    frame = a.part('Roller_frame', 'Team')
    dark = a.part('Roller_armor', 'Armor')
    discs = a.part('Roller_discs', 'Armor')
    steel = a.part('Roller_steel', 'Steel')
    ya, r = -5.22, .45                              # axle and disc radius: fronts at y = -5.67
    for s in (-1, 1):
        c = s * 1.3
        for dx in (-.3, 0, .3):
            _toothed_disc(discs, c + dx, ya, r, r, .16, teeth=9, depth=.09)
            steel.cyl(.13, .22, loc=(c + dx, ya, r), rot=ACROSS, seg=8, bevel=0)             # hubs
        steel.cyl(.07, 1.08, loc=(c, ya, r), rot=ACROSS, seg=8, bevel=0)                  # axle
        for dx in (-.52, .52):
            x = c + dx
            dark.box((.1, .34, .3), loc=(x, ya + .02, r + .02), bevel=.02, seg=1)             # axle boxes
            frame.limb((x, ya + .1, r + .1), (x, ya + .75, r + .32), .13, .16, bevel=.015, seg=1)
            xb = s * .95 + (.14 if dx > 0 else -.14)
            frame.limb((x, ya + .7, r + .32), (xb, y_mount - .1, .74), .13, .16, bevel=.015, seg=1)   # push arms
        frame.box((1.2, .26, .22), loc=(c, ya + .72, r + .32), bevel=.02, seg=1)                  # cross beam
        dark.box((.8, .3, .2), loc=(c, ya + .74, r + .52), bevel=.02, seg=1)                      # weights
        steel.box((.1, .1, .08), loc=(c, ya + .74, r + .64), bevel=0)                             # lifting eye
        dark.box((.44, .36, .5), loc=(s * .95, y_mount + .1, .72), bevel=.02, seg=1)             # hull bracket
        steel.cyl(.07, .52, loc=(s * .95, y_mount - .06, .74), rot=ACROSS, seg=8, bevel=0)      # pivot pin
    dark.limb((-1.1, y_mount + .03, .95), (1.1, y_mount + .03, .95), .14, .16, bevel=.015, seg=1)  # mount beam
    link = a.part('Roller_chain', 'Steel')
    pts = [(.72 - 1.44 * k / 8, ya - .05, r - .05 - .26 * math.sin(math.pi * k / 8)) for k in range(9)]
    link.tube(pts, .025, seg=5)
    for p in pts[1:-1]:
        link.box((.1, .05, .05), loc=p, bevel=0)


def turtle_tank(a):
    """The improvised turtle tank (Tsar Mangal lineage): see the module docstring."""
    tracks(a, 1.3, 6.4, .9, .34, 6, .5, belt_width=.58, wheel_seg=10, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    nose, brow = (-3.52, .98), (-2.2, 1.42)
    hull.prism([(-3.3, .55), nose, brow, (3.2, 1.42), (3.42, 1.22), (3.42, .55)], 2.1, bevel=.06)
    # Glacis under the front eave: splash board, headlights; lower glacis: the roller brackets.
    gy, gz, grot = _glacis(nose, brow, .45, .03)
    armor.box((1.8, .08, .16), loc=(0, gy, gz + .06), rot=(grot - R90, 0, 0), bevel=0)
    for s in (-1, 1):
        _headlight(a, s * 1.25, -3.42, 1.02, guard=False)
    # Rear: fuel drums on the tail plate, the unditching log below them, tail lights and tow hooks.
    for s in (-1, 1):
        x = s * .6
        hull.cyl(.27, .9, loc=(x, 3.64, 1.2), rot=ACROSS, seg=12, bevel=.04)
        for dx in (-.3, .3):
            steel.cyl(.282, .05, loc=(x + dx, 3.64, 1.2), rot=ACROSS, seg=12, bevel=0)
        steel.box((.1, .3, .1), loc=(x, 3.52, .95), bevel=0)
        _taillight(a, s * 1.2, 3.42, 1.1)
        steel.box((.16, .2, .14), loc=(s * .75, 3.5, .7), bevel=.02, seg=1)
    a.part('Log', 'Wood').cyl(.13, 2.5, loc=(0, 3.6, .78), rot=ACROSS, seg=10, bevel=.03)
    _mine_roller(a, -3.42)

    _shed(a)
    # Fringes: chains along the front apron and the front of both side walls, wire mesh behind them.
    _chains(a, -XE + .1, XE - .1, YFE - .08, YFE - .08, 1.19, .42, pitch=.3)
    for s in (-1, 1):
        _chains(a, s * (XE + .08), s * (XE + .08), YFE + .1, -1.0, ZS - .03, .36, pitch=.3)
        _mesh_curtain(a, s * (XE + .09), -.6, 3.3, .42, ZS - .02, 9, 2)
    # Roof: a drone jammer box with a cluster of stubby antennas at the front, a jammer mast with
    # panel antennas at the rear, a drone-detector dome and two radio whips with team beacons.
    zt = ZT + .08
    jam = a.part('Jammer', 'Armor')
    jam.box((.66, .44, .3), loc=(.45, -1.5, zt + .12), bevel=.03, seg=1)
    a.part('Jammer_face', 'Glass').box((.4, .02, .12), loc=(.45, -1.73, zt + .14), bevel=0)
    for i in range(3):
        for j in range(2):
            x, y = .25 + i * .2, -1.6 + j * .2
            steel.cyl(.03, .08, loc=(x, y, zt + .29), seg=6, bevel=0)
            a.part('Jammer_whips', 'Rubber').cyl(.022, .55, loc=(x, y, zt + .56), seg=5, bevel=0)
    _cable(a, [(.2, -1.3, zt + .02), (-.2, -.9, zt + .02), (-.4, .9, zt + .02)], r=.018)
    steel.cyl(.05, .7, loc=(.45, 2.1, zt + .35), seg=8, bevel=0)                          # jammer mast
    jam.box((.3, .3, .2), loc=(.45, 2.1, zt + .08), bevel=.02, seg=1)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        a.part('Radomes', 'Fuel').box((.24, .05, .46), loc=(.45 + math.cos(ang) * .16, 2.1 + math.sin(ang) * .16,
                                                             zt + .78), rot=(0, 0, ang + R90), bevel=.015, seg=1)
    jam.cyl(.07, .06, loc=(.45, 2.1, zt + 1.03), seg=8, bevel=0)
    a.part('Radomes', 'Fuel').sphere(.16, loc=(-.45, 1.6, zt + .06), seg=10, rings=6, cut=0)      # detector dome
    jam.cyl(.18, .08, loc=(-.45, 1.6, zt + .03), seg=10, bevel=0)
    _antenna(a, None, -.8, 2.75, zt, 1.5)
    _antenna(a, None, .8, 2.75, zt, 1.2)
    steel.box((.1, .1, .08), loc=(-.8, 2.75, zt + .02), bevel=0)
    steel.box((.1, .1, .08), loc=(.8, 2.75, zt + .02), bevel=0)
    # Bits of stowage on the roof: a rolled tarpaulin and an ammunition box.
    _roll(a, (-.35, -1.55, zt + .12), 1.0, r=.12)
    a.part('Ammo_boxes', 'Crate').box((.5, .3, .24), loc=(-.4, 2.55, zt + .1), bevel=.02, seg=1)

    # The T-72 turret inside the shed; only the gun (through the front slot) and the cupola (under
    # the roof opening) show.
    steel.cyl(1.05, .1, loc=(0, .1, 1.45), seg=16, bevel=.02, bseg=1)
    t = a.pivot('Turret', (0, .1, 1.48))
    a.part('Turret_body', 'Team', t).lathe([(1.08, 0), (1.1, .12), (.98, .42), (.7, .62), (.3, .7), (0, .7)], seg=16)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.6, .4, .44), loc=(0, -1.0, .36), bevel=.04, seg=1)                          # mantlet
    tarm.cyl(.3, .16, loc=(-.45, .2, .72), seg=12, bevel=.02, bseg=1)                      # cupola
    _hatch(a, -.45, .2, .8, .24, parent=t)
    tip = _barrel(a, t, start_y=-1.15, length=4.35, radius=.095, height=.34, brake=(.24, .22, .24),
                  sleeve=(.58, .5, .15), style='collar', bands=(.28, .82))
    a.pivot('Muzzle_main', tip, t)
    # Coaxial machine gun right of the gun, its barrel run out in a pipe so that the muzzle pokes out of
    # the front slot beside the gun (Muzzle_coax), well back from the gun's tip.
    _coax(a, t, -.21, -1.1, .38, length=2.2, housing=.3)
    a.part('Coax_pipe', 'Armor', t).cyl(.045, 1.4, loc=(-.21, -2.6, .38), rot=FORWARD, seg=8, bevel=0)


# ----------------------------------------------------------------------------- BMPT Terminator
def _t72_hull(a, front=-3.38, rear=3.2, drums=True):
    """T-72 lineage hull from y = front to rear: a narrow belly between the tracks and an upper hull as
    wide as the tracks (sponsons over them) with a long upper glacis; fuel drums and the unditching log
    on the tail. Returns (nose, brow) of the upper glacis."""
    tracks(a, 1.3, rear - front - .2, .9, .34, 6, .5, belt_width=.58, wheel_seg=10, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    steel = a.part('Steel', 'Steel')
    hull.prism([(front + .28, .55), (front + .06, 1.04), (rear - .1, 1.04), (rear - .1, .55)], 2.1, bevel=.05)  # belly
    nose, brow = (front, 1.02), (front + 1.31, 1.44)
    hull.prism([(front + .12, .96), nose, brow, (rear - .15, 1.44), (rear, 1.3), (rear, .96)], 3.18, bevel=.06)
    for s in (-1, 1):
        _taillight(a, s * 1.25, rear, 1.2)
        steel.box((.16, .2, .14), loc=(s * .8, rear + .06, .78), bevel=.02, seg=1)             # rear tow hooks
        steel.box((.16, .2, .14), loc=(s * .45, front + .2, .66), bevel=.02, seg=1)            # front tow hooks
        if drums:
            x = s * .62
            hull.cyl(.27, .9, loc=(x, rear + .26, 1.18), rot=ACROSS, seg=12, bevel=.04)
            for dx in (-.3, .3):
                steel.cyl(.282, .05, loc=(x + dx, rear + .26, 1.18), rot=ACROSS, seg=12, bevel=0)
            steel.box((.1, .3, .1), loc=(x, rear + .08, .93), bevel=0)
    if drums:
        a.part('Log', 'Wood').cyl(.13, 2.6, loc=(0, rear + .18, .76), rot=ACROSS, seg=10, bevel=.03)
    return nose, brow


def _agl_sponson(a, s, nose, brow, yaw=.16):
    """Armoured sponson on the front fender of side s carrying a 30 mm AG-17 grenade launcher in a
    ball mount, fixed to the hull and turned `yaw` outwards. Adds Muzzle_agl_l / Muzzle_agl_r."""
    x = s * 1.3
    (y0, z0), (y1, z1) = nose, brow

    def gz(y):
        return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    yf, top = y0 + .6, 1.88
    yr = yf + 1.23
    prof = [(yf, gz(yf) - .03), (y1, z1 - .03), (yr, z1 - .03), (yr, top), (yf + .38, top), (yf, top - .28)]
    a.part('AGL_sponson', 'Team').prism(prof, .52, loc=(x, 0, 0), bevel=.03, seg=1)
    armor = a.part('AGL_armor', 'Armor')
    steel = a.part('AGL_steel', 'Steel')
    armor.box((.56, .1, .06), loc=(x, yr - .3, top + .01), bevel=0)                       # roof hinge strip
    armor.box((.3, .36, .05), loc=(x, yr - .55, top + .02), bevel=.01, seg=1)             # access hatch
    for dy in (-.12, .12):
        steel.box((.04, .06, .04), loc=(x + s * .27, yr - .55 + dy, top - .12), bevel=0)
    # Ball mount in the vertical front face, the launcher's jacket and barrel pointing forward-outward.
    zb = gz(yf) + .2
    armor.sphere(.13, loc=(x, yf - .02, zb), seg=10, rings=6)
    d = Vector((s * math.sin(yaw), -math.cos(yaw), 0))
    rot = (R90, 0, s * yaw)
    base = Vector((x, yf - .08, zb))
    steel.cyl(.068, .3, loc=base + d * .15, rot=rot, seg=10, bevel=0)                     # barrel jacket
    a.part('AGL_bands', 'Undercarriage').cyl(.078, .04, loc=base + d * .08, rot=rot, seg=10, bevel=0)
    steel.cyl(.038, .38, loc=base + d * .48, rot=rot, seg=8, bevel=0)                     # barrel
    tip = base + d * .7
    a.part('AGL_muzzle', 'Undercarriage').cyl(.052, .1, loc=tip - d * .05, rot=rot, seg=8, bevel=0)
    m = a.pivot('Muzzle_agl_l' if s > 0 else 'Muzzle_agl_r', tuple(tip))
    a.pivots[m].rotation_euler = (0, 0, s * yaw)
    # Headlight under the ball mount, a sensor window above it.
    a.part('Lamps', 'Lamp').box((.16, .03, .08), loc=(x - s * .14, yf - .015, gz(yf) + .06), bevel=0)
    a.part('Light_housing', 'Armor').box((.22, .08, .12), loc=(x - s * .14, yf + .02, gz(yf) + .06), bevel=0)
    a.part('Vision_blocks', 'Glass').box((.14, .05, .07), loc=(x + s * .1, yf + .19, top - .13),
                                         rot=(-.6, 0, 0), bevel=0)


def bmpt(a):
    """BMPT Terminator tank support vehicle: see the module docstring."""
    nose, brow = _t72_hull(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    era = a.part('Hull_ERA', 'Armor')
    # Glacis: two rows of wedge reactive-armour blocks; the grenade-launcher sponsons at its corners.
    for row, u in enumerate((.24, .66)):
        gy, gz, grot = _glacis(nose, brow, u, .05)
        for x in ((-1.25, -.75, -.25, .25, .75, 1.25) if row == 0 else (-.75, -.25, .25, .75)):
            era.box((.46, .42, .12), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0, taper=(1, .7))
    for s in (-1, 1):
        _agl_sponson(a, s, nose, brow)
    # Dozer blade across the nose, below the glacis, on two arms into the lower hull.
    ny = nose[0] + 3.56                                                     # blade profile authored at -3.56
    blade = [(y + ny, z) for y, z in ((-3.84, .3), (-3.74, .46), (-3.7, .64), (-3.72, .84), (-3.78, .96),
                                      (-3.7, .98), (-3.62, .84), (-3.6, .64), (-3.64, .44), (-3.74, .3))]
    a.part('Blade', 'Team').prism(blade, 2.9, bevel=.015)
    steel.box((2.92, .1, .07), loc=(0, -3.83 + ny, .31), rot=(.5, 0, 0), bevel=0)             # cutting edge
    for x in (-1.1, -.37, .37, 1.1):
        armor.prism([(y + ny, z) for y, z in ((-3.66, .36), (-3.62, .64), (-3.64, .86), (-3.5, .84), (-3.44, .5))],
                    .06, loc=(x, 0, 0), bevel=0)                                              # back ribs
    for s in (-1, 1):
        armor.limb((s * .7, -3.62 + ny, .6), (s * .7, -3.3 + ny, .7), .14, .16, bevel=0)     # blade arms
    # Side skirts: reactive armour over the front four panels, slat armour at the rear.
    for s in (-1, 1):
        _skirt(a, s, 1.64, -3.05, 3.05, .6, 1.4, 6, thick=.08, bolts=False)
        step = (3.05 + 3.05 + .035) / 6
        for i in range(4):
            yc = -3.05 + step * (i + .5) - .0175
            for dy in (-.27, .27):
                for z in (.82, 1.18):
                    era.box((.1, .5, .32), loc=(s * 1.72, yc + dy, z), bevel=0)
        _slats(a, _frame((s * 1.79, 2.05, .98), (0, 0, R90)), 1.95, .72, 5)
        for y in (1.2, 2.05, 2.9):
            steel.box((.16, .05, .05), loc=(s * 1.73, y, 1.28), bevel=0)                          # slat brackets
            steel.box((.16, .05, .05), loc=(s * 1.73, y, .7), bevel=0)
        _cable(a, [(s * 1.5, -1.2, 1.465), (s * 1.5, .5, 1.465), (s * 1.48, 2.3, 1.465)])
    # Deck: driver's hatch and vision blocks, engine grilles, fender bins and fuel cells, exhaust.
    _hatch(a, 0, -1.75, 1.43, .25)
    _periscopes(a, [(dx, -2.04, 1.43, 0) for dx in (-.2, 0, .2)])
    for s in (-1, 1):
        deck.grille(.9, .9, loc=(s * .55, 2.2, 1.45), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        _grille_frame(a, s * .55, 2.2, 1.43, .9, .9, t=.04)
    _stowage_bin(a, (-1.32, .9, 1.43), (.36, .95, .28), latch_side=-1)
    _stowage_bin(a, (-1.32, 2.1, 1.43), (.36, 1.1, .28), latch_side=-1)
    for y in (1.2, 1.75):
        a.part('Fuel_cells', 'Team').box((.36, .5, .26), loc=(1.32, y, 1.55), bevel=.03, seg=1)   # below the ATGM sweep
    a.part('Exhaust_louvres', 'Undercarriage').grille(.7, .2, loc=(1.6, 2.45, 1.3), rot=(0, 0, R90), slats=3,
                                                      depth=.05, thickness=.04)
    armor.box((.08, .9, .3), loc=(1.56, 2.45, 1.3), bevel=.015, seg=1)
    _antenna(a, None, -1.3, 2.9, 1.43, 1.2)
    steel.cyl(1.2, .1, loc=(0, .3, 1.47), seg=20, bevel=.02, bseg=1)                          # turret ring

    # Turret: low and wide, the twin-cannon cradle on the roof front, an ATGM box on each side.
    t = a.pivot('Turret', (0, .3, 1.5))
    turret = a.part('Turret_body', 'Team', t)
    H = .5
    outline = [(-.7, -1.28), (.7, -1.28), (1.15, -.76), (1.2, 1.0), (1.0, 1.28), (-1.0, 1.28), (-1.2, 1.0),
               (-1.15, -.76)]
    turret.prism(outline, H, loc=(0, 0, H / 2), axis='Z', bevel=.05, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for b0, b1 in (((.7, -1.28), (1.15, -.76)), ((-1.15, -.76), (-.7, -1.28))):          # cheek ERA
        _era(a, _face_frame(b0, b1, H, .9, u=.5, v=.5), 2, 2, (.22, .19, .08), parent=t, mat='Armor', bevel=0)
    _era(a, _face_frame((-.7, -1.28), (.7, -1.28), H, .9, u=.5, v=.5), 4, 2, (.28, .19, .08), parent=t,
         mat='Armor', bevel=0)
    # Cannon cradle: a raised armoured box whose sloped front carries both barrels and the coax.
    tarm.box((.96, 1.35, .36), loc=(0, -.6, H + .16), bevel=.04, seg=1, taper=(.92, .86), shift=(0, .06))
    tarm.box((.6, .3, .32), loc=(0, -1.24, H + .13), bevel=.03, seg=1)                     # mantlet
    tips = []
    for x, suffix in ((.15, ''), (-.15, '_2')):
        tips.append(_barrel(a, t, start_y=-1.36, length=2.45, radius=.05, height=H + .15, x=x, suffix=suffix,
                            brake=(.11, .24, .11), sleeve=(.1, .55, .085), seg=10, style='flash', bands=(.55,)))
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    _coax(a, t, -.4, -1.22, H + .1, length=.42, housing=.3)
    # ATGM boxes on arms off both sides, two tubes each, fixed to the turret.
    zc, yc, L, xa = .52, -.3, 1.6, 1.47
    for s in (-1, 1):
        tsteel.box((.34, .5, .18), loc=(s * (xa - .23), yc + .1, zc - .05), bevel=.02, seg=1)   # arms
        box = a.part('ATGM_box', 'Team', t)
        box.box((.4, L, .6), loc=(s * xa, yc, zc), bevel=.04, seg=1)
        for dy in (.48, -.22):
            a.part('ATGM_bands', 'Armor', t).box((.43, .1, .63), loc=(s * xa, yc + dy, zc), bevel=0)
        for dz in (-.14, .14):
            _tube_mouth(a, t, _frame((s * xa, yc - L / 2, zc + dz), FORWARD), .11, protrude=.05, seg=10,
                        name='Launch_tubes')
    a.pivot('Muzzle_missile', (0, yc - L / 2 - .05, zc), t)
    # Roof: commander's panoramic sight (right rear), gunner's sight (left), hatches, smoke dischargers,
    # wind sensor, rear bustle box and antennas.
    tsteel.cyl(.14, .3, loc=(-.62, .6, H + .12), seg=10, bevel=.02, bseg=1)
    tarm.box((.42, .42, .32), loc=(-.62, .57, H + .41), bevel=.04, seg=1)
    sight = a.part('Sight', 'Glass', t)
    sight.box((.3, .04, .14), loc=(-.62, .35, H + .43), bevel=.01, seg=1)
    tarm.box((.36, .32, .28), loc=(.7, -.5, H + .1), bevel=.04, seg=1)
    sight.box((.26, .04, .12), loc=(.7, -.67, H + .14), bevel=.01, seg=1)
    _hatch(a, -.62, 0, H - .02, .25, parent=t)
    _hatch(a, .62, .4, H - .02, .25, parent=t)
    _periscopes(a, [(.62, .06, H - .02, 0), (.93, .4, H - .02, R90)], parent=t, size=(.1, .06, .07))
    for s in (-1, 1):
        _smoke(a, tsteel, .88, -1.0, H - .05, s, count=3, gap=.08, r=.045, depth=.15)
        _rail(a, [(s * .9, .25, H - .02), (s * .9, .25, H + .05), (s * .92, .95, H + .05), (s * .92, .95, H - .02)],
              parent=t)
    tsteel.cyl(.02, .3, loc=(.2, .95, H + .12), seg=5, bevel=0)                          # wind sensor
    tsteel.box((.08, .08, .1), loc=(.2, .95, H + .3), bevel=0)
    tarm.box((1.7, .45, .38), loc=(0, 1.43, .24), bevel=.04, seg=1, taper=(.95, .9))       # bustle box
    _roll(a, (0, 1.46, .54), 1.3, r=.1, parent=t)
    _antenna(a, t, -.85, 1.1, H - .02, 1.3)
    _antenna(a, t, .85, 1.1, H - .02, 1.0)


# ----------------------------------------------------------------------------- combat engineer vehicle
def _rws_mg(a, loc, length=1.0):
    """Remote weapon station on the `Turret` pivot at loc: ring, armoured cradle, sensor head and an
    ammunition box that only turn, and a 12.7 mm machine gun (receiver, barrel jacket and barrel as
    `Main_cannon`, flash hider as `Muzzle_brake`) that also elevates and recoils. `Muzzle_main` sits
    at the flash hider's face."""
    t = a.pivot('Turret', loc)
    body = a.part('RWS_body', 'Armor', t)
    a.part('RWS_ring', 'Steel', t).cyl(.3, .08, loc=(0, 0, .03), seg=14, bevel=.015, bseg=1)
    body.box((.42, .56, .22), loc=(0, .05, .17), bevel=.03, seg=1)                     # base
    for s in (-1, 1):
        body.box((.05, .4, .26), loc=(s * .13, -.02, .38), bevel=0)                      # cradle cheeks
    body.box((.24, .3, .26), loc=(.3, .0, .36), bevel=.03, seg=1)                        # sensor head
    a.part('RWS_sensor', 'Glass', t).box((.16, .03, .14), loc=(.3, -.155, .38), bevel=0)
    a.part('RWS_ammo', 'Crate', t).box((.16, .32, .22), loc=(-.26, .06, .33), bevel=.02, seg=1)
    zb = .4
    gun = a.part('Main_cannon', 'Steel', t)
    gun.box((.14, .46, .15), loc=(0, .02, zb), bevel=.02, seg=1)                       # receiver
    gun.box((.1, .2, .03), loc=(0, .0, zb + .085), bevel=0)                             # feed cover
    front = -.21
    gun.cyl(.052, .28, loc=(0, front - .12, zb), rot=FORWARD, seg=10, bevel=0)           # barrel jacket
    gun.cyl(.037, length - .3, loc=(0, front - .24 - (length - .3) / 2 + .02, zb), rot=FORWARD, seg=8, bevel=0)
    tip = front - length
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.052, .12, loc=(0, tip + .06, zb), rot=FORWARD, seg=8,
                                                   bevel=0)
    a.pivot('Muzzle_main', (0, tip, zb), t)
    return t


def _bucket(a, x, y, z, width=.92, f=1):
    """Excavator bucket curled in for travel, hinged at (x, y, z): a J-shaped shell (its caps are the
    side plates) reaching towards -f * Y, a steel lip with five teeth curled back towards +f * Y, hinge
    lugs and pin."""
    pts = [(.04, .08), (-.3, .06), (-.5, -.14), (-.52, -.38), (-.36, -.56), (-.06, -.6), (.1, -.54), (.08, -.46),
           (-.06, -.5), (-.3, -.46), (-.42, -.34), (-.42, -.16), (-.28, -.02), (.02, -.01)]
    prof = [(y + f * dy, z + dz) for dy, dz in pts]
    if f < 0:
        prof.reverse()
    a.part('Bucket', 'Armor').prism(prof, width, loc=(x, 0, 0), bevel=.012, seg=1)
    steel = a.part('Bucket_steel', 'Steel')
    steel.box((width + .02, .1, .05), loc=(x, y + f * .07, z - .5), rot=(f * .4, 0, 0), bevel=0)   # cutting lip
    for k in range(5):
        dx = (k - 2) * width / 5.2
        steel.box((.08, .16, .06), loc=(x + dx, y + f * .16, z - .47), rot=(f * .4, 0, 0), bevel=0)   # teeth
    for side in (-1, 1):
        steel.box((.04, .22, .12), loc=(x + side * .14, y - f * .02, z + .08), bevel=0)           # hinge lugs
    steel.cyl(.05, .4, loc=(x, y, z + .06), rot=ACROSS, seg=8, bevel=0)                         # hinge pin


def sapper(a):
    """Combat engineer vehicle: see the module docstring."""
    tracks(a, 1.32, 6.6, .92, .31, 7, .5, belt_width=.6, wheel_seg=10, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    full = (.5, 1.0, 1.62, 1.02, 1.66, 1.36)
    front, back = (-3.62, 1.14), (-2.55, 1.62)                     # upper glacis (y, z)
    hull.loft([
        _sponson_section(-3.62, .72, 1.0, 1.14, .96, 1.58, 1.3),
        _sponson_section(-2.55, *full),
        _sponson_section(3.2, *full),
        _sponson_section(3.48, .62, 1.0, 1.48, .98, 1.64, 1.32),
    ], bevel=.05, seg=2)
    # Heavy side skirts over the tracks, bolt-on plates on the sloped flanks above them.
    fx, fz, lean = _flank((1.66, 1.08), (1.36, 1.62), .5, .025)
    for s in (-1, 1):
        _skirt(a, s, 1.72, -3.25, 3.3, .56, 1.18, 5, thick=.1, bolts=True)
        for y in (-2.1, -.9, .35, 1.6, 2.75):
            armor.box((.06, 1.1, .4), loc=(s * fx, y, fz), rot=(0, -s * lean, 0), bevel=0)
    # Crew cab on the front left: a steep front plate with vision blocks, inward-sloped sides.
    x0, x1 = -.05, 1.42

    def cab_ring(y, zt, inset):
        return [(x0, y, 1.56), (x1, y, 1.56), (x1 - inset, y, zt), (x0 + inset, y, zt)]
    a.part('Cab', 'Team').loft([cab_ring(-2.56, 1.84, .05), cab_ring(-2.14, 2.44, .15), cab_ring(-.5, 2.44, .15),
                                cab_ring(-.36, 2.32, .1)], bevel=.04, seg=1)
    zr = 2.44
    cab_front = ((-2.56, 1.84), (-2.14, zr))
    gy, gz, grot = _glacis(*cab_front, .62, .012)
    glass = a.part('Vision_blocks', 'Glass')
    for dx in (-.17, 0, .17):
        glass.box((.13, .07, .06), loc=(.95 + dx, gy, gz), rot=(grot, 0, 0), bevel=0)
    glass.box((.3, .07, .08), loc=(.25, gy, gz), rot=(grot, 0, 0), bevel=0)
    for dy in (-1.7, -1.1):                                                                   # side vision blocks
        glass.box((.05, .2, .08), loc=(x1 - .085, dy, 2.18), rot=(0, -.17, 0), bevel=0)
    armor.box((.06, .7, .6), loc=(x1 - .06, -1.3, 1.92), rot=(0, -.17, 0), bevel=0)            # side door
    steel.box((.05, .16, .04), loc=(x1 - .02, -1.05, 1.9), bevel=0)
    _hatch(a, .3, -.85, zr, .25)
    _hatch(a, 1.05, -.85, zr, .23, hinge=-1)
    _periscopes(a, [(.3, -1.95, zr - .01, 0), (1.05, -1.95, zr - .01, 0), (1.25, -1.3, zr - .01, -R90)])
    for x in (.05, 1.3):                                                                      # warning beacons
        _beacon(a, x, -.55, zr - .01, mat='TeamGlow', r=.085)
    lights = a.part('Light_housing', 'Armor')
    for x in (.25, 1.15):                                                                      # work lights
        lights.box((.2, .12, .15), loc=(x, -2.16, zr + .06), bevel=0)
        a.part('Lamps', 'Lamp').box((.15, .03, .1), loc=(x, -2.225, zr + .06), bevel=0)
    for k in range(3):                                                                         # smoke dischargers
        steel.cyl(.045, .16, loc=(1.3 - k * .09, -2.28, 2.36), rot=(.6, 0, .5), seg=8, bevel=0)
        steel.cyl(.045, .16, loc=(.07 + k * .09, -2.28, 2.36), rot=(.6, 0, -.5), seg=8, bevel=0)
    _antenna(a, None, 1.25, -.5, zr - .01, 1.3)
    _rws_mg(a, (.68, -1.45, zr + .01))
    steel.cyl(.33, .05, loc=(.68, -1.45, zr + .005), seg=14, bevel=0)                          # RWS race

    # Glacis: headlights, tow hooks, spare track links on the right.
    for s in (-1, 1):
        gy, gz, grot = _glacis(front, back, .3, .02)
        _headlight(a, s * 1.18, gy - .02, gz + .08, guard=False)
        steel.box((.16, .2, .14), loc=(s * .5, -3.66, .86), bevel=.02, seg=1)
    gy, gz, grot = _glacis(front, back, .55, 0)
    _track_links(a, _frame((-.62, gy, gz), (grot, 0, 0)), 3, width=.46)
    _track_links(a, _frame((.72, gy, gz), (grot, 0, 0)), 2, width=.46)

    # Dozer blade: a wide concave moldboard raised for travel, cutting edge and top lip, end plates and
    # back ribs, push arms into the lower hull and two lift rams from the glacis; hazard band on top.
    by = .1                                                                 # blade profile authored 10 cm forward
    blade = [(y + by, z) for y, z in ((-4.18, .24), (-4.08, .44), (-4.03, .68), (-4.03, .98), (-4.08, 1.18),
                                      (-4.16, 1.3), (-4.06, 1.32), (-3.98, 1.18), (-3.94, .98), (-3.94, .68),
                                      (-3.98, .44), (-4.08, .24))]
    a.part('Blade', 'Team').prism(blade, 3.6, bevel=.015)
    steel.box((3.62, .12, .08), loc=(0, -4.16 + by, .26), rot=(.5, 0, 0), bevel=0)             # cutting edge
    steel.box((3.62, .12, .05), loc=(0, -4.1 + by, 1.31), bevel=0)                              # top lip
    for s in (-1, 1):
        armor.prism([(y + by, z) for y, z in ((-4.21, .22), (-4.12, 1.34), (-3.92, 1.3), (-3.92, .28))], .06,
                    loc=(s * 1.81, 0, 0), bevel=0)                                              # end plates
    for x in (-1.4, -.7, 0, .7, 1.4):                                                           # back ribs
        armor.prism([(y + by, z) for y, z in ((-3.96, .3), (-3.93, .6), (-3.92, .96), (-3.96, 1.2), (-3.8, 1.12),
                                              (-3.78, .4))], .07, loc=(x, 0, 0), bevel=0)
    for s in (-1, 1):
        armor.limb((s * .95, -3.84 + by, .5), (s * .95, -3.3, .64), .16, .18, bevel=0)          # push arms
        armor.box((.24, .3, .3), loc=(s * .95, -3.3, .66), bevel=.02, seg=1)
        _ram(a, (s * .5, -3.25, 1.3), (s * .5, -3.86 + by, 1.1), .07)                         # lift rams
        armor.box((.14, .2, .14), loc=(s * .5, -3.2, 1.33), bevel=0)
    _stripes(a, _plane((0, -4.1 + by, 1.16), (1, 0, 0), (0, .25, 1)), 3.5, .2, pitch=.4)

    # Excavator arm folded along the right side: slewing base at the front right, a bent boom rising back
    # to the elbow on an A-frame rest, the stick folded down behind it and the bucket curled in on the rear
    # deck; boom, stick and bucket rams and hoses.
    ax = -.88
    steel.cyl(.5, .1, loc=(ax, -1.95, 1.64), seg=16, bevel=.02, bseg=1)
    arm = a.part('Arm', 'Team')
    arm.box((.78, .7, .42), loc=(ax, -1.9, 1.88), bevel=.04, seg=1, taper=(.85, .9))            # slewing housing
    for s in (-1, 1):
        armor.box((.06, .42, .36), loc=(ax + s * .2, -1.9, 2.12), bevel=0)                        # foot cheeks
    steel.cyl(.07, .5, loc=(ax, -1.95, 2.18), rot=ACROSS, seg=8, bevel=0)                      # foot pin
    F, K, E = Vector((ax, -1.95, 2.18)), Vector((ax, -.35, 2.92)), Vector((ax, 1.3, 2.88))
    S = Vector((ax, 2.5, 2.32))
    arm.limb(tuple(F), tuple(K), .3, .38, bevel=.03, seg=1)                                     # boom
    arm.limb(tuple(K + Vector((0, -.08, -.02))), tuple(E), .28, .34, bevel=.03, seg=1)
    arm.limb(tuple(E + Vector((0, -.05, .02))), tuple(S), .22, .28, bevel=.025, seg=1)           # stick
    lever = E + Vector((0, -.12, .3))
    armor.limb(tuple(E), tuple(lever), .24, .16, bevel=0)                                        # stick lever
    steel.cyl(.07, .4, loc=E, rot=ACROSS, seg=8, bevel=0)                                        # elbow pin
    steel.cyl(.05, .34, loc=lever, rot=ACROSS, seg=8, bevel=0)
    _bucket(a, ax, S.y, S.z, f=-1)
    for s in (-1, 1):
        _ram(a, (ax + s * .22, -1.55, 1.98), (ax + s * .22, -.9, 2.5), .065)                     # boom rams
    _ram(a, (ax, -.55, 3.08), tuple(lever), .06)                                                 # stick ram
    _ram(a, (ax, 1.45, 3.02), (ax, 2.35, 2.52), .05)                                             # bucket ram
    armor.box((.3, .3, .12), loc=(ax, -.55, 3.04), bevel=0)                                      # ram lug
    hoses = a.part('Hoses', 'Rubber')
    for dx in (-.17, .17):
        hoses.tube([(ax + dx, -1.7, 2.3), (ax + dx, -.35, 3.06), (ax + dx, 1.2, 3.02), (ax + dx, 2.3, 2.46)], .022,
                   seg=4)
    for dx in (-.24, .24):                                                                       # A-frame rest
        armor.limb((ax + dx * 1.4, .45, 1.6), (ax + dx * .5, .45, 2.66), .07, .07, bevel=0)
    armor.box((.4, .16, .06), loc=(ax, .45, 2.68), bevel=0)
    _stripes(a, _plane(K + Vector((0, .5, .17)), (0, 1, -.02), (1, 0, 0)), .9, .3, pitch=.2, lean=.6)

    # Rear deck: welding kit (gas bottles in a rack, a welder box with cable reels) behind the cab, a small
    # jib crane with a hook at the left rear, engine grilles, the recovery winch and tool boxes.
    for x, mat in ((.35, 'Fuel'), (.6, 'Fuel'), (.85, 'BarrelRed')):
        a.part(f'Gas_bottles_{mat}', mat).lathe([(.11, 1.6), (.11, 2.28), (.075, 2.37), (.035, 2.41), (.035, 2.45)],
                                                loc=(x, -.12, 0), seg=8)
        steel.cyl(.045, .06, loc=(x, -.12, 2.47), seg=6, bevel=0)
    for z in (1.85, 2.15):
        steel.box((.78, .03, .05), loc=(.6, -.005, z), bevel=0)
    for x in (.18, 1.02):
        steel.box((.04, .28, .7), loc=(x, -.12, 1.95), bevel=0)
    armor.box((.62, .52, .44), loc=(.72, .62, 1.84), bevel=.03, seg=1)                          # welder
    a.part('Welder_panel', 'Glass').box((.3, .02, .12), loc=(.72, .355, 1.92), bevel=0)
    for dx in (-.16, .16):
        a.part('Cable_reels', 'Rubber').cyl(.15, .12, loc=(.72 + dx, .98, 1.8), rot=ACROSS, seg=10, bevel=0)
    steel.cyl(.04, .44, loc=(.72, .98, 1.8), rot=ACROSS, seg=6, bevel=0)
    a.part('Hoses', 'Rubber').tube([(.72, .36, 1.7), (.6, .1, 1.66), (.5, -.1, 1.66), (.4, -.12, 1.72)], .02,
                                   seg=4)
    for x in (.1, .85):
        deck.grille(.66, .8, loc=(x, 2.05, 1.64), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        _grille_frame(a, x, 2.05, 1.62, .66, .8, t=.04)
    wx, wy = .2, 2.95
    armor.box((1.0, .6, .1), loc=(wx, wy, 1.64), bevel=0)
    for s in (-1, 1):
        armor.box((.08, .5, .5), loc=(wx + s * .46, wy, 1.9), bevel=0)
    a.part('Winch_drum', 'Steel').cyl(.22, .76, loc=(wx, wy, 1.92), rot=ACROSS, seg=12, bevel=0)
    for dx in (-.38, .38):
        a.part('Winch_flanges', 'Armor').cyl(.28, .04, loc=(wx + dx, wy, 1.92), rot=ACROSS, seg=12, bevel=0)
    steel.box((.5, .16, .16), loc=(wx, 3.44, 1.36), bevel=0)                                   # fairlead
    _cable(a, [(wx, wy + .12, 1.72), (wx, 3.4, 1.46), (wx, 3.52, 1.3), (wx, 3.56, 1.1)], r=.028)
    # Jib crane on the left rear corner: post, jib and a hook block on its cable.
    cx, cy = 1.05, 2.9
    crane = a.part('Crane', 'Hazard')
    steel.cyl(.14, .1, loc=(cx, cy, 1.66), seg=10, bevel=0)
    crane.cyl(.09, .9, loc=(cx, cy, 2.1), seg=10, bevel=0)                                     # post
    tipc = Vector((cx + .3, cy + .55, 2.62))
    crane.limb((cx, cy - .05, 2.5), tuple(tipc), .12, .14, bevel=0)                               # jib
    _ram(a, (cx, cy + .02, 1.9), (cx + .17, cy + .36, 2.47), .04)
    steel.cyl(.07, .1, loc=tipc + Vector((0, 0, -.06)), rot=ACROSS, seg=8, bevel=0)             # sheave
    _rod(steel, tipc + Vector((0, .04, -.1)), tipc + Vector((0, .04, -.62)), .012, seg=4)
    a.part('Hook_block', 'Hazard').box((.14, .1, .14), loc=tipc + Vector((0, .04, -.68)), bevel=0)
    steel.torus(.05, .014, loc=tipc + Vector((0, .04, -.8)), rot=(0, R90, 0), seg=8, ring=4)
    _beacon(a, cx, cy, 2.55, mat='TeamGlow', r=.07)
    # Lane-marking dispensers at the rear corners.
    for x in (-1.22, 1.3):
        a.part('Lane_markers', 'Hazard').cyl(.1, .42, loc=(x, 3.28, 1.8), seg=10, bevel=0)
        for dx in (-.04, .04):
            steel.cyl(.012, .5, loc=(x + dx, 3.28, 2.2), seg=4, bevel=0)
    # Right side: a tool box in front of the bucket and a tool chest; left edge: jerrycans, shovel and pick;
    # tow cables.
    _stowage_bin(a, (-1.12, 1.2, 1.61), (.34, .8, .3), latch_side=-1)
    a.part('Tool_chest', 'Crate').box((.52, .62, .34), loc=(-.28, 1.1, 1.78), bevel=.02, seg=1)
    steel.box((.3, .04, .04), loc=(-.28, .78, 1.88), bevel=0)
    _jerrycans(a, (1.2, 1.25, 1.61), 3)
    _shovel(a, (1.2, .1, 1.64), length=1.0)
    _pick(a, (-1.2, -.2, 1.645), length=.9)
    for s in (-1, 1):
        _cable(a, [(s * 1.3, -2.3, 1.645), (s * 1.3, -.5, 1.645), (s * 1.3, .6, 1.645)])
        _taillight(a, s * 1.2, 3.48, 1.3)
        steel.box((.16, .2, .14), loc=(s * .75, 3.54, .82), bevel=.02, seg=1)                  # rear tow hooks
        _exhaust(a, s * .7, 3.48, 1.02, .34, .2)
    # Spare track links on the rear plate.
    _track_links(a, _frame((0, 3.5, 1.02), (-R90, 0, 0)), 3, width=.42)


BUILDERS = {
    'turtle_tank': (turtle_tank, dict(ao_distance=.6, grime_height=.55)),
    'bmpt': (bmpt, dict(ao_distance=.6, grime_height=.55)),
    'sapper': (sapper, dict(ao_distance=.6, grime_height=.55)),
}
