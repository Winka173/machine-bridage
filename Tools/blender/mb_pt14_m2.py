"""Play-test 14 model wave M2 (lane models): the two boss trains get more cars, Ixion more guns and launchers, Harpy stub
wings that carry its weapons, Daedalus redrawn at 5 x the boss budget (owner, Docs/prompts/playtest14_vi.txt: "2 boss
tau lua: deu them 2-4 toa", "ixion: them sung / ten lua, khoang 4-5 vu khi", "harpy ... nen cho no doi canh nhu attack
helicopter va gan vao o do", Daedalus 500 %; DECISIONS "Play-test 14 model wave M2 (lane models)").

- armored_train (Juggernaut): the wave 8 train (locomotive, gun wagon, mortar flatcar) kept as built, three cars added:
  the armoured control platform pushed ahead of the locomotive (rail-repair load, a hand derrick, the obstacle
  deflector), the command car behind the mortar flatcar (the observation tower with the stereoscopic rangefinder that
  lays the 152 mm, the bedstead radio antenna) and the rear control platform (cable drums, a spare wheelset, sandbags,
  the tail lamps). Real reference: the Soviet BP-43 armoured train (control platforms at both ends, the staff car).
- nuke_train (Nemesis): the wave 12 train kept, two cars added at the tail as in the BZhRK "Molodets" (the RT-23 rail
  ICBM train ran with a command module and three diesels): the command and communications car disguised as a
  refrigerator wagon (radomes, the folded telescopic mast, A/C units) and the pusher diesel with its cab at the tail.
- Both trains are re-centred on the middle of their length (the Sim holds a train on its rail as a span of `length`
  centred on its position), so every part's place moves along the length (CHANGES).
- ixion: the P35 truck kept, four weapons added (models + data): a 2A42 30 mm in a low remote turret on the canopy
  (Mount_gun), two 9M133 Kornet-EM twin launchers on the roof edges (Mount_missile / .001) and a 12-tube 122 mm
  BM-21V "Grad-V" pack on the rear roof (Mount_rocket).
- mega_gunship (Harpy) and daedalus: redrawn from scratch (their own functions below).

Every round leaves from a barrel, tube or rail with its Muzzle_* point at the mouth (owner 03/10). Metres, +Z up,
-Y front, +X left. Built from frontier_kit / mb_kit27 / mb_kit35 primitives; the trains and Ixion call their own
previous builders first (their parts are kept) and only add.
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_ixion as IX
import mb_p35_nuke_train as NT
import mb_p35_wave8_bosses as W8

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= helpers
def _drop(a, name, mat, parent=None):
    """Remove a part the previous builder made (its tail lamps, now in the middle of the longer train)."""
    key = (name, mat, parent)
    if key in a.shapes:
        a.shapes[key].bm.free()
        del a.shapes[key]
        a.order.remove(key)


def _span_y(a):
    """The model's extent along Y (world), over every part's vertices."""
    lo, hi = math.inf, -math.inf
    for (name, mat, parent), shape in a.shapes.items():
        if not shape.bm.verts:
            continue
        w = a._world(parent)
        for v in shape.bm.verts:
            y = (w @ v.co).y
            lo, hi = min(lo, y), max(hi, y)
    return lo, hi


def _recentre(a):
    """Move the whole model along Y after its finish so its length is centred on the origin (the Sim's rail span is
    centred on the train's position). Returns the shift (m, Blender Y) through a.recentred."""
    lo, hi = _span_y(a)
    dy = (lo + hi) / 2
    a.recentred = dy
    print(f'[pt14-m2] {a.name} span {lo:.3f} .. {hi:.3f}, recentred by {dy:.3f}')
    original = a.finish

    def finish():
        out = original()
        for o in a.collection.objects:
            if o.parent is None:
                o.location.y -= dy
        return out
    a.finish = finish


def _studs(part, p0, p1, pitch=.2, size=.045):
    p0, p1 = Vector(p0), Vector(p1)
    n = max(1, int((p1 - p0).length / pitch))
    for i in range(n + 1):
        part.box((size, size, size), loc=tuple(p0.lerp(p1, i / n)), bevel=0)


def _rail_section(part, y0, y1, x, z):
    """A spare rail lying on its foot along Y: foot, web and head (an R65 rail at the boss's scale)."""
    L, yc = y1 - y0, (y0 + y1) / 2
    part.box((.15, L, .025), loc=(x, yc, z + .0125), bevel=0)
    part.box((.035, L, .11), loc=(x, yc, z + .08), bevel=0)
    part.box((.08, L, .05), loc=(x, yc, z + .16), bevel=0)


def _sleepers(a, x, y, z, rows, layers, crosswise=True, part='Sleepers'):
    """A stack of timber sleepers (2.5 x 0.25 x 0.16 m), `rows` per layer, `layers` high, laid across the car."""
    s = a.part(part, 'Wood')
    for j in range(layers):
        for i in range(rows):
            yy = y + (i - (rows - 1) / 2) * .29 + (j % 2) * .03
            s.box((2.3 if crosswise else .25, .25 if crosswise else 2.3, .155), loc=(x, yy, z + .08 + j * .16), bevel=0)


def _cable_drum(a, loc, r=.55, w=.7, axis_x=True, mat='Wood'):
    """A cable drum standing on its rims (two flanges, the core with the cable wound on it, the axle)."""
    rot = (0, R90, 0) if axis_x else K.FORWARD
    x, y, z = loc
    k.lathe(a.part('Cable_drums', mat), [(r, -w / 2), (r, -w / 2 + .05), (r * .55, -w / 2 + .05),
                                         (r * .55, w / 2 - .05), (r, w / 2 - .05), (r, w / 2)],
            loc=(x, y, z + r), rot=rot, seg=16)
    k.lathe(a.part('Drum_cable', 'Rubber'), [(r * .55, -w / 2 + .06), (r * .82, -w / 2 + .08), (r * .84, 0),
                                             (r * .82, w / 2 - .08), (r * .55, w / 2 - .06)],
            loc=(x, y, z + r), rot=rot, seg=16)
    a.part('Drum_axles', 'Steel').cyl(.06, w + .2, loc=(x, y, z + r), rot=rot, seg=8, bevel=0)


# ============================================================================= armored_train (Juggernaut)
JT_FRONT = (-16.8, -10.4)     # control platform ahead of the locomotive (-9.4)
JT_CMD = (15.7, 24.3)         # command car behind the mortar flatcar (14.76)
JT_TAIL = (25.25, 31.25)      # rear control platform
JT_DECK = 1.47


def _jt_flat_sides(a, y0, y1, ends=(True, True)):
    """A control platform's deck (riveted plate over timber), low armoured sides with loopholes, end walls."""
    mid, L = (y0 + y1) / 2, y1 - y0
    a.part('Deck', 'Armor').box((2.6, L, .1), loc=(0, mid, 1.42), bevel=0)
    pl = a.part('Deck_planks', 'Wood')
    for i in range(int((L - .6) / .45)):
        pl.box((2.3, .38, .012), loc=(0, y0 + .5 + i * .45, JT_DECK + .006), bevel=0)
    body = a.part('Car_body', 'Team')
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        k.block(body, (.1, L - .2, .62), loc=(s * 1.28, mid, JT_DECK + .31), chamfer=.02)
        _studs(rv, (s * 1.335, y0 + .2, JT_DECK + .55), (s * 1.335, y1 - .2, JT_DECK + .55), pitch=.24)
        _studs(rv, (s * 1.335, y0 + .2, JT_DECK + .08), (s * 1.335, y1 - .2, JT_DECK + .08), pitch=.24)
        for i in range(int(L / 1.4)):
            y = y0 + .8 + i * 1.4
            a.part('Loopholes', 'Charred').box((.02, .16, .08), loc=(s * 1.335, y, JT_DECK + .4), bevel=0)
            a.part('Loophole_covers', 'Armor').box((.03, .22, .04), loc=(s * 1.345, y, JT_DECK + .49), bevel=0)
        a.part('Car_band', 'Team').box((.03, L - .6, .12), loc=(s * 1.62, mid, 1.22), bevel=0)
    for y, on in ((y0 + .05, ends[0]), (y1 - .05, ends[1])):
        if on:
            k.block(body, (2.66, .1, .62), loc=(0, y, JT_DECK + .31), chamfer=.02)
    # Bogie skirts, end handles and steps (the wave 8 kit's pattern for the new cars).
    for s in (-1, 1):
        for yb in (y0 + 1.5, y1 - 1.5):
            K.armour_plate(a, a.part('Skirt_plates', 'Armor'), (.55, 2.1, .05), (s * 1.42, yb, .78),
                           rot=(0, s * R90, 0), rivet=.5)
        for y in (y0 + .15, y1 - .15):
            K.handle(a.part('Kit_handles', 'Steel'), (s * 1.5, y, 1.5), (s * 1.5, y, 2.05), (s, 0, 0), h=.06)
            a.part('Steps', 'Steel').box((.3, .25, .03), loc=(s * 1.45, y, .62), bevel=0)


def _jt_front_platform(a):
    """The control platform pushed ahead of the locomotive: it takes a mine or a sabotaged rail first. The obstacle
    deflector on its nose, the hazard board, two marker lamps on posts, the sandbag breastwork at the front, the
    rail-repair load (sleepers, spare rails, a track jack, a spike keg, tool chests) and the hand derrick that lifts
    them."""
    y0, y1 = JT_FRONT
    W8._train_car_base(a, y0, y1, (y0 + 1.5, y1 - 1.5))
    _jt_flat_sides(a, y0, y1)
    # The obstacle deflector: a low V of plate below the headstock, chevrons on it.
    arm = a.part('Deflector', 'Armor')
    k.sharp_loft(arm, [[(-.3, y0 - .62, .2), (.3, y0 - .62, .2), (1.35, y0 - .32, .2), (1.45, y0 - .1, .2),
                        (-1.45, y0 - .1, .2), (-1.35, y0 - .32, .2)],
                       [(-.25, y0 - .42, .92), (.25, y0 - .42, .92), (1.25, y0 - .22, .92), (1.38, y0 - .08, .92),
                        (-1.38, y0 - .08, .92), (-1.25, y0 - .22, .92)]], chamfer=.03)
    chev = a.part('Chevrons', 'SafetyStripe')
    for s in (-1, 1):
        for i in range(3):
            chev.box((.17, .03, .5), loc=(s * (.42 + i * .32), y0 - .52 + i * .1, .58), rot=(0, s * .5, -s * .3),
                     bevel=0)
    # The hazard board on the front wall, the marker lamps on their posts at the corners.
    a.part('Hazard_board', 'Hazard').box((1.6, .03, .3), loc=(0, y0 - .02, JT_DECK + .35), bevel=0)
    for i in range(4):
        a.part('Hazard_bars', 'Charred').box((.14, .035, .32), loc=(-.6 + i * .4, y0 - .03, JT_DECK + .35),
                                             rot=(0, .6, 0), bevel=0)
    for s in (-1, 1):
        a.part('Lamp_posts', 'Steel').cyl(.035, 1.0, loc=(s * 1.2, y0 + .25, JT_DECK + .9), seg=6, bevel=0)
        K.lamp(a, (s * 1.2, y0 + .18, JT_DECK + 1.38), (0, -1, 0), r=.11, guard=True)
    # Sandbag breastwork across the front, short returns along the sides.
    K.sandbag_run(a, [(-1.05, y0 + .45, JT_DECK), (1.05, y0 + .45, JT_DECK)], courses=3, bag=(.5, .3, .16),
                  part='Sandbags', seed=31, lean=True)
    for s in (-1, 1):
        K.sandbag_run(a, [(s * 1.05, y0 + .8, JT_DECK), (s * 1.05, y0 + 1.6, JT_DECK)], courses=2,
                      bag=(.5, .3, .16), part='Sandbags', seed=33 + s, lean=True)
    # The rail-repair load: two stacks of sleepers, the spare rails on bearers, the jack, the spike keg, chests.
    _sleepers(a, 0, y0 + 2.6, JT_DECK, 4, 3)
    _sleepers(a, 0, y0 + 3.85, JT_DECK, 3, 2)
    bear = a.part('Rail_bearers', 'Wood')
    for y in (y0 + 4.55, y1 - .55):
        bear.box((1.5, .14, .1), loc=(-.35, y, JT_DECK + .05), bevel=0)
    rails = a.part('Spare_rails', 'Steel')
    for i, x in enumerate((-.95, -.65, -.35, -.05)):
        _rail_section(rails, y0 + 4.3, y1 - .3, x, JT_DECK + .1 + (i % 2) * .0)
    k.lathe(a.part('Track_jack', 'BarrelRed'), [(.14, 0), (.14, .35), (.09, .4), (.06, .62), (.1, .64), (.1, .7),
                                                (0, .7)], loc=(.85, y0 + 4.6, JT_DECK), seg=10, worn=(1,))
    a.part('Track_jack', 'Steel').limb((.85, y0 + 4.6, JT_DECK + .45), (.85, y0 + 5.3, JT_DECK + .55), .04, .04,
                                       bevel=0)
    k.lathe(a.part('Spike_keg', 'Wood'), [(.2, 0), (.24, .25), (.2, .5), (0, .5)], loc=(.95, y0 + 5.55, JT_DECK),
            seg=10)
    a.part('Keg_bands', 'Steel').cyl(.245, .04, loc=(.95, y0 + 5.55, JT_DECK + .25), seg=10, bevel=0)
    K.crate(a.part('Tool_chests', 'Armor'), a.part('Kit_latches', 'Steel'), (.55, .4, .32), (.95, y0 + 1.25, JT_DECK),
            bands=1)
    K.crate(a.part('Tool_chests', 'Crate'), a.part('Kit_latches', 'Steel'), (.45, .5, .28), (-.95, y0 + 1.25,
                                                                                            JT_DECK), bands=1)
    # The hand derrick on its post (left rear corner): the mast, the jib, the winch drum and crank, the hook block.
    der = a.part('Derrick', 'CraneYellow')
    bx, by = .95, y1 - .7
    k.block(a.part('Derrick_base', 'Armor'), (.5, .5, .1), loc=(bx, by, JT_DECK + .05), chamfer=.02)
    der.cyl(.07, 1.7, loc=(bx, by, JT_DECK + .9), seg=8, bevel=0)
    top = Vector((bx, by, JT_DECK + 1.72))
    tip = Vector((bx - .55, by - 1.6, JT_DECK + 2.1))
    der.limb(tuple(top - Vector((0, 0, .2))), tuple(tip), .08, .1, bevel=0)
    der.limb(tuple(Vector((bx, by, JT_DECK + .5))), tuple(tip.lerp(top, .55)), .05, .05, bevel=0)
    a.part('Derrick_steel', 'Steel').cyl(.09, .3, loc=(bx, by + .15, JT_DECK + .7), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Derrick_steel', 'Steel').limb((bx + .17, by + .15, JT_DECK + .7), (bx + .17, by + .45, JT_DECK + .6),
                                          .03, .03, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(bx, by + .15, JT_DECK + .79), tuple(top), tuple(tip),
                                        tuple(tip - Vector((0, 0, .7)))], .012, seg=4, caps=False)
    k.block(a.part('Hook_block', 'Steel'), (.12, .08, .16), loc=tuple(tip - Vector((0, 0, .88))), chamfer=.01)
    K.dust(a, (0, (y0 + y1) / 2, .5), radius=4.0, k=.18)


