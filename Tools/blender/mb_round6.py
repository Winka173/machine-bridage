"""Machine Brigade round 6 vehicles, built with frontier_kit and the aircraft / vehicle kits of mb_air,
mb_vehicles and mb_artillery. Each model replaces an older one that looked like another unit.

  * heavy_attack_heli: coaxial-rotor attack helicopter (Ka-52 "Alligator" lineage), origin on the ground
    under the cabin (the wheels stand on z = 0). Two stacked three-blade rotors, `Rotor` (upper) and
    `Rotor_2` (lower); the lower pivot is turned 180 degrees about Y so the game's spin about local up
    turns it the other way. No tail rotor: a stabiliser with twin end-plate fins. A side-by-side
    cockpit, stub wings with two pylons each (a 20-tube rocket pod inboard, a six-round anti-tank
    missile pack outboard) and wingtip countermeasure pods carrying twin Igla launchers.
    `Muzzle_rocket` between the rocket pods (launch points: the `Pods`), `Muzzle_missile` between the
    missile packs (`Launch_tubes`), `Muzzle_aam` at the left wingtip Igla, and the 30 mm cannon on the
    right of the fuselage on `Mount_gun` with `Muzzle_gun`.
  * attack_jet: close-support jet (Su-25 "Frogfoot" lineage), origin at the fuselage centre (it
    flies). A long pointed nose with the twin-barrel cannon under its left side (`Muzzle_gun`, the data's
    main slot, and `Muzzle_main` at the same point), a bubble canopy, twin engines in nacelles along the
    lower fuselage under the shoulder wing, wingtip airbrake pods, one fin and a tailplane. Ten pylons:
    bombs, rocket pods (`Pods`, `Muzzle_rocket`), a heavy bomb outboard on each wing whose bodies are the
    missile slot's launchers (`Missile_racks`, `Muzzle_missile`) and an R-60 on each outer pylon
    (`Muzzle_aam` at the left one).
  * siege_tank: super-heavy siege howitzer (KV-2 / Sturmtiger / 2S4 lineage): a long heavy hull behind
    thick bolted skirts and a huge slab-sided `Turret` with a short, very fat 305 mm barrel in a drum
    mantlet (Main_cannon*, Muzzle_brake, `Muzzle_main`), an ammunition crane with a shell on the hook at
    the turret rear and a roof heavy machine gun on `Mount_mg` (`Muzzle_mg`).

Conventions as in mb_air / mb_vehicles: metres, +Z up, Blender -Y is the front. Pivots that the game
pairs by slot take a numeric suffix (`Mount_mg.001`); they are authored as `Mount_mg__001` (frontier_kit
refuses runtime names with a dot) and renamed after the asset is finished (see `finish`).

Headless: blender --background --python Tools/blender/mb_round6.py -- [--out DIR] [names...]
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import frontier_kit as kit  # noqa: E402
import mb_detail as hd  # noqa: E402
import mb_weapons as wpn  # noqa: E402
from mb_air import (ACROSS, BACKWARD, FORWARD, R90, RIGHT, LEFT, Planform, _aam, _aam_parts, _blade,  # noqa: E402
                    _bomb, _bubble, _canopy, _dome, _exhaust_duct, _hoop, _octagon, _patch, _pylon, _revolve,
                    _rocket_pod, _sec, _skin_panel, _skin_z, _store_parts, _surface, _trap_fin, _upright, _wing)
from mb_vehicles import (_antenna, _frame, _glacis, _grille_frame, _hatch, _headlight, _periscopes, _smoke,  # noqa: E402
                         _stowage_bin, _taillight, _track_links, tracks)
from mb_vehicles2 import _axis  # noqa: E402

ROOT = HERE.parents[1]
OUT = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'


# ----------------------------------------------------------------------------- build helpers
def dotted(name):
    """Kit-safe spelling of a suffixed runtime name: 'Mount_mg.001' -> 'Mount_mg__001'."""
    return name.replace('.', '__')


def pivot(a, name, loc, parent=None):
    """a.pivot for names that may carry a Blender-style suffix (Mount_gun.001); returns the kit key."""
    return a.pivot(dotted(name), loc, dotted(parent) if parent else None)


def flip_spinner(a, name):
    """Turn a spinner pivot 180 degrees about Y without moving its meshes: the game spins it about its
    local up, which then points down, so it turns the other way (the lower rotor of a coaxial pair)."""
    p = a.pivots[name]
    turn = Matrix.Rotation(math.pi, 4, 'Y')
    for o in a.collection.objects:
        if o.parent is p and o.type == 'MESH':
            o.data.transform(turn)          # inverse of the pivot's turn: the mesh stays where it was
            o.location = turn @ o.location
    p.rotation_euler = (0.0, math.pi, 0.0)


def finish(a):
    """Finish an asset, run its post steps (a.post) and give suffixed pivots their runtime names."""
    a.finish()
    for step in getattr(a, 'post', []):
        step(a)
    for o in list(a.collection.objects):
        if '__' in o.name:
            want = o.name.replace('__', '.')
            o.name = want
            if o.name != want:
                raise ValueError(f'{a.name}: could not name {want} (got {o.name})')
    return a


def uniform_scale(k):
    """Post step: scale the whole finished asset by k about the origin (pivots only translate)."""
    def step(a):
        m = Matrix.Scale(k, 4)
        for o in a.collection.objects:
            o.location = o.location * k
            if o.type == 'MESH':
                o.data.transform(m)
            elif o.type == 'EMPTY':
                o.empty_display_size *= k
    return step


def build(builders, names=(), out=OUT, extra=None):
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o)
    root = kit.workspace()
    kit.clear_workspace(root)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    # Extra builders (high-detail variants) are only built when named.
    todo = dict(builders, **{k: v for k, v in (extra or {}).items() if k in names})
    for name, (fn, options) in todo.items():
        if names and name not in names:
            continue
        a = kit.Asset(name, root, **options)
        fn(a)
        finish(a)
        a.export(out / f'{name}.glb')
        report[name] = a.triangles()
        print(f'BUILT {name}: {a.triangles()} triangles -> {out / (name + ".glb")}')
        kit.clear_workspace(root)
    return report


def main(builders, extra=None):
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = OUT
    if '--out' in args:
        i = args.index('--out')
        out = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    build(builders, tuple(args), out, extra)
    print('MB_ROUND_COMPLETE')


# ----------------------------------------------------------------------------- Ka-52
def _coax_rotor(a, name, loc, phase, R=7.5, chord=.5, blades=3, t=.06, hub=.34):
    """One rotor of a coaxial pair on its own pivot (spins about local Z): a hub disc with blade grips
    and dampers, a cap, and airfoil blades with yellow tip stripes. Part names carry the pivot name so
    two rotors never share one."""
    r = a.pivot(name, loc)
    steel = a.part(f'{name}_hub', 'Steel', r)
    grips = a.part(f'{name}_grips', 'Armor', r)
    bl = a.part(f'{name}_blades', 'Armor', r)
    tips = a.part(f'{name}_tips', 'Hazard', r)
    steel.cyl(hub, .14, seg=12, bevel=.02, bseg=1)
    steel.cyl(hub * .7, .1, loc=(0, 0, .12), seg=10, bevel=0)
    grip = .62
    for k in range(blades):
        ang = phase + k * math.tau / blades
        d = Vector((math.cos(ang), math.sin(ang), 0))
        e = Vector((-math.sin(ang), math.cos(ang), 0))
        grips.box((grip, chord * .6, .12), loc=tuple(d * (hub * .55 + grip / 2) + Vector((0, 0, .01))), rot=(0, 0, ang),
                  bevel=.02, seg=1)
        steel.cyl(.035, grip * .7, loc=tuple(d * (hub * .8 + grip * .35) + e * chord * .38 + Vector((0, 0, .02))),
                  rot=(0, R90, ang), seg=5, bevel=0)                                          # lead-lag damper
        _blade(bl, tips, d, e, (0, 0, 1), hub * .55 + grip - .08, R, chord, t, stripe=.42, tip=.2, droop=.1)
    return r


def heavy_attack_heli(a):
    """Coaxial-rotor attack helicopter (Ka-52 "Alligator" lineage), 15.8 m over the rotors: a radar
    nose, a wide side-by-side cockpit under a framed canopy with big bulged side windows, engine
    nacelles with dust-filter caps and outward exhausts high on the sides, a tall coaxial mast with
    two stacked three-blade rotors, stub wings with a rocket pod and an anti-tank missile pack each and
    countermeasure pods with twin Igla launchers at the tips, the 30 mm cannon on the right side, a
    long boom ending in a stabiliser with twin end-plate fins and a small central fin, and tricycle
    wheels. Origin on the ground under the cabin (wheels on z = 0)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    hull = [
        _octagon(-7.85, .26, 1.5, 1.94),
        _octagon(-7.45, .46, 1.32, 2.04),
        _octagon(-7.0, .62, 1.2, 2.14),
        _octagon(-6.4, .8, 1.06, 2.22),
        _octagon(-5.6, .96, .98, 2.27),
        _octagon(-4.2, 1.03, .96, 2.32),
        _octagon(-3.0, 1.03, .98, 2.62),
        _octagon(-.8, .98, 1.02, 2.76),
        _octagon(1.0, .82, 1.15, 2.7),
        _octagon(2.4, .52, 1.55, 2.56),
    ]
    body.loft([[(0, -8.12, 1.72)]] + hull, bevel=.06, seg=1)                                      # radar nose
    boom = [_octagon(2.2, .52, 1.58, 2.56), _octagon(5.4, .34, 1.86, 2.4), _octagon(7.0, .2, 1.98, 2.3)]
    body.loft(boom + [[(0, 7.35, 2.14)]], bevel=.04, seg=1)
    armor.lathe([(0, -8.16), (.1, -8.08), (.22, -7.9), (.27, -7.78)], loc=(0, 0, 1.72), rot=BACKWARD, seg=10)  # radome cap
    # Side-by-side cockpit: a framed canopy wider than the fuselage, bulged side windows, a centre post.
    st = [(-6.78, .52, 1.95, 2.24), (-6.25, .86, 1.88, 2.86), (-5.3, 1.0, 1.88, 3.06), (-4.3, 1.05, 1.9, 3.03),
          (-3.82, .94, 1.94, 2.8)]
    glass.loft([_bubble(y, w, z0, z1) for y, w, z0, z1 in st], bevel=.02, seg=1)
    secs = [_bubble(y, w + .012, z0, z1 + .012) for y, w, z0, z1 in st]
    for sec in secs[1:4]:
        _hoop(frames, sec, r=.035)
    for i in (2, 3, 4, 5):                                                                       # canopy rails
        frames.tube([tuple(Vector(q[i]) + Vector((0, 0, .01))) for q in secs[1:]], .03, seg=5)
    frames.tube([(0, -6.3, 2.88), (0, -5.3, 3.08), (0, -4.3, 3.05)], .035, seg=5)                 # centre spine
    for s in (-1, 1):
        frames.tube([(s * 1.02, -5.25, 1.93), (s * .98, -5.1, 2.9)], .03, seg=5)                  # door frames
        armor.box((.05, 1.3, .36), loc=(s * 1.03, -4.9, 1.62), bevel=.012, seg=1)                 # cockpit armour
        steel.bolts([(s * 1.06, y, z) for y in (-5.45, -4.35) for z in (1.5, 1.74)], r=.03, h=.03, rot=ACROSS,
                    seg=6, bevel=0)
    # Cheek sensor ball under the nose; air-data boom; lamps.
    armor.cyl(.1, .2, loc=(0, -6.55, 1.02), seg=8, bevel=0)
    armor.sphere(.3, loc=(0, -6.55, .86), seg=12, rings=8)
    sensor = a.part('Sensor', 'Glass')
    sensor.cyl(.14, .05, loc=(0, -6.83, .86), rot=FORWARD, seg=10, bevel=0)
    sensor.cyl(.06, .05, loc=(.17, -6.79, .96), rot=FORWARD, seg=8, bevel=0)
    steel.tube([(.3, -7.5, 1.96), (.32, -8.1, 2.0), (.33, -8.6, 2.02)], .025, seg=6)              # air-data boom
    a.part('Lamps', 'Lamp').box((.22, .15, .06), loc=(0, -5.0, .95), bevel=.01, seg=1)
    # Engine deck: nacelles on the upper sides, dust-filter caps, outward exhausts; gearbox fairing.
    for s in (-1, 1):
        x = s * 1.02
        body.cyl(.46, 3.3, loc=(x, -1.1, 2.62), rot=FORWARD, seg=14, bevel=.1)
        armor.cyl(.5, .5, loc=(x, -2.85, 2.62), rot=FORWARD, seg=14, bevel=.04, bseg=1)               # filter drum
        armor.sphere((.46, .3, .46), loc=(x, -3.1, 2.62), seg=12, rings=6)                            # filter cap
        dark.grille(.5, .32, loc=(x + s * .49, -2.85, 2.62), rot=(0, 0, s * R90), slats=3, depth=.04, thickness=.03)
        _exhaust_duct(a, (s * 1.38, .85, 2.78), s * -.55, size=(.4, .9, .44), pitch=-.15)
        panels.box((.04, 1.4, .4), loc=(x + s * .44, -1.0, 2.62), bevel=.01, seg=1)                  # cowl doors
    body.box((1.2, 3.6, .7), loc=(0, -1.05, 2.95), bevel=.14, seg=2, taper=(.7, .82))                 # z 2.6 .. 3.3
    armor.cyl(.34, .12, loc=(0, -.95, 3.32), seg=14, bevel=.02, bseg=1)                              # mast base
    steel.cyl(.2, .5, loc=(0, -.95, 3.52), seg=12, bevel=0)                                          # z 3.27 .. 3.77
    steel.cyl(.15, 1.2, loc=(0, -.95, 4.3), seg=10, bevel=0)                                         # inter-rotor mast
    for zz in (3.62, 4.62):
        steel.cyl(.3, .05, loc=(0, -.95, zz), seg=12, bevel=0)                                       # swashplates
        for k in range(3):
            ang = k * math.tau / 3 + .4
            steel.cyl(.02, .2, loc=(math.cos(ang) * .22, -.95 + math.sin(ang) * .22, zz + .12), seg=4, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, .8, _skin_z(hull, .8, 0) + .02), seg=8, rings=5)
    steel.cyl(.015, .8, loc=(-.3, 2.3, 2.95), seg=5, bevel=0)                                        # antennas
    steel.box((.025, .3, .2), loc=(0, -2.6, .92), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    # Tail: stabiliser with twin end-plate fins, a small central fin, tail bumper.
    body.box((3.4, .9, .12), loc=(0, 6.1, 2.28), bevel=.03, seg=1, taper=(1, .7))
    for s in (-1, 1):
        body.prism([(5.62, 1.72), (6.62, 1.82), (6.95, 3.22), (6.35, 3.25)], .1, loc=(s * 1.72, 0, 0), bevel=.025)
        glow.box((.05, .14, .06), loc=(s * 1.78, 6.9, 3.1), bevel=0)
    body.prism([(6.2, 2.3), (7.2, 2.22), (7.35, 3.05), (6.95, 3.08)], .14, bevel=.03)                # central fin
    steel.limb((0, 6.6, 1.9), (0, 6.75, 1.45), .08, .08, bevel=0)                                    # tail bumper
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 7.35, 2.2), seg=8, rings=5)
    for s in (-1, 1):                                                                                # flare dispensers
        armor.box((.1, .6, .24), loc=(s * .44, 3.6, 2.35), bevel=.02, seg=1)
        dark.grille(.5, .22, loc=(s * .5, 3.6, 2.35), rot=(0, 0, s * R90), slats=3, depth=.03, thickness=.03)
    # Stub wings: inner pylon a 20-tube rocket pod, outer a six-round missile pack, a countermeasure pod
    # with twin Igla launchers at each tip.
    pylons = a.part('Pylons', 'Armor')
    tubes = a.part('Launch_tubes', 'Fuel')
    zw = 2.08
    for s in (-1, 1):
        body.box((2.75, 1.35, .2), loc=(s * 2.3, -1.2, zw), bevel=.04, seg=1, taper=(1, .92))
        # Inner: rocket pod.
        x = s * 1.78
        _pylon(pylons, x, -1.75, -.55, zw - .05, zw - .38, w=.14)
        _rocket_pod(a, x, -2.3, zw - .7, .3, 1.95, tubes=9)
        # Outer: missile pack, two rows of three tubes in a frame.
        x = s * 2.82
        _pylon(pylons, x, -1.7, -.6, zw - .05, zw - .3, w=.12)
        armor.box((.62, 1.6, .06), loc=(x, -1.25, zw - .32), bevel=0)                               # launcher beam
        for dx in (-.18, 0, .18):
            for dz in (-.47, -.64):
                tubes.cyl(.085, 2.0, loc=(x + dx, -1.25, zw + dz), rot=FORWARD, seg=8, bevel=.012, bseg=1)
                dark.cyl(.062, .02, loc=(x + dx, -2.255, zw + dz), rot=FORWARD, seg=8, bevel=0)
        for yy in (-1.95, -.6):
            armor.box((.66, .12, .44), loc=(x, yy, zw - .56), bevel=.015, seg=1)                    # frame bands
        a.part('Missile_bands', 'Hazard').box((.67, .06, .45), loc=(x, -1.1, zw - .56), bevel=0)
        # Wingtip: countermeasure pod, its windows, and twin Igla launchers under it.
        x = s * 3.72
        cm = a.part('CM_pods', 'Armor')
        cm.lathe([(0, 0), (.1, .08), (.2, .3), (.2, 1.3), (.14, 1.55), (0, 1.62)], loc=(x, -2.1, zw), rot=BACKWARD,
                 seg=10)
        sensor.box((.05, .14, .1), loc=(x + s * .19, -1.8, zw + .03), bevel=0)
        sensor.box((.05, .14, .1), loc=(x + s * .19, -.72, zw + .03), bevel=0)
        glow.box((.05, .14, .06), loc=(x + s * .18, -1.2, zw + .14), bevel=0)
        pylons.box((.08, .9, .12), loc=(x, -1.3, zw - .22), bevel=0)
        igla = a.part('Igla_tubes', 'Fuel')
        for dx in (-.08, .08):
            igla.cyl(.055, 1.7, loc=(x + dx, -1.35, zw - .34), rot=FORWARD, seg=8, bevel=0)
            dark.cyl(.04, .02, loc=(x + dx, -2.205, zw - .34), rot=FORWARD, seg=8, bevel=0)
        a.part('Igla_bands', 'Hazard').box((.28, .06, .13), loc=(x, -2.0, zw - .34), bevel=0)
    a.pivot('Muzzle_rocket', (0, -2.32, zw - .7))
    a.pivot('Muzzle_missile', (0, -2.27, zw - .555))
    a.pivot('Muzzle_aam', (3.72 - .08, -2.23, zw - .34))
    # The 30 mm cannon on the right (-X) of the fuselage under the wing root, on its own mount.
    armor.box((.3, 1.4, .5), loc=(-1.0, -1.55, 1.45), bevel=.06, seg=1, taper=(.9, .9))            # gun fairing
    g = pivot(a, 'Mount_gun', (-1.18, -1.7, 1.42))
    gm = a.part('Gun_mount', 'Armor', g)
    gm.box((.26, .9, .34), loc=(0, .1, 0), bevel=.04, seg=1)                                         # cradle
    gm.box((.3, .5, .3), loc=(-.1, .4, .02), bevel=.03, seg=1)                                       # ammo box
    gun = a.part('Gun', 'Steel', g)
    gun.box((.18, .9, .2), loc=(0, -.6, 0), bevel=.02, seg=1)                                        # receiver
    gun.cyl(.075, .6, loc=(0, -1.3, 0), rot=FORWARD, seg=10, bevel=0)                                # jacket
    gun.cyl(.05, 2.1, loc=(0, -2.5, 0), rot=FORWARD, seg=8, bevel=0)                                 # barrel
    gun.cyl(.08, .3, loc=(0, -3.6, 0), rot=FORWARD, seg=10, bevel=0)                                 # muzzle brake
    a.part('Gun_bore', 'Undercarriage', g).cyl(.045, .02, loc=(0, -3.755, 0), rot=FORWARD, seg=8, bevel=0)
    pivot(a, 'Muzzle_gun', (0, -3.77, 0), 'Mount_gun')
    # Tricycle gear: twin nose wheels, main wheels on struts from the lower sides.
    gear = a.part('Gear', 'Steel')
    tyres = a.part('Tyres', 'Rubber')
    for x in (-.17, .17):
        tyres.cyl(.27, .15, loc=(x, -5.25, .27), rot=ACROSS, seg=10, bevel=.04, bseg=1)
        gear.cyl(.12, .2, loc=(x * 1.02, -5.25, .27), rot=ACROSS, seg=8, bevel=0)
    gear.cyl(.05, .5, loc=(0, -5.25, .27), rot=ACROSS, seg=6, bevel=0)
    gear.limb((0, -5.25, .27), (0, -5.1, 1.02), .11, .11, bevel=.02, seg=1)
    for s in (-1, 1):
        body.loft([[(s * .96 + q[0], q[1], q[2]) for q in _sec(y, w, .72, 1.3, n=10)] for y, w in
                   ((-.55, .12), (-.2, .26), (.9, .26), (1.35, .12))], bevel=.02, seg=1)             # gear sponsons
        tyres.cyl(.36, .24, loc=(s * 1.3, .45, .36), rot=ACROSS, seg=12, bevel=.06, bseg=1)
        gear.cyl(.17, .27, loc=(s * 1.3, .45, .36), rot=ACROSS, seg=8, bevel=0)
        gear.limb((s * 1.2, .45, .36), (s * 1.0, .3, 1.0), .12, .12, bevel=.02, seg=1)
    # Coaxial rotors: upper `Rotor`, lower `Rotor_2` (counter-rotating), blades 60 degrees apart.
    _coax_rotor(a, 'Rotor', (0, -.95, 4.95), 0.0)
    _coax_rotor(a, 'Rotor_2', (0, -.95, 3.82), math.pi / 3)
    a.post = [lambda a_: flip_spinner(a_, 'Rotor_2')]


