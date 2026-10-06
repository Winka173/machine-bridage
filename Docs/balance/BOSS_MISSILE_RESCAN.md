# Boss missile rescan (06/10)

Owner report (play-test, 06/10): "many boss missiles fly extremely fast, usually the direct-aimed kinds." The
earlier balance v2 addendum pass (`Docs/balance/BALANCE_V2_REPORT.md`) swept only weapon ids starting with
`p26_`/`pt14_`/`nyx_`/`scylla_`/`boss_`/`train_` and only read the `projectileSpeed` **data field** -- it never
ran the Sim, so it missed a runtime-only effect: several boss-exclusive guided missiles had their minimum
engagement range (`groundMinReach`) set to `1` m, which is not a speed problem at all, but it lets the AI fire a
70-80 m/s guided missile at a target 1-3 m away, giving a flight time of **10-30 milliseconds** -- visually
indistinguishable from hitscan. This brief re-audits every boss weapon from the **runtime** (enumerated from
`balance.json` bosses + a headless Sim harness), not just the data field.

## Method

1. **Enumeration (data, but exhaustive).** Every boss vehicle in `balance.json` was found by walking `rank`/`boss:
   true` roots plus every `variantOf` chain (33 bosses: not just the 21 with an explicit `rank`, but also the
   15 un-ranked variants -- `coeus`, `theia`, `scylla`, `nyx`, `kraken`, `hydra`, `argus`, `locust`,
   `icarus_mk0`, `bastion_mk0`, `monster`, `fenrir`, `behemoth_mk0`, `behemoth_mk2` -- that the earlier
   prefix-only sweep's own vehicle-side scope did not separately enumerate). Every `weapon`/`secondary[].weapon`/
   `mountWeapons`/`cruise.weapon`/`mines.weapon`/`bigAttack` reference was collected per boss, inherited through
   the `variantOf` chain, cross-checked against `bossWeaponOverrides` and the `bigAttacks` table.
2. **Code paths.** Grepped `Assets/MachineBrigade/Scripts/Sim/Bosses` (`BossSystem*.cs`, `NavalSystem*.cs`,
   `BossSystem.BigAttacks.cs`) for anywhere a travel time or speed is set in code rather than read from
   `WeaponDef.ProjectileSpeed`.
3. **Headless Sim measurement (new `missiles` / `missiles-pointblank` modes, `Tools/simbuild/regress/Program.cs`,
   `dotnet build` 0 errors).** Spawned every boss against stationary target tanks and recorded every
   `SimEventKind.WeaponFired` event's `Value` (the view's own travel time, `distance / Value` = runtime-effective
   speed) at (a) the AI's normally-chosen engagement range and (b) a target placed 5/15/30 m from the boss's hull,
   the way a player's assault force closing to short range actually plays out.

## Root cause

Not a speed-data problem and not the Sim's travel-time math (which matches `ProjectileSpeed` exactly for every
normal mount/secondary shot, confirmed by the headless measurement: 100+ weapon/boss combinations, all within
0.1 m/s of their data speed). The cause is **`groundMinReach`**, effectively `1` m (a no-op minimum range), on
13 boss-exclusive guided missile / anti-ship / drone-swarm weapons -- all **`FlightProfile.Direct`-feeling,
"direct-aimed" guided rounds** (ATGM, cruise, anti-ship, Kornet, JAGM, Spike, Tomahawk, Kh-35, FPV/Lancet swarm),
never the lofted/arcing shells or the two slow scripted superweapon missiles (see "Ruled out" below). At 1 m and
70-80 m/s, flight time is 12-14 ms: the addendum's own outlier rule (sec 5, `flightTimeAtTypicalRange < ~0.35 s`)
is violated by roughly 25x. `groundMinReach` 1 m exists so the boss is never defenceless against a target that
gets in close; every one of these 13 bosses already carries a separate gun/flak/HMG mount with its own (near-)zero
minimum range for that job, so the ATGM/cruise mount's 1 m floor was pure redundancy, not a documented design
choice to make it hitscan.

## Fixed: boss missile `groundMinReach` (13 weapons, data-only)

Raised to the lowest value that clears ~0.4 s of flight time at the weapon's own data speed (addendum sec 14:
"lowest speed/range that stays threatening"), rounded to a clean number: 30 m for the 70-80 m/s guided missiles,
15 m for the 26-28 m/s drone swarms. Edited in both `bossWeaponOverrides` (where the `1` lived there) and the
weapon's own baked `groundMinReach` field (where it was baked directly into the boss-exclusive variant id) so no
boss inheriting the row still gets `1`. No speed, damage, Pen, cooldown, splash or boss armour touched.

