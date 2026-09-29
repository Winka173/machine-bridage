"""The shape of each battlefield: an outline inside the 160 m square, so no two maps are the same
box. Outside it is terrain (cliffs, mountains, forest, water) that nothing drives on.

The outline is carved in from the square's edge: a thin irregular strip everywhere, plus deeper
bites designed per map (a valley between two flanking ridges, a coast, a canyon), all
roughened by noise. It is carved point-symmetrically (the camps sit in opposite corners, so both
sides get the same ground) and never into anything the battle needs: the camps, objectives,
roads, buildings and other blocking props, map units, and every campaign mission's routes,
spawns and units on that map. Decoration left outside (trees, rocks, bushes) is dropped; the
terrain replaces it.

    carve(map_id, keep) -> [(x, z), ...]   the outline, counter-clockwise, in metres
"""
import math

# The battlefield is 300 m across; SHAPES are written for the 160 m design grid and scaled by SCALE.
SCALE = 1.875
DEPTH = 1.5
HALF = 80.0 * SCALE
RES = 1.0   # carving grid, metres
N = int(HALF * 2 / RES)

# Per map: (base strip depth, noise depth, noise scale, [(angle in degrees, depth, width in degrees[, 'force']), ...]).
# Angles are measured anticlockwise from +x (east); 90 is north. Each bite is mirrored through
# the centre automatically. The camps are at 225 (south-west) and 45 (north-east). A forced bite
# may take buildings and roads with it (a dense town or port would otherwise stay a square);
# the camps, objectives, campaign routes and units are protected everywhere.
SHAPES = {
    # A town in rolling country: the flanks fall away to woods.
    'ashfield':   (4.0, 7.0, 22.0, [(135, 30, 26), (100, 12, 12), (170, 12, 12)]),
    # A desert basin: broad bays of dune and mesa on every side.
    'dunebreak':  (5.0, 10.0, 26.0, [(135, 26, 34), (0, 18, 18), (90, 18, 18)]),
    # A valley between two mountain flanks, running from camp to camp.
    'frostpeak':  (4.0, 8.0, 18.0, [(128, 34, 20), (160, 24, 16), (95, 22, 14)]),
    # A port: inlets bite into the flanks, quay walls straight.
    'ironport':   (3.0, 4.0, 30.0, [(135, 28, 18, 'force'), (10, 20, 9, 'force')]),
    # A canyon: the rim closes in on the lanes from north and south.
    'redrock':    (5.0, 9.0, 16.0, [(135, 28, 18), (105, 24, 12), (160, 24, 12)]),
    # A forest pass pinched in the middle of each flank.
    'whiteout':   (5.0, 8.0, 18.0, [(135, 34, 16), (112, 18, 10), (158, 18, 10)]),
    # Farmland in a river bend: long gentle bays.
    'greenvale':  (4.0, 6.0, 30.0, [(135, 22, 40), (80, 12, 14)]),
    # Ruined works on a spit: jagged edges.
    'rustyard':   (3.0, 9.0, 12.0, [(135, 30, 20, 'force'), (180, 16, 9, 'force')]),
    # A lava field in a crater: rounded, with lava bays.
    'emberridge': (6.0, 8.0, 20.0, [(135, 30, 30), (90, 16, 16), (0, 16, 16)]),
    # A jungle gorge: steep, irregular walls.
    'junglepass': (5.0, 11.0, 14.0, [(135, 30, 22), (100, 16, 10), (170, 16, 10)]),
    # An airbase: a fenced plateau, clean straight edges, trimmed corners.
    'skyhold':    (3.0, 3.0, 40.0, [(135, 24, 14, 'force'), (100, 10, 8)]),
    # A city on a river: the embankment cuts deep into two corners.
    'metrocity':  (3.0, 3.0, 40.0, [(135, 36, 16, 'force'), (170, 14, 8, 'force')]),
    # Round 4M. A beach under bluffs: the sea's edge left alone, the headlands trimmed.
    'landingbeach': (3.0, 5.0, 26.0, [(0, 16, 12), (160, 20, 14)]),
    # A dammed valley: steep sides trimmed in on both flanks.
    'hydrodam':   (4.0, 7.0, 20.0, [(160, 22, 16), (20, 18, 14)]),
    # A capital: the city goes on past the edge; the embankments cut in on the flanks.
    'capital':    (3.0, 3.0, 40.0, [(165, 30, 12, 'force'), (80, 12, 10)]),
    # A launch complex in the desert: dunes and mesas close in on the flanks outside the fence.
    'launchsite': (5.0, 8.0, 22.0, [(135, 24, 22), (0, 14, 12), (90, 14, 12)]),
    # A border river: wooded hills trim the corners by the camps and the flanks beyond the detours.
    'borderbridge': (4.0, 6.0, 24.0, [(135, 26, 22), (90, 12, 14)]),
    # A swamp: the jungle closes in on every side, deepest round the camps' corners.
    'swamp':      (5.0, 10.0, 16.0, [(135, 30, 24), (90, 14, 12), (0, 14, 12)]),
    # Prompt 16. A rocky coast on the sea: the pine hills close in on the landward corner (the bite's
    # mirror falls in the sea, where build_maps keeps the square's edge: lb_open_sea).
    'lighthousebay': (3.0, 5.0, 24.0, [(135, 22, 22), (180, 10, 10)]),
    # A lagoon: the reef's rim, low and ragged, closes it in.
    'coralisles': (5.0, 9.0, 18.0, [(135, 26, 26), (90, 12, 12), (0, 12, 12)]),
    # Salt flats: the rim of a dry lake, broad shallow bays.
    'saltflat':   (4.0, 6.0, 34.0, [(135, 24, 34), (90, 14, 20), (0, 14, 20)]),
}

