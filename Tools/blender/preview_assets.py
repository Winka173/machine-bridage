"""Render a review sheet of exported GLB models (adapted from 3d_astra's preview_assets.py).

  blender --background --python Tools/blender/preview_assets.py -- <out.png> <game|hero> <name> [<name> ...]
"game" is an orthographic view from the in-game camera direction; "hero" is a close 3/4 view.
Team materials are painted olive, the player's colour.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'
TEAM = (0.13, 0.19, 0.06, 1)  # olive #62723c, linear
GROUND = (0.2, 0.19, 0.12, 1)


def paint_team(mat):
    if not mat.use_nodes:
        return
    for n in mat.node_tree.nodes:
        if n.type != 'BSDF_PRINCIPLED':
            continue
        base = n.inputs['Base Color']
        if base.is_linked:
            for s in base.links[0].from_node.inputs:
                if s.type == 'RGBA' and not s.is_linked:
                    s.default_value = TEAM
        else:
            base.default_value = TEAM
        if mat.name.startswith('TeamGlow'):
            n.inputs['Emission Color'].default_value = (0.4, 1.0, 0.3, 1)


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    out, angle, names = args[0], args[1], args[2:]
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    scene = bpy.context.scene
    for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.view_settings.view_transform = 'AgX'
    world = scene.world or bpy.data.worlds.new('preview')
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.42, 0.47, 0.46, 1)
    bg.inputs['Strength'].default_value = 0.9

    x, placed = 0.0, []
    for name in names:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(MODELS / f'{name}.glb'))
        new = [o for o in bpy.data.objects if o not in before]
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in new if o.type == 'MESH' for c in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        for r in (o for o in new if o.parent is None):
            r.location.x += x - lo.x
        placed.append(hi.z)
        x += (hi.x - lo.x) + 1.0
        for o in new:
            if o.type == 'MESH':
                for slot in o.material_slots:
                    if slot.material and slot.material.name.startswith('Team'):
                        paint_team(slot.material)
    span = x - 1.0
    for o in bpy.data.objects:
        if o.parent is None:
            o.location.x -= span / 2

    bpy.ops.mesh.primitive_plane_add(size=400)
    ground = bpy.context.object
    gm = bpy.data.materials.new('ground')
    gm.use_nodes = True
    gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    gb.inputs['Base Color'].default_value = GROUND
    gb.inputs['Roughness'].default_value = 0.95
    ground.data.materials.append(gm)

    sun = bpy.data.lights.new('sun', 'SUN')
    sun.energy = 3.6
    sun.angle = math.radians(3)
    sun.color = (1.0, 0.9, 0.75)
    so = bpy.data.objects.new('sun', sun)
    scene.collection.objects.link(so)
    so.rotation_euler = Vector((-25, -20, 55)).to_track_quat('Z', 'Y').to_euler()

    cam = bpy.data.cameras.new('cam')
    co = bpy.data.objects.new('cam', cam)
    scene.collection.objects.link(co)
    scene.camera = co
    height = max(placed)
    if angle == 'game':
        cam.type = 'ORTHO'
        cam.ortho_scale = max(span * 1.1, height * 3.2)
        direction = Vector((22, -38, 56)).normalized()
        target = Vector((0, 0, height * .35))
        co.location = target + direction * 80
    else:
        cam.lens = 55
        direction = Vector((.55, -1.0, .5)).normalized()
        target = Vector((0, 0, height * .42))
        co.location = target + direction * max(span * 1.25, height * 2.6)
    co.rotation_euler = (target - co.location).to_track_quat('-Z', 'Y').to_euler()
    cam.clip_end = 600
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print('PREVIEW_WRITTEN', out)


main()
