"""Naval models lane B (06/10 owner prompt; Docs/naval/MODEL_CONTRACT.md, DECISIONS "## Naval models (lane B)"): the
eight big new hulls, each its own builder on the lane's kit (mb_naval_b_kit), drawn from a real type at game scale:

- destroyer (Arleigh Burke): Mk 45 Mod 4 forward, forward and aft VLS fields (AShM / SAM), the faceted deckhouse with
  the four octagonal arrays, the raked mast, two square stacks, Phalanx fore and aft, the flight deck.
- gun_destroyer (Spruance / Kidd): two rounded Mk 45 Mod 2 fore and aft, the tall boxy deckhouse, the offset stacks
  and two lattice masts, the hangar with the Mk 29 Sea Sparrow box and one Phalanx on its roof.
- missile_destroyer (Type 055 read): a 100 mm stealth gun, the big raised eight-cell VLS block forward of the bridge,
  the integrated stealth tower with its four flat arrays, the wide funnel, two Type 1130, the RAM-type box aft.
- aa_destroyer (Ticonderoga baseline 1): the Mk 26 twin-arm with two big SAMs forward, the Aegis arrays fore and aft,
  the aft VLS field, a Mk 45 aft only, two Phalanx abeam.
- heavy_monitor (Erebus / Roberts): the wide low hull with anti-torpedo bulges and an armoured deck, one heavy turret
  forward on a tall barbette, the tripod with its director top, one tall funnel, a Phalanx aft.
- battlecruiser (Alaska, modernised): the long sheered hull, a twin 254 mm turret forward (two muzzles), the
  four-cell inclined anti-ship deck, the tower bridge with the conning tower, one trunk funnel, two Phalanx on
  sponsons, the Mk 26 aft.
- battleship (Iowa 1980s): three triple 406 mm turrets (two forward superfiring, one aft; barrels pass 06/10: three
  barrels a turret, Muzzle_b1..3_gun[_NN], all fire in one volley), the conning tower and tower
  bridge, two stacks, the tripod foremast, the Mk 29 box, two Phalanx, the helicopter fantail.
- missile_cruiser (Kirov read): the S-300F revolver hatches in the bow, the eight-cell inclined Granit deck, the
  pyramid superstructure with the Top Pair radar, the twin-uptake funnel, two AK-630 aft, a 130 mm aft.

Runtime nodes per the contract (stable names, no '.NNN'): Mount_gun[_02/_03], Mount_missile[_02], Mount_mg[_02], each
with its Muzzle_<slot>[_NN] child; launch cells Muzzle_b<k>_<slot>[_NN]; Radar; Mount_APS (the defs' "aps").
No transport bays or doors. The runtime sinks ships whole (ShipSinking) and draws the wake from the "naval" data.
Metres, +Z up, -Y front, +X left (port).
"""
import mb_kit27 as k
import mb_kit35 as K
import mb_naval_b_kit as N


def _common(a, ship, rails, bollards, ports, band, anchor_y, rafts=()):
    ship.hull()
    ship.rails(rails)
    ship.bollards(bollards)
    ship.portholes(ports)
    ship.team_bands(*band)
    ship.anchors(anchor_y)
    ship.jackstaff()
    ship.stern_details()
    for (x, ys, z, s) in rafts:
        N.life_rafts(a, x, ys, z, s)


def _antennas(a, pts, h=2.6):
    for (x, y, z) in pts:
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, z), h=h, r=.04, lean=.05)


def _finish(a, target=60):
    N.fold(a, target)
    k.clean(a)


