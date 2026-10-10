"""battle_7: "Frozen Front" - arctic battle, vast and cold. Eb minor, 94 BPM, 44 bars.

Form (bars): A 0-7 high tremolo, glockenspiel frost, wind, a lone horn call |
B 8-15 low-brass ostinato, marcato string 8ths, the horn theme | C 16-23 choir
and tubular bells, lighter | D 24-35 climax: horns and trumpets, full drums,
timpani | E 36-43 the ice settles, then rebuilds into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Ebm", "Cb", "Gb", "Db"]
P2 = ["Ebm", "Cb", "Abm", "Bb"]
P3 = ["Cb", "Db", "Ebm", "Ebm"]
P4 = ["Abm", "Cb", "Bbsus4>Bb", "Bb"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2 + P1  # D 24-35
          + P3 + P4)  # E 36-43

THEME = ("Eb4:3 Bb4:1 | Gb4:2 Eb4:1 F4:1 | Gb4:1.5 Ab4:0.5 Bb4:2 | Ab4:3 F4:1 |"
         " Eb4:3 Bb4:1 | Cb5:2 Bb4:1 Gb4:1 | Ab4:1.5 Cb5:0.5 Eb5:2 | D5:3 r:1")
CALL = "Bb3:1.5 Eb4:0.5 F4:2 | Gb4:4 | F4:1.5 Db4:0.5 Ab3:2 | Ab3:4"
CHORALE = "Gb4:4 | F4:4 | Gb4:2 Bb4:2 | Bb4:4 | Cb5:4 | Eb5:2 Cb5:2 | Bb4:4 | D5:4"
LOW = ["R", None, None, None, None, None, "R", "R", "R", None, None, None, "-5", None, None, None]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("battle_7", bpm=94, bars=44, seed=101, tail_beats=16)
    s.master = {"hall_rt": 3.4, "hall_gain": 1.1}
    c.setup_stems(s, gains={"ost": 1.0, "str_lo": 1.0, "str_hi": -1.0, "horns": 4.0, "brass": -2.0,
                            "low_brass": 0.0, "choir": -2.0, "drums": -4.0, "snare": -6.0, "timp": 0.0,
                            "cym": -9.0, "synth": -13.0, "sub": -10.0, "fx": -8.0, "keys": 0.0,
                            "drone": -11.0})
    B = s.bar
    bpb = s.beats_per_bar
    full = [(8, 16), (24, 36)]

    # --- high tremolo and frost ------------------------------------------------------------------
    tr = c.tremolo(s, vol=94)
    c.pad_chords(tr, s, 0, ch(0, 8), center=79, count=2, vel=70)
    c.pad_chords(tr, s, 36, ch(36, 44), center=79, count=2, vel=72)
    c.expr_curve(tr, s, [(0, 76), (8, 90), (36, 70), (44, 76)])
    gl = c.mallets(s, "glock", 9, vol=78, pan=0.3)
    for a, b in ((0, 8), (16, 24), (36, 44)):
        c.pattern_line(gl, s, a, ch(a, b), ["8", "10", "12", "10", "8", "5"], ref=86, steps=12, vel=60,
                       accents="Xxxxxo", dur=1.5)
    cel = c.mallets(s, "celesta", 8, vol=80, pan=-0.25)
    c.pattern_line(cel, s, 0, ch(0, 8), ["8", None, "12", None, "10", None, None, None], ref=74, steps=8, vel=66,
                   dur=2.0)

    # --- wind and drone -------------------------------------------------------------------------------
    for bar in (0, 4, 36, 40):
        c.riser_to(s, B(bar + 4), 16, vel=0.22, f0=180.0, f1=1400.0, tone=0.0, seed=bar + 3)
    s.clip("drone", B(36), synth.drone(39, s.sec(B(16)), 0.12, bright=0.25))

    # --- horn call and theme ---------------------------------------------------------------------------
    sh = c.solo_horn(s, vol=98)
    sh.mel(B(4), CALL, vel=84)
    sh.mel(B(40), "Eb4:3 Cb4:1 | Gb4:4 | F4:2 Eb4:2 | D4:4", vel=78)
    hn = c.horns(s, vol=106)
    hn.mel(B(8), THEME, vel=94)
    hn.mel(B(16), CHORALE, vel=78, shift=-12)
    hn.mel(B(24), THEME, vel=104)
    hn.mel(B(32), THEME[:THEME.index("| Eb4:3", 5)], vel=108)
    c.expr_curve(hn, s, [(8, 112), (16, 96), (24, 124), (36, 124)])
    tp = c.trumpets(s, vol=100)
    tp.mel(B(28), THEME[THEME.index("Eb4:3", 5):], vel=104, shift=12)
    tp.mel(B(32), THEME[:THEME.index("| Eb4:3", 5)], vel=106, shift=12)

    # --- low brass ostinato and strings ---------------------------------------------------------------
    tb = c.trombones(s, vol=104)
    tu = c.tuba(s, vol=102)
    for a, b in full:
        c.pattern_line(tb, s, a, ch(a, b), LOW, ref=51, vel=102, dur=2.4)
        c.pattern_line(tu, s, a, ch(a, b), LOW, ref=39, vel=100, dur=2.4)
    vc = c.celli(s, "celli", short=True, vol=102)
    cb = c.basses(s, "basses", short=True, vol=100)
    for a, b in full:
        c.pattern_line(vc, s, a, ch(a, b), LOW, ref=51, vel=100, dur=2.0)
        c.pattern_line(cb, s, a, ch(a, b), LOW, ref=39, vel=100, dur=2.0)
    mar = c.spiccato(s, "marcato", vol=100)
    for a, b in full:
        c.pattern_line(mar, s, a, ch(a, b), ["5", "R", "5", "8", "5", "R", "5", "10"], ref=63, steps=8,
                       accents="XxxxXxxx", vel=98, dur=0.8)
    pad = c.strings(s, "pad", slow=True, vol=96)
    c.pad_chords(pad, s, 16, ch(16, 24), center=63, count=4, vel=78)
    c.pad_chords(pad, s, 24, ch(24, 36), center=67, count=4, vel=86)
    lo = c.basses(s, "basses_sus", vol=96)
    for k in list(range(0, 8)) + list(range(16, 24)) + list(range(36, 44)):
        lo.note(B(k), bpb - 0.1, c.ctone(at(k), "R", 39), 74)

    # --- choir and bells -----------------------------------------------------------------------------------
    cho = c.choir(s, vol=104)
    c.pad_chords(cho, s, 16, ch(16, 24), center=63, count=3, vel=80)
    c.pad_chords(cho, s, 24, ch(24, 36), center=65, count=3, vel=90)
    c.expr_curve(cho, s, [(16, 90), (23.9, 116), (24, 104), (35.9, 120), (36, 80)])
    bells = c.mallets(s, "tubular", 14, vol=88, pan=-0.1)
    for k in range(16, 24, 2):
        bells.note(B(k), 3, c.ctone(at(k), "R", 75), 84)
    for k in (24, 28, 32):
        bells.chord(B(k), 3, [c.ctone(at(k), "R", 63), c.ctone(at(k), "R", 75)], 90)

    # --- drums ------------------------------------------------------------------------------------------------
    tm = c.timpani(s, vol=120)
    bd = c.concert_bd(s, vol=118)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=102, pan=0.3)
    kit = c.orch_kit(s, vol=100)
    for a, b in full:
        big = a == 24
        for bar in range(a, b):
            last = bar % 4 == 3
            bd.hits(bar, 1, "X.....X.X.......", 36, vel=110 if big else 100)
            tlo.hits(bar, 1, "X.....X.X...x..." if not last else "X.....X.X.x.xRRR", 40, vel=108)
            if big:
                thi.hits(bar, 1, "..x...x...x...xx", 47, vel=92)
                kit.hits(bar, 1, "....X.......X...", 38, vel=96)
            tm.note(B(bar), 1.4, c.ctone(at(bar), "R", 39), 104 if big else 96)
            tm.note(B(bar) + 1.5, 0.9, c.ctone(at(bar), "R", 39), 92)
    for bar in range(16, 24):
        tlo.hits(bar, 1, "X...............", 40, vel=86)
    tm.roll(B(7), B(8), 39, 30, 104, rate=8)
    tm.roll(B(23), B(24), 46, 40, 118, rate=8)
    tm.roll(B(43), B(44), 39, 20, 80, rate=6)
    kit.roll(B(23) + 2, B(24), 38, 40, 110, rate=8)
    for bar in (8, 24, 32):
        kit.note(B(bar), 3, 57, 112)
    for bb in c.pattern_beats(s, 8, 8, "X.....X.X.......") + c.pattern_beats(s, 24, 12, "X.....X.X......."):
        s.duck(bb, 0.7)
    for bar, v in ((0, 0.7), (8, 1.0), (16, 0.8), (24, 1.2), (32, 1.0), (36, 0.7)):
        c.boom_at(s, B(bar), vel=v, f0=62.0, f1=28.0)
    c.swell_to(s, B(24), 4, vel=0.6)
    c.swell_to(s, B(8), 2, vel=0.45)
    return s
