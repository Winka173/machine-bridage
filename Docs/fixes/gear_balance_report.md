# Gear balance 04/10 (lane A): report

Branch `feature/gear-balance` (worktree MachineBrigade-art). Source: `Docs/prompts/gear_balance_vi.md` sections 1-37.
Decisions: `Docs/DECISIONS.md` "Gear balance 04/10 (lane A)"; old -> new log: `Docs/export/CHANGES.md` "GEAR BALANCE" (GB-1..GB-24).
No Unity run. Tests: owner "không cần test" - none written, none run; sections 28-34 were checked by reading the code and a
Python emulation of the C# formulas (the exporter's ports in `Tools/export/domains/_game.py` for the tables; Arsenal.Value /
Boost, Vehicle.ArmourOn, GearSystem.Incoming / Outgoing re-typed). Compile check: `dotnet build Tools/simbuild/Sim.csproj`
0 errors (bin / obj / Temp/simbuild deleted after); Game-layer files (GearCatalog*, Strings, GearText) checked by hand (C# 9).

## 1-3. Every changed ID, old -> new, canonical source

| ID | field | old | new | source |
|---|---|---|---|---|
| armoured_tub | ArmourAll | 0.40 / 0.55 / 0.70 / 0.85 / 1.00 | 0.25 / 0.35 / 0.45 / 0.55 / 0.65 | `Scripts/Game/Match/GearCatalog.cs` Bases |
| hair_trigger | FireRate (implicit) | 0 / 0 / 0.10 / 0.12 / 0.15 | 0 / 0 / 0.08 / 0.10 / 0.12 | GearCatalog.cs |
| hair_trigger | Spread drawback | 0 / 0 / -0.10 / -0.12 / -0.14 | 0 / 0 / -0.08 / -0.10 / -0.12 | GearCatalog.cs |
| heavy_barrel | Range | 0 / 0 / 0.08 / 0.10 / 0.12 | 0 / 0 / 0.07 / 0.09 / 0.10 | GearCatalog.cs |
| heavy_barrel | Speed drawback | 0 / 0 / -0.05 / -0.06 / -0.07 | 0 / 0 / -0.03 / -0.04 / -0.05 | GearCatalog.cs |
| overtuned_engine | Speed | 0 / 0 / 0.10 / 0.12 / 0.15 | 0 / 0 / 0.08 / 0.10 / 0.12 | GearCatalog.cs |
| overtuned_engine | Health drawback | 0 / 0 / -0.04 / -0.05 / -0.06 | 0 / 0 / -0.03 / -0.04 / -0.05 | GearCatalog.cs |
| vulcan | 2-piece BurnDamage | 0.25 | 0.15 | GearCatalog.cs Brands |
| hivemind | 2-piece SummonPower | 0.15 | 0.10 | GearCatalog.cs Brands |
| phoenix | 2-piece RepairReceived | 0.10 | 0.06 | GearCatalog.cs Brands |
| quartermaster | 2-piece RepairReceived | 0.10 | 0.06 | GearCatalog.cs Brands |
| ammo_handling | Magazine | 0.10 / 0.15 / 0.20 / 0.25 / 0.30 | 0.08 / 0.12 / 0.16 / 0.20 / 0.24 | `GearCatalog.Tower.cs` TowerBases |
| ammo_handling | MainScale (MagazineReload) | 1.5 | 1.25 | GearCatalog.Tower.cs |
| ammo_hoist | ProjectileSpeed | 0.08 / 0.12 / 0.16 / 0.20 / 0.25 | 0.06 / 0.09 / 0.12 / 0.15 / 0.18 | GearCatalog.Tower.cs |

Every four-piece behaviour, MinRarity, slot and trade-off identity kept. KEEP lists untouched: tungsten_penetrator,
applique_steel, long_barrel, every tower base in section 18, all sub-stat values, all caps (section 25 values unchanged).

Rules changed or locked (code):

| rule | old | new | source |
|---|---|---|---|
| DamageVsHeavy / DamageVsLight | face struck, with gear (`ArmourOn(face) >= 3`): heavy 3-4 | chassis armour class = the data's front level, no gear, no buff: heavy 3-5, light 0-2 | `Sim/Abilities/GearSystem.cs` `HeavyChassis`, `ArmourClassOf` (Outgoing; the TandemWarhead trait's heavy bonus uses the same rule) |
| ResistIndirect | every `hit.Indirect` (WeaponDef.Indirect: minRange, lofted, bomb, **drone**) | `Armour.IndirectFire(weapon)`: Indirect, not a Drone projectile, not a guided topAttack missile; weapon-less strikes from above keep it | `Sim/Content/Armour.cs`, GearSystem.Incoming |
| ReactiveArmor | ShapedCharge, not tandem, not mine / burn | plus: not thermobaric (explicit) | GearSystem.Incoming |
| caps on module stat modifiers | VeteranCrew x(1+p) on damage and fire rate, AutoRepair +p regen, Splash->DamageVsLight conversion: all added outside the cap | added into the same cap (only the headroom left under the cap) | `Sim/SimWorld.cs` Upgrade, `SimWorld.Commanders.cs` `StatCapOf` / `Headroom`, GearSystem.Equip |
| fractional pen / armour | already float + linear interpolation (DamageTable.Read, Overpenetration) | unchanged, verified (section 7 below) | `Sim/Content/DamageTable.cs`, `Sim/Entities/Vehicle.cs` ArmourOn |

