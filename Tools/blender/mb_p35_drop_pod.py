"""Prompt 35 wave 11 (lane C): the orbital drop pod rebuilt from scratch (spec: Tools/blender/specs/drop_pod.json).

A one-vehicle orbital insertion pod standing on its heat shield (unit_refs: the Soyuz descent module's retro-rocket
landing, the ODST / Warhammer 40,000 drop pods; the old file's 3.2 x 3.2 x 6.3 m): the charred ablative heat shield
with its scorched rim, the eight-sided lower body with the ablative tile courses and their seams, the cone of the
upper body, the six retro-rockets round the skirt with their glowing throats and soot, four crush legs with pads,
four stabiliser fins on struts, the side hatch with its hinges and seam, the access panels, the RCS thruster quads,
the porthole, the lifting eyes, the drogue canister at the nose with the beacon and two whips, the team stripe.

Runtime nodes: none (the old file had no pivots); the old mesh names are kept (`Hull`, `Heat_shield`, `Stripe`,
`Seams`, `Rivets`, `Access_hatch`, `Retro_ring`, `Retro_glow`, `Fin_struts`, `Fins`, `Hatch`, `Hatch_seam`,
`Beacon`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
SIDES = 8
# The body's profile (radius, z): the skirt, the tile courses, the shoulder, the cone, the nose ring.
S = .88   # the radii below are drawn at 1.0 and scaled to keep the old file's 3.2 m width
PROFILE = [(r * S, z) for r, z in ((1.42, .38), (1.52, .55), (1.5, 1.1), (1.46, 2.0), (1.4, 2.6), (1.22, 3.3),
                                   (.92, 4.3), (.62, 5.05), (.55, 5.12))]


def _r_at(z):
    """The body's (flat-face) radius at height z."""
    for (r0, z0), (r1, z1) in zip(PROFILE, PROFILE[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return PROFILE[-1][0]


def _ap(z):
    """The apothem (centre to the middle of a flat face) at height z; faces centre on the 45-degree marks."""
    return _r_at(z) * math.cos(math.pi / SIDES)


def _face(u):
    """Unit normal of the body face whose centre is at angle u (multiples of 45 degrees)."""
    return (math.cos(u), math.sin(u), 0.0)


def _body(a):
    hull = a.part('Hull', 'Armor')
    k.lathe(hull, PROFILE, rot=(0, 0, math.pi / SIDES), seg=SIDES, worn=(1, 4, 7))
    # Heat shield: a dished ablative base, charred, a rim ring proud of the skirt.
    hs = a.part('Heat_shield', 'Charred')
    k.lathe(hs, [(0, 0), (.9 * S, .03), (1.35 * S, .12), (1.5 * S, .26), (1.48 * S, .4)], seg=16, worn=(3,))
    k.ring(a.part('Heat_shield_rim', 'Steel'), [(1.47 * S, .36), (1.58 * S, .38), (1.58 * S, .5), (1.47 * S, .52)], seg=16,
           worn=(2,))
    # Tile courses: a raised band at each course line, the seams between the tiles of each face.
    seams = a.part('Seams', 'Undercarriage')
    for z in (1.1, 2.0, 2.6):
        r = _r_at(z)
        k.ring(seams, [(r - .02, z - .03), (r + .025, z - .03), (r + .025, z + .03), (r - .02, z + .03)],
               rot=(0, 0, math.pi / SIDES), seg=SIDES)
    for i in range(SIDES):
        u = (i + .5) * TAU / SIDES
        for z0, z1 in ((.6, 1.05), (1.15, 1.95), (2.05, 2.55)):
            zc = (z0 + z1) / 2
            rc = _r_at(zc) + .012
            seams.box((.025, .025, z1 - z0), loc=(math.cos(u) * rc, math.sin(u) * rc, zc), rot=(0, 0, u), bevel=0)
    # Rivet rows along the octagon's edges on the lower body.
    rv = a.part('Rivets', 'Steel')
    for i in range(SIDES):
        u = i * TAU / SIDES
        c, s = math.cos(u), math.sin(u)
        for off in (-.26,):
            K.rivet_line(rv, (c * (_ap(.7) + .005) - s * off, s * (_ap(.7) + .005) + c * off, .7),
                         (c * (_ap(2.5) + .005) - s * off, s * (_ap(2.5) + .005) + c * off, 2.5), _face(u), pitch=.55,
                         r=.022, seg=5)
    # The team stripe round the shoulder.
    st = a.part('Stripe', 'Team')
    r = _r_at(2.95)
    k.ring(st, [(r - .03, 2.8), (r + .02, 2.8), (r + .02, 3.05), (r - .06, 3.05)], rot=(0, 0, math.pi / SIDES),
           seg=SIDES)


def _retros(a):
    """Six retro-rockets round the skirt, canted out and down, with the glowing throats and the soot."""
    ring = a.part('Retro_ring', 'Steel')
    glow = a.part('Retro_glow', 'Energy')
    k.ring(ring, [(1.5 * S, .6), (1.64 * S, .6), (1.64 * S, .78), (1.5 * S, .8)], seg=24, worn=(1, 2))
    for i in range(6):
        u = i * TAU / 6 + TAU / 12
        c, s = math.cos(u), math.sin(u)
        loc = (c * 1.68 * S, s * 1.68 * S, .66)
        # Each nozzle points down and out: rotate the bell's +Z to (out .35, down 1).
        rot = K.rot_to((c * .35, s * .35, -1.0))
        k.lathe(ring, [(.12, .16), (.13, .02), (.18, -.12), (.2, -.16), (.17, -.16), (.1, -.02), (0, .0)],
                loc=loc, rot=rot, seg=10, worn=(3,))
        glow.cyl(.15, .01, loc=K._at(K.frame(loc, rot), (0, 0, -.15)), rot=rot, seg=10, bevel=0)
        ring.box((.16, .12, .22), loc=(c * 1.58 * S, s * 1.58 * S, .74), rot=(0, 0, u), bevel=0)
        K.soot(a, (c * 1.75 * S, s * 1.75 * S, .45), radius=.45, k=.4)


def _legs(a):
    """Four crush legs between the retro-rockets: strut, shock cylinder, pad."""
    legs = a.part('Legs', 'Steel')
    pads = a.part('Pads', 'Undercarriage')
    for i in range(4):
        u = i * TAU / 4 + TAU / 8
        c, s = math.cos(u), math.sin(u)
        top = (c * 1.45 * S, s * 1.45 * S, 1.35)
        foot = (c * 1.85 * S, s * 1.85 * S, .1)
        legs.limb(top, foot, .1, .1, bevel=0)
        legs.limb((c * 1.5 * S, s * 1.5 * S, .55), (c * 1.78 * S, s * 1.78 * S, .4), .07, .07, bevel=0)
        k.lathe(legs, [(.075, 0), (.075, .55), (0, .56)], loc=(c * 1.6 * S, s * 1.6 * S, .95),
                rot=K.rot_to((c * .4, s * .4, -1.0)), seg=8)
        k.lathe(pads, [(0, 0), (.24, 0), (.26, .05), (.18, .1), (0, .11)], loc=foot, seg=10, worn=(2,))


def _fins(a):
    """Four stabiliser fins on the cone, each on two struts."""
    fins = a.part('Fins', 'Team')
    struts = a.part('Fin_struts', 'Steel')
    for i in range(4):
        u = i * TAU / 4
        c, s = math.cos(u), math.sin(u)
        r0 = _ap(3.6)
        prof = [(0, 3.2), (.62, 3.35), (.62, 4.0), (0, 4.45)]
        verts = []
        for t in (-.04, .04):
            for d, z in prof:
                rr = r0 + .18 + d
                verts.append((c * rr - s * t, s * rr + c * t, z))
        fins.mesh(verts, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
        for z in (3.45, 4.0):
            rr = _ap(z)
            struts.limb((c * (rr - .02), s * (rr - .02), z), (c * (r0 + .22), s * (r0 + .22), z), .06, .05, bevel=0)
        K.rivet_line(a.part('Rivets', 'Steel'), (c * (r0 + .45) - s * .045, s * (r0 + .45) + c * .045, 3.4),
                     (c * (r0 + .45) - s * .045, s * (r0 + .45) + c * .045, 3.95), (-s, c, 0), pitch=.27, r=.016, seg=5)


def _hatch(a):
    """The side hatch on the front face, its seam and hinges; two access panels and the porthole."""
    u = -R90                            # the face looking forward (-Y)
    n = (math.cos(u), math.sin(u), 0)
    r = _ap(1.6)
    loc = (n[0] * (r + .005), n[1] * (r + .005), 1.6)
    rot = K.rot_to(n)
    m = K.frame(loc, rot)
    hatch = a.part('Hatch', 'Armor')
    K.plate(hatch, (.95, 1.25, .05), loc=K._at(m, (0, 0, .02)), rot=rot)
    k.block(hatch, (.7, .95, .03), loc=K._at(m, (0, 0, .05)), rot=rot, chamfer=.01)
    seam = a.part('Hatch_seam', 'Undercarriage')
    for (x0, y0), (x1, y1) in (((-.5, -.65), (.5, -.65)), ((.5, -.65), (.5, .65)), ((.5, .65), (-.5, .65)),
                               ((-.5, .65), (-.5, -.65))):
        p0, p1 = K._at(m, (x0, y0, .02)), K._at(m, (x1, y1, .02))
        seam.limb(p0, p1, .03, .03, bevel=0)
    fit = a.part('Kit_hinges', 'Steel')
    for y in (-.35, .35):
        K.hinge(fit, K._at(m, (.52, y - .1, .04)), K._at(m, (.52, y + .1, .04)), r=.03, knuckles=3)
    K.handle(a.part('Kit_handles', 'Steel'), K._at(m, (-.35, -.12, .07)), K._at(m, (-.35, .12, .07)), n, h=.06)
    # Explosive-bolt heads round the hatch.
    bolts = a.part('Kit_bolts', 'Steel')
    for x, y in ((-.45, -.6), (.45, -.6), (.45, .6), (-.45, .6), (0, -.6), (0, .6)):
        K.rivet_line(bolts, K._at(m, (x, y, .05)), K._at(m, (x, y, .05)), n, pitch=1, r=.03, h=.03)
    # Access panels on two side faces.
    acc = a.part('Access_hatch', 'Steel')
    for u2, z in ((R90 * 0, 1.55), (math.pi, 1.55), (R90, 2.3)):
        n2 = (math.cos(u2), math.sin(u2), 0)
        r2 = _ap(z)
        K.panel(a, acc, (.55, .45), (n2[0] * (r2 + .003), n2[1] * (r2 + .003), z), n2, t=.03, rivet=.2)
    # The porthole above the hatch.
    zp = 3.05 + .3
    rp = _ap(zp)
    tilt = math.atan2(_ap(zp - .2) - _ap(zp + .2), .4)
    np_ = (0, -math.cos(tilt), math.sin(tilt))
    lp = (0, -(rp + .01), zp)
    k.ring(a.part('Port_rim', 'Steel'), [(.17, -.01), (.23, -.01), (.23, .05), (.17, .06)], loc=lp,
           rot=K.rot_to(np_), seg=12, worn=(2,))
    a.part('Glass', 'Glass').cyl(.18, .03, loc=lp, rot=K.rot_to(np_), seg=12, bevel=0)


def _nose(a):
    """The drogue canister, its cap, the beacon, two whips, the lifting eyes and the RCS quads."""
    can = a.part('Drogue_canister', 'Steel')
    k.lathe(can, [(.5, 5.08), (.5, 5.5), (.46, 5.6), (.3, 5.66), (0, 5.67)], seg=14, worn=(1, 3))
    k.ring(a.part('Canister_bands', 'Team'), [(.49, 5.25), (.52, 5.25), (.52, 5.33), (.49, 5.33)], seg=14)
    bolts = a.part('Kit_bolts', 'Steel')
    K.bolt_ring(bolts, (0, 0, 5.67), (0, 0, 1), .22, 6, r=.025)
    K.beacon(a, (0, 0, 5.66), r=.11)
    a.part('Beacon', 'Lamp').cyl(.06, .05, loc=(0, 0, 5.98), seg=8, bevel=0)
    ant = a.part('Antennas', 'Steel')
    K.whip_antenna(ant, (.36, .2, 5.6), h=.65, r=.022, lean=.1)
    K.whip_antenna(ant, (-.36, -.2, 5.6), h=.45, r=.022, lean=-.1)
    eyes = a.part('Lift_eyes', 'Steel')
    for i in range(3):
        u = i * TAU / 3 + .3
        c, s = math.cos(u), math.sin(u)
        k.ring(eyes, [(.07, -.02), (.1, -.02), (.1, .02), (.07, .02)], loc=(c * .58, s * .58, 5.16),
               rot=(R90, 0, u + R90), seg=8)
    rcs = a.part('Rcs_quads', 'Undercarriage')
    for i in range(4):
        u = i * TAU / 4 + TAU / 8
        c, s = math.cos(u), math.sin(u)
        z = 4.05
        r = _ap(z) + .06
        rcs.box((.2, .2, .2), loc=(c * r, s * r, z), rot=(0, 0, u), bevel=0)
        for d in ((0, 0, 1), (0, 0, -1), (-s, c, 0), (s, -c, 0)):
            p = (c * r + d[0] * .12, s * r + d[1] * .12, z + d[2] * .12)
            k.lathe(rcs, [(.03, 0), (.05, .06), (.04, .06)], loc=p, rot=K.rot_to(d), seg=5, caps=(False, True))
        K.soot(a, (c * (r + .1), s * (r + .1), z), radius=.25, k=.25)


def drop_pod(a, detail=False):
    """The orbital drop pod: see the module docstring."""
    _body(a)
    _retros(a)
    _legs(a)
    _fins(a)
    _hatch(a)
    _nose(a)
    K.soot(a, (0, 0, 0), radius=1.8, k=.35)
    K.dust(a, (0, 0, .1), radius=2.2, k=.15)
    k.clean(a)


BUILDERS = {
    'drop_pod': (drop_pod, dict(ao_distance=.5, grime_height=.6)),
}
