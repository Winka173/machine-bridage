"""Machine Brigade fixed defences, set 3: new towers and obstacles for the base slots, built with
frontier_kit and the mb_siege / mb_fortress base kit, in their style (battered concrete, Team steel,
sandbags, camouflage netting). Sizes are the in-game size at scale 1.0 (slot: small 5 m, medium 6.5 m,
large 9 m across).

Towers are "vehicles" with speed 0 (ModelLibrary rigs them like tanks):
  * ew_tower (small, 4 x 4 m pad, 10 m): electronic-warfare jamming mast: a galvanised four-legged lattice
    mast with a caged service platform on a concrete pad, an equipment shelter, a generator and fuel drums.
    The jamming head spins on `Radar` (the game's radar speed): three directional panel arrays round a
    column (the big main array faces -Y), two dishes on arms, a log-periodic antenna and a red obstruction
    light on top. No gun: `Muzzle_main` (child of Radar) is the centre of the main array's face, where the
    jamming pulse starts.
  * atgm_tower (medium, 5.2 x 5.2 m pad, launcher top 4.6 m): a squat battered concrete tower with firing
    slits, a blast door and an outside steel stair, a sandbagged roof and spare missile canisters. The
    roof carries a Kornet-EM style twin launcher on `Turret`: a thermal / TV sight box between two
    missile containers. Elevating group: `Launcher*` parts (containers, sight, cross beam) and the
    `ATGM_pod` tube mouths; its automatic elevation pivot falls on the yoke's trunnion shaft.
    `Muzzle_missile` (left tube, -X) and `Muzzle_missile.001` (right tube, +X) at the tube mouths;
    `Muzzle_main` = the left tube mouth (the elevation rig needs one). The two `ATGM_pod` mouths are also
    the missile slot's launch pair (ModelLibrary.AddLaunchPoints), so one missile mount fires from both
    tubes in turn.
  * c_ram (medium, 5.6 x 5.6 m pad, radome top 3.9 m, search radar 5.4 m): Centurion C-RAM: a Phalanx
    block 1B mount on a deployed trailer (outriggers down) with a power cabinet, on a thin concrete pad,
    and a search radar spinning on `Radar` on a telescopic mast at the rear right corner. `Turret` carries
    the yoke and the elevating mass: the white radome (`Pod_radome`, `Pod_*`), the magazine drum
    (`Pod_drum`) and the six-barrel 20 mm gatling (`Main_cannon`, the barrel clamp `Muzzle_brake`), so the
    radome elevates with the gun as on the real mount; the automatic pivot falls on the yoke's trunnions.
    `Muzzle_main` and `Muzzle_gun` at the barrel cluster's exit (only Muzzle_main rides the elevation
    pivot: ModelLibrary's BarrelPattern has no muzzle_gun).
  * gun_pit (medium, 6 m across the berm, turret top 1.85 m raised; the gun reaches 4.4 m forward): hidden
    gun pit: an earth berm ring faced with a timber revetment and sandbags, camouflage netting on low poles
    over the berm, an entrance at the back, ready rounds, and a dome turret with a 115 mm gun on a lifting
    platform. `Lift` (the game lowers it) carries `Turret`, and every moving part is under Turret (lift
    table, ram, turret, gun). Authored RAISED. Lowered by LIFT_DROP = 1.6 m the turret roof sits at the pit
    floor (cupola top 0.25 m, whip tip 0.87 m, under the 1.11 m sandbag crest) and the gun, the coax and the
    muzzle brake lie below ground level (brake top -0.05 m), so nothing shows above the berm or outside
    the pit. Raised, everything static inside the gun's reach stays under 1.28 m (net and garnish), 7 cm
    under the muzzle brake. Main_cannon / Muzzle_brake / `Muzzle_main`, coaxial MG (`Coax*`,
    `Muzzle_coax`).
  * drone_hangar (large, 8 x 8 m pad, 5 m): FPV drone hangar: an earth-covered concrete arch shelter
    with a headwall, an open roll-up door and a lit interior (workbench, drone shelf), a steel launch deck
    on the roof with an inclined launch rail (a drone ready at its top end) and a rack of four drones, a
    ground-control container with an antenna mast (panel antennas, datalink dish), a generator and
    sandbags. `Muzzle_door_l` (and `Muzzle_main` at the same point) sits on the ready drone at the top of
    the rail, turned to point along the rail (forward and 28 degrees up).
Obstacles (props, no weapon):
  * dragons_teeth (5 x 2.5 m, 1.2 m): weathered concrete dragon's teeth in two staggered rows on a
    buried footing, one broken tooth with rusty rebar, a Czech hedgehog, moss and grass, Team marker
    stakes at the ends. Segments tile every 5 m along X (each row keeps its 1.667 m pitch across the joint).
  * minefield (4.9 x 4.9 m, 1 m): a marked minefield: a dirt patch fenced with pickets, barbed wire and
    red-white tape, red triangular skull "MINES" signs at the corners and on the wire, half-buried
    anti-tank mines, a stake mine with its tripwire, and turned earth. The single regenerating mines
    reuse mb_support's `mine` model.

Conventions follow mb_siege / mb_fortress: metres, +Z up, Blender -Y is the front, +X the right, origins
on the ground at the footprint centre. Touching parts overlap or stand at least 1 cm apart, never face to
face. Each turret's weapon is the highest thing inside its sweep. Pivots the game pairs by slot take a
numeric suffix (Muzzle_missile.001): they are authored as Muzzle_missile__001 and renamed after
Asset.finish (see _runtime_names). Parts under a moving pivot (Radar, Lift) receive occlusion but never
cast it.
"""
import functools
import math
import random

from mathutils import Matrix, Vector, noise

from frontier_kit import chamfered
from mb_bosses import _railing
from mb_fortress import _embrasure, _qframe
from mb_siege import (_moving_pivots, bag_arc, bag_run, caged_lamp, crate, generator, hazard_sign, lattice,
                      loop_rail, shells, sweep)
from mb_support import _quadcopter
from mb_themes import ladder
from mb_vehicles import ACROSS, FORWARD, R90, _antenna, _face_box, _frame, _hatch, _periscopes
from mb_vehicles2 import _gun

TAU = math.tau
LIFT_DROP = 1.6  # how far the game lowers gun_pit's `Lift` to hide the gun (metres, Blender Z / Unity Y)


# ----------------------------------------------------------------------------- shared helpers
def _runtime_names(build):
    """Pivots named with a Blender-style suffix are authored as Name__001 (frontier_kit refuses runtime
    names with a dot) and renamed Name.001 once the asset is finished, as mb_round6.finish does;
    build_assets.py calls Asset.finish itself, so the rename rides on it."""
    @functools.wraps(build)
    def wrapped(a):
        build(a)
        finish = a.finish

        def finish_and_rename():
            finish()
            for o in list(a.collection.objects):
                if '__' in o.name:
                    want = o.name.replace('__', '.')
                    o.name = want
                    if o.name != want:
                        raise ValueError(f'{a.name}: could not name {want} (got {o.name})')
            return a
        a.finish = finish_and_rename
    return wrapped


def _dish_at(part, loc, yaw, rx, rz, depth=.15, seg=12, tilt=0.0):
    """mb_vehicles._dish turned by yaw about Z: the concave side faces (sin yaw, -cos yaw), tilted up."""
    turn = Matrix.Rotation(yaw, 3, 'Z') @ Matrix.Rotation(-tilt, 3, 'X')
    base = Vector(loc)

    def ring(k, dy):
        return [tuple(base + turn @ Vector((rx * k * math.cos(u), dy, rz * k * math.sin(u))))
                for u in (i * TAU / seg for i in range(seg))]
    part.loft([[tuple(base)], ring(.55, -depth * .35), ring(1.0, -depth), ring(.96, -depth - .05),
               ring(.5, -depth * .35 - .05), [tuple(base + turn @ Vector((0, -.05, 0)))]])


def _facing(yaw):
    """Outward unit normal (sin yaw, -cos yaw, 0) of a face turned by yaw (0: -Y) and its along-face axis."""
    return Vector((math.sin(yaw), -math.cos(yaw), 0)), Vector((math.cos(yaw), math.sin(yaw), 0))


def _tuft(part, x, y, z, s, seed):
    part.ico((s, s * .85, s * .55), loc=(x, y, z + s * .2), sub=1, jitter=.4, seed=seed)


def _net_ring(a, rng, r0, r1, height, cells=(28, 4), tufts=30, tuft_h=(.05, .08), tuft_rings=None, parent=None,
              seed=0.0, keep=None, name='Camo_net'):
    """Camouflage net draped round a ring from radius r0 to r1 (a polar grid: cells = (around, across)),
    its drape given by height(r, angle); the inner edge is ragged (the first ring's radius wobbles) and
    cells whose centre fails keep(r, angle) are dropped. Garnish tufts (small open pyramids in dark green,
    khaki and earth) stand tuft_h above the sheet, only on the radial cells in tuft_rings (j0, j1): low, so
    the net stays under a gun's sweep."""
    na, nr = cells
    off = Vector((seed * 3.7, seed * 1.3, seed * 2.1))
    verts, index = [], {}
    for j in range(nr + 1):
        for i in range(na):
            u = i * TAU / na + (.35 * TAU / na * noise.noise(Vector((i * .7, j * .9, 3.0)) + off) if 0 < j < nr else 0)
            r = r0 + (r1 - r0) * j / nr
            if j == 0:
                r += .12 * noise.noise(Vector((math.cos(u) * 2.3, math.sin(u) * 2.3, 1.0)) + off)
            z = height(r, u) + .03 * noise.noise(Vector((r * math.cos(u), r * math.sin(u), 7.0)) + off)
            index[i, j] = len(verts)
            verts.append((r * math.cos(u), r * math.sin(u), z))
    faces, kept = [], []
    for j in range(nr):
        for i in range(na):
            um = (i + .5) * TAU / na
            rm = r0 + (r1 - r0) * (j + .5) / nr
            if keep and not keep(rm, um):
                continue
            i2 = (i + 1) % na
            faces.append((index[i, j], index[i, j + 1], index[i2, j + 1], index[i2, j]))       # facing up
            kept.append((i, j))
    used = sorted({k for f in faces for k in f})
    remap = {k: n for n, k in enumerate(used)}
    a.part(name, 'Foliage', parent).mesh([verts[k] for k in used], [tuple(remap[k] for k in f) for f in faces])
    mats = ('FoliageDark', 'Canvas', 'FoliageDark', 'Dirt')
    if tuft_rings:
        kept = [(i, j) for i, j in kept if tuft_rings[0] <= j < tuft_rings[1]]
    for g in range(tufts if kept else 0):
        i, j = kept[rng.randrange(len(kept))]
        u = (i + rng.uniform(.2, .8)) * TAU / na
        r = r0 + (r1 - r0) * (j + rng.uniform(.25, .75)) / nr
        cx, cy = r * math.cos(u), r * math.sin(u)
        s = rng.uniform(.18, .3)
        yaw = rng.uniform(0, TAU)
        zc = height(r, u) + .035
        base = [(cx + s * math.cos(yaw + k * R90), cy + s * .75 * math.sin(yaw + k * R90), zc) for k in range(4)]
        top = (cx, cy, zc + rng.uniform(*tuft_h))
        a.part(f'{name}_garnish', mats[g % 4], parent).mesh(base + [top], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])


def _panel_array(a, parent, centre, yaw, w, h, d, name, bands=2):
    """Flat directional jammer array facing (sin yaw, -cos yaw): a Team back box with steel edge ribs and a
    raised white radome over its face, crossed by dark clamp bands; feed connectors under it. Returns the
    centre of the radome face."""
    n, t = _facing(yaw)
    c = Vector(centre)
    rot = (0, 0, yaw)
    a.part(f'{name}_back', 'Team', parent).box((w, d, h), loc=tuple(c), rot=rot, bevel=.03, seg=1)
    a.part(f'{name}_radome', 'Medical', parent).box((w - .08, .06, h - .08), loc=tuple(c + n * (d / 2 + .02)),
                                                    rot=rot, bevel=.025, seg=1)
    ribs = a.part(f'{name}_ribs', 'Armor', parent)
    for s in (-1, 1):
        ribs.box((.03, d + .04, h + .04), loc=tuple(c + t * (s * (w / 2 - .005))), rot=rot, bevel=0)
    for k in range(bands):
        z = -h / 2 + (k + 1) * h / (bands + 1)
        ribs.box((w + .02, .02, .05), loc=tuple(c + n * (d / 2 + .05) + Vector((0, 0, z))), rot=rot, bevel=0)
    plugs = a.part(f'{name}_plugs', 'Rubber', parent)
    for s in (-1, 1):
        plugs.cyl(.03, .1, loc=tuple(c + t * (s * w * .22) - n * .01 + Vector((0, 0, -h / 2 - .04))), seg=6, bevel=0)
    return c + n * (d / 2 + .05)


