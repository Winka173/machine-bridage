"""Play-test 14 model wave M7 (lane A): both Icarus redrawn (owner 04/10: "vẽ lại 2 boss icarus luôn"), at 3.5 x the boss
budget, no size change. Spec: Docs/cloud/PT14_CLOUD_TASKS.md session 4; DECISIONS "Play-test 14 model wave M7 (lane A)".

- silver_bug (Icarus, Aurel's orbital warship; bossfile: "a dagger of a hull, a stepped superstructure under its command
  tower and a bank of engines across the stern"): a lifting-body dagger read from the real spaceplanes (the Shuttle /
  Buran orbiters, the X-37B): silver plated upper hull in three tones with panel lines, black reusable-surface tiles on
  the belly (their gap grid and replaced tiles), grey reinforced-carbon nose cap and chine leading edges, the body flap
  under the engines, forward RCS pods on canards, OMS-style nacelles with their own engines on pylons, a bank of five
  regeneratively cooled main engines (bells with cooling bands, powerheads, turbopumps, gimbal actuators) on the
  thrust structure, ISS-style radiator wings and a half-sunk pressurised module with MMOD bands, the docking port; the
  warship on top: a three-tier stepped superstructure under the command tower with the bridge, the satellite uplink dish
  (Uplink), the APS emitter on the mast (Mount_APS).
  Weapons, every round from a barrel or emitter with its Muzzle_* at the mouth: the ventral main laser (Turret >
  Muzzle_main), two heavy coilguns on the shoulders (Mount_gun / .001: rails, coil rings, capacitor banks, Muzzle_gun at
  the mouth), two beam-director laser turrets (Mount_gun.002 / .003, mounts 3 and 4: p26_icarus_direct_ic_laser), two
  twin 40 mm turrets on the flank sponsons (Mount_gun.004 / .005: the crash turrets, mounts 5 and 6, per-barrel
  Muzzle_b1 / _b2), two point-defence lasers (Pd_laser_l / _r), the drop-pod bay (Pod_bay > Muzzle_missile). The view
  gives a slot's k-th mount the k-th Mount_<slot> by name, so six gun mounts need six Mount_gun pivots (the old model
  had four: mounts 3, 4 fired lasers out of the 40 mm turrets and 5, 6 their 40 mm out of the coilguns); data part
  nodes moved with it (CHANGES "Play-test 14 model wave M7").
- icarus_mk0 (Icarus Mk.0, the unfinished prototype; its own model now, it drew silver_bug's): the same dagger at the same
  length, built as a test article: primer and bare panels with open bays showing the stringers, half the belly tiled,
  strap-on propellant tanks instead of the nacelles, three big engines on an open thrust frame, the scaffolded command
  tower with a temporary cabin, calibration targets and test markings, the nose air-data boom; its three parts at
  silver_bug's places (main laser Turret, Pod_bay, Pd_laser_l), the right point-defence station an empty capped ring.
- Engine flames (owner: Daedalus "nên có lửa sau động cơ"): every nozzle that burns carries an `Engine_flame` empty on its
  exit plane (mb_kit35.engine_flame: scale = exit radius); the runtime draws the flame (EngineFlames.cs).

Metres, +Z up, -Y front, +X left. Every runtime node keeps its old place unless CHANGES lists it.
"""
import math
import random

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W5

R90 = math.pi / 2
TAU = math.tau


def _tab(t, y):
    """Piecewise-linear lookup in [(y, value), ...]."""
    if y <= t[0][0]:
        return t[0][1]
    for (y0, v0), (y1, v1) in zip(t, t[1:]):
        if y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return t[-1][1]


def surf_rot(n, along=(0, 1, 0)):
    """Euler turning local +Z onto the normal n with local +Y along the hull (`along` projected on the surface)."""
    z = Vector(n).normalized()
    y = Vector(along)
    y = (y - z * y.dot(z))
    if y.length < 1e-6:
        y = Vector((1, 0, 0)) - z * z.x
    y.normalize()
    x = y.cross(z)
    return tuple(Matrix((x, y, z)).transposed().to_euler('XYZ'))


# Parts the static merge never folds (the gate's roles, the mount-kick barrels, the engine and nacelle parts).
MERGE_KEEP = (r'^(Hull|Hull_belly|Superstructure|Tower|Bridge|Engine\w*|Nacelle\w*|Nozzles?|Fins?|Antennas?|Masts?|'
              r'Glass|Hatch(es)?|Crates?|Racks?|\w*_barrels(_\d+)?|Main_cannon\w*|Coil\w*|Gun_\w*|Director\w*|Pd_\w*|'
              r'Bay_\w*|Ext_tanks|Prop_spheres|Module|Radiators|Leading_edges|Body_flap|Sponsons)$')


def merge(a):
    """Fold same-material static parts into one renderer each (glb_check's renderer budget), runtime names kept."""
    W5.merge_static(a, keep=MERGE_KEEP)


# ============================================================================= the dagger hull
# The half outline from the chine (x = w, z = 0) up over the shoulder to the spine (UP, fractions of w and of the top
# height t), and from the keel line out to the chine (LOW, fractions of w and of the belly depth b, below).
UP = [(1.0, 0.0), (.985, .09), (.9, .3), (.74, .58), (.52, .8), (.28, .93), (.1, .99), (0.0, 1.0)]
LOW = [(0.0, 1.0), (.45, .995), (.72, .96), (.88, .78), (.96, .48), (.992, .2), (1.0, 0.0)]


class Hull:
    """The lifting-body dagger: half width at the chine, top (spine) height and belly depth along the length."""

    def __init__(self, W, T, B):
        self.W, self.T, self.B = W, T, B
        self.y0, self.y1 = W[0][0], W[-1][0]

    def w(self, y):
        return _tab(self.W, y)

    def t(self, y):
        return _tab(self.T, y)

    def b(self, y):
        return _tab(self.B, y)

    def top(self, x, y):
        return self._z(x, y, True)

    def bot(self, x, y):
        return self._z(x, y, False)

    def _z(self, x, y, top):
        w = max(1e-3, self.w(y))
        f = min(1.0, abs(x) / w)
        prof = sorted(UP if top else LOW, key=lambda p: p[0])
        h = self.t(y) if top else self.b(y)
        for (x0, z0), (x1, z1) in zip(prof, prof[1:]):
            if x0 <= f <= x1:
                u = 0 if x1 == x0 else (f - x0) / (x1 - x0)
                return (z0 + (z1 - z0) * u) * h
        return 0.0

    def normal(self, x, y, top=True, e=.03):
        f = self.top if top else self.bot
        dzdx = (f(x + e, y) - f(x - e, y)) / (2 * e)
        dzdy = (f(x, y + e) - f(x, y - e)) / (2 * e)
        n = Vector((-dzdx, -dzdy, 1.0)) if top else Vector((dzdx, dzdy, -1.0))
        return tuple(n.normalized())

    def on_top(self, x, y, lift=0.0):
        n = Vector(self.normal(x, y))
        return tuple(Vector((x, y, self.top(x, y))) + n * lift), tuple(n)

    def on_bot(self, x, y, lift=0.0):
        n = Vector(self.normal(x, y, top=False))
        return tuple(Vector((x, y, self.bot(x, y))) + n * lift), tuple(n)

    def stations(self, step_nose=.6, step=1.2):
        ys, y = [], self.y0
        while y < self.y1 - .05:
            ys.append(y)
            y += step_nose if y < self.y0 + 6 else step
        return ys + [self.y1]


ICARUS = Hull(W=[(-19.3, .22), (-18.4, .7), (-17, 1.25), (-15, 1.9), (-12.5, 2.65), (-9.5, 3.4), (-6, 4.15), (-2, 4.8),
                 (2, 5.35), (6, 5.8), (9.5, 6.0), (12.6, 5.8)],
              T=[(-19.3, .12), (-18.4, .34), (-17, .6), (-15, .92), (-12.5, 1.25), (-9.5, 1.56), (-6, 1.88), (-2, 2.12),
                 (2, 2.28), (12.6, 2.34)],
              B=[(-19.3, -.1), (-18.4, -.28), (-17, -.48), (-15, -.74), (-12.5, -1.02), (-9.5, -1.28), (-6, -1.52),
                 (-2, -1.7), (2, -1.8), (12.6, -1.84)])


# The prototype's hull: the same length, a slimmer and flatter blade (the finished ship's hull grew with its systems).
MK0 = Hull(W=[(y, w * (.9 if y > -12 else .95)) for y, w in ICARUS.W],
           T=[(y, t * .86) for y, t in ICARUS.T],
           B=[(y, b * .92) for y, b in ICARUS.B])


def hull_skin(a, H, upper='Fuel', lower='Undercarriage'):
    """The skin: the upper hull (silver) and the belly (tiles) as two closed lofts meeting at the chine."""
    up = a.part('Hull', upper)
    low = a.part('Hull_belly', lower)
    urings, lrings = [], []
    for y in H.stations():
        w, t, b = H.w(y), H.t(y), H.b(y)
        right = [(fx * w, y, fz * t) for fx, fz in UP]
        urings.append(right + [(-x, yy, z) for x, yy, z in reversed(right[:-1])])
        rl = [(fx * w, y, fz * b) for fx, fz in reversed(LOW)]
        lrings.append(rl + [(-x, yy, z) for x, yy, z in reversed(rl[:-1])])
    up.loft(urings, bevel=0)
    low.loft(lrings, bevel=0)


def leading_edges(a, H, y_end=11.5, mat='Concrete'):
    """The grey carbon nose cap and the chine leading edges (thermal protection), and the belly's chine band."""
    edge = a.part('Leading_edges', mat)
    for s in (-1, 1):
        pts = [(s * (H.w(y) + .02), y, .0) for y in [H.y0 + .35] + [v * .5 for v in range(-37, int(y_end * 2))]]
        edge.tube(pts, .085, seg=6, caps=True)
    y0 = H.y0
    k.lathe(a.part('Nose_cap', mat), [(0, -.05), (.18, .02), (.3, .2), (.36, .55), (.34, .9)],
            loc=(0, y0 + .05, -.02), rot=K.BACKWARD, seg=14)


