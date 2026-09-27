"""Machine Brigade Siege-mode base kit built with frontier_kit: the static defences and buildings of
a fortified enemy base that the player's army assaults, by day or by night.

Static defences are "vehicles" with speed 0 (ModelLibrary rigs them like tanks):
  * gun_turret: 120 mm gun turret on a battered concrete ring emplacement. `Turret` with
    Main_cannon / Muzzle_brake (recoil) and `Muzzle_main`; a coaxial MG on the mantlet with
    `Muzzle_coax` (child of Turret).
  * aa_turret: twin 35 mm flak turret on a sandbagged pad. `Turret` with Main_cannon and
    Main_cannon_2 (+ Muzzle_brake / Muzzle_brake_2), `Muzzle_main` centred between the tips, a
    tracking radar on `Radar` (child of Turret, spins about local Z) and a two-round SAM box on the
    turret's right side with `Muzzle_missile` (child of Turret).
  * rocket_turret: rocket and SAM box launcher behind a low blast wall. `Turret`, `Muzzle_main`; a
    heavy MG on an outrigger at the right of the launcher base, on `Mount_mg` (child of Turret) with
    `Muzzle_mg`.
  * mg_bunker: round "mushroom" pillbox: the roof stands on a central column over a continuous
    all-round firing slit, so the MG on `Turret` (a ring mount around the column) can yaw all the
    way round with its barrel through the slit. `Muzzle_main` at the barrel tip. A tripod ATGM on the
    roof turns on `Mount_missile` (`Muzzle_missile`).
  * artillery_emplacement: 152 mm towed howitzer on a firing platform in a sandbag ring. The
    whole gun (trails, wheels, shield, ready-round crates) is on `Turret`; Main_cannon /
    Muzzle_brake recoil; `Muzzle_main`. Spare ammunition stands in the corners outside the ring. A
    heavy MG on a sandbagged post on the ring wall guards the pit on `Mount_mg` (`Muzzle_mg`).
  * guard_tower: 11 m steel watchtower on a concrete blockhouse: ladder, walkway railing, cabin,
    a roof MG on `Turret` with `Muzzle_main`, a 40 mm grenade launcher on `Mount_gun` (`Muzzle_gun`)
    at the front right of the roof, and a searchlight on its own `Searchlight` pivot (the game sweeps
    it) whose Lamp lens faces the pivot's -Y.
Props (static buildings): command_hq (the Siege target; comms mast and a `Radar` dish),
base_wall, base_gate, floodlight_mast, fuel_depot, ammo_dump, vehicle_hangar, helipad (walkable,
under 0.1 m), razor_wire and sandbag_wall. base_wall, razor_wire and sandbag_wall end flush at
x = +-4 m (wire coils end in phase), so segments line up end to end every 8 m.

Conventions follow mb_vehicles / mb_props: metres, +Z up, Blender -Y is the front, origins on the
ground at the footprint centre (Blender X = width, Y = depth). Main paint is on `Team` panels so an
enemy base reads in its army colour; the rest is Concrete and Steel. Every light (searchlights,
floodlights, door lamps, lit windows, pad edge lights) is the emissive `Lamp` material so it reads at
night. Touching parts overlap or stand at least 1 cm apart, never face to face (coplanar faces
z-fight). Each turret's gun is the highest thing inside its sweep, so it can turn all the way
round without passing through the emplacement.
"""
import math
import random

import bmesh
from mathutils import Euler, Matrix, Vector, noise

import mb_weapons as wpn
from frontier_kit import chamfered
from mb_bosses import _railing
from mb_harbor import _trapezoids, corrugated_wall
from mb_themes import ladder, rim
from mb_town import fbox, slide
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _barrel, _basket, _dish, _face_box, _face_frame, _frame,
                         _hatch, _periscopes, _smoke, _stowage_bin, _tube_mouth)
from mb_vehicles2 import _axis, _gun

TAU = math.tau
BACKWARD = (-R90, 0, 0)  # cylinder axis along Y, local +Z -> +Y


# ----------------------------------------------------------------------------- shared helpers
def _circle(r, n, a0=0.0, cx=0.0, cy=0.0):
    """n points counter-clockwise on a circle."""
    return [(cx + r * math.cos(a0 + k * TAU / n), cy + r * math.sin(a0 + k * TAU / n)) for k in range(n)]


def _euler(m):
    return m.to_euler('XYZ')


def _moving_pivots(a, names):
    """Bake these pivots' parts like the kit's spinning parts (they receive AO but never cast it):
    frontier_kit only knows rotor / radar / mount names, and a sweeping searchlight moves too."""
    base = a._moving

    def moving(parent):
        o = a.pivots[parent] if parent else None
        while o is not None:
            if o.name in names:
                return True
            o = o.parent
        return base(parent)
    a._moving = moving


def bag(part, loc, size, yaw=0.0, tilt=(0.0, 0.0)):
    """Filled sandbag in 22 triangles: a pillow whose top, front and back bulge out and whose ends are
    pinched thinner and lower, so each bag reads as a soft lozenge from above and from the side.
    size = (length along local X, depth, height); loc is its centre."""
    w, d, h = size[0] / 2, size[1] / 2, size[2] / 2
    m = Matrix.Translation(Vector(loc)) @ Euler((tilt[0], tilt[1], yaw), 'XYZ').to_matrix().to_4x4()
    bm = part.bm

    def v(x, y, z):
        return bm.verts.new(m @ Vector((x, y, z)))
    c = {(sx, sy, sz): v(sx * w, sy * d * .7, -h if sz < 0 else h * .62)
         for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)}
    top = v(0, 0, h * 1.06)
    front, back = v(0, -d * 1.04, -h * .12), v(0, d * 1.04, -h * .12)
    edge_f, edge_b = v(0, -d * .86, h * .72), v(0, d * .86, h * .72)
    faces = []

    def fan(ring, centre):
        for i in range(len(ring)):
            faces.append(bm.faces.new((ring[i], ring[(i + 1) % len(ring)], centre)))
    fan([c[-1, -1, -1], c[1, -1, -1], c[1, -1, 1], edge_f, c[-1, -1, 1]], front)
    fan([c[1, 1, -1], c[-1, 1, -1], c[-1, 1, 1], edge_b, c[1, 1, 1]], back)
    fan([c[-1, -1, 1], edge_f, c[1, -1, 1], c[1, 1, 1], edge_b, c[-1, 1, 1]], top)
    faces.append(bm.faces.new((c[-1, -1, -1], c[-1, 1, -1], c[1, 1, -1], c[1, -1, -1])))
    faces.append(bm.faces.new((c[-1, -1, -1], c[-1, -1, 1], c[-1, 1, 1], c[-1, 1, -1])))
    faces.append(bm.faces.new((c[1, -1, -1], c[1, 1, -1], c[1, 1, 1], c[1, -1, 1])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)


def bag_run(part, rng, p0, p1, z, size=(.8, .4, .26), half=False, flush=True, jitter=1.0):
    """One course of sandbags laid end to end from p0 to p1 (x, y) with their centres at height z.
    half=True starts with a half bag, so alternate courses bond. flush cuts the last bag at p1 so
    the run ends exactly there; otherwise the run stops at the last whole bag."""
    p0, p1 = Vector(p0), Vector(p1)
    run = (p1 - p0).length
    if run < .05:
        return
    t = (p1 - p0) / run
    yaw = math.atan2(t.y, t.x)
    w = size[0]
    edges = [0.0]
    pos = w / 2 if half else w
    while pos < run - .12:
        edges.append(pos)
        pos += w
    if flush or run - edges[-1] > w * .9:
        edges.append(run)
    for u0, u1 in zip(edges, edges[1:]):
        lo, hi = max(0.0, u0 - .02), min(run, u1 + .02)
        c = p0 + t * ((lo + hi) / 2)
        j = jitter
        bag(part, (c.x, c.y, z + rng.uniform(-.01, .01) * j), (hi - lo, size[1] * rng.uniform(.95, 1.05), size[2]),
            yaw=yaw + rng.uniform(-.05, .05) * j, tilt=(rng.uniform(-.04, .04) * j, rng.uniform(-.03, .03) * j))


def bag_arc(part, rng, r, a0, a1, z, size=(.8, .4, .26), half=False, cx=0.0, cy=0.0):
    """One course of sandbags around an arc of radius r about (cx, cy) from angle a0 to a1
    (counter-clockwise)."""
    arc_len = r * (a1 - a0)
    n = max(1, round(arc_len / size[0]))
    step = (a1 - a0) / n
    start = a0 - (step / 2 if half else 0.0)
    for i in range(n + (1 if half else 0)):
        u0, u1 = max(a0, start + i * step), min(a1, start + (i + 1) * step)
        if u1 - u0 < step * .3:
            continue
        mid = (u0 + u1) / 2
        length = r * (u1 - u0) + .05
        bag(part, (cx + r * math.cos(mid), cy + r * math.sin(mid), z + rng.uniform(-.01, .01)),
            (length, size[1] * rng.uniform(.95, 1.05), size[2]), yaw=mid + R90 + rng.uniform(-.04, .04),
            tilt=(rng.uniform(-.04, .04), rng.uniform(-.03, .03)))


def coil(part, x0, x1, y, zc, r, pitch=.3, pts=8, wire=.018):
    """Concertina razor wire: a helix along X from x0 to x1 (whole turns, starting at the top, so
    runs placed end to end join in phase)."""
    n = max(1, round((x1 - x0) / pitch))
    total = n * pts
    points = [(x0 + (x1 - x0) * k / total, y + r * math.sin(k * TAU / pts), zc + r * math.cos(k * TAU / pts))
              for k in range(total + 1)]
    part.tube(points, wire, seg=3, caps=False)


def sweep(part, path, profile, closed=False, scale=None):
    """Sweep a (u, z) cross-section along a 2D path: u is the offset to the right of the direction
    of travel (outwards for a counter-clockwise path). scale(i) scales the section's height at
    path point i (ramps at open ends). Closed paths get no end caps."""
    pts = [Vector(p) for p in path]
    n = len(pts)
    bm = part.bm
    rings = []
    for i, p in enumerate(pts):
        if closed:
            a, b = pts[i - 1], pts[(i + 1) % n]
            e1, e2 = (p - a).normalized(), (b - p).normalized()
        else:
            e1 = (p - pts[max(0, i - 1)]).normalized() if i else (pts[1] - p).normalized()
            e2 = (pts[min(n - 1, i + 1)] - p).normalized() if i < n - 1 else e1
        n1, n2 = Vector((e1.y, -e1.x)), Vector((e2.y, -e2.x))
        nm = (n1 + n2)
        k = 1 / max(.5, (1 + n1.dot(n2)) / 2) ** .5
        nm = nm.normalized() * k if nm.length > 1e-6 else n1
        s = scale(i) if scale else 1.0
        rings.append([bm.verts.new((p.x + nm.x * u, p.y + nm.y * u, z * s)) for u, z in profile])
    if closed:
        part._faces(rings + [rings[0]], False, False)
    else:
        part._faces(rings)


def camo_net(a, rng, x0, x1, y0, y1, height, cells=(12, 10), keep=None, garnish=24, parent=None, seed=0.0,
             name='Camo_net'):
    """Draped camouflage net: a green sheet over the rectangle whose drape is height(x, y) (keep
    its slopes under ~35 degrees: the sheet is single-sided and seen from above). Cells whose
    centre fails keep(x, y) are dropped for a ragged outline. Garnish tufts (small open pyramids)
    in dark green, khaki and earth stand 2-3 cm proud of the sheet and break up its outline."""
    nx, ny = cells
    verts, faces, index = [], [], {}
    off = Vector((seed * 3.7, seed * 1.3, seed * 2.1))

    def z_at(x, y):
        return height(x, y) + .05 * noise.noise(Vector((x * .8, y * .8, 0)) + off)
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            y = y0 + (y1 - y0) * j / ny
            if 0 < i < nx and 0 < j < ny:
                x += (x1 - x0) / nx * .18 * noise.noise(Vector((x, y, 5.0)) + off)
                y += (y1 - y0) / ny * .18 * noise.noise(Vector((x, y, 9.0)) + off)
            index[i, j] = len(verts)
            verts.append((x, y, z_at(x, y)))
    cells_kept = []
    for j in range(ny):
        for i in range(nx):
            cx = x0 + (x1 - x0) * (i + .5) / nx
            cy = y0 + (y1 - y0) * (j + .5) / ny
            if keep and not keep(cx, cy):
                continue
            faces.append((index[i, j], index[i + 1, j], index[i + 1, j + 1], index[i, j + 1]))
            cells_kept.append((i, j))
    used = sorted({k for f in faces for k in f})
    remap = {k: n for n, k in enumerate(used)}
    a.part(name, 'Foliage', parent).mesh([verts[k] for k in used], [tuple(remap[k] for k in f) for f in faces])
    mats = ('FoliageDark', 'Canvas', 'FoliageDark', 'Dirt')
    for g in range(garnish if cells_kept else 0):
        i, j = cells_kept[rng.randrange(len(cells_kept))]
        cx = x0 + (x1 - x0) * (i + rng.uniform(.2, .8)) / nx
        cy = y0 + (y1 - y0) * (j + rng.uniform(.2, .8)) / ny
        s = rng.uniform(.22, .4)
        yaw = rng.uniform(0, TAU)
        base = []
        for k in range(4):
            u = yaw + k * R90
            px, py = cx + s * math.cos(u), cy + s * .75 * math.sin(u)
            base.append((px, py, z_at(px, py) + .03))
        top = (cx, cy, z_at(cx, cy) + rng.uniform(.1, .15))
        a.part(f'{name}_garnish', mats[g % 4], parent).mesh(base + [top], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])