# ============================================================================= destroyer
def destroyer(a):
    """Arleigh Burke at game scale (52 x 8.6 m): see the module docstring."""
    S = N.Ship(a, 52, 8.6, 2.0, 2.8, 3.0, 4.2, entry=.4, transom=.82, rake=2.2, flare=.25)
    dz = S.deck_z
    S.deck_dress([(-23.5, -9.8), (15.2, 20.8)], seed=503)
    _common(a, S, [(-24.6, -10.0), (-9.5, 15.0), (15.2, 25.8)], [-22.5, -14.5, 16.5, 23.5], range(-20, 22, 4),
            (-8.0, 14.0), -21.0)
    S.breakwater(-20.6, h=.55)
    N.gun_127(a, 0, (0, -17.3, dz(-17.3)), 'mod4', s=1.15, barrel=5.2)
    N.vls(a, 0, (0, -11.3, dz(-11.3)), 4, 4, .72, raised=.3, points=4, opened={(1, 0), (2, 2)}, name='Vls_fwd')
    # The superstructure: the 01-level deckhouse, the faceted array house, the bridge top.
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    z0 = dz(-3.0) - .05
    N.tier(sup, -9.6, 2.6, z0, 5.7, 3.75, 3.45, rf=.45, rb=.3)
    o0 = [(-2.0, -7.6), (2.0, -7.6), (3.2, -6.2), (3.2, .4), (2.0, 1.8), (-2.0, 1.8), (-3.2, .4), (-3.2, -6.2)]
    o1 = [(-1.7, -6.9), (1.7, -6.9), (2.65, -5.8), (2.65, .1), (1.7, 1.3), (-1.7, 1.3), (-2.65, .1), (-2.65, -5.8)]
    N.faceted(sup, 5.65, 8.1, o0, o1)
    N.tier(sup, -6.4, -1.0, 8.05, 9.0, 1.9, 1.7, rf=.25, rb=.2)
    for s in (-1, 1):
        N.spy_face(a, (s * 2.43, -6.64, 6.95), (s * .74, -.64, .27), r=.78)
        N.spy_face(a, (s * 2.43, .93, 6.95), (s * .76, .62, .25), r=.78)
        k.block(a.part('Bridge_wings', 'Team'), (1.3, 1.4, .18), loc=(s * 3.6, -5.6, 7.55), chamfer=.04)
        a.part('Bridge_wings', 'Team').limb((s * 3.3, -5.6, 5.75), (s * 3.9, -5.6, 7.45), .18, .18, bevel=0)
        N.side_windows(a, s * 2.66, -5.5, -1.0, 7.55, h=.38)
        N.doors(a, s * 3.75, (-4.0, 1.2), 3.0, s)
    N.windows(a, -1.6, 1.6, -6.97, 7.6, h=.5, tilt=.32)
    N.windows(a, -1.5, 1.5, -6.18, 8.6, h=.3, tilt=.25, name='Bridge_glass')
    # The raked mast, its yards, the radar and the APS head.
    k.block(a.part('Mast', 'Team'), (1.5, 1.3, .25), loc=(0, -3.4, 11.1), chamfer=.04)
    N.lattice_mast(a, (0, -3.4, 9.0), 14.4, .9, .3)
    N.yards(a, (0, -3.0, 12.2), 4.6, n=2, gap=1.1)
    N.radar(a, (0, -3.4, 14.45), w=2.6, h=.8)
    N.aps(a, (0, -4.15, 11.25))
    _antennas(a, [(-1.4, -2.0, 9.0), (1.4, -2.0, 9.0)])
    # Midships: the deckhouse, two square stacks, boats on davits.
    N.tier(a.part('Superstructure', 'Team'), 2.4, 15.0, dz(8) - .05, 5.0, 3.1, 2.9, rf=.2, rb=.2)
    N.funnel(a, (0, 4.6, 5.0), 1.45, 1.35, 4.0, rake=.14, taper=.82, caps=2, cap_r=.36)
    N.funnel(a, (0, 11.4, 5.0), 1.35, 1.25, 3.5, rake=.14, taper=.82, caps=2, cap_r=.34)
    N.boat(a, (-2.1, 8.0, 5.0), length=3.6, beam=1.3, s=-1)
    N.boat(a, (2.1, 8.0, 5.0), length=3.6, beam=1.3, s=1)
    N.vents(a, [(0, 8.0, 5.0), (-.9, 13.9, 5.0), (1.0, 2.9, 5.7)])
    for s in (-1, 1):
        N.doors(a, s * 3.45, (6.0, 10.5, 13.5), dz(10), s)
    N.life_rafts(a, 3.0, (-1.0, .2), 5.75, 1)
    N.life_rafts(a, -3.0, (-1.0, .2), 5.75, -1)
    # CIWS: forward on the deckhouse ahead of the bridge, aft on the deckhouse (port, clear of the stack).
    N.phalanx(a, 0, (0, -8.6, 5.7))
    N.phalanx(a, 1, (2.05, 13.8, 5.0))
    # Aft VLS (SAM), the flight deck.
    N.vls(a, 1, (0, 18.6, dz(18.6)), 6, 4, .72, raised=.0, points=4, opened={(2, 1), (4, 2)}, name='Vls_aft')
    N.heli_deck(a, S, 21.0, 25.8)
    K.clutter(a, 'Deck_lockers', 'Armor', -2.4, 2.4, 6.2, 9.8, 5.0, 5, seed=401, size=(.3, .9), height=(.2, .6),
              gap=.3)
    _finish(a)


# ============================================================================= gun_destroyer
def gun_destroyer(a):
    """Spruance / Kidd at game scale (53 x 8.6 m): see the module docstring."""
    S = N.Ship(a, 53, 8.6, 2.0, 2.7, 2.9, 4.0, entry=.42, transom=.85, rake=2.4, flare=.22)
    dz = S.deck_z
    S.deck_dress([(-24.0, -12.8), (21.5, 25.5)], seed=504)
    _common(a, S, [(-25.0, -12.8), (-12.0, 15.6), (16.0, 26.2)], [-23.0, -14.0, 17.0, 21.5], range(-20, 22, 3),
            (-11.0, 14.0), -21.6)
    S.breakwater(-21.2, h=.5)
    N.gun_127(a, 0, (0, -17.8, dz(-17.8)), 'mod2', s=1.2, barrel=5.4)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -12.6, -1.6, dz(-6) - .05, 5.5, 3.65, 3.55, rf=.15, rb=.1)
    N.tier(sup, -11.9, -5.0, 5.45, 7.6, 3.05, 2.95, rf=.2, rb=.1)
    N.tier(sup, -10.6, -6.4, 7.55, 8.4, 2.2, 2.1, rf=.1, rb=.1)
    N.windows(a, -2.7, 2.7, -11.83, 7.0, h=.55, tilt=.08)
    for s in (-1, 1):
        k.block(a.part('Bridge_wings', 'Team'), (1.4, 1.5, .18), loc=(s * 3.7, -11.0, 6.9), chamfer=.04)
        N.side_windows(a, s * 3.03, -11.4, -8.0, 7.0, h=.45)
        N.doors(a, s * 3.65, (-9.0, -4.0), dz(-6), s)
        K.ladder(a.part('Ladders', 'Steel'), (s * 3.75, -2.4, dz(-2.4)), (s * 3.75, -2.6, 5.5), width=.45)
    k.block(a.part('Mast', 'Team'), (1.4, 1.2, .25), loc=(0, -8.4, 11.6), chamfer=.04)
    N.lattice_mast(a, (0, -8.4, 8.4), 14.0, .8, .28)
    N.yards(a, (0, -8.4, 12.6), 4.0, n=2, gap=.9)
    N.radar(a, (0, -8.4, 14.05), w=2.7, h=.9, style='mesh')
    # Midships deckhouse, the two offset stacks, the main lattice mast with the APS, the hangar.
    N.tier(sup, -1.8, 15.6, dz(6) - .05, 5.4, 3.55, 3.4, rf=.1, rb=.1)
    N.tier(sup, 10.6, 15.6, 5.35, 6.4, 3.1, 3.0, rf=.1, rb=.05)
    N.funnel(a, (-1.0, .4, 5.4), 1.05, 1.35, 3.7, rake=.06, taper=.9, caps=2, cap_r=.34)
    N.funnel(a, (1.0, 8.4, 5.4), 1.0, 1.3, 3.4, rake=.06, taper=.9, caps=2, cap_r=.32)
    k.block(a.part('Mast', 'Team'), (1.0, 1.0, .2), loc=(0, 4.5, 10.2), chamfer=.03)
    N.lattice_mast(a, (0, 4.5, 5.4), 11.6, .75, .25, braces=3)
    N.aps(a, (0, 4.5, 11.65))
    door = a.part('Hangar_door', 'Undercarriage')
    door.box((4.2, .06, 2.6), loc=(0, 15.62, dz(15.6) + 1.35), bevel=0)
    for i in range(8):
        a.part('Door_slats', 'Armor').box((4.2, .03, .03), loc=(0, 15.66, dz(15.6) + .3 + i * .32), bevel=0)
    N.boat(a, (-2.6, 4.5, 5.4), length=3.8, beam=1.4, s=-1)
    N.boat(a, (2.6, 3.6, 5.4), length=3.8, beam=1.4, s=1)
    N.vents(a, [(1.6, -0.2, 5.4), (-1.8, 9.0, 5.4), (0, 11.8, 6.4)])
    N.life_rafts(a, 3.25, (11.4, 12.6, 13.8), 6.45, 1)
    _antennas(a, [(-1.6, -7.0, 8.4), (1.6, -7.0, 8.4), (0, 14.0, 6.4)])
    N.phalanx(a, 0, (-1.8, 12.6, 6.4))
    N.box_launcher(a, 0, (1.7, 14.2, 6.4), slot='missile', s=1.0, cols=4, rows=2)
    N.heli_deck(a, S, 16.2, 21.2)
    N.gun_127(a, 1, (0, 23.8, dz(23.8)), 'mod2', s=1.2, barrel=5.0)
    K.clutter(a, 'Deck_lockers', 'Armor', -2.4, 2.4, -1.0, 9.8, 5.4, 10, seed=411, size=(.3, .9), height=(.2, .6),
              gap=.35)
    _finish(a)


