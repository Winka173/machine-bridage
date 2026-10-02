"""Prompt 32 L3 (DECISIONS "Prompt 32 L3 / L7 / L9"): the wall lines of every base map, written into the map files.

    python Tools/maps/p32_walls.py            # plans every map and writes "walls" into the files (idempotent)
    python Tools/maps/p32_walls.py --check    # plans and compares, writes nothing (exit 1 when a file differs)
    python Tools/maps/p32_walls.py --report   # also prints each line's radius and segments

A wall line is a chain of logic segments (12 x 2 m, axis-aligned: NavGrid's blocks are) on a square round the HQ at a
Chebyshev radius R, on the sides that face the enemy, with a gate: two adjacent slots left open (where a road crosses the
line, else the slots facing the enemy). One gate slot is the T-wall's extra segment ("extra": the T-wall's narrower gate,
so the side's own reinforcements go the longer way); the segment next to the gate carries the gun wall's small tower
("gun"). A line has 3 or 4 plain segments (5 with the extra). Up to two lines per camp (ring 1 the outer line, ring 2 the
inner one); a siege fortress (Defend's three fall-back lines) gets three (ring 1, 2, 3), on the corner fortress's rings
(siegeRings) or the layered base's walls (outerWall / innerWall).

The planner works on the simulation's 2 m navigation grid as Tools/campaign/nav_states.py rasterises it (the map's
blocking props and outline, 1.5 m clearance), with every hardpoint filled (0.8 of its size class across) and the HQ.
A slot is skipped (a gap in the line) when its ground with the clearance touches anything blocked, a drop zone, a
capture circle, a neutral site, a start unit, the fortress's super-gun or firing positions; a slot a road crosses is a
gate. Then the whole line (every segment, the extra and the gun tower's block, the worst case of the three types) must
keep every anchor (both rallies, the capture points, the neutral sites) in one region and seal off no more than 6 open
cells: a segment that breaks this is dropped. Rubble only opens ground, so a line that passes intact passes in every
INTACT/RUBBLE combination. A line with fewer than 3 segments at every radius tried is not placed (the map's lines are
NONE there; the report says why). Conquest camps are planned for side 0 and mirrored through the centre for side 1
when the mirror passes; otherwise side 1 is planned on its own (the report says so).
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'campaign'))
import nav_states as nav  # noqa: E402

DATA = nav.DATA
MAPS = os.path.join(DATA, 'maps')
SEG, DEPTH = 12.0, 2.0
SIDE = 60.0      # metres of line on each side of its middle
STEP = 2.0
OFFSETS = (0.0, -2.0, 2.0, -4.0, 4.0, -6.0, 6.0)
SIZES = {'small': 5.0, 'medium': 6.5, 'large': 9.0}
HQ_ACROSS = 14.0
GUN_ACROSS = SIZES['small'] * 0.8
DROP_ZONE = 18.0
POINT_GAP = 3.0
NEUTRAL_RADIUS = 13.0
UNIT_GAP = 4.0
ROAD_GAP = 1.0
MIN_SEGMENTS, MAX_SEGMENTS = 3, 4

CAMP_RADII = {1: (58, 52, 64, 46, 70), 2: (34, 30, 38, 42, 27)}


def strip(text):
    return json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))


def seg_dist(px, pz, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    L = dx * dx + dz * dz
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / L))
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def rect_road_gap(cx, cz, w, d, road):
    """Distance from a rectangle to a road's centre line (sampled on the rectangle's outline and centre)."""
    pts = road['points']
    best = 1e9
    samples = [(cx, cz)]
    for fx in (-0.5, -0.25, 0, 0.25, 0.5):
        for fz in (-0.5, 0.5):
            samples.append((cx + fx * w, cz + fz * d))
            samples.append((cx + fz * w, cz + fx * d))
    for i in range(0, len(pts) - 2, 2):
        for px, pz in samples:
            best = min(best, seg_dist(px, pz, pts[i], pts[i + 1], pts[i + 2], pts[i + 3]))
    return best - road['width'] * 0.5


class Plan:
    def __init__(self, map_id):
        self.g = nav.Grid(map_id)
        self.m = self.g.map
        self.id = map_id
        m = self.m
        self.rallies = [(t['x'], t['z']) for t in m.get('teams', [])]
        self.points = [(p['x'], p['z'], p.get('radius', 10)) for p in m.get('points', [])]
        self.neutrals = [(n['x'], n['z']) for n in m.get('neutrals', [])]
        self.units = [(u['x'], u['z']) for u in m.get('units', [])]
        self.roads = list(m.get('roads', []))
        self.avoid = []      # (x, z, metres): the fortress's super gun and firing positions, the outposts
        f = m.get('fortress')
        if f:
            if f.get('superGun'):
                self.avoid.append((f['superGun']['x'], f['superGun']['z'], 9.0))
            for xz in f.get('firing', []) + f.get('forward', []):
                self.avoid.append((xz[0], xz[1], 7.0))
            a = f.get('arrival')
            if a:
                self.roads.append({'points': a['path'], 'width': a.get('width', 16.0)})
        for p in m.get('points', []):
            for o in p.get('outpost', []):
                self.avoid.append((o['x'], o['z'], SIZES.get(o.get('size'), 6.5) * 0.5 + 3.0))
        # Every hardpoint filled and the HQ, as SimWorld.AnchorDefence anchors them.
        for b in m.get('bases', []):
            self.g.rect(b['hq']['x'], b['hq']['z'], HQ_ACROSS * 0.8, HQ_ACROSS * 0.8, nav.CLEARANCE, +1)
            for s in b.get('slots', []):
                across = SIZES.get(s.get('size'), 9.0) * 0.8
                self.g.rect(s['x'], s['z'], across, across, nav.CLEARANCE, +1)
        if f:
            for s in f.get('slots', []):
                across = SIZES.get(s.get('size'), 9.0) * 0.8
                self.g.rect(s['x'], s['z'], across, across, nav.CLEARANCE, +1)
        self.anchors = self.rallies + [(p[0], p[1]) for p in self.points] + self.neutrals
        lab = self.g.regions()
        self.main = self.g.region_at(lab, *self.anchors[0]) if self.anchors else 0
        self.base_lab = lab

    # ------------------------------------------------------------------ slots
    def cells_clear(self, cx, cz, w, d):
        g = self.g
        hw, hd = w * 0.5 + nav.CLEARANCE, d * 0.5 + nav.CLEARANCE
        x0, y0 = g.cell(cx - hw, cz - hd)
        x1, y1 = g.cell(cx + hw - 1e-4, cz + hd - 1e-4)
        if x0 < 0 or y0 < 0 or x1 >= g.w or y1 >= g.h:
            return False
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if g.block[y * g.w + x]:
                    return False
        return True

    def slot_state(self, s):
        """'wall' (free ground), 'road' (a road crosses it: a gate), or the reason it is skipped."""
        cx, cz, w, d = s['x'], s['z'], s['w'], s['d']
        for road in self.roads:
            if rect_road_gap(cx, cz, w, d, road) < ROAD_GAP:
                return 'road'
        if not self.cells_clear(cx, cz, w, d):
            return 'blocked'
        hw, hd = w * 0.5, d * 0.5

        def near(px, pz, r):
            dx = max(abs(px - cx) - hw, 0.0)
            dz = max(abs(pz - cz) - hd, 0.0)
            return math.hypot(dx, dz) < r
        for x, z in self.rallies:
            if near(x, z, DROP_ZONE):
                return 'drop zone'
        for x, z, r in self.points:
            if near(x, z, r + POINT_GAP):
                return 'capture point'
        for x, z in self.neutrals:
            if near(x, z, NEUTRAL_RADIUS):
                return 'neutral site'
        for x, z in self.units:
            if near(x, z, UNIT_GAP):
                return 'start unit'
        for x, z, r in self.avoid:
            if near(x, z, r):
                return 'fortress works'
        return 'wall'

    @staticmethod
    def frame(hq, toward, R):
        """The line's frame: a function from (s, offset) to a segment rect, the s range of each side, and the middle."""
        hx, hz = hq
        ux, uz = toward
        n = math.hypot(ux, uz) or 1.0
        ux, uz = ux / n, uz / n
        if abs(ux) > 0.38 and abs(uz) > 0.38:
            sx, sz = (1 if ux > 0 else -1), (1 if uz > 0 else -1)
            cx, cz = hx + sx * R, hz + sz * R

            def rect(s0, off):
                # s >= 0: the side across z (runs along x, away from the corner); s < 0: the side across x.
                if s0 >= 0:
                    return {'x': cx - sx * (s0 + SEG / 2), 'z': cz + sz * off, 'w': SEG, 'd': DEPTH, 'facing': 0 if sz > 0 else 180}
                return {'x': cx + sx * off, 'z': cz - sz * (-s0 - SEG / 2), 'w': DEPTH, 'd': SEG, 'facing': 90 if sx > 0 else 270}
            return rect, [(-SIDE, 0.0), (0.0, SIDE)], 0.0
        if abs(uz) >= abs(ux):
            sz = 1 if uz > 0 else -1
            z = hz + sz * R

            def rect(s0, off):
                return {'x': hx + s0 + SEG / 2, 'z': z + sz * off, 'w': SEG, 'd': DEPTH, 'facing': 0 if sz > 0 else 180}
            return rect, [(-SIDE, SIDE)], 0.0
        sx = 1 if ux > 0 else -1
        x = hx + sx * R

        def rect(s0, off):
            return {'x': x + sx * off, 'z': hz + s0 + SEG / 2, 'w': DEPTH, 'd': SEG, 'facing': 90 if sx > 0 else 270}
        return rect, [(-SIDE, SIDE)], 0.0

    # ------------------------------------------------------------------ checks
    def blocks_of(self, line):
        out = []
        for s in line['segments']:
            out.append((s['x'], s['z'], s['w'], s['d']))
            if s.get('gun'):
                out.append((s['x'], s['z'], GUN_ACROSS, GUN_ACROSS))
        return out

    def passes(self, blocks):
        """With these blocks drawn: every anchor in one region, no more than 6 open cells of the main region cut off."""
        g = self.g
        for b in blocks:
            g.rect(*b, nav.CLEARANCE, +1)
        try:
            lab = g.regions()
            regions = {g.region_at(lab, x, z) for x, z in self.anchors}
            if len(regions) != 1 or 0 in regions:
                return False, 'cuts the anchors apart'
            target = next(iter(regions))
            sealed = {}
            for i, r in enumerate(lab):
                if r and self.base_lab[i] == self.main and r != target:
                    sealed[r] = sealed.get(r, 0) + 1
            cut = sum(n for n in sealed.values() if n > nav.POCKET_CELLS)
            return (cut == 0), (f'seals off {cut} cells' if cut else '')
        finally:
            for b in blocks:
                g.rect(*b, nav.CLEARANCE, -1)

    def draw(self, line, delta):
        for b in self.blocks_of(line):
            self.g.rect(*b, nav.CLEARANCE, delta)

    # ------------------------------------------------------------------ a line
    def place(self, rect, s0, taken):
        """The first offset at which a segment starting at s0 stands on free ground off the other segments; None if none."""
        for off in OFFSETS:
            r = rect(s0, off)
            r['x'], r['z'] = round(r['x'], 2), round(r['z'], 2)
            if any(abs(r['x'] - t['x']) < (r['w'] + t['w']) / 2 + 0.5 and abs(r['z'] - t['z']) < (r['d'] + t['d']) / 2 + 0.5 for t in taken):
                continue
            if self.slot_state(r) == 'wall':
                return r
        return None

    def line_at(self, hq, toward, R, ring):
        rect, sides, middle = self.frame(hq, toward, R)
        # The gate: where a road crosses the line nearest its middle, else the middle (the corner of a diagonal line).
        gate = middle
        crossings = []
        for lo, hi in sides:
            s0 = lo
            while s0 + SEG <= hi:
                if self.slot_state(rect(s0, 0.0)) == 'road':
                    crossings.append(s0 + SEG / 2)
                s0 += STEP
        if crossings:
            gate = min(crossings, key=lambda c: (abs(c - middle), c))
        g0, g1 = gate - SEG, gate + SEG
        taken, chosen = [], []
        # Plain segments from the gate outwards, alternately on each side, each where its ground is free.
        fronts = {'up': g1, 'down': g0}
        tried = 0
        while len(chosen) < MAX_SEGMENTS and tried < 200:
            tried += 1
            moved = False
            for way in ('up', 'down'):
                if len(chosen) >= MAX_SEGMENTS:
                    break
                s_at = fronts[way]
                while True:
                    s0 = s_at if way == 'up' else s_at - SEG
                    side = next(((lo, hi) for lo, hi in sides if lo <= s0 and s0 + SEG <= hi), None)
                    if side is None:
                        # Past a diagonal line's corner (or its end): jump to the next side, else stop.
                        nxt = [lo for lo, hi in sides if way == 'up' and lo > s0 and lo < s0 + SEG] +                               [hi for lo, hi in sides if way == 'down' and hi < s0 + SEG and hi > s0]
                        if not nxt:
                            s_at = None
                            break
                        s_at = nxt[0]
                        continue
                    r = self.place(rect, s0, taken)
                    if r:
                        taken.append(r)
                        chosen.append(r)
                        s_at = s0 + SEG if way == 'up' else s0
                        moved = True
                        break
                    s_at = s_at + STEP if way == 'up' else s_at - STEP
                if s_at is None:
                    fronts[way] = float('inf') if way == 'up' else float('-inf')
                else:
                    fronts[way] = s_at
            if not moved:
                break
        if len(chosen) < MIN_SEGMENTS:
            return None, f'R {R}: {len(chosen)} segments fit'
        # The T-wall's extra closes half the gate (the half that fits; none: the gate stays as wide).
        extra = None
        for s0 in ((gate, gate - SEG) if gate >= middle else (gate - SEG, gate)):
            if any(lo <= s0 and s0 + SEG <= hi for lo, hi in sides):
                extra = self.place(rect, s0, taken)
                if extra:
                    break
        while len(chosen) >= MIN_SEGMENTS:
            line = self.make(chosen, extra, gate, rect, ring, R)
            ok, why = self.passes(self.blocks_of(line))
            if ok:
                return line, ''
            if extra is not None:
                line2 = self.make(chosen, None, gate, rect, ring, R)
                if self.passes(self.blocks_of(line2))[0]:
                    return line2, ''
            chosen = chosen[:-1]
        return None, f'R {R}: {why}'

    @staticmethod
    def make(chosen, extra, gate, rect, ring, R):
        segs = []
        for i, c in enumerate(chosen):
            s = dict(c)
            if i == 0:
                s['gun'] = True
            segs.append(s)
        if extra is not None:
            e = dict(extra)
            e['extra'] = True
            segs.append(e)
        g = rect(gate - SEG / 2, 0.0)
        return {'ring': ring, 'radius': R, 'gate': {'x': round(g['x'], 2), 'z': round(g['z'], 2), 'w': SEG * 2}, 'segments': segs}

    def lines(self, owner, hq, toward, radii, report):
        out = []
        for ring, candidates in radii:
            used = [l['radius'] for l in out]
            why = []
            for R in candidates:
                if any(abs(R - u) < SEG for u in used):
                    continue
                line, reason = self.line_at(hq, toward, R, ring)
                if line:
                    line['owner'] = owner
                    out.append(line)
                    self.draw(line, +1)
                    break
                why.append(reason)
            else:
                report.append(f'{self.id} {owner} ring {ring}: NONE ({"; ".join(why)})')
        for line in out:
            self.draw(line, -1)
        return out


