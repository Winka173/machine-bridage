# Prompt 31 report: game-made decks, placed allies and battlefield events

Passes 0-6 were done in lead passes on `feature/p31-b1`, `feature/p31-b2` and `feature/p31-b3`. Nothing was run but the
Python tools over the data (`build_campaign.py --no-texts`, `nav_states.py`): no match, no test, no simulation, no measure
(the owner's rule); the tests were written for the lead (Prompt31NavStateTests, Prompt31PlacedAllyTests,
Prompt31LaterEventTests). Details and reasons are in `Docs/DECISIONS.md` under "Prompt 31 L0/L1/L2", "Prompt 31 L3",
"Prompt 31 L4", "Prompt 31 L5" and "Prompt 31 L6". No mission's objective changed (`Tools/campaign/p31_objectives_baseline.json`
is checked by the build).

## 1. Pass 0 results (`Docs/checks/p31_precheck.md`)

1. **CEASEFIRE and the target mask at the damage level**: yes, from prompt 28. `DamageSystem.Apply` refuses any hit from
   another side on a ceasefire team (direct fire, strikes, splash, burns all go through it); the combat system never
   picks a ceasefire target. The ceasefire is per team, so c6m14's column needed a per-vehicle form (pass 4:
   `Vehicle.Sworn`).
2. **Placed allies**: the allied TacticalAi (Thorne's troops) drives any player-side vehicle with `Ally`; it was only made
   for missions with an ally and did not follow the player's Attack/Defend order. Both added in pass 4.
3. **Mara's Behemoth and a named aircraft**: buildable from existing defs (`behemoth`, `mara_behemoth` with a fallback,
   `fighter_jet` named), the scripted-unit shape reused.
4. **"No mission asks for a locked card"**: `build_campaign.py` `check()` (owned = starters + earlier unlocks). Pass 1 added
   the fixed-deck check there; a loaned card is the only valid exception.
5. **Prebuilt NavGrid states at a fixed tick**: not before prompt 31 (reference-counted blockers only). Pass 3 built
   `world.NavStates` on them.
6. **Locked cards per fixed deck**: only c6m03, c7m16, c12m03 and i3m03 fitted "1-2 loaned" as the sheet wrote them;
   c1m01 needs four (a new player owns four vehicle cards). The table is in the precheck file.

## 2. Missions made and left

All 23 missions of the sheet "Màn bộ bài game" have their fixed deck: the 13 MAKE FIRST in pass 2 (c1m01, c2m04, c2s2,
c3m06, c4m05, c4m06, c5m07, c7m11, c8m11, c9m08, i3m02, i3m03, c11m13) and the 10 MAKE LATER in pass 4 (c6m03 first as the
placed-ally trial, then c10m12 and c12m03, then i1m01, c5m03, c6m14, i2m01, c7m16, c9m12, c10m11). **None was left on the
player's deck.**

Placed allies: c6m03 Mara's Behemoth (the escorted convoy itself; lost if it falls; halts on Defend), c10m12 Hawk's fighter
(must live), c12m03 Mara's repainted Behemoth (not lost if it falls). c7m16 uses the mission's own allied wing (Thorne's
army) for the chapter 7 anomaly (his wing turns away 180-270 s "on new intelligence"; nothing counts his refusals).

Pending items the sheet asks for that were not built (each in DECISIONS): i1m01's 3 stars for no alarm and i2m01's 3 stars
before dusk (no star rule of their own), c4m05's mines slowing the train (they damage it), c5m07's canopy hiding vehicles
from drones, i3m02's Morrigan preferring standing anti-air, i2m01's Venn convoy and c10m11's Albatross as background objects.

## 3. Loaned cards and the sheet's cards replaced

At most two loaned cards a mission ("Loaned for this mission" / "Mượn trong nhiệm vụ này"), c1m01 four. Every other locked
card of the sheet was replaced by an owned card of the same role (the reasons by mission in DECISIONS):