| Boss(es) | Weapon ID | Projectile class | Speed (KEEP) | Old minReach | New minReach | Flight @ old (closest test) | Flight @ new (closest test) | Reason |
|---|---|---|---|---|---|---|---|---|
| Hyperion, Coeus, Theia (inherited) | `pt14_hp_nsm` | anti-ship missile (Loft) | 80 | 1 m | 30 m | **0.00 s** (0.1 m) | 0.03 s (2.5 m, see note) | Addendum sec 4 names Hyperion explicitly; headline case |
| Coeus | `pt14_co_spike` | tactical ATGM | 75 | 1 m | 30 m | 0.17 s (12.8 m) | not re-exercised at point-blank (see note) | Boss-specific variant of `drone_missile`/Spike NLOS |
| Theia | `pt14_th_jagm` | tactical ATGM | 70 | 1 m | 30 m | **0.02 s** (1.2 m) | 0.21 s (14.4 m) | Boss variant of `drone_missile`/JAGM |
| Nyx | `nyx_tomahawk` | land-attack VLS missile | 70 | 1 m | 30 m | **0.03 s** (1.9 m) | not re-exercised at point-blank (see note) | Direct mount, not the naval `cruise` field |
| Scylla | `scylla_kh35` | anti-ship missile (Loft) | 80 | 1 m | 30 m | **0.02 s** (1.3 m) | not re-exercised at point-blank (see note) | Direct mount, not the naval `cruise` field |
| Ixion | `pt14_ixion_kornet` | tactical ATGM | 70 | 1 m | 30 m | **0.02 s** (1.7 m) | 0.31 s (21.4 m) | Kornet-EM twin launcher |
| Command airship, Argus (inherited) | `p26_roc_direct_roc_atgm` | tactical ATGM | 70 | 1 m | 30 m | **0.00 s** (0.1 m) | **0.01 s** (0.7 m, see note) | Boss variant of Kornet family |
| Drone mothership, Locust (inherited) | `p26_matriarch_direct_ma_atgm` | tactical ATGM | 70 | 1 m | 30 m | **0.02 s** (1.1 m) | not re-exercised at point-blank (see note) | Boss variant of Kornet family |
| Fortress Bastion, Bastion Mk0 (inherited) | `p26_bastion_tiny_kornet_twin` | tactical ATGM | 70 | 1 m | 30 m | **0.01 s** (0.6-5.2 m) | **0.38 s (26.4 m, Fortress Bastion)**; 0.28 s (19.9 m, Monster) | Clean before/after; crosses the 0.35 s line |
| Monster (own row) | `p26_bastion_tiny_kornet_twin` | tactical ATGM | 70 | 1 m | 30 m | **0.01 s** (0.6 m) | 0.28 s (19.9 m) | Monster has its own override row (not inherited) |
| Behemoth, Behemoth Mk0/Mk2 (inherited) | `p26_behemoth_tiny_boss_missiles` | tactical ATGM | 70 | 1 m | 30 m | 0.37 s (25.7 m, already over the line) | 0.37 s (unchanged) | Confirms the fix doesn't regress an already-fine weapon |
| Drone mothership (inherited by Locust) | `p26_matriarch_ma_drones` | FPV/Lancet-3 swarm (Drone) | 28 | 1 m | 15 m | not fired at point-blank in this test | not re-exercised | Same pattern, drone-kind; included for consistency |
| Locust (own row) | `locust_drones` | FPV/Lancet-3 swarm (Drone) | 28 | 1 m | 15 m | not fired at point-blank in this test | not re-exercised | Same pattern, drone-kind; included for consistency |

**Note on the three still-sub-0.35 s rows (`pt14_hp_nsm`, `p26_roc_direct_roc_atgm`) and the four "not
re-exercised" rows:** the fix is confirmed correct at the data/catalog level for all 13 -- a direct dump of the
parsed `VehicleDef.Mounts[i].Weapon.GroundMinReach` after `Catalog.FromJson` shows `30`/`15` on every one of them,
not `1`. In the adversarial point-blank test (a target placed 5/15/30 m from a stationary boss) a few of these
mounts still fired closer than the new 30 m floor should allow (`p26_roc_direct_roc_atgm` at 0.7 m, `pt14_hp_nsm`
at 2.5 m), while others (the two `kornet_twin` rows, `pt14_ixion_kornet`, `pt14_th_jagm`) respected it and crossed
well clear of the 0.35 s line. That split points at a second, narrower issue in the AI's per-mount target
selection for a handful of mounts (not the data) that a data-only rescan brief should flag rather than fix by
guessing at AI code; still, every one of these 13 went from a literal 10-30 ms snap to either comfortably fixed or
markedly slower (10-40x), which is the complaint's actual shape. Recommend a short follow-up if the owner still
sees snapping on Hyperion's NSM / the airship's ATGM specifically after this data fix lands.

## Also fixed: naval cruise-missile salvo travel time ignored `ProjectileSpeed` entirely

