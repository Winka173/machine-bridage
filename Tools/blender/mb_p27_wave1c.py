"""Prompt 27 wave 1c, pass A (DECISIONS "27 wave 1c pass A (lead pass, 2026-10-02)"): the first sixteen prompt 25
batch B stand-in units built as their own models on the V2 kit (mb_kit27 primitives + mb_parts27 parts), merged last
in build_assets.all_builders(). Each model keeps the runtime nodes of the stand-in it replaces (Turret, Main_cannon,
Muzzle_*, Radar, Rotor, Tail_rotor, Blade, Bombs, Point_*) and is built to its def's modelSize (length along Y with
the front at -Y, width along X, height along Z, ground at z 0; the gun or nose counts in the length).

  aa_57mm_vehicle         2S38 Derivatsiya-PVO: tracked chassis, boxy 57 mm turret, search radar on the roof
  mine_rocket_truck       BM-27 Uragan class: 8x8 truck, cab, mine-dispensing rocket pod on a turntable
  prop_attack_plane       EMB-314 Super Tucano: single turboprop, bubble canopy, underwing rocket pods
  light_attack_heli       a small stub-winged attack helicopter (AH-1Z light): tandem canopy, gun and rocket pods
  next_gen_tank           T-14 Armata: low unmanned turret set back, side screens, rear ERA
  demolition_line_vehicle M58 MICLIC: mine-roller frame ahead of the hull, line-charge rack on the rear deck
  combat_wreck_car        light car that becomes a gun pit: a car body with a roof gun and a built wreck-turret node
  drone_hijack_vehicle    EW truck with a directional hijack antenna array on a turning mast
  manpads_tower           sandbagged pit, two shoulder-launched tubes on a low tripod
  river_patrol_boat       Mark VI / riverine boat: shallow aluminium hull, pintle MG, grenade launcher
  river_gunboat           Buyan class: low hull, forward 100 mm turret, aft deckhouse
  coastal_ashm_vehicle    NSM coastal truck: four angled canisters on a flatbed
  auto_loader_howitzer    XM2001 Crusader: low tracked SPH, 155 mm barrel, autoloader bustle
  amphib_light_vehicle    EFV / AAV-7: boat hull on tracks, bow trim vane, small turret
  airborne_light_tank     M8 AGS / M10 Booker: light hull, low 105 mm turret (+ airborne_light_tank_chute)
  stealth_naval_strike    A-12 Avenger II: flying-wing, carrier folding wingtips

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front, +X the vehicle's left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_parts27 as parts
import mb_vehicles as mv
from mb_air import (LEFT, RIGHT, Planform, _bubble, _octagon, _prop_blade, _sec, _wing)
from mb_phase2 import _suffixed
from mb_phase8 import pv
from mb_vehicles import ACROSS, FORWARD, R90

TAU = math.tau
BACKWARD = (-R90, 0, 0)


# ----------------------------------------------------------------------------- shared helpers
def _tracks(a, x, length, top, wr, n, bw, sprocket_end=1):
    parts.track_unit(a, x, length, top, wr, n, bw, sprocket_end=sprocket_end, wheel_seg=8, teeth=7)


def _hull(part, prof, width, ch=.05, cn=.04, taper=1.0, loc=(0, 0, 0)):
    """Side-profile hull: prof = [(y, z)...] extruded across `width` centred on x = 0."""
    k.extrude(part, prof, width, loc=loc, axis='X', chamfer=ch, corner=cn, taper=taper)


def _house(part, plan, h, z0, ch=.05, taper=(.94, .94), loc=(0, 0)):
    """Turret house: plan = [(x, y)...] extruded up `h` from z0 (the top face is scaled by taper)."""
    k.extrude(part, plan, h, loc=(loc[0], loc[1], z0 + h / 2), axis='Z', chamfer=ch, taper=taper)


def _lights(a, w, yf, yr, zf, zr=None):
    for s in (-1, 1):
        mv._headlight(a, s * w, yf, zf, guard=False)
        mv._taillight(a, s * w * .9, yr, zr if zr is not None else zf)


def _tyre(a, x, y, r, w, s, seg=10):
    parts.road_wheel(a, (x, y, r), r, w, s, seg=seg)


def _sight(a, parent, x, y, z, r=.13):
    """A sight drum with a glass window on a turret roof."""
    k.lathe(a.part('Sight_drum', 'Armor', parent), [(r, -.1), (r, .08), (r * .8, .12)], loc=(x, y, z), seg=10,
            worn=(1,))
    a.part('Sight_glass', 'Glass', parent).box((r * 1.1, .03, r * .8), loc=(x, y - r - .01, z + .02), bevel=0)


def _gun(a, t, y0, z, length, r, brake='baffle', seg=12, x=0.0, sleeve=1.235, name='Main_cannon'):
    """Barrel on turret t from y0 forward, `Muzzle_brake` and `Muzzle_main` at the tip."""
    parts.barrel(a, name, t, x, y0, z, length, r, seg=seg, sleeve=sleeve, extractor=(.45, 1.5, .4),
                 brake_name='Muzzle_brake', brake=brake)
    a.pivot('Muzzle_main', (x, y0 - length - (.3 if brake == 'baffle' else .14), z), t)


def _points(a, ex, fire):
    a.pivot('Point_exhaust', ex)
    a.pivot('Point_fire', fire)


# ============================================================================= AA 57 mm vehicle
def aa_57mm_vehicle(a):
    """2S38 Derivatsiya-PVO: tracked chassis 5.9 m with the 57 mm barrel counted, a boxy turret with a sloped
    front, the autoloader's side boxes, a roof search radar (`Radar`) and sight."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _tracks(a, .96, 5.3, .8, .3, 6, .46)
    k.extrude(a.part('Hull_tub', 'Team'), [(-2.2, .42), (-2.3, .6), (2.9, .6), (2.95, .42)], 1.9, axis='X', chamfer=.03)
    _hull(hull, [(-2.35, .62), (-1.95, .95), (-1.55, 1.05), (2.45, 1.05), (2.9, .95), (2.92, .62)], 2.4)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -1.7, width=.07, depth=.012)
    k.cut(hull, lambda tool: k.block(tool, (1.3, .9, .12), loc=(0, 1.9, 1.04), chamfer=0))
    a.part('Deck_grille', 'Undercarriage').grille(1.2, .8, loc=(0, 1.9, 1.04), rot=(-R90, 0, 0), slats=5, depth=.08,
                                                  thickness=.05)
    for s in (-1, 1):
        mv._skirt(a, s, 1.25, -1.9, 2.7, .45, 1.0, 5, thick=.06, bolts=False)
        k.block(armor, (.4, 2.4, .18), loc=(s * 1.0, 1.2, 1.12), chamfer=.03)            # fender bins
        mv._exhaust(a, s * .7, 2.93, .8, .5, .22)
    _lights(a, 1.0, -2.33, 2.93, .86, .9)
    parts.hatch(a, -.62, -1.0, 1.05, .24)
    mv._periscopes(a, [(-.62 + dx, -1.35, 1.05, 0) for dx in (-.17, 0, .17)])
    t = a.pivot('Turret', (0, .5, 1.05))
    body = a.part('Turret_body', 'Team', t)
    _house(body, [(-.9, -1.15), (.9, -1.15), (.98, -.4), (.98, 1.05), (.8, 1.2), (-.8, 1.2), (-.98, 1.05),
                  (-.98, -.4)], .7, 0, ch=.06, taper=(.9, .9))
    k.inset(body, lambda c, n, f: n.z > .9, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Team', t)
    k.block(tarm, (.8, .34, .52), loc=(0, -1.26, .38), chamfer=.04, taper=(.9, .9))        # mantlet
    for s in (-1, 1):
        k.block(tarm, (.26, 1.3, .46), loc=(s * 1.09, .2, .3), chamfer=.04)                # autoloader boxes
        k.block(tarm, (.3, .16, .12), loc=(s * .6, -1.0, .76), chamfer=.02)
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.0, -.62, .5, s, count=3, gap=.08, r=.05, depth=.15)
    _gun(a, t, -1.4, .42, 1.55, .075, seg=12)
    _sight(a, t, -.62, -.2, .7)
    parts.hatch(a, .55, .25, .7, .24, parent=t)
    ra = a.pivot('Radar', (0, .7, .7), t)
    k.lathe(a.part('Radar_mast', 'Steel', ra), [(.12, -.04), (.1, .3), (.14, .4)], seg=8, worn=(1,))
    k.block(a.part('Radar_panel', 'Medical', ra), (1.1, .12, .52), loc=(0, 0, .62), chamfer=.04)
    k.block(a.part('Radar_back', 'Undercarriage', ra), (.9, .1, .4), loc=(0, .1, .62), chamfer=0)
    k.greebles(tarm, (0, .5, .7), (1, 0, 0), (0, 1, 0), (1.3, .5), 3, seed=2711, height=(.05, .1), chamfer=.012)
    _points(a, (.7, 2.95, .85), (0, 1.0, 1.1))
    k.clean(a)


# ============================================================================= mine rocket truck
def mine_rocket_truck(a):
    """BM-27 Uragan class: an 8x8 truck (6.09 x 2.0 x 2.6 m), cab with door lines and a brush guard, the
    mine-dispensing rocket pod (4 x 4 tubes, a hazard band) on a turntable (`Turret`, `Muzzle_main`), jacks."""
    _suffixed(a)
    cab, armor, steel = a.part('Cab', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.25, -1.0, 1.15, 2.4):
        for s in (-1, 1):
            _tyre(a, s * .64, y, .5, .4, s)
    for s in (-1, 1):
        dark.box((.2, 5.8, .3), loc=(s * .46, .1, .78), bevel=.03, seg=1)            # frame rails
        armor.box((.5, 2.6, .06), loc=(s * .66, -1.62, 1.04), bevel=.02, seg=1)        # front mudguards
        armor.box((.5, 2.6, .06), loc=(s * .66, 1.78, 1.04), bevel=.02, seg=1)
    # Cab: a sloped forward-control box, windscreens, mirrors.
    k.extrude(cab, [(-2.96, .95), (-2.96, 1.6), (-2.72, 2.2), (-1.55, 2.22), (-1.5, .95)], 1.96, axis='X',
              chamfer=.06, corner=.05)
    k.extrude(armor, [(-2.96, .55), (-2.96, .95), (-1.5, .95), (-1.5, .55)], 1.7, axis='X', chamfer=.03)
    glass = a.part('Windows', 'Glass')
    for s in (-1, 1):
        glass.box((.82, .04, .5), loc=(s * .46, -2.93, 1.85), rot=(.28, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .8, .5), loc=(s * .985, -2.2, 1.8), bevel=.01, seg=1)
        mv._headlight(a, s * .72, -2.97, 1.2, guard=False)
        mv._taillight(a, s * .6, 2.99, 1.12)
        armor.box((.05, .18, .3), loc=(s * 1.0, -2.7, 1.85), bevel=.01, seg=1)       # mirrors
        armor.box((.14, .8, .48), loc=(s * .9, -.3, .95), bevel=.03)                   # tool lockers
        steel.cyl(.07, .55, loc=(s * .75, 2.9, .6), seg=8, bevel=0)                      # rear jacks
        steel.cyl(.2, .06, loc=(s * .75, 2.9, .3), seg=10, bevel=.01, bseg=1)
    mv._rail(a, [(-.8, -2.97, .72), (-.8, -3.02, .9), (-.8, -3.02, 1.45), (.8, -3.02, 1.45), (.8, -3.02, .9),
                 (.8, -2.97, .72)], r=.03)
    steel.box((1.8, .12, .2), loc=(0, -2.99, .62), bevel=.03)
    parts.hatch(a, .45, -2.1, 2.22, .22)
    parts.antenna(a.part('Antennas', 'Steel'), (-.7, -1.8, 2.22), h=.12, r=.04)
    k.block(armor, (1.8, 3.7, .2), loc=(0, 1.2, 1.12), chamfer=.04)                      # launcher deck
    t = a.pivot('Turret', (0, 1.25, 1.22))
    tst, tar = a.part('Turret_steel', 'Steel', t), a.part('Turret_armor', 'Armor', t)
    tst.cyl(.8, .12, loc=(0, 0, .04), seg=18, bevel=.02, bseg=1)
    k.block(tar, (1.4, 1.5, .3), loc=(0, .1, .26), chamfer=.04, taper=(.92, .92))
    pod = a.part('Pod', 'Team', t)
    for s in (-1, 1):
        k.block(tar, (.14, .5, .5), loc=(s * .7, .85, .4), chamfer=.02)
    k.extrude(pod, [(-.92, -1.6), (.92, -1.6), (.92, 1.5), (-.92, 1.5)], .96, loc=(0, 0, .88), axis='Z',
              chamfer=.07, taper=(.98, .98))
    frame = a.part('Pod_frame', 'Armor', t)
    for y in (-1.5, 1.4):
        k.block(frame, (1.96, .14, 1.0), loc=(0, y, .88), chamfer=.02)
    a.part('Pod_band', 'Hazard', t).box((1.97, .1, .98), loc=(0, -.55, .88), bevel=0)
    tst.cyl(.1, 1.7, loc=(0, 1.25, .6), rot=ACROSS, seg=8, bevel=0)
    for row in (-.33, -.11, .11, .33):
        for col in (-.63, -.21, .21, .63):
            mv._tube_mouth(a, t, mv._frame((col, -1.6, .88 + row), FORWARD), .1, protrude=.06, seg=8)
    a.pivot('Muzzle_main', (0, -1.7, .88), t)
    _points(a, (.85, 2.9, 1.0), (0, 1.0, 1.3))
    k.clean(a)


# ============================================================================= prop attack plane
def prop_attack_plane(a):
    """EMB-314 Super Tucano: a lofted single-engine turboprop (6.15 m, span 6.04, 1.84 high) with a straight low
    wing, a bubble canopy over tandem seats, a T-less tail, a spinning `Propeller`, two underwing rocket pods and
    the wing guns."""
    _suffixed(a)
    body, armor, steel = a.part('Fuselage', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, moving = a.part('Undercarriage', 'Undercarriage'), a.part('Control_surfaces', 'Team')

    def sec(y, w, zb, zt, n=10):
        out = []
        for i in range(n):
            u = TAU * i / n
            out.append((w * math.cos(u), y, (zb + zt) / 2 + (zt - zb) / 2 * math.sin(u)))
        return out
    stations = [(-2.2, .3, .6, 1.02), (-1.8, .48, .46, 1.14), (-1.0, .58, .38, 1.28), (0.0, .5, .38, 1.22),
                (1.1, .36, .46, 1.04), (2.3, .18, .6, .9), (3.0, .09, .68, .86)]
    body.loft([sec(*s) for s in stations] + [[(0, 3.07, .76)]], bevel=0)
    body.loft([[(0, -2.45, .83)], sec(-2.2, .26, .62, 1.0)], bevel=0)
    # the propeller spinner and the spinning blades
    k.lathe(a.part('Spinner', 'Steel'), [(.0, 0), (.14, .1), (.22, .3), (.26, .42)], loc=(0, -2.62, .82), rot=BACKWARD,
            seg=12, worn=(2,))
    p = a.pivot('Propeller', (0, -2.66, .82))
    blades = a.part('Propeller_blades', 'Armor', p)
    for j in range(4):
        _prop_blade(blades, math.pi / 4 + j * R90, .2, 1.02, .2, .1, .045, .016, .7, .25, axis_y=.0)
    # exhaust stubs and intake
    for s in (-1, 1):
        steel.cyl(.07, .5, loc=(s * .27, -2.0, .6), rot=(-R90 + .7, 0, 0), seg=8, bevel=0)
    armor.box((.34, .5, .2), loc=(0, -2.25, .5), bevel=.04, seg=1, taper=(.9, .9))        # chin intake
    dark.box((.26, .04, .1), loc=(0, -2.52, .5), bevel=0)
    # wing, tailplane, fin
    wing = Planform(.0, 3.02, -1.02, -.7, 1.8, 1.05, .22, .11, .56, .6)
    for fr in (RIGHT, LEFT):
        _wing(body, moving, wing, fr, cs=[(.4, 1.4, .72), (1.8, 2.9, .74)], bevel=0, root=False)
    tail = Planform(0, 1.2, 2.5, 2.7, .75, .45, .07, .04, .72, .72)
    for fr in (RIGHT, LEFT):
        _wing(body, moving, tail, fr, cs=[(.1, 1.1, .6)], bevel=0)
    k.extrude(body, [(2.0, .8), (3.1, .8), (3.12, 1.78), (2.6, 1.78)], .1, axis='X', chamfer=.012, corner=.06)
    moving.box((.06, .3, .8), loc=(0, 3.18, 1.2), bevel=0)
    # canopy: tandem bubble over the cockpit
    glass = a.part('Canopy', 'Glass')
    parts.canopy(glass, a.part('Canopy_frames', 'Armor'),
                 [_bubble(-1.0, .3, 1.04, 1.28), _bubble(-.6, .34, 1.12, 1.44), _bubble(.0, .32, 1.14, 1.46),
                  _bubble(.6, .29, 1.08, 1.4), _bubble(1.05, .22, 1.0, 1.2)],
                 sill=.04, bows=(1, 3), bow_r=.02, sills=(1, 0), arch=(1, 2, 3, 4, 5, 0))
    # landing gear
    tyres = a.part('Tyres', 'Rubber')
    for s in (-1, 1):
        k.block(steel, (.07, .1, .5), loc=(s * .9, -.35, .3), rot=(0, s * .12, 0), chamfer=.012)
        tyres.cyl(.17, .1, loc=(s * .96, -.35, .17), rot=ACROSS, seg=10, bevel=.02)
    k.block(steel, (.06, .06, .45), loc=(0, -1.45, .38), chamfer=.012)
    tyres.cyl(.11, .08, loc=(0, -1.45, .12), rot=ACROSS, seg=8, bevel=.01)
    # underwing rocket pods (Muzzle_rocket / .001) and wing guns (Muzzle_gun)
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        parts.pylon(pylons, s * 1.5, -.55, -.05, .5, .38, w=.07)
        k.lathe(a.part('Pods', 'Team'), [(.0, -.05), (.1, .0), (.12, .15), (.12, .6), (.06, .72), (0, .74)],
                loc=(s * 1.5, -.7, .22), rot=BACKWARD, seg=8, worn=(2,))
        a.part('Pod_bands', 'Hazard').cyl(.125, .05, loc=(s * 1.5, -.55, .22), rot=FORWARD, seg=8, bevel=0)
        k.block(armor, (.1, .6, .12), loc=(s * 2.3, -.7, .62), chamfer=.015)          # wing gun fairings
    a.pivot('Muzzle_rocket', (-1.5, -.75, .22))
    pv(a, 'Muzzle_rocket.001', (1.5, -.75, .22))
    a.pivot('Muzzle_gun', (-2.3, -1.1, .62))
    a.pivot('Muzzle_main', (-2.3, -1.1, .62))
    a.part('Wing_lights', 'TeamGlow').box((.05, .12, .05), loc=(3.0, -.4, .6), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 2.3, .9), seg=6, rings=4)
    _points(a, (.3, -2.0, .55), (0, -.2, .8))
    k.clean(a)


