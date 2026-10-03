"""Prompt 35 wave 3 (lane B): the battlefield searchlight rebuilt from scratch (spec: Tools/blender/specs/searchlight.json).

A 150 cm defence searchlight of the Sperry 60-inch class, set up by the Accord at the base's edge (the def's modelSize
3.6 x 3.0 x 2.8 m): the four-wheeled light trailer levelled on its corner jacks behind a low sandbag arc, the drawbar
resting on a block; on the trailer's turntable the yoke (`Turret`, it turns at 30 degrees a second) carrying the big
drum on its trunnions: the front door with the lens and its vertical louvre bars (`Lens`, the beam's origin
`Muzzle_main`), the ribbed barrel, the rear door with the arc-lamp feed and the ventilation hood on top, the training
handles and the elevation quadrant; the operator's control box and stool; the generator skid behind it (radiator,
exhaust, fuel can) with the cable run to the light; a field telephone on a post with its whip.

Its own body: no shape is shared with the flare searchlight tower or the fortress's lights.
Runtime nodes kept: `Turret`, `Muzzle_main`; old part names `Drum`, `Lens`, `Yoke`, `Trailer`, `Generator`,
`Sandbags`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
DECK = .62              # the trailer deck's top
TT = (0, .1, DECK + .1)  # the yoke's yaw pivot
DR = .62                # the drum's radius
DZ = 1.2               # the drum axis above the yoke pivot
TILT = math.radians(12)  # the drum raised a little at rest


def _ground(a, rng):
    outline = [(-1.5, -1.45), (.2, -1.6), (1.5, -1.3), (1.55, .6), (1.3, 1.75), (-.3, 1.8), (-1.5, 1.5)]
    P.earth_pad(a, outline, .12, taper=.9)
    # A low arc of sandbags round the front and the right (the side the enemy comes from).
    R = 1.42
    path = [(math.sin(t) * R, .1 - math.cos(t) * R, .1) for t in [math.radians(d) for d in range(-95, 60, 15)]]
    P.sandbag_run(a, path, courses=2, bag=(.55, .32, .16), part='Sandbags', seed=91, lean=True)
    st = a.part('Stones', 'Rock')
    for j in range(9):
        z = rng.uniform(.05, .11)
        st.box((z * 1.3, z, z * .7), loc=(rng.uniform(-1.4, 1.4), rng.uniform(-1.4, 1.6), .08 + z * .2),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)
    for i in range(6):
        u = i * math.tau / 6
        K.dust(a, (math.cos(u) * 1.3, .1 + math.sin(u) * 1.3, .08), radius=.9, k=.28)


def _trailer(a):
    tr = a.part('Trailer', 'Team')
    k.block(tr, (1.5, 2.1, .16), loc=(0, .15, DECK - .08), chamfer=.04)
    fr = a.part('Trailer_frame', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.1, 2.2, .14), loc=(s * .55, .15, DECK - .23), bevel=0)
    for y in (-.6, .9):
        fr.box((1.2, .1, .12), loc=(0, y, DECK - .23), bevel=0)
    # The drawbar to the rear, resting on a timber block, its towing eye.
    fr.limb((-.5, 1.15, DECK - .25), (0, 1.75, .28), .08, .08, bevel=0)
    fr.limb((.5, 1.15, DECK - .25), (0, 1.75, .28), .08, .08, bevel=0)
    a.part('Kit_hooks', 'Steel').torus(.06, .016, loc=(0, 1.84, .28), rot=(0, R90, 0), seg=8, ring=4)
    k.block(a.part('Blocks', 'Wood'), (.3, .25, .2), loc=(0, 1.75, .18), chamfer=.03)
    # Four wheels on two axles, the corner jacks let down onto timber pads.
    for y in (-.45, .75):
        a.part('Axles', 'Undercarriage').cyl(.05, 1.5, loc=(0, y, .32), rot=(0, R90, 0), seg=6, bevel=0)
        for s in (-1, 1):
            P.tread_wheel(a, (s * .72, y, .32), .26, .18, s, seg=12, rim_seg=8, nuts=5)
    for sx in (-1, 1):
        for y in (-.85, 1.15):
            jack = a.part('Jacks', 'Steel')
            jack.box((.08, .08, DECK - .1), loc=(sx * .7, y, (DECK - .1) / 2 + .1), bevel=0)
            k.lathe(jack, [(.09, 0), (.09, .03), (.04, .05)], loc=(sx * .7, y, .1), seg=8)
            a.part('Jack_pads', 'Wood').box((.26, .26, .05), loc=(sx * .7, y, .1), bevel=0)
            K.handle(a.part('Kit_handles', 'Steel'), (sx * .7, y - .06, DECK - .05), (sx * .7, y + .06, DECK - .05),
                     (sx, 0, 0), h=.06, r=.01)
    k.ring(a.part('Turntable', 'Steel'), [(.5, -.04), (.58, -.04), (.58, .06), (.5, .06)], loc=TT, seg=16)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (TT[0], TT[1], TT[2] - .02), (0, 0, 1), .62, 10, r=.022, h=.03)


def _light(a):
    t = a.pivot('Turret', TT)
    yoke = a.part('Yoke', 'Armor', t)
    k.lathe(yoke, [(.55, 0), (.55, .08), (.45, .12), (0, .12)], seg=16, worn=(1,))
    for s in (-1, 1):
        k.extrude(yoke, [(-.25, .1), (.25, .1), (.12, DZ + .05), (-.12, DZ + .05)], .09, loc=(s * (DR + .14), 0, 0),
                  axis='X', chamfer=.025)
        a.part('Trunnions', 'Steel', t).cyl(.09, .1, loc=(s * (DR + .2), 0, DZ), rot=(0, R90, 0), seg=10, bevel=0)
    # The drum: a ribbed barrel lying along Y, raised TILT.
    c = (0, 0, DZ)
    rot = (R90 - TILT, 0, 0)                 # lathe +Z onto the drum's forward axis (to -Y, raised)
    drum = a.part('Drum', 'Team', t)
    k.lathe(drum, [(DR * .9, -.5), (DR, -.44), (DR, .4), (DR * .97, .46), (DR * .9, .48)], loc=c, rot=rot, seg=18,
            worn=(1, 3))
    ribs = a.part('Drum_ribs', 'Armor', t)
    for z in (-.3, -.05, .2):
        ribs.cyl(DR + .025, .05, loc=_on(c, z), rot=rot, seg=18, bevel=0)
    # The front door: its rim, the lens behind the louvre bars.
    k.ring(a.part('Door_rim', 'Steel', t), [(DR * .82, 0), (DR + .02, 0), (DR + .02, .06), (DR * .82, .06)],
           loc=_on(c, .46), rot=rot, seg=18)
    a.part('Lens', 'Lamp', t).cyl(DR * .82, .02, loc=_on(c, .5), rot=rot, seg=18, bevel=0)
    bars = a.part('Louvres', 'Undercarriage', t)
    for j in range(7):
        x = -DR * .7 + j * DR * .7 / 3
        h = 2 * math.sqrt(max(.01, (DR * .82) ** 2 - x * x))
        bars.box((.025, .03, h), loc=_on(c, .53, dx=x), rot=(-TILT, 0, 0), bevel=0)
    a.pivot('Muzzle_main', _on(c, .58), t)
    # The rear door, the arc-lamp feed box, the ventilation hood (chimney) on top.
    back = a.part('Rear_door', 'Armor', t)
    k.lathe(back, [(DR * .9, -.5), (DR * .8, -.56), (DR * .3, -.6), (0, -.6)], loc=c, rot=rot, seg=14)
    k.block(a.part('Lamp_feed', 'Undercarriage', t), (.3, .2, .3), loc=_on(c, -.62, up=-.1), rot=(-TILT, 0, 0),
            chamfer=.03)
    hood = a.part('Vent_hood', 'Armor', t)
    k.lathe(hood, [(.15, 0), (.15, .18), (.24, .2), (.24, .26), (0, .3)], loc=_on(c, -.15, up=DR - .02),
            rot=(-TILT, 0, 0), seg=10)
    # Training handles at the back, the elevation quadrant on the right trunnion arm.
    for s in (-1, 1):
        K.handle(a.part('Kit_handles', 'Steel', t), _on(c, -.58, dx=s * .35, up=-.2), _on(c, -.58, dx=s * .35, up=.2),
                 (0, 1, 0), h=.12, r=.015)
    k.sweep(a.part('Quadrant', 'Steel', t), [(-.015, -.02), (.015, -.02), (.015, .02), (-.015, .02)],
            [(-(DR + .24), .35 * math.cos(u), DZ + .35 * math.sin(u)) for u in [math.radians(d) for d in range(-40, 50, 15)]])
    a.part('Team_band', 'Team', t).box((.14, .5, .02), loc=_on(c, -.05, up=DR + .005), rot=(-TILT, 0, 0), bevel=0)
    return t


def _on(c, z, dx=0.0, up=0.0):
    """A point on the drum's axis z metres forward, dx to the side, `up` off the axis."""
    cz, sz = math.cos(TILT), math.sin(TILT)
    return (c[0] + dx, c[1] - z * cz - up * sz, c[2] + z * sz + up * cz)


