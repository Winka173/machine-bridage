"""Prompt 35 wave 1 (lane B): the VBIED rebuilt from scratch (spec: Tools/blender/specs/vbied.json).

An "Iron Coffin" of Mosul 2016-17 (the def's modelSize 4.58 x 1.68 x 1.6 m): a civilian double-cab pickup all but
hidden under welded steel plate. Faceted plates cover the bonnet, the cab (a raked front plate with two narrow vision
slits, tumblehome sides with slits) and the load bed (a sealed charge box with its loading hatch); a thicker ram
plate stands across the front; skirt plates hang down over the top half of the wheels; patch plates of other steel
(bare sheet, rusted, painted) are welded over the seams at odd angles, with weld beads along the joints; the
detonation cable runs from the charge box to the cab; a spare wheel is chained to the tailgate.

Runtime nodes kept: `Turret` (the roof hatch with its periscope: kamikaze, mainAim Hull), `Muzzle_main` (the front),
`Point_exhaust`, `Point_fire`; mb_p34_parts adds the wreck wheels (`Part_wheel`, `Part_wheelb`).
Plates are slabs through their corner points (cut by hand, not chamfered: torch-cut plate). Fixed seed.
Metres, +Z up, -Y front, +X left.
"""
import math
import random

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .34, .24, .66
AXLES = (-1.32, 1.36)
LOW = .32           # bottom edge of the skirt plates
BELT = .95          # top of the vertical side plates
X0, XR = .8, .6     # half width at the belt and at the roof
FRONT, REAR = -2.29, 2.29


def slab(part, corners, t=.03, jitter=0.0, rng=None):
    """A torch-cut plate through `corners` (3D, in order), `t` thick along the inward normal; jitter moves the
    corners a little in the plate's plane (irregular cut edges)."""
    c = [Vector(p) for p in corners]
    n = Vector((0, 0, 0))
    for i in range(len(c)):                            # Newell's normal
        a, b = c[i], c[(i + 1) % len(c)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    n.normalize()
    if jitter and rng is not None:
        out = []
        for p in c:
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
            d -= n * d.dot(n)
            out.append(p + d * jitter)
        c = out
    m = len(c)
    verts = [tuple(p) for p in c] + [tuple(p - n * t) for p in c]
    faces = [tuple(range(m)), tuple(reversed(range(m, 2 * m)))]
    faces += [(i, m + i, m + (i + 1) % m, (i + 1) % m) for i in range(m)]
    part.mesh(verts, faces)
    return n


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        frame.box((.08, 4.1, .14), loc=(s * .38, 0, .42), bevel=0)
    for y in (-1.8, -.3, 1.0, 2.0):
        frame.box((.7, .07, .07), loc=(0, y, .42), bevel=0)
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8, nuts=5)
            K.dust(a, (s * TRACK, y, .1), radius=.8, k=.3)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, TRACK - .06, r=.045, diff=True)
    susp = a.part('Suspension', 'Steel')
    for s in (-1, 1):
        P.leaf_pack(susp, s * .38, AXLES[1], WR + .1, .95, leaves=4, w=.06)
        susp.tube([(s * .45, AXLES[0], WR + .02), (s * .42, AXLES[0] - .05, WR + .3)], .025, seg=6)
    K.exhaust(a, (-.45, REAR - .1, .3), r=.03, length=.18, direction=(0, 1, 0), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-.45, REAR + .1, .3))
    a.pivot('Point_fire', (0, 1.2, 1.25))


def _side_top(y):
    """The top of the vertical side plates along the length (bonnet, cab belt, charge box)."""
    if y < -1.02:
        return .86 + (y - FRONT - .1) / (-1.02 - FRONT - .1) * (BELT - .86)
    return BELT if y < .44 else BELT - .05 * (y - .44) / (REAR - .44)


