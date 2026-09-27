"""Machine Brigade elite units: refurbished, up-armoured versions of existing vehicles.

Each elite calls its base model's builder unchanged, bolts the upgrades on in the base model's own
coordinates, repaints every `Armor` part in `EliteBlack` and finally scales the whole asset (meshes
and pivots) up uniformly: 1.15x for ground vehicles, 1.1x for the helicopter. So every rig name and
pivot of the base model survives with the same hierarchy (`Turret`, `Mount_*`, `Muzzle_*`,
`Main_cannon*`, `Rotor`, `Radar` ...) and the muzzles scale with the model. Where a weapon changes
(the APC's bigger autocannon, the helicopter's bigger rocket pods, the MLRS twin pod) the base parts
are dropped and rebuilt under the same names and slots, and the muzzle empty moves to the new opening.

Elite look, shared by every model: `Team` paint stays on the main hull panels (the unit still reads
as its army's colour), dark `EliteBlack` armour everywhere else, reactive armour, cage armour and
applique plates, `Gilded` chevrons and a crest plate, red `EliteGlow` sensor lights and visor slits,
a roof active-protection sensor ring, a commander's sight, extra smoke launchers and antennas.

Conventions are mb_vehicles.py's and mb_air.py's: metres, +Z up, Blender -Y is the front, origin on
the ground at the footprint centre. Touching parts overlap or stand at least 1 cm apart, never face
to face (coplanar faces z-fight). New part names never start with a runtime pattern (Turret,
Main_cannon, Muzzle, Mount_, Radar, Rotor ...) unless they belong to that rig: the gold barrel bands
are `Main_cannon*_gilt` so they recoil with the gun.
"""
import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

import mb_air as air
import mb_vehicles as veh
from mb_vehicles import ACROSS, FORWARD, R90, _face_frame, _flank, _frame, _glacis

ANY = object()  # _drop / _recolour filter: any parent


# ----------------------------------------------------------------------------- asset surgery
def _keys(a, names=None, mats=None, parent=ANY):
    return [k for k in a.order if (names is None or k[0] in names) and (mats is None or k[1] in mats)
            and (parent is ANY or k[2] == parent)]


def _drop(a, names, mats=None, parent=ANY):
    """Remove base parts (a weapon that is rebuilt bigger)."""
    for key in _keys(a, names, mats, parent):
        a.shapes.pop(key).bm.free()
        a.order.remove(key)


def _merge(dst, src):
    me = bpy.data.meshes.new('_elite_merge')
    src.bm.to_mesh(me)
    src.bm.free()
    dst.bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def _recolour(a, mapping, names=None, parent=ANY):
    """Swap materials {old: new} on every part (or only the named parts); parts that end up with the
    same (name, material, parent) are merged into one mesh."""
    order, shapes = [], {}
    for key in a.order:
        name, mat, par = key
        hit = (names is None or name in names) and (parent is ANY or par == parent)
        new = (name, mapping.get(mat, mat) if hit else mat, par)
        if new in shapes:
            _merge(shapes[new], a.shapes[key])
        else:
            shapes[new] = a.shapes[key]
            order.append(new)
    a.shapes, a.order = shapes, order


def _scale(a, k):
    """Uniform scale about the origin: part vertices are relative to their pivot and pivots only
    translate, so scaling both keeps every world position scaled by k."""
    for shape in a.shapes.values():
        bmesh.ops.scale(shape.bm, vec=(k, k, k), verts=list(shape.bm.verts))
    for o in a.pivots.values():
        o.location = o.location * k
    a.ao_distance *= k
    a.grime_height *= k


def elite(base, upgrade, scale=1.15):
    def build(a):
        base(a)
        upgrade(a)
        _recolour(a, {'Armor': 'EliteBlack'})
        _scale(a, scale)
    build.__doc__ = upgrade.__doc__
    return build


# ----------------------------------------------------------------------------- elite kit
def _onto(origin, normal, up):
    """Frame at origin: local Z along normal, local Y along `up` (made perpendicular), X = Y x Z."""
    z = Vector(normal).normalized()
    u = Vector(up)
    y = (u - z * u.dot(z)).normalized()
    x = y.cross(z)
    o = Vector(origin)
    return Matrix(((x.x, y.x, z.x, o.x), (x.y, y.y, z.y, o.y), (x.z, y.z, z.z, o.z), (0, 0, 0, 1)))


def _plate(part, m, size, sink=.01, bevel=.015, seg=1, off=(0, 0)):
    """Box lying on the plane of frame m: size (local X, local Y, thickness out along Z), its back
    sunk `sink` into the surface, centred at local (off[0], off[1])."""
    w, h, t = size
    part.box((w, h, t), loc=m @ Vector((off[0], off[1], t / 2 - sink)), rot=m.to_euler('XYZ'), bevel=bevel, seg=seg)


def _chevron(part, m, w, h, t, depth=.02, lift=0.0, z=0.0):
    """Chevron pointing along local +Y of frame m, `w` across, `h` tall with arms `t` thick, standing
    from local z up by `depth`."""
    prof = [(-w / 2, lift), (0, lift + h), (w / 2, lift), (w / 2, lift - t), (0, lift + h - t), (-w / 2, lift - t)]
    part.prism(prof, depth, loc=m @ Vector((0, 0, z + depth / 2)), rot=m.to_euler('XYZ'), axis='Z', bevel=0)


