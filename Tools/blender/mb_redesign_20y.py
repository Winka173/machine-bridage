"""Machine Brigade boss redesigns (DECISIONS 20Y), each drawn from outside references (listed there):

  * ixion: Ly Han's giant wheel, rebuilt as a war machine: the Lebedenko "Tsar Tank" layout (two 10 m spoked wheels
    on one axle, a war cabin slung between them, a trailing steering roller), dressed like a game war machine: an
    Ork "deff rolla" of spikes across the front (Warhammer 40,000), scythe spikes on the hubs and studded treads, slab
    armour, rivets, exhaust stacks and rust (Gears of War's Locust machines, Metal Gear's Shagohod). 21 x 12.7 m
    (17.5 m across the hub spikes). Nodes as before: `Part_wheel_l` / `Part_wheel_r` (each wheel whole),
    `Part_steer` (the steering roller), `Turret` with `Muzzle_main` (its 76 mm).
  * silver_bug / silver_bug_wreck: Aurel's Icarus, rebuilt as a warship spacecraft: a wedge hull after the Imperial
    Star Destroyer (a dagger plan, the side trench with its lit windows, a stepped superstructure and a command tower
    with its two shield domes) and the Republic Venator (the dorsal flight-deck doors, the red stripes, here in the
    side's colour), an engine bank across the stern and a ventral hangar. 33.5 x 22 m. Every node keeps its name and
    place (mb_orbital.NODES): `Turret` (the ventral laser ball, `Muzzle_main`), `Mount_gun` / `.001` (coilguns),
    `Mount_mg` / `.001` (flak), `Pd_laser_l` / `_r`, `Thruster_main` (the engine bank), `Thruster_fl` / `_fr` /
    `_rl` / `_rr`, `Pod_bay` (`Muzzle_missile`), `Uplink`, and the crash turrets `Mount_gun.002` / `.003` (40 mm,
    woken on the ground). The wreck is the same ship crashed, raised by mb_orbital.LIFT, its tower broken off.

Conventions are mb_vehicles'/mb_orbital's: metres, +Z up, Blender -Y is the front, +X the vehicle's left.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mb_orbital as orb  # noqa: E402
from mb_phase2 import _suffixed, dotted  # noqa: E402
from mb_p20_bosses import gun_turret, hanging_gun, rocket_box  # noqa: E402
from mb_phase8 import autocannon, ciws, pv  # noqa: E402
from mb_vehicles import FORWARD, R90  # noqa: E402

AXIS_X = (0, R90, 0)   # a cylinder's axis along X (wheels, rollers)


def _radial(part, n, radius, x, length, r, phase=0.0, r2=0.02, seg=6, centre=(0.0, 0.0)):
    """n spikes pointing out from an axis along X through (y, z) `centre` at `radius`, at x (a wheel, a roller)."""
    for k in range(n):
        ang = phase + k * math.tau / n
        c = radius + length / 2
        part.cyl(r, length, r2=r2, loc=(x, centre[0] + c * math.sin(ang), centre[1] + c * math.cos(ang)), rot=(-ang, 0, 0), seg=seg, bevel=0)


# ============================================================================== Ixion

IX_R, IX_X, IX_Y, IX_W = 5.0, 5.6, -1.5, 1.5     # wheel radius, centre x and y, tread width


def _ix_wheel(a, s, name):
    """A 10 m wheel: a studded iron tread with two rows of spikes, rusted rims, eight I-beam spokes, an armoured
    disc and a hub with a scythe spike out of its outer face."""
    p = pv(a, name, (s * IX_X, IX_Y, IX_R))
    tag = name[5:]
    ring = [(IX_R * math.cos(k * math.tau / 44), IX_R * math.sin(k * math.tau / 44)) for k in range(44)]
    a.part(f'Tread_{tag}', 'Undercarriage', p).shell(ring, IX_W, .6, loc=(-IX_W / 2, 0, 0), rot=AXIS_X, bevel=.06)
    rust = a.part(f'Rims_{tag}', 'Rust', p)
    for x in (-IX_W / 2 + .02, IX_W / 2 - .02):
        rust.torus(IX_R - .2, .24, loc=(x, 0, 0), rot=AXIS_X, seg=44, ring=6)
    cleat = a.part(f'Cleats_{tag}', 'Armor', p)
    for k in range(22):
        ang = k * math.tau / 22
        cleat.box((IX_W + .24, .5, .42), loc=(0, (IX_R + .08) * math.sin(ang), (IX_R + .08) * math.cos(ang)), rot=(-ang, 0, 0),
                  bevel=.05, seg=1)
    spikes = a.part(f'Tread_spikes_{tag}', 'Steel', p)
    for x in (-.42, .42):
        _radial(spikes, 22, IX_R + .2, x, .8, .17, phase=math.pi / 22)
    spokes = a.part(f'Spokes_{tag}', 'Armor', p)
    for k in range(8):
        ang = k * math.tau / 8
        for x in (-.4, .4):
            spokes.limb((x, 0, 0), (x, (IX_R - .35) * math.sin(ang), (IX_R - .35) * math.cos(ang)), .3, .62, bevel=.04, seg=1)
    out = s * (IX_W / 2 + .12)
    a.part(f'Disc_{tag}', 'Team', p).cyl(2.9, .22, loc=(out, 0, 0), rot=AXIS_X, seg=24, bevel=.05, bseg=1)
    a.part(f'Disc_ring_{tag}', 'Armor', p).torus(2.95, .16, loc=(out, 0, 0), rot=AXIS_X, seg=24, ring=6)
    a.part(f'Disc_rivets_{tag}', 'Steel', p).bolts(
        [(out + s * .12, 2.5 * math.sin(k * math.tau / 16), 2.5 * math.cos(k * math.tau / 16)) for k in range(16)], r=.07, h=.06, rot=AXIS_X)
    grime = a.part(f'Disc_rust_{tag}', 'Rust', p)
    for k in range(3):
        ang = 0.7 + k * 2.1
        grime.box((.05, .5, 1.6), loc=(out + s * .12, 1.6 * math.sin(ang), 1.6 * math.cos(ang) - .4), rot=(-ang * .2, 0, 0), bevel=0, seg=1)
    a.part(f'Hub_{tag}', 'Armor', p).cyl(1.05, 2.2, loc=(s * .4, 0, 0), rot=AXIS_X, seg=16, bevel=.08, bseg=1)
    hub_spikes = a.part(f'Hub_spikes_{tag}', 'Steel', p)
    # The scythe: a long spike out of the hub, and six short ones round it.
    hub_spikes.cyl(.5 if s > 0 else .02, 2.4, r2=.02 if s > 0 else .5, loc=(s * (1.5 + 1.2), 0, 0), rot=AXIS_X, seg=10, bevel=0)
    for k in range(6):
        ang = k * math.tau / 6
        hub_spikes.cyl(.16 if s > 0 else .02, .8, r2=.02 if s > 0 else .16, loc=(s * (1.5 + .4), 1.6 * math.sin(ang), 1.6 * math.cos(ang)),
                       rot=AXIS_X, seg=6, bevel=0)


def _ix_steer(a):
    """The trailing steering roller: a spiked drum in a fork."""
    p = pv(a, 'Part_steer', (0, 10.4, 1.3))
    a.part('Steer_drum', 'Undercarriage', p).cyl(1.3, 2.2, loc=(0, 0, 0), rot=AXIS_X, seg=22, bevel=.08, bseg=1)
    rims = a.part('Steer_rims', 'Rust', p)
    for x in (-1.0, 1.0):
        rims.torus(1.22, .14, loc=(x, 0, 0), rot=AXIS_X, seg=22, ring=6)
    spikes = a.part('Steer_spikes', 'Steel', p)
    for x in (-.55, .15, .8):
        _radial(spikes, 10, 1.3, x, .55, .12, phase=x)
    fork = a.part('Steer_fork', 'Armor', p)
    for x in (-1.35, 1.35):
        fork.limb((x, 0, 0), (x * .8, -1.2, 2.2), .28, .5, bevel=.04, seg=1)
    fork.box((2.9, .8, .5), loc=(0, -1.25, 2.3), bevel=.08, seg=1)
    a.part('Steer_axle', 'Steel', p).cyl(.22, 3.0, loc=(0, 0, 0), rot=AXIS_X, seg=10, bevel=0)


def ixion(a):
    """Ixion, a Tsar Tank war machine: see the module docstring."""
    _suffixed(a)
    for s, name in ((1, 'Part_wheel_l'), (-1, 'Part_wheel_r')):
        _ix_wheel(a, s, name)
    a.part('Axle', 'Undercarriage').cyl(.7, 2 * IX_X - IX_W, loc=(0, IX_Y, IX_R), rot=AXIS_X, seg=16, bevel=.04, bseg=1)
    a.part('Axle_collars', 'Rust').cyl(.9, 2 * IX_X - IX_W - 7.6, loc=(0, IX_Y, IX_R), rot=AXIS_X, seg=16, bevel=.04, bseg=1)

    # The war cabin slung on the axle: slab armour, a sloped glacis, a belly, rivet rows and rust streaks.
    team = a.part('Hull', 'Team')
    team.box((7.8, 9.6, 3.8), loc=(0, -.4, 5.6), bevel=.25, seg=1, taper=(.84, .82))                      # z 3.7 .. 7.5
    a.part('Belly', 'Undercarriage').box((6.4, 8.8, 1.8), loc=(0, -.4, 3.2), bevel=.2, seg=1)
    arm = a.part('Armour_slabs', 'Armor')
    arm.box((7.4, .6, 4.0), loc=(0, -5.02, 5.5), rot=(-.24, 0, 0), bevel=.12, seg=1)                     # glacis
    for s in (-1, 1):
        arm.box((.35, 7.6, 2.6), loc=(s * 3.72, -.6, 5.1), rot=(0, s * .12, 0), bevel=.08, seg=1)           # side slabs
        arm.box((.3, 2.6, 1.0), loc=(s * 3.2, 3.6, 7.3), bevel=.06, seg=1)                                 # rear bins
    for s in (-1, 1):
        arm.box((1.4, 6.8, .4), loc=(s * 2.7, -.9, 7.55), rot=(0, s * -.42, 0), bevel=.06, seg=1)             # raked roof plates
    a.part('Engine_grille', 'Undercarriage').box((2.6, 1.8, .2), loc=(0, 4.3, 7.55), bevel=.03, seg=1)
    rivets = a.part('Rivets', 'Steel')
    for s in (-1, 1):
        for row, z in enumerate((4.2, 5.9)):
            rivets.bolts([(s * (3.92 - (z - 4.2) * .12), -4.0 + k * .8 + row * .4, z) for k in range(10)], r=.07, h=.08, rot=AXIS_X)
    rivets.bolts([(-3.0 + k * .6, -5.36, 4.0) for k in range(11)], r=.07, h=.08, rot=FORWARD)
    rust = a.part('Rust_streaks', 'Rust')
    for s in (-1, 1):
        for y in (-3.2, -1.1, 1.4, 2.9):
            rust.box((.04, .28, 1.4 + (y % 1.0)), loc=(s * 3.93, y, 4.6), rot=(0, s * .12, 0), bevel=0, seg=1)
    for x in (-2.4, -.3, 1.9):
        rust.box((.4, .04, 1.6), loc=(x, -5.4, 4.6), rot=(-.24, 0, 0), bevel=0, seg=1)
    # Spikes along the roof's edges and down the glacis.
    spikes = a.part('Hull_spikes', 'Steel')
    for s in (-1, 1):
        for k in range(6):
            spikes.cyl(.16, 1.0, r2=.02, loc=(s * 3.45, -3.2 + k * 1.3, 7.85), rot=(0, s * -.5, 0), seg=6, bevel=0)
    for x in (-2.6, -.9, .9, 2.6):
        spikes.cyl(.2, 1.1, r2=.02, loc=(x, -5.9, 6.3), rot=(R90 - .3, 0, 0), seg=6, bevel=0)

    # The deff rolla across the front: a spiked drum on two arms, and a plough-ram under it.
    a.part('Roller_drum', 'Armor').cyl(1.15, 6.4, loc=(0, -7.5, 1.2), rot=AXIS_X, seg=20, bevel=.06, bseg=1)
    bands = a.part('Roller_bands', 'Rust')
    for x in (-3.0, -1.95, -.65, .65, 1.95, 3.0):
        bands.cyl(1.2, .22, loc=(x, -7.5, 1.2), rot=AXIS_X, seg=20, bevel=.02, bseg=1)
    rs = a.part('Roller_spikes', 'Steel')
    for x in (-2.6, -1.3, 0.0, 1.3, 2.6):
        _radial(rs, 10, 1.15, x, .8, .17, phase=x * .7, centre=(-7.5, 1.2))
    ra = a.part('Roller_arms', 'Armor')
    for s in (-1, 1):
        ra.limb((s * 3.35, -7.5, 1.2), (s * 3.0, -4.2, 3.8), .5, .7, bevel=.05, seg=1)
        ra.cyl(.45, .5, loc=(s * 3.45, -7.5, 1.2), rot=AXIS_X, seg=12, bevel=.03, bseg=1)
    # Chains slung across the glacis.
    chain = a.part('Chains', 'Charred')
    for c in range(2):
        for k in range(18):
            t = (k + .5) / 18
            x = -3.0 + 6.0 * t
            z = 6.6 - c * 1.1 - 0.9 * math.sin(t * math.pi)
            chain.box((.3, .14 if k % 2 else .06, .1 if k % 2 else .2), loc=(x, -5.5 - (z - 3.7) * .245 - .1, z), rot=(-.24, 0, 0), bevel=0, seg=1)

    # The command cupola behind the gun, its red vision slits; exhaust stacks with glowing mouths; the tail boom.
    team.box((2.8, 2.4, 1.6), loc=(0, 2.7, 8.2), bevel=.2, seg=1, taper=(.85, .85))
    glow = a.part('Vision_slits', 'EliteGlow')
    glow.box((1.8, .05, .14), loc=(0, 1.49, 8.4), bevel=0)
    for s in (-1, 1):
        glow.box((.05, 1.0, .12), loc=(s * 1.41, 2.6, 8.4), bevel=0)
    stack = a.part('Exhausts', 'Rust')
    soot = a.part('Soot', 'Charred')
    ember = a.part('Exhaust_glow', 'LavaGlow')
    for s in (-1, 1):
        stack.cyl(.36, 4.6, loc=(s * 2.7, 4.1, 8.0), seg=12, bevel=.03, bseg=1)
        stack.cyl(.46, .4, loc=(s * 2.7, 4.1, 8.7), seg=12, bevel=.03, bseg=1)
        soot.cyl(.4, .7, loc=(s * 2.7, 4.1, 10.2), seg=12, bevel=0)
        ember.cyl(.26, .03, loc=(s * 2.7, 4.1, 10.56), seg=12, bevel=0)
        soot.box((.04, 1.2, 1.4), loc=(s * 3.9, 3.8, 6.6), rot=(0, s * .12, 0), bevel=0, seg=1)
    boom = a.part('Tail_boom', 'Armor')
    for s in (-1, 1):
        boom.limb((s * 1.6, 4.2, 4.4), (s * 1.1, 9.2, 3.4), .5, .8, bevel=.05, seg=1)
    boom.box((3.4, 2.4, 1.6), loc=(0, 6.2, 4.6), bevel=.12, seg=1)
    a.part('Counterweight', 'Team').box((2.6, 1.6, 1.3), loc=(0, 6.2, 6.0), bevel=.12, seg=1)
    a.part('Ammo_crates', 'Crate').box((1.0, .8, .6), loc=(.9, 6.0, 6.95), bevel=.04, seg=1)
    _ix_steer(a)
    gun_turret(a, 'Turret', 'Muzzle_main', (0, -1.2, 7.5), w=3.0, d=3.4, h=1.4, barrel=6.0, r=.15)


# ============================================================================== Icarus (silver_bug)

# The wedge in plan, stern (+y) to nose (-y): (y, half-width, top z, belly z).
SD = [(16.0, 11.0, 2.05, -2.40), (11.0, 9.65, 2.0, -2.55), (4.0, 7.8, 1.9, -2.75), (-2.0, 6.2, 1.75, -2.75),
      (-8.0, 4.6, 1.45, -2.70), (-12.0, 2.9, 1.0, -2.20), (-15.5, 1.3, .6, -1.30), (-17.5, .3, .35, -.50)]


def _sd_at(y, prof=SD):
    """(half-width, top z, belly z) of a wedge profile at y."""
    s = prof
    if y >= s[0][0]:
        return s[0][1:]
    for a, b in zip(s, s[1:]):
        if y >= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return tuple(a[k] + (b[k] - a[k]) * t for k in range(1, 4))
    return s[-1][1:]


def _sd_surface(x, y, prof=SD):
    """The upper hull's height at (x, y): the flat top out to half the half-width, then the slope to the edge."""
    hw, zt, _ = _sd_at(y, prof)
    ax = abs(x)
    if ax <= hw * .5:
        return zt
    if ax <= hw * .78:
        return zt + (zt * .55 - zt) * (ax - hw * .5) / (hw * .28)
    return max(0.0, zt * .55 * (hw - ax) / (hw * .22))