# ----------------------------------------------------------------------------- ew_tower
def ew_tower(a):
    """Electronic-warfare jamming mast (4 x 4 m pad, 10 m): a concrete pad with a galvanised four-legged
    lattice mast (inner ladder, a railed service platform with red obstruction lights, a cable run), an
    equipment shelter with an air conditioner, a lit door and cable entry, a generator set and fuel
    drums. The jamming head spins on `Radar` above a bearing housing: three directional panel arrays
    (Team backs, white radome tiles) round a steel column, the biggest facing -Y with `Muzzle_main` at the
    centre of its face, two datalink dishes on arms, a log-periodic antenna and a whip with a red
    obstruction light on top."""
    a.part('Pad', 'Concrete').prism(chamfered(4.0, 4.0, .45), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .24
    top = .24
    mx, my = .3, -.25                                                                        # mast axis
    hw0, hw1, z0, z1 = .6, .28, top, 6.6
    lattice(a.part('Mast', 'Steel'), mx, my, z0, z1, hw0, hw1, 5, leg=.12, brace=.035)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Base_plates', 'Steel').box((.26, .26, .05), loc=(mx + sx * hw0, my + sy * hw0, top + .015), bevel=0)
            a.part('Footings', 'Concrete').box((.44, .44, .12), loc=(mx + sx * hw0, my + sy * hw0, top + .03),
                                               bevel=.03, seg=1)
    ladder(a.part('Mast_ladder', 'Steel'), (mx, my - .02, top + .02), z1 + .05, 0.0, width=.34, step=.45, rung=.026)
    # Service platform with a railing and red obstruction lights on two corners.
    a.part('Platform', 'Armor').box((1.3, 1.3, .1), loc=(mx, my, z1 + .05), bevel=.02, seg=1)
    a.part('Grating', 'Undercarriage').box((1.12, 1.12, .02), loc=(mx, my, z1 + .105), bevel=0)
    e = .6
    loop_rail(a.part('Railing', 'Steel'), [(mx - e, my - e, z1 + .1), (mx + e, my - e, z1 + .1),
                                           (mx + e, my + e, z1 + .1), (mx - e, my + e, z1 + .1)],
              h=.8, post=.04, rail=.02, every=.6)
    a.part('Kick_plates', 'Team').shell([(-e - .02, -e - .02), (e + .02, -e - .02), (e + .02, e + .02),
                                         (-e - .02, e + .02)], .12, .03, loc=(mx, my, z1 + .09))
    red = a.part('Obstruction_lights', 'LavaGlow')
    for sx, sy in ((-1, -1), (1, 1)):
        red.sphere(.06, loc=(mx + sx * e, my + sy * e, z1 + .96), seg=8, rings=5)
    hw_mid = hw0 + (hw1 - hw0) * .5
    red.sphere(.06, loc=(mx + hw_mid + .07, my - hw_mid - .07, (z0 + z1) / 2 + .1), seg=8, rings=5)
    a.part('Light_brackets', 'Steel').box((.12, .12, .05), loc=(mx + hw_mid + .04, my - hw_mid - .04,
                                                                (z0 + z1) / 2 + .03), rot=(0, 0, .78), bevel=0)
    # Bearing housing under the spinning head; a cable run up the rear left leg.
    a.part('Bearing', 'Armor').cyl(.3, .36, loc=(mx, my, z1 + .28), seg=14, bevel=.03, bseg=1)       # to z1 + .46
    a.part('Bearing_ring', 'Steel').cyl(.34, .06, loc=(mx, my, z1 + .44), seg=14, bevel=0)
    zr = z1 + .47
    lx, ly = mx - hw0 + .11, my + hw0 - .11
    a.part('Cable_run', 'Rubber').tube([(-.1, .78, .75), (lx + .02, ly + .05, .6), (lx, ly, 1.2),
                                        (mx - hw1 + .1, my + hw1 - .1, z1 - .1), (mx - .15, my + .15, z1 + .2)],
                                       .035, seg=5)

    # ---------------------------------------------------------------- jamming head (spins)
    # Everything that turns clears the platform railing (top at zr + .43): the arrays start above it.
    r = a.pivot('Radar', (mx, my, zr))
    head = a.part('Head_steel', 'Steel', r)
    head.cyl(.36, .08, loc=(0, 0, .04), seg=14, bevel=.015, bseg=1)                               # turntable
    head.cyl(.1, 1.86, loc=(0, 0, .06 + .93), seg=10, bevel=0)                                    # column
    head.cyl(.16, .14, loc=(0, 0, .2), seg=10, bevel=.02, bseg=1)                                # column foot
    arm = a.part('Head_arms', 'Armor', r)
    R, d = .3, .12
    zc = 1.12                                                                                    # arrays' centre
    for k in range(3):                                                                           # frame rings
        for z in (.62, 1.62):
            p0 = Vector((math.cos(k * TAU / 3 + R90) * R * 1.1, math.sin(k * TAU / 3 + R90) * R * 1.1, z))
            p1 = Vector((math.cos((k + 1) * TAU / 3 + R90) * R * 1.1,
                         math.sin((k + 1) * TAU / 3 + R90) * R * 1.1, z))
            arm.limb(tuple(p0), tuple(p1), .05, .05, bevel=0)
    for k in range(3):
        yaw = k * TAU / 3
        n, _t = _facing(yaw)
        for z in (.62, 1.62):
            arm.limb((0, 0, z), tuple(n * (R + .02) + Vector((0, 0, z))), .06, .06, bevel=0)
        big = k == 0
        w, h = (.96, 1.12) if big else (.72, .92)
        face = _panel_array(a, r, tuple(n * (R + d / 2) + Vector((0, 0, zc))), yaw, w, h, d, 'Array',
                            bands=3 if big else 2)
        if big:
            a.pivot('Muzzle_main', tuple(face + n * .01), r)
    # Two datalink dishes on arms between the arrays, facing the rear left and rear right.
    for yaw in (math.pi - .9, math.pi + .9):
        n, _t = _facing(yaw)
        p = n * .66 + Vector((0, 0, 1.86))
        arm.limb((0, 0, 1.8), tuple(p - n * .06), .07, .07, bevel=0)
        _dish_at(a.part('Dishes', 'Medical', r), tuple(p), yaw, .27, .27, depth=.11, seg=12, tilt=.15)
        a.part('Dish_feeds', 'Armor', r).limb(tuple(p + n * .05), tuple(p + n * .32), .03, .03, bevel=0)
    # Log-periodic antenna pointing forward on top of the column, a whip and the top light.
    zl = 1.98
    head.box((.06, 1.0, .06), loc=(0, -.24, zl), bevel=0)                                        # boom
    head.box((.15, .15, .12), loc=(0, 0, zl - .02), bevel=0)                                     # clamp
    lp = a.part('LPDA_elements', 'Steel', r)
    for k in range(7):
        half = .48 * .82 ** k
        lp.box((2 * half, .025, .025), loc=(0, .2 - k * .135, zl + (.035 if k % 2 else -.035)), bevel=0)
    a.part('Head_whip', 'Steel', r).cyl(.014, .8, loc=(0, .12, zl + .44), seg=5, bevel=0)
    a.part('Head_light', 'LavaGlow', r).sphere(.07, loc=(0, .12, zl + .87), seg=8, rings=5)

    # ---------------------------------------------------------------- shelter, generator, drums
    sx_, sy_, sw, sd, sh = -.62, 1.3, 1.9, 1.05, 1.3
    for x in (-1, 1):
        a.part('Shelter_blocks', 'Concrete').box((.3, sd + .1, .14), loc=(sx_ + x * (sw / 2 - .25), sy_, top + .05),
                                                 bevel=.02, seg=1)
    zs = top + .11
    a.part('Shelter', 'Team').box((sw, sd, sh), loc=(sx_, sy_, zs + sh / 2), bevel=.04, seg=1)
    fr = a.part('Shelter_frame', 'Armor')
    for x in (-1, 1):
        for y in (-1, 1):
            fr.box((.1, .1, sh + .04), loc=(sx_ + x * (sw / 2 - .03), sy_ + y * (sd / 2 - .03), zs + sh / 2), bevel=0)
    a.part('Shelter_roof', 'Team').box((sw + .06, sd + .06, .08), loc=(sx_, sy_, zs + sh + .02), bevel=.02, seg=1)
    for k in (-.5, 0, .5):                                                                   # roof seams
        fr.box((.04, sd + .07, .03), loc=(sx_ + k * sw * .6, sy_, zs + sh + .06), bevel=0)
    fy = sy_ - sd / 2
    a.part('Shelter_door', 'Armor').box((.7, .05, 1.08), loc=(sx_ - .45, fy - .01, zs + .58), bevel=.012, seg=1)
    a.part('Shelter_fittings', 'Steel').box((.05, .05, .12), loc=(sx_ - .2, fy - .045, zs + .58), bevel=0)
    a.part('Shelter_step', 'Steel').box((.8, .34, .05), loc=(sx_ - .45, fy - .19, top + .05), bevel=0)
    caged_lamp(a, '-y', (sx_ + .15, fy, zs + 1.12))
    a.part('Shelter_window', 'Glass').box((.42, .05, .26), loc=(sx_ + .55, fy - .005, zs + .82), bevel=0)
    a.part('Shelter_stencil', 'Hazard').box((.5, .03, .12), loc=(sx_ + .55, fy - .006, zs + 1.12), bevel=0)
    a.part('Aircon', 'Fuel').box((.36, .7, .62), loc=(sx_ - sw / 2 - .15, sy_, zs + .6), bevel=.03, seg=1)
    a.part('Aircon_grille', 'Undercarriage').grille(.5, .4, loc=(sx_ - sw / 2 - .34, sy_, zs + .6),
                                                    rot=(0, 0, -R90), slats=4, depth=.04, thickness=.03)
    a.part('Cable_entry', 'Armor').box((.08, .4, .34), loc=(sx_ + sw / 2 + .03, sy_ - .1, zs + .5), bevel=.01, seg=1)
    _antenna(a, None, sx_ - .7, sy_ + .3, zs + sh + .06, 1.2)
    a.part('Shelter_beacon', 'Alloy').sphere(.07, loc=(sx_ + .75, sy_ + .3, zs + sh + .12), seg=8, rings=5)
    cab = a.part('Cables', 'Rubber')
    cab.tube([(sx_ + sw / 2 + .06, sy_ - .2, zs + .4), (.25, .72, top + .04), (-.05, .5, top + .04)], .04, seg=5)
    generator(a, (-1.1, -1.3, top), size=(1.3, .7, .8), body='Armor', door='Team')
    cab.tube([(-.4, -1.05, top + .5), (-.2, -.9, top + .04), (.05, -.5, top + .04), (-.05, .5, top + .04)], .035, seg=5)
    for x, y in ((-1.58, -.32), (-1.52, .3)):
        a.part('Drums', 'BarrelRed').cyl(.26, .84, loc=(x, y, top + .42), seg=12, bevel=.02, bseg=1)
        a.part('Drum_rims', 'Steel').cyl(.27, .04, loc=(x, y, top + .6), seg=12, bevel=0)
        a.part('Drum_caps', 'Steel').cyl(.05, .03, loc=(x + .12, y, top + .85), seg=6, bevel=0)
    hazard_sign(a, (1.55, -1.5, top), size=.44, height=.95)
    # Cable reel on its side by the shelter's cable entry.
    reel = a.part('Cable_reel', 'Wood')
    for dy in (-.2, .2):
        reel.cyl(.42, .05, loc=(1.35, 1.3 + dy, top + .43), rot=FORWARD, seg=12, bevel=.01, bseg=1)
    a.part('Cable_reel_core', 'Rubber').cyl(.3, .36, loc=(1.35, 1.3, top + .43), rot=FORWARD, seg=12, bevel=0)
    a.part('Cable_reel_hub', 'Steel').cyl(.07, .52, loc=(1.35, 1.3, top + .43), rot=FORWARD, seg=6, bevel=0)
    for k in range(4):
        u = k * 1.7 + .4
        _tuft(a.part('Tufts', 'Grass', flat=True), 1.9 * math.cos(u), 1.9 * math.sin(u), -.02, .16, k * 1.3)


# ----------------------------------------------------------------------------- atgm_tower
def _tube_lip(part, bore, x, y, z, r, protrude=.06, seg=12):
    """Launch-tube mouth for a tube ending at (x, y, z) and facing -Y: a steel lip from 3 cm inside the tube
    to `protrude` in front of it (its face at y - protrude) round a dark recessed bore."""
    part.lathe([(r, -.03), (r, protrude), (r * .78, protrude), (r * .78, 0)], loc=(x, y, z), rot=FORWARD, seg=seg)
    bore.cyl(r * .76, .02, loc=(x, y - .012, z), rot=FORWARD, seg=seg, bevel=0)


def atgm_tower(a):
    """Anti-tank missile tower (5.2 x 5.2 m pad, launcher top 4.6 m): a squat battered concrete tower on a pad, with an
    overhanging roof slab and Team fascia, stepped firing slits, a steel blast door at the back under a
    lamp, and a steel stair up the right side to a landing at the roof. The roof is walled with two
    courses of sandbags (open at the stair) and holds spare missile containers on chocks, a hatch and a
    whip antenna. The launcher on `Turret` (Kornet-EM lineage) is a Team base housing on a turntable with a
    low shield and an electronics box, and a yoke whose trunnion shaft carries the elevating group: a
    thermal / TV sight box between two Team missile containers with bands, end caps and steel mouths, and
    a cross beam over them."""
    rng = random.Random(322)
    a.part('Pad', 'Concrete').prism(chamfered(5.2, 5.2, .7), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .24
    conc = a.part('Tower', 'Concrete')
    base = chamfered(3.4, 3.4, .55)
    z0, H, TP = .2, 2.8, .9
    conc.loft([[(x * (1 - (1 - TP) * f), y * (1 - (1 - TP) * f), z0 + H * f) for x, y in base]
               for f in (0, .25, .5, .75, 1)], bevel=.05, seg=1)                                # z .2 .. 3.0
    conc.prism(chamfered(3.7, 3.7, .6), .3, loc=(0, 0, 3.12), axis='Z', bevel=.04, seg=1)      # z 2.97 .. 3.27
    a.part('Fascia', 'Team').shell(chamfered(3.76, 3.76, .62), .18, .06, loc=(0, 0, 3.03))
    roof = 3.27

    def face(i, u, v, out=0.0):
        p, q = base[i], base[(i + 1) % len(base)]
        return _qframe((p[0], p[1], z0), (q[0], q[1], z0), (p[0] * TP, p[1] * TP, z0 + H),
                       (q[0] * TP, q[1] * TP, z0 + H), u, v, out)
    _embrasure(a, face(0, .5, .55), w=.7, h=.24)
    _embrasure(a, face(2, .3, .5), w=.6, h=.22)
    _embrasure(a, face(6, .5, .55), w=.7, h=.24)
    for u in (.2, .8):
        _face_box(a, 'Wall_band', 'Team', face(0, u, .86), (.5, .16, .03), bevel=0)
    _face_box(a, 'Stencils', 'Hazard', face(6, .5, .82), (.6, .16, .03), bevel=0)
    # Rear: steel blast door in a hazard frame, a lamp and a step.
    m = face(4, .5, .0)
    _face_box(a, 'Door_frame', 'Charred', m @ _frame((0, .95, 0), (0, 0, 0)), (1.12, 1.9, .06), bevel=0)
    _face_box(a, 'Door', 'Steel', m @ _frame((0, .9, 0), (0, 0, 0)), (.9, 1.7, .1), bevel=.015)
    for k in range(4):
        for s in (-1, 1):
            _face_box(a, 'Door_hazard', 'SafetyStripe' if k % 2 else 'Charred',
                      m @ _frame((s * .5, .25 + k * .42, 0), (0, 0, 0)), (.1, .42, .08), bevel=0)
    for dz in (.5, 1.3):
        _face_box(a, 'Door_ribs', 'Armor', m @ _frame((0, dz, 0), (0, 0, 0)), (.86, .08, .14), bevel=0)
    _face_box(a, 'Door_lamp_base', 'Steel', m @ _frame((0, 2.02, 0), (0, 0, 0)), (.18, .12, .1), bevel=0)
    lamp = m @ Vector((0, 2.0, .15))
    a.part('Door_lamp', 'Lamp').sphere(.07, loc=tuple(lamp), seg=8, rings=5)
    a.part('Steps', 'Concrete').box((1.2, .36, .1), loc=(0, 1.9, .27), bevel=.02, seg=1)
    # Steel stair up the right side, from the back to a landing at the roof slab's front right.
    st = a.part('Stair', 'Armor')
    tread = a.part('Stair_treads', 'Steel')
    rail = a.part('Stair_rail', 'Steel')
    xi, xo = 1.82, 2.36
    yb, yt, zb, zt = 1.95, -.4, .24, roof - .06
    for x in (xi, xo):
        st.limb((x, yb + .05, zb - .02), (x, yt, zt), .07, .2, bevel=0)
    steps = 12
    for k in range(1, steps):
        f = k / steps
        tread.box((xo - xi - .04, .24, .04), loc=((xi + xo) / 2, yb - (yb - yt) * f, zb + (zt - zb) * f), bevel=0)
    st.box((xo - xi + .08, .72, .08), loc=((xi + xo) / 2, yt - .3, zt - .02), bevel=.01, seg=1)       # landing
    for y in (yt - .6, yt + .02):
        st.limb(((xi + xo) / 2 + .2, y, zb), ((xi + xo) / 2 + .2, y, zt - .06), .08, .08, bevel=0)
    rail.tube([(xo + .02, yb - .15, zb + 1.0), (xo + .02, yt, zt + .95), (xo + .02, yt - .64, zt + .95),
               (xi - .08, yt - .64, zt + .95)], .025, seg=4)
    for k in range(5):
        f = k / 4
        y, z = yb - .15 - (yb - .15 - yt) * f, zb + (zt - zb) * (f * .92 + .04)
        rail.box((.04, .04, .95), loc=(xo + .02, y, z + .5), bevel=0)
    rail.box((.04, .04, .95), loc=(xo + .02, yt - .64, zt + .47), bevel=0)
    # Roof: two courses of sandbags round the edge, open at the stair landing.
    bags = a.part('Sandbags', 'Sandbag')
    e, c = 1.58, .52
    ring = [(e, -.3), (e, e - c), (e - c, e), (-e + c, e), (-e, e - c), (-e, -e + c), (-e + c, -e), (e - c, -e),
            (e, -e + c)]
    for course in range(2):
        for p, q in zip(ring, ring[1:]):
            bag_run(bags, rng, p, q, roof + .12 + course * .22, (.62, .34, .24), half=course == 1)
    # Spare missile containers on chocks at the back, a crate, a hatch and a whip antenna.
    chock = a.part('Chocks', 'Wood')
    for x in (-.55, .55):
        chock.box((.12, .62, .08), loc=(x, 1.0, roof + .04), bevel=0)
    spare = a.part('Spare_missiles', 'Team')
    caps = a.part('Spare_caps', 'Armor')
    for x, y, z in ((0, .86, .19), (0, 1.14, .19), (0, 1.0, .41)):
        spare.cyl(.1, 1.36, loc=(x, y, roof + z), rot=ACROSS, seg=10, bevel=.012, bseg=1)
        for s in (-1, 1):
            caps.cyl(.112, .06, loc=(s * .66, y, roof + z), rot=ACROSS, seg=10, bevel=0)
    crate(a, (-1.0, .95, roof), size=(.5, .36, .3), yaw=.2)
    a.part('Roof_hatch', 'Armor').box((.62, .62, .1), loc=(-.85, -.85, roof + .04), bevel=.025, seg=1)
    a.part('Roof_hatch_bar', 'Steel').box((.08, .5, .05), loc=(-.85, -.85, roof + .11), bevel=0)
    _antenna(a, None, -1.22, 1.24, roof, 1.6)
    a.part('Antenna_base', 'Steel').box((.12, .12, .08), loc=(-1.22, 1.24, roof + .03), bevel=0)
    for k, (x, y) in enumerate(((-2.2, -1.6), (2.2, 1.7), (-2.1, 1.9), (1.4, -2.2), (-1.0, 2.25))):
        _tuft(a.part('Tufts', 'Grass', flat=True), x, y, .2, .15 + .03 * (k % 2), k * 1.9)
    crate(a, (-2.05, -.5, .24), size=(.9, .4, .34), yaw=R90 + .1)

    # ---------------------------------------------------------------- launcher (Turret)
    tx, ty = 0.0, -.15
    a.part('Turret_socket', 'Armor').cyl(.64, .08, loc=(tx, ty, roof + .02), seg=16, bevel=.015, bseg=1)
    t = a.pivot('Turret', (tx, ty, roof + .04))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.56, .08, loc=(0, 0, .04), seg=16, bevel=.015, bseg=1)                             # turntable
    a.part('Base_housing', 'Team', t).box((.92, .82, .3), loc=(0, .02, .23), bevel=.04, seg=1, taper=(.92, .9))
    a.part('Base_shield', 'Team', t).box((1.06, .06, .34), loc=(0, -.47, .3), rot=(-.3, 0, 0), bevel=.012, seg=1)
    tarm.box((.56, .3, .24), loc=(0, .52, .3), bevel=.02, seg=1)                                  # electronics
    a.part('Base_vents', 'Undercarriage', t).grille(.4, .16, loc=(0, .675, .3), rot=(0, 0, math.pi), slats=3,
                                                    depth=.04, thickness=.03)
    # Elevating group (Launcher*, ATGM_pod): rear yr + .04 (end caps), front yf - .06 (tube mouths), bottom
    # zt_ - .145 (end caps), top zt_ + .34 (sight), so the automatic pivot (6 % from the rear, 30 % up) is
    # (yp, zt_): the trunnion shaft, on the tube axis.
    zt_, xr = .95, .5
    yr, yf, rt = .45, -1.45, .13
    yp = (yr + .04) - .06 * ((yr + .04) - (yf - .06))
    for s in (-1, 1):
        tarm.box((.07, .38, .64), loc=(s * .24, yp, .38 + .32), bevel=.015, seg=1, taper=(1, .7))       # yoke arms
        tsteel.cyl(.085, .05, loc=(s * .3, yp, zt_), rot=ACROSS, seg=10, bevel=0)                   # trunnion hubs
    tsteel.cyl(.05, .58, loc=(0, yp, zt_), rot=ACROSS, seg=8, bevel=0)                              # trunnion shaft
    tubes = a.part('Launcher', 'Team', t)
    bands = a.part('Launcher_bands', 'Armor', t)
    lips = a.part('ATGM_pod', 'Steel', t)
    bores = a.part('Launcher_bores', 'Undercarriage', t)
    for s in (-1, 1):
        x = s * xr
        tubes.cyl(rt, yr - yf, loc=(x, (yr + yf) / 2, zt_), rot=FORWARD, seg=12, bevel=.015, bseg=1)
        for f in (.14, .5, .86):
            bands.cyl(rt + .014, .05, loc=(x, yf + (yr - yf) * f, zt_), rot=FORWARD, seg=12, bevel=0)
        bands.cyl(rt + .015, .08, loc=(x, yr, zt_), rot=FORWARD, seg=12, bevel=.01, bseg=1)          # end cap
        _tube_lip(lips, bores, x, yf, zt_, rt + .01)
    sight = a.part('Launcher_sight', 'Armor', t)
    sight.box((.36, .7, .48), loc=(0, -.12, zt_ + .1), bevel=.035, seg=1)                           # zt_ -.14 .. +.34
    sight.box((.4, .12, .04), loc=(0, -.5, zt_ + .31), bevel=0)                                     # sun hood
    glass = a.part('Launcher_lens', 'Glass', t)
    glass.cyl(.1, .03, loc=(-.07, -.475, zt_ + .15), rot=FORWARD, seg=12, bevel=0)                  # thermal
    glass.box((.1, .03, .08), loc=(.1, -.475, zt_ + .17), bevel=0)                                  # TV
    glass.box((.08, .03, .05), loc=(.1, -.475, zt_ - .02), bevel=0)                                 # laser
    a.part('Launcher_frame', 'Armor', t).box((1.18, .12, .1), loc=(0, -.3, zt_ + .17), bevel=.01, seg=1)
    tip = yf - .06
    a.pivot('Muzzle_missile', (-xr, tip, zt_), t)
    a.pivot('Muzzle_missile__001', (xr, tip, zt_), t)
    a.pivot('Muzzle_main', (-xr, tip, zt_), t)
    _antenna(a, t, .3, .6, .42, .7)


# ----------------------------------------------------------------------------- c_ram
def c_ram(a):
    """Centurion C-RAM (5.6 x 5.6 m pad, 5.3 m to the radar head): a Phalanx block 1B mount on a deployed
    two-axle trailer (Team deck, chassis rails, tandem wheels, hazard-striped outriggers down on jack pads,
    drawbar on its stand, tail lights, tool boxes) with a Team power cabinet (louvres, fan, beacon) cabled to
    the mount, on a thin concrete pad. The mount: a white pedestal and turntable with a Team band, a rear
    electronics enclosure and a white yoke; between the yoke arms the elevating mass: the white radome with
    its tracking-radar window and a Team band, the magazine drum under it and the six-barrel 20 mm gatling
    (housing, mid clamp and muzzle clamp) under the radome's front. A search radar spins on `Radar` on a
    three-legged telescopic mast at the rear right corner; ready ammunition and a sign stand on the pad."""
    a.part('Pad', 'Concrete').prism(chamfered(5.6, 5.6, .7), .18, loc=(0, 0, .07), axis='Z', bevel=.03, seg=1,
                                    taper=.99)                                                 # z -.02 .. .16
    top = .16
    # ---------------------------------------------------------------- trailer
    chassis = a.part('Trailer_chassis', 'Undercarriage')
    for s in (-1, 1):
        chassis.box((.16, 4.1, .2), loc=(s * .5, 0, .8), bevel=.02, seg=1)                          # z .7 .. .9
    for y in (-1.7, -.1, .8, 1.7):
        chassis.box((1.16, .12, .12), loc=(0, y, .8), bevel=0)
    deck = a.part('Trailer_deck', 'Team')
    deck.box((2.3, 4.2, .14), loc=(0, 0, .97), bevel=.03, seg=1)                                   # z .9 .. 1.04
    dz = 1.04
    edge = a.part('Trailer_edges', 'Armor')
    for s in (-1, 1):
        edge.box((.06, 4.22, .12), loc=(s * 1.16, 0, .96), bevel=0)
        for y in (-1.6, -.6, .9, 1.8):
            a.part('Tie_downs', 'Steel').box((.06, .1, .06), loc=(s * 1.2, y, .94), bevel=0)
    edge.box((2.34, .06, .12), loc=(0, -2.12, .96), bevel=0)
    for s in (-1, 1):                                                                           # tail lights
        a.part('Tail_lights', 'LavaGlow').box((.16, .03, .07), loc=(s * .85, -2.16, .9), bevel=0)
        a.part('Reflectors', 'Alloy').box((.08, .03, .05), loc=(s * .6, -2.16, .9), bevel=0)
    tyre, hub = a.part('Tyres', 'Rubber'), a.part('Hubs', 'Steel')
    rw = .36
    for y in (-.55, .35):                                                                       # tandem axle
        chassis.box((2.0, .1, .1), loc=(0, y, top + rw), bevel=0)
        for s in (-1, 1):
            tyre.cyl(rw, .28, loc=(s * .95, y, top + rw), rot=ACROSS, seg=14, bevel=.05, bseg=1)
            hub.cyl(rw * .5, .3, loc=(s * .95, y, top + rw), rot=ACROSS, seg=10, bevel=.015, bseg=1)
            hub.cyl(rw * .18, .34, loc=(s * .95, y, top + rw), rot=ACROSS, seg=6, bevel=0)
    for s in (-1, 1):                                                                           # tool boxes
        a.part('Tool_boxes', 'Armor').box((.3, .7, .34), loc=(s * .8, -1.5, .68), bevel=.02, seg=1)
    # Drawbar on its stand at the back (+Y).
    bar = a.part('Drawbar', 'Armor')
    for s in (-1, 1):
        bar.limb((s * .5, 2.0, .8), (0, 2.5, .72), .1, .12, bevel=0)
    bar.cyl(.07, .1, loc=(0, 2.53, .72), seg=10, bevel=0)
    a.part('Drawbar_stand', 'Steel').cyl(.045, .52, loc=(0, 2.35, top + .28), seg=8, bevel=0)
    a.part('Drawbar_stand', 'Steel').cyl(.12, .04, loc=(0, 2.35, top + .02), seg=8, bevel=0)
    # Outriggers out to both sides, jacks down on their pads.
    for sy in (-1.35, 1.35):
        for s in (-1, 1):
            x = s * 1.72
            arm = a.part('Outriggers', 'Armor')
            arm.box((1.2, .14, .14), loc=(s * 1.16, sy, .8), bevel=.015, seg=1)
            for k in range(3):
                a.part('Outrigger_hazard', 'SafetyStripe' if k % 2 else 'Charred').box(
                    (.18, .15, .15), loc=(s * (1.4 + k * .18), sy, .8), bevel=0)
            a.part('Jacks', 'Steel').cyl(.07, .7, loc=(x, sy, top + .4), seg=8, bevel=0)
            a.part('Jacks', 'Steel').box((.18, .18, .12), loc=(x, sy, .8), bevel=0)
            a.part('Jack_pads', 'Undercarriage').cyl(.2, .05, loc=(x, sy, top + .025), seg=10, bevel=.01, bseg=1)
    # Power cabinet at the back of the deck, cabled to the mount.
    cab = a.part('Power_cabinet', 'Team')
    cy_ = 1.65
    cab.box((1.7, .7, .72), loc=(0, cy_, dz + .36), bevel=.04, seg=1)
    a.part('Cabinet_roof', 'Armor').box((1.76, .76, .05), loc=(0, cy_, dz + .74), bevel=.015, seg=1)
    for s in (-1, 1):
        a.part('Cabinet_louvres', 'Undercarriage').grille(.5, .44, loc=(s * .87, cy_, dz + .38), rot=(0, 0, s * R90),
                                                          slats=4, depth=.04, thickness=.03)
    a.part('Cabinet_fan', 'Undercarriage').cyl(.22, .04, loc=(.4, cy_, dz + .78), seg=12, bevel=0)
    a.part('Cabinet_fan_guard', 'Steel').cyl(.24, .02, loc=(.4, cy_, dz + .8), seg=12, bevel=0)
    a.part('Cabinet_doors', 'Armor').box((.6, .03, .56), loc=(-.35, cy_ - .36, dz + .38), bevel=0)
    a.part('Cabinet_panel', 'Glass').box((.22, .03, .12), loc=(.4, cy_ - .36, dz + .52), bevel=0)
    a.part('Cabinet_beacon', 'Alloy').sphere(.07, loc=(-.6, cy_ + .15, dz + .82), seg=8, rings=5)
    a.part('Cabinet_stencil', 'Hazard').box((.5, .03, .1), loc=(.4, cy_ - .362, dz + .3), bevel=0)
    a.part('Cables', 'Rubber').tube([(-.2, cy_ - .36, dz + .1), (-.25, 1.0, dz + .04), (-.3, .7, dz + .1)], .045, seg=5)

    # ---------------------------------------------------------------- mount (static base)
    mx, my = 0.0, .2
    a.part('Base_plate', 'Armor').box((1.3, 1.3, .2), loc=(mx, my, dz + .09), bevel=.03, seg=1)      # to 1.23
    a.part('Pedestal', 'Medical').cyl(.58, .38, loc=(mx, my, dz + .38), seg=18, bevel=.03, bseg=1)    # to 1.61
    a.part('Base_bolts', 'Steel').bolts([(mx + sx * .55, my + sy * .55, dz + .2) for sx in (-1, 1) for sy in (-1, 1)],
                                        r=.04, h=.04, seg=6)
    zt = dz + .56
    t = a.pivot('Turret', (mx, my, zt))
    white = a.part('Turret_white', 'Medical', t)
    white.cyl(.66, .1, loc=(0, 0, .05), seg=18, bevel=.02, bseg=1)                                 # turntable
    a.part('Base_band', 'Team', t).cyl(.672, .05, loc=(0, 0, .06), seg=18, bevel=0)
    white.box((.9, .44, .34), loc=(0, .84, .27), bevel=.04, seg=1)                                  # electronics
    a.part('Turret_vents', 'Undercarriage', t).grille(.6, .2, loc=(0, 1.07, .28), rot=(0, 0, math.pi), slats=3,
                                                     depth=.04, thickness=.03)
    # Elevating mass (Pod*, Main_cannon, Muzzle_brake): rear .5 (radome back), front -2.3, bottom .14 (drum),
    # top 2.3 (dome) -> the automatic pivot (6 % from the rear, 30 % up) is on the yoke trunnions.
    yc, rr, zr0, zr1, ztop = -.1, .6, .75, 1.72, 2.3
    yrear, yfront, zbot = yc + rr, -2.3, .14
    yp, zp = yrear - .06 * (yrear - yfront), zbot + .3 * (ztop - zbot)
    for s in (-1, 1):
        white.box((.1, .5, zp + .02), loc=(s * .75, yp, (zp + .02) / 2 + .07), bevel=.02, seg=1, taper=(1, .62))
        a.part('Trunnion_hubs', 'Steel', t).cyl(.12, .12, loc=(s * .75, yp, zp), rot=ACROSS, seg=12, bevel=.015, bseg=1)
    prof = [(0, zr0), (rr, zr0), (rr, zr1)]
    for k in range(1, 6):
        u = k / 6 * R90
        prof.append((rr * math.cos(u), zr1 + (ztop - zr1) * math.sin(u)))
    prof.append((0, ztop))
    a.part('Pod_radome', 'Medical', t).lathe(prof, loc=(0, yc, 0), seg=20)
    a.part('Pod_band', 'Team', t).cyl(rr + .012, .12, loc=(0, yc, zr0 + .12), seg=20, bevel=0)
    a.part('Pod_window', 'Charred', t).box((.44, .12, .4), loc=(0, yc - rr + .02, 1.25), bevel=.02, seg=1)
    # Electro-optical sensor (block 1B) on the radome's left side, above the yoke arm.
    a.part('Pod_sensor', 'Armor', t).box((.16, .34, .3), loc=(-.62, yc - .12, 1.3), bevel=.03, seg=1)
    a.part('Pod_sensor_glass', 'Glass', t).box((.1, .03, .12), loc=(-.63, yc - .3, 1.32), bevel=0)
    a.part('Pod_drum', 'Armor', t).cyl(.28, .8, loc=(0, .05, zbot + .28), rot=FORWARD, seg=14, bevel=.03, bseg=1)
    a.part('Pod_drum_ends', 'Steel', t).cyl(.285, .04, loc=(0, .43, zbot + .28), rot=FORWARD, seg=14, bevel=0)
    zg = .6                                                                                     # gun axis
    gun = a.part('Main_cannon', 'Steel', t)
    gun.box((.32, .9, .24), loc=(0, -.15, zg), bevel=.03, seg=1)                                     # housing
    gun.box((.2, .3, .16), loc=(0, -.5, zg - .14), bevel=.02, seg=1)                                  # drive motor
    y0, y1, rc, rb = -.6, yfront, .09, .038
    for k in range(6):
        u = k * TAU / 6 + TAU / 12
        gun.cyl(rb, y0 - y1, loc=(rc * math.cos(u), (y0 + y1) / 2, zg + rc * math.sin(u)), rot=FORWARD, seg=6, bevel=0)
    gun.cyl(.05, y0 - y1 - .1, loc=(0, (y0 + y1) / 2 + .05, zg), rot=FORWARD, seg=6, bevel=0)          # centre rod
    gun.cyl(.155, .07, loc=(0, -1.45, zg), rot=FORWARD, seg=12, bevel=.01, bseg=1)                   # mid clamp
    gun.cyl(.15, .12, loc=(0, -.66, zg), rot=FORWARD, seg=12, bevel=.015, bseg=1)                    # rotor collar
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.15, .09, loc=(0, y1 + .09, zg), rot=FORWARD, seg=12, bevel=.01,
                                                   bseg=1)
    a.pivot('Muzzle_main', (0, y1 - .005, zg), t)
    a.pivot('Muzzle_gun', (0, y1 - .005, zg), t)

    # ---------------------------------------------------------------- search radar mast (rear right)
    rx, ry = 2.15, 2.15
    a.part('Mast_footing', 'Concrete').box((.5, .5, .2), loc=(rx, ry, top + .09), bevel=.03, seg=1)
    mast = a.part('Radar_mast', 'Steel')
    zm = top + .18
    for r_, h_ in ((.1, 1.9), (.08, 1.3), (.065, 1.0)):
        mast.cyl(r_, h_ + .04, loc=(rx, ry, zm + h_ / 2), seg=10, bevel=0)
        a.part('Mast_collars', 'Armor').cyl(r_ + .03, .08, loc=(rx, ry, zm + h_ - .03), seg=10, bevel=0)
        zm += h_
    for k in range(3):                                                                   # tripod, feet on the pad
        u = math.radians(225) + k * TAU / 3
        a.part('Mast_legs', 'Armor').limb((rx + .5 * math.cos(u), ry + .5 * math.sin(u), top), (rx, ry, 1.35), .06, .06,
                                          bevel=0)
        a.part('Mast_feet', 'Steel').box((.14, .14, .04), loc=(rx + .5 * math.cos(u), ry + .5 * math.sin(u), top + .01),
                                         bevel=0)
    a.part('Mast_box', 'Team').box((.3, .2, .4), loc=(rx - .15, ry - .15, 1.0), rot=(0, 0, .78), bevel=.02, seg=1)
    r = a.pivot('Radar', (rx, ry, zm))
    a.part('Radar_turntable', 'Armor', r).cyl(.2, .12, loc=(0, 0, .06), seg=12, bevel=.02, bseg=1)
    tilt = .26
    a.part('Radar_back', 'Team', r).box((1.0, .12, .56), loc=(0, .02, .46), rot=(-tilt, 0, 0), bevel=.03, seg=1)
    a.part('Radar_face', 'Medical', r).box((.9, .05, .48), loc=(0, -.05, .445), rot=(-tilt, 0, 0), bevel=.015, seg=1)
    a.part('Radar_arm', 'Steel', r).box((.12, .14, .26), loc=(0, .1, .2), bevel=0)
    a.part('Radar_iff', 'Armor', r).box((.9, .07, .08), loc=(0, .1, .8), rot=(-tilt, 0, 0), bevel=0)
    a.part('Radar_beacon', 'Alloy', r).sphere(.05, loc=(0, .2, .6), seg=8, rings=4)
    a.part('Cables', 'Rubber').tube([(rx - .12, ry - .12, top + .2), (1.3, 2.0, top + .04), (.5, 2.0, .7),
                                     (.3, cy_ + .36, dz + .2)], .04, seg=5)
    # Ready ammunition, a jerrycan pair and a warning sign on the pad.
    crate(a, (-1.95, -1.9, top), size=(.8, .42, .34), yaw=.6)
    crate(a, (-1.93, -1.88, top + .34), size=(.76, .4, .32), yaw=.66, band=False)
    for k in range(2):
        a.part('Jerrycans', 'Armor').box((.16, .34, .46), loc=(-2.0 + k * .2, 1.85, top + .23), rot=(0, 0, .1),
                                         bevel=.02, seg=1)
    hazard_sign(a, (2.2, -2.2, top), yaw=-.5, size=.44, height=.9)
    for k, (x, y) in enumerate(((2.2, -.6), (-2.25, .5), (.9, -2.3), (-1.1, 2.3))):
        _tuft(a.part('Tufts', 'Grass', flat=True), x, y, .12, .14, k * 2.3)


