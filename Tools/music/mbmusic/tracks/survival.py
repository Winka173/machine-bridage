"""survival: "Last Stand" - Survival and Endless, waves that never stop. E Dorian, 104 BPM, 48 bars.

Built in layers like the waves it plays under: every eight bars something
joins, and the hopeful Dorian A major keeps the grit from turning grim.
Form (bars): A 0-7 piano ostinato, clock ticks, synth pulse | B 8-15 string
8ths, the horn theme | C 16-23 wave two: drums and brass join | D 24-31 the
lift: choir and horns over the borrowed C and D | E 32-43 wave three, the
climax | F 44-47 the ranks thin, back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Em", "A", "Em", "A"]
P2 = ["G", "D", "A", "Bm"]
P3 = ["C", "D", "Em", "Em"]
P4 = ["G", "A", "Bsus4>B", "B"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P1 + P2  # C 16-23
          + P3 + P4  # D 24-31
          + P1 + P2 + P3  # E 32-43
          + P4)  # F 44-47

THEME = ("E4:1.5 F#4:0.5 G4:1 B4:1 | C#5:2 A4:2 | G4:1 F#4:1 E4:1 B3:1 | C#4:4 |"
         " D5:1.5 B4:0.5 G4:2 | F#4:1.5 A4:0.5 D5:2 | E5:1.5 C#5:0.5 A4:2 | B4:3 F#4:1")
LIFT = "E5:2 G5:2 | F#5:2 A5:2 | G5:3 E5:1 | B4:4 | D5:2 B4:2 | C#5:2 E5:2 | E5:2 D#5:2 | D#5:4"
PIANO = ["R", "5", "8", "5", "9", "5", "8", "5"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("survival", bpm=104, bars=48, seed=211, tail_beats=16)
    s.master = {"hall_rt": 2.6}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 0.0, "str_hi": -2.0, "horns": 3.0, "brass": -1.0,
                            "low_brass": -1.0, "choir": -3.0, "drums": -4.0, "snare": -3.0, "timp": -2.0,
                            "cym": -9.0, "synth": -11.0, "bass": -15.0, "sub": -11.0, "fx": -10.0,
                            "keys": 8.0, "hats": -12.0, "drone": -12.0})
    B = s.bar

    # --- layer 1: piano, ticks, pulse (all through) -----------------------------------------------------
    pno = c.piano(s, vol=94)
    c.pattern_line(pno, s, 0, ch(0, 48), PIANO, ref=64, steps=8, vel=80, accents="XxxxXxxx", dur=1.2,
                   vel_curve=lambda k: 88 if k < 8 else 76 if k < 32 else 70 if k < 44 else 86)
    c.clip_ticks(s, 0, 48, "X.x.x.x.", vel=1.6)
    c.clip_pulse_line(s, "synth", 0, ch(0, 48), ["R", None, "8", "R"], ref=52, vel=0.5, gate=0.45, bright=0.4,
                      accents="Xoxo", vel_curve=lambda k: 0.42 + (0.1 if 16 <= k < 44 else 0.0))
    s.clip("drone", B(44), synth.drone(28, s.sec(B(12)), 0.11, bright=0.3))

    # --- layer 2: strings and the theme ----------------------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=102)
    cb = c.basses(s, "basses", short=True, vol=100)
    for a, b, v in ((8, 16, 88), (16, 24, 96), (24, 44, 102)):
        c.pattern_line(vc, s, a, ch(a, b), ["R", "R", "5", "R"], ref=40, steps=8, vel=v, accents="XxxxXxxx",
                       dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), ["R"], ref=28, steps=8, vel=v, accents="XxxxXxxx", dur=0.8)
    vn = c.spiccato(s, "violins", vol=96, pan=0.15)
    c.pattern_line(vn, s, 16, ch(16, 44), ["8", "5", "10", "5"], ref=64, steps=8, vel=86, accents="Xxxx",
                   dur=0.7)
    pad = c.strings(s, "pad", slow=True, vol=96)
    c.pad_chords(pad, s, 0, ch(0, 8), center=60, count=4, vel=74)
    c.pad_chords(pad, s, 44, ch(44, 48), center=62, count=4, vel=78)
    lo = c.celli(s, "celli_sus", vol=98)
    for k in list(range(0, 8)) + list(range(44, 48)):
        for frac, sym in c.split_bar(CHORDS[k]):
            lo.note(B(k) + frac * 4, 4 / len(CHORDS[k].split(">")) - 0.1, c.ctone(sym, "R", 40), 80)
    sp = c.spiccato(s, "spic", vol=98)
    c.pattern_line(sp, s, 32, ch(32, 44), ["R", "R", "5", "R"], ref=52, vel=92, accents="XxxxXxxxXxxxXxxx",
                   dur=0.7)
    hn = c.horns(s, vol=106)
    hn.mel(B(8), THEME, vel=92)
    hn.mel(B(16), THEME, vel=100)
    hn.mel(B(24), LIFT, vel=104, shift=-12)
    hn.mel(B(32), THEME, vel=108)
    c.expr_curve(hn, s, [(8, 110), (24, 118), (32, 126), (44, 126)])
    tp = c.trumpets(s, vol=100)
    tp.mel(B(32), THEME, vel=104, shift=12)
    tp.mel(B(40), LIFT[:LIFT.index("| D5:2 B4")], vel=106)
    hn.mel(B(40), LIFT[:LIFT.index("| D5:2 B4")], vel=108, shift=-12)

    # --- layer 3: brass and drums ---------------------------------------------------------------------------------
    br = c.brass_section(s, vol=98)
    for k in list(range(16, 24)) + list(range(32, 44)):
        br.chord(B(k) + 1.5, 0.3, c.voicing(at(k), 60, 4), 98)
        br.chord(B(k) + 3.5, 0.3, c.voicing(at(k), 60, 4), 94)
    c.pad_chords(br, s, 24, ch(24, 32), center=60, count=4, vel=84)
    tb = c.trombones(s, vol=100)
    tu = c.tuba(s, vol=98)
    for k in range(24, 44):
        tb.chord(B(k), 3.6, [c.ctone(at(k), "R", 40), c.ctone(at(k), "5", 40)], 88)
        tu.note(B(k), 3.6, c.ctone(at(k), "R", 28), 90)
    kit = c.orch_kit(s, vol=102)
    bd = c.concert_bd(s, vol=116)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=102, pan=0.3)
    tm = c.timpani(s, vol=116)
    for bar in range(0, 16):
        tlo.hits(bar, 1, "X.......X.......", 40, vel=84 if bar < 8 else 90)
    for bar in range(16, 44):
        last = bar % 4 == 3
        big = bar >= 32
        bd.hits(bar, 1, "X.......X.......", 36, vel=108 if big else 100)
        tlo.hits(bar, 1, "X..x..x.X.......", 40, vel=106 if big else 98)
        kit.hits(bar, 1, "X.xxX.x.X.xxX.x." if not last else "X.xxX.x.XrXrRRRR", 38, vel=92 if big else 84)
        if big or 24 <= bar < 32:
            thi.hits(bar, 1, "..x...x...x...xx", 47, vel=92)
    for bar in range(44, 48):
        kit.hits(bar, 1, "X.xxX.x.X.xxX.x.", 38, vel=80 - 4 * (bar - 44))
        tlo.hits(bar, 1, "X.......X.......", 40, vel=88)
    for bar in (16, 24, 32, 40):
        kit.note(B(bar), 2, 57, 112)
    for k in range(16, 44, 2):
        tm.note(B(k), 1.4, c.ctone(at(k), "R", 40), 98)
    tm.roll(B(15), B(16), 40, 40, 110, rate=8)
    tm.roll(B(31), B(32), 40, 40, 118, rate=8)
    for bb in c.pattern_beats(s, 16, 28, "X.......X......."):
        s.duck(bb, 0.7)
    c.clip_hats(s, 32, 12, "xoxoXoxoxoxoXoxo", vel=0.7)

    # --- choir in the lift --------------------------------------------------------------------------------------------
    cho = c.choir(s, vol=104)
    c.pad_chords(cho, s, 24, ch(24, 32), center=64, count=3, vel=90)
    c.pad_chords(cho, s, 40, ch(40, 44), center=64, count=3, vel=92)
    for bar, v in ((0, 0.7), (16, 0.9), (24, 1.0), (32, 1.15), (44, 0.7)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(16), 4, vel=0.35)
    c.riser_to(s, B(32), 8, vel=0.45)
    c.swell_to(s, B(24), 2, vel=0.45)
    return s
