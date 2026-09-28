"""siege: "Hold the Line" - tense and building (fortress defence / Endless). F minor, 108 BPM, 52 bars.

Form (bars): A 0-7 clock ticks, low ostinato, timpani, soft snare |
B 8-15 horn alarm calls, taiko, low choir | C 16-23 build: violin 16ths,
brass swells, Neapolitan (Gb) lift | D 24-39 full theme | E 40-47 peak push,
rising brass line and riser | F 48-51 pull back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Fm", "Db", "Ab", "C"]
P2 = ["Fm", "Db", "Bbm", "C"]
P3 = ["Db", "Eb", "Fm", "Fm"]
P4 = ["Gb", "Ab", "C", "C"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2 + P1 + P2  # D 24-39
          + P3 + P4  # E 40-47
          + P1)  # F 48-51

CALL = "C5:2 F4:2 | r:4 | C5:2 F4:1 Ab4:1 | G4:4 | C5:2 F4:2 | r:4 | Db5:2 Bb4:1 F4:1 | E4:4"
THEME = ("C5:3 F4:1 | F5:2 Eb5:1 Db5:1 | C5:2 Ab4:1 Bb4:1 | G4:2 E4:2 |"
         " C5:3 F4:1 | Ab5:2 F5:1 Db5:1 | Db5:2 F5:1 Bb4:1 | C5:4")
RISE = "Ab4:4 | Bb4:4 | C5:4 | C5:4 | Db5:4 | Eb5:4 | E5:4 | E5:4"
LOW_OST = ["R", "R", "8", "R", "R", "R", "6", "5"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("siege", bpm=108, bars=52, seed=61, tail_beats=16)
    s.master = {"hall_rt": 2.6}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 2.0, "str_hi": -2.0, "horns": 3.0, "brass": -1.0,
                            "low_brass": -1.0, "choir": -3.0, "drums": -5.0, "snare": 2.0, "timp": 0.0,
                            "cym": -9.0, "synth": -12.0, "sub": -11.0, "fx": -10.0, "hats": 5.0,
                            "drone": -13.0, "bass": -17.0})
    B = s.bar

    # --- clock ticks (whole piece, thinner in D) --------------------------------------
    c.clip_ticks(s, 0, 24, "XxxxXxxx", vel=0.7)
    c.clip_ticks(s, 24, 16, "X...X...", vel=0.4)
    c.clip_ticks(s, 40, 12, "XxxxXxxx", vel=0.7)

    # --- low ostinato (8ths) --------------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=106)
    cb = c.basses(s, "basses", short=True, vol=104)
    for a, b, v in ((0, 8, 94), (8, 16, 96), (16, 24, 98), (24, 40, 104), (40, 48, 108), (48, 52, 94)):
        c.pattern_line(vc, s, a, ch(a, b), LOW_OST, ref=41, vel=v, steps=8, accents="XxxxXxxx", dur=0.85)
        c.pattern_line(cb, s, a, ch(a, b), ["R"], ref=32, vel=v, steps=8, accents="XxxxXxxx", dur=0.85)
    c.clip_bass_line(s, "bass", 24, ch(24, 48), ["R", None, "R", None], ref=41, vel=0.8, gate=0.7, steps=8)

    # --- violins build ---------------------------------------------------------------------
    vn = c.spiccato(s, "violins", vol=100)
    c.pattern_line(vn, s, 16, ch(16, 24), ["8", "5", "10", "5"], ref=65, vel=80, accents="Xxxx", dur=0.7,
                   vel_curve=lambda k: 76 + 4 * k)
    c.pattern_line(vn, s, 24, ch(24, 40), ["8", "5", "10", "5"], ref=65, vel=96, accents="Xxxx", dur=0.7)
    c.pattern_line(vn, s, 40, ch(40, 48), ["8", "5", "10", "12"], ref=65, vel=104, accents="Xxxx", dur=0.7)
    pad = c.strings(s, "pad", slow=True, vol=96)
    c.pad_chords(pad, s, 0, CHORDS, center=60, count=4, vel=76)
    c.expr_curve(pad, s, [(0, 84), (8, 92), (16, 96), (23, 118), (24, 104), (40, 112), (47.9, 124), (48, 94),
                          (52, 84)])
    tr = c.tremolo(s, vol=100)
    c.pad_chords(tr, s, 40, ch(40, 48), center=76, count=3, vel=86)
    c.expr_curve(tr, s, [(40, 80), (47.9, 124)])

    # --- horns / brass ------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    hn.mel(B(8), CALL, vel=90)
    hn.mel(B(24), THEME, vel=100, shift=-12)
    hn.mel(B(32), THEME, vel=104, shift=-12)
    hn.mel(B(40), RISE, vel=108)
    tp = c.trumpets(s, vol=100)
    tp.mel(B(24), THEME, vel=96)
    tp.mel(B(32), THEME, vel=104)
    br = c.brass_section(s, vol=100)
    for k in range(16, 24):  # swells
        br.chord(B(k), 3.9, c.voicing(CHORDS[k], 58, 4), 90)
        br.ramp(B(k), B(k) + 3.8, 40, 120, curve=2.0)
    br.cc(B(24), 11, 110)
    c.pad_chords(br, s, 24, ch(24, 40), center=58, count=4, vel=82)
    for k in range(40, 48):
        for off in (0, 1.5, 3):
            br.chord(B(k) + off, 0.4, c.voicing(CHORDS[k], 60, 4), 108)
    br.cc(B(40), 11, 120)
    tb = c.trombones(s, vol=100)
    tu = c.tuba(s, vol=100)
    for k in range(24, 48):
        tb.chord(B(k), 3.8, [c.ctone(CHORDS[k], "R", 45), c.ctone(CHORDS[k], "5", 45)], 86 if k < 40 else 100)
        tu.note(B(k), 3.8, c.ctone(CHORDS[k], "R", 34), 90 if k < 40 else 104)

    # --- choir ------------------------------------------------------------------------------------
    cho = c.choir(s, vol=104, ohh=True)
    c.pad_chords(cho, s, 8, ch(8, 24), center=55, count=3, vel=74)
    cho2 = c.choir(s, "choir_ah", vol=104)
    c.pad_chords(cho2, s, 24, ch(24, 48), center=63, count=3, vel=88)

    # --- synth pulse + drone ---------------------------------------------------------------------
    c.clip_pulse_line(s, "synth", 0, ch(0, 24), ["R", "R", "8", "R"], ref=53, vel=0.5, gate=0.45, bright=0.4,
                      accents="Xoxo", vel_curve=lambda k: 0.4 + 0.012 * k)
    c.clip_pulse_line(s, "synth", 40, ch(40, 52), ["R", "R", "8", "R"], ref=53, vel=0.6, gate=0.45, bright=0.6,
                      accents="Xoxo")
    s.clip("drone", B(48), synth.drone(29, s.sec(B(28)), 0.12, bright=0.35))

    # --- drums --------------------------------------------------------------------------------------
    tm = c.timpani(s, vol=118)
    kit = c.orch_kit(s, vol=104)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=104, pan=0.3)
    bd = c.concert_bd(s, vol=116)
    for k in range(0, 52):
        r = c.ctone(CHORDS[k], "R", 41)
        if k < 24 or k >= 48:
            tm.note(B(k), 1, r, 84 if k < 16 else 96)
            tm.note(B(k) + 2, 1, r, 76 if k < 16 else 90)
        elif k % 2 == 0:
            tm.note(B(k), 1.5, r, 104)
    kit.hits(0, 8, "....x.o.....x.oo", 38, vel=80)
    kit.hits(8, 8, "..o.x.o...o.x.oo", 38, vel=80)
    for k in range(16, 24):
        kit.hits(k, 1, "x.ox.oxox.ox.oxo" if k < 22 else "XoxoXoxoXoxoRRRR", 38, vel=78 + 3 * (k - 16))
    for k in range(24, 48):
        last = k % 4 == 3
        kit.hits(k, 1, "..o.X..o..o.X.oo" if not last else "..o.X..o..rrRRRR", 38, vel=96)
    kit.hits(48, 4, "....x.o.....x.oo", 38, vel=80)
    tlo.hits(0, 8, "X.......x.......", 40, vel=84)
    tlo.hits(48, 4, "X.......x.......", 40, vel=84)
    tlo.hits(8, 8, "X.......x.....x.", 40, vel=92)
    tlo.hits(16, 8, "X.....x.x...x.x.", 40, vel=100)
    for k in range(24, 48):
        last = k % 4 == 3
        bd.hits(k, 1, "X.......X.......", 36, vel=108)
        tlo.hits(k, 1, "X..x..x.X...x.x." if k < 40 else "X..x..x.X..x..x.", 40, vel=108)
        thi.hits(k, 1, "....x..x....x.xx" if not last else "..x.x.x.xxxxRRRR", 47, vel=92)
    for bb in c.pattern_beats(s, 24, 24, "X.......X......."):
        s.duck(bb, 0.8)
    kit.roll(B(23), B(24), 38, 50, 116, rate=8)
    kit.roll(B(47), B(48), 38, 60, 118, rate=8)
    tm.roll(B(22), B(24), 41, 40, 118, rate=8)
    tm.roll(B(47), B(48), 36, 50, 118, rate=8)
    for bar in (24, 32, 40):
        kit.note(B(bar), 3, 57, 116)
    kit.note(B(48), 3, 55, 90)
    for bar, v in ((8, 0.7), (16, 0.8), (24, 1.15), (32, 1.0), (40, 1.1), (48, 0.9)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(24), 8, vel=0.4)
    c.riser_to(s, B(48), 8, vel=0.45, tone=0.3, tone_pitch=41)
    c.swell_to(s, B(40), 2, vel=0.5)
    return s
