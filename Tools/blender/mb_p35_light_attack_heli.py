"""Prompt 35 wave 11 (lane C): the light attack helicopter rebuilt from scratch (spec: Tools/blender/specs/light_attack_heli.json).

A Bell OH-58D Kiowa Warrior / ARH-70 pattern armed light helicopter (the def's modelSize 3.88 x 3.16 x 1.56 m, about
0.4 x the real one like every aircraft; a different airframe from scout_heli's Little Bird): the angular Bell 206
style cabin with the stepped, framed windscreen and the chin windows, the doors with their windows, the engine
fairing and its intake grilles behind the mast, the exhaust stack, the round mast-mounted sight ball over the
four-bladed main rotor (`Rotor`), the tapering tail boom with its horizontal stabiliser and end plates, the swept
fin and the ventral fin with the tail skid, the two-bladed tail rotor on the right (`Tail_rotor`); high skids on
cross tubes; the weapon stub wings with anhedral, an M134 minigun pod under each tip (`Mount_gun` pivots, the def's
main minigun) and a pair of 9M120 Ataka tubes on each inner station (the def's heli_atgm); flare dispensers on the
boom, a wire cutter, aerials, lights and team bands.

Runtime nodes kept where they were: `Rotor` (0, -.1, 1.3), `Tail_rotor` (-.13, 1.82, .98), `Muzzle_gun` /
`Muzzle_gun.001` (now under their `Mount_gun` pivots), `Muzzle_rocket` / `.001` (plain pivots on the inner stations:
the def has no rockets), `Point_exhaust`, `Point_fire`; new `Mount_gun` / `.001`, `Muzzle_missile` / `.001`; the
wrapper adds `Mount_Flare_*` at the `Flares`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
ROTOR = (0, -.1, 1.3)


def _half(w, h, zc, top=.7, bot=.85):
    """A boxy cabin half outline (x, z): flat sides with rounded upper and lower shoulders."""
    return [(0, zc - h), (w * bot * .6, zc - h), (w * bot, zc - h * .9), (w, zc - h * .55), (w, zc + h * .35),
            (w * (1 + top) / 2, zc + h * .8), (w * top, zc + h), (0, zc + h)]


def _cabin(a):
    body = a.part('Fuselage', 'Team')
    C.section_loft(body, [
        (-1.5, _half(.08, .1, .68)),
        (-1.42, _half(.2, .2, .7)),
        (-1.25, _half(.32, .3, .72)),
        (-1.0, _half(.38, .34, .75)),
        (-.6, _half(.41, .37, .78)),
        (-.15, _half(.41, .38, .8)),
        (.2, _half(.38, .36, .84, top=.75)),
        (.45, _half(.27, .27, .9, top=.8)),
        (.62, _half(.15, .17, .95, top=.85)),
    ])
    # Stepped, framed windscreen and chin windows over the nose.
    glass = a.part('Canopy', 'Glass')
    for s in (-1, 1):
        glass.mesh([(s * .03, -1.42, .82), (s * .3, -1.26, .86), (s * .3, -.95, 1.08), (s * .03, -1.0, 1.12)],
                   [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        glass.mesh([(s * .05, -1.45, .55), (s * .27, -1.3, .5), (s * .32, -1.22, .7), (s * .1, -1.4, .7)],
                   [(0, 1, 2, 3) if s < 0 else (3, 2, 1, 0)])
        # Side door windows.
        a.part('Glass', 'Glass').box((.01, .5, .3), loc=(s * .412, -.55, .92), bevel=0)
        a.part('Glass', 'Glass').box((.01, .3, .26), loc=(s * .412, -.05, .92), bevel=0)
        dr = a.part('Door_frames', 'Team')
        for y in (-.85, -.25, .12):
            dr.box((.015, .02, .62), loc=(s * .414, y, .78), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * .42, -.35, .8), (s * .42, -.28, .8), (s, 0, 0), h=.02, r=.008)
        a.part('Team_band', 'Team').box((.01, .35, .08), loc=(s * .412, .3, .7), bevel=0)
    fr = a.part('Canopy_frames', 'Team')
    fr.tube([(0, -1.47, .7), (0, -1.0, 1.13), (0, -.75, 1.15)], .018, seg=4)
    for s in (-1, 1):
        fr.tube([(s * .31, -1.27, .7), (s * .31, -.96, 1.09)], .016, seg=4)
    # Engine fairing behind the mast, its intakes and the exhaust stack.
    cowl = a.part('Engine_cowl', 'Team')
    C.section_loft(cowl, [(-.45, [(0, 1.1), (.18, 1.1), (.15, 1.2), (0, 1.22)]),
                          (-.2, [(0, 1.1), (.24, 1.1), (.2, 1.28), (0, 1.31)]),
                          (.35, [(0, 1.1), (.22, 1.1), (.18, 1.25), (0, 1.28)]),
                          (.6, [(0, 1.0), (.12, 1.0), (.1, 1.08), (0, 1.1)])])
    for s in (-1, 1):
        K.grille(a, (s * .22, -.1, 1.2), .2, .1, facing=(s, 0, .3), slats=3, frame_mat='Team')
    k.lathe(a.part('Exhausts', 'Steel'), [(.06, 0), (.065, .14), (.055, .2)], loc=(.15, .5, 1.12),
            rot=(-.5, 0, 0), seg=8, worn=(1,))
    a.pivot('Point_exhaust', (.3, .6, .9))
    K.soot(a, (.15, .6, 1.25), radius=.3, k=.4)
    a.pivot('Point_fire', (0, -.1, .85))
    # Crew in the cockpit (two helmeted heads), panel rivets, door hinges, the pitot and the belly aerial.
    crew = a.part('Crew', 'Suit')
    for x in (-.17, .17):
        crew.sphere(.08, loc=(x, -.85, .98), seg=8, rings=5)
        crew.box((.2, .14, .2), loc=(x, -.8, .82), bevel=0)
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        K.rivet_line(rv, (s * .412, -.95, .6), (s * .412, .2, .6), (s, 0, 0), pitch=.12, r=.009, h=.008, seg=4)
        K.rivet_line(rv, (s * .07, .65, 1.02), (s * .045, 1.9, .99), (s, 0, .4), pitch=.14, r=.008, h=.008, seg=4)
        K.hinge(a.part('Kit_hinges', 'Steel'), (s * .418, -.84, .65), (s * .418, -.84, .95), r=.01, knuckles=2)
    a.part('Pitot', 'Steel').tube([(.1, -1.42, .82), (.1, -1.62, .82)], .01, seg=4)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -.3, .42), h=.07, chord=.07, normal=(0, 0, -1))


def _tail(a):
    boom = a.part('Tail_boom', 'Team')
    k.lathe(boom, [(.12, 0), (.085, .5), (.06, 1.1), (.045, 1.45)], loc=(0, .55, .95), rot=K.BACKWARD, seg=10)
    stab = a.part('Tailplane', 'Team')
    K.wing(stab, (1.32, .18), (1.36, .14), .34, x0=0, z=.96, t=.1)
    for s in (-1, 1):
        stab.box((.02, .16, .14), loc=(s * .35, 1.42, .97), bevel=0)
    fin = a.part('Tail', 'Team')
    K.fin(fin, (1.75, .34), (1.98, .18), .45, x=0, z0=.98, t=.12)
    K.fin(fin, (1.8, .22), (1.92, .14), -.25, x=0, z0=.94, t=.12)
    a.part('Tail_skid', 'Steel').tube([(0, 1.85, .7), (0, 1.98, .66), (0, 2.02, .7)], .012, seg=4)
    for s in (-1, 1):
        K.flare_dispenser(a, (s * .07, 1.05, .93), normal=(s, 0, -.3), cols=2, rows=2, cell=.05)
    a.part('Wing_lights', 'Lamp').box((.03, .03, .03), loc=(0, 2.0, 1.4), bevel=0)


def _rotors(a):
    r = a.pivot('Rotor', ROTOR)
    K.rotor_head(a, r, 4, 1.56, .12, hub=.1, cap=.1, stripe=.18)
    # The mast-mounted sight ball over the hub (rides on the mast, so it is drawn under the rotor pivot's fixed
    # mast: on its own short tube, it does not spin with the blades).
    k.lathe(a.part('Mast_sight', 'Armor'), [(0, 1.44), (.07, 1.45), (.1, 1.5), (.1, 1.58), (.07, 1.62), (0, 1.63)],
            loc=(0, -.1, 0), seg=12, worn=(2, 3))
    a.part('Sight_glass', 'Glass').box((.13, .02, .05), loc=(0, -.2, 1.54), bevel=0)
    a.part('Rotor_mast', 'Steel').cyl(.035, .16, loc=(0, -.1, 1.38), seg=8, bevel=0)
    tr = a.pivot('Tail_rotor', (-.13, 1.82, .98))
    K.tail_rotor(a, tr, 2, .28, .055, side=-1)


def _wings_and_weapons(a):
    sk = a.part('Skids', 'Steel')
    K.skids(sk, .45, -.85, .4, 0.0, h=.42, r=.02)
    for s in (-1, 1):
        sk.box((.12, .2, .015), loc=(s * .45, -.45, .2), bevel=0)
        sk.tube([(s * .45, -.52, .2), (s * .45, -.52, .03)], .01, seg=4)
    a.part('Wire_cutter', 'Steel').limb((0, -1.45, .5), (0, -1.6, .3), .03, .02, bevel=0)
    wing = a.part('Wings', 'Armor')
    K.stub_wing(wing, .38, .95, -.65, .3, .55, t=.1, anhedral=.12)
    for s in (-1, 1):
        a.part('Wing_struts', 'Steel').limb((s * .4, -.5, .45), (s * .95, -.5, .5), .03, .03, bevel=0)
    # Minigun pods under the tips on their Mount_gun pivots.
    for s, idx in ((-1, ''), (1, '__001')):
        x = s * 1.3
        m = a.pivot('Mount_gun' + idx, (x, -.4, .36))
        k.lathe(a.part('Gun_pods', 'Armor', m), [(.0, -.25), (.06, -.22), (.075, -.1), (.075, .25), (.05, .32),
                                                  (0, .33)], rot=K.BACKWARD, seg=10, worn=(2,))
        mg = a.part('Miniguns', 'Steel', m)
        for i in range(6):
            u = i * math.tau / 6
            mg.cyl(.011, .2, loc=(math.cos(u) * .028, -.33, math.sin(u) * .028), rot=K.FORWARD, seg=4, bevel=0)
        mg.cyl(.045, .03, loc=(0, -.4, 0), rot=K.FORWARD, seg=8, bevel=0)
        a.pivot('Muzzle_gun' + idx, (0, -.42, 0), m)
        a.part('Pylons', 'Armor').box((.05, .25, .14), loc=(x, -.5, .47), bevel=0)
        # Two Ataka tubes on the inner station, the old rocket pivot between them.
        xi = s * .62
        a.part('Pylons', 'Armor').box((.05, .22, .1), loc=(xi, -.55, .43), bevel=0)
        tubes = a.part('Missile_tubes', 'Plaster')
        for j, dx in enumerate((-.06, .06)):
            k.lathe(tubes, [(.045, 0), (.045, .62), (.04, .64)], loc=(xi + dx, .02, .3), rot=K.FORWARD, seg=8,
                    caps=(True, False))
        a.part('Missile_bands', 'Hazard').box((.24, .04, .1), loc=(xi, -.1, .3), bevel=0)
        a.pivot('Muzzle_missile' + idx, (xi + .06 * s, -.63, .3))
        a.pivot('Muzzle_rocket' + idx, (xi, -.62, .26))
    K.whip_antenna(a.part('Antennas', 'Steel'), (0, .35, .45), h=.25, lean=-.3)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .25, 1.28), h=.08, chord=.08)
    a.part('Lamps', 'Lamp').cyl(.035, .02, loc=(0, -1.3, .42), rot=(.6, 0, 0), seg=8, bevel=0)


def light_attack_heli(a, detail=False):
    """The light attack helicopter: see the module docstring."""
    K.suffixed(a)
    _cabin(a)
    _tail(a)
    _rotors(a)
    _wings_and_weapons(a)
    k.clean(a)


BUILDERS = {
    'light_attack_heli': (light_attack_heli, dict(ao_distance=.3, grime_height=.2)),
}
