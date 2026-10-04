"""Play-test 14 after R4 (lane space): the space bosses' new weapons and their own liveries.

Owner (04/10, last block of Docs/prompts/playtest14_vi.txt, "Bổ sung 04/10 sau khi thử R4"): "dòng các tàu icarus,
icarus mk 0 và daedalus cũng thêm vũ khí như súng pháo ở dưới bắn xuống đất (2-4 khẩu)"; "3 tàu mới này nên có tên
lửa và súng pháo chỉa xuống bắn, bỏ railgun, và thêm vũ khí vào luôn"; "các model boss tàu mới ... nên sửa lại màu
luôn"; "nhớ là vẽ lại chứ đừng dùng model cũ". DECISIONS "Play-test 14 space ships after R4 (lane space)".

Every weapon here is drawn for one ship only (no kit sub-assembly, no other boss's part, no old mesh recoloured), read
from a real gun or launcher at the ship's scale:
- silver_bug (Icarus): two ventral twin 30 mm turrets (Mk 44 Bushmaster II read, sb_v30) forward and two ventral
  105 mm turrets (M102 read, sb_v105) amidships, each in its own blister on the belly near the chine.
- icarus_mk0: two ventral 40 mm L/60 test mounts (mk_v40): open cradles on bolted test frames, a hopper of clips,
  instrumentation and test cabling.
- daedalus: the two chin ball turrets become its targeting-laser balls (dd_laser_ball: the def's lasers fire from
  them), two ventral twin 57 mm turrets (dd_v57) amidships, two ventral GAU-12 25 mm gondolas (dd_v25) aft.
- hyperion: twin 155 mm dorsal turrets (hp_twin155) where the coilguns were, two ventral 127 mm turrets (hp_v127),
  two 8-cell VLS deckhouses on the sponson ledges (hp_vls).
- theia: two ventral twin 35 mm turrets (th_v35), two quad missile pods on the hangar pods (th_pods).
- coeus: a twin 203 mm dorsal turret (co_twin203) where the coil artillery was, two ventral twin 76 mm turrets
  (co_v76) where the laser batteries were, two Spike NLOS box launchers on the hammerhead (co_spike).

Ventral guns hang under their pivot with the barrels drawn depressed (25-35 degrees), so they read as firing down at
the ground; the pivot itself only turns (the view yaws Mount_* pivots), the runtime aligns each muzzle along the
barrel it sits on (ModelLibrary.AlignMuzzles). Runtime names: the k-th mount of a slot is the k-th Mount_<slot> /
Muzzle_<slot> by name; twins carry Muzzle_b1 / _b2 at each open end; launchers (slot rocket) carry Muzzle_rocket[.001]
only (they do not turn). Barrel parts are `*_barrels<tag>` / `*_muzzles<tag>` directly under the mount (the kick).

Paint: these bosses have "livery": "own" in balance.json (lane K): their Team surfaces draw in the def's "paint" /
"paintFinish", every other kit material as named (SpaceWhite, SpaceSilver, Titanium, GoldFoil ... exist in both
frontier_kit.MATERIALS and MaterialLibrary.Kit). livery(): after the bake (COLOR_0), per-part tints, dark heat tiles
on the downward faces, plate-to-plate tone steps. Metres, +Z up, -Y front, +X left.
"""
import math
import re

from mathutils import Euler, Vector

import frontier_kit as kit
import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= gun frames
class Gun:
    """A gun's frame in its pivot: trunnion at `o`, bore depressed `dep` radians below level (forward is -Y)."""

    def __init__(self, o, dep):
        self.o = Vector(o)
        self.dep = dep
        self.m = Euler((dep, 0, 0)).to_matrix()

    def p(self, x, y, z=0.0):
        """A point (x across, y along the bore with -y forward, z over the bore) in the pivot's frame."""
        return tuple(self.o + self.m @ Vector((x, y, z)))

    @property
    def rot(self):
        """Euler for a part laid in the gun frame (blocks on the cradle)."""
        return (self.dep, 0, 0)

    @property
    def bore(self):
        """Euler turning a lathe's +Z along the bore (forward and down)."""
        return (R90 + self.dep, 0, 0)


def bore(part, g, x, profile, z=0.0, seg=14):
    """A turned part on the bore at lateral offset x (and z over it): profile [(radius, distance forward)]."""
    k.lathe(part, profile, loc=g.p(x, 0, z), rot=g.bore, seg=seg)


def muzzles(a, slot, i, g, xs, L, mount, out=.03):
    """Muzzle_<slot>[.00i] at the middle of the open ends L forward of the trunnion, Muzzle_b<k>_<slot>[_00i] at
    each barrel's end (xs: the barrels' lateral offsets; one barrel: no per-barrel muzzles)."""
    tag = '' if i == 0 else f'_{i:03d}'
    mz = a.pivot(K.name(f'Muzzle_{slot}', i), g.p(0, -(L + out)), mount)
    if len(xs) > 1:
        for j, bx in enumerate(sorted(xs)):
            a.pivot(f'Muzzle_b{j + 1}_{slot}{tag}', (bx, 0, 0), mz)
    return mz


def octa(w, l, z, cf=.35, cb=.3, yc=0.0):
    """An eight-sided ring at height z: half width w, half length l, the front corners cut cf, the back cb."""
    return [(-w + cf, yc - l, z), (w - cf, yc - l, z), (w, yc - l + cf, z), (w, yc + l - cb, z),
            (w - cb, yc + l, z), (-w + cb, yc + l, z), (-w, yc + l - cb, z), (-w, yc - l + cf, z)]


# ============================================================================= silver_bug (Icarus)
def _belly_seat(H, x, y, depth):
    """The point `depth` below the belly at (x, y) along its normal, and the normal."""
    n = Vector(H.normal(x, y, top=False))
    return Vector((x, y, H.bot(x, y))) + n * depth, n