def _jt_command_car(a):
    """The command car: a faceted armoured body (sloped sides, the roof deck), riveted side plates, the observation
    tower at its front end with the stereoscopic rangefinder that lays the 152 mm, the bedstead radio antenna on
    insulators round the roof, whip antennas, the stove pipe, mushroom vents, end doors with gangway rails, side
    doors, vision slits and pistol ports, a ladder up the rear wall."""
    y0, y1 = JT_CMD
    mid = (y0 + y1) / 2
    W8._train_car_base(a, y0, y1, (y0 + 1.75, y1 - 1.75))

    def sec(y, w, zs, zr, wr):
        return [(-w, y, 1.34), (w, y, 1.34), (w, y, zs), (wr, y, zr), (-wr, y, zr), (-w, y, zs)]
    k.sharp_loft(a.part('Car_body', 'Team'), [sec(y0 + .02, 1.45, 1.95, 2.72, 1.0), sec(y0 + .45, 1.6, 2.12, 3.02, 1.15),
                                              sec(y1 - .45, 1.6, 2.12, 3.02, 1.15), sec(y1 - .02, 1.45, 1.95, 2.72, 1.0)],
                 chamfer=.06)
    a.part('Roof_deck', 'Armor').box((2.25, y1 - y0 - 1.0, .03), loc=(0, mid, 3.03), bevel=0)
    rv = a.part('Kit_rivets', 'Steel')
    arm = a.part('Armor', 'Armor')
    gl = a.part('Vision_slits', 'Glass')
    for s in (-1, 1):
        for j in range(5):
            y = y0 + 1.05 + j * 1.6
            if abs(y - mid) < .6:
                continue
            K.armour_plate(a, arm, (.6, 1.4, .05), (s * 1.62, y, 1.72), rot=(0, s * R90, 0), rivet=.45)
        a.part('Car_band', 'Team').box((.03, y1 - y0 - 1.0, .14), loc=(s * 1.63, mid, 2.06), bevel=0)
        _studs(rv, (s * 1.615, y0 + .5, 1.42), (s * 1.615, y1 - .5, 1.42), pitch=.2)
        _studs(rv, (s * 1.615, y0 + .5, 2.08), (s * 1.615, y1 - .5, 2.08), pitch=.2)
        _studs(rv, (s * 1.16, y0 + .5, 3.0), (s * 1.16, y1 - .5, 3.0), pitch=.24)
        # The side door with its hinges and handle, the step under it.
        k.block(a.part('Car_doors', 'Armor'), (.05, .8, 1.05), loc=(s * 1.63, mid, 1.95), chamfer=.012)
        for z in (1.6, 2.3):
            a.part('Kit_hinges', 'Steel').cyl(.03, .12, loc=(s * 1.665, mid + .4, z), seg=6, bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.66, mid - .3, 1.85), (s * 1.66, mid - .3, 2.2), (s, 0, 0),
                 h=.05)
        a.part('Steps', 'Steel').box((.32, .7, .03), loc=(s * 1.5, mid, .9), bevel=0)
        # Vision slits under the shoulder, pistol ports with their plugs.
        for y in (y0 + 1.2, y0 + 2.6, y1 - 2.6, y1 - 1.2):
            gl.box((.03, .42, .08), loc=(s * 1.5, y, 2.42), rot=(0, s * .48, 0), bevel=0)
            arm.box((.06, .52, .05), loc=(s * 1.48, y, 2.53), rot=(0, s * .48, 0), bevel=0)
        for y in (y0 + 1.9, y1 - 1.9):
            a.part('Pistol_ports', 'Steel').cyl(.08, .05, loc=(s * 1.635, y, 1.85), rot=(0, R90, 0), seg=8, bevel=0)
            a.part('Pistol_ports', 'Charred').cyl(.04, .02, loc=(s * 1.665, y, 1.85), rot=(0, R90, 0), seg=6, bevel=0)
        K.lamp(a, (s * 1.62, y0 + .5, 2.25), (s, 0, 0), r=.07, guard=False)
        for yb in (y0 + 1.75, y1 - 1.75):
            K.armour_plate(a, a.part('Skirt_plates', 'Armor'), (.55, 2.1, .05), (s * 1.42, yb, .78),
                           rot=(0, s * R90, 0), rivet=.5)
    # End doors and the gangway rails at both ends, the ladder up the rear wall.
    for y, e in ((y0, -1), (y1, 1)):
        k.block(a.part('Car_doors', 'Armor'), (.7, .05, 1.15), loc=(-.35, y + e * .025, 1.98), chamfer=.012)
        a.part('Gangway', 'Steel').box((2.2, .4, .03), loc=(0, y + e * .2, 1.38), bevel=0)
        for s in (-1, 1):
            a.part('Gangway', 'Steel').tube([(s * 1.1, y + e * .02, 1.4), (s * 1.1, y + e * .38, 1.4),
                                             (s * 1.1, y + e * .38, 2.25), (s * .5, y + e * .38, 2.25)], .02, seg=4)
    K.ladder(a.part('Ladders', 'Steel'), (.75, y1 + .06, 1.45), (.75, y1 + .06, 3.0), width=.4, step=.3,
             facing=(0, 1))
    # The observation tower at the front end: a faceted house on a ring, vision blocks, the rangefinder across it.
    ty = y0 + 1.9
    k.ring(a.part('Tower_ring', 'Steel'), [(.82, 0), (.9, 0), (.9, .1), (.82, .1)], loc=(0, ty, 3.02), seg=16)
    oct_lo = [(math.cos(u) * .95, math.sin(u) * .95) for u in [i * TAU / 8 + TAU / 16 for i in range(8)]]
    oct_hi = [(x * .78, y * .78) for x, y in oct_lo]
    K.slab_loft(a.part('Cmd_tower', 'Team'), oct_lo, oct_hi, 0, .78, loc=(0, ty, 3.1))
    a.part('Cmd_tower_roof', 'Armor').cyl(.74, .06, loc=(0, ty, 3.91), seg=8, bevel=0)
    for i in range(8):
        u = i * TAU / 8 + TAU / 16
        if abs(math.cos(u)) > .9:
            continue
        gl.box((.26, .02, .07), loc=(math.cos(u) * .88, ty + math.sin(u) * .88, 3.62), rot=(0, 0, u + R90), bevel=0)
    rf = a.part('Rangefinder', 'Steel')
    rf.cyl(.1, 2.9, loc=(0, ty - .15, 4.1), rot=(0, R90, 0), seg=12, bevel=0)
    for s in (-1, 1):
        k.block(a.part('Rangefinder_heads', 'Armor'), (.26, .3, .3), loc=(s * 1.5, ty - .15, 3.95), chamfer=.03)
        gl.box((.16, .02, .1), loc=(s * 1.5, ty - .31, 4.1), bevel=0)
        rf.cyl(.13, .08, loc=(s * .55, ty - .15, 4.1), rot=(0, R90, 0), seg=12, bevel=0)
    k.block(a.part('Rangefinder_hood', 'Armor'), (.7, .5, .28), loc=(0, ty - .1, 3.97), chamfer=.04)
    K.periscope(a, (.35, ty + .45, 3.97), facing=(0, -1, 0))
    K.hatch_round(a, (-.35, ty + .35, 3.97), r=.24, periscopes=0, seg=10)
    # The bedstead antenna: a rail loop on insulator posts round the roof behind the tower.
    ant = a.part('Frame_antenna', 'Steel')
    ins = a.part('Insulators', 'PlasterWhite')
    ya, yb = ty + 1.3, y1 - .55
    loop = [(-.95, ya), (.95, ya), (.95, yb), (-.95, yb)]
    for x, y in loop + [(0, ya), (0, yb), (-.95, (ya + yb) / 2), (.95, (ya + yb) / 2)]:
        ant.cyl(.025, .42, loc=(x, y, 3.25), seg=5, bevel=0)
        ins.cyl(.045, .1, loc=(x, y, 3.5), seg=8, bevel=0)
    ant.tube([(x, y, 3.56) for x, y in loop] + [(loop[0][0], loop[0][1], 3.56)], .02, seg=4, caps=False)
    ant.tube([(0, ya, 3.56), (0, yb, 3.56)], .016, seg=4, caps=False)
    a.part('Kit_cables', 'Rubber').tube([(0, ya, 3.56), (.2, ya - .3, 3.25), (.25, ya - .55, 3.05)], .015, seg=4)
    for x, y, h in ((-1.0, y1 - .35, 1.8), (1.0, ty + .3, 1.4)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, 3.04), h=h, r=.02)
    # The stove pipe and two mushroom vents on the roof, a field telephone box on the rear wall.
    K.smokestack(a, (-.7, y1 - 1.1, 3.04), r=.07, h=.55, mat='Steel')
    for x, y in ((.55, mid - .9), (-.55, mid + .4)):
        a.part('Vents', 'Steel').cyl(.07, .2, loc=(x, y, 3.13), seg=8, bevel=0)
        a.part('Vents', 'Armor').cyl(.17, .06, loc=(x, y, 3.25), seg=10, r2=.12, bevel=0)
    k.block(a.part('Phone_box', 'Armor'), (.35, .12, .4), loc=(-.85, y1 + .07, 1.9), chamfer=.02)
    K.dust(a, (0, mid, .5), radius=4.5, k=.16)


def _jt_tail_platform(a):
    """The rear control platform: telephone cable drums and a spare wheelset, fuel drums, a tarpaulin over stores, the
    sandbag breastwork at the tail, red tail lamps on posts and the train's tail discs."""
    y0, y1 = JT_TAIL
    W8._train_car_base(a, y0, y1, (y0 + 1.5, y1 - 1.5))
    _jt_flat_sides(a, y0, y1)
    _cable_drum(a, (.62, y0 + 1.0, JT_DECK), r=.5, w=.6)
    _cable_drum(a, (-.62, y0 + 1.0, JT_DECK), r=.45, w=.6)
    # A spare wheelset lying on chocks: two rail wheels on their axle.
    ws = a.part('Spare_wheelset', 'Steel')
    for s in (-1, 1):
        k.lathe(ws, [(0, -.07), (.41, -.07), (.46, -.04), (.46, .05), (.5, .07), (.23, .09), (0, .09)],
                loc=(s * .72, y0 + 2.6, JT_DECK + .5), rot=(0, s * R90, 0), seg=16)
    ws.cyl(.08, 1.55, loc=(0, y0 + 2.6, JT_DECK + .5), rot=(0, R90, 0), seg=8, bevel=0)
    for s in (-1, 1):
        a.part('Chocks', 'Wood').box((.25, .3, .12), loc=(s * .72, y0 + 2.6 + .32, JT_DECK + .06), bevel=0)
        a.part('Chocks', 'Wood').box((.25, .3, .12), loc=(s * .72, y0 + 2.6 - .32, JT_DECK + .06), bevel=0)
    for i, x in enumerate((-.85, -.3)):
        K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (x, y0 + 3.85, JT_DECK), r=.27, h=.85)
    # The tarpaulin over stacked stores, its ropes.
    k.block(a.part('Tarpaulin', 'Canvas'), (1.2, 1.3, .7), loc=(.55, y0 + 3.9, JT_DECK + .35), chamfer=.12)
    for f in (-.35, .35):
        st = a.part('Kit_straps', 'Undercarriage')
        st.box((1.1, .06, .025), loc=(.55, y0 + 3.9 + f, JT_DECK + .71), bevel=0)
        for sx in (-1, 1):
            st.box((.025, .06, .6), loc=(.55 + sx * .61, y0 + 3.9 + f, JT_DECK + .38), bevel=0)
    K.sandbag_run(a, [(-1.05, y1 - .45, JT_DECK), (1.05, y1 - .45, JT_DECK)], courses=3, bag=(.5, .3, .16),
                  part='Sandbags', seed=41, lean=True)
    for s in (-1, 1):
        K.sandbag_run(a, [(s * 1.05, y1 - .8, JT_DECK), (s * 1.05, y1 - 1.6, JT_DECK)], courses=2,
                      bag=(.5, .3, .16), part='Sandbags', seed=43 + s, lean=True)
        a.part('Lamp_posts', 'Steel').cyl(.035, 1.0, loc=(s * 1.2, y1 - .25, JT_DECK + .9), seg=6, bevel=0)
        K.lamp(a, (s * 1.2, y1 - .18, JT_DECK + 1.38), (0, 1, 0), r=.11, guard=True, glow='LavaGlow')
        k.lathe(a.part('Tail_discs', 'BarrelRed'), [(0, 0), (.16, 0), (.16, .02), (0, .02)],
                loc=(s * .6, y1 + .02, 1.1), rot=K.BACKWARD, seg=12)
    a.part('Hazard_board', 'Hazard').box((1.6, .03, .3), loc=(0, y1 + .02, JT_DECK + .35), bevel=0)
    K.dust(a, (0, (y0 + y1) / 2, .5), radius=4.0, k=.18)


def armored_train(a):
    """Juggernaut (module docstring): the wave 8 train with three more cars, centred on its length. Runtime names are
    the wave 8 builder's (Turret / Main_cannon / Muzzle_brake / Muzzle_main, Muzzle_main.001, Mount_rocket, Mount_mg /
    .001 / .002, Part_mortar > Mount_mortar > Muzzle_mortar, Point_fire, Point_exhaust); the new cars add none."""
    W8.armored_train(a)
    _drop(a, 'Tail_lights', 'LavaGlow')
    _jt_front_platform(a)
    _jt_command_car(a)
    _jt_tail_platform(a)
    k.clean(a)
    _recentre(a)


# ============================================================================= nuke_train (Nemesis)
NT_CMD = (30.59, 39.0)        # command and communications car behind the AA flatcar (29.83)
NT_PUSHER = (39.76, 48.36)    # pusher diesel, cab at the tail


def _nt_command_car(a):
    """The BZhRK command and communications car, disguised as a refrigerator wagon: the tall ribbed box body with the
    curved roof, sliding doors, the false reefer hatches, two satcom radomes, the telescopic mast folded along the roof
    on its hinge, HF antenna posts, the air-conditioning units with their grilles, a generator exhaust, ladders, the
    walkway; armoured skirts over the bogies."""
    y0, y1 = NT_CMD
    mid, L = (y0 + y1) / 2, y1 - y0
    for y in (y0 + 1.45, y1 - 1.45):
        NT._bogie(a, y, 2, 1.8, .46)
    NT._frame(a, y0, y1, z=1.34)
    prof = [(-1.56, 1.34), (1.56, 1.34), (1.6, 1.5), (1.6, 3.45), (1.5, 3.7), (1.15, 3.9), (0, 3.98), (-1.15, 3.9),
            (-1.5, 3.7), (-1.6, 3.45), (-1.6, 1.5)]
    k.extrude(a.part('Car_body', 'Team'), prof, L - .2, loc=(0, mid, 0), axis='Y', chamfer=.06)
    # The reefer's ribs and the side sill band, the sliding doors on their rails, the false reefer hatches.
    ribs = a.part('Car_ribs', 'Team')
    for s in (-1, 1):
        for i in range(12):
            y = y0 + .45 + i * (L - .9) / 11
            if abs(y - mid) < 1.0:
                continue
            ribs.box((.05, .07, 1.95), loc=(s * 1.625, y, 2.48), bevel=0)
        a.part('Car_band', 'Team').box((.02, L - .5, .16), loc=(s * 1.615, mid, 1.62), bevel=0)
        door = a.part('Car_doors', 'Armor')
        k.block(door, (.05, 1.7, 1.85), loc=(s * 1.635, mid + .15, 2.45), chamfer=.015)
        for z in (1.6, 3.42):
            a.part('Door_rails', 'Steel').box((.05, 3.6, .06), loc=(s * 1.67, mid, z), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.665, mid - .55, 2.2), (s * 1.665, mid - .55, 2.7), (s, 0, 0),
                 h=.05)
        for f in (-.5, .5):
            a.part('Door_bars', 'Steel').box((.03, .05, 1.7), loc=(s * 1.665, mid + .15 + f * 1.3, 2.47), bevel=0)
        for y in (y0 + 1.5, y1 - 1.5):
            k.block(a.part('Reefer_hatches', 'Armor'), (.05, .9, .7), loc=(s * 1.63, y, 2.6), chamfer=.01)
            a.part('Reefer_hatches', 'Steel').box((.03, .6, .05), loc=(s * 1.66, y, 3.15), bevel=0)
        # Armoured skirts over the bogies, small ports with armour shutters, marker lamps, the ladder.
        for y in (y0 + 1.45, y1 - 1.45):
            k.block(a.part('Armor', 'Armor'), (.06, 2.7, .7), loc=(s * 1.665, y, 1.05), chamfer=.015)
            a.part('Kit_bolts', 'Steel').bolts([(s * 1.7, y + d, 1.35) for d in (-1.1, -.37, .37, 1.1)], r=.028,
                                               h=.03, rot=(0, R90, 0), seg=6, bevel=0)
        for y in (mid - 2.2, mid + 2.4):
            a.part('Ports', 'Glass').box((.03, .35, .22), loc=(s * 1.615, y, 3.05), bevel=0)
            a.part('Port_shutters', 'Armor').box((.05, .45, .05), loc=(s * 1.63, y, 3.22), rot=(0, s * .5, 0),
                                                 bevel=0)
        K.lamp(a, (s * 1.6, y1 - .2, 1.8), (0, 1, 0), r=.07, guard=False, glow='Alloy')
        K.ladder(a.part('Ladders', 'Steel'), (s * 1.0, y0 - .02, 1.4), (s * 1.0, y0 - .02, 3.75), width=.42,
                 step=.3, facing=(0, -1))
    # The roof: the walkway, two radomes, the folded mast with its head, HF posts, A/C units, the exhaust.
    wk = a.part('Walkway', 'Steel')
    wk.box((.55, L - .6, .03), loc=(0, mid, 4.0), bevel=0)
    for i in range(int((L - .6) / .3)):
        wk.box((.55, .025, .02), loc=(0, y0 + .45 + i * .3, 4.025), bevel=0)
    for y, r in ((y0 + 1.6, .62), (y0 + 3.15, .48)):
        k.lathe(a.part('Radome_bases', 'Armor'), [(r * .9, 0), (r * .95, .05), (r * .95, .22), (r * .85, .26)],
                loc=(.85, y, 3.86), seg=14)
        k.lathe(a.part('Radomes', 'PlasterWhite'), [(r * .85, 0), (r * .85, r * .35), (r * .7, r * .78),
                                                    (r * .42, r * 1.02), (0, r * 1.12)], loc=(.85, y, 4.11), seg=16)
    mast = a.part('Mast', 'Steel')
    mx = -.75
    k.block(a.part('Mast_cradle', 'Armor'), (.5, .5, .32), loc=(mx, y1 - 1.0, 3.85), chamfer=.04)
    for r, y_a, y_b in ((.17, y1 - 1.1, y0 + 2.6), (.13, y0 + 2.6, y0 + 1.35), (.1, y0 + 1.35, y0 + .55)):
        mast.cyl(r, y_a - y_b, loc=(mx, (y_a + y_b) / 2, 4.3), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Mast_collars', 'Armor').cyl(r + .03, .1, loc=(mx, y_b + .05, 4.3), rot=K.FORWARD, seg=10, bevel=0)
    for y in (y0 + 2.4, mid + .5):
        a.part('Mast_cradle', 'Armor').box((.4, .14, .36), loc=(mx, y, 4.06), bevel=0)
    a.part('Mast_head', 'Medical').box((.7, .12, .45), loc=(mx, y0 + .5, 4.32), bevel=.02)
    a.part('Mast_hinge', 'Steel').cyl(.09, .6, loc=(mx, y1 - .9, 4.12), rot=(0, R90, 0), seg=10, bevel=0)
    for y in (mid - 1.4, mid + .2):
        K.chamfer_box(a.part('Ac_units', 'Armor'), (.9, 1.1, .35), loc=(.75, y, 3.88), c=.04)
        K.grille(a, (.75, y, 4.24), .7, .8, facing=(0, 0, 1), slats=5)
    for x, y in ((.95, y1 - .5), (-1.2, y0 + .5), (1.25, mid + 1.6)):
        a.part('Hf_posts', 'Steel').cyl(.03, 1.0, loc=(x, y, 4.3), seg=6, bevel=0)
        a.part('Insulators', 'PlasterWhite').cyl(.05, .1, loc=(x, y, 4.82), seg=8, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(.95, y1 - .5, 4.82), (1.25, mid + 1.6, 4.82)], .01, seg=4, caps=False)
    K.exhaust(a, (-1.25, mid + 1.7, 3.8), r=.08, length=.5, direction=(0, 0, 1), muffler=True)
    K.soot(a, (-1.25, mid + 1.7, 4.4), radius=.6, k=.4)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.2, mid - .8, 3.9), h=1.5, r=.02)
    K.beacon(a, (1.2, y0 + .45, 3.75), r=.08)
    K.dust(a, (0, mid, .5), radius=4.5, k=.14)