# ============================================================================= light attack helicopter
def light_attack_heli(a):
    """A small stub-winged attack helicopter (3.88 x 3.16 x 1.56 m, AH-1Z light class): a narrow flat-panel
    fuselage with a tandem canopy, a tail boom with fin, a four-blade `Rotor`, a `Tail_rotor`, stub wings with a
    gun pod (`Muzzle_gun`, `.001`) and a rocket pod (`Muzzle_rocket`, `.001`) on each side, skids."""
    _suffixed(a)
    body, armor, steel = a.part('Fuselage', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, glass = a.part('Undercarriage', 'Undercarriage'), a.part('Canopy', 'Glass')
    hull = [_octagon(-1.55, .1, .34, .58), _octagon(-1.3, .22, .26, .72), _octagon(-.8, .3, .24, .78),
            _octagon(-.1, .32, .26, .86), _octagon(.5, .26, .32, .84), _octagon(.9, .16, .45, .76)]
    k.sharp_loft(body, hull, chamfer=.03)
    k.sharp_loft(body, [_octagon(.85, .14, .5, .76), _octagon(1.75, .07, .56, .72)], chamfer=.02)
    k.extrude(body, [(1.5, .62), (1.9, .6), (2.0, 1.2), (1.72, 1.2)], .06, axis='X', chamfer=.01, corner=.03)   # fin
    k.block(body, (.8, .26, .04), loc=(0, 1.75, .66), chamfer=.01, taper=(1, .8))                            # tailplane
    frames = a.part('Canopy_frames', 'Armor')
    parts.canopy(glass, frames, [_bubble(-1.3, .16, .62, .8), _bubble(-1.1, .22, .66, .96),
                                 _bubble(-.8, .24, .68, .98)], sill=.03, bows=(2,), bow_r=.016,
                 sills=(1, 0), arch=(1, 2, 3, 4, 5, 0))
    parts.canopy(glass, frames, [_bubble(-.72, .24, .7, .98), _bubble(-.45, .25, .74, 1.05),
                                 _bubble(-.1, .24, .76, 1.03), _bubble(.15, .2, .8, .95)], sill=.03, bows=(0, 3),
                 bow_r=.016, sills=(1, 0), arch=(1, 2, 3, 4, 5, 0))
    for s in (-1, 1):
        parts.engine_nacelle(body, dark, (s * .22, .55, .9), .12, .8, rot=FORWARD, seg=10)
        # stub wing, a gun pod outboard and a rocket pod inboard
        k.extrude(body, [(-.2, 0), (-.15, .04), (.02, .045), (.2, .012), (.2, -.012), (.02, -.035), (-.15, -.03)],
                  1.0, loc=(s * .85, -.3, .46), axis='X', chamfer=.012)
        parts.pylon(a.part('Pylons', 'Armor'), s * .62, -.45, -.1, .46, .36, w=.06)
        parts.rocket_pod(a, s * .62, -.62, .26, .1, .6, s, seg=8)
        k.block(armor, (.14, .7, .14), loc=(s * 1.3, -.3, .36), chamfer=.02)                      # gun pod
        steel.cyl(.03, .3, loc=(s * 1.3, -.8, .36), rot=FORWARD, seg=6, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.05, .1, .05), loc=(s * 1.58, -.25, .47), bevel=0)
        # skids on two cross tubes
        steel.cyl(.03, 1.6, loc=(s * .52, -.2, .03), rot=FORWARD, seg=6, bevel=0)
        for y in (-.7, .3):
            steel.limb((s * .26, y, .3), (s * .52, y, .06), .04, .04, bevel=0)
    a.pivot('Muzzle_gun', (-1.3, -.82, .36))
    pv(a, 'Muzzle_gun.001', (1.3, -.82, .36))
    a.pivot('Muzzle_rocket', (-.62, -.62, .26))
    pv(a, 'Muzzle_rocket.001', (.62, -.62, .26))
    # turret gun under the nose (static look), sensor ball
    armor.sphere((.1, .12, .1), loc=(0, -1.6, .3), seg=10, rings=6)
    a.part('Sensor', 'Glass').box((.1, .03, .06), loc=(0, -1.7, .32), bevel=0)
    steel.cyl(.07, .5, loc=(0, -.1, 1.05), seg=8, bevel=0)
    r = a.pivot('Rotor', (0, -.1, 1.3))
    parts.rotor_head(a, r, 4, 1.45, .17, hub=.14, phase=math.pi / 4, t=.03, cap=.06, stripe=.2, droop=.04)
    armor.cyl(.05, .1, loc=(-.07, 1.82, .98), rot=ACROSS, seg=8, bevel=0)
    tr = a.pivot('Tail_rotor', (-.13, 1.82, .98))
    parts.tail_rotor(a, tr, 4, .4, .08, t=.018, phase=math.pi / 4, side=-1)
    ant = a.part('Antennas', 'Steel')
    parts.antenna(ant, (0, .5, .84), h=.2, r=.03, seg=6)
    _points(a, (.3, .6, .9), (0, -.1, .85))
    k.clean(a)



# ============================================================================= next generation tank
def next_gen_tank(a):
    """T-14 Armata: a 7.79 m tank with the gun counted: a low flat-faced hull on seven road wheels, a low
    unmanned turret set well back with ERA blocks, APS radar panels at its corners, a remote MG (`Mount_mg`), a
    panoramic sight mast, side screens with ERA, a rear cage."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _tracks(a, 1.2, 6.2, .94, .3, 7, .5)
    k.extrude(a.part('Hull_tub', 'Team'), [(-2.55, .4), (-2.8, .75), (3.6, .85), (3.7, .4)], 2.0, axis='X', chamfer=.04, corner=.03)
    _hull(hull, [(-2.9, .78), (-2.2, 1.15), (-1.7, 1.2), (3.4, 1.2), (3.85, 1.05), (3.85, .7)], 2.75, ch=.06)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -1.6, width=.08, depth=.012)
    k.cut(hull, lambda tool: k.block(tool, (1.6, 1.0, .14), loc=(0, 2.9, 1.2), chamfer=0))
    a.part('Deck_grille', 'Undercarriage').grille(1.5, .9, loc=(0, 2.9, 1.2), rot=(-R90, 0, 0), slats=6, depth=.1,
                                                  thickness=.05)
    for s in (-1, 1):
        mv._skirt(a, s, 1.5, -2.3, 3.4, .5, 1.15, 5, thick=.07, bolts=False)
        k.block(armor, (.16, 5.4, .22), loc=(s * 1.4, .5, 1.25), chamfer=.02)
        mv._exhaust(a, s * .55, 3.84, .85, .5, .22)
        for y in (-2.9, -2.56):
            k.block(armor, (.28, .26, .12), loc=(s * .35, y - .05, 1.0), chamfer=.015)       # front ERA row
    _lights(a, 1.15, -2.9, 3.85, .95, .9)
    parts.hatch(a, -.7, -1.6, 1.2, .24, handle=False)
    t = a.pivot('Turret', (0, .9, 1.2))
    tb = a.part('Turret_body', 'Team', t)
    _house(tb, [(-.5, -1.2), (.5, -1.2), (1.05, -.7), (1.15, -.4), (1.15, 1.1), (.85, 1.45), (-.85, 1.45), (-1.15, 1.1),
                (-1.15, -.4), (-1.05, -.7)], .46, 0, ch=.05, taper=(.9, .9))
    k.inset(tb, lambda c, n, f: n.z > .9, width=.09, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.8, .3, .4), loc=(0, -1.25, .26), chamfer=.04, taper=(.9, .9))              # mantlet
    for s in (-1, 1):
        for y in (-.55, -.1, .35):
            k.block(tarm, (.1, .36, .3), loc=(s * 1.17, y, .26), chamfer=.015)              # side ERA
        for y in (-.95, -.65):
            k.block(tarm, (.3, .3, .1), loc=(s * .75, y, .5), chamfer=.015)                  # front ERA
        k.block(a.part('Aps_panels', 'Medical', t), (.28, .06, .16), loc=(s * .98, 1.2, .54), chamfer=.015)
    k.block(tarm, (1.9, .3, .34), loc=(0, 1.6, .26), chamfer=.03)                              # rear cage
    a.part('Cage_grille', 'Undercarriage', t).grille(1.7, .3, loc=(0, 1.77, .26), rot=(R90, 0, 0), slats=6, depth=.05,
                                                       thickness=.04)
    mast = a.part('Sight_mast', 'Armor', t)
    k.lathe(mast, [(.16, 0), (.16, .4), (.2, .45), (.2, .6)], loc=(.55, .3, .44), seg=10, worn=(1,))
    a.part('Sight_glass', 'Glass', t).box((.3, .05, .1), loc=(.55, .12, .66), bevel=0)
    _sight(a, t, -.5, -.3, .46, r=.1)
    _gun(a, t, -1.4, .26, 3.25, .08, brake='collar', seg=12)
    mv._coax(a, t, .36, -1.28, .3, length=.4, housing=.22)
    parts.mg_mount(a, t, (.55, .85, .5), length=.7, shield=False)
    parts.antenna(a.part('Antennas', 'Steel', t), (-.7, 1.05, .46), h=.12, r=.04)
    _points(a, (0, 3.9, .9), (0, 2.6, 1.3))
    k.clean(a)


# ============================================================================= demolition line vehicle
def demolition_line_vehicle(a):
    """M58 MICLIC: a tracked engineer hull (6.45 m with the mine-roller frame), two pushing arms ahead of the hull
    with a roller set on each (five discs on an axle), the line-charge launcher on the rear deck (a rack with a
    rocket and the cable box) and a remote MG on a small turret (`Turret`, `Main_cannon`, `Muzzle_main`)."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _tracks(a, 1.15, 5.0, .85, .3, 6, .48)
    k.extrude(a.part('Hull_tub', 'Team'), [(-1.9, .4), (-1.95, .7), (3.2, .75), (3.25, .4)], 2.0, axis='X', chamfer=.03)
    _hull(hull, [(-2.2, .72), (-1.5, 1.1), (2.9, 1.1), (3.1, .98), (3.1, .72)], 2.5)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -.9, width=.07, depth=.012)
    for s in (-1, 1):
        mv._skirt(a, s, 1.4, -1.6, 3.0, .5, 1.0, 4, thick=.07, bolts=False)
        mv._exhaust(a, s * .6, 3.08, .85, .5, .22)
    _lights(a, 1.0, -2.18, 3.1, .85, .85)
    # roller frame: two pushing arms from the bow, a cross beam and a roller set on each side
    for s in (-1, 1):
        k.block(armor, (.2, .9, .16), loc=(s * .9, -2.55, .8), chamfer=.02)
        k.block(armor, (.16, .18, .7), loc=(s * .9, -2.85, .55), chamfer=.015)
        for i in range(5):
            k.lathe(a.part('Roller_discs', 'Steel'),
                    [(.0, -.07), (.3, -.07), (.34, -.03), (.34, .03), (.3, .07), (0, .07)],
                    loc=(s * (.3 + i * .25), -2.96, .32), rot=ACROSS, seg=12, worn=(2, 3))
        k.lathe(steel, [(.06, -.7), (.06, .7)], loc=(s * .75, -2.96, .32), rot=ACROSS, seg=8)
    k.block(armor, (2.0, .2, .18), loc=(0, -2.75, .86), chamfer=.02)
    a.part('Roller_stripe', 'Hazard').box((1.7, .06, .08), loc=(0, -2.85, .92), bevel=0)
    # driver hatch and the remote MG turret
    parts.hatch(a, .6, -1.2, 1.1, .24)
    mv._periscopes(a, [(.6 + dx, -1.6, 1.1, 0) for dx in (-.17, 0, .17)])
    t = a.pivot('Turret', (-.75, -.7, 1.1))
    tb = a.part('Turret_body', 'Team', t)
    _house(tb, [(-.4, -.4), (.4, -.4), (.45, .35), (-.45, .35)], .38, 0, ch=.04, taper=(.9, .9))
    _gun(a, t, -.4, .22, .9, .04, brake='collar', seg=8)
    _sight(a, t, .2, -.1, .38, r=.09)
    # the line-charge launcher: a rack on the rear deck with the rocket and its cable box
    k.block(armor, (2.3, 3.2, .22), loc=(0, 1.5, 1.2), chamfer=.04)
    k.block(a.part('Charge_box', 'Armor'), (1.9, 1.4, .8), loc=(0, 2.3, 1.55), chamfer=.05, taper=(.96, .96))
    a.part('Charge_box_hazard', 'Hazard').box((1.92, .12, .82), loc=(0, 2.3, 1.55), bevel=0)
    for s in (-1, 1):
        k.block(steel, (.1, .1, .7), loc=(s * .5, .55, 1.55), chamfer=0)
        k.sweep(a.part('Rack_rails', 'Steel'), [(-.04, -.04), (.04, -.04), (.04, .04), (-.04, .04)],
                [(s * .5, -.1, 1.4), (s * .5, 1.3, 1.7)])
    k.lathe(a.part('Rocket', 'Fuel'), [(.0, -.05), (.18, .05), (.2, .3), (.2, 2.3), (.12, 2.6), (.0, 2.7)],
            loc=(0, .1, 1.4), rot=(R90 + .3, 0, 0), seg=12, worn=(2,))
    a.part('Rocket_band', 'Hazard').cyl(.205, .2, loc=(0, -.12, 1.5), rot=(R90 + .3, 0, 0), seg=12, bevel=0)
    steel.cyl(.12, .3, loc=(0, 1.9, 1.3), rot=ACROSS, seg=8, bevel=0)
    parts.antenna(a.part('Antennas', 'Steel'), (1.0, 2.8, 1.2), h=.2, r=.04)
    _points(a, (.6, 3.1, .9), (0, 1.0, 1.2))
    k.clean(a)


# ============================================================================= combat wreck car
def combat_wreck_car(a):
    """A light armoured pickup car (4.78 x 2.08 x 1.49 m): a sloped bonnet, armoured cab, an open bed with a roof gun
    (`Turret`, `Main_cannon`, `Muzzle_main`, `Muzzle_coax`) behind a shield, four tyres. `Wreck_turret` is the
    standing gun pit the wreck becomes (a sandbag ring round the gun post in the bed): the node only, no behaviour."""
    _suffixed(a)
    body, armor, steel = a.part('Body', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-1.45, 1.4):
        for s in (-1, 1):
            _tyre(a, s * .8, y, .4, .34, s)
    for s in (-1, 1):
        dark.box((.18, 4.2, .24), loc=(s * .45, 0, .52), bevel=.03, seg=1)
        k.block(armor, (.34, .7, .3), loc=(s * .86, -1.45, .88), chamfer=.04)             # wheel arches
        k.block(armor, (.34, .7, .3), loc=(s * .86, 1.4, .88), chamfer=.04)
    k.extrude(body, [(-2.3, .4), (-2.3, .8), (-1.5, 1.0), (-.8, 1.1), (-.7, 1.38), (.2, 1.4), (.35, 1.1), (.35, .6),
                     (2.3, .6), (2.3, .4)], 1.96, axis='X', chamfer=.05, corner=.05)
    k.extrude(armor, [(-2.3, .35), (-2.3, .5), (2.3, .5), (2.3, .35)], 1.6, axis='X', chamfer=0)
    glass = a.part('Windows', 'Glass')
    glass.box((1.5, .04, .34), loc=(0, -.76, 1.22), rot=(.5, 0, 0), bevel=.01, seg=1)
    for s in (-1, 1):
        glass.box((.04, .8, .3), loc=(s * .985, -.2, 1.22), bevel=.01, seg=1)
        mv._headlight(a, s * .68, -2.31, .82, guard=False)
        mv._taillight(a, s * .68, 2.31, .86)
        armor.box((.05, .16, .22), loc=(s * 1.03, -.7, 1.15), bevel=.01, seg=1)               # mirrors
        k.block(armor, (.1, 1.9, .32), loc=(s * .99, 1.35, .98), chamfer=.015)                  # bed side plates
    k.block(armor, (1.9, .12, .46), loc=(0, 2.32, .98), chamfer=.015)                            # tailgate
    a.part('Bumper', 'Steel').box((1.9, .18, .18), loc=(0, -2.34, .56), bevel=.03)
    a.part('Grille', 'Undercarriage').grille(1.1, .26, loc=(0, -2.32, .86), slats=4, depth=.05, thickness=.04)
    k.block(a.part('Spare', 'Rubber'), (.2, .6, .6), loc=(0, .95, .72), chamfer=0)
    # The gun post: a ring on the bed, shield, MG; the sandbag ring is Wreck_turret
    t = a.pivot('Turret', (0, 1.2, .88))
    steel.cyl(.35, .08, loc=(0, 1.2, .88), seg=14, bevel=.01, bseg=1)
    k.lathe(a.part('Gun_post', 'Armor', t), [(.14, 0), (.14, .22), (.2, .26)], seg=10, worn=(1,))
    k.extrude(a.part('Gun_shield', 'Armor', t), [(-.34, -.1), (.34, -.1), (.28, .3), (-.28, .3)], .06,
              loc=(0, -.34, .32), rot=(-.1 + R90, 0, 0), axis='Z', chamfer=.01)
    parts.barrel(a, 'Main_cannon', t, 0, -.2, .3, 1.0, .035, seg=8, sleeve=1.3, extractor=(.5, 1.4, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -1.34, .3), t)
    mv._coax(a, t, .12, -.2, .26, length=.35, housing=.16)
    k.block(a.part('Ammo_box', 'Crate', t), (.2, .3, .2), loc=(.28, .2, .18), chamfer=.02)
    w = a.pivot('Wreck_turret', (0, 1.2, .55))
    sb = a.part('Wreck_sandbags', 'Sandbag', w)
    for i in range(8):
        u = TAU * (i + .5) / 8
        for lvl, off in ((0, 0), (1, TAU / 16)):
            uu = u + off
            k.block(sb, (.36, .22, .16), loc=(math.cos(uu) * .64, math.sin(uu) * .64, .16 + lvl * .16),
                    rot=(0, 0, uu + R90), chamfer=0)
    _points(a, (-.5, 2.3, .7), (0, 0, 1.1))
    k.clean(a)


