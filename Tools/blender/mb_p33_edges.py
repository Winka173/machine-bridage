"""Prompt 33 L2 (view side): the prebuilt edge pieces, the sea's dressing and the edge-type sets on the V2 kit
(DECISIONS "Prompt 33 L2 view / L7").

Decoration only: Surroundings.Edges.cs stands these round the map from its "edges" data (Tools/maps/edges.py) and
map_dressing.json; no collider, never a route or a line of sight, never in the simulation.

* `dress_edge_<piece>`: the ten corner pieces edges.py names where two edge types meet along a side and at the
  rectangle's four corners. Frame (Unity, after the glTF import; the helper B() below maps it to Blender): the map's
  edge runs along local X at z = 0 and local +Z points out of the map. A junction piece (corner_*, bank_*,
  embankment_*) has its first type on local -X and its second on +X (corner_land_sea: land at -X, sea at +X, the
  coast running out along +Z from the origin). An outer piece stands at the rectangle's corner with the map in the
  -X/-Z quadrant: the strip beyond the +Z side (z > 0, x < 0) is its first type, the strip beyond the +X side
  (x > 0, z < 0) its second, the corner square (x, z > 0) between them. The view mirrors a piece when the data's order
  is the other way round. Ground patches dip under the view's ground at their rims so no seam shows; nothing is water
  (the view draws the sea and the rivers).
* `dress_sea_*`: whitecaps, surf lines, far ship silhouettes, a hazy far island, a sea stack (cliff shores).
* `dress_edge_*` (others): quay wall segment, far gantry crane, container stack, chimney, storage tanks, scree, the
  rail track section (6 m, along local Z) and the tunnel portal at a RailSpline's far end.

    blender --background --python Tools/blender/build_assets.py -- dress_edge_ dress_sea_
"""
import math
import random

import mb_kit27 as k

R90 = math.pi / 2