def _armour(a, rng):
    body = a.part('Body', 'MetalSheet')                 # bare torch-cut steel
    sheet = a.part('Plates_Armor', 'Armor')            # painted plate taken off something else
    rust = a.part('Plates_Rust', 'Rust')
    team = a.part('Plates_Team', 'Team')
    welds = a.part('Kit_welds', 'Steel')
    bolts = a.part('Kit_bolts', 'Steel')
    J = .045
    # The ram: a thick slab across the front, stiffening ribs, three I-beam stubs standing out as teeth.
    ram = a.part('Ram_plate', 'Armor')
    slab(ram, [(-X0 - .03, FRONT, LOW - .04), (X0 + .03, FRONT, LOW - .04), (X0 + .03, FRONT + .04, .86),
               (-X0 - .03, FRONT + .04, .86)], t=.09)
    for z in (.45, .7):
        ram.box((1.62, .05, .06), loc=(0, FRONT - .02, z), bevel=0)
    for x in (-.55, 0, .55):
        ram.box((.1, .1, .1), loc=(x, FRONT - .07, .5), bevel=0)
        ram.box((.03, .1, .2), loc=(x, FRONT - .07, .5), bevel=0)
    # Side plates: separate torch-cut panels, alternately standing proud, a straight lower edge over the wheels
    # (the wheel's lower half shows), down to the skirt line between them.
    panels = [(FRONT + .1, -1.8, LOW), (-1.8, -.84, .55), (-.84, .02, LOW), (.02, .86, LOW), (.86, 1.86, .55),
              (1.86, REAR, LOW)]
    mats = [body, rust, sheet, body, rust, body]
    for s in (-1, 1):
        for i, (y0, y1, z0) in enumerate(panels):
            x = s * (X0 + (.045 if (i + (s > 0)) % 2 else 0))
            q = [(x, y0 + .01, z0), (x, y1 - .01, z0), (x, y1 - .01, _side_top(y1)), (x, y0 + .01, _side_top(y0))]
            part = mats[(i + (s > 0) * 3) % len(mats)]
            slab(part, q if s > 0 else list(reversed(q)), jitter=J, rng=rng)
            K.rivet_line(bolts, (x + s * .012, y0 + .08, z0 + .06), (x + s * .012, y1 - .08, z0 + .06), (s, 0, 0),
                         pitch=.24, r=.014, h=.016)
    # The bonnet: a sloped plate from the ram up to the windscreen foot.
    yb, zb = -1.02, 1.02
    slab(body, [(-X0, FRONT + .1, .86), (X0, FRONT + .1, .86), (.7, yb, zb), (-.7, yb, zb)], jitter=J, rng=rng)
    # The cab: raked front plate, flat roof, tumblehome upper sides from the belt.
    yr, ycb = -.62, .44
    slab(body, [(-.7, yb, zb), (.7, yb, zb), (XR, yr, 1.5), (-XR, yr, 1.5)])
    slab(body, [(-XR, yr, 1.5), (XR, yr, 1.5), (XR, ycb, 1.5), (-XR, ycb, 1.5)], jitter=J, rng=rng)
    for s in (-1, 1):
        upper = [(s * X0, yb, BELT), (s * X0, ycb, BELT), (s * XR, ycb, 1.5), (s * XR, yr, 1.5), (s * .7, yb, zb)]
        slab(body, upper if s > 0 else list(reversed(upper)), jitter=J, rng=rng)
    # The charge box: sloped shoulders, a lower roof falling to the rear, the back plate.
    yt, ze0, ze1 = REAR - .1, 1.32, 1.2
    for s in (-1, 1):
        q = [(s * X0, ycb + .02, BELT), (s * X0, REAR, BELT - .05), (s * .64, yt, ze1), (s * .64, ycb + .02, ze0)]
        slab(body, q if s > 0 else list(reversed(q)), jitter=J, rng=rng)
    slab(body, [(-.64, ycb, ze0), (.64, ycb, ze0), (.64, yt, ze1), (-.64, yt, ze1)], jitter=J, rng=rng)
    slab(body, [(X0, REAR, LOW), (-X0, REAR, LOW), (-X0, REAR, BELT - .05), (-.64, yt, ze1), (.64, yt, ze1),
                (X0, REAR, BELT - .05)])
    # The cab's back wall where it stands over the box roof.
    slab(body, [(-XR, ycb, 1.5), (XR, ycb, 1.5), (.64, ycb, ze0), (-.64, ycb, ze0)])
    # Patch plates of other steel welded over seams and weak spots at odd angles.
    patches = [
        (rust, [(.83, -1.95, .36), (.83, -1.5, .36), (.83, -1.48, .78), (.83, -1.9, .8)]),
        (team, [(.84, -.7, .45), (.84, .7, .45), (.84, .7, .8), (.84, -.7, .8)]),
        (team, [(-.84, -.6, .45), (-.84, .8, .45), (-.84, .8, .8), (-.84, -.6, .8)]),
        (sheet, [(.3, -.35, 1.515), (.55, -.35, 1.515), (.55, .3, 1.515), (.25, .3, 1.515)]),
        (rust, [(-.5, .55, 1.335), (.05, .55, 1.335), (.08, 1.0, 1.31), (-.48, 1.02, 1.31)]),
        (team, [(-.6, -2.0, .9), (.6, -2.0, .9), (.55, -1.5, .96), (-.55, -1.5, .96)]),
        (sheet, [(-.62, -.95, 1.12), (-.12, -.95, 1.12), (-.14, -.75, 1.36), (-.6, -.75, 1.36)]),
    ]
    for part, q in patches:
        n = slab(part, q, t=.022, jitter=.02, rng=rng)
        K.weld(welds, [tuple(Vector(p) + n * .006) for p in q[:2]], r=.012)
        K.weld(welds, [tuple(Vector(p) + n * .006) for p in q[2:4]], r=.012)
    for path in ([(-.7, yb, zb), (.7, yb, zb)], [(-XR, ycb, 1.5), (XR, ycb, 1.5)],
                 [(X0 + .02, yb, BELT), (X0 + .02, REAR, BELT - .05)],
                 [(-X0 - .02, yb, BELT), (-X0 - .02, REAR, BELT - .05)]):
        K.weld(welds, path, r=.014)
    # A rebar cage over the bonnet and the front plate (against RPGs and to shed grenades).
    cage = a.part('Rebar_cage', 'Rust')
    for x in (-.6, -.3, 0, .3, .6):
        cage.tube([(x, FRONT + .02, .9), (x * .95, -1.1, 1.1), (x * .9, -.75, 1.45)], .014, seg=4)
    for y, z in ((FRONT + .3, .97), (-1.5, 1.04), (-1.05, 1.13)):
        cage.tube([(-.72, y, z), (.72, y, z)], .014, seg=4)
    for x in (-.45, .45):                                       # rebar spikes on the ram
        cage.tube([(x, FRONT, .78), (x, FRONT - .2, .8)], .02, seg=4)