# ============================================================================= missile_destroyer
def missile_destroyer(a):
    """Type 055 read at game scale (54 x 8.8 m): see the module docstring."""
    S = N.Ship(a, 54, 8.8, 2.1, 2.9, 3.1, 4.4, entry=.42, transom=.84, rake=2.6, flare=.26)
    dz = S.deck_z
    S.deck_dress([(-25.0, -10.4), (18.6, 25.8)], hatches=5, planks=True, seed=505)
    _common(a, S, [(-25.6, -15.0), (-10.4, 6.5), (17.8, 26.8)], [-23.5, -16.5, 18.5, 24.0], range(-21, 20, 4),
            (-9.0, 16.0), -22.2)
    S.breakwater(-22.6, h=.5)
    N.gun_stealth(a, 0, (0, -19.8, dz(-19.8)), s=1.2, barrel=4.2)
    N.vls(a, 0, (0, -12.2, dz(-12.2)), 4, 2, 1.7, raised=.8, points=4, opened={(1, 0), (2, 1)}, name='Vls',
          big=True)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -10.2, 6.5, dz(-2) - .05, 6.2, 3.95, 3.5, rf=.8, rb=.4)
    N.tier(sup, -7.4, 3.0, 6.15, 9.4, 3.3, 2.4, rf=1.4, rb=.6)
    N.tier(sup, -5.2, -.2, 9.35, 13.2, 2.0, 1.1, rf=.9, rb=.6, chamfer=.05)
    N.windows(a, -1.9, 1.9, -6.48, 8.3, h=.45, tilt=.41)
    N.flat_array(a, (0, -4.79, 11.3), (0, -.973, .23), 1.6, 2.3)
    N.flat_array(a, (0, -.46, 11.3), (0, .988, .155), 1.6, 2.3)
    for s in (-1, 1):
        N.flat_array(a, (s * 1.59, -2.7, 11.3), (s * .973, 0, .23), 2.6, 2.3)
        N.flat_array(a, (s * 2.64, -4.6, 7.8), (s * .96, -.1, .27), 1.0, 1.4, name='Array_small')
        k.block(a.part('Bridge_wings', 'Team'), (1.4, 1.2, .16), loc=(s * 3.45, -6.0, 8.0), chamfer=.03)
        a.part('Bridge_wings', 'Team').limb((s * 3.3, -6.0, 6.25), (s * 3.9, -6.0, 7.92), .16, .16, bevel=0)
        N.doors(a, s * 3.95, (-6.0, 1.0, 4.5), dz(0), s)
    k.block(a.part('Mast', 'Team'), (1.6, 2.4, .3), loc=(0, -2.6, 13.35), chamfer=.06)
    N.radar(a, (0, -2.4, 13.5), w=2.8, h=.85, style='back')
    N.aps(a, (0, -3.95, 13.5))
    _antennas(a, [(-.9, -1.0, 13.5), (.9, -1.0, 13.5)], h=2.2)
    N.ak630(a, 0, (0, -8.6, 6.2), s=1.0, style='1130')
    # The aft deckhouse with the hangar, the wide stealth funnel, the RAM box, the second Type 1130, boats.
    N.tier(sup, 6.3, 17.6, dz(12) - .05, 5.6, 3.75, 3.45, rf=.3, rb=.2)
    N.funnel(a, (0, 8.8, 5.6), 1.6, 1.7, 3.3, rake=.12, taper=.74, caps=2, cap_r=.42)
    door = a.part('Hangar_door', 'Undercarriage')
    door.box((4.4, .06, 2.2), loc=(0, 17.62, dz(17.6) + 1.2), bevel=0)
    N.ak630(a, 1, (-2.15, 12.4, 5.6), s=.95, style='1130')
    N.box_launcher(a, 1, (1.6, 15.6, 5.6), slot='missile', s=1.0, cols=4, rows=3, el=.2, length=2.4, style='ram')
    N.boat(a, (2.4, 12.0, 5.6), length=3.6, beam=1.3, s=1)
    N.vents(a, [(-1.2, 15.6, 5.6), (0, 14.0, 5.6)])
    N.life_rafts(a, 2.95, (7.0, 8.1, 9.2), 5.65, 1)
    N.life_rafts(a, -2.95, (7.0, 8.1, 9.2), 5.65, -1)
    N.lattice_mast(a, (0, 14.2, 5.6), 11.2, .65, .22, braces=3)
    a.part('Radomes', 'Medical').sphere(.55, loc=(0, 14.2, 11.75), seg=12, rings=8)
    N.yards(a, (0, 14.2, 9.4), 3.0, n=1)
    st = a.part('Mast_steel', 'Steel')
    st.tube([(0, -2.4, 13.65), (0, -2.4, 17.2)], .08, seg=6)
    st.box((2.8, .1, .1), loc=(0, -2.4, 15.4), bevel=0)
    st.box((1.8, .08, .08), loc=(0, -2.4, 16.5), bevel=0)
    for s in (-1, 1):
        st.box((.05, .05, .7), loc=(s * .85, -2.4, 16.15), bevel=0)
    for s in (-1, 1):
        a.part('Radomes', 'Medical').sphere(.22, loc=(s * 1.3, -2.4, 15.6), seg=10, rings=6)
        K.whip_antenna(a.part('Antennas', 'Steel'), (s * 1.0, -6.6, 9.4), h=2.4, r=.04, lean=.15)
    N.heli_deck(a, S, 18.4, 26.0)
    K.clutter(a, 'Deck_lockers', 'Armor', -2.6, 2.6, 2.2, 6.0, 6.2, 6, seed=421, size=(.3, .8), height=(.2, .5),
              gap=.3)
    _finish(a)


