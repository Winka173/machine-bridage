# Play-test 14 plan (owner request: Docs/prompts/playtest14_vi.txt)

Owner answers 03/10 (questions A-F): A, C, D, F as proposed; B with changes; E (bosses) ON HOLD until the owner
names the bosses to redraw. Do not touch boss models, boss removal, boss size or Nyx escorts yet.

## Decisions
- "xóa" = "bỏ" = delete cleanly: data, cards, decks, campaign, strings EN/VI, guide text, GLB, builder, export pack,
  maps, tests (update, do not run). Old saves that own a deleted unit/support/structure get a refund.
- Core units deleted, replaced where referenced (default decks, generals' openingSquads, campaign, AI lists):
  gunship_heli -> attack_helicopter, bmpt -> ifv, interceptor_jet -> fighter_jet. Other deleted units: nearest role
  unit, listed in DECISIONS.
- Skill `apc_smoke` removed (from ifv); the ifv itself stays. `elite_smoke` stays.
- Fire support: `decoy_paradrop` and `decoy_tank` deleted. Supports that call units get a "Units called" tab in the
  fire-support screen. `reinforcements` (Airdropped armour): the player picks the units, total unit value <= 20 cp;
  call price = ceil(1.5 x total) (20 -> 30, 15 -> 23). `field_tower` keeps its guard tower.
- napalm_strike and airstrike: an aircraft flies over and drops bombs (napalm = fire canisters), on the existing
  bomb-run system; damage unchanged.
- Hangars (all 3 redrawn): drone hangar (FPV/Lancet as now), NEW vehicle hangar (scout_jeep / armored_car /
  light_tank, player picks one), NEW aircraft hangar (scout_heli / recon_drone, player picks one). Free, one unit per
  cycle, max 2 alive per hangar; tap the map to set a rally point.
- Aura buildings (global while standing, one per kind, no stacking): airfield = aircraft +10 % damage, +10 % speed;
  repair_bay = ground vehicles +10 % damage, +10 % max HP; fire_control_centre renamed "Defence Command Centre /
  Trung tâm chỉ huy phòng thủ" = structures +15 % range, +10 % HP. airfield.hangar / airfield.service dropped.
- laser_ad_station renamed "Laser Defence Tower / Tháp la-de phòng thủ"; variant .net dropped, .laser kept.
- New HQ tab: pick HQ type (Fortress / AA Fortress / Shield = the gun) and the unit the HQ calls (light vehicles as
  in the vehicle hangar). Base tab: fix scroll, text hidden behind the base cover.
- New Commander tab: pick commander + tactic, read-only view of the commander's starting forces (openingSquads).
- Sea: water covers every tile; waves follow the wind, not bottom-to-top.
- Every value change -> Docs/export/CHANGES.md.

## Deletion list (lane C)
Units: combat_wreck_car towed_at_gun aerial_tanker heavy_lift_helicopter gunship_heli smoke_carrier lancet_truck bmpt
counter_battery_radar recon_jet interceptor_jet wingman_drone bunker_vehicle shorad_vehicle microwave_vehicle
nlos_atgm_vehicle radar_atgm_vehicle airborne_vehicle(+_chute) wheeled_howitzer glide_bomber radar_scout
fibre_fpv_carrier interceptor_drone_vehicle aa_57mm_vehicle mine_rocket_truck prop_attack_plane light_attack_heli
turtle_tank drone_hijack_vehicle coastal_ashm_vehicle auto_loader_howitzer amphib_light_vehicle
airborne_light_tank(+_chute) ground_drone_carrier mobile_repair_vehicle radar_support_vehicle dazzler_vehicle
decoy_tank; uav_loiter_strike if only its support uses it.
Supports: gunship_support illum_flare_strike instant_counter_battery drone_intercept_strike chaff_strike uav_scan
sead_strike guided_shell_strike cluster_at_strike uav_loiter_strike_support ammo_resupply jam_storm smoke_screen
decoy_paradrop.
Structures (with all variants): at_gun_emplacement dragons_teeth inflatable_decoy minefield searchlight
heavy_flak_tower troop_shelter artillery_emplacement radar_station ammo_depot visual_jammer.
Keep: radar_station_prop (map dressing), flare_searchlight_tower, remote_mines, mine_layer.
Weapons/skills used only by deleted entries go too.

## Lanes (all opus)
- A feature/pt14-a: gameplay + VFX fixes (list in the lane brief).
- B feature/pt14-b: UI (commander tab, back button, base tab, HQ tab), hangars + aura logic, fire-support summon tab.
- C feature/pt14-c: deletions; then non-boss model waves (4-6 models each): ew_jammer, iron_beam, command_vehicle,
  wheeled_gun (smaller turret), stealth_naval_strike, aa_vehicle + heavy_aa (real twin-cannon spacing), guard_tower,
  laser_ad_station, mg_bunker (several MGs firing), drone hangar + vehicle hangar + aircraft hangar.

## Owner follow-up (03/10)
- Q18: boss +20-30 % is VISUAL size only (hitbox/collision unchanged). Still waits for the boss confirmation.
- Q19: boss escorts follow the boss's domain: ground boss -> ground vehicle escorts, sea boss -> boat escorts, air
  boss -> aircraft escorts (fixes Nyx). Data/rule work, allowed now (lane A).
