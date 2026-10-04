"""Play-test 14 sea bosses after R4 (lane sea): new weapons, smaller Hydra guns and the naval liveries.

Owner (04/10, Docs/prompts/playtest14_vi.txt, block "Bổ sung 04/10 sau khi thử R4"): "nyx thêm 1 bệ tên lửa, scylla
thêm 2 bệ tên lửa"; "scylla thêm súng máy hoặc súng flak phòng không vào 4 khẩu, nyx cũng thêm nhưng 2 khẩu"; "typhon
thêm 1 súng tương tự 2 súng kia ở đuôi"; "hydra ... súng làm nhỏ lại cỡ typhon thôi"; "các model boss tàu mới và model
các boss thuyền nên sửa lại màu luôn"; and "nhớ là vẽ lại chứ đừng dùng model cũ". Every function here is drawn for one
ship only, from geometry primitives (no kit sub-assembly, nothing shared with another unit or boss), read from a real
type at the ship's scale. DECISIONS "## Play-test 14 sea bosses after R4 (lane sea)".

- scylla: two AK-230-read twin 30 mm turrets on the after superstructure (Mount_mg.001 / .002), two 2M-7-read twin
  14.5 mm pedestal mounts on the bridge wings (Mount_mg.003 / .004), two Uran-read quad canister banks beside the after
  superstructure (Mount_missile / .001).
- nyx: two Millennium-read 35 mm stealth turrets on the hangar roof (Mount_mg.002 / .003), a Mk 41-read eight-cell VLS
  block in the B position (Mount_missile).
- typhon: a third AK-725-read twin 57 mm on the stern casing (Mount_gun.003), drawn anew on its own raised barbette.
- hydra_sub: the twin 57 mm (Mount_gun / .001) and the 100 mm (Mount_gun.002) drawn anew at Typhon's proportion to the
  hull (0.6 / 0.75 of the R4 guns), and the launch tubes behind the sail (Part_doors_l / _r) drawn as a real vertical
  launcher with two lids open a side (Hydra's cruise missiles leave from them).
- livery(a, ship): a bespoke naval paint scheme per ship (leviathan, kraken, scylla, nyx, typhon, hydra_sub): the
  builder's materials are mapped by part to kit surfaces (haze greys, deck greys, red oxide, anechoic black, stealth
  grey) before the finish, and after the bake each surface is tinted in COLOR_0 for that ship (the hue the material
  alone cannot give) with a little waterline grime. No Team material is left on these ships: they are shown as drawn
  (lane K's data flag keeps the bosses' own paint).

A Free mount's pivot is turned to its target by the view, so the canister banks and the VLS block are fixed geometry
and their Mount_missile pivots carry only the muzzle (at the mouth); turrets carry their house on the pivot.
Metres, +Z up, -Y front, +X left (port).
"""
import math
import re

from mathutils import Matrix, Vector

import frontier_kit as kit
import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau

# Two kit surfaces the runtime knows (MaterialLibrary.Kit) that the Blender kit had not listed yet; same values. The
# naval paints NavyGrey, NavyDeck, HullRed, BootTop, SubBlack are lane K's (frontier_kit and MaterialLibrary.Kit).
kit.MATERIALS.setdefault('ContainerGrey', ('#8a9095', 0.3, 0.55, 0.0))
kit.MATERIALS.setdefault('CarGrey', ('#6c7176', 0.4, 0.4, 0.0))


def fwd(part, profile, loc, seg=14, rot=K.FORWARD):
    """A turned part along -Y (the front): profile [(radius, distance forward)] from loc."""
    k.lathe(part, profile, loc=loc, rot=rot, seg=seg)


def barrel_points(a, muzzle, tag, offsets):
    """Muzzle_b<k>_<tag> under `muzzle` at the given (x, y, z) offsets (each barrel, tube or cell)."""
    for i, p in enumerate(offsets):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', p, muzzle)


def grown(a, s, centre, build):
    """Run build() and scale everything it added (geometry and new pivots) by `s` about the world point `centre`, so a
    mount drawn at its real proportions reads at the battle camera's zoom (the parts it shares, e.g. Glass or
    Kit_bolts, are scaled only in their new vertices)."""
    before = {key: len(sh.bm.verts) for key, sh in a.shapes.items()}
    old_pivots = set(a.pivots)
    build()
    c = Vector(centre)

    def base(pname):
        v, o = Vector(), a.pivots[pname] if pname else None
        while o is not None:
            v += o.location
            o = o.parent
        return v
    for key, sh in a.shapes.items():
        n0 = before.get(key, 0)
        sh.bm.verts.ensure_lookup_table()
        parent = key[2]
        local = parent is not None and parent not in old_pivots
        cl = c - base(parent)
        for v in sh.bm.verts[n0:]:
            v.co = v.co * s if local else cl + (v.co - cl) * s
    for name in set(a.pivots) - old_pivots:
        o = a.pivots[name]
        if o.parent is not None and o.parent.name not in old_pivots:
            o.location = o.location * s
        else:
            cl = c - (base(o.parent.name) if o.parent is not None else Vector())
            o.location = cl + (o.location - cl) * s


# ============================================================================= liveries
def _surface_role(name, mat):
    n = name.lower()
    if mat == 'Team':
        if n.startswith('ensign'):
            return 'flag'
        if re.match(r'(a12_|ka31_|heli_body|drone_)', n):
            return 'air'
        return 'super'
    if mat == 'Armor':
        if re.match(r'(hull|hull_seams|armor_belt|gallery_[lr])$', n):
            return 'hull'
        if re.match(r'(tier_deck|deck_panels|deckhouse_roof|mast_platform|bridge_wings|funnel_platform|lift_platform|'
                    r'aa_sponson_[lr])$', n):
            return 'deck'
        if re.match(r'(hangar|aft_superstructure)$', n):
            return 'super'
        return 'detail'
    if mat == 'Steel':
        if n.startswith(('shafts', 'screw', 'kit_bolts')):
            return None
        if re.search(r'(_barrels|_guns|ciws_gun)', n):
            return 'gunsteel'
        return 'steel'
    if mat == 'BarrelRed':
        return 'bottom' if re.match(r'(hull_bottom|bilge_keels|rudders|sonar_dome)', n) else None
    if mat in ('Undercarriage', 'Charred'):
        if n.startswith('boot_top'):
            return 'boot'
        if re.match(r'(hull_bottom|rudders|sonar_dome)', n):
            return 'bottom'
        return None
    if mat == 'Asphalt':
        return 'flightdeck' if n.startswith(('flight_deck', 'heli_deck')) else 'deck'
    if mat == 'Crate' or (mat == 'CraneYellow' and n == 'crane'):
        return 'detail'
    return None


def _sub_role(name, mat):
    n = name.lower()
    if mat == 'Team':
        if re.match(r'(gun_house|dg_house|sam_head|sg_house)', n):
            return 'gun'
        if n.startswith('hatch_doors'):
            return 'hatch'
        return 'hull'
    if mat == 'Armor':
        if re.match(r'(casing|sail_top|missile_deck|vls_deck_[lr])$', n):
            return 'deck'
        if re.match(r'(hull|sail|bow_planes|stern_fins|screw_shrouds|array_pod|sonar_dome|deck_hatches|well_doors|'
                    r'doors)$', n):
            return 'hull'
        if n == 'deck_tiles':
            return 'tiles'
        if re.match(r'(gun_|dg_|deck_gun|sam_frame|sg_|hg_|hd_)', n):
            return 'gun'
        return 'detail'
    if mat == 'Steel':
        if n == 'deck_tiles_bare':
            return 'primer'
        if re.search(r'(_barrels|_muzzles)', n):
            return 'gunsteel'
        if n.startswith(('screw', 'kit_bolts')):
            return None
        return 'fittings'
    if mat == 'BarrelRed' and n.startswith('boot_top'):
        return 'boot'
    if mat == 'Undercarriage' and n == 'deck_tiles_new':
        return 'tiles_new'
    if mat == 'Hazard' and re.match(r'(hatch_rims|sonar_band)', n):
        return 'detail'
    if mat == 'Asphalt' and n == 'walkway':
        return 'deck'
    return None


