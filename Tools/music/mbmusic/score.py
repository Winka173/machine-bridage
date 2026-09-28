"""Score model: songs made of parts (MIDI instruments) and clips (numpy audio).

A :class:`Song` holds a tempo, a length in bars and a set of :class:`Part`
objects. Each part is one SoundFont preset playing notes; parts are grouped
into named stems that are rendered and mixed separately. Numpy synth audio is
added as clips placed on a beat.
"""

from __future__ import annotations

import io
import random
import re
from dataclasses import dataclass, field

import mido
import numpy as np

from . import SR
from .theory import n

TPB = 960  # MIDI ticks per beat


@dataclass
class Note:
    beat: float
    dur: float
    pitch: int
    vel: int


@dataclass
class Stem:
    """Mix settings for one stem (see :mod:`mbmusic.mix`)."""

    gain_db: float = 0.0
    eq: list = field(default_factory=list)  # [(kind, freq, q, gain_db), ...]
    hall: float = 0.0  # send level to the long hall reverb
    room: float = 0.0  # send level to the short room reverb
    duck: float = 0.0  # sidechain depth 0..1 from the song's duck triggers
    duck_release: float = 0.18
    width: float = 1.0  # stereo width multiplier for the side channel
    delay: float = 0.0  # ping-pong delay send
    drive: float = 0.0  # soft saturation amount 0..1
    mono_below: float = 0.0  # make the stem mono below this frequency (Hz)


