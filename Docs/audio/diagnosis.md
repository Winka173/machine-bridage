# Audio diagnosis (fix pass L7, 2026-10-02)

The owner: "everything sounds 'keng keng'; blasts and shots lost their punch compared with before". The numbers below come
from `python Tools/sfx/analyze_sfx.py` (the clips as they were before this pass: `Docs/audio/metrics_before_fix.json`) and
from `git show 01f19757` (prompt 34 L6, the commit that brought the synthesised tiered sounds). The commit before the blasts
got weak is `793259a9` (01f19757~1): every shot and blast then played the recorded Sonniss clips.

## 1. Where the "keng" comes from

Not ricochets as such (a ricochet, `Projectile.Bounce`, lands with the same `ProjectileImpact` as any round; there is no ricochet sound) and not the armour hits alone: **every landing of a kinetic round
without a blast played a metal clip, whatever it struck.**

| path (before this pass) | what plays | when |
|---|---|---|
| `AudioDirector.P34.ImpactBank`: `DamageType.Kinetic && SplashRadius <= 0` and tier >= 1 | `p34/blast_ap_t1..t4` | every landing of 29 weapons: the 25-30 mm autocannons and gatlings (GSh-30, GAU, 2A42, the gunship's 25 mm), every tank gun (105-125 mm AP), the railguns and the coilgun, Leviathan's AK-127 |
| `ProjectileImpact` under `ExplosionTier.Medium` with no tiered bank | `impact_metal` (recorded) | every landing of the 14 T0 machine guns, and every interception (`Intercepted`) |

It did not matter whether the round struck armour, the ground or a building, or whether it went through: the event carried
no penetration bit and the view never looked. The autocannons fire in streams, so their hits came as a run of rings:
"keng keng keng".

`blast_ap_t*` is literally a bell: `build_sfx.blast_ap` adds five damped sines at 1520-1900 Hz x (1, 1.41, 2.23, 3.07, 4.9),
decaying over 0.08 + 0.04 x tier seconds (up to 0.24 s), on top of a short noise burst. The analyser's keng detector (a
2-6 kHz peak 12 dB or more over its 1/3-octave median, under 160 Hz wide, taking 120 ms or more to fall 20 dB) flags all
eight `blast_ap` clips: **36 dB prominence, 0.29-0.56 s ring** (every other battle clip: 3-7 dB, under 0.3 s). The only
other clips flagged were the two `train_horn` clips (a horn is tonal; rebuilt below a 2 kHz top).

Before prompt 34 a tank gun's hit (impactTier `Medium` in the data) played a recorded `explosion_medium`: a thud, not a ring.

## 2. Why the blasts and shots lost their punch (793259a9 -> 01f19757)

| what changed | before (793259a9) | after (01f19757) | effect |
|---|---|---|---|
| clips | recorded Sonniss blasts and guns (`explosion_*`, `cannon`, `heavy_cannon`, `mg`, `autocannon`, launches) | synthesised `p34/*` for every gun of a family, every HE / AP / HEAT / thermobaric landing, every rocket and missile of T2+, every wreck | the recorded clips stayed on disk but nothing played them any more |
| loudness of the clip | `explosion_medium` M-max -12.4 LUFS, `explosion_large` -13.5, `explosion_small` -16.0; `cannon` -15.5, `heavy_cannon` -14.3, `mg` -14.0 | `blast_he_t2` -16.1, `blast_he_t3` -15.7, `blast_he_t1` -18.6; `shot_t2` -17.0, `shot_t3` -15.1, `shot_t0` -21.5 | 2-4 dB quieter blasts, 1-7 dB quieter shots at the same bank level |
| why the clips are quieter | recorded and loudness-matched per category (crest 11.5-12.5 dB) | every clip peak-normalised to -1 dBFS with a 6 ms noise crack as its peak and no saturation or limiting: crest 14.7-17.7 dB for T1-T3 blasts, 20.6 dB for T0 shots | the crack takes the headroom, the body sits low |
| low end | `explosion_small` 72 % of its energy under 150 Hz, `explosion_medium` 57 % | `blast_he_t1` 16 %, `blast_he_t2` 39 % (the builder's note: "phones play little under 150 Hz: the rumble stays under the mid body") | the small and medium blasts have no weight |
| off-screen gain | none | `OffScreenGain = 0.6` (-4.4 dB) for anything off the screen | far half of the battle 4.4 dB down on top |
| bank levels | `explosion_medium` 0.72 x 0.85, `explosion_large` 0.88 x 0.85 | `blast_he_t2` 0.7 x 0.9, `blast_he_t3` 0.8 x 0.9 | about the same: the loss is in the clips, not the levels |
| mixer / compression / limiting | none (no AudioMixer asset, 32 AudioSources straight to the listener) | none | nothing changed, and nothing glued the mix either |
| voices | 32, per-bank limits 2-4, cooldowns 0.04-0.1 s | 32, of which 24 for ordinary effects (the last 8 kept for warnings and T5 / boss), per-bank limits 2-4 | in a busy fight the 25th sound is cut, and blasts compete with the metal rings for the same voices |
| AP hits | `explosion_medium` (recorded thud) | `blast_ap_t*` (synthesised ring) | the keng above, in place of a thud |

In short: the punch was lost because the recorded clips were replaced by synthesised ones that are 2-4 dB quieter at the
same level (a peak-normalised crack with a thin body and, for T0-T2, little energy under 150 Hz), and off-screen sounds
lost another 4.4 dB. No mixer, compressor, limiter or volume cap was ever involved.

## 3. What this pass does about it (details in DECISIONS "Sửa lỗi tổng hợp L7")

- A new library (`Resources/Audio/sfx`, `Tools/sfx/build_sfx.py`): shots and blasts by size class, each premixed into one
  file from a main layer (the recorded Sonniss clip where it was better, restored; synthesised for small arms), a sub layer
  under 150 Hz that rises with size, and a tail / echo that grows with size; loudness by size baked into the file through a
  limiter (so the size, not a crack, sets the level).
- Hits by surface: metal only for a kinetic round that strikes a vehicle's armour and does not penetrate it (a match-wide
  rate cap), a heavy impact when it penetrates, earth on the ground, concrete on buildings and fixed defences. The view reads
  the penetration from the event it already has (the struck entity and the hull contact point) and the target's armour.
- A code-side mixer: the four groups (Effects, Music, Dialogue, UI), a compressor on the Effects voices and a limiter on the
  output, camera-distance falloff, 24 effect voices cut by the prompt's priority, no AudioSource per round.
- `Docs/audio/metrics.md` (every clip, the per-size table, the keng list) and three offline test mixes in `Docs/audio/samples`.