def _chevrons(a, m, w=.36, h=.14, t=.06, gap=.1, count=2, parent=None, depth=.02, sink=.008):
    """Row of `count` gold chevrons on frame m (pointing along local +Y)."""
    part = a.part('Chevrons', 'Gilded', parent)
    for i in range(count):
        _chevron(part, m, w, h, t, depth=depth, lift=(i - (count - 1) / 2) * gap - h / 2, z=-sink)


def _crest(a, m, w=.34, h=.3, parent=None):
    """Elite insignia plate on frame m (local Y up the plate): a dark shield on a gold rim carrying a
    gold double chevron."""
    shield = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h * .12), (0, -h / 2), (-w / 2, -h * .12)]
    rot = m.to_euler('XYZ')
    rim = [(x * 1.16, y * 1.16 - .004) for x, y in shield]
    a.part('Crest_rim', 'Gilded', parent).prism(rim, .03, loc=m @ Vector((0, 0, .003)), rot=rot, axis='Z', bevel=0)
    a.part('Crest', 'EliteBlack', parent).prism(shield, .03, loc=m @ Vector((0, 0, .017)), rot=rot, axis='Z', bevel=0)
    part = a.part('Chevrons', 'Gilded', parent)
    for i, lift in enumerate((h * .02, -h * .22)):
        _chevron(part, m, w * .7, h * .22, h * .09, depth=.02, lift=lift, z=.025)


def _aps(a, loc, r=.14, parent=None, heads=4, yaw=0.0, post=.12):
    """Roof active-protection sensor ring: a post carrying a dark octagonal hub girdled by a red
    glowing sensor band, a cap, and `heads` radar heads with glass faces around it. loc is the roof
    point under the post; the top is post + 0.17 m above it."""
    x, y, z = loc
    hz = z + post + .055                                                               # hub centre
    blk = a.part('APS', 'EliteBlack', parent)
    a.part('APS_post', 'Steel', parent).cyl(r * .4, post + .02, loc=(x, y, z + post / 2 - .01), seg=8, bevel=0)
    blk.cyl(r, .13, loc=(x, y, hz), seg=8, bevel=.015, bseg=1)
    a.part('APS_glow', 'EliteGlow', parent).cyl(r + .014, .035, loc=(x, y, hz - .005), seg=8, bevel=0)
    blk.cyl(r * .55, .06, loc=(x, y, hz + .085), seg=8, bevel=0)
    glass = a.part('APS_sensors', 'Glass', parent)
    for k in range(heads):
        ang = yaw + math.pi / 8 + k * math.tau / heads
        d = Vector((math.cos(ang), math.sin(ang), 0))
        c = Vector((x, y, hz)) + d * (r + .02)
        rot = (0, 0, ang + R90)
        blk.box((.13, .07, .1), loc=tuple(c), rot=rot, bevel=0)
        glass.box((.1, .02, .07), loc=tuple(c + d * .04), rot=rot, bevel=0)


def _cdr_sight(a, loc, parent=None, yaw=0.0, post=.16, size=(.3, .26, .18)):
    """Commander's independent panoramic sight on a post: dark head with a glass window and a red
    laser-rangefinder eye. loc is the roof point under the post."""
    x, y, z = loc
    w, d, h = size
    a.part('Cdr_sight_post', 'Steel', parent).cyl(.06, post + .03, loc=(x, y, z + post / 2 - .005), seg=8, bevel=0)
    m = _frame((x, y, z + post + h / 2 - .02), (0, 0, yaw))
    rot = (0, 0, yaw)
    head = a.part('Cdr_sight', 'EliteBlack', parent)
    head.box(size, loc=m.to_translation(), rot=rot, bevel=.03, seg=1)
    head.box((w * .9, d * .5, .04), loc=m @ Vector((0, .02, h / 2 + .005)), rot=rot, bevel=0)           # hood
    a.part('Cdr_sight_glass', 'Glass', parent).box((w * .5, .03, h * .45),
                                                   loc=m @ Vector((-w * .12, -d / 2 - .002, .01)), rot=rot, bevel=0)
    a.part('Elite_glow', 'EliteGlow', parent).box((w * .16, .03, h * .3), loc=m @ Vector((w * .3, -d / 2 - .002, .01)),
                                                  rot=rot, bevel=0)


def _smoke_bank(a, loc, s, count=4, pitch=.11, r=.045, depth=.15, parent=None, yaw=0.0):
    """Bank of smoke dischargers on a dark mount block standing on loc (x, y, z of the surface),
    `count` tubes along the block (local Y), angled up and out to side s."""
    x, y, z = loc
    m = _frame((x, y, z), (0, 0, yaw))
    length = pitch * count + .05
    a.part('Smoke_mount', 'EliteBlack', parent).box((.16, length, .1), loc=m @ Vector((0, 0, .03)), rot=(0, 0, yaw),
                                                    bevel=.012, seg=1)
    tubes = a.part('Smoke_tubes', 'Steel', parent)
    for i in range(count):
        p = m @ Vector((s * .015, (i - (count - 1) / 2) * pitch, .1))
        tubes.cyl(r, depth, loc=tuple(p), rot=(.3, s * .7, yaw), seg=6, bevel=0)


