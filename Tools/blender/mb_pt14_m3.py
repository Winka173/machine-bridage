"""Play-test 14 model wave M3 (lane models): the sea bosses redrawn from scratch (owner, Docs/prompts/playtest14_vi.txt:
the boss notes and "Bo sung 03/10": Leviathan and Kraken 5 x the boss budget, Scylla, Nyx and Hydra 4 x; DECISIONS
"Play-test 14 model wave M3 (lane models)").

- leviathan: Kessler's battleship. Every runtime node at its old place, except the forward 155 mm triple (Part_sec_f,
  1.2 m aft so its well clears turret B) and the after 127 mm mount (Part_mg.001, beside the well). The three triple
  406 mm turrets (Part_gun* > Mount_gun* > Gun_barrels* / Gun_muzzles*: the barrels recoil on the mount pivot), the two
  155 mm triples (Mount_gun.003 / .004) that sleep until phase 1: each sits in a hull well (a hollow barbette with a
  dark floor and its two hatch leaves folded open) deep enough to take the whole gunhouse, so the runtime can lower it
  out of sight and raise it (VehicleView.WakeMounts). Mounts 5, 6 fire 127 mm shells, so Part_mg / .001 carry 127 mm
  enclosed mounts (the old gatlings fired 127 mm rounds); mount 15 (sam_post) a twin-arm SAM launcher (Mount_missile).
- scylla: its own model (it drew leviathan at half size): a fast cruiser in the Slava / Kirov read: the twin 130 mm
  AK-130 forward (Part_gun > Mount_gun), the 127 mm mount on the bridge roof (Part_mg > Mount_mg), the angled
  anti-ship missile tubes and the VLS (Part_vls), the pyramid mast, the funnels, the helicopter deck.
- kraken: the heavy aviation cruiser (Kiev / Kuznetsov read): the bow weapons deck with the two triple 406 mm turrets
  (Part_gun / .001: the def's main guns fire shells, so they are guns, not the old missile cells), the angled flight
  deck to port, the island to starboard, turret C (Part_gun.002) on the stern quarterdeck firing aft under the deck's
  round-down, the 155 mm triples in side sponsons, the 127 mm mounts, the gun galleries, the SAM launcher.
- nyx: the stealth destroyer (Zumwalt read): the AGS-style 155 mm turret (R1: it replaced the railgun), two stealth
  cupolas (mounts 1, 2 fire 127 mm shells), the peripheral VLS modules, the faceted deckhouse, a deck drone.
- R1 (owner 04/10, "đừng reuse gì hết"): Leviathan's, Scylla's and Nyx's weapons, directors, radars, launchers and VLS
  are drawn for each ship in mb_pt14_r1_naval (no shared mesh); the shared kit below is Kraken's only (redrawn in R2).
- hydra_sub: the drone submarine (model id hydra_sub; balance hydra "model"): the def's three gun mounts get three
  guns (twin 57 mm Mount_gun / .001 on retractable casing mounts, the 100 mm Mount_gun.002 forward of the sail).

Every round leaves from a barrel, tube or launcher with its Muzzle_* point at the mouth (owner 03/10). Ships float
with the waterline at the pivot (z 0). Built from frontier_kit / mb_kit27 / mb_kit35 primitives only.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W
import mb_pt14_r1_naval as RN

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= shared naval kit
def per_barrel(a, muzzle, tag, xs):
    """Muzzle_b<k>_<tag> under the pivot `muzzle`, one per barrel at the x offsets `xs` (left to right)."""
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def sfx(i):
    return '' if i == 0 else f'_{i:03d}'


def lerp_table(table, y, col):
    """Linear interpolation of column `col` of a station table [(y, ...), ...] sorted by y."""
    if y <= table[0][0]:
        return table[0][col]
    for r0, r1 in zip(table, table[1:]):
        if r0[0] <= y <= r1[0]:
            f = (y - r0[0]) / (r1[0] - r0[0])
            return r0[col] + (r1[col] - r0[col]) * f
    return table[-1][col]


class Hull:
    """A displacement hull from stations [(y, waterline half beam, deck half beam, deck z, keel depth, fullness)]
    (front to rear): the underwater body, the boot-top band and the topsides lofted through the same outline, so
    the colour lines follow the hull; half(y, z) gives its half beam anywhere (fittings sit on it)."""

    def __init__(self, stations, b0=-.4, b1=.5, flare=1.5):
        self.st = stations
        self.b0, self.b1, self.flare = b0, b1, flare

    def hb(self, y, z):
        hw = lerp_table(self.st, y, 1)
        hd = lerp_table(self.st, y, 2)
        zd = lerp_table(self.st, y, 3)
        kd = lerp_table(self.st, y, 4)
        n = lerp_table(self.st, y, 5)
        return self._hb(hw, hd, zd, kd, n, z)

    def _hb(self, hw, hd, zd, kd, n, z):
        # A floor that curves with z, so the stem's thin stations never lie in a straight line (zero-area faces).
        q = (z + kd) / (kd + zd)
        floor = .04 + .05 * q * q
        if z <= 0:
            t = min(1.0, -z / kd)
            return max(floor, hw * max(0.0, 1 - t ** n) ** (1 / n))
        t = min(1.0, z / zd)
        return max(floor, hw + (hd - hw) * t ** self.flare)

    def deck_z(self, y):
        return lerp_table(self.st, y, 3)

    def deck_half(self, y):
        return lerp_table(self.st, y, 2)

    def build(self, a, under='BarrelRed', boot='Undercarriage', top='Armor', top_name='Hull', round_edge=.12):
        s_under, s_boot, s_top = [], [], []
        for y, hw, hd, zd, kd, n in self.st:
            f = lambda z: self._hb(hw, hd, zd, kd, n, z)    # noqa: E731
            zs = [-kd * q for q in (.985, .93, .82, .64, .44, .25)] + [self.b0]
            s_under.append((y, [(0, -kd)] + [(f(z), z) for z in zs]))
            s_boot.append((y, [(f(self.b0), self.b0), (f(0), 0), (f(self.b1), self.b1)]))
            top_z = [self.b1 + (zd - round_edge - self.b1) * q for q in (0, .3, .58, .82, 1.0)]
            s_top.append((y, [(f(z), z) for z in top_z] + [(max(.04, hd - round_edge * .45), zd), (0, zd)]))
        K.section_loft(a.part('Hull_bottom', under), s_under)
        K.section_loft(a.part('Boot_top', boot), s_boot)
        K.section_loft(a.part(top_name, top), s_top)

    def line(self, part, z, y0, y1, out=.012, r=.02, sides=(-1, 1), step=2.0, seg=4):
        """A raised line along the hull at height z (strake seams, the degaussing cable, rubbing strakes)."""
        n = max(2, int(abs(y1 - y0) / step) + 1)
        for s in sides:
            pts = [(s * (self.hb(y, z) + out), y, z) for y in (y0 + (y1 - y0) * i / (n - 1) for i in range(n))]
            part.tube(pts, r, seg=seg)

    def deck_outline(self, y0, y1, inset=0.0, step=2.0):
        n = max(2, int(abs(y1 - y0) / step) + 1)
        ys = [y0 + (y1 - y0) * i / (n - 1) for i in range(n)]
        right = [(-(self.deck_half(y) - inset), y) for y in ys]
        left = [((self.deck_half(y) - inset), y) for y in reversed(ys)]
        return right + left

    def deck(self, a, name, mat, y0, y1, inset=.15, t=.06, lift=.02, step=2.0, part=None):
        """A deck plate following the sheer between y0 and y1."""
        sh = part or a.part(name, mat)
        before = set(sh.bm.verts)
        k.extrude(sh, self.deck_outline(y0, y1, inset, step), t, axis='Z')
        for v in sh.bm.verts:
            if v not in before:
                v.co.z += self.deck_z(v.co.y) + lift + t / 2
        return sh


def under_z(H, y, x):
    """The height of the hull's underside at (x, y): where its half beam below the waterline is |x|."""
    lo, hi = -lerp_table(H.st, y, 4), 0.0
    if H.hb(y, lo) >= abs(x):
        return lo
    for _ in range(30):
        mid = (lo + hi) / 2
        if H.hb(y, mid) >= abs(x):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def bollard_pair(part, loc, r=.16, gap=.5, h=.45):
    x, y, z = loc
    for dy in (-gap / 2, gap / 2):
        k.lathe(part, [(r, 0), (r, h * .8), (r * 1.35, h * .86), (r * 1.35, h), (0, h)], loc=(x, y + dy, z), seg=10)
    part.box((r * 1.6, gap + r * 2.2, .08), loc=(x, y, z + .04), bevel=0)


def fairlead(part, loc, facing_x, w=.8):
    x, y, z = loc
    part.box((.2, w, .35), loc=(x, y, z + .17), bevel=.02)
    for dy in (-w * .3, w * .3):
        part.cyl(.09, .32, loc=(x - facing_x * .14, y + dy, z + .16), seg=8, bevel=0)


def vent(part, loc, r=.3, h=1.2, turn=0.0):
    """A mushroom / cowl ventilator."""
    x, y, z = loc
    k.lathe(part, [(r, 0), (r, h * .75), (r * 1.4, h * .82), (r * 1.4, h * .95), (r * .6, h), (0, h)], loc=loc, seg=10)


def liferaft_rack(a, loc, n=3, axis='Y', r=.32, length=1.2, parent=None):
    """A rack of white life-raft canisters lying side by side."""
    x, y, z = loc
    rack = a.part('Raft_racks', 'Steel', parent)
    can = a.part('Liferafts', 'PlasterWhite', parent)
    band = a.part('Raft_bands', 'Hazard', parent)
    for i in range(n):
        off = (i - (n - 1) / 2) * (r * 2.15)
        if axis == 'Y':
            c, rot = (x + off, y, z + r + .06), (R90, 0, 0)
        else:
            c, rot = (x, y + off, z + r + .06), (0, R90, 0)
        k.lathe(can, [(0, -length / 2), (r * .8, -length / 2), (r, -length / 2 + .08), (r, length / 2 - .08),
                      (r * .8, length / 2), (0, length / 2)], loc=c, rot=rot, seg=10)
        for f in (-.3, .3):
            cc = (c[0], c[1] + f * length, c[2]) if axis == 'Y' else (c[0] + f * length, c[1], c[2])
            band.cyl(r * 1.03, .05, loc=cc, rot=rot, seg=10, bevel=0)
    if axis == 'Y':
        rack.box((n * r * 2.15 + .1, length * .7, .08), loc=(x, y, z + .04), bevel=0)
    else:
        rack.box((length * .7, n * r * 2.15 + .1, .08), loc=(x, y, z + .04), bevel=0)


def searchlight(a, loc, facing=(0, -1, 0), r=.35, parent=None):
    x, y, z = loc
    k.lathe(a.part('Searchlight_base', 'Steel', parent), [(r * .6, 0), (r * .5, r * .9), (r * .3, r * 1.0)], loc=loc,
            seg=8)
    rot = K.rot_to(facing)
    k.lathe(a.part('Searchlights', 'Armor', parent), [(r * .7, -r * .9), (r, -r * .3), (r, r * .4), (r * .95, r * .45)],
            loc=(x, y, z + r * 1.6), rot=rot, seg=12)
    f = Vector(facing).normalized() * r * .46
    a.part('Searchlight_lens', 'Lamp', parent).cyl(r * .9, .03, loc=(x + f.x, y + f.y, z + r * 1.6 + f.z), rot=rot,
                                                   seg=12, bevel=0)


def director(a, loc, w=2.2, d=1.8, h=1.1, parent=None, tag=''):
    """A fire-control director: the drum, the box house with its rangefinder arms and the radar dish on top."""
    x, y, z = loc
    k.lathe(a.part('Director_base' + tag, 'Armor', parent), [(w * .32, 0), (w * .32, h * .4), (w * .38, h * .45)],
            loc=loc, seg=12)
    hs = a.part('Director' + tag, 'Team', parent)
    k.block(hs, (w * .7, d, h * .8), loc=(x, y, z + h * .45), chamfer=.08, taper=(.86, .9))
    rf = a.part('Director_rf' + tag, 'Steel', parent)
    rf.cyl(.14, w, loc=(x, y + d * .15, z + h * .8), rot=(0, R90, 0), seg=8, bevel=0)
    for s in (-1, 1):
        rf.cyl(.2, .26, loc=(x + s * w / 2, y + d * .15, z + h * .8), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Director_glass' + tag, 'Glass', parent).box((w * .5, .03, .16), loc=(x, y - d / 2 - .01, z + h * .62),
                                                        bevel=0)
    K.dish(a.part('Director_dish' + tag, 'Medical', parent), a.part('Director_feed' + tag, 'Steel', parent),
           (x, y + .1, z + h * 1.25), r=w * .3, normal=(0, -1, .25), seg=12)


def triple_turret(a, index, part_loc, mount_z, P, part_name=None, house_mat='Team'):
    """A triple gun turret under its part pivot (Part_gun[.NNN] or a named part): the barbette, the gunhouse on
    Mount_gun[.NNN] (a faceted house with the sloped face plate, the rangefinder hood, periscope hoods, roof vents,
    the rear overhang with its hatches), three barrels (Gun_barrels* + Gun_muzzles*, the kick parts) in blast bags,
    Muzzle_gun[.NNN] at the middle barrel's tip and the per-barrel muzzles. P: dict(w=half width, f=front, b=back,
    h=height, L=barrel length, r=barrel radius, gap=barrel spacing, br=barbette radius, prefix='Gun', well=None)."""
    pname = part_name or K.name('Part_gun', index)
    tag = sfx(index)
    pre = P.get('prefix', 'Gun')
    p = a.pivot(pname, part_loc)
    px, py, pz = part_loc
    lz = mount_z - pz
    w, f, b, h = P['w'], P['f'], P['b'], P['h']
    br = P['br']
    if P.get('well'):
        _well(a, pname, tag, br, P['well'], lz, P.get('well_base', 0.0), pre)
    else:
        bar = a.part(f'{pre}_barbette{tag}', 'Armor', p)
        k.lathe(bar, [(br, P.get('barbette_base', -.05)), (br, lz - .12), (br * 1.03, lz - .08), (br * 1.03, lz - .02),
                      (br * .96, lz)], seg=28)
        bolts = a.part('Kit_bolts', 'Steel', p)
        for i in range(24):
            u = i * TAU / 24
            bolts.cyl(.05, .04, loc=(math.cos(u) * br * 1.035, math.sin(u) * br * 1.035, lz - .05), rot=(0, R90, u),
                      seg=6, bevel=0)
    m = a.pivot(K.name('Mount_gun', index), (0, 0, lz), p)
    k.lathe(a.part(f'{pre}_ring{tag}', 'Steel', m), [(br * .94, -.02), (br * .97, .06), (br * .9, .12)], seg=24)
    c = min(w, -f) * .3
    sec = [(-w + c, f), (w - c, f), (w, f + c * 1.6), (w, b - .5), (w - .6, b), (-w + .6, b), (-w, b - .5),
           (-w, f + c * 1.6)]
    top = [(-w * .76, f * .82), (w * .76, f * .82), (w * .9, f * .82 + c * 1.4), (w * .9, b - .55),
           (w * .9 - .5, b - .05), (-w * .9 + .5, b - .05), (-w * .9, b - .55), (-w * .9, f * .82 + c * 1.4)]
    mid = [(x * 1.0, y) for x, y in sec]
    W.poly_turret(a.part(f'{pre}_house{tag}', house_mat, m), [(0, sec), (h * .55, mid), (h, top)], chamfer=.07)
    # The sloped face plate, its bolt line; the gun ports; the roof plates (inset), the rangefinder hood.
    zg = P.get('zg', h * .48)
    face = a.part(f'{pre}_face{tag}', 'Armor', m)
    k.block(face, (2 * w - c * 2.2, .35, h * .92), loc=(0, f - .05, h * .45), rot=(.32, 0, 0), chamfer=.05,
            taper=(.9, 1))
    gap = P['gap']
    xs = (-gap, 0, gap)
    ports = a.part(f'{pre}_ports{tag}', 'Undercarriage', m)
    for x in xs:
        ports.box((P['r'] * 4.2, .2, P['r'] * 5.2), loc=(x, f - .25, zg), rot=(.32, 0, 0), bevel=.03)
    roof = a.part(f'{pre}_roof{tag}', 'Armor', m)
    k.block(roof, (2 * w * .78, (b - f) * .55, .08), loc=(0, (f + b) / 2 + .2, h - .02), chamfer=.02)
    k.inset(roof, lambda cc, n, fc: n.z > .9, width=.12, depth=-.02)
    rh = a.part(f'{pre}_hoods{tag}', 'Armor', m)
    for s in (-1, 1):
        k.block(rh, (.55, .7, .38), loc=(s * w * .48, f * .55, h + .12), chamfer=.05, taper=(.8, .85))
        a.part('Glass', 'Glass', m).box((.36, .02, .1), loc=(s * w * .48, f * .55 - .36, h + .2), bevel=0)
    rfl = P.get('rangefinder', 0)
    if rfl:
        k.lathe(a.part(f'{pre}_rangefinder{tag}', 'Armor', m), [(0, -rfl / 2), (.24, -rfl / 2), (.3, -rfl / 2 + .15),
                                                               (.3, rfl / 2 - .15), (.24, rfl / 2), (0, rfl / 2)],
                loc=(0, b - 1.3, h - .1), rot=(0, R90, 0), seg=12)
        for s in (-1, 1):
            k.block(rh, (.4, .5, .5), loc=(s * rfl / 2, b - 1.3, h - .25), chamfer=.04)
    vents_ = a.part(f'{pre}_vents{tag}', 'Steel', m)
    for x in (-w * .55, w * .55):
        k.lathe(vents_, [(.2, 0), (.2, .25), (.3, .3), (.3, .38), (0, .4)], loc=(x, b - .6, h - .02), seg=8)
    hatch = a.part(f'{pre}_hatches{tag}', 'Armor', m)
    for s in (-1, 1):
        k.block(hatch, (.8, .7, .1), loc=(s * w * .45, b - 2.4, h), chamfer=.02)
    K.ladder(a.part('Ladders', 'Steel', m), (w + .03, b - 1.2, .2), (w + .03, b - 1.2, h - .1), width=.45, step=.32,
             facing=(1, 0))
    rails = a.part('Railings', 'Steel', m)
    rails.tube([(-w * .75, b - .25, h + .55), (w * .75, b - .25, h + .55)], .03, seg=4)
    for x in (-w * .75, 0, w * .75):
        rails.box((.05, .05, .55), loc=(x, b - .25, h + .28), bevel=0)
    a.part('Team_band', 'Team', m).box((2 * w * .62, 1.0, .03), loc=(0, (f + b) / 2 + 1.0, h + .02), bevel=0)
    # Three barrels in canvas blast bags: the barrels and brakes are the mount's kick parts.
    bags = a.part(f'{pre}_bags{tag}', 'Canvas', m)
    y0 = f - .3
    for x in xs:
        k.lathe(bags, [(P['r'] * 2.1, 0), (P['r'] * 2.45, .14), (P['r'] * 2.2, .3), (P['r'] * 1.6, .42)],
                loc=(x, y0 + .1, zg), rot=K.FORWARD, seg=10)
        K.gun_barrel(a, f'{pre}_barrels{tag}', m, x, y0, zg, P['L'], P['r'], seg=12, extractor=(.18, 1.22, .7),
                     brake_name=f'{pre}_muzzles{tag}', brake='collar')
    mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - P['L'] - .1, zg), m)
    per_barrel(a, mz, f'gun_{index:03d}' if index else 'gun', xs)
    K.soot(a, (px, py + y0 - P['L'], mount_z + zg), radius=P['r'] * 4, k=.4)
    K.tone(a, pname, k=.92)
    return m


