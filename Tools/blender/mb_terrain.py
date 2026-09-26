"""Machine Brigade terrain pieces built with frontier_kit.

Origins sit on the ground at the base centre, +Z up; every piece sinks a few centimetres below
z = 0 so it never floats on uneven ground. Mountains are faceted scenery (a Delaunay-triangulated
height field) whose facets take Rock, Grass, Dirt or Snow from their height and slope. Cliffs,
boulders, sandbags, tank traps and dirt mounds are map obstacles. Rock is recoloured per map at
runtime.
"""
import math
import random

from mathutils import Matrix, Vector, noise
from mathutils.geometry import delaunay_2d_cdt

TAU = math.tau


def _split(a, verts, faces, pick, name, rewind=True):
    """One flat-shaded part per material: pick(centroid, normal) names each facet's material.
    rewind=True turns height-field facets to face up; built solids keep their own winding."""
    groups = {}
    for f in faces:
        p = [Vector(verts[j]) for j in f]
        n = (p[1] - p[0]).cross(p[2] - p[0])
        if n.length < 1e-9:
            continue
        n.normalize()
        f = list(f)
        if rewind and n.z < 0:
            f.reverse()
            n = -n
        groups.setdefault(pick(sum(p, Vector()) / len(p), n), []).append(f)
    for mat in sorted(groups):
        fs = groups[mat]
        used = sorted({j for f in fs for j in f})
        remap = {j: k for k, j in enumerate(used)}
        a.part(f'{name}_{mat}', mat, flat=True).mesh([verts[j] for j in used], [[remap[j] for j in f] for f in fs])


def _centred(verts):
    """Shift verts so the footprint's bounding box is centred on the origin; returns the shift."""
    cx = (min(v[0] for v in verts) + max(v[0] for v in verts)) / 2
    cy = (min(v[1] for v in verts) + max(v[1] for v in verts)) / 2
    return [(x - cx, y - cy, z) for x, y, z in verts], (cx, cy)


def _outline(rng, bumps=((2, 4, .1), (5, 7, .05))):
    """Wobbly closed outline: radius factor as a function of the angle."""
    lobes = [(rng.uniform(amp * .6, amp), rng.randint(k0, k1), rng.uniform(0, TAU)) for k0, k1, amp in bumps]
    return lambda th: 1 + sum(amp * math.sin(k * th + ph) for amp, k, ph in lobes)


def _heightfield(rng, rx, ry, count, height_at, edge, boundary=96, sink=-.5):
    """Jittered hex-grid points inside a wobbly ellipse, Delaunay-triangulated, lifted by
    height_at(u, v, d) (unit coordinates, d = 0 centre .. 1 outline). Returns verts, faces."""
    step = math.sqrt(math.pi / (count * .866))
    pts = []
    n = int(1.2 / step) + 2
    for j in range(-n, n + 1):
        for i in range(-n, n + 1):
            u = (i + .5 * (j % 2) + rng.uniform(-.32, .32)) * step
            v = (j * .866 + rng.uniform(-.28, .28)) * step
            if math.hypot(u, v) < edge(math.atan2(v, u)) * (1 - step * .6):
                pts.append((u, v))
    rim = [(edge(th) * math.cos(th), edge(th) * math.sin(th))
           for th in (k * TAU / boundary + rng.uniform(-.2, .2) * TAU / boundary for k in range(boundary))]
    coords = [Vector((u * rx, v * ry)) for u, v in rim + pts]
    out = delaunay_2d_cdt(coords, [(k, (k + 1) % boundary) for k in range(boundary)], [list(range(boundary))], 1,
                          1e-4, False)
    verts2, faces = out[0], out[2]
    verts = []
    for p in verts2:
        u, v = p.x / rx, p.y / ry
        d = math.hypot(u, v) / edge(math.atan2(v, u))
        verts.append((p.x, p.y, sink if d > .995 else height_at(u, v, d)))
    return verts, [tuple(f) for f in faces]