def _sd_hull(a, lift, wreck, rng, prof=SD, doors=True, hangar=True):
    """A wedge hull on a profile: the side trench with its lit windows, the side's stripes, greebles on top;
    Icarus's Venator doors and ventral hangar with `doors` / `hangar`."""
    SD_ = prof
    rings = []
    for y, hw, zt, zb in reversed(SD_):
        if wreck and -4.0 <= y <= 4.0:
            zt -= .35
        rings.append([(hw, y, lift), (hw * .78, y, zt * .55 + lift), (hw * .5, y, zt + lift), (-hw * .5, y, zt + lift),
                      (-hw * .78, y, zt * .55 + lift), (-hw, y, lift), (-hw * .62, y, zb + lift), (hw * .62, y, zb + lift)])
    a.part('Hull', 'Armor' if wreck else 'MetalSheet').loft(rings, bevel=.02, seg=1)
    # The side trench along each edge, its rows of lit windows; the Venator's stripes and dorsal doors.
    trench = a.part('Trench', 'Undercarriage')
    windows = a.part('Windows', 'Lamp')
    for sx in (-1, 1):
        for (y0, hw0, _, _), (y1, hw1, _, _) in zip(SD_, SD_[1:]):
            trench.limb((sx * (hw0 + .02), y0, lift), (sx * (hw1 + .02), y1, lift), .34, .26, bevel=0, seg=1)
            n = max(1, int(abs(y1 - y0) / 1.1))
            for k in range(n):
                t = (k + .5) / n
                if wreck and rng.random() < .5:
                    continue
                windows.box((.06, .42, .09), loc=(sx * (hw0 + (hw1 - hw0) * t + .19), y0 + (y1 - y0) * t, lift + .06), rot=(0, 0, 0),
                            bevel=0, seg=1)
    stripe = a.part('Stripes', 'Team')
    for sx in (-1, 1):
        y0, y1 = SD_[-1][0] + 1.1, SD_[-1][0] + .45 * (SD_[0][0] - SD_[-1][0])
        stripe.limb((sx * .9, y0, _sd_surface(0, y0, SD_) + lift + .04), (sx * 2.6, y1, _sd_surface(0, y1, SD_) + lift + .04), .5, .03,
                    bevel=0, seg=1)
    if doors:
        _sd_doors(a, lift)
    _sd_greebles(a, lift, rng, SD_, 140 if doors else 90)
    if hangar:
        a.part('Hangar_mouth', 'Charred').box((5.0, 5.6, .06), loc=(0, 4.0, -2.78 + lift), bevel=0)
        a.part('Hangar_lights', 'Lamp').box((5.2, .12, .05), loc=(0, 1.1, -2.8 + lift), bevel=0)
    belly = a.part('Belly_plates', 'Undercarriage')
    for y in range(int(SD_[-1][0]) + 6, int(SD_[0][0]) - 1, 3):
        hw, _, zb = _sd_at(y, SD_)
        belly.box((hw * 1.1, .12, .04), loc=(0, y, zb + lift - .02), bevel=0)
    if wreck:
        scorch = a.part('Scorch', 'Charred', flat=True)
        for i in range(12):
            y = rng.uniform(-12, 12)
            hw, zt, zb = _sd_at(y, SD_)
            scorch.ico((hw * .3, 1.2, .3), loc=(rng.uniform(-hw * .5, hw * .5), y, zt + lift + .05), sub=1, jitter=.3, seed=i * 2.7)
        crack = a.part('Hull_crack', 'Charred')
        for k in range(9):
            x = -6.0 + k * 1.5
            crack.box((1.4, .5, .6), loc=(x, (k % 2) * .6 - .3, _sd_surface(x, 0, SD_) + lift), rot=(0, 0, .3 * (1 - 2 * (k % 2))), bevel=0)


