"""Prompt 35 wave 12 (lane C): the heavy anti-tank minefield branch rebuilt from scratch (spec:
Tools/blender/specs/minefield_a.json).

The orphan "Anti-tank mines (A)" file of the no-branch minefield (mb_tower_branches: three big mines lying on the
ground, each with a glowing army-coloured rim so its own side sees it). Drawn as the same field as the rebuilt
minefield / minefield_b (wave 7): the base's earth patch, ruts, stones, tufts and the marked perimeter (lane C's
`mb_p35_minefield._patch`, its own seed), now carrying

- three heavy M21-pattern anti-tank mines laid on the surface (the old file's three, a larger-than-life 1.6 x so the
  battle camera reads them): the pressed-steel drum with its rolled rim and carrying ring, the M607 fuze with the
  tilt-rod extension standing up from it, the arming-plug boss and the pull-ring; each in its scuffed spoil ring and
  with the glowing Team rim (`Mine_rims`, TeamGlow) kept from the old file;
- a TM-83 off-route side-attack mine on its short stake in the rear-right corner aimed across the field, with its
  seismic sensor spiked into the ground on a cable;
- the cleared lane: a white-taped gap with pegs across the front edge, the way engineers mark a crossing;
- an opened mine crate with two more mines and its lid against it, a spare tilt-rod bundle and an entrenching tool.

No runtime nodes (the old file had none). Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_p35_minefield as MF

R90 = math.pi / 2
TAU = math.tau
MINES = ((-1.2, -.85, .2), (1.15, -.25, -.5), (-.2, 1.25, 1.1))


def _m21(a, loc, yaw, r=.37, crated=False):
    """An M21-pattern heavy AT mine standing on loc: drum, rolled rim, carrying ring, fuze, tilt rod, arming boss."""
    x, y, z = loc
    rot = (0, 0, yaw)
    c, s = math.cos(yaw), math.sin(yaw)
    k.lathe(a.part('Mine_bodies', 'Armor'), [(r * .15, 0), (r * .96, 0), (r, .03), (r, .2), (r * 1.04, .22),
                                            (r * 1.04, .26), (r * .92, .28), (r * .45, .3), (0, .3)],
            loc=(x, y, z), rot=rot, seg=18, worn=(3, 4, 5, 6))
    # The carrying ring (a folded wire bail on two lugs) and the arming-plug boss at the side.
    lugs = a.part('Mine_plates', 'Undercarriage')
    for d in (-1, 1):
        lugs.box((.05, .04, .06), loc=(x + c * d * r * .98, y + s * d * r * .98, z + .14), rot=rot, bevel=0)
    if not crated:
        K.handle(a.part('Mine_plates', 'Undercarriage'), (x - s * .14 + c * r, y + c * .14 + s * r, z + .24),
                 (x + s * .14 + c * r, y - c * .14 + s * r, z + .24), (c, s, 0), h=.07, r=.012)
    a.part('Mine_plates', 'Undercarriage').cyl(.06, .06, loc=(x - s * r * .95, y + c * r * .95, z + .1),
                                               rot=(R90, 0, yaw), seg=8, bevel=0)
    # The M607 fuze: a squat cylinder on the crown, its pressure ring and the tilt-rod extension.
    fz = a.part('Mine_fuzes', 'Steel')
    k.lathe(fz, [(.1, 0), (.1, .05), (.075, .07), (.075, .13), (.04, .15), (0, .15)], loc=(x, y, z + .29),
            rot=rot, seg=12, worn=(1,))
    a.part('Mine_bands', 'Hazard').cyl(.105, .02, loc=(x, y, z + .32), seg=12, bevel=0)
    if not crated:
        lean = (.06 * math.sin(yaw * 3), .05 * math.cos(yaw * 2), 0)
        a.part('Tilt_rods', 'Steel').cyl(.012, .6, loc=(x + lean[1] * .3, y - lean[0] * .3, z + .44 + .3),
                                         rot=lean, seg=5, bevel=0)
        a.part('Tilt_rods', 'Hazard').cyl(.02, .06, loc=(x + lean[1] * .6, y - lean[0] * .6, z + 1.04), rot=lean,
                                          seg=6, bevel=0)
        # The glowing army-coloured rim at the foot (the old file's readability ring), the spoil ring round it.
        a.part('Mine_rims', 'TeamGlow').torus(r * 1.22, .035, loc=(x, y, z + .03), seg=20, ring=4)
        k.lathe(a.part('Mine_earth', 'Dirt'), [(r * 1.05, .07), (r * 1.3, .06), (r * 1.6, .025), (r * 1.85, 0)],
                loc=(x, y, z - .02), seg=14, caps=(False, False), worn=(1,))


def _tm83(a):
    """A TM-83 off-route mine on its folding tripod in the rear-right corner, aimed across the field; the seismic
    sensor spiked into the ground on its cable."""
    x, y = -1.75, 1.7
    yaw = -2.3                                   # the face looks across the patch to the front left
    rot = (0, 0, yaw)
    c, s = math.cos(yaw), math.sin(yaw)
    face = (-s, c, 0)
    zc = .5
    legs = a.part('Mine_stake', 'Steel')
    for i in range(3):
        u = yaw + R90 + i * TAU / 3
        legs.tube([(x, y, zc - .12), (x + math.cos(u) * .32, y + math.sin(u) * .32, .05)], .014, seg=4)
        legs.box((.06, .06, .015), loc=(x + math.cos(u) * .32, y + math.sin(u) * .32, .055), bevel=0)
    k.block(a.part('Mine_stake', 'Armor'), (.1, .1, .08), loc=(x, y, zc - .14), rot=rot, chamfer=.01)
    # The charge: a short drum on its side, the dished shaped-charge face (dark) and the rim towards the field.
    k.lathe(a.part('Side_mine', 'Armor'), [(0, -.17), (.15, -.17), (.165, -.14), (.165, .14), (.17, .16), (.15, .17),
                                           (0, .17)], loc=(x, y, zc), rot=(R90, 0, yaw), seg=16, worn=(1, 4))
    a.part('Side_mine_face', 'Undercarriage').cyl(.13, .02, loc=(x + face[0] * .175, y + face[1] * .175, zc),
                                                  rot=(R90, 0, yaw), seg=14, bevel=0)
    a.part('Side_mine_band', 'Team').cyl(.17, .04, loc=(x - face[0] * .07, y - face[1] * .07, zc),
                                         rot=(R90, 0, yaw), seg=16, bevel=0)
    k.block(a.part('Mine_stake', 'Steel'), (.05, .09, .05), loc=(x, y, zc + .19), rot=rot, chamfer=.008)
    k.block(a.part('Mine_stake', 'Steel'), (.05, .03, .04), loc=(x - face[0] * .1, y - face[1] * .1, zc + .1),
            rot=rot, chamfer=.006)
    # The seismic sensor spiked into the ground a metre off, its cable lying in a loose curve.
    sx, sy = x + .6, y - .85
    a.part('Sensor_spike', 'Steel').cyl(.03, .25, loc=(sx, sy, .16), seg=6, bevel=0)
    k.block(a.part('Sensor_spike', 'Armor'), (.08, .08, .1), loc=(sx, sy, .33), chamfer=.012)
    a.part('Mine_cables', 'Rubber').tube([(x, y, zc - .16), (x + .1, y - .2, .07), (x + .45, y - .5, .065),
                                          (sx, sy, .3)], .012, seg=4)


def _lane(a):
    """The marked gap: two white tapes on short pegs across the front edge, with a lane sign."""
    pg = a.part('Lane_pegs', 'Wood')
    tape = a.part('Lane_tape', 'PlasterWhite')
    for x in (.35, 1.05):
        pts = [(x + .03 * (j % 2), -2.3 + j * .55) for j in range(5)]
        for (px, py) in pts:
            pg.box((.035, .035, .26), loc=(px, py, .16), bevel=0)
        for (p0, p1) in zip(pts, pts[1:]):
            L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            tape.box((.008, L, .035), loc=((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, .25),
                     rot=(0, 0, math.atan2(-(p1[0] - p0[0]), p1[1] - p0[1])), bevel=0)
    a.part('Lane_tape', 'PlasterWhite').box((.3, .02, .2), loc=(.7, -2.32, .5), bevel=0)
    a.part('Lane_pegs', 'Wood').box((.04, .04, .45), loc=(.7, -2.3, .27), bevel=0)
    a.part('Lane_sign_mark', 'Hazard').box((.2, .01, .05), loc=(.7, -2.335, .5), bevel=0)


def _crate(a):
    """The opened mine crate with two mines, its lid leaning on it, a bundle of spare rods and a shovel."""
    x, y, yaw = 1.45, 1.55, .35
    rot = (0, 0, yaw)
    m = K.frame((x, y, .06), rot)
    cr = a.part('Mine_crate', 'Wood')
    w, d, h = 1.0, .62, .3
    k.block(cr, (w, .04, h), loc=K._at(m, (0, -d / 2, h / 2)), rot=rot, chamfer=.008)
    k.block(cr, (w, .04, h), loc=K._at(m, (0, d / 2, h / 2)), rot=rot, chamfer=.008)
    k.block(cr, (.04, d, h), loc=K._at(m, (-w / 2, 0, h / 2)), rot=rot, chamfer=.008)
    k.block(cr, (.04, d, h), loc=K._at(m, (w / 2, 0, h / 2)), rot=rot, chamfer=.008)
    cr.box((w - .02, d - .02, .03), loc=K._at(m, (0, 0, .03)), rot=rot, bevel=0)
    band = a.part('Crate_bands', 'Steel')
    for f in (-.3, .3):
        band.box((.03, d + .012, h + .01), loc=K._at(m, (f, 0, h / 2)), rot=rot, bevel=0)
    a.part('Sign_marks', 'PlasterWhite').box((.4, .006, .08), loc=K._at(m, (0, -d / 2 - .022, h * .6)), rot=rot,
                                                bevel=0)
    for f in (-.22, .22):
        p = K._at(m, (f, 0, .045))
        _m21(a, (p[0], p[1], p[2]), yaw, r=.22, crated=True)
    # The lid leaning against the crate's rear face, its rope handles.
    k.block(cr, (w, .04, .62), loc=K._at(m, (0, d / 2 + .16, .3)), rot=(-.35, 0, yaw), chamfer=.008)
    a.part('Tilt_rods', 'Steel').tube([K._at(m, (-.4, -d / 2 - .25, .04)), K._at(m, (.45, -d / 2 - .35, .04))],
                                        .03, seg=6)
    a.part('Tilt_rods', 'Hazard').box((.04, .07, .07), loc=K._at(m, (0, -d / 2 - .3, .05)), rot=rot, bevel=0)
    C.entrenching_tools(a, (x - .9, y + .2, .06), yaw=1.2, lean=.25)


def minefield_a(a, detail=False):
    """The heavy anti-tank minefield (see the module docstring)."""
    MF._patch(a, seed=2, rng=random.Random(3512))
    for x, y, yaw in MINES:
        _m21(a, (x, y, .05), yaw)
    _tm83(a)
    _lane(a)
    _crate(a)
    k.clean(a)


BUILDERS = {
    'minefield_a': (minefield_a, dict(ao_distance=.3, grime_height=.2)),
}