def _well(a, pname, tag, br, depth, seat, base, pre):
    """The hull well of a turret that sleeps in the hull (VehicleView.WakeMounts lowers the gunhouse until its top is
    at the seat): a hollow barbette from `base` up to the seat, its inner wall down to a dark floor `depth` below the
    seat, the elevator ring on the floor, the two hatch leaves folded open on the lip, the lip's bolt ring."""
    outer, inner = br + .45, br + .06
    wall = a.part(f'{pre}_well{tag}', 'Armor', pname)
    k.lathe(wall, [(outer, base), (outer, seat - .14), (outer - .06, seat), (inner, seat), (inner, seat - depth),
                   (0, seat - depth)], seg=32)
    k.lathe(a.part(f'{pre}_well_floor{tag}', 'Undercarriage', pname),
            [(inner - .04, seat - depth + .02), (inner - .04, seat - depth + .12), (inner * .55, seat - depth + .12),
             (inner * .55, seat - depth + .03)], seg=24)
    lip = a.part(f'{pre}_well_lip{tag}', 'Hazard', pname)
    k.ring(lip, [(inner + .02, seat + .005), (outer - .1, seat + .005), (outer - .1, seat + .02),
                 (inner + .02, seat + .02)], seg=32)
    bolts = a.part('Kit_bolts', 'Steel', pname)
    for i in range(28):
        u = i * TAU / 28
        bolts.cyl(.045, .04, loc=(math.cos(u) * (outer - .22), math.sin(u) * (outer - .22), seat + .03), seg=6, bevel=0)
    # The two hatch leaves, swung open: half discs hanging down the barbette's sides from their hinges on the lip.
    leaves = a.part(f'{pre}_well_doors{tag}', 'Team', pname)
    hinge = a.part('Kit_hinges', 'Steel', pname)
    R = min(inner * .95, max(.6, seat - base - .15))
    for s in (-1, 1):
        prof = [(R * math.cos(u), seat - .05 - R * math.sin(u)) for u in (i * math.pi / 12 for i in range(13))]
        k.extrude(leaves, prof, .1, loc=(s * (outer + .07), 0, 0), axis='X', chamfer=.02)
        hinge.cyl(.07, R * 1.6, loc=(s * (outer + .02), 0, seat - .02), rot=(R90, 0, 0), seg=8, bevel=0)


def dp_mount(a, mount, muzzle, loc, parent, tag, s=1.0, shield='round', base=0.0):
    """A 127 mm single enclosed gun mount on its yaw pivot: the base ring, the gunhouse (round Mk 42 or faceted
    stealth shield), the barrel (Dp_barrels*, the kick part) with its collar brake, Muzzle_* at the mouth.
    Returns the mount pivot name."""
    if base > 0:
        k.lathe(a.part('Dp_pedestal' + tag, 'Armor', parent), [(1.35 * s, -base), (1.35 * s, -.05), (1.25 * s, 0)],
                loc=loc, seg=16)
    m = a.pivot(mount, loc, parent)
    k.lathe(a.part('Dp_ring' + tag, 'Steel', m), [(1.2 * s, 0), (1.2 * s, .1), (1.1 * s, .15)], seg=16)
    house = a.part('Dp_house' + tag, 'Team', m)
    if shield == 'round':
        W.poly_turret(house, [
            (.1, [(-.9 * s, -1.3 * s), (.9 * s, -1.3 * s), (1.25 * s, -.5 * s), (1.25 * s, 1.5 * s),
                  (-1.25 * s, 1.5 * s), (-1.25 * s, -.5 * s)]),
            (1.25 * s, [(-.55 * s, -1.05 * s), (.55 * s, -1.05 * s), (1.0 * s, -.35 * s), (1.0 * s, 1.35 * s),
                        (-1.0 * s, 1.35 * s), (-1.0 * s, -.35 * s)]),
            (1.55 * s, [(-.35 * s, -.6 * s), (.35 * s, -.6 * s), (.7 * s, -.1 * s), (.7 * s, 1.15 * s),
                        (-.7 * s, 1.15 * s), (-.7 * s, -.1 * s)])], chamfer=.04 * s)
    else:
        W.poly_turret(house, [
            (.1, [(-.5 * s, -1.9 * s), (.5 * s, -1.9 * s), (1.2 * s, -.4 * s), (1.2 * s, 1.5 * s),
                  (-1.2 * s, 1.5 * s), (-1.2 * s, -.4 * s)]),
            (1.3 * s, [(-.2 * s, -1.3 * s), (.2 * s, -1.3 * s), (.75 * s, -.25 * s), (.75 * s, 1.2 * s),
                       (-.75 * s, 1.2 * s), (-.75 * s, -.25 * s)])], chamfer=.03 * s)
    zg = .62 * s
    a.part('Dp_port' + tag, 'Undercarriage', m).box((.36 * s, .16, .5 * s), loc=(0, -1.12 * s, zg), bevel=.02)
    L = 4.9 * s
    y0 = -1.05 * s
    K.gun_barrel(a, 'Dp_barrels' + tag, m, 0, y0, zg, L, .085 * s, seg=10, extractor=(.3, 1.2, .3 * s),
                 brake_name='Dp_muzzles' + tag, brake='collar')
    a.pivot(muzzle, (0, y0 - L - .05, zg), m)
    k.block(a.part('Dp_hatch' + tag, 'Armor', m), (.6 * s, .5 * s, .08), loc=(0, .7 * s, 1.27 * s if shield == 'round'
                                                                              else 1.32 * s), chamfer=.02)
    return m


def aa_triple(a, mount, muzzle, loc, parent, tag, s=1.0):
    """A triple 25 mm on its pedestal with the splinter shield (Aa_guns*: no kick part, a light gun)."""
    m = a.pivot(mount, loc, parent)
    k.lathe(a.part('Aa_mount' + tag, 'Armor', m), [(.5 * s, -.25), (.5 * s, -.15), (.38 * s, -.05), (.3 * s, .2)],
            seg=10)
    k.block(a.part('Aa_cradle' + tag, 'Steel', m), (.62 * s, .55 * s, .3 * s), loc=(0, .05, .32 * s), chamfer=.03)
    k.block(a.part('Aa_shield' + tag, 'Team', m), (1.05 * s, .06, .5 * s), loc=(0, -.42 * s, .3 * s),
            rot=(-.25, 0, 0), chamfer=.012)
    g = a.part('Aa_guns' + tag, 'Steel', m)
    for dx in (-.17 * s, 0, .17 * s):
        k.lathe(g, [(.045 * s, 0), (.045 * s, .3), (.03 * s, .33), (.03 * s, 1.35 * s), (.045 * s, 1.37 * s),
                    (.045 * s, 1.45 * s), (0, 1.46 * s)], loc=(dx, -.3 * s, .42 * s), rot=K.FORWARD, seg=6)
    a.part('Aa_ammo' + tag, 'Crate', m).box((.22 * s, .3 * s, .2 * s), loc=(.42 * s, .15 * s, .45 * s), bevel=.02)
    a.part('Aa_seat' + tag, 'Rubber', m).box((.25 * s, .2 * s, .06), loc=(-.4 * s, .35 * s, .3 * s), bevel=.02)
    a.pivot(muzzle, (0, -1.8 * s, .42 * s), m)
    return m


def gatling(a, loc, parent=None, s=1.0, facing=0.0):
    """A Phalanx-style close-in gun (decoration beside a 127 mm mount; the APS's guns): base, radome, gatling."""
    x, y, z = loc
    k.lathe(a.part('Ciws_base', 'Armor', parent), [(.6 * s, 0), (.55 * s, .55 * s), (.45 * s, .65 * s)], loc=loc,
            seg=12)
    body = a.part('Ciws_body', 'PlasterWhite', parent)
    k.block(body, (.75 * s, 1.0 * s, .6 * s), loc=(x, y + .1 * s, z + .65 * s), chamfer=.06 * s)
    k.lathe(body, [(.32 * s, 0), (.4 * s, .42 * s), (.34 * s, .85 * s), (0, 1.0 * s)], loc=(x, y + .2 * s, z + 1.2 * s),
            seg=12)
    g = a.part('Ciws_gun', 'Steel', parent)
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.024 * s, 1.25 * s, loc=(x + math.cos(u) * .065 * s, y - .85 * s, z + .95 * s + math.sin(u) * .065 * s),
              rot=K.FORWARD, seg=5, bevel=0)
    g.cyl(.12 * s, .14 * s, loc=(x, y - 1.45 * s, z + .95 * s), rot=K.FORWARD, seg=10, bevel=0)


def twin_arm_launcher(a, loc, parent=None, s=1.0, tag=''):
    """A Mk 26-style twin-arm SAM launcher on Mount_missile: the deck ring and the magazine hatch, the trainable
    pedestal, two arms with a missile on each rail; Muzzle_missile at the left rail's missile nose."""
    x, y, z = loc
    k.lathe(a.part('Sam_deck' + tag, 'Armor', parent), [(1.5 * s, -.3), (1.5 * s, 0), (1.35 * s, .06)], loc=loc,
            seg=20)
    a.part('Sam_hatch' + tag, 'Hazard', parent).box((1.2 * s, .9 * s, .04), loc=(x, y + 2.0 * s, z + .02), bevel=0)
    a.part('Sam_hatch' + tag, 'Steel', parent).box((1.3 * s, 1.0 * s, .03), loc=(x, y + 2.0 * s, z + .005), bevel=0)
    m = a.pivot('Mount_missile', (x, y, z + .06), parent)
    k.lathe(a.part('Sam_pedestal' + tag, 'Team', m), [(1.1 * s, 0), (1.0 * s, .5 * s), (.7 * s, .8 * s),
                                                     (.5 * s, 1.0 * s)], seg=16)
    k.block(a.part('Sam_trunnion' + tag, 'Team', m), (1.9 * s, .8 * s, .55 * s), loc=(0, 0, 1.05 * s),
            chamfer=.06 * s)
    arms = a.part('Sam_arms' + tag, 'Steel', m)
    msl = a.part('Sam_missiles' + tag, 'PlasterWhite', m)
    fins = a.part('Sam_fins' + tag, 'Steel', m)
    for sx in (-1, 1):
        ax = sx * .78 * s
        arms.box((.22 * s, 2.6 * s, .25 * s), loc=(ax, -.5 * s, 1.55 * s), rot=(.12, 0, 0), bevel=.02)
        arms.box((.3 * s, .5 * s, .45 * s), loc=(ax, .6 * s, 1.32 * s), bevel=.03)
        tail = (ax, .7 * s, 1.92 * s)
        k.lathe(msl, [(0, 0), (.15 * s, .02), (.17 * s, .1), (.17 * s, 3.2 * s), (.12 * s, 3.65 * s), (0, 3.9 * s)],
                loc=tail, rot=(R90 - .12, 0, 0), seg=10)
        for j in range(4):
            u = j * R90 + math.pi / 4
            fins.box((.02, .5 * s, .26 * s), loc=(ax + math.cos(u) * .24 * s, .55 * s, 1.9 * s + math.sin(u) * .24 * s),
                     rot=(0, -u, 0), bevel=0)
    a.pivot('Muzzle_missile', (.78 * s, -3.15 * s, 2.4 * s), m)
    return m


def radar_array(a, pivot_name, loc, parent, w=3.0, h=1.0, tag=''):
    """A spinning search radar (`Radar` pivot): the drive, the curved reflector frame and its face."""
    r = a.pivot(pivot_name, loc, parent)
    a.part('Radar_drive' + tag, 'Steel', r).cyl(.3, .4, loc=(0, 0, .1), seg=10, bevel=0)
    fr = a.part('Radar_array' + tag, 'Armor', r)
    pts = [(-w / 2 + w * i / 8, .14 * math.cos((i - 4) / 4 * R90) - .1) for i in range(9)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        fr.box((math.hypot(x1 - x0, y1 - y0) + .02, .12, h), loc=((x0 + x1) / 2, (y0 + y1) / 2, .3 + h / 2),
               rot=(0, 0, math.atan2(y1 - y0, x1 - x0)), bevel=0)
    a.part('Radar_face' + tag, 'Undercarriage', r).box((w * .96, .02, h * .8), loc=(0, -.2, .3 + h / 2), bevel=0)
    fr.box((.15, .8, .15), loc=(0, .25, .25), bevel=0)
    return r


def team_mark(part, loc, size, normal_x):
    """Kessler's chevron (two plates in a V) on a hull side or a funnel."""
    x, y, z = loc
    w, h = size
    for s in (-1, 1):
        part.box((.03, w, h * .28), loc=(x, y + s * w * .3, z), rot=(s * .55, 0, 0), bevel=0)


# ============================================================================= leviathan
# (y, waterline half beam, deck half beam, deck z, keel depth, fullness)
LEV = [(-43.0, .04, .12, 5.75, .6, 1.0), (-42.2, .1, .75, 5.65, 1.4, 1.1), (-40.8, .45, 1.85, 5.46, 2.3, 1.3),
       (-38.4, 1.45, 3.3, 5.24, 2.5, 1.5), (-35.0, 2.85, 4.65, 5.02, 2.6, 1.8), (-31.0, 4.35, 5.8, 4.8, 2.6, 2.1),
       (-26.0, 5.9, 6.9, 4.56, 2.6, 2.5), (-20.0, 7.1, 7.7, 4.33, 2.6, 2.9), (-14.0, 7.8, 8.1, 4.15, 2.6, 3.3),
       (-7.0, 8.08, 8.24, 4.03, 2.6, 3.6), (0.0, 8.12, 8.27, 3.95, 2.6, 3.7), (8.0, 8.1, 8.25, 3.88, 2.6, 3.6),
       (16.0, 7.95, 8.15, 3.82, 2.6, 3.3), (24.0, 7.55, 7.92, 3.74, 2.55, 2.8), (30.0, 6.95, 7.58, 3.66, 2.3, 2.3),
       (35.0, 6.15, 7.05, 3.6, 1.85, 1.9), (39.0, 5.35, 6.5, 3.55, 1.4, 1.7), (42.0, 4.75, 6.0, 3.52, 1.05, 1.6),
       (43.9, 4.45, 5.7, 3.5, .85, 1.6)]
LEV_H = Hull(LEV)
LEV_KEEP = (r'^(Hull|Hull_bottom|Boot_top|Deck|Deckhouse|Superstructure|Tower|Funnel|Flight_deck|Bridge_wings|'
            r'[A-Za-z]+_(barrels|muzzles)(_\d+)?|Gun_house(_\d+)?|Sec_house(_\d+)?|Dp_house(_\d+)?|Aa_guns(_\d+)?|'
            r'Sam_missiles|Abl_box|Radar\w*|Antennas?|Mainmast|Glass|Windows|Railings|Helo\w*|Heli\w*)$')
LEV_SEC_F = (0, -6.0, 5.79)       # moved 1.2 m aft (was -7.2): the well's barbette clears turret B
LEV_MG1 = (2.6, 14.8, 6.26)       # the after 127 mm, beside the after well (was 2.1, 16.5)
DH_Z = 6.25                       # the deckhouse roof


def _lev_hull(a):
    H = LEV_H
    H.build(a, under='BarrelRed', boot='Undercarriage', top='Armor')
    # The armour belt: a raised plate band along the waterline amidships, its ends tapered; the strake seams,
    # the degaussing cable, the rubbing strake under the deck edge; portholes in rows fore and aft of the belt.
    belt = a.part('Armor_belt', 'Team')
    for s in (-1, 1):
        rings = []
        for y in [-29.0 + i * 2.0 for i in range(30)]:
            o = .1 if -27.0 <= y <= 27.0 else .035
            rings.append([(s * (H.hb(y, -1.1) - .05), y, -1.1)] +
                         [(s * (H.hb(y, z) + o * (.5 if z < 0 else 1.0)), y, z) for z in (-1.1, -.4, .6, 1.7)] +
                         [(s * (H.hb(y, 1.7) - .05), y, 1.7)])
        belt.loft(rings, bevel=0)
    seams = a.part('Hull_seams', 'Armor')
    H.line(seams, 2.35, -40.0, 42.5, out=.01, r=.018)
    H.line(seams, 1.75, -39.0, -29.5, out=.01, r=.018)
    H.line(seams, 1.75, 29.5, 42.5, out=.01, r=.018)
    H.line(a.part('Degaussing', 'Undercarriage'), 3.3, -38.0, 41.0, out=.03, r=.04)
    for y in range(-38, 43, 4):
        for s in (-1, 1):
            z0, z1 = 1.8, H.deck_z(y) - .2
            seams.tube([(s * (H.hb(y, z0) + .01), y, z0), (s * (H.hb(y, (z0 + z1) / 2) + .012), y, (z0 + z1) / 2),
                        (s * (H.hb(y, z1) + .01), y, z1)], .014, seg=3)
    for s in (-1, 1):
        pts = [(s * (H.hb(y, 2.75) + .005), y, 2.75) for y in list(range(-37, -28, 2)) + list(range(30, 42, 2))]
        K.portholes(a, pts, (s, 0, 0), r=.15)
        pts = [(s * (H.hb(y, 1.95) + .005), y, 1.95) for y in range(-36, -29, 3)]
        K.portholes(a, pts, (s, 0, 0), r=.13)
    # Draft marks at the stem and the stern, the bow's Kessler chevrons, the bilge keels, four screws on their shaft
    # brackets and the twin rudders under the counter.
    marks = a.part('Draft_marks', 'PlasterWhite')
    for y in (-40.6, 42.4):
        for s in (-1, 1):
            for z in (-.9, -.4, .1, .6, 1.1, 1.6):
                marks.box((.02, .35, .08), loc=(s * (H.hb(y, z) + .02), y, z), bevel=0)
    # The rubbing strake under the deck edge, the knuckle line at the bow.
    H.line(a.part('Rubbing_strake', 'Steel'), 3.0, -36.0, 43.0, out=.05, r=.06, step=1.5)
    bk = a.part('Bilge_keels', 'BarrelRed')
    for s in (-1, 1):
        pts = [(s * (H.hb(y, -2.2) + .12), y, -2.25) for y in range(-14, 22, 3)]
        bk.tube(pts, .09, seg=4)
    screws = a.part('Screws', 'Gilded')
    shafts = a.part('Shafts', 'Steel')
    for x, y, r in ((1.9, 35.6, .72), (-1.9, 35.6, .72), (4.3, 31.6, .62), (-4.3, 31.6, .62)):
        zc = under_z(H, y, x) - r - .12
        shafts.tube([(x * .6, y - 10.0, under_z(H, y - 10.0, x * .6) + .25), (x, y - .4, zc)], .15, seg=8)
        shafts.limb((x, y - 1.4, zc), (x * .82, y - 1.6, under_z(H, y - 1.6, x * .82) + .2), .13, .32, bevel=0)
        k.lathe(screws, [(0, -.3), (.24, -.26), (.24, .22), (0, .34)], loc=(x, y, zc), rot=(-R90, 0, 0), seg=10)
        for j in range(4):
            u = j * R90 + .4
            screws.box((.07, .22, r * .8), loc=(x + math.cos(u) * r * .55, y + .05, zc + math.sin(u) * r * .55),
                       rot=(0, -u + R90, 0), bevel=0)
    rud = a.part('Rudders', 'BarrelRed')
    for x in (1.6, -1.6):
        zt = under_z(H, 37.6, x) + .25
        k.extrude(rud, [(36.9, zt), (39.0, zt), (39.0, zt - 2.0), (37.2, zt - 2.15)], .28, loc=(x, 0, 0), axis='X',
                  chamfer=.04)


def _lev_deck(a):
    H = LEV_H
    deck = H.deck(a, 'Deck', 'Wood', -41.6, 41.5, inset=.22, t=.06, step=2.0)
    del deck
    # Plank seams and the steel waterways round the deck edge; the breakwater ahead of turret A.
    seams = a.part('Deck_seams', 'Undercarriage')
    for x in (-6.0, -4.5, -3.0, -1.5, 1.5, 3.0, 4.5, 6.0):
        ys = [y for y in range(-38, 42, 2) if H.deck_half(y) - .5 > abs(x)]
        if len(ys) > 1:
            seams.tube([(x, y, H.deck_z(y) + .095) for y in ys], .012, seg=3)
    ww = a.part('Waterways', 'Steel')
    for s in (-1, 1):
        ww.tube([(s * (H.deck_half(y) - .14), y, H.deck_z(y) + .07) for y in range(-41, 44, 2)], .07, seg=4)
    bw = a.part('Breakwater', 'Armor')
    for s in (-1, 1):
        y0, y1 = -30.4, -27.2
        L = math.hypot(4.8, y1 - y0)
        ym = (y0 + y1) / 2
        bw.box((L, .1, 1.0), loc=(s * 2.4, ym, H.deck_z(ym) + .55), rot=(0, 0, s * math.atan2(y1 - y0, 4.8)), bevel=.02)
        for f in (.2, .5, .8):
            bw.limb((s * 4.8 * f, y0 + (y1 - y0) * f + .5, H.deck_z(ym) + .08),
                    (s * 4.8 * f, y0 + (y1 - y0) * f + .05, H.deck_z(ym) + .9), .08, .08, bevel=0)
    # The anchor gear: three hawse pipes and anchors, the chains to the capstans, the jackstaff and the fairleads.
    ag = a.part('Anchors', 'Steel')
    ch = a.part('Chain', 'Undercarriage')
    cap = a.part('Winch', 'Steel')
    for s, x in ((1, 2.85), (-1, -2.85)):
        y = -37.6
        z = H.hb(y, 4.0)
        ag.cyl(.45, .35, loc=(s * (z + .1), y, 3.9), rot=(0, s * R90, 0), seg=12, bevel=.03)
        ag.box((.22, .5, 1.5), loc=(s * (z + .26), y, 3.2), rot=(0, 0, 0), bevel=.03)
        ag.box((.18, 1.2, .25), loc=(s * (z + .26), y, 2.45), rot=(0, 0, 0), bevel=.03)
        zz = H.deck_z(-34.0) + .1
        ch.tube([(s * 2.5, -37.4, H.deck_z(-37.4) + .12), (s * 1.9, -35.4, zz), (s * 1.6, -33.8, zz)], .12, seg=4)
        k.lathe(cap, [(.55, 0), (.55, .45), (.38, .55), (.38, .82), (.5, .9), (0, .95)], loc=(s * 1.6, -33.4, zz),
                seg=14)
    a.part('Jackstaff', 'Steel').cyl(.06, 2.6, loc=(0, -42.3, H.deck_z(-42.3) + 1.3), seg=6, bevel=0)
    a.part('Ensign', 'Team').box((.02, .9, .6), loc=(0, -42.0, H.deck_z(-42.3) + 2.3), bevel=0)
    fit = a.part('Fittings', 'Steel')
    for y in (-36.5, -30.0, 22.0, 30.5, 38.0):
        for s in (-1, 1):
            hb = H.deck_half(y)
            bollard_pair(fit, (s * (hb - .9), y, H.deck_z(y) + .09))
            fairlead(fit, (s * (hb - .35), y + 1.2, H.deck_z(y) + .09), s)
    # Guard rails along the deck edge (stanchions and wire), the vents and hatches on the open decks.
    rails = a.part('Railings', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-41.0, -9.0), (-9.0, 12.0), (12.0, 43.0)):
            ys = [y0 + (y1 - y0) * i / 8 for i in range(9)]
            K.railing(rails, [(s * (H.deck_half(y) - .25), y, H.deck_z(y) + .09) for y in ys], h=.95, post=2.0,
                      r=.022)
    v = a.part('Vents', 'Steel')
    for x, y in ((-4.2, -31.5), (4.2, -31.5), (-5.2, 23.2), (5.2, 23.2), (-3.4, 31.0), (3.4, 31.0)):
        vent(v, (x, y, H.deck_z(y) + .08), r=.3, h=1.1)
    for x, y in ((-3.6, -17.4), (3.6, -17.4), (0, 30.8), (-2.2, 33.4)):
        k.block(a.part('Hatches', 'Armor'), (1.3, 1.1, .22), loc=(x, y, H.deck_z(y) + .16), chamfer=.04)
    for x, y in ((-5.6, -25.0), (5.6, -25.0), (-6.0, 21.5), (6.0, 21.5)):
        liferaft_rack(a, (x, y, H.deck_z(y) + .09), n=3, axis='X', r=.3, length=1.1)


