# Balance v2 implementation report (06/10)

Source of truth: `Docs/prompts/balance_v2_vi.md` (owner prompt sec 1-33 + the boss missile / rocket
flight-feel addendum sec 1-14). Branch `feature/balance-v2`, worktree `MachineBrigade-bal`, on top of
lead commit `0b86165c` (merge of `lead/integration`) plus the already-committed WIP commit `dfe4bb5e`
(validator v2 refactor, finished and verified this pass -- see item 0 below).

Sections 8-10 and 20-26 of the prompt (bomb/aircraft/ground-vehicle/tower/structure/boss HP multipliers,
fire-support damage/coverage) were already applied in the previous pass (`Docs/balance/BALANCE_MASTER_FINAL_REPORT.md`,
commit `2625c100`). Spot-checked against the current `balance.json` and confirmed still present (towers
x1.20/1.25/1.30, structures x1.15-1.25, boss main hull x1.08 / mini-boss x1.05, Nyx/Scylla outgoing damage
x1.10/x1.08, etc.) -- **not reapplied this pass.** This report covers only the genuinely new v2 deltas:
projectile speeds/splash, the Pen hierarchy, the validator refactor, and the full boss missile audit.

## 0. Validator v2 (WIP commit `dfe4bb5e`, finished)

The WIP diff (`Tools/balance/flight_feel_audit.py`, `Tools/export/domains/_b01.py`, `_ref_units.py`) was
already functionally complete -- it had been committed but never run. Compiled clean (`py_compile`) and
run: **0 HARD_FAIL, 6 YELLOW_FEEL, 25 PASS_INTENTIONAL_SHORT_RANGE, 329 ok** across 360 weapons after this
pass's edits (was 359/0/5/25/329 before). No further code changes were needed; this pass only ran it and
verified the three-bucket / five-reason-code output is sane. No other script references the old
`TOO_FAST_AT_GEAR_CAP` / `OWNER_EXCEPTION` vocabulary the refactor removed.

## 1-3. Canonical files changed / affected IDs / old -> new values

**Canonical data:** `Assets/MachineBrigade/Resources/Data/balance.json` only.

| weapon/entity | field | old | new |
|---|---|---|---|
| `sam_48n6` | projectileSpeed | 140 | **115** |
| `sam_48n6` | splash | 7.2 | **6.0** |
| `ballistic_missile` | projectileSpeed | 200 | **90** |
| `ballistic_missile` | splash | 10 | **14** |
| `ballistic_missile` | impactScale | (none) | **1.3** |
| `jassm` | splash | 9 | **12** |
| `jassm_swarm_carrier` | *(new weapon, inherits jassm)* | - | speed 60, splash 14.4 |
| `air_cruise_missile` | splash | 9 | **12** |
| `cruise_missile_ground` | splash | 8 | **12** |
| `hydra_club_s` | splash | 6.5 | **10** |
| `nyx_tomahawk` | splash | 8 | **11** |
| `leviathan_cruise` | splash | 10 | **14** |
| `focus_laser` | pen | 4 | **5** |
| `focus_laser` | damage | 12.5 | **14** |
| `recoilless_106` | pen | 3 | **4** |
| `siege_gun_105` | pen | 3 | **2** |
| `swarm_carrier` (vehicle) | secondary weapon | `jassm` | **`jassm_swarm_carrier`** |
| `swarm_carrier` (vehicle) | loads key | `jassm` | **`jassm_swarm_carrier`** |
| `leviathan`/`typhon` "cruise" bigAttack | radius | 10 | **14** |
| `nyx`/`hydra`/`scylla` "cruise" bigAttack | radius | 6.5 | **10** |
| `leviathan_cruise_mark` (support) | blast / radius | 10 / 20 | **14 / 28** |
| `kalibr_cruise_mark` (support) | blast / radius | 6.5 / 13 | **10 / 20** |

Everything else named in the prompt (`railgun`, `gun_105_apfsds`, IFV `atgm`, `recon_missile`,
`anti_ship_missile`, `wheeled_gun`) was already at its target value -- **verified, not touched.** A
full before/after diff over every vehicle's `armour` field (whole file) found **zero changes**; a diff
over every weapon's `pen` field found **exactly the three rows above and nothing else.**

