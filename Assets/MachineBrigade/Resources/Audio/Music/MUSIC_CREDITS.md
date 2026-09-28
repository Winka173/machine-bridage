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
* **siege: Hold the Line.** Built for fortress defence and Endless waves.
  A clock-tick pulse and a low 8th-note ostinato with the b6-5 tension (Db-C)
  run under timpani and a soft snare. Horn alarm calls follow, then a violin
  16th build with brass swells through a Neapolitan (Gb) lift, and a full
  trumpet and horn theme. A rising brass line peaks the track before it
  pulls back into the loop.
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
