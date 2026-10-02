# Full fix prompt, pass 0: precheck (lane A, 2026-10-02)

Read only. The full fix prompt (`Docs/prompts/fix_full_vi.txt`) and its plan (`Docs/FIX_FULL_PLAN.md`). Where it overlaps a
prompt that already ran, this prompt wins (DECISIONS "Sửa lỗi tổng hợp L0").

## 1. Which prompts ran, and the boss weapons today

| prompt | ran | DECISIONS headings |
|---|---|---|
| 26 (boss health, weapons, sizes, hunts) | yes, A-E | 26AB, 26CD, 26E |
| 27 (models, v2) | yes, waves 1-8 (the last: 8a5, `b64f85ac`) | "27 wave ..." (51 commits) |
| 28 (cloud, 1-5 + extras) | yes | "28 1" ... "28 extras" |
| 29 (L0-L8, appendix, local UI; G1 Gungnir in L7) | yes | "Prompt 29 L0" ... "Prompt 29 appendix" |
| 30 (story) | yes | "Prompt 30", "Prompt 30 local" |
| 31 (L0-L6) | yes | "Prompt 31 ..." |
| 32 (L0-L9) | yes | "Prompt 32 ..." |
| 33 (L0-L7) | yes | "Prompt 33 ..." |
| 34 (L0-L9) | yes | "Prompt 34 ..." |

Boss weapons today: the prompt 26 set (`p26_*`, 52 lines, made by `Tools/balance/p26_ab.py` from target DPS shares
main 45 % / sec 25 % / direct 20 % / close 10 %) plus the older boss lines (`boss_*`, `train_gun`, `gunship_*`, ...).
Prompt 34 L1 gave every weapon a `weaponFamilyId` (103 families); prompt 34 L2 (`p34_boss_families.py`) put the family
round (damage, core, edge) on every boss weapon **and kept the old p26 DPS as the target**, so the cadence was solved
from that DPS: the big guns fire 3-12 times faster than real (Behemoth's 2A65 152 mm every 1.85 s, Bastion's M284 every
2.33 s, the 2B8 240 mm every 7.7 s, the 2A44 203 mm every 5.7 s, Ixion's 125 mm every 1.03 s, Moloch's 120 mm HE every 1.13 s)
and the small side mounts fire very rarely (Kornet every 32-56 s, Jötunn's 2A38 every 103 s, Behemoth's tiny 120 mm every
20 s, the 57 mm every 41 s). Prompt 34 L4 added `barrels` / `salvoMode` (SIMULTANEOUS) on 9 guns (ships, heavy turret,
HQ, super tank). This prompt says the p26 DPS was wrong from the start: the cadence goes first, the DPS is the result (L3).

## 2. Where the card's calibre comes from ("26 MM" on Behemoth)

`Game/Hud/WeaponInfo.Describe` names a weapon by its kind (`wpn.gun` = "Main gun" for every direct-fire shell weapon,
whatever its mount) and adds the **first 2-3 digits of the weapon id** as "N mm" (`Regex (\d{2,3})`). Every prompt 26
id starts `p26_`, so every boss gun reads "MAIN GUN 26 MM" (the detail page `MenuScreen.Detail.VehicleWeapons` and the
battle HUD's weapon line both use it). `UnitLines.WeaponName` (the "More" lines) reads the data's `size`, which holds
mm for guns but kg for bombs, missiles and drones, kW for lasers and MJ for railguns (prompt 34 L1 limited the "mm" to
gun families). A laser has projectile Bullet, so `WeaponInfo.Kind` calls it a machine gun.

## 3. "every X s"

`detail.weaponLine` ("{damage} dmg · every {seconds} s") shows `w.Cooldown`, or `w.ClipReload` for a magazine gun:
only the pause after the last round, not the full cycle. A 2-round salvo every 8.93 s and a 41-round magazine changed in
3.38 s read alike; the burst count is shown as "x N" on the damage only. The full cycle (`FirePower.Sustained`,
`WeaponDef.RoundsPerCycle`) is computed but not shown, nor the sustained DPS or the barrel count.

## 4. Audio

`Game/Audio/AudioDirector`: 32 pooled one-shot voices (2D AudioSources, panned by screen x, a low-pass that closes with
distance, a speed-of-sound delay for big blasts far off), 8 loops (ambient, rotor, jet, UI, rain, fire, boss drums,
beam), 20 sound categories each with a bank, a voice limit, a cooldown and a priority; the quietest least important
voice is cut when full; big blasts duck the small arms. No AudioSource per shot or per unit. Clips are recorded
(Resources/Audio, CREDITS.md) or synthesised (`SoundSynth`). No Unity AudioMixer groups. (Lane C owns L7.)

## 5. Blast and smoke VFX

`Game/Effects`: `BlastLayers` (ExplosionEffect.cs), a dozen shared world-space particle systems (flash, fireball, smoke,
sparks, shockwave rings) every blast emits into, sized by `BlastSizes` (ExplosionTier x ImpactScale, so a bigger blast is
the same prefab scaled). Pools: `TracerPool` 320, `ProjectilePool` 96 (grows to 512), `DebrisPool` / `DecalPool` (ring
buffers sized by `EffectBudget`), `MuzzleFx`, `FireBudget` (8 fire points a boss). Lifetimes are per layer, not per
calibre tier; no LOD by distance; camera shake falls off with distance and has a setting but no calibre rule or cap.
(Lane B owns L6.)

## 6. Flares

The Sim: a `Flares` skill (heli 20 s, jet 16 s, bomber 11 s; `Docs/checks/flare_baseline.md`), one use = one decoy
event. The view (`EffectsDirector.FlareSalvo`): each `Flares*` / flare point of the model (`VehicleView.FlarePoints`,
from prompt 29 5.5 / wave 4c tubes on eleven models) fires `Emitters.Flares`, 4 bright points fanning down and out with
short smoke trails, 1.6-2.2 s; a model without points fires from under both sides of the hull. Count per release is 4
a dispenser whatever the aircraft. No `Mount_Flare` naming convention yet. (Lane B owns L4 flares.)

## 7. Models rebuilt in prompt 27

436 GLBs were touched by the prompt 27 commits (waves 1-8; the bosses in wave 5a-5d: behemoth, behemoth_inferno,
behemoth_tempest, fortress_bastion, fortress_hive, command_airship, drone_mothership, mega_gunship, sky_fortress,
daedalus, morrigan, kronos, moloch, earth_borer, nuke_train, armored_train, leviathan, caspian, typhon,
landing_hovercraft, supreme_command; towers in wave 6, structures in wave 7, the rest in wave 8). The list: `git log
--name-only --grep="27 wave\|Wave [0-9]" -- 'Assets/MachineBrigade/Resources/Models/*.glb'`. (L8 is the lead's.)
