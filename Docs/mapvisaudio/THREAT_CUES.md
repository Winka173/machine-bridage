# Threat cue table (MVA W1-B, spec parts AE, AF, AG, AN, BL)

Source of truth: `Assets/MachineBrigade/Scripts/Game/Effects/ThreatCues.cs` (this page mirrors it). Audio classes: `Game/Audio/AudioPolicy.cs`
(P0-P1 are never virtualised during their active warning and play on the CriticalWarnings bus with their own slider). Every row is kept
on the Low graphics preset (spec part AN) and is not occluded by smoke, decals or debris (rings draw above them; super weapons on top).

| threat | prio | visual telegraph | telegraph shape = danger shape | min lead | audio cue | cancel | impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| artillery incoming (ordinary shells) | P1 | none: owner rule play-test 14 (zoneless howitzer / mortar) | - / blast core + edge | 1.15 s | warn_whistle | lands on its clock | blast by tier |
| heavy round (203 mm+, 300 mm+ rocket, 400 kg+ bomb) | P1 | escape ring pair, fades in | edge + core = blast edge + core | 2.5 s (floorT4) | warn_whistle; 406 mm+: warn_whistle_big (P0) | ring off the frame it lands | blast by tier |
| missile incoming (guided, direct) | P1 | the missile + motor plume | path / warhead splash | 0.4 s | missile_hiss at the target (P1 when aimed at the player's unit) | ends with the round | SC / HE impact |
| top attack | P1 | climb-dive flight + closing dive ring on the target + vertical dive line falling onto it (TopAttackMarks) | ring closing on the target / the target | 0.9 s | warn_topattack (P1): lock tones + rushing dive, its own pattern | ring and line off on landing or target gone | overhead SC impact |
| bomb (unguided) | P1 | none (owner rule); 400 kg+: escape ring | edge = blast edge | 1.15 s | warn_whistle; boss / 406 mm-class: big whistle (P0) | lands on its clock | HE blast |
| bomb stick | P1 | STICK_RECT rectangle | rectangle = stick footprint | 1.15 s | warn_whistle per stick | ends with the run | chain of blasts |
| support strike | P1 | strike zone (line / circle) | zone = support radius / blast inside | 1.15 s | warn_whistle (+ halfway on long barrages) | zone fades | the support's blasts |
| boss super weapon | P0 | big-attack zone, always shown, on top | zone = attack area | 2.5 s | its own super cue alarm + big whistle | zone fades | T4-T5 blast |
| super-heavy strike (T5) | P0 | escape ring pair as super weapon | edge + core | 4 s (floorT5) | warn_whistle_big | ring off on landing | T5 blast |
| thermobaric | P1 | as its carrier (ring from T4) | edge = pressure blast | 2.5 s | carrier's whistle / hiss; blast_thermo on impact | ends with the round | thermobaric blast |
| mine detected | P1 | amber ring pulsing 3x on the trigger radius for 3 s (HazardCues), then the mine model | trigger radius = trigger radius | 0 (found, not incoming) | warn_mine ping (P1) | fades after 3 s | mine blast |
| EMP | P1 | electric ring snapping out to the EMP radius, 1.4 s (HazardCues); the support's strike zone is its lead | EMP radius = EMP radius | 0 (skill) / 1.15 s (support zone) | emp_burst (P1 when it reaches the player's units) | fades | knocked-out crackle on the units hit |

MVA W2-B: every cue reports to `Game/Effects/CueFeed.cs` the moment its sound gets a voice: captions (Settings "Warning
captions", `Hud/CueCaptions.cs`, with an arrow for an off-screen spot) and the view telemetry read it. P0 / P1 cues carry
25 % farther than effects, are never dropped from a full schedule queue, and an incoming missile's hiss is never thinned.
Warnings are never occluded (AudioDirector.Space). Weather: danger telegraphs get `WeatherPresentation.TelegraphBoost`.

Rules: a top-attack cue is only ever shown for a weapon marked top attack (`ThreatCues.Of`), never for direct fire. The warning-rings
setting (Full / Important / Off) is the player's choice; Off keeps the super weapons' rings, and the audio cues stay. Haptics: none
mapped yet (spec part BI is P2). Known gap: a shot whose shooter and target are both off screen at launch draws no ring (ScreenCull).