# ----------------------------------------------------------------------------- Su-25
def attack_jet(a, detail=False):
    """Close-support jet (Su-25 "Frogfoot" lineage), 13.4 x 12.7 m: a long pointed nose with a laser
    window at its tip and the twin-barrel cannon under its left side, an armoured cockpit under a bubble
    canopy with a dorsal spine behind it, two engines in nacelles along the lower fuselage sides under
    the shoulder wing (intakes behind the cockpit, nozzles under the tail), straight tapered wings with
    flaps, ailerons and split airbrakes in the wingtip pods, a single fin with its rudder and a
    tailplane. Five pylons a wing: a bomb, two rocket pods, a heavy bomb and an R-60 air-to-air missile.
    Origin at the fuselage centre (it flies). detail=True marks the asset so the kit helpers add their
    high-detail parts (for an attack_jet_hd built from this model)."""
    hd.mark(a, detail)
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=16, pt=2.4, pb=2.6)
    hull = [sec(-6.55, .1, -.1, .07), sec(-6.2, .21, -.23, .16), sec(-5.5, .35, -.41, .31), sec(-4.6, .46, -.55, .45),
            sec(-3.7, .52, -.61, .54), sec(-2.8, .56, -.63, .6), sec(-1.6, .56, -.62, .6), sec(0.0, .5, -.58, .58),
            sec(1.8, .42, -.46, .54), sec(3.3, .32, -.3, .48), sec(4.6, .24, -.13, .44), sec(5.5, .17, .01, .4),
            sec(5.95, .1, .11, .34)]
    body.loft([[(0, -6.72, -.02)]] + hull + [[(0, 6.2, .24)]], bevel=.015, seg=1)
    glass.lathe([(0, -6.74), (.07, -6.66), (.1, -6.5)], loc=(0, 0, -.02), rot=BACKWARD, seg=10)     # laser window
    _patch(armor, hull, -4.6, -3.75, 6, 10)                                                     # anti-glare panel
    for i0, i1 in ((3, 5), (11, 13)):                                                           # cockpit armour
        _patch(panels, hull, -3.6, -2.0, i0, i1, out=.016, inn=.012, bevel=.005)
    steel.tube([(-.2, -5.9, .18), (-.21, -6.6, .2), (-.22, -7.2, .2)], .02, seg=5)              # air-data boom
    steel.box((.1, .16, .12), loc=(-.2, -5.9, .2), bevel=0)
    # Twin-barrel cannon under the left (+X) side of the nose, in a blister fairing.
    gx, gz = .3, -.5
    armor.loft([[(gx, -5.0, gz)]] + [[(gx + q[0], y, q[2]) for q in _sec(y, w, gz - h, gz + h, n=8)]
                                     for y, w, h in ((-4.8, .1, .08), (-4.3, .16, .13), (-3.2, .14, .12))],
               bevel=0)
    for dx in (-.05, .05):
        steel.cyl(.035, .9, loc=(gx + dx, -5.25, gz - .02), rot=FORWARD, seg=6, bevel=0)
    steel.cyl(.1, .1, loc=(gx, -4.95, gz - .02), rot=FORWARD, seg=10, bevel=0)                  # barrel clamp
    a.part('Gun_bore', 'Undercarriage').box((.18, .03, .06), loc=(gx, -5.7, gz - .02), bevel=0)
    a.pivot('Muzzle_gun', (gx, -5.72, gz - .02))
    a.pivot('Muzzle_main', (gx, -5.72, gz - .02))
    # Bubble canopy with a framed windscreen, the dorsal spine behind it.
    st = [(-3.95, .2, .6), (-3.6, .38, .9), (-3.0, .44, 1.03), (-2.4, .42, 1.0), (-1.95, .3, .86)]
    _canopy(glass, frames, [(y, w, _skin_z(hull, y, w) - .03, z1) for y, w, z1 in st], bows=(-3.55, -2.9))
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in ((-2.15, .32, .84), (-1.0, .36, .74),
                                                                         (1.5, .3, .64), (3.6, .21, .52))]
    body.loft(spine + [[(0, 4.4, .47)]], bevel=.015, seg=1)
    for y, z, t in ((-.6, .76, -.35), (2.4, .6, -.35), (-1.2, -.66, .35)):                        # blade aerials
        steel.box((.02, .24, .18), loc=(0, y, z), rot=(t, 0, 0), bevel=0, taper=(1, .5))
    # Engine nacelles along the lower sides: intake lips behind the cockpit, nozzles under the tail.
    for s in (-1, 1):
        x, zc = s * .64, -.34
        body.lathe([(.29, -2.46), (.36, -2.2), (.38, -1.5), (.38, 2.1), (.33, 3.4), (.28, 4.12)], loc=(x, 0, zc),
                   rot=BACKWARD, seg=14)
        _revolve(armor, [(.26, -.06), (.31, -.08), (.33, .04), (.28, .06)], (x, -2.4, zc), BACKWARD, 14)  # lip
        dark.cyl(.25, .04, loc=(x, -2.36, zc), rot=FORWARD, seg=12, bevel=0)                          # fan face
        steel.cyl(.07, .12, r2=.02, loc=(x, -2.42, zc), rot=FORWARD, seg=8, bevel=0)
        dark.grille(.5, .16, loc=(x + s * .37, 1.4, zc - .05), rot=(0, 0, s * R90), slats=3, depth=.03,
                    thickness=.025)                                                                    # cooling louvres
        a.part('Nozzles', 'Steel').lathe([(.29, 4.0), (.27, 4.5), (.23, 4.6), (.2, 4.6), (.22, 4.2)], loc=(x, 0, zc),
                                         rot=BACKWARD, seg=12)
        a.part('Nozzle_liners', 'Undercarriage').cyl(.2, .04, loc=(x, 4.35, zc), rot=FORWARD, seg=12, bevel=0)
        a.part('Exhaust_glow', 'Alloy').torus(.12, .025, loc=(x, 4.4, zc), rot=FORWARD, seg=12, ring=4)
    # Shoulder wing: flaps and ailerons, split airbrakes in the wingtip pods.
    wing = Planform(.45, 6.05, -2.05, -.12, 2.9, 1.2, .3, .11, .36, .16)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(.95, 3.4, .7), (3.5, 5.85, .72)], bevel=.01)
        _skin_panel(panels, wing, frame, 1.2, 3.1, .18, .55)
        _skin_panel(panels, wing, frame, 3.7, 5.4, .2, .56)
    pods = a.part('Tip_pods', 'Team')
    brakes = a.part('Airbrakes', 'Armor')
    for s in (-1, 1):
        x, z = s * 6.16, wing.at(6.05)[3]
        pods.lathe([(0, -.55), (.08, -.45), (.14, -.15), (.15, 1.3), (.13, 1.62)], loc=(x, 0, z), rot=BACKWARD, seg=10)
        for up in (-1, 1):                                                                   # split airbrake petals
            brakes.box((.24, .55, .03), loc=(x, 1.86, z + up * .1), rot=(up * .22, 0, 0), bevel=0)
        glow.box((.05, .1, .05), loc=(x + s * .14, -.2, z), bevel=0)
        a.part('Lamps', 'Lamp').cyl(.05, .02, loc=(x, -.54, z), rot=FORWARD, seg=8, bevel=0)
    # Single fin with its rudder; tailplane with elevators.
    fin = Planform(0, 1.85, 3.75, 5.0, 2.2, 1.0, .16, .07)
    _wing(body, moving, fin, _upright(0, .42, 0), cs=[(.25, 1.75, .66)], lower=1.0, bevel=.01)
    stab = Planform(0, 2.35, 4.25, 5.0, 1.45, .75, .12, .06, .2, .32)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.35, 2.25, .66)], bevel=.01)
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, 5.75, 2.2), seg=8, rings=5)
    # Stores on ten pylons.
    pylons = a.part('Pylons', 'Armor')
    light = _store_parts(a, None, 'Ordnance')
    heavy = dict(light, body=a.part('Missile_racks', 'Armor'))
    aams = _aam_parts(a, 'Aams')
    for s in (-1, 1):
        x = s * 1.38                                                                          # FAB-250
        zt = wing.bottom(1.38)
        _pylon(pylons, x, -1.55, -.35, zt + .05, zt - .16, w=.08)
        _bomb(light, (x, -1.0, zt - .16 - .15), length=1.35, r=.14, seg=8)
        for x in (s * 2.15, s * 3.1):                                                        # B-8M rocket pods
            zt = wing.bottom(abs(x))
            _pylon(pylons, x, -1.45, -.2, zt + .05, zt - .14, w=.08)
            _rocket_pod(a, x, -1.9, zt - .14 - .25, .24, 1.75, tubes=7)
        x = s * 3.95                                                                          # FAB-500
        zt = wing.bottom(3.95)
        _pylon(pylons, x, -1.1, .1, zt + .05, zt - .16, w=.08)
        _bomb(heavy, (x, -.55, zt - .16 - .19), length=1.75, r=.18, seg=8)
        x = s * 4.85                                                                          # R-60
        zt = wing.bottom(4.85)
        _pylon(pylons, x, -.85, .15, zt + .05, zt - .12, w=.07)
        pylons.box((.08, .9, .05), loc=(x, -.4, zt - .13), bevel=0)                           # launch rail
        _aam(aams, (x, -.45, zt - .13 - .07), length=1.6, r=.055)
    zr = wing.bottom(2.15) - .14 - .25
    a.pivot('Muzzle_rocket', (0, -1.92, zr))
    zb = wing.bottom(3.95) - .16 - .19
    a.pivot('Muzzle_missile', (0, -.55 - 1.75 / 2 - .05, zb))
    zt = wing.bottom(4.85) - .2
    a.pivot('Muzzle_aam', (4.85, -1.27, zt))


