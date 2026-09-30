"""Before/after model shots for the model rebuilds (prompt 25 B2), rendered on the CPU with Cycles so the GPU the
Android emulator uses is left alone.

  blender -b --python Tools/blender/model_shots.py -- <out_dir> <tag> <frame_m> <glb>[@scale] [<glb>[@scale] ...]

For every GLB it writes <out_dir>/<name>_<tag>_top.png, a top-down silhouette (black on white), and
<out_dir>/<name>_<tag>_game.png, the battle camera's view (orthographic, 52 degrees down, 45 degrees off the nose,
RtsCamera's angle) lit like a match. frame_m is the width of the view in metres, the same for every shot of a model
so the before and after compare at one scale; @scale draws a GLB at its balance.json "scale" (its size in battle). Tools/art/model_sheet.py lays the four shots out on one sheet.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

TEAM = (122 / 255, 150 / 255, 84 / 255)      # TeamColors.Main(0), the default palette's olive
TEAM_GLOW = (0.55, 0.95, 0.62)
SIZE = 420


def lin(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def load(glb, scale):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    for o in bpy.context.scene.objects:
        if o.parent is None:
            o.scale = [c * scale for c in o.scale]
            o.location = [c * scale for c in o.location]
    bpy.context.view_layer.update()
    for m in bpy.data.materials:
        base = m.name.split('.')[0]
        if base not in ('Team', 'TeamGlow') or not m.use_nodes:
            continue
        bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None:
            continue
        colour = (*lin(TEAM if base == 'Team' else TEAM_GLOW), 1.0)
        # The kit multiplies vertex colour (baked AO) into the base colour; keep the multiply, swap the colour.
        for n in m.node_tree.nodes:
            if n.type == 'MIX' and n.data_type == 'RGBA':
                b = next(s for s in n.inputs if s.identifier == 'B_Color')
                b.default_value = colour
        if not bsdf.inputs['Base Color'].is_linked:
            bsdf.inputs['Base Color'].default_value = colour
        if base == 'TeamGlow':
            bsdf.inputs['Emission Color'].default_value = colour
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                lo = Vector(map(min, lo, w))
                hi = Vector(map(max, hi, w))
    return lo, hi


def scene_setup(silhouette):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = 1 if silhouette else 48
    s.cycles.use_denoising = not silhouette
    s.render.resolution_x = s.render.resolution_y = SIZE
    s.render.film_transparent = False
    s.view_settings.view_transform = 'Standard' if silhouette else 'AgX'
    s.view_settings.exposure = 0.0 if silhouette else 0.35
    world = bpy.data.worlds.new('Shots')
    s.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (1, 1, 1, 1) if silhouette else (*lin((0.76, 0.85, 0.84)), 1)
    bg.inputs['Strength'].default_value = 1.0 if silhouette else 0.55
    if silhouette:
        black = bpy.data.materials.new('Silhouette')
        black.use_nodes = True
        nt = black.node_tree
        for n in list(nt.nodes):
            if n.type != 'OUTPUT_MATERIAL':
                nt.nodes.remove(n)
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (0, 0, 0, 1)
        nt.links.new(em.outputs['Emission'], nt.nodes['Material Output'].inputs['Surface'])
        bpy.context.view_layer.material_override = black
    else:
        sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
        sun.data.energy = 3.2
        sun.data.color = lin((1.0, 0.88, 0.69))
        sun.data.angle = math.radians(3)
        sun.rotation_euler = Euler((math.radians(42), 0, math.radians(-30)))
        s.collection.objects.link(sun)
        bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -0.02))
        ground = bpy.context.active_object
        mat = bpy.data.materials.new('Ground')
        mat.use_nodes = True
        p = mat.node_tree.nodes['Principled BSDF']
        p.inputs['Base Color'].default_value = (*lin((0.47, 0.5, 0.38)), 1)
        p.inputs['Roughness'].default_value = 0.95
        ground.data.materials.append(mat)


def camera(lo, hi, frame, top):
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = frame
    cam.data.clip_end = 2000
    centre = (lo + hi) / 2
    if top:
        cam.location = (centre.x, centre.y, hi.z + 50)
        cam.rotation_euler = Euler((0, 0, 0))
    else:
        # RtsCamera: pitch 52 degrees down; the model's nose (-Y) turned 45 degrees across the view.
        pitch, side = math.radians(52), math.cos(math.radians(45))
        d = Vector((-side * math.cos(pitch), -side * math.cos(pitch), math.sin(pitch)))  # front right, above
        cam.location = centre + d * 200
        cam.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    out, tag, frame = Path(args[0]), args[1], float(args[2])
    out.mkdir(parents=True, exist_ok=True)
    for item in args[3:]:
        path, _, scale = item.partition('@')
        glb = Path(path)
        for top in (True, False):
            lo, hi = load(glb, float(scale or 1))
            scene_setup(top)
            camera(lo, hi, frame, top)
            path = out / f'{glb.stem}_{tag}_{"top" if top else "game"}.png'
            bpy.context.scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            print(f'SHOT {path} size {hi.x - lo.x:.2f} x {hi.y - lo.y:.2f} x {hi.z - lo.z:.2f}')
    print('SHOTS_DONE')


main()
