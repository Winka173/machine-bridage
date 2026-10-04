"""Play-test 14 boss redraw R2 (lane A): the sea bosses' last shared or carried-over sub-assemblies, drawn from scratch.

Owner (04/10, Docs/prompts/playtest14_vi.txt, last block): "đừng reuse gì hết, tất cả boss khi vẽ lại đều vẽ lại từ đầu";
"kraken có thể triệu hồi máy bay do là tàu sân bay"; "typhon: tháp súng không hề quay mà bắn được ngược hướng, các tên lửa
phải bắn từ các bệ phóng thân tàu lên cao rồi bay xuống". Audit: Docs/models/pt14_reuse_audit.md; DECISIONS "Play-test 14
boss redraw R2 (lane A)".

Every function here draws for one boss only (no other model calls it), from geometry primitives, at that boss's scale,
read from a real design:
- typhon (Project 941 Akula, "Typhoon"): the whole boat. The very wide flat double hull, the raised missile deck with its
  twenty hatches FORWARD of the sail (Part_doors_l / Part_doors_r, the launch doors), the long low sail set aft with its
  ice-strengthened top, rescue capsule outlines, masts and the Igla-style SAM turret (Mount_missile), the twin
  shrouded seven-blade screws, the stern planes and the upper rudder with the towed-array pod (Part_rudder), the bow
  sonar (Part_sonar). The game's guns: a retractable 100 mm turret in a deck well on the forecasing (Mount_gun.002, the
  deck_gun part), an AK-725-style twin 57 mm on a pedestal ahead of the sail (Mount_gun) and one on the after casing
  (Mount_gun.001).
- kraken (a Kiev / Kuznetsov heavy aviation cruiser): MK-1-style triple 406 mm turrets (rounded rear, rangefinder in
  the rear wall with its ears, armoured port sleeves), MK-5-style triple 152 mm in sleeping wells, AK-726-style twin
  127 mm, Kashtan-style gun / missile modules in the deck-edge galleries, AK-630M-2 "Duet" twin gatlings, a Shtorm-style
  twin-arm SAM launcher, Owl Screech-style directors, a Top Sail-style search radar, flush Granit hatches (Part_vls), a
  Ka-31-style radar helicopter, the deck's two catapults, the lowered lift and parked / launching A-12-type strike jets
  (the stealth_naval_strike the kraken_jets skill launches).
- hydra_sub: its mast radar (a Snoop Pair-style slotted surface-search array).

Runtime names are the ones each mount had (Part_* / Mount_* / Muzzle_* / Radar; the barrels a mount kicks are its pivot's
`<word>_barrels` / `<word>_muzzles` parts, ModelLibrary.IsMountBarrel). Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_pt14_r5_sea as R5

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


def aft(part, profile, loc, seg=14):
    """A turned part along +Y (aft): profile [(radius, distance aft)] from loc."""
    k.lathe(part, profile, loc=loc, rot=K.BACKWARD, seg=seg)


def along_x(part, profile, loc, seg=12):
    k.lathe(part, profile, loc=loc, rot=(0, R90, 0), seg=seg)


def rounded_rect(w, d, r, n=3):
    """A rounded rectangle's outline (x, y), counter-clockwise, corner radius r with n steps a corner."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -d / 2 + r, -R90), (w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, R90),
                       (-w / 2 + r, -d / 2 + r, math.pi)):
        for i in range(n + 1):
            u = a0 + i / n * R90
            pts.append((cx + math.cos(u) * r, cy + math.sin(u) * r))
    return pts


# ============================================================================= typhon
TY_DECK = 3.6                 # the casing deck (flat over the middle body)
TY_ET, TY_EB = .34, .52       # superellipse exponents of the section: flat top, fuller bottom
# Stations (y, half beam, top, bottom): the blunt bow, the parallel body, the broad flattened stern.
TY_ST = [(-29.2, 1.25, 1.9, -.4), (-28.4, 2.7, 2.85, -1.55), (-27.0, 3.9, 3.3, -2.45), (-24.8, 4.85, 3.5, -2.95),
         (-21.5, 5.45, 3.58, -3.15), (-17.0, 5.72, TY_DECK, -3.2), (9.0, 5.75, TY_DECK, -3.2),
         (13.5, 5.55, 3.5, -3.05), (17.5, 4.95, 3.2, -2.7), (21.0, 3.95, 2.65, -2.1), (23.8, 2.9, 2.0, -1.45),
         (25.8, 1.95, 1.35, -.85), (27.0, 1.15, .85, -.4)]
TY_HUMP = (-19.0, -4.7, 4.15)   # the missile deck: front, back, top
TY_DOOR_Y = (-18.25, -5.45)     # first / last hatch centres (ten a row)
TY_DOOR_X = 1.72
TY_SAIL = (0, 3.1, TY_DECK)     # Part_sail
TY_100 = (0, -22.4, TY_DECK)    # Mount_gun.002's well
TY_57F = (0, -3.45, TY_DECK)    # Mount_gun's pedestal (ahead of the sail)
TY_57A = (0, 15.2, 3.41)        # Mount_gun.001's barbette (after casing)
TY_57S = 20.5                   # Mount_gun.003's barbette (stern casing; lane sea)


def _ty_station(y):
    """(half beam, top, bottom) at y, linear between the stations."""
    st = TY_ST
    if y <= st[0][0]:
        return st[0][1:]
    for (y0, *a0), (y1, *a1) in zip(st, st[1:]):
        if y <= y1:
            f = (y - y0) / (y1 - y0)
            return tuple(p + (q - p) * f for p, q in zip(a0, a1))
    return st[-1][1:]


def _ty_ring(y, n=28, grow=0.0):
    W, top, bot = _ty_station(y)
    W += grow
    zc, H = (top + bot) / 2, (top - bot) / 2 + grow
    pts = []
    for i in range(n):
        u = i / n * TAU
        c, s = math.cos(u), math.sin(u)
        e = TY_ET if s > 0 else TY_EB
        pts.append((W * math.copysign(abs(c) ** e, c), y, zc + H * math.copysign(abs(s) ** e, s)))
    return pts


def _ty_half(y, z, grow=0.0):
    """The hull's half beam at (y, z) (0 outside the section)."""
    W, top, bot = _ty_station(y)
    zc, H = (top + bot) / 2, (top - bot) / 2
    t = abs(z - zc) / H
    if t >= 1:
        return 0.0
    e = TY_ET if z > zc else TY_EB
    return W * (1 - t ** (2 / e)) ** (e / 2) + grow


def _ty_top(y, x=0.0):
    """The hull top's height at (x, y)."""
    W, top, bot = _ty_station(y)
    zc, H = (top + bot) / 2, (top - bot) / 2
    t = min(1.0, abs(x) / W)
    return zc + H * (1 - t ** (2 / TY_ET)) ** (TY_ET / 2)


def _ty_hull(a):
    """The outer hull (one loft of superellipse sections), the anechoic tile coating in patches (renewed tiles darker,
    a few fallen off), the tile seams, the limber holes, the boot topping, the draft marks, the bow planes, the anchor
    recess, the towed-array conduit, the hull's Team band."""
    rings = [[(0, -29.6, .85)]] + [_ty_ring(y) for y, *_ in TY_ST] + [[(0, 27.55, .22)]]
    a.part('Hull', 'Armor').loft(rings)
    # Deck tiles: big rubber tiles in rows over the flat deck, some renewed (darker) or fallen off (bare steel).
    tiles, new, bare = a.part('Deck_tiles', 'Armor'), a.part('Deck_tiles_new', 'Undercarriage'), \
        a.part('Deck_tiles_bare', 'Steel')
    for j in range(40):
        y = -27.4 + j * 1.18
        if TY_HUMP[0] - .3 < y < TY_HUMP[1] + .3 or abs(y - TY_100[1]) < 1.9 or abs(y - TY_57A[1]) < 1.6 or \
                -1.9 < y < 10.3:
            continue
        W, top, _ = _ty_station(y)
        half = min(W * .62, 3.6)
        n = max(2, int(half * 2 / 1.15))
        for c in range(n):
            x = -half + (c + .5) * (2 * half / n)
            code = (j * 7 + c * 5) % 13
            part = bare if code == 0 else new if code in (4, 9) else tiles
            part.box((2 * half / n - .1, 1.06, .04), loc=(x, y, _ty_top(y, x) + .02), bevel=0)
    # Side tiles as staggered strakes along the upper flanks (the curved part of the section).
    for s in (-1, 1):
        for j in range(30):
            y = -24.0 + j * 1.55
            for zz, row in ((1.6, 0), (2.7, 1)):
                hw = _ty_half(y, zz)
                if hw < 1.0:
                    continue
                code = (j * 5 + row * 3 + (s > 0)) % 9
                if code in (2, 6):
                    part = new if code == 2 else bare
                    tilt = math.atan2(hw - _ty_half(y, zz + .3), .3)
                    part.box((.04, 1.4, .95), loc=(s * (hw + .015), y, zz), rot=(0, s * -tilt, 0), bevel=0)
    seams = a.part('Tile_seams', 'Undercarriage')
    for zz in (.9, 2.2):
        for s in (-1, 1):
            seams.tube([(s * (_ty_half(y, zz) + .012), y, zz) for y in range(-26, 25, 2)], .022, seg=3, caps=False)
    for y in range(-25, 24, 3):
        for s in (-1, 1):
            pts = [(s * (_ty_half(y, z) + .012), y, z) for z in (-1.8, -.6, .6, 1.8, 2.8) if _ty_half(y, z) > .2]
            if len(pts) > 1:
                seams.tube(pts, .016, seg=3, caps=False)
    # Limber holes in rows along the casing's shoulder (the free-flooding space), the boot topping at the waterline.
    holes = a.part('Limber_holes', 'Charred')
    for s in (-1, 1):
        for j in range(44):
            y = -22.5 + j * .95
            zz = 3.05 if y < 14 else _ty_top(y) - .55
            hw = _ty_half(y, zz)
            if hw < 1.2:
                continue
            holes.box((.05, .52, .16), loc=(s * (hw + .006), y, zz), rot=(0, s * -.5, 0), bevel=0)
        a.part('Boot_top', 'BarrelRed').tube([(s * (_ty_half(y, .12) + .03), y, .12) for y in range(-27, 27)], .1,
                                            seg=4, caps=False)
        a.part('Team_band', 'Team').tube([(s * (_ty_half(y, 2.0) + .03), y, 2.0) for y in range(-17, 9, 2)], .14,
                                        seg=4, caps=False)
    marks = a.part('Draft_marks', 'PlasterWhite')
    for y in (-27.6, 25.6):
        for s in (-1, 1):
            for z in (-.6, -.2, .2, .6, 1.0):
                hw = _ty_half(y, z)
                if hw > .2:
                    marks.box((.02, .42, .08), loc=(s * (hw + .03), y, z), bevel=0)
    # The bow planes (out, as surfaced at manoeuvring speed), their root fairings; the anchor recess.
    bp = a.part('Bow_planes', 'Armor')
    for s in (-1, 1):
        x0 = _ty_half(-21.6, .9)
        k.extrude(bp, [(-1.0, -.06), (-.6, -.11), (.9, -.05), (1.1, 0), (.9, .05), (-.6, .11), (-1.0, .06)],
                  6.55 - x0 + .15, loc=(s * (x0 + 6.55) / 2 - s * .07, -21.6, .9), axis='X', chamfer=.03,
                  taper=(.7, 1.0) if s > 0 else 1.0)
        k.extrude(bp, [(-.7, -.2), (.7, -.2), (.7, .2), (-.7, .2)], .35, loc=(s * (x0 + .05), -21.6, .9), axis='X',
                  chamfer=.05)
        a.part('Anchor_recess', 'Charred').box((.05, .9, .6), loc=(s * (_ty_half(-26.4, 1.9) + .01), -26.4, 1.9),
                                               rot=(0, 0, s * -.5), bevel=0)
    # The towed-array conduit along the right flank, its fairlead at the stern.
    ta = a.part('Towed_conduit', 'Steel')
    ta.tube([(-(_ty_half(y, 2.45) + .06), y, 2.45) for y in range(-12, 22, 2)], .07, seg=6)


