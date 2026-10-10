"""boss_final: "Doomsday Engine" - the final boss and super-weapons. D harmonic minor, 7/4 at 132 BPM, 36 bars.

Seven beats to the bar, grouped 2+2+3, so the machine never settles. Patterns
use 14 eighth-note steps per bar. Form (bars): A 0-7 the 7/4 string
ostinato, tolling bells, clangs, a low hum | B 8-15 the choir chant over low
brass | C 16-23 the brass motif (the C# diminished turn), war drums,
trumpets | D 24-31 climax: the chant in choir, horns and trumpets over
everything | E 32-35 the motif's end collapses back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Dm", "Eb", "Dm", "A"]
P2 = ["Bb", "Gm", "Eb", "A"]
P3 = ["Dm", "Bb", "Gm", "A"]
P4 = ["F", "Eb", "C#dim", "A"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2  # D 24-31
          + P4)  # E 32-35

CHANT = ("D4:2 F4:2 A4:3 | Bb4:2 A4:2 G4:3 | F4:2 E4:2 D4:3 | C#4:4 E4:3 |"
         " D5:2 C5:2 Bb4:3 | Bb4:2 A4:2 G4:3 | G4:2 F4:2 Eb4:3 | E4:4 C#4:3")
MOTIF = ("A4:3 D5:2 F5:2 | F5:4 D5:3 | D5:2 Bb4:2 G4:3 | A4:7 |"
         " A4:3 C5:2 F5:2 | G5:4 Eb5:3 | E5:2 G5:2 Bb4:3 | C#5:7")
OST = [0, 0, 12, 0, 0, 0, 12, 0, 0, 0, 7, 0, 1, 0]
ACC = "XxxxXxxxXxxxxx"
STEPS = 14


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("boss_final", bpm=132, bars=36, beats_per_bar=7, seed=181, tail_beats=16)
    s.master = {"hall_rt": 3.0, "glue": (-24.0, 2.0, 0.02, 0.25)}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 2.0, "str_hi": -2.0, "horns": 3.0, "brass": 0.0,
                            "low_brass": 1.0, "choir": 0.0, "drums": -4.0, "snare": -4.0, "timp": -1.0,
                            "cym": -9.0, "synth": -12.0, "bass": -14.0, "sub": -11.0, "fx": -9.0,
                            "metal": -15.0, "drone": -12.0, "keys": -2.0, "hats": -13.0})
    B = s.bar
    bpb = s.beats_per_bar

    # --- the 7/4 ostinato -------------------------------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=110)
    cb = c.basses(s, "basses", short=True, vol=106)
    vla = c.spiccato(s, "violas", vol=98)
    for a, b, v in ((0, 8, 92), (8, 24, 102), (24, 36, 108)):
        c.pattern_line(vc, s, a, ch(a, b), OST, ref=50, steps=STEPS, vel=v, accents=ACC, dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), OST, ref=38, steps=STEPS, vel=v, accents=ACC, dur=0.8)
        c.pattern_line(vla, s, a, ch(a, b), OST, ref=62, steps=STEPS, vel=v - 8, accents=ACC, dur=0.7)
    c.clip_bass_line(s, "bass", 16, ch(16, 36), [0, None, None, None, 0, None, None, None, 0, None, None, None,
                                                 None, None], ref=38, vel=0.85, steps=STEPS, gate=0.8)

    # --- bells, clangs, hum ---------------------------------------------------------------------------------
    bells = c.mallets(s, "bells", 14, vol=92, pan=-0.15)
    for k in range(0, 36):
        if k < 8 or k >= 32:
            bells.chord(B(k), 4, [c.ctone(CHORDS[k], "R", 62), c.ctone(CHORDS[k], "R", 74)], 84)
        elif k % 2 == 0:
            bells.note(B(k), 4, c.ctone(CHORDS[k], "R", 74), 88)
        s.clip("metal", B(k) + 4, synth.clang(60, 0.9, 1.3, seed=k % 3))
        s.clip("metal", B(k) + 5.5, synth.clang(67, 0.7, 1.0, seed=(k + 1) % 3))
    s.clip("drone", B(32), synth.drone(26, s.sec(B(12)), 0.12, bright=0.35))
    hum = c.choir(s, "hum", vol=96, ohh=True)
    c.pad_chords(hum, s, 0, ch(0, 8), center=52, count=3, vel=72)
    c.pad_chords(hum, s, 32, ch(32, 36), center=52, count=3, vel=78)

    # --- choir chant, low brass ----------------------------------------------------------------------------------
    cho = c.choir(s, vol=108)
    cho.mel(B(8), CHANT, vel=96)
    cho.mel(B(24), CHANT, vel=108)
    c.pad_chords(cho, s, 16, ch(16, 24), center=60, count=3, vel=88)
    c.expr_curve(cho, s, [(8, 112), (24, 127), (32, 110)])
    tb = c.trombones(s, vol=106)
    tu = c.tuba(s, vol=104)
    for k in range(8, 36):
        r = c.ctone(CHORDS[k], "R", 38)
        tu.note(B(k), 3.8, r, 96)
        tu.note(B(k) + 4, 2.8, r, 92)
        if k < 16:
            tb.chord(B(k), 6.8, [c.ctone(CHORDS[k], "R", 50), c.ctone(CHORDS[k], "5", 50)], 88)
    tb.mel(B(24), CHANT, vel=104, shift=-12)

    # --- brass motif and climax -------------------------------------------------------------------------------
    hn = c.horns(s, vol=108)
    tp = c.trumpets(s, vol=102)
    hn.mel(B(16), MOTIF, vel=104)
    tb.mel(B(16), MOTIF, vel=102, shift=-12)
    hn.mel(B(24), CHANT, vel=110)
    tp.mel(B(24), CHANT, vel=106, shift=12)
    hn.mel(B(32), MOTIF[MOTIF.index("A4:3 C5"):], vel=108)
    tp.mel(B(32), MOTIF[MOTIF.index("A4:3 C5"):], vel=104)
    c.expr_curve(hn, s, [(16, 116), (24, 127), (36, 127)])
    br = c.brass_section(s, vol=102)
    for k in range(16, 32):
        v = c.voicing(CHORDS[k], 60, 4)
        for off in (0, 2, 4):
            br.chord(B(k) + off, 0.4, v, 110 if off == 0 else 102)
    tr = c.tremolo(s, vol=100)
    for k in range(16, 32):
        r = c.ctone(CHORDS[k], "R", 74)
        tr.chord(B(k), bpb, [r, r + 1, r + 7] if CHORDS[k] in ("Eb", "C#dim") else c.voicing(CHORDS[k], 76, 3),
                 82)
    c.expr_curve(tr, s, [(16, 80), (23.9, 120), (24, 100), (32, 124), (32.01, 70)])

    # --- hybrid weight ----------------------------------------------------------------------------------------
    for k in list(range(0, 36, 2)):
        r = c.ctone(CHORDS[k], "R", 26)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(6), 0.6 if k < 8 else 0.72, open_time=0.4,
                                        seed=k + 2, bright=1.1))

    # --- drums in seven -------------------------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=120)
    tlo = c.taiko(s, "taiko_lo", vol=118)
    thi = c.taiko(s, "taiko_hi", vol=104, pan=0.3)
    tmid = c.taiko(s, "taiko_mid", vol=106, pan=-0.3)
    kit = c.orch_kit(s, vol=102)
    tm = c.timpani(s, vol=120)
    for bar in range(36):
        last = bar % 4 == 3
        if bar < 8:
            tlo.hits(bar, 1, "X.......X.....", 38, vel=94, steps=STEPS)
            continue
        big = 16 <= bar < 32
        bd.hits(bar, 1, "X...X...X.....", 36, vel=114 if big else 106, steps=STEPS)
        tlo.hits(bar, 1, "X..xX..xX.x.x." if not last else "X..xX..xX.xRRR", 38, vel=112, steps=STEPS)
        tmid.hits(bar, 1, "..x...x.....x.", 43, vel=96, steps=STEPS)
        if big:
            thi.hits(bar, 1, "xoxoxoxoxoxoxo", 48, vel=90, steps=STEPS)
            kit.hits(bar, 1, "....X.......X.", 38, vel=98, steps=STEPS)
        tm.note(B(bar), 1.4, c.ctone(CHORDS[bar], "R", 38), 104 if big else 96)
        tm.note(B(bar) + 4, 1.4, c.ctone(CHORDS[bar], "R", 38), 96)
    tm.roll(B(7) + 4, B(8), 38, 30, 110, rate=6)
    tm.roll(B(15) + 4, B(16), 45, 40, 120, rate=8)
    kit.roll(B(23) + 4, B(24), 38, 40, 118, rate=8)
    kit.roll(B(35) + 3, B(36), 38, 30, 110, rate=8)
    for bar in (8, 16, 24, 28):
        kit.note(B(bar), 3, 57, 116)
    for bb in c.pattern_beats(s, 8, 28, "X...X...X.....", steps=STEPS):
        s.duck(bb, 0.75)
    c.thumps(s, c.pattern_beats(s, 16, 16, "X...X...X.....", steps=STEPS), vel=0.55, f0=110.0, f1=45.0)
    c.clip_hats(s, 16, 16, "xoxoXoxoxoxoxo", vel=0.65, steps=STEPS)
    for bar, v in ((0, 1.0), (8, 1.0), (16, 1.2), (24, 1.3), (32, 0.9)):
        c.boom_at(s, B(bar), vel=v, f0=60.0, f1=25.0)
    c.riser_to(s, B(16), 7, vel=0.45, tone=0.3, tone_pitch=38)
    c.riser_to(s, B(24), 7, vel=0.45)
    c.swell_to(s, B(36), 4, vel=0.45)
    return s
