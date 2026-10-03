"""Play-test 14 model wave M5 (lane models): five vehicles redrawn from scratch (owner, Docs/prompts/playtest14_vi.txt:
"xe ew hammer + laser aa + command vehicle co ve xau, nen ve lai", "wheeled tank thi thap sung to qua nhin ki",
"stealth carrier strike jet: nhin hoi xau, nen ve lai"; DECISIONS "Play-test 14 model wave M5").

- wheeled_gun: a Centauro / AMX-10RC-class 8x8 wheeled tank destroyer with a compact two-man 105 mm turret in
  proportion to the hull (about a third of its length, three quarters of its width), the long gun with its bore
  evacuator and multi-baffle brake on a baked Elevation pivot at the trunnion.
- command_vehicle: a 4x4 protected command vehicle (IVECO LMV / Dingo command read): bonnet, armoured crew cell,
  raised command module, the remote 12.7 mm station on the roof (Mount_mg), SATCOM dome, folded mast, tied-down whips.
- ew_jammer: the Krasukha-4 read on a BAZ-6910-class 8x8: the forward crew cab with the roof 12.7 mm (Turret), the
  engine bay, the long equipment van with jacks, ladders, A/C, and the big curved reflector on its turntable (Radar).
- iron_beam: an Iron Beam-M read (laser air defence) on an 8x8 tactical truck: the power and thermal module with its
  fans, the search radar (Radar), the beam director turret (Turret) with the big telescope and glowing aperture.
- stealth_naval_strike: the A-12 Avenger II carrier flying wing, redrawn: a blended centre body with the tandem
  canopy on its hump, sawtooth-edged doors and panels in place of the old grid, dark RAM edges, buried intakes,
  the exhaust troughs over the trailing edge, the bombs half-sunk in the bays (Bombs), wing-fold hinges.

Every round leaves from a barrel, tube or aperture with its Muzzle_* point at the mouth (owner 03/10). Built from
frontier_kit / mb_kit27 / mb_kit35 / mb_p35c_parts primitives only. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau


def _merge(a):
    """Fold static parts that share material and parent into one mesh each (glb_check's renderer hard cap), keeping
    every role, runtime and wreck-part name (mb_p35_w5parts.merge_static's list plus the wheel hubs)."""
    keep = W.merge_static.__defaults__[0].replace('^(', '^(Hubs?|Spare_\w+|', 1)
    W.merge_static(a, keep=keep)


def _half(zb, xk, xl, zc, zf, xs, zu, xt, zt):
    """A wheeled hull's half section (bottom centre up the +X side to the top centre): the keel flat, the V to the
    chine, the lower side inside the wheels, the sponson floor out over the wheels, the upper side, the deck edge."""
    return [(0, zb), (xk, zb + .03), (xl, zc), (xl, zf), (xs, zf), (xs - .02, zu), (xt, zt), (0, zt + .02)]


# Lean fittings: the wheeled units are seen in numbers (quality_gate NUMBERS_CAP: at most 1.5 x 5,000 triangles),
# so lamps, periscopes, bolts and hooks are boxes; the triangles go to the shapes that read at battle range.
def _lamp(a, loc, facing=-1, w=.16, h=.11, glow='Lamp', parent=None, guard=False):
    """A lamp on a front (facing -1) or rear (+1) face: a housing box, the lit lens, an optional guard bar."""
    x, y, z = loc
    a.part('Lamp_housings', 'Armor', parent).box((w, .08, h), loc=(x, y, z), bevel=0)
    a.part('Lamps', glow, parent).box((w * .78, .02, h * .7), loc=(x, y + facing * .045, z), bevel=0)
    if guard:
        a.part('Lamp_guards', 'Steel', parent).box((w + .04, .025, .025), loc=(x, y + facing * .1, z), bevel=0)


def _scope(a, loc, facing=(0, -1), parent=None, size=(.14, .1, .09)):
    """A vision block / periscope head: an armoured box with its glass face towards `facing` (x, y)."""
    x, y, z = loc
    u = math.atan2(facing[0], -facing[1])
    a.part('Periscopes', 'Armor', parent).box(size, loc=(x, y, z), rot=(0, 0, u), bevel=0)
    gx, gy = x + facing[0] * (size[1] / 2 + .005), y + facing[1] * (size[1] / 2 + .005)
    a.part('Glass', 'Glass', parent).box((size[0] * .8, .01, size[2] * .55), loc=(gx, gy, z + size[2] * .1),
                                         rot=(0, 0, u), bevel=0)


def _hook(a, loc, facing=-1):
    """A towing eye: two cheeks and the pin, standing out of a front (-1) or rear (+1) face."""
    x, y, z = loc
    hk = a.part('Kit_tow', 'Steel')
    for dx in (-.05, .05):
        hk.box((.025, .12, .12), loc=(x + dx, y + facing * .06, z), bevel=0)
    hk.box((.14, .03, .03), loc=(x, y + facing * .1, z), bevel=0)


def _wheel(a, centre, r, w, s, seg=16, parent=None, tyre='Tyres', rim='Wheels'):
    """A lean round tyre on an axle along X, outer face on side s: the casing with shoulders (no lug zig-zag, which
    reads as a hexagon at low segment counts), the dished rim and the hub boss."""
    rot = (0, s * R90, 0)
    k.lathe(a.part(tyre, 'Rubber', parent), [(r * .62, -w / 2), (r * .9, -w / 2), (r, -w * .3), (r, w * .3),
                                             (r * .9, w / 2), (r * .62, w / 2)], loc=centre, rot=rot, seg=seg,
            worn=(2, 3))
    f = w / 2
    k.lathe(a.part(rim, 'Armor', parent), [(r * .64, f - .01), (r * .58, f + .006), (r * .5, f - .04),
                                           (r * .22, f - .05), (0, f - .05)], loc=centre, rot=rot, seg=10 if seg > 14 else 8,
            worn=(1,))
    k.lathe(a.part('Hubs', 'Steel', parent), [(r * .14, f - .045), (r * .11, f + .02), (0, f + .03)], loc=centre,
            rot=rot, seg=6)


def _frame_of(loc, facing):
    rot = K.rot_to(facing)
    return K.frame(loc, rot), rot


def _grille(a, loc, w, h, facing=(0, -1, 0), slats=4, parent=None, frame_mat='Armor'):
    """A lean louvre panel: a frame plate, the dark recess in front of it and three or four slats."""
    m, rot = _frame_of(loc, facing)
    a.part('Grille_frames', frame_mat, parent).box((w + .08, h + .08, .03), loc=K._at(m, (0, 0, -.005)), rot=rot,
                                                   bevel=0)
    g = a.part('Grilles', 'Undercarriage', parent)
    g.box((w, h, .02), loc=K._at(m, (0, 0, .012)), rot=rot, bevel=0)
    n = min(slats, 4)
    for i in range(n):
        y = -h / 2 + (i + .5) * h / n
        g.box((w * .96, .025, .03), loc=K._at(m, (0, y, .03)), rot=rot, bevel=0)


def _door(a, loc, size=(1.0, 2.0), normal=(0, -1, 0), parent=None, mat='Armor', frame_mat='Steel'):
    """A lean door on a wall: frame plate, leaf, vision slot, handle (loc = bottom centre)."""
    w, h = size
    m, rot = _frame_of(loc, normal)
    a.part('Door_frames', frame_mat, parent).box((w + .1, h + .06, .02), loc=K._at(m, (0, h / 2, .0)), rot=rot,
                                                 bevel=0)
    a.part('Doors', mat, parent).box((w, h, .03), loc=K._at(m, (0, h / 2, .02)), rot=rot, bevel=0)
    a.part('Door_slots', 'Undercarriage', parent).box((w * .4, .05, .015), loc=K._at(m, (0, h * .74, .04)), rot=rot,
                                                      bevel=0)
    a.part('Kit_handles', 'Steel', parent).box((.1, .03, .04), loc=K._at(m, (w * .32, h * .45, .045)), rot=rot,
                                               bevel=0)


def _lampk(a, loc, facing=(0, -1, 0), r=.09, parent=None, guard=True, mat='Armor', glow='Lamp'):
    """K.lamp's call shape on the lean _lamp (front or rear faces)."""
    _lamp(a, loc, facing=1 if facing[1] > 0 else -1, w=r * 2, h=r * 1.4, glow=glow, parent=parent, guard=guard)


def _axle(a, y, z, half):
    """A lean beam axle with its differential box."""
    ax = a.part('Axles', 'Undercarriage')
    ax.cyl(.07, half * 2, loc=(0, y, z), rot=(0, R90, 0), seg=6, bevel=0)
    ax.box((.32, .3, .26), loc=(0, y, z), bevel=0)


def _smoke(a, parent, loc, s, count=3, yaw=0.0):
    """Smoke-grenade dischargers on side s at loc: a bracket and a fan of tubes pointing up and out."""
    x, y, z = loc
    part = a.part('Smoke_launchers', 'Armor', parent)
    part.box((.14, (count - 1) * .1 + .12, .05), loc=(x, y, z - .05), bevel=0)
    for i in range(count):
        yy = y + (i - (count - 1) / 2) * .1
        k.lathe(part, [(.04, -.08), (.046, .08), (.03, .08), (0, .05)], loc=(x, yy, z + .03),
                rot=(-.2 + .1 * i, s * .75, yaw), seg=6)


def _whip(a, parent, loc, h, lean, part='Antennas'):
    """A whip on a spring base leaning back (+Y) by `lean` radians (tied down as on real vehicles)."""
    K.whip_antenna(a.part(part, 'Steel', parent), loc, h=h, r=.02, lean=-lean)


def _wishbones(a, s, tx, y, wr, xl, zf, parent=None):
    """The independent suspension of one wheel: the lower arm from the hull side to the hub, the coil-over."""
    arm = a.part('Suspension', 'Undercarriage', parent)
    arm.limb((s * xl, y, wr - .1), (s * (tx - .18), y, wr - .05), .1, .06, bevel=0)
    a.part('Springs', 'Steel', parent).cyl(.055, zf - wr - .12, loc=(s * (xl + .12), y + .18, (zf + wr) / 2 + .02),
                                          rot=(0, s * .25, 0), seg=6, bevel=0)


# ============================================================================= wheeled_gun
G_WR, G_TW, G_TX = .5, .34, .93
G_AXLES = (-2.05, -.75, .6, 1.9)
G_DECK = 1.6
G_TUR = (0, .45, G_DECK)            # the turret ring centre


def _gun_hull(a):
    hull = a.part('Hull', 'Team')
    K.section_loft(hull, [
        (-3.15, _half(.8, .3, .58, .84, .92, .96, 1.0, .9, 1.04)),
        (-3.05, _half(.64, .34, .66, .74, 1.0, 1.1, 1.12, 1.0, 1.17)),
        (-2.7, _half(.48, .38, .68, .62, 1.06, 1.17, 1.22, 1.03, 1.27)),
        (-1.3, _half(.42, .4, .68, .58, 1.06, 1.18, 1.42, 1.0, G_DECK - .02)),
        (2.75, _half(.42, .4, .68, .58, 1.06, 1.18, 1.42, 1.0, G_DECK - .02)),
        (3.05, _half(.6, .36, .66, .68, 1.06, 1.16, 1.4, .98, 1.55)),
    ])
    # The sponson floor lip and the upper chine (a darker band reads the hull's break at range).
    arm = a.part('Hull_plates', 'Armor')
    for s in (-1, 1):
        arm.box((.04, 5.6, .06), loc=(s * 1.19, -.1, 1.07), bevel=0)
        arm.box((.03, 5.0, .05), loc=(s * 1.19, .1, 1.41), bevel=0)
    # Add-on armour on the upper sides: four panels each side with gaps between them.
    plates = a.part('Applique', 'Team')
    for s in (-1, 1):
        for y0, y1 in ((-2.45, -1.45), (-1.35, .0), (.1, 1.25), (1.35, 2.6)):
            plates.box((.05, y1 - y0, .3), loc=(s * 1.205, (y0 + y1) / 2, 1.24), bevel=0)


def _gun_running_gear(a):
    for y in G_AXLES:
        for s in (-1, 1):
            _wheel(a, (s * G_TX, y, G_WR), G_WR, G_TW, s)
            _wishbones(a, s, G_TX, y, G_WR, .68, 1.06)
    a.part('Driveline', 'Undercarriage').cyl(.06, 4.2, loc=(0, -.05, .5), rot=K.FORWARD, seg=6, bevel=0)


def _gun_front(a):
    """The nose: lamps in guards, tow eyes, the driver's hatch with periscopes, the engine deck's louvres and the
    exhaust on the right, the splash rib, pioneer tools on the glacis."""
    for s in (-1, 1):
        _lamp(a, (s * .78, -3.12, .98), guard=True)
        _lamp(a, (s * .55, -3.11, .99), w=.08, h=.06, glow='Alloy')
        _hook(a, (s * .42, -3.15, .8))
    a.part('Splash_rib', 'Armor').box((1.9, .06, .1), loc=(0, -2.62, 1.3), rot=(.23, 0, 0), bevel=0)
    k.block(a.part('Hatches', 'Armor'), (.56, .66, .06), loc=(.52, -1.56, G_DECK - .03), chamfer=0)
    a.part('Hatch_fittings', 'Steel').box((.46, .04, .04), loc=(.52, -1.22, G_DECK + .04), bevel=0)
    for dx in (-.18, 0, .18):
        _scope(a, (.52 + dx, -1.95, 1.52))
    for y in (-2.35, -1.75):
        _grille(a, (-.5, y, 1.29 + (y + 2.7) * .23 + .02), .7, .48, facing=(0, -.22, 1), slats=4, frame_mat='Armor')
    a.part('Exhaust_box', 'Armor').box((.08, .7, .26), loc=(-1.22, -2.0, 1.27), bevel=0)
    sl = a.part('Exhaust_louvres', 'Undercarriage')
    for i in range(3):
        sl.box((.02, .6, .04), loc=(-1.265, -2.0, 1.19 + i * .08), bevel=0)
    a.pivot('Point_exhaust', (-1.3, -2.0, 1.3))
    K.soot(a, (-1.25, -2.0, 1.27), radius=.5, k=.4)
    tl = a.part('Tools', 'Wood')
    tl.limb((.15, -2.85, 1.22), (.85, -2.3, 1.35), .05, .04, bevel=0)
    tl.limb((.2, -2.65, 1.26), (.8, -2.15, 1.38), .045, .04, bevel=0)
    a.part('Tool_heads', 'Steel').box((.18, .06, .2), loc=(.9, -2.27, 1.38), rot=(.23, 0, -.66), bevel=0)
    a.part('Kit_cables', 'Steel').tube([(1.16, -2.6, 1.3), (1.2, -1.2, 1.38), (1.2, .3, 1.38)], .025, seg=4)


def _gun_sides(a):
    """Stowage bins on the sponsons, side steps, grab rails, the rear: door, lamps, jerrycan, the tow pintle."""
    bins = a.part('Stowage_bins', 'Team')
    lat = a.part('Kit_latches', 'Steel')
    for s in (-1, 1):
        for (y, L) in ((-1.0, .8), (1.3, 1.1)):
            bins.box((.17, L, .2), loc=(s * 1.08, y, 1.57), bevel=0)
            lat.box((.02, .06, .05), loc=(s * 1.17, y, 1.58), bevel=0)
        a.part('Steps', 'Steel').box((.12, .4, .03), loc=(s * 1.2, -.06, .95), bevel=0)
        a.part('Grab_rails', 'Steel').tube([(s * 1.0, 2.3, G_DECK), (s * 1.02, 2.3, G_DECK + .1),
                                            (s * 1.02, 2.85, G_DECK + .1), (s * 1.0, 2.85, G_DECK)], .014, seg=4)
        _lamp(a, (s * .85, 3.06, 1.3), facing=1, w=.1, h=.07, glow='LavaGlow')
        _hook(a, (s * .45, 3.06, .74), facing=1)
    _door(a, (.22, 3.07, .7), size=(.7, .68), normal=(0, 1, 0), mat='Team', frame_mat='Armor')
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-.6, 3.12, .9))
    a.part('Tow_pintle', 'Steel').cyl(.06, .14, loc=(0, 3.14, .6), rot=K.FORWARD, seg=6, bevel=0)
    k.block(a.part('Hatches', 'Armor'), (.55, .6, .05), loc=(.45, 2.25, G_DECK - .01), chamfer=0)
    k.block(a.part('Stowage', 'Crate'), (.8, .4, .22), loc=(-.4, 2.55, G_DECK - .01), chamfer=.02)
    a.pivot('Point_fire', (0, 1.9, G_DECK + .1))


