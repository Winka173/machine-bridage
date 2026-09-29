"""Machine Brigade boss "Silver Bug" mk2 (prompt 19): the final boss stops being a flying saucer
(mb_boss_saucer.py, removed) and becomes a militarised orbital spacecraft in the spirit of Buran /
X-37 / a militarised Space Shuttle, plus its crash-landed wreck for phase 3's ground fortress, the
small satellite it deploys and the drop pod that lands the player's vehicles.

Conventions as in mb_boss_saucer.py: metres, +Z up, Blender -Y is the front, the vehicle's left is
+X. A design position given as [right, forward, up] is therefore Blender (-right, -forward, up)
(see `_pos`). Team / TeamGlow parts are recoloured per army at runtime. Touching parts overlap or
stand at least 1 cm apart, so no two visible faces are coplanar.

  * silver_bug: a 34 m military space-shuttle gunship, bare silver panels with rivet rows, dark
    heat-shield tiles on the belly and wing leading edges, a dorsal spine and a 3-bell main engine
    cluster at the tail. It flies: origin at the hull centre. Named nodes (see NODES below for the
    exact spot each sits at): `Turret` (ventral main-laser yaw pivot, barrel `Main_cannon[_*]`,
    `Muzzle_main` at the lens), `Mount_gun` / `Mount_gun.001` (upper-flank coilgun turrets,
    `Muzzle_gun` / `Muzzle_gun.001` at the rail tips), `Mount_mg` / `Mount_mg.001` (spine flak
    turrets, `Muzzle_mg` / `Muzzle_mg.001`), `Pd_laser_l` / `Pd_laser_r` (shoulder point-defence
    lasers), `Thruster_main` (the engine cluster), `Thruster_fl` / `_fr` / `_rl` / `_rr`
    (manoeuvring thruster pods), `Pod_bay` (ventral bay, `Muzzle_missile` inside) and `Uplink` (the
    dorsal dish).
  * silver_bug_wreck: the same ship crashed, origin on the ground under the hull centre (ground=True):
    the same named nodes at the same right/forward spot, raised so the hull rests on the ground. A
    cracked, buckled hull, one wing torn off and lying beside it, a scorched belly, the main engine
    torn open, the coilgun and flak turrets deployed, a scorched crater ring under the hull and six
    debris piles at the fixed spots the game places invisible cover (DEBRIS below).
  * bug_satellite: a small military satellite, about 5 m (bus, two solar wings, a dish, a rod
    magazine). Origin at its centre; it flies.
  * drop_pod: a 6 m capsule/cone that carries one or two vehicles down: a scorched heat shield, a
    retro-rocket ring, fins and a Team stripe. Origin at its centre; it flies.
"""
import math
import random

from mathutils import Vector

from mb_air import BACKWARD, FORWARD, R90, _octagon
from mb_phase2 import _suffixed, dotted

TAU = math.tau


def _pos(right, forward, up=0.0):
    """[right, forward, up] -> Blender (x, y, z): right is Blender -X, forward is Blender -Y."""
    return (-right, -forward, up)


# Named nodes on silver_bug / silver_bug_wreck, as [right, forward, up] from the origin.
NODES = {
    'Turret': (0, 7, -2.8),
    'Mount_gun': (-5, 0, 2.4),
    'Mount_gun.001': (5, 0, 2.4),
    'Mount_mg': (0, 10, 3.0),
    'Mount_mg.001': (0, -9, 3.4),
    'Pd_laser_l': (-3.2, 5, 3.2),
    'Pd_laser_r': (3.2, 5, 3.2),
    'Thruster_main': (0, -15.5, 0.6),
    'Thruster_fl': (-4.5, 11, 0.8),
    'Thruster_fr': (4.5, 11, 0.8),
    'Thruster_rl': (-8, -11, 0.4),
    'Thruster_rr': (8, -11, 0.4),
    'Pod_bay': (0, -4, -2.6),
    'Uplink': (0, -3, 4.2),
}
# The wreck's ring of debris piles the game places invisible cover on: [right, forward, w, d].
DEBRIS = [(-14, 10, 4.0, 2.5), (15, 6, 4.0, 2.5), (-17, -8, 4.0, 2.5), (13, -14, 4.0, 2.5),
          (0, 22, 4.0, 2.5), (-4, -24, 4.0, 2.5)]
