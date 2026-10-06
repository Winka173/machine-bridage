# Balance v3 — cheap/mid tier addendum (06/10)

Source: `Docs/prompts/balance_v3_cheap_mid_vi.md` (owner addendum, LOW/MID TIER §1-39), applied on top of pass 1
(`Docs/balance/balance_final_changes.json` + `BALANCE_MASTER_FINAL_REPORT.md`) and pass 2
(`BALANCE_V2_REPORT.md` + `Docs/prompts/balance_v2_clarify_vi.md`). Per §33, every target below is the **final total
versus the ORIGINAL baseline** (`balance.json` at `2a71b0cb`, the commit before the first "Balance final:" commit
`2625c100`), not a further multiply on top of pass 1/2. Branch `feature/balance-v3`, worktree `MachineBrigade-bal`.

Edits are textual (JSONC comments kept). `weapons[]` entries whose damage is shared live (`"weaponFamily"`-bound or a
child `"inherits"`-without-own-`"damage"`) got a unit-specific variant instead of a direct edit, so the buff cannot
leak to another vehicle, a tower, or a boss. Direct edits were only used where the weapon id already has exactly one
vehicle referencing it and no inherit-child without its own damage override.

## 1. Ledger (§33) — final multiplier vs. original baseline, not cumulative

| unit | orig HP | prev. HP mult | new final HP mult | new HP | primary weapon | prev. wpn mult | new final wpn mult | CP old→final |
|---|---|---|---|---|---|---|---|---|
| armored_car | 300 | ×1.00 | ×1.333 | 400 | autocannon_25 → **autocannon_25_car** | ×1.00 | ×1.15 | 3→4 |
| scout_jeep | 120 | ×1.00 | ×1.30 | 156 | mg_jeep → **mg_jeep_scout** | ×1.00 | ×1.10 | 2→3 |
| rocket_technical | 230 | ×1.00 | ×1.35 | 310.5 | technical_rockets (direct) | ×1.00 | ×1.15 | 3→4 |
| zu23_technical | 210 | ×1.00 | ×1.35 | 283.5 | zu23 → **zu23_cheap** | ×1.00 | ×1.20 | 3→4 |
| recoilless_jeep | 159 | ×1.00 | ×1.30 | 206.7 | recoilless_106 (KEEP) | ×1.00 | ×1.00 | 3→4 |
| light_tank | 460 | ×1.00 | ×1.18 | 542.8 | gun_57mm → **gun_57mm_lt** | ×1.00 | ×1.10 | 3→4 |
| ifv | 623 | ×1.00 | ×1.12 | 697.76 | ifv_30 (own damage added) | ×1.00 (inherited) | ×1.08 | 7→7 |
| wheeled_gun | 814 | ×1.00 | ×1.10 | 895.4 | gun_105_wheeled (direct) | ×1.00 | ×1.05 | 7→7 |
| tank_destroyer | 741 | ×1.05 (778) | ×1.10 | 815 | gun_105_long (direct) | ×1.00 | ×1.05 | 7→7 |
| flame_tank | 741 | ×1.08 (800) | ×1.12 | 830 | flamethrower (direct) | ×1.00 | ×1.05 | 6→6 |
| fpv_carrier | 500 | ×1.00 | ×1.12 | 560 | fpv_swarm KEEP | — | — | 7→7 |
| aa_vehicle | 350 | ×1.00 | ×1.12 | 392 | flak_35 (direct) | ×1.00 | ×1.08 | 4→4 |
| sam_launcher | 691 | ×1.00 | ×1.10 | 760.1 | buk_launcher KEEP | — | — | 8→8 |
| command_vehicle | 668 | ×1.00 | ×1.12 | 748 | — (support, no weapon buff) | — | — | 7→7 |
| ew_jammer | 468 | ×1.00 | ×1.12 | 524 | — | — | — | 6→6 |
| mine_layer | 518 | ×1.00 | ×1.12 | 580 | — | — | — | 6→6 |
| ammo_carrier | 520 | ×1.00 | ×1.18 | 613.6 | — | — | — | 4→4 |
| engineer_vehicle | 800 | ×1.10 (880) | ×1.18 | 944 | — | — | — | 3→3 |
| supply_truck | 700 | ×1.00 | ×1.15 | 805 | — | — | — | 0→0 |
| mortar_carrier | 320 | ×1.00 | ×1.12 | 358.4 | mortar_120 KEEP (fire-support rule, not this addendum) | — | — | 4→4 |
| recon_drone | 382 | ×1.00 | ×1.20 | 458.4 | recon_missile KEEP | — | — | 7→7 (base CP>5, KEEP) |
| strike_drone | 400 | ×1.00 | ×1.18 | 472 | drone_missile (direct) | ×1.00 | ×1.10 | 11→11 (base CP>7, KEEP) |
| scout_heli | 518 | ×1.15 (596) | ×1.18 | 611 | minigun (direct) | ×1.073 | ×1.08 | 6→7 |
| attack_helicopter | 700 | ×1.15 (805) | ×1.15 | 805 (no change) | heli_gun/heli_rockets/hellfire_standoff | ×1.08 | ×1.08 (no double-buff) | 11→11 |
| fighter_jet | 600 | ×1.15 (690) | ×1.12 | 672 (reduced) | air_to_air / fighter_cannon KEEP | — | — | 15→15 |
| attack_jet | 650 | ×1.15 (748) | ×1.15 | 748 (no change) | jet_cannon/s8_pods/kh29 | ×~1.08 | ×~1.08 (no double-stack) | 23→23 |
| stealth_fighter | 600 | ×1.15 (690) | ×1.15 | 690 (within 1.12-1.15, no change) | no separate ground-attack primary identified | — | — | 16→16 |
| heavy_bomber | 1400 | ×1.20 (1680) | ×1.20 | 1680 (no change) | bomber_payload (bomb rule, not this addendum) | ×1.30 | ×1.30 | 29→29 |
| sky_gunship | 1400 | ×1.15 (1610) | ×1.15 | 1610 (no change) | — | — | — | 29→29 |
| twin_rotor_gunship | 1400 | ×1.15 (1610) | ×1.15 | 1610 (no change) | — | — | — | 18→18 |
| heavy_turret | 2800 | ×1.30 (3640) | ×1.25 | 3500 (reduced) | turret weapon (outgoingDamageMult) | ×1.10 | ×1.10 (no change) | — |
| heavy_turret.bastion | 4340 | ×1.30 (5642) | ×1.25 | 5425 (reduced) | (same mechanism, inherited) | ×1.10 | ×1.10 | — |
| drone_hangar | 2200 | ×1.30 (2860) | ×1.25 | 2750 (reduced) | fpv_* (outgoingDamageMult) | ×1.10 | ×1.10 | — |
| missile_battery | 1900 | ×1.30 (2470) | ×1.25 | 2375 (reduced) | missile KEEP | — | — | — |
| targeting_station | 700 | ×1.20 (840) | ×1.15 | 805 (reduced) | none (no weapon) | — | — | — |
| mg_bunker | 1500 | ×1.20 HP / ×1.08 wpn | ×1.20 HP (no change) / ×1.10 wpn | 1800 / outgoingDamageMult 0.6695 | bunker_hmg | ×1.08 | ×1.10 | — |
| mg_bunker.twin | (inherits 1500) | ×1.08 wpn | ×1.10 wpn | outgoingDamageMult 0.554 | bunker_hmg_twin | ×1.08 | ×1.10 | — |
| mg_bunker.flame | (inherits 1500) | ×1.08 wpn | ×1.10 wpn | outgoingDamageMult 0.3573 | bunker_flame | ×1.08 | ×1.10 | — |

