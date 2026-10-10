# Machine Brigade music credits

All music in this folder is original to Machine Brigade. Our own Python
scripts in `Tools/music/` compose and render every track: the melodies,
harmony, rhythms and arrangements are written in that code (see
`Tools/music/mbmusic/tracks/`). They are not arrangements of existing music,
not sample-library loops, and not output from an AI music model. The game
may use, modify and redistribute these files freely. No in-game attribution
is required.

Rebuild the tracks with `python Tools/music/build_music.py`. See
`Tools/music/README.md`.

## Tracks

All files are Ogg Vorbis, 44.1 kHz stereo, Vorbis quality 0.5 (about
140-155 kbps). Loops are normalised to -16 LUFS integrated (ITU-R BS.1770)
with decoded peaks at or below -1 dBFS. Each loop file holds exactly one
seamless cycle: the render tail (note releases and reverb) is folded back onto
the start, so play it with `loop = true` and no loop points.

| File           | Title             | Length  | Size    | Key / tempo          | Loop |
|----------------|-------------------|---------|---------|----------------------|------|
| `menu.ogg`     | Command Briefing  | 108.0 s | 1.97 MB | D minor, 80 BPM      | yes  |
| `battle_1.ogg` | Armored Advance   | 135.0 s | 2.64 MB | E minor, 128 BPM     | yes  |
| `battle_2.ogg` | Iron Rain         | 132.4 s | 2.46 MB | C minor, 116 BPM     | yes  |
| `battle_3.ogg` | Air Superiority   | 139.1 s | 2.67 MB | G minor, 138 BPM     | yes  |
| `boss.ogg`     | Colossus          | 125.2 s | 2.37 MB | B Phrygian, 92 BPM   | yes  |
| `siege.ogg`    | Hold the Line     | 115.6 s | 2.22 MB | F minor, 108 BPM     | yes  |
| `battle_4.ogg` | Night Raid        | 105.6 s | 2.00 MB | F# minor, 100 BPM    | yes  |
| `battle_5.ogg` | Dust Devils       | 111.4 s | 2.35 MB | A Phrygian dominant, 112 BPM | yes |
| `battle_6.ogg` | Concrete Canyon   | 109.1 s | 2.13 MB | C# minor, 132 BPM    | yes  |
| `battle_7.ogg` | Frozen Front      | 112.3 s | 2.11 MB | Eb minor, 94 BPM     | yes  |
| `battle_8.ogg` | Total Offensive   | 115.2 s | 2.16 MB | Bb minor, 150 BPM    | yes  |
| `naval.ogg`    | Steel Tide        | 109.1 s | 2.07 MB | G# minor, 12/8, 88 BPM | yes |
| `boss_air.ogg` | Thunderhead       | 108.4 s | 2.16 MB | A Dorian, 124 BPM    | yes  |
| `boss_naval.ogg` | Abyssal Titan   | 108.0 s | 1.91 MB | C# Phrygian, 80 BPM  | yes  |
| `boss_land.ogg` | Iron Bastion     | 113.7 s | 2.16 MB | G harmonic minor, 76 BPM | yes |
| `boss_train.ogg` | Juggernaut Express | 113.3 s | 2.14 MB | F# Phrygian, 144 BPM | yes |
| `boss_orbital.ogg` | Orbital Lance | 106.7 s | 2.03 MB | E Lydian, 108 BPM    | yes  |
| `boss_final.ogg` | Doomsday Engine | 114.5 s | 2.17 MB | D harmonic minor, 7/4, 132 BPM | yes |
| `boss_mini.ogg` | Vanguard Hunter  | 104.0 s | 1.95 MB | B minor, 120 BPM     | yes  |
| `boss_rush.ogg` | Gauntlet         | 109.4 s | 2.12 MB | D Phrygian, 158 BPM  | yes  |
| `survival.ogg` | Last Stand        | 110.8 s | 2.19 MB | E Dorian, 104 BPM    | yes  |
| `menu_2.ogg`   | Rally Point       | 106.7 s | 2.00 MB | G Mixolydian, 90 BPM | yes  |
| `campaign.ogg` | War Room          | 106.7 s | 2.06 MB | Ab Lydian, 72 BPM    | yes  |
| `victory.ogg`  | Victory (stinger) | 8.6 s   | 0.16 MB | D major, 100 BPM     | no   |
| `defeat.ogg`   | Defeat (stinger)  | 9.5 s   | 0.16 MB | D minor, 66 BPM      | no   |

