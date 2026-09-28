"""Stingers: victory (D major fanfare on the Brigade theme) and defeat (D minor lament).

Both are one-shots (no loop); they start on the first sample and ring out
naturally into silence.
"""

from __future__ import annotations

from ..score import Song
from . import common as c


def victory() -> Song:
    s = Song("victory", bpm=100, bars=3, loop=False, tail_beats=6, seed=71)
    s.master = {"hall_rt": 2.6, "target_lufs": -15.0}
    c.setup_stems(s, gains={"brass": 1.0, "horns": 2.0, "str_hi": -2.0, "str_lo": 0.0, "choir": -3.0,
                            "drums": -3.0, "timp": 1.0, "cym": -6.0, "sub": -8.0, "low_brass": -1.0, "ost": -1.0})
    # chords: D (1-3) | G (3-4) | A (4-5) | D (5-9 ring)
    tp = c.trumpets(s, vol=106)
    tp.mel(0, "A4:0.333 A4:0.333 A4:0.334 | D5:1.5 A4:0.5 | B4:1 | C#5:1 | D5:4.5", vel=108)
    hn = c.horns(s, vol=106)
    hn.mel(1, "F#4:1.5 F#4:0.5 | G4:1 | A4:1 | F#4:4.5", vel=100)
    hn.mel(1, "D4:2 | D4:1 | C#4:1 | A3:4.5", vel=96)
    br = c.brass_section(s, vol=104)
    br.chord(1, 1.9, [50, 57, 62, 66], 104)
    br.chord(3, 0.95, [55, 59, 62, 67], 100)
    br.chord(4, 0.95, [57, 61, 64, 69], 104)
    br.chord(5, 4.5, [50, 57, 62, 66, 69], 110)
    br.ramp(5, 9.5, 127, 90)
    tb = c.trombones(s, vol=104)
    tu = c.tuba(s, vol=104)
    for b, d, notes, bass in ((1, 2, [50, 57], 38), (3, 1, [55, 59], 43), (4, 1, [57, 61], 45), (5, 4.5, [50, 57], 38)):
        tb.chord(b, d - 0.05, notes, 104)
        tu.note(b, d - 0.05, bass, 104)
    st = c.strings(s, "strings", vol=104)
    for b, d, v in ((1, 2, [62, 66, 69, 74]), (3, 1, [62, 67, 71, 74]), (4, 1, [64, 69, 73, 76]),
                    (5, 4.5, [62, 66, 69, 74, 78])):
        st.chord(b, d, v, 96)
    run = c.spiccato(s, "run", vol=100)
    for i, p in enumerate([62, 64, 66, 67, 69, 71, 73, 74]):  # scale run into the final chord
        run.note(4 + i * 0.125, 0.12, p + 12, 84 + 3 * i)
    lo = c.basses(s, "basses", vol=104)
    for b, d, p in ((1, 2, 38), (3, 1, 43), (4, 1, 45), (5, 4.5, 38)):
        lo.note(b, d, p, 100)
    cho = c.choir(s, vol=104)
    cho.chord(5, 4.5, [62, 66, 69, 74], 90)
    tm = c.timpani(s, vol=120)
    tm.note(1, 1, 38, 118)
    tm.note(3, 0.5, 43, 100)
    tm.note(4, 0.5, 45, 108)
    tm.note(5, 1, 38, 122)
    tm.roll(7.0, 9.0, 38, 50, 116, rate=8)
    tm.note(9, 2, 38, 124)
    kit = c.orch_kit(s, vol=106)
    kit.note(1, 2, 57, 112)
    kit.note(5, 3, 57, 120)
    kit.note(9, 3, 57, 118)
    kit.roll(0, 1, 38, 40, 100, rate=6)
    tk = c.taiko(s, vol=112)
    for b in (1, 5, 9):
        tk.note(b, 1, 40, 118)
    c.boom_at(s, 1, vel=0.8, duck=0)
    c.boom_at(s, 5, vel=1.0, duck=0)
    c.boom_at(s, 9, vel=0.9, duck=0)
    return s


def defeat() -> Song:
    s = Song("defeat", bpm=66, bars=2, loop=False, tail_beats=4, seed=81)
    s.master = {"hall_rt": 3.0, "target_lufs": -17.0}
    c.setup_stems(s, gains={"horns": 3.0, "str_hi": 0.0, "str_lo": 1.0, "choir": -2.0, "timp": 0.0,
                            "sub": -7.0, "low_brass": -3.0, "drone": -12.0})
    # Dm (0-2) | Bb (2-3) | Eb/Bb, Phrygian (3-4) | Dm (4-7 ring)
    hn = c.horns(s, vol=104)
    hn.mel(0, "A4:1.5 G4:0.5 | F4:1 | Eb4:1 | D4:3.5", vel=88)
    c.expr_curve(hn, s, [(0, 110), (0.9, 100), (1.9, 80)])
    pad = c.strings(s, "pad", slow=True, vol=104)
    for b, d, v in ((0, 2, [57, 62, 65, 69]), (2, 1, [58, 62, 65, 70]), (3, 1, [58, 63, 67, 70]),
                    (4, 3.5, [57, 62, 65, 69])):
        pad.chord(b, d, v, 84)
    c.expr_curve(pad, s, [(0, 100), (1, 104), (1.6, 86), (1.9, 60)])
    vc = c.celli(s, "celli", vol=104)
    for b, d, p in ((0, 2, 50), (2, 1, 46), (3, 1, 46), (4, 3.5, 38)):
        vc.note(b, d, p, 90)
    cb = c.basses(s, "basses", vol=104)
    for b, d, p in ((0, 2, 38), (2, 2, 34), (4, 3.5, 38)):
        cb.note(b, d, p, 92)
    tb = c.trombones(s, vol=100)
    tb.chord(3, 1, [46, 55], 84)
    tb.chord(4, 3.5, [38, 45, 50], 90)
    tb.ramp(4, 7.5, 110, 60)
    cho = c.choir(s, vol=100, ohh=True)
    cho.chord(3, 1, [58, 63, 67], 74)
    cho.chord(4, 3.5, [57, 62, 65], 80)
    tm = c.timpani(s, vol=120)
    tm.note(0, 1, 38, 96)
    tm.roll(3.0, 4.0, 45, 40, 104, rate=8)
    tm.note(4, 3, 38, 118)
    kit = c.orch_kit(s, vol=100)
    kit.note(4, 3, 55, 84)
    c.boom_at(s, 4, vel=0.9, duck=0, f0=60.0, f1=30.0)
    c.boom_at(s, 0, vel=0.5, duck=0, f0=60.0, f1=32.0)
    return s