# Each ship: the role -> kit surface map and that ship's COLOR_0 tint per surface (rgb multipliers, ~1 on average so
# the baked occlusion keeps its level). Real references: US haze grey 5-H with deck grey 20 and a teak main deck
# (Leviathan, Iowa after her refit); Soviet light blue-grey with dark grey decks (Scylla, Slava; Kraken, Kuznetsov,
# whose flight deck is a dark brownish grey); Zumwalt's dark matte stealth grey (Nyx); the 941's black anechoic coat
# with renewed tile patches and red primer where tiles fell (Typhon); a modern attack boat's blue-black (Hydra).
# Red-oxide anti-fouling (HullRed) at the waterline on the surface ships, each its own shade; deck grey NavyDeck.
LIVERIES = {
    'leviathan': ('surface', dict(hull='ContainerGrey', super='Corrugated', detail='CarGrey', deck='NavyDeck',
                                  flightdeck='Asphalt', steel='MetalSheet', gunsteel='MetalSheet', boot='HullRed',
                                  bottom='HullRed', air='CarGrey', flag='PlasterWhite'),
                  {'ContainerGrey': (1.0, 1.0, 1.03), 'Corrugated': (1.04, .99, 1.0), 'CarGrey': (1.02, 1.01, 1.02),
                   'NavyDeck': (1.04, 1.02, .98), 'MetalSheet': (.9, .91, .93), 'HullRed': (1.04, 1.0, 1.0),
                   'Asphalt': (1.04, 1.02, 1.0)}),
    'kraken': ('surface', dict(hull='ContainerGrey', super='MetalSheet', detail='CarGrey', deck='NavyDeck',
                               flightdeck='Asphalt', steel='Corrugated', gunsteel='Corrugated', boot='HullRed',
                               bottom='HullRed', air='CarGrey', flag='PlasterWhite'),
               {'ContainerGrey': (.93, .99, 1.08), 'MetalSheet': (.9, .96, 1.03), 'CarGrey': (.95, 1.0, 1.07),
                'NavyDeck': (1.0, 1.0, 1.02), 'Asphalt': (1.08, 1.03, .96), 'Corrugated': (.94, .98, 1.04),
                'HullRed': (.94, .9, .9)}),
    'scylla': ('surface', dict(hull='ContainerGrey', super='MetalSheet', detail='CarGrey', deck='NavyDeck',
                               flightdeck='Asphalt', steel='Corrugated', gunsteel='Corrugated', boot='HullRed',
                               bottom='HullRed', air='CarGrey', flag='PlasterWhite'),
               {'ContainerGrey': (.9, .98, 1.1), 'MetalSheet': (.88, .95, 1.04), 'CarGrey': (.93, 1.0, 1.09),
                'NavyDeck': (.96, 1.0, 1.04), 'Corrugated': (.93, .99, 1.06), 'HullRed': (1.08, 1.0, .98),
                'Asphalt': (1.0, 1.0, 1.03)}),
    'nyx': ('surface', dict(hull='NavyGrey', super='CarGrey', detail='RoofSlate', deck='NavyDeck',
                            flightdeck='NavyDeck', steel='MetalSheet', gunsteel='MetalSheet', boot='HullRed',
                            bottom='HullRed', air='CarGrey', flag='PlasterWhite'),
            {'NavyGrey': (1.0, 1.0, 1.0), 'CarGrey': (1.08, 1.06, 1.03), 'RoofSlate': (1.1, 1.05, .97),
             'NavyDeck': (1.0, 1.0, 1.02), 'MetalSheet': (.78, .79, .8), 'HullRed': (.78, .74, .74)}),
    'typhon': ('sub', dict(hull='SubBlack', deck='NavyDeck', gun='Armor', hatch='Undercarriage', tiles='EliteBlack',
                           tiles_new='Charred', primer='RailBrown', gunsteel='CarGrey', fittings='Undercarriage',
                           detail='Undercarriage', boot='HullRed'),
               {'SubBlack': (1.1, 1.1, 1.1), 'NavyDeck': (.8, .8, .8), 'Armor': (.86, .88, .9),
                'EliteBlack': (1.2, 1.2, 1.2), 'Charred': (1.05, .98, .92), 'HullRed': (.9, .86, .84),
                'CarGrey': (.84, .85, .87), 'RailBrown': (.72, .66, .64)}),
    'hydra_sub': ('sub', dict(hull='SubBlack', deck='NavyDeck', gun='CarGrey', hatch='Armor', tiles='EliteBlack',
                              tiles_new='Charred', primer='HullRed', gunsteel='Armor', fittings='Armor', detail='Armor',
                              boot='HullRed'),
                  {'SubBlack': (1.0, 1.08, 1.2), 'NavyDeck': (.76, .8, .86), 'CarGrey': (.9, .95, 1.02),
                   'Armor': (.8, .84, .9), 'EliteBlack': (1.1, 1.12, 1.2)}),
}


def _merge_into(dst, src):
    vmap = {}
    for v in src.bm.verts:
        nv = dst.bm.verts.new(v.co)
        nv[dst.wear] = v[src.wear]
        vmap[v] = nv
    for f in src.bm.faces:
        dst.bm.faces.new([vmap[v] for v in f.verts])
    src.bm.free()


def livery(a, ship):
    """Paint `ship` (a key of LIVERIES): call after every part is made (before a static merge, before the finish)."""
    kind, roles, tints = LIVERIES[ship]
    role_of = _surface_role if kind == 'surface' else _sub_role
    shapes, order = {}, []
    for key in a.order:
        name, mat, parent = key
        role = role_of(name, mat)
        new = roles.get(role, mat) if role else mat
        nk = (name, new, parent)
        if nk in shapes:
            _merge_into(shapes[nk], a.shapes[key])
        else:
            shapes[nk] = a.shapes[key]
            order.append(nk)
    a.shapes, a.order = shapes, order
    grime = {roles.get('hull'), roles.get('boot'), roles.get('bottom')}
    original = a.finish

    def finish():
        out = original()
        _tint(a, tints, grime)
        return out
    a.finish = finish


def _tint(a, tints, grime):
    for ob in a.objects:
        me = ob.data
        attr = me.color_attributes.get('Col')
        if attr is None or not me.materials or me.materials[0] is None:
            continue
        mat = me.materials[0].name.split('.')[0]
        if mat in kit.GLOWING:
            continue
        t = tints.get(mat)
        wet = mat in grime
        if t is None and not wet:
            continue
        t = t or (1.0, 1.0, 1.0)
        off = K._world_offset(ob)
        cols = [0.0] * (len(me.vertices) * 4)
        attr.data.foreach_get('color', cols)
        for i, v in enumerate(me.vertices):
            g = 1.0
            if wet:
                # Waterline grime: a little darker and greener in the splash zone, fading out by 0.9 m.
                z = off.z + v.co.z
                g = 1.0 - .12 * max(0.0, min(1.0, (.9 - z) / 1.2))
            for c in range(3):
                cols[i * 4 + c] = max(0.0, min(1.0, cols[i * 4 + c] * t[c] * (g if c != 1 else g * 1.01)))
        attr.data.foreach_set('color', cols)


