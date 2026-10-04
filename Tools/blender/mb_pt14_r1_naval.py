"""Play-test 14 boss redraw R1 (lane models): the bespoke weapons, towers and sensors of the redrawn sea bosses.

Owner (04/10, Docs/prompts/playtest14_vi.txt, last block): the turrets on the redrawn bosses looked reused and did not
fit ("đừng reuse gì hết, tất cả boss khi vẽ lại đều vẽ lại từ đầu"); Nyx's railgun goes, a naval gun turret takes its
mount. Audit: Docs/models/pt14_reuse_audit.md; DECISIONS "Play-test 14 boss redraw R1 (lane models)".

Every function here draws for one boss only (no other model calls it), from geometry primitives, at that boss's
scale, read from a real design:
- Leviathan (an Iowa-class battleship after its 1980s refit): the 16"/50 Mk 7 triple turrets (sloped face plate,
  canvas bloomers, rangefinder ears, sight hoods, officer's cupola), the 155 mm triples that sleep in hull wells (a
  Mogami / Yamato 15.5 cm read: rounded front, the rangefinder across the rear), the twin 5"/38 Mk 38 mounts, the
  Phalanx Block 1B, the Type 96 triple 25 mm with its top magazines, the Mk 13 single-arm SAM launcher, the Mk 37
  directors with their Mk 12 / Mk 22 radars, the SPS-49 search radar, the Mk 143 armoured box launchers.
- Scylla (a Slava-class cruiser): the AK-130 twin, the AK-100 single, the AK-630 gatlings, the Top Pair radar.
- Nyx (a Zumwalt read): the AGS-style 155 mm stealth turret, the Mk 110-style stealth cupolas, the peripheral VLS
  modules, the Fire Scout-style deck drone.

Runtime names are the ones each mount had (Part_* / Mount_* / Muzzle_* / Radar; the barrels a mount kicks are its
pivot's `<word>_barrels` / `<word>_muzzles` parts, ModelLibrary.IsMountBarrel). Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= small helpers (geometry only)
def per_barrel(a, muzzle, tag, xs):
    """Muzzle_b<k>_<tag> under the pivot `muzzle`, one per barrel at the x offsets `xs` (left to right)."""
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def fwd(part, profile, loc, seg=14):
    """A turned part along -Y (the front): profile [(radius, distance forward)] from loc."""
    k.lathe(part, profile, loc=loc, rot=K.FORWARD, seg=seg)


def along_x(part, profile, loc, seg=12):
    k.lathe(part, profile, loc=loc, rot=(0, R90, 0), seg=seg)


def slab(part, p0, p1, w, t):
    """A flat plate from p0 to p1 (its length), `w` wide across (in the plane perpendicular to Z x length), `t` thick."""
    part.limb(p0, p1, w, t, bevel=0)


def bloomer(part, x, y, z, r, seg=12):
    """A canvas blast bag where a barrel leaves its port: three folds, wider at the face, gathered on the barrel."""
    fwd(part, [(r * 2.3, 0), (r * 2.55, .1), (r * 2.25, .2), (r * 2.4, .3), (r * 2.0, .42), (r * 1.95, .5),
               (r * 1.45, .62), (r * 1.15, .66)], (x, y, z), seg=seg)


def hood(a, part, glass, loc, w, d, h, rake=.45, parent=None):
    """A sight hood on a turret roof: an armoured box with its front raked back and the glass slit in it."""
    x, y, z = loc
    k.extrude(part, [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], h, loc=(x, y, z + h / 2),
              axis='Z', chamfer=min(.04, h * .2), taper=(1, 1 - rake * h / d))
    a.part('Glass', 'Glass', parent).box((w * .7, .02, h * .3), loc=(x, y - d / 2 + rake * h * .275 - .012, z + h * .55),
                                         rot=(-math.atan(rake / 2), 0, 0), bevel=0)


# ============================================================================= Leviathan
def lev_main_turret(a, index, part_loc, mount_z, barbette_base=-.05):
    """A 16"/50 Mk 7 triple turret (Iowa) under Part_gun[.NNN]: the barbette with its armour ring, the gunhouse on
    Mount_gun[.NNN] (a long slab-sided house, the sloped face plate with three ports and canvas bloomers, the cheek
    plates, the flat roof with its plates, the pointer's and trainer's hoods forward, the officer's cupola aft, the
    rangefinder ears either side of the rear, the overhang with the rear door, roof vents and the ladder), three
    tapered barrels with the muzzle swell (Gun_barrels* / Gun_muzzles*, the kick parts), Muzzle_gun at the middle
    barrel's tip and the per-barrel muzzles."""
    pname = K.name('Part_gun', index)
    tag = '' if index == 0 else f'_{index:03d}'
    p = a.pivot(pname, part_loc)
    px, py, pz = part_loc
    lz = mount_z - pz
    br = 3.45
    bar = a.part('Gun_barbette' + tag, 'Armor', p)
    k.lathe(bar, [(br, barbette_base), (br, lz - .3), (br + .06, lz - .26), (br + .06, lz - .1), (br - .05, lz - .04),
                  (br - .05, lz)], seg=32)
    bolts = a.part('Kit_bolts', 'Steel', p)
    for i in range(32):
        u = (i + .5) * TAU / 32
        bolts.cyl(.05, .05, loc=(math.cos(u) * (br + .07), math.sin(u) * (br + .07), lz - .18), rot=(0, R90, u), seg=6,
                  bevel=0)
    m = a.pivot(K.name('Mount_gun', index), (0, 0, lz), p)
    k.ring(a.part('Gun_ring' + tag, 'Steel', m), [(br - .2, -.04), (br - .12, -.04), (br - .12, .1), (br - .2, .1)],
           seg=32)
    # The gunhouse: base plan, a mid ring and the roof ring; the face slopes back ~20 degrees, the sides 2.
    H = 2.45
    base = [(-2.25, -3.45), (2.25, -3.45), (3.3, -2.35), (3.3, 4.2), (3.05, 4.55), (-3.05, 4.55), (-3.3, 4.2),
            (-3.3, -2.35)]

    def ring_at(z):
        f = z / H
        return [(x * (1 - .045 * f), y + (.9 * f if y < -2 else (-.06 * f if y > 4 else 0)), z) for x, y in base]
    k.sharp_loft(a.part('Gun_house' + tag, 'Team', m), [ring_at(0), ring_at(H * .5), ring_at(H)], chamfer=.08)
    k.inset(a.part('Gun_house' + tag, 'Team', m), lambda c, n, f: abs(n.z) < .3 and c.z > .25 and n.y > -.5,
            width=.14, depth=-.03)
    # The face plate (Armor, its own slab proud of the house), the three ports, the bloomers.
    face = a.part('Gun_face' + tag, 'Armor', m)
    tilt = math.atan2(.9, H)
    k.block(face, (4.3, .16, H - .1), loc=(0, -3.03, H / 2 - .02), rot=(-tilt, 0, 0), chamfer=.05,
            taper=(.94, 1), ends=(True, True))
    zg, gap = 1.22, 1.78
    xs = (-gap, 0, gap)
    ports = a.part('Gun_ports' + tag, 'Undercarriage', m)
    yf = -3.45 + .9 * zg / H
    for x in xs:
        ports.box((.62, .1, .95), loc=(x, yf - .11, zg + .08), rot=(-tilt, 0, 0), bevel=.03)
        bloomer(a.part('Gun_bloomers' + tag, 'Canvas', m), x, yf - .14, zg, .27)
    # Bolt rows across the face plate.
    bolts_m = a.part('Kit_bolts', 'Steel', m)
    for zb in (.25, H - .3):
        for i in range(13):
            x = -1.95 + i * .325
            bolts_m.cyl(.035, .03, loc=(x, -3.45 + .9 * zb / H - .1, zb), rot=(R90 - tilt, 0, 0), seg=6, bevel=0)
    # The roof: plates with seams, the hoods, the cupola, the vents, the hatches.
    roof = a.part('Gun_roof' + tag, 'Armor', m)
    top = [(x * .93, y * .93 + .12) for x, y, _ in ring_at(H)]
    k.extrude(roof, top, .08, loc=(0, 0, H + .04), axis='Z', chamfer=.03)
    for y in (-1.0, 1.0, 3.0):
        a.part('Gun_roof_seams' + tag, 'Steel', m).box((5.6, .05, .03), loc=(0, y, H + .095), bevel=0)
    hoods = a.part('Gun_hoods' + tag, 'Armor', m)
    # Roof fittings stay out of the lanes a superfiring turret's barrels pass over (x = 0, +-1.78, +-0.32).
    for x in (-2.6, 2.6):
        hood(a, hoods, None, (x, -1.75, H + .08), .62, 1.0, .5, parent=m)
    hood(a, hoods, None, (-.95, -1.55, H + .08), .5, .8, .36, parent=m)
    k.lathe(a.part('Gun_cupola' + tag, 'Armor', m), [(.5, 0), (.5, .28), (.4, .38), (.2, .44), (0, .46)],
            loc=(.9, 2.2, H + .08), seg=16)
    for j in range(5):
        u = -R90 + (j - 2) * .5
        a.part('Gun_periscopes' + tag, 'Steel', m).box((.12, .12, .14), loc=(.9 + math.cos(u) * .4,
                                                                            2.2 + math.sin(u) * .4, H + .4),
                                                       rot=(0, 0, u), bevel=0)
    vents = a.part('Gun_vents' + tag, 'Steel', m)
    for x in (-2.6, -.9):
        k.lathe(vents, [(.22, 0), (.22, .28), (.34, .32), (.34, .42), (.12, .46), (0, .46)], loc=(x, 3.7, H + .08),
                seg=10)
    hatch = a.part('Gun_hatches' + tag, 'Steel', m)
    for x in (-1.0, 2.55):
        k.block(hatch, (.85, .75, .1), loc=(x, 3.75, H + .1), chamfer=.03)
        a.part('Kit_handles', 'Steel', m).box((.3, .04, .06), loc=(x, 3.48, H + .18), bevel=0)
    # Rangefinder ears either side of the rear: the tube across the house, the armoured end hoods.
    along_x(a.part('Gun_rangefinder' + tag, 'Steel', m), [(0, -4.45), (.26, -4.42), (.3, -4.2), (.3, 4.2),
                                                         (.26, 4.42), (0, 4.45)], (0, 2.95, 1.55), seg=12)
    ears = a.part('Gun_ears' + tag, 'Armor', m)
    for s in (-1, 1):
        k.extrude(ears, [(-.6, -.5), (.55, -.5), (.6, .35), (.3, .5), (-.6, .5)], 1.0, loc=(s * 3.85, 2.95, 1.55),
                  axis='X', chamfer=.05)
        a.part('Glass', 'Glass', m).box((.5, .04, .22), loc=(s * 4.0, 2.42, 1.6), bevel=0)
        a.part('Gun_ear_braces' + tag, 'Steel', m).limb((s * 3.3, 2.6, .9), (s * 3.75, 2.75, 1.15), .1, .1, bevel=0)
    # The overhang's rear plate, the rear door, the ladder up the right quarter.
    k.block(a.part('Gun_rear' + tag, 'Armor', m), (5.9, .12, H - .4), loc=(0, 4.58, H / 2 + .1), chamfer=.03,
            ends=(True, True))
    K.door(a, (1.4, 4.66, .3), size=(.85, 1.5), normal=(0, 1, 0), parent=m, mat='Armor', frame_mat='Steel')
    K.ladder(a.part('Ladders', 'Steel', m), (-3.34, 3.4, .25), (-3.34, 3.4, H), width=.45, step=.32, facing=(1, 0))
    a.part('Team_band', 'Team', m).box((4.6, .9, .03), loc=(0, .9, H + .1), bevel=0)
    # Three tapered barrels with the muzzle swell (kick parts), the bore at the crown.
    L = 9.5
    y0 = yf - .1
    for x in xs:
        fwd(a.part('Gun_barrels' + tag, 'Steel', m), [(.4, -.3), (.4, .25), (.33, .35), (.31, 2.0), (.27, 5.5),
                                                       (.235, L - .6), (.26, L - .35), (.265, L - .08), (.25, L)],
            (x, y0, zg), seg=16)
        fwd(a.part('Gun_muzzles' + tag, 'Undercarriage', m), [(.17, L - .02), (.245, L - .02), (.245, L + .01),
                                                               (.17, L + .01)], (x, y0, zg), seg=14)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .1, zg), m)
    per_barrel(a, mz, f'gun_{index:03d}' if index else 'gun', xs)
    K.soot(a, (px, py + y0 - L, mount_z + zg), radius=1.1, k=.4)
    K.tone(a, pname, k=.92)
    return m