def _ty_deck(a):
    """The forecasing and after casing fittings: the retractable cleats, the capstan, the weapons-loading hatch, the
    escape hatches, the vents, the safety track, the rescue buoys, the mooring rope coil."""
    st = a.part('Deck_steel', 'Steel')
    for s in (-1, 1):
        for y in (-25.4, -20.0, 11.5, 17.0, 20.5):
            x = s * min(_ty_station(y)[0] * .7, 3.6)
            z = _ty_top(y, x)
            st.box((.16, .55, .1), loc=(x, y, z + .05), bevel=0)
            st.cyl(.09, .22, loc=(x, y - .18, z + .13), seg=6, bevel=0)
            st.cyl(.09, .22, loc=(x, y + .18, z + .13), seg=6, bevel=0)
    k.lathe(st, [(.3, 0), (.3, .16), (.22, .2), (.22, .38), (.28, .42), (0, .44)], loc=(.9, -26.0, _ty_top(-26.0, .9)),
            seg=12)
    # The weapons-loading hatch on the bow (a long raked hatch with its hinge), round escape hatches.
    hz = _ty_top(-25.0)
    k.block(a.part('Deck_hatches', 'Armor'), (1.0, 2.2, .12), loc=(-.9, -25.0, hz - .02), rot=(-.05, 0, 0), chamfer=.04)
    st.cyl(.06, 1.0, loc=(-.9, -23.9, hz + .08), rot=(0, R90, 0), seg=6, bevel=0)
    for y in (18.6, -19.8):
        z = _ty_top(y)
        k.lathe(a.part('Deck_hatches', 'Armor'), [(.55, 0), (.55, .08), (.46, .13), (0, .15)], loc=(0, y, z - .01),
                seg=16)
        k.ring(a.part('Hatch_rims', 'Hazard'), [(.57, -.01), (.66, -.01), (.66, .03), (.57, .03)], loc=(0, y, z),
               seg=16)
    # Ventilation and snorkel induction grilles on the after casing, the safety track down the middle.
    for x, y in ((1.7, 19.4), (-1.7, 19.4), (1.4, 21.6), (-1.4, 21.6)):
        K.grille(a, (x, y, _ty_top(y, x) + .03), 1.0, .7, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    trk = a.part('Safety_track', 'Steel')
    trk.tube([(0, y, _ty_top(y) + .03) for y in (-27.0, -24.6, -21.5)], .03, seg=4, caps=False)
    trk.tube([(0, y, _ty_top(y) + .03) for y in (16.8, 19.0, 22.0, 24.0)], .03, seg=4, caps=False)
    for x, y in ((-2.6, -23.0), (2.6, 12.0)):
        K.chamfer_box(a.part('Rescue_buoys', 'Hazard'), (1.2, .8, .1), loc=(x, y, _ty_top(y, x) + .05), c=.03)
    k.ring(a.part('Rope_coil', 'Canvas'), [(.22, 0), (.42, 0), (.42, .11), (.22, .11)], loc=(2.4, -24.2,
                                                                                           _ty_top(-24.2, 2.4)), seg=10)
    # Lifelines on the forecasing and after casing (rigged while surfaced).
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-26.4, -20.2), (16.4, 22.6)):
            ys = [y0 + i * (y1 - y0) / 6 for i in range(7)]
            K.railing(rail, [(s * 2.9, y, _ty_top(y, s * 2.9)) for y in ys], h=.85, post=1.05, r=.022)


def _ty_silo(a):
    """The missile deck forward of the sail: the raised flat hump over the twenty tubes (two rows of ten, as on the real
    boat), its sloped sides with limber slots; each tube under a rounded-square hatch on its outboard hinge, rimmed,
    with its locking lugs; the left row on Part_doors_l, the right row on Part_doors_r (the launch doors)."""
    y0, y1, zt = TY_HUMP
    hump = a.part('Missile_deck', 'Armor')
    base = [(-4.15, y0 - .9), (4.15, y0 - .9), (4.45, y0 + .2), (4.45, y1 - .3), (4.0, y1 + .6), (-4.0, y1 + .6),
            (-4.45, y1 - .3), (-4.45, y0 + .2)]
    top = [(-3.55, y0), (3.55, y0), (3.75, y0 + .5), (3.75, y1 - .3), (3.45, y1), (-3.45, y1), (-3.75, y1 - .3),
           (-3.75, y0 + .5)]
    k.sharp_loft(hump, [[(x, y, TY_DECK - .25) for x, y in base], [(x, y, zt) for x, y in top]], chamfer=.06)
    slots = a.part('Limber_holes', 'Charred')
    for s in (-1, 1):
        for j in range(12):
            y = y0 + .9 + j * 1.15
            slots.box((.04, .55, .14), loc=(s * 4.11, y, TY_DECK + .22), rot=(0, s * -.92, 0), bevel=0)
    # The walkway between the rows (non-skid), its safety track, the hump's tile patches and the Team marks.
    a.part('Walkway', 'Asphalt').box((.9, y1 - y0 - .6, .02), loc=(0, (y0 + y1) / 2, zt + .01), bevel=0)
    a.part('Safety_track', 'Steel').tube([(0, y0 + .4, zt + .04), (0, y1 - .4, zt + .04)], .03, seg=4, caps=False)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.1, y1 - y0 - 1.2, .02), loc=(s * 3.45, (y0 + y1) / 2, zt + .012), bevel=0)
    lid = rounded_rect(1.22, 1.16, .3)
    for nm, s in (('Part_doors_l', 1), ('Part_doors_r', -1)):
        yc = (TY_DOOR_Y[0] + TY_DOOR_Y[1]) / 2
        p = a.pivot(nm, (s * TY_DOOR_X, yc, zt))
        side = nm[5:]
        lids = a.part(f'Hatch_{side}', 'Team', p)
        rims = a.part(f'Hatch_rims_{side}', 'Steel', p)
        hinge = a.part(f'Hatch_hinges_{side}', 'Steel', p)
        lugs = a.part('Kit_bolts', 'Steel', p)
        for j in range(10):
            y = TY_DOOR_Y[0] + j * (TY_DOOR_Y[1] - TY_DOOR_Y[0]) / 9 - yc
            k.extrude(rims, rounded_rect(1.38, 1.3, .36), .05, loc=(0, y, .025), axis='Z', chamfer=.012)
            k.extrude(lids, lid, .1, loc=(0, y, .1), axis='Z', chamfer=.03, taper=.94)
            hinge.cyl(.065, .82, loc=(s * .66, y, .12), rot=(R90, 0, 0), seg=8, bevel=0)
            for dy in (-.28, .28):
                hinge.box((.16, .12, .08), loc=(s * .6, y + dy, .1), bevel=0)
            for dx, dy in ((-s * .54, -.4), (-s * .54, .4), (-s * .62, 0)):
                lugs.box((.1, .1, .07), loc=(dx, y + dy, .07), bevel=0)
            # A dark sealing line round the lid, the tube number plate.
            a.part('Hatch_seals', 'Charred', p).box((1.24, .03, .015), loc=(0, y - .6, .055), bevel=0)
        K.tone(a, nm, k=.86)


def _ty_sail_ring(yr, w, h, n=7):
    """One cross-section of the sail (relative to Part_sail): sides with a slight tumblehome, the rounded ice cap."""
    right = [(w * 1.03, -.25), (w * 1.02, h * .3), (w, h * .62), (w * .96, h - .6), (w * .84, h - .24),
             (w * .55, h - .05)]
    pts = right + [(0, h)] + [(-x, z) for x, z in reversed(right)]
    return [(x, yr, z) for x, z in pts]


def _ty_sail(a):
    """Part_sail: the long low sail set aft (the real boat's), its rounded front and long sloping tail, the ice-
    strengthened cap, the bridge cockpit with its windows, the rescue capsule outlines either side, the access doors,
    the rungs, the masts (two periscopes, the snorkel with its exhaust, the radar mast, the ESM mast, the comms whips),
    the navigation lights; the SAM turret on its raised mast (Mount_missile > Muzzle_missile)."""
    p = a.pivot('Part_sail', TY_SAIL)
    secs = [(-5.05, .5, 4.9), (-4.85, 1.05, 5.35), (-4.4, 1.48, 5.55), (-3.6, 1.72, 5.62), (-2.0, 1.8, 5.62),
            (1.5, 1.74, 5.6), (3.0, 1.55, 4.75), (4.5, 1.3, 3.55), (6.0, .95, 2.2), (7.4, .45, .75)]
    a.part('Sail', 'Armor', p).loft([_ty_sail_ring(yr, w, h) for yr, w, h in secs])
    # The ice cap: a thicker band round the top edge (Steel worn), the flat bridge deck, the Team band.
    cap = a.part('Sail_cap', 'Undercarriage', p)
    cap.loft([[(x * 1.012, yr, z + .015) for x, yr, z in _ty_sail_ring(yr, w, h)[3:10]] for yr, w, h in secs[1:7]])
    seams = a.part('Sail_seams', 'Undercarriage', p)
    for s in (-1, 1):
        for zz, xx in ((1.2, 1.835),):
            seams.box((.025, 5.0, .05), loc=(s * xx, -1.05, zz), bevel=0)
    band = a.part('Team_band', 'Team', p)
    for s in (-1, 1):
        band.box((.03, 5.1, .26), loc=(s * 1.815, -1.05, 3.72), bevel=0)
    # Bridge cockpit: an open well in the cap's front with its windscreen and the windows round the front.
    glass = a.part('Sail_windows', 'Glass', p)
    for i in range(7):
        u = (i - 3) * .26
        glass.box((.3, .04, .26), loc=(math.sin(u) * 1.62, -4.45 + (1 - math.cos(u)) * 1.7, 5.05), rot=(0, 0, u),
                  bevel=0)
    k.block(a.part('Bridge_well', 'Charred', p), (1.5, 1.3, .1), loc=(0, -3.6, 5.56), chamfer=.03)
    a.part('Windscreen', 'Glass', p).box((1.5, .04, .4), loc=(0, -4.3, 5.8), rot=(-.5, 0, 0), bevel=0)
    rails = a.part('Railings', 'Steel', p)
    K.railing(rails, [(-.85, -4.15, 5.62), (-.85, -2.9, 5.62), (.85, -2.9, 5.62), (.85, -4.15, 5.62)], h=.7, post=.6,
              r=.02)
    # Rescue capsule outlines (the real boat's two pop-up capsules in the sail's base), doors, rungs, lights.
    cap_o = a.part('Capsule_seams', 'Charred', p)
    for s in (-1, 1):
        x = s * 1.83
        pts = [(x, -.6 + math.cos(u) * 1.5, 1.7 + math.sin(u) * .75) for u in (i * TAU / 16 for i in range(17))]
        cap_o.tube(pts, .03, seg=4, caps=False)
        K.door(a, (s * 1.84, 2.4, .05), size=(.8, 1.6), normal=(s, 0, 0), parent=p, mat='Armor', frame_mat='Steel')
        K.ladder(a.part('Rungs', 'Steel', p), (s * 1.86, -3.0, .2), (s * 1.8, -3.0, 5.2), width=.4, step=.34,
                 facing=(s, 0))
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen', p).box((.04, .3, .12), loc=(s * 1.78, -2.6, 4.7),
                                                                             bevel=0)
    # The masts behind the bridge (heights inside the old model's 11.9 m).
    masts = a.part('Masts', 'Steel', p)
    heads = a.part('Mast_heads', 'Armor', p)
    for x, y, h, r in ((.32, -2.2, 1.9, .13), (-.32, -1.7, 1.6, .16)):     # attack and search periscopes
        masts.cyl(r, h, loc=(x, y, 5.6 + h / 2), seg=10, bevel=0)
        k.block(heads, (r * 2.2, r * 3.0, .42), loc=(x, y - r * .4, 5.6 + h), chamfer=.04, taper=(.85, .8))
        glass.box((r * 1.4, .02, .14), loc=(x, y - r * 1.9, 5.6 + h + .22), bevel=0)
    masts.cyl(.22, 1.5, loc=(0, -.5, 6.35), seg=10, bevel=0)                 # snorkel
    k.lathe(heads, [(.3, 0), (.3, .45), (.24, .55), (0, .58)], loc=(0, -.5, 7.1), seg=10)
    a.part('Snorkel_exhaust', 'Charred', p).box((.16, .4, .3), loc=(0, -.1, 7.25), bevel=0)
    K.soot(a, (0, TY_SAIL[1] - .1, TY_SAIL[2] + 7.4), radius=.6, k=.35)
    masts.cyl(.11, 1.7, loc=(.45, .6, 6.45), seg=8, bevel=0)                 # ESM mast
    k.lathe(heads, [(.18, 0), (.2, .12), (.2, .42), (.14, .5), (0, .54)], loc=(.45, .6, 7.3), seg=10)
    for i in range(6):
        u = i * TAU / 6
        a.part('Esm_ribs', 'Undercarriage', p).box((.03, .06, .3), loc=(.45 + math.cos(u) * .205,
                                                                          .6 + math.sin(u) * .205, 7.57),
                                                    rot=(0, 0, u), bevel=0)
    for x, h in ((-.5, 1.6), (.15, 2.1)):
        K.whip_antenna(a.part('Antennas', 'Steel', p), (x, 1.3, 5.6), h=h, r=.025, lean=0)
    # The SAM turret (Strela-3 / Igla-style, raised for the boss): its mast, the trainable head with four tubes.
    masts.cyl(.2, 1.0, loc=(0, 1.9, 6.05), seg=10, bevel=0)
    m = a.pivot('Mount_missile', (0, 1.9, 6.55), p)
    k.lathe(a.part('Sam_head', 'Team', m), [(.42, 0), (.44, .08), (.4, .34), (.26, .46), (0, .48)], seg=12)
    k.block(a.part('Sam_frame', 'Armor', m), (1.16, .26, .2), loc=(0, .1, .26), chamfer=.02)
    tubes = a.part('Sam_tubes', 'Steel', m)
    caps_ = a.part('Sam_tube_caps', 'Charred', m)
    for sx in (-1, 1):
        for dz in (.13, .4):
            fwd(tubes, [(.085, -.55), (.095, -.5), (.095, .62), (.085, .66)], (sx * .43, .0, dz), seg=10)
            caps_.cyl(.07, .02, loc=(sx * .43, -.665, dz), rot=K.FORWARD, seg=10, bevel=0)
        k.block(a.part('Sam_frame', 'Armor', m), (.1, .5, .62), loc=(sx * .27, .05, .0), chamfer=.015)
    a.part('Sam_sight', 'Glass', m).box((.16, .03, .1), loc=(0, -.4, .4), bevel=0)
    a.pivot('Muzzle_missile', (.43, -.68, .4), m)
    K.tone(a, 'Part_sail', k=.92)


