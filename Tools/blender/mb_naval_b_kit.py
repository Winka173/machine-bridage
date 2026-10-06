"""Naval models lane B (06/10 owner prompt, Docs/naval/MODEL_CONTRACT.md): the shared ship kit of the eight big hulls.

The hull lofter (`Ship`: plan shape, sheer, flare, raked stem, cut-up stern, boot-top, red bottom, Team bands,
portholes, hawse pipes, railings, deck plates), superstructure tiers, funnels, masts, the spinning `Radar` and the
`Mount_APS` sensor, and the weapons, each on its own stable runtime node (Docs/models/RUNTIME_NODES.md: the k-th mount
of a slot is `Mount_<slot>` then `Mount_<slot>_02`, `_03`; its muzzle `Muzzle_<slot>[_NN]` is the mount's child):
the 127 mm (Mk 45 Mod 4 faceted / Mod 2 rounded), the 100-130 mm stealth gun, the heavy turrets (one or two barrels,
`Muzzle_b<k>_gun` per barrel of a twin), the Phalanx and AK-630 / Type 1130 CIWS, the VLS fields, the inclined-cell
anti-ship deck, the S-300F revolver hatches, the Mk 26 twin-arm, Mk 29 box and RAM-type box SAM launchers, the quad
anti-ship canister rack. A fixed launcher's mount pivot carries only its muzzle and the `Muzzle_b<k>_<tag>` launch
cells near it (the view turns a Free mount's pivot to its target, so the cells stay within ~1.2 m of the pivot); a
gun's house, barrels (`Gun_barrels[_N]`: ModelLibrary.IsMountBarrel, they kick back on each shot) and muzzle ride it.

Wake and smoke: no node (WakeView draws the wake from the `naval` data; the funnels get soot in COLOR_0 only).
Metres, +Z up, -Y front (the bow), +X left (port). Each builder uses its own dimensions, so no two ships share a mesh.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
FWD = K.FORWARD


def tag(i):
    """'' for the slot's first node, '_02', '_03' ... after it (stable semantic names)."""
    return '' if i == 0 else f'_{i + 1:02d}'


def sfx(i):
    """Mesh-name suffix of the i-th mount of a kind ('' then '_2', '_3'): unique, no Blender '.NNN'."""
    return '' if i == 0 else f'_{i + 1}'