def _gun_turret(a):
    t = a.pivot('Turret', G_TUR)
    body = a.part('Turret_body', 'Team', t)
    plan = [(-.52, -1.08), (.52, -1.08), (.84, -.5), (.88, .55), (.8, 1.0), (-.8, 1.0), (-.88, .55), (-.84, -.5)]
    k.extrude(body, plan, .5, loc=(0, 0, .3), axis='Z', chamfer=.04, corner=.03, taper=(.9, .94))
    k.ring(a.part('Turret_ring', 'Armor', t), [(.86, -.02), (.9, -.02), (.9, .06), (.86, .06)], seg=16)
    # Cheek armour modules, angled in plan.
    ch = a.part('Turret_cheeks', 'Team', t)
    for s in (-1, 1):
        k.extrude(ch, [(s * .3, -1.1), (s * .54, -1.1), (s * .87, -.52), (s * .8, -.46), (s * .5, -1.0),
                       (s * .3, -1.0)][::s], .4, loc=(0, -.02, .3), axis='Z', chamfer=.02, taper=(.92, .96))
        a.part('Turret_plates', 'Armor', t).box((.04, .95, .3), loc=(s * .87, .02, .2), rot=(0, s * -.06, 0),
                                                bevel=0)
        k.block(a.part('Stowage_bins', 'Team', t), (.2, .5, .24), loc=(s * .9, .72, .02), chamfer=.02)
        _smoke(a, t, (s * .78, -.5, .58), s)
        k.block(a.part('Sensors', 'Undercarriage', t), (.1, .08, .06), loc=(s * .76, -.98, .52), chamfer=0)
    # The bustle rack: a tube cage round the turret's rear with a crate and a net roll in it.
    rk = a.part('Bustle_rack', 'Steel', t)
    pts = [(.8, .95), (.8, 1.38), (-.8, 1.38), (-.8, .95)]
    for z in (.12, .4):
        rk.tube([(x, y, z) for x, y in pts], .016, seg=4)
    for x, y in pts[1:3] + [(.3, 1.38), (-.3, 1.38)]:
        rk.limb((x, y, .1), (x, y, .42), .025, .025, bevel=0)
    K.crate(a.part('Stowage', 'Crate', t), a.part('Kit_straps', 'Rubber', t), (.5, .34, .26), (.35, 1.17, .12),
            bands=1)
    K.net_roll(a.part('Net_roll', 'Canvas', t), a.part('Kit_straps', 'Rubber', t), (-.3, 1.17, .3), length=.75, r=.11,
               axis='X')
    # Roof: commander's cupola (left) with its vision blocks and the panoramic sight, the loader's hatch with the
    # 12.7 mm on its pintle (Mount_mg), the gunner's sight (right front), wind sensor, whips leaning back.
    k.lathe(a.part('Cupola', 'Armor', t), [(.3, .5), (.3, .62), (.27, .66), (0, .67)], loc=(.42, .3, 0), seg=12)
    for i in range(4):
        u = i * TAU / 4 + .4
        _scope(a, (.42 + math.sin(u) * .27, .3 - math.cos(u) * .27, .6), facing=(math.sin(u), -math.cos(u)),
               parent=t, size=(.11, .07, .07))
    a.part('Sight_mast', 'Steel', t).cyl(.05, .16, loc=(.32, -.2, .62), seg=6, bevel=0)
    k.block(a.part('Sight_head', 'Armor', t), (.26, .22, .18), loc=(.32, -.2, .7), chamfer=.02)
    a.part('Glass', 'Glass', t).box((.18, .01, .1), loc=(.32, -.315, .79), bevel=0)
    k.block(a.part('Sight_head', 'Armor', t), (.28, .34, .2), loc=(-.48, -.72, .52), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.2, .01, .1), loc=(-.48, -.895, .62), rot=(-.15, 0, 0), bevel=0)
    a.part('Sight_doors', 'Armor', t).box((.24, .02, .14), loc=(-.48, -.9, .74), rot=(-.6, 0, 0), bevel=0)
    C.hatch(a, (-.42, .38, .56), r=.26, parent=t)
    K.pintle_mg(a, t, (-.68, .3, .56), scale=.82, slot='mg', shield=False, length=1.0, post=.04)
    a.part('Wind_sensor', 'Steel', t).box((.025, .025, .22), loc=(-.2, .85, .66), bevel=0)
    for s in (-1, 1):
        _whip(a, t, (s * .62, .88, .56), .85, 1.22)
    _gun_elevation(a, t)


def _gun_elevation(a, t):
    """The 105 mm on the baked Elevation pivot at its trunnion (ModelLibrary takes a pivot that brings children):
    mantlet, the tube with its bore evacuator and thermal sleeve clamps, the multi-baffle brake (recoils with
    Main_cannon), the coaxial MG beside it."""
    e = a.pivot('Elevation', (0, -.95, .3), t)
    mt = a.part('Mantlet', 'Armor', e)
    k.extrude(mt, [(-.25, -.17), (.25, -.17), (.27, .1), (.18, .19), (-.18, .19), (-.27, .1)], .34,
              loc=(0, -.2, 0), axis='Y', chamfer=.03, corner=.02, taper=.86)
    k.lathe(mt, [(.15, 0), (.15, .1), (.12, .16)], loc=(0, -.37, 0), rot=K.FORWARD, seg=10)
    L = 4.85
    gun = a.part('Main_cannon', 'Steel', e)
    k.lathe(gun, [(.11, .3), (.11, .55), (.095, .62), (.09, 1.9), (.122, 1.95), (.122, 2.5), (.09, 2.56),
                  (.082, L - .05), (.088, L), (0, L)], loc=(0, -.3, 0), rot=K.FORWARD, seg=12, worn=(4, 5))
    for f in (1.2, 3.4):
        k.lathe(gun, [(.1 if f < 1.9 else .092, -.025), (.1 if f < 1.9 else .092, .025)], loc=(0, -.3 - f, 0),
                rot=K.FORWARD, seg=12)
    br = a.part('Muzzle_brake', 'Steel', e)
    y0 = -.3 - L
    k.lathe(br, [(.1, 0), (.12, .02), (.12, .36), (.105, .38), (0, .38)], loc=(0, y0 + .02, 0), rot=K.FORWARD,
            seg=12, worn=(1, 2))
    ports = a.part('Muzzle_brake_ports', 'Undercarriage', e)
    for s in (-1, 1):
        for j in range(3):
            ports.box((.02, .07, .14), loc=(s * .112, y0 - .07 - j * .1, 0), bevel=0)
    a.pivot('Muzzle_main', (0, y0 - .42, 0), e)
    cx = a.part('Coax', 'Undercarriage', e)
    k.lathe(cx, [(.03, 0), (.03, .1), (.018, .12), (.018, .5), (0, .5)], loc=(-.31, -.3, .04), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (-.31, -.81, .04), e)


