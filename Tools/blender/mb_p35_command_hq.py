"""Prompt 35 wave 7 (lane C): the Siege command HQ rebuilt from scratch (spec: Tools/blender/specs/command_hq.json).

The fortified command bunker the Siege fortress defends (balance.json: 16 x 14 m, it blocks and blows up with an
Ultimate explosion; the old mb_siege builder's brief): the apron slab with its joints; the battered cast-concrete
bunker with its parapet, Team bands and form-tie marks; the raised command room on top with a band of armoured, lit
windows under steel visors, its roof slab and the Team roof plate; the satellite dish turning on the roof (`Radar`);
the entrance portal at the front with the blast door in a hazard frame, lamps and a lit sign; precast T-walls with
Team bands flanking the entrance, two Team flags; the workshop annex with its roller door on the left; the generator
yard under a camouflage net on the right; the sandbag lookout ring on the roof's front corner; the 15 m lattice
comms mast at the rear corner with its antennas and the obstruction light.

Runtime nodes kept: `Radar`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
G = .22                       # apron top
BW, BD, BH = 10.0, 7.4, 4.4   # bunker footprint and height
BY = .9                       # bunker centre (y)


def _base(a):
    k.extrude(a.part('Base', 'Concrete'), C.octagon(15.8, 13.8, .7), G, loc=(0, 0, G / 2), axis='Z', corner=.05,
              taper=(.985, .985), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-3, 4):
        j.box((15.2, .04, .01), loc=(0, i * 1.9, G + .003), bevel=0)
    for i in range(-3, 4):
        j.box((.04, 13.2, .01), loc=(i * 2.2, 0, G + .003), bevel=0)
    for i in range(8):
        u = i * TAU / 8
        K.dust(a, (math.cos(u) * 7.0, math.sin(u) * 6.0, G), radius=2.2, k=.3)


def _bunker(a):
    # The battered walls (12 degrees), the parapet ring, the roof slab.
    k.extrude(a.part('Walls', 'Plaster'), [(-BW / 2, BY - BD / 2), (BW / 2, BY - BD / 2), (BW / 2, BY + BD / 2),
                                          (-BW / 2, BY + BD / 2)], BH, loc=(0, 0, G + BH / 2), axis='Z',
              chamfer=.08, corner=.15, taper=(.92, .9), caps=(False, False))
    top_w, top_d = BW * .92, BD * .9
    par = a.part('Parapet', 'Concrete')
    zt = G + BH
    for s in (-1, 1):
        k.block(par, (top_w + .1, .35, .55), loc=(0, BY + s * (top_d / 2 - .1), zt + .27), chamfer=.05)
        k.block(par, (.35, top_d - .5, .55), loc=(s * (top_w / 2 - .1), BY, zt + .27), chamfer=.05)
    k.block(a.part('Roof', 'Asphalt'), (top_w - .5, top_d - .5, .1), loc=(0, BY, zt + .05), chamfer=0)
    # Team bands round the walls, form-tie marks, drain spouts.
    tb = a.part('Team_band', 'Team')
    for s in (-1, 1):
        tb.box((BW * .96, .03, .35), loc=(0, BY + s * (BD * .95 / 2 + .01), G + BH * .78), rot=(-s * .21, 0, 0),
               bevel=0)
        tb.box((.03, BD * .93, .35), loc=(s * (BW * .96 / 2 + .01), BY, G + BH * .78), rot=(0, s * .17, 0), bevel=0)
    ties = a.part('Kit_steel', 'Steel')
    for s in (-1, 1):
        for f in (-3.5, -1.5, 1.5, 3.5):
            for zz in (1.2, 2.6):
                ties.cyl(.05, .04, loc=(f, BY + s * (BD / 2 - zz * .21 + .01), G + zz), rot=(R90 - s * .21, 0, 0),
                         seg=5, bevel=0)
    # Battered buttresses on the corners and the side walls.
    bt = a.part('Walls', 'Concrete')
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.extrude(bt, [(-.45, -.45), (.45, -.45), (.45, .45), (-.45, .45)], BH * .8,
                      loc=(sx * (BW / 2 - .1), BY + sy * (BD / 2 - .1), G + BH * .4), axis='Z', chamfer=.04,
                      taper=(.6, .6), caps=(False, True))
        for y in (-1.2, 1.6):
            k.extrude(bt, [(-.3, -.35), (.3, -.35), (.3, .35), (-.3, .35)], BH * .6,
                      loc=(sx * (BW / 2 + .05), BY + y, G + BH * .3), axis='Z', chamfer=.03, taper=(.5, .9),
                      caps=(False, True))
    # Wall kit: cameras and lamps on brackets, cable conduits, a fire-escape ladder.
    for x, y, f in ((-4.2, BY - BD / 2 + .3, (0, -1, -.3)), (4.2, BY + BD / 2 - .3, (0, 1, -.3)),
                    (-BW / 2 + .4, BY + 2.0, (-1, 0, -.3))):
        K.lamp(a, (x, y, G + 3.6), f, r=.1, guard=True)
        k.block(a.part('Window_visors', 'Armor'), (.14, .3, .14), loc=(x, y + f[1] * .2, G + 3.95), chamfer=.02)
    cd_ = a.part('Kit_steel', 'Steel')
    cd_.tube([(-2.0, BY + BD / 2 - .3, G + .3), (-2.0, BY + BD / 2 - .55, G + 2.0), (-2.0, BY + BD / 2 - .85, G + BH)],
             .06, seg=5)
    cd_.tube([(BW / 2 - .5, BY - 2.5, G + .3), (BW / 2 - .8, BY - 2.5, G + BH)], .05, seg=5)
    K.ladder(a.part('Ladders', 'Steel'), (-BW / 2 + .2, BY - 2.0, G), (-BW / 2 + .55, BY - 2.0, G + BH), width=.5,
             step=.35)
    for x in (-3.0, 3.0):
        a.part('Kit_steel', 'Steel').box((.2, .5, .12), loc=(x, BY + top_d / 2 + .2, zt - .1), bevel=0)


def _command_room(a):
    zt = G + BH
    cy = BY + .6
    cx = 1.0
    cw, cd, ch = 5.6, 3.8, 2.3
    k.extrude(a.part('Command_room', 'Concrete'), [(-cw / 2, cy - cd / 2), (cw / 2, cy - cd / 2), (cw / 2, cy + cd / 2),
                                                  (-cw / 2, cy + cd / 2)], ch, loc=(cx, 0, zt + .1 + ch / 2), axis='Z',
              chamfer=.06, corner=.1, taper=(.95, .94), caps=(False, True))
    # The band of armoured windows (lit) under their visors, front and sides.
    win = a.part('Lit_windows', 'Lamp')
    vis = a.part('Window_visors', 'Armor')
    frm = a.part('Window_visors', 'Armor')
    zw = zt + .1 + ch * .62
    for i in range(5):
        x = (i - 2) * 1.05
        frm.box((.9, .08, .5), loc=(cx + x, cy - cd * .97 / 2 - .02, zw), rot=(-.08, 0, 0), bevel=0)
        win.box((.76, .04, .36), loc=(cx + x, cy - cd * .97 / 2 - .05, zw), rot=(-.08, 0, 0), bevel=0)
        vis.box((.95, .45, .06), loc=(cx + x, cy - cd * .97 / 2 - .2, zw + .33), rot=(.15, 0, 0), bevel=0)
    for s in (-1, 1):
        for i in range(2):
            y = cy + (i - .5) * 1.4
            frm.box((.08, .9, .5), loc=(cx + s * (cw * .97 / 2 + .02), y, zw), rot=(0, s * .08, 0), bevel=0)
            win.box((.04, .76, .36), loc=(cx + s * (cw * .97 / 2 + .05), y, zw), rot=(0, s * .08, 0), bevel=0)
    k.block(a.part('Roof', 'Asphalt'), (cw * .94, cd * .94, .12), loc=(cx, cy, zt + .1 + ch + .06), chamfer=.03)
    a.part('Team_band', 'Team').box((2.4, 1.6, .02), loc=(cx - 1.0, cy + .2, zt + .1 + ch + .13), bevel=0)
    # Roof kit: vents, the air-conditioning box, the ladder up from the main roof.
    zr = zt + .1 + ch + .12
    for x in (1.6, 2.2):
        k.lathe(a.part('Vents', 'Steel'), [(.18, 0), (.18, .3), (.26, .32), (.26, .4), (0, .45)], loc=(cx + x, cy + 1.2, zr),
                seg=8, worn=(3,))
    k.block(a.part('Vents', 'Steel'), (.9, .7, .5), loc=(cx + 1.8, cy - .6, zr + .25), chamfer=.04)
    K.grille(a, (cx + 1.8, cy - .96, zr + .25), .7, .35, facing=(0, -1, 0), slats=4)
    K.ladder(a.part('Ladders', 'Steel'), (cx + cw / 2 - .4, cy - cd / 2 - .05, zt + .1), (cx + cw / 2 - .4, cy - cd / 2 - .05, zr),
             width=.45, step=.3)
    # The dish turning on the roof (`Radar`).
    k.lathe(a.part('Dish_pedestal', 'Steel'), [(.35, 0), (.35, .1), (.15, .2), (.12, .9), (0, .9)],
            loc=(cx - 1.0, cy + .2, zr), seg=10, worn=(2,))
    r = a.pivot('Radar', (cx - 1.0, cy + .2, zr + .9))
    K.dish(a.part('Radar_dish', 'PlasterWhite', r), a.part('Radar_horn', 'Steel', r), (0, 0, .75), r=.9,
           normal=(0, -1, .6), seg=16)
    a.part('Radar_frame', 'Steel', r).box((.3, .3, .5), loc=(0, .3, .25), bevel=0)
    # The sandbag lookout ring on the main roof's front-left corner.
    K.sandbag_wall(a, [(3.2, BY - top_d_half() + .6, zt + .1), (4.2, BY - top_d_half() + .6, zt + .1),
                       (4.2, BY - top_d_half() + 1.6, zt + .1)], layers=2, bag=(.55, .3, .15))


def top_d_half():
    return BD * .9 / 2


def _entrance(a):
    # The entrance portal at the front: a cast hood, the blast door in a hazard frame, lamps, the lit sign.
    py = BY - BD / 2 - .9
    px = -1.3
    k.extrude(a.part('Portal', 'Concrete'), [(-1.9, py - .9), (1.9, py - .9), (2.1, py + 1.2), (-2.1, py + 1.2)], 3.2,
              loc=(px, 0, G + 1.6), axis='Z', chamfer=.06, corner=.05, taper=(.94, .96), caps=(False, True))
    K.door(a, (px, py - .92, G), (1.8, 2.2), normal=(0, -1, 0), mat='Armor')
    hz = a.part('Hazard_marks', 'Hazard')
    for s in (-1, 1):
        hz.box((.15, .05, 2.4), loc=(px + s * 1.05, py - .95, G + 1.2), bevel=0)
    hz.box((2.25, .05, .15), loc=(px, py - .95, G + 2.42), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (px + s * 1.4, py - .95, G + 2.6), (0, -1, -.3), r=.09, guard=True)
    a.part('Lit_windows', 'Lamp').box((1.4, .05, .35), loc=(px, py - .95, G + 2.85), bevel=0)
    a.part('Team_band', 'Team').box((1.5, .03, .45), loc=(px, py - .935, G + 2.85), bevel=0)
    # T-walls flanking the approach, with Team bands; two flags on poles.
    tw = a.part('T_walls', 'Concrete')
    twb = a.part('Team_band', 'Team')
    for s in (-1, 1):
        for i in range(3):
            x = px + s * (2.6 + i * 1.5)
            prof = [(-.55, 0), (.55, 0), (.55, .25), (.18, .4), (.13, 3.0), (-.13, 3.0), (-.18, .4), (-.55, .25)]
            k.extrude(tw, [(px, pz) for px, pz in prof], 1.4, loc=(x, -5.9, G), rot=(0, 0, 0), axis='X', chamfer=.02)
            twb.box((1.3, .03, .3), loc=(x, -6.05, G + 2.3), bevel=0)
        fp = a.part('Kit_steel', 'Steel')
        fp.cyl(.05, 6.0, loc=(px + s * 2.0, -6.4, G + 3.0), seg=6, bevel=0)
        a.part('Flags', 'Team').box((.02, 1.4, .9), loc=(px + s * 2.0, -5.7, G + 5.4), rot=(0, 0, .15 * s), bevel=0)


def _annex_and_yard(a):
    # The workshop annex on the left side with its roller door.
    ax = 6.3
    k.extrude(a.part('Annex', 'Plaster'), [(ax - 1.4, -1.6), (ax + 1.4, -1.6), (ax + 1.4, 2.6), (ax - 1.4, 2.6)], 2.8,
              loc=(0, 0, G + 1.4), axis='Z', chamfer=.04, corner=.05, caps=(False, False))
    k.extrude(a.part('Roof', 'Corrugated'), [(-1.6, 2.8), (1.6, 3.1), (1.6, 3.2), (-1.6, 2.9)], 4.4,
              loc=(ax, .5, G), axis='Y', chamfer=0)
    a.part('Roller_door', 'MetalSheet').box((.05, 2.2, 2.2), loc=(ax + 1.42, .5, G + 1.1), bevel=0)
    rd = a.part('Roller_door_ribs', 'Steel')
    for i in range(6):
        rd.box((.06, 2.2, .03), loc=(ax + 1.45, .5, G + .3 + i * .35), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((.06, 2.3, .12), loc=(ax + 1.44, .5, G + 2.3), bevel=0)
    # The generator yard on the right under a camouflage net on poles.
    gx = -6.3
    for i, y in enumerate((1.6, 3.5)):
        k.block(a.part('Generators', 'ContainerBlue'), (1.4, 1.6, 1.2), loc=(gx, y, G + .6), chamfer=.04)
        K.grille(a, (gx - .71, y, G + .7), 1.2, .6, facing=(-1, 0, 0), slats=5)
        K.exhaust(a, (gx + .4, y + .5, G + 1.2), r=.06, length=.6, direction=(0, 0, 1), muffler=False, cap=True)
    for f in (gx - 1.2, gx + 1.2):
        for y in (.4, 4.8):
            a.part('Net_poles', 'Wood').cyl(.05, 2.6, loc=(f, y, G + 1.3), seg=5, bevel=0)
    net = a.part('Camo_net', 'Foliage')
    net.box((2.8, 4.8, .04), loc=(gx, 2.6, G + 2.6), rot=(0, .05, 0), bevel=0)
    for i in range(6):
        net.box((.8, .9, .03), loc=(gx + (i % 2 - .5) * 1.4, .8 + i * .7, G + 2.5), rot=(i * .2, .3, i), bevel=0)
    for i in range(3):
        K.fuel_drum(a.part('Fuel_drums', 'BarrelRed'), a.part('Kit_steel', 'Steel'), (gx + .9, .9 + i * .62, G))
    # HESCO cells along the front-right edge, crates by the annex.
    for i in range(4):
        K.hesco(a, (-7.2, -4.8 + i * 1.08, G), size=(1.0, 1.0, 1.3))
    for i, (x, y) in enumerate(((4.8, -3.2), (5.5, -3.3), (5.1, -3.25))):
        K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.6, .5, .45), (x, y, G + (.45 if i == 2 else 0)),
                bands=1)


def _mast(a):
    # The 15 m lattice comms mast on the rear-right corner with antennas and the obstruction light.
    mx, my = -6.2, 5.6
    h = 15.0
    ms = a.part('Masts', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            ms.tube([(mx + sx * .5, my + sy * .5, G), (mx + sx * .15, my + sy * .15, G + h)], .045, seg=5)
    for i in range(7):
        z0 = G + i * h / 7
        z1 = G + (i + 1) * h / 7
        w0 = .5 - .35 * i / 7
        w1 = .5 - .35 * (i + 1) / 7
        corners0 = [(-w0, -w0), (w0, -w0), (w0, w0), (-w0, w0)]
        corners1 = [(-w1, -w1), (w1, -w1), (w1, w1), (-w1, w1)]
        for c in range(4):
            p0 = corners0[c] if i % 2 == 0 else corners0[(c + 1) % 4]
            p1 = corners1[(c + 1) % 4] if i % 2 == 0 else corners1[c]
            ms.tube([(mx + p0[0], my + p0[1], z0), (mx + p1[0], my + p1[1], z1)], .02, seg=3)
    k.block(a.part('Masts', 'Steel'), (.7, .7, .05), loc=(mx, my, G + 10.0), chamfer=0)
    ant = a.part('Antennas', 'Steel')
    K.whip_antenna(ant, (mx, my, G + h), h=2.0, r=.04)
    for z, n in ((G + 12.0, (1, 0, 0)), (G + 9.0, (0, -1, 0))):
        K.mesh_antenna(ant, (mx + n[0] * .3, my + n[1] * .3, z), w=.8, h=.6, normal=n, bars=4)
    K.dish(a.part('Antennas', 'PlasterWhite'), a.part('Antennas', 'Steel'), (mx + .5, my, G + 7.0), r=.5,
           normal=(1, -.3, .2), seg=12)
    a.part('Obstruction_light', 'LavaGlow').sphere(.12, loc=(mx, my, G + h + .1), seg=8, rings=5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Base', 'Concrete').box((.4, .4, .3), loc=(mx + sx * .5, my + sy * .5, G + .15), bevel=0)


def command_hq(a, detail=False):
    """The Siege command HQ: see the module docstring."""
    _base(a)
    _bunker(a)
    _command_room(a)
    _entrance(a)
    _annex_and_yard(a)
    _mast(a)
    K.beacon(a, (2.6, BY + 1.6, G + BH + .1 + 2.3 + .12), r=.12)
    k.clean(a)


BUILDERS = {
    'command_hq': (command_hq, dict(ao_distance=1.6, grime_height=.9)),
}
