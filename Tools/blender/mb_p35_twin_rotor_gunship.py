"""Prompt 35 wave 10 (lane B): the twin-rotor gunship rebuilt from scratch (spec:
Tools/blender/specs/twin_rotor_gunship.json).

An ACH-47A "Guns-A-Go-Go" (a CH-47 Chinook armed as a gunship; the def's modelSize 11.93 x 5.7 x 4.82 m; heli_gun in
a chin turret, agl_40 grenade launchers aimed freely): the long box fuselage with its rounded flanks and flat belly,
the stepped cockpit with the framed windscreen, eyebrow and chin windows, the forward pylon with the three-blade
`Rotor`, the tall aft pylon with the three-blade `Rotor_rear` (its tail-rotor role: the tandem's rear rotor
balances the front one) between the two engine pods with intakes and exhausts, the side fuel sponsons with the
four fixed landing-gear legs, the rear ramp; the weapons: the chin turret (`Turret`) with the 40 mm / minigun
(`Muzzle_main`, `Muzzle_gun`), the two side pylons carrying the 40 mm grenade launcher pods (`Mount_mg`,
`Mount_mg.001`), door guns in the windows, armour plates round the cockpit, flare dispensers, round windows, rescue
hoist, antennas, beacons, Team bands.

Runtime nodes kept: `Rotor` (0, -2.75, 3.5), `Rotor_rear` (0, 2.85, 4.4) with their hubs, grips, blades and tips,
`Muzzle_main` / `Muzzle_gun` (0, -5.85, 0.7), `Muzzle_mg` / `.001` (±2.1, -1.5, 1.5), `Point_fire`, `Point_exhaust`;
new: `Turret` (the def's turning main weapon), `Mount_mg` / `Mount_mg.001` (the free secondary). Built only from
frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder. Metres, +Z up, -Y
front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
FRONT_R = (0, -2.75, 3.5)
REAR_R = (0, 2.85, 4.4)
HW = .9


def _fuselage(a):
    body = a.part('Fuselage', 'Team')

    def box_half(w, zb, zt, r=.25):
        return [(0, zb), (w - r, zb), (w, zb + r), (w, zt - r), (w - r * .6, zt), (0, zt)]
    stations = [(-5.45, box_half(.25, .75, 1.2, .1)), (-5.25, box_half(.55, .6, 1.6, .2)),
                (-4.8, box_half(.8, .55, 2.15, .25)), (-4.2, box_half(HW, .55, 2.35, .25)),
                (3.6, box_half(HW, .55, 2.35, .25)), (4.3, box_half(.8, 1.1, 2.35, .25))]
    K.section_loft(body, stations)
    g = a.part('Glass', 'Glass')
    g.mesh([(-.5, -5.15, 1.6), (.5, -5.15, 1.6), (.62, -4.82, 2.12), (-.62, -4.82, 2.12)], [(0, 1, 2, 3)])
    for s in (-1, 1):
        g.mesh([(s * .58, -5.05, 1.3), (s * .82, -4.6, 1.3), (s * .82, -4.6, 2.0), (s * .62, -4.85, 2.05)],
               [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        g.box((.25, .3, .02), loc=(s * .3, -5.25, .78), rot=(.7, 0, 0), bevel=0)
    fr = a.part('Canopy_frames', 'Armor')
    fr.box((.04, .45, .04), loc=(0, -4.98, 1.86), rot=(-1.0, 0, 0), bevel=0)
    fr.box((1.25, .04, .04), loc=(0, -4.82, 2.13), bevel=0)
    # Armour plates round the cockpit, round windows, doors, panel seams, Team bands.
    for s in (-1, 1):
        k.block(a.part('Armor', 'Armor'), (.04, .9, .5), loc=(s * (HW + .02), -4.05, 1.0), chamfer=.01)
        P.portholes(a, [(s * (HW + .005), y, 1.75) for y in (-3.2, -2.0, -.8, .4, 1.6, 2.8)], (s, 0, 0), r=.13, seg=8)
        a.part('Team_band', 'Team').box((.012, 7.4, .12), loc=(s * (HW + .006), -.4, 1.25), bevel=0)
        seams = a.part('Panel_seams', 'Undercarriage')
        for y in (-3.6, -2.6, -1.4, -.2, 1.0, 2.2, 3.3):
            seams.box((.012, .02, 1.6), loc=(s * (HW + .006), y, 1.45), bevel=0)
    a.part('Doors', 'Armor').box((.02, .7, 1.2), loc=(-HW - .006, -3.5, 1.2), bevel=0)
    a.part('Hatches', 'Armor').box((1.4, .05, 1.0), loc=(0, 4.28, 1.6), rot=(-.5, 0, 0), bevel=0)
    a.pivot('Point_fire', (0, -3.0, 1.5))


def _pylons(a):
    """The forward pylon over the cockpit, the tall aft pylon with the engine pods."""
    fp = a.part('Fuselage_pylon', 'Team')
    k.extrude(fp, [(-.5, 0), (.5, 0), (.35, .95), (-.35, .95)], 2.4, loc=(0, -3.0, 2.3), axis='Y', chamfer=.06)
    # The aft pylon: a swept fairing rising from the roof to the rear head, narrowing to its top.
    aft = a.part('Fuselage_pylon_aft', 'Team')

    def half(w, zt):
        return [(0, 2.3), (w, 2.3), (w, 2.5), (w * .8, zt - .25), (w * .45, zt), (0, zt)]
    K.section_loft(aft, [(1.0, half(.45, 2.42)), (1.7, half(.58, 3.3)), (2.3, half(.55, 4.2)),
                         (3.5, half(.5, 4.25)), (4.2, half(.4, 3.4)), (4.35, half(.3, 2.9))])
    a.part('Rotor_mast', 'Steel').cyl(.1, .3, loc=(0, -2.75, 3.3), seg=8, bevel=0)
    a.part('Rotor_mast', 'Steel').cyl(.1, .2, loc=(0, 2.85, 4.25), seg=8, bevel=0)
    for s in (-1, 1):
        x = s * 1.08
        k.lathe(a.part('Engines', 'Armor'), [(0, 0), (.24, .1), (.27, .5), (.27, 1.9), (.2, 2.3), (.16, 2.4)],
                loc=(x, 1.6, 2.75), rot=K.BACKWARD, seg=10, worn=(2,))
        k.lathe(a.part('Intakes', 'Undercarriage'), [(.14, 0), (.2, .03), (.2, .1)], loc=(x, 1.62, 2.75),
                rot=K.FORWARD, seg=10, caps=(False, False))
        a.part('Intake_screens', 'Steel').cyl(.17, .02, loc=(x, 1.65, 2.75), rot=(R90, 0, 0), seg=10, bevel=0)
        k.lathe(a.part('Exhaust', 'Charred'), [(.13, 0), (.13, .2), (.11, .2)], loc=(x, 4.0, 2.75),
                rot=K.BACKWARD, seg=10, caps=(True, False))
        K.soot(a, (x, 4.2, 2.75), radius=.5, k=.4)
        a.part('Engine_struts', 'Steel').limb((s * .55, 2.4, 2.6), (x, 2.4, 2.7), .08, .1, bevel=0)
        for y in (2.2, 2.8, 3.4):
            a.part('Engine_seams', 'Undercarriage').torus(.272, .012, loc=(x, y, 2.75), rot=(R90, 0, 0), seg=10,
                                                          ring=3)
    a.pivot('Point_exhaust', (.78, 4.5, 2.75))
    # Walkway grip strips and the hydraulic access panels on the roof.
    for y in (-1.5, -.5, .5):
        a.part('Roof_panels', 'Armor').box((.8, .6, .03), loc=(0, y, 2.36), bevel=0)


def _gear_and_sponsons(a):
    for s in (-1, 1):
        k.extrude(a.part('Sponsons', 'Team'), [(0, 0), (.35, 0), (.3, .45), (0, .55)], 4.0,
                  loc=(s * HW, -.4, .55), rot=(0, 0, 0 if s > 0 else math.pi), axis='Y', chamfer=.03)
        K.landing_gear(a, (s * 1.05, -3.6, .6), wheel_r=.22, leg=.38, width=.12, twin=True)
        K.landing_gear(a, (s * 1.05, 2.3, .6), wheel_r=.22, leg=.38, width=.12)


def _weapons(a):
    # The chin turret with the gun (Turret), its sight ball.
    t = a.pivot('Turret', (0, -5.25, .75))
    k.lathe(a.part('Gun_turret', 'Armor', t), [(.2, .1), (.24, 0), (.22, -.15), (.12, -.22), (0, -.23)], seg=10)
    k.block(a.part('Gun_turret', 'Armor', t), (.2, .3, .16), loc=(0, -.15, -.05), chamfer=.02)
    for dx in (-.04, .04):
        a.part('Guns', 'Steel', t).cyl(.025, .45, loc=(dx, -.4, -.05), rot=(R90, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_main', (0, -.6, -.05), t)
    a.pivot('Muzzle_gun', (0, -.6, -.05), t)
    a.part('Sensor_ball', 'Glass').sphere(.1, loc=(.35, -5.1, .62), seg=8, rings=5)
    # The two side pylons with the 40 mm grenade launcher pods (Mount_mg, Mount_mg.001).
    for i, s in enumerate((1, -1)):
        k.extrude(a.part('Pylons', 'Armor'), [(-.3, -.04), (.3, -.04), (.25, .04), (-.25, .04)], 1.2,
                  loc=(s * (HW + .6), -1.0, 1.55), axis='X', chamfer=.01)
        a.part('Pylons', 'Armor').limb((s * (HW + .1), -1.0, 1.0), (s * (HW + .9), -1.0, 1.5), .06, .08, bevel=0)
        m = a.pivot(K.name('Mount_mg', i), (s * 2.1, -.9, 1.5))
        k.lathe(a.part('Pods', 'Armor', m), [(0, -.55), (.1, -.5), (.12, -.2), (.12, .4), (.08, .5), (0, .52)],
                rot=K.FORWARD, seg=10, worn=(2,))
        a.part('Guns', 'Steel', m).cyl(.035, .25, loc=(0, -.62, 0), rot=(R90, 0, 0), seg=6, bevel=0)
        a.pivot(K.name('Muzzle_mg', i), (0, -.6, 0), m)
        # Door guns in the forward windows.
        a.part('Door_guns', 'Steel').cyl(.02, .7, loc=(s * (HW + .3), -2.6, 1.6), rot=(R90, 0, 0), seg=5, bevel=0)
        a.part('Door_guns', 'Undercarriage').box((.08, .3, .12), loc=(s * (HW + .1), -2.25, 1.6), bevel=0)
    # Flare dispensers, beacons, nav lights, antennas, the rescue hoist.
    for s in (-1, 1):
        K.flare_dispenser(a, (s * (HW + .01), 2.9, 1.0), normal=(s, 0, -.3), cols=3, rows=2)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .1, .05), loc=(s * 1.25, -.4, .8),
                                                                         bevel=0)
    a.part('Beacons', 'BarrelRed').sphere(.06, loc=(0, 3.4, 4.32), seg=8, rings=4)
    a.part('Beacons', 'BarrelRed').sphere(.05, loc=(0, -.5, .52), seg=8, rings=4)
    ant = a.part('Antennas', 'Steel')
    K.blade_antenna(ant, (0, -.2, 2.36), h=.22, chord=.14)
    K.blade_antenna(ant, (0, 1.0, .55), h=.18, chord=.12, normal=(0, 0, -1))
    K.whip_antenna(ant, (.5, -1.8, 2.36), h=.5, r=.015, lean=.4)
    k.block(a.part('Hoist', 'Armor'), (.25, .35, .2), loc=(-HW - .12, -3.5, 2.2), chamfer=.02)
    a.part('Pitot', 'Steel').cyl(.015, .35, loc=(.3, -5.3, 1.5), rot=(R90, 0, 0), seg=5, bevel=0)


def _skin(a):
    """Skin detail for the battle read: access panels one tone off, rivet rows, kick steps, walkway strips,
    warning marks, the side-door ammunition boxes."""
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        for i, y in enumerate((-3.0, -2.2, -1.1, .1, 1.2, 2.4, 3.2)):
            mat = 'Armor' if i % 2 else 'Undercarriage'
            a.part(f'Access_panels_{mat.lower()}', mat).box((.012, .35 + .04 * i, .22 + .03 * i + .02 * s), loc=(s * (HW + .008), y, .85), bevel=0)
            a.part('Access_panels_hazard', 'Hazard').box((.012, .12, .06), loc=(s * (HW + .009), y + .3, 2.15),
                                                         bevel=0)
        K.rivet_line(rv, (s * (HW + .005), -3.9, 2.24), (s * (HW + .005), 3.5, 2.24), (s, 0, 0), pitch=.7, r=.014)
        K.grille(a, (s * .62, 2.3, 3.3), .9, .4, facing=(s, 0, .15), slats=5)
        for z in (1.1, 1.45, 1.8):
            a.part('Kick_steps', 'Steel').box((.04, .14 + z * .05 + s * .01, .03), loc=(s * (HW + .02), -4.4, z), bevel=0)
        a.part('Hazard_marks', 'Hazard').box((.02, .5, .08), loc=(s * .63, 2.0, 3.6), rot=(0, s * .14, 0), bevel=0)
    mats = ('Armor', 'Undercarriage', 'Steel', 'Team', 'Charred')
    for i in range(9):
        for j, x in enumerate((-.62, .62)):
            if -3.6 < -4.0 + i * .9 < -2.0 and abs(x) < .7:
                pass
            mat = mats[(i + j * 2) % 5]
            a.part(f'Roof_panels_{mat.lower()}', mat).box((.24 + .03 * i, .4 + .04 * i + .1 * j, .02), loc=(x, -4.0 + i * .95, 2.355 + .002 * j),
                                                          bevel=0)
    for (x, y) in ((.3, -1.0), (-.3, .2), (.3, 1.3)):
        k.lathe(a.part('Vents', 'Steel'), [(.09, 0), (.09, .06), (.06, .08), (0, .08)], loc=(x, y, 2.35), seg=8)
    for x in (-.25, .25):
        a.part('Walkways', 'Charred').box((.18, 6.5, .01), loc=(x, -.4, 2.357), bevel=0)
    for y in (-2.2, -1.9):
        P.ammo_box(a, (-.6, y, .58), size=(.35, .22, .2))
    # Hand grips, drain masts, belly blade antennas, lights, the tie-down rings, the wire cutters.
    grips = a.part('Kit_handles', 'Steel')
    for s in (-1, 1):
        for y in (-3.8, -1.5, .6, 2.6):
            grips.box((.05, .12 + .02 * (y + 4) + .01 * s, .04), loc=(s * (HW + .03), y, 1.95), bevel=0)
        for y in (-2.8, 1.8):
            a.part('Drain_masts', 'Steel').box((.03, .08, .14), loc=(s * .6, y, .5), rot=(.3, 0, 0), bevel=0)
        a.part('Lamps', 'Lamp').box((.08, .08, .04), loc=(s * .4, -4.4, .53), bevel=0)
        for y in (-3.2, -1.0, 1.2, 3.2):
            a.part('Tie_rings', 'Steel').torus(.05, .012, loc=(s * (HW + .04), y, .62), rot=(0, R90, 0), seg=6, ring=3)
    ant = a.part('Antennas', 'Steel')
    for y in (-3.5, -2.0, 2.0, 3.0):
        K.blade_antenna(ant, (.3 if y < 0 else -.3, y, .55), h=.14, chord=.1, normal=(0, 0, -1))
    a.part('Wire_cutters', 'Steel').box((.04, .05, .35), loc=(0, -5.05, 2.1), rot=(-.6, 0, 0), bevel=0)
    a.part('Wire_cutters', 'Steel').box((.04, .05, .3), loc=(0, -5.3, .55), rot=(.5, 0, 0), bevel=0)


def twin_rotor_gunship(a):
    K.suffixed(a)
    _fuselage(a)
    _skin(a)
    _pylons(a)
    _gear_and_sponsons(a)
    _weapons(a)
    r = a.pivot('Rotor', FRONT_R)
    K.rotor_head(a, r, 3, 2.85, .3, hub=.24, cap=.16, stripe=.3)
    rr = a.pivot('Rotor_rear', REAR_R)
    K.rotor_head(a, rr, 3, 2.85, .3, hub=.24, cap=.16, stripe=.3, phase=math.pi / 3)
    # The rear head's meshes keep the old names (Rotor_rear_hub, _grips, _blades, _tips).
    for i, key in enumerate(a.order):
        name, mat, parent = key
        if parent == 'Rotor_rear' and name.startswith('Rotor_'):
            new = (name.replace('Rotor_', 'Rotor_rear_', 1), mat, parent)
            a.shapes[new] = a.shapes.pop(key)
            a.order[i] = new
    k.clean(a)


BUILDERS = {'twin_rotor_gunship': (twin_rotor_gunship, dict(ao_distance=.5, grime_height=.2, ground=False))}
