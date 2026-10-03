"""Prompt 35 wave 4 (lane C): the armoured bulldozer rebuilt from scratch
(spec: Tools/blender/specs/armored_bulldozer.json).

An IDF Caterpillar D9R with its armour kit (the def's modelSize 6.13 x 3.7 x 3.53 m): the huge semi-U blade wider
than the machine on its push arms and lift rams (`Blade`, the runtime part that rams); the high-drive track
frames (the sprocket raised at the rear, the front idler, a row of bogie rollers, the linked track) behind the
armoured track guards; the long engine hood with its armoured grille and the exhaust stack; the armoured cab
(`Casemate`) with the thick slit windows behind grilles, the roof hatch, smoke dischargers and the driving
camera; the 12.7 mm on a raised pintle on the cab roof (the def's free `hmg_roof`, owner's roof-gun rule); the
rear ripper with its shank and tooth; tool box, jerrycans and the tow cable.

Runtime nodes kept: `Blade` with `Blade_moldboard`, `Blade_edge`, `Blade_back`, `Blade_pins`, `Blade_rams`;
`Mount_mg`, `Muzzle_mg`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.2, .62
BOGIES = (-1.6, -1.15, -.7, -.25, .2, .65)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, BOGIES, .2, sprocket=(1.45, 1.42, .48), idler=(-2.05, .42, .38),
                       rollers=[(-1.0, .86)], pitch=.24, disc_mat='Armor', wheel_w=.24, seg=8, teeth=11, link_h=.07,
                       dust=.4)
        # The track roller frame and the equaliser bar, the armoured track guard over the front.
        fr = a.part('Track_frames', 'Armor')
        fr.box((.3, 2.8, .28), loc=(s * (TX - .08), -.75, .48), bevel=.03)
        guard = a.part('Skirts', 'Team')
        K.plate(guard, (.04, 2.4, .45), loc=(s * (TX + TW / 2 + .04), -1.1, .78), chamfer=.01)
        K.rivet_line(a.part('Kit_steel', 'Steel'), (s * (TX + TW / 2 + .07), -2.2, .92), (s * (TX + TW / 2 + .07), 0.0, .92),
                     (s, 0, 0), pitch=.25, r=.02)
    a.part('Equaliser', 'Steel').box((2.6, .2, .16), loc=(0, -.9, .78), bevel=.02)


def _body(a):
    # The engine hood: a long narrow box with sloped shoulders, the armoured grille at the front.
    hood = a.part('Hull', 'Team')
    C.section_loft(hood, [(-2.32, [(0, .72), (.68, .72), (.7, 1.45), (.5, 1.62), (0, 1.66)]),
                          (-2.1, [(0, .7), (.75, .7), (.78, 1.6), (.6, 1.82), (0, 1.86)]),
                          (-.55, [(0, .7), (.85, .7), (.88, 1.7), (.68, 1.95), (0, 2.0)])])
    K.grille(a, (0, -2.27, 1.25), 1.2, .8, facing=(0, -1, 0), slats=6, frame_mat='Armor')
    K.rivet_line(a.part('Kit_steel', 'Steel'), (-.6, -1.4, 1.94), (.6, -1.4, 1.94), (0, 0, 1), pitch=.2, r=.02)
    for s in (-1, 1):
        K.plate(a.part('Hood_plates', 'Armor'), (.04, 1.4, .8), loc=(s * .86, -1.4, 1.25), chamfer=.01)
        K.lamp(a, (s * .55, -2.27, 1.75), (0, -1, 0), r=.07, guard=True)
    st = a.part('Exhaust_stack', 'Steel')
    k.lathe(st, [(.09, 1.9), (.09, 2.55), (.11, 2.6), (.11, 2.68)], loc=(-.45, -1.2, 0), seg=10, worn=(2,))
    a.part('Exhaust_shield', 'Armor').box((.3, .3, .5), loc=(-.45, -1.2, 2.15), bevel=.02)
    K.soot(a, (-.45, -1.2, 2.68), radius=.3, k=.5)
    a.pivot('Point_exhaust', (-.45, -1.2, 2.7))
    # The base frame and fuel tank at the rear, the ripper on its parallelogram, its shank and tooth.
    base = a.part('Chassis', 'Team')
    k.block(base, (2.0, 2.2, .75), loc=(0, 1.0, .65), chamfer=.05)
    k.block(a.part('Fuel_tank', 'Armor'), (1.7, .6, .9), loc=(0, 2.25, .75), chamfer=.06)
    rp = a.part('Ripper', 'Steel')
    for s in (-1, 1):
        rp.limb((s * .5, 2.4, .95), (s * .5, 2.8, .8), .07, .07, bevel=0)
        rp.limb((s * .7, 2.5, 1.5), (s * .5, 2.75, 1.0), .05, .05, bevel=0)       # tilt rams
    k.block(rp, (1.2, .25, .3), loc=(0, 2.8, .7), chamfer=.03)
    k.extrude(a.part('Ripper_shank', 'Armor'), [(-.12, .9), (.12, .9), (.18, .2), (.05, 0), (-.08, .1)], .18,
              loc=(0, 2.85, 0), axis='X', chamfer=.02)
    a.part('Ripper_tooth', 'Steel').box((.14, .22, .12), loc=(0, 2.82, .05), rot=(.5, 0, 0), bevel=0)
    a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(.7, 2.56, 1.1), bevel=0)
    a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(-.7, 2.56, 1.1), bevel=0)


def _cab(a):
    """The armoured cab: sloped armour walls, slit windows behind grilles, the roof gun and fittings."""
    cab = a.part('Casemate', 'Team')
    bot = [(-1.0, -.55), (1.0, -.55), (1.05, 1.15), (-1.05, 1.15)]
    top = [(-.85, -.35), (.85, -.35), (.9, 1.0), (-.9, 1.0)]
    C.slab_loft(cab, bot, top, 1.4, 2.75)
    k.block(a.part('Cab_roof', 'Armor'), (1.85, 1.45, .08), loc=(0, .32, 2.75), chamfer=.02)
    gl = a.part('Glass', 'Glass')
    gr = a.part('Grilles', 'Steel')
    for x in (-.45, .45):
        gl.box((.6, .02, .3), loc=(x, -.47, 2.45), rot=(-.12, 0, 0), bevel=0)
        for i in range(4):
            gr.box((.02, .04, .34), loc=(x - .24 + i * .16, -.5, 2.45), rot=(-.12, 0, 0), bevel=0)
    for s in (-1, 1):
        gl.box((.02, .7, .28), loc=(s * .99, .3, 2.45), bevel=0)
        for i in range(4):
            gr.box((.04, .02, .32), loc=(s * 1.01, .0 + i * .2, 2.45), bevel=0)
        K.lamp(a, (s * .8, -.42, 2.62), (0, -1, -.2), r=.06, guard=True)
        sp = a.part('Smoke_launchers', 'Armor')
        for j in range(3):
            sp.cyl(.04, .2, loc=(s * .9, .7 + j * .1, 2.7), rot=(R90 - .6, 0, s * 1.2), seg=8, bevel=0)
    # The driving camera on the cab front, the roof hatch, the 12.7 mm on its raised pintle, aerials.
    k.block(a.part('Sensor', 'Armor'), (.14, .18, .14), loc=(.6, -.47, 2.65), chamfer=.02)
    C.hatch(a, (.35, .55, 2.79), r=.28)
    C.roof_gun(a, (-.35, .3, 2.79), pivot='Mount_mg', barrel='MG_barrel', brake='MG_brake', muzzle='Muzzle_mg',
               post=.22, length=1.0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.8, .9, 2.79), h=.3)
    a.part('Team_band', 'Team').box((.012, 1.5, .12), loc=(1.035, .3, 2.0), rot=(0, -.05, 0), bevel=0)
    a.part('Team_band', 'Team').box((.012, 1.5, .12), loc=(-1.035, .3, 2.0), rot=(0, .05, 0), bevel=0)
    # Stowage: the tool box and jerrycans on the fenders behind the cab, the tow cable coiled on the rear.
    C.stowage_box(a, (.4, .7, .3), (1.25, 1.6, 1.05), mat='Armor', latches=2)
    C.jerry_rack(a, (-1.25, 1.6, 1.05), count=2, axis='Y', rot=(0, 0, R90))
    C.cable_reel(a, (0, 1.75, 1.15), r=.2, w=.5, axis='X')
    a.pivot('Point_fire', (0, -1.3, 2.1))


def _blade(a):
    """The semi-U blade on its push arms, the lift rams and the tilt cylinder (`Blade` pivots at the arms'
    trunnions on the track frames, so the ram stroke swings the whole blade)."""
    b = a.pivot('Blade', (0, -.8, .6))
    mb = a.part('Blade_moldboard', 'Team', b)
    # The mouldboard: a curved plate (sections across), its wings turned forward (semi-U).
    prof = [(0, 0), (-.18, .3), (-.25, .7), (-.2, 1.1), (-.05, 1.45), (.15, 1.62)]
    for i, (x0, x1, yaw) in enumerate(((-1.25, 1.25, 0), (1.25, 1.85, .35), (-1.85, -1.25, -.35))):
        w = x1 - x0
        cx = (x0 + x1) / 2
        rings = []
        for y, z in prof:
            yy = y - 2.1 - (abs(cx) - 1.25) * math.sin(abs(yaw)) * (1 if yaw else 0)
            rings.append([(cx - w / 2, yy, z - .55), (cx + w / 2, yy, z - .55), (cx + w / 2, yy + .1, z - .55),
                          (cx - w / 2, yy + .1, z - .55)])
        mb.loft(rings, bevel=0)
    a.part('Blade_edge', 'Steel', b).box((3.7, .12, .14), loc=(0, -2.12, -.5), bevel=0)
    bk = a.part('Blade_back', 'Armor', b)
    for x in (-1.3, -.45, .45, 1.3):
        bk.box((.08, .3, 1.4), loc=(x, -1.92, .15), bevel=0)
    bk.box((3.0, .2, .15), loc=(0, -1.88, .55), bevel=0)
    for s in (-1, 1):
        a.part('Blade_arms', 'Armor', b).limb((s * 1.2, 0, 0), (s * 1.15, -1.85, -.25), .1, .14, bevel=0)
    rams = a.part('Blade_rams', 'Steel', b)
    for s in (-1, 1):
        rams.limb((s * .6, -1.3, 1.25), (s * .55, -1.9, .9), .06, .06, bevel=0)
    rams.limb((.9, -1.0, .95), (.5, -1.85, .5), .05, .05, bevel=0)                   # the tilt cylinder
    pins = a.part('Blade_pins', 'Steel', b)
    for x in (-1.15, -.55, .55, 1.15):
        pins.cyl(.06, .2, loc=(x, -1.9, x and .0), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Blade_marks', 'Hazard', b).box((.35, .02, .25), loc=(1.6, -2.2, .7), rot=(0, 0, .35), bevel=0)
    a.part('Blade_marks', 'Hazard', b).box((.35, .02, .25), loc=(-1.6, -2.2, .7), rot=(0, 0, -.35), bevel=0)


def armored_bulldozer(a, detail=False):
    """The armoured bulldozer: see the module docstring."""
    _running_gear(a)
    _body(a)
    _cab(a)
    _blade(a)
    K.dust(a, (0, -2.9, .2), radius=1.8, k=.35)
    K.dust(a, (0, 0, .3), radius=3.0, k=.15)
    k.clean(a)


BUILDERS = {
    'armored_bulldozer': (armored_bulldozer, dict(ao_distance=.55, grime_height=.6)),
}