def _slits(a):
    """Vision slits: a dark glass block behind a narrow cut, the cut's frame bars welded round it."""
    glass = a.part('Visors', 'Glass')
    fr = a.part('Slits', 'Steel')
    yb, zb, yr = -1.02, 1.02, -.62
    for x in (-.3, .3):
        # On the raked front plate: the plate rises 0.48 over 0.4 m back.
        z = 1.22
        y = yb + (z - zb) / (1.5 - zb) * (yr - yb)
        rot = (-math.atan2(yr - yb, 1.5 - zb), 0, 0)
        glass.box((.34, .04, .05), loc=(x, y - .005, z), rot=rot, bevel=0)
        for dz in (-.045, .045):
            fr.box((.4, .03, .025), loc=(x, y - .02 + dz * .6, z + dz), rot=rot, bevel=0)
    for s in (-1, 1):
        x = s * (X0 + (XR - X0) * .45)
        rot = (0, s * math.atan2(X0 - XR, 1.5 - BELT), 0)
        glass.box((.03, .3, .05), loc=(x + s * .005, -.55, BELT + .25), rot=rot, bevel=0)
        fr.box((.025, .36, .02), loc=(x + s * .02, -.55, BELT + .29), rot=rot, bevel=0)
    # Headlamps peering through holes in the ram's top corners.
    for s in (-1, 1):
        K.lamp(a, (s * .55, FRONT - .04, .78), (0, -1, 0), r=.055, mat='Undercarriage', guard=False)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .01, .05), loc=(s * .66, REAR + .005, .82), bevel=0)