def _whip(a, loc, h, parent=None, tip='EliteGlow'):
    """Whip antenna on a dark base with a glowing tip. loc is the surface point under it."""
    x, y, z = loc
    a.part('Antenna_base', 'EliteBlack', parent).box((.09, .09, .08), loc=(x, y, z + .02), bevel=0)
    a.part('Antenna', 'Steel', parent).cyl(.012, h, loc=(x, y, z + h / 2), seg=5, bevel=0)
    a.part('Antenna_tips', tip, parent).cyl(.028, .07, loc=(x, y, z + h + .02), seg=6, bevel=0)


def _era_on(a, m, cols, rows, size, gap=.04, parent=None, bevel=0.0):
    """Reactive armour grid on frame m (local Z out of the surface), blocks sunk 1 cm."""
    w, d, t = size
    part = a.part('ERA', 'EliteBlack', parent)
    for i in range(cols):
        for j in range(rows):
            _plate(part, m, size, off=((i - (cols - 1) / 2) * (w + gap), (j - (rows - 1) / 2) * (d + gap)),
                   bevel=bevel)


def _slat_cage(a, loc, length, height, s, bars=5, parent=None, bar=.04, brackets=(), bracket_z=None, reach=.22):
    """Cage (slat) armour on side s running along Y: horizontal bars between posts, standing at
    loc = (x, y centre, z centre), with brackets reaching `reach` inwards at the given y."""
    x, y, z = loc
    veh._slats(a, _frame((x, y, z), (0, 0, R90)), length, height, bars, parent=parent, bar=bar)
    for by in brackets:
        a.part('Slat_brackets', 'EliteBlack', parent).box((reach, .05, .05), loc=(x - s * reach / 2, by, bracket_z),
                                                          bevel=0)


def _gilt_band(a, parent, suffix, at, r, width=.07, seg=14, rot=FORWARD):
    """Gold band around a barrel (recoils with it: Main_cannon<suffix>_gilt)."""
    a.part(f'Main_cannon{suffix}_gilt', 'Gilded', parent).cyl(r, width, loc=at, rot=rot, seg=seg, bevel=0)


def _glow_glass(a, names, parent=ANY):
    """Turn glass sights / vision blocks into red glowing sensor eyes and visor slits."""
    _recolour(a, {'Glass': 'EliteGlow'}, names=set(names), parent=parent)


# ----------------------------------------------------------------------------- main battle tank
def _mbt(a):
    """Elite main battle tank: reactive armour on the front skirt panels and a second glacis row,
    bolted applique plates on the turret flanks, cage armour over the rear run of the tracks, a
    commander's panoramic sight, a roof active-protection ring, extra smoke banks and antennas, gold
    chevrons, crests on the bustle bins and a gold band on the gun; the driver's vision blocks and the
    gunner's sight glow red."""
    t = 'Turret'
    # Skirts: panels of 0.98 m from y = -2.75, outer face at |x| 1.68, lip from z 1.24.
    for s in (-1, 1):
        for yc in (-2.259, -1.242):
            _era_on(a, _onto((s * 1.68, yc, .98), (s, 0, 0), (0, 0, 1)), 2, 2, (.42, .2, .07), gap=.05)
        _chevrons(a, _onto((s * 1.68, .79, 1.0), (s, 0, 0), (0, -1, 0)), w=.4, h=.16, t=.07, gap=.14, parent=None)
        # Cage armour over the exposed rear run of the track, bracketed off the fender.
        _slat_cage(a, (s * 1.73, 2.68, 1.0), .66, .56, s, bars=5, brackets=(2.45, 2.9), bracket_z=1.06, reach=.75)
    # Second row of reactive armour low on the glacis.
    gy, gz, grot = _glacis((-3.0, .86), (-2.1, 1.38), .17, .03)
    for x in (-1.1, -.55, 0, .55, 1.1):
        a.part('ERA', 'EliteBlack').box((.5, .3, .1), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.015, seg=1)
    # Turret: bolted applique plates on the front flanks, crests on the bustle bins.
    steel = a.part('Elite_bolts', 'Steel', t)
    for s, (b0, b1) in ((1, ((.95, -.72), (1.12, .25))), (-1, ((-1.12, .25), (-.95, -.72)))):
        m = _face_frame(b0, b1, .66, .9, u=.62 if s > 0 else .38, v=.5)
        _plate(a.part('Elite_plates', 'EliteBlack', t), m, (.56, .38, .07), bevel=.015)
        for dx in (-.22, .22):
            for dy in (-.13, .13):
                steel.cyl(.022, .03, loc=m @ Vector((dx, dy, .065)), rot=m.to_euler('XYZ'), seg=6, bevel=0)
        _crest(a, _onto((s * .972, 1.35, .22), (s, 0, 0), (0, 0, 1)), w=.24, h=.2, parent=t)
    # Roof: gold chevrons pointing forward, commander's sight, APS ring, smoke banks, antenna.
    _chevrons(a, _onto((.12, -.78, .66), (0, 0, 1), (0, -1, 0)), w=.46, h=.16, t=.07, gap=.14, parent=t)
    _cdr_sight(a, (.16, -.4, .66), parent=t, yaw=-.25)
    _aps(a, (-.25, .78, .66), parent=t)
    for s in (-1, 1):
        _smoke_bank(a, (s * .9, .55, .64), s, count=4, parent=t, yaw=s * -.2)
    _whip(a, (.7, .9, .66), 1.5, parent=t)
    # Gun: gold band short of the muzzle collar.
    _gilt_band(a, t, '', (0, -1.38 - 2.8, .33), .124)
    _glow_glass(a, ('Periscope',), parent=None)
    _glow_glass(a, ('Sight',), parent=t)