def wheeled_gun(a):
    """Wheeled tank destroyer (see the module docstring). Runtime: Turret > Elevation (baked trunnion pivot) >
    Main_cannon / Muzzle_brake / Muzzle_main / Coax / Muzzle_coax; Mount_mg / Muzzle_mg on the turret roof;
    Point_fire, Point_exhaust; Part_wheel / Part_wheelb come from mb_p34_parts (Tyres / Wheels / Hubs)."""
    K.suffixed(a)
    _gun_hull(a)
    _gun_running_gear(a)
    _gun_front(a)
    _gun_sides(a)
    _gun_turret(a)
    K.dust(a, (0, 0, .3), radius=3.5, k=.16)
    _merge(a)
    k.clean(a)


# ============================================================================= command_vehicle
V_WR, V_TW, V_TX = .46, .32, .84
V_AXLES = (-1.6, 1.32)
V_ROOF = 1.9
V_W = .97                            # the crew cell's half width at the belt line


def _cell_half(ztop, w=V_W, zb=.62):
    return [(0, zb), (.5, zb + .02), (w - .08, .86), (w, .95), (w, 1.42), (w - .16, ztop - .07), (w - .23, ztop),
            (0, ztop + .01)]


def _arch(a, s, y, x, wr, part='Wheel_arches', mat='Team', w=.2):
    """A flared wheel arch round the wheel at (y, wr): a half-ring plate along X."""
    pts = []
    for i in range(7):
        u = math.pi * i / 6
        pts.append((y + math.cos(u) * (wr + .16), wr + math.sin(u) * (wr + .16)))
    for i in range(6, -1, -1):
        u = math.pi * i / 6
        pts.append((y + math.cos(u) * (wr + .07), wr + math.sin(u) * (wr + .07)))
    k.extrude(a.part(part, mat), pts, w, loc=(s * x, 0, 0), axis='X')


def _cv_body(a):
    # The V-hull crew cell (one armoured capsule from the windscreen to the rear door), the bonnet ahead of it.
    cell = a.part('Hull', 'Team')
    K.section_loft(cell, [
        (-1.34, _cell_half(1.5)),
        (-.9, _cell_half(V_ROOF)),
        (2.3, _cell_half(V_ROOF + .02)),
        (2.59, _cell_half(V_ROOF - .14, w=V_W - .02, zb=.7)),
    ])
    bon = a.part('Bonnet', 'Team')
    K.section_loft(bon, [
        (-2.62, [(0, .7), (.55, .72), (.8, .8), (.84, 1.12), (.74, 1.22), (0, 1.24)]),
        (-2.42, [(0, .62), (.6, .64), (.86, .78), (.9, 1.18), (.78, 1.3), (0, 1.32)]),
        (-1.3, [(0, .62), (.6, .64), (.9, .8), (.92, 1.3), (.8, 1.44), (0, 1.46)]),
    ])
    # Flared arches over the four wheels, the sill boxes between them with the steps.
    for s in (-1, 1):
        for y in V_AXLES:
            _arch(a, s, y, .93, V_WR)
        k.block(a.part('Sills', 'Armor'), (.14, 2.0, .2), loc=(s * .95, -.13, .62), chamfer=.02)
        for y in (-.75, .55):
            a.part('Steps', 'Steel').box((.14, .34, .03), loc=(s * 1.0, y, .55), bevel=0)
    # The windscreen: two thick armoured panes in heavy frames, wipers.
    for s in (-1, 1):
        x0, x1 = s * .05, s * .68
        quad = [(x0, -1.3, 1.53), (x1, -1.3, 1.53), (s * .62, -.93, 1.86), (s * .05, -.93, 1.86)]
        if s < 0:
            quad = [quad[1], quad[0], quad[3], quad[2]]
        K.windscreen(a, quad, frame_mat='Armor', wipers=1, bar=.07)
    # Side windows (two each side, in the sloped upper walls), door seams, handles, hinges.
    gl = a.part('Glass', 'Glass')
    fr = a.part('Window_frames', 'Armor')
    seam = a.part('Door_seams', 'Undercarriage')
    for s in (-1, 1):
        tilt = s * math.atan2(.16, .41)
        for y in (-.5, .55):
            gl.box((.012, .62, .3), loc=(s * (V_W - .07), y, 1.64), rot=(0, tilt, 0), bevel=0)
            fr.box((.02, .7, .05), loc=(s * (V_W - .055), y, 1.47), rot=(0, tilt, 0), bevel=0)
            fr.box((.02, .7, .05), loc=(s * (V_W - .1), y, 1.81), rot=(0, tilt, 0), bevel=0)
        for y in (-.9, .1, 1.1):
            seam.box((.012, .02, .62), loc=(s * (V_W + .005), y, 1.12), bevel=0)
        seam.box((.012, 2.0, .015), loc=(s * (V_W + .005), .1, .82), bevel=0)
        for y in (-.2, .82):
            K.handle(a.part('Kit_handles', 'Steel'), (s * (V_W + .01), y - .08, 1.3), (s * (V_W + .01), y + .08, 1.3),
                     (s, 0, 0), h=.04, r=.012)
        for y in (-.85, .15):
            a.part('Kit_hinges', 'Steel').box((.03, .05, .5), loc=(s * (V_W + .015), y, 1.12), bevel=0)
        K.mirror(a.part('Mirrors', 'Armor'), (s * .95, -1.2, 1.55), s, arm=.08, size=(.06, .03, .2))


