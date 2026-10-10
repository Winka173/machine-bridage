"""Instrument factories, stem presets and pattern helpers shared by all tracks."""

from __future__ import annotations

import zlib

import numpy as np

from .. import SR
from .. import synth
from ..score import Part, Song
from ..theory import chord, n, root, voicing

# ----------------------------------------------------------------------------
# Stem presets (EQ: (kind, freq, q, gain_db))
# ----------------------------------------------------------------------------

STEMS = {
    "str_hi": dict(eq=[("hp2", 90), ("peak", 380, 1.0, -2.0), ("peak", 2800, 0.9, 1.5)], hall=0.34, width=1.15),
    "str_lo": dict(eq=[("hp2", 32), ("peak", 220, 0.9, -0.5), ("peak", 1500, 1.0, 1.0)], hall=0.24, mono_below=90),
    "ost": dict(eq=[("hp2", 60), ("peak", 300, 1.0, -2.0), ("peak", 3200, 1.0, 2.0)], hall=0.22, room=0.12, width=1.1),
    "brass": dict(eq=[("hp2", 55), ("peak", 450, 1.0, -2.0), ("peak", 2200, 1.0, 2.0)], hall=0.36, room=0.05),
    "horns": dict(eq=[("hp2", 60), ("peak", 350, 1.0, -1.5), ("peak", 1800, 1.0, 1.0)], hall=0.46, width=1.1),
    "low_brass": dict(eq=[("hp2", 35), ("peak", 300, 1.0, -1.5), ("peak", 1200, 1.0, 2.0)], hall=0.28, drive=0.15, mono_below=100),
    "choir": dict(eq=[("hp2", 130), ("peak", 2500, 1.0, -1.0), ("hs", 8000, 0.7, -2.0)], hall=0.6, width=1.2),
    "drums": dict(eq=[("hp2", 30), ("peak", 65, 0.9, 1.5), ("peak", 420, 1.0, -3.5), ("peak", 3000, 1.0, 1.5)], room=0.28, hall=0.16, mono_below=160, drive=0.1),
    "snare": dict(eq=[("hp2", 110), ("peak", 900, 1.0, -1.0), ("peak", 5000, 1.0, 1.5)], room=0.32, hall=0.12),
    "timp": dict(eq=[("hp2", 32), ("peak", 350, 1.0, -2.0)], hall=0.3, room=0.12, mono_below=120),
    "cym": dict(eq=[("hp2", 350)], hall=0.28, width=1.2),
    "synth": dict(eq=[("hp2", 80), ("peak", 400, 1.0, -2.0), ("hs", 7000, 0.7, -2.0)], hall=0.12, delay=0.18, duck=0.55, width=1.2),
    "bass": dict(eq=[("hp2", 30), ("lp", 2500), ("peak", 250, 1.0, -1.5)], duck=0.5, mono_below=200),
    "sub": dict(eq=[("hp2", 24), ("lp", 5000)], hall=0.1, room=0.05, mono_below=200),
    "fx": dict(eq=[("hp2", 150), ("hs", 9000, 0.7, -3.0)], hall=0.35, width=1.3),
    "keys": dict(eq=[("hp2", 110), ("peak", 3000, 1.0, -1.0)], hall=0.5, delay=0.12),
    "pad": dict(eq=[("hp2", 90), ("peak", 500, 1.0, -2.0), ("hs", 7000, 0.7, -3.0)], hall=0.4, duck=0.3, width=1.3),
    "hats": dict(eq=[("hp2", 4000), ("hs", 11000, 0.7, -2.0)], room=0.2, hall=0.05, width=1.0),
    "metal": dict(eq=[("hp2", 150), ("peak", 3500, 1.0, -2.0)], hall=0.35, room=0.2),
    "drone": dict(eq=[("hp2", 28), ("lp", 1800)], hall=0.25, duck=0.25, width=1.3),
}


