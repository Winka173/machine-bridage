"""Machine Brigade munitions: one low-poly round per weapon family, built with frontier_kit.

Every vehicle used to fire the same `missile`, `rocket` or `bomb`. These models give each weapon a
round that looks like its real munition: ATGMs, Hellfires, MANPADS darts, air-to-air and surface-to-air
missiles, air-to-ground missiles, aircraft and artillery rockets, bombs, loitering munitions, tank
rounds, shells, a mortar bomb and a railgun slug. Real dimensions, fin layouts and colours come from the
r6 munitions research (section 5); lengths are the game lengths from its table, so a model is drawn
at the size it is built.

Conventions (as mb_air.py's munitions; ModelLibrary.Merged bakes each into one mesh per material):
  * metres, +Z up, the nose at -Y, the origin at the centre of the round's length and on its axis;
  * an emissive `Alloy` motor at the tail of powered rounds (a `Lamp` tracer on tank rounds and the
    rail slug); glide weapons, bombs and shells have none;
  * a few parts per model and 40-250 triangles: bodies are 6-10 sided lathes whose bands are their own
    rings (no hidden caps), fins and wings are thin double-sided plates.
Colours use house material names only (MaterialLibrary.Kit), mapped as below. Olive drab is `Crate`,
Russian grey-green `RoofGreen`, white `Fuel`, light / mid / dark grey `MetalSheet` / `Corrugated` /
`RoofSlate`, yellow HE bands `Hazard`, brown motor bands `LogWood`, the red cluster band `BarrelRed`,
the copper rotating band `Rust`, black tips and nozzles `Undercarriage`, seekers `Glass`, radomes
`Plaster` or `MetalSheet`.

Headless, from the repository root (every model, or the ones whose names contain a filter):
  blender --background --python Tools/blender/mb_munitions.py
  blender --background --python Tools/blender/mb_munitions.py -- hellfire aim9
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import frontier_kit as kit  # noqa: E402

TAU = math.tau
R90 = math.pi / 2
X4 = math.pi / 4  # X (cross at 45 degrees) fin layout; 0 is the + layout

OLIVE = 'Crate'
GREY_GREEN = 'RoofGreen'
WHITE = 'Fuel'
LIGHT_GREY = 'MetalSheet'
MID_GREY = 'Corrugated'
DARK_GREY = 'RoofSlate'
CREAM = 'Plaster'
YELLOW = 'Hazard'
BROWN = 'LogWood'
RED = 'BarrelRed'
COPPER = 'Rust'
BLACK = 'Undercarriage'
STEEL = 'Steel'
GLASS = 'Glass'
GLOW = 'Alloy'
TRACER = 'Lamp'


def inner(r, seg):
    """Radius a little inside a seg-sided lathe of radius r at any angle (fin roots)."""
    return r * math.cos(math.pi / seg) * .97


class Round:
    """A round lying along Y with its nose tip at y = -length / 2. Positions are (r, t, phi): radius from
    the axis, distance t back from the nose tip and the angle phi around the axis from +Z towards +X."""

    def __init__(self, a, length):
        self.a, self.length, self.y0 = a, length, -length / 2

    def at(self, r, t, phi=0.0):
        return Vector((r * math.sin(phi), self.y0 + t, r * math.cos(phi)))

    @staticmethod
    def _face(bm, verts, want):
        f = bm.faces.new(verts)
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
        return f

    def rev(self, name, mat, prof, seg=8, phase=0.0, caps=(True, True), flat=False):
        """Surface of revolution through [(r, t)...] from the nose backwards. A zero radius is a point
        (a tip); caps close a non-zero first / last ring with a flat face. Bands are separate rev calls
        that share their end rings with the body, so nothing hides inside."""
        bm = self.a.part(name, mat, flat=flat).bm
        rings = [[bm.verts.new(self.at(0, t))] if r <= 1e-6 else
                 [bm.verts.new(self.at(r, t, phase + j * TAU / seg)) for j in range(seg)] for r, t in prof]
        for (r0, t0), (r1, t1), ra, rb in zip(prof, prof[1:], rings, rings[1:]):
            if len(ra) == 1 and len(rb) == 1:
                continue
            for j in range(seg):
                k = (j + 1) % seg
                verts = ((ra[0], rb[k], rb[j]) if len(ra) == 1 else (ra[j], ra[k], rb[0]) if len(rb) == 1
                         else (ra[j], ra[k], rb[k], rb[j]))
                phi = phase + (j + .5) * TAU / seg
                # Outward normal of a profile running nose -> tail: (dt radially, -dr along +Y).
                self._face(bm, verts, Vector((math.sin(phi) * (t1 - t0), -(r1 - r0), math.cos(phi) * (t1 - t0))))
        for ring, facing, on in ((rings[0], -1, caps[0]), (rings[-1], 1, caps[1])):
            if on and len(ring) > 2:
                self._face(bm, ring, Vector((0, facing, 0)))
        return self

    def disc(self, name, mat, r, t, seg=8, phase=0.0, facing=1):
        bm = self.a.part(name, mat).bm
        self._face(bm, [bm.verts.new(self.at(r, t, phase + j * TAU / seg)) for j in range(seg)],
                   Vector((0, facing, 0)))

    def motor(self, r_end, t, r_noz, seg=8, phase=0.0, glow=GLOW):
        """Tail face at t: a dark nozzle ring from the body radius r_end in to r_noz around a glowing core."""
        self.rev('Nozzle', BLACK, [(r_end, t), (r_noz, t)], seg, phase, caps=(False, False))
        self.disc('Motor', glow, r_noz, t, seg, phase)

    def plate(self, name, mat, pts, thick=0.0):
        """Double-sided plate over a planar convex polygon (fins, wings, strakes): two opposite sheets with
        their own vertices, `thick` apart (0: coincident, so there is no open edge to see through). The game
        culls back faces, so each side shades and draws on its own."""
        bm = self.a.part(name, mat).bm
        pts = [Vector(p) for p in pts]
        n = Vector((0, 0, 0))
        for p, q in zip(pts, pts[1:] + pts[:1]):  # Newell normal
            n += p.cross(q)
        n.normalize()
        for s in (1, -1):
            self._face(bm, [bm.verts.new(p + n * (s * thick / 2)) for p in pts], n * s)

    def fin(self, name, mat, phi, rt, thick=0.0):
        """Plate through [(r, t)...] in the half-plane at angle phi around the axis."""
        self.plate(name, mat, [self.at(r, t, phi) for r, t in rt], thick)

    def fins(self, name, mat, n, phase, r0, t_le, c_root, span, c_tip, sweep, r1=None, thick=0.0):
        """n trapezoid fins: root chord c_root from t_le at radius r0 (r1 at the root trailing edge on a
        tapering body), the tip chord c_tip `span` further out with its leading edge `sweep` further back."""
        r1 = r0 if r1 is None else r1
        for k in range(n):
            rt = [(r0, t_le), (r0 + span, t_le + sweep)]
            if c_tip > 1e-4:
                rt.append((r0 + span, t_le + sweep + c_tip))
            rt.append((r1, t_le + c_root))
            self.fin(name, mat, phase + k * TAU / n, rt, thick)

    def wrap(self, name, mat, n, phase, r0, t0, chord, span, curl=1.1, nseg=2, thick=0.0):
        """n curved wraparound fins: each leaves the body radially at r0 and curls `curl` radians round
        the axis over its span, from t0 back for `chord`."""
        bm = self.a.part(name, mat).bm
        for k in range(n):
            phi = phase + k * TAU / n
            x, z = r0 * math.sin(phi), r0 * math.cos(phi)
            pts = [(x, z)]
            for s in range(nseg):
                h = phi + curl * (s + .5) / nseg
                x, z = x + math.sin(h) * span / nseg, z + math.cos(h) * span / nseg
                pts.append((x, z))
            for side in (1, -1):
                rows = []
                for i, (x, z) in enumerate(pts):
                    h = phi + curl * i / nseg
                    nx, nz = math.cos(h) * side * thick / 2, -math.sin(h) * side * thick / 2
                    rows.append([bm.verts.new((x + nx, self.y0 + t, z + nz)) for t in (t0, t0 + chord)])
                for i in range(nseg):
                    h = phi + curl * (i + .5) / nseg
                    self._face(bm, (rows[i][0], rows[i + 1][0], rows[i + 1][1], rows[i][1]),
                               Vector((math.cos(h) * side, 0, -math.sin(h) * side)))

    def box(self, name, mat, size, loc, rot=(0, 0, 0)):
        self.a.part(name, mat).box(size, loc=tuple(loc), rot=rot, bevel=0)


# ----------------------------------------------------------------------------- anti-tank missiles
def atgm_tow(a):
    """BGM-71 TOW-2B, 1.51 m with its 540 mm stand-off probe out (152 mm; drawn 1.3 m): olive body, a
    yellow HE band, the flight motor's two side nozzles mid-body, four wings sprung forward behind them,
    four tail control fins in the + layout and the IR beacon glowing at the tail."""
    m, r, s = Round(a, 1.3), .066, 8
    m.rev('Probe', STEEL, [(0, 0), (.024, .004), (.024, .028), (.013, .034), (.013, .30)], 6, caps=(False, False))
    m.rev('Body', OLIVE, [(.022, .29), (.05, .30), (.064, .34), (r, .44)], s, caps=(True, False))
    m.rev('Band', YELLOW, [(r, .44), (r, .47)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .47), (r, 1.27), (.058, 1.30)], s, caps=(False, False))
    m.motor(.058, 1.30, .032, s)
    m.fins('Fins', OLIVE, 4, X4, r * .95, .76, .10, .13, .075, .02)
    m.fins('Fins', OLIVE, 4, 0, r * .95, 1.18, .10, .075, .06, .04)
    for sx in (-1, 1):
        m.box('Nozzles', BLACK, (.03, .055, .04), m.at(r + .004, .66, sx * R90), rot=(0, 0, -sx * .5))


def atgm_kornet(a):
    """9M133 Kornet (1.20 m, 152 mm; drawn 1.3 m): grey-green with a blunt tandem-HEAT nose (the
    precursor charge stands proud of it), two pop-out nose canards, the motor's two oblique nozzles
    behind the warhead and four thin steel tail wings at 45 degrees."""
    m, r, s = Round(a, 1.3), .08, 8
    m.rev('Body', GREY_GREEN, [(0, 0), (.028, .004), (.032, .02), (.032, .10), (.058, .11), (.074, .15), (r, .22),
                               (r, .34)], s, caps=(False, False))
    m.rev('Band', BLACK, [(r, .34), (r, .36)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .36), (r, 1.28), (.074, 1.30)], s, caps=(False, False))
    m.motor(.074, 1.30, .036, s)
    m.fins('Canards', GREY_GREEN, 2, R90, .066, .15, .08, .06, .05, .03, r1=.075)
    m.fins('Wings', STEEL, 4, X4, r * .95, 1.10, .15, .16, .10, .05)
    for sx in (-1, 1):
        m.box('Nozzles', BLACK, (.035, .06, .045), m.at(r + .004, .44, sx * R90), rot=(0, 0, -sx * .45))


def atgm_ataka(a):
    """9M120 Ataka (1.83 m, 130 mm; drawn 1.5 m): slender and grey-green with a pointed ogive, a black
    stencil band, two nose canards and four folding tail fins."""
    m, r, s = Round(a, 1.5), .058, 8
    m.rev('Body', GREY_GREEN, [(0, 0), (.014, .04), (.032, .12), (.047, .21), (r, .34)], s, caps=(False, False))
    m.rev('Band', BLACK, [(r, .34), (r, .37)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .37), (r, 1.47), (.054, 1.50)], s, caps=(False, False))
    m.motor(.054, 1.50, .03, s)
    m.fins('Canards', GREY_GREEN, 2, R90, .046, .22, .08, .05, .045, .025, r1=.054)
    m.fins('Fins', GREY_GREEN, 4, X4, r * .95, 1.30, .15, .09, .11, .04)


def _hellfire(a, nose):
    """AGM-114 (1.63 m, 178 mm; drawn 1.4 m): olive with a yellow HE band and a brown motor band,
    cruciform canards at the front, four long-chord tail wings, and the seeker: 'sal' is the laser
    seeker's faceted glass dome, 'mmw' the Longbow's opaque rounded grey radome."""
    m, r, s = Round(a, 1.4), .077, 8
    if nose == 'sal':
        m.rev('Seeker', GLASS, [(0, 0), (.036, .014), (.062, .048), (.07, .075)], s, caps=(False, False), flat=True)
        m.rev('Body', OLIVE, [(.07, .075), (r, .10), (r, .28)], s, caps=(False, False))
    else:
        m.rev('Radome', LIGHT_GREY, [(0, 0), (.032, .007), (.054, .026), (.069, .058), (r, .10)], s,
              caps=(False, False))
        m.rev('Body', OLIVE, [(r, .10), (r, .28)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .28), (r, .32)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .32), (r, .66)], s, caps=(False, False))
    m.rev('Band_motor', BROWN, [(r, .66), (r, .70)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .70), (r, 1.37), (.07, 1.40)], s, caps=(False, False))
    m.motor(.07, 1.40, .04, s)
    m.fins('Canards', OLIVE, 4, X4, r * .95, .13, .09, .05, .04, .04)
    m.fins('Wings', OLIVE, 4, X4, r * .95, 1.12, .24, .07, .11, .12)


def hellfire(a):
    _hellfire(a, 'sal')


def hellfire_longbow(a):
    _hellfire(a, 'mmw')


def griffin(a):
    """AGM-176 Griffin (1.10 m, 140 mm; drawn 1.0 m): grey with a rounded glass seeker in a dark
    collar, a yellow band, small pop-out canards and four small pop-out tail fins."""
    m, r, s = Round(a, 1.0), .064, 8
    m.rev('Seeker', GLASS, [(0, 0), (.028, .006), (.048, .024), (.058, .05)], s, caps=(False, False))
    m.rev('Collar', BLACK, [(.058, .05), (r, .07)], s, caps=(False, False))
    m.rev('Body', LIGHT_GREY, [(r, .07), (r, .22)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .22), (r, .25)], s, caps=(False, False))
    m.rev('Body', LIGHT_GREY, [(r, .25), (r, .97), (.058, 1.0)], s, caps=(False, False))
    m.motor(.058, 1.0, .032, s)
    m.fins('Canards', LIGHT_GREY, 4, X4, r * .95, .10, .06, .035, .035, .02)
    m.fins('Fins', LIGHT_GREY, 4, X4, r * .95, .84, .12, .055, .07, .04)


def mam_l(a):
    """Roketsan MAM-L (about 1.0 m x 160 mm): a fat little glide bomb with a laser seeker, cruciform
    nose canards, a yellow band, a boat tail and four swept tail fins. No motor."""
    m, s = Round(a, 1.0), 8
    m.rev('Seeker', GLASS, [(0, 0), (.022, .005), (.036, .018), (.042, .035)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(.042, .035), (.062, .085), (.077, .16), (.085, .25)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(.085, .25), (.085, .28)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(.085, .28), (.085, .68), (.072, .82), (.05, .93), (.03, 1.0)], s, caps=(False, True))
    m.fins('Canards', MID_GREY, 4, X4, .055, .10, .08, .045, .05, .025, r1=.07)
    m.fins('Fins', MID_GREY, 4, X4, .07, .78, .18, .08, .10, .10, r1=.038)


# ----------------------------------------------------------------------------- MANPADS and SHORAD
def _manpads(a, spike):
    """MANPADS dart (1.52-1.57 m, 70 mm; drawn 1.3 m), thickened a little so it reads. Stinger:
    olive, a faceted IR dome, four tiny canards, a yellow band and four folding tail fins. Igla:
    grey-green, a rounded dome behind a needle aerospike and one pair of canards."""
    m, r, s = Round(a, 1.3), .037, 8
    if spike:
        body, t0, n = GREY_GREEN, .10, 2
        m.rev('Spike', STEEL, [(0, 0), (.004, .03), (.006, t0)], 4, caps=(False, False))
        m.rev('Seeker', GLASS, [(.006, t0), (.02, t0 + .006), (.03, t0 + .018), (.034, t0 + .034)], s,
              caps=(True, False))
    else:
        body, t0, n = OLIVE, 0.0, 4
        m.rev('Seeker', GLASS, [(0, 0), (.02, .014), (.034, .034)], s, caps=(False, False), flat=True)
    m.rev('Body', body, [(.034, t0 + .034), (r, t0 + .05), (r, .24)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .24), (r, .265)], s, caps=(False, False))
    m.rev('Body', body, [(r, .265), (r, 1.28), (.034, 1.30)], s, caps=(False, False))
    m.motor(.034, 1.30, .02, s)
    m.fins('Canards', body, n, X4 if n == 4 else R90, r * .95, t0 + .07, .05, .024, .025, .02)
    m.fins('Fins', body, 4, X4, r * .95, 1.17, .11, .045, .07, .04)


def stinger(a):
    _manpads(a, spike=False)


def igla(a):
    _manpads(a, spike=True)


def shorad_dart(a):
    """Tunguska 9M311 / Pantsir 57E6 two-stage missile (2.56-3.16 m; drawn 2.2 m), grey-green: a
    slim dart sustainer (pointed nose, canards, small tail fins) on a fat booster with four big fins
    that drops away, joined by a dark interstage cone."""
    m, rd, rb, s = Round(a, 2.2), .036, .066, 8
    m.rev('Dart', GREY_GREEN, [(0, 0), (.008, .05), (.02, .14), (.031, .26), (rd, .34), (rd, .44)], s,
          caps=(False, False))
    m.rev('Band', BLACK, [(rd, .44), (rd, .46)], s, caps=(False, False))
    m.rev('Dart', GREY_GREEN, [(rd, .46), (rd, 1.38)], s, caps=(False, False))
    m.rev('Interstage', BLACK, [(rd, 1.38), (.052, 1.42), (rb, 1.46)], s, caps=(False, False))
    m.rev('Booster', GREY_GREEN, [(rb, 1.46), (rb, 2.17), (.06, 2.2)], s, caps=(False, False))
    m.motor(.06, 2.2, .038, s)
    m.fins('Canards', GREY_GREEN, 4, X4, .031, .28, .08, .038, .04, .03, r1=rd * .95)
    m.fins('Fins', GREY_GREEN, 4, X4, rd * .95, 1.22, .14, .05, .08, .05)
    m.fins('Fins', GREY_GREEN, 4, X4, rb * .95, 1.95, .22, .08, .14, .06)


# ----------------------------------------------------------------------------- air-to-air missiles
def aim9(a):
    """AIM-9M Sidewinder (3.02 m, 127 mm; drawn 2.2 m, thickened a little): white with a glass IR dome
    in a grey seeker section, delta canards, yellow warhead and brown motor bands, and four tail wings
    with a rolleron wheel in each tip."""
    m, r, s = Round(a, 2.2), .055, 8
    m.rev('Seeker', GLASS, [(0, 0), (.026, .007), (.044, .026), (.052, .05)], s, caps=(False, False))
    m.rev('Seeker_section', LIGHT_GREY, [(.052, .05), (r, .07), (r, .20)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .20), (r, .50)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .50), (r, .54)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .54), (r, .92)], s, caps=(False, False))
    m.rev('Band_motor', BROWN, [(r, .92), (r, .95)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .95), (r, 2.18), (.05, 2.2)], s, caps=(False, False))
    m.motor(.05, 2.2, .03, s)
    m.fins('Canards', WHITE, 4, X4, r * .95, .22, .16, .075, .02, .12)
    t_le, c0, span, c1, sw = 1.86, .30, .15, .10, .18
    m.fins('Wings', WHITE, 4, X4, r * .95, t_le, c0, span, c1, sw)
    rt, tt = r * .95 + span - .02, t_le + sw + c1 - .022
    for k in range(4):  # rolleron wheels in the plane of each wing tip
        m.fin('Rollerons', STEEL, X4 + k * R90,
              [(rt - .018, tt), (rt, tt - .018), (rt + .018, tt), (rt, tt + .018)], thick=.005)


def r60(a):
    """R-60 (AA-8; 2.09 m, 120 mm; drawn 1.6 m): light grey, a small glass dome ringed by four tiny
    destabilisers on the very nose, cruciform canards, a dark joint band and big cropped-delta tail fins."""
    m, r, s = Round(a, 1.6), .053, 8
    m.rev('Seeker', GLASS, [(0, 0), (.02, .006), (.034, .022), (.04, .04)], s, caps=(False, False))
    m.rev('Body', LIGHT_GREY, [(.04, .04), (.05, .08), (r, .14), (r, .40)], s, caps=(False, False))
    m.rev('Band', BLACK, [(r, .40), (r, .42)], s, caps=(False, False))
    m.rev('Body', LIGHT_GREY, [(r, .42), (r, 1.57), (.048, 1.6)], s, caps=(False, False))
    m.motor(.048, 1.6, .03, s)
    m.fins('Destabilisers', LIGHT_GREY, 4, 0, .036, .045, .04, .022, 0, .035, r1=.046)
    m.fins('Canards', LIGHT_GREY, 4, X4, r * .95, .17, .12, .06, .03, .07)
    m.fins('Fins', LIGHT_GREY, 4, X4, r * .95, 1.22, .34, .14, .10, .22)


def aim120(a):
    """AIM-120C AMRAAM (3.65 m, 178 mm; drawn 2.6 m): white with an opaque grey ogive radome, yellow
    and brown bands, clipped-delta mid-body wings and four tail control fins behind them."""
    m, r, s = Round(a, 2.6), .07, 8
    m.rev('Radome', LIGHT_GREY, [(0, 0), (.012, .03), (.032, .10), (.05, .19), (.063, .28), (r, .36)], s,
          caps=(False, False))
    m.rev('Body', WHITE, [(r, .36), (r, .60)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .60), (r, .64)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .64), (r, 1.36)], s, caps=(False, False))
    m.rev('Band_motor', BROWN, [(r, 1.36), (r, 1.40)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, 1.40), (r, 2.57), (.064, 2.6)], s, caps=(False, False))
    m.motor(.064, 2.6, .036, s)
    m.fins('Wings', WHITE, 4, X4, r * .95, 1.02, .30, .085, .05, .22)
    m.fins('Fins', WHITE, 4, X4, r * .95, 2.28, .26, .10, .08, .16)


# ----------------------------------------------------------------------------- surface-to-air missiles
def patriot(a):
    """MIM-104 Patriot PAC-2 (5.3 m, 410 mm; drawn 3.4 m, a little slimmer): a white canister-launched
    cylinder with a blunt cream radome, yellow and brown bands and four small clipped-delta tail fins."""
    m, r, s = Round(a, 3.4), .12, 10
    m.rev('Radome', CREAM, [(0, 0), (.045, .015), (.088, .07), (.112, .17), (r, .30)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .30), (r, .95)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .95), (r, 1.0)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, 1.0), (r, 1.9)], s, caps=(False, False))
    m.rev('Band_motor', BROWN, [(r, 1.9), (r, 1.95)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, 1.95), (r, 3.4)], s, caps=(False, False))
    m.motor(r, 3.4, .08, s)
    m.fins('Fins', WHITE, 4, X4, inner(r, s), 2.92, .46, .15, .12, .30)


def buk(a):
    """Buk 9M38 (5.55 m, 400 mm; drawn 3.6 m): white with a pointed light-grey radome, an olive band,
    long-chord cruciform wings over the middle and four tail control fins."""
    m, r, s = Round(a, 3.6), .13, 10
    m.rev('Radome', LIGHT_GREY, [(0, 0), (.012, .05), (.045, .18), (.08, .34), (.108, .50), (r, .66)], s,
          caps=(False, False))
    m.rev('Body', WHITE, [(r, .66), (r, 1.0)], s, caps=(False, False))
    m.rev('Band', OLIVE, [(r, 1.0), (r, 1.12)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, 1.12), (r, 3.56), (.12, 3.6)], s, caps=(False, False))
    m.motor(.12, 3.6, .075, s)
    m.fins('Wings', LIGHT_GREY, 4, X4, inner(r, s), 1.30, 1.05, .15, .50, .45)
    m.fins('Fins', LIGHT_GREY, 4, X4, inner(r, s), 3.02, .50, .19, .22, .26)


# ----------------------------------------------------------------------------- air-to-ground
def maverick(a):
    """AGM-65 Maverick (2.49 m, 305 mm; drawn 2.0 m): a fat white body behind a big glass TV/IR dome in
    a grey seeker ring, yellow and brown bands, long-chord delta wings and four tail fins."""
    m, r, s = Round(a, 2.0), .1225, 8
    m.rev('Seeker', GLASS, [(0, 0), (.05, .01), (.086, .036), (.108, .07), (.116, .10)], s, caps=(False, False))
    m.rev('Seeker_ring', LIGHT_GREY, [(.116, .10), (r, .12), (r, .18)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .18), (r, .40)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .40), (r, .45)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .45), (r, .80)], s, caps=(False, False))
    m.rev('Band_motor', BROWN, [(r, .80), (r, .84)], s, caps=(False, False))
    m.rev('Body', WHITE, [(r, .84), (r, 1.96), (.112, 2.0)], s, caps=(False, False))
    m.motor(.112, 2.0, .06, s)
    m.fins('Wings', WHITE, 4, X4, r * .95, .72, .98, .17, .06, .90)
    m.fins('Fins', WHITE, 4, X4, r * .95, 1.74, .22, .12, .10, .10)


def kh29l(a):
    """Kh-29L (3.9 m, 380 mm; drawn at half size, 1.95 m, thickened 15 %): the laser-guided Kh-29 (prompt 25 B3: the
    Su-25's heavy missile, flying the Maverick until now). A blunt glass seeker dome in a steel ring, four small delta
    canards just behind it, a long fat grey-green body with a yellow warhead band and a brown motor band, and the big
    cruciform trapezoid wings at the tail that make the Kh-29 read from any side; the motor glows in the tail."""
    m, r, s = Round(a, 1.95), .11, 8
    m.rev('Seeker', GLASS, [(0, 0), (.045, .01), (.078, .035), (.094, .065)], s, caps=(False, False))
    m.rev('Seeker_ring', STEEL, [(.094, .065), (.1, .09), (.1, .12)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.1, .12), (r, .2), (r, .52)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .52), (r, .58)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .58), (r, 1.12)], s, caps=(False, False))
    m.rev('Band_motor', BROWN, [(r, 1.12), (r, 1.17)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, 1.17), (r, 1.9), (.1, 1.95)], s, caps=(False, False))
    m.motor(.1, 1.95, .065, s)
    m.fins('Canards', GREY_GREEN, 4, X4, inner(r, s), .2, .26, .1, .02, .2)
    m.fins('Wings', GREY_GREEN, 4, X4, inner(r, s), 1.28, .56, .24, .26, .2)


def gbu39(a):
    """GBU-39 Small Diameter Bomb (1.8 m, 190 mm; drawn at half size, 0.9 m, thickened a quarter): a slim grey glide
    bomb with a pointed steel nose, a yellow band, the Diamond Back wings folded flat along its back (a long plate on a
    spine: how it hangs on the rack and falls for the first moment), and a ring of small tail fins. No motor."""
    m, r, s = Round(a, .9), .06, 8
    m.rev('Nose', STEEL, [(0, 0), (.02, .03), (.04, .08)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(.04, .08), (r, .18), (r, .3)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .3), (r, .33)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(r, .33), (r, .74), (.045, .86), (.03, .9)], s, caps=(False, True))
    m.box('Wing_spine', DARK_GREY, (.05, .44, .03), m.at(r + .005, .5))
    m.box('Wings', DARK_GREY, (.16, .5, .014), m.at(r + .03, .5))
    m.fins('Fins', MID_GREY, 4, X4, inner(r, s), .72, .14, .07, .06, .06, r1=.045)
    _lugs(m, r, (.36, .62))


def jassm(a):
    """AGM-158 JASSM (4.27 m x 0.55 wide x 0.45 high; drawn 3.0 m), dark grey and faceted: a trapezoid
    body with a chine, a chisel nose, the straight wing folded out on top, one vertical tail fin, the
    flush intake under the belly and the turbojet's small exhaust."""
    h = 1.5

    def sec(y, wb, wt, z0, z1):  # flat belly, chine low on the flank, sides sloping in to a flat back
        zc, wc = z0 + (z1 - z0) * .25, wb * 1.08
        return [(-wb, y, z0), (wb, y, z0), (wc, y, zc), (wt, y, z1), (-wt, y, z1), (-wc, y, zc)]
    a.part('Body', DARK_GREY, flat=True).loft([
        sec(-h, .09, .07, -.11, -.08), sec(-1.15, .17, .10, -.135, .04), sec(-.75, .195, .11, -.14, .14),
        sec(1.1, .195, .11, -.14, .14), sec(h, .12, .07, -.09, .06)], bevel=0)
    a.part('Wing', DARK_GREY).prism([(-.845, -.03), (0, -.07), (.845, -.03), (.845, .10), (0, .15), (-.845, .10)],
                                   .02, loc=(0, -.05, .15), axis='Z', bevel=0)
    a.part('Tail_fin', DARK_GREY).prism([(1.0, .12), (1.28, .33), (1.46, .33), (1.45, .055)], .02, bevel=0)
    a.part('Intake', BLACK).box((.16, .42, .03), loc=(0, .5, -.145), bevel=0)
    a.part('Exhaust', BLACK).box((.14, .01, .07), loc=(0, h + .003, -.015), bevel=0)
    a.part('Motor', GLOW).box((.1, .01, .04), loc=(0, h + .006, -.015), bevel=0)


# ----------------------------------------------------------------------------- rockets
def hydra(a):
    """Hydra 70 (1.06 m, 70 mm; drawn 1.0 m, thickened): olive with a pointed HE warhead, a yellow band
    and four curved wraparound fins at the tail."""
    m, r, s = Round(a, 1.0), .04, 6
    m.rev('Body', OLIVE, [(0, 0), (.016, .06), (.032, .16), (r, .25)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .25), (r, .29)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .29), (r, .97), (.036, 1.0)], s, caps=(False, False))
    m.motor(.036, 1.0, .024, s)
    m.wrap('Fins', OLIVE, 4, X4, inner(r, s), .88, .10, .065, curl=1.2)


