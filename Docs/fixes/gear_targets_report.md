# Gear targets 04/10 (lane A): report

Branch `feature/gear-targets` (worktree MachineBrigade-art). Source: the owner's answers 04/10 at the end of
`Docs/prompts/gear_balance_vi.md` ("Trả lời của chủ dự án 04/10"). Decisions: `Docs/DECISIONS.md` "Gear targets 04/10 (lane A)";
old -> new: `Docs/export/CHANGES.md` "GEAR TARGETS" (GT-1..GT-10). No tests written or run (owner "không cần test"), no Unity run;
C# 9 checked by grep (lead compiles).

## The real formula (what the game applies)

One piece, per stat: `Gear.Value` (Arsenal.cs) = slot top table [rarity] (Loader / Armor: 0.03 / 0.05 / 0.08 / 0.11 / 0.14,
Engine 0.02 / 0.035 / 0.05 / 0.065 / 0.08, tower StandardTop 0.03-0.14) x `MainScale` x `LevelShare` (0.4 at level 1, 1.0 at the
rarity's level cap), plus `ImplicitValue` (`Top[rarity]` x LevelShare) and `Implicit2Value` (`Top2[rarity]` x LevelShare) when the
line raises the same stat; `Gear.Boost` sums every line per stat and applies `Min(sum, cap)`, drawbacks after the cap. The hair
trigger's main stat is the Loader's (FireRate) and the overtuned engine's the Engine's (Speed), the same stat as their implicit:
that is why the gear balance pass's implicit-only cut still left them at their cap.

## Emulation (Python, float32, raw values read from GearCatalog.cs / GearCatalog.Tower.cs / Arsenal.cs / Gear.Tower.cs)

Effective = summed then capped, one piece at its rarity's top level; in brackets main + implicit (+ implicit 2).
Common / Uncommon of the three trade-offs are formula values only: they drop from Rare (MinRarity 2).

| gear | stat | cap | Common | Uncommon | Rare | Epic | Legendary | target | result |
|---|---|---|---|---|---|---|---|---|---|
| hair_trigger | FireRate | 0.15 | n/a (0.75 %) | n/a (1.25 %) | **8.00 %** (0.0200 + 0.0600) | **10.00 %** (0.0275 + 0.0725) | **11.00 %** (0.0350 + 0.0750) | - / - / 8 / 10 / 11 | PASS |
| overtuned_engine | Speed | 0.15 | n/a (1.00 %) | n/a (1.75 %) | **8.00 %** (0.0250 + 0.0550) | **10.00 %** (0.0325 + 0.0675) | **12.00 %** (0.0400 + 0.0800) | - / - / 8 / 10 / 12 | PASS |
| monolith_plate | Health | 0.25 | n/a (5.14 %) | n/a (8.57 %) | 13.71 % (0.1371) | 18.86 % (0.1886) | **24.00 %** (0.2400) | L 24 | PASS |
| ammo_handling (tower) | MagazineReload | 0.30 | **10.00 %** (0.0300 + 0.0700) | **15.00 %** (0.0500 + 0.1000) | **20.00 %** (0.0800 + 0.1200) | **25.00 %** (0.1100 + 0.1400) | **30.00 %** (0.1400 + 0.1600) | 10 / 15 / 20 / 25 / 30 | PASS |
| ammo_handling (tower) | Magazine | 0.40 | **8.00 %** | **12.00 %** | **16.00 %** | **20.00 %** | **24.00 %** | 8 / 12 / 16 / 20 / 24 | PASS |

At level 1 every line is 40 % of these (hair trigger 3.2 / 4.0 / 4.4 %, engine 3.2 / 4.0 / 4.8 %, monolith L 9.6 %, ammo handling
reload 4-12 %, magazine 3.2-9.6 %). Old effective: hair trigger 16 / 21 / 26 % (capped 15), engine 13 / 16.5 / 20 % (capped 15
from Epic), monolith L 25.2 % (capped 25), ammo handling reload 3.75 / 6.25 / 10 / 13.75 / 17.5 %. All ascend with rarity and sit
under their caps alone. Drawbacks unchanged (hair trigger Spread -0.08 / -0.10 / -0.12, engine Health -0.03 / -0.04 / -0.05,
monolith Speed -0.04 / -0.05 / -0.06).

Raw values (the levers the formula has):
- hair_trigger: `MainScale` 1 -> 0.25, implicit FireRate 0.08 / 0.10 / 0.12 -> 0.06 / 0.0725 / 0.075.
- overtuned_engine: `MainScale` 1 -> 0.5, implicit Speed 0.08 / 0.10 / 0.12 -> 0.055 / 0.0675 / 0.08.
- monolith_plate: `MainScale` 1.8 -> 1.7142857 (12/7; it has no implicit, the main line is the only lever).
- ammo_handling: `MainScale` 1.25 dropped (StandardTop x 1 gives 0.03-0.14, no single scale reaches 10-30 %), and a second
  implicit `Implicit2 = MagazineReload`, `Top2` 0.07 / 0.10 / 0.12 / 0.14 / 0.16 (the drivetrain / signal relay mechanism, read
  by Gear.Boost, Gear.Lines and the sub-stat exclusion). Magazine implicit 0.08-0.24 unchanged.

## BuildCap and the over-cap display (owner answer 1)

The global cap stays on the sum of every source: gear lines and two-piece set lines are summed then capped (`Gear.Boost`); the
Veteran Crew (damage, fire rate), Auto Repair (regen) and the Splash -> DamageVsLight conversion add only the headroom left under
the same cap (`SimWorld.Headroom`, gear balance section 27). Nothing new bypasses it.

New `Gear.OverCap(loadout, caps, brandCounts, noBlast)` (Arsenal.cs; the summation moved out of Boost into a shared `Sums` so both
read one loop) returns per stat what the cap cuts off: lines over the cap plus the module / conversion share that does not fit (the
same rule as SimWorld.Headroom). Shown as `gear.overCap` "{line} over cap (not applied)" / "{line} bị trần cắt (không có tác dụng)",
e.g. "+5% fire rate over cap (not applied)":
- vehicle / tower detail page (MenuScreen.Detail VehicleStats, the facts under the stat bars: the summed, boosted stats);
- the Army equipment page under the set chips (the branch loadout; heading `gear.overCapTitle` "Over the loadout cap" / "Vượt trần
  trang bị").
Equipment cards: the main-stat number (KitCards ShortStat / MainLine / compare) now adds the implicit lines of the same stat, so a
hair trigger card reads +11 %, not its small +3.5 % main line.

## Generated files

`python Tools/export/export.py --game-json Docs/export/game_snapshot.json` (PYTHONIOENCODING=utf-8), then `export.py check`: 15 / 15
PASS (unmapped 0, foreign keys 304 OK, formulas 292 OK). `10_trang_bi` Trang_bi (hair_trigger main_scale 0.25, top
0.06 / 0.0725 / 0.075; overtuned_engine 0.5, 0.055 / 0.0675 / 0.08; monolith_plate 1.7142857) and Trang_bi_thap (ammo_handling
implicit2 MagazineReload, top2 0.07-0.16, no main_scale); `07` localisation (two new strings); other files the commit stamp.

## For the lead

- Compile: Arsenal.cs (Sums / OverCap, a local function, named tuple list), MenuScreen.Detail.cs, MenuScreen.Army.cs, KitCards.cs
  (`is A or B` pattern, C# 9), GearText.cs, Strings.cs.
- Tests not edited: `GearModelTests` capped-loadout test (overtuned engine L + drivetrain still reach the 0.15 speed cap, so the
  expectation is the same as after the gear balance pass); `TowerGearTests` line 103 (main stat MagazineReload) still holds.