def hull_plating(a, H, keep_out, tones=(('Fuel', .5), ('Medical', .32), ('MetalSheet', .18)), seed=7, density=1.0,
                 y_from=None, y_to=None, missing=None):
    """The upper hull's plate patchwork in three tones, laid on the slopes along the hull; `keep_out` (x0, x1, y0, y1)
    boxes stay clear for the superstructure and fittings. `missing` (a callable (x, y) -> bool) leaves a plate out and
    draws an open bay there instead (the prototype)."""
    rng = random.Random(seed)
    y = (y_from if y_from is not None else H.y0 + 1.6)
    end = y_to if y_to is not None else H.y1 - .3
    i = 0
    while y < end:
        depth = rng.choice((.5, .65, .8, 1.0, 1.25))
        yc = y + depth / 2
        w = H.w(yc)
        x = .12
        while x < .975 * w:
            width = rng.choice((.45, .6, .8, 1.0, 1.3)) * (1 if w > 2 else .6)
            xc = x + width / 2
            if xc > .97 * w:
                break
            for s in (-1, 1):
                X = s * xc
                if any(x0 <= X <= x1 and y0 <= yc <= y1 for x0, x1, y0, y1 in keep_out):
                    continue
                if rng.random() > .86 * density:
                    continue
                p, n = H.on_top(X, yc, .012)
                if missing is not None and missing(X, yc):
                    a.part('Open_bays', 'Undercarriage').box((width - .04, depth - .05, .02), loc=p, rot=surf_rot(n),
                                                             bevel=0)
                    for j in range(3):
                        q, _ = H.on_top(X, yc - depth * .35 + j * depth * .35, .05)
                        a.part('Stringers', 'Steel').box((width - .06, .05, .06), loc=q, rot=surf_rot(n), bevel=0)
                    continue
                mat = rng.choices([t[0] for t in tones], [t[1] for t in tones])[0]
                a.part(f'Hull_plates_{mat.lower()}', mat).box((width - .05, depth - .05, .028), loc=p,
                                                               rot=surf_rot(n), bevel=0)
                i += 1
            x += width
        y += depth


def panel_lines(a, H, y_from=None, y_to=None, mat='Undercarriage', every=1.6):
    """Panel lines across the upper hull at frame stations and along it at three stringers each side."""
    lines = a.part('Panel_lines', mat)
    y0 = y_from if y_from is not None else H.y0 + 1.2
    y1 = y_to if y_to is not None else H.y1 - .2
    y = y0
    while y < y1:
        w = H.w(y)
        for s in (-1, 1):
            pts = [H.on_top(s * f * w, y, .015)[0] for f in (.04, .25, .45, .62, .78, .9, .975)]
            lines.tube(pts, .016, seg=3, caps=False)
        y += every
    for f in (.3, .6, .86):
        for s in (-1, 1):
            pts = [H.on_top(s * f * H.w(yy), yy, .016)[0] for yy in [y0 + v * .8 for v in range(int((y1 - y0) / .8) + 1)]]
            lines.tube(pts, .014, seg=3, caps=False)


def belly_tiles(a, H, y_from=None, y_to=None, seed=3, patches=110):
    """The belly's reusable-surface tiles: the gap grid (lighter lines over the black) and replaced tiles in other
    shades; the tiled area runs y_from .. y_to."""
    grid = a.part('Tile_gaps', 'Armor')
    y0 = y_from if y_from is not None else H.y0 + .6
    y1 = y_to if y_to is not None else H.y1 - .1
    y = y0
    while y < y1:
        w = H.w(y)
        pts = [H.on_bot(s * f * w, y, .012)[0] for s, f in [(-1, .97), (-1, .85), (-1, .6), (-1, .3), (1, 0),
                                                             (1, .3), (1, .6), (1, .85), (1, .97)]]
        grid.tube(pts, .016, seg=3, caps=False)
        y += .95
    for i in range(-6, 7):
        x = i * .95
        ys = [yy for yy in [y0 + v * .9 for v in range(int((y1 - y0) / .9) + 1)] if abs(x) < .93 * H.w(yy)]
        if len(ys) < 2:
            continue
        grid.tube([H.on_bot(x, yy, .012)[0] for yy in ys], .016, seg=3, caps=False)
    rng = random.Random(seed)
    for _ in range(patches):
        yy = rng.uniform(y0 + .5, y1 - .5)
        x = rng.uniform(-.85, .85) * H.w(yy)
        p, n = H.on_bot(x, yy, .01)
        mat = rng.choice(('Charred', 'Concrete', 'Armor', 'Charred'))
        a.part(f'Tile_patches_{mat.lower()}', mat).box((.42, .42, .02), loc=p, rot=surf_rot(n), bevel=0)


def shoulder_windows(a, H, y0, y1, f=.86, pitch=.75, mat='Lamp'):
    """A row of lit windows along each shoulder (the crew decks inside the hull)."""
    win = a.part('Hull_windows', mat)
    y = y0
    while y < y1:
        for s in (-1, 1):
            p, n = H.on_top(s * f * H.w(y), y, .03)
            win.box((.11, .42, .03), loc=p, rot=surf_rot(n), bevel=0)
        y += pitch


def stripes(a, H, y0, y1, fs=(.95,), mat='Team'):
    st = a.part('Aurel_stripes', mat)
    for f in fs:
        for s in (-1, 1):
            pts = [H.on_top(s * f * H.w(y), y, .02)[0] for y in [y0 + v * .7 for v in range(int((y1 - y0) / .7) + 1)]]
            st.tube(pts, .07, seg=4, caps=False)


# ============================================================================= engines
def bell(a, part, loc, r_exit, length, r_throat, parent=None, seg=24, wall=.045, bands=3, band_part=None):
    """A rocket engine's bell pointing aft (+Y) from its throat at loc: a closed thin-walled solid (outer contour, the
    lip, the inner contour back to the throat floor), so the cavity is drawn from behind; regenerative cooling bands
    round the outside. Returns the exit plane's centre (in the parent's frame)."""
    n = 8

    def r_at(u):
        return r_throat + (r_exit - r_throat) * (1 - (1 - u) ** 1.9)
    outer = [(r_at(i / n) + wall, i / n * length) for i in range(n + 1)]
    inner = [(r_at(i / n), i / n * length) for i in range(n, 1, -1)]
    prof = [(r_throat * 1.25 + wall, -.12)] + outer + [(r_exit + wall * .2, length + .02)] + inner + \
           [(r_at(.15) * .9, .15 * length)]
    k.lathe(a.part(part[0], part[1], parent), prof, loc=loc, rot=K.BACKWARD, seg=seg)
    if bands and band_part:
        for j in range(bands):
            u = .25 + .7 * j / max(1, bands - 1)
            r = r_at(u) + wall
            k.ring(a.part(band_part[0], band_part[1], parent), [(r + .035, -.03), (r + .035, .03), (r, .045),
                                                               (r, -.045)], loc=(loc[0], loc[1] + u * length, loc[2]),
                   rot=K.BACKWARD, seg=seg)
    return (loc[0], loc[1] + length + .02, loc[2])


def powerhead(a, parent, loc, r, mat='Steel', dark='Undercarriage', pipes='Pipe', seed=0):
    """The powerhead forward of a bell: the injector dome, two turbopump cans on its sides, the hot-gas manifold and
    the propellant ducts, gimbal bearing and two actuators."""
    x, y, z = loc
    k.lathe(a.part('Powerheads', mat, parent), [(0, -.7 * r), (r * .55, -.62 * r), (r * .72, -.3 * r), (r * .62, 0)],
            loc=loc, rot=K.BACKWARD, seg=16)
    for s in (-1, 1):
        a.part('Turbopumps', dark, parent).cyl(r * .26, r * 1.1, loc=(x + s * r * .78, y - .25 * r, z + .1 * r),
                                               rot=(R90, 0, 0), seg=10, bevel=0)
        a.part('Turbopump_caps', mat, parent).cyl(r * .3, .06, loc=(x + s * r * .78, y - .82 * r, z + .1 * r),
                                                  rot=(R90, 0, 0), seg=10, bevel=0)
        a.part('Ducts', pipes, parent).tube([(x + s * r * .78, y - .7 * r, z + .25 * r), (x + s * r * .5, y - .95 * r,
                                                                                           z + .55 * r),
                                             (x, y - 1.05 * r, z + .62 * r)], r * .08, seg=6)
        a.part('Gimbal_rams', mat, parent).limb((x + s * r * .55, y - .9 * r, z - .45 * r),
                                                (x + s * r * .72, y + .55 * r, z - .55 * r), .07, .07, bevel=0)
    a.part('Gimbal_bearings', dark, parent).sphere(r * .22, loc=(x, y - .78 * r, z), seg=10, rings=6)


def rcs_quad(a, part, nozzles, loc, out, glow=None):
    """An RCS thruster quad: the block and four nozzles, one facing `out` (a unit axis) and three across it."""
    x, y, z = loc
    a.part(part[0], part[1]).box((.34, .34, .3), loc=loc, bevel=0)
    o = Vector(out)
    for d in (o, Vector((0, 0, 1)), Vector((0, 0, -1)), Vector((0, 1 if abs(o.y) < .5 else 0, 0 if abs(o.y) < .5 else 1))):
        p = Vector(loc) + d * .2
        a.part(nozzles[0], nozzles[1]).cyl(.06, .12, loc=tuple(p), rot=K.rot_to(tuple(d)), seg=6, r2=.04, bevel=0)


# ============================================================================= silver_bug (Icarus)
SB_KEEP = [(-4.3, 4.3, .2, 12.7),       # the superstructure
           (-1.6, 1.6, -9.0, -.6),      # the spine module
           (3.3, 5.4, -3.2, .2), (-5.4, -3.3, -3.2, .2),      # coilgun barbettes
           (1.6, 3.2, -7.0, -4.8), (-3.2, -1.6, -7.0, -4.8),  # PD towers
           (-.9, .9, -13.5, -10.6)]     # docking port


