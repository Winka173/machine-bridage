"""Naval models lane A (06/10, DECISIONS "Naval models (lane A)"): ship parts for the nine light and medium hulls of
the naval expansion (Docs/naval/MODEL_CONTRACT.md), built by mb_naval_a_ships.py.

Each ship is still its own builder with its own layout and numbers; this module only holds the parametric pieces
they share: the displacement / planing hull (open strips per material: painted topsides, boot-top, antifouling,
the deck, so nothing overlaps), the deckhouse tiers with their window bands, masts and radars, and the weapon mounts
with their runtime nodes (`Mount_<slot>[_NN]` > `Muzzle_<slot>[_NN]`, stable names, no Blender suffix): the OTO
76/62, the AK-100, the AK-630, the M2 tub, the Stinger / Mistral pedestal, the Sea Sparrow-type box, the RAM-type
box, the twin-arm area SAM, fixed canister banks (an invisible yaw pivot at the bank's mouth, so nothing visible
turns), the GMLRS-type pod battery, decoy launchers (`Aps_cluster`, the runtime's APS effect points) and
`Mount_APS`.

Conventions are frontier_kit's: metres, +Z up, -Y the bow, +X the ship's left; the waterline is z = 0.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= surfaces
def grid(shape, rings, hint, closed=False):
    """Skin point rings (same count) into an open quad surface with shared vertices (smooth shading); every face is
    turned to face along hint(centre) (a function) or the fixed vector `hint`."""
    bm = shape.bm
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(vr[0])
    for a, b in zip(vr, vr[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            quad = []
            for v in (a[i], a[j], b[j], b[i]):
                if all((v.co - u.co).length > 1e-5 for u in quad):
                    quad.append(v)
            if len(quad) < 3:
                continue
            f = bm.faces.new(quad)
            f.normal_update()
            c = f.calc_center_median()
            want = Vector(hint(c) if callable(hint) else hint)
            if f.normal.dot(want) < 0:
                f.normal_flip()
    return vr


def poly(shape, pts, hint):
    """One flat polygon, turned to face `hint`."""
    bm = shape.bm
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    f.normal_update()
    if f.normal.dot(Vector(hint)) < 0:
        f.normal_flip()


# ============================================================================= hull
class Hull:
    """A hull of length L and beam (bow at -L/2): the half beam narrowing to the stem over `entry` of the length, a
    transom aft, sheer from `deck_aft` to `deck_bow`, flare forward, a raked stem and a cut-away forefoot. planing=True
    gives a hard-chined deep-vee bottom (fast attack craft)."""

    def __init__(self, a, L, beam, deck_aft, deck_bow, keel=-1.1, entry=.42, transom=.9, flare=.2, rake=1.4,
                 sheer_from=.42, planing=False, bulwark=(.2, .6)):
        self.a, self.L, self.B = a, L, beam / 2
        self.bow, self.stern = -L / 2, L / 2
        self.deck_aft, self.deck_bow, self.keel = deck_aft, deck_bow, keel
        self.entry, self.transom, self.flare, self.rake = entry, transom, flare, rake
        self.sheer_from, self.planing, self.bulwark = sheer_from, planing, bulwark

    def f(self, y):
        return min(1.0, max(0.0, (y - self.bow) / self.L))

    def hb(self, y):
        """Half beam at the deck edge."""
        f = self.f(y)
        if f < self.entry:
            return max(.04, self.B * math.sin(min(1.0, f / self.entry) * R90) ** .72)
        return self.B * (1 - (1 - self.transom) * ((f - self.entry) / (1 - self.entry)) ** 1.6)

    def dz(self, y):
        """Deck height (the sheer rising to the bow)."""
        g = max(0.0, (self.sheer_from - self.f(y)) / self.sheer_from)
        return self.deck_aft + (self.deck_bow - self.deck_aft) * g * g

    def edge(self, y, s, inset=0.0, up=0.0):
        return (s * (self.hb(y) - inset), y, self.dz(y) + up)

    def _ring(self, y, s):
        """One side's section points, deck edge to keel: upper (3), boot-top (2, shared), bottom."""
        f = self.f(y)
        h, z = self.hb(y), self.dz(y)
        fw = max(0.0, 1 - f / self.entry)
        wl = h * (1 - self.flare * fw) * (1 - .1 * max(0.0, (f - .85) / .15))
        kz = self.keel * (1 - .72 * (max(0.0, .16 - f) / .16) ** 1.2) * (1 - .45 * max(0.0, (f - .8) / .2))
        kd = min(.55, (z - .4) * .28)
        pts = [(h, z), (h * .985, z - kd), (wl, .35), (wl * .985, 0.0)]
        if self.planing:
            pts += [(wl * .93, -.07), (wl * .5, kz * .55), (0.0, kz)]
        else:
            pts += [(wl * (.84 - .25 * fw), kz * .55), (wl * (.4 - .15 * fw), kz * .93), (0.0, kz)]
        out = []
        for x, zz in pts:
            yy = y
            if f < .14:                        # the raked stem: the lower points move aft towards the bow
                yy = y + self.rake * ((z - zz) / (z - self.keel)) * (1 - f / .14) ** 1.3
            out.append((s * x, yy, zz))
        return out

    def build(self, stations=None, team_band=None, portholes=()):
        a = self
        st = stations or (0, .012, .03, .055, .09, .14, .2, .28, .37, .47, .58, .7, .81, .91, .97, 1.0)
        ys = [self.bow + f * self.L for f in st]
        hull = self.a.part('Hull', 'Armor')
        boot = self.a.part('Boot_top', 'BootTop')
        low = self.a.part('Hull_low', 'HullRed')
        rings = {s: [self._ring(y, s) for y in ys] for s in (-1, 1)}
        for s in (-1, 1):
            grid(hull, [r[:3] for r in rings[s]], (s, 0, 0))
            grid(boot, [r[2:4] for r in rings[s]], (s, 0, 0))
        grid(low, [rings[-1][i][3:] + list(reversed(rings[1][i][3:-1])) for i in range(len(ys))],
             lambda c: (c.x, 0, -.45))
        # The stem (the two sides meet) and the transom.
        bowl, bowr = rings[-1][0], rings[1][0]
        grid(hull, [bowl[:4], bowr[:4]], (0, -1, 0))
        grid(low, [bowl[3:], bowr[3:]], (0, -1, 0))
        sl, sr = rings[-1][-1], rings[1][-1]
        poly(hull, sl[:4] + list(reversed(sr[:4])), (0, 1, 0))
        poly(low, sl[3:] + list(reversed(sr[3:-1])), (0, 1, 0))
        # The deck (one surface between the deck edges).
        grid(self.a.part('Deck', 'NavyDeck'), [[r[0] for r in (rings[-1][i], rings[1][i])] for i in range(len(ys))],
             (0, 0, 1))
        # The forecastle bulwark: an outer and an inner face and its capping.
        fb, bh = self.bulwark
        if fb > 0:
            bys = [y for y in ys if self.f(y) <= fb] + [self.bow + fb * self.L]
            for s in (-1, 1):
                outer = [[self.edge(y, s), self.edge(y, s, up=bh)] for y in bys]
                inner = [[self.edge(y, s, inset=.05, up=.0), self.edge(y, s, inset=.05, up=bh)] for y in bys]
                grid(hull, outer, (s, 0, 0))
                grid(hull, inner, (-s, 0, 0))
                grid(hull, [[o[1], i[1]] for o, i in zip(outer, inner)], (0, 0, 1))
                end = bys[-1]
                poly(hull, [self.edge(end, s), self.edge(end, s, up=bh), self.edge(end, s, inset=.05, up=bh),
                            self.edge(end, s, inset=.05)], (0, 1, 0))
        # Plating seams on the topsides, the faction band, portholes, hawse pipes.
        seams = self.a.part('Hull_seams', 'Undercarriage')
        for s in (-1, 1):
            for y in [self.bow + f * self.L for f in (.12, .22, .32, .42, .52, .62, .72, .82, .92)]:
                h, z = self.hb(y), self.dz(y)
                seams.box((.015, .03, max(.4, z - .5)), loc=(s * (h * .99 + .012), y, (z + .4) / 2 - .05), bevel=0)
            if team_band:
                y0, y1, zt, hgt = team_band
                yb = [y0 + (y1 - y0) * i / 8 for i in range(9)]
                grid(self.a.part('Team_band', 'Team'),
                     [[(s * (self.hb(y) * .99 + .018), y, self.dz(y) - zt - hgt), (s * (self.hb(y) + .018), y,
                                                                               self.dz(y) - zt)] for y in yb], (s, 0, 0))
            if portholes:
                K.portholes(self.a, [(s * (self.hb(y) * .995 + .012), y, self.dz(y) - .55) for y in portholes],
                            (s, 0, 0), r=.12)
            yh = self.bow + .05 * self.L
            self.a.part('Hull_seams', 'Undercarriage').cyl(.17, .1, loc=(s * (self.hb(yh) * .97 + .03), yh,
                                                                         self.dz(yh) - .55), rot=(0, R90, 0), seg=8,
                                                                    bevel=0)
        return self