# ============================================================================= scylla
def sc_ak230(a, index, loc):
    """An AK-230-read twin 30 mm turret (Mount_mg[.NNN], an AA mount): the deck coaming with its bolt ring; on the yaw
    pivot the low beehive house (a drum, a rounded shoulder, a flat crown), the raked mantlet face with its two
    embrasures and canvas-free rubber boots, the twin barrels with their flash hiders (Ak_barrels / Ak_muzzles, the
    kick parts), the cheek ammunition bulges, the roof hatch with hinges, the vision cupola, the rear door, the case
    chute under the guns; Muzzle_mg[.NNN] between the tips and the per-barrel muzzles."""
    tag = f'_{index:03d}'
    x, y, z = loc
    R = .58
    k.lathe(a.part('Ak_coaming' + tag, 'Armor'), [(R + .1, 0), (R + .1, .09), (R + .05, .14), (R - .02, .14)],
            loc=(x, y, z), seg=22)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .14), (0, 0, 1), R + .07, 14, r=.014, h=.016)
    m = a.pivot(K.name('Mount_mg', index), (x, y, z + .14))
    k.ring(a.part('Ak_race' + tag, 'Steel', m), [(R - .06, -.01), (R + .01, -.01), (R + .01, .05), (R - .06, .06)],
           seg=22)
    house = a.part('Ak_house' + tag, 'Team', m)
    k.lathe(house, [(R, .02), (R + .015, .07), (R + .015, .36), (R * .95, .46), (R * .82, .56), (R * .6, .63),
                    (R * .3, .665), (0, .67)], seg=24, worn=(2, 4))
    # The raked mantlet face, its embrasures, the boots; the cheek ammunition bulges.
    k.block(a.part('Ak_face' + tag, 'Armor', m), (.62, .14, .4), loc=(0, -R + .02, .27), rot=(-.28, 0, 0),
            chamfer=.025, ends=(True, True))
    zg, gap = .28, .12
    for s in (-1, 1):
        a.part('Ak_ports' + tag, 'Charred', m).box((.08, .05, .2), loc=(s * gap, -R - .06, zg), rot=(-.28, 0, 0),
                                                   bevel=0)
        fwd(a.part('Ak_boots' + tag, 'Rubber', m), [(.05, 0), (.056, .04), (.045, .08), (.05, .12), (.034, .15)],
            (s * gap, -R - .05, zg), seg=10)
        fwd(a.part('Ak_barrels' + tag, 'Steel', m), [(.03, 0), (.03, .62), (.026, .66), (.024, .98), (0, .98)],
            (s * gap, -R - .16, zg), seg=10)
        mz = a.part('Ak_muzzles' + tag, 'Undercarriage', m)
        fwd(mz, [(.026, 0), (.036, .02), (.036, .13), (.03, .15), (0, .15)], (s * gap, -R - 1.12, zg), seg=10)
        for j in range(3):
            mz.box((.08, .012, .01), loc=(s * gap, -R - 1.16 - j * .035, zg), bevel=0)
        k.lathe(a.part('Ak_cheeks' + tag, 'Armor', m), [(0, -.18), (.1, -.15), (.12, 0), (.1, .15), (0, .18)],
                loc=(s * (R - .02), -.08, .22), rot=(0, R90, 0), seg=10)
    mzp = a.pivot(K.name('Muzzle_mg', index), (0, -R - 1.3, zg), m)
    barrel_points(a, mzp, f'mg{tag}', [(-gap, 0, 0), (gap, 0, 0)])
    # The roof: the hatch on its hinges, the vision cupola with its slit, lifting eyes; the rear door; the chute.
    k.lathe(a.part('Ak_hatch' + tag, 'Armor', m), [(.17, 0), (.17, .03), (.13, .05), (0, .055)], loc=(-.14, .12, .665),
            seg=12)
    K.hinge(a.part('Kit_hinges', 'Steel', m), (-.3, .28, .68), (.02, .28, .68), r=.012, knuckles=2)
    k.lathe(a.part('Ak_cupola' + tag, 'Armor', m), [(.11, 0), (.11, .1), (.08, .14), (0, .15)], loc=(.2, -.1, .64),
            seg=10)
    a.part('Glass', 'Glass', m).box((.1, .02, .035), loc=(.2, -.21, .71), bevel=0)
    for ex, ey in ((.38, .3), (-.38, .3), (0, -.42)):
        a.part('Ak_eyes' + tag, 'Steel', m).box((.025, .06, .05), loc=(ex, ey, .6 if ey > 0 else .52), bevel=0)
    k.block(a.part('Ak_door' + tag, 'Armor', m), (.34, .04, .3), loc=(0, R + .01, .22), chamfer=.01)
    K.handle(a.part('Kit_handles', 'Steel', m), (-.08, R + .04, .26), (.08, R + .04, .26), Vector((0, 1, 0)), h=.03,
             r=.007)
    a.part('Ak_chute' + tag, 'Charred', m).box((.2, .05, .06), loc=(0, -R + .02, .06), bevel=0)
    K.soot(a, (x, y - R - 1.25, z + .14 + zg), radius=.3, k=.3)