# ----------------------------------------------------------------------------- mountains
def mountain(a, seed, rx, ry, height, peaks, snow=None, count=1250):
    """peaks: [(u, v, height fraction, spread)] in unit coordinates of the rx x ry footprint.
    Foothills rise from the rim; ridged noise carves ridges and gullies into the peaks. Facet
    materials come from the smooth height field (height, slope and broad noise patches), so
    they form coherent bands instead of per-facet speckles."""
    rng = random.Random(seed)
    edge = _outline(rng)
    off = Vector((seed * 7.13, seed * 3.71, seed * 1.93))

    def shape(u, v, d):
        w = Vector((u, v, 0)) * 1.4 + off
        u2, v2 = u + .1 * noise.noise(w), v + .1 * noise.noise(w + Vector((5.2, 1.3, 0)))
        z = .2 * max(0.0, 1 - d) ** 1.1  # foothills
        for pu, pv, ph, ps in peaks:
            t = math.hypot(u2 - pu, v2 - pv) / ps
            if t < 1:
                z = max(z, ph * (1 - t) ** 1.8)
        ridge = 1 - abs(noise.noise(Vector((u2 * 2.6, v2 * 2.6, seed))))
        z = z * (.74 + .36 * ridge * ridge) + .03 * noise.noise(Vector((u * 6, v * 6, seed + 9))) * (1 - d)
        z += .018 * noise.noise(Vector((u * 23, v * 23, seed + 4))) * (1 - d)  # facet jitter
        return z * (1 - max(0.0, d - .88) / .12)  # meets the ground at the rim

    def height_at(u, v, d):
        return max(.1, height * shape(u, v, d))

    count_now = count
    while True:
        verts, faces = _heightfield(random.Random(seed), rx, ry, count_now, height_at, edge)
        if len(faces) <= 3950:
            break
        count_now = int(count_now * .96)
    k = height / max(v[2] for v in verts)  # exact summit height
    verts, (cx, cy) = _centred([(x, y, z * k if z > 0 else z) for x, y, z in verts])

    def smooth(x, y):
        u, v = (x + cx) / rx, (y + cy) / ry
        return height * k * shape(u, v, min(1.0, math.hypot(u, v) / edge(math.atan2(v, u))))

    def pick(c, n):
        f = c.z / height
        e = 2.5
        slope = math.hypot(smooth(c.x + e, c.y) - smooth(c.x - e, c.y), smooth(c.x, c.y + e) - smooth(c.x, c.y - e))
        slope /= 2 * e
        c = c + Vector((cx, cy, 0))
        q = .08 * noise.noise(c * .035 + off)
        if snow is not None and f > snow + q and slope < 1.6:
            return 'Snow'
        if slope > .78 + q * 3 or f > .46 + q:
            return 'Rock'
        if (slope > .6 + q * 2 or noise.noise(c * .03 + off * 2) > .45) and f > .05:
            return 'Dirt'
        return 'Grass'
    _split(a, verts, faces, pick, 'Mountain')


def mountain_a(a):
    """Tallest (50 m): one dominant snow-capped peak with two shoulders, 114 x 115 m."""
    mountain(a, 3, 56, 52, 50, [(.04, -.06, 1.0, 1.15), (-.42, .34, .62, .7), (.46, .3, .45, .6)], snow=.64)


def mountain_b(a):
    """Twin rocky peaks, 38 m, 91 x 86 m."""
    mountain(a, 11, 48, 42, 38, [(-.3, .12, 1.0, .85), (.3, -.14, .86, .8), (.05, .5, .45, .6)])


def mountain_c(a):
    """Long ridge, 27 m, 116 x 66 m."""
    mountain(a, 23, 57, 33, 27, [(-.5, .05, .78, .7), (-.05, -.05, 1.0, .75), (.45, .1, .72, .7)], count=1150)


