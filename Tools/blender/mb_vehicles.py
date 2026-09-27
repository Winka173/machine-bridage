"""Machine Brigade ground vehicles built with frontier_kit.

Conventions (shared with ModelLibrary.cs): metres, +Z up, Blender -Y is the front, origin on the
ground at the hull centre. Each vehicle has a `Turret` empty at the turret ring; turret parts are
authored relative to it. Parts named Main_cannon* / Muzzle_brake* recoil along the barrel. Parts
using the `Team` / `TeamGlow` materials are recoloured per army at runtime.

Weapon empties: `Muzzle_main` sits at the tip of the main weapon (child of Turret). Secondary
weapons add `Muzzle_coax` (beside the main gun), `Muzzle_mg` (roof machine gun on its own
`Mount_mg` yaw pivot), `Muzzle_gun` (40 mm grenade launcher on its own `Mount_gun` yaw pivot) and
`Muzzle_missile` (launcher opening). The roof machine guns and grenade launchers that give the
scout jeep, MLRS, SAM launcher and rocket technical a second weapon come from mb_weapons.py. A
`Radar` pivot spins about Z.
"""
import math

from mathutils import Euler, Matrix, Vector

import mb_weapons as wpn
from frontier_kit import chamfered

R90 = math.pi / 2
TAU = math.tau
FORWARD = (R90, 0, 0)   # cylinder axis along Y (a cone's narrow end points to the front, -Y)
ACROSS = (0, R90, 0)    # cylinder axis along X