def _sd_doors(a, lift):
    """The Venator's dorsal flight-deck doors: a raised strip down the forward centreline."""
    doors = a.part('Deck_doors', 'Armor')
    ridge_top = 2.35
    doors.box((1.9, 12.5, ridge_top - 1.2), loc=(0, -8.0, (ridge_top + 1.2) / 2 + lift), bevel=.12, seg=1, taper=(.8, .96))
    a.part('Door_seam', 'Undercarriage').box((.05, 12.0, .04), loc=(0, -8.0, ridge_top + lift + .01), bevel=0)


def _sd_greebles(a, lift, rng, prof, n):
    """Plating and machinery on the upper hull (clear of the centreline forward)."""
    greeble = a.part('Greebles', 'Armor')
    light = a.part('Greebles_light', 'Steel')
    y_lo, y_hi = prof[-1][0] + 4.5, prof[0][0] - 1.5
    for i in range(n):
        y = rng.uniform(y_lo, y_hi)
        hw, _, _ = _sd_at(y, prof)
        x = rng.uniform(-hw * .82, hw * .82)
        if abs(x) < 1.3 and y < -1.0:
            continue
        w, d, h = rng.uniform(.3, 1.3), rng.uniform(.3, 1.6), rng.uniform(.08, .35)
        (greeble if i % 3 else light).box((w, d, h), loc=(x, y, _sd_surface(x, y, prof) + lift + h / 2 - .02), bevel=0, seg=1)