def lattice(part, cx, cy, z0, z1, hw0, hw1, panels, leg=.12, brace=.04):
    """Four-legged lattice mast from z0 (half width hw0) to z1 (hw1): straight tapered legs, X-bracing
    on every face and a girt at every level. Member sections step by 2.5 cm (braces b and b + 2.5,
    girts b + 5 and b + 7.5 cm; legs must be thicker still), so no two members that meet share a face plane."""
    def corners(z):
        h = hw0 + (hw1 - hw0) * (z - z0) / (z1 - z0)
        return [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    c0, c1 = corners(z0), corners(z1)
    for q in range(4):
        part.limb((*c0[q], z0 - .02), (*c1[q], z1 + .02), leg, leg, bevel=0)
    levels = [z0 + (z1 - z0) * i / panels for i in range(panels + 1)]
    for za, zb in zip(levels, levels[1:]):
        ca, cb = corners(za), corners(zb)
        for q in range(4):
            q2 = (q + 1) % 4
            part.limb((*ca[q], za + .04), (*cb[q2], zb - .04), brace, brace, bevel=0)
            part.limb((*ca[q2], za + .04), (*cb[q], zb - .04), brace + .025, brace + .025, bevel=0)
    for z in levels[1:]:
        c = corners(z)
        for q in range(4):
            g = brace + (.05 if q % 2 == 0 else .075)
            part.limb((*c[q], z), (*c[(q + 1) % 4], z), g, g, bevel=0)


def loop_rail(part, points, h=.95, post=.05, rail=.03, every=1.2):
    """Handrail round a closed polygon standing on the deck: posts at every corner and between them
    (one per corner, so the loop never doubles a post), two closed rails."""
    pts = [Vector(p) for p in points]
    for p, q in zip(pts, pts[1:] + pts[:1]):
        n = max(1, round((q - p).length / every))
        for i in range(n):
            c = p + (q - p) * (i / n)
            part.box((post, post, h), loc=(c.x, c.y, c.z + h / 2), bevel=0)
    for z in (h * .55, h):
        part.tube([(p.x, p.y, p.z + z) for p in pts + pts[:1]], rail, seg=4, caps=False)


def searchlight(a, name, loc, parent=None, r=.32, length=.56):
    """Searchlight on its own pivot: a turntable, a yoke and a drum whose domed Lamp lens faces the
    pivot's -Y, with a steel bezel, cooling ribs and a handle at the back. Returns the pivot name."""
    p = a.pivot(name, loc, parent)
    yoke = a.part('Searchlight_yoke', 'Steel', p)
    head = a.part('Searchlight_head', 'Armor', p)
    zc = .14 + r + .06
    yoke.cyl(.2, .1, loc=(0, 0, .04), seg=10, bevel=.015, bseg=1)
    yoke.box((2 * r + .26, .14, .07), loc=(0, 0, .12), bevel=.01, seg=1)
    for s in (-1, 1):
        yoke.box((.06, .12, zc - .1), loc=(s * (r + .08), 0, .1 + (zc - .1) / 2), bevel=0)
        yoke.cyl(.07, .06, loc=(s * (r + .03), 0, zc), rot=ACROSS, seg=8, bevel=0)
    head.cyl(r, length, loc=(0, .03, zc), rot=FORWARD, seg=14, bevel=.02, bseg=1)
    yf = .03 - length / 2
    yoke.cyl(r + .035, .08, loc=(0, yf + .02, zc), rot=FORWARD, seg=14, bevel=.012, bseg=1)   # bezel
    a.part('Searchlight_lens', 'Lamp', p).lathe([(r * .9, 0), (r * .72, .035), (r * .36, .06), (0, .068)],
                                                loc=(0, yf - .01, zc), rot=FORWARD, seg=14)
    for k in range(4):                                                                     # cooling ribs
        head.cyl(r + .025, .025, loc=(0, yf + .18 + k * .08, zc), rot=FORWARD, seg=14, bevel=0)
    head.cyl(r * .72, .08, loc=(0, .03 + length / 2 + .03, zc), rot=FORWARD, seg=12, bevel=.015, bseg=1)
    yoke.tube([(-.1, .03 + length / 2 + .06, zc + .12), (-.1, .03 + length / 2 + .16, zc + .1),
               (.1, .03 + length / 2 + .16, zc + .1), (.1, .03 + length / 2 + .06, zc + .12)], .016, seg=4)
    return p


def flood_head(a, loc, yaw=0.0, tilt=.3, size=(.64, .3, .44), parent=None, name='Floodlights'):
    """Rectangular floodlight whose Lamp lens faces local -Y after yawing by `yaw` and pitching down
    by `tilt`: housing, visor, cooling fins and a U bracket to the loc point (its pivot axis)."""
    w, d, h = size
    m = _frame(loc, (0, 0, yaw)) @ _frame((0, 0, 0), (tilt, 0, 0))
    rot = _euler(m)
    body = a.part(f'{name}_housing', 'Armor', parent)
    body.box((w, d, h), loc=m @ Vector((0, 0, 0)), rot=rot, bevel=.03, seg=1)
    a.part(f'{name}_lens', 'Lamp', parent).box((w - .08, .05, h - .08), loc=m @ Vector((0, -d / 2 - .012, 0)),
                                               rot=rot, bevel=.012, seg=1)
    body.box((w + .06, .2, .03), loc=m @ Vector((0, -d / 2 - .06, h / 2 + .005)), rot=rot, bevel=0)  # visor
    for k in (-.3, 0, .3):                                                                    # fins
        body.box((.03, .1, h * .8), loc=m @ Vector((k * w, d / 2 + .04, 0)), rot=rot, bevel=0)
    br = a.part(f'{name}_bracket', 'Steel', parent)
    yawm = _frame(loc, (0, 0, yaw))
    br.tube([tuple(yawm @ Vector((-w / 2 - .06, 0, 0))), tuple(yawm @ Vector((-w / 2 - .06, 0, -h / 2 - .1))),
             tuple(yawm @ Vector((w / 2 + .06, 0, -h / 2 - .1))), tuple(yawm @ Vector((w / 2 + .06, 0, 0)))],
            .025, seg=4)
    br.box((.08, .08, .16), loc=yawm @ Vector((0, 0, -h / 2 - .16)), rot=(0, 0, yaw), bevel=0)


def caged_lamp(a, face, p, parent=None):
    """Bulkhead wall lamp on a facade point p: a steel base, a Lamp globe and a wire guard."""
    fbox(a.part('Wall_lamp_base', 'Steel', parent), face, p, (.2, .08, .24), out=.03)
    nx, ny = {'-y': (0, -1), '+y': (0, 1), '-x': (-1, 0), '+x': (1, 0)}[face]
    c = (p[0] + nx * .12, p[1] + ny * .12, p[2])
    a.part('Wall_lamp', 'Lamp', parent).sphere(.075, loc=c, seg=6, rings=4)
    g = a.part('Wall_lamp_guard', 'Steel', parent)
    g.torus(.1, .012, loc=c, rot=(R90, 0, 0) if nx == 0 else (0, R90, 0), seg=6, ring=3)


def flag(a, x, y, z0, height, w=1.5, h=.9, phase=0.0, yaw=0.0, parent=None, mat='Team'):
    """Flag pole with a waving flag (a thin lofted sheet, Team by default) flying towards local +X of
    yaw."""
    pole = a.part('Flag_pole', 'Steel', parent)
    pole.cyl(.05, height, loc=(x, y, z0 + height / 2), r2=.035, seg=8, bevel=0)
    pole.sphere(.07, loc=(x, y, z0 + height + .03), seg=6, rings=4)
    c, s = math.cos(yaw), math.sin(yaw)
    rings = []
    zt = z0 + height - .12
    for k in range(7):
        u = w * k / 6
        wave = .13 * math.sin(phase + u * 3.4) * (u / w) ** .7
        droop = .05 * u
        ring = []
        for dv, dz in ((-.012, -h), (.012, -h), (.012, 0), (-.012, 0)):
            lx, ly = u + .03, wave + dv
            ring.append((x + c * lx - s * ly, y + s * lx + c * ly, zt + dz - droop))
        rings.append(ring)
    a.part('Flag', mat, parent).loft(rings)


def hazard_sign(a, loc, yaw=0.0, size=.5, height=1.2, mat='Hazard', parent=None):
    """Diamond warning sign facing local -Y on a steel post: a black-edged plate with an
    exclamation mark. loc is the foot of the post."""
    m = _frame(loc, (0, 0, yaw))
    diamond = m @ _frame((0, 0, height), (0, math.pi / 4, 0))
    a.part('Sign_posts', 'Steel', parent).box((.06, .06, height + .05), loc=m @ Vector((0, .04, height / 2)),
                                              rot=(0, 0, yaw), bevel=0)
    a.part('Sign_edges', 'Charred', parent).box((size + .07, .02, size + .07), loc=diamond @ Vector((0, 0, 0)),
                                                rot=_euler(diamond), bevel=0)
    a.part('Signs', mat, parent).box((size, .02, size), loc=diamond @ Vector((0, -.015, 0)), rot=_euler(diamond),
                                     bevel=0)
    mark = a.part('Sign_marks', 'Charred', parent)
    mark.box((.06, .02, size * .42), loc=m @ Vector((0, -.03, height + size * .08)), rot=(0, 0, yaw), bevel=0)
    mark.box((.07, .02, .07), loc=m @ Vector((0, -.03, height - size * .3)), rot=(0, 0, yaw), bevel=0)


def crate(a, loc, size=(1.1, .5, .38), yaw=0.0, parent=None, band=True, mat='Crate'):
    """Ammunition crate standing on loc (the centre of its base): body, dark end cleats, rope
    handles and an optional yellow stencil band."""
    w, d, h = size
    m = _frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Crates', mat, parent).box((w, d, h), loc=m @ Vector((0, 0, h / 2)), rot=rot, bevel=.025, seg=1)
    cleat = a.part('Crate_cleats', 'Wood', parent)
    for s in (-1, 1):
        cleat.box((.06, d + .025, h + .02), loc=m @ Vector((s * (w / 2 - .09), 0, h / 2)), rot=rot, bevel=0)
    if band:
        a.part('Crate_bands', 'Hazard', parent).box((w * .3, d + .03, .06), loc=m @ Vector((0, 0, h * .66)),
                                                    rot=rot, bevel=0)


def shells(a, loc, cols, rows, r=.078, h=.7, pitch=.19, yaw=0.0, parent=None):
    """Artillery rounds standing in a block on loc: brass cases (Gilded) with steel ogive noses."""
    m = _frame(loc, (0, 0, yaw))
    for i in range(cols):
        for j in range(rows):
            p = m @ Vector(((i - (cols - 1) / 2) * pitch, (j - (rows - 1) / 2) * pitch, 0))
            a.part('Shell_cases', 'Gilded', parent).cyl(r, h * .62, loc=(p.x, p.y, p.z + h * .31), seg=6, bevel=0)
            a.part('Shell_heads', 'Armor', parent).lathe([(r * .98, h * .6), (r * .78, h * .84), (0, h)],
                                                         loc=(p.x, p.y, p.z), seg=6)


def generator(a, loc, yaw=0.0, size=(2.3, 1.15, 1.35), body='Armor', door='Team'):
    """Diesel generator set on a skid: housing with louvred ends, service doors, an exhaust stack with
    a rain cap, a fuel tank underneath and a hazard stripe along the skid."""
    w, d, h = size
    m = _frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Generator_skid', 'Undercarriage').box((w + .2, d + .1, .16), loc=m @ Vector((0, 0, .07)), rot=rot,
                                                  bevel=.02, seg=1)
    a.part('Generator_stripe', 'SafetyStripe').box((w + .22, d + .12, .05), loc=m @ Vector((0, 0, .1)), rot=rot,
                                                   bevel=0)
    a.part('Generator', body).box((w, d, h), loc=m @ Vector((0, 0, .14 + h / 2)), rot=rot, bevel=.05, seg=1)
    a.part('Generator_roof', 'Armor').box((w + .06, d + .06, .06), loc=m @ Vector((0, 0, .14 + h + .01)), rot=rot,
                                          bevel=.02, seg=1)
    for s in (-1, 1):
        a.part('Generator_doors', door).box((w * .28, .04, h * .7),
                                            loc=m @ Vector((s * w * .2, -d / 2 - .01, .14 + h * .5)), rot=rot, bevel=0)
        a.part('Generator_louvres', 'Undercarriage').grille(
            d * .7, h * .6, loc=m @ Vector((s * (w / 2 + .02), 0, .14 + h * .5)), rot=(0, 0, yaw + s * R90), slats=3,
            depth=.05, thickness=.04)
    steel = a.part('Generator_exhaust', 'Steel')
    ex = m @ Vector((w * .32, d * .1, 0))
    steel.cyl(.08, .9, loc=(ex.x, ex.y, .14 + h + .4), seg=8, bevel=0)
    steel.cyl(.13, .05, loc=(ex.x, ex.y, .14 + h + .88), seg=8, bevel=0)
    a.part('Generator_panel', 'Glass').box((.3, .03, .2), loc=m @ Vector((-w * .38, -d / 2 - .045, .14 + h * .72)),
                                           rot=rot, bevel=0)


