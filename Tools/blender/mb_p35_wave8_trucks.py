"""Prompt 35 wave 8 (lane A): the wheeled vehicles rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library. DECISIONS "Prompt 35 wave 8 (lane A)". No body, cab, turret
or weapon of one is drawn by another's function; the lean helpers below only lay out wheels, axles and frame rails
from each builder's own numbers.

- mlrs: M142 HIMARS (sheet: 0.8 x the real truck): FMTV 6x6 with the armoured LSAC cab, the launcher module on its
  turntable carrying ONE six-round pod (2 x 3 tube mouths with frangible caps), the boom cradle and elevation rams,
  the exhaust stack behind the cab, the folded stabiliser jacks; the 12.7 mm on the cab's hatch ring.
- grad_truck (elite_grad's model): BM-21 Grad: Ural-375 6x6 with the long bonnet, the open cab under its canvas top,
  the 40-tube pack (4 x 10) on its traversing mount, the rear jacks and the 12.7 mm on a pedestal behind the cab.
- command_vehicle: M1130 Stryker CV: the 8x8 hull with its sloped bow, the commander's station, the folded telescopic
  mast along the roof, a row of whip antennas, the tent rolled on the rear, the 12.7 mm RWS-style mount.
- railgun_truck: an 8x8 heavy truck carrying a twin-rail electromagnetic gun of its own (no longer Ixion's
  stand-in): the rails between insulator bands, the capacitor banks and radiators with their glow, the breech and
  its loader, the elevation rams; the armoured cab ahead.
- radar_scout: a 4x4 scout car with a telescopic sensor mast (radar head and EO lens) and the 12.7 mm turret.
- heavy_aa: Pantsir-S1 on the KamAZ 8x8: the turret with the twin 30 mm each side and the 12-tube missile packs,
  the search radar on top (`Radar`), the tracking radar in front, the crew cab.
- wheeled_gun: Centauro II: an 8x8 hull with the 120 mm turret (muzzle brake, thermal sleeve, fume extractor), the
  commander's sight, smoke banks and the 12.7 mm on its post.

Runtime nodes are the old models' (positions within a few centimetres of the old pivots): see each builder.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= lean shared layout helpers
def _wheels(a, axles, r, w, hx, seg=12, nuts=4, springs=True, frame_z=None, diff_rear=True):
    """Wheels on every axle at |x| = hx, the beam axles with their differentials, leaf springs (trucks) and the
    dust round each wheel."""
    for i, y in enumerate(axles):
        for s in (-1, 1):
            K.tread_wheel(a, (s * hx, y, r), r, w, s, seg=seg, nuts=nuts)
            K.dust(a, (s * hx, y, .15), radius=r * 1.3, k=.22)
        K.axle(a.part('Axles', 'Undercarriage'), y, r, hx - w / 2, r=.07, diff=diff_rear or i == 0)
        if springs:
            for s in (-1, 1):
                K.leaf_spring(a.part('Suspension', 'Steel'), s * (hx - w / 2 - .12), y, r + .2, r * 2.2, leaves=3)


def _rails(a, y0, y1, z, x, h=.24, w=.12, part='Chassis', mat='Undercarriage', cross=()):
    """The ladder frame: two C-section rails and the cross members at `cross` (y's)."""
    ch = a.part(part, mat)
    for s in (-1, 1):
        k.extrude(ch, [(s * x - w / 2, -h / 2), (s * x + w / 2, -h / 2), (s * x + w / 2, h / 2),
                       (s * x - w / 2, h / 2)], y1 - y0, loc=(0, (y0 + y1) / 2, z), rot=(R90, 0, 0), axis='Z')
    for y in cross:
        ch.box((2 * x, .08, h * .7), loc=(0, y, z), bevel=0)
    return ch


def _fender(a, y0, y1, x, z, w=.42, part='Fenders', mat='Team'):
    """A mudguard over a wheel pair on both sides: the top sheet, the outer lip, the mud flap behind."""
    fen = a.part(part, mat)
    for s in (-1, 1):
        fen.box((w, y1 - y0, .04), loc=(s * x, (y0 + y1) / 2, z), bevel=0)
        fen.box((.04, y1 - y0, .16), loc=(s * (x + w / 2), (y0 + y1) / 2, z - .07), bevel=0)


# ============================================================================= mlrs (M142 HIMARS)
def mlrs(a):
    """See the module docstring. Runtime: Turret (the module's yaw pivot on the bed), Muzzle_main (centre of the
    pod face), Mount_mg / Muzzle_mg (the cab-roof gun), Point_fire, Point_exhaust; launch face `Tubes_bore`."""
    R, WD, HX = .45, .32, .79
    _wheels(a, (-1.95, 1.2, 2.3), R, WD, HX, nuts=0)
    _rails(a, -2.75, 2.95, .78, .42, cross=(-2.2, -.9, .4, 1.75, 2.85))
    # Fenders: front pair with the step, the rear tandem's flat guards; mud flaps behind the tandem.
    _fender(a, -2.4, -1.5, HX, 1.0)
    for s in (-1, 1):
        a.part('Fenders', 'Team').box((.44, 1.95, .04), loc=(s * HX, 1.75, 1.0), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.36, .02, .34), loc=(s * HX, 2.8, .72), bevel=0)
        K.lamp(a, (s * .78, 3.0, .92), (0, 1, 0), r=.05, guard=False, glow='LavaGlow')
        a.part('Steps', 'Steel').box((.24, .3, .03), loc=(s * .9, -1.35, .62), bevel=0)
        a.part('Steps', 'Steel').box((.24, .3, .03), loc=(s * .9, -1.35, .88), bevel=0)
    a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .06), loc=(.6, 3.03, .98), bevel=0)
    _mlrs_cab(a)
    _mlrs_bed(a)
    _mlrs_module(a)
    a.pivot('Point_fire', (0, 1.0, 1.94))
    a.pivot('Point_exhaust', (.76, -1.15, 2.1))
    k.clean(a)


def _mlrs_cab(a):
    """The armoured LSAC cab: the faceted body with the flat two-pane windscreen in thick frames, the doors with
    their small armoured windows, the bumper, grille and lamps, the roof hatch ring carrying the 12.7 mm."""
    y0, y1 = -2.99, -1.3
    cab = a.part('Body', 'Team')
    k.sharp_loft(cab, [[(-.98, y0 + .05, .72), (.98, y0 + .05, .72), (.98, y1, .72), (-.98, y1, .72)],
                       [(-.98, y0, 1.25), (.98, y0, 1.25), (.98, y1, 1.25), (-.98, y1, 1.25)],
                       [(-.8, y0 + .42, 1.85), (.8, y0 + .42, 1.85), (.8, y1, 1.86), (-.8, y1, 1.86)]],
                 chamfer=.04)
    a.part('Armor', 'Armor').box((1.5, 1.25, .05), loc=(0, (y0 + .42 + y1) / 2, 1.875), bevel=0)   # roof plate
    K.windscreen(a, [(.86, y0 + .04, 1.3), (.02, y0 + .04, 1.3), (.02, y0 + .38, 1.8), (.86, y0 + .38, 1.8)],
                 frame_mat='Armor', wipers=1, bar=.06)
    K.windscreen(a, [(-.02, y0 + .04, 1.3), (-.86, y0 + .04, 1.3), (-.86, y0 + .38, 1.8), (-.02, y0 + .38, 1.8)],
                 frame_mat='Armor', wipers=1, bar=.06)
    for s in (-1, 1):
        a.part('Glass', 'Glass').box((.02, .42, .32), loc=(s * .985, -2.25, 1.5), bevel=0)
        a.part('Armor', 'Armor').box((.03, .5, .4), loc=(s * .99, -2.25, 1.5), bevel=0)   # window frames
        a.part('Door_lines', 'Armor').box((.02, .03, .95), loc=(s * .985, -1.65, 1.28), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * .995, -1.85, 1.3), (s * .995, -1.7, 1.3), (s, 0, 0), h=.04)
        K.mirror(a.part('Mirrors', 'Steel'), (s * .92, -2.85, 1.6), s, arm=.05)
        K.lamp(a, (s * .72, y0 - .005, .95), (0, -1, 0), r=.07, guard=True)
        a.part('Light_rims', 'Armor').box((.2, .03, .16), loc=(s * .72, y0 + .005, .95), bevel=0)
    K.grille(a, (0, y0 - .005, 1.0), .9, .32, facing=(0, -1, 0), slats=5, frame_mat='Armor')
    a.part('Bumper', 'Armor').box((2.0, .16, .22), loc=(0, y0 - .02, .72), bevel=0)
    for x in (-.55, .55):
        K.tow_hook(a.part('Kit_tow', 'Steel'), (x, y0 - .1, .7), facing=(0, -1, 0), size=.09)
    # The hatch ring on the right of the roof with the gun on its short post (roof-gun rule).
    k.ring(a.part('Hatch_ring', 'Armor'), [(.3, 0), (.36, 0), (.36, .07), (.3, .07)], loc=(.4, -2.1, 1.88), seg=12)
    K.pintle_mg(a, None, (.4, -2.1, 1.9), length=.7, post=.1, shield=True)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.65, -1.45, 1.88), h=.85, lean=.05)
    K.blade_antenna(a.part('Antennas', 'Steel'), (-.4, -1.6, 1.9), h=.18)


