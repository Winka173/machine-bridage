"""Machine Brigade fortress defences built with frontier_kit: the heavy works of the reworked, multi-stage
Siege (outer defence line, shielded gates, citadel). They extend mb_siege's base kit and share its style,
materials and helpers.

Static defences are "vehicles" with speed 0 (ModelLibrary rigs them like tanks), each on its own
concrete pad with the origin on the ground at the footprint centre:
  * heavy_turret (8 x 8 m, turret top 4.4 m): coastal battery after the Maxim Gorky / Batterie Todt
    works: a twin 155 mm naval gun turret (sloped face, canvas blast bags, rangefinder ears, sighting
    hoods) on a battered concrete casemate with an overhanging roof slab. `Turret` with Main_cannon /
    Main_cannon_2 and Muzzle_brake / Muzzle_brake_2 (recoil), `Muzzle_main` centred between the tips, a
    ball-mounted coaxial MG on the turret face (Coax* parts, `Muzzle_coax`) and a roof HMG on `Mount_mg`
    (`Muzzle_mg`), all under Turret.
  * flak_tower (8 x 8 m, 7 m to the raised gun tips): a squat first-generation Flakturm: a battered
    concrete block with four octagonal corner towers under corbelled galleries, and a quad heavy flak
    mount on the central gun platform (`Turret` with Main_cannon .. Main_cannon_4 and Muzzle_brake ..
    Muzzle_brake_4, one `Muzzle_main`). The barrels ride in two cradles, `Pod` and `Pod_2`, with elevating
    arcs `Pod_arc` / `Pod_2_arc`; ModelLibrary elevates Pod* parts with the guns, and the arcs put its
    automatic elevation pivot on the trunnions. Galleries: a two-round SAM box on `Mount_missile`
    (`Muzzle_missile`, front right), a `Searchlight` pivot that the game sweeps (front left), a
    fire-control radar spinning on `Radar` (rear left) and a static rangefinder (rear right).
  * missile_battery (9 x 7 m): a Patriot / S-300 site: a four-canister launcher on a turntable (`Turret`;
    the canister box is the Launcher* group, which elevates about its A-frame trunnions, with
    `Muzzle_main` at its front), a search radar spinning on `Radar` on top of its own lattice mast, an
    equipment shelter, a generator, a spare canister and a guard HMG in a sandbag nest on `Mount_mg`
    (`Muzzle_mg`).
Prop: shield_generator (7 x 7 m, mast 5.8 m), the objective that drops a gate's shield: a hardened
generator block with a roof bank of cooling fins, two transformers with porcelain bushings, overhead lines
on H-frame pylons, ground cables, and an emitter mast whose glowing core (TeamGlow) sits in a strut cage
inside an emitter ring spinning on `Radar_2`. No Turret, no muzzles.

Conventions follow mb_siege / mb_vehicles: metres, +Z up, Blender -Y is the front. Main paint is on
`Team` parts; the rest is Concrete, Armor and Steel. Lights are Lamp; warning lights Alloy; the live
parts of the shield generator TeamGlow. Touching parts overlap or stand at least 1 cm apart, never face
to face (coplanar faces z-fight). Each main weapon is the highest thing inside its sweep, so its
`Turret` can turn all the way round. Only the elevating barrel groups use the names ModelLibrary's
BarrelPattern looks for (Main_cannon*, Muzzle_brake*, Launcher*, Pod*, Coax*); no other part uses those
prefixes (the SAM box tubes are SAM_tubes).
"""
import math
import random

from mathutils import Matrix, Vector

import mb_weapons as wpn
from frontier_kit import chamfered
from mb_siege import (_circle, _moving_pivots, bag_arc, bag_run, caged_lamp, crate, flood_head, generator, hazard_sign,
                      lattice, loop_rail, shells)
from mb_themes import ladder
from mb_vehicles import ACROSS, FORWARD, R90, _antenna, _dish, _face_box, _frame, _hatch, _stowage_bin, _tube_mouth
from mb_vehicles2 import _axis

TAU = math.tau


# ----------------------------------------------------------------------------- shared helpers
def _qframe(b0, b1, t0, t1, u=.5, v=.5, out=0.0):
    """Frame on a quad face whose bottom edge runs b0 -> b1 and top edge t0 -> t1 (3D points, the
    bottom edge counter-clockwise seen from above so +Z points out of the face): origin u along the
    edge and v up the face, X along the edge, Y up the face, Z out of it."""
    b0, b1, t0, t1 = (Vector(p) for p in (b0, b1, t0, t1))
    bot, top = b0.lerp(b1, u), t0.lerp(t1, u)
    ax = (b1 - b0).normalized()
    ay = (top - bot).normalized()
    az = ax.cross(ay).normalized()
    ay = az.cross(ax)
    o = bot.lerp(top, v) + az * out
    return Matrix(((ax.x, ay.x, az.x, o.x), (ax.y, ay.y, az.y, o.y), (ax.z, ay.z, az.z, o.z), (0, 0, 0, 1)))


def _house(part, bottom, top, z0, z1, loc=(0, 0, 0), bevel=.05, seg=1):
    """Armoured house: skins a bottom outline at z0 to a top outline at z1 (same point count,
    counter-clockwise), so the front can slope more than the sides."""
    part.loft([[(x, y, z0) for x, y in bottom], [(x, y, z1) for x, y in top]], loc=loc, bevel=bevel, seg=seg)


def _jersey(a, x, y, yaw=0.0, length=1.8, h=.82, band=True):
    """Precast jersey barrier standing on (x, y) along local X, with a Team reflector band on both faces."""
    m = _frame((x, y, 0), (0, 0, yaw))
    prof = [(-.3, -.02), (.3, -.02), (.3, .1), (.1, .32), (.08, h), (-.08, h), (-.1, .32), (-.3, .1)]
    a.part('Barriers', 'Concrete').prism(prof, length, loc=m @ Vector((0, 0, 0)), rot=(0, 0, yaw), axis='X', bevel=.02,
                                         seg=1)
    if band:
        zb = .6
        hw = .1 - .02 * (zb - .32) / (h - .32)
        for s in (-1, 1):
            a.part('Barrier_bands', 'Team').box((length - .3, .03, .12), loc=m @ Vector((0, s * (hw + .004), zb)),
                                                rot=(-s * .04, 0, yaw), bevel=0)


def _embrasure(a, m, w=.8, h=.26, parent=None):
    """Stepped firing embrasure on the face frame m (see _qframe): a raised concrete surround, a dark
    slit proud of it and a steel visor above."""
    _face_box(a, 'Embrasures', 'Concrete', m, (w + .4, h + .34, .18), parent=parent, bevel=.03, sink=.03)
    _face_box(a, 'Embrasure_slits', 'Charred', m, (w, h, .18), parent=parent, bevel=0, sink=.01)
    _face_box(a, 'Embrasure_visors', 'Steel', m, (w + .5, .07, .36), parent=parent, bevel=0, lift=h / 2 + .2, sink=.02)


def _bag_bend(part, rng, pts, z, size, half=False):
    """Sandbag course along a polyline (corners overlap)."""
    for p, q in zip(pts, pts[1:]):
        bag_run(part, rng, p, q, z, size, half)