def _hull2d(points):
    """Convex hull (counter-clockwise) of 2D points."""
    pts = sorted(set((round(p[0], 5), round(p[1], 5)) for p in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-9:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-9:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _perimeter(poly, pitch, offset=0.0):
    """Points every `pitch` metres around a closed (y, z) polygon, with the unit tangent there."""
    edges = [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
    out, carry = [], offset
    for (y0, z0), (y1, z1) in edges:
        n = math.hypot(y1 - y0, z1 - z0)
        if n < 1e-6:
            continue
        ty, tz = (y1 - y0) / n, (z1 - z0) / n
        d = carry
        while d < n:
            out.append(((y0 + ty * d, z0 + tz * d), (ty, tz)))
            d += pitch
        carry = d - n
    return out


def _road_wheel(a, x, y, z, r, s, seg=10, face=None):
    """Road wheel on the outer face of a track (side s): dark rubber tyre, painted disc, steel hub.
    Spans the same X as the old single-disc wheel: from the belt face - 2 cm to face + 9 cm."""
    face = x if face is None else face
    a.part('Tyres', 'Undercarriage').cyl(r, .08, loc=(face + s * .02, y, z), rot=ACROSS, seg=seg, bevel=0)
    a.part('Wheels', 'Team').cyl(r * .74, .03, loc=(face + s * .065, y, z), rot=ACROSS, seg=seg, bevel=0)
    a.part('Hubs', 'Steel').cyl(r * .26, .03, loc=(face + s * .075, y, z), rot=ACROSS, seg=6, bevel=0)


def tracks(a, half_width, length, height, wheel_r, wheels, z, belt_width=.46, wheel_seg=14, lean=False,
           sprocket=1, rollers=0, cleat_pitch=.19):
    """Track units after 3d_astra, reworked: a crisp belt whose ends climb from the first and last
    road wheel to the drive sprocket and idler, cleats on the exposed runs, rubber-tyred road wheels,
    a toothed drive sprocket (sprocket=1 rear, -1 front) and an idler, optional return rollers and
    the fenders over the top run. The belt runs from its top at z + height / 2 down to 1 cm below
    the ground, so the vehicle sits on its tracks. lean and wheel_seg are kept for the callers;
    small parts are never bevelled."""
    belt = a.part('Tracks', 'Undercarriage')
    fender = a.part('Fenders', 'Armor')
    drive = a.part('Sprockets', 'Armor')
    top, bottom = z + height / 2, -.01
    rb = min(.26, height * .45)
    first = length / 2 - .5
    rl = min(wheel_r, (top - bottom) / 2 - .02)
    circles = [(e * (length / 2 - rb), top - rb, rb) for e in (-1, 1)] + [(e * first, bottom + rl, rl) for e in (-1, 1)]
    outline = _hull2d([(cy + r * math.cos(k * TAU / 20), cz + r * math.sin(k * TAU / 20))
                       for cy, cz, r in circles for k in range(20)])
    fender_end = length * .46
    seg = min(wheel_seg, 12) if not lean else min(wheel_seg, 10)
    for s in (-1, 1):
        x = s * half_width
        face = x + s * belt_width / 2
        belt.prism(outline, belt_width, loc=(x, 0, 0), axis='X', bevel=.025, seg=1)
        for (py, pz), (ty, tz) in _perimeter(outline, cleat_pitch, .05):
            if abs(py) < first - .02 or pz < bottom + .06 or (pz > top - .02 and abs(py) < fender_end):
                continue
            ny, nz = tz, -ty  # outward normal of a counter-clockwise outline
            belt.box((belt_width + .04, .07, .05), loc=(x, py + ny * .012, pz + nz * .012),
                     rot=(math.atan2(tz, ty), 0, 0), bevel=0)
        fender.box((belt_width + .14, length * .92, .06), loc=(x, -.03, top + .05), bevel=.02, seg=1,
                   taper=(1, .98))
        for i in range(wheels):
            y = -length / 2 + .5 + i * (length - 1.0) / (wheels - 1)
            _road_wheel(a, x, y, z - .06, wheel_r, s, seg=seg, face=face)
        # Drive sprocket (toothed) and idler at the top corners of the belt.
        for end in (-1, 1):
            cy, cz = end * (length / 2 - rb), top - rb
            # Both sit a little inboard of the road wheels, whose outer faces are at face + 6/8/9 cm.
            if sprocket and end == sprocket:
                drive.cyl(rb * .86, .08, loc=(face - s * .01, cy, cz), rot=ACROSS, seg=12, bevel=0)
                for k in range(9):
                    ang = k * TAU / 9 + .2
                    drive.box((.05, .07, .08), loc=(face + s * .02, cy + math.cos(ang) * (rb * .86 + .02),
                                                    cz + math.sin(ang) * (rb * .86 + .02)),
                              rot=(ang + R90, 0, 0), bevel=0)
            else:
                a.part('Tyres', 'Undercarriage').cyl(rb * .9, .08, loc=(face - s * .01, cy, cz), rot=ACROSS,
                                                     seg=seg, bevel=0)
                drive.cyl(rb * .62, .03, loc=(face + s * .03, cy, cz), rot=ACROSS, seg=seg, bevel=0)
            a.part('Hubs', 'Steel').cyl(rb * .3, .035, loc=(face + s * .0525, cy, cz), rot=ACROSS, seg=8,
                                        bevel=0)
        for i in range(rollers):  # return rollers carry the top run between the wheels
            y = -length / 2 + 1.0 + (i + .5) * (length - 2.0) / rollers
            a.part('Tyres', 'Undercarriage').cyl(.1, .07, loc=(face + s * .015, y, top - .13), rot=ACROSS, seg=8,
                                                 bevel=0)
            a.part('Hubs', 'Steel').cyl(.045, .02, loc=(face + s * .055, y, top - .13), rot=ACROSS, seg=6, bevel=0)


def _barrel(a, turret, start_y, length, radius, height, pitch=0.0, brake=(.26, .28, .24), sleeve=None, x=0.0,
            suffix='', seg=14, style='box', bands=()):
    """Main gun from the mantlet forwards, optionally pitched up; muzzle device at the tip.
    Returns the centre of the muzzle device's front face (where `Muzzle_main` goes); every style
    ends at the same point, brake[1] * .9 beyond the barrel. style: 'box' (the old block),
    'baffle' (double-baffle brake), 'collar' (smooth-bore muzzle reference collar), 'flash' (slotted
    autocannon flash hider). bands: thermal-sleeve clamps at these fractions of the length."""
    # Rotating local Z by (90 deg - pitch) about X points it along (0, -cos, sin): forward and up.
    rot = (R90 - pitch, 0, 0)
    direction = (0.0, -math.cos(pitch), math.sin(pitch))

    def along(d):
        return (x, start_y + direction[1] * d, height + direction[2] * d)

    cannon = a.part(f'Main_cannon{suffix}', 'Steel', turret)
    cannon.cyl(radius, length, loc=along(length / 2), rot=rot, seg=seg, bevel=.015, bseg=1)
    if sleeve:
        at, sleeve_len, sleeve_r = sleeve
        cannon.cyl(sleeve_r, sleeve_len, loc=along(length * at), rot=rot, seg=seg, bevel=.02)
    for at in bands:  # same part: a second Main_cannon object would clash with the rig's names
        cannon.cyl(radius * 1.16, .05, loc=along(length * at), rot=rot, seg=seg, bevel=0)
    b = brake[1]
    device = a.part(f'Muzzle_brake{suffix}', 'Undercarriage', turret)
    if style == 'baffle':
        core = radius + .015
        device.cyl(core, b * .9 + .05, loc=along(length + b * .45 - .025), rot=rot, seg=seg, bevel=0)
        size = (max(brake[0], 2 * core + .03), b * .3, max(brake[2], 2 * core + .03))
        for at in (.2, .7):
            device.box(size, loc=along(length + b * at), rot=(-pitch, 0, 0), bevel=.015, seg=1)
    elif style == 'collar':
        device.cyl(radius * 1.28, b * .5, loc=along(length + b * .65), rot=rot, seg=seg, bevel=.012, bseg=1)
        device.cyl(radius * 1.1, b * .45, loc=along(length + b * .2 - .02), rot=rot, seg=seg, bevel=0)
    elif style == 'flash':
        device.cyl(radius * 1.35, b * .9 + .04, loc=along(length + b * .45 - .02), rot=rot, seg=seg, bevel=.008,
                   bseg=1)
        for at in (.25, .5, .75):
            device.cyl(radius * 1.7, .03, loc=along(length + b * .9 * at), rot=rot, seg=seg, bevel=0)
    else:
        device.box(brake, loc=along(length + b * .4), rot=(-pitch, 0, 0), bevel=.03)
    return along(length + b * .9)


def _antenna(a, turret, x, y, z, height=1.0):
    a.part('Antenna', 'Steel', turret).cyl(.012, height, loc=(x, y, z + height / 2), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow', turret).sphere(.045, loc=(x, y, z + height + .02), seg=8, rings=5)


def _coax(a, turret, x, y, z, length=.4, housing=.26):
    """Coaxial machine gun: a housing whose back half is buried in the turret face at y, and a
    thin barrel forwards. Adds `Muzzle_coax` at the barrel tip."""
    coax = a.part('Coax', 'Steel', turret)
    front = y - housing / 2
    coax.box((.1, housing, .1), loc=(x, y, z), bevel=.02, seg=1)
    coax.cyl(.022, length - .04, loc=(x, front - length / 2 + .04, z), rot=FORWARD, seg=8, bevel=0)
    coax.cyl(.034, .08, loc=(x, front - length + .06, z), rot=FORWARD, seg=8, bevel=0)  # flash hider
    a.pivot('Muzzle_coax', (x, front - length + .02, z), turret)


def _roof_mg(a, parent, loc, length=.8, shield=True):
    """Pintle heavy machine gun on its own `Mount_mg` yaw pivot: receiver, barrel, shield, ammo can."""
    m = a.pivot('Mount_mg', loc, parent)
    mg = a.part('MG', 'Steel', m)
    mg.cyl(.05, .15, loc=(0, 0, .065), seg=8, bevel=.01, bseg=1)             # pintle
    mg.box((.14, .36, .14), loc=(0, .02, .2), bevel=.02, seg=1)               # receiver
    mg.box((.05, .16, .08), loc=(0, .24, .17), rot=(.3, 0, 0), bevel=.01, seg=1)  # grips
    front = .02 - .18
    mg.cyl(.028, length - .05, loc=(0, front - length / 2 + .045, .21), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.042, .12, loc=(0, front - length + .08, .21), rot=FORWARD, seg=8, bevel=0)      # flash hider
    a.part('MG_ammo', 'Armor', m).box((.12, .2, .14), loc=(.14, .04, .19), bevel=.02, seg=1)
    if shield:
        a.part('MG_shield', 'Armor', m).box((.48, .04, .3), loc=(0, -.24, .25), rot=(-.12, 0, 0), bevel=.012,
                                             seg=1, taper=(.8, 1))
    a.pivot('Muzzle_mg', (0, front - length + .02, .21), m)


def _smoke(a, part, x, y, z, s, count=3, gap=.07, r=.04, depth=.14):
    """Smoke-grenade dischargers angled up and outwards on side s."""
    for i in range(count):
        part.cyl(r, depth, loc=(s * (x + i * gap), y, z), rot=(.6, 0, s * .4), seg=8, bevel=0)


def _wheel(a, x, y, r, width, seg=16):
    """Big off-road tyre touching the ground (z = r) with a steel hub and centre cap."""
    a.part('Tyres', 'Rubber').cyl(r, width, loc=(x, y, r), rot=ACROSS, seg=seg, bevel=r * .16, bseg=1)
    hubs = a.part('Hubs', 'Steel')
    hubs.cyl(r * .52, width + .04, loc=(x, y, r), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    hubs.cyl(r * .2, width + .1, loc=(x, y, r), rot=ACROSS, seg=6, bevel=0)


def _frame(loc, rot):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


def _tube_mouth(a, parent, m, r, protrude=.07, seg=10, name='Tubes'):
    """Launcher tube opening facing local +Z of matrix m: a steel lip around a dark bore whose
    recess darkens in the baked AO. The lip starts 3 cm inside the launcher face."""
    loc, rot = m.to_translation(), m.to_euler('XYZ')
    a.part(name, 'Steel', parent).lathe([(r, -.03), (r, protrude), (r * .74, protrude), (r * .74, protrude * .3)],
                                        loc=loc, rot=rot, seg=seg)
    a.part(f'{name}_bore', 'Undercarriage', parent).cyl(r * .7, .02, loc=m @ Vector((0, 0, protrude * .3 + .012)),
                                                        rot=rot, seg=seg, bevel=0)


def _dish(part, loc, rx, rz, depth=.15, seg=12, tilt=0.0):
    """Elliptical search-radar reflector: the back centre sits at loc, the concave side faces -Y
    and is tilted up by `tilt` radians."""
    turn = Matrix.Rotation(-tilt, 3, 'X')
    base = Vector(loc)

    def ring(k, dy):
        return [tuple(base + turn @ Vector((rx * k * math.cos(u), dy, rz * k * math.sin(u))))
                for u in (i * math.tau / seg for i in range(seg))]
    part.loft([[tuple(base)], ring(.55, -depth * .35), ring(1.0, -depth), ring(.96, -depth - .05),
               ring(.5, -depth * .35 - .05), [tuple(base + turn @ Vector((0, -.05, 0)))]])


# ----------------------------------------------------------------------------- detail kit
# Small hard-surface details shared by the ground vehicles. Repeated small parts are never bevelled:
# they are read at RTS range, where the silhouette and the baked light/dark rhythm matter more than
# rounded edges. Every detail sinks 1-2 cm into the surface it sits on, so no face lies flush on
# another (flush faces z-fight).
def _skirt(a, s, x, y0, y1, z0, z1, panels, mat='Team', thick=.08, gap=.035, bolts=True, parent=None):
    """Segmented side skirt on side s at |x|: `panels` plates from y0 to y1 (z0 to z1) with a raised
    lip on top; bolts pick out each plate's lower corners."""
    part = a.part('Skirts', mat, parent)
    lip = a.part('Skirt_edge', 'Armor', parent)
    steel = a.part('Skirt_bolts', 'Steel', parent)
    step = (y1 - y0 + gap) / panels
    for i in range(panels):
        yc = y0 + step * (i + .5) - gap / 2
        w = step - gap
        part.box((thick, w, z1 - z0), loc=(s * x, yc, (z0 + z1) / 2), bevel=.02, seg=1)
        lip.box((thick + .03, w + .03, .05), loc=(s * x, yc, z1 - .015), bevel=0)
        if bolts:
            for dy in (-w / 2 + .1, w / 2 - .1):
                steel.box((.03, .05, .05), loc=(s * (x + thick / 2 + .005), yc + dy, z0 + .1), bevel=0)


def _stowage_bin(a, loc, size, parent=None, mat='Armor', lid='Armor', latch_side=-1, yaw=0.0):
    """Stowage bin standing on loc (x, y, z of its base): body, overhanging lid and two latches on the
    long side facing latch_side (-1: -X, 1: +X, 0: front -Y)."""
    x, y, z = loc
    w, d, h = size
    m = _frame((x, y, z), (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Stowage', mat, parent).box((w, d, h), loc=m @ Vector((0, 0, h / 2 - .01)), rot=rot, bevel=.02, seg=1)
    a.part('Stowage_lid', lid, parent).box((w + .03, d + .03, .04), loc=m @ Vector((0, 0, h - .02)), rot=rot,
                                           bevel=.012, seg=1)
    steel = a.part('Latches', 'Steel', parent)
    for k in (-.25, .25):
        if latch_side:
            steel.box((.03, .05, .07), loc=m @ Vector((latch_side * (w / 2 + .006), k * d, h - .09)), rot=rot,
                      bevel=0)
        else:
            steel.box((.05, .03, .07), loc=m @ Vector((k * w, -d / 2 - .006, h - .09)), rot=rot, bevel=0)


def _jerrycans(a, loc, count, axis='y', parent=None, mat='Crate', bracket=True):
    """A rack of jerrycans standing on loc, `count` of them in a row along axis (their thin side
    faces that way), with carry handles and a steel strap."""
    x, y, z = loc
    body = a.part('Jerrycans', mat, parent)
    t, wide, h = .15, .33, .44
    for i in range(count):
        off = (i - (count - 1) / 2) * (t + .025)
        if axis == 'y':
            cx, cy, size, handle = x, y + off, (wide, t, h), (.2, .05, .04)
        else:
            cx, cy, size, handle = x + off, y, (t, wide, h), (.05, .2, .04)
        body.box(size, loc=(cx, cy, z + h / 2 - .01), bevel=.02, seg=1)
        body.box(handle, loc=(cx, cy, z + h + .005), bevel=0)
    if bracket:
        run = count * (t + .025) + .02
        size = (wide + .04, run, .04) if axis == 'y' else (run, wide + .04, .04)
        a.part('Jerrycan_rack', 'Steel', parent).box(size, loc=(x, y, z + h * .55), bevel=0)


def _cable(a, points, parent=None, r=.022):
    """Tow cable along a polyline with a thimble eye at both ends."""
    part = a.part('Tow_cable', 'Steel', parent)
    part.tube(points, r, seg=6)
    for p in (points[0], points[-1]):
        part.box((.08, .08, .075), loc=p, bevel=0)


def _shovel(a, loc, yaw=0.0, parent=None, length=1.0):
    """Pioneer shovel lying flat: steel blade and a dark handle along the local Y axis."""
    m = _frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Tools', 'Steel', parent).box((.2, .26, .025), loc=m @ Vector((0, -length / 2 + .13, 0)), rot=rot,
                                         bevel=0)
    a.part('Tool_handles', 'Armor', parent).box((.04, length - .26, .035), loc=m @ Vector((0, .13, 0)), rot=rot,
                                                bevel=0)


def _pick(a, loc, yaw=0.0, parent=None, length=.9):
    """Pick-axe lying flat: handle along local Y with a steel head across it."""
    m = _frame(loc, (0, 0, yaw))
    rot = (0, 0, yaw)
    a.part('Tool_handles', 'Armor', parent).box((.045, length, .04), loc=m @ Vector((0, 0, 0)), rot=rot, bevel=0)
    a.part('Tools', 'Steel', parent).box((.42, .06, .06), loc=m @ Vector((0, -length / 2 + .06, .01)), rot=rot,
                                         bevel=0)


def _headlight(a, x, y, z, parent=None, guard=True, facing=-1):
    """Armoured headlight on a surface at y facing `facing` (-1: front, 1: rear): housing, Lamp lens and a
    bent brush guard."""
    f = facing
    a.part('Light_housing', 'Armor', parent).box((.24, .12, .17), loc=(x, y - f * .04, z), bevel=.02, seg=1)
    a.part('Lamps', 'Lamp', parent).box((.17, .03, .11), loc=(x, y + f * .025, z), bevel=0)
    if guard:
        g = y + f * .1
        a.part('Light_guards', 'Steel', parent).tube(
            [(x - .15, y - f * .02, z - .09), (x - .15, g, z - .06), (x - .15, g, z + .1), (x + .15, g, z + .1),
             (x + .15, g, z - .06), (x + .15, y - f * .02, z - .09)], .014, seg=4)


def _taillight(a, x, y, z, parent=None, facing=1, lamp='Alloy'):
    """Rear light cluster on a surface at y facing `facing`: housing and two lenses (amber marker
    and a Lamp reversing light)."""
    f = facing
    a.part('Light_housing', 'Armor', parent).box((.22, .1, .12), loc=(x, y - f * .03, z), bevel=.015, seg=1)
    a.part('Tail_lights', lamp, parent).box((.08, .03, .07), loc=(x - .05, y + f * .025, z), bevel=0)
    a.part('Lamps', 'Lamp', parent).box((.07, .03, .07), loc=(x + .05, y + f * .025, z), bevel=0)


def _hatch(a, x, y, z, r, parent=None, mat='Armor', handle=True, hinge=1, seg=12):
    """Round hatch lid on a roof at height z with a hinge block (towards +Y if hinge=1) and a grab handle."""
    a.part('Hatches', mat, parent).cyl(r, .06, loc=(x, y, z + .02), seg=seg, bevel=.015, bseg=1)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    steel.box((r * .9, .08, .06), loc=(x, y + hinge * (r + .01), z + .03), bevel=0)
    if handle:
        hy = y - hinge * r * .3
        steel.tube([(x - r * .4, hy, z + .04), (x - r * .4, hy, z + .1), (x + r * .4, hy, z + .1),
                    (x + r * .4, hy, z + .04)], .014, seg=4)


def _periscopes(a, points, parent=None, size=(.13, .07, .08)):
    """Vision blocks: an armoured hood with a glass face towards local -Y, each at (x, y, z, yaw)."""
    for x, y, z, yaw in points:
        m = _frame((x, y, z), (0, 0, yaw))
        a.part('Periscope_hoods', 'Armor', parent).box((size[0] + .04, size[1] + .03, size[2]),
                                                       loc=m @ Vector((0, .015, size[2] / 2 - .02)),
                                                       rot=(0, 0, yaw), bevel=0)
        a.part('Periscope', 'Glass', parent).box((size[0], .02, size[2] * .5),
                                                 loc=m @ Vector((0, -size[1] / 2 - .003, size[2] * .45 - .02)),
                                                 rot=(0, 0, yaw), bevel=0)


def _rail(a, points, parent=None, r=.016):
    """Grab rail / handrail along a polyline."""
    a.part('Grab_rails', 'Steel', parent).tube(points, r, seg=4)


def _exhaust(a, x, y, z, w, d, parent=None, facing=1, slats=3):
    """Exhaust outlet on a rear plate at y facing `facing`: armoured cowl around dark louvres."""
    f = facing
    a.part('Exhaust', 'Armor', parent).box((w + .08, .08, d + .08), loc=(x, y - f * .02, z), bevel=.015, seg=1)
    a.part('Exhaust_louvres', 'Undercarriage', parent).grille(w, d, loc=(x, y + f * .03, z),
                                                              rot=(0, 0, 0 if f < 0 else math.pi), slats=slats,
                                                              depth=.05, thickness=.035)


def _grille_frame(a, x, y, z, w, d, parent=None, mat='Armor', t=.06):
    """Raised frame around a deck grille at height z (the grille itself is built by the caller)."""
    fr = a.part('Grille_frames', mat, parent)
    fr.box((w + 2 * t, t, .05), loc=(x, y - d / 2 - t / 2, z + .005), bevel=0)
    fr.box((w + 2 * t, t, .05), loc=(x, y + d / 2 + t / 2, z + .005), bevel=0)
    fr.box((t, d, .05), loc=(x - w / 2 - t / 2, y, z + .005), bevel=0)
    fr.box((t, d, .05), loc=(x + w / 2 + t / 2, y, z + .005), bevel=0)


def _era(a, m, cols, rows, size, gap=.03, parent=None, mat='Armor', bevel=.012):
    """Reactive armour: a grid of blocks laid on the plane of matrix m (local XY, blocks rising along
    local +Z), centred on its origin."""
    w, d, t = size
    rot = m.to_euler('XYZ')
    for i in range(cols):
        for j in range(rows):
            p = Vector(((i - (cols - 1) / 2) * (w + gap), (j - (rows - 1) / 2) * (d + gap), t / 2 - .01))
            a.part('ERA', mat, parent).box((w, d, t), loc=m @ p, rot=rot, bevel=bevel, seg=1)


def _face_frame(b0, b1, h, taper=1.0, z0=0.0, u=.5, v=.5, out=0.0):
    """Frame on a side face of a Z prism (outline point b0 -> b1 at the bottom, z0 to z0 + h, top ring
    scaled by taper): origin u along the edge and v up the face, pushed `out` along the normal; X runs
    along the edge, Y up the face and Z out of it (outwards when b0 -> b1 runs counter-clockwise seen
    from above)."""
    p0, p1 = Vector((b0[0], b0[1], z0)), Vector((b1[0], b1[1], z0))
    q0, q1 = Vector((b0[0] * taper, b0[1] * taper, z0 + h)), Vector((b1[0] * taper, b1[1] * taper, z0 + h))
    bot, top = p0.lerp(p1, u), q0.lerp(q1, u)
    ax = (p1 - p0).normalized()
    ay = (top - bot).normalized()
    az = ax.cross(ay).normalized()
    ay = az.cross(ax)
    # Climb the face square to the edge, so frames at one u but different v share their along-edge
    # position (the top ring is scaled, so the point at the same u drifts along the edge).
    o = bot + ay * (v * (top - bot).length) + az * out
    return Matrix(((ax.x, ay.x, az.x, o.x), (ax.y, ay.y, az.y, o.y), (ax.z, ay.z, az.z, o.z), (0, 0, 0, 1)))


def _face_box(a, name, mat, m, size, parent=None, bevel=.02, seg=1, lift=0.0, sink=.01):
    """Box standing on the face frame m (see _face_frame): size is (along the edge, up the face, out of
    it); its back sinks `sink` into the face (a negative sink stands it off the face). lift moves it up
    the face."""
    w, h, d = size
    a.part(name, mat, parent).box((w, h, d), loc=m @ Vector((0, lift, d / 2 - sink)), rot=m.to_euler('XYZ'),
                                  bevel=bevel, seg=seg)


def _slats(a, m, width, height, bars, parent=None, bar=.04):
    """Slat (bar) armour cage in the plane of matrix m: local X across, local Z up. Horizontal bars
    between two posts."""
    rot = m.to_euler('XYZ')
    part = a.part('Slat_armour', 'Armor', parent)
    for i in range(bars):
        zb = -height / 2 + (i + .5) * height / bars
        part.box((width, bar, bar * 1.6), loc=m @ Vector((0, 0, zb)), rot=rot, bevel=0)
    for sx in (-1, 1):
        part.box((bar * 1.2, bar * 1.8, height + .04), loc=m @ Vector((sx * width / 2, 0, 0)), rot=rot, bevel=0)


def _roll(a, loc, length, r=.13, axis='x', parent=None, mat='Canvas', straps=True):
    """Rolled tarpaulin / bedroll lying along axis with two dark straps."""
    rot = ACROSS if axis == 'x' else FORWARD
    a.part('Tarp', mat, parent).cyl(r, length, loc=loc, rot=rot, seg=10, bevel=.04, bseg=1)
    if straps:
        for k in (-.3, .3):
            off = Vector((k * length, 0, 0)) if axis == 'x' else Vector((0, k * length, 0))
            a.part('Straps', 'Undercarriage', parent).cyl(r + .012, .05, loc=Vector(loc) + off, rot=rot, seg=10,
                                                          bevel=0)


def _track_links(a, m, count, width=.5, parent=None):
    """Spare track links hung on a plate: `count` shoes side by side along local Y of matrix m,
    each with a raised grouser, lying on local +Z."""
    rot = m.to_euler('XYZ')
    part = a.part('Spare_links', 'Undercarriage', parent)
    for i in range(count):
        p = Vector((0, (i - (count - 1) / 2) * .19, .015))
        part.box((width, .16, .05), loc=m @ p, rot=rot, bevel=0)
        part.box((width * .8, .04, .04), loc=m @ (p + Vector((0, 0, .035))), rot=rot, bevel=0)


def _basket(a, x0, x1, y0, y1, z0, h, parent=None, contents=True, box=True):
    """Open stowage basket (turret bustle rack): tube rim on posts, with a bedroll and an ammo box."""
    steel = a.part('Basket', 'Steel', parent)
    steel.tube([(x0, y0, z0 + h), (x0, y1, z0 + h), (x1, y1, z0 + h), (x1, y0, z0 + h)], .02, seg=4)
    for x, y in ((x0, y1), (x1, y1)):
        steel.box((.035, .035, h), loc=(x, y, z0 + h / 2), bevel=0)
    a.part('Basket_floor', 'Armor', parent).box((x1 - x0, y1 - y0, .04),
                                                loc=((x0 + x1) / 2, (y0 + y1) / 2, z0 + .02), bevel=0)
    if contents:
        _roll(a, ((x0 + x1) / 2 - (x1 - x0) * .18, (y0 + y1) / 2 + .02, z0 + .04 + .12), (x1 - x0) * .55, r=.12,
              parent=parent)
    if contents and box:
        a.part('Ammo_boxes', 'Crate', parent).box((.3, (y1 - y0) * .7, .22),
                                                  loc=(x1 - .22, (y0 + y1) / 2, z0 + .04 + .1), bevel=.02, seg=1)


# ----------------------------------------------------------------------------- tanks
def light_tank(a):
    """Light tank: rear-drive running gear under four-panel skirts, fender stowage, tow cable and a
    small turret with a cupola, loader's hatch, bustle basket and a baffle-braked 90 mm gun."""
    tracks(a, 1.02, 4.4, .72, .25, 5, .42, belt_width=.5, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    front, brow = (-2.3, .74), (-1.55, 1.12)
    hull.prism([(-2.3, .5), front, brow, (1.95, 1.12), (2.25, .92), (2.25, .5)], 1.62, bevel=.06)
    for s in (-1, 1):
        _skirt(a, s, 1.3, -2.05, 1.95, .6, 1.0, 4, thick=.1)
        _headlight(a, s * .55, -2.3, .63)
        steel.box((.14, .16, .1), loc=(s * .22, -2.36, .56), bevel=.02, seg=1)             # tow hooks
        steel.cyl(.08, .3, loc=(s * .3, 2.32, .8), rot=FORWARD, seg=10, bevel=.015, bseg=1)  # exhausts
        _taillight(a, s * .64, 2.25, .8)
        gy, gz, grot = _glacis(front, brow, .5, 0)
        _track_links(a, _frame((s * .5, gy, gz), (grot, 0, 0)), 3, width=.42)
    # Fender stowage: bin and tools on the left, jerrycans and the tow cable on the right.
    _stowage_bin(a, (-1.03, 1.3, .85), (.36, .9, .26), latch_side=0)
    _shovel(a, (-1.1, -.95, .875), length=1.0)
    _pick(a, (-1.04, .1, .875), length=.85)
    _jerrycans(a, (1.03, 1.4, .85), 3)
    _cable(a, [(1.0, -1.85, .89), (1.0, -.4, .89), (.98, .7, .89), (.92, 1.02, .89)])
    # Driver's hatch with three vision blocks at the top of the glacis.
    _hatch(a, 0, -1.2, 1.11, .24)
    _periscopes(a, [(dx, -1.53, 1.1, 0) for dx in (-.17, 0, .17)])
    # Engine deck: framed grille and a rear stowage box.
    deck.grille(1.0, .6, loc=(0, 1.35, 1.13), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
    _grille_frame(a, 0, 1.35, 1.11, 1.0, .6)
    _stowage_bin(a, (0, 1.82, 1.11), (1.1, .2, .17), latch_side=0)
    steel.cyl(.72, .14, loc=(0, -.1, 1.17), seg=24, bevel=.03)

    t = a.pivot('Turret', (0, -.1, 1.24))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.62, .7), (.62, .7), (.74, .15), (.62, -.5), (.28, -.8), (-.28, -.8), (-.62, -.5), (-.74, .15)]
    turret.prism(outline, .5, loc=(0, 0, .25), axis='Z', bevel=.05, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.1, .45, .34), loc=(0, .85, .24), bevel=.04, taper=(.95, .9))
    tarm.box((.42, .24, .34), loc=(0, -.84, .25), bevel=.04)
    tsteel = a.part('Turret_steel', 'Steel', t)
    # Commander's cupola with vision blocks all round, loader's hatch, gunner's sight.
    tarm.cyl(.24, .1, loc=(.28, .15, .53), seg=14, bevel=.02, bseg=1)
    _hatch(a, .28, .15, .57, .19, parent=t, seg=12)
    _periscopes(a, [(.28 + math.cos(ang) * .27, .15 + math.sin(ang) * .27, .5, ang + R90)
                    for ang in (-R90, -R90 + .8, -R90 - .8, R90, math.pi)], parent=t, size=(.09, .06, .07))
    _hatch(a, -.3, .22, .49, .19, parent=t, seg=12)
    tarm.box((.2, .2, .14), loc=(-.3, -.36, .54), bevel=.02, seg=1)
    a.part('Periscope', 'Glass', t).box((.15, .02, .08), loc=(-.3, -.465, .55), bevel=0)
    for s in (-1, 1):
        _smoke(a, tsteel, .52, -.42, .42, s, count=2)
        _rail(a, [(s * .53, -.35, .49), (s * .53, -.35, .55), (s * .57, .3, .55), (s * .57, .3, .49)], parent=t)
    _basket(a, -.5, .5, 1.08, 1.38, .1, .26, parent=t)
    _antenna(a, t, -.45, .62, .5, .9)
    tsteel.box((.08, .08, .06), loc=(-.45, .62, .52), bevel=0)                            # antenna base
    tip = _barrel(a, t, start_y=-.95, length=1.9, radius=.085, height=.25, brake=(.22, .26, .2),
                  sleeve=(.09, .32, .12), style='baffle', bands=(.45, .7))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .29, -.8, .31, length=.36, housing=.32)


def main_battle_tank(a):
    """Main battle tank: rear-drive running gear behind five-panel skirts, reactive armour on the
    glacis and turret cheeks, fender and bustle stowage, and a smooth-bore 120 mm gun."""
    tracks(a, 1.28, 5.8, .9, .3, 7, .5, belt_width=.62, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    front, brow = (-3.0, .86), (-2.1, 1.38)
    hull.prism([(-3.0, .58), front, brow, (2.5, 1.38), (2.95, 1.1), (2.95, .58)], 2.0, bevel=.07)
    for s in (-1, 1):
        _skirt(a, s, 1.63, -2.75, 2.3, .72, 1.28, 5, thick=.1, bolts=False)
        _headlight(a, s * .72, -3.0, .72)
        steel.box((.16, .18, .12), loc=(s * .3, -3.06, .66), bevel=.02, seg=1)             # tow hooks
        _exhaust(a, s * .4, 2.95, .84, .4, .26)
        _taillight(a, s * .82, 2.95, .98)
    for x in (-1.1, -.55, 0, .55, 1.1):  # add-on armour blocks on the glacis
        armor.box((.5, .42, .12), loc=(x, -2.52, 1.14), rot=(-.52, 0, 0), bevel=.02, seg=1)
    # Driver's hatch and vision blocks behind the glacis.
    _hatch(a, 0, -1.72, 1.37, .26)
    _periscopes(a, [(dx, -2.1, 1.36, 0) for dx in (-.18, 0, .18)])
    # Engine deck: framed grille, rear bins, fender stowage and a tow cable.
    deck.grille(1.3, .8, loc=(0, 1.72, 1.39), rot=(-R90, 0, 0), slats=7, depth=.1, thickness=.05)
    _grille_frame(a, 0, 1.72, 1.37, 1.3, .8)
    for s in (-1, 1):
        _stowage_bin(a, (s * .62, 2.37, 1.37), (.62, .22, .19), latch_side=0)
    _stowage_bin(a, (-1.29, 1.2, 1.02), (.46, 1.1, .26), latch_side=0)
    _shovel(a, (-1.36, -1.3, 1.045), length=1.1)
    _jerrycans(a, (1.29, 1.6, 1.02), 2)
    _cable(a, [(1.25, -2.4, 1.06), (1.25, -.6, 1.06), (1.2, .8, 1.06), (1.1, 1.05, 1.06)])
    steel.cyl(.98, .16, loc=(0, .15, 1.44), seg=24, bevel=.03)

    t = a.pivot('Turret', (0, .15, 1.52))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.95, 1.05), (.95, 1.05), (1.12, .25), (.95, -.72), (.42, -1.18), (-.42, -1.18), (-.95, -.72),
               (-1.12, .25)]
    turret.prism(outline, .66, loc=(0, 0, .33), axis='Z', bevel=.06, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.6, .7, .5), loc=(0, 1.35, .32), bevel=.05, taper=(.95, .9))
    tarm.box((.62, .34, .5), loc=(0, -1.22, .33), bevel=.05)
    tsteel = a.part('Turret_steel', 'Steel', t)
    # Reactive armour on both cheeks, bins on the bustle sides, a basket behind it.
    for b0, b1 in (((.42, -1.18), (.95, -.72)), ((-.95, -.72), (-.42, -1.18))):
        u = .55 if b0[0] > 0 else .45
        _era(a, _face_frame(b0, b1, .66, .9, u=u, v=.45), 2, 2, (.24, .22, .09), parent=t, bevel=0)
    for s in (-1, 1):
        _stowage_bin(a, (s * .88, 1.35, .1), (.18, .62, .38), parent=t, latch_side=s)
        _smoke(a, tsteel, .78, -.7, .56, s, count=3, gap=.09, r=.05, depth=.16)
    _basket(a, -.7, .7, 1.72, 2.08, .14, .3, parent=t)
    tsteel.cyl(.3, .22, loc=(.42, .25, .77), seg=16, bevel=.04, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.26, .08, loc=(.42, .25, .92), seg=16, bevel=.02, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(4):
        ang = k * math.tau / 4 + .4
        glass.box((.1, .05, .07), loc=(.42 + math.cos(ang) * .29, .25 + math.sin(ang) * .29, .8),
                  rot=(0, 0, ang + R90), bevel=0)
    _hatch(a, -.42, .35, .65, .25, parent=t)                                              # loader's hatch
    _periscopes(a, [(-.42, -.02, .65, 0)], parent=t)
    tarm.box((.34, .3, .26), loc=(-.55, -.5, .76), bevel=.04)                            # sight box
    a.part('Sight', 'Glass', t).box((.24, .04, .14), loc=(-.55, -.66, .78), bevel=.01, seg=1)
    tsteel.cyl(.02, .3, loc=(.15, .85, .8), seg=5, bevel=0)                             # wind sensor
    tsteel.box((.08, .08, .1), loc=(.15, .85, .98), bevel=0)
    _antenna(a, t, -.7, .95, .66, 1.2)
    tsteel.box((.09, .09, .06), loc=(-.7, .95, .67), bevel=0)
    tip = _barrel(a, t, start_y=-1.38, length=3.0, radius=.11, height=.33, brake=(.26, .24, .26),
                  sleeve=(.45, .5, .165), style='collar', bands=(.25, .8))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .45, -1.17, .44, length=.46, housing=.3)
    _roof_mg(a, t, (.42, .25, .95), length=.85)


def artillery(a):
    """Tracked 155 mm self-propelled howitzer: a big boxy turret with bolted side doors, bins, hatches
    and roof stowage, a folded travel lock on the glacis, four-panel skirts and recoil spades."""
    tracks(a, 1.2, 5.4, .8, .28, 6, .45, belt_width=.56, wheel_seg=12, lean=True, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    front, brow = (-2.8, .82), (-2.1, 1.14)
    hull.prism([(-2.8, .52), front, brow, (2.75, 1.14), (2.75, .52)], 1.9, bevel=.06)
    armor.box((1.5, 1.0, .42), loc=(0, -1.75, 1.34), bevel=.05, taper=(.9, .8))  # driver cab
    a.part('Visor', 'Glass').box((1.1, .04, .14), loc=(0, -2.2, 1.38), rot=(-.4, 0, 0), bevel=.01, seg=1)
    _hatch(a, -.3, -1.68, 1.54, .22)
    for s in (-1, 1):
        _skirt(a, s, 1.525, -2.12, 2.5, .62, 1.06, 4, thick=.1)
        _headlight(a, s * .62, -2.8, .66)
        steel.box((.14, .16, .1), loc=(s * .25, -2.86, .6), bevel=.02, seg=1)             # tow hooks
        armor.box((.5, .12, .7), loc=(s * .7, 2.95, .55), rot=(.5, 0, 0), bevel=.03)  # recoil spades
        _taillight(a, s * .8, 2.75, 1.0)
    # Folded travel lock on the glacis, fender stowage in front of the turret.
    lock = [_glacis(front, brow, t, .04) for t in (.12, .88)]
    _rail(a, [(-.35, lock[0][0], lock[0][1]), (-.35, lock[1][0], lock[1][1]), (.35, lock[1][0], lock[1][1]),
              (.35, lock[0][0], lock[0][1])], r=.035)
    steel.box((.3, .14, .12), loc=(0, lock[1][0], lock[1][1] + .02), rot=(lock[1][2], 0, 0), bevel=0)
    _stowage_bin(a, (-1.2, -1.1, .92), (.42, .9, .22), latch_side=0)
    _shovel(a, (-1.25, -2.0, .945), length=.85)
    _jerrycans(a, (1.2, -1.45, .92), 3)
    _cable(a, [(1.42, -2.4, .96), (1.42, -.5, .96)])
    deck.grille(.9, .5, loc=(0, -.85, 1.15), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
    _grille_frame(a, 0, -.85, 1.13, .9, .5, t=.05)

    t = a.pivot('Turret', (0, .8, 1.14))
    turret = a.part('Turret_body', 'Team', t)
    turret.box((2.2, 2.7, 1.25), loc=(0, .15, .64), bevel=.07, taper=(.94, .96))
    tarm = a.part('Turret_armor', 'Armor', t)
    turret.box((2.26, 2.0, .12), loc=(0, .35, 1.3), bevel=.03, seg=1)                  # roof plate
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        a.part('Ammo', 'Hazard', t).box((.5, .3, .3), loc=(s * .55, 1.62, .36), bevel=.03)
        side = ((1.1, -1.2), (1.1, 1.5)) if s > 0 else ((-1.1, 1.5), (-1.1, -1.2))

        def at(y, z):
            u = (y + 1.2) / 2.7 if s > 0 else (1.5 - y) / 2.7
            return _face_frame(*side, 1.25, .94, z0=.015, u=u, v=(z - .015) / 1.25)
        _face_box(a, 'Turret_armor', 'Armor', at(.45, .6), (.9, .7, .05), parent=t)          # side door
        _face_box(a, 'Turret_steel', 'Steel', at(.2 if s > 0 else .7, .62), (.05, .22, .09), parent=t,
                  bevel=0, sink=-.035)                                                        # door handle
        _face_box(a, 'Turret_bins', 'Armor', at(1.2, .55), (.5, .5, .2), parent=t)            # rear bin
        _face_box(a, 'Turret_bins', 'Armor', at(1.2, .8), (.53, .05, .23), parent=t, bevel=0, sink=.02)
        _face_box(a, 'Turret_bins', 'Armor', at(-.6, .5), (.8, .36, .18), parent=t)           # front bin
        _face_box(a, 'Turret_bins', 'Armor', at(-.6, .69), (.83, .05, .21), parent=t, bevel=0, sink=.02)
        _smoke(a, tsteel, .78, -1.2, 1.05, s, count=3, gap=.08, r=.05, depth=.16)
        _rail(a, [(s * 1.02, -.4, 1.35), (s * 1.02, -.4, 1.42), (s * 1.02, 1.05, 1.42), (s * 1.02, 1.05, 1.35)],
              parent=t)
    a.part('Vents', 'Undercarriage', t).grille(.8, .5, loc=(0, 1.51, .75), slats=5, depth=.06, thickness=.04)
    tarm.box((.7, .5, .9), loc=(0, -1.32, .66), bevel=.05)  # cradle
    _hatch(a, .6, .4, 1.35, .28, parent=t)                                                  # commander
    _periscopes(a, [(.6 + math.cos(ang) * .37, .4 + math.sin(ang) * .37, 1.35, ang + R90)
                    for ang in (-R90, -R90 + .8, -R90 - .8)], parent=t)
    _hatch(a, -.4, .5, 1.35, .26, parent=t)                                                 # loader
    _roll(a, (0, 1.08, 1.47), 1.1, r=.11, parent=t)
    _antenna(a, t, -.8, 1.2, 1.3, 1.1)
    tip = _barrel(a, t, start_y=-1.55, length=4.4, radius=.13, height=.7, pitch=.14, brake=(.38, .42, .3),
                  sleeve=(.2, .8, .18), style='baffle', bands=(.4, .7))
    a.pivot('Muzzle_main', tip, t)
    _roof_mg(a, t, (.6, .4, 1.46), length=.75)


def scout_jeep(a):
    """Open-top 4x4 scout car with a pintle machine gun: louvred hood, guarded headlights, brush guard
    and winch, four seats, a braced roll bar, radio, ammunition and jerrycans in the rear tub, and a
    40 mm grenade launcher on a pedestal behind the roll bar (Mount_gun)."""
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    armor = a.part('Armor', 'Armor')
    chassis = a.part('Chassis', 'Undercarriage')
    rubber = a.part('Tyres', 'Rubber')
    seats = a.part('Seats', 'Canvas')
    chassis.box((1.45, 3.7, .26), loc=(0, 0, .55), bevel=.04)
    for sx in (-1, 1):
        for y in (-1.25, 1.2):
            rubber.cyl(.42, .34, loc=(sx * .86, y, .42), rot=ACROSS, seg=16, bevel=.07, bseg=1)
            armor.cyl(.24, .37, loc=(sx * .86, y, .42), rot=ACROSS, seg=10, bevel=.02, bseg=1)   # wheel discs
            steel.cyl(.09, .4, loc=(sx * .86, y, .42), rot=ACROSS, seg=6, bevel=0)               # hub caps
            body.box((.46, 1.05, .1), loc=(sx * .9, y, .92), bevel=.03, taper=(1, .8))
        a.part('Mud_flaps', 'Rubber').box((.34, .03, .26), loc=(sx * .86, -.78, .75), bevel=0)
        steel.box((.14, 1.3, .05), loc=(sx * .9, -.05, .64), bevel=0)                          # side steps
    body.prism([(-2.0, .62), (-2.0, .96), (-1.1, 1.12), (-.36, 1.14), (-.36, .62)], 1.7, bevel=.05)
    body.box((1.72, 2.3, .52), loc=(0, .8, .88), bevel=.05)
    chassis.grille(.7, .45, loc=(0, -.78, 1.15), rot=(-R90, 0, 0), slats=5, depth=.06, thickness=.035)  # hood louvres
    for sx in (-1, 1):                                                                        # hood latches
        steel.box((.04, .1, .06), loc=(sx * .86, -1.55, 1.0), bevel=0)
    # Seats: two in front, two in the back beside the gun pintle; a steering wheel.
    for x, y in ((-.38, -.05), (.38, -.05), (-.48, 1.0), (.48, 1.0)):
        seats.box((.44, .44, .12), loc=(x, y, 1.19), bevel=.03, seg=1)
        seats.box((.44, .1, .4), loc=(x, y + .25, 1.4), rot=(-.12, 0, 0), bevel=.03, seg=1)
    chassis.cyl(.16, .03, loc=(-.38, -.18, 1.42), rot=(-.9, 0, 0), seg=10, bevel=0)
    steel.tube([(-.38, -.18, 1.42), (-.38, -.3, 1.2)], .02, seg=4)
    frame = [(-.82, -.36, 1.12), (-.82, -.36, 1.66), (.82, -.36, 1.66), (.82, -.36, 1.12)]
    steel.tube(frame, .035, seg=8)
    a.part('Glass', 'Glass').box((1.6, .03, .44), loc=(0, -.38, 1.39), rot=(-.12, 0, 0), bevel=.01, seg=1)
    for sx in (-1, 1):                                                                        # mirrors
        steel.tube([(sx * .82, -.36, 1.3), (sx * .98, -.42, 1.3)], .015, seg=4)
        armor.box((.04, .13, .17), loc=(sx * 1.0, -.43, 1.33), bevel=.01, seg=1)
    steel.tube([(-.82, 1.55, 1.12), (-.82, 1.55, 1.78), (.82, 1.55, 1.78), (.82, 1.55, 1.12)], .045, seg=8)
    for sx in (-1, 1):                                                                        # roll bar braces
        steel.tube([(sx * .82, 1.55, 1.74), (sx * .82, 1.9, 1.14)], .03, seg=6)
    # Front: guarded headlights, grille, bumper with a winch and a brush guard.
    for sx in (-1, 1):
        _headlight(a, sx * .55, -2.0, .8, guard=False)
    chassis.grille(.64, .26, loc=(0, -2.03, .8), slats=4, depth=.05, thickness=.04)
    steel.box((1.5, .12, .14), loc=(0, -2.05, .6), bevel=.03)  # bumper
    armor.cyl(.07, .4, loc=(0, -2.14, .6), rot=ACROSS, seg=10, bevel=0)                    # winch drum
    _rail(a, [(-.62, -2.1, .67), (-.62, -2.17, .74), (-.62, -2.17, 1.0), (.62, -2.17, 1.0), (.62, -2.17, .74),
              (.62, -2.1, .67)], r=.025)
    # Rear: spare tyre, jerrycans, tail lights; radio and ammunition in the tub.
    rubber.cyl(.36, .22, loc=(0, 2.03, 1.02), rot=FORWARD, seg=16, bevel=.06, bseg=1)
    armor.cyl(.2, .25, loc=(0, 2.03, 1.02), rot=FORWARD, seg=10, bevel=0)
    for sx in (-1, 1):
        a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(sx * .58, 2.0, 1.05), bevel=.03)
        _taillight(a, sx * .72, 1.95, .72)
    armor.box((.4, .34, .3), loc=(.55, 1.65, 1.26), bevel=.02, seg=1)                     # radio
    a.part('Radio_dials', 'Glass').box((.26, .02, .1), loc=(.55, 1.475, 1.3), bevel=0)
    a.part('Ammo_boxes', 'Crate').box((.4, .3, .24), loc=(-.52, 1.65, 1.23), bevel=.02, seg=1)
    steel.cyl(.012, 1.1, loc=(.72, 1.75, 1.7), seg=5, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.045, loc=(.72, 1.75, 2.27), seg=8, rings=5)

    t = a.pivot('Turret', (0, .72, 1.14))
    a.part('Mount', 'Steel', t).cyl(.07, .52, loc=(0, 0, .26), seg=10, bevel=.01)
    a.part('Gun_shield', 'Armor', t).box((.66, .06, .42), loc=(0, -.22, .66), bevel=.02, taper=(.9, 1))
    cannon = a.part('Main_cannon', 'Steel', t)
    cannon.box((.14, .42, .16), loc=(0, 0, .64), bevel=.02)
    cannon.cyl(.035, 1.0, loc=(0, -.66, .66), rot=FORWARD, seg=8, bevel=0)
    cannon.cyl(.05, .12, loc=(0, -1.11, .66), rot=FORWARD, seg=8, bevel=0)                 # flash hider
    cannon.box((.05, .16, .08), loc=(0, .24, .6), rot=(.3, 0, 0), bevel=0)                  # grips
    a.part('Ammo_box', 'Armor', t).box((.2, .18, .16), loc=(.16, .05, .56), bevel=.02)
    a.pivot('Muzzle_main', (0, -1.16, .66), t)  # the pintle machine gun is the jeep's main weapon
    # Second weapon: a 40 mm grenade launcher on a pedestal in the rear tub behind the roll bar
    # (Mount_gun / Muzzle_gun): its cradle clears the spare tyre and its top stays under 1.73 m, so the
    # pintle gun's barrel sweeps over it.
    wpn.agl(a, (0, 1.8, 1.14), post=.26, shield=.22, ammo=-1, sight='side')


# ----------------------------------------------------------------------------- new vehicles
def _hull_section(y, zb, z1, z2, zt, wb, w1, w2, wt):
    """Eight-point hull cross-section: narrow belly, flared lower flank (zb->z1), short upright
    band (z1->z2) and inward-sloped upper flank to the roof (z2->zt)."""
    return [(-wb, y, zb), (wb, y, zb), (w1, y, z1), (w2, y, z2), (wt, y, zt), (-wt, y, zt), (-w2, y, z2),
            (-w1, y, z1)]


def apc(a):
    """8x8 wheeled armoured personnel carrier with a wedge nose and a 30 mm turret: bolted add-on
    armour, troop hatches with vision blocks, side bins, slat armour flanking the rear door and a
    bedroll on the roof."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.3, -1.12, .82, 2.0):
        for s in (-1, 1):
            _wheel(a, s * 1.15, y, .56, .44)
    hull.loft([
        _hull_section(-3.42, .86, .95, 1.03, 1.12, .62, .8, .82, .66),
        _hull_section(-2.75, .48, 1.02, 1.28, 1.5, .9, 1.2, 1.24, .96),
        _hull_section(-1.9, .45, 1.05, 1.35, 2.0, .9, 1.24, 1.28, 1.0),
        _hull_section(3.2, .45, 1.05, 1.35, 2.0, .9, 1.24, 1.28, 1.0),
        _hull_section(3.4, .58, 1.05, 1.33, 1.93, .86, 1.2, 1.24, .96),
    ], bevel=.06, seg=2)
    # Bolted add-on armour on the sloped upper flanks (rotated onto the 23-degree slope).
    slope = math.atan2(1.28 - 1.0, 2.0 - 1.35)
    for s in (-1, 1):
        for y in (-1.25, .15, 1.55):
            armor.box((.06, 1.3, .52), loc=(s * (1.14 + .018), y, 1.683), rot=(0, -s * slope, 0), bevel=.015, seg=1)
        _headlight(a, s * .45, -3.42, .99)
        steel.box((.12, .2, .12), loc=(s * .5, -3.3, .78), bevel=.02, seg=1)                # tow hooks
        _taillight(a, s * .9, 3.4, 1.62)
        steel.box((.1, .12, .08), loc=(s * .47, 3.45, 1.66), bevel=.01, seg=1)             # door hinges
        steel.box((.1, .12, .08), loc=(s * .47, 3.45, .9), bevel=.01, seg=1)
        # Troop hatches: hinged on the centre line, a grab handle and a vision block in front.
        armor.box((.75, 1.15, .06), loc=(s * .45, 2.35, 2.01), bevel=.015, seg=1)
        steel.box((.06, 1.0, .05), loc=(s * .12, 2.35, 2.04), bevel=0)
        _rail(a, [(s * .62, 2.2, 2.03), (s * .62, 2.2, 2.09), (s * .62, 2.5, 2.09), (s * .62, 2.5, 2.03)])
        _periscopes(a, [(s * .45, 1.66, 1.99, 0)])
        # Vision blocks along the roof edges of the troop compartment, a bin between the wheels.
        _periscopes(a, [(s * .93, y, 1.99, s * R90) for y in (.2, .9)])
        _stowage_bin(a, (s * 1.33, -.15, 1.06), (.14, .7, .28), latch_side=s)
        # Slat armour flanking the rear door, on brackets.
        _slats(a, _frame((s * .9, 3.56, 1.0), (0, 0, 0)), .55, .56, 5)
        for dx in (-.24, .24):
            steel.box((.04, .18, .04), loc=(s * .9 + dx, 3.48, 1.2), bevel=0)
    # Trim vane folded on the upper glacis, driver hatch and vision blocks.
    armor.box((1.1, .06, .34), loc=(0, -3.0, 1.37), rot=(-1.04, 0, 0), bevel=.015, seg=1)
    _hatch(a, -.52, -1.55, 1.99, .28)
    glass = a.part('Vision_blocks', 'Glass')
    for dx in (-.16, 0, .16):
        glass.box((.12, .05, .07), loc=(-.52 + dx, -1.92, 1.99), rot=(-.53, 0, 0), bevel=.01, seg=1)
    a.part('Deck', 'Undercarriage').grille(.72, .7, loc=(.48, -1.3, 2.01), rot=(-R90, 0, 0), slats=6, depth=.07,
                                           thickness=.04)
    armor.box((1.0, .08, 1.0), loc=(0, 3.42, 1.25), bevel=.02, seg=1)                  # rear door
    steel.box((.3, .06, .05), loc=(.25, 3.48, 1.3), bevel=.01, seg=1)                   # door handle
    dark.box((1.2, .3, .08), loc=(0, 3.47, .6), bevel=.02, seg=1)                       # rear step
    steel.cyl(.62, .1, loc=(0, -.55, 2.02), seg=20, bevel=.02, bseg=1)                  # turret ring
    _roll(a, (0, 3.05, 2.08), 1.3, r=.1)
    for s in (-1, 1):  # roof bins behind the turret's sweep, tow cable along the right roof edge
        _stowage_bin(a, (s * .45, 1.15, 1.99), (.56, .62, .22), latch_side=0)
    _cable(a, [(1.03, -1.7, 1.985), (1.03, .9, 1.985), (1.03, 3.0, 1.97)])
    _antenna(a, None, -.85, 3.0, 1.95, 1.3)

    t = a.pivot('Turret', (0, -.55, 2.06))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.55, .62), (.55, .62), (.66, .12), (.55, -.42), (.3, -.66), (-.3, -.66), (-.55, -.42), (-.66, .12)]
    turret.prism(outline, .5, loc=(0, 0, .27), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.36, .24, .3), loc=(0, -.72, .28), bevel=.035)                           # mantlet
    tarm.box((.9, .3, .3), loc=(0, .7, .25), bevel=.035, taper=(.95, .9))              # bustle
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.box((.26, .26, .22), loc=(.3, .1, .6), bevel=.035)                          # commander sight
    a.part('Sight', 'Glass', t).box((.18, .04, .11), loc=(.3, -.03, .62), bevel=.01, seg=1)
    for s in (-1, 1):
        _smoke(a, tsteel, .44, -.4, .44, s, count=2, gap=.07)
    _hatch(a, -.22, .22, .49, .19, parent=t)
    # Twin ATGM launcher box on an arm off the left side.
    tsteel.box((.34, .22, .12), loc=(-.72, .02, .38), bevel=.02, seg=1)
    launcher = a.part('Launcher', 'Armor', t)
    launcher.box((.3, 1.0, .46), loc=(-.95, .02, .42), bevel=.04)
    for z in (.31, .53):
        _tube_mouth(a, t, _frame((-.95, -.47, z), FORWARD), .085, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-.95, -.53, .42), t)
    tip = _barrel(a, t, start_y=-.84, length=1.95, radius=.05, height=.28, brake=(.11, .2, .11),
                  sleeve=(.1, .34, .075), seg=10, style='flash')
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .25, -.69, .33, length=.32, housing=.3)


def mlrs(a):
    """6x6 armoured truck carrying a trainable 12-round rocket pod: a cab with door lines, mirrors, a
    brush guard and roof hatch, a spare tyre and stowage on the bed, mudguards over the rear bogie, and a
    heavy machine gun on the cab roof (Mount_mg)."""
    cab = a.part('Cab', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.55, 1.2, 2.55):
        for s in (-1, 1):
            _wheel(a, s * 1.02, y, .55, .42)
    for s in (-1, 1):
        dark.box((.2, 6.9, .3), loc=(s * .46, -.15, .8), bevel=.03, seg=1)              # frame rails
    dark.box((1.5, 1.6, .48), loc=(0, -2.85, .92), bevel=.05)                           # engine block
    dark.grille(1.1, .3, loc=(0, -3.66, .97), slats=4, depth=.06, thickness=.05)
    steel.box((2.3, .2, .22), loc=(0, -3.72, .72), bevel=.04)                           # bumper
    cab.prism([(-3.66, 1.1), (-3.72, 1.72), (-3.38, 2.62), (-2.0, 2.7), (-1.92, 1.1)], 2.36, bevel=.07)
    glass = a.part('Windows', 'Glass')
    (wy, wz), rx = (-3.72 + .34 * .55, 1.72 + .9 * .55), -math.atan2(.34, .9)
    ny, nz = -math.cos(rx), -math.sin(rx)  # windshield outward normal (forwards and up)
    # Brush guard over the grille and lamps.
    _rail(a, [(-.9, -3.74, .86), (-.9, -3.84, 1.0), (-.9, -3.84, 1.46), (.9, -3.84, 1.46), (.9, -3.84, 1.0),
              (.9, -3.74, .86)], r=.03)
    _rail(a, [(-.9, -3.84, 1.2), (.9, -3.84, 1.2)], r=.025)
    for s in (-1, 1):
        glass.box((.86, .04, .4), loc=(s * .5, wy + ny * .012, wz + nz * .012), rot=(rx, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .7, .34), loc=(s * 1.19, -2.72, 2.22), bevel=.01, seg=1)
        _headlight(a, s * .82, -3.69, 1.34, guard=False)
        armor.box((.54, 1.3, .07), loc=(s * 1.02, -2.55, 1.15), bevel=.02, seg=1)        # front fenders
        armor.box((.48, .07, .34), loc=(s * 1.02, -1.93, .97), bevel=.02, seg=1)         # mud flaps
        # Doors: hinge and shut lines and a handle; a mirror on an arm.
        for y in (-3.22, -2.2):
            armor.box((.03, .04, 1.1), loc=(s * 1.187, y, 1.8), bevel=0)
        steel.box((.04, .16, .05), loc=(s * 1.195, -2.4, 1.86), bevel=0)
        steel.tube([(s * 1.16, -3.25, 2.2), (s * 1.28, -3.32, 2.24)], .018, seg=4)
        armor.box((.05, .16, .26), loc=(s * 1.3, -3.34, 2.14), bevel=.01, seg=1)
        # Rear bogie: mudguard over both wheels, mud flaps behind them, rear lights and jacks.
        armor.box((.46, 2.62, .06), loc=(s * 1.04, 1.875, 1.16), bevel=.015, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.02, 3.2, .86), bevel=0)
        _taillight(a, s * .62, 3.625, 1.24)
        # Stabiliser jacks at the rear corners, pads stowed just above the ground.
        armor.box((.26, .26, .46), loc=(s * .95, 3.42, 1.0), bevel=.03, seg=1)
        steel.cyl(.07, .6, loc=(s * .95, 3.42, .55), seg=10, bevel=0)
        steel.cyl(.2, .07, loc=(s * .95, 3.42, .25), seg=12, bevel=.02, bseg=1)
        armor.box((.14, .9, .5), loc=(s * .9, -.7, .9), bevel=.03)                       # stowage lockers
        steel.box((.03, .06, .08), loc=(s * .98, -.7, 1.02), bevel=0)                     # locker latches
    _hatch(a, .45, -2.6, 2.68, .26)                                                      # cab hatch
    for x in (-.5, 0, .5):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x, -3.37, 2.63), bevel=0)
    armor.box((.6, .4, .18), loc=(-.45, -2.35, 2.76), bevel=.02, seg=1)                  # radio / air unit
    steel.cyl(.07, 1.5, loc=(.95, -1.9, 2.02), seg=8, bevel=0)                          # exhaust stack
    steel.cyl(.1, .18, loc=(.95, -1.9, 2.72), seg=8, bevel=0)
    for z in (1.6, 2.3):
        steel.box((.06, .12, .06), loc=(.95, -1.97, z), bevel=0)                         # stack brackets
    armor.box((2.3, 5.25, .2), loc=(0, 1.0, 1.24), bevel=.04)                           # launcher bed
    # Bed stowage between the cab and the launcher: a spare tyre lying flat, a bin and jerrycans.
    a.part('Tyres', 'Rubber').cyl(.48, .3, loc=(-.5, -1.1, 1.48), seg=16, bevel=.06, bseg=1)
    a.part('Hubs', 'Steel').cyl(.24, .04, loc=(-.5, -1.1, 1.64), seg=10, bevel=0)
    _stowage_bin(a, (.52, -1.25, 1.33), (.7, .8, .4), latch_side=0)
    _jerrycans(a, (.52, -.38, 1.33), 2, axis='x')
    for s in (-1, 1):  # raised bed edges with tie-down rings, bins at the rear corners
        armor.box((.07, 5.2, .07), loc=(s * 1.11, 1.0, 1.365), bevel=0)
        for y in (-1.2, .2, 1.6, 3.0):
            steel.box((.04, .1, .06), loc=(s * 1.165, y, 1.26), bevel=0)
        _stowage_bin(a, (s * .68, 3.12, 1.33), (.62, .72, .36), latch_side=0)
    _antenna(a, None, -.9, -2.1, 2.66, 1.2)

    t = a.pivot('Turret', (0, 1.55, 1.34))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.85, .14, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                    # turntable
    tarm.box((1.5, 1.6, .4), loc=(0, .1, .3), bevel=.05, taper=(.9, .92))
    pitch, length, height, width = .35, 3.5, 1.12, 1.95
    hinge = Vector((0, .95, .52))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    centre = hinge - turn @ Vector((0, length / 2, -height / 2))
    pod = _frame(centre, rot)
    a.part('Pod', 'Team', t).box((width, length, height), loc=centre, rot=rot, bevel=.06)
    frame = a.part('Pod_frame', 'Armor', t)
    for y in (-length / 2 + .12, length / 2 - .12):  # reinforcing bands at both ends
        frame.box((width + .06, .16, height + .06), loc=pod @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
    for x in (-.55, .55):                            # raised top rails and lifting lugs at the corners
        frame.box((.12, length - .5, .05), loc=pod @ Vector((x, 0, height / 2 + .015)), rot=rot, bevel=0)
        for y in (-length / 2 + .12, length / 2 - .12):
            tsteel.box((.1, .1, .08), loc=pod @ Vector((x * 1.4, y, height / 2 + .06)), rot=rot, bevel=0)
    for s in (-1, 1):                                 # side ribs
        for y in (-.7, 0, .7):
            frame.box((.05, .1, height - .1), loc=pod @ Vector((s * (width / 2 + .015), y, 0)), rot=rot, bevel=0)
    tsteel.cyl(.12, 1.7, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)             # elevation hinge
    for s in (-1, 1):
        tarm.box((.14, .5, .5), loc=(s * .8, .95, .4), bevel=.02, seg=1)                  # hinge cheeks
        tsteel.limb((s * .5, -.35, .42), tuple(pod @ Vector((s * .5, -.55, -height / 2 + .02))), .12, .12,
                    bevel=.02)                                                           # elevation rams
    for row in (-.36, 0, .36):
        for col in (-.66, -.22, .22, .66):
            _tube_mouth(a, t, pod @ _frame((col, -length / 2, row), FORWARD), .15, protrude=.07, seg=10)
    a.pivot('Muzzle_main', tuple(pod @ Vector((0, -length / 2 - .07, 0))), t)
    # Second weapon: a heavy machine gun on the cab roof behind the hatch (Mount_mg / Muzzle_mg), well in
    # front of the pod's swing. roof(y) is the cab roof line.
    wpn.hmg(a, (.45, -2.18, 2.62 + (-2.18 + 3.38) / 1.38 * .08), post=.22, ammo=-1)


def aa_vehicle(a):
    """Tracked self-propelled anti-aircraft gun: twin 35 mm cannons with slotted flash hiders, a search
    radar and a SAM box; skirts, fender stowage, a commander's hatch and a bustle basket."""
    tracks(a, 1.02, 4.6, .72, .25, 5, .42, belt_width=.5, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    front, brow = (-2.4, .74), (-1.65, 1.12)
    hull.prism([(-2.4, .5), front, brow, (2.05, 1.12), (2.35, .92), (2.35, .5)], 1.62, bevel=.06)
    for s in (-1, 1):
        _skirt(a, s, 1.3, -2.15, 2.05, .6, 1.0, 4, thick=.1, bolts=False)
        _headlight(a, s * .55, -2.4, .63)
        steel.box((.14, .16, .1), loc=(s * .22, -2.46, .56), bevel=0)                     # tow hooks
        steel.cyl(.08, .3, loc=(s * .3, 2.42, .8), rot=FORWARD, seg=10, bevel=.015, bseg=1)  # exhausts
        _taillight(a, s * .64, 2.35, .8)
    _stowage_bin(a, (-1.03, 1.3, .85), (.36, .9, .26), latch_side=0)
    _shovel(a, (-1.1, -1.05, .875), length=1.0)
    _jerrycans(a, (1.03, 1.45, .85), 2)
    _cable(a, [(1.0, -1.95, .89), (1.0, -.4, .89), (.98, .7, .89), (.92, 1.02, .89)])
    _hatch(a, 0, -1.25, 1.11, .24)                                                      # driver's hatch
    _periscopes(a, [(dx, -1.58, 1.1, 0) for dx in (-.17, 0, .17)])
    deck.grille(1.0, .5, loc=(0, 1.72, 1.13), rot=(-R90, 0, 0), slats=5, depth=.08, thickness=.04)
    _grille_frame(a, 0, 1.72, 1.11, 1.0, .5, t=.05)
    steel.cyl(.8, .12, loc=(0, .15, 1.16), seg=20, bevel=.03, bseg=1)

    t = a.pivot('Turret', (0, .15, 1.2))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.74, .98), (.74, .98), (.8, .3), (.74, -.55), (.42, -.92), (-.42, -.92), (-.74, -.55), (-.8, .3)]
    turret.prism(outline, .72, loc=(0, 0, .38), axis='Z', bevel=.05, taper=.9)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tips = []
    for s, suffix in ((-1, '_L'), (1, '_R')):
        tarm.box((.3, 1.3, .5), loc=(s * .92, -.12, .42), bevel=.04, taper=(.9, .95))      # gun housings
        tsteel.box((.2, .7, .26), loc=(s * .74, .05, .42), bevel=.02, seg=1)                # trunnion arms
        tips.append(_barrel(a, t, start_y=-.76, length=2.25, radius=.055, height=.44, brake=(.13, .24, .13),
                            sleeve=(.07, .34, .09), x=s * .92, suffix=suffix, seg=10, style='flash'))
        _smoke(a, tsteel, .5, -.8, .6, s, count=3, gap=.07)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    # 4-cell SAM box on the roof, front left; tracking sensor front right.
    launcher = a.part('Launcher', 'Armor', t)
    launcher.box((.56, 1.0, .56), loc=(-.36, -.08, .99), bevel=.04)
    for x in (-.49, -.23):
        for z in (.86, 1.12):
            _tube_mouth(a, t, _frame((x, -.58, z), FORWARD), .1, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-.36, -.64, .99), t)
    tsteel.box((.42, .36, .3), loc=(.36, -.42, .86), bevel=.04)
    a.part('Sight', 'Glass', t).box((.3, .04, .14), loc=(.36, -.6, .88), bevel=.01, seg=1)
    _hatch(a, .38, .3, .7, .2, parent=t)                                               # commander's hatch
    _periscopes(a, [(.38, .02, .7, 0), (.64, .3, .7, R90)], parent=t, size=(.1, .06, .07))
    _basket(a, -.6, .6, 1.0, 1.3, .12, .28, parent=t, box=False)
    # Search radar pedestal at the rear; the dish spins on its own pivot.
    tsteel.cyl(.14, .3, loc=(0, .72, .86), seg=12, bevel=.02, bseg=1)
    r = a.pivot('Radar', (0, .72, 1.0), t)
    mast = a.part('Radar_mast', 'Steel', r)
    mast.cyl(.07, .46, loc=(0, 0, .23), seg=8, bevel=0)
    mast.box((.1, .24, .12), loc=(0, -.08, .48), bevel=.02, seg=1)             # yoke to the dish back
    mast.limb((0, -.22, .5), (0, -.52, .56), .035, .035, bevel=0)             # feed horn
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.18, .5), .6, .26, depth=.14, tilt=.25)
    _antenna(a, t, .6, .7, .7, .9)