def sb_v30(a, H, i, s, y, paint='SpaceWhite'):
    """Icarus's ventral twin 30 mm turret (Mount_gun.004 at +X, .005 at -X; Mk 44 Bushmaster II read): a faired
    blister on the belly near the chine with its heat-tile skirt, the race, an eight-sided armoured drum hanging from
    it with the sloped gun face, the cradle with two fluted barrels in cooling jackets and the Bushmaster's slotted
    brakes (Gun_barrels* / Gun_muzzles*), the link chutes from the side magazines, the EO ball; barrels 30 degrees
    down. Muzzle_gun.00i between the brakes, Muzzle_b1 / _b2 at each."""
    tag = f'_{i:03d}'
    x = s * .78 * H.w(y)
    seat, n = _belly_seat(H, x, y, .3)
    k.lathe(a.part('Vgun_blisters', 'MetalSheet'), [(1.32, -.55), (1.34, -.08), (1.22, .14), (1.06, .26), (1.0, .3)],
            loc=(x, y, H.bot(x, y)), rot=K.rot_to(tuple(n)), seg=22)
    k.ring(a.part('Vgun_skirts', 'Undercarriage'), [(1.0, .29), (1.12, .22), (1.12, .26), (1.0, .32)],
           loc=(x, y, H.bot(x, y)), rot=K.rot_to(tuple(n)), seg=22)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, tuple(seat))
    k.ring(a.part('Vgun_race' + tag, 'Steel', m), [(.84, .02), (.93, .02), (.93, -.07), (.84, -.09)], seg=20)
    drum = a.part('Vgun_drum' + tag, paint, m)
    k.sharp_loft(drum, [octa(.86, .82, -.07, .34, .3), octa(.82, .76, -.58, .4, .28, .04),
                        octa(.56, .42, -.86, .22, .2, .12)], chamfer=.035)
    k.inset(drum, lambda c, nn, f: abs(nn.z) < .7, width=.05, depth=-.012)
    a.part('Vgun_tiles' + tag, 'Undercarriage', m).cyl(.46, .04, loc=(0, .12, -.88), seg=14, bevel=0)
    g = Gun((0, -.66, -.42), math.radians(30))
    # The sloped gun face and the cradle block between the barrels.
    k.block(a.part('Vgun_face' + tag, 'Armor', m), (1.05, .18, .62), loc=g.p(0, .08, -.02), rot=(g.dep - R90 * .2, 0, 0),
            chamfer=.04, ends=(True, True))
    k.block(a.part('Vgun_cradle' + tag, 'Steel', m), (.28, .7, .26), loc=g.p(0, -.2, 0), rot=g.rot, chamfer=.03,
            ends=(True, True))
    xs = (-.2, .2)
    for bx in xs:
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, bx, [(.06, -.2), (.06, 2.05), (.054, 2.1), (.054, 2.18)],
             seg=10)
        bore(a.part('Gun_barrels' + tag, 'Armor', m), g, bx, [(.1, -.05), (.1, .62), (.075, .68)], seg=12)
        for j in range(5):
            # Fluting: thin raised strips along the barrel's first half.
            u = j * TAU / 5
            a.part('Gun_barrels' + tag, 'Undercarriage', m).box(
                (.022, .022, .8), loc=g.p(bx + math.cos(u) * .062, -1.1, math.sin(u) * .062), rot=g.bore, bevel=0)
        bore(a.part('Gun_muzzles' + tag, 'Armor', m), g, bx, [(.05, 2.18), (.085, 2.2), (.085, 2.42), (.06, 2.44)],
             seg=10)
        for e in (-1, 1):
            a.part('Gun_muzzles' + tag, 'Undercarriage', m).box((.03, .07, .1), loc=g.p(bx + e * .085, -2.32),
                                                                rot=g.rot, bevel=0)
    muzzles(a, 'gun', i, g, xs, 2.44, key)
    for e in (-1, 1):
        k.block(a.part('Vgun_magazines' + tag, 'Armor', m), (.3, .9, .5), loc=(e * .82, .1, -.52), chamfer=.04,
                ends=(True, True))
        a.part('Vgun_chutes' + tag, 'Steel', m).limb((e * .72, -.25, -.45), (e * .26, -.62, -.4), .1, .07, bevel=0)
    a.part('Vgun_eo' + tag, 'Undercarriage', m).sphere(.17, loc=(-.62 * s, -.55, -.72), seg=12, rings=8)
    a.part('Glass', 'Glass', m).cyl(.09, .02, loc=(-.62 * s, -.71, -.72), rot=(R90, 0, 0), seg=10, bevel=0)
    K.soot(a, tuple(Vector(seat) + Vector(g.p(0, -2.4))), radius=.5, k=.25)
    K.tone(a, key, k=.9)


def sb_v105(a, H, i, s, y, paint='SpaceWhite'):
    """Icarus's ventral 105 mm turret (Mount_gun.006 at +X, .007 at -X; M102 howitzer read): the belly blister, the
    race, a lathed armoured cupola hanging from it with its armour bands, the faceted gun shield, the 105 mm
    barrel with its recoil sleeve and the M102's double-baffle brake (Gun_barrels* / Gun_muzzles*), the recoil and
    recuperator cylinders over it, the ammunition trunk aft, the gunner's sight. Barrel 35 degrees down; one barrel:
    Muzzle_gun.00i at the brake."""
    tag = f'_{i:03d}'
    x = s * .8 * H.w(y)
    seat, n = _belly_seat(H, x, y, .34)
    k.lathe(a.part('Vgun_blisters', 'MetalSheet'), [(1.72, -.6), (1.74, -.08), (1.6, .16), (1.42, .3), (1.36, .34)],
            loc=(x, y, H.bot(x, y)), rot=K.rot_to(tuple(n)), seg=24)
    k.ring(a.part('Vgun_skirts', 'Undercarriage'), [(1.36, .33), (1.5, .25), (1.5, .29), (1.36, .36)],
           loc=(x, y, H.bot(x, y)), rot=K.rot_to(tuple(n)), seg=24)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, tuple(seat))
    k.ring(a.part('Vgun_race' + tag, 'Steel', m), [(1.2, .02), (1.32, .02), (1.32, -.08), (1.2, -.1)], seg=24)
    cup = a.part('Vgun_cupola' + tag, paint, m)
    k.lathe(cup, [(1.24, -.08), (1.3, -.32), (1.26, -.72), (1.06, -1.06), (.7, -1.28), (.3, -1.36), (0, -1.38)],
            seg=24, worn=(2,))
    k.inset(cup, lambda c, nn, f: nn.z > -.85, width=.07, depth=-.015)
    for z in (-.36, -.8):
        k.ring(a.part('Vgun_bands' + tag, 'Armor', m), [(1.29, z + .06), (1.34, z + .06), (1.34, z - .06),
                                                        (1.29, z - .06)], seg=24)
    g = Gun((0, -.9, -.62), math.radians(35))
    shield = a.part('Vgun_shield' + tag, 'Armor', m)
    k.sharp_loft(shield, [[g.p(-.62, .25, -.45), g.p(.62, .25, -.45), g.p(.62, .25, .5), g.p(-.62, .25, .5)],
                          [g.p(-.5, -.25, -.36), g.p(.5, -.25, -.36), g.p(.5, -.25, .4), g.p(-.5, -.25, .4)]],
                 chamfer=.05)
    bore(a.part('Vgun_mantlet' + tag, 'Steel', m), g, 0, [(.26, -.3), (.26, .25), (.2, .32)], seg=16)
    bore(a.part('Gun_barrels' + tag, 'Steel', m), g, 0, [(.13, .2), (.13, .35), (.11, .4), (.1, 2.9), (.115, 2.95),
                                                         (.115, 3.0)], seg=14)
    bore(a.part('Gun_barrels' + tag, 'Armor', m), g, 0, [(.18, .25), (.18, 1.2), (.14, 1.3)], seg=14)
    brake = a.part('Gun_muzzles' + tag, 'Armor', m)
    bore(brake, g, 0, [(.1, 3.0), (.19, 3.03), (.19, 3.15), (.13, 3.17), (.13, 3.24), (.19, 3.26), (.19, 3.38),
                       (.11, 3.4)], seg=14)
    for e in (-1, 1):
        for d in (3.09, 3.32):
            brake.box((.04, .09, .2), loc=g.p(e * .19, -d), rot=g.rot, bevel=0)
    for e in (-1, 1):
        a.part('Vgun_recoil' + tag, 'Steel', m).limb(g.p(e * .16, .1, .2), g.p(e * .16, -1.3, .2), .09, .09, bevel=.02)
    k.block(a.part('Vgun_trunk' + tag, 'Undercarriage', m), (.7, .6, .5), loc=(0, .95, -.5), chamfer=.05,
            ends=(True, True))
    k.block(a.part('Vgun_sight' + tag, 'Armor', m), (.26, .36, .3), loc=(.62 * s, -.62, -.9), chamfer=.03,
            ends=(True, True))
    a.part('Glass', 'Glass', m).box((.2, .02, .14), loc=(.62 * s, -.81, -.9), bevel=0)
    a.part('Vgun_tiles' + tag, 'Undercarriage', m).cyl(.42, .04, loc=(0, .1, -1.37), seg=16, bevel=0)
    muzzles(a, 'gun', i, g, (0,), 3.4, key)
    K.soot(a, tuple(Vector(seat) + Vector(g.p(0, -3.3))), radius=.6, k=.25)
    K.tone(a, key, k=.9)


