"""Measures hull footprints (X width, Y length) of vehicle GLBs, ignoring everything under turrets,
mounts, rotors and propellers, so the collision capsule fits the body rather than the gun."""
import json
import sys

import bpy
from mathutils import Vector

MODELS = r'C:\Users\Winka\Projects\MachineBrigade\Assets\MachineBrigade\Resources\Models'
names = sys.argv[sys.argv.index('--') + 1:]
out = {}
SKIP = ('Turret', 'Mount_', 'Rotor', 'Tail_rotor', 'Propeller', 'Radar', 'Bombs', 'Erector', 'Searchlight')


def skipped(o):
    while o is not None:
        if o.name.startswith(SKIP):
            return True
        o = o.parent
    return False


for name in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.gltf(filepath=f'{MODELS}\\{name}.glb')
    except Exception as e:  # noqa: BLE001
        out[name] = str(e)
        continue
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or skipped(o):
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    # glTF import converts to Blender's Z-up; the model's front is -Y.
    out[name] = {'width': round(hi.x - lo.x, 2), 'length': round(hi.y - lo.y, 2), 'cy': round((hi.y + lo.y) / 2, 2)}
print('HULLS ' + json.dumps(out))
