"""Prompt 35 wave 2 (lane A): the logistics station and the airfield pad with its two branches, rebuilt from scratch
each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)".

- logistics_station (the sheet: a container yard and a forklift; unit_refs: field fuel tanks lying in an earth
  berm): an Accord supply depot on a precast pad: a 20 ft and a 10 ft container (ribs, doors, locking bars, Team
  stripes), two fuel tanks on saddles inside a sloped earth bund with the pump skid, dispenser and hoses, a forklift
  (lean tyres from kit35.tread_wheel) lifting a pallet, pallets of crates and jerrycans under a camouflage net,
  fuel drums, a sandbag corner, a floodlight, a guyed antenna mast and a flag pole. `Point_fire` (kept) at the pump.
- helipad (airfield; the sheet: a flat concrete pad with paint marks and lights, 10 x 10 x 0.1 m): a precast pad
  with a 45-degree kerb, slab joints, the touchdown ring, the H, edge stripes, flush edge lights and tie-down rings,
  drain grates; kept flat (passable, and its height stays within 10 % of the old 0.115 m).
- helipad_a (airfield.hangar; unit_refs a field aircraft shelter): the pad with a fabric clamshell shelter on its
  rear: steel arches, the canvas skin, its end curtain drawn back, ballast blocks, a tool cart and a work light.
- helipad_b (airfield.service; unit_refs FARP): the pad with the forward arming and refuelling point: two pillow
  fuel bladders in a sandbag bund, the pump unit and hose reels, a rocket rack and ammunition boxes, an extinguisher
  trolley and a windsock.

Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and the wave's lean helpers; no other model's builder.
Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau


def _net(a, poles, mid, garnish):
    for (x, y, z0, h) in poles:
        a.part('Net_poles', 'Wood').cyl(.04, h, loc=(x, y, z0 + h / 2), seg=5, bevel=0)
    pts = [(x, y, z0 + h) for (x, y, z0, h) in poles]
    tris = []
    for i in range(len(pts)):
        tris += [pts[i], pts[(i + 1) % len(pts)], mid]
    n = len(pts)
    a.part('Camo_net', 'Canvas').mesh(tris, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(n)])
    a.part('Camo_net', 'Canvas').mesh(tris, [(3 * i, 3 * i + 2, 3 * i + 1) for i in range(n)])
    for (x, y, z) in garnish:
        a.part('Camo_garnish', 'Foliage').box((.55, .4, .03), loc=(x, y, z), rot=(.12, .1, x + y), bevel=0)


def _container(a, loc, length, yaw=0.0, mat='ContainerBlue'):
    """An ISO container standing on loc (x, y, z of its floor centre) along Y (yaw turns it): the box with its roof,
    the corrugation ribs, the doors at +Y with locking bars, the corner castings, a Team stripe."""
    x, y, z = loc
    w, h = 2.44, 2.59
    c, s = math.cos(yaw), math.sin(yaw)

    def at(dx, dy, dz):
        return (x + dx * c - dy * s, y + dx * s + dy * c, z + dz)
    W.slab(a.part('Shelter', mat), (w, length, h - .06), (x, y, z), caps=(False, False), rot=(0, 0, yaw))
    k.block(a.part('Roof', mat), (w + .02, length + .02, .08), loc=at(0, 0, h - .04), rot=(0, 0, yaw), chamfer=0)
    ribs = a.part('Container_ribs', 'Undercarriage')
    n = int(length / .55)
    for i in range(1, n):
        dy = -length / 2 + i * length / n
        for sx in (-1, 1):
            ribs.box((.03, .06, h - .3), loc=at(sx * (w / 2 + .012), dy, h / 2), rot=(0, 0, yaw), bevel=0)
    for sx in (-1, 1):
        a.part('Locking_bars', 'Steel').box((.04, .03, h - .2), loc=at(sx * .35, length / 2 + .02, h / 2),
                                            rot=(0, 0, yaw), bevel=0)
        a.part('Locking_bars', 'Steel').box((.04, .03, h - .2), loc=at(sx * .85, length / 2 + .02, h / 2),
                                            rot=(0, 0, yaw), bevel=0)
    a.part('Door_seams', 'Undercarriage').box((.02, .02, h - .1), loc=at(0, length / 2 + .015, h / 2),
                                              rot=(0, 0, yaw), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for zz in (.08, h - .08):
                a.part('Corner_castings', 'Steel').box((.18, .18, .16), loc=at(sx * (w / 2 - .08),
                                                                              sy * (length / 2 - .08), zz),
                                                       rot=(0, 0, yaw), bevel=0)
    a.part('Team_band', 'Team').box((.02, length * .9, .2), loc=at(w / 2 + .03, 0, h - .5), rot=(0, 0, yaw), bevel=0)
    rr = a.part('Roof_ribs', 'Undercarriage')
    for i in range(1, int(length / .6)):
        rr.box((w - .1, .05, .012), loc=at(0, -length / 2 + i * .6, h + .005), rot=(0, 0, yaw), bevel=0)
    a.part('Team_band', 'Team').box((.02, length * .9, .2), loc=at(-w / 2 - .03, 0, h - .5), rot=(0, 0, yaw),
                                    bevel=0)


def _forklift(a, loc, yaw=0.0):
    """A rough-terrain forklift facing -Y: body, counterweight, overhead guard, mast with forks carrying a pallet of
    boxes, four lean tyres (kit35.tread_wheel), seat, exhaust, beacon."""
    x, y, z = loc
    k.block(a.part('Forklift_body', 'CraneYellow'), (1.2, 2.0, .7), loc=(x, y, z + .6), chamfer=.05)
    k.block(a.part('Forklift_body', 'CraneYellow'), (1.2, .5, .5), loc=(x, y + .85, z + 1.15), chamfer=.06)
    g = a.part('Forklift_guard', 'Steel')
    for (dx, dy) in ((-.5, -.4), (.5, -.4), (-.5, .55), (.5, .55)):
        g.box((.06, .06, 1.2), loc=(x + dx, y + dy, z + 1.55), bevel=0)
    g.box((1.1, 1.05, .05), loc=(x, y + .07, z + 2.15), bevel=0)
    for dx in (-.4, -.15, .1, .35):
        g.box((.04, 1.0, .04), loc=(x + dx, y + .07, z + 2.19), bevel=0)
    k.block(a.part('Seats', 'Rubber'), (.45, .4, .15), loc=(x, y + .25, z + 1.0), chamfer=.02)
    for sx in (-1, 1):
        a.part('Forklift_mast', 'Undercarriage').box((.1, .12, 2.3), loc=(x + sx * .4, y - 1.1, z + 1.3), bevel=0)
    a.part('Forklift_mast', 'Undercarriage').box((.9, .1, .1), loc=(x, y - 1.1, z + 2.4), bevel=0)
    fk = a.part('Forks', 'Steel')
    fk.box((.9, .1, .5), loc=(x, y - 1.2, z + .85), bevel=0)
    for sx in (-1, 1):
        fk.box((.12, 1.1, .05), loc=(x + sx * .3, y - 1.8, z + .62), bevel=0)
    a.part('Pallets', 'Wood').box((1.1, 1.1, .12), loc=(x, y - 1.8, z + .7), bevel=0)
    W.stack(a, (x - .25, y - 1.8, z + .76), n=2, size=(.5, .9, .3), yaw=R90, seed=50)
    W.stack(a, (x + .3, y - 1.8, z + .76), n=1, size=(.5, .9, .3), yaw=R90, seed=51)
    for (dy, r) in ((-.65, .42), (.7, .38)):
        for sx in (-1, 1):
            K.tread_wheel(a, (x + sx * .62, y + dy, z + r), r, .3, sx, seg=12)
    a.part('Exhaust', 'Steel').cyl(.04, .5, loc=(x - .45, y + .8, z + 1.65), seg=6, bevel=0)
    K.beacon(a, (x, y + .07, z + 2.2), r=.07)


def logistics_station(a):
    """logistics_station: the field supply depot (see the module docstring)."""
    G = .1
    k.extrude(a.part('Base', 'Concrete'), [(-4.0, -5.0), (3.2, -5.0), (4.0, -4.2), (4.0, 5.0), (-4.0, 5.0)], G,
              loc=(0, 0, G / 2), axis='Z', corner=.05, taper=(.985, .985), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-4, 5):
        j.box((7.9, .03, .01), loc=(0, i * 1.1, G + .003), bevel=0)
    for i in range(-3, 4):
        j.box((.03, 9.9, .01), loc=(i * 1.1, 0, G + .003), bevel=0)
    st = a.part('Stains', 'Charred')
    for (x, y, w, r) in ((-2.5, -2.2, 1.0, .3), (0, -3.5, .8, 1.0), (.6, -1.2, .7, 2.0), (-2.2, .4, .9, .7)):
        st.box((w, w * .6, .006), loc=(x, y, G + .004), rot=(0, 0, r), bevel=0)
    # Containers on the left: a 20 ft along the side, a 10 ft at the rear.
    _container(a, (2.65, -1.3, G), 6.06)
    _container(a, (2.65, 3.4, G), 2.99, mat='ContainerRed')
    # The fuel bund on the right: sloped earth walls round two tanks on saddles, the pump skid and dispenser.
    bx0, bx1, by0, by1 = -3.9, -1.0, -.8, 4.7
    bund = a.part('Berm', 'Dirt')
    prof = [(-.45, 0), (.45, 0), (.15, .7), (-.15, .7)]
    k.extrude(bund, prof, by1 - by0, loc=(bx0 + .45, (by0 + by1) / 2, G), rot=(0, 0, R90), axis='X',
              caps=(False, False))
    k.extrude(bund, prof, by1 - by0, loc=(bx1 - .45, (by0 + by1) / 2, G), rot=(0, 0, R90), axis='X',
              caps=(False, False))
    k.extrude(bund, prof, bx1 - bx0, loc=((bx0 + bx1) / 2, by0 + .45, G), axis='X', caps=(True, True))
    k.extrude(bund, prof, bx1 - bx0, loc=((bx0 + bx1) / 2, by1 - .45, G), axis='X', caps=(True, True))
    for x in (-3.0, -1.95):
        k.lathe(a.part('Fuel_tanks', 'Fuel'), [(0, -2.0), (.45, -1.97), (.55, -1.85), (.55, 1.85), (.45, 1.97),
                                               (0, 2.0)], loc=(x, 1.95, G + .75), rot=(R90, 0, 0), seg=12,
                worn=(2, 3))
        for y in (.6, 1.95, 3.3):
            a.part('Saddles', 'Concrete').box((.9, .25, .3), loc=(x, y, G + .15), bevel=0)
            a.part('Tank_straps', 'Steel').cyl(.565, .06, loc=(x, y, G + .75), rot=(R90, 0, 0), seg=8, bevel=0)
        a.part('Tank_hatches', 'Steel').cyl(.18, .08, loc=(x, 1.2, G + 1.32), seg=8, bevel=0)
        a.part('Tank_vents', 'Steel').cyl(.04, .4, loc=(x, 2.9, G + 1.5), seg=6, bevel=0)
    a.part('Hazard_marks', 'Hazard').box((2.2, .03, .2), loc=(-2.45, by0 + .02, G + .45), rot=(.4, 0, 0), bevel=0)
    for x in (-3.0, -1.95):
        for y in (.0, 3.9):
            a.part('Tank_bands', 'Hazard').cyl(.56, .12, loc=(x, y, G + .75), rot=(R90, 0, 0), seg=8, bevel=0)
    # A wire fence along the front and the right edge, its gate gap at the forklift lane.
    K.wire_fence(a, [(-3.95, -1.0, G), (-3.95, -4.95, G), (-1.6, -4.95, G)], h=1.5, post=.75, strands=3,
                 concertina=False)
    K.wire_fence(a, [(1.4, -4.95, G), (3.95, -4.95, G)], h=1.5, post=.75, strands=3, concertina=False)
    k.block(a.part('Pump_skid', 'Armor'), (1.4, .9, .7), loc=(-2.4, -1.85, G + .35), chamfer=.04)
    K.grille(a, (-2.4, -2.31, G + .4), .9, .4, facing=(0, -1, 0), slats=4)
    k.block(a.part('Dispenser', 'BarrelRed'), (.5, .4, 1.3), loc=(-1.3, -1.9, G + .65), chamfer=.03)
    a.part('Glass', 'Glass').box((.3, .02, .2), loc=(-1.3, -2.11, G + 1.05), bevel=0)
    hz = a.part('Hoses', 'Rubber')
    hz.tube([(-2.4, -1.4, G + .5), (-2.4, -.9, G + .9), (-2.4, -.3, G + 1.0)], .05, seg=5)
    hz.tube([(-1.3, -2.12, G + .8), (-.9, -2.6, G + .5), (-1.1, -3.0, G + .05), (-1.8, -3.2, G + .03)], .035, seg=5)
    a.pivot('Point_fire', (-2.4, -2.0, 1.6))
    # The forklift with its load, pallets under a camouflage net, jerrycans, drums.
    _forklift(a, (.2, -2.6, G))
    for (x, y) in ((-.2, .8), (-.2, 2.2), (1.0, 3.6)):
        a.part('Pallets', 'Wood').box((1.1, 1.1, .12), loc=(x, y, G + .06), bevel=0)
    for (x, y, n, sd) in ((-.45, .8, 3, 52), (.05, .8, 2, 53), (-.2, 2.2, 3, 54), (1.0, 3.6, 2, 55)):
        W.stack(a, (x, y, G + .12), n=n, size=(.5, .95, .28), yaw=R90, seed=sd)
    for i in range(4):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (-.75 + i * .22, 3.4, G), rot=(0, 0, R90))
    for (x, y) in ((.6, 4.5),):
        K.fuel_drum(a.part('Fuel_drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (x, y, G), r=.28, h=.85)
    _net(a, [(-1.0, -.1, G, 2.6), (1.3, -.1, G, 2.4), (1.3, 3.0, G, 2.5), (-1.0, 3.0, G, 2.7)], (.15, 1.45, G + 2.1),
         [(-.5, .3, G + 2.4), (.8, .4, G + 2.3), (.7, 2.5, G + 2.35), (-.5, 2.6, G + 2.45)])
    # A sandbag corner and the floodlight at the front, the guyed antenna mast and the flag at the rear right.
    W.bags(a, [(-3.9, -3.3, G), (-3.9, -4.9, G), (-2.3, -4.9, G)], layers=2, bag=(.55, .3, .17), seed=56)
    K.floodlight(a, (-.9, -4.7, G), facing=(.3, 1, -.5), pole=3.0)
    mx, my = -3.5, 5.2 - .55
    a.part('Mast', 'Steel').cyl(.06, 3.2, loc=(mx, my, G + 1.6), seg=8, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (mx, my, G + 3.2), h=.25, r=.03)
    a.part('Antennas', 'Steel').box((.9, .04, .04), loc=(mx, my, G + 2.9), bevel=0)
    for dx in (-.4, .4):
        a.part('Antennas', 'Steel').box((.03, .03, .5), loc=(mx + dx, my, G + 3.1), bevel=0)
    for (x, y) in ((-3.9, 3.8), (-2.6, 4.9)):
        a.part('Guy_wires', 'Steel').tube([(mx, my, G + 2.9), (x, y, G)], .007, seg=3)
    k.block(a.part('Radio_box', 'Armor'), (.4, .3, .45), loc=(-3.0, 4.75, G + .22), chamfer=.02)
    a.part('Flag_pole', 'Steel').cyl(.025, 3.3, loc=(3.75, -4.7, G + 1.65), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.03, .7, .45), loc=(3.75, -4.35, G + 3.1), rot=(0, 0, .1), bevel=0)
    for i in range(8):
        u = i * TAU / 8
        K.dust(a, (math.cos(u) * 3.6, math.sin(u) * 4.5, G), radius=1.4, k=.3)
    k.clean(a)


# ============================================================================= the airfield pad and branches
PADH = .095


def pad(a, apron=False):
    """The precast pad: a 45-degree kerb, slab joints, touchdown ring, the H, edge stripes, flush lights, tie-downs,
    drain grates (common to the three)."""
    k.extrude(a.part('Base', 'Concrete'), [(-5.0, -5.0), (5.0, -5.0), (5.0, 3.8), (3.8, 5.0), (-5.0, 5.0)], PADH,
              loc=(0, 0, PADH / 2), axis='Z', corner=.15, taper=(.97, .97), caps=(False, True))
    z = PADH + .003
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-5, 6):
        j.box((9.6, .04, .006), loc=(0, i * .9, z), bevel=0)
        j.box((.04, 9.6, .006), loc=(i * .9, 0, z), bevel=0)
    # Approach arrows at the front and the pad's number block.
    arr = a.part('Paint_yellow', 'Hazard')
    for dx in (-1.3, 1.3):
        arr.box((.25, 1.2, .006), loc=(dx, -4.2, z + .001), bevel=0)
        for s_ in (-1, 1):
            arr.box((.2, .7, .006), loc=(dx + s_ * .22, -3.5, z + .001), rot=(0, 0, s_ * .6), bevel=0)
    for (x, y, w, d) in ((2.0, 3.9, .6, .15), (2.0, 4.25, .6, .15), (2.25, 4.08, .15, .5), (1.6, 4.08, .15, .5)):
        a.part('Paint_white', 'PlasterWhite').box((w, d, .006), loc=(x, y, z + .001), bevel=0)
    paint = a.part('Paint_white', 'PlasterWhite')
    ring = [(math.cos(t) * 3.4, math.sin(t) * 3.4) for t in (i * TAU / 32 for i in range(32))]
    for i in range(32):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % 32]
        paint.box((math.hypot(x1 - x0, y1 - y0) + .02, .3, .006), loc=((x0 + x1) / 2, (y0 + y1) / 2, z + .001),
                  rot=(0, 0, math.atan2(y1 - y0, x1 - x0)), bevel=0)
    for sx in (-1, 1):
        paint.box((.45, 2.6, .006), loc=(sx * .9, 0, z + .001), bevel=0)
    paint.box((1.35, .45, .006), loc=(0, 0, z + .001), bevel=0)
    edge = a.part('Paint_edge', 'Hazard')
    for s in (-1, 1):
        for i in range(5):
            f = -3.6 + i * 1.8
            edge.box((1.0, .2, .006), loc=(f, s * 4.6, z + .001), bevel=0)
            edge.box((.2, 1.0, .006), loc=(s * 4.6, f, z + .001), bevel=0)
    a.part('Team_band', 'Team').box((2.4, .3, .006), loc=(0, -3.95, z + .002), bevel=0)
    lights = a.part('Lamps', 'Lamp')
    rims = a.part('Lamp_rims', 'Steel')
    for i in range(16):
        t = i * TAU / 16
        x = max(-1, min(1, math.cos(t) * 1.42)) * 4.3
        y = max(-1, min(1, math.sin(t) * 1.42)) * 4.3
        rims.cyl(.09, .01, loc=(x, y, z + .004), seg=8, bevel=0)
        lights.cyl(.05, .012, loc=(x, y, z + .006), seg=6, bevel=0)
    tie = a.part('Tie_downs', 'Steel')
    for (x, y) in ((2.2, 2.2), (-2.2, 2.2), (2.2, -2.2), (-2.2, -2.2), (0, 2.9), (0, -2.9)):
        tie.torus(.08, .012, loc=(x, y, z + .004), seg=8, ring=3)
    gr = a.part('Drain_grates', 'Undercarriage')
    for (x, y) in ((4.85, 0), (-4.85, 0), (0, 4.85)):
        gr.box((.12 if abs(x) > 1 else 1.2, 1.2 if abs(x) > 1 else .12, .006), loc=(x, y, z), bevel=0)
    st = a.part('Stains', 'Charred')
    for (x, y, w, r) in ((.8, .6, 1.4, .4), (-1.1, -.9, 1.0, 1.4), (2.6, -1.6, .7, .9), (-2.8, 1.9, .8, 2.1)):
        st.box((w, w * .6, .006), loc=(x, y, z + .002), rot=(0, 0, r), bevel=0)


def helipad(a):
    """helipad: the flat pad (see the module docstring)."""
    pad(a)
    k.clean(a)


def helipad_a(a):
    """helipad_a: the pad with the fabric clamshell shelter on its rear (see the module docstring)."""
    pad(a)
    # The shelter: six steel arches across the rear third, the canvas skin, the drawn-back end curtain, ballast.
    y0, y1 = 1.8, 4.9
    prof = [(-1.2 + math.cos(t) * 3.7, math.sin(t) * 3.4) for t in (i * math.pi / 10 for i in range(11))]
    arch = a.part('Shelter_arches', 'Steel')
    for i in range(6):
        y = y0 + (y1 - y0) * i / 5
        arch.tube([(x, y, PADH + z) for x, z in prof], .05, seg=4, caps=False)
    skin = a.part('Roof', 'Canvas')
    rings = []
    verts, faces = [], []
    n = len(prof)
    for i, y in enumerate((y0 + .3, y1)):
        for x, z in prof:
            verts.append((x, y, PADH + z * .99))
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    skin.mesh(verts, faces)
    skin.mesh(verts, [tuple(reversed(f)) for f in faces])
    back = [(x, y1, PADH + z * .99) for x, z in prof] + [(-1.2, y1, PADH)]
    skin.mesh(back, [(i + 1, i, n) for i in range(n - 1)])
    # The end curtain gathered at both sides, the ballast blocks, the guy ropes.
    for sx in (-1, 1):
        k.lathe(a.part('Curtain', 'Canvas'), [(.3, 0), (.32, 2.6), (.2, 3.0), (0, 3.05)], loc=(-1.2 + sx * 3.3, y0 + .2,
                                                                                          PADH), seg=8)
        for y in (y0, y1):
            k.block(a.part('Ballast', 'Concrete'), (.6, .6, .5), loc=(-1.2 + sx * 3.75, y, PADH + .25), chamfer=.04)
        a.part('Guy_ropes', 'Canvas').tube([(-1.2 + sx * 3.4, 3.4, PADH + 1.8), (-1.2 + sx * 4.0, 3.4, PADH)], .012,
                                           seg=3)
    a.part('Team_band', 'Team').box((4.0, .03, .35), loc=(-1.2, y1 + .02, PADH + 2.2), bevel=0)
    # Inside: the tool cart, a work light, a rotor blade on trestles, spare parts boxes.
    cart = a.part('Tool_cart', 'BarrelRed')
    k.block(cart, (.9, .5, .8), loc=(-2.6, 3.6, PADH + .5), chamfer=.03)
    for (dx, dy) in ((-.35, -.2), (.35, -.2), (-.35, .2), (.35, .2)):
        a.part('Cart_wheels', 'Rubber').cyl(.08, .05, loc=(-2.6 + dx, 3.6 + dy, PADH + .08), rot=(0, R90, 0), seg=8,
                                            bevel=0)
    K.floodlight(a, (3.4, 2.4, PADH), facing=(-.6, -.6, -.6), pole=1.8)
    for x in (-1.4, 1.2):
        a.part('Trestles', 'Wood').box((.1, .6, .8), loc=(x, 4.2, PADH + .4), bevel=0)
    a.part('Rotor_blade', 'Armor').box((3.4, .35, .05), loc=(.1, 4.2, PADH + .83), bevel=0)
    W.stack(a, (3.4, 3.2, PADH), n=3, size=(.6, .4, .3), yaw=.1, seed=60)
    W.stack(a, (4.3, 3.0, PADH), n=2, size=(.6, .4, .3), yaw=-.1, seed=61)
    k.clean(a)


def helipad_b(a):
    """helipad_b: the pad with the forward arming and refuelling point (see the module docstring)."""
    pad(a)
    # Two pillow fuel bladders in a sandbag bund along the left edge.
    for y in (-2.2, 1.6):
        k.lathe(a.part('Fuel_bladders', 'Rubber'), [(0, 0), (1.0, .05), (1.25, .3), (1.2, .6), (.9, .75), (0, .8)],
                loc=(3.6, y, PADH), seg=12, worn=(2,))
        a.part('Bladder_valves', 'Steel').cyl(.08, .15, loc=(3.6, y - 1.2, PADH + .3), seg=6, bevel=0)
    W.bags(a, [(2.2, -4.0, PADH), (2.2, 3.4, PADH)], layers=2, bag=(.55, .3, .17), seed=62)
    W.bags(a, [(4.95, -4.0, PADH), (4.95, 3.4, PADH)], layers=1, bag=(.55, .3, .17), seed=63)
    # The pump unit with its hose reels and the hose to the pad's edge.
    k.block(a.part('Pump_skid', 'Armor'), (1.1, .8, .8), loc=(1.4, -.3, PADH + .4), chamfer=.04)
    K.grille(a, (1.4, -.71, PADH + .45), .7, .35, facing=(0, -1, 0), slats=4)
    for y in (-1.0, .4):
        a.part('Hose_reels', 'BarrelRed').cyl(.35, .3, loc=(1.4, y, PADH + .4), rot=(0, R90, 0), seg=10, bevel=0)
    hz = a.part('Hoses', 'Rubber')
    hz.tube([(3.6, -2.2, PADH + .55), (2.6, -1.5, PADH + .05), (1.95, -.4, PADH + .2)], .05, seg=5)
    hz.tube([(3.6, 1.6, PADH + .55), (2.6, 1.0, PADH + .05), (1.95, -.2, PADH + .2)], .05, seg=5)
    hz.tube([(1.0, -1.0, PADH + .3), (0, -1.6, PADH + .03), (-1.0, -1.0, PADH + .03)], .035, seg=5)
    # The arming point on the right: a rocket rack, ammunition boxes on pallets, the extinguisher trolley.
    rk = a.part('Rocket_rack', 'Wood')
    for x in (-4.4, -3.2):
        rk.box((.08, 1.4, .7), loc=(x, 2.4, PADH + .35), bevel=0)
    for i in range(4):
        k.lathe(a.part('Spare_rockets', 'Fuel'), [(0, -.75), (.04, -.7), (.05, -.6), (.05, .7), (0, .75)],
                loc=(-3.8, 1.9 + i * .3, PADH + .74), rot=(0, R90, 0), seg=6)
    a.part('Pallets', 'Wood').box((1.1, 1.1, .12), loc=(-3.9, -.4, PADH + .06), bevel=0)
    W.stack(a, (-4.1, -.4, PADH + .12), n=3, size=(.5, .9, .26), yaw=R90, seed=64)
    W.stack(a, (-3.6, -.4, PADH + .12), n=2, size=(.5, .9, .26), yaw=R90, seed=65)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.2, 0), (.2, .9), (.12, 1.0), (0, 1.05)], loc=(-3.7, -2.8, PADH + .1),
            seg=10, worn=(1,))
    for sx in (-1, 1):
        a.part('Cart_wheels', 'Rubber').cyl(.15, .06, loc=(-3.7 + sx * .25, -2.8, PADH + .15), rot=(0, R90, 0),
                                            seg=8, bevel=0)
    # The windsock on its pole at the rear right corner.
    a.part('Windsock_pole', 'Steel').cyl(.035, 1.7, loc=(-4.6, 4.6, PADH + .85), seg=6, bevel=0)
    k.lathe(a.part('Windsock', 'Hazard'), [(.14, 0), (.1, .6), (.06, .9)], loc=(-4.6, 4.6, PADH + 1.65),
            rot=(R90 - .3, 0, .8), seg=8, caps=(False, False))
    k.clean(a)


BUILDERS = {
    'logistics_station': (logistics_station, dict(ao_distance=.5, grime_height=.15, ao_strength=.5)),
    'helipad': (helipad, dict(ao_distance=.4, grime_height=.1, ao_strength=.5)),
    'helipad_a': (helipad_a, dict(ao_distance=.6, grime_height=.2, ao_strength=.55)),
    'helipad_b': (helipad_b, dict(ao_distance=.5, grime_height=.15, ao_strength=.55)),
}
