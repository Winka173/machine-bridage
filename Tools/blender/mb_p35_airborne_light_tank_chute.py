"""Prompt 35 wave 12 (lane C): the airborne light tank under its parachutes, rebuilt (spec:
Tools/blender/specs/airborne_light_tank_chute.json).

The parachute variant of `airborne_light_tank` (the paradrop proxy the game drops from 30 m): it calls lane B's wave 6
builder (mb_p35_airborne_light_tank, the M8 AGS / M10 Booker-class tank) unchanged, so the vehicle, its node names and
its pivots are the ground model's, and adds a US heavy-drop rig (FM 4-20.1xx heavy airdrop: the Type V platform under
a cluster of G-11 cargo parachutes; the old file's 9 x 9 x 11 m with the canopies 8-10 m up), drawn apart from the
Russian three-canopy rig of airborne_vehicle_chute (wave 11):

- the Type V platform: the aluminium deck panels with their joints, the side rails with the tie-down clevises, the
  front and rear end plates, the stacks of paper honeycomb under the hull (energy dissipaters), team stripes;
- the tie-down chains with load binders from the hull's lifting eyes to the side rails, two ground-sensing probes;
- four suspension slings up to the M-2 parachute release (the box with its timer cover), the riser extensions to
  four confluence clevises, eight suspension lines to each canopy's skirt;
- four G-11 canopies in a square cluster, splayed outwards: each a thin shell with its radial tapes (gores), the
  reinforced skirt hem, a Team stripe band and the apex vent ring.

Runtime nodes: the vehicle's (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Mantlet`,
`Mount_mg`, `Muzzle_mg`, `Point_exhaust`, `Point_fire`); the old rig names kept (`Canopy`, `Canopy_stripe`,
`Canopy_vent`, `Rigging`). Metres, +Z up, -Y front, +X left; the origin at the vehicle's bottom centre.
"""
import math
import re

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_airborne_light_tank as ALT
import mb_p35_airborne_vehicle_chute as AVC

R90 = math.pi / 2
TAU = math.tau
LINK = (0, .2, 3.7)          # the M-2 release where the slings meet
CANOPY_R = 2.3
RING_R = 2.85                # canopy centres from the axis (a square cluster)
SKIRT_Z = 8.3
SPLAY = math.radians(16)
DECK_L, DECK_W = 6.4, 2.75   # the Type V platform (a 20 ft class platform cut to the game's size)
CY = .5                      # the platform's centre along Y (under the hull's mass)


def _platform(a):
    deck = a.part('Platform', 'Alloy')
    k.block(deck, (DECK_W, DECK_L, .1), loc=(0, CY, -.17), chamfer=.015)
    j = a.part('Platform_joints', 'Undercarriage')
    for i in range(1, 8):
        j.box((DECK_W - .1, .02, .008), loc=(0, CY - DECK_L / 2 + i * DECK_L / 8, -.118), bevel=0)
    rails = a.part('Platform_rails', 'Steel')
    clev = a.part('Tie_down_rings', 'Steel')
    for s in (-1, 1):
        rails.box((.08, DECK_L, .14), loc=(s * (DECK_W / 2 + .02), CY, -.15), bevel=0)
        a.part('Team_bands', 'Team').box((.01, 1.4, .08), loc=(s * (DECK_W / 2 + .065), CY, -.15), bevel=0)
        for i in range(9):
            y = CY - DECK_L / 2 + .35 + i * (DECK_L - .7) / 8
            clev.torus(.05, .012, loc=(s * (DECK_W / 2 + .07), y, -.07), rot=(0, R90, 0), seg=6, ring=3)
    for y in (CY - DECK_L / 2, CY + DECK_L / 2):
        k.block(rails, (DECK_W + .12, .06, .16), loc=(0, y, -.15), chamfer=.01)
    # Paper honeycomb stacks under the hull (the energy dissipaters), each with its strap.
    hc = a.part('Honeycomb', 'Crate')
    st = a.part('Kit_straps', 'Canvas')
    for x in (-.62, .62):
        for y in (-1.5, -.4, .7, 1.8, 2.75):
            k.block(hc, (.8, .7, .1), loc=(x, y, -.07), chamfer=.008)
            st.box((.82, .05, .015), loc=(x, y, -.015), bevel=0)