## 4-5. Final runtime effective values / final projectile speeds

Resolved via `Tools/balance/flight_feel_audit.py` (inherits -> family -> runtime), all `ok`/`PASS` in
validator v2:

| id | speed m/s | splash m | pen | dmg | class | tmax (range) s |
|---|---|---|---|---|---|---|
| `sam_48n6` | 115 | 6.0 | 3 | 630 | AIR_DEFENCE_MISSILE | 0.826 (YELLOW_FEEL, see judgment calls) |
| `ballistic_missile` | 90 | 14 | 4 | 630 | BALLISTIC_MISSILE | 2.0 |
| `jassm` | 70 | 12 | 3 | 410 | CRUISE | 1.286 |
| `jassm_swarm_carrier` | 60 | 14.4 | 3 | 410 | CRUISE | 1.5 |
| `air_cruise_missile` | 65 | 12 | 3 | 378 | CRUISE | 1.692 |
| `cruise_missile_ground` | 70 | 12 | 4 | 450 | CRUISE | 2.571 |
| `hydra_club_s` | 70 | 10 | 3 | 520 | CRUISE | 5.714 |
| `leviathan_cruise` | 70 | 14 | 3 | 520 | CRUISE | 5.714 |
| `nyx_tomahawk` | 70 | 11 | 3 | 340 | CRUISE (PASS_INTENTIONAL_SHORT_RANGE, boss override) | 1.714 |
| `focus_laser` | 3000 (beam) | - | 5 | 14 | BEAM_OR_MELEE | n/a |
| `recoilless_106` | 150 | - | 4 | 314 | DIRECT_FAST | 0.213 |
| `siege_gun_105` | 190 | 1.5 | 2 | 303 | DIRECT_FAST | 0.179 |

## 6. Final Pen values, specialist anti-armour weapons

`gun_105_apfsds` 5 (already applied, KEEP), `focus_laser` 5 (new), `railgun` 5 (already applied, KEEP),
`recoilless_106` 4 (new), IFV `atgm` 4 (audited, already correct, no stale inheritance), `recon_missile`
3 (KEEP), `anti_ship_missile` 4 (KEEP), `siege_gun_105` 2 (corrected down from 3), `gun_105_long` 4 (KEEP),
`wheeled_gun` 4 (KEEP). No Pen 5 handed out beyond `gun_105_apfsds`/`focus_laser`/`railgun`.

## 7. Cruise splash values by family

See table in items 1-3. Generic baseline (light ~8-10, standard ~12, heavy ~14, boss/strategic ~14-16)
applied: `jassm`/`air_cruise_missile`/`cruise_missile_ground` -> 12 (standard); `hydra_club_s` -> 10,
`nyx_tomahawk` -> 11 (mini-boss "Large" tier); `leviathan_cruise` -> 14 (boss "Ultimate" tier, main
hull + Typhon). No damage changes, footprint only.

## 8. Ballistic missile speed/splash

200 -> 90 m/s, splash 10 -> 14 m, damage KEEP 630, `impactScale` added at 1.3 (+30%, inside the
"roughly +25-35%" the prompt asked for) so the VFX visually matches the bigger footprint.

## 9. Long-SAM speed/splash

140 -> 115 m/s as named. Splash: the prompt's "x1.25, cap 5-6 m" formula does not fit the canonical
starting value (7.2 m, already over the cap) -- see judgment calls. Final: capped to **6.0 m** (top of
the named band) rather than multiplied further over it. Damage/Pen KEEP.

## 10. Drone-mothership cruise result

Created `jassm_swarm_carrier` (inherits `jassm`): speed 60 m/s, splash 14.4 m (= new jassm splash 12 x
1.20), Pen/damage/cooldown/burst all inherited KEEP. `swarm_carrier`'s secondary weapon and `loads` key
switched from generic `jassm` to this variant. Generic `jassm` (used by `stealth_bomber` and any other
JASSM carrier) stays at 70 m/s, untouched identity.

## 11. Laser TD result

