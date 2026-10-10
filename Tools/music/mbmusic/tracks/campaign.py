"""campaign: "War Room" - the campaign map and briefings: pensive, planning, resolve. Ab Lydian, 72 BPM, 32 bars.

The raised fourth (D natural, the Bb major chord) keeps it open and
forward-looking. Form (bars): A 0-7 a piano figure, a soft pad, the clock |
B 8-15 the cello melody over a brushed snare cadence and harp | C 16-23
horns and strings swell to a resolve | D 24-31 the reprise in flute and
glockenspiel, thinning back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Ab", "Bb", "Fm", "Eb"]
P2 = ["Db", "Eb", "Cm", "Fm"]
P3 = ["Db", "Ab", "Bbm", "Eb"]
P4 = ["Fm", "Db", "Eb", "Eb"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2)  # D 24-31

MELODY = ("C4:3 Eb4:1 | D4:2 F4:2 | C4:2 Ab3:1 Bb3:1 | G3:4 |"
          " Ab3:2 F4:2 | Eb4:2 G4:2 | Eb4:1.5 D4:0.5 C4:2 | C4:4")
HORNS = "F4:2 Ab4:2 | Eb4:2 C5:2 | Db5:2 Bb4:2 | G4:4 | Ab4:2 C5:2 | Db5:2 F5:2 | Eb5:3 Db5:1 | Bb4:4"
FIGURE = ["R", "5", "9", "5", "10", "5", "8", "5"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("campaign", bpm=72, bars=32, seed=231, tail_beats=16)
    s.master = {"hall_rt": 3.2, "hall_gain": 1.1, "delay_beats": 0.75, "delay_feedback": 0.4}
    c.setup_stems(s, gains={"str_hi": -1.0, "str_lo": 1.0, "keys": 7.0, "synth": -14.0, "drone": -12.0,
                            "choir": -4.0, "brass": -3.0, "horns": 3.0, "drums": -4.0, "timp": 0.0,
                            "sub": -9.0, "low_brass": -4.0, "ost": 0.0, "snare": -5.0, "cym": -10.0,
                            "fx": -12.0, "hats": -12.0})
    c.setup_extra(s, gains={"harp": 0.0, "winds": 1.0})
    B = s.bar
    bpb = s.beats_per_bar

    # --- the piano figure and the clock ------------------------------------------------------------------
    pno = c.piano(s, vol=92)
    c.pattern_line(pno, s, 0, ch(0, 32), FIGURE, ref=56, steps=8, vel=74, accents="XxxxXxxx", dur=1.5,
                   vel_curve=lambda k: 76 if k < 8 else 66 if k < 24 else 70)
    c.clip_ticks(s, 0, 8, "X...x...", vel=1.4)
    c.clip_ticks(s, 24, 8, "X...x...", vel=1.4)
    c.clip_pulse_line(s, "synth", 0, ch(0, 32), ["R", None, None, None, "R", None, None, None], ref=44, vel=0.5,
                      steps=8, gate=0.8, bright=0.25)
    s.clip("drone", B(24), synth.drone(32, s.sec(B(16)), 0.1, bright=0.25))

    # --- pad, basses, celli melody ---------------------------------------------------------------------------
    pad = c.strings(s, "pad", slow=True, vol=98)
    c.pad_chords(pad, s, 0, CHORDS, center=63, count=4, vel=74)
    c.expr_curve(pad, s, [(0, 84), (8, 90), (16, 100), (22, 116), (24, 92), (32, 84)])
    lo = c.basses(s, "basses", vol=98)
    for k, sym in enumerate(CHORDS):
        lo.note(B(k), bpb - 0.1, c.ctone(sym, "R", 44), 74 if k < 8 else 84 if k < 24 else 76)
    vc = c.celli(s, "celli", vol=104)
    vc.mel(B(8), MELODY, vel=90)
    vc.mel(B(24), MELODY[:MELODY.index("| Ab3:2")], vel=76)
    c.expr_curve(vc, s, [(8, 104), (12, 116), (16, 104), (24, 96), (32, 104)])
    hp = c.harp(s, vol=92)
    c.pattern_line(hp, s, 8, ch(8, 24), ["R", "5", "8", "10", "12", "10"], ref=56, steps=12, vel=66, dur=2.0)

    # --- horns, violins, low brass: the resolve ----------------------------------------------------------------
    hn = c.horns(s, vol=104)
    hn.mel(B(16), HORNS, vel=90)
    c.expr_curve(hn, s, [(16, 100), (22, 122), (24, 100)])
    vn = c.strings(s, "violins", vol=96)
    vn.mel(B(16), HORNS, vel=82, shift=12)
    tb = c.trombones(s, vol=92)
    for k in range(16, 24):
        tb.chord(B(k), bpb - 0.2, [c.ctone(CHORDS[k], "R", 44), c.ctone(CHORDS[k], "5", 44)], 78)
    cho = c.choir(s, vol=96, ohh=True)
    c.pad_chords(cho, s, 16, ch(16, 24), center=60, count=3, vel=70)

    # --- reprise: flute and glockenspiel ----------------------------------------------------------------------
    fl = c.wind(s, "flute", 73, vol=92, pan=0.2)
    fl.mel(B(28), MELODY[MELODY.index("Ab3:2"):], vel=76, shift=12)
    gl = c.mallets(s, "glock", 9, vol=74, pan=0.3)
    c.pattern_line(gl, s, 24, ch(24, 28), ["12", None, None, None, "10", None, "8", None], ref=80, steps=8,
                   vel=58, dur=1.5)

    # --- percussion: a soft brushed cadence -----------------------------------------------------------------------
    kit = c.orch_kit(s, vol=92)
    kit.hits(8, 8, "o.o.x.o.o.oox.o.", 38, vel=60)
    kit.hits(16, 7, "o.o.X.o.o.ooX.oo", 38, vel=70)
    kit.roll(B(23), B(24), 38, 30, 90, rate=8)
    kit.note(B(16), 2, 55, 84)
    kit.note(B(24), 2, 57, 80)
    tm = c.timpani(s, vol=112)
    for k in range(16, 24, 2):
        tm.note(B(k), 1.5, c.ctone(CHORDS[k], "R", 44), 84)
    tm.roll(B(7) + 2, B(8), 44, 20, 70, rate=6)
    tk = c.taiko(s, vol=106)
    tk.hits(16, 8, "X.......x.......", 40, vel=78)
    c.boom_at(s, B(16), vel=0.55)
    c.boom_at(s, B(24), vel=0.45)
    c.swell_to(s, B(16), 4, vel=0.4)
    return s