# ----------------------------------------------------------------------------- gun_turret
def gun_turret(a):
    """Heavy 120 mm gun turret on a battered concrete ring emplacement (5 x 5 m): buttressed drum with
    a hazard-striped coping round the steel turret race, an ammunition porch with a lit steel door,
    a ladder and a cable conduit. The faceted turret carries add-on cheek armour, a cupola, a
    loader's hatch, a sight, smoke dischargers, a bustle rack, a spotlight and a long gun with a
    fume extractor and a grooved muzzle brake, with an armoured coaxial MG (Muzzle_coax) on the mantlet."""
    rng = random.Random(11)
    conc = a.part('Emplacement', 'Concrete')
    conc.prism(chamfered(5.0, 5.0, 1.1), .34, loc=(0, 0, .15), axis='Z', bevel=.05, seg=1, taper=.985)
    conc.lathe([(2.2, .28), (2.2, .34), (2.01, 1.16), (0, 1.16)], seg=24)
    a.part('Coping', 'Concrete').cyl(2.08, .14, loc=(0, 0, 1.19), seg=24, bevel=.03, bseg=1)       # z 1.12..1.26
    for k in range(8):                                                                         # buttresses
        ang = k * TAU / 8 + TAU / 16
        a.part('Buttresses', 'Concrete').box((.62, .5, .86), loc=(2.2 * math.cos(ang), 2.2 * math.sin(ang), .72),
                                             rot=(0, 0, ang), bevel=.04, seg=1, taper=(.45, .9), shift=(-.16, 0))
    for k in range(24):                                                                        # hazard band
        ang = (k + .5) * TAU / 24
        a.part('Race_band', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.26, .44, .04), loc=(1.93 * math.cos(ang), 1.93 * math.sin(ang), 1.265), rot=(0, 0, ang), bevel=0)
    a.part('Race', 'Steel').cyl(1.79, .12, loc=(0, 0, 1.28), seg=24, bevel=.02, bseg=1)             # z 1.22..1.34
    # Ammunition porch at the rear with a steel door, a caged lamp and a step.
    conc.box((1.5, .9, .82), loc=(0, 2.1, .7), bevel=.04, seg=1)
    a.part('Porch_door', 'Armor').box((.8, .06, .66), loc=(0, 2.56, .66), bevel=.015, seg=1)
    steel = a.part('Fittings', 'Steel')
    steel.box((.9, .08, .06), loc=(0, 2.57, 1.02), bevel=0)
    steel.box((.06, .06, .12), loc=(.3, 2.6, .66), bevel=0)                                        # handle
    for dz in (.45, .85):
        steel.box((.08, .06, .1), loc=(-.4, 2.58, dz), bevel=0)                                    # hinges
    caged_lamp(a, '+y', (.55, 2.55, .98))
    ladder(a.part('Ladder', 'Steel'), (2.28, 0, .3), 1.3, R90, width=.42, step=.32, rung=.028)
    a.part('Conduit', 'Pipe').tube([(-1.2, -2.35, .3), (-1.2, -2.08, .36), (-1.05, -1.9, 1.05), (-.95, -1.8, 1.13)],
                                   .05, seg=6)
    a.part('Junction_box', 'Armor').box((.36, .2, .3), loc=(-1.25, -2.28, .5), rot=(0, 0, .45), bevel=.02, seg=1)
    for k in range(10):                                                                        # anchor bolts
        ang = k * TAU / 10 + .2
        steel.box((.07, .07, .05), loc=(2.35 * math.cos(ang), 2.35 * math.sin(ang), .33), rot=(0, 0, ang), bevel=0)
    for x, y, yaw in ((1.9, 1.9, .5), (-1.95, 1.8, -.4)):                                        # sand heaps
        a.part('Grit', 'Dirt', flat=True).ico((.42, .32, .16), loc=(x, y, .3), rot=(0, 0, yaw), sub=1, jitter=.3,
                                              seed=x + y)

    t = a.pivot('Turret', (0, 0, 1.34))
    a.part('Turret_ring', 'Armor', t).cyl(1.72, .16, loc=(0, 0, .06), seg=24, bevel=.02, bseg=1)
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.95, -1.72), (.95, -1.72), (1.52, -.95), (1.6, .95), (1.38, 2.05), (-1.38, 2.05), (-1.6, .95),
               (-1.52, -.95)]
    H, z0 = .95, .12
    turret.prism(outline, H, loc=(0, 0, z0 + H / 2), axis='Z', bevel=.06, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((1.1, .5, .76), loc=(0, -1.82, .56), bevel=.05, taper=(.9, .88))                      # mantlet
    for b0, b1, u in (((.95, -1.72), (1.52, -.95), .52), ((-1.52, -.95), (-.95, -1.72), .48)):   # cheek blocks
        m = _face_frame(b0, b1, H, .86, z0=z0, u=u, v=.46)
        for i in (-1, 1):
            for j in (-1, 1):
                _face_box(a, 'Cheek_armor', 'Armor', m @ _frame((i * .23, j * .24, 0), (0, 0, 0)), (.42, .42, .12),
                          parent=t, bevel=.02)
    for b0, b1 in (((1.52, -.95), (1.6, .95)), ((-1.6, .95), (-1.52, -.95))):                   # side plates
        for u in (.2, .5, .8):
            _face_box(a, 'Side_plates', 'Armor', _face_frame(b0, b1, H, .86, z0=z0, u=u, v=.42), (.52, .6, .08),
                      parent=t, bevel=.015)
            m = _face_frame(b0, b1, H, .86, z0=z0, u=u, v=.42)
            tsteel.bolts([tuple(m @ Vector((dx, dy, .08))) for dx in (-.19, .19) for dy in (-.22, .22)], r=.03,
                         h=.03, rot=_euler(m), seg=6, bevel=0)
    top = z0 + H
    # Bustle: rack box with a louvred back and stowage bins on its sides.
    tarm.box((2.1, .7, .62), loc=(0, 2.1, .62), bevel=.04, seg=1, taper=(.96, .9))
    a.part('Bustle_vents', 'Undercarriage', t).grille(1.3, .36, loc=(0, 2.46, .62), rot=(0, 0, math.pi), slats=4,
                                                    depth=.05, thickness=.035)
    for s in (-1, 1):
        _stowage_bin(a, (s * 1.02, 2.1, .32), (.2, .6, .5), parent=t, latch_side=s)
        _smoke(a, tsteel, 1.05, -1.25, top - .12, s, count=3, gap=.09, r=.05, depth=.16)
    # Roof: cupola, loader's hatch, sight, vent, lifting eyes, periscopes, antennas, spotlight.
    tsteel.cyl(.38, .22, loc=(.6, .35, top + .09), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.33, .08, loc=(.6, .35, top + .23), seg=16, bevel=.02, bseg=1)
    _hatch(a, .6, .35, top + .25, .26, parent=t)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(5):
        ang = -R90 + (k - 2) * .62
        glass.box((.11, .05, .08), loc=(.6 + math.cos(ang) * .385, .35 + math.sin(ang) * .385, top + .13),
                  rot=(0, 0, ang + R90), bevel=0)
    _hatch(a, -.6, .55, top - .01, .3, parent=t)
    tarm.box((.42, .38, .3), loc=(-.72, -.72, top + .1), bevel=.04, seg=1)
    a.part('Sight', 'Glass', t).box((.3, .04, .15), loc=(-.72, -.915, top + .13), bevel=.01, seg=1)
    tarm.cyl(.22, .12, loc=(0, 1.2, top + .03), seg=12, bevel=.02, bseg=1)
    a.part('Vent_cap', 'Undercarriage', t).cyl(.16, .05, loc=(0, 1.2, top + .1), seg=12, bevel=0)
    _periscopes(a, [(dx, -1.18, top - .02, 0) for dx in (-.25, .25)], parent=t)
    for x, y in ((1.05, -.7), (-1.05, -.7), (1.05, 1.5), (-1.05, 1.5)):
        tsteel.tube([(x - .07, y, top - .02), (x - .07, y, top + .08), (x + .07, y, top + .08),
                     (x + .07, y, top - .02)], .02, seg=4)
    _antenna(a, t, -1.0, 1.7, top, 1.5)
    _antenna(a, t, 1.0, 1.7, top, 1.1)
    tsteel.box((.1, .1, .07), loc=(-1.0, 1.7, top + .02), bevel=0)
    tarm.box((.3, .34, .26), loc=(-.95, -1.5, top + .02), bevel=.03, seg=1)                         # spotlight
    a.part('Spotlight', 'Lamp', t).box((.22, .04, .16), loc=(-.95, -1.68, top + .03), bevel=.01, seg=1)
    # Gun: the coaxial MG (second weapon, slot coax) in an armoured housing on the mantlet's right cheek,
    # a 7.6 cm barrel with a flash hider and `Muzzle_coax` (a child of Turret) at its face; then the long
    # 120 mm tube.
    a.part('Coax_housing', 'Armor', t).box((.22, .34, .22), loc=(.42, -2.12, .47), bevel=.03, seg=1)
    coax = a.part('Coax', 'Steel', t)
    coax.box((.14, .1, .1), loc=(.42, -2.3, .47), bevel=0)                                          # trunnion block
    coax.cyl(.038, .5, loc=(.42, -2.55, .47), rot=FORWARD, seg=8, bevel=0)
    a.part('Coax_hider', 'Undercarriage', t).cyl(.052, .12, loc=(.42, -2.82, .47), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (.42, -2.88, .47), t)
    tip = _gun(a, t, 0, -2.04, .58, 3.35, .13, pitch=.02, seg=14,
               sleeves=((.26, .08, .155), (.72, .08, .155)), extractor=(.46, .66, .19), brake=(.6, .22, 2),
               brake_seg=12)
    _basket(a, -.95, .95, 2.47, 2.9, .3, .3, parent=t)
    tsteel.bolts([(x, -1.48, top - .005) for x in (-.7, -.35, 0, .35, .7)], r=.035, h=.03, seg=6, bevel=0)
    a.pivot('Muzzle_main', tip, t)


# ----------------------------------------------------------------------------- aa_turret
def aa_turret(a):
    """Twin 35 mm flak turret (Oerlikon GDF lineage) on a sandbagged concrete pad (4.5 x 4.5 m): a
    Team gun house on a turntable with a gun pod on each side, both barrels raised 28 degrees with
    cooling sleeves and flash hiders, ammunition magazines, an optical sight and a small tracking
    radar spinning on the turret roof, and a box of two SAM tubes on an arm at the turret's right side.
    Ready ammunition waits in the pad's corners."""
    rng = random.Random(21)
    a.part('Pad', 'Concrete').prism(chamfered(4.5, 4.5, .5), .32, loc=(0, 0, .14), axis='Z', bevel=.04, seg=1,
                                    taper=.99)
    bags = a.part('Sandbags', 'Sandbag')
    size, h = (.66, .36, .24), .23
    for course in range(3):
        z = .3 + h / 2 - .02 + course * h
        rows = (1.93, 1.57) if course < 2 else (1.75,)
        for r in rows:
            half = (course % 2 == 1) ^ (r < 1.7)
            # Front and back runs take the corners; the sides run between them. Gap at the back.
            e = r + size[1] / 2 - .02
            bag_run(bags, rng, (-e, -r), (e, -r), z, size, half)
            bag_run(bags, rng, (e, r), (.6, r), z, size, half, flush=True)
            bag_run(bags, rng, (-.6, r), (-e, r), z, size, not half, flush=True)
            f = r - size[1] / 2 + .02
            bag_run(bags, rng, (r, -f), (r, f), z, size, not half)
            bag_run(bags, rng, (-r, f), (-r, -f), z, size, half)
    for x, y in ((1.06, 1.06), (-1.06, 1.06), (1.06, -1.06)):                                   # ready rounds
        crate(a, (x, y, .3), size=(.62, .36, .3), yaw=math.atan2(y, x) + R90)
    a.part('Cable', 'Rubber').tube([(-1.7, .9, .32), (-1.2, .5, .32), (-.6, .15, .33)], .035, seg=5)

    t = a.pivot('Turret', (0, 0, .3))
    steel = a.part('Turret_steel', 'Steel', t)
    armor = a.part('Turret_armor', 'Armor', t)
    house = a.part('Gun_house', 'Team', t)
    steel.cyl(1.18, .14, loc=(0, 0, .05), seg=24, bevel=.02, bseg=1)                              # turntable
    armor.cyl(.6, .5, loc=(0, .1, .35), seg=16, bevel=.03, bseg=1)                                # pedestal
    house.box((1.04, 1.5, .9), loc=(0, .15, 1.0), bevel=.05, seg=2, taper=(.9, .86), shift=(0, .08))
    armor.box((.9, .5, .5), loc=(0, .95, .82), bevel=.04, seg=1)                                  # rear pack
    a.part('Rear_vents', 'Undercarriage', t).grille(.6, .3, loc=(0, 1.21, .82), rot=(0, 0, math.pi), slats=3,
                                                    depth=.05, thickness=.035)
    lean = -.2                                                                                  # house front slope
    armor.box((.8, .06, .42), loc=(0, -.565, .82), rot=(lean, 0, 0), bevel=.015, seg=1)            # front plate
    a.part('Vision_block', 'Glass', t).box((.44, .05, .12), loc=(0, -.48, 1.2), rot=(lean, 0, 0), bevel=.01, seg=1)
    steel.box((.52, .08, .04), loc=(0, -.47, 1.28), rot=(lean, 0, 0), bevel=0)                     # brow
    steel.bolts([(x, -.605 + (z - .82) * .203, z) for x in (-.33, .33) for z in (.68, .96)], r=.03, h=.04,
                rot=(R90 + lean, 0, 0), seg=6, bevel=0)
    for k in range(12):                                                                          # rim bolts
        u = k * TAU / 12
        steel.box((.07, .07, .04), loc=(1.1 * math.cos(u), 1.1 * math.sin(u), .125), rot=(0, 0, u), bevel=0)
    for x in (-.62, .62):                                                                        # ready boxes
        a.part('Ammo_boxes', 'Crate', t).box((.34, .5, .26), loc=(x, .78, .24), bevel=.02, seg=1)
        a.part('Ammo_bands', 'Hazard', t).box((.37, .12, .05), loc=(x, .78, .31), bevel=0)
    pitch = math.radians(28)
    rot = (-pitch, 0, 0)
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .78
        at = _axis((x, .25, 1.02), pitch)
        house.box((.36, 1.55, .5), loc=tuple(at(.55)), rot=rot, bevel=.04, seg=1)                   # gun pod
        armor.box((.2, 1.2, .3), loc=tuple(at(.6, .3)), rot=rot, bevel=.03, seg=1)                  # pod top rail
        steel.box((.3, .34, .3), loc=(s * .58, .2, 1.02), bevel=.02, seg=1)                          # trunnion
        steel.cyl(.1, .28, loc=(s * .6, .2, 1.02), rot=ACROSS, seg=10, bevel=.015, bseg=1)
        mag = at(.25, 0, s * .3)
        armor.box((.26, .7, .42), loc=tuple(mag), rot=rot, bevel=.03, seg=1)                        # magazine
        steel.box((.05, .5, .05), loc=tuple(at(.25, .1, s * .44)), rot=rot, bevel=0)
        base = at(1.3)
        tips.append(_barrel(a, t, start_y=base.y, length=2.35, radius=.045, height=base.z, pitch=pitch, x=x,
                            suffix=suffix, seg=10, style='flash', brake=(.12, .24, .12), sleeve=(.12, .5, .07),
                            ))
    a.pivot('Muzzle_main', tuple((Vector(tips[0]) + Vector(tips[1])) / 2), t)
    # Sight, hatch, grab rails, antenna and the tracking radar on its mast.
    armor.box((.3, .3, .28), loc=(.25, -.35, 1.5), bevel=.03, seg=1)
    a.part('Sight', 'Glass', t).box((.22, .04, .14), loc=(.25, -.515, 1.52), bevel=.01, seg=1)
    _hatch(a, -.2, -.1, 1.44, .24, parent=t)
    for s in (-1, 1):
        steel.tube([(s * .47, -.4, 1.3), (s * .47, -.4, 1.4), (s * .44, .5, 1.4), (s * .44, .5, 1.3)], .018, seg=4)
    _antenna(a, t, -.35, .9, 1.07, 1.2)
    steel.cyl(.1, .3, loc=(0, .62, 1.55), seg=10, bevel=.015, bseg=1)
    r = a.pivot('Radar', (0, .62, 1.7), t)
    rm = a.part('Radar_mast', 'Steel', r)
    rm.cyl(.08, .14, loc=(0, 0, .06), seg=10, bevel=0)
    rm.box((.12, .18, .3), loc=(0, .05, .26), bevel=.02, seg=1)
    rm.limb((0, -.15, .42), (0, -.44, .47), .03, .03, bevel=0)
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.1, .42), .44, .3, depth=.13, seg=12, tilt=.2)
    a.part('Radar_feed', 'Lamp', r).box((.06, .05, .06), loc=(0, -.47, .475), bevel=0)
    # Second weapon (slot missile): a box of two SAM tubes (Mistral / Stinger lineage) on an arm off the
    # right of the rear pack, outboard of the right gun pod and its magazine, raised 20 degrees and high
    # enough to sweep over the sandbags. `Muzzle_missile` (a child of Turret) sits between the two tube
    # mouths. The box is not named like the elevating barrel parts, so it stays at its authored angle.
    sam_pitch, L = math.radians(20), 1.5
    at = _axis((1.45, .8, 1.1), sam_pitch)
    srot = (-sam_pitch, 0, 0)
    a.part('SAM_box', 'Team', t).box((.3, L, .5), loc=tuple(at(L / 2 - .15)), rot=srot, bevel=.03, seg=1)
    frame = a.part('SAM_frame', 'Armor', t)
    for d in (-.13, L - .22):                                                                   # end bands
        frame.box((.34, .1, .54), loc=tuple(at(d)), rot=srot, bevel=.01, seg=1)
    frame.box((.05, L - .5, .06), loc=tuple(at(L / 2 - .15, .1, .165)), rot=srot, bevel=0)       # side rail
    a.part('SAM_bracket', 'Armor', t).limb((.4, .95, .85), (1.5, .95, .85), .14, .14, bevel=.015, seg=1)
    for up in (-.11, .11):
        _tube_mouth(a, t, _frame(at(L - .15, up), (R90 - sam_pitch, 0, 0)), .085, protrude=.05, seg=10,
                    name='SAM_tubes')
    a.pivot('Muzzle_missile', tuple(at(L - .15 + .05)), t)