def flame_tank(a):
    """Medium tank with a short, fat flame projector and armoured fuel tanks on the rear deck; four-panel
    skirts, jerrycan racks and tools on the fenders, a hatch with vision blocks and turret bins."""
    tracks(a, 1.12, 4.8, .78, .27, 6, .45, belt_width=.54, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    fuel = a.part('Fuel_tanks', 'Fuel')
    hazard = a.part('Hazard_bands', 'Hazard')
    hull.prism([(-2.5, .52), (-2.5, .78), (-1.7, 1.2), (2.2, 1.2), (2.5, .98), (2.5, .52)], 1.76, bevel=.06)
    for s in (-1, 1):
        _skirt(a, s, 1.42, -2.25, 2.15, .64, 1.08, 4, thick=.1)
        _headlight(a, s * .55, -2.5, .66)
        steel.box((.14, .16, .1), loc=(s * .25, -2.56, .58), bevel=.02, seg=1)             # tow hooks
        steel.cyl(.08, .28, loc=(s * .3, 2.52, .86), rot=FORWARD, seg=10, bevel=.015, bseg=1)  # exhausts
        _taillight(a, s * .64, 2.5, .76)
        _jerrycans(a, (s * 1.125, 1.4, .91), 3)                                            # spare fuel
        gy, gz, grot = _glacis((-2.5, .78), (-1.7, 1.2), .5, 0)
        _track_links(a, _frame((s * .5, gy, gz), (grot, 0, 0)), 3, width=.42)
        # Fuel tanks lying along the rear deck in armoured cradles.
        x = s * .45
        fuel.cyl(.3, 1.5, loc=(x, 1.52, 1.53), rot=FORWARD, seg=14, bevel=.1)
        for y in (1.02, 2.02):
            hazard.cyl(.315, .1, loc=(x, y, 1.53), rot=FORWARD, seg=14, bevel=0)
            armor.box((.58, .16, .2), loc=(x, y, 1.26), bevel=.02, seg=1)                  # cradles
        steel.tube([(x, .72, 1.5), (x * .7, .5, 1.36), (x * .45, .28, 1.28)], .045, seg=6)  # feed pipes
        steel.cyl(.06, .08, loc=(x, .74, 1.53), rot=FORWARD, seg=8, bevel=0)
    armor.box((1.62, .12, .5), loc=(0, .66, 1.44), rot=(.35, 0, 0), bevel=.03)             # blast shield
    armor.box((1.66, .1, .56), loc=(0, 2.32, 1.36), bevel=.03, seg=1)                      # rear guard
    for s in (-1, 1):                                                                        # tub side plates
        armor.box((.08, 1.62, .42), loc=(s * .82, 1.52, 1.4), bevel=.02, seg=1, taper=(1, .96))
    # Fender stowage: tools and a bin on the left, the tow cable on the right.
    _shovel(a, (-1.18, -1.45, .935), length=1.0)
    _stowage_bin(a, (-1.125, .15, .91), (.4, .9, .26), latch_side=0)
    _cable(a, [(1.1, -2.05, .95), (1.1, -.2, .95), (1.08, .8, .95), (1.02, 1.02, .95)])
    _hatch(a, 0, -1.3, 1.19, .24)                                                          # driver's hatch
    _periscopes(a, [(dx, -1.63, 1.19, 0) for dx in (-.17, 0, .17)])
    steel.cyl(.74, .12, loc=(0, -.45, 1.24), seg=20, bevel=.03)

    t = a.pivot('Turret', (0, -.45, 1.3))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.6, .66), (.6, .66), (.74, .2), (.66, -.42), (.36, -.74), (-.36, -.74), (-.66, -.42), (-.74, .2)]
    turret.prism(outline, .56, loc=(0, 0, .28), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.52, .3, .42), loc=(0, -.82, .3), bevel=.05)                                  # mantlet
    tarm.box((.9, .36, .34), loc=(0, .72, .26), bevel=.04, taper=(.95, .9))
    tsteel = a.part('Turret_steel', 'Steel', t)
    _hatch(a, -.28, .16, .55, .22, parent=t)
    _periscopes(a, [(-.28 + math.cos(ang) * .3, .16 + math.sin(ang) * .3, .55, ang + R90)
                    for ang in (-R90, -R90 - .75, R90 + .6)], parent=t, size=(.1, .06, .07))
    _periscopes(a, [(.3, -.34, .55, 0)], parent=t)                                         # gunner's sight
    for s in (-1, 1):
        _smoke(a, tsteel, .54, -.42, .44, s, count=2)
    for b0, b1 in (((.74, .2), (.6, .66)), ((-.6, .66), (-.74, .2))):
        m = _face_frame(b0, b1, .56, .86, u=.5, v=.42)
        _face_box(a, 'Turret_bins', 'Armor', m, (.4, .26, .14), parent=t)
        _face_box(a, 'Turret_bins', 'Armor', m, (.43, .04, .17), parent=t, bevel=0, lift=.13, sink=.02)
    _antenna(a, t, .45, .56, .52, .9)
    # Flame projector: fat barrel with cooling rings and a tapered nozzle; a pilot light glows below.
    cannon = a.part('Main_cannon', 'Steel', t)
    y0, h, length = -.96, .3, 1.0
    cannon.cyl(.14, length, loc=(0, y0 - length / 2, h), rot=FORWARD, seg=14, bevel=.02, bseg=1)
    cannon.cyl(.2, .44, loc=(0, y0 - .2, h), rot=FORWARD, seg=14, bevel=.03)
    for y in (-.62, -.8):
        cannon.cyl(.165, .06, loc=(0, y0 + y, h), rot=FORWARD, seg=14, bevel=.01, bseg=1)
    cannon.tube([(.2, y0 - .15, h - .02), (.2, y0 - .6, h - .02), (.12, y0 - .9, h - .1)], .03, seg=6)  # fuel line
    a.part('Muzzle_brake', 'Undercarriage', t).cyl(.17, .26, r2=.11, loc=(0, y0 - length - .1, h), rot=FORWARD,
                                                   seg=14, bevel=.02)
    a.part('Muzzle_brake_glow', 'Alloy', t).sphere(.04, loc=(0, y0 - length - .16, h - .14), seg=8, rings=5)
    a.pivot('Muzzle_main', (0, y0 - length - .23, h), t)
    _coax(a, t, .34, -.72, .4, length=.34, housing=.34)