# ============================================================================= icarus_mk0 (the prototype)
def mk_v40(a, H, i, s, y):
    """The prototype's ventral 40 mm L/60 test mount (Mount_gun at +X, .001 at -X): a bolted adapter plate on the
    belly and four struts down to the test frame (hazard bands), the slewing ring, an open cradle (primer side
    plates, trunnion caps), the L/60 barrel with its recoil spring and conical flash hider (Gun_barrels* /
    Gun_muzzles*), the four-round clip guide with brass rounds, the ring sight, the instrumentation box with its
    red lamp, the test cabling. Barrel 30 degrees down; Muzzle_gun[.001] at the flash hider."""
    tag = '' if i == 0 else f'_{i:03d}'
    x = s * .72 * H.w(y)
    zb = H.bot(x, y)
    n = Vector(H.normal(x, y, top=False))
    k.block(a.part('Test_adapters', 'Crate'), (1.6, 1.6, .1), loc=tuple(Vector((x, y, zb)) + n * .02),
            rot=K.rot_to(tuple(n)), chamfer=.03)
    zf = zb - .75
    frame = a.part('Test_frames', 'Steel')
    for ex in (-1, 1):
        for ey in (-1, 1):
            top = (x + ex * .6, y + ey * .6, H.bot(x + ex * .6, y + ey * .6) - .02)
            frame.limb(top, (x + ex * .55, y + ey * .55, zf), .1, .1, bevel=0)
            a.part('Test_bands', 'Hazard').box((.12, .12, .12), loc=(x + ex * .57, y + ey * .57, zf + .3), bevel=0)
    for ex in (-1, 1):
        frame.limb((x + ex * .55, y - .55, zf), (x + ex * .55, y + .55, zf), .1, .1, bevel=0)
        frame.limb((x - .55, y + ex * .55, zf), (x + .55, y + ex * .55, zf), .1, .1, bevel=0)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, zf - .05))
    k.ring(a.part('Test_ring' + tag, 'Steel', m), [(.42, 0), (.5, 0), (.5, -.1), (.42, -.1)], seg=16)
    g = Gun((0, -.1, -.5), math.radians(30))
    for e in (-1, 1):
        k.block(a.part('Test_cradle' + tag, 'Crate', m), (.08, .7, .5), loc=(e * .24, 0, -.32), chamfer=.02,
                ends=(True, True))
        a.part('Test_trunnions' + tag, 'Steel', m).cyl(.1, .06, loc=(e * .3, -.1, -.5), rot=(0, R90, 0), seg=10,
                                                      bevel=0)
    k.block(a.part('Test_breech' + tag, 'Armor', m), (.3, .7, .3), loc=g.p(0, .35, 0), rot=g.rot, chamfer=.03,
            ends=(True, True))
    bore(a.part('Gun_barrels' + tag, 'Steel', m), g, 0, [(.065, -.05), (.065, 2.35), (.058, 2.4)], seg=12)
    for j in range(6):
        k.ring(a.part('Gun_barrels' + tag, 'Steel', m), [(.085, -.025), (.1, -.025), (.1, .025), (.085, .025)],
               loc=g.p(0, -(.12 + j * .09)), rot=g.bore, seg=12)
    bore(a.part('Gun_muzzles' + tag, 'Armor', m), g, 0, [(.05, 2.4), (.07, 2.42), (.11, 2.72), (.1, 2.75),
                                                         (.06, 2.62)], seg=12)
    # The clip guide over the breech, four brass rounds in it.
    k.block(a.part('Test_clip_guide' + tag, 'Steel', m), (.16, .3, .5), loc=g.p(0, .3, .35), rot=g.rot, chamfer=.02,
            ends=(True, True))
    for j in range(4):
        a.part('Test_rounds' + tag, 'Gilded', m).cyl(.045, .3, loc=g.p(0, .3, .18 + j * .1), rot=g.bore, seg=8,
                                                     bevel=0)
    a.part('Test_sight' + tag, 'Steel', m).torus(.13, .015, loc=g.p(-.22, -.35, .22), rot=g.bore, seg=14, ring=4)
    a.part('Test_sight' + tag, 'Steel', m).limb(g.p(-.1, -.35, .05), g.p(-.22, -.35, .1), .03, .03, bevel=0)
    k.block(a.part('Test_box' + tag, 'Undercarriage', m), (.28, .34, .24), loc=(-.3 * s, .32, -.25), chamfer=.03,
            ends=(True, True))
    a.part('Test_lamp' + tag, 'EliteGlow', m).sphere(.05, loc=(-.3 * s, .32, -.39), seg=8, rings=4)
    a.part('Test_cables' + tag, 'Charred', m).tube([(-.3 * s, .45, -.2), (-.2 * s, .5, .05), (0, .3, .02)], .03,
                                                   seg=5)
    a.part('Test_cables', 'Charred').tube([(x, y + .5, zf + .05), (x + .3 * s, y + .62, zf + .4),
                                           (x + .45 * s, y + .65, zb - .02)], .035, seg=5)
    muzzles(a, 'gun', i, g, (0,), 2.75, key)
    K.tone(a, key, k=.92)


# ============================================================================= daedalus
def dd_laser_ball(a, i, x, y, z, zs, mark='ContainerBlue'):
    """Daedalus's chin targeting-laser ball (Mount_gun at +X, .005 at -X; the def's 300 kW lasers): the socket ring
    under the chine (on the hull), the armoured ball with its marking band, a faceted emitter housing on its face,
    the emitter tube with its cooling fins, two focusing rings and the lens (Las_barrels* / Las_muzzles*), the
    sensor eye. Emitter 20 degrees down; Muzzle_gun.00i at the lens."""
    tag = '' if i == 0 else f'_{i:03d}'
    k.lathe(a.part('Laser_sockets', 'Undercarriage'), [(1.0, 0), (1.0, .06), (.82, .1), (.82, .5)],
            loc=(x, y, zs - .02), seg=18)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, z))
    a.part('Las_ball' + tag, 'Armor', m).sphere(.78, seg=18, rings=12)
    a.part('Las_band' + tag, mark, m).cyl(.8, .12, loc=(0, 0, -.05), seg=18, bevel=0)
    g = Gun((0, -.55, -.3), math.radians(20))
    k.block(a.part('Las_housing' + tag, 'Titanium', m), (.7, .55, .6), loc=g.p(0, 0, -.3), rot=g.rot, chamfer=.06,
            ends=(True, True))
    bore(a.part('Las_barrels' + tag, 'Steel', m), g, 0, [(.2, -.1), (.2, .5), (.15, .58), (.13, 1.5), (.17, 1.56),
                                                         (.17, 1.7)], seg=14)
    for j in range(6):
        a.part('Las_barrels' + tag, 'Armor', m).box((.5, .5, .035), loc=g.p(0, -(.72 + j * .11)), rot=g.bore, bevel=0)
    bore(a.part('Las_muzzles' + tag, 'Armor', m), g, 0, [(.12, 1.7), (.21, 1.73), (.21, 1.92), (.16, 1.95)], seg=14)
    a.part('Las_muzzles' + tag, 'Energy', m).cyl(.14, .02, loc=g.p(0, -1.955), rot=g.bore, seg=12, bevel=0)
    a.part('Las_eye' + tag, 'Glass', m).sphere(.13, loc=(.42, -.5, .18), seg=10, rings=6)
    muzzles(a, 'gun', i, g, (0,), 1.95, key)
    K.tone(a, key, k=.88)


