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


# name: (builder, Asset options).
BUILDERS = {
    'supply_truck': (supply_truck, dict(ao_distance=.5, grime_height=.5)),
    'ammo_carrier': (ammo_carrier, dict(ao_distance=.5, grime_height=.5)),
    'counter_battery_radar': (counter_battery_radar, dict(ao_distance=.5, grime_height=.5)),
    'shahed_truck': (shahed_truck, dict(ao_distance=.5, grime_height=.5)),
    'iron_beam': (iron_beam, dict(ao_distance=.5, grime_height=.5)),
    'heavy_aa': (heavy_aa, dict(ao_distance=.5, grime_height=.5)),
}