def lev_sec_turret(a, index, pname, part_loc, mount_z):
    """A 155 mm triple (a Mogami / Yamato 15.5 cm read) that sleeps in its hull well (the well is drawn by the
    caller): the gunhouse on Mount_gun.00N with its rounded front, straight sides and flat rear, the sloped roof,
    the rangefinder across the rear with its end hoods, the layer's hood, three barrels (Sec_barrels* /
    Sec_muzzles*, the kick parts) in bloomers, Muzzle_gun.00N and the per-barrel muzzles. Kept under 1.9 m tall so
    the whole gunhouse goes into the 2.05 m well (VehicleView.WakeMounts)."""
    tag = f'_{index:03d}'
    px, py, pz = part_loc
    lz = mount_z - pz
    m = a.pivot(K.name('Mount_gun', index), (0, 0, lz), pname)
    k.ring(a.part('Sec_ring' + tag, 'Steel', m), [(1.86, -.03), (1.95, -.03), (1.95, .08), (1.86, .08)], seg=28)
    H = 1.3
    nose = [(math.sin(u) * 1.3, -1.25 - math.cos(u) * .55) for u in (-1.2, -.6, 0, .6, 1.2)]
    # Every corner inside r 1.95, so the gunhouse turns inside its well (inner radius 2.06).
    base = [nose[2]] + nose[3:] + [(1.4, -.6), (1.4, 1.0), (1.0, 1.6), (-1.0, 1.6), (-1.4, 1.0), (-1.4, -.6)] + nose[:2]

    def ring_at(z):
        f = z / H
        return [(x * (1 - .08 * f), y * (1 - .1 * f) + (.15 * f if y < 0 else 0), z) for x, y in base]
    k.sharp_loft(a.part('Sec_house' + tag, 'Team', m), [ring_at(0), ring_at(H * .55), ring_at(H)], chamfer=.05)
    k.extrude(a.part('Sec_roof' + tag, 'Armor', m), [(x * .92, y * .92 + .05) for x, y, _ in ring_at(H)], .06,
              loc=(0, 0, H + .03), axis='Z', chamfer=.02)
    zg, gap = .66, .56
    xs = (-gap, 0, gap)
    a.part('Sec_ports' + tag, 'Undercarriage', m).box((1.5, .12, .5), loc=(0, -1.73, zg + .05), rot=(-.12, 0, 0),
                                                      bevel=.02)
    for x in xs:
        bloomer(a.part('Sec_bloomers' + tag, 'Canvas', m), x, -1.78, zg, .1, seg=10)
    # The rangefinder across the rear (ears out past the sides), its end hoods; the layer's hood forward on the roof.
    along_x(a.part('Sec_rangefinder' + tag, 'Steel', m), [(0, -1.8), (.13, -1.78), (.15, -1.65), (.15, 1.65),
                                                         (.13, 1.78), (0, 1.8)], (0, .35, 1.0), seg=10)
    for s in (-1, 1):
        k.extrude(a.part('Sec_ears' + tag, 'Armor', m), [(-.28, -.22), (.26, -.22), (.28, .2), (-.28, .25)], .38,
                  loc=(s * 1.58, .35, 1.0), axis='X', chamfer=.03)
        a.part('Glass', 'Glass', m).box((.24, .03, .1), loc=(s * 1.62, .06, 1.02), bevel=0)
    hood(a, a.part('Sec_hoods' + tag, 'Armor', m), None, (.55, -.45, H + .06), .42, .55, .26, parent=m)
    k.block(a.part('Sec_hatches' + tag, 'Steel', m), (.55, .5, .07), loc=(-.5, .9, H + .07), chamfer=.02)
    k.block(a.part('Sec_rear' + tag, 'Armor', m), (1.8, .08, .95), loc=(0, 1.62, .55), chamfer=.02, ends=(True, True))
    for s in (-1, 1):
        a.part('Kit_handles', 'Steel', m).box((.04, .5, .04), loc=(s * 1.41, .6, .95), bevel=0)
    L = 5.9
    y0 = -1.8
    for x in xs:
        fwd(a.part('Sec_barrels' + tag, 'Steel', m), [(.15, -.2), (.15, .2), (.12, .3), (.11, 2.0), (.088, L - .3),
                                                       (.1, L - .18), (.1, L - .03), (.09, L)], (x, y0, zg), seg=12)
        fwd(a.part('Sec_muzzles' + tag, 'Undercarriage', m), [(.055, L - .02), (.09, L - .02), (.09, L + .01),
                                                               (.055, L + .01)], (x, y0, zg), seg=10)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .08, zg), m)
    per_barrel(a, mz, f'gun_{index:03d}', xs)
    K.soot(a, (px, py + y0 - L, mount_z + zg), radius=.5, k=.35)
    K.tone(a, pname, k=.92)
    return m