# ----------------------------------------------------------------------------- heavy tank
def _heavy(a):
    """Elite super-heavy tank: reactive armour on the front skirt panels and the wedge-cheek faces,
    gold trims along the cheek tops, applique plates along the exposed hull sides, crests on the turret
    bins, gold chevrons on the skirts and roof, a low APS ring clear of the remote weapon station, smoke
    banks on the bustle, a third antenna and a gold band on the gun; the driver's visor and both sights
    glow red."""
    t = 'Turret'
    # Skirts: 1.86 m panels (centres -2.82, -.92, .98, 2.88), outer face |x| 1.86, lip from z 1.32,
    # bolts at z .62.
    plates = a.part('Elite_plates', 'EliteBlack')
    for s in (-1, 1):
        for yc in (-2.82, -.92):
            _era_on(a, _onto((s * 1.86, yc, .98), (s, 0, 0), (0, 0, 1)), 3, 2, (.5, .26, .08), gap=.08)
        _chevrons(a, _onto((s * 1.86, .98, .98), (s, 0, 0), (0, -1, 0)), w=.46, h=.2, t=.08, gap=.17)
        # Hull side above the skirts: |x| 1.71 from the lip (z 1.37) to the deck edge bevel (z 1.61).
        for yc in (-2.45, -.8, .85, 2.5):
            _plate(plates, _onto((s * 1.71, yc, 1.5), (s, 0, 0), (0, 0, 1)), (1.5, .2, .06), bevel=0)
    # Turret: reactive armour on the wedge-cheek faces, gold trims along their top edges, crests on the bins.
    tgilt = a.part('Gilt_trims', 'Gilded', t)
    for s in (-1, 1):
        b0, b1 = ((.34, -2.0), (1.44, -.95)) if s > 0 else ((-1.44, -.95), (-.34, -2.0))
        _era_on(a, _face_frame(b0, b1, .7, .9, z0=.1, u=.5, v=.45), 3, 2, (.4, .26, .09), gap=.04, parent=t)
        p0, p1 = Vector((s * .306, -1.8, .8)), Vector((s * 1.296, -.855, .8))
        mid = (p0 + p1) / 2 + Vector((-s * .69, .723, 0)) * .06
        tgilt.box(((p1 - p0).length, .07, .03), loc=tuple(mid), rot=(0, 0, math.atan2(p1.y - p0.y, p1.x - p0.x)),
                  bevel=0)
        _crest(a, _onto((s * 1.482, .55, .36), (s, 0, 0), (0, 0, 1)), w=.3, h=.24, parent=t)
    # Roof and bustle: chevrons, APS ring (low: the RWS gun sweeps over it), smoke banks, antenna.
    _chevrons(a, _onto((0, -1.0, .9), (0, 0, 1), (0, -1, 0)), w=.5, h=.18, t=.08, gap=.16, parent=t)
    _aps(a, (0, 1.15, .9), parent=t, post=.02)
    for s in (-1, 1):
        _smoke_bank(a, (s * .9, 1.95, .77), s, count=4, parent=t)
    _whip(a, (-.5, 2.2, .77), 1.2, parent=t)
    _gilt_band(a, t, '', (0, -1.85 - 3.9, .44), .168, width=.08)
    _glow_glass(a, ('Vision_blocks',), parent=None)
    _glow_glass(a, ('Sight',), parent=t)