def _nt_sec(y, wb, zb, wm, zm, wt, zt):
    return [(-wb, y, zb), (wb, y, zb), (wm, y, zm), (wt, y, zt), (-wt, y, zt), (-wm, y, zm)]


def _nt_pusher(a):
    """The pusher diesel at the train's tail, the front locomotive's sister turned round: the wedge cab at the tail
    with its vision slits under the brow, headlamps and red tail lamps, the plough, the hood of sloped bolted plates
    with louvres, radiator fans and twin stacks, side doors with steps and handrails, armoured bogie skirts. Unarmed."""
    y0, y1 = NT_PUSHER
    for y in (y0 + 2.2, y1 - 2.0):
        NT._bogie(a, y, 3, 2.2, .5)
    NT._frame(a, y0, y1, z=1.3, rear=False)
    # The hull: the front locomotive's stations from its rear to its nose, laid from y0 (coupled end) to y1 (nose).
    st = [(8.87, 1.55, 2.05, 1.1, 2.75), (8.32, 1.62, 2.1, 1.18, 3.05), (3.62, 1.62, 2.1, 1.18, 3.05),
          (3.32, 1.62, 2.25, 1.22, 3.45), (1.62, 1.62, 2.25, 1.22, 3.45), (.92, 1.62, 2.05, 1.2, 2.95),
          (.17, 1.5, 1.85, .9, 2.25)]
    nose = y1 + .17
    rings = []
    for d, wm, zm, wt, zt in st:
        wb = 1.55 if d > 8.5 else (1.5 if d < .5 else 1.6)
        rings.append(_nt_sec(nose - d, wb, 1.32, wm, zm, wt, zt))
    k.sharp_loft(a.part('Hull', 'Team'), rings, chamfer=.05)
    arm = a.part('Armor', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    # The plough at the tail.
    k.sharp_loft(arm, [[(-1.45, y1 + .2, .2), (1.45, y1 + .2, .2), (1.35, y1 + .44, .2), (.3, y1 + .77, .2),
                        (-.3, y1 + .77, .2), (-1.35, y1 + .44, .2)],
                       [(-1.38, y1 + .18, 1.0), (1.38, y1 + .18, 1.0), (1.25, y1 + .32, 1.0), (.25, y1 + .48, 1.0),
                        (-.25, y1 + .48, 1.0), (-1.25, y1 + .32, 1.0)]], chamfer=.03)
    chev = a.part('Chevrons', 'SafetyStripe')
    for s in (-1, 1):
        for i in range(3):
            chev.box((.18, .03, .55), loc=(s * (.45 + i * .32), y1 + .64 - i * .09, .62), rot=(0, s * .5, s * .3),
                     bevel=0)
    gl = a.part('Vision_slits', 'Glass')
    ang = math.atan2(.5, .7)
    for x in (-.72, 0, .72):
        gl.box((.5, .12, .04), loc=(x, nose - 1.22, 3.18), rot=(-ang, 0, 0), bevel=0)
    arm.box((2.2, .26, .06), loc=(0, nose - 1.42, 3.42), bevel=0)
    gl.box((.7, .12, .04), loc=(0, nose - .52, 2.58), rot=(-math.atan2(.7, .75), 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .78, nose - .15, 1.7), (0, 1, 0), r=.13, mat='Armor', guard=True)
        K.lamp(a, (s * 1.08, nose - .15, 1.98), (0, 1, 0), r=.08, mat='Armor', guard=False, glow='LavaGlow')
        for d in (2.07, 2.87):
            gl.box((.03, .5, .1), loc=(s * 1.47, nose - d, 2.95), rot=(0, -s * .32, 0), bevel=0)
        k.block(a.part('Cab_doors', 'Armor'), (.04, .64, .72), loc=(s * 1.63, nose - 2.67, 1.75), chamfer=.01)
        a.part('Handrails', 'Steel').tube([(s * 1.68, nose - 2.27, 1.4), (s * 1.68, nose - 2.27, 2.2)], .02, seg=4)
        a.part('Car_steps', 'Steel').box((.3, .5, .03), loc=(s * 1.55, nose - 2.67, .95), bevel=0)
        for y in (y0 + 2.2, y1 - 2.0):
            k.block(arm, (.06, 3.3, .8), loc=(s * 1.67, y, 1.1), chamfer=.015)
            bolts.bolts([(s * 1.71, y + d, 1.42) for d in (-1.4, -.7, 0, .7, 1.4)], r=.028, h=.03, rot=(0, R90, 0),
                        seg=6, bevel=0)
        for d in (4.3, 5.6, 6.9, 8.2):
            k.block(arm, (.06, 1.2, .52), loc=(s * 1.42, nose - d, 2.56), rot=(0, -s * .44, 0), chamfer=.012)
            bolts.bolts([(s * 1.45, nose - d + e, 2.6) for e in (-.5, .5)], r=.025, h=.03, rot=(0, R90, 0), seg=6,
                        bevel=0)
        K.grille(a, (s * 1.645, nose - 4.9, 1.72), 1.1, .5, facing=(s, 0, 0), slats=4)
        K.grille(a, (s * 1.645, nose - 7.4, 1.72), 1.1, .5, facing=(s, 0, 0), slats=4)
        a.part('Car_band', 'Team').box((.012, 5.5, .12), loc=(s * 1.632, nose - 5.9, 1.42), bevel=0)
    # Roof: radiator fans in their rings, the twin stacks, the horn, a beacon, the antenna.
    for d in (4.6, 5.6):
        k.ring(a.part('Fans', 'Armor'), [(.36, 0), (.42, 0), (.42, .1), (.36, .1)], loc=(0, nose - d, 3.05), seg=12)
        a.part('Fans', 'Undercarriage').cyl(.36, .02, loc=(0, nose - d, 3.07), seg=12, bevel=0)
    for s in (-1, 1):
        K.smokestack(a, (s * .55, nose - 7.0, 3.0), r=.12, h=.6, mat='Steel')
    k.lathe(a.part('Horn', 'Steel'), [(.04, 0), (.05, .2), (.12, .32), (.12, .34)], loc=(.5, nose - 1.9, 3.45),
            rot=K.BACKWARD, seg=8)
    K.beacon(a, (-.5, nose - 2.2, 3.45), r=.08)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.8, nose - 3.0, 3.45), h=1.2, r=.02)
    k.ring(a.part('Cupola_top', 'Armor'), [(.3, 0), (.36, 0), (.36, .16), (.3, .16)], loc=(.4, nose - 2.6, 3.45),
           seg=12)
    K.dust(a, (0, (y0 + y1) / 2, .5), radius=5.0, k=.14)


def nuke_train(a):
    """Nemesis (module docstring): the wave 12 train with the command car and the pusher diesel at its tail, centred
    on its length. Runtime names are the wave 12 builder's (Turret / Main_cannon / _2 / Muzzle_brake / _2 /
    Muzzle_main, Mount_mg / .001 / .002 with their muzzles, Part_rocket / Part_missile / Part_gun152 / Part_aa with
    their mounts and muzzles, Erector / Icbm_payload, Point_fire, Point_exhaust); the new cars add none."""
    NT.nuke_train(a)
    _drop(a, 'Tail_lights', 'Alloy')
    _nt_command_car(a)
    _nt_pusher(a)
    k.clean(a)
    _recentre(a)


# ============================================================================= ixion
IX_ROOF = IX.ROOF


def _ixion_rws(a):
    """The 2A42 30 mm in a low remote turret at the canopy's right rear corner (Mount_gun), sized for the 26 m truck but kept under
    the 125 mm's line (its top 9.05 m; the main gun's barrel passes over at 9.18 m): the ring, the faceted armoured
    house with its front plate and side cheeks, the sight head on its left, the ammunition box on its right, the
    cradle, the long barrel with its jacket and the two-baffle brake (Gun_barrels / Gun_muzzles kick back on the
    mount), Muzzle_gun at the brake's mouth."""
    x, y, z = -3.9, -7.9, IX_ROOF
    k.lathe(a.part('Rws_ring', 'Steel'), [(1.12, 0), (1.17, .04), (1.17, .12), (1.08, .14)], loc=(x, y, z), seg=22)
    a.part('Rws_ring', 'Steel').bolts([(x + math.cos(u) * 1.12, y + math.sin(u) * 1.12, z + .15)
                                       for u in [i * TAU / 16 for i in range(16)]], r=.03, h=.03, seg=6, bevel=0)
    m = a.pivot('Mount_gun', (x, y, z + .14))
    house = a.part('Rws_house', 'Team', m)
    k.sharp_loft(house, [[(-.95, -.8, 0), (.95, -.8, 0), (1.0, 1.05, 0), (-1.0, 1.05, 0)],
                         [(-.92, -1.0, .2), (.92, -1.0, .2), (1.0, 1.08, .2), (-1.0, 1.08, .2)],
                         [(-.7, -.62, .46), (.7, -.62, .46), (.85, .98, .46), (-.85, .98, .46)]], chamfer=.05)
    arm = a.part('Rws_armor', 'Armor', m)
    k.block(arm, (.62, .5, .36), loc=(0, -1.2, .26), chamfer=.04)
    for sx in (-1, 1):
        k.block(arm, (.06, 1.5, .36), loc=(sx * 1.03, .1, .2), chamfer=.015)
        a.part('Rws_bolts', 'Steel', m).bolts([(sx * 1.07, yy, .3) for yy in (-.4, .1, .6)], r=.025, h=.025,
                                              rot=(0, R90, 0), seg=6, bevel=0)
    # The sight head (day / thermal windows) on its own post on the left, the ammunition box on the right.
    k.block(a.part('Rws_sight', 'Armor', m), (.4, .5, .36), loc=(1.25, -.5, .4), chamfer=.04)
    a.part('Rws_sight', 'Steel', m).cyl(.08, .3, loc=(1.25, -.4, .12), seg=8, bevel=0)
    for gx in (1.17, 1.33):
        a.part('Rws_glass', 'Glass', m).box((.12, .02, .12), loc=(gx, -.76, .43), bevel=0)
    k.block(a.part('Rws_ammo', 'Armor', m), (.36, .8, .4), loc=(-1.25, .3, .2), chamfer=.04)
    a.part('Rws_ammo', 'Steel', m).box((.28, .04, .3), loc=(-1.25, -.11, .2), bevel=0)
    # The cradle and the gun: the receiver box, the barrel with its jacket, the brake.
    k.block(a.part('Rws_cradle', 'Armor', m), (.34, .9, .26), loc=(0, -1.0, .3), chamfer=.03)
    gun = a.part('Gun_barrels', 'Steel', m)
    L, zg = 3.2, .3
    k.lathe(gun, [(.1, 0), (.1, .7), (.075, .76), (.068, L - .4), (.06, L - .35), (.06, L)],
            loc=(0, -1.45, zg), rot=K.FORWARD, seg=12, worn=(2,))
    k.lathe(a.part('Gun_muzzles', 'Steel', m), [(.07, -.02), (.11, 0), (.11, .16), (.07, .19), (.11, .23),
                                                (.11, .38), (.06, .4), (0, .4)],
            loc=(0, -1.45 - L, zg), rot=K.FORWARD, seg=12)
    a.part('Gun_muzzles', 'Charred', m).cyl(.035, .02, loc=(0, -1.45 - L - .405, zg), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, -1.45 - L - .42, zg), m)
    a.part('Rws_cables', 'Rubber', m).tube([(-1.1, .7, .2), (-.6, 1.0, .35), (0, .95, .46)], .03, seg=4)
    K.whip_antenna(a.part('Rws_antenna', 'Steel', m), (.7, .9, .46), h=.45, r=.018)
    K.tone(a, 'Mount_gun', k=.92)


def _ixion_kornet(a, index, s):
    """A 9M133 Kornet-EM twin launcher on the roof edge (Mount_missile left, .001 right), drawn at the truck's scale
    and kept under the 125 mm's line: the base plate and pedestal, the yaw head, the cradle arms carrying two
    transport-launch containers side by side (end caps, a clamp band, the bore at the front), the guidance unit
    behind them with its window; Muzzle_missile at the inner container's mouth."""
    x, y, z = s * 4.75, -.4, IX_ROOF
    k.block(a.part('Kornet_base', 'Armor'), (1.0, 1.0, .08), loc=(x, y, z + .04), chamfer=.02)
    a.part('Kornet_base', 'Steel').bolts([(x + dx, y + dy, z + .09) for dx in (-.38, .38) for dy in (-.38, .38)],
                                         r=.035, h=.03, seg=6, bevel=0)
    key = K.name('Mount_missile', index)
    m = a.pivot(key, (x, y, z + .08))
    tag = '' if index == 0 else '_001'
    k.lathe(a.part('Kornet_pedestal' + tag, 'Steel', m), [(.18, 0), (.18, .08), (.13, .1), (.13, .16)], seg=12)
    k.block(a.part('Kornet_head' + tag, 'Team', m), (.62, .62, .12), loc=(0, 0, .19), chamfer=.03)
    L, r, zt = 2.2, .16, .38
    for sx in (-1, 1):
        a.part('Kornet_cradle' + tag, 'Team', m).box((.05, .9, .26), loc=(sx * .42, -.1, .3), bevel=0)
    tubes = a.part('Kornet_tubes' + tag, 'Armor', m)
    caps = a.part('Kornet_caps' + tag, 'Steel', m)
    bore = a.part('Kornet_bores' + tag, 'Undercarriage', m)
    for tx in (-.2, .2):
        tubes.cyl(r, L, loc=(tx, -.25, zt), rot=K.FORWARD, seg=14, bevel=0)
        for f in (-1, 1):
            caps.cyl(r + .025, .12, loc=(tx, -.25 + f * (L / 2 - .06), zt), rot=K.FORWARD, seg=14, bevel=0)
        caps.cyl(r + .018, .07, loc=(tx, -.1, zt), rot=K.FORWARD, seg=14, bevel=0)
        bore.cyl(r * .8, .02, loc=(tx, -.25 - L / 2 - .002, zt), rot=K.FORWARD, seg=12, bevel=0)
    a.part('Kornet_bands' + tag, 'Hazard', m).cyl(r + .02, .04, loc=(.2, -.25 - L / 2 + .2, zt), rot=K.FORWARD,
                                                  seg=14, bevel=0)
    k.block(a.part('Kornet_sight' + tag, 'Armor', m), (.46, .44, .3), loc=(0, 1.08, .3), chamfer=.04)
    a.part('Kornet_glass' + tag, 'Glass', m).box((.3, .02, .12), loc=(0, .855, .34), bevel=0)
    a.part('Kornet_cables' + tag, 'Rubber', m).tube([(0, 1.3, .3), (.15, 1.25, .12), (.2, .9, .06)], .022, seg=4)
    inner = -s * .2
    a.pivot(K.name('Muzzle_missile', index), (inner, -.25 - L / 2 - .03, zt), key)
    K.tone(a, key, k=.93)