def dd_v57(a, i, x, y, zs, paint='Team', mark='ContainerBlue'):
    """Daedalus's ventral twin 57 mm turret (Mount_gun.001 at +X, .002 at -X; AU-220 read): the belly ring (on the
    hull), an angular gunhouse hanging under it (wide at the hull, its faces sloped in, a marking band), the
    mantlet, two 57 mm barrels in cooling jackets with the AU-220's perforated brakes (Gun_barrels* /
    Gun_muzzles*), the EO / radar sight box, the ammunition elevator up into the hull. Barrels 25 degrees down;
    Muzzle_gun.00i between the brakes, Muzzle_b1 / _b2 at each."""
    tag = f'_{i:03d}'
    k.lathe(a.part('Vgun_rings', 'Undercarriage'), [(1.25, .85), (1.25, 0), (1.15, -.06), (1.06, -.06)],
            loc=(x, y, zs), seg=22)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, zs - .08))
    house = a.part('Vgun_house' + tag, paint, m)
    k.sharp_loft(house, [octa(1.05, 1.15, 0, .5, .3), octa(1.0, 1.05, -.62, .6, .3, .05),
                         octa(.72, .7, -1.0, .35, .2, .15)], chamfer=.04)
    k.inset(house, lambda c, nn, f: nn.z > -.8, width=.06, depth=-.014)
    k.ring(a.part('Vgun_band' + tag, mark, m), [(1.04, -.2), (1.07, -.2), (1.07, -.32), (1.04, -.32)], seg=8)
    g = Gun((0, -.95, -.5), math.radians(25))
    k.block(a.part('Vgun_mantlet' + tag, 'Armor', m), (1.0, .35, .5), loc=g.p(0, .05), rot=g.rot, chamfer=.05,
            ends=(True, True))
    xs = (-.24, .24)
    for bx in xs:
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, bx, [(.075, 0), (.075, 2.25), (.068, 2.3)], seg=12)
        bore(a.part('Gun_barrels' + tag, 'Armor', m), g, bx, [(.12, .1), (.12, 1.1), (.1, 1.15)], seg=12)
        brk = a.part('Gun_muzzles' + tag, 'Armor', m)
        bore(brk, g, bx, [(.06, 2.3), (.1, 2.32), (.1, 2.58), (.075, 2.6)], seg=12)
        for j in range(3):
            for e in (-1, 1):
                brk.box((.03, .05, .06), loc=g.p(bx + e * .1, -(2.37 + j * .08)), rot=g.rot, bevel=0)
    muzzles(a, 'gun', i, g, xs, 2.6, key)
    k.block(a.part('Vgun_sight' + tag, 'Armor', m), (.32, .4, .34), loc=(.7, -.55, -.72), chamfer=.04,
            ends=(True, True))
    a.part('Glass', 'Glass', m).box((.22, .02, .16), loc=(.7, -.76, -.72), bevel=0)
    k.block(a.part('Vgun_elevator' + tag, 'Undercarriage', m), (.5, .5, .3), loc=(0, .75, -.12), chamfer=.04,
            ends=(True, True))
    a.part('Vgun_tiles' + tag, 'Undercarriage', m).cyl(.5, .04, loc=(0, .15, -1.01), seg=12, bevel=0)
    K.tone(a, key, k=.9)


def dd_v25(a, i, x, y, zs, paint='Team'):
    """Daedalus's ventral GAU-12 25 mm gondola (Mount_gun.003 at +X, .004 at -X): a short pylon and ring under the
    belly (on the hull), the streamlined gun gondola turning under it, the five-barrel rotary cluster with its
    clamp rings and the gun housing (Gun_barrels* / Gun_muzzles*), the linkless feed chute, the drive motor, the
    sensor window. Barrels 20 degrees down; one muzzle at the cluster's front (one weapon)."""
    tag = f'_{i:03d}'
    a.part('Vgun_pylons', 'Armor').limb((x, y + .2, zs + .3), (x, y + .1, zs - .25), .5, .9, bevel=.04)
    k.ring(a.part('Vgun_pylons', 'Steel'), [(.36, -.2), (.44, -.2), (.44, -.3), (.36, -.3)], loc=(x, y, zs),
           seg=14)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, zs - .3))
    k.lathe(a.part('Vgun_gondola' + tag, paint, m), [(0, -1.1), (.22, -1.0), (.36, -.7), (.4, -.2), (.4, .5),
                                                     (.3, .95), (0, 1.1)], loc=(0, 0, -.45), rot=K.BACKWARD, seg=16)
    a.part('Vgun_gondola' + tag, 'Armor', m).limb((0, .1, -.05), (0, -.2, -.45), .3, .6, bevel=.03)
    g = Gun((0, -1.0, -.5), math.radians(20))
    bore(a.part('Gun_barrels' + tag, 'Armor', m), g, 0, [(.2, -.1), (.2, .25), (.15, .3)], seg=14)
    for j in range(5):
        u = j * TAU / 5
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, math.cos(u) * .08, [(.028, .25), (.028, 1.55), (0, 1.55)],
             z=math.sin(u) * .08, seg=6)
    for d in (.65, 1.2):
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, 0, [(.13, d), (.13, d + .06)], seg=12)
    bore(a.part('Gun_muzzles' + tag, 'Armor', m), g, 0, [(.13, 1.5), (.135, 1.5), (.135, 1.58), (.11, 1.6)], seg=12)
    muzzles(a, 'gun', i, g, (0,), 1.6, key)
    a.part('Vgun_feed' + tag, 'Steel', m).tube([(0, .3, -.1), (.25, .0, -.25), (.2, -.6, -.45)], .07, seg=6)
    a.part('Vgun_motor' + tag, 'Undercarriage', m).cyl(.12, .3, loc=(-.32, -.55, -.42), rot=(R90, 0, 0), seg=10,
                                                       bevel=.02)
    a.part('Glass', 'Glass', m).box((.02, .3, .12), loc=(.39, -.3, -.4), bevel=0)
    K.tone(a, key, k=.9)