# ============================================================================= aa_destroyer
def aa_destroyer(a):
    """Ticonderoga baseline 1 read at game scale (53 x 8.7 m): see the module docstring."""
    S = N.Ship(a, 53, 8.7, 2.0, 2.8, 3.0, 4.2, entry=.4, transom=.84, rake=2.2, flare=.24)
    dz = S.deck_z
    S.deck_dress([(-24.0, -11.8), (12.8, 25.5)], seed=506)
    _common(a, S, [(-25.0, -12.0), (-11.5, 12.6), (13.2, 26.2)], [-23.0, -12.6, 13.6, 20.0], range(-20, 22, 4),
            (-10.0, 12.0), -21.8)
    S.breakwater(-20.8, h=.5)
    N.mk26(a, 0, (0, -15.8, dz(-15.8)), slot='missile', s=1.4, msl=4.0)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -11.6, 1.6, dz(-5) - .05, 6.0, 3.85, 3.65, rf=.2, rb=.15)
    o0 = [(-2.1, -10.9), (2.1, -10.9), (3.25, -9.6), (3.25, -1.0), (-3.25, -1.0), (-3.25, -9.6)]
    o1 = [(-1.95, -10.6), (1.95, -10.6), (3.05, -9.4), (3.05, -1.2), (-3.05, -1.2), (-3.05, -9.4)]
    N.faceted(sup, 5.95, 8.6, o0, o1)
    N.tier(sup, -10.2, -6.0, 8.55, 9.3, 2.4, 2.3, rf=.1, rb=.1)
    N.windows(a, -1.9, 1.9, -10.75, 8.0, h=.5, tilt=.05)
    for s in (-1, 1):
        N.spy_face(a, (s * 2.72, -10.15, 7.25), (s * .75, -.65, .08), r=.82)
        k.block(a.part('Bridge_wings', 'Team'), (1.0, 1.3, .18), loc=(s * 3.7, -9.9, 7.4), chamfer=.04)
        N.side_windows(a, s * 3.1, -9.0, -6.0, 8.0, h=.42)
        N.doors(a, s * 3.85, (-8.0, -3.0), dz(-5), s)
    k.block(a.part('Mast', 'Team'), (1.4, 1.2, .25), loc=(0, -4.2, 12.2), chamfer=.04)
    N.lattice_mast(a, (0, -4.2, 8.6), 14.0, .85, .3)
    N.yards(a, (0, -4.0, 12.9), 4.2, n=2, gap=.9)
    N.radar(a, (0, -4.2, 14.05), w=2.9, h=.9, style='mesh')
    N.aps(a, (0, -4.95, 12.35))
    # Midships deckhouse, the stack, the aft array house with its lattice mainmast.
    N.tier(sup, 1.4, 12.6, dz(7) - .05, 5.4, 3.5, 3.3, rf=.1, rb=.15)
    N.funnel(a, (0, 2.6, 5.4), 1.3, 1.0, 3.4, rake=.1, caps=2, cap_r=.34)
    a0 = [(-2.3, 6.8), (2.3, 6.8), (2.3, 10.8), (1.5, 12.0), (-1.5, 12.0), (-2.3, 10.8)]
    a1 = [(-2.1, 7.0), (2.1, 7.0), (2.1, 10.6), (1.4, 11.7), (-1.4, 11.7), (-2.1, 10.6)]
    N.faceted(sup, 5.35, 7.8, a0, a1)
    for s in (-1, 1):
        N.spy_face(a, (s * 1.92, 11.37, 6.6), (s * .83, .55, .06), r=.6)
        N.boat(a, (s * 3.0, 9.2, 5.4), length=3.6, beam=1.2, s=s)
    N.lattice_mast(a, (0, 9.0, 7.8), 11.6, .6, .22, braces=2)
    _antennas(a, [(-1.5, -7.0, 9.3), (1.5, -7.0, 9.3), (0, 11.0, 7.8)])
    N.vents(a, [(-1.6, 5.2, 5.4), (1.6, 5.4, 5.4)])
    N.phalanx(a, 0, (-2.75, 5.0, 5.4))
    N.phalanx(a, 1, (2.75, 5.0, 5.4))
    N.vls(a, 1, (0, 15.6, dz(15.6)), 4, 4, .72, raised=.0, points=4, opened={(1, 1), (2, 2)}, name='Vls_aft')
    N.gun_127(a, 0, (0, 22.0, dz(22.0)), 'mod4', s=1.15, barrel=5.8)
    K.clutter(a, 'Deck_lockers', 'Armor', -2.6, 2.6, 4.0, 6.4, 5.4, 5, seed=431, size=(.3, .8), height=(.2, .5),
              gap=.3)
    _finish(a)