LIFT = 2.9  # raises the wreck so the belly rests on the ground


def _node(name, lift=0.0):
    right, forward, up = NODES[name]
    return _pos(right, forward, up + lift)


# ----------------------------------------------------------------------------- hull profile
# (y, half-width, belly z, spine z), nose to tail; the hull is an octagonal-section loft through them.
STATIONS = [
    (-17.0, 0.10, -0.35, -0.15),
    (-15.3, 0.75, -1.15, 0.25),
    (-12.5, 1.65, -1.85, 0.95),
    (-9.0, 2.45, -2.35, 1.55),
    (-4.5, 3.05, -2.65, 1.95),
    (0.0, 3.55, -2.75, 2.10),
    (4.5, 3.50, -2.65, 2.10),
    (9.0, 2.95, -2.35, 1.90),
    (12.5, 2.15, -1.90, 1.55),
    (15.0, 1.30, -1.35, 1.15),
    (15.8, 0.85, -0.95, 0.95),
]


def _at(y, lift=0.0):
    """Interpolated (half-width, belly z, spine z) of the hull profile at y, lift added to the z's."""
    pts = STATIONS
    if y <= pts[0][0]:
        _, hw, zb, zt = pts[0]
    elif y >= pts[-1][0]:
        _, hw, zb, zt = pts[-1]
    else:
        hw = zb = zt = 0.0
        for (y0, hw0, zb0, zt0), (y1, hw1, zb1, zt1) in zip(pts, pts[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / (y1 - y0)
                hw, zb, zt = hw0 + (hw1 - hw0) * t, zb0 + (zb1 - zb0) * t, zt0 + (zt1 - zt0) * t
                break
    return hw, zb + lift, zt + lift


def _hull_rings(lift, wreck):
    rings = []
    for i, (y, hw, zb, zt) in enumerate(STATIONS):
        zb2, zt2, hw2 = zb + lift, zt + lift, hw
        if wreck and 4 <= i <= 6:  # the hull broke its back amidships
            pinch = (0.32, 0.52, 0.28)[i - 4]
            zt2 -= pinch
            hw2 *= 1 - 0.06 * pinch
        rings.append(_octagon(y, hw2, zb2, zt2, k=.32, flat=.66))
    return rings


def _build_hull(a, lift, wreck, rng):
    skin = a.part('Hull', 'Armor' if wreck else 'Steel')
    skin.loft(_hull_rings(lift, wreck), bevel=.02, seg=2)
    # dorsal spine ridge, tapering out towards the nose and tail.
    spine = a.part('Spine', 'Armor')
    for y10 in range(-70, 101, 6):
        y = y10 / 10
        hw, zb, zt = _at(y, lift)
        env = max(0.0, 1 - ((y - 1.5) / 9.2) ** 2)
        if env <= 0.03:
            continue
        w, h = 0.85 * env, 0.5 * env
        spine.box((w, .95, h), loc=(0, y, zt + h / 2 - .04), bevel=.05, seg=2)
    vents = a.part('Spine_vents', 'Undercarriage')
    for y10 in range(-50, 81, 10):
        y = y10 / 10
        hw, zb, zt = _at(y, lift)
        env = max(0.0, 1 - ((y - 1.5) / 9.2) ** 2)
        if env <= 0.2:
            continue
        vents.box((0.3, 0.5, 0.06), loc=(0, y, zt + 0.5 * env + 0.03), bevel=.01, seg=1)
    # dark ceramic heat-shield tiles along the belly centreline.
    tiles = a.part('Heat_tiles', 'Undercarriage')
    for y10 in range(-160, 151, 10):
        y = y10 / 10
        hw, zb, zt = _at(y, lift)
        for xf in (-0.62, -0.2, 0.2, 0.62):
            tiles.box((0.62, 0.62, 0.05), loc=(hw * xf, y, zb - 0.02), bevel=0, seg=1)
    # panel doublers, rivet rows, access hatches and a Day-Glo team stripe down each flank.
    stripe = a.part('Stripe', 'Team')
    doubler = a.part('Panels', 'MetalSheet')
    rivet = a.part('Rivets', 'MetalSheet')
    hatch = a.part('Hatches', 'Steel')
    for y10 in range(-150, 151, 9):
        y = y10 / 10
        hw, zb, zt = _at(y, lift)
        zc = (zb + zt) / 2
        for sx in (-1, 1):
            doubler.box((0.06, 0.82, (zt - zb) * 0.55), loc=(sx * hw * 0.98, y, zc), bevel=.01, seg=2)
            stripe.box((0.05, 0.82, 0.16), loc=(sx * hw * 1.0, y, zc + (zt - zb) * 0.18), bevel=0, seg=1)
            for k in (-1, 1):
                rivet.cyl(.035, .03, loc=(sx * hw * 0.99, y + k * .34, zc), rot=(0, R90, 0), seg=6, bevel=0)
    for y10 in range(-130, 121, 26):
        y = y10 / 10
        hw, zb, zt = _at(y, lift)
        hatch.box((0.5, 0.5, 0.03), loc=(0, y, zt + 0.015), bevel=.01, seg=1)
    # nose windows.
    a.part('Windows', 'Glass').box((0.9, 1.1, 0.1), loc=(0, -13.6, 0.55 + lift), bevel=.02, seg=1)
    if wreck:
        scorch = a.part('Scorch', 'Charred', flat=True)
        for i in range(10):
            y = rng.uniform(-10, 10)
            hw, zb, zt = _at(y, lift)
            scorch.ico((hw * 0.45, 1.1, 0.35), loc=(rng.uniform(-1, 1), y, zb + 0.12), sub=1, jitter=.3,
                      seed=i * 3.1)


# ----------------------------------------------------------------------------- wings and fin
WING_STATIONS = [(3.3, -1.0, 13.0, -0.3, 0.55), (6.0, 3.0, 12.0, 0.0, 0.4), (11.0, 7.0, 11.0, 0.35, 0.15)]


def _wing_ring(x, y_le, y_te, zc, ht):
    y_mid = (y_le + y_te) / 2
    return [(x, y_le, zc), (x, y_mid, zc + ht), (x, y_te, zc), (x, y_mid, zc - ht)]


def _build_wing(a, sx, lift, torn=False):
    """A short double-delta wing on side sx (+1 left / -1 right); torn=True leaves only a stump."""
    if torn:
        rng = random.Random(77 if sx > 0 else 78)
        skin = a.part('Wing_stump', 'Charred', flat=True)
        x0, y_le0, y_te0, zc0, ht0 = WING_STATIONS[0]
        for i in range(5):
            yy = y_le0 + (y_te0 - y_le0) * (i + .5) / 5
            xx = x0 * (0.3 + rng.uniform(0, .35))
            skin.box((xx, 1.5, ht0 * 1.5 + rng.uniform(0, .3)), loc=(sx * xx / 2, yy, zc0 + lift),
                    rot=(0, 0, rng.uniform(-.25, .25)), bevel=.05, seg=1)
        return
    skin = a.part('Wing', 'Steel')
    rings = [_wing_ring(sx * x, y_le, y_te, zc + lift, ht) for x, y_le, y_te, zc, ht in WING_STATIONS]
    skin.loft(rings, bevel=.02, seg=2)
    tiles = a.part('Heat_tiles', 'Undercarriage')
    rivet = a.part('Rivets', 'MetalSheet')
    for x, y_le, y_te, zc, ht in WING_STATIONS:
        tiles.box((0.5, 0.85, 0.06), loc=(sx * x, y_le + 0.3, zc + lift), bevel=0, seg=1)
    for x0, x1 in zip(WING_STATIONS, WING_STATIONS[1:]):
        for i in range(4):
            t = (i + .5) / 4
            x = x0[0] + (x1[0] - x0[0]) * t
            y = x0[1] + (x1[1] - x0[1]) * t
            zc = x0[3] + (x1[3] - x0[3]) * t
            rivet.cyl(.03, .025, loc=(sx * x, y + 0.5, zc + lift), seg=5, bevel=0)


def _build_torn_wing(a, lift):
    """The severed wing, flung clear and lying flat on the ground beside the hull."""
    dx, dy, dz = -14.0, 4.0, 0.35
    skin = a.part('Wing_debris', 'Rust', flat=True)
    rings = []
    for x, y_le, y_te, zc, ht in WING_STATIONS:
        ring = _wing_ring(-x, y_le, y_te, zc, ht)
        rings.append([(px + dx, py + dy, pz * 0.4 + dz) for px, py, pz in ring])
    skin.loft(rings, bevel=.03, seg=2)


FIN_STATIONS = [(2.0, 8.0, 15.2, 0.0, 0.5), (3.7, 9.6, 13.6, 0.0, 0.34), (5.3, 11.6, 12.9, 0.0, 0.12)]


def _fin_ring(z, y_le, y_te, xc, ht):
    y_mid = (y_le + y_te) / 2
    return [(xc, y_le, z), (xc + ht, y_mid, z), (xc, y_te, z), (xc - ht, y_mid, z)]


def _build_tail_fin(a, lift):
    skin = a.part('Fin', 'Steel')
    rings = [_fin_ring(z + lift, y_le, y_te, xc, ht) for z, y_le, y_te, xc, ht in FIN_STATIONS]
    skin.loft(rings, bevel=.02, seg=2)
    a.part('Fin_stripe', 'Team').box((.85, .1, 1.5), loc=(0, 10.5, 3.0 + lift), bevel=0, seg=1)


# ----------------------------------------------------------------------------- engines and thrusters
BELL_PROFILE = [(.42, 0), (.24, .28), (.4, .62), (.58, 1.1), (.64, 1.45)]


def _build_engines(a, loc, torn=False):
    """The main engine cluster: three bells with glowing nozzles, on `Thruster_main`."""
    t = a.pivot('Thruster_main', loc)
    shell = a.part('Engine_shell', 'Charred' if torn else 'Steel', t)
    glow = a.part('Engine_glow', 'TeamGlow', t)
    dark = a.part('Engine_dark', 'Undercarriage', t)
    for x in (-1.05, 0.0, 1.05):
        shell.lathe(BELL_PROFILE, loc=(x, 0, 0), rot=BACKWARD, seg=16)
        glow.torus(.36 if x else .4, .05, loc=(x, 1.42, 0), rot=BACKWARD, seg=16, ring=5)
        dark.cyl(.2, .05, loc=(x, .05, 0), rot=BACKWARD, seg=12, bevel=0)
    a.part('Engine_frame', 'Armor', t).box((2.6, .6, 1.1), loc=(0, -.35, 0), bevel=.08, seg=1)
    if torn:
        chunks = a.part('Engine_debris', 'Rust', t, flat=True)
        rng = random.Random(303)
        for i in range(6):
            chunks.ico((.3, .25, .2), loc=(rng.uniform(-1.3, 1.3), rng.uniform(-.2, 1.3), rng.uniform(-.5, .6)),
                       sub=1, jitter=.4, seed=i * 2.2)


def _build_thruster_pod(a, name, loc):
    p = a.pivot(name, loc)
    a.part('Thruster_pod', 'Armor', p).cyl(.32, .85, loc=(0, 0, 0), rot=FORWARD, seg=10, bevel=.05, bseg=1)
    a.part('Thruster_glow', 'TeamGlow', p).cyl(.2, .05, loc=(0, -.46, 0), rot=FORWARD, seg=10, bevel=0)


# ----------------------------------------------------------------------------- turrets
def _build_main_turret(a, loc):
    t = a.pivot('Turret', loc)
    a.part('Turret_collar', 'Armor', t).cyl(1.05, .16, loc=(0, 0, .05), seg=24, bevel=.03, bseg=2)
    a.part('Turret_ball', 'Steel', t).sphere(.85, loc=(0, 0, -.62), seg=24, rings=14)
    ta = a.part('Turret_armor', 'Armor', t)
    ta.box((.9, .4, .78), loc=(0, -.64, -.66), bevel=.06, seg=2)
    for sx in (-1, 1):
        ta.cyl(.3, .24, loc=(sx * .74, 0, -.62), rot=(0, R90, 0), seg=12, bevel=0)
    a.part('Turret_sight', 'Glass', t).box((.16, .05, .12), loc=(.32, -.84, -.38), bevel=0)
    zc = -.66
    a.part('Main_cannon', 'Steel', t).lathe([(0, .36), (.32, .36), (.32, 2.05), (.44, 2.15), (.44, 2.4),
                                            (.35, 2.43), (.35, 2.4)], loc=(0, 0, zc), rot=FORWARD, seg=20)
    fins = a.part('Main_cannon_fins', 'Armor', t)
    for i in range(6):
        fins.cyl(.5, .04, loc=(0, -(.8 + i * .18), zc), rot=FORWARD, seg=16, bevel=0)
    a.part('Main_cannon_lens', 'Glass', t).sphere((.34, .34, .1), loc=(0, -2.42, zc), rot=FORWARD, seg=16,
                                                  rings=6, cut=0)
    a.part('Main_cannon_glow', 'TeamGlow', t).torus(.38, .032, loc=(0, -2.45, zc), rot=FORWARD, seg=18, ring=5)
    a.part('Main_cannon_core', 'TeamGlow', t).cyl(.1, .03, loc=(0, -2.51, zc), rot=FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_main', (0, -2.55, zc), t)


def _build_coilgun(a, mount, muzzle, tag, loc, deployed=False):
    m = a.pivot(dotted(mount), loc)
    a.part('Coilgun_mount' + tag, 'Armor', m).cyl(.55, .34, loc=(0, 0, -.15), seg=18, bevel=.03, bseg=2)
    a.part('Coilgun_housing' + tag, 'Steel', m).sphere((.5, .5, .34), loc=(0, 0, .05), seg=18, rings=10, cut=0)
    a.part('Coilgun_caps' + tag, 'Armor', m).box((.46, .5, .28), loc=(0, -.46, .08), bevel=.05, seg=2)
    tilt = math.radians(38 if deployed else 8)
    d = Vector((0, math.cos(tilt), math.sin(tilt)))
    guns = a.part('Coilgun_rails' + tag, 'Steel', m)
    coils = a.part('Coilgun_coils' + tag, 'Gilded', m)
    tips = a.part('Coilgun_glow' + tag, 'TeamGlow', m)
    length = 2.1
    mids = []
    for ssx in (-1, 1):
        p0 = Vector((ssx * .16, .28, .12))
        p1 = p0 + d * length
        guns.tube([tuple(p0 + d * length * i / 8) for i in range(9)], .065, seg=6)
        for i in range(4):
            p = p0 + d * length * (.22 + i * .19)
            coils.cyl(.115, .13, loc=tuple(p), rot=(tilt, 0, 0), seg=6, bevel=0)
        tips.cyl(.075, .04, loc=tuple(p1 + d * .01), rot=(tilt, 0, 0), seg=8, bevel=0)
        mids.append(p1)
    a.pivot(dotted(muzzle), tuple((mids[0] + mids[1]) / 2), m)


def _build_flak(a, mount, muzzle, tag, loc, deployed=False):
    m = a.pivot(dotted(mount), loc)
    a.part('Flak_base' + tag, 'Armor', m).cyl(.5, .14, loc=(0, 0, .06), seg=18, bevel=.03, bseg=2)
    fb = a.part('Flak_body' + tag, 'Steel', m)
    fb.cyl(.42, .18, loc=(0, 0, .2), seg=18, bevel=.03, bseg=2)
    fb.box((.68, .62, .34), loc=(0, .04, .42), bevel=.06, seg=2, taper=(.82, .86))
    a.part('Flak_sight' + tag, 'Glass', m).box((.14, .06, .1), loc=(.24, -.3, .5), bevel=0)
    tilt = math.radians(55 if deployed else 15)
    d = Vector((0, -math.cos(tilt), math.sin(tilt)))
    guns = a.part('Flak_guns' + tag, 'Steel', m)
    tips = []
    for x in (-.13, .13):
        p0 = Vector((x, -.02, .42))
        p1 = p0 + d * 1.05
        guns.tube([tuple(p0 + (p1 - p0) * i / 5) for i in range(6)], .032, seg=6)
        tips.append(p1)
    a.pivot(dotted(muzzle), tuple((tips[0] + tips[1]) / 2), m)


def _build_pd_laser(a, name, loc):
    p = a.pivot(name, loc)
    a.part('Pd_base', 'Armor', p).cyl(.26, .12, loc=(0, 0, .04), seg=12, bevel=.02, bseg=1)
    a.part('Pd_dome', 'Steel', p).sphere(.24, loc=(0, 0, .16), seg=12, rings=8, cut=-.2)
    a.part('Pd_emitter', 'Glass', p).cyl(.08, .18, loc=(0, -.22, .16), rot=FORWARD, seg=8, bevel=0)
    a.part('Pd_glow', 'TeamGlow', p).cyl(.05, .02, loc=(0, -.32, .16), rot=FORWARD, seg=8, bevel=0)


def _build_pod_bay(a, loc):
    p = a.pivot('Pod_bay', loc)
    a.part('Bay', 'MetalSheet', p).box((3.4, 3.0, .6), loc=(0, 0, .1), bevel=.08, seg=2)
    a.part('Bay_dark', 'Undercarriage', p).box((2.8, 2.4, .04), loc=(0, 0, -.32), bevel=0, seg=1)
    doors = a.part('Bay_doors', 'Steel', p)
    for sx in (-1, 1):
        doors.box((1.5, 2.6, .06), loc=(sx * 1.55, 0, -.15), rot=(0, 0, sx * .35), bevel=.01, seg=1)
    a.pivot('Muzzle_missile', (0, 0, -.5), p)


def _build_uplink(a, loc):
    p = a.pivot('Uplink', loc)
    a.part('Uplink_strut', 'Steel', p).cyl(.1, .6, loc=(0, 0, -.3), seg=8, bevel=0)
    a.part('Uplink_dish', 'Medical', p).sphere((.55, .55, .24), loc=(0, 0, .05), seg=16, rings=8, cut=.55)
    a.part('Uplink_feed', 'Steel', p).cyl(.04, .3, loc=(0, -.15, .05), rot=FORWARD, seg=6, bevel=0)


def _build_pylons(a, lift):
    """Support struts from the hull surface up to the mounts that sit proud of it."""
    part = a.part('Pylons', 'Armor')
    for name in ('Mount_gun', 'Mount_gun.001', 'Mount_mg', 'Mount_mg.001', 'Pd_laser_l', 'Pd_laser_r'):
        x, y, z = _node(name, lift)
        hw, zb, zt = _at(y, lift)
        sx = 1 if x > 0.3 else (-1 if x < -0.3 else 0)
        hp = (sx * hw * 0.88, y, max(zt * 0.6, zb + 0.3)) if sx else (0.0, y, zt)
        part.limb(hp, (x, y, z - 0.22), 0.42, 0.34, bevel=.03, seg=1, taper=(1, .6))


# ----------------------------------------------------------------------------- craters and debris
def _crater_ring(a):
    crater = a.part('Crater', 'Charred', flat=True)
    crater.lathe([(9.0, 0.05), (14.0, 0.1), (19.0, 0.22), (21.5, -0.05), (20.5, -0.35), (16.0, -0.15),
                 (10.0, 0.0)], seg=48)


def _debris_pile(a, x, y, w, d, h, seed):
    rng = random.Random(seed)
    chunk = a.part('Debris_chunk', 'Armor', flat=True)
    tile = a.part('Debris_tile', 'Undercarriage')
    frag = a.part('Debris_frag', 'Steel')
    for i in range(5):
        cx = x + rng.uniform(-w / 2 * .6, w / 2 * .6)
        cy = y + rng.uniform(-d / 2 * .6, d / 2 * .6)
        cz = rng.uniform(.15, h * .5)
        s = rng.uniform(.5, .95)
        chunk.ico((s * .9, s * .7, s * .55), loc=(cx, cy, cz), sub=1, jitter=.35, seed=seed + i * 1.7)
    for i in range(3):
        cx = x + rng.uniform(-w / 2 * .5, w / 2 * .5)
        cy = y + rng.uniform(-d / 2 * .5, d / 2 * .5)
        tile.box((.7, .7, .05), loc=(cx, cy, rng.uniform(.1, h * .4)),
                rot=(rng.uniform(-.3, .3), rng.uniform(-.3, .3), rng.uniform(0, TAU)), bevel=0, seg=1)
    frag.limb((x - w * .3, y - d * .2, .1), (x + w * .35, y + d * .25, h * .7), .2, .08, bevel=.03, seg=1)


# ----------------------------------------------------------------------------- the ships
def _ship(a, lift, wreck):
    _suffixed(a)
    rng = random.Random(1956)
    _build_hull(a, lift, wreck, rng)
    _build_wing(a, 1, lift, torn=False)
    _build_wing(a, -1, lift, torn=wreck)
    if wreck:
        _build_torn_wing(a, lift)
    _build_tail_fin(a, lift)
    _build_engines(a, _node('Thruster_main', lift), torn=wreck)
    for name in ('Thruster_fl', 'Thruster_fr', 'Thruster_rl', 'Thruster_rr'):
        _build_thruster_pod(a, name, _node(name, lift))
    _build_main_turret(a, _node('Turret', lift))
    _build_coilgun(a, 'Mount_gun', 'Muzzle_gun', '', _node('Mount_gun', lift), deployed=wreck)
    _build_coilgun(a, 'Mount_gun.001', 'Muzzle_gun.001', '_001', _node('Mount_gun.001', lift), deployed=wreck)
    _build_flak(a, 'Mount_mg', 'Muzzle_mg', '', _node('Mount_mg', lift), deployed=wreck)
    _build_flak(a, 'Mount_mg.001', 'Muzzle_mg.001', '_001', _node('Mount_mg.001', lift), deployed=wreck)
    _build_pd_laser(a, 'Pd_laser_l', _node('Pd_laser_l', lift))
    _build_pd_laser(a, 'Pd_laser_r', _node('Pd_laser_r', lift))
    _build_pod_bay(a, _node('Pod_bay', lift))
    _build_uplink(a, _node('Uplink', lift))
    _build_pylons(a, lift)
    if wreck:
        _crater_ring(a)
        for i, (right, forward, w, d) in enumerate(DEBRIS):
            x, y, _z = _pos(right, forward)
            _debris_pile(a, x, y, w, d, 1.8, seed=200 + i)


def silver_bug(a):
    """Militarised orbital gunship: see the module docstring."""
    _ship(a, 0.0, False)


def silver_bug_wreck(a):
    """The same ship, crashed for phase 3's ground fortress: see the module docstring."""
    _ship(a, LIFT, True)


# ----------------------------------------------------------------------------- satellite and drop pod
def bug_satellite(a):
    """A small military recon satellite, about 5 m across: a bus, two solar wings, a dish and a rod
    magazine. Origin at its centre; it flies."""
    a.part('Bus', 'Armor').box((.9, 1.1, 1.5), bevel=.05, seg=2)
    a.part('Bus_band', 'Team').box((.94, .2, 1.54), loc=(0, 0, .1), bevel=.02, seg=2)
    a.part('Panels', 'Steel').box((.7, .9, .06), loc=(0, 0, .78), bevel=.02, seg=1)
    rivet = a.part('Rivets', 'MetalSheet')
    for sx in (-1, 1):
        for sz in (-.55, -.15, .3, .65):
            rivet.cyl(.025, .02, loc=(sx * .47, .3, sz), rot=(0, R90, 0), seg=5, bevel=0)
            rivet.cyl(.025, .02, loc=(sx * .47, -.3, sz), rot=(0, R90, 0), seg=5, bevel=0)
    thr = a.part('Rcs', 'Armor')
    glow = a.part('Rcs_glow', 'TeamGlow')
    for sx in (-1, 1):
        for sy in (-1, 1):
            thr.cyl(.08, .18, loc=(sx * .46, sy * .56, -.7), rot=(0, R90, 0), seg=8, bevel=.01, bseg=1)
            glow.cyl(.05, .02, loc=(sx * .56, sy * .56, -.7), rot=(0, R90, 0), seg=8, bevel=0)
    wing = a.part('Solar_wing', 'Glass')
    frame = a.part('Solar_frame', 'Steel')
    cell = a.part('Solar_cell', 'Steel')
    for sx in (-1, 1):
        wing.box((1.9, .85, .03), loc=(sx * 1.55, 0, 0), bevel=0, seg=1)
        frame.box((1.95, .06, .05), loc=(sx * 1.55, .42, .03), bevel=0, seg=1)
        frame.box((1.95, .06, .05), loc=(sx * 1.55, -.42, .03), bevel=0, seg=1)
        frame.box((.1, .9, .1), loc=(sx * .58, 0, 0), bevel=.02, seg=1)
        for i in range(7):
            cell.box((.02, .74, .01), loc=(sx * (.65 + i * .25), 0, .022), bevel=0, seg=1)
    a.part('Sensor_boom', 'Steel').cyl(.03, .9, loc=(0, .3, 1.2), rot=FORWARD, seg=6, bevel=0)
    a.part('Sensor_head', 'Glass').box((.14, .14, .14), loc=(0, -.15, 1.2), bevel=.02, seg=1)
    a.part('Dish_arm', 'Steel').cyl(.05, .5, loc=(0, -.65, .5), rot=FORWARD, seg=8, bevel=0)
    a.part('Dish', 'Medical').sphere((.4, .4, .18), loc=(0, -.95, .68), rot=FORWARD, seg=18, rings=10, cut=.5)
    a.part('Dish_feed', 'Steel').cyl(.03, .16, loc=(0, -.87, .68), rot=FORWARD, seg=8, bevel=0)
    mag = a.part('Rod_magazine', 'Gilded')
    mag.cyl(.22, 1.6, loc=(0, .3, -.95), rot=(0, R90, 0), seg=10, bevel=.03, bseg=1)
    tips = a.part('Rod_tips', 'Steel')
    for i in range(6):
        tips.cyl(.05, .12, loc=(-.75 + i * .3, .3, -.95), rot=(0, R90, 0), seg=6, bevel=0)
    a.part('Antenna', 'Steel').cyl(.02, .9, loc=(.2, .3, .95), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(.2, .3, 1.42), seg=6, rings=4)


def drop_pod(a):
    """A drop pod carrying one or two vehicles down: a 6 m capsule/cone with a scorched heat shield
    at the bottom, a retro-rocket ring, fins and a Team stripe. Origin at its centre; it flies."""
    hull = a.part('Hull', 'Armor')
    hull.lathe([(1.55, -3.0), (1.6, -2.8), (1.45, -1.5), (1.25, 0.2), (0.95, 1.6), (0.5, 2.5), (0.0, 3.0)],
              seg=26, bevel=.02)
    a.part('Heat_shield', 'Charred', flat=True).lathe([(0, -3.1), (1.5, -2.98), (1.58, -2.82), (1.4, -2.68),
                                                       (0, -2.8)], seg=26)
    a.part('Stripe', 'Team').lathe([(1.42, -.2), (1.57, -.2), (1.57, .35), (1.42, .35)], seg=26)
    rivet = a.part('Rivets', 'MetalSheet')
    for z in (-1.7, -0.4, 1.0):
        for k in range(12):
            q = k * TAU / 12
            r = 1.3 + 0.25 * (1 - abs(z) / 3.0)
            rivet.cyl(.03, .02, loc=(r * math.cos(q), r * math.sin(q), z), rot=(0, 0, 0), seg=5, bevel=0)
    hatch = a.part('Access_hatch', 'Steel')
    hatch.cyl(.32, .04, loc=(1.3 * math.cos(.3), 1.3 * math.sin(.3), .5), rot=(0, R90, 0), seg=14, bevel=.01, bseg=1)
    ring = a.part('Retro_ring', 'Steel')
    nozzle = a.part('Retro_glow', 'TeamGlow')
    for k in range(9):
        q = k * TAU / 9
        x, y = 1.5 * math.cos(q), 1.5 * math.sin(q)
        ring.cyl(.13, .5, loc=(x, y, -2.55), seg=9, bevel=.02, bseg=1)
        nozzle.cyl(.09, .05, loc=(x, y, -2.82), seg=9, bevel=0)
    struts = a.part('Fin_struts', 'Steel')
    fins = a.part('Fins', 'Armor')
    for k in range(4):
        q = k * TAU / 4 + TAU / 8
        x, y = math.cos(q), math.sin(q)
        struts.limb((x * 1.45, y * 1.45, -1.9), (x * 1.55, y * 1.55, -.3), .1, .06, bevel=.01, seg=1)
        fins.box((.06, 1.0, 2.0), loc=(x * 1.55, y * 1.55, -1.2), rot=(0, 0, q), bevel=.02, seg=1, taper=(.35, 1))
    a.part('Hatch', 'Steel').cyl(1.05, .08, loc=(0, 0, 2.98), seg=16, bevel=.02, bseg=1)
    a.part('Hatch_seam', 'Undercarriage').torus(1.05, .02, loc=(0, 0, 2.98), seg=16, ring=4)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 0, 3.15), seg=6, rings=4)


BUILDERS = {
    'silver_bug': (silver_bug, dict(ao_distance=.4, ground=False)),
    'silver_bug_wreck': (silver_bug_wreck, dict(ao_distance=1.1, grime_height=1.2)),
    'bug_satellite': (bug_satellite, dict(ao_distance=.15, ground=False)),
    'drop_pod': (drop_pod, dict(ao_distance=.3, ground=False)),
}
