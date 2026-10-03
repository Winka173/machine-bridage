"""Prompt 35 wave 11 (lane C): the Bulwark machine-gun post rebuilt from scratch (spec: Tools/blender/specs/bulwark_post.json).

The improvised 12.7 mm post the Bulwark gear leaves when its tower falls (unit_refs: the NSV 12.7 mm, a mushroom
pillbox; the old file's 4.4 x 4.4 x 2.4 m): a low earth berm in a ring, three courses of sandbags on it with the
entry gap at the rear, a duckboard floor, the NSV on its 6T7 tripod (`Turret`: cradle, receiver, ribbed barrel with
its conical flash hider, the bent gun shield, the ammunition box and belt); the "mushroom" cover over it: four timber
posts carrying a low hipped roof of corrugated sheet with sandbags weighing it down; a broken slab of the fallen
tower leaning on the wall with its rebar sticking out; the flag on its pole, the beacon, ready-round boxes, a spare
barrel, casings, helmets and an entrenching tool.

Runtime nodes kept where they were: `Turret` (0, 0, .92), `Muzzle_main` (0, -1.8, 1.16); old mesh names kept
(`Main_cannon`, `Muzzle_brake`, `Gun_shield`, `Flag`, `Flag_pole`, `Beacon`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
RING = 1.78          # the sandbag ring's centre line
BERM = .22


def _ground(a):
    """The berm ring, the floor, the sandbag courses with the rear entry gap."""
    pts = []
    for i in range(18):
        u = i * TAU / 18
        r = 2.12 + .06 * math.sin(3 * u) + .04 * math.cos(5 * u)
        pts.append((math.cos(u) * r, math.sin(u) * r))
    K.earth_pad(a, pts, BERM, part='Berm', mat='Dirt', taper=.9, bottom=False)
    C.duckboard(a, (0, .05, BERM + .01), 1.6, 2.0, planks=9, seed=3, part='Floor_boards')
    path = []
    gap = math.radians(34)                     # the entry at the rear (+Y)
    n = 22
    for i in range(n + 1):
        u = R90 + gap + (TAU - 2 * gap) * i / n
        path.append((math.cos(u) * RING, math.sin(u) * RING, BERM))
    K.sandbag_run(a, path, courses=3, bag=(.56, .3, .15), part='Sandbags', seed=5, lean=True)
    # The entry's end bags, stacked square.
    for s in (-1, 1):
        u = R90 + s * gap
        for c in range(3):
            k.block(a.part('Sandbags', 'Sandbag'), (.3, .52, .14),
                    loc=(math.cos(u) * RING, math.sin(u) * RING + .1, BERM + .07 + c * .135), rot=(0, 0, u),
                    chamfer=.05)


def _gun(a):
    """The NSV on its 6T7 tripod (`Turret` on the cradle)."""
    tri = a.part('Tripod', 'Steel')
    hub = (0, .05, .78)
    for u in (R90 + math.radians(140), R90 - math.radians(140), R90):
        foot = (math.cos(u) * .7, math.sin(u) * .7 + .05, BERM + .02)
        tri.limb(hub, foot, .045, .045, bevel=0)
        tri.box((.14, .08, .03), loc=foot, rot=(0, 0, u), bevel=0)
    k.lathe(tri, [(.07, .7), (.07, .84), (.05, .9), (0, .91)], loc=(0, .05, 0), seg=8, worn=(1,))
    t = a.pivot('Turret', (0, 0, .92))
    cr = a.part('Cradle', 'Armor', t)
    for s in (-1, 1):
        k.block(cr, (.03, .3, .2), loc=(s * .1, 0, 0), chamfer=.008)
    cr.box((.24, .12, .04), loc=(0, 0, 0), bevel=0)
    zg = .24
    rc = a.part('MG_receiver', 'Undercarriage', t)
    k.extrude(rc, [(-.42, -.08), (.3, -.08), (.33, .06), (.1, .1), (-.42, .08)], .16, loc=(0, 0, zg), axis='X',
              chamfer=.012, corner=.012)
    for s in (-1, 1):
        rc.limb((s * .05, .3, zg + .02), (s * .07, .45, zg - .07), .03, .03, bevel=0)
    front = -.42
    bp = a.part('Main_cannon', 'Steel', t)
    L = 1.38 - .02
    k.lathe(bp, [(.055, 0), (.055, .3), (.036, .34), (.03, L - .12), (0, L - .12)], loc=(0, front, zg),
            rot=K.FORWARD, seg=8, worn=(1,))
    for j in range(4):
        bp.cyl(.042, .03, loc=(0, front - .42 - j * .13, zg), rot=K.FORWARD, seg=8, bevel=0)
    K.handle(bp, (0, front - .35, zg + .05), (0, front - .6, zg + .05), (0, 0, 1), h=.06, r=.012)
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.03, L - .14), (.034, L - .13), (.05, L - .01), (0, L)],
            loc=(0, front, zg), rot=K.FORWARD, seg=8, worn=(1,))
    a.pivot('Muzzle_main', (0, -1.8, zg), t)
    am = a.part('Ammo_boxes', 'Crate', t)
    k.block(am, (.16, .36, .24), loc=(.22, .0, zg - .2), chamfer=.015)
    a.part('Gun_bracket', 'Steel', t).box((.2, .38, .025), loc=(.22, 0, zg - .21), bevel=0)
    a.part('Gun_belt', 'Crate', t).tube([(.14, 0, zg + .05), (.09, -.02, zg + .08), (.06, -.04, zg + .05)], .018,
                                        seg=4)
    sh = a.part('Gun_shield', 'Armor', t)
    k.extrude(sh, [(-.42, -.2), (.42, -.2), (.38, .3), (.12, .34), (-.12, .34), (-.38, .3)], .03,
              loc=(0, -.55, zg - .02), rot=(R90 - .1, 0, 0), axis='Z', chamfer=.01, corner=.012)
    for s in (-1, 1):
        k.extrude(sh, [(-.16, -.18), (.16, -.18), (.13, .24), (-.13, .24)], .025, loc=(s * .55, -.44, zg - .02),
                  rot=(R90, 0, s * .55), axis='Z', chamfer=.008)
    K.periscope(a, (-.16, -.06, zg + .13), facing=(0, -1, 0), parent=t, size=(.07, .09, .07))
    K.soot(a, (0, -1.8, 1.16), radius=.3, k=.35)


def _cover(a):
    """Four timber posts, the hipped corrugated roof, sandbags on it, a scrim edge."""
    posts = a.part('Posts', 'LogWood')
    h0, h1 = 1.84, 2.14
    P = 1.18
    for sx in (-1, 1):
        for sy in (-1, 1):
            posts.cyl(.07, h0 - BERM, loc=(sx * P, sy * P, (h0 + BERM) / 2), seg=6, bevel=0)
    for sy in (-1, 1):
        posts.box((2 * P + .3, .14, .14), loc=(0, sy * P, h0 - .05), bevel=0)
    for sx in (-1, 1):
        posts.box((.14, 2 * P + .3, .14), loc=(sx * P, 0, h0 + .07), bevel=0)
    roof = a.part('Roof', 'Corrugated')
    E = P + .16
    verts = [(-E, -E, h0 + .14), (E, -E, h0 + .14), (E, E, h0 + .14), (-E, E, h0 + .14),
             (-.5, 0, h1 + .14), (.5, 0, h1 + .14)]
    top = [(x, y, z + .04) for x, y, z in verts]
    vs = verts + top
    faces = [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)]
    tf = [tuple(i + 6 for i in f) for f in faces]
    roof.mesh(vs, [tuple(reversed(f)) for f in faces] + tf +
              [(0, 1, 7, 6), (1, 2, 8, 7), (2, 3, 9, 8), (3, 0, 6, 9)])
    # The corrugation ribs on the front and rear slopes.
    ribs = a.part('Roof_ribs', 'Corrugated')
    for i in range(9):
        x = -E + .15 + i * (2 * E - .3) / 8
        for sy in (-1, 1):
            p0 = (x, sy * (E - .05), h0 + .2)
            p1 = (x * .9 if abs(x) > .5 else x, sy * .12, h1 + .19)
            ribs.limb(p0, p1, .03, .02, bevel=0)
    bags = a.part('Roof_sandbags', 'Sandbag')
    for x, y, yaw in ((-.7, -.6, .2), (.6, -.7, -.15), (.75, .65, .1), (-.6, .7, -.25), (0, -.35, .05)):
        z = h0 + .2 + (h1 - h0) * (1 - abs(y) / E) + .05
        k.block(bags, (.5, .28, .13), loc=(x, y, z), rot=(math.atan2(-y, 3) * .9, 0, yaw), chamfer=.05)
    nails = a.part('Kit_bolts', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.rivet_line(nails, (sx * P, sy * (E - .1), h0 + .2), (sx * P, sy * (E - .1), h0 + .2), (0, 0, 1), pitch=1,
                         r=.025, h=.02)
    g = a.part('Scrim', 'FoliageDark')
    for i in range(10):
        u = i / 9
        x = -E + 2 * E * u
        g.box((.24, .02, .3), loc=(x, -E - .01, h0 + .02), rot=(.1, 0, (i % 3 - 1) * .1), bevel=0)


def _rubble(a):
    """A broken slab of the fallen tower leaning on the wall, its rebar, two loose blocks."""
    sl = a.part('Rubble', 'Concrete')
    k.extrude(sl, [(-.55, 0), (.6, 0), (.5, .9), (.1, 1.05), (-.45, .8)], .2, loc=(-2.22, .7, BERM - .05),
              rot=(0, .45, 0), axis='X', chamfer=.03, corner=.04)
    rb = a.part('Rebar', 'Rust')
    for i in range(4):
        y = .35 + i * .22
        rb.limb((-1.86, y, BERM + .9), (-1.75 + .05 * (i % 2), y + .05, BERM + 1.3 + .08 * (i % 2)), .02, .02,
                bevel=0)
    for x, y, s in ((1.85, -1.25, .32), (1.95, .75, .26)):
        k.block(sl, (s, s * 1.3, s * .8), loc=(x, y, BERM - .05), rot=(.15, .1, x), chamfer=.04)


def _kit(a):
    """Flag, beacon, ready rounds, a spare barrel, casings, helmets, a shovel."""
    fp = a.part('Flag_pole', 'Steel')
    fp.cyl(.03, 2.2, loc=(1.85, .62, BERM + 1.1 - .05), seg=6, bevel=0)
    fl = a.part('Flag', 'Team')
    verts = []
    for j in range(4):
        y = .62 + .02 + j * .2
        dx = .05 * math.sin(j * 1.6)
        for z in (2.0, 2.38):
            verts.append((1.85 + dx, y, z))
    faces = [(i * 2, i * 2 + 2, i * 2 + 3, i * 2 + 1) for i in range(3)]
    fl.mesh(verts + [(x + .01, y, z) for x, y, z in verts],
            faces + [tuple(reversed([j + 8 for j in f])) for f in faces])
    K.beacon(a, (-1.3, -1.3, BERM + .45 + .02), r=.09)
    a.part('Beacon', 'Steel').box((.18, .18, .45), loc=(-1.3, -1.3, BERM + .22), bevel=0)
    C.ammo_tins(a, (.85, .55, BERM + .02), n=3, size=(.14, .32, .22))
    C.ammo_tins(a, (-.75, .85, BERM + .02), n=2, size=(.14, .32, .22), axis='Y')
    k.lathe(a.part('Spare_barrel', 'Steel'), [(.04, 0), (.04, 1.2), (.03, 1.25), (0, 1.25)], loc=(-.9, -.2,
            BERM + .08), rot=(R90, 0, .4), seg=6)
    C.casings(a, (0, -.3), .5, 14, z=BERM + .02, seed=4)
    C.helmets(a, [(-.55, .45, BERM + .03), (.55, -.1, BERM + .03)])
    C.entrenching_tools(a, (1.25, -.5, BERM), yaw=.6)


def bulwark_post(a, detail=False):
    """The Bulwark machine-gun post: see the module docstring."""
    _ground(a)
    _gun(a)
    _cover(a)
    _rubble(a)
    _kit(a)
    K.dust(a, (0, 0, 0), radius=2.4, k=.16)
    k.clean(a)


BUILDERS = {
    'bulwark_post': (bulwark_post, dict(ao_distance=.5, grime_height=.4)),
}
