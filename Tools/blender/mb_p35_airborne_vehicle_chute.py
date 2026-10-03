"""Prompt 35 wave 11 (lane C): the airborne vehicle under its parachutes, rebuilt (spec: Tools/blender/specs/airborne_vehicle_chute.json).

The parachute variant of `airborne_vehicle`: it calls lane B's wave 6 builder (mb_p35_airborne_vehicle, the BMD-4M)
unchanged, so the vehicle, its node names and its pivots are the same as the ground model's, and adds the drop rig
of a Soviet / Russian heavy airdrop (the P-7 / PBS-950 platform under an MKS-350-9 multi-canopy system; the old
file's 9 x 9 x 11 m with the canopies 8-10 m up): the platform deck with its side rails, skid beams and the
honeycomb crush pads under the vehicle, the tie-down straps from the vehicle to the deck, the two ground-contact
probes hanging below, team stripes; four sling legs up to the central link, the risers to three confluences, eight
suspension lines to each canopy's skirt; three canopies splayed outwards, each a thin shell with its gore seams,
the reinforced skirt hem and the apex vent ring.

Runtime nodes: the vehicle's (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`,
`Point_exhaust`, `Point_fire`); old rig names kept (`Pallet`, `Canopies`, `Risers`, `Team_bands`). Metres, +Z up,
-Y front, +X left; the origin at the vehicle's bottom centre (the game draws it falling).
"""
import math
import re

import bpy

import frontier_kit as kit
import mb_kit27 as k
import mb_kit35 as K
import mb_p35_airborne_vehicle as AV

R90 = math.pi / 2
TAU = math.tau
LINK = (0, 0, 3.4)          # the central link where the sling legs meet
CANOPY_R = 2.3
RING_R = 2.45               # canopy centres from the axis
SKIRT_Z = 8.45
SPLAY = math.radians(14)


def _platform(a):
    pal = a.part('Pallet', 'Wood')
    k.block(pal, (2.9, 5.5, .14), loc=(0, .0, -.12), chamfer=.02)
    rails = a.part('Pallet_rails', 'Steel')
    for s in (-1, 1):
        rails.box((.08, 5.5, .12), loc=(s * 1.45, 0, -.08), bevel=0)
        a.part('Team_bands', 'Team').box((.01, 1.2, .08), loc=(s * 1.495, 0, -.08), bevel=0)
    for y in (-2.75, 2.75):
        rails.box((2.9, .08, .12), loc=(0, y, -.08), bevel=0)
    sk = a.part('Skid_beams', 'Steel')
    for x in (-1.1, 0, 1.1):
        sk.box((.14, 5.4, .1), loc=(x, 0, -.24), bevel=0)
    pads = a.part('Crush_pads', 'Crate')
    for x in (-.6, .6):
        for y in (-1.6, -.5, .6, 1.7):
            k.block(pads, (.7, .75, .12), loc=(x, y, -.0), chamfer=.01)
    # Tie-down straps from the hull's lifting points to the deck edge.
    st = a.part('Kit_straps', 'Canvas')
    for sx in (-1, 1):
        for y in (-1.8, 1.8):
            st.tube([(sx * .95, y, .7), (sx * 1.35, y * 1.15, -.04)], .025, seg=4)
    # Two ground-contact probes hanging below the platform.
    pr = a.part('Probes', 'Steel')
    for y in (-2.2, 2.2):
        pr.tube([(1.2, y, -.28), (1.2, y, -.85)], .02, seg=4)
        pr.cyl(.08, .03, loc=(1.2, y, -.87), seg=8, bevel=0)