Text: `Scripts/Game/Hud/Strings.cs` (`stat.line.damage_vs_light/heavy`, `trait.tandem_warhead.info`, `stat.line.resist_indirect`,
`special.veteran_crew.info`, `special.auto_repair.info`, names and `.info` of the three new kits), `GearText.BaseNote` (shows
`gear.base.<id>.info`), comments in VehicleBoost.cs / Enums.cs. Exporter: `Tools/export/domains/d02_phuong_tien.py` (sheet
descriptions 40 / 14 base types).

## 4. The three new gear

| id | slot | EN / VI name | implicit | values C / U / R / E / L | drawback | main stat |
|---|---|---|---|---|---|---|
| energy_dissipation_liner | Armor | Energy Dissipation Liner / Tấm lót tản năng lượng | ResistEnergy | 0.04 / 0.06 / 0.09 / 0.12 / 0.15 | none | Health (not plating: same convention as spall_liner / composite_addon) |
| field_service_interface | Repair | Field Service Interface / Bộ tiếp nhận sửa chữa dã chiến | RepairReceived | 0.02 / 0.03 / 0.04 / 0.06 / 0.08 | none | Regen (slot default) |
| grounding_mesh | TowerStructure | Grounding Mesh / Lưới tiếp địa năng lượng | ResistEnergy | 0.04 / 0.06 / 0.09 / 0.12 / 0.15 | none | Health (tower Structure default) |

Each has a tooltip line (`gear.base.<id>.info`, EN + VI) and export rows (`10_trang_bi` Trang_bi / Trang_bi_thap / Trang_bi_ten).
ResistEnergy and RepairReceived need nothing of a vehicle or tower (VehicleFit / TowerFit: None), so all three drop for every
branch / tower. No picture yet (GearArt falls back to the slot icon, as for airburst_rounds and the tower bases). Max values stay
under their caps (ResistEnergy 0.15 <= 0.30; RepairReceived 0.08 <= 0.10). No other gear added; nothing deleted.

## 5. monolith_plate runtime audit: ALIVE, kept unchanged

1. `implicitStat = Count` is the "no implicit line" sentinel (BaseTypeDef.Implicit doc): ImplicitValue returns 0, Lines and
   Boost skip it. It has no combat effect of its own, by design.
