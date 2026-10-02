"""Machine Brigade prompt 16 models: Kessler's Leviathan, its fleet and Lighthouse Bay's coast props.

  * leviathan (DECISIONS 20Y): a battleship of the Yamato lineage, 86 x 14.4 m as built (96 x 16 m in the game),
    the biggest model in the game (its LOD is ModelLibrary.Lod's, automatic). A long flush deck with a strong
    sheer and flare at the bow, a wide beam, three triple 460 mm turrets (two forward, B superfiring, one aft),
    a pagoda tower with the bridge and a long rangefinder on its director, one raked funnel with launch cells
    beside it, two triple 155 mm secondaries, 25 mm tubs and twin 127 mm mounts along the sides, two CIWS,
    catapults, a floatplane and a crane over the aircraft deck aft, a stern gate for the landing craft, anchors
    and their chains on the forecastle. Hegemon's marks: chevrons in the side's colour on the bow, a crest on
    the stem, the side's colour on the turret roofs and the funnel band. Parts and pivots: see `leviathan`.
  * sea_cruiser: prompt 16's first Leviathan (a battleship-and-missile-cruiser hybrid, 64 x 11 m), kept as the
    fleet's missile cruiser and drawn at 0.72 by the data: two twin 203 mm turrets (`Mount_gun` / `.001`, the
    muzzles between the barrels), launch cells, a stepped superstructure, a lattice mast with a spinning radar,
    two CIWS (`Mount_mg` / `.001`), a hangar, a helicopter deck and a stern gate.
  * sea_corvette: a 30 m escort corvette: a 76 mm gun forward, a CIWS aft on the hangar, a mast.
  * missile_boat: a 14 m fast attack boat on a planing hull: a low cabin, two rocket pods amidships, a
    heavy machine gun on the cabin roof. (The hovercraft's escort shares it, prompt 16 E.)
  * landing_craft: a 17 m landing craft (LCM lineage): a bow ramp, an open well for two tanks, a wheelhouse aft.
  * lighthouse, pier, fishing_boat: the coast's props.

Boss parts (see mb_phase8's notes): each part is an empty `Part_<kind>` holding its meshes and pivots, its
origin where a wreck piece belongs. The corvette's `Part_gun` and `Part_mg`.

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


def _twin_turret(a, mount, part_name, loc, size=(4.6, 5.6, 2.2), barrel=9.0, bore=0.23, material='Team', spread=None):
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
        x = s * (spread if spread else w * 0.22)
        bags.cyl(bore * 2.1, 0.9, loc=(x, y0 - 0.35, zb), rot=FORWARD, seg=10, bevel=0.03, bseg=1)
        steel.cyl(bore * 1.35, barrel * 0.45, loc=(x, y0 - 0.8 - barrel * 0.225, zb), rot=FORWARD, seg=10, bevel=0.02, bseg=1)
        steel.cyl(bore, barrel * 0.55, loc=(x, y0 - 0.8 - barrel * 0.45 - barrel * 0.275, zb), rot=FORWARD, seg=10, bevel=0.01, bseg=1)
        a.part(f'Bores_{tag}', 'Charred', m).cyl(bore * 0.6, 0.02, loc=(x, y0 - 0.81 - barrel, zb), rot=FORWARD, seg=8, bevel=0)
    a.pivot(dotted(mount.replace('Mount_', 'Muzzle_')), (0, y0 - 0.8 - barrel, zb), m)
    return pk


def sea_cruiser(a):
    """The missile cruiser of Leviathan's fleet: prompt 16's first Leviathan, kept as it was built (64 x 11 m;
    the data draws it at 0.72, 46 x 8 m). Its turrets `Mount_gun` / `Mount_gun.001` (`Muzzle_gun*` between the
    barrels), its CIWS `Mount_mg` / `Mount_mg.001`; the other empties (Piece_vls, Piece_engine, Piece_deck, Piece_welldeck) are plain pieces: no def part uses them (DECISIONS 27 wave 2 pass B) and Part_radar only carries the Radar."""
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
    # DECISIONS 20Y: the barrels 1.1 m apart, so each gets a launch point of its own (ModelLibrary's twin rule).
    _twin_turret(a, 'Mount_gun', 'Part_gun', (0, -19.0, 4.1), spread=0.55)
    _twin_turret(a, 'Mount_gun.001', 'Part_gun.001', (0, 16.0, 3.4), spread=0.55)

    # The launch cells before the bridge: a raised block of hatches.
    pvls = pv(a, 'Piece_vls', (0, -11.5, 3.4))
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
    peng = pv(a, 'Piece_engine', (0, 2.5, 8.0))
    fun = a.part('Funnel', 'Armor', peng)
    fun.box((3.0, 4.2, 5.0), loc=(0, 0.4, 2.5), rot=(-0.12, 0, 0), bevel=0.3, seg=2, taper=(0.85, 0.8))
    a.part('Funnel_cap', 'Charred', peng).box((2.4, 3.0, 0.4), loc=(0, 0.8, 5.1), rot=(-0.12, 0, 0), bevel=0.1, seg=1)
    a.part('Funnel_band', 'Team', peng).box((3.05, 4.0, 0.5), loc=(0, 0.6, 3.8), rot=(-0.12, 0, 0), bevel=0.05, seg=1)

    # The hangar and the helicopter deck aft (Part_deck), the well-deck gate in the transom (Part_welldeck).
    a.part('Hangar', 'Team').box((8.0, 7.0, 3.6), loc=(0, 10.0, 5.1), bevel=0.1, seg=1)
    a.part('Hangar_door', 'Undercarriage').box((5.4, 0.08, 3.0), loc=(0, 13.53, 5.0), bevel=0)
    pdeck = pv(a, 'Piece_deck', (0, 24.5, 3.36))
    pad = a.part('Flight_deck', 'Asphalt', pdeck)
    pad.box((10.0, 11.0, 0.08), loc=(0, 0, 0.04), bevel=0, seg=1)
    mark = a.part('Deck_marks', 'SafetyStripe', pdeck)
    for k in range(16):
        u = k * math.tau / 16
        mark.box((0.35, 1.1, 0.02), loc=(math.cos(u) * 3.2, math.sin(u) * 3.2, 0.09), rot=(0, 0, u + R90), bevel=0)
    mark.box((0.3, 3.0, 0.02), loc=(0, 0, 0.09), bevel=0)
    a.part('Deck_lights', 'Lamp', pdeck).box((9.6, 0.1, 0.05), loc=(0, 5.45, 0.1), bevel=0)
    pwell = pv(a, 'Piece_welldeck', (0, 30.5, 2.0))
    a.part('Stern_gate', 'Armor', pwell).box((6.4, 0.4, 2.6), loc=(0, 1.55, 0.0), bevel=0.05, seg=1)
    a.part('Gate_edges', 'Hazard', pwell).box((6.5, 0.1, 0.2), loc=(0, 1.8, 1.2), bevel=0)
    for s in (-1, 1):
        a.part('Gate_rails', 'Steel', pwell).box((0.2, 0.3, 2.8), loc=(s * 3.3, 1.5, 0.0), bevel=0)
    # Navigation lights and the ensign staff.
    a.part('Nav_green', 'SignalGreen').box((0.2, 0.3, 0.2), loc=(-4.2, -6.0, 9.2), bevel=0)
    a.part('Nav_red', 'LavaGlow').box((0.2, 0.3, 0.2), loc=(4.2, -6.0, 9.2), bevel=0)
    steel.cyl(0.06, 2.4, loc=(0, 31.6, 4.5), seg=6, bevel=0)


# ---------------------------------------------------------------------------------------------------------------
# DECISIONS 20Y: Leviathan rebuilt as a battleship (Yamato lineage), 86 x 14.4 m as built (the data's size 1.12 draws
# it 96 x 16 m). Bow (-Y) to stern: (y, half beam at the deck, half beam at the waterline, deck height, rake of the
# lower hull: the stem leans forward at the top, the counter stern hangs over the water).
LEV_SECTIONS = (
    (-43.0, 0.25, 0.10, 6.70, 2.4), (-41.6, 1.70, 0.45, 6.45, 1.7), (-39.0, 3.30, 1.50, 6.05, 1.0),
    (-35.0, 4.90, 3.10, 5.55, 0.4), (-30.0, 6.00, 4.80, 5.05, 0.1), (-24.0, 6.80, 6.20, 4.60, 0.0),
    (-16.0, 7.20, 7.05, 4.25, 0.0), (-6.0, 7.20, 7.20, 4.05, 0.0), (6.0, 7.20, 7.20, 3.95, 0.0),
    (16.0, 7.05, 7.00, 3.85, 0.0), (24.0, 6.70, 6.50, 3.75, 0.0), (31.0, 6.00, 5.50, 3.65, 0.0),
    (37.0, 5.10, 4.10, 3.55, -0.3), (41.4, 4.30, 2.90, 3.50, -0.8), (43.0, 3.70, 1.80, 3.45, -1.3))
LEV_KEEL = -2.6


def _lev_at(y):
    """The hull's section at y, interpolated: (deck half beam, waterline half beam, deck height, rake)."""
    s = LEV_SECTIONS
    if y <= s[0][0]:
        return s[0][1:]
    for a, b in zip(s, s[1:]):
        if y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return tuple(a[k] + (b[k] - a[k]) * t for k in range(1, 5))
    return s[-1][1:]


