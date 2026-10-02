# Prompt 29 report: balance round 2 (v2), applied in the cloud session

Source: `Docs/balance/Machine_Brigade_Can_bang_dot2_v2.xlsx` (sha256 4bef428df8e2...), exported to `manifest_v2.json`;
applied by `Tools/balance/p29_apply.py` (log `apply_log_p29.md`, state `apply_state_p29.json`). Theory only: nothing was
run but the Python tools and the dotnet compile check of the Sim. Decisions: DECISIONS "Prompt 29 0" to "Prompt 29 L8".

## Bundles (157)

| outcome | count | bundles |
|---|---|---|
| OK (applied) | 128 data bundles + 9 code | E1; B0 x7; B1 x97 (sky_gunship last, pass 7); B2-FLR x17; B2-APS x4 (trophy is code); B3-AI (code); G1 (code + data); S01-S09 (code) |
| ALREADY_APPLIED (whole bundle) | 0 | (many B1 bundles had ALREADY_APPLIED rows: outgoingDamageMult already 1.0) |
| CONFLICT | 0 | (two false CONFLICT rows from re-checking B0 after B1 were a tool bug, fixed: see DECISIONS L4) |
| BLOCKED | 0 | |
| SKIPPED (HOLD) | 13 | E2, B5 x12 |
| SKIPPED (REJECT) | 7 | R-supergun, R-radar, R-floor, R-typhon, R-icarus, R-round-hover, R-speed-new |

## Checks

| check | result | file |
|---|---|---|
| C01 field map | every Manifest path mapped; new keys outgoingDamageMult, dropDelay, flareCharges, flareRecharge, apsCapability, interceptionMode, economy.bankByMode | `Docs/balance_field_map.md` |
| C03 zero-CP cards | not bought by the AI; deck filter is UI (local); the support's UAV counts in the air cap, not in supply | `Docs/checks/zero_cp.md` |
| C05 flares | all 23 baselines match | `Docs/checks/flare_baseline.md` |
| C06 APS | one code path; bosses carry the same `aps`; classified, numbers kept | `Docs/checks/aps_audit.md` |
| C07 iron_beam | 0.8 s in the data | `Docs/checks/aps_audit.md` |
| C09 weapon map | exact ids only, no fuzzy match in the game | `Docs/checks/weapon_map.md` |
| C10 AA vs aircraft | x1.3 confirmed (Fragmentation x1.3, no overmatch on aircraft) | `Docs/checks/aa_multipliers.md` |
| C11 Boss Hunt | main-rank bosses count as mains: 17 / 24 | `Docs/checks/boss_hunt.md` |
| C12 aircraft return | one condition in `TacticalAi.Refit`; removed | `Docs/checks/aircraft_rtb.md` |
| C13 attack flags | none stored; S05 adds overrides | `Docs/checks/attack_flags.md` |
| C15 runtime cost | spend/afford only; one classification (AI shares) moved to base CP | `Docs/checks/runtime_cost.md` |
| C16 AoE list | 3 listed without splash (missile blasts), 28 splash weapons not listed: reported only | `Docs/checks/aoe_list.md` |

Not done (optional, prompt section 3): **C02** (the 20 supply questions: needs reading the supply/refund/catch-up code
end to end; E2 stays HOLD so nothing waits on it), **C04** (entity budget), **C08** (tracing round 1's unplanned
changes through git history), **C14** (role metrics for cheap cards): left for a later session to save tokens; none
blocks a bundle.

## Decisions made here (owner may review)

1. HP rows compare and write in data units (effective / toughness, one ROUND_HALF_UP).
2. `outgoingDamageMult` is new rather than the existing `weaponDamage` (ground-only, already used).
3. The bank by mode is data holding the manifest's [from, to], moved only where the mode set the "from" bank; Vault
   derived (+15).
4. "Xem lại" is read from status columns only (the B0 rows quote it in their reason).
5. New SELF_APS on titan_tank gets 20 m (the sheet "APS"; no manifest radius row).
6. Interception modes set explicitly for iron_beam, sea_corvette, sea_cruiser, icarus_mk0 (PointDefense) and
   next_gen_tank (SelfAps); inferred elsewhere.
7. The heat-decoy module no longer works as its own dispenser (D6).
8. Vehicle missile loads (5.4) set per vehicle (none existed); `atgm` stays shared.
9. Gungnir: health 156,900 data (chapter-11 main table), bombard every 45 s, explicit Global targeting (it never had a
   range check).
10. E1 not cross-checked against v1 (file missing).

## Waits for the local session

Unity compile, CatalogCheck, EditMode (`BalanceRound2Tests`, `AircraftReturnTests`, updated `Prompt25BossTests`,
`WorldModelTests`), `python -m unittest Tools/balance/test_p29.py`, card renders, the PDF (`build_doc.py`: new section
"Cân bằng đợt 2", appendix "Lịch sử đo"), Blender details (5.5), UI items in `Docs/ai/LOCAL_TODO.md`.