# ============================================================================= hyperion
def hp_twin155(a, i, x, y, z0, paint, mark='GoldFoil'):
    """Hyperion's dorsal twin 155 mm turret (Mount_gun at +X, .001 at -X, where the coilguns were): the barbette
    and its bolt ring, a low wide gunhouse with a rounded face and raked roof, the slab mantlet with two gun slots
    and their blast boots, two 155 mm/52 barrels with thermal sleeves and double-baffle brakes (Gun_barrels* /
    Gun_muzzles*), rangefinder ears, the commander's cupola, roof hatches and vents, a heat radiator pair over the
    rear bustle, a gilded crown band. Barrels laid level; Muzzle_gun[.001] between the brakes, Muzzle_b1 / _b2."""
    tag = '' if i == 0 else f'_{i:03d}'
    k.lathe(a.part('Gun_barbettes', 'Armor'), [(2.35, -.12), (2.35, .3), (2.2, .42), (2.1, .45)], loc=(x, y, z0),
            seg=30)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z0 + .43), (0, 0, 1), 2.2, 22, r=.05, h=.05)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, z0 + .46))
    house = a.part('Gun_house' + tag, paint, m)
    rings = []
    for z, sc, yb in ((0, 1.0, 3.0), (1.1, .93, 2.85), (1.65, .74, 2.5)):
        pts = []
        for j in range(7):
            u = math.pi + j * math.pi / 6           # the rounded face: a half octagon-ish front
            pts.append((math.cos(u) * 2.1 * sc, -1.0 + math.sin(u) * 1.5 * sc, z))
        pts += [(2.1 * sc, yb, z), (-2.1 * sc, yb, z)]
        rings.append(pts)
    k.sharp_loft(house, rings, chamfer=.06)
    k.inset(house, lambda c, nn, f: nn.z > .3, width=.08, depth=-.02)
    k.ring(a.part('Gun_crown' + tag, mark, m), [(2.06, .45), (2.12, .45), (2.12, .58), (2.06, .58)], seg=28)
    g = Gun((0, -2.0, .78), math.radians(-2))
    k.block(a.part('Gun_mantlet' + tag, 'Armor', m), (2.6, .5, 1.0), loc=g.p(0, .1, -.5), rot=g.rot, chamfer=.08,
            ends=(True, True))
    xs = (-.68, .68)
    for bx in xs:
        bore(a.part('Gun_boots' + tag, 'Rubber', m), g, bx, [(.3, -.2), (.3, .05), (.22, .3), (.2, .45)], seg=14)
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, bx, [(.17, .3), (.17, 1.3), (.14, 1.45), (.13, 6.9),
                                                              (.145, 7.0), (.145, 7.05)], seg=16)
        for d in (1.9, 3.0, 4.1, 5.2):
            bore(a.part('Gun_barrels' + tag, 'Armor', m), g, bx, [(.155, d), (.165, d + .02), (.165, d + .32),
                                                                 (.155, d + .34)], seg=16)
        brk = a.part('Gun_muzzles' + tag, 'Armor', m)
        bore(brk, g, bx, [(.12, 7.05), (.26, 7.08), (.26, 7.24), (.17, 7.26), (.17, 7.34), (.26, 7.36),
                          (.26, 7.52), (.15, 7.55)], seg=16)
        for e in (-1, 1):
            for d in (7.16, 7.44):
                brk.box((.05, .11, .26), loc=g.p(bx + e * .26, -d), rot=g.rot, bevel=0)
    muzzles(a, 'gun', i, g, xs, 7.55, key)
    for e in (-1, 1):
        a.part('Gun_ears' + tag, 'Armor', m).cyl(.22, .8, loc=(e * 2.25, .2, 1.25), rot=(0, R90, 0), seg=12,
                                                 bevel=.03)
        a.part('Glass', 'Glass', m).cyl(.15, .02, loc=(e * 2.66, .2, 1.25), rot=(0, R90, 0), seg=10, bevel=0)
    k.lathe(a.part('Gun_cupola' + tag, 'Armor', m), [(.48, 0), (.48, .28), (.36, .4), (0, .44)],
            loc=(-.85, .9, 1.62), seg=14)
    for j in range(5):
        u = -R90 + (j - 2) * .45
        a.part('Gun_periscopes' + tag, 'Glass', m).box((.1, .06, .08), loc=(-.85 + math.cos(u) * .44,
                                                                          .9 + math.sin(u) * .44, 1.95),
                                                       rot=(0, 0, u), bevel=0)
    k.block(a.part('Gun_hatch' + tag, 'Steel', m), (.7, .8, .06), loc=(.8, 1.0, 1.64), chamfer=.02)
    a.part('Gun_vents' + tag, 'Undercarriage', m).box((1.4, .5, .05), loc=(0, 2.2, 1.66), bevel=0)
    for e in (-1, 1):
        k.extrude(a.part('Gun_radiators' + tag, 'Steel', m), [(2.0, .6), (3.0, .6), (3.0, .9), (2.3, 1.9)], .12,
                  loc=(e * 1.45, 0, 0), axis='X', chamfer=.02)
        a.part('Gun_radiator_glow' + tag, 'Alloy', m).box((.03, .6, .06), loc=(e * 1.52, 2.6, 1.1), bevel=0)
    K.soot(a, (x, y + g.p(0, -7.4)[1], z0 + .46 + .78), radius=.7, k=.25)
    K.tone(a, key, k=.9)


def hp_v127(a, i, x, y, z0, paint, mark='GoldFoil'):
    """Hyperion's ventral 127 mm turret (Mount_gun.004 at +X, .005 at -X; Mk 45 Mod 4 read, hung under the hull):
    the barbette ring under the midships (on the hull), the faceted stealth gunhouse hanging from it (its "roof"
    facing down, the chined sides, a gilded band), the gun port with its blast boot, the long 127 mm/62 barrel with
    its muzzle swell (Gun_barrels* / Gun_muzzles*), the EO director ball, the ammunition hoist trunk, the drain
    louvres. Barrel 28 degrees down; Muzzle_gun.00i at the muzzle."""
    tag = f'_{i:03d}'
    k.lathe(a.part('Vgun_barbettes', 'Armor'), [(1.75, .35), (1.75, 0), (1.62, -.1), (1.5, -.12)], loc=(x, y, z0),
            seg=26)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, z0 - .12))
    house = a.part('Vgun_house' + tag, paint, m)
    k.sharp_loft(house, [octa(1.5, 1.9, 0, .9, .5), octa(1.42, 1.75, -.85, 1.0, .45, .1),
                         octa(.95, 1.1, -1.4, .55, .3, .25)], chamfer=.05)
    k.inset(house, lambda c, nn, f: nn.z > -.85, width=.08, depth=-.016)
    k.ring(a.part('Vgun_band' + tag, mark, m), [(1.47, -.25), (1.5, -.25), (1.5, -.36), (1.47, -.36)], seg=8)
    g = Gun((0, -1.35, -.75), math.radians(28))
    bore(a.part('Vgun_boot' + tag, 'Rubber', m), g, 0, [(.34, -.2), (.34, .1), (.24, .32), (.2, .45)], seg=16)
    bore(a.part('Gun_barrels' + tag, 'Steel', m), g, 0, [(.15, .3), (.15, .8), (.12, .95), (.11, 4.5), (.13, 4.62),
                                                         (.13, 4.8)], seg=16)
    bore(a.part('Gun_muzzles' + tag, 'Armor', m), g, 0, [(.1, 4.8), (.14, 4.82), (.14, 4.92), (.11, 4.95)], seg=16)
    muzzles(a, 'gun', i, g, (0,), 4.95, key)
    a.part('Vgun_eo' + tag, 'Armor', m).sphere(.3, loc=(-.95, -1.0, -1.0), seg=14, rings=8)
    a.part('Glass', 'Glass', m).cyl(.17, .02, loc=(-.95, -1.3, -1.0), rot=(R90, 0, 0), seg=12, bevel=0)
    k.block(a.part('Vgun_trunk' + tag, 'Undercarriage', m), (.9, .8, .45), loc=(0, 1.45, -.4), chamfer=.05,
            ends=(True, True))
    for j in range(5):
        a.part('Vgun_louvres' + tag, 'Undercarriage', m).box((1.1, .08, .04), loc=(0, .6 + j * .2, -1.41), bevel=0)
    K.tone(a, key, k=.9)


