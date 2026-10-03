"""Prompt 35 wave 6 (lane B): the inflatable decoy rebuilt to follow the wave 2 gun turret's outline (spec:
Tools/blender/specs/inflatable_decoy.json; the lead's call 2 on the wave 3 questions).

An inflatable replica of `gun_turret` (def decoy.mimic gun_turret) of the kind used in the war in Ukraine, laid out on
the gun turret's own plan and heights so it reads as the real tower at the battle camera: a ground sheet under a
puffed, printed "concrete" casemate with the same battered square sides and deck height (its joints and Team band
printed on), the turret as an inflated box on the gun turret's plan (the chisel front, the bustle) with printed
spaced-armour side plates, the puffed mantlet and the full-length inflated barrel at the real gun's height with its
fume-extractor bulge and a fabric muzzle collar (sagging a little at the tip), a printed cupola, hatch and sight
block, the inflated bustle basket with a printed tarp roll, two fibreglass whips; the giveaways for a close look:
seams, a repair patch, the tethers to stakes, the petrol blower with its hose, a fuel can and the folded bag.

Its own geometry: the gun turret's dimensions are followed, no mesh is taken from its builder. It does not turn (no
`Turret`: the def is unarmed). Old part names kept: `Pad`, `Walls`, `Skin`, `Seams`, `Team_band`, `Dome`, `Fabric`,
`Painted_hatches`, `Patches`, `Antenna`, `Tethers`, `Stakes`, `Blower*`, `Hose`, `Jerrycans`, `Transport_bag`.
The turret stands traversed 38 degrees to the front left: with the gun straight ahead the replica is 8.97 x 5.25 x 4.0 m,
which the def's modelSize (5.0 x 4.6 x 2.6) cannot hold; traversed it is about 7.6 x 6.8 x 4.0 m, the modelSize's
proportions, so the size gate and glb_check pass, and the runtime draws it at 5.0 / 7.6 = 0.66 x the real tower. A
modelSize of its own size would draw it 1:1 (lead / owner question, WAVE_6_REPORT.md). Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
DECK = 1.25                      # the gun turret's casemate deck
TZ = 1.34                        # its turret base
TH = .78                         # its turret height
PLAN = [(-.75, -2.0), (.75, -2.0), (1.65, -1.2), (1.65, 1.6), (1.35, 2.4), (-1.35, 2.4), (-1.65, 1.6), (-1.65, -1.2)]


def _ground(a):
    k.block(a.part('Pad', 'Canvas'), (5.0, 5.2, .02), loc=(0, .1, .01), rot=(0, 0, .03), chamfer=0)
    st = a.part('Stakes', 'Steel')
    for x, y in ((-2.55, -2.55), (2.55, -2.5), (2.5, 2.6), (-2.55, 2.6), (3.25, -4.15), (-2.6, .2)):
        st.cyl(.025, .35, loc=(x, y, .12), rot=(.25, 0, 0), seg=5, bevel=0)


def _casemate(a):
    """The puffed casemate: the gun turret's battered square on a fabric skin, printed joints and Team band."""
    w = a.part('Walls', 'Plaster')
    k.extrude(w, [(-2.3, -2.3), (2.3, -2.3), (2.3, 2.3), (-2.3, 2.3)], DECK - .02, loc=(0, 0, .02 + (DECK - .02) / 2),
              axis='Z', chamfer=.18, corner=.3, taper=(.82, .82), caps=(False, True))
    seams = a.part('Seams', 'Undercarriage')
    for v in (-1.3, 1.3):
        seams.box((3.5, .03, .012), loc=(0, v, DECK + .005), bevel=0)
        seams.box((.03, 3.5, .012), loc=(v, 0, DECK + .005), bevel=0)
    team = a.part('Team_band', 'Team')
    for s in (-1, 1):
        team.box((.03, 3.5, .16), loc=(s * 2.03, 0, DECK - .22), rot=(0, s * .35, 0), bevel=0)
        team.box((3.5, .03, .16), loc=(0, s * 2.03, DECK - .22), rot=(-s * .35, 0, 0), bevel=0)
        # The printed form-tie dots and the corner seams of the skin.
        for f in (-1.2, 0, 1.2):
            seams.box((.05, .05, .012), loc=(s * 2.17, f, .55), rot=(0, s * .35, 0), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            seams.tube([(sx * 2.28, sy * 2.28, .05), (sx * 1.9, sy * 1.9, DECK - .03)], .015, seg=4)


def _turret(a):
    """The inflated turret on the gun turret's plan: puffed edges, printed plates and fittings, the barrel."""
    sk = a.part('Skin', 'Armor')
    a.part('Patch_side', 'Canvas').box((.02, .5, .3), loc=(-2.02, .8, .7), rot=(0, -.35, .1), bevel=0)
    k.extrude(sk, PLAN, TH, loc=(0, 0, TZ + .08 + TH / 2), axis='Z', chamfer=.12, corner=.18, taper=(.86, .86),
              caps=(False, True))
    k.extrude(a.part('Skin', 'Armor'), [(-1.6, -1.6), (1.6, -1.6), (1.6, 2.0), (-1.6, 2.0)], .12,
              loc=(0, 0, DECK + .06), axis='Z', chamfer=.04, corner=.3)
    top = TZ + .08 + TH
    pr = a.part('Painted_hatches', 'Charred')
    for s in (-1, 1):
        k.extrude(a.part('Turret_plates', 'Team'), [(-1.0, .1), (1.5, .1), (1.4, .62), (-1.0, .58)], .03,
                  loc=(s * 1.63, 0, TZ), axis='X', chamfer=.01)
    pr.cyl(.36, .012, loc=(.75, .4, top + .005), seg=12, bevel=0)
    pr.box((.6, .75, .012), loc=(-.75, .6, top + .005), bevel=0)
    pr.box((1.4, .025, .012), loc=(0, -1.8, top + .005), bevel=0)
    pr.box((2.6, .025, .012), loc=(0, 1.0, top + .005), bevel=0)
    k.block(a.part('Dome', 'Armor'), (.4, .55, .34), loc=(-.95, -1.25, top - .02), chamfer=.1)
    pr.box((.3, .02, .14), loc=(-.95, -1.535, top + .2), bevel=0)
    k.lathe(a.part('Dome', 'Armor'), [(.36, 0), (.36, .1), (.3, .2), (0, .24)], loc=(.75, .4, top - .02), seg=12,
            worn=(1,))
    # The puffed mantlet and the full-length inflated barrel at the real gun's height, sagging at the tip.
    k.block(a.part('Fabric', 'Armor'), (.95, .55, .6), loc=(0, -2.12, TZ + .36), chamfer=.2)
    z0 = TZ + .66
    pts = [(0, -2.3, z0), (0, -3.4, z0), (0, -4.6, z0 - .05), (0, -5.5, z0 - .12), (0, -5.9, z0 - .17)]
    a.part('Fabric', 'Armor').tube(pts, .12, seg=10)
    k.lathe(a.part('Fabric', 'Armor'), [(.12, -.25), (.17, -.15), (.17, .15), (.12, .25)], loc=(0, -3.0, z0),
            rot=K.FORWARD, seg=10)
    k.lathe(a.part('Fabric', 'Armor'), [(.12, -.1), (.16, -.06), (.16, .06), (.12, .1)], loc=(0, -5.85, z0 - .16),
            rot=(R90 - .08, 0, 0), seg=10)
    seams = a.part('Barrel_seams', 'Undercarriage')
    for y in (-3.9, -4.9):
        seams.cyl(.125, .02, loc=(0, y, z0 - (.02 if y > -4.6 else .08)), rot=K.FORWARD, seg=10, bevel=0)
    # The inflated bustle basket with a printed tarp roll, two fibreglass whips, a repair patch.
    k.block(a.part('Skin', 'Armor'), (2.6, .52, .45), loc=(0, 2.68, TZ + .3), chamfer=.12)
    pr.box((1.8, .02, .2), loc=(0, 2.95, TZ + .55), bevel=0)
    for x, h in ((1.1, 1.6), (-1.1, 1.45)):
        a.part('Antenna', 'Steel').cyl(.02, h, loc=(x, 2.2, top + h / 2), seg=4, bevel=0)
    a.part('Patches', 'Canvas').box((.45, .35, .02), loc=(1.2, -.6, top + .006), rot=(0, 0, .3), bevel=0)


def _giveaways(a):
    teth = a.part('Tethers', 'Undercarriage')
    top = TZ + .08 + TH
    for (x, y), (px, py, pz) in (((-2.55, -2.55), (-1.4, -1.2, top - .1)), ((2.55, -2.5), (1.4, -1.2, top - .1)),
                                 ((2.5, 2.6), (1.2, 2.3, top - .1)), ((-2.55, 2.6), (-1.2, 2.3, top - .1)),
                                 ((3.25, -4.15), (3.37, -4.3, TZ + .55))):
        teth.tube([(x, y, .25), (px, py, pz)], .008, seg=3)
    # The petrol blower on its frame behind the casemate, its guard and hose into the skin; a fuel can; the bag.
    bx, by = -2.25, 2.55
    k.block(a.part('Blower', 'Armor'), (.55, .45, .4), loc=(bx, by, .05), chamfer=.05)
    k.ring(a.part('Blower_guard', 'Steel'), [(.22, -.05), (.25, -.05), (.25, .05), (.22, .05)], loc=(bx + .4, by, .28),
           rot=(0, R90, 0), seg=10)
    fr = a.part('Blower_frame', 'Steel')
    fr.tube([(bx - .35, by - .3, .02), (bx - .35, by - .3, .5), (bx + .35, by - .3, .5), (bx + .35, by - .3, .02)],
            .015, seg=4)
    a.part('Hose', 'Rubber').tube([(bx + .5, by, .28), (bx + .7, by - .5, .15), (bx + .2, by - 1.0, .3),
                                   (bx, 2.25, .5)], .07, seg=6)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (bx - .6, by + .1, .02), rot=(0, 0, .4), scale=.9)
    k.block(a.part('Transport_bag', 'Canvas'), (.9, .6, .35), loc=(2.0, 2.55, .02), rot=(0, 0, .2), chamfer=.12)


