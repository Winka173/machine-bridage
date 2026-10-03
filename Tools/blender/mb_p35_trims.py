"""Prompt 35 wave 2 (lane A): trim the old towers over the 1.5 x cap that no wave rebuilds (owner review of wave 1,
item 2; DECISIONS "Prompt 35 wave 2 (lane A)").

ew_tower_a, guard_tower, guard_tower_a, missile_battery, missile_battery_a and missile_battery_b keep their builders
(mb_p27_wave6 over mb_siege / mb_fortress / mb_tower_branches); after their finish (the COLOR_0 bake done) the
heaviest dense parts listed in TRIMS are reduced with Blender's collapse decimation at the given ratio, so the look,
the parts, the node names and the runtime pivots stay and each file comes under 6,000 triangles. Only these six ids
are wrapped (applied last in build_assets.all_builders, after every other wrapper).
"""
import re

import bmesh
import bpy

# model -> {mesh name (the exporter's ".NNN" suffix ignored): collapse ratio}
TRIMS = {
    'ew_tower_a': {'Jam_waves': .5, 'Footings': .5},
    'guard_tower': {'Leg_gussets': .25, 'Base_plates': .6},
    'guard_tower_a': {'Leg_gussets': .3, 'Watch_mast': .5, 'Searchlight_head': .5, 'Searchlight_yoke': .5,
                      'Base_plates': .6},
    'missile_battery': {'Sandbags': .4, 'Mast': .45, 'Platform_armor': .5, 'Shelter_blocks': .5, 'Race_band': .5,
                        'Turntable': .6, 'Plinth': .6},
    'missile_battery_a': {'Launcher_tubes': .3, 'Launcher_tubes_bore': .3, 'Sandbags': .4, 'Mast': .45,
                          'Platform_armor': .5, 'Shelter_blocks': .5, 'Race_band': .5, 'Turntable': .6, 'Plinth': .6,
                          'Radar_reflector': .6},
    'missile_battery_b': {'Sandbags': .4, 'Mast': .45, 'Platform_armor': .5, 'Shelter_blocks': .5, 'Race_band': .5,
                          'Turntable': .6, 'Plinth': .6, 'Radar_reflector': .6},
}
# Play-test 14 wave M4 (lane A): the guard towers are redrawn under the tower cap by mb_pt14_m4 (no trim).
for _redrawn in ('guard_tower', 'guard_tower_a'):
    TRIMS.pop(_redrawn)


def _clean(me):
    """Collapse can leave zero-area triangles and two faces on the same vertices: drop both kinds."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])
    seen, dup = set(), []
    for f in bm.faces:
        key = tuple(sorted(v.index for v in f.verts))
        if key in seen or f.calc_area() < 1e-8:
            dup.append(f)
        seen.add(key)
    if dup:
        bmesh.ops.delete(bm, geom=dup, context='FACES_ONLY')
    bm.to_mesh(me)
    bm.free()


def _decimate(asset, plan):
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in list(asset.collection.objects):
        if ob.type != 'MESH':
            continue
        ratio = plan.get(re.sub(r'\.\d{3}$', '', ob.name))
        if not ratio:
            continue
        mod = ob.modifiers.new('trim', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        dg.update()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        ob.modifiers.remove(mod)
        _clean(me)
        old = ob.data
        ob.data = me
        if old.users == 0:
            bpy.data.meshes.remove(old)


def wrap(builders):
    out = dict(builders)
    for name, plan in TRIMS.items():
        if name not in out:
            continue
        build, options = out[name]

        def run(a, _build=build, _plan=plan):
            _build(a)
            original = a.finish

            def finish():
                res = original()
                _decimate(a, _plan)
                return res
            a.finish = finish
        out[name] = (run, options)
    return out