def deck(y):
    """The main deck's height at y (the sheer: high at the bow, low over the quarterdeck)."""
    return _lev_at(y)[2]


def _flare(hd, hw):
    """Half beam halfway up the side: the flare is concave, most of it near the deck."""
    return hw + (hd - hw) * 0.35


def _side(y, z):
    """The port side's x at height z (above half the deck height) and the side's lean there (radians)."""
    hd, hw, zd, _ = _lev_at(y)
    hm = _flare(hd, hw)
    k = max(0.0, min(1.0, (z - zd * 0.5) / (zd * 0.5)))
    return hm + (hd - hm) * k, math.atan2(hd - hm, zd * 0.5)


def _lev_hull(a):
    """The flush-decked hull (Armor) with its flared bow, a planked deck on it (Wood, 2.5 cm above the hull's
    top so they never z-fight) and the boot-top band in the side's colour at the waterline."""
    rings = []
    for y, hd, hw, zd, rake in LEV_SECTIONS:
        hm = _flare(hd, hw)
        side = [(hd, y, zd), (hm, y + rake * 0.2, zd * 0.5), (hw, y + rake * 0.5, 0.3),
                (hw * 0.93, y + rake * 0.8, LEV_KEEL * 0.55), (hw * 0.4, y + rake, LEV_KEEL)]
        rings.append(side + [(-x, yy, z) for x, yy, z in reversed(side)])
    a.part('Hull', 'Armor').loft(rings)
    slab = []
    for y in (-41.0, -39.0, -35.0, -30.0, -24.0, -16.0, -6.0, 6.0, 16.0, 24.0, 31.0, 37.0, 41.4, 42.7):
        hd, _, zd, _ = _lev_at(y)
        w = hd - 0.14
        slab.append([(w, y, zd + 0.025), (-w, y, zd + 0.025), (-w, y, zd - 0.3), (w, y, zd - 0.3)])
    a.part('Deck', 'Wood').loft(slab)
    # Plank seams: dark lines along the deck, so the planking reads from above.
    seams = a.part('Deck_seams', 'Charred')
    for x in (-5.4, -3.6, -1.8, 1.8, 3.6, 5.4):
        for y0, y1 in ((-33.0, -24.0), (-24.0, -9.8), (13.5, 24.0), (24.0, 33.0)):
            seams.limb((x, y0, deck(y0) + 0.045), (x, y1, deck(y1) + 0.045), 0.04, 0.012, bevel=0, seg=1)
    for s in (-1, 1):
        band = []
        for y in (-24.0, -16.0, -6.0, 6.0, 16.0, 24.0, 31.0, 37.0, 40.5):
            _, hw, _, rake = _lev_at(y)
            yy = y + rake * 0.5
            band.append([(s * (hw + 0.06), yy, 0.62), (s * (hw + 0.06), yy, 0.0), (s * (hw - 0.3), yy, 0.0), (s * (hw - 0.3), yy, 0.62)])
        a.part('Boot_top', 'Team').loft(band)