# ============================================================================= hull
class Ship:
    """A displacement hull from the stem (y = -L/2) to the transom (y = +L/2); z = 0 is the waterline."""

    def __init__(self, a, L, B, draft, z_aft, z_mid, z_bow, entry=.36, transom=.8, sheer_from=.15, rake=2.0,
                 flare=.22, bulge=0.0, fb_knuckle=.45, deck_mat='NavyDeck', hull_mat='Armor'):
        self.a, self.L, self.hb, self.d = a, L, B / 2, draft
        self.bow, self.stern = -L / 2, L / 2
        self.z_aft, self.z_mid, self.z_bow = z_aft, z_mid, z_bow
        self.entry, self.transom, self.sheer_from, self.rake = entry, transom, sheer_from, rake
        self.flare, self.bulge, self.kn = flare, bulge, fb_knuckle
        self.deck_mat, self.hull_mat = deck_mat, hull_mat

    def half_beam(self, y):
        f = (y - self.bow) / self.L
        h = self.hb * math.sin(min(1.0, f / self.entry) * R90) ** .8 if f < self.entry else self.hb
        if f > .7:
            h *= 1 - (1 - self.transom) * ((f - .7) / .3) ** 1.6
        return max(h, .05)

    def deck_z(self, y):
        if y >= 0:
            return self.z_mid + (self.z_aft - self.z_mid) * (y / (self.L / 2)) ** 1.5
        f = max(0.0, (-y / (self.L / 2) - self.sheer_from) / (1 - self.sheer_from))
        return self.z_mid + (self.z_bow - self.z_mid) * f ** 1.7

    def wl_beam(self, y):
        h = self.half_beam(y)
        fb = max(0.0, -y / (self.L / 2))
        mid = max(0.0, 1 - abs(y) / (self.L * .38)) ** .5
        return h * (1 - self.flare * fb ** 1.3) * (1 + self.bulge * mid)

    def keel(self, y):
        f = (y - self.bow) / self.L
        z = -self.d
        if f < .12:
            z += self.d * .8 * (1 - f / .12) ** 2.5
        if f > .8:
            z += self.d * .55 * ((f - .8) / .2) ** 1.4
        return z

    def ring(self, y):
        h, z, wl, kz = self.half_beam(y), self.deck_z(y), self.wl_beam(y), self.keel(y)
        fb = z * self.kn
        b = .35 if self.bulge else .78
        side = [(h, y, z), (h * .995, y, z - fb), (wl, y, .35), (wl * b if self.bulge else wl * .8, y, -self.d * .55),
                (.35, y, kz)]
        if self.bulge:
            side[3] = (wl * .82, y, -self.d * .6)
        left = [(-p[0], p[1], p[2]) for p in side]
        return left + list(reversed(side))

    def stations(self):
        fs = [0, .03, .08, .16, .26, .38, .5, .6, .68, .75, .81, .86, .9, .935, .96, .98, .992]
        return [self.stern - f * self.L for f in fs]

    def hull(self):
        a = self.a
        rings = [self.ring(y) for y in self.stations()]
        zt, zb = self.z_bow, self.keel(self.bow)
        stem = []
        for (x, y, z) in self.ring(self.bow + .02):
            u = (zt - z) / (zt - zb)
            stem.append((math.copysign(.03, x) + x * .02, self.bow + self.rake * max(0.0, u) ** 1.3, z))
        rings.append(stem)
        k.sharp_loft(a.part('Hull', self.hull_mat), rings, chamfer=.05)
        self._waterline_paint()
        self._deck()
        edge = a.part('Deck_edge', 'MetalSheet')
        ys = [self.stern - .1] + [y for y in self.stations()[1:]] + [self.bow + .5]
        for s in (-1, 1):
            edge.tube([(s * (self.half_beam(y) + .01), y, self.deck_z(y) + .03) for y in ys], .07, seg=5)
        seams = a.part('Hull_seams', 'Undercarriage')
        y = self.bow + self.rake + 2.5
        while y < self.stern - 1.0:
            z = self.deck_z(y)
            for s in (-1, 1):
                seams.box((.03, .05, z * .6), loc=(s * (self.side_x(y, z * .6) + .02), y, z * .62), bevel=0)
            y += 3.2

    def side_x(self, y, z):
        """The hull side's half-width at height z (between the ring's points), for paint strips."""
        r = self.ring(y)[5:]
        pts = [(p[0], p[2]) for p in r]   # from the keel up to the deck edge
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            if z0 <= z <= z1 + 1e-6:
                t = (z - z0) / max(1e-6, z1 - z0)
                return x0 + (x1 - x0) * t
        return pts[-1][0]

    def strip(self, part, y0, y1, z0, z1, out=.015, n=None):
        """A paint strip on both sides of the hull between heights z0 (bottom) and z1 (top)."""
        n = n or max(2, int((y1 - y0) / 2.5))
        ys = [y0 + (y1 - y0) * i / n for i in range(n + 1)]
        for s in (-1, 1):
            vs = [(s * (self.side_x(y, z1) + out), y, z1) for y in ys] + \
                 [(s * (self.side_x(y, z0) + out), y, z0) for y in reversed(ys)]
            idx = tuple(range(len(vs)))
            part.mesh(vs, [idx if s < 0 else tuple(reversed(idx))])

    def _waterline_paint(self):
        a = self.a
        y0, y1 = self.bow + self.rake * .55 + .6, self.stern - .05
        self.strip(a.part('Hull_low', 'HullRed'), y0, y1, -self.d * .5, .12, out=.035, n=24)
        self.strip(a.part('Boot_top', 'BootTop'), y0 - .3, y1, .12, .5, out=.045, n=24)

    def _deck(self):
        a = self.a
        deck = a.part('Deck', self.deck_mat)
        ys = []
        y = self.stern - .06
        while y > self.bow + 1.2:
            ys.append(y)
            y -= 1.6 if y > -self.L * .3 else .9
        ys.append(self.bow + 1.0)
        for ya, yb in zip(ys, ys[1:]):
            ha, hb = self.half_beam(ya) - .06, self.half_beam(yb) - .06
            deck.mesh([(-ha, ya, self.deck_z(ya) + .012), (ha, ya, self.deck_z(ya) + .012),
                       (hb, yb, self.deck_z(yb) + .012), (-hb, yb, self.deck_z(yb) + .012)], [(3, 2, 1, 0)])

    # -- fittings on the hull
    def deck_dress(self, ranges, seed=0, hatches=3, planks=False):
        """The open decks in `ranges` (y0, y1): the dark non-skid walkways inside both rails with their yellow edge
        lines, the plank seams across the deck, a few hatches and ready-use lockers."""
        import random
        rng = random.Random(seed)
        a = self.a
        walk = a.part('Walkways', 'Charred')
        lines = a.part('Deck_lines', 'Hazard')
        seams = a.part('Deck_seams', 'Undercarriage')
        hat = a.part('Deck_hatches', 'Armor')
        for y0, y1 in ranges:
            n = max(1, int((y1 - y0) / 1.6))
            for i in range(n):
                ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
                ym = (ya + yb) / 2
                z = self.deck_z(ym) + .02
                h = self.half_beam(ym)
                for s in (-1, 1):
                    xo = s * (h - .55)
                    K.plane(walk, min(xo, xo - s * .7), max(xo, xo - s * .7), ya + .05, yb - .05, z)
                    xl = xo - s * .75
                    K.plane(lines, xl - .04, xl + .04, ya + .05, yb - .05, z + .004)
            y = y0 + 1.0
            while y < y1 - .5:
                h = self.half_beam(y) - 1.4
                if h > .4:
                    K.plane(seams, -h, h, y - .025, y + .025, self.deck_z(y) + .018)
                y += 1.2
            if planks:
                ym = (y0 + y1) / 2
                n = int((self.half_beam(ym) - 1.4) / .9)
                for i in range(-n, n + 1):
                    xs = i * .9
                    pts = [y for y in (y0 + (y1 - y0) * t / 6 for t in range(7)) if self.half_beam(y) - 1.4 > abs(xs)]
                    for ya, yb in zip(pts, pts[1:]):
                        seams.mesh([(xs - .02, ya, self.deck_z(ya) + .018), (xs + .02, ya, self.deck_z(ya) + .018),
                                    (xs + .02, yb, self.deck_z(yb) + .018), (xs - .02, yb, self.deck_z(yb) + .018)],
                                   [(3, 2, 1, 0)] if yb < ya else [(0, 1, 2, 3)])
            for j in range(hatches if y1 - y0 > 5 else 1):
                yy = rng.uniform(y0 + 1.0, y1 - 1.0)
                xx = rng.choice((-1, 1)) * rng.uniform(.9, max(1.0, self.half_beam(yy) - 1.9))
                k.block(hat, (.8, .9, .12), loc=(xx, yy, self.deck_z(yy) + .07), chamfer=.03)
                hat.box((.5, .05, .05), loc=(xx, yy - .3, self.deck_z(yy) + .15), bevel=0)

    def team_bands(self, y0, y1, depth=.5):
        part = self.a.part('Team_band', 'Team')
        zt = min(self.deck_z(y0), self.deck_z(y1)) - .25
        self.strip(part, y0, y1, zt - depth, zt, out=.02, n=8)

    def portholes(self, ys, dz=.7, r=.16):
        for s in (-1, 1):
            pts = [(s * (self.side_x(y, self.deck_z(y) - dz) + .015), y, self.deck_z(y) - dz) for y in ys]
            K.portholes(self.a, pts, (s, 0, 0), r=r, seg=6)

    def rails(self, y_ranges, h=.85, post=1.7):
        part = self.a.part('Railings', 'Steel')
        for y0, y1 in y_ranges:
            n = max(2, int(abs(y1 - y0) / 2.0))
            for s in (-1, 1):
                pts = [(s * (self.half_beam(y) - .12), y, self.deck_z(y) + .012)
                       for y in (y0 + (y1 - y0) * i / n for i in range(n + 1))]
                K.railing(part, pts, h=h, post=post, r=.025)

    def anchors(self, y, size=1.0):
        a = self.a
        for s in (-1, 1):
            z = self.deck_z(y) - .9 * size
            x = self.side_x(y, z) + .02
            a.part('Hawse', 'Undercarriage').cyl(.32 * size, .12, loc=(s * x, y, z), rot=(0, R90, 0), seg=10,
                                                 bevel=0)
            anc = a.part('Anchors', 'Undercarriage')
            anc.box((.1, .16 * size, .9 * size), loc=(s * (x + .06), y + .05, z - .5 * size), rot=(0, 0, 0), bevel=0)
            anc.box((.12, .9 * size, .14), loc=(s * (x + .07), y + .05, z - .95 * size), bevel=0)
            # The chain from the hawse to the capstan.
            zc = self.deck_z(y + 2.2)
            a.part('Anchor_chain', 'Undercarriage').tube([(s * (self.half_beam(y) - .4), y + .2, self.deck_z(y) + .06),
                                                         (s * 1.0, y + 2.2, zc + .08)], .07, seg=4)
            k.lathe(a.part('Capstans', 'Steel'), [(.36, 0), (.36, .1), (.27, .2), (.27, .55), (.36, .65), (0, .65)],
                    loc=(s * 1.0, y + 2.6, zc), seg=10)

    def bollards(self, ys, inset=.55):
        bol = self.a.part('Bollards', 'Steel')
        for y in ys:
            for s in (-1, 1):
                for dy in (-.28, .28):
                    bol.cyl(.15, .42, loc=(s * (self.half_beam(y) - inset), y + dy, self.deck_z(y) + .22), seg=8,
                            bevel=0)

    def breakwater(self, y, w=None, h=.7):
        w = w or self.half_beam(y) * .75
        z = self.deck_z(y)
        bw = self.a.part('Breakwater', 'Armor')
        for s in (-1, 1):
            bw.limb((0, y - 1.0, z + h / 2), (s * w, y + .6, z + h / 2), .12, h, bevel=0)
        st = self.a.part('Breakwater_stays', 'Steel')
        for s in (-1, 1):
            for t in (.3, .65):
                st.box((.05, .5, h * .8), loc=(s * w * t, y - 1.0 + 1.6 * t + .3, z + h * .4), bevel=0)

    def jackstaff(self, h=2.0):
        y = self.bow + .6
        self.a.part('Flag_staffs', 'Steel').cyl(.04, h, loc=(0, y, self.deck_z(y) + h / 2), seg=6, bevel=0)
        y = self.stern - .3
        self.a.part('Flag_staffs', 'Steel').cyl(.045, h * 1.2, loc=(0, y, self.deck_z(y) + h * .6), seg=6, bevel=0)

    def stern_details(self):
        a = self.a
        y = self.stern
        z = self.deck_z(y)
        hb = self.half_beam(y)
        a.part('Stern_lights', 'Lamp').box((.3, .05, .2), loc=(0, y + .03, z - .4), bevel=0)
        for s in (-1, 1):
            a.part('Fairleads', 'Steel').box((.5, .3, .25), loc=(s * (hb - .6), y - .3, z + .13), bevel=.03)


# ============================================================================= structure
def tier(part, y0, y1, z0, z1, w0, w1=None, rf=0.0, rb=0.0, x=0.0, chamfer=.06):
    """A deckhouse tier: the footprint w0 half-wide at z0, the roof w1 half-wide at z1, the front raked back by rf and
    the back by rb (Burke / stealth walls lean inwards)."""
    w1 = w0 if w1 is None else w1
    k.sharp_loft(part, [[(x - w0, y0, z0), (x + w0, y0, z0), (x + w0, y1, z0), (x - w0, y1, z0)],
                        [(x - w1, y0 + rf, z1), (x + w1, y0 + rf, z1), (x + w1, y1 - rb, z1), (x - w1, y1 - rb, z1)]],
                 chamfer=chamfer)
    a = getattr(part, 'asset', None)
    if a is not None and y1 - y0 > 2.5:
        dress(a, y0, y1, z0, z1, w0, w1, rf, rb, x)


