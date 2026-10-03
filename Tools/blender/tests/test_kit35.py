"""Unit tests for the prompt 35 kit (Tools/blender/mb_kit35.py) and its catalogue picture.

    blender --background --python Tools/blender/tests/test_kit35.py                 # tests only
    blender --background --python Tools/blender/tests/test_kit35.py -- --catalog    # + Docs/models/kit_catalog/

Every component is built alone into a fresh asset and finished (the COLOR_0 bake runs). Checked per component:
  * size: the built bounding box against the real-size dimensions it was asked for (15 % tolerance per axis given);
  * bevel: components with big chamfered edges mark worn vertices (the bake's bright edge rows);
  * triangles: at most the component's ceiling (a guard against a parameter exploding the count);
  * names: the part names it promises exist (runtime pivots such as Mount_* / Muzzle_* exactly);
  * no zero-area triangles (mb_kit27.degenerate_triangles) and COLOR_0 on every mesh.
Exit code 1 when any check fails. Deterministic: the kit uses no unseeded randomness.
"""
import json
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
BLENDER = HERE.parent
ROOT = BLENDER.parents[1]
sys.path.insert(0, str(BLENDER))
import frontier_kit as kit  # noqa: E402
import mb_kit27 as k  # noqa: E402
import mb_kit35 as K  # noqa: E402

CATALOG = ROOT / 'Docs' / 'models' / 'kit_catalog'


def _road(a):
    K.road_wheel(a, (0, 0, .35), .35, .14, 1)


