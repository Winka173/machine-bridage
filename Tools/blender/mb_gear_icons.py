"""Machine Brigade equipment icons: each equipment piece modelled with the frontier kit (so it
shares the vehicles' bevels, materials and baked occlusion) and rendered on a transparent
background for the arsenal's item tiles. Rarity is not in the render: the game draws it as the
tile's frame, glow and pips, so one render serves every rarity.

  blender --background --python Tools/blender/mb_gear_icons.py [-- <item> ...]

Writes Assets/MachineBrigade/Resources/UI/Gear/gear_<item>.png (256 x 256).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frontier_kit as fk  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Gear'
TEAM = (0.13, 0.19, 0.06, 1)  # olive, the player's colour (linear)
R90 = math.pi / 2
ALONG_X = (0, R90, 0)   # cylinder axis (local Z) along X
ALONG_Y = (R90, 0, 0)   # cylinder axis along Y


def gun(a):
    """Main gun upgrade: barrel with thermal sleeve bands, fume extractor and muzzle brake on a mantlet."""
    mantlet, barrel, steel, bore = a.part('Mantlet', 'Team'), a.part('Barrel', 'Armor'), a.part('Brake', 'Steel'), a.part('Bore', 'Undercarriage')
    mantlet.box((1.1, 1.0, 0.95), loc=(-0.2, 0, 0.5), bevel=0.14)
    mantlet.box((0.5, 0.7, 0.6), loc=(0.45, 0, 0.5), bevel=0.08, taper=(0.8, 0.8))
    barrel.cyl(0.17, 2.3, loc=(1.75, 0, 0.5), rot=ALONG_X, seg=22)
    for x in (0.95, 1.25, 2.3, 2.6):
        barrel.cyl(0.21, 0.16, loc=(x, 0, 0.5), rot=ALONG_X, seg=22)
    barrel.cyl(0.28, 0.55, loc=(1.75, 0, 0.5), rot=ALONG_X, seg=22, bevel=0.06)
    steel.box((0.5, 0.5, 0.42), loc=(3.05, 0, 0.5), bevel=0.06)
    steel.box((0.12, 0.62, 0.26), loc=(3.05, 0, 0.5), bevel=0.02)
    bore.cyl(0.11, 0.03, loc=(3.31, 0, 0.5), rot=ALONG_X, seg=16, bevel=0)


def loader(a):
    """Autoloader: a carousel of shells round a hub, with the rammer arm."""
    tray, brass, tips, hub, arm = (a.part('Tray', 'Armor'), a.part('Shells', 'Gilded'), a.part('Tips', 'Undercarriage'),
                                   a.part('Hub', 'Steel'), a.part('Rammer', 'Team'))
    tray.cyl(1.05, 0.2, loc=(0, 0, 0.1), seg=36, bevel=0.05)
    hub.cyl(0.28, 0.9, loc=(0, 0, 0.55), seg=20, bevel=0.04)
    for k in range(10):
        t = k / 10 * math.tau
        x, y = math.cos(t) * 0.74, math.sin(t) * 0.74
        brass.cyl(0.13, 0.95, loc=(x, y, 0.68), seg=14, bevel=0.02)
        tips.cyl(0.13, 0.3, r2=0.035, loc=(x, y, 1.3), seg=14, bevel=0.01)
    arm.box((0.26, 1.7, 0.26), loc=(0, -1.35, 0.9), bevel=0.06)
    arm.box((0.5, 0.4, 0.5), loc=(0, -2.1, 0.9), bevel=0.08)


def armor(a):
    """Armour kit: two thick bolted plates, the front one sloped."""
    plate, bolts = a.part('Plates', 'Team'), a.part('Bolts', 'Steel')
    plate.box((2.2, 0.3, 1.5), loc=(0, 0.25, 0.8), rot=(-0.25, 0, 0), bevel=0.08)
    plate.box((1.9, 0.28, 1.2), loc=(0.25, -0.2, 0.62), rot=(-0.45, 0, 0.12), bevel=0.08)
    # The front plate leans back 0.45 rad about X: its face is at local y = -0.14 from its centre.
    c, s_ = math.cos(-0.45), math.sin(-0.45)
    for x in (-0.6, 0.0, 0.6):
        for v in (-0.4, 0.4):
            ly, lz = -0.15, v
            y = -0.2 + ly * c - lz * s_
            z = 0.62 + ly * s_ + lz * c
            bolts.cyl(0.08, 0.08, loc=(x + 0.25 + v * 0.05, y, z), rot=(R90 - 0.45, 0, 0.12), seg=8, bevel=0.015)


def plating(a):
    """Composite plating: a sandwich of steel, ceramic and rubber, its cut edge showing the layers."""
    for i, (mat, thick) in enumerate((('Armor', 0.16), ('Concrete', 0.14), ('Rubber', 0.1), ('Steel', 0.14), ('Team', 0.16))):
        a.part(f'Layer{i}', mat).box((2.3, thick, 1.6), loc=(0, -0.35 + i * 0.16, 0.8), rot=(0, 0, 0.35), bevel=0.03)


def engine(a):
    """Engine: a V-block with its cylinder heads, air filter drum, exhausts and belt pulley."""
    block, heads, filt, pipe, pulley = (a.part('Block', 'Armor'), a.part('Heads', 'Steel'), a.part('Filter', 'Team'),
                                        a.part('Exhaust', 'Rust'), a.part('Pulley', 'Undercarriage'))
    block.box((1.8, 1.0, 0.8), loc=(0, 0, 0.45), bevel=0.08)
    for s in (-1, 1):
        heads.box((1.7, 0.5, 0.38), loc=(0, s * 0.42, 1.0), rot=(s * 0.55, 0, 0), bevel=0.06)
        for k in range(4):
            pipe.cyl(0.07, 0.42, loc=(-0.6 + k * 0.4, s * 0.78, 1.05), rot=(s * 1.1, 0, 0), seg=10)
    filt.cyl(0.42, 0.34, loc=(0, 0, 1.45), seg=28, bevel=0.06)
    pulley.cyl(0.34, 0.14, loc=(1.0, 0, 0.5), rot=ALONG_X, seg=24, bevel=0.03)
    pulley.cyl(0.2, 0.16, loc=(1.0, 0, 0.95), rot=ALONG_X, seg=20, bevel=0.03)


def repair(a):
    """Field repair kit: a red toolbox with its handle, and a spanner beside it."""
    box, steel, dark = a.part('Toolbox', 'BarrelRed'), a.part('Tools', 'Steel'), a.part('Latch', 'Undercarriage')
    box.box((1.7, 0.85, 0.72), loc=(0, 0, 0.36), bevel=0.06)
    box.box((1.74, 0.89, 0.12), loc=(0, 0, 0.78), bevel=0.04)
    for x in (-0.55, 0.55):
        dark.box((0.16, 0.06, 0.18), loc=(x, -0.46, 0.66), bevel=0.02)
    steel.tube([(-0.45, 0, 0.84), (-0.45, 0, 1.12), (0.45, 0, 1.12), (0.45, 0, 0.84)], 0.05, seg=10)
    steel.limb((-0.4, -1.05, 0.05), (1.3, -0.75, 0.05), 0.16, 0.07, bevel=0.02)
    steel.torus(0.2, 0.06, loc=(1.42, -0.73, 0.06), seg=18, ring=8)
    steel.torus(0.16, 0.055, loc=(-0.55, -1.08, 0.06), seg=18, ring=8)


def reactive(a):
    """Reactive armour: a grid of explosive bricks on a backing plate, each with its warning band."""
    back, bricks, band = a.part('Backing', 'Armor'), a.part('Bricks', 'Team'), a.part('Bands', 'Hazard')
    back.box((2.3, 0.14, 1.7), loc=(0, 0.2, 0.85), rot=(-0.3, 0, 0), bevel=0.04)
    for i in range(3):
        for j in range(3):
            x, z = -0.75 + i * 0.75, 0.3 + j * 0.55
            y = 0.02 - z * 0.3
            bricks.box((0.66, 0.24, 0.46), loc=(x, y, z + 0.05), rot=(-0.3, 0, 0), bevel=0.05)
            band.box((0.67, 0.25, 0.07), loc=(x, y - 0.005, z + 0.2), rot=(-0.3, 0, 0), bevel=0.01)


def autorepair(a):
    """Auto-repair system: a jointed arm on a turntable, its welding tip glowing."""
    base, arm, joint, tip = a.part('Base', 'Armor'), a.part('Arm', 'Team'), a.part('Joints', 'Steel'), a.part('Torch', 'Energy')
    base.cyl(0.7, 0.3, loc=(0, 0, 0.15), seg=28, bevel=0.06)
    joint.cyl(0.3, 0.3, loc=(0, 0, 0.45), seg=20, bevel=0.05)
    arm.limb((0, 0, 0.5), (0.35, 0, 1.6), 0.3, 0.3, bevel=0.07)
    joint.cyl(0.2, 0.42, loc=(0.35, 0, 1.6), rot=ALONG_Y, seg=18, bevel=0.04)
    arm.limb((0.35, 0, 1.6), (1.35, 0, 1.2), 0.24, 0.24, bevel=0.06)
    joint.cyl(0.14, 0.34, loc=(1.35, 0, 1.2), rot=ALONG_Y, seg=16, bevel=0.03)
    # The nozzle points down and forward from the wrist; the flame sits at its tip.
    joint.limb((1.35, 0, 1.2), (1.62, 0, 0.84), 0.12, 0.12, bevel=0.03, taper=(0.55, 0.55))
    tip.sphere(0.11, loc=(1.66, 0, 0.78), seg=12, rings=8)


def crew(a):
    """Veteran crew: a padded tanker's helmet with goggles and a gold star."""
    helmet, pads, glass, rim, star = (a.part('Helmet', 'Team'), a.part('Pads', 'Rubber'), a.part('Lenses', 'Glass'),
                                      a.part('Rims', 'Steel'), a.part('Star', 'Gilded'))
    helmet.lathe([(0.0, 1.55), (0.35, 1.52), (0.62, 1.4), (0.8, 1.15), (0.86, 0.85), (0.84, 0.55), (0.8, 0.45)], seg=32, bevel=0.02)
    for s in (-1, 1):
        pads.box((0.26, 0.5, 0.55), loc=(s * 0.82, 0.05, 0.62), bevel=0.1)
        glass.cyl(0.19, 0.1, loc=(s * 0.26, -0.8, 1.08), rot=(R90 + 0.2, 0, 0), seg=18, bevel=0.02)
        rim.torus(0.2, 0.045, loc=(s * 0.26, -0.84, 1.08), rot=(R90 + 0.2, 0, 0), seg=18, ring=6)
    rim.box((0.18, 0.06, 0.06), loc=(0, -0.86, 1.08), bevel=0.01)
    points = []
    for k in range(10):
        t = math.pi / 2 + k * math.pi / 5
        r = 0.3 if k % 2 == 0 else 0.13
        points.append((math.cos(t) * r, math.sin(t) * r))
    star.prism(points, 0.08, loc=(0, -0.66, 1.34), rot=(-0.75, 0, 0), axis='Y', bevel=0.01)