# ============================================================================= deckhouses
def _plan(z, hw, ya, yb, c, ca):
    return [(-hw + c, ya, z), (hw - c, ya, z), (hw, ya + c, z), (hw, yb - ca, z), (hw - ca, yb, z), (-hw + ca, yb, z),
            (-hw, yb - ca, z), (-hw, ya + c, z)]


def tier(part, y0, y1, z0, z1, hw0, hw1, rake=.3, cut=.4, aft=0.0, cut_aft=.15, chamfer=.04, x=0.0):
    """A deckhouse tier from y0 (front) to y1 (aft), z0..z1, the walls leaning in from hw0 to hw1, the front raked
    back by `rake` (and the aft wall by `aft`), the front corners cut by `cut`."""
    r0 = [(p[0] + x, p[1], p[2]) for p in _plan(z0, hw0, y0, y1, cut, cut_aft)]
    r1 = [(p[0] + x, p[1], p[2]) for p in _plan(z1, hw1, y0 + rake, y1 - aft, cut * hw1 / hw0, cut_aft)]
    k.sharp_loft(part, [r0, r1], chamfer=chamfer)
    return part


def window_band(part, y0, z0, z1, rake, hw, n, frac=(.45, .85), gap=.08, x=0.0):
    """n windows across the raked front face of a tier (front at y0, z0..z1, raked back by `rake`), just proud of it."""
    ang = math.atan2(rake, z1 - z0)
    za, zb = z0 + (z1 - z0) * frac[0], z0 + (z1 - z0) * frac[1]
    zc = (za + zb) / 2
    yc = y0 + rake * (zc - z0) / (z1 - z0) - .025
    w = (2 * hw - gap * (n + 1)) / n
    hgt = (zb - za) / math.cos(ang)
    for i in range(n):
        xc = x - hw + gap + w / 2 + i * (w + gap)
        part.box((w, .02, hgt), loc=(xc, yc, zc), rot=(-ang, 0, 0), bevel=0)


def side_windows(part, s, ys, z, hw, lean=0.0, size=(.6, .35)):
    """Square windows on a tier's side wall at x = s * hw (leaning in by `lean` radians)."""
    for y in ys:
        part.box((.02, size[0], size[1]), loc=(s * (hw + .015), y, z), rot=(0, s * lean, 0), bevel=0)


