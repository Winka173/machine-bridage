"""menu: "Command Briefing" - calm, heroic, slow build. D minor, 80 BPM, 36 bars.

Form (bars): A 0-7 intro texture (pads, piano cell, pulse) | B 8-15 horn theme |
C 16-27 full statement (trumpets, brass, choir, drums) | D 28-35 wind-down that
flows back into A. The Brigade theme first heard here returns in the stingers.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

BRIGADE_THEME = "D4:3 A4:1 | Bb4:2 A4:1 G4:1 | A4:3 F4:1 | G4:4 | D4:3 A4:1 | D5:2 C5:1 Bb4:1 | A4:2 G4:1 F4:1 | E4:4"
CLIMAX = ("F4:1.5 Bb4:0.5 D5:2 | C5:3 A4:1 | G4:1.5 C5:0.5 E5:2 | D5:4 | F5:1.5 D5:0.5 Bb4:2 | C5:2 A4:1 C5:1 |"
          " D5:2 Bb4:1 G4:1 | A4:2 C#5:1 E5:1 | F5:3 E5:0.5 D5:0.5 | E5:2 C5:1 G4:1 | D5:4")

PHRASE = ["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "Asus4>A"]
CHORDS = (PHRASE  # A 0-7
          + PHRASE  # B 8-15
          + ["Bb", "F", "C", "Dm", "Bb", "F", "Gm", "A"]  # C 16-23
          + ["Bb", "C", "Dm", "Dm"]  # C 24-27
          + PHRASE)  # D 28-35


def build() -> Song:
    s = Song("menu", bpm=80, bars=36, seed=11, tail_beats=16)
    s.master = {"hall_rt": 3.1, "hall_gain": 1.05}
    c.setup_stems(s, gains={"str_hi": 0.0, "keys": 7.0, "synth": -12.0, "drone": -12.0, "choir": -2.0,
                            "brass": -2.0, "horns": 4.0, "drums": -1.0, "timp": 2.0, "sub": -6.0,
                            "low_brass": -4.0, "ost": 3.0, "snare": -6.0, "cym": -8.0, "fx": -10.0},
                  synth={"duck": 0.35, "delay": 0.25})
    bpb = s.beats_per_bar
    B = s.bar

    # --- strings pad and bass, whole piece ---------------------------------
    pad = c.strings(s, "pad", slow=True, vol=100)
    lo = c.basses(s, "basses", vol=100)
    c.pad_chords(pad, s, 0, CHORDS, center=62, count=4, vel=80)
    for k, sym in enumerate(CHORDS):
        for frac, ss in c.split_bar(sym):
            v = 74 if k < 8 or k >= 28 else 82 if k < 16 else 96
            lo.note(B(k) + frac * bpb, bpb / len(sym.split(">")), c.ctone(ss, "R", 38), v)
    c.expr_curve(pad, s, [(0, 86), (6, 90), (8, 92), (15, 100), (16, 108), (26, 116), (27, 98), (28, 96), (34, 86), (36, 86)])
    c.expr_curve(lo, s, [(0, 80), (16, 110), (27, 104), (28, 92), (36, 80)])

    # --- piano cell (A and D) -------------------------------------------------
    pno = c.piano(s, vol=88)
    cell = ["8", "5", "10"]
    c.pattern_line(pno, s, 0, CHORDS[0:8], cell, ref=64, vel=70, steps=8, dur=2.2)
    c.pattern_line(pno, s, 28, CHORDS[28:36], cell, ref=64, vel=60, steps=8, dur=2.2,
                   vel_curve=lambda k: 72 - 2 * k)

    # --- synth pulse -------------------------------------------------------------
    c.clip_pulse_line(s, "synth", 0, CHORDS[0:8], ["R"], ref=50, vel=0.55, steps=8, gate=0.5, bright=0.35,
                      vel_curve=lambda k: 0.45 + 0.03 * k)
    c.clip_pulse_line(s, "synth", 8, CHORDS[8:16], ["R", "R", "8", "R"], ref=50, vel=0.55, steps=16, gate=0.45,
                      bright=0.45, accents="Xoxo")
    c.clip_pulse_line(s, "synth", 16, CHORDS[16:27], ["R", "R", "8", "R"], ref=50, vel=0.62, steps=16, gate=0.45,
                      bright=0.6, accents="Xoxo")
    c.clip_pulse_line(s, "synth", 28, CHORDS[28:36], ["R"], ref=50, vel=0.55, steps=8, gate=0.5, bright=0.35,
                      vel_curve=lambda k: 0.62 - 0.03 * k)

    # --- low drone under A and D (wraps across the loop point) ----------------
    s.clip("drone", B(28), synth.drone(38, s.sec(B(16)), 0.12, bright=0.3))

    # --- celli ---------------------------------------------------------------------
    vc = c.celli(s, "celli_sus", vol=96)
    for k in range(4, 8):
        for frac, ss in c.split_bar(CHORDS[k]):
            vc.note(B(k) + frac * bpb, bpb / len(CHORDS[k].split(">")), c.ctone(ss, "5", 50), 60 + 3 * k)
    vco = c.celli(s, "celli_ost", vol=100, short=True)
    c.pattern_line(vco, s, 8, CHORDS[8:16], ["R", "5", "8", "5", "10", "5", "8", "5"], ref=50, vel=78, steps=8,
                   accents="XxxxXxxx", dur=0.9)
    c.pattern_line(vco, s, 16, CHORDS[16:27], ["R", "5", "8", "5", "10", "5", "8", "5"], ref=50, vel=96, steps=8,
                   accents="XxxxXxxx", dur=0.9)
    c.pattern_line(vco, s, 28, CHORDS[28:32], ["R", "5", "8", "5", "10", "5", "8", "5"], ref=50, steps=8,
                   accents="XxxxXxxx", dur=0.9, vel=70, vel_curve=lambda k: 72 - 5 * k)

    # --- horns: theme in B, echo in D ----------------------------------------------
    hn = c.horns(s, vol=104)
    hn.mel(B(8), BRIGADE_THEME, vel=88)
    hn.mel(B(16), CLIMAX, vel=96, shift=-12)
    hn.mel(B(28), "D4:3 A4:1 | Bb4:2 A4:1 G4:1 | A4:3 F4:1 | G4:4", vel=66)
    c.expr_curve(hn, s, [(0, 100), (8, 96), (15, 112), (16, 118), (27, 118), (28, 92), (32, 80), (36, 100)])

    # --- climax brass ------------------------------------------------------------------
    tp = c.trumpets(s, vol=100)
    tp.mel(B(16), CLIMAX, vel=100)
    br = c.brass_section(s, vol=96)
    c.pad_chords(br, s, 16, CHORDS[16:27], center=60, count=4, vel=86)
    tb = c.trombones(s, vol=96)
    tu = c.tuba(s, vol=96)
    for k in range(16, 27):
        sym = CHORDS[k]
        tb.chord(B(k), bpb - 0.2, [c.ctone(sym, "R", 48), c.ctone(sym, "5", 48)], 82 if k < 24 else 98)
        tu.note(B(k), bpb - 0.2, c.ctone(sym, "R", 38), 86 if k < 24 else 100)
    br.ramp(B(26), B(27) + 2, 127, 70)
    tb.ramp(B(26), B(27) + 2, 127, 70)

    # --- strings motion in C -------------------------------------------------------------
    vn = c.spiccato(s, "violins", vol=92)
    c.pattern_line(vn, s, 16, CHORDS[16:26], ["8", "5", "10", "5", "12", "5", "10", "5"], ref=62, vel=82, steps=8,
                   accents="XxxxXxxx", dur=0.8)

    # --- choir ----------------------------------------------------------------------------------
    ch = c.choir(s, vol=100)
    c.pad_chords(ch, s, 12, CHORDS[12:16], center=62, count=3, vel=62)
    c.pad_chords(ch, s, 16, CHORDS[16:27], center=64, count=3, vel=84)
    c.expr_curve(ch, s, [(12, 70), (16, 100), (26, 120), (27, 60), (28, 60)])

    # --- percussion ------------------------------------------------------------------------------
    tk = c.taiko(s, vol=112)
    tk.hits(8, 7, "X.......x...x...", 40, vel=82)
    tk.hits(15, 1, "X.......x.x.xxxx", 40, vel=90)
    tk.hits(16, 8, "X..x..x.X...x.x.", 40, vel=104)
    tk.hits(24, 2, "X..x..x.X..x..xR", 40, vel=112)
    tk.hits(26, 1, "X...............", 40, vel=120)
    tk.hits(28, 1, "X...............", 40, vel=70)
    tk2 = c.taiko(s, "taiko_hi", vol=100, pan=0.3)
    tk2.hits(16, 8, "....x.......x.xx", 47, vel=80)
    tk2.hits(24, 2, "..x...x...x...x.", 47, vel=90)
    bd = c.concert_bd(s, vol=118)
    bd.hits(16, 8, "X.......X.......", 36, vel=100)
    bd.hits(24, 3, "X.......X.......", 36, vel=112)
    for b in c.pattern_beats(s, 16, 11, "X.......X......."):
        s.duck(b, 0.7)
    tm = c.timpani(s, vol=118)
    tm.roll(B(6), B(8), 38, 20, 88, rate=6)
    tm.note(B(8), 2, 38, 96)
    for k in range(16, 26):
        tm.note(B(k), 1.5, c.ctone(CHORDS[k], "R", 43), 92)
    tm.roll(B(23), B(24), 45, 50, 105, rate=8)
    tm.roll(B(25) + 2, B(26), 38, 60, 115, rate=8)
    tm.note(B(26), 3, 38, 124)
    kit = c.orch_kit(s)
    for bar in (16, 24, 26):
        kit.note(B(bar), 2, 57, 110)
    kit.roll(B(15), B(16), 38, 30, 96, rate=8)
    kit.hits(16, 8, "....x......ox...", 38, vel=70)
    kit.roll(B(23) + 2, B(24), 38, 40, 100, rate=8)
    for bar in (16, 20, 24, 26):
        c.boom_at(s, B(bar), vel=0.95 if bar != 26 else 1.1)
    c.swell_to(s, B(16), 4, vel=0.7)
    c.swell_to(s, B(24), 4, vel=0.6)
    c.riser_to(s, B(16), 8, vel=0.35, tone=0.15)
    return s
