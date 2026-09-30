"""Machine Brigade prompt 25 B2, part 2 (DECISIONS 25B2 "Part 2"): the rest of the models rebuilt from the balance
sheet's "Hình dạng (cho AI vẽ)" notes and drawing guide, at the sheet's target sizes (ground 0.8 x real, aircraft
0.4 x real), drawn for a balance.json "scale" of 1.0 (the data's `modelSize` fits any model's length to the sheet).

The rules are part 1's (mb_p25_models' module notes): silhouette first, the identifying parts 10-20 % over scale,
the triangle budgets (light 1,500-3,000, tanks 3,000-5,000, aircraft 2,000-4,000), nothing thinner than 0.1 m that
would shimmer, every node, mount and muzzle name the game looks up kept, `Point_exhaust` / `Point_fire` empties, Team
as the side's colour. Conventions are mb_vehicles': metres, +Z up, -Y the front, +X the vehicle's left, the origin on
the ground at the hull centre.

Headless: blender --background --python Tools/blender/build_assets.py -- supply_truck
"""
import math

from mathutils import Vector

import mb_detail as hd
import mb_vehicles as mv
from mb_p25_models import _lean_tracks, _scale_asset  # noqa: F401  (shared with part 1)
from mb_vehicles import ACROSS, FORWARD, R90, TAU  # noqa: F401


def _wheels(a, xs, ys, r, width, z=None, seg=10, disc='Armor', hubs=False):
    """Big exposed wheels: a bevelled tyre and a painted disc on each (x, y) (a hub too with hubs=True); z is the
    axle height (r)."""
    z = r if z is None else z
    tyres = a.part('Tyres', 'Rubber')
    discs = a.part('Wheels', disc)
    for x in xs:
        for y in ys:
            tyres.cyl(r, width, loc=(x, y, z), rot=ACROSS, seg=seg, bevel=min(.05, r * .12), bseg=1)
            discs.cyl(r * .56, width + .02, loc=(x, y, z), rot=ACROSS, seg=8, bevel=0)
            if hubs:
                a.part('Hubs', 'Steel').cyl(r * .2, width + .04, loc=(x, y, z), rot=ACROSS, seg=6, bevel=0)


def _lights(a, xs, y, z, facing=-1, size=(.2, .04, .14), lamp='Lamp'):
    """Flush light lenses (a lens in a dark rim) at each x on a face at y looking along `facing`."""
    rim = a.part('Light_rims', 'Undercarriage')
    lens = a.part('Lamps' if lamp == 'Lamp' else 'Tail_lamps', lamp)
    for x in xs:
        rim.box((size[0] + .04, size[1], size[2] + .04), loc=(x, y + facing * .01, z), bevel=0)
        lens.box(size, loc=(x, y + facing * .025, z), bevel=0)


def _ring_gun(a, loc, length=.6, ring=.34):
    """A machine gun on a cab-roof ring mount that turns as the vehicle's `Turret`: the ring, a pintle, the gun
    (`Main_cannon`, drawn 0.12 m thick) with its ammunition can, and `Muzzle_main` at the flash hider."""
    t = a.pivot('Turret', loc)
    a.part('Ring', 'Armor', t).cyl(ring, .08, loc=(0, 0, .04), seg=12, bevel=.02, bseg=1)
    a.part('Mount', 'Steel', t).box((.1, .1, .18), loc=(0, .05, .16), bevel=0)
    gun = a.part('Main_cannon', 'Steel', t)
    gun.box((.14, .4, .15), loc=(0, .05, .3), bevel=.02, seg=1)
    gun.cyl(.06, length, loc=(0, -.15 - length / 2, .31), rot=FORWARD, seg=8, bevel=0)
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.075, .12, loc=(0, -.15 - length - .04, .31), rot=FORWARD, seg=8,
                                                   bevel=0)
    a.part('Ammo_box', 'Armor', t).box((.16, .2, .16), loc=(.16, .08, .26), bevel=.02, seg=1)
    a.pivot('Muzzle_main', (0, -.15 - length - .12, .31), t)
    return t


# ----------------------------------------------------------------------------- HEMTT pair (supply, ammunition)
HEMTT_AXLES = (-3.12, -1.95, 1.2, 2.4)


def _hemtt(a):
    """The M977 HEMTT 8x8 both logistics trucks ride, 8.2 x 2.0 m at 0.8 x (10.2 x 2.44 m real): a flat-fronted
    forward-control cab over the two steered front axles, its big grille below the windscreen, the engine box and
    exhaust stack behind it, a frame to the tail, four axles of big single tyres (two forward, a tandem aft), the
    cab-roof ring gun (`Turret`, `Muzzle_main`). Returns the load bed's floor height."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    dark.box((1.1, 7.9, .3), loc=(0, .05, .72), bevel=0)                                          # frame rails
    _wheels(a, (-.79, .79), HEMTT_AXLES, .48, .36)
    for s in (-1, 1):
        armor.box((.44, 1.95, .08), loc=(s * .79, -2.54, 1.02), bevel=.02, seg=1)                   # front fenders
        armor.box((.44, 2.1, .08), loc=(s * .79, 1.8, 1.02), bevel=.02, seg=1)                      # rear fenders
        steel.box((.14, .5, .14), loc=(s * .88, -.5, .86), bevel=0)                                 # fuel / air tanks
        a.part('Tanks', 'Armor').cyl(.22, 1.0, loc=(s * .74, -.35, .72), rot=FORWARD, seg=8, bevel=0)
        a.part('Glass', 'Glass').box((.03, .7, .42), loc=(s * .985, -3.25, 1.72), bevel=0)          # door windows
        steel.box((.2, .42, .06), loc=(s * .9, -3.6, .78), bevel=0)                                 # cab step
    # Flat-fronted cab above the front wheels, the nose and grille between them, a bumper.
    body.prism([(-4.06, 1.02), (-4.1, 1.45), (-3.98, 2.04), (-2.45, 2.06), (-2.4, 1.02)], 1.98, bevel=.05, seg=1)
    body.box((1.2, .9, .5), loc=(0, -3.62, .8), bevel=.03, seg=1)                                  # nose
    dark.grille(1.0, .34, loc=(0, -4.08, .82), slats=4, depth=.05, thickness=.05)
    dark.grille(1.3, .3, loc=(0, -4.1, 1.26), slats=3, depth=.05, thickness=.05)                   # cab grille
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.84, .04, .48), loc=(s * .45, -4.03, 1.76), rot=(-.2, 0, 0), bevel=0)
    steel.box((2.0, .16, .22), loc=(0, -4.16, .66), bevel=.03, seg=1)                              # bumper
    _lights(a, (-.72, .72), -4.1, .98)
    _lights(a, (-.8, .8), 4.08, 1.0, facing=1, size=(.16, .04, .1), lamp='Alloy')
    armor.box((1.6, .1, .08), loc=(0, -3.99, 2.04), rot=(-.2, 0, 0), bevel=0)                      # visor
    # The engine box behind the cab, the exhaust stack on its left, the air intake on its right.
    armor.box((1.5, .4, .95), loc=(0, -2.2, 1.45), bevel=.04, seg=1)
    steel.cyl(.08, 1.0, loc=(.62, -2.2, 1.9), seg=8, bevel=0)
    armor.box((.3, .3, .5), loc=(-.62, -2.2, 2.05), bevel=.03, seg=1)
    _ring_gun(a, (-.42, -3.3, 2.06))
    a.pivot('Point_exhaust', (.62, -2.2, 2.42))
    a.pivot('Point_fire', (0, -3.2, 2.1))
    return 1.12


def _crate_stack(a, x0, x1, y0, y1, z0, tiers, cols, rows, mat='Crate', lids='Armor', gap=.06):
    """Ammunition crates in a grid, `tiers` high, filling x0..x1 by y0..y1 from z0: from above, a grid of lids."""
    crates = a.part('Crates', mat)
    tops = a.part('Crate_lids', lids)
    w = (x1 - x0 - gap * (cols - 1)) / cols
    d = (y1 - y0 - gap * (rows - 1)) / rows
    h = .3
    for k in range(tiers):
        for i in range(cols):
            for j in range(rows):
                if k == tiers - 1 and (i + j) % 4 == 3:
                    continue     # a gap in the top tier: the stack reads as crates, not a block
                x = x0 + w / 2 + i * (w + gap)
                y = y0 + d / 2 + j * (d + gap)
                crates.box((w, d, h - .02), loc=(x, y, z0 + h / 2 + k * h), bevel=0)
                if k == tiers - 1:
                    tops.box((w * .7, d * .7, .03), loc=(x, y, z0 + (k + 1) * h - .005), bevel=0)


def supply_truck(a):
    """Supply truck (M977 HEMTT cargo truck), 8.2 x 2.0 x 2.1 m: the HEMTT (_hemtt) with a drop-side cargo bed two
    thirds of its length under a tarpaulin on its bows, and the open tail of the bed showing its load (ammunition
    boxes and crates, the sheet: they must show from above), the tailgate down; the cab-roof machine gun."""
    z = _hemtt(a)
    armor = a.part('Armor', 'Armor')
    a.part('Bed', 'Team').box((1.98, 6.1, .14), loc=(0, 1.0, z + .07), bevel=.02, seg=1)
    for s in (-1, 1):
        armor.box((.06, 6.1, .42), loc=(s * .97, 1.0, z + .35), bevel=.01, seg=1)                  # drop sides
    armor.box((1.98, .06, .42), loc=(0, -2.03, z + .35), bevel=.01, seg=1)                        # headboard
    # The tarpaulin over the front two thirds: a rounded canvas cover on bows, straps down its sides.
    tarp = a.part('Tarp', 'Canvas')
    prof = [(-.99, z + .5), (-.99, 1.86), (-.8, 2.02), (-.3, 2.08), (.3, 2.08), (.8, 2.02), (.99, 1.86), (.99, z + .5)]
    tarp.prism(prof, 4.0, loc=(0, -.02, 0), axis='Y', bevel=.03, seg=1)
    straps = a.part('Straps', 'Undercarriage')
    for y in (-1.3, -.3, .7, 1.7):
        straps.box((2.02, .1, .06), loc=(0, y, 2.07), bevel=0)
    # The open tail: ammunition boxes and crates, the tailgate lowered.
    _crate_stack(a, -.86, .86, 2.1, 3.85, z + .14, 2, 3, 3)
    a.part('Ammo_boxes', 'Armor').box((.5, .34, .28), loc=(-.55, 2.35, z + .9), bevel=.02, seg=1)
    a.part('Fuel_cans', 'Hazard').box((.3, .5, .36), loc=(.62, 3.6, z + .79), bevel=.03, seg=1)
    armor.box((1.9, .06, .42), loc=(0, 4.1, z - .2), bevel=.01, seg=1)                            # tailgate, down


def ammo_carrier(a):
    """Ammunition carrier (HEMTT with a load-handling bed, M1120 LHS / M985 class), 8.2 x 2.0 x 2.1 m: the HEMTT
    (_hemtt) with an open steel ammunition rack of square posts and rails over the bed, olive crates stacked in
    three tiers inside it (from above, a grid of crates), and the small knuckle crane folded at the tail: its
    pedestal, slewing column and boom lying forward over the load, the hook block."""
    z = _hemtt(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Bed', 'Team').box((1.98, 5.4, .14), loc=(0, .65, z + .07), bevel=.02, seg=1)
    rack = a.part('Rack', 'Armor')
    for s in (-1, 1):
        for y in (-1.95, -.6, .75, 2.1, 3.3):
            rack.box((.1, .1, .82), loc=(s * .93, y, z + .55), bevel=0)                            # posts
        for zz in (.5, .95):
            rack.box((.1, 5.35, .1), loc=(s * .93, .67, z + zz), bevel=0)                          # rails
    rack.box((1.96, .1, .1), loc=(0, -1.95, z + .95), bevel=0)
    _crate_stack(a, -.84, .84, -1.85, 3.2, z + .14, 3, 3, 5)
    # The small knuckle crane at the tail, folded forward over the load.
    armor.box((1.7, .6, .4), loc=(0, 3.72, z + .2), bevel=.04, seg=1)                             # pedestal
    a.part('Crane', 'Hazard').cyl(.24, .7, loc=(.45, 3.72, z + .75), seg=10, bevel=.03, bseg=1)   # column
    boom = a.part('Crane_boom', 'Hazard')
    boom.box((.22, 2.8, .24), loc=(.45, 2.3, z + 1.16), rot=(-.06, 0, 0), bevel=.03, seg=1)
    boom.box((.2, .5, .3), loc=(.45, 3.62, z + 1.2), bevel=.03, seg=1)                            # knuckle
    steel.box((.16, .16, .2), loc=(.45, .95, z + 1.02), bevel=0)                                  # hook block
    for s in (-1, 1):                                                                             # outriggers
        steel.box((.14, .2, .5), loc=(s * .92, 3.72, z - .1), bevel=0)


# ----------------------------------------------------------------------------- cab-over trucks (FMTV, KamAZ, MAN)
def _truck(a, front, rear, axles, r=.45, tw=.34, width=1.96, cab=1.55, roof=2.0, mg=None):
    """A forward-control military truck (FMTV / KamAZ / MAN HX class) from y = front to rear: a flat-fronted cab
    over the first axle with its windscreen, grille and bumper, the nose between the front wheels, a frame to the
    tail, `axles` of big single tyres under fenders, fuel tanks between the axles, and a machine gun on the cab roof
    (`Mount_mg`, `Muzzle_mg`) at mg = (x, y) if given. Returns the bed's floor height."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    top = 2 * r + .06
    wx = width / 2 - tw / 2 - .01
    dark.box((1.0, rear - front - .4, .28), loc=(0, (front + rear) / 2 + .15, r + .22), bevel=0)   # frame rails
    _wheels(a, (-wx, wx), axles, r, tw)
    groups = [[axles[0]]]
    for y in axles[1:]:
        if y - groups[-1][-1] < 2 * r + .4:
            groups[-1].append(y)
        else:
            groups.append([y])
    for s in (-1, 1):
        for g in groups:
            armor.box((tw + .1, g[-1] - g[0] + 2 * r + .2, .07), loc=(s * wx, (g[0] + g[-1]) / 2, top + .02), bevel=.02,
                      seg=1)
        a.part('Tanks', 'Armor').cyl(.2, .9, loc=(s * (wx - .06), (axles[0] + axles[1]) / 2 + .15, r + .15),
                                     rot=FORWARD, seg=8, bevel=0)
        a.part('Glass', 'Glass').box((.03, cab * .42, .38), loc=(s * (width / 2 + .005), front + cab * .45, roof - .3),
                                     bevel=0)                                                          # door windows
        steel.box((.18, .4, .06), loc=(s * (width / 2 - .08), front + cab * .5, top - .16), bevel=0)  # steps
    body.prism([(front + .04, top), (front, top + .45), (front + .12, roof - .02), (front + cab - .05, roof),
                (front + cab, top)], width, bevel=.05, seg=1)
    body.box((1.1, cab * .7, top - r * .9), loc=(0, front + cab * .38, r * .9 + (top - r * .9) / 2 - .02), bevel=.03,
             seg=1)                                                                                    # nose
    dark.grille(.9, .3, loc=(0, front - .02, top - .2), slats=4, depth=.05, thickness=.05)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((width / 2 - .14, .04, .44), loc=(s * (width / 4 + .02), front + .08, roof - .3), rot=(-.18, 0, 0),
                  bevel=0)
    steel.box((width + .04, .16, .22), loc=(0, front - .06, r + .18), bevel=.03, seg=1)             # bumper
    armor.box((width - .3, .1, .08), loc=(0, front + .12, roof - .02), rot=(-.2, 0, 0), bevel=0)    # visor
    _lights(a, (-(width / 2 - .25), width / 2 - .25), front - .02, top - .12)
    _lights(a, (-(width / 2 - .15), width / 2 - .15), rear + .02, top - .05, facing=1, size=(.16, .04, .1), lamp='Alloy')
    if mg is not None:
        mv._roof_mg(a, None, (mg[0], mg[1], roof), length=.75)
    a.pivot('Point_exhaust', (width / 2 - .2, front + cab + .1, roof + .1))
    steel.cyl(.07, .9, loc=(width / 2 - .2, front + cab + .1, roof - .35), seg=8, bevel=0)           # exhaust stack
    return top + .14