def _details(a):
    """Printed and sewn details that read at the battle camera: the apron and its joints printed on the ground
    sheet, fabric panel seams on the casemate sides, D-rings and inflation valves along its top edge, printed
    periscopes, smoke dischargers and boxes on the turret (turned with it), guy ropes."""
    j = a.part('Pad_print', 'Undercarriage')
    for i in range(-2, 3):
        j.box((4.7, .03, .008), loc=(0, i * 1.0, .025), bevel=0)
        j.box((.03, 4.8, .008), loc=(i * 1.0, .1, .025), bevel=0)
    seams = a.part('Seams', 'Undercarriage')
    for s in (-1, 1):
        for f in (-1.6, -.8, .0, .8, 1.6):
            seams.box((.02, .02, 1.1), loc=(s * 2.1, f, .62), rot=(0, s * .35, 0), bevel=0)
            seams.box((.02, .02, 1.1), loc=(f, s * 2.1, .62), rot=(-s * .35, 0, 0), bevel=0)
    rings = a.part('D_rings', 'Steel')
    valves = a.part('Valves', 'BarrelRed')
    for s in (-1, 1):
        for f in (-1.5, -.5, .5, 1.5):
            rings.box((.08, .03, .08), loc=(f, s * 1.93, DECK - .05), bevel=0)
            rings.box((.03, .08, .08), loc=(s * 1.93, f, DECK - .05), bevel=0)
        valves.cyl(.05, .06, loc=(s * 1.2, -1.9, DECK - .02), seg=6, bevel=0)
    top = TZ + .08 + TH
    pr = a.part('Painted_hatches', 'Charred')
    for x, y in ((.45, .1), (1.05, .1), (.75, .75), (.85, -.5)):
        pr.box((.14, .1, .06), loc=(x, y, top + .02), bevel=0)
    for s in (-1, 1):
        for i in range(4):
            pr.box((.09, .09, .09), loc=(s * 1.38, -.9 + i * .14, TZ + .7), bevel=0)
        pr.box((.5, .3, .26), loc=(s * .8, 2.7, TZ + .6), bevel=0)
    guy = a.part('Tethers', 'Undercarriage')
    for (x, y) in ((-2.55, .2), (2.55, .3)):
        guy.tube([(x, y, .05), (x * .85, y, DECK - .05)], .008, seg=3)


TURRET_PARTS = ('Skin', 'Turret_plates', 'Painted_hatches', 'Dome', 'Fabric', 'Barrel_seams', 'Antenna', 'Patches')
YAW = math.radians(38)           # the turret traversed to the front left (see the module docstring)


def _traverse(a):
    """Turn the turret's pieces about the race centre by YAW (the decoy stands with its gun laid off the bow)."""
    import bmesh
    from mathutils import Matrix
    m = Matrix.Rotation(YAW, 3, 'Z')
    for (name, mat, parent), shape in a.shapes.items():
        if name in TURRET_PARTS:
            bmesh.ops.rotate(shape.bm, cent=(0, 0, 0), matrix=m, verts=list(shape.bm.verts))


def inflatable_decoy(a):
    """The inflatable decoy: see the module docstring."""
    _ground(a)
    _casemate(a)
    _turret(a)
    _details(a)
    _traverse(a)
    _giveaways(a)
    k.clean(a)


BUILDERS = {
    'inflatable_decoy': (inflatable_decoy, dict(ao_distance=.6, grime_height=.4)),
}
