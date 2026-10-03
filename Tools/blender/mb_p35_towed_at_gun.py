"""Prompt 35 wave 4 (lane C): the towed anti-tank gun rebuilt from scratch (spec: Tools/blender/specs/towed_at_gun.json).

A 2A45M Sprut-B 125 mm towed anti-tank gun in action (the def's modelSize 7.89 x 2.62 x 2.04 m): the long
smoothbore with its thermal sleeve bands and the multi-baffle muzzle brake, the cradle with the recoil and
recuperator cylinders and the equilibrator, the upper carriage (`Body`) with the bent armoured shield and its
sight window, the OP4M-type sight; the lower carriage with the two road wheels on their swing axle, the trails
spread behind (spades down) and the front leg; the auxiliary power unit on the right trail (the 2A45M drives
itself short distances) with its convoy lamps; ammunition boxes and a round laid out by the trail.

Runtime nodes kept: `Turret` (the upper carriage's traverse), `Main_cannon`, `Muzzle_brake`, `Muzzle_main`,
`Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .42
WHEEL_X = 1.05
PIVOT = (0, .25, 1.15)


def _carriage(a):
    """The lower carriage: the pivot block, the axle and wheels, the spread trails with spades, the front leg."""
    low = a.part('Carriage', 'Team')
    k.block(low, (.9, .9, .3), loc=(0, .25, .62), chamfer=.04)
    ax = a.part('Axles', 'Undercarriage')
    for s in (-1, 1):
        ax.limb((s * .35, .25, .7), (s * (WHEEL_X - .15), .3, WR), .07, .09, bevel=0)       # swing axle arm
        C.lugged_tyre(a, (s * WHEEL_X, .3, WR), WR, .26, s, lugs=11, seg=16, rim_mat='Team', nuts=5)
    ax.cyl(.06, WHEEL_X * 2 - .3, loc=(0, .28, .55), rot=(0, R90, 0), seg=8, bevel=0)
    # The trails: box beams from the pivot out and back, the spades at their ends, the lifting handles.
    tr = a.part('Trails', 'Team')
    sp = a.part('Spades', 'Armor')
    st = a.part('Kit_steel', 'Steel')
    for s in (-1, 1):
        p0, p1 = (s * .3, .55, .58), (s * .95, 2.95, .16)
        L = math.dist(p0, p1)
        yaw = math.atan2(p1[0] - p0[0], p1[1] - p0[1])
        pitch = math.atan2(p0[2] - p1[2], L)
        k.block(tr, (.18, L, .2), loc=((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2 - .1),
                rot=(pitch, 0, -yaw), chamfer=.02)
        k.extrude(sp, [(-.22, 0), (.22, 0), (.15, -.4), (0, -.5), (-.15, -.4)], .05, loc=(p1[0], p1[1] + .12, .2),
                  rot=(R90 - .3, 0, -yaw), axis='Z', chamfer=.008)
        K.handle(st, (p1[0] * .9, p1[1] - .5, .32), (p1[0] * .9, p1[1] - .2, .25), (0, 0, 1), h=.06, r=.015)
    leg = a.part('Front_leg', 'Team')
    k.block(leg, (.16, 1.2, .18), loc=(0, -.4, .3), rot=(-.35, 0, 0), chamfer=.02)
    k.lathe(a.part('Front_leg_pad', 'Armor'), [(.22, 0), (.22, .04), (.08, .1)], loc=(0, -.95, .0), seg=10)
    # The auxiliary power unit on the right trail with its convoy lamps and the small exhaust.
    apu = a.part('Apu', 'Armor')
    k.block(apu, (.5, .7, .4), loc=(-.7, 1.75, .38), rot=(0, 0, .3), chamfer=.04)
    K.grille(a, (-.93, 1.75, .6), .4, .2, facing=(-1, 0, 0), slats=3, frame_mat='Armor')
    K.exhaust(a, (-.55, 2.0, .78), r=.03, length=.18, direction=(0, 0, 1), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-.55, 2.0, .98))
    for x in (-.85, -.55):
        K.lamp(a, (x, 2.13, .6), (0, 1, 0), r=.04, guard=False, glow='LavaGlow')
    a.part('Tail_lamps', 'LavaGlow').box((.06, .02, .05), loc=(.9, 2.9, .45), bevel=0)
    # Ammunition: two crates by the left trail, a round laid on top.
    crates = a.part('Crates', 'Crate')
    bands = a.part('Kit_straps', 'Steel')
    for i, (x, y) in enumerate(((.3, 1.55), (.35, 2.2))):
        K.crate(crates, bands, (.4, .62, .22), (x, y, 0), rot=(0, 0, .3), bands=2)
    k.lathe(a.part('Ammo_round', 'Crate'), [(0, -.5), (.06, -.45), (.065, .3), (.04, .45), (0, .5)],
            loc=(.33, 1.9, .3), rot=(R90, 0, .3), seg=8, worn=(2,))
    K.dust(a, (0, 1.5, .1), radius=2.0, k=.3)


def _gun(a):
    t = a.pivot('Turret', PIVOT)
    # The upper carriage (cab role: the gun's body), its trunnion cheeks.
    body = a.part('Body', 'Team', t)
    k.block(body, (.8, .9, .35), loc=(0, .05, -.35), chamfer=.04)
    body.cyl(.3, .25, loc=(0, .05, -.5), seg=12, bevel=0)
    for s in (-1, 1):
        k.extrude(body, [(-.35, 0), (.3, 0), (.15, .45), (-.2, .45)], .1, loc=(s * .32, 0, .1), axis='X',
                  chamfer=.015)
    # The bent armoured shield with its sight window and the glass.
    sh = a.part('Shield', 'Armor', t)
    k.extrude(sh, [(-.95, 0), (.95, 0), (.9, .9), (.25, 1.0), (-.25, 1.0), (-.9, .9)], .035,
              loc=(0, -.45, -.3), rot=(R90 - .2, 0, 0), axis='Z', chamfer=.008, corner=.02)
    for s in (-1, 1):
        k.extrude(sh, [(-.25, 0), (.25, 0), (.22, .8), (-.22, .8)], .03, loc=(s * 1.12, -.3, -.3),
                  rot=(R90 - .2, 0, s * .7), axis='Z', chamfer=.006)
    a.part('Glass', 'Glass', t).box((.18, .02, .12), loc=(.4, -.47, .25), rot=(-.2, 0, 0), bevel=0)
    K.rivet_line(a.part('Kit_steel', 'Steel', t), (-.9, -.47, .33), (.9, -.47, .33), (0, -1, .2), pitch=.18, r=.014)
    K.lamp(a, (-.8, -.48, .1), (0, -1, 0), r=.04, parent=t, guard=False)
    # The sight on its bracket behind the shield, left of the breech.
    k.block(a.part('Sight', 'Armor', t), (.12, .35, .16), loc=(.4, -.1, .18), chamfer=.015)
    a.part('Glass', 'Glass', t).box((.08, .01, .06), loc=(.4, .08, .28), bevel=0)
    # The cradle with the recoil cylinders and the equilibrator, the breech.
    cr = a.part('Cradle', 'Steel', t)
    k.lathe(cr, [(.14, 0), (.14, 1.2), (.12, 1.25), (0, 1.25)], loc=(0, .55, .12), rot=K.FORWARD, seg=12, worn=(1,))
    for x in (-.17, .17):
        cr.cyl(.055, 1.1, loc=(x, -.05, .25), rot=K.FORWARD, seg=8, bevel=0)
    cr.limb((-.3, .3, -.1), (-.18, -.3, .15), .04, .04, bevel=0)
    k.block(a.part('Breech', 'Armor', t), (.3, .45, .3), loc=(0, .75, -.03), chamfer=.03)
    # The long 125 mm smoothbore with sleeve bands and the multi-baffle brake.
    C.gun_tube(a, 'Main_cannon', t, (0, -.7, .12), 3.85, .072, seg=12, sleeve=4, brake='baffle',
               brake_name='Muzzle_brake')
    a.pivot('Muzzle_main', (0, -4.9, .12), t)
    a.part('Team_band', 'Team', t).box((1.6, .01, .1), loc=(0, -.44, .1), rot=(-.2, 0, 0), bevel=0)
    a.pivot('Point_fire', (0, .3, .6), t)


def towed_at_gun(a, detail=False):
    """The towed anti-tank gun: see the module docstring."""
    _carriage(a)
    _gun(a)
    k.clean(a)


BUILDERS = {
    'towed_at_gun': (towed_at_gun, dict(ao_distance=.45, grime_height=.4)),
}