# ============================================================================= drone hijack vehicle
def drone_hijack_vehicle(a):
    """An EW truck for hijacking drones (9.01 x 2.76 x 3.83 m): an 8x8 chassis, forward cab, a long equipment shelter
    with roof vents, and the directional hijack array on a turning mast (`Turret` > `Muzzle_main`: a flat phased
    panel, four yagi elements and a feed horn) with a small spinning sensor dish (`Radar`) on the cab roof."""
    _suffixed(a)
    cab, shelter, armor = a.part('Cab', 'Team'), a.part('Shelter', 'Team'), a.part('Armor', 'Armor')
    steel, dark = a.part('Steel', 'Steel'), a.part('Chassis', 'Undercarriage')
    fen = a.part('Fenders', 'Team')
    for y in (-3.4, -2.1, 2.0, 3.3):
        for s in (-1, 1):
            _tyre(a, s * .98, y, .55, .42, s)
    for s in (-1, 1):
        dark.box((.22, 8.4, .32), loc=(s * .55, 0, .8), bevel=.03, seg=1)
        fen.box((.5, 2.4, .06), loc=(s * 1.0, -2.75, 1.16), bevel=.02, seg=1)
        fen.box((.5, 2.4, .06), loc=(s * 1.0, 2.65, 1.16), bevel=.02, seg=1)
        mv._headlight(a, s * .8, -4.5, 1.2, guard=False)
        mv._taillight(a, s * .7, 4.5, 1.1)
    k.extrude(cab, [(-4.5, .95), (-4.5, 1.8), (-4.2, 2.5), (-2.8, 2.55), (-2.7, .95)], 2.3, axis='X', chamfer=.06,
              corner=.05)
    k.extrude(fen, [(-4.5, .6), (-4.5, .95), (-2.7, .95), (-2.7, .6)], 1.9, axis='X', chamfer=.03)
    glass = a.part('Windows', 'Glass')
    for s in (-1, 1):
        glass.box((.9, .04, .55), loc=(s * .55, -4.46, 2.05), rot=(.3, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .9, .55), loc=(s * 1.155, -3.7, 2.0), bevel=.01, seg=1)
    steel.box((2.0, .14, .2), loc=(0, -4.52, .72), bevel=.03)
    k.extrude(shelter, [(-2.4, 1.0), (-2.4, 2.65), (3.0, 2.65), (3.0, 1.0)], 2.5, axis='X', chamfer=.08)
    k.inset(shelter, lambda c, n, f: abs(n.x) > .9, width=.12, depth=.015)
    k.extrude(fen, [(-2.4, .85), (-2.4, 1.0), (4.5, 1.0), (4.5, .85)], 2.0, axis='X', chamfer=0)
    for s in (-1, 1):
        k.block(a.part('Door_panels', 'MetalSheet'), (.18, 1.2, .9), loc=(s * 1.3, -.7, 1.95), chamfer=.02)           # door panels
        for y in (-.1, .9, 1.9):
            a.part('Vents', 'Undercarriage').box((.06, .5, .3), loc=(s * 1.27, y, 1.8), bevel=0)
    k.greebles(a.part('Roof_boxes', 'MetalSheet'), (0, -1.0, 2.65), (1, 0, 0), (0, 1, 0), (2.0, 2.4), 5, seed=2751, height=(.08, .2), chamfer=.015)
    parts.hatch(a, .5, -3.4, 2.55, .22)
    ra = a.pivot('Radar', (-.55, -3.2, 2.55))
    k.lathe(a.part('Radar_mast', 'Steel', ra), [(.08, 0), (.08, .35)], seg=8)
    k.lathe(a.part('Radar_dish', 'Medical', ra), [(.0, .42), (.3, .52), (.32, .56), (.0, .46)], seg=14,
            caps=(False, False))
    a.part('Radar_feed', 'Armor', ra).cyl(.04, .14, loc=(0, 0, .6), seg=6, bevel=0)
    t = a.pivot('Turret', (0, 1.6, 2.65))
    steel_t = a.part('Turret_steel', 'Steel', t)
    steel_t.cyl(.5, .12, loc=(0, 0, .06), seg=14, bevel=.02, bseg=1)
    k.block(a.part('Turret_armor', 'Armor', t), (.8, .8, .3), loc=(0, 0, .26), chamfer=.04)
    k.lathe(a.part('Turret_mast', 'Armor', t), [(.2, .3), (.2, .55), (.1, .6)], seg=10)
    k.block(a.part('Array_panel', 'Team', t), (2.0, .16, .9), loc=(0, -.2, .7), rot=(-.18, 0, 0), chamfer=.05)
    ar = a.part('Array_cells', 'Undercarriage', t)
    for i in range(3):
        for j in range(4):
            ar.box((.5, .03, .17), loc=(-.65 + i * .65, -.31, .42 + j * .2), rot=(-.18, 0, 0), bevel=0)
    for s in (-1, 1):
        for z in (.5, 1.0):
            steel_t.cyl(.03, 1.0, loc=(s * .85, -.6, z), rot=FORWARD, seg=6, bevel=0)      # yagi elements
    steel_t.cyl(.08, .5, loc=(0, -.7, .7), rot=FORWARD, seg=8, bevel=0)                    # feed horn
    a.pivot('Muzzle_main', (0, -1.0, .7), t)
    _points(a, (.9, 4.5, 1.0), (0, 0.5, 1.9))
    k.clean(a)



# ============================================================================= MANPADS tower
def manpads_tower(a):
    """A sandbagged pit (3.2 x 3.2 x 2.4 m) with two shoulder-launched MANPADS tubes on a low tripod: a round Team
    firing pad, four courses of sandbags with a rear entrance, the tripod head on `Turret` carrying both tubes
    (`Muzzle_main`, `Muzzle_missile`, `Muzzle_missile.001` at their mouths), ammunition crates, a short radio mast."""
    _suffixed(a)
    sand, team = a.part('Sandbags', 'Sandbag'), a.part('Pad', 'Team')
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    k.lathe(a.part('Pit_floor', 'Concrete'), [(0, 0), (1.62, 0), (1.62, .1), (0, .1)], seg=20)
    k.lathe(team, [(0, .1), (1.0, .1), (1.0, .18), (.9, .22), (0, .22)], seg=16, worn=(2,))
    for i in range(14):
        a.part('Duckboards', 'Wood').box((.16, 1.7, .03), loc=(-1.1 + i * .17, 0, .235), bevel=0)
    import random
    rng = random.Random(2761)
    for course in range(4):
        n = 15
        for i in range(n):
            u = TAU * (i + .5 * (course % 2)) / n
            if abs(((u - R90 + math.pi) % TAU) - math.pi) < .42 and course < 3:
                continue                                                # the rear entrance (+Y)
            r = 1.38 + rng.uniform(-.025, .025)
            k.block(sand, (.58 + rng.uniform(-.04, .04), .36, .2), loc=(math.cos(u) * r, math.sin(u) * r, .14 + course * .2),
                    rot=(0, 0, u + R90), chamfer=0)
    # tripod: three legs from the head down to the pad
    t = a.pivot('Turret', (0, -.1, 1.0))
    for j in range(3):
        u = R90 + j * TAU / 3
        steel.limb((math.cos(u) * .55, -.1 + math.sin(u) * .55, .24), (0, -.1, .98), .06, .06, bevel=0)
    k.lathe(a.part('Head_ring', 'Steel', t), [(.26, -.05), (.26, .03), (.2, .06)], seg=12, worn=(1,))
    k.block(a.part('Head', 'Team', t), (.62, .5, .24), loc=(0, 0, .17), chamfer=.04)
    pit = (R90 - .52, 0, 0)
    for s, name in ((-1, 'Muzzle_missile'), (1, 'Muzzle_missile.001')):
        x = s * .2
        tube = a.part('Tubes', 'Team', t)
        k.lathe(tube, [(.05, -.7), (.11, -.62), (.085, -.45), (.085, .5), (.1, .62), (.1, .72), (.05, .76)],
                loc=(x, 0, .44), rot=pit, seg=10, worn=(2, 5))
        k.lathe(a.part('Seekers', 'Glass', t), [(.0, .72), (.08, .74), (.1, .76)], loc=(x, 0, .44), rot=pit, seg=8,
                caps=(False, False))
        k.block(a.part('Grips', 'Armor', t), (.08, .2, .22), loc=(x, -.14, .3), chamfer=0, rot=(-.5, 0, 0))
        pv(a, name, (x, -math.cos(.52) * .78, .44 + math.sin(.52) * .78), t)
    a.pivot('Muzzle_main', (0, -math.cos(.52) * .78, .44 + math.sin(.52) * .78), t)
    k.block(armor, (.5, .5, .4), loc=(-.8, .45, .3), chamfer=.03)
    k.block(a.part('Crates', 'Crate'), (.5, .6, .36), loc=(.75, .6, .28), chamfer=.03)
    k.block(a.part('Crates', 'Crate'), (.46, .5, .3), loc=(.75, .0, .25), chamfer=.03)
    parts.antenna(a.part('Antennas', 'Steel'), (-1.0, .9, .6), h=1.75, r=.04, seg=6)
    a.part('Flag', 'Team').box((.5, .02, .3), loc=(-.75, .9, 2.2), bevel=0)
    k.clean(a)


# ============================================================================= river patrol boat
def _boat_ring(y, w, zk, zc, zg, wc=None):
    wc = w * .85 if wc is None else wc
    return [(0, y, zk), (wc, y, zc), (w, y, zg), (-w, y, zg), (-wc, y, zc)]