def hp_vls(a, i, x, y0, y1, z, w, paint):
    """A Hyperion VLS deckhouse on a sponson ledge (Muzzle_rocket at +X, .001 at -X; the launcher does not turn):
    an armoured box with chamfered ends, two columns of four cell hatches (one lid swung open with the missile's
    nose in its cell), the exhaust uptake between the columns, deck-edge hazard bars, the maintenance access hatch,
    a status lamp. Muzzle_rocket[.00i] just over the open cell."""
    yc = (y0 + y1) / 2
    L = y1 - y0
    k.block(a.part('Vls_houses', 'Titanium'), (w + .2, L + .2, .42), loc=(x, yc, z + .21), chamfer=.08)
    a.part('Vls_decks', paint).box((w - .2, L - .2, .04), loc=(x, yc, z + .44), bevel=0)
    lids = a.part('Vls_lids', 'NavyDeck')
    cw = (w - .5) / 2
    ch = (L - .7) / 4
    open_cell = None
    for col, cx in enumerate((x - cw / 2 - .08, x + cw / 2 + .08)):
        for r_ in range(4):
            cy = y0 + .35 + ch * (r_ + .5)
            if col == (0 if x > 0 else 1) and r_ == 1:
                open_cell = (cx, cy)
                a.part('Vls_cells', 'Charred').box((cw - .1, ch - .1, .02), loc=(cx, cy, z + .47), bevel=0)
                k.lathe(a.part('Vls_missiles', 'PlasterWhite'), [(0, .45), (.12, .32), (.18, .1), (.18, 0)],
                        loc=(cx, cy, z + .2), seg=10)
                lids.box((cw - .12, .06, ch - .12), loc=(cx, cy - ch / 2 + .02, z + .46 + (ch - .12) / 2), bevel=.01)
                continue
            k.block(lids, (cw - .12, ch - .12, .06), loc=(cx, cy, z + .49), chamfer=.02)
            a.part('Vls_lid_marks', 'Hazard').box((.12, .04, .01), loc=(cx, cy - ch / 2 + .14, z + .53), bevel=0)
    a.part('Vls_uptakes', 'Undercarriage').box((.14, L - .9, .1), loc=(x, yc, z + .5), bevel=0)
    for e in (-1, 1):
        a.part('Vls_hazard', 'Hazard').box((w - .3, .08, .02), loc=(x, yc + e * (L / 2 - .12), z + .47), bevel=0)
    K.lamp(a, (x + (w / 2 + .01) * (1 if x > 0 else -1), y1 - .5, z + .15), facing=(1 if x > 0 else -1, 0, 0),
           r=.08, guard=False, glow='Alloy')
    cx, cy = open_cell
    a.pivot(K.name('Muzzle_rocket', i), (cx, cy, z + .75))


# ============================================================================= theia
def th_v35(a, i, x, y, z0, paint, mark='ContainerBlue'):
    """Theia's ventral twin 35 mm turret (Mount_gun at +X, .001 at -X; Oerlikon KDA read): the ring under the hull,
    a compact rounded cupola hanging from it (a blue band), two 35 mm barrels with the Oerlikon multi-port brakes
    (Gun_barrels* / Gun_muzzles*), the ammunition boxes on both cheeks, the tracking radar dish behind, the EO
    window. Barrels 30 degrees down; Muzzle_gun[.001] between the brakes, Muzzle_b1 / _b2."""
    tag = '' if i == 0 else f'_{i:03d}'
    k.lathe(a.part('Vgun_rings', 'Undercarriage'), [(1.0, .3), (1.0, 0), (.92, -.06), (.84, -.06)], loc=(x, y, z0),
            seg=20)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, z0 - .08))
    cup = a.part('Vgun_cupola' + tag, paint, m)
    k.lathe(cup, [(.86, 0), (.9, -.2), (.86, -.5), (.68, -.78), (.36, -.92), (0, -.95)], seg=20, worn=(2,))
    k.inset(cup, lambda c, nn, f: nn.z > -.8, width=.05, depth=-.012)
    k.ring(a.part('Vgun_band' + tag, mark, m), [(.89, -.24), (.92, -.24), (.92, -.36), (.89, -.36)], seg=20)
    g = Gun((0, -.72, -.45), math.radians(30))
    k.block(a.part('Vgun_mantlet' + tag, 'Armor', m), (.8, .3, .4), loc=g.p(0, .1), rot=g.rot, chamfer=.04,
            ends=(True, True))
    xs = (-.22, .22)
    for bx in xs:
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, bx, [(.055, 0), (.055, 1.95), (.05, 2.0)], seg=10)
        bore(a.part('Gun_barrels' + tag, 'Armor', m), g, bx, [(.085, .05), (.085, .55), (.065, .6)], seg=10)
        brk = a.part('Gun_muzzles' + tag, 'Armor', m)
        bore(brk, g, bx, [(.045, 2.0), (.075, 2.02), (.075, 2.26), (.055, 2.28)], seg=10)
        for j in range(4):
            brk.box((.17, .03, .03), loc=g.p(bx, -(2.06 + j * .06)), rot=g.rot, bevel=0)
    muzzles(a, 'gun', i, g, xs, 2.28, key)
    for e in (-1, 1):
        k.block(a.part('Vgun_boxes' + tag, 'Armor', m), (.26, .7, .42), loc=(e * .86, .05, -.42), chamfer=.03,
                ends=(True, True))
    a.part('Vgun_radar' + tag, 'Steel', m).limb((0, .5, -.6), (0, .78, -.88), .06, .06, bevel=0)
    k.lathe(a.part('Vgun_radar' + tag, 'Steel', m), [(0, 0), (.3, .06), (.32, .08), (0, .04)], loc=(0, .82, -.92),
            rot=(R90 * .7, 0, 0), seg=14)
    a.part('Glass', 'Glass', m).box((.2, .02, .12), loc=(.42, -.72, -.55), rot=(.4, 0, 0), bevel=0)
    K.tone(a, key, k=.9)


def th_pods(a, i, x, y, z, paint, mark='ContainerBlue'):
    """A quad missile pod on the front of a Theia hangar pod (Muzzle_rocket at +X, .001 at -X; JAGM read, fixed): a
    saddle bracket on the pod's back, the swivel stub, the launcher frame raised 12 degrees, four canisters in two
    rows with their frangible front caps (one off, the seeker dome showing), the blue band, the umbilical.
    Muzzle_rocket[.00i] at the canisters' front face."""
    tag = '' if i == 0 else f'_{i:03d}'
    k.block(a.part('Pod_saddles', 'Armor'), (1.4, 1.8, .2), loc=(x, y, z), chamfer=.04)
    a.part('Pod_saddles', 'Steel').cyl(.18, .4, loc=(x, y, z + .3), seg=10, bevel=.02)
    g = Gun((x, y, z + .82), math.radians(-12))
    frame = a.part('Jagm_frames' + tag, 'Armor')
    k.block(frame, (1.05, 1.9, .1), loc=g.p(0, 0, -.38), rot=g.rot, chamfer=.02, ends=(True, True))
    for e in (-1, 1):
        frame.box((.06, 1.9, .78), loc=g.p(e * .52, 0, 0), rot=g.rot, bevel=.01)
    can = a.part('Jagm_canisters' + tag, paint)
    caps = a.part('Jagm_caps' + tag, 'Undercarriage')
    for row, cz in enumerate((-.17, .19)):
        for col, cx in enumerate((-.24, .24)):
            bore(can, g, cx, [(.16, -.95), (.17, -.9), (.17, .9), (.16, .95)], z=cz, seg=12)
            if row == 1 and col == (0 if x > 0 else 1):
                k.lathe(a.part('Jagm_seekers' + tag, 'Glass'), [(.12, 0), (.09, .08), (0, .12)],
                        loc=g.p(cx, -.95, cz), rot=g.bore, seg=10)
            else:
                bore(caps, g, cx, [(.165, .95), (.165, .98), (0, .99)], z=cz, seg=12)
    a.part('Jagm_bands' + tag, mark).box((1.0, .14, .8), loc=g.p(0, .55), rot=g.rot, bevel=0)
    a.part('Jagm_umbilicals', 'Charred').tube([g.p(.3, .9, -.3), (x + .3, y + 1.1, z + .2)], .04, seg=5)
    a.pivot(K.name('Muzzle_rocket', i), g.p(0, -1.02))