# ----------------------------------------------------------------------------- gun_pit
def _dome_z(profile, r):
    """Height of a lathe profile [(radius, z)...] (radius falling as z rises) at radius r."""
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        if r1 <= r <= r0:
            return z0 + (z1 - z0) * (r0 - r) / (r0 - r1 or 1e-6)
    return profile[-1][1] if r < profile[-1][0] else profile[0][1]


def gun_pit(a):
    """Hidden gun pit (6 m across the berm, raised turret top 1.85 m): a round pit whose timber revetment (planks on log
    posts) carries two courses of sandbags, banked outside with an earth berm, under a camouflage net on low
    poles that drapes over the berm to the ground; an entrance with a duckboard at the back, ready rounds
    and crates against the wall, and a dark lift shaft with a hazard-striped rim and four guide posts in the
    floor. The gun rises on `Lift` (authored raised): a steel lift table with hazard edges on a ram with
    braces, and a low cast dome turret (`Turret`, Team) with a netted roof, cupola, hatches, sight, bustle and
    antenna, a mantlet, a 115 mm gun with a fume extractor and muzzle brake, and a coaxial MG. Lowered by
    LIFT_DROP the turret roof sits at the pit floor and the gun lies below ground level."""
    rng = random.Random(344)
    zg = 1.45                                                                                   # gun axis, raised
    # ---------------------------------------------------------------- pit (static)
    a.part('Pit_floor', 'Dirt').cyl(2.02, .04, loc=(0, 0, .02), seg=24, bevel=0)
    a.part('Shaft', 'Charred').cyl(1.25, .012, loc=(0, 0, .046), seg=24, bevel=0)
    for k in range(16):
        u = (k + .5) * TAU / 16
        a.part('Shaft_rim', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.5, .16, .03), loc=(1.33 * math.cos(u), 1.33 * math.sin(u), .05), rot=(0, 0, u + R90), bevel=0)
    for k in range(4):
        u = TAU / 8 + k * R90
        p = (1.45 * math.cos(u), 1.45 * math.sin(u))
        a.part('Guide_posts', 'Steel').box((.1, .1, 1.0), loc=(p[0], p[1], .5), rot=(0, 0, u), bevel=.01, seg=1)
        a.part('Guide_caps', 'SafetyStripe').box((.14, .14, .06), loc=(p[0], p[1], 1.01), rot=(0, 0, u), bevel=0)
    gap = .3                                                                                    # entrance half-angle
    a0, a1 = R90 + gap, R90 + TAU - gap
    # Revetment: plank panels between log posts, 0.68 m high.
    n = 20
    hr, rp = .88, 2.02
    step = (a1 - a0) / n
    for i in range(n):
        u = a0 + (i + .5) * step
        chord = 2 * rp * math.sin(step / 2) + .02
        a.part('Revetment', 'Wood').box((chord, .08, hr), loc=(rp * math.cos(u), rp * math.sin(u), hr / 2),
                                        rot=(0, 0, u + R90), bevel=.01, seg=1)
    for i in range(n + 1):
        u = a0 + i * step
        a.part('Revetment_posts', 'LogWood').cyl(.06, hr + .1, loc=(1.94 * math.cos(u), 1.94 * math.sin(u),
                                                                    (hr + .1) / 2), seg=6, bevel=0)
    # A sandbag course on the revetment (top 1.11 m, under the gun's sweep), the berm behind it.
    bags = a.part('Sandbags', 'Sandbag')
    bag_arc(bags, rng, 2.2, a0, a1, hr + .105, size=(.62, .36, .21))
    path = [(2.28 * math.cos(u), 2.28 * math.sin(u)) for u in (a0 + k * (a1 - a0) / 26 for k in range(27))]
    sweep(a.part('Berm', 'Dirt'), path,
          [(-.24, -.02), (-.24, .84), (-.1, .9), (.1, .88), (.3, .64), (.5, .3), (.66, .04), (.7, -.02)],
          scale=lambda i: min(1.0, .35 + .65 * min(i, 26 - i) / 2))
    # Camouflage net on low poles, draped over the sandbags and the berm to the ground (max 1.2 m).
    poles = [(k * TAU / 6 + TAU / 12) for k in range(6)]

    fall = ((2.36, 1.14), (2.5, 1.0), (2.65, .76), (2.8, .44), (2.9, .22), (3.0, .05))       # clears the berm

    def drape(r, u):
        bump = max(0.0, .03 - .03 * min(abs(math.atan2(math.sin(u - p), math.cos(u - p))) for p in poles) / .25)
        if r <= fall[0][0]:
            return fall[0][1] + bump
        for (r0, z0), (r1, z1) in zip(fall, fall[1:]):
            if r <= r1:
                return z0 + (z1 - z0) * (r - r0) / (r1 - r0)
        return fall[-1][1]
    _net_ring(a, rng, 1.9, 3.0, drape, cells=(30, 4), tufts=30, tuft_h=(.05, .08), tuft_rings=(1, 4), seed=2.0,
              keep=lambda r, u: not (r < 2.3 and abs(math.atan2(math.sin(u - R90), math.cos(u - R90))) < gap * .8))
    for u in poles:
        a.part('Net_poles', 'LogWood').cyl(.045, .42, loc=(2.2 * math.cos(u), 2.2 * math.sin(u), .98), seg=6, bevel=0)
    # Entrance at the back: door posts, a duckboard and sandbag wings.
    for s in (-1, 1):
        u = R90 + s * gap
        a.part('Door_posts', 'LogWood').cyl(.07, 1.1, loc=(2.2 * math.cos(u), 2.2 * math.sin(u), .55), seg=6, bevel=0)
    duck = a.part('Duckboard', 'Wood')
    for x in (-.22, .22):
        duck.box((.08, 1.3, .05), loc=(x, 2.25, .06), bevel=0)
    for k in range(6):
        duck.box((.56, .12, .03), loc=(0, 1.72 + k * .21, .1), bevel=0)
    for s in (-1, 1):
        bag_run(bags, rng, (s * .7, 2.36), (s * .74, 2.92), .11, (.6, .34, .22))
    # Ready rounds and crates against the wall (out of the lift's way).
    shells(a, (-1.55, .27, .04), 2, 2, yaw=-.2)
    crate(a, (1.62, .2, .04), size=(.8, .38, .3), yaw=R90 + .17)
    crate(a, (1.63, .22, .34), size=(.74, .36, .28), yaw=R90 + .22, band=False)
    a.part('Spent_cases', 'Gilded').cyl(.065, .5, loc=(-.9, -1.5, .1), rot=(R90, 0, .6), seg=6, bevel=0)
    a.part('Spent_cases', 'Gilded').cyl(.065, .5, loc=(-.62, -1.6, .1), rot=(R90, 0, 1.1), seg=6, bevel=0)
    for k in range(7):
        u = k * .9 + .5
        if abs(math.atan2(math.sin(u - R90), math.cos(u - R90))) < gap + .1:
            continue
        _tuft(a.part('Tufts', 'Grass', flat=True), 2.85 * math.cos(u), 2.85 * math.sin(u), -.03, .15, k * 1.7)

    # ---------------------------------------------------------------- lift and turret (moving)
    lift = a.pivot('Lift', (0, 0, 1.0))
    zt = 1.05
    t = a.pivot('Turret', (0, 0, zt - 1.0), lift)
    _moving_pivots(a, {'Lift'})
    steel = a.part('Lift_table', 'Steel', t)
    steel.cyl(1.22, .12, loc=(0, 0, -.07), seg=24, bevel=.02, bseg=1)                              # world .92 .. 1.04
    a.part('Lift_deck', 'Undercarriage', t).cyl(1.12, .02, loc=(0, 0, .0), seg=24, bevel=0)
    for k in range(20):
        u = (k + .5) * TAU / 20
        a.part('Lift_hazard', 'SafetyStripe' if k % 2 else 'Charred', t).box(
            (.36, .03, .1), loc=(1.225 * math.cos(u), 1.225 * math.sin(u), -.07), rot=(0, 0, u + R90), bevel=0)
    steel.cyl(.2, 1.72, loc=(0, 0, -.13 - .86), seg=12, bevel=0)                                   # ram
    brace = a.part('Lift_braces', 'Armor', t)
    for k in range(4):
        u = k * R90 + TAU / 8
        brace.limb((.95 * math.cos(u), .95 * math.sin(u), -.12), (.18 * math.cos(u), .18 * math.sin(u), -.85), .07,
                   .07, bevel=0)
    a.part('Turret_ring', 'Armor', t).cyl(1.08, .08, loc=(0, 0, .03), seg=22, bevel=.015, bseg=1)
    dome = [(1.02, .05), (1.04, .12), (1.0, .3), (.88, .48), (.62, .6), (.3, .64), (0, .65)]
    a.part('Turret_body', 'Team', t).lathe(dome, seg=22)
    zc = zg - zt                                                                                # gun axis .40
    mant = a.part('Mantlet', 'Armor', t)
    mant.box((.6, .34, .44), loc=(0, -.93, zc), bevel=.07, seg=1)
    mant.cyl(.15, .16, loc=(0, -1.12, zc), rot=FORWARD, seg=12, bevel=.02, bseg=1)
    # Roof: a camouflage net over the back of the dome, cupola, hatches, sight, periscopes.
    verts, faces, na = [], [], 16
    for j, r_ in enumerate((.3, .58, .86)):
        for i in range(na):
            u = i * TAU / na
            k = 1 + .05 * noise.noise(Vector((math.cos(u) * 3, math.sin(u) * 3, r_ * 4)))
            verts.append((r_ * k * math.cos(u), r_ * k * math.sin(u), _dome_z(dome, r_ * k) + .025))
    for j in range(2):
        for i in range(na):
            um = (i + .5) * TAU / na
            if abs(math.atan2(math.sin(um + R90), math.cos(um + R90))) < .9:                        # mantlet side
                continue
            i2 = (i + 1) % na
            faces.append((j * na + i, (j + 1) * na + i, (j + 1) * na + i2, j * na + i2))           # facing up
    a.part('Roof_net', 'Foliage', t).mesh(verts, faces)
    for g, (r_, u) in enumerate(((.5, 1.2), (.75, 2.2), (.45, 3.0), (.72, -.2), (.6, 2.7))):
        cx, cy = r_ * math.cos(u), r_ * math.sin(u)
        z = _dome_z(dome, r_) + .05
        a.part('Roof_net_garnish', ('FoliageDark', 'Canvas', 'Dirt')[g % 3], t).mesh(
            [(cx - .16, cy, z), (cx, cy - .12, z), (cx + .16, cy, z), (cx, cy + .12, z), (cx, cy, z + .07)],
            [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.cyl(.28, .2, loc=(-.38, .12, .67), seg=14, bevel=.03, bseg=1)                             # cupola
    a.part('Cupola_top', 'Armor', t).cyl(.23, .05, loc=(-.38, .12, .79), seg=14, bevel=.015, bseg=1)
    _hatch(a, -.38, .12, .8, .18, parent=t)
    _periscopes(a, [(-.38 + .29 * math.cos(u), .12 + .29 * math.sin(u), .64, u + R90)
                    for u in (-R90 - .7, -R90, -R90 + .7)], parent=t)
    _hatch(a, .38, .22, .63, .22, parent=t)
    tarm.box((.22, .3, .2), loc=(.46, -.5, .6), bevel=.03, seg=1)                                  # sight
    a.part('Sight_glass', 'Glass', t).box((.16, .03, .1), loc=(.46, -.655, .62), bevel=0)
    tarm.box((.84, .44, .32), loc=(0, 1.02, .3), bevel=.04, seg=1)                                 # bustle
    a.part('Bustle_rail', 'Steel', t).tube([(-.38, .86, .47), (-.38, 1.2, .47), (.38, 1.2, .47), (.38, .86, .47)],
                                            .02, seg=4)
    _antenna(a, t, .6, .7, .42, 1.0)
    # Gun and coaxial MG (the elevating group: rear -.88 at the coax housing, front at the brake, so the
    # automatic pivot falls at the mantlet's face).
    tip = _gun(a, t, 0, -1.05, zc, 2.95, .07, pitch=0.0, seg=12,
               sleeves=((.28, .06, .085), (.66, .06, .085)), extractor=(.45, .5, .105), brake=(.42, .1, 2),
               brake_seg=12)
    a.pivot('Muzzle_main', tip, t)
    coax = a.part('Coax', 'Steel', t)
    cx = .24
    coax.box((.1, .24, .1), loc=(cx, -1.0, zc), bevel=.015, seg=1)
    coax.cyl(.03, .48, loc=(cx, -1.36, zc), rot=FORWARD, seg=8, bevel=0)
    a.part('Coax_hider', 'Undercarriage', t).cyl(.042, .08, loc=(cx, -1.64, zc), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (cx, -1.685, zc), t)


# ----------------------------------------------------------------------------- drone_hangar
def _arch(cx, a_, b_, z0, th0, th1, n):
    """Points (x, z) of a half-ellipse arch about x = cx, radii a_ (across) and b_ (up) from angle th0 to th1."""
    return [(cx + a_ * math.cos(th0 + (th1 - th0) * i / n), z0 + b_ * math.sin(th0 + (th1 - th0) * i / n))
            for i in range(n + 1)]


def _drone_shelf(a, x0, y0, z0, tiers=(0.0, .5), k=1.1):
    """Two-tier steel drone shelf standing on (x0, y0, z0), a quadcopter on each half of each shelf."""
    frame = a.part('Drone_rack', 'Steel')
    w, d = .8, 1.7
    top = z0 + tiers[-1] + .5
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame.box((.05, .05, top - z0), loc=(x0 + sx * w / 2, y0 + sy * d / 2, (z0 + top) / 2), bevel=0)
    for zt in tiers:
        a.part('Drone_shelves', 'Armor').box((w + .06, d + .06, .04), loc=(x0, y0, z0 + zt + .1), bevel=0)
        for sy in (-1, 1):
            _quadcopter(a, _frame((x0, y0 + sy * .42, z0 + zt + .12), (0, 0, 0)), k=k, full=False)


def drone_hangar(a):
    """FPV drone hangar (8 x 8 m pad, 5 m): a hardened concrete arch shelter, its crown and flanks under
    a grass-covered earth layer, with a flat concrete headwall carrying a Team fascia, a hazard-striped
    doorway with its roll-up door raised (the shutter box and bottom slat above the opening) and a lamp; the
    dark interior shows a lit drone shelf and a workbench. On the roof a railed steel launch deck (reached
    by a ladder up the back wall) holds an inclined Team launch rail with a quadcopter ready at its top end
    and a two-tier rack of four more. A Team ground-control container (door, windows, air conditioner) with
    an antenna mast (panel antennas, datalink dish, whips), a generator, sandbags, battery crates and a
    drone on a trolley stand round it. `Muzzle_door_l` and `Muzzle_main` sit on the ready drone, turned to
    point along the rail."""
    rng = random.Random(355)
    a.part('Pad', 'Concrete').prism(chamfered(8.0, 8.0, .9), .22, loc=(0, 0, .09), axis='Z', bevel=.04, seg=1,
                                    taper=.995)                                                # z -.02 .. .2
    top = .2
    hx, A, B, th = -.55, 2.45, 2.8, .32                                                         # arch
    yf, yb = -2.25, 2.5
    n = 12
    outer = _arch(hx, A, B, top, 0, math.pi, n)
    inner = _arch(hx, A - th, B - th * .95, top, math.pi, 0, n)
    ring = outer + inner                                                                        # U section
    a.part('Hangar', 'Concrete').loft([[(x, y, z) for x, z in ring] for y in (yf, -1.0, .25, 1.5, yb)])
    wall = _arch(hx, A - th + .03, B - th * .95 + .03, top, 0, math.pi, n)
    a.part('Hangar_back', 'Concrete').prism(wall, .3, loc=(0, yb - .14, 0), axis='Y', bevel=0)
    a.part('Hangar_floor', 'Asphalt').box((2 * (A - th) - .04, yb - yf - .2, .04), loc=(hx, (yf + yb) / 2, top + .02),
                                           bevel=0)
    # Earth cover over the crown and flanks, bumpy, the concrete showing low on the sides.
    cover = []
    for th_ in [.34 + (math.pi - .68) * i / 10 for i in range(11)]:
        k = 1 + .025 * noise.noise(Vector((math.cos(th_) * 3, math.sin(th_) * 3, 1.0)))
        cover.append((hx + (A + .2) * k * math.cos(th_), top + (B + .2) * k * math.sin(th_)))
    under = [(hx + (A - .04) * math.cos(t_), top + (B - .04) * math.sin(t_))
             for t_ in [math.pi - .34 - (math.pi - .68) * i / 10 for i in range(11)]]
    a.part('Earth_cover', 'Grass').loft([[(x, y, z) for x, z in cover + under] for y in (yf + .1, -.6, 1.0, yb - .05)])
    for s in (-1, 1):                                                                           # earth toes
        x = hx + s * (A + .1)
        a.part('Earth_toes', 'Dirt').prism([(-.35, 0), (.35, 0), (.02, .95), (-.02, .95)], yb - yf - .2,
                                           loc=(x, (yf + yb) / 2, top - .02), rot=(0, 0, 0), axis='Y', bevel=0)
    # Headwall with the doorway, fascia, hazard jambs, the raised roll-up door and a lamp.
    hw = a.part('Headwall', 'Concrete')
    y0_, y1_ = -2.8, -2.2
    yc_, dp = (y0_ + y1_) / 2, y1_ - y0_
    dw, dh, H = 1.1, 2.1, 3.25
    hw.box((2.75 - dw, dp, H), loc=(hx - (2.75 + dw) / 2, yc_, top + H / 2), bevel=.05, seg=1)
    hw.box((2.75 - dw, dp, H), loc=(hx + (2.75 + dw) / 2, yc_, top + H / 2), bevel=.05, seg=1)
    hw.box((2 * dw + .1, dp, H - dh), loc=(hx, yc_, top + dh + (H - dh) / 2), bevel=.05, seg=1)
    a.part('Fascia', 'Team').box((5.56, .06, .32), loc=(hx, y0_ - .01, top + H - .26), bevel=0)
    a.part('Headwall_cap', 'Concrete').box((5.6, dp + .1, .12), loc=(hx, yc_, top + H + .04), bevel=.03, seg=1)
    for s in (-1, 1):
        for k in range(6):
            a.part('Door_hazard', 'SafetyStripe' if k % 2 else 'Charred').box(
                (.2, .04, .36), loc=(hx + s * (dw + .14), y0_ - .01, top + .2 + k * .36), bevel=0)
        a.part('Door_rails', 'Steel').box((.08, .12, dh), loc=(hx + s * (dw - .03), y0_ + .04, top + dh / 2), bevel=0)
    a.part('Door_box', 'Team').box((2 * dw + .3, .36, .42), loc=(hx, y0_ - .17, top + dh + .24), bevel=.03, seg=1)
    a.part('Shutter', 'Armor').box((2 * dw - .06, .06, .16), loc=(hx, y0_ + .02, top + dh - .06), bevel=0)
    a.part('Stencils', 'Hazard').box((.6, .03, .22), loc=(hx - 2.05, y0_ - .01, top + 2.1), bevel=0)
    caged_lamp(a, '-y', (hx + 2.05, y0_, top + 2.3))
    # Interior seen through the door: a lit drone shelf and a workbench with a lamp.
    _drone_shelf(a, hx + 1.2, -1.3, top + .04, tiers=(0.0, .55), k=1.15)
    bench = a.part('Workbench', 'Wood')
    bench.box((.7, 1.4, .06), loc=(hx - 1.3, -1.3, top + .85), bevel=0)
    for sy in (-1, 1):
        a.part('Workbench_legs', 'Steel').box((.6, .05, .82), loc=(hx - 1.3, -1.3 + sy * .62, top + .43), bevel=0)
    a.part('Interior_lamps', 'Lamp').box((.12, 1.6, .05), loc=(hx, -1.2, top + B - th - .06), bevel=0)
    a.part('Interior_lamps', 'Lamp').box((.3, .2, .12), loc=(hx - 1.3, -1.7, top + 1.0), bevel=0)
    _quadcopter(a, _frame((hx - 1.3, -1.1, top + .88), (0, 0, .5)), k=1.1, full=False)

    # ---------------------------------------------------------------- launch deck on the roof
    zd = top + B + .45                                                                          # deck top 3.45
    dx, dy = hx, .7
    a.part('Deck', 'Armor').box((2.5, 3.2, .1), loc=(dx, dy, zd - .05), bevel=.02, seg=1)
    a.part('Deck_grating', 'Undercarriage').box((2.3, 3.0, .02), loc=(dx, dy, zd + .005), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Deck_posts', 'Steel').box((.12, .12, .8), loc=(dx + sx * 1.0, dy + sy * 1.3, zd - .45), bevel=0)
    rail = a.part('Deck_railing', 'Steel')
    e, f = 1.22, 1.57
    _railing(rail, [(dx - e, dy - f + .6, zd), (dx - e, dy + f, zd), (dx + e, dy + f, zd), (dx + e, dy - f + .6, zd)],
             h=.9, post=.04, rail=.022, every=.8)
    a.part('Deck_kick', 'Team').box((2.5, .04, .12), loc=(dx, dy + f + .01, zd + .06), bevel=0)
    ladder(a.part('Ladder', 'Steel'), (dx + .7, yb + .12, top), zd + .9, 0.0, width=.44, step=.36, rung=.028)
    # Inclined launch rail, a drone ready at its top end.
    pitch = math.radians(28)
    d = Vector((0, -math.cos(pitch), math.sin(pitch)))
    nrm = Vector((0, math.sin(pitch), math.cos(pitch)))
    base = Vector((dx - .35, dy + 1.25, zd + .22))
    L = 2.5
    rot = (-pitch, 0, 0)
    a.part('Launch_rail', 'Team').box((.5, L, .1), loc=tuple(base + d * (L / 2)), rot=rot, bevel=.02, seg=1)
    for s in (-1, 1):
        p = base + d * (L / 2) + nrm * .07 + Vector((s * .17, 0, 0))
        a.part('Rail_tracks', 'Steel').box((.05, L, .05), loc=tuple(p), rot=rot, bevel=0)
    a.part('Rail_stripe', 'SafetyStripe').box((.52, .12, .11), loc=tuple(base + d * (L - .1)), rot=rot, bevel=0)
    frame = a.part('Rail_frame', 'Armor')
    hi = base + d * (L * .72)
    for s in (-1, 1):
        frame.limb((hi.x + s * .2, hi.y + .1, zd), (hi.x + s * .2, hi.y, hi.z - .06), .07, .07, bevel=0)
        frame.limb((base.x + s * .2, base.y, zd), (base.x + s * .2, base.y, base.z - .04), .07, .07, bevel=0)
    frame.box((.5, .12, .08), loc=(hi.x, hi.y, hi.z - .1), rot=rot, bevel=0)
    frame.box((.6, .3, .1), loc=(base.x, base.y + .1, zd + .05), bevel=0)                          # hinge block
    ready = base + d * (L - .55) + nrm * .12
    _quadcopter(a, _frame(tuple(ready), rot), k=1.6, full=False)
    a.part('Rail_cable', 'Rubber').tube([tuple(base + Vector((.3, 0, 0))), (dx + .35, dy + 1.0, zd + .03),
                                         (dx + .9, dy + .9, zd + .03)], .03, seg=4)
    for name in ('Muzzle_door_l', 'Muzzle_main'):
        a.pivot(name, tuple(ready + nrm * .1))
        a.pivots[name].rotation_euler = rot                                                     # -Y along the rail
    _drone_shelf(a, dx + .7, dy + .5, zd, tiers=(0.0, .5), k=1.3)

    # ---------------------------------------------------------------- ground control, power, stores
    gx, gy, gw, gd, gh = 2.85, .3, 1.25, 2.6, 1.25
    for sy in (-1, 1):
        a.part('Container_blocks', 'Concrete').box((gw + .1, .3, .12), loc=(gx, gy + sy * (gd / 2 - .3), top + .04),
                                                   bevel=.02, seg=1)
    zg = top + .1
    a.part('Container', 'Team').box((gw, gd, gh), loc=(gx, gy, zg + gh / 2), bevel=.04, seg=1)
    cf = a.part('Container_frame', 'Armor')
    for sx in (-1, 1):
        for sy in (-1, 1):
            cf.box((.1, .1, gh + .04), loc=(gx + sx * (gw / 2 - .03), gy + sy * (gd / 2 - .03), zg + gh / 2), bevel=0)
    for k in range(5):                                                                          # roof ribs
        cf.box((gw + .02, .05, .03), loc=(gx, gy - gd / 2 + .3 + k * (gd - .6) / 4, zg + gh + .01), bevel=0)
    a.part('Container_door', 'Armor').box((.7, .05, 1.0), loc=(gx, gy - gd / 2 - .01, zg + .55), bevel=.012, seg=1)
    a.part('Container_step', 'Steel').box((.8, .36, .05), loc=(gx, gy - gd / 2 - .2, top + .04), bevel=0)
    caged_lamp(a, '-y', (gx + .45, gy - gd / 2, zg + 1.05))
    for y in (-.5, .5):
        a.part('Container_windows', 'Glass').box((.05, .6, .34), loc=(gx + gw / 2 + .005, gy + y, zg + .78), bevel=0)
    a.part('Container_lit', 'Lamp').box((.05, .5, .26), loc=(gx + gw / 2 + .012, gy + .5, zg + .78), bevel=0)
    a.part('Aircon', 'Fuel').box((.7, .34, .6), loc=(gx, gy + gd / 2 + .15, zg + .6), bevel=.03, seg=1)
    a.part('Aircon_grille', 'Undercarriage').grille(.5, .4, loc=(gx, gy + gd / 2 + .33, zg + .6), rot=(0, 0, math.pi),
                                                    slats=4, depth=.04, thickness=.03)
    # Antenna mast on the container: panel antennas, a datalink dish, whips.
    mx_, my_ = gx, gy + .8
    zm = zg + gh + .02
    a.part('GCS_mast', 'Steel').cyl(.06, 2.6, loc=(mx_, my_, zm + 1.3), seg=8, bevel=0)
    a.part('GCS_mast', 'Steel').box((.3, .3, .06), loc=(mx_, my_, zm + .02), bevel=0)
    for yaw, z in ((-.6, zm + 1.6), (2.2, zm + 1.6)):
        n_, _t = _facing(yaw)
        a.part('GCS_arms', 'Armor').limb((mx_, my_, z), tuple(Vector((mx_, my_, z)) + n_ * .22), .04, .04, bevel=0)
        a.part('GCS_panels', 'Medical').box((.26, .08, .7), loc=tuple(Vector((mx_, my_, z)) + n_ * .27),
                                            rot=(0, 0, yaw), bevel=.02, seg=1)
    _dish_at(a.part('GCS_dish', 'Medical'), (mx_ - .12, my_ - .1, zm + 2.2), -.9, .32, .32, depth=.12, seg=12, tilt=.3)
    a.part('GCS_dish_feed', 'Armor').limb((mx_ - .2, my_ - .16, zm + 2.22), (mx_ - .45, my_ - .35, zm + 2.35), .03, .03,
                                          bevel=0)
    _antenna(a, None, mx_, my_, zm + 2.6, .7)
    _antenna(a, None, gx - .4, gy - 1.0, zg + gh + .02, 1.1)
    a.part('Cables', 'Rubber').tube([(gx - gw / 2, gy - .6, zg + .3), (1.95, -.4, top + .03), (1.2, -1.9, top + .03),
                                     (hx + dw + .3, y0_ - .1, top + .03)], .04, seg=5)
    generator(a, (2.85, -2.6, top), yaw=R90, size=(1.3, .7, .85), body='Armor', door='Team')
    a.part('Cables', 'Rubber').tube([(2.6, -1.95, top + .3), (2.55, -1.3, top + .03),
                                     (gx - .2, gy - gd / 2 - .05, top + .03)], .035, seg=5)
    # Sandbags at the front left, battery crates and a drone on a trolley by the door, drums, tufts.
    bags = a.part('Sandbags', 'Sandbag')
    for course in range(2):
        bag_run(bags, rng, (-3.45, -2.4), (-3.45, -3.35), top + .12 + course * .22, (.62, .34, .24), half=course == 1)
        bag_run(bags, rng, (-3.45, -3.35), (-2.45, -3.35), top + .12 + course * .22, (.62, .34, .24), half=course == 0)
    crate(a, (hx + 1.85, -3.35, top), size=(.7, .4, .32), yaw=.25)
    crate(a, (hx + 1.88, -3.33, top + .32), size=(.66, .38, .3), yaw=.3, band=False)
    cart = a.part('Trolley', 'Steel')
    tx_, ty_ = hx - .4, -3.3
    cart.box((.7, .9, .05), loc=(tx_, ty_, top + .5), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cart.box((.04, .04, .4), loc=(tx_ + sx * .3, ty_ + sy * .4, top + .28), bevel=0)
            a.part('Trolley_wheels', 'Rubber').cyl(.07, .05, loc=(tx_ + sx * .3, ty_ + sy * .4, top + .07), rot=ACROSS,
                                                   seg=8, bevel=0)
    cart.tube([(tx_ - .3, ty_ + .45, top + .52), (tx_ - .3, ty_ + .62, top + .95), (tx_ + .3, ty_ + .62, top + .95),
               (tx_ + .3, ty_ + .45, top + .52)], .02, seg=4)
    _quadcopter(a, _frame((tx_, ty_, top + .53), (0, 0, .3)), k=1.2, full=False)
    for x, y in ((-3.3, 2.9), (-2.8, 3.3)):
        a.part('Drums', 'BarrelRed').cyl(.26, .84, loc=(x, y, top + .42), seg=12, bevel=.02, bseg=1)
        a.part('Drum_rims', 'Steel').cyl(.27, .04, loc=(x, y, top + .6), seg=12, bevel=0)
    hazard_sign(a, (2.05, -3.6, top), yaw=-.2, size=.44, height=.9)
    for k, (x, y) in enumerate(((-3.6, 1.2), (-3.5, -1.0), (3.6, 2.6), (1.5, 3.4), (-1.0, 3.5), (3.5, -1.4))):
        _tuft(a.part('Tufts', 'Grass', flat=True), x, y, top - .02, .16, k * 1.3)


# ----------------------------------------------------------------------------- dragons_teeth
def _hedgehog(a, loc, yaw, length=1.45, flange=.1, t=.022):
    """Czech hedgehog: three steel angle beams crossed at right angles through one centre, standing on three
    ends with the cube diagonal vertical; `yaw` turns it (one foot points along +Y at yaw 0)."""
    turn = Vector((1, 1, 1)).normalized().rotation_difference(Vector((0, 0, 1))).to_matrix()
    spin = Matrix.Rotation(yaw, 3, 'Z')
    c = Vector(loc)
    lift = length / 2 / math.sqrt(3)
    part = a.part('Hedgehogs', 'Rust')
    for axis in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))):
        d = spin @ turn @ axis
        p0, p1 = c + Vector((0, 0, lift)) - d * length / 2, c + Vector((0, 0, lift)) + d * length / 2
        side = d.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = d.cross(side).normalized()
        rot = Matrix((side, up, d)).transposed().to_euler('XYZ')                            # X side, Y up, Z beam
        mid = (p0 + p1) / 2
        part.box((flange, t, length), loc=tuple(mid + side * (flange / 2 - t / 2)), rot=rot, bevel=0)
        part.box((t, flange, length), loc=tuple(mid + up * (flange / 2 - t / 2)), rot=rot, bevel=0)
    a.part('Hedgehog_plates', 'Steel').box((.16, .16, .16), loc=tuple(c + Vector((0, 0, lift))), rot=(.6, .6, yaw),
                                           bevel=0)


def dragons_teeth(a):
    """Dragon's teeth (5 x 2.5 m, 1.2 m): two staggered rows of weathered concrete truncated pyramids on a
    half-buried footing, the back row taller, one tooth broken off with rusty rebar and rubble, a Czech
    hedgehog in front of the front row, moss and grass at the bases and Team marker stakes at the two ends.
    Rows repeat every 5 m along X (teeth 1.667 m apart in each row, the rows half a pitch apart), so
    segments laid end to end continue the pattern."""
    rng = random.Random(366)
    a.part('Footing', 'Concrete').box((5.0, 2.3, .14), loc=(0, 0, 0), bevel=.03, seg=1)             # z -.07 .. .07
    teeth = a.part('Teeth', 'Concrete')
    a.part('Footing_dirt', 'Dirt').box((5.0, 2.44, .08), loc=(0, 0, -.02), bevel=.03, seg=1)
    rows = ((-.42, (-2.083, -.417, 1.25), .86, .82), (.55, (-1.25, .417, 2.083), .92, 1.06))
    for y, xs, b, h in rows:
        for x in xs:
            broken = (x, y) == (-1.25, .55)
            hh = .62 if broken else h + rng.uniform(-.06, .05)
            tp = (.6 if broken else .4) + rng.uniform(-.03, .03)
            teeth.box((b, b, hh), loc=(x + rng.uniform(-.04, .04), y + rng.uniform(-.04, .04), .05 + hh / 2),
                      rot=(rng.uniform(-.025, .025), rng.uniform(-.025, .025), rng.uniform(-.14, .14)), bevel=.05,
                      seg=2,
                      taper=(tp, tp), shift=(rng.uniform(-.04, .04), rng.uniform(-.04, .04)))
            if broken:
                bar = a.part('Rebar', 'Rust')
                for dx, dy, lean in ((-.08, .06, .25), (.1, -.05, -.3), (.02, .12, .1)):
                    bar.cyl(.014, .3, loc=(x + dx, y + dy, .05 + hh + .1), rot=(lean, lean * .6, 0), seg=4, bevel=0)
                rub = a.part('Rubble', 'Concrete', flat=True)
                for k, (dx, dy, s) in enumerate(((.55, -.2, .14), (.62, .15, .1), (-.5, -.35, .12), (.35, .5, .09))):
                    rub.ico((s, s * .8, s * .6), loc=(x + dx, y + dy, .07), sub=0, jitter=.3, seed=k + 2.0)
    _hedgehog(a, (.417, -.72, .07), .3, length=1.35)
    moss = a.part('Moss', 'FoliageDark', flat=True)
    grass = a.part('Tufts', 'Grass', flat=True)
    for k in range(14):
        y, xs, b, h = rows[k % 2]
        x = xs[k % 3] + rng.uniform(-.45, .45)
        yy = y + (b / 2 + .06) * (1 if k % 3 else -1)
        _tuft(grass, x, yy, .04, rng.uniform(.12, .17), k * 1.1)
    for k, (x, y) in enumerate(((-1.7, .0), (1.0, .1), (2.2, -.9), (-2.3, 1.0), (-.2, .95), (1.7, .95), (-1.2, -.95))):
        moss.ico((.24, .17, .035), loc=(x, y, .07), sub=1, jitter=.35, seed=k * 1.7)
    for k, (x, y, z) in enumerate(((-2.083, -.42, .3), (.417, .55, .45), (2.083, .55, .25), (1.25, -.42, .2))):
        moss.ico((.2, .12, .12), loc=(x + .28, y - .22, z), sub=1, jitter=.3, seed=k * 3.1)          # moss on faces
    for x, y in ((2.35, 1.0), (-2.35, -1.0)):                                                 # marker stakes
        a.part('Stakes', 'Wood').box((.06, .06, 1.2), loc=(x, y, .6), rot=(.03, -.02, .3), bevel=0)
        a.part('Stake_bands', 'Team').box((.08, .08, .26), loc=(x + .012, y, 1.05), rot=(.03, -.02, .3), bevel=0)
        a.part('Stake_reflectors', 'PlasterWhite').box((.075, .075, .06), loc=(x + .008, y, .84), rot=(.03, -.02, .3),
                                                       bevel=0)


# ----------------------------------------------------------------------------- minefield
def _mine_sign(a, loc, yaw, s=.42):
    """Red triangular "MINES" sign, point down, facing (sin yaw, -cos yaw): a white-edged red plate with a
    white skull (dark eye holes) and a white text bar; loc is the centre of the plate."""
    n, t = _facing(yaw)
    c = Vector(loc)
    rot = (0, 0, yaw)
    h = s * math.sqrt(3) / 2

    def tri(k):
        return [(-s * k / 2, h * k / 3), (s * k / 2, h * k / 3), (0, -h * k * 2 / 3)]
    for name, mat, k, off in (('Sign_edges', 'PlasterWhite', 1.14, .0), ('Sign_plates', 'BarrelRed', 1.0, .012)):
        prof = tri(k)
        a.part(name, mat).prism([(p[0], p[1]) for p in prof], .02, loc=tuple(c + n * off), rot=(R90, 0, yaw + math.pi),
                                axis='Z', bevel=0)
    white = a.part('Sign_marks', 'PlasterWhite')
    white.cyl(s * .13, .02, loc=tuple(c + n * .03 + Vector((0, 0, -h * .08))), rot=(R90, 0, yaw), seg=8, bevel=0)
    white.box((s * .16, .02, s * .08), loc=tuple(c + n * .03 + Vector((0, 0, -h * .08 - s * .15))), rot=rot, bevel=0)
    white.box((s * .6, .02, s * .07), loc=tuple(c + n * .03 + Vector((0, 0, h * .2))), rot=rot, bevel=0)
    dark = a.part('Sign_eyes', 'Charred')
    for sx in (-1, 1):
        dark.box((s * .05, .02, s * .05), loc=tuple(c + n * .042 + t * (sx * s * .045) + Vector((0, 0, -h * .06))),
                 rot=rot, bevel=0)


def _at_mine(a, x, y, r=.17, seed=0.0):
    """Half-buried anti-tank mine in a scuffed ring of earth (mb_support.mine without the owner light)."""
    seg = 10
    verts, faces = [], []
    rings = ((r * .9, .05), (r * 1.4, .06), (r * 2.1, .025), (r * 2.7, -.01))
    for rr, z in rings:
        for i in range(seg):
            u = i * TAU / seg
            nz = noise.noise(Vector((math.cos(u) * 1.7 + seed, math.sin(u) * 1.7, rr * 3)))
            k = (1 + .14 * nz) if rr > r else 1
            verts.append((x + rr * k * math.cos(u), y + rr * k * math.sin(u), z + (.012 * nz if 0 < z < .06 else 0)))
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            faces.append((k * seg + i, (k + 1) * seg + i, (k + 1) * seg + j, k * seg + j))
    a.part('Mine_earth', 'Dirt', flat=True).mesh(verts, faces)
    a.part('Mine_bodies', 'Crate').cyl(r, .09, loc=(x, y, .02), seg=seg, bevel=.01, bseg=1)
    a.part('Mine_plates', 'Steel').cyl(r * .55, .025, loc=(x, y, .07), seg=8, bevel=0)
    a.part('Mine_fuzes', 'Armor').cyl(r * .2, .025, loc=(x, y, .09), seg=6, bevel=0)


def minefield(a):
    """Marked minefield (4.9 x 4.9 m, 1 m): a patch of turned earth fenced with log corner posts and steel
    pickets, two strands of barbed wire and a red-and-white warning tape, red triangular skull "MINES"
    signs on the corner posts and on the wire, four half-buried anti-tank mines in scuffed earth, a stake
    mine with its tripwire, fresh mounds and grass."""
    rng = random.Random(377)
    # Ground: a slightly bumpy earth patch (a grid, so the baked shading has interior vertices).
    nx = 8
    e = 2.4
    verts, faces = [], []
    for j in range(nx + 1):
        for i in range(nx + 1):
            x, y = -e + 2 * e * i / nx, -e + 2 * e * j / nx
            edge = i in (0, nx) or j in (0, nx)
            if not edge:
                x += .08 * noise.noise(Vector((x, y, 3.0)))
                y += .08 * noise.noise(Vector((x, y, 5.0)))
            z = -.01 if edge else .012 + .012 * noise.noise(Vector((x * 1.3, y * 1.3, 1.0)))
            verts.append((x, y, z))
    for j in range(nx):
        for i in range(nx):
            k = j * (nx + 1) + i
            faces.append((k, k + 1, k + nx + 2, k + nx + 1))
    a.part('Ground', 'Dirt').mesh(verts, faces)
    # Fence: log posts at the corners, pickets between, two barbed-wire strands and the tape.
    c = 2.2
    corners = [(-c, -c), (c, -c), (c, c), (-c, c)]
    posts = []
    for (x0, y0), (x1, y1) in zip(corners, corners[1:] + corners[:1]):
        for k in range(4):
            posts.append((x0 + (x1 - x0) * k / 4, y0 + (y1 - y0) * k / 4, k == 0))
    for x, y, corner in posts:
        if corner:
            a.part('Posts', 'LogWood').cyl(.055, 1.05, loc=(x, y, .5), seg=6, bevel=0)
        else:
            lean = (rng.uniform(-.05, .05), rng.uniform(-.05, .05), rng.uniform(0, 1))
            a.part('Pickets', 'Rust').box((.045, .045, .82), loc=(x, y, .39), rot=lean, bevel=0)
    wire = a.part('Barbed_wire', 'Steel')
    for z in (.3, .6):
        pts = []
        for i, (x, y, _) in enumerate(posts):
            q = posts[(i + 1) % len(posts)]
            pts += [(x, y, z), ((x + q[0]) / 2, (y + q[1]) / 2, z - .03)]
        pts.append(pts[0])
        wire.tube(pts, .009, seg=3, caps=False)
    for i, (x, y, _) in enumerate(posts):                                                       # barbs
        q = posts[(i + 1) % len(posts)]
        for f in (.33, .66):
            p = Vector((x + (q[0] - x) * f, y + (q[1] - y) * f, .6 - .02))
            wire.box((.07, .012, .012), loc=tuple(p), rot=(0, .8, math.atan2(q[1] - y, q[0] - x) + .8), bevel=0)
    for i, (x, y, _) in enumerate(posts):                                                       # warning tape
        q = posts[(i + 1) % len(posts)]
        p, d = Vector((x, y)), Vector((q[0] - x, q[1] - y))
        m = (p + d / 2)
        a.part('Tape_red' if i % 2 else 'Tape_white', 'BarrelRed' if i % 2 else 'PlasterWhite').box(
            (d.length + .02, .012, .06), loc=(m.x, m.y, .8), rot=(0, 0, math.atan2(d.y, d.x)), bevel=0)
    # Signs: on the corner posts, facing out across the corner, and hung on the wire mid-side.
    for x, y in corners:
        yaw = math.atan2(x, -y)                                                                 # facing (x, y) out
        n_, _t = _facing(yaw)
        _mine_sign(a, tuple(Vector((x, y, .9)) + n_ * .08), yaw, s=.42)
    for x, y, yaw in ((0, -c, 0.0), (c, .5, R90), (-.4, c, math.pi), (-c, -.6, -R90)):
        n_, _t = _facing(yaw)
        _mine_sign(a, tuple(Vector((x, y, .55)) + n_ * .03), yaw, s=.3)
    # Mines, a stake mine with its tripwire, mounds and grass.
    for k, (x, y) in enumerate(((-1.1, -.9), (.9, -1.2), (.4, .8), (-1.2, 1.1))):
        _at_mine(a, x + rng.uniform(-.1, .1), y + rng.uniform(-.1, .1), seed=k * 1.3)
    sx, sy = 1.3, .2
    a.part('Stake_mine_post', 'Wood').box((.05, .05, .42), loc=(sx, sy, .2), rot=(.05, 0, .4), bevel=0)
    a.part('Stake_mine', 'Armor').cyl(.045, .15, loc=(sx + .01, sy, .48), seg=8, bevel=0)
    a.part('Stake_mine_fuze', 'Steel').cyl(.018, .06, loc=(sx + .01, sy, .58), seg=6, bevel=0)
    a.part('Tripwire', 'Steel').tube([(sx + .01, sy, .58), (sx - .8, sy + .5, .1), (sx - .82, sy + .5, .02)], .006,
                                     seg=3)
    a.part('Tripwire_peg', 'Wood').box((.03, .03, .16), loc=(sx - .82, sy + .5, .06), bevel=0)
    mound = a.part('Mounds', 'Dirt', flat=True)
    for k, (x, y) in enumerate(((-.3, -.2), (1.4, 1.5), (-1.7, .0))):
        mound.ico((.3, .24, .07), loc=(x, y, .0), sub=1, jitter=.3, seed=k * 2.3)
    for k in range(7):
        u = k * .95 + .3
        r = 1.2 + .8 * ((k * 37) % 10) / 10
        _tuft(a.part('Tufts', 'Grass', flat=True), r * math.cos(u), r * math.sin(u), .0, .12, k * 1.9)
    for k, (x, y) in enumerate(((2.3, -1.2), (-2.3, 1.6), (1.0, 2.3), (-1.6, -2.3))):
        _tuft(a.part('Tufts_dry', 'FoliageLight', flat=True), x, y, -.02, .13, k * 2.9)


BUILDERS = {
    'ew_tower': (ew_tower, dict(ao_distance=.7, grime_height=.6)),
    'atgm_tower': (_runtime_names(atgm_tower), dict(ao_distance=.8, grime_height=.6)),
    'c_ram': (c_ram, dict(ao_distance=.7, grime_height=.5)),
    'gun_pit': (gun_pit, dict(ao_distance=.8, grime_height=.5)),
    'drone_hangar': (drone_hangar, dict(ao_distance=.9, grime_height=.6)),
    'dragons_teeth': (dragons_teeth, dict(ao_distance=.5, grime_height=.4)),
    'minefield': (minefield, dict(ao_distance=.3, grime_height=.2)),
}