Units named by the addendum whose current values **already matched the new target exactly** and received **no edit**
this pass (confirmed by the original-baseline diff, listed for completeness): `guard_tower`, `recoilless_gun_tower`
(small combat tower, ×1.20 HP / ×1.08 weapon), `atgm_tower`, `gun_turret`, `rocket_turret`, `one_shot_atgm_tower`
(medium combat tower, ×1.25 HP / ×1.10 weapon), `aa_turret`, `aa_gun_tower`, `c_ram`, `laser_ad_station`,
`drone_net_tower`, `ew_tower`, `flare_tower`, `flare_searchlight_tower`, `barrage_balloon`, `shield_tower`,
`shield_tower.ward`, `shield_tower.bulwark` (body HP +10%, dome/ward pool untouched), `elite_tank_destroyer`,
`laser_tank` (already damage 14 / Pen 5), `railgun_truck` (already Pen 5, damage KEEP), `recoilless_jeep` weapon
(damage/cooldown already canonical), `ifv` ATGM (already Pen 4, damage KEEP), `recon_drone` weapon (already Pen 3).

## 2. Primary-weapon audit (§34)

| unit_id | primary role | primary weapon ID | old dmg | new dmg | secondary weapons | changed? | reason |
|---|---|---|---|---|---|---|---|
| armored_car | main gun | autocannon_25 → **autocannon_25_car** | 17 | 19.55 | mg_coax_long | NO | §2 +15%; variant made so tower_ac25 (inherits autocannon_25's damage) and pt14_dd_v25 stay untouched |
| scout_jeep | main gun | mg_jeep → **mg_jeep_scout** | 9.5 | 10.45 | none | NO | §2 +10%; variant so river_patrol_boat, supply_truck and rocket_technical's `mg_jeep_selfdef` (inherits mg_jeep) stay untouched |
| rocket_technical | rocket pod | technical_rockets | 49.5 | 56.9 | mg_jeep_selfdef | NO | §2 +15%; weapon id unique to this vehicle, direct edit safe |
| zu23_technical | AA/AT gun | zu23 → **zu23_cheap** | 3.5 | 4.2 | none | NO | §2 +20%; variant so moloch (boss, secondary MG x2) stays untouched |
| recoilless_jeep | main gun | recoilless_106 | 314 | 314 (KEEP) | none | NO | §2 explicit damage/cooldown KEEP; Pen already 4 from pass 2 |
| light_tank | main cannon | gun_57mm → **gun_57mm_lt** | 110 | 121 | mg_coax, gun_launched_atgm | NO | §3 +10%; variant so daedalus (boss secondary gun x2) stays untouched |
| ifv | main autocannon | ifv_30 | 22 (inherited) | 23.76 (own override) | mg_coax, atgm | NO | §4 +8%; own `damage` field added so autocannon_30 (heavy_tank/elite_heavy_tank coax, elite_apc, daedalus boss) stays untouched; ATGM Pen already 4, damage KEEP |
| wheeled_gun | main gun | gun_105_wheeled | 369 | 387.45 | mg_coax, hmg_roof | NO | §5 +5%; weapon id unique, direct edit |
| tank_destroyer | main gun | gun_105_long | 371 | 389.55 | hmg_roof | NO | §6 +5% weapon, HP final +10% vs original (not re-stacked on pass 2's +5%) |
| elite_tank_destroyer | main gun | gun_105_apfsds | 371 | 371 (KEEP) | hmg_roof | NO | §7: Pen 5 already set, no new damage buff |
| laser_tank | main weapon | focus_laser | 14 | 14 (KEEP) | none | NO | §7: already at damage 14 / Pen 5 from pass 2 |
| railgun_truck | main weapon | railgun | 510 | 510 (KEEP) | none | NO | §7: already Pen 5, no extra multiplier |
| flame_tank | main weapon | flamethrower | 21 | 22.05 | mg_coax | NO | §8 +5%; weapon id unique, direct edit |
| fpv_carrier | drone swarm | fpv_swarm | 140 | 140 (KEEP) | hmg_selfdef_18 | NO | §9: damage/cadence KEEP by design |
| aa_vehicle | AA gun | flak_35 | 26 | 28.08 | sam | NO | §10 +8%; weapon id unique, direct edit; SAM damage explicitly KEEP |
| sam_launcher | SAM | buk_launcher | KEEP | KEEP | none | NO | §11: damage/Pen KEEP |
| recon_drone | recon missile | recon_missile | 190 | 190 (KEEP) | none | NO | §14: damage/Pen 3 KEEP |
| strike_drone | ground-attack missile | drone_missile | 260 | 286 | guided_bomb | NO | §15 +10%; weapon id unique (children `pt14_th_jagm`/`pt14_co_spike` already have their own damage); guided_bomb (bomb rule) untouched |
| scout_heli | main gun | minigun | 5.5→5.9 (pass1) | 5.94 | scout_rockets | NO (rocket already at exact +8%, left as-is) | §16: +8% main gun vs original baseline; scout_rockets was already exactly ×1.08 (30→32.4), no change needed |
| attack_helicopter | cannon/rocket/missile | heli_gun / heli_rockets / hellfire_standoff | — | — (no change) | stinger_atas, apkws_rocket | NO | §17: already ~+8% from the prior aircraft pass; "do not double-buff", final stays ≈+8-10% vs original |
| fighter_jet | AAM / cannon | air_to_air / fighter_cannon | KEEP | KEEP | wvr_aam | NO | §18: weapons KEEP; only HP corrected down to +12% |
| attack_jet | cannon/rocket/missile | jet_cannon / s8_pods / kh29 | — | — (no change) | r60, jet_bombs (bomb rule) | NO | §19: already ~+8% from the prior pass, within the +8-10% band, not re-stacked |
| stealth_fighter | air-superiority / bomb / gun | air_to_air (KEEP) / guided_bomb (bomb rule) / fighter_cannon (KEEP) | — | — | — | NO | §20: no distinct dedicated ground-attack primary identified beyond the bomb-rule payload; not blanket-buffed |
| heavy_bomber | bomb payload | bomber_payload | 420 | 546 (already ×1.30, prior pass) | bomber_tail_guns, air_cruise_missile | NO | §21: bomb rule only, kept as-is |
| sky_gunship / twin_rotor_gunship | — | gunship_105 / heli_gun | — | — | gunship_40mm, gunship_25mm, agl_40 | NO | §21: HP-only buff, already at +15%, no further weapon change |
| mg_bunker / .twin / .flame | bunker gun | bunker_hmg / bunker_hmg_twin / bunker_flame | effective ×1.08 (pass1) | effective ×1.10 | none (secondary empty) | NO | §23: raised each branch's own `outgoingDamageMult` from the generic small-tower +8% to the MG-bunker-specific +10%; each branch has no secondary weapon so the multiplier cannot leak |
| rocket_turret / gun_turret / heavy_turret / heavy_turret.bastion / drone_hangar / atgm_tower / one_shot_atgm_tower | tower primary | turret_rockets / turret_gun_* / bastion/coastal branches / fpv_* / tower_kornet / one_shot_kornet | — | — (no change, already +8/+10% from pass 1) | — | NO | §22/24-27: only the three **large towers** (heavy_turret, heavy_turret.bastion, drone_hangar) had their HP corrected from the old +30% down to +25% per §22; weapon multipliers (+8/+10%) already matched and were left alone |
| missile_battery | SAM | patriot/… (inherits) | KEEP | KEEP | — | NO | §27: HP corrected 1900×1.30→1900×1.25 (2470→2375); damage KEEP |
| targeting_station | none | — | — | — | — | NO | §30: utility-tower "targeting" HP corrected 700×1.20→700×1.15 (840→805); no weapon |

## 3. Confirmations (§39 items 12-14)

- **SAM/AA/utility exceptions respected:** `sam` (aa_vehicle secondary), `buk_launcher` (sam_launcher), `recon_missile`
  Pen, `atgm` (ifv) Pen/damage all untouched; no SAM/missile-tower damage field touched anywhere in this pass.
- **No coax/HMG/self-defense weapon buffed:** `mg_coax`, `mg_coax_long`, `hmg_roof`, `mg_jeep_selfdef`,
  `hmg_selfdef_18`, `stinger_atas`, `apkws_rocket`, `r60`, `wvr_aam` — none of these ids appear on the left side of
  any edit in this pass (verified by the field-level diff against the original baseline, `full_diff2.txt`).
- **No previously-approved multiplier double-applied:** every HP/weapon target above was computed as
  `original_baseline × final_addendum_multiplier`, read straight off the pre-v3 `balance.json` vs. the original
  baseline diff (`balance_final_changes.json`/pass-1 and pass-2 reports), not by multiplying the addendum's number
  onto the already-buffed current value. Confirmed case-by-case above (tank_destroyer, flame_tank, scout_heli,
  engineer_vehicle, fighter_jet, heavy_turret family, mg_bunker family, missile_battery, targeting_station all show
  their pass-1/2 multiplier explicitly before the new final one).
- **Boss armour:** programmatic diff of every vehicle's `armour` field between the original baseline and the v3
  working tree shows **zero differences** (same check as pass 2). No boss weapon, projectile speed, or splash value
  was touched (that rescan is a separate, parallel branch per the brief).
- **§32 explicit-unchanged list:** `coastal_battery`, `bunker_shelter_tower`, `blast_wall`, `bulwark_post` — zero
  diffs against the original baseline, confirmed.

## 4. Regression (§35-38, headless only, no Unity)

- `dotnet build Tools/simbuild/Sim.csproj -c Release`: **0 errors** (3 pre-existing warnings, unrelated).
- `dotnet build Tools/simbuild/regress/Regress.csproj -c Release`: **0 errors**.
- `MachineBrigade.Tests.EditMode.exe` (the regress harness) run in modes `ttk`, `pd`, `aps`, `pressure`, `barrage`,
  before (pre-v3 `balance.json`, i.e. pass-1+2 state) / after (this pass), 3 seeds each:
  - **pressure** and **barrage**: byte-identical before/after (no scripted-barrage or sustained-pressure field
    touched).
  - **ttk** (armour-tier duels/sorties/towers): cheap units now take noticeably longer to kill by unchanged
    opposition — `MG bunker vs 3 armoured cars` 23.4s→32.6s, fire-support-vs-armoured-car/IFV lines all up
    15-30% (e.g. `2 mortar carriers vs 4 armoured cars` 68.9s→81.9s, `Elite MLRS (cluster) vs 4 armoured cars`
    36.4s→71.7s) — matches the addendum's "cheap unit should survive edge splash/incidental pressure" goal.
    Mid-tier units hit a bit harder: `Assault squad (2 MBT+IFV) vs heavy turret` 73.8s→67.6s,
    `TD vs Titan (front)` 97.4s→92.7s. The two large-tower lines got easier to clear
    (`Assault squad vs heavy turret` and `Bomber vs heavy turret`), matching the §22 +30%→+25% correction.
  - **pd/aps** (point-defence throughput, raw output): all deltas are the expected +8/+10% bumps on
    ifv/aa_vehicle/light_tank/strike_drone's primary weapon, no intercept-rate or mechanic change.
  - **One result flagged for the owner, not auto-fixed:** `Army vs Earth Borer (mini boss)` survival rate dropped
    from 2/3 seeds to 1/3 in the `ttk` boss set, even though no boss stat was touched. Likely a knock-on timing
    effect from several army units' HP/weapon changes shifting when losses happen during that boss's attack
    pattern; flagging rather than adjusting army composition or boss values, which are out of this addendum's scope.
- **Campaign audit (§38, measure only, no campaign.json edit):** `campaign.json` (generated by `Tools/campaign`)
  references changed canonical ids extensively — substring counts: `ifv` 321, `attack_helicopter` 137,
  `tank_destroyer` 132, `light_tank` 99, `sam_launcher` 101, `aa_vehicle` 167, `strike_drone` 60, `armored_car` 56,
  `flame_tank` 53, `mortar_carrier` 75, `fpv_carrier` 71, `wheeled_gun` 42, `fighter_jet` 43, `rocket_technical` 38,
  `recon_drone` 27, `mine_layer` 29, `scout_jeep` 23, `ew_jammer` 25, `zu23_technical` 13, `command_vehicle` 19,
  `engineer_vehicle` 14, `ammo_carrier` 8, `scout_heli` 8. Since campaign missions reference these by canonical id
  (resolved against `balance.json` at runtime, not baked-in stats), the HP/weapon buffs apply automatically to both
  player and AI/scripted use of these units with no campaign.json edit needed or made. Expect scripted militia and
  AI decks using these ids to hit a little harder and die a little slower; no campaign-only nerf was applied, per
  the brief.

## 5. Open owner decisions

1. **"Heavy/special fortress-style tower" (§22) has no confident id match.** `spawn_bastion` (hp 5000, weapon
   `bastion_gun`, shares the `heavy_turret` model) was the only candidate but has no `fort`/`rebuildCp`/`branches`
   fields like every real player tower — it looks boss-adjacent/scripted rather than a buildable tower, so it was
   **left untouched**. Confirm whether it should get the heavy/special-tower treatment (+20% HP, weapon +10% via a
   `spawn_bastion`-only `bastion_gun` variant, since `bastion_gun` is shared with `headquarters`).
2. **`supply_truck` (§12 "supply vehicle")** has `cp: 0` and `captureRate: 0` — looks like a scripted/event spawn,
   not a deck-purchasable unit. Applied the conservative end of the range (+15% HP, 700→805) rather than skipping it;
   confirm this is the right unit for that addendum example (as opposed to `ammo_carrier`, which is also named
   separately and was buffed +18%).
3. **`cp_relay`** was left unchanged: it is not literally named among §30's utility examples (EW/radar/flare/
   targeting/drone-net) and pass 1 classified it under a separate "structure HP" rule (×1.20) rather than the tower
   spec. If the owner wants it folded into the utility-tower bucket too, it would drop from 720 to 690 (600×1.15).
4. **`Army vs Earth Borer (mini boss)` survival regression** noted in §4 above — flagged, not altered.
5. Boss missile/projectile-speed rescan requested in the same owner message is **not** part of this brief (another
   agent is doing it on a separate branch) and was not touched here.