# ----------------------------------------------------------------------------- tank destroyer
def _td(a):
    """Elite tank destroyer: side skirts on a rail under the sponsons (reactive armour on the front
    panels, gold chevrons), reactive armour on the front flank plates and the turret's front walls,
    cage armour behind the turret, a crest on each turret wall, a commander's sight on the front wall,
    an APS ring on the rear wall corner, smoke banks on the rear deck, a whip antenna and a gold band on
    the long gun; the driver's periscopes and the gun sight glow red."""
    t = 'Turret'
    for s in (-1, 1):
        veh._skirt(a, s, 1.66, -2.8, 2.9, .5, 1.0, 4, thick=.08, bolts=False)
        a.part('Skirt_rail', 'EliteBlack').box((.23, 5.7, .05), loc=(s * 1.565, .1, 1.0), bevel=0)
        for yc in (-2.1, -.667):                                     # panel centres -2.1, -.667, .767, 2.2
            _era_on(a, _onto((s * 1.70, yc, .76), (s, 0, 0), (0, 0, 1)), 3, 2, (.4, .16, .06), gap=.05)
        _chevrons(a, _onto((s * 1.70, .77, .74), (s, 0, 0), (0, -1, 0)), w=.36, h=.16, t=.07, gap=.14)
    # Reactive armour on the two front bolt-on plates of each flank (plate face 5 cm out of the flank).
    fx, fz, _ = _flank((1.52, 1.04), (1.16, 1.36), .5, .05)
    for s in (-1, 1):
        for y in (-1.55, -.2):
            _era_on(a, _onto((s * fx, y, fz), (s * .664, 0, .747), (-s * .747, 0, .664)), 2, 1, (.5, .24, .06),
                    gap=.05)
    # Turret: ERA on the front walls, crests on the side walls, cage armour behind the rear stowage.
    for s in (-1, 1):
        b0, b1 = ((.5, -1.25), (1.02, -.6)) if s > 0 else ((-1.02, -.6), (-.5, -1.25))
        _era_on(a, _face_frame(b0, b1, .72, .9, u=.5, v=.5), 2, 2, (.3, .22, .08), gap=.04, parent=t)
        side = ((1.02, -.6), (1.08, .8)) if s > 0 else ((-1.08, .8), (-1.02, -.6))
        _crest(a, _face_frame(*side, .72, .9, u=.16, v=.5), w=.26, h=.24, parent=t)   # clear of the bins
    veh._slats(a, _frame((0, 1.52, .4), (0, 0, 0)), 1.5, .48, 4, parent=t)
    for x in (-.5, .5):
        a.part('Slat_brackets', 'EliteBlack', t).box((.05, .22, .1), loc=(x, 1.42, .34), bevel=0)
    _cdr_sight(a, (.634, -.84, .72), parent=t, yaw=.35, post=.12)
    _aps(a, (-.72, .93, .72), parent=t, post=.06)
    for s in (-1, 1):
        _smoke_bank(a, (s * .92, 1.8, 1.36), s, count=4)
    _whip(a, (1.0, 3.36, 1.325), 1.3)
    _gilt_band(a, t, '', (0, -1.46 - 4.6, .44), .1, width=.07, seg=12)
    _glow_glass(a, ('Periscope',), parent=None)
    _glow_glass(a, ('Sight',), parent=t)


# ----------------------------------------------------------------------------- anti-aircraft vehicle
def _aa(a):
    """Elite anti-aircraft vehicle: reactive armour on the front skirt panels, two rows on the glacis
    and on the gun housings, gold chevrons on the skirts, a crest on the missile box, an APS ring and a
    commander's sight on the roof, smoke banks on the gun housings, antennas moved onto the bustle
    basket (clear of the radar's sweep) and gold bands on both guns; the driver's periscopes and the
    tracking sensor glow red."""
    t = 'Turret'
    _drop(a, ('Antenna', 'Beacon'), parent=t)     # the base whip stands inside the radar dish's sweep
    for s in (-1, 1):
        for yc in (-1.638, -.579):                                 # panel centres -1.638, -.579, .48, 1.539
            _era_on(a, _onto((s * 1.35, yc, .78), (s, 0, 0), (0, 0, 1)), 2, 2, (.44, .15, .06), gap=.04)
        _chevrons(a, _onto((s * 1.35, .48, .78), (s, 0, 0), (0, -1, 0)), w=.28, h=.14, t=.06, gap=.12)
    for u in (.3, .72):
        gy, gz, grot = _glacis((-2.4, .74), (-1.65, 1.12), u, .03)
        for x in (-.57, -.19, .19, .57):
            a.part('ERA', 'EliteBlack').box((.34, .28, .09), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.012, seg=1)
    for s in (-1, 1):
        _era_on(a, _onto((s * 1.064, -.15, .42), (s, 0, .03), (0, 0, 1)), 3, 2, (.34, .17, .06), gap=.04, parent=t)
        _smoke_bank(a, (s * .92, .15, .67), s, count=4, parent=t)
    _crest(a, _onto((-.36, .02, 1.27), (0, 0, 1), (0, -1, 0)), w=.3, h=.3, parent=t)
    _aps(a, (.5, .72, .72), parent=t, post=.06)
    _cdr_sight(a, (.62, -.08, .72), parent=t, yaw=.3, post=.12, size=(.26, .22, .16))
    _whip(a, (.6, 1.3, .4), 1.1, parent=t, tip='TeamGlow')
    _whip(a, (-.6, 1.3, .4), 1.4, parent=t)
    for s, suffix in ((-1, '_L'), (1, '_R')):
        _gilt_band(a, t, suffix, (s * .92, -.76 - 1.9, .44), .066, width=.06, seg=10)
    _glow_glass(a, ('Periscope',), parent=None)
    _glow_glass(a, ('Sight',), parent=t)