def mirrored(line, owner):
    m = json.loads(json.dumps(line))
    m['owner'] = owner
    m['gate']['x'], m['gate']['z'] = -m['gate']['x'], -m['gate']['z']
    for s in m['segments']:
        s['x'], s['z'] = round(-s['x'], 2) + 0.0, round(-s['z'], 2) + 0.0
        s['facing'] = (s['facing'] + 180) % 360
    return m


def fortress_radii(m):
    f = m.get('fortress') or {}
    rings = m.get('siegeRings')
    if f.get('layout') == 'layered' or f.get('rings'):
        hz = f['hq'][1]
        r2 = hz - f.get('outerWall', 218.0) + 9.0
        r3 = hz - f.get('innerWall', 266.0) + 9.0
        r1 = r2 + 40.0
        return [(1, (r1, r1 + 6, r1 - 6, r1 + 12)), (2, (r2, r2 + 4, r2 - 3)), (3, (r3, r3 + 4, r3 - 3))]
    if rings:
        outer, walls = rings[0], rings[1]
        r1, r2, r3 = outer - 7.0, walls + 9.0, walls - 14.0
        return [(1, (r1, r1 - 6, r1 + 6, r1 - 12, r1 + 12, r1 - 18)), (2, (r2, r2 - 3, r2 + 4, r2 + 8)), (3, (r3, r3 - 4, r3 + 4, r3 - 8, r3 + 8))]
    return []