def _mlrs_bed(a):
    """Behind the cab: the power pack's exhaust stack and air intake, the fuel tank and battery box between the
    axles, the flat bed round the module, the folded stabiliser jacks at the rear corners, tool boxes."""
    stack = a.part('Exhaust', 'Steel')
    k.lathe(stack, [(.06, 0), (.06, .9), (.075, .92), (.075, 1.0)], loc=(.76, -1.15, 1.1), seg=8)
    a.part('Exhaust_shield', 'Armor').box((.18, .06, .6), loc=(.76, -1.06, 1.6), bevel=0)
    K.soot(a, (.76, -1.15, 2.1), radius=.3, k=.5)
    K.chamfer_box(a.part('Intake', 'Armor'), (.3, .4, .7), loc=(-.72, -1.1, 1.3), c=.03)
    K.grille(a, (-.72, -1.31, 1.4), .24, .3, facing=(0, -1, 0), slats=4, frame_mat='Armor')
    a.part('Tanks', 'Armor').cyl(.22, 1.0, loc=(-.72, -.45, .62), rot=K.FORWARD, seg=12, bevel=.02)
    a.part('Kit_straps', 'Steel').box((.48, .04, .48), loc=(-.72, -.7, .62), bevel=0)
    a.part('Kit_straps', 'Steel').box((.48, .04, .48), loc=(-.72, -.2, .62), bevel=0)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.34, .8, .34), (.74, -.45, .66), bands=1)
    bed = a.part('Bed', 'Armor')
    bed.box((1.9, 4.3, .1), loc=(0, .85, .96), bevel=0)
    for s in (-1, 1):
        a.part('Bed_rails', 'Steel').box((.05, 4.3, .08), loc=(s * .96, .85, 1.02), bevel=0)
        # Stabiliser jacks folded up at the rear corners: the leg in its sleeve, the pad.
        K.outrigger(a.part('Jacks', 'Armor'), a.part('Jack_pads', 'Steel'), (s * .6, 2.85, .85), s, reach=.12,
                    drop=.5, w=.14)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.5, .32, .3), (0, -1.05, 1.16), bands=1)


def _mlrs_module(a):
    """The launcher module on the Turret pivot: the turntable, the module base with its cable ducts, the boom cradle
    hinged at the rear, the elevation rams, and the six-round pod in its cage (Pod, Pod_frame): the face with six
    tube mouths in 2 x 3 (Tubes rings, Tubes_bore), frangible caps on four, the lifting points and the end frames."""
    t = a.pivot('Turret', (0, 1.55, 1.06))
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.62, 0), (.66, .02), (.66, .1), (.6, .12)], seg=16)
    base = a.part('Turret_armor', 'Armor', t)
    K.chamfer_box(base, (1.5, 1.4, .34), loc=(0, .2, .3), c=.04)
    a.part('Cable_ducts', 'Undercarriage', t).box((.12, 1.3, .1), loc=(.62, .2, .5), bevel=0)
    a.part('Cable_ducts', 'Undercarriage', t).tube([(.62, -.45, .5), (.5, -.6, .62), (.42, -.6, .8)], .03, seg=5)
    # Cradle and rams: a hinge at the rear, two rams under the front of the cage.
    cr = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        cr.box((.1, 3.2, .1), loc=(s * .6, -.35, .6), bevel=0)
        cr.cyl(.07, .18, loc=(s * .6, 1.2, .6), rot=(0, R90, 0), seg=8, bevel=0)
        a.part('Rams', 'Steel', t).tube([(s * .45, -.9, .48), (s * .45, -1.15, .72)], .055, seg=8)
        a.part('Rams', 'Undercarriage', t).tube([(s * .45, -1.0, .58), (s * .45, -1.22, .8)], .035, seg=6)
    # The pod in its cage: the box, the cage's end frames and the corner posts, the face of tubes.
    y0, y1, zc = -2.25, 1.55, 1.17     # pod front / rear (pivot frame), centre height
    pod = a.part('Pod', 'Team', t)
    K.chamfer_box(pod, (1.18, y1 - y0, .78), loc=(0, (y0 + y1) / 2, zc), c=.04)
    fr = a.part('Pod_frame', 'Armor', t)
    for y in (y0 + .06, y0 + 1.3, y1 - 1.3, y1 - .06):
        fr.box((1.32, .1, .9), loc=(0, y, zc), bevel=0) if y in (y0 + .06, y1 - .06) else \
            fr.box((1.26, .06, .84), loc=(0, y, zc), bevel=0)
    for s in (-1, 1):
        for zz in (-1, 1):
            fr.box((.07, y1 - y0, .07), loc=(s * .62, (y0 + y1) / 2, zc + zz * .42), bevel=0)
    face = y0 - .01
    tubes = a.part('Tubes', 'Steel', t)
    bore = a.part('Tubes_bore', 'Undercarriage', t)
    caps = a.part('Tube_caps', 'Canvas', t)
    for i, x in enumerate((-.38, 0, .38)):
        for j, z in enumerate((zc - .18, zc + .18)):
            k.ring(tubes, [(.14, 0), (.16, 0), (.16, .05), (.14, .05)], loc=(x, face, z), rot=K.FORWARD, seg=10)
            bore.cyl(.14, .02, loc=(x, face + .015, z), rot=K.FORWARD, seg=10, bevel=0)
            if (i + j) % 3:
                caps.cyl(.13, .02, loc=(x, face - .02, z), rot=K.FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_main', (0, -2.25, 1.17), t)
    # Lifting points, latches and the stencil band on the pod's sides; the team bands on the cage.
    for s in (-1, 1):
        for y in (y0 + .5,):
            K.handle(a.part('Kit_handles', 'Steel', t), (s * .6, y - .08, zc + .4), (s * .6, y + .08, zc + .4),
                     (0, 0, 1), h=.05)
        a.part('Team_band', 'Team', t).box((.012, 1.6, .14), loc=(s * .6, (y0 + y1) / 2, zc + .1), bevel=0)
        for y in (y0 + .9, y1 - .9):
            a.part('Kit_latches', 'Steel', t).box((.02, .1, .06), loc=(s * .6, y, zc - .3), bevel=0)
    K.bolt_ring(a.part('Kit_bolts', 'Steel', t), (0, 0, .12), (0, 0, 1), .55, 8)


# ============================================================================= grad_truck (BM-21 Grad)
def grad_truck(a):
    """See the module docstring. Runtime: Turret (the launcher's yaw pivot over the rear tandem), Muzzle_main (the
    centre of the tube face), Mount_mg / Muzzle_mg (the pedestal gun behind the cab); launch face
    `Rocket_tubes_face`."""
    R, WD, HX = .55, .38, 1.0
    _wheels(a, (-2.95, 1.05, 2.45), R, WD, HX, nuts=0, diff_rear=False)
    _rails(a, -3.6, 3.5, .95, .48, cross=(-3.3, -2.0, -.6, .6, 1.75, 3.3))
    # Wings over the front wheels (the Ural's rounded mudguards), flat guards over the tandem, mud flaps, steps.
    fen = a.part('Fenders', 'Team')
    for s in (-1, 1):
        k.extrude(fen, [(-.6, 0), (-.45, .3), (.45, .3), (.65, 0), (.6, -.04), (-.6, -.04)], .5,
                  loc=(s * HX, -2.95, 1.22), axis='X', chamfer=.02)
        fen.box((.5, 2.2, .04), loc=(s * HX, 1.75, 1.25), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.42, .02, .42), loc=(s * HX, 2.95, .9), bevel=0)
        a.part('Steps', 'Steel').box((.3, .34, .03), loc=(s * 1.0, -1.95, .72), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .07), loc=(s * .95, 3.57, 1.05), bevel=0)
        a.part('Marker_lights', 'Alloy').box((.06, .03, .05), loc=(s * 1.18, 3.4, 1.28), bevel=0)
    a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .06), loc=(-.95, 3.57, 1.18), bevel=0)
    _grad_cab(a)
    _grad_bed(a)
    _grad_pack(a)
    a.pivot('Point_fire', (0, 1.2, 2.0))
    a.pivot('Point_exhaust', (-1.05, -1.45, 1.2))
    k.clean(a)


