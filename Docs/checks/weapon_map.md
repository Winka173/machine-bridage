# C09: vehicle-weapon mapping (prompt 29, read only)

The game maps a vehicle to its weapons by exact id (`weapon`, `secondary`, `mounts` in balance.json); the catalog
throws on an unknown id at load, so no fuzzy match exists in the game. Fuzzy matching existed only in round 1's sheet
importer (`Tools/balance/import_xlsx.py`, names to ids); the round-2 tool (`p29_apply.py`) reads ids only and never
edits a weapon (R8 check after every bundle).

Shared weapons (the sheet "Vũ khí dùng chung"): mg_coax (11), hmg_selfdef_15 (11), hmg_roof (7), hmg_selfdef_18 (3),
atgm, mg_jeep, gun_120mm, sam, guided_bomb, air_to_air, fighter_cannon, jassm (2 each): per-vehicle factors go in
`outgoingDamageMult` (S03). The two the sheet names as ambiguous: no weapon in the data is called Khrizantema (the tank destroyer's gun is an
exact id; the only 9M1xx ATGM entries are `atgm_heavy`, `kornet_twin`, `gun_launched_atgm`), and the bunker's flamethrower
is its own id `bunker_flame` (not the flame tank's `flamethrower`): both are exact ids, nothing to disambiguate.
Test: `BalanceRound2Tests.ASharedWeaponIsNeverChangedByAUnitRow` lists every shared weapon's carriers.