def _ty_well(a, loc, R, depth=.12):
    """A retractable gun's deck well (Mount_gun.002 sleeps in it until its phase wakes it, VehicleView.WakeMounts):
    the lip ring flush with the deck, the dark well floor, the two hatch leaves folded open on their hinges."""
    x, y, z = loc
    k.ring(a.part('Well_lip', 'Steel'), [(R, -.12), (R + .28, -.12), (R + .28, .05), (R + .2, .08), (R, .08)],
           loc=loc, seg=28)
    a.part('Well_floor', 'Charred').cyl(R, .04, loc=(x, y, z + .02), seg=28, bevel=0)
    k.ring(a.part('Well_lip', 'Hazard'), [(R + .03, .081), (R + .2, .081), (R + .2, .095), (R + .03, .095)],
           loc=loc, seg=28)
    leaves = a.part('Well_doors', 'Armor')
    hinge = a.part('Kit_hinges', 'Steel')
    for s in (-1, 1):
        # Each leaf is half the hatch, stood up nearly vertical on its outboard hinge (open for the gun to rise).
        prof = [(R * math.cos(u), R * math.sin(u)) for u in (i * math.pi / 10 for i in range(11))]
        k.extrude(leaves, [(py, px) for px, py in prof], .1, loc=(x + s * (R + .32), y, z + .08), rot=(0, s * .12, 0),
                  axis='X', chamfer=.02)
        hinge.cyl(.07, R * 1.5, loc=(x + s * (R + .25), y, z + .1), rot=(R90, 0, 0), seg=8, bevel=0)


def _ty_100(a):
    """The retractable 100 mm (Mount_gun.002, the deck_gun part): a low pressure-tight turtle-back gunhouse in its deck
    well, the ball mantlet, the long barrel with its double-baffle brake (Dg_barrels / Dg_muzzles, the kick parts),
    the sight head, the roof hatch, lifting eyes, the rear vent; Muzzle_gun.002 at the brake's mouth."""
    _ty_well(a, TY_100, 1.48)
    m = a.pivot('Mount_gun__002', (TY_100[0], TY_100[1], TY_100[2] + .09))
    k.ring(a.part('Dg_ring', 'Steel', m), [(1.3, -.02), (1.38, -.02), (1.38, .08), (1.3, .1)], seg=28)
    k.lathe(a.part('Dg_house', 'Team', m), [(1.34, 0), (1.37, .12), (1.3, .46), (1.08, .78), (.62, .98), (0, 1.04)],
            seg=28, worn=(2,))
    # The flattened front: a sloped armour face over the mantlet.
    k.block(a.part('Dg_face', 'Armor', m), (1.3, .5, .6), loc=(0, -1.02, .22), rot=(.45, 0, 0), chamfer=.06)
    zg = .52
    k.lathe(a.part('Dg_mantlet', 'Armor', m), [(0, -.36), (.26, -.3), (.36, -.12), (.36, .12), (.26, .3), (0, .36)],
            loc=(0, -1.18, zg), rot=K.FORWARD, seg=14)
    L = 3.55
    y0 = -1.5
    fwd(a.part('Dg_barrels', 'Steel', m), [(.11, 0), (.11, .32), (.088, .4), (.075, 2.6), (.08, 2.95), (.072, 3.1),
                                           (0, 3.1)], (0, y0, zg), seg=12)
    br = a.part('Dg_muzzles', 'Undercarriage', m)
    fwd(br, [(.07, 0), (.12, .02), (.12, .14), (.1, .16), (.1, .26), (.12, .28), (.12, .44), (.085, .46), (0, .46)],
        (0, y0 - 3.05, zg), seg=12)
    for s in (-1, 1):
        for dy in (-.08, -.24):
            br.box((.03, .06, .14), loc=(s * .12, y0 - 3.05 + dy, zg), bevel=0)
    a.pivot('Muzzle_gun__002', (0, y0 - 3.05 - .47, zg), m)
    K.soot(a, (TY_100[0], TY_100[1] + y0 - L, TY_100[2] + zg), radius=.5, k=.3)
    # Roof: the commander's sight head, the hatch, lifting eyes; the rear vent, the radar-laid EO ball.
    k.block(a.part('Dg_sight', 'Armor', m), (.34, .42, .32), loc=(.5, -.35, .86), chamfer=.04, taper=(.8, .8))
    a.part('Glass', 'Glass', m).box((.22, .02, .1), loc=(.5, -.57, 1.02), bevel=0)
    k.lathe(a.part('Dg_hatch', 'Armor', m), [(.36, 0), (.36, .06), (.3, .1), (0, .11)], loc=(-.4, .3, .9), seg=12)
    eyes = a.part('Dg_eyes', 'Steel', m)
    for x, y in ((.9, .5), (-.9, .5), (0, .95)):
        eyes.box((.06, .16, .14), loc=(x, y, _ty_dome_z(x, y) + .04), rot=(0, 0, math.atan2(y, x)), bevel=0)
    K.grille(a, (0, 1.2, .5), .6, .3, facing=(0, 1, .3), slats=4, parent=m, frame_mat='Armor')
    k.lathe(a.part('Dg_eo', 'Armor', m), [(0, -.18), (.16, -.14), (.2, 0), (.16, .14), (0, .18)], loc=(-.62, -.55, .9),
            seg=10)
    a.part('Glass', 'Glass', m).box((.12, .02, .08), loc=(-.62, -.74, .9), bevel=0)


def _ty_dome_z(x, y):
    r = math.hypot(x, y)
    prof = [(1.34, 0), (1.37, .12), (1.3, .46), (1.08, .78), (.62, .98), (0, 1.04)]
    for (r0, z0), (r1, z1) in zip(prof[::-1], prof[::-1][1:]):
        if r0 <= r <= r1:
            return z0 + (z1 - z0) * (r - r0) / (r1 - r0)
    return 0.0


def _ty_57(a, index, loc, pedestal):
    """An AK-725-style twin 57 mm on its yaw pivot Mount_gun[.001]: the drum gunhouse with its domed roof and the flat
    sloped front, the two water-jacketed barrels with their slotted brakes (Gun_barrels / Gun_muzzles[_001], the kick
    parts), the sight blister, the rear hatch and vent; the fixed pedestal / barbette under it (`pedestal` m high, ribbed);
    Muzzle_gun[.001] between the brakes and the per-barrel muzzles."""
    tag = '' if index == 0 else f'_{index:03d}'
    x, y, z = loc
    ped = a.part('Gun_pedestal' + tag, 'Armor')
    k.lathe(ped, [(1.22, -.15), (1.22, pedestal * .2), (1.08, pedestal * .55), (1.06, pedestal), (.98, pedestal + .02)],
            loc=(x, y, z), seg=24)
    if pedestal > .6:
        for i in range(8):
            u = i * TAU / 8 + TAU / 16
            ped.box((.08, .22, pedestal * .7), loc=(x + math.cos(u) * 1.12, y + math.sin(u) * 1.12, z + pedestal * .4),
                    rot=(0, 0, u), bevel=0)
        K.ladder(a.part('Rungs', 'Steel'), (x + .0, y + 1.12, z), (x, y + 1.08, z + pedestal), width=.4, step=.3,
                 facing=(0, 1))
    m = a.pivot(K.name('Mount_gun', index), (x, y, z + pedestal + .03))
    k.ring(a.part('Gun_ring' + tag, 'Steel', m), [(.94, -.02), (1.0, -.02), (1.0, .07), (.94, .09)], seg=24)
    k.lathe(a.part('Gun_house' + tag, 'Team', m), [(.96, 0), (.98, .1), (.98, .6), (.9, .8), (.66, .95), (.3, 1.02),
                                                   (0, 1.03)], seg=24, worn=(2,))
    k.block(a.part('Gun_face' + tag, 'Armor', m), (1.32, .36, .78), loc=(0, -.86, .1), rot=(.38, 0, 0), chamfer=.05,
            taper=(.9, 1))
    zg = .46
    gap = .22
    ports = a.part('Gun_ports' + tag, 'Charred', m)
    for sx in (-gap, gap):
        ports.box((.2, .1, .34), loc=(sx, -1.0, zg + .02), rot=(.38, 0, 0), bevel=.02)
        fwd(a.part('Gun_sleeves' + tag, 'Armor', m), [(.11, 0), (.11, .16), (.09, .22)], (sx, -1.0, zg), seg=10)
        # Water-jacketed barrel, then the bare tube; the slotted brake on the kick part.
        fwd(a.part('Gun_barrels' + tag, 'Steel', m), [(.072, 0), (.072, 1.05), (.06, 1.1), (.045, 1.15), (.045, 2.12),
                                                      (0, 2.12)], (sx, -1.2, zg), seg=10)
        br = a.part('Gun_muzzles' + tag, 'Undercarriage', m)
        fwd(br, [(.05, 0), (.068, .02), (.068, .26), (.05, .28), (0, .28)], (sx, -3.3, zg), seg=10)
        for dy in (.07, .17):
            br.box((.15, .04, .03), loc=(sx, -3.3 - dy, zg), bevel=0)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, -3.6, zg), m)
    per_barrel(a, mz, f'gun{tag}', (-gap, gap))
    # The sight blister on the left of the roof, the rear hatch, the vent, the cartridge chute on the right.
    k.lathe(a.part('Gun_blister' + tag, 'Armor', m), [(0, -.2), (.18, -.16), (.22, 0), (.18, .16), (0, .2)],
            loc=(.55, -.35, .9), rot=K.FORWARD, seg=10)
    a.part('Glass', 'Glass', m).box((.16, .02, .1), loc=(.55, -.56, .9), bevel=0)
    k.block(a.part('Gun_hatch' + tag, 'Armor', m), (.5, .42, .08), loc=(-.25, .45, .96), rot=(.18, 0, 0), chamfer=.02)
    K.grille(a, (0, .97, .45), .5, .26, facing=(0, 1, 0), slats=3, parent=m, frame_mat='Armor')
    a.part('Gun_chute' + tag, 'Steel', m).limb((-.78, -.2, .35), (-.95, .0, .02), .14, .1, bevel=0)
    K.soot(a, (x, y - 3.4, z + pedestal + zg), radius=.4, k=.3)


