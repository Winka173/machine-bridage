# Audio credits

Every sound in this folder is a recorded sound effect taken from a free source whose licence allows commercial use in a game without an in-game credit. Nothing here is CC-BY or otherwise attribution-bound, so no credit screen is required; the credits below are kept for provenance.

## Licences used

- **Sonniss #GameAudioGDC bundles** (60 files). Sonniss gives these bundles away every year for GDC. Licence terms (from the License.pdf shipped inside every bundle zip, and https://sonniss.com/gdc-bundle-license/): worldwide, non-exclusive, royalty-free; use on unlimited projects; use and modify for personal and commercial projects **without attribution**; games explicitly included. Restrictions: do not sell the sounds as they come (selling them inside a game is allowed), do not claim authorship of the original recordings, do not use them to train AI. Copyright stays with the original publishers named below.
  The official download page (https://sonniss.com/gameaudiogdc/) is behind a Cloudflare check, so each file was read straight out of the unmodified official bundle zips mirrored on the Internet Archive (item `sonniss.com-gdc-game-audio-bundles`); the per-file links below point to the exact file inside the exact zip.

- **CC0 1.0** (2 files, Kenney UI Audio) and **CC0 1.0** (1 file, OpenGameArt "Horde War Drums loop" by William Hector). Public domain dedication; no conditions.

## Processing applied to every file

Python (numpy, scipy, soundfile): converted to mono (channel average; a single channel is used only if averaging would cancel more than 4.5 dB), resampled to 44.1 kHz, 30 Hz high-pass (90 Hz for UI sounds, none for the drum loop), leading silence trimmed to under 10 ms (3 ms pre-roll before the onset), trailing silence trimmed, short fade-in and a fade-out, peak-normalised to -1 dBFS, then loudness matched within each category (quiet files lifted with a look-ahead peak limiter, loud files turned down), and encoded as Ogg Vorbis (quality 0.9, about 160-200 kbit/s mono, so the re-encode Unity does on import starts from a clean file). Loops are cut from a steady section and made seamless by crossfading the audio that follows the loop end into the loop start. Per-file specifics are listed below.

## Files

| File | Length | Author / publisher | Source | Licence |
|---|---|---|---|---|
| `mg/mg_1.ogg` | 0.79 s | Super Thump | Weapons of World War II - Designed: "STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav" | Sonniss GDC licence (no attribution) |
| `mg/mg_2.ogg` | 0.75 s | Super Thump | Weapons of World War II - Designed: "STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav" | Sonniss GDC licence (no attribution) |
| `mg/mg_3.ogg` | 0.75 s | Super Thump | Weapons of World War II - Designed: "STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav" | Sonniss GDC licence (no attribution) |
| `autocannon/autocannon_1.ogg` | 0.69 s | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Single Shot with Report 03.wav" | Sonniss GDC licence (no attribution) |
| `autocannon/autocannon_2.ogg` | 0.69 s | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Single Shot with Report 03.wav" | Sonniss GDC licence (no attribution) |
| `autocannon/autocannon_3.ogg` | 0.68 s | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Single Shot with Report 03.wav" | Sonniss GDC licence (no attribution) |
| `cannon/cannon_1.ogg` | 1.50 s | Bluezone Corporation | Tank - Explosion Sound Effects: "Bluezone_BC0271_tank_artillery_cannon_shot_012.wav" | Sonniss GDC licence (no attribution) |
| `cannon/cannon_2.ogg` | 1.50 s | Pole Position Production | The Warfare Library: "warfare_t1b_cannon_firing_forest_distant_MKH8060_2.wav" | Sonniss GDC licence (no attribution) |
| `cannon/cannon_3.ogg` | 1.38 s | Pole Position Production | The Warfare Library: "warfare_t1b_cannon_firing_forest_distant_MKH8060_2.wav" | Sonniss GDC licence (no attribution) |
| `heavy_cannon/heavy_cannon_1.ogg` | 2.00 s | Airborne Sound | Battlefield Howitzers: "Howitzer,M101,C1,105 mm,Distant,Right Side,Shot,Pound,Thick.wav" | Sonniss GDC licence (no attribution) |
| `heavy_cannon/heavy_cannon_2.ogg` | 1.84 s | Airborne Sound | Battlefield Howitzers: "Howitzer,M101,C3,105 mm,Distant,Right Side,Shot,Explode,Crack,Sweetener.wav" | Sonniss GDC licence (no attribution) |
| `heavy_cannon/heavy_cannon_3.ogg` | 1.98 s | Airborne Sound | Battlefield Howitzers: "Howitzer,M101,C3,105 mm,Medium Distant,Right Side,Shot,Firm,Heavy,EQ Version,Soft Attack.wav" | Sonniss GDC licence (no attribution) |
| `rocket_launch/rocket_launch_1.ogg` | 1.14 s | Pole Position Production | The Warfare 2 Library: "RPG - FIRING AND IMPACT - Through Car Roof Hit Metal - XY - MKH8040.wav" | Sonniss GDC licence (no attribution) |
| `rocket_launch/rocket_launch_2.ogg` | 1.15 s | Bluezone Corporation | Detonation - Explosion: "Bluezone_BC0277_weapon_smoke_grenade_launcher_003.wav" | Sonniss GDC licence (no attribution) |
| `rocket_launch/rocket_launch_3.ogg` | 1.27 s | InspectorJ | Essentials 03 Fireworks: "FRWKComr_InsJ_Fireworks_Launch_Close_01-03.wav" | Sonniss GDC licence (no attribution) |
| `rocket_launch/rocket_launch_4.ogg` | 1.00 s | Soundrangers | Whooshes And Transitions: "torch_whoosh_20.wav" | Sonniss GDC licence (no attribution) |
| `missile_launch/missile_launch_1.ogg` | 1.47 s | David Dumais Audio | Sci-fi Flyby Sfx Pack: "Vehicle5_BlastOff1.wav" | Sonniss GDC licence (no attribution) |
| `missile_launch/missile_launch_2.ogg` | 1.50 s | Bluezone Corporation | Combat Drone: "Bluezone_BC0288_combat_drone_jet_texture_sonic_boom_002.wav" | Sonniss GDC licence (no attribution) |
| `flak/flak_1.ogg` | 0.60 s | Sound Villain | Fireworks Malta: "053_Very strong blast, crackles, sparkle.wav" | Sonniss GDC licence (no attribution) |
| `flak/flak_2.ogg` | 0.61 s | Sound Villain | Fireworks Malta: "053_Very strong blast, crackles, sparkle.wav" | Sonniss GDC licence (no attribution) |
| `flak/flak_3.ogg` | 0.61 s | Sound Villain | Fireworks Malta: "006_Strong blast with medium crackles.wav" | Sonniss GDC licence (no attribution) |
| `flame/flame_1.ogg` | 1.50 s | SoundMorph | STEAMPUNK WEAPONS: "Steampunk Weapons - Firestorm Flamer - set_1.wav" | Sonniss GDC licence (no attribution) |
| `flame/flame_2.ogg` | 1.38 s | Gregor Quendel | Designed Fire: "Designed Fire - Impacts - Large, ignition 03.wav" | Sonniss GDC licence (no attribution) |
| `explosion_small/explosion_small_1.ogg` | 0.95 s | Bluezone Corporation | Detonation - Explosion: "Bluezone_BC0277_explosion_mortar_002_01.wav" | Sonniss GDC licence (no attribution) |
| `explosion_small/explosion_small_2.ogg` | 1.00 s | Gladestock Studios | Naval Warfare: "GS cannonball impact 005.wav" | Sonniss GDC licence (no attribution) |
| `explosion_small/explosion_small_3.ogg` | 0.92 s | Coll Anderson | Guns: "EFX EXT Mortar Explosion 08.wav" | Sonniss GDC licence (no attribution) |
| `explosion_small/explosion_small_4.ogg` | 0.96 s | Pole Position Production | The Warfare 2 Library: "Tank Mine - EXPLOSION - Mounted on Metal Beam - DISTANT - AMBEO BLD.wav" | Sonniss GDC licence (no attribution) |
| `explosion_medium/explosion_medium_1.ogg` | 2.00 s | Gamemaster Audio | Explosion Sound Pack: "explosion_med_long_tail_01.wav" | Sonniss GDC licence (no attribution) |
| `explosion_medium/explosion_medium_2.ogg` | 1.99 s | David Dumais Audio | Explosion SFX Pack: "EXPLReal_Medium Realistic Explosion 15_DDUMAIS_NONE.wav" | Sonniss GDC licence (no attribution) |
| `explosion_medium/explosion_medium_3.ogg` | 2.00 s | Bluezone Corporation | Detonation - Explosion: "Bluezone_BC0277_explosion_urban_004_02.wav" | Sonniss GDC licence (no attribution) |
| `explosion_medium/explosion_medium_4.ogg` | 2.00 s | Stefano Cremona | Explosions: "DeepExplosion02.wav" | Sonniss GDC licence (no attribution) |
| `explosion_large/explosion_large_1.ogg` | 3.00 s | Bluezone Corporation | Tank - Explosion Sound Effects: "Bluezone_BC0271_explosion_outdoors_large_005.wav" | Sonniss GDC licence (no attribution) |
| `explosion_large/explosion_large_2.ogg` | 2.51 s | Gamemaster Audio | Guns, Bullets and Explosions: "explosion_large_07.wav" | Sonniss GDC licence (no attribution) |
| `explosion_large/explosion_large_3.ogg` | 3.00 s | Gamemaster Audio | Explosion Sound Pack: "explosion_large_08.wav" | Sonniss GDC licence (no attribution) |
| `explosion_large/explosion_large_4.ogg` | 2.69 s | Bluezone Corporation | Combat Drone: "Bluezone_BC0288_combat_drone_weapon_explosion_004.wav" | Sonniss GDC licence (no attribution) |
| `explosion_huge/explosion_huge_1.ogg` | 5.00 s | Stefano Cremona | Explosions: "BigExplosion02.wav" | Sonniss GDC licence (no attribution) |
| `explosion_huge/explosion_huge_2.ogg` | 4.97 s | David Dumais Audio | Explosion SFX Pack: "EXPLDsgn_Nuclear Explosion 07_DDUMAIS_NONE.wav" | Sonniss GDC licence (no attribution) |
| `explosion_huge/explosion_huge_3.ogg` | 4.96 s | MatiasMacSD | Eradication - Small Pack: "Planet_Explosion_High-12.wav" | Sonniss GDC licence (no attribution) |
| `collapse/collapse_1.ogg` | 3.70 s | Alexander Kopeikin | Rocks: "rocks stream down heavy 02.wav" | Sonniss GDC licence (no attribution) |
| `collapse/collapse_2.ogg` | 3.85 s | Alexander Kopeikin | Rocks: "rock tumble down debris long 06.wav" | Sonniss GDC licence (no attribution) |
| `debris/debris_1.ogg` | 0.81 s | Mechanical Wave | Undoing-Computer: "Drop Fall Metal Rattle Scrap Debris_UC 10.wav" | Sonniss GDC licence (no attribution) |
| `debris/debris_2.ogg` | 0.85 s | Mechanical Wave | Undoing-Computer: "Hit Impact Metal Scrap Debris_UC 06.wav" | Sonniss GDC licence (no attribution) |
| `debris/debris_3.ogg` | 0.95 s | Mechanical Wave | Rock Brick and Dirt: "Hit Rock Debris_RBD 02.wav" | Sonniss GDC licence (no attribution) |
| `impact_metal/impact_metal_1.ogg` | 0.45 s | Mechanical Wave | Undoing-Computer: "Hit Impact Hard Metal Scrap Debris_UC 01.wav" | Sonniss GDC licence (no attribution) |
| `impact_metal/impact_metal_2.ogg` | 0.47 s | Mechanical Wave | Undoing-Computer: "Hit Impact Hard Metal Scrap Debris_UC 01.wav" | Sonniss GDC licence (no attribution) |
| `impact_metal/impact_metal_3.ogg` | 0.44 s | Gamemaster Audio | Bullet Impact Sounds: "bullet_impact_metal_heavy_08.wav" | Sonniss GDC licence (no attribution) |
| `jet_pass/jet_pass_1.ogg` | 3.66 s | Bert Foley | MiG-15 UTI: "MiG15UTI_Ext_Flyby_100m_XY.wav" | Sonniss GDC licence (no attribution) |
| `jet_pass/jet_pass_2.ogg` | 3.76 s | Sound Ex Machina | F16 Maneuvers: "F-16 Jet Fighter passing by overhead and vanishing into the horizon 03.wav" | Sonniss GDC licence (no attribution) |
| `jet_pass/jet_pass_3.ogg` | 3.67 s | Airborne Sound | Jet Fighter Maneuvers: "Jet,Fighter,F-16,Fighting Falcon,Medium Distant,By,Whip,Buffet.wav" | Sonniss GDC licence (no attribution) |
| `jet_loop/jet_loop_1.ogg` | 5.00 s | Airborne Sound | Attack Aircraft Maneuvers: "Jet,Fighter,FA-18C,Hornet,Medium Distant,Climb,Right to High,Crest and Hold,Kill Engine,191.wav" | Sonniss GDC licence (no attribution) |
| `rotor_loop/rotor_loop_1.ogg` | 2.46 s | InspectorJ | 96 General Library: "AEROHeli_InsJ_Helicopter_Flyby_Close_03_Chinook.wav" | Sonniss GDC licence (no attribution) |
| `fire_loop/fire_loop_1.ogg` | 5.50 s | Pole Position Production | The Burning House Library: "Burning_House_t2_Fire_high_intensity_with_sizzling_and_some_debris_RE50_1.wav" | Sonniss GDC licence (no attribution) |
| `wind_loop/wind_loop_1.ogg` | 8.00 s | Wav Junction Sound Effects | Wind: "0008_Wind_heavy_slow_headwind_distant_birds_cows.wav" | Sonniss GDC licence (no attribution) |
| `rain_loop/rain_loop_1.ogg` | 8.00 s | Double Trouble Audio | Rain and Thunder: "RATH - Rain Hard Loop 08.wav" | Sonniss GDC licence (no attribution) |
| `drums_loop/drums_loop_1.ogg` | 7.38 s | William Hector | Horde War Drums loop (OpenGameArt) ("horde_war_drums_by_william_hector.wav") | CC0 1.0 |
| `thunder/thunder_1.ogg` | 4.45 s | Soundrangers | Thunder: "thunder_mountainous_big_crack_02.wav" | Sonniss GDC licence (no attribution) |
| `thunder/thunder_2.ogg` | 4.55 s | InspectorJ | Essentials 01 Thunder: "THUN_InsJ_Thunder_Extremely-Close_03.wav" | Sonniss GDC licence (no attribution) |
| `thunder/thunder_3.ogg` | 4.53 s | Soundrangers | Thunder: "thunder_strike_03.wav" | Sonniss GDC licence (no attribution) |
| `siren/siren_1.ogg` | 2.78 s | Pole Position Production | Sherman M4A1 Medium Tank: "Sherman_M4A1_t11_foley_siren_long_CMC6.wav" | Sonniss GDC licence (no attribution) |
| `capture/capture_1.ogg` | 1.00 s | Chris Logsdon | Ambient Puzzle SFX Pack: "Success 2a.wav" | Sonniss GDC licence (no attribution) |
| `lost/lost_1.ogg` | 1.00 s | Chris Logsdon | Ambient Puzzle SFX Pack: "Fail 3a.wav" | Sonniss GDC licence (no attribution) |
| `click/click_1.ogg` | 0.09 s | Kenney (www.kenney.nl) | UI Audio pack ("click1.ogg") | CC0 1.0 |
| `click/click_2.ogg` | 0.07 s | Kenney (www.kenney.nl) | UI Audio pack ("click3.ogg") | CC0 1.0 |

## Per-file details

### mg

**`mg/mg_1.ogg`** (0.79 s)
- Author: Super Thump
- Original: Weapons of World War II - Designed: "STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part13of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part13of14.zip/Super%20Thump%20-%20Weapons%20of%20World%20War%20II%20-%20Designed/STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-0.80 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 260 ms fade-out.

**`mg/mg_2.ogg`** (0.75 s)
- Author: Super Thump
- Original: Weapons of World War II - Designed: "STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part13of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part13of14.zip/Super%20Thump%20-%20Weapons%20of%20World%20War%20II%20-%20Designed/STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 4.78-5.58 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 260 ms fade-out.

**`mg/mg_3.ogg`** (0.75 s)
- Author: Super Thump
- Original: Weapons of World War II - Designed: "STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part13of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part13of14.zip/Super%20Thump%20-%20Weapons%20of%20World%20War%20II%20-%20Designed/STDSGN_WoWW2_Wep_MG_M1919_Machinegun_Auto-Burst_Shot_X6.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 9.78-10.58 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 260 ms fade-out.

### autocannon

**`autocannon/autocannon_1.ogg`** (0.69 s)
- Author: Fascinated Sound
- Original: The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Single Shot with Report 03.wav"
- From: Sonniss GDC 2016 Game Audio Bundle (Sonniss.com - GDC 2016- Game Audio Bundle Part 2of6.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202016-%20Game%20Audio%20Bundle%20Part%202of6.zip/Fascinated%20Sound%20-%20The%20Gun%20Locker%20SFX%20Pack/Automatic%20Cannon%20-%20MK44%20-%2003%20-%20Single%20Shot%20with%20Report%2003.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.20-1.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 280 ms fade-out.

**`autocannon/autocannon_2.ogg`** (0.69 s)
- Author: Fascinated Sound
- Original: The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Single Shot with Report 03.wav"
- From: Sonniss GDC 2016 Game Audio Bundle (Sonniss.com - GDC 2016- Game Audio Bundle Part 2of6.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202016-%20Game%20Audio%20Bundle%20Part%202of6.zip/Fascinated%20Sound%20-%20The%20Gun%20Locker%20SFX%20Pack/Automatic%20Cannon%20-%20MK44%20-%2003%20-%20Single%20Shot%20with%20Report%2003.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: the MK44 shot layered three times 140 ms apart (rounds 2 and 3 pitched down 0.4 and 0.8 semitone) to form a short burst; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 300 ms fade-out.

**`autocannon/autocannon_3.ogg`** (0.68 s)
- Author: Fascinated Sound
- Original: The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Single Shot with Report 03.wav"
- From: Sonniss GDC 2016 Game Audio Bundle (Sonniss.com - GDC 2016- Game Audio Bundle Part 2of6.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202016-%20Game%20Audio%20Bundle%20Part%202of6.zip/Fascinated%20Sound%20-%20The%20Gun%20Locker%20SFX%20Pack/Automatic%20Cannon%20-%20MK44%20-%2003%20-%20Single%20Shot%20with%20Report%2003.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: the MK44 shot pitched down 2 semitones (varispeed) and doubled 220 ms apart: a slower, heavier two-round burst; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 300 ms fade-out.

### cannon

**`cannon/cannon_1.ogg`** (1.50 s)
- Author: Bluezone Corporation
- Original: Tank - Explosion Sound Effects: "Bluezone_BC0271_tank_artillery_cannon_shot_012.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part2of14.zip/Bluezone%20-%20Tank%20-%20Explosion%20Sound%20Effects/Bluezone_BC0271_tank_artillery_cannon_shot_012.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.50 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 550 ms fade-out; lowered 0.6 dB to match the category loudness.

**`cannon/cannon_2.ogg`** (1.50 s)
- Author: Pole Position Production
- Original: The Warfare Library: "warfare_t1b_cannon_firing_forest_distant_MKH8060_2.wav"
- From: Sonniss GDC 2017 Game Audio Bundle (Sonniss.com - GDC 2017 - Game Audio Bundle Part 6of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%206of9.zip/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%206of9/Pole%20Position%20-%20The%20Warfare%20Library/warfare_t1b_cannon_firing_forest_distant_MKH8060_2.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 2.85-4.35 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 600 ms fade-out.

**`cannon/cannon_3.ogg`** (1.38 s)
- Author: Pole Position Production
- Original: The Warfare Library: "warfare_t1b_cannon_firing_forest_distant_MKH8060_2.wav"
- From: Sonniss GDC 2017 Game Audio Bundle (Sonniss.com - GDC 2017 - Game Audio Bundle Part 6of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%206of9.zip/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%206of9/Pole%20Position%20-%20The%20Warfare%20Library/warfare_t1b_cannon_firing_forest_distant_MKH8060_2.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 16.25-17.75 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 600 ms fade-out.

### heavy_cannon

**`heavy_cannon/heavy_cannon_1.ogg`** (2.00 s)
- Author: Airborne Sound
- Original: Battlefield Howitzers: "Howitzer,M101,C1,105 mm,Distant,Right Side,Shot,Pound,Thick.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 1of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8/Airborne%20Sound%20-%20Battlefield%20Howitzers/Howitzer%2CM101%2CC1%2C105%20mm%2CDistant%2CRight%20Side%2CShot%2CPound%2CThick.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 700 ms fade-out.

**`heavy_cannon/heavy_cannon_2.ogg`** (1.84 s)
- Author: Airborne Sound
- Original: Battlefield Howitzers: "Howitzer,M101,C3,105 mm,Distant,Right Side,Shot,Explode,Crack,Sweetener.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 1of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8/Airborne%20Sound%20-%20Battlefield%20Howitzers/Howitzer%2CM101%2CC3%2C105%20mm%2CDistant%2CRight%20Side%2CShot%2CExplode%2CCrack%2CSweetener.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 500 ms fade-out; peak-limited (0.8 dB drive) to match the category loudness.

**`heavy_cannon/heavy_cannon_3.ogg`** (1.98 s)
- Author: Airborne Sound
- Original: Battlefield Howitzers: "Howitzer,M101,C3,105 mm,Medium Distant,Right Side,Shot,Firm,Heavy,EQ Version,Soft Attack.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 1of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8/Airborne%20Sound%20-%20Battlefield%20Howitzers/Howitzer%2CM101%2CC3%2C105%20mm%2CMedium%20Distant%2CRight%20Side%2CShot%2CFirm%2CHeavy%2CEQ%20Version%2CSoft%20Attack.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 650 ms fade-out.

### rocket_launch

**`rocket_launch/rocket_launch_1.ogg`** (1.14 s)
- Author: Pole Position Production
- Original: The Warfare 2 Library: "RPG - FIRING AND IMPACT - Through Car Roof Hit Metal - XY - MKH8040.wav"
- From: Sonniss GDC 2024 Game Audio Bundle (Sonniss.com-GDC2024-GameAudioBundle6of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2024-GameAudioBundle6of9.zip/Pole%20Position%20-%20The%20Warfare%202%20Library/RPG%20-%20FIRING%20AND%20IMPACT%20-%20Through%20Car%20Roof%20Hit%20Metal%20-%20XY%20-%20MKH8040.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.25-1.45 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 450 ms fade-out; peak-limited (8.0 dB drive) to match the category loudness.

**`rocket_launch/rocket_launch_2.ogg`** (1.15 s)
- Author: Bluezone Corporation
- Original: Detonation - Explosion: "Bluezone_BC0277_weapon_smoke_grenade_launcher_003.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/BluezoneCorp%20-%20Detonation%20-%20Explosion/Bluezone_BC0277_weapon_smoke_grenade_launcher_003.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.15 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 400 ms fade-out; peak-limited (0.6 dB drive) to match the category loudness.

**`rocket_launch/rocket_launch_3.ogg`** (1.27 s)
- Author: InspectorJ
- Original: Essentials 03 Fireworks: "FRWKComr_InsJ_Fireworks_Launch_Close_01-03.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/InspectorJ%20-%20Essentials%2003%20Fireworks/FRWKComr_InsJ_Fireworks_Launch_Close_01-03.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.30 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 550 ms fade-out; lowered 0.6 dB to match the category loudness.

**`rocket_launch/rocket_launch_4.ogg`** (1.00 s)
- Author: Soundrangers
- Original: Whooshes And Transitions: "torch_whoosh_20.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 5of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8/Soundrangers%20-%20Whooshes%20And%20Transitions/torch_whoosh_20.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: used the whole file; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 150 ms fade-out; lowered 0.9 dB to match the category loudness.

### missile_launch

**`missile_launch/missile_launch_1.ogg`** (1.47 s)
- Author: David Dumais Audio
- Original: Sci-fi Flyby Sfx Pack: "Vehicle5_BlastOff1.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part3of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part3of14.zip/David%20Dumais%20Audio%20-%20Sci-fi%20Flyby%20Sfx%20Pack/Vehicle5_BlastOff1.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.50 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 550 ms fade-out.

**`missile_launch/missile_launch_2.ogg`** (1.50 s)
- Author: Bluezone Corporation
- Original: Combat Drone: "Bluezone_BC0288_combat_drone_jet_texture_sonic_boom_002.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/BluezoneCorp%20-%20Combat%20Drone/Bluezone_BC0288_combat_drone_jet_texture_sonic_boom_002.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.50 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 600 ms fade-out.

### flak

**`flak/flak_1.ogg`** (0.60 s)
- Author: Sound Villain
- Original: Fireworks Malta: "053_Very strong blast, crackles, sparkle.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part12of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part12of14.zip/Sound%20Villain%20%E2%80%93%20Fireworks%20Malta/053_Very%20strong%20blast%2C%20crackles%2C%20sparkle.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 3.66-4.31 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 220 ms fade-out.

**`flak/flak_2.ogg`** (0.61 s)
- Author: Sound Villain
- Original: Fireworks Malta: "053_Very strong blast, crackles, sparkle.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part12of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part12of14.zip/Sound%20Villain%20%E2%80%93%20Fireworks%20Malta/053_Very%20strong%20blast%2C%20crackles%2C%20sparkle.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 6.04-6.69 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 220 ms fade-out.

**`flak/flak_3.ogg`** (0.61 s)
- Author: Sound Villain
- Original: Fireworks Malta: "006_Strong blast with medium crackles.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part12of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part12of14.zip/Sound%20Villain%20%E2%80%93%20Fireworks%20Malta/006_Strong%20blast%20with%20medium%20crackles.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 9.55-10.20 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 220 ms fade-out; peak-limited (2.8 dB drive) to match the category loudness.

### flame

**`flame/flame_1.ogg`** (1.50 s)
- Author: SoundMorph
- Original: STEAMPUNK WEAPONS: "Steampunk Weapons - Firestorm Flamer - set_1.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 5of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8/SoundMorph%20-%20STEAMPUNK%20WEAPONS/Steampunk%20Weapons%20-%20Firestorm%20Flamer%20-%20set_1.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.50-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 15 ms fade-in, 420 ms fade-out.

**`flame/flame_2.ogg`** (1.38 s)
- Author: Gregor Quendel
- Original: Designed Fire: "Designed Fire - Impacts - Large, ignition 03.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 3of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%203of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%203of8/Gregor%20Quendel%20%E2%80%93%20Designed%20Fire/Designed%20Fire%20-%20Impacts%20-%20Large%2C%20ignition%2003.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.40 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 450 ms fade-out.

### explosion_small

**`explosion_small/explosion_small_1.ogg`** (0.95 s)
- Author: Bluezone Corporation
- Original: Detonation - Explosion: "Bluezone_BC0277_explosion_mortar_002_01.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/BluezoneCorp%20-%20Detonation%20-%20Explosion/Bluezone_BC0277_explosion_mortar_002_01.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-0.95 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 350 ms fade-out; lowered 0.7 dB to match the category loudness.

**`explosion_small/explosion_small_2.ogg`** (1.00 s)
- Author: Gladestock Studios
- Original: Naval Warfare: "GS cannonball impact 005.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/Gladestock%20Studios%20-%20Naval%20Warfare/GS%20cannonball%20impact%20005.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 350 ms fade-out.

**`explosion_small/explosion_small_3.ogg`** (0.92 s)
- Author: Coll Anderson
- Original: Guns: "EFX EXT Mortar Explosion 08.wav"
- From: Sonniss GDC 2015 Game Audio Bundle (Sonniss.com - GDC - Game Audio Bundle 1of5.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%20-%20Game%20Audio%20Bundle%201of5.zip/Coll%20Anderson%20-%20Guns/EFX%20EXT%20Mortar%20Explosion%2008.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.20-1.20 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 380 ms fade-out.

**`explosion_small/explosion_small_4.ogg`** (0.96 s)
- Author: Pole Position Production
- Original: The Warfare 2 Library: "Tank Mine - EXPLOSION - Mounted on Metal Beam - DISTANT - AMBEO BLD.wav"
- From: Sonniss GDC 2024 Game Audio Bundle (Sonniss.com-GDC2024-GameAudioBundle6of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2024-GameAudioBundle6of9.zip/Pole%20Position%20-%20The%20Warfare%202%20Library/Tank%20Mine%20-%20EXPLOSION%20-%20Mounted%20on%20Metal%20Beam%20-%20DISTANT%20-%20AMBEO%20BLD.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.80-1.80 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 400 ms fade-out.

### explosion_medium

**`explosion_medium/explosion_medium_1.ogg`** (2.00 s)
- Author: Gamemaster Audio
- Original: Explosion Sound Pack: "explosion_med_long_tail_01.wav"
- From: Sonniss GDC 2017 Game Audio Bundle (Sonniss.com - GDC 2017 - Game Audio Bundle Part 4of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%204of9.zip/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%204of9/Gamemaster%20Audio%20-%20%20Explosion%20Sound%20Pack/explosion_med_long_tail_01.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 700 ms fade-out.

**`explosion_medium/explosion_medium_2.ogg`** (1.99 s)
- Author: David Dumais Audio
- Original: Explosion SFX Pack: "EXPLReal_Medium Realistic Explosion 15_DDUMAIS_NONE.wav"
- From: Sonniss GDC 2024 Game Audio Bundle (Sonniss.com-GDC2024-GameAudioBundle1of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2024-GameAudioBundle1of9.zip/DavidDumais%20-%20Explosion%20SFX%20Pack/EXPLReal_Medium%20Realistic%20Explosion%2015_DDUMAIS_NONE.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 600 ms fade-out; peak-limited (1.4 dB drive) to match the category loudness.

**`explosion_medium/explosion_medium_3.ogg`** (2.00 s)
- Author: Bluezone Corporation
- Original: Detonation - Explosion: "Bluezone_BC0277_explosion_urban_004_02.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/BluezoneCorp%20-%20Detonation%20-%20Explosion/Bluezone_BC0277_explosion_urban_004_02.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 700 ms fade-out.

**`explosion_medium/explosion_medium_4.ogg`** (2.00 s)
- Author: Stefano Cremona
- Original: Explosions: "DeepExplosion02.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part12of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part12of14.zip/Stefano%20Cremona%20-%20Explosions/DeepExplosion02.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 800 ms fade-out.

### explosion_large

**`explosion_large/explosion_large_1.ogg`** (3.00 s)
- Author: Bluezone Corporation
- Original: Tank - Explosion Sound Effects: "Bluezone_BC0271_explosion_outdoors_large_005.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part2of14.zip/Bluezone%20-%20Tank%20-%20Explosion%20Sound%20Effects/Bluezone_BC0271_explosion_outdoors_large_005.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-3.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 900 ms fade-out.

**`explosion_large/explosion_large_2.ogg`** (2.51 s)
- Author: Gamemaster Audio
- Original: Guns, Bullets and Explosions: "explosion_large_07.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 3of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%203of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%203of8/Gamemaster%20Audio%20-%20Guns%2C%20Bullets%20and%20Explosions/explosion_large_07.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.70 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 500 ms fade-out.

**`explosion_large/explosion_large_3.ogg`** (3.00 s)
- Author: Gamemaster Audio
- Original: Explosion Sound Pack: "explosion_large_08.wav"
- From: Sonniss GDC 2017 Game Audio Bundle (Sonniss.com - GDC 2017 - Game Audio Bundle Part 4of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%204of9.zip/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%204of9/Gamemaster%20Audio%20-%20%20Explosion%20Sound%20Pack/explosion_large_08.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-3.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 900 ms fade-out.

**`explosion_large/explosion_large_4.ogg`** (2.69 s)
- Author: Bluezone Corporation
- Original: Combat Drone: "Bluezone_BC0288_combat_drone_weapon_explosion_004.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/BluezoneCorp%20-%20Combat%20Drone/Bluezone_BC0288_combat_drone_weapon_explosion_004.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-2.90 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 500 ms fade-out.

### explosion_huge

**`explosion_huge/explosion_huge_1.ogg`** (5.00 s)
- Author: Stefano Cremona
- Original: Explosions: "BigExplosion02.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part12of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part12of14.zip/Stefano%20Cremona%20-%20Explosions/BigExplosion02.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-5.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 2200 ms fade-out.

**`explosion_huge/explosion_huge_2.ogg`** (4.97 s)
- Author: David Dumais Audio
- Original: Explosion SFX Pack: "EXPLDsgn_Nuclear Explosion 07_DDUMAIS_NONE.wav"
- From: Sonniss GDC 2024 Game Audio Bundle (Sonniss.com-GDC2024-GameAudioBundle1of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2024-GameAudioBundle1of9.zip/DavidDumais%20-%20Explosion%20SFX%20Pack/EXPLDsgn_Nuclear%20Explosion%2007_DDUMAIS_NONE.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-5.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 2200 ms fade-out.

**`explosion_huge/explosion_huge_3.ogg`** (4.96 s)
- Author: MatiasMacSD
- Original: Eradication - Small Pack: "Planet_Explosion_High-12.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 2of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%202of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%202of8/MatiasMacSD%20-%20Eradication%20-%20Small%20Pack/Planet_Explosion_High-12.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-5.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 1800 ms fade-out.

### collapse

**`collapse/collapse_1.ogg`** (3.70 s)
- Author: Alexander Kopeikin
- Original: Rocks: "rocks stream down heavy 02.wav"
- From: Sonniss GDC 2016 Game Audio Bundle (Sonniss.com - GDC 2016- Game Audio Bundle Part 1of6.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202016-%20Game%20Audio%20Bundle%20Part%201of6.zip/Alexander%20Kopeikin%20-%20Rocks/rocks%20stream%20down%20heavy%2002.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-3.80 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 1200 ms fade-out.

**`collapse/collapse_2.ogg`** (3.85 s)
- Author: Alexander Kopeikin
- Original: Rocks: "rock tumble down debris long 06.wav"
- From: Sonniss GDC 2016 Game Audio Bundle (Sonniss.com - GDC 2016- Game Audio Bundle Part 1of6.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202016-%20Game%20Audio%20Bundle%20Part%201of6.zip/Alexander%20Kopeikin%20-%20Rocks/rock%20tumble%20down%20debris%20long%2006.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-4.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 1200 ms fade-out.

### debris

**`debris/debris_1.ogg`** (0.81 s)
- Author: Mechanical Wave
- Original: Undoing-Computer: "Drop Fall Metal Rattle Scrap Debris_UC 10.wav"
- From: Sonniss GDC 2015 Game Audio Bundle (Sonniss.com - GDC - Game Audio Bundle 3of5.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%20-%20Game%20Audio%20Bundle%203of5.zip/Mechanical%20Wave%20-%20Undoing-Computer/Drop%20Fall%20Metal%20Rattle%20Scrap%20Debris_UC%2010.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: used the whole file; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 120 ms fade-out.

**`debris/debris_2.ogg`** (0.85 s)
- Author: Mechanical Wave
- Original: Undoing-Computer: "Hit Impact Metal Scrap Debris_UC 06.wav"
- From: Sonniss GDC 2015 Game Audio Bundle (Sonniss.com - GDC - Game Audio Bundle 3of5.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%20-%20Game%20Audio%20Bundle%203of5.zip/Mechanical%20Wave%20-%20Undoing-Computer/Hit%20Impact%20Metal%20Scrap%20Debris_UC%2006.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: used the whole file; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 120 ms fade-out; lowered 0.7 dB to match the category loudness.

**`debris/debris_3.ogg`** (0.95 s)
- Author: Mechanical Wave
- Original: Rock Brick and Dirt: "Hit Rock Debris_RBD 02.wav"
- From: Sonniss GDC 2015 Game Audio Bundle (Sonniss.com - GDC - Game Audio Bundle 3of5.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%20-%20Game%20Audio%20Bundle%203of5.zip/Mechanical%20Wave%20-%20Rock%20Brick%20and%20Dirt/Hit%20Rock%20Debris_RBD%2002.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.08 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 250 ms fade-out.

### impact_metal

**`impact_metal/impact_metal_1.ogg`** (0.45 s)
- Author: Mechanical Wave
- Original: Undoing-Computer: "Hit Impact Hard Metal Scrap Debris_UC 01.wav"
- From: Sonniss GDC 2015 Game Audio Bundle (Sonniss.com - GDC - Game Audio Bundle 3of5.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%20-%20Game%20Audio%20Bundle%203of5.zip/Mechanical%20Wave%20-%20Undoing-Computer/Hit%20Impact%20Hard%20Metal%20Scrap%20Debris_UC%2001.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.15-0.70 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 160 ms fade-out.

**`impact_metal/impact_metal_2.ogg`** (0.47 s)
- Author: Mechanical Wave
- Original: Undoing-Computer: "Hit Impact Hard Metal Scrap Debris_UC 01.wav"
- From: Sonniss GDC 2015 Game Audio Bundle (Sonniss.com - GDC - Game Audio Bundle 3of5.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%20-%20Game%20Audio%20Bundle%203of5.zip/Mechanical%20Wave%20-%20Undoing-Computer/Hit%20Impact%20Hard%20Metal%20Scrap%20Debris_UC%2001.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 3.90-4.45 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 160 ms fade-out.

**`impact_metal/impact_metal_3.ogg`** (0.44 s)
- Author: Gamemaster Audio
- Original: Bullet Impact Sounds: "bullet_impact_metal_heavy_08.wav"
- From: Sonniss GDC 2017 Game Audio Bundle (Sonniss.com - GDC 2017 - Game Audio Bundle Part 4of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%204of9.zip/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%204of9/Gamemaster%20Audio%20-%20%20Bullet%20Impact%20Sounds/bullet_impact_metal_heavy_08.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-0.45 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 160 ms fade-out; lowered 1.0 dB to match the category loudness.

### jet_pass

**`jet_pass/jet_pass_1.ogg`** (3.66 s)
- Author: Bert Foley
- Original: MiG-15 UTI: "MiG15UTI_Ext_Flyby_100m_XY.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 1of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%201of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%201of8/Bert%20Foley%20-%20MiG-15%20UTI/MiG15UTI_Ext_Flyby_100m_XY.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 2.80-6.60 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 600 ms fade-in, 1000 ms fade-out.

**`jet_pass/jet_pass_2.ogg`** (3.76 s)
- Author: Sound Ex Machina
- Original: F16 Maneuvers: "F-16 Jet Fighter passing by overhead and vanishing into the horizon 03.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part12of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part12of14.zip/Sound%20Ex%20Machina%20-%20F16%20Maneuvers/F-16%20Jet%20Fighter%20passing%20by%20overhead%20and%20vanishing%20into%20the%20horizon%2003.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 2.50-6.30 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 500 ms fade-in, 1000 ms fade-out.

**`jet_pass/jet_pass_3.ogg`** (3.67 s)
- Author: Airborne Sound
- Original: Jet Fighter Maneuvers: "Jet,Fighter,F-16,Fighting Falcon,Medium Distant,By,Whip,Buffet.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 1of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8/Airborne%20Sound%20-%20Jet%20Fighter%20Maneuvers/Jet%2CFighter%2CF-16%2CFighting%20Falcon%2CMedium%20Distant%2CBy%2CWhip%2CBuffet.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 1.00-4.80 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 400 ms fade-in, 1200 ms fade-out; peak-limited (6.7 dB drive) to match the category loudness.

### jet_loop

**`jet_loop/jet_loop_1.ogg`** (5.00 s, seamless loop)
- Author: Airborne Sound
- Original: Attack Aircraft Maneuvers: "Jet,Fighter,FA-18C,Hornet,Medium Distant,Climb,Right to High,Crest and Hold,Kill Engine,191.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 1of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%201of8/Airborne%20Sound%20-%20Attack%20Aircraft%20Maneuvers/Jet%2CFighter%2CFA-18C%2CHornet%2CMedium%20Distant%2CClimb%2CRight%20to%20High%2CCrest%20and%20Hold%2CKill%20Engine%2C191.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 9.00-14.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, low-pass 5000 Hz; seamless loop: the 1000 ms after the loop end is equal-power crossfaded into the head; low-passed at 5 kHz for distance.

### rotor_loop

**`rotor_loop/rotor_loop_1.ogg`** (2.46 s, seamless loop)
- Author: InspectorJ
- Original: 96 General Library: "AEROHeli_InsJ_Helicopter_Flyby_Close_03_Chinook.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/InspectorJ%20-%2096%20General%20Library/AEROHeli_InsJ_Helicopter_Flyby_Close_03_Chinook.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 8.80-11.26 s of the source; slow level drift of the fly-by evened out (gain rides within +-4 dB, 0.6 s window); loop length tuned to 2.464 s so the rotor beats stay in phase across the seam (envelope correlation 0.25); mono, 44.1 kHz, high-pass 30 Hz; seamless loop: the 350 ms after the loop end is equal-power crossfaded into the head.

### fire_loop

**`fire_loop/fire_loop_1.ogg`** (5.50 s, seamless loop)
- Author: Pole Position Production
- Original: The Burning House Library: "Burning_House_t2_Fire_high_intensity_with_sizzling_and_some_debris_RE50_1.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 5of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8/Pole%20Position%20-%20The%20Burning%20House%20Library/Burning_House_t2_Fire_high_intensity_with_sizzling_and_some_debris_RE50_1.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 60.00-65.50 s of the source; crackle peaks limited by up to 8 dB so the fire bed sits higher; mono, 44.1 kHz, high-pass 30 Hz; seamless loop: the 1000 ms after the loop end is equal-power crossfaded into the head.

### wind_loop

**`wind_loop/wind_loop_1.ogg`** (8.00 s, seamless loop)
- Author: Wav Junction Sound Effects
- Original: Wind: "0008_Wind_heavy_slow_headwind_distant_birds_cows.wav"
- From: Sonniss GDC 2020 Game Audio Bundle (Sonniss.com - GDC 2020 - Game Audio Bundle Part14of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202020%20-%20Game%20Audio%20Bundle%20Part14of14.zip/Wav%20Junction%20Sound%20Effects%20-%20Wind/0008_Wind_heavy_slow_headwind_distant_birds_cows.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 40.00-48.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz; seamless loop: the 2000 ms after the loop end is equal-power crossfaded into the head.

### rain_loop

**`rain_loop/rain_loop_1.ogg`** (8.00 s, seamless loop)
- Author: Double Trouble Audio
- Original: Rain and Thunder: "RATH - Rain Hard Loop 08.wav"
- From: Sonniss GDC 2017 Game Audio Bundle (Sonniss.com - GDC 2017 - Game Audio Bundle Part 3of9.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%203of9.zip/Sonniss.com%20-%20GDC%202017%20-%20Game%20Audio%20Bundle%20Part%203of9/Double%20Trouble%20Audio%20-%20Rain%20and%20Thunder/RATH%20-%20Rain%20Hard%20Loop%2008.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 2.00-10.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz; seamless loop: the 1000 ms after the loop end is equal-power crossfaded into the head.

### drums_loop

**`drums_loop/drums_loop_1.ogg`** (7.38 s, seamless loop)
- Author: William Hector
- Original: Horde War Drums loop (OpenGameArt) ("horde_war_drums_by_william_hector.wav")
- From: https://opengameart.org/sites/default/files/horde_war_drums_by_william_hector.wav
- Source URL: <https://opengameart.org/content/horde-war-drums-loop>
- Licence: CC0 1.0 Universal (public domain dedication), as stated on the OpenGameArt page
- What was done: cut 1.85-9.23 s of the source; mono, 44.1 kHz; seamless loop: the 5 ms after the loop end is linearly crossfaded into the head; cut exactly on the 4-bar grid at 130 BPM (bars 2-5).

### thunder

**`thunder/thunder_1.ogg`** (4.45 s)
- Author: Soundrangers
- Original: Thunder: "thunder_mountainous_big_crack_02.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 5of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8/Soundrangers%20%E2%80%93%20Thunder/thunder_mountainous_big_crack_02.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-4.50 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 1500 ms fade-out; lowered 1.3 dB to match the category loudness.

**`thunder/thunder_2.ogg`** (4.55 s)
- Author: InspectorJ
- Original: Essentials 01 Thunder: "THUN_InsJ_Thunder_Extremely-Close_03.wav"
- From: Sonniss GDC 2023 Game Audio Bundle (Sonniss.com-GDC2023-GameAudioBundle2of14.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com-GDC2023-GameAudioBundle2of14.zip/InspectorJ%20-%20Essentials%2001%20Thunder/THUN_InsJ_Thunder_Extremely-Close_03.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 1.00-5.60 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 1500 ms fade-out; peak-limited (6.3 dB drive) to match the category loudness.

**`thunder/thunder_3.ogg`** (4.53 s)
- Author: Soundrangers
- Original: Thunder: "thunder_strike_03.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 5of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8/Soundrangers%20%E2%80%93%20Thunder/thunder_strike_03.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.20-4.80 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 1500 ms fade-out.

### siren

**`siren/siren_1.ogg`** (2.78 s)
- Author: Pole Position Production
- Original: Sherman M4A1 Medium Tank: "Sherman_M4A1_t11_foley_siren_long_CMC6.wav"
- From: Sonniss GDC 2018 Game Audio Bundle (Sonniss.com - GDC 2018 - Game Audio Bundle Part 5of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8.zip/Sonniss.com%20-%20GDC%202018%20-%20Game%20Audio%20Bundle%20Part%205of8/Pole%20Position%20-%20Sherman%20M4A1%20Medium%20Tank/Sherman_M4A1_t11_foley_siren_long_CMC6.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.10-3.00 s of the source; mono, 44.1 kHz, high-pass 30 Hz, head trimmed, 2 ms fade-in, 700 ms fade-out.

### capture

**`capture/capture_1.ogg`** (1.00 s)
- Author: Chris Logsdon
- Original: Ambient Puzzle SFX Pack: "Success 2a.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 2of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%202of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%202of8/Chris%20Logsdon%20-%20Ambient%20Puzzle%20SFX%20Pack/Success%202a.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.00 s of the source; mono, 44.1 kHz, high-pass 90 Hz, head trimmed, 2 ms fade-in, 420 ms fade-out.

### lost

**`lost/lost_1.ogg`** (1.00 s)
- Author: Chris Logsdon
- Original: Ambient Puzzle SFX Pack: "Fail 3a.wav"
- From: Sonniss GDC 2019 Game Audio Bundle (Sonniss.com - GDC 2019 - Game Audio Bundle Part 2of8.zip)
- Source URL: <https://archive.org/download/sonniss.com-gdc-game-audio-bundles/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%202of8.zip/Sonniss.com%20-%20GDC%202019%20-%20Game%20Audio%20Bundle%20Part%202of8/Chris%20Logsdon%20-%20Ambient%20Puzzle%20SFX%20Pack/Fail%203a.wav>
- Official page: <https://sonniss.com/gameaudiogdc/>
- Licence: Sonniss #GameAudioGDC Bundle Licensing Agreement: royalty-free, commercial use allowed, modification allowed, no attribution required (https://sonniss.com/gdc-bundle-license/)
- What was done: cut 0.00-1.00 s of the source; mono, 44.1 kHz, high-pass 90 Hz, head trimmed, 2 ms fade-in, 420 ms fade-out.

### click

**`click/click_1.ogg`** (0.09 s)
- Author: Kenney (www.kenney.nl)
- Original: UI Audio pack ("click1.ogg")
- From: kenney_ui-audio.zip, Audio/click1.ogg
- Source URL: <https://kenney.nl/assets/ui-audio>
- Licence: CC0 1.0 Universal (License.txt in the pack)
- What was done: used the whole file; mono, 44.1 kHz, high-pass 90 Hz, head trimmed, 2 ms fade-in, 10 ms fade-out; lowered 0.8 dB to match the category loudness.

**`click/click_2.ogg`** (0.07 s)
- Author: Kenney (www.kenney.nl)
- Original: UI Audio pack ("click3.ogg")
- From: kenney_ui-audio.zip, Audio/click3.ogg
- Source URL: <https://kenney.nl/assets/ui-audio>
- Licence: CC0 1.0 Universal (License.txt in the pack)
- What was done: used the whole file; mono, 44.1 kHz, high-pass 90 Hz, head trimmed, 2 ms fade-in, 10 ms fade-out.
