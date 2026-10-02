"""Prompt 35: six-angle pictures of a built GLB (front, rear, side, top, 3/4 front, 3/4 rear) plus the battle angle at
the default zoom's scale, rendered with Workbench (material colours, cavity, shadows) for the before / after sheets.

    blender --background --python Tools/blender/render_angles.py -- <model.glb> <out_dir> [px]

Writes <out_dir>/<view>.png (px square, default 640) and battle.png (orthographic, pitch 52, yaw -45, 28.4 px per
metre like the battle camera's default zoom on a 1080 px screen). Tools/models/sheet.py composes them into one sheet.
The in-game picture (the game's preview scene) stays a Unity render: MachineBrigade.Editor.ModelScan.RenderBatch.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

VIEWS = {  # name: (azimuth degrees from the front, elevation degrees)
    'front': (0, 8), 'rear': (180, 8), 'side': (90, 5), 'top': (0, 89.9), 'front34': (35, 28), 'rear34': (215, 28),
}
PX_PER_M = 28.4


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    glb, out = Path(args[0]), Path(args[1])
    px = int(args[2]) if len(args) > 2 else 640
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    # Workbench's material colour is the viewport colour: copy the glTF base colour into it.
    for mat in bpy.data.materials:
        node = mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes and mat.node_tree else None
        if node is not None:
            c = node.inputs['Base Color'].default_value
            mix = mat.node_tree.nodes.get('Mix')     # the importer's base colour x COLOR_0
            if node.inputs['Base Color'].is_linked and mix is not None:
                rgba = [i for i in mix.inputs if i.type == 'RGBA' and not i.is_linked]
                if rgba:
                    c = rgba[0].default_value
            mat.diffuse_color = (c[0], c[1], c[2], 1)
            mat.metallic = 0.0
            mat.roughness = .6
    bpy.context.view_layer.update()
    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    centre, size = (lo + hi) / 2, hi - lo
    radius = size.length / 2
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.show_shadows = True
    sh.show_object_outline = False
    scene.display.shadow_focus = .4
    scene.render.film_transparent = False
    world = bpy.data.worlds.new('w')
    scene.world = world
    sh.background_type = 'VIEWPORT'
    sh.background_color = (0.16, 0.17, 0.18)
    # A ground plane under the model so the shadows read.
    bpy.ops.mesh.primitive_plane_add(size=radius * 8, location=(centre.x, centre.y, lo.z - .005))
    ground = bpy.context.active_object
    mat = bpy.data.materials.new('ground')
    mat.diffuse_color = (0.36, 0.35, 0.32, 1)
    ground.data.materials.append(mat)
    cam_data = bpy.data.cameras.new('cam')
    cam_data.type = 'ORTHO'
    cam = bpy.data.objects.new('cam', cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    def shoot(name, az, el, ortho, res):
        a, e = math.radians(az), math.radians(el)
        # The model's front is -Y: azimuth 0 looks at the front from ahead of it.
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        cam.location = centre + d * radius * 4
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        cam_data.ortho_scale = ortho
        cam_data.clip_end = radius * 10
        scene.render.resolution_x, scene.render.resolution_y = res
        scene.render.filepath = str(out / f'{name}.png')
        bpy.ops.render.render(write_still=True)

    for name, (az, el) in VIEWS.items():
        shoot(name, az, el, radius * 2.05, (px, px))
    # Battle camera: yaw -45 (from the front-left), pitch 52, at the default zoom's pixel scale.
    span = radius * 2.1
    res = max(48, int(span * PX_PER_M))
    shoot('battle', -45, 52, span, (res, res))
    print('MB_ANGLES_DONE', out)


if __name__ == '__main__':
    main()
