"""Prompt 35 wave 11 (lane C): the anti-drone net corridor rebuilt from scratch (spec: Tools/blender/specs/drone_net_tower.json).

A section of the anti-drone net tunnels strung over front-line roads since 2023 (the weapon's `real`: "Anti-drone
net corridor"; the def's modelSize 6.0 x 4.0 x 4.6 m, passable): three pairs of steel poles on concrete footings with
sandbags at their feet, an arch over each pair, purlins along the ridge and shoulders, the net (cords along the
corridor and hoops round each bay) draped over the arches and down both sides, loose strands with weights hanging at
the open ends; the zap emitters on the front and rear apexes (`Turret` / `Muzzle_main` on the front one: a coil
ring, the glowing electrode, its insulators), the cable along the ridge to a generator box on skids with its
exhaust, guy ropes to ground stakes, warning plates and a lamp.

Runtime nodes kept where they were: `Turret` (0, -2.55, 4.2), `Muzzle_main` (0, -2.55, 4.6). Metres, +Z up, -Y front
(the corridor runs along Y), +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
PX = 1.72            # the poles' half spacing across the road
BAYS = (-2.55, 0.0, 2.55)
SHOULDER = 2.95      # where the poles meet the arch
APEX = 4.12


def _arch(t):
    """A point on the arch, t from -1 (left foot of the arch, x = +PX) to 1: (x, z)."""
    u = (t + 1) / 2 * math.pi
    return (PX * math.cos(u), SHOULDER + (APEX - SHOULDER) * math.sin(u))


def _side(t, x_sign):
    """A point of the net on a side wall, t from 0 (the shoulder) to 1 (near the ground)."""
    return (x_sign * (PX + .04), SHOULDER - t * (SHOULDER - .75))


def _frame(a):
    base = a.part('Base', 'Concrete')
    poles = a.part('Poles', 'Steel')
    arch = a.part('Roof_arches', 'Team')
    bolts = a.part('Kit_bolts', 'Steel')
    for y in BAYS:
        for s in (-1, 1):
            x = s * PX
            k.extrude(base, [(-.36, -.36), (.36, -.36), (.36, .36), (-.36, .36)], .32, loc=(x, y, .16), axis='Z',
                      chamfer=.05, corner=.05, taper=(.8, .8))
            for dx, dy in ((-.2, -.2), (.2, .2)):
                K.rivet_line(bolts, (x + dx * .7, y + dy * .7, .32), (x + dx * .7, y + dy * .7, .32), (0, 0, 1),
                             pitch=1, r=.03, h=.04)
            k.lathe(poles, [(.11, .3), (.11, .36), (.08, .4), (.075, SHOULDER), (0, SHOULDER + .02)],
                    loc=(x, y, 0), seg=8, worn=(1,))
            # A knee brace from pole to arch.
            p0 = (x, y, SHOULDER - .55)
            ax, az = _arch(-.72 if s > 0 else .72)
            poles.limb(p0, (ax, y, az), .06, .06, bevel=0)
        pts = [_arch(-1 + 2 * i / 8) for i in range(9)]
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            arch.limb((x0, y, z0), (x1, y, z1), .12, .1, bevel=0)
        # The arch's gusset plates at the shoulders.
        for s in (-1, 1):
            k.extrude(arch, [(0, 0), (.0, .32), (-.28, 0)], .02, loc=(s * (PX - .04), y, SHOULDER),
                      rot=(R90, 0, 0 if s > 0 else math.pi), axis='Z')
    # Purlins along the ridge and the shoulders.
    pur = a.part('Purlins', 'Steel')
    for t in (-1, -.5, 0, .5, 1):
        x, z = _arch(t)
        pur.limb((x, BAYS[0] - .1, z + .05), (x, BAYS[-1] + .1, z + .05), .06, .06, bevel=0)
    # Sandbags at the poles' feet.
    for y in BAYS:
        for s in (-1, 1):
            d = -1 if y > 0 else 1
            path = [(s * PX, y + d * .4, 0), (s * PX, y + d * 1.0, 0)]
            K.sandbag_run(a, path, courses=2, bag=(.5, .28, .14), part='Sandbags', seed=int(y * 10) + s, lean=True)


def _net(a):
    """Cords along the corridor over the arch and down the sides; hoops round each bay; loose ends."""
    net = a.part('Net', 'Canvas')
    y0, y1 = BAYS[0] - .05, BAYS[-1] + .05
    # Cords along Y at 13 arch stations and four side heights each side.
    for i in range(13):
        x, z = _arch(-1 + 2 * i / 12)
        sag = .08 * (1 - abs(-1 + 2 * i / 12))
        net.tube([(x, y0, z + .07), (x, (y0 + BAYS[1]) / 2, z + .07 - sag), (x, BAYS[1], z + .07),
                  (x, (BAYS[1] + y1) / 2, z + .07 - sag), (x, y1, z + .07)], .018, seg=3, caps=False)
    for s in (-1, 1):
        for j in range(1, 5):
            x, z = _side(j / 4.6, s)
            net.tube([(x, y0, z), (x + s * .04, 0, z - .05), (x, y1, z)], .018, seg=3, caps=False)
    # Hoops: one every 0.42 m along the corridor, over the arch and down both sides.
    n = 13
    for j in range(n):
        y = y0 + (y1 - y0) * j / (n - 1)
        pts = [(PX + .04, y, .75), (PX + .06, y, 1.8)]
        pts += [(x, y, z + .07) for x, z in (_arch(-1 + 2 * i / 8) for i in range(9))]
        pts += [(-PX - .06, y, 1.8), (-PX - .04, y, .75)]
        net.tube(pts, .016, seg=3, caps=False)
    # Loose strands hanging at the open ends, with weights.
    hang = a.part('Net_strands', 'Canvas')
    wts = a.part('Net_weights', 'Hazard')
    for y, sy in ((y0, -1), (y1, 1)):
        for i in range(5):
            x, z = _arch(-.8 + 1.6 * i / 4)
            drop = .5 + .25 * (i % 2)
            hang.tube([(x, y, z), (x, y + sy * .08, z - drop * .6), (x, y + sy * .04, z - drop)], .015, seg=3,
                      caps=False)
            wts.cyl(.05, .1, loc=(x, y + sy * .04, z - drop - .05), seg=5, bevel=0)


def _emitters(a):
    """The zap emitters on the apexes (the front one is the weapon pivot), the ridge cable."""
    def emitter(parent, loc, tag):
        x, y, z = loc
        k.lathe(a.part('Emitter_base' + tag, 'Armor', parent), [(.2, 0), (.2, .06), (.1, .1), (.1, .14)], loc=loc,
                seg=10, worn=(1,))
        ins = a.part('Insulators' + tag, 'Plaster', parent)
        for s in (-1, 1):
            for j in range(3):
                ins.cyl(.07, .03, loc=(x + s * .14, y, z + .14 + j * .05), seg=7, bevel=0)
            ins.cyl(.025, .2, loc=(x + s * .14, y, z + .2), seg=5, bevel=0)
        k.ring(a.part('Emitter_ring' + tag, 'Team', parent), [(.2, -.03), (.26, -.03), (.26, .03), (.2, .03)],
               loc=(x, y, z + .32), seg=12, worn=(1, 2))
        a.part('Emitter_ball' + tag, 'Energy', parent).sphere(.12, loc=(x, y, z + .32), seg=10, rings=6)
        sp = a.part('Emitter_spikes' + tag, 'Steel', parent)
        for i in range(6):
            u = i * TAU / 6
            sp.limb((x + math.cos(u) * .12, y + math.sin(u) * .12, z + .32),
                    (x + math.cos(u) * .3, y + math.sin(u) * .3, z + .3), .015, .015, bevel=0)
    t = a.pivot('Turret', (0, BAYS[0], 4.2))
    emitter(t, (0, 0, -.06), '')
    a.pivot('Muzzle_main', (0, 0, .4), t)
    emitter(None, (0, BAYS[-1], 4.14), '2')
    cab = a.part('Kit_cables', 'Rubber')
    cab.tube([(0, BAYS[0] + .15, APEX + .14), (0, BAYS[1], APEX + .12), (0, BAYS[-1] - .15, APEX + .14)], .025, seg=4)
    cab.tube([(PX - .1, BAYS[-1] - .3, SHOULDER - .1), (PX - .12, BAYS[-1] - .3, .9),
              (PX - .4, BAYS[-1] - .6, .1), (PX - .5, BAYS[-1] - .85, .3)], .025, seg=4)
    cab.tube([(0, BAYS[-1] - .15, APEX + .12), (PX * .7, BAYS[-1] - .2, APEX - .3), (PX - .1, BAYS[-1] - .3,
              SHOULDER - .1)], .025, seg=4)
    K.lamp(a, (-PX - .1, BAYS[0], SHOULDER - .3), (0, -1, -.2), r=.08, guard=True)


def _ground(a):
    """Generator box on skids, guy ropes and stakes, warning plates."""
    gx, gy = PX - .5, BAYS[-1] - 1.25
    gen = a.part('Generator', 'Team')
    k.block(gen, (.5, .8, .45), loc=(gx, gy, .325), chamfer=.04)
    k.extrude(gen, [(-.4, 0), (.4, 0), (.3, .12), (-.3, .12)], .5, loc=(gx, gy, .55), axis='X', chamfer=.01)
    sk = a.part('Skids', 'Steel')
    for s in (-1, 1):
        sk.box((.06, .95, .1), loc=(gx + s * .2, gy, .05), bevel=0)
    K.grille(a, (gx - .26, gy, .32), .5, .22, facing=(-1, 0, 0), slats=5)
    K.exhaust(a, (gx + .15, gy + .3, .67), r=.035, length=.3, direction=(0, 0, 1), muffler=False)
    K.handle(a.part('Kit_handles', 'Steel'), (gx, gy - .2, .69), (gx, gy + .2, .69), (0, 0, 1), h=.06)
    gu = a.part('Guy_ropes', 'Rubber')
    st = a.part('Stakes', 'Steel')
    for y in (BAYS[0], BAYS[-1]):
        for s in (-1, 1):
            top = (s * PX, y, SHOULDER - .1)
            foot = (s * (PX + .3), y + (-1.2 if y < 0 else 1.2) * .35, 0)
            gu.tube([top, foot], .012, seg=3)
            st.box((.04, .04, .25), loc=(foot[0], foot[1], .08), rot=(0, s * .3, 0), bevel=0)
    pl = a.part('Warning_plates', 'Hazard')
    for s in (-1, 1):
        k.block(pl, (.02, .45, .3), loc=(s * (PX + .1), BAYS[0] + .25, 1.5), chamfer=0)
    a.part('Kit_steel', 'Steel').box((.02, .05, .4), loc=(-PX - .12, BAYS[0] + .25, 1.3), bevel=0)


def drone_net_tower(a, detail=False):
    """The anti-drone net corridor: see the module docstring."""
    _frame(a)
    _net(a)
    _emitters(a)
    _ground(a)
    K.dust(a, (0, 0, 0), radius=3.0, k=.14)
    k.clean(a)


BUILDERS = {
    'drone_net_tower': (drone_net_tower, dict(ao_distance=.5, grime_height=.4)),
}