def _sb_engines(a, H, proto=False):
    """The bank of main engines across the stern (Thruster_main: the thrust structure, five regeneratively cooled bells
    with their powerheads; the prototype: three bigger ones on an open frame), the body flap under them, the heat
    shield round them. Engine_flame empties on every exit plane."""
    t = a.pivot('Thruster_main', (0, 15.5, .6))
    zc = 0.0
    if not proto:
        k.block(a.part('Engine_block', 'MetalSheet', t), (11.0, 1.7, 2.7), loc=(0, -2.2, -.05), chamfer=.15)
        k.block(a.part('Engine_block_plates', 'Armor', t), (11.2, .1, 2.5), loc=(0, -1.33, -.05), chamfer=0)
        for x in (-5.0, -3.1, -1.0, 1.0, 3.1, 5.0):
            a.part('Thrust_struts', 'Steel', t).limb((x, -1.3, 1.1), (x * .8, -.55, .0), .1, .1, bevel=0)
            a.part('Thrust_struts', 'Steel', t).limb((x, -1.3, -1.2), (x * .8, -.55, .0), .1, .1, bevel=0)
        # The heat shield face with the engines' boots.
        xs = [(-4.1, -.25), (-2.05, .45), (0, -.25), (2.05, .45), (4.1, -.25)]
        r_exit, length, r_t = .86, 2.0, .36
    else:
        for s in (-1, 1):
            a.part('Thrust_frame', 'Steel', t).limb((s * 3.6, -2.9, 1.2), (s * 3.6, -.6, -.4), .14, .14, bevel=0)
            a.part('Thrust_frame', 'Steel', t).limb((s * 3.6, -2.9, -1.6), (s * 3.6, -.6, -.4), .14, .14, bevel=0)
            a.part('Thrust_frame', 'Steel', t).limb((s * 3.6, -.6, -.4), (0, -.6, -.4), .12, .12, bevel=0)
        k.block(a.part('Engine_block', 'Crate', t), (8.4, .5, 2.8), loc=(0, -2.85, -.1), chamfer=.08)
        xs = [(-2.5, -.2), (0, .2), (2.5, -.2)]
        r_exit, length, r_t = 1.05, 2.35, .42
    for i, (x, dz) in enumerate(xs):
        z = dz + zc
        powerhead(a, t, (x, -.75, z), r_exit * .9, seed=i)
        ex = bell(a, ('Engine_bells', 'Steel'), (x, -.15, z), r_exit, length, r_t, parent=t, seg=26, bands=4,
                  band_part=('Engine_bands', 'Armor'))
        a.part('Engine_glow', 'LavaGlow', t).cyl(r_t * 1.1, .03, loc=(x, -.15 + .2 * length, z), rot=(R90, 0, 0),
                                                 seg=14, bevel=0)
        K.engine_flame(a, i, (ex[0], ex[1] + .01, ex[2]), r_exit, parent='Thruster_main')
        K.soot(a, (x, 15.5 + length * .55, z + .6), radius=r_exit * 1.1, k=.35)
    # Plumbing between the powerheads (feed lines along the thrust structure).
    feed = a.part('Feed_lines', 'Pipe', t)
    for z in (.95, -1.1):
        feed.tube([(xs[0][0] - .6, -1.15, z + zc), (xs[-1][0] + .6, -1.15, z + zc)], .09, seg=8)
    if not proto:
        # The body flap: the heat-shielded plate under the engines that trims the glide; hinge line and actuators.
        flap = a.part('Body_flap', 'Undercarriage')
        k.block(flap, (10.8, 2.9, .28), loc=(0, 14.0, -1.72), chamfer=.06)
        for x in range(-5, 6):
            a.part('Tile_gaps', 'Armor').box((.03, 2.8, .02), loc=(x * .95, 14.0, -1.875), bevel=0)
        a.part('Flap_hinge', 'Steel').cyl(.1, 10.6, loc=(0, 12.55, -1.72), rot=(0, R90, 0), seg=8, bevel=0)
        for s in (-1, 1):
            a.part('Leading_edges', 'Concrete').box((.3, 2.9, .3), loc=(s * 5.45, 14.0, -1.72), bevel=0)
    K.tone(a, 'Thruster_main', k=.88)


def _nacelle(a, s, proto=False):
    """An OMS-style nacelle on its pylon (Thruster_rl / _rr: the pod, the intake, the fin, its own engine bell, the
    Engine_flame on it)."""
    name = 'Thruster_rl' if s > 0 else 'Thruster_rr'
    tag = '' if s > 0 else '_r'
    p = a.pivot(name, (s * 8.0, 11.0, .4))
    k.lathe(a.part('Nacelle' + tag, 'Fuel', p), [(0, -4.3), (.32, -4.05), (.66, -3.5), (.93, -2.7), (1.1, -1.7),
                                                 (1.15, -.6), (1.15, 1.6), (1.02, 2.4), (.8, 2.7)], rot=K.BACKWARD, seg=22)
    for y in (-2.4, -.9, .6, 2.0):
        k.ring(a.part('Nacelle_bands' + tag, 'Armor', p), [(1.17, -.05), (1.19, -.05), (1.19, .05), (1.17, .05)],
               loc=(0, y, 0), rot=K.BACKWARD, seg=22)
    for e in (-1, 1):
        a.part('Nacelle_intake' + tag, 'Undercarriage', p).box((.3, 1.4, .5), loc=(-s * .95, -1.5, e * .45),
                                                              rot=(0, 0, 0), bevel=0)
    # The pylon to the hull's chine and the vertical fin on top.
    k.extrude(a.part('Nacelle_pylon' + tag, 'MetalSheet', p), [(-2.6, -.25), (2.0, -.25), (1.6, .25), (-2.0, .25)],
              2.6, loc=(-s * 1.55, 0, -.05), axis='X', chamfer=.05)
    k.extrude(a.part('Nacelle_fin' + tag, 'Fuel', p), [(-.6, 0), (2.2, 0), (2.5, 2.3), (1.4, 2.3)], .16,
              loc=(0, 0, 1.0), axis='X', chamfer=.03)
    a.part('Nacelle_fin_tip' + tag, 'Undercarriage', p).box((.18, 1.12, .12), loc=(0, 1.95, 3.32), bevel=0)
    a.part('Nav_lights_red' if s > 0 else 'Nav_lights_green', 'LavaGlow' if s > 0 else 'SignalGreen', p).sphere(
        .1, loc=(s * 1.18, -1.4, 0), seg=8, rings=4)
    powerhead(a, p, (0, 2.3, 0), .7)
    ex = bell(a, ('Nacelle_bell' + tag, 'Steel'), (0, 2.75, 0), .82, 1.75, .32, parent=name, seg=24, bands=3,
              band_part=('Nacelle_bell_bands' + tag, 'Armor'))
    a.part('Nacelle_glow' + tag, 'LavaGlow', p).cyl(.38, .03, loc=(0, 3.1, 0), rot=(R90, 0, 0), seg=14, bevel=0)
    K.engine_flame(a, 5 if s > 0 else 6, ex, .82, parent=name)
    K.tone(a, name, k=.9)


def _rcs_pod(a, H, s):
    """A forward RCS pod on its canard (Thruster_fl / _fr): the canard from the chine, the pod with its thruster quads
    and glow."""
    name = 'Thruster_fl' if s > 0 else 'Thruster_fr'
    tag = '' if s > 0 else '_r'
    p = a.pivot(name, (s * 4.5, -11.0, .8))
    # The canard from the chine out to the pod (in the hull frame: x from the chine at y = -11).
    x0 = H.w(-11.0) - .2
    a.part('Canards', 'Fuel').loft([[(s * x0, -12.6, .0), (s * x0, -9.4, .0), (s * x0, -9.4, .14), (s * x0, -12.6, .14)],
                                    [(s * 4.1, -11.8, .62), (s * 4.1, -10.2, .62), (s * 4.1, -10.2, .74),
                                     (s * 4.1, -11.8, .74)]], bevel=0)
    a.part('Canard_edges', 'Concrete').tube([(s * x0, -12.62, .07), (s * 4.1, -11.82, .68)], .07, seg=5)
    k.lathe(a.part('Rcs_pod' + tag, 'Fuel', p), [(0, -1.5), (.22, -1.35), (.42, -.9), (.48, -.3), (.48, .7),
                                                 (.4, 1.05), (.25, 1.2)], rot=K.BACKWARD, seg=16)
    a.part('Rcs_pod_band' + tag, 'Team', p).cyl(.5, .22, loc=(0, .3, 0), rot=(R90, 0, 0), seg=16, bevel=0)
    for y in (-.6, .5):
        for d in ((s, 0, 0), (0, 0, 1), (0, 0, -1)):
            q = (d[0] * .47, y, d[2] * .47)
            a.part('Rcs_nozzles' + tag, 'Steel', p).cyl(.07, .14, loc=q, rot=K.rot_to(d), seg=6, r2=.05, bevel=0)
            a.part('Rcs_glow' + tag, 'Energy', p).cyl(.04, .02, loc=(q[0] + d[0] * .075, y, q[2] + d[2] * .075),
                                                       rot=K.rot_to(d), seg=6, bevel=0)
    a.part('Rcs_nozzles' + tag, 'Steel', p).cyl(.08, .12, loc=(0, -1.48, 0), rot=K.FORWARD, seg=6, bevel=0)
    K.tone(a, name, k=.9)


def _main_laser(a, H, proto=False):
    """The ventral main laser (Turret): the blister pylon from the belly, the turning ball, the emitter barrel with its
    cooling fins, focusing rings and the glowing lens, Muzzle_main at the lens. The prototype's: a boxy test mount, a
    bare barrel with its coolant lines and a clamped-on lens housing."""
    if proto:
        _main_laser_proto(a, H)
        return
    zb = H.bot(0, -7.0)
    k.lathe(a.part('Laser_blister', 'Undercarriage'), [(1.5, zb + .25), (1.45, zb - .15), (1.15, zb - .6),
                                                       (.95, zb - .8)], loc=(0, -7.0, 0), seg=20)
    t = a.pivot('Turret', (0, -7.0, -2.8))
    a.part('Turret_ball', 'Armor', t).sphere(.95, seg=20, rings=12)
    a.part('Turret_collar', 'Steel', t).cyl(1.0, .16, loc=(0, 0, .55), seg=20, bevel=0)
    a.part('Turret_band', 'Team', t).cyl(.97, .14, loc=(0, 0, .1), seg=20, bevel=0)
    a.part('Turret_sight', 'Glass', t).sphere(.2, loc=(.62, -.6, .2), seg=10, rings=6)
    # The emitter: barrel along -Y with fins and rings, the lens at the front.
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.42, 0), (.42, .6), (.34, .75), (.3, 2.6), (.38, 2.75), (.38, 3.05),
                                                (.3, 3.12)], loc=(0, -.55, -.12), rot=K.FORWARD, seg=16)
    for j in range(7):
        a.part('Main_cannon_fins', 'Armor', t).box((.9, .05, .9), loc=(0, -1.55 - j * .17, -.12), bevel=0)
    for y in (-1.25, -2.95):
        a.part('Main_cannon_rings', 'Armor', t).cyl(.42, .12, loc=(0, y, -.12), rot=(R90, 0, 0), seg=16, bevel=0)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.26, .04, loc=(0, -3.68, -.12), rot=(R90, 0, 0), seg=16, bevel=0)
    a.pivot('Muzzle_main', (0, -3.72, -.12), 'Turret')
    K.tone(a, 'Turret', k=.88)


def _main_laser_proto(a, H):
    zb = H.bot(0, -7.0)
    for e in (-1, 1):
        a.part('Laser_pylons', 'Steel').limb((e * .9, -6.2, zb + .1), (e * .5, -7.0, -2.2), .2, .2, bevel=0)
        a.part('Laser_pylons', 'Steel').limb((e * .9, -7.8, zb + .1), (e * .5, -7.0, -2.2), .2, .2, bevel=0)
    k.block(a.part('Laser_blister', 'Crate'), (2.0, 2.6, .35), loc=(0, -7.0, zb - .05), chamfer=.05)
    t = a.pivot('Turret', (0, -7.0, -2.8))
    k.block(a.part('Turret_ball', 'Crate', t), (1.5, 1.6, 1.3), loc=(0, .1, -.1), chamfer=.1)
    a.part('Turret_collar', 'Steel', t).cyl(.8, .2, loc=(0, 0, .62), seg=16, bevel=0)
    a.part('Turret_band', 'Hazard', t).box((1.55, .12, 1.32), loc=(0, -.68, -.1), bevel=0)
    k.lathe(a.part('Main_cannon', 'MetalSheet', t), [(.36, 0), (.36, .5), (.28, .6), (.26, 2.9), (.33, 3.0)],
            loc=(0, -.6, -.12), rot=K.FORWARD, seg=12)
    for e in (-1, 1):
        a.part('Main_cannon_pipes', 'Pipe', t).tube([(e * .55, .3, .3), (e * .4, -.8, -.05), (e * .33, -2.9, -.05)],
                                                    .06, seg=6)
    k.block(a.part('Main_cannon_rings', 'Armor', t), (.9, .7, .9), loc=(0, -3.55, -.12), chamfer=.06)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.3, .04, loc=(0, -3.92, -.12), rot=(R90, 0, 0), seg=14, bevel=0)
    a.pivot('Muzzle_main', (0, -3.96, -.12), 'Turret')
    K.tone(a, 'Turret', k=.88)