# ----------------------------------------------------------------------------- rocket_turret
def rocket_turret(a):
    """Rocket and SAM battery (4.5 x 4.5 m): a trainable box launcher of eight canisters raised 30
    degrees on a Team launcher base, an elevation ram, a fire-control sensor with a glass eye, cable
    runs and hazard markings, a heavy MG on an outrigger at the right (Mount_mg), behind a low concrete
    blast wall open at the back."""
    rng = random.Random(33)
    a.part('Pad', 'Concrete').prism(chamfered(4.5, 4.5, .6), .3, loc=(0, 0, .13), axis='Z', bevel=.04, seg=1,
                                    taper=.99)
    wall = a.part('Blast_wall', 'Concrete')
    ring = chamfered(4.36, 4.36, .9)
    for i in range(len(ring)):
        p, q = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        if p.y > 1.9 and q.y > 1.9:                                                             # open back
            continue
        mid, d = (p + q) / 2, q - p
        wall.box((d.length + .02, .32, .62), loc=(mid.x, mid.y, .56), rot=(0, 0, math.atan2(d.y, d.x)), bevel=.04,
                 seg=1, taper=(1, .7))
    for i, (x, y) in enumerate(((-1.4, 2.18), (1.4, 2.18))):                                   # wall ends
        wall.box((.62, .34, .7), loc=(x * .92, y - .02, .6), bevel=.04, seg=1, taper=(1, .7))
    for x, y, yaw in ((0, -2.18, 0), (2.18, 0, R90), (-2.18, 0, -R90)):                           # warning bands
        m = _frame((x, y, .62), (0, 0, yaw))
        for j in range(6):
            a.part('Wall_band', 'SafetyStripe' if j % 2 else 'Charred').box(
                (.3, .03, .22), loc=m @ Vector(((j - 2.5) * .31, -.14, 0)), rot=(-.077, 0, yaw), bevel=0)
    for k, (x, y, s) in enumerate(((.9, -1.2, .8), (-1.1, -.6, .6), (.2, -1.6, .5))):              # scorch
        a.part('Scorch', 'Charred').cyl(s, .02, loc=(x, y, .285 + k * .012), seg=9, bevel=0)
    crate(a, (1.45, 1.3, .28), size=(1.0, .42, .34), yaw=.3)
    crate(a, (-1.5, 1.2, .28), size=(.9, .42, .34), yaw=-.4)
    a.part('Cable', 'Rubber').tube([(1.1, 2.3, .3), (.8, 1.6, .3), (.3, .9, .31)], .04, seg=5)

    t = a.pivot('Turret', (0, 0, .28))
    steel = a.part('Turret_steel', 'Steel', t)
    armor = a.part('Turret_armor', 'Armor', t)
    team = a.part('Launcher_base', 'Team', t)
    steel.cyl(1.2, .12, loc=(0, 0, .05), seg=24, bevel=.02, bseg=1)
    team.box((1.5, 1.8, .62), loc=(0, .25, .42), bevel=.05, seg=1, taper=(.9, .92))
    armor.box((1.6, .5, .3), loc=(0, 1.0, .3), bevel=.03, seg=1)
    a.part('Base_vents', 'Undercarriage', t).grille(.9, .4, loc=(.3, 1.26, .45), rot=(0, 0, math.pi), slats=3,
                                                    depth=.05, thickness=.035)
    pitch = math.radians(30)
    rot = (-pitch, 0, 0)
    hinge = Vector((0, .75, 1.0))
    L, W, Hb = 2.5, 1.9, 1.0
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = hinge - turn @ Vector((0, L / 2 - .25, -Hb / 2 - .05))
    box = _frame(mid, rot)
    a.part('Launcher_box', 'Team', t).box((W, L, Hb), loc=tuple(mid), rot=rot, bevel=.05, seg=1)
    frame = a.part('Box_frame', 'Armor', t)
    for y in (-L / 2 + .09, L / 2 - .1):
        frame.box((W + .06, .14, Hb + .06), loc=box @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
    for y in (-.5, .3):
        frame.box((W + .03, .08, Hb + .03), loc=box @ Vector((0, y, 0)), rot=rot, bevel=0)
    for s in (-1, 1):                                                                          # top rails, lugs
        frame.box((.1, L - .5, .05), loc=box @ Vector((s * .55, 0, Hb / 2 + .015)), rot=rot, bevel=0)
        steel.box((.09, .09, .08), loc=box @ Vector((s * .8, -L / 2 + .09, Hb / 2 + .06)), rot=rot, bevel=0)
    face = a.part('Box_face', 'Undercarriage', t)
    face.box((W - .08, .04, Hb - .08), loc=box @ Vector((0, -L / 2 - .005, 0)), rot=rot, bevel=0)
    for cx in (-.69, -.23, .23, .69):
        for cz in (-.23, .23):
            _tube_mouth(a, t, box @ _frame((cx, -L / 2 - .02, cz), FORWARD), .18, protrude=.06, seg=10)
            if (cx, cz) in ((-.69, .23), (.23, .23), (.69, -.23)):                              # sealed canisters
                cover = box @ _frame((cx, -L / 2 - .07, cz), FORWARD)
                a.part('Tube_covers', 'Canvas', t).cyl(.15, .04, loc=cover.to_translation(), rot=_euler(cover), seg=10,
                                                       bevel=.01, bseg=1)
    a.part('Box_stencil', 'Hazard', t).box((.5, .6, .03), loc=box @ Vector((-.5, -.1, Hb / 2 + .01)), rot=rot, bevel=0)
    for s in (-1, 1):
        armor.box((.16, .5, 1.02), loc=(s * (W / 2 + .1), hinge.y, .6), bevel=.02, seg=1)             # hinge cheeks
    steel.cyl(.1, W + .44, loc=tuple(hinge), rot=ACROSS, seg=10, bevel=.015, bseg=1)
    ram_top = box @ Vector((0, -.45, -Hb / 2))
    steel.limb((0, -.35, .5), tuple(ram_top + Vector((0, 0, .03))), .16, .16, bevel=.02)            # elevation ram
    steel.limb((0, -.35, .5), (0, -.45, .9), .11, .11, bevel=.01)
    a.pivot('Muzzle_main', tuple(box @ Vector((0, -L / 2 - .08, 0))), t)
    # Fire-control sensor on the right of the base, cabinet on the left.
    armor.box((.4, .4, .5), loc=(.95, -.55, .45), bevel=.03, seg=1)
    steel.cyl(.07, .3, loc=(.95, -.55, .85), seg=8, bevel=0)
    armor.box((.44, .4, .32), loc=(.95, -.55, 1.12), bevel=.04, seg=1)
    a.part('Sensor_eye', 'Glass', t).cyl(.11, .04, loc=(.95, -.76, 1.14), rot=FORWARD, seg=10, bevel=0)
    a.part('Sensor_lamp', 'Lamp', t).box((.1, .03, .06), loc=(1.08, -.76, 1.03), bevel=0)
    _stowage_bin(a, (-.95, -.5, .1), (.36, .5, .5), parent=t, latch_side=0)
    _antenna(a, t, -.6, 1.05, .45, 1.3)
    # Second weapon: a heavy machine gun on an outrigger arm at the right of the launcher base, at roof
    # height but outboard of the box launcher, so the box can elevate without meeting it; its tall pintle
    # lifts the barrel over the fire-control sensor (Mount_mg, a child of Turret, with Muzzle_mg).
    br = a.part('HMG_bracket', 'Armor', t)
    br.box((.92, .2, .12), loc=(1.08, .15, .64), bevel=.015, seg=1)
    br.limb((.72, .15, .2), (1.36, .15, .6), .1, .1, bevel=0)                                      # brace
    wpn.hmg(a, (1.45, .15, .7), parent=t, post=.52, ammo=1)


# ----------------------------------------------------------------------------- mg_bunker
def mg_bunker(a):
    """Round concrete MG pillbox (4 x 4 m, 1.9 m) after the British "mushroom" pillbox: a battered
    lower wall in an earth berm, a continuous 40 cm firing slit all round and a thick roof slab
    with a Team steel fascia, carried on a central column. The heavy MG rides a ring mount on the
    column, so it traverses all the way round with its barrel poking out of the slit. Camouflage
    netting and sandbags on the roof, a periscope, a vent, and a low steel door with a lamp at the
    back; a tripod ATGM stands on the roof (Mount_missile)."""
    rng = random.Random(44)
    conc = a.part('Pillbox', 'Concrete')
    slit0, slit1 = .95, 1.35
    conc.lathe([(1.86, -.02), (1.86, .06), (1.72, slit0), (0, slit0)], seg=20)                     # lower wall
    a.part('Interior', 'Undercarriage').cyl(1.52, .05, loc=(0, 0, slit0 + .005), seg=20, bevel=0)  # dark floor
    conc.cyl(.3, slit1 - slit0 + .1, loc=(0, 0, (slit0 + slit1) / 2), seg=12, bevel=0)             # column
    roof = a.part('Roof', 'Concrete')
    roof.lathe([(1.66, slit1), (1.79, slit1 + .04), (1.79, slit1 + .3), (1.58, 1.84), (0, 1.88)], seg=20)
    fascia = _circle(1.84, 20)
    a.part('Fascia', 'Team').shell(fascia, .2, .07, loc=(0, 0, slit1 + .07))
    a.part('Slit_lintel', 'Armor').shell(_circle(1.75, 20), .05, .06, loc=(0, 0, slit1 - .02))
    # Earth berm round the lower wall, split at the back for the door.
    berm = a.part('Berm', 'Dirt')
    gap = .38
    arc_pts = [(2.0 * math.cos(u), 2.0 * math.sin(u)) for u in
               (R90 + gap + k * (TAU - 2 * gap) / 24 for k in range(25))]
    sweep(berm, arc_pts, [(0, -.02), (-.1, .3), (-.25, .6), (-.45, .6), (-.45, -.02)],
          scale=lambda i: min(1.0, .25 + .75 * min(i, 24 - i) / 2))
    tufts = a.part('Tufts', 'Grass', flat=True)
    for k in range(7):
        u = R90 + .7 + k * .78
        tufts.ico((.22, .18, .1), loc=(1.93 * math.cos(u), 1.93 * math.sin(u), .2), sub=1, jitter=.35, seed=k * 2.1)
    # Rear door with steps down and a lamp.
    a.part('Door', 'Team').box((.76, .08, .8), loc=(0, 1.8, .44), rot=(-.14, 0, 0), bevel=.015, seg=1)
    steel = a.part('Fittings', 'Steel')
    steel.box((.9, .1, .07), loc=(0, 1.8, .87), bevel=0)
    steel.box((.05, .05, .14), loc=(.26, 1.86, .45), bevel=0)
    a.part('Steps', 'Concrete').box((.9, .5, .08), loc=(0, 2.08, .03), bevel=.02, seg=1)
    a.part('Door_lamp', 'Lamp').sphere(.07, loc=(-.5, 1.78, .8), seg=8, rings=5)
    steel.box((.12, .1, .16), loc=(-.5, 1.72, .8), bevel=0)
    # Roof: observation cupola, vent, sandbags at the front and a camouflage net over the back.
    top = 1.84
    cx, cy = -.55, .5
    cup = a.part('Cupola', 'Team')
    cup.cyl(.36, .36, loc=(cx, cy, top + .16), seg=12, bevel=.02, bseg=1)
    a.part('Cupola_top', 'Armor').cyl(.3, .1, loc=(cx, cy, top + .37), seg=12, bevel=.03, bseg=1)
    glass = a.part('Vision_slits', 'Glass')
    for k in range(5):
        u = -R90 + (k - 2) * .75
        glass.box((.14, .04, .06), loc=(cx + .355 * math.cos(u), cy + .355 * math.sin(u), top + .25),
                  rot=(0, 0, u + R90), bevel=0)
    _hatch(a, cx, cy + .02, top + .41, .2)
    steel.cyl(.1, .4, loc=(.62, .1, top + .15), seg=8, bevel=0)
    steel.cyl(.17, .06, loc=(.62, .1, top + .38), seg=8, bevel=0)
    bags = a.part('Roof_sandbags', 'Sandbag')
    for i, (u0, u1) in enumerate(((3.85, 5.55), (4.1, 5.3))):
        bag_arc(bags, rng, 1.28 - i * .08, u0, u1, top + .1 + i * .17, size=(.6, .34, .2), half=i == 1)
    _antenna(a, None, .95, .75, top, 1.4)

    def drape(x, y):
        r = math.hypot(x, y)
        return top + .05 + max(0.0, .5 - r * .25) * .45 - max(0.0, r - 1.6) * .9
    camo_net(a, rng, -1.95, 1.95, -1.2, 1.95, drape, cells=(12, 10),
             keep=lambda x, y: (math.hypot(x, y) < 1.9 + .1 * noise.noise(Vector((x * 2, y * 2, 1.0))) and
                                y > -.62 + .3 * math.sin(x * 1.7 + .5) and math.hypot(x - cx, y - cy) > .46),
             garnish=34, seed=4.0)

    # Ring-mounted heavy MG on the column.
    t = a.pivot('Turret', (0, 0, slit0 + .02))
    ring_ = a.part('MG_ring', 'Steel', t)
    ring_.cyl(.4, .14, loc=(0, 0, .09), seg=14, bevel=.02, bseg=1)
    ring_.box((.18, .45, .08), loc=(0, -.5, .16), bevel=0)                                          # arm
    mg = a.part('MG', 'Armor', t)
    zb = slit0 + .02
    zc = 1.16 - zb                                                                                 # barrel height
    mg.box((.22, .56, .24), loc=(0, -.76, zc), bevel=.03, seg=1)                                     # receiver
    mg.box((.07, .2, .13), loc=(0, -.42, zc - .07), rot=(.4, 0, 0), bevel=0)                         # grips
    a.part('MG_shield', 'Team', t).box((.64, .05, .3), loc=(0, -1.12, zc + .01), bevel=.012, seg=1, taper=(.8, 1))
    a.part('MG_ammo', 'Crate', t).box((.22, .3, .2), loc=(.24, -.7, zc - .05), bevel=.02, seg=1)
    tip_y = -2.06
    a.part('Main_cannon', 'Steel', t).cyl(.038, abs(tip_y) - 1.1, loc=(0, (tip_y - 1.03) / 2, zc), rot=FORWARD, seg=8,
                                          bevel=0)
    brake = a.part('Muzzle_brake', 'Undercarriage', t)
    brake.cyl(.056, .18, loc=(0, tip_y + .09, zc), rot=FORWARD, seg=8, bevel=0)
    brake.cyl(.062, .05, loc=(0, -1.3, zc), rot=FORWARD, seg=8, bevel=0)                          # barrel collar
    a.pivot('Muzzle_main', (0, tip_y - .01, zc), t)
    # Second weapon: a tripod anti-tank missile launcher on the roof slab, front right inside the sandbag
    # arc (Mount_missile / Muzzle_missile); its canister clears the sandbags.
    wpn.atgm_tripod(a, (.3, -.58, top + .02), height=.55, length=1.2, spread=.34)


# ----------------------------------------------------------------------------- artillery_emplacement
def artillery_emplacement(a):
    """152 mm towed howitzer (D-20 lineage) dug in behind a sandbag ring (7 x 7 m). The gun stands on a
    plank firing platform with its split trails spread and spades down; the carriage, wheels, shield,
    equilibrators, cradle, recuperators, double-baffle brake and two ready-round crates turn together
    on `Turret`. Spare crates and rounds wait in the corners outside the ring, and the ring opens at
    the back. A heavy MG on a sandbagged post on the ring wall (Mount_mg) guards the pit."""
    rng = random.Random(55)
    a.part('Platform', 'Wood').cyl(2.55, .08, loc=(0, 0, .03), seg=20, bevel=.02, bseg=1)
    planks = a.part('Planks', 'LogWood')
    for k in range(-5, 6):
        x = k * .44
        half = math.sqrt(max(0.0, 2.45 ** 2 - x * x))
        planks.box((.04, 2 * half, .03), loc=(x, 0, .075), bevel=0)
    a.part('Floor', 'Dirt').cyl(3.0, .04, loc=(0, 0, .0), seg=20, bevel=0)
    bags = a.part('Sandbags', 'Sandbag')
    size, h = (.8, .4, .3), .28
    g = .3                                                                                        # gap half-angle
    a0, a1 = R90 + g, R90 + TAU - g
    for course in range(3):
        z = h / 2 - .012 + course * h
        rows = (3.2, 2.82) if course < 2 else (3.02,)
        for r in rows:
            bag_arc(bags, rng, r, a0 + .03 * (course % 2), a1 - .03 * (course % 2), z, size,
                    half=(course % 2 == 1) ^ (r < 3.0))
    # Corner ammunition outside the ring.
    for x, y, yaw in ((2.75, 2.85, -.8), (-2.8, 2.8, .8), (-2.85, -2.75, -.75)):
        crate(a, (x, y, 0), size=(1.0, .46, .36), yaw=yaw)
        crate(a, (x + .05, y - .04, .36), size=(.95, .44, .34), yaw=yaw + .08, band=False)
    shells(a, (2.85, -2.85, 0), 3, 2, yaw=.8)
    shells(a, (-2.35, 3.2, 0), 2, 2, yaw=.3)
    a.part('Tarp', 'Canvas').box((1.1, .8, .12), loc=(2.72, 2.8, .78), rot=(.08, -.05, -.8), bevel=.05, seg=1)

    t = a.pivot('Turret', (0, 0, .09))
    team = a.part('Gun_carriage', 'Team', t)
    steel = a.part('Gun_steel', 'Steel', t)
    armor = a.part('Gun_armor', 'Armor', t)
    # Split trails with spades, spread from the pivot behind the axle.
    for s in (-1, 1):
        a0_, a1_ = Vector((s * .3, .45, .5)), Vector((s * 1.02, 1.78, .2))
        team.limb(tuple(a0_), tuple(a1_), .22, .26, bevel=.03)
        armor.limb(tuple(a1_ + Vector((0, 0, .02))), (s * 1.1, 1.98, .06), .28, .28, bevel=.02)         # trail end
        armor.box((.56, .08, .5), loc=(s * 1.14, 2.06, .24), rot=(-.3, 0, -s * .5), bevel=.02, seg=1)   # spade
        steel.box((.1, .5, .1), loc=(s * .8, 1.42, .42), rot=(0, 0, -s * .5), bevel=0)                 # handle
    # Carriage, axle and wheels.
    armor.box((1.9, .5, .3), loc=(0, .15, .62), bevel=.03, seg=1)
    for s in (-1, 1):
        x = s * 1.18
        a.part('Tyres', 'Rubber', t).cyl(.55, .3, loc=(x, .15, .56), rot=ACROSS, seg=16, bevel=.07, bseg=1)
        a.part('Wheels', 'Team', t).cyl(.34, .33, loc=(x, .15, .56), rot=ACROSS, seg=12, bevel=.02, bseg=1)
        steel.cyl(.12, .38, loc=(x, .15, .56), rot=ACROSS, seg=8, bevel=0)
    steel.cyl(.36, .12, loc=(0, .1, .77), seg=14, bevel=.02, bseg=1)                                # traverse ring
    zt = 1.2                                                                                     # trunnions
    for s in (-1, 1):                                                                             # upper carriage
        team.box((.1, .95, .62), loc=(s * .36, .28, .98), bevel=.03, seg=1, taper=(1, .55), shift=(0, -.12))
        steel.cyl(.11, .14, loc=(s * .44, .15, zt), rot=ACROSS, seg=10, bevel=0)
        steel.limb((s * .52, .7, .78), (s * .52, .3, zt + .3), .11, .11, bevel=.01)               # equilibrators
        steel.cyl(.075, .42, loc=(s * .52, .62, .92), rot=(-.75, 0, 0), seg=8, bevel=0)
    # Gun shield: two sloped plates either side of the barrel slot, a bridge under the slot and wings.
    shield = a.part('Gun_shield', 'Team', t)
    for s in (-1, 1):
        shield.box((.95, .07, .82), loc=(s * .66, -.56, 1.3), rot=(-.14, 0, 0), bevel=.02, seg=1, taper=(.94, 1))
        shield.box((.5, .07, .66), loc=(s * 1.3, -.42, 1.24), rot=(-.14, 0, s * .55), bevel=.02, seg=1)
    shield.box((.42, .07, .3), loc=(0, -.54, 1.04), rot=(-.14, 0, 0), bevel=.015, seg=1)
    shield.box((1.9, .06, .3), loc=(0, -.5, .56), rot=(.12, 0, 0), bevel=.015, seg=1)                 # lower apron
    armor.box((.24, .12, .18), loc=(-.62, -.66, 1.78), bevel=.02, seg=1)
    a.part('Sight', 'Glass', t).box((.16, .03, .1), loc=(-.62, -.73, 1.8), bevel=0)
    # Cradle, recuperators, breech and the long tube.
    pitch = math.radians(20)
    rot = (-pitch, 0, 0)
    at = _axis((0, .15, zt), pitch)
    armor.box((.4, 1.7, .34), loc=tuple(at(.2)), rot=rot, bevel=.04, seg=1)
    for up in (.25, -.23):
        steel.cyl(.085, 1.6, loc=tuple(at(.35, up)), rot=(R90 - pitch, 0, 0), seg=10, bevel=.01, bseg=1)
        steel.cyl(.1, .1, loc=tuple(at(-.45, up)), rot=(R90 - pitch, 0, 0), seg=10, bevel=0)
    steel.box((.38, .5, .38), loc=tuple(at(-.8)), rot=rot, bevel=.03, seg=1)                          # breech
    steel.box((.3, .7, .06), loc=tuple(at(-1.3, -.14)), rot=rot, bevel=0)                             # loading tray
    steel.torus(.12, .02, loc=(-.32, .32, .98), rot=(0, R90, 0), seg=10, ring=4)                    # handwheels
    steel.torus(.12, .02, loc=(.32, .32, .98), rot=(0, R90, 0), seg=10, ring=4)
    base = at(1.05)
    tip = _barrel(a, t, start_y=base.y, length=4.05, radius=.1, height=base.z, pitch=pitch, seg=14,
                  style='baffle', brake=(.34, .5, .3), sleeve=(.04, .3, .13), bands=(.5,))
    a.pivot('Muzzle_main', tip, t)
    # Ready rounds riding on the trails.
    for s in (-1, 1):
        crate(a, (s * 1.2, .95, .02), size=(.7, .38, .3), yaw=-s * .5, parent=t, band=s < 0)
    shells(a, (.0, 1.35, .1), 2, 1, parent=t, pitch=.2)
    # Second weapon: a heavy machine gun guarding the pit from a sandbagged post on the front right of the
    # ring wall (Mount_mg / Muzzle_mg, not on the Turret): a timber post through the wall with three bags
    # packed round its foot on the top course. The howitzer's barrel sweeps 0.6 m over it.
    u = math.radians(-55)
    post = Vector((3.02 * math.cos(u), 3.02 * math.sin(u), 0))
    n, tg = Vector((math.cos(u), math.sin(u), 0)), Vector((-math.sin(u), math.cos(u), 0))
    a.part('HMG_post', 'LogWood').cyl(.075, .66, loc=tuple(post + Vector((0, 0, .8))), seg=8, bevel=0)
    for off, yaw in ((n * .2, u + R90), (tg * .42 - n * .02, u), (-tg * .42 - n * .02, u)):
        bag(bags, tuple(post + off + Vector((0, 0, .95))), (.6, .34, .24), yaw=yaw)
    wpn.hmg(a, tuple(post + Vector((0, 0, 1.12))), post=.16, ammo=1)


# ----------------------------------------------------------------------------- guard_tower
def guard_tower(a):
    """Steel and concrete guard tower (3.5 x 3.5 m footprint, about 11 m): a concrete blockhouse with a
    steel door and firing slits, four H-beam legs with X-bracing, a caged ladder up the right side
    through a hatch to a walkway with a railing round a Team steel cabin with a glazed band (some
    panes lit), and a roof deck behind a low steel parapet carrying a roof MG on `Turret` (front
    left) and a searchlight on its own `Searchlight` pivot (rear right, Lamp lens facing the pivot's
    -Y), plus a 40 mm grenade launcher on `Mount_gun` at the roof's front right. The MG's barrel clears
    the parapet and never reaches the searchlight or the grenade launcher."""
    conc = a.part('Blockhouse', 'Concrete')
    conc.prism(chamfered(3.5, 3.5, .35), .32, loc=(0, 0, .14), axis='Z', bevel=.04, seg=1)
    conc.box((2.5, 2.5, 2.6), loc=(0, 0, 1.55), bevel=.06, seg=1, taper=(.95, .95))
    conc.box((2.7, 2.7, .16), loc=(0, 0, 2.86), bevel=.04, seg=1)
    fbox(a.part('Door', 'Team'), '-y', (0, -1.2, 1.2), (.9, .08, 1.8), out=0.0, bevel=.015)
    steel = a.part('Fittings', 'Steel')
    fbox(steel, '-y', (0, -1.2, 2.17), (1.1, .12, .1), out=.02)
    fbox(steel, '-y', (.3, -1.24, 1.2), (.06, .06, .16), out=.03)
    caged_lamp(a, '-y', (.72, -1.19, 2.25))
    for face, p in (('-x', (-1.2, 0, 2.2)), ('+x', (1.2, -.5, 2.2)), ('+y', (0, 1.2, 2.2))):
        fbox(a.part('Slits', 'Charred'), face, p, (.9, .06, .14), out=.0)
        fbox(steel, face, (p[0], p[1], p[2] + .12), (1.05, .1, .05), out=.02)
    a.part('Stencil', 'Hazard').box((.7, .03, .2), loc=(-.72, -1.215, 2.05), bevel=0)
    # Legs, bracing, walkway.
    frame = a.part('Tower_frame', 'Armor')
    zw = 7.5
    b0, b1, z0, z1 = 1.5, 1.3, .28, zw

    def leg(z):
        return b0 + (b1 - b0) * (z - z0) / (z1 - z0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame.limb((sx * b0, sy * b0, z0 - .02), (sx * b1, sy * b1, z1 + .02), .2, .2, bevel=0)
            a.part('Base_plates', 'Steel').box((.36, .36, .06), loc=(sx * b0, sy * b0, .31), bevel=0)
    for za, zb in ((3.0, 5.2), (5.2, zw - .12)):
        pa, pb = leg(za), leg(zb)
        for s in (-1, 1):
            frame.limb((-pa, s * pa, za), (pb, s * pb, zb), .08, .06, bevel=0)
            frame.limb((pa, s * (pa + .03), za), (-pb, s * (pb + .03), zb), .08, .06, bevel=0)
            frame.limb((s * pa, -pa, za), (s * pb, pb, zb), .06, .08, bevel=0)
            frame.limb((s * (pa + .03), pa, za), (s * (pb + .03), -pb, zb), .06, .08, bevel=0)
        for s in (-1, 1):
            frame.limb((-pb, s * pb, zb), (pb, s * pb, zb), .1, .1, bevel=0)
            frame.limb((s * pb, -pb, zb), (s * pb, pb, zb), .12, .12, bevel=0)
    a.part('Walkway', 'Armor').box((3.5, 3.5, .14), loc=(0, 0, zw + .07), bevel=.02, seg=1)
    grate = a.part('Walkway_grate', 'Undercarriage')
    for s in (-1, 1):
        grate.box((3.3, .44, .02), loc=(0, s * 1.46, zw + .14), bevel=0)
        grate.box((.44, 2.44, .02), loc=(s * 1.46, 0, zw + .14), bevel=0)
    rail = a.part('Railing', 'Steel')
    e, zd = 1.7, zw + .14
    _railing(rail, [(e, .42, zd), (e, e, zd), (-e, e, zd), (-e, -e, zd), (e, -e, zd), (e, -.42, zd)], h=1.0, post=.05,
             rail=.028, every=1.15)
    k = e + .04
    a.part('Kick_plates', 'Team').shell([(-k, -k), (k, -k), (k, k), (-k, k)], .16, .03, loc=(0, 0, zw + .13))
    # Caged ladder on the right side, from the ground up through a hatch in the walkway.
    lx = 1.64
    ladder(a.part('Ladder', 'Steel'), (lx, 0, .3), zw + 1.05, R90, width=.5, step=.34, rung=.028)
    cage = a.part('Ladder_cage', 'Steel')
    for z in (3.2, 4.5, 5.8, 7.0):
        cage.tube([(lx, -.27, z), (lx + .26, -.3, z), (lx + .38, 0, z), (lx + .26, .3, z), (lx, .27, z)], .018, seg=4,
                  caps=False)
    for dx, y in ((.26, -.3), (.38, 0), (.26, .3)):
        cage.box((.03, .03, 4.0), loc=(lx + dx, y, 5.1), bevel=0)
    fr = a.part('Hatch_frame', 'Steel')
    for s in (-1, 1):
        fr.box((.5, .06, .05), loc=(lx - .08, s * .33, zw + .16), bevel=0)
    fr.box((.06, .76, .05), loc=(lx - .33, 0, zw + .175), bevel=0)
    a.part('Hatch_lid', 'Armor').box((.05, .62, .5), loc=(lx - .36, 0, zw + .41), bevel=.01, seg=1)
    # Cabin with a glazed band.
    cz0, cz1 = zw + .14, zw + 2.3
    cab = a.part('Cabin', 'Team')
    cab.box((2.5, 2.5, .9), loc=(0, 0, cz0 + .45), bevel=.03, seg=1)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        cab.box((.2, .2, cz1 - cz0), loc=(sx * 1.16, sy * 1.16, (cz0 + cz1) / 2), bevel=.02, seg=1)
    cab.box((2.56, 2.56, .36), loc=(0, 0, cz1 - .18), bevel=.03, seg=1)
    glass = a.part('Cabin_glass', 'Glass')
    lit = a.part('Cabin_lit', 'Lamp')
    band0, band1 = cz0 + .9, cz1 - .36
    for face, (nx, ny) in (('-y', (0, -1)), ('+x', (1, 0)), ('+y', (0, 1)), ('-x', (-1, 0))):
        for k, u in enumerate((-.62, 0, .62)):
            part = lit if (face, k) in (('-x', 1), ('+y', 0), ('-y', 2), ('+x', 0)) else glass
            p = (nx * 1.2 + (u if ny else 0), ny * 1.2 + (u if nx else 0), (band0 + band1) / 2)
            fbox(part, face, p, (.56, .06, band1 - band0 + .04), out=-.01)
            fbox(a.part('Mullions', 'Armor'), face, (p[0] + (.31 if ny else 0), p[1] + (.31 if nx else 0), p[2]),
                 (.05, .05, band1 - band0 + .02), out=.012)
    a.part('Cabin_inner', 'Undercarriage').box((2.28, 2.28, band1 - band0 + .02), loc=(0, 0, (band0 + band1) / 2),
                                               bevel=0)
    fbox(a.part('Cabin_door', 'Armor'), '+x', (1.25, -.62, cz0 + .45), (.6, .04, .8), out=.012, bevel=.01)
    # Roof deck: low parapet, MG and searchlight.
    zr = cz1
    top = zr + .14
    a.part('Roof', 'Armor').box((2.8, 2.8, .16), loc=(0, 0, zr + .06), bevel=.03, seg=1)
    a.part('Parapet', 'Team').shell([(-1.38, -1.38), (1.38, -1.38), (1.38, 1.38), (-1.38, 1.38)], .34, .05,
                                    loc=(0, 0, top - .02))
    a.part('Parapet_cap', 'Steel').shell([(-1.4, -1.4), (1.4, -1.4), (1.4, 1.4), (-1.4, 1.4)], .04, .09,
                                         loc=(0, 0, top + .3))
    ladder(a.part('Roof_ladder', 'Steel'), (1.5, .75, zw + .14), zr + .75, R90, width=.44, step=.34, rung=.028)
    _antenna(a, None, -1.2, 1.2, top, 1.6)
    a.part('Aircon', 'Fuel').box((.6, .45, .4), loc=(-.8, 1.02, top + .18), bevel=.03, seg=1)
    a.part('Aircon_fan', 'Rubber').cyl(.15, .03, loc=(-.8, 1.02, top + .39), seg=10, bevel=0)
    t = a.pivot('Turret', (-.45, -.45, top))
    post = a.part('MG_post', 'Steel', t)
    post.cyl(.2, .08, loc=(0, 0, .03), seg=10, bevel=.01, bseg=1)
    post.cyl(.06, .56, loc=(0, 0, .34), seg=8, bevel=0)
    mg = a.part('MG', 'Armor', t)
    zc = .7
    mg.box((.16, .46, .18), loc=(0, -.02, zc), bevel=.025, seg=1)
    mg.box((.06, .16, .1), loc=(0, .26, zc - .07), rot=(.35, 0, 0), bevel=0)
    a.part('MG_ammo', 'Crate', t).box((.14, .22, .16), loc=(.15, .02, zc - .03), bevel=.02, seg=1)
    a.part('MG_shield', 'Team', t).box((.52, .04, .34), loc=(0, -.28, zc + .04), rot=(-.12, 0, 0), bevel=.012, seg=1,
                                       taper=(.8, 1))
    a.part('Main_cannon', 'Steel', t).cyl(.03, .66, loc=(0, -.58, zc), rot=FORWARD, seg=8, bevel=0)
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.045, .13, loc=(0, -.94, zc), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_main', (0, -1.01, zc), t)
    # Second weapon: a 40 mm grenade launcher on a pedestal at the front right of the roof deck (Mount_gun /
    # Muzzle_gun): the barrel clears the parapet, the launcher stays out of the roof MG's reach (its ammunition
    # can on the outer side) and far from the searchlight.
    wpn.agl(a, (.95, -.95, top), post=.45, ammo=1)
    a.part('Searchlight_post', 'Steel').cyl(.1, .36, loc=(.8, .8, top + .16), seg=8, bevel=0)
    searchlight(a, 'Searchlight', (.8, .8, top + .34), r=.28, length=.5)
    _moving_pivots(a, {'Searchlight'})


# ----------------------------------------------------------------------------- command_hq
def _t_wall(a, x, y, yaw=0.0, length=1.45, h=3.2):
    """Precast T-wall blast barrier standing on (x, y): an inverted-T section with a Team band near the
    top of both faces."""
    m = _frame((x, y, 0), (0, 0, yaw))
    prof = [(-.6, -.02), (.6, -.02), (.6, .26), (.2, .42), (.15, h), (-.15, h), (-.2, .42), (-.6, .26)]
    a.part('T_walls', 'Concrete').prism(prof, length, loc=m @ Vector((0, 0, 0)), rot=(0, 0, yaw), axis='X', bevel=0)
    hw = .2 - .05 * (2.45 - .42) / (h - .42)
    for s in (-1, 1):
        a.part('T_wall_bands', 'Team').box((length - .12, .03, .3), loc=m @ Vector((0, s * (hw + .005), 2.45)),
                                           rot=(0, 0, yaw), bevel=0)


def _slit_window(a, face, p, w=1.0, h=.32, lit=True, visor=True):
    """Armoured window: steel frame, a lit (Lamp) or dark (Glass) pane and a steel visor above."""
    fbox(a.part('Window_frames', 'Armor'), face, p, (w + .14, .1, h + .12), out=.03)
    fbox(a.part('Lit_windows' if lit else 'Windows', 'Lamp' if lit else 'Glass'), face, p, (w, .06, h), out=.065)
    if visor:
        fbox(a.part('Window_visors', 'Armor'), face, slide(face, p, 0, h / 2 + .1), (w + .24, .3, .06), out=.15)


def command_hq(a):
    """Fortified command bunker, the Siege target (16 x 14 m): a battered concrete bunker block with a
    parapet and an asphalt roof, a raised command room with a band of armoured, mostly lit windows
    and a Team roof plate under a satellite dish spinning on `Radar`, an entrance portal with a
    hazard-framed blast door, a lit Team sign and lamps, T-wall blast walls with Team bands and two
    Team flags in front, a workshop annex with a roller door, a generator yard under a camouflage
    net, a roof lookout ring of sandbags, and a 15 m lattice comms mast with antennas and an
    obstruction light."""
    rng = random.Random(77)
    a.part('Apron', 'Concrete').prism(chamfered(15.8, 13.8, .8), .22, loc=(0, 0, .09), axis='Z', bevel=.04, seg=1)
    blk = a.part('Bunker', 'Concrete')
    blk.box((10.0, 7.0, 4.85), loc=(0, 1.0, .18 + 2.425), bevel=.12, seg=1, taper=(.96, .95))
    top = 5.03
    rim(a.part('Parapet', 'Concrete'), -4.78, 4.78, -2.3, 4.3, top - .03, .5, .32, bevel=.04)
    a.part('Roof_deck', 'Asphalt').box((9.1, 6.2, .06), loc=(0, 1.0, top), bevel=0)
    # Command room.
    ux0, ux1, uy0, uy1, uz1 = -3.0, 2.6, -.9, 3.3, top + 2.38
    a.part('Command_room', 'Concrete').box((ux1 - ux0, uy1 - uy0, uz1 - top + .02),
                                           loc=((ux0 + ux1) / 2, (uy0 + uy1) / 2, (top - .02 + uz1) / 2),
                                           bevel=.08, seg=1)
    rim(a.part('Parapet', 'Concrete'), ux0 - .02, ux1 + .02, uy0 - .02, uy1 + .02, uz1 - .02, .3, .22, bevel=0)
    a.part('Roof_plate', 'Team').box((4.6, 3.2, .04), loc=((ux0 + ux1) / 2, (uy0 + uy1) / 2, uz1), bevel=0)
    zw = top + 1.25
    for i, x in enumerate((-2.3, -1.25, -.2, .85, 1.9)):
        _slit_window(a, '-y', (x, uy0, zw), w=.8, h=.5, lit=i != 3)
    for i, y in enumerate((.2, 2.2)):
        _slit_window(a, '+x', (ux1, y, zw), w=.8, h=.5, lit=i == 0)
        _slit_window(a, '-x', (ux0, y, zw), w=.8, h=.5, lit=i == 1)
    fbox(a.part('Room_door', 'Armor'), '+x', (ux1, 1.2, top + .95), (.9, .08, 1.9), out=.02, bevel=.015)
    # Satellite dish on the command room roof.
    dx, dy = (ux0 + ux1) / 2, 1.4
    a.part('Dish_pedestal', 'Steel').cyl(.4, .5, loc=(dx, dy, uz1 + .25), seg=10, bevel=.02, bseg=1)
    r = a.pivot('Radar', (dx, dy, uz1 + .5))
    a.part('Radar_turntable', 'Armor', r).cyl(.46, .14, loc=(0, 0, .07), seg=12, bevel=.02, bseg=1)
    frame = a.part('Radar_frame', 'Steel', r)
    frame.box((.34, .34, .6), loc=(0, .1, .42), bevel=.03, seg=1)
    frame.box((.7, .5, .4), loc=(0, .5, .5), bevel=.04, seg=1)
    _dish(a.part('Radar_dish', 'Medical', r), (0, .28, .95), 1.3, 1.3, depth=.38, seg=14, tilt=.55)
    for sx in (-1, 1):
        frame.limb((sx * 1.05, -.3, .6), (0, -1.05, 1.55), .04, .04, bevel=0)
    frame.limb((0, -.25, 2.0), (0, -1.05, 1.55), .04, .04, bevel=0)
    a.part('Radar_horn', 'Armor', r).box((.22, .26, .2), loc=(0, -1.1, 1.57), bevel=.03, seg=1)
    # Entrance portal: blast door, hazard frame, Team sign, lamps, canopy.
    conc = a.part('Portal', 'Concrete')
    conc.box((3.4, 1.8, 3.2), loc=(0, -3.2, .18 + 1.6), bevel=.08, seg=1)
    conc.box((3.8, 2.2, .3), loc=(0, -3.25, 3.46), bevel=.05, seg=1)
    fy = -4.1
    fbox(a.part('Blast_door', 'Steel'), '-y', (0, fy, 1.33), (2.0, .1, 2.3), out=.02, bevel=.02)
    for x in (-.5, .5):
        fbox(a.part('Door_ribs', 'Armor'), '-y', (x, fy, 1.33), (.12, .06, 2.2), out=.08)
    for k in range(6):                                                                         # hazard frame
        mat = 'SafetyStripe' if k % 2 else 'Charred'
        for s in (-1, 1):
            fbox(a.part('Door_hazard', mat), '-y', (s * 1.17, fy, .38 + k * .4), (.26, .04, .38), out=.01)
    for k in range(6):
        fbox(a.part('Door_hazard', 'SafetyStripe' if k % 2 else 'Charred'), '-y', (-1.0 + k * .4, fy, 2.7),
             (.38, .04, .22), out=.01)
    fbox(a.part('Sign', 'Team'), '-y', (0, fy, 3.02), (2.4, .05, .38), out=.02)
    for s in (-1, 1):
        caged_lamp(a, '-y', (s * 1.45, fy, 2.3))
    # T-wall blast walls and flags in front.
    for x in (-1.5, 0.0, 1.5):
        _t_wall(a, x, -5.9)
    for x in (-6.9, -5.4, -3.9, 3.9, 5.4, 6.9):
        _t_wall(a, x, -5.15)
    flag(a, -2.8, -5.6, .2, 6.5, w=1.6, h=1.0, phase=.4)
    flag(a, 2.8, -5.6, .2, 6.5, w=1.6, h=1.0, phase=1.9)
    # Main block windows (front and right, above the annex).
    for i, x in enumerate((-3.7, -2.3, 2.3, 3.7)):
        _slit_window(a, '-y', (x, -2.384, 3.4), lit=i in (0, 2))
    for i, y in enumerate((-.9, 1.4)):
        _slit_window(a, '+x', (4.847, y, 3.9), lit=i == 1)
    # Workshop annex on the right with a roller door.
    a.part('Annex', 'Concrete').box((2.9, 5.0, 2.72), loc=(6.2, .5, .18 + 1.36), bevel=.07, seg=1)
    rim(a.part('Parapet', 'Concrete'), 4.75, 7.65, -2.0, 3.0, 2.88, .3, .2, bevel=0)
    corrugated_wall(a.part('Roller_door', 'MetalSheet'), '-y', (6.25, -2.01), 2.2, .2, 2.35, pitch=.14, depth=.03)
    fr = a.part('Door_frame', 'Armor')
    for s in (-1, 1):
        fr.box((.16, .14, 2.3), loc=(6.25 + s * 1.18, -2.03, 1.33), bevel=0)
    fr.box((2.56, .16, .3), loc=(6.25, -2.04, 2.5), bevel=0)
    caged_lamp(a, '-y', (6.25, -2.0, 2.78))
    for x, y in ((5.6, 1.6), (6.8, 1.6)):
        a.part('Aircon', 'Fuel').box((.8, .9, .55), loc=(x, y, 3.13), bevel=.03, seg=1)
        a.part('Aircon_fans', 'Rubber').cyl(.28, .03, loc=(x, y, 3.415), seg=10, bevel=0)
    # Generator yard on the left under a camouflage net.
    for y in (-1.5, 1.5):
        generator(a, (-6.55, y, .2), yaw=R90, size=(2.2, 1.1, 1.3))
    for k, (x, y) in enumerate(((-7.45, -3.0), (-6.85, -3.25), (-7.45, 3.35))):
        a.part('Drums', 'BarrelRed').cyl(.29, .88, loc=(x, y, .63), seg=10, bevel=0)
    cab = a.part('Cables', 'Rubber')
    for y in (-1.5, 1.5):
        cab.tube([(-5.95, y + .3, .5), (-5.5, y + .4, .24), (-5.1, y + .5, .26), (-5.1, y + .5, 1.02)], .05, seg=5)
        a.part('Junction_boxes', 'Armor').box((.26, .3, .34), loc=(-5.06, y + .5, 1.15), bevel=.02, seg=1)
    poles = [(-7.75, -2.7, 2.9), (-5.3, -2.7, 2.9), (-7.75, 2.9, 2.9), (-5.3, 2.9, 2.9), (-6.5, .1, 3.2)]
    for x, y, h in poles:
        a.part('Net_poles', 'Wood').cyl(.06, h, loc=(x, y, .2 + h / 2 - .02), seg=6, bevel=0)

    def drape(x, y):
        return .2 + max(max(h - .4 * math.hypot(x - px, y - py) for px, py, h in poles), 2.1)
    camo_net(a, rng, -7.95, -5.1, -3.0, 3.25, drape, cells=(6, 12), garnish=26, seed=7.0)
    # Roof: lookout sandbag ring, hatch, vents, antennas and the cable tray to the mast.
    bags = a.part('Roof_sandbags', 'Sandbag')
    for i in range(1):
        bag_arc(bags, rng, .8 - i * .05, R90 + .6, R90 + TAU - .6, top + .14 + i * .2, size=(.62, .36, .22),
                half=i == 1, cx=3.6, cy=-1.2)
    a.part('Roof_hatch', 'Armor').box((.9, .9, .12), loc=(-3.9, -1.4, top + .07), bevel=.03, seg=1)
    for x, y in ((-3.9, 1.0), (-3.9, 2.6), (3.7, 3.2)):
        a.part('Vents', 'Steel').cyl(.18, .6, loc=(x, y, top + .3), seg=8, bevel=0)
        a.part('Vents', 'Steel').cyl(.28, .08, loc=(x, y, top + .62), seg=8, bevel=0)
    _antenna(a, None, -4.3, 4.14, top + .47, 2.6)
    _antenna(a, None, 1.4, 3.1, uz1 + .28, 3.2)
    mx, my = 6.3, 5.4
    a.part('Cable_tray', 'Steel').box((2.3, .3, .08), loc=(5.35, 4.5, 5.7), rot=(0, 0, .75), bevel=0)
    # Comms mast.
    a.part('Mast_footing', 'Concrete').box((1.9, 1.9, .45), loc=(mx, my, .3), bevel=.05, seg=1)
    lattice(a.part('Mast', 'Steel'), mx, my, .5, 13.0, .72, .26, 4, leg=.15, brace=.04)
    ant = a.part('Antennas', 'Steel')
    ant.cyl(.06, 2.6, loc=(mx, my, 14.2), seg=6, bevel=0)
    ant.cyl(.025, 2.0, loc=(mx, my, 16.4), seg=5, bevel=0)
    for z, yaw in ((11.8, .4), (12.7, 2.2)):                                                   # yagis
        m = _frame((mx, my, z), (0, 0, yaw))
        ant.box((1.9, .05, .05), loc=m @ Vector((.95, 0, 0)), rot=(0, 0, yaw), bevel=0)
        for k in range(5):
            ant.box((.04, .8 - k * .08, .03), loc=m @ Vector((.35 + k * .35, 0, 0)), rot=(0, 0, yaw), bevel=0)
    for k in range(3):                                                                         # panel antennas
        u = k * TAU / 3 + .5
        a.part('Panel_antennas', 'Medical').box((.3, .12, 1.1),
                                                loc=(mx + .42 * math.cos(u), my + .42 * math.sin(u), 10.5),
                                                rot=(0, 0, u + R90), bevel=0)
    _dish(a.part('Mast_dish', 'Medical'), (mx, my - .55, 8.6), .55, .55, depth=.16, seg=10, tilt=.1)
    a.part('Obstruction_lights', 'Alloy').sphere(.1, loc=(mx, my, 17.45), seg=6, rings=4)


# ----------------------------------------------------------------------------- base_wall
def base_wall(a):
    """Perimeter wall segment (8 x 1.2 m, 3 m + wire): four battered precast panels with a Team band on
    both faces, on a continuous footing, with Y-outriggers carrying a concertina coil and two strands.
    Both ends are flush at x = +-4 m and the coil ends in phase, so segments line up end to end."""
    L = 8.0
    a.part('Footing', 'Concrete').prism([(-.6, -.02), (.6, -.02), (.6, .14), (.5, .24), (-.5, .24), (-.6, .14)], L,
                                        axis='X', bevel=.03, seg=1)
    n, gap = 4, .015
    lp = (L - gap * (n - 1)) / n

    def half(z):
        return .28 - .11 * (z - .2) / 2.8
    prof = [(-.28, .2), (.28, .2), (.17, 3.0), (-.17, 3.0)]
    z0, z1 = 2.3, 2.62
    band = [(-half(z0) - .015, z0), (half(z0) + .015, z0), (half(z1) + .015, z1), (-half(z1) - .015, z1)]
    post = a.part('Outriggers', 'Armor')
    for i in range(n):
        x = -L / 2 + lp / 2 + i * (lp + gap)
        a.part('Panels', 'Concrete').prism(prof, lp, loc=(x, 0, 0), axis='X', bevel=.04, seg=1)
        a.part('Wall_band', 'Team').prism(band, lp - .02, loc=(x, 0, 0), axis='X', bevel=0)
        for s in (-1, 1):                                                                      # lifting anchors
            a.part('Anchors', 'Steel').box((.12, .06, .06), loc=(x + s * .55, 0, 3.01), bevel=0)
        post.box((.08, .08, .5), loc=(x, 0, 3.1), bevel=0)
        for s in (-1, 1):
            post.limb((x + (s + 1) * .0125, 0, 3.28), (x + (s + 1) * .0125, s * .34, 3.66), .06, .06, bevel=0)
        a.part('Stencil', 'Hazard').box((.28, .52, .12), loc=(x - .6, 0, 1.15), bevel=0)
    wire = a.part('Razor_wire', 'Steel')
    coil(wire, -L / 2, L / 2, 0, 3.36, .29, pitch=.4, pts=8, wire=.018)
    for s in (-1, 1):
        wire.tube([(-L / 2, s * .34, 3.66), (L / 2, s * .34, 3.66)], .012, seg=3, caps=False)


# ----------------------------------------------------------------------------- base_gate
def base_gate(a):
    """Base gate (9 x 2 m, open): two concrete pillars with Team panels, hazard-banded inner faces and
    lit lanterns on their caps, an overhead truss with a Team sign on both sides and two floodlights,
    and a red and white barrier arm raised almost upright on its housing (counterweight, rest fork on
    the far pillar). Units drive through the 7 m gap."""
    for s in (-1, 1):
        x = s * 4.0
        a.part('Pillars', 'Concrete').box((1.0, 1.8, 4.1), loc=(x, 0, 2.03), bevel=.06, seg=1, taper=(.94, .96))
        a.part('Pillar_caps', 'Concrete').box((1.2, 2.0, .24), loc=(x, 0, 4.18), bevel=.04, seg=1)
        for face, y in (('-y', -.9), ('+y', .9)):
            fbox(a.part('Pillar_panels', 'Team'), face, (x, y + (.02 if y < 0 else -.02), 2.4), (.7, .04, 2.2), out=0.0)
        inner = '-x' if s > 0 else '+x'
        for k in range(5):
            fbox(a.part('Pillar_bands', 'SafetyStripe' if k % 2 else 'Charred'), inner, (x - s * .5, 0, .12 + k * .22),
                 (1.7, .04, .22), out=0.0)
        # Lantern on the cap.
        a.part('Lantern_posts', 'Steel').cyl(.06, .34, loc=(x, 0, 4.45), seg=6, bevel=0)
        a.part('Lanterns', 'Lamp').box((.28, .28, .36), loc=(x, 0, 4.78), bevel=.02, seg=1)
        a.part('Lantern_caps', 'Armor').box((.38, .38, .07), loc=(x, 0, 4.98), bevel=.015, seg=1)
        a.part('Lantern_caps', 'Armor').box((.34, .34, .06), loc=(x, 0, 4.6), bevel=0)
        # Truss column.
        a.part('Truss', 'Armor').box((.22, .22, 1.9), loc=(x, .55, 5.15), bevel=0)
    fbox(a.part('Control_box', 'Armor'), '-y', (-4.0, -.87, 1.3), (.5, .2, .6), out=.1, bevel=.02)
    a.part('Control_lamp', 'Alloy').box((.08, .03, .08), loc=(-3.85, -1.08, 1.5), bevel=0)
    truss = a.part('Truss', 'Armor')
    for z in (5.3, 6.1):
        truss.box((8.2, .14, .14), loc=(0, .55, z), bevel=0)
    for k in range(8):
        x0, x1 = -4.0 + k, -3.0 + k
        za, zb = (5.3, 6.1) if k % 2 == 0 else (6.1, 5.3)
        truss.limb((x0, .55, za), (x1, .55, zb), .08 + .02 * (k % 2), .08 + .02 * (k % 2), bevel=0)
    for side, yb in ((-1, .55 - .09), (1, .55 + .09)):
        a.part('Sign_backing', 'Charred').box((3.56, .02, .96), loc=(0, yb + side * .005, 5.7), bevel=0)
        a.part('Gate_sign', 'Team').box((3.4, .05, .8), loc=(0, yb + side * .04, 5.7), bevel=.01, seg=1)
        for sx in (-1, 1):
            a.part('Sign_stripes', 'Hazard').box((.32, .03, .8), loc=(sx * 1.42, yb + side * .075, 5.7), bevel=0)
    for x in (-2.6, 2.6):
        flood_head(a, (x, .55, 6.58), yaw=0.0, tilt=.55, size=(.56, .26, .38))
    # Barrier: housing on the right, arm raised to 80 degrees towards -X, rest fork on the left.
    hx, hy = 3.26, -.62
    a.part('Barrier_housing', 'Armor').box((.42, .46, 1.0), loc=(hx, hy, .5), bevel=.03, seg=1)
    a.part('Barrier_housing_top', 'SafetyStripe').box((.44, .48, .08), loc=(hx, hy, .98), bevel=.01, seg=1)
    a.part('Barrier_hub', 'Steel').cyl(.12, .56, loc=(hx, hy, 1.1), rot=(R90, 0, 0), seg=10, bevel=.01, bseg=1)
    ang = math.radians(80)
    d = Vector((-math.cos(ang), 0, math.sin(ang)))
    piv = Vector((hx, hy - .3, 1.1))
    seg_len = 6.3 / 7
    for k in range(7):
        a.part('Barrier_arm', 'BarrelRed' if k % 2 == 0 else 'PlasterWhite').limb(
            tuple(piv + d * (.1 + k * seg_len)), tuple(piv + d * (.1 + (k + 1) * seg_len)), .1, .12, bevel=0)
    a.part('Barrier_weight', 'Armor').limb(tuple(piv + d * .12), tuple(piv - d * .5), .24, .26, bevel=.02)
    a.part('Barrier_tip', 'Lamp').box((.15, .15, .12), loc=tuple(piv + d * (.1 + 7 * seg_len + .06)), bevel=0)
    fork = a.part('Barrier_rest', 'Steel')
    fork.box((.08, .08, 1.0), loc=(-3.3, hy - .3, .5), bevel=0)
    for s in (-1, 1):
        fork.box((.04, .04, .16), loc=(-3.3, hy - .3 + s * .08, 1.06), bevel=0)


# ----------------------------------------------------------------------------- floodlight_mast
def floodlight_mast(a):
    """Floodlight mast (1.2 x 1.2 m, 12 m): a concrete footing, a four-legged lattice with an inner
    ladder, a railed service platform and a cross headframe carrying four big floodlights (Lamp
    lenses) aimed down to all four sides, an obstruction light, and a Team control box and conduit
    at the foot."""
    a.part('Footing', 'Concrete').box((1.2, 1.2, .52), loc=(0, 0, .24), bevel=.06, seg=1, taper=(.9, .9))
    z0, z1 = .48, 10.2
    lattice(a.part('Mast', 'Armor'), 0, 0, z0, z1, .42, .26, 5, leg=.125, brace=.025)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Base_plates', 'Steel').box((.2, .2, .04), loc=(sx * .42, sy * .42, .5), bevel=0)
    ladder(a.part('Ladder', 'Steel'), (0, -.08, .5), z1, 0.0, width=.34, step=.5, rung=.028)
    a.part('Platform', 'Armor').box((1.5, 1.5, .1), loc=(0, 0, z1 + .05), bevel=.02, seg=1)
    a.part('Grating', 'Undercarriage').box((1.3, 1.3, .02), loc=(0, 0, z1 + .105), bevel=0)
    e = .7
    loop_rail(a.part('Railing', 'Steel'), [(-e, -e, z1 + .1), (e, -e, z1 + .1), (e, e, z1 + .1), (-e, e, z1 + .1)],
              h=.85, post=.04, rail=.022, every=.75)
    hf = a.part('Headframe', 'Armor')
    zb = z1 + 1.1
    hf.box((.16, .16, 1.25), loc=(0, 0, z1 + .675), bevel=0)
    hf.box((1.9, .12, .12), loc=(0, 0, zb), bevel=0)
    hf.box((.12, 1.9, .12), loc=(0, 0, zb + .02), bevel=0)
    for x, y, yaw in ((0, -.85, 0.0), (0, .85, math.pi), (.85, 0, R90), (-.85, 0, -R90)):
        flood_head(a, (x, y, zb + .47 + (.02 if x == 0 else 0)), yaw=yaw, tilt=.4, size=(.72, .3, .5))
    a.part('Obstruction_pole', 'Steel').cyl(.03, .9, loc=(0, 0, zb + .5), seg=5, bevel=0)
    a.part('Obstruction_light', 'Alloy').sphere(.07, loc=(0, 0, zb + .98), seg=8, rings=5)
    a.part('Control_box', 'Team').box((.5, .3, .8), loc=(0, -.76, .38), bevel=.02, seg=1)
    a.part('Control_lamp', 'Lamp').box((.08, .03, .08), loc=(.15, -.915, .62), bevel=0)
    a.part('Conduit', 'Rubber').tube([(.12, -.7, .76), (.28, -.5, 1.1), (.33, -.37, 1.6), (.3, -.3, z1 - .1)], .03,
                                     seg=5)


# ----------------------------------------------------------------------------- fuel_depot
def fuel_depot(a):
    """Fuel depot (10 x 8 m): three horizontal fuel tanks on concrete saddles inside an earth bund,
    each with a Team band, steel straps, a manhole and a vent; a catwalk with a railing and a stair
    over the bund, outlet pipes with red valves into a header, a pump skid in the gap at the front,
    hazard signs and a fire extinguisher stand."""
    rng = random.Random(88)
    hx, hy, rc = 4.45, 3.45, .8
    path = [(1.25, -hy), (2.2, -hy)]
    for cx, cy, a0 in ((hx - rc, -hy + rc, -R90), (hx - rc, hy - rc, 0.0), (-hx + rc, hy - rc, R90),
                       (-hx + rc, -hy + rc, math.pi)):
        path += [(cx + rc * math.cos(a0 + k * R90 / 3), cy + rc * math.sin(a0 + k * R90 / 3)) for k in range(4)]
        if cx > 0 and cy < 0:
            path.append((hx, 0.0))
        if cx < 0 and cy > 0:
            path.append((-hx, 0.0))
    path += [(-2.2, -hy), (-1.25, -hy)]
    last = len(path) - 1
    sweep(a.part('Bund', 'Dirt'), path, [(.55, -.02), (.18, 1.05), (-.18, 1.05), (-.55, -.02)],
          scale=lambda i: .12 if i in (0, last) else 1.0)
    tufts = a.part('Tufts', 'Grass', flat=True)
    for k, (x, y) in enumerate(((-3.2, 3.45), (1.5, 3.45), (4.45, 1.8), (-4.45, -1.2), (3.3, -3.45), (-3.6, -3.45))):
        tufts.ico((.3, .24, .12), loc=(x, y, 1.02), sub=1, jitter=.35, seed=k * 1.9)
    a.part('Bund_floor', 'Concrete').box((8.3, 6.3, .08), loc=(0, 0, .02), bevel=0)
    steel = a.part('Steel', 'Steel')
    for i, x in enumerate((-2.8, 0.0, 2.8)):
        body = a.part('Tanks', 'Fuel')
        body.cyl(1.15, 4.9, loc=(x, 0, 1.62), rot=FORWARD, seg=18, bevel=0)
        for s, rot in ((-1, FORWARD), (1, BACKWARD)):
            body.lathe([(1.15, 0), (1.0, .22), (.62, .38), (0, .44)], loc=(x, s * 2.43, 1.62), rot=rot, seg=18)
        a.part('Tank_bands', 'Team').cyl(1.165, .5, loc=(x, .9, 1.62), rot=FORWARD, seg=18, bevel=0)
        for y in (-1.7, 1.7):
            a.part('Saddles', 'Concrete').box((1.9, .5, .75), loc=(x, y, .36), bevel=.03, seg=1)
            a.part('Straps', 'Armor').cyl(1.165, .08, loc=(x, y, 1.62), rot=FORWARD, seg=18, bevel=0)
        steel.cyl(.3, .14, loc=(x, -1.1, 2.79), seg=10, bevel=.02, bseg=1)                            # manhole
        steel.cyl(.06, .5, loc=(x + .5, 1.6, 2.92), seg=6, bevel=0)                                  # vent
        steel.cyl(.12, .06, loc=(x + .5, 1.6, 3.18), seg=6, bevel=0)
        pipe = a.part('Pipes', 'Pipe')
        pipe.tube([(x + .3, -2.55, .8), (x + .3, -2.86, .8), (x + .3, -2.86, .42)], .08, seg=8)
        a.part('Valves', 'BarrelRed').cyl(.14, .04, loc=(x + .3, -2.95, .66), rot=(R90, 0, 0), seg=8, bevel=0)
        steel.box((.06, .1, .06), loc=(x + .3, -2.9, .66), bevel=0)
    a.part('Pipes', 'Pipe').tube([(-2.9, -2.86, .4), (3.2, -2.86, .4)], .09, seg=8)
    a.part('Pipes', 'Pipe').tube([(.3, -2.86, .4), (.3, -3.3, .4), (.3, -3.45, .55)], .09, seg=8)
    for x in (-1.4, 1.5):
        a.part('Pipe_stands', 'Concrete').box((.3, .3, .32), loc=(x, -2.86, .16), bevel=.02, seg=1)
    # Catwalk over the tank tops and a stair down onto the bund on the right.
    zc = 2.8
    a.part('Catwalk', 'Armor').box((6.9, .7, .06), loc=(0, .5, zc + .03), bevel=0)
    for x in (-2.8, 0.0, 2.8):
        a.part('Catwalk_brackets', 'Steel').box((.1, .5, .1), loc=(x, .5, 2.78), bevel=0)
    a.part('Catwalk_grate', 'Undercarriage').box((6.7, .5, .02), loc=(0, .5, zc + .065), bevel=0)
    _railing(a.part('Catwalk_rail', 'Steel'), [(-3.4, .17, zc + .06), (3.4, .17, zc + .06)], h=.9, post=.04, rail=.022,
             every=1.15)
    st = a.part('Stair', 'Steel')
    for y in (.22, .78):
        st.limb((3.42, y, zc + .02), (4.6, y, 1.0), .06, .1, bevel=0)
    for k in range(5):
        t_ = (k + .5) / 5
        a.part('Stair_treads', 'Armor').box((.2, .6, .04), loc=(3.45 + 1.15 * t_, .5, zc + .06 - (zc - .98) * t_),
                                            bevel=0)
    # Pump skid in the gap, signs and a fire extinguisher stand.
    a.part('Pump_skid', 'Undercarriage').box((1.7, .8, .16), loc=(0, -3.55, .07), bevel=.02, seg=1)
    a.part('Pump_motor', 'Team').cyl(.26, .8, loc=(-.35, -3.55, .45), rot=ACROSS, seg=10, bevel=.03, bseg=1)
    steel.cyl(.3, .3, loc=(.3, -3.55, .48), rot=(R90, 0, 0), seg=10, bevel=.03, bseg=1)
    a.part('Pump_panel', 'Armor').box((.4, .2, .7), loc=(.65, -3.3, .5), bevel=.02, seg=1)
    a.part('Pump_lamp', 'Lamp').box((.08, .03, .08), loc=(.65, -3.415, .72), bevel=0)
    a.part('Hose', 'Rubber').tube([(.3, -3.72, .48), (.5, -3.9, .2), (-.3, -3.92, .14), (-.7, -3.75, .14)], .05, seg=5)
    for x in (-1.6, 1.6):
        hazard_sign(a, (x, -3.95, 0), size=.5, height=1.1)
    a.part('Extinguishers', 'BarrelRed').cyl(.1, .55, loc=(-.95, -3.8, .42), seg=8, bevel=.02, bseg=1)
    a.part('Extinguisher_stand', 'Armor').box((.3, .08, .7), loc=(-.95, -3.68, .35), bevel=0)


# ----------------------------------------------------------------------------- ammo_dump
def ammo_dump(a):
    """Ammunition dump (6 x 5 m): crate stacks and artillery rounds on pallets under a camouflage net on
    poles with guy ropes, a sandbag wall along one side, an explosives sign and a red warning flag.
    It explodes in game."""
    rng = random.Random(99)

    def pallet(x, y, yaw=0.0, w=1.2, d=1.0):
        m = _frame((x, y, 0), (0, 0, yaw))
        a.part('Pallets', 'Wood').box((w, d, .06), loc=m @ Vector((0, 0, .11)), rot=(0, 0, yaw), bevel=0)
        for k in (-1, 0, 1):
            a.part('Pallet_skids', 'LogWood').box((w - .04, .12, .1), loc=m @ Vector((0, k * (d / 2 - .08), .04)),
                                                  rot=(0, 0, yaw), bevel=0)
        return m
    z = .14
    m = pallet(-1.75, -1.5, .08)
    for j in (-.26, .26):
        crate(a, tuple(m @ Vector((0, j, z))), size=(1.1, .48, .36), yaw=.08)
    for i in (-.27, .27):
        crate(a, tuple(m @ Vector((i, 0, z + .36))), size=(.98, .48, .34), yaw=.08 + R90, band=i < 0)
    m = pallet(.2, -1.55, -.05)
    shells(a, tuple(m @ Vector((0, 0, z))), 4, 3, r=.075, h=.68, pitch=.2, yaw=-.05)
    m = pallet(1.95, -1.35, .22, w=1.3, d=.9)
    for k in range(3):
        crate(a, tuple(m @ Vector((0, (k - 1) * .31, z))), size=(1.25, .28, .26), yaw=.22, band=k == 1, mat='Crate')
    crate(a, tuple(m @ Vector((0, 0, z + .26))), size=(1.2, .3, .26), yaw=.22, band=False)
    for x, yaw in ((-1.9, .03), (0.0, -.04), (1.9, .05)):                                        # under the net
        m = pallet(x, .65, yaw)
        for j in (-.26, .26):
            crate(a, tuple(m @ Vector((0, j, z))), size=(1.1, .48, .36), yaw=yaw, band=False)
        for i in (-.27, .27):
            crate(a, tuple(m @ Vector((i, 0, z + .36))), size=(.98, .48, .34), yaw=yaw + R90, band=i > 0)
    for x in (-1.0, 1.15):
        crate(a, (x, 1.95, 0), size=(1.3, .8, .62), yaw=rng.uniform(-.06, .06))
    a.part('Loose_rounds', 'Gilded').cyl(.075, .44, loc=(.85, -2.25, .075), rot=ACROSS, seg=6, bevel=0)
    a.part('Loose_heads', 'Armor').lathe([(.073, 0), (.058, .14), (0, .26)], loc=(1.07, -2.25, .075), rot=(0, R90, 0),
                                         seg=6)
    # Sandbag wall along the left side.
    bags = a.part('Sandbags', 'Sandbag')
    for k in range(2):
        bag_run(bags, rng, (-2.78, -2.3), (-2.78, 2.3), .12 + k * .23, (.72, .38, .25), half=k == 1)
    # Camouflage net on poles with guy ropes.
    poles = [(-2.5, -.55, 2.3), (2.5, -.55, 2.3), (-2.5, 2.2, 2.1), (2.5, 2.2, 2.1), (0.0, .8, 2.75)]
    for x, y, h in poles:
        a.part('Net_poles', 'Wood').cyl(.05, h, loc=(x, y, h / 2 - .02), seg=6, bevel=0)
    rope = a.part('Guy_ropes', 'Rubber')
    for x, y, h in poles[:2]:
        rope.tube([(x, y, h - .1), (x * 1.15, y - .75, .02)], .012, seg=3)

    def drape(x, y):
        return max(max(h - .42 * math.hypot(x - px, y - py) for px, py, h in poles), 1.25)
    camo_net(a, rng, -2.9, 2.9, -.85, 2.5, drape, cells=(12, 7), garnish=30, seed=2.0,
             keep=lambda x, y: y > -.8 + .12 * math.sin(x * 2.3))
    hazard_sign(a, (2.55, -2.3, 0), size=.55, height=1.15)
    flag(a, -2.6, -2.25, 0, 2.6, w=.8, h=.5, phase=1.1, mat='BarrelRed')
    for x in (2.55, 2.75):
        a.part('Extinguishers', 'BarrelRed').cyl(.09, .5, loc=(x, -.95, .27), seg=8, bevel=.02, bseg=1)
    a.part('Extinguisher_stand', 'Armor').box((.5, .08, .6), loc=(2.65, -.83, .3), bevel=0)


# ----------------------------------------------------------------------------- vehicle_hangar
def vehicle_hangar(a):
    """Arched vehicle shed (14 x 10 m): a corrugated steel arch on a concrete slab, open at the front
    where a Team portal frame and a hazard-striped threshold frame the dark interior (Charred arch
    lining and an asphalt floor). Inside: a workbench, tyres, drums, crates, an engine hoist and two
    hanging lamps; outside: roof ventilators and a floodlight over the entrance. The closed back
    wall has a door."""
    R, zc = 6.69, -1.09
    t = .25

    def arc(radius, n=14, z_end=-.02):
        amax = math.acos((z_end - zc) / radius)
        return [(radius * math.sin(amax - 2 * amax * k / n), zc + radius * math.cos(amax - 2 * amax * k / n))
                for k in range(n + 1)]
    y0, y1 = -4.4, 4.6
    core = arc(R) + list(reversed(arc(R - t)))
    a.part('Arch_lining', 'Charred').prism(core, y1 - y0, loc=(0, (y0 + y1) / 2, 0), axis='Y', bevel=0)
    # Corrugated outer skin: ribs follow the arch, so the trapezoid profile runs along Y.
    sheet = a.part('Arch_sheet', 'Corrugated')
    bm = sheet.bm
    sy0, sy1 = y0 + .1, y1 + .03
    prof = _trapezoids(sy1 - sy0, .72, .035)
    ring_pts = arc(R + .01)
    grid = []
    for u, o in prof:
        y = (sy0 + sy1) / 2 + u
        row = []
        for x, z in ring_pts:
            k = (R + .01 + o) / (R + .01)
            row.append(bm.verts.new((x * k, y, zc + (z - zc) * k)))
        grid.append(row)
    for i in range(len(grid) - 1):
        for k in range(len(ring_pts) - 1):
            f = bm.faces.new((grid[i][k], grid[i + 1][k], grid[i + 1][k + 1], grid[i][k + 1]))
            f.normal_update()
            c = f.calc_center_median()
            if f.normal.dot(Vector((c.x, 0, c.z - zc))) < 0:
                f.normal_flip()
    # Team portal frame and concrete footings at the front.
    band = arc(R + .16) + list(reversed(arc(R - t - .12)))
    a.part('Portal_frame', 'Team').prism(band, .45, loc=(0, y0 - .2 + .225 - .01, 0), axis='Y', bevel=.02, seg=1)
    for s in (-1, 1):
        a.part('Footings', 'Concrete').box((1.1, 1.0, .7), loc=(s * 6.55, y0 - .05, .33), bevel=.04, seg=1)
        a.part('Sills', 'Concrete').box((.6, y1 - y0 + .1, .3), loc=(s * 6.55, (y0 + y1) / 2, .13), bevel=.03, seg=1)
    # Back wall with a lining, a door, a vent and a lamp.
    back = arc(R + .02)
    a.part('Back_wall', 'Concrete').prism(back, .3, loc=(0, y1 + .12, 0), axis='Y', bevel=.03, seg=1)
    a.part('Back_lining', 'Charred').prism(arc(R - t - .02), .02, loc=(0, y1 - .04, 0), axis='Y', bevel=0)
    fbox(a.part('Back_door', 'Armor'), '+y', (2.5, y1 + .27, 1.2), (1.0, .06, 2.1), out=0.0, bevel=.015)
    a.part('Back_vent', 'Undercarriage').grille(1.4, .7, loc=(0, y1 + .3, 3.4), rot=(0, 0, math.pi), slats=4)
    caged_lamp(a, '+y', (3.3, y1 + .27, 2.5))
    # Slab, dark interior floor and the striped threshold.
    a.part('Slab', 'Concrete').box((14.0, 10.0, .16), loc=(0, 0, .06), bevel=.04, seg=1)
    a.part('Interior_floor', 'Asphalt').box((12.6, y1 - y0, .02), loc=(0, (y0 + y1) / 2, .15), bevel=0)
    for k in range(12):
        a.part('Threshold', 'SafetyStripe' if k % 2 else 'Charred').box(
            (1.02, .3, .03), loc=(-5.61 + k * 1.02, -4.82, .145), bevel=0)
    for k in range(5):
        a.part('Oil_stains', 'Charred').cyl(.5 + .15 * (k % 3), .01, loc=(-2.5 + k * 1.3, -1.5 + (k % 2) * 2.2, .165),
                                            seg=8, bevel=0)
    # Interior: workbench, tyres, drums, crates, engine hoist, hanging lamps.
    zf = .16
    a.part('Bench_top', 'Wood').box((2.0, .7, .08), loc=(-4.5, 2.8, zf + .92), bevel=.01, seg=1)
    for sx in (-.9, .9):
        for sy in (-.28, .28):
            a.part('Bench_legs', 'Armor').box((.06, .06, .9), loc=(-4.5 + sx, 2.8 + sy, zf + .45), bevel=0)
    a.part('Bench_tools', 'Steel').box((.25, .18, .16), loc=(-4.0, 2.75, zf + 1.04), bevel=0)
    a.part('Bench_tools', 'Hazard').box((.4, .25, .2), loc=(-4.9, 2.9, zf + 1.06), bevel=.02, seg=1)
    for k in range(2):
        a.part('Tyres', 'Rubber').cyl(.5, .3, loc=(-5.0, -.8, zf + .15 + k * .31), seg=12, bevel=.06, bseg=1)
    for x, y in ((4.9, 3.3), (5.4, 2.5), (4.6, 2.6)):
        a.part('Drums', 'BarrelRed').cyl(.29, .88, loc=(x, y, zf + .44), seg=10, bevel=.02, bseg=1)
    crate(a, (4.8, .1, zf), size=(1.1, .6, .5), yaw=.1)
    crate(a, (4.85, .1, zf + .5), size=(1.0, .55, .45), yaw=.25, band=False)
    hoist = a.part('Hoist', 'Steel')
    for s in (-1, 1):
        hoist.limb((2.2 + s * .5, 3.4, zf), (2.2, 3.2, zf + 2.0), .08, .08, bevel=0)
    hoist.limb((2.2, 3.2, zf + 1.95), (2.2, 1.9, zf + 2.2), .1, .12, bevel=0)
    hoist.box((.03, .03, .8), loc=(2.2, 1.95, zf + 1.75), bevel=0)
    a.part('Hoist_hook', 'SafetyStripe').box((.12, .08, .16), loc=(2.2, 1.95, zf + 1.3), bevel=0)
    top_z = zc + R - t - .02
    for y in (-3.85, 0.0):
        a.part('Lamp_cables', 'Steel').cyl(.015, top_z - 4.3, loc=(0, y, (top_z + 4.3) / 2), seg=4, bevel=0)
        a.part('Lamp_shades', 'Armor').lathe([(.4, 0), (.28, .12), (.08, .26), (0, .28)], loc=(0, y, 4.05), seg=10)
        a.part('Hangar_lamps', 'Lamp').sphere(.15, loc=(0, y, 4.02), seg=8, rings=5)
    # Roof ventilators and the entrance floodlight.
    crown = zc + R + .01 + .035
    for y in (-2.4, .6, 3.4):
        a.part('Ventilators', 'Steel').cyl(.24, .55, loc=(0, y, crown + .22), seg=8, bevel=0)
        a.part('Ventilator_caps', 'Armor').cyl(.36, .12, loc=(0, y, crown + .52), r2=.2, seg=8, bevel=0)
    flood_head(a, (0, y0 - .02, zc + R + .16 + .36), yaw=0.0, tilt=.6, size=(.7, .3, .45))


# ----------------------------------------------------------------------------- helipad
def helipad(a):
    """Helipad (10 x 10 m, 9.5 cm): an asphalt pad with a Team border, a white touchdown ring and H,
    tie-down points and twelve Lamp edge lights. Walkable."""
    a.part('Pad', 'Asphalt').box((10.0, 10.0, .07), loc=(0, 0, .015), bevel=.02, seg=1)
    team = a.part('Pad_border', 'Team')
    e, w = 4.72, .3
    for s in (-1, 1):
        team.box((2 * e + w, w, .03), loc=(0, s * e, .052), bevel=0)
        team.box((w, 2 * e - w, .03), loc=(s * e, 0, .052), bevel=0)
    paint = a.part('Markings', 'PlasterWhite')
    paint.shell(_circle(3.8, 24), .03, .32, loc=(0, 0, .037))
    for s in (-1, 1):
        paint.box((.55, 3.2, .035), loc=(s * 1.05, 0, .0545), bevel=0)
    paint.box((1.6, .55, .023), loc=(0, 0, .0485), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Tie_downs', 'Steel').cyl(.1, .02, loc=(sx * 2.2, sy * 2.2, .055), seg=8, bevel=0)
    for k in range(12):
        side, j = divmod(k, 3)
        u = (-4.3, -1.43, 1.43)[j]
        x, y = {0: (u, -4.3), 1: (4.3, u), 2: (-u, 4.3), 3: (-4.3, -u)}[side]
        a.part('Edge_light_bases', 'Armor').cyl(.1, .03, loc=(x, y, .06), seg=6, bevel=0)
        a.part('Edge_lights', 'Lamp').sphere((.065, .065, .025), loc=(x, y, .07), seg=6, rings=4, cut=0.0)


# ----------------------------------------------------------------------------- razor_wire
def razor_wire(a):
    """Concertina razor-wire fence (8 m, 1 m high): one coil on four steel pickets with top and bottom
    line wires and two warning tags. The coil ends in phase at x = +-4 m, so runs join end to end."""
    pk = a.part('Pickets', 'Armor')
    for x in (-3.0, -1.0, 1.0, 3.0):
        pk.box((.05, .07, 1.12), loc=(x, 0, .54), bevel=0)
        pk.box((.09, .09, .05), loc=(x, 0, 1.1), bevel=0)
    wire = a.part('Razor_wire', 'Steel')
    coil(wire, -4.0, 4.0, 0, .48, .45, pitch=.27, pts=9, wire=.016)
    for z in (.1, .92):
        wire.tube([(-4.0, 0, z), (4.0, 0, z)], .01, seg=3, caps=False)
    for x in (-2.0, 2.2):
        a.part('Warning_tags', 'Hazard').box((.22, .015, .15), loc=(x, 0, .83), bevel=0)


# ----------------------------------------------------------------------------- sandbag_wall
def sandbag_wall(a):
    """Sandbag wall (8 x 1.4 m, 1.2 m): five courses laid in a bond, three bags deep at the base and one
    at the top, over a hidden earth core. The ends are cut flush at x = +-4 m."""
    rng = random.Random(5)
    bags = a.part('Sandbags', 'Sandbag')
    size, step = (.8, .42, .27), .235
    rows = ((-.5, .5), (-.5, .5), (-.28, .28), (-.28, .28), (0.0,))
    for k, ys in enumerate(rows):
        z = size[2] / 2 - .012 + k * step
        for y in ys:
            bag_run(bags, rng, (-4.0, y), (4.0, y), z, size, half=(k % 2 == 1) ^ (y > 0))
    a.part('Core', 'Dirt').prism([(-.5, -.02), (.5, -.02), (.3, .8), (-.3, .8)], 7.9, axis='X', bevel=0)


# name: (builder, Asset options)
BUILDERS = {
    'gun_turret': (gun_turret, dict(ao_distance=.8, grime_height=.6)),
    'aa_turret': (aa_turret, dict(ao_distance=.6, grime_height=.5)),
    'rocket_turret': (rocket_turret, dict(ao_distance=.6, grime_height=.5)),
    'mg_bunker': (mg_bunker, dict(ao_distance=.8, grime_height=.5)),
    'artillery_emplacement': (artillery_emplacement, dict(ao_distance=.6, grime_height=.5)),
    'guard_tower': (guard_tower, dict(ao_distance=.9, grime_height=.8)),
    'command_hq': (command_hq, dict(ao_distance=1.6, grime_height=.9)),
    'base_wall': (base_wall, dict(ao_distance=.7, grime_height=.5)),
    'base_gate': (base_gate, dict(ao_distance=.8, grime_height=.5)),
    'floodlight_mast': (floodlight_mast, dict(ao_distance=.5, grime_height=.4)),
    'fuel_depot': (fuel_depot, dict(ao_distance=1.0, grime_height=.6)),
    'ammo_dump': (ammo_dump, dict(ao_distance=.6, grime_height=.4)),
    'vehicle_hangar': (vehicle_hangar, dict(ao_distance=2.0, grime_height=1.0)),
    'helipad': (helipad, dict(ao_distance=.3, grime_height=.2)),
    'razor_wire': (razor_wire, dict(ao_distance=.3, grime_height=.3)),
    'sandbag_wall': (sandbag_wall, dict(ao_distance=.4, grime_height=.3)),
}