# (name, build(a), expected (x, y, z) size or None, triangle ceiling, part names that must exist, bevelled)
CASES = [
    ('chamfer_box', lambda a: K.chamfer_box(a.part('Hull', 'Armor'), (2, 3, 1), (0, 0, .5)), (2, 3, 1), 300,
     ['Hull'], True),
    ('panel', lambda a: K.panel(a, a.part('Panels', 'Armor'), (1.0, .6), (0, 0, 0), (0, 0, 1)), (1.0, .6, None), 900,
     ['Panels', 'Kit_rivets'], True),
    ('weld', lambda a: K.weld(a.part('Kit_welds', 'Charred'), [(0, 0, 0), (1, 0, 0), (1, 1, 0)]), (1.03, 1.03, None),
     200, ['Kit_welds'], False),
    ('hinge', lambda a: K.hinge(a.part('Kit_hinges', 'Steel'), (0, 0, 0), (.4, 0, 0)), (.44, None, None), 200,
     ['Kit_hinges'], False),
    ('hatch_round', lambda a: K.hatch_round(a, (0, 0, 0), r=.4), (None, None, None), 1500,
     ['Hatches', 'Hatch_fittings', 'Glass'], True),
    ('hatch_rect', lambda a: K.hatch_rect(a, (0, 0, 0), (.7, .9)), (.8, 1.0, None), 900, ['Hatches'], True),
    ('lamp', lambda a: K.lamp(a, (0, 0, 0), (0, -1, 0)), (None, None, None), 400, ['Lamps', 'Lamp_rims'], True),
    ('whip_antenna', lambda a: K.whip_antenna(a.part('Antennas', 'Steel'), (0, 0, 0), h=1.6), (None, None, 1.67), 200,
     ['Antennas'], True),
    ('mesh_antenna', lambda a: K.mesh_antenna(a.part('Antennas', 'Steel'), (0, 0, 1), .6, .5), (None, None, None), 400,
     ['Antennas'], False),
    ('dish', lambda a: K.dish(a.part('Dish', 'Armor'), a.part('Dish_feed', 'Steel'), (0, 0, 1), r=.5),
     (1.04, None, 1.04), 600, ['Dish', 'Dish_feed'], True),
    ('periscope', lambda a: K.periscope(a, (0, 0, 0)), (None, None, None), 300, ['Sight', 'Glass'], True),
    ('tow_hook', lambda a: K.tow_hook(a.part('Kit_hooks', 'Steel'), (0, 0, 0)), (None, None, None), 200,
     ['Kit_hooks'], False),
    ('tow_cable', lambda a: K.tow_cable(a.part('Kit_cables', 'Steel'), [(0, 0, 0), (1.5, 0, .1), (2.5, .3, .1)]),
     (None, None, None), 400, ['Kit_cables'], False),
    ('crate', lambda a: K.crate(a.part('Crates', 'Crate'), a.part('Crate_bands', 'Steel'), (.8, .5, .4), (0, 0, 0)),
     (None, None, .41), 300, ['Crates', 'Crate_bands'], True),
    ('jerrycan', lambda a: K.jerrycan(a.part('Jerrycans', 'Fuel'), (0, 0, 0)), (.19, .36, .48), 300, ['Jerrycans'],
     True),
    ('backpack', lambda a: K.backpack(a.part('Bags', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (.4, .3, .5),
                                      (0, 0, 0)), (None, None, .5), 400, ['Bags', 'Kit_straps'], True),
    ('net_roll', lambda a: K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (0, 0, .2)),
     (1.6, None, None), 400, ['Tarp', 'Kit_straps'], False),
    ('grille', lambda a: K.grille(a, (0, 0, 0), 1.0, .6), (1.14, None, .74), 300, ['Grilles', 'Grille_frames'], False),
    ('exhaust', lambda a: K.exhaust(a, (0, 0, 0), r=.06, length=.6), (None, None, None), 700,
     ['Exhaust', 'Exhaust_mufflers'], True),
    ('road_wheel', _road, (None, .7, .7), 900, ['Tyres', 'Wheels'], True),
    ('sprocket', lambda a: K.sprocket(a, (0, 0, .35), .33, 11, .12, 1), (None, None, None), 900, ['Sprockets'], True),
    ('return_roller', lambda a: K.return_roller(a, (0, 0, .5), .1, .1, 1), (None, .2, .2), 200, ['Rollers'], False),
    ('tracks', lambda a: K.tracks(a, 1.4, 6.0, .9, .33, 6, .55), (None, 6.0, .92), 9000,
     ['Tracks', 'Tyres', 'Sprockets'], True),
    ('side_skirt', lambda a: K.side_skirt(a, 1.7, -3, 3, 1.0, .6, 1), (None, 6.0, None), 2500,
     ['Skirts', 'Skirt_flaps', 'Kit_hinges'], True),
    # Wave 2 (lane B's request): skirts without bolts or hinges are lean plates and flaps only.
    ('side_skirt_plain', lambda a: K.side_skirt(a, 1.7, -3, 3, 1.0, .6, 1, hinged=False, bolts=False),
     (None, 6.0, None), 400, ['Skirts', 'Skirt_flaps'], True),
    ('turret_ring', lambda a: K.turret_ring(a.part('Turret_ring', 'Steel'), (0, 0, 0), 1.0), (2.12, 2.12, None), 300,
     ['Turret_ring'], True),
    ('gun_barrel', lambda a: (a.pivot('Turret', (0, 0, 1)),
                              K.gun_barrel(a, 'Main_cannon', 'Turret', 0, 0, 0, 5.0, .08)), (None, None, None), 900,
     ['Main_cannon', 'Muzzle_brake'], True),
    ('roof_mg', lambda a: K.roof_mg(a, None, (0, 0, 0)), (None, None, None), 900, ['MG'], True),
    ('pintle_mg', lambda a: (K.pintle_mg(a, None, (0, 0, 0)), K.pintle_mg(a, None, (1, 0, 0), index=1)),
     (None, None, None), 1200, ['Mount_mg', 'Mount_mg.001', 'Muzzle_mg', 'Muzzle_mg.001'], True),
    # Wave 1 (the roof-gun rule): the raised post, its cradle and the big ammunition can.
    ('pintle_mg_post', lambda a: K.pintle_mg(a, None, (0, 0, 0), post=.5), (None, None, None), 900,
     ['Mount_mg', 'Muzzle_mg', 'MG_post', 'MG_cradle', 'MG_ammo'], True),
    # Wave 2 (lane B's request): the riser collar under the post, as on a hatch ring.
    ('pintle_mg_riser', lambda a: K.pintle_mg(a, None, (0, 0, 0), post=.3, riser=.16), (None, None, None), 1300,
     ['Mount_mg', 'Muzzle_mg', 'MG_riser', 'MG_post', 'MG_cradle', 'MG_ammo'], True),
    ('smoke_dischargers', lambda a: K.smoke_dischargers(a, .5, 0, 1, 1), (None, None, None), 500, ['Smoke_launchers'],
     True),
    ('era_bricks', lambda a: K.era_bricks(a, (0, 0, 1), (1, 0, 0), (0, 1, 0), 4, 3), (1.3, .7, None), 2500,
     ['Era_bricks', 'Kit_bolts'], True),
    ('era_bricks_plain', lambda a: K.era_bricks(a, (0, 0, 1), (1, 0, 0), (0, 1, 0), 4, 3, bolts=False), (1.3, .7, None),
     700, ['Era_bricks'], True),
    ('slat_cage', lambda a: K.slat_cage(a, (0, -1, 0), (0, 1, 0), .5, .8, (1, 0, 0)), (None, 2.04, None), 900,
     ['Slat_armour'], False),
    ('net_armour', lambda a: K.net_armour(a, (0, -1, 0), (0, 1, 0), .5, .8, (1, 0, 0)), (None, 2.04, None), 1500,
     ['Net_armour'], False),
    ('truck_wheel', lambda a: K.truck_wheel(a, (0, 0, .5), .5, .3, 1), (None, 1.0, 1.0), 1600,
     ['Tyres', 'Wheels', 'Wheel_nuts'], True),
    # Wave 2 (lane B's request): the lean tyre, about 250 triangles.
    ('tread_wheel', lambda a: K.tread_wheel(a, (0, 0, .5), .5, .3, 1), (None, 1.0, 1.0), 400, ['Tyres', 'Wheels', 'Hubs'],
     True),
    ('axle', lambda a: K.axle(a.part('Axles', 'Undercarriage'), 0, .5, .9), (1.8, None, None), 300, ['Axles'], True),
    ('leaf_spring', lambda a: K.leaf_spring(a.part('Suspension', 'Steel'), 0, 0, .6, 1.2), (None, 1.25, None), 200,
     ['Suspension'], False),
    ('windscreen', lambda a: K.windscreen(a, [(-.7, 0, 1), (.7, 0, 1), (.65, .3, 1.6), (-.65, .3, 1.6)]),
     (None, None, None), 300, ['Glass', 'Window_frames', 'Wipers'], False),
    ('mirror', lambda a: K.mirror(a.part('Mirrors', 'Steel'), (0, 0, 1), 1), (None, None, None), 100, ['Mirrors'],
     False),
    ('outrigger', lambda a: K.outrigger(a.part('Outriggers', 'Armor'), a.part('Outrigger_pads', 'Steel'), (1, 0, 1),
                                        1), (None, None, None), 300, ['Outriggers', 'Outrigger_pads'], True),
    ('wing', lambda a: K.wing(a.part('Wings', 'Team'), (-1.0, 4.0), (1.5, 1.2), 5.0, x0=.8, t=.06),
     (11.6, 4.0, None), 200, ['Wings'], False),
    ('fin', lambda a: K.fin(a.part('Fins', 'Team'), (0, 3.0), (1.6, 1.0), 3.0), (None, 3.0, 3.0), 100, ['Fins'], False),
    ('intake', lambda a: K.intake(a.part('Intakes', 'Team'), a.part('Intake_dark', 'Undercarriage'), (0, 0, 1), .8,
                                  .6, 1.0), (.8, 1.0, .6), 300, ['Intakes'], True),
    ('missile', lambda a: K.missile(a, (0, 0, 1), .09, 2.9), (None, 2.95, None), 600,
     ['Missiles', 'Missile_fins', 'Missile_seekers'], True),
    ('bomb', lambda a: K.bomb(a, (0, 0, 1), .14, 2.2), (None, None, None), 400, ['Bombs_body', 'Bomb_fins'], True),
    ('drop_tank', lambda a: K.drop_tank(a.part('Drop_tanks', 'Steel'), (0, 0, 1), .3, 3.0), (.6, 3.0, .6), 300,
     ['Drop_tanks'], True),
    ('flare_dispenser', lambda a: K.flare_dispenser(a, (0, 0, 1)), (None, None, None), 300,
     ['Flares', 'Flare_mouths'], False),
    ('landing_gear', lambda a: K.landing_gear(a, (0, 0, 1.5), twin=True), (None, None, None), 700,
     ['Gear', 'Gear_tyres'], True),
    ('skids', lambda a: K.skids(a.part('Skids', 'Steel'), 1.0, -2, 2, 0), (2.1, None, None), 400, ['Skids'], False),
    ('stub_wing', lambda a: K.stub_wing(a.part('Stub_wing', 'Team'), .6, 1.4, -.2, .9, 1.5), (None, None, None), 100,
     ['Stub_wing'], False),
    ('ship_hull', lambda a: K.ship_hull(a.part('Hull', 'Team'), 40, 6, 3), (6.0, 40.1, None), 300, ['Hull'], False),
    ('railing', lambda a: K.railing(a.part('Railings', 'Steel'), [(0, 0, 0), (4, 0, 0), (4, 3, 0)]),
     (None, None, 1.0), 900, ['Railings'], False),
    ('ladder', lambda a: K.ladder(a.part('Ladders', 'Steel'), (0, 0, 0), (0, .4, 3)), (None, None, None), 600,
     ['Ladders'], False),
    ('vls', lambda a: K.vls(a, (0, 0, 1), 4, 2), (2.5, 1.3, None), 600, ['Vls', 'Vls_hatches'], True),
    ('ciws', lambda a: K.ciws(a, 'ciws', (0, 0, 0)), (None, None, None), 900,
     ['Ciws_base', 'Ciws_body', 'Mount_ciws', 'Muzzle_ciws'], True),
    ('rhib', lambda a: K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (0, 0, 0)), (None, None, None),
     900, ['Boats', 'Boat_tubes'], True),
    ('radar_mast', lambda a: K.radar_mast(a, (0, 0, 0)), (None, None, None), 1200, ['Mast', 'Radar', 'Radar_array'],
     True),
    ('rail_track', lambda a: K.rail_track(a.part('Rails', 'Steel'), a.part('Sleepers', 'Concrete'), 6.0),
     (2.6, 6.0, None), 900, ['Rails', 'Sleepers'], True),
    ('bogie', lambda a: K.bogie(a, (0, 0, 0)), (None, None, None), 1600, ['Bogies', 'Rail_wheels'], True),
    ('footing_hegemon', lambda a: K.footing(a, (4, 4, .4), (0, 0, .2), 'hegemon'), (4.0, 4.0, .4), 400, ['Base'], True),
    ('footing_accord', lambda a: K.footing(a, (4, 4, .4), (0, 0, .2), 'accord'), (None, None, None), 600,
     ['Base', 'Base_timbers'], True),
    ('sandbag_wall', lambda a: K.sandbag_wall(a, [(-2, 0, 0), (2, 0, 0)], layers=3), (None, None, None), 2500,
     ['Sandbags'], True),
    ('wire_fence', lambda a: K.wire_fence(a, [(-3, 0, 0), (3, 0, 0)]), (None, None, None), 2500, ['Kit_fence'], False),
    ('hesco', lambda a: K.hesco(a, (0, 0, 0), cells=2), (2.15, 1.1, 1.38), 600, ['Hesco', 'Hesco_mesh'], True),
    ('t_wall', lambda a: K.t_wall(a, (0, 0, 0)), (1.5, 1.2, None), 400, ['Wall'], True),
    ('floodlight', lambda a: K.floodlight(a, (0, 0, 0)), (None, None, None), 300, ['Light_poles', 'Lamps'], True),
    ('door', lambda a: K.door(a, (0, 0, 0)), (None, None, None), 300, ['Doors', 'Door_frames'], True),
    ('beacon', lambda a: K.beacon(a, (0, 0, 0)), (None, None, None), 200, ['Beacons'], False),
    ('armour_plate', lambda a: K.armour_plate(a, a.part('Plates', 'Armor'), (3, 2, .2), (0, 0, .1)), (3.0, 2.0, None),
     900, ['Plates', 'Kit_rivets'], True),
    ('breakable_panel', lambda a: K.breakable_panel(a, 'Part_engine', (2, 1.5, .2), (0, 0, 1)), (None, None, None), 900,
     ['Part_engine', 'Part_engine_plates'], True),
    ('fuel_drum', lambda a: K.fuel_drum(a.part('Drums', 'BarrelRed'), a.part('Drum_bands', 'Steel'), (0, 0, 0)),
     (.6, .6, .88), 300, ['Drums'], True),
    ('smokestack', lambda a: K.smokestack(a, (0, 0, 0)), (None, None, 2.0), 300, ['Stacks'], True),
    ('gun_cluster', lambda a: K.gun_cluster(a, 'Mount_gun', (0, 0, 1), barrels=3), (None, None, None), 3000,
     ['Mount_gun', 'Muzzle_gun', 'Muzzle_gun.001', 'Muzzle_gun.002'], True),
    # Wave 5 (lane B's wave 3 requests, lifted from mb_p35b_parts): runs of sandbags, earth pads, nets, track runs.
    ('door_frame_mat', lambda a: K.door(a, (0, 0, 0), frame_mat='Armor'), (None, None, None), 300,
     ['Doors', 'Door_frames'], True),
    ('sandbag_run', lambda a: K.sandbag_run(a, [(0, 0, 0), (3, 0, 0)], courses=2, part='Parapet'), (None, None, None),
     900, ['Parapet'], True),
    ('sandbag_run_lean', lambda a: K.sandbag_run(a, [(0, 0, 0), (3, 0, 0)], courses=2, lean=True), (None, None, None),
     600, ['Sandbags'], True),
    ('earth_pad', lambda a: K.earth_pad(a, [(-2, -2), (2, -2), (2, 2), (-2, 2)], .4, bottom=False), (4.0, 4.0, .4),
     200, ['Base'], True),
    ('camo_net', lambda a: K.camo_net(a, [(-2, -2, 2), (2, -2, 2), (2, 2, 2), (-2, 2, 2)], .3, 0, garnish=6),
     (None, None, None), 400, ['Camo_net', 'Net_poles'], False),
    ('track_run', lambda a: K.track_run(a, 1.2, .5, [-1.5, -.5, .5, 1.5], .3, (2.0, .55, .25), (-2.0, .5, .22),
                                        rollers=(-1, 1), roller_z=.75), (None, None, None), 4000,
     ['Tracks', 'Track_links', 'Wheels', 'Sprockets', 'Idlers'], True),
    # Wave 5 (lane C's wave 4 helpers, lifted from mb_p35c_parts): bodies through sections, the lean store.
    ('section_loft', lambda a: K.section_loft(a.part('Hull', 'Team'), [(-2, K.ellipse_half(.8, .5, .6)),
                                                                       (2, K.ellipse_half(1.0, .6, .7))]),
     (2.0, 4.0, None), 200, ['Hull'], False),
    ('slab_loft', lambda a: K.slab_loft(a.part('Turret_body', 'Team'), [(-1, -1), (1, -1), (1, 1), (-1, 1)],
                                        [(-.8, -.8), (.8, -.8), (.8, .8), (-.8, .8)], 0, .5), (2.0, 2.0, .5), 50,
     ['Turret_body'], False),
    ('store_missile', lambda a: K.store(a, (0, 1, 1), .08, 1.8), (None, None, None), 300, ['Missiles', 'Missile_fins'],
     False),
    ('store_bomb', lambda a: K.store(a, (0, 1, 1), .15, 1.5, body='Bombs', kind='bomb'), (None, None, None), 300,
     ['Bombs', 'Missile_fins'], False),
]