def sc_2m7(a, index, loc):
    """A 2M-7-read twin 14.5 mm pedestal mount (Mount_mg[.NNN], an AA mount) on a bridge wing: the base flange and
    the column (fixed); on the yaw pivot the cradle, two KPV-read guns (receivers, perforated barrel jackets, conical
    flash hiders: Hmg_barrels / Hmg_muzzles, the kick parts), the outboard ammunition boxes with their feed chutes, the
    curved gun shield, the ring sight on its post, the gunner's seat, shoulder rests and the elevating handwheel;
    Muzzle_mg[.NNN] between the tips and the per-barrel muzzles."""
    tag = f'_{index:03d}'
    x, y, z = loc
    k.lathe(a.part('Hmg_base' + tag, 'Armor'), [(.3, 0), (.3, .04), (.14, .07), (.11, .1)], loc=(x, y, z), seg=14)
    k.lathe(a.part('Hmg_column' + tag, 'Armor'), [(.11, .1), (.09, .18), (.09, .5), (.13, .54), (.13, .58)],
            loc=(x, y, z), seg=12)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .045), (0, 0, 1), .24, 8, r=.012, h=.014)
    m = a.pivot(K.name('Mount_mg', index), (x, y, z + .58))
    k.lathe(a.part('Hmg_turntable' + tag, 'Steel', m), [(.16, 0), (.16, .05), (.12, .07)], seg=14)
    cr = a.part('Hmg_cradle' + tag, 'Armor', m)
    zg, gap = .3, .13
    for s in (-1, 1):
        cr.box((.035, .3, .3), loc=(s * .06, .0, .17), bevel=.008)
    cr.box((.36, .1, .06), loc=(0, .02, .2), bevel=.01)
    for s in (-1, 1):
        bx = s * gap
        k.block(a.part('Hmg_receivers' + tag, 'Armor', m), (.1, .5, .12), loc=(bx, .02, zg), chamfer=.015,
                ends=(True, True))
        fwd(a.part('Hmg_jackets' + tag, 'Undercarriage', m), [(.034, 0), (.034, .46), (.028, .5)], (bx, -.23, zg),
            seg=10)
        jh = a.part('Hmg_vents' + tag, 'Charred', m)
        for j in range(5):
            for u in (0, math.pi):
                jh.box((.012, .045, .012), loc=(bx + math.cos(u) * .035, -.29 - j * .08, zg + math.sin(u) * .035),
                       bevel=0)
        fwd(a.part('Hmg_barrels' + tag, 'Steel', m), [(.016, 0), (.016, .44), (0, .44)], (bx, -.7, zg), seg=8)
        fwd(a.part('Hmg_muzzles' + tag, 'Undercarriage', m), [(.018, 0), (.03, .1), (.03, .12), (0, .12)],
            (bx, -1.12, zg), seg=8)
        # The ammunition box outboard, its feed chute into the receiver.
        k.block(a.part('Hmg_ammo' + tag, 'Crate', m), (.12, .22, .18), loc=(s * (gap + .16), .06, zg - .08),
                chamfer=.012, ends=(True, True))
        a.part('Hmg_feed' + tag, 'Steel', m).limb((s * (gap + .12), .02, zg + .02), (s * (gap + .05), .0, zg + .04),
                                                  .05, .06, bevel=0)
    mzp = a.pivot(K.name('Muzzle_mg', index), (0, -1.26, zg), m)
    barrel_points(a, mzp, f'mg{tag}', [(-gap, 0, 0), (gap, 0, 0)])
    # The shield: three plates bent round the guns, cut out for the barrels.
    sh = a.part('Hmg_shield' + tag, 'Armor', m)
    for u, w_ in ((-.42, .26), (0, .3), (.42, .26)):
        sh.box((w_, .02, .34), loc=(math.sin(u) * .34, -.3 * math.cos(u) - .02, zg + .02), rot=(0, 0, u), bevel=0)
    sh.box((.02, .02, .22), loc=(0, -.33, zg + .3), bevel=0)
    k.ring(a.part('Hmg_sight' + tag, 'Steel', m), [(.04, -.004), (.048, -.004), (.048, .004), (.04, .004)],
           loc=(0, -.34, zg + .43), rot=(R90, 0, 0), seg=12)
    # The gunner: seat, back, shoulder rests, the handwheel.
    a.part('Hmg_seat' + tag, 'Rubber', m).box((.2, .16, .05), loc=(0, .34, .12), bevel=.01)
    a.part('Hmg_seat' + tag, 'Rubber', m).box((.2, .04, .2), loc=(0, .43, .23), rot=(-.2, 0, 0), bevel=.01)
    a.part('Hmg_frame' + tag, 'Steel', m).tube([(0, .06, .07), (0, .28, .1), (0, .34, .1)], .014, seg=5)
    for s in (-1, 1):
        a.part('Hmg_frame' + tag, 'Steel', m).tube([(s * .1, .18, zg), (s * .12, .3, zg + .05)], .012, seg=5)
        a.part('Hmg_rests' + tag, 'Rubber', m).box((.06, .1, .05), loc=(s * .12, .3, zg + .07), bevel=.01)
    k.ring(a.part('Hmg_wheel' + tag, 'Steel', m), [(.06, -.006), (.07, -.006), (.07, .006), (.06, .006)],
           loc=(.2, .2, .2), rot=(0, R90, 0), seg=10)
    K.soot(a, (x, y - 1.2, z + .58 + zg), radius=.2, k=.25)


def sc_uran(a, index, rear, side, deck_z):
    """An Uran-read quad canister bank (Mount_missile[.NNN]) on the main deck: four square ribbed containers in a 2 x 2
    frame laid at 20 degrees and turned 12 degrees outboard, frangible front covers with their tear lines, the
    rear covers with umbilical boxes, the frame's side rails, cross members and deck legs on foot plates, the blast
    deflector plate on the deck ahead of the mouths' path, the stowed handling davit. The pivot carries only the
    muzzle (the view turns it), at the mouths; one launch point per container."""
    el, yaw, L, cw, g = math.radians(20), math.radians(12), 1.9, .3, .02
    d = Vector((side * math.sin(yaw) * math.cos(el), -math.cos(yaw) * math.cos(el), math.sin(el)))
    rot = K.rot_to(d)
    o = Vector(rear) + Vector((0, 0, deck_z + .42))
    fr = K.frame(tuple(o), rot)

    def at(p):
        return K._at(fr, p)
    tag = f'_{index:03d}'
    can = a.part('Uran_canisters' + tag, 'Team')
    ribs = a.part('Uran_ribs' + tag, 'Armor')
    caps = a.part('Uran_caps' + tag, 'Charred')
    tear = a.part('Uran_tear' + tag, 'PlasterWhite')
    cells = [(cx, cy) for cy in (cw / 2 + g, -cw / 2 - g) for cx in (-cw / 2 - g, cw / 2 + g)]
    for cx, cy in cells:
        k.block(can, (cw, cw, L), loc=at((cx, cy, L / 2)), rot=rot, chamfer=.03, ends=(True, True))
        for f in (.08, .3, .52, .74, .94):
            ribs.box((cw + .03, cw + .03, .035), loc=at((cx, cy, L * f)), rot=rot, bevel=.006)
        caps.box((cw - .05, cw - .05, .02), loc=at((cx, cy, L + .01)), rot=rot, bevel=0)
        for q in (-1, 1):
            tear.box((.01, (cw - .06) * 1.38, .006), loc=at((cx, cy, L + .022)),
                     rot=tuple((fr.to_3x3() @ Matrix.Rotation(q * math.pi / 4, 3, 'Z')).to_euler('XYZ')),
                     bevel=0)
        caps.box((cw - .07, cw - .07, .02), loc=at((cx, cy, -.01)), rot=rot, bevel=0)
    # Umbilical boxes on the rear covers, the side rails, the cross members.
    for cy in (cw / 2 + g, -cw / 2 - g):
        a.part('Uran_boxes' + tag, 'Armor').box((.14, .1, .08), loc=at((0, cy, -.06)), rot=rot, bevel=.01)
    rail = a.part('Uran_frame' + tag, 'Armor')
    W = cw + g + .05
    for sx in (-1, 1):
        rail.box((.05, .08, L * .96), loc=at((sx * (W + .02), -W + .04, L * .5)), rot=rot, bevel=.008)
        rail.box((.05, .08, L * .96), loc=at((sx * (W + .02), W - .04, L * .5)), rot=rot, bevel=.008)
    for f in (.15, .85):
        rail.box((2 * W + .1, .06, .06), loc=at((0, -W - .02, L * f)), rot=rot, bevel=.006)
    # The legs from the frame's underside to the deck, on foot plates.
    legs = a.part('Uran_legs' + tag, 'Steel')
    for f in (.12, .78):
        for sx in (-1, 1):
            top = Vector(at((sx * W, -W - .04, L * f)))
            foot = Vector((top.x, top.y, deck_z + .03))
            legs.tube([tuple(top), tuple(foot)], .028, seg=6)
            a.part('Uran_feet' + tag, 'Armor').box((.16, .16, .03), loc=(foot.x, foot.y, deck_z + .015), bevel=0)
        legs.tube([at((-W, -W - .04, L * f)), at((W, -W - .04, L * f))], .02, seg=5)
    # The deflector plate on the deck under the mouths, the davit stowed beside the bank.
    mouth = Vector(at((0, 0, L)))
    a.part('Uran_deflector' + tag, 'Armor').box((1.0, .7, .03), loc=(mouth.x, mouth.y - .2, deck_z + .03),
                                                rot=(0, 0, side * yaw), bevel=.008)
    a.part('Uran_davit' + tag, 'Steel').tube([(o.x - side * .55, o.y - .1, deck_z), (o.x - side * .55, o.y - .1,
                                                                                      deck_z + .9),
                                              (o.x - side * .2, o.y - .4, deck_z + 1.0)], .03, seg=6)
    m = a.pivot(K.name('Mount_missile', index), tuple(mouth + d * .05))
    mz = a.pivot(K.name('Muzzle_missile', index), (0, 0, 0), m)
    barrel_points(a, mz, f'msl{tag}', [tuple(Vector(at((cx, cy, L + .05))) - (mouth + d * .05)) for cx, cy in cells])
    K.soot(a, tuple(mouth), radius=.35, k=.22)


