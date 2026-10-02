"""Prompt 31 L3 (DECISIONS "Prompt 31 L3"): the data side of the prebuilt NavGrid states (Sim/Navigation/NavStates.cs).

A mission names switchable pieces of ground in "navStates": [{"id": "foundry_door", "initial": "open", "states": [{"name":
"open", "blocks": []}, {"name": "shut", "blocks": [{"x": .., "z": .., "w": .., "d": ..}]}]}]. Every state is built when the
battle loads and only switched at a tick boundary (an event names the site and the state). The game checks each state itself
as it loads (NavStates.Validate) and refuses a state that cuts the anchors apart or seals ground off; this file does the same
over the data, so a bad rectangle fails the campaign build before it reaches Unity: the map's blocking props and its outline
rasterised as NavGrid does (2 m cells, 1.5 m clearance, the same rounding), then for every state of every site the anchors
(the team rallies and the capture points) must stay in one region and no open cell of the anchors' region may end up in a
pocket larger than POCKET_CELLS. The map's fixed defences (towers placed by the mission) are not drawn here; the game's own
check counts them.

  python nav_states.py <map file id> [x0 z0 x1 z1]   prints the map's walkable cells (4 m a character) for authoring.
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'Data'))
CELL, CLEARANCE, POCKET_CELLS = 2.0, 1.5, 6


def _json(path):
    text = open(path, encoding='utf-8').read()
    return json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))


_PROPS = None


def props():
    global _PROPS
    if _PROPS is None:
        b = _json(os.path.join(DATA, 'balance.json'))
        _PROPS = {}
        for p in b['props']:
            s = p.get('scale', 1.0)
            _PROPS[p['id']] = (p['width'] * s, p['depth'] * s, p.get('blocks', False))
    return _PROPS


class Grid:
    def __init__(self, map_id):
        m = _json(os.path.join(DATA, 'maps', map_id + '.json'))
        self.map = m
        if 'bounds' in m:
            x0, z0, x1, z1 = m['bounds']
        else:
            h = m['size'] * 0.5
            x0, z0, x1, z1 = -h, -h, h, h
        self.ox, self.oz = x0, z0
        self.w = int(math.ceil((x1 - x0) / CELL))
        self.h = int(math.ceil((z1 - z0) / CELL))
        self.block = [0] * (self.w * self.h)
        poly = [(p['x'], p['z']) for p in m.get('boundary', [])] if m.get('boundary') and isinstance(m['boundary'][0], dict) else \
            [(m['boundary'][i], m['boundary'][i + 1]) for i in range(0, len(m.get('boundary', [])), 2)]
        if len(poly) >= 3:
            for y in range(self.h):
                for x in range(self.w):
                    if not inside(poly, self.centre(x, y)):
                        self.block[y * self.w + x] += 1
        table = props()
        for p in m.get('props', []):
            if p['def'] not in table:
                continue
            pw, pd, blocks = table[p['def']]
            if not blocks:
                continue
            rot = ((p.get('rot', 0) % 360) + 360) % 360
            if rot in (90, 270):
                pw, pd = pd, pw
            if rot % 90:
                pw = pd = (pw + pd) * 0.70710677
            self.rect(p['x'], p['z'], pw, pd, CLEARANCE, +1)

    def centre(self, x, y):
        return self.ox + (x + 0.5) * CELL, self.oz + (y + 0.5) * CELL

    def cell(self, px, pz):
        return int(math.floor((px - self.ox) / CELL)), int(math.floor((pz - self.oz) / CELL))

    def rect(self, cx, cz, w, d, clearance, delta):
        hw, hd = w * 0.5 + clearance, d * 0.5 + clearance
        x0, y0 = self.cell(cx - hw, cz - hd)
        x1, y1 = self.cell(cx + hw - 1e-4, cz + hd - 1e-4)
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                i = y * self.w + x
                self.block[i] = max(0, self.block[i] + delta)

    def regions(self):
        """Four-neighbour regions numbered from 1 (0: blocked), as NavGrid.Label."""
        lab = [0] * len(self.block)
        n = 0
        for s in range(len(self.block)):
            if lab[s] or self.block[s]:
                continue
            n += 1
            lab[s] = n
            q = [s]
            while q:
                i = q.pop()
                x, y = i % self.w, i // self.w
                for j, ok in ((i + 1, x + 1 < self.w), (i - 1, x > 0), (i + self.w, y + 1 < self.h), (i - self.w, y > 0)):
                    if ok and not lab[j] and not self.block[j]:
                        lab[j] = n
                        q.append(j)
        return lab

    def region_at(self, lab, px, pz):
        x, y = self.cell(px, pz)
        if not (0 <= x < self.w and 0 <= y < self.h):
            return 0
        if lab[y * self.w + x]:
            return lab[y * self.w + x]
        # A point on a prop's clearance: the nearest open cell (NavGrid.TryNearestWalkable's rings).
        for ring in range(1, 6):
            for yy in range(y - ring, y + ring + 1):
                for xx in range(x - ring, x + ring + 1):
                    if 0 <= xx < self.w and 0 <= yy < self.h and lab[yy * self.w + xx]:
                        return lab[yy * self.w + xx]
        return 0

    def anchors(self):
        m = self.map
        out = [(t['x'], t['z']) for t in m.get('teams', [])]
        out += [(p['x'], p['z']) for p in m.get('points', [])]
        return out


def inside(poly, p):
    x, y = p
    res = False
    j = len(poly) - 1
    for i in range(len(poly)):
        ax, ay = poly[i]
        bx, by = poly[j]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            res = not res
        j = i
    return res


def apply_state(g, state, delta):
    for b in state.get('blocks', []):
        g.rect(b['x'], b['z'], b['w'], b['d'], b.get('clearance', CLEARANCE), delta)


def check_site(g, site, fail, where, extra_anchors=()):
    """Every state of a site against the initial one: the anchors stay joined, no open ground of theirs is sealed off."""
    states = {s['name']: s for s in site['states']}
    if len(states) != len(site['states']) or len(states) < 2:
        fail(f"{where}: nav site {site['id']} needs two or more states with different names")
        return
    initial = site.get('initial', site['states'][0]['name'])
    if initial not in states:
        fail(f"{where}: nav site {site['id']} starts in {initial}, which it does not define")
        return
    for s in site['states']:
        for b in s.get('blocks', []):
            if not (b.get('w', 0) > 0 and b.get('d', 0) > 0):
                fail(f"{where}: nav site {site['id']} state {s['name']} has a block without a size")
    apply_state(g, states[initial], +1)
    base = g.regions()
    anchors = list(g.anchors()) + list(extra_anchors)
    home = [g.region_at(base, x, z) for x, z in anchors]
    main = home[0]
    apply_state(g, states[initial], -1)
    for s in site['states']:
        if s['name'] == initial:
            continue
        apply_state(g, s, +1)
        lab = g.regions()
        now = [g.region_at(lab, x, z) for x, z in anchors]
        for k in range(len(anchors)):
            for j in range(k + 1, len(anchors)):
                if home[k] and home[k] == home[j] and now[k] != now[j]:
                    fail(f"{where}: nav site {site['id']} state {s['name']} cuts {anchors[k]} off from {anchors[j]} (no route round)")
        target = now[0]
        sealed = {}
        for i, r in enumerate(lab):
            if r and base[i] == main and r != target:
                sealed[r] = sealed.get(r, 0) + 1
        big = {r: n for r, n in sealed.items() if n > POCKET_CELLS}
        if big:
            fail(f"{where}: nav site {site['id']} state {s['name']} seals off {sum(big.values())} open cells (a vehicle there would be trapped)")
        apply_state(g, s, -1)


def check(missions, fail, library=None):
    """The campaign build's check: every mission's nav sites on the map file the mission loads (library: event id -> row)."""
    for m in missions:
        sites = m.get('navStates')
        if not sites:
            continue
        if m.get('reversed'):
            fail(f"{m['id']}: nav states on a reversed battlefield (the rectangles are written for the map as drawn)")
            continue
        map_id = m['map'] + '_' + m.get('variant', 'conquest')
        if not os.path.exists(os.path.join(DATA, 'maps', map_id + '.json')):
            map_id = m['map']
        try:
            g = Grid(map_id)
        except FileNotFoundError:
            fail(f"{m['id']}: nav states on {map_id}, which has no map file")
            continue
        ids = [s['id'] for s in sites]
        if len(set(ids)) != len(ids):
            fail(f"{m['id']}: a nav site id twice")
        for site in sites:
            check_site(g, site, fail, m['id'])
        named = {s['id']: {st['name'] for st in s['states']} for s in sites}
        refs = list(m.get('missionEvents', [])) + [r for st in m.get('stages', []) for r in st.get('missionEvents', [])]
        for r in refs:
            # The library row's params under the mission's own (prompt 31 L5: "cycle" walks the site's states, no "navState").
            rid = r if isinstance(r, str) else r.get('id')
            p = {**(library or {}).get(rid, {}).get('params', {}), **(r.get('params', {}) if isinstance(r, dict) else {})}
            if 'navSite' not in p:
                continue
            # A forest fire (or a cycle) walks the site's states itself; a plain switch names the state it brings in.
            walks = p.get('cycle') or (library or {}).get(rid, {}).get('kind') == 'ForestFire'
            if p['navSite'] not in named or (not walks and p.get('navState') not in named[p['navSite']]):
                fail(f"{m['id']}: event {rid} switches {p.get('navSite')} to {p.get('navState')}, which the mission does not build")


def render(map_id, box=None, extra=()):
    g = Grid(map_id)
    for site in extra:
        apply_state(g, site, +1)
    lab = g.regions()
    x0, z0, x1, z1 = box or (g.ox, g.oz, g.ox + g.w * CELL, g.oz + g.h * CELL)
    rows = []
    z = z1 - 2
    while z >= z0:
        row = ''
        x = x0 + 2
        while x <= x1:
            cx, cy = g.cell(x, z)
            ok = 0 <= cx < g.w and 0 <= cy < g.h
            row += '#' if not ok or g.block[cy * g.w + cx] else ('.' if lab[cy * g.w + cx] == g.region_at(lab, *g.anchors()[0]) else 'o')
            x += 4
        rows.append(f'{z:7.0f} {row}')
        z -= 4
    print('\n'.join(rows))


if __name__ == '__main__':
    args = sys.argv[1:]
    render(args[0], tuple(float(a) for a in args[1:5]) if len(args) >= 5 else None)