def _ty_stern(a):
    """Part_rudder: the twin shafts in their bossings, the two seven-blade skewed screws in ring shrouds, the broad
    stern planes behind them with end fins, the upper rudder with the towed-array pod on its top, the lower rudder."""
    p = a.pivot('Part_rudder', (0, 26.0, .2))
    arm = a.part('Stern_fins', 'Armor', p)
    for s in (-1, 1):
        x = s * 2.45
        zc = -.55
        # The bossing from the hull side to the screw, the shroud, the hub and the blades.
        arm.loft([[(x * .55 + s * dx, -6.5, zc + dz) for dx, dz in ((.0, -.5), (.45, 0), (0, .5), (-.45, 0))],
                  [(x + s * dx, -1.0, zc + dz) for dx, dz in ((.0, -.3), (.3, 0), (0, .3), (-.3, 0))]])
        k.ring(a.part('Screw_shrouds', 'Armor', p), [(1.22, -.75), (1.42, -.65), (1.42, .55), (1.24, .7)],
               loc=(x, -.55, zc), rot=K.BACKWARD, seg=24)
        k.ring(a.part('Shroud_bands', 'Steel', p), [(1.425, -.3), (1.45, -.3), (1.45, -.1), (1.425, -.1)],
               loc=(x, -.55, zc), rot=K.BACKWARD, seg=24)
        aft(a.part('Screw_hubs', 'Gilded', p), [(0, -.55), (.32, -.4), (.36, .2), (.22, .55), (0, .7)], (x, -.55, zc),
            seg=12)
        bl = a.part('Screws', 'Gilded', p)
        for j in range(7):
            u = j * TAU / 7
            r = .7
            bl.box((.34, .05, .98), loc=(x + math.cos(u) * r, -.55, zc + math.sin(u) * r), rot=(.42, -u + R90, 0),
                   bevel=0, taper=(.55, 1), shift=(.08, 0))
        # The end fins of the stern planes.
        k.extrude(arm, [(-1.0, -.6), (1.0, -.4), (1.0, .4), (-1.0, .6)], .1, loc=(s * 6.38, 1.4, .15), axis='X',
                  chamfer=.02)
    # The stern planes behind the screws (the real boat's): one surface across the tail cone, out to the old span.
    k.extrude(arm, [(-1.2, -.08), (-.8, -.15), (.9, -.07), (1.1, 0), (.9, .07), (-.8, .15), (-1.2, .08)], 12.66,
              loc=(0, 1.35, .15), axis='X', chamfer=.03)
    aft(arm, [(.95, -1.3), (.9, .4), (.6, 1.7), (.25, 2.35), (0, 2.45)], (0, 0, .15), seg=16)
    # Upper rudder with the towed-array pod, the lower rudder (the hull's centreline fins).
    k.extrude(arm, [(-1.5, 0), (1.6, 0), (2.4, 3.4), (-.4, 4.0)], .2, loc=(0, 0, 1.0), axis='X', chamfer=.03)
    aft(a.part('Array_pod', 'Armor', p), [(0, -1.3), (.32, -1.05), (.42, -.5), (.42, 1.4), (.3, 1.8), (0, 1.95)],
        (0, 0, 5.15), seg=12)
    a.part('Array_pod_band', 'Team', p).cyl(.44, .3, loc=(0, -.3, 5.15), rot=K.FORWARD, seg=12, bevel=0)
    k.extrude(arm, [(-1.1, 0), (1.4, 0), (1.9, -2.9), (-.2, -3.1)], .18, loc=(0, 0, -.1), axis='X', chamfer=.03)
    a.part('Rudder_hinges', 'Steel', p).box((.24, .06, 3.4), loc=(0, 1.2, 2.6), bevel=0)
    K.tone(a, 'Part_rudder', k=.9)


def _ty_sonar(a):
    """Part_sonar: the bow's cylindrical array behind its rubber acoustic windows, the chin dome under the bow."""
    ps = a.pivot('Part_sonar', (0, -26.4, .8))
    win = a.part('Sonar_windows', 'Undercarriage', ps)
    px, py, pz = 0, -26.4, .8
    for s in (-1, 1):
        for z0, z1 in ((-1.3, -.1), (.15, 1.35)):
            rings = []
            for yy in (-27.75, -26.9, -26.0, -25.1):
                xa, xb = _ty_half(yy, z0), _ty_half(yy, z1)
                rings.append([(s * (xa + .005), yy - py, z0 - pz), (s * (xa + .05), yy - py, z0 - pz),
                              (s * (xb + .05), yy - py, z1 - pz), (s * (xb + .005), yy - py, z1 - pz)])
            win.loft(rings)
    k.lathe(a.part('Sonar_dome', 'Armor', ps), [(0, -1.4), (.9, -1.2), (1.35, -.4), (1.4, .8), (1.0, 1.7), (0, 2.0)],
            loc=(0, 0, -2.45), rot=K.FORWARD, seg=16)
    a.part('Sonar_band', 'Hazard', ps).cyl(1.42, .12, loc=(0, -.2, -2.45), rot=K.FORWARD, seg=16, bevel=0)
    K.tone(a, 'Part_sonar', k=.85)


def typhon(a):
    """Typhon, the missile submarine (module docstring). Runtime: Part_sail (Mount_missile > Muzzle_missile on its SAM
    mast), Part_doors_l / Part_doors_r (the launch doors), Part_rudder, Part_sonar, Mount_gun / .001 (twin 57 mm, fore
    and aft: Gun_barrels[_001] / Gun_muzzles[_001] kick parts, Muzzle_gun[.001] + per-barrel muzzles), Mount_gun.002
    (the 100 mm in its deck well, the deck_gun part: Dg_barrels / Dg_muzzles, Muzzle_gun.002), Point_fire."""
    K.suffixed(a)
    _ty_hull(a)
    _ty_deck(a)
    _ty_silo(a)
    _ty_sail(a)
    _ty_100(a)
    _ty_57(a, 0, TY_57F, 1.05)
    _ty_57(a, 1, TY_57A, .32)
    # Lane sea (after R4, owner: "typhon thêm 1 súng tương tự 2 súng kia ở đuôi"): the third twin 57 mm on the stern
    # casing (Mount_gun.003), drawn anew on its raised barbette; then the 941's black livery (mb_pt14_r5_sea).
    R5.ty_stern57(a, (0, TY_57S, _ty_top(TY_57S + 1.4), 3.35))
    _ty_stern(a)
    _ty_sonar(a)
    a.pivot('Point_fire', (0, 2.0, 5.5))
    R5.livery(a, 'typhon')
    k.clean(a)


# ============================================================================= kraken
def _tilted(z, h, rake, y):
    """A raked face's y at height z (the face leans back `rake` metres over the height h)."""
    return y + rake * z / h


