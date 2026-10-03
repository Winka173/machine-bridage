"""Owner fix 2 (2026-10-03, lane A): the amphibious light vehicle rebuilt off AAV-7, which prompt 24 keeps for a
future card (spec: Tools/blender/specs/amphib_light_vehicle.json). Replaces lane C's wave 4 builder.

An amphibious tracked infantry fighting vehicle in the AMX-10P pattern (the AMX-10P Marine of the Indonesian and
Singapore marines swims on its two water jets), fitted to the def's modelSize 5.48 x 3.02 x 2.5 m (the real one is
5.79 x 2.78 x 2.57 m; confidence ban_dau_doan): the welded hull with the long upper glacis and the short lower
one meeting at a wedge nose, the trim vane folded flat on the glacis, the headlights in their guards on the nose
corners; the driver's hatch and periscopes on the front left, the engine grilles on the front right glacis and
roof, the exhaust louvre on the right side; sponson sides straight over the tracks with a lip along their foot;
five road wheels a side with three return rollers, the front drive sprocket and the rear idler, the track run
open to view; the troop roof with two hatches and side vision blocks; the big rear ramp with its vision blocks and
the two water-jet housings with their deflector doors either side of it. The two-man Toucan-pattern turret, set a
little left of the centre line behind the driver, carries the 25 mm cannon of the data (the real one a 20 mm
M693) with a coaxial MG, the commander's sight, two roof hatches, side ammunition boxes and smoke dischargers.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Point_exhaust`,
`Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
# Running gear: track centre, width (outer edge 1.50 m: the def's 3.02 m), road wheels, sprocket / idler (y, z, r).
TX, TW = 1.27, .46
WR = .30
WHEELS = (-1.56, -.78, 0.0, .78, 1.56)
SPROCKET = (-2.22, .56, .25)
IDLER = (2.2, .52, .25)
ROLLERS = [(-1.17, .72), (0.0, .73), (1.17, .72)]
# Hull: nose and tail plates, roof, belly, sponson foot, half widths (over the tracks, between them).
NOSE, TAIL = -2.70, 2.50
TOP, BELLY, SPON = 1.70, .42, .93
HALF, LOW = 1.49, 1.0
GLACIS_END = -1.30
NOSE_Z = .98
SLOPE = (TOP - NOSE_Z) / (GLACIS_END - NOSE)
GLACIS = math.atan(SLOPE)
TUR = (.12, -.35, TOP)


def glacis_z(y):
    """The upper glacis's height at y (from the nose up to the roof)."""
    return NOSE_Z + (y - NOSE) * SLOPE


def _sec(zb, wl, zs, ws, zt, ch):
    """A hull half section: belly, lower hull between the tracks, sponson foot, side, chamfered roof edge."""
    return [(0, zb), (wl, zb), (wl, zs), (ws, zs), (ws, zt - ch), (ws - ch, zt), (0, zt)]


