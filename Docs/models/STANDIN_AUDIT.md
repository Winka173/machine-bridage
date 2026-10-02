# Stand-in audit (prompt 27 stand-in sweep, 2026-10-02)

The owner's goal: every stand-in model gets its real model. Wave 1 swept the three stand-in sections of ASSET_DEBT.md
(prompt 25 batch B, batch D, prompt 26 pass 2); this audit covers the older sections (prompts 8 to 25 B2) and every
def whose `model` is another id in balance.json. Decisions: DECISIONS "27 stand-in sweep (lead pass, 2026-10-02)".

## (a) Unstruck ASSET_DEBT rows that are model stand-ins

| Section | Row | Verdict |
|---|---|---|
| Prompt 8 | Elite FPV carrier, attack jet, long SAM, SP howitzer: the base model repainted (`EliteRepaint`) | INTENTIONAL: the elite repaint is the design for elites without a model (DECISIONS 25B2 Part 2); the row's need is "if a closer look is wanted" |
| Prompt 16 (old bosses) | `hover_gunboat` on `missile_boat` | DONE already (own model since 25B2, rebuilt in 27 wave 3): struck |
| Prompt 13 | `ammo_carrier` on `truck` | DONE already (own model since 25B2, wave 3): struck |
| Prompt 13 | `airfield.hangar`, `airfield.service` on `helipad` | DONE already: `TowerArt.ModelFor` draws them with `helipad_a` / `helipad_b` (25B2, wave 2): struck |
| Prompt 16 | Coastal battery on the heavy fortress | STAND-IN: built (`coastal_battery`) |
| Prompt 17 C | Eight "simple temporary models" (`mb_p17_temp`) | DONE already: every one rebuilt in 25B2 and 27 waves 3, 4, 7 (own ids): struck |
| Prompt 25 B1 | Kh-29L and GBU-39 drawn as the Maverick and GBU-12 (`RoundStandIns`) | DONE already: `kh29l`, `gbu39` built in 27 wave 8a (the stand-in map applies only to a missing model): struck |
| Prompt 25 B2 | Structures "also kept": super_gun, coastal_battery, bulwark_post, spawn_bastion, ammo_depot | see (b) |

Not model stand-ins of a def (left in their sections): broken-part wreck pieces and the Leviathan's stern copy
(prompts 9, 16: damage effects), Foundry walls and Veyra's church-as-cathedral (prompt 22 E: map dressing, needs new
props and map edits), the variants' marks (decals), detail passes on models that are their own (Leviathan, Morrigan,
lighthouse, laser tank...), sizes (25 B1), portraits and maps (22 D, 22 F).

## (b) The 16 defs that draw another model

| Def | Model | Verdict | Reason |
|---|---|---|---|
| elite_grad | grad_truck | INTENTIONAL | `grad_truck` is the elite's own BM-21 model under a free id (no other def wears it; DECISIONS 25B2 "elite_grad keeps grad_truck") |
| super_gun | heavy_turret x 1.8 | STAND-IN | "the fortress's giant twin gun"; built `super_gun` |
| spawn_bastion | heavy_turret | INTENTIONAL | only `ModeSupport.Build`'s fallback when the catalogue has no HQ, which never happens with the shipped content (DECISIONS 25D1, "the skipped row"); it stands in for the old pair of fortress bastions |
| ammo_depot | ammo_dump | INTENTIONAL | `ammo_dump` is the sheet's note itself (berm-covered store, crates outside; DECISIONS 25B2 Part 2 kept it) |
| airfield | helipad | INTENTIONAL | the airfield is the landing pad (sheet: "a flat concrete pad with markings and lights") |
| airfield.hangar | helipad | INTENTIONAL | a branch naming its tower's model wears `helipad_a` (TowerArt.ModelFor) |
| airfield.service | helipad | INTENTIONAL | as above, `helipad_b` |
| radar_station | radar_site | INTENTIONAL | `radar_site` is its own model (25B2); the id `radar_station` is the 14 m map-prop mast |
| bulwark_post | mg_bunker x 0.8 | STAND-IN | the sheet: "a small sandbag gun post" (3.5 x 3.5 x 2.7 m), not a concrete pillbox; built `bulwark_post` |
| shield_tower.ward | shield_tower | INTENTIONAL | `"art": "shield_tower_b"`: BranchArt draws the branch model |
| cp_relay.loot | cp_relay | INTENTIONAL | `"art": "cp_relay_b"`: as above |
| uav_loiter_strike | strike_drone | STAND-IN | "new drone" of the ht04 support (DECISIONS 25F2-C), drawn as the MQ-9 card unit; built `uav_loiter_strike` (an MQ-1C Gray Eagle) |
| decoy_tank | main_battle_tank | INTENTIONAL | a decoy must look like what it mimics (`decoy.mimic`) |
| coastal_battery | heavy_turret | STAND-IN | sheet: "a coastal gun turret on a concrete base by the rocks"; built `coastal_battery` |
| hydra | hydra_sub | INTENTIONAL | its own model; `hydra.glb` is the Hydra 70 rocket (DECISIONS 27 wave 1b) |
| mara_behemoth | behemoth | PROMPT 31 | Mara's Behemoth is prompt 31's: left as it is |

Counts: 11 intentional, 4 stand-ins (super_gun, bulwark_post, uav_loiter_strike, coastal_battery), 1 left for
prompt 31 (mara_behemoth). From (a): 1 more stand-in row (the coastal battery, the same def), 5 rows already done.