def _grad_cab(a):
    """The Ural-375's long bonnet with its louvred sides and the vertical radiator grille, the bumper with the
    winch and tow hooks, headlamps on the wings, the open cab with the folding windscreen and the canvas top, the
    pedestal 12.7 mm behind it, the whip antenna."""
    hood = a.part('Body', 'Team')
    k.sharp_loft(hood, [[(-.62, -3.72, .95), (.62, -3.72, .95), (.62, -2.45, .95), (-.62, -2.45, .95)],
                        [(-.62, -3.75, 1.5), (.62, -3.75, 1.5), (.66, -2.45, 1.62), (-.66, -2.45, 1.62)],
                        [(-.48, -3.68, 1.72), (.48, -3.68, 1.72), (.55, -2.45, 1.82), (-.55, -2.45, 1.82)]],
                 chamfer=.04)
    K.grille(a, (0, -3.765, 1.25), .9, .5, facing=(0, -1, 0), slats=7, frame_mat='Armor')
    for s in (-1, 1):
        for i in range(4):
            a.part('Louvres', 'Armor').box((.012, .08, .2), loc=(s * .64, -3.3 + i * .16, 1.3), rot=(0, 0, .3),
                                           bevel=0)
        K.lamp(a, (s * .9, -3.42, 1.42), (0, -1, 0), r=.09, guard=False)
    a.part('Bumper', 'Armor').box((2.3, .2, .24), loc=(0, -3.8, .95), bevel=0)
    k.lathe(a.part('Winch', 'Steel'), [(.12, -.35), (.12, .35)], loc=(0, -3.86, .82), rot=(0, R90, 0), seg=10)
    for x in (-.8, .8):
        K.tow_hook(a.part('Kit_tow', 'Steel'), (x, -3.9, .92), facing=(0, -1, 0), size=.1)
    # The cab: lower body and doors, the open upper with the windscreen frame and the canvas top on its bows.
    cab = a.part('Body', 'Team')
    K.chamfer_box(cab, (2.2, 1.15, .75), loc=(0, -1.95, 1.55), c=.04)
    K.windscreen(a, [(1.0, -2.5, 1.95), (-1.0, -2.5, 1.95), (-.98, -2.42, 2.45), (.98, -2.42, 2.45)],
                 frame_mat='Armor', wipers=2, bar=.05)
    top = a.part('Canvas_top', 'Canvas')
    k.sharp_loft(top, [[(-1.08, -2.4, 1.92), (1.08, -2.4, 1.92), (1.08, -1.4, 1.92), (-1.08, -1.4, 1.92)],
                       [(-1.06, -2.4, 2.4), (1.06, -2.4, 2.4), (1.06, -1.4, 2.4), (-1.06, -1.4, 2.4)],
                       [(-.9, -2.38, 2.52), (.9, -2.38, 2.52), (.9, -1.42, 2.52), (-.9, -1.42, 2.52)]],
                 chamfer=.06)
    bows = a.part('Canvas_bows', 'Steel')
    for y in (-2.1, -1.75):
        bows.box((2.12, .03, .03), loc=(0, y, 2.53), bevel=0)
    for s in (-1, 1):
        a.part('Windows', 'Glass').box((.02, .55, .35), loc=(s * 1.09, -2.0, 2.15), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.11, -1.75, 1.6), (s * 1.11, -1.6, 1.6), (s, 0, 0), h=.04)
        K.mirror(a.part('Mirrors', 'Steel'), (s * 1.12, -2.45, 2.05), s, arm=.08)
        a.part('Door_lines', 'Armor').box((.02, .03, .7), loc=(s * 1.105, -1.5, 1.55), bevel=0)
        a.part('Canvas_ties', 'Undercarriage').box((.02, .02, .3), loc=(s * 1.085, -2.2, 2.25), bevel=0)
    # The pedestal gun behind the cab (a 12.7 mm on its post), the antenna on the cab corner.
    a.part('Pedestal', 'Armor').box((.5, .5, .06), loc=(.5, -1.6, 2.33), bevel=0)
    K.pintle_mg(a, None, (.5, -1.6, 2.36), length=.74, post=.22, shield=True)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.95, -1.5, 2.5), h=1.1, lean=.04)


def _grad_bed(a):
    """The bed under the launcher: the platform, the fuel tank and the tool box on the frame, the exhaust under
    the cab, the rear jacks (rams and pads), the spare wheel behind the cab, ammunition crates."""
    a.part('Bed', 'Armor').box((2.3, 4.6, .1), loc=(0, 1.15, 1.15), bevel=0)
    for s in (-1, 1):
        a.part('Bed_rails', 'Steel').box((.05, 4.6, .08), loc=(s * 1.15, 1.15, 1.2), bevel=0)
        a.part('Jacks', 'Armor').box((.16, .16, .55), loc=(s * .85, 3.35, .82), bevel=0)
        a.part('Jack_rams', 'Steel').cyl(.05, .4, loc=(s * .85, 3.35, .42), seg=8, bevel=0)
        k.block(a.part('Jack_pads', 'Steel'), (.3, .3, .05), loc=(s * .85, 3.35, .2), chamfer=.015)
    a.part('Tanks', 'Armor').cyl(.26, 1.1, loc=(1.0, -.55, .82), rot=K.FORWARD, seg=12, bevel=.02)
    a.part('Kit_straps', 'Steel').box((.56, .04, .56), loc=(1.0, -.8, .82), bevel=0)
    a.part('Kit_straps', 'Steel').box((.56, .04, .56), loc=(1.0, -.3, .82), bevel=0)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.38, .8, .38), (-1.0, -.55, .85), bands=1)
    K.exhaust(a, (-1.05, -1.45, .8), r=.06, length=.4, direction=(0, 0, 1))
    K.soot(a, (-1.05, -1.45, 1.2), radius=.3, k=.4)
    K.crate(a.part('Stowage', 'Crate'), a.part('Kit_latches', 'Steel'), (.45, .6, .3), (.85, -.55, 1.36), bands=2)


def _grad_pack(a):
    """The launcher on the Turret pivot: the traverse ring, the cradle with its trunnions and elevating screw, the
    40-tube pack (4 rows of 10) in its three frame bands, the firing cables along the top, the sight box; the
    travel rest under the front of the pack."""
    t = a.pivot('Turret', (0, 2.25, 1.27))
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.7, 0), (.74, .02), (.74, .12), (.68, .14)], seg=16)
    K.bolt_ring(a.part('Kit_bolts', 'Steel', t), (0, 0, .14), (0, 0, 1), .62, 6)
    arm = a.part('Turret_armor', 'Armor', t)
    K.chamfer_box(arm, (1.3, 1.1, .3), loc=(0, 0, .3), c=.04)
    for s in (-1, 1):
        k.extrude(arm, [(-.5, 0), (.5, 0), (.25, .55), (-.25, .55)], .08, loc=(s * .6, 0, .45), axis='X')
        a.part('Turret_steel', 'Steel', t).cyl(.09, .14, loc=(s * .66, .15, .95), rot=(0, R90, 0), seg=8,
                                               bevel=0)
    a.part('Elevating_screw', 'Steel', t).tube([(0, -.4, .45), (0, -.85, .78)], .05, seg=8)
    y0, y1, zc = -2.73, .32, 1.2          # pack front / rear (pivot frame), centre height
    tubes = a.part('Rocket_tubes', 'Undercarriage', t)
    face = a.part('Rocket_tubes_face', 'Steel', t)
    for i in range(10):
        x = -.94 + i * .209
        for j in range(4):
            z = zc - .3 + j * .2
            if i in (0, 9) or j in (0, 3):     # the inner tubes are hidden by the outer ones and the bands
                tubes.cyl(.075, y1 - y0, loc=(x, (y0 + y1) / 2, z), rot=K.FORWARD, seg=6, bevel=0)
            face.cyl(.068, .04, loc=(x, y0 - .01, z), rot=K.FORWARD, seg=6, bevel=0)
    fr = a.part('Rocket_tubes_frame', 'Team', t)
    for y in (y0 + .15, (y0 + y1) / 2, y1 - .15):
        k.extrude(fr, [(-1.1, zc - .45), (1.1, zc - .45), (1.1, zc + .45), (-1.1, zc + .45)], .12,
                  loc=(0, y, 0), axis='Y', chamfer=.02)
    for s in (-1, 1):
        fr.box((.06, y1 - y0, .06), loc=(s * 1.08, (y0 + y1) / 2, zc - .42), bevel=0)
    cab = a.part('Rocket_tubes_cables', 'Rubber', t)
    for x in (-.6, 0, .6):
        cab.tube([(x, y1 - .1, zc + .46), (x, (y0 + y1) / 2, zc + .5), (x, y0 + .3, zc + .46)], .025, seg=5)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.22, .3, .25), loc=(-1.2, -.3, .9), c=.02)
    a.part('Glass', 'Glass', t).box((.15, .01, .1), loc=(-1.2, -.455, .95), bevel=0)
    a.pivot('Muzzle_main', (0, -2.73, 1.2), t)
    a.part('Team_band', 'Team', t).box((2.0, .5, .012), loc=(0, -1.6, zc + .46), bevel=0)
    rest = a.part('Rest_pad', 'Steel')
    for s in (-1, 1):
        rest.tube([(s * .5, -.35, 1.2), (0, -.35, 1.95)], .04, seg=6)
    rest.box((.5, .2, .06), loc=(0, -.35, 1.97), bevel=0)


# ============================================================================= command_vehicle (M1130 Stryker CV)
def command_vehicle(a):
    """See the module docstring. Runtime: Mount_mg / Muzzle_mg (the commander's 12.7 mm on its riser),
    Point_fire, Point_exhaust."""
    R, WD, HX = .38, .3, .82
    for i, y in enumerate((-1.95, -.85, .6, 1.7)):
        for s in (-1, 1):
            K.tread_wheel(a, (s * HX, y, R), R, WD, s, seg=12, nuts=0)
            K.dust(a, (s * HX, y, .12), radius=.5, k=.22)
        a.part('Undercarriage', 'Undercarriage').box((2 * HX - .3, .12, .12), loc=(0, y, R), bevel=0)
        for s in (-1, 1):
            a.part('Undercarriage', 'Undercarriage').tube([(s * (HX - .2), y, R), (s * .45, y - .25, R + .25)], .045,
                                                          seg=5)
    hull = a.part('Hull', 'Team')
    k.sharp_loft(hull, [[(-.62, -2.45, .42), (.62, -2.45, .42), (.62, 2.7, .42), (-.62, 2.7, .42)],
                        [(-.98, -2.78, .78), (.98, -2.78, .78), (.98, 2.82, .78), (-.98, 2.82, .78)],
                        [(-.98, -2.6, 1.0), (.98, -2.6, 1.0), (.98, 2.84, 1.02), (-.98, 2.84, 1.02)],
                        [(-.84, -1.95, 1.4), (.84, -1.95, 1.4), (.86, 2.8, 1.42), (-.86, 2.8, 1.42)]],
                 chamfer=.04)
    # Add-on armour panels on the sides (bolted), the rear ramp outline, the bow's trim plate.
    arm = a.part('Armor', 'Armor')
    for s in (-1, 1):
        for i, y in enumerate((-1.75, -.65, .45, 1.55, 2.4)):
            K.chamfer_box(arm, (.04, 1.0 if i < 4 else .6, .3), loc=(s * .995, y + (.0 if i < 4 else -.1), .92),
                          c=.01)
        K.rivet_line(a.part('Kit_bolts', 'Steel'), (s * 1.02, -2.2, 1.04), (s * 1.02, 2.6, 1.04), (s, 0, 0),
                     pitch=.45)
        a.part('Team_band', 'Team').box((.012, 2.4, .1), loc=(s * 1.02, .3, .76), bevel=0)
    a.part('Ramp_lines', 'Undercarriage').box((1.3, .02, .04), loc=(0, 2.845, .5), bevel=0)
    for s in (-1, 1):
        a.part('Ramp_lines', 'Undercarriage').box((.04, .02, .85), loc=(s * .63, 2.85, .9), bevel=0)
        K.lamp(a, (s * .8, -2.72, .98), (0, -1, .2), r=.06, guard=True)
        a.part('Light_rims', 'Armor').box((.18, .04, .14), loc=(s * .8, -2.7, .98), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .07), loc=(s * .85, 2.86, 1.2), bevel=0)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .5, -2.82, .62), facing=(0, -1, 0), size=.09)
    a.part('Trim_plate', 'Armor').box((1.5, .06, .3), loc=(0, -2.72, .7), rot=(.5, 0, 0), bevel=0)
    _cv_roof(a)
    a.pivot('Point_fire', (0, .8, 1.6))
    a.pivot('Point_exhaust', (-.7, 2.85, .7))
    k.clean(a)