def river_patrol_boat(a):
    """A riverine command boat (4.78 x 2.08 x 1.49 m): a shallow V hull with chines, a deck with a wheelhouse and
    seats, two outboards on the transom, a pintle MG on the bow (`Turret`, `Main_cannon`, `Muzzle_main`) and a
    grenade launcher on a mount aft (`Mount_mg` > `Muzzle_mg`)."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    rings = [[(0, -2.1, .72)], _boat_ring(-1.9, .38, .3, .5, .74), _boat_ring(-1.2, .86, .12, .38, .78),
             _boat_ring(-.2, 1.0, .08, .34, .76), _boat_ring(1.2, 1.02, .08, .34, .76), _boat_ring(1.95, .96, .1, .34, .74)]
    k.sharp_loft(hull, rings, chamfer=.04)
    k.block(hull, (2.0, .1, .5), loc=(0, 1.97, .5), chamfer=.015)                         # transom
    for s in (-1, 1):
        k.block(hull, (.1, 3.6, .12), loc=(s * .97, -.1, .8), chamfer=0)                   # rub rails
        k.block(a.part('Fenders', 'Rubber'), (.12, .4, .2), loc=(s * .99, 0, .66), chamfer=0)
        # outboards
        k.block(hull, (.34, .56, .8), loc=(s * .48, 2.0, .5), chamfer=.05)
        steel.cyl(.1, .6, loc=(s * .48, 2.1, .0 + .22), rot=(0, 0, 0), seg=8, bevel=0)
        k.block(dark, (.22, .3, .22), loc=(s * .48, 2.2, .08), chamfer=0)
    # wheelhouse
    k.extrude(a.part('Wheelhouse', 'Team'), [(-1.0, .76), (-.6, 1.3), (.9, 1.3), (1.0, .76)], 1.5, axis='X',
              chamfer=.05, corner=.04)
    glass = a.part('Windows', 'Glass')
    glass.box((1.3, .04, .34), loc=(0, -.9, 1.05), rot=(.5, 0, 0), bevel=.01, seg=1)
    for s in (-1, 1):
        glass.box((.04, .9, .3), loc=(s * .76, .1, 1.05), bevel=.01, seg=1)
        k.block(a.part('Seats', 'Undercarriage'), (.45, .5, .3), loc=(s * .42, 1.3, .9), chamfer=.03)
    parts.antenna(a.part('Antennas', 'Steel'), (.4, .6, 1.3), h=.08, r=.035, seg=6)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(-.4, .6, 1.34), seg=6, rings=4)
    # pintle MG on the bow
    t = a.pivot('Turret', (0, -1.1, .76))
    steel.cyl(.2, .06, loc=(0, -1.1, .78), seg=10, bevel=.01, bseg=1)
    k.lathe(a.part('Pintle', 'Armor', t), [(.08, 0), (.08, .3), (.14, .34)], seg=8, worn=(1,))
    k.extrude(a.part('MG_shield', 'Armor', t), [(-.3, -.1), (.3, -.1), (.24, .28), (-.24, .28)], .05, loc=(0, -.25, .36),
              rot=(-.1 + R90, 0, 0), axis='Z', chamfer=.01)
    k.block(a.part('MG_body', 'Steel', t), (.16, .4, .18), loc=(0, .0, .36), chamfer=.015)
    parts.barrel(a, 'Main_cannon', t, 0, -.2, .36, .85, .03, seg=8, sleeve=1.3, extractor=(.5, 1.4, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -1.19, .36), t)
    k.block(a.part('Ammo_box', 'Crate', t), (.2, .22, .18), loc=(.22, .08, .3), chamfer=.02)
    # grenade launcher aft
    m = a.pivot('Mount_mg', (0, 1.55, .76))
    k.lathe(a.part('Agl_pedestal', 'Armor', m), [(.1, 0), (.1, .2), (.16, .24)], seg=8, worn=(1,))
    k.block(a.part('Agl_body', 'Steel', m), (.22, .42, .2), loc=(0, -.04, .36), chamfer=.02)
    k.lathe(a.part('Agl_barrel', 'Steel', m), [(.04, -.1), (.04, .5), (.05, .54)], loc=(0, -.2, .38), rot=FORWARD, seg=8)
    k.block(a.part('Agl_drum', 'Armor', m), (.2, .2, .2), loc=(.0, .12, .28), chamfer=0)
    a.pivot('Muzzle_mg', (0, -.76, .38), m)
    _points(a, (.48, 2.35, .3), (0, 0, .9))
    k.clean(a)


# ============================================================================= river gunboat
def river_gunboat(a):
    """A Buyan-class river gunboat (7.86 x 3.14 x 2.88 m with the gun): a low hull with a flared bow, a faceted
    deckhouse with a mast, a forward 100 mm turret (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`), an
    eight-cell VLS block aft, a close-in gun on the stern deck, waterjet nozzles on the transom."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    rings = [[(0, -2.8, 1.0)], _boat_ring(-2.5, .5, .55, .8, 1.02), _boat_ring(-1.5, 1.3, .1, .45, 1.0),
             _boat_ring(0.0, 1.5, .08, .4, .95), _boat_ring(2.0, 1.52, .08, .4, .92), _boat_ring(3.4, 1.42, .1, .4, .9)]
    k.sharp_loft(hull, rings, chamfer=.06)
    k.block(hull, (2.8, .12, .7), loc=(0, 3.45, .62), chamfer=.02)
    for s in (-1, 1):
        k.block(hull, (.12, 5.0, .14), loc=(s * 1.5, .3, .98), chamfer=0)
        for y in (-1.0, .4, 1.8, 3.0):
            k.block(steel, (.1, .1, .28), loc=(s * 1.45, y, 1.1), chamfer=0)                # stanchions
        for y in (3.0,):
            k.block(armor, (.4, .5, .5), loc=(s * .8, y + .5, .6), chamfer=.03)
            k.lathe(dark, [(.17, 0), (.17, .3)], loc=(s * .8, 3.76, .5), rot=BACKWARD, seg=10)
    # deckhouse: faceted block amidships with a mast
    k.extrude(a.part('Deckhouse', 'Team'), [(-1.0, .96), (-.6, 1.9), (.8, 1.9), (1.4, .96)], 2.0, axis='X', chamfer=.08,
              corner=.05, taper=1)
    k.inset(a.part('Deckhouse', 'Team'), lambda c, n, f: abs(n.x) > .9, width=.12, depth=.015)
    glass = a.part('Windows', 'Glass')
    glass.box((1.6, .04, .3), loc=(0, -.85, 1.65), rot=(.6, 0, 0), bevel=.01, seg=1)
    for s in (-1, 1):
        glass.box((.04, .8, .26), loc=(s * 1.01, -.1, 1.6), bevel=.01, seg=1)
        k.block(hull, (.5, 1.2, .5), loc=(s * 1.2, .4, 1.2), chamfer=.04)                  # boat davit boxes
    k.block(armor, (.5, .6, .4), loc=(0, .3, 2.1), chamfer=.04)
    k.lathe(steel, [(.1, 0), (.08, .6), (.05, .75)], loc=(0, .5, 1.9), seg=8, worn=(1,))
    k.block(a.part('Radar_array', 'Medical'), (.8, .08, .45), loc=(0, .5, 2.65), chamfer=.03)
    k.block(a.part('Radar_back', 'Undercarriage'), (.62, .08, .36), loc=(0, .56, 2.65), chamfer=0)
    parts.antenna(a.part('Antennas', 'Steel'), (.4, .9, 1.9), h=.5, r=.04, seg=6)
    # forward 100 mm turret
    t = a.pivot('Turret', (0, -1.3, .98))
    tb = a.part('Turret_body', 'Team', t)
    _house(tb, [(-.6, -.7), (.6, -.7), (.8, .1), (.7, .75), (-.7, .75), (-.8, .1)], .62, 0, ch=.06, taper=(.7, .8))
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .3, .32), loc=(0, -.78, .3), chamfer=.03)
    _gun(a, t, -.85, .3, 1.4, .07, brake='baffle', seg=12)
    _sight(a, t, .35, .1, .6, r=.1)
    # eight VLS cells on the aft deck and a close-in gun on the stern
    k.block(hull, (1.7, 1.7, .12), loc=(0, 2.0, 1.0), chamfer=.015)
    for i in range(2):
        for j in range(4):
            k.lathe(a.part('Vls_lids', 'MetalSheet'), [(.17, .06), (.17, .12), (0, .14)],
                    loc=(-.42 + i * .84, 1.55 + j * .42, 1.0), seg=10)
    ci = a.pivot('Mount_mg', (0, 3.1, .9))
    k.lathe(a.part('Ciws_tub', 'Armor', ci), [(.28, 0), (.28, .1), (.22, .2)], seg=10, worn=(1,))
    k.block(a.part('Ciws_drum', 'Team', ci), (.5, .5, .3), loc=(0, 0, .34), chamfer=.04)
    k.lathe(a.part('Ciws_barrels', 'Steel', ci), [(.05, -.1), (.05, .8), (.07, .84)], loc=(0, -.1, .4), rot=FORWARD, seg=8)
    a.pivot('Muzzle_mg', (0, -.9, .4), ci)
    _points(a, (.8, 3.76, .5), (0, 0.5, 1.1))
    k.clean(a)


# ============================================================================= coastal anti-ship missile vehicle
def coastal_ashm_vehicle(a):
    """An NSM Coastal Defence truck (7.18 x 2.7 x 2.97 m): a 6x6 chassis with a forward cab, a flatbed with the
    launcher turntable (`Turret`) carrying four angled missile canisters in a 2 x 2 frame (`Muzzle_main` at the
    front of the group), stabiliser jacks."""
    _suffixed(a)
    cab, armor, steel = a.part('Cab', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    fen = a.part('Fenders', 'Team')
    for y in (-2.45, .45, 2.4):
        for s in (-1, 1):
            _tyre(a, s * 1.0, y, .55, .44, s)
    for s in (-1, 1):
        dark.box((.22, 6.6, .32), loc=(s * .6, 0, .8), bevel=.03, seg=1)
        fen.box((.5, 1.6, .06), loc=(s * 1.02, -2.45, 1.16), bevel=.02, seg=1)
        fen.box((.5, 3.4, .06), loc=(s * 1.02, 1.4, 1.16), bevel=.02, seg=1)
        mv._headlight(a, s * .8, -3.55, 1.2, guard=False)
        mv._taillight(a, s * .7, 3.58, 1.12)
        fen.box((.14, 1.2, .5), loc=(s * 1.0, -.7, .95), bevel=.03)                       # lockers
        steel.cyl(.07, .5, loc=(s * 1.15, 3.2, .62), seg=8, bevel=0)                        # jacks
        steel.cyl(.2, .06, loc=(s * 1.15, 3.2, .34), seg=10, bevel=.01, bseg=1)
    k.extrude(cab, [(-3.58, .95), (-3.58, 1.75), (-3.34, 2.5), (-2.2, 2.52), (-2.1, .95)], 2.34, axis='X', chamfer=.06,
              corner=.05)
    k.extrude(fen, [(-3.58, .55), (-3.58, .95), (-2.1, .95), (-2.1, .55)], 2.0, axis='X', chamfer=.03)
    glass = a.part('Windows', 'Glass')
    for s in (-1, 1):
        glass.box((.9, .04, .52), loc=(s * .5, -3.52, 2.0), rot=(.3, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .8, .5), loc=(s * 1.17, -2.7, 1.95), bevel=.01, seg=1)
    steel.box((2.0, .14, .2), loc=(0, -3.6, .7), bevel=.03)
    parts.hatch(a, .5, -2.6, 2.52, .22)
    parts.antenna(a.part('Antennas', 'Steel'), (-.8, -2.4, 2.52), h=.12, r=.04)
    k.block(a.part('Flatbed', 'Team'), (2.3, 5.0, .4), loc=(0, 1.0, 1.02), chamfer=.04)                          # flatbed
    t = a.pivot('Turret', (0, 1.3, 1.22))
    tst, tar = a.part('Turret_steel', 'Steel', t), a.part('Turret_armor', 'Team', t)
    tst.cyl(.8, .12, loc=(0, 0, .04), seg=18, bevel=.02, bseg=1)
    k.block(tar, (1.2, 1.2, .3), loc=(0, .1, .24), chamfer=.04, taper=(.9, .9))
    pitch = .2
    pr = (R90 - pitch, 0, 0)
    hinge = (0, 1.3, .45)
    for s in (-1, 1):
        k.block(tar, (.14, .6, .6), loc=(s * .55, .9, .35), chamfer=.02)                    # hinge cheeks
    tst.cyl(.1, 1.3, loc=hinge, rot=ACROSS, seg=8, bevel=0)
    for ix in (-1, 1):
        for iz in (0, 1):
            cx, cz = ix * .27, .45 + iz * .46
            k.lathe(a.part('Canisters', 'Fuel', t),
                    [(.0, -.05), (.22, -.05), (.22, 3.1), (.19, 3.14), (.19, 3.2), (0, 3.2)], loc=(cx, .75, cz),
                    rot=pr, seg=10, worn=(2,))
            k.lathe(a.part('Canister_bands', 'Hazard', t), [(.225, 2.7), (.225, 2.85)], loc=(cx, .75, cz), rot=pr, seg=10,
                    caps=(False, False))
    for y in (.9, -.2):
        k.block(a.part('Canister_frame', 'Team', t), (1.3, .12, 1.15), loc=(0, y, .7), chamfer=.02, rot=(-pitch, 0, 0))
    a.pivot('Muzzle_main', (0, .75 - math.cos(pitch) * 3.2, .68 + math.sin(pitch) * 3.2), t)
    _points(a, (.9, 3.58, 1.0), (0, 1.0, 1.4))
    k.clean(a)



# ============================================================================= auto-loader howitzer
def auto_loader_howitzer(a):
    """XM2001 Crusader: a tracked self-propelled howitzer (7.86 x 3.14 x 2.88 m with the barrel): a low wide hull on
    six road wheels with side skirts, a faceted turret with a big autoloader bustle behind it, the cradle
    (`Main_cannon_cradle`) and a 155 mm barrel with a baffle brake (`Main_cannon`, `Muzzle_brake`, `Muzzle_main`),
    a roof MG (`Mount_mg`)."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _tracks(a, 1.22, 5.4, .95, .3, 6, .5)
    k.extrude(a.part('Hull_tub', 'Team'), [(-1.8, .4), (-2.0, .75), (3.7, .8), (3.8, .4)], 2.1, axis='X', chamfer=.04, corner=.03)
    _hull(hull, [(-2.1, .75), (-1.6, 1.12), (-1.2, 1.2), (3.6, 1.2), (3.95, 1.05), (3.95, .72)], 2.85, ch=.06)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -1.2, width=.08, depth=.012)
    for s in (-1, 1):
        mv._skirt(a, s, 1.53, -1.8, 3.5, .5, 1.15, 5, thick=.07, bolts=False)
        mv._exhaust(a, s * .6, 3.94, .85, .5, .22)
    _lights(a, 1.2, -2.08, 3.95, .95, .9)
    parts.hatch(a, -.7, -1.4, 1.2, .24)
    mv._periscopes(a, [(-.7 + dx, -1.75, 1.2, 0) for dx in (-.17, 0, .17)])
    t = a.pivot('Turret', (0, 1.0, 1.2))
    tb = a.part('Turret_body', 'Team', t)
    _house(tb, [(-.85, -1.2), (.85, -1.2), (1.15, -.3), (1.25, .9), (1.05, 1.7), (-1.05, 1.7), (-1.25, .9), (-1.15, -.3)],
           1.06, 0, ch=.07, taper=(.9, .9))
    k.inset(tb, lambda c, n, f: n.z > .9, width=.09, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.9, .4, .6), loc=(0, -1.3, .55), chamfer=.04, taper=(.9, .9))               # mantlet
    k.block(a.part('Autoloader_bustle', 'Team', t), (2.2, 1.3, 1.1), loc=(0, 2.1, .55), chamfer=.07, taper=(.94, .94))
    a.part('Bustle_hatch', 'Armor', t).box((1.4, .06, .8), loc=(0, 2.77, .58), bevel=0)
    for s in (-1, 1):
        k.block(tarm, (.2, 1.6, .5), loc=(s * 1.3, .4, .5), chamfer=.03)                     # side bins
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.2, -.7, .7, s, count=4, gap=.09, r=.05, depth=.15)
    k.block(a.part('Main_cannon_cradle', 'Armor', t), (.6, 1.0, .5), loc=(0, -.85, .55), chamfer=.04)
    parts.barrel(a, 'Main_cannon', t, 0, -1.5, .55, 3.2, .1, seg=14, sleeve=1.25, extractor=(.4, 1.55, .5),
                 brake_name='Muzzle_brake', brake='baffle')
    a.pivot('Muzzle_main', (0, -1.5 - 3.2 - .3, .55), t)
    _sight(a, t, -.6, -.5, 1.06, r=.12)
    parts.hatch(a, .55, .2, 1.06, .25, parent=t)
    parts.mg_mount(a, t, (.55, .2, 1.16), length=.7, shield=False)
    parts.antenna(a.part('Antennas', 'Steel', t), (-.9, 1.6, 1.1), h=.5, r=.04)
    k.greebles(tarm, (0, .3, 1.0), (1, 0, 0), (0, 1, 0), (1.4, 1.2), 4, seed=2771, height=(.05, .1), chamfer=.012)
    _points(a, (.6, 3.95, .95), (0, 1.1, 1.3))
    k.clean(a)


# ============================================================================= amphibious light vehicle
def amphib_light_vehicle(a):
    """EFV / AAV-7: a boat-hulled tracked APC (5.48 x 3.02 x 2.5 m): a slab-sided hull with a sloped planing bow and
    a folded bow trim vane, narrow tracks under the hull, a rear ramp, two troop hatches and a small one-man
    turret on the right front (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Muzzle_coax`)."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _tracks(a, 1.2, 4.7, .8, .28, 5, .5)
    _hull(hull, [(-2.74, .98), (-2.2, .55), (2.45, .55), (2.74, .8), (2.74, 1.78), (-1.5, 1.85), (-2.3, 1.52)], 2.8,
          ch=.07, cn=.05)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9, width=.12, depth=.015)
    k.inset(hull, lambda c, n, f: n.z > .8 and c.y > 0, width=.1, depth=.012)
    # bow trim vane folded over the glacis, a bow wave guard and the rear ramp seams
    k.block(hull, (2.4, .8, .1), loc=(0, -2.35, 1.38), rot=(-.62, 0, 0), chamfer=.02)
    a.part('Vane_hinge', 'Steel').cyl(.07, 2.4, loc=(0, -2.62, 1.0), rot=ACROSS, seg=8, bevel=0)
    k.block(hull, (2.5, .12, .4), loc=(0, 2.78, 1.1), chamfer=.02)                       # ramp frame
    a.part('Ramp_seam', 'Undercarriage').box((2.0, .04, 1.1), loc=(0, 2.76, 1.2), bevel=0)
    for s in (-1, 1):
        k.block(hull, (.22, 4.8, .2), loc=(s * 1.38, .1, 1.82), chamfer=.03)             # roof rails
        mv._exhaust(a, s * .8, 2.76, 1.55, .5, .22)
        k.block(armor, (.1, 2.2, .12), loc=(s * 1.4, 0, .62), chamfer=0)                   # sponson lip
    _lights(a, 1.1, -2.7, 2.76, 1.2, 1.4)
    parts.hatch(a, -.5, 1.2, 1.85, .3)
    parts.hatch(a, .5, 1.9, 1.85, .3)
    mv._periscopes(a, [(-.9 + dx, -1.5, 1.85, 0) for dx in (-.17, 0, .17)])
    k.greebles(armor, (-.4, 0.2, 1.85), (1, 0, 0), (0, 1, 0), (1.6, 1.8), 4, seed=2772, height=(.05, .1), chamfer=.012)
    t = a.pivot('Turret', (.7, -.6, 1.85))
    tb = a.part('Turret_body', 'Team', t)
    _house(tb, [(-.45, -.5), (.45, -.5), (.55, .15), (.5, .55), (-.5, .55), (-.55, .15)], .45, 0, ch=.04, taper=(.9, .9))
    k.block(a.part('Turret_armor', 'Armor', t), (.4, .24, .28), loc=(0, -.55, .24), chamfer=.03)
    _gun(a, t, -.62, .24, .95, .04, brake='collar', seg=10)
    mv._coax(a, t, .2, -.5, .22, length=.3, housing=.16)
    _sight(a, t, -.2, .1, .45, r=.09)
    _points(a, (.8, 2.76, 1.6), (0, 0, 1.9))
    k.clean(a)


# ============================================================================= airborne light tank
def _booker(a, lite=False):
    """The M8 AGS / M10 Booker body (6.39 x 2.61 x 1.89 m with the gun): a low light-tank hull on six road
    wheels, a low flat turret with a large mantlet, a bustle, a 105 mm barrel with a brake (`Turret`, `Main_cannon`,
    `Muzzle_brake`, `Muzzle_main`, `Muzzle_coax`)."""
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    if lite:       # the chute proxy: a jet-class unit, so the tank under it is drawn leaner
        parts.track_unit(a, 1.0, 4.9, .78, .27, 5, .46, wheel_seg=6, teeth=6, return_rollers=2)
    else:
        _tracks(a, 1.0, 4.9, .78, .27, 6, .46)
    _hull(hull, [(-2.15, .62), (-1.6, .95), (-1.2, 1.0), (2.9, 1.0), (3.15, .85), (3.15, .6)], 2.2, ch=.05)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -1.0, width=.07, depth=.012)
    for s in (-1, 1):
        if lite:
            k.block(a.part('Skirts', 'Team'), (.06, 4.5, .55), loc=(s * 1.23, .75, .72), chamfer=0)
        else:
            mv._skirt(a, s, 1.23, -1.5, 3.0, .45, 1.0, 4, thick=.06, bolts=False)
            mv._exhaust(a, s * .55, 3.14, .8, .45, .2)
    if not lite:
        _lights(a, .95, -2.13, 3.15, .8, .8)
        parts.hatch(a, -.55, -1.2, 1.0, .22)
        mv._periscopes(a, [(-.55 + dx, -1.55, 1.0, 0) for dx in (-.17, 0, .17)])
    t = a.pivot('Turret', (0, .5, 1.0))
    tb = a.part('Turret_body', 'Team', t)
    _house(tb, [(-.5, -.95), (.5, -.95), (.95, -.55), (1.05, -.1), (1.05, 1.0), (.8, 1.25), (-.8, 1.25), (-1.05, 1.0),
                (-1.05, -.1), (-.95, -.55)], .6, 0, ch=.05, taper=(.9, .9))
    k.inset(tb, lambda c, n, f: n.z > .9, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.8, .34, .5), loc=(0, -1.0, .3), chamfer=.04, taper=(.9, .9))            # mantlet
    k.block(tarm, (1.6, .5, .46), loc=(0, 1.4, .26), chamfer=.04)                              # bustle
    for s in (-1, 1):
        if not lite:
            parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.0, -.45, .42, s, count=3, gap=.08, r=.045, depth=.14)
    _gun(a, t, -1.15, .3, 2.3, .075, brake='baffle', seg=12)
    if lite:
        a.pivot('Muzzle_coax', (.3, -1.25, .34), t)
    else:
        mv._coax(a, t, .3, -1.05, .34, length=.4, housing=.2)
        parts.hatch(a, .45, .35, .6, .22, parent=t)
    _sight(a, t, -.45, -.2, .6, r=.1)
    parts.antenna(a.part('Antennas', 'Steel', t), (-.8, 1.3, .5), h=.22, r=.04)
    _points(a, (.55, 3.14, .8), (0, 1.0, 1.1))


def airborne_light_tank(a):
    _suffixed(a)
    _booker(a)
    k.clean(a)


def airborne_light_tank_chute(a):
    """The airborne tank under its parachute (9 x 9 x 11 m, the proxy unit of a paradrop): the Booker body below, a
    12-gore Team canopy 9 m across with a Medical stripe and a vent ring, twelve rigging lines to the hull."""
    _suffixed(a)
    _booker(a, lite=True)
    steel = a.part('Rigging', 'Steel')
    prof = [(4.5, 7.7), (4.38, 8.5), (3.95, 9.4), (3.2, 10.2), (2.0, 10.8), (.7, 11.0)]
    k.lathe(a.part('Canopy', 'Team'), prof + [(.0, 11.0)], seg=12, caps=(False, False), worn=(0,))
    k.lathe(a.part('Canopy_stripe', 'Medical'), [(4.4, 8.4), (4.0, 9.3), (3.28, 10.1), (3.4, 10.0), (4.14, 9.2), (4.5, 8.4)],
            seg=12, caps=(False, False))
    k.lathe(a.part('Canopy_vent', 'Hazard'), [(.72, 10.98), (.7, 11.0), (.5, 11.0)], seg=12, caps=(False, False))
    for i in range(12):
        u = TAU * i / 12
        steel.limb((math.cos(u) * 4.45, math.sin(u) * 4.45, 7.7), (math.cos(u) * .55, math.sin(u) * .35 + .5, 1.75), .1, .1,
                   bevel=0)
    k.clean(a)


# ============================================================================= stealth naval strike aircraft
SN_HALF = 10.5
SN_NOSE = -4.2
SN_SWEEP = .72                                    # leading edge: y = nose + 0.72 |x|
SN_ST = [(0.0, 4.2, .62, .38), (1.6, 4.15, .55, .34), (3.4, 4.05, .4, .26), (5.6, 3.95, .27, .18), (7.8, 3.82, .17, .12),
         (10.4, 3.62, .08, .06)]                   # x, trailing edge y, upper and lower thickness


def _sn_section(x, te, tu, tl):
    le = SN_NOSE + SN_SWEEP * abs(x)
    c = te - le
    return [(x, le, 0), (x, le + .12 * c, tu * .75), (x, le + .35 * c, tu), (x, le + .7 * c, tu * .5), (x, te, 0),
            (x, le + .7 * c, -tl * .4), (x, le + .35 * c, -tl), (x, le + .12 * c, -tl * .7)]


def _sn_z(x, y, top=True):
    """Height of the upper (or lower) skin at (x, y), to seat parts on it."""
    ax = min(abs(x), SN_ST[-1][0])
    for (x0, te0, u0, l0), (x1, te1, u1, l1) in zip(SN_ST, SN_ST[1:]):
        if x0 <= ax <= x1:
            f = (ax - x0) / (x1 - x0)
            te, tu, tl = te0 + (te1 - te0) * f, u0 + (u1 - u0) * f, l0 + (l1 - l0) * f
            break
    le = SN_NOSE + SN_SWEEP * ax
    u = max(0.0, min(1.0, (y - le) / (te - le)))
    prof = [(0, 0), (.12, .75), (.35, 1.0), (.7, .5), (1, 0)] if top else [(0, 0), (.12, .7), (.35, 1.0), (.7, .4), (1, 0)]
    for (u0, h0), (u1, h1) in zip(prof, prof[1:]):
        if u0 <= u <= u1:
            h = h0 + (h1 - h0) * (u - u0) / (u1 - u0)
            return h * tu if top else -h * tl
    return 0.0