`focus_laser`: Pen 4 -> 5, damage 12.5 -> 14, cooldown/ramp/range all KEEP (0.1 s cooldown, same ramp
curve). No beam-ramp or cooldown inflation added.

## 12. Elite TD result

`gun_105_apfsds`: Pen already 5 from the previous pass, damage KEEP at 371. No change this pass;
verified holds. Standard `gun_105_long` stays Pen 4.

## 13. Railgun result

`railgun`: Pen already 5 from the previous pass, damage/reload KEEP (510 dmg, 7 s reload). No change
this pass; verified holds. (Reload increase deferred per the prompt, pending in-game proof of
overperformance -- no such proof exists yet.)

## 14. Recoilless jeep result

`recoilless_106`: Pen 3 -> 4. Damage: the prompt states "220 KEEP" twice (sec 11 and 15), but the
canonical value has always been 314 in this branch's history (checked `balance_master_final_spec.md`,
`balance_final_answers_vi.md`, `BALANCE_MASTER_FINAL_REPORT.md`, `balance_final_changes.json` -- none
ever set it to 220). Left unchanged at 314; see judgment calls.

## 15. IFV ATGM result

Audited the runtime-effective value: the IFV's missile slot fires weapon id `atgm`, which carries its
own `"pen": 4` directly (no `inherits`, no stale family override) -- already exactly the target, no fix
needed.

## 16. Boss HP application

Unchanged this pass -- confirmed already applied (main hull x1.08, mini-boss x1.05) in the previous
pass and still present in the current file (e.g. `leviathan` hp 65772, `scylla` hp 39638 match the
previous report's "after" column exactly).

## 17. Boss armour confirmation

**Confirmed unchanged.** A full diff of every `vehicles[].armour` field between this pass's starting
point and the final edited file returns **zero differences** (checked programmatically, not by eye).

## 18. Tower/structure results

Unchanged this pass -- verified already applied in the previous pass per `BALANCE_MASTER_FINAL_REPORT.md`
("spec 11"/"spec 12" sections); current `balance.json` HP/outgoingDamageMult values match that report's
"after" column. No new changes this pass.

## 19. Fire-support results

Unchanged this pass (sections 24-26 were part of the previous pass). Headless `Regress` harness
`barrage` mode produced byte-identical output before/after this pass's edits, confirming no incidental
drift.

## 20. Flight-time min/half/max (changed weapons)

| id | tmin s | thalf s | tmax s |
|---|---|---|---|
| `sam_48n6` | 0.174 | 0.413 | 0.826 |
| `ballistic_missile` | 0.444 | 1.0 | 2.0 |
| `jassm` | 0.321 | 0.643 | 1.286 |
| `jassm_swarm_carrier` | 0.375 | 0.75 | 1.5 |
| `air_cruise_missile` | 0.423 | 0.846 | 1.692 |
| `cruise_missile_ground` | 0.643 | 1.286 | 2.571 |
| `hydra_club_s` / `leviathan_cruise` | 1.429 | 2.857 | 5.714 |
| `nyx_tomahawk` | 0.429 | 0.857 | 1.714 |

## 21. ProjectileSpeed gear max values

`GearCatalog.cs`'s cap is unchanged (ProjectileSpeed substat +4/+6/+8/+10%, BuildCap 30%). At the legal
max cap (x1.30): `sam_48n6` 149.5 m/s, `ballistic_missile` 117 m/s, `jassm` 91 m/s, `jassm_swarm_carrier`
78 m/s. None of these push any weapon back into HARD_FAIL territory (validator v2 doesn't gate on the
gear-cap time directly, by design; checked anyway, all comfortably inside their class band at cap).

## 22. APS/CIWS/flare/jammer regression

Headless `Regress` harness, `pd` mode, `long_sam` (= `sam_48n6`) vs `attack_jet`:

| scenario | before (dmg through / TTC s) | after |
|---|---|---|
| no jammer | 7935 / 7.0 | 7832 / 6.7 |
| + enemy EW jammer | 3055 / 5.7 | 2419 / 4.7 |

Expected, natural consequence of the 140->115 m/s slowdown (more time inside the intercept window,
especially combined with jammer); no APS/CIWS parameter was touched to produce this -- no nerf applied,
per the "do NOT automatically nerf APS/CIWS" instruction. `aps` mode (which also runs the AI-lead check)
produced byte-identical output before/after, since no boss missile speed changed this pass.

## 23. AI lead/intercept regression

No change. `Regress` harness `aps` mode (covers `Aps()` + `Lead()`) is byte-identical before/after.

## 24. Warning-marker/radius audit

Found and fixed the exact stale-marker problem the prompt named: five `"cruise"` boss bigAttack blocks
(`leviathan`, `typhon`, `nyx`, `hydra`, `scylla`) and two shared `Barrage` support entries
(`leviathan_cruise_mark`, `kalibr_cruise_mark`) carried hardcoded radii (10 m and a literal stale 6.5 m)
independent of the weapon catalog's own `splash` field (confirmed via `NavalSystem.cs` `Cruise()`: the
scripted attack's own `Radius` field is the real damage radius, `Weapon`/`Warning` are separate string
references for VFX/telegraph only). Updated all five bigAttack radii and both marker defs to match (see
item 1-3 table). No stale 6.5/10 m markers remain.