def _hull(a):
    hull = a.part('Hull', 'Team')
    C.section_loft(hull, [
        (NOSE, _sec(.90, .92, SPON, 1.28, NOSE_Z, .03)),
        (-2.50, _sec(.70, LOW, SPON, 1.44, glacis_z(-2.50), .04)),
        (-2.20, _sec(BELLY, LOW, SPON, HALF, glacis_z(-2.20), .06)),
        (GLACIS_END, _sec(BELLY, LOW, SPON, HALF, TOP, .08)),
        (TAIL - .18, _sec(BELLY, LOW, SPON, HALF, TOP, .08)),
        (TAIL, _sec(.48, .98, SPON, HALF - .02, TOP - .03, .08)),
    ])
    st = a.part('Kit_steel', 'Steel')
    # The sponson foot's lip over the track run, the team bands, the weld seams (rivet lines).
    for s in (-1, 1):
        a.part('Skirt_edge', 'Armor').box((.04, 4.7, .08), loc=(s * (HALF + .02), -.05, SPON + .04), bevel=0)
        a.part('Team_band', 'Team').box((.012, 2.6, .1), loc=(s * (HALF + .006), .55, 1.42), bevel=0)
        K.rivet_line(st, (s * (HALF + .01), -1.9, 1.12), (s * (HALF + .01), 2.3, 1.12), (s, 0, 0), pitch=.32,
                     r=.015)
        for y in (-.4, 1.0):
            K.handle(st, (s * (HALF + .01), y - .15, 1.3), (s * (HALF + .01), y + .15, 1.3), (s, 0, 0), h=.05,
                     r=.012)
    # The trim vane folded flat on the glacis, its ribs and the hinge arms at its foot.
    vane = a.part('Bow_plane', 'Armor')
    vy = -2.22
    vz = glacis_z(vy) + .035
    K.plate(vane, (2.3, .78, .04), loc=(0, vy, vz), rot=(GLACIS, 0, 0), chamfer=.012)
    for x in (-.75, 0, .75):
        vane.box((.05, .74, .03), loc=(x, vy - .012, vz + .025), rot=(GLACIS, 0, 0), bevel=0)
    for x in (-1.0, 1.0):
        K.hinge(st, (x - .1, NOSE + .1, glacis_z(NOSE + .1) + .03), (x + .1, NOSE + .1, glacis_z(NOSE + .1) + .03),
                r=.025, knuckles=2)
    # Nose: lamps in guards on the corners, tow hooks.
    for s in (-1, 1):
        K.lamp(a, (s * 1.18, -2.56, glacis_z(-2.56) + .06), (0, -1, .35), r=.07, guard=True)
        K.tow_hook(st, (s * .72, NOSE - .02, .9), facing=(0, -1, 0), size=.08)
    # The driver on the front left: hatch and three periscopes looking over the glacis.
    C.hatch(a, (.72, -1.08, TOP + .01), r=.26)
    for dx in (-.2, 0, .2):
        K.periscope(a, (.72 + dx, -1.4, TOP - .01), facing=(0, -1, 0), size=(.12, .1, .08))
    # The engine on the front right: grilles on the glacis and the roof, the exhaust louvre on the right side.
    gy = -1.75
    K.grille(a, (-.62, gy, glacis_z(gy) + .01), .72, .5, facing=(0, -math.sin(GLACIS), math.cos(GLACIS)), slats=5,
             frame_mat='Team')
    K.grille(a, (-.62, -.98, TOP + .01), .72, .42, facing=(0, 0, 1), slats=4, frame_mat='Team')
    K.grille(a, (-HALF - .01, -1.3, 1.38), .55, .28, facing=(-1, 0, 0), slats=3, frame_mat='Team')
    a.pivot('Point_exhaust', (-HALF - .06, -1.3, 1.42))
    # The troop roof: two hatches over the rear, vision blocks along both roof edges.
    hp = a.part('Hatches', 'Armor')
    for x in (-.45, .45):
        K.plate(hp, (.74, .82, .04), loc=(x, 1.62, TOP + .02))
        K.hinge(st, (x - .3, 1.2, TOP + .05), (x + .3, 1.2, TOP + .05), r=.02, knuckles=3)
    for s in (-1, 1):
        for y in (.55, 1.15, 1.75):
            K.periscope(a, (s * (HALF - .14), y, TOP + .01), facing=(s, 0, 0), size=(.1, .14, .08))
    C.stowage_box(a, (.42, .78, .24), (-1.02, .45, TOP), mat='Armor', latches=1)
    C.jerry_rack(a, (1.02, 2.12, TOP), count=2, axis='Y', rot=(0, 0, R90))
    a.pivot('Point_fire', (0, .8, TOP + .3))