def dress(a, y0, y1, z0, z1, w0, w1, rf, rb, x=0.0):
    """A superstructure tier's fittings (the tiers of a part marked .asset): portholes along both walls, a louvred
    vent grille per side, the roof's edge rail along the sides, a dark roof walkway and a few roof boxes."""
    h = z1 - z0
    lean = (w0 - w1) / max(h, .1)
    seed = int(abs(y0) * 37 + abs(z0) * 11 + y1 * 5) % 997
    for s in (-1, 1):
        if h > 1.4:
            zp = z0 + h * .58
            xp = w0 + (w1 - w0) * .58
            n = max(1, int((y1 - y0 - 1.6) / 2.2))
            pts = [(x + s * (xp + .012), y0 + 1.0 + i * (y1 - y0 - 2.0) / max(1, n - 1 if n > 1 else 1), zp)
                   for i in range(n)]
            K.portholes(a, pts, (s, 0, lean), r=.17, seg=6)
            g = a.part('Wall_grilles', 'Undercarriage')
            zg = z0 + h * .35
            xg = x + s * (w0 + (w1 - w0) * .35 + .015)
            g.box((.03, .9, .55), loc=(xg, y1 - 1.2, zg), rot=(0, s * -math.atan(lean), 0), bevel=0)
            for j in range(4):
                g.box((.05, .86, .04), loc=(xg + s * .02, y1 - 1.2, zg - .2 + j * .13), rot=(0, s * -math.atan(lean), 0),
                      bevel=0)
        ya, yb = y0 + rf + .5, y1 - rb - .5
        if yb - ya > 1.5:
            K.railing(a.part('Roof_rails', 'Steel'), [(x + s * (w1 - .1), ya, z1), (x + s * (w1 - .1), yb, z1)], h=.75,
                      post=1.5, r=.022)
        # Fire boxes and a hose reel at the wall's foot, a lip round the roof edge.
        fb = a.part('Fire_boxes', 'BarrelRed')
        for t in (.3, .72):
            fb.box((.14, .32, .42), loc=(x + s * (w0 + .07), y0 + (y1 - y0) * t, z0 + .55), bevel=0)
        k.lathe(a.part('Hose_reels', 'Medical'), [(.22, -.07), (.22, .07)], loc=(x + s * (w0 + .09), y0 + (y1 - y0) * .5,
                                                                              z0 + .6), rot=(0, R90, 0), seg=10)
        a.part('Roof_lips', 'Armor').box((.08, y1 - y0 - rf - rb, .1), loc=(x + s * (w1 + .02), (y0 + rf + y1 - rb) / 2,
                                                                            z1 - .03), bevel=0)
    for yy, sgn in ((y0 + rf, -1), (y1 - rb, 1)):
        a.part('Roof_lips', 'Armor').box((2 * w1 + .1, .08, .1), loc=(x, yy + sgn * .02, z1 - .03), bevel=0)
    if y1 - y0 > 4 and w1 > 1.2:
        K.plane(a.part('Roof_walks', 'NavyDeck'), x - .45, x + .45, y0 + rf + .3, y1 - rb - .3, z1 + .012)
        K.clutter(a, 'Roof_boxes', 'Armor', x - w1 + .5, x - .6, y0 + rf + .6, y1 - rb - .6, z1, 2, seed=seed,
                  size=(.3, .8), height=(.2, .5), gap=.4)


def faceted(part, z0, z1, ring0, ring1, chamfer=.05):
    """A loft from one (x, y) outline at z0 to another at z1 (stealth deckhouses, gun houses)."""
    k.sharp_loft(part, [[(x, y, z0) for x, y in ring0], [(x, y, z1) for x, y in ring1]], chamfer=chamfer)


def windows(a, x0, x1, y, z, h=.45, tilt=0.0, n=None, name='Bridge_glass', facing=-1):
    """A band of window panes across the front (facing -1: forward, +1: aft) of a wall at y, leaning back by tilt."""
    n = n or max(2, int((x1 - x0) / .62))
    w = (x1 - x0) / n
    g = a.part(name, 'Glass')
    for i in range(n):
        g.box((w * .82, .03, h), loc=(x0 + w * (i + .5), y + facing * .02, z), rot=(facing * -tilt, 0, 0), bevel=0)


def side_windows(a, x, y0, y1, z, h=.4, n=None, name='Bridge_glass'):
    n = n or max(2, int((y1 - y0) / .7))
    w = (y1 - y0) / n
    s = 1 if x > 0 else -1
    g = a.part(name, 'Glass')
    for i in range(n):
        g.box((.03, w * .8, h), loc=(x + s * .02, y0 + w * (i + .5), z), bevel=0)


def doors(a, x, ys, z, s):
    d = a.part('Doors', 'Undercarriage')
    for y in ys:
        d.box((.04, .8, 1.6), loc=(x + s * .02, y, z + .85), bevel=0)


def funnel(a, at, w, d, h, rake=.12, taper=.85, name='Funnel', mat='Team', caps=2, cap_r=.35):
    """A raked funnel on its base: the casing, a dark cap band, the exhaust pipes, soot round the mouths."""
    x, y, z = at
    off = math.tan(rake) * h
    k.sharp_loft(a.part(name, mat), [[(x - w, y - d, z), (x + w, y - d, z), (x + w, y + d, z), (x - w, y + d, z)],
                                     [(x - w * taper, y - d * taper + off, z + h), (x + w * taper, y - d * taper + off, z + h),
                                      (x + w * taper, y + d * taper + off, z + h), (x - w * taper, y + d * taper + off, z + h)]],
                 chamfer=.08)
    a.part('Funnel_caps', 'Charred').box((2 * w * taper + .06, 2 * d * taper + .06, .35),
                                         loc=(x, y + off, z + h - .15), bevel=0)
    for i in range(caps):
        dx = 0 if caps == 1 else (i - (caps - 1) / 2) * (w * taper * 2 / caps)
        a.part('Exhausts', 'Steel').cyl(cap_r, .7, loc=(x + dx, y + off, z + h + .3), seg=10, bevel=0)
        a.part('Exhaust_mouths', 'Charred').cyl(cap_r * .8, .02, loc=(x + dx, y + off, z + h + .66), seg=10, bevel=0)
    K.soot(a, (x, y + off, z + h + .6), radius=max(w, d) * 1.6, k=.5)


def lattice_mast(a, base, top_z, w0, w1, name='Mast_steel', braces=3):
    """A four-legged lattice mast from base (x, y, z) to top_z, w0 / w1 half-wide at the foot / head."""
    x, y, z = base
    p = a.part(name, 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.tube([(x + sx * w0, y + sy * w0, z), (x + sx * w1, y + sy * w1, top_z)], .07, seg=4)
    for i in range(1, braces + 1):
        t = i / (braces + 1)
        zz = z + (top_z - z) * t
        ww = w0 + (w1 - w0) * t
        sq = [(x - ww, y - ww, zz), (x + ww, y - ww, zz), (x + ww, y + ww, zz), (x - ww, y + ww, zz), (x - ww, y - ww, zz)]
        p.tube(sq, .04, seg=4)
        zn = z + (top_z - z) * (i + 1) / (braces + 1)
        wn = w0 + (w1 - w0) * (i + 1) / (braces + 1)
        p.tube([(x - ww, y - ww, zz), (x + wn, y - wn, zn)], .03, seg=4)
        p.tube([(x + ww, y + ww, zz), (x - wn, y + wn, zn)], .03, seg=4)
    k.block(a.part('Mast_platforms', 'Armor'), (2 * w1 + .9, 2 * w1 + .9, .1), loc=(x, y, top_z - .05), chamfer=.03)
    K.railing(a.part('Roof_rails', 'Steel'), [(x - w1 - .4, y - w1 - .4, top_z), (x + w1 + .4, y - w1 - .4, top_z),
                                              (x + w1 + .4, y + w1 + .4, top_z), (x - w1 - .4, y + w1 + .4, top_z),
                                              (x - w1 - .4, y - w1 - .4, top_z)], h=.6, post=.9, r=.02)
    for s in (-1, 1):
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.18, .18, .18), loc=(x + s * (w1 + .45), y,
                                                                                         top_z + .15), bevel=0)


def yards(a, at, span, n=2, gap=1.0, name='Mast_steel'):
    x, y, z = at
    p = a.part(name, 'Steel')
    for i in range(n):
        p.box((span * (1 - .25 * i), .12, .12), loc=(x, y, z + i * gap), bevel=0)
        for s in (-1, 1):
            p.box((.05, .05, .6), loc=(x + s * span * (1 - .25 * i) * .45, y, z + i * gap - .3), bevel=0)