def doors(part, s, ys, z0, hw, h=1.7, lean=0.0):
    for y in ys:
        part.box((.03, .75, h), loc=(s * (hw + .02), y, z0 + h / 2 + .05), rot=(0, s * lean, 0), bevel=0)


# ============================================================================= masts, radars, funnels
def mast(a, loc, h, w0, w1, top=None, lattice=0.0, yard=2.6, name='Mast'):
    """An enclosed tapered mast (h tall, w0 -> w1 wide) from loc, a top platform, a yard, and an optional lattice
    pole of `lattice` metres on it; returns the top point."""
    x, y, z = loc
    k.extrude(a.part(name, 'Team'), [(-w0 / 2, -w0 / 2), (w0 / 2, -w0 / 2), (w0 / 2, w0 / 2), (-w0 / 2, w0 / 2)], h,
              loc=(x, y, z + h / 2), axis='Z', chamfer=.04, corner=.06, taper=(w1 / w0, w1 / w0))
    st = a.part('Mast_steel', 'Steel')
    zt = z + h
    k.block(st, (w1 + .4, w1 + .4, .08), loc=(x, y, zt + .04), chamfer=.02)
    K.railing(st, [(x - w1 / 2 - .18, y - w1 / 2 - .18, zt + .08), (x + w1 / 2 + .18, y - w1 / 2 - .18, zt + .08),
                   (x + w1 / 2 + .18, y + w1 / 2 + .18, zt + .08), (x - w1 / 2 - .18, y + w1 / 2 + .18, zt + .08),
                   (x - w1 / 2 - .18, y - w1 / 2 - .18, zt + .08)], h=.45, post=.6, r=.015)
    st.box((yard, .07, .07), loc=(x, y, z + h * .82), bevel=0)
    st.box((yard * .6, .06, .06), loc=(x, y + .05, z + h * .45), bevel=0)
    domes = a.part('Mast_domes', 'Medical')
    for xx in (-yard / 2 + .1, yard / 2 - .1):
        st.box((.04, .04, .4), loc=(x + xx, y, z + h * .82 - .2), bevel=0)
        domes.sphere(.13, loc=(x + xx * .7, y, z + h * .82 + .14), seg=10, rings=6)
    for sx in (-1, 1):
        k.block(a.part('Mast_boxes', 'Armor'), (.3, .35, .45), loc=(x + sx * (w0 + w1) / 4 * 1.05, y - .1, z + h * .55),
                chamfer=.03)
    if lattice > 0:
        b = w1 * .3
        for sx in (-1, 1):
            for sy in (-1, 1):
                st.tube([(x + sx * b, y + sy * b, zt), (x + sx * .06, y + sy * .06, zt + lattice)], .03, seg=4)
        for i in range(3):
            zz = zt + lattice * (i + .5) / 3
            ww = b - (b - .06) * (i + .5) / 3
            st.tube([(x - ww, y - ww, zz), (x + ww, y - ww, zz), (x + ww, y + ww, zz), (x - ww, y + ww, zz),
                     (x - ww, y - ww, zz)], .015, seg=3)
        zt += lattice
        st.tube([(x, y, zt), (x, y, zt + .9)], .03, seg=5)
        st.box((1.1, .05, .05), loc=(x, y, zt + .55), bevel=0)
        for xx in (-.5, .5):
            st.tube([(x + xx, y, zt + .55), (x + xx * 1.05, y, zt + 1.15)], .012, seg=3)
    return (x, y, zt)


def radar(a, loc, kind='bar', w=2.4, parent=None):
    """The spinning `Radar` pivot on loc: 'bar' (slotted search array), 'twin' (back-to-back faces, a 3D radar),
    'big' (a curved air-search reflector), 'nav' (a small navigation scanner)."""
    r = a.pivot('Radar', loc, parent)
    a.part('Radar_pedestal', 'Steel', r).cyl(.14, .35, loc=(0, 0, .17), seg=10, bevel=0)
    if kind == 'nav':
        k.block(a.part('Radar_array', 'Armor', r), (w, .16, .18), loc=(0, 0, .42), chamfer=.03)
        return r
    if kind == 'big':
        arr = a.part('Radar_array', 'Armor', r)
        segs = 8
        for i in range(segs):
            u0, u1 = (i / segs - .5) * 1.1, ((i + 1) / segs - .5) * 1.1
            pts = []
            for u in (u0, u1):
                pts.append((math.sin(u) * w / 2 / .53, -math.cos(u) * .55 + .55, .35))
            xa, ya, _ = pts[0]
            xb, yb, _ = pts[1]
            q = [(xa, ya, .3), (xb, yb, .3), (xb, yb, 1.4), (xa, ya, 1.4)]
            arr.mesh(q, [(0, 1, 2, 3)])
            arr.mesh([(p[0], p[1] + .03, p[2]) for p in q], [(3, 2, 1, 0)])
        arr.box((.12, .9, .12), loc=(0, .45, .36), bevel=0)
        a.part('Radar_face', 'Steel', r).box((w * .9, .05, .07), loc=(0, .55, .85), bevel=0)
        return r
    arr = a.part('Radar_array', 'Armor', r)
    if kind == 'twin':
        for s in (-1, 1):
            k.block(arr, (w, .22, .9), loc=(0, s * .2, .85), chamfer=.04)
            a.part('Radar_face', 'Undercarriage', r).box((w * .9, .02, .78), loc=(0, s * .32, .85), bevel=0)
        arr.box((.3, .6, .3), loc=(0, 0, .4), bevel=0)
        return r
    k.block(arr, (w, .3, .5), loc=(0, 0, .55), chamfer=.04)
    a.part('Radar_face', 'Undercarriage', r).box((w * .92, .02, .38), loc=(0, -.16, .58), bevel=0)
    return r