def _coilgun(a, H, i, x, y):
    """A heavy coilgun on its shoulder barbette (Mount_gun / .001): the barbette from the hull, the turning house with
    its capacitor banks, the two rails with the coil rings between them, the muzzle collar; Muzzle_gun at the mouth."""
    s = 1 if x > 0 else -1
    zs = H.top(x, y)
    tag = '' if i == 0 else '_001'
    k.lathe(a.part('Coilgun_barbettes', 'MetalSheet'), [(1.45, zs - .4), (1.45, zs + .25), (1.3, zs + .45)],
            loc=(x, y, 0), seg=20)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, zs + .45))
    k.lathe(a.part('Coilgun_ring' + tag, 'Armor', m), [(1.2, 0), (1.25, .08), (1.1, .2)], seg=20)
    k.sharp_loft(a.part('Coilgun_housing' + tag, 'Fuel', m), [
        [(-1.0, -1.1, .15), (1.0, -1.1, .15), (1.05, 1.3, .15), (-1.05, 1.3, .15)],
        [(-.8, -.95, .95), (.8, -.95, .95), (.85, 1.2, .95), (-.85, 1.2, .95)]], chamfer=.05)
    for e in (-1, 1):
        k.block(a.part('Coilgun_caps' + tag, 'Undercarriage', m), (.3, 1.7, .6), loc=(e * 1.1, .2, .5), chamfer=.04)
        for j in range(4):
            a.part('Coilgun_cells' + tag, 'Steel', m).box((.08, .3, .45), loc=(e * 1.27, -.45 + j * .42, .5), bevel=0)
    # Rails and coils.
    for e in (-1, 1):
        a.part('Coil_barrels' + tag, 'Steel', m).box((.12, 6.4, .2), loc=(e * .26, -4.0, .6), bevel=0)
    for j in range(12):
        yy = -1.3 - j * .48
        k.ring(a.part('Coil_rings' + tag, 'Armor', m), [(.4, -.07), (.44, -.07), (.44, .07), (.4, .07)],
               loc=(0, yy, .6), rot=(R90, 0, 0), seg=14)
        if j % 2:
            a.part('Coil_glow' + tag, 'Energy', m).cyl(.36, .03, loc=(0, yy + .24, .6), rot=(R90, 0, 0), seg=12,
                                                       bevel=0)
    a.part('Coil_barrels' + tag, 'Undercarriage', m).box((.36, 6.2, .1), loc=(0, -4.0, .28), bevel=0)
    k.lathe(a.part('Coil_muzzles' + tag, 'Armor', m), [(.38, 0), (.5, .1), (.5, .45), (.4, .55)],
            loc=(0, -7.15, .6), rot=K.FORWARD, seg=14)
    a.pivot(K.name('Muzzle_gun', i), (0, -7.75, .6), key)
    K.tone(a, key, k=.9)


def _beam_director(a, i, loc, gun_index):
    """A laser beam director (Mount_gun.002 / .003): the drum base, the yoke, the telescope with its sunshade and the
    glowing aperture; Muzzle_gun.00N at the aperture."""
    tag = f'_{gun_index:03d}'
    key = K.name('Mount_gun', gun_index)
    m = a.pivot(key, loc)
    k.lathe(a.part('Director_base' + tag, 'Armor', m), [(.75, -.25), (.75, .1), (.62, .2), (.55, .45)], seg=18)
    for e in (-1, 1):
        k.block(a.part('Director_yoke' + tag, 'Fuel', m), (.16, .5, .85), loc=(e * .55, 0, .75), chamfer=.03)
    k.lathe(a.part('Director_tube' + tag, 'Fuel', m), [(.32, -.5), (.38, -.4), (.38, .9), (.44, 1.0), (.44, 1.35),
                                                       (.4, 1.4)], loc=(0, 0, .95), rot=K.FORWARD, seg=16)
    a.part('Director_rings' + tag, 'Team', m).cyl(.4, .1, loc=(0, -.35, .95), rot=(R90, 0, 0), seg=16, bevel=0)
    a.part('Director_aperture' + tag, 'Energy', m).cyl(.3, .03, loc=(0, -1.38, .95), rot=(R90, 0, 0), seg=16, bevel=0)
    a.part('Director_sensor' + tag, 'Glass', m).box((.2, .3, .16), loc=(.38, -.6, 1.3), bevel=0)
    a.pivot(K.name('Muzzle_gun', gun_index), (0, -1.42, .95), key)
    K.tone(a, key, k=.9)


def _crash_turret(a, H, gun_index, s, y):
    """A twin 40 mm turret on its flank sponson (Mount_gun.004 / .005, the crash turrets that keep firing on the
    ground): the sponson from the chine, the ring, the faceted house, two barrels with their brakes, the sight;
    Muzzle_gun.00N between the tips and Muzzle_b1 / _b2 at each."""
    w = H.w(y)
    tag = f'_{gun_index:03d}'
    # The sponson: a faceted barbette pod hung on the chine.
    a.part('Sponsons', 'MetalSheet').loft([
        [(s * (w - .4), y - 2.4, -.5), (s * (w + .9), y - 1.6, -.4), (s * (w + .9), y + 1.9, -.4),
         (s * (w - .4), y + 2.6, -.5)],
        [(s * (w - .4), y - 2.1, .55), (s * (w + 1.05), y - 1.3, .6), (s * (w + 1.05), y + 1.6, .6),
         (s * (w - .4), y + 2.3, .55)]], bevel=0)
    a.part('Sponson_tiles', 'Undercarriage').box((1.4, 3.4, .08), loc=(s * (w + .25), y + .15, -.48), bevel=0)
    key = K.name('Mount_gun', gun_index)
    m = a.pivot(key, (s * (w + .3), y, .62))
    k.lathe(a.part('Gun_ring' + tag, 'Steel', m), [(.75, 0), (.78, .06), (.7, .12)], seg=18)
    k.sharp_loft(a.part('Gun_house' + tag, 'Fuel', m), [
        [(-.7, -.75, .1), (.7, -.75, .1), (.75, .85, .1), (-.75, .85, .1)],
        [(-.55, -.55, .72), (.55, -.55, .72), (.6, .7, .72), (-.6, .7, .72)]], chamfer=.04)
    a.part('Gun_mantlet' + tag, 'Armor', m).box((.85, .3, .42), loc=(0, -.86, .4), bevel=0)
    for j, dx in enumerate((-.2, .2)):
        k.lathe(a.part('Gun_barrels' + tag, 'Steel', m), [(.08, 0), (.08, 1.7), (.1, 1.75), (.1, 2.05), (.07, 2.1)],
                loc=(dx, -.95, .42), rot=K.FORWARD, seg=10)
        a.part('Gun_jackets' + tag, 'Armor', m).cyl(.1, .5, loc=(dx, -1.35, .42), rot=(R90, 0, 0), seg=10, bevel=0)
    a.part('Gun_sight' + tag, 'Glass', m).box((.18, .22, .16), loc=(-.42, -.4, .82), bevel=0)
    mz = K.name('Muzzle_gun', gun_index)
    a.pivot(mz, (0, -3.07, .42), key)
    a.pivot(f'Muzzle_b1_gun{tag}', (-.2 if s > 0 else .2, 0, 0), mz)
    a.pivot(f'Muzzle_b2_gun{tag}', (.2 if s > 0 else -.2, 0, 0), mz)
    K.tone(a, key, k=.88)


def _pd_laser(a, H, name, x, y, tag, capped=False, z=None, proto=False):
    """A point-defence laser on its tower (Pd_laser_l / _r): the tower from the hull, the dome, the emitter and glow.
    capped: the prototype's empty station (a ring and a blanking cover with hazard bands, no pivot)."""
    zs = H.top(x, y)
    if capped:
        k.lathe(a.part('Pd_station_empty', 'Crate'), [(.85, zs - .3), (.85, zs + .25), (.7, zs + .32)], loc=(x, y, 0),
                seg=16)
        a.part('Pd_station_cover', 'Hazard').cyl(.68, .06, loc=(x, y, zs + .35), seg=16, bevel=0)
        for e in (-1, 1):
            a.part('Pd_station_cover', 'Charred').box((1.2, .12, .02), loc=(x, y + e * .25, zs + .39), bevel=0)
        return
    p = a.pivot(name, (x, y, z if z is not None else zs + .45))
    if proto:
        zl = zs - (z if z is not None else zs + .45)
        for j in range(4):
            v = j * R90 + .4
            a.part('Pd_tower' + tag, 'Steel', p).limb((math.cos(v) * .8, math.sin(v) * .8, zl - .1), (0, 0, -.1), .12,
                                                      .12, bevel=0)
        k.block(a.part('Pd_dome' + tag, 'Crate', p), (.9, 1.0, .6), loc=(0, 0, .15), chamfer=.06)
        a.part('Pd_emitter' + tag, 'Steel', p).cyl(.1, .8, loc=(0, -.75, .3), rot=(R90, 0, 0), seg=8, bevel=0)
        a.part('Pd_glow' + tag, 'Energy', p).sphere(.1, loc=(0, -1.18, .3), seg=8, rings=4)
        a.part('Pd_cables' + tag, 'Charred', p).tube([(.4, .4, .2), (.7, .6, zl + .05)], .04, seg=4)
        return
    k.lathe(a.part('Pd_tower' + tag, 'MetalSheet', p), [(.9, -.75), (.85, -.3), (.62, -.05), (.55, 0)], seg=14)
    a.part('Pd_dome' + tag, 'Fuel', p).sphere(.5, loc=(0, 0, .12), seg=14, rings=7)
    a.part('Pd_band' + tag, 'Team', p).cyl(.52, .1, loc=(0, 0, .05), seg=14, bevel=0)
    a.part('Pd_emitter' + tag, 'Steel', p).cyl(.1, .85, loc=(0, -.55, .42), rot=(R90 - .3, 0, 0), seg=10, bevel=0)
    a.part('Pd_emitter' + tag, 'Steel', p).cyl(.16, .14, loc=(0, -.22, .3), rot=(R90 - .3, 0, 0), seg=10, bevel=0)
    a.part('Pd_glow' + tag, 'Energy', p).sphere(.1, loc=(0, -.97, .55), seg=8, rings=4)
    K.tone(a, name, k=.88)


