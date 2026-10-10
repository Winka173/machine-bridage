"""menu_2: "Rally Point" - the second main-menu theme, warm and hopeful. G Mixolydian, 90 BPM, 40 bars.

The flat seventh (F) gives it an anthem's lift. Form (bars): A 0-7 piano
arpeggios, string pad, a solo horn hint | B 8-15 the horn theme over cello
8ths, light snare | C 16-23 the strings' counter-theme, swelling | D 24-31
the full statement: trumpets, choir, timpani | E 32-39 winding down into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["G", "F", "C", "G"]
P2 = ["Em", "C", "Dsus4>D", "D"]
P3 = ["C", "G", "Am", "Em"]
P4 = ["C", "D", "G", "G"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2  # D 24-31
          + P3 + P4)  # E 32-39

THEME = ("D4:1.5 G4:0.5 B4:2 | A4:1.5 F4:0.5 C5:2 | E5:1.5 D5:0.5 C5:1 A4:1 | B4:3 G4:1 |"
         " B4:1.5 G4:0.5 E5:2 | E5:1 D5:1 C5:1 G4:1 | A4:2 D5:2 | D5:2 F#5:2")
COUNTER = "G4:2 E4:1 G4:1 | D5:3 B4:1 | C5:2 A4:1 E4:1 | B4:4 | C5:2 E5:2 | F#5:2 A5:2 | G5:4 | D5:2 B4:2"
ARP = ["R", "5", "8", "10", "12", "10", "8", "5"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("menu_2", bpm=90, bars=40, seed=221, tail_beats=16)
    s.master = {"hall_rt": 3.0, "hall_gain": 1.05}
    c.setup_stems(s, gains={"str_hi": 0.0, "str_lo": 0.0, "keys": 6.0, "synth": -13.0, "drone": -13.0,
                            "choir": -2.0, "brass": -2.0, "horns": 4.0, "drums": -2.0, "timp": 1.0,
                            "sub": -7.0, "low_brass": -4.0, "ost": 2.0, "snare": -6.0, "cym": -9.0,
                            "fx": -11.0})
    c.setup_extra(s, gains={"harp": 0.0, "winds": 0.0})
    B = s.bar
    bpb = s.beats_per_bar

    # --- piano and harp ---------------------------------------------------------------------------------
    pno = c.piano(s, vol=92)
    for a, b, v in ((0, 8, 74), (8, 16, 68), (32, 40, 70)):
        c.pattern_line(pno, s, a, ch(a, b), ARP, ref=55, steps=8, vel=v, accents="XxxxXxxx", dur=1.6)
    hp = c.harp(s, vol=94)
    c.pattern_line(hp, s, 16, ch(16, 32), ["R", "5", "8", "10", "12", "15", "12", "10"], ref=55, steps=8, vel=74,
                   dur=1.8)

    # --- strings pad, basses ---------------------------------------------------------------------------
    pad = c.strings(s, "pad", slow=True, vol=100)
    c.pad_chords(pad, s, 0, CHORDS, center=62, count=4, vel=78)
    c.expr_curve(pad, s, [(0, 84), (8, 92), (16, 100), (23, 112), (24, 116), (31, 116), (32, 96), (40, 84)])
    lo = c.basses(s, "basses", vol=100)
    for k, sym in enumerate(CHORDS):
        for frac, ss in c.split_bar(sym):
            lo.note(B(k) + frac * bpb, bpb / len(sym.split(">")) - 0.05, c.ctone(ss, "R", 43),
                    76 if k < 8 or k >= 32 else 86 if k < 24 else 96)
    vco = c.celli(s, "celli_ost", vol=100, short=True)
    c.pattern_line(vco, s, 8, ch(8, 32), ["R", "5", "8", "5"], ref=48, steps=8, vel=84, accents="XxxxXxxx",
                   dur=0.9, vel_curve=lambda k: 80 + k)

    # --- horn theme, strings counter, trumpets ---------------------------------------------------------------
    sh = c.solo_horn(s, vol=96)
    sh.mel(B(4), "D4:3 G4:1 | G4:4 | A4:4 | A4:2 F#4:2", vel=70)
    hn = c.horns(s, vol=106)
    hn.mel(B(8), THEME, vel=90)
    hn.mel(B(24), THEME, vel=104, shift=-12)
    c.expr_curve(hn, s, [(8, 104), (15, 116), (16, 104), (24, 124), (32, 100), (40, 100)])
    vn = c.strings(s, "violins", vol=100)
    vn.mel(B(16), COUNTER, vel=88)
    vn.mel(B(24), THEME, vel=96, shift=12)
    vn.mel(B(32), COUNTER[:COUNTER.index("| C5:2 E5")], vel=78)
    fl = c.wind(s, "flute", 73, vol=90, pan=0.2)
    fl.mel(B(36), COUNTER[COUNTER.index("C5:2 E5"):], vel=74)
    tp = c.trumpets(s, vol=98)
    tp.mel(B(24), THEME, vel=100)
    br = c.brass_section(s, vol=94)
    c.pad_chords(br, s, 24, ch(24, 32), center=60, count=4, vel=84)
    tb = c.trombones(s, vol=94)
    tu = c.tuba(s, vol=94)
    for k in range(24, 32):
        tb.chord(B(k), bpb - 0.2, [c.ctone(at(k), "R", 48), c.ctone(at(k), "5", 48)], 84)
        tu.note(B(k), bpb - 0.2, c.ctone(at(k), "R", 36), 88)
    br.ramp(B(31), B(32), 127, 80)

    # --- choir -----------------------------------------------------------------------------------------------
    cho = c.choir(s, vol=100)
    c.pad_chords(cho, s, 20, ch(20, 24), center=62, count=3, vel=66)
    c.pad_chords(cho, s, 24, ch(24, 32), center=64, count=3, vel=86)
    c.expr_curve(cho, s, [(20, 80), (24, 106), (31, 116), (32, 70)])

    # --- percussion ---------------------------------------------------------------------------------------------
    kit = c.orch_kit(s, vol=96)
    kit.hits(8, 8, "....x.......x.o.", 38, vel=66)
    kit.hits(16, 8, "....x.....o.x.o.", 38, vel=74)
    kit.hits(24, 8, "..o.X...o.o.X.oo", 38, vel=86)
    kit.roll(B(23) + 2, B(24), 38, 30, 100, rate=8)
    for bar in (16, 24, 28):
        kit.note(B(bar), 2, 57, 104)
    tk = c.taiko(s, vol=110)
    tk.hits(16, 8, "X.......x.......", 40, vel=86)
    tk.hits(24, 7, "X..x..x.X...x.x.", 40, vel=102)
    tk.hits(31, 1, "X..x..x.X.x.xxxx", 40, vel=108)
    bd = c.concert_bd(s, vol=116)
    bd.hits(24, 8, "X.......X.......", 36, vel=100)
    for b in c.pattern_beats(s, 24, 8, "X.......X......."):
        s.duck(b, 0.6)
    tm = c.timpani(s, vol=116)
    tm.roll(B(7), B(8), 43, 20, 80, rate=6)
    tm.note(B(8), 2, 43, 88)
    for k in range(24, 32):
        tm.note(B(k), 1.5, c.ctone(at(k), "R", 43), 94)
    tm.roll(B(23), B(24), 43, 40, 110, rate=8)
    for bar, v in ((16, 0.6), (24, 0.95), (28, 0.8)):
        c.boom_at(s, B(bar), vel=v)
    c.swell_to(s, B(24), 4, vel=0.55)
    c.riser_to(s, B(24), 8, vel=0.3, tone=0.1)
    return s