def _canopy(a, centre, tilt_dir):
    """One canopy: a thin shell (outer up, inner back down) with gores, hem and vent ring, splayed outwards."""
    cx, cy = centre
    rot = K.rot_to((tilt_dir[0] * math.sin(SPLAY), tilt_dir[1] * math.sin(SPLAY), math.cos(SPLAY)))
    loc = (cx, cy, SKIRT_Z)
    R = CANOPY_R
    outer = [(R, 0), (R * .98, .45), (R * .88, .95), (R * .68, 1.42), (R * .4, 1.72), (R * .13, 1.84)]
    inner = [(r * .985 - .02, z - .03) for r, z in reversed(outer)]
    k.ring(a.part('Canopies', 'Canvas'), outer + inner, loc=loc, rot=rot, seg=16, worn=(2,))
    m = K.frame(loc, rot)
    gores = a.part('Canopy_gores', 'Undercarriage')
    for i in range(8):
        u = i * TAU / 8 + TAU / 32
        c, s = math.cos(u), math.sin(u)
        pts = [K._at(m, (c * r * 1.01, s * r * 1.01, z + .01)) for r, z in outer]
        gores.tube(pts, .022, seg=3, caps=False)
    k.ring(a.part('Canopy_hem', 'Team'), [(R * .99, -.02), (R * 1.03, -.02), (R * 1.03, .12), (R * .99, .12)],
           loc=loc, rot=rot, seg=16)
    k.ring(a.part('Canopy_hem', 'Team'), [(R * .11, 1.82), (R * .16, 1.82), (R * .16, 1.88), (R * .11, 1.88)],
           loc=loc, rot=rot, seg=10)
    # Suspension lines to the confluence, then the riser to the central link.
    conf = (cx * .45, cy * .45, 5.6)
    lines = a.part('Risers', 'Undercarriage')
    for i in range(8):
        u = i * TAU / 8
        skirt = K._at(m, (math.cos(u) * R * 1.0, math.sin(u) * R * 1.0, .02))
        lines.tube([skirt, conf], .02, seg=3, caps=False)
    lines.tube([conf, LINK], .05, seg=4)
    a.part('Kit_steel', 'Steel').cyl(.07, .1, loc=conf, seg=6, bevel=0)


def _rig(a):
    """Sling legs to the platform's corners, the link, three canopies."""
    sl = a.part('Slings', 'Canvas')
    for sx in (-1, 1):
        for sy in (-1, 1):
            sl.tube([LINK, (sx * 1.35, sy * 2.6, .0)], .045, seg=4)
    k.lathe(a.part('Kit_steel', 'Steel'), [(.0, -.12), (.14, -.08), (.14, .08), (0, .12)], loc=LINK, seg=8)
    for j in range(3):
        u = j * TAU / 3
        d = (math.cos(u), math.sin(u))
        _canopy(a, (d[0] * RING_R, d[1] * RING_R), d)


# Parts kept apart when the static fittings are merged: the runtime's names, the old file's names, the rig.
KEEP = re.compile(r'^(Hull|Tracks|Track_links|Sprockets|Tyres|Wheels|Hubs|Pallet|Canopies|Risers|Team_bands|Turret_body|'
                  r'Coax|Mantlet|Pallet_rails|Skid_beams|Crush_pads|Kit_straps|Probes|Slings|Canopy_gores|Canopy_hem)$')


def _merge_static(a):
    """Join the parts that share a material and a pivot into one mesh each (the vehicle's 52 renderers plus the rig
    would pass the air class's 44-renderer cap); runtime-named and KEEP parts stay their own meshes."""
    groups = {}
    for key in list(a.order):
        name, mat, parent = key
        if KEEP.match(name) or kit.RUNTIME.match(name) or kit.RIG.match(name):
            continue
        groups.setdefault((mat, parent), []).append(key)
    for (mat, parent), keys in groups.items():
        if len(keys) < 2:
            continue
        target = a.shapes[keys[0]]
        for key in keys[1:]:
            me = bpy.data.meshes.new('merge_tmp')
            a.shapes[key].bm.to_mesh(me)
            target.bm.from_mesh(me)
            bpy.data.meshes.remove(me)
            a.shapes[key].bm.free()
            del a.shapes[key]
            a.order.remove(key)


def airborne_vehicle_chute(a, detail=False):
    """The airborne vehicle under its parachutes: the ground model's builder plus the drop rig."""
    AV.airborne_vehicle(a)
    _platform(a)
    _rig(a)
    k.clean(a)
    _merge_static(a)


BUILDERS = {
    'airborne_vehicle_chute': (airborne_vehicle_chute, dict(ao_distance=.5, grime_height=.55)),
}