# ============================================================================= coeus
def co_twin203(a, x, y, z, paint, mark='Hazard', q=1.2):
    """Coeus's dorsal twin 203 mm turret (Turret, the main weapon's mount, where the coil artillery was; Mk 71 read,
    paired): the barbette and bolt ring, a tall angular gunhouse (sloped face plate, raked cheeks, flat roof with
    the rangefinder ears, two cupolas and periscopes, the rear bustle with its vent grille, hazard chevrons on the
    face), two blast bags, the two 203 mm barrels with bore evacuators and muzzle swells (Main_cannon: the barrels,
    Main_cannon_bands, Main_cannon_evacuators). Barrels raised 4 degrees; Muzzle_main between the muzzles,
    Muzzle_b1_main / _b2_main at each."""
    k.lathe(a.part('Turret_barbette', 'Armor'), [(2.7 * q, -.1), (2.7 * q, .2), (2.55 * q, .3)], loc=(x, y, z), seg=32)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .3), (0, 0, 1), 2.6 * q, 28, r=.05, h=.05)
    t = a.pivot('Turret', (x, y, z + .3))
    house = a.part('Turret_house', paint, t)
    rings = [(0, [(-1.6, -3.0), (1.6, -3.0), (2.7, -1.6), (2.7, 2.9), (2.2, 3.5), (-2.2, 3.5), (-2.7, 2.9),
                  (-2.7, -1.6)]),
             (1.55, [(-1.45, -2.2), (1.45, -2.2), (2.5, -1.1), (2.5, 2.7), (2.0, 3.3), (-2.0, 3.3), (-2.5, 2.7),
                     (-2.5, -1.1)]),
             (2.0, [(-1.25, -1.75), (1.25, -1.75), (2.2, -.8), (2.2, 2.5), (1.8, 3.0), (-1.8, 3.0), (-2.2, 2.5),
                    (-2.2, -.8)])]
    k.sharp_loft(house, [[(px * q, py * q, pz * q) for px, py in pts] for pz, pts in rings], chamfer=.08)
    k.inset(house, lambda c, nn, f: c.z > .25, width=.1, depth=-.022)
    hz = a.part('Turret_chevrons', mark, t)
    for e in (-1, 1):
        for j in range(3):
            hz.box((.42, .06, .12), loc=(e * (2.0 + j * .18) * q * .78, -2.6 * q + .02 + j * .2, .45),
                   rot=(.5, 0, e * .5), bevel=0)
    zg = 1.15 * q
    g = Gun((0, -2.55 * q, zg), math.radians(-4))
    xs = (-.85, .85)
    for bx in xs:
        bore(a.part('Turret_bags', 'Rubber', t), g, bx, [(.42, -.3), (.42, .05), (.3, .4), (.26, .55)], seg=14)
        bore(a.part('Main_cannon', 'Steel', t), g, bx, [(.24, .35), (.24, 1.0), (.2, 1.2), (.17, 8.1), (.2, 8.25),
                                                        (.2, 8.6)], seg=16)
        bore(a.part('Main_cannon_evacuators', 'Armor', t), g, bx, [(.17, 3.0), (.25, 3.15), (.25, 4.1), (.17, 4.25)],
             seg=16)
        for d in (1.6, 2.3, 5.4, 6.6):
            bore(a.part('Main_cannon_bands', 'Armor', t), g, bx, [(.2, d), (.215, d + .02), (.215, d + .2),
                                                                  (.2, d + .22)], seg=16)
    a.pivot('Muzzle_main', g.p(0, -8.63), t)
    for j, bx in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{j + 1}_main', (bx, 0, 0), 'Muzzle_main')
    for e in (-1, 1):
        a.part('Turret_ears', 'Armor', t).cyl(.26, .9, loc=(e * 2.9 * q, -.2, 1.55 * q), rot=(0, R90, 0), seg=12,
                                              bevel=.03)
        a.part('Glass', 'Glass', t).cyl(.18, .02, loc=(e * (2.9 * q + .46), -.2, 1.55 * q), rot=(0, R90, 0), seg=10,
                                        bevel=0)
    for cx in (-1.2, 1.2):
        k.lathe(a.part('Turret_cupola', 'Armor', t), [(.5, 0), (.5, .3), (.38, .42), (0, .46)],
                loc=(cx, 1.6, 2.0 * q), seg=14)
        for j in range(5):
            u = -R90 + (j - 2) * .45
            a.part('Turret_periscopes', 'Glass', t).box((.1, .06, .08), loc=(cx + math.cos(u) * .46,
                                                                            1.6 + math.sin(u) * .46, 2.0 * q + .33),
                                                        rot=(0, 0, u), bevel=0)
    k.block(a.part('Turret_bustle', 'Undercarriage', t), (4.2, 1.4, 1.5), loc=(0, 3.5 * q + .5, .85), chamfer=.08,
            ends=(True, True))
    K.grille(a, (0, 3.5 * q + 1.22, .9), 3.2, 1.0, facing=(0, 1, 0), slats=8, parent=t, frame_mat='Armor')
    K.soot(a, (x, y + g.p(0, -8.5)[1], z + .3 + zg), radius=.9, k=.25)