def radar(a, at, w=2.6, h=.8, style='bar'):
    """The spinning air-search radar on its pivot `Radar` (set node, ModelLibrary turns it)."""
    a.pivot('Radar', at)
    if style == 'bar':
        k.block(a.part('Radar_array', 'Armor', 'Radar'), (w, .3, h), loc=(0, 0, h / 2 + .25), chamfer=.05)
        a.part('Radar_face', 'Undercarriage', 'Radar').box((w * .94, .03, h * .8), loc=(0, -.17, h / 2 + .25), bevel=0)
    elif style == 'mesh':     # an open lattice reflector (SPS-49 / Top Pair read)
        g = a.part('Radar_array', 'Armor', 'Radar')
        for i in range(5):
            g.box((w, .05, .05), loc=(0, .1, .3 + i * h / 4), bevel=0)
        for i in range(7):
            g.box((.05, .05, h), loc=(-w / 2 + i * w / 6, .1, .3 + h / 2), bevel=0)
        a.part('Radar_face', 'Undercarriage', 'Radar').box((.4, .5, .4), loc=(0, -.25, .3 + h / 2), bevel=.04)
    else:                     # 'back-to-back': two faces (Top Plate read)
        k.block(a.part('Radar_array', 'Armor', 'Radar'), (w, .5, h), loc=(0, 0, h / 2 + .25), chamfer=.05)
        for s in (-1, 1):
            a.part('Radar_face', 'Undercarriage', 'Radar').box((w * .9, .03, h * .75), loc=(0, s * .27, h / 2 + .25),
                                                              bevel=0)
    a.part('Radar_pedestal', 'Steel', 'Radar').cyl(.18, .4, loc=(0, 0, .1), seg=10, bevel=0)


def aps(a, at, r=.32):
    """`Mount_APS`: the hard-kill interceptor (the def's "aps") as a small sensor head with its launch tubes."""
    m = a.pivot('Mount_APS', at)
    k.lathe(a.part('Aps_head', 'Medical', m), [(r, 0), (r, r * .6), (r * .7, r * 1.2), (0, r * 1.35)], seg=12)
    t = a.part('Aps_tubes', 'Undercarriage', m)
    for s in (-1, 1):
        t.cyl(.07, .5, loc=(s * r * 1.3, -.05, r * .5), rot=(R90 - .5, 0, 0), seg=6, bevel=0)
    return m


def spy_face(a, loc, normal, r=1.05, name='Array_faces'):
    """An octagonal phased-array face (Aegis read) on a wall facing `normal`, with its rim."""
    rot = K.rot_to(normal)
    pts = [(r * math.cos(i * TAU / 8 + TAU / 16), r * math.sin(i * TAU / 8 + TAU / 16)) for i in range(8)]
    k.extrude(a.part(name, 'Undercarriage'), pts, .06, loc=loc, rot=rot, axis='Z', chamfer=.02)
    m = K.frame(loc, rot)
    rim = [tuple(m @ Vector((x * 1.12, y * 1.12, -.02))) for x, y in pts]
    a.part('Array_rims', 'Armor').tube(rim + [rim[0]], .05, seg=4)


def flat_array(a, loc, normal, w, h, name='Array_faces'):
    """A square flush array panel (Type 055 / stealth read)."""
    rot = K.rot_to(normal)
    k.extrude(a.part(name, 'Undercarriage'), [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], .05,
              loc=loc, rot=rot, axis='Z', chamfer=.015)


def boat(a, at, length=4.2, beam=1.6, davit=True, s=1):
    """A RHIB with its davit arms (both from the kit), on a deck at at = (x, y, z)."""
    x, y, z = at
    K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (x, y, z + .5), length=length, beam=beam)
    if davit:
        dav = a.part('Davits', 'Steel')
        for dy in (-length * .38, length * .38):
            dav.tube([(x - s * beam * .9, y + dy, z), (x - s * beam * .9, y + dy, z + 2.1), (x, y + dy, z + 2.3)],
                     .08, seg=6)
            a.part('Kit_cables', 'Undercarriage').tube([(x, y + dy, z + 2.3), (x, y + dy * .8, z + 1.3)], .02, seg=3)


def life_rafts(a, x, ys, z, s):
    for y in ys:
        k.lathe(a.part('Life_rafts', 'Medical'), [(.3, -.5), (.34, -.45), (.34, .45), (.3, .5)],
                loc=(x, y, z + .34), rot=FWD, seg=8)
        a.part('Raft_cradles', 'Steel').box((.5, .9, .1), loc=(x, y, z + .05), bevel=0)


def vents(a, pts, name='Vents'):
    v = a.part(name, 'Armor')
    for (x, y, z) in pts:
        v.cyl(.18, .5, loc=(x, y, z + .25), seg=8, bevel=0)
        v.cyl(.24, .08, loc=(x, y, z + .52), seg=8, bevel=0)


def heli_deck(a, ship, y0, y1, circle=True):
    """Flight deck markings: the touchdown circle, centre line, the yellow deck edge lines, the safety nets."""
    z = ship.deck_z((y0 + y1) / 2) + .024
    yc = (y0 + y1) / 2
    marks = a.part('Deck_marks', 'PlasterWhite')
    if circle:
        r = min(ship.half_beam(yc) * .62, (y1 - y0) * .38)
        k.ring(marks, [(r - .12, z), (r, z), (r, z + .01), (r - .12, z + .01)], loc=(0, yc, 0), seg=24)
    marks.box((.14, y1 - y0 - .6, .01), loc=(0, yc, z), bevel=0)
    lines = a.part('Deck_lines', 'Hazard')
    for s in (-1, 1):
        K.plane(lines, s * (ship.half_beam(yc) - .35) - .06, s * (ship.half_beam(yc) - .35) + .06, y0 + .3, y1 - .3, z)
    nets = a.part('Deck_nets', 'Steel')
    for s in (-1, 1):
        n = int((y1 - y0) / 1.1)
        for i in range(n):
            y = y0 + .6 + i * 1.1
            nets.box((.6, 1.0, .02), loc=(s * (ship.half_beam(y) + .2), y, ship.deck_z(y) - .08), rot=(0, s * -.25, 0),
                     bevel=0)