def director(a, loc, r=.45, facing=(0, -1, 0), part='Directors'):
    """A fire-control director: a pedestal, a drum and its dish."""
    x, y, z = loc
    d = a.part(part, 'Medical')
    d.cyl(.18, .4, loc=(x, y, z + .2), seg=10, bevel=0)
    k.block(d, (r * 1.6, r * 1.3, r * 1.1), loc=(x, y, z + .4 + r * .55), chamfer=.05)
    K.dish(d, a.part('Director_feeds', 'Steel'), (x + facing[0] * r * .7, y + facing[1] * r * .7, z + .4 + r * .6),
           r=r, normal=facing, seg=12)


def funnel(a, loc, w, d, h, rake=.25, caps=2):
    x, y, z = loc
    k.extrude(a.part('Funnel', 'Team'), [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2 * .9, d / 2), (-w / 2 * .9, d / 2)], h,
              loc=(x, y + rake / 2, z + h / 2), axis='Z', chamfer=.05, corner=.12, taper=(.9, .92))
    cap = a.part('Funnel_cap', 'Undercarriage')
    cap.box((w * .85, d * .85, .08), loc=(x, y + rake, z + h + .02), bevel=0)
    for i in range(caps):
        xx = (i - (caps - 1) / 2) * w * .35
        a.part('Exhausts', 'Steel').cyl(.14, .5, loc=(x + xx, y + rake, z + h + .25), seg=8, bevel=0)
    K.soot(a, (x, y + rake, z + h + .3), radius=max(w, d) * .9, k=.5)


def nav_lights(a, s, loc):
    a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.14, .14, .14), loc=loc, bevel=0)


# ============================================================================= weapons
def _tag(tag):
    return f'_{tag}' if tag else ''


def _scale(a, m, sc):
    """Scale a mount's own pieces and child pivots (all in its local frame) by sc about the pivot (readability)."""
    if abs(sc - 1.0) < 1e-6:
        return m
    root = a.pivots[m]

    def under(name):
        o = a.pivots.get(name) if name else None
        while o is not None:
            if o is root:
                return True
            o = o.parent
        return False
    for (name, mat, parent), sh in a.shapes.items():
        if parent and under(parent):
            for v in sh.bm.verts:
                v.co *= sc
    for name, o in a.pivots.items():
        if o is not root and under(name):
            o.location = o.location * sc
    return m


def gun_76(a, loc, tag='', slot='gun', sc=1.0):
    """OTO Melara 76/62 Super Rapid: the faceted cupola on its ring, the barrel with fume extractor and muzzle brake.
    `Mount_<slot>[_tag]` > `Muzzle_<slot>[_tag]`."""
    t = _tag(tag)
    m = a.pivot(f'Mount_{slot}{t}', loc)
    k.lathe(a.part(f'Gun_ring{t}', 'Steel', m), [(1.25, 0), (1.25, .12), (1.15, .18), (0, .18)], seg=18)
    rings = []
    for z, f, w, rr in ((.15, -1.15, 1.15, 1.45), (.95, -.95, 1.05, 1.4), (1.38, -.45, .68, 1.1)):
        rings.append([(-w * .7, f, z), (w * .7, f, z), (w, f + .65, z), (w, rr, z), (-w, rr, z), (-w, f + .65, z)])
    k.sharp_loft(a.part(f'Gun_house{t}', 'Team', m), rings, chamfer=.06)
    k.block(a.part(f'Gun_mantlet{t}', 'Armor', m), (.55, .3, .5), loc=(0, -1.1, .8), chamfer=.04)
    k.lathe(a.part(f'Gun_barrel{t}', 'Steel', m), [(.16, 0), (.16, .2), (.095, .3), (.082, 1.5), (.115, 1.56),
                                                  (.115, 2.15), (.085, 2.22), (.074, 3.85), (0, 3.85)],
            loc=(0, -1.2, .8), rot=K.FORWARD, seg=12, worn=(1, 5))
    k.lathe(a.part(f'Gun_brake{t}', 'Undercarriage', m), [(.074, 0), (.112, .04), (.112, .34), (.08, .38), (0, .38)],
            loc=(0, -5.03, .8), rot=K.FORWARD, seg=12)
    a.part(f'Gun_vents{t}', 'Undercarriage', m).box((.7, .02, .22), loc=(0, 1.42, .75), bevel=0)
    a.pivot(f'Muzzle_{slot}{t}', (0, -5.45, .8), m)
    return _scale(a, m, sc)


def gun_100(a, loc, tag='', slot='gun', sc=1.0):
    """AK-100 100 mm: the angular, flat-roofed turret with sloped cheeks, the long barrel and its sleeve."""
    t = _tag(tag)
    m = a.pivot(f'Mount_{slot}{t}', loc)
    k.lathe(a.part(f'Gun_ring{t}', 'Steel', m), [(1.5, 0), (1.5, .14), (1.4, .2), (0, .2)], seg=20)
    rings = []
    for z, f, w, rr in ((.18, -1.6, 1.45, 2.0), (1.15, -1.4, 1.4, 1.95), (1.75, -.7, 1.05, 1.75)):
        rings.append([(-w * .55, f, z), (w * .55, f, z), (w, f + .8, z), (w, rr, z), (-w, rr, z), (-w, f + .8, z)])
    k.sharp_loft(a.part(f'Gun_house{t}', 'Team', m), rings, chamfer=.07)
    hs = a.part(f'Gun_hatches{t}', 'Armor', m)
    k.block(hs, (.7, .6, .1), loc=(.5, .7, 1.8), chamfer=.03)
    k.block(hs, (.5, .5, .25), loc=(-.55, .3, 1.85), chamfer=.03)
    k.block(a.part(f'Gun_mantlet{t}', 'Armor', m), (.7, .35, .7), loc=(0, -1.5, .95), chamfer=.05)
    k.lathe(a.part(f'Gun_barrel{t}', 'Steel', m), [(.2, 0), (.2, .25), (.12, .35), (.105, 1.9), (.13, 1.95),
                                                  (.13, 3.1), (.1, 3.16), (.09, 4.7), (.11, 4.75), (.11, 4.95),
                                                  (0, 4.95)],
            loc=(0, -1.65, .95), rot=K.FORWARD, seg=12, worn=(1, 6))
    a.pivot(f'Muzzle_{slot}{t}', (0, -6.65, .95), m)
    return _scale(a, m, sc)


