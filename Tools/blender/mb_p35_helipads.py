"""Prompt 35 wave 12 (lane C): the helipad family lifted with real heliport furniture (owner, DECISIONS "Prompt 35:
owner answers on REBUILD_REPORT section 8", item 5; specs Tools/blender/specs/helipad*.json).

Lane A's wave 2 builders (mb_p35_wave2_support: helipad, helipad_a's clamshell shelter, helipad_b's FARP) are kept
and run on this module's pad, which is lane A's pad with its paint fixed and its fittings made real; the footprint is
exactly the old 10 x 10 m (nothing reaches past x, y = +-5). Thin props stand above the flat pad (the lead allows
them):

- the pad (all three): the paint now sits 1 cm over the concrete and the tyre / soot stains below it, so the H and
  the ring are never blotted out (the wave 2 stains were drawn over the H); the flush TLOF lights in their steel rims,
  eight elevated green FATO perimeter lights on frangible stalks round the edge, the tie-down points as recessed cups
  with their rings, the drain grates;
- the windsock (ICAO pattern) at the rear right corner: the hinged frangible mast on its base plate, the swivel
  frame, the five-band orange / white sock streaming out, the red obstruction light on top;
- two floodlight posts at the front corners aimed at the pad (lamp heads, cable down);
- helipad: a hose-reel fuel cabinet and the fire extinguisher trolley by the cut corner;
- helipad_a: a towed fuel bowser (tank, frame, axle and wheels, the hose reel and the drawbar) parked at the front
  left, clear of the touchdown ring;
- helipad_b: its own FARP windsock (wave 2) replaced by the common one; the pump, bladders and arming point kept.

No runtime nodes (lane A's `helipad_*` had none). Metres, +Z up, -Y front, +X left.
"""
import contextlib
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_wave2_support as S
import mb_tower_branches as tb

R90 = math.pi / 2
TAU = math.tau
PADH = S.PADH
ZS = PADH + .004            # stains, joints (their top)
ZP = PADH + .012            # paint (its top: 8 mm over the stains, 1.2 cm over the concrete)
SKIP_LEFT = [False]         # helipad_b: its sandbag run stands on the +X edge, so no perimeter lights there


def _flat(part, w, d, loc_xy, top, rot=0.0, t=.006):
    part.box((w, d, t), loc=(loc_xy[0], loc_xy[1], top - t / 2), rot=(0, 0, rot), bevel=0)