# ============================================================================= guns
def gun_127(a, i, at, style='mod4', s=1.0, barrel=5.6, base=.45):
    """A 127 mm single gun on `Mount_gun[_NN]`: the deck coaming and the training base, the gun house (Mk 45 Mod 4:
    faceted stealth shield; Mod 2: the rounded front), the embrasure, the long 62- or 54-calibre barrel with its
    muzzle ring (Gun_barrels / Gun_muzzles kick back on each shot), roof hatch and vents. at = deck point."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    k.lathe(a.part('Gun_base' + n, 'Armor'), [(1.5 * s, 0), (1.5 * s, base * .6), (1.35 * s, base), (0, base)],
            loc=(x, y, z), seg=20)
    m = a.pivot('Mount_gun' + t, (x, y + .2 * s, z + base))
    house = a.part('Gun_house' + n, 'Team', m)
    if style == 'mod4':
        r0 = [(-.6, -2.0), (.6, -2.0), (1.15, -.9), (1.15, 1.7), (.8, 2.0), (-.8, 2.0), (-1.15, 1.7), (-1.15, -.9)]
        r1 = [(-.42, -1.2), (.42, -1.2), (.85, -.55), (.9, 1.45), (.62, 1.7), (-.62, 1.7), (-.9, 1.45), (-.85, -.55)]
        hh = 1.35
    else:
        r0 = [(-.55, -1.95), (.55, -1.95), (1.0, -1.6), (1.2, -.9), (1.2, 1.9), (-1.2, 1.9), (-1.2, -.9), (-1.0, -1.6)]
        r1 = [(-.5, -1.7), (.5, -1.7), (.9, -1.4), (1.08, -.8), (1.08, 1.8), (-1.08, 1.8), (-1.08, -.8), (-.9, -1.4)]
        hh = 1.5
    faceted(house, 0, hh * s, [(p * s, q * s) for p, q in r0], [(p * s, q * s) for p, q in r1], chamfer=.05 * s)
    a.part('Gun_slot' + n, 'Undercarriage', m).box((.36 * s, .05, .62 * s),
                                                    loc=(0, (-1.62 if style == 'mod4' else -1.9) * s, .6 * s), bevel=0)
    zb = .62 * s
    y0 = (-1.4 if style == 'mod4' else -1.6) * s
    k.lathe(a.part('Gun_barrels' + n, 'Steel', m), [(.15 * s, 0), (.15 * s, .35 * s), (.1 * s, .55 * s),
                                                    (.085 * s, barrel * s - .1), (0, barrel * s - .1)],
            loc=(0, y0, zb), rot=FWD, seg=12)
    k.lathe(a.part('Gun_muzzles' + n, 'Undercarriage', m), [(.11 * s, 0), (.11 * s, .14 * s), (.06 * s, .15 * s),
                                                            (0, .15 * s)], loc=(0, y0 - barrel * s + .14, zb), rot=FWD,
            seg=12)
    a.pivot('Muzzle_gun' + t, (0, y0 - barrel * s, zb), m)
    roof = a.part('Gun_roof' + n, 'Armor', m)
    k.block(roof, (.6 * s, .6 * s, .14 * s), loc=(.35 * s, .9 * s, hh * s + .05), chamfer=.03)
    roof.cyl(.12 * s, .3 * s, loc=(-.45 * s, 1.1 * s, hh * s + .15), seg=8, bevel=0)
    a.part('Gun_fittings' + n, 'Steel', m).box((.04, .5 * s, .04), loc=(1.1 * s, .6 * s, .9 * s), bevel=0)
    K.soot(a, (x, y - barrel * s - 1.2 * s, z + base + zb), radius=.9 * s, k=.3)


def gun_stealth(a, i, at, s=1.0, barrel=4.6, base=.4):
    """A 100-130 mm stealth gun on `Mount_gun[_NN]` (A-190 / H-PJ-87 read): a low angular house in steep facets, the
    flat roof with its sensor block, a thick jacketed barrel with a fume extractor and muzzle brake."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    k.lathe(a.part('Gun_base' + n, 'Armor'), [(1.35 * s, 0), (1.35 * s, base * .6), (1.2 * s, base), (0, base)],
            loc=(x, y, z), seg=8)
    m = a.pivot('Mount_gun' + t, (x, y, z + base))
    r0 = [(0, -2.1), (.7, -1.6), (1.05, -.6), (1.05, 1.5), (.7, 1.9), (-.7, 1.9), (-1.05, 1.5), (-1.05, -.6), (-.7, -1.6)]
    r1 = [(0, -1.25), (.45, -1.0), (.75, -.35), (.78, 1.3), (.5, 1.6), (-.5, 1.6), (-.78, 1.3), (-.75, -.35),
          (-.45, -1.0)]
    faceted(a.part('Gun_house' + n, 'Team', m), 0, 1.25 * s, [(p * s, q * s) for p, q in r0],
            [(p * s, q * s) for p, q in r1], chamfer=.04 * s)
    zb = .58 * s
    y0 = -1.5 * s
    k.lathe(a.part('Gun_barrels' + n, 'Steel', m), [(.17 * s, 0), (.17 * s, .5 * s), (.11 * s, .7 * s),
                                                    (.1 * s, barrel * s * .45), (.15 * s, barrel * s * .5),
                                                    (.15 * s, barrel * s * .6), (.1 * s, barrel * s * .65),
                                                    (.1 * s, barrel * s - .35 * s), (0, barrel * s - .35 * s)],
            loc=(0, y0, zb), rot=FWD, seg=12)
    k.lathe(a.part('Gun_muzzles' + n, 'Undercarriage', m), [(.15 * s, 0), (.15 * s, .35 * s), (.08 * s, .36 * s),
                                                            (0, .36 * s)], loc=(0, y0 - barrel * s + .36 * s, zb),
            rot=FWD, seg=10)
    a.pivot('Muzzle_gun' + t, (0, y0 - barrel * s, zb), m)
    k.block(a.part('Gun_roof' + n, 'Armor', m), (.7 * s, .5 * s, .3 * s), loc=(0, .8 * s, 1.25 * s + .15), chamfer=.04)
    K.soot(a, (x, y + y0 - barrel * s, z + base + zb), radius=.8 * s, k=.3)