def setup_stems(song: Song, gains: dict[str, float] | None = None, **overrides) -> None:
    """Create every preset stem; ``gains`` sets per-stem gain in dB."""
    gains = gains or {}
    for name, cfg in STEMS.items():
        c = dict(cfg)
        c.update(overrides.get(name, {}))
        song.stem(name, gain_db=gains.get(name, 0.0), **c)


# ----------------------------------------------------------------------------
# Instruments (FluidR3_GM programs)
# ----------------------------------------------------------------------------

def spiccato(song: Song, name: str = "spic", stem: str = "ost", vol: int = 100, pan: float = 0.0, ens: int = 2) -> Part:
    """Short bowed strings: sample start skipped for a sharp attack, short release."""
    p = song.part(name, 48, stem=stem, volume=vol, pan=pan, ens=ens, ens_cents=6, human_t=0.004, human_v=6)
    return p.start_offset(2600).release(-3400)


def pizz(song: Song, name: str = "pizz", stem: str = "ost", vol: int = 90, pan: float = 0.0) -> Part:
    return song.part(name, 45, stem=stem, volume=vol, pan=pan, ens=1, human_t=0.004)


def strings(song: Song, name: str = "strings", stem: str = "str_hi", vol: int = 100, slow: bool = False,
            pan: float = 0.0, ens: int = 2) -> Part:
    p = song.part(name, 49 if slow else 48, stem=stem, volume=vol, pan=pan, ens=ens, ens_cents=7,
                  human_t=0.008, legato=0.06, swell=0.5)
    return p.start_offset(600 if slow else 1200)


def tremolo(song: Song, name: str = "trem", stem: str = "str_hi", vol: int = 95) -> Part:
    return song.part(name, 44, stem=stem, volume=vol, ens=2, ens_cents=6, human_t=0.008, legato=0.05, swell=0.6)


def celli(song: Song, name: str = "celli", stem: str = "str_lo", vol: int = 100, short: bool = False) -> Part:
    p = song.part(name, 42, stem=stem, volume=vol, pan=0.15, ens=2, ens_cents=6, ens_spread=0.3, human_t=0.005)
    if short:
        p.start_offset(3200).release(-2400)
    return p


def basses(song: Song, name: str = "basses", stem: str = "str_lo", vol: int = 100, short: bool = False) -> Part:
    p = song.part(name, 43, stem=stem, volume=vol, pan=-0.1, ens=1, human_t=0.005)
    if short:
        p.start_offset(1500).release(-2400)
    return p


def horns(song: Song, name: str = "horns", stem: str = "horns", vol: int = 100, pan: float = -0.15) -> Part:
    return song.part(name, 60, stem=stem, volume=vol, pan=pan, ens=2, ens_cents=6, ens_spread=0.35,
                     human_t=0.01, legato=0.04, swell=1.0)


def trumpets(song: Song, name: str = "tpts", stem: str = "brass", vol: int = 96, pan: float = 0.2) -> Part:
    return song.part(name, 56, stem=stem, volume=vol, pan=pan, ens=2, ens_cents=7, ens_spread=0.3,
                     human_t=0.008, legato=0.02, swell=0.8)


def brass_section(song: Song, name: str = "brass", stem: str = "brass", vol: int = 100, wide: bool = True) -> Part:
    return song.part(name, 61, bank=8 if wide else 0, stem=stem, volume=vol, ens=2 if not wide else 1,
                     human_t=0.008, legato=0.03, swell=0.8)


def trombones(song: Song, name: str = "tbns", stem: str = "low_brass", vol: int = 100, pan: float = 0.25) -> Part:
    return song.part(name, 57, stem=stem, volume=vol, pan=pan, ens=2, ens_cents=6, ens_spread=0.3,
                     human_t=0.007, legato=0.02, swell=0.8)


def tuba(song: Song, name: str = "tuba", stem: str = "low_brass", vol: int = 100) -> Part:
    return song.part(name, 58, stem=stem, volume=vol, pan=0.0, ens=1, human_t=0.006)