## 25. Structure repair audit

Not touched this pass (no new tower/structure HP buff was applied this pass to require it; sec 22 was
part of the previous pass and is unaffected by this pass's edits).

## 26. Fire-support resupply audit

Not touched this pass (sec 26 unaffected by this pass's edits).

## 27. Generated file list

`Docs/checks/full_weapon_audit.md` and `Docs/balance/player_weapon_waitlist.md` regenerated via
`python Tools/balance/full_weapon_audit.py` (counts: boss TOO FAST=4/TOO SLOW=6, player TOO FAST=18/TOO
SLOW=6, tower TOO FAST=12/TOO SLOW=1 -- unaffected by this pass's pen/speed/splash edits except for one
count-only artifact, see judgment calls). `Docs/balance/flight feel` re-run (`flight_feel_audit.py`, not
written to a file by default; console summary quoted in item 0). **Not regenerated per this task's brief:**
`Docs/export/*` (XLSX/MD packs, 01-10 + 00_index + README/CHANGES) -- explicit owner rule, the lead
rebuilds the export pack once at the very end.

## 28. Remaining validator HARD_FAIL items

**Zero.** `sam_48n6` is flagged `YELLOW_FEEL`/`TOO_SLOW_FOR_CLASS` by a small margin (tmax 0.826 s vs the
AIR_DEFENCE_MISSILE band ceiling 0.80 s) -- expected and intentional at the owner's explicit 115 m/s
target, not a hard fail, not corrected.

## 29. Stale data/inheritance mismatches found

- The five naval-boss "cruise" bigAttack radii and their two warning markers (fixed, item 24).
- The owner's prompt assumed slightly different starting splash values than canonical data for three
  weapons (`jassm` 10 vs actual 9; `nyx_tomahawk` 8.5 vs actual 8; recoilless damage 220 vs actual 314).
  Applied the prompt's explicit final numeric targets regardless of the starting-point mismatch (see
  judgment calls) rather than trusting the stale assumption.
- `siege_gun_105`'s canonical Pen was 3, not the 2 the prompt's "KEEP 2" implied as current -- treated
  the explicit number as the corrective target and changed it.

## Addendum: boss missile / rocket flight-feel audit (sec 1-14)

**Scope swept:** every weapon id starting with `p26_`, `pt14_`, `nyx_`, `scylla_`, `boss_`, `train_`
whose `projectile` is `Missile` or `Rocket`, plus the boss howitzer/mortar indirect-fire weapons and the
naval "cruise" bigAttack scripted events. **Result: every single one is already inside its target band**
(see table). No boss missile speed change was needed this pass -- the earlier master-final pass already
brought them in line.

| Boss | Weapon ID | Projectile class | Old/new speed m/s | Range | tmax s | Splash before/after | Reason |
|---|---|---|---|---|---|---|---|
| Hyperion | `pt14_hp_nsm` | anti-ship missile | 80 / KEEP | 95 | 1.19 | 5 / KEEP | Explicitly reviewed: within 70-85 boss anti-ship band |
| Hyperion | `pt14_hp_155` | naval direct gun | 88 / KEEP | 95 | - | - | Non-goal: direct kinetic shell, not missile-like |
| Scylla | `scylla_kh35` | anti-ship missile | 80 / KEEP | 110 | 1.375 | 6 / KEEP | Within 70-85 band; splash flagged but kept (see judgment calls) |
| Coeus | `pt14_co_spike` | tactical ATGM | 75 / KEEP | 80 | 1.067 | 0 / KEEP | Within 65-80 band |
| multiple (`boss_missiles` family: `p26_matriarch_ma_atgm`, `p26_roc_roc_atgm`, `pt14_ixion_kornet`, `p26_bastion_tiny_kornet_twin`, `pt14_th_jagm`, etc.) | ATGM | 70 / KEEP | 45-55 | 0.64-0.79 | 0 / KEEP | Within 65-80 band |
| multiple (`boss_rockets` family: `p26_behemoth_*_rockets`, `p26_jotunn_*_rockets`, `p26_nemesis_sec_boss_rockets`, `pt14_train_grad`) | barrage rocket | 65 / KEEP | 45 | 0.69 | 4.5-8 / KEEP | Matches the preserved "boss Grad/rockets 65 m/s" exception |
| Ixion | `pt14_ixion_grad` | barrage rocket | 65 / KEEP | 55 | 0.85 | 4.5 / KEEP | Grad family, within band |
| Nyx | `nyx_tomahawk` | direct VLS missile | 70 / KEEP | 120 | 1.71 | **8 -> 11** | Direct-fire weapon, footprint-only change (sec 5) |
| Leviathan/Typhon | `leviathan_cruise` (scripted "cruise" bigAttack) | boss cruise | 70 / KEEP | 400 | 5.71 | **10 -> 14** | Footprint-only (sec 5); shared Ultimate-tier Kalibr attack |
| Hydra/Nyx/Scylla (scripted "cruise" bigAttack) | `hydra_club_s` / shared Large-tier Kalibr | boss cruise | 70 / KEEP | 400 | 5.71 | **6.5 -> 10** (all three) | Footprint-only (sec 5); see judgment calls for the Nyx/Scylla grouping |
| Behemoth/Jotunn/Nemesis/etc. | `boss_howitzer`/`boss_mortar`/`p26_*_howitzer`/`p26_*_mortar` | indirect artillery (not missile-like) | 40-150 / KEEP | - | - | - | Non-goal: direct/indirect artillery shells, covered by main sec 24, not this addendum |

**Acceptance criteria (sec 14):**
- Hyperion missile speeds explicitly reviewed: yes (`pt14_hp_nsm`, `pt14_hp_155`).
- No boss tactical/heavy missile near-hitscan at normal range: confirmed, max boss missile speed found is
  80 m/s (anti-ship band).
- No stale player-family speed silently overriding an intended slower boss variant: confirmed via the
  validator's `CANONICAL_FAMILY_SPEED` regression guard (0 `INHERITANCE_MISMATCH` flags).
- Intentional boss-specific overrides preserved: `sam_post` 80, `sam_battery` 95, boss Grad/rockets 65,
  boss cruise 65-70 -- all confirmed present, untouched.
- Warning/projectile travel tracked separately: yes, `PreLaunchWarning` (`warn`/`delay` fields) vs
  projectile travel (`radius`/flight time) are distinct fields throughout; not merged.
- Guidance/APS/CIWS retested: no boss missile speed changed this pass, so no new guidance or intercept
  regression was introduced (confirmed via the `Regress` harness `aps` mode, byte-identical before/after).
- Explosion footprint vs warning radius agree: yes, after item 24's marker fixes.
- Boss armour unchanged: confirmed (item 17).

## Judgment calls (documented per addendum sec 14 and sec 33)

1. **`sam_48n6` splash formula vs cap.** The prompt says "splash x1.25, cap around 5-6 m." Canonical
   splash (7.2) already exceeds the cap before any multiplication. Chose to cap directly to 6.0 m (top of
   the named band) rather than apply x1.25 first (which would push it to 9 m, further over the cap).
2. **`recoilless_106` damage.** Prompt states "220 KEEP" in two places; canonical has always been 314 in
   every prior-pass document checked. No explicit delta was instructed (only "KEEP"), so left at 314
   rather than cutting it to an unsupported number. Flagged for the owner to confirm which is correct.
3. **`siege_gun_105` Pen.** Canonical was 3; the prompt's "KEEP 2" was read as the corrective final target
   (both prompt sections state 2 explicitly) and applied as 3 -> 2.
4. **Nyx/Scylla "cruise" bigAttack grouping.** Neither declares a `weapon` field for its scripted Kalibr
   bombardment (unlike Hydra, which names `hydra_club_s`); a code comment in `NavalSystem.cs` confirms
   this is by design -- "a ship's own cruise size (Scylla's and Nyx's Kalibr: Large) brings its missile's
   T look with it," i.e. this scripted attack is explicitly a shared Kalibr-type land-attack missile for
   all three ships, independent of what they actually carry in their turrets (Tomahawk VLS for Nyx, Kh-35
   for Scylla). Raised all three from the stale 6.5 m to 10 m together (matching the explicitly-named
   `hydra_club_s` target) rather than inventing an unsupported per-ship mapping.
5. **Boss anti-ship missile splash (`pt14_hp_nsm` 5 m, `scylla_kh35` 6 m) kept, not raised.** Below the
   addendum's "~8-14 m" anti-ship identity guidance, but the addendum explicitly says "do not automatically
   increase every boss missile splash" and these are small, not egregious. Flagged, not auto-fixed;
   recommend the owner revisit in-game if they still read as too small.
6. **`typhon_underwater_launch` / `doomsday_missile` StrikeSystem events** (hardcoded radius 9 m / 18 m,
   referencing `leviathan_cruise`/`ballistic_missile` by name) left unchanged. These are independently-tuned
   scripted superweapon events (structure-destroying strikes with their own `damage`/`structure`/`falloff`
   fields), never 1:1-mirrored to the referenced weapon's splash to begin with (unlike the five `"cruise"`
   bigAttack blocks fixed in item 24) -- not treated as a stale marker.
