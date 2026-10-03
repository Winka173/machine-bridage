"""Prompt 35 wave 1, lane B: small parametric helpers for the lane's vehicle builders (DECISIONS "Prompt 35 wave 1
(lane B)").

Not a model: generic, parametric sub-assemblies only (prompt 35 section 1 allows a component library), each called
with the model's own sizes. Bodies, cabs, hulls, turrets, wings stay in each model's own script (mb_p35_<id>.py).

* raised_gun: a roof-mounted machine gun that stands clear of the roof line (owner, pilot review 2026-10-03,
  MODEL_STANDARD "Roof guns"): the ring or pedestal riser, the yaw pivot, the pintle post, the cradle, the receiver
  with its feed cover and spade grips, the barrel with carrying handle and flash hider, the ammunition can on its
  tray, the gun shield. Its runtime names are the caller's (Turret / Main_cannon / Muzzle_brake / Muzzle_main for a
  main-weapon gun; Mount_mg / Muzzle_mg for a free secondary).
* tarp_bows: a canvas cover over a cargo bed on bows, with tie-down ropes and sag between the bows.
* mudflap, step, fuel_tank, toolbox: truck furniture with real sizes.

Conventions: frontier_kit's (metres, +Z up, -Y the front, +X the left side).
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


def raised_gun(a, loc, parent=None, pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake', muzzle='Muzzle_main',
               riser=.16, ring_r=.42, post=.3, length=1.25, shield=True, ring=True, mat='Armor', tag='', shield_k=1.0):
    """A 12.7 mm class gun on a raised roof ring (ring=True: an M66-style ring on a riser collar) or a pedestal
    (ring=False). loc is the roof point under it; the yaw pivot `pivot` sits on top of the riser. Returns the pivot.
    The barrel points to -Y (forward) at rest."""
    x, y, z = loc
    base = a.part(f'Gun_ring{tag}', mat, parent)
    steel = a.part(f'Gun_ring_fit{tag}', 'Steel', parent)
    if ring:
        # The riser collar on the roof hatch, the ring rail on top and its support brackets.
        k.ring(base, [(ring_r * .8, 0), (ring_r * .92, 0), (ring_r * .92, riser * .7), (ring_r * .86, riser),
                      (ring_r * .8, riser)], loc=loc, seg=12, worn=(3,))
        k.ring(steel, [(ring_r * .95, riser - .015), (ring_r * 1.02, riser - .015), (ring_r * 1.02, riser + .025),
                       (ring_r * .95, riser + .025)], loc=loc, seg=12)
        for i in range(4):
            u = i * TAU / 4 + TAU / 8
            steel.box((.03, .05, riser * .9), loc=(x + math.cos(u) * ring_r * .97, y + math.sin(u) * ring_r * .97,
                                                   z + riser * .45), rot=(0, 0, u), bevel=0)
    else:
        k.lathe(base, [(ring_r * .55, 0), (ring_r * .55, .04), (ring_r * .25, .07), (ring_r * .2, riser)], loc=loc,
                seg=10, worn=(1,))
    p = a.pivot(pivot, (x, y, z + riser + .02), parent)
    # Traverse carriage: on a ring a slide arm runs from the rail to the centre post.
    car = a.part(f'Gun_carriage{tag}', 'Steel', p)
    if ring:
        car.box((.1, ring_r * .95, .05), loc=(0, ring_r * .48, .03), bevel=0)
        car.box((.14, .1, .08), loc=(0, ring_r * .95, .03), bevel=0)
    k.lathe(car, [(.06, 0), (.06, .04), (.04, .07), (.035, post)], seg=8, worn=(1,))
    # Cradle (yoke) carrying the gun.
    cr = a.part(f'Cradle{tag}', mat, p)
    for s in (-1, 1):
        k.block(cr, (.03, .16, .14), loc=(s * .085, 0, post - .02), chamfer=0)
    cr.box((.2, .12, .03), loc=(0, 0, post - .04), bevel=0)
    zg = post + .1
    # Receiver: the long box with the sloped feed cover, the back plate with spade grips and the butterfly trigger.
    rc = a.part(f'Receiver{tag}', 'Undercarriage', p)
    k.extrude(rc, [(-.24, -.06), (.2, -.06), (.22, .04), (.08, .07), (-.24, .06)], .13, loc=(0, 0, zg), axis='X',
              chamfer=.01, corner=.01)
    for s in (-1, 1):
        rc.limb((s * .045, .22, zg + .02), (s * .06, .32, zg - .04), .025, .025, bevel=0)
    # Barrel: the perforated jacket, the barrel, the carrying handle and the flash hider.
    bp = a.part(barrel, 'Steel', p)
    front = -.24
    L = length
    k.lathe(bp, [(.042, 0), (.042, .26), (.03, .3), (.022, L - .1), (0, L - .1)], loc=(0, front, zg), rot=K.FORWARD,
            seg=8, worn=(1,))
    K.handle(bp, (0, front - .3, zg + .04), (0, front - .48, zg + .04), (0, 0, 1), h=.05, r=.01)
    k.lathe(a.part(brake, 'Undercarriage', p), [(.022, L - .12), (.036, L - .1), (.036, L - .01), (.026, L),
                                               (.018, L), (.018, L - .04), (0, L - .04)], loc=(0, front, zg),
            rot=K.FORWARD, seg=8, worn=(1,))
    # Ammunition can on its tray on the gun's left, the belt into the feed.
    am = a.part(f'Ammo_can{tag}', 'Crate', p)
    k.block(am, (.12, .3, .2), loc=(.16, .02, zg - .14), chamfer=.012)
    am.box((.13, .31, .025), loc=(.16, .02, zg - .03), bevel=0)
    steel2 = a.part(f'Gun_fit{tag}', 'Steel', p)
    steel2.box((.16, .32, .02), loc=(.16, .02, zg - .25), bevel=0)
    steel2.tube([(.1, .02, zg - .03), (.07, .0, zg + .03), (.05, -.02, zg + .03)], .012, seg=4)
    if shield:
        sh = a.part(f'Gun_shield{tag}', mat, p)
        q = shield_k
        k.extrude(sh, [(-.36 * q, -.18 * q), (.36 * q, -.18 * q), (.32 * q, .26 * q), (.08, .3 * q), (-.08, .3 * q),
                       (-.32 * q, .26 * q)], .025,
                  loc=(0, -.42, zg - .02), rot=(R90 - .1, 0, 0), axis='Z', chamfer=.008, corner=.01)
        for s in (-1, 1):
            k.extrude(sh, [(-.14 * q, -.16 * q), (.14 * q, -.16 * q), (.12 * q, .2 * q), (-.12 * q, .2 * q)], .02,
                      loc=(s * (.07 + .36 * q), -.33, zg - .02),
                      rot=(R90, 0, s * .55), axis='Z', chamfer=.006, corner=0)
            steel2.tube([(s * .2, -.4, zg - .14), (s * .08, -.05, post - .06)], .012, seg=4)
    a.pivot(muzzle, (0, front - L - .005, zg), p)
    return p


def tarp_bows(a, y0, y1, half_w, z_rail, z_top, bows=5, parent=None, sag=.035, mat='Canvas', tag='', hoops=True,
              steps=4):
    """A canvas cover from y0 to y1 over a bed whose side rails are at z_rail, half_w out: rounded shoulders, the
    roof sagging between the bows, the hoops of the bows standing proud, tie ropes down the sides."""
    tarp = a.part(f'Tarp{tag}', mat, parent)
    sh = min(.18, (z_top - z_rail) * .35)

    def section(yy, dz):
        pts = [(-half_w, z_rail), (-half_w, z_top - sh), (-half_w + sh * .3, z_top - sh * .3),
               (-half_w + sh, z_top - dz), (half_w - sh, z_top - dz), (half_w - sh * .3, z_top - sh * .3),
               (half_w, z_top - sh), (half_w, z_rail)]
        return [(x, yy, z) for x, z in pts]
    n = max(2, bows - 1)
    rings = []
    for i in range(n * steps + 1):
        f = i / (n * steps)
        yy = y0 + (y1 - y0) * f
        ph = (i % steps) / steps
        rings.append(section(yy, sag * math.sin(math.pi * ph)))
    tarp.loft(rings, bevel=0)          # the loft closes both ends (the curtains) and the floor
    # Bow hoops showing through the canvas, and the ropes down the sides.
    hoop = a.part(f'Tarp_bows{tag}', 'Undercarriage', parent) if hoops else None
    rope = a.part(f'Kit_straps{tag}', 'Steel', parent)
    for i in range(bows):
        yy = y0 + (y1 - y0) * i / (bows - 1)
        sec = section(yy, -.012)
        if hoops:
            hoop.tube([(x * 1.008, yy, z) for x, _, z in sec[1:-1]], .018, seg=4)
        for s in (-1, 1):
            rope.tube([(s * (half_w + .012), yy + .12, z_top - sh - .05), (s * (half_w + .012), yy + .1, z_rail + .02)],
                      .008, seg=3)
    return tarp


def mudflap(a, loc, w=.42, h=.38, parent=None):
    x, y, z = loc
    a.part('Mudflaps', 'Rubber', parent).box((w, .02, h), loc=(x, y, z - h / 2), bevel=0)
    a.part('Kit_hooks', 'Steel', parent).box((w + .04, .04, .04), loc=(x, y - .02, z + .01), bevel=0)


def step(a, loc, w=.42, d=.2, parent=None):
    """A truck boarding step: a chequer tread plate on two hangers."""
    x, y, z = loc
    st = a.part('Steps', 'Steel', parent)
    k.block(st, (w, d, .03), loc=(x, y, z), chamfer=0)
    for dy in (-d * .35, d * .35):
        st.box((.015, .03, .02), loc=(x, y + dy, z + .03), bevel=0)


def fuel_tank(a, loc, length, r, axis_y=True, parent=None, mat='Armor', straps=2):
    """A cylindrical side fuel tank lying along Y with its filler cap and steel straps."""
    rot = K.FORWARD if axis_y else (0, R90, 0)
    x, y, z = loc
    k.lathe(a.part('Fuel_tanks', mat, parent), [(r * .8, -length / 2), (r, -length / 2 + .03), (r, length / 2 - .03),
                                                 (r * .8, length / 2)], loc=loc, rot=rot, seg=12, worn=(1, 2))
    st = a.part('Kit_straps', 'Steel', parent)
    for i in range(straps):
        f = -0.5 + (i + 1) / (straps + 1)
        st.cyl(r * 1.03, .04, loc=(x, y + f * length, z), rot=rot, seg=12, bevel=0)
    a.part('Fuel_caps', 'Steel', parent).cyl(r * .22, .05, loc=(x, y - length * .32, z + r), seg=8, bevel=0)


def toolbox(a, loc, size, parent=None, mat='Armor'):
    """A chassis-mounted lockable box: the box, its lid seam, two latches."""
    x, y, z = loc
    w, d, h = size
    K.chamfer_box(a.part('Toolbox', mat, parent), size, loc=loc, c=.015)
    st = a.part('Kit_latches', 'Steel', parent)
    s = 1 if x >= 0 else -1
    for dy in (-d * .25, d * .25):
        st.box((.015, .04, .06), loc=(x + s * (w / 2 + .005), y + dy, z + h * .2), bevel=0)
    st.box((.008, d * .95, .012), loc=(x + s * (w / 2 + .002), y, z + h * .32), bevel=0)


def tread_wheel(a, centre, r, width, s, seg=14, depth=None, parent=None, tyre='Tyres', rim='Wheels', rim_mat='Steel',
                hub=True, nuts=0, dish=.6, rim_seg=8):
    """A lean military tyre on an axle along X, outer face on side s (about 300 triangles): the casing's tread rows
    are staggered in radius vertex by vertex, so a chevron lug pattern reads in the silhouette without lug boxes; a
    dished rim with its flange, the hub boss and (nuts > 0) wheel nuts. For vehicles with many wheels."""
    import bmesh
    from mathutils import Vector
    w = width
    ld = depth if depth is not None else r * .07
    R = r - ld
    # The inner face (towards the hull) ends at the sidewall's bulge: it is never seen.
    prof = [(R * .9, -w / 2), (R, -w / 2 + w * .12), (r, -w / 2 + w * .3),
            (r, w / 2 - w * .3), (R, w / 2 - w * .12), (R * .9, w / 2), (r * .62, w / 2 - .012)]
    sh = a.part(tyre, 'Rubber', parent)
    bm = sh.bm
    rows = []
    for j, (rr, z) in enumerate(prof):
        row = []
        for i in range(seg):
            u = i * TAU / seg
            q = rr
            if j in (2, 3):                    # the tread: lug and groove alternate, offset between the two rows
                q = r if (i + j) % 2 == 0 else R + ld * .5
            row.append(bm.verts.new((q * math.cos(u), q * math.sin(u), z)))
        rows.append(row)
    faces = []
    for ra, rb in zip(rows, rows[1:]):
        faces += [bm.faces.new((ra[i], ra[(i + 1) % seg], rb[(i + 1) % seg], rb[i])) for i in range(seg)]
    faces.append(bm.faces.new(list(reversed(rows[0]))))
    faces.append(bm.faces.new(rows[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    k._wear(sh, rows[1] + rows[4])
    rot = (0, s * R90, 0)
    bmesh.ops.transform(bm, matrix=k._frame(centre, rot), verts=[v for row in rows for v in row])
    f = w / 2
    k.lathe(a.part(rim, rim_mat, parent), [(r * .64, f + .012), (r * .57, f + .016),
                                           (r * .5, f - .05 * dish / .6), (r * .22, f - .06 * dish / .6),
                                           (0, f - .06 * dish / .6)], loc=centre, rot=rot, seg=rim_seg, worn=(0,))
    m = K.frame(centre, rot)
    if hub:
        k.lathe(a.part('Hubs', 'Steel', parent), [(r * .13, f), (r * .1, f + .05), (0, f + .065)], loc=centre, rot=rot,
                seg=6)
    if nuts:
        nut = a.part('Wheel_nuts', 'Steel', parent)
        for i in range(nuts):
            u = i * TAU / nuts
            p = m @ Vector((r * .3 * math.cos(u), r * .3 * math.sin(u), f - .03))
            nut.cyl(r * .03 + .004, .03, loc=tuple(p), rot=rot, seg=5, bevel=0)


def ammo_box(a, loc, size=(.5, .3, .26), rot=(0, 0, 0), parent=None, part='Ammo_boxes', mat='Crate'):
    """An olive ammunition box (M2A1 can class) standing on loc: the body, its lid lip and the latch (lean)."""
    import mb_kit35 as K35
    w, d, h = size
    m = K35.frame(loc, rot)
    p = a.part(part, mat, parent)
    k.block(p, (w, d, h * .86), loc=K35._at(m, (0, 0, h * .43)), rot=rot, chamfer=.012)
    p.box((w * .98, d * .96, h * .14), loc=K35._at(m, (0, 0, h * .92)), rot=rot, bevel=0)
    a.part('Kit_latches', 'Steel', parent).box((.05, d + .016, .05), loc=K35._at(m, (w * .3, 0, h * .8)), rot=rot,
                                                bevel=0)


def leaf_pack(part, x, y, z, length, leaves=3, w=.08):
    """A lean leaf-spring pack along Y (stacked leaves, the centre clamp): springs hidden behind wheels."""
    for i in range(leaves):
        part.box((w, length * (1 - i * .2), .02), loc=(x, y, z - i * .022), bevel=0)
    part.box((w * 1.3, .1, .08), loc=(x, y, z - leaves * .011), bevel=0)


def canvas_roll(a, loc, length, r=.1, parent=None, mat='Canvas'):
    """A rolled-up tarpaulin edge lying along X with two tie bands."""
    x, y, z = loc
    k.lathe(a.part('Tarp_roll', mat, parent), [(r * .8, -length / 2), (r, -length / 2 + .03), (r, length / 2 - .03),
                                               (r * .8, length / 2)], loc=loc, rot=(0, R90, 0), seg=8)
    for f in (-.3, .3):
        a.part('Kit_straps', 'Steel', parent).box((.04, r * 2.1, r * 2.1), loc=(x + f * length, y, z), bevel=0)
