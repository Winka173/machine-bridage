"""Machine Brigade phase 2 models, built with frontier_kit and the mb_vehicles* / mb_new_trucks / mb_siege /
mb_fortress helpers: a wheeled command post, a wheeled tank hunter, a counter-battery radar truck, a long-range
SAM launcher and the camp headquarters.

  * command_vehicle: 8x8 armoured command post (Stryker CV / BTR-80 KShM / LAV-C2 lineage), 7.4 m hull, no
    turret. A boat nose with hinged armoured windscreen shutters, and a raised command box over the rear
    two-thirds (the stepped silhouette that tells it from the APC); on the box a folded telescopic mast with
    its sensor head, a SATCOM dome, a small link dish, an air-recognition panel and two tall whips; two more
    whips bent forward and tied down to the nose. Side bins, a rolled tent on the left flank, an APU at the
    rear. The heavy machine gun on the commander's cupola turns on `Mount_mg`, `Muzzle_mg` at its flash
    hider (root > Mount_mg > Muzzle_mg).
  * wheeled_gun: 8x8 wheeled tank destroyer (Centauro B1 / M1128 MGS / Rooikat lineage), 7.6 m hull: a low
    wide hull with the engine deck at the front, and a low angular `Turret` a little ahead of the middle
    with a long 105 mm gun overhanging the nose: `Main_cannon` (thermal sleeve, fume extractor) and
    `Muzzle_brake` (multi-baffle) recoil, `Muzzle_main` at the brake exit. Coaxial MG right of the mantlet
    (`Coax`, `Muzzle_coax`); commander's MG on the turret roof (`Mount_mg` / `Muzzle_mg`, child of Turret).
  * counter_battery_radar: 6x6 truck (AN/TPQ-53 / Zoopark-1 / COBRA lineage), 8 m: cab-over cab with the
    roof MG (`Mount_mg` / `Muzzle_mg`), an equipment shelter, an under-slung generator, four stabiliser jacks
    and at the rear a big flat AESA face tilted back 20 degrees on a turntable; everything above the
    turntable spins on `Radar` (about Z).
  * long_sam: heavy 8x8 transporter-erector-launcher (S-300PMU 5P85 / S-400 lineage), 11 m: the split crew
    cabs of a MAZ-543 chassis either side of the engine, four 8 m missile canisters side by side on an
    erector, stabiliser jacks and a folded radar mast. The canisters (`Launcher*` parts) lie along the truck
    pointing forward, raised 4 degrees, on `Turret`, which the game yaws; ModelLibrary elevates the
    Launcher group about its rear trunnion. `Muzzle_missile`, `Muzzle_missile.001` .. `.003` sit at the
    four canister mouths, left to right (Blender +X is the vehicle's left), each carrying a small
    `Launch_tubes` cap mesh so AddLaunchPoints finds one launch point per canister; `Muzzle_main` marks the
    middle of the mouths for the elevation rig.
  * headquarters: the camp HQ (14 m wide on X, 12 m deep on Y, roof 5.4 m): a two-storey fortified
    concrete command block with Team fascia bands and shutters, a hardened entrance with a blast door, a
    single-storey signals wing whose roof is a helipad with a big H and edge lights, HESCO walls, a flag
    mast, antennas, a radar dish spinning on `Radar` and floodlights. On the main roof a twin heavy gun
    `Turret`: `Main_cannon` (left) / `Main_cannon_2` (right) and `Muzzle_brake` / `Muzzle_brake_2` recoil,
    `Muzzle_main` at the left bore and `Muzzle_main.001` at the right one, a ball-mounted `Coax` between
    them (`Muzzle_coax`); at the rear left corner a twin 30 mm flak mount in a sandbag nest on `Mount_mg`
    with `Muzzle_mg` (left barrel) and `Muzzle_mg.001` (right barrel).

Rig (ModelLibrary.cs, VehicleView.cs): `Turret` yaws; its children named main_cannon*, muzzle_brake*,
launcher*, coax*, muzzle_main*, muzzle_missile* ... elevate on a pivot the game puts at the back of their
bounds (6 % of their length from the rear, 30 % of their height up); Main_cannon* / Muzzle_brake* also
recoil, and twin barrels (Main_cannon, Main_cannon_2) fire in turn, each from its own tip. `Mount_<slot>`
pivots turn on their own (only secondary mounts, data index 1 and up), `Radar` spins. A slot's k-th mount in
the data takes the k-th `Muzzle_<slot>` in name order; launchers (the `Launch_tubes` caps) are used in turn
by one mount.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front and +X the vehicle's left,
origin on the ground at the footprint centre, wheels touching z = 0. Every muzzle empty sits at the bore
end of its barrel, on the bore axis, under the pivot that moves that barrel; at rest every bore points
along -Y. Each gun is the highest thing inside its sweep. Touching parts overlap or stand at least 1 cm
apart, never face to face (coplanar faces z-fight).

Pivots that the game pairs by slot take a numeric suffix (`Muzzle_mg.001`); they are authored as
`Muzzle_mg__001` (frontier_kit refuses runtime names with a dot) and renamed when the asset finishes, both
under build_assets.py (which calls asset.finish() itself) and under this module's own main.

Headless: blender --background --python Tools/blender/build_assets.py -- command_vehicle
     or:  blender --background --python Tools/blender/mb_phase2.py -- [--out DIR] [names...]
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mb_weapons as wpn  # noqa: E402
from frontier_kit import chamfered  # noqa: E402
from mb_fortress import _jersey  # noqa: E402
from mb_new_trucks import _fuel_tank, _ladder, _mirror, _plate_frame, _side_window, _stripe_band, _wiper  # noqa: E402
from mb_siege import _circle, bag_arc, bag_run, caged_lamp, flag, flood_head, generator, lattice, loop_rail  # noqa: E402
from mb_support import _beacon, _ram, _whip  # noqa: E402
from mb_town import fbox, slide  # noqa: E402
from mb_themes import ladder, rim  # noqa: E402
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _cable, _dish, _flank, _frame, _glacis,  # noqa: E402
                         _grille_frame, _hatch, _headlight, _hull_section, _jerrycans, _periscopes, _roll,
                         _smoke, _stowage_bin, _taillight, _wheel)
from mb_vehicles2 import _axis, _gun  # noqa: E402
from mb_vehicles3 import _at, _jack  # noqa: E402

TAU = math.tau
BACKWARD = (-R90, 0, 0)   # cylinder axis along Y, local +Z -> +Y


# ----------------------------------------------------------------------------- rig helpers
def dotted(name):
    """Kit-safe spelling of a suffixed runtime name: 'Muzzle_mg.001' -> 'Muzzle_mg__001'."""
    return name.replace('.', '__')


def _suffixed(a):
    """Wrap a.finish so the plain `asset.finish()` of build_assets.py also renames suffixed pivots
    (Muzzle_mg__001 -> Muzzle_mg.001) once the kit's duplicate-name check has passed. Idempotent, so
    mb_round6.finish (this module's main) can run its own rename afterwards."""
    base = a.finish

    def finish():
        base()
        for o in list(a.collection.objects):
            if '__' in o.name:
                want = o.name.replace('__', '.')
                o.name = want
                if o.name != want:
                    raise ValueError(f'{a.name}: could not name {want} (got {o.name})')
        return a
    a.finish = finish


def _tied_whip(a, base, tie, rise, parent=None, r=.014):
    """Whip antenna bent over and tied down: from a spring base at `base` it climbs `rise`, arcs forward and
    ends in a clip at `tie` (the classic look of a command vehicle's radio whips)."""
    b, t = Vector(base), Vector(tie)
    p1 = b + Vector((0, 0, rise))
    p2 = Vector((t.x, t.y + (b.y - t.y) * .25, b.z + rise * .95))
    pts = []
    for k in range(13):
        u = k / 12
        pts.append(tuple(b * (1 - u) ** 3 + p1 * 3 * u * (1 - u) ** 2 + p2 * 3 * u * u * (1 - u) + t * u ** 3))
    steel = a.part('Whips', 'Steel', parent)
    steel.cyl(.04, .14, loc=(b.x, b.y, b.z + .06), seg=6, bevel=0)                          # spring base
    steel.tube([(b.x, b.y, b.z + .1)] + pts[1:], r, seg=4)
    a.part('Whip_clips', 'Armor', parent).box((.08, .06, .07), loc=(t.x, t.y, t.z - .02), bevel=0)


# ----------------------------------------------------------------------------- command_vehicle
CV_AXLES = (-2.6, -1.42, .98, 2.16)


def command_vehicle(a):
    """8x8 armoured command post (Stryker CV / BTR-80 KShM / LAV-C2 lineage), 7.4 x 2.9 m, hull 2.62 m: a boat
    nose whose upper glacis carries two armoured windscreens under propped-open shutters, a flat front
    roof with the driver's hatch and the commander's cupola, and a raised command box over the rear
    two-thirds. On the box: a folded telescopic mast lying back along its left side with the sensor head
    (camera ball and a small radar panel) on a rest at the rear, a SATCOM dome, a link dish, an orange
    air-recognition panel, a mast control box, and two tall whips at the rear corners; two whips from the
    box's front corners are bent forward and tied down to the nose. Flanks: side bins and a crew door
    between the axles, a rolled tent on the left upper flank, a tow cable; rear: a door, an APU with its
    exhaust, lights and jerrycans. The cupola's heavy machine gun turns on `Mount_mg` (`Muzzle_mg`)."""
    _suffixed(a)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in CV_AXLES:
        for s in (-1, 1):
            _wheel(a, s * 1.18, y, .55, .44)
            dark.box((.3, .22, .16), loc=(s * .92, y, .55), bevel=.02, seg=1)                  # hub carriers
    full = (.5, 1.0, 1.35, 2.0, .85, 1.26, 1.3, 1.06)
    hull.loft([
        _hull_section(-3.72, .9, .95, 1.0, 1.06, .6, .74, .76, .68),
        _hull_section(-3.35, .55, 1.0, 1.25, 1.45, .82, 1.18, 1.22, 1.0),
        _hull_section(-2.35, *full),
        _hull_section(3.5, *full),
        _hull_section(3.72, .62, 1.02, 1.33, 1.94, .8, 1.2, 1.24, 1.0),
    ], bevel=.06, seg=2)
    G0, G1 = (-3.35, 1.45), (-2.35, 2.0)                                                   # upper glacis
    wr = _glacis(G0, G1, 0, 0)[2]
    L = math.hypot(G1[0] - G0[0], G1[1] - G0[1])
    # Windscreens: armoured panes in frames, their shutters hinged at the top and propped open.
    for s in (-1, 1):
        x = s * .44
        y, z, _ = _glacis(G0, G1, .5, .015)
        a.part('Windows', 'Glass').box((.56, .34, .04), loc=(x, y, z), rot=(wr, 0, 0), bevel=.01, seg=1)
        fr = a.part('Window_frames', 'Armor')
        for dt in (-.23, .23):
            fy, fz, _ = _glacis(G0, G1, .5 + dt / L, .03)
            fr.box((.7, .08, .06), loc=(x, fy, fz), rot=(wr, 0, 0), bevel=0)
        for dx in (-.32, .32):
            fy, fz, _ = _glacis(G0, G1, .5, .03)
            fr.box((.08, .38, .06), loc=(x + dx, fy, fz), rot=(wr, 0, 0), bevel=0)
        hy, hz, _ = _glacis(G0, G1, .5 + .27 / L, .05)                                     # hinge line
        down = Vector((0, -math.cos(wr), -math.sin(wr)))
        out = Vector((0, -math.sin(wr), math.cos(wr)))
        theta = math.radians(105)
        d = down * math.cos(theta) + out * math.sin(theta)
        c = Vector((x, hy, hz)) + d * .21
        armor.box((.66, .42, .05), loc=tuple(c), rot=(math.atan2(d.z, d.y) - R90, 0, 0), bevel=.01, seg=1)
        steel.cyl(.025, .6, loc=(x, hy, hz), rot=ACROSS, seg=6, bevel=0)                    # hinge pin
        # Prop arm from the frame to the shutter's edge.
        steel.tube([(x + s * .3, *_glacis(G0, G1, .5 - .1 / L, .04)[:2]), tuple(c + d * .15 + Vector((s * .3, 0, 0)))],
                   .012, seg=4)
        hy, hz, _ = _glacis(G0, G1, .06, 0)
        _headlight(a, s * .7, hy - .06, hz + .1)
        steel.box((.12, .2, .12), loc=(s * .45, -3.62, .86), bevel=.02, seg=1)             # tow hooks
    # Splash board across the nose edge, tie-down clips for the whips.
    by, bz, _ = _glacis(G0, G1, .16, .03)
    armor.box((1.9, .05, .16), loc=(0, by, bz), rot=(wr - 1.1, 0, 0), bevel=.012, seg=1)
    # Front roof: driver's hatch with vision blocks, the commander's cupola (the MG turns on it), a grille.
    zr = 2.0
    _hatch(a, .52, -1.98, zr, .26)
    _periscopes(a, [(.52 + dx, -2.28, zr - .02, 0) for dx in (-.16, 0, .16)])
    cx, cy = -.45, -1.55
    armor.cyl(.44, .16, loc=(cx, cy, zr + .06), seg=16, bevel=.03, bseg=1)                 # cupola ring
    _periscopes(a, [(cx + math.cos(u) * .45, cy + math.sin(u) * .45, zr + .02, u + R90)
                    for u in (-R90 - .75, -R90, -R90 + .75, R90 + .6)])
    wpn.hmg(a, (cx, cy, zr + .13), post=.2, length=.9, ammo=1)
    a.part('Deck', 'Undercarriage').grille(.66, .6, loc=(.5, -1.0, zr + .01), rot=(-R90, 0, 0), slats=5, depth=.06,
                                           thickness=.04)
    _grille_frame(a, .5, -1.0, zr - .01, .66, .6, t=.04)

    # Command box over the rear two-thirds.
    bz0, bz1, by0, by1 = 1.95, 2.62, -.32, 3.52
    hull.box((2.02, by1 - by0, bz1 - bz0), loc=(0, (by0 + by1) / 2, (bz0 + bz1) / 2), bevel=.06, seg=2,
             taper=(.95, .98))
    top = bz1
    for s in (-1, 1):
        _periscopes(a, [(s * .95, y, 2.26, s * R90) for y in (.3, 1.4, 2.5)])
        _stowage_bin(a, (s * .72, -.54, zr - .01), (.5, .36, .3), latch_side=0)             # map boxes
    armor.box((1.0, .06, .5), loc=(0, by0 - .02, 2.3), bevel=.015, seg=1)                  # front access panel
    # Folded telescopic mast on the left: a hinge block at the front, three sections back to a rest,
    # the sensor head lying on the rest over the rear.
    mx = .55
    armor.box((.4, .46, .26), loc=(mx, .02, top + .12), bevel=.03, seg=1)                   # hinge block
    steel.cyl(.06, .5, loc=(mx, .1, top + .28), rot=ACROSS, seg=8, bevel=0)                 # hinge pin
    zm = top + .3
    mast = a.part('Mast', 'Steel')
    fit = a.part('Mast_fittings', 'Armor')
    y = .12
    for r, ln in ((.11, 1.05), (.09, .95), (.075, .8)):
        mast.cyl(r, ln + .04, loc=(mx, y + ln / 2, zm), rot=FORWARD, seg=10, bevel=0)
        fit.cyl(r + .025, .07, loc=(mx, y + ln - .04, zm), rot=FORWARD, seg=10, bevel=0)
        y += ln
    _ram(a, (mx, .3, top + .1), (mx, .95, zm - .09), .04)
    for dx in (-.16, .16):                                                                  # rest
        steel.box((.05, .05, .2), loc=(mx + dx, 2.55, top + .1), bevel=0)
    steel.box((.4, .08, .05), loc=(mx, 2.55, top + .2), bevel=0)
    head = a.part('Sensor_head', 'Armor')
    hy = y + .22
    head.box((.44, .5, .36), loc=(mx, hy, zm + .02), bevel=.04, seg=1)
    a.part('Sensor_glass', 'Glass').box((.3, .04, .18), loc=(mx, hy - .26, zm + .04), bevel=.01, seg=1)
    a.part('Sensor_ball', 'Armor').sphere(.15, loc=(mx, hy + .1, zm + .34), seg=12, rings=8)
    a.part('Sensor_glass', 'Glass').box((.12, .06, .1), loc=(mx, hy - .03, zm + .36), bevel=0)
    a.part('Radar_panel', 'Fuel').box((.62, .08, .4), loc=(mx - .02, hy + .34, zm + .08), rot=(-.3, 0, 0), bevel=.02,
                                      seg=1)
    a.part('Mast_cable', 'Undercarriage').tube([(mx - .12, .2, top + .02), (mx - .16, 1.2, top + .05),
                                                (mx - .16, 2.2, top + .05), (mx - .1, hy - .2, zm - .1)], .025, seg=5)
    # SATCOM dome and a link dish on the right, the recognition panel and control box between them.
    sx, sy = -.52, 2.6
    armor.cyl(.36, .08, loc=(sx, sy, top + .03), seg=16, bevel=.015, bseg=1)
    a.part('Satcom', 'Medical').sphere((.33, .33, .27), loc=(sx, sy, top + .07), seg=16, rings=8, cut=0)
    steel.cyl(.05, .3, loc=(-.55, .45, top + .15), seg=8, bevel=0)                          # dish post
    steel.box((.12, .12, .14), loc=(-.55, .5, top + .32), bevel=0)
    _dish(a.part('Link_dish', 'Medical'), (-.55, .45, top + .48), .28, .28, depth=.11, seg=12, tilt=.6)
    a.part('Recognition_panel', 'BarrelRed').box((.78, 1.1, .025), loc=(-.4, 1.45, top + .002), bevel=0)
    straps = a.part('Panel_straps', 'Charred')
    for y in (1.05, 1.85):
        straps.box((.82, .05, .03), loc=(-.4, y, top + .006), bevel=0)
    _stowage_bin(a, (-.52, -.02, top - .01), (.62, .36, .22), latch_side=0)                  # mast control box
    # Whips: two tall at the rear corners, two bent forward and tied to the nose.
    for s in (-1, 1):
        _antenna(a, None, s * .88, 3.3, top, 2.9 if s > 0 else 2.4)
        _tied_whip(a, (s * .9, -.16, top), (s * .62, -3.46, 1.2), 1.1)
    _whip(a, -.9, 1.0, top, .9)

    # Flanks: side bins between the middle axles on the left, a crew door on the right; the tent roll on the
    # left upper flank; a tow cable on the right.
    fx, fz, lean = _flank((1.3, 1.35), (1.06, 2.0), .5, .12)
    _roll(a, (fx, 1.2, fz), 2.6, r=.13, axis='y')
    for y in (.3, 2.1):
        steel.box((.05, .06, .3), loc=(1.21, y, 1.62), rot=(0, -lean, 0), bevel=0)          # roll brackets
    for y in (-.62, .2):
        _stowage_bin(a, (1.36, y, .96), (.16, .72, .34), latch_side=1)
    armor.box((.06, .9, .88), loc=(-1.31, -.22, 1.38), bevel=.015, seg=1)                   # crew door
    steel.box((.06, .16, .05), loc=(-1.35, -.52, 1.4), bevel=0)
    for dz in (-.3, .3):
        steel.box((.08, .1, .12), loc=(-1.34, .2, 1.38 + dz), bevel=0)                      # hinges
    steel.box((.3, .26, .04), loc=(-1.2, -.22, .82), bevel=0)                               # step
    _cable(a, [(-1.08, -2.2, 1.99), (-1.08, -.5, 1.99), (-1.06, 3.3, 1.96)])
    # Rear: door, APU with its grille and exhaust, lights, jerrycans, step.
    armor.box((.86, .08, 1.02), loc=(.25, 3.73, 1.36), bevel=.02, seg=1)
    steel.box((.26, .05, .05), loc=(.5, 3.78, 1.4), bevel=0)
    for dz in (-.36, .36):
        steel.box((.1, .08, .12), loc=(-.12, 3.77, 1.36 + dz), bevel=0)
    apu = a.part('APU', 'Armor')
    apu.box((.66, .42, .6), loc=(-.78, 3.9, 1.3), bevel=.03, seg=1)
    dark.grille(.44, .36, loc=(-.78, 4.12, 1.32), rot=(0, 0, math.pi), slats=4, depth=.05, thickness=.035)
    steel.cyl(.05, .45, loc=(-1.02, 3.85, 1.78), seg=8, bevel=0)                            # exhaust stack
    steel.cyl(.07, .05, loc=(-1.02, 3.85, 2.01), seg=8, bevel=0)
    for s in (-1, 1):
        _taillight(a, s * .88, 3.72, 1.72)
    _jerrycans(a, (.95, 3.84, 1.0), 2, axis='x')
    dark.box((1.1, .3, .08), loc=(.25, 3.82, .66), bevel=.02, seg=1)                        # rear step
    for s in (-1, 1):
        steel.box((.12, .16, .12), loc=(s * .6, 3.78, .8), bevel=.02, seg=1)               # tow hooks
    # Bolted appliqué plates on the upright flank band, clear of the bins and the door.
    for s, spans in ((1, ((-2.3, -1.2), (1.05, 3.3))), (-1, ((-2.3, -.8), (.45, 3.3)))):
        for y0, y1 in spans:
            armor.box((.05, y1 - y0, .3), loc=(s * 1.315, (y0 + y1) / 2, 1.18), bevel=.012, seg=1)
            steel.bolts([(s * 1.345, y, z) for y in (y0 + .08, y1 - .08) for z in (1.08, 1.28)], r=.018, h=.02,
                        rot=(0, R90, 0), bevel=0)


# ----------------------------------------------------------------------------- wheeled_gun
WG_AXLES = (-2.62, -1.2, .6, 2.02)


def wheeled_gun(a):
    """8x8 wheeled tank destroyer (Centauro B1 / M1128 MGS / Rooikat lineage), 7.6 x 3.0 m: a low wide hull with
    a long glacis, the engine deck and its grilles at the front beside the driver, bolted sponson bins over
    the wheels, and a low faceted turret a little ahead of the middle. Its 105 mm gun (thermal sleeve with
    clamps, a bulged fume extractor, a multi-baffle muzzle brake) overhangs the nose by 3 m; a boxy
    mantlet, the coaxial MG on its right, smoke-grenade banks on both cheeks, a gunner's sight, the
    commander's panoramic sight and a roof MG on `Mount_mg` (child of Turret), hatches, antennas and a bustle
    basket with a bedroll and ammunition box."""
    _suffixed(a)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in WG_AXLES:
        for s in (-1, 1):
            _wheel(a, s * 1.26, y, .6, .46)
            dark.box((.3, .24, .18), loc=(s * .98, y, .6), bevel=.02, seg=1)                  # hub carriers
    full = (.55, .95, 1.25, 1.66, .9, 1.3, 1.36, 1.18)
    hull.loft([
        _hull_section(-3.82, .82, .86, .92, .98, .7, 1.0, 1.02, .92),
        _hull_section(-3.45, .56, .95, 1.16, 1.28, .88, 1.26, 1.3, 1.12),
        _hull_section(-2.3, *full),
        _hull_section(3.56, *full),
        _hull_section(3.8, .64, .95, 1.23, 1.6, .85, 1.26, 1.3, 1.1),
    ], bevel=.06, seg=2)
    zr = 1.66
    G0, G1 = (-3.45, 1.28), (-2.3, zr)                                                     # upper glacis
    wr = _glacis(G0, G1, 0, 0)[2]
    for s in (-1, 1):
        hy, hz, _ = _glacis(G0, G1, .12, 0)
        _headlight(a, s * .78, hy - .07, hz + .08)
        steel.box((.14, .2, .14), loc=(s * .5, -3.72, .88), bevel=.02, seg=1)             # tow hooks
        _taillight(a, s * .95, 3.8, 1.42)
    # Glacis: a hinged engine access plate with lifting eyes, and the splash board.
    gy, gz, _ = _glacis(G0, G1, .55, .015)
    armor.box((1.5, .7, .05), loc=(-.1, gy, gz), rot=(wr, 0, 0), bevel=.015, seg=1)
    for dx in (-.6, .4):
        ey, ez, _ = _glacis(G0, G1, .55, .06)
        steel.tube([(dx - .06, ey, ez - .02), (dx - .06, ey, ez + .05), (dx + .06, ey, ez + .05),
                    (dx + .06, ey, ez - .02)], .016, seg=4)
    by, bz, _ = _glacis(G0, G1, .08, .03)
    armor.box((2.0, .05, .14), loc=(0, by, bz), rot=(wr - 1.1, 0, 0), bevel=.012, seg=1)
    # Front deck: driver's hatch and periscopes on the left, the engine grilles on the right and behind.
    _hatch(a, .62, -2.0, zr, .27)
    _periscopes(a, [(.62 + dx, -2.3, zr - .02, 0) for dx in (-.17, 0, .17)])
    deck = a.part('Deck', 'Undercarriage')
    for x, y, w, d in ((-.42, -1.98, .9, .62), (.3, -1.52, .7, .3), (-.42, -1.44, .9, .32)):
        deck.grille(w, d, loc=(x, y, zr + .01), rot=(-R90, 0, 0), slats=max(2, int(d / .1)), depth=.06,
                    thickness=.035)
        _grille_frame(a, x, y, zr - .01, w, d, t=.04)
    # Exhausts on the front flanks, sponson bins over the wheels, tow cable on the left.
    for s in (-1, 1):
        fx, fz, lean = _flank((1.36, 1.25), (1.18, zr), .5, .01)
        a.part('Exhaust', 'Armor').box((.06, .5, .24), loc=(s * fx, -2.0, fz), rot=(0, -s * lean, 0), bevel=.01, seg=1)
        a.part('Exhaust_louvres', 'Undercarriage').box((.04, .4, .16), loc=(s * (fx + .02), -2.0, fz),
                                                       rot=(0, -s * lean, 0), bevel=0)
        for y0, y1 in ((-1.6, -.25), (.95, 3.2)):
            bx, bz, _ = _flank((1.36, 1.25), (1.18, zr), .45, .1)
            armor.box((.2, y1 - y0, .36), loc=(s * bx, (y0 + y1) / 2, bz), rot=(0, -s * lean, 0), bevel=.02, seg=1)
            a.part('Stowage_lid', 'Armor').box((.24, y1 - y0 + .03, .04), loc=(s * (bx - .02), (y0 + y1) / 2, bz + .2),
                                               rot=(0, -s * lean, 0), bevel=.01, seg=1)
            steel.bolts([(s * (bx + .1), y, bz - .05) for y in (y0 + .15, (y0 + y1) / 2, y1 - .15)], r=.02, h=.03,
                        rot=(0, s * (R90 - lean), 0), bevel=0)
    _cable(a, [(1.0, -1.1, zr + .015), (1.0, 1.2, zr + .015), (.98, 3.3, zr - .01)])
    # Rear: an ammunition door, jerrycans, a stowage bin, the rear step and tow hooks.
    armor.box((.9, .08, .7), loc=(-.2, 3.81, 1.2), bevel=.02, seg=1)
    steel.box((.24, .05, .05), loc=(.05, 3.86, 1.22), bevel=0)
    for dz in (-.25, .25):
        steel.box((.1, .08, .1), loc=(-.6, 3.85, 1.2 + dz), bevel=0)
    _jerrycans(a, (.8, 3.9, .92), 2, axis='x')
    dark.box((1.2, .3, .08), loc=(0, 3.84, .68), bevel=.02, seg=1)
    for s in (-1, 1):
        steel.box((.12, .16, .12), loc=(s * .55, 3.84, .84), bevel=.02, seg=1)
    _stowage_bin(a, (-.7, 3.1, zr - .01), (.8, .6, .24), latch_side=0)
    steel.cyl(1.06, .1, loc=(0, -.1, zr + .03), seg=24, bevel=.02, bseg=1)                 # turret ring

    # Turret: a low faceted house, wedge front, bustle; the gun in a boxy mantlet.
    t = a.pivot('Turret', (0, -.1, zr + .06))
    bottom = [(-.56, -1.3), (.56, -1.3), (1.06, -.78), (1.16, .3), (1.08, 1.05), (-1.08, 1.05), (-1.16, .3),
              (-1.06, -.78)]
    topo = [(-.4, -.98), (.4, -.98), (.92, -.6), (1.02, .3), (.96, .98), (-.96, .98), (-1.02, .3), (-.92, -.6)]
    zt = .7
    a.part('Turret_body', 'Team', t).loft([[(x, y, .02) for x, y in bottom], [(x, y, zt) for x, y in topo]],
                                          bevel=.05, seg=1)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((1.8, .6, .5), loc=(0, 1.3, .36), bevel=.04, seg=1, taper=(.95, .92))          # bustle
    _basket_rack(a, t, 1.62, 2.02, .2)
    tarm.box((.56, .34, .44), loc=(0, -1.22, .38), bevel=.04, seg=1)                        # mantlet
    tarm.box((.7, .12, .5), loc=(0, -1.08, .38), bevel=.02, seg=1)                          # mantlet cheeks
    zg = .4
    # The breech runs back inside the turret, so the game's elevation pivot (6 % of the barrel group's length
    # from its rear) falls inside the mantlet.
    a.part('Main_cannon', 'Steel', t).cyl(.13, .62, loc=(0, -.83, zg), rot=FORWARD, seg=12, bevel=0)
    tip = _gun(a, t, 0, -1.12, zg, 5.25, .08, seg=12, sleeves=((.12, .5, .105), (.62, .05, .1), (.82, .05, .095)),
               extractor=(.38, .6, .13), brake=(.56, .14, 3))
    a.pivot('Muzzle_main', tip, t)
    # Coaxial MG on the right of the mantlet.
    coax = a.part('Coax', 'Steel', t)
    coax.box((.12, .3, .12), loc=(-.4, -1.28, .44), bevel=.02, seg=1)
    coax.cyl(.026, .34, loc=(-.4, -1.58, .44), rot=FORWARD, seg=8, bevel=0)
    coax.cyl(.038, .08, loc=(-.4, -1.76, .44), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (-.4, -1.8, .44), t)
    # Cheeks: smoke-grenade banks; roof: gunner's sight, commander's panoramic sight, hatches, vents.
    for s in (-1, 1):
        _smoke(a, tsteel, .58, -.66, zt + .03, s, count=3, gap=.08)
    tarm.box((.3, .34, .22), loc=(-.42, -.28, zt + .09), bevel=.03, seg=1)                 # gunner's sight
    a.part('Sight', 'Glass', t).box((.22, .04, .12), loc=(-.42, -.46, zt + .11), bevel=.01, seg=1)
    tsteel.cyl(.1, .16, loc=(.42, -.24, zt + .06), seg=10, bevel=0)                         # panoramic sight
    tarm.cyl(.14, .18, loc=(.42, -.24, zt + .22), seg=10, bevel=.02, bseg=1)
    a.part('Sight', 'Glass', t).box((.16, .04, .1), loc=(.42, -.38, zt + .23), bevel=0)
    _hatch(a, -.42, .3, zt - .01, .25, parent=t)
    tarm.cyl(.13, .1, loc=(0, .62, zt + .03), seg=10, bevel=.02, bseg=1)                    # ventilator
    a.part('Vent_cap', 'Undercarriage', t).cyl(.1, .04, loc=(0, .62, zt + .09), seg=10, bevel=0)
    _antenna(a, t, .8, 1.5, .6, 1.3)
    _antenna(a, t, -.8, 1.5, .6, 1.0)
    # Commander's MG on its own mount on the left of the roof, behind the panoramic sight.
    tsteel.cyl(.36, .1, loc=(.5, .35, zt + .02), seg=16, bevel=.02, bseg=1)                # cupola ring
    wpn.hmg(a, (.5, .35, zt + .07), parent=t, post=.2, length=.8, ammo=-1)


def _basket_rack(a, parent, y0, y1, z0):
    """Bustle basket behind a turret: tube rails on posts round a floor, a bedroll and an ammunition box."""
    steel = a.part('Basket', 'Steel', parent)
    x = .82
    steel.tube([(-x, y0, z0 + .34), (-x, y1, z0 + .34), (x, y1, z0 + .34), (x, y0, z0 + .34)], .02, seg=4)
    for px, py in ((-x, y1), (x, y1), (0, y1)):
        steel.box((.035, .035, .34), loc=(px, py, z0 + .17), bevel=0)
    a.part('Basket_floor', 'Armor', parent).box((2 * x, y1 - y0, .04), loc=(0, (y0 + y1) / 2, z0 + .02), bevel=0)
    _roll(a, (-.25, (y0 + y1) / 2, z0 + .17), .9, r=.12, parent=parent)
    a.part('Ammo_boxes', 'Crate', parent).box((.34, .3, .24), loc=(.5, (y0 + y1) / 2, z0 + .15), bevel=.02, seg=1)


# ----------------------------------------------------------------------------- shared truck cab
def _truck_cab(a, yf, yb, zb, zs, zt, w, wt, rake, x=0.0, name='Body', panes=((-.52, .86), (.52, .86)), pane_h=.6,
               grille=True):
    """Cab-over truck cab (see mb_new_trucks._cab_over) centred at x: raked front with framed armoured
    windscreens and wipers, a visor, a radiator grille, headlights and marker lights. Returns (front bottom,
    front top) for _glacis."""
    def ring(y0, k):
        pts = [(-w, zb), (w, zb), (w, zs), (wt, zt), (-wt, zt), (-w, zs)]
        return [(x + px, y0 + k * (z - zb), z) for px, z in pts]
    a.part(name, 'Team').loft([ring(yf, rake), ring(yb, 0)], bevel=.06)
    F0, F1 = (yf, zb), (yf + rake * (zt - zb), zt)
    armor = a.part('Armor', 'Armor')

    def on_front(z, out):
        return _glacis(F0, F1, (z - zb) / (zt - zb), out)
    wr = on_front(zb + .5, 0)[2]
    tz = (zs + .05 - zb) / (zt - zb)
    for px, pw in panes:
        _plate_frame(a, F0, F1, tz, x + px, pw, pane_h)
        _wiper(a, F0, F1, tz - .3, tz + .2, x + px - pw * .35, x + px + pw * .1)
    vy, vz, _ = on_front(zt, .04)
    armor.box((2 * wt + .3, .3, .05), loc=(x, vy - .1, vz - .03), rot=(wr - 1.25, 0, 0), bevel=.012, seg=1)   # visor
    if grille:
        gy, gz, _ = on_front(zb + .38, .015)
        a.part('Chassis', 'Undercarriage').grille(w * 1.05, .36, loc=(x, gy, gz), rot=(-(R90 - wr), 0, 0), slats=4,
                                                  depth=.05, thickness=.04)
    for s in (-1, 1):
        hy = on_front(zb + .32, 0)[0]
        _headlight(a, x + s * (w - .28), hy, zb + .32, guard=True)
    for dx in (-.5, 0, .5):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x + dx * w / 1.2, yf + .3, zt + .005), bevel=0)
    return F0, F1