def s8(a):
    """S-8 (1.57 m, 80 mm; drawn 1.2 m, thickened): grey-green with a pointed nose, a black stencil band
    and six narrow flip-out tail fins swept back behind the nozzle."""
    m, r, s = Round(a, 1.2), .038, 6
    m.rev('Body', GREY_GREEN, [(0, 0), (.01, .04), (.026, .12), (r, .22)], s, caps=(False, False))
    m.rev('Band', BLACK, [(r, .22), (r, .24)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .24), (r, 1.15), (.034, 1.17)], s, caps=(False, False))
    m.motor(.034, 1.17, .024, s)
    m.fins('Fins', GREY_GREEN, 6, 0, .03, 1.10, .035, .06, .03, .065)


def _grad(a, band, split):
    """BM-21 Grad 9M22U (2.87 m, 122 mm; drawn 2.2 m): grey-green with a steel fuze on a pointed
    ogive, a coloured band (yellow HE, red cluster) and four curved wraparound fins. split draws the
    cluster warhead's dark nose seam."""
    m, r, s = Round(a, 2.2), .052, 6
    m.rev('Fuze', STEEL, [(0, 0), (.012, .05)], s, caps=(False, False))
    if split:
        m.rev('Body', GREY_GREEN, [(.012, .05), (.034, .18)], s, caps=(False, False))
        m.rev('Seam', BLACK, [(.034, .18), (.037, .195)], s, caps=(False, False))
        m.rev('Body', GREY_GREEN, [(.037, .195), (r, .38)], s, caps=(False, False))
    else:
        m.rev('Body', GREY_GREEN, [(.012, .05), (.038, .20), (r, .38)], s, caps=(False, False))
    m.rev('Band', band, [(r, .38), (r, .44)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(r, .44), (r, 2.17), (.048, 2.2)], s, caps=(False, False))
    m.motor(.048, 2.2, .03, s)
    m.wrap('Fins', GREY_GREEN, 4, X4, inner(r, s), 2.05, .13, .075, curl=1.1)


