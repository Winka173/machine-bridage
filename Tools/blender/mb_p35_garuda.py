"""Prompt 35 wave 6 (lane B): Garuda, the giant flying-wing bomber, rebuilt from scratch (spec: Tools/blender/specs/garuda.json).

Quaden's Garuda (variant of command_airship with all its parts; BossText: a huge flying wing with defensive turrets,
escorted, a carpet of bombs; tip: break the bomb bay and the carpet is gone, the engines slow it down). A B-2 / B-21
flying wing drawn 1.3-1.5 x up for a boss (the def's modelSize 27.9 x 70 x 4.5 m): one airfoil loft from tip to tip
along the straight swept leading edge and the double-W sawtooth trailing edge, the blended centre body with the
cockpit hump and its four-pane windscreen, the elevons and drag rudders along the trailing edge; the four buried
engines (`Part_engine` inner left, `.001` inner right, `.002` / `.003` outer: the weak points the tip names, riveted
and one shade off) with their serrated dorsal intakes and the exhaust troughs over the wing; under the belly the
two bomb bay doors (`Part_bay`, `Part_bay.001`) with the carpet load racked inside, the two drone bays
(`Part_hangar` > `Muzzle_door_l`, `Part_hangar.001` > `Muzzle_door_r`) with their doors and launch rails, the nose
radar panel (`Part_radar`); the defensive turrets: twin 30 mm dorsal turrets (`Mount_gun`, `.001`: one muzzle a
barrel), the 105 mm pods under the outer wing (`Mount_gun.002`, `.003`: parts pod_105_l / _r), two fixed tail
barbettes; radar-absorbent edge bands and seam tape, the wingtip lights, Quaden's colour bands. Jet rule: no insets
or panel greebles on the skin (the tape and bands are paint).

Its own wing (not stealth_bomber's or stealth_naval_strike's). Runtime nodes kept: every `Part_*`, `Mount_*` and
`Muzzle_*` of the old model at its old place; new: `Muzzle_b1_gun` / `_b2_gun` and `_gun_001` (the twin barrels'
own launch points; the def's eight mounts want eight muzzles). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
APEX = -13.9
SPAN = 35.0
TE = [(0.0, 13.9), (8.5, 6.0), (17.0, 12.5), (25.0, 4.5), (35.0, 11.0)]


def le_y(x):
    return APEX + abs(x) * (22.6 / SPAN)


def te_y(x):
    x = abs(x)
    for (x0, y0), (x1, y1) in zip(TE, TE[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return TE[-1][1]


def thick(x):
    """Thickness / chord: the deep centre section thinning to the tips."""
    return .1 - .055 * min(1.0, abs(x) / SPAN)


def top_z(x, y):
    le, te = le_y(x), te_y(x)
    chord = te - le
    u = min(1.0, max(0.0, (y - le) / chord))
    pts = ((0, 0), (.2, .55), (.45, 1.0), (.675, .8), (1.0, 0))
    for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
        if u <= u1:
            return (v0 + (v1 - v0) * (u - u0) / (u1 - u0)) * thick(x) * chord * .5
    return 0.0


def _wing(a):
    w = a.part('Wing', 'Team')
    xs = [-35.0, -32.5, -30.0, -27.5, -25.0, -23.0, -21.0, -19.0, -17.0, -14.8, -12.5, -10.5, -8.5, -6.2, -4.0, -2.0,
          0.0, 2.0, 4.0, 6.2, 8.5, 10.5, 12.5, 14.8, 17.0, 19.0, 21.0, 23.0, 25.0, 27.5, 30.0, 32.5, 35.0]
    rings = [K._foil_ring(le_y(x), te_y(x) - le_y(x), thick(x), x, 0.0) for x in xs]
    w.loft(rings, bevel=0)
    # Elevons and drag rudders along the trailing edge's outer legs (paint seams and a split), the tip caps.
    seam = a.part('Elevon_seams', 'Undercarriage')
    for s in (-1, 1):
        for x0, x1 in ((18.0, 24.0), (26.0, 30.5), (31.0, 34.5)):
            for f in (.0, 1.0):
                xx = x0 + (x1 - x0) * f
                y = te_y(xx)
                seam.box((.08, 1.6, .03), loc=(s * xx, y - .8, top_z(xx, y - .8) + .02), bevel=0)
            xm = (x0 + x1) / 2
            ym = te_y(xm) - 1.6
            seam.box((x1 - x0, .08, .03), loc=(s * xm, ym, top_z(xm, ym) + .02),
                     rot=(0, 0, math.atan2(te_y(x1) - te_y(x0), x1 - x0) * s), bevel=0)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.25, .5, .15), loc=(s * 34.7, 9.5, 0),
                                                                          bevel=0)


def _body(a):
    """The blended centre body (fuselage) with the cockpit hump and windscreen."""
    body = a.part('Fuselage', 'Team')
    rings = [[(0, APEX + .1, .1)]]
    for y, w, top, bot in ((-12.5, 1.6, .8, -.4), (-10.5, 2.8, 1.6, -.6), (-8.0, 3.6, 2.1, -.8), (-4.0, 4.2, 1.9, -.9),
                           (1.0, 4.4, 1.3, -.9), (6.0, 4.0, 1.0, -.8), (10.0, 3.2, .7, -.6), (13.4, 2.0, .35, -.3)):
        rings.append([(-w, y, .05), (-w * .6, y, top * .85), (0, y, top), (w * .6, y, top * .85), (w, y, .05),
                      (w * .6, y, bot * .85), (0, y, bot), (-w * .6, y, bot * .85)])
    k.sharp_loft(body, rings, chamfer=.04)
    glass = a.part('Cockpit_glass', 'Glass')
    for i, x in enumerate((-1.1, -.37, .37, 1.1)):
        glass.mesh([(x - .34, -10.7, 1.6), (x + .34, -10.7, 1.6), (x + .3, -9.7, 1.98), (x - .3, -9.7, 1.98)],
                   [(0, 1, 2, 3)])
    a.part('Canopy_frames', 'Armor').box((2.9, .08, .06), loc=(0, -10.2, 1.8), rot=(.36, 0, 0), bevel=0)


def _engines(a):
    """The four buried engines (`Part_engine` .. `.003`): dorsal serrated intakes, riveted covers, exhaust troughs."""
    for i, (x, y, z) in enumerate(((4.0, -1.5, 1.64), (-4.0, -1.5, 1.64), (7.6, .5, 1.13), (-7.6, .5, 1.13))):
        part = K.name('Part_engine', i)
        p = a.pivot(part, (x, y, z))
        sfx = f'_{i}'
        hump = a.part('Engine_cover' + sfx, 'Team', p)
        hump.loft([[(0, -2.6, -.35)], [(-1.0, -1.4, -.4), (1.0, -1.4, -.4), (.8, -1.4, .75), (-.8, -1.4, .75)],
                   [(-1.2, 1.5, -.5), (1.2, 1.5, -.5), (1.0, 1.5, .6), (-1.0, 1.5, .6)],
                   [(-1.1, 3.8, -.6), (1.1, 3.8, -.6), (.9, 3.8, 0), (-.9, 3.8, 0)]])
        intake = a.part('Intakes' + sfx, 'Undercarriage', p)
        intake.mesh([(-.9, -1.42, -.35), (.9, -1.42, -.35), (.7, -1.42, .7), (0, -1.6, .62), (-.7, -1.42, .7)],
                    [(0, 1, 2, 3, 4)])
        teeth = a.part('Intake_lips' + sfx, 'Armor', p)
        for t in (-.55, -.2, .2, .55):
            teeth.box((.25, .06, .06), loc=(t, -1.48, .73), rot=(0, 0, .5 if t > 0 else -.5), bevel=0)
        rv = a.part('Kit_rivets', 'Steel', p)
        for dx in (-.75, .75):
            for dy in (-.8, .4, 1.6, 2.8):
                rv.box((.1, .1, .05), loc=(dx * (1 - .1 * dy / 2.8), dy, .1 - .2 * dy / 3.6), bevel=0)
        K.tone(a, part, k=.84)
    for x in (4.0, -4.0, 7.6, -7.6):
        y0 = 2.6 if abs(x) < 5 else 4.6
        y1 = te_y(x) - .2
        k.extrude(a.part('Exhaust_trough', 'Undercarriage'), [(-.75, 0), (.75, 0), (.65, .12), (-.65, .12)], y1 - y0,
                  loc=(x, (y0 + y1) / 2, top_z(x, (y0 + y1) / 2) - .02), axis='Y', chamfer=.02)
        a.part('Exhaust_glow', 'LavaGlow').box((1.2, .05, .08), loc=(x, y1 + .02, top_z(x, y1) + .06), bevel=0)
        K.soot(a, (x, y1, .2), radius=2.0, k=.3)
    a.pivot('Point_exhaust', (4.0, 8.0, .4))
    a.pivot('Point_fire', (0, 0, 1.5))


def _bays(a):
    """Bomb bays (`Part_bay` / `.001`), drone bays (`Part_hangar` / `.001` with their door muzzles), the radar."""
    for i, s in enumerate((1, -1)):
        part = K.name('Part_bay', i)
        p = a.pivot(part, (s * .62, -3.0, -.93))
        d = a.part('Bay_doors' + ('' if i == 0 else '_r'), 'Armor', p)
        k.block(d, (1.1, 6.0, .08), loc=(s * .05, 2.4, .0), chamfer=.02)
        rv = a.part('Kit_rivets', 'Steel', p)
        for dy in (0.0, 1.6, 3.2, 4.8):
            rv.box((.08, .08, .04), loc=(s * .5, dy - .3, -.05), bevel=0)
        a.part('Bay_bands', 'Hazard', p).box((1.0, .1, .02), loc=(s * .05, -.55, -.05), bevel=0)
        K.tone(a, part, k=.86)
    # The carpet load racked between the doors (bomb noses showing at the bay's gap).
    bombs = a.part('Bomb_racks', 'Undercarriage')
    for j in range(5):
        bombs.box((.35, .9, .25), loc=(0, -2.5 + j * 1.15, -.95), bevel=0)
    for i, (s, door) in enumerate(((1, 'Muzzle_door_l'), (-1, 'Muzzle_door_r'))):
        part = K.name('Part_hangar', i)
        p = a.pivot(part, (s * 4.2, 0, -.57))
        k.block(a.part('Hangar_doors' + ('' if i == 0 else '_r'), 'Armor', p), (2.0, 4.6, .1), loc=(0, .2, -.22),
                chamfer=.03)
        a.part('Hangar_seam' + ('' if i == 0 else '_r'), 'Undercarriage', p).box((.06, 4.6, .02), loc=(0, .2, -.28),
                                                                                  bevel=0)
        rails = a.part('Launch_rails' + ('' if i == 0 else '_r'), 'Steel', p)
        for dx in (-.6, .6):
            rails.box((.1, 4.0, .1), loc=(dx, .2, -.32), bevel=0)
        a.pivot(door, (0, 0, -.3), p)
        K.tone(a, part, k=.88)
    p = a.pivot('Part_radar', (0, -9.0, -.78))
    k.block(a.part('Radar_panel', 'Undercarriage', p), (2.4, 1.6, .06), loc=(0, 0, .0), chamfer=.02)
    a.part('Radar_frame', 'Steel', p).box((2.6, .08, .05), loc=(0, -.85, .0), bevel=0)
    K.tone(a, 'Part_radar', k=.9)


def _turrets(a):
    """Twin 30 mm dorsal turrets (`Mount_gun`, `.001`), the 105 mm pods (`Mount_gun.002`, `.003`), tail barbettes."""
    for i, x in enumerate((10.0, -10.0)):
        m = a.pivot(K.name('Mount_gun', i), (x, -1.0, 1.25))
        sfx = '' if i == 0 else '_001'
        k.lathe(a.part('Turret_ring' + sfx, 'Steel', m), [(.85, -1.0), (.85, -.1), (.75, .05), (.65, .12), (0, .12)], seg=14)
        K.beacon(a, (0, .9, .1), parent=m, r=.08)
        k.lathe(a.part('Turret_dome' + sfx, 'Armor', m), [(.7, 0), (.7, .35), (.62, .7), (.4, .95), (0, 1.05)], seg=14,
                worn=(1, 2))
        for dx in (-.18, .18):
            k.lathe(a.part('Gun_barrels' + sfx, 'Steel', m), [(.06, 0), (.06, .5), (.04, .55), (.035, 2.6), (0, 2.6)],
                    loc=(dx, -.55, .33), rot=K.FORWARD, seg=6)
        muzzle = K.name('Muzzle_gun', i)
        a.pivot(muzzle, (0, -3.2, .33), m)
        tag = 'gun' if i == 0 else 'gun_001'
        for b, dx in ((1, -.18), (2, .18)):
            a.pivot(f'Muzzle_b{b}_{tag}', (dx, 0, 0), muzzle)
        a.part('Turret_glass' + sfx, 'Glass', m).box((.3, .02, .14), loc=(.35, -.62, .36), bevel=0)
    for i, x in enumerate((14.5, -14.5)):
        m = a.pivot(K.name('Mount_gun', i + 2), (x, 0.0, -1.14))
        sfx = '_002' if i == 0 else '_003'
        k.block(a.part('Pod_pylon' + sfx, 'Armor', m), (.4, 2.2, .6), loc=(0, .3, .25), chamfer=.04)
        k.lathe(a.part('Gun_pod' + sfx, 'Armor', m), [(0, -1.6), (.45, -1.2), (.55, 0), (.5, 1.4), (.3, 2.0)],
                loc=(0, .2, -.1), rot=K.BACKWARD, seg=12, worn=(2,))
        k.lathe(a.part('Pod_barrel' + sfx, 'Steel', m), [(.12, 0), (.12, .3), (.09, .35), (.08, 2.3), (0, 2.3)],
                loc=(0, -1.5, -.05), rot=K.FORWARD, seg=8)
        a.pivot(K.name('Muzzle_gun', i + 2), (0, -3.85, -.05), m)
    bar = a.part('Tail_barbettes', 'Armor')
    for s in (-1, 1):
        k.lathe(bar, [(.4, 0), (.38, .2), (.25, .45), (0, .5)], loc=(s * 2.2, 12.6, .15), seg=10)
        a.part('Barbette_guns', 'Steel').cyl(.05, 1.2, loc=(s * 2.2, 13.2, .4), rot=K.BACKWARD, seg=6, bevel=0)


def _paint(a):
    """Radar-absorbent bands along the leading edge, seam tape across the wing, Quaden's colour bands (paint)."""
    ram = a.part('Ram_edges', 'Undercarriage')
    tape = a.part('Ram_tape', 'Armor')
    for s in (-1, 1):
        for i in range(12):
            xa, xb = 4.5 + i * 2.5, 4.5 + (i + 1) * 2.5
            ya, yb = le_y(xa), le_y(xb)
            za, zb = top_z(xa, ya + .9) + .03, top_z(xb, yb + .9) + .03
            ram.mesh([(s * xa, ya + .3, za * .7), (s * xb, yb + .3, zb * .7), (s * xb, yb + 1.3, zb), (s * xa, ya + 1.3, za)],
                     [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        for i in range(10):
            x = s * (6.0 + i * 2.8)
            y0, y1 = le_y(x) + 1.6, te_y(x) - 1.0
            n = 12
            for j in range(n):
                ya, yb = y0 + (y1 - y0) * j / n, y0 + (y1 - y0) * (j + 1) / n
                za, zb = top_z(x, ya) + .09, top_z(x, yb) + .09
                tape.mesh([(x - .06, ya, za), (x + .06, ya, za), (x + .06, yb, zb), (x - .06, yb, zb)], [(0, 1, 2, 3)])
        for f in (.2, .35, .5, .65, .8):
            n = 24
            for j in range(n):
                xa, xb = 5.0 + 28.0 * j / n, 5.0 + 28.0 * (j + 1) / n
                ya = le_y(xa) + f * (te_y(xa) - le_y(xa))
                yb = le_y(xb) + f * (te_y(xb) - le_y(xb))
                tape.mesh([(s * xa, ya - .06, top_z(xa, ya) + .09), (s * xb, yb - .06, top_z(xb, yb) + .09),
                           (s * xb, yb + .06, top_z(xb, yb) + .09), (s * xa, ya + .06, top_z(xa, ya) + .09)],
                          [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        a.part('Team_band', 'Team').box((3.0, 1.2, .03), loc=(s * 28.0, 7.0, top_z(28.0, 7.0) + .05),
                                        rot=(0, 0, s * .1), bevel=0)


def _details(a):
    """Denser seam tape, sawtooth access panel outlines, warning lights, rivet rows along the body's armour."""
    tape = a.part('Ram_tape', 'Armor')
    for s in (-1, 1):
        for i in range(20):
            x = s * (5.2 + i * 1.45)
            y0, y1 = le_y(x) + 1.0, te_y(x) - .6
            n = 14
            for j in range(n):
                ya, yb = y0 + (y1 - y0) * j / n, y0 + (y1 - y0) * (j + 1) / n
                tape.mesh([(x - .06, ya, top_z(x, ya) + .09), (x + .06, ya, top_z(x, ya) + .09),
                           (x + .06, yb, top_z(x, yb) + .09), (x - .06, yb, top_z(x, yb) + .09)], [(0, 1, 2, 3)])
    saw = a.part('Panel_lines', 'Undercarriage')
    for s in (-1, 1):
        for (xc, yc, w, d) in ((6.0, -3.5, 2.0, 2.4), (11.0, .5, 1.8, 2.0), (15.0, 3.5, 1.6, 1.8), (20.0, 6.0, 1.6, 1.6),
                               (13.0, -4.5, 1.4, 1.4), (24.0, 2.5, 1.4, 1.4), (28.0, 6.5, 1.2, 1.2)):
            z = top_z(xc, yc) + .09
            for kk in range(4):
                x0 = xc - w / 2 + kk * w / 4
                saw.mesh([(s * x0, yc - d / 2, z), (s * (x0 + w / 8), yc - d / 2 - .2, z), (s * (x0 + w / 4), yc - d / 2, z),
                          (s * (x0 + w / 4), yc - d / 2 + .06, z), (s * x0, yc - d / 2 + .06, z)],
                         [(0, 1, 2, 3, 4) if s > 0 else (4, 3, 2, 1, 0)])
            for xx in (xc - w / 2, xc + w / 2):
                saw.box((.06, d, .02), loc=(s * xx, yc, z), bevel=0)
            saw.box((w, .06, .02), loc=(s * xc, yc + d / 2, z), bevel=0)
    for x, y, z in ((0, -6.0, 2.05), (0, 4.0, 1.4), (2.6, 9.0, .8), (-2.6, 9.0, .8)):
        K.beacon(a, (x, y, z), r=.12)
    rv = a.part('Body_rivets', 'Steel')
    for s in (-1, 1):
        for i in range(14):
            y = -9.0 + i * 1.5
            rv.box((.1, .1, .05), loc=(s * 3.0, y, .9 + .6 * math.cos((y + 4.0) / 10.0)), bevel=0)


def _ram_panels(a):
    """Radar-absorbent panel patches a shade apart on the upper skin (the stealth skin's patchwork, paint)."""
    import random
    rng = random.Random(91)
    pan = a.part('Ram_panels', 'Concrete')
    for s in (-1, 1):
        for i in range(16):
            x0 = 5.6 + i * 1.8
            le, te = le_y(x0), te_y(x0)
            for f in (.12, .3, .48, .66):
                if rng.random() < .35:
                    continue
                w, d = 1.2 + .1 * rng.randint(0, 4), (te - le) * (.1 + .02 * rng.randint(0, 3))
                xa, ya = x0, le + f * (te - le)
                quads = []
                for (u0, u1) in ((0, .5), (.5, 1)):
                    for (v0, v1) in ((0, .5), (.5, 1)):
                        pts = [(xa + w * u0, ya + d * v0), (xa + w * u1, ya + d * v0), (xa + w * u1, ya + d * v1),
                               (xa + w * u0, ya + d * v1)]
                        quads.append([(s * px, py, top_z(px, py) + .07) for px, py in pts])
                for q in quads:
                    pan.mesh(q if s > 0 else list(reversed(q)), [(0, 1, 2, 3)])


def garuda(a):
    """Garuda: see the module docstring."""
    K.suffixed(a)
    _wing(a)
    _body(a)
    _engines(a)
    _bays(a)
    _turrets(a)
    _paint(a)
    _details(a)
    _ram_panels(a)
    k.clean(a)


BUILDERS = {
    'garuda': (garuda, dict(ao_distance=1.2, ground=False)),
}