def _hull_details(a):
    """Rows of scuttles along the sides, the Hegemon marks on the bow (chevrons in the side's colour, a crest on
    the stem), the anchors in their hawse pipes, the chains over the forecastle to the windlasses, the
    breakwater, bollards, ventilators and the jack and ensign staffs."""
    dark = a.part('Scuttles', 'Undercarriage')
    for s in (-1, 1):
        for row, dz in enumerate((0.75, 1.45)):
            for k in range(32):
                y = -24.0 + k * 1.75 + row * 0.6
                if y > 30.0:
                    break
                x, lean = _side(y, deck(y) - dz)
                dark.box((0.05, 0.34, 0.3), loc=(s * (x + 0.012), y, deck(y) - dz), rot=(0, s * lean, 0), bevel=0, seg=1)
    team = a.part('Hull_marks', 'Team')
    for s in (-1, 1):
        for y in (-35.4, -33.4):
            for dz, tilt in ((0.28, 0.6), (-0.28, -0.6)):
                z = deck(y) - 1.4 + dz
                x, lean = _side(y, z)
                team.box((0.05, 1.5, 0.3), loc=(s * (x + 0.02), y + 0.3, z), rot=(tilt, s * lean, 0), bevel=0, seg=1)
    a.part('Crest_rim', 'Gilded').cyl(0.55, 0.12, loc=(0, -42.8, 5.7), rot=(R90 + 0.36, 0, 0), seg=6, bevel=0.02, bseg=1)
    a.part('Crest', 'Team').cyl(0.36, 0.12, loc=(0, -42.88, 5.7), rot=(R90 + 0.36, 0, 0), seg=6, bevel=0.01, bseg=1)
    # Anchors hang in their hawse pipes on the bow's flare; the chains run aft over the deck to the windlasses.
    iron = a.part('Anchors', 'Undercarriage')
    steel = a.part('Fittings', 'Steel')
    chain = a.part('Chains', 'Charred')
    for s in (-1, 1):
        y = -37.2
        x, lean = _side(y, deck(y) - 1.0)
        iron.box((0.3, 0.9, 1.2), loc=(s * (x + 0.12), y, deck(y) - 1.35), rot=(0, s * lean, 0), bevel=0.06, seg=1)
        iron.cyl(0.32, 0.3, loc=(s * (x + 0.05), y, deck(y) - 0.7), rot=(0, R90 + s * lean, 0), seg=10, bevel=0.02, bseg=1)
        hx = s * 2.1
        steel.cyl(0.42, 0.18, loc=(hx, -37.0, deck(-37.0) + 0.06), seg=12, bevel=0.03, bseg=1)             # deck hawse
        steel.cyl(0.5, 0.9, loc=(s * 1.55, -30.6, deck(-30.6) + 0.5), rot=(0, R90, 0), seg=12, bevel=0.05, bseg=1)  # windlass
        steel.cyl(0.36, 0.5, loc=(s * 1.55, -29.2, deck(-29.2) + 0.26), seg=12, bevel=0.04, bseg=1)       # capstan
        n = 16
        for k in range(n):
            t = (k + 0.5) / n
            px = hx + (s * 1.55 - hx) * t
            py = -37.0 + (-30.6 + 37.0) * t
            chain.box((0.2 if k % 2 else 0.1, 0.4, 0.1 if k % 2 else 0.18), loc=(px, py, deck(py) + 0.14), bevel=0, seg=1)
        chain.cyl(0.26, 0.06, loc=(s * 1.55, -29.8, deck(-29.8) + 0.07), seg=10, bevel=0)                 # chain pipe
    # The breakwater: a V across the forecastle, and bollards and mushroom ventilators.
    arm = a.part('Breakwater', 'Armor')
    for s in (-1, 1):
        arm.limb((0, -28.2, deck(-28.2) + 0.4), (s * 5.6, -25.4, deck(-25.4) + 0.4), 0.18, 0.8, bevel=0.03, seg=1)
    for s in (-1, 1):
        for y in (-34.0, -23.0, -10.2, 20.5, 30.5, 38.0):
            hd = _lev_at(y)[0]
            for dy in (-0.35, 0.35):
                steel.cyl(0.14, 0.42, loc=(s * (hd - 0.55), y + dy, deck(y) + 0.22), seg=8, bevel=0)
        for y in (-26.2, 30.2):
            steel.cyl(0.22, 0.5, loc=(s * 2.2, y, deck(y) + 0.26), seg=10, bevel=0.02, bseg=1)
            steel.sphere((0.34, 0.34, 0.16), loc=(s * 2.2, y, deck(y) + 0.56), seg=10, rings=4)
    steel.cyl(0.06, 3.2, loc=(0, -42.3, deck(-42.3) + 1.6), seg=6, bevel=0)                          # jack staff
    steel.cyl(0.06, 3.0, loc=(0, 42.7, deck(42.7) + 1.5), seg=6, bevel=0)                            # ensign staff
    a.part('Ensign', 'Team').box((0.03, 1.3, 0.8), loc=(0, 43.4, deck(42.7) + 2.5), bevel=0, seg=1)