def _lev_superstructure(a):
    """The deckhouse (one long block on the main deck, the forward tier over it), the tower with the bridge, the
    platforms, the directors and the radar; the funnel (Part_engine), the VLS (Part_vls), the mainmast, the boats,
    the searchlights, the APS clusters (Mount_APS)."""
    z0 = 3.9
    dh = a.part('Deckhouse', 'Team')
    out = [(-4.4, -9.4), (4.4, -9.4), (5.0, -7.2), (5.0, 15.6), (4.6, 17.0), (-4.6, 17.0), (-5.0, 15.6), (-5.0, -7.2)]
    W.poly_turret(dh, [(z0, out), (DH_Z, [(x * .97, y + (.15 if y < 0 else -.15)) for x, y in out])], chamfer=.08)
    k.inset(dh, lambda c, n, f: abs(n.z) < .3 and c.z > z0 + .4, width=.12, depth=-.025)
    roof = a.part('Deckhouse_roof', 'Armor')
    k.block(roof, (9.4, 25.2, .06), loc=(0, 3.8, DH_Z + .01), chamfer=.02)
    for s in (-1, 1):
        K.portholes(a, [(s * 5.0, y, 5.25) for y in range(-6, 15, 2)], (s, 0, 0), r=.15)
        K.door(a, (s * 4.98, 1.0, z0 + .05), size=(.9, 1.8), normal=(s, 0, 0), mat='Armor', frame_mat='Steel')
        K.door(a, (s * 4.98, 12.5, z0 + .05), size=(.9, 1.8), normal=(s, 0, 0), mat='Armor', frame_mat='Steel')
        K.ladder(a.part('Ladders', 'Steel'), (s * 5.25, -5.5, 4.0), (s * 5.25, -4.8, DH_Z), width=.5, step=.3)
    # The forward tier (the 01 level): the 127 mm on its right wing, the director on the left.
    t1 = a.part('Superstructure', 'Team')
    tier = [(-3.1, -4.7), (3.1, -4.7), (4.2, -3.9), (4.2, 3.2), (3.4, 4.1), (-3.4, 4.1), (-4.2, 3.2), (-4.2, -3.9)]
    W.poly_turret(t1, [(DH_Z, tier), (9.2, [(x * .96, y) for x, y in tier])], chamfer=.07)
    k.inset(t1, lambda c, n, f: abs(n.z) < .3, width=.12, depth=-.025)
    a.part('Tier_deck', 'Armor').box((8.8, 9.2, .1), loc=(0, -.3, 9.25), bevel=.02)
    for i in range(9):
        x = -2.4 + i * .6
        a.part('Windows', 'Glass').box((.42, .04, .38), loc=(x, -4.72, 8.4), rot=(-.1, 0, 0), bevel=0)
    for s in (-1, 1):
        K.portholes(a, [(s * 4.22, y, 7.8) for y in (-2.5, -1.0, .5, 2.0)], (s, 0, 0), r=.14)
    rails = a.part('Railings', 'Steel')
    # (R1: the rails stop short of the 5-inch mount's sweep on the right wing.)
    K.railing(rails, [(-1.2, -4.8, 9.3), (4.3, -4.8, 9.3)], h=.9, post=1.1, r=.022)
    for s in (-1, 1):
        K.railing(rails, [(s * 4.35, -4.6 if s > 0 else -1.1, 9.3), (s * 4.35, 4.2, 9.3)], h=.9, post=1.1, r=.022)
    RN.lev_director(a, (3.3, -1.0, 9.3), tag='')
    # The tower: three tiers to the bridge, the navigation bridge with its wings and windows, the upper tiers and the
    # foretop (directors, the rangefinder), the radar mast on top (Part_radar > Radar).
    tw = a.part('Tower', 'Team')
    tiers = ((9.3, 12.0, 1.8, 2.6, 1.7, 2.4, -.3), (12.0, 13.1, 2.9, 2.9, 2.9, 2.8, -.5),
             (13.1, 15.2, 1.6, 2.2, 1.45, 2.0, -.4), (15.2, 17.3, 1.3, 1.8, 1.1, 1.5, -.6))
    for zb, zt, w0, d0, w1, d1, yc in tiers:
        k.sharp_loft(tw, [[(-w0, yc - d0, zb), (w0, yc - d0, zb), (w0, yc + d0, zb), (-w0, yc + d0, zb)],
                          [(-w1, yc - d1, zt), (w1, yc - d1, zt), (w1, yc + d1, zt), (-w1, yc + d1, zt)]],
                     chamfer=.06)
        a.part('Tower_platforms', 'Armor').box((2 * w0 + 1.4, 2 * d0 + 1.0, .1), loc=(0, yc, zt), bevel=.02)
        K.railing(rails, [(-w0 - .6, yc - d0 - .45, zt), (w0 + .6, yc - d0 - .45, zt), (w0 + .6, yc + d0 + .4, zt),
                          (-w0 - .6, yc + d0 + .4, zt), (-w0 - .6, yc - d0 - .45, zt)], h=.85, post=1.0, r=.02)
    # The navigation bridge (13.1 level): the wide window band and its wings.
    for i in range(11):
        x = -2.5 + i * .5
        a.part('Windows', 'Glass').box((.4, .04, .5), loc=(x, -3.42, 12.7), rot=(-.15, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Bridge_wings', 'Armor').box((1.6, 1.5, .12), loc=(s * 3.7, -2.8, 12.05), bevel=.02)
        a.part('Windows', 'Glass').box((.04, 1.8, .45), loc=(s * 2.93, -.5, 12.65), bevel=0)
        searchlight(a, (s * 3.9, -2.8, 12.12), facing=(s * .5, -1, 0), r=.32)
        for z in (13.6, 15.7):
            a.part('Windows', 'Glass').box((.04, 1.2, .3), loc=(s * (1.62 if z < 15 else 1.26), -.4, z), bevel=0)
    for i in range(5):
        a.part('Windows', 'Glass').box((.36, .04, .32), loc=(-1.0 + i * .5, -2.63, 14.2), bevel=0)
    RN.lev_director(a, (0, -2.05, 17.36), tag='_top')
    K.ladder(a.part('Ladders', 'Steel'), (1.9, 2.3, 9.3), (1.9, 2.3, 13.1), width=.45, step=.3, facing=(0, 1))
    # Part_radar: the radar mast on the foretop with the yard, the whips, the search array (Radar spins).
    pr = a.pivot('Part_radar', (0, -1.0, 18.39))
    k.lathe(a.part('Radar_mast', 'Steel', pr), [(.6, -1.1), (.6, -.9), (.45, -.7), (.3, 2.4), (.4, 2.6), (.4, 2.9)],
            loc=(0, .5, 0), seg=12)
    a.part('Mast_platform', 'Armor', pr).box((1.8, 1.6, .12), loc=(0, .5, -.95), bevel=.02)
    a.part('Yard', 'Steel', pr).box((6.4, .14, .14), loc=(0, .5, 1.6), bevel=0)
    for x in (-2.9, 2.9):
        K.whip_antenna(a.part('Antennas', 'Steel', pr), (x, .5, 1.68), h=2.2, lean=0)
    for x in (-1.5, 1.5):
        a.part('Signal_lamps', 'Lamp', pr).cyl(.08, .14, loc=(x, .5, 1.55), seg=6, bevel=0)
    RN.lev_radar(a, 'Radar', (0, .5, 3.0), pr)
    for s in (-1, 1):
        K.dish(a.part('Dishes', 'Medical', pr), a.part('Dishes', 'Steel', pr), (s * 1.0, .5, .9), r=.42,
               normal=(s * .2, -1, .2), seg=12)
    K.beacon(a, (0, -1.0, 21.95), r=.12)
    K.tone(a, 'Part_radar', k=.9)
    # APS launch clusters on the tower's 13.1 platform (Mount_APS at their centre).
    aps = a.pivot('Mount_APS', (0, -3.0, 13.15))
    for s in (-1, 1):
        for y in (-.6, 2.6):
            K.chamfer_box(a.part('Aps_launchers', 'Armor', aps), (.55, .5, .42), loc=(s * 3.45, y, .27), c=.04)
            for j in range(3):
                a.part('Aps_tubes', 'Undercarriage', aps).cyl(.07, .04, loc=(s * 3.45 - .17 + j * .17, y - .26, .3),
                                                              rot=K.FORWARD, seg=6, bevel=0)
    # Part_vls (R1): four Mk 143 armoured box launchers either side of the funnel, the outer two raised.
    pv = a.pivot('Part_vls', (0, 5.6, 7.49))
    RN.lev_abl(a, 'Part_vls', [(2.35, 0, False), (3.45, 0, True), (-2.35, 0, False), (-3.45, 0, True)], DH_Z - 7.49)
    K.tone(a, 'Part_vls', k=.88)
    # Part_engine: the raked funnel with its cap, the grille, the steam pipes and the searchlight platform.
    pe = a.pivot('Part_engine', (0, 7.0, 7.49))
    fn = [(-1.4, -2.2), (1.4, -2.2), (1.75, -1.4), (1.75, 1.8), (1.2, 2.4), (-1.2, 2.4), (-1.75, 1.8), (-1.75, -1.4)]
    k.extrude(a.part('Funnel', 'Team', pe), fn, 7.6, loc=(0, .3, 2.55), rot=(-.12, 0, 0), axis='Z', chamfer=.06,
              taper=(.9, .9))
    k.extrude(a.part('Funnel_cap', 'Charred', pe), [(x * .82, y * .82) for x, y in fn], .55, loc=(0, 1.25, 6.45),
              rot=(-.12, 0, 0), axis='Z')
    gr = a.part('Funnel_grille', 'Steel', pe)
    for i in range(6):
        gr.box((2.6, .05, .05), loc=(0, -.25 + i * .52 + .95, 6.78), rot=(-.12, 0, 0), bevel=0)
    a.part('Funnel_bands', 'Team', pe).box((3.25, 4.45, .3), loc=(0, .95, 5.0), rot=(-.12, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Steam_pipes', 'Steel', pe).tube([(s * 1.2, 2.4, -1.2), (s * 1.25, 2.55, 3.0), (s * 1.0, 3.2, 6.9)],
                                                .1, seg=6)
    a.part('Funnel_platform', 'Armor', pe).box((4.6, 3.4, .1), loc=(0, -3.4, 2.25), bevel=.02)
    for s in (-1, 1):
        searchlight(a, (s * 1.7, 3.8, 9.79), facing=(s * .4, -1, 0), r=.3, parent=None)
    K.soot(a, (0, 8.1, 14.3), radius=2.6, k=.55)
    # The mainmast (tripod) with its yard, the whips and the stern light.
    mm = a.part('Mainmast', 'Steel')
    for leg in ((0, 9.8), (-1.3, 12.0), (1.3, 12.0)):
        mm.tube([(leg[0], leg[1], DH_Z), (0, 10.6, 14.6)], .14, seg=6)
    mm.box((6.0, .18, .18), loc=(0, 10.6, 13.7), bevel=0)
    mm.box((3.4, .14, .14), loc=(0, 10.6, 12.3), bevel=0)
    for x in (-2.8, 2.8):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, 10.6, 13.8), h=2.0, lean=0)
    K.beacon(a, (0, 10.6, 14.6), r=.1)
    # Boats in their davits (both sides), the boat crane.
    for s in (-1, 1):
        K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Canvas'), (s * 3.45, 10.2, DH_Z + .35), length=4.6,
               beam=1.7)
        for y in (8.6, 11.8):
            a.part('Davits', 'Steel').tube([(s * 2.3, y, DH_Z), (s * 2.3, y, 7.9), (s * 3.45, y, 8.1)], .08, seg=6)
    # The after 127 mm on the deckhouse roof (Part_mg.001), the SAM launcher opposite (Mount_missile).
    RN.lev_sam(a, (-2.4, 14.8, DH_Z))
    # Life rafts along the deckhouse roof edge.
    for s in (-1, 1):
        liferaft_rack(a, (s * 4.3, 2.6, DH_Z), n=3, axis='Y', r=.28, length=1.0)


def _lev_guns(a):
    # R1: Leviathan's own guns (mb_pt14_r1_naval): the Mk 7 triples, the 155 mm triples in their wells, the twin
    # 5"/38 mounts with a Phalanx, the Type 96 triple 25 mm on the sponsons.
    RN.lev_main_turret(a, 0, (0, -21.4, 4.49), 5.09)
    RN.lev_main_turret(a, 1, (0, -13.0, 4.19), 6.79, barbette_base=.0)
    RN.lev_main_turret(a, 2, (0, 25.6, 3.73), 4.43)
    for i, pname, loc, mz, base in ((3, 'Part_sec_f', LEV_SEC_F, 9.59, DH_Z - LEV_SEC_F[2] - .02),
                                    (4, 'Part_sec_a', (0, 19.8, 3.8), 6.8, -.05)):
        a.pivot(pname, loc)
        _well(a, pname, f'_{i:03d}', 2.0, 2.05, mz - loc[2], base, 'Sec')
        RN.lev_sec_turret(a, i, pname, loc, mz)
    # The 127 mm mounts (mounts 5, 6): Part_mg on the forward tier's right wing, Part_mg.001 aft on the deckhouse,
    # a Phalanx beside the forward one (the APS's guns).
    p = a.pivot('Part_mg', (-3.4, -3.4, 9.27))
    RN.lev_dp_twin(a, 'Mount_mg', 'Muzzle_mg', (0, 0, .05), p, '')
    RN.lev_ciws(a, (-.9, 2.6, .05), parent=p, s=.85)
    K.tone(a, 'Part_mg', k=.9)
    p = a.pivot('Part_mg__001', LEV_MG1)
    RN.lev_dp_twin(a, 'Mount_mg__001', 'Muzzle_mg__001', (0, 0, .02), p, '_001')
    K.tone(a, 'Part_mg__001', k=.9)
    # The AA sponsons along both sides (Part_aa_l with Mount_mg.002 - .005, Part_aa_r with .006 - .009).
    for pname, s, first in (('Part_aa_l', 1, 2), ('Part_aa_r', -1, 6)):
        p = a.pivot(pname, (s * 6.1, 4.5, 3.96))
        side = '_l' if s > 0 else '_r'
        k.block(a.part('Aa_sponson' + side, 'Armor', p), (2.5, 21.0, .2), loc=(s * .1, 0, .1), chamfer=.03)
        k.block(a.part('Aa_shield' + side, 'Team', p), (.12, 21.0, .85), loc=(s * 1.25, 0, .5), chamfer=.02)
        for y in (-9.5, -2.4, 4.0, 9.8):
            a.part('Aa_lockers' + side, 'Crate', p).box((.7, .9, .55), loc=(s * -.75, y, .48), bevel=.03)
        for j in range(8):
            a.part('Aa_braces' + side, 'Steel', p).limb((s * -1.05, -9.5 + j * 2.7, -.9), (s * 1.0, -9.5 + j * 2.7, .02),
                                                       .1, .1, bevel=0)
        for j, y in enumerate((-5.0, 0.0, 8.0, 13.0)):
            i = first + j
            RN.lev_aa25(a, K.name('Mount_mg', i), K.name('Muzzle_mg', i), (s * .2, y - 4.5, .55), p, f'_{i:03d}')
        K.tone(a, pname, k=.92)


def _lev_aft(a):
    """The flight deck (Part_deck) with its markings, nets, lights and a parked helicopter; the stern gate of the well
    deck (Part_welldeck), the ensign staff, the stern lights."""
    pd = a.pivot('Part_deck', (0, 36.0, 3.57))
    a.part('Flight_deck', 'Asphalt', pd).box((12.6, 11.0, .1), loc=(0, .5, .07), bevel=0)
    mk = a.part('Deck_markings', 'PlasterWhite', pd)
    k.ring(mk, [(2.4, 0), (2.7, 0), (2.7, .02), (2.4, .02)], loc=(0, .5, .12), seg=28)
    for x in (-.9, .9):
        mk.box((.4, 2.6, .02), loc=(x, .5, .13), bevel=0)
    mk.box((1.4, .4, .02), loc=(0, .5, .13), bevel=0)
    for s in (-1, 1):
        mk.box((.15, 10.0, .02), loc=(s * 5.9, .5, .13), bevel=0)
        a.part('Deck_nets', 'Steel', pd).box((.6, 10.6, .05), loc=(s * 6.6, .5, -.08), rot=(0, s * .3, 0), bevel=0)
        for y in (-4.0, -1.0, 2.0, 5.0):
            a.part('Deck_lights', 'Lamp', pd).cyl(.08, .06, loc=(s * 6.1, y, .14), seg=6, bevel=0)
    a.part('Team_band', 'Team', pd).box((12.6, .3, .03), loc=(0, -4.9, .13), bevel=0)
    _helicopter(a, (1.4, 1.6, .12), pd, yaw=.5, s=1.15)
    K.tone(a, 'Part_deck', k=.9)
    pw = a.pivot('Part_welldeck', (0, 42.75, 1.9))
    k.block(a.part('Stern_gate', 'Armor', pw), (6.0, .3, 3.0), loc=(0, 1.15, -.25), chamfer=.04)
    for x in (-2.0, 2.0):
        a.part('Gate_hinges', 'Steel', pw).cyl(.15, .5, loc=(x, 1.25, -1.6), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Gate_frame', 'Hazard', pw).box((6.4, .1, .2), loc=(0, 1.35, 1.25), bevel=0)
    a.part('Ensign_staff', 'Steel', pw).cyl(.05, 3.0, loc=(0, 1.0, 3.2), seg=6, bevel=0)
    a.part('Ensign', 'Team', pw).box((.02, 1.2, .8), loc=(0, 1.6, 4.2), bevel=0)
    for x in (-2.6, 2.6):
        a.part('Stern_lights', 'Lamp', pw).cyl(.1, .08, loc=(x, 1.33, 1.0), rot=(R90, 0, 0), seg=8, bevel=0)
    K.tone(a, 'Part_welldeck', k=.9)
    # The crane at the stern quarter, the accommodation ladder down the right side.
    cr = a.part('Crane', 'CraneYellow')
    cr.cyl(.45, 2.4, loc=(-6.0, 30.4, LEV_H.deck_z(30.4) + 1.2), seg=10, bevel=0)
    cr.limb((-6.0, 30.4, 5.9), (-8.0, 34.6, 7.3), .35, .45, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(-8.0, 34.6, 7.2), (-8.0, 34.6, 4.9)], .04, seg=4)
    a.part('Crane_hook', 'Steel').box((.4, .4, .5), loc=(-8.0, 34.6, 4.7), bevel=0)
    lad = a.part('Accommodation_ladder', 'Steel')
    lad.tube([(-8.25, -8.0, 4.0), (-8.35, -12.5, .6)], .06, seg=4)
    lad.tube([(-8.75, -8.0, 4.0), (-8.85, -12.5, .6)], .06, seg=4)
    for j in range(8):
        f = (j + .5) / 8
        lad.box((.5, .25, .04), loc=(-8.5 - .1 * f, -8.0 - 4.5 * f, 4.0 - 3.4 * f), bevel=0)
    lad.box((.9, 1.2, .1), loc=(-8.55, -13.1, .55), bevel=0)