def _cv_roof(a):
    """The roof: the driver's hatch with three periscopes and vision blocks, the commander's cupola with its vision
    ring and the 12.7 mm on its riser, the exhaust louvres on the right front, the folded telescopic mast in its
    cradles along the roof with the sensor head, the SATCOM dish, a row of whip antennas on their bases, the tent
    rolled on the rear deck under straps, the beacons, stowage bins."""
    # Driver (front left): hatch, three periscope hoods with glass.
    hc = (-.45, -1.75, 1.4)
    k.ring(a.part('Hatch_fittings', 'Steel'), [(.22, 0), (.27, 0), (.27, .05), (.22, .05)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .07), (.2, .065), (.24, .04), (.24, .02)], loc=hc, seg=10)
    for dx in (-.2, 0, .2):
        a.part('Periscope_hoods', 'Armor').box((.14, .1, .07), loc=(-.45 + dx, -2.03, 1.41), rot=(-.3, 0, 0), bevel=0)
        a.part('Periscope', 'Glass').box((.11, .01, .04), loc=(-.45 + dx, -2.085, 1.405), rot=(-.3, 0, 0), bevel=0)
    # Exhaust louvres (the engine is front right).
    K.grille(a, (.45, -1.6, 1.405), .55, .5, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    a.part('Exhaust_louvres', 'Armor').box((.04, .5, .25), loc=(.99, -1.25, 1.15), bevel=0)
    a.part('Exhaust', 'Undercarriage').box((.02, .4, .15), loc=(1.0, -1.25, 1.15), bevel=0)
    # Commander's cupola with its vision blocks, the gun on the riser (roof-gun rule).
    k.ring(a.part('Hatch_fittings', 'Steel'), [(.3, 0), (.36, 0), (.36, .06), (.3, .06)], loc=(.5, -1.4, 1.4),
           seg=12)
    for i in range(6):
        u = i * TAU / 6 + .26
        a.part('Glass', 'Glass').box((.07, .015, .04), loc=(.5 + math.cos(u) * .34, -1.4 + math.sin(u) * .34, 1.43),
                                     rot=(0, 0, u + R90), bevel=0)
    K.pintle_mg(a, None, (.5, -1.4, 1.46), length=.7, post=.06, shield=True)
    # The telescopic mast folded along the roof's left in two cradles, its sensor head forward.
    mast = a.part('Mast', 'Steel')
    for j, r in enumerate((.09, .07, .05)):
        mast.cyl(r, 2.6 - j * .3, loc=(-.55, .9 - j * .1, 1.6), rot=K.FORWARD, seg=8, bevel=0)
    for y in (-.2, 1.9):
        a.part('Mast', 'Armor').box((.3, .1, .2), loc=(-.55, y, 1.5), bevel=0)
    k.lathe(a.part('Mast', 'Armor'), [(.16, -.1), (.16, .12), (0, .14)], loc=(-.55, 2.3, 1.6), rot=K.BACKWARD, seg=10)
    K.chamfer_box(a.part('Sensor', 'Armor'), (.26, .3, .24), loc=(-.55, -.55, 1.62), c=.03)
    a.part('Glass', 'Glass').box((.14, .01, .1), loc=(-.55, -.705, 1.64), bevel=0)
    # The SATCOM dish on its pedestal, antenna row along the right edge.
    K.dish(a.part('Dish', 'Medical'), a.part('Dish', 'Steel'), (.45, .3, 1.75), r=.28, normal=(0, -.4, 1), seg=12)
    a.part('Dish', 'Steel').cyl(.04, .3, loc=(.45, .3, 1.55), seg=6, bevel=0)
    ant = a.part('Antenna', 'Steel')
    for j, (x, y, h) in enumerate(((.78, .9, .65), (.78, 1.45, .7), (.78, 2.0, .6), (-.8, 2.5, .68), (.2, 2.55, .55))):
        ant.cyl(.05, .06, loc=(x, y, 1.45), seg=6, bevel=0)
        K.whip_antenna(ant, (x, y, 1.48), h=h, lean=.05)
    # The command tent rolled across the rear deck under its straps, beacons, bins.
    a.part('Tent', 'Canvas').cyl(.16, 1.5, loc=(.0, 2.45, 1.58), rot=(0, R90, 0), seg=10, bevel=.02)
    for x in (-.5, .5):
        a.part('Straps', 'Undercarriage').box((.05, .34, .34), loc=(x, 2.45, 1.58), bevel=0)
    for x in (-.8, .8):
        a.part('Beacons', 'TeamGlow').cyl(.05, .08, loc=(x, 2.7, 1.47), seg=8, bevel=0)
        a.part('Beacons', 'Armor').cyl(.06, .03, loc=(x, 2.7, 1.42), seg=8, bevel=0)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.4, .7, .25), (.4, 1.3, 1.53), bands=1)
    K.jerrycan(a.part('Stowage', 'Armor'), (-.85, 2.9, .85), rot=(0, 0, R90))
    a.part('Team_band', 'Team').box((1.2, .6, .012), loc=(0, .3, 1.415), bevel=0)


# ============================================================================= railgun_truck (its own vehicle)
def railgun_truck(a):
    """See the module docstring. Runtime: Turret (the gun's yaw pivot on the rear deck), Muzzle_main (the rails'
    mouth), Point_fire, Point_exhaust. The charge glow lives in Main_cannon_glow and Radiator_glow (Energy)."""
    R, WD, HX = .55, .4, .93
    _wheels(a, (-3.55, -2.3, 1.55, 2.8), R, WD, HX, nuts=0, springs=False)
    _rails(a, -4.6, 4.7, .95, .5, cross=(-4.2, -2.9, -1.0, .6, 2.2, 4.4))
    for y0, y1 in ((-4.1, -1.75), (1.0, 3.35)):
        _fender(a, y0, y1, HX, 1.2, w=.46)
    for s in (-1, 1):
        for y in (-2.92, 2.2):     # bogie beams between each axle pair
            a.part('Suspension', 'Steel').box((.1, 1.4, .14), loc=(s * (HX - .32), y + (.0 if y > 0 else -.0), .78),
                                              bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.42, .02, .4), loc=(s * HX, 3.38, .92), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * .95, 4.9, 1.05), bevel=0)
        K.outrigger(a.part('Outriggers', 'Armor'), a.part('Outrigger_pads', 'Steel'), (s * .75, 4.5, 1.0), s,
                    reach=.25, drop=.62, w=.16)
    _rail_cab(a)
    _rail_power(a)
    _rail_gun(a)
    a.pivot('Point_fire', (0, -1.35, 2.3))
    a.pivot('Point_exhaust', (1.0, -3.05, 2.3))
    k.clean(a)


def _rail_cab(a):
    """The low armoured cab-over cab (kept under the rails' travel line): faceted front with two narrow armoured
    windscreens, side doors with vision blocks, the bumper with the winch, lamps, the travel rest on its roof."""
    y0, y1 = -4.86, -2.95
    cab = a.part('Body', 'Team')
    k.sharp_loft(cab, [[(-1.18, y0 + .05, .95), (1.18, y0 + .05, .95), (1.18, y1, .95), (-1.18, y1, .95)],
                       [(-1.18, y0, 1.45), (1.18, y0, 1.45), (1.18, y1, 1.45), (-1.18, y1, 1.45)],
                       [(-1.0, y0 + .45, 2.1), (1.0, y0 + .45, 2.1), (1.02, y1, 2.12), (-1.02, y1, 2.12)]],
                 chamfer=.05)
    for x0, x1 in ((.95, .1), (-.1, -.95)):
        K.windscreen(a, [(x0, y0 + .06, 1.52), (x1, y0 + .06, 1.52), (x1, y0 + .38, 1.98), (x0, y0 + .38, 1.98)],
                     frame_mat='Armor', wipers=1, bar=.07)
    for s in (-1, 1):
        a.part('Glass', 'Glass').box((.02, .36, .26), loc=(s * 1.13, -3.9, 1.7), bevel=0)
        a.part('Armor', 'Armor').box((.03, .46, .36), loc=(s * 1.135, -3.9, 1.7), bevel=0)
        a.part('Door_lines', 'Armor').box((.02, .03, .9), loc=(s * 1.18, -3.3, 1.4), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.19, -3.5, 1.35), (s * 1.19, -3.35, 1.35), (s, 0, 0), h=.04)
        K.lamp(a, (s * .85, y0 - .005, 1.15), (0, -1, 0), r=.08, guard=True)
        a.part('Light_rims', 'Armor').box((.22, .03, .18), loc=(s * .85, y0 + .005, 1.15), bevel=0)
        a.part('Steps', 'Steel').box((.3, .34, .03), loc=(s * 1.1, -3.0, .72), bevel=0)
    K.grille(a, (0, y0 - .005, 1.22), 1.0, .3, facing=(0, -1, 0), slats=4, frame_mat='Armor')
    a.part('Bumper', 'Armor').box((2.4, .18, .26), loc=(0, y0 - .02, .92), bevel=0)
    for x in (-.7, .7):
        K.tow_hook(a.part('Kit_tow', 'Steel'), (x, y0 - .1, .9), facing=(0, -1, 0), size=.09)
    # The travel rest: a padded yoke on two struts on the cab roof, under the rails.
    rest = a.part('Rest', 'Steel')
    for s in (-1, 1):
        rest.tube([(s * .45, -3.6, 2.12), (s * .22, -3.6, 2.42)], .04, seg=6)
    rest.box((.6, .16, .06), loc=(0, -3.6, 2.44), bevel=0)
    a.part('Rest_pads', 'Rubber').box((.5, .14, .04), loc=(0, -3.6, 2.49), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, -3.1, 2.12), h=.7, lean=.05)