| Mission | Status | Loaned | Replaced (sheet → deck) | Placed allies | Special rules |
|---|---|---|---|---|---|
| c1m01 | MAKE FIRST | amphib_light_vehicle, light_tank, rocket_technical, mortar_carrier | zu23_technical → ifv, engineer_vehicle → main_battle_tank | — | noBaseStart, beachLanding, coastalGuns |
| c2m04 | MAKE FIRST | vbied, demolition_line_vehicle | recoilless_jeep → ifv | — | raidNoBase |
| c2s2 | MAKE FIRST | shorad_vehicle, aa_gun_vehicle | mobile_repair_vehicle → ammo_carrier, uav_scan → smoke_screen | — | warnedAirWaves |
| c3m06 | MAKE FIRST | radar_scout, instant_counter_battery | wheeled_howitzer → mortar_carrier, scout_heli → attack_helicopter, illum_flare_strike → uav_scan | — | nightGuns |
| c4m05 | MAKE FIRST | towed_at_gun, remote_mines | demolition_line_vehicle → vbied, nlos_atgm_vehicle → artillery | — | trainPrep |
| c4m06 | MAKE FIRST | river_patrol_boat, river_gunboat | amphib_light_vehicle → ifv, coastal_ashm_vehicle → railgun_truck, prop_attack_plane → scout_heli, guided_shell_strike → artillery_barrage | — | seaFogLighthouse |
| c5m07 | MAKE FIRST | iron_beam, drone_intercept_strike | light_attack_heli → scout_heli, wingman_drone → strike_drone, interceptor_drone_vehicle → sam_launcher, microwave_vehicle → ew_jammer, shorad_vehicle → aa_vehicle, jam_storm → uav_scan | — | airCap6 |
| c7m11 | MAKE FIRST | aa_57mm_vehicle, shorad_vehicle | radar_support_vehicle → recon_drone, illum_flare_strike → uav_scan, sead_strike → airstrike | — | airCap6, cityBlackout |
| c8m11 | MAKE FIRST | combat_wreck_car, recoilless_jeep | demolition_line_vehicle → engineer_vehicle, reinforcements → artillery_barrage | — | patchworkDeck |
| c9m08 | MAKE FIRST | coastal_ashm_vehicle, ground_cruise_missile_vehicle | stealth_naval_strike → attack_jet, river_gunboat → mlrs, cruise_missile → airstrike, chaff_strike → smoke_screen | — | ciwsSaturate |
| i3m02 | MAKE FIRST | aa_57mm_vehicle, decoy_paradrop | shorad_vehicle → aa_vehicle, radar_support_vehicle → recon_drone, interceptor_drone_vehicle → heavy_aa, mobile_repair_vehicle → engineer_vehicle, chaff_strike → smoke_screen | — | morriganDecoys |
| i3m03 | MAKE FIRST | next_gen_tank, mobile_repair_vehicle | — | — | eliteRank |
| c11m13 | MAKE FIRST | recon_jet, gps_jammer_vehicle | airborne_vehicle → light_tank, decoy_paradrop → sead_strike | — | timedRecon |
| c6m03 | MAKE LATER | mobile_repair_vehicle | — | Mara's Behemoth (the convoy) | behemothOurs |
| c10m12 | MAKE LATER | wingman_drone, chaff_strike | radar_support_vehicle → recon_drone, aa_57mm_vehicle → heavy_aa, aerial_tanker → stealth_fighter, shorad_vehicle → aa_vehicle | Hawk's fighter (must live) | hawkWingman |
| c12m03 | MAKE LATER | mobile_repair_vehicle | — | Mara's repainted Behemoth | maraBehemoth |
| i1m01 | MAKE LATER | radar_scout, ew_jammer | recoilless_jeep → rocket_technical | — | factoryAlarm |
| c5m03 | MAKE LATER | microwave_vehicle, interceptor_drone_vehicle | drone_intercept_strike → uav_scan | — | droneCanopy |
| c6m14 | MAKE LATER | microwave_vehicle, interceptor_drone_vehicle | bridging_vehicle → armored_bulldozer, mobile_repair_vehicle → ammo_carrier, drone_intercept_strike → uav_scan | — | ceasefireFaction |
| i2m01 | MAKE LATER | amphib_light_vehicle, airborne_light_tank | shorad_vehicle → aa_vehicle, mobile_repair_vehicle → engineer_vehicle, decoy_paradrop → uav_scan | — | mirewoodFog |
| c7m16 | MAKE LATER | — | — | — | thorneAnomaly |
| c9m12 | MAKE LATER | amphib_light_vehicle, river_patrol_boat | river_gunboat → mlrs, coastal_ashm_vehicle → railgun_truck, airborne_vehicle → armored_car, guided_shell_strike → artillery_barrage | — | islandHop |
| c10m11 | MAKE LATER | aa_57mm_vehicle, radar_support_vehicle | — | — | airfieldLanding |