def _sd_superstructure(a, lift, wreck):
    """The stepped superstructure over the stern, the command tower with its bridge and two shield domes."""
    tiers = a.part('Superstructure', 'Armor' if wreck else 'MetalSheet')
    bands = a.part('Tier_bands', 'Undercarriage')
    lights = a.part('Tier_windows', 'Lamp')
    z = _sd_surface(0, 8.0)
    for w, y0, y1, h in ((9.4, 0.0, 15.4, 1.35), (6.8, 3.8, 14.4, 1.1), (4.4, 7.0, 13.4, 1.0)):
        tiers.box((w, y1 - y0, h), loc=(0, (y0 + y1) / 2, z + h / 2 + lift - .05), bevel=.08, seg=1, taper=(.9, .96))
        bands.box((w * .9 + .02, .05, .18), loc=(0, y0 - .02 + .02, z + h * .5 + lift), bevel=0)
        lights.box((w * .7, .05, .08), loc=(0, y0 - .04 + h * .02, z + h * .75 + lift), bevel=0)
        z += h - .05
    if wreck:
        # The tower broke off in the crash: its stump on the deck, the bridge lying beside the hull.
        a.part('Tower_stump', 'Charred', flat=True).box((2.0, 2.0, .9), loc=(0, 11.4, z + .4 + lift), rot=(.1, .12, .3), bevel=.05)
        fallen = a.part('Tower_fallen', 'Rust', flat=True)
        fallen.box((7.0, 1.8, 1.1), loc=(12.5, 14.0, .6), rot=(0, .25, .5), bevel=.06, seg=1)
        fallen.sphere(.8, loc=(15.4, 15.8, .7), seg=10, rings=5)
        return
    neck = a.part('Tower', 'MetalSheet')
    neck.box((2.4, 2.6, 2.8), loc=(0, 11.4, z + 1.35 + lift), bevel=.08, seg=1, taper=(.75, .8))
    zb = z + 2.7
    neck.box((8.8, 2.4, 1.3), loc=(0, 11.4, zb + .65 + lift), bevel=.12, seg=1, taper=(.96, .78))
    a.part('Bridge_windows', 'Lamp').box((7.8, .05, .2), loc=(0, 10.18, zb + .7 + lift), bevel=0)
    domes = a.part('Shield_domes', 'Medical')
    posts = a.part('Dome_posts', 'Steel')
    for sx in (-1, 1):
        posts.cyl(.2, .7, loc=(sx * 3.3, 11.4, zb + 1.55 + lift), seg=8, bevel=0)
        domes.sphere(1.0, loc=(sx * 3.3, 11.4, zb + 2.7 + lift), seg=16, rings=8)
    posts.cyl(.05, 2.2, loc=(0, 11.6, zb + 2.4 + lift), seg=6, bevel=0)
    posts.cyl(.05, 1.5, loc=(.7, 11.6, zb + 2.05 + lift), seg=6, bevel=0)


