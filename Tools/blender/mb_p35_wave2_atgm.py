"""Prompt 35 wave 2 (lane A): the ATGM tower and its two branches rebuilt from scratch on one emplacement (owner
decision 4), each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)".

A Hegemon cast-concrete blockhouse, 5.2 x 5.2 m: a chamfered pad, a battered (sloping) blockhouse with a firing slit,
a steel rear door, a ladder with a cage up the right side, a roof slab with a concrete parapet, sandbags and a guard
rail, and on a race ring in the middle the launcher (the sheet: a twin missile launcher on a low tower with a shield):

- atgm_tower (tower_kornet): a Kornet-EM-class twin launcher: a pedestal, the armoured shield with its sight window,
  the yoke and two transport-launch containers (`ATGM_pod`, the runtime's missile pairs) either side of the 1P163-class
  guidance box (thermal and TV lenses, laser window).
- atgm_tower_a (kornet_top, the top-attack branch): the launcher raised 1.8 m on a guyed column (`Launch_column`,
  `Launch_collar` kept from the old model) so it can look down on roofs; a Javelin-class launch box pair elevated
  15 degrees with a command launch unit and its sunshade, a cable trunk down the column, column rungs.
- atgm_tower_b (kornet_multi): four containers in two pairs one over the other on a wider yoke, and a small
  search radar panel turning on a post at the launcher's rear (`Radar`).

Runtime nodes (kept): `Turret` (yaw pivot), `Muzzle_main`, `Muzzle_missile[.001 ...]` at the tubes' mouths, `Radar`
(atgm_tower_b), mesh names `ATGM_pod` (launch point pairs), `Launch_column` / `Launch_collar` (atgm_tower_a). Built
only from frontier_kit / mb_kit27 primitives and mb_kit35; no other model's builder. Metres, +Z up, -Y front, +X left.
Each stays under 1.5 x the tower maximum (6,000 triangles, owner decision 6).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
PAD = .25                # top of the cast pad
WALL_H = 2.6             # blockhouse wall height above the pad
ROOF = PAD + WALL_H      # underside of the roof slab
DECK = ROOF + .24        # roof deck top
TY = -.15                # the Turret pivot's y (the old model's)


def _pad(a):
    """The cast pad (its edge a 45-degree kerb all round), joints, dust; two jersey barriers at the front-left."""
    outline = [(-2.6, -2.35), (-2.35, -2.6), (2.35, -2.6), (2.6, -2.35), (2.6, 2.35), (2.35, 2.6), (-1.6, 2.6),
               (-2.6, 1.6)]
    k.extrude(a.part('Base', 'Concrete'), outline, PAD, loc=(0, 0, PAD / 2), axis='Z', chamfer=.05, corner=.05,
              taper=(.904, .904), caps=(False, True))
    # The pad is laid in precast slabs: their joints, an oil stain and tyre scuffs where the resupply truck stops.
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-2, 3):
        v = i * .85
        j.box((4.5, .03, .01), loc=(0, v, PAD + .003), bevel=0)
        j.box((.03, 4.5, .01), loc=(v, 0, PAD + .003), bevel=0)
    st = a.part('Stains', 'Charred')
    st.box((.7, .5, .008), loc=(1.3, 2.25, PAD + .006), rot=(0, 0, .4), bevel=0)
    for dx in (-.45, .45):
        st.box((.25, 1.4, .006), loc=(-1.0 + dx, -2.1, PAD + .006), rot=(0, 0, .1), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((1.4, .12, .012), loc=(.6, 2.2, PAD + .004), bevel=0)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 2.3, math.sin(u) * 2.3, PAD), radius=1.0, k=.28)
    K.dust(a, (0, 0, PAD), radius=3.0, k=.18)
    bar = a.part('Barriers', 'Concrete')
    bolts = a.part('Kit_bolts', 'Steel')
    for (x, y, yaw) in ((1.75, -2.0, 0.0), (2.05, -1.05, R90)):
        k.extrude(bar, [(-.3, 0), (.3, 0), (.12, .25), (.08, .8), (-.08, .8), (-.12, .25)], 1.2, loc=(x, y, PAD),
                  rot=(0, 0, yaw), axis='X', chamfer=.02)
        stripe = (x, y - .19, PAD + .55) if yaw == 0 else (x - .19, y, PAD + .55)
        a.part('Barrier_stripes', 'SafetyStripe').box((1.2, .02, .1), loc=stripe, rot=(0, 0, yaw), bevel=0)
        for f in (-.45, .45):
            bolts.cyl(.04, .05, loc=(x + f * math.cos(yaw), y + f * math.sin(yaw), PAD + .82), seg=6, bevel=0)


def _blockhouse(a):
    """The battered concrete blockhouse: walls with formwork lifts, slit, porch and door, form ties, the Team band
    under the roof, the roof slab with its parapet and sandbag course, a rail at the rear, the ladder with its cage,
    the gas-filter vent, intake, antenna, conduit and lamp."""
    walls = a.part('Walls', 'Plaster')
    k.extrude(walls, [(-1.75, -1.75), (1.75, -1.75), (1.75, 1.75), (-1.75, 1.75)], WALL_H,
              loc=(0, 0, PAD + WALL_H / 2), axis='Z', corner=.09, taper=(.9, .9), caps=(False, False))
    for s in (-1, 1):
        for h in (.45, .9, 1.35, 1.8, 2.2):
            off = 1.75 - .175 * h / WALL_H
            W.lift_lines(a, (s * off, 0, PAD), 'y', 3.4 - .35 * h / WALL_H, (h,), s)
            if s < 0 or h < .5:
                W.lift_lines(a, (0, s * off, PAD), 'x', 3.4 - .35 * h / WALL_H, (h,), s)
    sl = a.part('Slits', 'Undercarriage')
    sl.box((1.5, .06, .22), loc=(0, -1.655, PAD + 1.55), rot=(.07, 0, 0), bevel=0)
    k.extrude(a.part('Slit_frames', 'Steel'), [(-.85, -.18), (.85, -.18), (.85, .18), (-.85, .18)], .06,
              loc=(0, -1.67, PAD + 1.55), rot=(R90 + .07, 0, 0), axis='Z', chamfer=0)
    for s in (-1, 1):
        sl.box((.06, .7, .14), loc=(s * 1.655, -.3, PAD + 1.6), rot=(0, -s * .07, 0), bevel=0)
        a.part('Slit_frames', 'Steel').box((.03, .8, .04), loc=(s * 1.68, -.3, PAD + 1.71), bevel=0)
    # The door in a cast porch (the walls are battered; the porch face is upright), a step up to it.
    W.slab(a.part('Door_porch', 'Plaster'), (1.35, .4, 2.3), (-.5, 1.72, PAD), caps=(False, True))
    K.door(a, (-.5, 1.93, PAD + .18), (.9, 1.85), normal=(0, 1, 0), mat='Armor')
    a.part('Door_hazard', 'Hazard').box((1.2, .04, .1), loc=(-.5, 1.935, PAD + 2.1), bevel=0)
    W.slab(a.part('Steps', 'Concrete'), (1.1, .3, .18), (-.5, 2.07, PAD), caps=(False, True), chamfer=.02)
    ties = a.part('Base_ties', 'Steel')
    for s in (-1, 1):
        for f in (-.3, .3):
            ties.cyl(.03, .03, loc=(s * 1.715, f * 3, PAD + .6), rot=(0, R90, 0), seg=4, bevel=0)
            ties.cyl(.03, .03, loc=(f * 3, -1.715, PAD + .6), rot=(R90, 0, 0), seg=4, bevel=0)
    team = a.part('Team_band', 'Team')
    for s in (-1, 1):
        K.team_band(team, (s * 1.62, 0, ROOF - .35), (.04, 3.1, .32))
    K.team_band(team, (0, -1.62, ROOF - .35), (3.1, .04, .32))
    # The roof slab (overhanging, its underside never seen), lifting eyes, the parapet on three sides with drain
    # spouts, a sandbag course on the front and left parapets.
    k.extrude(a.part('Roof', 'Concrete'), [(-1.95, -1.95), (1.95, -1.95), (1.95, 1.95), (-1.95, 1.95)], .24,
              loc=(0, 0, ROOF + .12), axis='Z', chamfer=.05, corner=.05, caps=(False, True))
    eyes = a.part('Kit_hooks', 'Steel')
    for sx in (-1, 1):
        eyes.box((.12, .03, .1), loc=(sx * 1.4, 1.4, DECK + .04), bevel=0)
    par = a.part('Parapet', 'Plaster')
    for (x, y, w, d) in ((0, -1.82, 3.6, .22), (1.82, 0, .22, 3.4), (-1.82, -.9, .22, 1.6)):
        W.slab(par, (w, d, .48), (x, y, DECK), caps=(False, True), chamfer=.04)
    sp = a.part('Drain_spouts', 'Steel')
    for (x, y, yaw) in ((1.0, -1.98, 0), (-1.0, -1.98, 0), (1.98, .9, R90), (1.98, -.9, R90)):
        sp.box((.1, .25, .08), loc=(x, y, DECK + .02), rot=(0, 0, yaw), bevel=0)
    W.bags(a, [(-1.6, -1.82, DECK + .48), (1.6, -1.82, DECK + .48)], layers=1, bag=(.62, .3, .17), seed=1)
    W.bags(a, [(1.82, -1.5, DECK + .48), (1.82, 1.5, DECK + .48)], layers=1, bag=(.62, .3, .17), seed=2)
    K.railing(a.part('Railings', 'Steel'), [(-1.92, 1.2, DECK), (-1.92, 1.92, DECK), (1.92, 1.92, DECK),
                                            (1.92, -1.92, DECK), (-1.92, -1.92, DECK), (-1.92, .35, DECK)], h=1.0,
              post=.55, r=.02)
    dj = a.part('Deck_joints', 'Undercarriage')
    for i in range(-2, 3):
        v = i * .65
        dj.box((3.4, .03, .01), loc=(0, v, DECK + .003), bevel=0)
        dj.box((.03, 3.4, .01), loc=(v, 0, DECK + .003), bevel=0)
    # The ladder up the right wall with its safety cage hoops.
    K.ladder(a.part('Ladders', 'Steel'), (-1.95, .8, PAD), (-1.95, .8, DECK + .9), width=.45, step=.32, r=.02)
    cage = a.part('Ladder_cage', 'Steel')
    for z in (PAD + 2.0, PAD + 2.6, DECK + .6):
        cage.tube([(-1.95, .55, z), (-2.3, .55, z), (-2.3, 1.05, z), (-1.95, 1.05, z)], .015, seg=3, caps=False)
    for y in (.55, 1.05):
        cage.tube([(-2.3, y, PAD + 2.0), (-2.3, y, DECK + .6)], .015, seg=3, caps=False)
    # Roof fittings: the gas-filter vent, a periscope, the warning beacon, the radio and its whip; wall intake,
    # conduit with clips and its junction box, the door lamp.
    k.lathe(a.part('Vents', 'Steel'), [(.09, 0), (.09, .5), (.24, .52), (.24, .6), (0, .66)], loc=(1.3, 1.3, DECK),
            seg=8, worn=(3,))
    K.periscope(a, (-1.2, -1.4, DECK), facing=(0, -1, 0))
    K.beacon(a, (1.6, -1.6, DECK + .48))
    K.grille(a, (1.62, .9, PAD + 1.9), .5, .35, facing=(1, 0, 0), slats=4)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.45, 1.6, DECK), h=2.0, r=.025)
    k.block(a.part('Radio_box', 'Armor'), (.3, .22, .3), loc=(1.45, 1.35, DECK), chamfer=.02)
    a.part('Lamps', 'Lamp').box((.22, .06, .12), loc=(.5, 1.63, ROOF - .2), rot=(-.3, 0, 0), bevel=0)
    a.part('Lamp_rims', 'Armor').box((.28, .1, .06), loc=(.5, 1.62, ROOF - .1), bevel=0)
    cab = a.part('Kit_cables', 'Undercarriage')
    cab.tube([(1.45, 1.62, DECK + .1), (1.7, 1.75, DECK), (1.75, 1.75, PAD + .3), (2.1, 2.2, PAD + .02)], .02, seg=4)
    con = a.part('Conduit', 'Steel')
    con.tube([(.9, 1.66, PAD + .4), (.9, 1.6, ROOF - .1)], .025, seg=4)
    for z in (.9, 1.6, 2.2):
        con.box((.08, .04, .03), loc=(.9, 1.68 - z * .02, PAD + z), bevel=0)
    k.block(a.part('Junction_box', 'Armor'), (.3, .12, .36), loc=(.9, 1.7, PAD + .1), chamfer=.015)


def _yard(a):
    """Round the blockhouse: missile crates and an ammunition box stack by the door, a spare-round rack, the cable
    reel, a jerrycan, the floodlight, an extinguisher, a fuel drum and a sign board."""
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(crates, straps, (1.0, .4, .3), (1.0, 2.05, PAD), rot=(0, 0, .08))
    K.crate(crates, straps, (1.0, .4, .3), (1.0, 2.05, PAD + .3), rot=(0, 0, -.05), bands=1)
    W.stack(a, (1.95, 1.75, PAD), n=3, size=(.5, .28, .22), yaw=R90, seed=3)
    rack = a.part('Rocket_rack', 'Wood')
    for y in (-.6, .6):
        rack.box((.5, .08, .4), loc=(2.1, y, PAD + .2), bevel=0)
    for i in range(2):
        k.lathe(a.part('Spare_rounds', 'Fuel'), [(.1, -.95), (.1, .95)], loc=(2.1 + (i - .5) * .23, 0, PAD + .48),
                rot=(R90, 0, 0), seg=8, worn=(0, 1))
        for y in (-.9, .9):
            a.part('Spare_round_caps', 'Undercarriage').cyl(.115, .06, loc=(2.1 + (i - .5) * .23, y, PAD + .48),
                                                          rot=(R90, 0, 0), seg=6, bevel=0)
    reel = a.part('Cable_reel', 'Wood')
    for dx in (-.2, .2):
        reel.cyl(.32, .05, loc=(-1.65 + dx, 2.12, PAD + .32), rot=(0, R90, 0), seg=10, bevel=0)
    a.part('Cable_reel_core', 'Rubber').cyl(.2, .36, loc=(-1.65, 2.12, PAD + .32), rot=(0, R90, 0), seg=10, bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-2.1, 1.55, PAD), rot=(0, 0, .4))
    K.fuel_drum(a.part('Fuel_drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (2.0, 1.15, PAD), r=.26, h=.8)
    K.floodlight(a, (-2.2, -1.4, PAD), facing=(-.3, -1, -.4), pole=2.4)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .4), (.04, .46), (0, .48)], loc=(.35, 1.95, PAD),
            seg=8, worn=(1,))
    sign = a.part('Signs', 'PlasterWhite')
    k.block(sign, (.7, .04, .45), loc=(-1.4, -2.25, PAD + .9), chamfer=0)
    a.part('Sign_posts', 'Steel').cyl(.03, .9, loc=(-1.4, -2.22, PAD + .45), seg=5, bevel=0)
    a.part('Hazard_marks', 'Hazard').box((.66, .045, .08), loc=(-1.4, -2.27, PAD + 1.05), bevel=0)


def emplacement(a):
    _pad(a)
    _blockhouse(a)
    _yard(a)


# ============================================================================= the launchers
def _race(a, z, r=.62):
    k.ring(a.part('Race', 'Steel'), [(r * .96, -.02), (r * 1.06, -.02), (r * 1.06, .06), (r * 1.02, .1), (r * .96, .1)],
           loc=(0, TY, z), seg=14, worn=(3,))


def _container(a, parent, x, y0, z, length, el=0.0, r=.085, name='ATGM_pod'):
    """One transport-launch container along -Y (raised el radians) from y0: the tube with its end rings, the front
    cap's dark bore, a carrying band and the umbilical box. Returns the mouth's local point."""
    d = (0, -math.cos(el), math.sin(el))
    rot = (R90 - el, 0, 0)
    c = (x + d[0] * length / 2, y0 + d[1] * length / 2, z + d[2] * length / 2)
    k.lathe(a.part(name, 'Team', parent), [(r, -length / 2), (r, length / 2)], loc=c, rot=rot, seg=8,
            caps=(False, False), worn=(0, 1))
    rings = a.part('Launcher_bands', 'Armor', parent)
    for f in (-.47, .47):
        p = (c[0], c[1] + d[1] * f * length, c[2] + d[2] * f * length)
        rings.cyl(r * 1.16, .07, loc=p, rot=rot, seg=8, bevel=0)
    mouth = (x + d[0] * length, y0 + d[1] * length, z + d[2] * length)
    a.part('Launcher_bores', 'Undercarriage', parent).cyl(r * .98, .02, loc=(mouth[0], mouth[1] + .012, mouth[2]),
                                                         rot=rot, seg=8, bevel=0)
    k.block(a.part('Launcher_frame', 'Armor', parent), (.08, .16, .1), loc=(x - math.copysign(r + .04, x or 1),
                                                                           c[1], c[2] - .02), rot=(-el, 0, 0),
            chamfer=0)
    return mouth


def _sight(a, parent, loc, w=.36, h=.3, d=.42):
    """The guidance box between the tubes: housing, three lenses (thermal, TV, laser), a hood over them."""
    x, y, z = loc
    k.block(a.part('Launcher_sight', 'Armor', parent), (w, d, h), loc=(x, y, z - h / 2), chamfer=.03)
    lens = a.part('Launcher_lens', 'Glass', parent)
    lens.cyl(.075, .03, loc=(x - .08, y - d / 2 - .01, z - h * .45), rot=(R90, 0, 0), seg=10, bevel=0)
    lens.cyl(.045, .03, loc=(x + .1, y - d / 2 - .01, z - h * .35), rot=(R90, 0, 0), seg=8, bevel=0)
    lens.box((.08, .03, .06), loc=(x + .1, y - d / 2 - .01, z - h * .72), bevel=0)
    a.part('Launcher_sight', 'Armor', parent).box((w + .04, .16, .025), loc=(x, y - d / 2 - .05, z + .01), bevel=0)
    K.handle(a.part('Kit_handles', 'Steel', parent), (x - w / 2 + .05, y + .1, z + .01), (x + w / 2 - .05, y + .1,
                                                                                         z + .01), (0, 0, 1), h=.06)


def _pedestal(a, t, h=.55, shield=True, sw=1.5):
    """The turning pedestal on the race: a column, the traverse drum, the cable loom and (shield=True) the armoured
    shield with its sight window and Team band. Returns the steel part."""
    st = a.part('Turret_steel', 'Steel', t)
    k.lathe(a.part('Turret_socket', 'Armor', t), [(.5, 0), (.5, .1), (.42, .16), (.22, .2), (.18, h), (0, h)],
            seg=12, worn=(1, 2))
    st.cyl(.25, .12, loc=(0, 0, h * .55), seg=10, bevel=0)
    a.part('Kit_cables', 'Undercarriage', t).tube([(.22, .1, .16), (.3, .25, h * .5), (.12, .2, h)], .025, seg=4)
    if shield:
        arm = a.part('Turret_armor', 'Armor', t)
        k.extrude(arm, [(-sw / 2, 0), (sw / 2, 0), (sw / 2 - .1, .75), (.25, .82), (-.25, .82), (-sw / 2 + .1, .75)],
                  .05, loc=(0, -.42, .12), rot=(R90 - .2, 0, 0), axis='Z', chamfer=.012, corner=.01)
        for s in (-1, 1):
            k.extrude(arm, [(-.18, 0), (.18, 0), (.15, .62), (-.15, .62)], .04, loc=(s * (sw / 2 + .1), -.3, .12),
                      rot=(R90 - .1, 0, s * .6), axis='Z', chamfer=.01)
        a.part('Turret_glass', 'Glass', t).box((.3, .02, .12), loc=(0, -.355, .62), rot=(-.2, 0, 0), bevel=0)
        a.part('Turret_band', 'Team', t).box((sw - .2, .02, .1), loc=(0, -.415, .3), rot=(-.2, 0, 0), bevel=0)
        K.rivet_line(a.part('Kit_rivets', 'Steel', t), (-sw / 2 + .12, -.43, .2), (sw / 2 - .12, -.43, .2),
                     (0, -1, .2), pitch=.32, r=.016)
    return st


def _yoke(a, t, z, half, depth=.5):
    """The launcher yoke: two side arms from the pedestal to the trunnion at height z, the trunnion tube and the
    elevating gear sector."""
    fr = a.part('Launcher', 'Armor', t)
    for s in (-1, 1):
        k.extrude(fr, [(-.15, 0), (.15, 0), (.1, z - .35), (-.1, z - .35)], .06, loc=(s * half, 0, .35),
                  axis='X', chamfer=.015)
    st = a.part('Turret_steel', 'Steel', t)
    st.cyl(.05, half * 2 + .12, loc=(0, 0, z), rot=(0, R90, 0), seg=8, bevel=0)
    k.extrude(a.part('Launcher', 'Armor', t), [(-.18, -.12), (.18, -.12), (.12, .12), (-.12, .12)], .05,
              loc=(half - .06, 0, z - .1), axis='X', chamfer=0)
    return fr


def _muzzles(a, t, mouths):
    K.suffixed(a)
    for i, p in enumerate(mouths):
        a.pivot(K.name('Muzzle_missile', i), p, t)
    a.pivot('Muzzle_main', mouths[0], t)


def atgm_tower(a):
    """atgm_tower: the base Kornet-EM-class twin launcher on the race (see the module docstring)."""
    emplacement(a)
    _race(a, DECK)
    t = a.pivot('Turret', (0, TY, 3.31))
    _pedestal(a, t)
    zt = .95
    _yoke(a, t, zt - .05, .62)
    mouths = [_container(a, t, s * .5, .3, zt, 1.81) for s in (-1, 1)]
    _sight(a, t, (0, -.1, zt + .2))
    _muzzles(a, t, mouths)
    k.clean(a)


def atgm_tower_a(a):
    """atgm_tower_a: the top-attack launcher raised on its guyed column (see the module docstring)."""
    emplacement(a)
    _race(a, DECK, r=.5)
    # The column: a tapered tube with its collar, the base flange with gussets, rungs, a cable trunk, guy wires.
    col = a.part('Launch_column', 'Armor')
    top = 5.11 - .12
    k.lathe(col, [(.3, DECK), (.3, DECK + .12), (.2, DECK + .2), (.17, top)], loc=(0, TY, 0), seg=12, worn=(1,))
    band = a.part('Launch_column_band', 'Team')
    band.cyl(.185, .25, loc=(0, TY, DECK + 1.1), seg=12, bevel=0)
    k.lathe(a.part('Launch_collar', 'Steel'), [(.17, top - .1), (.3, top - .06), (.3, top + .06), (.17, top + .1)],
            loc=(0, TY, 0), seg=12, worn=(2,))
    gus = a.part('Column_gussets', 'Steel')
    for i in range(4):
        u = i * TAU / 4 + TAU / 8
        gus.box((.03, .3, .3), loc=(math.cos(u) * .3, TY + math.sin(u) * .3, DECK + .2), rot=(0, 0, u - R90),
                bevel=0)
    rungs = a.part('Ladders', 'Steel')
    for j in range(5):
        z = DECK + .5 + j * .3
        rungs.tube([(-.16, TY + .1, z), (-.3, TY + .1, z), (-.3, TY - .1, z), (-.16, TY - .1, z)], .015, seg=3,
                   caps=False)
    a.part('Kit_cables', 'Undercarriage').tube([(.19, TY + .05, DECK + .05), (.19, TY + .05, top - .1)], .03, seg=4)
    guys = a.part('Guy_wires', 'Steel')
    for (x, y) in ((1.6, -1.6), (-1.6, -1.6), (1.6, 1.5), (-1.5, 1.5)):
        guys.tube([(x * .1, TY + y * .1, top - .35), (x, y, DECK + .3)], .008, seg=3)
        k.block(a.part('Guy_anchors', 'Steel'), (.12, .12, .06), loc=(x, y, DECK + .27), chamfer=0)
    t = a.pivot('Turret', (0, TY, 5.11))
    st = _pedestal(a, t, h=.4, shield=False)
    # The command launch unit on a short arm, its sunshade; the launch box pair elevated 15 degrees.
    el = math.radians(15)
    zt = .95
    _yoke(a, t, zt - .1, .56)
    mouths = [_container(a, t, s * .5, .35, zt - .05, 1.62, el=el, r=.095) for s in (-1, 1)]
    # A shroud over each launch box (the top-attack seeker's sunshield), the CLU between them.
    sh = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.block(sh, (.26, 1.3, .03), loc=(s * .5, -.25, zt + .25), rot=(-el, 0, 0), chamfer=0)
    _sight(a, t, (0, -.05, zt + .25), w=.32, h=.34, d=.36)
    st.tube([(0, .1, .4), (0, .05, zt - .1)], .05, seg=6)
    k.block(a.part('Clu_battery', 'Fuel', t), (.22, .16, .2), loc=(.0, .28, zt - .2), chamfer=.02)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.3, .35, .5), h=.9, r=.02)
    _muzzles(a, t, mouths)
    k.clean(a)


def atgm_tower_b(a):
    """atgm_tower_b: four containers in two stacked pairs and the search radar on its post (module docstring)."""
    emplacement(a)
    _race(a, DECK)
    t = a.pivot('Turret', (0, TY, 3.31))
    _pedestal(a, t, sw=1.7)
    _yoke(a, t, .9, .72)
    mouths = []
    for zt in (1.15, .75):
        for s in (-1, 1):
            mouths.append(_container(a, t, s * .5, .3, zt, 1.81, r=.08))
    # The pair frames tying each stacked pair together, a Team plate on the frame.
    fr = a.part('Launcher_frame', 'Armor', t)
    for s in (-1, 1):
        for y in (.05, -1.0):
            fr.box((.24, .08, .58), loc=(s * .5, y, .95), bevel=0)
    _sight(a, t, (0, -.15, 1.15), w=.34, h=.32)
    # The search radar: a post behind the launcher, the Radar pivot turning a flat array with its back frame.
    a.part('Radar_post', 'Steel', t).cyl(.05, .85, loc=(0, .62, .52), seg=8, bevel=0)
    a.part('Radar_post', 'Steel', t).limb((0, .2, .3), (0, .62, .3), .08, .08, bevel=0)
    r = a.pivot('Radar', (0, .62, .95), t)
    k.block(a.part('Radar_array', 'Armor', r), (.9, .08, .45), loc=(0, 0, .02), chamfer=.02)
    a.part('Radar_face', 'Undercarriage', r).box((.82, .02, .38), loc=(0, -.05, .245), bevel=0)
    rb = a.part('Radar_frame', 'Steel', r)
    rb.box((.9, .04, .04), loc=(0, .06, .25), bevel=0)
    rb.box((.04, .04, .45), loc=(0, .06, .25), bevel=0)
    _muzzles(a, t, [mouths[0], mouths[1], mouths[2], mouths[3]])
    k.clean(a)


BUILDERS = {
    'atgm_tower': (atgm_tower, dict(ao_distance=.6, grime_height=.45, ao_strength=.65)),
    'atgm_tower_a': (atgm_tower_a, dict(ao_distance=.6, grime_height=.45, ao_strength=.65)),
    'atgm_tower_b': (atgm_tower_b, dict(ao_distance=.6, grime_height=.45, ao_strength=.65)),
}