def bounds(objs):
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for ob in objs:
        if ob.type != 'MESH':
            continue
        off = K._world_offset(ob)
        for v in ob.data.vertices:
            p = off + v.co
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return [h - l for l, h in zip(lo, hi)] if lo[0] < math.inf else [0, 0, 0]


def run_case(root, case):
    name, build, size, ceiling, names, bevelled = case
    kit.clear_workspace(root)
    a = kit.Asset(f'kit35_{name}', root, ao_samples=12)
    build(a)
    worn = any(any(v[sh.wear] > 0 for v in sh.bm.verts) for sh in a.shapes.values() if sh.bm.verts)
    k.clean(a)
    degenerate = k.degenerate_triangles(a)
    a.finish()
    objs = list(a.collection.objects)
    got = bounds(objs)
    tris = a.triangles()
    have = {o.name for o in objs}
    fails = []
    if size:
        for axis, want in enumerate(size):
            if want is not None and abs(got[axis] - want) > .15 * want:
                fails.append(f'size {"xyz"[axis]} {got[axis]:.3f} vs {want}')
    if tris > ceiling:
        fails.append(f'triangles {tris} > {ceiling}')
    if tris == 0:
        fails.append('no geometry')
    missing = [n for n in names if n not in have]
    if missing:
        fails.append('missing ' + ', '.join(missing))
    if bevelled and not worn:
        fails.append('no chamfer (no worn vertices)')
    if degenerate:
        fails.append(f'{degenerate} zero-area triangles')
    no_col = [o.name for o in objs if o.type == 'MESH' and not o.data.color_attributes]
    if no_col:
        fails.append('no COLOR_0 on ' + ', '.join(no_col[:3]))
    return {'component': name, 'triangles': tris, 'size': [round(x, 3) for x in got], 'fails': fails}, a