def B(x, z, y=0.0):
    """Unity-local (x along the edge, z out of the map, y up) to Blender: the import turns Blender (x, y) by 180 deg."""
    return (-x, -z, y)


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def patch(part, x0, x1, z0, z1, nx, nz, h, rim=-0.25):
    """A ground patch over [x0, x1] x [z0, z1] (Unity-local) with heights h(x, z); its rim dips under the ground."""
    verts, faces = [], []
    for j in range(nz + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            z = z0 + (z1 - z0) * j / nz
            edge = i in (0, nx) or j in (0, nz)
            verts.append(B(x, z, rim if edge else h(x, z)))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    part.mesh(verts, faces)


def rocks(part, items, sub=2, jitter=.28):
    for i, (x, z, y, r) in enumerate(items):
        part.ico(r, loc=B(x, z, y), sub=sub, jitter=jitter, seed=i * 2.3 + x * .1 + z * .07)


def tree(trunk, crown, x, z, h=7.0, seed=0.0):
    trunk.cyl(.25, h * .4, loc=B(x, z, h * .2), seg=5, r2=.17, bevel=0)
    crown.ico((h * .3, h * .28, h * .36), loc=B(x, z, h * .62), sub=0, jitter=.14, seed=seed)


def reeds(part, x, z, n, seed, height=1.3, spread=1.2):
    rng = random.Random(seed)
    for _ in range(n):
        dx, dz = rng.uniform(-spread, spread), rng.uniform(-spread, spread)
        hh = height * rng.uniform(.6, 1.1)
        part.cyl(.05, hh, loc=B(x + dx, z + dz, hh / 2 - .1), rot=(rng.uniform(-.2, .2), rng.uniform(-.2, .2), 0),
                 seg=3, r2=.01, bevel=0)


def foam(part, x, z, length, seed, width=.7, along_x=False):
    """A broken foam line: flattened slivers along local Z (or X)."""
    rng = random.Random(seed)
    s = 0.0
    while s < length:
        piece = rng.uniform(1.6, 3.4)
        c = s + piece / 2
        off = rng.uniform(-.4, .4)
        px, pz = (x + c, z + off) if along_x else (x + off, z + c)
        r = (piece / 2, width * rng.uniform(.6, 1.1), .06) if along_x else (width * rng.uniform(.6, 1.1), piece / 2, .06)
        part.ico((r[0], r[1], r[2]), loc=B(px, pz, .02), sub=0, jitter=.15, seed=seed + s)
        s += piece + rng.uniform(.2, 1.2)


def lamp_post(steel, lamp, x, z, h=6.0):
    steel.cyl(.09, h, loc=B(x, z, h / 2), seg=6, bevel=0)
    lamp.box((.5, .3, .18), loc=B(x, z, h + .05), bevel=0)


# ============================================================================= junction pieces
def corner_land_sea(a):
    """Land (-X) meeting the sea (+X) where the coast leaves the map: a sand beach falling into the water, a rocky
    point at the edge and rocks along the shore, dune grass on the land side, a broken surf line (26 x 36 m)."""
    def h(x, z):
        n = math.sin(z * .45 + x * .2) * .05
        if x < -12:
            return .35 + n
        if x < 1:
            return .35 * (1 - (x + 12) / 13) + n
        return -.6 * smooth(1, 9, x)
    patch(a.part('Beach', 'Sandstone', flat=True), -16, 10, -1.5, 36, 13, 14, h)
    rocks(a.part('Rocks', 'Rock', flat=True), ((1.5, 2.5, .4, (2.2, 1.8, 1.5)), (3.5, 5.5, .1, (1.4, 1.2, 1.0)),
                                               (-.5, 6.5, .2, (1.1, 1.0, .8)), (2.5, 19, .0, (1.3, 1.1, .7)),
                                               (4.5, 29, .0, (1.6, 1.3, .8))))
    grass = a.part('Dune', 'FoliageLight', flat=True)
    for i, (x, z) in enumerate(((-10, 4), (-13, 11), (-9, 17), (-12, 25), (-8, 31))):
        grass.ico((1.1, .9, .35), loc=B(x, z, .35), sub=0, jitter=.3, seed=i + .5)
    foam(a.part('Surf', 'PlasterWhite'), 2.0, 1, 34, 7)


def corner_land_cliff(a):
    """Open land (-X) meeting a cliff stretch (+X): a scree ramp climbing to the cliff's height, boulders at its foot
    and a few shrubs (26 x 29 m, 9 m high)."""
    def h(x, z):
        n = math.sin(z * .6) * .5 + math.cos(x * .9 + z * .3) * .35
        return max(0.0, 9.5 * smooth(-7, 11, x) * (.85 + .15 * math.sin(z * .25)) + n * smooth(-7, 2, x))
    patch(a.part('Scree', 'Rock', flat=True), -12, 14, -1.5, 28, 9, 10, h)
    rocks(a.part('Boulders', 'Rock', flat=True), ((-5, 4, .3, (1.3, 1.1, .9)), (-7, 12, .2, (.9, .8, .6)),
                                                  (-4.5, 21, .3, (1.2, 1.0, .8)), (-8.5, 25, .1, (.7, .6, .5))))
    bush = a.part('Shrubs', 'FoliageDark', flat=True)
    for i, (x, z) in enumerate(((-9, 7), (-10, 18), (-6.5, 15))):
        bush.ico((.9, .8, .7), loc=B(x, z, .5), sub=0, jitter=.25, seed=i * 1.3)


def bank_land_river(a):
    """Land (-X) meeting a river leaving the map (+X): a grassy bank sloping into the water, reeds at the waterline,
    stones and a small timber jetty (20 x 33 m)."""
    def h(x, z):
        n = math.sin(z * .5) * .06
        return .45 - 1.25 * smooth(-8, 4, x) + n
    patch(a.part('Bank', 'Grass', flat=True), -14, 6, -1.5, 32, 10, 12, h)
    rd = a.part('Reeds', 'FoliageLight')
    for i, z in enumerate((3, 9, 16, 23, 29)):
        reeds(rd, -.8, z, 6, 11 + i)
    rocks(a.part('Stones', 'Rock', flat=True), ((-2, 6, .1, (.8, .7, .5)), (-3, 20, .1, (.7, .6, .4)),
                                                (.5, 26, -.2, (.9, .7, .5))))
    wood = a.part('Jetty', 'Wood')
    wood.box((8, 2.2, .18), loc=B(1, 13, .45), bevel=0)
    for x in (-2.5, .5, 3.5):
        for dz in (-.9, .9):
            wood.cyl(.12, 2.2, loc=B(x, 13 + dz, -.5), seg=5, bevel=0)


def embankment_urban_river(a):
    """The city (-X) meeting its river (+X): a stone embankment wall along the bank with coping and railings, a
    paved quay walk, steps down to the water and two lamps (12 x 32 m)."""
    stone = a.part('Wall', 'Sandstone')
    stone.box((1.2, 32, 2.4), loc=B(-.6, 16, -.6), bevel=0)
    stone.box((1.6, 32, .3), loc=B(-.7, 16, .72), bevel=0)
    # Steps down to the water, cut along the wall's face.
    for i in range(5):
        stone.box((.9, 2.6 - i * .1, .28), loc=B(.45, 20.5, .4 - i * .32), bevel=0)
    pave = a.part('Walk', 'Concrete')
    pave.box((5.5, 32, .14), loc=B(-4.0, 16, .07), bevel=0)
    steel = a.part('Railing', 'Steel')
    z = 1.0
    while z < 31.5:
        if not 19 <= z <= 22:
            steel.cyl(.04, 1.0, loc=B(-.25, z, 1.37), seg=4, bevel=0)
        z += 2.5
    steel.box((.06, 18.5, .06), loc=B(-.25, 9.7, 1.86), bevel=0)
    steel.box((.06, 9.5, .06), loc=B(-.25, 26.75, 1.86), bevel=0)
    lamp = a.part('Lamps', 'Lamp')
    lamp_post(steel, lamp, -2.0, 8)
    lamp_post(steel, lamp, -2.0, 27)


# ============================================================================= outer corners
def outer_land(a):
    """The rectangle's corner with land on both sides: a boundary cairn, the stubs of a dry-stone wall, a copse and
    a few boulders in the corner square (22 x 22 m)."""
    stone = a.part('Stone', 'Rock', flat=True)
    rocks(stone, ((3, 3, .4, (.9, .9, .9)), (3.2, 3.1, 1.3, (.6, .55, .5)), (3.0, 3.0, 1.9, (.4, .35, .35)),
                  (7, 1.5, .2, (1.1, .9, .6)), (1.5, 7.5, .2, (1.0, .9, .6)), (14, 3.5, .1, (1.3, 1.0, .7))), sub=0)
    for i in range(6):
        stone.box((2.2, .9, .8), loc=B(6 + i * 2.3, -1.0, .35), rot=(0, 0, .05 * (i % 3 - 1)), bevel=0)
        stone.box((.9, 2.2, .8), loc=B(-1.0, 6 + i * 2.3, .35), rot=(0, 0, .05 * (i % 2)), bevel=0)
    trunk, crown = a.part('Trunks', 'Bark'), a.part('Crowns', 'Foliage', flat=True)
    for i, (x, z, h) in enumerate(((12, 12, 7.5), (16.5, 8.5, 6.2), (9, 17, 6.8), (17, 16, 8.0))):
        tree(trunk, crown, x, z, h, seed=i * 1.7)


def outer_urban(a):
    """The rectangle's corner on a city map: a paved street corner with kerbs, a newsstand, lamps, bollards, a
    planter tree and zebra stripes on the two streets running out (18 x 18 m)."""
    pave = a.part('Paving', 'Concrete')
    pave.box((14, 14, .16), loc=B(9, 9, .08), bevel=0)
    pave.box((14.4, .35, .22), loc=B(9, 1.9, .11), bevel=0)
    pave.box((.35, 14.4, .22), loc=B(1.9, 9, .11), bevel=0)
    paint = a.part('Stripes', 'PlasterWhite')
    for i in range(5):
        paint.box((.55, 3.0, .03), loc=B(4 + i * 1.1, -2.2, .02), bevel=0)
        paint.box((3.0, .55, .03), loc=B(-2.2, 4 + i * 1.1, .02), bevel=0)
    steel, lamp = a.part('Steel', 'Steel'), a.part('Lamps', 'Lamp')
    lamp_post(steel, lamp, 3, 3, 6.5)
    lamp_post(steel, lamp, 14, 3, 6.5)
    for i in range(5):
        steel.cyl(.12, .8, loc=B(3 + i * 1.4, 6.5, .55), seg=5, bevel=0)
    kiosk = a.part('Kiosk', 'PlasterBlue')
    kiosk.box((2.6, 1.8, 2.3), loc=B(10, 8, 1.3), bevel=0)
    a.part('Awning', 'WoodRed').box((3.2, 2.4, .15), loc=B(10, 8, 2.55), bevel=0)
    a.part('Planter', 'Concrete').box((2.2, 2.2, .7), loc=B(6, 13, .5), bevel=0)
    tree(a.part('Trunk', 'Bark'), a.part('Crown', 'Foliage', flat=True), 6, 13, 5.5, seed=3.3)


def outer_cliff(a):
    """The rectangle's corner where cliffs meet: a faceted rock bluff filling the corner square (10 m), scree at its
    foot and a dead tree on top (26 x 26 m)."""
    def h(x, z):
        d = min(x, z)
        return max(0.0, 10.5 * smooth(-2, 9, d) * (.8 + .2 * math.sin(x * .3) * math.cos(z * .25)))
    patch(a.part('Bluff', 'Rock', flat=True), -4, 24, -4, 24, 9, 9, h)
    rocks(a.part('Scree', 'Rock', flat=True), ((1, 6, .2, (1.1, 1.0, .7)), (6, 1, .2, (1.2, 1.0, .7)),
                                               (-1.5, 12, .1, (.8, .7, .5)), (12, -1.5, .1, (.9, .8, .5))), sub=0)
    a.part('Snag', 'BarkWhite').limb(B(14, 14, 10), B(14.4, 14.2, 15), .3, .3, bevel=0)


def outer_river(a):
    """The rectangle's corner between two river stretches (a reservoir): a concrete revetment round the corner, a
    gauge post, a small valve house and reeds (20 x 20 m)."""
    conc = a.part('Revetment', 'Concrete')
    for i in range(7):
        ang = i / 6 * R90
        x, z = 4 + 6 * math.cos(ang), 4 + 6 * math.sin(ang)
        conc.box((3.2, 1.6, 1.4), loc=B(x, z, -.3), rot=(0, 0, -ang), bevel=0)
    conc.box((3, 3, .3), loc=B(3, 3, .15), bevel=0)
    house = a.part('House', 'Brick')
    house.box((3.2, 2.6, 2.6), loc=B(12, 12, 1.3), bevel=0)
    a.part('Roof', 'RoofSlate').prism([(-1.6, 2.6), (1.6, 2.6), (0, 3.6)], 3.6, loc=B(12, 12), axis='Y', bevel=0)
    steel = a.part('Gauge', 'SafetyStripe')
    steel.box((.25, .25, 3.2), loc=B(9.5, 3.0, .8), bevel=0)
    rd = a.part('Reeds', 'FoliageLight')
    reeds(rd, 9, 8, 7, 3)
    reeds(rd, 7, 14, 6, 4)


def outer_sea(a):
    """The rectangle's corner out at sea: a reef of dark rock stacks with breaking surf round them and a red channel
    light on the outermost (22 x 22 m)."""
    rocks(a.part('Reef', 'Rock', flat=True), ((7, 7, .5, (2.6, 2.2, 3.2)), (10, 5, -.2, (1.6, 1.4, 1.8)),
                                              (5, 11, -.3, (1.5, 1.3, 1.2)), (13, 10, -.4, (1.0, 1.0, .8))))
    sf = a.part('Surf', 'PlasterWhite')
    for i in range(9):
        ang = i / 9 * math.tau
        sf.ico((1.6, .5, .06), loc=B(8 + 5.2 * math.cos(ang), 8 + 5.2 * math.sin(ang), .02), rot=(0, 0, ang + R90),
               sub=0, jitter=.15, seed=i)
    light = a.part('Light', 'ContainerRed')
    k.lathe(light, [(.9, -.5), (.9, 3.5), (.55, 4.2), (.55, 6.0), (.01, 6.4)], loc=B(15, 15), seg=8)
    a.part('Band', 'PlasterWhite').cyl(.92, .6, loc=B(15, 15, 2.2), seg=8, bevel=0)
    a.part('Lantern', 'Lamp').cyl(.4, .5, loc=B(15, 15, 5.6), seg=6, bevel=0)


def outer_land_sea(a):
    """A harbour's sea side meeting a land side at the corner: the quay's last block (its wall facing the sea beyond
    the +Z side), fenders, bollards and a harbour light on the corner (24 x 14 m)."""
    conc = a.part('Quay', 'Concrete')
    conc.box((26, 12, 2.2), loc=B(11, -6, -.7), bevel=0)
    conc.box((26, .5, .25), loc=B(11, -.25, .52), bevel=0)
    rub = a.part('Fenders', 'Rubber')
    for x in (2, 8, 14, 20):
        rub.box((1.2, .35, 1.4), loc=B(x, .18, -.2), bevel=0)
    steel = a.part('Bollards', 'Steel')
    for x in (5, 11, 17, 23):
        steel.cyl(.25, .6, loc=B(x, -1.0, .7), seg=6, r2=.32, bevel=0)
    tower = a.part('Light', 'PlasterWhite')
    k.lathe(tower, [(1.0, .3), (.8, 6.5), (.6, 6.8), (.6, 7.8), (.01, 8.2)], loc=B(3, -3), seg=8)
    a.part('Top', 'ContainerRed').cyl(.82, .8, loc=B(3, -3, 6.0), seg=8, bevel=0)
    a.part('Lantern', 'Lamp').cyl(.45, .6, loc=B(3, -3, 7.3), seg=6, bevel=0)


# ============================================================================= sea
def sea_whitecap(a):
    """Three wind-blown whitecaps (6 m across), riding just above the sea plane."""
    sf = a.part('Foam', 'PlasterWhite')
    for i, (x, z, r) in enumerate(((0, 0, 1.4), (2.4, 1.6, .9), (-1.8, 2.2, 1.0))):
        sf.ico((r, r * .3, .05), loc=B(x, z, .03), rot=(0, 0, .3 * i), sub=0, jitter=.2, seed=i * 1.9)


def sea_surf(a):
    """A broken surf line 12 m long (along local Z), for a beach meeting the sea beyond the map."""
    foam(a.part('Surf', 'PlasterWhite'), 0, -6, 12, 23, width=.9)
    foam(a.part('Surf', 'PlasterWhite'), 1.8, -5, 10, 31, width=.5)


def sea_ship_far(a):
    """A far cargo ship silhouette (72 m along local Z): hull, container rows, the bridge aft and its funnel."""
    hull = a.part('Hull', 'ContainerBlue')
    hull.prism([(-6, 0), (6, 0), (5, -4), (-5, -4)], 64, loc=B(0, -4, 3.5), axis='Y', bevel=0)
    hull.prism([(-6, 0), (6, 0), (0, -4)], 8, loc=B(0, 32, 3.5), axis='Y', bevel=0, taper=.2)
    cargo = a.part('Boxes', 'ContainerRed')
    for i in range(5):
        cargo.box((10.5, 9, 2.6 + (i % 2) * 2.6), loc=B(0, 22 - i * 10.5, 4.8 + (i % 2) * 1.3), bevel=0)
    bridge = a.part('Bridge', 'PlasterWhite')
    bridge.box((11, 6, 8), loc=B(0, -31, 7.5), bevel=0)
    a.part('Funnel', 'BarrelRed').box((3, 3, 5), loc=B(0, -35, 12), bevel=0)


def sea_tanker_far(a):
    """A far tanker silhouette (80 m along local Z): a long low hull, the deck's pipe run and the castle aft."""
    hull = a.part('Hull', 'Steel')
    hull.prism([(-7, 0), (7, 0), (6, -4.5), (-6, -4.5)], 70, loc=B(0, -2, 3.0), axis='Y', bevel=0)
    hull.prism([(-7, 0), (7, 0), (0, -4.5)], 10, loc=B(0, 38, 3.0), axis='Y', bevel=0, taper=.2)
    a.part('Deck', 'BarrelRed').box((12, 62, .6), loc=B(0, 1, 3.3), bevel=0)
    a.part('Pipes', 'Pipe').box((1.2, 50, 1.0), loc=B(0, 6, 4.1), bevel=0)
    castle = a.part('Castle', 'PlasterWhite')
    castle.box((12, 8, 9), loc=B(0, -32, 7.5), bevel=0)
    castle.box((3, 3, 4), loc=B(0, -35, 13), bevel=0)


def sea_island_haze(a):
    """A low far island for the sea horizon (120 x 50 m, 9 m): rock shoulders and a dark wooded crown; the fog makes
    it faint at that distance."""
    a.part('Rock', 'Rock', flat=True).ico((60, 24, 6), loc=B(0, 0, -1.5), sub=2, jitter=.25, seed=7.7)
    a.part('Woods', 'FoliageDark', flat=True).ico((38, 15, 6), loc=B(-8, 2, 3.0), sub=1, jitter=.3, seed=4.4)


def sea_stack(a):
    """A sea stack and its fallen blocks for a cliff shore (to 7 m), surf round its foot."""
    rocks(a.part('Stack', 'Rock', flat=True), ((0, 0, 2.2, (2.0, 1.7, 3.6)), (2.6, 1.2, .1, (1.2, 1.0, 1.0)),
                                               (-2.0, 1.8, -.1, (1.0, .9, .8))))
    sf = a.part('Surf', 'PlasterWhite')
    for i in range(6):
        ang = i / 6 * math.tau
        sf.ico((1.3, .4, .05), loc=B(3.0 * math.cos(ang), 3.0 * math.sin(ang), .02), rot=(0, 0, ang + R90), sub=0,
               jitter=.15, seed=i + 2)


# ============================================================================= edge-type dressing
def edge_quay(a):
    """A 12 m quay wall segment (along local X): its face at z = 0 towards the sea (+Z), the quay top behind, a
    bollard and two fenders. Laid end to end along a harbour's coast beyond the map."""
    conc = a.part('Quay', 'Concrete')
    conc.box((12, 8, 2.2), loc=B(0, -4, -.7), bevel=0)
    conc.box((12, .45, .22), loc=B(0, -.22, .51), bevel=0)
    rub = a.part('Fenders', 'Rubber')
    for x in (-3, 3):
        rub.box((1.1, .3, 1.3), loc=B(x, .15, -.2), bevel=0)
    a.part('Bollard', 'Steel').cyl(.25, .6, loc=B(0, -1.0, .7), seg=6, r2=.32, bevel=0)


def edge_crane_far(a):
    """A far gantry crane silhouette on a quay (30 m high): four legs, the portal beam, the boom over the water and
    the cab."""
    y = a.part('Frame', 'CraneYellow')
    for x in (-5, 5):
        for z in (-4, 4):
            y.limb(B(x, z, 0), B(x * .8, z * .8, 22), .7, .7, bevel=0)
    y.box((11, 1.2, 2.0), loc=B(0, -4, 22), bevel=0)
    y.box((11, 1.2, 2.0), loc=B(0, 4, 22), bevel=0)
    y.box((2.0, 44, 1.8), loc=B(0, 10, 25), bevel=0)
    y.limb(B(0, -4, 24), B(0, 0, 31), .6, .6, bevel=0)
    a.part('Cab', 'PlasterWhite').box((3, 3, 2.4), loc=B(0, 6, 22.6), bevel=0)


def edge_containers(a):
    """A stack of six shipping containers, two high (12 x 5 m)."""
    red, blue = a.part('Red', 'ContainerRed'), a.part('Blue', 'ContainerBlue')
    for i, (x, z, y) in enumerate(((0, -1.25, 1.3), (0, 1.25, 1.3), (0, -1.25, 3.9), (.3, 1.25, 3.9),
                                   (0, 3.75, 1.3), (-.4, -3.75, 1.3))):
        (red if i % 2 else blue).box((12, 2.4, 2.5), loc=B(x, z, y), bevel=0)


def edge_chimney(a):
    """An industrial chimney (34 m) with red and white bands over a low boiler house, readable from the far ring."""
    stack = a.part('Stack', 'Concrete')
    k.lathe(stack, [(2.4, 0), (1.6, 34), (1.7, 34.4), (.01, 34.4)], loc=B(0, 0), seg=10)
    bands = a.part('Bands', 'BarrelRed')
    for y in (26, 31):
        bands.cyl(1.82 - (y - 26) * .02, 2.2, loc=B(0, 0, y), seg=10, r2=1.72 - (y - 26) * .02, bevel=0)
    a.part('House', 'Corrugated').box((10, 8, 6), loc=B(6, 0, 3), bevel=0)


def edge_tanks(a):
    """Two storage tanks (14 m across, 9 m) with a pipe between them."""
    steel = a.part('Tanks', 'Steel')
    for x in (-8, 8):
        k.lathe(steel, [(7, 0), (7, 9), (5, 10.2), (.01, 10.6)], loc=B(x, 0), seg=12)
    a.part('Pipe', 'Pipe').cyl(.5, 4, loc=B(0, 0, 1.2), rot=(0, R90, 0), seg=6, bevel=0)
    a.part('Stairs', 'SafetyStripe').limb(B(-1.3, -6, 0), B(-1.3, -2, 9), .8, .4, bevel=0)


def edge_scree(a):
    """A scree fan at a cliff's foot (8 m): five angular blocks."""
    rocks(a.part('Scree', 'Rock', flat=True), ((0, 0, .5, (1.6, 1.3, 1.0)), (2.2, .8, .3, (1.0, .9, .6)),
                                               (-2.0, 1.2, .3, (1.1, .9, .6)), (.8, 2.6, .2, (.8, .7, .5)),
                                               (-1, -2, .2, (.9, .8, .5))), sub=0, jitter=.3)


def edge_rail_track(a):
    """A 6 m section of railway along local Z: the ballast bed, ten sleepers and the two rails (1.435 m gauge). The
    view lays it along every RailSpline, in the play area and out to the tunnel portal."""
    a.part('Ballast', 'Rock', flat=True).prism([(-1.9, 0), (1.9, 0), (1.3, .3), (-1.3, .3)], 6.0, loc=B(0, 0, -.02),
                                               axis='Y', bevel=0)
    wood = a.part('Sleepers', 'LogWood')
    for i in range(10):
        wood.box((2.6, .26, .14), loc=B(0, -2.7 + i * .6, .34), bevel=0)
    steel = a.part('Rails', 'Steel')
    for x in (-.72, .72):
        steel.box((.08, 6.02, .14), loc=B(x, 0, .48), bevel=0)


def edge_tunnel_portal(a):
    """A concrete tunnel portal at a RailSpline's far end (the track runs into it along local +Z): two piers, the
    lintel and wing walls, the dark bore, and the rocky hill it is cut into (24 x 20 m)."""
    conc = a.part('Portal', 'Concrete')
    conc.box((1.8, 2.0, 7.5), loc=B(-3.6, 0, 3.75), bevel=0)
    conc.box((1.8, 2.0, 7.5), loc=B(3.6, 0, 3.75), bevel=0)
    conc.box((9.0, 2.0, 1.8), loc=B(0, 0, 8.1), bevel=0)
    conc.box((5.0, .9, 5.0), loc=B(-6.8, -1.6, 2.5), rot=(0, 0, .5), bevel=0)
    conc.box((5.0, .9, 5.0), loc=B(6.8, -1.6, 2.5), rot=(0, 0, -.5), bevel=0)
    a.part('Bore', 'EliteBlack').box((5.6, 1.0, 7.1), loc=B(0, .6, 3.55), bevel=0)
    a.part('Hill', 'Rock', flat=True).ico((13, 10, 11), loc=B(0, 9, 1.0), sub=2, jitter=.2, seed=5.5)


def _gen(fn, ao=.8, dist=.8):
    def run(a):
        fn(a)
        k.clean(a)
    return run, dict(ao_distance=dist, grime_height=.3, ao_strength=ao)


BUILDERS = {
    # The ten corner pieces (Tools/maps/edges.py PIECE / corners()).
    'dress_edge_outer_land': _gen(outer_land),
    'dress_edge_corner_land_cliff': _gen(corner_land_cliff, .6, 2.0),
    'dress_edge_outer_urban': _gen(outer_urban),
    'dress_edge_bank_land_river': _gen(bank_land_river, .6, 1.5),
    'dress_edge_corner_land_sea': _gen(corner_land_sea, .6, 1.5),
    'dress_edge_outer_sea': _gen(outer_sea),
    'dress_edge_embankment_urban_river': _gen(embankment_urban_river),
    'dress_edge_outer_land_sea': _gen(outer_land_sea),
    'dress_edge_outer_cliff': _gen(outer_cliff, .6, 2.0),
    'dress_edge_outer_river': _gen(outer_river),
    # The sea side.
    'dress_sea_whitecap': _gen(sea_whitecap, .3),
    'dress_sea_surf': _gen(sea_surf, .3),
    'dress_sea_ship_far': _gen(sea_ship_far, .5, 2.0),
    'dress_sea_tanker_far': _gen(sea_tanker_far, .5, 2.0),
    'dress_sea_island_haze': _gen(sea_island_haze, .4, 3.0),
    'dress_sea_stack': _gen(sea_stack, .7, 1.2),
    # Edge types and modifiers beyond the map, and the rails' continuation.
    'dress_edge_quay': _gen(edge_quay),
    'dress_edge_crane_far': _gen(edge_crane_far, .5, 2.0),
    'dress_edge_containers': _gen(edge_containers),
    'dress_edge_chimney': _gen(edge_chimney, .5, 2.0),
    'dress_edge_tanks': _gen(edge_tanks, .6, 2.0),
    'dress_edge_scree': _gen(edge_scree),
    'dress_edge_rail_track': _gen(edge_rail_track, .6, .5),
    'dress_edge_tunnel_portal': _gen(edge_tunnel_portal, .7, 1.5),
}