# ----------------------------------------------------------------------------- heavy_turret
def heavy_turret(a):
    """Coastal gun battery (8 x 8 m, turret top 4.4 m) after the Maxim Gorky and Batterie Todt works: a
    battered concrete casemate with an overhanging roof slab and a Team fascia, stepped MG embrasures,
    a rear blast door with a lamp and hazard frame, a ladder, vents and a hazard-striped turret collar.
    The twin 155 mm naval turret has a sloped face with canvas blast bags round the gun ports, bolted
    cheek and side plates, rangefinder ears, two sighting hoods, a cupola, hatches, an ammunition hoist
    door, antennas, a roof HMG (Mount_mg) and a ball-mounted coaxial MG (Muzzle_coax). Sandbag nests with
    ready rounds guard the front corners; jersey barriers and crates stand at the back."""
    rng = random.Random(101)
    a.part('Pad', 'Concrete').prism(chamfered(8.0, 8.0, 1.0), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .24
    conc = a.part('Casemate', 'Concrete')
    W, H, TP, z0 = 6.0, 2.2, .93, .2
    base = chamfered(W, W, 1.0)
    # Lofted through intermediate rings, so the baked occlusion under the slab and at the foot does not
    # streak across the whole battered wall.
    conc.loft([[(x * (1 - (1 - TP) * f), y * (1 - (1 - TP) * f), z0 + H * f) for x, y in base]
               for f in (0, .22, .5, .78, 1)], bevel=.05, seg=1)                                # z .2 .. 2.4
    slab = chamfered(6.4, 6.4, 1.05)
    conc.prism(slab, .34, loc=(0, 0, 2.54), axis='Z', bevel=.04, seg=1)                        # z 2.37 .. 2.71
    a.part('Fascia', 'Team').shell(chamfered(6.46, 6.46, 1.07), .18, .06, loc=(0, 0, 2.46))
    roof = 2.71

    def face(i, u, v, out=0.0):
        p, q = base[i], base[(i + 1) % len(base)]
        return _qframe((p[0], p[1], z0), (q[0], q[1], z0), (p[0] * TP, p[1] * TP, z0 + H),
                       (q[0] * TP, q[1] * TP, z0 + H), u, v, out)
    # Front: two stepped MG embrasures and a stencil; right: a third embrasure.
    for u in (.2, .8):
        _embrasure(a, face(0, u, .5))
    _embrasure(a, face(2, .5, .52))
    _face_box(a, 'Stencils', 'Hazard', face(0, .5, .72), (.6, .22, .03), bevel=0)
    _face_box(a, 'Stencils', 'Hazard', face(0, .5, .6), (.3, .1, .03), bevel=0)
    # Rear: entrance portal with a steel blast door in a hazard frame, lamp and step.
    conc.box((2.2, 1.1, 2.25), loc=(0, 3.05, .2 + 1.125), bevel=.05, seg=1)                     # y 2.5 .. 3.6
    fy = 3.6
    a.part('Blast_door', 'Steel').box((1.2, .1, 1.6), loc=(0, fy + .02, 1.05), bevel=.02, seg=1)
    for x in (-.3, .3):
        a.part('Door_ribs', 'Armor').box((.1, .06, 1.5), loc=(x, fy + .08, 1.05), bevel=0)
    for k in range(5):
        for s in (-1, 1):
            a.part('Door_hazard', 'SafetyStripe' if k % 2 else 'Charred').box(
                (.2, .04, .34), loc=(s * .75, fy + .02, .4 + k * .34), bevel=0)
    for k in range(6):
        a.part('Door_hazard', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.29, .04, .2), loc=(-.725 + k * .29, fy + .01, 1.98), bevel=0)
    caged_lamp(a, '+y', (.0, fy, 2.25))
    a.part('Steps', 'Concrete').box((1.4, .3, .1), loc=(0, 3.73, .27), bevel=.02, seg=1)
    # Right side: ladder to the roof with standoff brackets, conduit and a junction box.
    lx = 3.33
    ladder(a.part('Ladder', 'Steel'), (lx, 1.4, .24), roof + .45, R90, width=.46, step=.34, rung=.03)

    def wall_x(z):                                                                          # right face
        return W / 2 - W / 2 * (1 - TP) * (z - z0) / H
    for z in (.9, 2.0):
        x0 = wall_x(z) - .03
        a.part('Ladder', 'Steel').box((lx - x0, .04, .04), loc=((lx + x0) / 2, 1.4, z), bevel=0)
    a.part('Conduit', 'Pipe').tube([(3.07, -1.6, .22), (3.035, -1.6, .6), (2.855, -1.6, 2.45)], .05, seg=6)
    jx = wall_x(1.0)
    a.part('Junction_box', 'Armor').box((.2, .4, .5), loc=(jx + .08, -1.1, 1.0), rot=(0, -.1, 0), bevel=.02, seg=1)
    a.part('Junction_lamp', 'Alloy').box((.04, .08, .08), loc=(jx + .19, -1.0, 1.16), rot=(0, -.1, 0), bevel=0)
    # Roof: hazard-striped collar round the turret race, a low observation cupola, vents.
    tx, ty = 0.0, .2
    a.part('Collar', 'Armor').lathe([(2.72, roof - .03), (2.72, roof + .03), (2.3, roof + .15), (0, roof + .15)],
                                    loc=(tx, ty, 0), seg=28)
    for k in range(28):
        ang = (k + .5) * TAU / 28
        a.part('Collar_band', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.5, .24, .04), loc=(tx + 2.88 * math.cos(ang), ty + 2.88 * math.sin(ang), roof + .005),
            rot=(0, 0, ang + R90), bevel=0)
    a.part('Race', 'Steel').cyl(2.12, .1, loc=(tx, ty, roof + .16), seg=28, bevel=.02, bseg=1)   # z 2.82 .. 2.92
    cx, cy = -2.5, -2.26
    a.part('Obs_cupola', 'Armor').cyl(.4, .4, loc=(cx, cy, roof + .18), seg=12, bevel=.03, bseg=1)
    glass = a.part('Obs_slits', 'Glass')
    for k in range(5):
        u = -R90 + (k - 2) * .6
        glass.box((.16, .05, .07), loc=(cx + .395 * math.cos(u), cy + .395 * math.sin(u), roof + .3),
                  rot=(0, 0, u + R90), bevel=0)
    a.part('Obs_cap', 'Steel').cyl(.33, .06, loc=(cx, cy, roof + .4), seg=12, bevel=.015, bseg=1)
    # A low searchlight on the front-right corner (under the guns' sweep).
    lx_, ly_ = 2.45, -2.3
    a.part('Lamp_post', 'Steel').cyl(.06, .3, loc=(lx_, ly_, roof + .14), seg=8, bevel=0)
    a.part('Lamp_post', 'Steel').box((.4, .1, .06), loc=(lx_, ly_, roof + .2), bevel=0)
    a.part('Lamp_drum', 'Armor').cyl(.16, .34, loc=(lx_, ly_ + .02, roof + .36), rot=FORWARD, seg=12, bevel=.02, bseg=1)
    a.part('Lamp_lens', 'Lamp').cyl(.13, .04, loc=(lx_, ly_ - .15, roof + .36), rot=FORWARD, seg=12, bevel=0)
    for x, y in ((2.5, 2.35), (-2.5, 2.35)):
        a.part('Vents', 'Steel').cyl(.13, .42, loc=(x, y, roof + .19), seg=8, bevel=0)
        a.part('Vent_caps', 'Armor').cyl(.22, .07, loc=(x, y, roof + .42), r2=.14, seg=8, bevel=0)
    # Roof hatch over the shell room.
    a.part('Roof_hatch', 'Armor').box((.8, .8, .12), loc=(-2.55, 1.2, roof + .04), bevel=.03, seg=1)
    a.part('Roof_hatch_bar', 'Steel').box((.1, .7, .06), loc=(-2.55, 1.2, roof + .12), bevel=0)
    # Sandbag nests with ready rounds in the front corners, barriers and crates at the back.
    bags = a.part('Sandbags', 'Sandbag')
    size = (.7, .38, .25)
    for s in (-1, 1):
        pts = [(s * 1.35, -3.62), (s * 2.7, -3.62), (s * 3.62, -2.7), (s * 3.62, -1.35)]
        if s > 0:
            pts = pts[::-1]
        for course in range(2):
            _bag_bend(bags, rng, pts, .24 + .12 + course * .22, size, half=course == 1)
        shells(a, (s * 2.55, -3.05, .24), 2, 2, r=.075, h=.66, pitch=.18, yaw=s * .78)
    for s in (-1, 1):
        _jersey(a, s * 3.05, 3.05, yaw=-s * math.pi / 4, length=1.7)
    crate(a, (1.65, 3.62, .24), size=(.9, .42, .34), yaw=.05)
    crate(a, (1.67, 3.6, .58), size=(.84, .4, .32), yaw=-.05, band=False)
    crate(a, (-1.7, 3.64, .24), size=(.9, .42, .34), yaw=-.08, band=False)

    # ---------------------------------------------------------------- turret
    t = a.pivot('Turret', (tx, ty, roof + .21))                                             # z 2.92
    a.part('Turret_ring', 'Armor', t).cyl(2.02, .22, loc=(0, 0, .06), seg=20, bevel=0)
    bottom = [(-1.4, -2.0), (1.4, -2.0), (2.1, -1.2), (2.1, 1.9), (1.7, 2.5), (-1.7, 2.5), (-2.1, 1.9), (-2.1, -1.2)]
    top = [(-1.25, -.95), (1.25, -.95), (1.95, -.55), (1.98, 1.85), (1.6, 2.4), (-1.6, 2.4), (-1.98, 1.85),
           (-1.95, -.55)]
    zb, zt = .12, 1.5                                                                       # turret top 4.42
    _house(a.part('Turret_body', 'Team', t), bottom, top, zb, zt, bevel=.06)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    B = [(x, y, zb) for x, y in bottom]
    T = [(x, y, zt) for x, y in top]

    def tface(i, u, v, out=0.0):
        j = (i + 1) % 8
        return _qframe(B[i], B[j], T[i], T[j], u, v, out)
    zg = .72                                                                                # gun axis
    face_y = -2.0 + 1.05 * (zg - zb) / (zt - zb)                                           # face at gun height
    # Face: bolted plates between and beside the gun ports, cheek plates on the angled corners.
    _face_box(a, 'Face_plates', 'Armor', tface(0, .5, .87), (.6, .4, .1), parent=t, bevel=.02)
    for i in (1, 7):
        for v in (.3, .72):
            _face_box(a, 'Cheek_plates', 'Armor', tface(i, .5, v), (.62, .52, .12), parent=t, bevel=.02)
            m = tface(i, .5, v)
            tsteel.bolts([tuple(m @ Vector((dx, dy, .115))) for dx in (-.22, .22) for dy in (-.18, .18)], r=.03, h=.03,
                         rot=m.to_euler('XYZ'), seg=5, bevel=0)
    for i, us in ((2, (.17, .45)), (6, (.55, .83))):                                        # side plates
        for u in us:
            m = tface(i, u, .42)
            _face_box(a, 'Side_plates', 'Armor', m, (.84, .9, .08), parent=t, bevel=.015)
            tsteel.bolts([tuple(m @ Vector((dx, dy, .075))) for dx in (-.34, .34) for dy in (-.36, .36)], r=.03,
                         h=.03, rot=m.to_euler('XYZ'), seg=5, bevel=0)
    # Rear: ammunition hoist door with hinges, rungs up to the roof, a stowage bin.
    m = tface(4, .5, .42)
    _face_box(a, 'Hoist_door', 'Armor', m, (1.0, .8, .08), parent=t, bevel=.015)
    for dx in (-.42, .42):
        _face_box(a, 'Hoist_hinges', 'Steel', m @ _frame((dx, .25, 0), (0, 0, 0)), (.1, .12, .15), parent=t, bevel=0,
                  sink=.03)
    _face_box(a, 'Hoist_handle', 'Steel', m @ _frame((.3, 0, 0), (0, 0, 0)), (.14, .05, .14), parent=t, bevel=0,
              sink=.03)
    for k in range(4):
        _face_box(a, 'Rungs', 'Steel', tface(4, .8, .15 + k * .2), (.36, .03, .1), parent=t, bevel=0)
    _stowage_bin(a, (1.2, 2.55, .45), (.7, .3, .5), parent=t, latch_side=0, yaw=math.pi)
    # Rangefinder ears on both sides at the rear, lenses facing forward.
    for s in (-1, 1):
        ex = s * 2.15
        tarm.box((.56, .8, .5), loc=(ex, 1.35, 1.12), bevel=.05, seg=1)
        tarm.box((.62, .1, .56), loc=(ex, .95, 1.12), bevel=.02, seg=1)                     # lens hood
        a.part('Rangefinder_lens', 'Glass', t).box((.3, .04, .22), loc=(ex, .895, 1.12), bevel=.01, seg=1)
        tsteel.box((.2, .5, .14), loc=(ex, 1.45, 1.4), bevel=0)                              # top rail
    # Roof: sighting hoods, cupola, hatches, ventilator, lifting eyes, seams and rivets, antennas.
    for s in (-1, 1):
        hx = s * 1.08
        tarm.box((.5, .5, .32), loc=(hx, -.58, zt + .12), bevel=.05, seg=1)
        a.part('Sight_glass', 'Glass', t).box((.34, .06, .12), loc=(hx, -.84, zt + .15), bevel=.01, seg=1)
    tsteel.cyl(.42, .24, loc=(-.75, .75, zt + .1), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.36, .08, loc=(-.75, .75, zt + .25), seg=16, bevel=.02, bseg=1)
    _hatch(a, -.75, .75, zt + .27, .27, parent=t)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(6):
        ang = -R90 + (k - 2.5) * .55
        glass.box((.12, .05, .08), loc=(-.75 + math.cos(ang) * .425, .75 + math.sin(ang) * .425, zt + .15),
                  rot=(0, 0, ang + R90), bevel=0)
    _hatch(a, .75, 1.6, zt - .01, .3, parent=t)
    tarm.cyl(.24, .14, loc=(0, 1.9, zt + .05), seg=12, bevel=.02, bseg=1)
    a.part('Vent_cap', 'Undercarriage', t).cyl(.18, .05, loc=(0, 1.9, zt + .13), seg=12, bevel=0)
    seams = a.part('Roof_seams', 'Armor', t)
    for y in (.2, 1.2):
        seams.box((3.7, .07, .04), loc=(0, y, zt + .005), bevel=0)
    tsteel.bolts([(x, -.82, zt - .005) for x in (-.8, -.4, 0, .4, .8)] +
                 [(s * 1.78, y, zt - .005) for s in (-1, 1) for y in (-.3, .3, .9, 1.5)], r=.035, h=.03, seg=5,
                 bevel=0)
    for x, y in ((1.5, -.35), (-1.5, -.35), (1.35, 2.05), (-1.35, 2.05)):
        tsteel.tube([(x - .08, y, zt - .02), (x - .08, y, zt + .09), (x + .08, y, zt + .09), (x + .08, y, zt - .02)],
                    .022, seg=4)
    _antenna(a, t, -1.45, 2.1, zt, 1.6)
    _antenna(a, t, 1.5, 2.15, zt, 1.2)
    tsteel.box((.12, .12, .08), loc=(-1.45, 2.1, zt + .02), bevel=0)
    # Roof HMG (second weapon, slot mg) on a pintle at the right of the roof.
    wpn.hmg(a, (1.0, .5, zt - .01), parent=t, post=.3, ammo=1)
    # Coaxial MG in a ball mount on the face between the guns, on their axis, so the automatic elevation pivot
    # stays near the axis (Muzzle_coax).
    zc = zg                                                                                 # on the gun axis
    cy_ = -2.0 + 1.05 * (zc - zb) / (zt - zb)
    a.part('Coax_mount', 'Armor', t).sphere(.19, loc=(0, cy_ + .02, zc), seg=10, rings=6)
    a.part('Coax', 'Steel', t).cyl(.04, .6, loc=(0, cy_ - .38, zc), rot=FORWARD, seg=8, bevel=0)
    a.part('Coax_hider', 'Undercarriage', t).cyl(.055, .12, loc=(0, cy_ - .68, zc), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (0, cy_ - .75, zc), t)
    # Twin 155 mm guns: canvas blast bags at the ports, jacketed tapering barrels, muzzle swells.
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .78
        a.part('Blast_bags', 'Canvas', t).lathe(
            [(.37, 0), (.37, .14), (.31, .22), (.35, .31), (.29, .4), (.32, .49), (.26, .58), (.235, .68),
             (.215, .72)], loc=(x, face_y + .38, zg), rot=FORWARD, seg=12)
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        y0 = face_y + .2
        gun.cyl(.2, 1.2, loc=(x, y0 - .6, zg), rot=FORWARD, seg=14, bevel=.02, bseg=1)           # jacket
        gun.cyl(.225, .07, loc=(x, y0 - 1.2, zg), rot=FORWARD, seg=14, bevel=0)                  # jacket band
        L = 3.5
        gun.cyl(.165, L, loc=(x, y0 - 1.15 - L / 2, zg), r2=.135, rot=FORWARD, seg=14, bevel=.01, bseg=1)
        gun.cyl(.16, .05, loc=(x, y0 - 1.15 - L * .55, zg), rot=FORWARD, seg=14, bevel=0)        # mid band
        mz = y0 - 1.15 - L + .03
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).lathe(
            [(.13, 0), (.19, .12), (.2, .42), (.18, .5), (.11, .5), (.11, .38)], loc=(x, mz, zg), rot=FORWARD,
            seg=14)
        tips.append(Vector((x, mz - .5, zg)))
    a.pivot('Muzzle_main', tuple((tips[0] + tips[1]) / 2), t)