def _ixion_grad(a):
    """The BM-21V "Grad-V" pack (12 x 122 mm, two rows of six) on the rear roof's right edge (Mount_rocket), clear of
    the turret's bustle as it turns: the turntable, the cradle cheeks and the elevating ram, the tube pack raised 10
    degrees with its frame bands, the bores at the front (Tubes_bore: the rounds leave from a random tube of the
    face), Muzzle_rocket at the face."""
    x, y, z = -4.5, 6.95, IX_ROOF
    k.lathe(a.part('Grad_base', 'Steel'), [(.82, 0), (.86, .05), (.86, .16), (.78, .2)], loc=(x, y, z), seg=18)
    m = a.pivot('Mount_rocket', (x, y, z + .2))
    k.lathe(a.part('Grad_turntable', 'Team', m), [(.76, -.02), (.76, .1), (.66, .16), (0, .17)], seg=18)
    for sx in (-1, 1):
        k.block(a.part('Grad_cheeks', 'Armor', m), (.1, .9, .5), loc=(sx * .66, .25, .3), chamfer=.02)
    pitch = math.radians(10)
    piv = Vector((0, .35, .55))
    mm = Matrix.Translation(piv) @ Matrix.Rotation(-pitch, 4, 'X')
    rot = (-pitch, 0, 0)
    L = 2.7
    tubes = a.part('Grad_tubes', 'Armor', m)
    bore = a.part('Tubes_bore', 'Undercarriage', m)
    rims = a.part('Grad_rims', 'Steel', m)
    for ix in range(6):
        for iz in range(2):
            px, pz = -.5 + ix * .2, .02 + iz * .2
            c = mm @ Vector((px, -.45, pz))
            tubes.cyl(.085, L, loc=tuple(c), rot=(R90 - pitch, 0, 0), seg=10, bevel=0)
            f = mm @ Vector((px, -.45 - L / 2 - .01, pz))
            bore.cyl(.064, .02, loc=tuple(f), rot=(R90 - pitch, 0, 0), seg=10, bevel=0)
            rims.cyl(.092, .05, loc=tuple(mm @ Vector((px, -.45 - L / 2 + .02, pz))), rot=(R90 - pitch, 0, 0),
                     seg=10, bevel=0)
    for f in (-1.0, .1, 1.1):
        a.part('Grad_bands', 'Team', m).box((1.34, .1, .5), loc=tuple(mm @ Vector((0, -.45 + f, .12))), rot=rot,
                                            bevel=0)
    a.part('Grad_ram', 'Steel', m).tube([(0, -.55, .12), tuple(mm @ Vector((0, -.9, -.1)))], .06, seg=8)
    a.part('Grad_hazard', 'SafetyStripe', m).box((1.2, .02, .08), loc=tuple(mm @ Vector((0, -.45 + L / 2 + .01,
                                                                                         .35))), rot=rot, bevel=0)
    a.pivot('Muzzle_rocket', tuple(mm @ Vector((0, -.45 - L / 2 - .03, .12))), 'Mount_rocket')
    K.tone(a, 'Mount_rocket', k=.92)


def ixion(a):
    """Ixion (module docstring): the P35 builder's truck and its runtime names (Part_wheel / .001, Part_tyre ..
    .003, Turret / Main_cannon / Muzzle_brake / Muzzle_main, Part_cab > Mount_mg / .001, Point_mines, Point_exhaust,
    Point_fire), plus the new weapon mounts: Mount_gun / Muzzle_gun (30 mm), Mount_missile / .001 with their muzzles
    (Kornet-EM, left / right), Mount_rocket / Muzzle_rocket (Grad-V)."""
    IX.ixion(a)
    _ixion_rws(a)
    _ixion_kornet(a, 0, 1)
    _ixion_kornet(a, 1, -1)
    _ixion_grad(a)
    k.clean(a)


# ============================================================================= mega_gunship (Harpy)
# The fuselage stations (y, half width, bottom, top): the Chinook's box with the rounded nose, the long constant
# section and the rising ramp line; the outline round each is _hp_half.
HP_ST = [(-8.8, .3, 1.5, 2.0), (-8.62, .72, 1.18, 2.42), (-8.3, 1.05, 1.02, 2.8), (-7.85, 1.27, .96, 3.12),
         (-7.3, 1.38, .95, 3.33), (-6.6, 1.42, .95, 3.42), (-3.0, 1.42, .95, 3.45), (2.0, 1.42, .95, 3.45),
         (5.0, 1.42, .97, 3.47), (6.2, 1.4, 1.3, 3.5), (7.4, 1.36, 1.85, 3.52), (8.4, 1.3, 2.3, 3.55),
         (8.72, 1.18, 2.48, 3.48)]
HP_WING = dict(root=(-.95, 2.15), tip=(-.78, 1.55), x0=1.38, span=3.05, z=2.3, anhedral=math.radians(8))
HP_STATIONS = (2.3, 3.2, 4.3)          # inner (gun pod), middle (rocket pod), wingtip (missile launcher)


def _hp_params(y):
    st = HP_ST
    if y <= st[0][0]:
        return st[0][1:]
    for (y0, *p0), (y1, *p1) in zip(st, st[1:]):
        if y <= y1:
            f = (y - y0) / (y1 - y0)
            return tuple(a + (b - a) * f for a, b in zip(p0, p1))
    return st[-1][1:]


def _hp_half(y, grow=0.0):
    """The half outline at y (bottom centre up the +X side to the top centre), `grow` m outwards."""
    w, zb, zt = _hp_params(y)
    h = zt - zb
    pts = [(0, zb), (w * .78, zb + .02), (w * .97, zb + .22), (w, zb + h * .35), (w, zb + h * .7),
           (w * .95, zt - .3), (w * .78, zt - .08), (w * .4, zt), (0, zt)]
    if grow:
        out = []
        for i, (x, z) in enumerate(pts):
            nx = 0 if i in (0, len(pts) - 1) else (1.0 if 2 <= i <= 5 else .6)
            nz = -1 if i <= 1 else (1 if i >= 6 else 0)
            out.append((x + nx * grow, z + nz * grow))
        return out
    return pts


def _hp_on(y, i, f=0.0, grow=0.0):
    """A point on the outline at y between outline points i and i + 1 (fraction f), on the +X side."""
    h = _hp_half(y, grow)
    (x0, z0), (x1, z1) = h[i], h[min(i + 1, len(h) - 1)]
    return (x0 + (x1 - x0) * f, y, z0 + (z1 - z0) * f)


def _quad(shape, pts, out):
    """A one-sided quad facing `out` (the kit's materials cull back faces)."""
    p0, p1, p2 = (Vector(p) for p in pts[:3])
    n = (p1 - p0).cross(p2 - p0)
    shape.mesh(pts, [(0, 1, 2, 3) if n.dot(Vector(out)) > 0 else (3, 2, 1, 0)])


def _hp_wing_z(x):
    w = HP_WING
    return w['z'] - math.tan(w['anhedral']) * (x - w['x0'])


def _hp_fuselage(a):
    """The fuselage skin, the cockpit glazing and its frames, the chin windows, the cabin windows, the forward door,
    the side armour kit, the sponsons along the lower sides, the ramp, seams and rivet rows, the team bands."""
    fus = a.part('Fuselage', 'Team')
    ys = [-8.8, -8.62, -8.3, -7.85, -7.3, -6.6] + [(-6.6 + i * .9) for i in range(1, 13)] + \
        [5.0, 5.6, 6.2, 6.8, 7.4, 7.9, 8.4, 8.72]
    ys = sorted(set(round(y, 3) for y in ys))
    K.section_loft(fus, [(y, _hp_half(y)) for y in ys])
    # The cockpit glazing on the nose's own facets (each pane a facet of the skin, inset and lifted 12 mm): the
    # windscreen pair, the upper windscreen, the side windows, the chin windows; the frames round every pane.
    gl = a.part('Canopy', 'Glass')
    fr = a.part('Canopy_frames', 'Armor')
    panes = [(-8.62, -8.3, 5), (-8.62, -8.3, 6), (-8.3, -7.85, 6), (-8.3, -7.85, 5), (-8.3, -7.85, 4),
             (-7.85, -7.3, 5), (-8.62, -8.3, 2), (-8.62, -8.3, 3)]
    for s in (-1, 1):
        for ya, yb, i in panes:
            ha, hb = _hp_half(ya), _hp_half(yb)
            c = [Vector((s * ha[i][0], ya, ha[i][1])), Vector((s * ha[i + 1][0], ya, ha[i + 1][1])),
                 Vector((s * hb[i + 1][0], yb, hb[i + 1][1])), Vector((s * hb[i][0], yb, hb[i][1]))]
            mid = sum(c, Vector()) / 4
            n = (c[1] - c[0]).cross(c[3] - c[0])
            if n.dot(mid - Vector((0, mid.y, 2.2))) < 0:
                n = -n
            n.normalize()
            pane = [tuple(p.lerp(mid, .1) + n * .012) for p in c]
            _quad(gl, pane, tuple(n))
            ring = [tuple(p + n * .008) for p in c]
            fr.tube(ring + [ring[0]], .022, seg=4, caps=False)
        # Wipers on the windscreen.
        h = _hp_half(-8.46)
        a.part('Wipers', 'Undercarriage').limb((s * h[6][0] * .8, -8.5, h[6][1] + .05),
                                               (s * h[6][0] * .55, -8.4, h[6][1] + .28), .02, .015, bevel=0)
    # Cabin windows (Chinook rectangles) in their frames, the forward door with its open gun port.
    for s in (-1, 1):
        for y in (-5.6, -3.3, -2.1, 2.7, 3.9):
            if s > 0 and y == -5.6:
                continue
            x = 1.425
            gl.box((.02, .42, .42), loc=(s * x, y, 2.55), bevel=0)
            fr.box((.03, .5, .5), loc=(s * (x - .012), y, 2.55), bevel=0)
        # Door gun openings (the miniguns at y -4.6): a dark recess with its frame and the sliding door slid back.
        a.part('Door_openings', 'Charred').box((.02, 1.0, 1.1), loc=(s * 1.428, -4.6, 2.05), bevel=0)
        fr.tube([(s * 1.44, -5.12, 1.48), (s * 1.44, -5.12, 2.62), (s * 1.44, -4.08, 2.62), (s * 1.44, -4.08, 1.48)],
                .03, seg=4, caps=True)
        k.block(a.part('Doors', 'Armor'), (.04, 1.0, 1.15), loc=(s * 1.47, -3.55, 2.05), chamfer=.012)
        a.part('Door_rails', 'Steel').box((.04, 2.2, .05), loc=(s * 1.49, -4.0, 2.66), bevel=0)
    # Side armour kit on the cockpit and cabin sides: bolted plates.
    arm = a.part('Armor', 'Armor')
    for s in (-1, 1):
        for y, z, wd, ht in ((-7.0, 1.55, .9, .7), (-6.1, 1.55, .8, .7), (-1.0, 1.25, 1.8, .45), (1.0, 1.25, 1.8, .45)):
            K.panel(a, arm, (wd, ht), (s * 1.432, y, z), (s, 0, 0), t=.03, rivet=.22, r=.012, seg=4)
    # Seams and rivet rows round the fuselage at the frames, the team bands along the shoulders.
    rv = a.part('Kit_rivets', 'Steel')
    seams = a.part('Seams', 'Undercarriage')
    for y in (-6.6, -5.0, -1.9, .2, 3.2, 5.0):
        h = _hp_half(y, .006)
        ring = [(x, y, z) for x, z in h] + [(-x, y, z) for x, z in reversed(h[1:-1])]
        seams.tube(ring + [ring[0]], .008, seg=3, caps=False)
    for s in (-1, 1):
        K.rivet_line(rv, (s * 1.43, -6.5, 3.0), (s * 1.43, 4.9, 3.0), (s, 0, 0), pitch=.35, r=.014, h=.014, seg=4)
        K.rivet_line(rv, (s * 1.43, -6.5, 1.12), (s * 1.43, 4.9, 1.12), (s, 0, 0), pitch=.35, r=.014, h=.014, seg=4)
        a.part('Fuselage_stripes', 'Hazard').box((.015, 11.8, .1), loc=(s * 1.432, -.6, 3.12), bevel=0)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .14, .06),
                                                                         loc=(s * 1.44, -6.9, 3.3), bevel=0)
    # Sponsons (the Chinook's side fuel pods) along the lower sides, their filler caps and access panels.
    for s in (-1, 1):
        prof = lambda y, w: [(s * 1.38, y, .98), (s * (1.38 + w * .65), y, .99), (s * (1.38 + w * .97), y, 1.18),
                             (s * (1.38 + w), y, 1.55), (s * (1.38 + w * .85), y, 1.92), (s * 1.38, y, 2.02)]
        rings = [prof(-4.35, .05), prof(-4.0, .38), prof(-3.5, .56), prof(4.2, .56), prof(4.8, .4), prof(5.25, .06)]
        k.sharp_loft(a.part('Sponsons', 'Team'), rings, chamfer=.03)
        for y in (-2.5, -.2, 2.2):
            K.panel(a, a.part('Sponson_panels', 'Armor'), (1.1, .4), (s * 1.95, y, 1.5), (s, 0, 0), t=.02, rivet=.25,
                    r=.012, seg=4)
        a.part('Filler_caps', 'Steel').cyl(.07, .04, loc=(s * 1.75, 3.4, 2.0), seg=8, bevel=0)
        K.rivet_line(rv, (s * 1.95, -3.4, 1.15), (s * 1.95, 4.1, 1.15), (s, 0, -.3), pitch=.3, r=.013, h=.013, seg=4)
    # The ramp, closed: its panel, the hinges, ribs, the tail lights.
    ramp = a.part('Ramp', 'Armor')
    ang = math.atan2(2.3 - 1.3, 8.4 - 6.2)
    d = Vector((0, math.cos(ang), math.sin(ang)))
    o = Vector((0, 6.25, 1.27))
    k.block(ramp, (2.3, 2.35, .06), loc=tuple(o + d * 1.17 - Vector((0, 0, .04))), rot=(ang, 0, 0), chamfer=.015)
    for x in (-.9, .9):
        a.part('Kit_hinges', 'Steel').cyl(.06, .3, loc=(x, 6.25, 1.22), rot=(0, R90, 0), seg=8, bevel=0)
    for j in range(5):
        a.part('Ramp_ribs', 'Steel').box((2.0, .05, .03), loc=tuple(o + d * (.35 + j * .42) - Vector((0, 0, .08))),
                                          rot=(ang, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lights', 'LavaGlow').box((.08, .04, .08), loc=(s * 1.12, 8.73, 3.0), bevel=0)


def _hp_nose(a):
    """The nose fittings: the FLIR turret under the chin, the in-flight refuelling probe along the right side, the pitot
    tubes, the missile-approach sensors, the search light, the steps up to the cockpit."""
    k.lathe(a.part('Sensor_mount', 'Armor'), [(.24, 0), (.24, .12), (.18, .2)], loc=(0, -8.15, .95), rot=(math.pi, 0, 0),
            seg=12)
    a.part('Sensor', 'Armor').sphere(.26, loc=(0, -8.2, .68), seg=14, rings=8)
    a.part('Sensor_glass', 'Glass').box((.2, .04, .16), loc=(0, -8.45, .66), bevel=0)
    # The refuelling probe (right side): the boom on its brackets, the nozzle.
    pr = a.part('Refuel_probe', 'Steel')
    p0, p1 = Vector((-1.2, -6.4, 2.35)), Vector((-.97, -9.75, 2.26))
    pr.tube([tuple(p0), tuple(p1)], .07, seg=10)
    k.lathe(pr, [(.07, 0), (.11, .08), (.06, .25), (0, .27)], loc=tuple(p1), rot=K.FORWARD, seg=10)
    for f in (.0, .28):
        b = p0.lerp(p1, f)
        pr.limb(tuple(b), (-1.38 if f == 0 else -1.2, b.y, b.z - .05), .05, .05, bevel=0)
    a.part('Probe_tip', 'Hazard').cyl(.075, .25, loc=tuple(p0.lerp(p1, .9)), rot=(R90, 0, -math.atan2(.25, 3.7)),
                                      seg=10, bevel=0)
    for s in (-1, 1):
        a.part('Pitot', 'Steel').limb((s * .5, -8.35, 2.6), (s * .55, -9.0, 2.62), .025, .025, bevel=0)
        a.part('Maws', 'Glass').sphere(.07, loc=(s * .95, -8.2, 1.4), seg=8, rings=4)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.38, -7.6, 1.15), (s * 1.38, -7.2, 1.15), (s, 0, 0), h=.05)
        a.part('Steps', 'Steel').box((.12, .3, .03), loc=(s * 1.36, -7.0, .85), bevel=0)
    K.lamp(a, (.45, -8.2, .95), (0, -1, -.4), r=.12, guard=False)