class Part:
    """One instrument line rendered through FluidSynth."""

    def __init__(self, song: "Song", name: str, program: int, bank: int = 0, drum: bool = False,
                 stem: str = "main", volume: int = 100, pan: float = 0.0, ens: int = 1,
                 ens_cents: float = 7.0, ens_spread: float = 0.45, ens_delay: float = 0.012,
                 human_t: float = 0.006, human_v: int = 5, legato: float = 0.0, transpose: int = 0,
                 swell: float = 0.0):
        self.song = song
        self.name = name
        self.program = program
        self.bank = bank
        self.drum = drum
        self.stem = stem
        self.volume = volume
        self.pan = pan
        self.ens = ens
        self.ens_cents = ens_cents
        self.ens_spread = ens_spread
        self.ens_delay = ens_delay
        self.human_t = human_t
        self.human_v = human_v
        self.legato = legato
        self.transpose = transpose
        self.swell = swell  # 0..1 depth of the automatic per-note expression swell
        self.notes: list[Note] = []
        self.ccs: list[tuple[float, int, int]] = []

    # ----- note entry -------------------------------------------------
    def note(self, beat: float, dur: float, pitch, vel: int = 90) -> "Part":
        p = n(pitch) + self.transpose
        if beat < 0 and self.song.loop:  # pickups before the loop start wrap to the end
            beat += self.song.length_beats
        if 0 <= p <= 127 and dur > 0:
            self.notes.append(Note(float(beat), float(dur), p, int(max(1, min(127, vel)))))
        return self

    def chord(self, beat: float, dur: float, pitches, vel: int = 90, strum: float = 0.0) -> "Part":
        for i, p in enumerate(pitches):
            self.note(beat + i * strum, dur - i * strum, p, vel)
        return self

    def cc(self, beat: float, ctrl: int, val: int) -> "Part":
        self.ccs.append((float(beat), int(ctrl), int(max(0, min(127, val)))))
        return self

    # SoundFont generator offsets via NRPN (MSB 120, LSB = generator id).
    # FluidSynth scales the 14-bit data entry by 2 for time/cutoff generators.
    _NRPN_SCALE = {0: 1, 8: 2, 9: 1, 34: 2, 36: 2, 38: 2, 48: 1}

    def gen(self, gen: int, amount: float, beat: float = 0.0) -> "Part":
        v = int(round(8192 + amount / self._NRPN_SCALE.get(gen, 1)))
        v = max(0, min(16383, v))
        self.cc(beat, 99, 120).cc(beat, 98, gen).cc(beat, 38, v & 127).cc(beat, 6, v >> 7)
        return self

    def start_offset(self, samples: int) -> "Part":
        """Skip the first ``samples`` of every sample (sharper attacks)."""
        return self.gen(0, samples)

    def release(self, timecents: float) -> "Part":
        """Scale the release time by ``2 ** (timecents / 1200)``."""
        return self.gen(38, timecents)

    def cutoff(self, cents: float) -> "Part":
        """Offset the SoundFont low-pass cutoff (negative = darker)."""
        return self.gen(8, cents)

    def ramp(self, b0: float, b1: float, v0: int, v1: int, ctrl: int = 11, steps_per_beat: int = 8,
             curve: float = 1.0) -> "Part":
        """Continuous controller ramp (default CC11 expression) from ``b0`` to ``b1``."""
        steps = max(2, int((b1 - b0) * steps_per_beat))
        for i in range(steps + 1):
            u = (i / steps) ** curve
            self.cc(b0 + (b1 - b0) * i / steps, ctrl, round(v0 + (v1 - v0) * u))
        return self

    def mel(self, beat: float, text: str, vel: int = 90, gap: float = 0.0, shift: int = 0) -> float:
        """Enter a melody from text like ``"D4:3 A4:1 | Bb4:2 r:1 [D4 F4]:1"``.

        Each token is ``pitch:beats``; the duration carries over when omitted.
        ``r`` is a rest, ``[..]`` a chord, a trailing ``!`` accents the note
        and ``~`` marks a softer note. ``shift`` transposes by semitones.
        Returns the beat after the last token.
        """
        dur = 1.0
        b = beat
        for tok in re.findall(r"\[[^\]]*\](?::[\d.]+)?[!~]*|[^\s|]+", text):
            acc = 0
            while tok and tok[-1] in "!~":
                acc += 14 if tok[-1] == "!" else -16
                tok = tok[:-1]
            if ":" in tok and not tok.startswith("[") or (tok.startswith("[") and "]:" in tok):
                head, d = tok.rsplit(":", 1)
                dur = float(d)
            else:
                head = tok
            if head == "r":
                pass
            elif head.startswith("["):
                for p in head[1:-1].split():
                    self.note(b, dur - gap, n(p) + shift, vel + acc)
            else:
                self.note(b, dur - gap, n(head) + shift, vel + acc)
            b += dur
        return b

    def hits(self, bar0: int, nbars: int, pattern: str, pitch, vel: int = 100, steps: int = 16,
             dur: float | None = None, flam_vel: float = 0.6) -> "Part":
        """Step-sequencer entry, one character per step, repeated for ``nbars`` bars.

        ``X`` accent, ``x`` normal, ``o`` ghost, ``f`` flam, ``r`` two-hit roll,
        ``R`` three-hit roll, ``.`` rest. ``|`` is ignored (visual separator).
        """
        pat = pattern.replace("|", "").replace(" ", "")
        bpb = self.song.beats_per_bar
        step = bpb / steps
        d = dur if dur is not None else step * 0.9
        levels = {"X": 1.0, "x": 0.78, "o": 0.45, "f": 0.9, "r": 0.8, "R": 0.8}
        for bar in range(bar0, bar0 + nbars):
            for i in range(steps):
                c = pat[i % len(pat)]
                if c == ".":
                    continue
                b = bar * bpb + i * step
                v = int(vel * levels[c])
                if c == "f":
                    self.note(b - 0.035 * self.song.bpm / 60.0, d, pitch, int(v * flam_vel))
                    self.note(b, d, pitch, v)
                elif c == "r":
                    self.note(b, step / 2, pitch, int(v * 0.8))
                    self.note(b + step / 2, step / 2, pitch, v)
                elif c == "R":
                    for k in range(3):
                        self.note(b + k * step / 3, step / 3, pitch, int(v * (0.7 + 0.15 * k)))
                else:
                    self.note(b, d, pitch, v)
        return self

    def roll(self, b0: float, b1: float, pitch, v0: int, v1: int, rate: float = 8.0) -> "Part":
        """A roll (``rate`` hits per beat) crescendoing from ``v0`` to ``v1``."""
        k = int((b1 - b0) * rate)
        for i in range(k):
            u = i / max(1, k - 1)
            self.note(b0 + i / rate, 1.0 / rate, pitch, int(v0 + (v1 - v0) * u))
        return self