def _helicopter(a, loc, parent, yaw=0.0, s=1.0, tag=''):
    """A parked naval helicopter (Ka-27 read: coaxial rotors folded back, the twin tail fins)."""
    x, y, z = loc
    c, sn = math.cos(yaw), math.sin(yaw)

    def at(px, py, pz):
        return (x + (px * c - py * sn) * s, y + (px * sn + py * c) * s, z + pz * s)
    body = a.part('Heli_body' + tag, 'Team', parent)
    rings = []
    for py, w, h0, h1 in ((-2.4, .25, .45, 1.05), (-1.9, .6, .2, 1.5), (-.6, .75, .15, 1.75), (1.4, .75, .15, 1.75),
                          (2.4, .45, .35, 1.4), (5.6, .14, .9, 1.25)):
        rings.append([at(-w, py, h0), at(w, py, h0), at(w, py, h1), at(-w, py, h1)])
    body.loft(rings, bevel=0)
    a.part('Heli_glass' + tag, 'Glass', parent).loft([[at(-.55, -2.05, .9), at(.55, -2.05, .9), at(.55, -1.6, 1.55),
                                                       at(-.55, -1.6, 1.55)],
                                                      [at(-.6, -1.4, .9), at(.6, -1.4, .9), at(.6, -1.3, 1.6),
                                                       at(-.6, -1.3, 1.6)]], bevel=0)
    fins = a.part('Heli_fins' + tag, 'Armor', parent)
    fins.box((2.4 * s, .3 * s, .06 * s), loc=at(0, 5.5, 1.2), rot=(0, 0, yaw), bevel=0)
    for sx in (-1, 1):
        fins.box((.06 * s, .7 * s, 1.0 * s), loc=at(sx * 1.2, 5.5, 1.5), rot=(0, 0, yaw), bevel=0)
        a.part('Heli_wheels' + tag, 'Rubber', parent).cyl(.18 * s, .14 * s, loc=at(sx * .8, .6, .18),
                                                          rot=(0, R90, yaw), seg=8, bevel=0)
    hub = at(0, -.2, 1.9)
    a.part('Heli_hub' + tag, 'Steel', parent).cyl(.18 * s, .9 * s, loc=(hub[0], hub[1], hub[2] + .3 * s), seg=8,
                                                 bevel=0)
    bl = a.part('Heli_blades' + tag, 'Undercarriage', parent)
    # Folded for stowage: both rotors' blades swung back along the tail boom, drooping a little.
    for dz, off in ((.28, -.05), (.62, .05)):
        for b in (-1, 0, 1):
            u = yaw + R90 + off + b * .07
            tip = (hub[0] + math.cos(u) * 5.4 * s, hub[1] + math.sin(u) * 5.4 * s, hub[2] + (dz - .25) * s)
            bl.limb((hub[0], hub[1], hub[2] + dz * s), tip, .1 * s, .26 * s, bevel=0)


def leviathan(a):
    """Leviathan (see the module docstring). Runtime: Part_gun / .001 / .002 > Mount_gun / .001 / .002 (triple 406 mm,
    Gun_barrels* / Gun_muzzles* on the mount pivots for the kick, Muzzle_gun* and per-barrel muzzles), Part_sec_f /
    Part_sec_a > Mount_gun.003 / .004 (triple 155 mm in their hull wells, Sec_barrels* / Sec_muzzles*), Part_mg /
    .001 > Mount_mg / .001 (127 mm, Dp_barrels*), Part_aa_l / _r > Mount_mg.002 - .009, Mount_missile >
    Muzzle_missile (the SAM), Part_vls, Part_radar > Radar, Part_deck, Part_welldeck, Part_engine, Mount_APS,
    Point_fire, Point_exhaust."""
    K.suffixed(a)
    _lev_hull(a)
    _lev_deck(a)
    _lev_superstructure(a)
    _lev_guns(a)
    _lev_aft(a)
    a.pivot('Point_fire', (0, 4.0, 8.0))
    a.pivot('Point_exhaust', (0, 7.0, 14.0))
    # R1: the bespoke guns added parts; fold same-material static parts per pivot into one renderer each (boss_l
    # cap 299), keeping the gate's roles and every mount's kick parts.
    W.merge_static(a, keep=LEV_KEEP)
    k.clean(a)


# ============================================================================= kraken
# (y, waterline half beam, deck half beam, deck z, keel depth, fullness); the main deck: the forecastle forward, the
# hangar deck amidships (the hangar block and the flight deck stand on it), the quarterdeck aft one level down.
KR = [(-55.0, .04, .15, 7.9, .8, 1.0), (-54.0, .14, 1.1, 7.8, 2.0, 1.1), (-52.0, .7, 2.6, 7.62, 2.9, 1.3),
      (-48.0, 2.2, 4.3, 7.4, 3.0, 1.6), (-43.0, 3.9, 5.6, 7.2, 3.0, 1.9), (-36.0, 5.6, 6.8, 7.05, 3.0, 2.4),
      (-28.0, 6.9, 7.6, 7.0, 3.0, 2.9), (-18.0, 7.7, 8.1, 7.0, 3.0, 3.4), (-6.0, 8.0, 8.3, 7.0, 3.0, 3.8),
      (8.0, 8.05, 8.3, 7.0, 3.0, 3.8), (22.0, 7.9, 8.2, 7.0, 3.0, 3.5), (34.0, 7.4, 7.95, 7.0, 2.8, 2.9),
      (38.5, 7.0, 7.7, 7.0, 2.5, 2.5), (40.5, 6.8, 7.55, 5.3, 2.3, 2.3), (46.0, 6.2, 7.2, 5.3, 1.8, 2.0),
      (51.0, 5.6, 6.8, 5.3, 1.4, 1.8), (54.8, 5.2, 6.5, 5.3, 1.1, 1.7)]
KR_H = Hull(KR, flare=1.3)
KR_FD = 9.0                     # the flight deck
KR_QD = 5.3                     # the quarterdeck
KR_ISL = -7.3                   # the island's centre line (starboard)
# The flight deck outline (x, y), counter-clockwise from the forward starboard corner: the angled deck to port.
KR_DECK = [(-3.2, -18.0), (6.4, -18.0), (9.4, -6.0), (9.4, 26.0), (8.8, 41.0), (-8.4, 41.0), (-8.8, 20.0),
           (-8.8, -5.0), (-6.0, -14.0)]


def _kr_hull(a):
    H = KR_H
    H.build(a, under='Undercarriage', boot='Charred', top='Armor')
    seams = a.part('Hull_seams', 'Armor')
    for z in (1.6, 3.4, 5.2):
        H.line(seams, z, -51.0 if z < 5 else -50.0, 53.5 if z < 5 else 38.0, out=.012, r=.02, step=2.5)
    for y in range(-48, 54, 5):
        zt = H.deck_z(y) - .3
        for s in (-1, 1):
            seams.tube([(s * (H.hb(y, z) + .012), y, z) for z in (.7, (zt + .7) / 2, zt)], .015, seg=3)
    H.line(a.part('Rubbing_strake', 'Steel'), 2.6, -50.0, 54.0, out=.05, r=.07, step=2.0)
    for s in (-1, 1):
        K.portholes(a, [(s * (H.hb(y, 4.3) + .005), y, 4.3) for y in range(-49, -20, 2)], (s, 0, 0), r=.16)
        K.portholes(a, [(s * (H.hb(y, 2.2) + .005), y, 2.2) for y in range(-46, 52, 3)], (s, 0, 0), r=.14)
    marks = a.part('Draft_marks', 'PlasterWhite')
    for y in (-52.5, 53.5):
        for s in (-1, 1):
            for z in (-1.0, -.4, .2, .8, 1.4, 2.0):
                marks.box((.02, .4, .09), loc=(s * (H.hb(y, z) + .02), y, z), bevel=0)
    # The bulbous bow's sonar dome, the bilge keels, four screws and two rudders.
    k.lathe(a.part('Sonar_dome', 'Undercarriage'), [(0, 0), (.9, .3), (1.3, 1.6), (1.3, 3.6), (0, 4.4)],
            loc=(0, -51.2, -2.1), rot=K.FORWARD, seg=14)
    bk = a.part('Bilge_keels', 'Undercarriage')
    for s in (-1, 1):
        bk.tube([(s * (H.hb(y, -2.6) + .12), y, -2.65) for y in range(-20, 30, 3)], .1, seg=4)
    screws = a.part('Screws', 'Gilded')
    shafts = a.part('Shafts', 'Steel')
    for x, y, r in ((2.2, 47.0, .8), (-2.2, 47.0, .8), (5.0, 42.5, .7), (-5.0, 42.5, .7)):
        zc = under_z(H, y, x) - r - .12
        shafts.tube([(x * .6, y - 12.0, under_z(H, y - 12.0, x * .6) + .25), (x, y - .4, zc)], .17, seg=8)
        shafts.limb((x, y - 1.5, zc), (x * .85, y - 1.7, under_z(H, y - 1.7, x * .85) + .2), .14, .34, bevel=0)
        k.lathe(screws, [(0, -.34), (.27, -.3), (.27, .25), (0, .38)], loc=(x, y, zc), rot=(-R90, 0, 0), seg=10)
        for j in range(4):
            u = j * R90 + .7
            screws.box((.08, .24, r * .8), loc=(x + math.cos(u) * r * .55, y + .05, zc + math.sin(u) * r * .55),
                       rot=(0, -u + R90, 0), bevel=0)
    rud = a.part('Rudders', 'Undercarriage')
    for x in (2.2, -2.2):
        zt = under_z(H, 50.0, x) + .25
        k.extrude(rud, [(49.2, zt), (51.6, zt), (51.6, zt - 2.4), (49.5, zt - 2.55)], .3, loc=(x, 0, 0), axis='X',
                  chamfer=.04)


def _kr_forecastle(a):
    """The forecastle: the steel deck with its anti-skid panels, the breakwater, the anchor gear, the jackstaff, the
    rails, bollards and fairleads; the VLS between turret B and the flight deck (Part_vls)."""
    H = KR_H
    H.deck(a, 'Deck', 'Asphalt', -54.2, -17.6, inset=.2, t=.06, step=1.5)
    pan = a.part('Deck_panels', 'Armor')
    for y in range(-50, -18, 4):
        for x in (-3.6, 0.0, 3.6):
            if abs(x) + 1.7 < H.deck_half(y) - .4:
                pan.box((3.2, 3.6, .02), loc=(x, y, H.deck_z(y) + .1), bevel=0)
    ww = a.part('Waterways', 'Steel')
    for s in (-1, 1):
        ww.tube([(s * (H.deck_half(y) - .12), y, H.deck_z(y) + .07) for y in range(-54, -17, 2)], .07, seg=4)
    bw = a.part('Breakwater', 'Armor')
    for s in (-1, 1):
        y0, y1 = -46.0, -43.0
        ym = (y0 + y1) / 2
        bw.box((math.hypot(4.2, y1 - y0), .1, 1.1), loc=(s * 2.1, ym, H.deck_z(ym) + .6),
               rot=(0, 0, s * math.atan2(y1 - y0, 4.2)), bevel=.02)
    ag = a.part('Anchors', 'Steel')
    ch = a.part('Chain', 'Undercarriage')
    cap = a.part('Winch', 'Steel')
    for s in (-1, 1):
        y = -50.5
        xo = H.hb(y, 5.0)
        ag.cyl(.5, .35, loc=(s * (xo + .1), y, 5.0), rot=(0, s * R90, 0), seg=12, bevel=.03)
        ag.box((.24, .55, 1.6), loc=(s * (xo + .27), y, 4.25), bevel=.03)
        ag.box((.2, 1.3, .28), loc=(s * (xo + .27), y, 3.45), bevel=.03)
        zz = H.deck_z(-47.0) + .1
        ch.tube([(s * 2.2, -50.2, H.deck_z(-50.2) + .12), (s * 1.8, -48.2, zz), (s * 1.6, -47.0, zz)], .13, seg=4)
        k.lathe(cap, [(.6, 0), (.6, .45), (.42, .55), (.42, .85), (.55, .95), (0, 1.0)], loc=(s * 1.6, -46.5, zz),
                seg=14)
    a.part('Jackstaff', 'Steel').cyl(.06, 2.8, loc=(0, -54.4, H.deck_z(-54.4) + 1.4), seg=6, bevel=0)
    a.part('Ensign', 'Team').box((.02, 1.0, .65), loc=(0, -54.1, H.deck_z(-54.4) + 2.5), bevel=0)
    fit = a.part('Fittings', 'Steel')
    for y in (-48.5, -40.0, -24.0):
        for s in (-1, 1):
            hb = H.deck_half(y)
            bollard_pair(fit, (s * (hb - 1.0), y, H.deck_z(y) + .09), r=.18, gap=.55)
            fairlead(fit, (s * (hb - .35), y + 1.4, H.deck_z(y) + .09), s, w=.9)
    rails = a.part('Railings', 'Steel')
    for s in (-1, 1):
        ys = [-53.6 + i * (35.0 / 10) for i in range(11)]
        K.railing(rails, [(s * (H.deck_half(y) - .25), y, H.deck_z(y) + .09) for y in ys], h=1.0, post=2.0, r=.022)
    v = a.part('Vents', 'Steel')
    for x, y in ((-4.2, -36.0), (4.2, -36.0), (-5.6, -22.5), (5.6, -22.5)):
        vent(v, (x, y, H.deck_z(y) + .08), r=.32, h=1.2)
    for y in (-44.5, -35.5):
        liferaft_rack(a, (-(H.deck_half(y) - 1.2), y, H.deck_z(y) + .09), n=3, axis='X', r=.32, length=1.2)
        liferaft_rack(a, ((H.deck_half(y) - 1.2), y, H.deck_z(y) + .09), n=3, axis='X', r=.32, length=1.2)
    pv = a.pivot('Part_vls', (0, -21.2, 7.05))
    k.block(a.part('Vls_coaming', 'Armor', pv), (6.4, 3.0, .26), loc=(0, 0, .1), chamfer=.04)
    K.vls(a, (0, 0, .3), 8, 4, cell=.68, parent=pv)
    a.part('Vls_band', 'BarrelRed', pv).box((6.0, .14, .02), loc=(0, -1.48, .36), bevel=0)
    K.tone(a, 'Part_vls', k=.88)


def _kr_hangar(a):
    """The hangar block on the main deck from the forecastle to the quarterdeck, flush with the hull sides: its
    plated walls, the hangar side doors, the boat bay, the flight deck plate over it (overhanging to port), the
    deck-edge catwalks with their nets, the three lifts, the markings, the arresting gear on Part_deck."""
    H = KR_H
    y0, y1 = -17.6, 41.0
    outline = H.deck_outline(y0, y1, inset=0.0, step=2.0)
    hg = a.part('Hangar', 'Armor')
    base = set(hg.bm.verts)
    hh = KR_FD - 7.0 - .25
    k.extrude(hg, outline, hh, axis='Z')
    for vv in hg.bm.verts:
        if vv not in base:
            vv.co.z += 7.0 + hh / 2 - .02
    k.inset(hg, lambda c, n, f: abs(n.z) < .3, width=.15, depth=-.03)
    for s in (-1, 1):
        for yy in (2.0, 16.0):
            hb = H.hb(yy, 7.8)
            a.part('Hangar_doors', 'Undercarriage').box((.06, 7.0, 1.55), loc=(s * (hb + .02), yy, 7.85), bevel=0)
            a.part('Door_rails', 'Steel').box((.1, 8.0, .08), loc=(s * (hb + .05), yy, 8.66), bevel=0)
            for j in range(6):
                a.part('Door_slats', 'Steel').box((.04, .05, 1.5), loc=(s * (hb + .06), yy - 3.0 + j * 1.2, 7.85),
                                                  bevel=0)
    # The hangar's after wall over the quarterdeck: the boat bay with its RHIB, the doors.
    a.part('Aft_wall', 'Armor').box((15.0, .2, KR_FD - KR_QD), loc=(0, 41.1, (KR_FD + KR_QD) / 2), bevel=.03)
    for s in (-1, 1):
        K.door(a, (s * 5.2, 41.21, KR_QD + .05), size=(1.0, 2.0), normal=(0, 1, 0), mat='Armor', frame_mat='Steel')
    a.part('Boat_bay', 'Undercarriage').box((5.2, .1, 2.2), loc=(0, 41.22, KR_QD + 1.3), bevel=0)
    # The flight deck plate with its rounded corners.
    fd = a.part('Flight_deck', 'Asphalt')
    k.extrude(fd, KR_DECK, .32, loc=(0, 0, KR_FD - .16), axis='Z', chamfer=.06, corner=.4)
    mk = a.part('Deck_markings', 'PlasterWhite')
    yl = a.part('Deck_lines', 'Hazard')
    # The axial take-off line, the angled landing area's edge and centre lines, the deck edge lines.
    for y in range(-14, 38, 4):
        mk.box((.3, 2.2, .02), loc=(-2.5, y, KR_FD + .17), bevel=0)
    ang = math.radians(8.0)
    for off, w_ in ((0.0, .3), (-4.3, .18), (4.3, .18)):
        for j in range(12):
            py = 39.0 - j / 11 * 52.0
            px = 3.4 + off + (39.0 - py) * math.tan(ang) * .35
            if -9.0 < px < 9.8 and (off or j % 2 == 0):
                (mk if off else yl).box((w_, 3.6 if off else 2.4, .02), loc=(px, py, KR_FD + .17),
                                        rot=(0, 0, -ang * .35), bevel=0)
    for x in (-8.2, 9.4):
        mk.box((.16, 52.0, .02), loc=(x, 14.0, KR_FD + .17), bevel=0)
    # Three lifts (plates with their safety edges), the jet blast deflectors.
    for (x, y, w_, d_) in ((3.6, -10.5, 6.6, 5.4), (-4.6, 22.5, 5.6, 6.4), (6.2, 13.0, 5.2, 6.0)):
        a.part('Lifts', 'Armor').box((w_, d_, .04), loc=(x, y, KR_FD + .17), bevel=0)
        yl.box((w_ + .2, .12, .02), loc=(x, y - d_ / 2, KR_FD + .19), bevel=0)
        yl.box((w_ + .2, .12, .02), loc=(x, y + d_ / 2, KR_FD + .19), bevel=0)
    jbd = a.part('Blast_deflectors', 'Steel')
    for x, y in ((-2.5, -6.0), (2.6, -9.0)):
        jbd.box((3.6, .14, 1.4), loc=(x, y, KR_FD + .74), rot=(-.95, 0, 0), bevel=.02)
        for dx in (-1.2, 1.2):
            jbd.limb((x + dx, y + .7, KR_FD + .16), (x + dx, y + .2, KR_FD + .9), .1, .1, bevel=0)
    # Deck-edge catwalks and safety nets round the flight deck, the deck lights, the radio masts folded out.
    cw = a.part('Catwalks', 'Steel')
    nets = a.part('Deck_nets', 'Steel')
    lights = a.part('Deck_lights', 'Lamp')
    pts = KR_DECK + [KR_DECK[0]]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        L = math.hypot(xb - xa, yb - ya)
        if L < 3.0 or (xa < -8.5 and xb < -8.5 and -5.0 <= min(ya, yb) <= 20.0):
            continue
        u = math.atan2(yb - ya, xb - xa)
        nx_, ny_ = math.sin(u), -math.cos(u)
        mx, my = (xa + xb) / 2 + nx_ * .38, (ya + yb) / 2 + ny_ * .38
        nets.box((L * .96, .6, .04), loc=(mx, my, KR_FD - .12), rot=(0, 0, u), bevel=0)
        cw.box((L * .96, .08, .08), loc=(mx + nx_ * .3, my + ny_ * .3, KR_FD - .05), rot=(0, 0, u), bevel=0)
        n = int(L / 4)
        for j in range(n):
            t = (j + .5) / n
            lights.cyl(.07, .06, loc=(xa + (xb - xa) * t - nx_ * .3, ya + (yb - ya) * t - ny_ * .3, KR_FD + .17), seg=6,
                       bevel=0)
    for y in (-2.0, 10.0, 22.0):
        a.part('Radio_masts', 'Steel').limb((9.45, y, KR_FD - .1), (9.95, y + .3, KR_FD + 1.4), .12, .12, bevel=0)
    # Part_deck: the landing area (four arresting wires on their sheaves, the landing box one shade off) with two
    # jets parked on its edge.
    pd = a.pivot('Part_deck', (3.4, 30.0, KR_FD))
    wires = a.part('Arresting_wires', 'Steel', pd)
    for j in range(4):
        y = -2.4 + j * 1.6
        wires.tube([(-5.0, y, .2), (5.0, y + .7, .2)], .035, seg=4)
        for xx in (-5.0, 5.0):
            wires.cyl(.16, .16, loc=(xx, y + (0 if xx < 0 else .7), .24), seg=8, bevel=0)
    lb = a.part('Landing_box', 'Hazard', pd)
    lb.box((10.6, .18, .02), loc=(0, 5.6, .19), rot=(0, 0, .06), bevel=0)
    lb.box((10.6, .18, .02), loc=(0, -4.4, .19), rot=(0, 0, .06), bevel=0)
    _jet(a, (3.6, 6.6, .18), math.pi * .85, '_d', parent=pd)
    _jet(a, (.4, 7.4, .18), math.pi * .85, '_d', parent=pd)
    K.tone(a, 'Part_deck', k=.9)
    # More aircraft parked forward of the island and aft on the starboard side; a helicopter abaft the island.
    for x, y, yaw in ((-4.4, -13.6, .75), (-1.4, -15.0, .75), (5.2, 1.4, -.45), (5.2, 8.6, -.45), (-4.4, 30.6, .55),
                      (-4.0, 36.2, .55)):
        _jet(a, (x, y, KR_FD + .18), yaw, '')
    _helicopter(a, (-4.2, 16.4, KR_FD + .18), None, yaw=-.4, s=1.1, tag='_k')
    for x, y in ((-3.4, 21.6), (2.0, -2.0)):
        k.block(a.part('Tractors', 'CraneYellow'), (1.4, 2.4, .7), loc=(x, y, KR_FD + .55), chamfer=.08)
        a.part('Tractor_wheels', 'Rubber').box((1.6, 1.8, .36), loc=(x, y, KR_FD + .36), bevel=.08)