def catalog(root, results):
    """All components on one grid, Workbench render from the battle angle with labels."""
    kit.clear_workspace(root)
    scene = bpy.context.scene
    cols = 9
    pitch = 7.0
    for i, case in enumerate(CASES):
        a = kit.Asset(f'cat_{case[0]}', root, ao_samples=12)
        case[1](a)
        k.clean(a)
        a.finish()
        size = max(results[i]['size']) or 1
        s = max(.3, min(12.0, 3.2 / size))
        x, y = (i % cols) * pitch, -(i // cols) * pitch
        for o in a.collection.objects:
            if o.parent is None:
                o.scale = (s, s, s)
                o.location = (o.location.x * s + x, o.location.y * s + y, o.location.z * s)
        curve = bpy.data.curves.new(f'label_{case[0]}', 'FONT')
        curve.body = case[0]
        curve.size = .55
        label = bpy.data.objects.new(f'label_{case[0]}', curve)
        label.location = (x - 2.8, y - 3.2, 0)
        a.collection.objects.link(label)
    rows = (len(CASES) + cols - 1) // cols
    cam_data = bpy.data.cameras.new('cat_cam')
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = cols * pitch * 1.02
    cam = bpy.data.objects.new('cat_cam', cam_data)
    root.objects.link(cam)
    cx, cy = (cols - 1) * pitch / 2, -(rows - 1) * pitch / 2
    cam.location = (cx, cy - 60, 60)
    cam.rotation_euler = (math.radians(45), 0, 0)
    scene.camera = cam
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'VERTEX'
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = 2400
    scene.render.resolution_y = int(2400 * rows / cols * .78) + 120
    scene.render.film_transparent = False
    CATALOG.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(CATALOG / 'kit35_catalog.png')
    bpy.ops.render.render(write_still=True)
    for o in list(bpy.data.objects):
        if o.name.startswith(('label_', 'cat_cam')):
            data = o.data
            bpy.data.objects.remove(o)
            (bpy.data.curves if isinstance(data, bpy.types.Curve) else bpy.data.cameras).remove(data)


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o)
    root = kit.workspace()
    results, failed = [], 0
    for case in CASES:
        try:
            res, _ = run_case(root, case)
        except Exception as exc:  # a crash is a failure of that component
            res = {'component': case[0], 'triangles': 0, 'size': [0, 0, 0], 'fails': [f'error: {exc!r}']}
        results.append(res)
        failed += bool(res['fails'])
        print(f"KIT35 {'FAIL' if res['fails'] else 'ok  '} {res['component']:18s} tris {res['triangles']:5d} "
              f"size {res['size']} {'; '.join(res['fails'])}")
    print(f'KIT35 {len(results) - failed}/{len(results)} components pass')
    if '--catalog' in args:
        catalog(root, results)
        (CATALOG / 'kit35_components.json').write_text(json.dumps(results, indent=1) + '\n', encoding='utf-8')
    kit.clear_workspace(root)
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
