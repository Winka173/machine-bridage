"""Prompt 35 wave 1 (lane B): the elite rocket launcher rebuilt from scratch (spec: Tools/blender/specs/elite_mlrs.json).

Not the plain mlrs (an M142 HIMARS with one six-round pod): the elite carries the M270's launcher-loader module on
an armoured-cab 6x6 (unit_refs: "M142 HIMARS / M270"; the def's modelSize 7.01 x 2.3 x 2.99 m is the HIMARS
truck's own size): the blocky armoured cab (LSAC) with its thick flat windscreens and roof hatch ring; behind it the
exhaust and the air intake; the launcher module on its turntable with TWO six-round pods side by side (twelve tube
mouths facing forward at rest), the two loader booms along its top with the hoist at the rear, the elevation rams
and the module's cable ducts; folded stabiliser jacks at the rear; six wheels (single front axle, rear tandem).
The elite's marks (DECISIONS 25B2): black armour (`EliteBlack`), gold chevrons and bands, the red-glowing sight.

Runtime nodes kept: `Turret` (the module's yaw pivot), `Muzzle_main`, `Mount_mg` / `Muzzle_mg` (the roof gun),
`Point_exhaust`, `Point_fire`; launch points: `Pods` (two groups across the module, used in turn) and `Tubes_bore`.
Metres, +Z up, -Y front, +X left.
"""
import math

import bmesh
from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .55, .38, .82
AXLES = (-2.3, 1.05, 2.5)
FRONT, REAR = -3.5, 3.5
HALF = 1.14
CAB_Y0, CAB_Y1, CAB_Z0, ROOF = -3.44, -1.62, 1.05, 2.5
TT = (0, 1.25, 1.36)          # the turntable (Turret pivot)
POD_L, POD_W, POD_H = 3.9, .98, .86
RAISE = -.12                  # the pods' rest elevation (radians about X: the front up)


def _chassis(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.12, 6.7, .28), loc=(s * .45, 0, .96), c=.02)
    for y in (-2.9, .2, 3.2):
        frame.box((.8, .08, .14), loc=(0, y, .96), bevel=0)
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8, nuts=0)
            K.dust(a, (s * TRACK, y, .15), radius=1.0, k=.27)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, TRACK - .1, r=.08, diff=False)
    susp = a.part('Suspension', 'Steel')
    for s in (-1, 1):
        P.leaf_pack(susp, s * .45, AXLES[0], WR + .2, 1.1, leaves=3, w=.09)
        susp.box((.12, AXLES[2] - AXLES[1] + .4, .14), loc=(s * .45, (AXLES[1] + AXLES[2]) / 2, WR + .12), bevel=0)
        susp.tube([(s * .6, AXLES[0] + .1, WR + .05), (s * .58, AXLES[0] + .18, WR + .45)], .035, seg=6)
    fen = a.part('Fenders', 'Undercarriage')
    for s in (-1, 1):
        k.sweep(fen, [(-.21, -.012), (.21, -.012), (.21, .012), (-.21, .012)],
                [(s * TRACK, AXLES[1] - .7, WR + .32), (s * TRACK, AXLES[1] - .55, WR + .62),
                 (s * TRACK, AXLES[2] + .55, WR + .62), (s * TRACK, AXLES[2] + .7, WR + .32)])
        P.mudflap(a, (s * TRACK, AXLES[2] + .72, WR + .5), w=.42, h=.45)
    # Side boxes: the fuel tank (right), the batteries and the hydraulic reservoir (left).
    P.fuel_tank(a, (-.85, -.5, 1.0), 1.1, .25, straps=2)
    P.toolbox(a, (.86, -.65, .98), (.3, .8, .5), mat='Armor')
    a.pivot('Point_fire', (0, .5, 1.8))


