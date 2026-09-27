# Mobile performance: research and status

Research run on 2026-09-26, drawing on:
- Unity and URP documentation and source;
- Android developer guides;
- the CoD Mobile, Supercell and Wargaming tech posts;
- settings screens from Genshin, Honkai Star Rail, PUBG Mobile, Wild Rift, WoT Blitz, Diablo Immortal and Art of War 3.

Everything is tuned for this game: an orthographic RTS with heavy particles and one directional light, running on Android GLES3 or Vulkan.

## Done

| Technique | Where |
|---|---|
| Shadow map fitted to the view every frame (near plane above the highest caster, range to the farthest visible ground corner, 5% fade band) | `Atmosphere.FitShadows` |
| One cascade (an orthographic camera has no perspective aliasing) | `Atmosphere` |
| Soft 4-tap on phones from Medium, hard on Low, off on Off (blob shadows then) | `Atmosphere`, `ViewRegistry.DrawBlobs` |
| Graphics preset plus Custom, frame-rate cap limited to display divisors, battery saver (Auto: under 20% and unplugged) | `GraphicsOptions`, `MatchSettings`, `MenuScreen` |
| Frame-rate governor that steps between 30, 60, 90 and 120 | `FrameRateGovernor` |
| Menus and pause rendered every other frame until touched | `MatchRunner.Update` (`OnDemandRendering`) |
| Swappy frame pacing on release builds only (it crashes the emulator) | `BuildScripts.BuildAndroid` |
| Particle screen-size cap (0.75 of view height) | `ParticleBuilder.Create` |
| Off-screen effects skip their particles (the sound still plays) | `ScreenCull`, `EffectsDirector`, `FireSpots` |
| Bloom Low: quarter resolution, 4 passes, dual filter; High: half resolution, 6 passes | `MatchRunner.ApplyPost` |
| FSR 1 upscaling below 100% resolution | `Atmosphere` |
| SRP Batcher off on GLES (stale transforms), on under Vulkan | `Atmosphere` |
| LOD cross-fade variants dropped | `Mobile_RPAsset` |
| Effects never reduced by any preset | `GraphicsOptions.For` |

## Next, by priority

1. **Test on real devices.** Emulator numbers mean nothing. Options:
   - Firebase Test Lab game-loop tests (a scripted battle with an FPS graph);
   - Samsung Remote Test Lab;
   - two cheap phones: a low-end Mali and a mid-range Adreno.
2. **Pipeline-state warm-up.** Use `GraphicsStateCollection`, recorded over a full battle for each MSAA level and tier, and `WarmUpProgressively` during loading. This removes the stutter on the first explosion under Vulkan.
3. **Thermal scaling.** Adaptive Performance is built in from Unity 6.3, with the Android ADPF provider. Use custom scalers that feed one modifier layer, and step down in this order:
   1. render scale −5%
   2. shadows 2048 → 1024, then soft → hard
   3. bloom
   4. scenery
   5. frame rate

   Never cut particles. Do not use the built-in URP scalers: they write into the asset and fight the settings.
4. **Particle fill rate:**
   - a single premultiplied-alpha material, so fire and smoke share one draw;
   - half precision;
   - a height fade instead of soft particles.
   - Later, a half-resolution particle pass composited before bloom.
5. **Tree shadow proxies.** A low-poly shadows-only mesh per instanced cell, and blob "shadow cards" for scenery beyond the map.
6. **Vulkan first,** with GLES as fallback through the device filter.
7. **Texture compression audit:** ASTC 6×6 for albedo, 8×8 for smoke.
8. **Static shadow cache,** re-rendered only when a building falls.

## Do not adopt

| Feature | Reason |
|---|---|
| GPU Resident Drawer | Needs Forward+, compute shaders and the SRP Batcher; not GLES |
| Forward+ | About 30% base GPU cost on Adreno 650 |
| STP / TAA | Needs compute; smears particles |
| VFX Graph | No GLES |
| On-tile post-processing | No bloom |
| Cascades | See above |


## 2026-09-27: after the big expansion (emulator, relative only)

`-mb-perf` on the Pixel 3a API 35 emulator (host GPU; its 30 fps cap and timings say nothing about phones, they compare maps and changes):

| Scene | fps | setpass | triangles | shadow pass |
|---|---|---|---|---|
| Ashfield Conquest | 30 (cap) | ~70 | ~380k | ~4.5 ms |
| Metro City, before | 15-19 | 200-300 | 500-640k | 10-15 ms |
| Metro City, skyline ring + static batching | 25-30 | 100-250 | 250-420k | ~7 ms |

Changes: prewarm only the vehicles a battle can field; Metro City's skyline only where the camera sees (it was 1M instanced triangles in 1631 batches); static batching of map props that never move; skill triggers at 4 Hz. Still to do on a real phone: measure the new flipbook fill (+13% quad area in the effects agent's stress rig) and the city in the dense centre.