def _roof(a):
    """The roof hatch on the `Turret` pivot: a ring, the lid propped open a crack, a periscope box."""
    t = a.pivot('Turret', (.0, -.1, 1.5))
    hatch = a.part('Hatch', 'Armor', t)
    k.ring(hatch, [(.28, 0), (.33, 0), (.33, .06), (.28, .06)], seg=12, worn=(2,))
    k.block(hatch, (.5, .5, .04), loc=(0, .05, .12), rot=(.3, 0, 0), chamfer=0)               # lid propped open
    K.hinge(a.part('Kit_hinges', 'Steel', t), (-.15, .3, .07), (.15, .3, .07), r=.02, knuckles=2)
    K.periscope(a, (-.0, -.3, .02), facing=(0, -1, 0), parent=t, size=(.16, .12, .1), mat='Armor')
    a.pivot('Muzzle_main', (0, FRONT - .1, .6))


def _charge_box(a):
    """The bomb compartment's details: the loading hatch, the cable to the cab, the chained spare, sandbags."""
    hz = 1.27
    hatch = a.part('Bed_box', 'Armor')
    slab(hatch, [(-.38, .9, hz + .025), (.38, .9, hz + .025), (.38, 1.6, hz - .02), (-.38, 1.6, hz - .02)], t=.03)
    fit = a.part('Kit_hinges', 'Steel')
    for x in (-.25, .25):
        K.hinge(fit, (x - .08, .88, hz + .02), (x + .08, .88, hz + .02), r=.018, knuckles=2)
    fit.box((.12, .05, .04), loc=(0, 1.62, hz), bevel=0)                                       # padlock hasp
    cab = a.part('Kit_cables', 'Undercarriage')
    cab.tube([(.52, .7, 1.31), (.5, .4, 1.42), (.45, .2, 1.52), (.4, -.4, 1.52)], .018, seg=5)
    cab.tube([(.47, .7, 1.31), (.44, .45, 1.43), (.35, .2, 1.52)], .012, seg=4)
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(.2, -.1), (.3, -.1), (.32, -.06), (.32, .06), (.3, .1), (.2, .1)],
            loc=(.25, 1.25, 1.36), rot=(.06, 0, 0), seg=14)
    a.part('Kit_straps', 'Steel').tube([(.25, .9, 1.33), (.25, 1.25, 1.47), (.25, 1.6, 1.3)], .012, seg=4)
    bags = a.part('Sandbags', 'Sandbag')
    for i, (x, y, rz) in enumerate(((-.35, 1.85, .1), (.0, 1.92, -.05), (.33, 1.86, .12), (-.15, 1.95, .3))):
        z = 1.25 + (.1 if i == 3 else 0)
        k.block(bags, (.42, .24, .1), loc=(x, y, z), rot=(0, 0, rz), chamfer=.03, ends=(True, True))


def vbied(a):
    """The VBIED: see the module docstring."""
    rng = random.Random(3517)
    _running_gear(a)
    _armour(a, rng)
    _slits(a)
    _roof(a)
    _charge_box(a)
    k.clean(a)


BUILDERS = {
    'vbied': (vbied, dict(ao_distance=.4, grime_height=.45)),
}