KEEP_CAMP = 20.0
KEEP_POINT = 10.0
KEEP_ROAD = 5.0
KEEP_PROP = 4.0
KEEP_UNIT = 8.0
KEEP_ROUTE = 9.0


# ------------------------------------------------------------------------------------ noise
def _hash(ix, iz, seed):
    h = (ix * 374761393 + iz * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def _value(x, z, seed):
    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    sx, sz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a, b = _hash(ix, iz, seed), _hash(ix + 1, iz, seed)
    c, d = _hash(ix, iz + 1, seed), _hash(ix + 1, iz + 1, seed)
    return (a + (b - a) * sx) + ((c + (d - c) * sx) - (a + (b - a) * sx)) * sz


def fbm(x, z, seed):
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for octave in range(4):
        total += amp * _value(x * freq, z * freq, seed + octave * 17)
        norm += amp
        amp *= 0.5
        freq *= 2.1
    return total / norm


# ------------------------------------------------------------------------------------ keep mask
def _cell(x, z):
    return int((x + HALF) / RES), int((z + HALF) / RES)


def _centre(gx, gz):
    return gx * RES - HALF + RES * 0.5, gz * RES - HALF + RES * 0.5


def keep_mask(keep):
    """keep: {'circles': [(x, z, r)], 'rects': [(x0, z0, x1, z1)], 'lines': [(points, half)]}"""
    mask = [[False] * N for _ in range(N)]

    def disc(x, z, r):
        a0, b0 = _cell(x - r, z - r)
        a1, b1 = _cell(x + r, z + r)
        for gz in range(max(0, b0), min(N, b1 + 1)):
            for gx in range(max(0, a0), min(N, a1 + 1)):
                cx, cz = _centre(gx, gz)
                if (cx - x) ** 2 + (cz - z) ** 2 <= r * r:
                    mask[gz][gx] = True

    for x, z, r in keep.get('circles', []):
        disc(x, z, r)
    for x0, z0, x1, z1 in keep.get('rects', []):
        a0, b0 = _cell(x0, z0)
        a1, b1 = _cell(x1, z1)
        for gz in range(max(0, b0), min(N, b1 + 1)):
            for gx in range(max(0, a0), min(N, a1 + 1)):
                mask[gz][gx] = True
    for points, half in keep.get('lines', []):
        for i in range(len(points) - 1):
            (ax, az), (bx, bz) = points[i], points[i + 1]
            steps = max(1, int(math.hypot(bx - ax, bz - az) / 1.5))
            for k in range(steps + 1):
                t = k / steps
                disc(ax + (bx - ax) * t, az + (bz - az) * t, half)
    return mask


# ------------------------------------------------------------------------------------ carving
def carve_mask(map_id, keep, seed):
    base, noise, scale, bites = SHAPES.get(map_id, (4.0, 6.0, 20.0, []))
    # The shapes' features spread with the battlefield; how deep the edge cuts in grows less
    # (DEPTH), so the bays stay bays and never reach what sits near the edge.
    base, noise, scale = base * DEPTH, noise * DEPTH, scale * SCALE
    bites = [(b[0], b[1] * DEPTH, b[2], len(b) > 3 and b[3] == 'force') for b in bites]
    bites = bites + [((a + 180.0) % 360.0, d, w, f) for a, d, w, f in bites]
    core = keep_mask(keep.get('core', {}))
    extra = keep_mask(keep.get('extra', {}))
    k = [[core[z][x] or extra[z][x] for x in range(N)] for z in range(N)]

    def wants(gx, gz):
        """(carve here, and may it take buildings and roads)"""
        x, z = _centre(gx, gz)
        edge = min(HALF - abs(x), HALF - abs(z))
        theta = math.degrees(math.atan2(z, x)) % 360.0
        depth, forced = base, 0.0
        for a, d, w, f in bites:
            delta = (theta - a + 180.0) % 360.0 - 180.0
            bite = d * math.exp(-(delta / w) ** 2)
            depth += bite
            if f:
                forced += bite
        # Symmetric noise, so a bite and its mirror have the same outline.
        n = fbm(x / scale + 50, z / scale + 50, seed) + fbm(-x / scale + 50, -z / scale + 50, seed)
        depth += (n - 1.0) * noise
        return edge < depth, edge < base + forced * 0.95

    carved = [[False] * N for _ in range(N)]
    for gz in range(N):
        for gx in range(N):
            if core[gz][gx]:
                continue
            want, force = wants(gx, gz)
            if not want:
                continue
            if force:
                # A forced bite takes what is here on its own: campaign routes on one side
                # must not stop the matching corner on the other being cut.
                carved[gz][gx] = True
                continue
            mx, mz = N - 1 - gx, N - 1 - gz
            if core[mz][mx] or extra[gz][gx] or extra[mz][mx] or not wants(mx, mz)[0]:
                continue
            carved[gz][gx] = True

    # Round off single-cell spikes and diagonal pinches (majority filter; protected cells stay open).
    for _ in range(2):
        nxt = [row[:] for row in carved]
        for gz in range(N):
            for gx in range(N):
                if core[gz][gx]:
                    nxt[gz][gx] = False
                    continue
                count = 0
                for dz in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, nz = gx + dx, gz + dz
                        count += 1 if (nx < 0 or nz < 0 or nx >= N or nz >= N or carved[nz][nx]) else 0
                nxt[gz][gx] = count >= 5
        carved = nxt
    # Keep one connected battlefield, with no carved pockets inside it.
    open_cells = _largest_region(carved)
    for gz in range(N):
        for gx in range(N):
            carved[gz][gx] = not open_cells[gz][gx]
    return carved


def _largest_region(carved):
    seen = [[False] * N for _ in range(N)]
    best = []
    for sz in range(N):
        for sx in range(N):
            if carved[sz][sx] or seen[sz][sx]:
                continue
            region, todo = [], [(sx, sz)]
            seen[sz][sx] = True
            while todo:
                gx, gz = todo.pop()
                region.append((gx, gz))
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, nz = gx + dx, gz + dz
                    if 0 <= nx < N and 0 <= nz < N and not seen[nz][nx] and not carved[nz][nx]:
                        seen[nz][nx] = True
                        todo.append((nx, nz))
            if len(region) > len(best):
                best = region
    open_cells = [[False] * N for _ in range(N)]
    for gx, gz in best:
        open_cells[gz][gx] = True
    # Fill carved pockets that do not reach the square's edge: those become open ground.
    outside = [[False] * N for _ in range(N)]
    todo = [(gx, gz) for gx in range(N) for gz in (0, N - 1)] + [(gx, gz) for gz in range(N) for gx in (0, N - 1)]
    todo = [(gx, gz) for gx, gz in todo if not open_cells[gz][gx]]
    for gx, gz in todo:
        outside[gz][gx] = True
    while todo:
        gx, gz = todo.pop()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = gx + dx, gz + dz
            if 0 <= nx < N and 0 <= nz < N and not outside[nz][nx] and not open_cells[nz][nx]:
                outside[nz][nx] = True
                todo.append((nx, nz))
    for gz in range(N):
        for gx in range(N):
            if not outside[gz][gx]:
                open_cells[gz][gx] = True
    return open_cells


# ------------------------------------------------------------------------------------ outline
def outline(carved):
    """Traces the open region's boundary along cell edges (counter-clockwise), then simplifies it."""
    def is_open(gx, gz):
        return 0 <= gx < N and 0 <= gz < N and not carved[gz][gx]

    # Directed boundary edges with the open cell on the left, on the corner lattice.
    edges = {}

    def add(a, b):
        edges.setdefault(a, []).append(b)

    for gz in range(N):
        for gx in range(N):
            if not is_open(gx, gz):
                continue
            if not is_open(gx, gz - 1):
                add((gx, gz), (gx + 1, gz))
            if not is_open(gx + 1, gz):
                add((gx + 1, gz), (gx + 1, gz + 1))
            if not is_open(gx, gz + 1):
                add((gx + 1, gz + 1), (gx, gz + 1))
            if not is_open(gx - 1, gz):
                add((gx, gz + 1), (gx, gz))
    start = min(edges)
    loop, prev, p = [start], start, edges[start].pop(0)
    guard = 0
    while p != start and guard < 400000:
        loop.append(p)
        options = edges[p]
        if len(options) > 1:
            # At a pinch, turn left: that keeps following the same open cell.
            dx, dz = p[0] - prev[0], p[1] - prev[1]
            options.sort(key=lambda e: -((dx * (e[1] - p[1])) - (dz * (e[0] - p[0]))))
        prev, p = p, options.pop(0)
        guard += 1
    pts = [(x * RES - HALF, z * RES - HALF) for x, z in loop]
    pts = _simplify(pts + [pts[0]], 0.9)[:-1]
    pts = _chaikin(_subdivide(pts, 3.0), 2)
    # Drop the points rounding left on straight runs (keeps the JSON lean; 0.25 m off at most).
    pts = _simplify(pts + [pts[0]], 0.25)[:-1]
    return [(round(x, 2), round(z, 2)) for x, z in pts]


def _simplify(pts, tolerance):
    if len(pts) < 3:
        return pts
    ax, az = pts[0]
    bx, bz = pts[-1]
    best, index = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, pz = pts[i]
        dx, dz = bx - ax, bz - az
        length = math.hypot(dx, dz)
        d = math.hypot(px - ax, pz - az) if length < 1e-9 else abs(dz * px - dx * pz + bx * az - bz * ax) / length
        if d > best:
            best, index = d, i
    if best <= tolerance:
        return [pts[0], pts[-1]]
    return _simplify(pts[:index + 1], tolerance)[:-1] + _simplify(pts[index:], tolerance)


def _subdivide(pts, longest):
    """Splits long edges, so rounding the corners (Chaikin) never shaves more than a metre off."""
    out = []
    for i in range(len(pts)):
        (ax, az), (bx, bz) = pts[i], pts[(i + 1) % len(pts)]
        steps = max(1, int(math.ceil(math.hypot(bx - ax, bz - az) / longest)))
        for k in range(steps):
            t = k / steps
            out.append((ax + (bx - ax) * t, az + (bz - az) * t))
    return out


def _chaikin(pts, rounds):
    for _ in range(rounds):
        out = []
        for i in range(len(pts)):
            (ax, az), (bx, bz) = pts[i], pts[(i + 1) % len(pts)]
            out.append((ax * 0.75 + bx * 0.25, az * 0.75 + bz * 0.25))
            out.append((ax * 0.25 + bx * 0.75, az * 0.25 + bz * 0.75))
        pts = out
    return pts


def inside(poly, x, z):
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi + 1e-12) + xi:
            hit = not hit
        j = i
    return hit


def carve(map_id, keep, seed=7):
    carved = carve_mask(map_id, keep, seed)
    poly = outline(carved)
    # Smoothing may shave a keep cell by a hair; every protected point must still be inside.
    for x, z, r in keep.get('core', {}).get('circles', []):
        if not inside(poly, x, z):
            raise SystemExit(f'{map_id}: the outline cut off a protected point at ({x}, {z})')
    return poly, carved
