"""Play-test 14 wave R4 (lane models): Hydra's and Nyx's guns redrawn.

Owner (04/10, Docs/prompts/playtest14_vi.txt, block "Bổ sung 04/10 sau khi thử lane H"): "tháp pháo trên hydra, làm
lại, theo tiêu chuẩn typhon"; "nyx cũng vậy vẽ lại tháp pháo theo chuẩn leviathan". Hydra's twin 57 mm and its 100 mm
were W.poly_turret boxes with kit barrels (K.gun_barrel); Nyx's AGS and cupolas (R1) were plain facets. Each function
here draws for one ship only, from geometry primitives, at that ship's scale, read from a real design, at the detail
of Typhon's R2 guns (Hydra) and Leviathan's R1 turrets (Nyx). DECISIONS "Play-test 14 wave R4 (lane models)".

- Hydra (hydra_sub): `hy_twin57` (Mount_gun / .001: a faceted low-signature twin 57 mm on its retractable casing
  mount, a Bofors 57 Mk 3 read doubled: the faceted house with its visor plate, two barrels in thermal sleeves with
  pepperpot brakes, the EO sight, the hoist bulge and vents; Gun_barrels* / Gun_muzzles*, per-barrel muzzles) and
  `hy_a190` (Mount_gun.002, the deck_gun part: an A-190 read 100 mm, the chined stealth house, the barrel with its
  fume extractor and double-baffle brake, the radar-optical sight, the ribbed pedestal; Dg_barrels / Dg_muzzles).
- Nyx: `nx_gun` (Part_gun > Mount_gun: the AGS-read 155 mm rebuilt at Leviathan's detail: skirt and chines, flush
  fastener rows, roof plate seams, the sight hood and EO ball, flush hatches with handles, roof vents, the raked
  gun-port housing and its boot, the thermal-shrouded barrel with the fume extractor and the multi-baffle brake, the
  magazine bustle with its loading door, the ladder, the team band; Gun_barrels / Gun_muzzles) and `nx_cupola`
  (Part_mg[.001] > Mount_mg[.001]: the Mk 110-read 57 mm stealth cupola at the same detail; Cupola_barrels* /
  Cupola_muzzles*).

Every runtime name and position is the one the mount had. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


def fwd(part, profile, loc, seg=14):
    """A turned part along -Y (the front): profile [(radius, distance forward)] from loc."""
    k.lathe(part, profile, loc=loc, rot=K.FORWARD, seg=seg)


def per_barrel(a, muzzle, tag, xs):
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def pepperpot(a, part, holes, x, y, z, r, L, rows=3, per=6, seg=12):
    """A pepperpot brake along -Y from y: the drum and rows of dark vent holes round it."""
    fwd(part, [(r * .7, 0), (r, .02), (r, L - .02), (r * .75, L)], (x, y, z), seg=seg)
    for i in range(rows):
        yy = y - L * (i + .6) / (rows + .2)
        for j in range(per):
            u = j * TAU / per + (i % 2) * TAU / per / 2
            holes.box((.022, r * .32, r * .32), loc=(x + math.cos(u) * (r + .004), yy, z + math.sin(u) * (r + .004)),
                      rot=(0, -u, 0), bevel=0)


# ============================================================================= Hydra
def hy_twin57(a, index, loc, tag, muzzle_tag):
    """A twin 57 mm on Hydra's casing (Mount_gun[.001]): the flush coaming with its hazard lip and bolt ring, the
    faceted low house (a raked visor plate with two embrasures and their rubber boots, chined cheeks, a stepped
    roof), the EO sight in its faceted box, the roof hatch with hinges and handle, lifting eyes, the hoist bulge and
    louvred vents at the back, the case-ejection port; two barrels in thermal sleeves (three clamp bands) with
    pepperpot brakes (Gun_barrels* / Gun_muzzles*, the kick parts); Muzzle_gun[.001] between the brakes and the
    per-barrel muzzles."""
    x, y, z = loc
    k.ring(a.part('Gun_well' + tag, 'Undercarriage'), [(.98, -.02), (1.08, -.02), (1.08, .04), (.98, .05)],
           loc=(x, y, z), seg=24)
    k.ring(a.part('Gun_well' + tag, 'Hazard'), [(1.0, .051), (1.06, .051), (1.06, .062), (1.0, .062)], loc=(x, y, z),
           seg=24)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .05), (0, 0, 1), 1.03, 16, r=.018, h=.02)
    m = a.pivot(K.name('Mount_gun', index), (x, y, z + .04))
    k.ring(a.part('Gun_ring' + tag, 'Steel', m), [(.84, -.02), (.92, -.02), (.92, .06), (.84, .08)], seg=22)
    house = a.part('Gun_house' + tag, 'Team', m)
    k.sharp_loft(house, [
        [(-.42, -1.02, .02), (.42, -1.02, .02), (.86, -.5, .02), (.9, .78, .02), (.62, .98, .02), (-.62, .98, .02),
         (-.9, .78, .02), (-.86, -.5, .02)],
        [(-.36, -.92, .38), (.36, -.92, .38), (.8, -.44, .42), (.84, .74, .44), (.58, .93, .44), (-.58, .93, .44),
         (-.84, .74, .44), (-.8, -.44, .42)],
        [(-.24, -.6, .66), (.24, -.6, .66), (.58, -.3, .7), (.62, .64, .7), (.42, .8, .7), (-.42, .8, .7),
         (-.62, .64, .7), (-.58, -.3, .7)]], chamfer=.025)
    k.inset(house, lambda c, n, f: c.z > .08, width=.035, depth=-.008)
    # The visor plate over the embrasures, the two embrasures with boots.
    k.block(a.part('Gun_face' + tag, 'Armor', m), (.9, .08, .44), loc=(0, -1.0, .27), rot=(-.32, 0, 0), chamfer=.015)
    zg, gap = .26, .2
    xs = (-gap, gap)
    for bx in xs:
        a.part('Gun_ports' + tag, 'Charred', m).box((.14, .06, .22), loc=(bx, -1.05, zg + .02), rot=(-.32, 0, 0),
                                                    bevel=0)
        fwd(a.part('Gun_boots' + tag, 'Rubber', m), [(.1, 0), (.11, .05), (.085, .1), (.095, .15), (.07, .2)],
            (bx, -1.04, zg), seg=10)
        fwd(a.part('Gun_barrels' + tag, 'Steel', m), [(.068, 0), (.068, .95), (.05, 1.0), (.042, 1.05), (.042, 2.02),
                                                      (0, 2.02)], (bx, -1.2, zg), seg=10)
        for j in range(3):
            fwd(a.part('Bands_barrels' + tag, 'Undercarriage', m), [(.075, 0), (.075, .05)], (bx, -1.3 - j * .3, zg),
                seg=10)
        pepperpot(a, a.part('Gun_muzzles' + tag, 'Steel', m), a.part('Holes_muzzles' + tag, 'Charred', m),
                  bx, -3.18, zg, .062, .3, rows=2, per=6, seg=10)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, -3.52, zg), m)
    per_barrel(a, mz, muzzle_tag, xs)
    # Roof: the EO sight box, the hatch with hinges and handle, lifting eyes.
    k.sharp_loft(a.part('Gun_sight' + tag, 'Armor', m), [
        [(.2, -.42, .68), (.48, -.42, .68), (.5, -.1, .68), (.2, -.1, .68)],
        [(.24, -.36, .86), (.44, -.36, .86), (.46, -.12, .86), (.24, -.12, .86)]], chamfer=.012)
    a.part('Glass', 'Glass', m).box((.16, .02, .08), loc=(.34, -.4, .78), rot=(-.3, 0, 0), bevel=0)
    k.block(a.part('Gun_hatch' + tag, 'Armor', m), (.36, .36, .04), loc=(-.22, .3, .72), chamfer=.01)
    K.hinge(a.part('Kit_hinges', 'Steel', m), (-.36, .49, .74), (-.08, .49, .74), r=.016, knuckles=2)
    K.handle(a.part('Kit_handles', 'Steel', m), (-.3, .14, .745), (-.14, .14, .745), Vector((0, 0, 1)), h=.035, r=.008)
    for ex, ey in ((.5, .6), (-.5, .6), (0, -.48)):
        a.part('Gun_eyes' + tag, 'Steel', m).box((.03, .08, .07), loc=(ex, ey, .72), bevel=0)
    # Back: the hoist bulge, the louvred vents, the case-ejection port on the right cheek.
    k.block(a.part('Gun_hoist' + tag, 'Armor', m), (.7, .2, .4), loc=(0, 1.02, .24), chamfer=.03, ends=(True, True))
    for j in range(4):
        a.part('Gun_vents' + tag, 'Undercarriage', m).box((.36, .02, .03), loc=(0, 1.13, .12 + j * .08), bevel=0)
    a.part('Gun_ports' + tag, 'Charred', m).box((.02, .22, .1), loc=(-.86, -.1, .2), rot=(0, .05, 0), bevel=0)
    K.soot(a, (x, y - 3.4, z + .04 + zg), radius=.35, k=.3)
    K.tone(a, K.name('Mount_gun', index), k=.94)


def hy_a190(a, loc):
    """The 100 mm forward of the sail (Mount_gun.002, the deck_gun part) on its ribbed pedestal: an A-190 read, the
    chined stealth house (a long raked face, the slot cover, flush seams), the barrel with its fume extractor and the
    double-baffle brake with side ports (Dg_barrels / Dg_muzzles, the kick parts), the radar-optical sight dome on
    its post, the roof hatch, lifting eyes, a whip, the rear ammunition door and vents; Muzzle_gun.002 at the brake's
    mouth."""
    x, y, z = loc
    ped = a.part('Deck_gun_pedestal', 'Armor')
    k.lathe(ped, [(1.18, -.1), (1.18, .12), (1.1, .3), (1.06, .42), (1.0, .45)], loc=(x, y, z), seg=24)
    for i in range(10):
        u = i * TAU / 10
        ped.box((.07, .2, .3), loc=(x + math.cos(u) * 1.14, y + math.sin(u) * 1.14, z + .2), rot=(0, 0, u), bevel=0)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .45), (0, 0, 1), .96, 16, r=.018, h=.02)
    m = a.pivot('Mount_gun__002', (x, y, z + .45))
    k.ring(a.part('Dg_ring', 'Steel', m), [(.86, -.02), (.95, -.02), (.95, .06), (.86, .08)], seg=24)
    house = a.part('Dg_house', 'Team', m)
    k.sharp_loft(house, [
        [(-.48, -1.4, .02), (.48, -1.4, .02), (1.02, -.55, .02), (1.06, 1.05, .02), (.8, 1.25, .02), (-.8, 1.25, .02),
         (-1.06, 1.05, .02), (-1.02, -.55, .02)],
        [(-.36, -1.15, .5), (.36, -1.15, .5), (.92, -.45, .56), (.96, 1.0, .58), (.72, 1.18, .58), (-.72, 1.18, .58),
         (-.96, 1.0, .58), (-.92, -.45, .56)],
        [(-.2, -.7, .92), (.2, -.7, .92), (.62, -.28, .96), (.66, .86, .96), (.46, 1.02, .96), (-.46, 1.02, .96),
         (-.66, .86, .96), (-.62, -.28, .96)]], chamfer=.03)
    k.inset(house, lambda c, n, f: c.z > .1, width=.04, depth=-.01)
    zg = .46
    k.block(a.part('Dg_slot', 'Armor', m), (.3, .1, .52), loc=(0, -1.3, zg + .06), rot=(-.4, 0, 0), chamfer=.015)
    fwd(a.part('Dg_boot', 'Rubber', m), [(.13, 0), (.14, .06), (.11, .12), (.12, .18), (.09, .24)], (0, -1.32, zg),
        seg=12)
    L = 3.45
    y0 = -1.5
    fwd(a.part('Dg_barrels', 'Steel', m), [(.1, -.1), (.1, .45), (.082, .55), (.078, 1.35), (.11, 1.45), (.115, 1.9),
                                           (.08, 2.0), (.07, L - .05), (0, L - .05)], (0, y0, zg), seg=12)
    br = a.part('Dg_muzzles', 'Armor', m)
    fwd(br, [(.07, 0), (.13, .02), (.13, .14), (.1, .16), (.1, .24), (.13, .26), (.13, .4), (.09, .42), (0, .42)],
        (0, y0 - L + .05, zg), seg=12)
    for s in (-1, 1):
        for dy in (-.08, -.32):
            a.part('Ports_muzzles', 'Charred', m).box((.03, .07, .15), loc=(s * .13, y0 - L + .05 + dy, zg), bevel=0)
    a.pivot('Muzzle_gun__002', (0, y0 - L - .4, zg), m)
    K.soot(a, (x, y + y0 - L, z + .45 + zg), radius=.45, k=.3)
    # Roof: the radar-optical sight dome on its post, the hatch, lifting eyes, a whip.
    a.part('Dg_post', 'Armor', m).cyl(.1, .22, loc=(.35, .1, 1.06), seg=10, bevel=0)
    k.lathe(a.part('Dg_sight', 'PlasterWhite', m), [(.2, 0), (.21, .08), (.15, .2), (0, .24)], loc=(.35, .1, 1.17),
            seg=14)
    a.part('Glass', 'Glass', m).box((.14, .02, .06), loc=(.35, -.1, 1.24), bevel=0)
    k.block(a.part('Dg_hatch', 'Armor', m), (.42, .4, .04), loc=(-.3, .55, .98), chamfer=.01)
    K.hinge(a.part('Kit_hinges', 'Steel', m), (-.48, .76, 1.0), (-.12, .76, 1.0), r=.016, knuckles=2)
    for ex, ey in ((.58, .85), (-.58, .85), (0, -.6)):
        a.part('Dg_eyes', 'Steel', m).box((.03, .09, .08), loc=(ex, ey, .98), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', m), (-.55, .95, .96), h=.8, r=.02)
    # Back: the ammunition door with its frame, louvred vents either side.
    k.block(a.part('Dg_door', 'Armor', m), (.5, .05, .5), loc=(0, 1.24, .32), rot=(.05, 0, 0), chamfer=.01)
    for s in (-1, 1):
        for j in range(3):
            a.part('Dg_vents', 'Undercarriage', m).box((.26, .02, .03), loc=(s * .55, 1.17, .22 + j * .09),
                                                       rot=(0, 0, s * .45), bevel=0)
    K.tone(a, 'Mount_gun__002', k=.94)


# ============================================================================= Nyx
def nx_gun(a):
    """The AGS-read 155 mm stealth turret (Part_gun > Mount_gun), at Leviathan's detail: the deck ring with its bolt
    ring, the gunhouse (a lower skirt of armour facets, the chined upper house with recessed panels, flush fastener
    rows along the chines), the roof (plate seams, the sight hood with its slit, the EO ball in its recess, two flush
    hatches with hinges and handles, a louvred vent, lifting eyes, the team band), the raked gun-port housing with
    the barrel's boot, the barrel (thermal shroud segments, the fume extractor) and the multi-baffle brake
    (Gun_barrels / Gun_muzzles, the kick parts), the magazine bustle with its loading door and ladder rungs;
    Muzzle_gun at the brake."""
    a.pivot('Part_gun', (0, -13.2, 3.0))
    m = a.pivot('Mount_gun', (0, 0, .2), 'Part_gun')
    k.lathe(a.part('Gun_ring', 'Steel', 'Part_gun'), [(2.1, -.02), (2.1, .12), (2.0, .2)], seg=28)
    K.bolt_ring(a.part('Kit_bolts', 'Steel', 'Part_gun'), (0, 0, .2), (0, 0, 1), 2.04, 28, r=.03, h=.03)
    skirt = a.part('Gun_skirt', 'Armor', m)
    base = [(-1.0, -2.85), (1.0, -2.85), (2.0, -1.4), (2.1, 2.4), (1.6, 3.0), (-1.6, 3.0), (-2.1, 2.4), (-2.0, -1.4)]
    k.sharp_loft(skirt, [[(px, py, 0) for px, py in base],
                         [(px * .97, py * .97, .38) for px, py in base]], chamfer=.03)
    house = a.part('Gun_house', 'Team', m)
    rings = [
        (.36, [(-.92, -2.7), (.92, -2.7), (1.9, -1.3), (2.0, 2.3), (1.52, 2.85), (-1.52, 2.85), (-2.0, 2.3),
               (-1.9, -1.3)]),
        (1.0, [(-.76, -2.25), (.76, -2.25), (1.62, -1.06), (1.72, 2.12), (1.3, 2.6), (-1.3, 2.6), (-1.72, 2.12),
               (-1.62, -1.06)]),
        (1.5, [(-.4, -1.55), (.4, -1.55), (1.04, -.7), (1.12, 1.84), (.82, 2.2), (-.82, 2.2), (-1.12, 1.84),
               (-1.04, -.7)])]
    k.sharp_loft(house, [[(px, py, pz) for px, py in pts] for pz, pts in rings], chamfer=.04)
    k.inset(house, lambda c, n, f: n.z < .9 and c.z > .45, width=.08, depth=-.015)
    # Flush fastener rows along the lower chine and the roof edge.
    bolts = a.part('Kit_bolts', 'Steel', m)
    for (pz, pts), lift in ((rings[0], .05), (rings[2], -.04)):
        for p0, p1 in zip(pts, pts[1:] + pts[:1]):
            n = max(2, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / .3))
            for i in range(1, n):
                f = i / n
                bolts.cyl(.022, .02, loc=(p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f, pz + lift), seg=6,
                          bevel=0)
    # Roof: plates and seams, the sight hood, the EO ball, two hatches, a vent, lifting eyes, the team band.
    roof = a.part('Gun_roof', 'Armor', m)
    k.extrude(roof, [(px * .9, py * .9 + .05) for px, py in rings[2][1]], .04, loc=(0, 0, 1.52), axis='Z',
              chamfer=.01)
    for yy in (-.5, .5, 1.4):
        a.part('Gun_seams', 'Undercarriage', m).box((1.6, .03, .015), loc=(0, yy, 1.55), bevel=0)
    k.sharp_loft(a.part('Gun_hood', 'Armor', m), [
        [(.25, -1.15, 1.54), (.75, -1.15, 1.54), (.8, -.55, 1.54), (.25, -.55, 1.54)],
        [(.3, -1.0, 1.82), (.7, -1.0, 1.82), (.74, -.6, 1.82), (.3, -.6, 1.82)]], chamfer=.02)
    a.part('Glass', 'Glass', m).box((.34, .02, .1), loc=(.5, -1.1, 1.69), rot=(-.4, 0, 0), bevel=0)
    k.lathe(a.part('Gun_eo', 'Undercarriage', m), [(0, -.02), (.26, -.02), (.26, .06), (0, .06)],
            loc=(-.6, -.75, 1.52), seg=14)
    k.lathe(a.part('Gun_eo_ball', 'Steel', m), [(0, -.18), (.13, -.13), (.18, 0), (.13, .13), (0, .18)],
            loc=(-.6, -.75, 1.6), seg=12)
    a.part('Glass', 'Glass', m).box((.1, .02, .07), loc=(-.6, -.92, 1.62), bevel=0)
    hatch = a.part('Gun_hatches', 'Armor', m)
    for hx, hy in ((.45, .7), (-.4, 1.35)):
        k.block(hatch, (.55, .62, .035), loc=(hx, hy, 1.555), chamfer=.01)
        K.hinge(a.part('Kit_hinges', 'Steel', m), (hx - .2, hy + .33, 1.57), (hx + .2, hy + .33, 1.57), r=.016,
                knuckles=2)
        K.handle(a.part('Kit_handles', 'Steel', m), (hx - .1, hy - .2, 1.575), (hx + .1, hy - .2, 1.575), Vector((0, 0, 1)),
                 h=.03, r=.008)
    for j in range(4):
        a.part('Gun_vents', 'Undercarriage', m).box((.5, .04, .02), loc=(-.4, .25 + j * .1, 1.555), bevel=0)
    for ex, ey in ((.9, 1.8), (-.9, 1.8), (0, -1.35)):
        a.part('Gun_eyes', 'Steel', m).box((.04, .1, .08), loc=(ex, ey, 1.56), bevel=0)
    a.part('Team_band', 'Team', m).box((1.7, .35, .02), loc=(0, .05, 1.555), bevel=0)
    # The gun-port housing: a raked faceted box on the front, the slot, its seams; the boot where the barrel leaves.
    gp = a.part('Gun_port', 'Team', m)
    k.sharp_loft(gp, [[(-.56, -2.95, .2), (.56, -2.95, .2), (.64, -1.2, .2), (-.64, -1.2, .2)],
                      [(-.46, -2.5, 1.5), (.46, -2.5, 1.5), (.52, -1.0, 1.7), (-.52, -1.0, 1.7)]], chamfer=.03)
    k.inset(gp, lambda c, n, f: abs(n.x) > .8, width=.05, depth=-.01)
    a.part('Gun_slot', 'Charred', m).box((.36, .06, 1.0), loc=(0, -2.76, .9), rot=(-.33, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Gun_seams', 'Undercarriage', m).box((.03, 1.7, .04), loc=(s * .56, -1.95, 1.1), rot=(-.25, 0, 0),
                                                     bevel=0)
    zg, y0 = .9, -2.7
    fwd(a.part('Gun_boot', 'Rubber', m), [(.22, 0), (.24, .08), (.19, .16), (.21, .24), (.16, .32), (.17, .38)],
        (0, y0 - .02, zg), seg=14)
    L = 6.8
    fwd(a.part('Gun_barrels', 'Steel', m), [(.15, -.2), (.15, .4), (.17, .45), (.17, 1.6), (.13, 1.7), (.12, 2.6),
                                             (.165, 2.75), (.17, 3.4), (.115, 3.55), (.1, L - .55), (0, L - .55)],
        (0, y0, zg), seg=14)
    for j in range(4):
        fwd(a.part('Bands_barrels', 'Undercarriage', m), [(.18, 0), (.18, .05)], (0, y0 - .55 - j * .3, zg), seg=14)
    br = a.part('Gun_muzzles', 'Armor', m)
    fwd(br, [(.08, L - .55), (.17, L - .53), (.17, L - .4), (.12, L - .37), (.12, L - .3), (.17, L - .27),
             (.17, L - .14), (.12, L - .11), (.12, L - .06), (.16, L - .04), (.16, L), (.08, L)], (0, y0, zg), seg=14)
    for s in (-1, 1):
        for dy in (.47, .2):
            a.part('Ports_muzzles', 'Charred', m).box((.04, .08, .12), loc=(s * .17, y0 - L + dy, zg), bevel=0)
    a.pivot('Muzzle_gun', (0, y0 - L - .05, zg), m)
    K.soot(a, (0, -13.2 + y0 - L, 3.0 + .2 + zg), radius=.6, k=.3)
    # The magazine bustle at the back: the loading door with its frame and hinges, a ladder up its face.
    bu = a.part('Gun_bustle', 'Armor', m)
    k.block(bu, (2.4, .5, .9), loc=(0, 2.95, .6), chamfer=.04, ends=(True, True))
    K.door(a, (.5, 3.21, .3), size=(.7, .6), normal=(0, 1, 0), parent=m, mat='Armor', frame_mat='Steel')
    K.ladder(a.part('Ladders', 'Steel', m), (-.75, 3.22, .25), (-.75, 3.0, 1.45), width=.35, step=.25, facing=(0, 1))
    K.tone(a, 'Part_gun', k=.92)
    return m


def nx_cupola(a, pname, mount, muzzle, loc, tag):
    """A Mk 110-read 57 mm stealth cupola (Part_mg[.001] > Mount_mg[.001]) at Leviathan's detail: the deck ring with
    bolts, the faceted shroud (a skirt, chined upper facets, recessed panels, a fastener row), the raked slot with its
    boot, the barrel in its faceted sleeve with the stealth cap (Cupola_barrels* / Cupola_muzzles*), the roof hatch
    with hinge and handle, the EO window, lifting eyes, the rear access door and vents; Muzzle_* at the cap."""
    p = a.pivot(pname, loc)
    m = a.pivot(mount, (0, 0, .03), p)
    k.lathe(a.part('Cupola_ring' + tag, 'Steel', m), [(1.05, -.02), (1.05, .06), (.98, .08)], seg=22)
    K.bolt_ring(a.part('Kit_bolts', 'Steel', p), (0, 0, .07), (0, 0, 1), 1.0, 16, r=.02, h=.02)
    rings = [
        (.06, [(-.44, -1.08), (.44, -1.08), (.98, -.5), (1.02, .66), (.64, 1.02), (-.64, 1.02), (-1.02, .66),
               (-.98, -.5)]),
        (.24, [(-.42, -1.04), (.42, -1.04), (.95, -.48), (.99, .64), (.62, .99), (-.62, .99), (-.99, .64),
               (-.95, -.48)]),
        (.6, [(-.33, -.86), (.33, -.86), (.78, -.4), (.82, .54), (.5, .84), (-.5, .84), (-.82, .54), (-.78, -.4)]),
        (1.0, [(-.16, -.42), (.16, -.42), (.42, -.18), (.45, .4), (.3, .58), (-.3, .58), (-.45, .4), (-.42, -.18)])]
    sh = a.part('Cupola_house' + tag, 'Team', m)
    k.sharp_loft(sh, [[(x, y, z) for x, y in pts] for z, pts in rings], chamfer=.03)
    k.inset(sh, lambda c, n, f: n.z < .95 and c.z > .3, width=.05, depth=-.01)
    skirt = a.part('Cupola_skirt' + tag, 'Armor', m)
    k.sharp_loft(skirt, [[(x * 1.02, y * 1.02, .02) for x, y in rings[0][1]],
                         [(x * 1.02, y * 1.02, .22) for x, y in rings[1][1]]], chamfer=.015)
    bolts = a.part('Kit_bolts', 'Steel', m)
    pts = rings[2][1]
    for p0, p1 in zip(pts, pts[1:] + pts[:1]):
        n = max(2, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / .22))
        for i in range(1, n):
            f = i / n
            bolts.cyl(.016, .015, loc=(p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f, .64), seg=6, bevel=0)
    a.part('Cupola_slot' + tag, 'Charred', m).box((.2, .05, .5), loc=(0, -.97, .44), rot=(-.25, 0, 0), bevel=0)
    zg, y0 = .42, -.95
    fwd(a.part('Cupola_boot' + tag, 'Rubber', m), [(.11, 0), (.12, .05), (.095, .1), (.1, .15), (.08, .2)],
        (0, y0 - .02, zg), seg=10)
    k.extrude(a.part('Cupola_sleeve' + tag, 'Team', m), [(-.1, -.06), (-.05, -.11), (.05, -.11), (.1, -.06), (.1, .06),
                                                         (.05, .11), (-.05, .11), (-.1, .06)], .75,
              loc=(0, y0 - .45, zg), rot=(R90, 0, 0), axis='Z', chamfer=.015, taper=.8)
    L = 3.1
    fwd(a.part('Cupola_barrels' + tag, 'Steel', m), [(.07, -.1), (.07, .9), (.055, .98), (.048, L - .35),
                                                      (.06, L - .3)], (0, y0, zg), seg=10)
    for j in range(2):
        fwd(a.part('Cbands_barrels' + tag, 'Undercarriage', m), [(.075, 0), (.075, .04)], (0, y0 - 1.0 - j * .3, zg),
            seg=10)
    k.extrude(a.part('Cupola_muzzles' + tag, 'Team', m), [(-.08, -.05), (-.04, -.09), (.04, -.09), (.08, -.05),
                                                          (.08, .05), (.04, .09), (-.04, .09), (-.08, .05)], .32,
              loc=(0, y0 - L + .14, zg), rot=(R90, 0, 0), axis='Z', chamfer=.01, taper=.8)
    a.pivot(muzzle, (0, y0 - L - .05, zg), m)
    # Roof hatch with hinge and handle, the EO window, lifting eyes; the rear access door and vents.
    k.block(a.part('Cupola_hatch' + tag, 'Armor', m), (.36, .3, .03), loc=(0, .15, 1.0), chamfer=.01)
    K.hinge(a.part('Kit_hinges', 'Steel', m), (-.12, .31, 1.02), (.12, .31, 1.02), r=.014, knuckles=2)
    K.handle(a.part('Kit_handles', 'Steel', m), (-.07, .02, 1.025), (.07, .02, 1.025), Vector((0, 0, 1)), h=.025, r=.007)
    a.part('Glass', 'Glass', m).box((.18, .02, .07), loc=(.3, -.62, .76), rot=(-.6, 0, .35), bevel=0)
    for ex, ey in ((.4, .5), (-.4, .5)):
        a.part('Cupola_eyes' + tag, 'Steel', m).box((.03, .07, .06), loc=(ex, ey, .9), bevel=0)
    k.block(a.part('Cupola_door' + tag, 'Armor', m), (.4, .04, .34), loc=(0, .99, .38), rot=(.25, 0, 0), chamfer=.01)
    for s in (-1, 1):
        for j in range(3):
            a.part('Cupola_vents' + tag, 'Undercarriage', m).box((.18, .02, .025),
                                                                 loc=(s * .42, .92, .3 + j * .07),
                                                                 rot=(0, 0, s * .6), bevel=0)
    K.tone(a, pname, k=.9)
    return m