# ----------------------------------------------------------------------------- siege tank
def _thick_skirts(a, s, x, y0, y1, z0, z1, panels, thick=.16, gap=.04):
    """Heavy bolted skirt plates on side s at |x| (team paint), a dark top lip and a bolt row along the
    top and the bottom of each plate."""
    part = a.part('Skirts', 'Team')
    lip = a.part('Skirt_edge', 'Armor')
    bolts = a.part('Skirt_bolts', 'Steel')
    step = (y1 - y0 + gap) / panels
    for i in range(panels):
        yc = y0 + step * (i + .5) - gap / 2
        w = step - gap
        part.box((thick, w, z1 - z0), loc=(s * x, yc, (z0 + z1) / 2), bevel=.035, seg=1)
        lip.box((thick + .04, w + .02, .07), loc=(s * x, yc, z1 - .02), bevel=0)
        for z in (z0 + .1, z1 - .14):
            for k in range(3):
                bolts.box((.03, .06, .06), loc=(s * (x + thick / 2 + .005), yc - w / 2 + .18 + k * (w - .36) / 2, z),
                          bevel=0)


def _shell_305(part, band, loc, length=1.15, r=.15, up=False):
    """305 mm howitzer shell lying along Y (nose forwards), or standing nose up; a copper driving band."""
    rot = (0, 0, 0) if up else FORWARD
    part.lathe([(r * .95, 0), (r, length * .08), (r, length * .55), (r * .72, length * .82), (r * .28, length),
                (.001, length)], loc=loc if up else (loc[0], loc[1] + length / 2, loc[2]), rot=rot, seg=8)
    if up:
        band.cyl(r + .014, .07, loc=(loc[0], loc[1], loc[2] + length * .16), seg=8, bevel=0)
    else:
        band.cyl(r + .014, .07, loc=(loc[0], loc[1] + length / 2 - length * .16, loc[2]), rot=FORWARD, seg=8, bevel=0)