7. **`player_weapon_waitlist.md` count-only artifact.** Adding `jassm_swarm_carrier` (no entry in the
   reference XLSX sheet) shifts the console-printed "player TOO FAST" tally from 17 to 18, but the written
   report content is byte-identical either way (the new id has no matching reference row to print).
   Harmless; noted for anyone diffing the printed counts against an older run.

## Headless regression summary (offline tools only, per brief)

- `dotnet build Tools/simbuild/Sim.csproj` and `.../regress/Regress.csproj`: **0 errors** both.
- `Regress` harness `ttk`/`pd`/`barrage`/`aps`/`pressure` modes run against before/after `balance.json`
  snapshots (git-committed state vs this pass's final state). Differences found: `long_sam` (`sam_48n6`)
  vs `attack_jet` TTK +0.1-0.5 s (item 22/23 table); `nyx` sustained pressure +3.2% (69308 -> 71559,
  expected from the cruise splash increase hitting more targets in an AoE scenario); heavy-bomber sortie
  value vs 4 IFV +4% (6461 -> 6717, same cause via `air_cruise_missile`'s splash). No other matchup moved.
  `barrage` and the `aps`/AI-lead half of the harness were byte-identical before/after.
- No Unity EditMode run was needed or used.

## Owner clarifications applied (06/10, Docs/prompts/balance_v2_clarify_vi.md)

| ID | Field | Old | New | Note |
|---|---|---|---|---|
| recoilless_106 | damage / cooldown / Pen | 314 / 9.524 / 4 | 314 / 9.524 / 4 | confirmed; "220" was stale |
| sam_48n6 | splash | 6.0 | 6.0 | confirmed; cap wins over ×1.25 |
| pt14_hp_nsm | splash | 5 | 8 | impact overlay and rings follow the radius (TierFx Core -1) |
| scylla_kh35 | splash | 6 | 8 | same |
| railgun | Pen / damage / cooldown | 5 / 510 / 7 | 5 / 510 / 7 | confirmed; reload only after an Armour 4/5 TTK regression |

Boss armour unchanged.