def scylla_weapons(a, deck_z):
    """Scylla's added mounts. Data order (balance scylla "secondary"): mount 1 the AK-100 (Mount_mg), mounts 2-3 the
    AK-230s (Mount_mg.001 port, .002 starboard), mounts 4-5 the 2M-7s (Mount_mg.003 port, .004 starboard), mounts 6-7
    the Uran banks (Mount_missile port, Mount_missile.001 starboard)."""
    # The two smallest mounts are drawn a size up (1.15 / 1.35) so they read at the battle camera's zoom.
    for i, loc in ((1, (1.62, 12.55, 5.06)), (2, (-1.62, 12.55, 5.06))):
        grown(a, 1.15, loc, lambda i=i, loc=loc: sc_ak230(a, i, loc))
    for i, loc in ((3, (2.5, -8.05, 6.235)), (4, (-2.5, -8.05, 6.235))):
        grown(a, 1.35, loc, lambda i=i, loc=loc: sc_2m7(a, i, loc))
    sc_uran(a, 0, (3.42, 11.35, 0), 1, deck_z(11.35))
    sc_uran(a, 1, (-3.42, 11.35, 0), -1, deck_z(11.35))


# ============================================================================= nyx
def nx_millennium(a, index, loc):
    """A Millennium-read 35 mm revolver gun in its stealth turret (Mount_mg[.NNN], an AA mount) on the hangar roof:
    the faceted fixed plinth with its access door; on the yaw pivot the low faceted house (chined, its panels
    recessed), the gun's raked trunnion shroud and boot, the long barrel with its thermal sleeve bands and the
    AHEAD muzzle-velocity coils (Mil_barrels / Mil_muzzles, the kick parts), the drum magazine bulge behind, the
    EO sensor box, the roof hatch; Muzzle_mg[.NNN] at the muzzle."""
    tag = f'_{index:03d}'
    x, y, z = loc
    oct_ = [(math.cos(i * TAU / 8 + TAU / 16) * .62, math.sin(i * TAU / 8 + TAU / 16) * .62) for i in range(8)]
    k.sharp_loft(a.part('Mil_plinth' + tag, 'Team'), [[(x + px, y + py, z) for px, py in oct_],
                                                     [(x + px * .9, y + py * .9, z + .22) for px, py in oct_]],
                 chamfer=.02)
    a.part('Mil_plinth_door' + tag, 'Armor').box((.02, .3, .16), loc=(x + (1 if x > 0 else -1) * .6, y, z + .11),
                                                 rot=(0, (1 if x > 0 else -1) * -.25, 0), bevel=0)
    m = a.pivot(K.name('Mount_mg', index), (x, y, z + .22))
    k.ring(a.part('Mil_race' + tag, 'Steel', m), [(.48, -.01), (.54, -.01), (.54, .04), (.48, .05)], seg=16)
    house = a.part('Mil_house' + tag, 'Team', m)
    k.sharp_loft(house, [
        [(-.3, -.62, .02), (.3, -.62, .02), (.55, -.25, .02), (.56, .5, .02), (.36, .66, .02), (-.36, .66, .02),
         (-.56, .5, .02), (-.55, -.25, .02)],
        [(-.24, -.52, .3), (.24, -.52, .3), (.5, -.2, .32), (.5, .46, .34), (.32, .6, .34), (-.32, .6, .34),
         (-.5, .46, .34), (-.5, -.2, .32)],
        [(-.14, -.3, .48), (.14, -.3, .48), (.34, -.1, .5), (.34, .36, .5), (.22, .48, .5), (-.22, .48, .5),
         (-.34, .36, .5), (-.34, -.1, .5)]], chamfer=.02)
    k.inset(house, lambda c, n, f: c.z > .06 and abs(n.z) < .9, width=.03, depth=-.006)
    zg = .27
    k.sharp_loft(a.part('Mil_shroud' + tag, 'Armor', m), [
        [(-.14, -.5, zg - .14), (.14, -.5, zg - .14), (.14, -.5, zg + .12), (-.14, -.5, zg + .12)],
        [(-.1, -.72, zg - .09), (.1, -.72, zg - .09), (.1, -.72, zg + .09), (-.1, -.72, zg + .09)]], chamfer=.015)
    fwd(a.part('Mil_boot' + tag, 'Rubber', m), [(.075, 0), (.08, .04), (.064, .08), (.068, .12), (.05, .15)],
        (0, -.72, zg), seg=10)
    fwd(a.part('Mil_barrels' + tag, 'Steel', m), [(.042, 0), (.042, .7), (.034, .76), (.032, 1.34), (0, 1.34)],
        (0, -.84, zg), seg=10)
    for j in range(3):
        fwd(a.part('Mil_bands' + tag, 'Undercarriage', m), [(.048, 0), (.048, .045)], (0, -.92 - j * .2, zg), seg=10)
    coil = a.part('Mil_muzzles' + tag, 'Armor', m)
    for j in range(3):
        fwd(coil, [(.034, 0), (.058, .01), (.058, .06), (.034, .07)], (0, -2.0 - j * .085, zg), seg=12)
    mzp = a.pivot(K.name('Muzzle_mg', index), (0, -2.24, zg), m)
    barrel_points(a, mzp, f'mg{tag}', [(0, 0, 0)])
    # The drum magazine bulge, the EO sensor box, the roof hatch, lifting eyes.
    k.lathe(a.part('Mil_drum' + tag, 'Armor', m), [(0, -.2), (.2, -.17), (.24, 0), (.2, .17), (0, .2)],
            loc=(0, .62, .22), rot=(0, R90, 0), seg=12)
    k.sharp_loft(a.part('Mil_eo' + tag, 'Armor', m), [
        [(.2, -.2, .5), (.36, -.2, .5), (.36, .02, .5), (.2, .02, .5)],
        [(.22, -.16, .62), (.34, -.16, .62), (.34, 0, .62), (.22, 0, .62)]], chamfer=.01)
    a.part('Glass', 'Glass', m).box((.1, .015, .06), loc=(.28, -.205, .56), rot=(-.25, 0, 0), bevel=0)
    k.block(a.part('Mil_hatch' + tag, 'Armor', m), (.26, .26, .025), loc=(-.12, .2, .51), chamfer=.008)
    K.hinge(a.part('Kit_hinges', 'Steel', m), (-.24, .34, .53), (0, .34, .53), r=.01, knuckles=2)
    for ex, ey in ((.3, .4), (-.3, .4)):
        a.part('Mil_eyes' + tag, 'Steel', m).box((.02, .05, .04), loc=(ex, ey, .51), bevel=0)
    K.soot(a, (x, y - 2.2, z + .22 + zg), radius=.25, k=.25)