# ----------------------------------------------------------------------------- roster v3
def _flank(bottom, top, t, out=.02):
    """Point a fraction t up a sloped hull flank running from `bottom` to `top` ((x, z) on the +X
    side), pushed `out` along its outward normal, and the flank's lean from vertical. A box laid
    on side s uses loc=(s * x, y, z) and rot=(0, -s * lean, 0)."""
    (x0, z0), (x1, z1) = bottom, top
    dx, dz = x1 - x0, z1 - z0
    n = math.hypot(dx, dz)
    return x0 + dx * t + dz / n * out, z0 + dz * t - dx / n * out, math.atan2(-dx, dz)


def _glacis(front, back, t, out=.02):
    """Point a fraction t along a sloped front plate from `front` to `back` ((y, z), rising towards
    the back), pushed `out` along its normal, and the X rotation that lays a box flat on it."""
    (y0, z0), (y1, z1) = front, back
    dy, dz = y1 - y0, z1 - z0
    n = math.hypot(dy, dz)
    return y0 + dy * t - dz / n * out, z0 + dz * t + dy / n * out, math.atan2(dz, dy)


def _rws(a, parent, loc, length=.85):
    """Remote weapon station on its own `Mount_mg` yaw pivot: armoured cradle, sensor head and a
    heavy machine gun, with `Muzzle_mg` at the barrel tip."""
    m = a.pivot('Mount_mg', loc, parent)
    body = a.part('RWS', 'Armor', m)
    body.cyl(.2, .1, loc=(0, 0, .05), seg=12, bevel=.02, bseg=1)
    body.box((.4, .56, .3), loc=(0, .06, .25), bevel=.04, seg=1)               # cradle
    body.box((.22, .3, .26), loc=(-.32, .02, .3), bevel=.03, seg=1)             # sensor head
    body.box((.16, .3, .2), loc=(.3, .14, .25), bevel=.03, seg=1)               # ammo box
    a.part('RWS_sensor', 'Glass', m).box((.16, .04, .14), loc=(-.32, -.14, .31), bevel=.01, seg=1)
    gun = a.part('RWS_gun', 'Steel', m)
    gun.box((.13, .4, .13), loc=(.08, -.3, .3), bevel=.02, seg=1)             # receiver
    front = -.5
    gun.cyl(.03, length, loc=(.08, front - length / 2 + .02, .3), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.046, .12, loc=(.08, front - length + .06, .3), rot=FORWARD, seg=8, bevel=0)  # flash hider
    a.pivot('Muzzle_mg', (.08, front - length, .3), m)