def pad(a, apron=False):
    """Lane A's precast pad (kerb with the cut corner, slab joints, ring, H, edge stripes, arrows, number, Team bar)
    with the paint over the stains and the fittings made real."""
    k.extrude(a.part('Base', 'Concrete'), [(-5.0, -5.0), (5.0, -5.0), (5.0, 3.8), (3.8, 5.0), (-5.0, 5.0)], PADH,
              loc=(0, 0, PADH / 2), axis='Z', corner=.15, taper=(.97, .97), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-5, 6):
        _flat(j, 9.6, .04, (0, i * .9), ZS)
        _flat(j, .04, 9.6, (i * .9, 0), ZS)
    # Tyre scuffs and soot under the paint, off the H.
    st = a.part('Stains', 'Charred')
    for (x, y, w, r) in ((1.9, .9, 1.2, .5), (-2.1, -1.2, .9, 1.4), (2.7, -1.9, .6, .9), (-2.6, 2.1, .7, 2.1),
                         (.2, 2.0, 1.4, .1), (-.4, -2.1, 1.3, .2)):
        _flat(st, w, w * .35, (x, y), ZS - .001, rot=r)
    arr = a.part('Paint_yellow', 'Hazard')
    for dx in (-1.3, 1.3):
        _flat(arr, .25, 1.2, (dx, -4.2), ZP)
        for s_ in (-1, 1):
            _flat(arr, .2, .7, (dx + s_ * .22, -3.5), ZP, rot=s_ * .6)
    paint = a.part('Paint_white', 'PlasterWhite')
    for (x, y, w, d) in ((2.0, 3.9, .6, .15), (2.0, 4.25, .6, .15), (2.25, 4.08, .15, .5), (1.6, 4.08, .15, .5)):
        _flat(paint, w, d, (x, y), ZP)
    ring = [(math.cos(t) * 3.4, math.sin(t) * 3.4) for t in (i * TAU / 32 for i in range(32))]
    for i in range(32):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % 32]
        _flat(paint, math.hypot(x1 - x0, y1 - y0) + .02, .3, ((x0 + x1) / 2, (y0 + y1) / 2), ZP,
              rot=math.atan2(y1 - y0, x1 - x0))
    for sx in (-1, 1):
        _flat(paint, .45, 2.6, (sx * .9, 0), ZP)
    _flat(paint, 1.35, .45, (0, 0), ZP)
    edge = a.part('Paint_edge', 'Hazard')
    for s in (-1, 1):
        for i in range(5):
            f = -3.6 + i * 1.8
            _flat(edge, 1.0, .2, (f, s * 4.6), ZP)
            _flat(edge, .2, 1.0, (s * 4.6, f), ZP)
    _flat(a.part('Team_band', 'Team'), 2.4, .3, (0, -3.95), ZP + .002)
    # Flush TLOF lights in steel rims round the ring of paint.
    lights = a.part('Lamps', 'Lamp')
    rims = a.part('Lamp_rims', 'Steel')
    for i in range(16):
        t = i * TAU / 16
        x = max(-1, min(1, math.cos(t) * 1.42)) * 4.3
        y = max(-1, min(1, math.sin(t) * 1.42)) * 4.3
        rims.cyl(.09, .02, loc=(x, y, PADH + .006), seg=8, bevel=0)
        lights.cyl(.05, .02, loc=(x, y, PADH + .012), seg=6, bevel=0)
    # Elevated green FATO perimeter lights on frangible stalks round the edge.
    green = a.part('Perimeter_lights', 'SignalGreen')
    stalk = a.part('Lamp_rims', 'Steel')
    for (x, y) in ((4.82, -4.82), (0, -4.82), (-4.82, -4.82), (-4.82, 0), (-4.82, 4.82), (0, 4.82), (4.82, 0),
                   (4.82, 2.6)):
        if SKIP_LEFT[0] and x > 4:
            continue
        k.lathe(stalk, [(.07, 0), (.07, .03), (.025, .05), (.025, .26), (0, .26)], loc=(x, y, PADH), seg=8)
        k.lathe(green, [(.055, 0), (.055, .05), (.03, .1), (0, .11)], loc=(x, y, PADH + .26), seg=8)
    # Tie-down points: a dark recessed cup with its ring.
    cups = a.part('Tie_down_cups', 'Undercarriage')
    tie = a.part('Tie_downs', 'Steel')
    for (x, y) in ((2.2, 2.2), (-2.2, 2.2), (2.2, -2.2), (-2.2, -2.2), (0, 2.9), (0, -2.9)):
        cups.cyl(.14, .02, loc=(x, y, PADH + .006), seg=10, bevel=0)
        tie.torus(.09, .016, loc=(x, y, PADH + .02), rot=(.35, 0, 0), seg=8, ring=3)
    gr = a.part('Drain_grates', 'Undercarriage')
    for (x, y) in ((4.85, 0), (-4.85, 0), (0, 4.85)):
        _flat(gr, .12 if abs(x) > 1 else 1.2, 1.2 if abs(x) > 1 else .12, (x, y), ZS)


