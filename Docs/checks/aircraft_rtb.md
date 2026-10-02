# C12: aircraft returning on low health (prompt 29, read only)

- The condition is in `TacticalAi.Refit` (`Scripts/Sim/AI/TacticalAi.cs`): `hurt = !Layered && v.Hp < v.MaxHp * RefitBelow`
  (RefitBelow 0.35, RefitUntil 0.9): an aircraft below 35 % flies to the airfield (or the HQ) and stays until mended
  to 90 %. Prompt 28 already turned it off for the layered AI (ConquestAi's TacticalAi); TacticalAi used alone (wave
  modes, the Sandbox's Combat AI, allies) still has it.
- Untouched by removing it: out of ammunition (`SendToRearm`, `RearmInLulls`, the supply system's `CanBreakOff`), mending
  while standing on the airfield or the HQ (the airfield's `AirRepair` aura), the holding pattern, repair stations and
  engineers mending what is in reach.
- So B3-AI's change is one line: drop the health test everywhere (pass 6).