def _cv_front(a):
    """Bull bar with the winch, lamps in brush guards, the grille slots, bonnet hinges and louvres, the exhaust."""
    bb = a.part('Bull_bar', 'Armor')
    for s in (-1, 1):
        bb.tube([(s * .7, -2.62, .55), (s * .72, -2.78, .62), (s * .72, -2.78, 1.05), (s * .55, -2.66, 1.18)], .035,
                seg=6)
    bb.tube([(-.72, -2.78, .85), (.72, -2.78, .85)], .035, seg=6)
    k.block(a.part('Bumper', 'Armor'), (1.7, .16, .2), loc=(0, -2.65, .55), chamfer=.03)
    C.cable_reel(a, (0, -2.72, .66), r=.13, w=.36, axis='X')
    for s in (-1, 1):
        _lampk(a, (s * .62, -2.68, 1.0), (0, -1, 0), r=.075, guard=True)
        _lampk(a, (s * .42, -2.66, .62), (0, -1, 0), r=.04, guard=False, glow='Alloy')
        _hook(a, (s * .5, -2.75, .45), facing=-1)
    sl = a.part('Grille_slots', 'Undercarriage')
    for i in range(5):
        sl.box((.9, .02, .035), loc=(0, -2.63, .88 + i * .065), rot=(.2, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Kit_hinges', 'Steel').cyl(.02, .2, loc=(s * .45, -1.36, 1.46), rot=(0, R90, 0), seg=6, bevel=0)
        _grille(a, (s * .5, -1.82, 1.43), .3, .45, facing=(0, 0, 1), slats=4, frame_mat='Armor')
    K.exhaust(a, (-.95, -1.55, .9), r=.045, length=.45, direction=(-.3, .4, 1), muffler=False)
    a.pivot('Point_exhaust', (-1.05, -1.4, 1.4))


def _cv_rear(a):
    """The rear door with the spare wheel, tail lamps, jerrycans, the tow hitch, the roof basket."""
    _door(a, (0, 2.6, .78), size=(1.0, .95), normal=(0, 1, 0), mat='Team', frame_mat='Armor')
    r, w = .42, .26
    sp = dict(loc=(0, 2.76, 1.23), rot=(-R90, 0, 0), seg=18)
    k.lathe(a.part('Spare_tyre', 'Rubber'), [(r * .6, -w / 2), (r * .92, -w / 2), (r, -w * .3), (r, w * .3),
                                             (r * .92, w / 2), (r * .6, w / 2)], worn=(2, 3), **sp)
    k.lathe(a.part('Spare_rim', 'Armor'), [(r * .62, w / 2 - .01), (r * .5, w / 2 - .05), (r * .15, w / 2 - .05),
                                           (r * .12, w / 2 + .02), (0, w / 2 + .02)], **sp)
    a.part('Spare_bracket', 'Steel').box((.5, .06, .08), loc=(0, 2.64, 1.23), bevel=0)
    for s in (-1, 1):
        _lampk(a, (s * .78, 2.61, 1.05), (0, 1, 0), r=.05, guard=False, glow='LavaGlow')
        C.jerry_rack(a, (s * .78, 2.8, .62), count=1, axis='X')
    a.part('Tow_pintle', 'Steel').cyl(.05, .16, loc=(0, 2.7, .5), rot=K.FORWARD, seg=8, bevel=0)
    # The roof basket over the rear with bags, a net roll and a crate.
    rk = a.part('Roof_rack', 'Steel')
    z = V_ROOF + .03
    pts = [(.62, 1.35), (.62, 2.5), (-.62, 2.5), (-.62, 1.35)]
    rk.tube([(x, y, z + .18) for x, y in pts] + [(pts[0][0], pts[0][1], z + .18)], .016, seg=4, caps=False)
    for x, y in pts:
        rk.limb((x, y, z), (x, y, z + .18), .03, .03, bevel=0)
    for y in (1.75, 2.15):
        rk.limb((.62, y, z + .02), (-.62, y, z + .02), .03, .03, bevel=0)
    K.net_roll(a.part('Net_roll', 'Canvas'), a.part('Kit_straps', 'Rubber'), (.2, 2.3, z + .12), length=.9, r=.1,
               axis='X')
    K.backpack(a.part('Bags', 'Canvas'), a.part('Kit_straps', 'Rubber'), (.32, .26, .2), (-.38, 2.0, z + .04))
    K.crate(a.part('Stowage', 'Crate'), a.part('Kit_straps', 'Rubber'), (.4, .3, .18), (.35, 1.8, z + .03), bands=1)
    a.pivot('Point_fire', (0, 1.2, V_ROOF))


def _cv_roof(a):
    """The command fit: SATCOM dome, the folded telescopic mast, tied-down whips, the GPS puck, smoke dischargers,
    the beacon; the remote weapon station (Mount_mg) at the roof's front."""
    z = V_ROOF + .01
    k.lathe(a.part('Satcom_base', 'Armor'), [(.3, 0), (.3, .06), (.27, .08)], loc=(-.35, 1.0, z), seg=16)
    k.lathe(a.part('Satcom', 'Medical'), [(.27, .08), (.26, .16), (.2, .26), (.11, .31), (0, .33)],
            loc=(-.35, 1.0, z), seg=16)
    # The telescopic mast folded along the roof's right edge on its two cradles, the head with the antennas.
    ms = a.part('Masts', 'Steel')
    ms.cyl(.07, 1.9, loc=(-.68, .85, z + .14), rot=K.FORWARD, seg=10, bevel=0)
    ms.cyl(.05, .35, loc=(-.68, -.25, z + .14), rot=K.FORWARD, seg=8, bevel=0)
    for y in (-.1, 1.5):
        a.part('Mast_cradles', 'Armor').box((.2, .1, .14), loc=(-.68, y, z + .06), bevel=0)
    a.part('Mast_hinge', 'Armor').box((.26, .26, .2), loc=(-.68, 1.9, z + .1), bevel=.02)
    k.block(a.part('Mast_head', 'Armor'), (.22, .3, .16), loc=(-.68, -.5, z + .07), chamfer=.02)
    # Whips tied down in arcs from the rear corners to clips at the cab's front corners.
    ant = a.part('Antennas', 'Steel')
    for s in (-1, 1):
        x = s * .8
        k.lathe(ant, [(.05, 0), (.05, .06), (.03, .1), (.03, .2), (0, .21)], loc=(x, 2.38, z), seg=6)
        ant.tube([(x, 2.38, z + .2), (x, 2.2, z + .34), (x, 1.2, z + .4), (x * .97, 0, z + .34),
                  (x * .95, -.8, z + .14)], .014, seg=4)
        a.part('Kit_clips', 'Steel').box((.06, .06, .08), loc=(x * .95, -.82, z + .06), bevel=0)
    for x, y in ((.55, .85), (.1, 2.25)):
        K.whip_antenna(ant, (x, y, z), h=.28, r=.02)
    a.part('Gps', 'Undercarriage').cyl(.07, .04, loc=(.25, .35, z + .02), seg=10, bevel=0)
    for s in (-1, 1):
        _smoke(a, None, (s * .7, -.72, z + .06), s, count=3, yaw=s * .4)
    K.beacon(a, (.68, .8, z), r=.07)
    _cv_rws(a, (0, -.25, z))


def _cv_rws(a, loc):
    """A remote weapon station (Protector-class): ring base, the yawing cradle (Mount_mg) with the 12.7 mm, its
    ammunition box, the sensor head with day / thermal windows on the left."""
    x, y, z = loc
    k.lathe(a.part('Rws_base', 'Armor'), [(.3, 0), (.3, .05), (.26, .08)], loc=loc, seg=16, worn=(1,))
    m = a.pivot('Mount_mg', (x, y, z + .08))
    k.lathe(a.part('Rws_ring', 'Armor', m), [(.25, 0), (.25, .05), (.2, .07)], seg=14)
    body = a.part('Rws_body', 'Team', m)
    k.extrude(body, [(-.22, .05), (.22, .05), (.24, .2), (.16, .26), (-.16, .26), (-.24, .2)], .5,
              loc=(0, .02, 0), axis='Y', chamfer=.02, corner=.02)
    rc = a.part('Rws_gun', 'Undercarriage', m)
    k.block(rc, (.14, .55, .12), loc=(0, -.15, .2), chamfer=.015)
    g = a.part('Rws_barrel', 'Steel', m)
    k.lathe(g, [(.04, 0), (.04, .12), (.026, .16), (.022, .78), (.034, .8), (.034, .9), (0, .9)],
            loc=(0, -.42, .26), rot=K.FORWARD, seg=8, worn=(4,))
    a.pivot('Muzzle_mg', (0, -1.33, .26), m)
    k.block(a.part('Rws_ammo', 'Crate', m), (.12, .34, .22), loc=(-.3, .02, .06), chamfer=.015)
    sh = a.part('Rws_sensor', 'Armor', m)
    k.block(sh, (.16, .26, .2), loc=(.32, -.1, .1), chamfer=.02)
    gl = a.part('Glass', 'Glass', m)
    for dz in (.16, .24):
        gl.box((.1, .01, .05), loc=(.32, -.235, dz), bevel=0)


def command_vehicle(a):
    """4x4 protected command vehicle (see the module docstring). Runtime: Mount_mg / Muzzle_mg (the remote 12.7 mm
    station; the def's main weapon in slot mg, aim Free), Point_fire, Point_exhaust."""
    K.suffixed(a)
    _cv_body(a)
    for y in V_AXLES:
        for s in (-1, 1):
            _wheel(a, (s * V_TX, y, V_WR), V_WR, V_TW, s, seg=18)
            _wishbones(a, s, V_TX, y, V_WR, .55, .95)
    a.part('Driveline', 'Undercarriage').cyl(.05, 2.8, loc=(0, -.14, .5), rot=K.FORWARD, seg=8, bevel=0)
    _cv_front(a)
    _cv_rear(a)
    _cv_roof(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.16)
    _merge(a)
    k.clean(a)


# ============================================================================= ew_jammer
E_WR, E_TW, E_TX = .62, .44, 1.0
E_AXLES = (-3.05, -1.7, 1.25, 2.6)
E_NOSE, E_TAIL = -4.5, 4.45
E_CAB0, E_CAB1 = -4.5, -2.6           # the crew cab
E_VAN0 = -1.9                         # the equipment van's front wall
E_FLOOR = 1.38                        # cab and van floor
E_ROOF = 3.05                         # the van roof


def _cab_half(zbelt, ztop, w=1.24, zb=E_FLOOR):
    return [(0, zb), (w - .1, zb), (w, zb + .1), (w, zbelt), (w - .06, ztop - .12), (w - .18, ztop), (0, ztop + .01)]


def _ew_cab(a):
    cab = a.part('Cab', 'Team')
    K.section_loft(cab, [
        (E_CAB0, _cab_half(1.78, 1.92, w=1.16)),
        (E_CAB0 + .06, _cab_half(1.82, 1.98, w=1.22)),
        (-4.12, _cab_half(1.95, 2.8)),
        (E_CAB1, _cab_half(1.95, 2.86)),
    ])
    # The lower front: valance under the cab with the grille, bumper, lamps, tow hooks, the steps.
    val = a.part('Valance', 'Armor')
    K.section_loft(val, [(E_NOSE - .02, [(0, .8), (1.1, .8), (1.16, .9), (1.16, E_FLOOR + .02), (0, E_FLOOR + .02)]),
                         (E_NOSE + .5, [(0, .8), (1.1, .8), (1.16, .9), (1.16, E_FLOOR + .02), (0, E_FLOOR + .02)])])
    _grille(a, (0, E_NOSE - .04, 1.12), 1.1, .34, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    k.block(a.part('Bumper', 'Steel'), (2.4, .16, .18), loc=(0, E_NOSE - .1, .75), chamfer=.03)
    for s in (-1, 1):
        _lampk(a, (s * .95, E_NOSE - .05, 1.15), (0, -1, 0), r=.09, guard=True)
        _lampk(a, (s * .95, E_NOSE - .05, 1.6), (0, -1, 0), r=.05, guard=False, glow='Alloy')
        _hook(a, (s * .55, E_NOSE - .17, .72), facing=-1)
        for j, z in enumerate((.95, 1.2)):
            a.part('Steps', 'Steel').box((.12, .45, .03), loc=(s * 1.18, -3.75 + .02 * j, z), bevel=0)
    # The windscreen in two panes, side windows in the four doors, door seams, mirrors on long arms.
    for s in (-1, 1):
        quad = [(s * .06, -4.45, 2.0), (s * 1.0, -4.45, 2.0), (s * .98, -4.14, 2.7), (s * .06, -4.14, 2.7)]
        if s < 0:
            quad = [quad[1], quad[0], quad[3], quad[2]]
        K.windscreen(a, quad, frame_mat='Armor', wipers=1, bar=.05)
    a.part('Sun_visor', 'Team').box((2.2, .4, .04), loc=(0, -4.25, 2.86), rot=(-.15, 0, 0), bevel=0)
    gl = a.part('Glass', 'Glass')
    seam = a.part('Door_seams', 'Undercarriage')
    for s in (-1, 1):
        for y, L in ((-3.8, .62), (-3.05, .55)):
            gl.box((.012, L, .5), loc=(s * 1.215, y, 2.28), rot=(0, s * .07, 0), bevel=0)
        for y in (-4.18, -3.42, -2.72):
            seam.box((.012, .02, 1.25), loc=(s * 1.245, y, 1.98), bevel=0)
        for y in (-3.5, -2.8):
            a.part('Kit_handles', 'Steel').limb((s * 1.25, y - .1, 1.85), (s * 1.25, y, 1.85), .03, .03, bevel=0)
        K.mirror(a.part('Mirrors', 'Armor'), (s * 1.2, -4.3, 2.3), s, arm=.06, size=(.07, .03, .3))
        # Mud guards over the front pair (the cab sits above them).
        for y in E_AXLES[:2]:
            K.fender(a.part('Mud_wings', 'Team'), E_TX, y - .75, y + .75, E_WR * 2 + .16, .5, s, lip=.12)
    # Roof: hatch, marker lamps, the self-defence 12.7 mm on its post (Turret: the def's hmg_selfdef_15).
    C.hatch(a, (-.5, -3.2, 2.86), r=.28)
    for x in (-.4, 0, .4):
        a.part('Marker_lamps', 'Alloy').box((.1, .05, .05), loc=(x, -4.32, 2.84), bevel=0)
    C.roof_gun(a, (.5, -3.35, 2.86), pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
               muzzle='Muzzle_main', post=.3, length=1.1, scale=.95, shield=True, mat='Team')


def _ew_chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.16, 8.7, .28), loc=(s * .5, .05, E_FLOOR - .16), bevel=0)
    for y in (-3.6, -.2, 1.9, 4.0):
        fr.box((1.0, .12, .12), loc=(0, y, E_FLOOR - .2), bevel=0)
    for i, y in enumerate(E_AXLES):
        _axle(a, y, E_WR, E_TX - .12)
        for s in (-1, 1):
            _wheel(a, (s * E_TX, y, E_WR), E_WR, E_TW, s, seg=14)
            a.part('Springs', 'Steel').box((.09, 1.0, .1), loc=(s * .55, y, E_WR + .32), bevel=0)
    for y in E_AXLES[2:]:
        for s in (-1, 1):
            K.fender(a.part('Mud_wings', 'Team'), E_TX, y - .75, y + .75, E_WR * 2 + .14, .5, s, lip=.12)
    a.part('Driveline', 'Undercarriage').cyl(.07, 6.0, loc=(0, -.2, .62), rot=K.FORWARD, seg=8, bevel=0)
    # The engine bay behind the cab: a cover with grilles and the twin exhausts at its corners.
    eng = a.part('Engine_cover', 'Team')
    C.slab_loft(eng, C.octagon(2.0, E_VAN0 - E_CAB1 - .1, .12, y0=(E_CAB1 + E_VAN0) / 2),
                C.octagon(1.7, E_VAN0 - E_CAB1 - .2, .12, y0=(E_CAB1 + E_VAN0) / 2), E_FLOOR, 2.55)
    for s in (-1, 1):
        _grille(a, (s * 1.0, (E_CAB1 + E_VAN0) / 2, 1.95), .45, .7, facing=(s, 0, 0), slats=6, frame_mat='Armor')
        a.part('Exhaust', 'Steel').cyl(.07, .7, loc=(s * .95, E_VAN0 - .08, 2.75), seg=8, bevel=0)
        K.soot(a, (s * .95, E_VAN0 - .08, 3.1), radius=.4, k=.45)
    a.pivot('Point_exhaust', (.95, E_VAN0 - .08, 3.2))
    # Fuel tank and battery boxes under the van between the axle pairs, tool lockers, a cable reel.
    for s in (-1, 1):
        C.stowage_box(a, (.36, .7, .38), (s * 1.0, -.95, E_FLOOR - .58), mat='Armor', latches=1)
    k.lathe(a.part('Fuel_tank', 'Armor'), [(.24, -.45), (.27, -.4), (.27, .4), (.24, .45)], loc=(-1.0, -.25, .98),
            rot=K.FORWARD, seg=12)


def _ew_van(a):
    y0, y1 = E_VAN0, E_TAIL
    van = a.part('Body', 'Team')
    half = [(0, E_FLOOR), (1.18, E_FLOOR), (1.26, E_FLOOR + .08), (1.27, E_ROOF - .2), (1.2, E_ROOF - .05),
            (1.05, E_ROOF), (0, E_ROOF + .01)]
    K.section_loft(van, [(y0, [(x * .97, z if z < 2 else z - .05) for x, z in half]), (y0 + .08, half),
                         (y1 - .08, half), (y1, [(x * .97, z if z < 2 else z - .05) for x, z in half])])
    # Panel ribs, side doors, louvres, the A/C units on the front wall, the rear door and ladder.
    rib = a.part('Body_ribs', 'Team')
    for s in (-1, 1):
        for y in (-1.25, .35, 2.0, 4.0):
            rib.box((.03, .06, E_ROOF - E_FLOOR - .3), loc=(s * 1.285, y, (E_ROOF + E_FLOOR) / 2 - .05), bevel=0)
        rib.box((.03, 6.2, .05), loc=(s * 1.285, 1.25, E_FLOOR + .25), bevel=0)
        _grille(a, (s * 1.29, 3.55, 2.05), .7, .5, facing=(s, 0, 0), slats=6, frame_mat='Team')
    _door(a, (1.29, .35, E_FLOOR + .1), size=(.75, 1.35), normal=(1, 0, 0), mat='Team', frame_mat='Armor')
    K.ladder(a.part('Ladders', 'Steel'), (1.31, 1.0, E_FLOOR - .5), (1.31, 1.0, E_ROOF + .05), width=.4, step=.28,
             facing=(1, 0))
    _door(a, (-1.29, -.6, E_FLOOR + .1), size=(.75, 1.35), normal=(-1, 0, 0), mat='Team', frame_mat='Armor')
    for x in (-.6, .6):
        a.part('Air_con', 'Armor').box((.8, .3, .6), loc=(x, E_VAN0 - .14, 2.55), bevel=0)
        a.part('Grilles', 'Undercarriage').box((.6, .02, .4), loc=(x, E_VAN0 - .3, 2.6), bevel=0)
    _door(a, (.3, E_TAIL + .01, E_FLOOR + .1), size=(.8, 1.4), normal=(0, 1, 0), mat='Team', frame_mat='Armor')
    K.ladder(a.part('Ladders', 'Steel'), (-.6, E_TAIL + .06, E_FLOOR - .4), (-.6, E_TAIL + .06, E_ROOF + .05),
             width=.4, step=.28)
    for s in (-1, 1):
        _lampk(a, (s * 1.1, E_TAIL + .02, E_FLOOR - .1), (0, 1, 0), r=.05, guard=False, glow='LavaGlow')
        # Stabiliser jacks at the van's four corners, stowed up, foot pads under them.
        for y in (-.35, 4.0):
            a.part('Jacks', 'Armor').box((.18, .18, .5), loc=(s * 1.12, y, E_FLOOR - .27), bevel=0)
            a.part('Jack_rams', 'Steel').cyl(.05, .3, loc=(s * 1.12, y, E_FLOOR - .64), seg=6, bevel=0)
            a.part('Jack_pads', 'Undercarriage').cyl(.17, .05, loc=(s * 1.12, y, E_FLOOR - .8), seg=6, bevel=0)
    # Roof: walkway plates, rails, the folded telescopic mast (Leer-3 read) with its head, whips, the cable runs.
    wk = a.part('Walkway', 'Armor')
    wk.box((.6, 4.4, .03), loc=(.55, .6, E_ROOF + .02), bevel=0)
    rl = a.part('Railings', 'Steel')
    rl.tube([(1.15, E_VAN0 + .3, E_ROOF + .4), (1.15, 2.0, E_ROOF + .4)], .02, seg=4)
    for y in (E_VAN0 + .3, -.4, .9, 2.0):
        rl.limb((1.15, y, E_ROOF), (1.15, y, E_ROOF + .4), .03, .03, bevel=0)
    ms = a.part('Masts', 'Steel')
    ms.cyl(.12, 3.6, loc=(-.55, .3, E_ROOF + .25), rot=K.FORWARD, seg=10, bevel=0)
    ms.cyl(.09, .9, loc=(-.55, -1.85, E_ROOF + .25), rot=K.FORWARD, seg=10, bevel=0)
    for y in (-1.2, 1.6):
        a.part('Mast_cradles', 'Armor').box((.36, .14, .22), loc=(-.55, y, E_ROOF + .1), bevel=0)
    a.part('Mast_hinge', 'Armor').box((.4, .4, .32), loc=(-.55, 2.0, E_ROOF + .16), bevel=0)
    hd = a.part('Mast_head', 'Armor')
    k.block(hd, (.7, .26, .5), loc=(-.55, -2.35, E_ROOF + .02), chamfer=.03)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (-.55, -2.5, E_ROOF + .3), w=.6, h=.4, normal=(0, -1, 0), bars=2)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.1, 3.9, E_ROOF), h=.75, r=.02)
    a.part('Kit_cables', 'Rubber').tube([(-.2, 1.9, E_ROOF + .02), (-.1, 2.4, E_ROOF + .02), (0, 2.75, E_ROOF + .1)],
                                        .03, seg=5)
    a.pivot('Point_fire', (0, .5, E_ROOF))