def _sd_engines(a, lift, wreck):
    """The engine bank across the stern (`Thruster_main`): a housing, three big nozzles and four smaller ones."""
    right, forward, up = orb.NODES['Thruster_main']
    t = a.pivot('Thruster_main', orb._pos(right, forward, up + lift))
    a.part('Engine_housing', 'Charred' if wreck else 'Armor', t).box((15.0, 1.6, 3.4), loc=(0, 1.1, -.6), bevel=.15, seg=1,
                                                                      taper=(.92, .9))
    nozzle = a.part('Engine_nozzles', 'Charred' if wreck else 'Steel', t)
    inner = a.part('Engine_inner', 'Undercarriage', t)
    glow = a.part('Engine_glow', 'Charred' if wreck else 'TeamGlow', t)
    for x, r in ((0.0, 1.25), (3.2, 1.05), (-3.2, 1.05), (5.8, .7), (-5.8, .7), (7.2, .5), (-7.2, .5)):
        z = -.4 if abs(x) < 4 else -1.1
        nozzle.cyl(r, 1.0, loc=(x, 2.3, z), rot=FORWARD, seg=18, bevel=.05, bseg=1)
        inner.cyl(r * .82, .04, loc=(x, 2.81, z), rot=FORWARD, seg=16, bevel=0)
        glow.cyl(r * .62, .04, loc=(x, 2.84, z), rot=FORWARD, seg=16, bevel=0)


def _sd_thruster(a, name, lift, raise_=0.0, strut=None):
    """A manoeuvring thruster pod on its node, drawn `raise_` above it (out of the hull), on a strut to the hull."""
    right, forward, up = orb.NODES[name]
    p = a.pivot(name, orb._pos(right, forward, up + lift))
    a.part('Thruster_pod', 'Armor', p).cyl(.5, 1.6, loc=(0, 0, raise_), rot=FORWARD, seg=12, bevel=.06, bseg=1)
    a.part('Thruster_glow', 'TeamGlow', p).cyl(.34, .04, loc=(0, .82, raise_), rot=FORWARD, seg=12, bevel=0)
    if strut:
        a.part('Thruster_struts', 'Armor', p).limb(strut, (0, 0, raise_), .3, .5, bevel=.03, seg=1)


def _sd_pylons(a, lift, wreck):
    """Pylons from the hull up to the mounts that sit proud of it."""
    part = a.part('Pylons', 'Armor')
    for name in ('Mount_gun', 'Mount_gun.001', 'Mount_mg', 'Mount_mg.001', 'Pd_laser_l', 'Pd_laser_r', 'Uplink'):
        x, y, z = orb._node(name, lift)
        base = _sd_surface(x, y) + lift
        if name in ('Mount_mg.001', 'Uplink'):
            base = z - .9
        if name == 'Mount_mg':
            base = 2.3 + lift
        top = z - (.6 if name == 'Uplink' else .2)
        if top - base > .05:
            part.cyl(.36, top - base, loc=(x, y, (top + base) / 2), seg=10, bevel=.03, bseg=1)


def _sd_crash_turrets(a, lift, wreck):
    """The two 40 mm turrets that wake on the ground (prompt 20 F.3), on pylons on the upper hull."""
    for s, mount in ((1, 'Mount_gun.002'), (-1, 'Mount_gun.003')):
        loc = (s * 6.5, 6.0, 2.2 + lift)
        base = _sd_surface(loc[0], loc[1]) + lift
        a.part(f'Crash_pylon_{mount[-3:]}', 'Armor').cyl(.5, loc[2] - base, loc=(loc[0], loc[1], (loc[2] + base) / 2), seg=10, bevel=.03, bseg=1)
        autocannon(a, mount, loc, length=2.4, size=(1.3, 1.5, .62))


def _warship(a, lift, wreck):
    _suffixed(a)
    rng = random.Random(1977)
    _sd_hull(a, lift, wreck, rng)
    _sd_superstructure(a, lift, wreck)
    _sd_engines(a, lift, wreck)
    for name in ('Thruster_fl', 'Thruster_fr'):
        sx = 1 if orb.NODES[name][0] < 0 else -1
        _sd_thruster(a, name, lift, 0.0, strut=(-sx * 1.4, 0, -.7))
    for name in ('Thruster_rl', 'Thruster_rr'):
        _sd_thruster(a, name, lift, .85)
    orb._build_main_turret(a, orb._node('Turret', lift))
    orb._build_coilgun(a, 'Mount_gun', 'Muzzle_gun', '', orb._node('Mount_gun', lift), deployed=wreck)
    orb._build_coilgun(a, 'Mount_gun.001', 'Muzzle_gun.001', '_001', orb._node('Mount_gun.001', lift), deployed=wreck)
    orb._build_flak(a, 'Mount_mg', 'Muzzle_mg', '', orb._node('Mount_mg', lift), deployed=wreck)
    orb._build_flak(a, 'Mount_mg.001', 'Muzzle_mg.001', '_001', orb._node('Mount_mg.001', lift), deployed=wreck)
    orb._build_pd_laser(a, 'Pd_laser_l', orb._node('Pd_laser_l', lift))
    orb._build_pd_laser(a, 'Pd_laser_r', orb._node('Pd_laser_r', lift))
    orb._build_pod_bay(a, orb._node('Pod_bay', lift))
    orb._build_uplink(a, orb._node('Uplink', lift))
    _sd_pylons(a, lift, wreck)
    _sd_crash_turrets(a, lift, wreck)
    if wreck:
        orb._crater_ring(a)
        for i, (right, forward, w, d) in enumerate(orb.DEBRIS):
            x, y, _z = orb._pos(right, forward)
            orb._debris_pile(a, x, y, w, d, 1.8, seed=200 + i)