def grad(a):
    _grad(a, YELLOW, split=False)


def grad_cluster(a):
    _grad(a, RED, split=True)


def rocket_107(a):
    """107 mm Type 63 rocket (about 0.84 m; drawn 0.9 m): short, olive and finless (it is spun by
    canted nozzles), with a blunt fuzed nose and a yellow band."""
    m, r, s = Round(a, .9), .057, 8
    m.rev('Fuze', STEEL, [(0, 0), (.012, .004), (.014, .035)], 6, caps=(False, False))
    m.rev('Body', OLIVE, [(.016, .035), (.045, .09), (r, .19)], s, caps=(True, False))
    m.rev('Band', YELLOW, [(r, .19), (r, .22)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .22), (r, .9)], s, caps=(False, False))
    m.motor(r, .9, .036, s)


def gmlrs(a):
    """GMLRS M31 (3.94 m, 227 mm; drawn 2.8 m): olive guided rocket with a pointed nose, four nose
    canards, a yellow band and four folding tail fins."""
    m, r, s = Round(a, 2.8), .081, 8
    m.rev('Body', OLIVE, [(0, 0), (.048, .19), (r, .44), (r, .70)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(r, .70), (r, .75)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .75), (r, 2.8)], s, caps=(False, False))
    m.motor(r, 2.8, .05, s)
    m.fins('Canards', OLIVE, 4, X4, r * .95, .48, .12, .07, .09, .03, r1=r * .95)
    m.fins('Fins', OLIVE, 4, X4, r * .95, 2.54, .24, .11, .18, .05)


