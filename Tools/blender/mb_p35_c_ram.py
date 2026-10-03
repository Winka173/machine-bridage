"""Prompt 35 wave 9 (lane C): the C-RAM tower and its two branches rebuilt from scratch together (specs:
Tools/blender/specs/c_ram.json, c_ram_a.json, c_ram_b.json).

All three stand on one FOB position (the def's 5.5 x 5.5 m tower; the old files' 5.6 m square kept): outrigger
pads and a gravel apron, an L of HESCO bastions on the left and rear with a T-wall on the right front, the
low flatbed trailer on its jacks with the towed generator behind it and the cables between them, the counter-fire
radar mast at the rear left corner (`Radar`), fuel drums, ammunition cans, a floodlight and warning boards, so the
branches read as the same site with a new launcher:

- c_ram (c_ram_gatling: the Centurion, a Phalanx Block 1B land mount; unit_refs Centurion C-RAM / Phalanx M61):
  on the trailer the below-deck cabinet, the white mount with the radome above the six-barrel M61 and its
  shroud, the ammunition drum, the search antenna bulge; the LCMR head spinning on its mast.
- c_ram_a (c_ram.centurion, the faster interceptor): the same Centurion upgraded, the electro-optical (FLIR) box
  on the radome's side, a second drum's feed chute, and the taller mast with the radome ball (`Radar`).
- c_ram_b (c_ram.dome, tamir: Iron Dome's launcher): on the same trailer the Tamir launcher's 20-cell box raised
  on its rams and hinge (cells with their bores), the EL/M-2084's flat array on the mast.

Runtime nodes kept: `Turret`, `Main_cannon` / `Muzzle_brake` (c_ram, c_ram_a), the `Launcher_*` parts (c_ram_b),
`Muzzle_main`, `Muzzle_gun`, `Radar`; `Mount_APS` added (the defs have APS). Metres, +Z up, -Y front, +X left.
Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
G = .04
DECK = .92           # the trailer deck
TY = -.35            # the mount's centre on the deck
MAST = (1.95, 1.95)  # the radar mast's foot


def _site(a, seed=0, extra_hesco=False, cases=9):
    """Apron, HESCO, T-wall, trailer on its jacks, generator, cables, drums, cans, floodlight, boards, the mast."""
    # Gravel patches where the jacks and the trailer's tyres stand (the ground is the floor).
    gp = a.part('Base', 'Rock')
    for x, y, w, l in ((1.52, -1.75, .7, .7), (-1.52, -1.75, .7, .7), (1.52, 2.0, .7, .7), (-1.52, 2.0, .7, .7),
                       (0, 1.45, 2.3, 1.4)):
        k.extrude(gp, [(-w / 2, -l / 2), (w / 2, -l / 2), (w / 2, l / 2), (-w / 2, l / 2)], .03, loc=(x, y, G + .015),
                  axis='Z', chamfer=0, corner=0, caps=(False, True))
    # HESCO: an L on the left and rear (the entry at the rear right), a T-wall at the right front.
    for y in (-1.9, -.84, .22):
        K.hesco(a, (2.32, y, G), size=(1.06, 1.06, 1.25), cells=1, yaw=R90)
    for x in ((.7, -.36) if extra_hesco else (.7,)):
        K.hesco(a, (x, 2.32, G), size=(1.06, 1.06, 1.25), cells=1)
    K.t_wall(a, (-2.3, -1.7, G), h=2.0, w=1.3, yaw=R90)
    a.part('Team_band', 'Team').box((.02, 1.0, .25), loc=(-2.17, -1.7, G + 1.3), bevel=0)
    # The flatbed trailer: frame, deck, two axles at the rear with twin tyres, the drawbar, four jacks on pads.
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.14, 4.3, .22), loc=(s * .55, .1, DECK - .2), bevel=0)
    deck = a.part('Deck', 'Team')
    k.extrude(deck, [(-1.1, -2.0), (1.1, -2.0), (1.1, 2.2), (-1.1, 2.2)], .1, loc=(0, 0, DECK - .05), axis='Z',
              chamfer=.02, corner=.04, caps=(False, True))
    tread = a.part('Deck_plates', 'Steel')
    for i in range(6):
        tread.box((2.0, .02, .012), loc=(0, -1.85 + i * .25, DECK + .005), bevel=0)
    st = a.part('Kit_steel', 'Steel')
    for s in (-1, 1):
        st.box((.03, 4.2, .12), loc=(s * 1.1, .1, DECK - .05), bevel=0)
        for y in (-1.5, -.5, .5, 1.5):
            st.box((.04, .04, .1), loc=(s * 1.1, y, DECK + .02), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in (1.15, 1.75):
        K.axle(ax, y, .38, .72, r=.05, diff=False)
        for s in (-1, 1):
            C.plain_wheel(a, (s * .86, y, .38), .38, .22, s, seg=10)
    for s in (-1, 1):
        a.part('Mudguards', 'Undercarriage').box((.32, 1.25, .03), loc=(s * .88, 1.45, .84), bevel=0)
        a.part('Mudflaps', 'Rubber').box((.3, .02, .3), loc=(s * .88, 2.08, .62), bevel=0)
    fr.limb((-.5, 2.2, DECK - .25), (0, 3.0, .55), .05, .05, bevel=0)
    fr.limb((.5, 2.2, DECK - .25), (0, 3.0, .55), .05, .05, bevel=0)
    k.lathe(a.part('Kit_steel', 'Steel'), [(.07, 0), (.07, .05), (0, .06)], loc=(0, 3.04, .52), rot=K.BACKWARD, seg=8)
    jk = a.part('Jacks', 'Steel')
    pads = a.part('Pads', 'Steel')
    for s in (-1, 1):
        for y in (-1.75, 2.0):
            jk.box((.5, .14, .14), loc=(s * 1.3, y, DECK - .3), bevel=0)
            jk.cyl(.05, DECK - .35, loc=(s * 1.52, y, G + (DECK - .35) / 2), seg=6, bevel=0)
            k.lathe(pads, [(.2, G), (.2, G + .04), (.07, G + .08)], loc=(s * 1.52, y, 0), seg=8)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.12, .02, .06), loc=(s * .9, 2.21, DECK - .1), bevel=0)
    # The towed generator behind the trailer's right (entry side) and the cables to the mount.
    gen = a.part('Generator', 'Armor')
    k.block(gen, (1.0, 1.5, .9), loc=(-1.75, 1.5, G + .55), chamfer=.04)
    K.grille(a, (-1.25, 1.5, G + .75), .9, .5, facing=(1, 0, 0), slats=5, frame_mat='Armor')
    K.exhaust(a, (-1.95, 1.2, G + 1.1), r=.05, length=.35, direction=(0, 0, 1))
    for x in (-2.15, -1.35):
        a.part('Generator_skids', 'Undercarriage').box((.1, 1.6, .1), loc=(x, 1.5, G + .05), bevel=0)
    a.part('Generator_panel', 'Steel').box((.02, .4, .3), loc=(-1.245, 1.0, G + .5), bevel=0)
    a.part('Generator_lamp', 'Lamp').box((.02, .06, .06), loc=(-1.24, .9, G + .72), bevel=0)
    K.handle(a.part('Kit_handles', 'Steel'), (-1.24, 1.9, G + .4), (-1.24, 1.9, G + .7), (1, 0, 0), h=.04, r=.01)
    for y in (.95, 2.05):
        a.part('Kit_steel', 'Steel').box((.9, .05, .2), loc=(-1.75, y, G + .2), bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(-1.25, 1.1, G + .5), (-.9, .6, G + .03), (-.4, .3, G + .03),
                                                (-.3, TY + .4, DECK)], .022, seg=5)
    a.part('Kit_cables', 'Undercarriage').tube([(-1.3, 2.0, G + .4), (-.6, 2.6, G + .03), (MAST[0], MAST[1] + .3, G + .03),
                                                (MAST[0] - .1, MAST[1], G + .5)], .018, seg=4)
    # Stores: fuel drums, ammunition cans, a fire extinguisher, the floodlight, warning boards.
    for i, (x, y) in enumerate(((-2.2, .2), (-2.25, .8))):
        K.fuel_drum(a.part('Fuel_drums', 'BarrelRed' if i == 1 else 'Fuel'), a.part('Kit_bands', 'Steel'), (x, y, G),
                    r=.27, h=.86)
    C.ammo_tins(a, (1.45, 2.6, G), n=3, size=(.14, .32, .22), axis='X')
    a.part('Extinguisher', 'BarrelRed').cyl(.07, .5, loc=(1.3, -2.45, G + .25), seg=8, bevel=0)
    K.floodlight(a, (-2.4, 2.4, G), facing=(.4, -1, -.4), pole=2.6)
    bd = a.part('Signs', 'Hazard')
    for x, y, u in ((-1.0, -2.6, 0), (1.0, -2.65, .1)):
        bd.box((.5, .02, .35), loc=(x, y, G + .85), rot=(0, 0, u), bevel=0)
        a.part('Sign_posts', 'Wood').box((.05, .05, .9), loc=(x, y + .03, G + .45), bevel=0)
    C.casings(a, (0, -1.6), 1.0, cases, r=.012, length=(.09, .16), seed=seed + 5, z=G + .05)
    K.dust(a, (0, 0, G), radius=2.8, k=.14)


def _mast(a, h, head):
    """The radar mast at the rear left corner: the guyed telescopic mast and its head (`Radar` spins)."""
    x, y = MAST
    m = a.part('Radar_mast', 'Steel')
    k.block(m, (.5, .5, .12), loc=(x, y, G), chamfer=.02)
    for i, (r, z0, z1) in enumerate(((.09, G, h * .45), (.07, h * .45, h * .8), (.055, h * .8, h))):
        m.cyl(r, z1 - z0 + .1, loc=(x, y, (z0 + z1) / 2), seg=8, bevel=0)
        m.cyl(r * 1.25, .06, loc=(x, y, z1 - .02), seg=8, bevel=0)
    guy = a.part('Kit_cables', 'Undercarriage')
    for u in (R90 * .5, R90 * 1.5, R90 * 2.5):
        gx, gy = x + math.cos(u + .5) * 1.0, y + math.sin(u + .5) * 1.0
        guy.tube([(x, y, h * .78), (gx, gy, G + .02)], .006, seg=3)
        a.part('Kit_steel', 'Steel').cyl(.025, .2, loc=(gx, gy, G + .1), seg=5, bevel=0)
    k.block(a.part('Radar_turntable', 'Armor'), (.32, .32, .12), loc=(x, y, h), chamfer=.02)
    r = a.pivot('Radar', (x, y, h + .12))
    if head == 'lcmr':        # the LCMR's drum head with its four faces
        k.lathe(a.part('Radar_back', 'Armor', r), [(.26, 0), (.3, .05), (.3, .55), (.24, .62), (0, .64)], seg=8,
                worn=(1, 3))
        for i in range(4):
            u = i * R90
            a.part('Radar_face', 'Undercarriage', r).box((.34, .02, .42), loc=(math.cos(u) * .305, math.sin(u) * .305,
                                                                                .3), rot=(0, 0, u + R90), bevel=0)
        a.part('Radar_iff', 'Steel', r).cyl(.03, .3, loc=(0, 0, .8), seg=5, bevel=0)
        K.beacon(a, (.15, 0, .64), parent=r, r=.05)
        a.part('Radar_beacon', 'Alloy', r).box((.03, .03, .02), loc=(.15, 0, .64), bevel=0)
    elif head == 'ball':      # the radome ball on its neck
        a.part('Radar_neck', 'Steel', r).cyl(.08, .35, loc=(0, 0, .17), seg=8, bevel=0)
        k.lathe(a.part('Radar_ball', 'PlasterWhite', r), [(0, .3), (.3, .36), (.44, .62), (.44, .8), (.3, 1.06),
                                                          (0, 1.12)], seg=10, worn=(3,))
        a.part('Radar_band', 'Team', r).cyl(.45, .05, loc=(0, 0, .7), seg=12, bevel=0)
        K.beacon(a, (0, 0, 1.12), parent=r, r=.05)
        a.part('Radar_beacon', 'Alloy', r).box((.03, .03, .02), loc=(0, 0, 1.13), bevel=0)
    else:                     # the EL/M-2084 flat array on its arm
        a.part('Radar_arm', 'Steel', r).limb((0, 0, 0), (0, -.1, .35), .06, .06, bevel=0)
        k.block(a.part('Radar_back', 'Armor', r), (1.3, .22, .9), loc=(0, -.05, .35), chamfer=.04)
        a.part('Radar_face', 'Undercarriage', r).box((1.2, .02, .8), loc=(0, -.17, .8), bevel=0)
        st = a.part('Radar_iff', 'Steel', r)
        st.box((1.2, .04, .06), loc=(0, -.05, 1.3), bevel=0)
        K.beacon(a, (.55, 0, 1.25), parent=r, r=.05)
        a.part('Radar_beacon', 'Alloy', r).box((.03, .03, .02), loc=(.55, 0, 1.26), bevel=0)


def _phalanx(a, eo=False):
    """The Centurion's Phalanx mount on the deck: cabinet, yaw base, white mount, radome, M61, drum."""
    cab = a.part('Turret_cabinet', 'Armor')
    C.slab_loft(cab, C.octagon(1.4, 1.5, .2, y0=TY + .15), C.octagon(.9, 1.0, .12, y0=TY + .15), DECK, DECK + .72)
    K.grille(a, (0, TY + .79, DECK + .4), .9, .45, facing=(0, 1, 0), slats=5, frame_mat='Armor')
    vents = a.part('Turret_vents', 'Undercarriage')
    for s in (-1, 1):
        vents.box((.02, .8, .25), loc=(s * .58, TY + .15, DECK + .4), rot=(0, -s * .33, 0), bevel=0)
    C.hatch(a, (.4, TY + .55, DECK + .72), r=.18)
    k.lathe(a.part('Turret_base', 'PlasterWhite'), [(.62, DECK + .72), (.62, DECK + .8), (.5, DECK + .9),
                                                    (.5, DECK + 1.0)], loc=(0, TY, 0), seg=14, caps=(False, True))
    tz = DECK + 1.0
    t = a.pivot('Turret', (0, TY, tz))
    a.pivot('Mount_APS', (0, 0, .9), t)
    w = a.part('Turret_white', 'PlasterWhite', t)
    for s in (-1, 1):       # the elevation arms
        k.extrude(w, [(-.35, 0), (.35, 0), (.25, .75), (-.25, .75)], .1, loc=(s * .46, 0, .02), axis='X',
                  chamfer=.015, corner=.02)
    a.part('Turret_trunnion', 'Steel', t).cyl(.08, 1.1, loc=(0, 0, .6), rot=(0, R90, 0), seg=8, bevel=0)
    # The radome above the gun (the search radar's bulge on its front top), the drum under it.
    body = a.part('Turret_body', 'PlasterWhite', t)
    k.lathe(body, [(.4, .55), (.44, .62), (.44, 1.25), (.36, 1.5), (.2, 1.62), (0, 1.66)], loc=(0, .1, 0), seg=14,
            caps=(True, True), worn=(2, 4))
    k.lathe(body, [(.18, 0), (.2, .08), (.2, .2), (0, .24)], loc=(0, -.2, 1.42), rot=(-.6, 0, 0), seg=10)
    a.part('Team_band', 'Team', t).cyl(.445, .08, loc=(0, .1, .7), seg=14, bevel=0)
    k.lathe(a.part('Turret_drum', 'PlasterWhite', t), [(.3, -.5), (.32, -.45), (.32, .45), (.3, .5)],
            loc=(0, .15, .28), rot=K.FORWARD, seg=12)
    a.part('Turret_feed', 'Steel', t).box((.12, .5, .12), loc=(.18, -.2, .35), rot=(-.2, 0, 0), bevel=0)
    # The six-barrel M61 under the radome: the barrel cluster, the clamp, the shroud.
    g = a.part('Main_cannon', 'Steel', t)
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.022, 1.45, loc=(math.cos(u) * .065, -.95, .5 + math.sin(u) * .065), rot=K.FORWARD, seg=5, bevel=0)
    g.cyl(.13, .14, loc=(0, -.45, .5), rot=K.FORWARD, seg=10, bevel=0)
    g.cyl(.11, .06, loc=(0, -1.15, .5), rot=K.FORWARD, seg=10, bevel=0)
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.1, 0), (.12, .04), (.12, .3), (.1, .34)],
            loc=(0, -1.7, .5), rot=K.FORWARD, seg=10)
    a.pivot('Muzzle_main', (0, -2.06, .5), t)
    a.pivot('Muzzle_gun', (0, -2.05, .5), t)
    if eo:                  # Block 1B's electro-optical box on the radome's left, a second feed chute
        eob = a.part('Turret_eo', 'Armor', t)
        k.block(eob, (.22, .34, .3), loc=(.58, -.05, .82), chamfer=.03)
        a.part('Glass', 'Glass', t).box((.16, .01, .16), loc=(.58, -.225, .97), bevel=0)
        a.part('Turret_feed', 'Steel', t).box((.12, .5, .12), loc=(-.18, -.2, .35), rot=(-.2, 0, 0), bevel=0)
        a.part('Turret_eo_arm', 'Steel', t).box((.14, .12, .1), loc=(.48, -.05, .82), bevel=0)