def siege_tank(a):
    """Super-heavy siege howitzer on a tank chassis (KV-2 / Sturmtiger / 2S4 lineage): a long, heavy hull
    on seven road wheels behind thick bolted skirts, a sloped glacis with spare track links, the driver's
    visor and headlights, an engine deck with grilles and twin exhaust mufflers on the tail. On it a huge
    slab-sided turret with bolted appliqué on its front, a drum mantlet and a short, very fat 305 mm
    howitzer: a stubby recoil sleeve, a thick tube and a heavy muzzle ring round a dark bore. A jib crane
    with a shell on its hook stands at the turret rear over the big loading door; a commander's cupola,
    a mushroom vent and a heavy machine gun on its own mount crown the roof."""
    tracks(a, 1.3, 9.6, .95, .36, 7, .52, belt_width=.64, wheel_seg=10, lean=True, sprocket=1, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    hull.prism([(-4.75, .52), (-5.05, 1.0), (5.1, 1.0), (4.95, .52)], 2.3, bevel=.05)             # belly
    front, top = (-5.25, 1.2), (-4.45, 1.72)
    hull.prism([(-5.0, .95), front, top, (4.75, 1.72), (5.2, 1.45), (5.2, .95)], 3.2, bevel=.07)
    for s in (-1, 1):
        _thick_skirts(a, s, 1.7, -4.7, 4.75, .42, 1.42, 5)
        for y in (-3.8, -1.9, 0.0, 1.9, 3.8):
            armor.box((.1, .16, .2), loc=(s * 1.6, y, 1.32), bevel=0)                          # skirt hangers
    # Glacis: spare track links, the driver's visor block, headlights and tow hooks.
    gy, gz, grot = _glacis(front, top, .45, .02)
    for x in (-.95, -.3, .35):
        _track_links(a, _frame((x, gy, gz), (grot - R90, 0, 0)), 3, width=.5)
    vy, vz, vrot = _glacis(front, top, .8, .08)
    armor.box((.7, .3, .22), loc=(.95, vy, vz), rot=(vrot, 0, 0), bevel=.03, seg=1)             # driver's visor
    glass.box((.4, .04, .05), loc=(.95, vy - .14, vz + .02), rot=(vrot, 0, 0), bevel=0)
    for s in (-1, 1):
        _headlight(a, s * 1.25, -5.2, 1.36, guard=True)
        steel.box((.2, .24, .18), loc=(s * .7, -5.12, .92), bevel=.02, seg=1)                     # tow hooks
        steel.box((.2, .24, .18), loc=(s * .7, 5.22, .98), bevel=.02, seg=1)
        _taillight(a, s * 1.35, 5.2, 1.5)
    _hatch(a, .95, -4.1, 1.7, .28)
    _hatch(a, -.95, -4.1, 1.7, .28)
    _periscopes(a, [(-.95 + dx, -4.45, 1.7, 0) for dx in (-.18, .18)])
    # Engine deck behind the turret: grilles, a fuel filler, tool box and the tow cable; mufflers on the tail.
    for x in (-.65, .65):
        deck.grille(1.0, 1.3, loc=(x, 3.7, 1.73), rot=(-R90, 0, 0), slats=6, depth=.07, thickness=.04)
        _grille_frame(a, x, 3.7, 1.71, 1.0, 1.3, t=.05)
    armor.box((2.6, .7, .2), loc=(0, 2.75, 1.8), bevel=.03, seg=1)                              # air intake hump
    deck.grille(2.2, .45, loc=(0, 2.75, 1.91), rot=(-R90, 0, 0), slats=6, depth=.05, thickness=.03)
    for s in (-1, 1):
        m = a.part('Mufflers', 'Steel')
        m.cyl(.2, .9, loc=(s * .9, 5.35, 1.55), rot=ACROSS, seg=10, bevel=.03, bseg=1)
        armor.box((.9, .08, .5), loc=(s * .9, 5.43, 1.55), bevel=.02, seg=1)                      # heat shields
        a.part('Soot', 'Charred').cyl(.1, .06, loc=(s * (.9 + .45), 5.35, 1.55), rot=ACROSS, seg=8, bevel=0)
        _stowage_bin(a, (s * 1.35, 3.7, 1.9), (.4, 1.6, .34), latch_side=s)
    # Ready rounds for the crane: an open rack of three shells on the rear deck, right side.
    shells = a.part('Shells', 'Steel')
    bands = a.part('Shell_bands', 'BarrelRed')
    armor.box((1.0, .4, .12), loc=(-.1, 4.72, 1.78), bevel=0)
    for k in range(3):
        _shell_305(shells, bands, (-.45 + k * .35, 4.6, 1.99), length=1.0, r=.14)
    steel.cyl(1.42, .12, loc=(0, -.5, 1.72), seg=28, bevel=.02, bseg=1)                          # turret ring

    # Turret: a tall slab-sided box, bolted appliqué on its front, a drum mantlet, the fat howitzer.
    t = a.pivot('Turret', (0, -.5, 1.74))
    body = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    body.prism(chamfered_rect(3.0, 4.4, .28, cy=.2), 2.05, loc=(0, 0, 1.045), axis='Z', bevel=.06, taper=.95)
    for s in (-1, 1):                                                                           # front appliqué
        tarm.box((.85, .14, 1.7), loc=(s * 1.0, -1.98, 1.02), bevel=.03, seg=1)
        tsteel.bolts([(s * 1.0 + dx, -2.06, z) for dx in (-.3, .3) for z in (.3, 1.0, 1.7)], r=.035, h=.04,
                     rot=FORWARD, seg=6, bevel=0)
        tarm.box((.14, 3.2, .55), loc=(s * 1.47, .2, .6), bevel=.02, seg=1)                          # side plates
        glass.box((.03, .3, .06), loc=(s * 1.44, -1.1, 1.5), bevel=0)                                # vision slits
        tarm.box((.06, .42, .14), loc=(s * 1.43, -1.1, 1.58), bevel=0)
        _smoke(a, tsteel, 1.2, -1.6, 2.1, s, count=3, gap=.12, r=.06, depth=.2)
        for y in (-1.5, 1.8):                                                                       # lifting eyes
            tsteel.box((.08, .2, .14), loc=(s * 1.2, y, 2.11), bevel=0)
    # Drum mantlet (static; the gun turns about its axis) and its cheek plates.
    T = Vector((0, -1.72, .98))                                                                    # trunnion
    tarm.cyl(.8, 1.9, loc=tuple(T), rot=ACROSS, seg=20, bevel=.05)
    for s in (-1, 1):
        tarm.cyl(.62, .16, loc=(s * 1.0, T.y, T.z), rot=ACROSS, seg=16, bevel=.02, bseg=1)
    pitch = math.radians(12)
    at = _axis(T, pitch)
    crot = (R90 - pitch, 0, 0)
    brot = (-pitch, 0, 0)
    # The elevating group: a cradle under the bore (sets the pivot's bottom), the sleeve, the tube, the ring.
    a.part('Main_cannon_cradle', 'Armor', t).box((.9, .5, .36), loc=tuple(at(0, -.34)), rot=brot, bevel=.03, seg=1)
    sleeve = a.part('Main_cannon_sleeve', 'Armor', t)
    sleeve.cyl(.46, .95, loc=tuple(at(.95)), rot=crot, seg=18, bevel=.03, bseg=1)
    sleeve.cyl(.49, .1, loc=tuple(at(1.35)), rot=crot, seg=18, bevel=0)
    gun = a.part('Main_cannon', 'Steel', t)
    gun.cyl(.33, 2.0, r2=.31, loc=tuple(at(2.35)), rot=crot, seg=18, bevel=.02, bseg=1)
    gun.cyl(.35, .1, loc=tuple(at(2.2)), rot=crot, seg=18, bevel=0)                               # tube band
    ring = a.part('Muzzle_brake', 'Undercarriage', t)
    ring.lathe([(.3, -.02), (.44, .06), (.45, .46), (.4, .52), (.19, .52), (.19, .3)], loc=tuple(at(3.3)), rot=crot,
               seg=18)
    a.pivot('Muzzle_main', tuple(at(3.84)), t)
    # Rear: the big loading door; the jib crane at the rear right corner with a shell on its hook.
    tarm.box((1.4, .1, 1.2), loc=(0, 2.43, 1.05), bevel=.02, seg=1)
    tsteel.box((.08, .12, .9), loc=(-.6, 2.5, 1.05), bevel=0)                                      # door hinges
    cx, cy = -1.15, 2.0
    tsteel.cyl(.12, .95, loc=(cx, cy, 2.05 + .45), seg=10, bevel=0)                                # crane post
    tsteel.cyl(.22, .12, loc=(cx, cy, 2.12), seg=12, bevel=.02, bseg=1)
    tsteel.limb((cx, cy, 2.9), (cx, cy + 1.45, 3.0), .14, .16, bevel=.02, seg=1)                   # jib
    tsteel.limb((cx, cy, 2.45), (cx, cy + 1.1, 2.95), .07, .07, bevel=0)                           # brace
    tsteel.tube([(cx, cy + 1.38, 2.95), (cx, cy + 1.38, 2.45)], .015, seg=4)                       # hoist cable
    tsteel.box((.16, .16, .14), loc=(cx, cy + 1.38, 2.41), bevel=0)                                # hook block
    _shell_305(a.part('Crane_shell', 'Steel', t), a.part('Crane_shell_band', 'BarrelRed', t),
               (cx, cy + 1.38, 1.25), length=1.08, r=.15, up=True)
    a.part('Crane_winch', 'Hazard', t).box((.3, .34, .3), loc=(cx, cy - .2, 2.3), bevel=.03, seg=1)
    # Roof: commander's cupola, mushroom vent, antenna and the heavy machine gun on its own mount.
    tsteel.cyl(.4, .3, loc=(-.85, -.4, 2.2), seg=16, bevel=.04)
    a.part('Cupola_top', 'Armor', t).cyl(.34, .08, loc=(-.85, -.4, 2.38), seg=16, bevel=.02, bseg=1)
    _periscopes(a, [(-.85 + math.cos(u) * .4, -.4 + math.sin(u) * .4, 2.2, u + R90)
                    for u in (-R90 - .7, -R90, -R90 + .7)], parent=t)
    tarm.cyl(.26, .16, loc=(.1, 1.2, 2.15), seg=12, bevel=.03, bseg=1)                            # mushroom vent
    tsteel.cyl(.1, .14, loc=(.1, 1.2, 2.06), seg=8, bevel=0)
    _hatch(a, .35, .35, 2.07, .3, parent=t)
    _antenna(a, t, 1.2, 1.9, 2.07, 1.0)
    wpn.hmg(a, (.85, -.9, 2.07), parent=t, post=.18, length=1.0, ammo=1)


def chamfered_rect(w, d, c, cy=0.0):
    """Rectangle outline (x, y) with chamfered corners, centred at (0, cy)."""
    x, y = w / 2, d / 2
    return [(px, py + cy) for px, py in ((-x + c, -y), (x - c, -y), (x, -y + c), (x, y - c), (x - c, y), (-x + c, y),
                                         (-x, y - c), (-x, -y + c))]


BUILDERS = {
    'heavy_attack_heli': (heavy_attack_heli, dict(ao_distance=.8, grime_height=.5)),
    'attack_jet': (attack_jet, dict(ao_distance=.6, ground=False)),
    'siege_tank': (siege_tank, dict(ao_distance=.7, grime_height=.6)),
}
# Built only when named: the high-detail Su-25 that should replace the A-10 attack_jet_hd.glb (same pivots
# as attack_jet, so ModelTests.HighDetailVariantsKeepThePivots holds).
EXTRA = {
    'attack_jet_hd': (lambda a: attack_jet(a, detail=True), dict(ao_distance=.6, ground=False)),
}


if __name__ == '__main__':
    main(BUILDERS, EXTRA)