def choir(song: Song, name: str = "choir", stem: str = "choir", vol: int = 100, ohh: bool = False) -> Part:
    return song.part(name, 53 if ohh else 52, stem=stem, volume=vol, ens=2, ens_cents=8, ens_spread=0.5,
                     human_t=0.01, legato=0.08, swell=0.7)


def taiko(song: Song, name: str = "taiko", stem: str = "drums", vol: int = 110, pan: float = 0.0) -> Part:
    return song.part(name, 116, stem=stem, volume=vol, pan=pan, human_t=0.003, human_v=6)


def concert_bd(song: Song, name: str = "bigdrum", stem: str = "drums", vol: int = 115) -> Part:
    return song.part(name, 116, bank=8, stem=stem, volume=vol, human_t=0.002, human_v=4)


def timpani(song: Song, name: str = "timp", stem: str = "timp", vol: int = 115) -> Part:
    return song.part(name, 47, stem=stem, volume=vol, human_t=0.003, human_v=5)


def orch_kit(song: Song, name: str = "kit", stem: str = "snare", vol: int = 100) -> Part:
    """Orchestra kit on the drum channel: 36 bass drum, 38/40 snare, 57 crash, 55 splash."""
    return song.part(name, 48, drum=True, stem=stem, volume=vol, human_t=0.003, human_v=6)


def piano(song: Song, name: str = "piano", stem: str = "keys", vol: int = 90) -> Part:
    return song.part(name, 0, stem=stem, volume=vol, human_t=0.006, human_v=4)


def bells(song: Song, name: str = "bells", stem: str = "keys", vol: int = 80) -> Part:
    return song.part(name, 14, stem=stem, volume=vol, human_t=0.004)


def synth_brass(song: Song, name: str = "sbrass", stem: str = "brass", vol: int = 90) -> Part:
    return song.part(name, 62, stem=stem, volume=vol, ens=2, ens_cents=10, ens_spread=0.6, human_t=0.004)


# ----------------------------------------------------------------------------
# Harmony helpers
# ----------------------------------------------------------------------------

def sym_at(sym: str, frac: float) -> str:
    """Active chord of a bar entry like ``'Asus4>A'`` (split evenly) at ``frac`` (0..1) of the bar."""
    if ">" not in sym:
        return sym
    parts = sym.split(">")
    return parts[min(len(parts) - 1, int(frac * len(parts)))]


def split_bar(sym: str) -> list[tuple[float, str]]:
    """``'Asus4>A'`` -> ``[(0.0, 'Asus4'), (0.5, 'A')]`` (fractions of the bar)."""
    parts = sym.split(">")
    return [(i / len(parts), p) for i, p in enumerate(parts)]


def ctone(sym: str, tok, ref: int) -> int:
    """Chord-relative pitch: ``tok`` is an int (semitones above the root nearest
    ``ref``) or one of 'R','3','5','7','8','10','12','-5','-8','b2','9'."""
    r = root(sym, ref)
    _, iv = chord(sym)
    third = next((i for i in iv if i in (3, 4)), next((i for i in iv if i in (2, 5)), 7))
    fifth = next((i for i in iv if i in (6, 7, 8)), 7)
    table = {"R": 0, "3": third, "5": fifth, "7": 10 if 10 in iv else 11 if 11 in iv else 10, "8": 12,
             "10": 12 + third, "12": 12 + fifth, "15": 24, "-5": fifth - 12, "-8": -12, "-4": third - 12,
             "b2": 1, "9": 14, "2": 2, "4": 5, "6": 8 if third == 3 else 9}
    if isinstance(tok, int):
        return r + tok
    return r + table[tok]