def _ew_reflector(a):
    """The Krasukha's reflector: a turntable on the van's rear (`Radar`), the yoke, a curved reflector face
    (a cylindrical-parabolic section) on a ribbed back frame, the feed boom with its horn cluster, the ram."""
    cy = 3.25
    k.lathe(a.part('Radar_base', 'Armor'), [(.7, 0), (.7, .08), (.6, .12), (0, .13)], loc=(0, cy, E_ROOF), seg=12,
            worn=(1,))
    r = a.pivot('Radar', (0, cy, E_ROOF + .13))
    k.lathe(a.part('Radar_turntable', 'Team', r), [(.62, 0), (.62, .1), (.5, .14), (0, .15)], seg=12)
    yk = a.part('Radar_yoke', 'Armor', r)
    for s in (-1, 1):
        k.extrude(yk, [(-.3, .1), (.3, .1), (.12, .48), (-.12, .48)], .1, loc=(s * .55, 0, 0), axis='X', chamfer=.02)
    hinge = Vector((0, 0, .38))
    tilt = math.radians(60)                     # the face leans back, looking up and forward
    rot = Matrix.Rotation(-tilt, 4, 'X')
    w, h, sag = 2.5, 1.15, .3
    cols, rows = 8, 4
    face, verts, back = a.part('Radar_dish', 'MetalSheet', r), [], []
    for j in range(rows + 1):
        for i in range(cols + 1):
            u = i / cols - .5
            v = j / rows - .5
            p = Vector((u * w, sag * (4 * u * u) - .05, v * h))
            verts.append(tuple(hinge + rot @ p))
            back.append(tuple(hinge + rot @ (p + Vector((0, .06, 0)))))
    faces = []
    for j in range(rows):
        for i in range(cols):
            q = j * (cols + 1) + i
            faces.append((q, q + cols + 1, q + cols + 2, q + 1))
    n = len(verts)
    face.mesh(verts + back, faces + [tuple(n + x for x in reversed(f)) for f in faces])
    rim = a.part('Radar_ribs', 'Armor', r)
    for i in range(0, cols + 1, 4):
        rim.tube([back[j * (cols + 1) + i] for j in range(rows + 1)], .04, seg=4)
    rim.tube([back[(rows // 2) * (cols + 1) + i] for i in range(cols + 1)], .035, seg=4)
    # The face's edge frame and the radiating grid (darker strips just proud of the face).
    outline = [verts[i] for i in range(cols + 1)] + [verts[j * (cols + 1) + cols] for j in range(1, rows + 1)] + \
        [verts[rows * (cols + 1) + i] for i in range(cols - 1, -1, -1)] + [verts[j * (cols + 1)] for j in range(rows - 1, 0, -1)]
    a.part('Radar_frame', 'Team', r).tube(outline + [outline[0]], .045, seg=4, caps=False)
    grid = a.part('Radar_grid', 'Undercarriage', r)
    lift = rot @ Vector((0, -.012, 0))
    for i in range(2, cols, 2):
        grid.tube([tuple(Vector(verts[j * (cols + 1) + i]) + lift) for j in range(rows + 1)], .014, seg=3)
    for j in (2,):
        grid.tube([tuple(Vector(verts[j * (cols + 1) + i]) + lift) for i in range(cols + 1)], .012, seg=3)
    # Trunnions on the yoke, the elevating ram from the turntable to the frame's back.
    for s in (-1, 1):
        a.part('Radar_trunnions', 'Steel', r).cyl(.09, .14, loc=(s * .55, 0, .38), rot=(0, R90, 0), seg=10, bevel=0)
    a.part('Radar_ram', 'Steel', r).limb((0, .45, .1), tuple(hinge + rot @ Vector((0, .1, -.2))), .08, .08, bevel=0)
    # The feed boom out of the face's lower edge to the horn cluster at the focus.
    root = hinge + rot @ Vector((0, -.05, -.55))
    tip = hinge + rot @ Vector((0, -.55, -.05))
    a.part('Radar_feed', 'Steel', r).limb(tuple(root), tuple(tip), .06, .06, bevel=0)
    for s in (-1, 1):
        a.part('Radar_feed', 'Steel', r).limb(tuple(hinge + rot @ Vector((s * .9, -.02, -.52))), tuple(tip), .03, .03,
                                              bevel=0)
    hc = a.part('Radar_horns', 'Undercarriage', r)
    for dx in (-.14, .14):
        for dz in (-.1, .1):
            k.extrude(hc, [(-.06, -.05), (.06, -.05), (.1, .08), (-.1, .08)], .22,
                      loc=tuple(tip + rot @ Vector((dx, .05, dz))), rot=(-tilt - R90, 0, 0), axis='Z', chamfer=0)
    k.block(a.part('Radar_box', 'Team', r), (.6, .4, .35), loc=(0, .65, .14), chamfer=.03)


def ew_jammer(a):
    """The Krasukha-4 read (see the module docstring). Runtime: Turret / Main_cannon / Muzzle_brake / Muzzle_main
    (the cab-roof 12.7 mm, the def's hmg_selfdef_15), Radar (the reflector's turntable), Point_exhaust, Point_fire."""
    K.suffixed(a)
    _ew_cab(a)
    _ew_chassis(a)
    _ew_van(a)
    _ew_reflector(a)
    K.dust(a, (0, 0, .3), radius=4.2, k=.15)
    _merge(a)
    k.clean(a)


# ============================================================================= iron_beam
I_WR, I_TW, I_TX = .5, .36, .79
I_AXLES = (-2.85, -1.6, 1.4, 2.65)
I_NOSE, I_TAIL = -4.1, 4.12
I_FLOOR = 1.12
I_CAB1 = -2.45
I_MOD0 = -2.3                         # the laser module's front wall
I_TOP = 2.2                           # the module roof


def _ib_cab(a):
    cab = a.part('Cab', 'Team')
    K.section_loft(cab, [
        (I_NOSE, _cab_half(1.55, 1.68, w=.92, zb=I_FLOOR - .05)),
        (I_NOSE + .06, _cab_half(1.6, 1.75, w=.98, zb=I_FLOOR - .05)),
        (-3.72, _cab_half(1.62, 2.42, w=.98, zb=I_FLOOR - .05)),
        (I_CAB1, _cab_half(1.62, 2.46, w=.98, zb=I_FLOOR - .05)),
    ])
    val = a.part('Valance', 'Armor')
    K.section_loft(val, [(I_NOSE - .02, [(0, .62), (.85, .62), (.92, .7), (.92, I_FLOOR), (0, I_FLOOR)]),
                         (I_NOSE + .45, [(0, .62), (.85, .62), (.92, .7), (.92, I_FLOOR), (0, I_FLOOR)])])
    _grille(a, (0, I_NOSE - .04, .88), .9, .3, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    k.block(a.part('Bumper', 'Steel'), (1.95, .14, .16), loc=(0, I_NOSE - .08, .6), chamfer=.03)
    for s in (-1, 1):
        _lampk(a, (s * .74, I_NOSE - .05, .9), (0, -1, 0), r=.08, guard=True)
        _lampk(a, (s * .74, I_NOSE - .02, 1.35), (0, -1, 0), r=.045, guard=False, glow='Alloy')
        _hook(a, (s * .45, I_NOSE - .15, .58), facing=-1)
        for j, z in enumerate((.72, .95)):
            a.part('Steps', 'Steel').box((.1, .4, .03), loc=(s * .94, -3.35, z), bevel=0)
        quad = [(s * .05, I_NOSE + .04, 1.72), (s * .84, I_NOSE + .04, 1.72), (s * .82, -3.75, 2.36),
                (s * .05, -3.75, 2.36)]
        if s < 0:
            quad = [quad[1], quad[0], quad[3], quad[2]]
        K.windscreen(a, quad, frame_mat='Armor', wipers=1, bar=.05)
        a.part('Glass', 'Glass').box((.012, .7, .42), loc=(s * .955, -3.15, 1.98), rot=(0, s * .07, 0), bevel=0)
        a.part('Door_seams', 'Undercarriage').box((.012, .02, 1.15), loc=(s * .985, -3.6, 1.62), bevel=0)
        a.part('Door_seams', 'Undercarriage').box((.012, .02, 1.15), loc=(s * .985, -2.6, 1.62), bevel=0)
        a.part('Kit_handles', 'Steel').limb((s * .99, -2.85, 1.55), (s * .99, -2.75, 1.55), .03, .03, bevel=0)
        K.mirror(a.part('Mirrors', 'Armor'), (s * .96, -3.95, 2.0), s, arm=.06, size=(.06, .03, .26))
        for y in I_AXLES[:2]:
            K.fender(a.part('Mud_wings', 'Team'), I_TX, y - .62, y + .62, I_WR * 2 + .12, .44, s, lip=.1)
    a.part('Sun_visor', 'Team').box((1.75, .3, .04), loc=(0, -3.88, 2.47), rot=(-.15, 0, 0), bevel=0)
    C.hatch(a, (.4, -3.0, 2.46), r=.25)
    for x in (-.3, 0, .3):
        a.part('Marker_lamps', 'Alloy').box((.09, .05, .05), loc=(x, -3.98, 2.45), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.75, -2.65, 2.46), h=.5, r=.02)


def _ib_chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.15, 8.0, .26), loc=(s * .45, 0, I_FLOOR - .15), bevel=0)
    for i, y in enumerate(I_AXLES):
        _axle(a, y, I_WR, I_TX - .12)
        for s in (-1, 1):
            _wheel(a, (s * I_TX, y, I_WR), I_WR, I_TW, s, seg=14)
            a.part('Springs', 'Steel').box((.08, .9, .1), loc=(s * .48, y, I_WR + .3), bevel=0)
    for y in I_AXLES[2:]:
        for s in (-1, 1):
            K.fender(a.part('Mud_wings', 'Team'), I_TX, y - .62, y + .62, I_WR * 2 + .1, .44, s, lip=.1)
    a.part('Driveline', 'Undercarriage').cyl(.06, 5.6, loc=(0, -.1, .52), rot=K.FORWARD, seg=8, bevel=0)
    for s in (-1, 1):
        C.stowage_box(a, (.3, .75, .32), (s * .82, -.1, I_FLOOR - .5), mat='Armor', latches=2)
    k.lathe(a.part('Fuel_tank', 'Armor'), [(.2, -.4), (.23, -.35), (.23, .35), (.2, .4)], loc=(-.82, .65, .78),
            rot=K.FORWARD, seg=12)
    _wheel(a, (.82, .75, .78), .38, .28, 1, seg=14, tyre='Spare_tyre', rim='Spare_rim')


def _ib_module(a):
    """The laser module: power unit (front), thermal management (middle, the chiller fans on the roof), the beam
    director's well (rear). Ribbed side doors, louvres, cable trays, jacks, rear ladder and lamps."""
    y0, y1 = I_MOD0, I_TAIL
    half = [(0, I_FLOOR), (.94, I_FLOOR), (1.0, I_FLOOR + .06), (1.0, I_TOP - .14), (.94, I_TOP - .03),
            (.84, I_TOP), (0, I_TOP + .01)]
    K.section_loft(a.part('Body', 'Team'), [(y0, [(x * .97, z if z < 1.6 else z - .04) for x, z in half]),
                                            (y0 + .06, half), (y1 - .06, half),
                                            (y1, [(x * .97, z if z < 1.6 else z - .04) for x, z in half])])
    rib = a.part('Body_ribs', 'Team')
    seam = a.part('Door_seams', 'Undercarriage')
    for s in (-1, 1):
        for y in (-1.6, -.5, .6, 1.7, 2.8, 3.7):
            rib.box((.03, .05, I_TOP - I_FLOOR - .25), loc=(s * 1.012, y, (I_TOP + I_FLOOR) / 2), bevel=0)
        # Side doors of the power and thermal bays, their handles, the louvres.
        for y in (-1.05, .05):
            seam.box((.012, .9, .015), loc=(s * 1.006, y, I_TOP - .2), bevel=0)
            seam.box((.012, .9, .015), loc=(s * 1.006, y, I_FLOOR + .15), bevel=0)
            a.part('Kit_handles', 'Steel').limb((s * 1.02, y + .25, 1.6), (s * 1.02, y + .38, 1.6), .03, .03, bevel=0)
        _grille(a, (s * 1.02, 1.15, 1.7), .8, .45, facing=(s, 0, 0), slats=6, frame_mat='Team')
        _grille(a, (s * 1.02, -1.6, 1.45), .5, .35, facing=(s, 0, 0), slats=4, frame_mat='Team')
        # Cable trays along the roof edges, the stowed jacks.
        a.part('Cable_trays', 'Armor').box((.12, 5.0, .06), loc=(s * .78, .55, I_TOP + .03), bevel=0)
        for y in (-.3, 3.85):
            a.part('Jacks', 'Armor').box((.16, .16, .45), loc=(s * .9, y, I_FLOOR - .25), bevel=0)
            a.part('Jack_pads', 'Undercarriage').cyl(.14, .05, loc=(s * .9, y, I_FLOOR - .52), seg=6, bevel=0)
    # The power unit's exhaust out of the front wall's top, the generator air intake.
    K.exhaust(a, (-.75, I_MOD0 - .06, 1.9), r=.06, length=.55, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (-.75, I_MOD0 - .06, 2.55))
    # The chiller's two big fans on the roof (housings, grilles, hubs).
    for y in (.2, 1.25):
        k.lathe(a.part('Fan_housings', 'Armor'), [(.4, 0), (.4, .1), (.36, .12), (.3, .12), (.3, .05)],
                loc=(0, y, I_TOP), seg=12)
        a.part('Fan_grilles', 'Undercarriage').cyl(.3, .02, loc=(0, y, I_TOP + .06), seg=12, bevel=0)
        fg = a.part('Fan_guards', 'Steel')
        for i in range(3):
            u = i * TAU / 6
            fg.box((.6, .02, .02), loc=(0, y, I_TOP + .11), rot=(0, 0, u), bevel=0)
        fg.cyl(.07, .04, loc=(0, y, I_TOP + .11), seg=8, bevel=0)
    # Rear wall: door, ladder, lamps, the tow pintle.
    _door(a, (.35, I_TAIL + .01, I_FLOOR + .05), size=(.6, .9), normal=(0, 1, 0), mat='Team', frame_mat='Armor')
    K.ladder(a.part('Ladders', 'Steel'), (-.55, I_TAIL + .05, I_FLOOR - .4), (-.55, I_TAIL + .05, I_TOP + .05),
             width=.36, step=.27, facing=(0, 1))
    for s in (-1, 1):
        _lampk(a, (s * .85, I_TAIL + .02, I_FLOOR - .08), (0, 1, 0), r=.045, guard=False, glow='LavaGlow')
    a.part('Tow_pintle', 'Steel').cyl(.05, .14, loc=(0, I_TAIL + .07, .62), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Point_fire', (0, .7, I_TOP))
    # The search radar: a flat-panel face on a short mast at the module's front (spins: `Radar`).
    a.part('Radar_mast', 'Steel').cyl(.08, .22, loc=(.45, -1.85, I_TOP + .11), seg=10, bevel=0)
    k.lathe(a.part('Radar_plinth', 'Armor'), [(.18, 0), (.18, .06), (.12, .08)], loc=(.45, -1.85, I_TOP), seg=12)
    r = a.pivot('Radar', (.45, -1.85, I_TOP + .22))
    k.block(a.part('Radar_panel', 'Armor', r), (.82, .16, .48), loc=(0, 0, .02), rot=(-.25, 0, 0), chamfer=.02)
    a.part('Radar_face', 'Undercarriage', r).box((.74, .02, .4), loc=(0, -.09, .26), rot=(-.25, 0, 0), bevel=0)
    rf = a.part('Radar_tiles', 'Steel', r)
    for i in range(4):
        rf.box((.012, .025, .38), loc=(-.27 + i * .18, -.1, .26), rot=(-.25, 0, 0), bevel=0)
    a.part('Radar_cooling', 'Armor', r).box((.5, .1, .2), loc=(0, .12, .12), rot=(-.25, 0, 0), bevel=0)
    # The electro-optical tracker on its own post beside the radar.
    a.part('Tracker_post', 'Steel').cyl(.05, .3, loc=(-.5, -1.8, I_TOP + .15), seg=8, bevel=0)
    k.block(a.part('Tracker', 'Armor'), (.3, .36, .26), loc=(-.5, -1.8, I_TOP + .3), chamfer=.03)
    a.part('Glass', 'Glass').box((.22, .01, .14), loc=(-.5, -1.985, I_TOP + .43), bevel=0)


def _ib_director(a):
    """The beam director (`Turret`, Mount_APS): a ring base, the yoke, the telescope (`Main_cannon`) with its
    sunshade and bezel (`Main_cannon_bezel`) round the glowing aperture (`Main_cannon_lens`, `Muzzle_main` at its
    centre), on the baked Elevation pivot at the trunnions; the fine tracker on the yoke."""
    k.lathe(a.part('Turret_ring', 'Armor'), [(.62, 0), (.62, .08), (.56, .1)], loc=(0, 2.75, I_TOP), seg=14,
            worn=(1,))
    t = a.pivot('Turret', (0, 2.75, I_TOP + .06))
    a.pivot('Mount_APS', (0, 0, .4), t)
    k.lathe(a.part('Turret_body', 'Team', t), [(.58, 0), (.58, .1), (.48, .2), (.44, .22)], seg=14, worn=(1,))
    yk = a.part('Turret_armor', 'Team', t)
    for s in (-1, 1):
        k.extrude(yk, [(-.32, .12), (.32, .12), (.2, .56), (-.2, .56)], .12, loc=(s * .52, 0, 0), axis='X')
        a.part('Turret_steel', 'Steel', t).cyl(.1, .1, loc=(s * .6, 0, .44), rot=(0, R90, 0), seg=10, bevel=0)
    k.block(a.part('Turret_cooling', 'Armor', t), (.62, .36, .22), loc=(0, .4, .2), chamfer=.03)
    a.part('Kit_cables', 'Rubber', t).tube([(.3, .5, .3), (.42, .3, .45), (.5, .05, .52)], .03, seg=5)
    e = a.pivot('Elevation', (0, 0, .44), t)
    tel = a.part('Main_cannon', 'Team', e)
    k.lathe(tel, [(.2, .5), (.28, .48), (.32, .4), (.32, -.3), (.35, -.34), (.35, -.46), (.31, -.5)],
            rot=(-R90, 0, 0), seg=16, worn=(4,))
    k.lathe(a.part('Main_cannon', 'Team', e), [(.36, -.46), (.38, -.5), (.38, -.7), (.36, -.72), (.31, -.72),
                                                (.31, -.5)], rot=(-R90, 0, 0), seg=16)
    k.lathe(a.part('Main_cannon_bezel', 'Steel', e), [(.31, -.5), (.27, -.53), (.27, -.58), (.31, -.6)],
            rot=(-R90, 0, 0), seg=16, caps=(False, False))
    a.part('Main_cannon_lens', 'Energy', e).cyl(.27, .02, loc=(0, -.53, 0), rot=(-R90, 0, 0), seg=16, bevel=0)
    for f in (-.1, .2):
        k.lathe(a.part('Main_cannon_bands', 'Armor', e), [(.335, -.025), (.335, .025)], loc=(0, f, 0),
                rot=(-R90, 0, 0), seg=16, caps=(False, False))
    a.pivot('Muzzle_main', (0, -.56, 0), e)
    # The fine tracker and illuminator pods on the telescope's flanks.
    for s, L in ((1, .5), (-1, .4)):
        k.lathe(a.part('Tracker_pods', 'Armor', e), [(.1, -.25), (.1, L - .25), (.08, L - .22), (0, L - .22)],
                loc=(s * .42, -.1, .12), rot=(-R90, 0, 0), seg=10)
        a.part('Glass', 'Glass', e).cyl(.075, .01, loc=(s * .42, -.36, .12), rot=K.FORWARD, seg=10,
                                        bevel=0)


def iron_beam(a):
    """Laser air defence (see the module docstring). Runtime: Turret > Elevation (baked) > Main_cannon /
    Main_cannon_bezel / Main_cannon_lens / Muzzle_main, Mount_APS, Radar, Point_exhaust, Point_fire; Part_wheel /
    Part_wheelb come from mb_p34_parts (Tyres / Wheels / Hubs)."""
    K.suffixed(a)
    _ib_cab(a)
    _ib_chassis(a)
    _ib_module(a)
    _ib_director(a)
    K.dust(a, (0, 0, .3), radius=4.0, k=.15)
    _merge(a)
    k.clean(a)


# ============================================================================= stealth_naval_strike
J_APEX, J_TE = -4.2, 4.15            # the planform's nose apex and the straight trailing edge
J_TIP, J_TIP_LE = 9.8, 3.45           # the clipped tips' span position and their leading edge
# Spanwise stations |x| and the section's thickness there (a 10 % section at the root, thinning to the tips).
J_STATIONS = ((0.0, .86), (.9, .72), (2.0, .46), (3.6, .3), (6.0, .2), (8.2, .13), (J_TIP, .08))
J_UP = .62                            # the share of the thickness above the chord plane (a cambered section)
J_U = (0, .015, .05, .12, .22, .35, .5, .65, .8, .92, 1.0)


def _le(x):
    return J_APEX + (J_TIP_LE - J_APEX) * min(1.0, abs(x) / J_TIP)


def _foil(u):
    """The NACA four-digit thickness form, 1.0 at its thickest (30 % chord)."""
    u = min(max(u, 0.0), 1.0)
    return (.2969 * math.sqrt(u) - .126 * u - .3516 * u * u + .2843 * u ** 3 - .1015 * u ** 4) / .1


def _thick(x):
    ax = min(abs(x), J_TIP)
    for (x0, t0), (x1, t1) in zip(J_STATIONS, J_STATIONS[1:]):
        if ax <= x1:
            return t0 + (t1 - t0) * (ax - x0) / (x1 - x0)
    return J_STATIONS[-1][1]


def _skin_z(x, y, upper=True):
    """The wing skin's height at (x, y) (upper or lower surface), for parts laid on it."""
    le = _le(x)
    u = (y - le) / max(J_TE - le, 1e-3)
    t = _thick(x)
    return (J_UP if upper else -(1 - J_UP)) * t * _foil(u) + (.006 if upper else -.006)


def _ribbon(part, p0, p1, width, upper=True, off=.006, n=8, thick=.01):
    """A thin strip laid on the skin from p0 to p1 (x, y), `width` wide: seams, hinge lines, RAM bands."""
    p0, p1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = (p1 - p0).normalized()
    side = Vector((-d.y, d.x, 0)) * width / 2
    sg = 1 if upper else -1
    rows = []
    for i in range(n + 1):
        c = p0.lerp(p1, i / n)
        row = []
        for q in (c - side, c + side):
            z = _skin_z(q.x, q.y, upper) + sg * off
            row.append((q.x, q.y, z))
        rows.append(row)
    verts, faces = [], []
    for r in rows:
        verts += [r[0], r[1], (r[0][0], r[0][1], r[0][2] - sg * thick), (r[1][0], r[1][1], r[1][2] - sg * thick)]
    for i in range(n):
        a, b = 4 * i, 4 * (i + 1)
        faces += [(a, a + 1, b + 1, b), (a + 2, b + 2, b + 3, a + 3), (a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1)]
    e = 4 * n
    faces += [(0, 2, 3, 1), (e, e + 1, e + 3, e + 2)]
    _closed(part, verts, faces)


def _closed(part, verts, faces):
    """Add a closed solid (verts, faces) to the part and turn its faces outward."""
    import bmesh
    bm = part.bm
    vs = [bm.verts.new(v) for v in verts]
    new = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=new)


def _patch(part, poly, upper=True, off=.008, thick=.012, step=.35):
    """A thin plate laid on the skin through the outline `poly` [(x, y), ...] (star-shaped round its centre):
    sawtooth doors and access panels. Edges are split every `step` so the plate follows the skin."""
    pts = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        L = math.hypot(bx - ax, by - ay)
        n = max(1, int(L / step))
        for i in range(n):
            pts.append((ax + (bx - ax) * i / n, ay + (by - ay) * i / n))
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    sg = 1 if upper else -1
    top = [(x, y, _skin_z(x, y, upper) + sg * off) for x, y in pts]
    low = [(x, y, z - sg * thick) for x, y, z in top]
    verts = [(cx, cy, _skin_z(cx, cy, upper) + sg * off)] + top + low
    m = len(pts)
    verts.append((cx, cy, verts[0][2] - sg * thick))
    faces = []
    for i in range(m):
        j = (i + 1) % m
        faces.append((0, 1 + i, 1 + j))
        faces.append((1 + i, 1 + m + i, 1 + m + j, 1 + j))
        faces.append((2 * m + 1, 1 + m + j, 1 + m + i))
    _closed(part, verts, faces)


def _saw(x0, x1, y0, y1, teeth=2, depth=.18):
    """A sawtooth-ended rectangle (stealth door): the front and rear edges zig-zag `teeth` times."""
    pts = []
    for i in range(teeth * 2 + 1):
        f = i / (teeth * 2)
        pts.append((x0 + (x1 - x0) * f, y0 + (depth if i % 2 else 0)))
    for i in range(teeth * 2, -1, -1):
        f = i / (teeth * 2)
        pts.append((x0 + (x1 - x0) * f, y1 - (depth if i % 2 else 0)))
    return pts


def _jet_wing(a):
    """The flying wing: one loft of airfoil sections from tip to tip (the root sections are the centre body's
    lower half), the dark RAM leading edge and trailing edge, elevon hinges, the wing-fold seams."""
    xs = [-J_TIP, -8.2, -6.0, -3.6, -2.0, -.9, 0, .9, 2.0, 3.6, 6.0, 8.2, J_TIP]
    rings = []
    for x in xs:
        le, t = _le(x), _thick(x)
        c = J_TE - le
        up = [(x, le + c * u, J_UP * t * _foil(u) + (.006 if u >= 1 else 0)) for u in J_U]
        lo = [(x, le + c * u, -(1 - J_UP) * t * _foil(u) - .006) for u in reversed(J_U[1:])]
        rings.append(up + lo)
    a.part('Wing', 'Team').loft(rings)
    edge = a.part('Wing_edges', 'Armor')
    for s in (-1, 1):
        lead = [(s * f * J_TIP, _le(f * J_TIP), 0.0) for f in (0.0, .1, .25, .45, .7, 1.0)]
        edge.tube([(x, y - .015, z) for x, y, z in lead], .045, seg=6)
        edge.tube([(s * J_TIP, J_TIP_LE, 0), (s * J_TIP, J_TE, 0)], .035, seg=4)
        # The RAM band behind the leading edge (upper skin), darker than the Team skin.
        _ribbon(edge, (s * .6, _le(.6) + .2), (s * (J_TIP - .4), _le(J_TIP - .4) + .2), .26, n=12)
    edge.tube([(-J_TIP, J_TE, 0), (J_TIP, J_TE, 0)], .03, seg=4)
    seam = a.part('Skin_seams', 'Undercarriage')
    for s in (-1, 1):
        # Elevons: two each side behind a hinge line, the gaps between them; the wing-fold line outboard.
        hinge = J_TE - .62
        _ribbon(seam, (s * 2.3, hinge), (s * 9.2, hinge), .035, n=10)
        for x0, x1 in ((2.35, 5.65), (5.75, 9.15)):
            _patch(a.part('Tail_elevons', 'Armor'), [(s * x0, hinge + .04), (s * x1, hinge + .04), (s * x1, J_TE - .04),
                                                (s * x0, J_TE - .04)][::s], off=.004, thick=.008)
        # Static dischargers on the elevons' trailing edges.
        for x in (4.0, 7.5, 9.0):
            a.part('Dischargers', 'Steel').limb((s * x, J_TE - .02, 0), (s * x, J_TE + .12, 0), .02, .02, bevel=0)
        for x in (2.3, 5.7, 9.2):
            _ribbon(seam, (s * x, hinge), (s * x, J_TE - .02), .03, n=2)
        _ribbon(seam, (s * 6.15, _le(6.15) + .05), (s * 6.15, hinge), .035, n=6)
        a.part('Fold_hinges', 'Steel').tube([(s * 6.15, _le(6.15) + .4, _skin_z(6.15, _le(6.15) + .4) + .01),
                                             (s * 6.15, hinge - .1, _skin_z(6.15, hinge - .1) + .01)], .025, seg=5)
        # Wingtip navigation lights (red left, green right), formation strips.
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .3, .05),
                                                                           loc=(s * (J_TIP + .03), J_TIP_LE + .25, 0),
                                                                           bevel=0)
        _ribbon(a.part('Formation_lights', 'SignalGreen'), (s * 7.2, _le(7.2) + .55), (s * 7.6, _le(7.6) + .55),
                .05, n=2)