def stealth_naval_strike(a):
    """A-12 Avenger II: a flat-iron flying wing (8.4 x 21 x 1.5 m): one loft from tip to tip, a straight 35 degree
    leading edge and an almost straight trailing edge, clipped tips with the carrier fold hinges, a flush canopy,
    dorsal intakes, flat exhaust troughs, an `Muzzle_rocket` weapon bay each side, the `Bombs` rack under the belly
    (`Muzzle_missile`). Jet rule: no insets or panel greebles on the skin."""
    _suffixed(a)
    team, arm, dark = a.part('Wing', 'Team'), a.part('Armor', 'Armor'), a.part('Undercarriage', 'Undercarriage')
    out = SN_ST[1:]
    st = [(-x, te, tu, tl) for x, te, tu, tl in reversed(out)] + [SN_ST[0]] + list(out)
    tip_y = SN_NOSE + SN_SWEEP * SN_HALF + .05
    rings = [[(-SN_HALF, tip_y, 0)]] + [_sn_section(*s) for s in st] + [[(SN_HALF, tip_y, 0)]]
    k.sharp_loft(team, rings, chamfer=.07, corners=[0, 4])
    # flush canopy: a low glass bubble ahead of the intakes
    glass = a.part('Canopy', 'Glass')
    z0 = _sn_z(0, -2.6)
    parts.canopy(glass, a.part('Canopy_frames', 'Armor'),
                 [_bubble(-3.4, .22, z0 - .02, z0 + .12), _bubble(-2.9, .42, z0 - .02, z0 + .34),
                  _bubble(-2.2, .45, z0 - .02, z0 + .36), _bubble(-1.7, .3, z0 - .02, z0 + .14)],
                 sill=.04, bows=(1, 2), bow_r=.02, sills=(1, 0), arch=(1, 2, 3, 4, 5, 0))
    for s in (-1, 1):
        # dorsal intakes with a dark mouth, flat exhaust troughs with a glow strip
        zi = _sn_z(s * 1.7, -.8)
        k.block(team, (.9, 1.5, .24), loc=(s * 1.7, -.2, zi + .08), chamfer=.04, taper=(.8, .7))
        a.part('Intakes', 'Undercarriage').box((.8, .05, .14), loc=(s * 1.7, -.98, zi + .12), rot=(-.4, 0, 0), bevel=0)
        ze = _sn_z(s * 2.2, 3.4)
        a.part('Exhaust_trough', 'Charred').box((1.3, 1.0, .05), loc=(s * 2.2, 3.5, ze + .03), bevel=0)
        a.part('Exhaust_glow', 'Alloy').box((1.1, .05, .05), loc=(s * 2.2, 4.0, ze + .05), bevel=0)
        # wingtip fold: a hinge seam across the outer panel with a hinge fairing on the leading edge
        x = s * 7.4
        le, te = SN_NOSE + SN_SWEEP * 7.4, 3.9
        zf = _sn_z(x, (le + te) / 2)
        a.part('Fold_seam', 'Charred').box((.06, te - le - .4, .03), loc=(x, (le + te) / 2, zf + .01), bevel=0)
        k.block(arm, (.3, .5, .14), loc=(x, le + .5, _sn_z(x, le + .5) + .04), chamfer=.02)
        a.part('Wing_lights', 'TeamGlow').box((.12, .2, .05), loc=(s * 10.3, 3.35, 0), bevel=0)
    # weapon bays: the standoff missiles (Muzzle_rocket) in the outer bays, aft of the intakes
    sm = a.part('Standoff_missile', 'Fuel')
    for s in (-1, 1):
        sm.box((.26, 1.7, .2), loc=(s * 3.0, 2.15, -.2), bevel=0, taper=(.8, 1))
        a.part('Bay_doors', 'Armor').box((.5, 1.9, .05), loc=(s * 3.0, 2.15, -.3), bevel=0)
    a.pivot('Muzzle_rocket', (-3.0, 1.28, -.32))
    pv(a, 'Muzzle_rocket.001', (3.0, 1.28, -.32))
    # the bomb load on `Bombs` under the belly: two rows of two precision bombs on a rack
    from mb_air import _bomb, _store_parts
    a.pivot('Bombs', (0, 0, 0))
    sp = _store_parts(a, parent='Bombs')
    for i in range(2):
        for j in range(2):
            _bomb(sp, (-.3 + j * .6, -.3 + i * 1.3, -.46), length=1.0, r=.14, seg=8, guided=True, lean=True)
    a.part('Bomb_rack', 'Undercarriage').box((1.3, 2.6, .05), loc=(0, .35, -.3), bevel=0)
    a.pivot('Muzzle_missile', (0, 0, -.5))
    # nose pitot and a dorsal antenna blister
    k.block(arm, (.5, .9, .1), loc=(0, 1.3, _sn_z(0, 1.3) + .03), chamfer=.02)
    _points(a, (2.0, 4.0, .2), (0, .5, .7))
    k.clean(a)


# ============================================================================= pass B: shared helpers
def _rws(a, x, y, z, length=.8, r=.04, s=1.0):
    """A small remote weapon station on a roof (`Turret` > `Main_cannon`, `Muzzle_brake`, `Muzzle_main`): a drum, a
    housing with a sensor window, a thin 12.7 mm barrel. Its top is .24 m above z."""
    t = a.pivot('Turret', (x, y, z))
    steel = a.part('Rws_ring', 'Steel', t)
    steel.cyl(.26, .05, loc=(0, 0, .025), seg=12, bevel=.01, bseg=1)
    k.block(a.part('Rws_body', 'Team', t), (.46, .5, .2), loc=(0, .02, .15), chamfer=.03, taper=(.9, .9))
    a.part('Rws_sensor', 'Glass', t).box((.18, .04, .09), loc=(.14, -.25, .2), bevel=0)
    parts.barrel(a, 'Main_cannon', t, 0, -.2, .15, length, r, seg=8, sleeve=1.3, extractor=(.5, 1.4, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -.2 - length - .14, .15), t)
    return t


def _truck_base(a, axles, wx, r, tw, yf, yr, yc, ztop, cw, zf=None, rail=.55, lamp_x=.8, fenders=True, fw=.5):
    """The wheeled truck every pass B truck shares: tyres on `axles`, frame rails, Team fenders over the axle groups,
    a cab from yf to yc (width cw, roof ztop) with windscreen and side glass, a bumper and lamps. Returns (cab, steel)."""
    cab, steel = a.part('Cab', 'Team'), a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    fen = a.part('Fenders', 'Team')
    zf = 2 * r - .15 if zf is None else zf
    for y in axles:
        for s in (-1, 1):
            _tyre(a, s * wx, y, r, tw, s)
    for s in (-1, 1):
        dark.box((.22, yr - yf - .3, .32), loc=(s * rail, (yf + yr) / 2, 2 * r - .3), bevel=.03, seg=1)
        if fenders:
            for y in (axles[0], axles[-1]):
                fen.box((fw, 1.5, .06), loc=(s * (wx + .02 - (.5 - fw) / 2), y, 2 * r + .06), bevel=.02, seg=1)
        mv._headlight(a, s * lamp_x, yf, zf + .22, guard=False)
        mv._taillight(a, s * lamp_x * .9, yr, zf + .12)
    k.extrude(cab, [(yf, zf), (yf, zf + .8), (yf + .3, ztop), (yc, ztop), (yc, zf)], cw, axis='X', chamfer=.06, corner=.05)
    k.extrude(fen, [(yf, zf - .4), (yf, zf), (yc, zf), (yc, zf - .4)], cw - .4, axis='X', chamfer=.03)
    glass = a.part('Windows', 'Glass')
    zg = zf + .8 + (ztop - zf - .8) * .4
    for s in (-1, 1):
        glass.box((cw * .38, .04, (ztop - zf - .8) * .6 + .2), loc=(s * cw * .23, yf + .1, zg), rot=(.3, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .9, (ztop - zf - .8) * .6), loc=(s * (cw / 2 + .005), yf + .95, zg), bevel=.01, seg=1)
    steel.box((cw - .3, .14, .2), loc=(0, yf - .02, zf - .22), bevel=.03)
    return cab, steel


def _rotor_head_as(a, r, prefix, *args, **kw):
    """parts.rotor_head with its part names starting `prefix_` instead of `Rotor_` (a second rotor on the model)."""
    orig = a.part

    def part(name, mat, parent=None):
        return orig(prefix + name[5:] if name.startswith('Rotor_') else name, mat, parent)
    a.part = part
    try:
        parts.rotor_head(a, r, *args, **kw)
    finally:
        del a.part


# ============================================================================= twin rotor gunship
def twin_rotor_gunship(a):
    """An ACH-47A 'Guns-A-Go-Go': a CH-47 tandem-rotor airframe (11.9 x 6.3 x 4.8 m): a boxy fuselage, cockpit canopy,
    a tall aft pylon between two engine nacelles, a three-blade `Rotor` forward and `Rotor_rear` aft, side gun
    sponsons (`Muzzle_mg`, `.001`) with minigun pods, a chin turret (`Muzzle_gun`, `Muzzle_main`), fixed wheels."""
    _suffixed(a)
    body, armor, steel = a.part('Fuselage', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    rings = [_octagon(-5.3, .32, 1.0, 1.75), _octagon(-4.8, .75, .9, 2.2), _octagon(-4.1, 1.05, .85, 2.7),
             _octagon(-3.2, 1.15, .82, 2.95), _octagon(3.4, 1.15, .9, 2.95), _octagon(4.6, 1.0, 1.4, 2.8),
             _octagon(5.4, .7, 1.9, 2.7)]
    k.sharp_loft(body, rings, chamfer=.04)
    k.extrude(body, [(2.0, 2.8), (2.55, 4.0), (3.3, 4.0), (4.9, 2.7)], 1.0, axis='X', chamfer=.04, corner=.05)   # aft pylon
    k.block(armor, (1.2, .12, .9), loc=(0, 5.45, 2.25), rot=(.12, 0, 0), chamfer=.02)                   # ramp
    glass = a.part('Canopy', 'Glass')
    parts.canopy(glass, a.part('Canopy_frames', 'Armor'),
                 [_bubble(-5.1, .3, 1.35, 1.8), _bubble(-4.7, .62, 1.5, 2.35), _bubble(-4.2, .9, 1.75, 2.85),
                  _bubble(-3.7, 1.0, 1.9, 3.05)], sill=.04, bows=(1, 2), bow_r=.02, sills=(1, 0),
                 arch=(1, 2, 3, 4, 5, 0))
    for s in (-1, 1):
        parts.engine_nacelle(body, dark, (s * .78, 4.5, 3.55), .3, 2.0, rot=FORWARD, seg=10)
        # side sponson: a stub wing with a minigun pod, a strut and the fixed wheels
        k.block(body, (1.5, 2.2, .14), loc=(s * 1.85, -.2, 1.7), chamfer=.02)
        k.lathe(a.part('Gun_pods', 'Team'), [(0, -.05), (.2, 0), (.22, .2), (.22, 1.1), (.12, 1.3), (0, 1.3)],
                loc=(s * 2.1, -.5, 1.5), rot=BACKWARD, seg=10, worn=(2,))
        for dx, dz in ((0, .0), (-.08, .07), (.08, .07)):
            steel.cyl(.035, .95, loc=(s * 2.1 + dx, -1.0, 1.5 + dz), rot=FORWARD, seg=6, bevel=0)
        a.part('Pod_bands', 'Hazard').cyl(.23, .06, loc=(s * 2.1, .2, 1.5), rot=FORWARD, seg=10, bevel=0)
        steel.limb((s * 1.2, -.2, 1.0), (s * 2.0, -.2, 1.62), .08, .08, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.07, .12, .07), loc=(s * 2.58, -.2, 1.7), bevel=0)
        for y, zt in ((-3.3, .9), (3.6, 1.2)):
            steel.limb((s * .95, y, zt), (s * 1.05, y, .36), .09, .09, bevel=0)
            a.part('Tyres', 'Rubber').cyl(.34, .2, loc=(s * 1.1, y, .34), rot=ACROSS, seg=10, bevel=.03)
            a.part('Hubs', 'Steel').cyl(.14, .24, loc=(s * 1.1, y, .34), rot=ACROSS, seg=8, bevel=0)
    # chin turret (the nose gun)
    armor.sphere((.35, .4, .3), loc=(0, -4.7, .78), seg=10, rings=6)
    steel.cyl(.06, .95, loc=(0, -5.3, .7), rot=FORWARD, seg=8, bevel=0)
    # forward rotor, aft rotor (a tall mast on the pylon)
    steel.cyl(.18, .6, loc=(0, -2.75, 3.2), seg=8, bevel=0)
    r1 = a.pivot('Rotor', (0, -2.75, 3.5))
    parts.rotor_head(a, r1, 3, 3.17, .34, hub=.3, phase=-R90, t=.04, cap=.2, stripe=.3, droop=.05)
    steel.cyl(.2, .5, loc=(0, 2.85, 4.15), seg=8, bevel=0)
    r2 = a.pivot('Rotor_rear', (0, 2.85, 4.4))
    _rotor_head_as(a, r2, 'Rotor_rear', 3, 3.17, .34, hub=.3, phase=R90, t=.04, cap=.25, stripe=.3, droop=.05)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 0.9, 3.0), seg=6, rings=4)
    ant = a.part('Antennas', 'Steel')
    parts.antenna(ant, (0, -2.0, 2.95), h=.3, r=.04, seg=6)
    a.pivot('Muzzle_gun', (0, -5.85, .7))
    a.pivot('Muzzle_main', (0, -5.85, .7))
    a.pivot('Muzzle_mg', (-2.1, -1.5, 1.5))
    pv(a, 'Muzzle_mg.001', (2.1, -1.5, 1.5))
    _points(a, (.78, 4.5, 3.55), (0, -3.0, 1.5))
    k.clean(a)


# ============================================================================= heavy lift helicopter
def heavy_lift_helicopter(a):
    """A Mi-26 class heavy-lift helicopter (7.6 x 6.6 x 2.1 m): one six-blade `Rotor` over a deep cabin with nose
    glazing, two engines on the roof, a thin tail boom with fin and `Tail_rotor`, sponsons with fixed wheels, rear
    clamshell doors and a cargo hook under the belly."""
    _suffixed(a)
    body, armor, steel = a.part('Fuselage', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, glass = a.part('Undercarriage', 'Undercarriage'), a.part('Canopy', 'Glass')
    rings = [_octagon(-3.3, .3, .62, 1.05), _octagon(-3.0, .6, .56, 1.38), _octagon(-2.3, .76, .52, 1.62),
             _octagon(-1.0, .82, .5, 1.66), _octagon(1.0, .82, .56, 1.62), _octagon(1.5, .6, .8, 1.48),
             _octagon(2.8, .3, .98, 1.46), _octagon(3.95, .17, 1.08, 1.5)]
    k.sharp_loft(body, rings, chamfer=.03)
    k.extrude(body, [(3.0, 1.2), (3.8, 1.92), (4.15, 1.92), (4.1, 1.2)], .08, axis='X', chamfer=.012, corner=.03)   # fin
    k.block(body, (1.1, .34, .05), loc=(0, 3.35, 1.0), chamfer=.01)                                          # tailplane
    parts.canopy(glass, a.part('Canopy_frames', 'Armor'),
                 [_bubble(-3.2, .22, .85, 1.15), _bubble(-2.95, .5, .9, 1.5), _bubble(-2.5, .66, .98, 1.72),
                  _bubble(-2.1, .7, 1.05, 1.74)], sill=.03, bows=(1, 2), bow_r=.018, sills=(1, 0),
                 arch=(1, 2, 3, 4, 5, 0))
    k.block(armor, (1.2, .1, .8), loc=(0, 1.45, .98), rot=(.5, 0, 0), chamfer=.02)                          # rear doors
    for s in (-1, 1):
        parts.engine_nacelle(body, dark, (s * .42, 1.3, 1.74), .2, 1.7, rot=FORWARD, seg=10)
        k.block(a.part('Sponsons', 'Team'), (.45, 2.4, .5), loc=(s * .98, -.1, .62), chamfer=.05)
        a.part('Tyres', 'Rubber').cyl(.3, .22, loc=(s * 1.0, -.2, .3), rot=ACROSS, seg=10, bevel=.03)
        a.part('Hubs', 'Steel').cyl(.12, .26, loc=(s * 1.0, -.2, .3), rot=ACROSS, seg=8, bevel=0)
        steel.limb((s * .98, -.2, .55), (s * 1.0, -.2, .3), .08, .08, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .1, .06), loc=(s * 1.22, -.9, .62), bevel=0)
    a.part('Tyres', 'Rubber').cyl(.22, .16, loc=(0, -2.4, .22), rot=ACROSS, seg=8, bevel=.02)
    steel.limb((0, -2.4, .5), (0, -2.4, .22), .07, .07, bevel=0)
    # cargo hook under the belly
    hook = a.part('Cargo_hook', 'Hazard')
    hook.cyl(.05, .14, loc=(0, -.3, .44), seg=6, bevel=0)
    hook.torus(.07, .022, loc=(0, -.3, .33), rot=(0, R90, 0), seg=10, ring=5)
    steel.cyl(.14, .1, loc=(0, -.3, .58), seg=8, bevel=0)
    steel.cyl(.17, .24, loc=(0, -.3, 1.7), seg=8, bevel=0)
    r = a.pivot('Rotor', (0, -.3, 1.72))
    parts.rotor_head(a, r, 6, 3.29, .24, hub=.3, phase=0, t=.03, cap=.22, stripe=.24, droop=.04)
    armor.cyl(.05, .1, loc=(-.07, 3.9, 1.3), rot=ACROSS, seg=8, bevel=0)
    tr = a.pivot('Tail_rotor', (-.13, 3.9, 1.3))
    parts.tail_rotor(a, tr, 4, .45, .09, t=.02, phase=math.pi / 4, side=-1)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 2.2, 1.46), seg=6, rings=4)
    parts.antenna(a.part('Antennas', 'Steel'), (0, 0.7, 1.64), h=.18, r=.03, seg=6)
    a.pivot('Muzzle_main', (0, -3.3, .85))
    _points(a, (.42, 1.3, 1.74), (0, -.3, 1.0))
    k.clean(a)