class Song:
    def __init__(self, name: str, bpm: float, bars: int, beats_per_bar: int = 4, loop: bool = True,
                 tail_beats: float = 16.0, seed: int = 1):
        self.name = name
        self.bpm = float(bpm)
        self.bars = bars
        self.beats_per_bar = beats_per_bar
        self.loop = loop
        self.tail_beats = tail_beats
        self.seed = seed
        self.parts: list[Part] = []
        self.stems: dict[str, Stem] = {}
        self.clips: list[tuple[str, float, np.ndarray]] = []
        self.duck_beats: list[tuple[float, float]] = []  # (beat, strength 0..1)
        self.master: dict = {}

    # ----- construction ----------------------------------------------
    def stem(self, name: str, **kw) -> Stem:
        s = Stem(**kw)
        self.stems[name] = s
        return s

    def part(self, name: str, program: int, **kw) -> Part:
        p = Part(self, name, program, **kw)
        if p.stem not in self.stems:
            self.stems[p.stem] = Stem()
        self.parts.append(p)
        return p

    def clip(self, stem: str, beat: float, audio: np.ndarray, gain: float = 1.0) -> None:
        if stem not in self.stems:
            self.stems[stem] = Stem()
        a = np.asarray(audio, dtype=np.float32)
        if a.ndim == 1:
            a = np.stack([a, a], axis=1)
        self.clips.append((stem, float(beat), a * gain))

    def duck(self, beat: float, strength: float = 1.0) -> None:
        self.duck_beats.append((float(beat), float(strength)))

    # ----- time --------------------------------------------------------
    @property
    def beat_sec(self) -> float:
        return 60.0 / self.bpm

    def sec(self, beat: float) -> float:
        return beat * 60.0 / self.bpm

    def bar(self, b: float) -> float:
        """Beat index of the start of bar ``b`` (0-based)."""
        return b * self.beats_per_bar

    @property
    def length_beats(self) -> float:
        return self.bars * self.beats_per_bar

    @property
    def loop_samples(self) -> int:
        return int(round(self.sec(self.length_beats) * SR))

    @property
    def total_samples(self) -> int:
        return int(round(self.sec(self.length_beats + self.tail_beats) * SR))

    # ----- MIDI --------------------------------------------------------
    def midi_for_stem(self, stem: str) -> bytes | None:
        parts = [p for p in self.parts if p.stem == stem and p.notes]
        if not parts:
            return None
        mid = mido.MidiFile(ticks_per_beat=TPB, type=1)
        tempo = mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.bpm), time=0)
        t0 = mido.MidiTrack()
        t0.append(tempo)
        end_tick = int(round((self.length_beats + self.tail_beats) * TPB))
        t0.append(mido.MetaMessage("end_of_track", time=end_tick))
        mid.tracks.append(t0)
        free = [c for c in range(16) if c != 9]
        for part in parts:
            copies = 1 if part.drum else max(1, part.ens)
            for k in range(copies):
                if part.drum:
                    ch = 9
                else:
                    if not free:
                        raise RuntimeError(f"stem {stem!r} of {self.name} needs more than 15 channels")
                    ch = free.pop(0)
                rng = random.Random(f"{self.name}/{part.name}/{k}/{self.seed}")
                mid.tracks.append(self._track(part, ch, k, copies, rng, end_tick))
        buf = io.BytesIO()
        mid.save(file=buf)
        return buf.getvalue()

    def _expression(self, part: Part, res: int = 8) -> list[tuple[float, int]]:
        """CC11 stream = the part's explicit CC11 curve x a swell on every long note.

        Long notes (>= 1.5 beats) start about 3 dB down, bloom to full level
        and relax about 2 dB at the end, which keeps sustained samples from
        sounding static. Overlapping notes take the louder envelope.
        """
        end = self.length_beats + self.tail_beats
        grid = np.arange(0, end, 1.0 / res)
        pts = sorted((b, v) for b, c, v in part.ccs if c == 11)
        if pts:
            base = np.interp(grid, [b for b, _ in pts], [v for _, v in pts])
        else:
            base = np.full(len(grid), 127.0)
        env = np.full(len(grid), -np.inf)
        for nt in part.notes:
            i0 = int(np.searchsorted(grid, nt.beat))
            i1 = int(np.searchsorted(grid, nt.beat + nt.dur))
            if i1 <= i0:
                continue
            if nt.dur >= 1.5:
                u = (grid[i0:i1] - nt.beat) / nt.dur
                g = np.where(u < 0.4, -3.0 * (1 - u / 0.4) ** 2,
                             np.where(u > 0.7, -2.0 * ((u - 0.7) / 0.3) ** 2, 0.0)) * part.swell
            else:
                g = np.zeros(i1 - i0)
            env[i0:i1] = np.maximum(env[i0:i1], g)
        env[~np.isfinite(env)] = 0.0
        val = np.clip(np.round(base * 10 ** (env / 40)), 0, 127).astype(int)
        out, last = [], -1
        for b, v in zip(grid.tolist(), val.tolist()):
            if v != last:
                out.append((b, v))
                last = v
        return out

    def _track(self, part: Part, ch: int, k: int, copies: int, rng: random.Random, end_tick: int):
        ev: list[tuple[int, int, mido.Message]] = []  # (tick, order, msg)
        if copies > 1:
            u = (k / (copies - 1)) * 2 - 1  # -1..1
        else:
            u = 0.0
        pan = max(-1.0, min(1.0, part.pan + u * part.ens_spread))
        cents = u * part.ens_cents
        delay_ticks = int(round(abs(u) * part.ens_delay / self.beat_sec * TPB))
        if not part.drum:
            ev.append((0, 0, mido.Message("control_change", channel=ch, control=0, value=part.bank)))
            ev.append((0, 0, mido.Message("control_change", channel=ch, control=32, value=0)))
        ev.append((0, 0, mido.Message("program_change", channel=ch, program=part.program)))
        vol = part.volume if copies == 1 else int(round(part.volume * 0.84))  # ~ -3 dB per copy (CC7 is squared)
        ev.append((0, 0, mido.Message("control_change", channel=ch, control=7, value=max(0, min(127, vol)))))
        ev.append((0, 0, mido.Message("control_change", channel=ch, control=10, value=int(round(64 + pan * 63)))))
        ev.append((0, 0, mido.Message("control_change", channel=ch, control=91, value=0)))
        ev.append((0, 0, mido.Message("control_change", channel=ch, control=93, value=0)))
        if cents:
            ev.append((0, 0, mido.Message("pitchwheel", channel=ch, pitch=int(round(cents / 200.0 * 8191)))))
        for b, c, v in part.ccs:
            if c == 11 and part.swell > 0:
                continue  # merged into the expression stream below
            ev.append((max(0, int(round(b * TPB)) + delay_ticks), 1, mido.Message("control_change", channel=ch, control=c, value=v)))
        if part.swell > 0:
            for b, v in self._expression(part):
                ev.append((max(0, int(round(b * TPB)) + delay_ticks), 1,
                           mido.Message("control_change", channel=ch, control=11, value=v)))
        elif not any(c == 11 and b <= 0 for b, c, _ in part.ccs):
            ev.append((0, 0, mido.Message("control_change", channel=ch, control=11, value=127)))
        # humanize and resolve same-pitch overlaps
        spb = self.beat_sec
        notes = []
        for nt in part.notes:
            jt = rng.gauss(0, part.human_t) if part.human_t else 0.0
            jt = max(-2.5 * part.human_t, min(2.5 * part.human_t, jt)) if part.human_t else 0.0
            on = nt.beat * TPB + jt / spb * TPB + delay_ticks
            off = (nt.beat + nt.dur + part.legato) * TPB + delay_ticks
            v = nt.vel + (rng.randint(-part.human_v, part.human_v) if part.human_v else 0)
            notes.append([max(0, int(round(on))), int(round(off)), nt.pitch, max(1, min(127, v))])
        notes.sort(key=lambda x: (x[2], x[0]))
        for i in range(len(notes) - 1):
            a, b = notes[i], notes[i + 1]
            if a[2] == b[2] and a[1] > b[0] - 1:
                a[1] = max(a[0] + 1, b[0] - 1)
        for on, off, p, v in notes:
            if on >= end_tick:
                continue
            off = min(off, end_tick - 1)
            ev.append((on, 3, mido.Message("note_on", channel=ch, note=p, velocity=v)))
            ev.append((max(on + 1, off), 2, mido.Message("note_off", channel=ch, note=p, velocity=0)))
        ev.sort(key=lambda e: (e[0], e[1]))
        tr = mido.MidiTrack()
        last = 0
        for t, _, m in ev:
            tr.append(m.copy(time=t - last))
            last = t
        tr.append(mido.MetaMessage("end_of_track", time=max(0, end_tick - last)))
        return tr
