# Target-mask check (prompt 29 appendix)

Written by `python Tools/balance/target_mask_check.py` from balance.json (a static read, no Unity); the same check is
`TargetMaskTests` (EditMode) on the loaded catalog. A gun's declared layer (Air; Ground = vehicles and structures)
with a highest damage-type multiplier of 0 over its valid rounds is listed under 1; a second round whose rule can
never be met under 2. Fixed in this pass (B6-mask, `Tools/balance/p29_apply.py`, `Docs/balance/manifest_p29_appendix.json`):
`gun_100_river` and `gun_155_crusader` All -> Ground (high explosive does 0 to aircraft; neither has a second round that
reaches aircraft). Everything below is reported only (the appendix: no rebalance of second rounds here).

## 1. Declared layer with no damage (0)

None.

## 2. Second rounds whose rule is never met (17)

| gun | round | for | why |
|---|---|---|---|
| `bomber_tail_guns` | `bomber_tail_guns_api` | air+ground | elite-only, and no elite or rank-7 branch carries the gun |
| `boss_hmg` | `boss_hmg_api` | air+ground | elite-only, and no elite or rank-7 branch carries the gun |
| `boss_howitzer` | `boss_howitzer_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `bunker_hmg` | `bunker_hmg_api` | air+ground | elite-only, and no elite or rank-7 branch carries the gun |
| `casemate_155` | `casemate_155_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `cruiser_203` | `cruiser_203_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `gun_155_coastal` | `gun_155_coastal_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `gun_behemoth` | `gun_behemoth_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `gunship_105` | `gunship_105_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `hmg_selfdef_21` | `hmg_selfdef_21_api` | air+ground | elite-only, and no elite or rank-7 branch carries the gun |
| `howitzer_fixed` | `howitzer_fixed_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `leviathan_460` | `leviathan_460_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `mg_jeep` | `mg_jeep_api` | air+ground | elite-only, and no elite or rank-7 branch carries the gun |
| `mg_jeep_selfdef` | `mg_jeep_selfdef_api` | air+ground | elite-only, and no elite or rank-7 branch carries the gun |
| `naval_100` | `naval_100_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `naval_155_triple` | `naval_155_triple_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
| `naval_76` | `naval_76_guided` | armour | elite-only, and no elite or rank-7 branch carries the gun |