def _triple(a, mount, part_name, loc, rise, w, d, h, barrel, r, gap, ears=1.0, body='Team'):
    """A triple gun turret on its own yaw pivot `mount` under its Part_ empty at loc (on the deck): the barbette
    up to the ring (tall for a superfiring turret), a long flat-sided gunhouse with a sloped face and an
    overhanging back, the rangefinder's arms out of its sides, a Hegemon chevron on the roof, three barrels in
    their blast bags, the muzzle empty on the middle barrel's tip."""
    pk = pv(a, part_name, loc)
    tag = mount[6:].replace('.', '_')
    a.part(f'Barbette_{tag}', 'Armor', pk).cyl(w * 0.46, rise + 0.3, loc=(0, 0, (rise + 0.3) / 2 - 0.3), seg=24, bevel=0.04, bseg=1)
    m = a.pivot(dotted(mount), (0, 0, rise), pk)
    a.part(f'Ring_{tag}', 'Undercarriage', m).cyl(w * 0.48, 0.12, loc=(0, 0, 0.06), seg=24, bevel=0.02, bseg=1)
    yc, top = 0.2, 0.8
    a.part(f'Gunhouse_{tag}', body, m).box((w, d, h), loc=(0, yc, h / 2 + 0.12), bevel=0.14, seg=1, taper=(0.9, top), shift=(0, 0.5))
    yb, yt = yc - d / 2, yc - d / 2 * top + 0.5               # the face's foot and top
    slope = math.atan2(yt - yb, h)
    a.part(f'Gunhouse_face_{tag}', 'Armor', m).box((w * 0.86, 0.3, h * 0.72), loc=(0, yb + (yt - yb) * 0.46 - 0.12, h * 0.46 + 0.12),
                                                  rot=(-slope, 0, 0), bevel=0.05, seg=1)
    roof = a.part(f'Gunhouse_roof_{tag}', 'Armor', m)
    roof.box((w * 0.72, d * 0.5, 0.14), loc=(0, yc + 0.9, h + 0.14), bevel=0.04, seg=1)
    if ears:
        ye = yc + d * 0.28
        roof.cyl(0.3 * ears, w + 1.6 * ears, loc=(0, ye, h * 0.62 + 0.12), rot=(0, R90, 0), seg=10, bevel=0.03, bseg=1)
        for s in (-1, 1):
            roof.box((0.55 * ears, 0.8 * ears, 0.8 * ears), loc=(s * (w / 2 + 0.8 * ears), ye, h * 0.62 + 0.12), bevel=0.06, seg=1)
    mark = a.part(f'Roof_mark_{tag}', 'Team', m)
    for s in (-1, 1):
        mark.limb((0, yc, h + 0.25), (s * w * 0.24, yc + 1.1, h + 0.25), 0.34 * w / 6.6, 0.03, bevel=0, seg=1)
    steel = a.part(f'Barrels_{tag}', 'Steel', m)
    bags = a.part(f'Blast_bags_{tag}', 'Canvas', m)
    bores = a.part(f'Bores_{tag}', 'Charred', m)
    zb = 0.12 + h * 0.45
    y0 = yb + (yt - yb) * 0.45                                # the face at the barrels' height
    sleeve = barrel * 0.3
    tip = y0 - 0.5 - barrel
    for x in (-gap, 0.0, gap):
        bags.cyl(r * 1.9, 0.8, loc=(x, y0 - 0.3, zb), rot=FORWARD, seg=12, bevel=0.03, bseg=1)
        steel.cyl(r * 1.45, sleeve, r2=r * 1.3, loc=(x, y0 - 0.5 - sleeve / 2, zb), rot=FORWARD, seg=12, bevel=0.02, bseg=1)
        steel.cyl(r, barrel - sleeve, r2=r * 0.86, loc=(x, y0 - 0.5 - sleeve - (barrel - sleeve) / 2, zb), rot=FORWARD, seg=12, bevel=0.01, bseg=1)
        bores.cyl(r * 0.5, 0.02, loc=(x, tip + 0.012, zb), rot=FORWARD, seg=10, bevel=0)
    a.pivot(dotted(mount.replace('Mount_', 'Muzzle_')), (0, tip, zb), m)
    return pk


def _aa_tub(tub, floor, x, y, z, r=0.78):
    """An open gun tub: a splinter wall and its dark floor (1 cm above the wall's top)."""
    tub.cyl(r, 0.5, loc=(x, y, z + 0.25), seg=14, bevel=0.03, bseg=1)
    floor.cyl(r * 0.84, 0.02, loc=(x, y, z + 0.51), seg=14, bevel=0)


