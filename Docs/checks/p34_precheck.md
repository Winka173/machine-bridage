# Prompt 34 pass 0: precheck (read only, 2026-10-02)

Nothing was changed for this file; it records how the code stood before prompt 34.

## 1. Sustained DPS of a boss weapon

- `WeaponDef.SustainedDps` / `FirePower.Sustained` (Sim/Combat/FirePower.cs): the rounds of one cycle over the cycle.
  A cycle is `cooldown + (burst - 1) x burstInterval` for a salvo, or `(clip - 1) x cooldown + clipReload` for a magazine
  (`CycleSeconds`, `RoundsPerCycle`). A launcher with `ammo` adds its `MagazineReload` once a magazine (`reload`, or
  0.4 x the time to fire the magazine, between 10 and 28 s). An aircraft's stores add their rearm time.
- The boss's own factors go on top: `weaponDamage` (prompt 25 C1, ground targets only, not on laid weapons),
  `OutgoingDamageMult`, the rank's x1.4 damage and x1.25 rate, phase 3's `fireRate 1.25`.
- Weapons the boss system lays are counted outside the combat system. A ship's salvo is
  `turrets x shells x damage / every`, e.g. Leviathan 3 x 1 x 1,200 / 10 s = 360. A cruise missile is `damage / every`.
  A bombard is `damage / every`; it covers Gungnir only.
- Offline: `Tools/balance/steps_c.sustained` (the same cycle; `reload` 0 when it is not in the data, where the C# derives
  one) and `steps_c.boss_dps` (per mount against armour 3: type factor x penetration step), used by `p26_ab.py`.
  Per-boss totals before prompt 34: `p26_ab.py` dry run and DECISIONS 26AB.

## 2. Boss weapons that warn today, and for how long

- **Boss gun shells** (26 B.4, `EffectsDirector.BossShellWarning`): any boss mount weapon that is not laid, with a core of
  5 m or more and a flight of at least 1.2 s, lobbed or a shell. The view draws a ring of the **core** size, in the view
  only, for the last **0.8 s** of the flight. Nothing in the Sim; no edge ring before impact; no minimap mark.
  This covers the 152/155, 203 and 240 mm guns, the 120 mm HE, the 105 mm, Roc's bomb strings (shells), and the Grad and
  "Smerch" pods. Smerch and Grad only qualify where their core is 5 m (Behemoth, Jotunn); the 4.5 m Grads have no ring.
- **Leviathan / Kraken 406 mm salvo** (`salvo.warn` 3 s): a `StrikeWarning` per shell (support `leviathan_shell`).
- **Cruise missiles**: Leviathan 5 s; Typhon, Scylla and Caspian use the cruise default.
- **Big attacks** (super weapons, B6): 3-4 s, zones of the core size. Monster's warning is 4 s.
- **Gungnir's bombard**: 3 s ring at the aim plus the aiming line (`AimLines`, prompt 29 G1).
- The guns' warning depends on the shell's flight time. A shell with a short flight (direct fire, short range) gets
  less than 0.8 s or no ring at all.

## 3. VFX and audio systems

- **VFX** (Game/Effects): `BlastLayers` (ExplosionEffect.cs) are a dozen shared world-space particle systems (flash,
  fireball, smoke, sparks, shockwave rings) that every blast emits into. No blast is cut short. Pools:
  `TracerPool` 320, `ProjectilePool` 96 (it grows to `MostShots` 512), `DebrisPool` and `DecalPool` (ring buffers sized
  by `EffectBudget`), `MuzzleFx` (flashes that follow the barrel), `FireBudget` (8 fire points per boss, 5 on Low),
  `ScreenCull` (shots entirely off screen are not drawn). Sizes come from `BlastSizes`, which scales by `ExplosionTier`
  and `ImpactScale`. There is no LOD by distance. Camera shake is `EffectsDirector.Shake`: trauma on `RtsCamera`, falling off with distance
  (amount / (1 + d / 25 m)) and scaled by the setting `MatchSettings.ScreenShake` (off / low / full). It has no tier rule and no cap of its own.
- **Audio** (`AudioDirector`): **32 pooled one-shot voices** (2D AudioSources, panned by screen x, a low-pass that
  closes with distance, delayed by the speed of sound for big blasts far off). There are 8 loops (ambient, rotor, jet,
  UI, rain, fire, boss drums, beam). Each sound has one bank per category (MachineGun ... ExplosionHuge, 20 categories)
  with a voice limit, a cooldown and a priority. When the voices are full, the least important and quietest voice is
  cut. Big blasts duck the small arms. A shot takes a pooled voice; there is no AudioSource per shot and none per unit.
  Clips are recorded (Resources/Audio, CREDITS.md) or synthesised by `SoundSynth`.

## 4. Wrecks and crashing aircraft

- **Wrecks** (`WreckManager`, view only): a dead vehicle's own model stays. It burns for 12 s and lives about 17 s
  (+-15 %), then sinks 2.2 m in 3 s. The death blast tears pieces off (`ChunkThrower` into `DebrisPool`), bucks the hull and can
  throw the turret. A turret-ring fountain plays now and then. Static wrecks burn 45 s. A ship lists, breaks in two
  (Leviathan) and sinks (`ShipSinking`). A wreck is dropped sooner when there are more than the budget allows.
  No wreck blocks movement or sight in the Sim (the Sim removes the vehicle).
- **Crashing aircraft** (`DamageSystem.ScheduleCrash`, Sim): when an aircraft dies, the Sim queues a `PendingExplosion`
  at `now + fall` (fall = sqrt(2 x height / g), g 11 m/s^2 for aeroplanes and 7 for helicopters). The point is
  where its momentum carries it (0.8 x speed over the glide, clamped to the map). The blast (`CrashBlast`) is 8 % of
  max HP (60-450) over 3.5 + HP/800 m (4-10 m) and hits either side. The view's fall (VehicleView, the same g)
  lands on that point and time. A tiered boss's crash (`BossSystem.Tiers`) queues its own Ultimate blast.

## 5. Preview scenes

- **Turntable** (`UnitPreview`, detail pages for vehicles, bosses and towers): the model on a turntable against a
  transparent background (the menu's own backdrop), with no ground, water or rail under it.
- **"In action" / "Xem bắn"** (`FiringRange`): a small real simulation on one flat **260 m ground quad**
  (`materials.Ground`) for every kind of unit. Ground vehicles, towers and bosses stand on it. Ships and boats sit on
  the same ground quad (no sea). Trains and the train bosses (Juggernaut, Nemesis, Gungnir) have no rail.
  Aircraft fly over the ground quad at their altitude. The targets are ground vehicles of armour 0-4 and an attack
  helicopter for anti-air.
- **Ammo guide**: icons and text only, no 3D scene.