def smoke(a):
    """Smoke dischargers: four launch tubes on a bracket, their caps off."""
    bracket, tubes, caps, puff = a.part('Bracket', 'Armor'), a.part('Tubes', 'Team'), a.part('Caps', 'Rubber'), a.part('Puff', 'Concrete')
    bracket.box((1.8, 0.7, 0.3), loc=(0, 0, 0.15), bevel=0.06)
    bracket.box((1.7, 0.2, 0.7), loc=(0, 0.3, 0.5), bevel=0.05)
    for i in range(4):
        x = -0.6 + i * 0.4
        tubes.cyl(0.15, 0.85, loc=(x, -0.05, 0.75), rot=(-0.7, 0, (i - 1.5) * 0.12), seg=18, bevel=0.03)
        caps.cyl(0.11, 0.03, loc=(x + (i - 1.5) * 0.05, -0.33, 1.1), rot=(-0.7, 0, 0), seg=16, bevel=0)
    puff.ico(0.32, loc=(0.25, -0.75, 1.55), sub=2, jitter=0.1, seed=3.0)
    puff.ico(0.24, loc=(-0.1, -0.9, 1.75), sub=2, jitter=0.1, seed=5.0)


ITEMS = {
    'weapon': gun, 'loader': loader, 'armor': armor, 'plating': plating, 'engine': engine, 'repair': repair,
    'reactivearmor': reactive, 'autorepair': autorepair, 'veterancrew': crew, 'smokedischarger': smoke,
}


