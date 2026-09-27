"""Machine Brigade artillery and new line vehicles, built with frontier_kit and the mb_vehicles* helpers.

Self-propelled guns that read as artillery from the high game camera, not as tanks:
  * artillery: 155 mm wheeled howitzer (CAESAR lineage). A 6x6 truck with a cab-forward armoured crew
    cab, an ammunition module behind it, and the long gun on an open mount at the back of the flatbed,
    laid forward over the cab. A big hydraulic spade is folded up at the tail, stabiliser jacks stand
    ahead of it. The light, fast, fragile gun.
  * howitzer: tracked 155 mm self-propelled howitzer (PzH 2000 / M109A7 lineage). The driver and the
    engine sit low at the front; a large slab-sided turret stands well back and overhangs the tail, with
    a rear ammunition door; a very long 52-calibre gun with a fume extractor and a pepperpot muzzle brake
    reaches 3.5 m past the bow over a travel lock folded on the glacis.
  * siege_tank: 203 mm self-propelled gun (2S7 Pion lineage). A long tracked chassis with exposed running
    gear, the crew cab at the front, ammunition racks along the deck and the gun on an open mount at the
    rear: a massive cradle and a thick, very long barrel, crew seats beside the breech, a loading crane,
    and a huge dozer-type spade raised at the tail.
  * grad_truck: 122 mm multiple rocket launcher (BM-21 Grad on an Ural-375 6x6). A bonneted cab with a
    blast shield over its rear window and folded window shutters, and a 40-tube pack (4 rows of 10) on a
    trainable mount at the rear.
  * atgm_carrier: 8x8 wheeled anti-tank missile carrier (M1134 Stryker ATGM lineage). A slab-sided hull
    covered in bolted applique tiles, a small turret whose raised arm holds a 2x2 missile pod, and a
    remote weapon station.
  * aps_tank: main battle tank with an active protection system (Merkava Mk4 with Trophy lineage). Front
    engine, a long glacis, and a low wedge turret set back on the hull, with a ball-and-chain curtain
    under the bustle, flat radar panels on the turret faces and a launcher head on each turret side.

Rest pose: the three guns are modelled 10 degrees above level, as they travel; the game raises the
barrel from there to its ballistic angle. The Grad pack and the missile pod rest level.

Rig (ModelLibrary.cs): `Turret` yaws. The game gathers the Turret's children whose names start with
main_cannon, muzzle_brake, rocket_tubes, launcher, coax or muzzle_main under an elevating pivot it puts at
the back of their bounds, 6% of their length from the rear and 30% of their height from the bottom. Each
gun group is shaped so that point falls on its trunnion (a breech block and an elevating arc under the
cradle set the rear and the bottom), so the cradle turns about its brackets. Everything that elevates is
named with those prefixes: the gun parts are Main_cannon*, and Main_cannon* parts also recoil, cradle
included. Nothing else uses those prefixes. `Muzzle_main` sits at each main weapon's opening;
`Muzzle_coax` beside the tank gun; `Mount_mg` -> `Muzzle_mg` machine guns; `Aps_left` / `Aps_right`
(children of Turret) at the openings of the tank's two protection-system launchers.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front, origin on the ground at
the footprint centre. Each gun is the highest thing inside its sweep, so the Turret turns all the way
round; the machine guns have clear circles too. Touching parts overlap or stand at least 1 cm apart,
never face to face (coplanar faces z-fight).
"""
import math

from mathutils import Vector

import mb_weapons as wpn
from frontier_kit import chamfered
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _barrel, _basket, _cable, _coax, _face_box, _face_frame,
                         _flank, _frame, _glacis, _grille_frame, _hatch, _headlight, _jerrycans, _periscopes, _rail,
                         _roll, _roof_mg, _rws, _shovel, _stowage_bin, _taillight, _track_links, _tube_mouth, _wheel,
                         tracks)
from mb_vehicles2 import _axis, _gun
from mb_vehicles3 import _jack

PITCH = math.radians(10)  # rest elevation of the three guns


# ----------------------------------------------------------------------------- helpers
def _along(pitch):
    """Rotation that lays a cylinder (local Z) along a bore pitched up by `pitch`, and the one that lays
    a box's local Y along it."""
    return (R90 - pitch, 0, 0), (-pitch, 0, 0)


def _tapered(part, at, s0, s1, r0, r1, rot, seg=14, bevel=.015):
    """Tapered tube along the bore from s0 to s1 (radius r0 at the back, r1 at the front)."""
    part.cyl(r0, s1 - s0, loc=at((s0 + s1) / 2), rot=rot, seg=seg, r2=r1, bevel=bevel, bseg=1)


def _arc(part, at, r_in, r_out, a0, a1, width, steps=5):
    """Elevating arc under a cradle: a flat sector in the bore's vertical plane, centred on the trunnion
    (the origin of `at`), from r_in to r_out, between angles a0 and a1 measured from straight down the
    bore's `up` axis towards the breech (positive) or the muzzle (negative)."""
    def point(ang, r, x):
        return tuple(at(-math.sin(ang) * r, -math.cos(ang) * r, x))
    for k in range(steps):
        b0, b1 = a0 + (a1 - a0) * k / steps, a0 + (a1 - a0) * (k + 1) / steps
        part.loft([[point(b0, r_in, x), point(b1, r_in, x), point(b1, r_out, x), point(b0, r_out, x)]
                   for x in (-width / 2, width / 2)])