def _rail_power(a):
    """Behind the cab: the gas-turbine generator house with its intake and the exhaust stack, the radiator banks on
    both sides with the glowing cores (Radiator_glow), the capacitor bank (Tanks) in its shielded rack (MetalSheet),
    the bus cables to the gun, the bed."""
    gen = a.part('Body', 'Team')
    K.chamfer_box(gen, (2.2, 1.8, 1.0), loc=(0, -1.85, 1.65), c=.05)
    K.grille(a, (0, -2.76, 1.75), 1.2, .5, facing=(0, -1, 0), slats=5, frame_mat='Armor')
    k.lathe(a.part('Exhaust', 'Steel'), [(.1, 0), (.1, .9), (.12, .92), (.12, 1.0)], loc=(1.0, -3.05, 1.3), seg=8)
    K.soot(a, (1.0, -3.05, 2.3), radius=.35, k=.5)
    for s in (-1, 1):
        rad = a.part('Radiators', 'Armor')
        K.chamfer_box(rad, (.14, 1.5, .8), loc=(s * 1.15, -1.85, 1.6), c=.02)
        for j in range(6):
            a.part('Radiator_glow', 'Energy').box((.02, .18, .62), loc=(s * 1.225, -2.45 + j * .24, 1.6), bevel=0)
            a.part('Radiator_fins', 'Steel').box((.04, .03, .7), loc=(s * 1.235, -2.33 + j * .24, 1.6), bevel=0)
    a.part('Bed', 'Armor').box((2.4, 5.6, .1), loc=(0, 1.9, 1.15), bevel=0)
    # The capacitor bank: three rows of drums in a shielded rack, its bus bars and cables to the turret.
    rack = a.part('Capacitor_rack', 'MetalSheet')
    rack.box((2.1, 2.2, .06), loc=(0, .1, 1.98), bevel=0)
    for s in (-1, 1):
        rack.box((.06, 2.2, .78), loc=(s * 1.05, .1, 1.6), bevel=0)
    tanks = a.part('Tanks', 'Steel')
    for i in range(3):
        for j in range(4):
            tanks.cyl(.2, .7, loc=(-.62 + i * .62, -.75 + j * .55, 1.56), seg=8, bevel=0)
            a.part('Tank_caps', 'Undercarriage').cyl(.12, .05, loc=(-.62 + i * .62, -.75 + j * .55, 1.93), seg=6,
                                                     bevel=0)
    bus = a.part('Bus_bars', 'Alloy')
    for x in (-.3, .3):
        bus.box((.05, 2.0, .04), loc=(x, .1, 2.03), bevel=0)
    cab = a.part('Kit_cables', 'Rubber')
    for x in (-.5, .5):
        cab.tube([(x, 1.2, 1.95), (x * .7, 1.9, 1.6), (x * .4, 2.4, 1.5)], .05, seg=6)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.36, .9, .36), (1.0, 4.1, 1.38), bands=1)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.36, .9, .36), (-1.0, 4.1, 1.38), bands=1)
    a.part('Team_band', 'Team').box((2.21, .3, .012), loc=(0, -1.85, 2.155), bevel=0)


def _rail_gun(a):
    """The gun on the Turret pivot: the turntable and the armoured mount with its trunnions, the breech block and
    the loader, the two rails (Main_cannon_rails) held in insulator bands (Main_cannon_bands) with the glowing
    bore between them (Main_cannon_glow), the cooling ribs, the muzzle frame (Muzzle_brake), the elevation rams."""
    t = a.pivot('Turret', (0, 2.95, 1.3))
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.8, 0), (.84, .02), (.84, .12), (.78, .14)], seg=16)
    K.bolt_ring(a.part('Kit_bolts', 'Steel', t), (0, 0, .14), (0, 0, 1), .72, 8)
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(-.9, -.7, .14), (.9, -.7, .14), (.9, .9, .14), (-.9, .9, .14)],
                        [(-.75, -.5, .9), (.75, -.5, .9), (.75, .85, .9), (-.75, .85, .9)]], chamfer=.04)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(arm, (.14, 1.2, .5), loc=(s * .55, -.1, 1.15), c=.02)
        a.part('Turret_steel', 'Steel', t).cyl(.12, .1, loc=(s * .64, 0, 1.25), rot=(0, R90, 0), seg=10, bevel=0)
    # Breech and loader.
    K.chamfer_box(a.part('Main_cannon_breech', 'Armor', t), (.75, 1.0, .55), loc=(0, .1, 1.35), c=.05)
    K.chamfer_box(a.part('Breech_loader', 'Steel', t), (.4, .5, .3), loc=(0, .85, 1.3), c=.03)
    a.part('Kit_cables', 'Rubber', t).tube([(.3, .6, 1.4), (.42, .3, 1.5), (.42, -.2, 1.42)], .04, seg=6)
    # The rails, the bore glow between them, the insulator bands and ribs along them.
    y0, y1, zc = -7.85, -.35, 1.35
    rails = a.part('Main_cannon_rails', 'Steel', t)
    for s in (-1, 1):
        k.extrude(rails, [(s * .1 - .06, -.13), (s * .1 + .06, -.13), (s * .1 + .06, .13), (s * .1 - .06, .13)],
                  y1 - y0, loc=(0, (y0 + y1) / 2, zc), rot=(R90, 0, 0), axis='Z', chamfer=.015, ends=(True, True))
    a.part('Main_cannon_glow', 'Energy', t).box((.06, y1 - y0 - .2, .12), loc=(0, (y0 + y1) / 2 - .05, zc),
                                                bevel=0)
    bands = a.part('Main_cannon_bands', 'MetalSheet', t)
    n = 12
    for i in range(n):
        y = y1 - .3 - i * (y1 - y0 - .7) / (n - 1)
        big = i % 3 == 0
        k.extrude(bands, [(-.27, -.22), (.27, -.22), (.27, .22), (-.27, .22)] if big else
                  [(-.22, -.18), (.22, -.18), (.22, .18), (-.22, .18)], .12 if big else .06, loc=(0, y, zc),
                  rot=(R90, 0, 0), axis='Z', chamfer=.02)
    ribs = a.part('Main_cannon_ribs', 'Armor', t)
    for s in (-1, 1):
        ribs.box((.04, y1 - y0 - 1.2, .05), loc=(s * .18, (y0 + y1) / 2 + .2, zc + .14), bevel=0)
    k.extrude(a.part('Muzzle_brake', 'Armor', t), [(-.32, -.26), (.32, -.26), (.32, .26), (-.32, .26)], .3,
              loc=(0, y0 + .1, zc), rot=(R90, 0, 0), axis='Z', chamfer=.03, ends=(True, True))
    a.pivot('Muzzle_main', (0, -7.9, 1.35), t)
    # Elevation rams from the mount to the rail cradle.
    for s in (-1, 1):
        a.part('Rams', 'Armor', t).tube([(s * .4, -.55, .6), (s * .28, -1.6, 1.08)], .07, seg=8)
        a.part('Ram_rods', 'Steel', t).tube([(s * .3, -1.4, 1.02), (s * .24, -1.9, 1.2)], .04, seg=6)
    a.part('Team_band', 'Team', t).box((1.52, .4, .012), loc=(0, .2, .91), bevel=0)


