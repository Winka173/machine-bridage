"""Naval models lane A (06/10, DECISIONS "Naval models (lane A)"): the nine light and medium hulls of the naval
expansion, each its own builder (contract: Docs/naval/MODEL_CONTRACT.md; parts: mb_naval_a_kit.py).

  torpedo_boat           18 m   Shershen / Turya-class fast attack craft: planing hull, low wheelhouse, two 533 mm
                                deck tubes either side (`Mount_missile`, the runtime launches from each tube in turn),
                                an M2 tub aft (`Mount_mg`); nothing else on deck.
  ashm_corvette          34 m   Tarantul / Molniya: a 2 x 2 bank of big Oniks-type canisters on the foredeck
                                (`Mount_missile`, fixed: an invisible pivot at the mouths), the bridge and pyramid
                                mast, an AK-630 aft (`Mount_mg`) with its director, decoy launchers (`Aps_cluster`).
  aa_corvette            33 m   light air-defence corvette: a Sea Sparrow-type 8-cell trainable box on a barbette in
                                place of a gun (`Mount_missile`), a tall mast with a 3D radar and illuminators, an
                                AK-630 aft (`Mount_mg`), an M2 tub on the starboard bridge wing (`Mount_mg_02`).
  ciws_escort_ship       26 m   point-defence escort: a 76 mm forward (`Mount_gun`), three AK-630s (aft `Mount_mg`,
                                on the bridge sponsons `Mount_mg_02` / `_03`), directors, many decoys; no missiles.
  ew_corvette            32 m   EW corvette: a 76 mm forward (`Mount_gun`), an enclosed mast crowned by a jammer dome,
                                the big jammer radome tower amidships with its arrays, a Mistral pedestal aft
                                (`Mount_missile`); no radar dish (owner constraint).
  frigate                42 m   balanced frigate: an AK-100 forward (`Mount_gun`), two canisters amidships angled
                                outboard (`Mount_missile`), a SHORAD pedestal on the after house (`Mount_missile_02`),
                                an AK-630 on the quarterdeck house (`Mount_mg`).
  missile_frigate        44 m   Krivak-like: the dominant 3 x 2 canister bank on the foredeck (`Mount_missile`), a
                                RAM-type box on the after house (`Mount_missile_02`), an AK-630 (`Mount_mg`) and the
                                76 mm right aft (`Mount_gun`) as the afterthought.
  aa_frigate             43 m   air-defence frigate: the twin-arm area SAM on its magazine barbette forward (the
                                biggest system on the hull, `Mount_missile`), a big air-search radar and
                                illuminators, an AK-630 amidships on a raised platform (`Mount_mg`), a 76 mm aft only.
  rocket_artillery_ship  38 m   navalised GMLRS: a four-pod rocket battery amidships on a training barbette
                                (`Mount_rocket`), reload pods and a crane, the bridge aft (coaster style), a bare M2
                                tub on the forecastle (`Mount_mg`); no gun, no CIWS, no missiles.

Simple (non-parts) vehicles: no `Part_*` nodes; the runtime sinks a ship whole (ShipSinking) and draws the wake from
the data (WakeView), so no wake / smoke / wreck nodes. Metres, +Z up, -Y the bow, +X the left; waterline z = 0.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_naval_a_kit as N

R90 = math.pi / 2

MERGE = {n: 'Rails' for n in ('Mast_steel', 'Windlass', 'Davits', 'Deck_fittings', 'Canister_frames', 'Tube_caps',
                              'Tube_saddles', 'Exhausts', 'Director_feeds', 'Antennas', 'Ladders', 'Wall_trays',
                              'Staffs', 'Winch')}
MERGE.update({n: 'Hull_seams' for n in ('Funnel_cap', 'Anchor_chain', 'Sam_hatches', 'Doors', 'Vents')})
MERGE.update({n: 'Deck_gear' for n in ('Ciws_base', 'Mg_tub', 'Sam_post', 'Sam_magazine', 'Launcher_base', 'Roof_plates',
                                        'Deck_lockers', 'Breakwater', 'Pod_stacks', 'Roof_fittings')})
MERGE.update({n: 'Superstructure' for n in ('Team_band', 'Bridge_wings', 'Deckhouse')})
MERGE.update({'Deck_plates': 'Deck_walkways'})
MERGE.update({'Portholes': 'Bridge_glass', 'Canister_bands': 'Hazard_marks', 'Tube_bands': 'Hazard_marks',
              'Porthole_rims': 'Rails', 'Mast_boxes': 'Deck_gear', 'Mast_domes': 'Directors', 'Fire_control': 'Directors'})


def _finish(a):
    K.merge_parts(a, MERGE)
    k.clean(a)


def _breakwater(a, hull, y, w=1.0, h=.5):
    bw = a.part('Breakwater', 'Armor')
    for s in (-1, 1):
        bw.box((w * 2.2, .08, h), loc=(s * w, y, hull.dz(y) + h / 2), rot=(0, 0, s * -.4), bevel=0)


def _quarterdeck(a, hull, y0, seed, x0=None, n=10):
    """Mooring gear, capstans, lockers and the stern rails from y0 to the transom."""
    y1 = hull.stern - .5
    hw = hull.hb((y0 + y1) / 2) - .5 if x0 is None else x0
    z = hull.dz(y0)
    fit = a.part('Deck_fittings', 'Steel')
    N.bollards(fit, [(s * (hull.hb(y) - .45), y, hull.dz(y)) for s in (-1, 1) for y in (y0 + .8, y1 - .8)])
    for s in (-1, 1):
        k.lathe(fit, [(.3, 0), (.3, .1), (.2, .15), (.2, .45), (.28, .5), (0, .5)], loc=(s * hw * .5, y1 - 1.6, z),
                seg=10)
        fit.box((.25, .5, .2), loc=(s * (hull.hb(y1 - .3) - .12), y1 - .3, z + .1), bevel=0)
    K.clutter(a, 'Deck_lockers', 'Armor', -hw * .8, hw * .8, y0 + .6, y1 - 2.4, z, n, seed=seed, size=(.3, .9),
              height=(.25, .7))
    _plates(a, 'Deck_plates', 'NavyGrey', -hw * .9, hw * .9, y0 + .4, y1 - .3, z, n + 4, seed + 100)
    for s in (-1, 1):
        K.railing(a.part('Rails', 'Steel'), [hull.edge(y, s, inset=.08) for y in (y0, (y0 + y1) / 2, y1)] +
                  [(s * .4, hull.stern - .08, hull.dz(hull.stern))], h=.9, post=1.2, r=.022)


def _vents(a, pts):
    v = a.part('Vents', 'Undercarriage')
    for x, y, z, w in pts:
        v.box((w, .5, .45), loc=(x, y, z + .22), bevel=0)
        a.part('Roof_fittings', 'Armor').box((w + .1, .6, .06), loc=(x, y, z + .47), bevel=0)


# ============================================================================= torpedo boat
def torpedo_boat(a):
    """torpedo_boat: see the module docstring (18 x 4.2 m)."""
    hull = N.Hull(a, 18.0, 4.2, 1.15, 1.6, keel=-.62, entry=.5, transom=.95, flare=.24, rake=1.0, sheer_from=.5,
                  planing=True, bulwark=(0, 0))
    hull.build(stations=(0, .01, .025, .045, .07, .1, .14, .19, .25, .32, .4, .48, .56, .64, .72, .8, .87, .93, .97, 1.0),
               team_band=(-6.0, 6.5, .12, .22))
    d = hull.dz
    # Spray rails and the rubbing strake along the topsides.
    sr = a.part('Hull_seams', 'Undercarriage')
    for s in (-1, 1):
        sr.tube([(s * (hull.hb(y) * .995 + .03), y, d(y) - .38) for y in (-8.0, -5.0, -1.0, 3.0, 8.9)], .045, seg=4)
    # The low wheelhouse with raked windows, the open conning position on its roof.
    sup = a.part('Superstructure', 'Team')
    N.tier(sup, -3.4, 1.2, d(-1.0) - .05, 2.45, 1.0, .82, rake=.75, cut=.3, aft=.15)
    N.window_band(a.part('Bridge_glass', 'Glass'), -3.4, d(-1.0) - .05, 2.45, .75, .66, 4, frac=(.42, .86))
    for s in (-1, 1):
        N.side_windows(a.part('Bridge_glass', 'Glass'), s, (-1.9, -1.1), 2.05, .9, lean=.07, size=(.55, .3))
        N.doors(a.part('Doors', 'Undercarriage'), s, (.3,), d(.3) - .05, .95, h=1.05, lean=.07)
    k.block(a.part('Deckhouse', 'Team'), (1.3, 1.2, .5), loc=(0, .3, 2.7), chamfer=.06)
    K.railing(a.part('Rails', 'Steel'), [(-.7, -.25, 2.95), (-.7, .9, 2.95), (.7, .9, 2.95), (.7, -.25, 2.95)], h=.5,
              post=.6, r=.018)
    # The short radar mast on the wheelhouse: a navigation scanner, whips, the lamps.
    top = N.mast(a, (0, -.9, 2.45), .55, .42, .3, lattice=.6, yard=1.4)
    N.radar(a, top, 'nav', w=1.2)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.55, .6, 2.95), h=1.5, r=.02, lean=.08)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.55, .6, 2.95), h=1.3, r=.02, lean=.08)
    for s in (-1, 1):
        N.nav_lights(a, s, (s * .95, -2.6, 2.3))
    # Two 533 mm tubes along the deck edges, mouths forward (the twin torpedo rack).
    N.torpedo_tubes(a, -1.6, d(1.0) + .6, (-1.45, 1.45), d(1.0), length=5.6, r=.3, splay=.04)
    # The M2 in its tub aft, the inflatable between the tubes, engine-room vents, the exhausts on the transom.
    N.hmg_tub(a, (0, 6.4, d(6.4)), r=.6)
    K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (0, 3.4, d(3.4) + .05), length=2.4, beam=1.1)
    _vents(a, [(-.7, 7.6, d(7.6), .6), (.7, 7.6, d(7.6), .6)])
    for s in (-1, 1):
        for xx in (.55, 1.15):
            a.part('Exhausts', 'Steel').cyl(.13, .3, loc=(s * xx, 9.05, .45), rot=K.BACKWARD, seg=8, bevel=0)
        K.soot(a, (s * .85, 9.0, .5), radius=.6, k=.5)
    fit = a.part('Deck_fittings', 'Steel')
    N.bollards(fit, [(s * (hull.hb(y) - .3), y, d(y)) for s in (-1, 1) for y in (-6.8, 8.2)])
    for s in (-1, 1):
        K.railing(a.part('Rails', 'Steel'), [hull.edge(y, s, inset=.07) for y in (-8.3, -6.5, -4.5)], h=.6, post=.9,
                  r=.018)
        K.railing(a.part('Rails', 'Steel'), [hull.edge(y, s, inset=.07) for y in (5.0, 7.0, 8.9)], h=.6, post=.9,
                  r=.018)
    N.life_rafts(a, [(s * .55, -2.0, 2.45 + .28) for s in (-1, 1)])
    # Ammunition lockers by the tub, the searchlight on the wheelhouse, cleats and the rope coils.
    for s in (-1, 1):
        for y in (5.6, 6.4, 7.2):
            P_ammo = a.part('Deck_lockers', 'Armor')
            k.block(P_ammo, (.45, .3, .3), loc=(s * .95, y, d(y) + .15), chamfer=.03)
        for y in (-7.4, -2.0, 4.6, 8.5):
            a.part('Deck_fittings', 'Steel').box((.08, .4, .08), loc=(s * (hull.hb(y) - .25), y, d(y) + .1), bevel=0)
        k.ring(a.part('Kit_cables', 'Undercarriage'), [(.18, 0), (.24, 0), (.24, .06), (.18, .06)],
               loc=(s * .8, 7.4, d(7.4)), seg=12)
    for x in (.55, -.55):
        k.lathe(a.part('Searchlight', 'Armor'), [(0, 0), (.16, 0), (.2, .1), (.2, .35), (.16, .4), (0, .4)],
                loc=(x, -1.6, 2.45), seg=14)
        a.part('Lamps', 'Lamp').cyl(.17, .02, loc=(x, -1.81, 2.65), rot=K.FORWARD, seg=14, bevel=0)
    for s in (-1, 1):
        K.railing(a.part('Rails', 'Steel'), [(s * 1.05, -1.3, d(-1.3) + .02), (s * 1.05, 1.0, d(1.0) + .02)], h=.7,
                  post=.7, r=.016)
    _deck_paint(a, hull, [(-8.0, -3.6), (4.4, 8.6)], hatches=((0, -5.6), (0, 8.0)))
    _staffs(a, hull, jack=.9, ensign=1.2)
    _finish(a)


def _wall_x(z, z0, z1, hw0, hw1):
    return hw0 - (hw0 - hw1) * ((z - z0) / (z1 - z0))


def _wall_fittings(a, y0, y1, z0, z1, hw0, hw1, lean, busy):
    """Louvres, lockers and a cable tray along both walls of a house, clear of its doors and portholes (busy y)."""
    zl, zk, zt = z0 + (z1 - z0) * .32, z0 + .45, z1 - .3
    n = max(1, int((y1 - y0) / 1.25))
    for s in (-1, 1):
        a.part('Wall_trays', 'Steel').tube([(s * (_wall_x(zt, z0, z1, hw0, hw1) + .05), y, zt) for y in (y0, y1)], .035,
                                           seg=4)
        for i in range(n):
            y = y0 + (i + .5) * (y1 - y0) / n
            if any(abs(y - b) < .75 for b in busy):
                continue
            if (i + (s > 0)) % 3 == 0:
                k.block(a.part('Deck_gear', 'Armor'), (.3, .7, .8), loc=(s * (_wall_x(zk, z0, z1, hw0, hw1) + .14), y,
                                                                         z0 + .45), chamfer=.03)
            else:
                a.part('Vents', 'Undercarriage').box((.04, .75, .42), loc=(s * (_wall_x(zl, z0, z1, hw0, hw1) + .02),
                                                                           y, zl), rot=(0, s * lean, 0), bevel=0)
                a.part('Wall_trays', 'Steel').box((.05, .82, .05), loc=(s * (_wall_x(zl + .24, z0, z1, hw0, hw1) + .03),
                                                                        y, zl + .24), bevel=0)


def _deck_paint(a, hull, ranges, hatches=()):
    """Walkway strips along both deck edges over `ranges` (light paint on the dark non-skid) and raised hatches."""
    strips = a.part('Deck_walkways', 'NavyGrey')
    for y0, y1 in ranges:
        ys = [y0 + (y1 - y0) * i / 6 for i in range(7)]
        for s in (-1, 1):
            N.grid(strips, [[(s * (hull.hb(y) - .55), y, hull.dz(y) + .012), (s * (hull.hb(y) - .3), y,
                                                                               hull.dz(y) + .012)] for y in ys],
                   (0, 0, 1))
    for x, y in hatches:
        k.block(a.part('Hatches', 'Armor'), (.8, .9, .1), loc=(x, y, hull.dz(y) + .05), chamfer=.02)
        a.part('Hatches', 'Steel').box((.4, .04, .04), loc=(x, y - .3, hull.dz(y) + .12), bevel=0)


def _staffs(a, hull, jack=1.3, ensign=1.7):
    """The jackstaff at the stem and the ensign staff at the transom (silhouette ends)."""
    yb, ys = hull.bow + .35, hull.stern - .25
    st = a.part('Staffs', 'Steel')
    st.tube([(0, yb, hull.dz(yb) + .5), (0, yb - .05, hull.dz(yb) + .5 + jack)], .03, seg=5)
    st.tube([(0, ys, hull.dz(ys)), (0, ys + .25, hull.dz(ys) + ensign)], .035, seg=5)
    a.part('Hazard_marks', 'Hazard').box((.25, .02, .16), loc=(0, ys + .21, hull.dz(ys) + ensign - .2), bevel=0)


def _crane(a, loc, s, reach=3.2, yaw=.35):
    """A boat / stores crane on side s: the pedestal, the slewing house, the jib laid along the deck edge."""
    x, y, z = loc
    cr = a.part('Crane', 'CraneYellow')
    k.lathe(cr, [(.3, 0), (.3, 1.1), (.22, 1.2), (0, 1.2)], loc=(x, y, z), seg=12)
    k.block(cr, (.6, .8, .55), loc=(x, y, z + 1.45), chamfer=.04)
    tip = (x + s * math.sin(yaw) * reach, y - math.cos(yaw) * reach, z + 2.2)
    cr.tube([(x, y - .2, z + 1.6), tip], .09, seg=6)
    a.part('Kit_cables', 'Undercarriage').tube([tip, (tip[0], tip[1], z + 1.2)], .015, seg=3)
    a.part('Hazard_marks', 'Hazard').box((.3, .3, .08), loc=(tip[0], tip[1], z + 1.15), bevel=0)


def _plates(a, name, mat, x0, x1, y0, y1, z, n, seed):
    """Flat 5 cm plates, hatches and access covers scattered over a deck or roof (breaks the big flat areas)."""
    if n > 0 and x1 - x0 > .8 and y1 - y0 > .8:
        K.clutter(a, name, mat, x0, x1, y0, y1, z, n, seed=seed, size=(.4, 1.3), height=(.05, .05), gap=.18)


def _house(a, y0, y1, z0, z1, hw0, hw1, rake=.4, cut=.45, aft=0.0, ports=(), doors=(), walls=True):
    """A deckhouse tier (Superstructure) with portholes and doors on both sides; walls=True adds the wall fittings
    (louvres, lockers, a cable tray) between them."""
    N.tier(a.part('Superstructure', 'Team'), y0, y1, z0, z1, hw0, hw1, rake=rake, cut=cut, aft=aft)
    lean = math.atan2(hw0 - hw1, z1 - z0)
    if walls:
        _wall_fittings(a, y0 + cut + .3, y1 - .4, z0, z1, hw0, hw1, lean, list(ports) + list(doors))
    _plates(a, 'Roof_plates', 'Armor', -hw1 + .3, hw1 - .3, y0 + rake + cut + .2, y1 - aft - .3, z1,
            int(2 * hw1 * (y1 - y0) / 3.2), seed=int(abs(y0) * 10 + z1 * 7))
    f = .62
    for s in (-1, 1):
        if ports:
            K.portholes(a, [(s * (hw0 + (hw1 - hw0) * f + .004), y, z0 + (z1 - z0) * f) for y in ports], (s, 0, 0),
                        r=.12)
        if doors:
            h = min(1.7, (z1 - z0) - .35)
            N.doors(a.part('Doors', 'Undercarriage'), s, doors, z0, hw0 - (hw0 - hw1) * ((.05 + h / 2) / (z1 - z0)),
                    h=h, lean=lean)


def _bridge(a, y0, y1, z0, z1, hw0, hw1, rake, n, wing=1.0, wings=(-1, 1), side=()):
    """The bridge tier: the raked window band, side windows, bridge wings with rails and the navigation lights."""
    cut = hw0 * .22
    N.tier(a.part('Superstructure', 'Team'), y0, y1, z0, z1, hw0, hw1, rake=rake, cut=cut, aft=.1)
    glass = a.part('Bridge_glass', 'Glass')
    N.window_band(glass, y0, z0, z1, rake, hw0 - cut - (hw0 - hw1) * .65 - .05, n)
    lean = math.atan2(hw0 - hw1, z1 - z0)
    for s in (-1, 1):
        if side:
            N.side_windows(glass, s, side, z0 + (z1 - z0) * .65, hw0 - (hw0 - hw1) * .65, lean=lean,
                           size=(.55, (z1 - z0) * .22))
    yw = y0 + cut + .55
    for s in wings:
        x = s * (hw0 + wing / 2 - .05)
        k.block(a.part('Bridge_wings', 'Team'), (wing + .1, 1.1, .12), loc=(x, yw, z0 + .06), chamfer=.03)
        xe = s * (hw0 + wing - .1)
        K.railing(a.part('Rails', 'Steel'), [(s * hw0, yw - .5, z0 + .12), (xe, yw - .5, z0 + .12),
                                             (xe, yw + .5, z0 + .12), (s * hw0, yw + .5, z0 + .12)], h=.7, post=.5,
                  r=.018)
        N.nav_lights(a, s, (xe, yw, z0 + .95))


def _ladder(a, x, y, z0, z1, back=.15):
    K.ladder(a.part('Ladders', 'Steel'), (x, y, z0), (x, y - back, z1), width=.45)


# ============================================================================= ASM corvette
def ashm_corvette(a):
    """ashm_corvette: see the module docstring (34 x 6.2 m)."""
    hull = N.Hull(a, 34.0, 6.2, 2.0, 2.85, keel=-1.25, entry=.42, transom=.88, rake=1.7, bulwark=(.17, .55))
    hull.build(team_band=(-4.5, 7.5, .35, .3), portholes=(-11.5, -10.5, -9.5, 11.0, 12.0))
    d = hull.dz
    N.anchor_gear(a, hull, -14.3)
    _breakwater(a, hull, -12.9, w=1.1, h=.55)
    # The quad canister bank on the foredeck, mouths up and forward.
    e, ln, r = .2, 5.4, .46
    zr = d(-12.2 + ln * math.cos(e)) + .45
    mz = zr + r + (2 * r + .08) / 2 + ln * math.sin(e)
    N.canister_bank(a, (0, -12.2, mz), 2, 2, ln, r, e, frame_z=d(-9.0))
    # The forward house, the bridge, the mast tier, the pyramid mast and radar.
    _house(a, -6.2, 3.4, d(-6.2) - .05, 4.35, 2.3, 2.18, rake=.5, cut=.5, ports=(-4.6, -3.6, 1.0, 2.0),
           doors=(-2.5, 2.7))
    _bridge(a, -5.6, -.8, 4.35, 6.25, 1.85, 1.62, .65, 6, side=(-4.4, -3.6, -2.8))
    N.tier(a.part('Superstructure', 'Team'), -3.9, -1.5, 6.25, 7.15, 1.05, .9, rake=.2, cut=.25)
    top = N.mast(a, (0, -2.7, 7.15), 1.8, 1.25, .7, lattice=1.1, yard=2.8)
    N.radar(a, top, 'bar', w=2.2)
    N.funnel(a, (0, .6, 4.35), 1.4, 1.7, 1.3)
    N.director(a, (0, 2.75, 4.35), r=.45, facing=(0, 1, 0))
    N.rhib_davit(a, (-2.6, 1.4, 4.55), -1, length=3.0, beam=1.3, deck=4.35)
    N.life_rafts(a, [(1.65, y, 4.62) for y in (-.2, .9, 2.0)])
    # The waist: decoy launchers on the deck edges, ladders up to the house roofs.
    N.decoys(a, [(s * (hull.hb(4.7) - .55), 4.7, d(4.7)) for s in (-1, 1)], (0, 4.7, d(4.7) + .6))
    for s in (-1, 1):
        _ladder(a, s * 1.4, 3.55, d(3.5), 4.35, back=-.15)
        _ladder(a, s * 1.3, 5.85, d(5.9), 3.55)
    # The after house with the AK-630 (Mount_mg).
    _house(a, 6.0, 11.0, d(8.5) - .05, 3.55, 1.9, 1.8, rake=.3, cut=.35, ports=(7.5, 9.6), doors=(8.5,))
    N.ak630(a, (0, 9.0, 3.55), base=.6, sc=1.15)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.6, 10.6, 3.55), h=2.4, r=.025, lean=.06)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.6, 10.6, 3.55), h=2.0, r=.025, lean=.06)
    _vents(a, [(1.3, -1.3, 4.35, .6), (-1.2, 3.0, 4.35, .5)])
    N.rails(a, hull, -15.8, -6.6, n=6)
    _crane(a, (-2.0, 12.0, d(12.0)), -1, reach=3.0, yaw=.25)
    _quarterdeck(a, hull, 11.2, seed=71)
    for s in (-1, 1):
        N.life_rafts(a, [(s * (hull.hb(y) - .35), y, d(y) + .3) for y in (12.2, 13.2)])
    _deck_paint(a, hull, [(-6.0, 3.4), (3.6, 6.0), (11.2, 16.0)], hatches=((0, -14.8), (1.0, 12.4), (-1.0, 15.2)))
    _staffs(a, hull)
    _finish(a)


# ============================================================================= AA corvette
def aa_corvette(a):
    """aa_corvette: see the module docstring (33 x 6.2 m)."""
    hull = N.Hull(a, 33.0, 6.2, 2.0, 2.75, keel=-1.2, entry=.44, transom=.9, rake=1.5, bulwark=(.15, .5))
    hull.build(team_band=(-5.0, 7.0, .35, .3), portholes=(-11.0, -10.0, 10.5, 11.5))
    d = hull.dz
    N.anchor_gear(a, hull, -13.8)
    # The 8-cell trainable box on its barbette where a corvette's gun would be.
    k.lathe(a.part('Sam_magazine', 'Armor'), [(1.45, 0), (1.45, .5), (1.3, .65), (0, .65)],
            loc=(0, -9.6, d(-9.6) - .05), seg=20, worn=(2,))
    N.sam_box(a, (0, -9.6, d(-9.6) + .6), cols=4, rows=2, cell=.42, length=3.2, elev=.24, sc=1.1)
    _house(a, -6.5, 3.2, d(-6.5) - .05, 4.3, 2.3, 2.18, rake=.5, cut=.55, ports=(-4.8, -3.8, 1.2, 2.2),
           doors=(-2.6, 2.4))
    _bridge(a, -5.9, -1.0, 4.3, 6.15, 1.85, 1.62, .65, 6, wings=(1,), side=(-4.9, -4.1, -3.3))
    # The starboard wing is the M2's platform (Mount_mg_02).
    k.block(a.part('Bridge_wings', 'Team'), (1.4, 1.6, .14), loc=(-2.45, -4.9, 4.37), chamfer=.03)
    N.hmg_tub(a, (-2.6, -4.9, 4.44), tag='02', r=.55)
    N.tier(a.part('Superstructure', 'Team'), -4.6, -1.8, 6.15, 7.2, 1.15, 1.0, rake=.2, cut=.25)
    top = N.mast(a, (0, -3.2, 7.2), 2.0, 1.4, .75, lattice=1.2, yard=3.0)
    N.radar(a, top, 'twin', w=2.0)
    for s in (-1, 1):
        N.director(a, (s * 1.25, -.3, 4.3), r=.5, facing=(s * .35, -1, 0))
    N.decoys(a, [(s * 1.85, 2.2, 4.3) for s in (-1, 1)], (0, 2.2, 4.55))
    N.funnel(a, (0, 1.2, 4.3), 1.4, 1.7, 1.3)
    N.director(a, (0, 2.85, 4.3), r=.42, facing=(0, 1, 0))
    # The waist: the RHIB in its davit to port, ladders.
    N.rhib_davit(a, (2.05, 4.6, d(4.6) + .55), 1, length=2.8, beam=1.2, deck=d(4.6))
    for s in (-1, 1):
        _ladder(a, s * 1.2, 3.35, d(3.3), 4.3, back=-.15)
    _house(a, 6.0, 10.6, d(8.3) - .05, 3.5, 1.9, 1.8, rake=.3, cut=.35, ports=(7.4, 9.4), doors=(8.4,))
    N.ak630(a, (0, 8.6, 3.5), base=.6, sc=1.15)
    N.life_rafts(a, [(s * 1.95, y, 3.75) for s in (-1, 1) for y in (6.9, 7.9)])
    _crane(a, (-2.0, 11.6, d(11.6)), -1, reach=2.8, yaw=.25)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.6, 10.3, 3.5), h=2.4, r=.025, lean=.06)
    _vents(a, [(-1.2, -.3, 4.3, .5), (-1.4, 5.2, d(5.2), .6)])
    N.rails(a, hull, -15.2, -6.9, n=6)
    _quarterdeck(a, hull, 10.8, seed=72)
    _deck_paint(a, hull, [(-6.3, 3.2), (3.3, 6.0), (10.8, 15.5)], hatches=((0, -12.6), (-1.0, 12.0), (1.0, 14.8)))
    _staffs(a, hull)
    _finish(a)


# ============================================================================= CIWS escort
def ciws_escort_ship(a):
    """ciws_escort_ship: see the module docstring (26 x 5.4 m)."""
    hull = N.Hull(a, 26.0, 5.4, 1.8, 2.5, keel=-1.05, entry=.44, transom=.9, rake=1.2, bulwark=(.16, .5))
    hull.build(team_band=(-4.0, 6.0, .3, .28), portholes=(-8.5, -7.6, 8.6))
    d = hull.dz
    N.anchor_gear(a, hull, -10.8, spread=.6)
    N.gun_76(a, (0, -7.3, d(-7.3)))
    _breakwater(a, hull, -9.7, w=.85, h=.45)
    _house(a, -5.0, 5.6, d(-5.0) - .05, 3.95, 2.0, 1.9, rake=.45, cut=.45, ports=(-3.5, -2.5, 3.2, 4.2),
           doors=(-.9, 4.9))
    _bridge(a, -4.5, -.9, 3.95, 5.55, 1.5, 1.32, .55, 5, wing=.8, side=(-3.6, -2.8, -2.0))
    # The two beam CIWS on sponsons abreast the funnel (Mount_mg_02 port, Mount_mg_03 starboard).
    for s, tag in ((1, '02'), (-1, '03')):
        k.block(a.part('Bridge_wings', 'Team'), (1.5, 1.7, .16), loc=(s * 1.85, 1.0, 4.03), chamfer=.04)
        N.ak630(a, (s * 1.8, 1.0, 4.1), tag=tag, base=.35)
    top = N.mast(a, (0, -2.6, 5.55), 1.6, 1.1, .6, lattice=1.0, yard=2.4)
    N.radar(a, top, 'bar', w=1.9)
    for s in (-1, 1):
        N.director(a, (s * .85, -1.6, 5.55), r=.36, facing=(s * .6, -1, 0))
    N.funnel(a, (0, 3.2, 3.95), 1.2, 1.5, 1.1)
    N.director(a, (0, 5.0, 3.95), r=.36, facing=(0, 1, 0))
    N.decoys(a, [(s * 1.5, y, 3.95) for s in (-1, 1) for y in (2.6, 4.4)], (0, 3.4, 4.2))
    # The after house with the third CIWS (Mount_mg).
    _house(a, 5.6, 9.2, d(7.4) - .05, 3.05, 1.7, 1.6, rake=.25, cut=.3, ports=(6.6, 8.4))
    N.ak630(a, (0, 7.5, 3.05), base=.55)
    for s in (-1, 1):
        _ladder(a, s * 1.2, 5.75, d(5.7), 3.95, back=-.15)
    # The RHIB in its chocks on the quarterdeck, life rafts, the stern gear.
    K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (0, 10.8, d(10.8) + .2), length=2.6, beam=1.1)
    for dy in (-.7, .7):
        a.part('Davits', 'Steel').box((1.0, .15, .2), loc=(0, 10.8 + dy, d(10.8) + .1), bevel=0)
    N.life_rafts(a, [(s * (hull.hb(y) - .35), y, d(y) + .3) for s in (-1, 1) for y in (9.8, 10.8)])
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.4, 8.8, 3.05), h=2.0, r=.022, lean=.06)
    N.rails(a, hull, -12.2, -5.3, n=5)
    _quarterdeck(a, hull, 9.4, seed=73, n=4)
    _deck_paint(a, hull, [(-4.8, 5.6), (9.4, 12.0)], hatches=((0, -10.0), (0, 12.2)))
    _staffs(a, hull, jack=1.1, ensign=1.5)
    _finish(a)


# ============================================================================= EW corvette
def ew_corvette(a):
    """ew_corvette: see the module docstring (32 x 6.0 m)."""
    hull = N.Hull(a, 32.0, 6.0, 1.95, 2.7, keel=-1.2, entry=.43, transom=.9, rake=1.5, bulwark=(.16, .5))
    hull.build(team_band=(-5.0, 6.5, .35, .3), portholes=(-10.5, -9.6, 10.0, 11.0))
    d = hull.dz
    N.anchor_gear(a, hull, -13.4)
    N.gun_76(a, (0, -10.0, d(-10.0)))
    _breakwater(a, hull, -12.2, w=1.0, h=.5)
    _house(a, -7.0, 5.0, d(-7.0) - .05, 4.25, 2.25, 2.12, rake=.5, cut=.5, ports=(-5.0, -4.0, 2.4, 3.4),
           doors=(-3.0, 1.0))
    _bridge(a, -6.4, -1.8, 4.25, 6.1, 1.8, 1.6, .65, 6, side=(-5.4, -4.6, -3.8))
    # The enclosed EW mast: ESM / jammer arrays on its faces, crowned by a jammer dome (no radar dish).
    mx, my, mz = 0, -4.0, 6.1
    k.extrude(a.part('Mast', 'Team'), [(-.8, -.8), (.8, -.8), (.8, .8), (-.8, .8)], 3.0, loc=(mx, my, mz + 1.5),
              axis='Z', chamfer=.04, corner=.08, taper=(.55, .55))
    arrays = a.part('Jammer_arrays', 'Undercarriage')
    for nx, ny in ((0, -1), (1, 0), (-1, 0), (0, 1)):
        arrays.box((.7, .7, .04), loc=(mx + nx * .73, my + ny * .73, mz + .95), rot=K.rot_to((nx, ny, .15)), bevel=0)
        arrays.box((.5, .5, .04), loc=(mx + nx * .55, my + ny * .55, mz + 2.05), rot=K.rot_to((nx, ny, .15)), bevel=0)
    dome = a.part('Jammer_dome', 'Medical')
    dome.cyl(.25, .3, loc=(mx, my, mz + 3.15), seg=12, bevel=0)
    dome.sphere(.6, loc=(mx, my, mz + 3.8), seg=16, rings=10)
    st = a.part('Mast_steel', 'Steel')
    st.box((3.0, .07, .07), loc=(mx, my, mz + 2.45), bevel=0)
    for s in (-1, 1):
        dome.sphere(.28, loc=(mx + s * 1.35, my, mz + 2.8), seg=12, rings=8)
        st.cyl(.04, .3, loc=(mx + s * 1.35, my, mz + 2.55), seg=6, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (mx, my, mz + 4.4), h=1.0, r=.02)
    # The jammer tower amidships: a drum on the house roof, the big radome, side arrays.
    k.lathe(a.part('Deckhouse', 'Team'), [(1.2, 0), (1.2, 1.3), (1.0, 1.5), (0, 1.5)], loc=(0, 1.8, 4.25), seg=18,
            worn=(1,))
    dome.sphere(1.35, loc=(0, 1.8, 6.95), seg=20, rings=12)
    dome.cyl(1.25, .12, loc=(0, 1.8, 5.81), seg=20, bevel=0)
    for s in (-1, 1):
        arrays.box((.05, 1.5, 1.0), loc=(s * 1.22, 1.8, 4.95), rot=(0, s * -.1, 0), bevel=0)
    N.funnel(a, (0, 3.9, 4.25), 1.3, 1.2, 1.0)
    N.rhib_davit(a, (-1.6, -.4, 4.45), -1, length=2.6, beam=1.2, deck=4.25)
    N.life_rafts(a, [(1.75, y, 4.52) for y in (-1.0, .1)])
    for s in (-1, 1):
        _ladder(a, s * 1.3, 5.15, d(5.1), 4.25, back=-.15)
    # The after house with the Mistral pedestal (Mount_missile).
    _house(a, 6.6, 10.4, d(8.5) - .05, 3.35, 1.85, 1.75, rake=.3, cut=.35, ports=(7.6, 9.4), doors=(8.5,))
    N.sam_pedestal(a, (0, 8.6, 3.35), tubes=4, sc=1.15)
    _vents(a, [(1.3, 4.2, 4.25, .5), (-1.3, 4.2, 4.25, .5)])
    N.rails(a, hull, -14.8, -7.3, n=6)
    _quarterdeck(a, hull, 10.6, seed=74)
    _deck_paint(a, hull, [(-6.8, 5.0), (5.1, 6.6), (10.6, 15.0)], hatches=((0, -12.8), (1.0, 11.8), (-1.0, 14.6)))
    _staffs(a, hull)
    _finish(a)


# ============================================================================= frigate
def frigate(a):
    """frigate: see the module docstring (42 x 7.4 m)."""
    hull = N.Hull(a, 42.0, 7.4, 2.2, 3.15, keel=-1.5, entry=.42, transom=.88, rake=2.0, bulwark=(.17, .6))
    hull.build(team_band=(-8.0, 10.0, .4, .34), portholes=(-15.5, -14.5, -13.5, 14.0, 15.0, 16.0))
    d = hull.dz
    N.anchor_gear(a, hull, -17.8, spread=.85)
    N.gun_100(a, (0, -13.4, d(-13.4)), sc=1.1)
    _breakwater(a, hull, -16.6, w=1.3, h=.6)
    _house(a, -10.0, 9.0, d(-10.0) - .05, 4.75, 2.75, 2.6, rake=.55, cut=.65,
           ports=(-8.0, -7.0, -1.5, -.5, 3.0, 4.0, 7.5), doors=(-5.0, 1.0, 6.0))
    _bridge(a, -9.4, -3.6, 4.75, 6.75, 2.2, 1.95, .7, 7, side=(-8.3, -7.4, -6.5, -5.6))
    N.tier(a.part('Superstructure', 'Team'), -7.8, -4.6, 6.75, 7.8, 1.3, 1.1, rake=.25, cut=.3)
    top = N.mast(a, (0, -6.2, 7.8), 2.0, 1.5, .8, lattice=1.2, yard=3.4)
    N.radar(a, top, 'big', w=2.6)
    N.director(a, (0, -4.0, 6.75), r=.5, facing=(0, -1, 0))
    # Two AShM canisters amidships, angled outboard either side (one Mount_missile between them).
    e, ln, r = .2, 3.8, .42
    mz = 4.75 + r + .3 + ln * math.sin(e)
    for s in (-1, 1):
        N.canister_bank(a, (s * 2.4, -2.6, mz), 1, 1, ln, r, e, yaw=s * -.6, frame_z=4.75, caps='Canister_caps',
                        pivot=False)
    m = a.pivot('Mount_missile', (0, -2.6, mz))
    a.pivot('Muzzle_missile', (0, 0, 0), m)
    N.funnel(a, (0, 2.1, 4.75), 1.9, 2.1, 1.5)
    # The after house: the SHORAD pedestal (Mount_missile_02), its director, the RHIBs either side; decoys.
    N.tier(a.part('Superstructure', 'Team'), 3.8, 8.7, 4.75, 5.95, 1.7, 1.6, rake=.2, cut=.3)
    N.sam_pedestal(a, (0, 6.7, 5.95), slot='missile', tag='02', tubes=4, sc=1.15)
    N.director(a, (0, 4.5, 5.95), r=.42, facing=(0, -1, 0))
    for s in (-1, 1):
        N.rhib_davit(a, (s * 2.45, 6.1, 4.95), s, length=3.4, beam=1.3, deck=4.75)
    N.decoys(a, [(s * 2.3, 1.7, 4.75) for s in (-1, 1)], (0, 1.7, 5.0))
    # The quarterdeck house with the AK-630 (Mount_mg), the decoy-towing winch aft.
    _house(a, 9.0, 13.0, d(11.0) - .05, 3.75, 2.2, 2.1, rake=.25, cut=.35, ports=(10.0, 12.0))
    N.ak630(a, (0, 11.2, 3.75), base=.72, sc=1.15)
    for s in (-1, 1):
        _ladder(a, s * 1.6, 9.15, 3.75, 4.75, back=-.15)
        _ladder(a, s * 1.5, 13.15, d(13.2), 3.75, back=-.15)
    k.lathe(a.part('Winch', 'Steel'), [(.55, -.6), (.55, -.5), (.35, -.45), (.35, .45), (.55, .5), (.55, .6)],
            loc=(0, 18.4, d(18.4) + .6), rot=(0, R90, 0), seg=14)
    a.part('Winch', 'Steel').box((1.5, .9, .3), loc=(0, 18.4, d(18.4) + .15), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (2.3, 8.4, 4.75), h=3.0, r=.028, lean=.05)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.3, 8.4, 4.75), h=2.6, r=.028, lean=.05)
    _vents(a, [(1.7, -1.2, 4.75, .6), (-1.0, -4.6, 6.75, .5)])
    N.rails(a, hull, -19.6, -10.3, n=7)
    _quarterdeck(a, hull, 13.2, seed=75, n=10)
    for s in (-1, 1):
        N.life_rafts(a, [(s * (hull.hb(y) - .35), y, d(y) + .3) for y in (14.0, 15.1, 16.2)])
    _deck_paint(a, hull, [(-9.8, 9.0), (13.2, 20.0)], hatches=((0, -17.0), (1.2, 15.0), (-1.2, 19.6)))
    _staffs(a, hull, jack=1.5, ensign=2.0)
    _finish(a)


# ============================================================================= missile frigate
def missile_frigate(a):
    """missile_frigate: see the module docstring (44 x 7.6 m)."""
    hull = N.Hull(a, 44.0, 7.6, 2.2, 3.2, keel=-1.5, entry=.4, transom=.88, rake=2.1, bulwark=(.14, .55))
    hull.build(team_band=(-6.5, 10.5, .4, .34), portholes=(-17.5, -16.5, 15.0, 16.0))
    d = hull.dz
    N.anchor_gear(a, hull, -19.3, spread=.85)
    _breakwater(a, hull, -17.6, w=1.35, h=.65)
    # The dominant six-cell bank on the foredeck (3 x 2 big canisters), on its raised plinth.
    e, ln, r = .17, 6.4, .48
    y_m = -16.4
    yr = y_m + ln * math.cos(e)
    plinth = d(yr) + .35
    k.block(a.part('Deck_gear', 'Armor'), (3.6, ln * .9, .4), loc=(0, (y_m + yr) / 2, plinth - .2), chamfer=.06)
    mz = plinth + .4 + r + (2 * r + .08) / 2 + ln * math.sin(e)
    N.canister_bank(a, (0, y_m, mz), 3, 2, ln, r, e, frame_z=plinth, caps='Canister_caps')
    _house(a, -8.6, 10.4, d(-8.6) - .05, 4.8, 2.8, 2.65, rake=.6, cut=.7,
           ports=(-6.5, -5.5, 0.0, 1.0, 4.0, 5.0, 8.0), doors=(-4.0, 2.6, 7.0))
    _bridge(a, -8.0, -2.6, 4.8, 6.8, 2.25, 2.0, .7, 7, side=(-6.9, -6.0, -5.1, -4.2))
    N.tier(a.part('Superstructure', 'Team'), -6.4, -3.6, 6.8, 7.8, 1.35, 1.15, rake=.25, cut=.3)
    top = N.mast(a, (0, -5.0, 7.8), 2.0, 1.5, .8, lattice=1.2, yard=3.4)
    N.radar(a, top, 'twin', w=2.3)
    for s in (-1, 1):
        N.director(a, (s * 1.55, -1.9, 4.8), r=.5, facing=(s * .3, -1, 0))
    N.funnel(a, (0, 1.2, 4.8), 1.8, 2.1, 1.5)
    # The after house: the RAM-type box (Mount_missile_02) and the AK-630 (Mount_mg); RHIBs either side; decoys.
    N.tier(a.part('Superstructure', 'Team'), 3.6, 9.6, 4.8, 6.0, 1.75, 1.65, rake=.2, cut=.3)
    N.ram_box(a, (0, 5.0, 6.0), tag='02', sc=1.15)
    N.ak630(a, (0, 8.4, 6.0), base=.3, sc=1.15)
    N.director(a, (0, 3.05, 4.8), r=.4, facing=(0, -1, 0))
    for s in (-1, 1):
        N.rhib_davit(a, (s * 2.45, 6.8, 5.0), s, length=3.4, beam=1.3, deck=4.8)
    N.decoys(a, [(s * 2.35, .6, 4.8) for s in (-1, 1)], (0, .6, 5.05))
    # The quarterdeck: the 76 mm on its tall barbette right aft (Mount_gun), the afterthought.
    k.lathe(a.part('Deck_gear', 'Armor'), [(1.5, 0), (1.5, 1.45), (1.35, 1.6), (0, 1.6)], loc=(0, 16.7, d(16.7) - .05),
            seg=20, worn=(2,))
    N.gun_76(a, (0, 16.7, d(16.7) + 1.55))
    for s in (-1, 1):
        _ladder(a, s * 1.9, 10.55, d(10.6), 4.8, back=-.15)
    K.whip_antenna(a.part('Antennas', 'Steel'), (2.4, 9.8, 4.8), h=3.0, r=.028, lean=.05)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.4, 9.8, 4.8), h=2.6, r=.028, lean=.05)
    _vents(a, [(1.6, -1.0, 4.8, .5), (-1.0, -3.4, 6.8, .5)])
    N.rails(a, hull, -21.0, -9.0, n=8)
    for s in (-1, 1):
        K.railing(a.part('Rails', 'Steel'), [hull.edge(y, s, inset=.08) for y in (11.0, 14.0, 17.0, 21.6)], h=.9,
                  post=1.2, r=.022)
        N.life_rafts(a, [(s * (hull.hb(y) - .35), y, d(y) + .3) for y in (11.6, 12.7, 13.8)])
    fit = a.part('Deck_fittings', 'Steel')
    N.bollards(fit, [(s * (hull.hb(y) - .45), y, d(y)) for s in (-1, 1) for y in (14.6, 20.6)])
    K.clutter(a, 'Deck_lockers', 'Armor', -1.6, 1.6, 10.9, 14.4, d(12.5), 8, seed=77, size=(.3, .9), height=(.25, .7))
    _deck_paint(a, hull, [(-8.4, 10.4), (10.6, 21.0)], hatches=((0, -19.9), (1.3, 14.6), (-1.3, 19.4)))
    _staffs(a, hull, jack=1.5, ensign=2.0)
    _finish(a)


# ============================================================================= AA frigate
def aa_frigate(a):
    """aa_frigate: see the module docstring (43 x 7.5 m)."""
    hull = N.Hull(a, 43.0, 7.5, 2.2, 3.2, keel=-1.5, entry=.42, transom=.88, rake=2.0, bulwark=(.15, .6))
    hull.build(team_band=(-8.0, 10.0, .4, .34), portholes=(-17.0, -16.0, 14.5, 15.5))
    d = hull.dz
    N.anchor_gear(a, hull, -18.6, spread=.85)
    # The twin-arm area SAM on its magazine barbette: the biggest system on the hull.
    N.twin_arm_sam(a, (0, -13.4, d(-13.4) - .05), mag_r=2.15, length=4.4, sc=1.1)
    _house(a, -9.6, 9.2, d(-9.6) - .05, 4.75, 2.75, 2.6, rake=.55, cut=.65,
           ports=(-7.6, -6.6, 2.6, 3.6, 7.6), doors=(-5.0, 4.4))
    _bridge(a, -9.0, -3.2, 4.75, 6.75, 2.2, 1.95, .7, 7, side=(-7.9, -7.0, -6.1, -5.2))
    N.tier(a.part('Superstructure', 'Team'), -7.6, -4.2, 6.75, 8.0, 1.4, 1.2, rake=.25, cut=.3)
    top = N.mast(a, (0, -5.9, 8.0), 2.2, 1.6, .85, lattice=1.3, yard=3.6)
    N.radar(a, top, 'big', w=3.0)
    for s in (-1, 1):
        N.director(a, (s * 1.4, -3.75, 6.75), r=.48, facing=(s * .3, -1, 0))
    # Amidships: the AK-630 on its raised platform (Mount_mg), the funnel, the after house with the aft illuminator.
    k.lathe(a.part('Deckhouse', 'Team'), [(1.15, 0), (1.15, .9), (1.0, 1.05), (0, 1.05)], loc=(0, -.4, 4.75), seg=16,
            worn=(1,))
    N.ak630(a, (0, -.4, 5.8), base=.35, sc=1.15)
    N.funnel(a, (0, 2.6, 4.75), 1.9, 2.3, 1.5)
    N.tier(a.part('Superstructure', 'Team'), 4.8, 9.0, 4.75, 5.95, 1.75, 1.65, rake=.2, cut=.3)
    N.director(a, (0, 7.5, 5.95), r=.55, facing=(0, 1, 0))
    K.whip_antenna(a.part('Antennas', 'Steel'), (.9, 5.6, 5.95), h=2.4, r=.025, lean=.05)
    N.rhib_davit(a, (3.35, 6.7, 4.95), 1, length=3.4, beam=1.3, deck=4.75)
    N.life_rafts(a, [(-2.3, y, 5.05) for y in (5.4, 6.3, 7.2, 8.1)])
    k.block(a.part('Deck_gear', 'Armor'), (.8, 1.6, 1.0), loc=(-2.2, 2.9, 5.25), chamfer=.05)
    for s in (-1, 1):
        _ladder(a, s * 1.9, 9.35, d(9.4), 4.75, back=-.15)
    N.decoys(a, [(s * 2.35, 1.0, 4.75) for s in (-1, 1)], (0, 1.0, 5.0))
    # Aft only: the 76 mm on its quarterdeck barbette (Mount_gun).
    k.lathe(a.part('Deck_gear', 'Armor'), [(1.45, 0), (1.45, .9), (1.3, 1.05), (0, 1.05)],
            loc=(0, 15.0, d(15.0) - .05), seg=18, worn=(2,))
    N.gun_76(a, (0, 15.0, d(15.0) + 1.0))
    _vents(a, [(1.7, -2.6, 4.75, .6), (-1.7, -2.6, 4.75, .6), (1.0, -4.5, 6.75, .4)])
    N.rails(a, hull, -20.3, -9.9, n=7)
    _crane(a, (-2.3, 11.0, d(11.0)), -1, reach=3.6, yaw=.3)
    _quarterdeck(a, hull, 16.7, seed=76, n=5)
    for s in (-1, 1):
        N.life_rafts(a, [(s * (hull.hb(y) - .35), y, d(y) + .3) for y in (10.4, 11.5, 12.6)])
    K.clutter(a, 'Deck_lockers', 'Armor', -.6, 2.4, 9.8, 13.4, d(11.5), 7, seed=78, size=(.3, .9), height=(.25, .7))
    _deck_paint(a, hull, [(-9.4, 9.2), (9.4, 20.5)], hatches=((0, -17.4), (1.3, 13.0), (-1.3, 19.6)))
    _staffs(a, hull, jack=1.5, ensign=2.0)
    _finish(a)


# ============================================================================= rocket artillery ship
def rocket_artillery_ship(a):
    """rocket_artillery_ship: see the module docstring (38 x 7.0 m)."""
    hull = N.Hull(a, 38.0, 7.0, 1.9, 2.6, keel=-1.0, entry=.34, transom=.95, flare=.15, rake=1.1, sheer_from=.36,
                  bulwark=(.2, .7))
    hull.build(team_band=(-10.0, 15.0, .3, .3), portholes=(10.0, 11.0, 12.0, 13.0))
    d = hull.dz
    N.anchor_gear(a, hull, -15.6, spread=.8)
    # The bare M2 tub on the forecastle (Mount_mg).
    N.hmg_tub(a, (0, -13.4, d(-13.4)), r=.65)
    # Blast plating round the launcher and the deflector screen ahead of the bridge.
    blast = a.part('Blast_plates', 'Steel')
    for i in range(6):
        y = -6.6 + i * 1.8
        blast.box((5.6, 1.7, .03), loc=(0, y, d(y) + .03), bevel=0)
    k.block(a.part('Deck_gear', 'Armor'), (5.4, .25, 1.4), loc=(0, 6.8, d(6.8) + .7), chamfer=.04)
    # The rocket battery amidships on its training barbette (Mount_rocket): the single dominant feature.
    N.rocket_battery(a, (0, -1.0, d(-1.0)), elev=.4, pod=(1.0, 4.4, .8), sc=1.2)
    # Reload pods on their deck racks and the reload crane.
    stacks = a.part('Pod_stacks', 'Armor')
    for s in (-1, 1):
        for j in range(2):
            k.block(stacks, (1.0, 4.4, .78), loc=(s * 2.0, -10.0 + 0.0, d(-10.0) + .5 + j * .82), chamfer=.04)
        a.part('Hazard_marks', 'Hazard').box((1.02, .12, 1.6), loc=(s * 2.0, -12.0, d(-12.0) + .9), bevel=0)
        a.part('Rails', 'Steel').box((1.3, .2, .1), loc=(s * 2.0, -8.3, d(-8.3) + .05), bevel=0)
        a.part('Rails', 'Steel').box((1.3, .2, .1), loc=(s * 2.0, -11.7, d(-11.7) + .05), bevel=0)
    cr = a.part('Crane', 'CraneYellow')
    k.lathe(cr, [(.45, 0), (.45, 1.6), (.35, 1.7), (0, 1.7)], loc=(2.4, 4.4, d(4.4)), seg=12)
    cr.tube([(2.4, 4.4, d(4.4) + 1.5), (2.75, 7.9, d(4.4) + 3.0)], .14, seg=6)
    k.block(cr, (.7, .9, .7), loc=(2.4, 4.6, d(4.4) + 1.95), chamfer=.05)
    a.part('Kit_cables', 'Undercarriage').tube([(2.75, 7.9, d(4.4) + 2.95), (2.75, 7.9, d(4.4) + 1.6)], .02, seg=3)
    # The bridge aft, coaster style: the main house, the wheelhouse, the mast with its navigation radar, two funnels.
    sup = a.part('Superstructure', 'Team')
    z0 = d(8.6) - .05
    N.tier(sup, 8.6, 16.6, z0, 4.2, 2.9, 2.8, rake=.4, cut=.6, cut_aft=.3)
    N.tier(sup, 9.0, 13.4, 4.2, 6.0, 2.3, 2.1, rake=.6, cut=.55, aft=.1)
    glass = a.part('Bridge_glass', 'Glass')
    N.window_band(glass, 9.0, 4.2, 6.0, .6, 1.7, 7)
    for s in (-1, 1):
        N.side_windows(glass, s, (10.0, 10.9, 11.8), 5.3, 2.2, lean=.11, size=(.6, .4))
        k.block(a.part('Bridge_wings', 'Team'), (1.0, 1.4, .14), loc=(s * 2.75, 9.8, 4.27), chamfer=.03)
        K.railing(a.part('Rails', 'Steel'), [(s * 2.3, 9.1, 4.34), (s * 3.2, 9.1, 4.34), (s * 3.2, 10.5, 4.34)], h=.7,
                  post=.6, r=.02)
        N.nav_lights(a, s, (s * 3.2, 9.8, 5.1))
        N.doors(a.part('Doors', 'Undercarriage'), s, (9.4, 14.6), z0, 2.88, lean=.02)
        K.ladder(a.part('Ladders', 'Steel'), (s * 1.7, 8.4, d(8.4)), (s * 1.7, 8.55, 4.2), width=.45)
        N.funnel(a, (s * 1.6, 14.6, 4.2), 1.0, 1.4, 1.6, caps=1)
    top = N.mast(a, (0, 11.6, 6.0), 1.2, .8, .45, lattice=1.2, yard=3.0)
    N.radar(a, top, 'nav', w=1.8)
    N.director(a, (0, 12.9, 6.0), r=.42, facing=(0, -1, 0), part='Fire_control')
    N.rhib_davit(a, (0, 15.0, 4.45), 1, length=3.0, beam=1.3, deck=4.2)
    N.life_rafts(a, [(s * 2.45, y, 4.47) for s in (-1, 1) for y in (13.9, 15.0)])
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.0, 13.0, 6.0), h=2.4, r=.025, lean=.05)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.0, 13.0, 6.0), h=2.0, r=.025, lean=.05)
    _vents(a, [(1.5, 16.0, 4.2, .6), (-1.5, 16.0, 4.2, .6)])
    N.rails(a, hull, -17.2, 8.2, n=12)
    fit = a.part('Deck_fittings', 'Steel')
    N.bollards(fit, [(s * (hull.hb(y) - .45), y, d(y)) for s in (-1, 1) for y in (-14.5, -9.0, 7.6, 17.6)])
    for s in (-1, 1):
        K.railing(a.part('Rails', 'Steel'), [hull.edge(y, s, inset=.08) for y in (16.8, 18.9)] +
                  [(s * .5, 18.92, d(18.9))], h=.9, post=1.1, r=.022)
    _deck_paint(a, hull, [(-14.0, 8.4), (16.8, 18.5)], hatches=((0, -16.2), (1.4, 7.2), (-1.4, 17.8)))
    _staffs(a, hull, jack=1.3, ensign=1.8)
    _finish(a)


BUILDERS = {
    'torpedo_boat': (torpedo_boat, dict(ao_distance=.8, grime_height=.4)),
    'ashm_corvette': (ashm_corvette, dict(ao_distance=1.2, grime_height=.5)),
    'aa_corvette': (aa_corvette, dict(ao_distance=1.2, grime_height=.5)),
    'ciws_escort_ship': (ciws_escort_ship, dict(ao_distance=1.1, grime_height=.5)),
    'ew_corvette': (ew_corvette, dict(ao_distance=1.2, grime_height=.5)),
    'frigate': (frigate, dict(ao_distance=1.3, grime_height=.6)),
    'missile_frigate': (missile_frigate, dict(ao_distance=1.3, grime_height=.6)),
    'aa_frigate': (aa_frigate, dict(ao_distance=1.3, grime_height=.6)),
    'rocket_artillery_ship': (rocket_artillery_ship, dict(ao_distance=1.3, grime_height=.6)),
}
