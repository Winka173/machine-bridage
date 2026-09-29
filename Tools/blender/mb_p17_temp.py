"""Machine Brigade prompt 17: TEMPORARY stand-in models for the new units (asset debt, to be replaced
by full builds). Simple but clean silhouettes in the kit's style, built with frontier_kit and the shared
kits of mb_air / mb_air2 / mb_air3 / mb_vehicles / mb_siege.

Conventions as everywhere: metres, +Z up, Blender -Y is the front (Unity +Z). Team / TeamGlow parts are
recoloured per army at runtime. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).
  * stealth_fighter: faceted twin-tail stealth fighter (F-22 / Su-57 lineage), fighter_jet's size
    (19 x 12.7 m), origin at the fuselage centre (it flies). Dark Armor body, Team wings and tails.
    `Muzzle_missile` between the noses of the two missiles on trapezes under the open main bays,
    `Muzzle_bomb` at the nose of the guided bomb in the rear centre bay, `Muzzle_gun` at the cannon on
    the left (+X) upper fuselage.
  * wingman_drone: loyal-wingman drone (XQ-58 lineage), 0.65 x fighter_jet's length, no cockpit, a
    dorsal intake, V-tail and a top exhaust; `Muzzle_missile` between the two missiles under the open
    belly bay.
  * laser_tank: tank-destroyer hull (tank_destroyer's) with a low boxy `Turret`; the thick emitter tube
    is `Main_cannon` (with Main_cannon_collar / _fins / _housing / _lens, all elevating with it),
    `Muzzle_main` at the lens inside the housing lip, `Muzzle_mg` at the coaxial MG port (MG_port,
    fixed to the turret).
  * shield_carrier: 8x8 wheeled carrier, `Turret` is the roof HMG ring (`Main_cannon` barrel,
    `Muzzle_main` at its flash hider); the shield `Emitter` (dish, ring, three prongs, glowing node) on
    a short mast is decoration.
  * bunker_vehicle: redrawn in mb_p21_models (play-test 4).
  * swarm_carrier: high-wing four-turboprop drone carrier (C-130 lineage, heavy_bomber's size),
    origin at the fuselage centre. `Propeller` .. `Propeller_4` (left to right, as sky_gunship) spin
    about local Y; `Muzzle_drone` at the rear of the open belly bay with two rows of FPV drones.
  * shield_tower: shield-generator tower for a large base slot (7.2 x 7.2 m pad, 9.2 m): armoured base,
    four capacitor drums, a finned emitter pylon; the glowing orb, its ring and spokes are `Emitter`.
  * cp_relay: CP relay station for a small base slot (4 x 4 m pad): equipment shelter, lattice comms
    mast with two dish antennas, a stack of supply crates.
"""
import math

from mathutils import Vector

from frontier_kit import chamfered
from mb_air import (BACKWARD, FORWARD, LEFT, R90, RIGHT, Planform, _aam, _aam_parts, _dome, _nozzle, _sec,
                    _upright, _wing)
from mb_air2 import _turboprop
from mb_air3 import _fpv_drone
from mb_siege import crate, lattice, loop_rail
from mb_vehicles import (_antenna, _barrel, _face_box, _face_frame, _flank, _glacis, _hatch, _headlight, _periscopes,
                         _sponson_section, _taillight, _wheel, tracks)


# ----------------------------------------------------------------------------- faceted airframe kit
def _hex(y, wb, zb, w, zc, wt, zt):
    """Chined hexagonal fuselage section at y: flat belly (half-width wb at zb), sharp chine (w at zc),
    flat spine (wt at zt)."""
    return [(wb, y, zb), (w, y, zc), (wt, y, zt), (-wt, y, zt), (-w, y, zc), (-wb, y, zb)]


def _hex_at(table, y):
    """(wb, zb, w, zc, wt, zt) of a chined body [(y, wb, zb, w, zc, wt, zt)...] interpolated at y."""
    for a, b in zip(table, table[1:]):
        if a[0] <= y <= b[0]:
            k = (y - a[0]) / (b[0] - a[0])
            return [p + (q - p) * k for p, q in zip(a[1:], b[1:])]
    return list((table[0] if y < table[0][0] else table[-1])[1:])


def _hex_top(table, y, x):
    """Height of the chined body's upper skin at (x, y)."""
    wb, zb, w, zc, wt, zt = _hex_at(table, y)
    x = abs(x)
    return zt if x <= wt else zt + (zc - zt) * min(1.0, (x - wt) / (w - wt))


def _slab(part, frame, stations, apex=.42):
    """Faceted lifting surface: a diamond section (leading edge, ridge at `apex` of the chord, trailing
    edge) at each station (s, le, chord, thickness), mapped by frame(s, y, n) -> (x, y, z)."""
    rings = [[frame(s, le, 0), frame(s, le + apex * c, t / 2), frame(s, le + c, 0), frame(s, le + apex * c, -t / 2)]
             for s, le, c, t in stations]
    part.loft(rings, bevel=0)