def lev_dp_twin(a, mount, muzzle, loc, parent, tag):
    """A twin 5"/38 Mk 38 enclosed mount (the 127 mm of the Iowa refit): the base ring, the shield (sloped front,
    flat roof, rounded rear corners), the two barrels (Dp_barrels*, the kick parts) in their bloomers, the pointer's
    and trainer's hoods on the roof's front corners, the officer's hatch, the rear access door; Muzzle_* between the
    tips with the per-barrel muzzles."""
    m = a.pivot(mount, loc, parent)
    k.lathe(a.part('Dp_ring' + tag, 'Steel', m), [(1.12, -.02), (1.12, .1), (1.04, .14)], seg=20)
    H = 1.45
    base = [(-.8, -1.35), (.8, -1.35), (1.12, -1.05), (1.12, 1.25), (.95, 1.5), (-.95, 1.5), (-1.12, 1.25),
            (-1.12, -1.05)]

    def ring_at(z):
        f = z / H
        return [(x * (1 - .05 * f), y + (.45 * f if y < -1 else 0), z) for x, y in base]
    k.sharp_loft(a.part('Dp_house' + tag, 'Team', m), [ring_at(.1), ring_at(.75), ring_at(H)], chamfer=.05)
    k.extrude(a.part('Dp_roof' + tag, 'Armor', m), [(x * .94, y * .94 + .04) for x, y, _ in ring_at(H)], .05,
              loc=(0, 0, H + .02), axis='Z', chamfer=.015)
    zg, gap = .66, .62
    xs = (-gap / 2, gap / 2)
    yf = -1.35 + .45 * zg / H
    tilt = math.atan2(.45, H)
    a.part('Dp_port' + tag, 'Undercarriage', m).box((1.2, .08, .5), loc=(0, yf - .03, zg + .03), rot=(-tilt, 0, 0),
                                                    bevel=.02)
    for x in xs:
        bloomer(a.part('Dp_bloomers' + tag, 'Canvas', m), x, yf - .05, zg, .085, seg=10)
    for s in (-1, 1):
        hood(a, a.part('Dp_hoods' + tag, 'Armor', m), None, (s * .72, -.55, H + .05), .38, .5, .26, parent=m)
    k.block(a.part('Dp_hatch' + tag, 'Steel', m), (.5, .45, .06), loc=(0, .7, H + .06), chamfer=.02)
    K.door(a, (.45, 1.5, .25), size=(.5, .9), normal=(0, 1, 0), parent=m, mat='Armor', frame_mat='Steel')
    for s in (-1, 1):
        a.part('Kit_handles', 'Steel', m).box((.04, .6, .04), loc=(s * 1.13, .3, 1.05), bevel=0)
    L = 4.2
    y0 = yf - .1
    for x in xs:
        fwd(a.part('Dp_barrels' + tag, 'Steel', m), [(.11, -.2), (.11, .15), (.085, .25), (.08, 1.4), (.068, L - .2),
                                                      (.075, L - .1), (.075, L)], (x, y0, zg), seg=10)
        fwd(a.part('Dp_muzzles' + tag, 'Undercarriage', m), [(.04, L - .01), (.074, L - .01), (.074, L + .01),
                                                              (.04, L + .01)], (x, y0, zg), seg=8)
    mz = a.pivot(muzzle, (0, y0 - L - .05, zg), m)
    per_barrel(a, mz, 'mg' + tag, xs)
    return m


def lev_ciws(a, loc, parent=None, s=1.0):
    """A Phalanx Block 1B beside a 5-inch mount (decoration: the APS's guns): the deck base, the mount's cradle, the
    white radome with the search antenna's bump and the track antenna under it, the FLIR on its side arm, the six
    barrels in their clamp with the muzzle shroud, the ammunition drum under the gun."""
    x, y, z = loc
    k.lathe(a.part('Ciws_base', 'Armor', parent), [(.62 * s, 0), (.6 * s, .35 * s), (.5 * s, .42 * s)], loc=loc, seg=14)
    k.block(a.part('Ciws_cradle', 'Steel', parent), (.95 * s, .9 * s, .35 * s), loc=(x, y + .05 * s, z + .6 * s),
            chamfer=.04 * s)
    for e in (-1, 1):
        k.block(a.part('Ciws_cradle', 'Steel', parent), (.12 * s, .7 * s, .55 * s),
                loc=(x + e * .42 * s, y + .05 * s, z + .95 * s), chamfer=.02 * s)
    dome = a.part('Ciws_radome', 'PlasterWhite', parent)
    k.lathe(dome, [(.42 * s, 0), (.44 * s, .5 * s), (.4 * s, .78 * s), (.28 * s, .95 * s), (0, 1.02 * s)],
            loc=(x, y + .15 * s, z + 1.15 * s), seg=16)
    k.block(dome, (.42 * s, .3 * s, .32 * s), loc=(x, y - .27 * s, z + 1.85 * s), chamfer=.06 * s, taper=(.8, .6))
    a.part('Ciws_radome_band', 'Steel', parent).cyl(.45 * s, .06 * s, loc=(x, y + .15 * s, z + 1.17 * s), seg=16,
                                                    bevel=0)
    # The FLIR on its arm (left side), the electronics box behind.
    a.part('Ciws_flir', 'Armor', parent).limb((x + .42 * s, y + .1 * s, z + 1.3 * s), (x + .62 * s, y - .1 * s, z + 1.3 * s),
                                             .1 * s, .1 * s, bevel=0)
    k.block(a.part('Ciws_flir', 'Armor', parent), (.24 * s, .3 * s, .24 * s), loc=(x + .7 * s, y - .2 * s, z + 1.18 * s),
            chamfer=.02 * s)
    a.part('Glass', 'Glass', parent).box((.16 * s, .02, .12 * s), loc=(x + .7 * s, y - .36 * s, z + 1.3 * s), bevel=0)
    # The gun: six barrels round the rotor axis, the mid clamp and the muzzle shroud; the drum under it.
    g = a.part('Ciws_gun', 'Steel', parent)
    zg = z + 1.0 * s
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.022 * s, 1.35 * s, loc=(x + math.cos(u) * .06 * s, y - .95 * s, zg + math.sin(u) * .06 * s),
              rot=K.FORWARD, seg=5, bevel=0)
    g.cyl(.11 * s, .1 * s, loc=(x, y - .75 * s, zg), rot=K.FORWARD, seg=10, bevel=0)
    k.lathe(a.part('Ciws_shroud', 'Undercarriage', parent), [(.1 * s, 0), (.11 * s, .05 * s), (.11 * s, .28 * s),
                                                            (.08 * s, .3 * s)], loc=(x, y - 1.35 * s, zg), rot=K.FORWARD,
            seg=12)
    a.part('Ciws_drum', 'Armor', parent).cyl(.22 * s, .9 * s, loc=(x, y + .05 * s, zg - .3 * s), rot=(R90, 0, 0), seg=14,
                                             bevel=.02)