def nx_vls(a, loc, deck_z):
    """A Mk 41-read eight-cell VLS block in the B position (Mount_missile): the raised stealth-faceted module (its
    sloped sides with flush panels, the deck coaming), two columns of four cell hatches with the exhaust uptake
    between them (the uptake hatch, its louvres), hinge fairings, two cells open (the hatches raised, the
    canister tops with their frangible covers, a round's nose cap in each), deck rings for the strongback, the
    drain scuppers. The pivot carries only the muzzle, above the open cells."""
    x, y, _ = loc
    W, D, H = 1.15, 1.25, .42
    z0 = deck_z
    blk = a.part('Vls_module', 'Team')
    k.sharp_loft(blk, [[(x - W, y - D, z0), (x + W, y - D, z0), (x + W, y + D, z0), (x - W, y + D, z0)],
                       [(x - W + .16, y - D + .16, z0 + H), (x + W - .16, y - D + .16, z0 + H),
                        (x + W - .16, y + D - .16, z0 + H), (x - W + .16, y + D - .16, z0 + H)]], chamfer=.03)
    k.inset(blk, lambda c, n, f: abs(n.z) < .9, width=.04, depth=-.008)
    a.part('Vls_coaming', 'Armor').box((2 * W + .1, 2 * D + .1, .04), loc=(x, y, z0 + .02), bevel=.008)
    top = z0 + H
    hat = a.part('Vls_hatches', 'Armor')
    seams = a.part('Vls_seams', 'Undercarriage')
    seams.box((2 * W - .34, 2 * D - .34, .01), loc=(x, y, top + .003), bevel=0)
    cs = .42
    opened = {(0, 1), (1, 1)}
    for col, cx in enumerate((-.47, .47)):
        for row, cy in enumerate((-.66, -.22, .22, .66)):
            px, py = x + cx, y + cy
            if (col, row) in opened:
                # The open cell: the canister top in its well, the frangible cover, the round's nose cap.
                a.part('Vls_cells', 'Charred').box((cs - .02, cs - .02, .02), loc=(px, py, top + .004), bevel=0)
                k.block(a.part('Vls_canister', 'Undercarriage'), (cs - .08, cs - .08, .03), loc=(px, py, top - .01),
                        chamfer=.006)
                k.lathe(a.part('Vls_nose', 'PlasterWhite'), [(.1, 0), (.09, .04), (.05, .08), (0, .1)],
                        loc=(px, py, top - .002), seg=10)
                # The hatch swung up past the vertical on its outboard hinge.
                s = 1 if cx > 0 else -1
                hx = px + s * (cs / 2 + .015)
                hat.box((.03, cs - .02, cs - .02), loc=(hx + s * .015, py, top + cs / 2 - .01), rot=(0, s * -.12, 0),
                        bevel=.006)
                a.part('Vls_hinges', 'Steel').cyl(.018, cs - .08, loc=(hx, py, top + .015), rot=(R90, 0, 0), seg=6,
                                                  bevel=0)
            else:
                k.block(hat, (cs - .03, cs - .03, .03), loc=(px, py, top + .02), chamfer=.008)
                a.part('Vls_hinges', 'Steel').box((.03, cs - .1, .02), loc=(px + (1 if cx > 0 else -1) *
                                                                            (cs / 2 - .01), py, top + .03),
                                                  bevel=0)
    # The exhaust uptake between the columns: its long hatch with louvres.
    k.block(a.part('Vls_uptake', 'Armor'), (.32, 2 * D - .5, .04), loc=(x, y, top + .02), chamfer=.01)
    for j in range(7):
        a.part('Vls_louvres', 'Undercarriage').box((.24, .04, .012), loc=(x, y - .62 + j * .2, top + .045), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.ring(a.part('Vls_rings', 'Steel'), [(.04, 0), (.055, 0), (.055, .02), (.04, .02)],
                   loc=(x + sx * (W - .1), y + sy * (D - .1), z0 + .04), seg=8)
        a.part('Vls_scuppers', 'Charred').box((.02, .4, .05), loc=(x + sx * (W + .006), y, z0 + .07), bevel=0)
    m = a.pivot('Mount_missile', (x, y + .22, top + .12))
    mz = a.pivot('Muzzle_missile', (0, 0, .05), m)
    barrel_points(a, mz, 'msl', [(-.47, 0, 0), (.47, 0, 0)])


def nyx_weapons(a, deck_z):
    """Nyx's added mounts. Data order (balance nyx "secondary"): mounts 1-2 the Mk 110 cupolas (Mount_mg / .001),
    mounts 3-4 the Millennium turrets (Mount_mg.002 port, .003 starboard), mount 5 the VLS block (Mount_missile)."""
    nx_millennium(a, 2, (2.2, 11.85, 6.42))
    nx_millennium(a, 3, (-2.2, 11.85, 6.42))
    nx_vls(a, (0, -8.7, 0), deck_z(-8.7) + .07)


# ============================================================================= typhon
def ty_stern57(a, loc):
    """The third AK-725-read twin 57 mm, on the stern casing (Mount_gun.003): drawn anew for this mount. The raised
    elliptical barbette that levels the sloping casing (ribbed, a hatch, its rail stanchions and a rung ladder), the
    deck ring with bolts; on the yaw pivot the drum gunhouse (a stepped dome in two rings, the flat raked front with
    its two ports), two water-jacketed barrels with slotted brakes (Gun_barrels_003 / Gun_muzzles_003, the kick
    parts), the twin sight blisters, the roof hatch and vent, the case chutes on both cheeks, the rear access door;
    Muzzle_gun.003 between the brakes and the per-barrel muzzles."""
    x, y, z0, ztop = loc
    h = ztop - z0
    bar = a.part('Sg_barbette', 'Armor')
    rings = []
    for zz, sx, sy in ((z0 - .25, 1.32, 1.5), (z0 + h * .5, 1.24, 1.38), (ztop, 1.16, 1.22)):
        rings.append([(x + math.cos(i * TAU / 20) * sx, y + math.sin(i * TAU / 20) * sy, zz) for i in range(20)])
    bar.loft(rings, bevel=0)
    for i in range(10):
        u = i * TAU / 10 + TAU / 20
        bar.box((.07, .18, h * .8), loc=(x + math.cos(u) * 1.25, y + math.sin(u) * 1.36, z0 + h * .45),
                rot=(0, 0, u), bevel=0)
    a.part('Sg_door', 'Charred').box((.04, .44, h * .55), loc=(x + 1.24, y + .3, z0 + h * .45), rot=(0, 0, -.2),
                                      bevel=0)
    K.ladder(a.part('Rungs', 'Steel'), (x, y + 1.42, z0 - .1), (x, y + 1.25, ztop), width=.36, step=.28,
             facing=(0, 1))
    st = a.part('Sg_stanchions', 'Steel')
    for i in range(7):
        u = math.pi * .15 + i * math.pi * .7 / 6
        p0 = (x + math.cos(u) * 1.1, y + math.sin(u) * 1.16, ztop)
        st.tube([p0, (p0[0], p0[1], ztop + .55)], .018, seg=5)
    st.tube([(x + math.cos(math.pi * .15 + i * math.pi * .7 / 6) * 1.1,
              y + math.sin(math.pi * .15 + i * math.pi * .7 / 6) * 1.16, ztop + .55) for i in range(7)], .015, seg=4)
    k.lathe(a.part('Sg_deck_ring', 'Steel'), [(1.08, 0), (1.12, 0), (1.12, .05), (1.06, .07)], loc=(x, y, ztop), seg=24)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, ztop + .05), (0, 0, 1), 1.09, 20, r=.016, h=.018)
    m = a.pivot('Mount_gun__003', (x, y, ztop + .07))
    house = a.part('Sg_house', 'Team', m)
    k.lathe(house, [(.95, 0), (.98, .08), (.98, .56), (.93, .7), (.8, .8)], seg=26, worn=(2,))
    k.lathe(house, [(.8, .8), (.74, .83), (.6, .9), (.36, .97), (0, 1.0)], seg=26)
    k.ring(a.part('Sg_roof_lip', 'Armor', m), [(.79, .79), (.83, .79), (.83, .82), (.79, .83)], seg=26)
    k.block(a.part('Sg_face', 'Armor', m), (1.3, .32, .74), loc=(0, -.85, .38), rot=(.36, 0, 0), chamfer=.05,
            taper=(.9, 1), ends=(True, True))
    zg, gap = .45, .22
    for sx in (-gap, gap):
        a.part('Sg_ports', 'Charred', m).box((.2, .1, .32), loc=(sx, -1.0, zg + .02), rot=(.36, 0, 0), bevel=.02)
        fwd(a.part('Sg_sleeves', 'Armor', m), [(.115, 0), (.115, .14), (.1, .2), (.09, .24)], (sx, -1.0, zg), seg=12)
        fwd(a.part('Gun_barrels_003', 'Steel', m), [(.074, 0), (.074, .5), (.07, .54), (.074, .58), (.074, 1.02),
                                                    (.06, 1.08), (.045, 1.13), (.045, 2.1), (0, 2.1)],
            (sx, -1.22, zg), seg=12)
        br = a.part('Gun_muzzles_003', 'Undercarriage', m)
        fwd(br, [(.05, 0), (.07, .02), (.07, .27), (.052, .29), (0, .29)], (sx, -3.3, zg), seg=12)
        for dy in (.06, .14, .22):
            br.box((.16, .035, .028), loc=(sx, -3.3 - dy, zg), bevel=0)
    mzp = a.pivot('Muzzle_gun__003', (0, -3.62, zg), m)
    barrel_points(a, mzp, 'gun_003', [(-gap, 0, 0), (gap, 0, 0)])
    for bx in (.52, -.52):
        k.lathe(a.part('Sg_blisters', 'Armor', m), [(0, -.19), (.16, -.15), (.2, 0), (.16, .15), (0, .19)],
                loc=(bx, -.4, .86), rot=K.FORWARD, seg=10)
        a.part('Glass', 'Glass', m).box((.14, .02, .09), loc=(bx, -.6, .87), bevel=0)
        a.part('Sg_chutes', 'Steel', m).limb((bx * 1.5, -.15, .32), (bx * 1.86, .05, .02), .13, .1, bevel=0)
    k.lathe(a.part('Sg_hatch', 'Armor', m), [(.22, 0), (.22, .04), (.17, .06), (0, .065)], loc=(0, .38, .93), seg=14)
    K.hinge(a.part('Kit_hinges', 'Steel', m), (-.18, .6, .96), (.18, .6, .96), r=.014, knuckles=2)
    k.lathe(a.part('Sg_vent', 'Armor', m), [(.1, 0), (.1, .14), (.14, .16), (0, .2)], loc=(.42, .5, .82), seg=10)
    k.block(a.part('Sg_door', 'Armor', m), (.46, .04, .44), loc=(0, .98, .32), chamfer=.012)
    K.handle(a.part('Kit_handles', 'Steel', m), (-.1, 1.01, .38), (.1, 1.01, .38), Vector((0, 1, 0)), h=.04, r=.009)
    K.soot(a, (x, y - 3.5, ztop + .07 + zg), radius=.4, k=.3)