def counter_battery_radar(a):
    """Counter-battery radar (AN/TPQ-53 on an FMTV 6x6), 6.4 x 2.0 x 2.8 m: the truck (_truck), an equipment shelter
    behind the cab with its cooling unit and generator, and on the rear third the big flat phased-array panel raised
    at 45 degrees on its turntable and yoke (the `Radar`, turning as before), drawn 15 % wider than the truck: from
    above, the flat rectangle the sheet asks for. The cab-roof machine gun is its weapon (`Mount_mg`, `Muzzle_mg`)."""
    z = _truck(a, -3.2, 3.2, (-2.4, 1.05, 2.15), mg=(-.45, -2.5))
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Bed', 'Armor').box((1.96, 4.9, .12), loc=(0, .75, z - .06), bevel=.02, seg=1)
    body.box((1.9, 1.7, 1.2), loc=(0, -.72, z + .6), bevel=.05, seg=1)                             # shelter
    armor.box((1.2, .8, .3), loc=(0, -.72, z + 1.35), bevel=.03, seg=1)                             # cooling unit
    a.part('Fan_grilles', 'Undercarriage').cyl(.28, .04, loc=(0, -.72, z + 1.51), seg=10, bevel=0)
    armor.box((.6, .6, .5), loc=(-.6, .4, z + .25), bevel=.04, seg=1)                               # generator
    a.part('Generator_panel', 'Undercarriage').box((.03, .44, .3), loc=(-.91, .4, z + .25), bevel=0)
    steel.cyl(.6, .12, loc=(0, 1.9, z + .06), seg=14, bevel=.02, bseg=1)                           # turntable
    for s in (-1, 1):                                                                               # jacks
        steel.box((.14, .14, .6), loc=(s * .9, 3.0, z - .45), bevel=0)
        steel.box((.3, .3, .05), loc=(s * .9, 3.0, .03), bevel=0)
    r = a.pivot('Radar', (0, 1.9, z + .12))
    tilt = math.radians(45)
    up = Vector((0, -math.sin(tilt), math.cos(tilt)))
    back = Vector((0, math.cos(tilt), math.sin(tilt)))
    yoke = a.part('Radar_yoke', 'Armor', r)
    yoke.box((1.0, .5, .3), loc=(0, 0, .15), bevel=.03, seg=1)
    for s in (-1, 1):
        yoke.limb((s * .5, 0, .2), tuple(Vector((s * .5, 0, 0)) + up * .8 + back * -.12), .12, .16, bevel=0)
    centre = Vector((0, 0, .2)) + up * .95
    a.part('Radar_panel', 'Team', r).box((2.3, .16, 1.9), loc=tuple(centre), rot=(tilt, 0, 0), bevel=.03, seg=1)
    a.part('Radar_face', 'MetalSheet', r).box((2.14, .03, 1.74), loc=tuple(centre + back * .09), rot=(tilt, 0, 0), bevel=0)
    seams = a.part('Radar_seams', 'Undercarriage', r)
    for k in (-.55, 0, .55):
        seams.box((2.16, .03, .05), loc=tuple(centre + back * .11 + up * k), rot=(tilt, 0, 0), bevel=0)
    a.part('Radar_iff', 'Armor', r).box((1.4, .14, .16), loc=tuple(centre + up * 1.0), rot=(tilt, 0, 0), bevel=.02,
                                        seg=1)
    a.pivot('Point_fire', (0, -.7, z + 1.3))


def _shahed_drone(a, t, c, pitch, span=2.3, length=1.85):
    """A Shahed-136 on its rail at c (turret space), nose up the rack: the white delta airframe with its tip winglets,
    the dark nose, the engine and the pusher propeller at the tail."""
    rot = (-pitch, 0, 0)
    fm = mv._frame(tuple(c), rot)
    h = length / 2
    air = a.part('Drone_airframe', 'Fuel', t)
    air.prism([(0, -h), (span / 2, h * .82), (span / 2 - .12, h), (-span / 2 + .12, h), (-span / 2, h * .82)], .07,
              loc=tuple(c), rot=rot, axis='Z', bevel=0)
    for s in (-1, 1):
        air.box((.05, .34, .26), loc=tuple(fm @ Vector((s * (span / 2 - .05), h * .8, .12))), rot=rot, bevel=0)
    air.box((.2, length * .8, .12), loc=tuple(fm @ Vector((0, .05, .05))), rot=rot, bevel=0)          # fuselage
    a.part('Drone_nose', 'Undercarriage', t).cyl(.1, .24, r2=.02, loc=tuple(fm @ Vector((0, -h - .06, .05))),
                                                 rot=(R90 - pitch, 0, 0), seg=6, bevel=0)
    a.part('Drone_engine', 'Armor', t).cyl(.09, .3, loc=tuple(fm @ Vector((0, h - .1, .14))), rot=(R90 - pitch, 0, 0),
                                           seg=6, bevel=0)
    a.part('Drone_prop', 'Undercarriage', t).box((.56, .04, .07), loc=tuple(fm @ Vector((0, h + .08, .14))), rot=rot,
                                                 bevel=0)


def shahed_truck(a):
    """Shahed launcher (a 6x6 truck with a five-rail rack), 6.4 x 2.0 x 2.8 m: the truck (_truck) with a flatbed
    and on it the trainable launch rack (`Turret`): five rails in a staircase, 11 degrees nose-up, a white Shahed-136
    delta on each (its span 15 % over, wider than the truck), one behind and above the next, so from above five
    triangles in a row down the bed (the sheet).
    The rack, rails, rams and drones are named for ModelLibrary's erector (they rise together to fire);
    `Muzzle_main` at the top drone's nose. The cab-roof machine gun (`Mount_mg`, `Muzzle_mg`)."""
    z = _truck(a, -3.2, 3.2, (-2.4, 1.05, 2.15), mg=(.45, -2.5))
    armor = a.part('Armor', 'Armor')
    a.part('Bed', 'Team').box((1.96, 4.9, .14), loc=(0, .75, z - .05), bevel=.02, seg=1)
    for s in (-1, 1):
        armor.box((.08, 4.9, .3), loc=(s * .95, .75, z + .12), bevel=0)                            # bed rails
        a.part('Steel', 'Steel').box((.14, .14, .55), loc=(s * .9, 3.0, z - .42), bevel=0)         # jacks
    a.pivot('Point_fire', (0, -1.0, z + .3))
    t = a.pivot('Turret', (0, 1.0, z + .02))
    a.part('Turntable', 'Steel', t).cyl(.5, .12, loc=(0, 0, .06), seg=12, bevel=0)
    pitch = .19
    hinge = Vector((0, 2.0, .3))
    along = Vector((0, -math.cos(pitch), math.sin(pitch)))
    normal = Vector((0, math.sin(pitch), math.cos(pitch)))
    rot = (-pitch, 0, 0)
    rack = a.part('Rack', 'Armor', t)
    for s in (-1, 1):
        rack.box((.12, 4.1, .14), loc=tuple(hinge + along * 2.05 + Vector((s * .82, 0, 0))), rot=rot, bevel=0)
    for u in (.3, 1.6, 2.9):
        rack.box((1.76, .12, .12), loc=tuple(hinge + along * u), rot=rot, bevel=0)
    rails = a.part('Rack_rails', 'Steel', t)
    top = None
    for k in range(5):
        u, n = .95 + k * .5, .14 + k * .12
        rails.box((.14, 1.7, .08), loc=tuple(hinge + along * (u + .1) + normal * (n - .07)), rot=rot, bevel=0)
        rack.box((.12, .12, max(.12, n)), loc=tuple(hinge + along * (u + .8) + normal * (n / 2 - .02)), rot=rot,
                 bevel=0)                                                                            # rail posts
        c = hinge + along * u + normal * n
        _shahed_drone(a, t, c, pitch)
        top = c + along * 1.25
    a.part('Ram_rods', 'Steel', t).box((.1, .1, 1.2), loc=(0, .2, .55), rot=(.55, 0, 0), bevel=0)
    a.part('Rams', 'Armor', t).box((.16, .16, .5), loc=(0, .05, .28), rot=(.55, 0, 0), bevel=0)
    a.pivot('Muzzle_main', tuple(top + normal * .05), t)


def iron_beam(a):
    """Iron Beam (a high-energy laser on an 8x8 truck), 8.0 x 2.0 x 2.8 m: the truck (_truck) with a long power and
    cooling container, radiator grilles down its flanks and fans on its roof, the laser turret on the container's
    front (`Turret`): a box with the beam director, a big round glass emitter window in a glowing bezel tilted
    30 degrees up (from above, the round window stands out, as the sheet asks; `Main_cannon_*`, it elevates),
    and a small search-radar panel turning at the rear (`Radar`). `Muzzle_main` just ahead of the window."""
    z = _truck(a, -4.0, 4.0, (-3.2, -2.05, 1.85, 2.95), r=.46)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    body.box((1.96, 6.2, .75), loc=(0, .85, z + .375), bevel=.05, seg=1)                           # container
    grilles = a.part('Fan_grilles', 'Undercarriage')
    for s in (-1, 1):
        for y in (-.9, .9, 2.7):
            grilles.grille(1.3, .45, loc=(s * .99, y, z + .38), rot=(0, 0, s * R90), slats=4, depth=.05,
                           thickness=.05)                                                             # radiators
    for y in (1.3, 2.5):
        armor.cyl(.42, .1, loc=(0, y, z + .8), seg=12, bevel=.02, bseg=1)                           # fan shrouds
        grilles.cyl(.36, .03, loc=(0, y, z + .86), seg=12, bevel=0)
    a.part('Coolant_pipes', 'Steel').box((.12, 4.0, .12), loc=(.7, 1.3, z + .81), bevel=0)
    a.pivot('Point_fire', (0, 2.0, z + 1.0))
    t = a.pivot('Turret', (0, -1.25, z + .75))
    steel.cyl(.62, .1, loc=(0, -1.25, z + .77), seg=14, bevel=0)                                    # ring
    a.part('Turret_body', 'Team', t).box((1.4, 1.5, .7), loc=(0, .05, .4), bevel=.06, seg=1, taper=(.9, .92))
    tarm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        tarm.box((.14, .8, .6), loc=(s * .77, .05, .45), bevel=.03, seg=1)                          # trunnion cheeks
    tilt = math.radians(30)
    axis = Vector((0, -math.cos(tilt), math.sin(tilt)))
    c = Vector((0, -.6, .45))
    rot = (R90 - tilt, 0, 0)
    a.part('Main_cannon_pod', 'Armor', t).cyl(.46, .5, loc=tuple(c + axis * .1), rot=rot, seg=16, bevel=.04, bseg=1)
    a.part('Main_cannon_glow', 'TeamGlow', t).cyl(.43, .04, loc=tuple(c + axis * .36), rot=rot, seg=16, bevel=0)
    a.part('Main_cannon_window', 'Glass', t).cyl(.37, .05, loc=tuple(c + axis * .37), rot=rot, seg=16, bevel=0)
    a.part('Main_cannon_sensor', 'Steel', t).box((.3, .3, .2), loc=(.5, .1, .85), bevel=.03, seg=1)
    a.part('Main_cannon_lens', 'Glass', t).box((.2, .03, .12), loc=(.5, -.06, .86), bevel=0)
    a.pivot('Muzzle_main', tuple(c + axis * .6), t)
    steel.box((.16, .16, .5), loc=(0, 3.5, z + 1.0), bevel=0)                                       # radar mast
    r = a.pivot('Radar', (0, 3.5, z + 1.25))
    a.part('Radar_panel', 'Armor', r).box((1.2, .14, .5), loc=(0, 0, .25), rot=(-.25, 0, 0), bevel=.03, seg=1)
    a.part('Radar_face', 'Undercarriage', r).box((1.08, .03, .4), loc=(0, -.08, .25), rot=(-.25, 0, 0), bevel=0)