def _pod_bay(a, H, pods=2):
    """The drop-pod bay (Pod_bay): the ventral housing, the opened doors hanging from it, the pod in its cradle with
    its glowing ring, the hazard chevrons; Muzzle_missile where the pods leave."""
    y = 4.0
    zb = H.bot(0, y)
    k.block(a.part('Bay_housing', 'Undercarriage'), (3.6, 5.2, .7), loc=(0, y, zb - .2), chamfer=.12)
    p = a.pivot('Pod_bay', (0, y, -2.6))
    a.part('Bay_well', 'Charred', p).box((2.6, 4.2, .05), loc=(0, 0, .02), bevel=0)
    for s in (-1, 1):
        a.part('Bay_doors', 'Undercarriage', p).box((.08, 4.1, 1.25), loc=(s * 1.42, 0, -.45), rot=(0, -s * .3, 0),
                                                    bevel=0)
        for j in range(4):
            a.part('Bay_door_ribs', 'Armor', p).box((.1, .08, 1.2), loc=(s * 1.36, -1.5 + j, -.45),
                                                    rot=(0, -s * .3, 0), bevel=0)
        a.part('Bay_rams', 'Steel', p).limb((s * 1.0, -1.2, .1), (s * 1.32, -1.2, -.6), .06, .06, bevel=0)
        a.part('Bay_rams', 'Steel', p).limb((s * 1.0, 1.2, .1), (s * 1.32, 1.2, -.6), .06, .06, bevel=0)
    for j in range(pods):
        yy = (-1.0 + 2.0 * j) if pods > 1 else 0.0
        k.lathe(a.part('Bay_pods', 'Team', p), [(0, -.95), (.32, -.85), (.55, -.5), (.6, -.1), (.55, .05), (0, .08)],
                loc=(0, yy, -.05), seg=14)
        a.part('Bay_pod_glow', 'Energy', p).torus(.58, .04, loc=(0, yy, -.35), seg=14, ring=4)
        for u in range(3):
            v = u * TAU / 3
            a.part('Bay_pod_fins', 'Armor', p).box((.04, .35, .32), loc=(math.cos(v) * .45, yy + math.sin(v) * .45,
                                                                          -.62), rot=(0, 0, v + R90), bevel=0)
        a.part('Bay_clamps', 'Steel', p).box((1.3, .14, .12), loc=(0, yy, .02), bevel=0)
    for s in (-1, 1):
        for j in range(5):
            a.part('Bay_chevrons', 'Hazard', p).box((.16, .45, .02), loc=(s * 1.2, -2.0 + j, .07),
                                                    rot=(0, 0, s * .6), bevel=0)
    a.pivot('Muzzle_missile', (0, 0, -.5), 'Pod_bay')
    K.tone(a, 'Pod_bay', k=.88)