### How each track was made

* **menu: Command Briefing.** A slow build over 36 bars. It opens with a soft
  string pad, a three-note piano cell and a quiet synth pulse over a low
  drone. French horns then state the Brigade theme over a cello ostinato and
  light taiko. Trumpets, horns, brass, choir, violins and war drums bring a
  full heroic climax. The track then winds down and flows back into the
  opening.
* **battle_1: Armored Advance.** Straight 16th-note spiccato strings accented
  3+3+2, with pumping low strings, taiko, concert bass drum, snare and synth
  hats. The horn theme runs through it. The track also has a breakdown with a
  synth arpeggio and horn chorale, a trumpet climax with choir, and a
  half-time low-brass riff. A snare roll and riser lead back to the top.
* **battle_2: Iron Rain.** A gallop ostinato (one 8th, two 16ths) with a
  3+3+2 taiko groove and a military snare cadence. It also has a low-brass
  riff (trombones, tuba, celli, basses), a broad horn and trumpet theme set
  against the riff in the climax, and a snare-solo breakdown with a horn
  call and a choir.
* **battle_3: Air Superiority.** The hybrid electronic track. It has a 16th
  synth arpeggio, a synth-sub kick (four on the floor and broken beat), claps
  and hats. Over these sit string 8ths, and a syncopated theme played by
  synth brass, then trumpets and horns. Half-time sections add braams, choir
  and tremolo strings, and a filtered breakdown adds piano and a supersaw
  pad.
* **boss: Colossus.** A chromatic 16th ostinato over a B pedal in three
  octaves of strings. It has dissonant brass (a minor-second motif,
  cluster stabs and tritone chords), trailer braams, huge taiko and
  bass-drum patterns, metallic anvil hits for the "machine" colour, choir,
  and high tremolo clusters. The breakdown is a metal-clock passage with
  distant horn calls, and the track ends with a four-bar hit fill that leads
  back to the start.
* **siege: Hold the Line.** Built for fortress defence (Siege and Defend).
  A clock-tick pulse and a low 8th-note ostinato with the b6-5 tension (Db-C)
  run under timpani and a soft snare. Horn alarm calls follow, then a violin
  16th build with brass swells through a Neapolitan (Gb) lift, and a full
  trumpet and horn theme. A rising brass line peaks the track before it
  pulls back into the loop.
* **battle_4: Night Raid.** Stealth that breaks into a fight. A ticking
  clock, a pizzicato cell, celesta and a low drone open it; a low flute and
  clarinet carry the theme over a cello pulse and a heartbeat taiko. Tremolo,
  spiccato 8ths and a horn counter-line on the Neapolitan G build the
  tension until the raid breaks loose with full drums and the theme in horns
  and trumpets, then it sinks back into the shadows.
* **battle_5: Dust Devils.** The desert battle, in the hijaz colour of A
  Phrygian dominant. Hammered-dulcimer 16ths and a frame-drum maqsum groove
  (taiko dum, conga tek, tambourine) carry a shanai and oboe theme over the
  Andalusian descent. Strings answer in unison riffs and horns reply; a
  half-time breakdown has a solo flute, harp, choir and a sandstorm riser
  before the climax.
* **battle_6: Concrete Canyon.** The urban street fight, hybrid
  rock-orchestral: two distorted guitars in power chords (palm-muted chugs
  and a syncopated riff), pick bass and a rock kit under a string theme,
  then trumpets and horns over the riff, a piano and pad breakdown and a
  syncopated stab bridge.