# ============================================================================= aerial tanker
def aerial_tanker(a):
    """A KC-135 / Il-78 class aerial tanker (19.8 x 22.6 x 5.7 m): a long round fuselage with a glazed nose, swept
    low wings with four turbofans on pylons and a wingtip hose pod each, a swept tail, a refuelling boom under the
    tail (`Muzzle_gun`)."""
    _suffixed(a)
    body, armor, steel = a.part('Fuselage', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, moving = a.part('Undercarriage', 'Undercarriage'), a.part('Control_surfaces', 'Team')
    st = [(-9.6, .35, 1.7, 2.5), (-8.6, .9, 1.25, 3.2), (-7.2, 1.2, 1.05, 3.5), (-5.0, 1.3, .95, 3.6),
          (4.2, 1.3, .95, 3.6), (6.2, 1.1, 1.2, 3.5), (8.2, .7, 1.9, 3.3), (9.7, .3, 2.5, 3.2)]
    body.loft([[(0, -9.9, 2.1)]] + [_sec(*s, n=14) for s in st] + [[(0, 9.9, 2.85)]], bevel=0)
    # canopy over the cockpit
    parts.canopy(a.part('Canopy', 'Glass'), a.part('Canopy_frames', 'Armor'),
                 [_bubble(-8.4, .5, 2.85, 3.3), _bubble(-7.9, .8, 2.9, 3.58), _bubble(-7.3, .92, 2.95, 3.68),
                  _bubble(-6.7, .88, 3.0, 3.66)], sill=.04, bows=(1, 2), bow_r=.02, sills=(1, 0),
                 arch=(1, 2, 3, 4, 5, 0))
    for s in (-1, 1):
        a.part('Cheat_line', 'Medical').box((.04, 12.0, .22), loc=(s * 1.31, -.4, 2.4), bevel=0)
    k.block(armor, (.5, 1.2, .3), loc=(0, -4.6, 3.7), chamfer=.04, taper=(.8, .9))                  # refuelling receptacle
    # wings, tailplanes, fin
    wing = Planform(.9, 11.31, -.9, 5.0, 4.2, 1.5, .62, .2, .75, 1.2)
    for fr in (RIGHT, LEFT):
        _wing(body, moving, wing, fr, cs=[(2.0, 5.6, .72), (6.0, 10.4, .76)], bevel=0, root=False)
    tail = Planform(.6, 3.2, 7.0, 8.6, 2.5, 1.2, .24, .12, 2.9, 3.2)
    for fr in (RIGHT, LEFT):
        _wing(body, moving, tail, fr, cs=[(1.0, 3.0, .68)], bevel=0)
    k.extrude(body, [(5.2, 3.2), (7.4, 5.7), (9.0, 5.7), (9.4, 3.0)], .22, axis='X', chamfer=.02, corner=.08)
    moving.box((.1, .9, 2.0), loc=(0, 9.35, 4.4), rot=(-.3, 0, 0), bevel=0)
    # four turbofans under the wing: a turned cowl with a dark intake face and a cone, on a pylon
    for s in (-1, 1):
        for sp in (3.9, 7.2):
            le = wing.le(sp) - 1.2
            x = s * sp
            k.lathe(a.part('Nacelles', 'Team'), [(.3, 0), (.44, .12), (.48, .5), (.5, 1.6), (.44, 2.7), (.3, 3.2),
                                                 (.18, 3.4), (0, 3.4)], loc=(x, le, .52), rot=BACKWARD, seg=12, worn=(2,))
            k.lathe(a.part('Intakes', 'Undercarriage'), [(.3, 0), (.2, .12), (0, .12)], loc=(x, le, .52), rot=BACKWARD,
                    seg=12, caps=(False, False))
            k.block(armor, (.14, 1.6, .42), loc=(x, le + 1.6, .96), chamfer=.015)
    # wingtip hose pods (drogues)
    for s in (-1, 1):
        k.lathe(a.part('Hose_pods', 'Team'), [(0, -.05), (.2, 0), (.26, .3), (.26, 1.9), (.14, 2.3), (0, 2.3)],
                loc=(s * 8.9, wing.le(8.9) + .5, 1.0), rot=BACKWARD, seg=10, worn=(2,))
        steel.limb((s * 8.9, wing.le(8.9) + 1.5, 1.35), (s * 8.9, wing.le(8.9) + 1.5, 1.2), .12, .12, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.08, .16, .08), loc=(s * 11.25, 5.0, 1.25), bevel=0)
    # refuelling boom under the tail
    steel.limb((0, 6.4, 1.3), (0, 9.5, .55), .16, .16, bevel=0)
    k.block(armor, (.5, 1.4, .26), loc=(0, 6.8, 1.35), chamfer=.04, taper=(.8, .9))
    k.block(moving, (1.1, .5, .05), loc=(0, 9.5, .55), chamfer=.01)
    a.part('Boom_tip', 'Hazard').cyl(.1, .5, loc=(0, 9.6, .52), rot=FORWARD, seg=8, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.08, loc=(0, 1.0, 3.65), seg=6, rings=4)
    a.pivot('Muzzle_gun', (0, 9.75, .52))
    _points(a, (3.9, wing.le(3.9) + 2.2, .52), (0, -5.0, 2.0))
    k.clean(a)


# ============================================================================= ground drone carrier
def _minion(a, x, y, z, i):
    """One of the carrier's three docked minion robots on its own `Minion_<i>` pivot (a THeMIS class tracked robot:
    hull, two tracks, a sensor head, a mast). Nodes only: no spawn mechanism reads them yet."""
    m = a.pivot(f'Minion_{i}', (x, y, z))
    k.block(a.part('Minion_hull', 'Team', m), (.34, .8, .24), loc=(0, 0, .2), chamfer=.03, taper=(.9, .9))
    for s in (-1, 1):
        k.block(a.part('Minion_tracks', 'Undercarriage', m), (.1, .86, .2), loc=(s * .22, 0, .12), chamfer=.03)
    k.block(a.part('Minion_head', 'Armor', m), (.2, .3, .1), loc=(0, -.1, .37), chamfer=.02)
    a.part('Minion_eye', 'Glass', m).box((.1, .03, .05), loc=(0, -.26, .38), bevel=0)
    parts.antenna(a.part('Minion_mast', 'Steel', m), (.1, .25, .32), h=.25, r=.03, seg=5)


def ground_drone_carrier(a):
    """A THeMIS / Uran-9 class drone carrier (4.95 x 2.0 x 2.4 m): a tracked unmanned hull with a remote turret and
    a coaxial machine gun (`Turret`, `Main_cannon`, `Muzzle_main`), a tall comms mast, and three small tracked
    minion robots docked on the rear deck (`Minion_1` .. `Minion_3`, nodes only) behind a folding ramp."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _tracks(a, .74, 4.3, .72, .22, 5, .4)
    k.extrude(a.part('Hull_tub', 'Team'), [(-2.1, .4), (-2.2, .6), (2.3, .6), (2.35, .4)], 1.6, axis='X', chamfer=.03)
    _hull(hull, [(-2.35, .6), (-1.95, .98), (-1.6, 1.0), (2.3, 1.0), (2.4, .9), (2.4, .6)], 1.7, ch=.05)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -1.5, width=.07, depth=.012)
    _lights(a, .65, -2.34, 2.4, .82, .82)
    for s in (-1, 1):
        k.block(armor, (.06, 1.8, .14), loc=(s * .8, 1.45, 1.06), chamfer=0)                 # deck rails
        mv._exhaust(a, s * .5, 2.4, .78, .4, .2)
    k.block(armor, (1.5, .36, .08), loc=(0, 2.5, 1.05), rot=(1.0, 0, 0), chamfer=.01)         # ramp
    parts.hatch(a, -.55, -1.6, 1.0, .2)
    for i, x in enumerate((-.52, 0, .52), 1):
        _minion(a, x, 1.45, 1.0, i)
    t = a.pivot('Turret', (0, -.7, 1.0))
    body = a.part('Turret_body', 'Team', t)
    _house(body, [(-.5, -.55), (.5, -.55), (.56, .45), (-.56, .45)], .4, 0, ch=.05, taper=(.9, .9))
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .3, .3), loc=(0, -.62, .22), chamfer=.03)
    _gun(a, t, -.5, .2, 1.1, .04, brake='collar', seg=8)
    a.part('Sensor_ball', 'Glass', t).sphere(.11, loc=(.28, -.2, .5), seg=8, rings=5)
    parts.antenna(a.part('Comms_mast', 'Steel', t), (-.3, .3, .4), h=.9, r=.045, seg=6)
    k.greebles(a.part('Turret_boxes', 'Armor', t), (0, .1, .4), (1, 0, 0), (0, 1, 0), (.8, .6), 2, seed=2801,
               height=(.04, .08), chamfer=.01)
    _points(a, (.5, 2.4, .8), (0, 0, 1.3))
    k.clean(a)


# ============================================================================= mobile repair vehicle
def mobile_repair_vehicle(a):
    """An MTO-UB class repair truck (6.45 x 3.02 x 2.02 m): a 6x6 chassis with a cab and a roof remote weapon station
    (`Turret`, `Muzzle_main`), a workshop box, a slewing crane on the rear deck (`Crane`), a welding rig with gas
    bottles, outrigger legs."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    shelter, crane = a.part('Workshop', 'Team'), a.part('Crane', 'Hazard')
    _truck_base(a, (-2.2, .9, 2.3), 1.22, .55, .5, -3.12, 3.14, -1.85, 1.7, 2.4, rail=.6, lamp_x=.9)
    k.extrude(shelter, [(-1.7, .95), (-1.7, 1.9), (1.5, 1.9), (1.5, .95)], 2.6, axis='X', chamfer=.07)
    k.inset(shelter, lambda c, n, f: abs(n.x) > .9, width=.12, depth=.015)
    k.block(a.part('Deck', 'Team'), (2.6, 1.8, .22), loc=(0, 2.35, 1.0), chamfer=.04)
    for s in (-1, 1):
        k.block(a.part('Lockers', 'MetalSheet'), (.1, 1.3, .8), loc=(s * 1.34, -.2, 1.3), chamfer=.02)
        a.part('Vents', 'Undercarriage').box((.06, .5, .26), loc=(s * 1.31, .75, 1.55), bevel=0)
        steel.limb((s * 1.2, -.7, 1.02), (s * 1.34, -.7, .5), .12, .12, bevel=0)            # outrigger legs
        steel.cyl(.16, .08, loc=(s * 1.34, -.7, .06), seg=8, bevel=.01, bseg=1)
    k.greebles(a.part('Roof_boxes', 'MetalSheet'), (0, -.1, 1.9), (1, 0, 0), (0, 1, 0), (2.0, 2.6), 4, seed=2811,
               height=(.04, .08), chamfer=.012)
    steel.cyl(.08, 1.1, loc=(1.3, -1.8, 1.45), seg=8, bevel=0)                                # exhaust stack
    parts.hatch(a, -.55, -2.6, 1.7, .22)
    # crane: a slewing base, an inner boom raised over the deck, the outer boom and the hook
    steel.cyl(.3, .45, loc=(.7, 2.0, 1.33), seg=10, bevel=.02, bseg=1)
    crane.limb((.7, 2.0, 1.55), (.7, 2.55, 1.9), .24, .22, bevel=.02)
    crane.limb((.7, 2.55, 1.9), (.7, 3.15, 1.78), .18, .16, bevel=.02)
    steel.limb((.7, 3.15, 1.74), (.7, 3.15, 1.42), .08, .08, bevel=0)
    steel.cyl(.1, .1, loc=(.7, 3.15, 1.36), seg=8, bevel=0)
    # welding rig: two gas bottles, the welder box, a cable drum
    for dx in (-.4, -.15):
        a.part('Gas_bottles', 'Fuel').cyl(.11, .85, loc=(-.9 + dx, 2.6, 1.54), seg=8, bevel=.02)
        a.part('Gas_caps', 'Hazard').cyl(.07, .12, loc=(-.9 + dx, 2.6, 2.0), seg=6, bevel=0)
    k.block(armor, (.7, .55, .5), loc=(-.7, 1.9, 1.36), chamfer=.03)
    a.part('Weld_lamp', 'Alloy').box((.12, .04, .08), loc=(-.7, 1.62, 1.5), bevel=0)
    a.part('Cable_drum', 'Hazard').cyl(.28, .3, loc=(-.2, 3.0, 1.35), rot=ACROSS, seg=12, bevel=.02)
    _rws(a, .55, -2.2, 1.7, length=.55)
    _points(a, (1.3, 3.2, .9), (0, 0, 1.5))
    k.clean(a)