def ak630(a, loc, tag='', slot='mg', base=.6, sc=1.0):
    """AK-630M: the pedestal (static, `base` tall), the low rounded turret on its ring, the six-barrel cluster in its
    jacket. `Mount_<slot>[_tag]` > `Muzzle_<slot>[_tag]`. Names carry the tag (one mesh per mount)."""
    t = _tag(tag)
    x, y, z = loc
    k.lathe(a.part('Ciws_base', 'Armor'), [(.75, 0), (.72, base * .8), (.62, base), (0, base)], loc=(x, y, z), seg=14)
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + base))
    k.lathe(a.part(f'CIWS_ring{t}', 'Steel', m), [(.7, 0), (.7, .1), (.6, .16), (0, .16)], seg=14)
    k.extrude(a.part(f'CIWS_body{t}', 'Team', m), [(-.62, 0), (.62, 0), (.58, .55), (.32, .82), (-.32, .82),
                                                  (-.58, .55)], 1.7, loc=(0, .2, .12), axis='Y', chamfer=.05,
              corner=.04, taper=(1, 1))
    g = a.part(f'Barrels_ciws{t}', 'Steel', m)
    g.cyl(.13, .9, loc=(0, -.95, .5), rot=K.FORWARD, seg=10, bevel=0)
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.024, 1.15, loc=(math.cos(u) * .075, -1.85, .5 + math.sin(u) * .075), rot=K.FORWARD, seg=5, bevel=0)
    g.cyl(.12, .07, loc=(0, -2.3, .5), rot=K.FORWARD, seg=10, bevel=0)
    g.cyl(.12, .07, loc=(0, -1.75, .5), rot=K.FORWARD, seg=10, bevel=0)
    a.part(f'CIWS_hatch{t}', 'Armor', m).box((.5, .5, .04), loc=(0, .5, .95), bevel=0)
    a.pivot(f'Muzzle_{slot}{t}', (0, -2.4, .5), m)
    return _scale(a, m, sc)