def _hp_pylons(a):
    """The two rotor pylons: the low forward one over the cockpit, the tall aft one; the drive-shaft tunnel along the
    roof with its access panels and handholds, the two T55-class engines on the aft pylon's sides (intake screens,
    the IR suppressors turning the exhaust up), the APU exhaust, the IR jammer, the beacon, antennas."""
    team = a.part('Fuselage', 'Team')
    k.sharp_loft(team, [[(-.85, -7.4, 3.3), (.85, -7.4, 3.3), (.9, -4.2, 3.4), (-.9, -4.2, 3.4)],
                        [(-.7, -7.0, 3.95), (.7, -7.0, 3.95), (.72, -4.6, 4.0), (-.72, -4.6, 4.0)],
                        [(-.5, -6.5, 4.3), (.5, -6.5, 4.3), (.5, -5.1, 4.32), (-.5, -5.1, 4.32)]], chamfer=.06)
    k.sharp_loft(team, [[(-1.05, 4.5, 3.4), (1.05, 4.5, 3.4), (1.05, 8.5, 3.5), (-1.05, 8.5, 3.5)],
                        [(-.85, 5.2, 4.6), (.85, 5.2, 4.6), (.85, 8.3, 4.65), (-.85, 8.3, 4.65)],
                        [(-.55, 5.8, 5.32), (.55, 5.8, 5.32), (.55, 7.7, 5.34), (-.55, 7.7, 5.34)]], chamfer=.06)
    tun = a.part('Tunnel', 'Team')
    k.block(tun, (.62, 9.2, .3), loc=(0, .15, 3.55), chamfer=.05)
    pnl = a.part('Tunnel_panels', 'Undercarriage')
    for i in range(8):
        pnl.box((.5, .02, .04), loc=(0, -4.0 + i * 1.15, 3.71), bevel=0)
    for s in (-1, 1):
        for y in (-6.5, -5.2):
            K.grille(a, (s * .72, y, 3.9), .55, .3, facing=(s, 0, .3), slats=3, frame_mat='Armor')
        K.grille(a, (s * .9, 6.8, 4.55), 1.1, .5, facing=(s, 0, .2), slats=4, frame_mat='Armor')
        a.part('Kit_cables', 'Rubber').tube([(s * .33, -4.3, 3.62), (s * .33, 0, 3.66), (s * .33, 4.4, 3.62)], .025,
                                            seg=4)
        K.handle(a.part('Kit_handles', 'Steel'), (s * .31, -2.0, 3.71), (s * .31, -1.0, 3.71), (0, 0, 1), h=.05)
    # Engines.
    for s in (-1, 1):
        ex, ey, ez = s * 1.3, 6.3, 4.05
        k.lathe(a.part('Engines', 'Team'), [(.1, -1.35), (.42, -1.25), (.47, -.85), (.47, .7), (.4, 1.0), (.33, 1.2)],
                loc=(ex, ey, ez), rot=(-R90, 0, 0), seg=16, worn=(2,))
        a.part('Intake_screens', 'Undercarriage').cyl(.4, .03, loc=(ex, ey - 1.26, ez), rot=K.FORWARD, seg=16, bevel=0)
        a.part('Intake_rings', 'Steel').torus(.42, .03, loc=(ex, ey - 1.27, ez), rot=(R90, 0, 0), seg=16, ring=4)
        a.part('Engine_bands', 'Steel').cyl(.48, .06, loc=(ex, ey - .2, ez), rot=K.FORWARD, seg=16, bevel=0)
        sup = a.part('Ir_suppressors', 'Steel')
        sup.tube([(ex, ey + 1.15, ez), (ex, ey + 1.55, ez + .1), (ex + s * .1, ey + 1.8, ez + .45)], .27, seg=12)
        a.part('Exhaust_soot', 'Charred').cyl(.24, .04, loc=(ex + s * .1, ey + 1.83, ez + .5), rot=(-.9, 0, 0),
                                              seg=12, bevel=0)
        K.soot(a, (ex, ey + 1.9, ez + .6), radius=.7, k=.45)
        a.part('Engine_mounts', 'Steel').box((.35, .9, .22), loc=(s * .9, ey, ez - .25), bevel=0)
        K.rivet_line(a.part('Kit_rivets', 'Steel'), (ex + s * .45, ey - .8, ez), (ex + s * .45, ey + .6, ez), (s, 0, 0),
                     pitch=.18, r=.012, h=.012, seg=4)
    # The IR jammer on the aft pylon's rear, the beacon, antennas and blade aerials.
    k.lathe(a.part('Ir_jammer', 'Armor'), [(.16, 0), (.16, .12), (.13, .14)], loc=(0, 8.25, 5.0), seg=10)
    a.part('Ir_jammer_glass', 'Glass').sphere(.14, loc=(0, 8.25, 5.2), seg=10, rings=5)
    K.beacon(a, (0, 1.5, 3.72), r=.08)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.25, -2.6, 3.72), h=.7, lean=.3)
    for y in (-3.4, 2.4):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, 3.71), h=.22, chord=.18)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -2.0, .94), h=.2, chord=.16, normal=(0, 0, -1))
    a.part('Apu_exhaust', 'Charred').cyl(.1, .1, loc=(-.4, 8.5, 4.4), rot=K.BACKWARD, seg=8, bevel=0)


def _hp_rotor(a, pivot, prefix, R, chord, phase, blades=3):
    """A three-blade rotor under its pivot: the hub with its arms and droop stops, the pitch links and swashplate,
    the blades lofted from an airfoil with a root cuff and the tip caps. One material per runtime-prefixed name."""
    hub = a.part(f'{prefix}_hub', 'Steel', pivot)
    k.lathe(hub, [(.1, -.55), (.18, -.5), (.22, -.3), (.36, -.25), (.42, -.12), (.46, 0), (.46, .12), (.3, .2),
                  (.12, .3), (0, .32)], seg=16, worn=(4, 5))
    k.lathe(hub, [(.36, -.42), (.44, -.4), (.44, -.34), (.36, -.32)], seg=16)
    grips = a.part(f'{prefix}_grips', 'Armor', pivot)
    blade = a.part(f'{prefix}_blades', 'Armor', pivot)
    tips = a.part(f'{prefix}_tips', 'Hazard', pivot)
    links = a.part(f'{prefix}_links', 'Undercarriage', pivot)
    for j in range(blades):
        u = phase + j * TAU / blades
        c, s_ = math.cos(u), math.sin(u)
        rot = Matrix.Rotation(u, 4, 'Z')
        k.block(grips, (1.1, .32, .16), loc=(c * .9, s_ * .9, .03), rot=(0, 0, u), chamfer=.03)
        grips.cyl(.12, .3, loc=(c * 1.35, s_ * 1.35, .03), rot=(0, R90, u), seg=10, bevel=0)
        links.limb((c * .55 - s_ * .18, s_ * .55 + c * .18, -.38), (c * .7 - s_ * .2, s_ * .7 + c * .2, -.02), .035,
                   .035, bevel=0)
        rings = []
        for r_, ch, t, twist in ((1.4, chord * .7, .16, .12), (1.9, chord, .12, .1), (R * .5, chord, .1, .05),
                                 (R - .5, chord * .95, .09, 0.0), (R - .05, chord * .8, .08, -.02)):
            ring = []
            for fu, fv in K.FOIL:
                yy = -ch * .25 + ch * (1 - fu) / 2 * 1.0 - ch * .25
                zz = fv * t * ch * .5
                yy, zz = yy * math.cos(twist) - zz * math.sin(twist), yy * math.sin(twist) + zz * math.cos(twist)
                ring.append(tuple(rot @ Vector((r_, yy, zz + .03 - r_ * .008))))
            rings.append(ring)
        blade.loft(rings, bevel=0)
        tip_rings = []
        for r_ in (R - .45, R):
            ring = []
            for fu, fv in K.FOIL:
                ch = chord * (.95 if r_ < R else .78)
                yy = -ch * .5 + ch * (1 - fu) / 2
                ring.append(tuple(rot @ Vector((r_ + .005, yy, fv * .09 * ch * .5 + .035 - r_ * .008))))
            tip_rings.append(ring)
        tips.loft(tip_rings, bevel=0)
    k.lathe(a.part(f'{prefix}_swash', 'Steel', pivot), [(.0, -.48), (.38, -.48), (.38, -.42), (.26, -.38), (0, -.38)],
            seg=16)


def _hp_rotors(a):
    r = a.pivot('Rotor', (0, -5.8, 4.62))
    _hp_rotor(a, r, 'Rotor', 7.6, .64, R90)
    rr = a.pivot('Rotor_rear', (0, 6.7, 5.68))
    _hp_rotor(a, rr, 'Rotor_rear', 7.6, .64, -R90)
    # The masts under the hubs (static, on the pylons).
    for y, z0, z1 in ((-5.8, 4.3, 4.1), (6.7, 5.33, 5.15)):
        k.lathe(a.part('Masts', 'Steel'), [(.22, 0), (.2, .25), (.14, .3)], loc=(0, y, z0 - .02), seg=12)


def _hp_wings(a):
    """The stub wings (an attack helicopter's, as on the Mi-24): the anhedral wing panels from the sponson tops, the
    root fairings, panel lines, wing fences, the three stations each side with their pylons and ejector racks, the
    wingtip end plates and navigation lights."""
    w = HP_WING
    wing = a.part('Wings', 'Team')
    K.wing(wing, w['root'], w['tip'], w['span'], x0=w['x0'], z=w['z'], t=.16, dihedral=-w['anhedral'])
    for s in (-1, 1):
        # Root fairing blending the wing into the sponson and fuselage side.
        k.sharp_loft(a.part('Wing_fairings', 'Team'), [
            [(s * 1.38, -1.2, 2.0), (s * 1.38, 1.4, 2.0), (s * 1.38, 1.4, 2.42), (s * 1.38, -1.2, 2.4)],
            [(s * 1.75, -1.0, 2.08), (s * 1.75, 1.25, 2.08), (s * 1.75, 1.25, 2.37), (s * 1.75, -1.0, 2.36)]],
            chamfer=.03)
        pl = a.part('Wing_panels', 'Undercarriage')
        for x in (2.0, 2.75, 3.6):
            z = _hp_wing_z(x)
            pl.box((.02, 1.7, .02), loc=(s * x, .1, z + .13), rot=(0, s * w['anhedral'], 0), bevel=0)
        for y in (-.3, .65):
            x0, x1 = 1.9, 4.2
            pl.box((x1 - x0, .02, .02), loc=(s * (x0 + x1) / 2, y, _hp_wing_z((x0 + x1) / 2) + .13),
                   rot=(0, s * w['anhedral'], 0), bevel=0)
        # Wing fences at mid span, the wingtip end plate with its nav light.
        xf = 3.65
        k.extrude(a.part('Wing_fences', 'Armor'), [(-1.05, -.05), (.75, -.05), (.8, .18), (-.85, .22)], .03,
                  loc=(s * xf, .05, _hp_wing_z(xf)), rot=(0, s * w['anhedral'], 0), axis='X', chamfer=0)
        xt = w['x0'] + w['span']
        zt = _hp_wing_z(xt)
        k.extrude(a.part('Wing_tips', 'Armor'), [(-.95, -.55), (.75, -.55), (.6, .22), (-.7, .2)], .05,
                  loc=(s * (xt + .02), .05, zt), axis='X', chamfer=.01)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .16, .07),
                                                                         loc=(s * (xt + .06), -.85, zt + .05), bevel=0)
        a.part('Wing_lights', 'Lamp').box((.05, .1, .05), loc=(s * (xt + .06), .7, zt + .12), bevel=0)
        # Pylons at the inner and middle stations (sway braces, the ejector rack shoes).
        for xs in HP_STATIONS[:2]:
            z = _hp_wing_z(xs)
            k.extrude(a.part('Pylons', 'Armor'), [(-.75, 0), (.65, 0), (.55, -.32), (-.6, -.32)], .14,
                      loc=(s * xs, .05, z - .08), axis='X', chamfer=.02)
            rack = a.part('Racks', 'Steel')
            rack.box((.12, .9, .06), loc=(s * xs, .0, z - .43), bevel=0)
            for e in (-1, 1):
                rack.limb((s * xs - .1, e * .35, z - .4), (s * xs - .22, e * .35, z - .55), .03, .03, bevel=0)
                rack.limb((s * xs + .1, e * .35, z - .4), (s * xs + .22, e * .35, z - .55), .03, .03, bevel=0)


def _hp_gun_pods(a):
    """The inner stations: a turreted 30 mm gun pod each side (M230 in a chin-style turret under the pod's nose, as on
    the Apache, the pod's feed carrying 300 rounds): the pod body with its access door and vents, the turret on its
    yaw pivot (Mount_gun left, .001 right), the barrel (Gun_barrels / _001 kick back), the flash suppressor,
    Muzzle_gun at the mouth. The data limits each gun's arc to its own side (CHANGES)."""
    for i, s in ((0, 1), (1, -1)):
        x = s * HP_STATIONS[0]
        z = _hp_wing_z(HP_STATIONS[0]) - .9
        tg = '' if i == 0 else '_001'
        pod = a.part('Gun_pods', 'Team')
        k.lathe(pod, [(0, -1.25), (.12, -1.2), (.24, -1.0), (.29, -.6), (.3, .6), (.27, .95), (.18, 1.15), (0, 1.2)],
                loc=(x, .05, z), rot=K.BACKWARD, seg=16, worn=(3,))
        a.part('Gun_pod_doors', 'Armor').box((.02, .9, .3), loc=(x + s * .3, .2, z), bevel=0)
        K.grille(a, (x, .7, z - .29), .3, .4, facing=(0, 0, -1), slats=3)
        a.part('Gun_pod_bands', 'Steel').cyl(.305, .05, loc=(x, -.45, z), rot=K.FORWARD, seg=16, bevel=0)
        m = a.pivot(K.name('Mount_gun', i), (x, -1.05, z - .32))
        k.lathe(a.part(f'Gun_turret{tg}', 'Armor', m), [(.2, .14), (.24, .05), (.25, -.08), (.2, -.2), (0, -.24)],
                seg=14)
        k.block(a.part(f'Gun_cradle{tg}', 'Armor', m), (.18, .5, .2), loc=(0, -.25, -.12), chamfer=.03)
        a.part(f'Gun_feed{tg}', 'Steel', m).tube([(.12, .1, -.05), (.18, -.15, -.12), (.1, -.35, -.14)], .04, seg=6)
        k.lathe(a.part(f'Gun_barrels{tg}', 'Steel', m), [(.055, 0), (.055, .4), (.045, .45), (.045, 1.55),
                                                         (.04, 1.6)], loc=(0, -.45, -.14), rot=K.FORWARD, seg=10)
        k.lathe(a.part(f'Gun_muzzles{tg}', 'Steel', m), [(.04, -.01), (.06, 0), (.06, .18), (.045, .2), (0, .2)],
                loc=(0, -2.05, -.14), rot=K.FORWARD, seg=10)
        a.pivot(K.name('Muzzle_gun', i), (0, -2.27, -.14), K.name('Mount_gun', i))
        K.tone(a, K.name('Mount_gun', i), k=.9)


def _hp_rocket_pods(a):
    """The middle stations: a 20-tube 80 mm rocket pod each side (B-8M1 class: the gunship's S-8s) on its part node
    (Part_pod left, Part_pod.001 right; Pods: the rounds leave from both pods in turn), the faired nose ring, the
    tube mouths on the face, the bands, Muzzle_rocket at the face."""
    for i, s in ((0, 1), (1, -1)):
        x = s * HP_STATIONS[1]
        z = _hp_wing_z(HP_STATIONS[1]) - .9
        p = a.pivot(K.name('Part_pod', i), (x, .1, z))
        k.lathe(a.part('Pods', 'Team', p), [(0, -.97), (.31, -.97), (.36, -.92), (.36, .75), (.3, .95), (.12, 1.05),
                                            (0, 1.07)], rot=K.BACKWARD, seg=18, worn=(2,))
        k.lathe(a.part('Pod_rings', 'Steel', p), [(.3, -1.0), (.375, -1.0), (.375, -.92), (.3, -.92)], rot=K.BACKWARD,
                seg=18, caps=(False, False))
        face = a.part('Pod_tubes', 'Undercarriage', p)
        holes = [(0, 0)] + [(math.cos(j * TAU / 6) * .11, math.sin(j * TAU / 6) * .11) for j in range(6)] + \
            [(math.cos(j * TAU / 13 + .2) * .24, math.sin(j * TAU / 13 + .2) * .24) for j in range(13)]
        for hx, hz in holes:
            face.cyl(.042, .02, loc=(hx, -.975, hz), rot=K.FORWARD, seg=8, bevel=0)
        for f in (-.45, .5):
            a.part('Pod_bands', 'Steel', p).cyl(.365, .06, loc=(0, f, 0), rot=K.FORWARD, seg=18, bevel=0)
        a.part('Pod_hazard', 'Hazard', p).cyl(.362, .04, loc=(0, -.7, 0), rot=K.FORWARD, seg=18, bevel=0)
        a.pivot(K.name('Muzzle_rocket', i), (0, -1.03, 0), K.name('Part_pod', i))
        K.tone(a, K.name('Part_pod', i), k=.92)