def silver_bug(a):
    """Icarus, the warship spacecraft: see the module docstring."""
    _warship(a, 0.0, False)


def silver_bug_wreck(a):
    """Icarus crashed, for its ground phase: see the module docstring."""
    _warship(a, orb.LIFT, True)


# ============================================================================== Typhon (the boss review)

def _ellipse_ring(y, hw, hh, zc, n=16, flat=0.0):
    """A hull section at y: a super-ellipse of half-width hw and half-height hh round zc, its top flattened by `flat`."""
    pts = []
    for k in range(n):
        u = k * math.tau / n
        c, s = math.cos(u), math.sin(u)
        x = hw * math.copysign(abs(c) ** .8, c)
        z = hh * math.copysign(abs(s) ** (.8 - flat if s > 0 else .9), s)
        pts.append((x, y, zc + z))
    return pts


def typhon(a):
    """Typhon, rebuilt on the Project 941 (Typhoon) lines: a broad, flattened hull in a dark anechoic coat, the
    missile hump aft of the sail with its launch doors, a long streamlined sail, bow planes, a cruciform tail with
    twin shrouded screws, the bow sonar dome. Nodes as before: `Part_sail` (with `Mount_missile` on top),
    `Part_doors_l` / `_r`, `Part_rudder`, `Part_sonar`, `Mount_gun` (the deck gun)."""
    _suffixed(a)
    prof = [(-29.5, .3, .3), (-28.0, 1.8, 1.4), (-25.0, 3.6, 2.5), (-20.0, 5.3, 3.2), (-12.0, 6.0, 3.45), (0.0, 6.0, 3.5),
            (12.0, 5.9, 3.45), (19.0, 5.2, 3.1), (24.0, 3.8, 2.4), (27.5, 2.0, 1.4), (29.5, .5, .5)]
    a.part('Hull', 'Undercarriage').loft([_ellipse_ring(y, hw, hh, .2, 18, .35) for y, hw, hh in prof], bevel=.02, seg=1)
    # The anechoic coat's panel lines, a band in the side's colour at the waterline, the hump over the tubes.
    for s in (-1, 1):
        a.part('Waterline_band', 'Team').box((.06, 24.0, .45), loc=(s * 6.0, 0, .6), bevel=0)
    a.part('Missile_hump', 'Undercarriage').box((6.2, 14.0, .5), loc=(0, 6.0, 3.45), bevel=.4, seg=2, taper=(.9, .96))
    ps = pv(a, 'Part_sail', (0, -6.0, 3.6))
    sail = a.part('Sail_body', 'Team', ps)
    sail.box((3.0, 9.2, 4.9), loc=(0, .2, 2.5), bevel=.9, seg=3, taper=(.72, .66), shift=(0, .5))
    a.part('Sail_top', 'Armor', ps).box((2.0, 5.4, .2), loc=(0, .6, 5.0), bevel=.08, seg=1)
    a.part('Sail_windows', 'Glass', ps).box((1.6, .05, .3), loc=(0, -2.62, 4.4), rot=(.5, 0, 0), bevel=0)
    a.part('Sail_planes', 'Armor', ps).box((9.0, 1.8, .3), loc=(0, -1.2, 3.4), bevel=.14, seg=1, taper=(.8, 1))
    masts = a.part('Sail_masts', 'Steel', ps)
    for x, y, h in ((0, 1.8, 2.2), (.35, 2.6, 1.6), (-.35, 2.9, 1.2)):
        masts.cyl(.13, h, loc=(x, y, 5.0 + h / 2), seg=8, bevel=0)
    rocket_box(a, 'Mount_missile', 'Muzzle_missile', (0, -3.0, 9.0), size=(1.4, 1.8, .9))
    for s, name in ((1, 'Part_doors_l'), (-1, 'Part_doors_r')):
        pd = pv(a, name, (s * 2.2, 6.0, 3.8))
        lids = a.part(f'Doors_{name[5:]}', 'Armor', pd)
        rims = a.part(f'Doors_rim_{name[5:]}', 'Hazard', pd)
        for k in range(5):
            lids.cyl(.8, .16, loc=(0, -4.0 + k * 2.0, 0), seg=16, bevel=.03, bseg=1)
            rims.torus(.82, .06, loc=(0, -4.0 + k * 2.0, .08), seg=16, ring=6)
    a.part('Bow_planes', 'Armor').box((12.4, 1.6, .25), loc=(0, -20.0, 1.2), bevel=.1, seg=1, taper=(.8, 1))
    pr = pv(a, 'Part_rudder', (0, 27.0, 1.0))
    fins = a.part('Rudder_fins', 'Armor', pr)
    fins.box((.4, 3.4, 5.6), loc=(0, -.2, 1.6), bevel=.1, seg=1, taper=(1, .6))
    fins.box((.4, 3.0, 3.2), loc=(0, -.2, -2.2), bevel=.1, seg=1, taper=(1, .6))
    fins.box((8.6, 2.8, .35), loc=(0, 0, -.2), bevel=.1, seg=1, taper=(.9, .8))
    shroud = a.part('Screw_shrouds', 'Team', pr)
    blades = a.part('Screws', 'Steel', pr)
    for s in (-1, 1):
        shroud.torus(1.25, .22, loc=(s * 2.6, 1.4, -.8), rot=(R90, 0, 0), seg=18, ring=6)
        blades.cyl(1.05, .25, loc=(s * 2.6, 1.4, -.8), rot=FORWARD, seg=7, bevel=0)
        a.part('Screw_hubs', 'Armor', pr).cyl(.3, 1.2, r2=.1, loc=(s * 2.6, 1.8, -.8), rot=(-R90, 0, 0), seg=10, bevel=0)
    pn = pv(a, 'Part_sonar', (0, -26.0, 1.2))
    a.part('Sonar_dome', 'Rubber', pn).sphere((2.6, 3.0, 1.9), loc=(0, 0, 0), seg=18, rings=8)
    a.part('Sonar_band', 'Team', pn).torus(2.1, .1, loc=(0, .7, .1), rot=(R90, 0, 0), seg=18, ring=5)
    a.part('Sonar_emitter', 'Energy', pn).cyl(.35, .05, loc=(0, -2.95, .3), rot=FORWARD, seg=10, bevel=0)
    autocannon(a, 'Mount_gun', (0, -16.0, 3.8), length=4.0, r=.1, size=(1.9, 2.4, 1.0))