def heavy_aa(a):
    """Gun-missile air defence (Pantsir-S1 on a KamAZ 8x8), 9.6 x 2.6 x 2.8 m: the truck (_truck) with the crew
    module behind the cab and, on the rear bed, the combat module (`Turret`): a boxy turret carrying the round
    tracking radar on its roof (`Radar`) and the search array at its back (`Radar_search`), a twin 30 mm gun low on
    each side (`Main_cannon` / `_2`, their tips `Muzzle_brake` / `_2`, `Muzzle_main` between them), and over them
    two three-round missile packs a side, 12 tubes in all (from above, the turret with its tubes down both sides, as
    the sheet asks). A `Missile_pack` liner in each pack's middle tube is a launcher (four, 0.38 m apart across:
    ModelLibrary finds them as four), a `Muzzle_missile` (.001 ..) at each pack's mouth."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    z = _truck(a, -4.8, 4.8, (-3.95, -2.75, 1.5, 2.7), r=.5, width=2.1, cab=1.6, roof=2.15)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    body.box((2.06, 1.9, .92), loc=(0, -2.1, z + .46), bevel=.05, seg=1)                          # crew module
    a.part('Glass', 'Glass').box((.03, .5, .28), loc=(1.04, -2.3, z + .6), bevel=0)
    armor.box((2.1, 5.8, .16), loc=(0, 1.9, z + .02), bevel=.03, seg=1)                             # turret bed
    for s in (-1, 1):
        steel.box((.14, .14, .6), loc=(s * .95, 4.3, z - .45), bevel=0)                             # jacks
    a.pivot('Point_fire', (0, -2.1, z + 1.0))
    t = a.pivot('Turret', (0, 1.6, z + .1))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.8, .1, loc=(0, 0, .05), seg=14, bevel=0)                                            # turntable
    a.part('Turret_body', 'Team', t).prism([(-.62, -1.0), (.62, -1.0), (.72, -.75), (.72, 1.0), (-.72, 1.0),
                                            (-.72, -.75)], .7, loc=(0, 0, .45), axis='Z', bevel=.05, seg=1, taper=.94)
    tarm.box((.4, .28, .3), loc=(0, -1.06, .6), bevel=.03, seg=1)                                 # optical tracker
    a.part('Sight', 'Glass', t).box((.26, .03, .16), loc=(0, -1.21, .62), bevel=0)
    # A twin 30 mm gun low on each side, on its trunnion housing.
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .86
        tarm.box((.3, 1.2, .36), loc=(x, -.3, .36), bevel=.04, seg=1)                             # gun housing
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        brake = a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t)
        for dx in (-.07, .07):
            gun.cyl(.045, 1.9, loc=(x + dx, -1.85, .36), rot=FORWARD, seg=8, bevel=0)
            brake.cyl(.065, .16, loc=(x + dx, -2.86, .36), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_main', (-.86, -2.96, .36), t)
    # Two three-round missile packs a side over the guns, tubes across (from above, a row of 12 tube ends).
    for s in (-1, 1):
        for xc in (.6, 1.1):
            x = s * xc
            a.part('Pack_box', 'Team', t).box((.44, 2.3, .22), loc=(x, -.2, .92), bevel=.03, seg=1)
            frame = a.part('Pack_frame', 'Armor', t)
            for y in (-1.1, .7):
                frame.box((.48, .14, .26), loc=(x, y, .92), bevel=0)
            for dx in (-.14, 0, .14):
                a.part('Pack_tubes', 'Undercarriage', t).cyl(.055, .04, loc=(x + dx, -1.36, .92), rot=FORWARD, seg=8,
                                                             bevel=0)
            a.part('Missile_pack', 'Undercarriage', t).cyl(.05, 2.32, loc=(x, -.24, .92), rot=FORWARD, seg=6, bevel=0)
            tsteel.box((.12, .3, .3), loc=(x - s * .2, .2, .72), bevel=0)                          # pack mount
            a.pivot('Muzzle_missile' + ('' if x == -1.1 else '__%03d' % (1 + [-.6, .6, 1.1].index(x))), (x, -1.43, .92), t)
    # The round tracking radar on the roof front and the search array at the back, each turning on its pivot.
    r = a.pivot('Radar', (0, -.3, .8), t)
    a.part('Radar_mast', 'Steel', r).cyl(.08, .16, loc=(0, 0, .08), seg=8, bevel=0)
    mv._dish(a.part('Radar_dish', 'Armor', r), (0, .05, .42), .32, .32, depth=.12, seg=12, tilt=.15)
    rs = a.pivot('Radar_search', (0, .75, .8), t)
    a.part('Search_mount', 'Steel', rs).box((.2, .2, .2), loc=(0, 0, .1), bevel=0)
    a.part('Search_panel', 'Armor', rs).box((1.2, .14, .45), loc=(0, .05, .4), rot=(.2, 0, 0), bevel=.03, seg=1)
    a.part('Search_array', 'MetalSheet', rs).box((1.08, .03, .38), loc=(0, .13, .41), rot=(.2, 0, 0), bevel=0)


# ----------------------------------------------------------------------------- self-propelled howitzer (M109A7)
def artillery(a, detail=False):
    """Self-propelled howitzer (M109A7, the sheet's pick over the CAESAR), 7.8 x 3.1 x 2.9 m with the gun forward:
    a flat-topped tracked hull (front drive, seven road wheels, the sponsons over the tracks) with a sloped glacis and
    the folded travel lock on it, the big square turret set at the rear, and the long 155 mm M284 barrel (4.3 m
    from the mantlet, over half the vehicle's length, reaching 2.6 m past the nose) with its bore evacuator and double-baffle muzzle
    brake; the commander's cupola with the M2 (`Mount_mg`, `Muzzle_mg`), side doors and stowage boxes, the bustle
    rack. `Turret`, `Main_cannon` (it elevates), `Muzzle_brake`, `Muzzle_main`. The high-detail variant adds hubs,
    bolts and vision blocks on the same pivots."""
    hd.mark(a, detail)
    _lean_tracks(a, 1.3, 4.9, .8, .28, 7, .42, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-2.2, .38), (-2.46, .66), (-2.3, .9), (2.4, .9), (2.46, .5), (2.3, .38)], 2.08, bevel=.04, seg=1)
    hull.prism([(-2.47, .84), (-1.72, 1.24), (2.44, 1.26), (2.48, .84)], 3.02, bevel=.05, seg=1)
    for s in (-1, 1):
        _lights(a, (s * 1.2,), -2.2, 1.02, size=(.16, .04, .1))
        _lights(a, (s * 1.25,), 2.49, 1.05, facing=1, size=(.12, .04, .08), lamp='Alloy')
        steel.box((.14, .16, .12), loc=(s * .6, -2.5, .62), bevel=0)                               # tow eyes
        armor.box((.1, .9, .3), loc=(s * 1.46, -1.25, 1.12), bevel=.02, seg=1)                     # side boxes
    mv._hatch(a, .75, -1.62, 1.24, .24, handle=False)                                              # driver
    mv._periscopes(a, [(.75 + dx, -1.93, 1.2, 0) for dx in (-.16, .16)])
    deck = a.part('Deck', 'Undercarriage')
    deck.grille(.9, .7, loc=(-.72, -1.6, 1.22), rot=(-.5, 0, 0), slats=4, depth=.06, thickness=.05)  # engine intake
    armor.box((1.1, .06, .95), loc=(0, 2.49, .78), bevel=.02, seg=1)                               # rear door
    # The travel lock folded down on the glacis: an A-frame with the barrel cradle at its top.
    lock = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        lock.limb((s * .42, -2.28, .98), (s * .12, -1.62, 1.33), .1, .1, bevel=0)
    lock.box((.4, .16, .14), loc=(0, -1.6, 1.36), bevel=.02, seg=1)
    a.pivot('Point_exhaust', (-1.0, -1.9, 1.3))
    a.pivot('Point_fire', (0, -1.2, 1.3))
    # The big square turret at the rear.
    t = a.pivot('Turret', (0, .95, 1.26))
    steel.cyl(1.1, .08, loc=(0, .95, 1.26), seg=16, bevel=0)                                      # turret ring
    a.part('Turret_body', 'Team', t).prism([(-1.24, -1.25), (1.24, -1.25), (1.36, -1.05), (1.36, 1.35), (-1.36, 1.35),
                                            (-1.36, -1.05)], 1.1, loc=(0, 0, .6), axis='Z', bevel=.05, seg=1, taper=.97)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.9, .34, .7), loc=(0, -1.33, .55), bevel=.04, seg=1, taper=(.9, .9))                 # mantlet
    for s in (-1, 1):
        tarm.box((.06, .8, .75), loc=(s * 1.37, .1, .55), bevel=.02, seg=1)                        # side doors
        tarm.box((.3, .9, .4), loc=(s * 1.42, .8, .7), bevel=.03, seg=1)                          # stowage boxes
    tarm.box((2.2, .36, .3), loc=(0, 1.52, .5), bevel=.03, seg=1)                                   # bustle rack box
    a.part('Tarp', 'Canvas', t).cyl(.16, 1.8, loc=(0, 1.52, .78), rot=ACROSS, seg=8, bevel=0)
    mv._hatch(a, .6, .45, 1.15, .26, parent=t, seg=10, handle=False)                               # loader
    a.part('Cupola', 'Armor', t).cyl(.36, .2, loc=(-.75, -.45, 1.2), seg=12, bevel=.03, bseg=1)    # commander
    tarm.box((.4, .3, .26), loc=(.2, -.98, 1.24), bevel=.03, seg=1)                                 # gunner's sight
    a.part('Sight', 'Glass', t).box((.3, .03, .14), loc=(.2, -1.14, 1.25), bevel=0)
    mv._roof_mg(a, t, (-.75, -.45, 1.3), length=.8, shield=False)
    # The 155 mm M284 barrel: 4.3 m from the mantlet, drawn a little thick, bore evacuator, double-baffle brake.
    gun = a.part('Main_cannon', 'Steel', t)
    y0, length, z = -1.5, 4.3, .55
    seg = 14 if detail else 10
    gun.cyl(.13, length, r2=.105, loc=(0, y0 - length / 2, z), rot=FORWARD, seg=seg, bevel=0)
    gun.cyl(.17, .7, loc=(0, y0 - length * .62, z), rot=FORWARD, seg=seg, bevel=.02, bseg=1)      # bore evacuator
    a.part('Main_cannon_cradle', 'Armor', t).box((.44, .9, .4), loc=(0, -1.2, .52), bevel=.03, seg=1)
    brake = a.part('Muzzle_brake', 'Undercarriage', t)
    brake.box((.32, .36, .28), loc=(0, y0 - length - .18, z), bevel=.03, seg=1)
    a.pivot('Muzzle_main', (0, y0 - length - .4, z), t)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        for dx in (-.3, .3):
            for dz in (-.22, .22):
                hd.bolt(det, (dx, -1.51, .55 + dz), hd.FRONT, r=.02, h=.026)
        hd.bolt_ring(det, hd.frame((-.75, -.45, 1.31)), .3, 8, r=.014, h=.02)
        for s in (-1, 1):
            hd.bolt_line(det, (s * 1.41, -.25, .85), (s * 1.41, .45, .85), 5, rot=hd.side_rot(s), r=.014, h=.02)
        mv._periscopes(a, [(-.75 + .3 * math.cos(u), -.45 + .3 * math.sin(u), 1.22, u + R90)
                           for u in (-2.4, -1.6, -.8)], parent=t)
        mv._vent(a, .1, 1.0, 1.16, parent=t)
        mv._eyes(a, [(s * 1.2, -1.05, 1.16, 0) for s in (-1, 1)], parent=t)
        mv._glacis_bolts(a, (-2.47, .84), (-1.72, 1.24), .5, -1.4, 1.4, 12)


# ----------------------------------------------------------------------------- siege tank (2S4 Tyulpan lines)
# The siege tank keeps play-test 6's model units (DECISIONS 21H): VehicleView.Deploy's sieged pose is in them (the
# legs' hinge height and length, the pads, the hull lift, the twin 105 mm's 3 m slide, the siege cannon's 1.9 m run).
# It is drawn at SIEGE_K x the sheet's 6.8 x 2.6 x 2.6 m box (9.1 x 3.5 x 3.5 model units): its data fits the length.
SIEGE_K = 9.08 / 6.8
SIEGE_X = 1.3               # the tracks' and pods' centre line (was 1.55: the sheet's 2.6 m width)


def _siege_leg(a, root, sx, sy):
    """One hydraulic leg hinged on a pod's top at its outer end (sy: -1 front, 1 rear), folded towards the middle of
    the hull; the ram housing at its tip holds the ram and its pad (names and sizes as mb_p22_siege._leg)."""
    from mb_p22_siege import LEG_HINGE_Z, LEG_LENGTH, PAD_UNDER
    lr = 'l' if sx > 0 else 'r'
    hinge = (sx * SIEGE_X, sy * 2.6, LEG_HINGE_Z)
    a.part('Leg_lugs', 'Steel').box((.4, .36, .12), loc=(hinge[0], hinge[1], 1.08), bevel=0)
    p = a.pivot(f'Deploy_{root}_{lr}', hinge)
    arm = a.part(f'Deploy_{root}_{lr}_arm', 'Armor', p)
    arm.box((.28, LEG_LENGTH, .24), loc=(0, -sy * LEG_LENGTH / 2, 0), bevel=.03, seg=1, taper=(.85, .96))
    arm.box((.34, .3, .3), loc=(0, -sy * (LEG_LENGTH - .12), 0), bevel=.03, seg=1)
    a.part(f'Deploy_{root}_{lr}_stripe', 'Team', p).box((.22, .5, .05), loc=(0, -sy * .82, .12), bevel=0)
    steel = a.part(f'Deploy_{root}_{lr}_steel', 'Steel', p)
    steel.cyl(.16, .4, rot=ACROSS, seg=10, bevel=0)                                                  # knuckle
    steel.cyl(.06, 1.0, loc=(0, -sy * .66, .17), rot=FORWARD, seg=6, bevel=0)                        # actuator
    k = a.pivot(f'Deploy_{root}knee_{lr}', (0, -sy * LEG_LENGTH, 0), p)
    a.part(f'Deploy_{root}knee_{lr}_housing', 'Steel', k).cyl(.15, .62, loc=(0, 0, .3), seg=10, bevel=0)
    a.part(f'Deploy_{root}knee_{lr}_collar', 'Armor', k).cyl(.19, .1, loc=(0, 0, .6), seg=10, bevel=0)
    r = a.pivot(f'Deploy_{root}ram_{lr}', (0, 0, 0), k)
    a.part(f'Deploy_{root}ram_{lr}_rod', 'Steel', r).cyl(.08, .68, loc=(0, 0, .35), seg=8, bevel=0)
    pad = a.part(f'Deploy_{root}ram_{lr}_pad', 'Undercarriage', r)
    pad.cyl(.3, .1, loc=(0, 0, -PAD_UNDER + .05), seg=12, bevel=.02, bseg=1)
    claws = a.part(f'Deploy_{root}ram_{lr}_claws', 'Steel', r)
    for dx, dy in ((.27, 0), (-.27, 0), (0, .27), (0, -.27)):
        claws.box((.1, .1, .1), loc=(dx, dy, -.04), bevel=0, taper=(.5, .5))


def siege_tank(a):
    """Siege tank after the sheet's 2S4 Tyulpan, 6.8 x 2.6 x 2.6 m (drawn at SIEGE_K in the rig's units): a low
    tracked hull, its tracks' ends in armoured pods, the four hydraulic legs folded on the pods, the rear spades
    stowed up against the tail plate, and a broad turret drawn in its sieged heading (ModelLibrary turns it round,
    RestTurretYaw): the very big, short 240 mm siege mortar (`Main_cannon_*`, `Muzzle_brake`, `Muzzle_main`; drawn
    a third fatter than before, the silhouette's big round tube, over the engine deck at the tail in tank mode) and
    the twin 105 mm at the other end (`Deploy_gun`, `Muzzle_gun`), the roof M2 (`Mount_mg`, `Muzzle_mg`). Every
    Deploy_* pivot of mb_p22_siege is kept with its children, where VehicleView.Deploy expects it."""
    from mb_p22_siege import BARREL_RUN, GUN_RETRACT  # noqa: F401  (the pose these parts are drawn for)
    hd.mark(a, False)
    _lean_tracks(a, SIEGE_X, 7.3, .8, .3, 6, .56, sprocket=1, teeth=5)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.6, .38), (-4.02, .62), (-4.02, .95), (-3.2, 1.38), (3.3, 1.38), (3.85, 1.3), (3.88, .52),
                (3.5, .38)], 1.96, bevel=.05, seg=1)
    armor.box((1.7, .85, .08), loc=(0, -3.6, 1.2), rot=(math.atan2(.43, .82), 0, 0), bevel=.02, seg=1)  # glacis plate
    for s in (-1, 1):
        steel.box((.16, .2, .16), loc=(s * .6, -4.07, .78), bevel=0)                                  # tow hooks
        for front in (True, False):
            k = -1 if front else 1
            prof = [(k * 3.98, .62), (k * 3.76, 1.1), (k * 1.5, 1.1), (k * 1.38, .92), (k * 1.38, .5), (k * 3.7, .42)]
            a.part('Track_pods', 'Team').prism(prof if front else prof[::-1], .7, loc=(s * SIEGE_X, 0, 0), axis='X',
                                               bevel=.03, seg=1)
            a.part('Pod_trim', 'Armor').box((.74, 1.9, .08), loc=(s * SIEGE_X, k * 2.6, 1.12), bevel=0)
    _lights(a, (-.7, .7), -4.03, .98)
    _lights(a, (-.8, .8), 3.9, 1.1, facing=1, size=(.14, .04, .1), lamp='Alloy')
    mv._periscopes(a, [(dx, -3.18, 1.38, 0) for dx in (-.25, 0, .25)])
    mv._hatch(a, -.55, -2.7, 1.38, .26, handle=False)
    deck.grille(1.5, 1.1, loc=(0, 2.9, 1.39), rot=(-R90, 0, 0), slats=4, depth=.07, thickness=.05)
    for s in (-1, 1):
        steel.cyl(.15, .44, loc=(s * .75, 3.55, 1.55), seg=8, bevel=0)                                # exhausts
        deck.cyl(.12, .05, loc=(s * .75, 3.55, 1.76), seg=8, bevel=0)
        armor.box((.5, .7, .3), loc=(s * .66, 1.95, 1.5), bevel=.03, seg=1)                          # deck bins
    steel.cyl(.95, .1, loc=(0, .1, 1.385), seg=20, bevel=0)                                           # turret ring
    a.pivot('Point_exhaust', (.75, 3.55, 1.85))
    a.pivot('Point_fire', (0, 2.9, 1.45))
    for s in (1, -1):
        _siege_leg(a, 'brace', s, -1)
        _siege_leg(a, 'leg', s, 1)
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        x = s * .72
        for dx in (-.36, .36):
            a.part('Spade_lugs', 'Armor').box((.14, .22, .22), loc=(x + dx, 3.86, .66), bevel=0)
        p = a.pivot(name, (x, 3.93, .66))
        a.part(f'{name}_blade', 'Armor', p).box((.86, .08, 1.0), loc=(0, .09, .55), bevel=.02, seg=1)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .56, rot=ACROSS, seg=8, bevel=0)
        a.part(f'{name}_stripe', 'Team', p).box((.87, .02, .16), loc=(0, .14, .82), bevel=0)
        teeth = a.part(f'{name}_teeth', 'Steel', p)
        for dx in (-.3, -.1, .1, .3):
            teeth.box((.14, .06, .14), loc=(dx, .09, 1.1), bevel=0, taper=(.4, 1))
    # The turret stands on a tall ring (0.45 m over play-test 6's) so it turns clear of the folded legs' ram housings.
    r = a.pivot('Deploy_riser', (0, .1, 1.87))
    a.part('Deploy_riser_column', 'Steel', r).cyl(.85, .72, loc=(0, 0, -.33), seg=18, bevel=0)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.88, .08, loc=(0, 0, -.06), seg=18, bevel=0)
    t = a.pivot('Turret', (0, 0, .04), r)
    a.part('Turret_body', 'Team', t).prism([(-.95, -1.6), (.95, -1.6), (1.25, -.8), (1.25, 1.2), (.95, 1.75),
                                            (-.95, 1.75), (-1.25, 1.2), (-1.25, -.8)], .7, loc=(0, 0, .35), axis='Z',
                                           bevel=.05, seg=1, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        tarm.box((.3, 1.5, .36), loc=(s * 1.2, .2, .32), bevel=.03, seg=1)                            # side plates
    tsteel.box((.24, .28, .24), loc=(-.8, .95, .82), bevel=.03, seg=1)                                 # sight
    a.part('Sight', 'Glass', t).box((.18, .03, .1), loc=(-.8, 1.1, .84), bevel=0)
    mv._hatch(a, .6, .45, .7, .28, parent=t, handle=False)
    tarm.box((1.1, .5, .1), loc=(0, .1, .74), bevel=0)                                                 # roof plate
    # The 240 mm siege mortar at the -Y end, telescoped in: cradle on trunnions, a fat sleeve, the inner tube with
    # its lock collar, the big brake (the tube and brake run out BARREL_RUN sieged).
    z = .92
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((1.2, 1.7, .66), loc=(0, -1.05, z - .06), bevel=.05, seg=1, taper=(.9, .95))
    for s in (-1, 1):
        cradle.cyl(.22, .16, loc=(s * .64, -.45, z), rot=ACROSS, seg=10, bevel=0)                     # trunnions
    sleeve = a.part('Main_cannon_sleeve', 'Steel', t)
    sleeve.cyl(.36, 1.8, loc=(0, -2.7, z), rot=FORWARD, seg=14, bevel=0)
    for y in (-2.2, -3.0):
        sleeve.cyl(.38, .07, loc=(0, y, z), rot=FORWARD, seg=14, bevel=0)                             # bands
    sleeve.cyl(.41, .12, loc=(0, -3.56, z), rot=FORWARD, seg=14, bevel=0)                             # mouth ring
    a.part('Main_cannon_sleeve_team', 'Team', t).cyl(.37, .3, loc=(0, -2.6, z), rot=FORWARD, seg=14, bevel=0)
    tube = a.part('Main_cannon_tube', 'Steel', t)
    tube.cyl(.27, 3.6, loc=(0, -1.8, z), rot=FORWARD, seg=14, bevel=0)
    tube.cyl(.32, .14, loc=(0, -1.8, z), rot=FORWARD, seg=14, bevel=0)                               # lock collar
    brake = a.part('Muzzle_brake', 'Armor', t)
    brake.box((.82, .66, .66), loc=(0, -3.94, z), bevel=.05, seg=1)
    brake.cyl(.33, .1, loc=(0, -4.28, z), rot=FORWARD, seg=14, bevel=0)
    ports = a.part('Muzzle_brake_ports', 'Undercarriage', t)
    for s in (-1, 1):
        for y in (-3.8, -4.06):
            ports.box((.04, .14, .4), loc=(s * .41, y, z), bevel=0)
    a.pivot('Muzzle_main', (0, -4.36, z), t)
    # The twin 105 mm at the +Y end on a mantlet that slides GUN_RETRACT back into the turret sieged.
    p = a.pivot('Deploy_gun', (0, 1.6, .42), t)
    a.part('Gun105_mantlet', 'Armor', p).box((1.0, .5, .46), loc=(0, .05, 0), bevel=.04, seg=1, taper=(.9, .9))
    tubes = a.part('Gun105_tubes', 'Steel', p)
    brakes = a.part('Gun105_brakes', 'Undercarriage', p)
    for x in (-.22, .22):
        tubes.cyl(.085, 2.9, loc=(x, 1.55, 0), rot=FORWARD, seg=8, bevel=0)
        tubes.cyl(.11, 1.0, loc=(x, .8, 0), rot=FORWARD, seg=8, bevel=0)
        brakes.cyl(.11, .28, loc=(x, 3.06, 0), rot=FORWARD, seg=8, bevel=0)
    a.part('Gun105_bridge', 'Armor', p).box((.62, .14, .12), loc=(0, 2.2, 0), bevel=0)
    a.pivot('Muzzle_gun', (-.22, 3.22, 0), p)
    m = a.pivot('Mount_mg', (.8, .95, .74), t)
    mg = a.part('MG_mount', 'Steel', m)
    mg.cyl(.1, .42, loc=(0, 0, .21), seg=8, bevel=0)
    mg.box((.14, .5, .14), loc=(0, -.2, .52), bevel=.02, seg=1)
    mg.cyl(.05, .7, loc=(0, -.75, .52), rot=FORWARD, seg=6, bevel=0)
    a.part('MG_shield', 'Armor', m).box((.5, .05, .32), loc=(0, -.42, .59), bevel=0)
    a.pivot('Muzzle_mg', (0, -1.12, .52), m)


# ----------------------------------------------------------------------------- SAM launcher (Buk TELAR)
def _sam_round(a, t, x, y_nose, z, length, r, wing=(.2, 1.3), fin=(.26, .45), body='Launcher_missiles',
               nose='Launcher_face', mat='Fuel', rot=None):
    """A surface-to-air missile lying along -Y (nose at y_nose) at the round's own length: the white body, the grey
    radome, four long-chord wings mid-body and four tail fins in an X. The noses are `nose` (a launch face)."""
    bodies = a.part(body, mat, t)
    bodies.cyl(r, length - r * 2.4, loc=(x, y_nose + r * 2.4 + (length - r * 2.4) / 2, z), rot=FORWARD, seg=8, bevel=0)
    a.part(nose, 'Armor', t).cyl(r, r * 2.4, r2=.02, loc=(x, y_nose + r * 1.2, z), rot=FORWARD, seg=8, bevel=0)
    fins = a.part(body + '_fins', 'MetalSheet', t)
    for k in range(4):
        u = math.pi / 4 + k * R90
        for (span, chord), yc in ((wing, y_nose + length * .45), (fin, y_nose + length - fin[1] / 2 - .04)):
            d = r + span / 2 - .02
            fins.box((.04, chord, span), loc=(x + math.sin(u) * d, yc, z + math.cos(u) * d), rot=(0, u, 0), bevel=0,
                     taper=(1, .7))


def sam_launcher(a):
    """SAM launcher (Buk-M1 9A310 TELAR on the GM-569 chassis), 7.4 x 2.6 x 3.0 m: a flat tracked hull (six road
    wheels, the driver's cab at the front left), and on its turntable (`Turret`) the Fire Dome tracking radar, a
    squat cylinder with its flat dark array facing forward (a fixed part, `Radar_dome`: it no longer spins), and over
    it the launcher with four 9M38 missiles side by side on their rails, at the round's own 4.44 m (B3: the data's
    length, they used to overflow a 2.45 m box): from above, four long parallel missiles (the sheet). The missiles
    and rails are Launcher_* (they elevate), their noses the `Launcher_face` the rounds leave from, `Muzzle_main` at
    its middle. A hull-top machine gun (`Mount_mg`, `Muzzle_mg`)."""
    hd.mark(a, False)
    _lean_tracks(a, 1.07, 7.0, .72, .28, 6, .44, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-3.4, .36), (-3.6, .62), (-3.4, .8), (3.4, .8), (3.55, .6), (3.4, .36)], 1.66, bevel=.04, seg=1)
    hull.prism([(-3.62, .74), (-3.0, 1.18), (3.45, 1.2), (3.55, .74)], 2.6, bevel=.05, seg=1)
    armor.box((.9, 1.0, .4), loc=(.62, -2.65, 1.34), bevel=.04, seg=1, taper=(.9, .85))          # driver's cab
    a.part('Glass', 'Glass').box((.6, .03, .18), loc=(.62, -3.16, 1.38), bevel=0)
    _lights(a, (-1.0, 1.0), -3.45, 1.0, size=(.16, .04, .1))
    _lights(a, (-1.1, 1.1), 3.56, 1.0, facing=1, size=(.14, .04, .1), lamp='Alloy')
    a.part('Deck', 'Undercarriage').grille(1.2, .8, loc=(-.55, 3.0, 1.19), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.05)
    mv._roof_mg(a, None, (.62, -2.65, 1.54), length=.75, shield=False)
    a.pivot('Point_exhaust', (-.9, 3.4, 1.1))
    a.pivot('Point_fire', (0, 3.0, 1.25))
    t = a.pivot('Turret', (0, .4, 1.2))
    steel.cyl(1.0, .08, loc=(0, .4, 1.2), seg=14, bevel=0)                                        # turret ring
    a.part('Turret_body', 'Team', t).box((2.1, 2.6, .5), loc=(0, .1, .25), bevel=.05, seg=1, taper=(.95, .95))
    tarm = a.part('Turret_armor', 'Armor', t)
    # The Fire Dome tracking radar at the front: a squat drum with its flat array facing forward.
    tarm.cyl(.55, .6, loc=(0, -1.05, .8), seg=12, bevel=.04, bseg=1)
    a.part('Radar_dome', 'Team', t).cyl(.58, .1, loc=(0, -1.05, 1.14), seg=12, bevel=.02, bseg=1)
    a.part('Radar_array', 'Undercarriage', t).box((.8, .06, .5), loc=(0, -1.6, .8), bevel=0)
    # The launcher: a cradle on trunnions at its rear and four 9M38s at their real length on rails.
    y_nose, z, length = -2.35, 1.42, 4.44
    frame = a.part('Launcher_cradle', 'Armor', t)
    frame.box((2.1, .5, .3), loc=(0, 1.55, 1.0), bevel=.03, seg=1)
    for s in (-1, 1):
        tarm.box((.2, .6, .7), loc=(s * .95, 1.55, .72), bevel=.03, seg=1)                        # trunnion posts
        frame.box((.14, 3.2, .16), loc=(s * .95, .2, 1.18), bevel=0)                               # side beams
    rails = a.part('Launcher_rails', 'Steel', t)
    for x in (-.9, -.3, .3, .9):
        rails.box((.12, 3.4, .1), loc=(x, .1, z - .23), bevel=0)
        _sam_round(a, t, x, y_nose, z, length, .17)
    a.pivot('Muzzle_main', (0, y_nose - .06, z), t)


# ----------------------------------------------------------------------------- long-range SAM (S-400 5P85 TEL)
def long_sam(a):
    """Long-range SAM launcher (S-400's 5P85SM TEL on a MAZ-543 8x8), 11.2 x 2.5 x 3.0 m: the MAZ's two small cabs
    either side of the engine at the front, four evenly spaced axles, jacks at the tail, and the erector (`Turret`,
    hinged at the tail as before) carrying four big launch canisters side by side along the whole bed, each at the
    48N6's 6.0 m (B3's round length: it overflowed the old tubes): from above, four tubes as long as the vehicle (the
    sheet). The canisters are Launcher_* (they rise upright to fire); their front covers are the `Launcher_covers`
    face the rounds leave from, `Muzzle_missile` (and `Muzzle_main`) at its middle."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    r = .55
    dark.box((1.1, 10.4, .34), loc=(0, .1, .78), bevel=0)                                         # frame rails
    _wheels(a, (-.94, .94), (-4.3, -2.75, .75, 2.3), r, .42)
    for s in (-1, 1):
        armor.box((.52, 3.0, .08), loc=(s * .94, -3.52, 1.16), bevel=.02, seg=1)                   # fenders
        armor.box((.52, 3.0, .08), loc=(s * .94, 1.52, 1.16), bevel=.02, seg=1)
        # The MAZ-543's two cabs either side of the engine, each with its sloped windscreen.
        body.prism([(-5.55, 1.1), (-5.6, 1.6), (-5.3, 2.35), (-4.0, 2.4), (-3.9, 1.1)], .9, loc=(s * .75, 0, 0),
                   bevel=.05, seg=1)
        a.part('Glass', 'Glass').box((.7, .04, .42), loc=(s * .75, -5.44, 2.0), rot=(-.38, 0, 0), bevel=0)
        a.part('Glass', 'Glass').box((.03, .7, .36), loc=(s * 1.205, -4.6, 2.0), bevel=0)
        steel.box((.14, .14, .7), loc=(s * 1.0, 4.9, .75), bevel=0)                                 # tail jacks
        steel.box((.34, .34, .05), loc=(s * 1.0, 4.9, .03), bevel=0)
        a.part('Tanks', 'Armor').cyl(.22, 1.1, loc=(s * .8, -1.0, .72), rot=FORWARD, seg=8, bevel=0)
    body.box((.56, 1.5, .9), loc=(0, -4.8, 1.55), bevel=.04, seg=1, taper=(.9, .9))                # engine between
    dark.grille(.44, .4, loc=(0, -5.56, 1.4), slats=3, depth=.05, thickness=.04)
    steel.box((2.3, .16, .24), loc=(0, -5.64, .8), bevel=.03, seg=1)                               # bumper
    _lights(a, (-.9, .9), -5.62, 1.2)
    _lights(a, (-1.05, 1.05), 5.12, 1.0, facing=1, size=(.14, .04, .1), lamp='Alloy')
    body.box((2.3, 1.4, .75), loc=(0, -3.0, 1.4), bevel=.05, seg=1)                                # equipment box
    armor.box((2.36, 7.6, .14), loc=(0, 1.3, 1.25), bevel=.02, seg=1)                              # launcher bed
    for y in (-1.7, 3.7):
        armor.box((2.0, .3, .5), loc=(0, y, 1.55), bevel=.03, seg=1)                               # canister rests
    a.pivot('Point_exhaust', (0, -4.3, 2.05))
    a.pivot('Point_fire', (0, -3.0, 1.8))
    # The erector, hinged at the tail, with the four canisters.
    t = a.pivot('Turret', (0, 4.0, 1.48))
    frame = a.part('Launcher_frame', 'Armor', t)
    frame.box((2.4, .5, .5), loc=(0, .45, .76), bevel=.04, seg=1)                                  # tail yoke
    for y in (-5.4, -3.2, -1.0):
        frame.box((2.46, .22, .66), loc=(0, y, .78), bevel=.02, seg=1)                             # canister bands
    for s in (-1, 1):
        steel.box((.2, .5, .6), loc=(s * 1.05, 4.2, 1.55), bevel=0)                                # hinge posts
    tubes = a.part('Launcher_tubes', 'Team', t)
    ends = a.part('Launcher_ends', 'Armor', t)
    covers = a.part('Launcher_covers', 'Undercarriage', t)
    z, front, length = .78, -6.9, 6.0
    for x in (-.87, -.29, .29, .87):
        tubes.cyl(.27, length, loc=(x, front + length / 2, z), rot=FORWARD, seg=12, bevel=0)
        ends.cyl(.29, .14, loc=(x, front + .07, z), rot=FORWARD, seg=12, bevel=0)                  # front rims
        ends.cyl(.29, .14, loc=(x, front + length - .07, z), rot=FORWARD, seg=12, bevel=0)
        covers.cyl(.25, .03, loc=(x, front - .01, z), rot=FORWARD, seg=12, bevel=0)
    a.pivot('Muzzle_missile', (0, front - .05, z), t)
    a.pivot('Muzzle_main', (0, front - .05, z), t)


# ----------------------------------------------------------------------------- super tank (titan)
def titan_tank(a):
    """Super tank (Object 279 / the Ratte's four tracks, the premium card), 11.0 x 5.2 x 3.3 m with its guns forward:
    four track units, two a side under a hull as wide as two tanks (the sheet's silhouette), side skirts over the
    outer pair, a long glacis, two machine-gun sub-turrets on the front corners and the rear one on its own mount
    (`Mount_mg`, `Muzzle_mg`); a big wide turret with twin 140 mm guns 2.5 m past the nose (`Main_cannon` / `_2`,
    `Muzzle_brake` / `_2`, `Muzzle_main` at the left tip), the coaxial gun, an ATGM pod on each turret side 1.95 m
    out (`ATGM_pod`, the missile launchers: two, mirrored, a `Muzzle_missile` at each), active-protection blocks and
    the card's gilt bands."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    _lean_tracks(a, 2.24, 8.0, .98, .34, 6, .6, sprocket=1, teeth=6)
    _lean_tracks(a, 1.5, 7.4, .9, .32, 4, .56, sprocket=1, teeth=5, cleat_pitch=9)             # inner pair, under the hull
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    gilt = a.part('Gilt', 'Gilded')
    armor.prism([(-3.3, .4), (-3.7, .7), (-3.5, .92), (3.7, .92), (3.8, .6), (3.5, .4)], 2.3, bevel=.04, seg=1)
    hull.prism([(-4.05, .92), (-2.7, 1.6), (3.95, 1.62), (4.05, .92)], 3.96, bevel=.06, seg=1)
    for s in (-1, 1):
        mv._skirt(a, s, 2.56, -3.9, 3.9, .6, 1.3, 3, thick=.1, bolts=False)                       # outer skirts
        hull.box((.62, 7.9, .1), loc=(s * 2.24, 0, 1.33), bevel=.02, seg=1)                         # outer fenders
        armor.box((.5, 1.1, .5), loc=(s * 2.2, 2.9, 1.6), bevel=.03, seg=1)                         # rear bins
        gilt.box((.06, 5.0, .08), loc=(s * 2.62, 0, 1.24), bevel=0)                                 # gilt skirt band
        steel.box((.2, .2, .16), loc=(s * .7, -3.75, .72), bevel=0)                                 # tow hooks
        # The front corner sub-turrets: a small dome with twin machine guns each.
        armor.cyl(.42, .3, loc=(s * 1.55, -2.9, 1.52), seg=12, bevel=.04, bseg=1)
        a.part('Sub_turrets', 'Team').sphere((.38, .38, .24), loc=(s * 1.55, -2.9, 1.67), seg=12, rings=5, cut=0)
        for dx in (-.08, .08):
            steel.cyl(.04, .6, loc=(s * 1.55 + dx, -3.45, 1.72), rot=FORWARD, seg=6, bevel=0)
    _lights(a, (-1.0, 1.0), -3.75, 1.02)
    _lights(a, (-1.5, 1.5), 4.06, 1.2, facing=1, size=(.16, .04, .1), lamp='Alloy')
    mv._hatch(a, 0, -2.45, 1.52, .28, handle=False)                                                # driver
    mv._periscopes(a, [(dx, -2.75, 1.47, 0) for dx in (-.18, 0, .18)])
    deck = a.part('Deck', 'Undercarriage')
    deck.grille(2.0, 1.0, loc=(0, 3.4, 1.63), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.05)
    for s in (-1, 1):
        mv._exhaust(a, s * 1.2, 4.05, 1.25, .5, .24)
    steel.cyl(1.55, .1, loc=(0, -.3, 1.62), seg=18, bevel=0)                                       # turret ring
    a.pivot('Point_exhaust', (1.2, 4.1, 1.25))
    a.pivot('Point_fire', (0, 3.4, 1.7))
    # The rear sub-turret on its own mount, at the back of the deck.
    m = a.pivot('Mount_mg', (0, 2.55, 1.62))
    a.part('Rear_turret', 'Team', m).cyl(.5, .36, r2=.42, loc=(0, 0, .18), seg=12, bevel=.04, bseg=1)
    a.part('Rear_turret_armor', 'Armor', m).box((.34, .3, .24), loc=(0, -.42, .26), bevel=.03, seg=1)
    a.part('RWS_gun', 'Steel', m).cyl(.05, .8, loc=(0, -.95, .28), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.38, .28), m)
    # The big wide turret.
    t = a.pivot('Turret', (0, -.3, 1.62))
    a.part('Turret_body', 'Team', t).prism([(-.9, -2.1), (.9, -2.1), (1.75, -1.4), (1.8, 1.2), (1.5, 1.95),
                                            (-1.5, 1.95), (-1.8, 1.2), (-1.75, -1.4)], .95, loc=(0, 0, .48),
                                           axis='Z', bevel=.06, seg=1, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((2.0, .4, .7), loc=(0, -2.12, .5), bevel=.05, seg=1, taper=(.92, .9))                 # mantlet
    for s in (-1, 1):
        tarm.box((.7, .1, .7), loc=(s * 1.35, -1.8, .48), rot=(0, 0, s * .66), bevel=.02, seg=1)    # cheek plates
        tarm.box((.24, 1.5, .5), loc=(s * 1.78, .5, .42), bevel=.03, seg=1)                        # side bins
        a.part('APS', 'Steel', t).box((.3, .3, .2), loc=(s * 1.1, .9, 1.03), bevel=.02, seg=1)    # APS blocks
    tarm.box((2.6, .5, .5), loc=(0, 2.0, .42), bevel=.04, seg=1)                                   # bustle box
    a.part('Turret_gilt', 'Gilded', t).box((3.2, .06, .1), loc=(0, -1.0, .96), bevel=0)
    a.part('Cupola', 'Armor', t).cyl(.34, .24, loc=(-.9, .5, 1.05), seg=12, bevel=.03, bseg=1)
    mv._hatch(a, .9, .5, .95, .3, parent=t, seg=10, handle=False)
    a.part('Sight', 'Glass', t).box((.3, .03, .14), loc=(-.9, .15, 1.1), bevel=0)
    # Twin 140 mm guns, drawn 15 % thick, 2.5 m past the nose.
    y0, length, z = -2.32, 4.35, .52
    for x, suffix in ((-.62, ''), (.62, '_2')):
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        gun.cyl(.12, length, loc=(x, y0 - length / 2, z), rot=FORWARD, seg=10, bevel=0)
        gun.cyl(.15, length * .55, loc=(x, y0 - length * .32, z), rot=FORWARD, seg=10, bevel=0)     # thermal sleeve
        gun.cyl(.19, .5, loc=(x, y0 - length * .4, z), rot=FORWARD, seg=10, bevel=.02, bseg=1)     # fume extractor
        a.part(f'Main_cannon{suffix}_gilt', 'Gilded', t).cyl(.16, .08, loc=(x, y0 - length * .12, z), rot=FORWARD,
                                                             seg=10, bevel=0)
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).cyl(.16, .24, loc=(x, y0 - length - .1, z), rot=FORWARD,
                                                                seg=10, bevel=.02, bseg=1)
    a.pivot('Muzzle_main', (-.62, y0 - length - .24, z), t)
    mv._coax(a, t, 0, -2.3, .7, length=.45, housing=.28)
    # The ATGM pods on the turret sides: two-round boxes, their tube mouths the launch face.
    for s in (-1, 1):
        x = s * 1.95
        a.part('ATGM_pod', 'Armor', t).box((.36, 1.1, .36), loc=(x, -.8, .9), bevel=.03, seg=1)
        tarm.box((.2, .4, .2), loc=(s * 1.8, -.7, .78), bevel=0)                                   # pod mounts
        for dz in (-.08, .08):
            a.part('Tubes_bore', 'Undercarriage', t).cyl(.07, .03, loc=(x, -1.36, .9 + dz), rot=FORWARD, seg=8,
                                                         bevel=0)
    a.pivot('Muzzle_missile', (-1.95, -1.38, .9), t)
    a.pivot('Muzzle_missile__001', (1.95, -1.38, .9), t)


# ----------------------------------------------------------------------------- IFV (M2 Bradley)
def ifv(a):
    """Infantry fighting vehicle (M2 Bradley), 5.2 x 2.9 x 2.4 m: a tracked hull taller than a tank's with a steep
    glacis, six road wheels, front drive, skirts, the big rear ramp; the two-man turret set left of centre (the
    sheet) with the short 25-30 mm gun (`Main_cannon`, `Muzzle_brake`, `Muzzle_main`) and its coaxial gun, and the
    twin TOW box on the turret's left side (`Launcher_box`, `Tubes`, `Muzzle_missile`: ModelLibrary moves them on to
    their own `Deploy_atgm` pivot, raised to fire as a Bradley's). From above: a rectangle with the square missile box
    beside the turret."""
    hd.mark(a, False)
    _lean_tracks(a, 1.23, 5.0, .78, .27, 6, .42, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-2.25, .38), (-2.55, .66), (-2.4, .86), (2.45, .86), (2.55, .6), (2.4, .38)], 1.9, bevel=.04, seg=1)
    hull.prism([(-2.58, .8), (-1.85, 1.62), (2.52, 1.64), (2.58, .8)], 2.86, bevel=.05, seg=1)
    for s in (-1, 1):
        mv._skirt(a, s, 1.46, -2.3, 2.35, .52, .98, 3, thick=.07, bolts=False)
        steel.box((.14, .16, .12), loc=(s * .6, -2.6, .6), bevel=0)                                  # tow hooks
        _lights(a, (s * 1.18,), -2.2, 1.12, size=(.16, .04, .1))
        _lights(a, (s * 1.2,), 2.59, 1.2, facing=1, size=(.12, .04, .08), lamp='Alloy')
    armor.box((1.5, .08, 1.0), loc=(0, 2.59, 1.1), bevel=.02, seg=1)                                # rear ramp
    mv._hatch(a, .8, -1.55, 1.62, .23, handle=False)                                               # driver (left)
    mv._periscopes(a, [(.8 + dx, -1.84, 1.58, 0) for dx in (-.15, .15)])
    a.part('Deck', 'Undercarriage').grille(.8, .7, loc=(-.75, -1.45, 1.63), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.04)                                         # engine (right)
    mv._hatch(a, -.5, 1.9, 1.64, .3, handle=False)                                                 # cargo hatch
    a.pivot('Point_exhaust', (-1.3, -1.2, 1.7))
    a.pivot('Point_fire', (0, 1.3, 1.7))
    # The turret, left of centre, with the short gun and the TOW box on its left side.
    t = a.pivot('Turret', (.22, -.25, 1.64))
    steel.cyl(.78, .08, loc=(.22, -.25, 1.64), seg=14, bevel=0)                                    # ring
    a.part('Turret_body', 'Team', t).prism([(-.55, -.9), (.55, -.9), (.8, -.55), (.8, .75), (-.8, .75), (-.8, -.55)],
                                           .6, loc=(0, 0, .3), axis='Z', bevel=.04, seg=1, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.5, .3, .36), loc=(0, -.98, .3), bevel=.03, seg=1, taper=(.85, .9))                  # mantlet
    tarm.box((.3, .3, .24), loc=(-.5, .1, .7), bevel=.03, seg=1)                                    # sight
    a.part('Sight', 'Glass', t).box((.2, .03, .12), loc=(-.5, -.06, .7), bevel=0)
    mv._hatch(a, .35, .35, .6, .22, parent=t, seg=10, handle=False)
    for s in (-1, 1):
        mv._smoke(a, a.part('Smoke', 'Steel', t), .72, -.4, .45, s, count=2, gap=.08, r=.05, depth=.14)
    cannon = a.part('Main_cannon', 'Steel', t)
    cannon.cyl(.08, .4, loc=(0, -1.3, .3), rot=FORWARD, seg=8, bevel=0)                           # receiver sleeve
    cannon.cyl(.06, 1.05, loc=(0, -1.97, .3), rot=FORWARD, seg=8, bevel=0)
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.085, .14, loc=(0, -2.53, .3), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_main', (0, -2.63, .3), t)
    mv._coax(a, t, -.22, -.95, .36, length=.34, housing=.22)
    # The TOW box on the turret's left side: a twin-tube box on its arm, its tube mouths forward.
    a.part('Launcher_arm', 'Armor', t).box((.16, .5, .2), loc=(.85, .1, .38), bevel=0)
    a.part('Launcher_box', 'Armor', t).box((.44, 1.3, .4), loc=(1.02, -.15, .55), bevel=.03, seg=1)
    for dx in (-.1, .1):
        a.part('Tubes', 'Undercarriage', t).cyl(.075, .03, loc=(1.02 + dx, -.81, .55), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_missile', (1.02, -.86, .55), t)


# ----------------------------------------------------------------------------- light tank (PT-76 / ZBD-05)
def light_tank(a, detail=False):
    """Light tank (PT-76 / ZBD-05 class), 6.1 x 2.6 x 1.8 m: the low amphibious hull with its boat bow (from above,
    a pointed nose), six big road wheels, rear drive, the water-jet ports at the tail, a small flat turret set well
    forward and the long, thin 57 mm gun reaching past the nose (drawn 15 % thick: the silhouette's spike),
    `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, the coaxial gun (`Muzzle_coax`). The high-detail variant adds
    hubs, bolts and vision blocks on the same pivots."""
    hd.mark(a, detail)
    _lean_tracks(a, 1.02, 4.3, .62, .29, 6, .42, sprocket=1, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-2.2, .34), (-2.5, .6), (-2.2, .76), (2.45, .76), (2.55, .5), (2.4, .34)], 1.62, bevel=.04, seg=1)
    # The boat hull: a pointed bow in plan, flat sides over the tracks, a low deck.
    rings = []
    for y, hw, z0, z1 in ((-3.05, .1, .72, .95), (-2.7, .8, .58, 1.1), (-2.1, 1.24, .58, 1.2), (2.3, 1.26, .62, 1.22),
                          (2.62, 1.2, .64, 1.14)):
        rings.append([(hw, y, z0), (hw, y, z1), (-hw, y, z1), (-hw, y, z0)])
    hull.loft(rings, bevel=.04, seg=1)
    for s in (-1, 1):
        armor.box((.05, 4.3, .22), loc=(s * 1.28, .05, .76), bevel=0)                                # track guards
        _lights(a, (s * .85,), -2.4, 1.0, size=(.14, .04, .1))
        _lights(a, (s * 1.0,), 2.63, 1.0, facing=1, size=(.12, .04, .08), lamp='Alloy')
        a.part('Jet_ports', 'Undercarriage').cyl(.16, .05, loc=(s * .55, 2.63, .78), rot=FORWARD, seg=10, bevel=0)
    armor.box((1.6, .6, .06), loc=(0, -2.5, .92), rot=(.5, 0, 0), bevel=.01, seg=1)                    # trim vane
    a.part('Deck', 'Undercarriage').grille(1.2, .9, loc=(0, 1.6, 1.2), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    mv._hatch(a, .0, -1.88, 1.17, .2, handle=False)                                                # driver
    mv._periscopes(a, [(dx, -2.06, 1.14, 0) for dx in (-.15, 0, .15)])
    a.pivot('Point_exhaust', (.8, 2.6, 1.0))
    a.pivot('Point_fire', (0, 1.6, 1.25))
    t = a.pivot('Turret', (0, -.6, 1.22))
    steel.cyl(.82, .08, loc=(0, -.6, 1.22), seg=14, bevel=0)
    a.part('Turret_body', 'Team', t).cyl(.9, .5, r2=.72, loc=(0, .05, .25), seg=12 if not detail else 20, bevel=.04,
                                         bseg=1)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.46, .3, .3), loc=(0, -.86, .24), bevel=.03, seg=1, taper=(.85, .9))                 # mantlet
    a.part('Cupola', 'Armor', t).cyl(.24, .16, loc=(-.35, .25, .56), seg=10, bevel=.02, bseg=1)
    mv._hatch(a, .35, .3, .5, .2, parent=t, seg=10, handle=False)
    tarm.box((.36, .36, .18), loc=(0, .72, .24), bevel=.02, seg=1)                                   # bustle box
    y0, length, z = -.98, 1.95, .25
    gun = a.part('Main_cannon', 'Steel', t)
    gun.cyl(.07, length, loc=(0, y0 - length / 2, z), rot=FORWARD, seg=12 if detail else 8, bevel=0)
    gun.cyl(.095, .9, loc=(0, y0 - .45, z), rot=FORWARD, seg=12 if detail else 8, bevel=0)          # sleeve
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.1, .22, loc=(0, y0 - length - .08, z), rot=FORWARD,
                                                   seg=12 if detail else 8, bevel=.015, bseg=1)
    a.pivot('Muzzle_main', (0, y0 - length - .22, z), t)
    mv._coax(a, t, .26, -.86, .3, length=.34, housing=.22)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        hd.bolt_ring(det, hd.frame((0, .05, .51)), .62, 12, r=.014, h=.02)
        hd.bolt_ring(det, hd.frame((-.35, .25, .65)), .2, 6, r=.012, h=.018)
        mv._periscopes(a, [(-.35 + .22 * math.cos(u), .25 + .22 * math.sin(u), .58, u + R90) for u in (-2.2, -1.2)],
                       parent=t)
        mv._eyes(a, [(s * .7, -.3, .42, 0) for s in (-1, 1)], parent=t)
        for s in (-1, 1):
            hd.bolt_line(a.part('Hull_bolts', 'Steel'), (s * 1.27, -1.7, 1.0), (s * 1.27, 2.0, 1.0), 10,
                         rot=hd.side_rot(s), r=.014, h=.02)


# ----------------------------------------------------------------------------- AA vehicle (Gepard)
def aa_vehicle(a, detail=False):
    """Self-propelled AA gun (Flakpanzer Gepard on the Leopard 1 hull), 6.2 x 3.0 x 2.4 m: the tracked hull (seven
    road wheels, rear drive), the square turret with a 35 mm gun in a pod on each side (`Main_cannon` / `_2`,
    `Muzzle_brake` / `_2`, `Muzzle_main` at the left tip: from above, two long barrels either side), the round
    search-radar dish turning behind the turret (`Radar`), the tracking dish on its front, and a two-round
    missile box on the turret's rear corner (`Launch_tubes`, `Muzzle_missile`, as the Gepard 1A2 upgrades). The
    high-detail variant adds hubs and bolts on the same pivots."""
    hd.mark(a, detail)
    _lean_tracks(a, 1.24, 5.6, .72, .28, 7, .44, sprocket=1, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-2.55, .36), (-2.85, .62), (-2.7, .82), (2.75, .82), (2.85, .55), (2.7, .36)], 1.86, bevel=.04,
                seg=1)
    hull.prism([(-2.95, .78), (-2.2, 1.3), (2.8, 1.32), (2.88, .78)], 2.94, bevel=.05, seg=1)
    for s in (-1, 1):
        mv._skirt(a, s, 1.48, -2.7, 2.6, .5, .96, 3, thick=.07, bolts=False)
        _lights(a, (s * 1.15,), -2.55, 1.1, size=(.16, .04, .1))
        _lights(a, (s * 1.2,), 2.9, 1.08, facing=1, size=(.12, .04, .08), lamp='Alloy')
        armor.box((.4, .9, .26), loc=(s * 1.2, 2.2, 1.44), bevel=.03, seg=1)                         # deck bins
    a.part('Deck', 'Undercarriage').grille(1.4, 1.0, loc=(0, 1.9, 1.33), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    mv._hatch(a, .7, -2.35, 1.12, .22, handle=False)                                               # driver
    a.pivot('Point_exhaust', (1.0, 2.9, 1.1))
    a.pivot('Point_fire', (0, 1.9, 1.4))
    t = a.pivot('Turret', (0, -.1, 1.32))
    steel.cyl(1.0, .08, loc=(0, -.1, 1.32), seg=14, bevel=0)
    a.part('Turret_body', 'Team', t).box((2.0, 2.3, .8), loc=(0, .1, .4), bevel=.05, seg=1, taper=(.93, .95))
    tarm = a.part('Turret_armor', 'Armor', t)
    seg = 12 if detail else 8
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * 1.22
        tarm.box((.42, 1.5, .55), loc=(x, -.25, .5), bevel=.04, seg=1)                             # gun pods
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        gun.cyl(.07, 2.3, loc=(x, -2.1, .55), rot=FORWARD, seg=seg, bevel=0)
        gun.cyl(.09, .5, loc=(x, -1.2, .55), rot=FORWARD, seg=seg, bevel=0)
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).cyl(.1, .2, loc=(x, -3.3, .55), rot=FORWARD, seg=seg,
                                                                bevel=0)
    a.pivot('Muzzle_main', (-1.22, -3.42, .55), t)
    # The tracking dish on the front, the search radar turning behind.
    mv._dish(a.part('Tracking_radar', 'Armor', t), (0, -1.08, .5), .42, .42, depth=.14, seg=12, tilt=.1)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.1, .12, loc=(0, 1.0, .84), seg=8, bevel=0)
    r = a.pivot('Radar', (0, 1.0, .88), t)
    a.part('Radar_mast', 'Steel', r).box((.14, .14, .16), loc=(0, 0, .08), bevel=0)
    mv._dish(a.part('Radar_dish', 'Armor', r), (0, .05, .33), .62, .32, depth=.16, seg=12, tilt=.15)
    # The two-round missile box on the turret's rear left corner.
    a.part('Launcher_box', 'Armor', t).box((.4, 1.0, .3), loc=(.72, .7, .96), bevel=.03, seg=1)
    for dx in (-.09, .09):
        a.part('Launch_tubes', 'Undercarriage', t).cyl(.07, .03, loc=(.72 + dx, .19, .96), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_missile', (.72, .14, .96), t)
    mv._hatch(a, -.55, .5, .8, .24, parent=t, seg=10, handle=False)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        for s in (-1, 1):
            hd.bolt_line(det, (s * 1.44, -.9, .7), (s * 1.44, .4, .7), 6, rot=hd.side_rot(s), r=.014, h=.02)
            hd.bolt_line(a.part('Hull_bolts', 'Steel'), (s * 1.48, -2.3, 1.1), (s * 1.48, 2.3, 1.1), 10,
                         rot=hd.side_rot(s), r=.014, h=.02)
        mv._eyes(a, [(s * .9, -.8, .8, 0) for s in (-1, 1)], parent=t)


# ----------------------------------------------------------------------------- escort hovercraft
def _circle(r, n=16):
    return [(r * math.cos(k * TAU / n), r * math.sin(k * TAU / n)) for k in range(n)]


def hover_gunboat(a):
    """Escort hovercraft (a fast air-cushion gunboat with the AK-630), 14.0 x 3.9 x 3.9 m, the size it has today:
    a low hull on a black rubber skirt, a teardrop from above (a round bow narrowing aft), the wheelhouse amidships
    with its mast and small radar, the six-barrel AK-630 on the foredeck (`Mount_mg`, `Muzzle_mg`, its weapon), and
    two big ducted fans aft in their guard rings (`Propeller`, `Propeller_2`, turning) with rudders behind: from
    above, the two round rings at the tail. Its own model: balance.json borrows `missile_boat` today."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    stations = ((-7.0, .25), (-6.6, 1.05), (-5.8, 1.6), (-4.2, 1.92), (-1.0, 1.95), (2.5, 1.85), (5.2, 1.6),
                (6.7, 1.35), (7.0, 1.1))
    a.part('Skirt', 'Rubber').loft([[(hw * .86, y, 0), (hw, y, .5), (hw * .96, y, .95), (-hw * .96, y, .95),
                                     (-hw, y, .5), (-hw * .86, y, 0)] for y, hw in stations], bevel=0)
    hull.loft([[(hw * .95, y, .9), (hw * .9, y, 1.45), (-hw * .9, y, 1.45), (-hw * .95, y, .9)]
               for y, hw in stations], bevel=.03, seg=1)
    a.part('Skirt_band', 'Undercarriage').loft([[(hw * 1.005, y, .42), (hw * 1.005, y, .56), (-hw * 1.005, y, .56),
                                                 (-hw * 1.005, y, .42)] for y, hw in stations[1:-1]], bevel=0)
    # The wheelhouse amidships, its windows, the mast and radar.
    hull.prism([(-2.6, 1.4), (-2.2, 2.45), (.8, 2.5), (1.0, 1.4)], 2.3, bevel=.05, seg=1)
    a.part('Glass', 'Glass').box((2.0, .05, .34), loc=(0, -2.34, 2.12), rot=(-.36, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Glass', 'Glass').box((.04, 1.6, .3), loc=(s * 1.16, -.9, 2.1), bevel=0)
    armor.box((1.4, 1.2, .12), loc=(0, -.5, 2.54), bevel=.02, seg=1)                                # wheelhouse roof
    steel.box((.16, .16, 1.0), loc=(0, .2, 3.05), bevel=0)                                         # mast
    r = a.pivot('Radar', (0, .2, 3.55))
    a.part('Radar_bar', 'Armor', r).box((1.1, .16, .12), loc=(0, 0, .06), bevel=0)
    a.part('Beacon', 'TeamGlow').box((.12, .12, .1), loc=(0, .2, 3.5), bevel=0)
    # The AK-630 on the foredeck.
    m = a.pivot('Mount_mg', (0, -4.4, 1.45))
    mount = a.part('CIWS_mount', 'Armor', m)
    mount.cyl(.6, .3, loc=(0, 0, .15), seg=12, bevel=.03, bseg=1)
    mount.box((.9, 1.0, .55), loc=(0, .1, .55), bevel=.06, seg=1, taper=(.8, .8))
    guns = a.part('CIWS_barrels', 'Steel', m)
    guns.cyl(.13, 1.5, loc=(0, -1.1, .58), rot=FORWARD, seg=8, bevel=0)
    guns.cyl(.16, .12, loc=(0, -1.8, .58), rot=FORWARD, seg=8, bevel=0)                          # muzzle clamp
    a.pivot('Muzzle_mg', (0, -1.9, .58), m)
    # Two ducted fans aft on pylons, their rudders behind.
    for s, name in ((1, 'Propeller'), (-1, 'Propeller_2')):
        x, y, z = s * .95, 5.3, 2.35
        a.part('Fan_ducts', 'Team').shell(_circle(.95, 16), .6, .12, loc=(x, y - .3, z), rot=(-R90, 0, 0), bevel=0)
        armor.torus(.95, .05, loc=(x, y + .3, z), rot=(-R90, 0, 0), seg=16, ring=4)                  # guard ring lip
        steel.box((.16, .5, .9), loc=(x, y, 1.45 + .45), bevel=0)                                   # pylon
        p = a.pivot(name, (x, y - .05, z))
        a.part('Fan_hubs', 'Armor', p).cyl(.18, .4, loc=(0, 0, 0), rot=FORWARD, seg=8, bevel=0)
        blades = a.part('Fan_blades', 'Undercarriage', p)
        for k in range(5):
            u = k * TAU / 5
            blades.box((.2, .05, .72), loc=(math.cos(u) * .48, 0, math.sin(u) * .48), rot=(0, -u + R90, 0), bevel=0)
        for dx in (-.35, .35):
            armor.box((.06, .5, 1.5), loc=(x + dx, y + .75, z), bevel=0)                               # rudders
    a.pivot('Point_exhaust', (0, 5.9, 2.3))
    a.pivot('Point_fire', (0, -.5, 2.6))


# ----------------------------------------------------------------------------- engineer vehicle (BREM-1)
def engineer_vehicle(a):
    """Engineer and recovery vehicle (BREM-1 on the T-72 hull, M88 class), 6.9 x 3.0 x 2.6 m: a turretless T-72
    hull (six road wheels, rear drive), a dozer blade across the nose wider than the hull (`Blade`, it strokes
    when used), the folding crane lying diagonally along the roof from its pedestal at the front left to the tail
    (from above, the sheet's diagonal), a cargo platform with spare track links at the back, and the commander's
    machine-gun cupola (`Turret`, `Main_cannon`, `Muzzle_main`)."""
    hd.mark(a, False)
    _lean_tracks(a, 1.1, 5.7, .76, .3, 6, .46, sprocket=1, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-2.7, .38), (-2.95, .64), (-2.75, .84), (2.8, .84), (2.92, .56), (2.75, .38)], 1.72, bevel=.04,
                seg=1)
    hull.prism([(-3.0, .8), (-2.2, 1.2), (2.85, 1.24), (2.95, .8)], 2.8, bevel=.05, seg=1)
    for s in (-1, 1):
        armor.box((.5, 5.6, .06), loc=(s * 1.15, 0, 1.2), bevel=0)                                   # fenders
        _lights(a, (s * 1.0,), -2.65, 1.1, size=(.14, .04, .1))
        _lights(a, (s * 1.05,), 2.96, 1.05, facing=1, size=(.12, .04, .08), lamp='Alloy')
        steel.limb((s * 1.1, -2.8, .72), (s * 1.3, -3.2, .5), .12, .12, bevel=0)                    # blade arms
    # The dozer blade across the nose, 3.0 m wide: its own pivot at the hinge.
    b = a.pivot('Blade', (0, -3.1, .55))
    a.part('Blade_plate', 'Armor', b).box((3.0, .14, .8), loc=(0, -.2, -.05), rot=(-.2, 0, 0), bevel=.03, seg=1)
    a.part('Blade_edge', 'Steel', b).box((3.0, .12, .1), loc=(0, -.28, -.46), bevel=0)
    a.part('Blade_stripe', 'Hazard', b).box((3.02, .02, .1), loc=(0, -.29, .2), rot=(-.2, 0, 0), bevel=0)
    # The crane: its pedestal at the front left, the boom lying diagonally back across the roof, the hook block.
    a.part('Crane', 'Armor').cyl(.36, .5, loc=(.8, -1.6, 1.48), seg=10, bevel=.03, bseg=1)
    boom = a.part('Boom_inner', 'Armor')
    boom.limb((.8, -1.6, 1.75), (-.85, 2.7, 1.6), .3, .3, bevel=.03, seg=1)
    boom.box((.34, .4, .34), loc=(.8, -1.6, 1.8), bevel=.03, seg=1)
    a.part('Boom_stripes', 'Hazard').limb((.2, -.05, 1.9), (-.5, 1.75, 1.84), .32, .04, bevel=0)
    steel.box((.2, .2, .26), loc=(-.85, 2.7, 1.36), bevel=0)                                       # hook block
    steel.box((.3, .3, .4), loc=(-.85, 2.7, 1.44), bevel=0)                                        # boom rest
    # The cargo platform at the back, spare track links, the tow bars.
    armor.box((1.3, 1.5, .1), loc=(.55, 2.1, 1.3), bevel=0)
    armor.box((1.3, .08, .3), loc=(.55, 1.35, 1.44), bevel=0)                                      # platform rail
    a.part('Track_links', 'Undercarriage').box((.9, .5, .12), loc=(.55, 2.2, 1.41), bevel=0)
    steel.box((.1, 1.8, .1), loc=(-1.3, .5, 1.3), bevel=0)                                          # tow bar
    a.pivot('Point_exhaust', (-1.2, 2.9, 1.1))
    a.pivot('Point_fire', (0, 1.8, 1.3))
    # The commander's machine-gun cupola at the front right.
    t = a.pivot('Turret', (-.75, -1.3, 1.24))
    a.part('Cupola', 'Team', t).cyl(.42, .3, r2=.36, loc=(0, 0, .15), seg=12, bevel=.03, bseg=1)
    gun = a.part('Main_cannon', 'Steel', t)
    gun.box((.14, .4, .16), loc=(0, -.1, .42), bevel=.02, seg=1)
    gun.cyl(.05, .8, loc=(0, -.7, .42), rot=FORWARD, seg=6, bevel=0)
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.07, .1, loc=(0, -1.12, .42), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_main', (0, -1.2, .42), t)


# ----------------------------------------------------------------------------- M113 pair (smoke, mortar)
def _m113(a, cupola=True):
    """The M113 hull both carriers ride, 3.9 x 2.2 m at 0.8 x: a tall aluminium box with a steep upper glacis,
    five road wheels under the flush sides, front drive, the trim vane, the rear ramp; with cupola=True the
    commander's machine-gun cupola (`Turret`, `Main_cannon`, `Muzzle_main`). Returns the roof height."""
    hd.mark(a, False)
    _lean_tracks(a, .88, 3.7, .62, .25, 5, .36, sprocket=-1, teeth=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.prism([(-1.7, .36), (-1.9, .6), (-1.8, .74), (1.85, .74), (1.95, .5), (1.8, .36)], 1.36, bevel=.03, seg=1)
    roof = 1.72
    hull.prism([(-1.96, .66), (-1.98, 1.02), (-1.4, roof - .02), (1.9, roof), (1.96, .66)], 2.16, bevel=.05, seg=1)
    armor.box((1.9, .5, .05), loc=(0, -1.96, 1.1), rot=(.5, 0, 0), bevel=0)                          # trim vane
    armor.box((1.3, .06, 1.0), loc=(0, 1.97, .95), bevel=.02, seg=1)                                  # rear ramp
    for s in (-1, 1):
        _lights(a, (s * .75,), -1.99, 1.0, size=(.14, .04, .1))
        _lights(a, (s * .85,), 1.97, 1.4, facing=1, size=(.12, .04, .08), lamp='Alloy')
    mv._hatch(a, .6, -1.15, roof, .2, handle=False)                                                 # driver
    a.part('Deck', 'Undercarriage').grille(.6, .5, loc=(-.55, -1.05, roof + .005), rot=(-R90, 0, 0), slats=3,
                                           depth=.04, thickness=.04)
    a.pivot('Point_exhaust', (-.95, -1.3, roof - .2))
    if cupola:
        t = a.pivot('Turret', (-.1, -.55, roof))
        a.part('Cupola', 'Armor', t).cyl(.34, .24, r2=.3, loc=(0, 0, .12), seg=10, bevel=.03, bseg=1)
        a.part('Gun_shield', 'Armor', t).box((.6, .06, .34), loc=(0, -.36, .42), bevel=0)
        gun = a.part('Main_cannon', 'Steel', t)
        gun.box((.14, .4, .14), loc=(0, -.1, .38), bevel=.02, seg=1)
        gun.cyl(.05, .75, loc=(0, -.66, .38), rot=FORWARD, seg=6, bevel=0)
        a.part('Muzzle_brake', 'Undercarriage', t).cyl(.07, .1, loc=(0, -1.06, .38), rot=FORWARD, seg=6, bevel=0)
        a.pivot('Muzzle_main', (0, -1.14, .38), t)
    return roof


def smoke_carrier(a):
    """Smoke generator carrier (M1059 Lynx: the M113 with the smoke generator), 3.9 x 2.2 x 2.0 m: the M113 (_m113)
    with the big cylindrical fog-oil generator lying across the rear roof and its exhaust stack, the fuel drum
    beside it, and a four-tube smoke-grenade launcher on each front corner. From above: a plain box, the
    generator drum at the back (the sheet)."""
    roof = _m113(a)
    a.part('Generator', 'MetalSheet').cyl(.36, 1.7, loc=(0, 1.2, roof + .38), rot=ACROSS, seg=12, bevel=.03, bseg=1)
    a.part('Generator_bands', 'Armor').cyl(.38, .08, loc=(.5, 1.2, roof + .38), rot=ACROSS, seg=12, bevel=0)
    a.part('Generator_bands', 'Armor').cyl(.38, .08, loc=(-.5, 1.2, roof + .38), rot=ACROSS, seg=12, bevel=0)
    a.part('Steel', 'Steel').box((.6, .5, .2), loc=(0, 1.2, roof + .06), bevel=0)                     # cradle
    a.part('Exhaust', 'Undercarriage').cyl(.12, .5, loc=(.7, 1.75, roof + .6), rot=(-.6, 0, 0), seg=8, bevel=0)
    a.part('Fuel', 'BarrelRed').cyl(.2, .5, loc=(-.72, 1.72, roof + .25), seg=10, bevel=.02, bseg=1)
    for s in (-1, 1):
        for k in range(4):
            a.part('Smoke', 'Steel').cyl(.05, .18, loc=(s * .95, -1.35 + k * .1, roof - .12), rot=(-.6, 0, s * .5),
                                         seg=6, bevel=0)
    a.pivot('Point_fire', (0, 1.2, roof + .8))


def mortar_carrier(a):
    """Mortar carrier (M1064: the M113 with a 120 mm mortar), 3.9 x 2.2 x 2.0 m: the M113 (_m113, no cupola) with the
    big rear roof hatch folded open to both sides and the 120 mm mortar standing up through it on its turntable
    (`Turret`, `Mortar_tube`: it elevates, `Muzzle_main` at the mouth, 65 degrees up at rest); the commander's M2 on
    its own mount (`Mount_mg`, `Muzzle_mg`). From above: the big roof opening and the mortar tube."""
    roof = _m113(a, cupola=False)
    dark = a.part('Hatch_well', 'Undercarriage')
    dark.box((1.5, 1.6, .04), loc=(0, .85, roof + .002), bevel=0)                                    # the opening
    for s in (-1, 1):
        a.part('Hatch_lids', 'Team').box((.06, 1.5, .72), loc=(s * 1.12, .85, roof + .02), bevel=.01, seg=1)
        a.part('Armor', 'Armor').box((.08, 1.6, .1), loc=(s * .8, .85, roof + .05), bevel=0)         # coaming
    mv._roof_mg(a, None, (.55, -.9, roof), length=.75, shield=True)
    a.pivot('Point_fire', (0, .85, roof))
    t = a.pivot('Turret', (0, .85, .85))
    a.part('Turret_steel', 'Steel', t).cyl(.5, .1, loc=(0, 0, .05), seg=12, bevel=0)                 # turntable
    a.part('Turret_armor', 'Armor', t).box((.5, .5, .3), loc=(0, .1, .25), bevel=.03, seg=1)        # base plate
    ang = math.radians(65)
    axis = Vector((0, -math.cos(ang), math.sin(ang)))
    base = Vector((0, .15, .35))
    length = 2.1
    a.part('Mortar_tube', 'Steel', t).cyl(.13, length, loc=tuple(base + axis * length / 2), rot=(R90 - ang, 0, 0),
                                          seg=10, bevel=0)
    a.part('Mortar_tube_ring', 'Armor', t).cyl(.16, .1, loc=tuple(base + axis * (length - .05)),
                                               rot=(R90 - ang, 0, 0), seg=10, bevel=0)
    a.part('Sight', 'Glass', t).box((.1, .14, .1), loc=(.2, -.3, 1.0), bevel=0)
    a.part('Turret_armor', 'Armor', t).limb((0, .1, .4), tuple(base + axis * .9), .08, .08, bevel=0)  # bipod
    a.pivot('Muzzle_main', tuple(base + axis * (length + .05)), t)


# ----------------------------------------------------------------------------- pickups (technicals, VBIED)
PICKUP_AXLES = (-1.32, 1.22)


def _pickup(a, body_mat='Team', plated=False):
    """The civilian double-cab pickup (Toyota Hilux class) the technicals and the VBIED are built on, 4.2 x 1.45 m at
    0.8 x: the bonnet, the cab with its windscreen and windows, the load bed with low sides and a drop tailgate, two
    axles of road tyres under arches, bumpers and lights. plated=True leaves the glass off (the VBIED plates it).
    Returns the bed floor height."""
    hd.mark(a, False)
    body = a.part('Body', body_mat)
    dark = a.part('Chassis', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    dark.box((1.0, 3.9, .22), loc=(0, 0, .42), bevel=0)                                             # frame
    _wheels(a, (-.62, .62), PICKUP_AXLES, .33, .24, seg=10, disc='Steel')
    body.prism([(-2.1, .5), (-2.12, .86), (-1.45, .98), (-.98, 1.02), (-.72, 1.44), (-.12, 1.44), (-.06, .5)], 1.44,
               bevel=.05, seg=1)
    for s in (-1, 1):
        dark.box((.18, .9, .2), loc=(s * .66, PICKUP_AXLES[0], .72), bevel=0)                          # arches
        dark.box((.18, .9, .2), loc=(s * .66, PICKUP_AXLES[1], .72), bevel=0)
        if not plated:
            a.part('Glass', 'Glass').box((.03, .55, .32), loc=(s * .725, -.42, 1.2), bevel=0)
    if not plated:
        a.part('Glass', 'Glass').box((1.26, .04, .36), loc=(0, -.85, 1.22), rot=(-.95, 0, 0), bevel=0)
    body.box((1.44, 2.1, .12), loc=(0, 1.0, .72), bevel=.02, seg=1)                                   # bed floor
    for s in (-1, 1):
        body.box((.06, 2.1, .42), loc=(s * .69, 1.0, .98), bevel=0)                                   # bed sides
    body.box((1.44, .06, .42), loc=(0, -.02, .98), bevel=0)
    body.box((1.44, .06, .4), loc=(0, 2.04, .97), bevel=0)                                            # tailgate
    steel.box((1.5, .14, .16), loc=(0, -2.16, .56), bevel=.03, seg=1)                                # bumpers
    steel.box((1.5, .12, .14), loc=(0, 2.1, .56), bevel=.02, seg=1)
    _lights(a, (-.52, .52), -2.13, .78, size=(.22, .04, .1))
    _lights(a, (-.62, .62), 2.08, .9, facing=1, size=(.1, .04, .16), lamp='Alloy')
    dark.grille(.7, .2, loc=(0, -2.13, .66), slats=2, depth=.04, thickness=.04)
    a.pivot('Point_exhaust', (.45, 2.1, .45))
    return .78


def vbied(a):
    """Armoured suicide car (VBIED), 4.2 x 1.5 x 1.8 m: the pickup (_pickup) welded over with patched steel plates
    of uneven sizes and colours (rusted, bare and painted), a thick ram plate on the nose, vision slits instead of
    glass, the bed boxed in over its load, spare wheels and sandbags lashed on; no weapon shows. From above: a rough
    steel box with uneven plate edges (the sheet). `Turret` carries only the roof hatch; `Muzzle_main` is at the
    ram plate (the detonation)."""
    import random
    rng = random.Random(4104)
    _pickup(a, body_mat='Rust', plated=True)
    mats = ('MetalSheet', 'Rust', 'Armor', 'Team')
    # Patched plates over the cab and bonnet, each a little askew, overlapping the body.
    for k, (x, y, z, w, d, h, rot) in enumerate((
            (.0, -1.75, 1.0, 1.52, .7, .08, (-.18, 0, 0)), (.0, -1.2, 1.06, 1.5, .55, .08, (-.05, 0, 0)),
            (.0, -.4, 1.5, 1.52, .72, .08, (0, 0, .04)), (.76, -.45, 1.12, .08, .9, .6, (0, 0, .02)),
            (-.76, -.45, 1.12, .08, .9, .6, (0, 0, -.03)), (.78, -1.5, .8, .08, 1.0, .42, (0, 0, .05)),
            (-.78, -1.5, .8, .08, 1.0, .42, (0, 0, -.04)))):
        a.part(f'Plates_{mats[k % 4]}', mats[k % 4]).box((w, d, h), loc=(x, y, z), rot=rot, bevel=0)
    slits = a.part('Slits', 'Undercarriage')
    slits.box((.9, .04, .06), loc=(0, -.88, 1.3), rot=(-.95, 0, 0), bevel=0)
    for s in (-1, 1):
        slits.box((.03, .4, .05), loc=(s * .81, -.45, 1.28), bevel=0)
    a.part('Ram_plate', 'Armor').box((1.62, .2, .75), loc=(0, -2.28, .72), rot=(-.12, 0, 0), bevel=.03, seg=1)
    # The boxed-in bed over the load, its plates uneven.
    for k in range(4):
        w, d = rng.uniform(.62, .78), rng.uniform(.9, 1.1)
        x = (-1) ** k * .37
        y = .55 if k < 2 else 1.5
        a.part(f'Plates_{mats[(k + 1) % 4]}', mats[(k + 1) % 4]).box((w, d, .1), loc=(x, y, 1.3 + rng.uniform(0, .06)),
                                                                     rot=(rng.uniform(-.05, .05), rng.uniform(-.05, .05), 0),
                                                                     bevel=0)
    a.part('Bed_box', 'Armor').box((1.4, 2.0, .5), loc=(0, 1.0, 1.02), bevel=0)
    a.part('Spare_wheel', 'Rubber').cyl(.3, .2, loc=(.2, 1.3, 1.46), seg=10, bevel=0)
    a.part('Sandbags', 'Sandbag').box((.5, .3, .2), loc=(-.35, 1.7, 1.45), bevel=.05, seg=1)
    t = a.pivot('Turret', (0, -.4, 1.54))
    a.part('Hatch', 'Armor', t).cyl(.22, .08, loc=(0, 0, .04), seg=8, bevel=0)
    a.pivot('Muzzle_main', (0, -2.06, -.9), t)
    a.pivot('Point_fire', (0, 1.0, 1.4))


def rocket_technical(a):
    """Rocket technical (a pickup with the Type 63 12-tube 107 mm launcher), 4.2 x 1.4 x 1.6 m: the pickup
    (_pickup) and on its bed the launcher on a turntable (`Turret`): 12 tubes in three rows of four in a band-clamped
    cluster (`Rocket_tubes`, `Tubes`: they elevate; the dark mouths are the `Tubes_bore` face the rockets leave from,
    `Muzzle_main` at its middle), pointing forward over the cab. From above: a grid of small round tubes on the bed.
    A machine gun on the cab roof (`Mount_mg`, `Muzzle_mg`)."""
    z = _pickup(a)
    mv._roof_mg(a, None, (.3, -.72, 1.44), length=.7, shield=False)
    a.pivot('Point_fire', (0, 1.0, 1.0))
    t = a.pivot('Turret', (0, 1.05, z))
    a.part('Turret_steel', 'Steel', t).cyl(.32, .1, loc=(0, 0, .05), seg=10, bevel=0)
    a.part('Turret_armor', 'Armor', t).box((.5, .5, .36), loc=(0, .1, .28), bevel=.03, seg=1)        # cradle
    tilt = .12
    rot = (R90 - tilt, 0, 0)
    axis = Vector((0, -math.cos(tilt), math.sin(tilt)))
    c = Vector((0, -.1, .72))
    tubes = a.part('Rocket_tubes', 'Crate', t)
    bores = a.part('Tubes_bore', 'Undercarriage', t)
    for row in range(3):
        for col in range(4):
            p = c + Vector((-.3 + col * .2, 0, -.2 + row * .2 + 0)) + Vector((0, 0, 0))
            tubes.cyl(.085, 1.2, loc=tuple(p), rot=rot, seg=8, bevel=0)
            bores.cyl(.06, .02, loc=tuple(p + axis * .61), rot=rot, seg=8, bevel=0)
    bands = a.part('Pod_bands', 'Armor', t)
    for k in (-.35, .35):
        bands.box((.86, .06, .66), loc=tuple(c + axis * k), rot=(-tilt, 0, 0), bevel=0)
    a.pivot('Muzzle_main', tuple(c + axis * .66), t)


def zu23_technical(a):
    """Anti-aircraft technical (a pickup with the ZU-23-2), 4.2 x 1.4 x 1.8 m: the pickup (_pickup) and on its bed the
    twin 23 mm gun on its carriage (`Turret`): the two long barrels side by side (`Main_cannon` / `_2`, drawn 15 %
    long and thick: from above, two long parallel barrels), their flash hiders (`Muzzle_brake` / `_2`), the ammunition
    boxes either side, the gunner's seats and sight. `Muzzle_main` at the left tip."""
    z = _pickup(a)
    a.pivot('Point_fire', (0, 1.0, 1.0))
    t = a.pivot('Turret', (0, 1.1, z))
    a.part('Gun_carriage', 'Armor', t).cyl(.45, .14, loc=(0, 0, .07), seg=10, bevel=0)
    a.part('Turret_armor', 'Armor', t).box((.6, .7, .3), loc=(0, .05, .3), bevel=.03, seg=1)        # cradle
    for s, suffix in ((1, ''), (-1, '_2')):
        x = s * .16
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        gun.box((.14, .6, .16), loc=(x, -.15, .55), bevel=.02, seg=1)                               # receiver
        gun.cyl(.045, 1.85, loc=(x, -1.37, .55), rot=FORWARD, seg=8, bevel=0)
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).cyl(.065, .16, loc=(x, -2.36, .55), rot=FORWARD, seg=8,
                                                                bevel=0)
        a.part('Ammo_boxes', 'Crate', t).box((.2, .4, .3), loc=(s * .42, -.05, .55), bevel=.02, seg=1)
        a.part('Seats', 'Canvas', t).box((.26, .24, .1), loc=(s * .3, .5, .42), bevel=.02, seg=1)
    a.part('Sight', 'Glass', t).box((.1, .1, .1), loc=(.3, .2, .75), bevel=0)
    a.pivot('Muzzle_main', (.16, -2.46, .55), t)


# name: (builder, Asset options).
BUILDERS = {
    'supply_truck': (supply_truck, dict(ao_distance=.5, grime_height=.5)),
    'ammo_carrier': (ammo_carrier, dict(ao_distance=.5, grime_height=.5)),
    'counter_battery_radar': (counter_battery_radar, dict(ao_distance=.5, grime_height=.5)),
    'shahed_truck': (shahed_truck, dict(ao_distance=.5, grime_height=.5)),
    'iron_beam': (iron_beam, dict(ao_distance=.5, grime_height=.5)),
    'heavy_aa': (heavy_aa, dict(ao_distance=.5, grime_height=.5)),
    'artillery': (artillery, dict(ao_distance=.6, grime_height=.55)),
    'siege_tank': (siege_tank, dict(ao_distance=.7, grime_height=.6)),
    'sam_launcher': (sam_launcher, dict(ao_distance=.6, grime_height=.55)),
    'long_sam': (long_sam, dict(ao_distance=.6, grime_height=.55)),
    'titan_tank': (titan_tank, dict(ao_distance=.7, grime_height=.6)),
    'ifv': (ifv, dict(ao_distance=.55, grime_height=.5)),
    'light_tank': (light_tank, dict(ao_distance=.55, grime_height=.5)),
    'aa_vehicle': (aa_vehicle, dict(ao_distance=.55, grime_height=.5)),
    'hover_gunboat': (hover_gunboat, dict(ao_distance=.7, grime_height=.3)),
    'engineer_vehicle': (engineer_vehicle, dict(ao_distance=.55, grime_height=.5)),
    'smoke_carrier': (smoke_carrier, dict(ao_distance=.45, grime_height=.45)),
    'mortar_carrier': (mortar_carrier, dict(ao_distance=.45, grime_height=.45)),
    'vbied': (vbied, dict(ao_distance=.35, grime_height=.4)),
    'rocket_technical': (rocket_technical, dict(ao_distance=.35, grime_height=.4)),
    'zu23_technical': (zu23_technical, dict(ao_distance=.35, grime_height=.4)),
}