def kr_main_turret(a, index, part_loc, mount_z, barbette_base=-.05):
    """A triple 406 mm in the MK-1 read (the Sovetsky Soyuz class's B-37 turret) under Part_gun[.NNN]: the barbette
    with its collar and bolt row; on Mount_gun[.NNN] the gunhouse with the raked face and the ROUNDED rear (not the
    Iowa's square box), the face plate with its bolt rows, three armoured port sleeves, the rangefinder built into the
    rear wall with its ear hoods proud of the sides, two periscope hoods and the commander's cupola kept out of the
    barrel lanes of a turret firing over it, roof vents, the hatch, the ladder; three long tapered barrels with the
    muzzle swell (Gun_barrels* / Gun_muzzles*, the kick parts), Muzzle_gun[.NNN] at the middle tip, per-barrel muzzles."""
    pname = K.name('Part_gun', index)
    tag = '' if index == 0 else f'_{index:03d}'
    p = a.pivot(pname, part_loc)
    px, py, pz = part_loc
    lz = mount_z - pz
    br = 3.5
    bar = a.part('Gun_barbette' + tag, 'Armor', p)
    k.lathe(bar, [(br, barbette_base), (br, lz - .32), (br + .08, lz - .26), (br + .08, lz - .1), (br - .04, lz - .04),
                  (br - .04, lz)], seg=32)
    bolts = a.part('Kit_bolts', 'Steel', p)
    for i in range(30):
        u = (i + .5) * TAU / 30
        bolts.cyl(.05, .05, loc=(math.cos(u) * (br + .09), math.sin(u) * (br + .09), lz - .18), rot=(0, R90, u), seg=6,
                  bevel=0)
    m = a.pivot(K.name('Mount_gun', index), (0, 0, lz), p)
    k.ring(a.part('Gun_ring' + tag, 'Steel', m), [(br - .22, -.04), (br - .12, -.04), (br - .12, .1), (br - .22, .1)],
           seg=32)
    H, rake = 2.65, .95
    arc = [(3.2, 3.15), (2.75, 3.8), (2.0, 4.28), (1.05, 4.56), (0, 4.65)]
    plan = [(-2.45, -3.3), (2.45, -3.3), (3.15, -2.6), (3.35, -1.7), (3.35, 2.35)] + arc + \
        [(-x, y) for x, y in reversed(arc[:-1])] + [(-3.35, 2.35), (-3.35, -1.7), (-3.15, -2.6)]

    def ring_at(z):
        f = z / H
        out = []
        for x, y in plan:
            if y < -1.0:
                yy = _tilted(z, H, rake, y)
            elif y > 2.3:
                yy = y * (1 - .03 * f)
            else:
                yy = y
            out.append((x * (1 - .04 * f), yy, z))
        return out
    k.sharp_loft(a.part('Gun_house' + tag, 'Team', m), [ring_at(0), ring_at(H * .5), ring_at(H)], chamfer=.08)
    tilt = math.atan2(rake, H)
    face = a.part('Gun_face' + tag, 'Armor', m)
    k.block(face, (4.7, .18, H - .12), loc=(0, -3.3 + rake / 2 - .07, H / 2 - .04), rot=(-tilt, 0, 0), chamfer=.05,
            taper=(.95, 1), ends=(True, True))
    zg, gap = 1.28, 1.75
    xs = (-gap, 0, gap)
    yf = _tilted(zg, H, rake, -3.3) - .17
    bolts_m = a.part('Kit_bolts', 'Steel', m)
    for zb in (.3, H - .35):
        for i in range(14):
            x = -2.1 + i * .323
            bolts_m.cyl(.035, .03, loc=(x, _tilted(zb, H, rake, -3.3) - .17, zb), rot=(R90 - tilt, 0, 0), seg=6,
                        bevel=0)
    slots = a.part('Gun_ports' + tag, 'Charred', m)
    for x in xs:
        slots.box((.6, .12, 1.25), loc=(x, yf - .02, zg + .2), rot=(-tilt, 0, 0), bevel=.02)
        fwd(a.part('Gun_sleeves' + tag, 'Armor', m), [(.58, 0), (.6, .1), (.6, .42), (.5, .55), (.4, .58)],
            (x, yf + .05, zg), seg=16)
    # The rangefinder in the rear wall, its ears proud of the sides with their hoods and glass.
    rfz, rfy = 1.85, 2.0
    along_x(a.part('Gun_rangefinder' + tag, 'Armor', m), [(0, -4.25), (.3, -4.25), (.34, -4.05), (.34, 4.05),
                                                          (.3, 4.25), (0, 4.25)], (0, rfy, rfz), seg=14)
    for sx in (-1, 1):
        k.block(a.part('Gun_hoods' + tag, 'Armor', m), (.55, .9, .78), loc=(sx * 4.0, rfy - .05, rfz - .38),
                chamfer=.06, taper=(.85, .8))
        a.part('Glass', 'Glass', m).box((.3, .03, .16), loc=(sx * 4.0, rfy - .52, rfz + .08), bevel=0)
    # Roof: plates and seams, the hoods and the cupola out of the lanes (x 0, +-1.75), vents, the hatch, the bands.
    roof = a.part('Gun_roof' + tag, 'Armor', m)
    top = [(x * .9, y * .9 + .2) for x, y, _ in ring_at(H)]
    k.extrude(roof, top, .07, loc=(0, 0, H + .035), axis='Z', chamfer=.025)
    for y in (-.6, 1.4, 3.2):
        a.part('Gun_roof_seams' + tag, 'Steel', m).box((5.4, .05, .025), loc=(0, y, H + .08), bevel=0)
    hoods = a.part('Gun_hoods' + tag, 'Armor', m)
    for sx in (-1, 1):
        k.extrude(hoods, [(-.3, -.5), (.3, -.5), (.3, .5), (-.3, .5)], .45, loc=(sx * 2.62, -1.4, H + .22), axis='Z',
                  chamfer=.04, taper=(1, .55))
        a.part('Glass', 'Glass', m).box((.42, .02, .12), loc=(sx * 2.62, -1.78, H + .24), rot=(-.45, 0, 0), bevel=0)
    k.lathe(a.part('Gun_cupola' + tag, 'Armor', m), [(.42, 0), (.42, .3), (.34, .4), (.16, .46), (0, .47)],
            loc=(-.875, 1.0, H + .07), seg=16)
    for j in range(5):
        u = -R90 + (j - 2) * .55
        a.part('Gun_periscopes' + tag, 'Steel', m).box((.1, .1, .12), loc=(-.875 + math.cos(u) * .35,
                                                                        1.0 + math.sin(u) * .35, H + .4),
                                                       rot=(0, 0, u), bevel=0)
    vents = a.part('Gun_vents' + tag, 'Steel', m)
    for x in (-2.55, 2.55):
        k.lathe(vents, [(.17, 0), (.17, .3), (.3, .34), (.3, .44), (0, .48)], loc=(x, 3.2, H * .97), seg=10)
    k.block(a.part('Gun_hatch' + tag, 'Armor', m), (.6, .75, .09), loc=(.875, 2.3, H + .07), chamfer=.02)
    band = a.part('Team_band', 'Team', m)
    band.box((.5, 3.2, .02), loc=(.875, -.2, H + .075), bevel=0)
    band.box((.5, 3.2, .02), loc=(-.875, -1.2, H + .075), bevel=0)
    K.ladder(a.part('Ladders', 'Steel', m), (-3.38, .9, .15), (-3.38, .9, H - .1), width=.45, step=.32,
             facing=(-1, 0))
    # Barrels: the B-37's long taper with the muzzle swell; the kick parts.
    y0 = yf - .1
    L = 9.6
    for x in xs:
        fwd(a.part('Gun_barrels' + tag, 'Steel', m), [(.33, 0), (.33, .55), (.29, .62), (.27, 1.3), (.215, 8.8),
                                                      (.235, 9.15), (.23, L), (0, L)], (x, y0, zg), seg=14)
        fwd(a.part('Gun_muzzles' + tag, 'Undercarriage', m), [(.2, 0), (.245, .03), (.245, .32), (.19, .36), (0, .36)],
            (x, y0 - L + .02, zg), seg=14)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .36, zg), m)
    per_barrel(a, mz, f'gun_{index:03d}' if index else 'gun', xs)
    K.soot(a, (px, py + y0 - L, mount_z + zg), radius=1.1, k=.4)
    K.tone(a, pname, k=.92)
    return m


def kr_sec_turret(a, index, pname, part_loc, mount_z, depth=1.55, base=-1.1, tub=False):
    """A triple 152 mm in the MK-5 read (the Chapayev / Sverdlov B-38 turret) that sleeps in a well until its phase
    (VehicleView.WakeMounts lowers the gunhouse): the well (a hollow barbette, its dark floor, the hatch leaves folded
    open fore and aft); on Mount_gun.NNN the small sloped-front house with the square rear and its overhang, the roof
    rangefinder across the rear with ear hoods, the front-left sight hood, three barrels with plain muzzles
    (Sec_barrels_NNN / Sec_muzzles_NNN), per-barrel muzzles. `tub`: the well hangs off the hull side as a sponson tub
    on its braces."""
    tag = f'_{index:03d}'
    p = a.pivot(pname, part_loc)
    px, py, pz = part_loc
    seat = mount_z - pz
    outer, inner = 2.12, 1.9
    wall = a.part('Sec_well' + tag, 'Armor', p)
    k.lathe(wall, [(outer, base), (outer, seat - .14), (outer - .06, seat), (inner, seat), (inner, seat - depth),
                   (0, seat - depth)], seg=32)
    a.part('Sec_well_floor' + tag, 'Charred', p).cyl(inner - .02, .03, loc=(0, 0, max(seat - depth, .0) + .03),
                                                     seg=28, bevel=0)
    k.ring(a.part('Sec_well_lip' + tag, 'Hazard', p), [(inner + .02, seat + .005), (outer - .08, seat + .005),
                                                       (outer - .08, seat + .02), (inner + .02, seat + .02)], seg=32)
    leaves = a.part('Sec_well_doors' + tag, 'Team', p)
    hinge = a.part('Kit_hinges', 'Steel', p)
    for sy in (-1, 1):
        # Half-disc leaves hinged on the lip fore and aft, swung open and leaning out.
        prof = [(inner * .9 * math.cos(u), inner * .9 * math.sin(u)) for u in (i * math.pi / 10 for i in range(11))]
        k.extrude(leaves, prof, .08, loc=(0, sy * (outer + .1), seat), rot=(sy * .15, 0, 0), axis='Y', chamfer=.02)
        hinge.cyl(.06, inner * 1.5, loc=(0, sy * (outer + .03), seat + .02), rot=(0, R90, 0), seg=8, bevel=0)
    if tub:
        inboard = 1.0 if px < 0 else -1.0
        for dy in (-1.2, 1.2):
            a.part('Sec_braces' + tag, 'Armor', p).limb((inboard * 1.9, dy, base - 1.4), (inboard * .3, dy * .9, base),
                                                        .25, .25, bevel=0)
    m = a.pivot(K.name('Mount_gun', index), (0, 0, seat), p)
    k.ring(a.part('Sec_ring' + tag, 'Steel', m), [(1.66, -.02), (1.74, -.02), (1.74, .06), (1.66, .08)], seg=24)
    H, rake = 1.22, .55
    plan = [(-1.0, -1.3), (1.0, -1.3), (1.25, -.95), (1.25, 1.25), (1.1, 1.4), (-1.1, 1.4), (-1.25, 1.25),
            (-1.25, -.95)]

    def ring_at(z):
        return [(x * (1 - .05 * z / H), _tilted(z, H, rake, y) if y < 0 else y + .1 * z / H, z) for x, y in plan]
    k.sharp_loft(a.part('Sec_house' + tag, 'Team', m), [ring_at(0), ring_at(H * .45), ring_at(H)], chamfer=.05)
    tilt = math.atan2(rake, H)
    zg = .62
    gap = .52
    xs = (-gap, 0, gap)
    yf = _tilted(zg, H, rake, -1.3) - .06
    face = a.part('Sec_face' + tag, 'Armor', m)
    for x in xs:
        k.block(face, (.36, .12, .62), loc=(x, yf, zg - .05), rot=(-tilt, 0, 0), chamfer=.03, ends=(True, True))
    k.block(a.part('Sec_overhang' + tag, 'Armor', m), (2.3, .3, .2), loc=(0, 1.55, H * .55), chamfer=.03)
    along_x(a.part('Sec_rangefinder' + tag, 'Armor', m), [(0, -1.75), (.15, -1.75), (.17, -1.6), (.17, 1.6),
                                                          (.15, 1.75), (0, 1.75)], (0, .85, H + .16), seg=10)
    for sx in (-1, 1):
        k.block(a.part('Sec_hoods' + tag, 'Armor', m), (.24, .4, .36), loc=(sx * 1.72, .85, H - .02), chamfer=.03)
        a.part('Glass', 'Glass', m).box((.12, .02, .08), loc=(sx * 1.72, .64, H + .2), bevel=0)
    k.block(a.part('Sec_hoods' + tag, 'Armor', m), (.36, .45, .24), loc=(-.72, -.35, H - .02), chamfer=.03,
            taper=(.9, .7))
    a.part('Glass', 'Glass', m).box((.24, .02, .08), loc=(-.72, -.6, H + .12), bevel=0)
    k.block(a.part('Sec_hatch' + tag, 'Armor', m), (.42, .4, .06), loc=(.6, .4, H - .01), chamfer=.015)
    L = 5.85
    y0 = yf - .05
    for x in xs:
        fwd(a.part('Sec_barrels' + tag, 'Steel', m), [(.13, 0), (.13, .3), (.105, .36), (.085, 5.5), (.092, L),
                                                      (0, L)], (x, y0, zg), seg=10)
        fwd(a.part('Sec_muzzles' + tag, 'Undercarriage', m), [(.088, 0), (.1, .03), (.1, .2), (0, .22)],
            (x, y0 - L + .02, zg), seg=10)
    mz = a.pivot(K.name('Muzzle_gun', index), (0, y0 - L - .22, zg), m)
    per_barrel(a, mz, f'gun_{index:03d}', xs)
    K.soot(a, (px, py + y0 - L, mount_z + zg), radius=.5, k=.35)
    K.tone(a, pname, k=.92)
    return m


