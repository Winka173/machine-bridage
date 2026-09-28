# Machine Brigade music generator

Every music track in the game is composed by the Python scripts in this
folder and rendered offline. Nothing in here ships with the game; only the
resulting `.ogg` files in `Assets/MachineBrigade/Resources/Audio/Music/` do.

| Track        | Use                       | Key / tempo       | Length  | Loop |
|--------------|---------------------------|-------------------|---------|------|
| `menu`       | main menu                 | D minor, 80 BPM   | 108.0 s | yes  |
| `battle_1`   | battle ("Armored Advance")| E minor, 128 BPM  | 135.0 s | yes  |
| `battle_2`   | battle ("Iron Rain")      | C minor, 116 BPM  | 132.4 s | yes  |
| `battle_3`   | battle ("Air Superiority")| G minor, 138 BPM  | 139.1 s | yes  |
| `boss`       | boss fights               | B Phrygian, 92 BPM| 125.2 s | yes  |
| `siege`      | Siege / Defend / Endless  | F minor, 108 BPM  | 115.6 s | yes  |
| `victory`    | win stinger               | D major, 100 BPM  | ~8.6 s  | no   |
| `defeat`     | loss stinger              | D minor, 66 BPM   | ~9.5 s  | no   |

## Regenerate

Python 3.11, from the repo root:

```sh
python -m pip install -r Tools/music/requirements.txt
python Tools/music/fetch_tools.py          # once: FluidSynth + FluidR3_GM.sf2 (~150 MB, outside the repo)
python Tools/music/build_music.py          # all tracks -> Assets/MachineBrigade/Resources/Audio/Music/*.ogg
python Tools/music/analyze_music.py        # QA report + spectrogram PNGs
```

Useful options:

* `build_music.py menu boss` builds only those tracks.
* `build_music.py --wav-only` writes float WAV previews to the build dir and
  leaves the `.ogg` files alone.
* `build_music.py --stems` prints a per-stem loudness table (4-bar blocks),
  which is how the mix was balanced.
* `build_music.py --quality 0.5` sets the Vorbis quality (0..1, default 0.5,
  about 140-155 kbps).

The build is deterministic: the same scripts, SoundFont and FluidSynth version
give the same audio. A full build takes about 4 minutes; FluidSynth renders are
cached by content hash, so re-mixing after a mix-only change is faster.

Environment variables (all optional):

| Variable         | Default                                                   | Contents                       |
|------------------|-----------------------------------------------------------|--------------------------------|
| `MB_MUSIC_CACHE` | `%LOCALAPPDATA%/MachineBrigade/music-cache` (Windows) or `~/.cache/machinebrigade-music` | FluidSynth, SoundFont |
| `MB_MUSIC_BUILD` | `<cache>/build`                                           | render cache, previews, QA PNGs |
| `MB_FLUIDSYNTH`  | cache copy, then `fluidsynth` on PATH                     | path to `fluidsynth(.exe)`     |
| `MB_SOUNDFONT`   | `<cache>/FluidR3_GM.sf2`                                  | path to the SoundFont          |

On Linux/macOS install FluidSynth with the package manager (`apt install
fluidsynth`, `brew install fluid-synth`); `fetch_tools.py` still fetches the
SoundFont.

## How it works

1. **Compose** (`mbmusic/tracks/*.py`). Each track is a `Song` with a tempo,
   bar count, chord list and parts. Melodies are written as text
   (`"E4:0.75 E4:0.25 B4:2 ..."`), ostinatos and drums as chord-relative step
   patterns (`common.pattern_line`, `Part.hits`). Strings and brass are
   doubled on two MIDI channels detuned by about ±7 cents with a small delay
   for an ensemble sound; timing and velocity are humanised with a seeded RNG.
   SoundFont generators are adjusted per part through NRPN (sample start
   offset for sharper spiccato attacks, shorter releases).
2. **Render** (`mbmusic/render.py`). Each stem (strings, brass, drums, ...) is
   written to a MIDI file with `mido` and rendered by FluidSynth
   (`-F`, 44.1 kHz float, built-in reverb and chorus off) with FluidR3_GM.
3. **Synth layers** (`mbmusic/synth.py`). The hybrid elements are pure numpy:
   PolyBLEP saw/square pulses and bass, supersaw pads, trailer braams, sub
   booms and drum thumps, noise risers, reverse swells, metallic hats and
   clock ticks, claps and modal-synthesis "clang" metal hits.
4. **Mix** (`mbmusic/mix.py`, `mbmusic/dsp.py`). Per-stem RBJ biquad EQ, soft
   saturation, bass-mono, stereo width and kick-triggered sidechain ducking.
   Two synthetic convolution reverbs (a hall with frequency-dependent decay
   and early reflections, and a short room) plus a ping-pong delay are shared
   sends. Master: EQ, bass mono below 110 Hz, a gentle glue compressor, a 4x
   oversampled look-ahead limiter and loudness normalisation (ITU-R BS.1770
   via pyloudnorm) to -16 LUFS for the loops.
5. **Seamless loops.** Each loop is rendered for its length plus a 16-beat
   tail. The tail (note releases, reverb) is folded back onto the start, and
   every later step runs periodically: filters and dynamics get a wrap-around
   pre-roll and the reverbs use circular convolution. The last sample
   therefore flows into the first exactly as it does when the game loops the
   clip. The files contain exactly one loop, so play them with
   `AudioSource.loop = true` and no loop points.
6. **Encode.** Vorbis quality 0.5 through libsndfile (via `soundfile`), in
   small blocks, because large single writes crash the encoder on Windows.

## QA (`analyze_music.py`)

The script reports duration, bitrate, integrated loudness, sample and 4x true
peak, clipped samples, DC offset, band energy shares, stereo correlation, the
longest near-silent stretch and, for loops, seam continuity. For the seam it
reports the sample jump at the wrap against the 99.9th percentile of normal
sample steps, RMS either side, a third-octave spectral distance compared with
the track's own 4-bar downbeats, and a click detector. It writes a spectrogram
plus a short-term loudness curve per track to `<build>/qa/*.png`.

## Adding or changing a track

* Copy one of the modules in `mbmusic/tracks/`, register it in
  `mbmusic/tracks/__init__.py` and build it with `--wav-only --stems`.
* Keep the bar count a multiple of 4 and make the last bars lead back into
  bar 0; anything that rings past the end wraps into the start automatically.
* Only use permissively licensed sources. The SoundFont is FluidR3_GM (MIT).
  Do not add AI-generated audio from models with non-commercial terms.
* Record new tools or samples in
  `Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md`.
