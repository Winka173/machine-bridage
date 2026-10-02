# Munition behaviour (fix prompt L4 step 1, read from the code, 2026-10-02)

Read before any change of pass 4, from `Sim/Combat/CombatSystem.cs` (`Launch`, `UpdateProjectiles`),
`Sim/Combat/DamageSystem.cs` (`ResolveImpact`, `TryIntercept`), `CombatSystem.PointDefence.cs`, `CombatSystem.P25A.cs`,
`AbilitySystem` (flares), `GearSystem.Lure`, and the view (`Game/Effects/WeaponEffects.cs`, `ProjectilePool.cs`,
`TracerPool.cs`, `EscapeWarnings.cs`, `EffectsDirector*.cs`). "Ring" is the warning ring on the ground.

The model every round shares: `Launch` fixes a travel time at the shot (distance at launch / speed; a bomb by its fall;
a boss's T4+ round no less than its escape warning, prompt 34 L3; an MRSI salvo stretched), the round's `TimeLeft` runs
down by the step, and on the tick it reaches 0 `ResolveImpact` lands it. There is no position in flight: a round is a
timer plus an aim point. `Guided` is `Projectile is Missile or Drone`; a guided round lands on its target's position *at
impact* (wherever it drove), everything else on the aim point fixed at the shot (the target's position then, plus
spread). The view flies each round for the Sim's travel time on the render clock (`Time.time`).

| group | how it aims | when it goes off | why it misses (before) | ring (before) |
|---|---|---|---|---|
| ATGM (TOW, Kornet, Konkurs, Ataka, Vikhr, Khrizantema) | guided: lands on the target's position at impact; no spread | at the end of the launch-time travel | APS (`TryIntercept`), a jammer at launch (`Jammed`), one launch roll `Failed` (2 % + 8 % x reach², boss part fail), gear lures (EW jammer status, Ghost Net, a decoy) | none |
| air-to-ground missiles (Hellfire, Kh-29, Maverick, Griffin, MAM-L, Spike NLOS) | as ATGM (guided) | as ATGM | as ATGM; flares never (the target is on the ground). The helicopters' and jets' **rockets** (Hydra, S-8, and the laser-guided APKWS, a `Rocket`, so not guided) aim at the target's position at the shot with no lead; a salvo's later rockets at its position when each leaves; a tank driving at 6-10 m/s is 6-10 m on in a 1 s flight, past a 3 m spread and a 2-3 m hull: the "helicopter missiles all miss a moving tank" | none |
| anti-air missiles (Stinger, Igla, R-60, AIM-9, AMRAAM, R-37M, Buk, Patriot, S-400, Pantsir, Tamir) | guided onto the aircraft at impact | end of travel; no fuze distance: a direct hit or nothing | flares: one roll at impact, 35 % x (1 - flareResist) if flares burnt any time after launch (radar SAMs only resist by flareResist 0.5-0.85, not immune); jam / fail / APS of a tiered craft; a decoyed missile lands 5-11 m off the aircraft and its impact plays there, but the drawn missile flew on to the aircraft and vanished there: it looked like it disappeared silently | none |
| cruise missiles (JASSM, Kh-101, Kalibr, Typhon, NSM) | guided onto the target at impact | end of travel | heavy-missile point defence (PAC-3 class), APS by the stacking rule, jam / fail | none |
| unguided rockets (Hydra, S-8, Grad, Smerch, TOS) | the target's position at the shot, no lead; spread by reach; artillery brackets | end of travel at the aim point | any movement: lands where the target was | Smerch (T4) from a boss only: L3 escape ring; else none |
| shells, mortars (tank guns, howitzers, mortars, naval) | the target's position at the shot, no lead (lead only with the Fire-Control Computer gear, main weapon); spread by reach, brackets for artillery | end of travel at the aim point | movement; spread | a boss's T4+ round: L3 escape ring for its warning; a boss's shell with a 5 m+ core: a 0.8 s ring (prompt 26 B.4) |
| bombs, guided bombs | free fall: where the drop and the aircraft's speed put it; a guided bomb (JDAM, SDB, glide bomb) onto the target at impact | end of the fall | free fall: the stick misses a mover; guided: as missiles | a boss's 400 kg+ bomb (T4): L3 ring |
| kamikaze drones (FPV, Lancet, Shahed, Switchblade) | guided (Drone), swarms retarget on arrival | end of travel | APS (drones are lobbed: the systems that take lobbed rounds), interceptor drones and the microwave (`StepDroneKillers`), lasers, jam / fail, Ghost Net | none |
| flares | `FlaresUntil` set by the Flares skill (a charge each, prompt 29 S06), the Afterburner and Strafing Run gear, a P22 boss | see anti-air: one roll per missile at impact | -- | -- |

Other findings:

- **The delayed damage ("đạn dính ra 1 khoảng thời gian sau máu mới trừ").** A round's flight on screen runs on the
  render clock (`ProjectilePool` / `TracerPool` use `Time.time`), its damage on the Sim tick. Whenever the Sim runs
  slower than real time the drawn round reaches the target first and the hit points drop later: the Sandbox at a slow
  speed or stepping, a frame that needs more than `SimClock.MaxStepsPerFrame` (5) steps (the rest of the time is
  dropped), a heavy frame on a phone. The round is drawn arriving, then nothing until the step lands it.
- No round has a flight-time limit of its own; each lands at its launch-time travel. A guided round never misses by its
  target driving away (the Sim lands it on the target wherever it is), not even out of its reach.
- Sight-guided missiles (wire / beam / laser guided) keep going when their shooter dies or loses sight.
- The SAM has no proximity fuze: its blast is drawn on the aircraft, its hit is direct.