def _jet(a, loc, yaw, tag, parent=None, s=.62):
    """A parked carrier fighter (Su-33 read): the lofted fuselage, the canopy, the canards, the outer wings folded
    up, the twin fins and tailplanes, the nozzles, the intakes, the gear."""
    x, y, z = loc
    c, sn = math.cos(yaw), math.sin(yaw)

    def at(px, py, pz):
        return (x + (px * c - py * sn) * s, y + (px * sn + py * c) * s, z + pz * s)
    body = a.part('Jets' + tag, 'Armor', parent)
    rings = [[at(0, -10.0, 1.6)]]
    for py, w, z0, z1 in ((-9.2, .32, 1.35, 1.85), (-7.0, .62, 1.12, 2.15), (-4.5, .78, 1.05, 2.25),
                          (-1.0, 1.55, .95, 2.0), (3.0, 1.7, .95, 1.95), (6.4, 1.15, 1.05, 1.85), (7.6, .95, 1.1, 1.75)):
        rings.append([at(-w * .6, py, z0), at(w * .6, py, z0), at(w, py, (z0 + z1) / 2), at(w * .55, py, z1),
                      at(-w * .55, py, z1), at(-w, py, (z0 + z1) / 2)])
    body.loft(rings, bevel=0)
    a.part('Jet_canopies' + tag, 'Glass', parent).loft(
        [[at(0, -6.6, 2.15)], [at(-.36, -5.6, 2.2), at(.36, -5.6, 2.2), at(.2, -5.6, 2.62), at(-.2, -5.6, 2.62)],
         [at(-.36, -3.6, 2.22), at(.36, -3.6, 2.22), at(.2, -3.6, 2.5), at(-.2, -3.6, 2.5)], [at(0, -2.6, 2.25)]],
        bevel=0)
    wg = a.part('Jet_wings' + tag, 'Team', parent)

    def slab(pts, t=.06):
        """A thin plate through four points (both faces, so it shows from either side)."""
        lo = [(p[0], p[1], p[2] - t / 2) for p in pts]
        hi = [(p[0], p[1], p[2] + t / 2) for p in pts]
        wg.loft([lo, hi], bevel=0)
    for sx in (-1, 1):
        # The wing (spread: the battle camera reads a fighter by its planform), the canard, the tailplane, the fin.
        slab([at(sx * 1.4, -3.6, 1.5), at(sx * 6.2, 2.6, 1.42), at(sx * 6.2, 3.7, 1.42), at(sx * 1.6, 4.4, 1.5)])
        slab([at(sx * .9, -5.0, 1.75), at(sx * 2.4, -3.9, 1.75), at(sx * 2.4, -3.3, 1.75), at(sx * .9, -3.5, 1.75)],
             t=.05)
        slab([at(sx * 1.1, 5.2, 1.45), at(sx * 3.5, 7.0, 1.45), at(sx * 3.5, 8.0, 1.45), at(sx * 1.1, 7.6, 1.45)],
             t=.05)
        q = [at(sx * .75, 4.0, 1.95), at(sx * 1.05, 6.6, 3.9), at(sx * 1.05, 7.7, 3.9), at(sx * .75, 7.6, 1.85)]
        off = (c * sx * .035 * s, sn * sx * .035 * s, 0)
        wg.loft([[(p[0] - off[0], p[1] - off[1], p[2]) for p in q], [(p[0] + off[0], p[1] + off[1], p[2]) for p in q]],
                bevel=0)
        k.lathe(a.part('Jet_nozzles' + tag, 'Charred', parent), [(.42 * s, 0), (.4 * s, .7 * s), (.34 * s, .75 * s)],
                loc=at(sx * .5, 7.5, 1.45), rot=(-R90, 0, yaw), seg=8)
        a.part('Jet_intakes' + tag, 'Undercarriage', parent).box((.6 * s, .1, .55 * s), loc=at(sx * .78, -1.3, .95),
                                                                 rot=(0, 0, yaw), bevel=0)
    gear = a.part('Jet_gear' + tag, 'Rubber', parent)
    for px, py in ((0, -6.6), (-1.4, 1.4), (1.4, 1.4)):
        gear.cyl(.3 * s, .22 * s, loc=at(px, py, .3), rot=(0, R90, yaw), seg=8, bevel=0)
        a.part('Jet_struts' + tag, 'Steel', parent).cyl(.07 * s, .7 * s, loc=at(px, py, .75), seg=5, bevel=0)


def _kr_island(a):
    """The island to starboard: the stepped blocks with the bridge and flight-control window bands, the fixed array
    faces (the APS's eyes, Mount_APS), the mast with the spinning search radar (Part_radar > Radar), the funnel
    (Part_engine), the platforms, rails, ladders, whips, the SAM launcher aft (Mount_missile)."""
    x0 = KR_ISL
    isl = a.part('Island', 'Team')
    rails = a.part('Railings', 'Steel')
    for (y0, y1, za, zb, w0, w1) in ((-6.0, 14.0, KR_FD, 12.6, 3.3, 3.1), (-4.6, 9.6, 12.6, 15.0, 2.9, 2.7),
                                     (-3.4, 3.8, 15.0, 17.0, 2.5, 2.3)):
        rings = [[(x0 - w0 / 2, y0, za), (x0 + w0 / 2, y0, za), (x0 + w0 / 2, y1, za), (x0 - w0 / 2, y1, za)],
                 [(x0 - w1 / 2, y0 + .25, zb), (x0 + w1 / 2, y0 + .25, zb), (x0 + w1 / 2, y1, zb),
                  (x0 - w1 / 2, y1, zb)]]
        k.sharp_loft(isl, rings, chamfer=.08)
        a.part('Island_decks', 'Armor').box((w0 + .9, y1 - y0 + .8, .1), loc=(x0, (y0 + y1) / 2, zb + .05), bevel=.02)
        hw_ = w0 / 2 + .35
        K.railing(rails, [(x0 - hw_, y0 - .3, zb + .1), (x0 + hw_, y0 - .3, zb + .1), (x0 + hw_, y1 + .3, zb + .1),
                          (x0 - hw_, y1 + .3, zb + .1), (x0 - hw_, y0 - .3, zb + .1)], h=.9, post=1.2, r=.02)
    k.inset(isl, lambda c, n, f: abs(n.z) < .3, width=.14, depth=-.03)
    glass = a.part('Windows', 'Glass')
    for z, y, n in ((14.2, -4.62, 6), (16.2, -3.42, 5), (11.2, -6.02, 6)):
        for i in range(n):
            glass.box((.42, .05, .5 if z > 12 else .4), loc=(x0 - (n - 1) * .25 + i * .5, y, z), rot=(-.12, 0, 0),
                      bevel=0)
    for side in (-1, 1):
        for i in range(8):
            glass.box((.05, .8, .45), loc=(x0 + side * 1.4, -3.8 + i * 1.6, 14.0), bevel=0)
        for y in (-4.6, -2.4, 9.0, 11.6):
            glass.box((.05, .5, .4), loc=(x0 + side * 1.6, y, 11.0), bevel=0)
        ribs = a.part('Island_ribs', 'Armor')
        for y in range(-5, 14, 2):
            ribs.box((.08, .12, 3.4), loc=(x0 + side * 1.62, y + .5, 10.8), rot=(0, side * -.03, 0), bevel=0)
        K.door(a, (x0 + side * 1.62, 4.0, KR_FD + .02), size=(.9, 1.9), normal=(side, 0, 0), mat='Armor',
               frame_mat='Steel')
    # Primary flight control: the glazed bay hung on the island's port face, over the deck.
    pf = a.part('Prifly', 'Team')
    k.block(pf, (1.4, 4.6, 1.6), loc=(x0 + 2.05, 4.4, 14.0), chamfer=.06, taper=(1.3, 1.0))
    glass.box((.05, 4.2, .8), loc=(x0 + 2.82, 4.4, 14.3), rot=(0, .35, 0), bevel=0)
    for dy in (-1.8, 1.8):
        a.part('Prifly_braces', 'Steel').limb((x0 + 1.6, 4.4 + dy, 12.7), (x0 + 2.5, 4.4 + dy, 13.25), .12, .12,
                                              bevel=0)
    K.ladder(a.part('Ladders', 'Steel'), (x0 + 1.75, 12.5, KR_FD), (x0 + 1.75, 12.5, 12.6), width=.5, step=.3,
             facing=(1, 0))
    faces = a.part('Array_faces', 'Undercarriage')
    rims = a.part('Array_rims', 'Steel')
    for nx_, ny_, ly in ((0, -1, -3.55), (1, 0, .2), (-1, 0, .2), (0, 1, 3.85)):
        loc = (x0 + nx_ * 1.17, ly, 15.9)
        faces.box((1.7, 1.7, .06), loc=loc, rot=K.rot_to((nx_, ny_, .22)), bevel=0)
        rims.box((1.85, 1.85, .03), loc=(loc[0] - nx_ * .03, loc[1] - ny_ * .03, loc[2]),
                 rot=K.rot_to((nx_, ny_, .22)), bevel=0)
    a.pivot('Mount_APS', (x0, -1.5, 16.6))
    # The mast with the yard, the whips, the spinning radar (Part_radar > Radar).
    pr = a.pivot('Part_radar', (x0, 0.0, 17.05))
    mast = a.part('Mast', 'Steel', pr)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mast.tube([(sx * .9, sy * .9, 0), (sx * .3, sy * .3, 2.4)], .07, seg=5)
    for zz in (.8, 1.6):
        w_ = .9 - .6 * zz / 2.4
        mast.tube([(-w_, -w_, zz), (w_, -w_, zz), (w_, w_, zz), (-w_, w_, zz), (-w_, -w_, zz)], .035, seg=4)
    mast.box((5.0, .18, .18), loc=(0, 0, 2.0), bevel=0)
    for dx in (-2.3, 2.3):
        K.whip_antenna(a.part('Antennas', 'Steel', pr), (dx, 0, 2.1), h=1.6, lean=0)
    a.part('Mast_platform', 'Armor', pr).box((1.2, 1.2, .1), loc=(0, 0, 2.45), bevel=.02)
    radar_array(a, 'Radar', (0, 0, 2.5), pr, w=4.6, h=1.05, tag='')
    K.tone(a, 'Part_radar', k=.9)
    pe = a.pivot('Part_engine', (x0, 9.6, 15.0))
    k.extrude(a.part('Funnel', 'Team', pe), [(-1.25, -2.4), (1.25, -2.4), (1.4, -1.6), (1.2, 2.6), (-1.2, 2.6),
                                             (-1.4, -1.6)], 3.2, loc=(0, .2, 1.6), axis='Z', chamfer=.06, corner=.2,
              taper=(.86, .9))
    for dy in (-1.0, .2, 1.4):
        k.lathe(a.part('Funnel_caps', 'Charred', pe), [(.46, 0), (.46, .55), (.52, .62), (.52, .72), (0, .74)],
                loc=(0, dy, 3.2), seg=10)
    a.part('Funnel_bands', 'Team', pe).box((2.5, 4.9, .3), loc=(0, .3, 2.6), bevel=0)
    K.tone(a, 'Part_engine', k=.88)
    K.soot(a, (x0, 9.6, 18.9), radius=3.0, k=.55)
    for i in range(3):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x0 + (i - 1) * 1.0, 12.8, 15.05), h=3.0, r=.07, lean=.05)
    searchlight(a, (x0 - 1.6, -4.0, 15.1), facing=(-.4, -1, 0), r=.32)
    searchlight(a, (x0 + 1.6, -4.0, 15.1), facing=(.4, -1, 0), r=.32)
    director(a, (x0, 6.2, 15.1), w=2.0, d=1.6, h=.95, tag='_k')
    # The SAM launcher on the deck-edge sponson aft of the island (Mount_missile, mount 15).
    k.block(a.part('Sam_sponson', 'Armor'), (3.2, 4.4, .3), loc=(x0 - .4, 18.6, KR_FD - .1), chamfer=.04)
    twin_arm_launcher(a, (x0 - .3, 18.6, KR_FD + .05), s=.88, tag='_k')


def _kr_guns(a):
    """Turrets A and B on the forecastle, C on the quarterdeck (Part_gun* > Mount_gun*: triple 406 mm), the two 155 mm
    triples in their side sponsons (Part_sec_f starboard forward, Part_sec_a port aft under the deck's overhang),
    the 127 mm mounts (Part_mg starboard forward, Part_mg.001 on the quarterdeck), the gun galleries
    (Part_aa_l > Mount_mg.002 - .005, Part_aa_r > .006 - .009)."""
    main = dict(w=3.35, f=-3.3, b=4.3, h=2.65, L=9.8, r=.28, gap=1.75, br=3.5, rangefinder=6.8, zg=1.28)
    triple_turret(a, 0, (0, -38.4, KR_H.deck_z(-38.4) + .05), KR_H.deck_z(-38.4) + .65, main)
    triple_turret(a, 1, (0, -28.6, 7.05), 9.85, dict(main, barbette_base=-.05))
    triple_turret(a, 2, (0, 48.4, KR_QD + .05), KR_QD + .65, main)
    sec = dict(w=1.4, f=-1.35, b=1.65, h=1.35, L=6.1, r=.105, gap=.57, br=2.05, zg=.74, prefix='Sec')
    loc = (-7.7, -17.8, 7.05)
    triple_turret(a, 3, loc, 7.65, sec, part_name='Part_sec_f')
    k.block(a.part('Sponsons', 'Armor'), (3.6, 6.0, .4), loc=(loc[0] + .3, loc[1], loc[2] - .1), chamfer=.06)
    for dy in (-2.0, 2.0):
        a.part('Sponson_braces', 'Armor').limb((-7.4, loc[1] + dy, loc[2] - 3.0), (loc[0] - .9, loc[1] + dy, loc[2] - .3),
                                               .3, .3, bevel=0)
    # The after 155 mm on the flight deck's port quarter, on its low barbette, firing aft over the round-down.
    triple_turret(a, 4, (7.2, 38.2, KR_FD + .16), KR_FD + .66, sec, part_name='Part_sec_a')
    p = a.pivot('Part_mg', (-5.4, -24.4, 7.05))
    dp_mount(a, 'Mount_mg', 'Muzzle_mg', (0, 0, .05), p, '', s=.95)
    K.tone(a, 'Part_mg', k=.9)
    p = a.pivot('Part_mg__001', (5.8, 52.2, KR_QD + .05))
    dp_mount(a, 'Mount_mg__001', 'Muzzle_mg__001', (0, 0, 0), p, '_001', s=.95)
    K.tone(a, 'Part_mg__001', k=.9)
    gatling(a, (-5.6, 52.4, KR_QD + .05), s=.9)
    gatling(a, (KR_ISL + .9, -5.5, 12.66), s=.8)
    # The gun galleries on the flight deck's edges (a raised gallery deck, the splinter shield outboard, the ammo
    # lockers inboard).
    for pname, s, first, at_ in (('Part_aa_l', 1, 2, (8.3, 10.0, KR_FD + .16)),
                                 ('Part_aa_r', -1, 6, (-7.8, 30.0, KR_FD + .16))):
        p = a.pivot(pname, at_)
        side = '_l' if s > 0 else '_r'
        k.block(a.part('Gallery' + side, 'Armor', p), (1.9, 15.0, .2), loc=(0, 0, .1), chamfer=.04)
        k.block(a.part('Gallery_shield' + side, 'Team', p), (.1, 15.0, .75), loc=(s * .92, 0, .55), chamfer=.02)
        for gy in (-7.2, -1.8, 1.8, 7.2):
            a.part('Gallery_lockers' + side, 'Crate', p).box((.5, .8, .5), loc=(-s * .62, gy, .45), bevel=.03)
        for j in range(4):
            i = first + j
            aa_triple(a, K.name('Mount_mg', i), K.name('Muzzle_mg', i), (s * .05, -5.4 + j * 3.6, .45), p,
                      f'_{i:03d}', s=1.05)
        K.tone(a, pname, k=.92)