def lev_aa25(a, mount, muzzle, loc, parent, tag):
    """A Type 96 triple 25 mm (Yamato's light AA): the pedestal, the carriage, three receivers with their curved
    15-round magazines standing on top, the barrels with the flash hiders, the layer's and trainer's seats either
    side with their handwheels, the ring sight on its post; Muzzle_mg.00N at the middle barrel's tip."""
    m = a.pivot(mount, loc, parent)
    k.lathe(a.part('Aa_pedestal' + tag, 'Armor', m), [(.45, -.3), (.45, -.2), (.34, -.12), (.24, .2), (.28, .26)],
            seg=12)
    k.block(a.part('Aa_carriage' + tag, 'Team', m), (.82, .62, .22), loc=(0, .05, .3), chamfer=.03)
    rec = a.part('Aa_receivers' + tag, 'Steel', m)
    mags = a.part('Aa_magazines' + tag, 'Crate', m)
    guns = a.part('Aa_guns' + tag, 'Steel', m)
    for x in (-.19, 0, .19):
        k.block(rec, (.13, .78, .18), loc=(x, .02, .41), chamfer=.02, ends=(True, True))
        # The curved box magazine: three slabs leaning back, stacked as a curve.
        for j, (dy, dz, rx) in enumerate(((-.02, .55, -.15), (.03, .66, -.32), (.1, .76, -.5))):
            mags.box((.1, .16, .13), loc=(x, dy, dz), rot=(rx, 0, 0), bevel=.01)
        fwd(guns, [(.045, 0), (.045, .25), (.03, .3), (.03, 1.42), (.045, 1.44), (.05, 1.62), (.032, 1.64)],
            (x, -.36, .43), seg=8)
    for s in (-1, 1):
        a.part('Aa_seats' + tag, 'Rubber', m).box((.24, .2, .06), loc=(s * .62, .32, .26), bevel=.02)
        a.part('Aa_seats' + tag, 'Rubber', m).box((.22, .05, .22), loc=(s * .62, .44, .38), rot=(-.25, 0, 0), bevel=.02)
        a.part('Aa_arms' + tag, 'Steel', m).limb((s * .41, .2, .26), (s * .62, .3, .22), .05, .05, bevel=0)
        a.part('Aa_wheels' + tag, 'Steel', m).torus(.11, .018, loc=(s * .52, -.05, .45), rot=(0, R90, 0), seg=10, ring=4)
    a.part('Aa_sight' + tag, 'Steel', m).cyl(.012, .35, loc=(.3, -.2, .68), seg=4, bevel=0)
    a.part('Aa_sight' + tag, 'Steel', m).torus(.08, .01, loc=(.3, -.2, .88), rot=(R90, 0, 0), seg=10, ring=3)
    a.pivot(muzzle, (0, -2.02, .43), m)
    return m


def lev_sam(a, loc):
    """The Mk 13 single-arm launcher (the "one-armed bandit") for the SAM (Mount_missile): the deck ring over the
    round magazine with its loader doors, the guide stand that trains, the single arm elevated with an SM-1 on its
    rail (the long strakes, the tail fins), the blast deflector; Muzzle_missile at the missile's nose."""
    x, y, z = loc
    k.lathe(a.part('Sam_deck', 'Armor'), [(1.45, -.25), (1.45, 0), (1.32, .06), (1.0, .07)], loc=loc, seg=24)
    k.ring(a.part('Sam_deck_ring', 'Steel'), [(1.0, .07), (1.08, .07), (1.08, .12), (1.0, .12)], loc=loc, seg=24)
    for e in (-1, 1):
        a.part('Sam_doors', 'Hazard').box((.5, .9, .04), loc=(x + e * .28, y - 1.0, z + .09), bevel=0)
    m = a.pivot('Mount_missile', (x, y, z + .1))
    k.lathe(a.part('Sam_stand', 'Team', m), [(.85, 0), (.85, .12), (.62, .3), (.5, .95), (.56, 1.0), (.56, 1.1)],
            seg=18)
    k.block(a.part('Sam_trunnion', 'Team', m), (1.0, .8, .45), loc=(0, .05, 1.15), chamfer=.05)
    for e in (-1, 1):
        a.part('Sam_trunnion', 'Team', m).cyl(.2, .12, loc=(e * .56, .05, 1.38), rot=(0, R90, 0), seg=12, bevel=0)
    el = .26
    d = Vector((0, -math.cos(el), math.sin(el)))
    pivot = Vector((0, .05, 1.4))
    arm = a.part('Sam_arm', 'Steel', m)
    arm.limb(tuple(pivot + d * -.6), tuple(pivot + d * 3.0), .3, .26, bevel=.02)
    up = Vector((0, math.sin(el), math.cos(el)))
    a.part('Sam_rail', 'Undercarriage', m).limb(tuple(pivot + d * -.2 + up * .16),
                                                tuple(pivot + d * 2.9 + up * .16), .12, .06, bevel=0)
    a.part('Sam_blast', 'Armor', m).limb(tuple(pivot + d * -.7 + Vector((0, 0, -.5))),
                                         tuple(pivot + d * -.7 + Vector((0, 0, .5))), .9, .06, bevel=.01)
    # The missile under the rail: body, ogive, strakes, tail fins.
    # The missile rides on the rail (the real Mk 13 slings it under; on top it reads from the battle camera).
    c0 = pivot + d * -.3 + up * .36
    msl = a.part('Sam_missiles', 'PlasterWhite', m)
    k.lathe(msl, [(0, -.05), (.12, -.04), (.15, .05), (.15, 2.7), (.13, 3.05), (.08, 3.3), (0, 3.45)],
            loc=tuple(c0), rot=(R90 - el, 0, 0), seg=12)
    fins = a.part('Sam_fins', 'Steel', m)
    for t0, t1, w in ((.6, 2.2, .13), (0.0, .35, .26)):
        for e in (-1, 1):
            off = Vector((e * .2, 0, 0))
            fins.limb(tuple(c0 + d * t0 + off), tuple(c0 + d * t1 + off), w, .02, bevel=0)
            off = up * (e * .2)
            fins.limb(tuple(c0 + d * t0 + off), tuple(c0 + d * t1 + off), .02, w, bevel=0)
    a.part('Sam_band', 'Hazard', m).cyl(.155, .1, loc=tuple(c0 + d * 2.4), rot=(R90 - el, 0, 0), seg=12, bevel=0)
    a.pivot('Muzzle_missile', tuple(c0 + d * 3.5), 'Mount_missile')
    K.tone(a, 'Mount_missile', k=.9)
    return m


