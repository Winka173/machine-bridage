# C15: where the discounted (runtime) call cost is used (prompt 29, read only)

`TeamEconomy.PriceOf` (now also `RuntimeCallCost`, S04) is used to spend and to check affordability only:
`EconomySystem` (buy, paradrop), `StrikeSystem` (supports), `ConquestAi` (affordability, readiness). Supply
(`ArmyCp` sums `ArmyCost` = base CP), bounties (`Bounty` reads `ArmyCost`), refunds (`KillShare` of the bounty) and the
card's class all read the base price. One classification used the runtime price: the layered AI's CP-spent force
shares (`ConquestAi.P28.Bought`): moved to the base price in S04 (R7).