# ----------------------------------------------------------------------------- APC
def _apc(a):
    """Elite APC: the 30 mm gun becomes a bigger autocannon in a bigger mantlet (same Main_cannon /
    Muzzle_brake names, Muzzle_main moved to its opening), reactive armour on the front add-on flank
    plates, crests on the rear ones, gold chevrons on the turret roof, an APS ring, smoke banks, a
    second whip antenna and a gold band on the gun; the driver's vision blocks and the commander's
    sight glow red."""
    t = 'Turret'
    _drop(a, ('Main_cannon', 'Muzzle_brake'), parent=t)
    a.part('Mantlet', 'EliteBlack', t).box((.42, .34, .36), loc=(0, -.74, .28), bevel=.035)
    tip = veh._barrel(a, t, start_y=-.86, length=2.35, radius=.085, height=.28, brake=(.2, .26, .2),
                      sleeve=(.12, .6, .12), seg=12, style='baffle', bands=(.55, .78))
    a.pivots['Muzzle_main'].location = tip
    _gilt_band(a, t, '', (0, -.86 - 2.0, .28), .1, width=.06, seg=12)
    # Add-on plates on the 23-degree upper flanks: centres (|x| 1.158, z 1.683), 6 cm thick.
    for s in (-1, 1):
        n = Vector((s * .918, 0, .396))
        up = (-s * .396, 0, .918)
        for y in (-1.25, .15):
            _era_on(a, _onto(Vector((s * 1.158, y, 1.683)) + n * .03, n, up), 3, 2, (.38, .2, .06), gap=.04)
        _crest(a, _onto(Vector((s * 1.158, 1.55, 1.683)) + n * .032, n, up), w=.34, h=.3)
    _chevrons(a, _onto((-.08, -.32, .52), (0, 0, 1), (0, -1, 0)), w=.34, h=.13, t=.055, gap=.12, parent=t)
    _aps(a, (.1, .5, .52), parent=t, post=.04, yaw=math.pi / 8)
    for s in (-1, 1):
        _smoke_bank(a, (s * .52, .25, .52), s, count=4, parent=t)
    _whip(a, (.85, 3.0, 2.0), 1.3)
    _glow_glass(a, ('Vision_blocks',), parent=None)
    _glow_glass(a, ('Sight',), parent=t)