# ----------------------------------------------------------------------------- counter_battery_radar
CB_AXLES = (-3.05, 1.3, 2.7)


def counter_battery_radar(a):
    """6x6 counter-battery radar truck (AN/TPQ-53 / Zoopark-1 / COBRA lineage), 8.1 x 2.6 m: an armoured cab-over
    cab with the roof MG (`Mount_mg`) and a hatch, a Team equipment shelter behind it (side door and steps,
    an air-conditioning unit, louvres, whips and a GPS puck), a generator and a battery box slung under the left of
    the bed and a fuel tank under the right, four stabiliser jacks, and at the rear a pedestal carrying
    the radar on `Radar` (it spins about Z): a turntable, a yoke with side arms and a big flat 2.5 x 2.0 m
    phased-array face tilted back 20 degrees, a light radome face gridded by its tile seams, a Team frame,
    an IFF bar on top and the electronics and cooling unit on its back."""
    _suffixed(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    _running_gear_cb(a)
    zb, zs, zt, w, wt = 1.1, 2.3, 2.88, 1.22, 1.02
    yf, yb = -4.0, -2.12
    _truck_cab(a, yf, yb, zb, zs, zt, w, wt, .1)
    # Bumper with a winch fairlead and striped ends, tow hooks.
    steel.box((2.5, .24, .3), loc=(0, yf - .06, .9), bevel=.04, seg=1)
    armor.box((.6, .1, .2), loc=(0, yf - .2, .9), bevel=.02, seg=1)
    dark.box((2.0, .4, .3), loc=(0, yf + .18, 1.0), bevel=.02, seg=1)
    for s in (-1, 1):
        steel.box((.14, .14, .14), loc=(s * .5, yf - .2, .8), bevel=.02, seg=1)
        _stripe_band(a, (s * .95, yf - .185, .9), '-y', .6, .2)
    # Flanks: door windows, shut lines, handles, steps, mirrors, mud flaps; roof: MG ring, hatch, whips.
    for s in (-1, 1):
        for y in (-3.45, -2.55):
            _side_window(a, s, w, y, 2.0, .5, .34)
        for y in (-3.85, -3.0, -2.2):
            armor.box((.03, .04, 1.1), loc=(s * (w + .006), y, 1.72), bevel=0)
        for y in (-3.15, -2.3):
            steel.box((.04, .16, .05), loc=(s * (w + .02), y, 1.85), bevel=0)
        for y in (-3.8, -2.3):                                                                # steps, clear of the wheel
            for zz in (.78, .5):
                steel.box((.3, .26, .04), loc=(s * 1.08, y, zz), bevel=0)
            steel.box((.04, .26, .42), loc=(s * 1.24, y, .72), bevel=0)
        _mirror(a, s, (s * 1.2, -3.8, 2.5), out=.18)
        _whip(a, s * .85, -2.3, zt, 1.2)
    armor.cyl(.34, .1, loc=(-.48, -3.3, zt + .02), seg=16, bevel=.02, bseg=1)
    wpn.hmg(a, (-.48, -3.3, zt + .07), post=.12, length=.85, ammo=-1)
    _hatch(a, .48, -2.8, zt, .26)

    # Bed: deck, mudguards over the tandem, tail.
    deck_z = 1.36
    armor.box((2.5, 5.96, .12), loc=(0, .96, deck_z - .06), bevel=.02, seg=1)                 # y -2.02 .. 3.94
    for s in (-1, 1):
        armor.box((.5, 2.6, .05), loc=(s * 1.02, 2.0, 1.2), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .4), loc=(s * 1.02, 3.42, .72), bevel=0)
        _taillight(a, s * .95, 3.97, 1.12)
    dark.box((2.3, .12, .22), loc=(0, 3.9, 1.12), bevel=0)
    steel.box((2.4, .16, .2), loc=(0, 4.02, .88), bevel=.03, seg=1)
    _stripe_band(a, (0, 4.1, .88), '+y', 2.3, .16)
    _ladder(a, .7, 4.12, .3, deck_z + .1, width=.36)
    # Under the bed: generator on the right, fuel tank and battery box on the left; stabiliser jacks.
    gen = a.part('Generator', 'Armor')
    gen.box((.52, 1.7, .62), loc=(.96, -.85, .92), bevel=.03, seg=1)
    dark.grille(1.2, .4, loc=(1.225, -.85, .95), rot=(0, 0, R90), slats=4, depth=.05, thickness=.035)
    a.part('Generator_panel', 'Glass').box((.03, .22, .14), loc=(1.23, -1.55, 1.1), bevel=0)
    steel.tube([(.9, -.05, .9), (.9, .25, .72), (.9, .45, .62)], .045, seg=6)                  # exhaust
    armor.box((.4, .5, .5), loc=(1.02, .4, .98), bevel=.03, seg=1)                           # battery box
    steel.box((.03, .06, .08), loc=(1.23, .4, 1.08), bevel=0)
    _fuel_tank(a, -.95, .12, .9, .9)
    for x, y in ((-1.12, -1.78), (1.12, -1.78), (-1.12, 3.62), (1.12, 3.62)):
        _jack(a, x, y, deck_z - .1)

    # Equipment shelter behind the cab.
    sy0, sy1, sz1 = -1.95, .5, 2.95
    shelter = a.part('Shelter', 'Team')
    shelter.box((2.42, sy1 - sy0, sz1 - deck_z + .02), loc=(0, (sy0 + sy1) / 2, (deck_z - .02 + sz1) / 2), bevel=.04,
                seg=1)
    rim(a.part('Shelter_rim', 'Armor'), -1.23, 1.23, sy0 - .01, sy1 + .01, sz1 - .04, .1, .06, bevel=0)
    fbox(armor, '-x', (-1.21, -.75, 2.0), (.8, .06, 1.3), out=.02, bevel=.012)                  # side door
    fbox(steel, '-x', (-1.21, -1.05, 2.0), (.05, .05, .2), out=.05)
    for k in range(2):
        steel.box((.32, .6, .04), loc=(-1.36, -.75, .98 + k * .3), bevel=0)                  # steps
    steel.box((.04, .6, .7), loc=(-1.5, -.75, 1.05), bevel=0)
    for y in (-1.45, -.05):                                                                   # louvres
        fbox(dark, '+x', (1.21, y, 2.35), (.6, .05, .4), out=.02)
        for k in range(3):
            fbox(armor, '+x', (1.21, y, 2.22 + k * .13), (.62, .05, .03), out=.05)
    fbox(dark, '-y', (0, sy0, 2.5), (1.2, .05, .36), out=.02)                                 # front vent
    ac = a.part('Aircon', 'Fuel')
    ac.box((.9, .62, .34), loc=(.45, -1.45, sz1 + .16), bevel=.03, seg=1)
    a.part('Aircon_fans', 'Rubber').cyl(.22, .03, loc=(.45, -1.45, sz1 + .335), seg=12, bevel=0)
    a.part('Satcom', 'Medical').sphere((.14, .14, .07), loc=(-.7, -1.5, sz1), seg=10, rings=5, cut=0)
    for x in (-.95, .95):
        _antenna(a, None, x, .2, sz1, 1.6 if x > 0 else 1.2)
    cable = a.part('Cables', 'Rubber')
    for x in (-.3, .3):
        cable.tube([(x, sy1 + .02, 1.62), (x, sy1 + .4, 1.45), (x, 1.62, 1.45), (x, 1.66, 1.56)], .04, seg=5)
    fbox(armor, '+y', (0, sy1, 1.7), (.9, .08, .3), out=.02)                                  # cable port
    for x in (-.6, .6):
        _stowage_bin(a, (x, 3.55, deck_z - .01), (.5, .4, .3), latch_side=0)
    # Cable reel and a tool box between the shelter and the radar, low under the array's sweep.
    reel = a.part('Cable_reel', 'Rubber')
    reel.cyl(.24, .5, loc=(.78, 1.05, deck_z + .36), rot=ACROSS, seg=12, bevel=.02, bseg=1)
    for dx in (-.28, .28):
        steel.cyl(.34, .04, loc=(.78 + dx, 1.05, deck_z + .36), rot=ACROSS, seg=14, bevel=0)
        steel.box((.05, .4, .08), loc=(.78 + dx * 1.2, 1.05, deck_z + .03), bevel=0)
        steel.box((.05, .06, .36), loc=(.78 + dx * 1.2, 1.05, deck_z + .2), bevel=0)
    _stowage_bin(a, (-.75, 1.05, deck_z - .01), (.56, .5, .4), latch_side=0)

    # Radar: pedestal on the deck; turntable, yoke, arms and the tilted phased-array face on `Radar`.
    ry = 2.35
    armor.box((1.4, 1.4, .36), loc=(0, ry, deck_z + .17), bevel=.04, seg=1, taper=(.9, .9))
    steel.cyl(.66, .06, loc=(0, ry, deck_z + .36), seg=20, bevel=0)
    r = a.pivot('Radar', (0, ry, deck_z + .38))
    rsteel = a.part('Radar_steel', 'Steel', r)
    rarm = a.part('Radar_yoke', 'Armor', r)
    rsteel.cyl(.62, .12, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                         # turntable
    rarm.box((1.0, .8, .44), loc=(0, .12, .33), bevel=.04, seg=1)
    tilt = math.radians(20)
    W, H, D = 2.5, 2.0, .26
    m = _frame((0, .22, 1.55), (-tilt, 0, 0))

    def pm(part, size, loc, bevel=0.0, seg=1):
        wl, wrot = _at(m, loc)
        part.box(size, loc=wl, rot=wrot, bevel=bevel, seg=seg)
    pm(a.part('Radar_frame', 'Team', r), (W, D, H), (0, 0, 0), bevel=.05)
    pm(a.part('Radar_face', 'Fuel', r), (W - .18, .04, H - .18), (0, -D / 2 - .01, 0), bevel=.01)
    seams = a.part('Radar_seams', 'Undercarriage', r)
    for k in range(-2, 3):
        pm(seams, (.025, .02, H - .2), (k * (W - .18) / 6, -D / 2 - .035, 0))
    for k in (-1, 0, 1):
        pm(seams, (W - .2, .02, .025), (0, -D / 2 - .035, k * (H - .18) / 4))
    pm(rarm, (W * .82, .14, .1), (0, -.02, H / 2 + .06))                                     # IFF bar
    pm(a.part('Radar_iff', 'Undercarriage', r), (W * .78, .02, .06), (0, -.1, H / 2 + .06))
    pm(rarm, (1.5, .3, 1.2), (0, D / 2 + .14, -.1), bevel=.03)                                # electronics
    for z in (-.55, -.2, .15, .5):
        pm(rarm, (2.2, .06, .06), (0, D / 2 + .02, z))                                        # back ribs
    pm(a.part('Radar_cooler', 'Armor', r), (.7, .2, .5), (0, D / 2 + .39, .1), bevel=.02)
    fan_l, fan_r = _at(m, (0, D / 2 + .5, .1), (R90, 0, 0))
    a.part('Radar_fan', 'Rubber', r).cyl(.18, .03, loc=fan_l, rot=fan_r, seg=12, bevel=0)
    for s in (-1, 1):                                                                         # side arms
        top_l = m @ Vector((s * (W / 2 - .12), D / 2 + .05, -.35))
        rarm.limb((s * .42, .3, .45), tuple(top_l), .12, .16, bevel=.02)
        pin_l, pin_r = _at(m, (s * (W / 2 - .12), D / 2 + .05, -.35), (0, R90, 0))
        rsteel.cyl(.07, .12, loc=pin_l, rot=pin_r, seg=8, bevel=0)
    a.part('Radar_cable', 'Undercarriage', r).tube([(.3, .5, .5), (.3, .52, .68), tuple(m @ Vector((.3, D / 2 + .28, -.6)))],
                                                    .035, seg=5)


def _running_gear_cb(a):
    """The radar truck's axles, wheels, frame rails and cross members."""
    dark = a.part('Chassis', 'Undercarriage')
    for y in CB_AXLES:
        for s in (-1, 1):
            _wheel(a, s * 1.02, y, .55, .42)
        dark.box((1.74, .22, .17), loc=(0, y, .55), bevel=.02, seg=1)
        dark.box((.36, .42, .32), loc=(0, y, .65), bevel=.03, seg=1)
    for s in (-1, 1):
        dark.box((.2, 7.7, .3), loc=(s * .48, .05, .92), bevel=.03, seg=1)
    for y in (-3.5, -1.0, 1.95, 3.7):
        dark.box((.8, .12, .16), loc=(0, y, .92), bevel=0)


# ----------------------------------------------------------------------------- long_sam
LS_AXLES = (-3.85, -1.65, 1.65, 3.85)


def long_sam(a):
    """Heavy 8x8 transporter-erector-launcher (S-300PMU 5P85 / S-400 lineage), 11.4 x 3 m: the two split crew
    cabs of a MAZ-543 chassis either side of the engine hood, an engine and equipment compartment behind them
    with grilles and exhaust stacks, big tyres, fuel tanks, lockers and four stabiliser jacks, a transport
    rest. On the rear a low turntable (`Turret`) and the erector: four 8 m missile canisters side by side
    (Team bodies with clamp bands, frames, rails and lifting lugs, domed rear caps with connectors, steel
    mouth rims round dark frangible covers) on two erector beams, raised 4 degrees and pointing forward over
    the bed. Every canister and erector part is named Launcher*, so the game raises the whole group about
    its rear trunnion (0.5 m ahead of the rear caps); a cradle on the turntable carries the rear, a transport
    rest on the bed the front, and the erector beams start ahead of the trunnion so they lift clear. A heavy
    machine gun on the right cab (`Mount_mg`), kept off the canister mouths' line, and whips."""
    _suffixed(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    body = a.part('Body', 'Team')
    for y in LS_AXLES:
        for s in (-1, 1):
            _wheel(a, s * 1.2, y, .72, .52, seg=18)
        dark.box((2.0, .24, .2), loc=(0, y, .72), bevel=.02, seg=1)
        dark.box((.4, .46, .36), loc=(0, y, .82), bevel=.03, seg=1)
    for s in (-1, 1):
        dark.box((.24, 10.6, .36), loc=(s * .5, 0, 1.1), bevel=.03, seg=1)                  # frame rails
    for y in (-4.9, -2.8, 0, 2.8, 4.9):
        dark.box((.9, .14, .2), loc=(0, y, 1.1), bevel=0)
    # Split cabs either side of the engine hood.
    zb, zs, zt = 1.48, 2.4, 2.8                           # low roofs: the canister mouths look over them at rest
    yf, yb = -5.5, -4.0
    for s in (-1, 1):
        cx = s * .96
        _truck_cab(a, yf, yb, zb, zs, zt, .5, .4, .14, x=cx, name='Body', panes=((0, .62),), pane_h=.5, grille=False)
        _side_window(a, s, 1.46, -4.55, 2.1, .44, .34)
        armor.box((.03, .04, 1.0), loc=(s * 1.466, -4.2, 1.98), bevel=0)                    # door shut line
        steel.box((.04, .16, .05), loc=(s * 1.49, -4.35, 2.0), bevel=0)
        _mirror(a, s, (s * 1.44, -5.3, 2.6), out=.2)
        for zz in (1.0, 1.3):
            steel.box((.34, .3, .04), loc=(s * 1.3, -4.5, zz), bevel=0)                      # steps
        armor.box((.6, 1.7, .06), loc=(s * 1.2, -3.85, 1.52), bevel=0)                       # fender
        a.part('Mud_flaps', 'Rubber').box((.5, .04, .44), loc=(s * 1.2, -3.0, .9), bevel=0)
    _whip(a, 1.25, -4.2, zt, 1.5)                          # left cab; the right one carries the MG
    # Engine hood between the cabs: radiator grille, lights, bumper.
    body.box((.88, 1.5, 1.0), loc=(0, -4.72, 1.78), bevel=.05, seg=1, taper=(.92, .9))
    dark.grille(.62, .6, loc=(0, -5.48, 1.72), rot=(0, 0, 0), slats=5, depth=.05, thickness=.04)
    steel.box((2.9, .26, .3), loc=(0, -5.6, 1.12), bevel=.04, seg=1)                           # bumper
    for s in (-1, 1):
        steel.box((.16, .16, .16), loc=(s * .45, -5.76, 1.0), bevel=.02, seg=1)
        _stripe_band(a, (s * 1.1, -5.735, 1.12), '-y', .6, .2)
    dark.box((2.5, 1.3, .3), loc=(0, -4.8, 1.3), bevel=.02, seg=1)                             # cab floor
    # MG on the right cab between the lines of the right-hand canisters; hatch on the left cab.
    armor.cyl(.34, .1, loc=(-.7, -4.55, zt + .02), seg=16, bevel=.02, bseg=1)
    wpn.hmg(a, (-.7, -4.55, zt + .07), post=.14, length=.85, ammo=1)
    _hatch(a, .8, -4.6, zt, .24)
    # Engine and equipment compartment behind the cabs.
    body.box((2.9, .9, 1.25), loc=(0, -3.5, 1.9), bevel=.05, seg=1)                           # y -3.95 .. -3.05
    deck = a.part('Deck', 'Undercarriage')
    for x in (-.8, .8):
        deck.grille(.9, .6, loc=(x, -3.5, 2.535), rot=(-R90, 0, 0), slats=5, depth=.06, thickness=.04)
        _grille_frame(a, x, -3.5, 2.52, .9, .6, t=.04)
    for s in (-1, 1):
        steel.cyl(.09, .7, loc=(s * 1.3, -3.2, 2.75), seg=8, bevel=0)                         # exhaust stacks
        steel.cyl(.12, .06, loc=(s * 1.3, -3.2, 3.1), seg=8, bevel=0)
        fbox(dark, '+x' if s > 0 else '-x', (s * 1.45, -3.5, 1.9), (.6, .05, .5), out=.02)
    _whip(a, -1.35, -3.3, 2.525, 1.3)                      # right whip on the compartment, outside the MG's sweep
    # Bed: deck plate, fuel tanks and lockers, fenders, rear platform, lights, ladder.
    dz = 1.36
    armor.box((2.9, 8.55, .1), loc=(0, 1.22, dz), bevel=.02, seg=1)                             # y -3.05 .. 5.5
    for s in (-1, 1):
        _fuel_tank(a, s * 1.1, -.1, 1.05, 1.5, r=.3)
        _stowage_bin(a, (s * 1.18, 2.75, .85), (.36, .9, .46), latch_side=s)
        armor.box((.6, 2.9, .06), loc=(s * 1.2, 2.75, 1.52), bevel=0)                          # fenders
        _taillight(a, s * 1.2, 5.52, 1.2)
        for y in (-2.6, .2, 2.9, 5.3):
            steel.box((.05, .1, .06), loc=(s * 1.44, y, dz + .07), bevel=0)                    # tie-downs
    for x, y in ((-1.3, -2.5), (1.3, -2.5), (-1.3, 5.15), (1.3, 5.15)):
        _jack(a, x, y, dz - .05, pad=.26)
    dark.box((2.6, .14, .24), loc=(0, 5.45, 1.12), bevel=0)
    steel.box((2.8, .18, .2), loc=(0, 5.6, .92), bevel=.03, seg=1)
    _stripe_band(a, (0, 5.69, .92), '+y', 2.6, .16)
    _ladder(a, .9, 5.72, .4, dz + .05, width=.36)
    # Transport rest under the erector beams near the front (the erector lifts off it; its pad stays 2 cm under
    # the beams, at the same height all round the turret's sweep).
    for x in (-1.2, 1.2):
        steel.box((.12, .12, .67), loc=(x, -2.03, 1.745), bevel=0)
    steel.box((2.6, .16, .14), loc=(0, -2.03, 2.145), bevel=.02, seg=1)
    a.part('Rest_pads', 'Rubber').box((2.5, .2, .05), loc=(0, -2.03, 2.215), bevel=0)

    # Turntable and erector on `Turret`.
    t = a.pivot('Turret', (0, 4.0, dz + .12))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.2, .1, loc=(0, 0, .04), seg=24, bevel=.02, bseg=1)
    tarm.box((2.2, 1.6, .16), loc=(0, .1, .15), bevel=.03, seg=1)                               # base, top .23
    tarm.box((2.7, .3, .27), loc=(0, .95, .365), bevel=.03, seg=1)                              # rear cradle, top .5
    a.part('Turret_labels', 'Hazard', t).box((.3, .02, .12), loc=(0, .795, .38), bevel=0)
    pitch = math.radians(4)
    L, R, gap = 8.0, .3, .7
    xs = (1.5 * gap, .5 * gap, -.5 * gap, -1.5 * gap)                                          # left to right
    at = _axis((0, 1.15, .9), pitch)                                                            # at(s, up, side)
    crot = (R90 - pitch, 0, 0)                                                                  # cylinder along the bore
    brot = (-pitch, 0, 0)                                                                       # box along the bore
    can = a.part('Launcher', 'Team', t)
    bands = a.part('Launcher_bands', 'Armor', t)
    rims = a.part('Launcher_rims', 'Steel', t)
    caps = a.part('Launcher_caps', 'Undercarriage', t)
    ends = a.part('Launcher_ends', 'Armor', t)
    for x in xs:
        can.cyl(R, L - .1, loc=tuple(at(L / 2 + .05, 0, x)), rot=crot, seg=16, bevel=.02, bseg=1)
        for f in (.08, .3, .55, .8):
            bands.cyl(R + .025, .12, loc=tuple(at(L * f, 0, x)), rot=crot, seg=16, bevel=0)
        rims.lathe([(R + .02, -.12), (R + .02, .02), (R * .82, .02), (R * .82, -.06)],
                   loc=tuple(at(L - .02, 0, x)), rot=crot, seg=16)
        caps.cyl(R * .84, .03, loc=tuple(at(L - .07, 0, x)), rot=crot, seg=16, bevel=0)
        ends.lathe([(R + .01, 0), (R + .01, .06), (R * .7, .16), (0, .2)], loc=tuple(at(.12, 0, x)),
                   rot=(-R90 - pitch, 0, 0), seg=16)                                           # domed rear cap
        ends.box((.2, .12, .16), loc=tuple(at(-.06, .1, x)), rot=brot, bevel=0)               # connector
    frame = a.part('Launcher_frame', 'Armor', t)
    W = 4 * gap + .1
    for f in (.14, .45, .75, .96):                                                              # clamp frames
        for up in (R + .04, -R - .04):
            frame.box((W, .16, .1), loc=tuple(at(L * f, up)), rot=brot, bevel=.01, seg=1)
        for x in (W / 2, -W / 2):
            frame.box((.08, .16, 2 * R + .18), loc=tuple(at(L * f, 0, x)), rot=brot, bevel=0)
    for x in (-gap, 0, gap):                                                                    # top rails
        frame.box((.08, L - .8, .06), loc=tuple(at(L / 2, R + .04, x)), rot=brot, bevel=0)
    lugs = a.part('Launcher_lugs', 'Steel', t)
    for f in (.14, .75):
        for x in (W / 2 - .12, -W / 2 + .12):
            lugs.box((.1, .12, .1), loc=tuple(at(L * f, R + .14, x)), rot=brot, bevel=0)
    beams = a.part('Launcher_beams', 'Armor', t)
    for x in (-.75, .75):                  # erector beams, from ahead of the trunnion, so they rise when it lifts
        beams.box((.2, L - 1.0, .24), loc=tuple(at(L / 2 + .2, -R - .2, x)), rot=brot, bevel=.02, seg=1)
    for f in (.2, .5, .8):
        beams.box((1.7, .14, .16), loc=tuple(at(L * f, -R - .2)), rot=brot, bevel=0)
    a.part('Launcher_conduit', 'Undercarriage', t).box((.1, L - 1.2, .08), loc=tuple(at(L / 2, R + .06, .5 * gap)),
                                                       rot=brot, bevel=0)
    # Muzzles at the four mouths, each with its Launch_tubes cap (the game's launch point for that canister).
    for k, x in enumerate(xs):
        name = 'Muzzle_missile' if k == 0 else f'Muzzle_missile.{k:03d}'
        mk = a.pivot(dotted(name), tuple(at(L, 0, x)), t)
        a.part('Launch_tubes', 'Steel', mk).cyl(.14, .05, loc=tuple(Vector(at(-.025)) - Vector(at(0))), rot=crot,
                                                seg=12, bevel=0)
    a.pivot('Muzzle_main', tuple(at(L)), t)
    # Trunnion: the game raises the Launcher group about mb_new_trucks._game_pivot(a, t) (check_muzzles.py prints
    # it), 0.5 m ahead of the rear caps and low inside the canisters.


# ----------------------------------------------------------------------------- headquarters
def _hesco(a, x, y, z0=.2, w=1.05, d=1.05, h=1.2, yaw=0.0):
    """HESCO bastion unit standing on (x, y, z0): a wire-mesh gabion filled with earth, its sand-coloured
    geotextile liner, the soil top and the steel mesh picked out by uprights and a band on every face."""
    m = _frame((x, y, z0), (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Hesco', 'Sandbag').box((w, d, h), loc=m @ Vector((0, 0, h / 2)), rot=rot, bevel=.04, seg=1)
    a.part('Hesco_soil', 'Dirt').box((w - .1, d - .1, .06), loc=m @ Vector((0, 0, h - .01)), rot=rot, bevel=0)
    mesh = a.part('Hesco_mesh', 'Steel')
    for sx, sy, ax in ((1, 0, 'x'), (-1, 0, 'x'), (0, 1, 'y'), (0, -1, 'y')):
        off = Vector((sx * (w / 2 + .005), sy * (d / 2 + .005), 0))
        span = d if ax == 'x' else w
        for u in (-.3, .3):
            du = Vector((0, u * span, 0)) if ax == 'x' else Vector((u * span, 0, 0))
            size = (.03, .04, h - .08) if ax == 'x' else (.04, .03, h - .08)
            mesh.box(size, loc=m @ (off + du + Vector((0, 0, h / 2))), rot=rot, bevel=0)
        size = (.03, span - .06, .04) if ax == 'x' else (span - .06, .03, .04)
        mesh.box(size, loc=m @ (off + Vector((0, 0, h * .55))), rot=rot, bevel=0)


def _hesco_run(a, p0, p1, n, z0=.2, h=1.2):
    """n HESCO units in a row from p0 to p1 (their centres), turned along the run."""
    p0, p1 = Vector(p0), Vector(p1)
    yaw = math.atan2(p1.y - p0.y, p1.x - p0.x)
    for i in range(n):
        c = p0.lerp(p1, i / max(1, n - 1))  # callers space units at least 1.07 m apart (2 cm gaps)
        _hesco(a, c.x, c.y, z0, h=h, yaw=yaw)


def _slit(a, face, p, w=1.0, h=.4, lit=True, shutter=False):
    """Armoured window on a wall face: a steel frame, a lit (Lamp) or dark (Glass) pane, a visor above and, with
    shutter=True, a Team steel shutter swung open beside it."""
    fbox(a.part('Window_frames', 'Armor'), face, p, (w + .16, .1, h + .14), out=.03)
    fbox(a.part('Lit_windows' if lit else 'Windows', 'Lamp' if lit else 'Glass'), face, p, (w, .06, h), out=.065)
    fbox(a.part('Window_visors', 'Armor'), face, slide(face, p, 0, h / 2 + .1), (w + .26, .3, .06), out=.15)
    if shutter:
        fbox(a.part('Shutters', 'Team'), face, slide(face, p, w / 2 + .3 + .04, 0), (.56, .05, h + .06), out=.06)


def _blast_door(a, face, p, w=1.8, h=2.3):
    """Steel blast door on a wall face with ribs and a hazard-striped frame (p: the middle of its bottom edge)."""
    x, y, z = p
    fbox(a.part('Blast_door', 'Steel'), face, (x, y, z + h / 2), (w, .1, h), out=.02, bevel=.02)
    for du in (-w / 4, w / 4):
        fbox(a.part('Door_ribs', 'Armor'), face, slide(face, (x, y, z + h / 2), du), (.1, .06, h - .1), out=.08)
    n = 6
    for k in range(n):
        mat = 'SafetyStripe' if k % 2 else 'Charred'
        for s in (-1, 1):
            fbox(a.part('Door_hazard', mat), face, slide(face, (x, y, z + (k + .5) * h / n), s * (w / 2 + .14)),
                 (.24, .04, h / n - .01), out=.01)
    for k in range(6):
        mat = 'SafetyStripe' if k % 2 else 'Charred'
        fbox(a.part('Door_hazard', mat), face, slide(face, (x, y, z + h + .12), (k - 2.5) * (w + .5) / 6),
             ((w + .5) / 6 - .01, .04, .22), out=.01)


def _flak_mount(a, loc):
    """Twin 30 mm flak mount on its own `Mount_mg` yaw pivot standing on loc: a turntable and carriage, cradle
    cheeks, two receivers with their barrels and dark flash hiders (Flak_barrel_1 / _2), ammunition boxes on both
    sides, the gunner's seat and sight and a small shield. `Muzzle_mg` sits at the left barrel's hider face,
    `Muzzle_mg.001` at the right one."""
    m = a.pivot('Mount_mg', loc)
    steel = a.part('Flak_steel', 'Steel', m)
    body = a.part('Flak_carriage', 'Armor', m)
    steel.cyl(.56, .1, loc=(0, 0, .05), seg=18, bevel=.02, bseg=1)                           # turntable
    body.box((.9, 1.1, .3), loc=(0, .1, .25), bevel=.04, seg=1)                             # carriage
    for s in (-1, 1):
        body.box((.1, .7, .5), loc=(s * .42, -.02, .58), bevel=.02, seg=1)                  # cradle cheeks
    steel.cyl(.06, .96, loc=(0, -.02, .7), rot=ACROSS, seg=8, bevel=0)                      # trunnion
    zb = .76
    tip = -2.25
    for k, s in enumerate((1, -1)):                                                          # left, right
        x = s * .2
        steel.box((.2, .9, .22), loc=(x, -.05, zb), bevel=.02, seg=1)                        # receiver
        a.part(f'Flak_barrel_{k + 1}', 'Steel', m).cyl(.048, 1.72, loc=(x, -.5 - .86, zb), rot=FORWARD, seg=10,
                                                       bevel=0)
        a.part(f'Flak_jacket_{k + 1}', 'Armor', m).cyl(.075, .5, loc=(x, -.72, zb), rot=FORWARD, seg=10, bevel=0)
        a.part(f'Flak_hider_{k + 1}', 'Undercarriage', m).cyl(.07, .2, loc=(x, tip + .1, zb), rot=FORWARD, seg=10,
                                                              bevel=0)
        a.part('Flak_ammo', 'Crate', m).box((.24, .56, .42), loc=(s * .62, .05, .62), bevel=.02, seg=1)
        steel.box((.1, .2, .06), loc=(s * .5, .05, .72), rot=(0, s * .4, 0), bevel=0)        # feed chutes
        pivot_name = 'Muzzle_mg' if k == 0 else dotted('Muzzle_mg.001')
        a.pivot(pivot_name, (x, tip, zb), m)
    body.box((.46, .36, .1), loc=(0, .72, .5), bevel=.02, seg=1)                             # seat
    body.box((.46, .08, .4), loc=(0, .88, .72), bevel=.02, seg=1)                            # seat back
    a.part('Flak_sight', 'Armor', m).box((.14, .24, .18), loc=(0, .2, 1.0), bevel=.02, seg=1)
    a.part('Flak_sight_glass', 'Glass', m).box((.1, .03, .1), loc=(0, .07, 1.02), bevel=0)
    steel.box((.04, .04, .2), loc=(0, .25, .88), bevel=0)
    a.part('Flak_shield', 'Armor', m).box((1.3, .05, .46), loc=(0, -.52, .6), rot=(-.18, 0, 0), bevel=.015, seg=1,
                                          taper=(.9, 1))
    return m


HQ_BLOCK = (-6.0, 1.2, -3.0, 5.0, 5.4)      # main block x0, x1, y0, y1, roof
HQ_TURRET = (-2.3, -.9)


def headquarters(a):
    """Camp headquarters (14 x 12 m plinth, roof 5.4 m): a two-storey fortified command block of battered concrete
    with Team fascia and floor bands, rows of armoured slit windows (lit, some behind Team shutters), a hardened
    entrance portal with a hazard-framed blast door, lamps and a sandbag chicane, and a corner bastion tower at
    the rear left carrying the twin 30 mm flak mount (`Mount_mg`) in a sandbag nest. The single-storey signals
    wing on the right has a helipad roof (asphalt deck, Team border, white ring and H, edge lights, a
    windsock) and a ladder; behind it a yard with a lattice radar tower (dish spinning on `Radar`), a
    generator and drums. HESCO bastion walls and jersey barriers guard the front, a Team flag flies at the front
    left. On the main roof, on a hazard-striped drum, the twin heavy gun `Turret`: a faceted house with canvas
    blast bags, two long barrels with muzzle brakes (Main_cannon / Muzzle_brake on the left, Main_cannon_2 /
    Muzzle_brake_2 on the right, `Muzzle_main` and `Muzzle_main.001` at their bores), a ball-mounted coaxial MG
    between them (`Muzzle_coax`), sight hoods, a cupola, hatches and antennas."""
    _suffixed(a)
    rng = random.Random(2024)
    x0, x1, y0, y1, roof = HQ_BLOCK
    z0 = .22
    a.part('Plinth', 'Concrete').prism(chamfered(14.0, 12.0, .9), .26, loc=(0, 0, .09), axis='Z', bevel=.04, seg=1)
    conc = a.part('Block', 'Concrete')
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    conc.box((x1 - x0, y1 - y0, roof - z0 + .02), loc=(xc, yc, (z0 - .02 + roof) / 2), bevel=.1, seg=1)
    team = a.part('Fascia', 'Team')
    team.shell([(x0 - .04, y0 - .04), (x1 + .04, y0 - .04), (x1 + .04, y1 + .04), (x0 - .04, y1 + .04)], .5, .08,
               loc=(0, 0, roof - .56))                                                        # top fascia band
    team.shell([(x0 - .02, y0 - .02), (x1 + .02, y0 - .02), (x1 + .02, y1 + .02), (x0 - .02, y1 + .02)], .22, .06,
               loc=(0, 0, 2.78))                                                              # floor band
    rim(a.part('Parapet', 'Concrete'), x0, x1, y0, y1, roof - .02, .72, .32, bevel=.03)
    rim(a.part('Coping', 'Team'), x0 - .02, x1 + .02, y0 - .02, y1 + .02, roof + .69, .08, .36, bevel=0)
    a.part('Roof_deck', 'Asphalt').box((x1 - x0 - .6, y1 - y0 - .6, .05), loc=(xc, yc, roof + .005), bevel=0)
    # Windows: ground floor and first floor on the front, left and rear faces; first floor over the wing.
    for i, x in enumerate((-5.1, -4.0, -.8, .3)):
        _slit(a, '-y', (x, y0, 1.7), w=.8, lit=i % 2 == 0, shutter=i == 1)
    for i, x in enumerate((-5.1, -3.9, -2.4, -.9, .3)):
        _slit(a, '-y', (x, y0, 4.1), w=.8, lit=i != 2, shutter=i in (0, 4))
    for i, y in enumerate((-1.8, .2, 2.2)):
        _slit(a, '-x', (x0, y, 1.7), w=.9, lit=i == 1, shutter=i == 2)
        _slit(a, '-x', (x0, y, 4.1), w=.9, lit=i != 1)
    for i, x in enumerate((-3.4, -1.9, -.4)):
        _slit(a, '+y', (x, y1, 4.1), w=.8, lit=i == 1, shutter=i == 0)
    for i, y in enumerate((-2.0, -.4, 1.2, 2.9)):
        _slit(a, '+x', (x1, y, 4.3), w=.8, lit=i % 2 == 1)
    _blast_door(a, '+y', (-.2, y1, z0), w=1.3, h=2.1)                                          # rear door
    caged_lamp(a, '+y', (-.2, y1, 2.75))
    a.part('Steps', 'Concrete').box((1.8, .5, .12), loc=(-.2, y1 + .25, z0 + .05), bevel=.02, seg=1)

    # Entrance portal on the front with the blast door, lamps, a sign band and a canopy.
    px = HQ_TURRET[0]
    portal = a.part('Portal', 'Concrete')
    portal.box((3.2, 1.4, 3.0), loc=(px, y0 - .68, z0 + 1.5), bevel=.08, seg=1, taper=(.97, .97))
    portal.box((3.6, 1.8, .3), loc=(px, y0 - .78, z0 + 3.1), bevel=.05, seg=1)                # canopy slab
    fy = y0 - 1.38
    _blast_door(a, '-y', (px, fy, z0), w=1.7, h=2.2)
    fbox(a.part('Sign', 'Team'), '-y', (px, fy, 2.95), (2.4, .05, .3), out=.02)
    for s in (-1, 1):
        caged_lamp(a, '-y', (px + s * 1.35, fy, 2.25))
    # Sandbag chicane in front of the door.
    bags = a.part('Sandbags', 'Sandbag')
    for course in range(3):
        bag_run(bags, rng, (px - 1.5, -5.25), (px + 1.0, -5.25), z0 + .14 + course * .23, half=course % 2 == 1)
    # HESCO walls and jersey barriers along the front, the flag at the front left.
    _hesco_run(a, (-5.9, -5.1), (-4.83, -5.1), 2)
    _hesco_run(a, (-.3, -5.1), (.77, -5.1), 2)
    for x in (1.9, 3.7, 5.5):
        _jersey(a, x, -5.4, length=1.7)
    # The flag stands outside the guns' reach and flies forwards, away from their sweep.
    flag(a, -6.6, -4.9, z0, 8.0, w=1.8, h=1.1, phase=.8, yaw=-R90)
    a.part('Obstruction_lights', 'LavaGlow').sphere(.08, loc=(-6.6, -4.9, z0 + 8.12), seg=6, rings=4)
    # Floodlights on wall brackets at the front corners, below the parapet.
    for x, yaw in ((x0 + .4, -.5), (x1 - .4, .5)):
        a.part('Flood_brackets', 'Steel').box((.1, .5, .1), loc=(x, y0 - .22, 4.95), bevel=0)
        flood_head(a, (x, y0 - .5, 4.95), yaw=yaw, tilt=.5, size=(.5, .26, .36))

    # Corner bastion tower at the rear left, carrying the flak nest.
    # Its deck (6.3 m) stays under the guns' barrels, and its sandbags ring only the three sides away from the
    # turret, outside the barrels' reach.
    fx, fy_, tz, tw = -5.35, 4.25, 6.3, 2.6
    conc.prism(chamfered(tw, tw, .5), tz - z0 + .02, loc=(fx, fy_, (z0 - .02 + tz) / 2), axis='Z', bevel=.08, seg=1)
    team.shell(chamfered(tw + .12, tw + .12, .52), .4, .08, loc=(fx, fy_, tz - .62))
    for y in (3.7, 4.6):
        _slit(a, '-x', (fx - tw / 2, y, 2.4), w=.5, h=.3, lit=y > 4)
    _slit(a, '+y', (fx, fy_ + tw / 2, 2.4), w=.6, h=.3, lit=False)
    a.part('Tower_deck', 'Asphalt').prism(chamfered(tw - .3, tw - .3, .4), .05, loc=(fx, fy_, tz + .005), axis='Z',
                                          bevel=0)
    away = math.atan2(fy_ - HQ_TURRET[1], fx - HQ_TURRET[0])
    for course in range(2):
        bag_arc(bags, rng, 1.2, away - 1.95, away + 1.95, tz + .14 + course * .22, size=(.62, .36, .22),
                half=course == 1, cx=fx, cy=fy_)
    _flak_mount(a, (fx, fy_, tz + .03))
    ladder(a.part('Ladder', 'Steel'), (fx + tw / 2 + .12, 4.9, roof), tz + .5, R90, width=.44, step=.3, rung=.03)

    # Roof: the gun drum, hatch, vents, air-conditioning units, whips (all low inside the gun's sweep).
    gx, gy = HQ_TURRET
    a.part('Drum', 'Concrete').cyl(2.15, .78, loc=(gx, gy, roof + .39), seg=28, bevel=.04, bseg=1)
    for k in range(28):
        u = (k + .5) * TAU / 28
        a.part('Drum_band', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.46, .06, .16), loc=(gx + 2.16 * math.cos(u), gy + 2.16 * math.sin(u), roof + .6), rot=(0, 0, u + R90),
            bevel=0)
    a.part('Race', 'Steel').cyl(1.95, .08, loc=(gx, gy, roof + .81), seg=28, bevel=.02, bseg=1)
    a.part('Roof_hatch', 'Armor').box((.9, .9, .14), loc=(-.4, 3.8, roof + .06), bevel=.03, seg=1)
    for x, y in ((-.2, 2.4), (-4.9, -2.3), (.4, -2.3)):
        a.part('Vents', 'Steel').cyl(.16, .5, loc=(x, y, roof + .25), seg=8, bevel=0)
        a.part('Vent_caps', 'Armor').cyl(.26, .07, loc=(x, y, roof + .5), r2=.16, seg=8, bevel=0)
    for x in (-2.4, -1.2):
        a.part('Aircon', 'Fuel').box((.8, .9, .5), loc=(x, 4.2, roof + .25), bevel=.03, seg=1)
        a.part('Aircon_fans', 'Rubber').cyl(.28, .03, loc=(x, 4.2, roof + .51), seg=12, bevel=0)
    _antenna(a, None, .7, 4.6, roof + .7, 3.2)
    _antenna(a, None, -3.3, 4.7, roof + .7, 2.4)
    a.part('Cable_tray', 'Steel').box((.3, 2.4, .08), loc=(.85, 3.4, roof + .1), bevel=0)

    # Signals wing on the right with the helipad roof.
    wx0, wx1, wy0, wy1, wz = 1.2, 6.8, -4.6, 1.5, 3.4
    wing = a.part('Wing', 'Concrete')
    wing.box((wx1 - wx0 + .1, wy1 - wy0, wz - z0 + .02), loc=((wx0 + wx1) / 2 - .05, (wy0 + wy1) / 2, (z0 - .02 + wz) / 2),
             bevel=.08, seg=1)
    team.shell([(wx0 + .06, wy0 - .04), (wx1 + .04, wy0 - .04), (wx1 + .04, wy1 + .04), (wx0 + .06, wy1 + .04)], .35,
               .08, loc=(0, 0, wz - .4))
    rim(a.part('Parapet', 'Concrete'), wx0 + .1, wx1, wy0, wy1, wz - .02, .3, .22, bevel=0)
    for i, x in enumerate((2.2, 3.4, 4.6, 5.8)):
        _slit(a, '-y', (x, wy0, 1.6), w=.7, h=.36, lit=i != 2, shutter=i == 3)
    for i, y in enumerate((-3.4, -1.9, -.4)):
        _slit(a, '+x', (wx1, y, 1.6), w=.7, h=.36, lit=i == 1)
    fbox(a.part('Side_door', 'Armor'), '+x', (wx1, .7, z0 + 1.05), (1.0, .08, 2.1), out=.02, bevel=.015)
    caged_lamp(a, '+x', (wx1, .7, 2.6))
    ladder(a.part('Ladder', 'Steel'), (5.9, wy1 + .3, z0), wz + .6, 0, width=.44, step=.34, rung=.03)
    for z in (1.2, 2.6):
        a.part('Ladder', 'Steel').box((.04, .3, .04), loc=(5.9, wy1 + .15, z), bevel=0)
    # Helipad: asphalt deck, Team border, white ring and H, edge lights, a windsock.
    hx, hy, hs, hz = (wx0 + wx1) / 2 + .05, (wy0 + wy1) / 2, 5.0, wz + .02
    a.part('Pad', 'Asphalt').box((hs, hs, .05), loc=(hx, hy, hz), bevel=0)
    e, bw = hs / 2 - .2, .28
    for s in (-1, 1):
        team.box((2 * e + bw, bw, .03), loc=(hx, hy + s * e, hz + .03), bevel=0)
        team.box((bw, 2 * e - bw, .03), loc=(hx + s * e, hy, hz + .03), bevel=0)
    paint = a.part('Pad_markings', 'PlasterWhite')
    paint.shell(_circle(1.95, 24, cx=hx, cy=hy), .03, .22, loc=(0, 0, hz + .012))
    for s in (-1, 1):
        paint.box((.36, 1.9, .035), loc=(hx + s * .62, hy, hz + .042), bevel=0)
    paint.box((1.0, .34, .025), loc=(hx, hy, hz + .037), bevel=0)
    d = e + .02
    for lx, ly in [(hx + i * d, hy + j * d) for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j]:
        a.part('Edge_light_bases', 'Armor').cyl(.09, .04, loc=(lx, ly, hz + .04), seg=6, bevel=0)
        a.part('Edge_lights', 'Lamp').sphere((.06, .06, .03), loc=(lx, ly, hz + .06), seg=6, rings=4, cut=0.0)
    sock = a.part('Windsock', 'SafetyStripe')
    a.part('Windsock_pole', 'Steel').cyl(.04, 2.2, loc=(wx1 - .25, wy0 + .25, wz + 1.1), seg=6, bevel=0)
    sock.cyl(.16, .7, loc=(wx1 - .25, wy0 - .12, wz + 2.1), rot=(R90 - .3, 0, 0), r2=.09, seg=8, bevel=0)

    # Yard behind the wing: radar tower, generator, drums, HESCO along the right edge.
    rx, ry = 4.4, 3.95
    a.part('Tower_footing', 'Concrete').box((1.8, 1.8, .3), loc=(rx, ry, z0 + .1), bevel=.04, seg=1)
    lattice(a.part('Radar_tower', 'Steel'), rx, ry, z0 + .25, 6.2, .75, .45, 3, leg=.14, brace=.04)
    a.part('Tower_platform', 'Armor').box((1.5, 1.5, .1), loc=(rx, ry, 6.25), bevel=.02, seg=1)
    loop_rail(a.part('Tower_rail', 'Steel'), [(rx - .72, ry - .72, 6.3), (rx + .72, ry - .72, 6.3),
                                              (rx + .72, ry + .72, 6.3), (rx - .72, ry + .72, 6.3)], h=.6, every=1.5)
    a.part('Dish_pedestal', 'Steel').cyl(.25, .35, loc=(rx, ry, 6.47), seg=10, bevel=.02, bseg=1)
    r = a.pivot('Radar', (rx, ry, 6.64))
    a.part('Radar_turntable', 'Armor', r).cyl(.34, .1, loc=(0, 0, .05), seg=12, bevel=.02, bseg=1)
    rf = a.part('Radar_frame', 'Steel', r)
    rf.box((.26, .26, .45), loc=(0, .08, .32), bevel=.02, seg=1)
    _dish(a.part('Radar_dish', 'Medical', r), (0, .2, .7), 1.0, 1.0, depth=.3, seg=14, tilt=.45)
    for sx in (-1, 1):
        rf.limb((sx * .8, -.2, .5), (0, -.8, 1.2), .035, .035, bevel=0)
    a.part('Radar_horn', 'Armor', r).box((.18, .2, .16), loc=(0, -.84, 1.22), bevel=.02, seg=1)
    _beacon(a, rx + .6, ry + .6, 6.3, mat='LavaGlow')
    generator(a, (2.5, 4.3, z0), yaw=R90, size=(2.0, 1.0, 1.2))
    for x, y in ((1.75, 5.7), (2.35, 5.72), (3.2, 5.68)):
        a.part('Drums', 'BarrelRed').cyl(.28, .86, loc=(x, y, z0 + .43), seg=10, bevel=0)
    a.part('Cables', 'Rubber').tube([(2.5, 3.65, .5), (2.1, 3.2, .3), (1.5, 3.0, .3), (1.3, 3.0, .9)], .05, seg=5)
    _hesco_run(a, (6.3, 2.0), (6.3, 4.72), 3)

    # The twin heavy gun turret on the drum.
    t = a.pivot('Turret', (gx, gy, roof + .86))
    a.part('Turret_ring', 'Armor', t).cyl(1.85, .16, loc=(0, 0, .06), seg=24, bevel=0)
    bottom = [(-1.2, -1.75), (1.2, -1.75), (1.75, -1.0), (1.8, 1.3), (1.4, 1.9), (-1.4, 1.9), (-1.8, 1.3), (-1.75, -1.0)]
    top = [(-1.0, -1.02), (1.0, -1.02), (1.55, -.62), (1.6, 1.2), (1.26, 1.75), (-1.26, 1.75), (-1.6, 1.2), (-1.55, -.62)]
    zb, zt = .12, 1.22
    a.part('Turret_body', 'Team', t).loft([[(x, y, zb) for x, y in bottom], [(x, y, zt) for x, y in top]], bevel=.06,
                                          seg=1)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    zg = .62                                                                                  # gun axis
    face_y = -1.75 + (-1.02 + 1.75) * (zg - zb) / (zt - zb)                                   # face at gun height
    # Face plates between and beside the ports, rear hoist door, side stowage.
    tarm.box((.5, .12, .5), loc=(0, face_y - .02, zg + .3), rot=(-.58, 0, 0), bevel=.02, seg=1)
    tarm.box((1.1, .1, .8), loc=(0, 1.86, .6), bevel=.02, seg=1)                              # hoist door
    for s in (-1, 1):
        _stowage_bin(a, (s * 1.8, .3, .35), (.18, 1.2, .5), parent=t, latch_side=s)
    # Roof: sight hoods, commander's cupola with periscopes, hatch, vent, lifting eyes, antennas.
    for s in (-1, 1):
        tarm.box((.46, .44, .3), loc=(s * 1.0, -.62, zt + .1), bevel=.04, seg=1)
        a.part('Sight_glass', 'Glass', t).box((.3, .05, .12), loc=(s * 1.0, -.85, zt + .13), bevel=.01, seg=1)
    tsteel.cyl(.4, .24, loc=(.75, .75, zt + .1), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.34, .08, loc=(.75, .75, zt + .25), seg=16, bevel=.02, bseg=1)
    _periscopes(a, [(.75 + math.cos(u) * .41, .75 + math.sin(u) * .41, zt + .05, u + R90)
                    for u in (-R90 - .6, -R90, -R90 + .6)], parent=t)
    _hatch(a, -.7, 1.0, zt - .01, .3, parent=t)
    tarm.cyl(.22, .12, loc=(0, 1.4, zt + .04), seg=12, bevel=.02, bseg=1)
    for x, y in ((1.3, -.4), (-1.3, -.4), (1.1, 1.6), (-1.1, 1.6)):
        tsteel.tube([(x - .08, y, zt - .02), (x - .08, y, zt + .09), (x + .08, y, zt + .09), (x + .08, y, zt - .02)],
                    .022, seg=4)
    _antenna(a, t, -1.2, 1.55, zt, 1.4)
    _antenna(a, t, 1.25, 1.5, zt, 1.0)
    # Coaxial MG in a ball mount on the face between the guns, on their axis.
    a.part('Coax_mount', 'Armor', t).sphere(.17, loc=(0, face_y + .03, zg), seg=10, rings=6)
    coax = a.part('Coax', 'Steel', t)
    coax.cyl(.035, .55, loc=(0, face_y - .3, zg), rot=FORWARD, seg=8, bevel=0)
    coax.cyl(.05, .12, loc=(0, face_y - .58, zg), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (0, face_y - .64, zg), t)
    # Twin guns: canvas blast bags at the ports, jacketed tapering barrels, muzzle brakes. The breeches run back
    # inside the house, so the game's elevation pivot falls inside the turret face.
    for k, (s, suffix) in enumerate(((1, ''), (-1, '_2'))):                                   # left, right
        x = s * .6
        a.part('Blast_bags', 'Canvas', t).lathe(
            [(.3, 0), (.3, .12), (.25, .19), (.28, .27), (.23, .35), (.25, .43), (.2, .52), (.18, .6)],
            loc=(x, face_y + .3, zg), rot=FORWARD, seg=12)
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        gun.cyl(.15, 1.1, loc=(x, face_y + .55, zg), rot=FORWARD, seg=12, bevel=0)             # breech (hidden)
        y_ = face_y - .25
        gun.cyl(.17, .8, loc=(x, y_ - .4, zg), rot=FORWARD, seg=14, bevel=.02, bseg=1)       # jacket
        gun.cyl(.19, .06, loc=(x, y_ - .8, zg), rot=FORWARD, seg=14, bevel=0)                # jacket band
        Lb = 2.5
        gun.cyl(.12, Lb, loc=(x, y_ - .78 - Lb / 2, zg), r2=.1, rot=FORWARD, seg=14, bevel=.01, bseg=1)
        gun.cyl(.125, .05, loc=(x, y_ - .78 - Lb * .55, zg), rot=FORWARD, seg=14, bevel=0)  # mid band
        mz = y_ - .78 - Lb + .03
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).lathe(
            [(.09, 0), (.15, .08), (.16, .38), (.14, .44), (.08, .44), (.08, .32)], loc=(x, mz, zg), rot=FORWARD,
            seg=14)
        name = 'Muzzle_main' if k == 0 else dotted('Muzzle_main.001')
        a.pivot(name, (x, mz - .44, zg), t)


BUILDERS = {
    'command_vehicle': (command_vehicle, dict(ao_distance=.6, grime_height=.55)),
    'wheeled_gun': (wheeled_gun, dict(ao_distance=.6, grime_height=.55)),
    'counter_battery_radar': (counter_battery_radar, dict(ao_distance=.6, grime_height=.55)),
    'long_sam': (long_sam, dict(ao_distance=.7, grime_height=.6)),
    'headquarters': (headquarters, dict(ao_distance=1.2, grime_height=.8)),
}


if __name__ == '__main__':
    import mb_round6
    mb_round6.main(BUILDERS)