def hmg_tub(a, loc, tag='', slot='mg', r=.65, sc=1.0):
    """An M2 Browning in its splinter tub: the tub (static), the pintle, receiver, barrel, shield and ammo can on
    `Mount_<slot>[_tag]` > `Muzzle_<slot>[_tag]`."""
    t = _tag(tag)
    x, y, z = loc
    k.lathe(a.part('Mg_tub', 'Armor'), [(0, 0), (r, 0), (r, .95), (r - .05, .95), (r - .05, .06), (0, .06)],
            loc=(x, y, z), seg=14)
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + .7))
    a.part(f'Mg_post{t}', 'Steel', m).cyl(.05, .5, loc=(0, 0, .1), seg=8, bevel=0)
    body = a.part(f'Mg_body{t}', 'Armor', m)
    body.box((.16, .75, .18), loc=(0, -.1, .45), bevel=.01)
    body.box((.6, .03, .45), loc=(0, -.42, .48), bevel=0)
    body.box((.18, .25, .2), loc=(.17, .05, .38), bevel=0)
    a.part(f'Barrel_mg{t}', 'Steel', m).cyl(.03, 1.05, loc=(0, -.95, .47), rot=K.FORWARD, seg=6, bevel=0)
    a.part(f'Barrel_mg{t}', 'Steel', m).cyl(.05, .3, loc=(0, -.55, .47), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot(f'Muzzle_{slot}{t}', (0, -1.5, .47), m)
    return _scale(a, m, sc)


def _tilt(y, z, e):
    """(y, z) of a point turned nose-up by e about the X axis (rot=(-e, 0, 0)): -Y (the front) rises."""
    return y * math.cos(e) + z * math.sin(e), -y * math.sin(e) + z * math.cos(e)


def sam_pedestal(a, loc, tag='', slot='missile', tubes=4, body='Sam_tubes', elev=.12, sc=1.0):
    """A Stinger / Mistral pedestal (SIMBAD / Sadral class): the post (static), the yawing head with its sight and
    two pods of tubes either side."""
    t = _tag(tag)
    x, y, z = loc
    k.lathe(a.part('Sam_post', 'Armor'), [(.5, 0), (.45, .15), (.25, .25), (.25, .9), (0, .9)], loc=(x, y, z), seg=12)
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + .9))
    head = a.part(f'Sam_head{t}', 'Team', m)
    k.block(head, (.6, .7, .7), loc=(0, .05, .35), chamfer=.05)
    a.part(f'Sam_sight{t}', 'Glass', m).box((.3, .02, .2), loc=(0, -.31, .5), bevel=0)
    tb = a.part(f'{body}{t}', 'Fuel', m)
    caps = a.part(f'Sam_caps{t}', 'Undercarriage', m)
    per = max(1, tubes // 2)
    zc = .45
    for s in (-1, 1):
        a.part(f'Sam_arms{t}', 'Steel', m).box((.32, .2, .12), loc=(s * .44, 0, zc), bevel=0)
        for j in range(per):
            col, row = divmod(j, 2)
            xx = s * (.68 + col * .19)
            zz = (row - .5) * .19 if per > 1 else 0.0
            ty, tz = _tilt(-.1, zz, elev)
            tb.cyl(.085, 1.7, loc=(xx, ty, zc + tz), rot=(R90 - elev, 0, 0), seg=10, bevel=0)
            fy, fz = _tilt(-.97, zz, elev)
            caps.cyl(.088, .04, loc=(xx, fy, zc + fz), rot=(R90 - elev, 0, 0), seg=10, bevel=0)
    my, mz = _tilt(-1.05, 0, elev)
    a.pivot(f'Muzzle_{slot}{t}', (0, my, zc + mz), m)
    return _scale(a, m, sc)


def sam_box(a, loc, tag='', slot='missile', cols=4, rows=2, cell=.44, length=3.3, elev=.2, covers='Launcher_covers', sc=1.0):
    """A Sea Sparrow (Mk 29) type trainable box launcher: the turntable, the yoke, the cell box and its frangible
    front covers (`covers`: 'Launcher_covers' gives the runtime a face of cells to launch from)."""
    t = _tag(tag)
    m = a.pivot(f'Mount_{slot}{t}', loc)
    k.lathe(a.part(f'Sam_base{t}', 'Steel', m), [(1.0, 0), (1.0, .2), (.85, .35), (0, .35)], seg=16)
    k.block(a.part(f'Sam_stand{t}', 'Team', m), (1.1, 1.2, .6), loc=(0, .3, .65), chamfer=.06)
    w, h = cols * cell + .16, rows * cell + .16
    zc = 1.45
    for s in (-1, 1):
        k.block(a.part(f'Sam_yoke{t}', 'Team', m), (.18, .9, 1.25), loc=(s * (w / 2 + .14), .2, .9), chamfer=.04)
    rot = (-elev, 0, 0)
    k.block(a.part(f'Sam_box{t}', 'Medical', m), (w, length, h), loc=(0, 0, zc), rot=rot, chamfer=.04,
            ends=(True, True))
    cv = a.part(f'{covers}{t}', 'Undercarriage', m)
    for i in range(cols):
        for j in range(rows):
            xx = (i - (cols - 1) / 2) * cell
            fy, fz = _tilt(-length / 2 - .015, (j - (rows - 1) / 2) * cell, elev)
            cv.box((cell * .84, .02, cell * .84), loc=(xx, fy, zc + fz), rot=rot, bevel=0)
    by, bz = _tilt(length / 2 - .3, 0, elev)
    a.part(f'Sam_bands{t}', 'Hazard', m).box((w + .02, .12, h + .02), loc=(0, by, zc + bz), rot=rot, bevel=0)
    my, mz = _tilt(-length / 2 - .1, 0, elev)
    a.pivot(f'Muzzle_{slot}{t}', (0, my, zc + mz), m)
    return _scale(a, m, sc)


def ram_box(a, loc, tag='', slot='missile', elev=.15, sc=1.0):
    """A RAM-type (Mk 49) launcher: the pedestal, the trunnion arms and the 21-cell box with its round cell mouths."""
    t = _tag(tag)
    x, y, z = loc
    k.lathe(a.part('Sam_post', 'Armor'), [(.7, 0), (.6, .3), (.45, .5), (0, .5)], loc=(x, y, z), seg=14)
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + .5))
    k.lathe(a.part(f'Ram_base{t}', 'Steel', m), [(.55, 0), (.55, .25), (.4, .35), (0, .35)], seg=14)
    for s in (-1, 1):
        k.block(a.part(f'Ram_arms{t}', 'Team', m), (.14, .6, .95), loc=(s * .66, .1, .7), chamfer=.03)
    zc = 1.05
    rot = (-elev, 0, 0)
    k.block(a.part(f'Ram_box{t}', 'Medical', m), (1.1, 2.2, .95), loc=(0, 0, zc), rot=rot, chamfer=.05,
            ends=(True, True))
    cells = a.part(f'Ram_cells{t}', 'Undercarriage', m)
    for j in range(3):
        for i in range(7):
            fy, fz = _tilt(-1.11, (j - 1) * .26, elev)
            cells.cyl(.055, .03, loc=((i - 3) * .14, fy, zc + fz), rot=(R90 - elev, 0, 0), seg=6, bevel=0)
    my, mz = _tilt(-1.2, 0, elev)
    a.pivot(f'Muzzle_{slot}{t}', (0, my, zc + mz), m)
    return _scale(a, m, sc)


def twin_arm_sam(a, loc, tag='', slot='missile', body='Missiles', mag_r=2.0, length=4.4, sc=1.0):
    """A twin-arm area SAM launcher (Mk 26 / ZIF-type) on its magazine barbette: the rotating base, the pillar, two
    launch arms and the two big rounds hung under them."""
    t = _tag(tag)
    x, y, z = loc
    k.lathe(a.part('Sam_magazine', 'Armor'), [(mag_r, 0), (mag_r, .9), (mag_r - .15, 1.1), (0, 1.1)], loc=(x, y, z),
            seg=24, worn=(2,))
    hatch = a.part('Sam_hatches', 'Undercarriage')
    for s in (-1, 1):
        hatch.box((.9, .9, .03), loc=(x + s * .6, y - mag_r * .55, z + 1.1), bevel=0)
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + 1.1))
    k.lathe(a.part(f'Sam_base{t}', 'Team', m), [(1.5, 0), (1.5, .3), (1.25, .5), (0, .5)], seg=20, worn=(1,))
    k.block(a.part(f'Sam_pillar{t}', 'Team', m), (.9, 1.0, 1.2), loc=(0, .25, 1.0), chamfer=.06)
    e = .17
    d = Vector((0, -math.cos(e), math.sin(e)))
    arm = a.part(f'Sam_arms{t}', 'Steel', m)
    for s in (-1, 1):
        x0 = s * .8
        root = Vector((x0, .5, 1.45))
        k.block(arm, (.22, .9, .45), loc=(x0, .45, 1.35), chamfer=.04)
        tip = root + d * 2.4
        arm.tube([tuple(root), tuple(tip)], .1, seg=6)
        tail = root + d * -.4 + Vector((0, 0, -.33))
        K.missile(a, tuple(tail), .2, length, direction=tuple(d), parent=m, body=f'{body}{t}', seeker='Glass')
    a.pivot(f'Muzzle_{slot}{t}', tuple(Vector((0, .5, 1.12)) + d * (length - .2)), m)
    return _scale(a, m, sc)


