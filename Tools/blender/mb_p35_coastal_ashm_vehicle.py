"""Prompt 35 wave 10 (lane B): the coastal anti-ship missile launcher rebuilt from scratch (spec:
Tools/blender/specs/coastal_ashm_vehicle.json).

An NSM Coastal Defence System launcher (the def's modelSize 7.18 x 2.7 x 2.97 m; nsm_coastal): a 6x6 tactical
truck (MAN SX / Scania class, drawn 0.8 x) with the forward-control cab (flat face with the grille and bumper, the
two-piece windscreen with wipers, side doors with windows and steps, the roof hatch, mirrors, lamps, a whip), the
ladder chassis with its fuel tank, battery box, exhaust stack and spare wheel, six wheels on three axles (the front
under the cab, the rear tandem) with fenders and mud flaps; on the bed the fire-control box behind the cab, the
launcher turntable (`Turret`) with its elevating frame and rams, the 2 x 2 pack of NSM canisters (Team) with their
end caps and lifting lugs, raised a little at rest (`Muzzle_main` at the front of the pack), four stabiliser jacks
on outriggers, a cable reel, stowage and Team bands.

Runtime nodes kept: `Turret` (0, 1.3, 1.22), `Muzzle_main` (0, -1.09, 2.54), `Point_fire`, `Point_exhaust`
(Part_wheel / Part_wheelb come from the prompt 34 wrapper). Built only from frontier_kit / mb_kit27 primitives,
mb_kit35 and lane B's helpers; no other model's builder. Metres, +Z up, -Y front, +X left. Under 7,500 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .5, .34, 1.0
AXLES = (-2.65, 1.25, 2.5)
FRAME_Z = .85
BED = 1.15


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(fr, (.12, 6.6, .26), loc=(s * .45, .05, FRAME_Z), c=.02)
    for y in (-2.0, -.5, 1.0, 2.6):
        fr.box((.9, .1, .1), loc=(0, y, FRAME_Z), bevel=0)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8, nuts=6, depth=.05)
            K.dust(a, (s * TRACK, y, .1), radius=.9, k=.3)
            P.leaf_pack(susp, s * .45, y, WR + .22, 1.0, leaves=3)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .6, r=.09, diff=True)
    for s in (-1, 1):
        fen = a.part('Fenders', 'Armor')
        k.block(fen, (.42, 1.25, .05), loc=(s * TRACK, AXLES[0] + .05, 1.12), chamfer=0)
        k.block(fen, (.42, 2.45, .05), loc=(s * TRACK, 1.88, 1.12), chamfer=0)
        P.mudflap(a, (s * TRACK, AXLES[0] + .62, 1.1), w=.4, h=.4)
        P.mudflap(a, (s * TRACK, 3.1, 1.1), w=.4, h=.4)
    P.fuel_tank(a, (-.75, -1.2, .7), 1.0, .25, parent=None)
    P.toolbox(a, (.78, -1.2, .7), (.28, .8, .4))
    k.block(a.part('Battery_box', 'Armor'), (.3, .5, .35), loc=(.78, -.3, .68), chamfer=.02)
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(.25, -.15), (.46, -.15), (.5, -.1), (.5, .1), (.46, .15), (.25, .15)],
            loc=(0, 3.3, .75), rot=(R90, 0, 0), seg=12, caps=(False, False))
    a.pivot('Point_fire', (0, 1.0, 1.4))


def _cab(a):
    """The forward-control cab (front at y -3.55)."""
    y0, y1, w, zb, zt = -3.55, -1.85, 1.22, 1.0, 2.6
    cab = a.part('Cab', 'Team')
    rings = []
    for y, top, half in ((y0, zt - .15, w - .06), (y0 + .25, zt, w), (y1, zt, w)):
        rings.append([(-half, y, zb), (half, y, zb), (half, y, top - .2), (half - .12, y, top), (-half + .12, y, top),
                      (-half, y, top - .2)])
    k.sharp_loft(cab, rings, chamfer=.04)
    K.windscreen(a, [(-1.1, y0 + .1, 1.85), (1.1, y0 + .1, 1.85), (1.05, y0 + .2, 2.45), (-1.05, y0 + .2, 2.45)],
                 frame_mat='Armor', wipers=2)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.02, .7, .5), loc=(s * (w + .005), -2.95, 2.1), bevel=0)
        a.part('Door_seams', 'Undercarriage').box((.015, .02, 1.1), loc=(s * (w + .008), -2.45, 1.6), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * (w + .02), -2.6, 1.75), (s * (w + .02), -2.4, 1.75), (s, 0, 0),
                 h=.04)
        P.step(a, (s * (w - .1), -2.95, .75), w=.4, d=.22)
        K.mirror(a.part('Cab_fit', 'Steel'), (s * (w + .05), y0 + .3, 2.2), s, arm=.06, size=(.05, .14, .3))
        K.lamp(a, (s * .85, y0 - .05, 1.2), (0, -1, 0), r=.09, mat='Armor', guard=True)
        a.part('Lamps', 'Alloy').box((.12, .02, .06), loc=(s * 1.05, y0 - .02, 1.38), bevel=0)
    K.grille(a, (0, y0 - .02, 1.45), 1.1, .45, facing=(0, -1, 0), slats=6, frame_mat='Armor')
    k.block(a.part('Bumper', 'Armor'), (2.4, .2, .25), loc=(0, y0 - .1, .95), chamfer=.03)
    a.part('Hazard_marks', 'Hazard').box((2.3, .02, .06), loc=(0, y0 - .21, .95), bevel=0)
    k.lathe(a.part('Hatches', 'Armor'), [(.3, 0), (.3, .05), (0, .07)], loc=(.4, -2.6, zt), seg=10)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, -2.0, zt), h=.35, r=.02, lean=.1)
    a.part('Team_band', 'Team').box((2.46, .02, .14), loc=(0, y1 + .01, 2.2), bevel=0)
    # The exhaust stack behind the cab on the right, its guard.
    K.exhaust(a, (-1.05, -1.75, 1.2), r=.06, length=1.6, direction=(0, 0, 1), muffler=True, cap=True)
    a.pivot('Point_exhaust', (-1.05, -1.75, 2.9))
    K.soot(a, (-1.05, -1.75, 2.9), radius=.4, k=.4)


def _bed(a):
    k.block(a.part('Bed', 'Armor'), (2.4, 5.0, .12), loc=(0, .95, BED), chamfer=.02)
    for s in (-1, 1):
        a.part('Bed_rails', 'Undercarriage').box((.06, 5.0, .12), loc=(s * 1.18, .95, BED + .1), bevel=0)
        a.part('Team_band', 'Team').box((.012, 4.6, .12), loc=(s * 1.215, .95, BED - .02), bevel=0)
    # Fire-control box behind the cab with its louvre and a door.
    k.block(a.part('Equipment_box', 'Armor'), (2.2, .8, 1.1), loc=(0, -1.3, BED + .06 + .55), chamfer=.04)
    K.grille(a, (.6, -1.71, BED + .7), .6, .4, facing=(0, -1, 0), slats=4)
    a.part('Doors', 'Armor').box((.6, .02, .8), loc=(-.5, -.89, BED + .55), bevel=0)
    # Stabiliser jacks on outriggers at the bed's corners.
    for y in (-.6, 3.0):
        for s in (-1, 1):
            K.outrigger(a.part('Outriggers', 'Steel'), a.part('Jack_pads', 'Steel'), (s * 1.15, y, BED - .05), s,
                        reach=.08, drop=BED - .2, w=.16)
    # Cable reel, stowage.
    k.lathe(a.part('Cable_reel', 'Steel'), [(.32, -.18), (.32, -.15), (.18, -.15), (.18, .15), (.32, .15), (.32, .18)],
            loc=(.8, 3.05, BED + .45), rot=(0, R90, 0), seg=12)
    a.part('Kit_cables', 'Rubber').torus(.24, .05, loc=(.8, 3.05, BED + .45), rot=(0, R90, 0), seg=12, ring=4)
    K.jerrycan(a.part('Jerrycans', 'Armor'), (-.85, 3.1, BED + .06))
    K.jerrycan(a.part('Jerrycans', 'Armor'), (-.55, 3.1, BED + .06))


def _launcher(a):
    t = a.pivot('Turret', (0, 1.3, 1.22))
    k.lathe(a.part('Turntable', 'Steel', t), [(.75, 0), (.75, .1), (.6, .16), (0, .16)], seg=14, worn=(1,))
    fr = a.part('Launcher_frame', 'Armor', t)
    e = math.atan2(1.32 - .62, 2.39 + 1.1)
    bore = P.Elev((0, 1.1, .62), e)
    L = math.hypot(2.39 + 1.1, 1.32 - .62)
    for s in (-1, 1):
        fr.limb((s * .55, 1.2, .16), (s * .55, 1.1, .62), .1, .14, bevel=0)
        a.part('Rams', 'Steel', t).tube([(s * .35, -.3, .16), bore.at(1.3, dx=s * .35, up=-.5)], .05, seg=6)
    k.block(a.part('Cradle', 'Armor', t), (1.2, 2.6, .12), loc=bore.at(L * .55, up=-.55), rot=bore.box_rot,
            chamfer=.02)
    # The 2 x 2 canister pack: four square canisters with end caps, frames, lugs.
    pitch = .5
    for i in range(2):
        for j in range(2):
            dx, up = (i - .5) * pitch, (j - .5) * pitch
            k.block(a.part('Launcher', 'Team', t), (.46, L, .46), loc=bore.at(L / 2, dx=dx, up=up), rot=bore.box_rot,
                    chamfer=.03)
            for f, mat in ((L - .02, 'Undercarriage'), (.02, 'Armor')):
                a.part('Canister_caps', mat, t).box((.4, .04, .4), loc=bore.at(f, dx=dx, up=up), rot=bore.box_rot,
                                                    bevel=0)
    bands = a.part('Canister_frames', 'Steel', t)
    for f in (.35, L * .5, L - .35):
        bands.box((1.04, .08, 1.04), loc=bore.at(f), rot=bore.box_rot, bevel=0)
    for f in (.8, L - .8):
        for s in (-1, 1):
            a.part('Kit_lugs', 'Steel', t).box((.08, .08, .1), loc=bore.at(f, dx=s * .3, up=.55), rot=bore.box_rot,
                                               bevel=0)
    a.part('Hazard_marks', 'Hazard', t).box((1.0, .02, .08), loc=bore.at(L + .01, up=.45), rot=bore.box_rot, bevel=0)
    a.pivot('Muzzle_main', (0, -2.39, 1.32), t)


def coastal_ashm_vehicle(a):
    _chassis(a)
    _cab(a)
    _bed(a)
    _launcher(a)
    k.clean(a)


BUILDERS = {'coastal_ashm_vehicle': (coastal_ashm_vehicle, dict(ao_distance=.5, grime_height=.6))}