def paint_team(mat):
    if not mat.use_nodes:
        return
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            base = n.inputs['Base Color']
            if base.is_linked:
                for s in base.links[0].from_node.inputs:
                    if s.type == 'RGBA' and not s.is_linked:
                        s.default_value = TEAM
            else:
                base.default_value = TEAM


def setup_scene():
    scene = bpy.context.scene
    for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x = scene.render.resolution_y = 256
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    world = scene.world or bpy.data.worlds.new('icons')
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.5, 0.55, 0.6, 1)
    bg.inputs['Strength'].default_value = 0.7
    for name, energy, colour, direction in (('key', 4.2, (1.0, 0.93, 0.82), (-0.6, -1.0, 1.3)),
                                            ('rim', 3.0, (0.75, 0.85, 1.0), (0.9, 1.2, 0.6))):
        light = bpy.data.lights.new(name, 'SUN')
        light.energy = energy
        light.color = colour
        light.angle = math.radians(4)
        o = bpy.data.objects.new(name, light)
        scene.collection.objects.link(o)
        o.rotation_euler = (-Vector(direction)).to_track_quat('-Z', 'Y').to_euler()
    cam = bpy.data.cameras.new('cam')
    cam.lens = 60
    co = bpy.data.objects.new('cam', cam)
    scene.collection.objects.link(co)
    scene.camera = co
    return scene, co


def render(scene, co, name, build):
    root = fk.workspace()
    a = fk.Asset(f'gear_{name}', root, ground=False)
    build(a)
    a.finish()
    objects = [o for o in a.collection.objects if o.type == 'MESH']
    for o in objects:
        for slot in o.material_slots:
            if slot.material and slot.material.name.startswith('Team'):
                paint_team(slot.material)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre, radius = (lo + hi) / 2, (hi - lo).length / 2
    direction = Vector((0.75, -1.0, 0.72)).normalized()
    fov = 2 * math.atan(36 / (2 * co.data.lens))
    co.location = centre + direction * (radius / math.sin(fov / 2) * 0.92)
    co.rotation_euler = (centre - co.location).to_track_quat('-Z', 'Y').to_euler()
    OUT.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(OUT / f'gear_{name}.png')
    bpy.ops.render.render(write_still=True)
    print('ICON_WRITTEN', scene.render.filepath)
    fk.clear_workspace(root)


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    scene, co = setup_scene()
    for name, build in ITEMS.items():
        if args and name not in args:
            continue
        render(scene, co, name, build)


main()