def canister_bank(a, mouth, cols, rows, length, r, elev, tag='', slot='missile', gap=.08, caps='Launcher_covers',
                  yaw=0.0, frame_z=None, body='Canisters', pivot=True, mat='Fuel'):
    """A fixed bank of cols x rows round launch canisters with their mouths centred on `mouth`, pointing forward
    (turned `yaw` radians, up `elev`), on two cradle frames down to `frame_z` (the deck). The invisible yaw pivot
    `Mount_<slot>[_tag]` sits at the mouth with its muzzle (nothing visible turns)."""
    t = _tag(tag)
    mx, my, mz = mouth
    d = Vector((-math.sin(yaw) * math.cos(elev), -math.cos(yaw) * math.cos(elev), math.sin(elev)))
    side = Vector((math.cos(yaw), -math.sin(yaw), 0))
    up = side.cross(d).normalized()
    if up.z < 0:
        up = -up
    rot = K.rot_to(tuple(d))
    pitch = 2 * r + gap
    can = a.part(f'{body}{t}', mat)
    cap = a.part(f'{caps}{t}', 'Undercarriage')
    band = a.part('Canister_bands', 'Hazard')
    lows = []
    for i in range(cols):
        for j in range(rows):
            fc = Vector(mouth) + side * ((i - (cols - 1) / 2) * pitch) + up * ((j - (rows - 1) / 2) * pitch)
            c = fc - d * (length / 2)
            k.lathe(can, [(r * .96, -length / 2), (r, -length / 2 + .06), (r, length / 2 - .06), (r * .96, length / 2)],
                    loc=tuple(c), rot=rot, seg=14)
            for f in (.08, .92):
                k.lathe(can, [(r * 1.06, -.05), (r * 1.06, .05)], loc=tuple(c + d * (length * (f - .5))), rot=rot,
                        seg=14, caps=(False, False))
            band.cyl(r * 1.015, .1, loc=tuple(c + d * (-length * .3)), rot=rot, seg=14, bevel=0)
            k.lathe(cap, [(0, 0), (r * .97, 0), (r * .9, .06), (r * .4, .12), (0, .13)], loc=tuple(fc), rot=rot, seg=14)
            cap.cyl(r * .97, .05, loc=tuple(c - d * (length / 2 + .02)), rot=rot, seg=14, bevel=0)
            if j == 0:
                lows.append(c)
    if frame_z is not None:
        fr = a.part('Canister_frames', 'Steel')
        for f in (.2, .78):
            for i in range(cols):
                fc = Vector(mouth) + side * ((i - (cols - 1) / 2) * pitch) - up * ((rows - 1) / 2 * pitch)
                p = fc - d * (length * f) - up * r
                for s in (-1, 1):
                    q = p + side * (s * r * .7)
                    fr.tube([(q.x, q.y, frame_z), tuple(q)], .05, seg=5)
                fr.tube([tuple(p + side * (-r * .8)), tuple(p + side * (r * .8))], .05, seg=5)
    if not pivot:
        return None
    m = a.pivot(f'Mount_{slot}{t}', (mx, my, mz))
    a.pivot(f'Muzzle_{slot}{t}', (0, 0, 0), m)
    return m


def rocket_battery(a, loc, tag='', slot='rocket', elev=.38, pod=(1.0, 4.2, .78), sc=1.0):
    """A navalised GMLRS battery: the barbette (static), the training housing, the cradle and four six-cell pods in
    two columns (`Rocket_pods`: the runtime launches from the columns in turn) with their tube mouths."""
    t = _tag(tag)
    x, y, z = loc
    k.lathe(a.part('Launcher_base', 'Armor'), [(2.3, 0), (2.3, .55), (2.1, .7), (0, .7)], loc=(x, y, z), seg=24,
            worn=(2,))
    m = a.pivot(f'Mount_{slot}{t}', (x, y, z + .7))
    k.lathe(a.part(f'Launcher_ring{t}', 'Steel', m), [(1.9, 0), (1.9, .15), (1.75, .22), (0, .22)], seg=22)
    k.block(a.part(f'Launcher_housing{t}', 'Team', m), (3.0, 3.4, 1.1), loc=(0, .9, .75), chamfer=.1)
    pw, pl, ph = pod
    zc = 2.15
    rot = (-elev, 0, 0)
    for s in (-1, 1):
        cy, cz = _tilt(.3, -.6, elev)
        k.block(a.part(f'Launcher_cradle{t}', 'Armor', m), (.22, 3.2, 1.4), loc=(s * (pw + .42), cy, zc + cz),
                rot=rot, chamfer=.05)
    pods = a.part('Rocket_pods', 'Armor', m)
    bores = a.part(f'Pod_bores{t}', 'Undercarriage', m)
    bands = a.part(f'Pod_bands{t}', 'Hazard', m)
    for s in (-1, 1):
        xc = s * (pw / 2 + .25)
        for j in (-1, 1):
            zz = j * (ph / 2 + .02)
            cy, cz = _tilt(0, zz, elev)
            k.block(pods, (pw, pl, ph), loc=(xc, cy, zc + cz), rot=rot, chamfer=.04, ends=(True, True))
            for i in range(3):
                for kk in range(2):
                    fy, fz = _tilt(-pl / 2 - .012, zz + (kk - .5) * ph * .48, elev)
                    bores.cyl(.1, .03, loc=(xc + (i - 1) * pw * .3, fy, zc + fz), rot=(R90 - elev, 0, 0), seg=8,
                              bevel=0)
            by, bz = _tilt(pl / 2 - .4, zz, elev)
            bands.box((pw + .02, .1, ph + .02), loc=(xc, by, zc + bz), rot=rot, bevel=0)
    my, mz = _tilt(-pl / 2 - .1, 0, elev)
    a.pivot(f'Muzzle_{slot}{t}', (0, my, zc + mz), m)
    return _scale(a, m, sc)