def tos_rocket(a):
    """TOS-1A thermobaric rocket (about 3.3 m, 220 mm; drawn 2.4 m): olive, short, with a fat bulbous
    warhead wider than the motor tube and four wraparound tail fins."""
    m, rw, r, s = Round(a, 2.4), .092, .074, 8
    m.rev('Body', OLIVE, [(0, 0), (.05, .06), (.084, .17), (rw, .31), (r, .50), (r, 2.4)], s, caps=(False, False))
    m.motor(r, 2.4, .045, s)
    m.wrap('Fins', OLIVE, 4, X4, inner(r, s), 2.24, .15, .09, curl=1.1)


# ----------------------------------------------------------------------------- bombs
def _lugs(m, r, ts, mat=STEEL):
    for t in ts:
        m.box('Lugs', mat, (.045, .08, .05), m.at(r + .012, t))


def bomb_mk84(a):
    """Mk 84 2,000 lb bomb (3.84 m, 460 mm; drawn 2.7 m as the game's Mk 82 stretched 1.7 times):
    olive with a steel fuze, a yellow nose band, a boat tail with four swept conical-assembly fins and
    two suspension lugs."""
    m, r, s = Round(a, 2.7), .27, 8
    m.rev('Fuze', STEEL, [(0, 0), (.03, .006), (.036, .05)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(.07, .05), (.15, .18), (.21, .34)], s, caps=(True, False))
    m.rev('Band', YELLOW, [(.21, .34), (.236, .42)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(.236, .42), (r, .72), (r, 1.75), (.225, 2.08), (.14, 2.42), (.09, 2.62)], s,
          caps=(False, True))
    m.fins('Fins', OLIVE, 4, X4, .215, 2.02, .60, .19, .30, .38, r1=.085)
    _lugs(m, r, (1.05, 1.45))


