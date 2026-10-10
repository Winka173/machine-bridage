"""boss_naval: "Abyssal Titan" - capital ships and submarines. C# Phrygian, 80 BPM, 36 bars.

Slow and crushing, with the weight in the low register. Form (bars): A 0-7
sonar pings, deep drone, whale-call braams, a triplet ostinato in the celli
and basses | B 8-15 the low-brass motif (the tritone on the flat second),
low choir | C 16-23 the hull breaks the surface: brass chords, war drums,
the Phrygian dominant turn | D 24-31 climax, the motif in horns |
E 32-35 back down into the deep.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["C#m", "D", "C#m", "D"]
P2 = ["A", "Bm", "C#m", "C#m"]
P3 = ["F#m", "D", "Bm", "C#sus4>C#"]
P4 = ["D", "C#m", "D", "C#"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2  # D 24-31
          + P4)  # E 32-35

MOTIF = ("C#3:2 D3:1 C#3:1 | G#3:3 A3:1 | G#3:2 F#3:1 E3:1 | D3:4 |"
         " E3:2 C#3:2 | D3:2 F#3:2 | G#3:4 | G#3:2 C#4:2")
OST = [0, None, 0, 1, None, 0, 0, None, 0, 3, None, 1]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("boss_naval", bpm=80, bars=36, seed=141, tail_beats=16)
    s.master = {"hall_rt": 3.3, "glue": (-24.0, 2.0, 0.02, 0.3), "delay_beats": 1.5, "delay_feedback": 0.5}
    c.setup_stems(s, gains={"ost": 1.0, "str_lo": 3.0, "str_hi": -3.0, "horns": 2.0, "brass": 0.0,
                            "low_brass": 2.0, "choir": -1.0, "drums": -3.0, "snare": -5.0, "timp": 0.0,
                            "cym": -9.0, "synth": -12.0, "sub": -10.0, "fx": -9.0, "metal": -12.0,
                            "drone": -10.0, "keys": -4.0})
    B = s.bar
    bpb = s.beats_per_bar
    heavy = [(8, 24), (24, 32)]

    # --- triplet ostinato, low strings ---------------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=110)
    cb = c.basses(s, "basses", short=True, vol=108)
    for a, b, v in ((0, 8, 84), (8, 24, 100), (24, 36, 106)):
        c.pattern_line(vc, s, a, ch(a, b), OST, ref=49, steps=12, vel=v, accents="XxxxxxXxxxxx", dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), OST, ref=37, steps=12, vel=v, accents="XxxxxxXxxxxx", dur=0.8)
    c.expr_curve(vc, s, [(0, 90), (8, 112), (24, 124), (32, 100), (36, 90)])

    # --- the deep: drone, sonar, whale calls --------------------------------------------------------------
    s.clip("drone", B(32), synth.drone(25, s.sec(B(16)), 0.13, bright=0.3))  # wraps into A
    s.clip("drone", B(12), synth.drone(25, s.sec(B(24)), 0.11, bright=0.4, seed=5))
    sonar = c.mallets(s, "sonar", 11, vol=80, pan=0.3)  # vibraphone, through the long delay
    for bar in list(range(0, 8, 2)) + [32, 34]:
        sonar.note(B(bar), 3, 85, 74)
    for bar in (0, 4, 32):
        r = c.ctone(at(bar), "R", 37)
        s.clip("sub", B(bar) + 2, synth.braam([r, r + 7, r + 12], s.sec(8), 0.6, open_time=1.5, seed=bar + 1,
                                            bright=0.7))
    for k in range(8, 32, 2):
        r = c.ctone(at(k), "R", 37)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 13], s.sec(6), 0.7, open_time=0.35, seed=k, bright=1.1))
    for k in range(16, 32):
        s.clip("metal", B(k) + 2.5, synth.clang(52 if k % 2 else 57, 0.9, 2.2, seed=k % 4))

    # --- motif in the low brass, later the horns ------------------------------------------------------------
    tb = c.trombones(s, vol=108)
    tu = c.tuba(s, vol=106)
    tb.mel(B(8), MOTIF, vel=100)
    tu.mel(B(8), MOTIF, vel=100, shift=-12)
    tb.mel(B(24), MOTIF, vel=110)
    tu.mel(B(24), MOTIF, vel=108, shift=-12)
    hn = c.horns(s, vol=108)
    hn.mel(B(24), MOTIF, vel=110, shift=12)
    hn.mel(B(4), "G#3:4 | A3:4", vel=70, shift=12)
    c.expr_curve(hn, s, [(4, 90), (8, 90), (24, 127), (36, 127)])
    br = c.brass_section(s, vol=104)
    for k in range(16, 24):
        v = c.voicing(at(k), 58, 4)
        br.chord(B(k), 1.5, v, 110)
        br.chord(B(k) + 2, 0.5, c.voicing(at(k, 0.6), 58, 4), 104)
        br.chord(B(k) + 3, 1.0, c.voicing(at(k, 0.9), 58, 4), 108)
        tu.note(B(k), 1.9, c.ctone(at(k), "R", 37), 104)
        tu.note(B(k) + 2, 1.9, c.ctone(at(k, 0.6), "R", 37), 100)
    tp = c.trumpets(s, vol=98)
    for k in range(16, 24):
        r = c.ctone(at(k, 0.9), "R", 73)
        tp.chord(B(k) + 3, 0.9, [r, r + 1], 98)
    for k in range(32, 36):  # dissonant decline
        r = c.ctone(at(k), "R", 61)
        br.chord(B(k), 3.8, [r, r + 1, r + 7], 84)

    # --- choir and strings -------------------------------------------------------------------------------
    cho = c.choir(s, vol=106, ohh=True)
    c.pad_chords(cho, s, 8, ch(8, 16), center=52, count=3, vel=84)
    c.pad_chords(cho, s, 16, ch(16, 32), center=58, count=3, vel=96)
    c.expr_curve(cho, s, [(8, 90), (16, 110), (32, 120), (34, 80)])
    tr = c.tremolo(s, vol=100)
    for k in range(16, 32):
        r = c.ctone(at(k), "R", 73)
        tr.chord(B(k), bpb, [r, r + 1, r + 7], 84)
    c.expr_curve(tr, s, [(16, 80), (23.9, 120), (24, 96), (32, 120)])
    pad = c.strings(s, "pad", slow=True, vol=96)
    c.pad_chords(pad, s, 0, ch(0, 8), center=56, count=3, vel=70)

    # --- drums: half-time weight --------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=122)
    tlo = c.taiko(s, "taiko_lo", vol=120)
    tmid = c.taiko(s, "taiko_mid", vol=108, pan=-0.3)
    kit = c.orch_kit(s, vol=100)
    tm = c.timpani(s, vol=120)
    for bar in range(0, 8):
        tlo.hits(bar, 1, "X...............", 36, vel=86)
    for a, b in heavy:
        big = a == 24
        for bar in range(a, b):
            last = bar % 4 == 3
            bd.hits(bar, 1, "X.......X.....x.", 36, vel=114 if big else 106)
            tlo.hits(bar, 1, "X.....x.X.....x." if not last else "X.....x.X.x.xRRR", 36, vel=114)
            tmid.hits(bar, 1, "....x.......x...", 43, vel=96)
            if bar >= 16:
                kit.hits(bar, 1, "....X.......X...", 38, vel=96)
    for k in range(8, 32):
        tm.note(B(k), 1.5, c.ctone(at(k), "R", 37), 104)
    tm.roll(B(15), B(16), 37, 40, 120, rate=8)
    tm.roll(B(35), B(36), 37, 20, 84, rate=6)
    kit.roll(B(23), B(24), 38, 40, 118, rate=8)
    for bar in (8, 16, 24):
        kit.note(B(bar), 3, 57, 116)
    for bb in c.pattern_beats(s, 8, 24, "X.......X......."):
        s.duck(bb, 0.8)
    c.thumps(s, c.pattern_beats(s, 16, 16, "X.......X......."), vel=0.6, f0=95.0, f1=38.0, decay=0.4)
    for bar, v in ((0, 0.9), (8, 1.0), (16, 1.2), (24, 1.25), (32, 0.8)):
        c.boom_at(s, B(bar), vel=v, f0=50.0, f1=22.0, dur=4.0)
    c.riser_to(s, B(16), 8, vel=0.4, tone=0.3, tone_pitch=37)
    c.riser_to(s, B(24), 4, vel=0.35, tone=0.2, tone_pitch=37)
    return s