def fortress_hq(m):
    f = m.get('fortress')
    if f:
        return tuple(f['hq'])
    for p in m.get('props', []):
        if p['def'] == 'command_hq':
            return (p['x'], p['z'])
    t = [t for t in m.get('teams', []) if t['team'] == 1]
    return (t[0]['x'], t[0]['z']) if t else None


def plan_map(map_id, report):
    p = Plan(map_id)
    m = p.m
    lines = []
    bases = m.get('bases', [])
    rally = {t['team']: (t['x'], t['z']) for t in m.get('teams', [])}
    camp_radii = [(1, CAMP_RADII[1]), (2, CAMP_RADII[2])]
    conquest = map_id.endswith('_conquest')
    for b in bases:
        team = b.get('team', 0)
        hq = (b['hq']['x'], b['hq']['z'])
        enemy = rally.get(1 - team, (0.0, 0.0)) if conquest or team == 1 else (0.0, 0.0)
        # A siege or long camp (side 0) faces the map's middle and the fortress beyond.
        if not conquest:
            fq = fortress_hq(m)
            enemy = fq if fq else (0.0, 0.0)
        toward = (enemy[0] - hq[0], enemy[1] - hq[1])
        owner = f'camp{team}'
        if conquest and team == 1 and any(l['owner'] == 'camp0' for l in lines):
            mirror = [mirrored(l, owner) for l in lines if l['owner'] == 'camp0']
            blocks = [b2 for l in mirror for b2 in p.blocks_of(l)]
            ok, why = p.passes(blocks + [b2 for l in lines for b2 in p.blocks_of(l)])
            if ok and all(all(p.slot_state(s) == 'wall' for s in l['segments']) for l in mirror):
                lines += mirror
                continue
            report.append(f'{map_id} camp1: the mirror of camp0 does not fit ({why or "a slot in the way"}): planned on its own')
        for l in lines:
            p.draw(l, +1)
        lines += p.lines(owner, hq, toward, camp_radii, report)
        for l in lines:
            if l['owner'] != owner:
                p.draw(l, -1)
    radii = fortress_radii(m)
    if radii and map_id.endswith(('_siege', '_long')):
        hq = fortress_hq(m)
        attacker = rally.get(0, (0.0, 0.0))
        toward = (attacker[0] - hq[0], attacker[1] - hq[1])
        for l in lines:
            p.draw(l, +1)
        lines += p.lines('fortress', hq, toward, radii, report)
    if conquest:
        # A symmetric battlefield keeps its camps alike: a ring only one camp could take is dropped from the other.
        rings = [{l['ring'] for l in lines if l['owner'] == f'camp{t}'} for t in (0, 1)]
        both = rings[0] & rings[1]
        for t in (0, 1):
            for r in sorted(rings[t] - both):
                report.append(f'{map_id} camp{t} ring {r}: dropped (the other camp has no line there: kept symmetric)')
        lines = [l for l in lines if l['owner'] not in ('camp0', 'camp1') or l['ring'] in both]
    if lines:
        ok, why = p.passes([b for l in lines for b in p.blocks_of(l)])
        if not ok:
            report.append(f'{map_id}: every line together fails ({why}): the inner lines dropped')
            lines = [l for l in lines if l['ring'] == 1]
    return lines


