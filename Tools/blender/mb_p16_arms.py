"""Machine Brigade prompt 16 boss arms: new breakable weapon parts on five existing bosses. Each builder here
calls the current builder of its model (mb_bosses / mb_bosses2 / mb_phase8, unchanged) and adds the new
parts; no existing node is renamed or moved. build_assets.py merges these BUILDERS last, so they win.

  * armored_train: a mortar flatcar coupled behind the gun wagon (headstocks y 10.31 .. 14.76, 5.2 m over
    the buffers; the train is now 25.1 m over the buffers, from y -9.93 to 15.14). On it a twin 120 mm
    mortar on a turntable: `Part_mortar` (on the deck at the car's middle) > `Mount_mortar` (yaw pivot on
    the turntable ring) > two 1.8 m tubes laid 60 degrees up facing forward on baseplates, a cradle and
    elevating struts; `Muzzle_mortar` at the left (+X) tube's bore (`Mortar_tube`; the right one is
    `Mortar_tube_2`).
  * nuke_train: two flatcars behind the missile wagon (headstocks y 11.38 .. 15.43 and 16.19 .. 20.24; the
    train is now 31.6 m over the buffers, from y -11.0 to 20.62). The rocket car carries the armoured
    train's 122 mm launcher (a copy of mb_bosses' `Mount_rocket`: 2 x 4 tubes, `Tubes` / `Tubes_bore`) on a
    pedestal: `Part_rocket` > `Mount_rocket` > `Muzzle_rocket` at the tube face. The last car carries a
    long-range SAM launcher: `Part_missile` > `Mount_missile` > a box of four canisters raised 35 degrees
    (`Launcher_tubes` / `Launcher_tubes_bore`, the missile slot's launch face) with `Muzzle_missile` at the
    face, and a flat radar panel on a mast on the same turntable. Both launchers stay clear of the ICBM
    when its `Erector` stands it up at the wagon's rear (it reaches back to y 12.0).
  * rail_supergun: two six-barrel CIWS (mb_phase8.ciws) on pedestals at the rear corners of the deck,
    `Part_mg` (left, x +2.55) and `Part_mg.001` (right) at y 12.1 holding `Mount_mg` / `Mount_mg.001`
    (`Muzzle_mg` / `Muzzle_mg.001`) 0.66 m up. They stand outside the sweep of the traversing upper
    carriage's rear loading platform (radius 11.14 m), their barrels at rest under its struts and clear of
    the deck railings when turned outboard; their blind arc is inboard, over the generator set.
  * landing_hovercraft: two more CIWS on the side-structure roofs abaft the cabin, `Part_mg` (left) /
    `Part_mg.001` (right) at y 3.7 on columns standing in the gap between the middle and rear turbine
    intakes (their rings clear the intakes' tops), with `Mount_mg` / `Mount_mg.001`; and two 140 mm rocket
    launchers (A-22 "Ogon" lineage: a 22-tube box on a trainable mount, tubes laid 15 degrees up, facing
    forward) on columns rising from the sloped bows ahead of the cabin: `Part_rocket` (left) /
    `Part_rocket.001` (right) > `Mount_rocket` / `Mount_rocket.001` > `Muzzle_rocket` / `Muzzle_rocket.001`
    at each tube face. The left box's tubes are `Tubes` / `Tubes_bore`, the right one's `Launcher_tubes` /
    `Launcher_tubes_bore`, so the game's launch-face search (by mesh name, model-wide) never merges the two.
  * fortress_bastion: a twin Kornet ATGM launcher on the roof behind the mortar pit, left of the centreline
    between the smokestacks: `Part_missile` > `Mount_missile` (yaw pivot on a short pedestal) > two 1.2 m,
    0.15 m tubes side by side (`Launch_tubes`, 0.56 m apart so the game fires them in turn) either side of a
    sight box, level at 6.8 m so they fire over the pit wall and the bridge roof; `Muzzle_missile` at the
    left tube's mouth.

Conventions are those of mb_bosses / mb_phase8: metres, +Z up, Blender -Y is the front and +X the model's
left, origin on the ground at the original footprint centre (the trains keep theirs: the new cars extend
them backwards). Each new breakable weapon is a `Part_<slot>` empty holding its `Mount_<slot>`; suffixed
pivots are authored as `Mount_mg__001` and renamed when the asset finishes (mb_phase2._suffixed). Touching
parts overlap or stand at least 1 cm apart.

Headless: blender --background --python Tools/blender/build_assets.py -- armored_train nuke_train
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mb_bosses  # noqa: E402
import mb_bosses2  # noqa: E402
import mb_phase8  # noqa: E402
from mb_bosses import _bogie, _plate_bolts, _underframe  # noqa: E402
from mb_phase2 import _suffixed, dotted  # noqa: E402
from mb_vehicles import ACROSS, FORWARD, R90, _frame, _tube_mouth  # noqa: E402

COUPLE = .76     # headstock face to the coupled car's headstock face: the buffer heads stand 1 cm apart


# ----------------------------------------------------------------------------- shared helpers
def _pv(a, name, loc, parent=None):
    return a.pivot(dotted(name), loc, dotted(parent) if parent else None)


def _flatcar(a, y0, y1, coupled_to, tail=False):
    """Two-axle armoured flatcar between the headstock faces y0 and y1, coupled at its front to the car whose
    rear headstock face is at `coupled_to` (a screw coupling bridges the two couplers): single-axle running
    gear (mb_bosses._bogie) under skirts, the train's underframe, buffers and steps, an armoured open-top
    body with low sides and end walls, a Team band along each side, a dark deck plate; tail lights if last.
    The deck (the body's floor) is at z 1.62, the side walls' tops at 2.22."""
    steel, armor = a.part('Steel', 'Steel'), a.part('Armor', 'Armor')
    steel.box((.1, .5, .08), loc=(0, (coupled_to + y0) / 2, 1.1), bevel=0)
    mid, L = (y0 + y1) / 2, y1 - y0
    axles = (y0 + .95, y1 - .95)
    for y in axles:
        _bogie(a, y, 1, 1.0, .46, 1.3)
    _underframe(a, y0, y1)
    trough = [(-1.6, 1.34), (1.6, 1.34), (1.62, 2.0), (1.42, 2.22), (1.3, 2.22), (1.3, 1.62), (-1.3, 1.62),
              (-1.3, 2.22), (-1.42, 2.22), (-1.62, 2.0)]
    a.part('Car_body', 'Armor').loft([[(x, y, z) for x, z in trough] for y in (y0 + .17, y1 - .17)], bevel=.04, seg=1)
    for y in (y0 + .3, y1 - .3):                                                             # end walls
        armor.box((2.62, .12, .42), loc=(0, y, 1.82), bevel=.02, seg=1)
    a.part('Car_deck', 'Undercarriage').box((2.56, L - 1.0, .04), loc=(0, mid, 1.63), bevel=0)
    band = a.part('Car_band', 'Team')
    for s in (-1, 1):
        band.box((.04, L - .7, .22), loc=(s * 1.62, mid, 1.78), bevel=.01, seg=1)
        for y in axles:
            armor.box((.06, 1.5, .8), loc=(s * 1.645, y, 1.1), bevel=.015, seg=1)                # skirts
            _plate_bolts(steel, s * 1.68, (y - .55, y, y + .55), 1.4, r=.028)
        if tail:
            a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.0, y1 - .225, 1.9), bevel=0)
    return mid


# ----------------------------------------------------------------------------- armored_train
def armored_train(a):
    """mb_bosses.armored_train with a mortar flatcar coupled behind the gun wagon carrying a twin 120 mm
    mortar on `Part_mortar` > `Mount_mortar` (`Muzzle_mortar` at the left tube's bore)."""
    _suffixed(a)
    mb_bosses.armored_train(a)
    y0 = 9.55 + COUPLE
    mid = _flatcar(a, y0, y0 + 4.45, 9.55, tail=True)
    # Mortar bomb crates at the car's ends, outside the turntable's sweep.
    crate = a.part('Mortar_crates', 'Crate')
    for s in (-1, 1):
        for e in (-1, 1):
            crate.box((.5, .3, .3), loc=(s * .75, mid + e * 1.6, 1.795), bevel=.03, seg=1)
    pm = _pv(a, 'Part_mortar', (0, mid, 1.62))
    a.part('Mortar_ring', 'Steel', pm).cyl(1.16, .1, loc=(0, 0, .03), seg=24, bevel=.02, bseg=1)   # z -.02 .. .08
    m = _pv(a, 'Mount_mortar', (0, 0, .1), 'Part_mortar')
    a.part('Mortar_turntable', 'Team', m).cyl(1.08, .095, loc=(0, 0, .0475), seg=24, bevel=.02, bseg=1)
    base = a.part('Mortar_baseplates', 'Armor', m)
    ammo = a.part('Mortar_ammo', 'Crate', m)
    for s in (-1, 1):
        ammo.box((.36, .3, .34), loc=(s * .72, .6, .26), bevel=.03, seg=1)
    pitch = math.radians(60)
    d = Vector((0, -math.cos(pitch), math.sin(pitch)))            # along the tubes: forward and up
    trot, lrot = (R90 - pitch, 0, 0), (-pitch, 0, 0)              # a cylinder along d; a box whose -Y is d
    L = 1.8
    breech = a.part('Mortar_breech', 'Armor', m)
    lip = a.part('Mortar_muzzle', 'Steel', m)
    bore = a.part('Mortar_bore', 'Charred', m)
    bands = a.part('Mortar_bands', 'Armor', m)
    muzzle = None
    for s in (1, -1):                                              # left (+X) tube first
        B = Vector((s * .24, .5, .25))                             # breech end on the tube's axis
        M = B + d * L                                              # the tube's front end
        a.part('Mortar_tube' if s > 0 else 'Mortar_tube_2', 'Steel', m).cyl(.075, L, loc=B + d * (L / 2), rot=trot,
                                                                           seg=14, bevel=.01, bseg=1)
        breech.cyl(.105, .24, loc=B + d * .04, rot=trot, seg=14, bevel=.02, bseg=1)
        base.box((.44, .5, .06), loc=(s * .24, .56, .12), bevel=.015, seg=1)
        lip.lathe([(.095, -.03), (.095, .06), (.06, .06), (.06, .02)], loc=M, rot=trot, seg=14)
        bore.cyl(.056, .02, loc=M + d * .02, rot=trot, seg=12, bevel=0)
        for f in (.3, .72):
            bands.cyl(.088, .07, loc=B + d * (L * f), rot=trot, seg=14, bevel=0)
        if s > 0:
            muzzle = M + d * .06                                   # the lip's open end
    cradle = a.part('Mortar_cradle', 'Team', m)
    C = Vector((0, .5, .25)) + d * (L * .45)
    cradle.box((.74, .34, .26), loc=C, rot=lrot, bevel=.03, seg=1)
    cradle.box((.74, .22, .22), loc=Vector((0, .5, .25)) + d * (L * .14), rot=lrot, bevel=.03, seg=1)
    n = Vector((0, math.sin(pitch), math.cos(pitch)))              # the cradle's up
    under = C - n * .12
    struts = a.part('Mortar_struts', 'Steel', m)
    for s in (-1, 1):
        struts.limb((s * .36, -.42, .09), (s * .36, under.y, under.z), .08, .08, bevel=0)
    struts.limb((0, -.62, .09), (0, under.y, under.z), .11, .11, bevel=0)                    # elevating ram
    a.part('Mortar_ram_foot', 'Armor', m).box((.8, .3, .1), loc=(0, -.5, .12), bevel=.02, seg=1)
    _pv(a, 'Muzzle_mortar', tuple(muzzle), 'Mount_mortar')


# ----------------------------------------------------------------------------- nuke_train
def _rocket_launcher(a, mount):
    """The armoured train's rocket launcher (mb_bosses.armored_train's `Mount_rocket`), copied onto `mount`:
    a base, a hinge block, a 2 x 4 box of 122 mm tubes raised 8 degrees with bands, `Muzzle_rocket` just
    ahead of its tube face (`Tubes_bore`, the rocket slot's launch face)."""
    rk = mount
    a.part('Launcher_base', 'Steel', rk).cyl(.68, .08, loc=(0, 0, .05), seg=16, bevel=.015, bseg=1)
    lbase = a.part('Launcher_armor', 'Armor', rk)
    lbase.box((.5, .6, .2), loc=(0, .3, .18), bevel=.03, seg=1)
    pitch, L, H, W = math.radians(8), 1.4, .42, 1.3
    lrot = (-pitch, 0, 0)
    hinge = Vector((0, .5, .27))
    turn = _frame((0, 0, 0), lrot).to_3x3()
    centre = hinge - turn @ Vector((0, L / 2, -H / 2))
    pod = _frame(centre, lrot)
    a.part('Rocket_box', 'Team', rk).box((W, L, H), loc=centre, rot=lrot, bevel=.04)
    band = a.part('Pod_bands', 'Armor', rk)
    for yy in (-L / 2 + .1, L / 2 - .1):
        band.box((W + .05, .1, H + .05), loc=pod @ Vector((0, yy, 0)), rot=lrot, bevel=.012, seg=1)
    a.part('Launcher_steel', 'Steel', rk).cyl(.07, W + .1, loc=hinge, rot=ACROSS, seg=8, bevel=0)
    for row in (-.1, .1):
        for col in (-.45, -.15, .15, .45):
            _tube_mouth(a, rk, pod @ _frame((col, -L / 2, row), FORWARD), .085, protrude=.04, seg=8)
    a.pivot('Muzzle_rocket', tuple(pod @ Vector((0, -L / 2 - .05, 0))), rk)


def _sam_launcher(a, mount):
    """Long-range SAM launcher on `mount`: a turntable, a yoke, a box of four big canisters raised 35 degrees on
    a hinge at its rear with an elevating ram (`Launcher_tubes` mouths, `Launcher_tubes_bore` the missile
    slot's launch face, `Muzzle_missile` just ahead of it), and a flat radar panel on a mast beside the box."""
    m = mount
    a.part('Sam_base', 'Steel', m).cyl(1.05, .1, loc=(0, 0, .05), seg=20, bevel=.02, bseg=1)
    yoke = a.part('Sam_yoke', 'Armor', m)
    for s in (-1, 1):
        yoke.box((.12, .6, .55), loc=(s * .64, .45, .37), bevel=.02, seg=1)
    yoke.box((.9, .5, .2), loc=(0, .55, .19), bevel=.03, seg=1)
    pitch, L, H, W = math.radians(35), 2.5, .95, 1.1
    lrot = (-pitch, 0, 0)
    hinge = Vector((0, .6, .55))
    turn = _frame((0, 0, 0), lrot).to_3x3()
    centre = hinge - turn @ Vector((0, L / 2, -H / 2))             # the hinge along the box's rear bottom edge
    box = _frame(centre, lrot)
    a.part('Sam_box', 'Team', m).box((W, L, H), loc=centre, rot=lrot, bevel=.05, seg=1)
    bands = a.part('Sam_bands', 'Armor', m)
    for yy in (-L / 2 + .15, 0, L / 2 - .15):
        bands.box((W + .04, .1, H + .04), loc=box @ Vector((0, yy, 0)), rot=lrot, bevel=.015, seg=1)
    sst = a.part('Sam_steel', 'Steel', m)
    sst.cyl(.08, 1.44, loc=hinge, rot=ACROSS, seg=10, bevel=0)                                # hinge pin
    sst.limb((0, -.35, .08), tuple(box @ Vector((0, .1, -H / 2 + .03))), .14, .14, bevel=0)   # elevating ram
    for cx in (-.27, .27):
        for cz in (-.22, .22):
            _tube_mouth(a, m, box @ _frame((cx, -L / 2, cz), FORWARD), .2, protrude=.06, seg=12, name='Launcher_tubes')
    # Flat radar panel on a mast beside the box (right side), tilted back 15 degrees.
    sst.box((.2, .2, .1), loc=(-.95, .3, .1), bevel=.01, seg=1)
    sst.cyl(.06, 2.2, loc=(-.95, .3, 1.2), seg=8, bevel=0)                                   # z .1 .. 2.3
    tilt = (-.26, 0, 0)
    panel = _frame((-.95, .3, 2.45), tilt)
    a.part('Sam_radar', 'Armor', m).box((.6, .08, .5), loc=panel.to_translation(), rot=tilt, bevel=.015, seg=1)
    a.part('Sam_radar_face', 'Undercarriage', m).box((.52, .02, .42), loc=panel @ Vector((0, -.045, 0)), rot=tilt,
                                                     bevel=0)
    a.pivot('Muzzle_missile', tuple(box @ Vector((0, -L / 2 - .14, 0))), m)


def nuke_train(a):
    """mb_bosses2.nuke_train with a rocket car (`Part_rocket` > `Mount_rocket` > `Muzzle_rocket`) and a SAM car
    (`Part_missile` > `Mount_missile` > `Muzzle_missile`) coupled behind the missile wagon."""
    _suffixed(a)
    mb_bosses2.nuke_train(a)
    y0 = 10.62 + COUPLE
    mid = _flatcar(a, y0, y0 + 4.05, 10.62)
    pr = _pv(a, 'Part_rocket', (0, mid, 1.62))
    a.part('Rocket_pedestal', 'Armor', pr).cyl(.55, .65, loc=(0, 0, .305), seg=18, bevel=.03, bseg=1)  # z -.02 .. .63
    a.part('Rocket_pedestal_band', 'SafetyStripe', pr).cyl(.565, .1, loc=(0, 0, .45), seg=18, bevel=0)
    _rocket_launcher(a, _pv(a, 'Mount_rocket', (0, 0, .64), 'Part_rocket'))
    y2 = y0 + 4.05 + COUPLE
    mid = _flatcar(a, y2, y2 + 4.05, y0 + 4.05, tail=True)
    pm = _pv(a, 'Part_missile', (0, mid, 1.62))
    a.part('Sam_pedestal', 'Armor', pm).cyl(.62, .32, loc=(0, 0, .14), seg=20, bevel=.03, bseg=1)       # z -.02 .. .3
    _sam_launcher(a, _pv(a, 'Mount_missile', (0, 0, .32), 'Part_missile'))


# ----------------------------------------------------------------------------- rail_supergun
def rail_supergun(a):
    """mb_phase8.rail_supergun with a CIWS on a pedestal at each rear corner of the deck: `Part_mg` (left) and
    `Part_mg.001` (right) holding `Mount_mg` / `Mount_mg.001`."""
    mb_phase8.rail_supergun(a)
    for name, x in (('Part_mg', 2.55), ('Part_mg.001', -2.55)):
        pg = _pv(a, name, (x, 12.1, mb_phase8.SG_DECK))
        tag = name[5:].replace('.', '_')
        a.part(f'Pedestal_{tag}', 'Armor', pg).cyl(.78, .68, loc=(0, 0, .32), seg=18, bevel=.04, bseg=1)  # to .66
        a.part(f'Pedestal_band_{tag}', 'SafetyStripe', pg).cyl(.8, .1, loc=(0, 0, .45), seg=18, bevel=0)
        mb_phase8.ciws(a, name.replace('Part_', 'Mount_'), (0, 0, .66), parent=name)


# ----------------------------------------------------------------------------- landing_hovercraft
def _ogon(a, part, tubes):
    """140 mm rocket launcher (A-22 "Ogon" lineage) on its own mount under `part`: a base, trunnion cheeks and
    a Team box of 22 tubes in four staggered rows (6, 5, 6, 5) laid 15 degrees up with bands; the tube
    mouths are the parts `tubes` / `<tubes>_bore`; `Muzzle_rocket*` just ahead of the tube face."""
    mount = part.replace('Part_', 'Mount_')
    tag = part[5:].replace('.', '_')
    m = _pv(a, mount, (0, 0, .02), part)
    a.part(f'Launcher_base_{tag}', 'Steel', m).cyl(.72, .08, loc=(0, 0, .04), seg=16, bevel=.015, bseg=1)
    cheeks = a.part(f'Launcher_cheeks_{tag}', 'Armor', m)
    for s in (-1, 1):
        cheeks.box((.1, .5, .62), loc=(s * .62, 0, .385), bevel=.02, seg=1)
    pitch, L, H, W = math.radians(15), 1.3, .72, 1.1
    lrot = (-pitch, 0, 0)
    centre = Vector((0, 0, .65))                                   # on the trunnion
    box = _frame(centre, lrot)
    a.part(f'Rocket_box_{tag}', 'Team', m).box((W, L, H), loc=centre, rot=lrot, bevel=.04, seg=1)
    band = a.part(f'Launcher_bands_{tag}', 'Armor', m)
    for yy in (-L / 2 + .1, L / 2 - .1):
        band.box((W + .05, .1, H + .05), loc=box @ Vector((0, yy, 0)), rot=lrot, bevel=.012, seg=1)
    a.part(f'Launcher_pin_{tag}', 'Steel', m).cyl(.06, 1.36, loc=centre, rot=ACROSS, seg=8, bevel=0)
    pitch_x, pitch_z = .165, .143
    for row, count in enumerate((6, 5, 6, 5)):
        cz = (row - 1.5) * pitch_z
        for k in range(count):
            cx = (k - (count - 1) / 2) * pitch_x
            _tube_mouth(a, m, box @ _frame((cx, -L / 2, cz), FORWARD), .07, protrude=.04, seg=8, name=tubes)
    _pv(a, mount.replace('Mount_', 'Muzzle_'), tuple(box @ Vector((0, -L / 2 - .05, 0))), mount)


def landing_hovercraft(a):
    """mb_phase8.landing_hovercraft with a CIWS on a column in each side structure's intake gap (`Part_mg` left,
    `Part_mg.001` right) and a 22-tube rocket launcher on a column on each sloped bow (`Part_rocket` left,
    `Part_rocket.001` right)."""
    mb_phase8.landing_hovercraft(a)
    col = a.part('Weapon_columns', 'Armor')
    steel = a.part('Steel', 'Steel')
    for name, x in (('Part_mg', 5.3), ('Part_mg.001', -5.3)):
        col.cyl(.28, .47, loc=(x, 3.7, 4.485), seg=14, bevel=.02, bseg=1)                       # z 4.25 .. 4.72
        col.cyl(.3, .1, loc=(x, 3.7, 4.75), r2=.62, seg=18, bevel=0)                             # flare to 4.8
        _pv(a, name, (x, 3.7, 4.8))
        mb_phase8.ciws(a, name.replace('Part_', 'Mount_'), (0, 0, 0), parent=name)
    # Rocket launchers ahead of the cabin: a bracket on the sloped bow, a column, a collar at the top.
    theta = math.atan2(1.65, 1.0)                                  # the bow slope: (y -11.6, z 2.6) .. (-10.6, 4.25)
    normal = Vector((0, -math.sin(theta), math.cos(theta)))
    for name, x, tubes in (('Part_rocket', 5.3, 'Tubes'), ('Part_rocket.001', -5.3, 'Launcher_tubes')):
        foot = Vector((x, -11.2, 2.6 + .4 * 1.65)) + normal * .03
        col.box((.9, .8, .08), loc=foot, rot=(theta, 0, 0), bevel=.02, seg=1)
        col.cyl(.24, 1.65, loc=(x, -11.2, 3.625), seg=14, bevel=.02, bseg=1)                     # z 2.8 .. 4.45
        steel.cyl(.34, .08, loc=(x, -11.2, 4.41), seg=16, bevel=.015, bseg=1)
        _pv(a, name, (x, -11.2, 4.45))
        _ogon(a, name, tubes)


# ----------------------------------------------------------------------------- fortress_bastion
def fortress_bastion(a):
    """mb_bosses2.fortress_bastion with a twin Kornet ATGM launcher on the roof behind the mortar pit:
    `Part_missile` > `Mount_missile` > `Muzzle_missile` at the left tube's mouth."""
    _suffixed(a)
    mb_bosses2.fortress_bastion(a)
    pm = _pv(a, 'Part_missile', (.85, 3.75, 5.5))
    ped = a.part('Atgm_pedestal', 'Armor', pm)
    a.part('Atgm_flange', 'Steel', pm).cyl(.34, .06, loc=(0, 0, .02), seg=14, bevel=.01, bseg=1)   # z -.01 .. .05
    ped.cyl(.2, .5, loc=(0, 0, .24), seg=12, bevel=.02, bseg=1)                                    # to .49
    m = _pv(a, 'Mount_missile', (0, 0, .5), 'Part_missile')
    a.part('Atgm_turntable', 'Steel', m).cyl(.3, .08, loc=(0, 0, .04), seg=14, bevel=.015, bseg=1)
    arm = a.part('Atgm_armor', 'Armor', m)
    arm.box((.3, .3, .5), loc=(0, .05, .32), bevel=.03, seg=1)                                     # yoke
    a.part('Atgm_cradle', 'Team', m).box((.74, .44, .12), loc=(0, -.05, .62), bevel=.02, seg=1)     # z .56 .. .68
    tz = .8
    tubes = a.part('Launch_tubes', 'Team', m)
    clamps = a.part('Atgm_clamps', 'Armor', m)
    for s in (1, -1):
        x = s * .28
        tubes.cyl(.075, 1.2, loc=(x, -.1, tz), rot=FORWARD, seg=12, bevel=.01, bseg=1)             # y -.7 .. .5
        _tube_mouth(a, m, _frame((x, -.7, tz), FORWARD), .088, protrude=.05, seg=12, name='Launch_tubes')
        for y in (.3, -.35):
            clamps.cyl(.09, .06, loc=(x, y, tz), rot=FORWARD, seg=12, bevel=0)
        clamps.box((.1, .12, .1), loc=(s * .22, -.05, .7), bevel=.01, seg=1)                     # tube saddles
    arm.box((.3, .4, .3), loc=(0, -.2, .82), bevel=.03, seg=1)                                     # sight box
    a.part('Atgm_sight_glass', 'Glass', m).box((.16, .02, .12), loc=(0, -.405, .86), bevel=0)
    a.part('Atgm_sight_top', 'Steel', m).box((.12, .2, .06), loc=(0, -.1, .995), bevel=.01, seg=1)
    _pv(a, 'Muzzle_missile', (.28, -.75, tz), 'Mount_missile')


BUILDERS = {
    'armored_train': (armored_train, dict(ao_distance=.8, grime_height=.7)),
    'nuke_train': (nuke_train, dict(ao_distance=.8, grime_height=.7)),
    'rail_supergun': (rail_supergun, dict(ao_distance=1.4, grime_height=.8)),
    'landing_hovercraft': (landing_hovercraft, dict(ao_distance=1.0, grime_height=.8)),
    'fortress_bastion': (fortress_bastion, dict(ao_distance=1.1, grime_height=1.0)),
}