# ============================================================================= heavy_monitor
def heavy_monitor(a):
    """Erebus / Roberts read at game scale (46 x 10 m over the bulges): see the module docstring."""
    S = N.Ship(a, 46, 8.2, 1.4, 1.5, 1.5, 2.3, entry=.3, transom=.9, sheer_from=.4, rake=1.2, flare=.05, bulge=.22,
               fb_knuckle=.45)
    dz = S.deck_z
    S.deck_dress([(-20.0, -6.0), (13.8, 21.0)], seed=507)
    _common(a, S, [(-21.5, -15.5), (-6.0, 22.6)], [-19.5, -15.0, 15.0, 20.5], range(-16, 20, 4), (-4.0, 12.0), -19.4)
    # The armoured deck: plate seams across and along.
    seams = a.part('Deck_plates', 'Undercarriage')
    for y in range(-20, 22, 2):
        h = S.half_beam(y) - .15
        K.plane(seams, -h, h, y - .03, y + .03, dz(y) + .022)
    for x in (-2.6, -1.0, 1.0, 2.6):
        K.plane(seams, x - .03, x + .03, -19.0, 21.5, dz(0) + .022)
    N.heavy_turret(a, 0, (0, -10.5, dz(-10.5)), s=1.15, barrels=1, barrel=8.4, cal=.32, base_h=1.6, base_r=2.7)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -4.6, 1.6, dz(-2) - .05, 4.3, 2.6, 2.4, rf=.2, rb=.1)
    N.tier(sup, -4.0, -.6, 4.25, 6.0, 2.0, 1.85, rf=.15, rb=.1)
    N.windows(a, -1.7, 1.7, -3.92, 5.4, h=.5, tilt=.08)
    for s in (-1, 1):
        k.block(a.part('Bridge_wings', 'Team'), (1.2, 1.1, .16), loc=(s * 2.5, -3.4, 5.4), chamfer=.03)
        N.side_windows(a, s * 2.0, -3.4, -.8, 5.4, h=.4)
        N.doors(a, s * 2.6, (-2.0, 1.0), dz(0), s)
    # The tripod: the main leg, two raked legs, the director top, the radar and the APS head.
    st = a.part('Mast_steel', 'Steel')
    st.tube([(0, -2.0, 6.0), (0, -2.0, 9.6)], .16, seg=8)
    for s in (-1, 1):
        st.tube([(s * 1.7, .8, 4.3), (0, -1.9, 9.0)], .13, seg=6)
    N.tier(a.part('Mast', 'Team'), -3.1, -.9, 9.4, 10.6, 1.2, 1.05, rf=.1, rb=.1)
    a.part('Mast_glass', 'Glass').box((2.0, .03, .3), loc=(0, -3.13, 10.2), bevel=0)
    K.dish(a.part('Mast_steel', 'Steel'), a.part('Mast_steel', 'Steel'), (0, -1.9, 11.3), r=.5, normal=(0, -1, .3))
    N.radar(a, (0, -1.9, 10.65), w=1.5, h=.5)
    N.aps(a, (0, -3.15, 10.65), r=.26)
    N.tier(sup, 1.4, 13.6, dz(7) - .05, 3.4, 2.6, 2.45, rf=.15, rb=.15)
    N.funnel(a, (0, 3.4, 3.4), .9, 1.05, 3.4, rake=.08, taper=.92, caps=1, cap_r=.55)
    N.boat(a, (1.4, 7.6, 3.4), length=3.4, beam=1.2, s=1)
    N.vents(a, [(-1.4, 6.0, 3.4), (-1.4, 9.0, 3.4), (0, 12.6, 3.4)])
    _antennas(a, [(-1.4, -1.0, 6.0), (1.4, -1.0, 6.0)], h=2.2)
    N.phalanx(a, 0, (0, 11.2, 3.4), s=.95)
    N.life_rafts(a, -2.2, (9.0, 10.2), 3.45, -1)
    K.clutter(a, 'Deck_lockers', 'Armor', -3.0, 3.0, 14.4, 19.5, dz(17) + .01, 8, seed=441, size=(.3, .9),
              height=(.2, .6), gap=.4)
    _finish(a)