def _bay_bomb(part, loc, h=.9, r=.12):
    """Small guided bomb (nose at -Y) with four tail fins."""
    x, y, z = loc
    part.lathe([(0, -h), (r * .55, -h * .88), (r, -h * .6), (r, h * .72), (r * .7, h)], loc=loc, rot=BACKWARD, seg=10)
    for k in range(4):
        phi = math.pi / 4 + k * R90
        part.box((.02, .3, .14), loc=(x + math.cos(phi) * (r + .05), y + h * .78, z + math.sin(phi) * (r + .05)),
                 rot=(0, R90 - phi, 0), bevel=0)


# ----------------------------------------------------------------------------- stealth fighter
SF = [(-8.9, .1, -.2, .34, -.05, .08, .14),
      (-7.4, .28, -.38, .7, -.08, .2, .36),
      (-5.2, .55, -.5, 1.25, -.1, .32, .52),
      (-3.2, 1.0, -.55, 2.1, -.12, .55, .58),
      (-.5, 1.2, -.55, 2.5, -.12, .8, .56),
      (3.8, 1.15, -.5, 2.35, -.1, .88, .5),
      (6.6, .95, -.42, 1.9, -.08, .78, .4),
      (8.0, .82, -.36, 1.55, -.06, .62, .32)]


