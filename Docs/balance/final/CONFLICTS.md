# MB_FINAL_2026_10_04: conflicts found while applying

Per PLAN_APPLY.md: a manifest row whose expected_before (or entity) no longer matches ours is listed here with our current
value, and the bundle's derivation is applied to the current entity. Each lane adds its own section.

## F2 (lane B): boss weapon range overrides

The bundle's expected_before 0.0 on every `bossWeaponOverrides[...]` row is the override layer (new in F2), so "no override
yet" counts as matching; all 99 rows on pairs that still exist matched and were applied as given (Docs/export/CHANGES.md
"MB_FINAL F2"). Nine rows name a boss weapon that play-test 14 (04/10, after the bundle's snapshot) replaced:

| manifest rows | bundle value | ours now | applied (bundle rule on the replacement) |
|---|---|---|---|
| `bossWeaponOverrides[armored_train][boss_rockets].groundMinReach` | 14 (max 45 kept) | the rack fires `pt14_train_grad` (inherits boss_rockets, groundMinReach 14, range 45) | `pt14_train_grad`: groundMinReach 16 (geometry), maxRange 52 (ceil 16 x 3.2) |
| `bossWeaponOverrides[daedalus][p26_daedalus_sec_dae57]` groundMinReach / maxRange | 13 / 42 | the 57 mm twins are ventral turrets `pt14_dd_v57` (groundMinReach 0, range 28), drawn under the belly to fire down (owner, play-test 14 space lane) | none: ventral guns are the ship's close-in cover of its dead zone; the rule keeps close defence at min ~0, max = max(28, ceil(0 x 3.2)) = 28 |
| `bossWeaponOverrides[hyperion][p26_icarus_main_ic_coil]` groundMinReach / maxRange | 21 / 68 | coilguns replaced by twin 155 mm `pt14_hp_155` (groundMinReach 19, range 95) | `pt14_hp_155`: groundMinReach 27 (geometry, 2 mounts); maxRange 95 kept (>= ceil 27 x 3.2 = 87) |
| `bossWeaponOverrides[hyperion][p26_icarus_direct_ic_laser]` groundMinReach / maxRange | 18 / 58 | laser batteries refitted to reach straight down as `pt14_hp_vlaser` (groundMinReach 0, range 36) | none: ventral (as Daedalus's twins); min 0, max 36 |
| `bossWeaponOverrides[nyx][boss_railgun]` groundMinReach / maxRange | 39 / 125 | railgun replaced by `nyx_ags_155` (groundMinReach 33, range 80) | `nyx_ags_155`: groundMinReach 42 (geometry), maxRange 135 (ceil 42 x 3.2) |

Open for the owner: if the ventral guns should carry the bundle's numbers of the weapons they replaced (Daedalus 13 / 42,
Hyperion lasers 18 / 58) instead of min 0, add the two rows to `bossWeaponOverrides` (no code change).

# MB_FINAL_2026_10_04: conflicts between the manifest and our data

Rule (PLAN_APPLY.md): a row whose `expected_before` differs from our current value is listed here with our value, and the
bundle's derivation formula is applied to our value instead.

## F1 (lane A): 108 rows (every row but bossWeaponOverrides and campaign fixedDeck)

**Value conflicts: 0.** All 108 rows matched `expected_before` (inheritance resolved: `inherits`, then the weapon family
on top, as Catalog does; `None` = no value on the entity's own line, which matched for every `None` row).

Not conflicts, recorded so the reader does not trip on them (all applied as the bundle wrote them):

| row | field | note |
|---|---|---|
| M26 / M29 / M32 / M35 | `howitzer_fixed` / `casemate_155` / `gun_105_bunker_he` / `boat_rockets` splash | A weapon family's fields win over the weapon's line (Catalog.WeaponFamilies), so a splash on the line would not take effect. howitzer_fixed: its family already gives 7 (no edit). The other three get a copy of their family with the bundle's splash (`m284_155_mm_casemate` 8, `l7_105_mm_he_bunker` 5.5, `s_8_80_mm_boat` 3.5), named on the line. |
| M95-M98 | `naval_100` / `naval_127` cooldown | Heavy_Guns_Final lists burst 1, ours is burst 2 / 0.5 s (inherited from naval_76). The bundle's cooldown (cooldown / 0.7) was applied as written; with our burst the cycle grows x1.375 / x1.389 instead of x1.429 (DPS +4 % / +3 %). |
| M55 | `matchRules.modes.survival.text.timeLimit` | Text applied; the cadence (requires_code) is lane F3's. |
| M15 / M6 | `ixion` rank mini -> main, hp 72000 -> 98400 | The mini rank scaled health by 0.55 (bossRanks.mini.hp), the main rank does not: Ixion's health in play goes 39,600 -> 98,400 (x2.5), not x1.37. Applied as the bundle wrote it; for the owner to confirm. |