def _rear(a):
    st = a.part('Kit_steel', 'Steel')
    # The ramp: one big plate down the rear with two vision blocks, a handle, the hinges along its foot.
    K.plate(a.part('Ramp', 'Armor'), (1.46, .05, 1.06), loc=(0, TAIL + .03, 1.09))
    for x in (-.35, .35):
        a.part('Periscopes', 'Glass').box((.16, .02, .08), loc=(x, TAIL + .065, 1.45), bevel=0)
    K.handle(st, (.55, TAIL + .07, 1.0), (.55, TAIL + .07, 1.2), (0, 1, 0), h=.04, r=.012)
    for x in (-.5, .5):
        K.hinge(st, (x - .14, TAIL + .07, .6), (x + .14, TAIL + .07, .6), r=.03, knuckles=2)
    # The water jets either side of the ramp: housings, their dark outlets, the deflector doors; tail lamps.
    for s in (-1, 1):
        jet = a.part('Waterjets', 'Armor')
        k.extrude(jet, [(-.24, -.2), (.24, -.2), (.24, .2), (-.24, .2)], .2, loc=(s * 1.15, TAIL + .12, .82),
                  axis='Y', chamfer=.04, corner=.05)
        a.part('Waterjets_dark', 'Undercarriage').box((.34, .01, .28), loc=(s * 1.15, TAIL + .225, .82), bevel=0)
        K.plate(a.part('Jet_doors', 'Armor'), (.46, .03, .36), loc=(s * 1.15, TAIL + .25, .82))
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.2, TAIL + .03, 1.52), bevel=0)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=SPROCKET, idler=IDLER, rollers=ROLLERS, pitch=.2,
                       hide_top=None, disc_mat='Armor', wheel_w=.2, seg=10, teeth=11)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .7, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.6, -.62), (.6, -.62), (.72, -.36), (.72, .62), (.55, .8), (-.55, .8), (-.72, .62), (-.72, -.36)]
    top = [(-.4, -.47), (.4, -.47), (.58, -.26), (.6, .55), (.45, .7), (-.45, .7), (-.6, .55), (-.58, -.26)]
    C.slab_loft(body, bot, top, 0, .52)
    # The mantlet, the 25 mm cannon with its flash collar, the coaxial MG.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.13, -.15), (.1, -.16), (.13, .15), (-.1, .16)], .42, loc=(0, -.64, .28), axis='X',
              chamfer=.02, corner=.02)
    end = C.gun_tube(a, 'Main_cannon', t, (0, -.74, .28), 1.15, .035, seg=8, sleeve=2, brake='collar',
                     brake_name='Muzzle_brake')
    a.pivot('Muzzle_main', (end[0], end[1] - .06, end[2]), t)
    co = a.pivot('Coax', (.24, -.64, .3), t)
    a.part('MG_coax', 'Steel', co).cyl(.018, .36, loc=(0, -.18, 0), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_coax', (0, -.37, 0), co)
    # The commander's sight head on the left front, the gunner's periscope, two roof hatches.
    sight = a.part('Sight', 'Armor', t)
    k.extrude(sight, [(-.1, -.1), (.1, -.1), (.1, .1), (-.1, .1)], .16, loc=(.32, -.22, .6), axis='Z', chamfer=.02,
              corner=.02)
    a.part('Sight_glass', 'Glass', t).box((.14, .01, .08), loc=(.32, -.325, .6), bevel=0)
    K.periscope(a, (-.3, -.4, .52), facing=(0, -1, 0), parent=t, size=(.16, .12, .1))
    C.hatch(a, (.28, .28, .52), r=.22, parent=t)
    C.hatch(a, (-.28, .28, .52), r=.22, parent=t)
    # Ammunition boxes on the turret cheeks, the smoke dischargers, the team band, the aerial.
    ammo = a.part('Ammo_boxes', 'Armor', t)
    for s in (-1, 1):
        K.plate(ammo, (.12, .5, .26), loc=(s * .78, .25, .22), chamfer=.015)
        K.smoke_dischargers(a, .66, -.2, .34, s, count=2, parent=t)
    a.part('Team_band', 'Team', t).box((1.0, .01, .07), loc=(0, .79, .24), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.5, .55, .52), h=.22)


def amphib_light_vehicle(a, detail=False):
    """The amphibious light vehicle: see the module docstring."""
    _hull(a)
    _rear(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=2.6, k=.14)
    k.clean(a)


BUILDERS = {
    'amphib_light_vehicle': (amphib_light_vehicle, dict(ao_distance=.5, grime_height=.6)),
}
