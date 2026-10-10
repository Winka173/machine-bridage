"""battle_4: "Night Raid" - stealth and tension that breaks into a fight. F# minor, 100 BPM, 44 bars.

Form (bars): A 0-7 ticking clock, pizzicato cell, celesta, low drone | B 8-15
low flute theme over a cello pulse, heartbeat taiko | C 16-27 rising tension:
tremolo, spiccato 8ths, horn counter-line on the Neapolitan G | D 28-35 the
raid breaks loose: full drums, theme in horns and trumpets | E 36-43 back to
the shadows, ticks and pizzicato, a riser into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["F#m", "F#m", "D", "C#sus4>C#"]
P2 = ["F#m", "G", "Em", "F#m"]
P3 = ["Bm", "D", "G", "C#"]
P4 = ["F#m", "G", "F#m", "C#sus4>C#"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P2 + P3 + P3  # C 16-27
          + P1 + P2  # D 28-35
          + P1 + P4)  # E 36-43

THEME = ("F#4:1.5 G#4:0.5 A4:2 | C#5:1.5 B4:0.5 A4:1 G#4:1 | F#4:1.5 A4:0.5 D5:2 | C#5:3 r:1 |"
         " F#4:1.5 G#4:0.5 A4:2 | B4:1 A4:1 G4:2 | E4:1.5 G4:0.5 B4:2 | A4:2 G#4:1 F#4:1")
COUNTER = "B3:2 D4:1 F#4:1 | A4:3 F#4:1 | G4:2 B4:1 D5:1 | C#5:2 B4:1 G#4:1"
CELESTA = "C#6:0.5 A5:0.5 F#5:1 r:2 | r:4 | D6:0.5 A5:0.5 F#5:1 r:2 | r:4"
PIZZ = ["R", None, None, "5", None, "R", None, None, "8", None, "5", None, None, "R", None, None]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    """The chord sounding at ``frac`` of bar ``k`` (split bars like 'C#sus4>C#')."""
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("battle_4", bpm=100, bars=44, seed=71, tail_beats=16)
    s.master = {"hall_rt": 2.9, "delay_beats": 0.75, "delay_feedback": 0.45}
    c.setup_stems(s, gains={"ost": 3.0, "str_lo": 1.0, "str_hi": -2.0, "horns": 3.0, "brass": -1.0,
                            "low_brass": -2.0, "choir": -5.0, "drums": -4.0, "snare": -5.0, "timp": -3.0,
                            "cym": -10.0, "synth": -12.0, "bass": -16.0, "sub": -10.0, "fx": -10.0,
                            "hats": -13.0, "keys": 2.0, "drone": -11.0, "metal": -15.0})
    c.setup_extra(s, gains={"winds": 3.0})
    B = s.bar
    bpb = s.beats_per_bar
    quiet = [(0, 16), (36, 44)]

    # --- pizzicato cell and celesta (the night) -----------------------------------
    pz = c.pizz(s, vol=100)
    for a, b in quiet + [(16, 28)]:
        vel = 80 if a != 16 else 90
        c.pattern_line(pz, s, a, ch(a, b), PIZZ, ref=54, vel=vel, accents="XxxxxXxxxxxxxXxx", dur=0.9)
    cel = c.mallets(s, "celesta", 8, vol=84)
    for bar in (0, 4, 36, 40):
        cel.mel(B(bar), CELESTA, vel=70)

    # --- clock ticks and drone ----------------------------------------------------------
    c.clip_ticks(s, 0, 16, "X.x.x.x.", vel=2.2)
    c.clip_ticks(s, 36, 8, "X.x.x.x.", vel=2.2)
    s.clip("drone", B(36), synth.drone(30, s.sec(B(20)), 0.12, bright=0.25))  # wraps over the loop into A

    # --- cello pulse (B, D) and low strings ---------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=100)
    cb = c.basses(s, "basses", short=True, vol=100)
    c.pattern_line(vc, s, 8, ch(8, 16), ["R", None, "R", "R"], ref=42, vel=84, steps=8, accents="Xxxx", dur=0.8)
    c.pattern_line(cb, s, 8, ch(8, 16), ["R", None, None, None], ref=30, vel=82, steps=8, dur=1.6)
    c.pattern_line(vc, s, 16, ch(16, 28), ["R"], ref=42, vel=90, steps=8, accents="XxxXxxXx", dur=0.8,
                   vel_curve=lambda k: 84 + 2 * k)
    c.pattern_line(cb, s, 16, ch(16, 28), ["R"], ref=30, vel=90, steps=8, accents="XxxXxxXx", dur=0.8,
                   vel_curve=lambda k: 84 + 2 * k)
    gallop = ["R", "R", "R", None, "R", "R", "R", None, "R", "R", "R", None, "R", None, "5", "R"]
    c.pattern_line(vc, s, 28, ch(28, 36), gallop, ref=42, vel=106, dur=0.8)
    c.pattern_line(cb, s, 28, ch(28, 36), gallop, ref=30, vel=104, dur=0.8)

    # --- winds: the theme in the low flute, clarinet shadow -------------------------------
    fl = c.wind(s, "flute", 73, vol=96, pan=0.15)
    cl = c.wind(s, "clarinet", 71, vol=88, pan=-0.2)
    fl.mel(B(8), THEME, vel=84)
    cl.mel(B(8), THEME, vel=70, shift=-12)
    fl.mel(B(36), THEME[:THEME.index("| F#4:1.5", 10)], vel=72)
    c.expr_curve(fl, s, [(0, 96), (8, 96), (15, 112), (16, 100), (36, 92), (44, 96)])

    # --- spiccato 8ths and tremolo in C -------------------------------------------------------
    sp = c.spiccato(s, "spic", vol=98)
    c.pattern_line(sp, s, 20, ch(20, 28), ["8", "5", "10", "5"], ref=66, steps=8, accents="Xxxx", dur=0.7,
                   vel=80, vel_curve=lambda k: 76 + 4 * k)
    c.pattern_line(sp, s, 28, ch(28, 36), ["8", "5", "10", "5", "12", "5", "10", "5"], ref=66, steps=16,
                   accents="XxxxXxxxXxxxXxxx", dur=0.7, vel=100)
    tr = c.tremolo(s, vol=96)
    c.pad_chords(tr, s, 16, ch(16, 28), center=66, count=3, vel=76)
    c.expr_curve(tr, s, [(16, 60), (27.9, 122), (28, 70), (36, 70)])

    # --- horns and brass ------------------------------------------------------------------------
    hn = c.horns(s, vol=104)
    hn.mel(B(20), COUNTER, vel=86)
    hn.mel(B(24), COUNTER, vel=96)
    hn.mel(B(28), THEME, vel=104, shift=-12)
    c.expr_curve(hn, s, [(16, 100), (20, 96), (27.9, 124), (28, 120), (36, 120)])
    tp = c.trumpets(s, vol=98)
    tp.mel(B(32), THEME[THEME.index("F#4:1.5", 10):], vel=104)
    tb = c.trombones(s, vol=100)
    tu = c.tuba(s, vol=96)
    for k in range(28, 36):
        sym = at(k, 0.75)
        tb.chord(B(k), 1.6, [c.ctone(sym, "R", 47), c.ctone(sym, "5", 47)], 100)
        tb.chord(B(k) + 2.5, 1.2, [c.ctone(sym, "R", 47), c.ctone(sym, "5", 47)], 94)
        tu.note(B(k), 3.5, c.ctone(sym, "R", 30), 96)
    br = c.brass_section(s, vol=96)
    for k in range(28, 36):
        br.chord(B(k) + 1.5, 0.35, c.voicing(at(k), 62, 4), 100)
        br.chord(B(k) + 3.5, 0.35, c.voicing(at(k, 0.9), 62, 4), 96)
    for k in (25, 27):  # stopped-horn stings on the way up
        r = c.ctone(at(k), "R", 61)
        br.chord(B(k) + 3, 0.8, [r, r + 1], 84)

    # --- choir breath in C and D ---------------------------------------------------------------
    cho = c.choir(s, vol=96, ohh=True)
    c.pad_chords(cho, s, 24, ch(24, 36), center=62, count=3, vel=72)

    # --- synth pulse under C --------------------------------------------------------------------
    c.clip_pulse_line(s, "synth", 16, ch(16, 28), ["R", None, "8", "R"], ref=54, vel=0.5, gate=0.45, bright=0.4,
                      accents="Xoxo", vel_curve=lambda k: 0.36 + 0.03 * k)
    c.clip_bass_line(s, "bass", 28, ch(28, 36), ["R", None, "R", "R"], ref=42, vel=0.8, gate=0.6)

    # --- percussion -------------------------------------------------------------------------------
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=102, pan=0.3)
    bd = c.concert_bd(s, vol=116)
    kit = c.orch_kit(s, vol=98)
    tm = c.timpani(s, vol=116)
    tlo.hits(8, 8, "X..x............", 38, vel=78)  # heartbeat
    tlo.hits(16, 8, "X..x......x.....", 38, vel=88)
    tlo.hits(24, 3, "X..x..x...x.x...", 38, vel=98)
    tlo.hits(27, 1, "X..x..x.x.x.xxxx", 38, vel=104)
    kit.hits(8, 8, "............o...", 38, vel=60)
    kit.hits(16, 12, "....o.......o.oo", 38, vel=70)
    for bar in range(28, 36):
        last = bar % 4 == 3
        bd.hits(bar, 1, "X.....x...X.....", 36, vel=110)
        tlo.hits(bar, 1, "X..x..x.X..x.x.." if not last else "X..x..x.X.x.xRRR", 38, vel=110)
        thi.hits(bar, 1, "..x...x...x.x.x.", 47, vel=92)
        kit.hits(bar, 1, "....X.......X..o" if not last else "....X.......XrRR", 38, vel=100)
    kit.roll(B(27), B(28), 38, 30, 112, rate=8)
    kit.note(B(28), 3, 57, 116)
    kit.note(B(32), 2, 55, 100)
    for bar in range(36, 44, 4):
        tlo.hits(bar, 1, "X...............", 38, vel=82)
    tm.roll(B(15), B(16), 42, 30, 90, rate=6)
    tm.note(B(16), 2, 42, 92)
    for k in range(28, 36, 2):
        tm.note(B(k), 1.5, c.ctone(at(k), "R", 42), 104)
    for bb in c.pattern_beats(s, 28, 8, "X.....x...X....."):
        s.duck(bb, 0.8)
    c.clip_hats(s, 20, 8, "x.o.x.o.x.o.xoxo", vel=0.55)
    c.clip_hats(s, 28, 8, "xoxoXoxoxoxoXoxo", vel=0.8)
    for bar in (25, 27, 33, 35):
        s.clip("metal", B(bar) + 3, synth.clang(66, 0.8, 1.3, seed=bar % 3))
    for bar, v in ((0, 0.6), (16, 0.8), (28, 1.1), (36, 0.7)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(28), 8, vel=0.45, tone=0.25, tone_pitch=42)
    c.riser_to(s, B(44), 4, vel=0.3, tone=0.15, tone_pitch=42)
    c.swell_to(s, B(16), 2, vel=0.4)
    return s