# ============================================================================= battlecruiser
def battlecruiser(a):
    """Alaska, modernised, at game scale (68 x 11 m): see the module docstring."""
    S = N.Ship(a, 68, 11.0, 2.6, 3.9, 4.2, 6.0, entry=.4, transom=.8, rake=3.2, flare=.25)
    dz = S.deck_z
    S.deck_dress([(-31.0, -8.0), (16.2, 23.8)], seed=508)
    _common(a, S, [(-32.0, -15.5), (-8.5, 16.5), (16.8, 33.6)], [-29.5, -24.0, 22.5, 29.0], range(-26, 30, 4),
            (-10.0, 18.0), -27.6)
    S.breakwater(-26.5, h=.6)
    N.heavy_turret(a, 0, (0, -19.5, dz(-19.5)), s=1.15, barrels=2, barrel=8.8, cal=.3, base_h=1.1, base_r=2.6)
    N.inclined_cells(a, 0, (0, -11.5, dz(-11.5)), 2, 2, cell=1.5, raised=.7)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -7.8, 16.0, dz(4) - .05, 6.8, 4.2, 4.0, rf=.3, rb=.2)
    N.tier(sup, -7.2, -.5, 6.75, 9.4, 3.4, 3.0, rf=.5, rb=.2)
    N.tier(sup, -6.6, -2.0, 9.35, 11.6, 2.4, 2.1, rf=.3, rb=.1)
    N.tier(sup, -5.6, -3.0, 11.55, 12.8, 1.6, 1.4, rf=.1, rb=.1)
    k.lathe(a.part('Conning_tower', 'Armor'), [(1.3, 0), (1.3, 2.0), (1.15, 2.2), (0, 2.2)], loc=(0, -7.0, 6.75),
            seg=16)
    a.part('Conning_slits', 'Glass').box((1.6, .05, .14), loc=(0, -8.31, 8.6), bevel=0)
    N.windows(a, -2.0, 2.0, -6.42, 10.8, h=.5, tilt=.13)
    for s in (-1, 1):
        k.block(a.part('Bridge_wings', 'Team'), (1.5, 1.4, .18), loc=(s * 3.1, -5.8, 10.6), chamfer=.04)
        N.side_windows(a, s * 2.12, -6.0, -2.4, 10.8, h=.42)
        N.doors(a, s * 4.2, (-4.0, 2.0, 12.0), dz(4), s)
    k.lathe(a.part('Directors', 'Armor'), [(.9, 0), (.9, .5), (.6, .9), (0, .95)], loc=(0, -4.6, 12.8), seg=14)
    K.dish(a.part('Mast_steel', 'Steel'), a.part('Mast_steel', 'Steel'), (0, -5.3, 13.9), r=.55, normal=(0, -1, .2))
    k.block(a.part('Mast', 'Team'), (1.5, 1.3, .25), loc=(0, -3.4, 15.0), chamfer=.04)
    N.lattice_mast(a, (0, -3.4, 12.8), 17.0, .7, .28, braces=2)
    N.yards(a, (0, -3.2, 15.8), 4.6, n=2, gap=.9)
    N.radar(a, (0, -3.4, 17.05), w=3.2, h=.95, style='mesh')
    N.aps(a, (0, -4.15, 15.15))
    # The trunk funnel, the after superstructure and mainmast, the Phalanx sponsons, boats.
    N.funnel(a, (0, 4.6, 6.8), 1.7, 2.3, 4.2, rake=.1, taper=.86, caps=2, cap_r=.5)
    N.tier(sup, 9.0, 15.6, 6.75, 8.8, 2.4, 2.2, rf=.2, rb=.2)
    N.lattice_mast(a, (0, 11.6, 8.8), 13.2, .6, .22, braces=2)
    k.lathe(a.part('Directors', 'Armor'), [(.7, 0), (.7, .45), (.5, .75), (0, .8)], loc=(0, 14.2, 8.8), seg=12)
    for s, y, i in ((-1, 1.4, 0), (1, 8.0, 1)):
        k.block(a.part('Sponsons', 'Armor'), (1.8, 2.0, .25), loc=(s * 4.2, y, 6.7), chamfer=.04)
        a.part('Sponsons', 'Armor').limb((s * 4.6, y, 4.6), (s * 5.1, y, 6.6), .25, .25, bevel=0)
        N.phalanx(a, i, (s * 4.3, y, 6.82))
    for s in (-1, 1):
        N.boat(a, (s * 3.3, 12.6, 6.8), length=4.0, beam=1.4, s=s)
    N.vents(a, [(-2.2, 2.5, 6.8), (2.2, 2.5, 6.8), (0, 8.0, 6.8)])
    _antennas(a, [(-1.8, -1.0, 9.4), (1.8, -1.0, 9.4), (0, 15.0, 8.8)])
    N.mk26(a, 1, (0, 20.2, dz(20.2)), slot='missile', s=1.0, msl=4.0)
    N.heli_deck(a, S, 24.0, 32.6)
    cr = a.part('Crane', 'Armor')
    cr.cyl(.35, 2.2, loc=(0, 33.0, dz(33) + 1.1), seg=10, bevel=0)
    cr.limb((0, 33.0, dz(33) + 2.0), (0, 30.0, dz(33) + 4.0), .3, .3, bevel=0)
    K.clutter(a, 'Deck_lockers', 'Armor', -3.4, 3.4, 0.5, 8.6, 6.8, 10, seed=451, size=(.3, 1.0), height=(.2, .6),
              gap=.4)
    _finish(a)