def _windsock(a, x=-4.55, y=4.55, wind=(.55, -.85)):
    """The ICAO windsock: hinged frangible mast on a base plate, swivel frame, five-band sock, obstruction light."""
    k.block(a.part('Base', 'Concrete'), (.5, .5, .12), loc=(x, y, PADH + .06), chamfer=.03)
    a.part('Windsock_pole', 'Steel').box((.3, .3, .02), loc=(x, y, PADH + .13), bevel=0)
    pole = a.part('Windsock_pole', 'Steel')
    H = 2.6
    k.lathe(pole, [(.05, 0), (.045, .25), (.04, .28), (.04, .32), (.035, .35), (.03, H), (0, H)],
            loc=(x, y, PADH + .14), seg=8)
    a.part('Windsock_pole', 'Steel').cyl(.05, .1, loc=(x, y, PADH + .44), rot=(0, R90, 0), seg=8, bevel=0)
    zt = PADH + .14 + H - .05
    yaw = math.atan2(wind[1], wind[0])
    # The swivel frame: a ring the sock's mouth hangs on, on an arm off the mast head.
    c, s = math.cos(yaw), math.sin(yaw)
    mouth = (x + c * .18, y + s * .18, zt - .1)
    fr = a.part('Windsock_pole', 'Steel')
    fr.tube([(x, y, zt), (mouth[0], mouth[1], zt)], .02, seg=4)
    fr.torus(.17, .015, loc=(mouth[0], mouth[1], zt - .1), rot=(R90, 0, yaw + R90), seg=12, ring=3)
    # The sock: five bands from the mouth, tapering and drooping a little, alternating orange and white.
    L, r0, r1, droop = 1.35, .17, .08, .25
    for i in range(5):
        f0, f1 = i / 5, (i + 1) / 5
        mat = 'BarrelRed' if i % 2 == 0 else 'PlasterWhite'
        prof = [(r0 + (r1 - r0) * f0, f0 * L), (r0 + (r1 - r0) * f1, f1 * L)]
        lean = math.atan2(droop, L)
        k.lathe(a.part('Windsock', mat), prof, loc=(mouth[0], mouth[1], mouth[2]),
                rot=(R90 + lean, 0, yaw + R90), seg=10, caps=(False, False))
    a.part('Obstruction_light', 'LavaGlow').sphere(.055, loc=(x, y, zt + .1), seg=8, rings=5)


def _posts(a):
    """Two floodlight posts at the front corners aimed at the pad's middle."""
    for sx in (-1, 1):
        x, y = sx * 4.5, -4.45
        k.block(a.part('Base', 'Concrete'), (.36, .36, .1), loc=(x, y, PADH + .05), chamfer=.025)
        K.floodlight(a, (x, y + .1, PADH + .1), facing=(-sx * .5, .6, -.55), pole=2.9)
        a.part('Light_housing', 'Armor').box((.16, .1, .26), loc=(x, y + .09, PADH + .55), bevel=0)


def _cabinet(a):
    """helipad: the hose-reel fuel cabinet and the extinguisher trolley by the cut corner."""
    x, y = 4.3, 3.0
    cab = a.part('Fuel_cabinet', 'Team')
    k.block(cab, (.55, 1.0, 1.1), loc=(x, y, PADH + .55), chamfer=.03)
    a.part('Fuel_cabinet_door', 'Armor').box((.02, .8, .9), loc=(x - .285, y, PADH + .58), bevel=0)
    a.part('Hose_reels', 'BarrelRed').cyl(.3, .22, loc=(x - .32, y, PADH + .7), rot=(0, R90, 0), seg=12, bevel=0)
    a.part('Hose_reels', 'Steel').cyl(.08, .26, loc=(x - .32, y, PADH + .7), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Hoses', 'Rubber').tube([(x - .4, y - .2, PADH + .55), (x - .7, y - .5, PADH + .03),
                                    (x - 1.3, y - .6, PADH + .03)], .03, seg=5)
    a.part('Hoses', 'Steel').cyl(.035, .2, loc=(x - 1.4, y - .6, PADH + .04), rot=(0, R90, 0), seg=6, bevel=0)
    a.part('Cabinet_sign', 'PlasterWhite').box((.01, .3, .14), loc=(x - .29, y - .1, PADH + 1.0), bevel=0)
    ex, ey = 3.5, 4.0
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.17, 0), (.17, .7), (.1, .8), (0, .84)], loc=(ex, ey, PADH + .12),
            seg=10, worn=(1,))
    for sx in (-1, 1):
        a.part('Cart_wheels', 'Rubber').cyl(.13, .05, loc=(ex + sx * .22, ey, PADH + .13), rot=(0, R90, 0), seg=8,
                                            bevel=0)
    a.part('Cart_frame', 'Steel').tube([(ex, ey + .2, PADH + .13), (ex, ey + .25, PADH + 1.0)], .015, seg=4)