def _jet_body(a):
    """The blended centre body over the crew and the bays, the tandem canopy, the over-wing exhaust troughs,
    the refuelling probe fairing (right), the anti-collision beacon, blade antennas."""
    st = [(-3.98, .18, .12), (-3.5, .66, .46), (-2.9, 1.15, .68), (-2.0, 1.5, .75), (-1.0, 1.7, .73),
          (.5, 1.75, .62), (2.0, 1.55, .44), (3.2, 1.2, .26), (3.95, .9, .1)]
    rings = []
    for y, w, h in st:
        rings.append((y, [(0, 0), (w, 0), (w * .85, h * .2), (w * .66, h * .5), (w * .42, h * .8), (w * .2, h * .96),
                          (0, h)]))
    K.section_loft(a.part('Fuselage', 'Team'), rings)
    # Canopy: the tandem two-seat bubble, its frames (sill, the bow between the seats, the windscreen arch).
    can = [(-3.2, .02, .6, .62), (-2.9, .22, .62, .8), (-2.35, .32, .66, .92), (-1.7, .32, .68, .92),
           (-1.3, .24, .68, .86), (-1.12, .02, .68, .7)]
    K.section_loft(a.part('Canopy', 'Glass'), [(y, [(0, b), (w, b), (w * .9, (b + h) / 2 + .03), (w * .55, h - .015),
                                                       (0, h)]) for y, w, b, h in can])
    fr = a.part('Canopy_frames', 'Armor')
    for y, w, h in ((-2.82, .24, .82), (-2.0, .325, .925)):
        fr.tube([(-w, y, .66), (-w * .7, y, h - .05), (0, y, h + .012), (w * .7, y, h - .05), (w, y, .66)], .025,
                seg=4)
    for s in (-1, 1):
        fr.tube([(s * .22, -2.9, .63), (s * .325, -2.3, .68), (s * .32, -1.5, .69), (s * .22, -1.25, .69)], .022,
                seg=4)
    # The exhaust troughs over the trailing edge: dark channels, lips, the glowing slot nozzles.
    tr = a.part('Exhaust_trough', 'Undercarriage')
    for s in (-1, 1):
        _patch(tr, [(s * .7, 2.55), (s * 1.55, 2.75), (s * 1.6, J_TE - .05), (s * .65, J_TE - .05)], off=.01,
               thick=.02)
        for x in (.68, 1.57):
            a.part('Exhaust_lips', 'Armor').tube([(s * x, 2.6, _skin_z(x, 2.6) + .06),
                                                  (s * x, J_TE - .05, _skin_z(x, J_TE) + .04)], .03, seg=4)
        zs = _skin_z(1.1, 2.68) + .07
        a.part('Exhaust_glow', 'Alloy').box((.78, .03, .09), loc=(s * 1.11, 2.66, zs), rot=(0, 0, s * -.12),
                                            bevel=0)
        a.part('Exhaust_hood', 'Team').box((.9, .22, .06), loc=(s * 1.11, 2.56, zs + .05), rot=(-.25, 0, s * -.12),
                                           bevel=0)
    a.pivot('Point_exhaust', (1.1, 3.9, .15))
    a.pivot('Point_fire', (0, .3, .6))
    # Sawtooth access panels and the refuelling receptacle on the upper skin.
    pn = a.part('Skin_panels', 'Team')
    for s in (-1, 1):
        _patch(pn, [(s * x, y) for x, y in _saw(1.35, 2.3, -.9, .7, teeth=2, depth=.16)])
        _patch(pn, [(s * x, y) for x, y in _saw(2.6, 3.4, .4, 1.5, teeth=1, depth=.14)])
        # Outboard access panels in two rows, smaller towards the tips, each with sawtooth ends.
        for x0, x1, dy, h in ((3.0, 3.9, .5, .7), (4.2, 5.0, .45, .6), (5.4, 5.95, .4, .5), (6.45, 7.2, .35, .45),
                              (7.6, 8.3, .3, .35), (3.7, 4.6, 1.6, .8), (5.0, 5.9, 1.3, .7), (6.5, 7.3, 1.0, .5),
                              (2.2, 3.0, 2.6, .55), (7.9, 8.7, .85, .35)):
            y0 = _le(x1) + dy
            _patch(pn, [(s * x, y) for x, y in _saw(x0, x1, y0, y0 + h, teeth=1, depth=.1)])
        # Small flush vents, drains and lights on the upper skin.
        vt = a.part('Skin_vents', 'Armor')
        for x, dy in ((1.5, 1.2), (2.2, 2.8), (3.2, 2.6), (4.4, 2.0), (5.3, 2.3), (8.6, .5), (2.8, 3.6), (1.9, .5),
                      (3.5, .3), (4.8, .25), (6.0, 1.9), (6.9, 1.6), (7.8, 1.0), (9.0, .3), (2.4, 1.9), (3.9, 3.1),
                      (5.6, 2.9), (7.2, 2.3), (1.7, 3.3), (4.1, 1.15), (6.3, .7), (8.0, 1.6), (9.3, .2)):
            y = _le(x) + dy
            _patch(vt, [(s * (x - .1), y - .06), (s * (x + .1), y - .06), (s * (x + .1), y + .06), (s * (x - .1), y + .06)],
                   off=.004, thick=.008, step=1.0)
    # The refuelling probe's fairing on the nose's right (retracted probe tip showing) - an asymmetric detail.
    a.part('Probe_fairing', 'Team').box((.16, .9, .1), loc=(-.55, -3.2, _skin_z(.55, -3.2) + .03),
                                        rot=(-.12, 0, -.05), bevel=.03)
    a.part('Probe', 'Steel').limb((-.55, -3.6, _skin_z(.55, -3.6) + .07), (-.56, -3.95, _skin_z(.56, -3.95) + .07),
                                  .04, .04, bevel=0)
    k.lathe(a.part('Beacons', 'LavaGlow'), [(.05, 0), (.05, .03), (0, .06)], loc=(0, -.4, .7), seg=8)
    ant = a.part('Antennas', 'Armor')
    K.blade_antenna(ant, (0, 1.4, .5), h=.14, chord=.18)
    K.blade_antenna(ant, (.25, -.6, -.36), h=.12, chord=.15, normal=(0, 0, -1))