# Mudguard arch (y offset, z) over a 0.52 m wheel: outer edge forwards, inner edge back.
ARCH = [(-.54, .9), (-.38, 1.14), (.38, 1.14), (.54, .9), (.48, .9), (.34, 1.09), (-.34, 1.09), (-.48, .9)]


def armored_car(a):
    """6x6 wheeled armoured car: a narrow wedge hull between six big outboard wheels under separate
    mudguards (the 8x8 APC hides its wheels under a wide hull), and a small 30 mm turret with a bustle
    basket; bins between the wheels, jerrycans and a tow cable on the deck, guarded headlights."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for y in (-2.05, -.15, 1.75):
        for s in (-1, 1):
            _wheel(a, s * 1.09, y, .52, .4)
            hull.prism([(y + dy, z) for dy, z in ARCH], .46, loc=(s * 1.09, 0, 0), bevel=0)   # mudguards
            dark.box((.26, .18, .14), loc=(s * .9, y, .52), bevel=.02, seg=1)                # hub carriers
    full = (.44, .78, 1.2, 1.56, .7, .88, .88, .7)
    hull.loft([
        _hull_section(-3.15, .74, .8, .86, .92, .5, .64, .64, .52),
        _hull_section(-2.7, .5, .78, 1.1, 1.2, .66, .86, .86, .68),
        _hull_section(-1.45, *full),
        _hull_section(2.9, *full),
        _hull_section(3.15, .58, .8, 1.18, 1.5, .66, .86, .86, .68),
    ], bevel=.06, seg=2)
    for s in (-1, 1):
        for y, d in ((-1.1, .74), (.8, .74), (2.68, .82)):                                # side bins
            _stowage_bin(a, (s * .97, y, .81), (.2, d, .32), latch_side=s)
        _headlight(a, s * .4, -3.15, .83)
        steel.box((.12, .2, .1), loc=(s * .26, -3.18, .76), bevel=.02, seg=1)             # tow hooks
        a.part('Tail_lights', 'Alloy').box((.12, .06, .1), loc=(s * .66, 3.16, 1.32), bevel=.01, seg=1)
        dark.grille(.34, .26, loc=(s * .58, 3.17, .98), rot=(0, 0, math.pi), slats=3, depth=.05, thickness=.04)
        dark.grille(.5, .55, loc=(s * .32, 2.2, 1.57), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
        _grille_frame(a, s * .32, 2.2, 1.55, .5, .55, t=.04)
    armor.box((.46, .06, .56), loc=(0, 3.17, 1.04), bevel=.015, seg=1)                    # rear door
    steel.box((.2, .05, .05), loc=(.12, 3.21, 1.08), bevel=.01, seg=1)
    # Driver hatch and vision blocks on the glacis.
    _hatch(a, -.36, -1.2, 1.55, .24)
    sy, sz, srot = _glacis((-2.7, 1.2), (-1.45, 1.56), .42, .1)                         # spare wheel
    a.part('Tyres', 'Rubber').cyl(.42, .2, loc=(.1, sy, sz), rot=(srot, 0, 0), seg=14, bevel=.05, bseg=1)
    hy, hz, _ = _glacis((-2.7, 1.2), (-1.45, 1.56), .42, .215)
    a.part('Hubs', 'Steel').cyl(.2, .03, loc=(.1, hy, hz), rot=(srot, 0, 0), seg=10, bevel=0)
    _jerrycans(a, (0, 2.7, 1.55), 3, axis='x')
    _cable(a, [(.62, -1.3, 1.585), (.62, .6, 1.585), (.6, 1.8, 1.585)])
    glass = a.part('Vision_blocks', 'Glass')
    gy, gz, grot = _glacis((-2.7, 1.2), (-1.45, 1.56), .86, .012)
    for dx in (-.14, 0, .14):
        glass.box((.12, .07, .05), loc=(-.36 + dx, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    steel.cyl(.66, .1, loc=(0, -.15, 1.58), seg=20, bevel=.02, bseg=1)                   # turret ring

    t = a.pivot('Turret', (0, -.15, 1.63))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.62, .72), (.62, .72), (.78, .18), (.66, -.46), (.36, -.8), (-.36, -.8), (-.66, -.46), (-.78, .18)]
    turret.prism(outline, .46, loc=(0, 0, .23), axis='Z', bevel=.05, taper=.8)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.44, .26, .32), loc=(0, -.88, .24), bevel=.035)                           # mantlet
    tarm.box((1.0, .34, .3), loc=(0, .82, .21), bevel=.035, taper=(.94, .9))             # bustle
    tsteel = a.part('Turret_steel', 'Steel', t)
    sight = a.part('Sight', 'Glass', t)
    tsteel.box((.26, .26, .22), loc=(-.3, .12, .55), bevel=.035)                        # commander sight
    sight.box((.18, .04, .11), loc=(-.3, -.01, .57), bevel=.01, seg=1)
    tsteel.box((.22, .2, .16), loc=(.34, -.3, .5), bevel=.03)                           # gunner sight
    sight.box((.16, .04, .08), loc=(.34, -.41, .5), bevel=.01, seg=1)
    for s in (-1, 1):
        _smoke(a, tsteel, .5, -.34, .38, s, count=3, gap=.07)
    _hatch(a, .3, .32, .45, .2, parent=t)
    _basket(a, -.45, .45, 1.0, 1.26, .08, .24, parent=t, box=False)
    _antenna(a, t, -.46, .6, .42, 1.1)
    tip = _barrel(a, t, start_y=-.98, length=2.35, radius=.05, height=.25, brake=(.11, .22, .11),
                  sleeve=(.1, .46, .085), seg=10, style='flash')
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .3, -.74, .32, length=.3, housing=.26)


def _sponson_section(y, zb, zs, zt, wb, ws, wt):
    """Ten-point hull section with sponsons over the tracks: belly between the belts (wb), a flat
    sponson floor at zs out to ws, a short upright edge, then a sloped flank up to the roof."""
    return [(-wb, y, zb), (wb, y, zb), (wb, y, zs), (ws, y, zs), (ws, y, zs + .08), (wt, y, zt), (-wt, y, zt),
            (-ws, y, zs + .08), (-ws, y, zs), (-wb, y, zs)]


def tank_destroyer(a):
    """Low tank destroyer: sloped sponson hull with bolt-on plates, an open-top turret with side bins
    and a very long 105 mm gun with a double-baffle muzzle brake; spare wheel, jerrycans and a tow
    cable on the hull."""
    tracks(a, 1.22, 6.2, .8, .28, 7, .45, belt_width=.56, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.46, .96, 1.36, .95, 1.52, 1.16)
    hull.loft([
        _sponson_section(-3.5, .62, .96, 1.1, .9, 1.4, 1.24),
        _sponson_section(-2.1, *body),
        _sponson_section(3.25, *body),
        _sponson_section(3.5, .56, .96, 1.28, .92, 1.48, 1.14),
    ], bevel=.05, seg=2)
    x, z, lean = _flank((1.52, 1.04), (1.16, 1.36), .5, .02)
    for s in (-1, 1):
        for y in (-1.55, -.2, 1.15, 2.5):                                               # bolt-on plates
            armor.box((.06, 1.1, .34), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=.015, seg=1)
        _headlight(a, s * .75, -3.5, .86)
        steel.box((.14, .2, .12), loc=(s * .55, -3.56, .72), bevel=.02, seg=1)             # tow hooks
        steel.cyl(.1, .5, loc=(s * .55, 3.55, .95), rot=FORWARD, seg=10, bevel=.015, bseg=1)  # exhausts
        _taillight(a, s * 1.05, 3.5, 1.12)
        _hatch(a, s * .55, -1.85, 1.35, .26)                                               # driver hatches
        _periscopes(a, [(s * .55 + dx, -2.2, 1.35, 0) for dx in (-.12, .12)])
        _jerrycans(a, (s * .2, 3.565, .6), 1, bracket=False)                               # on the tail plate
    a.part('Jerrycan_rack', 'Steel').box((.78, .04, .05), loc=(0, 3.65, .86), bevel=0)
    for s in (-1, 1):  # tow cables along the roof edges, smoke dischargers at the front corners
        _cable(a, [(s * 1.12, -1.95, 1.385), (s * 1.12, .5, 1.385), (s * 1.1, 1.7, 1.385)])
        _smoke(a, steel, .98, -2.0, 1.43, s, count=3, gap=.08, r=.045, depth=.16)
    gy, gz, grot = _glacis((-3.5, 1.1), (-2.1, 1.36), .45, .015)
    for x in (-.8, -.4, 0, .4, .8):                                                      # spare track links
        deck.box((.34, .24, .05), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    deck.grille(1.5, .9, loc=(0, 2.4, 1.37), rot=(-R90, 0, 0), slats=7, depth=.08, thickness=.04)
    # Rear deck: a spare road wheel lying flat and a stowage bin.
    a.part('Tyres', 'Undercarriage').cyl(.26, .09, loc=(.8, 3.0, 1.395), seg=10, bevel=0)
    a.part('Wheels', 'Team').cyl(.19, .03, loc=(.8, 3.0, 1.445), seg=10, bevel=0)
    a.part('Hubs', 'Steel').cyl(.07, .03, loc=(.8, 3.0, 1.465), seg=6, bevel=0)
    _stowage_bin(a, (-.58, 3.0, 1.35), (.6, .36, .22), latch_side=0)
    steel.cyl(1.02, .1, loc=(0, -.3, 1.38), seg=24, bevel=.03)                          # turret ring
    _antenna(a, None, -1.0, 3.0, 1.36, 1.2)

    t = a.pivot('Turret', (0, -.3, 1.43))
    outline = [(-.5, -1.25), (.5, -1.25), (1.02, -.6), (1.08, .8), (.84, 1.08), (-.84, 1.08), (-1.08, .8),
               (-1.02, -.6)]
    a.part('Turret_body', 'Team', t).shell(outline, .72, .07, taper=.9, floor=.08, bevel=.02)
    a.part('Turret_floor', 'Undercarriage', t).prism([(x * .9, y * .9) for x, y in outline], .02, loc=(0, 0, .1),
                                                     axis='Z', bevel=0)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((.72, .4, .5), loc=(0, -1.3, .42), bevel=.04, taper=(.9, .9))              # mantlet
    tarm.box((1.3, .4, .36), loc=(0, 1.16, .36), bevel=.03)                             # rear stowage
    _roll(a, (0, 1.22, .64), 1.1, r=.12, parent=t)
    tsteel.box((.32, .8, .32), loc=(0, -.72, .44), bevel=.03)                           # breech
    tarm.box((1.3, .22, .4), loc=(0, .86, .31), bevel=.02, seg=1)                       # ready rack
    for x in (-.5, -.25, 0, .25, .5):
        tsteel.cyl(.05, .04, loc=(x, .74, .38), rot=FORWARD, seg=8, bevel=0)             # shell bases
    for s in (-1, 1):
        a.part('Seats', 'Canvas', t).box((.34, .34, .3), loc=(s * .55, .15, .27), bevel=.05)
    # Stowage bins bolted to the outside of both turret walls.
    for b0, b1 in (((1.02, -.6), (1.08, .8)), ((-1.08, .8), (-1.02, -.6))):
        m = _face_frame(b0, b1, .72, .9, u=.62, v=.42)
        _face_box(a, 'Turret_bins', 'Armor', m, (.82, .36, .16), parent=t)
        _face_box(a, 'Turret_bins', 'Armor', m, (.86, .05, .19), parent=t, bevel=0, lift=.19, sink=.02)
    tsteel.box((.2, .26, .2), loc=(-.46, -.95, .8), bevel=.03)                          # gun sight
    a.part('Sight', 'Glass', t).box((.14, .04, .1), loc=(-.46, -1.08, .8), bevel=.01, seg=1)
    tip = _barrel(a, t, start_y=-1.46, length=5.0, radius=.085, height=.44, brake=(.26, .32, .22),
                  sleeve=(.42, .5, .125), seg=12, style='baffle', bands=(.2, .72))
    a.pivot('Muzzle_main', tip, t)
    _roof_mg(a, t, (.93, .5, .72), length=.8, shield=False)


def heavy_tank(a):
    """Super-heavy tank: seven-wheel running gear under a deck as wide as the tracks, bolted
    four-panel skirts, reactive armour and a massive angular turret with a baffle-braked 152 mm gun,
    bustle basket, bins, tools and tow cables."""
    # Seven lean 8-sided road wheels and two idlers: the skirts and the wide deck hide nearly all of them.
    tracks(a, 1.32, 7.4, 1.0, .33, 7, .55, belt_width=.66, wheel_seg=8, lean=True, sprocket=0, cleat_pitch=.28)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.95, .6), (-4.15, 1.2), (4.1, 1.2), (4.1, .6)], 2.0, bevel=.05)       # belly
    front, back = (-4.28, 1.3), (-3.0, 1.68)
    hull.prism([(-4.2, 1.14), front, back, (3.9, 1.68), (4.24, 1.44), (4.24, 1.14)], 3.42, bevel=.07)
    for s in (-1, 1):
        _skirt(a, s, 1.8, -3.75, 3.81, .52, 1.36, 4, thick=.12, gap=.04)
        _headlight(a, s * 1.25, -4.26, 1.22)
        steel.box((.16, .2, .14), loc=(s * .7, -4.08, .82), bevel=.02, seg=1)             # tow hooks
        _taillight(a, s * 1.4, 4.24, 1.3)
        _exhaust(a, s * .62, 4.24, 1.29, .5, .18)
        deck.grille(1.0, .9, loc=(s * .68, 3.35, 1.69), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        _grille_frame(a, s * .68, 3.35, 1.67, 1.0, .9, t=.04)
        _stowage_bin(a, (s * 1.42, 3.35, 1.67), (.34, .9, .3), latch_side=s)
        _stowage_bin(a, (s * 1.38, -2.5, 1.67), (.46, .8, .3), latch_side=s)
        _cable(a, [(s * 1.58, -1.95, 1.705), (s * 1.58, .4, 1.705), (s * 1.56, 2.3, 1.705), (s * 1.45, 2.75, 1.705)])
    _shovel(a, (-.9, -1.95, 1.695), yaw=R90, length=1.1)
    _pick(a, (.6, -1.95, 1.7), yaw=R90, length=.95)
    for row, u in enumerate((.3, .74)):                                                   # reactive armour
        gy, gz, grot = _glacis(front, back, u, .035)
        for x in ((-1.2, -.4, .4, 1.2) if row else (-1.3, -.65, 0, .65, 1.3)):
            armor.box((.72 if row else .58, .44, .1), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    _hatch(a, 0, -2.72, 1.67, .3)                                                       # driver's hatch
    gy, gz, grot = _glacis(front, back, .96, .012)
    a.part('Vision_blocks', 'Glass').box((.5, .07, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    steel.cyl(1.25, .12, loc=(0, .45, 1.68), seg=24, bevel=.03)                          # turret ring

    t = a.pivot('Turret', (0, .45, 1.72))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.2, 1.5), (1.2, 1.5), (1.45, .9), (1.45, -.6), (.95, -1.5), (-.95, -1.5), (-1.45, -.6),
               (-1.45, .9)]
    turret.prism(outline, .9, loc=(0, 0, .45), axis='Z', bevel=.07, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):                                                                     # wedge cheeks
        tarm.prism([(s * .3, -1.3), (s * 1.44, -.5), (s * 1.44, -.95), (s * .34, -2.0)], .7, loc=(0, 0, .45),
                   axis='Z', bevel=.04, taper=.9)
        _stowage_bin(a, (s * 1.4, .55, .2), (.16, 1.2, .44), parent=t, latch_side=s)
        _smoke(a, tsteel, 1.16, -.2, .74, s, count=3, gap=.09, r=.05, depth=.16)
        _rail(a, [(s * 1.08, .2, .88), (s * 1.08, .2, .94), (s * 1.12, 1.1, .94), (s * 1.12, 1.1, .88)], parent=t)
    tarm.box((.56, .5, .6), loc=(0, -1.62, .44), bevel=.05, seg=1)                       # mantlet
    tarm.box((2.3, 1.0, .7), loc=(0, 1.9, .42), bevel=.05, seg=1, taper=(.92, .9))      # bustle
    _basket(a, -1.0, 1.0, 2.42, 2.82, .16, .34, parent=t)
    tsteel.cyl(.16, .3, loc=(-.62, .1, 1.0), seg=12, bevel=.02, bseg=1)                 # panoramic sight
    tsteel.box((.3, .3, .2), loc=(-.62, .1, 1.2), bevel=.04)
    a.part('Sight', 'Glass', t).box((.22, .04, .1), loc=(-.62, -.06, 1.21), bevel=.01, seg=1)
    tsteel.box((.36, .34, .24), loc=(.5, -.82, .98), bevel=.04)                         # gunner sight
    a.part('Sight', 'Glass', t).box((.26, .04, .12), loc=(.5, -1.0, 1.0), bevel=.01, seg=1)
    _hatch(a, -.62, .7, .89, .28, parent=t)                                             # commander's hatch
    _periscopes(a, [(-.62 + math.cos(ang) * .38, .7 + math.sin(ang) * .38, .88, ang + R90)
                    for ang in (-R90 + .9, R90, R90 + .8)], parent=t)
    _hatch(a, .55, 1.05, .89, .26, parent=t, hinge=-1)                                            # loader's hatch
    _antenna(a, t, -1.0, 1.35, .88, 1.4)
    _antenna(a, t, 1.0, 1.35, .88, 1.1)
    tip = _barrel(a, t, start_y=-1.85, length=4.2, radius=.15, height=.44, brake=(.46, .46, .4),
                  sleeve=(.42, .8, .22), seg=14, style='baffle', bands=(.2, .66))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .2, -1.8, .3, length=.4, housing=.26)
    _rws(a, t, (.55, .35, .9))


def sam_launcher(a):
    """Tracked surface-to-air missile launcher: two ribbed 4-cell missile boxes raised 35 degrees on a
    trainable launcher, a search radar panel spinning on its own mast beside the cab, five-panel
    skirts, fender stowage and rear bins, and a heavy machine gun on the driver's cab (Mount_mg)."""
    tracks(a, 1.18, 5.6, .8, .27, 6, .45, belt_width=.54, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    front, brow = (-3.1, .84), (-2.4, 1.3)
    hull.prism([(-3.05, .52), front, brow, (2.85, 1.3), (3.1, 1.08), (3.1, .52)], 2.34, bevel=.06)
    for s in (-1, 1):
        _skirt(a, s, 1.56, -2.5, 2.4, .57, .99, 5, thick=.08, bolts=False)
        _headlight(a, s * .75, -3.08, .68)
        steel.box((.14, .18, .12), loc=(s * .3, -3.12, .6), bevel=0)                       # tow hooks
        _taillight(a, s * .95, 3.1, .95)
        _exhaust(a, s * .45, 3.1, .78, .36, .2)
        _stowage_bin(a, (s * .82, 2.72, 1.29), (.5, .5, .32), latch_side=0)              # rear lockers
        _jerrycans(a, (s * 1.345, 1.9, .92), 3, bracket=False)
        gy, gz, grot = _glacis(front, brow, .5, 0)
        _track_links(a, _frame((s * .55, gy, gz), (grot, 0, 0)), 3, width=.46)
    _shovel(a, (-1.35, -1.3, .945), length=1.0)
    _cable(a, [(1.35, -2.4, .96), (1.35, .2, .96), (1.34, 1.35, .96)])
    deck.grille(.9, .6, loc=(-.45, -.95, 1.31), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
    _grille_frame(a, -.45, -.95, 1.29, .9, .6, t=.05)
    _stowage_bin(a, (.55, -.95, 1.29), (.6, .7, .24), latch_side=0)
    # Driver cab on the front left.
    armor.box((1.0, 1.1, .46), loc=(-.58, -1.9, 1.5), bevel=.05, taper=(.9, .8))
    a.part('Visor', 'Glass').box((.7, .04, .14), loc=(-.58, -2.39, 1.58), rot=(-.234, 0, 0), bevel=.01, seg=1)
    _hatch(a, -.58, -1.78, 1.72, .22)                                                    # cab hatch
    # Radar mast on the front right; the panel spins on its own pivot.
    armor.box((.62, .62, .32), loc=(.55, -2.0, 1.44), bevel=.04, taper=(.8, .8))
    steel.cyl(.13, 1.0, loc=(.55, -2.0, 1.95), seg=10, bevel=0)
    steel.cyl(.2, .12, loc=(.55, -2.0, 1.66), seg=10, bevel=.02, bseg=1)                   # mast collar
    steel.tube([(.37, -1.84, 1.58), (.44, -1.9, 2.3)], .025, seg=4)                        # radar cable
    r = a.pivot('Radar', (.55, -2.0, 2.45))
    rm = a.part('Radar_mast', 'Steel', r)
    rm.cyl(.15, .16, loc=(0, 0, .08), seg=12, bevel=.02, bseg=1)                         # bearing
    rm.box((.18, .3, .44), loc=(0, .08, .36), bevel=.03)                                  # yoke
    rot = (-.3, 0, 0)
    face = _frame((0, -.08, .66), rot)
    a.part('Radar_panel', 'Team', r).box((1.7, .14, .95), loc=face.to_translation(), rot=rot, bevel=.04)
    a.part('Radar_array', 'Armor', r).box((1.54, .04, .8), loc=face @ Vector((0, -.08, 0)), rot=rot, bevel=.01,
                                          seg=1)
    a.part('Radar_back', 'Armor', r).box((.5, .2, .42), loc=face @ Vector((0, .16, 0)), rot=rot, bevel=.03)
    for z in (-.27, -.09, .09, .27):                                                      # array ribs
        rm.box((1.5, .03, .04), loc=face @ Vector((0, -.105, z)), rot=rot, bevel=0)
    _antenna(a, None, -.95, 2.5, 1.3, 1.3)

    t = a.pivot('Turret', (0, 1.2, 1.3))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.0, .12, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                    # turntable
    tarm.box((1.5, 1.9, .5), loc=(0, .15, .36), bevel=.05, taper=(.9, .92))              # launcher base
    pitch, length, height, width = math.radians(35), 2.6, .86, .86
    hinge = Vector((0, .95, .72))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = hinge - turn @ Vector((0, length / 2, -height / 2))
    for s in (-1, 1):
        centre = mid + Vector((s * .56, 0, 0))
        box = _frame(centre, rot)
        a.part('Missile_box', 'Team', t).box((width, length, height), loc=centre, rot=rot, bevel=.05)
        frame = a.part('Box_frame', 'Armor', t)
        for y in (-length / 2 + .1, length / 2 - .12):
            frame.box((width + .05, .14, height + .05), loc=box @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
        # Raised top rail, lifting lugs and outer side ribs.
        frame.box((.1, length - .5, .05), loc=box @ Vector((s * .2, 0, height / 2 + .015)), rot=rot, bevel=0)
        for y in (-length / 2 + .1, length / 2 - .12):
            tsteel.box((.08, .08, .07), loc=box @ Vector((s * .34, y, height / 2 + .05)), rot=rot, bevel=0)
        for y in (-.55, 0, .55):
            frame.box((.05, .1, height - .1), loc=box @ Vector((s * (width / 2 + .015), y, 0)), rot=rot, bevel=0)
        for cx in (-.2, .2):
            for cz in (-.2, .2):
                _tube_mouth(a, t, box @ _frame((cx, -length / 2, cz), FORWARD), .16, protrude=.06, seg=10)
        tarm.box((.14, .46, .5), loc=(s * 1.07, .95, .68), bevel=.02, seg=1)             # hinge cheeks
        tsteel.limb((s * .56, -.55, .5), tuple(box @ Vector((0, -.25, -height / 2 + .02))), .12, .12, bevel=.02)
    spine = _frame(mid, rot)
    tsteel.box((.24, length * .9, .24), loc=spine @ Vector((0, 0, -.22)), rot=rot, bevel=.03)  # cradle
    tsteel.cyl(.11, 2.2, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)             # elevation hinge
    a.pivot('Muzzle_main', tuple(spine @ Vector((0, -length / 2 - .06, 0))), t)
    # Second weapon: a heavy machine gun on the driver's cab roof in front of the hatch (Mount_mg /
    # Muzzle_mg), low and far ahead of the missile boxes' swing; its 0.8 m barrel stops short of the
    # radar mast when it swings right.
    wpn.hmg(a, (-.58, -2.18, 1.73), post=.16, length=.8, ammo=-1)


def mortar_carrier(a):
    """Boxy tracked carrier (M113 lineage) with a 120 mm mortar firing through the open roof hatch:
    headlight clusters in brush guards, side bins and jerrycans, a front-right engine grille, roof
    stowage and a door in the rear ramp."""
    tracks(a, 1.08, 4.4, .72, .25, 5, .42, belt_width=.5, wheel_seg=12, lean=True, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.25, .44), (-2.42, .95), (2.38, .95), (2.38, .44)], 1.7, bevel=.05)        # belly
    nose, brow = (-2.56, 1.22), (-1.95, 1.84)
    hull.prism([(-2.46, .88), nose, brow, (2.45, 1.84), (2.45, .88)], 2.64, bevel=.06)
    gy, gz, grot = _glacis(nose, brow, .42, .02)
    armor.box((1.8, .5, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.015, seg=1)      # trim vane
    for s in (-1, 1):
        _headlight(a, s * 1.08, -2.2, 1.7)                                                 # on brackets
        steel.box((.12, .2, .12), loc=(s * .6, -2.5, .95), bevel=.02, seg=1)              # tow hooks
        _taillight(a, s * 1.12, 2.45, 1.62)
        for y in (1.75, 2.1):
            a.part('Jerrycans', 'Hazard').box((.16, .3, .4), loc=(s * 1.41, y, 1.3), bevel=.03)
        steel.box((.1, .12, .08), loc=(s * .8, 2.5, 1.7), bevel=.01, seg=1)              # ramp hinges
        # Side stowage: a bin on the front half, a bolted strip along the top edge, a lip over the tracks.
        _stowage_bin(a, (s * 1.39, -.85, 1.27), (.16, 1.1, .38), latch_side=s)
        armor.box((.03, 4.3, .06), loc=(s * 1.335, .0, 1.76), bevel=0)
        armor.box((.12, 4.3, .05), loc=(s * 1.34, -.05, .895), bevel=0)
        _rail(a, [(s * 1.18, -1.8, 1.83), (s * 1.18, -1.8, 1.9), (s * 1.18, -.9, 1.9), (s * 1.18, -.9, 1.83)])
    armor.box((1.9, .06, .96), loc=(0, 2.46, 1.3), bevel=.02, seg=1)                     # rear ramp
    armor.box((.7, .03, .72), loc=(.4, 2.505, 1.3), bevel=0)                             # door in the ramp
    steel.box((.05, .05, .2), loc=(.12, 2.535, 1.32), bevel=0)
    # Driver hatch and vision blocks, commander's cupola with the pintle gun, engine grille.
    _hatch(a, -.6, -1.55, 1.83, .28)
    for dx in (-.16, 0, .16):
        a.part('Vision_blocks', 'Glass').box((.12, .06, .07), loc=(-.6 + dx, -1.92, 1.87), bevel=.01, seg=1)
    armor.cyl(.34, .22, loc=(.6, -1.05, 1.93), seg=14, bevel=.03)
    glass = a.part('Periscopes', 'Glass')
    for k in range(5):
        ang = -R90 + (k - 2) * .6
        glass.box((.1, .05, .07), loc=(.6 + math.cos(ang) * .34, -1.05 + math.sin(ang) * .34, 1.98),
                  rot=(0, 0, ang + R90), bevel=0)
    dark.grille(.7, .4, loc=(.6, -1.68, 1.85), rot=(-R90, 0, 0), slats=4, depth=.06, thickness=.04)
    _grille_frame(a, .6, -1.68, 1.83, .7, .4, t=.05)
    _roof_mg(a, None, (.6, -1.05, 2.04), length=.9)
    _antenna(a, None, -1.1, 2.2, 1.84, 1.3)
    # Roof stowage: a rolled camouflage net at the back, ammunition boxes in front of the hatch.
    _roll(a, (0, 2.2, 1.95), 1.5, r=.12)
    for x in (-.5, .5):
        a.part('Ammo_boxes', 'Crate').box((.4, .28, .24), loc=(x, -.45, 1.94), bevel=.02, seg=1)
    # Open mortar hatch: raised coaming around a dark well, both leaves folded up and out.
    hy = .8
    armor.shell(chamfered(1.5, 1.9, .22), .15, .07, loc=(0, hy, 1.82), bevel=.015)
    dark.prism(chamfered(1.38, 1.78, .19), .02, loc=(0, hy, 1.86), axis='Z', bevel=0)
    lean = math.radians(28)
    for s in (-1, 1):
        hull.box((.06, 1.8, .74), loc=(s * (.8 + .37 * math.sin(lean)), hy, 1.97 + .37 * math.cos(lean)),
                 rot=(0, s * lean, 0), bevel=.02, seg=1)
        steel.box((.1, .16, .08), loc=(s * .79, hy - .6, 1.98), bevel=.01, seg=1)          # leaf hinges
        steel.box((.1, .16, .08), loc=(s * .79, hy + .6, 1.98), bevel=.01, seg=1)

    t = a.pivot('Turret', (0, .9, 1.87))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.56, .06, loc=(0, 0, .04), seg=18, bevel=.015, bseg=1)                   # turntable
    tarm.box((.56, .52, .28), loc=(0, .36, .2), bevel=.04)                              # breech mount
    pitch, length = math.radians(55), 1.9
    rot = (R90 - pitch, 0, 0)
    d = Vector((0, -math.cos(pitch), math.sin(pitch)))
    base = Vector((0, .4, .3))
    tube = a.part('Mortar_tube', 'Steel', t)
    tube.cyl(.1, length, loc=base + d * (length / 2), rot=rot, seg=14, bevel=.015, bseg=1)
    tube.cyl(.15, .3, loc=base + d * .12, rot=rot, seg=14, bevel=.04)                    # breech cap
    tube.cyl(.13, .14, loc=base + d * (length - .1), rot=rot, seg=14, bevel=.02)         # blast ring
    collar = base + d * 1.0
    tarm.cyl(.15, .3, loc=collar, rot=rot, seg=12, bevel=.03)                            # recoil collar
    for s in (-1, 1):
        tsteel.limb(tuple(collar + Vector((s * .1, 0, -.06))), (s * .45, -.3, .08), .06, .06, bevel=0)  # bipod
    tsteel.limb((0, -.05, .07), tuple(collar + Vector((0, .05, -.14))), .07, .07, bevel=0)  # elevation screw
    tarm.box((.16, .2, .16), loc=(-.24, -.1, .72), bevel=.02, seg=1)                     # sight
    a.part('Sight', 'Glass', t).box((.1, .04, .08), loc=(-.24, -.21, .74), bevel=.01, seg=1)
    tsteel.limb((-.24, -.1, .64), tuple(collar + Vector((-.1, 0, 0))), .04, .04, bevel=0)
    a.pivot('Muzzle_main', tuple(base + d * length), t)


def rocket_technical(a):
    """Civilian pickup turned rocket artillery: team paint over a tired body, canvas and rust, a bull
    bar, a spare tyre on the cab roof, reload crates in the bed, a twelve-tube rocket launcher on a
    turntable and a pintle machine gun on the cab roof (Mount_mg)."""
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    chassis = a.part('Chassis', 'Undercarriage')
    rust = a.part('Rust', 'Roof')
    chassis.box((1.24, 4.6, .22), loc=(0, .05, .56), bevel=.04)                           # ladder frame
    for sx in (-1, 1):
        for y in (-1.6, 1.5):
            a.part('Tyres', 'Rubber').cyl(.4, .3, loc=(sx * .8, y, .4), rot=ACROSS, seg=16, bevel=.06, bseg=1)
            a.part('Wheels', 'Armor').cyl(.22, .33, loc=(sx * .8, y, .4), rot=ACROSS, seg=10, bevel=.02, bseg=1)
            steel.cyl(.08, .36, loc=(sx * .8, y, .4), rot=ACROSS, seg=6, bevel=0)
            chassis.tube([(sx * .93, y + .5 * math.cos(u), .4 + .5 * math.sin(u))
                          for u in (i * math.pi / 6 for i in range(7))], .045, seg=6)       # arch flares
    body.prism([(-2.5, .7), (-2.58, 1.0), (-2.48, 1.14), (-1.3, 1.22), (-.74, 1.76), (.28, 1.8), (.36, 1.76),
                (.36, .7)], 1.78, bevel=.06)
    body.shell(chamfered(1.78, 2.1, .05), .46, .06, loc=(0, 1.5, .72), floor=.08, bevel=.02)  # bed
    glass = a.part('Windows', 'Glass')
    glass.box((1.5, .03, .64), loc=(0, -1.03, 1.5), rot=(-.804, 0, 0), bevel=.01, seg=1)
    glass.box((1.2, .02, .3), loc=(0, .38, 1.52), bevel=.005, seg=1)
    for s in (-1, 1):
        glass.box((.02, .76, .36), loc=(s * .91, -.24, 1.5), bevel=.005, seg=1)
        a.part('Lamps', 'Lamp').box((.26, .06, .1), loc=(s * .62, -2.57, .98), bevel=.01, seg=1)
        a.part('Tail_lights', 'Alloy').box((.1, .06, .16), loc=(s * .8, 2.56, 1.02), bevel=.01, seg=1)
        steel.box((.05, .1, .14), loc=(s * .98, -.78, 1.42), bevel=.01, seg=1)            # mirrors
        for y in (-1.0, .26):                                                            # door shut lines
            a.part('Trim', 'Armor').box((.03, .03, .78), loc=(s * .895, y, 1.12), bevel=0)
        steel.box((.03, .12, .04), loc=(s * .9, .1, 1.24), bevel=0)                       # door handles
    chassis.grille(1.0, .22, loc=(0, -2.57, .86), slats=3, depth=.05, thickness=.04)
    rust.box((1.84, .16, .16), loc=(0, -2.62, .66), bevel=.03)                            # bumpers
    rust.box((1.84, .14, .14), loc=(0, 2.62, .64), bevel=.03)
    rust.box((.9, .02, .22), loc=(-.25, 2.57, .98), bevel=0)                              # tailgate rust
    rust.box((.02, .5, .26), loc=(-.9, -1.9, .92), bevel=0)                               # wing rust
    steel.box((.3, .04, .05), loc=(.3, 2.6, 1.08), bevel=0)                                # tailgate handle
    _rail(a, [(-.7, -2.66, .75), (-.7, -2.72, .85), (-.7, -2.72, 1.12), (.7, -2.72, 1.12), (.7, -2.72, .85),
              (.7, -2.66, .75)], r=.03)                                                   # bull bar
    _rail(a, [(-.7, -2.72, .97), (.7, -2.72, .97)], r=.025)
    # Spare tyre on a roof rack, reload crates in the bed.
    _rail(a, [(-.55, -.7, 1.8), (-.55, -.7, 1.86), (-.55, -.14, 1.86), (.55, -.14, 1.86), (.55, -.7, 1.86),
              (.55, -.7, 1.8)], r=.02)
    a.part('Tyres', 'Rubber').cyl(.29, .18, loc=(0, -.42, 1.9), seg=14, bevel=.05, bseg=1)
    a.part('Wheels', 'Armor').cyl(.15, .04, loc=(0, -.42, 1.99), seg=10, bevel=0)
    for y in (1.95, 2.3):
        a.part('Crates', 'Crate').box((.24, .3, .22), loc=(.66, y, .9), bevel=.02, seg=1)
    steel.tube([(-.82, .56, 1.18), (-.82, .56, 1.98), (.82, .56, 1.98), (.82, .56, 1.18)], .045, seg=8)  # roll bar
    for x in (-.4, 0, .4):
        a.part('Lamps', 'Lamp').box((.16, .08, .08), loc=(x, .5, 2.06), bevel=.01, seg=1)
    a.part('Tarp', 'Canvas').cyl(.13, 1.5, loc=(0, .05, 1.93), rot=ACROSS, seg=10, bevel=.04)
    a.part('Crates', 'Crate').box((.42, .32, .3), loc=(.55, .72, .96), bevel=.03)
    a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(-.55, .66, 1.01), bevel=.03)
    a.part('Jerrycans', 'Hazard').box((.3, .16, .4), loc=(-.55, .85, 1.01), bevel=.03)
    _antenna(a, None, .7, .15, 1.79, 1.4)

    t = a.pivot('Turret', (0, 1.62, .81))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.46, .07, loc=(0, 0, .045), seg=16, bevel=.015, bseg=1)                  # turntable
    tarm.box((.36, .36, .5), loc=(0, 0, .32), bevel=.03)                                # pedestal
    tarm.box((1.14, .3, .12), loc=(0, -.1, .6), bevel=.02, seg=1)                       # yoke bar
    tarm.box((.2, .16, .14), loc=(-.54, .12, 1.09), bevel=.02, seg=1)                   # firing box
    tsteel.tube([(-.54, .2, 1.05), (-.3, .25, .7), (-.1, .12, .5)], .02, seg=4)           # firing cable
    for s in (-1, 1):
        tarm.box((.08, .44, .44), loc=(s * .54, -.1, .82), bevel=.02, seg=1)             # yoke arms
    pitch, length = .22, 1.5
    rot = (-pitch, 0, 0)
    centre = Vector((0, -.1, .92))
    pod = _frame(centre, rot)
    tsteel.cyl(.06, 1.2, loc=centre, rot=ACROSS, seg=8, bevel=0)                        # trunnion
    tubes = a.part('Rocket_tubes', 'Armor', t)
    for row in (-.2, 0, .2):
        for col in (-.3, -.1, .1, .3):
            tubes.cyl(.085, length, loc=pod @ Vector((col, 0, row)), rot=(R90 - pitch, 0, 0), seg=10, bevel=.01,
                      bseg=1)
            _tube_mouth(a, t, pod @ _frame((col, -length / 2, row), FORWARD), .085, protrude=.03, seg=10)
    for y in (-length / 2 + .22, length / 2 - .2):
        a.part('Pod_bands', 'Team', t).box((.88, .1, .68), loc=pod @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
    a.pivot('Muzzle_main', tuple(pod @ Vector((0, -length / 2 - .03, 0))), t)
    # Second weapon: a pintle machine gun on the right of the cab roof beside the spare-tyre rack, firing
    # over the bonnet (Mount_mg / Muzzle_mg), high enough to turn over the tarp roll and the light bar.
    wpn.hmg(a, (.72, -.42, 1.772), post=.3, ammo=-1)


# name: (builder, Asset options). Vehicles use tight contact AO like 3d_astra's units.
BUILDERS = {
    'scout_jeep': (scout_jeep, dict(ao_distance=.5, grime_height=.45)),
    'light_tank': (light_tank, dict(ao_distance=.55, grime_height=.5)),
    'main_battle_tank': (main_battle_tank, dict(ao_distance=.6, grime_height=.55)),
    'artillery': (artillery, dict(ao_distance=.6, grime_height=.55)),
    'apc': (apc, dict(ao_distance=.6, grime_height=.55)),
    'mlrs': (mlrs, dict(ao_distance=.6, grime_height=.55)),
    'aa_vehicle': (aa_vehicle, dict(ao_distance=.55, grime_height=.5)),
    'flame_tank': (flame_tank, dict(ao_distance=.55, grime_height=.5)),
    'armored_car': (armored_car, dict(ao_distance=.6, grime_height=.55)),
    'tank_destroyer': (tank_destroyer, dict(ao_distance=.6, grime_height=.55)),
    'heavy_tank': (heavy_tank, dict(ao_distance=.65, grime_height=.6)),
    'sam_launcher': (sam_launcher, dict(ao_distance=.6, grime_height=.55)),
    'mortar_carrier': (mortar_carrier, dict(ao_distance=.55, grime_height=.5)),
    'rocket_technical': (rocket_technical, dict(ao_distance=.5, grime_height=.45)),
}