def _lashings(a):
    """Tie-down chains with load binders from the hull's sides to the rails; two ground-sensing probes."""
    ch = a.part('Tie_down_chains', 'Steel')
    lb = a.part('Load_binders', 'Armor')
    for s in (-1, 1):
        for y0, y1 in ((-1.5, -2.2), (-.3, -.7), (1.4, 1.9), (2.6, 3.3)):
            p0 = (s * 1.08, y0, .66)
            p1 = (s * (DECK_W / 2 + .06), y1, -.06)
            ch.tube([p0, p1], .018, seg=4)
            mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2)
            lb.box((.06, .06, .14), loc=mid, rot=(math.atan2(y1 - y0, .7) * .5, s * .6, 0), bevel=0)
    pr = a.part('Probes', 'Steel')
    for y in (CY - 2.6, CY + 2.6):
        pr.tube([(-1.2, y, -.22), (-1.2, y, -.95)], .02, seg=4)
        pr.cyl(.07, .03, loc=(-1.2, y, -.97), seg=8, bevel=0)


def _canopy(a, centre, tilt_dir):
    """One G-11: a thin shell (outer up, inner back down) with radial tapes, hem, Team band and vent, splayed out."""
    cx, cy = centre
    rot = K.rot_to((tilt_dir[0] * math.sin(SPLAY), tilt_dir[1] * math.sin(SPLAY), math.cos(SPLAY)))
    loc = (cx, cy, SKIRT_Z)
    R = CANOPY_R
    outer = [(R, 0), (R * .985, .4), (R * .9, .88), (R * .72, 1.32), (R * .45, 1.64), (R * .15, 1.78)]
    inner = [(r * .985 - .02, z - .03) for r, z in reversed(outer)]
    k.ring(a.part('Canopy', 'Canvas'), outer + inner, loc=loc, rot=rot, seg=16, worn=(2,))
    m = K.frame(loc, rot)
    tapes = a.part('Canopy_gores', 'Undercarriage')
    for i in range(8):
        u = i * TAU / 8 + TAU / 32
        c, s = math.cos(u), math.sin(u)
        tapes.tube([K._at(m, (c * r * 1.01, s * r * 1.01, z + .01)) for r, z in outer], .02, seg=3, caps=False)
    k.ring(a.part('Canopy_stripe', 'Team'), [(R * .9, .86), (R * .92, .86), (R * .82, 1.12), (R * .8, 1.12)],
           loc=loc, rot=rot, seg=16)
    k.ring(a.part('Canopy_stripe', 'Canvas'), [(R * .99, -.02), (R * 1.03, -.02), (R * 1.03, .1), (R * .99, .1)],
           loc=loc, rot=rot, seg=16)
    k.ring(a.part('Canopy_vent', 'Steel'), [(R * .12, 1.76), (R * .17, 1.76), (R * .17, 1.82), (R * .12, 1.82)],
           loc=loc, rot=rot, seg=10)
    # Suspension lines to the confluence clevis, then the riser extension to the release.
    conf = (cx * .42, cy * .42, 5.9)
    lines = a.part('Rigging', 'Undercarriage')
    for i in range(8):
        u = i * TAU / 8
        lines.tube([K._at(m, (math.cos(u) * R, math.sin(u) * R, .02)), conf], .018, seg=3, caps=False)
    lines.tube([conf, LINK], .045, seg=4)
    k.block(a.part('Clevises', 'Steel'), (.1, .1, .14), loc=conf, chamfer=.015)


def _rig(a):
    """Four slings from the hull's lifting eyes to the M-2 release, the release, four canopies."""
    sl = a.part('Slings', 'Canvas')
    for sx in (-1, 1):
        for y in (-1.6, 2.6):
            sl.tube([(sx * .95, y, .98), LINK], .04, seg=4)
            a.part('Clevises', 'Steel').torus(.06, .015, loc=(sx * .95, y, 1.0), rot=(R90, 0, 0), seg=8, ring=3)
    rel = a.part('Release', 'Armor')
    k.block(rel, (.3, .22, .36), loc=(LINK[0], LINK[1], LINK[2] + .15), chamfer=.03)
    a.part('Release_cover', 'Hazard').box((.2, .015, .14), loc=(LINK[0], LINK[1] - .118, LINK[2] + .2), bevel=0)
    k.lathe(a.part('Clevises', 'Steel'), [(0, -.12), (.12, -.08), (.12, .06), (0, .1)], loc=LINK, seg=8)
    for j in range(4):
        u = TAU / 8 + j * TAU / 4
        d = (math.cos(u), math.sin(u))
        _canopy(a, (d[0] * RING_R, d[1] * RING_R), d)


KEEP = re.compile(r'^(Hull|Tracks|Wheels|Tyres|Turret_body|Coax|Mantlet|Platform|Canopy|Canopy_stripe|Rigging)$')


def airborne_light_tank_chute(a, detail=False):
    """The airborne light tank under its parachutes: the ground model's builder plus the drop rig."""
    ALT.airborne_light_tank(a)
    _platform(a)
    _lashings(a)
    _rig(a)
    k.clean(a)
    AVC._merge_static(a, keep=KEEP)


BUILDERS = {
    'airborne_light_tank_chute': (airborne_light_tank_chute, dict(ao_distance=.5, grime_height=.55)),
}