# ----------------------------------------------------------------------------- obstacles
def cliff(a, seed, rx, ry, height, segments=28):
    """Rocky outcrop: stacked strata with ledges, a flattish grassy top and scree at its foot."""
    rng = random.Random(seed)
    edge = _outline(rng, ((2, 3, .14), (4, 6, .07)))
    jitter = [rng.uniform(-.06, .06) for _ in range(segments)]
    # (height fraction, inset); pairs at one height make a flat ledge between strata.
    levels = [(-.06, 1.04), (.2, 1.0), (.42, .95), (.42, .88), (.64, .85), (.66, .8), (.66, .76), (.9, .73),
              (1.0, .7), (1.03, .55), (1.06, .3)]
    rings = []
    for k, (f, s) in enumerate(levels):
        ring = []
        for i in range(segments):
            th = i * TAU / segments + (k % 2) * .5 * TAU / segments * .3
            r = s * edge(th) * (1 + jitter[i] + rng.uniform(-.035, .035))
            z = height * f + (rng.uniform(-.12, .12) if 0 < k < len(levels) - 1 else 0)
            ring.append((rx * r * math.cos(th), ry * r * math.sin(th), max(z, -.3) if k == 0 else z))
        rings.append(ring)
    verts, (cx, cy) = _centred([p for ring in rings for p in ring])
    verts.append((-cx, -cy, height * 1.08))
    centre = len(verts) - 1
    faces = []
    for k in range(len(rings) - 1):
        for i in range(segments):
            j = (i + 1) % segments
            a0, a1 = k * segments + i, k * segments + j
            b0, b1 = a0 + segments, a1 + segments
            faces += [(a0, a1, b1), (a0, b1, b0)] if (i + k) % 2 else [(a0, a1, b0), (a1, b1, b0)]
    last = (len(rings) - 1) * segments
    faces += [(last + i, last + (i + 1) % segments, centre) for i in range(segments)]

    def pick(c, n):
        if n.z > .82:
            return 'Grass' if c.z > height * .95 else 'Dirt'
        return 'Rock'
    _split(a, verts, faces, pick, 'Cliff', rewind=False)
    scree = a.part('Scree', 'Rock', flat=True)
    for k in range(5):
        th = rng.uniform(0, TAU)
        r = edge(th) * 1.06
        size = rng.uniform(.45, .85)
        loc = (rx * r * math.cos(th) - cx, ry * r * math.sin(th) - cy, size * .2)
        scree.ico((size * 1.2, size, size * .7), loc=loc, sub=1, jitter=.3, seed=seed + k * 1.7)


def cliff_a(a):
    """13.5 x 10.7 m outcrop, 6.5 m tall."""
    cliff(a, 5, 6.0, 4.6, 6.0)


def cliff_b(a):
    """10 x 9.7 m outcrop, 4.8 m tall."""
    cliff(a, 9, 4.6, 4.0, 4.4)


def boulders(a):
    """Cluster of five faceted rocks about 4 m across."""
    stone = a.part('Rock', 'Rock', flat=True)
    for k, (x, y, r, sub) in enumerate(((0, .1, (1.25, 1.05, .95), 3), (1.3, .7, (.8, .7, .72), 3),
                                        (-1.25, .55, (.7, .65, .55), 2), (.45, -1.2, (.62, .55, .5), 2),
                                        (-.7, -1.0, (.48, .42, .36), 2))):
        stone.ico(r, loc=(x, y, r[2] * .55), sub=sub, jitter=.28, seed=k * 2.3 + .7)