def kr_twin127(a, pname, mount, muzzle, ploc, tag, mtag):
    """A twin 127 mm in the AK-726 read (the Kiev's rounded twin), under its part pivot: the base ring, the drum
    gunhouse with the domed roof and the flat raked front, two barrels with multi-baffle brakes (Dp_barrels /
    Dp_muzzles, the kick parts), the sight blister, the rear door and vent; Muzzle_mg[.NNN] + per-barrel muzzles."""
    p = a.pivot(pname, ploc)
    k.lathe(a.part('Dp_base' + tag, 'Armor', p), [(1.42, -.1), (1.42, .1), (1.32, .16)], seg=24)
    m = a.pivot(mount, (0, 0, .16), p)
    k.ring(a.part('Dp_ring' + tag, 'Steel', m), [(1.24, -.02), (1.3, -.02), (1.3, .08), (1.24, .1)], seg=24)
    k.lathe(a.part('Dp_house' + tag, 'Team', m), [(1.22, 0), (1.25, .1), (1.25, .95), (1.12, 1.24), (.8, 1.44),
                                                  (.35, 1.52), (0, 1.53)], seg=24, worn=(2,))
    k.block(a.part('Dp_face' + tag, 'Armor', m), (1.85, .45, 1.3), loc=(0, -1.05, .05), rot=(.3, 0, 0), chamfer=.06,
            taper=(.92, 1))
    zg, gap = .66, .34
    for x in (-gap, gap):
        a.part('Dp_ports' + tag, 'Charred', m).box((.28, .1, .5), loc=(x, -1.25, zg + .06), rot=(.3, 0, 0), bevel=.02)
        fwd(a.part('Dp_sleeves' + tag, 'Armor', m), [(.17, 0), (.17, .2), (.13, .28)], (x, -1.22, zg), seg=10)
        fwd(a.part('Dp_barrels' + tag, 'Steel', m), [(.12, 0), (.12, .3), (.095, .38), (.075, 3.9), (.08, 4.1),
                                                     (0, 4.1)], (x, -1.48, zg), seg=10)
        br = a.part('Dp_muzzles' + tag, 'Undercarriage', m)
        fwd(br, [(.08, 0), (.12, .03), (.12, .38), (.085, .42), (0, .42)], (x, -5.55, zg), seg=10)
        for dy in (.1, .22):
            br.box((.26, .05, .05), loc=(x, -5.55 - dy, zg), bevel=0)
    mz = a.pivot(muzzle, (0, -6.0, zg), m)
    per_barrel(a, mz, mtag, (-gap, gap))
    k.lathe(a.part('Dp_blister' + tag, 'Armor', m), [(0, -.24), (.2, -.2), (.25, 0), (.2, .2), (0, .24)],
            loc=(.62, -.45, 1.3), rot=K.FORWARD, seg=10)
    a.part('Glass', 'Glass', m).box((.18, .02, .1), loc=(.62, -.7, 1.3), bevel=0)
    K.door(a, (0, 1.24, .1), size=(.6, .9), normal=(0, 1, 0), parent=m, mat='Armor', frame_mat='Steel')
    k.lathe(a.part('Dp_vent' + tag, 'Steel', m), [(.14, 0), (.14, .22), (.22, .26), (.22, .34), (0, .37)],
            loc=(-.5, .6, 1.38), seg=8)
    K.tone(a, pname, k=.9)


def kr_kashtan(a, mount, muzzle, loc, parent, tag):
    """A Kashtan-style gun / missile module on Mount_mg.NNN (Kraken's gun galleries): the drum base, the central body
    with its EO director, two six-barrel 30 mm guns either side (the barrel clusters with their clamps and muzzle
    rings), the missile container pack over each gun (four tubes, caps dark), the flat tracking antenna on its mast
    behind; Muzzle_mg.NNN between the gun tips."""
    m = a.pivot(mount, loc, parent)
    k.lathe(a.part('Kash_base' + tag, 'Armor', m), [(.66, -.25), (.66, .12), (.58, .2), (.5, .32)], seg=16)
    body = a.part('Kash_body' + tag, 'Team', m)
    k.block(body, (.78, 1.0, .62), loc=(0, .05, .3), chamfer=.06, taper=(.88, .9))
    k.block(a.part('Kash_eo' + tag, 'Armor', m), (.36, .34, .3), loc=(0, -.4, .9), chamfer=.04)
    a.part('Glass', 'Glass', m).box((.22, .02, .12), loc=(0, -.575, .96), bevel=0)
    zg = .62
    g = a.part('Kash_guns' + tag, 'Steel', m)
    for sx in (-1, 1):
        x = sx * .58
        k.block(a.part('Kash_cradles' + tag, 'Armor', m), (.3, .95, .3), loc=(x, .02, zg - .15), chamfer=.03)
        for i in range(6):
            u = i * TAU / 6
            g.cyl(.022, 1.2, loc=(x + math.cos(u) * .055, -1.05, zg + math.sin(u) * .055), rot=K.FORWARD, seg=5,
                  bevel=0)
        for yy in (-.55, -1.6):
            g.cyl(.095, .06, loc=(x, yy, zg), rot=K.FORWARD, seg=10, bevel=0)
        fwd(a.part('Kash_tips' + tag, 'Undercarriage', m), [(.09, 0), (.1, .03), (.1, .12), (0, .14)],
            (x, -1.62, zg), seg=10)
        pk = a.part('Kash_packs' + tag, 'Armor', m)
        k.block(pk, (.34, 1.1, .4), loc=(x, .05, zg + .22), chamfer=.03)
        for dx in (-.08, .08):
            for dz in (.1, .27):
                a.part('Kash_caps' + tag, 'Charred', m).cyl(.065, .02, loc=(x + dx, -.505, zg + .22 + dz),
                                                            rot=K.FORWARD, seg=8, bevel=0)
    a.part('Kash_mast' + tag, 'Steel', m).cyl(.05, .55, loc=(0, .45, .85), seg=6, bevel=0)
    k.block(a.part('Kash_antenna' + tag, 'Armor', m), (.62, .1, .44), loc=(0, .42, 1.15), rot=(-.25, 0, 0),
            chamfer=.02, ends=(True, True))
    a.part('Kash_antenna_face' + tag, 'Undercarriage', m).box((.54, .02, .36), loc=(0, .36, 1.31), rot=(-.25, 0, 0),
                                                              bevel=0)
    a.pivot(muzzle, (0, -1.76, zg), m)
    return m


def kr_duet(a, loc, parent=None, s=1.0):
    """An AK-630M-2 "Duet"-style close-in mount (decoration: the APS's guns): the low ring base, the faceted stealth
    house wider at the bottom, two six-barrel guns one over the other in their slots with the muzzle clamps."""
    x, y, z = loc
    k.lathe(a.part('Duet_base', 'Armor', parent), [(.75 * s, 0), (.72 * s, .2 * s), (.62 * s, .26 * s)], loc=loc,
            seg=16)
    house = a.part('Duet_house', 'Team', parent)
    b = [(-.55, -.6), (.55, -.6), (.7, -.2), (.7, .6), (-.7, .6), (-.7, -.2)]
    t = [(-.4, -.38), (.4, -.38), (.52, -.08), (.52, .48), (-.52, .48), (-.52, -.08)]
    k.sharp_loft(house, [[(x + px * s, y + py * s, z + .25 * s) for px, py in b],
                         [(x + px * s, y + py * s, z + 1.15 * s) for px, py in t]], chamfer=.04 * s)
    g = a.part('Duet_guns', 'Steel', parent)
    for zz in (.5, .86):
        a.part('Duet_slots', 'Charred', parent).box((.3 * s, .08 * s, .26 * s),
                                                    loc=(x, y - .58 * s + (zz - .25) * .25 * s, z + zz * s),
                                                    rot=(-.28, 0, 0), bevel=0)
        for i in range(6):
            u = i * TAU / 6
            g.cyl(.018 * s, 1.0 * s, loc=(x + math.cos(u) * .05 * s, y - 1.0 * s, z + zz * s + math.sin(u) * .05 * s),
                  rot=K.FORWARD, seg=5, bevel=0)
        for yy in (-.7, -1.42):
            g.cyl(.075 * s, .05 * s, loc=(x, y + yy * s, z + zz * s), rot=K.FORWARD, seg=10, bevel=0)


def kr_shtorm(a, loc):
    """A Shtorm-style twin-arm SAM launcher (the Kiev's) on Mount_missile: the deck ring and the magazine hatch behind,
    the tall trainable drum with its domed top, the trunnion housing, two box-girder arms with lightening holes and
    blast plates, a V-611-type missile riding each arm (the long cruciform mid wings, the tail fins, the ogive nose,
    the red band); Muzzle_missile at the left missile's nose."""
    x, y, z = loc
    k.lathe(a.part('Sam_deck', 'Armor'), [(1.45, -.3), (1.45, 0), (1.32, .06)], loc=loc, seg=24)
    k.block(a.part('Sam_hatch', 'Armor'), (1.4, 1.0, .08), loc=(x, y + 2.0, z), chamfer=.02)
    for yy in (1.46, 2.54):
        a.part('Sam_hatch', 'Hazard').box((1.5, .08, .02), loc=(x, y + yy, z + .07), bevel=0)
    m = a.pivot('Mount_missile', (x, y, z + .06))
    k.lathe(a.part('Sam_drum', 'Team', m), [(1.08, 0), (1.08, .62), (1.0, .78), (.72, .92), (0, .96)], seg=20)
    k.block(a.part('Sam_trunnion', 'Armor', m), (1.95, .9, .6), loc=(0, .1, .9), chamfer=.06)
    arms = a.part('Sam_arms', 'Steel', m)
    holes = a.part('Sam_holes', 'Charred', m)
    msl = a.part('Sam_missiles', 'PlasterWhite', m)
    fins = a.part('Sam_fins', 'Steel', m)
    nose = a.part('Sam_noses', 'Armor', m)
    el = .14
    d = Vector((0, -math.cos(el), math.sin(el)))
    for sx in (-1, 1):
        ax = sx * .82
        arms.box((.22, 3.0, .32), loc=(ax, -.65, 1.42), rot=(el, 0, 0), bevel=.02)
        for j in range(4):
            yy = -1.7 + j * .62
            holes.box((.24, .3, .14), loc=(ax, yy, 1.42 - (yy + .65) * math.tan(el)), rot=(el, 0, 0), bevel=0)
        k.block(a.part('Sam_blast', 'Armor', m), (.5, .08, .55), loc=(ax, .95, 1.25), chamfer=.015)
        tail = Vector((ax, .75, 1.82))
        k.lathe(msl, [(0, 0), (.16, .02), (.18, .12), (.18, 2.6), (.15, 3.05), (.1, 3.3)], loc=tuple(tail),
                rot=(R90 - el, 0, 0), seg=12)
        k.lathe(nose, [(.1, 3.3), (.06, 3.55), (0, 3.7)], loc=tuple(tail), rot=(R90 - el, 0, 0), seg=12)
        a.part('Sam_bands', 'BarrelRed', m).cyl(.185, .12, loc=tuple(tail + d * 2.3), rot=(R90 - el, 0, 0), seg=12,
                                                bevel=0)
        for j in range(4):
            u = j * R90 + math.pi / 4
            c, sn = math.cos(u), math.sin(u)
            for along, chord, span in ((1.55, 1.3, .48), (.25, .5, .3)):
                pc = tail + d * along
                fins.box((.02, chord, span), loc=(pc.x + c * (.18 + span / 2), pc.y, pc.z + sn * (.18 + span / 2)),
                         rot=(el, R90 - u, 0), bevel=0)
    tip = Vector((.82, .75, 1.82)) + d * 3.72
    a.pivot('Muzzle_missile', tuple(tip), m)
    return m