def _cab(a):
    blk = a.part('Cab', 'Team')                  # team paint; the add-on armour is the elite's black
    dark = a.part('Cab_dark', 'Undercarriage')
    # Horizontal sections: the armour wraps the front corners, the windscreens rake back a little, the roof edge
    # is cut at 45 degrees all round (the LSAC's add-on armour).
    rings = []
    for z, yf, c, inset in ((CAB_Z0, CAB_Y0 + .02, .18, 0), (CAB_Z0 + .7, CAB_Y0, .2, 0),
                            (ROOF - .2, CAB_Y0 + .18, .26, .05), (ROOF, CAB_Y0 + .38, .38, .22)):
        h = HALF - inset
        rings.append([(-h, CAB_Y1, z), (-h, yf + c, z), (-h + c, yf, z), (h - c, yf, z), (h, yf + c, z),
                      (h, CAB_Y1, z)])
    k.sharp_loft(blk, rings, chamfer=.04)
    # The grille and lamps low on the front, a brush guard, the bumper with tow eyes.
    K.grille(a, (0, CAB_Y0 - .02, CAB_Z0 + .33), 1.2, .38, facing=(0, -1, 0), slats=5, frame_mat='Undercarriage')
    bump = a.part('Bumper', 'Steel')
    K.chamfer_box(bump, (HALF * 2 - .1, .2, .3), loc=(0, FRONT + .1, .9), c=.03)
    for s in (-1, 1):
        K.lamp(a, (s * .8, CAB_Y0 - .02, CAB_Z0 + .32), (0, -1, 0), r=.08, mat='Undercarriage', guard=False)
        bump.box((.1, .08, .1), loc=(s * .5, FRONT - .02, .8), bevel=0)
    # Thick armoured windscreens: two flat panes in heavy frames on the raked face.
    z0, z1 = CAB_Z0 + .78, ROOF - .26

    def fy(z):
        return CAB_Y0 + .18 * (z - CAB_Z0 - .7) / (ROOF - .2 - CAB_Z0 - .7) - .01
    for s in (-1, 1):
        x0, x1 = s * .08, s * (HALF - .32)
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.07)
    glass = a.part('Glass', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .004)
        # Doors: a heavy door with a small armoured window, the hinges, a handle, the step.
        for y in (CAB_Y0 + .5, CAB_Y1 - .25):
            dark.box((.012, .02, ROOF - CAB_Z0 - .35), loc=(x, y, (ROOF + CAB_Z0) / 2 - .1), bevel=0)
        glass.box((.014, .45, .38), loc=(s * (HALF + .003), -2.55, ROOF - .58), bevel=0)
        dark.box((.016, .52, .05), loc=(s * (HALF + .006), -2.55, ROOF - .36), bevel=0)
        K.handle(fit, (x, CAB_Y1 - .35, CAB_Z0 + .55), (x, CAB_Y1 - .45, CAB_Z0 + .55), (s, 0, 0), h=.025, r=.01)
        P.step(a, (s * (HALF - .12), -2.55, .7), w=.4)
        K.mirror(fit, (s * (HALF - .03), CAB_Y0 + .4, ROOF - .45), s, arm=.04, size=(.035, .1, .26))
        K.plate(a.part('Cab_armor', 'EliteBlack'), (.03, 1.25, .55), loc=(s * (HALF + .02), (CAB_Y0 + CAB_Y1) / 2,
                                                                          CAB_Z0 + .38), chamfer=.01)
    # Roof: the team panel, the commander's sight (red glow), the hatch ring with the gun, antennas.
    K.plate(a.part('Cab_armor', 'EliteBlack'), (1.2, .9, .03), loc=(0, CAB_Y1 - .75, ROOF + .01), chamfer=.01)
    K.periscope(a, (-.55, CAB_Y0 + .62, ROOF - .02), facing=(0, -1, 0), size=(.2, .18, .16), mat='Steel')
    a.part('Sight_glow', 'EliteGlow').box((.14, .01, .07), loc=(-.55, CAB_Y0 + .52, ROOF + .11), bevel=0)
    ant = a.part('Antennas', 'Steel')
    for x in (-.95,):
        K.whip_antenna(ant, (x, CAB_Y1 - .1, ROOF - .05), h=.55, r=.02)
    P.raised_gun(a, (.35, CAB_Y1 - .62, ROOF), pivot='Mount_mg', barrel='MG_barrel', brake='MG_flash',
                 muzzle='Muzzle_mg', riser=.1, ring_r=.36, post=.14, length=1.0, shield_k=.75, tag='_mg')
    # Behind the cab: the exhaust stack and the air intake with its pre-cleaner.
    K.exhaust(a, (-.9, CAB_Y1 + .16, 1.2), r=.06, length=1.0, direction=(0, 0, 1), muffler=True, cap=True)
    a.pivot('Point_exhaust', (-.9, CAB_Y1 + .16, 2.3))
    k.lathe(a.part('Air_intake', 'EliteBlack'), [(.14, 0), (.14, .45), (.1, .5), (0, .52)],
            loc=(.9, CAB_Y1 + .18, 1.6), seg=10, worn=(1,))