def sandbags(a):
    """4 m curved wall of four courses of sandbags laid in a brick bond, bulging to the front."""
    rng = random.Random(4)
    bags = a.part('Sandbags', 'Sandbag')
    radius, arc = 3.4, 4.0 / 3.4
    length, depth, tall = .56, .36, .2
    for row in range(4):
        count = 8 if row % 2 == 0 else 7
        for i in range(count):
            th = ((i + (.5 if row % 2 == 0 else 1.0)) / 8 - .5) * arc
            x, y = radius * math.sin(th), radius * (1 - math.cos(th)) - radius * (1 - math.cos(arc / 2)) / 2
            z = tall / 2 - .02 + row * (tall - .025)
            bags.box((length * rng.uniform(.94, 1.04), depth * rng.uniform(.95, 1.05), tall), loc=(x, y, z),
                     rot=(rng.uniform(-.04, .04), rng.uniform(-.05, .05), th + rng.uniform(-.06, .06)),
                     bevel=.07, seg=1, taper=(.9, .86))


def tank_trap(a):
    """Czech hedgehog: three steel angle beams crossing at the centre, standing on three feet."""
    beams = a.part('Hedgehog', 'Armor')
    angle = [(-.1, -.1), (.1, -.1), (.1, -.064), (-.064, -.064), (-.064, .1), (-.1, .1)]
    tilt = Vector((1, 1, 1)).normalized().rotation_difference(Vector((0, 0, 1))).to_matrix()
    for k, axis in enumerate(((1, 0, 0), (0, 1, 0), (0, 0, 1))):
        d = tilt @ Vector(axis)
        m = Vector((0, 0, 1)).rotation_difference(d).to_matrix() @ Matrix.Rotation(k * TAU / 3, 3, 'Z')
        beams.prism(angle, 1.9, axis='Z', rot=m.to_euler('XYZ'), bevel=.012, seg=1)
    plate = a.part('Gusset', 'Armor')
    plate.box((.26, .26, .26), rot=tilt.to_euler('XYZ'), bevel=.03, seg=1)
    lowest = min(v.co.z for sh in (beams, plate) for v in sh.bm.verts)
    for sh in (beams, plate):
        for v in sh.bm.verts:
            v.co.z -= lowest + .02


def dirt_mound(a):
    """Low earth berm about 6 m long with a few grass tufts."""
    rng = random.Random(8)
    edge = _outline(rng, ((2, 3, .08), (4, 5, .05)))

    def height_at(u, v, d):
        return 1.05 * (1 - d * d) ** .8 * (1 + .14 * noise.noise(Vector((u * 3, v * 3, 2.0)))) + .02

    verts, faces = _heightfield(rng, 3.0, 1.35, 110, height_at, edge, boundary=30, sink=-.08)
    _split(a, verts, faces, lambda c, n: 'Dirt', 'Mound')
    tufts = a.part('Tufts', 'Grass', flat=True)
    for k, (x, y) in enumerate(((-1.2, .2), (.3, -.25), (1.5, .15), (-.2, .45))):
        tufts.ico((.3, .26, .18), loc=(x, y, height_at(x / 3, y / 1.35, math.hypot(x / 3, y / 1.35)) - .02), sub=1,
                  jitter=.35, seed=k * 3.1)


# name: (builder, Asset options). Big scenery bakes wide, soft AO.
BUILDERS = {
    'mountain_a': (mountain_a, dict(ao_distance=12.0, ao_strength=.75, grime_height=4.0)),
    'mountain_b': (mountain_b, dict(ao_distance=10.0, ao_strength=.75, grime_height=4.0)),
    'mountain_c': (mountain_c, dict(ao_distance=9.0, ao_strength=.75, grime_height=3.0)),
    'cliff_a': (cliff_a, dict(ao_distance=2.0, grime_height=1.0)),
    'cliff_b': (cliff_b, dict(ao_distance=1.8, grime_height=.9)),
    'boulders': (boulders, dict(ao_distance=1.0, grime_height=.3)),
    'sandbags': (sandbags, dict(ao_distance=.35, grime_height=.25)),
    'tank_trap': (tank_trap, dict(ao_distance=.4, grime_height=.3)),
    'dirt_mound': (dirt_mound, dict(ao_distance=1.2, grime_height=.4)),
}