def kr_director(a, loc, tag=''):
    """An Owl Screech-style gun director: the pedestal, the rounded director house, the elevating yoke with the big
    dish (its rim, the feed on three struts), the TV / laser box on its side, the cable trunk."""
    x, y, z = loc
    k.lathe(a.part('Dir_base' + tag, 'Armor'), [(.55, 0), (.55, .45), (.65, .52), (.62, .58)], loc=loc, seg=14)
    k.block(a.part('Dir_house' + tag, 'Team'), (1.3, 1.15, .78), loc=(x, y + .1, z + .58), chamfer=.12, taper=(.9, .9))
    yk = a.part('Dir_yoke' + tag, 'Steel')
    for sx in (-1, 1):
        yk.box((.12, .4, .7), loc=(x + sx * .72, y - .1, z + 1.55), bevel=.02)
    yk.cyl(.07, 1.5, loc=(x, y - .1, z + 1.75), rot=(0, R90, 0), seg=8, bevel=0)
    dc = Vector((x, y - .4, z + 1.75))
    tilt = .3
    rot = (R90 + tilt, 0, 0)
    k.lathe(a.part('Dir_dish' + tag, 'PlasterWhite'), [(0, 0), (.3, .02), (.55, .08), (.78, .19), (.82, .21),
                                                      (.8, .24)], loc=tuple(dc), rot=rot, seg=18, caps=(False, True))
    d = Vector((0, -math.cos(tilt), math.sin(tilt)))
    up = Vector((0, math.sin(tilt), math.cos(tilt)))
    tip = dc + d * .62
    feed = a.part('Dir_feed' + tag, 'Steel')
    feed.cyl(.06, .14, loc=tuple(tip), rot=rot, seg=8, bevel=0)
    for i in range(3):
        u = i * TAU / 3
        e1 = Vector((math.cos(u), 0, 0)) + up * math.sin(u)
        feed.tube([tuple(dc + e1 * .72 + d * .2), tuple(tip)], .015, seg=4)
    k.block(a.part('Dir_tv' + tag, 'Armor'), (.32, .55, .3), loc=(x - .95, y - .25, z + 1.3), chamfer=.03)
    a.part('Glass', 'Glass').box((.2, .02, .14), loc=(x - .95, y - .53, z + 1.33), bevel=0)
    a.part('Dir_trunk' + tag, 'Rubber').tube([(x + .3, y + .65, z + .3), (x + .35, y + .9, z + .05)], .07, seg=6)


def kr_topsail(a, loc, parent):
    """A Top Sail-style 3D search radar on its own `Radar` pivot: the turntable drive, the large cylindrical-section
    reflector (curved top to bottom) with its back framing, the line feed across its focus on two arms, the IFF bar."""
    r = a.pivot('Radar', loc, parent)
    a.part('Radar_drive', 'Steel', r).cyl(.34, .3, loc=(0, 0, .15), seg=12, bevel=0)
    a.part('Topsail_base', 'Armor', r).cyl(.5, .1, loc=(0, 0, .05), seg=12, bevel=0)
    R, cz = 1.3, .82
    arc = [math.radians(v) for v in (-24, -12, 0, 12, 24)]
    prof = [(R * math.cos(u) - 1.05, cz + R * math.sin(u)) for u in arc]
    prof_b = [(y + .07, z) for y, z in reversed(prof)]
    k.extrude(a.part('Radar_reflector', 'PlasterWhite', r), prof + prof_b, 4.4, loc=(0, 0, 0), axis='X', chamfer=.03)
    back = a.part('Radar_frame', 'Steel', r)
    for xx in (-2.0, -1.0, 0, 1.0, 2.0):
        back.tube([(xx, prof[0][0] + .1, prof[0][1]), (xx, .55, cz), (xx, prof[-1][0] + .1, prof[-1][1])], .03, seg=4)
    back.tube([(-2.1, .55, cz), (2.1, .55, cz)], .04, seg=4)
    back.limb((0, .1, .3), (0, .55, cz), .16, .16, bevel=0)
    fy = R * math.cos(0) - 1.05 - R / 2
    a.part('Radar_feed', 'Armor', r).box((4.0, .12, .12), loc=(0, fy, cz), bevel=0)
    for xx in (-1.6, 1.6):
        back.tube([(xx, prof[2][0] - .02, cz - .3), (xx, fy, cz - .02)], .025, seg=4)
    a.part('Radar_iff', 'Armor', r).box((2.6, .1, .14), loc=(0, .45, cz + .47), bevel=0)
    return r


def kr_granit(a, pv):
    """The flush anti-ship missile hatches on Part_vls (the Kuznetsov's Granit cells forward of the flight deck): the
    raised armoured panel, three rows of four round hatches, each with its rim, painted ring, hinge block and locking
    dogs; the panel's hazard border."""
    k.block(a.part('Vls_coaming', 'Armor', pv), (6.4, 3.0, .26), loc=(0, 0, .1), chamfer=.04)
    rim = a.part('Vls_rims', 'Steel', pv)
    lid = a.part('Vls_lids', 'Team', pv)
    ring_ = a.part('Vls_rings', 'Hazard', pv)
    hinge = a.part('Vls_hinges', 'Steel', pv)
    for i in range(4):
        for j in range(3):
            x, y = -2.4 + i * 1.6, -1.0 + j * 1.0
            k.ring(rim, [(.4, .34), (.46, .34), (.46, .39), (.4, .39)], loc=(x, y, 0), seg=16)
            k.lathe(lid, [(.4, .34), (.4, .38), (.33, .41), (0, .42)], loc=(x, y, 0), seg=16)
            k.ring(ring_, [(.28, .412), (.33, .412), (.33, .418), (.28, .418)], loc=(x, y, 0), seg=16)
            hinge.box((.16, .3, .1), loc=(x + .46, y, .39), bevel=0)
            for u in (math.pi * .75, math.pi * 1.25):
                hinge.box((.07, .07, .05), loc=(x + math.cos(u) * .43, y + math.sin(u) * .43, .39), bevel=0)
    for yy in (-1.48, 1.48):
        a.part('Vls_band', 'Hazard', pv).box((6.2, .1, .02), loc=(0, yy, .36), bevel=0)
    K.tone(a, 'Part_vls', k=.88)


def _xf(loc, yaw, s):
    x, y, z = loc
    c, sn = math.cos(yaw), math.sin(yaw)

    def at(px, py, pz):
        return (x + (px * c - py * sn) * s, y + (px * sn + py * c) * s, z + pz * s)
    return at


def kr_ka31(a, loc, yaw, s=.55, parent=None):
    """A Ka-31-style radar picket helicopter, parked with its blades folded aft: the deep fuselage with the glazed
    nose, the twin engine nacelles, the coaxial rotor heads with the blades folded along the tail, the tail boom with
    its twin fins and tailplane, the four-wheel gear, the big flat radar antenna folded flat under the belly."""
    at = _xf(loc, yaw, s)
    body = a.part('Ka31_body', 'Team', parent)
    st = [(-5.6, .5, 1.3, 2.2), (-5.0, 1.0, 1.0, 2.9), (-3.8, 1.25, .9, 3.4), (-1.0, 1.3, .9, 3.6),
          (2.4, 1.25, .95, 3.5), (3.6, .9, 1.4, 3.1)]
    rings = []
    for py, w, z0, z1 in st:
        rings.append([at(-w * .8, py, z0), at(w * .8, py, z0), at(w, py, (z0 + z1) * .5), at(w * .8, py, z1),
                      at(-w * .8, py, z1), at(-w, py, (z0 + z1) * .5)])
    body.loft(rings)
    a.part('Ka31_boom', 'Team', parent).loft(
        [[at(-.45, 3.5, 2.2), at(.45, 3.5, 2.2), at(.45, 3.5, 3.0), at(-.45, 3.5, 3.0)],
         [at(-.25, 8.6, 2.6), at(.25, 8.6, 2.6), at(.25, 8.6, 3.0), at(-.25, 8.6, 3.0)]])
    a.part('Ka31_glass', 'Glass', parent).loft(
        [[at(-.7, -5.45, 1.9), at(.7, -5.45, 1.9), at(.75, -5.1, 2.3), at(.6, -4.6, 2.95), at(-.6, -4.6, 2.95),
          at(-.75, -5.1, 2.3)],
         [at(-.8, -5.0, 1.9), at(.8, -5.0, 1.9), at(.95, -4.0, 2.3), at(.85, -3.8, 3.3), at(-.85, -3.8, 3.3),
          at(-.95, -4.0, 2.3)]])
    nac = a.part('Ka31_engines', 'Armor', parent)
    for sx in (-1, 1):
        nac.loft([[at(sx * .55 + dx, py, 3.5 + dz) for dx, dz in ((-.4, 0), (.4, 0), (.4, .65), (-.4, .65))]
                  for py in (-2.6, 1.4)])
        a.part('Ka31_intakes', 'Charred', parent).box((.6 * s, .05, .5 * s), loc=at(sx * .55, -2.63, 3.82),
                                                      rot=(0, 0, yaw), bevel=0)
    k.lathe(a.part('Ka31_hub', 'Steel', parent), [(.5 * s, 0), (.5 * s, .5 * s), (.3 * s, .6 * s), (.3 * s, 1.6 * s),
                                                   (.45 * s, 1.7 * s), (.2 * s, 2.0 * s), (0, 2.05 * s)],
            loc=at(0, -.4, 4.1), seg=10)
    blades = a.part('Ka31_blades', 'Armor', parent)
    for zz in (4.75, 5.55):
        for j in range(3):
            o = (j - 1) * .18
            blades.limb(at(o, -.4, zz), at(o * 3, 8.0, zz - .3), .3 * s, .06 * s, bevel=0)
    fin = a.part('Ka31_fins', 'Team', parent)
    fin.box((3.2 * s, .9 * s, .12 * s), loc=at(0, 8.4, 2.9), rot=(0, 0, yaw), bevel=0)
    for sx in (-1, 1):
        fin.box((.1 * s, 1.0 * s, 1.6 * s), loc=at(sx * 1.6, 8.4, 3.2), rot=(0, 0, yaw), bevel=0)
    a.part('Ka31_radar', 'Armor', parent).box((1.8 * s, 5.6 * s, .12 * s), loc=at(0, -.6, .82), rot=(0, 0, yaw),
                                              bevel=0)
    a.part('Ka31_radar_face', 'Undercarriage', parent).box((1.6 * s, 5.4 * s, .02), loc=at(0, -.6, .74),
                                                            rot=(0, 0, yaw), bevel=0)
    gear = a.part('Ka31_wheels', 'Rubber', parent)
    for px, py in ((-.9, -3.4), (.9, -3.4), (-1.5, 1.3), (1.5, 1.3)):
        gear.cyl(.32 * s, .22 * s, loc=at(px, py, .32), rot=(0, R90, yaw), seg=8, bevel=0)
        a.part('Ka31_struts', 'Steel', parent).limb(at(px, py, .32), at(px * .7, py, 1.1), .1 * s, .1 * s, bevel=0)


# The A-12 Avenger II (the stealth_naval_strike the kraken_jets skill launches): real half span and length.
A12_T, A12_L = 10.7, 11.4


def _a12_le(x):
    """The leading edge's y at span station x (the 45-48 degree sweep), local, nose at -L/2."""
    return -A12_L / 2 + abs(x) * (A12_L - .8) / A12_T


def _a12_section(x, at, fold=None):
    """One airfoil section of the wing at span x (upper surface, trailing edge, lower surface); fold = (hinge x,
    angle) turns an outer panel up about its fold line."""
    le = _a12_le(x)
    te = A12_L / 2
    c = te - le
    t = max(.05, .085 * c)
    up = [(0, 0), (.08, .55), (.3, 1.0), (.62, .72), (1.0, .06)]
    lo = [(1.0, -.04), (.62, -.32), (.3, -.45), (.08, -.28)]
    pts = []
    for u, f in up + lo:
        px, py, pz = x, le + c * u, t * f
        if fold is not None:
            hx, ang = fold
            sgn = 1 if x > 0 else -1
            d = abs(x) - hx
            px = sgn * (hx + d * math.cos(ang) - pz * math.sin(ang))
            pz = d * math.sin(ang) + pz * math.cos(ang)
        pts.append(at(px, py, pz + 1.15))
    return pts


