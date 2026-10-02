# Prompt 27 wave 8: the remaining 198 models, two lanes

The owner (2026-10-02) chose "Làm hết 198 model". The model lists are the rows of `Docs/models/PROGRESS.md` "Wave 8";
a pass takes the named builder rows (or the named half of a row, in the row's order). Same standing brief as
`Docs/models/WAVES_4_6_PLAN.md` (and through it `WAVE3_PLAN.md`): gates, allowed runs, no runner mirror, no card or
preview renders, do not edit PROGRESS.md / plan tables / CHANGELOG, write a DECISIONS section `## 27 wave <pass>
(lead pass, <date>)`, accept your models in the validator.

Wave 8 specifics:
- Most of these have no card: the gates are the validator, COLOR_0 >= old (but scenery should stay natural: rocks,
  trees, terrain no more than ~+10 % COLOR_0) and triangles <= 1.6x. Props and scenery are drawn many times per map:
  stay lean (prefer <= 1.3x), no new materials, no new moving parts.
- Munitions (the generated dicts the static scan missed, `mb_air`, `mb_vehicles3`) are tiny and fast: keep their
  silhouettes and nodes (`Muzzle`, fins, `Exhaust`); triangles may grow only where the munition is seen big
  (cruise and ballistic missiles, ICBM, heavy rockets).
- Unlisted units (apc, armed_truck, heavy_attack_heli, sapper, transport_plane, aps_tank, atgm_carrier, howitzer,
  fpv_drone, bug_satellite) follow the wave 3/4 rules (V2, runtime nodes identical).
- Find each model's real builder first (`grep` the id in `Tools/blender`): several are generated in loops.

| lane | worktree | builder file | passes |
|---|---|---|---|
| A | `MachineBrigade-art` | `Tools/blender/mb_p27_wave8a.py` | 8a1 munitions row ("not found by the static scan"), first half; 8a2 its second half; 8a3 mb_air, mb_vehicles3, mb_support, mb_artillery; 8a4 mb_vehicles (apc +hd), mb_new_trucks, mb_orbital, mb_pt5_models, mb_round6, mb_air3, mb_new_tracked, mb_p25_models2 (transport_plane); 8a5 mb_phase8 (wreck_*; rail_tractor is done), mb_naval, mb_siege |
| B | `MachineBrigade-art2` | `Tools/blender/mb_p27_wave8b.py` | 8b1 mb_props; 8b2 mb_mapkit; 8b3 mb_town; 8b4 mb_themes; 8b5 mb_themes2 first half; 8b6 mb_themes2 second half; 8b7 mb_harbor, mb_terrain |

Register the lane's builder file last in `build_assets.py` (one import line, one `**module.BUILDERS` line). The
substring build filter rebuilds other ids that contain yours: revert any GLB outside your pass.