# ============================================================================= battleship
def battleship(a):
    """Iowa (1980s) at game scale (82 x 13 m): see the module docstring."""
    S = N.Ship(a, 82, 13.0, 3.0, 4.4, 4.8, 7.4, entry=.42, transom=.78, sheer_from=.1, rake=3.6, flare=.3)
    dz = S.deck_z
    S.deck_dress([(-38.0, -9.6), (10.2, 30.8)], hatches=7, planks=True, seed=509)
    _common(a, S, [(-39.0, -18.0), (-10.0, 18.0), (18.5, 40.6)], [-36.0, -30.0, 30.0, 37.0], range(-32, 36, 4),
            (-11.0, 19.0), -34.0)
    S.breakwater(-31.0, h=.65)
    N.heavy_turret(a, 0, (0, -24.5, dz(-24.5)), s=1.35, barrels=3, barrel=8.5, cal=.32, base_h=.9, base_r=2.9,
                   width=1.12, pitch=1.25)
    N.heavy_turret(a, 1, (0, -15.0, dz(-15.0)), s=1.35, barrels=3, barrel=8.5, cal=.32, base_h=3.8, base_r=2.9,
                   width=1.12, pitch=1.25)
    N.heavy_turret(a, 2, (0, 25.5, dz(25.5)), s=1.35, barrels=3, barrel=8.5, cal=.32, base_h=.9, base_r=2.9,
                   width=1.12, pitch=1.25)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -9.4, 10.0, dz(0) - .05, 8.0, 5.6, 5.4, rf=.3, rb=.3)
    N.tier(sup, -8.6, -.6, 7.95, 11.0, 4.4, 4.1, rf=.3, rb=.1)
    N.tier(sup, -7.0, -1.2, 10.95, 13.8, 3.2, 3.0, rf=.3, rb=.1)
    N.tier(sup, -6.2, -2.4, 13.75, 15.6, 2.4, 2.2, rf=.2, rb=.1)
    N.tier(sup, 7.6, 9.8, 7.95, 9.4, 2.3, 2.1, rf=.2, rb=.2)
    k.lathe(a.part('Conning_tower', 'Armor'), [(1.6, 0), (1.6, 2.8), (1.45, 3.1), (0, 3.1)], loc=(0, -7.6, 7.95),
            seg=18)
    a.part('Conning_slits', 'Glass').box((2.2, .05, .16), loc=(0, -9.21, 10.5), bevel=0)
    N.windows(a, -2.6, 2.6, -6.78, 13.0, h=.5, tilt=.11)
    for s in (-1, 1):
        k.block(a.part('Bridge_wings', 'Team'), (1.8, 1.6, .2), loc=(s * 4.0, -6.2, 12.8), chamfer=.04)
        N.side_windows(a, s * 3.06, -6.6, -2.0, 13.0, h=.45)
        N.doors(a, s * 5.4, (-6.0, 0.0, 6.0), dz(0), s)
        K.ladder(a.part('Ladders', 'Steel'), (s * 5.45, 8.6, dz(8.6)), (s * 5.45, 8.2, 8.0), width=.5)
    k.block(a.part('Directors', 'Armor'), (2.4, 1.8, 1.1), loc=(0, -4.2, 16.15), chamfer=.12)
    a.part('Directors', 'Armor').box((4.4, .4, .4), loc=(0, -3.6, 16.2), bevel=.05)
    st = a.part('Mast_steel', 'Steel')
    st.tube([(0, -2.2, 15.6), (0, -2.2, 22.0)], .18, seg=8)
    for s in (-1, 1):
        st.tube([(s * 2.2, -.6, 13.8), (0, -2.1, 20.6)], .14, seg=6)
    k.block(a.part('Mast', 'Team'), (1.8, 1.6, .25), loc=(0, -2.2, 19.0), chamfer=.04)
    N.yards(a, (0, -2.2, 20.2), 5.4, n=2, gap=1.0)
    N.radar(a, (0, -2.2, 22.05), w=3.6, h=1.1, style='mesh')
    N.aps(a, (0, -3.0, 19.15), r=.36)
    N.funnel(a, (0, 1.6, 8.0), 2.2, 2.5, 5.6, rake=.05, taper=.9, caps=2, cap_r=.6)
    N.funnel(a, (0, 6.8, 8.0), 2.0, 2.2, 5.0, rake=.05, taper=.9, caps=2, cap_r=.55)
    st.tube([(0, 9.2, 9.4), (0, 9.2, 15.0)], .14, seg=8)
    for s in (-1, 1):
        st.tube([(s * 1.6, 9.6, 9.4), (0, 9.2, 13.8)], .1, seg=6)
    k.lathe(a.part('Directors', 'Armor'), [(.9, 0), (.9, .6), (.6, 1.0), (0, 1.05)], loc=(0, 9.2, 15.0), seg=14)
    for s, i in ((-1, 0), (1, 1)):
        N.phalanx(a, i, (s * 4.4, 3.8, 8.0))
    N.box_launcher(a, 0, (3.9, 8.6, 8.0), slot='missile', s=1.1, cols=4, rows=2)
    N.boat(a, (-4.2, 7.6, 8.0), length=4.2, beam=1.5, s=-1)
    N.boat(a, (4.5, .9, 8.0), length=3.8, beam=1.4, s=1)
    for s in (-1, 1):
        cr = a.part('Crane', 'Armor')
        cr.cyl(.3, 2.6, loc=(s * 3.8, 5.2, 9.3), seg=10, bevel=0)
        cr.limb((s * 3.8, 5.2, 10.4), (s * 5.2, 7.0, 11.8), .26, .26, bevel=0)
    N.vents(a, [(-3.0, -.2, 8.0), (3.0, 6.0, 8.0), (-2.8, 9.6, 8.0)])
    N.life_rafts(a, 5.0, (-6.0, -4.8, -3.6), 8.05, 1)
    N.life_rafts(a, -5.0, (-6.0, -4.8, -3.6), 8.05, -1)
    _antennas(a, [(-2.4, -2.0, 13.8), (2.4, -2.0, 13.8), (1.2, 9.2, 9.4)], h=3.0)
    for s in (-1, 1):
        k.lathe(a.part('Directors', 'Armor'), [(.5, 0), (.5, .5), (.35, .8), (0, .85)], loc=(s * 3.7, -1.7, 11.0),
                seg=14)
        K.dish(a.part('Mast_steel', 'Steel'), a.part('Mast_steel', 'Steel'), (s * 3.7, -2.1, 12.05), r=.42,
               normal=(s * .3, -1, .25))
        sl = a.part('Searchlights', 'Armor')
        sl.cyl(.12, 1.2, loc=(s * 2.4, 4.3, 8.6), seg=8, bevel=0)
        k.lathe(a.part('Searchlights', 'Armor'), [(.3, 0), (.34, .4), (.3, .5)], loc=(s * 2.4, 4.3, 9.2),
                rot=N.FWD, seg=10)
        a.part('Searchlight_lens', 'Lamp').cyl(.26, .02, loc=(s * 2.4, 3.8, 9.45), rot=N.FWD, seg=10, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.4, 1.6, 13.6), h=3.4, r=.04, lean=.1)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.4, 6.8, 13.0), h=3.0, r=.04, lean=.1)
    a.part('Mast_steel', 'Steel').box((7.0, .14, .14), loc=(0, 9.2, 14.2), bevel=0)
    a.part('Directors', 'Armor').box((3.6, .35, .35), loc=(0, 9.9, 15.4), bevel=.04)
    K.dish(a.part('Mast_steel', 'Steel'), a.part('Mast_steel', 'Steel'), (0, 9.2, 16.4), r=.6, normal=(0, 1, .3))
    for s in (-1, 1):
        a.part('Mast_steel', 'Steel').tube([(s * 3.4, 9.2, 14.2), (s * 3.4, 9.2, 15.4)], .05, seg=4)
    N.heli_deck(a, S, 31.0, 40.0)
    cr = a.part('Crane', 'Armor')
    cr.cyl(.4, 3.0, loc=(0, 40.0, dz(40) + 1.5), seg=10, bevel=0)
    cr.limb((0, 40.0, dz(40) + 2.6), (0, 36.0, dz(40) + 5.2), .34, .34, bevel=0)
    K.clutter(a, 'Deck_lockers', 'Armor', -4.6, 4.6, -.4, 9.4, 8.0, 12, seed=461, size=(.3, 1.0), height=(.2, .7),
              gap=.45)
    _finish(a)


