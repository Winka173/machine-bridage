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
