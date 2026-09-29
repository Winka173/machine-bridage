"""Machine Brigade prompt 16 models: Kessler's Leviathan, its fleet and Lighthouse Bay's coast props.

  * leviathan: a battleship-and-missile-cruiser hybrid, 64 x 11 m, the biggest model in the game (its LOD is
    ModelLibrary.Lod's, automatic). A long flared hull with a raised forecastle and a sheer to the bow, a
    grey deck, two twin 203 mm turrets fore and aft, a block of vertical launch cells before the bridge, a
    stepped superstructure with the bridge, phased-array panels, a lattice mast with a spinning search radar,
    a raked funnel, two six-barrel CIWS, a hangar and a helicopter deck aft and a well-deck gate in the transom.
  * sea_corvette: a 30 m escort corvette: a 76 mm gun forward, a CIWS aft on the hangar, a mast.
  * missile_boat: a 14 m fast attack boat on a planing hull: a low cabin, two rocket pods amidships, a
    heavy machine gun on the cabin roof. (The hovercraft's escort shares it, prompt 16 E.)
  * landing_craft: a 17 m landing craft (LCM lineage): a bow ramp, an open well for two tanks, a wheelhouse aft.
  * lighthouse, pier, fishing_boat: the coast's props.

Boss parts (see mb_phase8's notes): each part is an empty `Part_<kind>` holding its meshes and pivots, its
origin where a wreck piece belongs: Leviathan's `Part_gun` / `Part_gun.001` (turrets, on `Mount_gun` /
`Mount_gun.001`, `Muzzle_gun*` between the barrels' tips), `Part_mg` / `Part_mg.001` (CIWS), `Part_vls`,
`Part_radar` (with the spinning `Radar`), `Part_deck`, `Part_welldeck`, `Part_engine` (the funnel). The
corvette's `Part_gun` and `Part_mg`.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front and +X the vehicle's left.
A ship's origin is at the waterline under its middle (z 0 is the water: the hull below it is hidden there);
data positions (x right, y forward) are Blender (-x, -y). Every bore points along -Y at rest.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from mb_phase2 import _suffixed, dotted  # noqa: E402
from mb_phase8 import ciws, pv  # noqa: E402
from mb_vehicles import FORWARD, R90  # noqa: E402


def _hull(part, sections, keel=-2.0, bevel=0.0):
    """A ship's hull lofted through sections (y, half beam, deck height), bow first: flared sides, a round
    bilge, a flat keel below the waterline; the deck is its top face."""
    rings = []
    for y, hw, zd in sections:
        rings.append([(hw, y, zd), (hw * 0.97, y, 0.6), (hw * 0.78, y, keel * 0.6), (hw * 0.3, y, keel),
                      (-hw * 0.3, y, keel), (-hw * 0.78, y, keel * 0.6), (-hw * 0.97, y, 0.6), (-hw, y, zd)])
    part.loft(rings, bevel=bevel)


def _twin_turret(a, mount, part_name, loc, size=(4.6, 5.6, 2.2), barrel=9.0, bore=0.23, material='Team'):
    """A twin gun turret on its own yaw pivot under its Part_ empty at loc (on the deck): the gunhouse, two
    barrels in their blast bags and the muzzle empty between their tips."""
    pk = pv(a, part_name, loc)
    key = dotted(mount)
    m = a.pivot(key, (0, 0, 0), pk)
    tag = mount[6:].replace('.', '_')
    w, d, h = size
    a.part(f'Barbette_{tag}', 'Armor', pk).cyl(w * 0.62, 0.5, loc=(0, 0, 0.25), seg=20, bevel=0.03, bseg=1)
    a.part(f'Gunhouse_{tag}', material, m).box((w, d, h), loc=(0, 0.2, 0.5 + h / 2), bevel=0.12, seg=1, taper=(0.86, 0.8), shift=(0, 0.25))
    a.part(f'Gunhouse_roof_{tag}', 'Armor', m).box((w * 0.7, d * 0.55, 0.18), loc=(0, 0.6, 0.5 + h + 0.08), bevel=0.04, seg=1)
    steel = a.part(f'Barrels_{tag}', 'Steel', m)
    bags = a.part(f'Blast_bags_{tag}', 'Canvas', m)
    zb = 0.5 + h * 0.5
    y0 = -d / 2 + 0.2
    for s in (-1, 1):
        x = s * w * 0.22
        bags.cyl(bore * 2.1, 0.9, loc=(x, y0 - 0.35, zb), rot=FORWARD, seg=10, bevel=0.03, bseg=1)
        steel.cyl(bore * 1.35, barrel * 0.45, loc=(x, y0 - 0.8 - barrel * 0.225, zb), rot=FORWARD, seg=10, bevel=0.02, bseg=1)
        steel.cyl(bore, barrel * 0.55, loc=(x, y0 - 0.8 - barrel * 0.45 - barrel * 0.275, zb), rot=FORWARD, seg=10, bevel=0.01, bseg=1)
        a.part(f'Bores_{tag}', 'Charred', m).cyl(bore * 0.6, 0.02, loc=(x, y0 - 0.81 - barrel, zb), rot=FORWARD, seg=8, bevel=0)
    a.pivot(dotted(mount.replace('Mount_', 'Muzzle_')), (0, y0 - 0.8 - barrel, zb), m)
    return pk


def leviathan(a):
    """Kessler's Leviathan (see the module docstring for the parts and the rig)."""
    _suffixed(a)
    hull = a.part('Hull', 'Armor')
    # Bow (-Y) to stern: a sharp raked stem, a raised forecastle with sheer, flat sides, a square transom.
    _hull(hull, [(-32.0, 0.3, 5.0), (-30.0, 1.6, 4.8), (-26.0, 3.4, 4.5), (-20.0, 4.8, 4.2), (-12.0, 5.4, 3.9),
                 (0.0, 5.5, 3.4), (14.0, 5.5, 3.3), (24.0, 5.3, 3.3), (30.0, 5.0, 3.3), (32.0, 4.7, 3.3)], keel=-2.4)
    # The boot-top band at the waterline in the side's colour, a rub strake, the deck edge.
    band = a.part('Boot_top', 'Team')
    for s in (-1, 1):
        band.box((0.08, 50.0, 0.5), loc=(s * 5.52, 4.0, 0.35), bevel=0, seg=1)
        a.part('Deck_edge', 'Steel').box((0.1, 56.0, 0.12), loc=(s * 5.45, 2.0, 3.36), bevel=0, seg=1)
    deck = a.part('Deck', 'Asphalt')
    deck.box((10.2, 40.0, 0.06), loc=(0, 6.0, 3.34), bevel=0, seg=1)
    deck.box((8.0, 12.0, 0.06), loc=(0, -18.5, 3.95), rot=(0.02, 0, 0), bevel=0, seg=1)
    # Anchors, hawse pipes, a jack staff, bollards along the forecastle.
    steel = a.part('Fittings', 'Steel')
    for s in (-1, 1):
        steel.box((0.5, 0.9, 0.9), loc=(s * 2.6, -27.0, 3.7), bevel=0.08, seg=1)
        for y in (-22.0, -8.0, 12.0, 26.0):
            steel.cyl(0.18, 0.5, loc=(s * 4.6, y, 3.6), seg=8, bevel=0)
    steel.cyl(0.06, 3.0, loc=(0, -31.2, 6.4), seg=6, bevel=0)

    # Turrets: 203 mm twins, fore (superfiring over the launch cells) and aft.
    _twin_turret(a, 'Mount_gun', 'Part_gun', (0, -19.0, 4.1))
    _twin_turret(a, 'Mount_gun.001', 'Part_gun.001', (0, 16.0, 3.4))

    # The launch cells before the bridge: a raised block of hatches.
    pvls = pv(a, 'Part_vls', (0, -11.5, 3.4))
    a.part('Vls_block', 'Armor', pvls).box((6.2, 4.4, 0.8), loc=(0, 0, 0.4), bevel=0.06, seg=1)
    hatch = a.part('Vls_hatches', 'Undercarriage', pvls)
    for i in range(4):
        for j in range(3):
            hatch.box((1.2, 1.1, 0.06), loc=(-2.2 + i * 1.47, -1.3 + j * 1.3, 0.83), bevel=0.02, seg=1)

    # The superstructure: two stepped blocks, the bridge with its windows and wings, phased-array panels.
    sup = a.part('Superstructure', 'Team')
    sup.box((8.4, 14.0, 3.0), loc=(0, -1.0, 4.9), bevel=0.1, seg=1, taper=(0.96, 0.97))
    sup.box((6.8, 9.0, 2.8), loc=(0, -2.5, 7.8), bevel=0.1, seg=1, taper=(0.93, 0.95))
    sup.box((5.0, 4.6, 2.2), loc=(0, -4.5, 10.3), bevel=0.08, seg=1, taper=(0.9, 0.9))
    glass = a.part('Bridge_glass', 'Glass')
    glass.box((4.6, 0.08, 0.7), loc=(0, -6.83, 10.6), rot=(0.18, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((0.08, 3.6, 0.6), loc=(s * 2.52, -4.5, 10.6), bevel=0)
        a.part('Bridge_wing', 'Armor').box((1.6, 1.4, 0.16), loc=(s * 4.0, -6.2, 9.4), bevel=0.03, seg=1)
    panels = a.part('Radar_panels', 'Undercarriage')
    for s in (-1, 1):
        panels.box((0.12, 2.6, 2.6), loc=(s * 3.42, -5.2, 7.9), rot=(0, s * 0.12, 0), bevel=0.02, seg=1)
        panels.box((0.12, 2.6, 2.6), loc=(s * 3.42, 1.6, 7.9), rot=(0, s * 0.12, 0), bevel=0.02, seg=1)
    # The CIWS: forward on the bridge's starboard shoulder, aft on the hangar's port side.
    pv(a, 'Part_mg', (-3.0, -6.0, 9.2))
    ciws(a, 'Mount_mg', (0, 0, 0), parent='Part_mg')
    pv(a, 'Part_mg.001', (3.0, 8.5, 8.2))
    ciws(a, 'Mount_mg.001', (0, 0, 0), parent='Part_mg.001')

    # The mast and its search radar (Part_radar at its top; the Radar bar spins).
    mast = a.part('Mast', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            mast.limb((sx * 1.1, -1.5 + sy * 1.1, 11.4), (sx * 0.35, -1.5 + sy * 0.35, 16.6), 0.14, 0.14, bevel=0)
    mast.box((1.2, 1.2, 0.1), loc=(0, -1.5, 14.0), bevel=0)
    prad = pv(a, 'Part_radar', (0, -1.5, 16.6))
    a.part('Radar_base', 'Armor', prad).cyl(0.5, 0.5, loc=(0, 0, 0.25), seg=12, bevel=0.03, bseg=1)
    rad = a.pivot('Radar', (0, 0, 0.6), prad)
    a.part('Radar_bar', 'Medical', rad).box((4.2, 0.35, 0.9), loc=(0, 0, 0.45), bevel=0.05, seg=1)
    a.part('Mast_lamp', 'Lamp', prad).sphere(0.12, loc=(0, 0, 1.6), seg=8, rings=4)

    # The funnel (the engine room below it is the part): raked, with its cap.
    peng = pv(a, 'Part_engine', (0, 2.5, 8.0))
    fun = a.part('Funnel', 'Armor', peng)
    fun.box((3.0, 4.2, 5.0), loc=(0, 0.4, 2.5), rot=(-0.12, 0, 0), bevel=0.3, seg=2, taper=(0.85, 0.8))
    a.part('Funnel_cap', 'Charred', peng).box((2.4, 3.0, 0.4), loc=(0, 0.8, 5.1), rot=(-0.12, 0, 0), bevel=0.1, seg=1)
    a.part('Funnel_band', 'Team', peng).box((3.05, 4.0, 0.5), loc=(0, 0.6, 3.8), rot=(-0.12, 0, 0), bevel=0.05, seg=1)

    # The hangar and the helicopter deck aft (Part_deck), the well-deck gate in the transom (Part_welldeck).
    a.part('Hangar', 'Team').box((8.0, 7.0, 3.6), loc=(0, 10.0, 5.1), bevel=0.1, seg=1)
    a.part('Hangar_door', 'Undercarriage').box((5.4, 0.08, 3.0), loc=(0, 13.53, 5.0), bevel=0)
    pdeck = pv(a, 'Part_deck', (0, 24.5, 3.36))
    pad = a.part('Flight_deck', 'Asphalt', pdeck)
    pad.box((10.0, 11.0, 0.08), loc=(0, 0, 0.04), bevel=0, seg=1)
    mark = a.part('Deck_marks', 'SafetyStripe', pdeck)
    for k in range(16):
        u = k * math.tau / 16
        mark.box((0.35, 1.1, 0.02), loc=(math.cos(u) * 3.2, math.sin(u) * 3.2, 0.09), rot=(0, 0, u + R90), bevel=0)
    mark.box((0.3, 3.0, 0.02), loc=(0, 0, 0.09), bevel=0)
    a.part('Deck_lights', 'Lamp', pdeck).box((9.6, 0.1, 0.05), loc=(0, 5.45, 0.1), bevel=0)
    pwell = pv(a, 'Part_welldeck', (0, 30.5, 2.0))
    a.part('Stern_gate', 'Armor', pwell).box((6.4, 0.4, 2.6), loc=(0, 1.55, 0.0), bevel=0.05, seg=1)
    a.part('Gate_edges', 'Hazard', pwell).box((6.5, 0.1, 0.2), loc=(0, 1.8, 1.2), bevel=0)
    for s in (-1, 1):
        a.part('Gate_rails', 'Steel', pwell).box((0.2, 0.3, 2.8), loc=(s * 3.3, 1.5, 0.0), bevel=0)
    # Navigation lights and the ensign staff.
    a.part('Nav_green', 'SignalGreen').box((0.2, 0.3, 0.2), loc=(-4.2, -6.0, 9.2), bevel=0)
    a.part('Nav_red', 'LavaGlow').box((0.2, 0.3, 0.2), loc=(4.2, -6.0, 9.2), bevel=0)
    steel.cyl(0.06, 2.4, loc=(0, 31.6, 4.5), seg=6, bevel=0)


def sea_corvette(a):
    """An escort corvette, 30 x 5.6 m: a 76 mm gun forward (Part_gun, Mount_gun, Muzzle_gun), a CIWS on the
    hangar aft (Part_mg), a stepped superstructure, a mast with a radar."""
    _suffixed(a)
    _hull(a.part('Hull', 'Armor'), [(-15.0, 0.2, 3.0), (-13.5, 1.2, 2.9), (-10.0, 2.4, 2.6), (-4.0, 2.8, 2.4),
                                    (6.0, 2.8, 2.3), (13.0, 2.6, 2.3), (15.0, 2.4, 2.3)], keel=-1.4)
    for s in (-1, 1):
        a.part('Boot_top', 'Team').box((0.06, 24.0, 0.35), loc=(s * 2.8, 1.0, 0.25), bevel=0, seg=1)
    a.part('Deck', 'Asphalt').box((5.0, 26.0, 0.05), loc=(0, 1.0, 2.35), bevel=0, seg=1)
    pg = pv(a, 'Part_gun', (0, -9.0, 2.6))
    m = a.pivot('Mount_gun', (0, 0, 0), pg)
    a.part('Gun_house', 'Team', m).box((1.9, 2.4, 1.2), loc=(0, 0.1, 0.7), bevel=0.25, seg=2, taper=(0.8, 0.75))
    a.part('Gun_barrel', 'Steel', m).cyl(0.09, 3.2, loc=(0, -2.6, 0.85), rot=FORWARD, seg=10, bevel=0.01, bseg=1)
    a.pivot('Muzzle_gun', (0, -4.2, 0.85), m)
    sup = a.part('Superstructure', 'Team')
    sup.box((4.4, 8.0, 2.2), loc=(0, -1.0, 3.5), bevel=0.08, seg=1, taper=(0.95, 0.95))
    sup.box((3.6, 4.0, 1.8), loc=(0, -2.5, 5.5), bevel=0.08, seg=1, taper=(0.9, 0.9))
    a.part('Bridge_glass', 'Glass').box((3.2, 0.06, 0.5), loc=(0, -4.52, 5.8), rot=(0.18, 0, 0), bevel=0)
    a.part('Hangar', 'Team').box((4.0, 5.0, 2.4), loc=(0, 6.5, 3.6), bevel=0.08, seg=1)
    pv(a, 'Part_mg', (0, 6.5, 4.85))
    ciws(a, 'Mount_mg', (0, 0, 0), parent='Part_mg')
    mast = a.part('Mast', 'Steel')
    mast.cyl(0.14, 4.0, loc=(0, -1.8, 8.4), seg=8, bevel=0)
    mast.box((1.8, 0.12, 0.12), loc=(0, -1.8, 9.2), bevel=0)
    rad = a.pivot('Radar', (0, -1.8, 10.4))
    a.part('Radar_bar', 'Medical', rad).box((2.0, 0.2, 0.45), loc=(0, 0, 0.2), bevel=0.03, seg=1)
    a.part('Funnel', 'Armor').box((1.4, 1.8, 1.8), loc=(0, 2.6, 5.4), rot=(-0.1, 0, 0), bevel=0.15, seg=1, taper=(0.8, 0.8))


def missile_boat(a):
    """A fast attack boat, 14 x 3.8 m, on a planing hull: rocket pods amidships (Mount_rocket, Muzzle_rocket),
    a heavy machine gun on the cabin roof (Mount_mg, Muzzle_mg)."""
    hull = a.part('Hull', 'Armor')
    rings = []
    for y, hw, zd in ((-7.0, 0.15, 1.5), (-6.0, 0.9, 1.45), (-4.0, 1.7, 1.35), (0.0, 1.9, 1.25), (4.0, 1.9, 1.2), (7.0, 1.8, 1.2)):
        rings.append([(hw, y, zd), (hw * 0.98, y, 0.3), (hw * 0.4, y, -0.5), (0.0, y, -0.7), (-hw * 0.4, y, -0.5), (-hw * 0.98, y, 0.3), (-hw, y, zd)])
    hull.loft(rings)
    for s in (-1, 1):
        a.part('Stripe', 'Team').box((0.05, 10.0, 0.22), loc=(s * 1.9, 0.5, 0.75), bevel=0, seg=1)
    a.part('Deck', 'Asphalt').box((3.4, 10.0, 0.04), loc=(0, 1.5, 1.24), bevel=0, seg=1)
    a.part('Cabin', 'Team').box((2.4, 3.6, 1.2), loc=(0, -1.2, 1.85), bevel=0.2, seg=2, taper=(0.85, 0.75), shift=(0, 0.3))
    a.part('Cabin_glass', 'Glass').box((2.0, 0.05, 0.4), loc=(0, -3.0, 2.05), rot=(0.5, 0, 0), bevel=0)
    m = a.pivot('Mount_rocket', (0, 2.6, 1.3))
    pods = a.part('Rocket_pods', 'Armor', m)
    for s in (-1, 1):
        pods.box((0.8, 2.4, 0.7), loc=(s * 0.8, 0, 0.55), rot=(0.18, 0, 0), bevel=0.06, seg=1)
        a.part('Pod_tubes', 'Charred', m).box((0.7, 0.04, 0.6), loc=(s * 0.8, -1.22, 0.78), rot=(0.18, 0, 0), bevel=0)
    a.pivot('Muzzle_rocket', (0, -1.3, 0.8), m)
    mg = a.pivot('Mount_mg', (0, -0.8, 2.45))
    a.part('Mg_body', 'Steel', mg).box((0.25, 0.9, 0.25), loc=(0, -0.2, 0.2), bevel=0.02, seg=1)
    a.part('Mg_barrel', 'Steel', mg).cyl(0.04, 0.8, loc=(0, -1.05, 0.22), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.45, 0.22), mg)
    a.part('Mast', 'Steel').cyl(0.05, 1.4, loc=(0, 0.2, 3.0), seg=6, bevel=0)


def landing_craft(a):
    """A landing craft, 17 x 7 m (LCM lineage): a bow ramp, an open well, a wheelhouse aft with a heavy machine
    gun on its roof (Mount_mg, Muzzle_mg)."""
    hull = a.part('Hull', 'Armor')
    hull.box((7.0, 16.0, 2.2), loc=(0, 0.5, 0.3), bevel=0.15, seg=1)
    well = a.part('Well', 'Undercarriage')
    well.box((5.6, 11.0, 0.05), loc=(0, -1.5, 1.42), bevel=0, seg=1)
    for s in (-1, 1):
        a.part('Wing_walls', 'Team').box((0.6, 12.0, 1.0), loc=(s * 3.2, -1.5, 1.9), bevel=0.05, seg=1)
    ramp = a.part('Ramp', 'Armor')
    ramp.box((5.8, 0.3, 2.4), loc=(0, -7.9, 1.8), rot=(-0.18, 0, 0), bevel=0.05, seg=1)
    a.part('Ramp_edges', 'Hazard').box((6.0, 0.1, 0.18), loc=(0, -8.2, 2.9), bevel=0)
    a.part('Wheelhouse', 'Team').box((3.2, 2.6, 2.2), loc=(0, 6.2, 2.5), bevel=0.1, seg=1)
    a.part('Wheelhouse_glass', 'Glass').box((2.6, 0.05, 0.5), loc=(0, 4.88, 3.0), bevel=0)
    mg = a.pivot('Mount_mg', (0, 6.2, 3.65))
    a.part('Mg_body', 'Steel', mg).box((0.25, 0.9, 0.25), loc=(0, -0.2, 0.2), bevel=0.02, seg=1)
    a.part('Mg_barrel', 'Steel', mg).cyl(0.045, 0.9, loc=(0, -1.1, 0.22), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.55, 0.22), mg)


def lighthouse(a):
    """Lighthouse Bay's lighthouse: an 18 m tapered tower in red and white bands on a stone base, a gallery
    and the lamp room's glass (lit), a small store beside it. Footprint 7.2 m."""
    a.part('Base', 'Concrete').cyl(3.4, 1.2, loc=(0, 0, 0.6), seg=16, bevel=0.1, bseg=1)
    tower = a.part('Tower', 'PlasterWhite')
    red = a.part('Bands', 'BarrelRed')
    z = 1.2
    for k in range(5):
        r0 = 2.3 - 0.24 * k
        r1 = r0 - 0.24
        (red if k % 2 else tower).cyl(r0, 3.2, r2=r1, loc=(0, 0, z + 1.6), seg=16, bevel=0)
        z += 3.2
    a.part('Gallery', 'Armor').cyl(1.7, 0.2, loc=(0, 0, z + 0.1), seg=16, bevel=0.02, bseg=1)
    a.part('Railing', 'Steel').cyl(1.65, 0.6, loc=(0, 0, z + 0.5), seg=16, bevel=0)
    a.part('Lamp_room', 'Lamp').cyl(0.95, 1.4, loc=(0, 0, z + 0.9), seg=12, bevel=0)
    a.part('Lamp_roof', 'BarrelRed').cyl(1.1, 0.9, r2=0.1, loc=(0, 0, z + 2.05), seg=12, bevel=0)
    a.part('Store', 'PlasterWhite').box((2.4, 2.0, 1.8), loc=(0, 2.4, 0.9), bevel=0.05, seg=1)
    a.part('Store_roof', 'RoofSlate').box((2.6, 2.2, 0.2), loc=(0, 2.4, 1.9), bevel=0.03, seg=1)


def pier(a):
    """A length of wooden pier on its piles (7.6 x 6 m), its deck a little above the water."""
    deck = a.part('Deck', 'Wood')
    for k in range(9):
        deck.box((7.6, 0.6, 0.12), loc=(0, -2.7 + k * 0.675, 0.42), bevel=0.02, seg=1)
    piles = a.part('Piles', 'LogWood')
    for x in (-3.4, 0.0, 3.4):
        for y in (-2.6, 2.6):
            piles.cyl(0.18, 1.4, loc=(x, y, -0.2), seg=8, bevel=0)
    a.part('Bollards', 'Steel').cyl(0.16, 0.4, loc=(3.5, 0, 0.66), seg=8, bevel=0)


def fishing_boat(a):
    """A fishing boat drawn up on the sand, 7.4 x 2.8 m: a clinker hull, a small wheelhouse, nets."""
    rings = []
    for y, hw, zd in ((-3.7, 0.1, 1.3), (-2.8, 0.9, 1.15), (-1.0, 1.35, 1.05), (1.5, 1.4, 1.05), (3.5, 1.1, 1.1)):
        rings.append([(hw, y, zd), (hw * 0.9, y, 0.45), (hw * 0.4, y, 0.12), (-hw * 0.4, y, 0.12), (-hw * 0.9, y, 0.45), (-hw, y, zd)])
    a.part('Hull', 'PlasterBlue').loft(rings)
    a.part('Gunwale', 'Wood').box((2.6, 6.0, 0.08), loc=(0, 0.3, 1.08), bevel=0, seg=1)
    a.part('Wheelhouse', 'PlasterWhite').box((1.4, 1.4, 1.2), loc=(0, 1.6, 1.7), bevel=0.05, seg=1)
    a.part('Nets', 'Canvas').box((1.8, 1.6, 0.35), loc=(0, -1.2, 1.25), bevel=0.15, seg=1)


BUILDERS = {
    'leviathan': (leviathan, dict(ao_distance=1.5, grime_height=1.0)),
    'sea_corvette': (sea_corvette, dict(ao_distance=1.0, grime_height=0.8)),
    'missile_boat': (missile_boat, dict(ao_distance=0.6, grime_height=0.5)),
    'landing_craft': (landing_craft, dict(ao_distance=0.8, grime_height=0.6)),
    'lighthouse': (lighthouse, dict(ao_distance=0.8, grime_height=0.6)),
    'pier': (pier, dict(ao_distance=0.4, grime_height=0.3)),
    'fishing_boat': (fishing_boat, dict(ao_distance=0.5, grime_height=0.4)),
}