# ----------------------------------------------------------------------------- flak_tower
def _shuttered_window(a, m, lit=False, size=.42):
    """Small armoured window on the face frame m: a steel surround and a Team shutter, closed, or
    swung open on its left hinge beside a lit pane."""
    _face_box(a, 'Window_frames', 'Armor', m, (size + .14, size + .14, .08), bevel=0, sink=.02)
    if lit:
        _face_box(a, 'Lit_windows', 'Lamp', m, (size, size, .09), bevel=0, sink=.01)
        hinge = m @ _frame((-size / 2 - .07, 0, .06), (0, 0, 0))
        _face_box(a, 'Shutters', 'Team', hinge @ _frame((-.03, 0, size / 2), (0, -R90, 0)), (size, size, .05),
                  bevel=0, sink=.025)
    else:
        _face_box(a, 'Shutters', 'Team', m, (size, size, .1), bevel=0, sink=.01)
        _face_box(a, 'Shutter_bars', 'Steel', m, (size + .06, .05, .12), bevel=0, sink=.005)


def _sam_box(a, loc, pitch=math.radians(15), L=1.1, post=.3):
    """Two-round SAM box (Mistral / Stinger lineage) on a pedestal standing on loc: the pedestal stays,
    the box turns on `Mount_missile`, raised `pitch`, with `Muzzle_missile` between the tube mouths."""
    x, y, z = loc
    ped = a.part('SAM_pedestal', 'Armor')
    ped.cyl(.2, .08, loc=(x, y, z + .03), seg=10, bevel=.01, bseg=1)
    ped.cyl(.08, post, loc=(x, y, z + post / 2 + .02), seg=8, bevel=0)
    m = a.pivot('Mount_missile', (x, y, z + post))
    arm = a.part('SAM_cradle', 'Steel', m)
    arm.cyl(.11, .1, loc=(0, 0, .04), seg=10, bevel=0)
    for s in (-1, 1):
        arm.box((.05, .26, .3), loc=(s * .2, .02, .2), bevel=0)
    at = _axis((0, .1, .3), pitch)
    rot = (-pitch, 0, 0)
    a.part('SAM_box', 'Team', m).box((.34, L, .48), loc=tuple(at(L / 2 - .2)), rot=rot, bevel=.03, seg=1)
    fr = a.part('SAM_frame', 'Armor', m)
    for d in (-.14, L - .28):
        fr.box((.38, .1, .52), loc=tuple(at(d)), rot=rot, bevel=.01, seg=1)
    a.part('SAM_sight', 'Armor', m).box((.14, .22, .16), loc=tuple(at(.1, .06, -.26)), rot=rot, bevel=.01, seg=1)
    a.part('SAM_sight_glass', 'Glass', m).box((.1, .03, .1), loc=tuple(at(-.02, .06, -.26)), rot=rot, bevel=0)
    for up in (-.11, .11):
        _tube_mouth(a, m, _frame(at(L - .2, up), (R90 - pitch, 0, 0)), .09, protrude=.05, seg=10, name='SAM_tubes')
    a.part('SAM_band', 'Hazard', m).box((.36, .08, .5), loc=tuple(at(L * .45)), rot=rot, bevel=0)
    a.pivot('Muzzle_missile', tuple(at(L - .2 + .05)), m)


def _searchlight(a, loc, r=.3, length=.52, parent=None):
    """Light searchlight on the `Searchlight` pivot (the game sweeps it): a turntable, a yoke and a drum
    whose Lamp lens faces the pivot's -Y, with a steel bezel and a back cap."""
    p = a.pivot('Searchlight', loc, parent)
    yoke = a.part('Searchlight_yoke', 'Steel', p)
    zc = .14 + r + .06
    yoke.cyl(.2, .1, loc=(0, 0, .04), seg=10, bevel=0)
    yoke.box((2 * r + .26, .14, .07), loc=(0, 0, .12), bevel=0)
    for s in (-1, 1):
        yoke.box((.06, .12, zc - .1), loc=(s * (r + .08), 0, .1 + (zc - .1) / 2), bevel=0)
    head = a.part('Searchlight_head', 'Armor', p)
    head.cyl(r, length, loc=(0, .03, zc), rot=FORWARD, seg=12, bevel=.015, bseg=1)
    yf = .03 - length / 2
    yoke.cyl(r + .035, .08, loc=(0, yf + .02, zc), rot=FORWARD, seg=12, bevel=0)               # bezel
    a.part('Searchlight_lens', 'Lamp', p).cyl(r * .9, .04, loc=(0, yf - .01, zc), rot=FORWARD, seg=12, bevel=0)
    head.cyl(r * .72, .08, loc=(0, .03 + length / 2 + .03, zc), rot=FORWARD, seg=10, bevel=0)
    return p


