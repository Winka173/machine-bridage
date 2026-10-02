# Prompt 27 waves 4 and 6 in parallel (two agents), plus prompt 29's model details

The owner (2026-10-02): "tiếp tục prompt 27 luôn, nâng agent lên 2". Two agents at once, on files that do not overlap:

| lane | worktree | branch per pass | builder file | passes |
|---|---|---|---|---|
| A: aircraft + prompt 29 5.5 | `C:\Users\Winka\Projects\MachineBrigade-art` | `feature/p27-wave4<x>` | `Tools/blender/mb_p27_wave4.py` | 4a, 4b, 4c |
| B: towers | `C:\Users\Winka\Projects\MachineBrigade-art2` | `feature/p27-wave6<x>` | `Tools/blender/mb_p27_wave6.py` | 6a-6e |

| pass | models |
|---|---|
| 4a | scout_heli, gunship_heli, elite_attack_helicopter, swarm_carrier, recon_drone, strike_drone, wingman_drone, drop_pod |
| 4b | attack_jet (+hd), heavy_bomber, stealth_bomber, stealth_fighter, glide_bomber, recon_jet, airborne_vehicle_chute |
| 4c | prompt 29 5.5 details only (no V2 rebuild): flare tubes on heavy_lift_helicopter, light_attack_heli, prop_attack_plane, aerial_tanker, attack_helicopter (+hd), fighter_jet (+hd), interceptor_jet, twin_rotor_gunship, sky_gunship (+hd); the APS cluster on next_gen_tank and titan_tank |
| 6a | aa_turret, artillery_emplacement, guard_tower, each with `_a` and `_b` |
| 6b | gun_turret, mg_bunker, rocket_turret, each with `_a` and `_b` |
| 6c | atgm_tower, c_ram, each with `_a` and `_b`; gun_pit |
| 6d | drone_hangar, ew_tower, each with `_a` and `_b` |
| 6e | heavy_turret, missile_battery, each with `_a` and `_b`; aa_gun_tower, flare_tower, searchlight, wreck_turret |

## Standing brief (both lanes)

Follow `Docs/models/WAVE3_PLAN.md` "The standing brief for every pass" (reading list, gates, allowed runs, no runner
mirror, no card/preview renders, the old card luma in the report), with these changes:
- Read `PROGRESS.md` "Wave 4" or "Wave 6", and every DECISIONS section headed "27 wave 3", "27 wave 4" or "27 wave 6"
  (grep headings; never read DECISIONS whole). Lesson from wave 3: a brighter COLOR_0 does not guarantee a brighter card
  (radar_atgm_vehicle); prefer pale top surfaces and avoid dark `Steel` on large faces.
- Write builders ONLY in your lane's builder file (register it last in `build_assets.py`, after `mb_p27_wave3`; lane A
  registers `mb_p27_wave4` and lane B `mb_p27_wave6` in one line each, so a merge of both is trivial).
- To keep the two lanes mergeable, do NOT edit `Docs/models/PROGRESS.md`, this file's table or `Docs/CHANGELOG.md` (the
  lead does). Do write your DECISIONS section "## 27 wave <x> (lead pass, <date>)" at the end of `Docs/DECISIONS.md`,
  and accept your models in the validator (`glb_check.py --accept`).
- Lane A: jets get only `k.clean` + the library nozzle/canopy in `_hd` (checkpoint 1); helicopters and drones V2.
  Prompt 29 5.5: use `Tools/blender/mb_p29_details.py` (`flare_tubes`, `aps_cluster`, `FLARE_MODELS` tube counts) on
  every FLARE model in your pass; small details only, nodes unchanged except new non-runtime meshes. The flare/APS
  effects and all Game code are NOT yours (the lead's UI pass).
- Lane B: towers keep everything `TowerArt` and `TowerRankDetails` need (grep them); the weapon on top must read at
  40 px; a base tower and its `_a`/`_b` branches in one commit.
- Commit messages end with: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Report in ~8 lines.

## Wave 7 (structures), lane B after wave 6 (2026-10-02)

Same standing brief; builder file `Tools/blender/mb_p27_wave7.py` (register it last in `build_assets.py`, one import
line and one `**mb_p27_wave7.BUILDERS` line). Unarmed statics: big volumes, no new moving parts; pale base colours on
the biggest top/side faces (wave 6 lesson).

| pass | models |
|---|---|
| 7a | cp_relay, shield_tower, dragons_teeth, minefield, each with `_a` and `_b` |
| 7b | barrage_balloon, blast_wall, fire_control_centre, inflatable_decoy, troop_shelter, logistics_station, radar_site, repair_bay, ammo_dump, targeting_station |

## Wave 5 (bosses), both lanes (2026-10-02)

Same standing brief, plus PROGRESS.md "Wave 5": at the prompt 26 sizes (`size`, `modelSize`); keep every boss part node
(`Part_<letters>[.NNN]`, grep the def's `parts` in balance.json), `mountWeapons` slots, `Mount_*`/`Muzzle_*`, phase
and escort nodes; vary greeble seeds per ship; boss class budgets (boss_s/m/l). Check each model id is not shared by
another def's variant (grep `"model"`); if it is, keep the variant's keep/drop nodes. Pale base colours on the biggest
faces, but bosses are dark war machines: aim for card luma >= old, not much above (<= ~+20 %).

| lane | pass | models | builder file |
|---|---|---|---|
| A (art) | 5a | behemoth, behemoth_inferno, behemoth_tempest, fortress_bastion, fortress_hive | `mb_p27_wave5_ground.py` |
| A (art) | 5b | kronos, moloch, nuke_train, armored_train, earth_borer | `mb_p27_wave5_ground.py` |
| B (art2) | 5c | command_airship, drone_mothership, mega_gunship, sky_fortress, daedalus, morrigan | `mb_p27_wave5_air.py` |
| B (art2) | 5d | leviathan, caspian, typhon, landing_hovercraft, supreme_command | `mb_p27_wave5_air.py` |
