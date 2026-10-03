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


BUILDERS = {
    'mlrs': (mlrs, dict(ao_distance=.5, grime_height=.5)),
}