def flak_tower(a):
    """Flak tower (8 x 8 m, 6.9 m to the gun tips) after the first-generation Flakturm G-towers, scaled
    down and squat: a battered concrete block with an overhanging roof slab, rows of small windows
    behind Team steel shutters (a few swung open on lit rooms), and four octagonal corner towers
    carrying corbelled galleries behind parapets with Team bands. The galleries hold a sweeping
    `Searchlight` (front left), a two-round SAM box on `Mount_missile` (front right), a fire-control
    radar spinning on `Radar` (rear left) and an optical rangefinder (rear right). The central gun
    platform carries a quad heavy flak mount on `Turret`: a Team gun house with two gun cradles
    (`Pod`, `Pod_2`, elevating with the guns) of two long barrels each, brass ready rounds and a
    loading tray. An entrance with a blast door on the right, sandbags, flak crates, a generator and
    fuel drums fill the recesses between the corner towers."""
    rng = random.Random(202)
    a.part('Pad', 'Concrete').prism(chamfered(8.0, 8.0, .8), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .24
    conc = a.part('Tower', 'Concrete')
    hw, z0, H, TP = 2.7, .2, 2.9, .95
    sq = [(-hw, -hw), (hw, -hw), (hw, hw), (-hw, hw)]
    conc.loft([[(x * (1 - (1 - TP) * f), y * (1 - (1 - TP) * f), z0 + H * f) for x, y in sq]
               for f in (0, .25, .5, .75, 1)], bevel=.05, seg=1)                                # z .2 .. 3.1
    conc.prism(chamfered(5.7, 5.7, .3), .3, loc=(0, 0, 3.2), axis='Z', bevel=.04, seg=1)        # slab 3.05 .. 3.35
    roof = 3.35

    def bface(i, u, v):
        p, q = sq[i], sq[(i + 1) % 4]
        return _qframe((p[0], p[1], z0), (q[0], q[1], z0), (p[0] * TP, p[1] * TP, z0 + H),
                       (q[0] * TP, q[1] * TP, z0 + H), u, v)
    # Corner towers with corbelled galleries and parapets.
    ct, R = 2.45, 1.25
    octo = _circle(R, 8, TAU / 16)
    gal = _circle(1.5, 8, TAU / 16)
    zg = 3.75                                                                                 # gallery floor
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * ct, sy * ct
            ring = [(cx + x, cy + y) for x, y in octo]
            conc.loft([[(cx + x * k, cy + y * k, z) for x, y in octo] for k, z in ((1, z0), (.97, 1.9), (.95, 3.3))],
                      bevel=.04, seg=1)
            conc.loft([[(cx + x * k, cy + y * k, z) for x, y in octo] for k, z in ((.93, 3.2), (1.18, 3.52))], bevel=0)
            a.part('Galleries', 'Concrete').prism([(x, y) for x, y in gal], .26, loc=(cx, cy, zg - .13), axis='Z',
                                                  bevel=.03, seg=1)
            a.part('Parapets', 'Concrete').shell(gal, .55, .14, loc=(cx, cy, zg - .02), bevel=0)
            a.part('Parapet_bands', 'Team').shell(_circle(1.52, 8, TAU / 16), .16, .05, loc=(cx, cy, zg + .28), bevel=0)
            # Slit windows on the three outward faces.
            for k in range(8):
                ang = TAU / 16 + (k + .5) * TAU / 8
                if math.cos(ang) * sx < -.1 or math.sin(ang) * sy < -.1:
                    continue
                p, q = ring[k], ring[(k + 1) % 8]
                m = _qframe((p[0], p[1], z0), (q[0], q[1], z0),
                            (cx + (p[0] - cx) * .97, cy + (p[1] - cy) * .97, 1.9),
                            (cx + (q[0] - cx) * .97, cy + (q[1] - cy) * .97, 1.9), .5, .75)
                _face_box(a, 'Slit_frames', 'Armor', m, (.3, .66, .06), bevel=0, sink=.02)
                _face_box(a, 'Slits', 'Charred', m, (.16, .5, .07), bevel=0, sink=.01)
    # Block faces between the towers: two rows of shuttered windows (a few open and lit).
    lit = {(0, 1, 0), (1, 0, 1), (2, 1, 1), (3, 0, 0)}
    for i in range(4):
        for row, v in enumerate((.36, .74)):
            for col, u in enumerate((.4, .6)):
                if i == 1 and row == 0:
                    continue                                                              # the entrance
                _shuttered_window(a, bface(i, u, v), lit=(i, row, col) in lit)
    # Front face stencil and a Team band under the slab on all four faces.
    _face_box(a, 'Stencils', 'Hazard', bface(0, .5, .55), (.5, .18, .03), bevel=0)
    for i in range(4):
        _face_box(a, 'Wall_bands', 'Team', bface(i, .5, .9), (2.1, .16, .03), bevel=0)
    # Entrance on the right face: blast door in a hazard frame, lamp, barrier.
    m = bface(1, .5, 0.0)
    door = m @ _frame((0, .95, 0), (0, 0, 0))
    _face_box(a, 'Door_frame', 'Armor', door, (1.6, 1.7, .1), bevel=.02, sink=.04)
    _face_box(a, 'Blast_door', 'Team', door, (1.3, 1.52, .14), bevel=.015, sink=.03)
    _face_box(a, 'Door_seam', 'Charred', door, (.04, 1.5, .15), bevel=0, sink=.02)
    for k in range(6):
        _face_box(a, 'Door_hazard', 'SafetyStripe' if k % 2 else 'Charred', m @ _frame((-.75 + k * .3, 1.84, 0),
                                                                                         (0, 0, 0)),
                  (.3, .16, .12), bevel=0, sink=.05)
    caged_lamp(a, '+x', (2.625, 0, 2.1))
    _jersey(a, 3.62, -.3, yaw=R90, length=1.4)
    # Front recess: sandbag wall and flak crates; rear: generator and drums; left: crates and a ladder.
    bags = a.part('Sandbags', 'Sandbag')
    for course in range(2):
        bag_run(bags, rng, (-1.25, -3.6), (1.25, -3.6), .36 + course * .22, (.7, .38, .25), half=course == 1)
    for x in (-.7, .1):
        crate(a, (x, -3.02, .24), size=(.72, .4, .3), yaw=.04)
    crate(a, (-.3, -3.04, .54), size=(.7, .4, .28), yaw=-.06, band=False)
    crate(a, (.85, -3.0, .24), size=(.5, .36, .26), yaw=-.3, band=False)
    generator(a, (0, 3.3, .24), yaw=math.pi, size=(1.9, .9, 1.05))
    for k, (x, y) in enumerate(((1.15, 3.45), (-1.2, 3.5), (-1.15, 2.95))):
        a.part('Drums', 'BarrelRed').cyl(.27, .84, loc=(x, y, .66), seg=10, bevel=0)
        a.part('Drum_rims', 'Steel').cyl(.285, .04, loc=(x, y, .9), seg=10, bevel=0)
    crate(a, (-3.25, .5, .24), size=(.9, .44, .36), yaw=R90 + .05)
    crate(a, (-3.28, .52, .6), size=(.84, .42, .32), yaw=R90 - .06, band=False)
    lx = -2.93
    ladder(a.part('Ladder', 'Steel'), (lx, -.2, .24), roof + .5, R90, width=.44, step=.34, rung=.03)
    for z in (1.0, 2.4):                                                                   # standoffs
        x0 = -(hw - hw * (1 - TP) * (z - z0) / H) + .03
        a.part('Ladder', 'Steel').box((x0 - lx, .04, .04), loc=((lx + x0) / 2, -.2, z), bevel=0)
    # Roof: the gun platform drum with ready-ammunition lockers round it, hatches.
    conc.cyl(1.98, .5, loc=(0, 0, roof + .2), seg=24, bevel=.03, bseg=1)                        # z 3.4 .. 3.9
    for k in range(6):
        ang = R90 + (k - 2.5) * .55 + math.pi
        a.part('Lockers', 'Armor').box((.6, .34, .36), loc=(2.04 * math.cos(ang), 2.04 * math.sin(ang), roof + .17),
                                       rot=(0, 0, ang + R90), bevel=0)
        a.part('Locker_bands', 'Hazard').box((.2, .36, .06),
                                             loc=(2.06 * math.cos(ang), 2.06 * math.sin(ang), roof + .3),
                                             rot=(0, 0, ang + R90), bevel=0)
    a.part('Race', 'Steel').cyl(1.7, .1, loc=(0, 0, roof + .48), seg=24, bevel=0)                 # z 3.78 .. 3.88
    for k in range(24):                                                                        # hazard band
        ang = (k + .5) * TAU / 24
        a.part('Race_band', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.44, .24, .04), loc=(1.855 * math.cos(ang), 1.855 * math.sin(ang), roof + .455), rot=(0, 0, ang + R90),
            bevel=0)
    for x, y in ((-2.25, 0.0), (0.0, 2.3)):
        a.part('Roof_hatches', 'Armor').box((.5, .5, .1), loc=(x, y, roof + .03), bevel=.02, seg=1)
    # Galleries: searchlight (front left), SAM box (front right), radar (rear left), rangefinder (rear right).
    a.part('Searchlight_post', 'Steel').cyl(.12, .4, loc=(-ct, -ct, zg + .18), seg=8, bevel=0)
    _searchlight(a, (-ct, -ct, zg + .38), r=.3, length=.52)
    _moving_pivots(a, {'Searchlight'})
    _sam_box(a, (ct, -ct, zg - .01))
    rx, ry = -ct, ct
    a.part('Radar_pedestal', 'Armor').cyl(.22, .34, loc=(rx, ry, zg + .15), seg=10, bevel=.02, bseg=1)
    r = a.pivot('Radar', (rx, ry, zg + .32))
    yoke = a.part('Radar_yoke', 'Steel', r)
    yoke.cyl(.18, .08, loc=(0, 0, .03), seg=10, bevel=0)
    yoke.box((.3, .26, .3), loc=(0, .12, .2), bevel=.02, seg=1)
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.02, .5), .5, .42, depth=.16, seg=12, tilt=.35)
    yoke.limb((0, -.2, .45), (0, -.62, .66), .03, .03, bevel=0)
    a.part('Radar_feed', 'Lamp', r).box((.07, .07, .07), loc=(0, -.64, .67), bevel=0)
    fx, fy = ct, ct
    a.part('Rangefinder_base', 'Armor').cyl(.26, .48, loc=(fx, fy, zg + .22), seg=10, bevel=.02, bseg=1)
    rf = a.part('Rangefinder', 'Steel')
    rf.cyl(.11, 1.7, loc=(fx, fy, zg + .6), rot=ACROSS, seg=10, bevel=.01, bseg=1)
    for s in (-1, 1):
        a.part('Rangefinder_hoods', 'Team').box((.24, .3, .3), loc=(fx + s * .85, fy, zg + .6), bevel=.03, seg=1)
        a.part('Rangefinder_lens', 'Glass').box((.14, .03, .14), loc=(fx + s * .85, fy - .16, zg + .61), bevel=0)
    a.part('Rangefinder_body', 'Armor').box((.46, .4, .34), loc=(fx, fy + .05, zg + .56), bevel=.03, seg=1)
    _antenna(a, None, fx + .5, fy + .6, zg - .01, 1.3)

    # ---------------------------------------------------------------- quad heavy flak mount
    t = a.pivot('Turret', (0, 0, roof + .53))                                                # z 3.88
    a.part('Turntable', 'Armor', t).cyl(1.6, .14, loc=(0, 0, .05), seg=24, bevel=.02, bseg=1)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.cyl(1.1, .3, loc=(0, 0, .25), seg=16, bevel=.03, bseg=1)                               # carriage ring
    bottom = [(-.6, -1.1), (.6, -1.1), (.75, -.7), (.75, 1.1), (.6, 1.3), (-.6, 1.3), (-.75, 1.1), (-.75, -.7)]
    top = [(-.48, -.45), (.48, -.45), (.64, -.2), (.66, 1.0), (.52, 1.2), (-.52, 1.2), (-.66, 1.0), (-.64, -.2)]
    zb, zt = .36, 1.34
    _house(a.part('Gun_house', 'Team', t), bottom, top, zb, zt, bevel=.05)
    B = [(x, y, zb) for x, y in bottom]
    T = [(x, y, zt) for x, y in top]

    def hface(i, u, v):
        j = (i + 1) % 8
        return _qframe(B[i], B[j], T[i], T[j], u, v)
    m = hface(0, .5, .45)
    _face_box(a, 'House_plates', 'Armor', m, (.86, .6, .08), parent=t, bevel=.015)
    tsteel.bolts([tuple(m @ Vector((dx, dy, .075))) for dx in (-.35, .35) for dy in (-.24, .24)], r=.03, h=.03,
                 rot=m.to_euler('XYZ'), seg=5, bevel=0)
    for i in (2, 6):
        _face_box(a, 'House_plates', 'Armor', hface(i, .5, .5), (1.2, .55, .06), parent=t, bevel=.015)
    tarm.box((.42, .34, .26), loc=(-.26, -.2, zt + .1), bevel=.03, seg=1)                         # sight hood
    a.part('Sight', 'Glass', t).box((.3, .05, .12), loc=(-.26, -.37, zt + .12), bevel=.01, seg=1)
    _hatch(a, .26, .5, zt - .01, .22, parent=t)
    tsteel.box((.5, .06, .05), loc=(0, 1.0, zt + .01), bevel=0)
    _antenna(a, t, -.4, 1.0, zt, 1.1)
    # Loading gear at the rear: rammer tray and ready rounds in racks on the turntable.
    tarm.box((1.1, .36, .5), loc=(0, 1.42, .45), bevel=.03, seg=1)
    a.part('Loading_tray', 'Steel', t).box((.3, .9, .06), loc=(0, 1.35, .74), rot=(-.15, 0, 0), bevel=0)
    for s in (-1, 1):
        shells(a, (s * .95, 1.2, .12), 2, 2, r=.07, h=.62, pitch=.16, parent=t)
        a.part('Rack_frames', 'Armor', t).box((.44, .44, .06), loc=(s * .95, 1.2, .38), bevel=0)
    # Two gun cradles (Pod, Pod_2) with two long barrels each, raised 30 degrees, on trunnions in carriage
    # cheeks. The cradles end just behind the trunnion and an elevating arc (Pod_arc, Pod_2_arc) hangs
    # 0.9 m below it, so the automatic elevation pivot of ModelLibrary (the back of the barrel group, a
    # third of the way up) falls on the trunnion and the cradles pivot where they visibly hinge.
    pitch = math.radians(30)
    rot = (-pitch, 0, 0)
    py, pz = .25, 1.05
    arc = [(.05, .06)] + [(-.9 * math.sin(math.radians(d)), -.9 * math.cos(math.radians(d)))
                          for d in (0, 15, 30, 45, 60)]
    arc.append((-.25, .1))
    tips = []
    n = 0
    for s, pod in ((-1, 'Pod'), (1, 'Pod_2')):
        x = s * 1.08
        at = _axis((x, py, pz), pitch)
        cradle = a.part(pod, 'Team', t)
        cradle.box((.56, 1.42, .5), loc=tuple(at(.59)), rot=rot, bevel=.04, seg=1)             # s -.12 .. 1.3
        cradle.box((.4, 1.0, .1), loc=tuple(at(.7, .29)), rot=rot, bevel=.01, seg=1)           # top plate
        a.part(f'{pod}_arc', 'Armor', t).prism(arc, .06, loc=(s * 1.42, py, pz), axis='X', bevel=0)
        tarm.box((.08, .7, .95), loc=(s * 1.52, py, .595), bevel=.02, seg=1, taper=(1, .5))     # carriage cheek
        tsteel.cyl(.13, .14, loc=(s * 1.57, py, pz), rot=ACROSS, seg=10, bevel=.015, bseg=1)   # trunnion hub
        for side in (-.15, .15):
            n += 1
            suffix = '' if n == 1 else f'_{n}'
            gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
            gun.cyl(.12, .8, loc=tuple(at(1.45, 0, side)), rot=(R90 - pitch, 0, 0), seg=10, bevel=.015, bseg=1)
            gun.cyl(.085, 2.4, loc=tuple(at(2.5, 0, side)), rot=(R90 - pitch, 0, 0), seg=10, bevel=.01, bseg=1)
            gun.cyl(.1, .05, loc=tuple(at(2.9, 0, side)), rot=(R90 - pitch, 0, 0), seg=10, bevel=0)
            brake = a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t)
            brake.lathe([(.08, 0), (.12, .04), (.12, .3), (.07, .3), (.07, .22)], loc=tuple(at(3.66, 0, side)),
                        rot=(R90 - pitch, 0, 0), seg=10)
            brake.cyl(.14, .04, loc=tuple(at(3.8, 0, side)), rot=(R90 - pitch, 0, 0), seg=10, bevel=0)
            tips.append(at(3.96, 0, side))
    a.pivot('Muzzle_main', tuple(sum(tips, Vector()) / len(tips)), t)



