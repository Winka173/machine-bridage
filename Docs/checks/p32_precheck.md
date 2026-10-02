# Prompt 32 L0: precheck (2026-10-02, lead pass)

Read from the code and data on `feature/p32-a1` (after the prompt 29 appendix); nothing run.

1. **Guard tower reach: replace or add?** Replace. The base card's `towerRangeAura` (+10 % within 25 m) and the Watch
   branch's (+15 % within 30 m, `guard_tower.watch`) are the same field: the branch row inherits the card and overrides
   the object, so a Watch tower carries only +15 %. Across towers `GearSystem` (the "best aura counts" loop) takes
   `MathF.Max(t.TowerRange, 1 + rate)`: two guard towers never add up either. No fix needed.
2. **Units seen at the start.** The map data: each generated map's `"units"` (Tools/maps/build_maps.py
   `CONQUEST_UNITS` / `SURVIVAL_UNITS`; Conquest maps: 2 scout jeeps, 1 IFV, 1 light tank per side), spawned by
   `ConquestMode.Setup` / `MissionMode` (campaign missions have their own `units`). Then Auto-buy
   (`ConquestAi.Tick`, every `Interval`) spends the starting CP (Conquest 18) from its first decision. No other system.
3. **Rebuilt towers and supply; CP for destroying a tower.** A tower's `cp` is 0 in the data, so its `ArmyCost` is 0:
   `EconomySystem.ArmyCp` (the army value supply reads) never counts a tower, rebuilt or not; the CP paid to rebuild is
   spent, not added to the army. Destroying one pays `ArmyCost x share` = 0 to the destroyer (`OnVehicleDestroyed`;
   the loot depot's share is of the same price, so 0 too). Both already match prompt 32 L2.
4. **Catch-up.** Two systems. (a) Sliding (`EconomySystem.CatchUpFor`, quick modes without the underdog rule): no
   boost while the side's army is at least 75 % of the rival's, rising linearly to +`CatchUpMax` (0.5 = +50 %
   income) at 20 %; none while the rival's army is under 14 CP; eased in over 4 s. Kill pay is scaled by
   `Bounty` = sqrt(victim side's army / killer's), clamped 0.5-1.5. (b) The once-a-match underdog rule
   (`UnderdogRules`, Conquest after 240 s): when the stronger side has >= 14 CP and >= 1.6 x the weaker side's army,
   the weaker side gets +25 % income for the rest of the match and a free drop of 2-3 of its deck's vehicle nearest the
   deck's average price (3 for a deck averaging <= 6 CP) at its drop zone (a mission's scripted allied wave can stand in).
5. **Forward drop at a strongpoint's outpost.** Yes: `BaseSystem.TryGetDropZone` lands bought vehicles at the side's
   most forward outpost (a held point set up for `base.outpost.cp` = 6 CP), a command vehicle's forward zone, else the
   rally point. An outpost goes when its point is lost.
6. **Thermobaric x2 and the structure multiplier.** Not multiplied: `DamageTable.TypeOf` replaces the high-explosive
   structure value (1.5) with `max(thermobaric, 1.5)` = 2.0 for a thermobaric HE weapon. No x3 on structures.
7. **Second-round choice.** `CombatSystem.RoundIndexFor`: for the target picked, the first second round in data order
   whose rule ("for": air / ground / armour = front > 1 / light = front <= 1 / structure / cluster = two more of the
   side in the blast, 4 m at least) suits it and whose round can hit its layer, else the gun's own; elite-only rounds
   only on elites and rank-7 branches. `KeepRound`: a change starts only once the round in has been in
   `RoundHoldSeconds` = 2 s and no burst or charge is under way; it takes `SwitchSeconds` (the round's `"switch"`, else
   the gun's magazine change or cooldown, at least 0.5 s), during which the mount does not fire; a magazine gun's new
   magazine is full. Deterministic (no random draw), in the state hash.
8. **Prompt 29 appendix.** Not done before; done in this pass first (commit "P29 appendix", DECISIONS "Prompt 29
   appendix (lead pass, 2026-10-02)", Docs/checks/target_mask.md).