def _iron_dome(a):
    """c_ram_b: the Tamir launcher's 20-cell box raised on its rams on the deck."""
    cab = a.part('Turret_cabinet', 'Armor')
    C.slab_loft(cab, C.octagon(1.6, 1.3, .2, y0=TY + .4), C.octagon(1.2, .9, .12, y0=TY + .4), DECK, DECK + .35)
    tz = DECK + .35
    t = a.pivot('Turret', (0, TY + .3, tz))
    a.pivot('Mount_APS', (0, 0, 1.0), t)
    k.lathe(a.part('Turret_white', 'Armor', t), [(.6, 0), (.6, .08), (.45, .14), (0, .15)], seg=14)
    fr = a.part('Launcher_frame', 'Team', t)
    for s in (-1, 1):
        k.extrude(fr, [(-.5, .1), (.6, .1), (.5, .45), (-.4, .4)], .08, loc=(s * .62, 0, .05), axis='X', chamfer=.01)
    a.part('Launcher_hinge', 'Steel', t).cyl(.07, 1.4, loc=(0, .5, .45), rot=(0, R90, 0), seg=8, bevel=0)
    ang = math.radians(55)
    ca, sa = math.cos(ang), math.sin(ang)
    L, W, D = 2.7, 1.25, .95            # box length (along its axis), width, depth
    # The box's axis points forward and up at `ang`; its rear end sits on the hinge.
    cy, cz = .5 - ca * L / 2, .45 + sa * L / 2
    box = a.part('Launcher_box', 'Team', t)
    k.extrude(box, [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)], L, loc=(0, cy, cz),
              rot=(-ang, 0, 0), axis='Y', chamfer=.03, corner=.03)
    face = a.part('Launcher_face', 'Armor', t)
    fy, fz = .5 - ca * L, .45 + sa * L
    face.box((W + .04, .04, D + .04), loc=(0, fy - .02 * ca, fz + .02 * sa), rot=(R90 - ang, 0, 0), bevel=0)
    tubes = a.part('Launcher_tubes', 'Armor', t)
    bores = a.part('Launcher_tubes_bore', 'Undercarriage', t)
    for c in range(5):
        for r in range(4):
            u = (c - 2) * .23
            v = (r - 1.5) * .21
            # a point on the face plane: across = X, up the face = (0, sa, ca) rotated
            px, py, pz = u, fy - v * sa - .04 * ca, fz + v * ca + .04 * sa
            tubes.cyl(.095, .06, loc=(px, py, pz), rot=(R90 - ang, 0, 0), seg=6, bevel=0)
            bores.box((.13, .13, .02), loc=(px, py - .03 * ca, pz + .03 * sa), rot=(R90 - ang, 0, 0), bevel=0)
    rams = a.part('Launcher_rams', 'Steel', t)
    for s in (-1, 1):
        rams.limb((s * .5, -.1, .2), (s * .5, cy - .2, cz - .55), .05, .06, bevel=0)
    st = a.part('Kit_steel', 'Steel', t)
    for f in (.2, .5, .8):
        yy, zz = .5 - ca * L * f, .45 + sa * L * f
        st.box((W + .05, .05 * sa + .02, .05), loc=(0, yy - (D / 2 + .01) * sa * 0, zz), rot=(-ang, 0, 0), bevel=0)
    a.pivot('Muzzle_main', (0, fy - .1 * ca, fz + .1 * sa), t)
    a.pivot('Muzzle_gun', (0, fy - .09 * ca, fz + .09 * sa), t)
    a.part('Hazard_marks', 'Hazard', t).box((.02, 1.4, .1), loc=(W / 2 + .01, cy, cz - .2), rot=(-ang, 0, 0), bevel=0)


def c_ram(a, detail=False):
    """The C-RAM (Centurion): see the module docstring."""
    _site(a, seed=0)
    _phalanx(a)
    _mast(a, 4.35, 'lcmr')
    k.clean(a)


def c_ram_a(a, detail=False):
    """The Centurion branch: see the module docstring."""
    _site(a, seed=1, cases=4)
    _phalanx(a, eo=True)
    _mast(a, 4.65, 'ball')
    k.clean(a)


def c_ram_b(a, detail=False):
    """The Iron Dome branch: see the module docstring."""
    _site(a, seed=2)
    _iron_dome(a)
    _mast(a, 3.75, 'array')
    k.clean(a)


BUILDERS = {
    'c_ram': (c_ram, dict(ao_distance=.4, grime_height=.35)),
    'c_ram_a': (c_ram_a, dict(ao_distance=.4, grime_height=.35)),
    'c_ram_b': (c_ram_b, dict(ao_distance=.4, grime_height=.35)),
}