def _aa25(a, mount, loc, parent):
    """A 25 mm triple anti-aircraft mount (Type 96 lineage) in its tub, on its own yaw pivot `mount` at loc
    (relative to `parent`): a pedestal, the cradle, a splinter shield, three barrels with the muzzle on the
    middle one's tip."""
    pk = dotted(parent)
    tag = mount[6:].replace('.', '_')
    x, y, z = loc
    _aa_tub(a.part(f'AA_tub_{tag}', 'Armor', pk), a.part(f'AA_floor_{tag}', 'Undercarriage', pk), x, y, z)
    m = a.pivot(dotted(mount), (x, y, z + 0.52), pk)
    body = a.part(f'AA_body_{tag}', 'Team', m)
    body.cyl(0.24, 0.3, loc=(0, 0, 0.15), seg=10, bevel=0.03, bseg=1)
    body.box((0.62, 0.62, 0.26), loc=(0, 0.02, 0.4), bevel=0.04, seg=1)
    a.part(f'AA_shield_{tag}', 'Armor', m).box((0.9, 0.05, 0.3), loc=(0, -0.36, 0.3), bevel=0, seg=1)
    steel = a.part(f'AA_barrels_{tag}', 'Steel', m)
    for bx in (-0.15, 0.0, 0.15):
        steel.cyl(0.05, 1.45, r2=0.04, loc=(bx, -0.3 - 0.725, 0.42), rot=FORWARD, seg=8, bevel=0)
    a.pivot(dotted(mount.replace('Mount_', 'Muzzle_')), (0, -1.75, 0.42), m)


def _decor_aa(tub, floor, gun, steel, x, y, z, yaw, pitch=0.45, triple=True):
    """A 25 mm mount that is only drawn (no pivot), trained out to sea at `yaw` and raised."""
    _aa_tub(tub, floor, x, y, z)
    gun.box((0.6, 0.6, 0.26), loc=(x, y, z + 0.8), rot=(0, 0, yaw), bevel=0.04, seg=1)
    d = (math.sin(yaw), -math.cos(yaw))
    for off in ((-0.15, 0.0, 0.15) if triple else (0.0,)):
        ox, oy = x + math.cos(yaw) * off, y + math.sin(yaw) * off
        steel.cyl(0.05, 1.4, r2=0.04, loc=(ox + d[0] * math.cos(pitch), oy + d[1] * math.cos(pitch), z + 0.85 + math.sin(pitch)),
                  rot=(R90 - pitch, 0, yaw), seg=8, bevel=0)


def _decor_127(house, steel, x, y, z, yaw, pitch=0.35):
    """A twin 127 mm high-angle mount (Type 89 lineage) under its shield, only drawn, trained outboard."""
    house.box((1.6, 1.9, 1.0), loc=(x, y, z + 0.5), rot=(0, 0, yaw), bevel=0.2, seg=2, taper=(0.86, 0.8))
    d = (math.sin(yaw), -math.cos(yaw))
    for off in (-0.32, 0.32):
        ox, oy = x + math.cos(yaw) * off, y + math.sin(yaw) * off
        steel.cyl(0.08, 2.3, loc=(ox + d[0] * 2.0 * math.cos(pitch), oy + d[1] * 2.0 * math.cos(pitch), z + 0.6 + 2.0 * math.sin(pitch)),
                  rot=(R90 - pitch, 0, yaw), seg=8, bevel=0)


def _ellipse(cx, cy, z, ax, ay, n=14):
    return [(cx + ax * math.cos(k * math.tau / n), cy + ay * math.sin(k * math.tau / n), z) for k in range(n)]


