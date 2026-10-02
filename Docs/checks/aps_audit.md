# C06 + C07: APS audit (prompt 29, read only)

**One code path.** Every interception goes through `ApsDef` on the vehicle (`aps` in balance.json):
`DamageSystem.TryIntercept` (missiles, drones, direct-fire rockets; `rockets` adds artillery rockets, `shells` a share of
lobbed shells, `laser` a laser look, `heavy`/`missiles`/`direct` for Patriot and the Dome) and, for guns with `burst`,
`CombatSystem.EngageIncoming`/`GunTakes` (point-defence guns). There is no separate boss path: bosses carry the same
`aps` object. Aircraft are guarded only by a tiered craft's own APS (prompt 19).

| holder | kind in data | classification |
|---|---|---|
| next_gen_tank | unit, 2 / 1.2 s / 20 m, rockets, shells 0.5, laser | SELF_APS (B2-APS-next_gen_tank) |
| iron_beam | unit, 1 / 0.8 s / 30 m, rockets, shells 0.3, laser | POINT_DEFENSE |
| laser_ad_station | tower, 1 / 0.8 s / 40 m, rockets, shells 0.5, laser | POINT_DEFENSE |
| c_ram, c_ram.centurion, c_ram.dome | tower and its branches (burst guns; the Dome missiles) | POINT_DEFENSE |
| missile_battery.pac3 | tower branch, heavy missiles only | POINT_DEFENSE |
| behemoth (and mara_behemoth, same numbers) | boss, 2 / 4 s / 11 m | BOSS_SELF_APS |
| behemoth_tempest | boss, 2 / 1.6 s / 26 m, rockets, laser | BOSS_SELF_APS |
| silver_bug (Icarus), icarus_mk0 | boss, 3 / 1.4 s / 49.6 m (19.5 m mk0), rockets, laser | POINT_DEFENSE (covers its parts and escorts in reach) |
| daedalus | boss, 2 / 1.6 s / 31.6 m, rockets, laser | POINT_DEFENSE |
| leviathan, landing_hovercraft | boss, 3 / 2.2 s / 30 m; 2 / 3 s / 22 m, rockets | BOSS_SELF_APS |
| sea_corvette, sea_cruiser | ship units (escorts), rockets | POINT_DEFENSE (naval) |

Boss ids map one-to-one to the ids above (the sheet's "Behemoth, Behemoth Mk.II, Tempest, Scylla..." are behemoth,
behemoth_mk0 (no APS in data), behemoth_tempest...; Scylla has no `aps`). Following prompt 29 5.3 they keep their
numbers (not normalised to a vehicle profile). The classification is recorded as the new `interceptionMode` only for
the player-vehicle rows of the manifest; bosses and towers keep their data.

**C07 iron_beam:** the data says recharge **0.8 s** (charges 1, radius 30 m, shells 0.3). The 1.2 s of the description is
not in the data. Not changed.