# ============================================================================= missile_cruiser
def missile_cruiser(a):
    """Kirov read at game scale (58 x 9.4 m): see the module docstring."""
    S = N.Ship(a, 58, 9.4, 2.2, 3.3, 3.5, 5.0, entry=.4, transom=.82, rake=2.8, flare=.26)
    dz = S.deck_z
    S.deck_dress([(-26.0, -6.8), (14.8, 28.0)], seed=510)
    _common(a, S, [(-27.0, -14.6), (-7.0, 14.6), (15.0, 28.6)], [-25.0, -16.0, 16.0, 26.0], range(-22, 24, 4),
            (-6.0, 14.0), -23.6)
    N.revolvers(a, 1, (0, -19.6, dz(-19.6) + .01), 2, 3, r=.72, pitch=1.9, slot='missile', points=4)
    N.inclined_cells(a, 0, (0, -10.9, dz(-10.9)), 2, 4, cell=1.4, raised=.6)
    sup = a.part('Superstructure', 'Team')
    sup.asset = a
    N.tier(sup, -6.6, 14.6, dz(4) - .05, 6.4, 4.3, 4.1, rf=.4, rb=.2)
    N.tier(sup, -5.8, 4.0, 6.35, 9.4, 3.6, 3.2, rf=.6, rb=.2)
    N.tier(sup, -4.6, 1.5, 9.35, 11.4, 2.4, 2.0, rf=.4, rb=.2)
    N.windows(a, -2.2, 2.2, -5.42, 8.6, h=.5, tilt=.2)
    for s in (-1, 1):
        k.block(a.part('Bridge_wings', 'Team'), (1.3, 1.4, .18), loc=(s * 3.9, -4.8, 8.4), chamfer=.04)
        N.side_windows(a, s * 3.22, -4.6, 3.0, 8.6, h=.42)
        N.doors(a, s * 4.3, (-4.0, 2.0, 11.0), dz(4), s)
    k.extrude(a.part('Mast', 'Team'), [(-1.6, -1.4), (1.6, -1.4), (1.6, 1.4), (-1.6, 1.4)], 3.0,
              loc=(0, -1.4, 12.9), axis='Z', chamfer=.06, taper=(.5, .5))
    k.block(a.part('Mast', 'Team'), (2.0, 1.8, .25), loc=(0, -1.4, 14.5), chamfer=.04)
    N.yards(a, (0, -1.0, 13.6), 5.2, n=1)
    N.radar(a, (0, -1.4, 14.65), w=3.2, h=.9, style='back')
    N.aps(a, (0, -2.75, 12.85), r=.3)
    for y, z in ((-4.0, 11.4), (3.0, 9.4)):
        k.lathe(a.part('Directors', 'Armor'), [(.7, 0), (.7, .45), (.5, .8), (0, .85)], loc=(0, y, z), seg=12)
    N.funnel(a, (0, 6.8, 6.4), 1.8, 1.8, 3.4, rake=.06, taper=.85, caps=2, cap_r=.45)
    N.tier(sup, 9.5, 14.0, 6.35, 9.0, 2.6, 2.3, rf=.2, rb=.2)
    N.lattice_mast(a, (0, 11.6, 9.0), 13.4, .7, .25, braces=2)
    a.part('Radomes', 'Medical').sphere(.75, loc=(0, 11.6, 14.15), seg=14, rings=8)
    N.yards(a, (0, 11.6, 12.4), 3.6, n=1)
    for s in (-1, 1):
        a.part('Mast_steel', 'Steel').tube([(s * 1.2, -4.3, 11.4), (s * 1.2, -4.4, 11.95)], .08, seg=6)
        K.dish(a.part('Mast_steel', 'Steel'), a.part('Mast_steel', 'Steel'), (s * 1.2, -4.6, 12.0), r=.55,
               normal=(s * .4, -1, .2))
        a.part('Radomes', 'Medical').sphere(.32, loc=(s * 1.6, -1.4, 14.9), seg=10, rings=6)
        K.whip_antenna(a.part('Antennas', 'Steel'), (s * 2.6, -1.0, 13.6), h=2.6, r=.04, lean=.12)
    N.ak630(a, 0, (-3.3, 12.8, 6.4))
    N.ak630(a, 1, (3.3, 12.8, 6.4))
    for s in (-1, 1):
        N.boat(a, (s * 3.3, 6.6, 6.4), length=3.8, beam=1.3, s=s)
    door = a.part('Hangar_door', 'Undercarriage')
    door.box((4.0, .06, 2.0), loc=(0, 14.62, dz(14.6) + 1.1), bevel=0)
    a.part('Lift_seams', 'Undercarriage').box((4.4, 5.0, .02), loc=(0, 19.0, dz(19) + .025), bevel=0)
    N.vents(a, [(-2.2, 9.8, 6.4), (2.2, 9.8, 6.4), (0, 3.4, 9.4)])
    _antennas(a, [(-1.8, .8, 11.4), (1.8, .8, 11.4)])
    N.gun_stealth(a, 0, (0, 23.5, dz(23.5)), s=1.3, barrel=5.0)
    K.clutter(a, 'Deck_lockers', 'Armor', -3.4, 3.4, 4.4, 9.2, 6.4, 8, seed=471, size=(.3, .9), height=(.2, .6),
              gap=.4)
    _finish(a)


SHIP = dict(ao_distance=2.0, grime_height=.6)
BUILDERS = {
    'destroyer': (destroyer, SHIP),
    'gun_destroyer': (gun_destroyer, SHIP),
    'missile_destroyer': (missile_destroyer, SHIP),
    'aa_destroyer': (aa_destroyer, SHIP),
    'heavy_monitor': (heavy_monitor, dict(ao_distance=1.6, grime_height=.5)),
    'battlecruiser': (battlecruiser, SHIP),
    'battleship': (battleship, dict(ao_distance=2.4, grime_height=.7)),
    'missile_cruiser': (missile_cruiser, SHIP),
}