def heavy_turret(a, i, at, s=1.0, barrels=1, barrel=10.0, cal=.42, base_h=1.0, base_r=2.6, elev=.03,
                 rangefinder=True, house_mat='Team', width=1.0, pitch=1.25, rise=False):
    """A heavy turret on `Mount_gun[_NN]` (Iowa / Alaska / monitor read): the armoured barbette (static, base_h above
    the deck point `at`), the gun house with the sloped face plate, flat sides, the rear overhang and its bevels, the
    sighting hoods and roof vents, the rangefinder ears at the rear; per barrel a canvas blast bag and the long tapered
    barrel with its muzzle swell. A twin gets `Muzzle_b1_gun` / `Muzzle_b2_gun` under its muzzle (each barrel fires).
    Barrels pass (owner 06/10): a triple (Iowa) takes `width` (the house's breadth) and `pitch` (x s, the gap between
    barrels) so its three blast bags sit apart on the face; it gets a third sight hood on the roof's centre line, a gun
    port plate behind each bag and `Muzzle_b1..3_gun[_NN]` left to right (all three fire in one volley)."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    bar = a.part('Barbettes', 'Armor')
    k.lathe(bar, [(base_r * s, -.3), (base_r * s, base_h - .12), (base_r * s - .1, base_h), (0, base_h)],
            loc=(x, y, z), seg=28, worn=(2,))
    m = a.pivot('Mount_gun' + t, (x, y, z + base_h))
    w, f, r, h = 2.35 * s * width, -3.0 * s, 3.4 * s, 2.3 * s
    r0 = [(-w * .74, f), (w * .74, f), (w, f + 1.1 * s), (w, r), (w * .82, r + .5 * s), (-w * .82, r + .5 * s),
          (-w, r), (-w, f + 1.1 * s)]
    fz = 1.9 * s       # the face plate leans back above this
    r1 = [(-w * .72, f + .2 * s), (w * .72, f + .2 * s), (w * .98, f + 1.2 * s), (w * .98, r), (w * .8, r + .45 * s),
          (-w * .8, r + .45 * s), (-w * .98, r), (-w * .98, f + 1.2 * s)]
    r2 = [(-w * .62, f + 1.5 * s), (w * .62, f + 1.5 * s), (w * .9, f + 2.1 * s), (w * .9, r - .1 * s),
          (w * .72, r + .3 * s), (-w * .72, r + .3 * s), (-w * .9, r - .1 * s), (-w * .9, f + 2.1 * s)]
    house = a.part('Gun_house' + n, house_mat, m)
    k.sharp_loft(house, [[(p, q, 0) for p, q in r0], [(p, q, fz) for p, q in r1], [(p, q, h) for p, q in r2]],
                 chamfer=.08 * s)
    a.part('Gun_roof' + n, 'Armor', m).box((w * 1.5, (r - f) * .55, .05), loc=(0, (f + r) / 2 + .6 * s, h + .02),
                                          bevel=0)
    hoods = a.part('Sight_hoods' + n, 'Armor', m)
    for sx in (-1, 1):
        k.block(hoods, (.55 * s, .9 * s, .35 * s), loc=(sx * w * .62, f + 2.4 * s, h + .17 * s), chamfer=.05 * s)
    if barrels == 3:
        # The Iowa's centre sight hood (the turret officer's), a little behind the side pair.
        k.block(hoods, (.5 * s, .8 * s, .3 * s), loc=(0, f + 2.9 * s, h + .15 * s), chamfer=.05 * s)
    v = a.part('Gun_vents' + n, 'Armor', m)
    for sx in (-1, 1):
        v.cyl(.16 * s, .35 * s, loc=(sx * .5 * s, r - .8 * s, h + .17 * s), seg=8, bevel=0)
    if rangefinder:
        rf = a.part('Rangefinder' + n, 'Armor', m)
        rf.box((2 * w + 1.6 * s, .45 * s, .45 * s), loc=(0, r - .4 * s, h - .5 * s), bevel=.04 * s)
        for sx in (-1, 1):
            rf.cyl(.26 * s, .12 * s, loc=(sx * (w + .8 * s), r - .4 * s, h - .5 * s), rot=(0, R90, 0), seg=10, bevel=0)
    a.part('Gun_ladders' + n, 'Steel', m).box((.5 * s, .04, .04), loc=(0, r + .52 * s, .6 * s), bevel=0)
    xs = [0.0] if barrels == 1 else [-.95 * s, .95 * s] if barrels == 2 else [-pitch * s, 0, pitch * s]
    zb = 1.05 * s
    L = barrel * s
    dz = math.sin(elev) * L
    # Barrels pass 06/10: rise=True lifts the barrels by elev so the bores meet the muzzles (without it they dip by elev,
    # 2 x dz under the muzzle; the monitor and battlecruiser keep that until their own rework).
    tilt = R90 - elev if rise else R90 + elev
    for bx in xs:
        if barrels == 3:
            # The gun port plate on the face, behind the bag (proud of the face by 2-6 cm: no coplanar faces).
            fy = f + .2 * s * (zb / fz)
            # (in the hoods' armour mesh: no renderer of its own)
            a.part('Sight_hoods' + n, 'Armor', m).box((cal * 4.0 * s, .06, cal * 4.4 * s), loc=(bx, fy - .04, zb),
                                                     bevel=.02)
        k.lathe(a.part('Blast_bags' + n, 'Canvas', m), [(cal * 1.55 * s, 0), (cal * 1.8 * s, .2 * s),
                                                       (cal * 1.65 * s, .45 * s), (cal * 1.3 * s, .6 * s)],
                loc=(bx, f + .2 * s, zb), rot=(tilt, 0, 0), seg=12)
        k.lathe(a.part('Gun_barrels' + n, 'Steel', m), [(cal * 1.25 * s, 0), (cal * 1.25 * s, L * .22),
                                                       (cal * .95 * s, L * .3), (cal * .78 * s, L * .93),
                                                       (cal * .88 * s, L * .965), (cal * .85 * s, L),
                                                       (0, L)], loc=(bx, f + .4 * s, zb), rot=(tilt, 0, 0),
                seg=14, worn=(4,))
        a.part('Gun_muzzles' + n, 'Undercarriage', m).cyl(cal * .5 * s, .03, loc=(bx, f + .4 * s - L - .015,
                                                                                  zb + dz), rot=FWD, seg=10, bevel=0)
    mz = a.pivot('Muzzle_gun' + t, (0, f + .4 * s - L, zb + dz), m)
    if barrels > 1:
        for j, bx in enumerate(xs):
            a.pivot(f'Muzzle_b{j + 1}_gun{t}', (bx, 0, 0), mz)
    K.soot(a, (x, y + f - L, z + base_h + zb + dz), radius=1.4 * s, k=.35)


# ============================================================================= CIWS
def phalanx(a, i, at, s=1.0, ped=.5):
    """A Phalanx-read CIWS on `Mount_mg[_NN]`: the pedestal on its deck, the white radome on its stalk, the search
    antenna, the gatling with its shroud, the ammunition drum; at = deck point."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    k.lathe(a.part('CIWS_base' + n, 'Armor'), [(.62 * s, 0), (.55 * s, ped), (.45 * s, ped + .05), (0, ped + .05)],
            loc=(x, y, z), seg=12)
    m = a.pivot('Mount_mg' + t, (x, y, z + ped + .05))
    k.lathe(a.part('CIWS_mount' + n, 'Armor', m), [(.5 * s, 0), (.5 * s, .2 * s), (.35 * s, .3 * s), (0, .3 * s)],
            seg=12)
    k.block(a.part('CIWS_drum' + n, 'Medical', m), (.9 * s, .9 * s, .75 * s), loc=(0, .25 * s, .7 * s),
            chamfer=.08 * s)
    k.lathe(a.part('CIWS_dome' + n, 'Medical', m), [(.4 * s, 0), (.44 * s, .25 * s), (.4 * s, .55 * s),
                                                    (.25 * s, .78 * s), (0, .84 * s)], loc=(0, .05 * s, 1.08 * s),
            seg=14, worn=(2,))
    a.part('CIWS_ant' + n, 'Undercarriage', m).box((.5 * s, .05, .3 * s), loc=(0, -.35 * s, 1.45 * s), bevel=0)
    g = a.part('CIWS_gun' + n, 'Steel', m)
    for j in range(6):
        u = j * TAU / 6
        g.cyl(.022 * s, 1.2 * s, loc=(math.cos(u) * .07 * s, -.95 * s, .62 * s + math.sin(u) * .07 * s), rot=FWD,
              seg=5, bevel=0)
    g.cyl(.13 * s, .4 * s, loc=(0, -.5 * s, .62 * s), rot=FWD, seg=10, bevel=0)
    g.cyl(.12 * s, .1 * s, loc=(0, -1.4 * s, .62 * s), rot=FWD, seg=10, bevel=0)
    a.pivot('Muzzle_mg' + t, (0, -1.6 * s, .62 * s), m)


def ak630(a, i, at, s=1.0, ped=.25, style='ak630'):
    """An AK-630 (or the bigger Type 1130, style='1130') CIWS on `Mount_mg[_NN]`: the low domed / faceted house on its
    deck ring, the rotating gun's cylinder with its multi-barrel cluster and the flash hider."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    k.lathe(a.part('CIWS_base' + n, 'Armor'), [(.85 * s, 0), (.85 * s, ped), (.75 * s, ped + .05), (0, ped + .05)],
            loc=(x, y, z), seg=14)
    m = a.pivot('Mount_mg' + t, (x, y, z + ped + .05))
    if style == 'ak630':
        k.lathe(a.part('CIWS_house' + n, 'Team', m), [(.75 * s, 0), (.75 * s, .35 * s), (.6 * s, .7 * s),
                                                      (.3 * s, .88 * s), (0, .92 * s)], seg=14, worn=(2,))
        nb, br, L = 6, .07, 1.3
    else:
        faceted(a.part('CIWS_house' + n, 'Team', m), 0, 1.0 * s,
                [(-.75 * s, -.6 * s), (.75 * s, -.6 * s), (.85 * s, .9 * s), (-.85 * s, .9 * s)],
                [(-.5 * s, -.3 * s), (.5 * s, -.3 * s), (.6 * s, .75 * s), (-.6 * s, .75 * s)], chamfer=.05 * s)
        a.part('CIWS_sensor' + n, 'Medical', m).box((.5 * s, .4 * s, .35 * s), loc=(0, .4 * s, 1.17 * s), bevel=.04)
        nb, br, L = 11, .1, 1.6
    g = a.part('CIWS_gun' + n, 'Steel', m)
    g.cyl(.2 * s, .5 * s, loc=(0, -.7 * s, .5 * s), rot=FWD, seg=10, bevel=0)
    for j in range(nb):
        u = j * TAU / nb
        g.cyl(.022 * s, L * s, loc=(math.cos(u) * br * s, -.95 * s - L * s / 2, .5 * s + math.sin(u) * br * s),
              rot=FWD, seg=5, bevel=0)
    g.cyl(br * 1.5 * s, .14 * s, loc=(0, -.95 * s - L * s, .5 * s), rot=FWD, seg=10, bevel=0)
    a.pivot('Muzzle_mg' + t, (0, -1.05 * s - L * s, .5 * s), m)


# ============================================================================= missile launchers
def _mount(a, slot, i, loc, cells=(), cell_tag=None):
    """A fixed launcher's mount pivot: only the muzzle, with the launch cells (Muzzle_b<k>_<tag>) near it."""
    t = tag(i)
    m = a.pivot(f'Mount_{slot}{t}', loc)
    mz = a.pivot(f'Muzzle_{slot}{t}', (0, 0, 0), m)
    ct = cell_tag or (slot + t)
    for j, p in enumerate(cells):
        a.pivot(f'Muzzle_b{j + 1}_{ct}', p, mz)
    return m