# ============================================================================= hydra_sub
HY_57 = .6     # the R4 twin 57 mm's size -> Typhon's proportion to the hull
HY_100 = .75


def hy_twin57(a, index, loc, tag, mtag):
    """Hydra's twin 57 mm (Mount_gun[.001]) drawn anew at Typhon's proportion (house 1.14 m wide): the flush ring in
    the casing with its drain slots; on the yaw pivot a low rounded-wedge house (superelliptic plan, a sloped front
    shield with one wide embrasure for both barrels and its rubber curtain), the barrels in short thermal sleeves with
    perforated brakes (Gun_barrels* / Gun_muzzles*), the ammunition hoist trunk at the back, the EO pod on a short
    arm, the roof hatch, the louvre; Muzzle_gun[.001] between the brakes and the per-barrel muzzles."""
    x, y, z = loc
    s = HY_57
    k.ring(a.part('Hg_ring' + tag, 'Undercarriage'), [(.6, -.02), (.66, -.02), (.66, .03), (.6, .04)], loc=(x, y, z),
           seg=22)
    for i in range(6):
        u = i * TAU / 6
        a.part('Hg_drains' + tag, 'Charred').box((.1, .03, .01), loc=(x + math.cos(u) * .7, y + math.sin(u) * .7,
                                                                      z + .005), rot=(0, 0, u + R90), bevel=0)
    m = a.pivot(K.name('Mount_gun', index), (x, y, z + .03))
    house = a.part('Gun_house' + tag, 'Team', m)

    def plan(w, f, b, e=3.2, n=16):
        pts = []
        for i in range(n):
            u = i * TAU / n - R90
            c, sn = math.cos(u), math.sin(u)
            px = w * math.copysign(abs(c) ** (2 / e), c)
            py = (f if sn < 0 else b) * math.copysign(abs(sn) ** (2 / e), sn)
            pts.append((px, py))
        return pts
    rings = [(.0, plan(.57, .7, .62)), (.24, plan(.55, .66, .6)), (.4, plan(.45, .48, .52)), (.47, plan(.3, .3, .4))]
    k.sharp_loft(house, [[(px, py, zz) for px, py in pl] for zz, pl in rings], chamfer=.012, corners=[])
    zg, gap = .22, .13
    k.block(a.part('Gun_face' + tag, 'Armor', m), (.62, .06, .26), loc=(0, -.66, zg + .01), rot=(-.42, 0, 0),
            chamfer=.012, ends=(True, True))
    a.part('Gun_ports' + tag, 'Charred', m).box((.42, .04, .1), loc=(0, -.7, zg), rot=(-.42, 0, 0), bevel=0)
    a.part('Gun_boots' + tag, 'Rubber', m).box((.4, .05, .09), loc=(0, -.73, zg), rot=(-.42, 0, 0), bevel=.01)
    for bx in (-gap, gap):
        fwd(a.part('Hg_sleeves' + tag, 'Armor', m), [(.052, 0), (.052, .2), (.044, .24)], (bx, -.72, zg), seg=10)
        fwd(a.part('Gun_barrels' + tag, 'Steel', m), [(.034, 0), (.034, .5), (.028, .54), (.026, 1.1), (0, 1.1)],
            (bx, -.94, zg), seg=10)
        br = a.part('Gun_muzzles' + tag, 'Undercarriage', m)
        fwd(br, [(.026, 0), (.038, .015), (.038, .17), (.03, .18), (0, .18)], (bx, -2.02, zg), seg=10)
        for j in range(2):
            for u in (0, math.pi):
                a.part('Hg_holes' + tag, 'Charred', m).box((.012, .03, .016), loc=(bx + math.cos(u) * .039,
                                                                                    -2.07 - j * .07,
                                                                                    zg),
                                                            bevel=0)
    mzp = a.pivot(K.name('Muzzle_gun', index), (0, -2.24, zg), m)
    barrel_points(a, mzp, mtag, [(-gap, 0, 0), (gap, 0, 0)])
    k.lathe(a.part('Hg_trunk' + tag, 'Armor', m), [(.16, 0), (.16, .3), (.12, .34), (0, .35)], loc=(0, .6, .02),
            seg=12)
    a.part('Hg_arm' + tag, 'Steel', m).limb((.3, -.1, .44), (.38, -.22, .58), .03, .03, bevel=0)
    k.lathe(a.part('Hg_eo' + tag, 'Armor', m), [(0, -.08), (.07, -.06), (.08, 0), (.07, .06), (0, .08)],
            loc=(.38, -.25, .6), rot=K.FORWARD, seg=10)
    a.part('Glass', 'Glass', m).box((.07, .012, .04), loc=(.38, -.335, .6), bevel=0)
    k.lathe(a.part('Hg_hatch' + tag, 'Armor', m), [(.13, 0), (.13, .02), (.1, .03), (0, .035)], loc=(-.14, .14, .465),
            seg=12)
    for j in range(3):
        a.part('Hg_louvre' + tag, 'Undercarriage', m).box((.2, .015, .02), loc=(0, .62, .14 + j * .05),
                                                          rot=(.2, 0, 0), bevel=0)
    K.soot(a, (x, y - 2.2, z + .03 + zg), radius=.25, k=.28)
    K.tone(a, K.name('Mount_gun', index), k=.95)
    return s


