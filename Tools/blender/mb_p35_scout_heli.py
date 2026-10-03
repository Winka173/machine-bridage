"""Prompt 35 wave 4 (lane C): the scout helicopter rebuilt from scratch (spec: Tools/blender/specs/scout_heli.json).

An AH-6 / MH-6 Little Bird (the def's modelSize 3.88 x 3.16 x 1.56 m, 0.4 x the real one like every aircraft): the
egg-shaped cabin with the big glazed nose and the open doorways, the engine hump and the exhaust behind the rotor
mast, the five-bladed main rotor (`Rotor`, the sheet's five blades), the slim tail boom with the T-tail (the
horizontal stabiliser with its end plates, the upper and lower fins), the two-bladed tail rotor on the right
(`Tail_rotor`); the skids on their cross tubes; the weapons plank across the cabin floor (`Pylons`) carrying the two
M134 miniguns outboard and the two seven-tube Hydra pods inboard; flare dispensers on the boom, aerials, lights.

The guns are fixed on the plank: the whole helicopter aims (the def's turretTurnRate 360 is the body's), so the
main mount is merged into `Pylons` (spec "merged").
Runtime nodes kept: `Rotor`, `Rotor_blades`, `Rotor_grips`, `Rotor_hub`, `Rotor_tips`, `Tail_rotor` (+ blades, hub,
tips), `Muzzle_gun`, `Muzzle_gun.001`, `Muzzle_rocket`, `Muzzle_rocket.001`, `Pods`, `Point_exhaust`, `Point_fire`
(the wrapper adds `Mount_Flare_L / _R / _TL / _TR` at the `Flares`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_parts27 as p27

R90 = math.pi / 2
ROTOR = (0, -.05, 1.36)


def _cabin(a):
    body = a.part('Fuselage', 'Team')
    # The egg: sections from the nose to the cabin's rear, then the boom root.
    C.section_loft(body, [
        (-1.18, C.ellipse_half(.12, .14, .78, 8)),
        (-1.1, C.ellipse_half(.24, .25, .77, 8)),
        (-1.0, C.ellipse_half(.33, .34, .77, 8)),
        (-.85, C.ellipse_half(.4, .4, .78, 8)),
        (-.6, C.ellipse_half(.44, .44, .79, 8)),
        (-.3, C.ellipse_half(.46, .46, .8, 8)),
        (0.0, C.ellipse_half(.45, .45, .81, 8)),
        (.25, C.ellipse_half(.39, .41, .83, 8)),
        (.45, C.ellipse_half(.28, .32, .87, 8)),
        (.62, C.ellipse_half(.17, .2, .91, 8)),
        (.75, C.ellipse_half(.1, .12, .95, 8)),
    ])
    # The glazed nose: a bubble over the front half, the frame bows and the chin windows.
    glass = a.part('Canopy', 'Glass')
    C.section_loft(glass, [
        (-1.2, C.ellipse_half(.13, .15, .79, 8)),
        (-1.1, C.ellipse_half(.25, .26, .775, 8)),
        (-.98, C.ellipse_half(.345, .35, .775, 8)),
        (-.82, C.ellipse_half(.415, .415, .785, 8)),
        (-.62, C.ellipse_half(.455, .455, .795, 8)),
        (-.48, C.ellipse_half(.47, .47, .8, 8)),
    ])
    fr = a.part('Canopy_frames', 'Team')
    for y, w, h, zc in ((-1.07, .32, .32, .77), (-.8, .45, .45, .79)):
        pts = [(x * 1.02, y, z) for x, z in C.ellipse_half(w, h, zc, 6)][2:]
        fr.tube(pts + [(-x, yy, z) for x, yy, z in reversed(pts[:-1])], .016, seg=4)
    fr.tube([(0, -1.2, .92), (0, -.9, 1.22), (0, -.48, 1.28)], .018, seg=4)
    # The open doorways (dark), the bench seats on the sills, the floor.
    dark = a.part('Doorways', 'Undercarriage')
    for s in (-1, 1):
        dark.box((.02, .45, .42), loc=(s * .455, -.25, .8), bevel=0)
        a.part('Seats', 'Canvas').box((.14, .5, .05), loc=(s * .52, -.2, .5), bevel=0)
        a.part('Team_band', 'Team').box((.01, .3, .07), loc=(s * .44, .25, .7), bevel=0)
    # The engine hump and the exhaust behind the mast, the mast fairing.
    hump = a.part('Engine_cowl', 'Team')
    C.section_loft(hump, [(-.4, C.ellipse_half(.16, .08, 1.22, 4)), (.0, C.ellipse_half(.24, .14, 1.24, 4)),
                          (.45, C.ellipse_half(.14, .1, 1.18, 4))])
    k.lathe(a.part('Exhausts', 'Steel'), [(.07, 0), (.08, .12), (.06, .2)], loc=(0, .5, 1.17), rot=(-R90 - .4, 0, 0),
            seg=8, worn=(1,))
    K.soot(a, (0, .65, 1.2), radius=.3, k=.4)
    a.pivot('Point_exhaust', (0, .65, 1.22))
    a.part('Rotor_mast', 'Steel').cyl(.06, .14, loc=(ROTOR[0], ROTOR[1], 1.3), seg=8, bevel=0)
    K.grille(a, (.2, -.1, 1.26), .16, .12, facing=(1, 0, .5), slats=3, frame_mat='Team')
    K.grille(a, (-.2, -.1, 1.26), .16, .12, facing=(-1, 0, .5), slats=3, frame_mat='Team')
    a.pivot('Point_fire', (0, .1, 1.0))


def _boom(a):
    boom = a.part('Tail_boom', 'Team')
    k.lathe(boom, [(.1, 0), (.075, .6), (.055, 1.4), (.045, 1.75)], loc=(0, .55, .95), rot=K.BACKWARD, seg=10)
    # The T-tail: the horizontal stabiliser with its end plates, the upper and lower fins.
    tail = a.part('Tail', 'Team')
    K.fin(tail, (2.05, .32), (2.2, .2), .38, x=0, z0=.98, t=.12)
    K.fin(tail, (2.1, .25), (2.2, .18), -.2, x=0, z0=.95, t=.12)
    tail.box((.05, .02, .02), loc=(0, 2.3, .74), bevel=0)
    stab = a.part('Tailplane', 'Team')
    K.wing(stab, (2.12, .22), (2.17, .17), .32, x0=0, z=1.33, t=.1)
    for s in (-1, 1):
        stab.box((.02, .2, .16), loc=(s * .33, 2.22, 1.33), bevel=0)
    # Flare dispensers on the boom's sides, the tail light, the strobe.
    for s in (-1, 1):
        K.flare_dispenser(a, (s * .085, 1.35, .95), normal=(s, 0, -.3), cols=2, rows=2, cell=.05)
    a.part('Wing_lights', 'Lamp').box((.03, .03, .03), loc=(0, 2.3, 1.38), bevel=0)


def _rotors(a):
    r = a.pivot('Rotor', ROTOR)
    K.rotor_head(a, r, 5, 1.66, .13, hub=.1, cap=.12, stripe=.18)
    tr = a.pivot('Tail_rotor', (-.07, 2.36, .95))
    K.tail_rotor(a, tr, 2, .3, .06, side=-1)


def _gear_and_weapons(a):
    sk = a.part('Skids', 'Steel')
    K.skids(sk, .5, -.75, .45, 0.0, h=.36, r=.022)
    # The weapons plank across the cabin floor, its drop links to the stores.
    pl = a.part('Pylons', 'Armor')
    k.block(pl, (2.0, .2, .06), loc=(0, -.3, .42), chamfer=.01)
    for x in (-.85, -.6, .6, .85):
        pl.box((.05, .12, .1), loc=(x, -.3, .37), bevel=0)
    # Two miniguns outboard (six barrels each, the feed chute, the motor) and two seven-tube pods inboard.
    for s, mname in ((1, 'Muzzle_gun.001'), (-1, 'Muzzle_gun')):
        x = s * .85
        k.block(a.part('Gun_housings', 'Undercarriage'), (.1, .3, .1), loc=(x, -.3, .26), chamfer=.01)
        mg = a.part('Miniguns', 'Steel')
        for i in range(6):
            u = i * math.tau / 6
            mg.cyl(.012, .55, loc=(x + math.cos(u) * .03, -.7, .31 + math.sin(u) * .03), rot=K.FORWARD, seg=4, bevel=0)
        mg.cyl(.05, .04, loc=(x, -.92, .31), rot=K.FORWARD, seg=8, bevel=0)
        a.part('Gun_feeds', 'Undercarriage').tube([(x, -.2, .3), (x * .8, -.1, .4), (x * .55, -.1, .5)], .02, seg=4)
        a.pivot(mname.replace('.001', '__001'), (x, -.99, .31))
    for s, pname in ((1, 'Muzzle_rocket.001'), (-1, 'Muzzle_rocket')):
        x = s * .6
        p27.rocket_pod(a, x, -.55, .3, .085, .62, s, seg=10)
        a.pivot(pname.replace('.001', '__001'), (x, -.57, .3))
    # Aerials, the landing light, the step.
    K.whip_antenna(a.part('Antennas', 'Steel'), (0, .4, .52), h=.25, lean=-.3)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .2, 1.24), h=.08, chord=.08)
    a.part('Lamps', 'Lamp').cyl(.04, .02, loc=(0, -1.0, .4), rot=(.6, 0, 0), seg=8, bevel=0)


def scout_heli(a, detail=False):
    """The scout helicopter: see the module docstring."""
    K.suffixed(a)
    _cabin(a)
    _boom(a)
    _rotors(a)
    _gear_and_weapons(a)
    k.clean(a)


BUILDERS = {
    'scout_heli': (scout_heli, dict(ao_distance=.3, grime_height=.2)),
}