# ============================================================================= radar support vehicle
def radar_support_vehicle(a):
    """A Giraffe AMB / Kasta class radar truck (4.6 x 2.0 x 4.0 m): a 4x4 truck with a cab and a roof remote weapon
    station (`Turret`, `Muzzle_main`), an equipment box, four stabiliser jacks and a raised telescopic mast carrying
    the flat array on a turning head (`Radar`)."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    box = a.part('Equipment', 'Team')
    _truck_base(a, (-1.5, 1.5), .8, .5, .36, -2.25, 2.25, -1.0, 1.75, 1.7, rail=.5, lamp_x=.6, fw=.4)
    k.extrude(box, [(-.85, .9), (-.85, 1.75), (2.25, 1.75), (2.25, .9)], 1.8, axis='X', chamfer=.06)
    k.inset(box, lambda c, n, f: abs(n.x) > .9, width=.1, depth=.015)
    k.greebles(a.part('Roof_boxes', 'MetalSheet'), (0, .7, 1.75), (1, 0, 0), (0, 1, 0), (1.5, 2.2), 3, seed=2821,
               height=(.06, .14), chamfer=.012)
    for s in (-1, 1):
        for y in (-.2, 2.1):
            steel.cyl(.07, .5, loc=(s * .85, y, .62), seg=8, bevel=0)
            steel.cyl(.13, .06, loc=(s * .85, y, .34), seg=10, bevel=.01, bseg=1)
        k.block(a.part('Lockers', 'MetalSheet'), (.1, 1.4, .5), loc=(s * .9, .95, 1.2), chamfer=.02)
    steel.cyl(.26, .18, loc=(0, 1.3, 1.83), seg=10, bevel=.02, bseg=1)
    k.lathe(steel, [(.2, 0), (.2, 1.5), (.15, 1.5), (.15, 1.55)], loc=(0, 1.3, 1.75), seg=10, worn=(1,))
    parts.hatch(a, -.5, -1.9, 1.75, .2)
    ra = a.pivot('Radar', (0, 1.3, 3.2))
    a.part('Radar_head', 'Steel', ra).cyl(.2, .22, loc=(0, 0, .11), seg=10, bevel=.02, bseg=1)
    k.block(a.part('Radar_panel', 'Team', ra), (1.7, .22, .7), loc=(0, 0, .45), chamfer=.04)
    ar = a.part('Radar_cells', 'Undercarriage', ra)
    for i in range(5):
        for j in range(3):
            ar.box((.28, .03, .18), loc=(-.68 + i * .34, -.12, .27 + j * .2), bevel=0)
    k.block(a.part('Radar_cabin', 'Armor', ra), (.7, .5, .5), loc=(0, .36, .45), chamfer=.04)
    a.part('Radar_beacon', 'TeamGlow').sphere(.05, loc=(.0, 0, .83), seg=6, rings=4)
    _rws(a, 0, -1.4, 1.75, length=.55)
    _points(a, (.6, 2.3, .8), (0, 0, 1.5))
    k.clean(a)


# ============================================================================= towed AT gun
def towed_at_gun(a):
    """A 2A45 Sprut-B class towed anti-tank gun (7.9 x 2.62 x 2.04 m): a long smoothbore barrel with a baffle brake
    on a cradle (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`) behind a gun shield, two road wheels,
    and a split trail carriage spread behind with spades. No armour: crew, sight and ammunition boxes in the open."""
    _suffixed(a)
    team, armor, steel = a.part('Carriage', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    for s in (-1, 1):
        _tyre(a, s * .95, .2, .5, .3, s, seg=12)
        # split trail: a long leg to a ground spade, a toe cap and a hook
        trail = a.part('Trails', 'Team')
        trail.limb((s * .25, .45, .68), (s * 1.1, 3.7, .2), .2, .16, bevel=.02)
        k.block(armor, (.4, .34, .08), loc=(s * 1.1, 3.85, .1), rot=(.2, 0, 0), chamfer=.015)
        steel.cyl(.07, .26, loc=(s * 1.1, 3.5, .34), seg=6, bevel=0)
        k.block(a.part('Trail_brace', 'Armor'), (.12, .6, .12), loc=(s * .82, 1.2, .5), rot=(0, 0, s * -.5), chamfer=.01)
        # gun shield wings
        k.block(team, (.5, .08, .8), loc=(s * .98, -.34, 1.5), rot=(0, 0, s * .5), chamfer=.015)
        k.block(armor, (.14, .3, .2), loc=(s * .45, -.42, 1.12), chamfer=.015)
    steel.box((1.9, .2, .2), loc=(0, .2, .5), bevel=.03)                                        # axle
    k.block(team, (1.0, 1.5, .34), loc=(0, .3, .85), chamfer=.05)                               # carriage body
    k.block(team, (1.5, .1, .96), loc=(0, -.5, 1.55), chamfer=.015, taper=(1, .95))             # shield
    t = a.pivot('Turret', (0, .3, 1.25))
    k.block(a.part('Cradle', 'Armor', t), (.5, 1.0, .46), loc=(0, -.1, -.05), chamfer=.04)
    k.block(a.part('Breech', 'Steel', t), (.34, .6, .34), loc=(0, .5, 0), chamfer=.03)
    _gun(a, t, -.6, 0, 3.35, .08, brake='baffle', seg=12)
    k.block(a.part('Sight', 'Armor', t), (.14, .3, .18), loc=(-.34, .1, .26), chamfer=.02)
    a.part('Sight_glass', 'Glass', t).box((.08, .03, .09), loc=(-.34, -.06, .28), bevel=0)
    a.part('Aim_wheel', 'Hazard', t).cyl(.15, .04, loc=(-.4, .5, -.15), rot=ACROSS, seg=10, bevel=.01, bseg=1)
    k.block(a.part('Ammo_boxes', 'Crate'), (.5, .6, .3), loc=(.85, 1.6, .5), chamfer=.03)
    k.block(a.part('Ammo_boxes', 'Crate'), (.4, .5, .26), loc=(.85, 2.3, .48), chamfer=.03)
    k.block(a.part('Seat', 'Undercarriage'), (.4, .4, .08), loc=(-.5, 1.3, 1.0), chamfer=.01)
    _points(a, (0, .45, .7), (0, 1.0, 1.0))
    k.clean(a)


# ============================================================================= EW trucks (dazzler, GPS jammer)
def _ew_truck(a, shelter_y0, shelter_y1, sw=2.7, top=2.6):
    """The 8x8 chassis of the two EW trucks (9.0 x 2.76 m): tyres, cab with a roof remote weapon station (`Turret`,
    `Muzzle_main`), exhausts, the equipment shelter from shelter_y0 to shelter_y1. Returns the shelter part."""
    shelter = a.part('Shelter', 'Team')
    _truck_base(a, (-3.4, -2.1, 2.0, 3.3), .98, .55, .42, -4.5, 4.5, -2.7, 2.5, 2.3, rail=.55)
    k.extrude(shelter, [(shelter_y0, 1.0), (shelter_y0, top), (shelter_y1, top), (shelter_y1, 1.0)], sw, axis='X', chamfer=.08)
    k.inset(shelter, lambda c, n, f: abs(n.x) > .9, width=.12, depth=.015)
    for s in (-1, 1):
        mv._exhaust(a, s * .9, 4.5, 1.0, .5, .22)
    parts.hatch(a, .5, -3.4, 2.5, .22)
    _rws(a, 0, -3.5, 2.5, length=.55)
    return shelter


def dazzler_vehicle(a):
    """A Peresvet class dazzler (9.0 x 2.76 x 3.83 m): an 8x8 EW truck whose shelter carries a lift frame with a
    large forward-facing housing of six glowing lenses (two rows of three, bezels and glass), a roof remote weapon
    station (`Turret`, `Muzzle_main`), door panels, vents and side lockers."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _ew_truck(a, -2.5, 4.4)
    for s in (-1, 1):
        k.block(a.part('Lockers', 'MetalSheet'), (.08, 1.6, .7), loc=(s * 1.34, 1.2, 1.5), chamfer=.015)
        k.block(a.part('Door_panels', 'MetalSheet'), (.08, 1.2, .9), loc=(s * 1.34, -1.4, 1.9), chamfer=.015)
        for y in (2.6, 3.4):
            a.part('Vents', 'Undercarriage').box((.06, .5, .3), loc=(s * 1.37, y, 2.1), bevel=0)
        steel.limb((s * .7, -.5, 2.6), (s * .7, -1.35, 3.0), .14, .14, bevel=0)            # lift rams
    steel.box((2.0, 1.0, .1), loc=(0, -.9, 2.65), bevel=.02)
    k.block(a.part('Lens_housing', 'Team'), (2.3, .55, 1.2), loc=(0, -1.4, 3.2), chamfer=.06)
    k.block(a.part('Lens_hood', 'Armor'), (2.4, .3, .1), loc=(0, -1.55, 3.85), chamfer=.02)
    y0 = -1.4 - .275
    for x in (-.75, 0, .75):
        for z in (2.9, 3.5):
            a.part('Lens_bezels', 'Armor').cyl(.31, .2, loc=(x, y0 - .08, z), rot=FORWARD, seg=12, bevel=.02)
            a.part('Lens_glass', 'Energy').cyl(.24, .05, loc=(x, y0 - .19, z), rot=FORWARD, seg=12, bevel=0)
    k.greebles(a.part('Roof_boxes', 'MetalSheet'), (0, 2.2, 2.6), (1, 0, 0), (0, 1, 0), (2.0, 3.0), 4, seed=2831,
               height=(.06, .15), chamfer=.012)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(.9, 4.0, 2.7), seg=6, rings=4)
    _points(a, (.9, 4.5, 1.0), (0, .5, 1.9))
    k.clean(a)


def gps_jammer_vehicle(a):
    """A Pole-21 class GPS jammer (9.0 x 2.76 x 3.83 m): an 8x8 truck with an equipment shelter behind the cab, a
    flatbed with stowed antenna sections and a cable reel, and a tall mast carrying a turning array of three
    dipole tiers (`Radar`), a roof remote weapon station (`Turret`, `Muzzle_main`)."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    _ew_truck(a, -2.5, -.2, sw=2.6, top=2.45)
    k.block(a.part('Flatbed', 'Team'), (2.6, 4.5, .25), loc=(0, 2.25, 1.1), chamfer=.04)
    for s in (-1, 1):
        k.block(a.part('Lockers', 'MetalSheet'), (.1, 1.5, .7), loc=(s * 1.3, -1.4, 1.3), chamfer=.015)
        k.block(a.part('Bed_rails', 'Armor'), (.08, 4.4, .3), loc=(s * 1.26, 2.25, 1.38), chamfer=.01)
        steel.cyl(.07, .5, loc=(s * 1.2, 4.2, .6), seg=8, bevel=0)
        steel.cyl(.17, .06, loc=(s * 1.2, 4.2, .34), seg=10, bevel=.01, bseg=1)
        for j, y in enumerate((3.0, 3.5)):                                                   # stowed antenna sections
            k.block(a.part('Stowed_sections', 'Steel'), (.14, 1.3, .14), loc=(s * (.75 - j * .2), 2.6 + j * .9, 1.35), chamfer=.015)
    a.part('Cable_reel', 'Hazard').cyl(.4, .4, loc=(0, 3.9, 1.5), rot=ACROSS, seg=12, bevel=.02)
    steel.cyl(.4, .1, loc=(0, 2.0, 1.28), seg=14, bevel=.02, bseg=1)
    k.lathe(steel, [(.16, 0), (.16, 1.55), (.12, 1.55), (.12, 1.6)], loc=(0, 2.0, 1.3), seg=10, worn=(1,))
    ra = a.pivot('Radar', (0, 2.0, 2.75))
    a.part('Radar_head', 'Steel', ra).cyl(.18, .2, loc=(0, 0, .1), seg=10, bevel=.02, bseg=1)
    bars = a.part('Radar_bars', 'Steel', ra)
    rods = a.part('Radar_rods', 'Team', ra)
    for z, w in ((.2, 1.9), (.5, 1.5), (.8, 1.1)):
        bars.cyl(.05, w, loc=(0, 0, z), rot=ACROSS, seg=6, bevel=0)
        bars.cyl(.05, w * .7, loc=(0, 0, z), rot=FORWARD, seg=6, bevel=0)
        for i in range(-2, 3):
            rods.box((.1, .1, .3), loc=(i * w / 5, 0, z + .15), bevel=0)
    a.part('Radar_cap', 'TeamGlow').sphere(.07, loc=(0, 0, .96), seg=6, rings=4)
    _points(a, (.9, 4.5, 1.0), (0, .5, 1.9))
    k.clean(a)


# ============================================================================= ground-launched cruise missile vehicle
def ground_cruise_missile_vehicle(a):
    """A Typhon MRC class ground-launched cruise missile vehicle (7.18 x 2.7 x 2.97 m): a tractor with a cab and a
    low trailer carrying a turntable (`Turret`) with two long vertical missile canisters (`Muzzle_main` at the
    tops), a launch frame, rear stabiliser jacks."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    deck = a.part('Trailer', 'Team')
    _truck_base(a, (-2.7, -1.4), 1.1, .5, .42, -3.59, 3.59, -2.2, 2.3, 2.3, rail=.55, lamp_x=.8)
    fen = a.part('Fenders', 'Team')
    for y in (2.2, 3.05):
        for s in (-1, 1):
            _tyre(a, s * 1.1, y, .42, .4, s)
    for s in (-1, 1):
        fen.box((.5, 1.7, .06), loc=(s * 1.12, 2.62, .9), bevel=.02, seg=1)
        a.part('Skirts', 'Team').box((.06, 3.4, .3), loc=(s * 1.2, 1.0, .85), bevel=.015, seg=1)
        steel.cyl(.07, .5, loc=(s * 1.2, 3.3, .62), seg=8, bevel=0)
        steel.cyl(.17, .06, loc=(s * 1.2, 3.3, .34), seg=10, bevel=.01, bseg=1)
    k.block(deck, (2.5, 4.9, .25), loc=(0, 1.15, .93), chamfer=.04)
    steel.cyl(.35, .1, loc=(0, -1.2, 1.0), seg=12, bevel=.015, bseg=1)                       # kingpin plate
    k.block(armor, (1.2, .4, .3), loc=(0, -1.4, 1.05), chamfer=.03)
    for dx in (-.9, .9):
        mv._taillight(a, dx, 3.59, .98)
    k.block(a.part('Electronics_box', 'Team'), (.7, 1.0, .6), loc=(.9, -.1, 1.3), chamfer=.04)
    k.block(a.part('Electronics_box', 'Team'), (.7, 1.0, .6), loc=(-.9, -.1, 1.3), chamfer=.04)
    k.greebles(a.part('Deck_boxes', 'Armor'), (0, 2.7, 1.06), (1, 0, 0), (0, 1, 0), (2.0, 1.4), 3, seed=2841,
               height=(.05, .1), chamfer=.012)
    t = a.pivot('Turret', (0, 1.2, 1.0))
    steel_t = a.part('Turret_steel', 'Steel', t)
    steel_t.cyl(.85, .1, loc=(0, 0, .05), seg=18, bevel=.02, bseg=1)
    k.block(a.part('Turret_base', 'Team', t), (1.5, 1.3, .22), loc=(0, 0, .21), chamfer=.04, taper=(.92, .92))
    for ix in (-1, 1):
        cx = ix * .42
        k.lathe(a.part('Canisters', 'Fuel', t), [(0, .3), (.27, .3), (.27, 1.9), (.24, 1.94), (.24, 2.0), (0, 2.0)],
                loc=(cx, 0, 0), seg=12, worn=(2,))
        k.lathe(a.part('Canister_bands', 'Hazard', t), [(.275, 1.55), (.275, 1.7)], loc=(cx, 0, 0), seg=12, caps=(False, False))
        k.lathe(a.part('Canister_bands', 'Hazard', t), [(.275, .5), (.275, .6)], loc=(cx, 0, 0), seg=12, caps=(False, False))
    for y in (-.22, .22):
        k.block(a.part('Launch_frame', 'Team', t), (1.5, .1, .12), loc=(0, y, 1.0), chamfer=.01)
        k.block(a.part('Launch_frame', 'Team', t), (1.5, .1, .12), loc=(0, y, 1.8), chamfer=.01)
    a.pivot('Muzzle_main', (-.42, 0, 2.0), t)
    parts.hatch(a, .5, -3.1, 2.3, .2)
    parts.antenna(a.part('Antennas', 'Steel'), (-.8, -2.6, 2.3), h=.2, r=.04, seg=6)
    _points(a, (.9, 3.5, .8), (0, 0, 1.8))
    k.clean(a)


# ============================================================================= bridging vehicle
def bridging_vehicle(a):
    """An AVLB / MTU-72 class bridgelayer (6.45 x 3.02 x 2.02 m): a tracked hull with skirts, a folded scissor
    bridge (two stacked span halves with rails, ribs and two tread plates) lifted on hydraulic rams, a driver hatch
    and a low remote weapon station on the front right fender (`Turret`, `Muzzle_main`)."""
    _suffixed(a)
    hull, armor, steel = a.part('Hull', 'Team'), a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    span = a.part('Bridge', 'Team')
    _tracks(a, 1.2, 5.6, .85, .3, 6, .5)
    k.extrude(a.part('Hull_tub', 'Team'), [(-2.4, .4), (-2.6, .65), (2.9, .65), (3.0, .4)], 2.0, axis='X', chamfer=.04)
    _hull(hull, [(-2.8, .62), (-2.35, 1.0), (-1.9, 1.1), (2.9, 1.1), (3.05, .95), (3.05, .62)], 2.7, ch=.06)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -1.9, width=.08, depth=.012)
    for s in (-1, 1):
        mv._skirt(a, s, 1.47, -2.2, 2.7, .5, 1.05, 5, thick=.07, bolts=False)
        mv._exhaust(a, s * .6, 3.04, .85, .5, .22)
        steel.limb((s * .5, -2.4, 1.1), (s * .5, -2.7, 1.55), .12, .12, bevel=0)           # lift rams
        k.block(armor, (.12, 6.0, .12), loc=(s * 1.28, 0, 1.64), chamfer=.01)                  # side rails
    _lights(a, .95, -2.78, 3.05, .9, .9)
    # the folded scissor bridge: a lower and an upper half, hinge blocks, ribs, two tread plates
    k.block(span, (2.5, 6.4, .22), loc=(0, 0, 1.35), chamfer=.04)
    k.block(span, (2.5, 6.0, .22), loc=(0, 0, 1.8), chamfer=.04)
    for y in (-2.9, 0, 2.9):
        k.block(steel, (2.4, .22, .3), loc=(0, y, 1.58), chamfer=.02)
    for y in (-2.0, -1.0, 1.0, 2.0):
        k.block(armor, (2.3, .12, .06), loc=(0, y, 1.94), chamfer=0)
    for s in (-1, 1):
        a.part('Tread_plates', 'Steel').box((.8, 5.6, .04), loc=(s * .75, 0, 1.93), bevel=0)
    parts.hatch(a, -.8, -2.1, 1.1, .22)
    mv._periscopes(a, [(-.8 + dx, -2.5, 1.0, 0) for dx in (-.17, 0, .17)])
    _rws(a, 1.0, -2.3, 1.1, length=.6)
    _points(a, (.6, 3.05, .9), (0, 0, 1.4))
    k.clean(a)


# ============================================================================= pass B towers
def _sand_ring(a, radius, courses, seed, gap_u=None, gap_w=.42, n=15, bag=(.58, .36, .2), z0=.14):
    """Courses of sandbags round a circle (`Sandbags`), a gap of `gap_w` rad centred on angle gap_u in the lowest
    courses (an entrance)."""
    import random
    rng = random.Random(seed)
    sand = a.part('Sandbags', 'Sandbag')
    for course in range(courses):
        for i in range(n):
            u = TAU * (i + .5 * (course % 2)) / n
            if gap_u is not None and abs(((u - gap_u + math.pi) % TAU) - math.pi) < gap_w and course < courses - 1:
                continue
            r = radius + rng.uniform(-.025, .025)
            k.block(sand, (bag[0] + rng.uniform(-.04, .04), bag[1], bag[2]),
                    loc=(math.cos(u) * r, math.sin(u) * r, z0 + course * bag[2]), rot=(0, 0, u + R90), chamfer=0)


# ============================================================================= flare / searchlight tower
def flare_searchlight_tower(a):
    """A small flare launcher post (3.6 x 3.6 x 5.0 m): four concrete footings, four braced steel legs to a Team
    deck with rails and a ladder, a flare launcher on a turntable (`Turret`, `Launcher`, `Tubes`, `Muzzle_main`:
    2 x 3 tubes at 30 degrees), flare drums and crates, a floodlight on a mast and an antenna."""
    _suffixed(a)
    steel, armor, team = a.part('Legs', 'Steel'), a.part('Armor', 'Armor'), a.part('Deck', 'Team')
    conc = a.part('Footings', 'Concrete')
    zd = 3.55
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.block(conc, (.6, .6, .26), loc=(sx * 1.5, sy * 1.5, .13), chamfer=.03)
            steel.limb((sx * 1.5, sy * 1.5, .2), (sx * .85, sy * .85, zd), .16, .16, bevel=.01)
    # cross braces at two levels
    for z in (1.2, 2.3):
        f = 1.5 - (1.5 - .85) * (z - .2) / (zd - .2)
        for s in (-1, 1):
            a.part('Braces', 'Steel').limb((s * f, -f, z), (s * f, f, z), .1, .1, bevel=0)
            a.part('Braces', 'Steel').limb((-f, s * f, z), (f, s * f, z), .1, .1, bevel=0)
    k.block(team, (2.2, 2.2, .14), loc=(0, 0, zd), chamfer=.03)
    k.block(a.part('Deck_ring', 'Armor'), (2.3, 2.3, .06), loc=(0, 0, zd - .1), chamfer=0)
    # rails
    for s in (-1, 1):
        for sy in (-1, 1):
            k.block(armor, (.1, .1, .8), loc=(s * 1.05, sy * 1.05, zd + .47), chamfer=0)
        k.block(armor, (.08, 2.2, .08), loc=(s * 1.05, 0, zd + .85), chamfer=0)
        if s < 0:
            k.block(armor, (2.2, .08, .08), loc=(0, -1.05, zd + .85), chamfer=0)
    # ladder up the +Y side
    for s in (-1, 1):
        a.part('Ladder', 'Steel').limb((s * .3, 1.75, .2), (s * .3, 1.1, zd), .1, .08, bevel=0)
    for j in range(1, 8):
        z = .2 + j * (zd - .2) / 8
        y = 1.75 - (1.75 - 1.1) * (z - .2) / (zd - .2)
        a.part('Ladder', 'Steel').box((.6, .1, .08), loc=(0, y, z), bevel=0)
    # launcher turntable: 2 x 3 flare tubes, 30 degrees up
    t = a.pivot('Turret', (0, 0, zd + .07))
    a.part('Turntable', 'Steel', t).cyl(.6, .1, loc=(0, 0, .05), seg=14, bevel=.02, bseg=1)
    k.block(a.part('Launcher_body', 'Team', t), (1.1, .9, .5), loc=(0, .05, .4), chamfer=.05, rot=(.0, 0, 0))
    p = math.radians(30)
    pit = (R90 - p, 0, 0)
    for ix in (-1, 0, 1):
        for iz in (0, 1):
            cx, cz = ix * .32, .35 + iz * .3
            k.lathe(a.part('Tubes', 'Armor', t), [(.12, -.35), (.12, .3), (.13, .75), (.13, .82), (.0, .82)],
                    loc=(cx, .1, cz), rot=pit, seg=8, worn=(3,))
            a.part('Tube_caps', 'Alloy', t).cyl(.08, .04, loc=(cx, .1 - math.cos(p) * .83, cz + math.sin(p) * .83),
                                                rot=pit, seg=8, bevel=0)
    a.part('Launcher_bands', 'Hazard', t).box((1.1, .06, .1), loc=(0, -.4, .66), bevel=0)
    a.pivot('Muzzle_main', (0, .1 - math.cos(p) * .85, .5 + math.sin(p) * .85), t)
    # floodlight on a mast at the back corner, antenna at the front corner
    k.lathe(a.part('Light_mast', 'Steel'), [(.08, 0), (.08, .85)], loc=(-.85, .85, zd + .07), seg=6)
    k.lathe(a.part('Floodlight', 'Armor'), [(.1, -.12), (.26, .1), (.3, .2), (.0, .2)], loc=(-.85, .75, zd + .96), rot=(R90 - .2, 0, 0), seg=10, worn=(2,))
    a.part('Floodlamp', 'Lamp').cyl(.22, .04, loc=(-.85, .75 - .22, zd + 1.0), rot=(R90 - .2, 0, 0), seg=10, bevel=0)
    parts.antenna(a.part('Antennas', 'Steel'), (.85, .85, zd + .07), h=1.25, r=.045, seg=6)
    # flare drums and crates on the deck
    for x, y in ((.7, -.6), (.7, -.2), (.7, .2)):
        a.part('Flare_drums', 'Hazard').cyl(.14, .5, loc=(x, y, zd + .39), seg=8, bevel=.02)
    k.block(a.part('Crates', 'Crate'), (.5, .4, .3), loc=(-.6, -.7, zd + .22), chamfer=.03)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(.85, .85, zd + 1.4), seg=6, rings=4)
    k.clean(a)


# ============================================================================= recoilless gun tower
def recoilless_gun_tower(a):
    """An SPG-9 Kopyo emplacement (4.2 x 4.2 x 3.0 m): a round sandbagged pit with a rear entrance, a tripod head on a
    Team pad carrying the short recoilless tube (`Turret`, `Cradle`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`) behind
    a split gun shield, rounds, crates, a stake fence, a radio mast and a flag."""
    _suffixed(a)
    steel, armor = a.part('Steel', 'Steel'), a.part('Armor', 'Armor')
    k.lathe(a.part('Pit_floor', 'Concrete'), [(0, 0), (2.05, 0), (2.05, .1), (0, .1)], seg=22)
    k.lathe(a.part('Pad', 'Team'), [(0, .1), (1.1, .1), (1.1, .18), (1.0, .22), (0, .22)], seg=16, worn=(2,))
    _sand_ring(a, 1.92, 4, 2851, gap_u=R90, n=17, bag=(.6, .36, .2))
    t = a.pivot('Turret', (0, -.1, 1.05))
    for j in range(3):
        u = R90 + j * TAU / 3
        steel.limb((math.cos(u) * .6, -.1 + math.sin(u) * .6, .24), (0, -.1, 1.0), .1, .1, bevel=0)
    k.lathe(a.part('Head_ring', 'Steel', t), [(.28, -.06), (.28, .03), (.22, .06)], seg=12, worn=(1,))
    k.block(a.part('Head', 'Team', t), (.6, .5, .26), loc=(0, 0, .17), chamfer=.04)
    k.block(a.part('Cradle', 'Armor', t), (.3, .8, .2), loc=(0, .0, .38), chamfer=.03)
    parts.barrel(a, 'Main_cannon', t, 0, -.3, .45, 1.6, .07, seg=10, sleeve=1.2, extractor=(.7, 1.3, .4),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -.3 - 1.6 - .14, .45), t)
    k.lathe(a.part('Venturi', 'Armor', t), [(.07, 0), (.14, .22), (.15, .34), (.1, .4), (0, .4)], loc=(0, -.05, .45), rot=BACKWARD, seg=10, worn=(3,))
    for s in (-1, 1):
        k.block(a.part('Gun_shield', 'Armor', t), (.42, .06, .6), loc=(s * .36, -.7, .5), chamfer=.01)
    k.block(a.part('Sight', 'Armor', t), (.1, .24, .14), loc=(-.2, .05, .55), chamfer=.015)
    a.part('Sight_glass', 'Glass', t).box((.06, .03, .07), loc=(-.2, -.08, .56), bevel=0)
    k.block(a.part('Crates', 'Crate'), (.55, .7, .36), loc=(1.0, .75, .28), chamfer=.03)
    k.block(a.part('Crates', 'Crate'), (.5, .5, .3), loc=(-1.0, .6, .25), chamfer=.03)
    for j in range(3):
        a.part('Rounds', 'Fuel').cyl(.09, .6, loc=(.7 + j * .22, .0, .3), rot=FORWARD, seg=8, bevel=.015)
        a.part('Round_noses', 'Hazard').cyl(.09, .08, loc=(.7 + j * .22, -.34, .3), rot=FORWARD, seg=8, bevel=0)
    for i in range(6):
        u = -R90 + (i - 2.5) * .5
        a.part('Stakes', 'Wood').box((.1, .1, .5), loc=(math.cos(u) * 2.02, math.sin(u) * 2.02, .3), bevel=0)
    parts.antenna(a.part('Antennas', 'Steel'), (-1.2, 1.0, .7), h=2.2, r=.045, seg=6)
    a.part('Flag', 'Team').box((.5, .03, .3), loc=(-1.0, 1.0, 2.7), bevel=0)
    k.clean(a)


# ============================================================================= bunker shelter tower
def bunker_shelter_tower(a):
    """A concrete bunker (6.0 x 5.0 x 2.2 m): thick concrete walls with a Team roof slab and a Team band on the
    front, earth berms banked against both sides and the rear, an entrance porch with a steel door and steps,
    sandbag piles either side of the door, roof vents and a beacon. No weapon."""
    _suffixed(a)
    steel, armor = a.part('Steel', 'Steel'), a.part('Armor', 'Armor')
    conc = a.part('Walls', 'Concrete')
    berm = a.part('Berm', 'Sandbag')
    k.block(a.part('Slab', 'Concrete'), (4.6, 6.0, .16), loc=(0, -.0, .08), chamfer=.03)
    k.block(conc, (3.4, 4.6, 1.7), loc=(0, .0, .85), chamfer=.08)
    k.block(a.part('Roof', 'Team'), (3.7, 4.9, .26), loc=(0, 0, 1.8), chamfer=.06)
    for s in (-1, 1):
        k.block(berm, (1.6, 4.6, 1.3), loc=(s * 1.7, .2, .65), chamfer=.04, taper=(.35, .9))
    k.block(berm, (3.6, 1.2, 1.3), loc=(0, 2.3, .65), chamfer=.04, taper=(.9, .35))
    # front: band, door, porch, steps, sandbag piles
    k.block(a.part('Team_bands', 'Team'), (3.42, .05, .3), loc=(0, -2.32, 1.45), chamfer=0)
    k.block(a.part('Porch', 'Concrete'), (1.8, .7, 1.35), loc=(0, -2.65, .675), chamfer=.04)
    k.block(a.part('Porch_roof', 'Team'), (2.0, .8, .14), loc=(0, -2.65, 1.42), chamfer=.03)
    k.block(armor, (1.0, .1, 1.1), loc=(0, -3.0, .72), chamfer=.02)
    a.part('Door_lamp', 'Lamp').box((.14, .05, .1), loc=(.7, -3.03, 1.1), bevel=0)
    import random
    rng = random.Random(2861)
    sand = a.part('Sandbags', 'Sandbag')
    for s in (-1, 1):
        for course in range(3):
            for i in range(3 - course // 2):
                k.block(sand, (.6, .36, .2), loc=(s * (.82 + i * .52 + .26 * (course % 2)), -2.78 + rng.uniform(-.03, .03), .1 + course * .2),
                        rot=(0, 0, rng.uniform(-.08, .08)), chamfer=0)
    # roof vents, hatch, antenna, beacon
    for x, y in ((-.9, -1.2), (.9, -1.2), (0, .9)):
        k.lathe(a.part('Vents', 'Steel'), [(.12, 0), (.12, .22), (.18, .26), (.18, .3)], loc=(x, y, 1.93), seg=8, worn=(2,))
    parts.hatch(a, .8, 1.5, 1.93, .22)
    parts.antenna(a.part('Antennas', 'Steel'), (-1.2, 1.6, 1.93), h=.12, r=.04, seg=6)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(-1.2, -1.8, 2.0), seg=6, rings=4)
    k.greebles(a.part('Roof_boxes', 'MetalSheet'), (0, .5, 1.93), (1, 0, 0), (0, 1, 0), (2.8, 3.2), 3, seed=2862, height=(.05, .1), chamfer=.012)
    k.clean(a)


# ============================================================================= drone net tower
def drone_net_tower(a):
    """An anti-drone net corridor (6.0 x 4.0 x 4.6 m): two tall poles 5.2 m apart on concrete bases with splayed
    A-frame legs, anti-drone netting strung between them (eight cords, twelve hanging lines), a zap emitter on
    each pole top (`Turret`, `Muzzle_main` on the first) and a control box. No turret."""
    _suffixed(a)
    steel, team = a.part('Poles', 'Steel'), a.part('Pole_caps', 'Team')
    conc, net = a.part('Footings', 'Concrete'), a.part('Net', 'Medical')
    ys = (-2.55, 2.55)
    for y in ys:
        k.block(conc, (.9, .9, .3), loc=(0, y, .15), chamfer=.04)
        k.lathe(steel, [(.16, 0), (.14, 4.0), (.12, 4.05)], loc=(0, y, .28), seg=8, worn=(1,))
        k.block(team, (.5, .5, .22), loc=(0, y, 4.1), chamfer=.03)
        for s in (-1, 1):
            steel.limb((0, y, 2.3), (s * 1.78, y, .22), .14, .14, bevel=0)
            a.part('Foot_pads', 'Team').cyl(.26, .12, loc=(s * 1.78, y, .06), seg=8, bevel=.02, bseg=1)
    # the net: eight cords along Y, twelve hanging lines
    for j in range(8):
        z = 1.1 + j * .44
        k.block(net, (.1, 5.1, .1), loc=(0, 0, z), chamfer=0)
    for i in range(12):
        y = -2.35 + i * (4.7 / 11)
        k.block(net, (.1, .1, 3.1), loc=(0, y, 2.65), chamfer=0)
    for y in (-2.5, 2.5):
        a.part('Net_weights', 'Hazard').cyl(.12, .2, loc=(0, y, 1.0), seg=6, bevel=0)
    # the emitters: a glowing ball in a Team ring on each pole top; the first is the weapon node
    t = a.pivot('Turret', (0, ys[0], 4.2))
    a.part('Emitter_ring', 'Armor', t).cyl(.26, .08, loc=(0, 0, .04), seg=10, bevel=.015, bseg=1)
    a.part('Emitter_ball', 'Energy', t).sphere(.2, loc=(0, 0, .2), seg=10, rings=6)
    a.pivot('Muzzle_main', (0, 0, .4), t)
    a.part('Emitter_ring2', 'Armor').cyl(.26, .08, loc=(0, ys[1], 4.24), seg=10, bevel=.015, bseg=1)
    a.part('Emitter_ball2', 'Energy').sphere(.2, loc=(0, ys[1], 4.4), seg=10, rings=6)
    k.block(a.part('Control_box', 'Team'), (.6, .5, .7), loc=(.9, -2.55, .35), chamfer=.04)
    a.part('Box_lamp', 'TeamGlow').box((.1, .04, .06), loc=(.9, -2.82, .55), bevel=0)
    parts.antenna(a.part('Antennas', 'Steel'), (.9, -2.55, .7), h=.9, r=.045, seg=6)
    k.clean(a)


# ============================================================================= one-shot ATGM tower
def one_shot_atgm_tower(a):
    """An automatic Kornet launcher box (4.8 x 4.8 x 3.6 m): a concrete pedestal with embrasure slits, a Team band and
    a Team roof deck, a sandbag apron round it, a rear door with steps, and on a turntable (`Turret`) a launcher box
    with eight ready-to-fire tubes in two rows (`Launcher`, `Tubes`, `Muzzle_main`, `Muzzle_missile`, `.001`) pitched
    up 12 degrees. Nothing else: no spare missiles."""
    _suffixed(a)
    steel, armor = a.part('Steel', 'Steel'), a.part('Armor', 'Armor')
    conc = a.part('Pedestal', 'Concrete')
    k.block(a.part('Slab', 'Concrete'), (4.5, 4.5, .14), loc=(0, 0, .07), chamfer=.03)
    k.block(conc, (3.8, 3.8, 1.4), loc=(0, 0, .84), chamfer=.08)
    k.block(a.part('Deck', 'Team'), (4.0, 4.0, .16), loc=(0, 0, 1.62), chamfer=.04)
    for s in (-1, 1):
        a.part('Embrasures', 'Undercarriage').box((.9, .06, .2), loc=(s * .95, -1.92, 1.1), bevel=0)
        a.part('Embrasures', 'Undercarriage').box((.06, .9, .2), loc=(s * 1.92, -.2, 1.1), bevel=0)
    k.block(a.part('Team_bands', 'Team'), (3.84, .05, .22), loc=(0, -1.92, 1.42), chamfer=0)
    k.block(a.part('Team_bands', 'Team'), (.05, 3.84, .22), loc=(-1.92, 0, 1.42), chamfer=0)
    k.block(a.part('Team_bands', 'Team'), (.05, 3.84, .22), loc=(1.92, 0, 1.42), chamfer=0)
    # sandbag apron round the pedestal (to the 4.8 m footprint)
    import random
    rng = random.Random(2871)
    sand = a.part('Sandbags', 'Sandbag')
    for course in range(2):
        for side in range(4):
            horiz = side % 2 == 0
            sgn = -1 if side < 2 else 1
            for i in range(7):
                off = -1.9 + i * .6 + (.3 if course else 0)
                if abs(off) > 2.0:
                    continue
                if side == 3 and abs(off) < .55:          # the rear door
                    continue
                loc = (off, sgn * 2.2, .27 + course * .2 - .1) if horiz else (sgn * 2.2, off, .27 + course * .2 - .1)
                k.block(sand, (.56, .38, .2) if horiz else (.38, .56, .2), loc=loc,
                        rot=(0, 0, rng.uniform(-.05, .05)), chamfer=0)
    # the rear door and steps
    k.block(armor, (.9, .08, 1.0), loc=(0, 1.93, .75), chamfer=.02)
    k.block(a.part('Steps', 'Concrete'), (1.2, .4, .15), loc=(0, 2.15, .15), chamfer=0)
    # turntable and the launcher box
    t = a.pivot('Turret', (0, 0, 1.7))
    a.part('Turntable', 'Steel', t).cyl(.95, .12, loc=(0, 0, .06), seg=16, bevel=.02, bseg=1)
    k.block(a.part('Launcher', 'Team', t), (2.4, 1.1, 1.0), loc=(0, .1, .66), chamfer=.06, rot=(.0, 0, 0))
    k.block(a.part('Launcher_hood', 'Armor', t), (2.5, .5, .1), loc=(0, -.5, 1.2), chamfer=.015)
    p = math.radians(12)
    pit = (R90 - p, 0, 0)
    for ix in (-1.5, -.5, .5, 1.5):
        for iz in (0, 1):
            cx, cz = ix * .5, .43 + iz * .5
            k.lathe(a.part('Tubes', 'Armor', t), [(.13, -.3), (.14, .0), (.14, 1.05), (.16, 1.1), (.0, 1.1)],
                    loc=(cx, -.4, cz), rot=pit, seg=10, worn=(3,))
            a.part('Launcher_bores', 'Undercarriage', t).cyl(.1, .03, loc=(cx, -.4 - math.cos(p) * 1.08, cz + math.sin(p) * 1.08),
                                                             rot=pit, seg=10, bevel=0)
    a.part('Launcher_bands', 'Hazard', t).box((2.4, .06, .12), loc=(0, -.46, 1.0), bevel=0)
    mz = (-.4 - math.cos(p) * 1.12, .68 + math.sin(p) * 1.12)
    a.pivot('Muzzle_main', (0, mz[0], mz[1]), t)
    a.pivot('Muzzle_missile', (-.25, mz[0], mz[1]), t)
    pv(a, 'Muzzle_missile.001', (.25, mz[0], mz[1]), t)
    # a radio mast with a beacon on the deck's rear corner
    parts.antenna(a.part('Antennas', 'Steel'), (-1.7, 1.7, 1.7), h=1.7, r=.05, seg=6)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(-1.7, 1.7, 3.5), seg=6, rings=4)
    k.block(a.part('Crates', 'Crate'), (.6, .5, .4), loc=(1.5, 1.5, 1.9), chamfer=.03)
    k.clean(a)


BUILDERS = {
    'aa_57mm_vehicle': (aa_57mm_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'mine_rocket_truck': (mine_rocket_truck, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'prop_attack_plane': (prop_attack_plane, dict(ao_distance=.35, ao_strength=.15, ground=False)),
    'light_attack_heli': (light_attack_heli, dict(ao_distance=.35, ao_strength=.15, grime_height=.05)),
    'next_gen_tank': (next_gen_tank, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'demolition_line_vehicle': (demolition_line_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'combat_wreck_car': (combat_wreck_car, dict(ao_distance=.5, ao_strength=.15, grime_height=.05)),
    'drone_hijack_vehicle': (drone_hijack_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'manpads_tower': (manpads_tower, dict(ao_distance=.4, ao_strength=.15, grime_height=.05)),
    'river_patrol_boat': (river_patrol_boat, dict(ao_distance=.5, ao_strength=.15, grime_height=.05)),
    'river_gunboat': (river_gunboat, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'coastal_ashm_vehicle': (coastal_ashm_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'auto_loader_howitzer': (auto_loader_howitzer, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'amphib_light_vehicle': (amphib_light_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'airborne_light_tank': (airborne_light_tank, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'airborne_light_tank_chute': (airborne_light_tank_chute, dict(ao_distance=.6, ao_strength=.15, grime_height=.05)),
    'stealth_naval_strike': (stealth_naval_strike, dict(ao_distance=.4, ao_strength=.15, ground=False)),
}
BUILDERS['twin_rotor_gunship'] = (twin_rotor_gunship, dict(ao_distance=.35, ao_strength=.15, grime_height=.05))
BUILDERS['heavy_lift_helicopter'] = (heavy_lift_helicopter, dict(ao_distance=.35, ao_strength=.15, grime_height=.05))
BUILDERS['aerial_tanker'] = (aerial_tanker, dict(ao_distance=.4, ao_strength=.15, ground=False))
BUILDERS['ground_drone_carrier'] = (ground_drone_carrier, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['mobile_repair_vehicle'] = (mobile_repair_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['radar_support_vehicle'] = (radar_support_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['towed_at_gun'] = (towed_at_gun, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['dazzler_vehicle'] = (dazzler_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['gps_jammer_vehicle'] = (gps_jammer_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['ground_cruise_missile_vehicle'] = (ground_cruise_missile_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['bridging_vehicle'] = (bridging_vehicle, dict(ao_distance=.6, ao_strength=.15, grime_height=.05))
BUILDERS['flare_searchlight_tower'] = (flare_searchlight_tower, dict(ao_distance=.4, ao_strength=.15, grime_height=.05))
BUILDERS['recoilless_gun_tower'] = (recoilless_gun_tower, dict(ao_distance=.4, ao_strength=.15, grime_height=.05))
BUILDERS['bunker_shelter_tower'] = (bunker_shelter_tower, dict(ao_distance=.4, ao_strength=.15, grime_height=.05))
BUILDERS['drone_net_tower'] = (drone_net_tower, dict(ao_distance=.4, ao_strength=.15, grime_height=.05))
BUILDERS['one_shot_atgm_tower'] = (one_shot_atgm_tower, dict(ao_distance=.4, ao_strength=.15, grime_height=.05))