def bomb_fab(a):
    """FAB-500 M-62 (2.4 m, 400 mm; drawn 1.8 m): grey-green with a blunt fuzed ogive, a cylindrical
    body, a tail cone carrying four fins inside a ring (box) tail, and two lugs."""
    m, r, s = Round(a, 1.8), .15, 8
    m.rev('Fuze', STEEL, [(0, 0), (.02, .005), (.024, .04)], 6, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.05, .04), (.12, .15), (r, .34), (r, 1.25), (.12, 1.45), (.07, 1.62), (.055, 1.66)],
          s, caps=(True, True))
    R, th, t0, t1 = .19, .012, 1.52, 1.8
    m.rev('Ring_tail', GREY_GREEN, [(R, t0), (R, t1), (R - th, t1), (R - th, t0), (R, t0)], s, X4,
          caps=(False, False))
    for k in range(4):
        m.fin('Fins', GREY_GREEN, X4 + k * R90, [(.115, 1.40), (R - th * .5, t0), (R - th * .5, t1), (.05, 1.66)])
    _lugs(m, r, (.62, 1.0))


def gbu12(a):
    """GBU-12 Paveway II (3.27 m, 273 mm; drawn 2.2 m, thickened): a laser seeker ball in a steel
    gimbal collar, the olive guidance section with four big nose canards, the Mk 82 body with a yellow
    band and four big pop-out rear wings on the tail adaptor."""
    m, r, s = Round(a, 2.2), .11, 8
    m.rev('Seeker', GLASS, [(0, 0), (.035, .012), (.052, .045), (.048, .07)], s, caps=(False, False))
    m.rev('Collar', STEEL, [(.048, .07), (.067, .095), (.062, .125)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(.062, .125), (.062, .34), (.09, .42), (.106, .52)], s, caps=(False, False))
    m.rev('Band', YELLOW, [(.106, .52), (r, .58)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .58), (r, 1.46), (.09, 1.66), (.068, 1.78), (.066, 2.16)], s, caps=(False, True))
    m.fins('Canards', OLIVE, 4, X4, .06, .15, .19, .075, .10, .05)
    m.fins('Wings', OLIVE, 4, X4, .063, 1.88, .28, .30, .26, .06)