# ============================================================================= radar_scout (Fennek-class with the mast)
def radar_scout(a):
    """See the module docstring. Runtime: Turret (the remote 12.7 mm station's yaw pivot), Muzzle_mg (on it),
    Point_fire, Point_exhaust; Part_wheel / Part_wheelb come from mb_p34_parts out of these Tyres / Wheels."""
    R, WD, HX = .45, .34, .82
    for y in (-1.4, 1.35):
        for s in (-1, 1):
            K.tread_wheel(a, (s * HX, y, R), R, WD, s, seg=12, nuts=5)
            K.dust(a, (s * HX, y, .12), radius=.55, k=.22)
        K.axle(a.part('Axles', 'Undercarriage'), y, R, HX - WD / 2, r=.07)
        for s in (-1, 1):
            a.part('Axles', 'Steel').tube([(s * (HX - .25), y, R + .02), (s * .35, y + .3, R + .3)], .04, seg=5)
    a.part('Chassis', 'Undercarriage').box((1.2, 4.2, .28), loc=(0, 0, .55), bevel=0)
    hull = a.part('Hull', 'Team')
    k.sharp_loft(hull, [[(-.7, -2.25, .5), (.7, -2.25, .5), (.7, 2.3, .55), (-.7, 2.3, .55)],
                        [(-.97, -2.38, .82), (.97, -2.38, .82), (.97, 2.38, .86), (-.97, 2.38, .86)],
                        [(-.97, -1.95, 1.05), (.97, -1.95, 1.05), (.97, 2.35, 1.1), (-.97, 2.35, 1.1)],
                        [(-.8, -1.1, 1.42), (.8, -1.1, 1.42), (.82, 2.3, 1.42), (-.82, 2.3, 1.42)]], chamfer=.04)
    fen = a.part('Fenders', 'Team')
    for y in (-1.4, 1.35):
        for s in (-1, 1):
            k.extrude(fen, [(-.55, 0), (-.42, .22), (.42, .22), (.55, 0), (.5, -.04), (-.5, -.04)], .2,
                      loc=(s * .96, y, .88), axis='X', chamfer=.01)
    # The front: windscreen panes on the glacis, lamps, tow points; the sides: doors with vision blocks.
    K.windscreen(a, [(.75, -1.75, 1.16), (.05, -1.75, 1.16), (.05, -1.25, 1.38), (.75, -1.25, 1.38)],
                 frame_mat='Armor', wipers=1, bar=.05)
    K.windscreen(a, [(-.05, -1.75, 1.16), (-.75, -1.75, 1.16), (-.75, -1.25, 1.38), (-.05, -1.25, 1.38)],
                 frame_mat='Armor', wipers=1, bar=.05)
    for s in (-1, 1):
        K.lamp(a, (s * .75, -2.37, .95), (0, -1, 0), r=.06, guard=True)
        a.part('Light_rims', 'Armor').box((.18, .04, .14), loc=(s * .75, -2.35, .95), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .07), loc=(s * .8, 2.39, 1.0), bevel=0)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .5, -2.42, .65), facing=(0, -1, 0), size=.08)
        a.part('Glass', 'Glass').box((.02, .4, .2), loc=(s * .97, -.7, 1.2), rot=(0, s * .3, 0), bevel=0)
        a.part('Door_lines', 'Armor').box((.02, .03, .55), loc=(s * .98, -.2, 1.0), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * .99, -.45, .98), (s * .99, -.3, .98), (s, 0, 0), h=.04)
        K.smoke_dischargers(a, s * .78, -1.6, 1.3, s, count=3)
        a.part('Team_bands', 'Team').box((.012, 1.8, .1), loc=(s * .985, .9, .95), bevel=0)
        K.jerrycan(a.part('Stowage', 'Crate'), (s * .99, 1.95, 1.0), rot=(0, 0, 0), scale=.9)
    # Engine deck at the rear: grilles, exhaust, the hatch.
    K.grille(a, (.35, 1.75, 1.425), .55, .8, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    a.part('Engine_deck', 'Armor').box((1.5, 1.4, .03), loc=(0, 1.6, 1.415), bevel=0)
    K.exhaust(a, (.8, 2.2, .7), r=.05, length=.3, direction=(0, 0, 1))
    K.soot(a, (.8, 2.2, 1.0), radius=.3, k=.4)
    hc = (-.45, -.85, 1.42)
    k.ring(a.part('Hatch_fittings', 'Steel'), [(.2, 0), (.25, 0), (.25, .05), (.2, .05)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .07), (.18, .065), (.22, .04), (.22, .02)], loc=hc, seg=10)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.5, .5, .25), (-.4, .4, 1.54), bands=1)
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (0, 2.25, 1.5), length=1.4,
               r=.12, axis='X')
    K.whip_antenna(a.part('Antenna', 'Steel'), (-.75, 2.0, 1.42), h=1.1, lean=.05)
    _scout_turret(a)
    _scout_mast(a)
    a.pivot('Point_fire', (0, 0, 1.6))
    a.pivot('Point_exhaust', (.8, 2.2, 1.0))
    k.clean(a)


def _scout_turret(a):
    """The remote weapon station on the Turret pivot: its ring, the cradle, the 12.7 mm with the big ammunition
    box, the sight head and the shield."""
    k.ring(a.part('Ring', 'Steel'), [(.3, 0), (.36, 0), (.36, .05), (.3, .05)], loc=(0, -.3, 1.42), seg=12)
    t = a.pivot('Turret', (0, -.3, 1.45))
    K.chamfer_box(a.part('Turret_body', 'Team', t), (.5, .55, .2), loc=(0, .05, .1), c=.03)
    for s in (-1, 1):
        k.block(a.part('MG_shield', 'Armor', t), (.03, .5, .3), loc=(s * .2, -.05, .2), chamfer=.01)
    k.lathe(a.part('MG', 'Steel', t), [(.04, 0), (.04, .4), (.03, .42), (.03, .7), (.04, .72), (.04, .78), (0, .79)],
            loc=(0, -.16, .3), rot=K.FORWARD, seg=8)
    K.chamfer_box(a.part('MG', 'Steel', t), (.12, .38, .14), loc=(0, .05, .3), c=.015)
    K.chamfer_box(a.part('MG_ammo', 'Armor', t), (.18, .26, .2), loc=(.25, .08, .3), c=.02)
    K.chamfer_box(a.part('Turret_sight', 'Armor', t), (.16, .2, .18), loc=(-.26, -.05, .38), c=.02)
    a.part('Glass', 'Glass', t).box((.1, .01, .08), loc=(-.26, -.155, .4), bevel=0)
    a.pivot('Muzzle_mg', (0, -.95, .3), t)


def _scout_mast(a):
    """The telescopic sensor mast at the rear left: the base housing, three sections with their collars and guy
    clamps, the sensor head on top (EO lens, radar panel, laser window)."""
    x, y = -.45, 1.15
    K.chamfer_box(a.part('Mast', 'Armor'), (.4, .4, .3), loc=(x, y, 1.57), c=.03)
    m = a.part('Mast', 'Steel')
    z = 1.72
    for j, (r, h) in enumerate(((.09, .85), (.07, .75), (.055, .7))):
        m.cyl(r, h, loc=(x, y, z + h / 2), seg=8, bevel=0)
        a.part('Mast', 'Armor').cyl(r + .025, .06, loc=(x, y, z + h), seg=8, bevel=0)
        z += h - .05
    head = a.part('Sensor_head', 'Armor')
    K.chamfer_box(head, (.42, .34, .3), loc=(x, y, z + .15), c=.04)
    head.box((.5, .06, .36), loc=(x, y + .19, z + .18), bevel=0)        # the radar panel behind
    lens = a.part('Sensor_lens', 'Glass')
    lens.cyl(.08, .04, loc=(x - .1, y - .18, z + .16), rot=K.FORWARD, seg=10, bevel=0)
    lens.box((.1, .02, .07), loc=(x + .1, y - .175, z + .2), bevel=0)
    a.part('Antenna', 'Steel').cyl(.012, .16, loc=(x + .15, y, z + .38), seg=4, bevel=0)


# ============================================================================= heavy_aa (Pantsir-S1 on the KamAZ 8x8)
def heavy_aa(a):
    """See the module docstring. Runtime: Turret (the combat module's yaw pivot), Radar (the search radar, spins,
    on the turret), Muzzle_main (the left gun), Muzzle_missile .. .003 (the tube columns), Point_fire,
    Point_exhaust; launch pairs `Missile_pack`; Part_wheel / Part_wheelb from mb_p34_parts."""
    R, WD, HX = .55, .4, .93
    _wheels(a, (-3.95, -2.65, 1.45, 2.7), R, WD, HX, nuts=0, springs=False, diff_rear=False)
    _rails(a, -4.6, 4.7, .95, .5, cross=(-4.2, -3.3, -1.5, .2, 2.1, 4.4))
    for y0, y1 in ((-4.55, -2.05), (.85, 3.3)):
        _fender(a, y0, y1, HX, 1.22, w=.46)
    for s in (-1, 1):
        for y in (-3.3, 2.07):
            a.part('Suspension', 'Steel').box((.1, 1.3, .14), loc=(s * (HX - .32), y, .78), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.42, .02, .4), loc=(s * HX, 3.33, .92), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * .95, 4.85, 1.05), bevel=0)
        K.outrigger(a.part('Outriggers', 'Armor'), a.part('Outrigger_pads', 'Steel'), (s * .75, 4.45, 1.0), s,
                    reach=.25, drop=.62, w=.16)
    _pantsir_cab(a)
    _pantsir_body(a)
    _pantsir_turret(a)
    a.pivot('Point_fire', (0, -2.1, 2.2))
    a.pivot('Point_exhaust', (.85, -3.1, 2.25))
    k.clean(a)