def _jet_under(a):
    """Underneath: the buried intakes behind the leading edge, the bays with the two guided bombs half sunk in
    them (`Bombs`, `Muzzle_missile` between them), sawtooth bay and gear doors, the standoff missiles on their
    pylons (`Muzzle_rocket` / .001), flush flare dispensers, the arrestor hook."""
    for s in (-1, 1):
        x = 1.2
        y = _le(x) + .45
        z = _skin_z(x, y, False)
        k.extrude(a.part('Intakes', 'Team', None), [(-.38, 0), (.38, 0), (.3, .16), (-.3, .16)], 1.2,
                  loc=(s * x, y + .45, z - .14), axis='Y', chamfer=.03, taper=(.9, .5))
        a.part('Intake_mouths', 'Undercarriage').box((.6, .02, .11), loc=(s * x, y - .16, z - .07), bevel=0)
    bays = a.part('Bay_doors', 'Armor')
    dark = a.part('Bay_wells', 'Undercarriage')
    for s in (-1, 1):
        # The bays open for the attack run: the dark well, two door leaves hanging from its edges.
        _patch(dark, [(s * x, y) for x, y in _saw(.12, .98, -1.3, 1.7, teeth=2, depth=.2)], upper=False, off=.008)
        for hx, lean in ((.14, -.12), (.96, .18)):
            zh = _skin_z(hx, .2, False) - .01
            leaf = Matrix.Translation(Vector((s * hx, .2, zh))) @ Matrix.Rotation(s * lean, 4, 'Y')
            bays.box((.025, 2.7, .3), loc=tuple(leaf @ Vector((0, 0, -.15))), rot=tuple(leaf.to_euler('XYZ')),
                     bevel=0)
        # The main gear doors, the nose gear doors, flush vents and blade antennas underneath.
        _patch(bays, [(s * x, y) for x, y in _saw(1.5, 2.1, -2.0, -.7, teeth=1, depth=.15)], upper=False)
        _patch(bays, [(s * x, y) for x, y in _saw(.06, .34, -3.1, -2.3, teeth=1, depth=.08)], upper=False)
        for x0, x1, dy, h in ((2.4, 3.3, .5, .8), (3.8, 4.7, .45, .7), (5.2, 5.9, .4, .55), (6.4, 7.1, .35, .45),
                              (7.5, 8.2, .3, .35), (3.0, 3.9, 1.7, .9), (4.6, 5.5, 1.4, .8), (6.1, 6.9, 1.1, .6),
                              (1.3, 2.1, 3.0, .7), (2.3, 3.1, 3.6, .6), (3.6, 4.4, 3.4, .6), (5.3, 6.1, 2.9, .5)):
            y0 = _le(x1) + dy
            _patch(bays, [(s * x, y) for x, y in _saw(x0, x1, y0, y0 + h, teeth=1, depth=.1)], upper=False)
        for x, dy in ((2.6, 1.0), (3.4, 2.4), (4.6, 1.6), (6.0, 1.2), (1.8, 2.2), (2.2, 3.4), (5.1, 2.6),
                      (7.0, 1.7), (8.3, .9), (8.9, .4), (4.0, 3.0), (6.6, 2.4)):
            y = _le(x) + dy
            _patch(a.part('Skin_vents', 'Undercarriage'), [(s * (x - .1), y - .06), (s * (x + .1), y - .06),
                                                           (s * (x + .1), y + .06), (s * (x - .1), y + .06)],
                   upper=False, off=.004, thick=.008, step=1.0)
        K.blade_antenna(a.part('Antennas', 'Armor'), (s * 1.1, 2.0, _skin_z(1.1, 2.0, False)), h=.12, chord=.15,
                        normal=(0, 0, -1))
        _patch(a.part('Flare_mouths', 'Undercarriage'), [(s * 2.2, 2.9), (s * 2.55, 2.9), (s * 2.55, 3.15),
                                                          (s * 2.2, 3.15)], upper=False, off=.01)
    b = a.pivot('Bombs', (0, 0, 0))
    for s in (-1, 1):
        z = _skin_z(.55, .2, False) - .02
        k.lathe(a.part('Bomb_bodies', 'Armor', b), [(0, -1.45), (.12, -1.38), (.19, -1.1), (.2, -.6), (.2, .9),
                                                     (.16, 1.25), (.12, 1.35), (0, 1.36)],
                loc=(s * .55, .2, z), rot=(-R90, 0, 0), seg=12, worn=(3,))
        k.lathe(a.part('Bomb_seekers', 'Glass', b), [(.11, 0), (.08, .07), (0, .1)], loc=(s * .55, -1.33, z),
                rot=K.FORWARD, seg=10)
        fins = a.part('Bomb_fins', 'Steel', b)
        for u in (math.radians(45), math.radians(135), math.radians(225), math.radians(315)):
            fins.box((.012, .38, .2), loc=(s * .55 + math.cos(u) * .2, 1.25, z + math.sin(u) * .2),
                     rot=(0, -u + R90, 0), bevel=0)
        a.part('Bomb_bands', 'Hazard', b).cyl(.205, .05, loc=(s * .55, -.85, z), rot=K.FORWARD, seg=12, bevel=0)
    a.pivot('Muzzle_missile', (0, .2, _skin_z(0, .2, False) - .2))
    # The standoff missiles (JASSM-class, faceted) on pylons under the wings.
    for i, s in enumerate((1, -1)):
        x, y = s * 3.7, .55
        z = _skin_z(3.7, y, False)
        a.part('Pylons', 'Armor').box((.08, 1.3, .22), loc=(x, y + .1, z - .1), taper=(1, .85), bevel=.01)
        zm = z - .36
        k.extrude(a.part('Standoff_missile', 'Armor'), [(-.17, -.1), (.17, -.1), (.13, .1), (-.13, .1)], 2.3,
                  loc=(x, y, zm), axis='Y', chamfer=.08, corner=.02)
        k.extrude(a.part('Standoff_missile', 'Armor'), [(-.17, -.1), (.17, -.1), (.13, .1), (-.13, .1)], .35,
                  loc=(x, y - 1.3, zm), axis='Y', chamfer=0, taper=(.15, .35))
        mf = a.part('Missile_fins', 'Steel')
        mf.box((1.1, .26, .015), loc=(x, y - .1, zm + .1), bevel=0)
        mf.box((.015, .3, .22), loc=(x, y + 1.0, zm + .18), rot=(-.3, 0, 0), bevel=0)
        a.pivot(K.name('Muzzle_rocket', i), (x, y - 1.5, zm))
    hook = a.part('Arrestor_hook', 'Steel')
    zh = _skin_z(0, 3.2, False)
    hook.limb((0, 2.6, zh - .02), (0, 3.95, zh + .02), .06, .05, bevel=0)
    hook.box((.14, .14, .08), loc=(0, 3.98, zh - .01), bevel=0)
    a.part('Hook_stripes', 'Hazard').box((.07, .3, .055), loc=(0, 3.5, zh - .03), bevel=0)


def stealth_naval_strike(a):
    """The A-12 Avenger II carrier flying wing (see the module docstring). Runtime: Bombs (the two bombs, hidden
    when they drop), Muzzle_missile (the bay release point), Muzzle_rocket / .001 (the standoff missiles' noses),
    Point_exhaust, Point_fire; Part_wing comes from mb_p34_parts (the left half of `Wing`, whole length)."""
    K.suffixed(a)
    _jet_wing(a)
    _jet_body(a)
    _jet_under(a)
    _merge(a)
    k.clean(a)


BUILDERS = {
    'wheeled_gun': (wheeled_gun, dict(ao_distance=.5, grime_height=.55, ao_strength=.72)),
    'command_vehicle': (command_vehicle, dict(ao_distance=.45, grime_height=.5, ao_strength=.7)),
    'ew_jammer': (ew_jammer, dict(ao_distance=.5, grime_height=.55, ao_strength=.72)),
    'iron_beam': (iron_beam, dict(ao_distance=.45, grime_height=.5, ao_strength=.72)),
    'stealth_naval_strike': (stealth_naval_strike, dict(ao_distance=.6, ao_strength=.6, ground=False)),
}