def _hp_missiles(a):
    """The wingtip launchers: four 9M120 Ataka-class tubes each side (two rows of two) under the end plates, on one
    part node (Part_missiles: the data's "missiles"); Launch_tubes: the rounds leave from the left and right
    launchers in turn, Muzzle_missile on the centre line level with their mouths. Each tube: the container with its
    front and rear rings, the bore, the frangible cap's rim."""
    xt = HP_WING['x0'] + HP_WING['span']
    zt = _hp_wing_z(xt)
    zc = zt - .45
    p = a.pivot('Part_missiles', (0, -.1, zc))
    L, r = 1.9, .1
    for s in (-1, 1):
        cx = s * (xt - .14)
        beam = a.part('Launcher_beams', 'Team', p)
        k.block(beam, (.36, 1.7, .16), loc=(cx, .05, .3), chamfer=.03)
        a.part('Launcher_beams', 'Team', p).box((.06, 1.2, .3), loc=(cx, .0, .38), bevel=0)
        tubes = a.part('Launch_tubes', 'Armor', p)
        rings = a.part('Launch_rings', 'Steel', p)
        bore = a.part('Launch_bores', 'Undercarriage', p)
        for dx in (-.12, .12):
            for dz in (.1, -.12):
                c = (cx + dx, -.1, dz)
                tubes.cyl(r, L, loc=c, rot=K.FORWARD, seg=12, bevel=0)
                for f in (-1, 1):
                    rings.cyl(r + .018, .08, loc=(c[0], c[1] + f * (L / 2 - .04), dz), rot=K.FORWARD, seg=12, bevel=0)
                bore.cyl(r * .8, .02, loc=(c[0], c[1] - L / 2 - .002, dz), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Launch_straps', 'Steel', p).box((.52, .06, .5), loc=(cx, .35, 0), bevel=0)
        a.part('Launch_hazard', 'Hazard', p).box((.52, .05, .06), loc=(cx, -.6, .25), bevel=0)
    a.pivot('Muzzle_missile', (0, -.1 - L / 2 - .03, 0), 'Part_missiles')
    K.tone(a, 'Part_missiles', k=.92)


def _hp_door_guns(a):
    """The forward door miniguns (Mount_mg left, .001 right: the data's two boss_minigun) on swing arms in the open
    doors: the pintle, the M134 body and motor, the six-barrel cluster with its clamp (Minigun_barrels / _001), the
    spade grips, the feed chute into the cabin; and the aft window guns (Mount_mg.002 / .003: the data's two
    boss_hmg) on their brackets."""
    for i, s in ((0, 1), (1, -1)):
        tg = '' if i == 0 else '_001'
        arm = a.part('Door_gun_arms', 'Steel')
        arm.limb((s * 1.38, -4.6, 1.62), (s * 1.6, -4.6, 1.62), .07, .07, bevel=0)
        m = a.pivot(K.name('Mount_mg', i), (s * 1.62, -4.6, 1.7))
        k.lathe(a.part(f'Minigun_pintle{tg}', 'Steel', m), [(.06, -.08), (.06, .2), (.08, .22), (.08, .3)], seg=8)
        body = a.part(f'Minigun_body{tg}', 'Armor', m)
        k.block(body, (.18, .5, .2), loc=(0, .05, .4), chamfer=.03)
        body.cyl(.07, .3, loc=(.12, .15, .42), rot=K.FORWARD, seg=8, bevel=0)
        bar = a.part(f'Minigun_barrels{tg}', 'Steel', m)
        for j in range(6):
            u = j * TAU / 6
            bar.cyl(.017, .8, loc=(math.cos(u) * .045, -.6, .42 + math.sin(u) * .045), rot=K.FORWARD, seg=4, bevel=0)
        bar.cyl(.07, .05, loc=(0, -.45, .42), rot=K.FORWARD, seg=10, bevel=0)
        bar.cyl(.07, .04, loc=(0, -.95, .42), rot=K.FORWARD, seg=10, bevel=0)
        a.part(f'Minigun_grips{tg}', 'Rubber', m).limb((-.06, .3, .45), (-.06, .42, .35), .03, .03, bevel=0)
        a.part(f'Minigun_grips{tg}', 'Rubber', m).limb((.06, .3, .45), (.06, .42, .35), .03, .03, bevel=0)
        a.part(f'Minigun_feed{tg}', 'Undercarriage', m).tube([(-.09, .1, .38), (-.35 * s, .25, .2),
                                                              (-.4 * s, .3, -.05)], .045, seg=6)
        a.pivot(K.name('Muzzle_mg', i), (0, -1.02, .42), K.name('Mount_mg', i))
    for i, s in ((2, 1), (3, -1)):
        a.part('Hmg_brackets', 'Steel').limb((s * 1.4, 3.2, 1.95), (s * 1.62, 3.2, 1.95), .06, .06, bevel=0)
        K.pintle_mg(a, None, (s * 1.62, 3.2, 1.98), index=i, scale=1.35, shield=False, length=1.15, post=.12)


def _hp_gear_and_kit(a):
    """The fixed landing gear (twin-wheel front legs, single rear legs with their oleos and drag struts), the
    flare dispensers on the aft sponsons, the chaff, the hoist over the door, fire extinguisher access, lifting
    points, the tail markings."""
    gear = a.part('Gear', 'Steel')
    for s in (-1, 1):
        for y, twin in ((-3.95, True), (4.95, False)):
            x = s * 1.75
            gear.tube([(s * 1.5, y, 1.1), (x, y, .62), (x, y, .36)], .07, seg=8)
            gear.limb((s * 1.42, y + .5, 1.05), (x, y + .02, .65), .05, .05, bevel=0)
            k.lathe(a.part('Gear_oleos', 'Undercarriage'), [(.09, 0), (.09, .25), (.075, .27)], loc=(x, y, .5),
                    seg=8)
            for dx in ((-.17, .17) if twin else (0,)):
                c = (x + dx, y, .32)
                k.lathe(a.part('Tyres', 'Rubber'), [(.16, -.08), (.3, -.075), (.32, -.04), (.32, .04), (.3, .075),
                                                    (.16, .08)], loc=c, rot=(0, R90, 0), seg=16)
                a.part('Gear_hubs', 'Steel').cyl(.16, .17, loc=c, rot=(0, R90, 0), seg=10, bevel=0)
            a.part('Gear', 'Steel').cyl(.04, (.5 if twin else .2), loc=(x, y, .32), rot=(0, R90, 0), seg=6, bevel=0)
        K.flare_dispenser(a, (s * 1.97, 3.6, 1.45), normal=(s, 0, -.25), cols=3, rows=2, cell=.07)
        K.flare_dispenser(a, (s * 1.97, 4.0, 1.45), normal=(s, 0, -.25), cols=3, rows=2, cell=.07)
        for y in (-5.6, 5.6):
            K.hd.lifting_eye(a.part('Lifting_eyes', 'Steel'), (s * .6, y, 3.48 if y < 0 else 3.5), yaw=0, size=.12)
    # The rescue hoist boom over the right door.
    hz = a.part('Hoist', 'Armor')
    k.block(hz, (.3, .7, .25), loc=(-1.3, -4.6, 3.3), chamfer=.03)
    hz.limb((-1.3, -4.6, 3.3), (-1.75, -4.6, 3.15), .1, .1, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(-1.75, -4.6, 3.1), (-1.75, -4.6, 2.85)], .012, seg=4)
    # Tail markings and the fin flash in the faction's colour (no national insignia).
    for s in (-1, 1):
        a.part('Tail_marks', 'Hazard').box((.015, .8, .35), loc=(s * 1.365, 7.4, 3.0), bevel=0)


def _hp_detail(a):
    """Third-tier kit for the boss's close shots: the three cargo hooks under the belly, the belly lights and
    aerials, seam lines along the sides, the formation-light strips on the pylons, kick steps up the aft pylon,
    static dischargers, the mirrors by the cockpit, extra IR jammers on the sponson tails, armour plates on the
    sponson noses, the fuel dump pipe."""
    hk = a.part('Cargo_hooks', 'Steel')
    for y, r in ((-1.6, .12), (0.0, .18), (1.6, .12)):
        k.block(a.part('Hook_housings', 'Armor'), (.5, .5, .12), loc=(0, y, .9), chamfer=.03)
        hk.limb((0, y, .86), (0, y + .05, .55), .05, .07, bevel=0)
        hk.torus(r * .6, .03, loc=(0, y + .05, .5), rot=(0, R90, 0), seg=10, ring=4)
    K.beacon(a, (0, 3.2, .92), r=.08)
    for y in (-3.0, 2.6):
        K.blade_antenna(a.part('Antennas', 'Steel'), (.4, y, .94), h=.18, chord=.14, normal=(0, 0, -1))
    seams = a.part('Seams', 'Undercarriage')
    for s in (-1, 1):
        for z in (2.12, 2.92):
            seams.box((.012, 11.4, .014), loc=(s * 1.427, -.7, z), bevel=0)
        # Formation light strips on the pylons' sides, kick steps up the aft pylon, static dischargers.
        for y0, y1, z in ((-6.9, -5.3, 3.75), (5.4, 7.8, 4.25)):
            a.part('Formation_lights', 'Lamp').box((.012, y1 - y0, .05), loc=(s * (.82 if y0 < 0 else .99),
                                                                              (y0 + y1) / 2, z), bevel=0)
        for j in range(4):
            a.part('Kick_steps', 'Undercarriage').box((.02, .22, .08), loc=(s * (1.02 - j * .045), 8.0,
                                                                            3.65 + j * .38), bevel=0)
        for y in (7.6, 8.0):
            a.part('Dischargers', 'Steel').limb((s * .5, y, 5.3), (s * .55, y + .25, 5.4), .012, .012, bevel=0)
        K.mirror(a.part('Mirrors', 'Steel'), (s * 1.3, -7.95, 2.95), s, arm=.3, size=(.14, .03, .2))
        # IR jammer pods on the sponson tails, armour on the sponson noses.
        k.lathe(a.part('Ir_jammer', 'Armor'), [(.13, 0), (.13, .1), (.1, .12)], loc=(s * 1.75, 4.95, 2.0), seg=10)
        a.part('Ir_jammer_glass', 'Glass').sphere(.11, loc=(s * 1.75, 4.95, 2.16), seg=10, rings=5)
        K.armour_plate(a, a.part('Sponson_armour', 'Armor'), (.55, .6, .04), (s * 1.73, -3.95, 1.5),
                       rot=(0, s * R90, -s * .9), rivet=.2)
    a.part('Fuel_dump', 'Steel').tube([(1.95, 4.6, 1.05), (2.0, 5.1, .95), (2.0, 5.4, .9)], .035, seg=6)


def mega_gunship(a):
    """Harpy, redrawn: Quaden's heavy tandem-rotor gunship (a Chinook airframe armed as the ACH-47 "Guns-A-Go-Go",
    with Mi-24-style stub wings on the sponsons that carry its guns and launchers, owner's note). Runtime (the def's
    parts and secondary list): Rotor / Rotor_rear (rotor_rear), Mount_gun / .001 + Muzzle_gun / .001 (gun_l / gun_r:
    the turreted 30 mm pods under the inner stations), Part_pod / .001 + Muzzle_rocket / .001 (pod_l / pod_r: the
    rocket pods), Part_missiles + Muzzle_missile (missiles: the wingtip launchers), Mount_mg / .001 (minigun_l / _r:
    the door miniguns), Mount_mg.002 / .003 (the aft window HMGs); mb_flare_mounts adds Mount_Flare_* from the
    Flares dispensers. Metres, +Z up, -Y front, +X left."""
    K.suffixed(a)
    _hp_fuselage(a)
    _hp_nose(a)
    _hp_pylons(a)
    _hp_rotors(a)
    _hp_wings(a)
    _hp_gun_pods(a)
    _hp_rocket_pods(a)
    _hp_missiles(a)
    _hp_door_guns(a)
    _hp_gear_and_kit(a)
    _hp_detail(a)
    k.clean(a)


# ============================================================================= daedalus
# Aurel's orbital assault ship (an Acclamator-class read: the arrowhead hull, the hard chine, the stepped
# superstructure aft), redrawn at 5 x the boss budget. The hull: a closed loft through stations of a half outline
# (keel up to the chine, the upper slopes with the terrace lip, the spine); its size and every runtime node at the
# old file's places.
DY0, DY1 = -18.5, 15.6        # nose / stern


def _dd_w(y):
    return .6 + (10.0 - .6) * (y - DY0) / (DY1 - DY0)


def _dd_t(y):
    return min(2.7, .32 + (y - DY0) * .16)


def _dd_b(y):
    return max(-2.6, -.32 - (y - DY0) * .16)


# The half outline as (fraction of the half width, fraction of the bottom / top depth): keel, belly, lower flank,
# the chine, the upper flank, the terrace lip (a step), the upper deck, the spine.
DD_LOW = [(0, 1.0), (.5, .98), (.75, .8), (.93, .3), (1.0, 0.0)]
DD_UP = [(1.0, 0.0), (.965, .1), (.77, .58), (.71, .6), (.69, .66), (.4, .94), (.15, 1.0), (0, 1.03)]


def _dd_half(y):
    w, t, b = _dd_w(y), _dd_t(y), _dd_b(y)
    return [(fx * w, fz * b) for fx, fz in DD_LOW] + [(fx * w, fz * t) for fx, fz in DD_UP[1:]]


def _dd_surface(x, y, top=True):
    """The hull's height at (x, y): on the upper skin (top) or the belly."""
    w = _dd_w(y)
    f = min(1.0, abs(x) / w)
    prof = DD_UP if top else DD_LOW
    k_ = _dd_t(y) if top else _dd_b(y)
    pts = sorted(prof, key=lambda p: p[0])
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        if x0 <= f <= x1:
            u = 0 if x1 == x0 else (f - x0) / (x1 - x0)
            return (z0 + (z1 - z0) * u) * k_
    return 0.0


def _dd_hull(a):
    """The hull skin (upper: Plaster, keel: Armor, one closed loft split at the chine by material), the chine band
    with its trench windows, the Aurel stripes along the chine, the spine ridge with its lights, the bow cap."""
    ys = [DY0, -17.0, -15.0, -12.5, -10.0, -7.5, -5.0, -2.5, 0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 14.5, DY1]
    up = a.part('Upper_hull', 'Plaster')
    low = a.part('Keel', 'Concrete')
    urings, lrings = [], []
    for y in ys:
        w, t, b = _dd_w(y), _dd_t(y), _dd_b(y)
        right = [(fx * w, y, fz * t) for fx, fz in DD_UP]
        urings.append(right + [(-x, yy, z) for x, yy, z in reversed(right[:-1])])
        rl = [(fx * w, y, fz * b) for fx, fz in reversed(DD_LOW)]
        lrings.append(rl + [(-x, yy, z) for x, yy, z in reversed(rl[:-1])])
    up.loft(urings, bevel=0)
    low.loft(lrings, bevel=0)
    # The chine band: a dark recessed trench along both flanks with lit windows and fittings in it.
    tr = a.part('Chine_trench', 'Undercarriage')
    win = a.part('Trench_windows', 'Lamp')
    fit = a.part('Trench_fittings', 'Steel')
    ang = math.atan((10.0 - .6) / (DY1 - DY0))
    for s in (-1, 1):
        for i in range(17):
            y0 = -16.5 + i * 1.9
            y1 = y0 + 1.75
            yc = (y0 + y1) / 2
            w = _dd_w(yc)
            tr.box((.06, 1.75, .34), loc=(s * (w + .02), yc, .03), rot=(0, 0, -s * ang), bevel=0)
            if i % 2 == 0:
                win.box((.03, 1.1, .07), loc=(s * (w + .055), yc, .08), rot=(0, 0, -s * ang), bevel=0)
            else:
                fit.box((.08, .5, .2), loc=(s * (w + .05), yc - .4, .02), rot=(0, 0, -s * ang), bevel=0)
                fit.box((.08, .3, .14), loc=(s * (w + .05), yc + .45, .02), rot=(0, 0, -s * ang), bevel=0)
        st = a.part('Aurel_stripes', 'Team')
        st.tube([(s * _dd_w(y) * 1.004, y, .27) for y in (DY0 + .4, -10.0, 2.0, DY1 - .1)], .07, seg=4, caps=False)
        st.tube([(s * _dd_w(y) * 1.004, y, -.24) for y in (DY0 + .4, -10.0, 2.0, DY1 - .1)], .07, seg=4, caps=False)
    # The spine ridge with its running lights, the bow cap.
    sp = a.part('Spine', 'Armor')
    for y0, y1 in ((-15.5, -6.0), (-5.6, 4.5)):
        z0, z1 = _dd_t(y0) * 1.03, _dd_t(y1) * 1.03
        sp.limb((0, y0, z0 + .12), (0, y1, z1 + .12), .5, .3, bevel=.04)
    lights = a.part('Spine_lights', 'Lamp')
    for y in range(-14, 4, 2):
        lights.box((.14, .14, .05), loc=(0, y, _dd_t(y) * 1.03 + .3), bevel=0)
    k.lathe(a.part('Bow_cap', 'Armor'), [(0, -.2), (.35, -.1), (.42, .2), (.3, .4)], loc=(0, DY0 + .1, 0),
            rot=K.FORWARD, seg=10)