def stealth_fighter(a):
    """Faceted stealth fighter (F-22 / Su-57 lineage), 19 x 12.7 m: a chined lifting body in dark grey,
    caret intakes under the chines, a diamond wing and stabilisers, twin canted fins, twin nozzles, a
    frameless canopy. Internal bays: two main bays with their doors open and a missile each on an
    extended trapeze, a centre bay behind them with a guided bomb, a cannon port on the left shoulder."""
    body = a.part('Fuselage', 'Armor', flat=True)
    skin = a.part('Wings', 'Team', flat=True)
    dark = a.part('Undercarriage', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Wing_lights', 'TeamGlow')
    body.loft([[(0, -9.7, -.06)]] + [_hex(*r) for r in SF], bevel=0)
    for sg in (-1, 1):
        _slab(skin, lambda s, y, n, sg=sg: (sg * s, y, -.12 - (s - 2.0) * .02 + n),
              [(2.0, -2.4, 6.6, .26), (6.3, 1.47, 1.3, .07)])                              # 42-degree diamond wing
        _slab(skin, lambda s, y, n, sg=sg: (sg * s, y, -.1 + n), [(1.3, 6.0, 2.6, .12), (4.4, 7.6, 1.0, .04)])
        fin = _upright(sg * 1.45, .1, .45)
        _slab(skin, fin, [(0, 4.2, 3.4, .14), (2.7, 6.4, 1.3, .05)])                        # canted twin fins
        glow.box((.05, .3, .04), loc=(sg * 6.31, 2.1, -.206), bevel=0)                      # wingtip lights
        glow.box((.04, .2, .04), loc=tuple(Vector(fin(2.72, 7.0, 0))), bevel=0)
    # Frameless canopy, sills buried in the spine.
    st = [(-7.7, .1, .44), (-7.0, .36, .74), (-6.0, .44, .92), (-5.0, .4, .88), (-4.1, .24, .7), (-3.6, .1, .62)]
    a.part('Canopy', 'Glass').loft([_dome(y, w, _hex_top(SF, y, w) - .06, z1, n=7) for y, w, z1 in st], bevel=0)
    a.part('Sensor', 'Glass', flat=True).box((.2, .3, .1), loc=(0, -7.8, -.36), bevel=0, taper=(.7, .7))
    # Caret intakes under the chines, dark faces 1.5 cm in front of their mouths.
    for sg in (-1, 1):
        def rect(y, x0, x1, z0, z1, sg=sg):
            return [(sg * x0, y, z0), (sg * x1, y, z0), (sg * x1, y, z1), (sg * x0, y, z1)]
        body.loft([rect(-4.8, .72, 1.52, -.64, -.14), rect(-2.0, .7, 1.45, -.62, -.12), rect(.5, .75, 1.4, -.5, -.15)],
                  bevel=0)
        dark.box((.74, .02, .44), loc=(sg * 1.12, -4.825, -.39), bevel=0)
        _nozzle(a, sg * .7, 7.55, -.05, .38, 1.05, seg=12)
    # Main bays: dark liners, a keel between them, doors hanging open at the outer edges, one missile each
    # on an extended trapeze below the belly. Muzzle_missile between the two noses.
    doors = a.part('Bay_doors', 'Armor', flat=True)
    for sg in (-1, 1):
        x = sg * .35
        dark.box((.52, 3.6, .02), loc=(x, -1.2, -.57), bevel=0)
        doors.box((.03, 3.4, .53), loc=(sg * .66, -1.2, -.785), bevel=0)
        for dy in (-.6, .6):
            steel.limb((x, -1.2 + dy, -.53), (x, -1.2 + dy, -.87), .05, .05, bevel=0)
    body.box((.1, 3.6, .1), loc=(0, -1.2, -.58), bevel=0)
    aams = _aam_parts(a)
    for sg in (-1, 1):
        _aam(aams, (sg * .35, -1.2, -.95), length=3.0, r=.085, canards=False, fin=1.7)
    a.pivot('Muzzle_missile', (0, -2.7, -.95))
    # Centre bay behind them: a guided bomb on a rack between two open doors; Muzzle_bomb at its nose.
    dark.box((.7, 2.4, .02), loc=(0, 2.1, -.56), bevel=0)
    for sg in (-1, 1):
        doors.box((.03, 2.2, .45), loc=(sg * .38, 2.1, -.725), bevel=0)
    steel.limb((0, 2.1, -.5), (0, 2.1, -.69), .06, .06, bevel=0)
    _bay_bomb(a.part('Bay_stores', 'Armor'), (0, 2.1, -.8))
    a.pivot('Muzzle_bomb', (0, 2.1 - .9 - .01, -.8))
    # Cannon on the left shoulder (+X, the pilot's left): fairing, barrel and muzzle ring.
    gx, gy = 1.25, -3.9
    gz = _hex_top(SF, gy, gx) + .1
    body.box((.24, 1.2, .2), loc=(gx, -3.3, _hex_top(SF, -3.3, gx)), bevel=0, taper=(.6, .9))
    steel.cyl(.04, .55, loc=(gx, gy - .1, gz), rot=FORWARD, seg=8, bevel=0)
    steel.cyl(.055, .08, loc=(gx, gy - .36, gz), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (gx, gy - .41, gz))
    a.part('Beacon', 'TeamGlow').sphere(.045, loc=(0, 8.03, .1), seg=8, rings=5)


# ----------------------------------------------------------------------------- loyal wingman drone
WD = [(-5.7, .1, -.18, .3, -.04, .08, .12),
      (-4.2, .26, -.34, .56, -.06, .18, .26),
      (-1.2, .4, -.44, .74, -.06, .28, .34),
      (2.4, .4, -.42, .7, -.05, .3, .36),
      (4.8, .28, -.3, .52, -.02, .26, .34),
      (5.9, .18, -.18, .34, 0, .2, .28)]


def wingman_drone(a):
    """Loyal-wingman drone (XQ-58 / S-70 lineage), 12.3 x 10.6 m: a chined fuselage with no cockpit, a
    chin sensor window, a dorsal intake, a swept wing, a dark V-tail and a flat exhaust on top at the
    back; the belly bay's doors fold out sideways under two missiles on a trapeze."""
    body = a.part('Fuselage', 'Team', flat=True)
    skin = a.part('Wings', 'Team', flat=True)
    armor = a.part('Armor', 'Armor', flat=True)
    dark = a.part('Undercarriage', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Wing_lights', 'TeamGlow')
    body.loft([[(0, -6.35, -.04)]] + [_hex(*r) for r in WD], bevel=0)
    a.part('Sensor', 'Glass', flat=True).box((.24, .5, .06), loc=(0, -4.9, -.26), bevel=0, taper=(.7, .8))
    for sg in (-1, 1):
        _slab(skin, lambda s, y, n, sg=sg: (sg * s, y, -.08 + n), [(.5, -.9, 3.1, .2), (5.3, 2.1, .9, .06)])
        _slab(armor, _upright(sg * .18, .18, .85), [(0, 4.0, 1.9, .12), (2.1, 5.5, .75, .04)])   # V-tail
        glow.box((.05, .25, .03), loc=(sg * 5.33, 2.5, -.08), bevel=0)

    def rect(y, w, z0, z1):
        return [(-w, y, z0), (w, y, z0), (w, y, z1), (-w, y, z1)]
    # Dorsal intake: a hump from behind the nose, its dark face 1.5 cm in front of the mouth.
    armor.loft([rect(-3.0, .34, _hex_top(WD, -3.0, .34) - .06, .6), rect(-.8, .3, .2, .5), [(0, 1.4, .3)]], bevel=0)
    dark.box((.6, .02, .3), loc=(0, -3.025, .43), bevel=0)
    # Flat exhaust on top at the back, shielded by the V-tail.
    steel.box((.56, .8, .2), loc=(0, 5.55, .34), bevel=0, taper=(.9, 1))
    dark.box((.44, .02, .12), loc=(0, 5.97, .34), bevel=0)
    a.part('Exhaust_glow', 'Alloy').box((.3, .02, .05), loc=(0, 6.0, .34), bevel=0)
    # Belly bay: dark liner, doors folded out and down, two missiles on a trapeze.
    dark.box((.68, 2.8, .02), loc=(0, -.4, -.46), bevel=0)
    doors = a.part('Bay_doors', 'Team', flat=True)
    for sg in (-1, 1):
        doors.box((.42, 2.6, .03), loc=(sg * .54, -.4, -.545), rot=(0, sg * .42, 0), bevel=0)
        for dy in (-.5, .5):
            steel.limb((sg * .32, -.4 + dy, -.43), (sg * .32, -.4 + dy, -.58), .04, .04, bevel=0)
    aams = _aam_parts(a)
    for sg in (-1, 1):
        _aam(aams, (sg * .32, -.4, -.64), length=2.2, r=.07, canards=False, fin=1.7)
    a.pivot('Muzzle_missile', (0, -1.5, -.64))


# ----------------------------------------------------------------------------- laser tank
def laser_tank(a):
    """Focused-laser tank destroyer: tank_destroyer's sponson hull and running gear, a low boxy turret
    with two radiator boxes and rear cooling fins, a thick emitter tube with cooling rings and a lens in
    a steel housing (no muzzle brake), and a coaxial MG port beside it."""
    tracks(a, 1.22, 6.2, .8, .28, 7, .45, belt_width=.56, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.46, .96, 1.36, .95, 1.52, 1.16)
    hull.loft([_sponson_section(-3.5, .62, .96, 1.1, .9, 1.4, 1.24), _sponson_section(-2.1, *body),
               _sponson_section(3.25, *body), _sponson_section(3.5, .56, .96, 1.28, .92, 1.48, 1.14)], bevel=.05, seg=2)
    x, z, lean = _flank((1.52, 1.04), (1.16, 1.36), .5, .02)
    for s in (-1, 1):
        for y in (-1.4, .2, 1.8):                                                        # bolt-on plates
            armor.box((.06, 1.3, .3), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=.015, seg=1)
        _headlight(a, s * .75, -3.5, .86)
        _taillight(a, s * 1.05, 3.5, 1.12)
        steel.cyl(.1, .5, loc=(s * .55, 3.55, .95), rot=FORWARD, seg=10, bevel=.015, bseg=1)  # exhausts
        _hatch(a, s * .55, -1.85, 1.35, .26)
        _periscopes(a, [(s * .55 + dx, -2.2, 1.35, 0) for dx in (-.12, .12)])
    deck.grille(1.5, .9, loc=(0, 2.4, 1.37), rot=(-R90, 0, 0), slats=7, depth=.08, thickness=.04)
    steel.cyl(1.02, .09, loc=(0, -.2, 1.375), seg=24, bevel=.03)                           # turret ring

    t = a.pivot('Turret', (0, -.2, 1.43))
    outline = [(-.62, -1.15), (.62, -1.15), (1.05, -.7), (1.08, .95), (.8, 1.25), (-.8, 1.25), (-1.08, .95),
               (-1.05, -.7)]
    a.part('Turret_body', 'Team', t).prism(outline, .55, loc=(0, 0, .275), axis='Z', bevel=.04, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((.8, .3, .5), loc=(0, -1.22, .3), bevel=.03, taper=(.9, .9))                  # mantlet
    for s in (-1, 1):                                                                      # radiator boxes
        tarm.box((.46, .8, .34), loc=(s * .52, .55, .7), bevel=.02, seg=1)
        a.part('Radiator_grilles', 'Undercarriage', t).grille(.38, .7, loc=(s * .52, .55, .88), rot=(-R90, 0, 0),
                                                              slats=6, depth=.06, thickness=.03)
    for k in range(7):                                                                     # rear cooling fins
        tsteel.box((.04, .4, .4), loc=(-.6 + k * .2, 1.25, .27), bevel=0)
    tsteel.box((.2, .24, .2), loc=(-.55, -.7, .64), bevel=.02, seg=1)                      # sight
    a.part('Sight', 'Glass', t).box((.14, .04, .1), loc=(-.55, -.83, .66), bevel=.01, seg=1)
    _hatch(a, .42, -.25, .55, .22, parent=t)
    _antenna(a, t, -.8, -.3, .55, 1.0)
    a.part('Conduits', 'Undercarriage', t).tube([(.52, .2, .75), (.36, -.8, .62), (.22, -1.15, .45)], .05, seg=6)
    # Emitter: every part named Main_cannon* elevates together on the runtime trunnion.
    zc = .3
    a.part('Main_cannon', 'Armor', t).cyl(.17, 3.3, loc=(0, -2.9, zc), rot=FORWARD, seg=12, bevel=.015, bseg=1)
    a.part('Main_cannon_collar', 'Team', t).cyl(.27, .6, loc=(0, -1.55, zc), rot=FORWARD, seg=12, bevel=.03)
    fins = a.part('Main_cannon_fins', 'Steel', t)
    for k in range(6):
        fins.cyl(.24, .05, loc=(0, -2.15 - k * .24, zc), rot=FORWARD, seg=12, bevel=0)
    # Lens housing: a steel cup whose lip is 2 cm ahead of the glowing lens; Muzzle_main between them.
    y0 = -4.45
    a.part('Main_cannon_housing', 'Steel', t).lathe([(.16, -.05), (.25, 0), (.25, .28), (.215, .31), (.19, .31),
                                                     (.19, .25)], loc=(0, y0, zc), rot=FORWARD, seg=14)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.175, .03, loc=(0, y0 - .275, zc), rot=FORWARD, seg=14, bevel=0)
    a.pivot('Muzzle_main', (0, y0 - .30, zc), t)
    # Coaxial MG port on the turret face (fixed: it does not elevate with the emitter).
    mg = a.part('MG_port', 'Steel', t)
    mg.box((.12, .3, .12), loc=(.5, -1.25, .24), bevel=.02, seg=1)
    mg.cyl(.025, .4, loc=(.5, -1.6, .24), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.036, .08, loc=(.5, -1.79, .24), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (.5, -1.84, .24), t)


# ----------------------------------------------------------------------------- shield carrier
def shield_carrier(a):
    """8x8 wheeled shield carrier, 8.5 x 3.0 m: a slab-sided hull whose sponsons cover the wheels, thin
    bolt-on flank panels, a roof HMG on its ring (`Turret`) and the shield emitter on a short mast at
    the back (`Emitter`: a Team dish, a steel ring, three prongs and a glowing node)."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.9, -1.65, 1.35, 2.6):
        for s in (-1, 1):
            _wheel(a, s * 1.2, y, .55, .42)
            dark.box((.22, .2, .16), loc=(s * .95, y, .55), bevel=.02, seg=1)             # hub carriers
    body = (.48, 1.16, 2.0, .9, 1.5, 1.18)
    hull.loft([_sponson_section(-4.25, .62, 1.16, 1.4, .8, 1.3, 1.0), _sponson_section(-3.3, *body),
               _sponson_section(3.9, *body), _sponson_section(4.25, .55, 1.16, 1.9, .85, 1.45, 1.12)], bevel=.05, seg=2)
    x, z, lean = _flank((1.5, 1.24), (1.18, 2.0), .5, .01)
    for s in (-1, 1):
        for y in (-2.6, -1.0, .6, 2.2):                                                    # thin add-on panels
            armor.box((.04, 1.4, .56), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=.01, seg=1)
        _headlight(a, s * .6, -4.25, 1.0)
        _taillight(a, s * .95, 4.25, 1.5)
    armor.box((.9, .06, 1.0), loc=(0, 4.26, 1.1), bevel=.015, seg=1)                       # rear door
    gy, gz, grot = _glacis((-4.25, 1.4), (-3.3, 2.0), .7, .012)
    glass = a.part('Vision_blocks', 'Glass')
    for dx in (-.14, 0, .14):
        glass.box((.12, .07, .05), loc=(-.45 + dx, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    _hatch(a, -.45, -2.85, 2.0, .26)
    _hatch(a, .55, .6, 2.0, .3)
    dark.grille(.6, .7, loc=(.7, 3.45, 2.01), rot=(-R90, 0, 0), slats=5, depth=.06, thickness=.03)
    _antenna(a, None, -.95, 3.7, 2.0, 1.4)
    # Roof HMG on its ring.
    steel.cyl(.5, .08, loc=(0, -1.3, 2.02), seg=18, bevel=.02, bseg=1)
    t = a.pivot('Turret', (0, -1.3, 2.07))
    a.part('Turret_body', 'Team', t).cyl(.44, .14, loc=(0, 0, .07), seg=16, bevel=.03)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.72, .05, .42), loc=(0, -.36, .38), rot=(-.12, 0, 0), bevel=.012, seg=1, taper=(.85, 1))  # shield
    for s in (-1, 1):
        tarm.box((.05, .4, .36), loc=(s * .36, -.18, .34), bevel=.01, seg=1)
    tarm.box((.14, .24, .18), loc=(.18, .05, .33), bevel=.02, seg=1)                       # ammo can
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.06, .2, loc=(0, 0, .2), seg=8, bevel=0)                                    # pintle
    tsteel.box((.16, .5, .16), loc=(0, -.02, .34), bevel=.02, seg=1)                       # receiver
    tip = _barrel(a, t, start_y=-.27, length=1.05, radius=.032, height=.34, brake=(.07, .14, .07), seg=8,
                  style='flash')
    a.pivot('Muzzle_main', tip, t)
    # Shield emitter on a short mast.
    armor.cyl(.3, .2, loc=(0, 2.0, 2.08), seg=12, bevel=.03)
    steel.cyl(.12, .995, loc=(0, 2.0, 2.4725), seg=10, bevel=0)
    e = a.pivot('Emitter', (0, 2.0, 2.95))
    a.part('Emitter_dish', 'Team', e).lathe([(0, 0), (.35, .06), (.62, .2), (.6, .23), (.33, .1), (0, .05)], seg=18)
    a.part('Emitter_ring', 'Steel', e).torus(.62, .04, loc=(0, 0, .215), seg=20, ring=6)
    prongs = a.part('Emitter_prongs', 'Steel', e)
    for k in range(3):
        u = R90 + k * math.tau / 3
        prongs.limb((.56 * math.cos(u), .56 * math.sin(u), .2), (.1 * math.cos(u), .1 * math.sin(u), .78), .05, .05,
                    bevel=0)
    a.part('Emitter_glow', 'TeamGlow', e).sphere(.13, loc=(0, 0, .8), seg=12, rings=8)
    a.part('Emitter_core', 'TeamGlow', e).cyl(.16, .08, loc=(0, 0, .08), seg=12, bevel=0)


# ----------------------------------------------------------------------------- swarm carrier
def swarm_carrier(a):
    """Drone-carrier transport (C-130 lineage), 15.8 x 18 m: a chunky fuselage with a glazed cockpit
    and upswept tail, a high straight wing on a root fairing with four turboprops, a tall fin and
    stabilisers, landing-gear sponsons, and an open belly bay with two staggered rows of FPV drones
    hanging from rails between its doors."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    glow = a.part('Wing_lights', 'TeamGlow')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=16, pt=2.6, pb=3.4)
    hull = [sec(-7.3, .5, -.55, .4), sec(-6.7, .92, -.95, .82), sec(-5.8, 1.12, -1.1, 1.0), sec(3.0, 1.15, -1.1, 1.05),
            sec(4.6, 1.02, -.62, 1.02), sec(6.4, .55, .2, .95), sec(7.7, .22, .55, .85)]
    body.loft([[(0, -7.75, -.1)]] + hull + [[(0, 8.0, .72)]], bevel=.02, seg=1)
    a.part('Canopy', 'Glass').loft([_dome(y, w, z0, z1, n=9) for y, w, z0, z1 in
                                    ((-7.2, .32, .1, .42), (-6.85, .68, .28, .84), (-6.45, .8, .42, .98),
                                     (-6.05, .62, .62, 1.02))], bevel=.02, seg=1)
    body.box((2.0, 3.8, .5), loc=(0, -.5, .88), bevel=.08, seg=1, taper=(.8, .95))        # wing-root fairing
    wing = Planform(0, 9.0, -2.0, -1.55, 3.0, 1.55, .4, .18, 1.02, 1.18)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(1.4, 4.1, .75), (5.6, 8.7, .74)])
    for x, name in ((-5.2, 'Propeller'), (-2.6, 'Propeller_2'), (2.6, 'Propeller_3'), (5.2, 'Propeller_4')):
        _turboprop(a, x, -3.7, .76 if abs(x) > 4 else .74, name, wing.te(abs(x)), 1 if x > 0 else -1)
    for s in (-1, 1):
        glow.box((.06, .3, .05), loc=(s * 9.03, -1.0, 1.18), bevel=0)                    # wingtip lights
    fin = Planform(0, 3.3, 4.7, 6.5, 3.0, 1.45, .32, .14)
    _wing(body, moving, fin, _upright(0, .85, 0), cs=[(.4, 3.0, .7)], lower=1.0)
    stab = Planform(0, 3.7, 5.9, 6.7, 2.2, 1.1, .2, .08, .92)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.6, 3.5, .7)])
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 7.72 + .06, 4.15), seg=8, rings=5)
    for s in (-1, 1):                                                                     # gear sponsons
        armor.box((.5, 3.6, .8), loc=(s * 1.2, -.2, -.72), bevel=.06, seg=1, taper=(.8, 1))
    # Open belly bay: frame, rails, two staggered rows of FPV drones (the right row 1.5 cm lower so no
    # two props share a plane) and the doors hanging open. Muzzle_drone at the back of the bay.
    dark.box((1.8, 4.4, .3), loc=(0, .2, -1.05), bevel=.03, seg=1)
    rails = a.part('Drone_rails', 'Steel')
    for x, ys, dz in ((-.3, (-1.6, -.6, .4, 1.4), 0.0), (.3, (-1.1, -.1, .9, 1.9), -.015)):
        rails.box((.06, 4.2, .1), loc=(x, .2, -1.24), bevel=0)
        for k, y in enumerate(ys):
            _fpv_drone(a, x, y, -1.42 + dz, k=k + (x > 0) * 2)
    doors = a.part('Bay_doors', 'Team')
    for s in (-1, 1):
        doors.box((.04, 4.2, .74), loc=(s * .9, .2, -1.33), bevel=0)
    a.pivot('Muzzle_drone', (0, 2.1, -1.55))