def jdam(a):
    """GBU-31 JDAM (Mk 84 with the JDAM kit, 3.88 m; drawn 2.7 m): a grey Mk 84 body with a yellow nose
    band, the strake kit's strap and two side strakes mid-body, and the JDAM tail kit's long cone with
    four control fins; two lugs."""
    m, r, s = Round(a, 2.7), .27, 8
    m.rev('Fuze', STEEL, [(0, 0), (.03, .006), (.036, .05)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(.07, .05), (.15, .18), (.21, .34)], s, caps=(True, False))
    m.rev('Band', YELLOW, [(.21, .34), (.236, .42)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(.236, .42), (r, .72), (r, 1.10)], s, caps=(False, False))
    m.rev('Strap', LIGHT_GREY, [(r, 1.10), (r, 1.16)], s, caps=(False, False))
    m.rev('Body', MID_GREY, [(r, 1.16), (r, 1.80)], s, caps=(False, False))
    m.rev('Tail_kit', LIGHT_GREY, [(r, 1.80), (.242, 2.1), (.165, 2.62), (.15, 2.7)], s,
          caps=(False, True))
    m.fins('Fins', LIGHT_GREY, 4, X4, .222, 2.22, .40, .17, .20, .24, r1=.17)
    for sx in (-1, 1):
        m.fin('Strakes', LIGHT_GREY, sx * R90, [(r * .97, 1.12), (r + .075, 1.30), (r + .075, 1.56), (r * .97, 1.64)])
    _lugs(m, r, (.95, 1.40))