def _kr_stern(a):
    """The quarterdeck under the round-down (the deck, its bollards and rails), the stern gate (Part_welldeck), the
    ensign staff, the stern lights."""
    H = KR_H
    H.deck(a, 'Quarterdeck', 'Asphalt', 40.6, 54.6, inset=.2, t=.06, step=1.0)
    fit = a.part('Fittings', 'Steel')
    for y in (45.0, 52.5):
        for s in (-1, 1):
            bollard_pair(fit, (s * (H.deck_half(y) - .9), y, KR_QD + .09), r=.18, gap=.55)
    rails = a.part('Railings', 'Steel')
    for s in (-1, 1):
        ys = [41.0 + i * 1.7 for i in range(9)]
        K.railing(rails, [(s * (H.deck_half(y) - .25), y, KR_QD + .09) for y in ys], h=1.0, post=1.8, r=.022)
    K.railing(rails, [(-(H.deck_half(54.6) - .3), 54.5, KR_QD + .09), ((H.deck_half(54.6) - .3), 54.5, KR_QD + .09)],
              h=1.0, post=1.8, r=.022)
    pw = a.pivot('Part_welldeck', (0, 54.75, 2.4))
    k.block(a.part('Stern_gate', 'Armor', pw), (6.4, .3, 3.2), loc=(0, .2, -.1), chamfer=.04)
    for x in (-2.2, 2.2):
        a.part('Gate_hinges', 'Steel', pw).cyl(.16, .55, loc=(x, .3, -1.6), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Gate_frame', 'Hazard', pw).box((6.8, .1, .2), loc=(0, .38, 1.55), bevel=0)
    a.part('Ensign_staff', 'Steel', pw).cyl(.05, 3.0, loc=(-3.2, .1, 4.4), seg=6, bevel=0)
    a.part('Ensign', 'Team', pw).box((.02, 1.2, .8), loc=(-3.2, .7, 5.4), bevel=0)
    for x in (-2.8, 2.8):
        a.part('Stern_lights', 'Lamp', pw).cyl(.1, .08, loc=(x, .38, .9), rot=(R90, 0, 0), seg=8, bevel=0)
    K.tone(a, 'Part_welldeck', k=.9)


def kraken(a):
    """Kraken (see the module docstring). Runtime: Part_gun / .001 / .002 > Mount_gun / .001 / .002 (triple 406 mm,
    Gun_barrels* kick parts, per-barrel muzzles), Part_sec_f / Part_sec_a > Mount_gun.003 / .004 (triple 155 mm),
    Part_mg / .001 > Mount_mg / .001 (127 mm), Part_aa_l / _r > Mount_mg.002 - .009, Mount_missile > Muzzle_missile,
    Part_vls, Part_radar > Radar, Part_engine, Part_deck, Part_welldeck, Mount_APS."""
    K.suffixed(a)
    _kr_hull(a)
    _kr_forecastle(a)
    _kr_hangar(a)
    _kr_island(a)
    _kr_guns(a)
    _kr_stern(a)
    a.pivot('Point_fire', (0, 10.0, 10.0))
    a.pivot('Point_exhaust', (KR_ISL, 9.6, 19.0))
    k.clean(a)


# ============================================================================= scylla
# Scylla is drawn at its old size (Leviathan's model at 0.56: 49.3 x 9.8 x 14.2 m), now with "modelSize" so the
# view fits this model's own length.
SC = [(-24.6, .04, .1, 3.75, .5, 1.0), (-23.8, .1, .6, 3.68, 1.1, 1.1), (-22.5, .4, 1.35, 3.55, 1.55, 1.3),
      (-20.0, 1.2, 2.4, 3.4, 1.75, 1.5), (-16.0, 2.3, 3.4, 3.22, 1.8, 1.9), (-11.0, 3.4, 4.1, 3.08, 1.8, 2.4),
      (-5.0, 4.1, 4.5, 3.0, 1.8, 2.9), (2.0, 4.3, 4.6, 2.95, 1.8, 3.1), (9.0, 4.25, 4.55, 2.92, 1.75, 2.9),
      (15.0, 4.0, 4.4, 2.9, 1.6, 2.5), (20.0, 3.6, 4.15, 2.88, 1.3, 2.0), (23.0, 3.3, 3.95, 2.86, 1.0, 1.8),
      (24.65, 3.15, 3.85, 2.85, .85, 1.7)]
SC_H = Hull(SC, flare=1.4)


def twin_turret(a, part, mount, muzzle, ploc, mz, tag, P, parent_mat='Team'):
    """A stealth-shaped twin gun turret (AK-130 read) under its part pivot: the low barbette, the faceted house on the
    yaw pivot, two barrels in their sleeves (Gun_barrels* / Gun_muzzles*, the kick parts), the sight and radar
    housing on the roof, Muzzle_* between the tips and the per-barrel muzzles."""
    p = a.pivot(part, ploc)
    lz = mz - ploc[2]
    w, f, b, h = P['w'], P['f'], P['b'], P['h']
    k.lathe(a.part('Gun_barbette' + tag, 'Armor', p), [(P['br'], -.05), (P['br'], lz - .05), (P['br'] * .95, lz)],
            seg=20)
    m = a.pivot(mount, (0, 0, lz), p)
    W.poly_turret(a.part('Gun_house' + tag, parent_mat, m), [
        (0, [(-w * .55, f), (w * .55, f), (w, f * .45), (w, b), (-w, b), (-w, f * .45)]),
        (h * .62, [(-w * .5, f * .92), (w * .5, f * .92), (w * .98, f * .42), (w * .98, b - .05), (-w * .98, b - .05),
                   (-w * .98, f * .42)]),
        (h, [(-w * .3, f * .55), (w * .3, f * .55), (w * .7, f * .2), (w * .7, b - .4), (-w * .7, b - .4),
             (-w * .7, f * .2)])], chamfer=.05)
    k.inset(a.part('Gun_house' + tag, parent_mat, m), lambda c, n, fc: abs(n.z) < .5 and c.z > .2, width=.08,
            depth=-.015)
    zg = P['zg']
    gap = P['gap']
    xs = (-gap / 2, gap / 2)
    k.block(a.part('Gun_mantlet' + tag, 'Armor', m), (gap + .7, .5, .7), loc=(0, f * .9 - .05, zg), chamfer=.06,
            ends=(True, True))
    for x in xs:
        K.gun_barrel(a, 'Gun_barrels' + tag, m, x, f * .9 - .25, zg, P['L'], P['r'], seg=12, extractor=(.3, 1.25, .5),
                     brake_name='Gun_muzzles' + tag, brake='collar')
    mzp = a.pivot(muzzle, (0, f * .9 - .25 - P['L'] - .1, zg), m)
    per_barrel(a, mzp, 'gun', xs)
    k.lathe(a.part('Gun_radome' + tag, 'PlasterWhite', m), [(.32, 0), (.34, .22), (.2, .42), (0, .48)],
            loc=(w * .32, b - .9, h - .02), seg=12)
    k.block(a.part('Gun_sight' + tag, 'Armor', m), (.4, .5, .35), loc=(-w * .35, f * .25, h + .1), chamfer=.04)
    a.part('Glass', 'Glass', m).box((.3, .02, .12), loc=(-w * .35, f * .25 - .26, h + .15), bevel=0)
    k.block(a.part('Gun_hatch' + tag, 'Armor', m), (.6, .55, .08), loc=(0, b - .7, h - .02), chamfer=.02)
    a.part('Team_band', 'Team', m).box((w * 1.4, .4, .03), loc=(0, (f + b) / 2, h - .01), bevel=0)
    return m


def _sc_hull(a):
    H = SC_H
    H.build(a, under='BarrelRed', boot='Undercarriage', top='Armor')
    seams = a.part('Hull_seams', 'Armor')
    H.line(seams, 1.0, -22.0, 24.0, out=.008, r=.014, step=1.5)
    H.line(seams, 2.0, -22.5, 24.2, out=.008, r=.014, step=1.5)
    for y in range(-21, 25, 3):
        for s in (-1, 1):
            seams.tube([(s * (H.hb(y, z) + .008), y, z) for z in (.45, 1.4, H.deck_z(y) - .15)], .011, seg=3)
    H.line(a.part('Rubbing_strake', 'Steel'), 2.45, -21.0, 24.4, out=.03, r=.04, step=1.0)
    for s in (-1, 1):
        K.portholes(a, [(s * (H.hb(y, 1.6) + .004), y, 1.6) for y in range(-20, 22, 2)], (s, 0, 0), r=.1)
        team_band_hull = a.part('Hull_band', 'Team')
        team_band_hull.tube([(s * (H.hb(y, 2.75) + .01), y, 2.75) for y in range(-22, 25, 1)], .07, seg=4)
    marks = a.part('Draft_marks', 'PlasterWhite')
    for y in (-22.6, 24.0):
        for s in (-1, 1):
            for z in (-.6, -.3, 0, .3, .6, .9):
                marks.box((.02, .22, .05), loc=(s * (H.hb(y, z) + .02), y, z), bevel=0)
    k.lathe(a.part('Sonar_dome', 'BarrelRed'), [(0, 0), (.45, .15), (.65, .8), (.65, 1.8), (0, 2.2)],
            loc=(0, -22.4, -1.15), rot=K.FORWARD, seg=12)
    screws = a.part('Screws', 'Gilded')
    for x, y in ((1.45, 20.4), (-1.45, 20.4)):
        r = .55
        zc = under_z(H, y, x) - r - .08
        a.part('Shafts', 'Steel').tube([(x * .5, y - 7.0, under_z(H, y - 7.0, x * .5) + .2), (x, y - .3, zc)], .09,
                                       seg=6)
        k.lathe(screws, [(0, -.2), (.17, -.18), (.17, .15), (0, .24)], loc=(x, y, zc), rot=(-R90, 0, 0), seg=8)
        for j in range(5):
            u = j * TAU / 5
            screws.box((.05, .15, r * .75), loc=(x + math.cos(u) * r * .5, y + .03, zc + math.sin(u) * r * .5),
                       rot=(0, -u + R90, 0), bevel=0)
        zt = under_z(H, 22.0, x) + .15
        k.extrude(a.part('Rudders', 'BarrelRed'), [(21.4, zt), (22.9, zt), (22.9, zt - 1.3), (21.6, zt - 1.4)], .16,
                  loc=(x, 0, 0), axis='X', chamfer=.03)


def _sc_deck(a):
    H = SC_H
    H.deck(a, 'Deck', 'Asphalt', -24.2, 24.5, inset=.14, t=.05, step=1.0)
    ww = a.part('Waterways', 'Steel')
    for s in (-1, 1):
        ww.tube([(s * (H.deck_half(y) - .1), y, H.deck_z(y) + .06) for y in range(-24, 25, 1)], .045, seg=4)
    rails = a.part('Railings', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-23.8, -10.5), (-10.5, 4.0), (4.0, 24.4)):
            ys = [y0 + (y1 - y0) * i / 6 for i in range(7)]
            K.railing(rails, [(s * (H.deck_half(y) - .16), y, H.deck_z(y) + .07) for y in ys], h=.8, post=1.2,
                      r=.016)
    fit = a.part('Fittings', 'Steel')
    for y in (-20.5, -12.5, 14.0, 22.5):
        for s in (-1, 1):
            hb = H.deck_half(y)
            bollard_pair(fit, (s * (hb - .55), y, H.deck_z(y) + .07), r=.1, gap=.32, h=.3)
            fairlead(fit, (s * (hb - .22), y + .7, H.deck_z(y) + .07), s, w=.5)
    ag = a.part('Anchors', 'Steel')
    for s in (-1, 1):
        y = -21.6
        xo = H.hb(y, 2.6)
        ag.cyl(.26, .2, loc=(s * (xo + .05), y, 2.6), rot=(0, s * R90, 0), seg=10, bevel=.02)
        ag.box((.12, .3, .8), loc=(s * (xo + .14), y, 2.2), bevel=.02)
        ag.box((.1, .7, .14), loc=(s * (xo + .14), y, 1.8), bevel=.02)
        a.part('Chain', 'Undercarriage').tube([(s * 1.2, -21.4, H.deck_z(-21.4) + .08), (s * .8, -19.6,
                                                                                         H.deck_z(-19.6) + .08)],
                                              .07, seg=4)
        k.lathe(a.part('Winch', 'Steel'), [(.32, 0), (.32, .25), (.22, .3), (.22, .45), (.3, .5), (0, .52)],
                loc=(s * .8, -19.2, H.deck_z(-19.2) + .05), seg=12)
    a.part('Jackstaff', 'Steel').cyl(.035, 1.6, loc=(0, -24.0, H.deck_z(-24.0) + .8), seg=6, bevel=0)
    bw = a.part('Breakwater', 'Armor')
    for s in (-1, 1):
        y0, y1 = -19.0, -17.4
        ym = (y0 + y1) / 2
        bw.box((math.hypot(2.4, y1 - y0), .06, .6), loc=(s * 1.2, ym, H.deck_z(ym) + .32),
               rot=(0, 0, s * math.atan2(y1 - y0, 2.4)), bevel=.01)


def _sc_superstructure(a):
    """The forward superstructure (the 01 level, the bridge with its wings and window band, the pyramid mast with the
    search radar on top), the angled anti-ship missile tubes along its sides (Part_vls), the twin funnels, the
    after superstructure with the fire-control dome and the SAM revolver lids, the hangar, the boats, the
    gatlings."""
    H = SC_H
    rails = a.part('Railings', 'Steel')
    ss = a.part('Superstructure', 'Team')
    lvl1 = [(-1.6, -10.8), (1.6, -10.8), (2.3, -9.6), (2.3, -1.4), (-2.3, -1.4), (-2.3, -9.6)]
    W.poly_turret(ss, [(2.95, lvl1), (5.35, [(x * .96, y + (.12 if y < -5 else 0)) for x, y in lvl1])], chamfer=.05)
    br = [(-1.3, -9.4), (1.3, -9.4), (2.0, -8.6), (2.0, -4.4), (-2.0, -4.4), (-2.0, -8.6)]
    W.poly_turret(ss, [(5.35, br), (7.3, [(x * .9, y + (.25 if y < -6 else 0)) for x, y in br])], chamfer=.05)
    k.inset(ss, lambda c, n, f: abs(n.z) < .35, width=.08, depth=-.015)
    a.part('Tier_deck', 'Armor').box((5.0, 9.8, .06), loc=(0, -6.1, 5.38), bevel=.01)
    a.part('Tier_deck', 'Armor').box((4.2, 5.4, .06), loc=(0, -6.9, 7.33), bevel=.01)
    glass = a.part('Windows', 'Glass')
    for i in range(7):
        glass.box((.3, .03, .36), loc=(-.9 + i * .3, -9.18, 6.75), rot=(-.25, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.03, 1.6, .32), loc=(s * 1.84, -7.2, 6.75), bevel=0)
        glass.box((.42, .03, .32), loc=(s * 1.65, -8.9, 6.75), rot=(-.25, 0, s * .5), bevel=0)
        a.part('Bridge_wings', 'Armor').box((.9, 1.0, .07), loc=(s * 2.45, -8.2, 6.2), bevel=.01)
        K.railing(rails, [(s * 2.9, -8.7, 6.24), (s * 2.9, -7.7, 6.24)], h=.7, post=.5, r=.014)
        K.portholes(a, [(s * 2.31, y, 4.4) for y in (-9.0, -7.4, -5.8, -4.2, -2.6)], (s, 0, 0), r=.09)
        K.door(a, (s * 2.32, -3.2, 2.98), size=(.6, 1.3), normal=(s, 0, 0), mat='Armor', frame_mat='Steel')
        K.ladder(a.part('Ladders', 'Steel'), (s * 2.55, -2.0, 3.0), (s * 2.1, -2.0, 5.38), width=.35, step=.25)
    K.railing(rails, [(-2.35, -10.4, 5.42), (2.35, -10.4, 5.42)], h=.7, post=.8, r=.014)
    # The pyramid mast on the bridge roof: four lattice legs, the platforms, the yards, the radar on top.
    pm = a.part('Mast', 'Steel')
    MY = -2.9
    base, top, zb, zt = 1.25, .34, 5.38, 10.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            pm.tube([(sx * base, MY + sy * base, zb), (sx * top, MY + sy * top, zt)], .05, seg=5)
    for f in (.25, .5, .75):
        w_ = base + (top - base) * f
        z_ = zb + (zt - zb) * f
        pm.tube([(-w_, MY - w_, z_), (w_, MY - w_, z_), (w_, MY + w_, z_), (-w_, MY + w_, z_),
                 (-w_, MY - w_, z_)], .025, seg=4)
        if f < .7:
            for sx in (-1, 1):
                pm.tube([(sx * w_, MY - w_, z_), (sx * (w_ + (top - base) * .25), MY + w_ + (top - base) * .25,
                                                    z_ + (zt - zb) * .25)], .018, seg=3)
    a.part('Mast_platform', 'Armor').box((1.6, 1.6, .06), loc=(0, MY, 8.1), bevel=.01)
    pm.box((3.6, .08, .08), loc=(0, MY, 9.4), bevel=0)
    for x in (-1.6, 1.6):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, MY, 9.45), h=1.3, r=.016, lean=0)
    RN.sc_radar(a, (0, MY, 10.45))
    for s in (-1, 1):
        K.dish(a.part('Dishes', 'Medical'), a.part('Dish_feeds', 'Steel'), (s * .8, MY + .3, 8.4), r=.28,
               normal=(s * .3, -1, .2), seg=10)
    K.beacon(a, (1.15, MY, 9.48), r=.07)     # R1: off the spinning radar's path, on the yard
    # The APS launchers on the 01 level ahead of the bridge (Mount_APS at their centre).
    aps = a.pivot('Mount_APS', (0, -10.1, 5.4))
    for s in (-1, 1):
        K.chamfer_box(a.part('Aps_launchers', 'Armor', aps), (.42, .4, .34), loc=(s * 1.2, 0, .2), c=.03)
        for j in range(3):
            a.part('Aps_tubes', 'Undercarriage', aps).cyl(.05, .03, loc=(s * 1.2 - .12 + j * .12, -.21, .22),
                                                          rot=K.FORWARD, seg=6, bevel=0)
    # Part_vls: the angled anti-ship missile tubes along both sides, in pairs (Slava's battery).
    pv = a.pivot('Part_vls', (0, -6.2, 3.0))
    tubes = a.part('Missile_tubes', 'Team', pv)
    caps = a.part('Tube_caps', 'Armor', pv)
    cr = a.part('Tube_cradles', 'Steel', pv)
    ang = .3
    for s in (-1, 1):
        for y in (-3.6, -1.2, 1.2, 3.6):
            for dx in (.0, .62):
                x = s * (2.85 + dx)
                k.lathe(tubes, [(0, -1.25), (.27, -1.25), (.29, -1.15), (.29, 1.15), (.27, 1.25), (0, 1.25)],
                        loc=(x, y, .78), rot=(R90 - ang, 0, 0), seg=10)
                k.lathe(caps, [(.29, 0), (.3, .06), (0, .08)], loc=(x, y - 1.25 * math.cos(ang),
                                                                    .78 + 1.25 * math.sin(ang)),
                        rot=(R90 - ang, 0, 0), seg=10)
            cr.box((1.4, .14, .5), loc=(s * 3.16, y - .6, .3), bevel=0)
            cr.box((1.4, .14, .9), loc=(s * 3.16, y + .6, .52), bevel=0)
    K.tone(a, 'Part_vls', k=.88)
    # The twin funnels side by side, their caps and the soot.
    fn = a.part('Funnel', 'Team')
    for s in (-1, 1):
        k.extrude(fn, [(-.75, -1.6), (.75, -1.6), (.9, -1.0), (.9, 1.8), (-.9, 1.8), (-.9, -1.0)], 4.4,
                  loc=(s * 1.15, 2.6, 5.15), rot=(-.1, 0, 0), axis='Z', chamfer=.05, taper=(.86, .9))
        k.extrude(a.part('Funnel_cap', 'Charred', None), [(-.6, -1.25), (.6, -1.25), (.72, -.75), (.72, 1.45),
                                                          (-.72, 1.45), (-.72, -.75)], .3,
                  loc=(s * 1.15, 3.05, 7.42), rot=(-.1, 0, 0), axis='Z')
        K.soot(a, (s * 1.15, 3.2, 7.6), radius=1.3, k=.5)
    a.part('Funnel_bands', 'Team').box((3.9, 3.2, .18), loc=(0, 2.7, 6.6), rot=(-.1, 0, 0), bevel=0)
    a.part('Funnel_base', 'Team').box((4.4, 5.2, .5), loc=(0, 2.4, 3.2), bevel=.04)
    # The after superstructure: the mainmast, the fire-control dome, the gatlings, the SAM revolver lids, the hangar.
    af = a.part('Aft_superstructure', 'Team')
    lvl = [(-2.0, 5.0), (2.0, 5.0), (2.4, 5.8), (2.4, 13.6), (-2.4, 13.6), (-2.4, 5.8)]
    W.poly_turret(af, [(2.95, lvl), (5.0, [(x * .96, y) for x, y in lvl])], chamfer=.05)
    k.inset(af, lambda c, n, f: abs(n.z) < .35, width=.08, depth=-.015)
    a.part('Tier_deck', 'Armor').box((4.7, 8.5, .06), loc=(0, 9.3, 5.03), bevel=.01)
    mm = a.part('Mainmast', 'Steel')
    for leg in ((0, 5.8), (-.7, 7.2), (.7, 7.2)):
        mm.tube([(leg[0], leg[1], 5.03), (0, 6.4, 9.0)], .07, seg=5)
    mm.box((2.8, .08, .08), loc=(0, 6.4, 8.4), bevel=0)
    K.dish(a.part('Dishes', 'Medical'), a.part('Dish_feeds', 'Steel'), (0, 6.0, 9.25), r=.4, normal=(0, -1, .5),
           seg=12)
    k.lathe(a.part('Fc_dome', 'PlasterWhite'), [(.85, 0), (.85, .25), (.7, .7), (.4, 1.0), (0, 1.1)],
            loc=(0, 10.6, 5.06), seg=16)
    k.lathe(a.part('Fc_dome_base', 'Armor'), [(1.0, -.3), (1.0, 0), (.9, .05)], loc=(0, 10.6, 5.06), seg=16)
    for s in (-1, 1):
        RN.sc_ak630(a, (s * 1.6, 8.2, 5.06), s=.7)
        K.portholes(a, [(s * 2.41, y, 4.2) for y in (6.6, 8.2, 9.8, 11.4)], (s, 0, 0), r=.09)
        K.door(a, (s * 2.42, 12.6, 2.98), size=(.6, 1.3), normal=(s, 0, 0), mat='Armor', frame_mat='Steel')
    K.railing(rails, [(-2.45, 5.0, 5.06), (2.45, 5.0, 5.06)], h=.7, post=.8, r=.014)
    lids = a.part('Sam_lids', 'Steel')
    for y in (14.6, 16.0):
        for x in (-1.4, 0, 1.4):
            k.lathe(lids, [(.5, 0), (.5, .06), (.42, .1), (0, .12)], loc=(x, y, H.deck_z(y) + .05), seg=14)
            lids.box((.06, .9, .04), loc=(x, y, H.deck_z(y) + .17), bevel=0)
    # The hangar door in the after superstructure's stern face, the helicopter deck aft.
    a.part('Hangar_door', 'Undercarriage').box((3.0, .05, 1.7), loc=(0, 13.62, 3.9), bevel=0)
    for j in range(5):
        a.part('Door_slats', 'Steel').box((3.0, .04, .04), loc=(0, 13.66, 3.2 + j * .35), bevel=0)
    hd = a.part('Heli_deck', 'Asphalt')
    hd.box((7.2, 7.6, .06), loc=(0, 20.0, H.deck_z(20.0) + .08), bevel=0)
    mk = a.part('Deck_markings', 'PlasterWhite')
    k.ring(mk, [(1.6, 0), (1.8, 0), (1.8, .02), (1.6, .02)], loc=(0, 20.0, H.deck_z(20.0) + .12), seg=24)
    mk.box((.12, 7.0, .02), loc=(0, 20.0, H.deck_z(20.0) + .12), bevel=0)
    for s in (-1, 1):
        mk.box((.08, 7.4, .02), loc=(s * 3.45, 20.0, H.deck_z(20.0) + .12), bevel=0)
        for y in (17.0, 20.0, 23.0):
            a.part('Deck_lights', 'Lamp').cyl(.05, .04, loc=(s * 3.55, y, H.deck_z(y) + .12), seg=6, bevel=0)
    # Boats in their davits by the funnels, life rafts, vents.
    for s in (-1, 1):
        K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Canvas'), (s * 3.25, 2.0, 3.6), length=3.2, beam=1.2)
        for y in (1.0, 3.0):
            a.part('Davits', 'Steel').tube([(s * 2.6, y, 3.0), (s * 2.6, y, 4.6), (s * 3.3, y, 4.75)], .05, seg=5)
        liferaft_rack(a, (s * 3.2, 6.6, H.deck_z(6.6) + .06), n=2, axis='X', r=.2, length=.75)
        vent(a.part('Vents', 'Steel'), (s * 3.0, -13.0, H.deck_z(-13.0) + .05), r=.18, h=.7)
    for s in (-1, 1):
        RN.sc_ak630(a, (s * 1.7, -11.6, 3.05), s=.7)