# ----------------------------------------------------------------------------- shield tower
def shield_tower(a):
    """Shield-generator tower for a large base slot (7.2 x 7.2 m pad, 9.2 m): a squat armoured base with
    plates and a lit door, four capacitor drums with glowing bands and cables, a tapered finned emitter
    pylon with conduit rings, and the `Emitter` on top: a glowing orb inside a steel ring on spokes."""
    a.part('Pad', 'Concrete').prism(chamfered(7.2, 7.2, .9), .3, loc=(0, 0, .13), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                    # z -.02 .. .28
    top = .28
    base = chamfered(4.6, 4.6, 1.2)
    z0, h, tp = .26, 1.9, .88
    a.part('Base', 'Team').prism(base, h, loc=(0, 0, z0 + h / 2), axis='Z', bevel=.05, taper=tp)   # .26 .. 2.16
    for i in (2, 4, 6):
        _face_box(a, 'Base_plates', 'Armor', _face_frame(base[i], base[(i + 1) % 8], h, tp, z0, v=.45), (1.8, 1.1, .08))
    _face_box(a, 'Door', 'Armor', _face_frame(base[0], base[1], h, tp, z0, v=.38), (1.0, 1.35, .06))
    _face_box(a, 'Door_lamp', 'Lamp', _face_frame(base[0], base[1], h, tp, z0, v=.84), (.3, .1, .08))
    for i in (1, 3, 5, 7):
        _face_box(a, 'Base_vents', 'Undercarriage', _face_frame(base[i], base[(i + 1) % 8], h, tp, z0, v=.5),
                  (.8, .5, .05))
    loop_rail(a.part('Railing', 'Steel'), [(x * .8, y * .8, 2.14) for x, y in base], h=.9)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 2.6, sy * 2.6
            a.part('Capacitors', 'Armor').cyl(.6, 1.8, loc=(x, y, top + .88), seg=16, bevel=.04)  # .26 .. 2.06
            a.part('Capacitor_caps', 'Steel').cyl(.5, .14, loc=(x, y, top + 1.8), seg=16, bevel=.03)
            bands = a.part('Capacitor_bands', 'TeamGlow')
            for zb in (.7, 1.35):
                bands.cyl(.615, .07, loc=(x, y, top + zb), seg=16, bevel=0)
            a.part('Cables', 'Undercarriage').tube([(x * .95, y * .95, 2.18), (x * .8, y * .8, 2.33),
                                                    (x * .55, y * .55, 1.78)], .07, seg=6)
    # Emitter pylon: an octagonal frustum with three Team fins, glow strips and conduit rings.
    zp0, zp1, r0, r1 = 2.14, 7.64, .85, .45
    slope = math.atan((r0 - r1) / (zp1 - zp0))
    a.part('Pylon', 'Armor').cyl(r0, zp1 - zp0, r2=r1, loc=(0, 0, (zp0 + zp1) / 2), seg=8, bevel=.03)
    fins = a.part('Pylon_fins', 'Team')
    strips = a.part('Pylon_glow', 'TeamGlow')
    for k in range(3):
        u = R90 + k * math.tau / 3
        fins.box((.42, .12, 5.0), loc=(.77 * math.cos(u), .77 * math.sin(u), 4.8), rot=(0, -slope, u), bevel=.02, seg=1)
        v = u + math.pi / 3
        strips.box((.06, .1, 4.4), loc=(.607 * math.cos(v), .607 * math.sin(v), 4.8), rot=(0, -slope, v), bevel=0)
    rings = a.part('Pylon_rings', 'Steel')
    for zr in (3.4, 5.0, 6.6):
        rings.torus(r0 - (r0 - r1) * (zr - zp0) / (zp1 - zp0) + .02, .07, loc=(0, 0, zr), seg=16, ring=6)
    a.part('Pylon_cap', 'Steel').cyl(.55, .3, loc=(0, 0, 7.76), seg=12, bevel=.04)
    a.part('Pylon_neck', 'Steel').cyl(.2, .35, loc=(0, 0, 8.05), seg=10, bevel=0)
    e = a.pivot('Emitter', (0, 0, 8.6))
    a.part('Emitter_orb', 'TeamGlow', e).sphere(.6, seg=20, rings=12)
    a.part('Emitter_ring', 'Steel', e).torus(1.35, .1, seg=32, ring=8)
    spokes = a.part('Emitter_spokes', 'Steel', e)
    nodes = a.part('Emitter_nodes', 'TeamGlow', e)
    for k in range(3):
        u = R90 + k * math.tau / 3
        spokes.limb((.4 * math.cos(u), .4 * math.sin(u), 0), (1.3 * math.cos(u), 1.3 * math.sin(u), 0), .08, .08,
                    bevel=0)
        nodes.sphere(.16, loc=(1.35 * math.cos(u), 1.35 * math.sin(u), 0), seg=10, rings=6)


# ----------------------------------------------------------------------------- CP relay station
def _dish_antenna(a, centre, facing, r, arm_to):
    """Parabolic dish (white) whose concave side faces `facing`, with a feed boom and horn, on an arm
    from its back to `arm_to` (a point on the mast)."""
    f = Vector(facing).normalized()
    rot = tuple(Vector((0, 0, 1)).rotation_difference(f).to_euler('XYZ'))
    c = Vector(centre)
    a.part('Dishes', 'Medical').lathe([(0, 0), (r * .5, r * .07), (r, r * .26), (r * .96, r * .3), (r * .48, r * .12),
                                       (0, .05)], loc=tuple(c), rot=rot, seg=16)
    mounts = a.part('Dish_mounts', 'Steel')
    mounts.limb(tuple(c + f * .02), tuple(c + f * r * .7), .03, .03, bevel=0)
    a.part('Dish_feeds', 'Armor').cyl(.06, .12, loc=tuple(c + f * r * .72), rot=rot, seg=8, bevel=0)
    mounts.limb(tuple(c + f * .02), tuple(arm_to), .06, .06, bevel=0)


def cp_relay(a):
    """CP relay station for a small base slot (4 x 4 m pad, 7.7 m): a Team equipment shelter with a lit
    door and an air conditioner, a galvanised lattice comms mast with two dish antennas, a whip and an
    obstruction light, a cable run, and a stack of supply crates."""
    a.part('Pad', 'Concrete').prism(chamfered(4.0, 4.0, .45), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                    # z -.02 .. .24
    top = .24
    sx, sy = -.75, .7
    a.part('Shelter', 'Team').box((2.2, 1.5, 1.35), loc=(sx, sy, top + .655), bevel=.04, seg=1)     # .22 .. 1.57
    a.part('Shelter_roof', 'Armor').box((2.32, 1.62, .08), loc=(sx, sy, 1.6), bevel=.02, seg=1)
    a.part('Shelter_door', 'Armor').box((.7, .05, 1.0), loc=(sx - .45, sy - .75 - .015, .78), bevel=.01, seg=1)
    a.part('Door_lamp', 'Lamp').box((.3, .12, .08), loc=(sx - .45, sy - .79, 1.38), bevel=.01, seg=1)
    a.part('Status_light', 'TeamGlow').box((.12, .06, .12), loc=(sx + .4, sy - .76, 1.2), bevel=0)
    a.part('Aircon', 'Armor').box((.24, .7, .55), loc=(sx + 1.21, sy + .1, .75), bevel=.02, seg=1)
    a.part('Aircon_grille', 'Undercarriage').grille(.5, .4, loc=(sx + 1.34, sy + .1, .75), rot=(0, 0, R90), slats=4,
                                                    depth=.06, thickness=.03)
    a.part('Roof_vent', 'Steel').cyl(.12, .2, loc=(sx - .5, sy + .3, 1.7), seg=8, bevel=0)
    mx, my, z1 = 1.15, -1.0, 6.2
    lattice(a.part('Mast', 'Steel'), mx, my, top, z1, .38, .16, 5, leg=.1, brace=.03)
    for qx in (-1, 1):
        for qy in (-1, 1):
            a.part('Footings', 'Concrete').box((.3, .3, .1), loc=(mx + qx * .38, my + qy * .38, top + .03), bevel=.02,
                                               seg=1)
    a.part('Mast_cap', 'Armor').box((.44, .44, .06), loc=(mx, my, z1 + .03), bevel=.01, seg=1)
    a.part('Whip', 'Steel').cyl(.02, 1.4, loc=(mx, my, z1 + .75), seg=6, bevel=0)
    a.part('Obstruction_light', 'LavaGlow').sphere(.06, loc=(mx, my, z1 + 1.48), seg=8, rings=5)
    a.part('Mast_beacon', 'TeamGlow').box((.08, .08, .1), loc=(mx + .18, my - .18, z1 + .1), bevel=0)

    def hw(z):
        return .38 - .22 * (z - top) / (z1 - top)
    _dish_antenna(a, (mx - .55, my - .5, 5.1), (-1, -.9, .25), .5, (mx - hw(5.1), my - hw(5.1), 5.1))
    _dish_antenna(a, (mx + .5, my + .1, 3.7), (1, .3, .15), .42, (mx + hw(3.7), my, 3.7))
    a.part('Cables', 'Undercarriage').tube([(sx + .85, sy - .72, 1.25), (.5, -.35, 1.3),
                                            (mx - hw(1.4), my + hw(1.4), 1.4)], .035, seg=6)
    crate(a, (-1.25, -1.2, top - .01), size=(1.1, .6, .45), yaw=.08)
    crate(a, (-1.2, -1.15, top + .43), size=(.9, .5, .4), yaw=-.12)
    crate(a, (-1.3, -1.2, top + .82), size=(.7, .45, .34), yaw=.3, band=False)
    crate(a, (-.2, -1.45, top - .01), size=(.8, .5, .38), yaw=.5)


BUILDERS = {
    'stealth_fighter': (stealth_fighter, dict(ao_distance=.7, ground=False)),
    'wingman_drone': (wingman_drone, dict(ao_distance=.5, ground=False)),
    'laser_tank': (laser_tank, dict(ao_distance=.6, grime_height=.55)),
    'shield_carrier': (shield_carrier, dict(ao_distance=.6, grime_height=.55)),
    'swarm_carrier': (swarm_carrier, dict(ao_distance=.9, ground=False)),
    'shield_tower': (shield_tower, dict(ao_distance=.9, grime_height=.6)),
    'cp_relay': (cp_relay, dict(ao_distance=.7, grime_height=.6)),
}