def _pantsir_cab(a):
    """The KamAZ cab-over cab: the flat-fronted body with its slight rake, the split windscreen, doors with windows,
    the grille and bumper, mirrors, the roof beacon and the exhaust stack behind it."""
    y0, y1 = -4.92, -3.15
    cab = a.part('Body', 'Team')
    k.sharp_loft(cab, [[(-1.2, y0 + .05, 1.0), (1.2, y0 + .05, 1.0), (1.2, y1, 1.0), (-1.2, y1, 1.0)],
                       [(-1.2, y0, 1.55), (1.2, y0, 1.55), (1.2, y1, 1.55), (-1.2, y1, 1.55)],
                       [(-1.12, y0 + .25, 2.35), (1.12, y0 + .25, 2.35), (1.12, y1, 2.38), (-1.12, y1, 2.38)]],
                 chamfer=.05)
    for x0, x1 in ((1.0, .04), (-.04, -1.0)):
        K.windscreen(a, [(x0, y0 + .04, 1.65), (x1, y0 + .04, 1.65), (x1, y0 + .22, 2.2), (x0, y0 + .22, 2.2)],
                     frame_mat='Armor', wipers=1, bar=.05)
    for s in (-1, 1):
        a.part('Glass', 'Glass').box((.02, .6, .45), loc=(s * 1.17, -4.1, 1.95), bevel=0)
        a.part('Door_lines', 'Armor').box((.02, .03, 1.0), loc=(s * 1.205, -3.45, 1.6), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.215, -3.65, 1.45), (s * 1.215, -3.5, 1.45), (s, 0, 0), h=.04)
        K.mirror(a.part('Mirrors', 'Steel'), (s * 1.18, -4.75, 2.0), s, arm=.06)
        K.lamp(a, (s * .9, y0 - .005, 1.2), (0, -1, 0), r=.08, guard=False)
        a.part('Light_rims', 'Armor').box((.22, .03, .16), loc=(s * .9, y0 + .005, 1.2), bevel=0)
        a.part('Steps', 'Steel').box((.3, .34, .03), loc=(s * 1.1, -3.4, .72), bevel=0)
    K.grille(a, (0, y0 - .005, 1.3), 1.1, .3, facing=(0, -1, 0), slats=4, frame_mat='Armor')
    a.part('Bumper', 'Armor').box((2.4, .18, .26), loc=(0, y0 - .02, .95), bevel=0)
    for x in (-.7, .7):
        K.tow_hook(a.part('Kit_tow', 'Steel'), (x, y0 - .1, .92), facing=(0, -1, 0), size=.09)
    k.lathe(a.part('Exhaust', 'Steel'), [(.08, 0), (.08, .9), (.1, .92), (.1, 1.0)], loc=(.85, -3.1, 1.25), seg=8)
    K.soot(a, (.85, -3.1, 2.25), radius=.3, k=.45)
    a.part('Beacon', 'Alloy').cyl(.06, .08, loc=(-.7, -3.5, 2.42), seg=8, bevel=0)


def _pantsir_body(a):
    """The equipment body behind the cab: the power unit with its louvres and fuel tanks, the operator module under
    the turret with its door, ladder and air conditioners, the cable tray, the tool boxes."""
    pw = a.part('Body', 'Team')
    k.sharp_loft(pw, [[(-1.15, -3.0, 1.2), (1.15, -3.0, 1.2), (1.15, -1.3, 1.2), (-1.15, -1.3, 1.2)],
                      [(-1.15, -3.0, 1.95), (1.15, -3.0, 1.95), (1.15, -1.3, 1.95), (-1.15, -1.3, 1.95)],
                      [(-.85, -2.8, 2.3), (.85, -2.8, 2.3), (.85, -1.45, 2.3), (-.85, -1.45, 2.3)]], chamfer=.04)
    K.grille(a, (1.155, -2.15, 1.6), 1.2, .5, facing=(1, 0, 0), slats=6, frame_mat='Armor')
    K.grille(a, (-1.155, -2.15, 1.6), 1.2, .5, facing=(-1, 0, 0), slats=6, frame_mat='Armor')
    for s in (-1, 1):
        a.part('Tanks', 'Armor').cyl(.26, 1.1, loc=(s * 1.0, -.6, .82), rot=K.FORWARD, seg=10, bevel=.02)
        a.part('Kit_straps', 'Steel').box((.56, .04, .56), loc=(s * 1.0, -.8, .82), bevel=0)
        a.part('Kit_straps', 'Steel').box((.56, .04, .56), loc=(s * 1.0, -.4, .82), bevel=0)
    a.part('Chassis', 'Armor').box((2.4, 5.4, .1), loc=(0, 1.7, 1.15), bevel=0)
    op = a.part('Body', 'Team')
    k.sharp_loft(op, [[(-1.2, -.1, 1.2), (1.2, -.1, 1.2), (1.2, 3.6, 1.2), (-1.2, 3.6, 1.2)],
                      [(-1.2, -.1, 1.25), (1.2, -.1, 1.25), (1.2, 3.6, 1.25), (-1.2, 3.6, 1.25)],
                      [(-1.1, .05, 1.32), (1.1, .05, 1.32), (1.1, 3.5, 1.32), (-1.1, 3.5, 1.32)]], chamfer=.03)
    a.part('Door_lines', 'Armor').box((.03, .62, .5), loc=(1.19, 3.0, .85), bevel=0)
    K.ladder(a.part('Ladders', 'Steel'), (1.0, 3.75, .3), (1.0, 3.62, 1.2), width=.4, step=.25)
    for y in (.4, 3.2):
        K.chamfer_box(a.part('Ac_units', 'Armor'), (.5, .4, .2), loc=(-.75, y, 1.42), c=.02)
    a.part('Cable_tray', 'Undercarriage').box((.15, 3.0, .08), loc=(-1.05, 1.7, 1.36), bevel=0)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.36, .9, .36), (1.0, 4.1, 1.38), bands=1)
    a.part('Team_band', 'Team').box((1.71, .3, .012), loc=(0, -2.1, 2.305), bevel=0)