def _superstructure(a, H, broken=False):
    """The stepped superstructure aft under the command tower: three tiers with raked walls, window bands and plates,
    the tower, the bridge with its window band, the sensor mast with the APS emitter (Mount_APS), the uplink dish
    (Uplink) on the first tier's roof."""
    st = a.part('Superstructure', 'Fuel')
    tiers = [((-4.0, .4), (-4.2, 12.6), (4.2, 12.6), (4.0, .4), 1.3, 3.4, .86),
             ((-3.0, 3.6), (-3.2, 12.4), (3.2, 12.4), (3.0, 3.6), 3.4, 4.65, .86),
             ((-2.0, 6.6), (-2.2, 12.2), (2.2, 12.2), (2.0, 6.6), 4.65, 5.75, .84)]
    for ti, (p0, p1, p2, p3, z0, z1, tp) in enumerate(tiers):
        bottom = [p0, p3, p2, p1]
        cy = sum(p[1] for p in bottom) / 4
        top = [(x * tp, cy + (yy - cy) * tp + .35) for x, yy in bottom]
        K.slab_loft(st, bottom, top, z0, z1)
        yf, ytop = p0[1], cy + (p0[1] - cy) * tp + .35
        th = math.atan2(ytop - yf, z1 - z0)
        for zw in (z1 - .35, z1 - .7) if ti == 0 else (z1 - .4,):
            yw = yf + (ytop - yf) * (zw - z0) / (z1 - z0) - .03
            wx = abs(p3[0]) * (1 - (1 - tp) * (zw - z0) / (z1 - z0)) * 1.6
            a.part('Step_windows', 'Lamp').box((wx, .04, .12), loc=(0, yw, zw), rot=(-th, 0, 0), bevel=0)
        # Side wall plates and window rows.
        for s in (-1, 1):
            for j in range(int((p2[1] - p3[1]) / 1.1)):
                yy = p3[1] + .6 + j * 1.1
                xw = abs(p3[0]) + (abs(p2[0]) - abs(p3[0])) * (yy - p3[1]) / (p2[1] - p3[1])
                slope = math.atan2(xw * (1 - tp), z1 - z0)
                xm = xw - xw * (1 - tp) * .5
                mat = ('Medical', 'Fuel', 'Fuel', 'MetalSheet')[(j * 3 + ti) % 4]
                a.part(f'Tier_plates_{mat.lower()}', mat).box((.03, .95, (z1 - z0) * .8), loc=(s * (xm + .02), yy,
                                                                                               (z0 + z1) / 2),
                                                               rot=(0, -s * slope, 0), bevel=0)
                a.part('Tier_ribs', 'Armor').box((.08, .1, (z1 - z0) * .92), loc=(s * (xm + .05), yy + .55,
                                                                                   (z0 + z1) / 2),
                                                 rot=(0, -s * slope, 0), bevel=0)
                if j % 2 == 0:
                    a.part('Tier_windows', 'Lamp').box((.03, .6, .1), loc=(s * (xm - xw * (1 - tp) * .3 + .05), yy,
                                                                           z1 - .3),
                                                       rot=(0, -s * slope, 0), bevel=0)
    # Window bands along the tier sides, vent grilles low on the walls.
    for ti, (p0, p1, p2, p3, z0, z1, tp) in enumerate(tiers):
        for s in (-1, 1):
            for zf in ((.35, .62) if ti == 0 else (.5,)):
                z = z0 + (z1 - z0) * zf
                xw = abs(p3[0]) * (1 - (1 - tp) * zf) + .075
                a.part('Tier_bands', 'Lamp').box((.03, (p2[1] - p3[1]) * .8, .07), loc=(s * xw, (p2[1] + p3[1]) / 2 + .2,
                                                                                         z),
                                                 rot=(0, -s * math.atan2(abs(p3[0]) * (1 - tp), z1 - z0), 0), bevel=0)
        if ti < 2:
            k.greebles(a.part('Roof_greebles', 'MetalSheet'), (0, (p3[1] + p2[1]) / 2 + 1.6, z1 + .01), (1, 0, 0),
                       (0, 1, 0), (abs(p3[0]) * 1.4, (p2[1] - p3[1]) * .5), 14, seed=70 + ti, height=(.08, .3),
                       vents=a.part('Roof_vents', 'Undercarriage'), avoid=[((0, 10.0, z1), 2.6), ((0, 3.0, z1), 1.6)])
    # Roof kit on the tiers: vents, hatches, small structures.
    for s in (-1, 1):
        K.clutter(a, 'Roof_fittings', 'MetalSheet', s * .6 if s > 0 else -3.2, 3.2 if s > 0 else -.6, 5.0, 11.8, 3.4,
                  9, seed=41 + s, size=(.3, .8), height=(.12, .4))
    if broken:
        _broken_tower(a)
        return
    # The tower and the bridge.
    k.extrude(a.part('Tower', 'Fuel'), [(-1.1, -1.25), (1.1, -1.25), (1.4, .1), (1.1, 1.3), (-1.1, 1.3), (-1.4, .1)],
              1.9, loc=(0, 10.1, 6.7), axis='Z', chamfer=.06, taper=(.88, .9))
    for z in (5.95, 6.45, 7.0):
        a.part('Tower_windows', 'Lamp').box((2.1, 2.5, .07), loc=(0, 10.13, z), bevel=0)
    for x, y in ((1.2, 8.95), (-1.2, 8.95), (1.2, 11.3), (-1.2, 11.3)):
        a.part('Tower_ribs', 'MetalSheet').box((.14, .14, 1.9), loc=(x, y, 6.65), bevel=0)
    br = a.part('Bridge', 'MetalSheet')
    k.sharp_loft(br, [[(-2.3, 8.7, 7.55), (2.3, 8.7, 7.55), (2.3, 10.8, 7.55), (-2.3, 10.8, 7.55)],
                      [(-2.5, 8.45, 8.0), (2.5, 8.45, 8.0), (2.45, 10.9, 8.0), (-2.45, 10.9, 8.0)],
                      [(-2.05, 8.8, 8.45), (2.05, 8.8, 8.45), (2.0, 10.7, 8.45), (-2.0, 10.7, 8.45)]], chamfer=.05)
    a.part('Bridge_windows', 'Lamp').box((4.2, .04, .16), loc=(0, 8.55, 8.1), rot=(.55, 0, 0), bevel=0)
    for x in (-1.4, -.45, .45, 1.4):
        a.part('Bridge_mullions', 'Armor').box((.05, .06, .2), loc=(x, 8.53, 8.1), rot=(.55, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Bridge_windows', 'Lamp').box((.04, 1.3, .14), loc=(s * 2.47, 9.6, 8.0), bevel=0)
        a.part('Aurel_stripes', 'Team').box((.06, 2.1, .18), loc=(s * 2.42, 9.7, 7.72), bevel=0)
    # The sensor mast, its yards, dishes, the APS emitter on top.
    a.part('Mast', 'Steel').cyl(.13, 1.6, loc=(0, 9.9, 9.2), seg=8, bevel=0)
    a.part('Mast', 'Steel').box((2.6, .07, .07), loc=(0, 9.9, 9.55), bevel=0)
    for s in (-1, 1):
        K.dish(a.part('Tower_dishes', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (s * 1.55, 10.2, 8.75), r=.55,
               normal=(s * .5, -.4, .8), seg=16)
        a.part('Mast_tips', 'LavaGlow').sphere(.06, loc=(s * 1.3, 9.9, 9.6), seg=6, rings=3)
    m = a.pivot('Mount_APS', (0, 9.9, 10.0))
    k.lathe(a.part('Aps_emitter', 'Armor', m), [(.36, 0), (.36, .14), (.2, .28), (0, .31)], seg=12)
    a.part('Aps_glow', 'Energy', m).sphere(.13, loc=(0, -.08, .3), seg=8, rings=4)
    # The uplink: the satellite dish on its gimbal over the first tier's roof.
    u = a.pivot('Uplink', (0, 3.0, 4.2))
    a.part('Uplink_strut', 'Steel', u).cyl(.18, 1.0, loc=(0, 0, -.55), seg=10, bevel=0)
    a.part('Uplink_strut', 'Steel', u).box((.9, .3, .2), loc=(0, 0, -.05), bevel=0)
    K.dish(a.part('Uplink_dish', 'PlasterWhite', u), a.part('Uplink_feed', 'Steel', u), (0, -.1, .1), r=1.25,
           normal=(0, -.55, .85), seg=22)
    a.part('Uplink_glow', 'Energy', u).sphere(.09, loc=(0, -.6, 1.05), seg=8, rings=4)
    K.tone(a, 'Uplink', k=.9)


def _broken_tower(a):
    """The wreck's command tower snapped off: a torn stump (jagged plates, hanging cables), the APS emitter on its
    remains (Mount_APS), the bridge thrown down beside the hull on its side, the mast across the deck."""
    k.extrude(a.part('Tower', 'Fuel'), [(-1.1, -1.25), (1.1, -1.25), (1.4, .1), (1.1, 1.3), (-1.1, 1.3), (-1.4, .1)],
              .9, loc=(0, 10.1, 6.2), axis='Z', chamfer=.04, taper=(.95, .96))
    rng = random.Random(23)
    for i in range(9):
        u = i * TAU / 9
        h = rng.uniform(.3, 1.1)
        a.part('Torn_stump', 'Charred').box((.5, .08, h), loc=(math.cos(u) * 1.15, 10.1 + math.sin(u) * 1.15, 6.65 + h / 2),
                                            rot=(rng.uniform(-.3, .3), rng.uniform(-.3, .3), u + R90), bevel=0)
    for j in range(4):
        a.part('Hanging_cables', 'Undercarriage').tube([(rng.uniform(-.8, .8), 10.1 + rng.uniform(-.8, .8), 6.7),
                                                        (rng.uniform(-1.6, 1.6), 10.1 + rng.uniform(-1.4, 1.4), 5.7),
                                                        (rng.uniform(-2.4, 2.4), 10.1 + rng.uniform(-1.6, 1.6), 4.9)],
                                                       .05, seg=4)
    m = a.pivot('Mount_APS', (.5, 10.6, 6.65))
    k.lathe(a.part('Aps_emitter', 'Armor', m), [(.36, 0), (.36, .14), (.2, .28), (0, .31)], seg=12)
    a.part('Aps_glow', 'Energy', m).sphere(.13, loc=(0, -.08, .3), seg=8, rings=4)
    # The bridge down on the ground off the left flank, rolled on its side, and the mast across the tier roofs.
    br = a.part('Bridge', 'MetalSheet')
    k.block(br, (4.6, 2.3, 1.0), loc=(10.6, 2.5, -1.15), rot=(0, 1.35, .35), chamfer=.06)
    a.part('Bridge_windows', 'Charred').box((.05, 2.1, .2), loc=(10.2, 2.5, -.6), rot=(0, 1.35, .35), bevel=0)
    a.part('Mast', 'Steel').cyl(.13, 4.2, loc=(1.2, 9.0, 4.85), rot=(0, R90 - .2, .5), seg=8, bevel=0)


def _module(a, H):
    """The pressurised module half sunk in the spine forward of the superstructure (an ISS-style can: MMOD shield
    bands, handrails, portholes, the docking port and its hatch ahead of it)."""
    y0, y1 = -8.8, -.8
    zc = H.t(-5.0) - .2
    k.lathe(a.part('Module', 'PlasterWhite'), [(0, 0), (.6, .05), (.95, .3), (1.05, .7), (1.05, y1 - y0 - .7),
                                               (.95, y1 - y0 - .3), (.6, y1 - y0 - .05), (0, y1 - y0)],
            loc=(0, y0, zc), rot=K.BACKWARD, seg=20)
    for j in range(7):
        yy = y0 + .9 + j * 1.05
        k.ring(a.part('Module_bands', 'Medical'), [(1.06, -.06), (1.1, -.06), (1.1, .06), (1.06, .06)],
               loc=(0, yy, zc), rot=K.BACKWARD, seg=20)
    for s in (-1, 1):
        a.part('Handrails', 'Hazard').tube([(s * .55, y0 + .9, zc + .92), (s * .55, y1 - .9, zc + .92)], .025, seg=4)
        K.portholes(a, [(s * .7, y0 + 2.0 + j * 1.6, zc + .8) for j in range(4)], (s * .65, 0, .75), r=.11)
    # The docking port ahead of it.
    yd = -12.0
    zd = H.t(yd)
    k.lathe(a.part('Docking_port', 'Steel'), [(.95, zd - .3), (.95, zd + .2), (.8, zd + .32), (.8, zd + .45),
                                              (.6, zd + .5)], loc=(0, yd, 0), seg=20)
    a.part('Docking_hatch', 'Armor').cyl(.55, .06, loc=(0, yd, zd + .52), seg=16, bevel=0)
    for j in range(3):
        v = j * TAU / 3
        a.part('Docking_petals', 'Fuel').box((.3, .12, .3), loc=(math.cos(v) * .7, yd + math.sin(v) * .7, zd + .6),
                                             rot=(0, 0, v + R90), bevel=0)


def _radiators(a, H, ys=(1.4, 11.2)):
    """ISS-style radiator wings on the aft shoulders: three white panels each on a boom, raised 28 degrees, their
    coolant ribs and hinge blocks."""
    for s in (-1, 1):
        y0, y1 = ys
        for j in range(3):
            yc = y0 + .3 + j * (y1 - y0 - .6) / 3 + (y1 - y0 - .6) / 6
            L = (y1 - y0 - .6) / 3 - .15
            x = H.w(yc) * .78
            z = H.top(x, yc) + .5
            rot = (0, -s * .5, 0)
            a.part('Radiators', 'PlasterWhite').box((1.4, L, .05), loc=(s * (x + .55), yc, z + .32), rot=rot, bevel=0)
            for r in range(6):
                a.part('Radiator_ribs', 'Pipe').box((1.4, .025, .025), loc=(s * (x + .55), yc - L / 2 + .2 + r * (L - .4)
                                                                         / 5, z + .36), rot=rot, bevel=0)
            a.part('Radiator_hinges', 'Armor').box((.25, .35, .4), loc=(s * x, yc, z), bevel=0)
        a.part('Radiator_booms', 'Steel').tube([(s * H.w(y0) * .78, y0 + .2, H.top(H.w(y0) * .78, y0) + .45),
                                                (s * H.w(y1) * .78, y1 - .2, H.top(H.w(y1) * .78, y1) + .45)],
                                               .05, seg=6)


def _hull_kit(a, H, proto=False):
    """Fourth-tier fittings: antennas with red tips, hull and nav lights, RCS quads along the hull, star trackers,
    hatches with their frames, the ventral sensor keel."""
    for j, (x, y) in enumerate(((1.1, -15.5), (-1.3, -13.8), (3.5, -8.0), (-3.6, -7.6), (4.6, 1.0), (-4.7, 1.4))):
        h = .8 + .3 * (j % 3)
        z = H.top(x, y)
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, z), h=h, r=.03)
        a.part('Antenna_tips', 'LavaGlow').sphere(.05, loc=(x, y, z + h + .05), seg=6, rings=3)
    for s in (-1, 1):
        for y in (-16.0, -6.5, 3.0, 11.0):
            p, n = H.on_top(s * H.w(y) * .985, y, .04)
            a.part('Hull_lights', 'Lamp').box((.1, .18, .06), loc=p, rot=surf_rot(n), bevel=0)
        for y in (-14.5, 8.5):
            rcs_quad(a, ('Rcs_blocks', 'Armor'), ('Rcs_nozzles', 'Steel'), (s * (H.w(y) + .05), y, .32), (s, 0, 0))
        # Star tracker heads and crew hatches.
        x, y = s * 1.7, -14.6
        a.part('Star_trackers', 'Undercarriage').cyl(.17, .3, loc=(x, y, H.top(x, y) + .12), seg=10, bevel=0)
        a.part('Star_tracker_glass', 'Glass').cyl(.12, .02, loc=(x, y, H.top(x, y) + .28), seg=10, bevel=0)
        for y in (-10.5, -2.5):
            x = s * H.w(y) * .55
            p, n = H.on_top(x, y, .03)
            a.part('Hatches', 'Armor').box((.7, .9, .04), loc=p, rot=surf_rot(n), bevel=0)
            q, _ = H.on_top(x, y, .055)
            a.part('Hatch_frames', 'Hazard').box((.78, .06, .03), loc=(q[0], q[1] - .47, q[2]), rot=surf_rot(n),
                                                 bevel=0)
    # The ventral sensor keel forward.
    zb = H.bot(0, -14.0)
    k.extrude(a.part('Keel_sensor', 'Undercarriage'), [(-2.4, 0), (1.6, 0), (1.0, -.5), (-1.8, -.35)], .3,
              loc=(0, -14.0, zb + .05), axis='X', chamfer=.03)
    a.part('Keel_sensor_glass', 'Glass').sphere(.22, loc=(0, -15.6, zb - .18), seg=10, rings=6)


def _flank_kit(a, H, y0=-13.0, y1=11.5, seed=9):
    """Service panels, vents and access boxes along the lower shoulders between the windows and the chine."""
    rng = random.Random(seed)
    y = y0
    while y < y1:
        for s in (-1, 1):
            if rng.random() < .55:
                f = rng.uniform(.91, .955)
                p, n = H.on_top(s * f * H.w(y), y, .04)
                kind = rng.random()
                if kind < .4:
                    a.part('Flank_vents', 'Undercarriage').box((.16, rng.choice((.5, .7, .9)), .04), loc=p,
                                                               rot=surf_rot(n), bevel=0)
                elif kind < .75:
                    a.part('Flank_boxes', 'MetalSheet').box((.2, rng.choice((.35, .5)), .14), loc=p, rot=surf_rot(n),
                                                            bevel=0)
                else:
                    a.part('Flank_hatches', 'Armor').box((.22, .55, .05), loc=p, rot=surf_rot(n), bevel=0)
        y += rng.choice((.6, .8, 1.0))


def _hull_details(a, H):
    """The coilgun barbette and PD tower fairings, the spine ridge with its running lights, the Aurel stripes."""
    sp = a.part('Spine', 'MetalSheet')
    for y0, y1 in ((-17.6, -12.9), (-11.1, -9.1)):
        sp.limb((0, y0, H.t(y0) - .02), (0, y1, H.t(y1) - .02), .5, .32, bevel=.03)
    for y in range(-17, -9, 2):
        a.part('Spine_lights', 'Lamp').box((.12, .12, .05), loc=(0, y + .3, H.t(y + .3) + .15), bevel=0)


def silver_bug(a, wreck=False):
    """Icarus, redrawn (module docstring). Runtime nodes: Turret > Muzzle_main, Mount_gun .. .005 with Muzzle_gun ..,
    the 40 mm turrets' Muzzle_b1 / _b2, Pd_laser_l / _r, Pod_bay > Muzzle_missile, Uplink, Thruster_main / _fl / _fr /
    _rl / _rr, Mount_APS, Engine_flame .. .006."""
    K.suffixed(a)
    H = ICARUS
    hull_skin(a, H)
    leading_edges(a, H)
    hull_plating(a, H, SB_KEEP)
    panel_lines(a, H)
    belly_tiles(a, H)
    shoulder_windows(a, H, -15.5, 11.5)
    stripes(a, H, -17.8, -3.0, fs=(.95, .6))
    _hull_details(a, H)
    _flank_kit(a, H)
    _module(a, H)
    _superstructure(a, H, broken=wreck)
    _radiators(a, H, ys=(.5, 4.4))
    _main_laser(a, H)
    _coilgun(a, H, 0, 4.35, -1.4)
    _coilgun(a, H, 1, -4.35, -1.4)
    _beam_director(a, 0, (2.9, 1.25, 3.4), 2)
    _beam_director(a, 1, (-2.9, 1.25, 3.4), 3)
    _crash_turret(a, H, 4, 1, 7.0)
    _crash_turret(a, H, 5, -1, 7.0)
    _pd_laser(a, H, 'Pd_laser_l', 2.4, -6.0, '')
    _pd_laser(a, H, 'Pd_laser_r', -2.4, -6.0, '_r')
    _pod_bay(a, H)
    _sb_engines(a, H)
    _nacelle(a, 1)
    _nacelle(a, -1)
    _rcs_pod(a, H, 1)
    _rcs_pod(a, H, -1)
    _hull_kit(a, H)
    merge(a)
    k.clean(a)


# ============================================================================= silver_bug_wreck
WRECK_LIFT = 2.0      # raises the crashed ship so its belly rests on the ground (origin on the ground)


def silver_bug_wreck(a):
    """Icarus crashed, for its ground phase (the crash's "form"): the redrawn ship itself, every runtime node kept (the
    crash turrets Mount_gun.004 / .005 and the lasers .002 / .003 fire on from it: tiers.crash.guns 3-6), raised so its
    belly lies on the ground, its main laser and bay doors dug in; the earth it ploughed up heaped along its flanks and
    ahead of its nose, a scorched ground disc, torn and burnt plates, soot, debris thrown round it. No engine flames."""
    import bpy
    silver_bug(a, wreck=True)
    for name in [n for n in a.pivots if n.startswith('Engine_flame')]:
        bpy.data.objects.remove(a.pivots.pop(name))
    for o in a.pivots.values():
        if o.parent is None:
            o.location.z += WRECK_LIFT
    for (name, mat, parent), sh in a.shapes.items():
        if parent is None:
            for v in sh.bm.verts:
                v.co.z += WRECK_LIFT
    for fx in getattr(a, '_fx35', []):
        if fx[1] is not None:
            fx[1].z += WRECK_LIFT
    H = ICARUS
    rng = random.Random(1977)
    L = WRECK_LIFT
    # Ploughed earth: lumps along both flanks (bigger towards the nose, where it dug in) and a berm ahead of the nose.
    dirt = a.part('Earth_berms', 'Dirt', flat=True)
    for s_ in (-1, 1):
        y = -18.0
        while y < 9.0:
            w = H.w(y)
            r = (.7 + .9 * (1 - (y + 18) / 27)) * rng.uniform(.6, 1.35)
            if rng.random() < .82:
                dirt.ico(r, loc=(s_ * (w + r * .5 + rng.uniform(-.2, .9)), y + rng.uniform(-.4, .4), -r * .3),
                         sub=1, jitter=.35, seed=y * 1.7 + s_)
            y += r * rng.uniform(.7, 1.5)
    for j in range(6):
        u = (j - 2.5) / 2.5
        dirt.ico(1.6 - abs(u) * .4, loc=(u * 3.2, H.y0 - 1.6 - abs(u) * 1.2, .3), sub=1, jitter=.3, seed=40 + j)
    # The scorched ground round it.
    ring = [(math.cos(i * TAU / 24) * 15.5 * (1 + .12 * math.sin(i * 2.3)), math.sin(i * TAU / 24) * 22.0 *
             (1 + .1 * math.cos(i * 1.7)) - 1.0, .05) for i in range(24)]
    a.part('Scorch_ground', 'Charred', flat=True).mesh([(0, -1.0, .05)] + ring, [(0, i + 1, (i + 1) % 24 + 1)
                                                                                 for i in range(24)])
    # Torn and burnt plates on the upper hull, soot over the breaks.
    for i in range(34):
        y = rng.uniform(-16.0, 11.0)
        x = rng.uniform(-.9, .9) * H.w(y)
        p, n = H.on_top(x, y, .05)
        p = (p[0], p[1], p[2] + L)
        r_ = surf_rot(n)
        r_ = (r_[0] + rng.uniform(-.5, .5), r_[1] + rng.uniform(-.5, .5), r_[2] + rng.uniform(-1, 1))
        mat = 'Charred' if i % 3 else 'MetalSheet'
        a.part(f'Torn_plates_{mat.lower()}', mat).box((rng.uniform(.3, .9), rng.uniform(.4, 1.1), .03), loc=p,
                                                      rot=r_, bevel=0)
        if i % 4 == 0:
            K.soot(a, p, radius=rng.uniform(1.2, 2.2), k=.55)
    for p in ((0, -17.0, .4 + L), (4.6, -11.0, .8 + L), (-8.0, 11.0, .4 + L), (0, 15.5, .6 + L), (0, 8.0, 6.0 + L)):
        K.soot(a, p, radius=2.6, k=.5)
    # Debris thrown round it: plates, struts, a tile shower.
    for i in range(26):
        ang = rng.uniform(0, TAU)
        d = rng.uniform(9.0, 17.0)
        x, y = math.cos(ang) * d * .75, math.sin(ang) * d - 1.0
        mat = rng.choice(('MetalSheet', 'Charred', 'Fuel', 'Undercarriage'))
        k.block(a.part(f'Debris_{mat.lower()}', mat), (rng.uniform(.3, 1.2), rng.uniform(.3, 1.4), rng.uniform(.08, .4)),
                loc=(x, y, .15), rot=(rng.uniform(-.4, .4), rng.uniform(-.4, .4), rng.uniform(0, TAU)), chamfer=.02)
    merge(a)
    k.clean(a)


# ============================================================================= icarus_mk0 (the prototype)
MK_KEEP = [(-4.3, 4.3, .2, 12.7), (-1.6, 1.6, -9.0, -.6), (1.6, 3.2, -7.0, -4.8), (-3.2, -1.6, -7.0, -4.8),
           (5.0, 7.6, -1.0, 11.5), (-7.6, -5.0, -1.0, 11.5)]


def _mk_tower(a, H):
    """The unfinished superstructure: the first tier only (primer and bare panels), an open lattice tower over it with
    the temporary cabin on top (window band, railings, a work lamp), the APS emitter on the cabin (Mount_APS)."""
    st = a.part('Superstructure', 'Crate')
    bottom = [(-4.0, .4), (4.0, .4), (4.2, 12.6), (-4.2, 12.6)]
    cy = sum(p[1] for p in bottom) / 4
    top = [(x * .86, cy + (y - cy) * .86 + .35) for x, y in bottom]
    K.slab_loft(st, bottom, top, 1.1, 3.0)
    a.part('Step_windows', 'Lamp').box((5.6, .04, .12), loc=(0, .58, 2.6), rot=(-.5, 0, 0), bevel=0)
    # The roof not closed yet: two open bays with their frames, tarps over a third, crates and test racks.
    for yc in (2.6, 5.4):
        a.part('Roof_bays', 'Undercarriage').box((4.4, 2.2, .03), loc=(0, yc, 3.01), bevel=0)
        for x in (-1.6, -.5, .6, 1.7):
            a.part('Roof_frames', 'Steel').box((.1, 2.3, .16), loc=(x, yc, 3.08), bevel=0)
        for e in (-1, 1):
            a.part('Roof_frames', 'Steel').box((4.5, .1, .16), loc=(0, yc + e * 1.1, 3.08), bevel=0)
    a.part('Tarps', 'Canvas').loft([[(-2.4, 6.9, 3.02), (2.4, 6.9, 3.02), (2.4, 6.9, 3.12), (-2.4, 6.9, 3.12)],
                                    [(-2.5, 7.8, 3.35), (2.5, 7.8, 3.38), (2.5, 7.8, 3.48), (-2.5, 7.8, 3.45)],
                                    [(-2.4, 8.4, 3.02), (2.4, 8.4, 3.02), (2.4, 8.4, 3.12), (-2.4, 8.4, 3.12)]], bevel=0)
    for e in (-1, 1):
        a.part('Tarp_straps', 'Hazard').box((.08, 1.6, .5), loc=(e * 1.2, 7.65, 3.2), rot=(0, 0, 0), bevel=0)
        K.crate(a.part('Crates', 'Crate'), a.part('Crate_bands', 'Steel'), (.8, .6, .5), (e * 2.9, 11.4, 3.0))
        k.block(a.part('Test_racks', 'Armor'), (.7, 1.2, 1.1), loc=(e * 2.6, 1.2, 3.55), chamfer=.04)
        for j in range(4):
            a.part('Test_rack_lights', 'SignalGreen' if j % 2 else 'Alloy').box((.06, .08, .06),
                                                                                 loc=(e * 2.6 - e * .36, .8 + j * .25,
                                                                                      3.75), bevel=0)
    for s in (-1, 1):
        for j in range(10):
            yy = 1.0 + j * 1.15
            mat = ('MetalSheet', 'Crate', 'Concrete')[j % 3]
            a.part(f'Tier_plates_{mat.lower()}', mat).box((.03, .95, 1.6), loc=(s * 3.9, yy, 2.35),
                                                           rot=(0, -s * .26, 0), bevel=0)
    # The lattice tower: four legs, battens, diagonals.
    legs = a.part('Scaffold', 'Steel')
    pts = [(-1.3, 8.5), (1.3, 8.5), (1.3, 11.2), (-1.3, 11.2)]
    z0, z1 = 3.0, 7.5
    for x, y in pts:
        legs.limb((x, y, z0), (x * .85, y + (9.85 - y) * .15, z1), .14, .14, bevel=0)
    for z in (4.4, 5.4, 6.4, 7.4):
        f = (z - z0) / (z1 - z0) * .15
        ring = [(x * (1 - f), y + (9.85 - y) * f, z) for x, y in pts]
        for p, q in zip(ring, ring[1:] + ring[:1]):
            legs.limb(p, q, .08, .08, bevel=0)
    for z in (3.9, 4.9, 5.9, 6.9):
        f0 = (z - .5 - z0) / (z1 - z0) * .15
        f1 = (z + .5 - z0) / (z1 - z0) * .15
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            legs.limb((x0 * (1 - f0), y0 + (9.85 - y0) * f0, z - .5), (x1 * (1 - f1), y1 + (9.85 - y1) * f1, z + .5),
                      .05, .05, bevel=0)
    # A ladder and the cable run up the tower.
    K.ladder(a.part('Ladders', 'Hazard'), (1.35, 9.9, 3.0), (1.2, 9.9, 7.5), width=.45)
    a.part('Cable_runs', 'Charred').tube([(-1.2, 11.0, 3.0), (-1.05, 10.7, 5.5), (-1.0, 10.6, 7.6)], .07, seg=5)
    # The temporary cabin.
    k.block(a.part('Bridge', 'Concrete'), (3.4, 2.6, 1.1), loc=(0, 9.85, 8.05), chamfer=.06)
    a.part('Bridge_windows', 'Lamp').box((3.0, .04, .3), loc=(0, 8.53, 8.15), bevel=0)
    for s in (-1, 1):
        a.part('Bridge_windows', 'Lamp').box((.04, 1.8, .26), loc=(s * 1.71, 9.85, 8.15), bevel=0)
    K.railing(a.part('Railings', 'Hazard'), [(-1.7, 8.55, 8.6), (1.7, 8.55, 8.6), (1.7, 11.15, 8.6),
                                             (-1.7, 11.15, 8.6), (-1.7, 8.55, 8.6)], h=.55, post=.85)
    K.lamp(a, (1.4, 8.5, 8.85), facing=(0, -1, -.4), r=.12)
    a.part('Mast', 'Steel').cyl(.08, 1.2, loc=(-.9, 10.6, 9.2), seg=6, bevel=0)
    a.part('Mast_tips', 'LavaGlow').sphere(.07, loc=(-.9, 10.6, 9.85), seg=6, rings=3)
    m = a.pivot('Mount_APS', (.3, 10.4, 8.6))
    k.lathe(a.part('Aps_emitter', 'Armor', m), [(.32, 0), (.32, .12), (.18, .25), (0, .28)], seg=12)
    a.part('Aps_glow', 'Energy', m).sphere(.11, loc=(0, -.07, .27), seg=8, rings=4)


def _mk_spine(a, H):
    """The prototype's spine: no module yet, a lattice keel truss along the centre line carrying three propellant
    spheres and their plumbing, a cable tray, the docking ring's bare adapter."""
    tr = a.part('Spine_truss', 'Steel')
    y0, y1 = -12.5, -.8
    for e in (-1, 1):
        tr.tube([(e * .55, y, H.t(y) + .5) for y in (y0, -8.0, -4.0, y1)], .07, seg=6)
        tr.tube([(e * .55, y, H.t(y) + .02) for y in (y0, -8.0, -4.0, y1)], .07, seg=6)
    for j in range(13):
        y = y0 + j * (y1 - y0) / 12
        z = H.t(y)
        for e in (-1, 1):
            tr.limb((e * .55, y, z + .02), (e * .55, y, z + .5), .05, .05, bevel=0)
        tr.limb((-.55, y, z + .5), (.55, y, z + .5), .05, .05, bevel=0)
        if j < 12:
            yn = y + (y1 - y0) / 12
            tr.limb((-.55, y, z + .02), (.55, yn, H.t(yn) + .5), .035, .035, bevel=0)
    for y, r in ((-10.5, .75), (-6.8, .85), (-3.0, .8)):
        a.part('Prop_spheres', 'Fuel').sphere(r, loc=(0, y, H.t(y) + .3 + r * .55), seg=18, rings=10)
        a.part('Prop_sphere_bands', 'Armor').torus(r * 1.0, .04, loc=(0, y, H.t(y) + .3 + r * .55), seg=18, ring=4)
    a.part('Feed_lines', 'Pipe').tube([(.5, -10.5, H.t(-10.5) + .6), (.7, -6.8, H.t(-6.8) + .6),
                                       (.6, -3.0, H.t(-3.0) + .6), (.5, -.6, H.t(-.6) + .5)], .07, seg=6)
    k.lathe(a.part('Docking_port', 'Crate'), [(.85, H.t(-14.0) - .3), (.85, H.t(-14.0) + .25), (.7, H.t(-14.0) + .3)],
            loc=(0, -14.0, 0), seg=16)


def _mk_tanks(a, H):
    """The strap-on propellant tanks along the flanks (where the finished ship has its nacelles and sponsons): white
    tanks with their bands, straps, the feed lines into the hull, the vent valves."""
    for s in (-1, 1):
        x, z = s * 6.55, .35
        k.lathe(a.part('Ext_tanks', 'Fuel'), [(0, 0), (.55, .15), (.95, .7), (1.05, 1.6), (1.05, 9.4), (.95, 10.3),
                                              (.55, 10.85), (0, 11.0)], loc=(x, -1.2, z), rot=K.BACKWARD, seg=20)
        for j in range(5):
            k.ring(a.part('Ext_tank_bands', 'Armor'), [(1.06, -.07), (1.1, -.07), (1.1, .07), (1.06, .07)],
                   loc=(x, .9 + j * 1.95, z), rot=K.BACKWARD, seg=20)
        for y in (.8, 4.6, 8.4):
            w = H.w(y)
            a.part('Tank_struts', 'Steel').limb((s * (w - .2), y, -.05), (s * 5.6, y, .35), .16, .16, bevel=0)
        a.part('Feed_lines', 'Pipe').tube([(x, 9.7, z - .6), (s * 5.4, 10.6, -.6), (s * 4.0, 12.4, -.6)], .12, seg=8)
        a.part('Tank_vents', 'BarrelRed').cyl(.09, .3, loc=(x, 0.0, z + 1.12), seg=8, bevel=0)
        for j in range(4):
            a.part('Tank_stripes', 'Charred').box((.05, .7, .8), loc=(x + s * 1.04, 1.7 + j * 2.0, z), bevel=0)


def _mk_test_kit(a, H):
    """Test-article fittings: the nose air-data boom (striped), photogrammetry targets, hazard bands round the
    unfinished hatches, cable runs and instrumentation boxes taped on the deck, the strapped-down covers over the
    coilgun rings that are not fitted yet."""
    y0 = H.y0
    boom = a.part('Nose_boom', 'Steel')
    boom.cyl(.06, 2.6, loc=(0, y0 - 1.2, 0), rot=(R90, 0, 0), seg=8, bevel=0)
    for j in range(5):
        a.part('Nose_boom_bands', 'BarrelRed' if j % 2 else 'PlasterWhite').cyl(.075, .32, loc=(0, y0 - .4 - j * .45,
                                                                                               0),
                                                                                rot=(R90, 0, 0), seg=8, bevel=0)
    a.part('Nose_boom_vanes', 'Armor').box((.5, .08, .02), loc=(0, y0 - 2.2, 0), bevel=0)
    a.part('Nose_boom_vanes', 'Armor').box((.02, .08, .5), loc=(0, y0 - 2.0, 0), bevel=0)
    # Photogrammetry targets: black and white quartered discs along the hull.
    rng = random.Random(5)
    for j in range(16):
        y = -16.0 + j * 1.75
        s = 1 if j % 2 else -1
        f = rng.choice((.35, .55, .78))
        p, n = H.on_top(s * f * H.w(y), y, .035)
        rot = surf_rot(n)
        a.part('Targets_white', 'PlasterWhite').cyl(.24, .015, loc=p, rot=rot, seg=12, bevel=0)
        q, _ = H.on_top(s * f * H.w(y), y, .045)
        a.part('Targets_black', 'Charred').box((.17, .17, .012), loc=q, rot=surf_rot(n), bevel=0)
    # Covered coilgun rings (not fitted yet), with hazard bands.
    for s in (-1, 1):
        x, y = s * 4.35, -1.4
        zs = H.top(x, y)
        k.lathe(a.part('Coil_covers', 'Crate'), [(1.45, zs - .4), (1.45, zs + .2), (1.3, zs + .3)], loc=(x, y, 0),
                seg=20)
        a.part('Coil_covers_cap', 'Canvas').cyl(1.32, .1, loc=(x, y, zs + .34), seg=20, bevel=0)
        for e in (-1, 1):
            a.part('Cover_straps', 'Hazard').box((2.7, .12, .03), loc=(x, y + e * .5, zs + .41), bevel=0)
    # Instrumentation boxes and the cable runs between them.
    for j, (x, y) in enumerate(((1.8, -13.5), (-2.0, -11.8), (3.0, -8.8), (-2.9, -3.5), (2.4, -.2))):
        p, n = H.on_top(x, y, .1)
        a.part('Test_boxes', 'Hazard' if j % 2 else 'Armor').box((.45, .6, .3), loc=p, rot=surf_rot(n), bevel=0)
    pts = [H.on_top(x, y, .06)[0] for x, y in ((1.8, -13.5), (.5, -12.5), (-2.0, -11.8), (-1.6, -10), (-2.9, -3.5))]
    a.part('Cable_runs', 'Charred').tube(pts, .04, seg=4)


def _mk_rcs(a, H):
    """The prototype's forward RCS blocks on the chine (no canards yet) and its thruster quads."""
    for s in (-1, 1):
        y = -11.0
        x = s * (H.w(y) + .15)
        k.block(a.part('Rcs_blocks', 'Crate'), (.55, 1.6, .7), loc=(x, y, .1), chamfer=.05)
        for yy in (-11.5, -10.5):
            for d in ((s, 0, 0), (0, 0, 1)):
                q = (x + d[0] * .3, yy, .1 + d[2] * .38)
                a.part('Rcs_nozzles', 'Steel').cyl(.07, .12, loc=q, rot=K.rot_to(d), seg=6, r2=.05, bevel=0)


def icarus_mk0(a):
    """Icarus Mk.0, the prototype (module docstring). Runtime nodes at silver_bug's places: Turret > Muzzle_main,
    Pd_laser_l, Pod_bay > Muzzle_missile, Thruster_main, Mount_APS, Engine_flame .. .002."""
    K.suffixed(a)
    H = MK0

    def missing(x, y):
        # Open bays: two rows of panels not fitted yet on each shoulder.
        return (2.0 < abs(x) < 3.6 and -9.5 < y < -6.5) or (3.2 < abs(x) < 4.9 and 2.0 < y < 6.5) or \
            (.6 < abs(x) < 2.0 and -15.5 < y < -13.6)
    hull_skin(a, H, upper='MetalSheet', lower='MetalSheet')
    leading_edges(a, H, y_end=4.0)
    hull_plating(a, H, MK_KEEP, tones=(('Crate', .45), ('MetalSheet', .35), ('Concrete', .2)), seed=19, density=.9, missing=missing)
    panel_lines(a, H, every=1.9)
    belly_tiles(a, H, y_to=-1.0, patches=60)
    shoulder_windows(a, H, -15.0, -4.0, pitch=1.2)
    stripes(a, H, -17.5, -9.0, fs=(.95,), mat='Hazard')
    _mk_spine(a, H)
    _mk_tower(a, H)
    _main_laser(a, H, proto=True)
    _pd_laser(a, H, 'Pd_laser_l', 2.4, -6.0, '', z=ICARUS.top(2.4, -6.0) + .45, proto=True)
    _pd_laser(a, H, None, -2.4, -6.0, '_r', capped=True)
    _pod_bay(a, H, pods=1)
    _sb_engines(a, H, proto=True)
    _mk_tanks(a, H)
    _mk_rcs(a, H)
    _mk_test_kit(a, H)
    merge(a)
    k.clean(a)


BUILDERS = {
    'silver_bug': (silver_bug, dict(ao_distance=1.2, grime_height=.2, ground=False)),
    'icarus_mk0': (icarus_mk0, dict(ao_distance=1.2, grime_height=.2, ground=False)),
    'silver_bug_wreck': (silver_bug_wreck, dict(ao_distance=1.2, grime_height=1.2)),
}