def leviathan(a):
    """Kessler's Leviathan, rebuilt as a battleship (Yamato lineage; DECISIONS 20Y), 86 x 14.4 m as built.

    Its parts (each an empty holding its meshes and pivots): three triple 460 mm turrets `Part_gun` (A),
    `Part_gun.001` (B, superfiring) and `Part_gun.002` (C, aft) on `Mount_gun` / `.001` / `.002`; two triple
    155 mm secondaries `Part_sec_f` / `Part_sec_a` (`Mount_gun.003` / `.004`, superfiring over B and C); the
    launch cells beside the funnel `Part_vls`; two CIWS `Part_mg` / `Part_mg.001`; the 25 mm batteries along
    the side decks `Part_aa_l` (port, `Mount_mg.002`-`.005`) and `Part_aa_r` (starboard, `.006`-`.009`); the
    fire-control top `Part_radar` (the rangefinder and the spinning `Radar`); the aircraft deck `Part_deck`
    (catapults, a floatplane, the helicopter spot, the crane); the stern gate `Part_welldeck`; the funnel
    `Part_engine`. Every muzzle sits on its middle barrel's tip; every bore points along -Y at rest (the aft
    guns too: the game trains them aft or out to the beam).
    """
    _suffixed(a)
    _lev_hull(a)
    _hull_details(a)

    # Main battery: A and B forward (B on a tall barbette, superfiring), C aft.
    main = dict(w=6.6, d=7.2, h=2.5, barrel=9.6, r=0.27, gap=1.7, ears=1.0)
    _triple(a, 'Mount_gun', 'Part_gun', (0, -21.4, deck(-21.4)), rise=0.6, **main)
    _triple(a, 'Mount_gun.001', 'Part_gun.001', (0, -13.0, deck(-13.0)), rise=2.6, **main)
    _triple(a, 'Mount_gun.002', 'Part_gun.002', (0, 25.6, deck(25.6)), rise=0.7, **main)

    # The superstructure: two deckhouses, the pagoda tower with its galleries, the bridge and the director.
    z01 = deck(1.7)
    z02 = z01 + 1.8
    z03 = z02 + 1.7
    team = a.part('Superstructure', 'Team')
    team.box((10.2, 22.6, 2.2), loc=(0, 1.7, z01 + 0.7), bevel=0.1, seg=1, taper=(0.98, 0.99))            # 01 level
    team.box((8.6, 15.5, 1.7), loc=(0, 0.5, z02 + 0.85), bevel=0.1, seg=1, taper=(0.97, 0.98))           # 02 level
    team.box((4.6, 5.6, 7.5), loc=(0, -1.0, z03 + 3.75), bevel=0.12, seg=1, taper=(0.8, 0.82))           # the tower
    ztop = z03 + 7.5
    team.box((6.0, 4.0, 1.6), loc=(0, -1.5, ztop + 0.8), bevel=0.12, seg=1, taper=(0.92, 0.9))            # bridge
    team.box((3.2, 3.0, 1.8), loc=(0, -1.0, ztop + 2.5), bevel=0.1, seg=1, taper=(0.9, 0.9))              # director tower
    glass = a.part('Bridge_glass', 'Glass')
    glass.box((5.2, 0.06, 0.55), loc=(0, -3.42, ztop + 1.0), rot=(0.12, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((0.06, 3.0, 0.5), loc=(s * 2.84, -1.5, ztop + 1.0), bevel=0)
    gal = a.part('Galleries', 'Armor')
    dark = a.part('Tower_windows', 'Undercarriage')
    for zz, gw, gd in ((z03 + 1.7, 8.4, 7.2), (z03 + 3.7, 6.6, 6.2), (z03 + 5.6, 5.8, 5.4)):
        gal.box((gw, gd, 0.16), loc=(0, -1.0, zz), bevel=0.03, seg=1)
        t = (zz + 0.45 - z03) / 7.5
        dark.box((4.6 * (1 - 0.2 * t) * 0.8, 0.05, 0.28), loc=(0, -1.0 - 2.8 * (1 - 0.18 * t) - 0.02, zz + 0.45), bevel=0)
    for s in (-1, 1):
        gal.box((1.8, 1.6, 0.14), loc=(s * 3.9, -3.0, ztop + 0.1), bevel=0.03, seg=1)                   # bridge wings
    strut = a.part('Tower_struts', 'Steel')
    for s in (-1, 1):
        strut.limb((s * 1.8, 4.1, z03), (s * 0.9, 0.8, ztop + 1.2), 0.22, 0.22, bevel=0)

    # The fire-control top: the rangefinder's long arms across the director, the radar mast and its spinning array.
    prad = pv(a, 'Part_radar', (0, -1.0, ztop + 3.4))
    a.part('Director', 'Armor', prad).box((2.4, 2.2, 1.1), loc=(0, 0, 0.55), bevel=0.1, seg=1)
    a.part('Rangefinder', 'Steel', prad).cyl(0.3, 7.2, loc=(0, 0.2, 0.75), rot=(0, R90, 0), seg=12, bevel=0.02, bseg=1)
    for s in (-1, 1):
        a.part('Rangefinder_hoods', 'Armor', prad).box((0.5, 0.8, 0.8), loc=(s * 3.6, 0.2, 0.75), bevel=0.08, seg=1)
    a.part('Radar_mast', 'Steel', prad).cyl(0.09, 2.4, loc=(0, 0.5, 2.3), seg=8, bevel=0)
    rad = a.pivot('Radar', (0, 0.5, 3.2), prad)
    a.part('Radar_bar', 'Medical', rad).box((2.8, 0.22, 0.9), loc=(0, 0, 0.45), bevel=0.04, seg=1)
    a.part('Radar_grid', 'Undercarriage', rad).box((2.6, 0.26, 0.1), loc=(0, 0, 0.45), bevel=0)
    a.part('Mast_lamp', 'Lamp', prad).sphere(0.12, loc=(0, 0.5, 4.3), seg=8, rings=4)

    # The forward secondary on the superstructure's face, superfiring over B.
    sec = dict(w=3.6, d=4.4, h=1.6, barrel=5.6, r=0.12, gap=0.62, ears=0.55)
    _triple(a, 'Mount_gun.003', 'Part_sec_f', (0, -7.2, z02), rise=z03 - z02 + 2.1, **sec)

    # The funnel (the engine room below is the part): raked aft, oval, its cap and a band in the side's colour.
    peng = pv(a, 'Part_engine', (0, 7.0, z03))
    RAKE = 0.45
    rings = []
    for k in range(7):
        zz = k * 1.5
        first = k == 0
        rings.append(_ellipse(0, zz * RAKE + (0.4 if first else 0), zz, 1.75 - zz * 0.02 + (0.25 if first else 0), 2.6 - zz * 0.04 + (0.5 if first else 0)))
    a.part('Funnel', 'Armor', peng).loft(rings)
    a.part('Funnel_band', 'Team', peng).loft([_ellipse(0, 6.2 * RAKE, 6.2, 1.66, 2.39), _ellipse(0, 7.0 * RAKE, 7.0, 1.645, 2.36)])
    a.part('Funnel_cap', 'Charred', peng).loft([_ellipse(0, 9.0 * RAKE, 9.02, 1.54, 2.2), _ellipse(0, 9.0 * RAKE, 9.2, 1.3, 1.95)])
    pipes = a.part('Funnel_pipes', 'Steel', peng)
    for s in (-1, 1):
        pipes.limb((s * 0.9, 3.35, 0.0), (s * 0.8, 2.25 + 9.3 * RAKE, 9.3), 0.16, 0.16, bevel=0)

    # The launch cells either side of the funnel (a missile cruiser's: the hybrid's).
    pvls = pv(a, 'Part_vls', (0, 5.6, z03))
    hatch = a.part('Vls_hatches', 'Undercarriage', pvls)
    for s in (-1, 1):
        a.part('Vls_block', 'Armor', pvls).box((2.0, 5.0, 0.6), loc=(s * 3.15, 0, 0.3), bevel=0.05, seg=1)
        for i in range(2):
            for j in range(4):
                hatch.box((0.8, 1.05, 0.05), loc=(s * 3.15 + (i - 0.5) * 0.9, -1.8 + j * 1.2, 0.64), bevel=0.02, seg=1)

    # Searchlights on a platform round the funnel, boats on the 01 deck.
    gal.box((7.4, 3.0, 0.14), loc=(0, 9.9, z03 + 2.6), bevel=0.03, seg=1)
    lights = a.part('Searchlights', 'Steel')
    lamp = a.part('Searchlight_faces', 'Lamp')
    for s in (-1, 1):
        for dy in (-0.7, 0.7):
            lights.cyl(0.36, 0.5, loc=(s * 3.1, 9.9 + dy, z03 + 3.0), rot=FORWARD, seg=10, bevel=0.03, bseg=1)
            lamp.cyl(0.3, 0.02, loc=(s * 3.1, 9.9 + dy - 0.27, z03 + 3.0), rot=FORWARD, seg=10, bevel=0)
        strut.limb((s * 3.4, 9.9, z02), (s * 3.2, 9.9, z03 + 2.55), 0.12, 0.12, bevel=0)
    for s in (-1, 1):
        a.part('Boats', 'Medical').box((1.3, 4.2, 0.7), loc=(s * 4.45, 10.9, z02 + 0.4), bevel=0.3, seg=2, taper=(0.8, 0.9))
        a.part('Boat_covers', 'Canvas').box((1.0, 3.2, 0.2), loc=(s * 4.45, 10.9, z02 + 0.82), bevel=0.06, seg=1)

    # The aft superstructure, its small rangefinder tower and the mainmast (a tripod on them).
    team.box((6.0, 5.0, 2.8), loc=(0, 15.0, deck(15.0) + 1.0), bevel=0.1, seg=1, taper=(0.95, 0.95))
    zaft = deck(15.0) + 2.4
    team.box((3.0, 2.8, 3.0), loc=(0, 14.2, zaft + 1.5), bevel=0.1, seg=1, taper=(0.9, 0.9))
    a.part('Aft_rangefinder', 'Steel').cyl(0.2, 4.2, loc=(0, 14.2, zaft + 3.3), rot=(0, R90, 0), seg=10, bevel=0.02, bseg=1)
    mast = a.part('Mainmast', 'Steel')
    mtop = (0, 14.2, zaft + 10.8)
    for foot in ((0, 13.4, zaft + 3.0), (-1.1, 16.2, zaft), (1.1, 16.2, zaft)):
        mast.limb(foot, mtop, 0.2, 0.2, bevel=0)
    mast.cyl(0.08, 2.0, loc=(0, 14.2, mtop[2] + 1.0), seg=6, bevel=0)
    mast.box((4.4, 0.14, 0.14), loc=(0, 14.2, mtop[2] - 1.4), bevel=0)
    a.part('Mast_top_lamp', 'Lamp').sphere(0.12, loc=(0, 14.2, mtop[2] + 2.1), seg=8, rings=4)
    _triple(a, 'Mount_gun.004', 'Part_sec_a', (0, 19.8, deck(19.8)), rise=3.0, **sec)

    # The CIWS: forward on the tower's first gallery (starboard), aft on the aft superstructure (port).
    pv(a, 'Part_mg', (-3.4, -3.4, z03 + 1.78))
    ciws(a, 'Mount_mg', (0, 0, 0), parent='Part_mg')
    pv(a, 'Part_mg.001', (2.1, 16.5, zaft))
    ciws(a, 'Mount_mg.001', (0, 0, 0), parent='Part_mg.001')

    # The 25 mm batteries along the side decks (each side a part with four trainable mounts).
    for side, part, first in ((1, 'Part_aa_l', 2), (-1, 'Part_aa_r', 6)):
        pv(a, part, (side * 6.1, 4.5, deck(4.5)))
        for k, y in enumerate((-5.0, 0.0, 8.0, 13.0)):
            _aa25(a, f'Mount_mg.{first + k:03d}', (0, y - 4.5, deck(y) - deck(4.5)), part)

    # Drawn-only mounts: twin 127 mm high-angle guns and more 25 mm tubs round the ship.
    tub, floor = a.part('Decor_tubs', 'Armor'), a.part('Decor_tub_floors', 'Undercarriage')
    gun, barrels = a.part('Decor_guns', 'Team'), a.part('Decor_barrels', 'Steel')
    for s in (-1, 1):
        for y in (-2.5, 4.0):
            _decor_127(gun, barrels, s * 6.1, y, deck(y), s * 0.67)
        _decor_aa(tub, floor, gun, barrels, s * 6.1, 10.5, deck(10.5), s * R90, triple=False)
        for x, y, z in ((3.4, -5.6, z03), (2.4, 12.2, z02), (4.6, -23.6, deck(-23.6)), (5.4, 21.0, deck(21.0)), (5.3, 28.6, deck(28.6))):
            _decor_aa(tub, floor, gun, barrels, s * x, y, z, s * (R90 + 0.3 * (-1 if y < 0 else 1)))

    # The aircraft deck aft: two catapults, a floatplane on the port one, the helicopter spot, the crane.
    y_ad = 36.0
    pdeck = pv(a, 'Part_deck', (0, y_ad, deck(y_ad)))

    def dz(y):
        return deck(y_ad + y) - deck(y_ad)

    cat = a.part('Catapults', 'Undercarriage', pdeck)
    rail = a.part('Catapult_rails', 'Steel', pdeck)
    for s in (-1, 1):
        cx, cy = s * 3.6, -2.4
        cat.cyl(0.85, 0.2, loc=(cx, cy, dz(cy) + 0.12), seg=14, bevel=0.03, bseg=1)
        yaw = s * 0.5
        cat.box((1.0, 7.4, 0.45), loc=(cx, cy, dz(cy) + 0.45), rot=(0, 0, yaw), bevel=0.04, seg=1)
        for o in (-0.3, 0.3):
            rail.box((0.12, 7.2, 0.06), loc=(cx + math.cos(yaw) * o, cy + math.sin(yaw) * o, dz(cy) + 0.7), rot=(0, 0, yaw), bevel=0)
    yaw = 0.5
    fx, fy = 3.6 + 1.5 * math.sin(yaw), -2.4 - 1.5 * math.cos(yaw)
    plane = a.part('Floatplane', 'Medical', pdeck)
    plane.cyl(0.32, 3.6, r2=0.2, loc=(fx, fy, dz(fy) + 1.25), rot=(R90, 0, yaw), seg=10, bevel=0)
    plane.box((5.2, 0.8, 0.08), loc=(fx, fy, dz(fy) + 1.45), rot=(0, 0, yaw), bevel=0.02, seg=1)
    tx, ty = fx - math.sin(yaw) * 1.55, fy + math.cos(yaw) * 1.55
    plane.box((1.8, 0.5, 0.06), loc=(tx, ty, dz(ty) + 1.3), rot=(0, 0, yaw), bevel=0.02, seg=1)
    a.part('Floatplane_floats', 'Team', pdeck).cyl(0.16, 2.6, loc=(fx, fy, dz(fy) + 0.82), rot=(R90, 0, yaw), seg=8, bevel=0)
    spot = a.part('Deck_marks', 'SafetyStripe', pdeck)
    for k in range(16):
        u = k * math.tau / 16
        py = 3.0 + math.sin(u) * 2.0
        spot.box((0.28, 0.8, 0.02), loc=(math.cos(u) * 2.0, py, dz(py) + 0.06), rot=(0, 0, u + R90), bevel=0)
    spot.box((0.28, 2.4, 0.02), loc=(0, 3.0, dz(3.0) + 0.06), bevel=0)
    a.part('Hangar_hatch', 'Undercarriage', pdeck).box((3.0, 2.4, 0.05), loc=(0, -4.4, dz(-4.4) + 0.06), bevel=0.02, seg=1)
    crane = a.part('Crane', 'Armor', pdeck)
    crane.cyl(0.38, 2.4, loc=(0, 5.9, dz(5.9) + 1.2), seg=12, bevel=0.03, bseg=1)
    crane.limb((0, 5.9, dz(5.9) + 2.2), (0, 2.4, dz(5.9) + 5.8), 0.34, 0.4, bevel=0.03, seg=1, taper=(0.7, 0.7))
    a.part('Crane_band', 'Hazard', pdeck).cyl(0.4, 0.3, loc=(0, 5.9, dz(5.9) + 2.0), seg=12, bevel=0)
    a.part('Crane_cable', 'Charred', pdeck).limb((0, 2.45, dz(5.9) + 5.7), (0, 2.45, dz(5.9) + 3.4), 0.04, 0.04, bevel=0)
    a.part('Crane_hook', 'Charred', pdeck).box((0.3, 0.3, 0.4), loc=(0, 2.45, dz(5.9) + 3.2), bevel=0.04, seg=1)

    # The stern gate (the well deck for the landing craft) in the transom.
    hd, hw, zd, rake = _lev_at(43.0)
    pwell = pv(a, 'Part_welldeck', (0, 42.75, 1.9))
    lean = math.atan2(-rake * 0.5, zd - 0.3)
    a.part('Stern_gate', 'Armor', pwell).box((4.2, 0.3, 2.4), loc=(0, 0.18, 0), rot=(-lean, 0, 0), bevel=0.05, seg=1)
    a.part('Gate_edges', 'Hazard', pwell).box((4.3, 0.08, 0.18), loc=(0, 0.42, 1.1), rot=(-lean, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Gate_rails', 'Steel', pwell).box((0.18, 0.26, 2.5), loc=(s * 2.15, 0.2, 0), rot=(-lean, 0, 0), bevel=0)

    # Navigation lights on the bridge wings.
    a.part('Nav_green', 'SignalGreen').box((0.2, 0.3, 0.2), loc=(-4.6, -3.0, ztop + 0.3), bevel=0)
    a.part('Nav_red', 'LavaGlow').box((0.2, 0.3, 0.2), loc=(4.6, -3.0, ztop + 0.3), bevel=0)


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
    'leviathan': (leviathan, dict(ao_distance=1.6, grime_height=1.0)),
    'sea_cruiser': (sea_cruiser, dict(ao_distance=1.5, grime_height=1.0)),
    'sea_corvette': (sea_corvette, dict(ao_distance=1.0, grime_height=0.8)),
    'missile_boat': (missile_boat, dict(ao_distance=0.6, grime_height=0.5)),
    'landing_craft': (landing_craft, dict(ao_distance=0.8, grime_height=0.6)),
    'lighthouse': (lighthouse, dict(ao_distance=0.8, grime_height=0.6)),
    'pier': (pier, dict(ao_distance=0.4, grime_height=0.3)),
    'fishing_boat': (fishing_boat, dict(ao_distance=0.5, grime_height=0.4)),
}