* **battle_7: Frozen Front.** Arctic, vast and cold. High tremolo,
  glockenspiel frost, wind and a lone horn call open; a low-brass ostinato,
  marcato string 8ths and timpani carry the horn theme; choir and tubular
  bells lighten the middle before the full climax.
* **battle_8: Total Offensive.** The fastest battle track. A military snare
  cadence and spiccato 16ths drive a dotted trumpet fanfare; a broad horn and
  choir counter-theme lifts through C major; a hybrid drop (braams, synth
  arps, half-time) leads to the climax and the fanfare up high.
* **naval: Steel Tide.** The sea battle, in a rolling 12/8 swell. Wave
  arpeggios in the celli and harp, a foghorn in the low brass and a ship's
  bell open it; the horns take a sea-shanty theme; choir, tremolo and a
  trumpet counter-line swell into a climax over 12/8 war drums.
* **boss_air: Thunderhead.** Airships and air bosses. A propeller drone,
  16th violins and a synth arp under a horn motif of rising fourths in A
  Dorian; the storm turns harmonic minor with choir and trumpet stabs;
  above the clouds a tremolo, flute whistles and a high trumpet call; thunder
  booms throughout.
* **boss_naval: Abyssal Titan.** Capital ships and submarines. Slow and
  low: sonar pings through a long delay, a deep drone, whale-call braams and
  a triplet ostinato in the celli and basses; the low brass states a motif
  with the tritone on the flat second; the hull breaks the surface with brass
  chords and war drums.
* **boss_land: Iron Bastion.** Land fortresses and super-heavy tanks. A
  gothic march of steel: church organ pedal and chords, anvils and a heavy
  3+3+2 march; a brass chorale over low-string riffs; choir and doubled war
  drums through the Neapolitan Ab; organ, choir and brass together at the
  climax.
* **boss_train: Juggernaut Express.** Armoured and nuclear trains. A
  brushed "chukka" snare, piston clangs, a wheel rhythm in the low strings
  and a steam whistle; a Phrygian low-brass motif, a string theme over the
  rails, a pistons-and-synth breakdown and a full-steam climax.
* **boss_orbital: Orbital Lance.** Spacecraft and orbital bosses. Bright
  and alien in E Lydian with a flat-six turn: synth arps, a crystal pad and
  sub pulse; the choir states the theme; an electronic (808) kit drops in with
  brass "laser" stabs; a piano breakdown with countdown ticks; the brass and
  choir climax.
* **boss_final: Doomsday Engine.** The final boss and super-weapons, in 7/4
  (2+2+3) so the machine never settles. A string ostinato in seven, tolling
  bells and clangs; a choir chant over low brass; a brass motif through a C#
  diminished turn; the chant in choir, horns and trumpets at the climax.
* **boss_mini: Vanguard Hunter.** The mini bosses' track (the "mini" rank's
  music). Lighter and quicker: a hunting motif in short notes over string
  16ths and a snare-led groove, a low-brass answer in half-time, and the
  motif in canon at the climax.
* **boss_rush: Gauntlet.** Boss Rush, between its bosses. A hybrid
  four-on-the-floor engine (synth bass 16ths, sub kick) under the
  orchestra: a Phrygian brass motif, a choir and horn hymn turning to D
  major, a breakdown with a long riser, and a high trumpet counter-line.
* **survival: Last Stand.** Survival and Endless. Built in layers like the
  waves: a piano ostinato, clock ticks and a pulse, then string 8ths and the
  horn theme, then drums and brass, then the choir lift over the borrowed C
  and D; the hopeful Dorian A major keeps the grit from turning grim.
* **menu_2: Rally Point.** The second main-menu theme, warm and hopeful in
  G Mixolydian: piano arpeggios and a string pad, a horn theme over cello
  8ths, a strings counter-theme with harp, and a full statement with
  trumpets, choir and timpani.
* **campaign: War Room.** The campaign map and its briefings: pensive and
  forward-looking in Ab Lydian. A piano figure, a soft pad and a clock; a
  cello melody over a brushed snare cadence and harp; horns and strings
  swell to a resolve; a flute and glockenspiel reprise.