def pattern_line(part: Part, song: Song, bar0: int, chords: list[str], cells: list, ref: int, vel: int = 96,
                 steps: int = 16, accents: str | None = None, dur: float = 0.85, vel_curve=None) -> None:
    """Chord-following step pattern, one chord per bar.

    ``cells`` holds one token per step (see :func:`ctone`), ``None`` for a rest.
    ``accents`` is a per-step string: 'X' accent, 'x' normal, 'o' ghost.
    """
    bpb = song.beats_per_bar
    step = bpb / steps
    lv = {"X": 1.0, "x": 0.8, "o": 0.6}
    for k, sym in enumerate(chords):
        bar = bar0 + k
        vv = vel if vel_curve is None else int(vel_curve(k))
        for i in range(steps):
            tok = cells[i % len(cells)]
            if tok is None:
                continue
            a = lv[accents[i % len(accents)]] if accents else 0.85
            part.note(bar * bpb + i * step, step * dur, ctone(sym_at(sym, i / steps), tok, ref), int(vv * a))


def pad_chords(part: Part, song: Song, bar0: int, chords: list[str], center: int, count: int = 4, vel: int = 80,
               beats: float | None = None, prev: list[int] | None = None, bass_part: Part | None = None,
               bass_ref: int = 38, bass_vel: int | None = None) -> list[int]:
    """Sustained voice-led chords, one per bar (or per ``beats``)."""
    bpb = song.beats_per_bar
    length = beats or bpb
    b = bar0 * bpb
    for entry in chords:
        for frac, sym in split_bar(entry):
            seg = length / len(entry.split(">"))
            v = voicing(sym, center, count, prev)
            part.chord(b + frac * length, seg, v, vel)
            if bass_part is not None:
                bass_part.note(b + frac * length, seg, root(sym, bass_ref), bass_vel or vel)
            prev = v
        b += length
    return prev


def expr_curve(part: Part, song: Song, points: list[tuple[float, int]]) -> None:
    """CC11 expression through (bar, value) points, linear between them."""
    for (b0, v0), (b1, v1) in zip(points, points[1:]):
        part.ramp(song.bar(b0), song.bar(b1), v0, v1)


def humanize_rng(song: Song, tag: str) -> np.random.Generator:
    return np.random.default_rng(zlib.crc32(f"{song.name}/{tag}/{song.seed}".encode()))


# ----------------------------------------------------------------------------
# Numpy layers
# ----------------------------------------------------------------------------

def clip_pulse_line(song: Song, stem: str, bar0: int, chords: list[str], cells: list, ref: int, vel: float = 0.8,
                    steps: int = 16, gate: float = 0.7, bright: float = 0.8, decay: float = 0.12,
                    accents: str | None = None, vel_curve=None) -> None:
    """Synth-pulse ostinato following the chords (numpy voice, cached per note)."""
    bpb = song.beats_per_bar
    step = bpb / steps
    lv = {"X": 1.0, "x": 0.8, "o": 0.55}
    dur = song.sec(step) * gate
    for k, sym in enumerate(chords):
        vv = vel if vel_curve is None else vel_curve(k)
        for i in range(steps):
            tok = cells[i % len(cells)]
            if tok is None:
                continue
            a = lv[accents[i % len(accents)]] if accents else 1.0
            p = ctone(sym_at(sym, i / steps), tok, ref)
            song.clip(stem, (bar0 + k) * bpb + i * step,
                      synth.pulse_note(p, round(dur, 4), round(float(vv * a), 3), bright, 0.08, decay))


def clip_bass_line(song: Song, stem: str, bar0: int, chords: list[str], cells: list, ref: int, vel: float = 0.9,
                   steps: int = 16, gate: float = 0.8, drive: float = 0.4, cutoff: float = 900.0) -> None:
    bpb = song.beats_per_bar
    step = bpb / steps
    for k, sym in enumerate(chords):
        for i in range(steps):
            tok = cells[i % len(cells)]
            if tok is None:
                continue
            p = ctone(sym_at(sym, i / steps), tok, ref)
            song.clip(stem, (bar0 + k) * bpb + i * step,
                      synth.bass_note(p, round(song.sec(step) * gate, 4), vel, drive, cutoff))