def torpedo_tubes(a, mouth_y, z, xs, deck, length=5.6, r=.33, splay=.06, body='Launch_tubes'):
    """Fixed 533 mm deck tubes, one per x in xs, mouths at mouth_y, splayed out by `splay` radians, on saddles;
    `Mount_missile` (invisible yaw pivot) between the mouths with its muzzle."""
    tube = a.part(body, 'Armor')
    caps = a.part('Tube_caps', 'Steel')
    sad = a.part('Tube_saddles', 'Steel')
    for x in xs:
        s = 1 if x > 0 else -1
        yaw = s * splay
        d = Vector((math.sin(yaw), -math.cos(yaw), 0))
        rot = K.rot_to(tuple(d))
        mouth = Vector((x, mouth_y, z))
        c = mouth - d * (length / 2)
        k.lathe(tube, [(r, -length / 2), (r, length / 2 - .5), (r * 1.08, length / 2 - .45), (r * 1.08, length / 2)],
                loc=tuple(c), rot=rot, seg=16, worn=(2,))
        k.lathe(caps, [(0, 0), (r * 1.12, 0), (r * 1.12, .12), (0, .16)], loc=tuple(mouth), rot=rot, seg=16)
        k.lathe(caps, [(0, 0), (r * .9, 0), (r * .5, .25), (0, .3)], loc=tuple(c - d * (length / 2)),
                rot=K.rot_to(tuple(-d)), seg=12)
        for f in (.2, .75):
            p = mouth - d * (length * f)
            sad.box((r * 2.2, .22, z - r * .6 - deck + .03), loc=(p.x, p.y, deck + (z - r * .6 - deck) / 2), bevel=0)
        a.part('Tube_bands', 'Hazard').cyl(r * 1.02, .12, loc=tuple(mouth - d * .8), rot=rot, seg=16, bevel=0)
    m = a.pivot('Mount_missile', (0, mouth_y, z))
    a.pivot('Muzzle_missile', (0, 0, 0), m)
    return m


def decoys(a, pts, aps_at):
    """Decoy / chaff launchers (`Aps_cluster`: the runtime puts its APS effect points on them, one per side) and the
    `Mount_APS` point the quality gate asks of a def with `aps`."""
    part = a.part('Aps_cluster', 'Armor')
    for x, y, z in pts:
        s = 1 if x > 0 else -1
        k.block(part, (.5, .9, .25), loc=(x, y, z + .12), chamfer=.03)
        for i in range(3):
            for j in range(2):
                part.cyl(.07, .5, loc=(x + s * (.1 + j * .12), y - .3 + i * .3, z + .45 + j * .05),
                         rot=(0, s * .7, 0), seg=6, bevel=0)
    a.pivot('Mount_APS', aps_at)


# ============================================================================= deck gear
def rhib_davit(a, loc, s, length=4.0, beam=1.6, deck=0.0):
    """A RHIB in its davit on side s (cradle on the deck at z `deck`)."""
    x, y, z = loc
    K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (x, y, z), length=length, beam=beam)
    dav = a.part('Davits', 'Steel')
    for dy in (-length * .35, length * .35):
        dav.tube([(x - s * beam * .2, y + dy, deck), (x - s * beam * .2, y + dy, z + 1.5), (x, y + dy, z + 1.5)], .06,
                 seg=6)
        dav.tube([(x, y + dy, z + 1.5), (x, y + dy, z + .8)], .012, seg=3)


def life_rafts(a, pts, axis='Y'):
    rot = K.FORWARD if axis == 'Y' else (0, R90, 0)
    for p in pts:
        k.lathe(a.part('Life_rafts', 'Medical'), [(.24, -.42), (.27, -.36), (.27, .36), (.24, .42)], loc=p, rot=rot,
                seg=10)


def bollards(part, pts):
    for x, y, z in pts:
        for dy in (-.17, .17):
            part.cyl(.11, .32, loc=(x, y + dy, z + .16), seg=8, bevel=0)
            part.cyl(.15, .04, loc=(x, y + dy, z + .33), seg=8, bevel=0)


def anchor_gear(a, hull, y, spread=.75):
    """Windlasses, chain pipes and chains to the hawses on the foredeck at y."""
    z = hull.dz(y)
    for s in (-1, 1):
        k.lathe(a.part('Windlass', 'Steel'), [(.28, -.18), (.28, -.13), (.18, -.08), (.18, .08), (.28, .13),
                                              (.28, .18)], loc=(s * spread, y, z + .32), rot=(0, R90, 0), seg=10)
        a.part('Windlass', 'Steel').box((.5, .5, .2), loc=(s * spread, y, z + .1), bevel=0)
        yh = hull.bow + .05 * hull.L
        a.part('Anchor_chain', 'Undercarriage').tube([(s * spread, y, z + .12), (s * hull.hb(yh) * .8, yh,
                                                                                 hull.dz(yh) + .04)], .055, seg=4)


def rails(a, hull, y0, y1, n=6, h=.9, s_list=(-1, 1)):
    for s in s_list:
        ys = [y0 + (y1 - y0) * i / n for i in range(n + 1)]
        K.railing(a.part('Rails', 'Steel'), [hull.edge(y, s, inset=.08) for y in ys], h=h, post=1.2, r=.022)