# ----------------------------------------------------------------------------- artillery (CAESAR)
def artillery(a):
    """155 mm wheeled self-propelled howitzer (CAESAR 6x6 lineage): a cab-forward armoured crew cab with
    four doors, a big raked windscreen, guarded lamps and a roof machine gun; an ammunition module with
    side locker doors behind it; charge lockers, a fuel tank and tool boxes between the axles; and on the
    flatbed's tail an open gun mount whose long L52 barrel is laid forward over the cab: a cradle with twin
    recuperators, an elevating arc, a breech ring and a double-baffle muzzle brake. The hydraulic
    earth spade is folded up at the tail behind two stabiliser jacks."""
    cab = a.part('Cab', 'Team')
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    axles = (-2.95, 1.5, 2.9)
    for y in axles:
        for s in (-1, 1):
            _wheel(a, s * 1.0, y, .56, .44, seg=16)
    for s in (-1, 1):
        dark.box((.2, 7.9, .3), loc=(s * .46, .05, .92), bevel=.03, seg=1)                     # frame rails
    for y in axles:
        dark.box((1.6, .22, .16), loc=(0, y, .56), bevel=.02, seg=1)                          # axle beams
    for y in (1.5, 2.9):
        dark.box((.3, .4, .34), loc=(0, y, .78), bevel=.02, seg=1)                            # differentials
    # Cab-forward crew cab over the front axle: the body starts above the tyres; a lower nose in front
    # of the wheels and a narrow belly between them.
    front, top = (-4.5, 1.66), (-4.3, 2.62)
    cab.prism([(-4.42, 1.28), front, top, (-4.1, 2.84), (-2.06, 2.84), (-2.0, 1.28)], 2.46, bevel=.06)
    body.box((2.42, .82, .64), loc=(0, -4.05, 1.0), bevel=.05, seg=1)                          # lower nose
    dark.box((1.44, 1.55, .46), loc=(0, -2.875, 1.07), bevel=.03, seg=1)                       # belly
    body.box((2.42, .32, .5), loc=(0, -2.17, 1.07), bevel=.03, seg=1)                          # step block
    steel.box((2.56, .2, .22), loc=(0, -4.52, .82), bevel=.04, seg=1)                          # bumper
    for s in (-1, 1):
        steel.box((.16, .16, .14), loc=(s * .55, -4.66, .8), bevel=.02, seg=1)                  # tow eyes
    dark.grille(1.0, .3, loc=(0, -4.47, 1.105), slats=4, depth=.05, thickness=.04)            # radiator grille
    for z in (.955, 1.255):
        armor.box((1.12, .05, .05), loc=(0, -4.47, z), bevel=0)                                  # grille frame
    # Windscreen: two big raked panes with a centre pillar, a sun visor over them and wipers.
    wr = _glacis(front, top, .5, .012)[2]
    for s in (-1, 1):
        wy, wz, _ = _glacis(front, top, .52, .012)
        glass.box((1.02, .58, .04), loc=(s * .56, wy, wz), rot=(wr, 0, 0), bevel=.012, seg=1)
        py, pz, _ = _glacis(front, top, .52, .02)
        steel.box((.04, .03, .34), loc=(s * .3, py - .02, pz - .12), rot=(wr - .3, 0, 0), bevel=0)  # wipers
    py, pz, _ = _glacis(front, top, .52, .03)
    armor.box((.08, .62, .05), loc=(0, py, pz), rot=(wr, 0, 0), bevel=0)                      # centre pillar
    vy, vz, _ = _glacis(front, top, .98, .04)
    armor.box((2.36, .2, .06), loc=(0, vy - .06, vz + .02), rot=(wr - .9, 0, 0), bevel=.015, seg=1)  # sun visor
    for s in (-1, 1):
        ox = s * 1.23
        # Four doors: side windows, shut lines, handles; steps ahead of and behind the front wheel.
        for y0, y1 in ((-4.0, -3.4), (-3.18, -2.5)):
            glass.box((.04, y1 - y0, .44), loc=(ox + s * .006, (y0 + y1) / 2, 2.3), bevel=.01, seg=1)
            armor.box((.05, y1 - y0 + .1, .06), loc=(ox + s * .012, (y0 + y1) / 2, 2.56), bevel=0)  # rain strip
        for y in (-4.16, -3.3, -2.36):
            armor.box((.03, .04, 1.36), loc=(ox + s * .006, y, 2.04), bevel=0)                 # shut lines
        for y in (-3.52, -2.62):
            steel.box((.04, .16, .05), loc=(ox + s * .015, y, 2.0), bevel=0)                   # handles
        for y, z in ((-3.95, .95), (-3.95, .66), (-2.2, .72)):
            steel.box((.3, .28, .04), loc=(s * 1.1, y, z), bevel=0)                           # steps
        steel.box((.04, .04, .5), loc=(s * 1.26, -3.95, .8), bevel=0)                         # step hanger
        _headlight(a, s * .88, -4.46, 1.1, guard=True)
        a.part('Marker_lights', 'Alloy').box((.14, .04, .08), loc=(s * .88, -4.47, .9), bevel=0)  # indicators
        # Mirrors on arms at the windscreen corners.
        steel.tube([(ox - s * .02, -4.2, 2.45), (ox + s * .06, -4.36, 2.5)], .018, seg=4)
        armor.box((.05, .18, .3), loc=(ox + s * .09, -4.4, 2.42), bevel=.012, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .38), loc=(s * 1.0, -2.3, .72), bevel=0)
    # Cab roof: marker lights, a hatch with the machine gun ring on the left, the air unit, antennas and
    # the travel lock (folded; the gun rests above it) on the front edge.
    for x in (-.55, 0, .55):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x, -4.07, 2.85), bevel=0)
    armor.cyl(.36, .1, loc=(-.62, -3.62, 2.86), seg=16, bevel=.02, bseg=1)                     # MG ring
    _hatch(a, .62, -3.1, 2.84, .27)
    armor.box((.9, .6, .16), loc=(0, -2.5, 2.9), bevel=.03, seg=1)                             # air unit
    dark.grille(.6, .34, loc=(0, -2.5, 2.99), rot=(-R90, 0, 0), slats=4, depth=.04, thickness=.03)
    lock = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        lock.box((.06, .1, .28), loc=(s * .2, -4.0, 2.97), bevel=0)                            # lock posts
    lock.box((.5, .12, .06), loc=(0, -4.0, 3.1), bevel=.01, seg=1)                              # cradle bar
    for s in (-1, 1):
        lock.box((.05, .12, .14), loc=(s * .27, -4.0, 3.18), bevel=0)                           # jaws
    _antenna(a, None, 1.05, -2.25, 2.84, 1.3)
    steel.box((.08, .08, .06), loc=(1.05, -2.25, 2.86), bevel=0)
    _antenna(a, None, -1.05, -2.25, 2.84, .9)
    steel.box((.08, .08, .06), loc=(-1.05, -2.25, 2.86), bevel=0)
    wpn.hmg(a, (-.62, -3.62, 2.91), post=.1, length=.8, ammo=-1)

    # Ammunition module behind the cab: locker doors on both sides, roof hatches and a ladder.
    body.box((2.44, 1.34, 1.08), loc=(0, -1.3, 1.86), bevel=.05, seg=1)
    armor.box((2.3, 1.2, .06), loc=(0, -1.3, 2.41), bevel=.015, seg=1)                          # roof plate
    for s in (-1, 1):
        for y in (-1.62, -.98):
            armor.box((.05, .56, .74), loc=(s * 1.23, y, 1.86), bevel=.012, seg=1)             # locker doors
            steel.box((.04, .05, .16), loc=(s * 1.26, y + .2, 1.9), bevel=0)                  # latches
        steel.box((.04, 1.2, .04), loc=(s * 1.25, -1.3, 2.3), bevel=0)                         # hinge rail
        _rail(a, [(s * 1.1, -1.85, 2.44), (s * 1.1, -1.85, 2.52), (s * 1.1, -.75, 2.52), (s * 1.1, -.75, 2.44)])
    for x in (-.55, .55):
        armor.box((.8, .5, .05), loc=(x, -1.3, 2.45), bevel=.012, seg=1)                        # roof hatches
        steel.box((.3, .04, .04), loc=(x, -1.5, 2.49), bevel=0)
    steel.tube([(.9, -.61, 1.35), (.9, -.61, 2.4)], .022, seg=6)                                # ladder
    steel.tube([(.6, -.61, 1.35), (.6, -.61, 2.4)], .022, seg=6)
    for z in (1.6, 1.9, 2.2):
        steel.box((.3, .03, .035), loc=(.75, -.61, z), bevel=0)
    # Flatbed and the lockers between the axles.
    body.box((2.4, 4.95, .16), loc=(0, 1.72, 1.33), bevel=.03, seg=1)                          # deck
    for s in (-1, 1):
        armor.box((.06, 4.9, .08), loc=(s * 1.2, 1.72, 1.42), bevel=0)                          # deck edges
        for y in (.0, 1.3, 2.6, 3.9):
            steel.box((.04, .1, .06), loc=(s * 1.225, y, 1.3), bevel=0)                         # tie-downs
        armor.box((.4, 1.3, .58), loc=(s * .98, .1, 1.0), bevel=.03, seg=1)                     # charge lockers
        armor.box((.42, 1.32, .05), loc=(s * .98, .1, 1.3), bevel=0)                            # locker lids
        for y in (-.25, .45):
            steel.box((.03, .06, .08), loc=(s * 1.185, y, 1.14), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.0, 3.55, .7), bevel=0)
        _taillight(a, s * .95, 4.22, 1.2)
        steel.box((.2, .12, .16), loc=(s * .4, 4.24, .95), bevel=.02, seg=1)                    # tow eyes
        _jack(a, s * 1.02, 3.86, 1.3)
    steel.cyl(.25, 1.0, loc=(-.95, -1.3, .9), rot=FORWARD, seg=12, bevel=.04, bseg=1)          # fuel tank
    for y in (-1.6, -1.0):
        dark.box((.56, .04, .56), loc=(-.95, y, .9), bevel=0)                                  # tank straps
    armor.box((.4, .9, .42), loc=(.98, -1.3, .92), bevel=.03, seg=1)                           # battery box
    steel.box((.03, .06, .08), loc=(1.185, -1.3, 1.02), bevel=0)
    steel.box((2.3, .18, .2), loc=(0, 4.18, .9), bevel=.03, seg=1)                             # rear bumper
    # Hydraulic earth spade folded up at the tail: a ribbed blade with teeth on its (raised) digging
    # edge, hinged on the frame, with two rams.
    lean = .3
    hinge = Vector((0, 4.3, .74))
    up = Vector((0, math.sin(lean), math.cos(lean)))       # up the folded blade, leaning back
    out = Vector((0, math.cos(lean), -math.sin(lean)))     # its rear face
    srot = (-lean, 0, 0)
    spade = a.part('Spade', 'Armor')
    spade.box((2.1, .12, 1.3), loc=hinge + up * .65, rot=srot, bevel=.03, seg=1)
    for x in (-.78, 0, .78):                                                                   # ribs
        spade.box((.1, .12, 1.14), loc=hinge + up * .62 + out * .09 + Vector((x, 0, 0)), rot=srot, bevel=0)
    spade.box((2.14, .16, .12), loc=hinge + up * .2 + out * .03, rot=srot, bevel=0)             # heel bar
    for x in (-.84, -.42, 0, .42, .84):                                                        # teeth
        steel.box((.2, .09, .16), loc=hinge + up * 1.35 + Vector((x, 0, 0)), rot=srot, bevel=0)
    steel.cyl(.07, 2.0, loc=hinge, rot=ACROSS, seg=8, bevel=0)                                 # hinge pin
    for s in (-1, 1):
        steel.box((.14, .34, .2), loc=(s * .75, 4.18, .74), bevel=.01, seg=1)                  # hinge lugs
        steel.limb((s * .55, 3.9, 1.18), tuple(hinge + up * .95 - out * .06 + Vector((s * .55, 0, 0))), .1, .1,
                   bevel=0)                                                                     # rams
    # Bed stowage between the module and the mount: charge containers, a cable reel, tarp and cans.
    for x in (-.62, .62):
        _stowage_bin(a, (x, .35, 1.4), (.9, 1.3, .44), mat='Crate', lid='Armor', latch_side=0)
    armor.cyl(.26, .3, loc=(-.2, 1.35, 1.66), rot=ACROSS, seg=12, bevel=.02, bseg=1)           # cable reel
    dark.cyl(.3, .06, loc=(-.2, 1.35, 1.66), rot=ACROSS, seg=12, bevel=0)
    for s in (-1, 1):
        armor.box((.04, .5, .36), loc=(-.2 + s * .18, 1.35, 1.58), bevel=0)                    # reel cheeks
    _roll(a, (.62, 1.3, 1.53), .9, r=.11)
    _jerrycans(a, (1.0, 1.95, 1.4), 2, axis='x')
    _jerrycans(a, (-1.0, 1.95, 1.4), 2, axis='x')

    # Open gun mount on the tail of the flatbed.
    t = a.pivot('Turret', (0, 3.0, 1.41))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.95, .1, loc=(0, 0, .02), seg=20, bevel=.02, bseg=1)                            # turntable
    tarm.box((1.6, 1.5, .3), loc=(0, .05, .22), bevel=.04, seg=1, taper=(.94, .94))           # carriage
    T = (0, .12, .96)                                                                          # trunnion
    for s in (-1, 1):
        tarm.prism([(-.72, .06), (.62, .06), (.4, .8), (.26, 1.1), (-.04, 1.1), (-.46, .62)], .14,
                   loc=(s * .5, 0, 0), bevel=.03)                                               # brackets
        tsteel.cyl(.15, .08, loc=(s * .6, T[1], T[2]), rot=ACROSS, seg=12, bevel=.015, bseg=1)  # trunnion caps
        tsteel.limb((s * .3, -.5, .3), (s * .3, -.68, .62), .12, .12, bevel=.02, seg=1)        # elevation rams
    tarm.box((.24, .46, .4), loc=(-.78, -.2, .72), bevel=.03, seg=1)                           # gunner's console
    a.part('Console', 'Glass', t).box((.03, .3, .18), loc=(-.905, -.2, .8), bevel=0)
    tsteel.box((.34, .9, .08), loc=(.84, .45, .66), bevel=0)                                   # loading tray
    for s in (-1, 1):
        tsteel.box((.03, .94, .1), loc=(.84 + s * .13, .45, .74), bevel=0)
    tsteel.limb((.84, .2, .62), (.84, .2, .3), .06, .06, bevel=0)
    tsteel.limb((.84, .7, .62), (.84, .7, .3), .06, .06, bevel=0)
    # The gun, laid 10 degrees up: tapered L52 barrel, cradle with twin recuperators, breech ring,
    # elevating arc (it and the breech set the game's elevation pivot on the trunnion) and brake.
    at = _axis(T, PITCH)
    crot, brot = _along(PITCH)
    gun = a.part('Main_cannon', 'Steel', t)
    L = 7.05
    _tapered(gun, at, -.1, L, .135, .1, crot, seg=14)
    for f in (.34, .62, .9):
        gun.cyl(.135 - .035 * f + .025, .06, loc=at(L * f), rot=crot, seg=12, bevel=0)          # clamps
    gun.box((.5, .52, .46), loc=at(-.26), rot=brot, bevel=.04, seg=1)                           # breech ring
    gun.box((.08, .3, .12), loc=at(-.3, 0, .24), rot=brot, bevel=0)                             # breech lever
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((.44, 2.4, .38), loc=at(1.05), rot=brot, bevel=.04, seg=1)
    cradle.box((.5, .16, .44), loc=at(2.2), rot=brot, bevel=.02, seg=1)                         # front collar
    for side in (-.12, .12):
        cradle.cyl(.085, 2.0, loc=at(1.2, .27, side), rot=crot, seg=10, bevel=.01, bseg=1)     # recuperators
        cradle.cyl(.1, .08, loc=at(2.2, .27, side), rot=crot, seg=10, bevel=0)
    _arc(cradle, at, .5, .64, -.5, .9, .1, steps=5)                                      # elevating arc
    brake = a.part('Muzzle_brake', 'Undercarriage', t)
    bl = .52
    brake.cyl(.125, bl, loc=at(L - .02 + bl / 2), rot=crot, seg=14, bevel=.01, bseg=1)
    for f in (.22, .72):
        brake.box((.42, .13, .3), loc=at(L - .02 + bl * f), rot=brot, bevel=.02, seg=1)
    a.pivot('Muzzle_main', tuple(at(L - .02 + bl)), t)