def vls(a, i, at, cols, rows, cell=.7, raised=.0, slot='missile', points=4, opened=(), name='Vls', big=False,
        mat='Team'):
    """A VLS field at deck point at = (x, y, z): an optional raised module (`raised` high), the coaming, the cell
    hatches in their grid with hinges, the exhaust uptakes between the columns, a few cells open (the canister tops
    and frangible covers). The mount pivot sits above the field's centre with `points` launch cells nearest it."""
    x, y, z = at
    W, D = cols * cell / 2 + .25, rows * cell / 2 + .25
    top = z + raised
    if raised > 0:
        tier(a.part(name + '_module', mat), y - D, y + D, z - .05, top, W + .12, W, rf=.12, rb=.12, x=x, chamfer=.04)
    a.part(name + '_coaming', 'Charred').box((2 * W, 2 * D, .08), loc=(x, y, top + .03), bevel=.01)
    hat = a.part(name + '_hatches', 'Team')
    dark = a.part(name + '_cells', 'Charred')
    hng = a.part(name + '_hinges', 'Steel')
    centres = []
    for c in range(cols):
        for r in range(rows):
            cx = x + (c - (cols - 1) / 2) * cell
            cy = y + (r - (rows - 1) / 2) * cell
            centres.append((cx, cy))
            if (c, r) in opened:
                dark.box((cell * .8, cell * .8, .02), loc=(cx, cy, top + .075), bevel=0)
                k.lathe(a.part(name + '_noses', 'Medical'), [(cell * .22, 0), (cell * .2, cell * .1), (cell * .1, cell * .2),
                                                             (0, cell * .24)], loc=(cx, cy, top + .07), seg=8)
                hat.box((cell * .8, .04, cell * .8), loc=(cx, cy - cell * .43, top + .07 + cell * .4),
                        rot=(.15, 0, 0), bevel=0)
            else:
                k.block(hat, (cell * .84, cell * .84, .05 if not big else .1), loc=(cx, cy, top + .1),
                        chamfer=.01 if not big else .03)
                if big:
                    hat.box((cell * .5, cell * .08, .04), loc=(cx, cy, top + .17), bevel=0)
            hng.box((cell * .7, .04, .04), loc=(cx, cy + cell * .42, top + .1), bevel=0)
    lines = a.part('Deck_lines', 'Hazard')
    for x0, x1, y0, y1 in ((x - W, x + W, y - D - .12, y - D - .02), (x - W, x + W, y + D + .02, y + D + .12)):
        K.plane(lines, x0, x1, y0, y1, top + .075)
    pts = sorted(centres, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)[:points]
    _mount(a, slot, i, (x, y, top + .2), cells=[(cx - x, cy - y, 0) for cx, cy in pts])
    return top


def inclined_cells(a, i, at, cols, rows, cell=1.3, slot='missile', points=4, raised=.6, tilt=.5, mat='Team'):
    """An inclined-cell anti-ship deck (Granit read): a raised armoured module with big square hatches tilted forward
    in a grid, each with its hinge bar and the deck lines; the pivot carries the launch cells nearest its centre."""
    x, y, z = at
    W, D = cols * cell / 2 + .35, rows * cell / 2 + .35
    top = z + raised
    tier(a.part('Cell_module', mat), y - D, y + D, z - .05, top, W + .15, W, rf=.25, rb=.1, x=x, chamfer=.05)
    hat = a.part('Cell_hatches', 'Armor')
    hng = a.part('Cell_hinges', 'Steel')
    dark = a.part('Cell_seams', 'Undercarriage')
    centres = []
    for c in range(cols):
        for r in range(rows):
            cx = x + (c - (cols - 1) / 2) * cell
            cy = y + (r - (rows - 1) / 2) * cell
            centres.append((cx, cy))
            dark.box((cell * .92, cell * .92, .02), loc=(cx, cy, top + .01), bevel=0)
            k.block(hat, (cell * .84, cell * .84, .1), loc=(cx, cy, top + .1), rot=(-tilt * .2, 0, 0), chamfer=.03)
            hat.cyl(cell * .22, .06, loc=(cx, cy, top + .2), seg=10, bevel=0)
            hng.box((cell * .8, .07, .07), loc=(cx, cy + cell * .44, top + .1), bevel=0)
    pts = sorted(centres, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)[:points]
    _mount(a, slot, i, (x, y, top + .3), cells=[(cx - x, cy - y, 0) for cx, cy in pts])
    return top


def revolvers(a, i, at, cols, rows, r=.75, pitch=1.9, slot='missile', points=4):
    """S-300F revolver hatches (Fort read): round flush covers in a grid, each with its rim, the eight-sector cover
    seams and a hinge; the pivot carries the launch cells nearest the centre."""
    x, y, z = at
    rim = a.part('Revolver_rims', 'Armor')
    cov = a.part('Revolver_covers', 'Medical')
    seam = a.part('Revolver_seams', 'Undercarriage')
    centres = []
    for c in range(cols):
        for rr in range(rows):
            cx = x + (c - (cols - 1) / 2) * pitch
            cy = y + (rr - (rows - 1) / 2) * pitch
            centres.append((cx, cy))
            k.ring(rim, [(r, z), (r + .18, z), (r + .14, z + .14), (r, z + .14)], loc=(cx, cy, 0), seg=20)
            cov.cyl(r, .1, loc=(cx, cy, z + .07), seg=20, bevel=.02)
            for j in range(4):
                seam.box((2 * r - .05, .04, .02), loc=(cx, cy, z + .125), rot=(0, 0, j * math.pi / 4), bevel=0)
            cov.cyl(.16, .05, loc=(cx, cy, z + .15), seg=8, bevel=0)
    pts = sorted(centres, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)[:points]
    _mount(a, slot, i, (x, y, z + .25), cells=[(cx - x, cy - y, 0) for cx, cy in pts])


def _missile(a, part_body, part_tip, loc, r, length, direction, fins_part=None):
    """A missile body from its tail at loc towards `direction` (white body, dark radome, four tail fins)."""
    rot = K.rot_to(direction)
    k.lathe(part_body, [(0, 0), (r * .85, .03), (r, .1), (r, length * .8), (r * .8, length * .93), (r * .3, length)],
            loc=loc, rot=rot, seg=10)
    k.lathe(part_tip, [(r * .3, length - .005), (0, length + r * .4)], loc=loc, rot=rot, seg=10, caps=(False, False))
    if fins_part is not None:
        m = K.frame(loc, rot)
        for j in range(4):
            u = j * TAU / 4 + TAU / 8
            c, s_ = math.cos(u), math.sin(u)
            tx, ty = -s_ * .012, c * .012
            quad = [(c * r, s_ * r, .05), (c * r * 2.6, s_ * r * 2.6, .1), (c * r * 2.6, s_ * r * 2.6, length * .14),
                    (c * r, s_ * r, length * .2)]
            vs = [tuple(m @ Vector((p[0] + tx * e, p[1] + ty * e, p[2]))) for e in (-1, 1) for p in quad]
            fins_part.mesh(vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])


