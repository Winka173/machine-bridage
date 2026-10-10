"""battle_5: "Dust Devils" - desert battle. A Phrygian dominant (hijaz), 112 BPM, 52 bars.

Form (bars): A 0-7 hammered-dulcimer 16ths, frame-drum maqsum groove, drone |
B 8-15 shanai and oboe theme over the Andalusian descent | C 16-23 strings
in unison riffs, horns answer | D 24-31 half-time breakdown: solo flute, harp,
choir, a sandstorm riser | E 32-47 climax: the theme in horns and strings,
brass, war drums | F 48-51 the vamp again, a fill into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["A", "Bb", "A", "A"]
P2 = ["Dm", "C", "Bb", "A"]
P3 = ["Gm", "Bb", "A", "A"]
P4 = ["Dm", "Gm", "Bb", "A"]
CHORDS = (P1 + P1  # A 0-7
          + P2 + P2  # B 8-15
          + P1 + P3  # C 16-23
          + P4 + P4  # D 24-31
          + P2 + P2 + P2 + P1  # E 32-47
          + P1)  # F 48-51

THEME = ("D5:1.5 E5:0.5 F5:1 E5:0.5 D5:0.5 | E5:1.5 D5:0.5 C5:1 Bb4:0.5 C5:0.5 |"
         " D5:1 Bb4:1 A4:1 G4:0.5 Bb4:0.5 | A4:3 r:1 |"
         " A4:0.5 Bb4:0.5 C#5:0.5 D5:0.5 E5:1 F5:1 | G5:1.5 F5:0.5 E5:1 C5:1 |"
         " D5:1.5 C5:0.25 Bb4:0.25 A4:1 Bb4:1 | A4:4")
RIFF_A = "A3:0.5 A3:0.25 Bb3:0.25 C#4:0.5 D4:0.5 E4:0.5 F4:0.25 E4:0.25 D4:0.5 C#4:0.5"
RIFF_BB = "Bb3:0.5 Bb3:0.25 A3:0.25 Bb3:0.5 D4:0.5 F4:1 E4:0.5 D4:0.5"
RIFF_G = "G3:0.5 G3:0.25 A3:0.25 Bb3:0.5 D4:0.5 G4:1 F4:0.5 D4:0.5"
RIFF_END = "E4:0.5 D4:0.5 C#4:0.5 Bb3:0.5 A3:2"
ANSWER = "C#4:1.5 D4:0.5 E4:2 | F4:1 E4:1 C#4:2"
SOLO = ("A4:3 F4:1 | G4:2 Bb4:2 | D5:3 C5:0.5 Bb4:0.5 | C#5:4 | D5:2 E5:1 F5:1 | G5:2 F5:1 E5:1 |"
        " F5:1.5 E5:0.5 D5:1 C5:1 | C#5:2 E5:2")
DULC = ["8", "5", "3", "5", "R", "3", "5", "3"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("battle_5", bpm=112, bars=52, seed=81, tail_beats=16)
    s.master = {"hall_rt": 2.4}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 0.0, "str_hi": -1.0, "horns": 3.0, "brass": -1.0,
                            "low_brass": -2.0, "choir": -4.0, "drums": -4.0, "snare": -5.0, "timp": -3.0,
                            "cym": -9.0, "synth": -12.0, "sub": -10.0, "fx": -9.0, "keys": 1.0,
                            "drone": -11.0, "hats": -13.0})
    c.setup_extra(s, gains={"winds": 2.0, "perc": -2.0, "harp": 0.0})
    B = s.bar
    groove = [(0, 8), (8, 16), (16, 24), (32, 52)]

    # --- hammered dulcimer 16ths and harp -------------------------------------------------
    dul = s.part("dulcimer", 15, stem="ost", volume=100, pan=-0.2, ens=1, human_t=0.004, human_v=6)
    for a, b in groove:
        c.pattern_line(dul, s, a, ch(a, b), DULC, ref=62, vel=84 if a < 32 else 92,
                       accents="XxoxXxoxXxoxXxox", dur=1.4)
    hp = c.harp(s, vol=96)
    c.pattern_line(hp, s, 24, ch(24, 32), ["R", "5", "8", "10", "12", "10", "8", "5"], ref=50, steps=8,
                   vel=78, dur=1.8)

    # --- drone and bass ---------------------------------------------------------------------------
    s.clip("drone", B(48), synth.drone(33, s.sec(B(12)), 0.12, bright=0.4))  # wraps into A
    s.clip("drone", B(24), synth.drone(38, s.sec(B(8)), 0.1, bright=0.3))
    vc = c.celli(s, "celli", short=True, vol=100)
    cb = c.basses(s, "basses", short=True, vol=100)
    for a, b in groove:
        v = 86 if a < 16 else 98
        c.pattern_line(vc, s, a, ch(a, b), ["R", None, None, "R", None, None, "R", None], ref=45, steps=8,
                       vel=v, dur=1.0)
        c.pattern_line(cb, s, a, ch(a, b), ["R", None, None, "R", None, None, "R", None], ref=33, steps=8,
                       vel=v, dur=1.0)

    # --- the theme: shanai over oboe -----------------------------------------------------------
    sh = c.wind(s, "shanai", 111, vol=88, pan=0.1)
    ob = c.wind(s, "oboe", 68, vol=96, pan=-0.1)
    ob.mel(B(8), THEME, vel=92)
    sh.mel(B(8), THEME, vel=74)
    ob.mel(B(40), THEME, vel=96)
    c.expr_curve(ob, s, [(0, 110), (15, 120), (16, 110), (48, 110)])

    # --- C: string unison riff, horn answers ------------------------------------------------------
    us = c.strings(s, "unison", vol=104)
    lo = c.celli(s, "celli_riff", vol=100)
    for bar0, first in ((16, RIFF_A), (20, RIFF_G)):
        second = RIFF_BB
        for part, sh_ in ((us, 12), (lo, 0)):
            part.mel(B(bar0), first, vel=100, shift=sh_)
            part.mel(B(bar0 + 1), second, vel=96, shift=sh_)
            part.mel(B(bar0 + 2), RIFF_A, vel=100, shift=sh_)
            part.mel(B(bar0 + 3), RIFF_END, vel=96, shift=sh_)
    hn = c.horns(s, vol=104)
    hn.mel(B(18), ANSWER, vel=92)
    hn.mel(B(22), ANSWER, vel=100)
    hn.mel(B(32), THEME, vel=104, shift=-12)
    hn.mel(B(40), THEME, vel=108, shift=-12)
    c.expr_curve(hn, s, [(16, 108), (32, 120), (48, 120), (48.01, 100)])

    # --- D: solo flute, choir ---------------------------------------------------------------------
    fl = c.wind(s, "flute", 73, vol=98, pan=0.2)
    fl.mel(B(24), SOLO, vel=88)
    cho = c.choir(s, vol=98, ohh=True)
    c.pad_chords(cho, s, 24, ch(24, 32), center=60, count=3, vel=70)
    c.pad_chords(cho, s, 32, ch(32, 48), center=64, count=3, vel=84)
    c.expr_curve(cho, s, [(24, 70), (31.9, 110), (32, 96), (48, 100)])

    # --- E: strings and brass ------------------------------------------------------------------------
    vn = c.strings(s, "violins", vol=98)
    vn.mel(B(32), THEME, vel=96)
    vn.mel(B(40), THEME, vel=100, shift=12)
    sp = c.spiccato(s, "spic", vol=96)
    c.pattern_line(sp, s, 32, ch(32, 48), ["8", "5", "3", "5"], ref=57, steps=16,
                   accents="XxxxXxxxXxxxXxxx", vel=94, dur=0.7)
    br = c.brass_section(s, vol=98)
    tb = c.trombones(s, vol=100)
    tu = c.tuba(s, vol=96)
    for k in range(32, 48):
        sym = CHORDS[k]
        br.chord(B(k) + 1.5, 0.3, c.voicing(sym, 60, 4), 98)
        br.chord(B(k) + 2.5, 0.3, c.voicing(sym, 60, 4), 94)
        tb.chord(B(k), 1.4, [c.ctone(sym, "R", 45), c.ctone(sym, "5", 45)], 92)
        tu.note(B(k), 1.4, c.ctone(sym, "R", 33), 92)
    tp = c.trumpets(s, vol=96)
    tp.mel(B(44), "A4:0.5 Bb4:0.5 C#5:0.5 D5:0.5 E5:2 | F5:1 E5:1 D5:1 C#5:1 | E5:4 | r:4", vel=104)

    # --- percussion: frame drums (taiko dum, conga tek), tambourine --------------------------------
    dum = c.taiko(s, "dum", vol=112)
    hi = c.taiko(s, "taiko_hi", vol=100, pan=0.3)
    perc = c.drum_kit(s, "hand", 0, stem="perc", vol=100)
    bd = c.concert_bd(s, vol=114)
    kit = c.orch_kit(s, vol=98)
    tm = c.timpani(s, vol=114)
    for a, b in groove:
        big = a >= 32
        for bar in range(a, b):
            last = bar % 4 == 3
            dum.hits(bar, 1, "X..x..x.X.......", 40, vel=108 if big else 98)
            perc.hits(bar, 1, "...x..x....x.x.." if not last else "...x..x..xxxRRRR", 63, vel=92)
            perc.hits(bar, 1, ".o..o..o.o..o..o", 62, vel=74)
            perc.hits(bar, 1, "xoxoxoxoxoxoxoxo", 54, vel=56 if not big else 66)
            if big:
                bd.hits(bar, 1, "X.......X.......", 36, vel=104)
                hi.hits(bar, 1, "..x...x...x..xx." if not last else "..x...x.xxxxRRRR", 47, vel=94)
                kit.hits(bar, 1, "....X.......X...", 38, vel=92)
    for bar in range(24, 32):  # half-time
        dum.hits(bar, 1, "X.........x.....", 40, vel=92)
        perc.hits(bar, 1, "........x.......", 63, vel=80)
    dum.hits(31, 1, "X.....x.x.x.xRRR", 40, vel=104)
    kit.roll(B(31) + 2, B(32), 38, 40, 110, rate=8)
    kit.roll(B(51) + 2, B(52), 38, 40, 104, rate=8)
    for bar in (0, 16, 32, 40):
        kit.note(B(bar), 2, 57, 108)
    for k in range(32, 48, 2):
        tm.note(B(k), 1.5, c.ctone(CHORDS[k], "R", 45), 98)
    tm.roll(B(15) + 2, B(16), 45, 50, 104, rate=8)
    for bb in c.pattern_beats(s, 32, 16, "X.......X......."):
        s.duck(bb, 0.7)
    c.thumps(s, c.pattern_beats(s, 32, 16, "X.......X......."), vel=0.45)
    for bar, v in ((0, 0.8), (16, 0.9), (24, 0.7), (32, 1.1), (40, 0.9)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(32), 8, vel=0.5, f0=200.0, f1=7000.0)  # the sandstorm
    c.swell_to(s, B(8), 2, vel=0.45)
    c.swell_to(s, B(52), 2, vel=0.4)
    return s