def _module(a):
    """The launcher-loader module on its turntable (`Turret`): base, two pods, booms, rams, ducts."""
    bed = a.part('Bed', 'EliteBlack')
    K.chamfer_box(bed, (2.1, 4.9, .14), loc=(0, .95, 1.17), c=.02)
    k.ring(a.part('Turntable', 'Steel'), [(.75, -.02), (.82, -.02), (.82, .1), (.75, .1)], loc=(0, TT[1], TT[2] - .14),
           seg=16)
    t = a.pivot('Turret', TT)
    base = a.part('Turret_armor', 'EliteBlack', t)
    # The cradle base: a deep box with sloped front, the trunnion blocks at the rear.
    k.extrude(base, [(-1.9, 0), (1.9, 0), (2.0, .18), (1.7, .32), (-1.75, .32), (-2.05, .18)], 2.06,
              axis='X', chamfer=.03, corner=.03)
    steel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        K.chamfer_box(steel, (.16, .4, .3), loc=(s * .95, 1.55, .45), c=.03)                       # trunnions
        k.lathe(steel, [(.07, 0), (.07, .55), (.05, .58), (.05, 1.0)], loc=(s * .55, -1.0, .2),
                rot=(-1.25, 0, 0), seg=6)                                                         # rams
    # The two pods side by side (olive munition containers in the black frame): body, the forward face with six
    # tube mouths each, end frames, lifting lugs; built level, then raised RAISE about the rear trunnions.
    before = {key: len(sh.bm.verts) for key, sh in a.shapes.items()}
    pods = a.part('Pods', 'Crate', t)
    face = a.part('Pod_face', 'Undercarriage', t)
    bore = a.part('Tubes_bore', 'Undercarriage', t)
    frame = a.part('Pod_frame', 'Steel', t)
    z0 = .36
    y0 = -POD_L / 2 - .15
    for s in (-1, 1):
        x = s * (POD_W / 2 + .03)
        K.chamfer_box(pods, (POD_W, POD_L, POD_H), loc=(x, y0 + POD_L / 2, z0 + POD_H / 2), c=.04)
        face.box((POD_W - .06, .03, POD_H - .06), loc=(x, y0 - .01, z0 + POD_H / 2), bevel=0)
        for i in range(3):
            for j in range(2):
                bore.cyl(.12, .04, loc=(x + (i - 1) * .29, y0 - .02, z0 + .22 + j * .42), rot=K.FORWARD, seg=6,
                         bevel=0)
        for yy in (y0 + .06, y0 + POD_L - .06):                                      # end frames
            frame.box((POD_W + .04, .08, POD_H + .04), loc=(x, yy, z0 + POD_H / 2), bevel=0)
        for yy in (y0 + .6, y0 + POD_L - .6):
            frame.box((.12, .08, .06), loc=(x, yy, z0 + POD_H + .03), bevel=0)                    # lugs
        # The ribs along the pod's skin.
        for zz in (z0 + .3, z0 + .6):
            frame.box((.02, POD_L - .3, .04), loc=(x + s * (POD_W / 2 + .005), y0 + POD_L / 2, zz), bevel=0)
        # Gold chevrons and a band on the pod side (the elite's marks).
        gilt = a.part('Chevrons', 'Gilded', t)
        for i in range(2):
            yy = y0 + 1.1 + i * .22
            for d in (-1, 1):
                gilt.box((.012, .3, .06), loc=(x + s * (POD_W / 2 + .012), yy + d * .06, z0 + .45 + d * .0),
                         rot=(d * .6, 0, 0), bevel=0)
        gilt.box((.014, .12, POD_H - .1), loc=(x + s * (POD_W / 2 + .012), y0 + POD_L - .5, z0 + POD_H / 2), bevel=0)
    # The loader booms along the top outer edges, the hoist at the rear, the hoist cable.
    boom = a.part('Booms', 'EliteBlack', t)
    zb = z0 + POD_H + .1
    for s in (-1, 1):
        x = s * (POD_W + .02)
        k.block(boom, (.14, POD_L + .1, .16), loc=(x, y0 + POD_L / 2 + .05, zb), chamfer=.02)
        for yy in (y0 + .4, y0 + POD_L / 2, y0 + POD_L - .3):
            boom.box((.1, .1, .14), loc=(x, yy, zb - .12), bevel=0)
    boom.box((2.1, .16, .14), loc=(0, y0 + POD_L, zb + .02), bevel=0)
    k.lathe(a.part('Pod_frame', 'Steel', t), [(.12, -.06), (.12, .06)], loc=(.3, y0 + POD_L - .05, zb - .12),
            rot=(0, R90, 0), seg=10)
    a.part('Pod_frame', 'Steel', t).tube([(.3, y0 + POD_L - .05, zb - .2), (.3, y0 + POD_L + .05, z0 + .2)], .012,
                                          seg=4)
    # Cable ducts down the module's sides.
    for s in (-1, 1):
        a.part('Pod_face', 'Undercarriage', t).box((.06, 3.0, .08), loc=(s * 1.06, 0, .2), bevel=0)
    rot = Matrix.Rotation(RAISE, 3, 'X')
    cent = Vector((0, y0 + POD_L, z0))
    for key, sh in a.shapes.items():
        if key[2] != t or key[0] in ('Turret_armor', 'Turret_steel'):
            continue
        sh.bm.verts.ensure_lookup_table()
        new = list(sh.bm.verts)[before.get(key, 0):]
        if new:
            bmesh.ops.rotate(sh.bm, verts=new, cent=cent, matrix=rot)
    mz = cent + rot @ (Vector((0, y0 - .05, z0 + POD_H / 2)) - cent)
    a.pivot('Muzzle_main', tuple(mz), t)