def render(lines):
    if not lines:
        return None
    return '  "walls": [\n' + ',\n'.join('    ' + json.dumps(l) for l in lines) + '\n  ]'


WALLS = re.compile(r',\n\n  "walls": \[\n(?:    .*\n)*?  \]')


def write(path, lines, check):
    text = open(path, encoding='utf-8', newline='').read()
    clean = WALLS.sub('', text)
    block = render(lines)
    new = clean
    if block:
        at = clean.find('\n  "roads": [')
        if at < 0:
            at = clean.rfind('\n}')
            new = clean[:at] + ',\n\n' + block + clean[at:]
        else:
            # "...,\n\n  "roads"": the walls go in before the roads, with the same separator.
            head = clean[:at].rstrip()
            assert head.endswith(','), path
            new = head + '\n\n' + block + ',\n' + clean[at:]
    if new == text:
        return False
    if not check:
        open(path, 'w', encoding='utf-8', newline='').write(new)
    return True


def main(args):
    check = '--check' in args
    verbose = '--report' in args
    ids = [a for a in args if not a.startswith('--')]
    report, summary, changed = [], [], 0
    for name in sorted(os.listdir(MAPS)):
        if not name.endswith('.json'):
            continue
        map_id = name[:-5]
        if ids and not any(i in map_id for i in ids):
            continue
        m = strip(open(os.path.join(MAPS, name), encoding='utf-8').read())
        if not m.get('bases') and not m.get('fortress') and not m.get('siegeRings'):
            continue
        lines = plan_map(map_id, report)
        if write(os.path.join(MAPS, name), lines, check):
            changed += 1
        summary.append((map_id, lines))
        if verbose:
            for l in lines:
                print(f"  {map_id} {l['owner']} ring {l['ring']} R {l['radius']}: {len(l['segments'])} segments, gate {l['gate']}")
    for map_id, lines in summary:
        owners = {}
        for l in lines:
            owners.setdefault(l['owner'], []).append(l['ring'])
        print(f'{map_id}: ' + (', '.join(f'{o} rings {sorted(r)}' for o, r in sorted(owners.items())) or 'no wall line'))
    for r in report:
        print('NOTE', r)
    print(f'{len(summary)} base maps, {changed} {"would change" if check else "written"}')
    if check and changed:
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