# ============================================================================== Caspian (the boss review)

def caspian(a):
    """Caspian, rebuilt on the Lun-class ekranoplan's lines (MD-160, the "Caspian Sea Monster"): a long flying-boat
    hull with a planing step and chines, the canard pylon with eight turbofans in two banks, three pairs of
    anti-ship canisters on the back, low stub wings with endplate floats, the tall fin and its T-tail, a radome
    nose. Nodes as before: `Part_engines`, `Part_launcher`, `Part_wing_l` / `_r`, `Mount_gun` (the tail CIWS)."""
    _suffixed(a)
    prof = [(-25.5, .3, 4.2, .5), (-24.0, 1.6, 5.6, 1.4), (-21.0, 2.8, 6.4, 1.0), (-15.0, 3.0, 6.6, .8), (0.0, 3.0, 6.5, .8),
            (4.0, 2.9, 6.4, 1.1), (12.0, 2.6, 6.3, 1.6), (20.0, 2.0, 6.2, 2.4), (24.5, 1.1, 6.1, 3.6), (26.0, .3, 5.9, 4.6)]
    rings = []
    for y, hw, zt, zk in prof:
        rings.append([(hw * .6, y, zt), (hw, y, zt - .9), (hw, y, zk + 1.2), (hw * .55, y, zk + .25), (0, y, zk),
                      (-hw * .55, y, zk + .25), (-hw, y, zk + 1.2), (-hw, y, zt - .9), (-hw * .6, y, zt)])
    a.part('Hull', 'Team').loft(rings, bevel=.03, seg=1)
    chine = a.part('Hull_chines', 'Armor')
    for (y0, hw0, _, zk0), (y1, hw1, _, zk1) in zip(prof, prof[1:]):
        for s in (-1, 1):
            chine.limb((s * hw0, y0, zk0 + 1.2), (s * hw1, y1, zk1 + 1.2), .22, .16, bevel=0, seg=1)
    a.part('Planing_step', 'Undercarriage').box((5.4, .5, .6), loc=(0, 4.0, 1.25), bevel=.05, seg=1)
    a.part('Radome', 'Medical').sphere((1.1, 1.6, 1.0), loc=(0, -25.2, 4.2), seg=14, rings=6)
    a.part('Cockpit', 'Glass').box((3.4, 2.6, .6), loc=(0, -19.2, 6.55), rot=(-.28, 0, 0), bevel=.1, seg=1)
    ports = a.part('Portholes', 'Glass')
    for s in (-1, 1):
        for k in range(14):
            ports.box((.05, .45, .35), loc=(s * 3.01, -12.0 + k * 1.9, 4.9), bevel=0)
        a.part('Side_stripe', 'Armor').box((.06, 40.0, .3), loc=(s * 3.02, 0, 3.7), bevel=0)
    for s, name in ((1, 'Part_wing_l'), (-1, 'Part_wing_r')):
        p = pv(a, name, (s * 11.0, 0, 2.6))
        a.part(f'Wing_{name[5:]}', 'Team', p).box((16.4, 9.0, .75), loc=(-s * .4, 0, 0), rot=(0, s * -.05, 0), bevel=.28, seg=2,
                                                 taper=(1, .62), shift=(0, 1.2))
        a.part(f'Wing_flaps_{name[5:]}', 'Armor', p).box((14.0, 1.2, .2), loc=(-s * .4, 4.2, .2), bevel=.05, seg=1)
        a.part(f'Float_{name[5:]}', 'Armor', p).box((1.2, 8.0, 2.2), loc=(s * 7.9, -.6, -.6), bevel=.4, seg=2, taper=(.8, .8))
        a.part(f'Wing_mark_{name[5:]}', 'Hazard', p).box((1.2, 4.0, .06), loc=(s * 5.0, 0, .42), bevel=0)
    pe = pv(a, 'Part_engines', (0, -18.0, 5.4))
    a.part('Canards', 'Armor', pe).box((15.0, 3.4, .55), loc=(0, .4, 1.25), bevel=.18, seg=1, taper=(.9, .7), shift=(0, .5))
    jets = a.part('Jets', 'Steel', pe)
    lips = a.part('Jet_intakes', 'Undercarriage', pe)
    glow = a.part('Jet_glow', 'Energy', pe)
    for i in range(4):
        for s in (-1, 1):
            x = s * (1.7 + i * 1.55)
            jets.cyl(.64, 3.6, r2=.5, loc=(x, 0, 1.95), rot=FORWARD, seg=14, bevel=.05, bseg=1)
            lips.cyl(.5, .06, loc=(x, -1.82, 1.95), rot=FORWARD, seg=12, bevel=0)
            glow.cyl(.36, .05, loc=(x, 1.83, 1.95), rot=FORWARD, seg=12, bevel=0)
    pl = pv(a, 'Part_launcher', (0, 2.0, 6.4))
    a.part('Launcher_fairing', 'Armor', pl).box((4.6, 10.0, .5), loc=(0, -.5, .2), bevel=.2, seg=1)
    tubes = a.part('Launch_canisters', 'Team', pl)
    caps = a.part('Canister_caps', 'Charred', pl)
    for k in range(3):
        for s in (-1, 1):
            tubes.cyl(.75, 7.0, loc=(s * .95, -3.0 + k * 3.0, .9 + k * .5), rot=(R90 - .15, 0, 0), seg=14, bevel=.05, bseg=1)
            caps.cyl(.62, .05, loc=(s * .95, -3.0 + k * 3.0 - 3.49, .9 + k * .5 + .53), rot=(R90 - .15, 0, 0), seg=12, bevel=0)
    fin = a.part('Tail_fin', 'Team')
    fin.loft([[(.45, 15.5, 6.0), (.45, 24.5, 6.0), (-.45, 24.5, 6.0), (-.45, 15.5, 6.0)],
              [(.3, 20.5, 16.0), (.3, 25.0, 16.0), (-.3, 25.0, 16.0), (-.3, 20.5, 16.0)]])
    a.part('Stabiliser', 'Armor').box((19.0, 4.4, .6), loc=(0, 23.0, 16.2), bevel=.2, seg=1, taper=(.7, .8), shift=(0, .8))
    a.part('Fin_mark', 'Hazard').box((.95, 2.0, 1.2), loc=(0, 21.0, 12.0), bevel=0)
    ciws(a, 'Mount_gun', (0, 17.0, 6.4))