def clip_hats(song: Song, bar0: int, nbars: int, pattern: str, vel: float = 0.5, stem: str = "hats",
              pan_spread: float = 0.25, steps: int = 16) -> None:
    pat = pattern.replace("|", "").replace(" ", "")
    lv = {"X": 1.0, "x": 0.7, "o": 0.4, "O": 0.8}
    step = song.beats_per_bar / steps
    rng = np.random.default_rng(len(song.name) * 7 + bar0)
    for bar in range(bar0, bar0 + nbars):
        for i in range(steps):
            c = pat[i % len(pat)]
            if c == ".":
                continue
            h = synth.hat(open_=(c == "O"), vel=1.0, seed=1 + (i % 3))
            g = vel * lv[c] * (1 + rng.uniform(-0.1, 0.1))
            song.clip(stem, bar * song.beats_per_bar + i * step, synth.pan(h, pan_spread * (1 if i % 2 else -1)) * g)


def clip_ticks(song: Song, bar0: int, nbars: int, pattern: str, vel: float = 0.5, stem: str = "hats",
               hi: float = 91.0, lo: float = 84.0, steps: int = 8) -> None:
    pat = pattern.replace("|", "").replace(" ", "")
    step = song.beats_per_bar / steps
    for bar in range(bar0, bar0 + nbars):
        for i in range(steps):
            c = pat[i % len(pat)]
            if c == ".":
                continue
            p = hi if c == "X" else lo
            song.clip(stem, bar * song.beats_per_bar + i * step, synth.pan(synth.tick(p, 1.0), 0.15) * vel)


def boom_at(song: Song, beat: float, vel: float = 1.0, stem: str = "sub", duck: float = 1.0, **kw) -> None:
    song.clip(stem, beat, synth.boom(vel=1.0, **kw), gain=vel)
    if duck:
        song.duck(beat, duck)


def thumps(song: Song, beats: list[float], vel: float = 0.8, stem: str = "sub", duck: float = 0.8, **kw) -> None:
    th = synth.thump(1.0, **kw)
    for b in beats:
        song.clip(stem, b, th, gain=vel)
        if duck:
            song.duck(b, duck)


def riser_to(song: Song, end_beat: float, beats: float, vel: float = 0.5, stem: str = "fx", **kw) -> None:
    """Riser that ends exactly on ``end_beat``."""
    dur = song.sec(beats)
    song.clip(stem, end_beat - beats, synth.riser(dur, 1.0, **kw), gain=vel)


def swell_to(song: Song, end_beat: float, beats: float, vel: float = 0.5, stem: str = "cym") -> None:
    dur = song.sec(beats)
    song.clip(stem, end_beat - beats, synth.reverse_swell(dur, 1.0), gain=vel)


def pattern_beats(song: Song, bar0: int, nbars: int, pattern: str, steps: int = 16, chars: str = "X") -> list[float]:
    pat = pattern.replace("|", "").replace(" ", "")
    step = song.beats_per_bar / steps
    out = []
    for bar in range(bar0, bar0 + nbars):
        for i in range(steps):
            if pat[i % len(pat)] in chars:
                out.append(bar * song.beats_per_bar + i * step)
    return out


# ----------------------------------------------------------------------------
# Extra stems and instruments (added with the 10/10 tracks; the first eight
# tracks never create these stems, so their renders are unchanged)
# ----------------------------------------------------------------------------

EXTRA_STEMS = {
    "winds": dict(eq=[("hp2", 140), ("peak", 600, 1.0, -1.5), ("peak", 3000, 1.0, 1.0)], hall=0.42, room=0.06, width=1.05),
    "gtr": dict(eq=[("hp2", 85), ("peak", 350, 1.0, -2.5), ("peak", 1600, 1.2, 1.5), ("lp", 7500)], room=0.12, hall=0.08,
                width=1.25, duck=0.25),
    "kit": dict(eq=[("hp2", 32), ("peak", 60, 0.9, 1.5), ("peak", 450, 1.0, -3.0), ("peak", 4000, 1.0, 1.0)], room=0.25,
                hall=0.06, mono_below=150, drive=0.08),
    "perc": dict(eq=[("hp2", 120), ("peak", 2500, 1.0, 1.0)], room=0.25, hall=0.18, width=1.2),
    "harp": dict(eq=[("hp2", 90), ("peak", 2500, 1.0, 1.0)], hall=0.45, width=1.2),
    "lead": dict(eq=[("hp2", 120), ("peak", 400, 1.0, -2.0), ("hs", 7000, 0.7, -3.0)], hall=0.22, delay=0.22, width=1.1),
}