def _station(a):
    # The operator's control box on a stand and his stool beside the trailer (left).
    k.block(a.part('Control_box', 'Armor'), (.35, .25, .35), loc=(1.1, -.2, .9), chamfer=.03)
    a.part('Control_stand', 'Steel').box((.06, .06, .82), loc=(1.1, -.2, .49), bevel=0)
    a.part('Dials', 'Glass').box((.22, .01, .12), loc=(1.1, -.33, .95), bevel=0)
    a.part('Stool', 'Wood').cyl(.16, .05, loc=(1.15, .35, .5), seg=8, bevel=0)
    a.part('Stool', 'Wood').cyl(.03, .42, loc=(1.15, .35, .29), seg=5, bevel=0)
    # The generator skid behind on the right: frame, engine box, radiator grille, exhaust, a fuel can.
    gx, gy = -.95, 1.35
    k.block(a.part('Generator_skid', 'Undercarriage'), (.95, .7, .1), loc=(gx, gy, .13), chamfer=.02)
    gen = a.part('Generator', 'Armor')
    k.block(gen, (.85, .6, .55), loc=(gx, gy, .455), chamfer=.04)
    K.grille(a, (gx, gy - .305, .45), .5, .35, facing=(0, -1, 0), slats=4, frame_mat='Armor')
    K.exhaust(a, (gx + .3, gy + .1, .73), r=.04, length=.35, direction=(0, 0, 1), muffler=False, cap=True)
    K.soot(a, (gx + .3, gy + .1, 1.1), radius=.3, k=.4)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (gx - .5, gy + .2, .08), rot=(0, 0, .3))
    a.part('Kit_cables', 'Undercarriage').tube([(gx + .35, gy - .2, .2), (-.3, .9, .1), (0, .4, DECK + .02)], .025,
                                               seg=4)
    # The field telephone on a post with its whip.
    a.part('Stakes', 'Wood').cyl(.04, 1.0, loc=(1.25, 1.35, .5), seg=5, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.22, .12, .18), loc=(1.25, 1.28, .9), chamfer=.015)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.3, 1.45, 1.0), h=1.2, r=.02, lean=.1)


def searchlight(a):
    """The battlefield searchlight: see the module docstring."""
    rng = random.Random(3581)
    _ground(a, rng)
    _trailer(a)
    _light(a)
    _station(a)
    k.clean(a)


BUILDERS = {
    'searchlight': (searchlight, dict(ao_distance=.45, grime_height=.5)),
}