## 4. Battlefield events made and stopped

Every event that changes the ground uses prebuilt NavGrid states (`world.NavStates`, built and checked at load), switches
only at a tick boundary, leaves a way round in every state (the build's check and the game's at load), traps nobody
(vehicles on closed ground are put out), warns 8-12 s ahead with a system notice and minimap marks, and happens on the
battle's clock or a condition, so a replay meets it on the same step.

| Event (sheet) | Pass | Missions | What happens |
|---|---|---|---|
| Bão cát đổi hướng | 3 | c2m06, c12m07 | the storm rolls over one half (sight there falls, the other half clears); the view's sandstorm covers only that half (pass 5) |
| Báo động nhà máy | 3 | i1m01 | spotted: the mill gate shuts, the garrison's wave follows |
| Mất điện thành phố | 3 | c7m11 | night falls, every grid tower of both sides off for 90 s |
| Phản bội (báo trước) | 3 | c7m10 | Thorne's columns marked and Nadia's line 10 s before they turn |
| Khoang đổ bộ quỹ đạo | 3 | c11m10 | three pods stand up as enemy towers on prebuilt landing sites; a site reopens when its tower falls, after the fortress stage too (pass 5) |
| Triều lên/xuống | 5 | c1m01 | every 150 s the eastern shoal floods and dries |
| Cầu sập | 5 | i2m03 | at 150 s the east bridge falls (a time mark only) |
| Cần cẩu đổ | 5 | c4m05, c4m02 | the neutral crane, once shot down, falls along the quay and closes its middle lane |
| Hồ băng nứt | 5 | c3m04 | medium and heavy vehicles (by weight class, not CP) 10 s on the lake are slowed as the ice gives |
| Đập nứt | 5 | c6m10, c6m14 | the river below the dam rises in three levels, never down |
| Sập hầm mỏ | 5 | c8m10 | at 240 s one adit caves in and the other is blasted open |
| Dung nham | 5 | c5m10 | at 180 s lava cuts the west causeway road's north-east lane |
| Cháy rừng | 5 | c5m13 | a prebuilt wind-driven front burns four strips in turn (flames, burns, smoke), then goes out |

**Stopped: none.** Mây thấp was dropped by the sheet (it needs height play the game does not have). The forest fire, the
sheet's riskiest, was made without its risks: no cell-by-cell spread, a prebuilt front on the battle's clock.

Places the sheet named that were not used: c9m02 (tide) and c7m17 (bridge) are reversed battlefields, and nav states on a
reversed battlefield are refused by the build (the rectangles are written for the map as drawn); both keep their events.
The bridge's "or when shot enough" is not made (the bridge is a prop the game never damages).

To watch in play: the view draws no closed ground yet (the flooded ford, the fallen bridge and boom, the sealed adit and
the lava look as the map draws them; the minimap marks and notices carry them; the forest fire has its flames and smoke):
a per-site look is the next view task. The sandstorm-half view and the minimap marks were written blind.
