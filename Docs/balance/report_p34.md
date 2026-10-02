# Prompt 34 report: weapon families, warnings, barrels, tiered effects and sound, wrecks, previews

Branch `feature/p34-c3` (lane C), 2026-10-02. Decisions: DECISIONS "Prompt 34 L0" ... "Prompt 34 L8 / L9". No battle, no
simulation and no frame-rate measure were run for this report (the owner's rule of 30/09): every DPS here is on paper
(a weapon's sustained DPS on one target, `steps_c.sustained`, before weaponDamage, rank and phases), and nothing
here concludes anything about balance in play.

## 1. Balance before / after, per boss

From `Docs/balance/boss_weapon_families.md` (written by `Tools/balance/p34_boss_families.py`; the numbers before are in
`Tools/balance/p34_boss_baseline.json`, each weapon's rows are there). Each changed weapon fires its family's round
and keeps its DPS through its cycle; where the family's core is more than 1.25 times the old one, the cycle is that
much longer (the area bonus), and that is the only DPS that moves. Health is not recalculated (the prompt).

| boss | ground DPS before | after | kept | area bonus on a weapon |
|---|---|---|---|---|
| behemoth | 1012 | 1012 | 100 % | — |
| mobile_fortress | 1082 | 954 | 88 % | x1.60 |
| armored_train | 660 | 660 | 100 % | — |
| mega_gunship | 462 | 462 | 100 % | — |
| drone_mothership | 1303 | 1304 | 100 % | — |
| nuke_train | 1751 | 1751 | 100 % | — |
| silver_bug | 1638 | 1638 | 100 % | — |
| behemoth_inferno | 282 | 282 | 100 % | — |
| behemoth_tempest | 299 | 299 | 100 % | — |
| fortress_hive | 586 | 586 | 100 % | — |
| fortress_bastion | 792 | 792 | 100 % | — |
| rail_supergun | 170 | 170 | 100 % | — |
| earth_borer | 289 | 289 | 100 % | — |
| command_airship | 1848 | 1532 | 83 % | x2.00 |
| landing_hovercraft | 302 | 302 | 100 % | — |
| supreme_command | 143 | 143 | 100 % | — |
| sky_fortress | 418 | 418 | 100 % | — |
| leviathan | 771 | 771 | 100 % | — |
| moloch | 1381 | 1382 | 100 % | — |
| daedalus | 745 | 745 | 100 % | — |
| kronos | 439 | 439 | 100 % | — |
| typhon | 707 | 707 | 100 % | — |
| ixion | 615 | 615 | 100 % | — |
| caspian | 260 | 260 | 100 % | — |
| morrigan | 165 | 165 | 100 % | — |
| bastion_mk0 | 239 | 239 | 100 % | — |
| fenrir | 478 | 350 | 73 % | x1.60 |
| scylla | 234 | 234 | 100 % | — |
| locust | 552 | 552 | 100 % | — |
| behemoth_mk2 | 569 | 569 | 100 % | — |
| icarus_mk0 | 400 | 400 | 100 % | — |
| argus | 632 | 316 | 50 % | x2.00 |
| behemoth_mk0 | 733 | 733 | 100 % | — |
| kraken | 771 | 771 | 100 % | — |
| monster | 792 | 792 | 100 % | — |
| garuda | 1848 | 1532 | 83 % | x2.00 |
| hyperion | 1320 | 1320 | 100 % | — |
| stymphalos | 622 | 622 | 100 % | — |
| nyx | 239 | 239 | 100 % | — |
| cerberus | 875 | 875 | 100 % | — |
| hydra | 707 | 707 | 100 % | — |

Moved: Jötunn (mobile_fortress) 88 % and Fenrir 73 % (the Smerch pods' wider 8 / 16 m blast, cycle x1.6), Roc
(command_airship) and Garuda 83 % (the 400 kg bombs, 10 / 20 m, cycle x2), Argus 50 % (its main weapon is the bomb stick).
Leviathan / Kraken: the 406 mm salvo, 3 shells a turret x 2,400 every 60 s (core 14 / edge 24 m), 360 DPS on its own,
kept. Gungnir (rail_supergun) untouched in damage, radius, cycle and aim (prompt 29 G1).

Other numbers that changed in this prompt: the T4+ warnings (L3: a boss's T4+ round stays in the air at least its
warning, so a short-range 203 mm shot lands 2.5 s after firing; Leviathan's salvo warns 3.7 s), the barrels fired
together (L4: cycle and DPS kept), and in L9 the cruise missiles' warning rings (view only, section 5).

## 2. Player weapon families that deviate (not fixed)

From `Docs/checks/player_weapon_family.md`. Prompt 34 changes no player weapon; fix after prompt 29 and the
replacement-round balance. 19 families whose player weapons differ in damage per round, speed, blast or type:

- **atgm_agm_114_hellfire**, T2: 3 weapons
- **cal_100_105_ap**, T2: 4 weapons
- **cal_100_105_he**, T2 (boss table: 300 a round): 3 weapons
- **cal_120_ap**, T3 (boss table: 260 a round): 5 weapons
- **cal_125_ap**, T3 (boss table: 400 a round): 4 weapons
- **cal_12_7**, T0 (boss table: 15 a round): 10 weapons
- **cal_152_155**, T3 (boss table: 600 a round): 8 weapons
- **cal_152_155 / ap**, T3 (boss table: 600 a round): 3 weapons
- **cal_23**, T1 (boss table: 7 a round): 2 weapons
- **cal_25**, T1: 3 weapons
- **cal_30**, T1 (boss table: 22 a round): 7 weapons
- **cal_30 / flak**, T1 (boss table: 22 a round): 3 weapons
- **cal_35**, T1 (boss table: 25 a round): 3 weapons
- **cal_57 / ap**, T2 (boss table: 120 a round): 2 weapons
- **cal_7_62**, T0: 4 weapons
- **flame_flamethrower**, T1: 2 weapons
- **rkt_70_80**, T2: 5 weapons
- **rkt_gmlrs_227**, T4: 2 weapons
- **sam_fim_92_stinger**, T2: 2 weapons

Weapons bosses share with player vehicles keep the player's numbers: `boss_flak` and `zu23` already match the
table; `gunship_105`, `gunship_40mm` and `hover_ciws` do not and wait for the player pass.

## 3. Effects before / after (pictures)

Not rendered in this pass (no Unity run allowed). NEED RENDER: the lead renders them with the effect shot tool into
`Docs/vfx/p34/` (the LOCAL_TODO line from L5): for each tier T2-T5 the old blast alone and with its tier overlay, from
the same camera; the firing look of T3-T5 (a 152 mm, a 203 mm, the 406 mm volley); one wreck of each class; and the
previews (a ship on the sea, a train on its track, an aircraft over the ground, a tower on its pad).

## 4. Stress scene (the definition; counts when the lead runs it)

`-mb-play -mb-lighthousebay -mb-p34stress` (or `-mb-p34stress=SECONDS`, default 120): the Leviathan at sea, Jötunn
(Smerch) and Roc (400 kg bombs) for the enemy, 32 vehicles a side kept up to strength (`Game/Match/P34StressCheck.cs`).
Once a second it samples the live particles, the busy voices (of 32) and the wrecks and their pieces, and at the end
writes the peaks and means to `Docs/balance/p34_stress_counts.json`. FPS: NEED PROFILE on a device. Not run.

## 5. Validators

`python Tools/balance/p34_validate.py` (run in L9; all six OK after the ring fix):

1. Families: one family, one round in every boss; every variant with its reason: OK.
2. Warnings: every T4+ boss round warns at least the escape formula: OK (Gungnir's 3 s bombard, the named exception).
3. Rings: 7 problems found and fixed. The cruise missiles' warning mark drew a 12 m ring over a 10 m core whose edge
   reaches 20 m (Leviathan, Kraken, Typhon, Hydra, Nyx, Scylla), and over Caspian's 7 / 14 m blast. The mark is now
   20 / 10 m and Caspian has its own 14 / 7 m mark (`leviathan_cruise_mark_7`). View only (damage-0 event supports).
4. Muzzles: every gun that fires its barrels together has a Muzzle_b<k> for each barrel on its model (Kraken the listed
   exception): OK.
5. Previews: every unit maps to ground / water / rail / air: OK (air 38, ground 192, rail 3, water 17 in balance.json;
   `Prompt34PreviewTests` checks the whole catalog).
6. Wrecks: the wreck code adds no collider and no model is imported with colliders: OK.

The same rules as C# tests (written, not run): `Prompt34Tests` (1, 2), `Prompt34ValidatorTests` (3, 4, 6 and the stress
scene's definition), `Prompt34PreviewTests` (5).

## 6. Every point decided in this prompt (from DECISIONS)

- L1: guns are families by calibre class, everything else by the real weapon; a variant only where the round or fire mode differs, each with its reason; tiers for families outside the calibre table from their family and size; a data edge may reach 28 m for the T5 profiles.
- L1: Roc's bomb stick reads "bomb-bay stick 400 kg" and the Smerch pods size 300 (display and form only; penetration kept explicit); lasers, railguns, bombs and missiles lose the wrong "mm".
- L2: targetDPS = the old sustained DPS on one target; an old core under 2 m counts as 2 m for the area bonus; a smaller core never shortens the cycle.
- L2: variants take the family's damage only and keep their own round; Leviathan's AK-127 became the variant cal_127_130/ap.
- L2: where the old cadence could not hold the DPS with the lighter round, the cadence went up (Moloch's 35 mm, Icarus's 40 mm, Matriarch's 2A42, Nemesis's Grad); the tiny 26 B mounts fire full rounds rarely.
- L2: left alone: Gungnir, the weapons shared with player vehicles, the laid weapons other than the 406 mm salvo, the super weapons and the cruise missiles; the 800 mm row unused.
- L3: the floors T4 2.5 s, 406 mm 3.5 s, T5 4 s, cap 6 s; the Sim keeps a boss's unguided T4+ round in the air at least its warning (deterministic; it changes when the round lands); guided rounds get no ring.
- L3: Gungnir's 3 s bombard is a named exception (one line in p34_warnings.EXCEPTIONS); Monster's 800 mm shell (4.94 s needed against 4 s) left as a note.
- L4: a ripple of N became one volley of N barrels with the gaps moved onto the cooldown (cycle and DPS kept); a magazine gun cannot fire together; the view staggers barrels 0.07 s; Kraken's mounts have no barrels (one muzzle each).
- L5: tier overlays drawn on top of every round's own blast (nothing gets smaller); full-detail caps T5 1 / T4 3 / T3 6 by weight; camera shake for T4+ only, on screen and within 90 m, with the screen shake setting back.
- L6: sounds synthesised (no AI, no samples), three layers premixed into one clip a shot; the seven priority steps as numbers; 24 effect voices before cutting, the last 8 for warnings and T5 / boss; the low rumble kept under the mid body for phones.
- L7: wreck classes by model parts, class and id; wrecks live 30-45 s (bosses 90), about 12 full near the camera; the fuselage break (Part_tail) written but not built (over the Su-27's renderer cap); falling aircraft fly onto the Sim's fixed crash plan.
- L8: prompt 33's biome, sea and rail assets are not merged, so the previews use temporary scenes of the right kind (procedural ground in the biome's colours, a flat sea with swells, a short track, a base pad); the biome is the chosen map's theme, else temperate.
- L8: the river boats, hovercraft and amphibious vehicles are placed by id (the Sim drives them as ground vehicles); the "Amphibious light tank" stands at the water's edge; the coastal battery gets a ship to fire at.
- L8: a range ship stands off far enough for its bow to stay on the water (half its length + 14 m, never past 90 % of its reach).
- L8: in a preview every unguided blast round of the shown unit lands inside its edge and core rings (a player's T4 round shows its escape warning there too); a boss's own warnings are left as they are.
- L9: the cruise missiles' warning rings set to the blast's real edge and core (section 5); the in-game ammunition handbook gains a "Calibre tiers T0-T5" entry; the stress scene runs on Lighthouse Bay (the map with a sea).