# ----------------------------------------------------------------------------- loitering munitions
def lancet(a):
    """ZALA Lancet-3 (about 1.65 m long and across; drawn 1.4 m): a grey tube with a blunt camera
    nose, two tandem cruciform X-wings of long narrow panels and a small pusher propeller."""
    m, r, s = Round(a, 1.4), .05, 8
    m.rev('Camera', GLASS, [(0, 0), (.026, .005), (.04, .022)], s, caps=(False, False))
    m.rev('Body', LIGHT_GREY, [(.04, .022), (r, .06), (r, 1.20), (.04, 1.30), (.022, 1.33)], s, caps=(False, True))
    m.rev('Spinner', BLACK, [(.02, 1.33), (.016, 1.37), (0, 1.40)], 6, caps=(True, False))
    m.fins('Wings', MID_GREY, 4, X4, r * .95, .30, .11, .58, .08, .02)
    m.fins('Wings', MID_GREY, 4, X4, r * .95, 1.02, .13, .58, .10, .02)
    m.box('Propeller_blades', BLACK, (.34, .012, .035), m.at(0, 1.355), rot=(0, 0, 0))


def shahed(a):
    """HESA Shahed-136 (3.5 m long, 2.5 m span; drawn 2.6 m x 1.9 m): a light grey fuselage with a
    pointed warhead, the white cropped-delta wing low on it, vertical fins over and under each wing
    tip, the engine fairing and a two-blade pusher propeller on a dark spinner."""
    m, r, s = Round(a, 2.6), .11, 8
    m.rev('Body', LIGHT_GREY, [(0, 0), (.032, .05), (.07, .15), (.098, .30), (r, .45), (r, 2.22), (.09, 2.36),
                               (.06, 2.44)], s, caps=(False, True))
    m.rev('Spinner', BLACK, [(.05, 2.44), (.04, 2.52), (0, 2.6)], 6, caps=(True, False))
    y = m.y0
    a.part('Wing', WHITE).prism([(0, y + .75), (.95, y + 1.72), (.95, y + 2.2), (-.95, y + 2.2), (-.95, y + 1.72)], .03,
                                loc=(0, 0, -.03), axis='Z', bevel=0)
    for sx in (-1, 1):
        a.part('Winglets', LIGHT_GREY).prism([(y + 1.70, -.02), (y + 1.92, .22), (y + 2.16, .22), (y + 2.22, -.02),
                                              (y + 2.14, -.11), (y + 1.86, -.11)], .02, loc=(sx * .95, 0, 0), bevel=0)
    a.part('Propeller_blades', BLACK).box((.58, .015, .05), loc=m.at(0, 2.46), rot=(0, .5, 0), bevel=0)


