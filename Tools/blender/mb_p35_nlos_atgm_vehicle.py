"""Prompt 35 wave 7 (lane C): the Spike NLOS launcher truck rebuilt from scratch (spec: Tools/blender/specs/nlos_atgm_vehicle.json).

A Spike NLOS launcher on a Tatra-pattern armoured 6x6 (no sheet row; the old builders drew a Spike NLOS truck; the
def's modelSize 6.0 x 2.1 x 2.6 m): the armoured cab-over crew cab with its steep windscreen, side windows, roof
hatch, mirrors, lamps and bumper, the chassis frame with the front axle and the rear tandem on lugged tyres, the
mudguards; on the bed the launcher turntable (`Turret`) with its elevating arm and the four-cell canister box raised
for firing (`Muzzle_missile` at the ready cell), the datalink mast with its optic head, a rack of reload canisters,
side bins, the fuel tank and the exhaust stack; the 12.7 mm on its ring over the cab roof hatch (the def's free
`hmg_selfdef_15`).

Runtime nodes kept: `Turret`, `Muzzle_missile`, `Mount_mg`, `Muzzle_mg`, `Hatches`, `Point_exhaust`, `Point_fire`
(the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .44
AX = (-1.95, 1.0, 2.05)
TRACK = .8
DECK = 1.2


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (-3.0, [(0, .95), (.98, .95), (.98, 1.35), (.82, 1.88), (.7, 1.97), (0, 1.98)]),
        (-2.55, [(0, .9), (1.02, .9), (1.02, 1.4), (.84, 2.08), (.7, 2.2), (0, 2.21)]),
        (-1.35, [(0, .9), (1.02, .9), (1.02, 1.4), (.84, 2.08), (.7, 2.2), (0, 2.21)]),
    ])
    # The steep two-pane windscreen, side windows, the cab doors' outlines, the roof hatch and the gun ring.
    for s in (-1, 1):
        x0, x1 = s * .05, s * .9
        K.windscreen(a, [(min(x0, x1), -2.99, 1.45), (max(x0, x1), -2.99, 1.45), (max(x0, x1), -2.62, 2.08),
                         (min(x0, x1), -2.62, 2.08)], frame_mat='Team', wipers=1)
        a.part('Windows', 'Glass').box((.02, .55, .4), loc=(s * .95, -2.0, 1.78), rot=(0, s * .27, 0), bevel=0)
        door = a.part('Doors', 'Armor')
        K.plate(door, (.03, .8, 1.0), loc=(s * 1.03, -2.0, 1.5), chamfer=.008)
        K.handle(a.part('Kit_steel', 'Steel'), (s * 1.05, -1.75, 1.45), (s * 1.05, -1.62, 1.45), (s, 0, 0), h=.035)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .95, -2.75, 1.75), s, arm=.08)
        a.part('Steps', 'Steel').box((.25, .4, .04), loc=(s * .9, -2.0, .72), bevel=0)
        a.part('Team_band', 'Team').box((.012, 1.0, .08), loc=(s * 1.035, -2.0, 1.1), bevel=0)
    # The front: bumper with lamps, grille, tow hooks, the sun visor.
    bp = a.part('Bumper', 'Armor')
    K.chamfer_box(bp, (2.0, .2, .28), loc=(0, -3.08, .82), c=.03)
    K.grille(a, (0, -3.01, 1.22), 1.3, .35, facing=(0, -1, 0), slats=6, frame_mat='Team')
    for s in (-1, 1):
        K.lamp(a, (s * .75, -3.16, .85), (0, -1, 0), r=.07, guard=False)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .4, -3.18, .7), facing=(0, -1, 0), size=.07)
    a.part('Visor', 'Team').box((1.85, .2, .03), loc=(0, -3.0, 2.12), rot=(-.15, 0, 0), bevel=0)
    k.ring(a.part('Gun_ring', 'Armor'), [(.36, 0), (.42, 0), (.42, .1), (.38, .12)], loc=(-.35, -1.85, 2.21), seg=14,
           worn=(2,))
    k.lathe(a.part('Hatches', 'Armor'), [(0, .05), (.3, .045), (.34, .02), (.34, 0)], loc=(.4, -2.2, 2.21), seg=12)
    K.pintle_mg(a, None, (-.35, -1.85, 2.28), post=.06, length=1.0)


def _chassis(a):
    ch = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        ch.box((.12, 5.6, .24), loc=(s * .45, -.1, .82), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AX:
        K.axle(ax, y, WR, TRACK - .15, r=.08)
        for s in (-1, 1):
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .38, s, lugs=8, seg=11, nuts=4)
            ax.limb((s * .45, y - .35, .78), (s * .62, y, WR + .08), .045, .045, bevel=0)
    fl = a.part('Fender_flares', 'Armor')
    for y in AX:
        for s in (-1, 1):
            fl.box((.42, 1.05, .04), loc=(s * .85, y, WR * 2 + .1), bevel=0)
            fl.box((.04, 1.05, .2), loc=(s * 1.05, y, WR * 2 + .0), bevel=0)
    # The bed: a flat deck, side rails, the fuel tank, bins, the exhaust stack behind the cab.
    bed = a.part('Body', 'Team')
    K.chamfer_box(bed, (2.0, 4.2, .14), loc=(0, .85, DECK - .07), c=.02)
    rl = a.part('Racks', 'Steel')
    for s in (-1, 1):
        rl.tube([(s * .98, -1.2, DECK), (s * .98, -1.2, DECK + .35), (s * .98, 2.9, DECK + .35), (s * .98, 2.9, DECK)],
                .02, seg=4)
    k.block(a.part('Fuel_tank', 'Armor'), (.3, .9, .45), loc=(-.85, -.6, .75), chamfer=.04)
    C.stowage_box(a, (.3, .8, .4), (.85, -.6, .55), mat='Armor', latches=2)
    K.exhaust(a, (.82, -1.3, 1.3), r=.06, length=.75, direction=(0, 0, 1), muffler=True, cap=True)
    a.pivot('Point_exhaust', (.82, -1.3, 2.1))
    a.pivot('Point_fire', (0, .9, DECK + .4))
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .1), loc=(s * .85, 2.96, DECK - .05), bevel=0)


def _launcher(a):
    t = a.pivot('Turret', (0, 1.75, DECK))
    k.lathe(a.part('Turntable', 'Armor', t), [(.68, 0), (.68, .08), (.55, .14), (0, .14)], seg=16, worn=(1,))
    # The elevating arm: trunnion posts, a pivot at the rear, the canister box raised 30 degrees.
    arm = a.part('Launcher_arm', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(arm, (.12, .5, .4), loc=(s * .55, .35, .32), c=.02)
    k.lathe(arm, [(.06, -.62), (.06, .62)], loc=(0, .45, .45), rot=(0, R90, 0), seg=8)
    a.part('Rams', 'Steel', t).limb((0, -.3, .14), (0, -.35, .7), .05, .04, bevel=0)
    pitch = math.radians(24)
    c, sn = math.cos(pitch), math.sin(pitch)
    box_c = (0, .45 - .7 * c, .45 + .7 * sn)
    rot = (pitch, 0, 0)
    lb = a.part('Launcher', 'Team', t)
    K.chamfer_box(lb, (1.0, 1.7, .7), loc=box_c, rot=rot, c=.04)
    cells = a.part('Launch_cells', 'Undercarriage', t)
    lids = a.part('Cell_lids', 'Armor', t)
    fy, fz = box_c[1] - .86 * c, box_c[2] + .86 * sn
    for i, (dx, dz) in enumerate(((-.23, -.16), (.23, -.16), (-.23, .16), (.23, .16))):
        p = (dx, fy - dz * sn, fz + dz * c)
        cells.box((.36, .02, .26), loc=p, rot=rot, bevel=0)
        if i == 3:
            lids.box((.36, .03, .26), loc=(dx, p[1] - .12, p[2] + .18), rot=(pitch + 1.2, 0, 0), bevel=0)
    a.pivot('Muzzle_missile', (.23, fy - .16 * sn - .05, fz + .16 * c), t)
    st = a.part('Kit_steel', 'Steel', t)
    for dz in (-.36, .36):
        st.box((1.04, .06, .04), loc=(0, box_c[1] - dz * sn * 0 + .0, box_c[2]), rot=rot, bevel=0)
    a.part('Team_band', 'Team', t).box((1.02, .9, .02), loc=(0, box_c[1] + .1 * c, box_c[2] + .36), rot=rot, bevel=0)


def _mast_and_reloads(a):
    ms = a.part('Mast', 'Steel')
    k.lathe(ms, [(.08, 0), (.08, .06), (.045, .1), (.04, .85), (0, .85)], loc=(.75, .0, DECK), seg=8, worn=(2,))
    sh = a.part('Sensor_head', 'Armor')
    K.chamfer_box(sh, (.26, .3, .24), loc=(.75, .0, DECK + .95), c=.04)
    a.part('Glass', 'Glass').box((.18, .01, .1), loc=(.75, -.155, DECK + .97), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.75, .1, DECK + 1.07), h=.2, r=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.85, -1.6, 2.21), h=.35, r=.02)
    # Reload canisters lying in a rack on the bed's front half.
    rc = a.part('Reload_canisters', 'Team')
    for x in (-.55, -.15):
        K.chamfer_box(rc, (.36, 1.4, .62), loc=(x, -.3, DECK + .31), c=.03)
        rc.box((.37, .02, .58), loc=(x, -.3, DECK + .31), bevel=0)
    a.part('Kit_straps', 'Steel').box((.85, .05, .7), loc=(-.35, -.3, DECK + .33), bevel=0)


def nlos_atgm_vehicle(a, detail=False):
    """The Spike NLOS launcher truck: see the module docstring."""
    _cab(a)
    _chassis(a)
    _launcher(a)
    _mast_and_reloads(a)
    K.dust(a, (0, 0, .3), radius=3.2, k=.14)
    k.clean(a)


BUILDERS = {
    'nlos_atgm_vehicle': (nlos_atgm_vehicle, dict(ao_distance=.5, grime_height=.6)),
}