def lev_director(a, loc, parent=None, tag='', s=1.0):
    """A Mk 37 gun director: the drum base, the box house with its raked front and the window slits, the stereo
    rangefinder through it with the ear hoods, the Mk 12 radar's rectangular mesh reflector on top with the
    narrow Mk 22 "orange peel" beside it, the hatch and the hand rail."""
    x, y, z = loc
    k.lathe(a.part('Director_base' + tag, 'Armor', parent), [(.75 * s, 0), (.75 * s, .35 * s), (.85 * s, .4 * s)],
            loc=loc, seg=16)
    hs = a.part('Director' + tag, 'Team', parent)
    prof = [(-.95 * s, 0), (.95 * s, 0), (.95 * s, 1.0 * s), (-.55 * s, 1.0 * s), (-.95 * s, .55 * s)]
    k.extrude(hs, prof, 1.6 * s, loc=(x, y, z + .4 * s), rot=(0, 0, 0), axis='X', chamfer=.05 * s)
    a.part('Glass', 'Glass', parent).box((1.3 * s, .03, .12 * s), loc=(x, y - .78 * s, z + 1.15 * s),
                                         rot=(-.73, 0, 0), bevel=0)
    along_x(a.part('Director_rf' + tag, 'Steel', parent), [(0, -1.6 * s), (.13 * s, -1.58 * s), (.15 * s, -1.4 * s),
                                                          (.15 * s, 1.4 * s), (.13 * s, 1.58 * s), (0, 1.6 * s)],
            (x, y + .2 * s, z + .95 * s), seg=10)
    for e in (-1, 1):
        k.block(a.part('Director_ears' + tag, 'Armor', parent), (.3 * s, .45 * s, .38 * s),
                loc=(x + e * 1.42 * s, y + .2 * s, z + .78 * s), chamfer=.03 * s)
    # The Mk 12: a curved rectangular mesh; the Mk 22 beside it on the right.
    zr = z + 1.5 * s
    fr = a.part('Director_radar' + tag, 'Steel', parent)
    for i in range(4):
        zz = zr + .15 * s + i * .22 * s
        pts = [(x + u * .8 * s, y - .1 * s - (u * u) * .18 * s, zz) for u in (-1, -.5, 0, .5, 1)]
        fr.tube(pts, .02 * s, seg=4)
    for u in (-1, -.5, 0, .5, 1):
        fr.tube([(x + u * .8 * s, y - .1 * s - u * u * .18 * s, zr + .12 * s),
                 (x + u * .8 * s, y - .1 * s - u * u * .18 * s, zr + .85 * s)], .02 * s, seg=4)
    a.part('Director_radar_face' + tag, 'Undercarriage', parent).box((1.55 * s, .02, .7 * s),
                                                                    loc=(x, y - .02 * s, zr + .48 * s), bevel=0)
    fr.limb((x, y + .05 * s, z + 1.4 * s), (x, y + .35 * s, zr + .5 * s), .1 * s, .1 * s, bevel=0)
    k.lathe(a.part('Director_peel' + tag, 'Medical', parent), [(0, 0), (.14 * s, .03 * s), (.22 * s, .12 * s)],
            loc=(x - .95 * s, y - .05 * s, zr + .5 * s), rot=K.FORWARD, seg=10)
    a.part('Director_peel' + tag, 'Medical', parent).box((.04 * s, .1 * s, .8 * s), loc=(x - .95 * s, y - .02 * s,
                                                                                        zr + .5 * s), bevel=0)
    k.block(a.part('Director_hatch' + tag, 'Steel', parent), (.5 * s, .45 * s, .05 * s),
            loc=(x + .4 * s, y + .45 * s, z + 1.42 * s), chamfer=.01)


def lev_radar(a, pivot_name, loc, parent):
    """The SPS-49 air-search radar (`Radar` spins): the drive pedestal, the curved mesh reflector (its frame,
    the crossing bars and the mesh face), the feed horn on its boom, the IFF bar along the top."""
    r = a.pivot(pivot_name, loc, parent)
    k.lathe(a.part('Radar_drive', 'Steel', r), [(.32, 0), (.32, .3), (.22, .38), (.22, .55)], seg=12)
    W, Hh = 4.0, 1.5
    fr = a.part('Radar_frame', 'Armor', r)
    rows = []
    for j in range(4):
        z = .62 + j * Hh / 3
        pts = [(u * W / 2, .25 - (u * u) * .45 + (z - .62) * .12, z) for u in (i / 4 - 1 for i in range(9))]
        rows.append(pts)
        fr.tube(pts, .035, seg=4)
    for i in range(9):
        fr.tube([rows[j][i] for j in range(4)], .03 if i % 2 else .045, seg=4)
    face = a.part('Radar_mesh', 'Undercarriage', r)
    for j in range(3):
        for i in range(8):
            p00, p01, p10, p11 = rows[j][i], rows[j][i + 1], rows[j + 1][i], rows[j + 1][i + 1]
            face.mesh([tuple(Vector(p) + Vector((0, .012, 0))) for p in (p00, p01, p11, p10)], [(0, 1, 2, 3)])
            face.mesh([tuple(Vector(p) + Vector((0, .04, 0))) for p in (p10, p11, p01, p00)], [(0, 1, 2, 3)])
    fr.limb((0, 0, .5), (0, .3, .9), .14, .14, bevel=0)
    # The feed on its boom ahead of the dish, the IFF bar on top.
    a.part('Radar_feed', 'Steel', r).limb((0, .3, .62), (0, -1.0, .95), .07, .07, bevel=0)
    k.block(a.part('Radar_feed', 'Steel', r), (.32, .22, .22), loc=(0, -1.05, .85), chamfer=.02)
    a.part('Radar_iff', 'Armor', r).box((3.2, .1, .14), loc=(0, .95, 2.2), bevel=.01)
    for u in (-1, 1):
        a.part('Radar_iff', 'Armor', r).limb((u * 1.2, .95, 2.15), (u * 1.0, .85, 2.0), .04, .04, bevel=0)
    return r


def lev_abl(a, parent, cells, z):
    """The Mk 143 armoured box launchers (Part_vls): each a long armoured box on its elevating cradle (the hinge at
    the rear, the ram ahead), the four cell doors on its front end, the stiffening ribs and the hazard bands; the
    outer two raised to the firing angle. cells: [(x, y, raised)] in the part's frame."""
    for i, (x, y, raised) in enumerate(cells):
        el = .5 if raised else 0.0
        cr = a.part('Abl_cradle', 'Steel', parent)
        k.block(cr, (1.15, 3.6, .16), loc=(x, y, z + .08), chamfer=.02)
        for e in (-1, 1):
            cr.box((.14, .4, .85), loc=(x + e * .56, y + 1.55, z + .55), bevel=.01)
        hinge = Vector((x, y + 1.55, z + .95))
        d = Vector((0, -math.cos(el), math.sin(el)))
        up = Vector((0, math.sin(el), math.cos(el)))
        c = hinge + d * 1.75 + up * .05
        box = a.part('Abl_box', 'Team', parent)
        k.block(box, (1.0, 3.5, .78), loc=tuple(c - up * .39), rot=(-el, 0, 0), chamfer=.06, ends=(True, True))
        for t in (-1.1, -.3, .5, 1.3):
            p = c + d * -t
            a.part('Abl_ribs', 'Armor', parent).box((1.04, .08, .82), loc=tuple(p - up * .39), rot=(-el, 0, 0), bevel=0)
        front = c + d * 1.77
        for ex in (-.25, .25):
            for ez in (-.2, .2):
                a.part('Abl_doors', 'Undercarriage', parent).box((.42, .03, .32),
                                                                loc=tuple(front - up * .39 + Vector((ex, 0, 0)) + up * ez),
                                                                rot=(-el, 0, 0), bevel=0)
        a.part('Abl_bands', 'Hazard', parent).box((1.02, .14, .8), loc=tuple(c + d * 1.45 - up * .39), rot=(-el, 0, 0),
                                                  bevel=0)
        a.part('Kit_hinges', 'Steel', parent).cyl(.1, .9, loc=tuple(hinge), rot=(0, R90, 0), seg=8, bevel=0)
        if raised:
            ram0 = Vector((x + .3, y - .3, z + .15))
            ram1 = c + d * .2 - up * .7 + Vector((.3, 0, 0))
            a.part('Abl_rams', 'Steel', parent).limb(tuple(ram0), tuple(ram1), .12, .12, bevel=0)