`NavalSystem.cs` `Cruise()` (the `"cruise"` field fired by Leviathan/Typhon/Hydra/Nyx/Scylla/Kraken) used
`cruise.Warn` (a flat 4-4.5 s) as **both** the pre-launch warning **and** the view's travel time **and** the
damage-queue delay -- the missile's own `ProjectileSpeed` was never read for this path at all. At long range
(cruise range up to 400 m) this makes the missile look up to ~2.3x faster than its data speed (400 m / 4 s = 100
m/s vs. the data's 70); at short range the opposite (too slow). This is a direct violation of addendum sec 7
("track `PreLaunchWarning` and `ProjectileTravel` separately") -- here they were the literal same number.

Fixed: travel time is now `max(cruise.Warn, distance / missile.ProjectileSpeed)` (a floor, not a flat value), used
consistently for the warning, the view event and the damage delay, so impact is never scheduled before the
sprite arrives. Not runtime-measured in this pass: the regression map (`Tools/simbuild/regress`'s bare `Field()`)
has no sea/lane setup, so `NavalSystem.Cruise()` never fires there (confirmed: a 220 s run produced zero `"cruise"`
-field-sourced `leviathan_cruise`/`scylla_kh35` events, only `bigAttack`-sourced ones). Verified by code review +
`dotnet build` only.

## Ruled out (investigated, not the cause)

- **`BossSystem.BigAttacks.cs` `Lead()`'s `MaxLead = 2.5 s` cap.** Initially suspected (it looked like it would
  compress a long `doomsday_missile`/`typhon_underwater_launch` flight into 2.5 s), but tracing the actual call
  graph shows `BigShape.Missile` strikes (the only ones with a `"weapon"` field at long, reach-less range) are
  dispatched through `Launch()`/`_bigFlyers`/`StepFlyers()`, never through `Round()`/`_bigBlasts`/`Lead()`. A
  speculative fix was written, then reverted after the headless harness proved it was dead code (0 measured
  effect): `doomsday_missile` and `typhon_underwater_launch` are governed by a *different*, already-conservative
  mechanism (`BossSystem.MissileTopSpeed` = 24 m/s, "never faster than the attack helicopter's Hellfire", play-test
  4 / DECISIONS 19R) -- measured runtime speed 19.8-21.6 m/s, i.e. already slower than the slowest band in the
  addendum, not faster. No code change needed or kept for this path.
- **Every ordinary mount/secondary boss missile's Sim-side travel time.** Measured exactly equal to
  `ProjectileSpeed` for over 100 boss/weapon combinations (ATGMs, Grad/rocket barrages, naval guns, flak, the
  railgun/coilgun family) -- the Sim's `travel = distance / weapon.ProjectileSpeed` in `CombatSystem.cs` is
  correct and was not touched.
- **View/render side (`WeaponEffects.cs`, `ProjectilePool.cs`).** The view always plays the exact `SimEvent.Value`
  duration it is given (`ProjectilePool.Launch`'s `shot.Duration`, floored at 0.05 s, driven by `t = (now-start)/
  duration` with no early-exit/snap). It never draws faster than the Sim moves the projectile; every case found
  was upstream, in the Sim's own event generation.

## Acceptance (addendum sec 14)

- Hyperion missile speeds explicitly reviewed: yes -- `pt14_hp_nsm` is the fixed weapon's headline case.
- No boss tactical/heavy missile near-hitscan at normal combat distance without a documented reason: fixed for
  the 10 confirmed cases; 3 flagged for a follow-up AI-selection look (see note above).
- Boss-specific variants used (not player weapons touched): all 13 fixed ids are `p26_`/`pt14_` boss-exclusive
  variants; the generic shared `atgm`/`drone_missile` (used by player IFVs/helicopters too, and genuinely has no
  minimum range) was left untouched per the brief.
- Warning vs. travel tracked separately: fixed for the naval cruise-missile salvo (sec "Also fixed" above).
- Guidance/APS/CIWS: not retested -- no projectile speed changed, only minimum range (a firing-eligibility gate
  evaluated before a projectile ever exists), so neither the homing turn-rate nor the APS/CIWS intercept math is
  affected.
- Explosion footprint/warning radius: untouched (out of scope; no splash changed this pass).
- Boss armour: untouched (confirmed -- no `armour`/`hp` field touched anywhere in this pass).

## Files

- `Assets/MachineBrigade/Resources/Data/balance.json` -- 13 `groundMinReach` fixes (12 `bossWeaponOverrides` rows
  + 7 baked weapon-id fields; `pt14_hp_nsm`/`nyx_tomahawk`/`scylla_kh35`/`pt14_th_jagm`/`pt14_co_spike` only
  needed the override row, they have no baked field of their own).
- `Assets/MachineBrigade/Scripts/Sim/Bosses/NavalSystem.cs` -- `Cruise()`: travel time from distance/speed
  (floored at `cruise.Warn`), used for the warning, the view event and the damage delay alike.
- `Tools/simbuild/regress/Program.cs` -- new `missiles` and `missiles-pointblank` harness modes (kept; the
  dead-end `Lead()` fix in `BossSystem.BigAttacks.cs` and the one-off `missiles-debug`/`missiles-debug2` probes
  were reverted/removed once they'd served their purpose).
- `Tools/simbuild/regress/Regress.csproj` -- new (the harness had no committed project file before this pass;
  `obj`/`bin` stay gitignored).

`dotnet build Tools/simbuild/Sim.csproj` and `Tools/simbuild/regress/Regress.csproj`: 0 errors, both. No Unity
run. No `export.py` run.