def _sc_weapons(a):
    """Part_gun > Mount_gun (the twin 130 mm on the foredeck), Part_mg > Mount_mg (the 127 mm on the bridge roof)."""
    RN.sc_ak130(a, (0, -15.2, SC_H.deck_z(-15.2) + .02), SC_H.deck_z(-15.2) + .3)
    K.soot(a, (0, -22.4, 4.2), radius=.6, k=.35)
    K.tone(a, 'Part_gun', k=.92)
    RN.sc_ak100(a, (0, -7.3, 7.36))
    K.tone(a, 'Part_mg', k=.9)


def scylla(a):
    """Scylla (see the module docstring), its own model (balance "model": "scylla"). Runtime (the variant keeps
    turret_fore, vls, ciws_fore of leviathan): Part_gun > Mount_gun > Gun_barrels / Gun_muzzles, Muzzle_gun with
    the per-barrel muzzles (twin 130 mm), Part_mg > Mount_mg > Dp_barrels, Muzzle_mg (127 mm), Part_vls, Radar,
    Mount_APS (the inherited APS). No other Part_* of the parent."""
    K.suffixed(a)
    _sc_hull(a)
    _sc_deck(a)
    _sc_superstructure(a)
    _sc_weapons(a)
    a.pivot('Point_fire', (0, 2.0, 5.0))
    a.pivot('Point_exhaust', (0, 3.0, 7.6))
    k.clean(a)


# ============================================================================= nyx
NX = [(-26.5, .18, .04, 2.72, .35, 1.0), (-25.6, .55, .14, 2.78, .9, 1.1), (-23.6, 1.25, .62, 2.86, 1.3, 1.3),
      (-20.0, 2.25, 1.55, 2.95, 1.5, 1.6), (-15.0, 3.3, 2.6, 3.0, 1.6, 2.0), (-8.0, 4.1, 3.42, 3.0, 1.6, 2.6),
      (0.0, 4.45, 3.76, 3.0, 1.6, 3.0), (10.0, 4.45, 3.8, 3.0, 1.6, 3.0), (18.0, 4.3, 3.75, 3.0, 1.5, 2.7),
      (24.0, 4.1, 3.62, 3.0, 1.25, 2.2), (26.4, 4.0, 3.56, 3.0, 1.1, 2.0)]
NX_H = Hull(NX, flare=1.0)
NX_DH = [(-2.6, -7.2), (2.6, -7.2), (3.45, -5.8), (3.55, 13.0), (-3.55, 13.0), (-3.45, -5.8)]


def _nx_hull(a):
    H = NX_H
    H.build(a, under='Undercarriage', boot='Charred', top='Armor', round_edge=.06)
    seams = a.part('Hull_seams', 'Armor')
    H.line(seams, 1.1, -22.0, 26.0, out=.006, r=.012, step=1.5)
    H.line(seams, 2.1, -21.0, 26.2, out=.006, r=.012, step=1.5)
    # The chine (knuckle) line, the anchor recesses, the draft marks, the stern; no portholes (stealth).
    H.line(a.part('Chine', 'Steel'), .55, -24.0, 26.3, out=.02, r=.03, step=1.0)
    for s in (-1, 1):
        y = -21.0
        a.part('Anchor_recess', 'Undercarriage').box((.04, .9, .7), loc=(s * (H.hb(y, 2.0) + .005), y, 2.0),
                                                     rot=(0, s * -.12, 0), bevel=0)
    marks = a.part('Draft_marks', 'PlasterWhite')
    for y in (-23.5, 26.0):
        for s in (-1, 1):
            for z in (-.6, -.3, 0, .3, .6):
                marks.box((.02, .22, .05), loc=(s * (H.hb(y, z) + .02), y, z), bevel=0)
    for x in (1.5, -1.5):
        r = .48
        zc = under_z(NX_H, 22.5, x) - r * .45
        a.part('Shafts', 'Steel').tube([(x * .5, 15.5, under_z(NX_H, 15.5, x * .5) + .2), (x, 22.2, zc)], .09, seg=6)
        k.lathe(a.part('Screws', 'Gilded'), [(0, -.2), (.17, -.18), (.17, .15), (0, .24)], loc=(x, 22.5, zc),
                rot=(-R90, 0, 0), seg=8)
        for j in range(5):
            u = j * TAU / 5 + .3
            a.part('Screws', 'Gilded').box((.05, .15, r * .75), loc=(x + math.cos(u) * r * .5, 22.53,
                                                                     zc + math.sin(u) * r * .5),
                                           rot=(0, -u + R90, 0), bevel=0)
        zt = under_z(NX_H, 24.4, x) + .15
        k.extrude(a.part('Rudders', 'Undercarriage'), [(23.8, zt), (25.2, zt), (25.2, zt - .8), (24.0, zt - .85)],
                  .16, loc=(x, 0, 0), axis='X', chamfer=.03)
    H.deck(a, 'Deck', 'Asphalt', -26.0, 26.2, inset=.08, t=.05, step=1.0)
    pan = a.part('Deck_panels', 'Armor')
    for y in range(-22, -7, 3):
        for x in (-1.3, 1.3):
            if abs(x) + 1.0 < H.deck_half(y) - .3:
                pan.box((2.0, 2.6, .02), loc=(x, y, H.deck_z(y) + .085), bevel=0)
    fit = a.part('Fittings', 'Steel')
    for y in (-19.0, 16.0, 23.0):
        for s in (-1, 1):
            # Flush, retractable stealth bollards: low domes in recesses.
            k.lathe(fit, [(.16, 0), (.16, .08), (.1, .14), (0, .15)], loc=(s * (H.deck_half(y) - .5), y,
                                                                         H.deck_z(y) + .07), seg=10)


def _nx_deckhouse(a):
    """The faceted deckhouse: the lower block with its tumblehome walls, the upper pyramid with the flush array faces
    (the APS's eyes, Mount_APS), the bridge's slit windows, the two exhaust uplifts, the comms mast; the hangar and
    the helicopter deck aft."""
    dh = a.part('Deckhouse', 'Team')
    k.sharp_loft(dh, [[(x, y, 3.02) for x, y in NX_DH],
                      [(x * .86, y + (.95 if y < 0 else -.55), 6.4) for x, y in NX_DH]], chamfer=.07)
    up = [(-1.7, -4.4), (1.7, -4.4), (2.55, -3.2), (2.55, 6.6), (-2.55, 6.6), (-2.55, -3.2)]
    k.sharp_loft(dh, [[(x, y, 6.38) for x, y in up], [(x * .7, y * .62 + 1.4, 9.15) for x, y in up]], chamfer=.06)
    k.inset(dh, lambda c, n, f: abs(n.z) < .55, width=.1, depth=-.018)
    a.part('Deckhouse_roof', 'Armor').box((5.4, 16.5, .05), loc=(0, 4.6, 6.42), bevel=.01)
    glass = a.part('Windows', 'Glass')
    # The bridge's slit windows on the upper pyramid's sloped front, the side slits.
    for i in range(9):
        x = -1.2 + i * .3
        glass.box((.22, .03, .14), loc=(x, -3.95, 7.25), rot=(-.6, 0, 0), bevel=0)
    faces = a.part('Array_faces', 'Undercarriage')
    rims = a.part('Array_rims', 'Steel')
    for n, loc in (((0, -2.77, 3.07), (0, -2.71, 7.9)), ((2.77, 0, .765), (2.13, 1.6, 7.9)),
                   ((-2.77, 0, .765), (-2.13, 1.6, 7.9)), ((0, 2.77, 1.11), (0, 5.99, 7.9))):
        nv = Vector(n).normalized()
        rot = K.rot_to(tuple(nv))
        faces.box((1.3, 1.3, .05), loc=tuple(Vector(loc) + nv * .035), rot=rot, bevel=0)
        rims.box((1.42, 1.42, .025), loc=tuple(Vector(loc) + nv * .012), rot=rot, bevel=0)
    a.pivot('Mount_APS', (0, -2.0, 8.6))
    ex = a.part('Exhausts', 'Charred')
    for x in (-.75, .75):
        k.extrude(ex, [(-.5, -.55), (.5, -.55), (.45, .55), (-.45, .55)], .3, loc=(x, 4.5, 9.25), axis='Z',
                  chamfer=.03)
        for j in range(4):
            a.part('Exhaust_slats', 'Steel').box((.85, .05, .05), loc=(x, 4.1 + j * .27, 9.42), bevel=0)
        K.soot(a, (x, 4.5, 9.5), radius=1.0, k=.5)
    # The comms mast on the pyramid's top, the whips, the beacon, the IFF ring.
    cm = a.part('Mast', 'Steel')
    k.lathe(cm, [(.22, 0), (.18, .3), (.1, .55), (.05, .7)], loc=(0, 2.6, 9.15), seg=8)
    k.ring(cm, [(.32, 0), (.38, 0), (.38, .12), (.32, .12)], loc=(0, 2.6, 9.42), seg=12)
    for dx in (-.9, .9):
        K.whip_antenna(a.part('Antennas', 'Steel'), (dx, 3.4, 9.1), h=.6, r=.015, lean=0)
    K.beacon(a, (0, 2.6, 9.85), r=.05)
    for s in (-1, 1):
        K.door(a, (s * 3.42, 10.0, 3.02), size=(.6, 1.3), normal=(s, -0, .15), mat='Armor', frame_mat='Steel')
    # The hangar in the deckhouse's stern face, the helicopter deck aft with its markings and nets, a drone parked.
    a.part('Hangar_door', 'Undercarriage').box((4.2, .05, 2.4), loc=(0, 12.96, 4.3), bevel=0)
    for j in range(7):
        a.part('Door_slats', 'Steel').box((4.2, .04, .04), loc=(0, 13.0, 3.3 + j * .34), bevel=0)
    H = NX_H
    mk = a.part('Deck_markings', 'PlasterWhite')
    k.ring(mk, [(1.7, 0), (1.9, 0), (1.9, .02), (1.7, .02)], loc=(0, 19.4, H.deck_z(19.4) + .1), seg=24)
    mk.box((.12, 10.0, .02), loc=(0, 19.4, H.deck_z(19.4) + .1), bevel=0)
    for s in (-1, 1):
        mk.box((.08, 11.0, .02), loc=(s * 3.2, 19.6, H.deck_z(19.6) + .1), bevel=0)
        a.part('Deck_nets', 'Steel').box((.4, 11.0, .03), loc=(s * (H.deck_half(19.6) + .12), 19.6,
                                                                H.deck_z(19.6) - .05), rot=(0, s * .3, 0), bevel=0)
        for y in (15.5, 19.5, 23.5):
            a.part('Deck_lights', 'Lamp').cyl(.05, .04, loc=(s * 3.3, y, H.deck_z(y) + .1), seg=6, bevel=0)
    RN.nx_drone(a, (.6, 19.8, H.deck_z(19.8) + .1), yaw=.35, s=.85)
    a.part('Stern_lights', 'Lamp').cyl(.07, .05, loc=(0, 26.42, 2.4), rot=(R90, 0, 0), seg=8, bevel=0)


def _nx_detail(a):
    """Nyx's finer layer: the deckhouse's raised panel seams and the team band at its foot, the side doors, the boat
    bays with their RHIBs, the EO/IR balls and the IFF on the pyramid, the decoy launchers, the folding lifelines
    along the deck edges, the anchor in its recess, the helicopter deck's tie-down grid, the hull's panel seams."""
    H = NX_H
    seam = a.part('Deckhouse_seams', 'Armor')
    tilt = math.atan2(.5, 3.38)
    for z in (4.0, 5.0, 5.9):
        f = (z - 3.02) / 3.38
        for s in (-1, 1):
            x = 3.55 - .5 * f + .012
            y0, y1 = -5.8 + 0.95 * f + .3, 13.0 - .55 * f - .2
            seam.box((.03, y1 - y0, .05), loc=(s * x, (y0 + y1) / 2, z), rot=(0, s * tilt, 0), bevel=0)
    for y in range(-4, 13, 2):
        for s in (-1, 1):
            seam.tube([(s * (3.55 + .012), y, 3.1), (s * (3.05 + .012), y, 6.3)], .02, seg=3)
    a.part('Hull_band', 'Team').box((7.25, 19.6, .12), loc=(0, 3.2, 3.1), bevel=.01)
    for s in (-1, 1):
        for y in (-3.6, 4.0):
            K.door(a, (s * 3.47, y, 3.12), size=(.62, 1.35), normal=(s, 0, .14), mat='Armor', frame_mat='Steel')
        # The boat bay: the dark recess in the deckhouse side, its RHIB on the cradle, the roller door above.
        a.part('Boat_bay', 'Undercarriage').box((.05, 3.6, 1.55), loc=(s * 3.44, 9.6, 4.1), rot=(0, s * tilt, 0),
                                                bevel=0)
        # The RHIB swung out on its davit arms, ready to lower.
        bx = H.deck_half(9.6) - .45
        K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Canvas'), (s * bx, 9.6, 3.55), length=3.2, beam=.9)
        a.part('Bay_door', 'Steel').box((.06, 3.7, .35), loc=(s * 3.25, 9.6, 5.05), rot=(0, s * tilt, 0), bevel=0)
        for dy in (-1.1, 1.1):
            a.part('Davits', 'Steel').tube([(s * 3.2, 9.6 + dy, 4.9), (s * (bx + .1), 9.6 + dy, 5.1),
                                            (s * (bx + .1), 9.6 + dy, 4.3)], .05, seg=5)
        # Folding HF whips raised at 45 degrees from the deck edge.
        for y in (-17.0, 15.0, 22.0):
            x0 = H.deck_half(y) - .1
            a.part('Whips', 'Steel').tube([(s * x0, y, H.deck_z(y) + .1), (s * (x0 + .5), y, H.deck_z(y) + 3.2)],
                                          .045, seg=5)
            a.part('Whip_bases', 'Armor').box((.3, .3, .25), loc=(s * x0, y, H.deck_z(y) + .15), bevel=.02)
    # The after comms mast on the deckhouse roof: lattice legs, two yards, the satcom domes and dishes.
    am = a.part('Aft_mast', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            am.tube([(sx * .55, 11.6 + sy * .55, 6.45), (sx * .18, 11.6 + sy * .18, 9.7)], .04, seg=5)
    for z, w_ in ((7.4, 1.6), (8.6, 1.1)):
        am.box((2 * w_, .07, .07), loc=(0, 11.6, z), bevel=0)
        for sx in (-1, 1):
            am.tube([(sx * w_, 11.6, z), (sx * w_, 11.6, z + .7)], .02, seg=3)
    for x, z in ((-.7, 9.2), (.7, 9.2)):
        k.lathe(a.part('Satcom_domes', 'PlasterWhite'), [(.3, 0), (.32, .2), (.2, .45), (0, .5)], loc=(x, 11.4, z),
                seg=10)
    am.box((1.6, .7, .08), loc=(0, 11.5, 9.2), bevel=0)
    K.dish(a.part('Dishes', 'Medical'), a.part('Dish_feeds', 'Steel'), (0, 11.15, 8.0), r=.35, normal=(0, -1, .3),
           seg=10)
    eo = a.part('Sensor_balls', 'PlasterWhite')
    for x, y in ((-1.4, -.9), (1.4, -.9), (-1.4, 5.1), (1.4, 5.1)):
        k.lathe(eo, [(.18, 0), (.2, .08), (.17, .28), (0, .33)], loc=(x, y, 9.15), seg=10)
    for s in (-1, 1):
        dl = a.part('Decoy_launchers', 'Armor')
        for j in range(2):
            dl.box((.5, .55, .3), loc=(s * 2.2, 7.2 + j * .8, 6.6), rot=(.5, 0, 0), bevel=.02)
            for q in range(3):
                a.part('Decoy_tubes', 'Undercarriage').cyl(.06, .04, loc=(s * 2.2 - .15 + q * .15, 7.2 + j * .8 - .25,
                                                                           6.68), rot=K.FORWARD, seg=6, bevel=0)
    life = a.part('Lifelines', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-23.0, -8.0), (13.6, 25.6)):
            n = int((y1 - y0) / 1.5)
            pts = [(s * (H.deck_half(y) - .12), y, H.deck_z(y) + .06) for y in
                   (y0 + (y1 - y0) * i / n for i in range(n + 1))]
            K.railing(life, pts, h=.7, post=1.5, r=.022)
    ag = a.part('Anchors', 'Steel')
    for s in (-1, 1):
        y = -21.0
        ag.box((.1, .45, .55), loc=(s * (H.hb(y, 2.0) + .03), y, 2.0), rot=(0, s * -.12, 0), bevel=.02)
    td = a.part('Tie_downs', 'Steel')
    for i in range(6):
        for j in range(7):
            y = 15.6 + j * 1.3
            x = -2.5 + i * 1.0
            if abs(x) < H.deck_half(y) - .6:
                td.cyl(.06, .02, loc=(x, y, H.deck_z(y) + .085), seg=6, bevel=0)
    seams = a.part('Hull_seams', 'Armor')
    for y in range(-20, 26, 3):
        for s in (-1, 1):
            seams.tube([(s * (H.hb(y, z) + .006), y, z) for z in (.35, 1.5, 2.85)], .01, seg=3)