# ============================================================================= Scylla
def sc_ak130(a, ploc, mz):
    """The AK-130 twin 130 mm (Slava) under Part_gun: the low barbette, the gunhouse on Mount_gun (its narrow
    raked front, the inward-sloped faceted sides, the flat roof and the raised rear hump with the sight and the
    small radome), the single wide mantlet slot, two barrels close together with their fume extractors
    (Gun_barrels / Gun_muzzles, the kick parts), the side doors and the hand rails; Muzzle_gun between the tips with
    the per-barrel muzzles."""
    p = a.pivot('Part_gun', ploc)
    lz = mz - ploc[2]
    k.lathe(a.part('Gun_barbette', 'Armor', p), [(1.55, -.05), (1.55, lz - .05), (1.48, lz)], seg=24)
    m = a.pivot('Mount_gun', (0, 0, lz), p)
    k.ring(a.part('Gun_ring', 'Steel', m), [(1.4, -.02), (1.48, -.02), (1.48, .07), (1.4, .07)], seg=24)
    rings = [
        (0.0, [(-.55, -2.3), (.55, -2.3), (1.25, -1.35), (1.62, -.4), (1.62, 2.55), (-1.62, 2.55), (-1.62, -.4),
               (-1.25, -1.35)]),
        (1.0, [(-.48, -2.0), (.48, -2.0), (1.12, -1.2), (1.45, -.35), (1.45, 2.5), (-1.45, 2.5), (-1.45, -.35),
               (-1.12, -1.2)]),
        (1.62, [(-.35, -1.55), (.35, -1.55), (.85, -1.0), (1.18, -.3), (1.18, 2.42), (-1.18, 2.42), (-1.18, -.3),
                (-.85, -1.0)])]
    house = a.part('Gun_house', 'Team', m)
    k.sharp_loft(house, [[(x, y, z) for x, y in pts] for z, pts in rings], chamfer=.05)
    k.inset(house, lambda c, n, f: abs(n.z) < .5 and c.z > .2, width=.08, depth=-.015)
    # The rear hump (sight, ventilation, the radome), the roof hatch, the side doors.
    k.sharp_loft(a.part('Gun_hump', 'Team', m), [
        [(-.95, .5, 1.6), (.95, .5, 1.6), (.95, 2.35, 1.6), (-.95, 2.35, 1.6)],
        [(-.8, .85, 2.02), (.8, .85, 2.02), (.8, 2.25, 2.02), (-.8, 2.25, 2.02)]], chamfer=.04)
    k.lathe(a.part('Gun_radome', 'PlasterWhite', m), [(.22, 0), (.24, .12), (.16, .3), (0, .34)], loc=(-.45, 1.9, 2.02),
            seg=12)
    hood(a, a.part('Gun_sight', 'Armor', m), None, (.4, 1.05, 2.02), .36, .42, .24, parent=m)
    k.block(a.part('Gun_hatch', 'Steel', m), (.55, .5, .06), loc=(0, -.35, 1.64), chamfer=.02)
    for s in (-1, 1):
        K.door(a, (s * 1.56, 1.2, .2), size=(.55, 1.0), normal=(s, 0, .12), parent=m, mat='Armor', frame_mat='Steel')
        a.part('Kit_handles', 'Steel', m).box((.04, 1.2, .04), loc=(s * 1.3, .4, 1.5), bevel=0)
    # The mantlet: one wide slot in the raked front with its rubber boot.
    zg, gap = .82, .62
    xs = (-gap / 2, gap / 2)
    k.block(a.part('Gun_mantlet', 'Armor', m), (1.15, .3, .55), loc=(0, -2.05, zg), chamfer=.04,
            ends=(True, True))
    a.part('Gun_boots', 'Rubber', m).box((1.0, .1, .4), loc=(0, -2.24, zg), bevel=.03)
    L = 4.7
    y0 = -2.2
    for x in xs:
        fwd(a.part('Gun_barrels', 'Steel', m), [(.11, -.1), (.11, .25), (.085, .35), (.08, 1.4), (.12, 1.5),
                                                 (.12, 2.2), (.078, 2.3), (.07, L - .15), (.08, L - .1), (.08, L)],
            (x, y0, zg), seg=12)
        fwd(a.part('Gun_muzzles', 'Undercarriage', m), [(.045, L - .01), (.079, L - .01), (.079, L + .01),
                                                         (.045, L + .01)], (x, y0, zg), seg=10)
    mzp = a.pivot('Muzzle_gun', (0, y0 - L - .08, zg), m)
    per_barrel(a, mzp, 'gun', xs)
    a.part('Team_band', 'Team', m).box((1.9, .35, .03), loc=(0, .4, 1.635), bevel=0)
    return m


