"""boss_train: "Juggernaut Express" - armoured and nuclear trains. F# Phrygian, 144 BPM, 68 bars.

Wheels, pistons and a steam whistle. Form (bars): A 0-7 the engine starts:
brushed "chukka" snare 16ths, piston clangs, low-string wheel rhythm, a
whistle | B 8-23 the low-brass motif (the Phrygian G) | C 24-31 the strings'
theme over the rails | D 32-39 breakdown: pistons, kit and synth only |
E 40-55 climax | F 56-67 full steam, whistle, into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["F#m", "G", "F#m", "G"]
P2 = ["Em", "D", "G", "F#m"]
P3 = ["Bm", "G", "A", "G"]
P4 = ["Em", "G", "F#sus4>F#", "F#"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P1  # D 32-39
          + P2 + P3 + P2 + P4  # E 40-55
          + P1 + P2 + P1)  # F 56-67

MOTIF = ("F#3:0.75 F#3:0.25 G3:1 F#3:0.5 C#4:1.5 | D4:1 C#4:1 B3:0.5 A3:0.5 G3:1 |"
         " F#3:0.75 F#3:0.25 G3:1 F#3:0.5 E4:1.5 | D4:2 C#4:2")
MOTIF2 = "E4:1.5 G4:0.5 B4:2 | A4:1 F#4:1 D4:2 | B3:1 D4:1 G4:2 | F#4:3 C#4:1"
THEME = "D5:2 C#5:1 B4:1 | B4:2 D5:2 | C#5:2 E5:2 | D5:4 | B4:2 G4:1 E4:1 | D5:2 B4:2 | B4:2 A#4:2 | C#5:4"
WHEELS = "X.x.X.x.X.x.X.x."


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def whistle(part, s: Song, bar: float, vel: int = 96) -> None:
    """A steam whistle: a short then a long blast on a dissonant dyad, falling away."""
    b = s.bar(bar)
    part.chord(b, 0.5, [85, 88, 92], vel)
    part.chord(b + 0.75, 2.6, [85, 88, 92], vel)
    part.ramp(b + 0.75, b + 3.4, 120, 50)
    part.cc(b + 3.5, 11, 120)


def build() -> Song:
    s = Song("boss_train", bpm=144, bars=68, seed=161, tail_beats=16)
    s.master = {"hall_rt": 2.2}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 1.0, "str_hi": -2.0, "horns": 3.0, "brass": 0.0,
                            "low_brass": 1.0, "choir": -4.0, "drums": -4.0, "snare": -3.0, "timp": -2.0,
                            "cym": -9.0, "synth": -11.0, "bass": -14.0, "sub": -11.0, "fx": -9.0,
                            "metal": -15.0, "hats": -12.0})
    c.setup_extra(s, gains={"lead": -6.0})
    B = s.bar
    run = [(0, 32), (40, 68)]

    # --- the wheels: low strings, spiccato --------------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=106)
    cb = c.basses(s, "basses", short=True, vol=104)
    for a, b in run:
        c.pattern_line(vc, s, a, ch(a, b), ["R", None, "R", None, "R", None, "R", "R"], ref=42, vel=98,
                       accents="XxxxXxxx", dur=0.8, vel_curve=(lambda k: 94 + k) if a == 0 else None)
        c.pattern_line(cb, s, a, ch(a, b), ["R", None, "R", None, "R", None, "R", "R"], ref=30, vel=98,
                       accents="XxxxXxxx", dur=0.8)
    sp = c.spiccato(s, "spic", vol=100)
    for a, b in ((8, 32), (40, 68)):
        c.pattern_line(sp, s, a, ch(a, b), ["R", "R", "5", "R", "b2", "R", "5", "R"], ref=54, vel=96,
                       accents="XxxxXxxxXxxxXxxx", dur=0.7)

    # --- motif and theme -------------------------------------------------------------------------------------
    tb = c.trombones(s, vol=106)
    tu = c.tuba(s, vol=102)
    hn = c.horns(s, vol=106)
    for k in range(0, 8):  # the engine: low brass pedal, swelling
        tb.chord(B(k), 3.8, [c.ctone(at(k), "R", 42), c.ctone(at(k), "5", 42)], 92)
        tu.note(B(k), 3.8, c.ctone(at(k), "R", 30), 94)
    tb.ramp(B(0), B(8) - 0.2, 70, 120)
    for bar0 in (8, 16):
        tb.mel(B(bar0), MOTIF, vel=100)
        tu.mel(B(bar0), MOTIF, vel=98, shift=-12)
        hn.mel(B(bar0 + 4), MOTIF2, vel=96)
        tb.mel(B(bar0 + 4), MOTIF2, vel=96, shift=-12)
    for bar0 in (40, 48):
        hn.mel(B(bar0), MOTIF2, vel=108)
        tb.mel(B(bar0), MOTIF2, vel=104, shift=-12)
    for bar0 in (56, 64):
        tb.mel(B(bar0), MOTIF, vel=108)
        tu.mel(B(bar0), MOTIF, vel=104, shift=-12)
        hn.mel(B(bar0), MOTIF, vel=106, shift=12)
    hn.mel(B(60), MOTIF2, vel=108)
    c.expr_curve(hn, s, [(8, 116), (24, 104), (40, 126), (68, 126)])
    vn = c.strings(s, "violins", vol=102)
    vn.mel(B(24), THEME, vel=94)
    half = THEME[:THEME.index("| B4:2 G4")]
    vn.mel(B(44), half, vel=100)
    vn.mel(B(52), THEME[THEME.index("B4:2 G4"):], vel=104)
    tp = c.trumpets(s, vol=100)
    tp.mel(B(44), half, vel=104)
    tp.mel(B(52), THEME[THEME.index("B4:2 G4"):], vel=108)
    lo = c.celli(s, "celli_theme", vol=98)
    lo.mel(B(24), THEME, vel=88, shift=-12)
    br = c.brass_section(s, vol=100)
    for k in list(range(8, 24)) + list(range(40, 68)):
        v = c.voicing(at(k), 60, 4)
        br.chord(B(k) + 1.5, 0.3, v, 100)
        br.chord(B(k) + 3.5, 0.3, c.voicing(at(k, 0.9), 60, 4), 96)

    # --- whistle and choir ------------------------------------------------------------------------------------
    wh = c.synth_lead(s, "whistle", 80, vol=86)
    for bar in (2, 6, 24, 40, 56, 66):
        whistle(wh, s, bar)
    cho = c.choir(s, vol=100)
    c.pad_chords(cho, s, 24, ch(24, 32), center=62, count=3, vel=80)
    c.pad_chords(cho, s, 48, ch(48, 56), center=64, count=3, vel=90)

    # --- breakdown: pistons and synth ----------------------------------------------------------------------
    c.clip_pulse_line(s, "synth", 32, ch(32, 40), ["R", "R", "8", "R", "b2", "R", "8", "R"], ref=54, vel=0.65,
                      gate=0.4, bright=0.75, vel_curve=lambda k: 0.5 + 0.03 * k)
    c.clip_bass_line(s, "bass", 32, ch(32, 40), ["R", None, "R", "R"], ref=42, vel=0.85, gate=0.55)
    for k in range(0, 68):
        if 32 <= k < 40:
            for off in (0, 1, 2, 3):
                s.clip("metal", B(k) + off, synth.clang(57 if off % 2 == 0 else 62, 0.9, 0.9, seed=off))
        else:
            s.clip("metal", B(k) + 1, synth.clang(62, 0.8, 0.9, seed=1))
            s.clip("metal", B(k) + 3, synth.clang(62, 0.8, 0.9, seed=2))
    for k in range(32, 40, 4):
        r = c.ctone(at(k), "R", 30)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(8), 0.65, open_time=0.4, seed=k, bright=1.1))

    # --- drums: the "chukka" brushes and the train -------------------------------------------------------------
    kit = c.orch_kit(s, vol=102)
    bd = c.concert_bd(s, vol=116)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=102, pan=0.3)
    tm = c.timpani(s, vol=116)
    for bar in range(0, 68):
        last = bar % 4 == 3
        ramp = min(1.0, 0.7 + 0.04 * bar) if bar < 8 else 1.0
        kit.hits(bar, 1, "XoxoXoxoXoxoXoxo", 38, vel=int(86 * ramp))
        if bar < 8 or 32 <= bar < 40:
            bd.hits(bar, 1, "X.......X.......", 36, vel=int(108 * ramp))
            tlo.hits(bar, 1, "X.......X.....x." if bar % 4 != 3 else "X.......X.x.xRRR", 40, vel=int(104 * ramp))
            continue
        bd.hits(bar, 1, "X.....x.X.......", 36, vel=110)
        tlo.hits(bar, 1, "X..x..x.X..x..x." if not last else "X..x..x.X.x.xRRR", 40, vel=108)
        thi.hits(bar, 1, "....x.......x.x.", 47, vel=94)
    for bar in (8, 24, 40, 56):
        kit.note(B(bar), 2, 57, 114)
    kit.roll(B(39), B(40), 38, 40, 118, rate=8)
    for k in range(8, 68, 2):
        if 32 <= k < 40:
            continue
        tm.note(B(k), 1.4, c.ctone(at(k), "R", 42), 100)
    tm.roll(B(31), B(32), 42, 40, 116, rate=8)
    for bb in c.pattern_beats(s, 8, 24, "X.....x.X.......") + c.pattern_beats(s, 40, 28, "X.....x.X......."):
        s.duck(bb, 0.7)
    c.clip_hats(s, 32, 8, WHEELS, vel=0.8)
    c.clip_hats(s, 40, 28, "x.x.x.x.x.x.x.x.", vel=0.55)
    for bar, v in ((0, 0.8), (8, 1.0), (24, 0.9), (32, 1.0), (40, 1.2), (56, 1.1)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(40), 8, vel=0.5)
    c.riser_to(s, B(68), 4, vel=0.35)
    c.swell_to(s, B(24), 2, vel=0.45)
    return s
