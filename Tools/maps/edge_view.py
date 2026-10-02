"""Prompt 33 L2 view / L7: the view's edge rules in Python, for map_dressing.py (landmark spots) and validate_p33.py.

Mirrors Assets/MachineBrigade/Scripts/Game/Views/Surroundings.Edges.cs without its coast wobble (Unity's Perlin noise;
the wobble is 0 within CoastStraight m of the edge and at most +-17 m beyond, so the checks keep a tolerance there):

- the stretch beyond a point outside the map's rectangle is the side's segment at the point's along value (clamped);
- a point outside is on the sea when either side it is beyond has a SEA stretch there (the sea takes a corner square);
- a river link runs on out as a channel of its width; road links and rails run on out as lines.
"""
from __future__ import annotations

import math

COAST_STRAIGHT = 36.0
COAST_WOBBLE = 17.0


def rect(m):
    if m.get('bounds'):
        return tuple(m['bounds'])
    h = m['size'] / 2
    return (-h, -h, h, h)


def segments(m):
    return (m.get('edges') or {}).get('segments', [])


def seg_at(m, side, along):
    for s in segments(m):
        if s['side'] == side and s['from'] - 1e-3 <= along <= s['to'] + 1e-3:
            return s
    return None


def beyond(m, x, z):
    """Metres outside the rectangle (negative inside): the larger overshoot."""
    x0, z0, x1, z1 = rect(m)
    return max(x0 - x, x - x1, z0 - z, z - z1)


def side_segments(m, x, z):
    """The (side, segment, overshoot) of every side the point is beyond."""
    x0, z0, x1, z1 = rect(m)
    out = []
    dx = max(x0 - x, x - x1)
    dz = max(z0 - z, z - z1)
    if dx > 0:
        side = 'E' if x > x1 else 'W'
        out.append((side, seg_at(m, side, min(max(z, z0), z1)), dx))
    if dz > 0:
        side = 'N' if z > z1 else 'S'
        out.append((side, seg_at(m, side, min(max(x, x0), x1)), dz))
    return out


def edge_sea(m, x, z):
    return any(s is not None and s['type'] == 'SEA' for _, s, _ in side_segments(m, x, z))


def near_coast(m, x, z, tol=COAST_WOBBLE + 3.0):
    """Within the wobble's reach of a sea/land boundary (the checks do not judge there)."""
    here = edge_sea(m, x, z)
    for dx, dz in ((tol, 0), (-tol, 0), (0, tol), (0, -tol)):
        if edge_sea(m, x + dx, z + dz) != here:
            return True
    return False


def rivers(m):
    out = []
    for link in (m.get('edges') or {}).get('links', []):
        if link['kind'] == 'river' and (link.get('dirX') or link.get('dirZ')):
            n = math.hypot(link['dirX'], link['dirZ'])
            out.append((link['x'], link['z'], link['dirX'] / n, link['dirZ'] / n, max(4.0, link.get('width', 8) / 2)))
    return out


def river_distance(m, x, z, meander=14.0):
    """Metres from the nearest river running out (its meander counted as width past CoastStraight)."""
    best = 999.0
    for rx, rz, dx, dz, half in rivers(m):
        t = (x - rx) * dx + (z - rz) * dz
        if t < -1:
            continue
        across = abs(dx * (z - rz) - dz * (x - rx))
        slack = min(meander, half * 0.6) if t > COAST_STRAIGHT else 0.0
        best = min(best, across - half - slack)
    return best


def seg_dist(px, pz, ax, az, bx, bz):
    vx, vz = bx - ax, bz - az
    L = vx * vx + vz * vz
    t = 0.0 if L < 1e-9 else max(0.0, min(1.0, ((px - ax) * vx + (pz - az) * vz) / L))
    return math.hypot(px - ax - vx * t, pz - az - vz * t)


def lines(m, reach=900.0):
    """Roads running out (link + its way out) and rails (their polylines): (ax, az, bx, bz, half, kind)."""
    out = []
    for link in (m.get('edges') or {}).get('links', []):
        if link['kind'] == 'road':
            n = math.hypot(link['dirX'], link['dirZ']) or 1.0
            dx, dz = link['dirX'] / n, link['dirZ'] / n
            half = min(max(link.get('width', 6) / 2, 1.5), 12.0)
            out.append((link['x'] - dx * 2, link['z'] - dz * 2, link['x'] + dx * reach, link['z'] + dz * reach, half, 'road'))
    for r in m.get('rails', []):
        pts = list(zip(r['points'][0::2], r['points'][1::2]))
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            out.append((ax, az, bx, bz, 2.4, 'rail'))
    return out