def sc_ak100(a, ploc):
    """The AK-100 single 100 mm on the bridge roof (Part_mg > Mount_mg: the 127 mm of the def): the base ring, the
    gunhouse with its rounded front and sloped sides, the roof sight cupola and the aerial, the barrel with its fume
    extractor (Dp_barrels / Dp_muzzles, the kick parts); Muzzle_mg at the mouth."""
    p = a.pivot('Part_mg', ploc)
    m = a.pivot('Mount_mg', (0, 0, .02), p)
    k.lathe(a.part('Dp_ring', 'Steel', m), [(.78, -.02), (.78, .07), (.72, .1)], seg=18)
    nose = [(math.sin(u) * .72, -.45 - math.cos(u) * .45) for u in (-1.3, -.85, -.4, 0, .4, .85, 1.3)]
    base = nose[3:] + [(.74, .95), (-.74, .95)] + nose[:3]

    def ring_at(z, f):
        return [(x * f, y * f + (1 - f) * .3, z) for x, y in base]
    k.sharp_loft(a.part('Dp_house', 'Team', m), [ring_at(.06, 1.0), ring_at(.6, .95), ring_at(1.0, .72)], chamfer=.03)
    k.lathe(a.part('Dp_cupola', 'Armor', m), [(.18, 0), (.18, .14), (.12, .2), (0, .22)], loc=(.3, .35, 1.0), seg=10)
    a.part('Glass', 'Glass', m).box((.14, .02, .05), loc=(.3, .17, 1.08), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', m), (-.35, .65, 1.0), h=.55, r=.014, lean=.15)
    a.part('Dp_port', 'Undercarriage', m).box((.22, .08, .3), loc=(0, -.9, .45), bevel=.02)
    L = 3.2
    fwd(a.part('Dp_barrels', 'Steel', m), [(.08, -.1), (.08, .2), (.058, .28), (.055, 1.1), (.085, 1.18), (.085, 1.62),
                                            (.055, 1.7), (.05, L - .08), (.058, L - .05), (.058, L)],
        (0, -.92, .45), seg=10)
    fwd(a.part('Dp_muzzles', 'Undercarriage', m), [(.03, L - .01), (.057, L - .01), (.057, L + .01), (.03, L + .01)],
        (0, -.92, .45), seg=8)
    a.pivot('Muzzle_mg', (0, -.92 - L - .05, .45), m)
    return m


def sc_ak630(a, loc, s=.5):
    """An AK-630 gatling (decoration: the APS's guns): the base ring, the rounded turret drum with its flattened
    top, the single barrel jacket out of its front slot with the six barrels' muzzle cap."""
    x, y, z = loc
    k.lathe(a.part('Ciws_base', 'Armor'), [(.62 * s, 0), (.62 * s, .12 * s), (.55 * s, .16 * s)], loc=loc, seg=16)
    k.lathe(a.part('Ciws_body', 'Team'), [(.55 * s, .16 * s), (.6 * s, .45 * s), (.56 * s, .7 * s), (.42 * s, .88 * s),
                                          (0, .92 * s)], loc=loc, seg=16)
    a.part('Ciws_slot', 'Undercarriage').box((.32 * s, .1 * s, .36 * s), loc=(x, y - .55 * s, z + .5 * s), bevel=0)
    fwd(a.part('Ciws_gun', 'Steel'), [(.12 * s, 0), (.12 * s, 1.0 * s), (.14 * s, 1.05 * s), (.14 * s, 1.25 * s),
                                      (.1 * s, 1.28 * s)], (x, y - .5 * s, z + .5 * s), seg=10)
    for i in range(6):
        u = i * TAU / 6
        a.part('Ciws_bores', 'Undercarriage').cyl(.02 * s, .03, loc=(x + math.cos(u) * .07 * s, y - 1.79 * s,
                                                                      z + .5 * s + math.sin(u) * .07 * s),
                                                  rot=K.FORWARD, seg=5, bevel=0)


def sc_radar(a, loc):
    """The Top Pair-style search radar on the pyramid mast (`Radar` spins): the drive, two back-to-back open mesh
    reflectors (the larger forward), their frames, struts and feeds."""
    r = a.pivot('Radar', loc)
    k.lathe(a.part('Radar_drive', 'Steel', r), [(.18, 0), (.18, .25), (.12, .3), (.12, .45)], seg=10)
    for side, W, Hh, z0 in ((-1, 2.6, .8, .45), (1, 1.8, .55, .55)):
        fr = a.part('Radar_frame', 'Armor', r)
        rows = []
        for j in range(3):
            z = z0 + j * Hh / 2
            pts = [(u * W / 2, side * (.12 + .32 * u * u), z) for u in (i / 3 - 1 for i in range(7))]
            rows.append(pts)
            fr.tube(pts, .02, seg=4)
        for i in range(7):
            fr.tube([rows[j][i] for j in range(3)], .018, seg=4)
        face = a.part('Radar_mesh', 'Undercarriage', r)
        for j in range(2):
            for i in range(6):
                q = [rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]]
                face.mesh([(p[0], p[1] - side * .01, p[2]) for p in q], [(0, 1, 2, 3)])
                face.mesh([(p[0], p[1] + side * .015, p[2]) for p in reversed(q)], [(0, 1, 2, 3)])
        a.part('Radar_feed', 'Steel', r).limb((0, side * .1, z0 + Hh / 2), (0, side * .75, z0 + Hh / 2), .05, .05,
                                              bevel=0)
    a.part('Radar_frame', 'Armor', r).box((.12, .5, .5), loc=(0, 0, .55), bevel=.01)
    return r