# ============================================================================== Daedalus (the boss review)

# An Acclamator-like assault ship: a thicker, blunter wedge than Icarus's (y, half-width, top z, belly z).
ACC = [(16.0, 10.0, 2.6, -1.9), (8.0, 8.2, 2.6, -2.0), (0.0, 6.2, 2.4, -1.9), (-6.0, 4.6, 2.0, -1.45),
       (-12.0, 2.6, 1.4, -1.0), (-17.0, .6, .6, -.4), (-18.0, .2, .3, -.2)]


def daedalus(a):
    """Daedalus, rebuilt as an assault ship on the Republic Acclamator's lines (Star Wars: Attack of the Clones): a
    blunt wedge in the Icarus family (Aurel's fleet), a tall spine with the bridge tower aft, turbolaser turrets
    drawn along the spine, an engine bank, the three drop-pod bays under the belly and two 30 mm guns hanging under
    the nose. Nodes as before: `Pod_bay_1` .. `_3`, `Mount_gun` / `.001`, `Pd_laser_l` / `_r`, `Thruster_main`."""
    _suffixed(a)
    rng = random.Random(1952)
    _sd_hull(a, 0.0, False, rng, prof=ACC, doors=False, hangar=False)
    spine = a.part('Spine', 'MetalSheet')
    spine.box((3.4, 17.0, 1.6), loc=(0, 4.5, _sd_surface(0, 4.5, ACC) + .75), bevel=.12, seg=1, taper=(.8, .95))
    z = _sd_surface(0, 11.0, ACC) + 1.5
    spine.box((2.2, 2.4, 3.2), loc=(0, 11.5, z + 1.5), bevel=.1, seg=1, taper=(.7, .8))
    spine.box((6.4, 2.2, 1.1), loc=(0, 11.5, z + 3.5), bevel=.1, seg=1, taper=(.95, .8))
    a.part('Bridge_windows', 'Lamp').box((5.6, .05, .18), loc=(0, 10.42, z + 3.55), bevel=0)
    a.part('Spine_lights', 'Lamp').box((2.4, .05, .1), loc=(0, -3.95, _sd_surface(0, 4.5, ACC) + 1.2), bevel=0)
    tur = a.part('Turbolasers', 'Armor')
    guns = a.part('Turbolaser_barrels', 'Steel')
    for s in (-1, 1):
        for y in (-2.0, 3.5, 9.0):
            x = s * 3.3
            base = _sd_surface(x, y, ACC)
            tur.box((1.3, 1.5, .6), loc=(x, y, base + .3), bevel=.1, seg=1, taper=(.8, .8))
            for o in (-.25, .25):
                guns.cyl(.07, 1.6, loc=(x + o, y - 1.4, base + .45), rot=FORWARD, seg=6, bevel=0)
    right, forward, up = orb.NODES['Thruster_main']
    t = a.pivot('Thruster_main', orb._pos(right, forward, up))
    a.part('Engine_housing', 'Armor', t).box((12.0, 1.6, 3.4), loc=(0, 1.1, -.2), bevel=.15, seg=1, taper=(.92, .9))
    nozzle = a.part('Engine_nozzles', 'Steel', t)
    glow = a.part('Engine_glow', 'TeamGlow', t)
    for x, r in ((0.0, 1.2), (3.0, 1.1), (-3.0, 1.1), (5.4, .7), (-5.4, .7)):
        nozzle.cyl(r, 1.0, loc=(x, 2.3, 0), rot=FORWARD, seg=18, bevel=.05, bseg=1)
        glow.cyl(r * .66, .04, loc=(x, 2.84, 0), rot=FORWARD, seg=16, bevel=0)
    orb._build_pd_laser(a, 'Pd_laser_l', orb._node('Pd_laser_l', 0.0))
    orb._build_pd_laser(a, 'Pd_laser_r', orb._node('Pd_laser_r', 0.0))
    pyl = a.part('Pylons', 'Armor')
    for name in ('Pd_laser_l', 'Pd_laser_r'):
        x, y, zz = orb._node(name, 0.0)
        base = _sd_surface(x, y, ACC)
        pyl.cyl(.3, zz - base - .1, loc=(x, y, (zz - .1 + base) / 2), seg=10, bevel=.03, bseg=1)
    for i, (x, y) in enumerate(((4.0, 2.0), (0.0, 5.0), (-4.0, 2.0))):
        p = pv(a, f'Pod_bay_{i + 1}', (x, y, -2.0))
        a.part(f'Bay_frame_{i + 1}', 'Armor', p).box((3.0, 3.6, .5), loc=(0, 0, 0), bevel=.1, seg=1)
        a.part(f'Bay_pod_{i + 1}', 'Team', p).cyl(1.0, 1.6, loc=(0, 0, -.8), seg=14, r2=.7, bevel=.05, bseg=1)
        a.part(f'Bay_glow_{i + 1}', 'Energy', p).cyl(.5, .05, loc=(0, 0, -1.62), seg=12, bevel=0)
    hanging_gun(a, 'Mount_gun', 'Muzzle_gun', (2.4, -6.0, -1.4))
    hanging_gun(a, 'Mount_gun.001', 'Muzzle_gun.001', (-2.4, -6.0, -1.4))


BUILDERS = {
    'ixion': (ixion, dict(ao_distance=1.2, grime_height=1.6)),
    'silver_bug': (silver_bug, dict(ao_distance=.6, ground=False)),
    'silver_bug_wreck': (silver_bug_wreck, dict(ao_distance=1.1, grime_height=1.2)),
    # The boss review: the weakest first passes redrawn from their references.
    'typhon': (typhon, dict(ao_distance=1.0, grime_height=.3)),
    'caspian': (caspian, dict(ao_distance=1.0, grime_height=.3)),
    'daedalus': (daedalus, dict(ao_distance=.6, ground=False)),
}
