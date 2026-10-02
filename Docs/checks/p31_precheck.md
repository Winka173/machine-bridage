# Prompt 31 pass 0: precheck (read only, 2026-10-02)

Read from the code at `feature/p31-b1` (from `ca1488f4`); nothing was run but Python over the data. Source sheets:
`Docs/story/Machine_Brigade_Cot_truyen_Che_do_v2.xlsx` "Màn bộ bài game", "Biến cố", "AI theo chế độ".

## 1. CEASEFIRE and targetFactionMask at the damage level

Yes (prompt 28 appendix). `SimWorld.AiModes.cs`: `SetCeasefire(team, on)` / `Ceasefire(source, target)`;
`DamageSystem.Apply` returns 0 for any hit whose source team is not the target's when the target's team is a ceasefire
faction. Every vehicle and prop loss goes through `Apply` (direct fire, strikes, splash, burns; the only other `Hp -=` are
a boss's big-attack flights), so fire support and splash are covered. `CombatSystem` never picks a ceasefire target.
`AiModeProfile.TargetMask` (balance.json `aiModeProfiles.*.targetMask`) is data; the ceasefire itself is per team, so a
CEASEFIRE faction (c6m14, Varga's column) needs a team of its own, or the per-vehicle `Truce` of prompt 23 E.1 (which
an ordered attack can still break). Environment blasts (team -1) do not hurt a ceasefire team either.

## 2. Placed allies: can the existing allied AI drive a single unit

Mostly. `MissionSession.Build` makes `AllyAi = new TacticalAi(PlayerTeam, EnemyTeam) { Allies = true }` when the mission
has an `ally` (Thorne's troops, Varro's militia) or an event that sends allies; it drives every player-team vehicle with
`Vehicle.Ally == true` (TacticalAi lines 695 and 767) towards the player's goal. A lone placed unit spawned with
`Ally = true` would be driven by it. Missing: the AI is only made for missions with `ally` or ally events (one more
condition: the fixed deck's `placedAllies`), and it does not follow the player's Attack/Defend order (prompt 31 wants
placed allies "theo lệnh Tấn công/Phòng thủ chung"); both are pass 4 work (c6m03 first).

## 3. Mara's Behemoth and a named aircraft from existing units

Data: yes. `behemoth` and the variant defs exist in balance.json (`behemoth_mk0` is still a pending boss slot with a
fallback, build_campaign `PENDING_BOSSES`); a mission's scripted unit has `name` and `fallback` (`ScriptedUnitDef`), and
`fighter_jet` exists for Hawk's aircraft. The fixed deck's `placedAllies` entries reuse the same shape (def, x, z,
heading, name, fallback, lossIfDestroyed). Behaviour: a boss on the player's team is untested (BossSystem's escorts and
big attacks assume the enemy side in places); pass 4 must check it in c6m03 before c10m12 and c12m03.

## 4. Where the campaign generator's rule "no mission asks for a card not unlocked" lives

`Tools/campaign/build_campaign.py` `check()`: it walks the missions in order with `owned` (STARTERS + every earlier
mission's `unlocks`). The card rules there today: a card is unlocked once, side missions pay no cards, a flying boss
needs at least four anti-air cards owned. No mission named a player card before prompt 31 (only `playerDeck: "air"`,
whose top-up takes unlocked fighters, `MissionDecks.Vehicles`). The design doc states the rule
(`Tools/docs/programme.py` section 3). Pass 1 adds the fixed-deck check there: every card of a fixed deck is owned by
then or listed in its `loanedCards` (the only valid exception), at most two loaned (c1m01: four, see DECISIONS).

## 5. NavGrid prebuilt states switched at a fixed tick

No named states. `NavGrid` keeps a reference count of blockers per cell (`AddBlocker` / `RemoveBlocker`, `BlockWhere`),
bumps `Version` on every change, recomputes its connected regions lazily (`RegionOf`, `RegionSize`), and `LaneMap`
rebuilds when the version changed (at most every 2 s). Walls and defences use this at run time. Pass 3 can build
"prebuilt states" on it: named blocker sets per map, applied or removed in one Sim step at a fixed tick, their
connectivity checked by `RegionOf` in a test; nothing there needs Unity NavMesh.

## 6. Locked cards in each of the 23 fixed decks at the time of the mission

"Locked": not a starter and not unlocked by an earlier mission (a mission's own reward counts as locked in it).
"Shop": among them, cards no campaign mission unlocks (the shop's new content; `reinforcements` is a consumable item,
not a card).

| Mission | Status | Locked vehicles | Which | Locked supports | Which | Shop-only of them |
|---|---|---|---|---|---|---|
| c1m01 | MAKE FIRST | 6 | amphib_light_vehicle, light_tank, rocket_technical, mortar_carrier, zu23_technical, engineer_vehicle | 0 | - | 1 |
| c2m04 | MAKE FIRST | 3 | vbied, recoilless_jeep, demolition_line_vehicle | 0 | - | 2 |
| c2s2 | MAKE FIRST | 3 | shorad_vehicle, aa_gun_vehicle, mobile_repair_vehicle | 1 | uav_scan | 3 |
| c3m06 | MAKE FIRST | 3 | radar_scout, wheeled_howitzer, scout_heli | 2 | instant_counter_battery, illum_flare_strike | 4 |
| i1m01 | MAKE LATER | 3 | radar_scout, recoilless_jeep, ew_jammer | 0 | - | 2 |
| c4m05 | MAKE FIRST | 3 | demolition_line_vehicle, nlos_atgm_vehicle, towed_at_gun | 1 | remote_mines | 3 |
| c4m06 | MAKE FIRST | 5 | river_patrol_boat, river_gunboat, amphib_light_vehicle, coastal_ashm_vehicle, prop_attack_plane | 1 | guided_shell_strike | 6 |
| c5m03 | MAKE LATER | 2 | microwave_vehicle, interceptor_drone_vehicle | 1 | drone_intercept_strike | 3 |
| c5m07 | MAKE FIRST | 6 | light_attack_heli, wingman_drone, interceptor_drone_vehicle, microwave_vehicle, iron_beam, shorad_vehicle | 2 | drone_intercept_strike, jam_storm | 6 |
| c6m03 | MAKE LATER | 1 | mobile_repair_vehicle | 0 | - | 1 |
| c6m14 | MAKE LATER | 4 | microwave_vehicle, interceptor_drone_vehicle, bridging_vehicle, mobile_repair_vehicle | 1 | drone_intercept_strike | 5 |
| i2m01 | MAKE LATER | 4 | amphib_light_vehicle, airborne_light_tank, shorad_vehicle, mobile_repair_vehicle | 1 | decoy_paradrop | 5 |
| c7m16 | MAKE LATER | 0 | - | 0 | - | 0 |
| c7m11 | MAKE FIRST | 3 | aa_57mm_vehicle, shorad_vehicle, radar_support_vehicle | 2 | illum_flare_strike, sead_strike | 4 |
| c8m11 | MAKE FIRST | 3 | combat_wreck_car, recoilless_jeep, demolition_line_vehicle | 1 | reinforcements | 4 |
| c9m08 | MAKE FIRST | 4 | coastal_ashm_vehicle, ground_cruise_missile_vehicle, stealth_naval_strike, river_gunboat | 2 | cruise_missile, chaff_strike | 5 |
| c9m12 | MAKE LATER | 5 | amphib_light_vehicle, river_gunboat, river_patrol_boat, coastal_ashm_vehicle, airborne_vehicle | 1 | guided_shell_strike | 6 |
| i3m02 | MAKE FIRST | 5 | shorad_vehicle, radar_support_vehicle, aa_57mm_vehicle, interceptor_drone_vehicle, mobile_repair_vehicle | 2 | decoy_paradrop, chaff_strike | 7 |
| i3m03 | MAKE FIRST | 2 | next_gen_tank, mobile_repair_vehicle | 0 | - | 2 |
| c10m11 | MAKE LATER | 2 | aa_57mm_vehicle, radar_support_vehicle | 0 | - | 2 |
| c10m12 | MAKE LATER | 5 | wingman_drone, radar_support_vehicle, aa_57mm_vehicle, aerial_tanker, shorad_vehicle | 1 | chaff_strike | 5 |
| c11m13 | MAKE FIRST | 3 | recon_jet, gps_jammer_vehicle, airborne_vehicle | 1 | decoy_paradrop | 4 |
| c12m03 | MAKE LATER | 1 | mobile_repair_vehicle | 0 | - | 1 |

Every id of the sheet is in balance.json (vehicles or supports). Only c6m03, c7m16, c12m03 and i3m03 fit the
"at most 1-2 loaned" rule as written; the others need replacements (pass 1/2, DECISIONS "Prompt 31 L0/L1/L2").
c1m01 cannot: a new player owns four vehicle cards, so an eight-card deck there needs four loaned.
