"""Build every Machine Brigade model into Assets/MachineBrigade/Resources/Models/<name>.glb.

Headless (from the repository root):
  blender --background --python Tools/blender/build_assets.py            # everything
  blender --background --python Tools/blender/build_assets.py -- tank    # names containing "tank"
Also writes Docs/art/models.json (triangle counts). Blender is only needed to change the art;
the committed GLB files are all Unity needs.

The most-seen vehicles also get a high-detail variant, <name>_hd.glb: the same builder run with
detail=True (see mb_detail.py), which the high graphics tiers load instead (ModelLibrary.HighDetail).
  blender --background --python Tools/blender/build_assets.py -- apc_hd   # one variant
  blender --background --python Tools/blender/build_assets.py -- _hd      # every variant
"""
import functools
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import frontier_kit as kit  # noqa: E402
import mb_air  # noqa: E402
import mb_artillery  # noqa: E402
import mb_air2  # noqa: E402
import mb_air3  # noqa: E402
import mb_boss_saucer  # noqa: E402
import mb_bosses  # noqa: E402
import mb_bosses2  # noqa: E402
import mb_munitions  # noqa: E402
import mb_round6  # noqa: E402
import mb_elites  # noqa: E402
import mb_fortress  # noqa: E402
import mb_harbor  # noqa: E402
import mb_mapkit  # noqa: E402
import mb_new_tracked  # noqa: E402
import mb_new_trucks  # noqa: E402
import mb_new_wheeled  # noqa: E402
import mb_p16_arms  # noqa: E402
import mb_p17_temp  # noqa: E402
import mb_phase2  # noqa: E402
import mb_phase8  # noqa: E402
import mb_props  # noqa: E402
import mb_siege  # noqa: E402
import mb_support  # noqa: E402
import mb_terrain  # noqa: E402
import mb_themes  # noqa: E402
import mb_themes2  # noqa: E402
import mb_towers3  # noqa: E402
import mb_town  # noqa: E402
import mb_vehicles  # noqa: E402
import mb_vehicles2  # noqa: E402
import mb_vehicles3  # noqa: E402

ROOT = HERE.parents[1]
OUT = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'
REPORT = ROOT / 'Docs' / 'art' / 'models.json'
# Vehicles with a high-detail variant: <name>_hd is the builder called with detail=True.
HIGH_DETAIL = ('main_battle_tank', 'light_tank', 'heavy_tank', 'apc', 'scout_jeep', 'aa_vehicle', 'artillery',
               'tank_destroyer', 'attack_helicopter', 'attack_jet', 'fighter_jet', 'sky_gunship')


def all_builders():
    builders = {**mb_vehicles.BUILDERS, **mb_air.BUILDERS, **mb_air2.BUILDERS, **mb_props.BUILDERS,
                **mb_terrain.BUILDERS, **mb_town.BUILDERS, **mb_themes.BUILDERS, **mb_harbor.BUILDERS,
                **mb_vehicles2.BUILDERS, **mb_bosses.BUILDERS, **mb_elites.BUILDERS, **mb_vehicles3.BUILDERS,
                **mb_support.BUILDERS, **mb_air3.BUILDERS, **mb_siege.BUILDERS, **mb_themes2.BUILDERS,
                **mb_mapkit.BUILDERS, **mb_artillery.BUILDERS, **mb_fortress.BUILDERS,
                **mb_new_wheeled.BUILDERS, **mb_new_trucks.BUILDERS, **mb_new_tracked.BUILDERS,
                **mb_boss_saucer.BUILDERS, **mb_munitions.BUILDERS, **mb_towers3.BUILDERS,
                # Round 6 rebuilt some models (Ka-52, Su-25, siege tank, bosses with every mount): theirs win.
                **mb_round6.BUILDERS, **mb_bosses2.BUILDERS, **mb_phase2.BUILDERS, **mb_phase8.BUILDERS,
                # Prompt 16: new weapon parts on five bosses; they wrap the builders above.
                **mb_p16_arms.BUILDERS,
                # Prompt 17's temporary stand-ins for the new units (asset debt).
                **mb_p17_temp.BUILDERS}
    for name in HIGH_DETAIL:
        build, options = builders[name]
        builders[f'{name}_hd'] = (functools.partial(build, detail=True), options)
    # A round 6 builder's own high-detail variant (attack_jet_hd) over the generic one.
    builders.update({k: v for k, v in mb_round6.BUILDERS.items() if k.endswith('_hd')})
    return builders


def build_all(filters=()):
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o)
    root = kit.workspace()
    kit.clear_workspace(root)
    OUT.mkdir(parents=True, exist_ok=True)
    builders = all_builders()
    report = json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() else {}
    for name, (build, options) in builders.items():
        if filters and not any(f in name for f in filters):
            continue
        asset = kit.Asset(name, root, **options)
        build(asset)
        asset.finish()
        asset.export(OUT / f'{name}.glb')
        report[name] = {'file': f'{name}.glb', 'triangles': asset.triangles()}
        print(f'BUILT {name}: {asset.triangles()} triangles')
        # Blender object names are global: clear this asset so the next one gets clean names
        # ("Turret", not "Turret.001"), which the runtime looks up.
        kit.clear_workspace(root)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(dict(sorted(report.items())), indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    build_all(tuple(args))
    print('MB_ASSETS_COMPLETE')
