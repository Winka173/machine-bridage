# Barrel audit (battleship triple turrets, owner 06/10)

Scope (owner, narrowed 06/10): only the battleship changed. The audit of every other unit, tower and boss mount is
reported below; nothing else was fixed. DECISIONS "## Barrels: battleship triple turrets + audit".

## Battleship (changed)

| side | before | after |
| --- | --- | --- |
| model `battleship.glb` (Tools/blender/mb_naval_b.py, mb_naval_b_kit.heavy_turret) | 3 turrets x 1 barrel, one `Muzzle_gun[_NN]` each | 3 Iowa triple turrets x 3 barrels; `Muzzle_b1..3_gun`, `_gun_02`, `_gun_03` under each turret's `Muzzle_gun[_NN]` (left to right, 1.69 m apart); barrels rise by elev so the bores meet the muzzles (they dipped 0.6 m under them); centre sight hood, gun port plates; 21,164 -> 24,152 tris (2.5 x the ground cap; the stage rework allows 3 x) |
| data `naval_406_bs` (battleship only) | barrels 1, damage 600, cooldown 11, SIMULTANEOUS (inherited) | barrels 3, SIMULTANEOUS, damage 200, cooldown 11, roundWeight 600 (the 406 mm's look and sound); pen 5, splash 8, range unchanged |

DPS proof (WeaponDef.SustainedDps = damage x burst x barrels / cycle): before 600 x 1 x 1 / 11 = 54.55; after 200 x 1 x 3 / 11 = 54.55.
Per volley: 600 before, 3 x 200 = 600 after. Per ship (3 turrets): 163.6 DPS, unchanged.

## Audit of every other mount (not fixed: the owner narrowed the scope)

`python Tools/assets/barrel_audit.py` (data barrels resolved through inherits / mountWeapons / variants against the
model's `Muzzle_b<k>` children, else the barrels found in the meshes at that muzzle). Totals: mismatch 63, no_muzzle 18, not_simultaneous 12, ok 225, skip 217.
`skip`: launchers, rotary guns, lasers, railguns, mortar salvos (owner: they keep their firing).

| weapon | finding | data barrels | units (model barrels) |
| --- | --- | --- | --- |
| flak_35 | mismatch | 1 | aa_vehicle (2) |
| twin_30_flak | mismatch | 1 | heavy_aa (4) |
| gun_120_twin | mismatch | 1 | twin_tank (2) |
| zu23_cheap | not_simultaneous | 2 | zu23_technical (2) |
| hq_flak | mismatch | 1 | headquarters (2), headquarters.fortress_air (2), headquarters.fortress_ground (2), headquarters.shield (2) |
| tower_flak_30 | mismatch | 1 | aa_turret (2) |
| bunker_hmg_twin | mismatch | 1 | mg_bunker.twin (2) |
| gun_57_auto | not_simultaneous | 2 | gun_turret.auto (2) |
| flak_quad | mismatch | 1 | aa_turret.flak (4) |
| p26_behemoth_tiny_be120 | mismatch | 1 | behemoth (2) |
| p26_behemoth_close_boss_flak | mismatch | 1 | behemoth (2), behemoth_mk2 (2) |
| p26_jotunn_close_boss_flak | mismatch | 1 | fenrir (2), mobile_fortress (2) |
| p26_jotunn_tiny_twin_30_flak | mismatch | 1 | mobile_fortress (2) |
| boss_flak | mismatch | 1 | armored_train (4), mara_behemoth (2) |
| p26_matriarch_tiny_mothership_cannon | mismatch | 1 | drone_mothership (2) |
| p26_matriarch_close_boss_flak | mismatch | 1 | drone_mothership (4), locust (4) |
| p26_nemesis_main_ne152 | mismatch | 1 | nuke_train (2) |
| pt14_sb_v30 | mismatch | 1 | silver_bug (2) |
| p26_icarus_close_autocannon_40 | mismatch | 1 | silver_bug (2) |
| p26_bastion_close_boss_hmg | mismatch | 1 | fortress_bastion (2), monster (2) |
| p26_bastion_tiny_zu23 | not_simultaneous | 2 | fortress_bastion (2), monster (2) |
| p26_leviathan_direct_lev127 | mismatch | 1 | kraken (2), leviathan (2) |
| aa_25_triple | mismatch | 1 | leviathan (3) |
| p26_moloch_tiny_zu23 | not_simultaneous | 2 | moloch (2) |
| p26_moloch_close_boss_flak | mismatch | 1 | moloch (2) |
| scylla_ak230 | not_simultaneous | 2 | scylla (2) |
| scylla_2m7 | not_simultaneous | 2 | scylla (2) |
| pt14_hp_155 | mismatch | 1 | hyperion (2) |
| pt14_th_v35 | mismatch | 1 | theia (2) |
| pt14_co_v76 | mismatch | 1 | coeus (2) |
| p26_typhon_direct_ty100 | mismatch | 1 | hydra (2) |
| gun_behemoth | mismatch | 1 | mara_behemoth (2) |
| gun_120mm | mismatch | 1 | mara_behemoth (2) |

Follow-ups if the owner widens the scope: most are twin / quad AA and boss guns whose models show more barrels than
the data; magazine (clip) guns cannot be SIMULTANEOUS today (Catalog.P34 throws), so they need a Sim change first.
The monitor's and battlecruiser's heavy turrets keep their dipped barrels (rise=False) until their own rework.