def _bowser(a):
    """helipad_a: a towed aviation-fuel bowser parked at the front left, clear of the ring."""
    x, y = 4.05, -2.75
    fr = a.part('Bowser_frame', 'Steel')
    for s in (-1, 1):
        fr.box((.06, 2.2, .1), loc=(x + s * .45, y, PADH + .42), bevel=0)
    k.lathe(a.part('Bowser_tank', 'Fuel'), [(0, -1.0), (.42, -.98), (.5, -.9), (.5, .9), (.42, .98), (0, 1.0)],
            loc=(x, y, PADH + .95), rot=K.BACKWARD, seg=14, worn=(1, 4))
    for f in (-.55, .55):
        a.part('Bowser_bands', 'Team').cyl(.51, .08, loc=(x, y + f, PADH + .95), rot=K.BACKWARD, seg=14, bevel=0)
    a.part('Bowser_frame', 'Steel').cyl(.15, .06, loc=(x, y + .2, PADH + 1.46), seg=10, bevel=0)
    a.part('Bowser_frame', 'Steel').tube([(x - .2, y - .5, PADH + 1.46), (x - .2, y + .7, PADH + 1.46)], .015, seg=4)
    ax = a.part('Axles', 'Undercarriage')
    ax.cyl(.05, 1.0, loc=(x, y + .3, PADH + .3), rot=(0, R90, 0), seg=8, bevel=0)
    for s in (-1, 1):
        K.tread_wheel(a, (x + s * .55, y + .3, PADH + .3), .3, .18, s, seg=12)
        a.part('Light_housing', 'Armor').box((.22, .7, .03), loc=(x + s * .55, y + .3, PADH + .64), bevel=0)
    a.part('Bowser_frame', 'Steel').tube([(x - .3, y - 1.05, PADH + .42), (x, y - 1.6, PADH + .3),
                                     (x + .3, y - 1.05, PADH + .42)], .03, seg=4)
    a.part('Bowser_frame', 'Steel').cyl(.07, .05, loc=(x, y - 1.62, PADH + .3), seg=8, bevel=0)
    a.part('Hose_reels', 'BarrelRed').cyl(.25, .2, loc=(x - .45, y + .95, PADH + .7), rot=(0, R90, 0), seg=12,
                                          bevel=0)
    a.part('Hoses', 'Rubber').tube([(x - .55, y + .95, PADH + .5), (x - .9, y + .7, PADH + .03),
                                    (x - 1.4, y + .3, PADH + .03)], .03, seg=5)
    a.part('Paint_yellow', 'Hazard').box((.01, .5, .2), loc=(x - .505, y - .3, PADH + .95), bevel=0)
    a.part('Obstruction_light', 'LavaGlow').box((.05, .02, .04), loc=(x - .4, y + 1.1, PADH + .45), bevel=0)
    a.part('Obstruction_light', 'LavaGlow').box((.05, .02, .04), loc=(x + .4, y + 1.1, PADH + .45), bevel=0)


@contextlib.contextmanager
def _our_pad():
    """Run lane A's builder on this module's pad (its `pad` is looked up in its module at call time)."""
    old = S.pad
    S.pad = pad
    try:
        yield
    finally:
        S.pad = old


def helipad(a, detail=False):
    with _our_pad():
        S.helipad(a)
    _windsock(a)
    _posts(a)
    _cabinet(a)
    k.clean(a)


def helipad_a(a, detail=False):
    with _our_pad():
        S.helipad_a(a)
    _windsock(a, x=4.55, y=1.3, wind=(-.55, -.85))         # the shelter fills the rear right corner
    _posts(a)
    _bowser(a)
    k.clean(a)


def helipad_b(a, detail=False):
    SKIP_LEFT[0] = True
    try:
        with _our_pad():
            S.helipad_b(a)
    finally:
        SKIP_LEFT[0] = False
    tb.strip(a, ('Windsock_pole', 'Windsock'))
    _windsock(a)
    _posts(a)
    k.clean(a)


BUILDERS = {
    'helipad': (helipad, dict(ao_distance=.4, grime_height=.1, ao_strength=.5)),
    'helipad_a': (helipad_a, dict(ao_distance=.6, grime_height=.2, ao_strength=.55)),
    'helipad_b': (helipad_b, dict(ao_distance=.5, grime_height=.15, ao_strength=.55)),
}
