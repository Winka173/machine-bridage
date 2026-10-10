"""naval: "Steel Tide" - sea battle, rolling 12/8 swell. G# minor, 88 BPM (dotted-quarter beat), 40 bars.

Every beat is split in three: patterns use 12 steps per bar and melodies use
thirds of a beat. Form (bars): A 0-7 wave arpeggios in the celli and harp,
foghorn low brass, ship's bell | B 8-15 the horn theme, a sea-shanty shape |
C 16-23 the swell: choir, tremolo, trumpet counter-line | D 24-35 climax:
the theme in trumpets and horns over 12/8 war drums | E 36-39 the sea calms
back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

T = 1 / 3  # one eighth note of the 12/8 bar, in beats

P1 = ["G#m", "E", "B", "F#"]
P2 = ["G#m", "C#m", "D#sus4>D#", "D#"]
P3 = ["E", "B", "C#m", "D#"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P3  # C 16-23
          + P1 + P2 + P1  # D 24-35
          + P3)  # E 36-39


def _t(n: int) -> str:
    return f"{n * T:.6f}"


THEME = (f"D#4:{_t(2)} G#4:{_t(1)} G#4:1 A#4:{_t(2)} B4:{_t(1)} C#5:{_t(2)} B4:{_t(1)} |"
         f" B4:2 G#4:{_t(2)} E4:{_t(1)} G#4:1 |"
         f" F#4:1 B4:{_t(2)} C#5:{_t(1)} D#5:1 C#5:{_t(2)} B4:{_t(1)} | A#4:3 r:1 |"
         f" D#4:{_t(2)} G#4:{_t(1)} G#4:1 A#4:{_t(2)} B4:{_t(1)} C#5:{_t(2)} B4:{_t(1)} |"
         f" E5:{_t(5)} D#5:{_t(1)} C#5:1 G#4:1 | G#4:1 A#4:1 G4:1 A#4:1 | D#5:3 r:1")
COUNTER = "G#4:2 B4:2 | F#4:2 D#5:2 | E5:2 C#5:2 | D#5:4"
WAVE = ["R", "5", "8", "10", "8", "5", "R", "5", "8", "10", "12", "10"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("naval", bpm=88, bars=40, seed=121, tail_beats=16)
    s.master = {"hall_rt": 3.0, "hall_gain": 1.05}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 2.0, "str_hi": -1.0, "horns": 4.0, "brass": -1.0,
                            "low_brass": 0.0, "choir": -3.0, "drums": -4.0, "snare": -4.0, "timp": -1.0,
                            "cym": -9.0, "synth": -13.0, "sub": -10.0, "fx": -9.0, "keys": -1.0,
                            "drone": -12.0})
    c.setup_extra(s, gains={"harp": 1.0})
    B = s.bar
    bpb = s.beats_per_bar

    # --- waves: celli arpeggios, harp, violas -------------------------------------------------------
    vc = c.celli(s, "celli", vol=102)
    c.pattern_line(vc, s, 0, ch(0, 40), WAVE, ref=44, steps=12, vel=86, accents="XxxxxxXxxxxx", dur=1.3,
                   vel_curve=lambda k: 80 if k < 8 else 90 if k < 24 else 100 if k < 36 else 84)
    c.expr_curve(vc, s, [(0, 96), (24, 120), (36, 100), (40, 96)])
    hp = c.harp(s, vol=96)
    for a, b in ((0, 8), (16, 24), (36, 40)):
        c.pattern_line(hp, s, a, ch(a, b), ["8", "10", "12", "15", "12", "10"], ref=56, steps=12, vel=72,
                       dur=2.0)
    va = c.spiccato(s, "violas", vol=96, pan=-0.15)
    c.pattern_line(va, s, 24, ch(24, 36), ["8", "5", "3", "5", "8", "10"], ref=56, steps=12, vel=92,
                   accents="XxxXxx", dur=0.8)
    cb = c.basses(s, "basses", vol=100)
    for k in range(40):
        for frac, sym in c.split_bar(CHORDS[k]):
            cb.note(B(k) + frac * bpb, bpb / len(CHORDS[k].split(">")) - 0.1, c.ctone(sym, "R", 32),
                    74 if k < 8 or k >= 36 else 88)

    # --- foghorn and the ship's bell -----------------------------------------------------------------------
    tu = c.tuba(s, vol=104)
    tb = c.trombones(s, vol=100)
    for bar in (0, 4, 36):
        r = c.ctone(at(bar), "R", 32)
        tu.note(B(bar), 7.5, r, 92)
        tb.chord(B(bar), 7.5, [r + 12, r + 19], 80)
    tb.ramp(B(0), B(2), 60, 112)
    tb.ramp(B(2), B(8), 112, 70)
    tb.cc(B(16) - 0.05, 11, 110)
    tb.ramp(B(36), B(37), 70, 112)
    tb.ramp(B(37), B(40), 112, 60)
    bell = c.mallets(s, "ship_bell", 14, vol=86, pan=0.25)
    for bar in (0, 2, 4, 6, 36, 38):
        bell.note(B(bar), 3, 80, 82)
        bell.note(B(bar) + 1, 3, 80, 72)
    s.clip("drone", B(36), synth.drone(32, s.sec(B(12)), 0.11, bright=0.3))

    # --- the theme ------------------------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    hn.mel(B(8), THEME, vel=94)
    hn.mel(B(24), THEME, vel=106)
    hn.mel(B(32), THEME[:THEME.index("r:1") + 3], vel=106)
    c.expr_curve(hn, s, [(8, 112), (16, 104), (24, 126), (36, 126)])
    tp = c.trumpets(s, vol=100)
    tp.mel(B(16), COUNTER, vel=90)
    tp.mel(B(20), COUNTER, vel=98)
    tp.mel(B(24), THEME, vel=102, shift=12)
    tp.mel(B(32), THEME[:THEME.index("r:1") + 3], vel=104, shift=12)
    tb.mel(B(16), COUNTER, vel=86, shift=-12)
    tb.mel(B(20), COUNTER, vel=92, shift=-12)
    for k in range(24, 36):
        sym = at(k, 0.75)
        tb.chord(B(k), 1.9, [c.ctone(sym, "R", 44), c.ctone(sym, "5", 44)], 96)
        tb.chord(B(k) + 2, 1.9, [c.ctone(sym, "R", 44), c.ctone(sym, "5", 44)], 90)
        tu.note(B(k), 3.8, c.ctone(sym, "R", 32), 94)
    br = c.brass_section(s, vol=96)
    c.pad_chords(br, s, 24, ch(24, 36), center=62, count=4, vel=86)

    # --- swell: choir and tremolo ------------------------------------------------------------------------------
    cho = c.choir(s, vol=100, ohh=True)
    c.pad_chords(cho, s, 8, ch(8, 16), center=60, count=3, vel=64)
    c.pad_chords(cho, s, 16, ch(16, 36), center=63, count=3, vel=84)
    c.expr_curve(cho, s, [(8, 80), (16, 100), (23.9, 120), (24, 108), (36, 108)])
    tr = c.tremolo(s, vol=96)
    c.pad_chords(tr, s, 16, ch(16, 24), center=70, count=3, vel=80)
    c.expr_curve(tr, s, [(16, 70), (19.9, 100), (20, 80), (23.9, 124), (24, 70)])

    # --- 12/8 drums -------------------------------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=116)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=100, pan=0.3)
    kit = c.orch_kit(s, vol=100)
    tm = c.timpani(s, vol=118)
    for bar in range(8, 16):
        tlo.hits(bar, 1, "X.....x.....", 40, vel=92, steps=12)
        kit.hits(bar, 1, "...x.....x.x", 38, vel=70, steps=12)
    for bar in range(16, 24):
        last = bar % 4 == 3
        tlo.hits(bar, 1, "X..x..x..x.." if not last else "X..x..x.xxxx", 40, vel=98, steps=12)
        kit.hits(bar, 1, "...x.x...xxx", 38, vel=80, steps=12)
    for bar in range(24, 36):
        last = bar % 4 == 3
        bd.hits(bar, 1, "X.....X.....", 36, vel=112, steps=12)
        tlo.hits(bar, 1, "X..x.xX..x.x" if not last else "X..x.xX.xxxx", 40, vel=110, steps=12)
        thi.hits(bar, 1, "..x..x..x.xx", 47, vel=92, steps=12)
        kit.hits(bar, 1, "...X.x...X.x" if not last else "...X.x..xXXX", 38, vel=96, steps=12)
        tm.note(B(bar), 0.9, c.ctone(at(bar), "R", 44), 100)
        tm.note(B(bar) + 2, 0.9, c.ctone(at(bar, 0.6), "R", 44), 94)
    tm.roll(B(7), B(8), 44, 30, 96, rate=6)
    tm.roll(B(23), B(24), 44, 40, 118, rate=6)
    kit.roll(B(23) + 2, B(24), 38, 40, 110, rate=6)
    for bar in (8, 24, 32):
        kit.note(B(bar), 3, 57, 110)
    for bb in c.pattern_beats(s, 24, 12, "X.....X.....", steps=12):
        s.duck(bb, 0.7)
    for bar, v in ((0, 0.7), (8, 0.8), (16, 0.8), (24, 1.15), (32, 0.9), (36, 0.6)):
        c.boom_at(s, B(bar), vel=v, f0=60.0, f1=28.0)
    for bar in (0, 16, 36):  # the swell of the sea
        c.swell_to(s, B(bar + 4), 8, vel=0.35)
    c.riser_to(s, B(24), 8, vel=0.4, f0=150.0, f1=5000.0)
    return s
