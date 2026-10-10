"""boss_rush: "Gauntlet" - Boss Rush, one boss after another. D Phrygian, 158 BPM, 72 bars.

The fastest track: a hybrid four-on-the-floor engine under the orchestra.
Form (bars): A 0-7 synth bass 16ths, sub kick, arp | B 8-23 the brass motif
over driving strings | C 24-31 half-time: choir and horns, the D major turn |
D 32-39 breakdown: arp and pad, a long riser | E 40-55 climax | F 56-71 the
next wave: the motif with a high trumpet counter-line, back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Dm", "Eb", "Dm", "Eb"]
P2 = ["Bb", "Cm", "Dm", "Dm"]
P3 = ["Gm", "Eb", "F", "Eb"]
P4 = ["Gm", "Bb", "Eb", "Dsus4>D"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P2  # D 32-39
          + P1 + P2 + P3 + P4  # E 40-55
          + P1 + P2 + P1 + P2)  # F 56-71

MOTIF = ("D4:0.5 D4:0.5 A4:1 G4:0.5 F4:0.5 Eb4:1 | D4:0.5 D4:0.5 Bb4:1 A4:0.5 G4:0.5 Eb4:1 |"
         " D4:0.5 D4:0.5 A4:1 C5:1 A4:1 | Bb4:2 G4:1 Eb4:1 |"
         " F4:1 Bb4:1 D5:2 | Eb5:1 C5:1 G4:2 | F4:1 A4:1 D5:2 | D5:3 r:1")
HYMN = "G4:2 Bb4:2 | Bb4:2 G4:2 | A4:2 C5:2 | Bb4:4 | D5:2 Bb4:2 | D5:2 F5:2 | Eb5:2 G4:2 | G4:2 F#4:2"
COUNTER = "A5:2 Bb5:2 | G5:4 | A5:2 F5:2 | G5:4 | F5:2 D5:2 | Eb5:2 G5:2 | F5:2 A5:2 | D5:4"


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("boss_rush", bpm=158, bars=72, seed=201, tail_beats=16)
    s.master = {"hall_rt": 1.9, "delay_beats": 0.75, "delay_feedback": 0.35}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": -1.0, "str_hi": -2.0, "horns": 3.0, "brass": 0.0,
                            "low_brass": -1.0, "choir": -3.0, "drums": -6.0, "snare": -4.0, "timp": -3.0,
                            "cym": -9.0, "synth": -9.0, "bass": -10.0, "sub": -13.0, "fx": -9.0,
                            "hats": -10.0, "pad": -12.0})
    B = s.bar
    engine = [(0, 24), (40, 72)]

    # --- the engine: synth bass, sub kick, arp ---------------------------------------------------------
    for a, b in engine:
        c.clip_bass_line(s, "bass", a, ch(a, b), [None, "R", "R", "8", None, "R", "R", "R"], ref=38, vel=0.85,
                         gate=0.55, cutoff=1100)
        c.thumps(s, c.pattern_beats(s, a, b - a, "X...X...X...X..."), vel=0.7, f0=130.0, f1=48.0, decay=0.22)
        c.clip_hats(s, a, b - a, "..x...x...x...x." if a == 0 else "x.X.x.X.x.X.x.X.", vel=0.7)
    c.clip_pulse_line(s, "synth", 0, ch(0, 8), ["R", "8", "5", "8", "b2", "8", "5", "8"], ref=62, vel=0.55,
                      gate=0.4, bright=0.7)
    c.clip_pulse_line(s, "synth", 32, ch(32, 40), ["R", "8", "5", "8", "10", "8", "5", "8"], ref=62, vel=0.65,
                      gate=0.4, bright=0.8, vel_curve=lambda k: 0.5 + 0.03 * k)
    c.clip_pulse_line(s, "synth", 56, ch(56, 72), ["R", "8", "5", "8"], ref=62, vel=0.45, gate=0.4, bright=0.6)
    for k in range(32, 40, 4):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(at(k), 62, 4), s.sec(16), 0.9, cutoff=1500))

    # --- strings ---------------------------------------------------------------------------------------------
    sp = c.spiccato(s, "spic", vol=102)
    for a, b in ((8, 24), (40, 72)):
        c.pattern_line(sp, s, a, ch(a, b), ["R", "R", "5", "R", "8", "R", "5", "R"], ref=62, vel=96,
                       accents="XxxxXxxxXxxxXxxx", dur=0.7)
    vc = c.celli(s, "celli", short=True, vol=102)
    for a, b in ((8, 24), (40, 72)):
        c.pattern_line(vc, s, a, ch(a, b), ["R"], ref=50, steps=8, vel=96, accents="XxXxXxXx", dur=0.8)
    hs = c.strings(s, "hi_str", slow=True, vol=92)
    c.pad_chords(hs, s, 24, ch(24, 32), center=74, count=3, vel=76)
    c.pad_chords(hs, s, 48, ch(48, 56), center=76, count=3, vel=80)
    c.pad_chords(hs, s, 32, ch(32, 40), center=72, count=3, vel=74)
    c.expr_curve(hs, s, [(24, 100), (32, 80), (39.9, 122), (40, 100)])
    for k in range(32, 40):
        vc.note(B(k), 3.8, c.ctone(at(k), "R", 50), 86)

    # --- brass ---------------------------------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    tp = c.trumpets(s, vol=100)
    tb = c.trombones(s, vol=104)
    for bar0 in (8, 16, 40, 56, 64):
        hn.mel(B(bar0), MOTIF, vel=100 if bar0 < 40 else 108)
        tb.mel(B(bar0), MOTIF, vel=98 if bar0 < 40 else 104, shift=-12)
    tp.mel(B(16), MOTIF, vel=100, shift=12)
    hn.mel(B(32), MOTIF, vel=84)  # the breakdown: the motif, distant
    hn.mel(B(24), HYMN, vel=96)
    hn.mel(B(48), HYMN, vel=110)
    tp.mel(B(48), HYMN, vel=106, shift=12)
    for bar0 in (56, 64):
        tp.mel(B(bar0), COUNTER, vel=104)
    c.expr_curve(hn, s, [(8, 116), (24, 104), (40, 126), (72, 126)])
    br = c.brass_section(s, vol=98)
    for k in list(range(8, 24)) + list(range(40, 72)):
        br.chord(B(k) + 1.5, 0.3, c.voicing(at(k), 62, 4), 100)
        br.chord(B(k) + 3.5, 0.3, c.voicing(at(k, 0.9), 62, 4), 96)
    tu = c.tuba(s, vol=100)
    for k in list(range(24, 32)) + list(range(48, 56)):
        tu.note(B(k), 3.8, c.ctone(at(k), "R", 38), 96)

    # --- choir --------------------------------------------------------------------------------------------------
    cho = c.choir(s, vol=104)
    c.pad_chords(cho, s, 24, ch(24, 32), center=62, count=3, vel=86)
    c.pad_chords(cho, s, 48, ch(48, 56), center=65, count=3, vel=94)
    for k in range(40, 48):  # choir hits
        cho.chord(B(k), 0.5, c.voicing(at(k), 64, 3), 104)

    # --- orchestral drums over the engine ------------------------------------------------------------------------
    kit = c.orch_kit(s, vol=102)
    bd = c.concert_bd(s, vol=114)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=102, pan=0.3)
    tm = c.timpani(s, vol=114)
    for a, b in ((8, 24), (40, 72)):
        for bar in range(a, b):
            last = bar % 4 == 3
            tlo.hits(bar, 1, "X..x..x.X..x..x." if not last else "X..x..x.X.x.xRRR", 40, vel=104)
            thi.hits(bar, 1, "..x...x...x...x.", 47, vel=90)
            kit.hits(bar, 1, "....X.......X..." if not last else "....X.......XrRR", 38, vel=100)
    for bar in range(24, 32):
        bd.hits(bar, 1, "X.........X.....", 36, vel=112)
        tlo.hits(bar, 1, "X.........x.....", 40, vel=108)
        kit.hits(bar, 1, "........X.......", 38, vel=104)
    for bar in range(32, 40):
        kit.hits(bar, 1, "x.x.x.x.x.x.x.x." if bar < 38 else "xxxxxxxxxxxxxxxx", 38, vel=60 + 6 * (bar - 32))
    for bar in (8, 24, 40, 48, 56):
        kit.note(B(bar), 2, 57, 114)
    for k in list(range(8, 32, 2)) + list(range(40, 72, 2)):
        tm.note(B(k), 1.4, c.ctone(at(k), "R", 43), 98)
    for bb in c.pattern_beats(s, 0, 24, "X...X...X...X...") + c.pattern_beats(s, 40, 32, "X...X...X...X...") + \
            c.pattern_beats(s, 24, 8, "X.........X....."):
        s.duck(bb, 0.7)
    for k in (24, 28, 40, 48):
        r = c.ctone(at(k), "R", 38)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(5), 0.7, open_time=0.3, seed=k, bright=1.2))
    for bar, v in ((0, 0.9), (8, 1.0), (24, 1.0), (40, 1.2), (56, 1.0)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(40), 8, vel=0.55)
    c.riser_to(s, B(72), 4, vel=0.35)
    c.swell_to(s, B(24), 2, vel=0.45)
    return s