# ----------------------------------------------------------------------------- tank rounds and shells
def apfsds(a):
    """120 mm APFSDS long-rod penetrator in flight (M829: rod 0.73 m x 25 mm; drawn 1.0 m, thickened):
    a dark rod behind a steel ballistic tip, six small aluminium fins and a bright tracer in the base."""
    m, r, s = Round(a, 1.0), .022, 6
    m.rev('Tip', STEEL, [(0, 0), (.008, .05), (.016, .12)], s, caps=(False, False))
    m.rev('Rod', BLACK, [(.016, .12), (r, .20), (r, .95), (.018, 1.0)], s, caps=(False, False))
    m.motor(.018, 1.0, .013, s, glow=TRACER)
    m.fins('Fins', STEEL, 6, 0, r * .9, .82, .16, .036, .10, .06, r1=.017)


def heat_round(a):
    """Tank HEAT round (M830 / 3BK lineage; drawn 0.9 m): olive with a flat black spike tip on a
    stand-off probe, a conical shaped-charge head, a slim tail boom with four fins and a tracer."""
    m, s = Round(a, .9), 6
    m.rev('Tip', BLACK, [(0, 0), (.02, .003), (.02, .025), (.011, .03)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(.011, .03), (.011, .18), (.062, .40), (.062, .55), (.025, .64), (.024, .9)], s,
          caps=(False, False))
    m.motor(.024, .9, .016, s, glow=TRACER)
    m.fins('Fins', OLIVE, 4, X4, .021, .74, .16, .045, .10, .06)


def shell_155(a):
    """155 mm M795 HE shell (0.86 m; drawn 1.1 m, the game scales it for 105 / 203 mm): olive ogive with
    a steel fuze, a yellow band, the copper rotating band and a boat tail."""
    m, r, s = Round(a, 1.1), .099, 8
    m.rev('Fuze', STEEL, [(0, 0), (.016, .03), (.026, .11)], 6, caps=(False, False))
    m.rev('Body', OLIVE, [(.028, .11), (.07, .25), (r, .48)], s, caps=(True, False))
    m.rev('Band', YELLOW, [(r, .48), (r, .53)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .53), (r, .88)], s, caps=(False, False))
    m.rev('Rotating_band', COPPER, [(r, .88), (r, .93)], s, caps=(False, False))
    m.rev('Body', OLIVE, [(r, .93), (.084, 1.1)], s, caps=(False, True))


def mortar_bomb(a):
    """240 mm mortar bomb (about 1.5 m; drawn 0.9 m, the game scales it for 120 mm): a grey-green
    teardrop with a steel fuze, dark obturating rings at its widest, a tail boom and six fins."""
    m, s = Round(a, .9), 6
    m.rev('Fuze', STEEL, [(0, 0), (.012, .01), (.018, .055)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.018, .055), (.058, .12), (.075, .23)], s, caps=(False, False))
    m.rev('Obturator', BLACK, [(.075, .23), (.075, .27)], s, caps=(False, False))
    m.rev('Body', GREY_GREEN, [(.075, .27), (.056, .43), (.024, .58)], s, caps=(False, True))
    m.rev('Boom', GREY_GREEN, [(.022, .58), (.022, .9)], 6, caps=(False, True))
    m.fins('Fins', GREY_GREEN, 6, 0, .018, .72, .17, .05, .15, .02)


def rail_slug(a):
    """Railgun hyper-velocity projectile (flight body 0.61 m; drawn 0.9 m): a slim bare-metal dart with
    a long pointed nose, a small cruciform tail and a white-hot base."""
    m, r, s = Round(a, .9), .03, 6
    m.rev('Body', STEEL, [(0, 0), (.01, .08), (.024, .26), (r, .40), (r, .80), (.024, .88)], s, caps=(False, False))
    m.motor(.024, .88, .017, s, glow=TRACER)
    m.fins('Fins', STEEL, 4, X4, inner(r, s), .74, .14, .03, .09, .07, r1=.02)


# name: (builder, Asset options). They all fly: no ground occlusion or grime.
BUILDERS = {name: (fn, dict(ao_distance=ao, ground=False)) for name, fn, ao in (
    ('atgm_tow', atgm_tow, .12), ('atgm_kornet', atgm_kornet, .12), ('atgm_ataka', atgm_ataka, .12),
    ('hellfire', hellfire, .12), ('hellfire_longbow', hellfire_longbow, .12), ('griffin', griffin, .1),
    ('mam_l', mam_l, .12), ('stinger', stinger, .08), ('igla', igla, .08), ('shorad_dart', shorad_dart, .12),
    ('aim9', aim9, .15), ('r60', r60, .12), ('aim120', aim120, .15), ('patriot', patriot, .25), ('buk', buk, .3),
    ('maverick', maverick, .2), ('kh29l', kh29l, .2), ('gbu39', gbu39, .12), ('jassm', jassm, .3), ('hydra', hydra, .08), ('s8', s8, .08), ('grad', grad, .12),
    ('grad_cluster', grad_cluster, .12), ('rocket_107', rocket_107, .08), ('gmlrs', gmlrs, .15),
    ('tos_rocket', tos_rocket, .15), ('bomb_mk84', bomb_mk84, .3), ('bomb_fab', bomb_fab, .2), ('gbu12', gbu12, .25),
    ('jdam', jdam, .3), ('lancet', lancet, .2), ('shahed', shahed, .3), ('apfsds', apfsds, .06),
    ('heat_round', heat_round, .08), ('shell_155', shell_155, .1), ('mortar_bomb', mortar_bomb, .08),
    ('rail_slug', rail_slug, .06),
)}

OUT = HERE.parents[1] / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'


def build(filters=(), out=OUT):
    """Build and export the munitions whose names contain one of the filters (all without filters)."""
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o)
    root = kit.workspace()
    kit.clear_workspace(root)
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, (fn, options) in BUILDERS.items():
        if filters and not any(f in name for f in filters):
            continue
        asset = kit.Asset(name, root, **options)
        fn(asset)
        asset.finish()
        asset.export(out / f'{name}.glb')
        counts[name] = asset.triangles()
        print(f'BUILT {name}: {counts[name]} triangles')
        kit.clear_workspace(root)
    return counts


if __name__ == '__main__':
    build(tuple(sys.argv[sys.argv.index('--') + 1:]) if '--' in sys.argv else ())
    print('MB_MUNITIONS_COMPLETE')
