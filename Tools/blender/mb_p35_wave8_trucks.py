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


BUILDERS = {
    'mlrs': (mlrs, dict(ao_distance=.5, grime_height=.5)),
    'grad_truck': (grad_truck, dict(ao_distance=.6, grime_height=.55, ao_strength=.65)),
}