def _dd_plating(a):
    """The upper hull's plating patchwork in three tones over the slopes and the deck, the panel-line grid, window
    rows along the terrace lip, the hangar-door recesses in the flanks, deck fittings and the radiator rows aft."""
    tones = ('PlasterWhite', 'Concrete', 'Armor', 'Plaster')
    rng = __import__('random').Random(11)
    for i, y in enumerate([v * .5 for v in range(-32, 28)]):
        w, t = _dd_w(y), _dd_t(y)
        for f in (.2, .3, .45, .55, .82):
            if f * w < .9 or rng.random() < .35:
                continue
            z = _dd_surface(f * w, y)
            slope = math.atan2(t * (.94 - .66), w * (.69 - .4)) if f < .69 else math.atan2(t * .58, w * (.965 - .77))
            for s in (-1, 1):
                mat = tones[(i * 3 + int(f * 10) + (s > 0)) % 4]
                L = .35 + rng.random() * .5
                a.part(f'Hull_plates_{mat.lower()}', mat).box((w * .1 + rng.random() * .3, L, .03),
                                                               loc=(s * f * w, y + rng.random() * .2, z + .02),
                                                               rot=(0, -s * slope, 0), bevel=0)
    lines = a.part('Panel_lines', 'Undercarriage')
    for y in range(-16, 15, 2):
        w, t = _dd_w(y), _dd_t(y)
        for s in (-1, 1):
            for f0, f1 in ((.15, .4), (.42, .68)):
                p0 = (s * f0 * w, y, _dd_surface(f0 * w, y) + .012)
                p1 = (s * f1 * w, y, _dd_surface(f1 * w, y) + .012)
                lines.limb(p0, p1, .03, .015, bevel=0)
    for f in (.3, .55):
        for s in (-1, 1):
            pts = [(s * f * _dd_w(y), y, _dd_surface(f * _dd_w(y), y) + .015) for y in (-15.0, -8.0, 0.0, 8.0, 14.5)]
            lines.tube(pts, .012, seg=3, caps=False)
    # Window rows along the terrace lip, both sides.
    win = a.part('Windows', 'Lamp')
    for s in (-1, 1):
        for y in [v * .8 for v in range(-17, 18)]:
            w, t = _dd_w(y), _dd_t(y)
            if w < 2.0:
                continue
            x = .7 * w
            win.box((.04, .45, .07), loc=(s * (x + .015), y, t * .63), rot=(0, 0, -s * .27), bevel=0)
    # Hangar-door recesses in the flanks (under the chine), their frames and lights.
    for s in (-1, 1):
        for y in (-3.5, 3.5):
            w = _dd_w(y)
            x = w * .9
            z = _dd_b(y) * .32
            k.block(a.part('Hangar_doors', 'Undercarriage'), (.06, 2.6, .55), loc=(s * (x + .02), y, z),
                    rot=(0, -s * .7, -s * .27), chamfer=0)
            a.part('Hangar_frames', 'Steel').box((.08, 2.8, .06), loc=(s * (x + .05), y, z + .3),
                                                 rot=(0, -s * .7, -s * .27), bevel=0)
            for e in (-1, 1):
                a.part('Hangar_lights', 'Alloy').box((.06, .1, .1), loc=(s * (x + .06), y + e * 1.35, z),
                                                     rot=(0, -s * .7, -s * .27), bevel=0)
    # Deck fittings forward of the superstructure, the radiator fin rows aft on both sides.
    for s in (-1, 1):
        rad = a.part('Radiators', 'Steel')
        x0 = s * 7.2
        for j in range(9):
            yy = 6.2 + j * .9
            x = x0 + s * j * .2
            z = _dd_surface(abs(x), yy)
            rad.box((.05, .7, .7), loc=(x, yy, z + .32), rot=(0, s * .25, 0), bevel=0)
        a.part('Radiator_rails', 'Armor').box((.15, 8.0, .12), loc=(x0 + s * .8, 9.8, _dd_t(9.8) * .55),
                                              rot=(0, 0, -s * ang_r()), bevel=0)


def ang_r():
    return math.atan((10.0 - .6) / (DY1 - DY0))


DD_TIERS = [((-6.0, 5.2), (-7.2, 15.4), (7.2, 15.4), (6.0, 5.2), 1.0, 3.85, .86),
            ((-5.2, 6.8), (-4.7, 15.2), (4.7, 15.2), (5.2, 6.8), 3.85, 5.05, .88),
            ((-3.2, 8.4), (-2.9, 14.9), (2.9, 14.9), (3.2, 8.4), 5.05, 6.35, .88)]