def kr_a12(a, loc, yaw, tag='', parent=None, s=.45, folded=False, launch=False):
    """An A-12-type carrier flying wing (Kraken's strike jets, the type it launches): the triangular wing lofted from
    airfoil sections (its outer panels folded up when parked), the crew hump and the tandem canopy, the dark leading
    edge, the exhaust troughs on the upper trailing edge, the tricycle gear; `launch`: wings spread, the nose-gear
    launch bar down to the catapult shuttle."""
    at = _xf(loc, yaw, s)
    wing = a.part('A12_wings' + tag, 'Team', parent)
    hx = A12_T * .52
    wing.loft([_a12_section(x, at) for x in (-hx, -2.2, -1.0, 0, 1.0, 2.2, hx)])
    for sgn in (-1, 1):
        xs = [sgn * hx, sgn * (hx + (A12_T - hx) * .5), sgn * (A12_T - .05)]
        if sgn < 0:
            xs = xs[::-1]
        wing.loft([_a12_section(x, at, fold=(hx, math.radians(105)) if folded else None) for x in xs])
    hump = a.part('A12_hump' + tag, 'Team', parent)
    mid = [[at(-w, py, 1.25), at(w, py, 1.25), at(w * .6, py, 1.25 + h), at(-w * .6, py, 1.25 + h)]
           for py, w, h in ((-3.4, .55, .35), (-1.4, .85, .6), (1.2, .9, .42), (3.2, .7, .2))]
    hump.loft([[at(0, -4.4, 1.3)]] + mid + [[at(0, 4.8, 1.3)]])
    a.part('A12_canopy' + tag, 'Glass', parent).loft(
        [[at(-.35, -2.9, 1.6), at(.35, -2.9, 1.6), at(.25, -2.9, 1.8), at(-.25, -2.9, 1.8)],
         [at(-.42, -.6, 1.8), at(.42, -.6, 1.8), at(.3, -.6, 2.02), at(-.3, -.6, 2.02)],
         [at(-.3, .5, 1.7), at(.3, .5, 1.7), at(.2, .5, 1.82), at(-.2, .5, 1.82)]])
    edge = a.part('A12_edges' + tag, 'Armor', parent)
    for sgn in (-1, 1):
        x1 = hx if folded else A12_T - .4
        edge.tube([at(sgn * f * x1, _a12_le(f * x1) + .08, 1.17) for f in (.04, .4, .75, 1.0)], .07, seg=4)
        a.part('A12_exhaust' + tag, 'Charred', parent).box((1.0 * s, .9 * s, .06 * s), loc=at(sgn * .75, 5.0, 1.32),
                                                           rot=(0, 0, yaw), bevel=0)
    gear = a.part('A12_wheels' + tag, 'Rubber', parent)
    struts = a.part('A12_struts' + tag, 'Steel', parent)
    for px, py, r in ((0, -3.6, .28), (-1.8, 1.0, .36), (1.8, 1.0, .36)):
        gear.cyl(r * s, .24 * s, loc=at(px, py, r), rot=(0, R90, yaw), seg=8, bevel=0)
        struts.limb(at(px, py, r), at(px, py, 1.12), .1 * s, .1 * s, bevel=0)
    if launch:
        struts.limb(at(0, -3.6, .3), at(0, -4.5, .05), .08 * s, .08 * s, bevel=0)


def kr_catapult(a, x, y0, y1, z):
    """A catapult track on the flight deck from y1 (the shuttle's start, aft) to y0 (forward): the slot, the cover
    strips either side, the shuttle, the hazard chevrons at the start, the dashed launch line, the water brake hatch at
    the forward end."""
    L = y1 - y0
    yc = (y0 + y1) / 2
    a.part('Cat_slot', 'Charred').box((.07, L, .02), loc=(x, yc, z + .012), bevel=0)
    for sx in (-1, 1):
        a.part('Cat_covers', 'Steel').box((.16, L, .02), loc=(x + sx * .14, yc, z + .01), bevel=0)
    k.block(a.part('Cat_shuttle', 'Steel'), (.3, .7, .12), loc=(x, y1 - .5, z), chamfer=.03)
    hz = a.part('Cat_marks', 'Hazard')
    for j in range(4):
        for sx in (-1, 1):
            hz.box((.12, .9, .015), loc=(x + sx * .55, y1 - .5 - j * .7, z + .008), rot=(0, 0, sx * .5), bevel=0)
    wm = a.part('Deck_markings', 'PlasterWhite')
    for j in range(int(L / 1.8)):
        wm.box((.12, .9, .015), loc=(x + .6, y0 + .5 + j * 1.8, z + .008), bevel=0)
    k.block(a.part('Cat_brake', 'Armor'), (.7, 1.0, .05), loc=(x, y0 + .7, z - .01), chamfer=.015)


def kr_jbd(a, x, y, z, w=5.2, raised=True):
    """A jet blast deflector behind a catapult's start: the water-cooled panel row hinged at the deck, raised on its
    rams (or lying flush, `raised` False), the cooling panel seams."""
    d = 1.5
    if raised:
        ang = .95
        c = (x, y + math.sin(ang) * d / 2, z + math.cos(ang) * d / 2)
        a.part('Jbd_panels', 'Steel').box((w, .14, d), loc=c, rot=(-ang, 0, 0), bevel=.02)
        for j in range(1, 4):
            a.part('Jbd_seams', 'Charred').box((.04, .02, d * .95), loc=(x - w / 2 + j * w / 4, c[1] - .07, c[2]),
                                               rot=(-ang, 0, 0), bevel=0)
        for dx in (-w * .3, w * .3):
            a.part('Jbd_rams', 'Steel').limb((x + dx, y + 1.5, z), (x + dx, y + .75, z + .5), .1, .1, bevel=0)
    else:
        a.part('Jbd_panels', 'Steel').box((w, d, .03), loc=(x, y + d / 2, z + .005), bevel=0)
        for j in range(1, 4):
            a.part('Jbd_seams', 'Charred').box((.04, d - .1, .015), loc=(x - w / 2 + j * w / 4, y + d / 2, z + .02),
                                               bevel=0)


def kr_notched(outline, hole, corner=.4):
    """The outline (its corners rounded) with a rectangular hole (`hole` = x0, x1, y0, y1) as two polygons: the
    outline cut across the hole's middle, each half with its notch."""
    poly = [(p[0], p[1]) for p in (k.round_corners(outline, corner) if corner > 0 else outline)]
    x0, x1, hy0, hy1 = hole
    yc = (hy0 + hy1) / 2

    def clip(below):
        out = []
        n = len(poly)
        for i in range(n):
            p, q = poly[i], poly[(i + 1) % n]
            pin = p[1] <= yc if below else p[1] >= yc
            qin = q[1] <= yc if below else q[1] >= yc
            if pin:
                out.append(p)
            if pin != qin:
                f = (yc - p[1]) / (q[1] - p[1])
                out.append((p[0] + (q[0] - p[0]) * f, yc))
        n = len(out)
        i = next(i for i in range(n) if abs(out[i][1] - yc) < 1e-6 and abs(out[(i + 1) % n][1] - yc) < 1e-6)
        a_, b_ = out[i], out[(i + 1) % n]
        yn = hy0 if below else hy1
        notch = [(x0, yc), (x0, yn), (x1, yn), (x1, yc)] if a_[0] < b_[0] else [(x1, yc), (x1, yn), (x0, yn), (x0, yc)]
        return out[:i + 1] + notch + out[i + 1:]
    return [clip(True), clip(False)]


def kr_deck_plate(a, outline, z0, t, hole, corner=.4):
    """The flight deck plate (`outline`, z0 .. z0 + t) with the lift well cut through it (kr_notched)."""
    fd = a.part('Flight_deck', 'Asphalt')
    for poly in kr_notched(outline, hole, corner):
        k.extrude(fd, poly, t, loc=(0, 0, z0 + t / 2), axis='Z', chamfer=.05)


def kr_lift_well(a, hole, z_top, z_floor):
    """The lowered lift in its well: the well's dark walls round the cut, the lift platform down at the hangar deck
    with its hazard edges and tie-downs, the safety stanchions and chains raised round the opening."""
    x0, x1, y0, y1 = hole
    w, d = x1 - x0, y1 - y0
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    hgt = z_top - z_floor
    wall = a.part('Lift_well', 'Charred')
    wall.box((w, .06, hgt), loc=(xc, y0 + .03, z_floor + hgt / 2), bevel=0)
    wall.box((w, .06, hgt), loc=(xc, y1 - .03, z_floor + hgt / 2), bevel=0)
    wall.box((.06, d, hgt), loc=(x0 + .03, yc, z_floor + hgt / 2), bevel=0)
    wall.box((.06, d, hgt), loc=(x1 - .03, yc, z_floor + hgt / 2), bevel=0)
    a.part('Lift_platform', 'Armor').box((w - .16, d - .16, .06), loc=(xc, yc, z_floor + .03), bevel=0)
    hz = a.part('Lift_edges', 'Hazard')
    for yy in (y0 + .2, y1 - .2):
        hz.box((w - .3, .12, .01), loc=(xc, yy, z_floor + .065), bevel=0)
    grid = a.part('Lift_tiedowns', 'Steel')
    for i in range(4):
        for j in range(5):
            grid.box((.06, .06, .01), loc=(x0 + .8 + i * (w - 1.6) / 3, y0 + .8 + j * (d - 1.6) / 4, z_floor + .065),
                     bevel=0)
    st = a.part('Lift_stanchions', 'Steel')
    for xx in (x0 + .4, xc, x1 - .4):
        for yy in (y0 - .25, y1 + .25):
            st.box((.04, .04, .8), loc=(xx, yy, z_top + .4), bevel=0)
    for yy in (y0 - .25, y1 + .25):
        st.tube([(x0 + .4, yy, z_top + .78), (x1 - .4, yy, z_top + .78)], .02, seg=4, caps=False)


# ============================================================================= hydra_sub
def hy_mast_radar(a, loc):
    """Hydra's mast radar (a Snoop Pair-style surface-search head on its own `Radar` pivot): the turning drive collar,
    the slim slotted-waveguide array in its fairing with the radome strip, the twin back-to-back IFF bar, the drip
    shield."""
    r = a.pivot('Radar', loc)
    k.lathe(a.part('Hy_radar_drive', 'Steel', r), [(.09, 0), (.09, .12), (.12, .14), (.12, .2), (0, .21)], seg=10)
    k.extrude(a.part('Hy_radar_fairing', 'Armor', r), [(-.07, 0), (.05, 0), (.07, .12), (.05, .22), (-.07, .22),
                                                       (-.09, .11)], .95, loc=(0, 0, .21), axis='X', chamfer=.012)
    a.part('Hy_radar_face', 'PlasterWhite', r).box((.9, .02, .17), loc=(0, -.075, .32), bevel=0)
    a.part('Hy_radar_iff', 'Undercarriage', r).box((.6, .05, .05), loc=(0, .06, .47), bevel=0)
    a.part('Hy_radar_drive', 'Steel', r).box((.04, .1, .05), loc=(0, .03, .43), bevel=0)
    return r


BUILDERS = {
    'typhon': (typhon, dict(ao_distance=1.0, grime_height=.6, ao_strength=.75)),
}