def mk26(a, i, at, slot='missile', s=1.0, msl=4.6, mag=True):
    """A Mk 26-read twin-arm launcher on `Mount_<slot>[_NN]`: the magazine deck house (static), the training
    pedestal, the two guide arms each with a big white SAM hung under it at the loading elevation, the blast deflector,
    the blast doors of the loader; launch cells `Muzzle_b1/2` at the noses."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    if mag:
        tier(a.part('Launcher_house' + n, 'Team'), y - 2.4 * s, y + 2.6 * s, z - .05, z + .55 * s, 2.0 * s, 1.85 * s,
             rf=.2, rb=.2, x=x)
        a.part('Blast_doors' + n, 'Undercarriage').box((1.6 * s, 1.0 * s, .03), loc=(x, y + 1.6 * s, z + .57 * s),
                                                       bevel=0)
    zt = z + (.55 * s if mag else 0)
    k.lathe(a.part('Launcher_base' + n, 'Armor'), [(1.0 * s, 0), (1.0 * s, .25 * s), (.85 * s, .35 * s), (0, .35 * s)],
            loc=(x, y - .6 * s, zt), seg=16)
    m = a.pivot(f'Mount_{slot}{t}', (x, y - .6 * s, zt + .35 * s))
    k.block(a.part('Launcher_ped' + n, 'Team', m), (1.2 * s, 1.3 * s, 1.1 * s), loc=(0, 0, .55 * s), chamfer=.1 * s)
    arm = a.part('Launcher_arms' + n, 'Team', m)
    el = .4
    tips = []
    for sx in (-1, 1):
        ax = sx * .95 * s
        arm.box((.3 * s, .5 * s, .5 * s), loc=(sx * .7 * s, 0, 1.0 * s), bevel=.04)
        a0 = Vector((ax, .6 * s, 1.05 * s))
        d = Vector((0, -math.cos(el), math.sin(el)))
        arm.limb(tuple(a0), tuple(a0 + d * (msl * s * .85)), .13 * s, .14 * s, bevel=.02)
        tail = a0 + d * (-.3 * s) + Vector((0, 0, -.3 * s))
        _missile(a, a.part('Launcher_missiles' + n, 'Medical', m), a.part('Missile_tips' + n, 'Undercarriage', m),
                 tuple(tail), .2 * s, msl * s, tuple(d), a.part('Missile_fins' + n, 'Armor', m))
        tips.append(tuple(tail + d * (msl * s)))
    a.part('Launcher_deflector' + n, 'Steel', m).box((2.2 * s, .1, .8 * s), loc=(0, 1.0 * s, .8 * s),
                                                    rot=(.5, 0, 0), bevel=0)
    mid = (Vector(tips[0]) + Vector(tips[1])) / 2
    mz = a.pivot(f'Muzzle_{slot}{t}', tuple(mid), m)
    for j, p in enumerate(tips):
        a.pivot(f'Muzzle_b{j + 1}_{slot}{t}', tuple(Vector(p) - mid), mz)


def box_launcher(a, i, at, slot='missile', s=1.0, cols=4, rows=2, el=.28, length=3.4, style='mk29'):
    """A trainable box launcher on `Mount_<slot>[_NN]` (Mk 29 Sea Sparrow eight-cell box, or style='ram' a 21/24-round
    RAM / HQ-10 box with round cells): the pedestal, the trunnion arms, the elevated box with its cell doors; the
    launch cells at the box mouth."""
    x, y, z = at
    t, n = tag(i), sfx(i)
    k.lathe(a.part('Launcher_base' + n, 'Armor'), [(.8 * s, 0), (.8 * s, .2 * s), (.65 * s, .3 * s), (0, .3 * s)],
            loc=(x, y, z), seg=14)
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + .3 * s))
    k.block(a.part('Launcher_ped' + n, 'Team', m), (1.0 * s, 1.0 * s, .8 * s), loc=(0, .2 * s, .4 * s), chamfer=.08 * s)
    W = cols * .42 * s / 2 + .1 * s
    H = rows * .42 * s / 2 + .1 * s
    for sx in (-1, 1):
        a.part('Launcher_arms' + n, 'Armor', m).box((.15 * s, .7 * s, 1.0 * s), loc=(sx * (W + .12 * s), .1 * s,
                                                                                   1.05 * s), bevel=.03)
    pivot = Vector((0, .1 * s, 1.35 * s))
    d = Vector((0, -math.cos(el), math.sin(el)))
    centre = pivot + d * (length * s * .1)
    rot = (R90 + el, 0, 0)
    box = a.part('Launcher_box' + n, 'Team', m)
    k.extrude(box, [(-W, -H), (W, -H), (W, H), (-W, H)], length * s, loc=tuple(centre), rot=rot, axis='Z',
              chamfer=.05 * s)
    mouth = centre + d * (length * s / 2 + .01)
    up = Vector((0, math.sin(el), math.cos(el)))
    fr = a.part('Launcher_doors' + n, 'Undercarriage' if style == 'ram' else 'Medical', m)
    cells = []
    for c in range(cols):
        for r in range(rows):
            cx = (c - (cols - 1) / 2) * .42 * s
            cz = (r - (rows - 1) / 2) * .42 * s
            p = mouth + Vector((cx, 0, 0)) + up * cz
            if style == 'ram':
                fr.cyl(.16 * s, .03, loc=tuple(p), rot=rot, seg=8, bevel=0)
            else:
                fr.box((.36 * s, .03, .36 * s), loc=tuple(p), rot=(el, 0, 0), bevel=0)
            cells.append(p)
    mz = a.pivot(f'Muzzle_{slot}{t}', tuple(mouth), m)
    near = sorted(cells, key=lambda p: (p - mouth).length)[:4]
    for j, p in enumerate(near):
        a.pivot(f'Muzzle_b{j + 1}_{slot}{t}', tuple(p - mouth), mz)


def quad_canisters(a, i, at, slot='missile', s=1.0, el=.3, length=4.2, n=4, across=True):
    """A quad anti-ship canister rack (Harpoon / Uran read), fixed: the deck frame, the four tubes angled forward
    over the beam with their end caps and the umbilical boxes; the pivot carries the four tube mouths."""
    x, y, z = at
    t = tag(i)
    fr = a.part('Canister_frames', 'Steel')
    can = a.part('Canisters', 'Team')
    caps = a.part('Canister_caps', 'Undercarriage')
    d = Vector((0, -math.cos(el), math.sin(el)))
    mouths = []
    for j in range(n):
        row, col = j // 2, j % 2
        cx = x + (col - .5) * .62 * s
        base = Vector((cx, y + length * s * .45, z + .5 * s + row * .62 * s))
        c = base + d * (length * s / 2)
        k.extrude(can, [(-.27 * s, -.27 * s), (.27 * s, -.27 * s), (.27 * s, .27 * s), (-.27 * s, .27 * s)],
                  length * s, loc=tuple(c), rot=(R90 + el, 0, 0), axis='Z', chamfer=.03 * s)
        for e in (0, 1):
            p = base + d * (length * s * e + (.01 if e else -.01))
            caps.box((.5 * s, .02, .5 * s), loc=tuple(p), rot=(el, 0, 0), bevel=0)
        mouths.append(base + d * (length * s))
    for dy in (-length * .3, length * .35):
        fr.box((1.5 * s, .12 * s, 1.6 * s), loc=(x, y + dy * s, z + .7 * s), bevel=0)
    mid = sum(mouths, Vector()) / len(mouths)
    m = a.pivot(f'Mount_{slot}{t}', tuple(mid))
    mz = a.pivot(f'Muzzle_{slot}{t}', (0, 0, 0), m)
    for j, p in enumerate(mouths):
        a.pivot(f'Muzzle_b{j + 1}_{slot}{t}', tuple(p - mid), mz)


# ============================================================================= finishing
PROTECT = ('Hull', 'Hull_low', 'Boot_top', 'Deck', 'Deck_edge', 'Superstructure', 'Mast', 'Funnel', 'Team_band',
           'Railings', 'Boats', 'Barbettes')


def _move(a, src_key, dst_key):
    src = a.shapes[src_key]
    dst = a.shapes.get(dst_key) or a.part(*dst_key)
    sl = list(src.bm.verts.layers.float)
    layers = [(l, dst.bm.verts.layers.float.get(l.name) or dst.bm.verts.layers.float.new(l.name)) for l in sl]
    vmap = {}
    for v in src.bm.verts:
        nv = dst.bm.verts.new(v.co)
        for ls, ld in layers:
            nv[ld] = v[ls]
        vmap[v] = nv
    for f in src.bm.faces:
        try:
            dst.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            pass
    src.bm.free()
    del a.shapes[src_key]
    a.order.remove(src_key)


def kick_part(name):
    import re
    return bool(re.match(r'^[a-z]+_(barrels|muzzles)(_\d+)?$', name, re.I))


def fold(a, target=68):
    """Fold static (and same-pivot) parts of one material into fewer meshes until the model has `target` renderers
    (glb_check's enforced renderer cap is 76): the smallest unprotected member of the biggest (material, pivot) group
    joins that group's biggest member. Barrels that kick (IsMountBarrel) stay their own meshes."""
    def size(key):
        return len(a.shapes[key].bm.faces)
    for key in list(a.order):
        if not a.shapes[key].bm.faces:
            a.shapes[key].bm.free()
            del a.shapes[key]
            a.order.remove(key)
    while len(a.order) > target:
        groups = {}
        for key in a.order:
            groups.setdefault((key[1], key[2]), []).append(key)
        best = None
        for g, keys in groups.items():
            movable = [kk for kk in keys if kk[0] not in PROTECT and not kick_part(kk[0])]
            if len(keys) < 2 or not movable:
                continue
            if best is None or len(keys) > len(best[1]):
                best = (g, keys, movable)
        if best is None:
            break
        _, keys, movable = best
        src = min(movable, key=size)
        others = [kk for kk in keys if kk != src and not kick_part(kk[0])]
        if not others:
            break
        dst = max(others, key=lambda kk: (kk[0] in PROTECT, size(kk)))
        _move(a, src, dst)