def _rear(a):
    # Folded stabiliser jacks at the rear corners, tail lamps, the tow pintle.
    for s in (-1, 1):
        K.outrigger(a.part('Jacks', 'EliteBlack'), a.part('Kit_hooks', 'Steel'), (s * .5, REAR - .25, 1.05), s,
                    reach=.42, drop=.55, w=.16)
        a.part('Tail_lamps', 'Undercarriage').box((.2, .05, .1), loc=(s * .75, REAR - .05, .95), bevel=0)
        a.part('Tail_lenses', 'EliteGlow').box((.16, .01, .07), loc=(s * .75, REAR - .02, .95), bevel=0)
    a.part('Kit_hooks', 'Steel').box((.16, .1, .12), loc=(0, REAR - .02, .8), bevel=0)               # tow pintle
    # Stowage on the bed's front corners: a tarp roll and a box.
    P.canvas_roll(a, (0, -1.3, 1.36), 1.6, r=.12)
    K.chamfer_box(a.part('Stowage', 'Crate'), (.4, .3, .28), loc=(.8, -1.25, 1.38), c=.02)


def elite_mlrs(a):
    """The elite rocket launcher: see the module docstring."""
    _chassis(a)
    _cab(a)
    _module(a)
    _rear(a)
    k.clean(a)


BUILDERS = {
    'elite_mlrs': (elite_mlrs, dict(ao_distance=.55, grime_height=.7)),
}
