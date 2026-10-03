"""Prompt 35 wave 12 (lane C): the wire obstacle branch of dragon's teeth rebuilt from scratch (spec:
Tools/blender/specs/dragons_teeth_b.json).

dragons_teeth.wire (towerRole wire_slow, passable with a slow aura): a triple-standard concertina fence (FM 5-34 /
STANAG barbed-wire obstacle) laid on the same half-buried footing as lane A's rebuilt dragons_teeth /
dragons_teeth_a (wave 8: `mb_p35_wave8_fort._footing`, the cast spine, the dug earth bed, stones and grass, the marker
stakes with Team bands at the two ends), so the three read as one family:

- two rows of U-section steel long pickets driven into sockets on the spine, each with its strand eyes and the
  driving cap; short anchor pickets at the two ends, angled out, with their guy wires;
- two base coils of razor-wire concertina (helical coils, front and rear) and the top coil resting in the cradle
  between them, tied to the pickets with wire clips; barbed strands along both picket rows (top and bottom);
- warning tags, the empty-tin alarm rattles hung on the top strand, a barbed-wire spool on its wooden reel and a pair
  of heavy gloves left on the footing at one end.

The coils and the picket rows repeat every 5 m along X (the helix phase meets itself at x = +-2.5), so segments laid
end to end continue. No runtime nodes (a static obstacle). Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_wave8_fort as F

R90 = math.pi / 2
TAU = math.tau
TOP = .07                       # the footing spine's top (lane A's _footing)
PICKETS = (-1.875, -.625, .625, 1.875)
ROW_Y = .36                     # the picket rows either side of the centre line
LOOPS = 18                      # helix turns per 5 m segment (an integer: the phase repeats at the ends)


def _coil(a, y, zc, r, phase=0.0, pts_per_loop=11):
    """One concertina coil along X: a helix of razor wire (thin tube), its loops slightly flattened at the bottom
    where it rests, the phase matching at x = -2.5 and +2.5."""
    pts = []
    n = LOOPS * pts_per_loop
    for i in range(n + 1):
        f = i / n
        u = phase + f * LOOPS * TAU
        x = -2.5 + 5.0 * f + .06 * math.sin(u)            # the loops lean a little (a stretched coil)
        cy, cz = math.cos(u) * r, math.sin(u) * r
        if cz < -r * .8:
            cz = -r * .8                                  # the flattened foot of each loop
        pts.append((x, y + cy, zc + cz))
    a.part('Razor_wire', 'Steel').tube(pts, .011, seg=3, caps=False)


def _picket(a, x, y, h, lean=(0, 0)):
    """A U-section steel long picket: the channel, its driving cap, three strand eyes, set in a socket block."""
    prof = [(-.035, -.025), (.035, -.025), (.035, .025), (.022, .025), (.022, -.012), (-.022, -.012), (-.022, .025),
            (-.035, .025)]
    rot = (lean[0], lean[1], 0)
    k.extrude(a.part('Pickets', 'Armor'), prof, h, loc=(x, y, TOP + h / 2 - .05), rot=rot, axis='Z', chamfer=0)
    k.block(a.part('Picket_caps', 'Steel'), (.09, .07, .05), loc=(x + lean[1] * h, y - lean[0] * h, TOP + h - .04),
            rot=rot, chamfer=.012)
    eyes = a.part('Picket_eyes', 'Steel')
    for z in (.3, .62, .95):
        eyes.torus(.03, .007, loc=(x + lean[1] * z, y - lean[0] * z - math.copysign(.035, y), TOP + z),
                   rot=(0, 0, 0), seg=6, ring=3)
    k.block(a.part('Footing', 'Plaster'), (.2, .2, .08), loc=(x, y, TOP + .01), chamfer=.015)


def dragons_teeth_b(a, detail=False):
    """See the module docstring."""
    rng = random.Random(3512)
    F._footing(a, rng, 7.0, [(x, s * ROW_Y, .32) for x in PICKETS for s in (-1, 1)])
    h = 1.02
    for x in PICKETS:
        for s in (-1, 1):
            _picket(a, x + rng.uniform(-.03, .03), s * ROW_Y, h, (s * .03, rng.uniform(-.02, .02)))
    # The three coils: front and rear base coils outside the picket rows, the top coil in the cradle above.
    rb, rt = .37, .3
    _coil(a, -(ROW_Y + rb * .55), TOP + rb * .8, rb, phase=.0)
    _coil(a, ROW_Y + rb * .55, TOP + rb * .8, rb, phase=1.3)
    _coil(a, 0.0, TOP + h - .13, rt, phase=2.4)
    # Barbed strands along both rows (bottom and top), with their barbs every 0.25 m.
    strand = a.part('Barbed_wire', 'Steel')
    barbs = a.part('Barbs', 'Steel')
    for s in (-1, 1):
        for z in (.3, .95):
            yy = s * (ROW_Y + .035)
            strand.tube([(-2.5, yy, TOP + z), (2.5, yy, TOP + z)], .008, seg=3, caps=False)
            for j in range(10):
                x = -2.25 + j * .5
                barbs.box((.008, .05, .008), loc=(x, yy, TOP + z), rot=(.7 if j % 2 else -.7, 0, 0), bevel=0)
    # Wire clips tying the coils to the pickets (short loops at each picket).
    clips = a.part('Wire_clips', 'Steel')
    for x in PICKETS:
        for s in (-1, 1):
            clips.torus(.05, .008, loc=(x, s * (ROW_Y + .06), TOP + .3), rot=(R90, 0, 0), seg=6, ring=3)
            clips.torus(.05, .008, loc=(x, s * (ROW_Y - .02), TOP + h - .1), rot=(R90, 0, 0), seg=6, ring=3)
    # Short anchor pickets at the two ends, angled out, with the guy wires to the picket tops.
    for x0, sx in ((-2.38, -1), (2.38, 1)):
        for s in (-1, 1):
            ax, ay = x0, s * (ROW_Y + .35)
            a.part('Anchor_pickets', 'Rust').cyl(.022, .45, loc=(ax, ay, TOP + .1), rot=(-s * .45, sx * .45, 0),
                                                 seg=5, bevel=0)
            px = PICKETS[0] if sx < 0 else PICKETS[-1]
            strand.tube([(ax + sx * .08, ay + s * .08, TOP + .28), (px, s * ROW_Y, TOP + h - .08)], .008, seg=3,
                        caps=False)
    # Warning tags and the tin-can rattles on the top strands; the wire spool and gloves on the footing.
    for x, s in ((-1.25, -1), (1.25, 1), (0.0, -1)):
        k.block(a.part('Warning_tags', 'Hazard'), (.3, .012, .2), loc=(x, s * (ROW_Y + .06), TOP + .78), chamfer=0)
        a.part('Warning_marks', 'PlasterWhite').box((.06, .006, .14), loc=(x, s * (ROW_Y + .067), TOP + .78),
                                                    bevel=0)
    cans = a.part('Alarm_cans', 'MetalSheet')
    for x, s in ((-.95, 1), (-.35, -1), (.95, -1), (1.55, 1)):
        yy = s * (ROW_Y + .035)
        cans.cyl(.04, .1, loc=(x, yy, TOP + .95 - .1), seg=7, bevel=0)
        strand.tube([(x, yy, TOP + .95), (x, yy, TOP + .9)], .004, seg=3, caps=False)
    sx, sy = -1.25, -.95
    k.lathe(a.part('Wire_spool', 'Wood'), [(0, -.22), (.26, -.22), (.26, -.18), (.13, -.18), (.13, .18), (.26, .18),
                                           (.26, .22), (0, .22)], loc=(sx, sy, .29), rot=(0, R90, .3), seg=12, worn=(1, 2, 5, 6))
    k.lathe(a.part('Wire_spool', 'Rust'), [(.13, -.17), (.21, -.16), (.22, .0), (.21, .16), (.13, .17)],
            loc=(sx, sy, .29), rot=(0, R90, .3), seg=12, caps=(False, False), worn=(1, 2, 3))
    strand.tube([(sx + .05, sy - .2, .45), (sx + .5, sy - .05, .05), (sx + 1.0, sy + .1, .06)], .008, seg=3)
    gl = a.part('Gloves', 'Canvas')
    for dx in (0, .14):
        k.block(gl, (.1, .2, .04), loc=(1.75 + dx, -.9, .06), rot=(0, 0, .5 + dx * 3), chamfer=.012)
    # Marker stakes at the two ends (the family's: Team band, a white reflector).
    for x, y, yaw in ((2.38, 1.0, .3), (-2.38, -1.0, -.4)):
        rot = (.03, -.02, yaw)
        a.part('Stakes', 'Wood').box((.06, .06, 1.2), loc=(x, y, .6), rot=rot, bevel=0)
        k.block(a.part('Stake_bands', 'Team'), (.13, .13, .26), loc=(x, y, .94), rot=rot, chamfer=.03)
        k.block(a.part('Stake_bands', 'Team'), (.13, .13, .06), loc=(x, y, 1.2), rot=rot, chamfer=.02)
        a.part('Stake_reflectors', 'PlasterWhite').box((.075, .075, .06), loc=(x, y, .84), rot=rot, bevel=0)
    # Rust bleeding onto the spine under the pickets.
    stain = a.part('Rust_stains', 'Dirt')
    for x in PICKETS:
        stain.box((.3, .2, .006), loc=(x + .05, -ROW_Y + .12, TOP + .003), rot=(0, 0, x), bevel=0)
    K.dust(a, (0, 0, -.6), radius=1.0, k=.1)
    k.clean(a)


BUILDERS = {
    'dragons_teeth_b': (dragons_teeth_b, dict(ao_distance=.5, grime_height=.4, ao_strength=.5)),
}