def _dd_superstructure(a):
    """The stepped superstructure aft (three tiers with sloped walls and window bands), the bridge tower, the wide
    bridge module with its window band, the two sensor dishes on their posts, the comms masts and the APS emitter
    on the bridge roof (Mount_APS)."""
    st = a.part('Hull', 'Plaster')
    for (p0, p1, p2, p3, z0, z1, tp) in DD_TIERS:
        bottom = [p0, p3, p2, p1]
        cx, cy = 0.0, sum(p[1] for p in bottom) / 4
        top = [(cx + (x - cx) * tp, cy + (y - cy) * tp + .25) for x, y in bottom]
        K.slab_loft(st, bottom, top, z0, z1)
        # Window bands on each tier's front wall (leaning back with it), lights at its corners.
        yf = p0[1]
        ytop = cy + (yf - cy) * tp + .25
        th = math.atan2(ytop - yf, z1 - z0)
        zw = z1 - .45
        yw = yf + (ytop - yf) * (zw - z0) / (z1 - z0) - .03
        a.part('Step_windows', 'Lamp').box((abs(p3[0]) * 1.3, .04, .14), loc=(0, yw, zw), rot=(-th, 0, 0), bevel=0)
        for s in (-1, 1):
            a.part('Tier_lights', 'Alloy').box((.12, .12, .08), loc=(s * abs(p3[0]) * .92, yf + .3, z1 + .04),
                                               bevel=0)
    # Tier roofs: inset plates, vents, small structures.
    for s in (-1, 1):
        K.clutter(a, 'Roof_fittings', 'Concrete', s * .6 if s > 0 else -4.3, 4.3 if s > 0 else -.6, 9.4, 14.2, 5.05,
                  10, seed=31 + s, size=(.3, .9), height=(.15, .5))
    # The bridge tower and the bridge.
    k.extrude(a.part('Hull_tower', 'Plaster'), [(-1.0, -1.3), (1.0, -1.3), (1.35, .1), (1.0, 1.35), (-1.0, 1.35),
                                                (-1.35, .1)], 1.5, loc=(0, 10.8, 7.1), axis='Z', chamfer=.06,
              taper=(.88, .9))
    br = a.part('Hull_bridge', 'Armor')
    k.sharp_loft(br, [[(-2.6, 9.4, 7.65), (2.6, 9.4, 7.65), (2.6, 11.2, 7.65), (-2.6, 11.2, 7.65)],
                      [(-2.75, 9.15, 8.15), (2.75, 9.15, 8.15), (2.7, 11.25, 8.15), (-2.7, 11.25, 8.15)],
                      [(-2.35, 9.5, 8.6), (2.35, 9.5, 8.6), (2.3, 11.1, 8.6), (-2.3, 11.1, 8.6)]], chamfer=.05)
    a.part('Bridge_windows', 'Lamp').box((4.6, .04, .16), loc=(0, 9.24, 8.26), rot=(.55, 0, 0), bevel=0)
    for x in (-1.5, -.5, .5, 1.5):
        a.part('Bridge_mullions', 'Armor').box((.05, .06, .2), loc=(x, 9.22, 8.26), rot=(.55, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Bridge_windows', 'Lamp').box((.04, 1.2, .14), loc=(s * 2.72, 10.2, 8.15), bevel=0)
    a.part('Aurel_stripes', 'Team').box((4.72, 1.72, .12), loc=(0, 10.3, 7.72), bevel=0)
    # Dishes on posts, masts and the APS emitter.
    for s in (-1, 1):
        a.part('Dish_posts', 'Steel').cyl(.12, 1.0, loc=(s * 1.75, 10.7, 9.05), seg=8, bevel=0)
        K.dish(a.part('Tower_dishes', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (s * 1.75, 10.7, 9.6), r=.8,
               normal=(s * .6, -.3, 1), seg=18)
    for x, y, h in ((.9, 11.0, 1.4), (-.6, 11.0, 1.0), (0, 9.8, .8)):
        a.part('Masts', 'Steel').cyl(.05, h, loc=(x, y, 8.6 + h / 2), seg=6, bevel=0)
        a.part('Mast_tips', 'BarrelRed').box((.12, .12, .12), loc=(x, y, 8.6 + h), bevel=0)
    a.part('Masts', 'Steel').box((.9, .05, .05), loc=(.9, 11.0, 9.75), bevel=0)
    m = a.pivot('Mount_APS', (0, 10.4, 8.65))
    k.lathe(a.part('Aps_emitter', 'Armor', m), [(.38, 0), (.38, .15), (.22, .3), (0, .33)], seg=12)
    a.part('Aps_glow', 'Energy', m).sphere(.14, loc=(0, -.1, .32), seg=8, rings=4)
    # Comms towers on the first tier with their dishes, the stern vanes.
    for s in (-1, 1):
        x, y, z = s * 4.1, 8.0, 3.85
        k.block(a.part('Comm_towers', 'Plaster'), (.9, .9, 1.6), loc=(x, y, z + .8), chamfer=.06, taper=(.8, .8))
        K.dish(a.part('Tower_dishes', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (x, y, z + 1.9), r=.6,
               normal=(s * .7, -.6, .6), seg=14)
        k.extrude(a.part('Stern_vanes', 'Armor'), [(0, 0), (1.6, 0), (1.9, 2.4), (1.2, 2.4)], .2,
                  loc=(s * 6.0, 14.4, 2.6), rot=(0, -s * .35, 0), axis='X', chamfer=.02)


def _dd_deck_modules(a):
    """The deck between the spine and the terrace lips: rows of low hull modules (two tones, chamfered, varied
    heights) laid along the slope with service gaps between them, vents on some, a few dark hatch recesses: the
    "city" read of a capital ship's upper hull from the battle camera."""
    import random
    rng = random.Random(53)
    tones = (('Deck_modules', 'Plaster'), ('Deck_modules_light', 'PlasterWhite'), ('Deck_modules_grey', 'Concrete'))
    vents = a.part('Deck_vents', 'Undercarriage')
    for s in (-1, 1):
        y = -14.5
        while y < 4.6:
            depth = rng.choice((.7, .9, 1.1, 1.4, 1.8))
            yc = y + depth / 2
            w = _dd_w(yc)
            x = .55
            while True:
                width = rng.choice((.6, .8, 1.0, 1.3, 1.7, 2.1))
                if x + width > .66 * w:
                    break
                if rng.random() < .82:
                    xc = x + width / 2
                    z = _dd_surface(xc + width / 2, yc)
                    h = rng.choice((.12, .18, .25, .32))
                    name, mat = tones[rng.randrange(3)]
                    k.block(a.part(name, mat), (width, depth - .1, h + (_dd_surface(x, yc) - z)),
                            loc=(s * xc, yc, z + (h + (_dd_surface(x, yc) - z)) / 2 - .02), chamfer=.03)
                    top = z + h + (_dd_surface(x, yc) - z) - .02
                    if rng.random() < .3:
                        vents.box((width * .6, .04, .02), loc=(s * xc, yc - depth * .2, top + .01), bevel=0)
                        vents.box((width * .6, .04, .02), loc=(s * xc, yc, top + .01), bevel=0)
                    elif rng.random() < .2:
                        a.part('Deck_hatches', 'Charred').box((width * .5, (depth - .1) * .5, .02),
                                                              loc=(s * xc, yc, top + .01), bevel=0)
                x += width + .08
            y += depth + .12


def _dd_tier_wall(tier, u, v):
    """A point on a tier's right side wall (+X): u along it (0 front, 1 rear), v up it (0 foot, 1 top)."""
    (p0, p1, p2, p3, z0, z1, tp) = tier
    cy = (p0[1] + p1[1] + p2[1] + p3[1]) / 4
    top = lambda p: (p[0] * tp, cy + (p[1] - cy) * tp + .25)  # noqa: E731
    b = Vector((p3[0] + (p2[0] - p3[0]) * u, p3[1] + (p2[1] - p3[1]) * u, z0))
    t0, t1 = top(p3), top(p2)
    t = Vector((t0[0] + (t1[0] - t0[0]) * u, t0[1] + (t1[1] - t0[1]) * u, z1))
    return b.lerp(t, v)


def _dd_tier_kit(a):
    """The superstructure walls' detail: alternating plates on the tier side walls in three tones, window rows
    along them, vent grilles, lights."""
    import random
    rng = random.Random(61)
    for ti, tier in enumerate(DD_TIERS):
        n = (9, 7, 5)[ti]
        v0, v1 = ((.5, .92), (.12, .9), (.12, .9))[ti]
        for s in (-1, 1):
            for j in range(n):
                ua, ub = (j + .06) / n, (j + .94) / n
                c = (_dd_tier_wall(tier, (ua + ub) / 2, (v0 + v1) / 2))
                pa, pb = _dd_tier_wall(tier, ua, v0), _dd_tier_wall(tier, ub, v0)
                qa = _dd_tier_wall(tier, ua, v1)
                along = (pb - pa)
                up = (qa - pa)
                n_out = along.cross(up).normalized()
                if n_out.x < 0:
                    n_out = -n_out
                m = Matrix((along.normalized(), up.normalized(), n_out)).transposed()
                rot = m.to_euler('XYZ')
                mat = ('Concrete', 'PlasterWhite', 'Plaster')[rng.randrange(3)]
                pc = c + n_out * .03
                a.part(f'Tier_plates_{mat.lower()}', mat).box((along.length, up.length, .04),
                                                               loc=(s * pc.x, pc.y, pc.z), rot=(rot.x, -rot.y, -rot.z)
                                                               if s < 0 else tuple(rot), bevel=0)
                if j % 2 == 0:
                    wc = _dd_tier_wall(tier, (ua + ub) / 2, v1 - .08) + n_out * .06
                    a.part('Tier_windows', 'Lamp').box((along.length * .7, .08, .03), loc=(s * wc.x, wc.y, wc.z),
                                                       rot=(rot.x, -rot.y, -rot.z) if s < 0 else tuple(rot), bevel=0)


def _dd_turbolaser(a, x, y, size=1.0):
    """A twin heavy laser turret on the upper hull (decor: the def's lasers fire from the ball guns): the base drum
    on the hull, the faceted house, the two long barrels with their cooling rings and emitter tips."""
    z = _dd_surface(abs(x), y)
    sc = size
    k.lathe(a.part('Turbolaser_bases', 'Armor'), [(.95 * sc, -.4), (.95 * sc, .12), (.85 * sc, .18)], loc=(x, y, z),
            seg=14)
    k.sharp_loft(a.part('Turbolasers', 'Plaster'), [
        [(x - .75 * sc, y - .6 * sc, z + .18), (x + .75 * sc, y - .6 * sc, z + .18), (x + .8 * sc, y + .8 * sc, z + .18),
         (x - .8 * sc, y + .8 * sc, z + .18)],
        [(x - .55 * sc, y - .45 * sc, z + .72 * sc), (x + .55 * sc, y - .45 * sc, z + .72 * sc),
         (x + .6 * sc, y + .7 * sc, z + .72 * sc), (x - .6 * sc, y + .7 * sc, z + .72 * sc)]], chamfer=.05)
    for dx in (-.24, .24):
        bx = x + dx * sc
        k.lathe(a.part('Turbolaser_barrels', 'Steel'), [(.1 * sc, 0), (.1 * sc, .5), (.075 * sc, .55),
                                                         (.07 * sc, 2.0 * sc), (.1 * sc, 2.05 * sc),
                                                         (.1 * sc, 2.25 * sc), (.06 * sc, 2.3 * sc)],
                loc=(bx, y - .4 * sc, z + .45 * sc), rot=K.FORWARD, seg=8)
        for f in (.9, 1.3):
            a.part('Turbolaser_rings', 'Armor').cyl(.1 * sc, .07, loc=(bx, y - .4 * sc - f * sc, z + .45 * sc),
                                                    rot=K.FORWARD, seg=8, bevel=0)
        a.part('Turbolaser_tips', 'Energy').cyl(.05 * sc, .02, loc=(bx, y - .4 * sc - 2.31 * sc, z + .45 * sc),
                                                rot=K.FORWARD, seg=8, bevel=0)


def _dd_weapons(a):
    """Four twin laser turrets on the terrace lips (decor), the two point-defence lasers forward (Pd_laser_l / _r,
    breakable: a pylon from the hull, the dome, the emitter, its glow), the two forward ball guns under the chine
    (Mount_gun / .001: the 57 mm twins, the armoured ball in its socket, two jacketed barrels, Muzzle_gun between
    their tips and Muzzle_b1 / _b2 at each, Gun_barrels_* kick on the mount)."""
    for x, y, sc in ((3.6, 1.2, 1.0), (-3.6, 1.2, 1.0), (1.9, -9.5, .75), (-1.9, -9.5, .75),
                     (2.3, -2.2, .9), (-2.3, -2.2, .9)):
        _dd_turbolaser(a, x, y, sc)
    for name, x, tag in (('Pd_laser_l', 3.2, ''), ('Pd_laser_r', -3.2, '_r')):
        p = a.pivot(name, (x, -5.0, 3.2))
        zs = _dd_surface(abs(x), -5.0) - 3.2
        k.lathe(a.part('Pd_tower' + tag, 'Plaster', p), [(.98, zs - .15), (.9, zs + .2), (.7, -.32), (.62, -.25)],
                seg=8)
        k.lathe(a.part('Pd_base' + tag, 'Armor', p), [(.66, -.3), (.62, -.2), (.6, -.02), (0, 0)], seg=14)
        for j in range(4):
            u = j * R90 + R90 / 2
            a.part('Pd_fins' + tag, 'Steel', p).box((.06, .5, .5), loc=(math.cos(u) * .8, math.sin(u) * .8,
                                                                       zs + .4), rot=(0, 0, u + R90), bevel=0)
        a.part('Pd_dome' + tag, 'Armor', p).sphere(.48, loc=(0, 0, .1), seg=12, rings=6)
        a.part('Pd_emitter' + tag, 'Steel', p).cyl(.09, .8, loc=(0, -.55, .38), rot=(R90 - .3, 0, 0), seg=8, bevel=0)
        a.part('Pd_emitter' + tag, 'Steel', p).cyl(.14, .12, loc=(0, -.2, .27), rot=(R90 - .3, 0, 0), seg=8, bevel=0)
        a.part('Pd_glow' + tag, 'Energy', p).sphere(.1, loc=(0, -.95, .5), seg=8, rings=4)
        K.tone(a, name, k=.86)
    for i, x in enumerate((2.4, -2.4)):
        tag = '' if i == 0 else '_001'
        key = K.name('Mount_gun', i)
        zs = _dd_surface(abs(x), -6.0, top=False)
        k.lathe(a.part('Gun_sockets', 'Undercarriage'), [(1.0, 0), (1.0, .06), (.82, .1), (.82, .5)],
                loc=(x, -6.0, zs - .02), seg=16)
        m = a.pivot(key, (x, -6.0, -1.4))
        a.part('Gun_ball' + tag, 'Armor', m).sphere(.78, seg=16, rings=10)
        a.part('Gun_ball_band' + tag, 'Team', m).cyl(.8, .12, loc=(0, 0, -.05), seg=16, bevel=0)
        k.block(a.part('Gun_mantlet' + tag, 'Armor', m), (.85, .4, .55), loc=(0, -.62, -.28), chamfer=.06)
        for j, dx in enumerate((-.19, .19)):
            k.lathe(a.part(f'Gun_barrels{tag}', 'Steel', m), [(.12, 0), (.12, .45), (.095, .5), (.085, 1.85),
                                                              (.11, 1.9), (.11, 2.05), (.08, 2.1)],
                    loc=(dx, -.75, -.43), rot=(R90, 0, 0), seg=10)
            for f in (.75, 1.25):
                a.part(f'Gun_jackets{tag}', 'Armor', m).cyl(.11, .14, loc=(dx, -.75 - f, -.43), rot=K.FORWARD,
                                                            seg=10, bevel=0)
        mz = K.name('Muzzle_gun', i)
        a.pivot(mz, (0, -2.88, -.43), key)
        a.pivot(f'Muzzle_b1_gun{tag}', (-.19 if x > 0 else .19, 0, 0), mz)
        a.pivot(f'Muzzle_b2_gun{tag}', (.19 if x > 0 else -.19, 0, 0), mz)
        K.tone(a, key, k=.88)


def _dd_belly(a):
    """The three drop-pod bays (Pod_bay_1 .. _3: the well collar from the belly, the clamp frame, the pod with its
    glowing ring and fins), the four landing legs folded under the belly (hydraulic struts, the pads), the ventral
    keel fin, belly plates and lights, the ventral hangar door."""
    for i, (x, y) in enumerate(((4.0, 2.0), (0.0, 5.0), (-4.0, 2.0)), start=1):
        p = a.pivot(f'Pod_bay_{i}', (x, y, -2.0))
        zb = _dd_surface(abs(x), y, top=False) + 2.0
        k.lathe(a.part(f'Bay_ring_{i}', 'Armor', p), [(1.3, zb - .12), (1.38, zb - .05), (1.38, zb + .05),
                                                     (1.05, zb + .05), (1.05, zb - .3)], seg=18)
        k.lathe(a.part(f'Bay_pod_{i}', 'Team', p), [(0, zb - 1.05), (.45, zb - .95), (.78, zb - .6), (.82, zb - .2),
                                                   (.8, zb + .1), (0, zb + .12)], seg=16)
        a.part(f'Bay_glow_{i}', 'Energy', p).torus(.9, .05, loc=(0, 0, zb - .3), seg=18, ring=4)
        fr = a.part(f'Bay_frame_{i}', 'Steel', p)
        for j in range(4):
            u = j * R90 + .4
            fr.box((.16, .5, .5), loc=(math.cos(u) * 1.15, math.sin(u) * 1.15, zb - .25), rot=(0, 0, u), bevel=0)
        for j in range(3):
            u = j * TAU / 3
            a.part(f'Bay_fins_{i}', 'Armor', p).box((.04, .45, .4), loc=(math.cos(u) * .6, math.sin(u) * .6,
                                                                        zb - .75), rot=(0, 0, u + R90), bevel=0)
        K.tone(a, f'Pod_bay_{i}', k=.88)
    legs = a.part('Legs', 'Steel')
    pads = a.part('Leg_pads', 'Armor')
    rams = a.part('Leg_rams', 'Undercarriage')
    for (x, y) in ((5.0, -2.0), (-5.0, -2.0), (6.5, 9.0), (-6.5, 9.0)):
        z = _dd_surface(abs(x), y, top=False)
        k.block(a.part('Leg_wells', 'Undercarriage'), (1.2, 3.0, .1), loc=(x, y + 1.0, z - .02), chamfer=0)
        legs.limb((x, y, z - .05), (x * 1.04, y + 2.0, z - .85), .32, .36, bevel=.03)
        legs.limb((x * 1.04, y + 2.0, z - .85), (x * 1.07, y + 1.0, z - 1.15), .24, .24, bevel=.02)
        rams.limb((x, y + 1.2, z - .05), (x * 1.03, y + 1.6, z - .7), .1, .1, bevel=0)
        k.block(pads, (1.1, 1.5, .2), loc=(x * 1.07, y + 1.0, z - 1.25), chamfer=.04)
    k.extrude(a.part('Keel_fin', 'Armor'), [(-6.0, 0), (6.5, 0), (5.5, -.9), (-3.0, -.7)], .35,
              loc=(0, 8.0, -2.58), axis='X', chamfer=.04)
    for i, y in enumerate((-12.0, -8.5, -5.0, 10.5)):
        K.armour_plate(a, a.part('Belly_plates', 'Armor'), (2.4 + .4 * (i % 2), 2.0, .08),
                       (0, y, _dd_surface(0, y, top=False) - .04), rivet=.7)
    for s in (-1, 1):
        for y in (-10.0, 0.0, 12.0):
            a.part('Belly_lights', 'Alloy').box((.14, .14, .06), loc=(s * _dd_w(y) * .6, y,
                                                                      _dd_surface(_dd_w(y) * .6, y, top=False) - .02),
                                                bevel=0)
    k.block(a.part('Hangar_doors', 'Undercarriage'), (3.0, 3.6, .06), loc=(0, -.5, -2.63), chamfer=0)
    a.part('Hangar_frames', 'Steel').box((3.2, .08, .06), loc=(0, -2.35, -2.64), bevel=0)


def _dd_engines(a):
    """The main thruster block (Thruster_main: the housing, six big nozzles with their throats and glow, the engine
    collars and gimbal rams), two auxiliary engines at the stern corners, the RCS quads at the bow and the stern."""
    t = a.pivot('Thruster_main', (0, 15.5, .6))
    k.block(a.part('Engine_housing', 'Concrete', t), (12.4, 2.2, 3.4), loc=(0, .2, 0), chamfer=.18, taper=(.92, .9))
    K.grille(a, (0, -.85, 1.75), 6.0, .9, facing=(0, 0, 1), slats=8, parent='Thruster_main', frame_mat='Armor')
    for i in range(6):
        x = -5.0 + i * 2.0
        zz = (i % 2) * .55 - .28
        k.lathe(a.part('Engine_nozzles', 'Steel', t), [(.66, 0), (.72, .25), (.86, .7), (.92, .9), (.88, .95),
                                                       (.7, .95)], loc=(x, 1.0, zz), rot=K.BACKWARD, seg=20,
                caps=(False, False))
        k.lathe(a.part('Engine_collars', 'Armor', t), [(.78, -.05), (.8, .0), (.8, .2), (.72, .25)], loc=(x, .95, zz),
                rot=K.BACKWARD, seg=20)
        k.lathe(a.part('Engine_throats', 'Charred', t), [(.6, 0), (.4, .4), (0, .5)], loc=(x, 1.85, zz),
                rot=K.FORWARD, seg=16)
        a.part('Engine_glow', 'Energy', t).cyl(.58, .04, loc=(x, 1.45, zz), rot=(R90, 0, 0), seg=16, bevel=0)
        for e in (-1, 1):
            a.part('Gimbal_rams', 'Steel', t).limb((x + e * .5, .9, zz + .55), (x + e * .7, 1.5, zz + .55), .06, .06,
                                                   bevel=0)
    K.tone(a, 'Thruster_main', k=.86)
    for s in (-1, 1):
        x, y, z = s * 7.6, 15.4, .1
        k.lathe(a.part('Aux_engines', 'Armor'), [(.5, -1.4), (.62, -1.2), (.62, .3), (.5, .5)], loc=(x, y, z),
                rot=K.BACKWARD, seg=16)
        k.lathe(a.part('Aux_nozzles', 'Steel'), [(.42, 0), (.5, .4), (.44, .45)], loc=(x, y + .5, z), rot=K.BACKWARD,
                seg=16, caps=(False, False))
        a.part('Engine_glow', 'Energy').cyl(.38, .03, loc=(x, y + .7, z), rot=(R90, 0, 0), seg=14, bevel=0)
        for (yy, xf) in ((-17.4, .9), (13.8, .985)):
            xx = s * _dd_w(yy) * xf
            rcs = a.part('Rcs_quads', 'Armor')
            rcs.box((.3, .3, .25), loc=(xx, yy, .05), bevel=0)
            for dz in (-.1, .1):
                a.part('Rcs_nozzles', 'Steel').cyl(.05, .1, loc=(xx + s * .17, yy, .05 + dz), rot=(0, R90, 0), seg=6,
                                                   bevel=0)
    a.pivot('Point_exhaust', (0, 19.0, .6))
    a.pivot('Point_fire', (0, 3.0, 3.6))
    K.soot(a, (0, 17.0, .6), radius=4.5, k=.3)


def _dd_kit(a):
    """Fourth-tier fittings: antennas with red tips over the hull, the sensor blister and its mast on the right flank,
    hull lights, docking clamps on the stern deck, the forward sensor array, warning chevrons at the pod bays."""
    for j, (x, y) in enumerate(((2.2, -8.0), (-2.6, -4.0), (3.4, 4.5), (-3.8, 6.0), (1.8, 2.5), (-1.5, -11.0),
                                (5.5, -1.0), (-6.0, 3.0))):
        h = 1.0 + .35 * (j % 4)
        z = _dd_surface(abs(x), y)
        a.part('Antennas', 'Steel').cyl(.045, h, loc=(x, y, z + h / 2), seg=5, bevel=0)
        a.part('Antenna_tips', 'BarrelRed').box((.1, .1, .1), loc=(x, y, z + h), bevel=0)
    x, y = -_dd_w(4.0) - .35, 4.0
    k.lathe(a.part('Sensor_blister', 'Armor'), [(0, -1.8), (.9, -1.4), (1.1, 0), (.9, 1.4), (0, 1.8)],
            loc=(x, y, .3), rot=K.FORWARD, seg=12)
    a.part('Antennas', 'Steel').cyl(.06, 2.6, loc=(x, y + .5, 1.6), seg=5, bevel=0)
    # The forward sensor array on the bow deck: a low dome and a flat panel.
    y = -13.0
    z = _dd_t(y)
    a.part('Sensor_dome', 'PlasterWhite').sphere(.5, loc=(0, y, z + .1), seg=14, rings=6)
    k.block(a.part('Sensor_panel', 'Medical'), (1.2, .1, .7), loc=(0, y + 1.4, z + .35), rot=(-.4, 0, 0), chamfer=.02)
    # Hull lights along the chine, docking clamps aft.
    for s in (-1, 1):
        for y in (-14.0, -7.0, 0.0, 7.0, 13.5):
            a.part('Hull_lights', 'Alloy').box((.08, .14, .08), loc=(s * (_dd_w(y) + .06), y, .45), bevel=0)
        for y in (12.6, 14.0):
            k.block(a.part('Clamps', 'Armor'), (.6, .5, .35), loc=(s * 5.0, y, _dd_t(y) + .17), chamfer=.04)
            a.part('Clamps', 'Steel').box((.2, .6, .1), loc=(s * 5.0, y, _dd_t(y) + .4), bevel=0)
    for i, (x, y) in enumerate(((4.0, 2.0), (0.0, 5.0), (-4.0, 2.0))):
        zb = _dd_surface(abs(x), y, top=False)
        for j in range(4):
            u = j * R90
            a.part('Bay_chevrons', 'Hazard').box((.5, .12, .02), loc=(x + math.cos(u) * 1.6, y + math.sin(u) * 1.6,
                                                                       zb - .02), rot=(0, 0, u + R90), bevel=0)


def daedalus(a):
    """Daedalus, redrawn (module docstring). Runtime nodes at the old file's places: Mount_gun / .001 with
    Muzzle_gun / .001 and their per-barrel Muzzle_b1 / _b2 (the twins are modelled here: mb_fix_barrels no longer
    copies them), Pd_laser_l / _r, Thruster_main, Pod_bay_1 .. _3, Mount_APS, Point_fire, Point_exhaust."""
    K.suffixed(a)
    _dd_hull(a)
    _dd_plating(a)
    _dd_deck_modules(a)
    _dd_superstructure(a)
    _dd_tier_kit(a)
    _dd_weapons(a)
    _dd_belly(a)
    _dd_engines(a)
    _dd_kit(a)
    k.clean(a)


BUILDERS = {
    'armored_train': (armored_train, dict(ao_distance=.8, grime_height=.7, ao_strength=.72)),
    'nuke_train': (nuke_train, dict(ao_distance=.8, grime_height=.7)),
    'ixion': (ixion, dict(ao_distance=1.1, grime_height=1.6)),
    'mega_gunship': (mega_gunship, dict(ao_distance=.8, grime_height=.5, ao_strength=.75)),
    'daedalus': (daedalus, dict(ao_distance=1.5, grime_height=.2, ground=False)),
}