def _pantsir_turret(a):
    """The combat module on the Turret pivot: the faceted turret body, the search radar on its post at the rear
    (Radar spins it: the flat array, its frame), the tracking radar head on the front (dish, mast, the search panel
    and array), the missile packs either side (Missile_pack: six tubes each in 2 x 3, the pack frame), the twin
    30 mm guns under them (Main_cannon left pair, Main_cannon_2 right pair, their brakes), the EO sight."""
    t = a.pivot('Turret', (0, 1.6, 1.3))
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.85, 0), (.9, .02), (.9, .1), (.84, .12)], seg=16)
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(-.7, -1.5, .12), (.7, -1.5, .12), (.75, 1.0, .12), (-.75, 1.0, .12)],
                        [(-.75, -1.7, .45), (.75, -1.7, .45), (.78, 1.05, .45), (-.78, 1.05, .45)],
                        [(-.55, -1.35, .78), (.55, -1.35, .78), (.6, .95, .8), (-.6, .95, .8)]], chamfer=.04)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(arm, (.14, 1.6, .55), loc=(s * .82, -.5, .5), c=.02)      # the trunnion cheeks
        arm.cyl(.13, .12, loc=(s * .9, -.45, .6), rot=(0, R90, 0), seg=10, bevel=0)
    # Missile packs: each side two columns of three tubes (x .6 and 1.1), the frame round them.
    y0, y1, zc = -1.43, 1.2, .92
    for s in (-1, 1):
        pack = a.part('Missile_pack', 'Team', t)
        K.chamfer_box(pack, (.98, y1 - y0, .72), loc=(s * .85, (y0 + y1) / 2, zc), c=.03)
        fr = a.part('Pack_frame', 'Armor', t)
        for y in (y0 + .05, y1 - .05):
            fr.box((1.04, .08, .78), loc=(s * .85, y, zc), bevel=0)
        tubes = a.part('Pack_tubes', 'Undercarriage', t)
        caps = a.part('Pack_box', 'Steel', t)
        for x in (.6, 1.1):
            for z in (zc - .22, zc, zc + .22):
                tubes.cyl(.105, .05, loc=(s * x, y0 - .02, z), rot=K.FORWARD, seg=8, bevel=0)
                caps.cyl(.075, .02, loc=(s * x, y0 - .05, z), rot=K.FORWARD, seg=6, bevel=0)
    for i, x in enumerate((-1.1, -.6, .6, 1.1)):
        a.pivot('Muzzle_missile' + ('' if i == 0 else f'__{i:03d}'), (x, -1.43, .92), t)
    # The twin 30 mm guns under the packs: the receiver housing, two barrels with brakes each side.
    for s, cn, bn in ((-1, 'Main_cannon', 'Muzzle_brake'), (1, 'Main_cannon_2', 'Muzzle_brake_2')):
        K.chamfer_box(a.part('Turret_steel', 'Steel', t), (.3, .9, .26), loc=(s * .86, -.9, .36), c=.03)
        for dx in (-.07, .07):
            k.lathe(a.part(cn, 'Steel', t), [(.04, 0), (.04, .5), (.03, .52), (.03, 1.6), (0, 1.61)],
                    loc=(s * .86 + dx, -1.3, .36), rot=K.FORWARD, seg=8)
            k.lathe(a.part(bn, 'Undercarriage', t), [(.045, 1.48), (.045, 1.66), (0, 1.67)],
                    loc=(s * .86 + dx, -1.3, .36), rot=K.FORWARD, seg=8)
    a.pivot('Muzzle_main', (-.86, -2.96, .36), t)
    # Tracking radar head at the front of the roof: its mast, the dish, the search panel and array beside it.
    a.part('Radar_mast', 'Steel', t).cyl(.08, .25, loc=(0, -1.15, .9), seg=8, bevel=0)
    K.chamfer_box(a.part('Search_mount', 'Armor', t), (.5, .3, .3), loc=(0, -1.15, 1.1), c=.03)
    K.dish(a.part('Radar_dish', 'Armor', t), a.part('Dish_feed', 'Steel', t), (-.15, -1.33, 1.12), r=.2,
           normal=(0, -1, 0), seg=10)
    k.block(a.part('Search_panel', 'Team', t), (.26, .06, .26), loc=(.15, -1.33, .98), chamfer=.01)
    a.part('Search_array', 'Undercarriage', t).box((.2, .02, .2), loc=(.15, -1.365, 1.11), bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.18, .26, .2), loc=(-.4, -1.3, .9), c=.02)
    a.part('Glass', 'Glass', t).box((.12, .01, .1), loc=(-.4, -1.435, .92), bevel=0)
    # The search radar on its post at the rear (Radar spins it).
    a.part('Search_post', 'Steel', t).cyl(.12, .3, loc=(0, -.3, .9), seg=8, bevel=0)
    r = a.pivot('Radar', (0, -.3, .8), t)
    K.chamfer_box(a.part('Search_drive', 'Armor', r), (.3, .3, .2), loc=(0, 0, .35), c=.03)
    k.block(a.part('Radar_search', 'Team', r), (1.1, .1, .58), loc=(0, .12, .4), rot=(-.25, 0, 0), chamfer=.02)
    a.part('Search_array', 'MetalSheet', r).box((1.0, .02, .48), loc=(0, .05, .68), rot=(-.25, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Search_braces', 'Steel', r).box((.04, .2, .5), loc=(s * .5, .2, .45), bevel=0)
    a.part('Team_band', 'Team', t).box((1.0, .5, .012), loc=(0, -.2, .805), bevel=0)


# ============================================================================= wheeled_gun (Centauro II)
def wheeled_gun(a):
    """See the module docstring. Runtime: Turret, Main_cannon, Muzzle_brake, Muzzle_main, Muzzle_coax,
    Mount_mg / Muzzle_mg (on the turret roof), Point_fire, Point_exhaust; Part_wheel / Part_wheelb from
    mb_p34_parts."""
    R, WD, HX = .46, .34, .94
    for y in (-2.0, -.85, .65, 1.8):
        for s in (-1, 1):
            K.tread_wheel(a, (s * HX, y, R), R, WD, s, seg=12, nuts=0)
            K.dust(a, (s * HX, y, .12), radius=.55, k=.22)
        a.part('Axles', 'Undercarriage').box((2 * HX - .3, .12, .12), loc=(0, y, R), bevel=0)
        for s in (-1, 1):
            a.part('Axles', 'Steel').tube([(s * (HX - .2), y, R + .02), (s * .45, y - .3, R + .28)], .045, seg=5)
    hull = a.part('Hull', 'Team')
    k.sharp_loft(hull, [[(-.7, -2.75, .48), (.7, -2.75, .48), (.7, 2.85, .5), (-.7, 2.85, .5)],
                        [(-1.08, -3.0, .85), (1.08, -3.0, .85), (1.08, 2.98, .88), (-1.08, 2.98, .88)],
                        [(-1.08, -2.7, 1.05), (1.08, -2.7, 1.05), (1.08, 2.95, 1.1), (-1.08, 2.95, 1.1)],
                        [(-.95, -2.0, 1.42), (.95, -2.0, 1.42), (.96, 2.9, 1.44), (-.96, 2.9, 1.44)]], chamfer=.04)
    # Side bins over the wheels, the front engine deck (Centauro's engine is front right), the driver front left.
    deck = a.part('Deck', 'Armor')
    deck.box((1.7, 1.7, .03), loc=(0, -1.2, 1.415), bevel=0)
    K.grille(a, (.45, -1.4, 1.43), .7, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (1.085, -1.9, 1.0), .7, .22, facing=(1, 0, 0), slats=3, frame_mat='Armor')
    hc = (-.5, -1.85, 1.42)
    k.ring(a.part('Hatch_fittings', 'Steel'), [(.22, 0), (.27, 0), (.27, .05), (.22, .05)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .07), (.2, .065), (.24, .04), (.24, .02)], loc=hc, seg=10)
    for dx in (-.18, 0, .18):
        a.part('Periscope_hoods', 'Armor').box((.13, .1, .07), loc=(-.5 + dx, -2.15, 1.41), rot=(-.3, 0, 0), bevel=0)
        a.part('Glass', 'Glass').box((.1, .01, .04), loc=(-.5 + dx, -2.205, 1.405), rot=(-.3, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .85, -2.95, 1.0), (0, -1, .2), r=.06, guard=True)
        a.part('Light_rims', 'Armor').box((.18, .04, .14), loc=(s * .85, -2.93, 1.0), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .07), loc=(s * .9, 2.99, 1.2), bevel=0)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .55, -3.05, .65), facing=(0, -1, 0), size=.09)
        for y in (-1.4, .1, 1.6):
            K.chamfer_box(a.part('Stowage', 'Armor'), (.16, 1.2, .26), loc=(s * 1.13, y, 1.2), c=.02)
        a.part('Team_band', 'Team').box((.012, 4.4, .08), loc=(s * 1.215, .1, 1.05), bevel=0)
    K.exhaust(a, (-.8, 2.9, .9), r=.05, length=.25, direction=(0, 1, 0))
    K.soot(a, (-.8, 2.95, 1.1), radius=.35, k=.4)
    K.crate(a.part('Stowage', 'Crate'), a.part('Kit_latches', 'Steel'), (.7, .4, .3), (0, 2.6, 1.6), bands=2)
    a.part('Trim_plate', 'Armor').box((1.6, .06, .32), loc=(0, -2.86, .72), rot=(.5, 0, 0), bevel=0)
    _centauro_turret(a)
    a.pivot('Point_fire', (0, 2.2, 1.5))
    a.pivot('Point_exhaust', (-.8, 2.9, 1.1))
    k.clean(a)


def _centauro_turret(a):
    """The Hitfact II turret on the Turret pivot: the faceted house with its wedge front and long bustle, the
    mantlet, the 120 mm with thermal sleeve, fume extractor and muzzle brake, the coax, the commander's panoramic
    sight, the gunner's sight box, smoke banks on the cheeks, the 12.7 mm on its post, the bustle rack."""
    t = a.pivot('Turret', (0, -.1, 1.44))
    k.lathe(a.part('Turret_ring', 'Steel', t), [(.9, 0), (.94, .02), (.94, .08), (.88, .1)], seg=16)
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(-.6, -1.55, .08), (.6, -1.55, .08), (1.05, -.9, .08), (1.05, 1.9, .08), (-1.05, 1.9, .08),
                         (-1.05, -.9, .08)],
                        [(-.55, -1.7, .4), (.55, -1.7, .4), (1.1, -.95, .4), (1.1, 1.95, .42), (-1.1, 1.95, .42),
                         (-1.1, -.95, .4)],
                        [(-.45, -1.4, .52), (.45, -1.4, .52), (.92, -.8, .55), (.92, 1.8, .55), (-.92, 1.8, .55),
                         (-.92, -.8, .55)]], chamfer=.04)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.extrude(arm, [(-1.62, .12), (-.95, .12), (-.95, .5), (-1.38, .46)], .1, loc=(s * .82, 0, 0), axis='X',
                  chamfer=.01)        # the cheek armour modules
        K.smoke_dischargers(a, s * .95, -.5, .5, s, count=4, parent=t)
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.62, .35, .5), loc=(0, -1.55, .36), c=.04)
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.7, .32, 3.88, .085, seg=12, extractor=(.38, 1.55, .45),
                 brake='baffle')
    a.pivot('Muzzle_main', (0, -5.88, .32), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.03, 0), (.03, .25), (0, .26)], loc=(-.3, -1.62, .38), rot=K.FORWARD,
            seg=6)
    a.pivot('Muzzle_coax', (-.3, -1.86, .38), t)
    # Commander's panoramic sight (its head on a post), the gunner's sight box, hatches.
    a.part('Sight', 'Steel', t).cyl(.08, .2, loc=(-.45, .1, .65), seg=8, bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.3, .3, .24), loc=(-.45, .1, .84), c=.03)
    a.part('Glass', 'Glass', t).box((.2, .01, .14), loc=(-.45, -.055, .86), bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.26, .3, .2), loc=(.55, -.95, .64), c=.03)
    a.part('Glass', 'Glass', t).box((.18, .01, .12), loc=(.55, -1.105, .65), bevel=0)
    for hx in (-.45, .45):
        hc = (hx, .75, .55)
        k.ring(a.part('Hatch_fittings', 'Steel', t), [(.24, 0), (.29, 0), (.29, .05), (.24, .05)], loc=hc, seg=10)
        k.lathe(a.part('Hatches', 'Armor', t), [(0, .08), (.22, .075), (.26, .05), (.26, .02)], loc=hc, seg=10)
    K.pintle_mg(a, t, (.5, .4, .55), length=.7, post=.07, shield=False)
    # Bustle rack with a net roll, the antennas, the team panel.
    rack = a.part('Bustle_rack', 'Steel', t)
    for s in (-1, 1):
        rack.box((.04, .5, .04), loc=(s * .9, 2.15, .45), bevel=0)
    rack.box((1.84, .04, .04), loc=(0, 2.4, .45), bevel=0)
    rack.box((1.84, .04, .3), loc=(0, 2.4, .3), bevel=0)
    K.net_roll(a.part('Stowage', 'Canvas', t), a.part('Kit_straps', 'Undercarriage', t), (0, 2.2, .55), length=1.5,
               r=.13, axis='X')
    for x in (-.8, .8):
        K.whip_antenna(a.part('Antennas', 'Steel', t), (x, 1.7, .55), h=.38, lean=.05)
    a.part('Team_band', 'Team', t).box((1.2, .9, .012), loc=(0, .9, .555), bevel=0)


BUILDERS = {
    'mlrs': (mlrs, dict(ao_distance=.5, grime_height=.5)),
    'grad_truck': (grad_truck, dict(ao_distance=.6, grime_height=.55, ao_strength=.65)),
    'command_vehicle': (command_vehicle, dict(ao_distance=.5, grime_height=.5, ao_strength=.65)),
    'railgun_truck': (railgun_truck, dict(ao_distance=.6, grime_height=.55)),
    'radar_scout': (radar_scout, dict(ao_distance=.4, ao_strength=.65, grime_height=.4)),
    'heavy_aa': (heavy_aa, dict(ao_distance=.5, grime_height=.5)),
    'wheeled_gun': (wheeled_gun, dict(ao_distance=.55, grime_height=.5)),
}
