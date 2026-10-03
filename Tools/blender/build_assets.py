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
import mb_orbital  # noqa: E402
import mb_bosses  # noqa: E402
import mb_bosses2  # noqa: E402
import mb_munitions  # noqa: E402
import mb_naval  # noqa: E402
import mb_round6  # noqa: E402
import mb_elites  # noqa: E402
import mb_fortress  # noqa: E402
import mb_harbor  # noqa: E402
import mb_mapkit  # noqa: E402
import mb_new_tracked  # noqa: E402
import mb_new_trucks  # noqa: E402
import mb_new_wheeled  # noqa: E402
import mb_p16_arms  # noqa: E402
import mb_p20_bosses  # noqa: E402
import mb_p21_models  # noqa: E402
import mb_pt5_models  # noqa: E402
import mb_pt8_icarus  # noqa: E402
import mb_pt9_models  # noqa: E402
import mb_p22_siege  # noqa: E402
import mb_p22_content  # noqa: E402
import mb_p25_models  # noqa: E402
import mb_p25_models2  # noqa: E402
import mb_p25_new  # noqa: E402
import mb_p25_rounds  # noqa: E402
import mb_p27_experiment  # noqa: E402
import mb_p27_wave1a  # noqa: E402
import mb_p27_wave1b  # noqa: E402
import mb_p27_wave1c  # noqa: E402
import mb_p27_wave2  # noqa: E402
import mb_p27_wave3  # noqa: E402
import mb_p27_wave4  # noqa: E402
import mb_p27_wave6  # noqa: E402
import mb_p27_wave7  # noqa: E402
import mb_p27_wave8a  # noqa: E402
import mb_p27_wave5_ground  # noqa: E402
import mb_p27_wave5_air  # noqa: E402
import mb_p27_wave8b  # noqa: E402
import mb_p27_standins  # noqa: E402
import mb_p34_barrels  # noqa: E402
import mb_fix_barrels  # noqa: E402
import mb_p34_parts  # noqa: E402
import mb_flare_mounts  # noqa: E402
import mb_p32_walls  # noqa: E402
import mb_p33_biomes  # noqa: E402
import mb_p33_edges  # noqa: E402
import mb_p33_landmarks  # noqa: E402
import mb_fix_l8  # noqa: E402
import mb_p35_ixion  # noqa: E402
import mb_p35_rocket_turret  # noqa: E402
import mb_p35_zu23_technical  # noqa: E402
import mb_p35_wave1_bosses  # noqa: E402
import mb_p35_wave1_towers  # noqa: E402
import mb_p35_supply_truck  # noqa: E402
import mb_p35_ammo_carrier  # noqa: E402
import mb_p35_vbied  # noqa: E402
import mb_p35_elite_mlrs  # noqa: E402
import mb_p35_counter_battery_radar  # noqa: E402
import mb_p35_lancet_truck  # noqa: E402
import mb_p35_microwave_vehicle  # noqa: E402
import mb_p35_smoke_carrier  # noqa: E402
import mb_p35_elite_mbt  # noqa: E402
import mb_p35_swarm_carrier  # noqa: E402
import mb_p35_wave2_atgm  # noqa: E402
import mb_p35_wave2_guns  # noqa: E402
import mb_p35_wave2_heavy  # noqa: E402
import mb_p35_wave2_hangar  # noqa: E402
import mb_p35_wave2_shield  # noqa: E402
import mb_p35_wave2_branches  # noqa: E402
import mb_p35_wave2_support  # noqa: E402
import mb_p35_trims  # noqa: E402
import mb_p35_wall_hesco  # noqa: E402
import mb_p35_wall_gun  # noqa: E402
import mb_p35_wall_t  # noqa: E402
import mb_p35_blast_wall  # noqa: E402
import mb_p35_aa_gun_tower  # noqa: E402
import mb_p35_at_gun_emplacement  # noqa: E402
import mb_p35_heavy_flak_tower  # noqa: E402
import mb_p35_searchlight  # noqa: E402
import mb_p35_one_shot_atgm_tower  # noqa: E402
import mb_p35_laser_ad_station  # noqa: E402
import mb_p35_fire_control_centre  # noqa: E402
import mb_p35_troop_shelter  # noqa: E402
import mb_p35_bunker_shelter_tower  # noqa: E402
import mb_p35_inflatable_decoy  # noqa: E402
import mb_p35_barrage_balloon  # noqa: E402
import mb_p35_super_gun  # noqa: E402
import mb_p35_ifv  # noqa: E402
import mb_p35_light_tank  # noqa: E402
import mb_p35_engineer_vehicle  # noqa: E402
import mb_p35_mortar_carrier  # noqa: E402
import mb_p35_flame_tank  # noqa: E402
import mb_p35_moloch  # noqa: E402
import mb_p35_attack_jet  # noqa: E402
import mb_p35_strike_drone  # noqa: E402
import mb_p35_recon_drone  # noqa: E402
import mb_p35_scout_heli  # noqa: E402
import mb_p35_river_patrol_boat  # noqa: E402
import mb_p35_towed_at_gun  # noqa: E402
import mb_p35_fpv_carrier  # noqa: E402
import mb_p35_shorad_vehicle  # noqa: E402
import mb_p35_armored_bulldozer  # noqa: E402
import mb_p35_sam_launcher  # noqa: E402
import mb_p35_amphib_light_vehicle  # noqa: E402
import mb_p35_mine_layer  # noqa: E402
import mb_p35_demolition_line_vehicle  # noqa: E402
import mb_p35_bmpt  # noqa: E402
import mb_p35_aa_gun_vehicle  # noqa: E402
import mb_p35_aa_vehicle  # noqa: E402
import mb_p35_artillery  # noqa: E402
import mb_p35_tank_destroyer  # noqa: E402
import mb_p35_wave5_tanks  # noqa: E402
import mb_p35_wave5_deploy  # noqa: E402
import mb_p35_wave5_bosses  # noqa: E402
import mb_p35_wave5_air  # noqa: E402
import mb_p35_elite_aa  # noqa: E402
import mb_p35_elite_heavy_tank  # noqa: E402
import mb_p35_elite_tank_destroyer  # noqa: E402
import mb_p35_elite_apc  # noqa: E402
import mb_p35_radar_atgm_vehicle  # noqa: E402
import mb_p35_ground_drone_carrier  # noqa: E402
import mb_p35_nlos_atgm_vehicle  # noqa: E402
import mb_p35_armored_car  # noqa: E402
import mb_p35_scout_jeep  # noqa: E402
import mb_p35_rocket_technical  # noqa: E402
import mb_p35_uav_loiter_strike  # noqa: E402
import mb_p35_aerial_tanker  # noqa: E402
import mb_p35_command_hq  # noqa: E402
import mb_p35_minefield  # noqa: E402
import mb_p35_gun_turret_a  # noqa: E402
import mb_p35_mg_bunker  # noqa: E402
import mb_p35_guard_tower_b  # noqa: E402
import mb_p35_next_gen_tank  # noqa: E402
import mb_p35_airborne_light_tank  # noqa: E402
import mb_p35_airborne_vehicle  # noqa: E402
import mb_p35_bridging_vehicle  # noqa: E402
import mb_p35_shield_carrier  # noqa: E402
import mb_p35_dazzler_vehicle  # noqa: E402
import mb_p35_drone_hijack_vehicle  # noqa: E402
import mb_p35_fibre_fpv_carrier  # noqa: E402
import mb_p35_hover_gunboat  # noqa: E402
import mb_p35_landing_craft  # noqa: E402
import mb_p35_missile_boat  # noqa: E402
import mb_p35_sea_corvette  # noqa: E402
import mb_p35_sea_cruiser  # noqa: E402
import mb_p35_interceptor_jet  # noqa: E402
import mb_p35_glide_bomber  # noqa: E402
import mb_p35_stealth_naval_strike  # noqa: E402
import mb_p35_hydra_sub  # noqa: E402
import mb_p35_nyx  # noqa: E402
import mb_p35_kraken  # noqa: E402
import mb_p35_garuda  # noqa: E402
import mb_p35_aa_turret  # noqa: E402
import mb_p35_c_ram  # noqa: E402
import mb_p35_artillery_emplacement  # noqa: E402
import mb_p35_long_sam  # noqa: E402
import mb_p35_heavy_rocket_artillery  # noqa: E402
import mb_p35_ballistic_launcher  # noqa: E402
import mb_p35_ew_jammer  # noqa: E402
import mb_p35_iron_beam  # noqa: E402
import mb_p35_shahed_truck  # noqa: E402
import mb_p35_interceptor_drone_vehicle  # noqa: E402
import mb_p35_mobile_repair_vehicle  # noqa: E402
import mb_p35_ground_cruise_missile_vehicle  # noqa: E402
import mb_p35_combat_wreck_car  # noqa: E402
import mb_p35_stealth_fighter  # noqa: E402
import mb_p35_supreme_command  # noqa: E402
import mb_p35_kronos  # noqa: E402
import mb_p35_earth_borer  # noqa: E402
import mb_p35_drop_pod  # noqa: E402
import mb_redesign_20y  # noqa: E402
import mb_p17_temp  # noqa: E402
import mb_phase2  # noqa: E402
import mb_phase8  # noqa: E402
import mb_props  # noqa: E402
import mb_siege  # noqa: E402
import mb_support  # noqa: E402
import mb_terrain  # noqa: E402
import mb_themes  # noqa: E402
import mb_themes2  # noqa: E402
import mb_tower_branches  # noqa: E402
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
                **mb_orbital.BUILDERS, **mb_munitions.BUILDERS, **mb_towers3.BUILDERS,
                # Round 6 rebuilt some models (Ka-52, Su-25, siege tank, bosses with every mount): theirs win.
                **mb_round6.BUILDERS, **mb_bosses2.BUILDERS, **mb_phase2.BUILDERS, **mb_phase8.BUILDERS,
                # Prompt 16: Leviathan, its fleet and Lighthouse Bay's props.
                **mb_naval.BUILDERS,
                # Prompt 16: new weapon parts on five bosses; they wrap the builders above.
                **mb_p16_arms.BUILDERS,
                # Prompt 17's temporary stand-ins for the new units (asset debt).
                **mb_p17_temp.BUILDERS,
                # Prompt 20 pass 2: the new bosses and the old bosses' new weapons (they wrap the builders above).
                **mb_p20_bosses.BUILDERS,
                # Tower branches (C.1): <tower>_a and <tower>_b, each built on its tower's builder.
                **mb_tower_branches.BUILDERS,
                # Play-test 4 (DECISIONS 19R): the bunker vehicle's dug-in mode and the look-alike redraws.
                **mb_p21_models.BUILDERS,
                # Play-test 5 (DECISIONS 20V): the FPV drone, the dug-in bunker, the AC-130, its transport twin, the stealth fighter.
                **mb_pt5_models.BUILDERS,
                **mb_p22_siege.BUILDERS,
                # Prompt 22 E (DECISIONS 22E): Morrigan, Wolff's stealth fighter.
                **mb_p22_content.BUILDERS,
                # DECISIONS 20Y: Ixion and Icarus redesigned from outside references (they win over the builders above).
                **mb_redesign_20y.BUILDERS,
                # Play-test 8 (DECISIONS 22R): Icarus redrawn as an orbital weapons platform (wins over 20Y's warship).
                **mb_pt8_icarus.BUILDERS,
                # Play-test 9 (DECISIONS 23M): Icarus a spaceship again, the stealth jet redrawn slim (they win over the above).
                **mb_pt9_models.BUILDERS,
                # Prompt 25 B2 (DECISIONS 25B2): models rebuilt to the balance sheet's shape notes and sizes (they win).
                **mb_p25_models.BUILDERS,
                # Prompt 25 B2 part 2 (DECISIONS 25B2): the rest of the vehicles, the bosses and the structures (they win).
                **mb_p25_models2.BUILDERS,
                # Prompt 25 F2 batch A (DECISIONS 25F2-A): the new units and structures.
                **mb_p25_new.BUILDERS,
                # Prompt 25 F2 batch C (DECISIONS 25F2-C): the new ordnance's rounds.
                **mb_p25_rounds.BUILDERS,
                # Prompt 27 experiment 1 (DECISIONS "27 experiment 1"): MBT, Su-27, Icarus, Apache on the improved
                # kit; last, so it wins (MB_P27_VARIANT=v0 gives the original builders back).
                **mb_p27_experiment.BUILDERS,
                # Prompt 27 wave 1a (DECISIONS "27 wave 1a"): Ixion, Gungnir (rail_supergun) and its rail_tractor on
                # the V2 kit; last, so it wins.
                **mb_p27_wave1a.BUILDERS,
                # Prompt 27 wave 1b (part): Monster and Nyx get their own models.
                # Prompt 27 wave 1c pass A: the first sixteen batch B stand-in units get their own models.
                **mb_p27_wave1b.BUILDERS,
                **mb_p27_wave1c.BUILDERS,
                # Prompt 27 wave 2 pass A: the validator's flagged models, smallest fixes (last, so it wins).
                **mb_p27_wave2.BUILDERS,
                # Prompt 27 wave 3: ground vehicles on the V2 kit (last, so it wins).
                **mb_p27_wave3.BUILDERS,
                # Prompt 27 wave 4: aircraft on the V2 kit (last, so it wins).
                **mb_p27_wave4.BUILDERS,
                # Prompt 27 wave 6 (lane B): towers on the V2 kit (last, so it wins).
                **mb_p27_wave6.BUILDERS,
                # Prompt 27 wave 7 (lane B): structures on the V2 kit (last, so it wins).
                **mb_p27_wave7.BUILDERS,
                # Prompt 27 wave 5 (lane A): the ground bosses on the V2 kit (last, so it wins).
                **mb_p27_wave5_ground.BUILDERS,
                # Prompt 27 wave 5 (lane B): the flying and naval bosses on the V2 kit (last, so it wins).
                **mb_p27_wave5_air.BUILDERS,
                # Prompt 27 wave 8 (lane A): munitions, props and unlisted units (last, so it wins).
                **mb_p27_wave8a.BUILDERS,
                # Prompt 27 wave 8 (lane B): props, scenery and town on the V2 kit (last, so it wins).
                **mb_p27_wave8b.BUILDERS,
                # Prompt 27 stand-in sweep: coastal_battery, super_gun, bulwark_post, uav_loiter_strike get their own
                # models (they drew heavy_turret, mg_bunker, strike_drone; last, so it wins).
                **mb_p27_standins.BUILDERS,
                # Prompt 32 L3: the base wall segments (HESCO, T-wall, gun wall) on the V2 kit.
                **mb_p32_walls.BUILDERS,
                # Prompt 33 L6: biome dressing (decoration only, drawn instanced by Surroundings.Dressing; last).
                **mb_p33_biomes.BUILDERS,
                # Prompt 33 L2 view: the edge corner pieces, the sea's and the edge types' dressing (decoration; last).
                **mb_p33_edges.BUILDERS,
                # Prompt 33 L3 view: the landmark models no map prop is (decoration; last).
                **mb_p33_landmarks.BUILDERS,
                # Full fix L8 (lead pass): the worst Kem models of the model scan rebuilt on the V2 kit (last, so it wins).
                **mb_fix_l8.BUILDERS,
                # Prompt 35 pilots (DECISIONS "Prompt 35"): rebuilt from scratch on the kit35 library (last, so they win).
                **mb_p35_ixion.BUILDERS, **mb_p35_zu23_technical.BUILDERS, **mb_p35_rocket_turret.BUILDERS,
                # Prompt 35 wave 1 lane A (DECISIONS "Prompt 35 wave 1 (lane A)"): five bosses and three structures.
                **mb_p35_wave1_bosses.BUILDERS, **mb_p35_wave1_towers.BUILDERS,
                # Prompt 35 wave 1, lane B (DECISIONS "Prompt 35 wave 1 (lane B)"): vehicles rebuilt from scratch (last).
                **mb_p35_supply_truck.BUILDERS, **mb_p35_ammo_carrier.BUILDERS,
                **mb_p35_vbied.BUILDERS, **mb_p35_elite_mlrs.BUILDERS,
                **mb_p35_counter_battery_radar.BUILDERS, **mb_p35_lancet_truck.BUILDERS,
                **mb_p35_microwave_vehicle.BUILDERS, **mb_p35_smoke_carrier.BUILDERS,
                **mb_p35_elite_mbt.BUILDERS, **mb_p35_swarm_carrier.BUILDERS,
                # Prompt 35 wave 2 lane A (DECISIONS "Prompt 35 wave 2 (lane A)"): towers with their branches (last).
                **mb_p35_wave2_atgm.BUILDERS, **mb_p35_wave2_guns.BUILDERS,
                **mb_p35_wave2_heavy.BUILDERS, **mb_p35_wave2_hangar.BUILDERS,
                **mb_p35_wave2_shield.BUILDERS, **mb_p35_wave2_branches.BUILDERS,
                **mb_p35_wave2_support.BUILDERS,
                # Prompt 35 wave 3, lane B (DECISIONS "Prompt 35 wave 3 (lane B)"): walls, towers, structures and four
                # vehicles rebuilt from scratch, one builder each (last, so they win).
                **mb_p35_wall_hesco.BUILDERS, **mb_p35_wall_gun.BUILDERS, **mb_p35_wall_t.BUILDERS,
                **mb_p35_blast_wall.BUILDERS, **mb_p35_aa_gun_tower.BUILDERS, **mb_p35_at_gun_emplacement.BUILDERS,
                **mb_p35_heavy_flak_tower.BUILDERS, **mb_p35_searchlight.BUILDERS,
                **mb_p35_one_shot_atgm_tower.BUILDERS, **mb_p35_laser_ad_station.BUILDERS,
                **mb_p35_fire_control_centre.BUILDERS, **mb_p35_troop_shelter.BUILDERS,
                **mb_p35_bunker_shelter_tower.BUILDERS, **mb_p35_inflatable_decoy.BUILDERS,
                **mb_p35_barrage_balloon.BUILDERS, **mb_p35_super_gun.BUILDERS, **mb_p35_ifv.BUILDERS,
                **mb_p35_light_tank.BUILDERS, **mb_p35_engineer_vehicle.BUILDERS, **mb_p35_mortar_carrier.BUILDERS,
                # Prompt 35 wave 4, lane C (DECISIONS "Prompt 35 wave 4 (lane C)"): rebuilt from scratch (last).
                **mb_p35_flame_tank.BUILDERS, **mb_p35_moloch.BUILDERS, **mb_p35_attack_jet.BUILDERS, **mb_p35_strike_drone.BUILDERS, **mb_p35_recon_drone.BUILDERS, **mb_p35_scout_heli.BUILDERS, **mb_p35_river_patrol_boat.BUILDERS, **mb_p35_towed_at_gun.BUILDERS, **mb_p35_fpv_carrier.BUILDERS, **mb_p35_shorad_vehicle.BUILDERS, **mb_p35_armored_bulldozer.BUILDERS, **mb_p35_sam_launcher.BUILDERS, **mb_p35_amphib_light_vehicle.BUILDERS, **mb_p35_mine_layer.BUILDERS, **mb_p35_demolition_line_vehicle.BUILDERS, **mb_p35_bmpt.BUILDERS, **mb_p35_aa_gun_vehicle.BUILDERS, **mb_p35_aa_vehicle.BUILDERS, **mb_p35_artillery.BUILDERS, **mb_p35_tank_destroyer.BUILDERS,
                # Prompt 35 wave 5 lane A (DECISIONS "Prompt 35 wave 5 (lane A)"): bosses, tanks, aircraft (last).
                **mb_p35_wave5_tanks.BUILDERS, **mb_p35_wave5_deploy.BUILDERS,
                **mb_p35_wave5_bosses.BUILDERS, **mb_p35_wave5_air.BUILDERS,
                # Prompt 35 wave 7, lane C (DECISIONS "Prompt 35 wave 7 (lane C)"): rebuilt from scratch (last).
                **mb_p35_elite_aa.BUILDERS, **mb_p35_elite_heavy_tank.BUILDERS, **mb_p35_elite_tank_destroyer.BUILDERS, **mb_p35_elite_apc.BUILDERS, **mb_p35_radar_atgm_vehicle.BUILDERS, **mb_p35_ground_drone_carrier.BUILDERS, **mb_p35_nlos_atgm_vehicle.BUILDERS, **mb_p35_armored_car.BUILDERS, **mb_p35_scout_jeep.BUILDERS, **mb_p35_rocket_technical.BUILDERS, **mb_p35_uav_loiter_strike.BUILDERS, **mb_p35_aerial_tanker.BUILDERS, **mb_p35_command_hq.BUILDERS, **mb_p35_minefield.BUILDERS, **mb_p35_gun_turret_a.BUILDERS, **mb_p35_mg_bunker.BUILDERS, **mb_p35_guard_tower_b.BUILDERS,
                # Prompt 35 wave 6 (lane B): tanks, ships, jets and four bosses, each from its own builder.
                **mb_p35_next_gen_tank.BUILDERS, **mb_p35_airborne_light_tank.BUILDERS,
                **mb_p35_airborne_vehicle.BUILDERS, **mb_p35_bridging_vehicle.BUILDERS,
                **mb_p35_shield_carrier.BUILDERS, **mb_p35_dazzler_vehicle.BUILDERS,
                **mb_p35_drone_hijack_vehicle.BUILDERS, **mb_p35_fibre_fpv_carrier.BUILDERS,
                **mb_p35_hover_gunboat.BUILDERS, **mb_p35_landing_craft.BUILDERS, **mb_p35_missile_boat.BUILDERS,
                **mb_p35_sea_corvette.BUILDERS, **mb_p35_sea_cruiser.BUILDERS, **mb_p35_interceptor_jet.BUILDERS,
                **mb_p35_glide_bomber.BUILDERS, **mb_p35_stealth_naval_strike.BUILDERS,
                **mb_p35_hydra_sub.BUILDERS, **mb_p35_nyx.BUILDERS, **mb_p35_kraken.BUILDERS,
                **mb_p35_garuda.BUILDERS,
                # Prompt 35 wave 9, lane C (DECISIONS "Prompt 35 wave 9 (lane C)"): rebuilt from scratch (last).
                **mb_p35_aa_turret.BUILDERS, **mb_p35_c_ram.BUILDERS, **mb_p35_artillery_emplacement.BUILDERS, **mb_p35_long_sam.BUILDERS, **mb_p35_heavy_rocket_artillery.BUILDERS, **mb_p35_ballistic_launcher.BUILDERS, **mb_p35_ew_jammer.BUILDERS, **mb_p35_iron_beam.BUILDERS, **mb_p35_shahed_truck.BUILDERS, **mb_p35_interceptor_drone_vehicle.BUILDERS, **mb_p35_mobile_repair_vehicle.BUILDERS, **mb_p35_ground_cruise_missile_vehicle.BUILDERS, **mb_p35_combat_wreck_car.BUILDERS, **mb_p35_stealth_fighter.BUILDERS, **mb_p35_supreme_command.BUILDERS, **mb_p35_kronos.BUILDERS, **mb_p35_earth_borer.BUILDERS,
                # Prompt 35 wave 11, lane C (DECISIONS "Prompt 35 wave 11 (lane C)"): rebuilt from scratch (last).
                **mb_p35_drop_pod.BUILDERS}
    for name in HIGH_DETAIL:
        build, options = builders[name]
        builders[f'{name}_hd'] = (functools.partial(build, detail=True), options)
    # A round 6 builder's own high-detail variant (attack_jet_hd) over the generic one.
    builders.update({k: v for k, v in mb_round6.BUILDERS.items() if k.endswith('_hd')})
    # Prompt 25 B2 part 2's own high-detail variants (attack_jet_hd) over round 6's.
    builders.update({k: v for k, v in mb_p25_models2.BUILDERS.items() if k.endswith('_hd')})
    # Prompt 27 wave 4b: attack_jet_hd on the V2 parts (nozzle, canopy frame) over the old one.
    builders.update({k: v for k, v in mb_p27_wave4.BUILDERS.items() if k.endswith('_hd')})
    # Prompt 35 wave 4 lane C: attack_jet_hd is the rebuilt Su-25 (over the prompt 27 one).
    builders.update({k: v for k, v in mb_p35_attack_jet.BUILDERS.items() if k.endswith('_hd')})
    # Prompt 34 L4: a muzzle for every barrel of the guns that fire their barrels together (after every other builder).
    builders = mb_p34_barrels.wrap(builders)
    # Full fix L3: the bosses' twin guns (a second barrel where one was) and their per-barrel muzzles.
    builders = mb_fix_barrels.wrap(builders)
    # Prompt 34 L7: separable wreck parts (Part_wheel, Part_wheelb, Part_wing, Part_tail) for the breakup by class.
    builders = mb_p34_parts.wrap(builders)
    # Fix prompt L4: the Mount_Flare_* points on every unit with flares (after every other builder and wrapper).
    builders = mb_flare_mounts.wrap(builders)
    # Prompt 35 wave 2: the old towers over the 1.5 x cap that no wave rebuilds, trimmed after their bake (last).
    builders = mb_p35_trims.wrap(builders)
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