* **victory.** A D major fanfare on the Brigade theme: a trumpet triplet
  pickup, then D, G, A and D chords for full brass, strings and choir, with
  a string scale run, timpani roll, cymbals and a final hit.
* **defeat.** A D minor lament: a solo horn line descends over slow
  strings, and a Phrygian cadence (Eb to Dm) closes with a low timpani and
  sub impact.

### Production

1. **Composition.** Python code generates notes, dynamics (velocity and
   CC11 expression with automatic swells on long notes) and step patterns,
   with seeded humanisation of timing and velocity.
2. **Orchestral rendering.** Each stem is written to MIDI (`mido`) and
   rendered offline by FluidSynth with the FluidR3_GM SoundFont. Sections
   are doubled on detuned channels for an ensemble sound, and SoundFont
   generators are adjusted through NRPN for sharper spiccato.
3. **Hybrid layers.** These are synthesised directly in numpy by our code:
   synth pulses and bass, supersaw pads, braams, sub booms, drum thumps,
   risers, reverse swells, hats, ticks, claps and modal metal hits.
4. **Mix and master.** Our numpy/scipy code does the rest. It applies
   biquad EQ, saturation and sidechain ducking. It adds two synthetic
   convolution reverbs (hall and room) and a ping-pong delay. The master
   stage has a glue compressor, a 4x-oversampled look-ahead limiter and
   loudness normalisation. Loops are processed circularly so the end flows
   into the start without a seam.

## Tools and licences

The tools below were used offline to make the audio. None of them is shipped
with the game, and the SoundFont is not redistributed.

| Tool | Version | Licence | Use | URL |
|------|---------|---------|-----|-----|
| FluidR3_GM.sf2 (Fluid Release 3 General MIDI SoundFont) by Frank Wen | 3.1 (Debian `fluid-soundfont-gm` 3.1-6) | MIT | instrument samples | http://deb.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont-gm_3.1-6_all.deb |
| FluidSynth | 2.6.1 (win10-x64-cpp11) | LGPL-2.1-or-later | offline MIDI renderer | https://github.com/FluidSynth/fluidsynth |
| Python | 3.11 | PSF | build scripts | https://www.python.org |
| numpy, scipy | 2.x, 1.17 | BSD-3-Clause | synthesis, DSP | https://numpy.org, https://scipy.org |
| soundfile (libsndfile, libvorbis) | 0.14 (1.2.2) | BSD-3-Clause (LGPL-2.1, BSD) | WAV I/O, Ogg Vorbis encoding | https://github.com/bastibe/python-soundfile |
| mido | 1.3.3 | MIT | MIDI file writing | https://github.com/mido/mido |
| pyloudnorm | 0.2.0 | MIT | BS.1770 loudness | https://github.com/csteinmetz1/pyloudnorm |
| matplotlib | 3.10 | PSF-style (matplotlib licence) | QA spectrograms only | https://matplotlib.org |

No AI music model (for example MusicGen/AudioCraft or Stable Audio) was used.

SoundFont checksums, as verified by `Tools/music/fetch_tools.py`:

* `fluid-soundfont-gm_3.1-6_all.deb` SHA-256
  `9965fbcc6acee17d6f72b685d28c7f968ec64eba14645445b476d5c6cc2eee4c`
* `FluidR3_GM.sf2` SHA-256
  `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`

The package's copyright file
(https://metadata.ftp-master.debian.org/changelogs//main/f/fluid-soundfont/fluid-soundfont_3.1-6_copyright)
and README state the licence. The README says: "Copyright (c) 2000-2002,
2008 Frank Wen <getfrank@gmail.com>. I hereby release Fluid under the MIT
license". The MIT licence covers the SoundFont itself. Music rendered with it
is our own work and needs no attribution. The notice is reproduced here as a
courtesy:

```
Fluid (R3) SoundFont
Copyright (c) 2000-2002, 2008 Frank Wen <getfrank@gmail.com>
          2008 Toby Smithe

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
```