# ============================================================================= Nyx
def nx_ags(a):
    """The AGS-style 155 mm stealth turret (Part_gun > Mount_gun; the railgun's mount): the flush deck ring, the low
    faceted gunhouse rising to a ridge, the tall raked gun-port housing the barrel leaves through, the faceted
    barrel sleeve, the long 155 mm barrel with its double-baffle brake (Gun_barrels / Gun_muzzles, the kick parts),
    the flush roof hatches and the panel seams; Muzzle_gun at the brake."""
    p = a.pivot('Part_gun', (0, -13.2, 3.0))
    m = a.pivot('Mount_gun', (0, 0, .2), 'Part_gun')
    k.lathe(a.part('Gun_ring', 'Steel', 'Part_gun'), [(1.95, -.02), (1.95, .12), (1.86, .2)], seg=24)
    del p
    rings = [
        (0.0, [(-.95, -2.75), (.95, -2.75), (1.85, -1.35), (1.95, 2.25), (1.45, 2.75), (-1.45, 2.75), (-1.95, 2.25),
               (-1.85, -1.35)]),
        (.8, [(-.78, -2.3), (.78, -2.3), (1.58, -1.1), (1.68, 2.08), (1.25, 2.5), (-1.25, 2.5), (-1.68, 2.08),
              (-1.58, -1.1)]),
        (1.32, [(-.38, -1.55), (.38, -1.55), (.98, -.72), (1.08, 1.78), (.78, 2.12), (-.78, 2.12), (-1.08, 1.78),
                (-.98, -.72)])]
    house = a.part('Gun_house', 'Team', m)
    k.sharp_loft(house, [[(x, y, z) for x, y in pts] for z, pts in rings], chamfer=.04)
    k.inset(house, lambda c, n, f: n.z < .9 and c.z > .15, width=.07, depth=-.012)
    k.extrude(a.part('Gun_roof', 'Armor', m), [(x * .9, y * .9 + .05) for x, y in rings[2][1]], .04,
              loc=(0, 0, 1.34), axis='Z', chamfer=.01)
    # The gun-port housing: a raked faceted box on the front, the slot the barrel elevates in.
    gp = a.part('Gun_port', 'Team', m)
    k.sharp_loft(gp, [[(-.5, -2.85, .15), (.5, -2.85, .15), (.58, -1.2, .15), (-.58, -1.2, .15)],
                      [(-.42, -2.45, 1.32), (.42, -2.45, 1.32), (.48, -1.0, 1.52), (-.48, -1.0, 1.52)]], chamfer=.03)
    a.part('Gun_slot', 'Undercarriage', m).box((.34, .06, .9), loc=(0, -2.66, .82), rot=(-.33, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Gun_seams', 'Armor', m).box((.03, 1.6, .04), loc=(s * .52, -1.9, 1.0), rot=(-.25, 0, 0), bevel=0)
    for y in (-.3, 1.2):
        k.block(a.part('Gun_hatches', 'Armor', m), (.6, .7, .03), loc=(.45 if y < 0 else -.4, y, 1.37), chamfer=.01)
    zg = .82
    y0 = -2.55
    sleeve = a.part('Gun_sleeve', 'Team', m)
    k.extrude(sleeve, [(-.17, -.1), (-.08, -.19), (.08, -.19), (.17, -.1), (.17, .1), (.08, .19), (-.08, .19),
                       (-.17, .1)], 1.3, loc=(0, y0 - .55, zg), rot=(R90, 0, 0), axis='Z', chamfer=.02, taper=.85)
    L = 6.6
    fwd(a.part('Gun_barrels', 'Steel', m), [(.13, -.2), (.13, 1.3), (.115, 1.4), (.1, 3.5), (.085, L - .55),
                                             (.1, L - .5)], (0, y0, zg), seg=12)
    fwd(a.part('Gun_muzzles', 'Armor', m), [(.06, L - .5), (.16, L - .48), (.16, L - .3), (.11, L - .26),
                                             (.11, L - .2), (.16, L - .17), (.16, L), (.06, L)], (0, y0, zg), seg=12)
    for e in (-1, 1):
        a.part('Gun_muzzles', 'Armor', m).box((.05, .2, .1), loc=(e * .165, y0 - L + .38, zg), bevel=0)
    a.pivot('Muzzle_gun', (0, y0 - L - .05, zg), m)
    K.soot(a, (0, -13.2 + y0 - L, 3.0 + .2 + zg), radius=.6, k=.3)
    K.tone(a, 'Part_gun', k=.92)
    return m


def nx_cupola(a, pname, mount, muzzle, loc, tag):
    """A Mk 110-style stealth cupola (the 127 mm mounts on the deckhouse roof): the flush ring, the faceted pyramid
    shroud with its front slot, the barrel in its faceted sleeve and the stealth cap (Cupola_barrels* /
    Cupola_muzzles*, the kick parts), the flush hatch and the panel seams; Muzzle_* at the cap."""
    p = a.pivot(pname, loc)
    m = a.pivot(mount, (0, 0, .03), p)
    k.lathe(a.part('Cupola_ring' + tag, 'Steel', m), [(1.0, -.02), (1.0, .06), (.95, .08)], seg=20)
    rings = [
        (.04, [(-.42, -1.05), (.42, -1.05), (.95, -.5), (1.0, .65), (.62, 1.0), (-.62, 1.0), (-1.0, .65),
               (-.95, -.5)]),
        (.55, [(-.34, -.9), (.34, -.9), (.8, -.42), (.85, .55), (.52, .86), (-.52, .86), (-.85, .55), (-.8, -.42)]),
        (.98, [(-.16, -.42), (.16, -.42), (.42, -.18), (.45, .4), (.3, .58), (-.3, .58), (-.45, .4), (-.42, -.18)])]
    sh = a.part('Cupola_house' + tag, 'Team', m)
    k.sharp_loft(sh, [[(x, y, z) for x, y in pts] for z, pts in rings], chamfer=.03)
    k.inset(sh, lambda c, n, f: n.z < .95 and c.z > .1, width=.05, depth=-.01)
    a.part('Cupola_slot' + tag, 'Undercarriage', m).box((.2, .05, .5), loc=(0, -.97, .42), rot=(-.25, 0, 0), bevel=0)
    k.block(a.part('Cupola_hatch' + tag, 'Armor', m), (.36, .3, .03), loc=(0, .15, .99), chamfer=.01)
    zg = .42
    y0 = -.95
    k.extrude(a.part('Cupola_sleeve' + tag, 'Team', m), [(-.1, -.06), (-.05, -.11), (.05, -.11), (.1, -.06), (.1, .06),
                                                         (.05, .11), (-.05, .11), (-.1, .06)], .75,
              loc=(0, y0 - .3, zg), rot=(R90, 0, 0), axis='Z', chamfer=.015, taper=.8)
    L = 3.1
    fwd(a.part('Cupola_barrels' + tag, 'Steel', m), [(.07, -.1), (.07, .7), (.055, .78), (.048, L - .35),
                                                      (.06, L - .3)], (0, y0, zg), seg=10)
    k.extrude(a.part('Cupola_muzzles' + tag, 'Team', m), [(-.08, -.05), (-.04, -.09), (.04, -.09), (.08, -.05),
                                                          (.08, .05), (.04, .09), (-.04, .09), (-.08, .05)], .32,
              loc=(0, y0 - L + .14, zg), rot=(R90, 0, 0), axis='Z', chamfer=.01, taper=.8)
    a.pivot(muzzle, (0, y0 - L - .05, zg), m)
    K.tone(a, pname, k=.9)
    return m


def nx_pvls_module(a, parent, x, y, out, cells=2, rows=2, cell=.55, z=0.0):
    """A peripheral VLS module set into the deck edge: the armoured coaming, the cell hatches (each with its hinge
    and the raised armour lip), the gas uptake slot on the outboard edge with its louvres."""
    W, D = cells * cell + .16, rows * cell + .16
    k.block(a.part('Pvls_coaming', 'Armor', parent), (W, D, .14), loc=(x, y, z + .07), chamfer=.03)
    lids = a.part('Pvls_hatches', 'Steel', parent)
    for i in range(cells):
        for j in range(rows):
            cx = x + (i - (cells - 1) / 2) * cell
            cy = y + (j - (rows - 1) / 2) * cell
            k.block(lids, (cell - .07, cell - .07, .05), loc=(cx, cy, z + .165), chamfer=.015)
            a.part('Pvls_hinges', 'Undercarriage', parent).box((cell - .15, .05, .04),
                                                              loc=(cx, cy + cell / 2 - .06, z + .2), bevel=0)
    k.block(a.part('Pvls_uptake', 'Undercarriage', parent), (.18, D - .1, .06), loc=(x + out * (W / 2 - .02), y,
                                                                                     z + .13), chamfer=0)
    for j in range(int(D / .2)):
        a.part('Pvls_louvres', 'Steel', parent).box((.2, .03, .03), loc=(x + out * (W / 2 - .02), y - D / 2 + .15 + j * .2,
                                                                       z + .17), bevel=0)


def nx_drone(a, loc, yaw=0.0, s=1.0):
    """A Fire Scout-style deck drone (an unmanned light helicopter, no cockpit glass): the smooth fuselage with the
    sensor turret under the nose, the four-blade rotor, the tail boom with its fin and tailplane, the skids and the
    tie-down straps."""
    x, y, z = loc
    c, sn = math.cos(yaw), math.sin(yaw)

    def at(px, py, pz):
        return (x + (px * c - py * sn) * s, y + (px * sn + py * c) * s, z + pz * s)
    body = a.part('Drone_body', 'PlasterWhite')
    rings = []
    for py, w, h0, h1 in ((-2.1, .2, .55, .85), (-1.8, .5, .35, 1.15), (-1.0, .62, .3, 1.35), (.6, .62, .3, 1.3),
                          (1.3, .4, .5, 1.15), (1.6, .2, .78, 1.0)):
        rings.append([at(-w, py, h0), at(w, py, h0), at(w * .85, py, h1), at(-w * .85, py, h1)])
    body.loft(rings, bevel=0)
    a.part('Drone_boom', 'PlasterWhite').limb(at(0, 1.4, .9), at(0, 4.6, 1.05), .18 * s, .2 * s, bevel=0)
    a.part('Drone_fin', 'Team').limb(at(0, 4.3, .9), at(0, 4.7, 1.8), .05 * s, .45 * s, bevel=0)
    a.part('Drone_fin', 'Team').box((1.3 * s, .3 * s, .04 * s), loc=at(0, 4.1, 1.05), rot=(0, 0, yaw), bevel=0)
    k.lathe(a.part('Drone_eo', 'Glass'), [(.0, 0), (.18 * s, .02 * s), (.2 * s, .15 * s), (0, .3 * s)],
            loc=at(0, -1.7, .05), seg=10)
    a.part('Drone_mast', 'Steel').cyl(.08 * s, .35 * s, loc=at(0, -.4, 1.5), seg=8, bevel=0)
    hub = at(0, -.4, 1.72)
    a.part('Drone_hub', 'Steel').cyl(.16 * s, .12 * s, loc=hub, seg=8, bevel=0)
    for b in range(4):
        u = yaw + .4 + b * R90
        mid = (hub[0] + math.cos(u) * 1.75 * s, hub[1] + math.sin(u) * 1.75 * s, hub[2] - .04 * s)
        a.part('Drone_blades', 'Undercarriage').box((3.3 * s, .2 * s, .035 * s), loc=mid, rot=(0, -.02, u), bevel=0)
    sk = a.part('Drone_skids', 'Steel')
    for e in (-1, 1):
        sk.tube([at(e * .55, -1.4, .05), at(e * .55, .8, .05)], .04 * s, seg=5)
        for py in (-.9, .4):
            sk.tube([at(e * .55, py, .05), at(e * .4, py, .4)], .035 * s, seg=4)
        a.part('Tie_downs', 'Hazard').tube([at(e * .55, -1.2, .08), at(e * 1.1, -1.5, -.02)], .015, seg=3)
        a.part('Tie_downs', 'Hazard').tube([at(e * .55, .6, .08), at(e * 1.1, .9, -.02)], .015, seg=3)
    a.part('Drone_band', 'Team').box((1.1 * s, .25 * s, .08 * s), loc=at(0, -.2, 1.2), rot=(0, 0, yaw), bevel=0)