# ----------------------------------------------------------------------------- MLRS
def _mlrs(a):
    """Elite MLRS: an armoured cab (shutters over the windscreen and side windows leave red-lit visor
    slits, applique plates on the doors), side skirts with reactive armour over the chassis, and the
    12-round pod replaced by a twin pod of 2 x 9 rounds on the same launcher pivot (Muzzle_main stays
    centred on the pod faces); an APS ring, a commander's sight, smoke banks and a whip antenna on the
    cab roof, gold chevrons on the pods and crests on their flanks. The base model's roof HMG (Mount_mg)
    turns black with a gold barrel band and a red-lit sight."""
    t = 'Turret'
    wy, wz, rx = -3.72 + .34 * .55, 1.72 + .9 * .55, -math.atan2(.34, .9)
    n = Vector((0, -math.cos(rx), -math.sin(rx)))            # windscreen normal (forwards and up)
    up = Vector((0, .34, .9)).normalized()
    shutters = a.part('Shutters', 'EliteBlack')
    glow = a.part('Visor_glow', 'EliteGlow')
    for s in (-1, 1):
        m = _onto(Vector((s * .5, wy, wz)) + n * .012, n, up)                         # windscreen pane centre
        for v in (-.13, .13):
            _plate(shutters, m, (.94, .16, .05), sink=0.0, off=(0, v), bevel=0)
        _plate(glow, m, (.8, .03, .02), sink=-.015, bevel=0)
        m = _onto((s * 1.19, -2.72, 2.22), (s, 0, 0), (0, 0, 1))                       # side window centre
        for v in (-.11, .11):
            _plate(shutters, m, (.78, .15, .05), sink=0.0, off=(0, v), bevel=0)
        _plate(glow, m, (.66, .025, .02), sink=-.015, bevel=0)
        _plate(a.part('Elite_plates', 'EliteBlack'), _onto((s * 1.18, -2.72, 1.58), (s, 0, 0), (0, 0, 1)),
               (.8, .45, .05), sink=.005, bevel=.012)
        # Side skirts over the chassis between the front mud flap and the middle axle.
        for y0, y1 in ((-1.82, -.72), (-.68, .5)):
            yc = (y0 + y1) / 2
            a.part('Skirts', 'Team').box((.06, y1 - y0, .56), loc=(s * 1.17, yc, .9), bevel=.015, seg=1)
            _era_on(a, _onto((s * 1.20, yc, .88), (s, 0, 0), (0, 0, 1)), 2, 2, (.46, .2, .06), gap=.05)

    def roof(y):
        return 2.62 + (y + 3.38) / 1.38 * .08
    _aps(a, (-.45, -2.9, roof(-2.9)), post=.04)
    _cdr_sight(a, (.1, -3.0, roof(-3.0)), yaw=.2, post=.12)
    for s, y in ((1, -2.3), (-1, -2.6)):
        _smoke_bank(a, (s * .95, y, roof(y)), s, count=4)
    _whip(a, (-.95, -3.15, roof(-3.15)), 1.3)          # front left, out of the roof HMG's traverse
    # Twin pod on the same launcher: every base launcher part is rebuilt around two 9-round pods.
    _drop(a, None, parent=t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'EliteBlack', t)
    tsteel.cyl(.85, .14, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                    # turntable
    tarm.box((1.5, 1.6, .4), loc=(0, .1, .3), bevel=.05, taper=(.9, .92))
    pitch, L, H, W = .35, 3.5, 1.12, .98
    hinge = Vector((0, .95, .52))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = _frame(hinge - turn @ Vector((0, L / 2, -H / 2)), rot)
    tsteel.cyl(.12, 2.3, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)             # elevation hinge
    frame = a.part('Pod_frame', 'EliteBlack', t)
    for s in (-1, 1):
        tarm.box((.14, .5, .5), loc=(s * .8, .95, .4), bevel=.02, seg=1)                  # hinge cheeks
        tsteel.limb((s * .5, -.35, .42), tuple(mid @ Vector((s * .5, -.55, -H / 2 + .02))), .12, .12, bevel=.02)
        pod = _frame(mid @ Vector((s * .54, 0, 0)), rot)
        a.part('Pod', 'Team', t).box((W, L, H), loc=pod.to_translation(), rot=rot, bevel=.05)
        for y in (-L / 2 + .12, L / 2 - .12):                                             # end bands
            frame.box((W + .06, .16, H + .06), loc=pod @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
            for x in (-.44, .44):
                tsteel.box((.1, .1, .08), loc=pod @ Vector((x, y, H / 2 + .06)), rot=rot, bevel=0)   # lugs
        for x in (-.36, .36):                                                             # top rails
            frame.box((.12, L - .5, .05), loc=pod @ Vector((x, 0, H / 2 + .015)), rot=rot, bevel=0)
        for y in (-.7, 0, .7):                                                            # outer ribs
            frame.box((.05, .1, H - .1), loc=pod @ Vector((s * (W / 2 + .015), y, 0)), rot=rot, bevel=0)
        a.part('Pod_face', 'Undercarriage', t).box((W - .08, .02, H - .08), loc=pod @ Vector((0, -L / 2 - .005, 0)),
                                                   rot=rot, bevel=0)
        for row in (-.34, 0, .34):
            for col in (-.3, 0, .3):
                m = pod @ _frame((col, -L / 2, row), FORWARD)
                a.part('Tubes', 'Steel', t).lathe([(.12, -.04), (.12, .06), (.09, .06), (.09, -.02)],
                                                  loc=m.to_translation(), rot=m.to_euler('XYZ'), seg=8)
        up, fwd, out = (pod.to_3x3() @ Vector(v) for v in ((0, 0, 1), (0, -1, 0), (s, 0, 0)))
        _chevrons(a, _onto(pod @ Vector((0, -L / 2 + .75, H / 2)), up, fwd), w=.5, h=.18, t=.08, gap=.16, parent=t)
        _crest(a, _onto(pod @ Vector((s * (W / 2 + .002), 1.25, 0)), out, up), w=.3, h=.34, parent=t)
    tarm.box((.14, L - .4, H * .7), loc=mid @ Vector((0, .1, -H * .1)), rot=rot, bevel=0)  # spine between the pods
    a.pivots['Muzzle_main'].location = tuple(mid @ Vector((0, -L / 2 - .07, 0)))
    # The base model's roof HMG (on Mount_mg, mb_weapons.hmg with post .22: bore 0.36 m up, jacket from
    # y -0.17 to -0.43) turns EliteBlack with the other Armor; it also gets a gold band on the jacket in
    # front of the shield and a red-lit sight on the feed cover.
    m = 'Mount_mg'
    a.part('HMG_gilt', 'Gilded', m).cyl(.058, .05, loc=(0, -.39, .36), rot=FORWARD, seg=10, bevel=0)
    a.part('HMG_sight', 'EliteBlack', m).box((.06, .12, .07), loc=(0, -.02, .48), bevel=0)
    a.part('HMG_glow', 'EliteGlow', m).box((.04, .02, .04), loc=(0, -.088, .485), bevel=0)


# ----------------------------------------------------------------------------- attack helicopter
GUNNER = ((-4.05, .32, 1.6, 1.82), (-3.55, .54, 1.7, 2.26), (-2.68, .56, 1.76, 2.34))
PILOT = ((-2.78, .58, 1.78, 2.44), (-2.4, .6, 1.8, 2.62), (-1.35, .58, 1.84, 2.64), (-.95, .46, 1.88, 2.42))


def _bubble_at(secs, y):
    """(w, z0, z1) of attack_helicopter's canopy loft at y (linear between its sections)."""
    for (y0, *p0), (y1, *p1) in zip(secs, secs[1:]):
        if y0 <= y <= y1:
            f = (y - y0) / (y1 - y0)
            return [u + (v - u) * f for u, v in zip(p0, p1)]
    raise ValueError(y)


def _tub(y, w, z0, z1, t=.03, drop=.06, k=.55):
    """Armour ring around the lower sides of a canopy section: its top edge stands `t` outside the glass
    at k of the canopy height, its bottom edge `drop` below the sill, inside the fuselage."""
    zt = z0 + (z1 - z0) * k
    return [(-(w + t), y, z0 - drop), (w + t, y, z0 - drop), (w * .92 + t, y, zt), (-(w * .92 + t), y, zt)]


def _boom_w(y):
    """Half-width of attack_helicopter's tail boom at y (its loft runs from y 1.8 to 4.75)."""
    return .42 - .22 * (y - 1.8) / 2.95


def _big_pod(a, x, y, z, r, length):
    """19-round rocket pod (front at y): dark body, gold bands, a steel face with three rings of bores."""
    a.part('Pods', 'EliteBlack').lathe([(r * .5, length), (r * .85, length * .9), (r, length * .65), (r, .05),
                                         (r * .93, 0)], loc=(x, y, z), rot=air.BACKWARD, seg=14)
    for f in (.2, .55):
        a.part('Pod_bands', 'Gilded').cyl(r + .012, .05, loc=(x, y + length * f, z), rot=FORWARD, seg=14, bevel=0)
    a.part('Pod_face', 'Steel').cyl(r * .9, .02, loc=(x, y - .005, z), rot=FORWARD, seg=14, bevel=0)
    bores = a.part('Pod_tubes_bore', 'Undercarriage')
    pts = [(0.0, 0.0)] + [(math.cos(k * math.tau / 6) * .115, math.sin(k * math.tau / 6) * .115) for k in range(6)] + \
          [(math.cos((k + .5) * math.tau / 12) * .215, math.sin((k + .5) * math.tau / 12) * .215) for k in range(12)]
    for px, pz in pts:
        bores.cyl(.042, .02, loc=(x + px, y - .018, z + pz), rot=FORWARD, seg=6, bevel=0)


def _heli(a):
    """Elite attack helicopter (1.1x): armoured cockpit (dark armour tubs round the lower canopy),
    bigger 19-round rocket pods (Muzzle_rocket moved to their faces), four more flare dispensers on the
    tail boom, missile-warning sensors on the nose, a red sensor ring on the mast radar, gold chevrons on
    the stub wings, crests on the fin, two more antennas; the nose sensor windows and the IR jammer glow
    red."""
    tubs = a.part('Cockpit_armor', 'EliteBlack')
    for secs, ys in ((GUNNER, (-3.85, -3.55, -3.1, -2.74)), (PILOT, (-2.72, -2.4, -1.35, -1.05))):
        tubs.loft([_tub(y, *_bubble_at(secs, y)) for y in ys], bevel=.02, seg=1)
    for s in (-1, 1):
        for y, zc, h in ((2.5, 1.71, .2), (3.55, 1.73, .16)):
            w = _boom_w(y)
            a.part('Flare_pods', 'EliteBlack').box((.1, .46, h + .02), loc=(s * (w + .03), y, zc), bevel=.015, seg=1)
            a.part('Flares', 'Undercarriage').grille(.4, h, loc=(s * (w + .085), y, zc), rot=(0, 0, s * R90), slats=3,
                                                     depth=.03, thickness=.03)
        # Missile-approach warning sensors on the nose flanks, looking forwards and out.
        d = Vector((s * .7, -.7, .1)).normalized()
        rot = Vector((0, 0, 1)).rotation_difference(d).to_euler('XYZ')
        c = Vector((s * .5, -3.9, 1.4))
        a.part('MAWS', 'EliteBlack').cyl(.075, .16, loc=tuple(c + d * .03), rot=rot, seg=10, bevel=.015, bseg=1)
        a.part('Elite_glow', 'EliteGlow').cyl(.05, .03, loc=tuple(c + d * .115), rot=rot, seg=10, bevel=0)
        _chevrons(a, _onto((s * 1.45, .02, 1.6), (0, 0, 1), (0, -1, 0)), w=.44, h=.16, t=.07, gap=.14)
        _crest(a, _onto((s * .082, 4.62, 2.5), (s, 0, 0), (0, 0, 1)), w=.3, h=.32)
    _drop(a, ('Pods', 'Pod_bands', 'Pod_tubes_bore'), parent=None)
    for s in (-1, 1):
        _big_pod(a, s * 1.5, -1.0, 1.04, .3, 1.8)
    a.pivots['Muzzle_rocket'].location = (0, -1.05, 1.04)
    a.part('Mast_glow', 'EliteGlow').cyl(.412, .035, loc=(0, -.6, 3.84), seg=14, bevel=0)
    _whip(a, (0, 2.2, 1.975), .7)
    _whip(a, (.25, .15, 2.52), .45)
    _glow_glass(a, ('Sensor',), parent=None)


# name: (builder, Asset options): the base model's options (AO distance and grime scale with it).
BUILDERS = {
    'elite_mbt': (elite(veh.main_battle_tank, _mbt), dict(ao_distance=.6, grime_height=.55)),
    'elite_heavy_tank': (elite(veh.heavy_tank, _heavy), dict(ao_distance=.65, grime_height=.6)),
    'elite_tank_destroyer': (elite(veh.tank_destroyer, _td), dict(ao_distance=.6, grime_height=.55)),
    'elite_attack_helicopter': (elite(air.attack_helicopter, _heli, scale=1.1), dict(ao_distance=.6, grime_height=.4)),
    'elite_mlrs': (elite(veh.mlrs, _mlrs), dict(ao_distance=.6, grime_height=.55)),
    'elite_aa': (elite(veh.aa_vehicle, _aa), dict(ao_distance=.55, grime_height=.5)),
    'elite_apc': (elite(veh.apc, _apc), dict(ao_distance=.6, grime_height=.55)),
}