def hy_100(a, loc):
    """Hydra's 100 mm (Mount_gun.002, the deck_gun part) drawn anew at Typhon's proportion (house 1.5 m wide): a
    low fluted pedestal with an access hatch; on the yaw pivot a pentagonal stealth house (the long raked glacis,
    chined cheeks, a recessed roof), the barrel in its sleeve and boot, the fume extractor, the single-baffle brake
    with side ports (Dg_barrels / Dg_muzzles), the fire-control radome on a stalk, the hatch, the rear ammunition
    door; Muzzle_gun.002 at the brake."""
    x, y, z = loc
    ped = a.part('Hd_pedestal', 'Armor')
    k.lathe(ped, [(.92, -.08), (.92, .08), (.84, .2), (.8, .3), (.76, .32)], loc=(x, y, z), seg=22)
    for i in range(12):
        u = i * TAU / 12
        ped.box((.05, .14, .2), loc=(x + math.cos(u) * .86, y + math.sin(u) * .86, z + .12), rot=(0, 0, u), bevel=0)
    a.part('Hd_ped_hatch', 'Charred').box((.03, .26, .16), loc=(x - .85, y + .2, z + .14), rot=(0, .3, 0), bevel=0)
    m = a.pivot('Mount_gun__002', (x, y, z + .32))
    k.ring(a.part('Hd_race', 'Steel', m), [(.66, -.02), (.72, -.02), (.72, .04), (.66, .05)], seg=20)
    house = a.part('Dg_house', 'Team', m)
    base = [(0, -1.12), (.42, -.86), (.76, -.2), (.76, .82), (-.76, .82), (-.76, -.2), (-.42, -.86)]
    k.sharp_loft(house, [[(px, py, .02) for px, py in base],
                         [(px * .9, py * .9 + .05, .38) for px, py in base],
                         [(px * .62, py * .6 + .16, .62) for px, py in base]], chamfer=.02)
    k.inset(house, lambda c, n, f: c.z > .06, width=.03, depth=-.008)
    zg = .3
    k.block(a.part('Hd_slot', 'Armor', m), (.24, .08, .36), loc=(0, -1.02, zg + .02), rot=(-.5, 0, 0), chamfer=.012)
    fwd(a.part('Hd_boot', 'Rubber', m), [(.09, 0), (.1, .05), (.08, .1), (.085, .14), (.066, .18)], (0, -1.02, zg),
        seg=12)
    L = 2.2
    y0 = -1.18
    fwd(a.part('Dg_barrels', 'Steel', m), [(.07, -.06), (.07, .3), (.058, .36), (.055, .9), (.08, .98), (.084, 1.3),
                                           (.058, 1.38), (.05, L - .04), (0, L - .04)], (0, y0, zg), seg=12)
    br = a.part('Dg_muzzles', 'Armor', m)
    fwd(br, [(.05, 0), (.095, .02), (.095, .2), (.07, .22), (0, .22)], (0, y0 - L + .04, zg), seg=12)
    for sx in (-1, 1):
        a.part('Hd_ports', 'Charred', m).box((.025, .07, .1), loc=(sx * .095, y0 - L - .07, zg), bevel=0)
    a.pivot('Muzzle_gun__002', (0, y0 - L - .22, zg), m)
    a.part('Hd_stalk', 'Armor', m).cyl(.05, .2, loc=(.26, .3, .72), seg=8, bevel=0)
    k.lathe(a.part('Hd_radome', 'PlasterWhite', m), [(.13, 0), (.14, .05), (.1, .13), (0, .16)], loc=(.26, .3, .82),
            seg=12)
    k.lathe(a.part('Hd_hatch', 'Armor', m), [(.15, 0), (.15, .02), (.12, .035), (0, .04)], loc=(-.22, .4, .62), seg=12)
    k.block(a.part('Hd_door', 'Armor', m), (.36, .04, .3), loc=(0, .84, .2), chamfer=.01)
    K.soot(a, (x, y + y0 - L, z + .32 + zg), radius=.3, k=.3)
    K.tone(a, 'Mount_gun__002', k=.95)


def hy_launcher(a, deck_z):
    """Hydra's vertical launcher behind the sail (Part_doors_l / _r, five tubes a side; its cruise missiles leave
    here): per tube a rectangular lid in a raised coaming with its drain slots, the outboard hinge fairing and a
    locking lug; the second and fourth lids of each row stand open past the vertical, showing the tube's dark
    mouth, the muzzle-hatch ring and the round's nose under its cover."""
    for name, s in (('Part_doors_l', 1), ('Part_doors_r', -1)):
        side = '_l' if s > 0 else '_r'
        p = a.pivot(name, (s * .48, 3.8, deck_z))
        a.part('Vls_deck' + side, 'Armor', p).box((.96, 6.1, .06), loc=(0, 0, .03), bevel=.01)
        for j in range(5):
            y = -2.4 + j * 1.2
            k.ring(a.part('Hl_coaming' + side, 'Armor', p), [(.36, .05), (.4, .05), (.4, .1), (.36, .11)],
                   loc=(0, y, 0), seg=16)
            for q in (-1, 1):
                a.part('Hl_drains' + side, 'Charred', p).box((.03, .18, .02), loc=(q * .41, y, .07), bevel=0)
            if j in (1, 3):
                k.lathe(a.part('Hl_mouth' + side, 'Charred', p), [(.34, .11), (.34, .03), (0, .03)], loc=(0, y, 0),
                        seg=16)
                k.ring(a.part('Hl_tube_ring' + side, 'Steel', p), [(.3, .06), (.33, .06), (.33, .1), (.3, .1)],
                       loc=(0, y, 0), seg=16)
                k.lathe(a.part('Hl_nose' + side, 'PlasterWhite', p), [(.22, .04), (.2, .1), (.12, .17), (0, .2)],
                        loc=(0, y, 0), seg=14)
                # The lid stands open on its outboard hinge, tilted a little past the vertical.
                k.lathe(a.part('Hl_lids' + side, 'Armor', p), [(.37, 0), (.37, .06), (.32, .08), (0, .085)],
                        loc=(s * .52, y, .46), rot=(0, s * (R90 + .12), 0), seg=16)
            else:
                k.lathe(a.part('Hl_lids' + side, 'Armor', p), [(.37, 0), (.37, .05), (.3, .075), (0, .08)],
                        loc=(0, y, .1), seg=16)
                a.part('Hl_lugs' + side, 'Steel', p).box((.06, .1, .04), loc=(-s * .34, y, .14), bevel=0)
            a.part('Hl_hinges' + side, 'Steel', p).cyl(.035, .36, loc=(s * .43, y, .12), rot=(R90, 0, 0), seg=8,
                                                     bevel=0)
        K.tone(a, name, k=.9)