2. `MainScale = 1.8` is consumed in `Arsenal.cs` `Gear.Value` (vehicle branch: `top * MainScale * LevelShare`): main stat Health
   (Armor slot, not plating) 0.144 / 0.198 / 0.252 at Rare / Epic / Legendary top level (others' Armor main: 0.08 / 0.11 / 0.14),
   and in `GearText.BaseNote` ("80 % bigger, no sub-stats").
3. Measurable benefit: Health goes into `Gear.Boost` sum -> capped 0.25 -> `VehicleBoost.Hp` -> `Vehicle.HpScale` -> `MaxHp`. Speed
   drawback -0.04 / -0.05 / -0.06 after the cap.
4. `NoSubs = true` is consumed in `Gear.FillSubs` (0 sub-stats, also on merge / migrate): the design trades sub-stats for one big
   main line, and the in-game text says so. Correct.
Note for the lead: a Legendary at max level gives 0.252 Health alone, over the 0.25 cap (effective 0.25, and it leaves no room
for Health subs / sets). The prompt says keep it if it works, and caps may not move, so it is unchanged.

## 6. BuildCap validation

Caps unchanged (Damage 0.25, FireRate 0.15, Health 0.25, Penetration 1.00, ProjectileSpeed 0.30, Range 0.12 / tower 0.10,
Speed 0.15, resistances 0.30, RepairReceived 0.10 ...). Where they apply (code read):
- `Gear.Boost` (Arsenal.cs): main + implicit + sub-stats + two-piece set lines are **summed per stat, then capped**
  (`Min(sum, cap) + penalty`); trade-off drawbacks after the cap (existing design). Towers: the same with TowerStatCap.
- Commander lines: `CommanderRules.Merge` adds to the already-capped sum and caps the total (a commander's own line above the
  cap is its own cap: existing design).
- Module stat modifiers (section 27) were outside the cap; now inside: VeteranCrew adds only the damage / fire-rate headroom
  left under 0.25 / 0.15 (as an additive share of `1 + stat`), AutoRepair only the Regen headroom under 0.02, and the
  Splash -> DamageVsLight conversion (a blast-less gun) only up to 0.25. Where the Sim has no cap table (headless runs without
  `SetStatCaps`, a stat with no cap) nothing is clamped.
- Not stat lines, so not capped: conditional traits and four-piece behaviours (procs, auras, timers: Executioner, OpeningSalvo,
  SetFirestorm ...), reactive armour, statuses. A trait never raises a stat line.

## 7. Fractional Pen / Armour (sections 8, 29, 30)

Code path: `DamageSystem.HitMultiplier` / `Estimate`: `pen = weapon.Penetration + Attacker.PenetrationUp` (float), armour =
`Vehicle.ArmourOn(face)` = `min(cap, data + ArmourAllUp + ArmourSideUp on side / rear)` (float, no rounding; cap max(4, data face),
so gear never lifts a face to 5) -> `DamageTable.Read` (step = 2 - (pen - armour), linear between the two neighbours) and
`DamageTable.Overpenetration` (float diff, linear). No Round / Floor / Ceil / int cast anywhere before the lookup.

Emulation, prompt 8.1 example (armour 4): +0.40 -> 0.9100, +0.50 -> 0.9250, +0.70 -> 0.9550, +0.85 -> 0.9775, +1.00 -> 1.0000 (match).

Tungsten on a pen-4 gun (direct table x overpenetration):

| pen | A0 | A1 | A2 | A3 | A4 | A5 |
|---|---|---|---|---|---|---|
| 4.00 | 1.20x0.85=1.020 | 1.20x0.95=1.140 | 1.200 | 1.000 | 0.850 | 0.650 |
| 4.40 | 1.20x0.81=0.972 | 1.20x0.91=1.092 | 1.20x0.98=1.176 | 1.080 | 0.910 | 0.730 |
| 4.55 | 0.954 | 1.074 | 1.167 | 1.110 | 0.9325 | 0.760 |
| 4.70 | 0.936 | 1.056 | 1.158 | 1.140 | 0.955 | 0.790 |
| 4.85 | 0.918 | 1.038 | 1.149 | 1.170 | 0.9775 | 0.820 |
| 5.00 | 1.20x0.75=0.900 | 1.20x0.85=1.020 | 1.20x0.95=1.140 | 1.200 | 1.000 | 0.850 |

Overpenetration reads the same float diff (pen 4.40 vs armour 1: diff 3.40 -> 0.91, between 0.95 and 0.85).

Armour gear as float (illustration: the tub and the applique share the one Armor slot, so a real loadout wears one): MBT side 2
+ ArmourAll 0.65 + ArmourSide 1.00 = 3.65 -> pen 4 direct 0.9025; light front 2 + 0.65 = 2.65 -> pen 4 1.07; a data-5 front
stays 5, a 4 front stays 4 (cap).

## 8. Top Attack interaction (section 31)

Roof = `ArmourOn(Top)` = roof + ArmourAllUp only (ArmourSideUp applies to Side / Rear only); the top-attack table, float
interpolation; `Overpenetrates` is false for every topAttack weapon. Emulation (pen 4 Hellfire, roof 2): roof 2.00 -> 1.1500,
+ArmourAll 0.25 -> 2.25 -> 1.1375, 0.45 -> 1.1275, 0.65 -> 1.1175; ArmourSide 1.00 never added. ResistIndirect not triggered by
topAttack (section 10 below).

ResistIndirect by weapon after the change (`Armour.IndirectFire`): howitzer, mortar_120, grad_rockets, thermobaric_rockets,
guided_bomb, jet_bombs -> applies (artillery / lobbed / bombs, canonically indirect: WeaponDef.Indirect "bombs fall");
hellfire_standoff, kornet_top, atgm, lancet, fpv_swarm, shahed, gun_120mm -> no. Before: lancet, fpv_swarm, shahed and every
other Drone weapon took it (WeaponDef.Indirect counts drones).

## 9. ERA interaction (section 34)

`GearSystem.Incoming`: `type == ShapedCharge` (the damage type: ATGM, HEAT shell, shaped-charge drones; no projectile-family
condition), not a mine / burn, not tandem (`Projectile.Tandem`, the TandemWarhead trait: full bypass, the existing rule), not
thermobaric. Epic 0.40 / Legendary 0.55 unchanged (cap 0.8): ShapedCharge x0.60 / x0.45 -> active; tandem x1.00 (bypass);
Kinetic, HE, Fragmentation, Fire, Energy, thermobaric x1.00 -> inactive.

## 10. Energy resist (section 32)

Pipeline for a 100-damage Energy hit on the ground: type x0.90 (HitMultiplier) -> `GearSystem.Incoming` ResistEnergy
(`Stats.Resist(Energy)`) -> `DomeSystem.Absorb` returns the damage untouched for Energy (shield bypass) -> Barrier. The resist
never touches the bypass. energy_dissipation_liner / grounding_mesh C..L: 86.4 / 84.6 / 81.9 / 79.2 / 76.5 (towers are Vehicles,
same path). The 0.70 total-cut clamp in Incoming is unchanged.

## 11. DamageVsHeavy (section 33)

Heavy chassis 5/3/2/2: front 5, side 3, rear 2, roof 2 -> Heavy (old rule: rear / roof read Light). Light chassis 2/1/0/0 with
ArmourAll 0.65 (faces 2.65 / 1.65 / 0.65): Light (unchanged). Structures and aircraft keep DamageVsStructure / DamageVsAir.

## 12. Rarity progression (section 28): one piece alone at its rarity's top level, summed then capped

| gear | Rare | Epic | Legendary | finding |
|---|---|---|---|---|
| hair_trigger | FireRate main 0.08 + 0.08 = 0.16 -> **0.15** | 0.11 + 0.10 -> **0.15** | 0.14 + 0.12 -> **0.15** | capped from Rare (the Loader's main stat is FireRate too) |
| overtuned_engine | Speed 0.05 + 0.08 = 0.13 | 0.065 + 0.10 -> **0.15** | 0.08 + 0.12 -> **0.15** | capped from Epic (Engine main = Speed) |
| heavy_barrel | Range 0.07 | 0.09 | 0.10 | rising, under 0.12; drawbacks -0.03 / -0.04 / -0.05 |
| armoured_tub | ArmourAll 0.45 | 0.55 | 0.65 | rising (C 0.25, U 0.35) |
| tungsten_penetrator | Pen 0.70 | 0.85 | 1.00 | rising, Legendary at the cap 1.00 (kept by the prompt) |
| applique_steel | ArmourSide 0.70 | 0.85 | 1.00 | rising, Legendary at the cap 1.00 (kept) |
| ammo_handling | MagazineReload 0.10, Magazine 0.16 | 0.1375 / 0.20 | 0.175 / 0.24 | rising, under caps |
| ammo_hoist | FireRate main 0.08, ProjSpeed 0.12 | 0.11 / 0.15 | 0.14 / 0.18 | rising, under caps |
| monolith_plate | Health 0.144 | 0.198 | 0.252 -> **0.25** | Legendary over the Health cap |

No rarity gives less than the one below it; drawbacks rise with rarity and stay under the gain.

## 13. Needs the lead / owner

- hair_trigger (from Rare) and overtuned_engine (from Epic) still reach their cap alone: the prompt's numbers cover the implicit
  line, but the slot's main stat is the same stat (Loader -> FireRate, Engine -> Speed). Applied exactly as written; a further
  cut (or a different main stat) is the owner's call.
- ammo_handling: the prompt expects MagazineReload 0.10 / 0.15 / 0.20 / 0.25 / 0.30, but the tower main stat is StandardTop
  (0.03 / 0.05 / 0.08 / 0.11 / 0.14) x MainScale: 1.25 gives 0.0375 / 0.0625 / 0.10 / 0.1375 / 0.175 (1.5 gave up to 0.21).
  MainScale 1.25 applied as asked; the "no +30 % Magazine and +30 % reload" goal holds (0.24 / 0.175).
- monolith_plate Legendary 0.252 Health over the 0.25 cap (kept, see 5).
- Module stat modifiers now inside the cap (section 6): VeteranCrew gives nothing on a loadout already at +25 % damage /
  +15 % fire rate. This follows section 27 literally; the earlier design said the module "rides along" outside the caps.
- Existing EditMode tests whose expected numbers move (not edited, not run): `GearModelTests` (capped loadout test: overtuned
  engine drawback 0.06 -> 0.05, heavy barrel 0.07 -> 0.05 speed, range 0.12 -> 0.10), `EquipmentPrompt8Tests.TradeOffDrawbacksGrowWithTheGain`
  (heavy_barrel -0.05 -> -0.03, -0.07 -> -0.05), `Prompt15MigrationTests` line 53 message only. Count assertions moved to 40 / 14
  (`GearModelTests`, `TowerGearTests`) so the shipped catalogue does not trip them.
- Old-save migration (`Gear.Migrate`, pieces from before the affix model) picks a plain base by id modulo the slot's plain bases;
  the Armor and Repair slots now have one more, so such a never-loaded old piece could land on a different base. Saves loaded
  since prompt 8 are unaffected.
- Unity re-export (ExportGameDoc) not needed for these numbers: the gear sheets are read from the C# source.

## 14. Generated files regenerated

`python Tools/export/export.py --game-json Docs/export/game_snapshot.json`, then `export.py check`: 15 / 15 PASS (unmapped 0,
foreign keys 304 OK, formulas 292 OK, NEED_CODE_CHECK 0, identical across two processes).
- `10_trang_bi.xlsx` / `.md`: Trang_bi (40 rows: the new values, energy_dissipation_liner, field_service_interface),
  Trang_bi_thap (14 rows: ammo_handling, ammo_hoist, grounding_mesh), Trang_bi_bo (four sets), Trang_bi_ten (names), caps and
  rarity tables (unchanged values).
- `07_hinh_anh_am_thanh_model.xlsx` (localisation: new / changed strings), `00_index.xlsx`, `README.md`, `bulk.zip`; the other md
  files only change their commit stamp. `01_chien_dau` and `03_can_cu` carry no gear values (checked: no cell changed beyond the
  stamp), so nothing else to update there.

## 15. Confirmations

`deleted gear = 0`

`new gear = 3`

`DamageVsHeavy = chassis armour class 3–5`

`fractional penetration/armour is not rounded before lookup`

`ResistIndirect is not automatically triggered by topAttack`

`boss armour/HP unchanged` (no balance.json line touched in this task)
