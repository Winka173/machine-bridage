"""battle_2: "Iron Rain" - gallop and 3+3+2 martial groove. C minor, 116 BPM, 64 bars.

Form (bars): A 0-7 gallop + taiko + snare | B 8-15 low-brass riff |
C 16-31 theme (horns/trumpets) over the gallop | D 32-39 breakdown (snare
cadence, horn call, choir) | E 40-55 climax: theme against the riff |
F 56-63 riff + fill back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Cm", "Ab", "Eb", "Bb"]
P2 = ["Cm", "Ab", "Fm", "G"]
P3 = ["Ab", "Bb", "Cm", "Cm"]
P4 = ["Fm", "Ab", "G", "G"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2  # B 8-15
          + P1 + P2 + P1 + P2  # C 16-31
          + P3 + P4  # D 32-39
          + P1 + P2 + P1 + P2  # E 40-55
          + P1 + P2)  # F 56-63

THEME = ("G4:3 Eb4:1 | C5:3 Ab4:1 | Bb4:2 G4:2 | F4:4 | G4:3 Eb4:1 | Ab4:2 C5:2 | C5:1.5 Bb4:0.5 Ab4:2 |"
         " G4:2 B4:2")
CALL = "Eb4:4 | D4:4 | C4:4 | G4:4 | F4:2 Ab4:2 | C5:4 | B4:4 | B4:2 D5:2"
GALLOP = ["R", None, "R", "R"]
RIFF = ["R", None, None, "R", None, None, "3", None, "2", None, None, "R", None, None, "-5", None]
SNARE_332 = "XooXooXoXooXooXo"


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("battle_2", bpm=116, bars=64, seed=31, tail_beats=16)
    s.master = {"hall_rt": 2.5}
    c.setup_stems(s, gains={"ost": 3.0, "str_lo": 1.0, "str_hi": -2.0, "horns": 3.0, "brass": 0.0,
                            "low_brass": 0.0, "choir": -3.0, "drums": -3.0, "snare": -1.0, "timp": -2.0,
                            "cym": -9.0, "synth": -12.0, "bass": -16.0, "sub": -10.0, "fx": -10.0, "drone": -14.0,
                            "hats": -15.0})
    B = s.bar
    gallop_secs = [(0, 8), (16, 32)]
    riff_secs = [(8, 16), (40, 64)]

    # --- gallop low strings + synth bass -------------------------------------
    vc = c.celli(s, "celli", short=True, vol=106)
    cb = c.basses(s, "basses", short=True, vol=104)
    for a, b in gallop_secs:
        c.pattern_line(vc, s, a, ch(a, b), GALLOP, ref=48, vel=92 if a == 0 else 98, accents="Xoxx", dur=0.85)
        c.pattern_line(cb, s, a, ch(a, b), GALLOP, ref=38, vel=92 if a == 0 else 98, accents="Xoxx", dur=0.85)
        c.clip_bass_line(s, "bass", a, ch(a, b), GALLOP, ref=36, vel=0.8, gate=0.7)
    # --- riff ---------------------------------------------------------------------
    tb = c.trombones(s, vol=106)
    tu = c.tuba(s, vol=102)
    for a, b in riff_secs:
        vel = 100 if a == 8 else 110
        c.pattern_line(tb, s, a, ch(a, b), RIFF, ref=48, vel=vel, dur=1.9)
        c.pattern_line(tu, s, a, ch(a, b), RIFF, ref=36, vel=vel, dur=1.9)
        c.pattern_line(vc, s, a, ch(a, b), RIFF, ref=48, vel=vel, dur=1.8)
        c.pattern_line(cb, s, a, ch(a, b), RIFF, ref=38, vel=vel, dur=1.8)
        c.clip_bass_line(s, "bass", a, ch(a, b), RIFF, ref=36, vel=0.8, gate=1.6)

    # --- high string ostinato (3+3+2 arpeggio) ----------------------------------
    sp = c.spiccato(s, "violins", vol=100)
    cells = ["R", "5", "8", "R", "5", "8", "R", "5"]
    c.pattern_line(sp, s, 16, ch(16, 32), cells, ref=62, vel=88, accents="XxxXxxXx", dur=0.7)
    c.pattern_line(sp, s, 40, ch(40, 56), cells, ref=62, vel=96, accents="XxxXxxXx", dur=0.7)
    c.pattern_line(sp, s, 56, ch(56, 64), ["8", "5"], ref=62, vel=90, accents="Xx", dur=0.7)

    # --- theme --------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    tp = c.trumpets(s, vol=100)
    hn.mel(B(16), THEME, vel=92)
    hn.mel(B(24), THEME, vel=100)
    tp.mel(B(24), THEME, vel=92)
    hn.mel(B(32), CALL, vel=72)
    tp.mel(B(40), THEME, vel=104)
    tp.mel(B(48), THEME, vel=110)
    hn.mel(B(40), THEME, vel=104, shift=-12)
    hn.mel(B(48), THEME, vel=108, shift=-12)
    c.expr_curve(hn, s, [(0, 116), (32, 116), (32.01, 88), (38, 110), (40, 124), (64, 124)])

    # --- brass chords, sustained strings, choir ---------------------------------------------
    br = c.brass_section(s, vol=100)
    for k in range(16, 32):
        br.chord(B(k) + 2.5, 0.35, c.voicing(CHORDS[k], 60, 4), 96)
    c.pad_chords(br, s, 40, ch(40, 56), center=58, count=4, vel=86)
    for k in range(56, 64):
        for off in (0, 1.5):
            br.chord(B(k) + off, 0.35, c.voicing(CHORDS[k], 62, 4), 108)
    hs = c.strings(s, "hi_str", slow=True, vol=92)
    c.pad_chords(hs, s, 24, ch(24, 32), center=72, count=3, vel=74)
    c.pad_chords(hs, s, 40, ch(40, 56), center=74, count=3, vel=80)
    tr = c.tremolo(s, vol=100)
    c.pad_chords(tr, s, 32, ch(32, 40), center=62, count=4, vel=76)
    c.expr_curve(tr, s, [(32, 70), (38, 105), (39.95, 122), (40, 80)])
    cho = c.choir(s, vol=104, ohh=True)
    c.pad_chords(cho, s, 32, ch(32, 40), center=58, count=3, vel=70)
    cho2 = c.choir(s, "choir_ah", vol=104)
    c.pad_chords(cho2, s, 40, ch(40, 56), center=64, count=3, vel=88)

    # --- breakdown synth pulse + drone ---------------------------------------------------------
    c.clip_pulse_line(s, "synth", 32, ch(32, 40), ["R", "R", "8", "R", "5", "R", "8", "R"], ref=48, vel=0.6,
                      gate=0.5, bright=0.5, vel_curve=lambda k: 0.4 + 0.08 * k, accents="XoxoXoxo")
    s.clip("drone", B(32), synth.drone(36, s.sec(B(8)), 0.12, bright=0.35))

    # --- drums ---------------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=118)
    tlo = c.taiko(s, "taiko_lo", vol=116)
    thi = c.taiko(s, "taiko_hi", vol=106, pan=-0.25)
    kit = c.orch_kit(s, vol=106)
    tm = c.timpani(s, vol=118)
    full = [(0, 32), (40, 64)]
    for a, b in full:
        for bar in range(a, b):
            last = (bar - a) % 4 == 3
            intense = bar >= 40
            bd.hits(bar, 1, "X.....X.........", 36, vel=108 if intense else 100)
            tlo.hits(bar, 1, "X..X..X.X..X..X.", 40, vel=108 if intense else 100)
            thi.hits(bar, 1, "..x..x.x..x.xRRR" if last else "..x..x.x..x..x.x", 47, vel=90)
            if bar < 8 or intense:
                kit.hits(bar, 1, SNARE_332, 38, vel=92 if intense else 82)
            else:
                kit.hits(bar, 1, "....X..o....X.oo" if not last else "....X..o..rrRRRR", 38, vel=96)
    cadence = ["X.oxX.oxX.oxRRRR", "f.o.x.o.f.o.x.oo", "X.oxX.oxX.oxRRRR", "f.o.x.o.RRRRRRRR"]
    for i, bar in enumerate(range(32, 40)):
        kit.hits(bar, 1, cadence[i % 4], 38, vel=78 + 3 * i)
        tlo.hits(bar, 1, "X.......X.......", 40, vel=80 + 3 * i)
    kit.roll(B(63), B(64), 38, 50, 115, rate=8)
    for bar in (0, 16, 40, 56):
        kit.note(B(bar), 2, 57, 112)
    for bar in (8, 24, 48):
        kit.note(B(bar), 2, 55, 100)
    for bar in range(0, 64, 2):
        if 32 <= bar < 40:
            continue
        tm.note(B(bar), 1.5, c.ctone(CHORDS[bar], "R", 43), 100)
    for bar in range(32, 40):
        tm.note(B(bar), 1, c.ctone(CHORDS[bar], "R", 43), 70 + 4 * (bar - 32))
    tm.roll(B(39), B(40), 43, 60, 118)
    tm.roll(B(15) + 2, B(16), 43, 60, 112)
    for a, b in full:
        for bb in c.pattern_beats(s, a, b - a, "X.....X.........", chars="X"):
            s.duck(bb, 0.8)
    for bar, v in ((0, 1.0), (8, 0.9), (16, 1.0), (32, 0.7), (40, 1.15), (56, 1.0)):
        c.boom_at(s, B(bar), vel=v)
    for a, b in ((16, 32), (40, 64)):  # shaker-style 16ths for drive and air
        c.clip_hats(s, a, b - a, "xoxoXoxoxoxoXoxo", vel=0.7, pan_spread=0.4)
    c.riser_to(s, B(40), 8, vel=0.4)
    c.riser_to(s, B(64), 4, vel=0.35)
    c.swell_to(s, B(16), 2, vel=0.5)
    return s