# ----------------------------------------------------------------------------- howitzer (PzH 2000)
def howitzer(a):
    """Tracked 155 mm self-propelled howitzer (PzH 2000 / M109A7 lineage): a long, low front hull with a
    shallow glacis, the driver's hatch and engine grilles at the front and an A-frame travel lock folded on
    the glacis; seven road wheels behind bolted skirts. A large slab-sided turret stands well back and
    overhangs the tail, with a rear ammunition door, side bins, add-on roof armour, smoke dischargers, a
    panoramic sight and the commander's cupola with its machine gun. The very long L52 gun has a big
    mantlet, a fume extractor, thermal-sleeve clamps and a pepperpot muzzle brake 3.3 m past the bow."""
    tracks(a, 1.3, 7.0, .95, .32, 7, .5, belt_width=.6, wheel_seg=10, lean=True, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.45, .56), (-3.78, 1.12), (3.72, 1.12), (3.72, .56)], 1.9, bevel=.05)       # belly
    nose, brow = (-3.9, 1.3), (-2.7, 1.7)
    hull.prism([(-3.8, 1.065), nose, brow, (3.66, 1.7), (3.8, 1.6), (3.8, 1.065)], 3.28, bevel=.06)
    gy, gz, grot = _glacis(nose, brow, .52, 0)
    for s in (-1, 1):
        _skirt_panels(a, s, 1.72, -3.3, 3.45, .66, 1.4, 4)
        a.part('Skirt_flaps', 'Rubber').box((.04, .42, .56), loc=(s * 1.72, -3.56, 1.1), rot=(.3, 0, 0), bevel=0)
        hy, hz, hrot = _glacis(nose, brow, .12, .03)
        armor.box((.36, .2, .16), loc=(s * 1.28, hy, hz), rot=(hrot, 0, 0), bevel=.02, seg=1)   # lamp housings
        ly, lz, _ = _glacis(nose, brow, .045, .045)
        a.part('Lamps', 'Lamp').box((.24, .03, .09), loc=(s * 1.28, ly, lz), rot=(hrot, 0, 0), bevel=0)
        steel.box((.16, .2, .14), loc=(s * .75, -3.72, .95), bevel=.02, seg=1)                 # tow hooks
        steel.box((.16, .2, .14), loc=(s * .75, 3.86, .95), bevel=.02, seg=1)
        _taillight(a, s * 1.35, 3.8, 1.42)
        steel.box((.08, .1, .16), loc=(-.55, 3.83, .95 + (s + 1) * .21), bevel=.01, seg=1)     # door hinges
        _track_links(a, _frame((s * .95, gy, gz), (grot, 0, 0)), 2, width=.44)
    # Folded travel lock on the glacis: an A-frame lying flat with the barrel cradle at its head.
    lock = a.part('Travel_lock', 'Steel')
    y0, z0, rot0 = _glacis(nose, brow, .16, .06)
    y1, z1, _ = _glacis(nose, brow, .86, .06)
    for s in (-1, 1):
        lock.limb((s * .42, y0, z0), (s * .14, y1, z1), .08, .07, bevel=0)
        hy, hz, _ = _glacis(nose, brow, .16, .04)
        armor.box((.14, .22, .16), loc=(s * .56, hy, hz), rot=(rot0, 0, 0), bevel=0)             # hinge lugs
    lock.box((1.0, .1, .09), loc=(0, y0, z0), rot=(rot0, 0, 0), bevel=0)                        # hinge bar
    y2, z2, _ = _glacis(nose, brow, .9, .1)
    lock.box((.44, .16, .16), loc=(0, y2, z2), rot=(rot0, 0, 0), bevel=.02, seg=1)              # cradle
    for s in (-1, 1):
        y3, z3, _ = _glacis(nose, brow, .9, .22)
        lock.box((.06, .14, .16), loc=(s * .17, y3, z3), rot=(rot0, 0, 0), bevel=0)             # jaws
    # Front deck: engine grilles on the right, the driver's hatch and vision blocks on the left, the
    # exhaust on the right flank.
    for y, d in ((-2.2, .7), (-1.35, .6)):
        deck.grille(1.1, d, loc=(.75, y, 1.71), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
        _grille_frame(a, .75, y, 1.69, 1.1, d, t=.04)
    _hatch(a, -.8, -2.1, 1.69, .28)
    _periscopes(a, [(-.8 + dx, -2.46, 1.69, 0) for dx in (-.17, 0, .17)])
    armor.box((.1, .9, .34), loc=(1.66, -1.6, 1.38), bevel=.015, seg=1)                          # exhaust cowl
    deck.grille(.8, .24, loc=(1.72, -1.6, 1.38), rot=(0, 0, R90), slats=3, depth=.05, thickness=.035)
    _cable(a, [(-1.5, -2.5, 1.725), (-1.5, -.9, 1.725)])
    _shovel(a, (1.45, -2.45, 1.715), yaw=0, length=1.0)
    # Rear: hull door with hinges and a handle.
    armor.box((.9, .06, .66), loc=(-.1, 3.82, 1.2), bevel=.02, seg=1)
    steel.box((.26, .05, .05), loc=(.18, 3.86, 1.22), bevel=0)
    steel.cyl(1.3, .1, loc=(0, 1.5, 1.72), seg=24, bevel=.02, bseg=1)                           # turret ring

    t = a.pivot('Turret', (0, 1.5, 1.72))
    H = 1.16
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.02, -2.2), (1.02, -2.2), (1.5, -1.62), (1.52, 2.5), (1.34, 2.7), (-1.34, 2.7), (-1.52, 2.5),
               (-1.5, -1.62)]
    turret.prism(outline, H, loc=(0, 0, H / 2), axis='Z', bevel=.06, taper=.95)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    # Add-on roof armour: a grid of bolted plates (the cupola takes the front-right one).
    for x in (-.78, 0, .78):
        for y in (-1.2, -.35, .5):
            if x > 0 and y < 0:
                continue
            turret.box((.72, .78, .06), loc=(x, y, H + .01), bevel=.015, seg=1)
    # Side bins on the rear half and side doors ahead of them; smoke dischargers at the front corners;
    # rails along the roof edges.
    for s in (-1, 1):
        side = ((1.5, -1.62), (1.52, 2.5)) if s > 0 else ((-1.52, 2.5), (-1.5, -1.62))

        def at_side(y, z):
            u = (y + 1.62) / 4.12 if s > 0 else (2.5 - y) / 4.12
            return _face_frame(*side, H, .95, u=u, v=z / H)
        _face_box(a, 'Turret_bins', 'Armor', at_side(1.55, .28), (1.7, .52, .26), parent=t)
        _face_box(a, 'Turret_bins', 'Armor', at_side(1.55, .82), (1.74, .05, .29), parent=t, bevel=0, sink=.02)
        for y in (1.0, 2.1):
            _face_box(a, 'Turret_steel', 'Steel', at_side(y, .7), (.05, .1, .31), parent=t, bevel=0)
        _face_box(a, 'Turret_armor', 'Armor', at_side(-.3, .5), (.9, .76, .05), parent=t)       # side door
        _face_box(a, 'Turret_steel', 'Steel', at_side(-.05, .55), (.2, .05, .09), parent=t, bevel=0, sink=-.035)
        tarm.box((.36, .5, .16), loc=(s * 1.26, -1.62, H - .2), bevel=.02, seg=1)             # discharger base
        for k in range(4):                                                                     # smoke dischargers
            tsteel.cyl(.055, .2, loc=(s * (1.16 + k * .07), -1.8 + k * .12, H - .08), rot=(.6, 0, s * .5), seg=8,
                       bevel=0)
        _rail(a, [(s * 1.28, .2, H - .02), (s * 1.28, .2, H + .06), (s * 1.3, 2.1, H + .06), (s * 1.3, 2.1, H - .02)],
              parent=t)
    # Rear: the ammunition door (hinged, with a handle), jerrycans and lights either side of it.
    ry, rz, rrot = _glacis((2.7 * .95, H), (2.7, 0), .52, .025)
    tarm.box((1.16, .76, .06), loc=(0, ry, rz), rot=(rrot, 0, 0), bevel=.02, seg=1)
    for z in (.3, .82):
        tsteel.box((.1, .08, .14), loc=(-.62, 2.69 - .05 * z, z), bevel=0)                      # hinges
    hy, hz, _ = _glacis((2.7 * .95, H), (2.7, 0), .5, .065)
    tsteel.box((.3, .05, .05), loc=(.3, hy, hz), rot=(rrot, 0, 0), bevel=0)                     # handle
    for s in (-1, 1):
        cy, cz, _ = _glacis((2.7 * .95, H), (2.7, 0), .55, .085)
        a.part('Jerrycans', 'Crate', t).box((.26, .15, .44), loc=(s * .95, cy, cz), rot=(rrot, 0, 0), bevel=.02,
                                            seg=1)
    # Front: muzzle-velocity radar and an NBC box either side of the mantlet.
    tarm.box((.4, .3, .22), loc=(.74, -2.12, H - .16), bevel=.03, seg=1)
    a.part('Radar_face', 'Glass', t).box((.3, .03, .14), loc=(.74, -2.28, H - .16), bevel=0)
    tarm.box((.36, .3, .26), loc=(-.74, -2.1, H - .2), bevel=.03, seg=1)
    # Roof: commander's cupola with the machine gun (right), panoramic sight (left), loader's hatch,
    # vents, a tarp roll and antennas.
    tsteel.cyl(.33, .12, loc=(.78, -.35, H + .05), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.28, .05, loc=(.78, -.35, H + .12), seg=16, bevel=.015, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(4):
        ang = -R90 + (k - 1.5) * .7
        glass.box((.1, .05, .07), loc=(.78 + math.cos(ang) * .33, -.35 + math.sin(ang) * .33, H + .07),
                  rot=(0, 0, ang + R90), bevel=0)
    _roof_mg(a, t, (.78, -.35, H + .145), length=.9)
    tsteel.cyl(.13, .22, loc=(-.8, -1.35, H + .1), seg=10, bevel=.02, bseg=1)                    # panoramic sight
    tsteel.box((.32, .32, .22), loc=(-.8, -1.35, H + .3), bevel=.04, seg=1)
    a.part('Sight', 'Glass', t).box((.24, .04, .1), loc=(-.8, -1.52, H + .31), bevel=0)
    _hatch(a, -.7, .5, H + .04, .28, parent=t)
    a.part('Vents', 'Undercarriage', t).grille(.9, .5, loc=(0, 1.55, H + .01), rot=(-R90, 0, 0), slats=5,
                                               depth=.07, thickness=.04)
    _roll(a, (0, 2.3, H + .12), 1.8, r=.12, parent=t)
    for x, height in ((-1.2, 1.3), (1.2, 1.0)):
        tsteel.box((.1, .1, .07), loc=(x, 2.2, H), bevel=0)
        _antenna(a, t, x, 2.2, H + .02, height)
    # The gun, laid 10 degrees up. The mantlet turns with it; a breech block hidden inside the turret sets
    # the game's elevation pivot on the trunnion.
    T = (0, -1.98, .62)
    at = _axis(T, PITCH)
    crot, brot = _along(PITCH)
    mant = a.part('Main_cannon_mantlet', 'Armor', t)
    mant.box((1.06, .64, .84), loc=at(.02), rot=brot, bevel=.05, seg=1)
    mant.box((.56, .36, .5), loc=at(.46), rot=brot, bevel=.04, seg=1)                          # gun collar
    for side in (-.4, .4):
        mant.box((.14, .2, .5), loc=at(.4, 0, side), rot=brot, bevel=0)                         # collar ribs
    a.part('Main_cannon_breech', 'Steel', t).box((.5, .2, .6), loc=at(-.38, -.24), rot=brot, bevel=0)
    base = at(.6)
    tip = _gun(a, t, 0, base.y, base.z, 5.4, .105, pitch=PITCH, seg=14,
               sleeves=((.08, .22, .135), (.34, .07, .128), (.86, .07, .128)), extractor=(.6, .86, .168),
               brake=(.72, .2, 2), brake_seg=12)
    a.pivot('Muzzle_main', tip, t)


def _skirt_panels(a, s, x, y0, y1, z0, z1, panels, thick=.1, gap=.04):
    """Bolted side-skirt plates on side s at |x| (team paint), a dark lip along their top and a row of
    bolts along their bottom edge."""
    part = a.part('Skirts', 'Team')
    lip = a.part('Skirt_edge', 'Armor')
    bolts = a.part('Skirt_bolts', 'Steel')
    step = (y1 - y0 + gap) / panels
    for i in range(panels):
        yc = y0 + step * (i + .5) - gap / 2
        w = step - gap
        part.box((thick, w, z1 - z0), loc=(s * x, yc, (z0 + z1) / 2), bevel=.02, seg=1)
        lip.box((thick + .03, w + .03, .05), loc=(s * x, yc, z1 - .015), bevel=0)
        for k in range(4):
            bolts.box((.03, .05, .05), loc=(s * (x + thick / 2 + .005), yc - w / 2 + .15 + k * (w - .3) / 3,
                                            z0 + .09), bevel=0)



# ----------------------------------------------------------------------------- siege_tank (2S7 Pion)
def _shell(part, band, x, y, z, length=.9, r=.1):
    """203 mm projectile lying along Y (nose forwards) with a driving band."""
    part.lathe([(r, 0), (r, length * .55), (r * .7, length * .85), (r * .25, length), (.001, length)],
               loc=(x, y + length / 2, z), rot=FORWARD, seg=7)
    band.cyl(r + .012, .05, loc=(x, y + length / 2 - .12, z), rot=FORWARD, seg=7, bevel=0)


def siege_tank(a):
    """203 mm self-propelled gun (2S7 Pion lineage): a long tracked chassis with exposed running gear
    (seven road wheels, return rollers, thin track guards), the full-width crew cab at the front with
    armoured window shutters, hatches and the machine gun, the engine deck behind it, and ammunition racks
    along both sides of the deck. The gun stands in the open on a mount at the rear: massive trunnion
    brackets, a big cradle with three recoil cylinders, an elevating arc and a square breech;
    the thick, very long barrel is laid forward over the cab and ends in a heavy muzzle collar. Two crew
    seats with the laying controls sit beside the breech on the left, a loading crane and tray on the
    right, and a huge dozer-type spade is raised at the tail."""
    tracks(a, 1.32, 8.8, .92, .36, 7, .5, belt_width=.62, wheel_seg=8, lean=True, sprocket=-1, cleat_pitch=.3)
    for s in (-1, 1):                                  # return rollers between the road wheels
        face = s * (1.32 + .31)
        for y in (-1.95, -.65, .65, 1.95):
            a.part('Tyres', 'Undercarriage').cyl(.1, .07, loc=(face + s * .005, y, .84), rot=ACROSS, seg=8, bevel=0)
            a.part('Hubs', 'Steel').cyl(.045, .03, loc=(face + s * .045, y, .84), rot=ACROSS, seg=6, bevel=0)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    hull.prism([(-4.5, .56), (-4.98, 1.16), (4.85, 1.16), (4.85, .56)], 1.96, bevel=.05)       # belly
    hull.prism([(-4.98, 1.06), (-5.08, 1.3), (-4.9, 1.5), (4.85, 1.5), (5.0, 1.36), (5.0, 1.06)], 3.3, bevel=.06)
    # Crew cab across the full width at the front: raked front plate with three windows under hinged
    # armoured shutters, side doors, roof hatches and the machine gun.
    front, top = (-5.02, 1.42), (-4.66, 2.42)
    hull.prism([(-4.98, 1.4), front, top, (-4.5, 2.5), (-2.9, 2.5), (-2.84, 1.4)], 3.34, bevel=.06)
    wr = _glacis(front, top, .5, 0)[2]
    for x in (-1.0, 0, 1.0):
        wy, wz, _ = _glacis(front, top, .56, .012)
        glass.box((.62, .4, .04), loc=(x, wy, wz), rot=(wr, 0, 0), bevel=.01, seg=1)
        sy, sz, _ = _glacis(front, top, .93, .03)
        armor.box((.72, .14, .06), loc=(x, sy - .12, sz + .02), rot=(wr - 1.2, 0, 0), bevel=.012, seg=1)  # shutters
        steel.box((.05, .1, .1), loc=(x - .3, sy, sz - .02), rot=(wr, 0, 0), bevel=0)                 # hinges
        steel.box((.05, .1, .1), loc=(x + .3, sy, sz - .02), rot=(wr, 0, 0), bevel=0)
    for s in (-1, 1):
        ox = s * 1.67
        armor.box((.05, .8, .86), loc=(ox + s * .005, -3.75, 1.95), bevel=.015, seg=1)                # side doors
        steel.box((.05, .18, .06), loc=(ox + s * .03, -3.5, 1.95), bevel=0)
        glass.box((.04, .34, .2), loc=(ox + s * .02, -3.75, 2.22), bevel=.01, seg=1)
        steel.box((.3, .26, .04), loc=(s * 1.55, -3.75, 1.12), bevel=0)                               # step
        gy, gz, grot = _glacis((-5.08, 1.3), (-4.9, 1.5), .5, .02)
        _headlight(a, s * 1.25, -5.07, 1.42, guard=True)
        steel.box((.18, .22, .16), loc=(s * .62, -5.06, 1.0), bevel=0)                               # tow hooks
        steel.box((.18, .22, .16), loc=(s * .4, 5.02, 1.0), bevel=0)
        _taillight(a, s * 1.45, 5.0, 1.3)
    _hatch(a, -.95, -3.5, 2.49, .3)
    _hatch(a, .1, -3.3, 2.49, .28)
    _periscopes(a, [(-.95 + dx, -3.92, 2.49, 0) for dx in (-.2, 0, .2)])
    for x in (-1.3, -.4, .5, 1.3):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x, -4.52, 2.51), bevel=0)
    armor.cyl(.38, .14, loc=(1.0, -3.7, 2.53), seg=16, bevel=.02, bseg=1)                              # MG cupola
    glass_c = a.part('Periscopes', 'Glass')
    for k in range(4):
        ang = -R90 + (k - 1.5) * .65
        glass_c.box((.1, .05, .07), loc=(1.0 + math.cos(ang) * .38, -3.7 + math.sin(ang) * .38, 2.56),
                    rot=(0, 0, ang + R90), bevel=0)
    wpn.hmg(a, (1.0, -3.7, 2.6), post=.12, length=.85, ammo=-1)
    _antenna(a, None, -1.45, -3.0, 2.5, 1.4)
    steel.box((.1, .1, .07), loc=(-1.45, -3.0, 2.52), bevel=0)
    # Glacis: spare track links and the towing cable.
    for s in (-1, 1):
        _track_links(a, _frame((s * .95, -5.05, 1.22), (-R90 + .5, 0, 0)), 3, width=.46)
    # Engine deck behind the cab: raised cover with grilles, exhaust on the left flank, tool boxes and
    # cables on the track guards.
    hull.box((2.3, 2.3, .22), loc=(0, -1.7, 1.58), bevel=.04, seg=1)
    for y in (-2.3, -1.2):
        deck.grille(.9, .7, loc=(-.5, y, 1.7), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
        deck.grille(.9, .7, loc=(.5, y, 1.7), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
    for x in (-.5, .5):
        _grille_frame(a, x, -1.75, 1.68, .9, 1.8, t=.04)
    armor.box((.12, 1.0, .36), loc=(-1.68, -1.5, 1.28), bevel=.015, seg=1)                            # exhaust cowl
    deck.grille(.9, .26, loc=(-1.745, -1.5, 1.28), rot=(0, 0, -R90), slats=3, depth=.05, thickness=.035)
    for s in (-1, 1):
        _stowage_bin(a, (s * 1.4, -1.7, 1.49), (.42, 1.9, .3), latch_side=s)
        _cable(a, [(s * 1.25, -.5, 1.525), (s * 1.25, 1.1, 1.525)])
    # Ammunition racks on both sides of the deck ahead of the mount: three shells each in open cradles.
    shells = a.part('Shells', 'Steel')
    bands = a.part('Shell_bands', 'BarrelRed')
    for s in (-1, 1):
        rack = a.part('Racks', 'Armor')
        for y in (-.35, .45):
            rack.box((1.1, .08, .3), loc=(s * 1.02, y, 1.62), bevel=0)                              # cradles
        rack.box((.08, 1.0, .12), loc=(s * 1.58, .05, 1.8), bevel=0)                                # outer rail
        for k in range(3):
            _shell(shells, bands, s * (.62 + k * .32), -.5, 1.82, length=1.0, r=.11)
    for s in (-1, 1):                                                                             # charge cases
        a.part('Charges', 'Crate').cyl(.16, .7, loc=(s * .45, .05, 1.68), rot=FORWARD, seg=8, bevel=0)
    # Huge dozer-type spade raised at the tail: a curved ribbed blade on two arms, with rams.
    lean = .22
    hinge = Vector((0, 5.0, .8))
    up = Vector((0, math.sin(lean), math.cos(lean)))
    out = Vector((0, math.cos(lean), -math.sin(lean)))
    srot = (-lean, 0, 0)
    spade = a.part('Spade', 'Armor')
    spade.box((3.3, .14, 1.35), loc=hinge + up * .68, rot=srot, bevel=.04, seg=1)
    spade.box((3.34, .22, .2), loc=hinge + up * 1.32 - out * .02, rot=srot, bevel=.02, seg=1)        # cutting edge
    for x in (-1.3, -.65, 0, .65, 1.3):                                                             # ribs
        spade.box((.12, .14, 1.2), loc=hinge + up * .66 + out * .1 + Vector((x, 0, 0)), rot=srot, bevel=0)
    for x in (-1.4, -.84, -.28, .28, .84, 1.4):                                                     # teeth
        steel.box((.22, .12, .18), loc=hinge + up * 1.48 - out * .02 + Vector((x, 0, 0)), rot=srot, bevel=0)
    steel.cyl(.09, 3.0, loc=hinge, rot=ACROSS, seg=8, bevel=0)                                       # hinge pin
    for s in (-1, 1):
        armor.box((.2, .5, .34), loc=(s * 1.35, 4.95, .78), bevel=.02, seg=1)                        # hinge lugs
        steel.limb((s * 1.1, 4.8, 1.45), tuple(hinge + up * 1.0 - out * .08 + Vector((s * 1.1, 0, 0))), .13, .13,
                   bevel=.02, seg=1)                                                               # rams
    # Rear deck: loading platform plates and a stowage box behind the mount.
    armor.box((2.6, .5, .06), loc=(0, 4.6, 1.52), bevel=0)
    steel.cyl(1.25, .1, loc=(0, 2.55, 1.52), seg=24, bevel=.02, bseg=1)                             # mount ring

    # The open gun mount.
    t = a.pivot('Turret', (0, 2.55, 1.52))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tteam = a.part('Turret_body', 'Team', t)
    tsteel.cyl(1.2, .1, loc=(0, 0, .03), seg=24, bevel=.02, bseg=1)                                 # turntable
    tteam.box((1.9, 1.2, .34), loc=(0, -.55, .22), bevel=.04, seg=1)                                # carriage front
    T = (0, .05, 1.02)                                                                              # trunnion
    for s in (-1, 1):
        tteam.prism([(-1.15, .05), (.95, .05), (.62, .8), (.34, 1.24), (-.26, 1.24), (-.7, .78)], .2,
                    loc=(s * .64, 0, 0), bevel=.03)                                                 # brackets
        tsteel.cyl(.2, .12, loc=(s * .78, T[1], T[2]), rot=ACROSS, seg=12, bevel=.02, bseg=1)       # trunnion caps
        tarm.box((.1, 1.6, .5), loc=(s * .77, -.1, .32), bevel=.02, seg=1)                          # bracket feet
    # Crew platform on the left: two seats with the laying handwheels and sight, a railing.
    tarm.box((.9, 1.8, .06), loc=(-1.25, .05, .38), bevel=0)
    seats = a.part('Seats', 'Canvas', t)
    for y in (-.45, .45):
        seats.box((.4, .4, .12), loc=(-1.25, y, .72), bevel=.03, seg=1)
        seats.box((.4, .1, .42), loc=(-1.25, y + .24, .95), rot=(-.12, 0, 0), bevel=.03, seg=1)
        tsteel.cyl(.05, .3, loc=(-1.25, y, .5), seg=6, bevel=0)                                      # seat posts
        tsteel.torus(.13, .02, loc=(-.95, y - .28, .95), rot=(0, R90, 0), seg=8, ring=3)             # handwheels
        tsteel.box((.12, .05, .3), loc=(-.88, y - .28, .82), bevel=0)                                # wheel boxes
    tarm.box((.26, .3, .36), loc=(-1.0, -.95, 1.1), bevel=.03, seg=1)                               # sight box
    a.part('Sight', 'Glass', t).box((.18, .03, .12), loc=(-1.0, -1.11, 1.14), bevel=0)
    tsteel.box((.05, .05, .4), loc=(-1.0, -.95, .75), bevel=0)
    _rail(a, [(-1.68, -.8, .4), (-1.68, -.8, 1.0), (-1.68, .9, 1.0), (-1.68, .9, .4)], parent=t, r=.022)
    # Loading crane and tray on the right.
    tarm.box((.8, 1.2, .06), loc=(1.22, .2, .38), bevel=0)
    tsteel.cyl(.09, 1.3, loc=(1.45, .55, 1.0), seg=10, bevel=0)                                     # crane post
    tsteel.limb((1.45, .55, 1.6), (1.0, .2, 1.72), .1, .1, bevel=0)                                 # boom
    tsteel.tube([(1.0, .2, 1.68), (1.0, .2, 1.25)], .012, seg=4)                                     # hoist cable
    tsteel.box((.12, .12, .1), loc=(1.0, .2, 1.22), bevel=0)                                        # hook block
    tsteel.box((.34, 1.1, .08), loc=(1.1, .6, .8), bevel=0)                                         # loading tray
    for s in (-1, 1):
        tsteel.box((.03, 1.14, .12), loc=(1.1 + s * .13, .6, .86), bevel=0)
    tsteel.limb((1.1, .2, .76), (1.1, .2, .42), .06, .06, bevel=0)
    tsteel.limb((1.1, 1.0, .76), (1.1, 1.0, .42), .06, .06, bevel=0)
    # The gun, laid 10 degrees up: tapered barrel, muzzle collar, a big cradle with two recuperators over
    # the barrel and a recoil brake under it, the square breech and the elevating arc (these two set the
    # game's elevation pivot on the trunnion).
    at = _axis(T, PITCH)
    crot, brot = _along(PITCH)
    gun = a.part('Main_cannon', 'Steel', t)
    L = 9.5
    _tapered(gun, at, -.1, L, .235, .165, crot, seg=14, bevel=.02)
    for f in (.36, .66):
        gun.cyl(.235 - .07 * f + .03, .09, loc=at(L * f), rot=crot, seg=12, bevel=0)                 # clamps
    gun.box((.72, .62, .72), loc=at(-.34), rot=brot, bevel=.05, seg=1)                                # breech
    gun.box((.1, .34, .16), loc=at(-.4, .1, .36), rot=brot, bevel=0)                                  # breech lever
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((.66, 2.9, .6), loc=at(1.2), rot=brot, bevel=.05, seg=1)
    cradle.box((.72, .2, .66), loc=at(2.62), rot=brot, bevel=.03, seg=1)                              # front collar
    for side in (-.17, .17):
        cradle.cyl(.13, 2.7, loc=at(1.35, .4, side), rot=crot, seg=12, bevel=.015, bseg=1)           # recuperators
        cradle.cyl(.15, .1, loc=at(2.72, .4, side), rot=crot, seg=12, bevel=0)
    cradle.cyl(.14, 2.3, loc=at(1.3, -.38), rot=crot, seg=12, bevel=.015, bseg=1)                    # recoil brake
    _arc(cradle, at, .72, .88, -.45, 1.0, .12, steps=6)                                               # elevating arc
    brake = a.part('Muzzle_brake', 'Undercarriage', t)
    brake.lathe([(.16, -.04), (.215, .06), (.215, .5), (.19, .56), (.12, .56), (.12, .4)], loc=at(L - .02), rot=crot,
                seg=14)
    a.pivot('Muzzle_main', tuple(at(L + .54)), t)



# ----------------------------------------------------------------------------- grad_truck (BM-21 Grad)
def grad_truck(a):
    """122 mm multiple rocket launcher (BM-21 Grad on an Ural-375D 6x6): a bonneted truck with a long
    narrow hood, a slotted radiator grille and big flat-topped front fenders, a two-door cab with a canvas
    top, armoured window shutters folded on its roof, a blast shield over its rear window and a machine gun
    on the roof; fuel tanks, a spare wheel and tool lockers along the frame, mudguards over the rear bogie
    and two rear jacks. On a turntable at the rear, two side brackets carry the 40-tube pack (4 rows of 10)
    on its rear hinge, bound by three frames and laid level over the bed with the tubes facing forward."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    axles = (-2.75, 1.15, 2.55)
    for y in axles:
        for s in (-1, 1):
            _wheel(a, s * 1.0, y, .54, .4, seg=14)
    for s in (-1, 1):
        dark.box((.18, 7.1, .26), loc=(s * .42, -.05, .86), bevel=.02, seg=1)                   # frame rails
    for y in axles:
        dark.box((1.56, .2, .16), loc=(0, y, .54), bevel=.02, seg=1)                          # axle beams
    for y in (1.15, 2.55):
        dark.box((.3, .38, .3), loc=(0, y, .74), bevel=.02, seg=1)                            # differentials
    # Front: bumper with tow hooks and a winch drum, the narrow hood over the engine, slotted grille.
    steel.box((2.3, .18, .2), loc=(0, -3.62, .8), bevel=.03, seg=1)
    for s in (-1, 1):
        steel.box((.14, .16, .14), loc=(s * .55, -3.74, .8), bevel=.02, seg=1)
    dark.cyl(.09, .5, loc=(0, -3.52, .96), rot=ACROSS, seg=10, bevel=0)                         # winch drum
    body.prism([(-3.5, .95), (-3.52, 1.62), (-3.3, 1.74), (-2.05, 1.8), (-2.05, .95)], 1.12, bevel=.05)   # hood
    for x in (-.3, 0, .3):
        dark.box((.07, .04, .5), loc=(x, -3.525, 1.28), bevel=0)                               # grille slots
    for x in (-.45, -.15, .15, .45):
        dark.box((.05, .04, .5), loc=(x, -3.525, 1.28), bevel=0)
    for s in (-1, 1):
        steel.box((.05, .5, .04), loc=(s * .45, -2.75, 1.79), bevel=0)                         # hood latches
        dark.grille(.7, .26, loc=(s * .565, -2.7, 1.5), rot=(0, 0, s * R90), slats=4, depth=.04, thickness=.03)
    # Front fenders: flat-topped, rounded at the front, with the headlights and side lights on them.
    for s in (-1, 1):
        x = s * .9
        body.prism([(-3.5, 1.04), (-3.46, 1.26), (-3.25, 1.4), (-2.05, 1.42), (-2.05, 1.22), (-3.2, 1.2)], .66,
                   loc=(x, 0, 0), bevel=.03)
        armor.box((.6, .06, .5), loc=(x, -2.08, 1.0), bevel=.01, seg=1)                          # fender back
        _headlight(a, s * .78, -3.47, 1.2, guard=False)
        a.part('Marker_lights', 'Alloy').box((.1, .1, .07), loc=(s * 1.1, -3.1, 1.44), bevel=0)
    # Cab: two doors with windows, a flat split windscreen under folded armour shutters, a canvas top,
    # mirrors, and the blast shield over the rear window.
    body.prism([(-2.06, 1.2), (-2.06, 1.82), (-1.96, 2.44), (-.8, 2.44), (-.8, 1.2)], 2.3, bevel=.05)
    for s in (-1, 1):
        glass.box((.98, .04, .5), loc=(s * .54, -2.02, 2.12), rot=(-.16, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .56, .4), loc=(s * 1.155, -1.62, 2.1), bevel=.01, seg=1)
        for y in (-1.98, -1.12):
            armor.box((.03, .04, 1.1), loc=(s * 1.152, y, 1.84), bevel=0)                      # door lines
        steel.box((.04, .16, .05), loc=(s * 1.165, -1.3, 1.9), bevel=0)                        # handles
        steel.box((.3, .24, .04), loc=(s * 1.08, -1.55, .98), bevel=0)                         # steps
        steel.tube([(s * 1.14, -1.95, 2.3), (s * 1.22, -2.1, 2.34)], .016, seg=4)              # mirrors
        armor.box((.05, .16, .26), loc=(s * 1.25, -2.14, 2.26), bevel=.01, seg=1)
        steel.cyl(.24, .9, loc=(s * .8, -1.45, .78), rot=FORWARD, seg=12, bevel=.03, bseg=1)   # fuel tanks
        for y in (-1.75, -1.15):
            dark.box((.52, .04, .52), loc=(s * .8, y, .78), bevel=0)
    armor.box((.08, .04, .5), loc=(0, -2.035, 2.12), rot=(-.16, 0, 0), bevel=0)                  # centre pillar
    armor.box((2.2, .12, .06), loc=(0, -2.02, 2.47), rot=(-1.2, 0, 0), bevel=.01, seg=1)          # folded shutters
    for s in (-1, 1):
        armor.box((1.02, .5, .05), loc=(s * .54, -1.8, 2.49), bevel=.012, seg=1)
    a.part('Canvas_top', 'Canvas').box((2.2, .9, .12), loc=(0, -1.12, 2.48), bevel=.04, seg=1, taper=(.97, .95))
    steel.box((2.26, .05, .05), loc=(0, -.85, 2.46), bevel=0)                                    # top bow
    armor.box((1.9, .08, .66), loc=(0, -.73, 2.02), bevel=.015, seg=1)                            # blast shield
    for s in (-1, 1):
        steel.box((.06, .1, .06), loc=(s * .8, -.76, 2.3), bevel=0)                               # shield brackets
        steel.box((.06, .1, .06), loc=(s * .8, -.76, 1.75), bevel=0)
    armor.cyl(.3, .08, loc=(.5, -1.6, 2.54), seg=14, bevel=.015, bseg=1)                           # MG ring
    wpn.hmg(a, (.5, -1.6, 2.58), post=.12, length=.8, ammo=1)
    _antenna(a, None, -1.05, -.9, 2.44, 1.3)
    # Behind the cab: spare wheel upright on the left, air cleaner and battery box on the right.
    a.part('Tyres', 'Rubber').cyl(.5, .34, loc=(-.72, -.35, 1.12), rot=ACROSS, seg=14, bevel=.06, bseg=1)
    a.part('Hubs', 'Steel').cyl(.26, .38, loc=(-.72, -.35, 1.12), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    steel.box((.08, .3, .7), loc=(-.5, -.35, .98), bevel=0)                                      # spare carrier
    armor.cyl(.18, .6, loc=(.75, -.45, 1.28), seg=12, bevel=.02, bseg=1)                          # air cleaner
    armor.box((.46, .5, .4), loc=(.78, -.35, .78), bevel=.02, seg=1)                              # battery box
    # Bed under the launcher, tool lockers, mudguards over the bogie, rear lights, jacks.
    body.box((2.2, 4.3, .14), loc=(0, 1.55, 1.2), bevel=.03, seg=1)
    for s in (-1, 1):
        armor.box((.06, 4.3, .08), loc=(s * 1.1, 1.55, 1.28), bevel=0)
        armor.box((.5, 2.5, .06), loc=(s * 1.0, 1.85, 1.3), bevel=.015, seg=1)                   # mudguards
        armor.box((.5, .06, .44), loc=(s * 1.0, .6, 1.08), bevel=.01, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .4), loc=(s * 1.0, 3.2, .72), bevel=0)
        _taillight(a, s * .95, 3.63, 1.1)
        _jack(a, s * .85, 3.35, 1.2, pad=.16)
    armor.box((.36, .9, .4), loc=(.98, .2, .82), bevel=.03, seg=1)                                # tool locker
    steel.box((.03, .06, .08), loc=(1.165, .2, .9), bevel=0)
    steel.box((2.2, .16, .18), loc=(0, 3.6, .86), bevel=.03, seg=1)                              # rear bumper
    # Travel rest behind the cab: the pack's front lies on its padded beam (flat, so the pack swings clear).
    steel.box((.14, .14, 1.0), loc=(0, -.2, 1.44), bevel=0)
    for s in (-1, 1):
        steel.limb((s * .36, -.2, 1.26), (s * .06, -.2, 1.7), .07, .07, bevel=0)                    # braces
    armor.box((.9, .16, .1), loc=(0, -.2, 1.9), bevel=.015, seg=1)                                 # rest beam
    a.part('Rest_pad', 'Rubber').box((.6, .14, .05), loc=(0, -.2, 1.965), bevel=0)

    # Launcher: turntable, base, side brackets and the 40-tube pack on its rear hinge.
    t = a.pivot('Turret', (0, 2.25, 1.27))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.82, .1, loc=(0, 0, .03), seg=20, bevel=.02, bseg=1)                               # turntable
    tarm.box((1.4, 1.3, .32), loc=(0, .05, .22), bevel=.04, seg=1, taper=(.94, .94))               # base
    L, cols, rows, pitch_x, pitch_z, r = 3.0, 10, 4, .16, .158, .066
    W, H = cols * pitch_x, rows * pitch_z
    hinge = Vector((0, .22, .84))                                                                 # pack rear-bottom
    centre = hinge + Vector((0, -L / 2 + .06, H / 2 + .04))
    for s in (-1, 1):
        tarm.prism([(-.5, .06), (.5, .06), (.36, .74), (.3, .96), (.1, .96), (-.3, .6)], .1,
                   loc=(s * (W / 2 + .12), 0, 0), bevel=.02)                                        # brackets
        tsteel.cyl(.1, .06, loc=(s * (W / 2 + .19), hinge.y, hinge.z), rot=ACROSS, seg=10, bevel=0)  # hinge caps
        tsteel.limb((s * .45, -.55, .36), (s * .45, -.78, .76), .1, .1, bevel=0)                    # elevation screws
    tsteel.cyl(.06, W + .4, loc=hinge, rot=ACROSS, seg=8, bevel=0)                                  # hinge axle
    tarm.box((.22, .3, .34), loc=(-.62, -.45, .55), bevel=.02, seg=1)                               # laying sight
    a.part('Sight', 'Glass', t).box((.16, .03, .1), loc=(-.62, -.61, .6), bevel=0)
    tubes = a.part('Rocket_tubes', 'Team', t)
    front = centre.y - L / 2
    for i in range(cols):
        for j in range(rows):
            x = (i - (cols - 1) / 2) * pitch_x
            z = centre.z + (j - (rows - 1) / 2) * pitch_z
            tubes.lathe([(r, 0), (r, L), (r * .76, L), (r * .76, L - .14)], loc=(x, front + L, z), rot=FORWARD,
                        seg=6)
    # A dark plate across the bundle 10 cm inside the mouths: it closes every bore and the gaps between the
    # tubes, so the front face reads as 40 black holes.
    a.part('Rocket_tubes_face', 'Undercarriage', t).box((W - .02, .02, H - .02), loc=(0, front + .1, centre.z),
                                                       bevel=0)
    frame = a.part('Rocket_tubes_frame', 'Armor', t)
    for y in (front + .22, centre.y + .05, front + L - .2):                                        # frames
        frame.box((W + .1, .1, H + .1), loc=(0, y, centre.z), bevel=.015, seg=1)
    for s in (-1, 1):
        frame.box((.05, L - .5, .1), loc=(s * (W / 2 + .06), centre.y + .05, centre.z), bevel=0)    # side bars
    frame.box((.5, L - .4, .12), loc=(0, centre.y + .05, centre.z - H / 2 - .08), bevel=.02, seg=1)  # spine
    frame.box((.14, .22, .16), loc=(0, hinge.y - .06, hinge.z + .04), bevel=0)                      # hinge lug
    a.part('Rocket_tubes_cables', 'Undercarriage', t).box((.12, L - .6, .06),
                                                          loc=(W / 2 - .3, centre.y + .1, centre.z + H / 2 + .05),
                                                          bevel=0)                                  # firing cables
    a.pivot('Muzzle_main', (0, front - .01, centre.z), t)



# ----------------------------------------------------------------------------- atgm_carrier (M1134)
def _box_section(y, zb, zs, z2, zt, wb, ws, wt):
    """Ten-point hull section of a wheeled carrier: a belly between the wheels (wb), a flat shelf over the
    tyres at zs out to ws, vertical sides up to z2 and a short sloped flank to the roof at zt (wt)."""
    return [(-wb, y, zb), (wb, y, zb), (wb, y, zs), (ws, y, zs), (ws, y, z2), (wt, y, zt), (-wt, y, zt), (-ws, y, z2),
            (-ws, y, zs), (-wb, y, zs)]


def atgm_carrier(a):
    """8x8 wheeled anti-tank missile carrier (M1134 Stryker ATGM lineage): a slab-sided hull with a blunt
    wedge nose and bolted applique armour tiles on its sides and upper flanks, the driver's hatch and
    periscopes front left, the engine grille and exhaust on the right, guarded lamps, a rear ramp with
    its door, and a remote weapon station behind the driver. On the roof a small turret raises its
    missile arm: the pod of 2x2 missile tubes (with its sight) sits on top and elevates on the arm's
    hinge."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.32, -1.12, .92, 2.12):
        for s in (-1, 1):
            _wheel(a, s * 1.12, y, .54, .4, seg=14)
            dark.box((.3, .2, .16), loc=(s * .86, y, .54), bevel=.02, seg=1)                     # hub carriers
    full = (.5, 1.14, 1.72, 2.08, .8, 1.36, 1.08)
    hull.loft([
        _box_section(-3.48, .95, 1.14, 1.2, 1.3, .78, 1.2, 1.0),
        _box_section(-2.95, .52, 1.14, 1.58, 1.76, .8, 1.36, 1.1),
        _box_section(-2.45, *full),
        _box_section(3.3, *full),
        _box_section(3.46, .62, 1.14, 1.7, 2.02, .78, 1.33, 1.05),
    ], bevel=.05, seg=2)
    # Applique tiles: a row along each vertical side, a row on each upper flank, a band on the glacis.
    x, z, lean = _flank((1.36, 1.72), (1.08, 2.08), .5, .015)
    tiles = a.part('Tiles', 'Team')
    bolts = a.part('Tile_bolts', 'Steel')
    for s in (-1, 1):
        for i in range(8):
            y = -2.3 + i * .72
            tiles.box((.04, .66, .5), loc=(s * 1.37, y, 1.44), bevel=0)
            tiles.box((.04, .66, .36), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=0)
            bolts.box((.03, .05, .05), loc=(s * 1.395, y - .24, 1.64), bevel=0)
            bolts.box((.03, .05, .05), loc=(s * 1.395, y + .24, 1.26), bevel=0)
    gy, gz, grot = _glacis((-3.48, 1.3), (-2.95, 1.76), .5, .015)
    for xx in (-.66, 0, .66):
        tiles.box((.6, .5, .04), loc=(xx, gy, gz), rot=(grot, 0, 0), bevel=0)
    # Nose: lamps with brush guards, tow eyes, a winch fairlead.
    for s in (-1, 1):
        _headlight(a, s * .92, -3.47, 1.08, guard=True)
        steel.box((.14, .18, .14), loc=(s * .45, -3.5, .98), bevel=.02, seg=1)
        a.part('Marker_lights', 'Alloy').box((.1, .05, .06), loc=(s * 1.18, -3.47, 1.18), bevel=0)
        # Smoke dischargers on the front roof corners, mirrors on arms.
        for k in range(4):
            steel.cyl(.05, .18, loc=(s * (1.0 - k * .08), -2.5, 2.12), rot=(.7, 0, s * .6), seg=8, bevel=0)
        steel.tube([(s * 1.3, -2.7, 1.9), (s * 1.38, -2.88, 1.95)], .016, seg=4)
        armor.box((.05, .16, .26), loc=(s * 1.4, -2.92, 1.9), bevel=.01, seg=1)
        _taillight(a, s * .98, 3.46, 1.82)
        steel.box((.12, .12, .08), loc=(s * .55, 3.53, 1.04), bevel=0)                            # ramp hinges
        a.part('Mud_flaps', 'Rubber').box((.4, .04, .34), loc=(s * 1.12, 2.8, .72), bevel=0)
    dark.box((.5, .1, .14), loc=(0, -3.46, .98), bevel=.02, seg=1)
    # Driver front left: raised hatch ring with periscopes. Engine grille and exhaust on the right.
    armor.cyl(.34, .1, loc=(-.55, -2.1, 2.1), seg=14, bevel=.02, bseg=1)
    _hatch(a, -.55, -2.1, 2.15, .27)
    _periscopes(a, [(-.55 + math.cos(ang) * .36, -2.1 + math.sin(ang) * .36, 2.12, ang + R90)
                    for ang in (-R90, -R90 - .7, -R90 + .7)], size=(.1, .06, .07))
    dark.grille(.8, .7, loc=(.5, -2.05, 2.09), rot=(-R90, 0, 0), slats=6, depth=.07, thickness=.04)
    _grille_frame(a, .5, -2.05, 2.07, .8, .7, t=.04)
    armor.box((.1, .6, .26), loc=(1.39, -1.6, 1.52), bevel=.015, seg=1)                            # exhaust
    dark.grille(.5, .16, loc=(1.445, -1.6, 1.52), rot=(0, 0, R90), slats=2, depth=.04, thickness=.03)
    # Roof: the remote weapon station behind the driver, a rear troop hatch, antennas, a tow cable.
    armor.cyl(.26, .06, loc=(-.5, -1.2, 2.09), seg=12, bevel=0)
    _rws(a, None, (-.5, -1.2, 2.1))
    armor.box((1.0, .8, .06), loc=(0, 2.7, 2.09), bevel=.015, seg=1)                              # troop hatch
    steel.box((.8, .06, .05), loc=(0, 2.32, 2.12), bevel=0)
    for xx, h in ((-.85, 1.4), (.85, 1.1)):
        steel.box((.1, .1, .07), loc=(xx, 3.1, 2.08), bevel=0)
        _antenna(a, None, xx, 3.1, 2.1, h)
    _cable(a, [(-.95, -1.9, 2.1), (-.95, .0, 2.1), (-.95, 1.9, 2.1)])
    _stowage_bin(a, (.72, 2.2, 2.07), (.5, .8, .24), latch_side=0)
    for s in (-1, 1):                                                  # vision blocks along the roof edges
        _periscopes(a, [(s * .98, y, 2.07, s * R90) for y in ((-.6, 1.8, 2.6) if s > 0 else (2.85, 3.22))])
        _rail(a, [(s * .9, -.2, 2.07), (s * .9, -.2, 2.14), (s * .9, .5, 2.14), (s * .9, .5, 2.07)])  # grab rails
    _stowage_bin(a, (-.72, 2.2, 2.07), (.5, .8, .24), latch_side=0)
    for y in (-.45, 1.75):                                             # roof plate seams
        armor.box((1.9, .04, .03), loc=(0, y, 2.085), bevel=0)
    gy, gz, grot = _glacis((-2.95, 1.76), (-2.45, 2.08), .5, .01)
    armor.box((2.0, .04, .03), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=0)                    # glacis seam
    # Rear: ramp with a personnel door, handle, step and a jerrycan either side.
    armor.box((1.5, .07, 1.0), loc=(0, 3.47, 1.55), bevel=.02, seg=1)
    armor.box((.6, .06, .8), loc=(-.28, 3.5, 1.55), bevel=.015, seg=1)
    steel.box((.2, .05, .05), loc=(-.05, 3.54, 1.55), bevel=0)
    steel.box((1.0, .26, .05), loc=(0, 3.58, .98), bevel=0)
    for s in (-1, 1):
        _jerrycans(a, (s * 1.08, 3.56, 1.3), 1, axis='x', bracket=False)
    a.part('Jerrycan_rack', 'Steel').box((2.2, .05, .05), loc=(0, 3.65, 1.55), bevel=0)
    steel.cyl(.62, .08, loc=(0, .8, 2.1), seg=20, bevel=.02, bseg=1)                              # turret ring

    # Turret: a low base, the missile arm and the elevating pod on its hinge.
    t = a.pivot('Turret', (0, .8, 2.12))
    tteam = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tteam.prism(chamfered(1.3, 1.5, .3), .34, loc=(0, 0, .17), axis='Z', bevel=.04, taper=.9)       # base
    _hatch(a, -.3, .3, .34, .22, parent=t)
    tarm.box((.36, .4, .22), loc=(.35, .45, .44), bevel=.03, seg=1)                                 # electronics
    L, W, H = 1.75, .72, .68
    px, y0, zb = .12, -1.02, .98                                                                     # pod centre x, front, bottom
    hinge = Vector((px, y0 + L - .06 * L, zb + .3 * H))                                              # the game's pivot
    arm = a.part('Missile_arm', 'Armor', t)
    ax = px - W / 2 - .1
    arm.box((.18, .46, hinge.z - .2), loc=(ax, hinge.y - .05, (hinge.z + .2) / 2 + .02), bevel=.03, seg=1)
    arm.box((.2, .3, .3), loc=(ax, hinge.y - .05, .38), bevel=.03, seg=1)                            # arm root
    tsteel.limb((ax + .02, -.25, .36), (ax + .02, hinge.y - .28, hinge.z - .35), .08, .08, bevel=0)  # ram
    tsteel.cyl(.1, .16, loc=(ax + .06, hinge.y, hinge.z), rot=ACROSS, seg=10, bevel=0)                # hinge boss
    pod = a.part('Launcher', 'Team', t)
    pod.box((W, L, H), loc=(px, y0 + L / 2, zb + H / 2), bevel=.04, seg=1)
    frame = a.part('Launcher_frame', 'Armor', t)
    for y in (y0 + .12, y0 + L - .14):
        frame.box((W + .05, .1, H + .05), loc=(px, y, zb + H / 2), bevel=.012, seg=1)
    frame.box((.08, L - .5, .06), loc=(px, y0 + L / 2 + .05, zb + H + .02), bevel=0)               # top rail
    for cx in (-.17, .17):
        for cz in (-.17, .17):
            _tube_mouth(a, t, _frame((px + cx, y0, zb + H / 2 + cz), FORWARD), .12, protrude=.06, seg=10,
                        name='Launcher_tubes')
    frame.box((.16, .3, .24), loc=(px + W / 2 + .07, y0 + .3, zb + H / 2 + .08), bevel=.02, seg=1)  # sight
    a.part('Launcher_sight', 'Glass', t).box((.12, .03, .14), loc=(px + W / 2 + .07, y0 + .145, zb + H / 2 + .09),
                                              bevel=0)
    # Muzzle_main on the pod's front face at the hinge's height, so the game reads the pod as level (a
    # direct-fire weapon rests at 0 degrees and must not droop).
    a.pivot('Muzzle_main', (px, y0 - .065, hinge.z), t)



# ----------------------------------------------------------------------------- aps_tank (Merkava Mk4)
def _turret_section(y, zb, zm, zt, wb, ws, wt):
    """Six-point turret section: floor (wb), side top at zm (ws), roof edge (wt at zt)."""
    return [(-wb, y, zb), (wb, y, zb), (ws, y, zm), (wt, y, zt), (-wt, y, zt), (-ws, y, zm)]


def _aps_radar(a, parent, loc, yaw):
    """Flat radar panel of the active protection system: a thick frame with a dark antenna face looking
    along -Y rotated by yaw, on a bracket."""
    m = _frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Aps_radar', 'Armor', parent).box((.72, .1, .54), loc=loc, rot=rot, bevel=.02, seg=1)
    a.part('Aps_radar_face', 'Undercarriage', parent).box((.6, .03, .42), loc=m @ Vector((0, -.055, 0)), rot=rot,
                                                           bevel=0)
    a.part('Aps_radar', 'Armor', parent).box((.14, .18, .34), loc=m @ Vector((0, .12, -.06)), rot=rot, bevel=0)


def aps_tank(a):
    """Main battle tank with an active protection system (Merkava Mk4 with Trophy lineage): front engine
    and a long shallow glacis with the driver's hatch at its head, air intakes and exhaust on the right,
    six road wheels behind heavy skirts with a saw-tooth lower edge, the rear door and rear baskets.
    Its own low wedge turret is set back on the hull: two long armour cheeks close to a point either side
    of the gun slot, the bustle overhangs with a ball-and-chain curtain under it and a basket behind it.
    The protection system is plain to see: four flat radar panels on the turret faces (two looking
    forward-out, two back-out) and a launcher head on each turret side (`Aps_left` / `Aps_right` at
    their openings). Smooth-bore 120 mm gun with a thermal sleeve, coaxial and roof machine guns."""
    tracks(a, 1.33, 6.9, .95, .32, 6, .5, belt_width=.64, wheel_seg=10, lean=True, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.4, .56), (-3.72, 1.12), (3.7, 1.12), (3.7, .56)], 1.96, bevel=.05)          # belly
    nose, brow = (-3.85, 1.12), (-1.95, 1.72)
    hull.prism([(-3.72, 1.02), nose, brow, (3.55, 1.72), (3.8, 1.55), (3.8, 1.02)], 3.36, bevel=.07)
    # Heavy skirts: five plates a side whose lower front corners are cut away (the saw-tooth edge).
    skirt = a.part('Skirts', 'Team')
    lip = a.part('Skirt_edge', 'Armor')
    for s in (-1, 1):
        y0 = -3.3
        for i in range(5):
            ya, yb = y0 + i * 1.36, y0 + i * 1.36 + 1.32
            skirt.prism([(ya, 1.5), (ya, .82), (ya + .32, .6), (yb, .6), (yb, 1.5)], .12, loc=(s * 1.79, 0, 0),
                        bevel=.025, seg=1)
            lip.box((.15, 1.34, .05), loc=(s * 1.79, (ya + yb) / 2, 1.495), bevel=0)
        gy, gz, grot = _glacis(nose, brow, .1, .03)
        armor.box((.34, .2, .16), loc=(s * 1.3, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)     # lamp housings
        ly, lz, _ = _glacis(nose, brow, .045, .045)
        a.part('Lamps', 'Lamp').box((.24, .03, .09), loc=(s * 1.3, ly, lz), rot=(grot, 0, 0), bevel=0)
        steel.box((.16, .2, .14), loc=(s * .7, -3.76, .98), bevel=.02, seg=1)                   # tow hooks
        steel.box((.16, .2, .14), loc=(s * .9, 3.86, .98), bevel=.02, seg=1)
        _taillight(a, s * 1.45, 3.8, 1.36)
        # Rear baskets at the hull corners.
        _basket(a, s * .75 - .45, s * .75 + .45, 3.0, 3.72, 1.71, .28, contents=False)
    # Glacis: add-on armour plates and the driver's hatch with vision blocks at its head.
    for row, u in enumerate((.3, .62)):
        gy, gz, grot = _glacis(nose, brow, u, .035)
        for x in ((-1.1, -.37, .37, 1.1) if row else (-1.2, -.6, 0, .6, 1.2)):
            armor.box((.66 if row else .54, .5, .08), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
    _hatch(a, -.72, -1.72, 1.71, .26, handle=False)
    gy, gz, grot = _glacis(nose, brow, .93, .015)
    a.part('Vision_blocks', 'Glass').box((.5, .07, .05), loc=(-.72, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    # Engine air intakes on the right of the deck, exhaust louvres on the right flank.
    for y in (-1.55, -.95):
        deck.grille(.9, .45, loc=(.95, y, 1.73), rot=(-R90, 0, 0), slats=4, depth=.06, thickness=.04)
    _grille_frame(a, .95, -1.25, 1.71, .9, 1.05, t=.04)
    armor.box((.1, .9, .3), loc=(1.7, -1.0, 1.6), bevel=.015, seg=1)
    deck.grille(.8, .2, loc=(1.755, -1.0, 1.6), rot=(0, 0, R90), slats=2, depth=.04, thickness=.03)
    _cable(a, [(-1.45, -1.9, 1.745), (-1.45, .2, 1.745), (-1.45, 2.6, 1.745)])
    # Rear door in the middle of the tail, hinged on the left, with a handle and a step.
    armor.box((.95, .07, .52), loc=(0, 3.8, 1.25), bevel=.02, seg=1)
    for z in (1.08, 1.42):
        steel.box((.08, .1, .1), loc=(-.5, 3.84, z), bevel=0)
    steel.box((.24, .05, .05), loc=(.3, 3.855, 1.25), bevel=0)
    steel.box((.9, .2, .05), loc=(0, 3.86, .9), bevel=0)
    steel.cyl(1.3, .1, loc=(0, .7, 1.75), seg=24, bevel=.02, bseg=1)                             # turret ring

    t = a.pivot('Turret', (0, .7, 1.75))
    turret = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    turret.loft([
        _turret_section(-1.62, .02, .52, .78, 1.2, 1.26, 1.0),
        _turret_section(1.2, .02, .58, .84, 1.52, 1.58, 1.3),
        _turret_section(1.62, .22, .58, .84, 1.5, 1.56, 1.28),
        _turret_section(2.4, .28, .56, .78, 1.38, 1.44, 1.18),
    ], bevel=.05, seg=2)
    # Two long armour cheeks close to a point either side of the gun slot.
    for s in (-1, 1):
        def sec(y, xo, zb, zt, ch):
            pts = [(xo, y, zb), (.27, y, zb), (.27, y, zt), (xo - ch, y, zt), (xo, y, zt - ch)]
            return [(s * px, py, pz) for px, py, pz in pts]
        turret.loft([sec(-1.5, 1.22, .03, .77, .2), sec(-2.35, .8, .1, .6, .14), sec(-3.05, .42, .22, .44, .06)],
                    bevel=.03, seg=1)
    tarm.box((.5, .42, .44), loc=(0, -1.66, .46), bevel=.04, seg=1)                             # mantlet
    # Ball-and-chain curtain under the bustle, a basket behind it.
    chains = a.part('Chains', 'Steel', t)
    for i in range(14):
        x = -1.04 + i * .16
        chains.box((.025, .025, .22), loc=(x, 2.9, .19), bevel=0)
        chains.box((.07, .07, .07), loc=(x, 2.9, .07), bevel=0)
    _basket(a, -1.1, 1.1, 2.36, 2.95, .3, .3, parent=t)
    # Protection system: four radar panels on the turret faces and a launcher head on each side.
    for s in (-1, 1):
        _aps_radar(a, t, (s * 1.2, -1.25, .98), s * .75)
        _aps_radar(a, t, (s * 1.38, 1.74, .98), s * (math.pi - .75))
        tsteel.cyl(.1, .2, loc=(s * 1.42, .55, .82), seg=10, bevel=0)                             # launcher mount
        head = a.part('Aps_launcher', 'Armor', t)
        m = _frame((s * 1.42, .55, 1.06), (0, 0, s * .7))
        head.box((.34, .42, .3), loc=m.to_translation(), rot=(0, 0, s * .7), bevel=.03, seg=1)
        _tube_mouth(a, t, m @ _frame((0, -.21, 0), FORWARD), .1, protrude=.05, seg=10, name='Aps_tube')
        a.pivot('Aps_left' if s < 0 else 'Aps_right', tuple(m @ Vector((0, -.27, 0))), t)
        # Smoke dischargers on the cheeks, a rail along the roof edge.
        for k in range(3):
            tsteel.cyl(.05, .18, loc=(s * (1.0 + k * .08), -.7 + k * .1, .82), rot=(.6, 0, s * .5), seg=8, bevel=0)
    # Roof: commander's cupola with the machine gun (right), loader's hatch and the 60 mm mortar (left),
    # the gunner's sight on the right cheek, wind sensor and antennas.
    tsteel.cyl(.33, .14, loc=(.6, .3, .88), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.28, .06, loc=(.6, .3, .97), seg=16, bevel=.015, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(5):
        ang = -R90 + (k - 2) * .62
        glass.box((.1, .05, .07), loc=(.6 + math.cos(ang) * .33, .3 + math.sin(ang) * .33, .9),
                  rot=(0, 0, ang + R90), bevel=0)
    _roof_mg(a, t, (.6, .3, 1.0), length=.9)
    _hatch(a, -.6, .45, .85, .26, parent=t)
    tsteel.cyl(.07, .7, loc=(-.95, .9, 1.0), rot=(-.5, 0, 0), seg=8, bevel=0)                     # mortar
    tarm.box((.3, .3, .24), loc=(.55, -1.1, .82), bevel=.03, seg=1)                              # gunner's sight
    a.part('Sight', 'Glass', t).box((.22, .03, .12), loc=(.55, -1.26, .84), bevel=0)
    tsteel.cyl(.02, .3, loc=(0, 1.6, 1.0), seg=5, bevel=0)                                        # wind sensor
    tsteel.box((.08, .08, .1), loc=(0, 1.6, 1.18), bevel=0)
    for x, h in ((-1.0, 1.4), (1.0, 1.1)):
        tsteel.box((.09, .09, .06), loc=(x, 2.05, .83), bevel=0)
        _antenna(a, t, x, 2.05, .84, h)
    tip = _barrel(a, t, start_y=-1.8, length=4.3, radius=.11, height=.46, brake=(.26, .24, .26),
                  sleeve=(.42, .5, .16), style='collar', bands=(.2, .72))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .19, -1.79, .6, length=.4, housing=.26)


BUILDERS = {
    'artillery': (artillery, dict(ao_distance=.6, grime_height=.55)),
    'howitzer': (howitzer, dict(ao_distance=.6, grime_height=.55)),
    'siege_tank': (siege_tank, dict(ao_distance=.7, grime_height=.6)),
    'grad_truck': (grad_truck, dict(ao_distance=.6, grime_height=.55)),
    'atgm_carrier': (atgm_carrier, dict(ao_distance=.6, grime_height=.55)),
    'aps_tank': (aps_tank, dict(ao_distance=.6, grime_height=.55)),
}