def _nx_weapons(a):
    """R1 (owner 04/10: the railgun goes, a gun turret takes its mount): Part_gun > Mount_gun, the AGS-style 155 mm
    stealth turret (mb_pt14_r1_naval.nx_ags); Part_vls, the peripheral VLS modules set into both deck edges forward
    of the deckhouse, and two more aft; Part_mg / .001 > Mount_mg / .001, the Mk 110-style stealth cupolas on the
    deckhouse roof fore and aft (mounts 1, 2 fire 127 mm)."""
    H = NX_H
    RN.nx_ags(a)
    a.pivot('Part_vls', (0, -8.6, 3.0))
    for s in (-1, 1):
        x = s * (H.deck_half(-8.6) - .75)
        for dy in (-.68, .68):
            RN.nx_pvls_module(a, 'Part_vls', x, dy, s, z=.02)
    K.tone(a, 'Part_vls', k=.88)
    for s in (-1, 1):
        RN.nx_pvls_module(a, None, s * (H.deck_half(14.2) - .75), 14.2, s, z=3.02)
    for pname, mount, muzzle, loc, tag in (('Part_mg', 'Mount_mg', 'Muzzle_mg', (0, -5.35, 6.42), ''),
                                           ('Part_mg__001', 'Mount_mg__001', 'Muzzle_mg__001', (0, 9.8, 6.42),
                                            '_001')):
        RN.nx_cupola(a, pname, mount, muzzle, loc, tag)


def nyx(a):
    """Nyx (see the module docstring). Runtime (the variant keeps turret_fore, vls, ciws_fore, ciws_aft of
    leviathan): Part_gun > Mount_gun > Gun_barrels / Gun_muzzles, Muzzle_gun (the AGS-style 155 mm), Part_vls, Part_mg /
    .001 > Mount_mg / .001 > Cupola_barrels*, Muzzle_mg / .001 (127 mm), Mount_APS."""
    K.suffixed(a)
    _nx_hull(a)
    _nx_deckhouse(a)
    _nx_weapons(a)
    _nx_detail(a)
    a.pivot('Point_fire', (0, 4.0, 6.0))
    a.pivot('Point_exhaust', (0, 6.5, 7.0))
    k.clean(a)


# ============================================================================= hydra_sub
HY_AX = -.3            # the pressure hull's axis (the waterline just above it, at the pivot)
HY_R = 2.45            # the pressure hull's radius
HY_DECK = 2.2          # the casing deck


def _hy_radius(y):
    """The hull's radius along y: the bow dome, the parallel body, the long stern cone."""
    if y < -13.0:
        t = (y + 17.2) / 4.2
        return HY_R * math.sqrt(max(0.0, 1 - (1 - t) ** 2)) if t > 0 else 0.0
    if y < 7.0:
        return HY_R
    t = (y - 7.0) / 10.2
    return HY_R * (1 - .72 * t ** 1.5)


def _hy_hull(a):
    """The lathed pressure hull with its anechoic-tile lower half (dark) and the tile seams, the casing deck with
    its limber holes and the safety track, the bow's hydroplanes, the escape hatches."""
    prof = []
    for i in range(41):
        y = -17.2 + 34.4 * i / 40
        prof.append((max(.04 if 0 < i < 40 else 0.0, _hy_radius(y)), y))
    prof[0] = (0, -17.2)
    prof[-1] = (_hy_radius(17.2) * .98, 17.2)
    upper = a.part('Hull', 'Armor')
    k.lathe(upper, [(r, -y) for r, y in prof], loc=(0, 0, HY_AX), rot=K.FORWARD, seg=28)
    # The tile seams round the hull, a band of the team colour on the upper hull.
    tiles = a.part('Hull_tiles', 'Undercarriage')
    for y in range(-14, 12, 2):
        r = _hy_radius(y) + .012
        k.ring(tiles, [(r, 0), (r + .01, 0), (r + .01, .04), (r, .04)], loc=(0, y, HY_AX), rot=K.FORWARD, seg=24)
    # The casing: a flat-topped free-flooding deck over the hull from the bow to the stern cone.
    cs = a.part('Casing', 'Armor')
    rings = []
    for y in [-14.6 + i * 1.0 for i in range(27)]:
        r = _hy_radius(y)
        w = min(.98, r * .5)
        top = HY_DECK + (0 if y < 9 else -(y - 9) * .12)
        rings.append([(-w * 1.25, y, HY_AX + r * .78), (w * 1.25, y, HY_AX + r * .78), (w, y, top), (-w, y, top)])
    rings.insert(0, [(0, -15.4, HY_AX + 1.9)])
    rings.append([(0, 12.2, HY_DECK - .4)])
    cs.loft(rings, bevel=0)
    holes = a.part('Limber_holes', 'Undercarriage')
    for y in [-12.0 + i * .7 for i in range(30)]:
        if -6.4 < y < -.4:
            continue
        r = _hy_radius(y)
        w = min(.98, r * .5)
        for s in (-1, 1):
            holes.box((.03, .4, .12), loc=(s * (w * 1.12 + .02), y, HY_AX + r * .78 + (HY_DECK - HY_AX - r * .78) * .4),
                      rot=(0, s * -.7, 0), bevel=0)
    trk = a.part('Safety_track', 'Steel')
    trk.tube([(0, -13.5, HY_DECK + .02), (0, 9.0, HY_DECK + .02)], .03, seg=4)
    for y in (-11.0, 9.5):
        k.lathe(a.part('Escape_hatches', 'Armor'), [(.38, 0), (.38, .06), (.3, .1), (0, .11)], loc=(0, y, HY_DECK),
                seg=14)
    for y in (-12.5, 8.0):
        for s in (-1, 1):
            k.lathe(a.part('Cleats', 'Steel'), [(.08, 0), (.08, .12), (.12, .15), (0, .16)],
                    loc=(s * .8, y, HY_DECK), seg=8)
    # The bow hydroplanes folded against the casing, the sonar window, the draft marks.
    for s in (-1, 1):
        k.extrude(a.part('Bow_planes', 'Undercarriage'), [(-.9, -.05), (.6, -.05), (.6, .05), (-.9, .05)], 1.3,
                  loc=(s * 2.85, -12.6, HY_AX + .9), rot=(0, 0, 0), axis='X', chamfer=.02)
    a.part('Sonar_window', 'Glass').box((1.6, .04, .9), loc=(0, -16.5, HY_AX - .2), rot=(.6, 0, 0), bevel=0)
    marks = a.part('Draft_marks', 'PlasterWhite')
    for y in (-15.0, 13.0):
        for s in (-1, 1):
            for z in (-.5, -.2, .1, .4):
                r = _hy_radius(y)
                marks.box((.02, .2, .05), loc=(s * (math.sqrt(max(.01, r * r - (z - HY_AX) ** 2)) + .02), y, z),
                          bevel=0)
    # Longitudinal tile seams, the casing's panel lines, the capstan, the towed-array fairing along the right side.
    for u in (math.radians(d) for d in (-150, -115, -80, -45, 45, 80, 115, 150, 180)):
        pts = []
        for y in [-13.5 + i * 1.5 for i in range(16)]:
            r = _hy_radius(y) + .012
            pts.append((math.sin(u) * r, y, HY_AX + math.cos(u) * r))
        tiles.tube(pts, .012, seg=3)
    pl = a.part('Casing_panels', 'Undercarriage')
    for y in [-14.0 + i * 1.4 for i in range(19)]:
        if -6.4 < y < -.4:
            continue
        w = min(.98, _hy_radius(y) * .5)
        top = HY_DECK + (0 if y < 9 else -(y - 9) * .12)
        pl.box((2 * w - .1, .03, .012), loc=(0, y, top + .006), bevel=0)
    k.lathe(a.part('Capstan', 'Steel'), [(.22, 0), (.22, .14), (.16, .18), (.16, .3), (.2, .34), (0, .36)],
            loc=(.45, -14.2, HY_DECK), seg=10)
    ta = a.part('Towed_array', 'Steel')
    ta.tube([(-(HY_R + .06) * .7, y, HY_AX + (HY_R + .06) * .7) for y in (-6.0, 0.0, 6.0)], .08, seg=6)
    ta.tube([(-(_hy_radius(y) + .06) * .7, y, HY_AX + (_hy_radius(y) + .06) * .7) for y in (6.0, 10.0, 14.0)], .06,
            seg=6)
    team = a.part('Hull_band', 'Team')
    team.box((.05, 6.0, .3), loc=(1.62, -9.5, HY_AX + 1.65), rot=(0, -.75, 0), bevel=0)
    team.box((.05, 6.0, .3), loc=(-1.62, -9.5, HY_AX + 1.65), rot=(0, .75, 0), bevel=0)


def _hy_sail(a):
    """The sail: the lofted fin with its fairwater planes, the bridge cockpit windows, the masts (periscopes, the
    radar, the snorkel, the comms mast), the rails of the bridge."""
    sl = a.part('Sail', 'Team')
    rings = []
    for z in (HY_DECK - .1, 4.4):
        sec = []
        for i in range(12):
            u = i / 12 * TAU
            # A teardrop plan: blunt front, tapering trailing edge.
            x = math.sin(u) * (.78 if z < 4.2 else .7)
            y = -math.cos(u) * 2.7
            if y > 0:
                x *= (1 - y / 2.7 * .55)
            sec.append((x, y - 3.4 + (0 if z < 4.2 else .25), z))
        rings.append(sec)
    sl.loft(rings, bevel=0)
    a.part('Sail_top', 'Armor').loft([[(x, y, 4.4) for x, y, _ in rings[1]], [(x * .92, y, 4.48) for x, y, _ in
                                                                              rings[1]]], bevel=0)
    for s in (-1, 1):
        k.extrude(a.part('Sail_planes', 'Undercarriage'), [(-.7, -.06), (.9, -.04), (.9, .04), (-.7, .06)], 1.6,
                  loc=(s * 1.45, -4.6, 3.3), axis='X', chamfer=.02)
    glass = a.part('Windows', 'Glass')
    for i in range(5):
        u = (i - 2) * .32
        glass.box((.22, .03, .2), loc=(math.sin(u) * .7, -6.05 + (1 - math.cos(u)) * .6, 4.1), rot=(0, 0, u), bevel=0)
    rails = a.part('Railings', 'Steel')
    rails.tube([(-.6, -5.6, 5.0), (0, -6.0, 5.0), (.6, -5.6, 5.0)], .02, seg=4)
    for x, y in ((-.6, -5.6), (0, -6.0), (.6, -5.6)):
        rails.box((.03, .03, .5), loc=(x, y, 4.74), bevel=0)
    masts = a.part('Masts', 'Steel')
    for x, y, h, r in ((0, -4.4, 1.0, .1), (.25, -3.6, .85, .08), (-.25, -3.1, .7, .14), (0, -2.2, .55, .09)):
        masts.cyl(r, h, loc=(x, y, 4.48 + h / 2), seg=8, bevel=0)
    k.block(a.part('Periscope_heads', 'Armor'), (.22, .3, .25), loc=(0, -4.4, 5.55), chamfer=.03)
    a.part('Periscope_glass', 'Glass').box((.14, .02, .1), loc=(0, -4.56, 5.6), bevel=0)
    radar_array(a, 'Radar', (.25, -3.6, 5.35), None, w=.9, h=.2, tag='_h')
    k.lathe(a.part('Snorkel_head', 'Armor'), [(.2, 0), (.2, .3), (.14, .38), (0, .4)], loc=(-.25, -3.1, 5.18), seg=8)
    K.whip_antenna(a.part('Antennas', 'Steel'), (0, -2.2, 5.03), h=.55, r=.018, lean=0)
    K.beacon(a, (0, -1.6, 4.48), r=.06)
    # The sail's team band, the climbing rungs, the bridge hatch, the running lights.
    band = a.part('Sail_band', 'Team')
    sec = []
    for i in range(12):
        u = i / 12 * TAU
        x = math.sin(u) * .73
        y = -math.cos(u) * 2.7
        if y > 0:
            x *= (1 - y / 2.7 * .55)
        sec.append((x * 1.02, y - 3.4 + .2, 4.05))
    band.loft([[(x, y, 3.9) for x, y, _ in sec], [(x, y, 4.1) for x, y, _ in sec]], bevel=0)
    rungs = a.part('Rungs', 'Steel')
    for j in range(7):
        z = HY_DECK + .3 + j * .3
        rungs.box((.04, .32, .03), loc=(-.81, -2.2, z), bevel=0)
    k.block(a.part('Bridge_hatch', 'Armor'), (.5, .5, .06), loc=(0, -5.0, 4.5), chamfer=.015)
    for sx, mat in ((-1, 'Lamp'), (1, 'Lamp')):
        a.part('Running_lights', mat).cyl(.05, .06, loc=(sx * .62, -5.4, 4.2), rot=(0, R90, 0), seg=6, bevel=0)


def _hy_weapons(a):
    """Mount_gun / .001 (the twin 57 mm on retractable casing mounts fore and aft, Gun_barrels* kick parts, per-barrel
    muzzles), Mount_gun.002 (the 100 mm in its faceted mount forward of the sail on a raised pedestal), the launch
    tube hatches behind the sail (Part_doors_l / _r), the drone deck aft, the stern planes and the pump-jet
    (Part_rudder)."""
    for mount, muzzle, loc, tag, tg in (('Mount_gun', 'Muzzle_gun', (0, -12.6, HY_DECK), '', 'gun'),
                                        ('Mount_gun__001', 'Muzzle_gun__001', (0, 9.7, HY_DECK - .08), '_001',
                                         'gun_001')):
        k.lathe(a.part('Gun_well' + tag, 'Undercarriage'), [(.98, -.02), (.98, .03), (.9, .05)],
                loc=loc, seg=16)
        m = a.pivot(mount, (loc[0], loc[1], loc[2] + .04))
        W.poly_turret(a.part('Gun_house' + tag, 'Team', m), [
            (0, [(-.45, -1.0), (.45, -1.0), (.85, -.4), (.85, .9), (-.85, .9), (-.85, -.4)]),
            (.62, [(-.3, -.8), (.3, -.8), (.65, -.3), (.65, .75), (-.65, .75), (-.65, -.3)])], chamfer=.03)
        zg = .36
        for x in (-.2, .2):
            K.gun_barrel(a, 'Gun_barrels' + tag, m, x, -.85, zg, 2.3, .045, seg=8, extractor=(.3, 1.2, .2),
                         brake_name='Gun_muzzles' + tag, brake='collar')
        mz = a.pivot(muzzle, (0, -.85 - 2.3 - .06, zg), m)
        per_barrel(a, mz, tg, (-.2, .2))
        a.part('Gun_sight' + tag, 'Glass', m).box((.16, .02, .08), loc=(.42, -.62, .5), bevel=0)
    # The 100 mm forward of the sail on its pedestal (Mount_gun.002, the def's deck_gun part).
    k.lathe(a.part('Deck_gun_pedestal', 'Armor'), [(1.15, -.1), (1.15, .38), (1.05, .45)], loc=(0, -8.4, HY_DECK),
            seg=18)
    m = a.pivot('Mount_gun__002', (0, -8.4, HY_DECK + .45))
    W.poly_turret(a.part('Dg_house', 'Team', m), [
        (0, [(-.45, -1.35), (.45, -1.35), (1.05, -.4), (1.05, 1.15), (-1.05, 1.15), (-1.05, -.4)]),
        (.95, [(-.22, -.95), (.22, -.95), (.7, -.25), (.7, .95), (-.7, .95), (-.7, -.25)])], chamfer=.03)
    k.inset(a.part('Dg_house', 'Team', m), lambda c, n, f: abs(n.z) < .6, width=.05, depth=-.01)
    K.gun_barrel(a, 'Dg_barrels', m, 0, -1.15, .48, 3.4, .07, seg=10, extractor=(.35, 1.25, .25),
                 brake_name='Dg_muzzles', brake='collar')
    a.pivot('Muzzle_gun__002', (0, -1.15 - 3.4 - .06, .48), m)
    k.block(a.part('Dg_hatch', 'Armor', m), (.4, .35, .06), loc=(0, .5, .96), chamfer=.015)
    K.soot(a, (0, -13.0, 3.1), radius=.4, k=.3)
    # The launch tube hatches, five a side behind the sail (Part_doors_l / _r), riveted, one shade off.
    for name, s in (('Part_doors_l', 1), ('Part_doors_r', -1)):
        p = a.pivot(name, (s * .48, 3.8, HY_DECK))
        for j in range(5):
            y = -2.4 + j * 1.2
            k.block(a.part('Hatch_plates' + ('_l' if s > 0 else '_r'), 'Armor', p), (.82, 1.05, .08),
                    loc=(0, y, .04), chamfer=.02)
            a.part('Hatch_hinges' + ('_l' if s > 0 else '_r'), 'Steel', p).cyl(.04, .9, loc=(s * .43, y, .06),
                                                                              rot=(R90, 0, 0), seg=6, bevel=0)
            K.bolt_ring(a.part('Kit_bolts', 'Steel', p), (0, y, .085), (0, 0, 1), .32, 8, r=.018, h=.02)
        K.tone(a, name, k=.88)
    # The drone deck aft: six FPV quadcopters on their pads, the deck's hazard edge.
    dd = a.part('Drone_deck', 'Armor')
    dd.box((1.9, 3.6, .05), loc=(0, 12.4, HY_DECK - .4 - .15), bevel=0)
    a.part('Drone_edge', 'Hazard').box((1.95, .1, .02), loc=(0, 10.6, HY_DECK - .52), bevel=0)
    for j in range(6):
        x, y = (-.45 if j % 2 else .45), 11.2 + (j // 2) * 1.2
        z = HY_DECK - .48
        a.part('Drone_pads', 'PlasterWhite').cyl(.3, .02, loc=(x, y, z), seg=12, bevel=0)
        dr = a.part('Drones', 'Undercarriage')
        dr.box((.16, .22, .07), loc=(x, y, z + .06), bevel=.01)
        for dx, dy in ((-.15, -.15), (.15, -.15), (-.15, .15), (.15, .15)):
            dr.limb((x, y, z + .06), (x + dx, y + dy, z + .07), .025, .02, bevel=0)
            a.part('Drone_rotors', 'Steel').cyl(.08, .01, loc=(x + dx, y + dy, z + .1), seg=8, bevel=0)
    # Part_rudder: the cruciform stern planes and the shrouded pump-jet.
    pr = a.pivot('Part_rudder', (0, 15.4, HY_AX))
    pl = a.part('Stern_planes', 'Undercarriage', pr)
    for u in (0, R90, math.pi, -R90):
        span = 2.25 if u in (0, math.pi) else 1.55
        c, s_ = math.cos(u), math.sin(u)
        k.extrude(pl, [(-.9, -.05), (.7, -.04), (.7, .04), (-.9, .05)], span, loc=(c * (span / 2 + .3), -.2,
                                                                                    s_ * (span / 2 + .3)),
                  rot=(0, -u, 0), axis='X', chamfer=.02)
    k.lathe(a.part('Pumpjet', 'Undercarriage', pr), [(.62, 1.0), (.82, 1.2), (.8, 1.9), (.68, 2.1), (.6, 2.0),
                                                      (.6, 1.1)], loc=(0, 0, 0), rot=(-R90, 0, 0), seg=18)
    k.lathe(a.part('Pumpjet_hub', 'Steel', pr), [(0, .8), (.3, 1.0), (.25, 1.9), (0, 2.0)], rot=(-R90, 0, 0), seg=10)
    K.tone(a, 'Part_rudder', k=.9)


def hydra_sub(a):
    """Hydra's model (balance hydra "model": "hydra_sub"; see the module docstring). Runtime (the variant keeps
    doors_l, doors_r, deck_gun, rudder of typhon; its three gun mounts): Mount_gun / .001 (twin 57 mm, Gun_barrels*,
    Muzzle_gun / .001 + per-barrel muzzles), Mount_gun.002 (the 100 mm, the deck_gun part's node: data tune),
    Part_doors_l, Part_doors_r, Part_rudder, Radar."""
    K.suffixed(a)
    _hy_hull(a)
    _hy_sail(a)
    _hy_weapons(a)
    a.pivot('Point_fire', (0, 0.0, 2.6))
    k.clean(a)


BUILDERS = {
    'leviathan': (leviathan, dict(ao_distance=1.6, grime_height=1.0, ao_strength=.75)),
    'kraken': (kraken, dict(ao_distance=1.6, grime_height=1.0, ao_strength=.75)),
    'scylla': (scylla, dict(ao_distance=1.0, grime_height=.8, ao_strength=.75)),
    'nyx': (nyx, dict(ao_distance=1.0, grime_height=.7, ao_strength=.72)),
    'hydra_sub': (hydra_sub, dict(ao_distance=.8, grime_height=.6, ao_strength=.72)),
}