def setup_extra(song: Song, gains: dict[str, float] | None = None, **overrides) -> None:
    """Create the extra stems (call after :func:`setup_stems`); ``gains`` sets per-stem gain in dB."""
    gains = gains or {}
    for name, cfg in EXTRA_STEMS.items():
        c = dict(cfg)
        c.update(overrides.get(name, {}))
        song.stem(name, gain_db=gains.get(name, 0.0), **c)


def wind(song: Song, name: str, program: int, stem: str = "winds", vol: int = 92, pan: float = 0.0,
         ens: int = 1, legato: float = 0.04) -> Part:
    """Woodwinds and solo reeds: 68 oboe, 69 cor anglais, 70 bassoon, 71 clarinet, 72 piccolo, 73 flute, 111 shanai."""
    return song.part(name, program, stem=stem, volume=vol, pan=pan, ens=ens, ens_cents=5, human_t=0.008,
                     legato=legato, swell=0.6)


def harp(song: Song, name: str = "harp", stem: str = "harp", vol: int = 92, pan: float = -0.2) -> Part:
    return song.part(name, 46, stem=stem, volume=vol, pan=pan, human_t=0.004, human_v=4)


def mallets(song: Song, name: str, program: int = 8, stem: str = "keys", vol: int = 86, pan: float = 0.15) -> Part:
    """Tuned percussion: 8 celesta, 9 glockenspiel, 11 vibraphone, 12 marimba, 13 xylophone, 14 tubular bells."""
    return song.part(name, program, stem=stem, volume=vol, pan=pan, human_t=0.004, human_v=4)


def guitar(song: Song, name: str = "gtr", program: int = 30, stem: str = "gtr", vol: int = 96, pan: float = -0.3,
           ens: int = 2) -> Part:
    """Rock guitar (29 overdriven, 30 distortion); doubled and panned wide for a two-guitar wall."""
    return song.part(name, program, stem=stem, volume=vol, pan=pan, ens=ens, ens_cents=8, ens_spread=0.9,
                     ens_delay=0.018, human_t=0.004, human_v=5)


def e_bass(song: Song, name: str = "ebass", program: int = 34, stem: str = "bass", vol: int = 96) -> Part:
    """Electric bass (33 finger, 34 pick, 38/39 synth bass)."""
    return song.part(name, program, stem=stem, volume=vol, human_t=0.004, human_v=5)


def drum_kit(song: Song, name: str = "drumkit", program: int = 0, stem: str = "kit", vol: int = 100) -> Part:
    """A GM kit on the drum channel (0 standard, 8 room, 16 power, 24 electronic, 25 TR-808).
    Only one kit program per stem: every drum part of a stem shares MIDI channel 10."""
    return song.part(name, program, drum=True, stem=stem, volume=vol, human_t=0.003, human_v=6)


def synth_lead(song: Song, name: str = "slead", program: int = 81, stem: str = "lead", vol: int = 84,
               pan: float = 0.0) -> Part:
    """Synth lead (80 square, 81 saw, 87 bass+lead) or pads (89 warm, 91 choir, 95 sweep)."""
    return song.part(name, program, stem=stem, volume=vol, pan=pan, ens=2, ens_cents=9, ens_spread=0.5,
                     human_t=0.004, legato=0.03)


def solo_horn(song: Song, name: str = "solo_horn", stem: str = "horns", vol: int = 96, pan: float = -0.1) -> Part:
    return song.part(name, 60, stem=stem, volume=vol, pan=pan, ens=1, human_t=0.01, legato=0.05, swell=1.0)