# ----------------------------------------------------------------------------- missile_battery
def missile_battery(a):
    """Surface-to-air missile site (9 x 7 m) after the Patriot M901 launching station and the S-300's
    mast-mounted search radar. A four-canister launcher (2 x 2 Team canisters with frame bands, light
    frangible covers, rear umbilicals and stencils) is raised 38 degrees between A-frame cheeks on a Team
    launcher platform on a turntable (`Turret`). The canister group is named Launcher*, so it elevates
    about its trunnions (ModelLibrary's automatic pivot falls on them); `Muzzle_main` is at its front. A
    lattice mast carries a railed platform, a floodlight and a search radar (reflector, feed horn, IFF bar,
    cabin) spinning on `Radar`. A Team equipment shelter with an air conditioner and a lit door, a spare
    canister on skids, cable runs, sandbags and a guard HMG in a sandbag nest (`Mount_mg`) complete it."""
    rng = random.Random(303)
    a.part('Pad', 'Concrete').prism(chamfered(9.0, 7.0, .8), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .24
    # ---------------------------------------------------------------- launcher
    lx, ly = -1.6, .3
    a.part('Plinth', 'Concrete').cyl(1.75, .2, loc=(lx, ly, .3), seg=20, bevel=.03, bseg=1)       # z .2 .. .4
    a.part('Race', 'Steel').cyl(1.58, .06, loc=(lx, ly, .41), seg=20, bevel=0)                  # z .38 .. .44
    for k in range(20):
        ang = (k + .5) * TAU / 20
        a.part('Race_band', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.48, .14, .03), loc=(lx + 1.67 * math.cos(ang), ly + 1.67 * math.sin(ang), .4), rot=(0, 0, ang + R90),
            bevel=0)
    t = a.pivot('Turret', (lx, ly, .42))
    a.part('Turntable', 'Armor', t).cyl(1.5, .14, loc=(0, 0, .05), seg=20, bevel=.02, bseg=1)     # z -.02 .. .12
    team = a.part('Platform', 'Team', t)
    team.box((2.2, 3.4, .42), loc=(0, .55, .33), bevel=.04, seg=1)                              # z .12 .. .54
    tarm = a.part('Platform_armor', 'Armor', t)
    tsteel = a.part('Platform_steel', 'Steel', t)
    for s in (-1, 1):
        tarm.box((.06, 3.1, .28), loc=(s * 1.115, .55, .3), bevel=0)                            # side skirts
        _stowage_bin(a, (s * 1.28, 1.3, .14), (.3, .9, .36), parent=t, latch_side=s)
        for k in range(3):
            a.part('Platform_hazard', 'SafetyStripe' if k % 2 else 'Charred', t).box(
                (.2, .03, .2), loc=(s * (.9 - k * .2), -1.16, .33), bevel=0)
    tarm.box((.8, .5, .22), loc=(-.45, -.75, .62), bevel=.02, seg=1)                             # electronics
    a.part('Platform_panel', 'Glass', t).box((.3, .03, .1), loc=(-.45, -1.015, .64), bevel=0)
    a.part('Platform_lamp', 'Alloy', t).box((.08, .03, .06), loc=(-.15, -1.015, .66), bevel=0)
    tsteel.tube([(-.05, -.7, .56), (.4, -.6, .56), (.55, .2, .56)], .035, seg=5)                # cable
    # Canister group, raised TH, hinged on trunnions (TY, TZ) in two A-frame cheeks.
    TH = math.radians(38)
    L = 4.2
    d = Vector((0, -math.cos(TH), math.sin(TH)))
    u = Vector((0, math.sin(TH), math.cos(TH)))
    P0 = Vector((0, 1.0, .9))                                                               # rear-bottom edge
    C = P0 + d * (L / 2) + u * .85
    box = _frame(C, (-TH, 0, 0))
    rot = (-TH, 0, 0)
    for cx in (-.43, .43):
        for cz in (-.43, .43):
            a.part('Launcher', 'Team', t).box((.8, L, .8), loc=box @ Vector((cx, 0, cz)), rot=rot, bevel=.03, seg=1)
            a.part('Launcher_covers', 'Medical', t).box((.66, .04, .66), loc=box @ Vector((cx, -L / 2 - .01, cz)),
                                                        rot=rot, bevel=.01, seg=1)
            a.part('Launcher_plugs', 'Armor', t).box((.3, .1, .22), loc=box @ Vector((cx, L / 2 + .03, cz)), rot=rot,
                                                     bevel=0)
    frame = a.part('Launcher_frame', 'Armor', t)
    for y in (-L / 2 + .12, -L / 6, L / 6, L / 2 - .12):
        frame.box((1.74, .1, 1.74), loc=box @ Vector((0, y, 0)), rot=rot, bevel=.01, seg=1)
    for s in (-1, 1):
        a.part('Launcher_stencil', 'Hazard', t).box((.03, .9, .22), loc=box @ Vector((s * .84, -1.25, .43)), rot=rot,
                                                    bevel=0)
        a.part('Launcher_lugs', 'Steel', t).box((.1, .1, .08), loc=box @ Vector((s * .55, -L / 2 + .45, .86)), rot=rot,
                                                bevel=0)
    a.pivot('Muzzle_main', tuple(box @ Vector((0, -L / 2 - .05, 0))), t)
    TY, TZ = 1.76, 2.09                                                                  # = the auto pivot
    for s in (-1, 1):
        x = s * 1.0
        tarm.limb((x, .72, .5), (x, TY, TZ), .16, .16, bevel=.02)                               # A-frame
        tarm.limb((x, 2.12, .5), (x, TY, TZ), .14, .14, bevel=.02)
        tsteel.cyl(.15, .34, loc=(s * .98, TY, TZ), rot=ACROSS, seg=10, bevel=.015, bseg=1)       # trunnion hub
        tarm.box((.2, 1.5, .1), loc=(x, 1.42, .58), bevel=0)                                    # foot beam
    # ---------------------------------------------------------------- radar mast
    mx, my = 3.3, 1.4
    a.part('Mast_footing', 'Concrete').box((1.6, 1.6, .45), loc=(mx, my, .42), bevel=.04, seg=1)   # z .2 .. .65
    zp = 4.8
    lattice(a.part('Mast', 'Steel'), mx, my, .63, zp, .62, .34, 4, leg=.14, brace=.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Base_plates', 'Steel').box((.26, .26, .04), loc=(mx + sx * .62, my + sy * .62, .66), bevel=0)
    ladder(a.part('Mast_ladder', 'Steel'), (mx, my - .05, .65), zp + .02, 0.0, width=.36, step=.4, rung=.028)
    a.part('Mast_platform', 'Armor').box((1.5, 1.5, .1), loc=(mx, my, zp + .05), bevel=.02, seg=1)
    a.part('Mast_grating', 'Undercarriage').box((1.3, 1.3, .02), loc=(mx, my, zp + .105), bevel=0)
    e = .7
    loop_rail(a.part('Mast_rail', 'Steel'), [(mx - e, my - e, zp + .1), (mx + e, my - e, zp + .1),
                                             (mx + e, my + e, zp + .1), (mx - e, my + e, zp + .1)],
              h=.8, post=.04, rail=.022, every=.7)
    a.part('Radar_pedestal', 'Steel').cyl(.24, .66, loc=(mx, my, zp + .41), seg=10, bevel=.02, bseg=1)
    a.part('Mast_flood_arm', 'Steel').box((.36, .06, .06), loc=(mx - e - .15, my, zp + .33), bevel=0)
    flood_head(a, (mx - e - .3, my, zp + .62), yaw=-R90, tilt=.5, size=(.5, .24, .34))
    r = a.pivot('Radar', (mx, my, zp + .72))
    a.part('Radar_turntable', 'Armor', r).cyl(.44, .12, loc=(0, 0, .06), seg=12, bevel=.02, bseg=1)
    a.part('Radar_cabin', 'Team', r).box((.7, .6, .5), loc=(0, .18, .37), bevel=.03, seg=1)
    rs = a.part('Radar_struts', 'Steel', r)
    rs.limb((0, .0, .5), (0, -.12, .98), .12, .12, bevel=0)
    _dish(a.part('Radar_reflector', 'Medical', r), (0, -.12, 1.0), 1.3, .6, depth=.26, seg=14, tilt=.25)
    horn = Vector((0, -1.12, .84))
    for p in ((-1.0, -.42, 1.06), (1.0, -.42, 1.06), (0, -.45, .5)):
        rs.limb(p, tuple(horn), .04, .04, bevel=0)
    a.part('Radar_horn', 'Armor', r).box((.28, .24, .22), loc=tuple(horn + Vector((0, -.06, 0))), bevel=.02, seg=1)
    a.part('Radar_feed', 'Lamp', r).box((.16, .03, .1), loc=tuple(horn + Vector((0, .07, 0))), bevel=0)
    a.part('Radar_iff', 'Armor', r).box((1.5, .12, .16), loc=(0, -.3, 1.7), rot=(.25, 0, 0), bevel=.02, seg=1)
    a.part('Radar_beacon', 'Alloy', r).sphere(.07, loc=(0, .3, .66), seg=8, rings=5)
    # ---------------------------------------------------------------- shelter
    sx_, sy_, sw, sd, sh = 2.55, -1.9, 2.8, 1.6, 1.62
    for x in (-1, 1):
        for y in (-1, 1):
            a.part('Shelter_blocks', 'Concrete').box(
                (.36, .36, .22), loc=(sx_ + x * (sw / 2 - .3), sy_ + y * (sd / 2 - .25), .33), bevel=.02, seg=1)
    z0 = .43
    a.part('Shelter', 'Team').box((sw, sd, sh), loc=(sx_, sy_, z0 + sh / 2), bevel=.04, seg=1)
    fr = a.part('Shelter_frame', 'Armor')
    for x in (-1, 1):
        for y in (-1, 1):
            fr.box((.14, .14, sh + .04), loc=(sx_ + x * (sw / 2 - .05), sy_ + y * (sd / 2 - .05), z0 + sh / 2), bevel=0)
    fr.box((sw - .1, .1, .1), loc=(sx_, sy_ - sd / 2 + .04, z0 + sh - .04), bevel=0)
    fr.box((sw - .1, .1, .1), loc=(sx_, sy_ + sd / 2 - .04, z0 + sh - .04), bevel=0)
    fy = sy_ - sd / 2
    a.part('Shelter_door', 'Armor').box((.8, .06, 1.3), loc=(sx_ - .6, fy - .01, z0 + .7), bevel=.015, seg=1)
    a.part('Shelter_fittings', 'Steel').box((.05, .05, .14), loc=(sx_ - .3, fy - .05, z0 + .7), bevel=0)
    a.part('Shelter_steps', 'Steel').box((.9, .4, .06), loc=(sx_ - .6, fy - .2, .34), bevel=0)
    caged_lamp(a, '-y', (sx_ + .0, fy, z0 + 1.4))
    a.part('Shelter_window', 'Glass').box((.5, .05, .3), loc=(sx_ + .55, fy - .005, z0 + 1.0), bevel=0)
    a.part('Shelter_vents', 'Undercarriage').grille(.5, .4, loc=(sx_ + .55, fy - .02, z0 + .45), slats=3, depth=.04,
                                                    thickness=.03)
    a.part('Shelter_stencil', 'Hazard').box((.7, .03, .14), loc=(sx_ + .55, fy - .005, z0 + 1.4), bevel=0)
    ac = a.part('Aircon', 'Fuel')
    ac.box((.4, .9, .8), loc=(sx_ + sw / 2 + .17, sy_, z0 + .8), bevel=.03, seg=1)
    a.part('Aircon_grille', 'Undercarriage').grille(.6, .5, loc=(sx_ + sw / 2 + .38, sy_, z0 + .8), rot=(0, 0, R90),
                                                    slats=4, depth=.04, thickness=.03)
    a.part('Cable_panel', 'Armor').box((.5, .06, .4), loc=(sx_ - .3, sy_ + sd / 2 + .02, z0 + .5), bevel=0)
    _antenna(a, None, sx_ + 1.1, sy_ + .5, z0 + sh, 1.4)
    a.part('Shelter_beacon_base', 'Steel').box((.12, .12, .1), loc=(sx_ - 1.1, sy_ + .5, z0 + sh + .04), bevel=0)
    a.part('Shelter_beacon', 'Alloy').sphere(.08, loc=(sx_ - 1.1, sy_ + .5, z0 + sh + .15), seg=8, rings=5)
    # Cables to the launcher plinth and the mast footing.
    cab = a.part('Cables', 'Rubber')
    cab.tube([(1.2, -1.45, .27), (.6, -1.0, .265), (.12, -.2, .27)], .045, seg=5)
    cab.tube([(3.3, -1.08, .27), (3.45, -.1, .265), (3.35, .58, .28)], .045, seg=5)
    # ---------------------------------------------------------------- spare canister, sandbags, HMG nest
    for x in (.2, 1.5, 2.8):
        a.part('Skids', 'Wood').box((.2, .9, .14), loc=(x, 2.95, .29), bevel=0)
    a.part('Spare_canister', 'Team').box((3.7, .8, .8), loc=(1.5, 2.95, .74), bevel=.03, seg=1)
    for x in (.0, 1.5, 3.0):
        a.part('Spare_bands', 'Armor').box((.1, .86, .86), loc=(x, 2.95, .74), bevel=0)
    a.part('Spare_cover', 'Medical').box((.04, .66, .66), loc=(-.36, 2.95, .74), bevel=0)
    a.part('Spare_stencil', 'Hazard').box((.8, .03, .2), loc=(2.2, 2.54, .9), bevel=0)
    bags = a.part('Sandbags', 'Sandbag')
    for course in range(2):
        bag_run(bags, rng, (-4.15, -1.2), (-4.15, 2.7), .36 + course * .22, (.72, .38, .25), half=course == 1)
    nx, ny = -3.5, -2.35
    for course in range(3):
        bag_arc(bags, rng, .72, R90 + .75, R90 + TAU - .75, .36 + course * .22, size=(.62, .36, .24),
                half=course % 2 == 1, cx=nx, cy=ny)
    a.part('HMG_post', 'LogWood').cyl(.08, .8, loc=(nx, ny, .62), seg=8, bevel=0)
    crate(a, (nx + .25, ny + .1, .24), size=(.34, .22, .2), yaw=.4, band=False)
    wpn.hmg(a, (nx, ny, 1.0), post=.2, ammo=1)
    # Power: a generator set in front of the shelter, cabled to it; crates and a warning sign.
    generator(a, (.2, -2.8, .24), size=(1.6, .8, .95))
    cab.tube([(.95, -2.65, .5), (1.05, -2.5, .27), (1.18, -2.2, .27)], .04, seg=5)
    crate(a, (-3.35, 2.95, .24), size=(.9, .44, .36), yaw=.1)
    crate(a, (-3.3, 2.93, .6), size=(.84, .42, .32), yaw=-.05, band=False)
    hazard_sign(a, (-2.55, 3.15, .24), size=.5, height=1.0)



# ----------------------------------------------------------------------------- shield_generator
def _bushing(a, loc, h=.5, discs=3):
    """Porcelain insulator bushing standing on loc: a white core with sheds and a steel terminal cap."""
    x, y, z = loc
    a.part('Insulators', 'Medical').cyl(.06, h, loc=(x, y, z + h / 2), seg=6, bevel=0)
    for k in range(discs):
        a.part('Insulators', 'Medical').cyl(.12, .04, loc=(x, y, z + .1 + k * (h - .15) / max(1, discs - 1)), seg=6,
                                            bevel=0)
    a.part('Terminals', 'Steel').cyl(.075, .08, loc=(x, y, z + h + .03), seg=6, bevel=0)
    return Vector((x, y, z + h + .06))


def _transformer(a, x, y, s):
    """Step-up transformer on a plinth: an Armor tank with a Team band, radiator fins on the outer side
    (s), a conservator drum, two insulator bushings and a warning plate. Returns the bushing tops."""
    a.part('Plinths', 'Concrete').box((1.6, 1.3, .22), loc=(x, y, .31), bevel=.03, seg=1)               # z .2 .. .42
    a.part('Transformer_tanks', 'Pipe').box((1.2, .9, 1.1), loc=(x, y, .96), bevel=.04, seg=1)           # z .41 .. 1.51
    a.part('Transformer_bands', 'Team').box((1.22, .92, .16), loc=(x, y, 1.3), bevel=0)
    fins = a.part('Radiator_fins', 'Armor')
    for k in range(6):
        fins.box((.3, .04, .84), loc=(x + s * .74, y - .35 + k * .14, .95), bevel=0)
    a.part('Radiator_headers', 'Steel').box((.12, .86, .08), loc=(x + s * .8, y, 1.4), bevel=0)
    a.part('Conservators', 'Armor').cyl(.16, .9, loc=(x - s * .2, y + .3, 1.72), rot=ACROSS, seg=10, bevel=.02, bseg=1)
    a.part('Conservator_legs', 'Steel').box((.06, .06, .24), loc=(x - s * .2, y + .3, 1.55), bevel=0)
    a.part('Warning_plates', 'Hazard').box((.4, .03, .3), loc=(x, y - .455, .9), bevel=0)
    a.part('Warning_marks', 'Charred').box((.06, .03, .16), loc=(x, y - .465, .92), bevel=0)
    return [_bushing(a, (x + dx, y - .15, 1.49)) for dx in (-.3, .3)]


def _pylon(a, x, y, h=3.3):
    """H-frame line pylon on a footing: two steel posts, an X brace, a crossarm with two hanging
    insulator strings and an Alloy warning light. Returns the two conductor points."""
    a.part('Pylon_footings', 'Concrete').box((.5, 1.3, .3), loc=(x, y, .33), bevel=.03, seg=1)
    st = a.part('Pylons', 'Steel')
    for dy in (-.45, .45):
        st.limb((x, y + dy, .44), (x, y + dy * .7, h), .1, .1, bevel=0)
    st.limb((x, y - .42, .9), (x, y + .36, 2.3), .05, .05, bevel=0)
    st.limb((x, y + .43, .9), (x, y - .37, 2.3), .07, .07, bevel=0)
    a.part('Crossarms', 'Armor').box((.14, 1.5, .14), loc=(x, y, h - .1), bevel=.02, seg=1)
    pts = []
    for dy in (-.62, .62):
        a.part('Insulators', 'Medical').cyl(.05, .34, loc=(x, y + dy, h - .33), seg=6, bevel=0)
        for k in range(2):
            a.part('Insulators', 'Medical').cyl(.1, .03, loc=(x, y + dy, h - .26 - k * .14), seg=6, bevel=0)
        pts.append(Vector((x, y + dy, h - .52)))
    a.part('Pylon_lights', 'Alloy').sphere(.07, loc=(x, y, h + .02), seg=8, rings=5)
    return pts


def _sag(p, q, droop=.25, n=6):
    """Points of a cable hanging from p to q."""
    return [tuple(p.lerp(q, k / n) - Vector((0, 0, droop * math.sin(math.pi * k / n)))) for k in range(n + 1)]


def shield_generator(a):
    """Shield generator (7 x 7 m, mast 5.8 m), the objective that keeps a gate's shield up: a grounded
    power plant with a sci-fi core. A hardened concrete generator block (battered walls, a Team blast
    door in a hazard frame, louvres, a lamp, exhaust stacks, a roof bank of cooling fins between
    headers) feeds two step-up transformers (radiator fins, conservators, porcelain bushings) whose
    lines run over H-frame pylons to an emitter mast. On a hazard-banded plinth the mast rises with
    glowing conduits (TeamGlow) to a cage of four struts round a big glowing core (TeamGlow), crowned by
    a finial with a glowing tip; a ring with three emitter nodes spins round the core on `Radar_2`. Thick
    ground cables, a jersey barrier and a warning sign make it read as the prime target."""
    a.part('Pad', 'Concrete').prism(chamfered(7.0, 7.0, .7), .26, loc=(0, 0, .11), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .24
    # ---------------------------------------------------------------- generator block
    bx, by, bw, bd, bh, TP, z0 = 0.0, 2.3, 4.4, 1.9, 1.9, .94, .2
    blk = [(bx - bw / 2, by - bd / 2), (bx + bw / 2, by - bd / 2), (bx + bw / 2, by + bd / 2),
           (bx - bw / 2, by + bd / 2)]

    def shrink(p, f):
        k = 1 - (1 - TP) * f
        return bx + (p[0] - bx) * k, by + (p[1] - by) * k
    a.part('Generator_block', 'Concrete').loft([[(*shrink(p, f), z0 + bh * f) for p in blk] for f in (0, .5, 1)],
                                               bevel=.05, seg=1)                               # z .2 .. 2.1
    top = z0 + bh
    a.part('Block_roof', 'Concrete').box((bw * TP + .3, bd * TP + .3, .2), loc=(bx, by, top + .06), bevel=.04, seg=1)
    roof = top + .16

    def bface(i, u, v):
        p, q = blk[i], blk[(i + 1) % 4]
        pt, qt = shrink(p, 1), shrink(q, 1)
        return _qframe((p[0], p[1], z0), (q[0], q[1], z0), (pt[0], pt[1], top), (qt[0], qt[1], top), u, v)
    door = bface(0, .25, 0) @ _frame((0, .82, 0), (0, 0, 0))
    _face_box(a, 'Door_frame', 'Armor', door, (1.3, 1.64, .1), bevel=.02, sink=.04)
    _face_box(a, 'Blast_door', 'Team', door, (1.0, 1.44, .14), bevel=.015, sink=.03)
    for k in range(5):
        _face_box(a, 'Door_hazard', 'SafetyStripe' if k % 2 else 'Charred',
                  bface(0, .25, 0) @ _frame((-.6 + k * .3, 1.74, 0), (0, 0, 0)), (.3, .16, .12), bevel=0, sink=.05)
    for u in (.62, .84):
        m = bface(0, u, .5)
        _face_box(a, 'Louvre_frames', 'Armor', m, (.8, .7, .08), bevel=0, sink=.03)
        g = m @ _frame((0, 0, .08), (-R90, 0, 0))
        a.part('Louvres', 'Undercarriage').grille(.66, .56, loc=g.to_translation(), rot=g.to_euler('XYZ'), slats=4,
                                                  depth=.05, thickness=.035)
    for u in (.3, .7):                                                                     # rear louvres
        m = bface(2, u, .45)
        _face_box(a, 'Louvre_frames', 'Armor', m, (1.0, .8, .08), bevel=0, sink=.03)
        g = m @ _frame((0, 0, .08), (-R90, 0, 0))
        a.part('Louvres', 'Undercarriage').grille(.86, .66, loc=g.to_translation(), rot=g.to_euler('XYZ'), slats=5,
                                                  depth=.05, thickness=.035)
    for i, w in ((0, bw - .5), (1, bd - .4), (2, bw - .5), (3, bd - .4)):
        _face_box(a, 'Block_band', 'Team', bface(i, .5, .9), (w, .14, .03), bevel=0)
    _face_box(a, 'Block_stencil', 'Hazard', bface(3, .5, .6), (.8, .22, .03), bevel=0)
    _face_box(a, 'Block_stencil', 'Hazard', bface(1, .5, .6), (.8, .22, .03), bevel=0)
    caged_lamp(a, '-y', (bx - 1.1, 1.41, 1.97))
    # Roof: cooling fins between two headers, exhaust stacks, a status lamp.
    fins = a.part('Cooling_fins', 'Steel')
    for k in range(13):
        fins.box((.05, 1.2, .56), loc=(bx - 1.5 + k * .25, by, roof + .27), bevel=0)
    for dy in (-.66, .66):
        a.part('Fin_headers', 'Pipe').cyl(.09, 3.62, loc=(bx, by + dy, roof + .3), rot=ACROSS, seg=8, bevel=0)
    for dx in (-1.85, 1.85):
        a.part('Fin_frames', 'Armor').box((.14, 1.5, .7), loc=(bx + dx, by, roof + .33), bevel=.02, seg=1)
    for x in (1.1, 1.45):
        a.part('Exhausts', 'Steel').cyl(.1, 1.0, loc=(x, by + .95, roof + .45), seg=8, bevel=0)
        a.part('Soot', 'Charred').cyl(.115, .12, loc=(x, by + .95, roof + .9), seg=8, bevel=0)
    # ---------------------------------------------------------------- transformers, pylons, lines
    mx, my = 0.0, -.6
    tops = {}
    for s in (-1, 1):
        tops[s] = _transformer(a, s * 2.3, -2.35, s)
    lines = a.part('Lines', 'Rubber')
    for s in (-1, 1):
        pts = _pylon(a, s * 2.75, -.3)
        near = min(tops[s], key=lambda p: (p - pts[0]).length)
        lines.tube(_sag(near, pts[0], .08, 3), .025, seg=4)
        for k, p in enumerate(pts):
            q = Vector((mx + s * .3, my + (k - .5) * .3, 2.55 + k * .12))
            lines.tube(_sag(p, q, .18), .025, seg=4)
            a.part('Line_terminals', 'Armor').box((.14, .14, .16), loc=(mx + s * .35, q.y, q.z), bevel=0)
        far = max(tops[s], key=lambda p: (p - pts[0]).length)
        lines.tube(_sag(far, pts[1], .1, 3), .025, seg=4)
    # ---------------------------------------------------------------- emitter mast
    plinth = _circle(1.05, 8, TAU / 16)
    a.part('Mast_plinth', 'Concrete').prism(plinth, .45, loc=(mx, my, .425), axis='Z', bevel=.04, seg=1,
                                            taper=.92)                                         # z .2 .. .65
    for k in range(16):
        ang = (k + .5) * TAU / 16
        a.part('Plinth_hazard', 'SafetyStripe' if k % 2 else 'Charred').box(
            (.28, .16, .03), loc=(mx + .78 * math.cos(ang), my + .78 * math.sin(ang), .65), rot=(0, 0, ang + R90),
            bevel=0)
    col = a.part('Mast_column', 'Team')
    col.lathe([(.55, .6), (.5, .8), (.42, 1.2), (.34, 2.6), (.3, 3.12), (0, 3.12)], loc=(mx, my, 0), seg=12)
    rings = a.part('Mast_rings', 'Steel')
    for z, r in ((.85, .52), (1.9, .41), (2.75, .36)):
        rings.cyl(r, .1, loc=(mx, my, z), seg=12, bevel=0)
    glow = a.part('Conduits', 'TeamGlow')
    for k in range(4):
        ang = k * R90 + TAU / 8
        c, s_ = math.cos(ang), math.sin(ang)
        glow.tube([(mx + r * c, my + r * s_, z) for r, z in ((.515, .8), (.44, 1.2), (.35, 2.74))], .035, seg=4)
    a.part('Collar', 'Steel').cyl(.42, .16, loc=(mx, my, 3.12), seg=12, bevel=.02, bseg=1)       # z 3.04 .. 3.2
    # Core cage: four struts from the collar round the core to the crown, the core, the finial.
    cage = a.part('Cage', 'Steel')
    zc = 3.98
    for k in range(4):
        ang = k * R90
        c, s_ = math.cos(ang), math.sin(ang)
        cage.tube([(mx + .3 * c, my + .3 * s_, 3.15), (mx + .54 * c, my + .54 * s_, 3.6),
                   (mx + .54 * c, my + .54 * s_, 4.3), (mx + .26 * c, my + .26 * s_, 4.72)], .045, seg=6)
    a.part('Core', 'TeamGlow').sphere((.48, .48, .62), loc=(mx, my, zc), seg=12, rings=8)
    a.part('Core_sockets', 'Armor').cyl(.24, .2, loc=(mx, my, 3.32), seg=10, bevel=.02, bseg=1)
    crown = a.part('Crown', 'Armor')
    crown.cyl(.3, .14, loc=(mx, my, 4.74), seg=12, bevel=.02, bseg=1)
    crown.cyl(.2, .1, loc=(mx, my, 4.62), r2=.28, seg=10, bevel=0)
    a.part('Finial', 'Steel').cyl(.06, .9, loc=(mx, my, 5.25), r2=.035, seg=6, bevel=0)
    for k in range(3):
        ang = k * TAU / 3
        a.part('Finial', 'Steel').limb((mx + .2 * math.cos(ang), my + .2 * math.sin(ang), 4.8),
                                       (mx + .3 * math.cos(ang), my + .3 * math.sin(ang), 5.2), .04, .04, bevel=0)
    a.part('Finial_tip', 'TeamGlow').sphere(.1, loc=(mx, my, 5.74), seg=8, rings=6)
    # Spinning emitter ring (Radar_2): a rotating collar, three arms, the ring and three emitter nodes
    # aimed at the core.
    r2 = a.pivot('Radar_2', (mx, my, 3.2))
    a.part('Ring_collar', 'Armor', r2).cyl(.78, .14, loc=(0, 0, .05), seg=16, bevel=.02, bseg=1)
    arms = a.part('Ring_arms', 'Steel', r2)
    R_ = 1.12
    for k in range(3):
        ang = k * TAU / 3 + TAU / 12
        c, s_ = math.cos(ang), math.sin(ang)
        arms.limb((.66 * c, .66 * s_, .08), (R_ * c, R_ * s_, .78), .08, .08, bevel=0)
    a.part('Emitter_ring', 'Armor', r2).torus(R_, .07, loc=(0, 0, .75), seg=24, ring=6)
    a.part('Emitter_glow', 'TeamGlow', r2).torus(R_ - .06, .035, loc=(0, 0, .75), seg=24, ring=4)
    for k in range(3):
        ang = k * TAU / 3 + TAU / 12 + TAU / 6
        m = _frame((R_ * math.cos(ang), R_ * math.sin(ang), .75), (0, 0, ang + R90))
        a.part('Emitter_nodes', 'Team', r2).box((.26, .22, .26), loc=m @ Vector((0, 0, 0)), rot=(0, 0, ang + R90),
                                                bevel=.02, seg=1)
        a.part('Emitter_lenses', 'TeamGlow', r2).box((.16, .04, .16), loc=m @ Vector((0, .12, 0)),
                                                     rot=(0, 0, ang + R90), bevel=0)
    # ---------------------------------------------------------------- ground cables, barrier, sign
    cab = a.part('Cables', 'Rubber')
    for dx in (-.55, .55):
        cab.tube([(bx + dx, by - bd / 2 - .05, .5), (bx + dx, by - bd / 2 - .3, .3), (mx + dx * .9, my + .95, .3),
                  (mx + dx * .7, my + .8, .55)], .07, seg=6)
    for s in (-1, 1):
        cab.tube([(s * (bw / 2 + .02), by - .5, .45), (s * 2.95, by - .7, .29), (s * 3.15, -.2, .29),
                  (s * 3.15, -1.2, .29), (s * 2.7, -1.55, .5), (s * 2.6, -1.88, .8)], .06, seg=6)
        a.part('Cable_boxes', 'Armor').box((.2, .5, .4), loc=(s * (bw / 2 + .06), by - .5, .5), bevel=.02, seg=1)
    _jersey(a, 0, -3.05, length=1.8)
    hazard_sign(a, (1.25, -3.1, .24), size=.5, height=1.0)


# name: (builder, Asset options)
BUILDERS = {
    'heavy_turret': (heavy_turret, dict(ao_distance=.9, grime_height=.6)),
    'flak_tower': (flak_tower, dict(ao_distance=.9, grime_height=.6)),
    'missile_battery': (missile_battery, dict(ao_distance=.8, grime_height=.6)),
    'shield_generator': (shield_generator, dict(ao_distance=.8, grime_height=.5)),
}