def co_v76(a, i, x, y, z0, paint, mark='Hazard'):
    """Coeus's ventral twin 76 mm turret (Mount_gun at +X, .001 at -X, where the laser batteries were; OTO Melara
    76/62 Super Rapid read, paired): the race under the keel line (on the hull), a faceted gunhouse hanging from it
    with its stealth chines and a hazard edge, two 76 mm barrels in cooling sleeves with the Super Rapid's slotted
    brakes (Gun_barrels* / Gun_muzzles*), the drum magazine fairing aft, the fire-control director box. Barrels 28
    degrees down; Muzzle_gun[.001] between the brakes, Muzzle_b1 / _b2."""
    tag = '' if i == 0 else f'_{i:03d}'
    k.ring(a.part('Vgun_race', 'Steel'), [(1.4, .02), (1.55, .02), (1.55, -.1), (1.4, -.12)], loc=(x, y, z0), seg=24)
    key = K.name('Mount_gun', i)
    m = a.pivot(key, (x, y, z0 - .08))
    house = a.part('Vgun_house' + tag, paint, m)
    k.sharp_loft(house, [octa(1.35, 1.45, 0, .75, .35), octa(1.28, 1.35, -.75, .85, .35, .08),
                         octa(.85, .85, -1.25, .45, .25, .2)], chamfer=.05)
    k.inset(house, lambda c, nn, f: nn.z > -.85, width=.07, depth=-.015)
    a.part('Vgun_edge' + tag, mark, m).box((1.6, .06, .1), loc=(0, -1.4, -.2), bevel=0)
    g = Gun((0, -1.1, -.65), math.radians(28))
    k.block(a.part('Vgun_mantlet' + tag, 'Armor', m), (1.3, .35, .6), loc=g.p(0, .05), rot=g.rot, chamfer=.05,
            ends=(True, True))
    xs = (-.36, .36)
    for bx in xs:
        bore(a.part('Gun_barrels' + tag, 'Steel', m), g, bx, [(.09, 0), (.09, 3.0), (.08, 3.05)], seg=12)
        bore(a.part('Gun_barrels' + tag, 'Armor', m), g, bx, [(.14, .1), (.14, 1.9), (.115, 2.0)], seg=12)
        brk = a.part('Gun_muzzles' + tag, 'Armor', m)
        bore(brk, g, bx, [(.075, 3.05), (.12, 3.07), (.12, 3.34), (.09, 3.36)], seg=12)
        for j in range(3):
            for e in (-1, 1):
                brk.box((.03, .06, .08), loc=g.p(bx + e * .12, -(3.12 + j * .08)), rot=g.rot, bevel=0)
    muzzles(a, 'gun', i, g, xs, 3.36, key)
    k.lathe(a.part('Vgun_magazine' + tag, 'Armor', m), [(.55, 0), (.55, -.35), (.4, -.5), (0, -.52)],
            loc=(0, .85, -.85), seg=16)
    k.block(a.part('Vgun_director' + tag, 'Undercarriage', m), (.4, .5, .4), loc=(-.95, -.6, -.75), chamfer=.04,
            ends=(True, True))
    a.part('Glass', 'Glass', m).box((.28, .02, .18), loc=(-.95, -.86, -.75), bevel=0)
    K.tone(a, key, k=.9)


def co_spike(a, i, x, y, z, paint, mark='Hazard'):
    """A Spike NLOS box launcher on Coeus's hammerhead (Muzzle_rocket at +X, .001 at -X; fixed): the deck mount, the
    erector hinge and hydraulic ram, the armoured box raised 18 degrees with its ribbed sides, two rows of two
    canister lids on the front face (one blown off, the missile's nose showing), hazard markings, the umbilical.
    Muzzle_rocket[.00i] at the front face."""
    k.block(a.part('Spike_mounts', 'Armor'), (1.5, 2.6, .25), loc=(x, y, z), chamfer=.04)
    g = Gun((x, y + .9, z + .25), math.radians(-18))
    box = a.part('Spike_boxes', paint)
    zc = .5
    k.block(box, (1.25, 2.5, .95), loc=g.p(0, -1.1, zc), rot=g.rot, chamfer=.06, ends=(True, True))
    for j in range(4):
        a.part('Spike_ribs', 'Armor').box((1.33, .08, 1.03), loc=g.p(0, -(.25 + j * .55), zc), rot=g.rot, bevel=.01)
    a.part('Spike_hinges', 'Steel').cyl(.12, 1.3, loc=g.p(0, .05, .05), rot=(0, R90, 0), seg=10, bevel=0)
    a.part('Spike_rams', 'Steel').limb((x, y - .9, z + .12), g.p(0, -1.6, .05), .1, .1, bevel=0)
    lids = a.part('Spike_lids', 'Undercarriage')
    for row, cz in enumerate((zc - .24, zc + .24)):
        for col, cx in enumerate((-.3, .3)):
            if row == 0 and col == (1 if x > 0 else 0):
                a.part('Spike_cells', 'Charred').box((.42, .02, .4), loc=g.p(cx, -2.37, cz), rot=g.rot, bevel=0)
                k.lathe(a.part('Spike_noses', 'PlasterWhite'), [(.17, 0), (.15, .1), (.08, .2), (0, .24)],
                        loc=g.p(cx, -2.2, cz), rot=g.bore, seg=10)
                continue
            lids.box((.44, .04, .42), loc=g.p(cx, -2.37, cz), rot=g.rot, bevel=.01)
            a.part('Spike_marks', mark).box((.3, .01, .05), loc=g.p(cx, -2.4, cz + .12), rot=g.rot, bevel=0)
    a.part('Spike_umbilicals', 'Charred').tube([g.p(.5, .05, .3), (x + .55, y + 1.2, z + .14)], .04, seg=5)
    a.pivot(K.name('Muzzle_rocket', i), g.p(0, -2.42, zc))


# ============================================================================= the ships' own paint
def glow_strip(a, mat, pts, w=.06, t=.03, name='Glow_strips'):
    """A thin lit strip along a polyline (heat-exchanger slots, running lights along a belt)."""
    p = a.part(name, mat)
    for p0, p1 in zip(pts, pts[1:]):
        p.limb(p0, p1, w, t, bevel=0)


def livery(a, tints=(), belly=None, panels=None):
    """The ship's own paint after the bake: tints [(name regex, (r, g, b))] (the first rule whose regex matches the
    mesh's or a pivot's name multiplies its COLOR_0), belly (regex, (r, g, b)): the downward faces of the matching
    meshes darkened to heat tiles (smooth over the bilge), panels (regex, cell m, amplitude): plate-to-plate tone
    steps on the matching meshes. Glowing materials are left alone."""
    a._r5_livery = ([(re.compile(p), c) for p, c in tints], belly and (re.compile(belly[0]), belly[1]),
                    panels and (re.compile(panels[0]), panels[1], panels[2]))
    if getattr(a, '_r5_hooked', False):
        return
    a._r5_hooked = True
    original = a.finish

    def finish():
        out = original()
        _apply_livery(a)
        return out
    a.finish = finish


def _hash3(i, j, l):
    h = (i * 73856093) ^ (j * 19349663) ^ (l * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xffff) / 65535.0


def _apply_livery(a):
    tints, belly, panels = a._r5_livery
    for ob in a.objects:
        me = ob.data
        attr = me.color_attributes.get('Col')
        if attr is None or not me.materials or me.materials[0] is None:
            continue
        if me.materials[0].name.split('.')[0] in kit.GLOWING:
            continue
        chain, o = [], ob
        while o is not None:
            chain.append(o.name)
            o = o.parent
        n = len(me.vertices)
        cols = [0.0] * (n * 4)
        attr.data.foreach_get('color', cols)
        mul = next((c for rx, c in tints if any(rx.search(nm) for nm in chain)), None)
        dark = belly is not None and any(belly[0].search(nm) for nm in chain)
        pan = panels is not None and any(panels[0].search(nm) for nm in chain)
        if mul is None and not dark and not pan:
            continue
        off = Vector()
        o = ob.parent
        while o is not None:
            off += o.location
            o = o.parent
        normals = me.vertex_normals
        for v in range(n):
            f = [1.0, 1.0, 1.0]
            if mul is not None:
                f = list(mul)
            if dark:
                nz = normals[v].vector.z
                u = max(0.0, min(1.0, (-nz - .35) / .35))
                if u > 0:
                    f = [f[c] * (1 - u + u * belly[1][c]) for c in range(3)]
            if pan:
                p = off + me.vertices[v].co
                cell = panels[1]
                h = _hash3(int(math.floor(p.x / cell)), int(math.floor(p.y / cell)), int(math.floor(p.z / cell)))
                t = 1 + panels[2] * (h - .5) * 2
                f = [c * t for c in f]
            for c in range(3):
                cols[v * 4 + c] = max(0.0, min(1.0, cols[v * 4 + c] * f[c]))
        attr.data.foreach_set('color', cols)
