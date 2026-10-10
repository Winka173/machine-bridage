"""boss_air: "Thunderhead" - airship and air bosses. A Dorian, 124 BPM, 56 bars.

Form (bars): A 0-7 propeller drone, 16th violins, synth arp, thunder |
B 8-15 the boss motif in horns (rising fourths, the bright Dorian sixth) |
C 16-23 the storm turns harmonic minor: choir, trumpet line, stabs |
D 24-31 above the clouds: tremolo, flute whistles, a high trumpet call |
E 32-47 climax | F 48-55 the storm again, into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Am", "D", "Am", "D"]
P2 = ["C", "G", "D", "Em"]
P3 = ["F", "G", "Am", "Esus4>E"]
P4 = ["Am", "D", "F", "E"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P2 + P3  # D 24-31
          + P1 + P2 + P1 + P4  # E 32-47
          + P3 + P4)  # F 48-55

MOTIF = "A3:1 D4:1 E4:2 | F#4:1.5 E4:0.5 D4:2 | A3:1 D4:1 E4:1 G4:1 | F#4:4"
MOTIF2 = "G4:1.5 E4:0.5 C5:2 | B4:1 D5:1 G4:2 | A4:1.5 F#4:0.5 D5:2 | E5:3 B4:1"
STORM = ("C5:1 A4:1 F4:2 | D5:1 B4:1 G4:2 | E5:1.5 C5:0.5 A4:2 | A4:2 G#4:2 |"
         " A4:1 C5:1 E5:2 | F#5:2 D5:2 | F5:1 C5:1 A4:2 | G#4:4")
CALL = "G5:3 E5:1 | D5:4 | F#5:3 D5:1 | E5:4 | F5:3 E5:0.5 D5:0.5 | D5:2 B4:2 | C5:2 E5:2 | E5:4"


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("boss_air", bpm=124, bars=56, seed=131, tail_beats=16)
    s.master = {"hall_rt": 2.6, "glue": (-24.0, 2.0, 0.02, 0.25)}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 1.0, "str_hi": -2.0, "horns": 3.0, "brass": 0.0,
                            "low_brass": 0.0, "choir": -2.0, "drums": -4.0, "snare": -4.0, "timp": -2.0,
                            "cym": -8.0, "synth": -10.0, "bass": -15.0, "sub": -11.0, "fx": -8.0,
                            "hats": -12.0, "drone": -12.0, "pad": -13.0})
    c.setup_extra(s, gains={"winds": 1.0})
    B = s.bar
    drive = [(0, 24), (32, 56)]

    # --- 16th violins, celli 8ths, synth arp -----------------------------------------------------------
    vn = c.spiccato(s, "violins", vol=100, pan=0.15)
    for a, b in drive:
        c.pattern_line(vn, s, a, ch(a, b), ["8", "5", "10", "5", "12", "5", "10", "5"], ref=69, vel=92,
                       accents="XxxxXxxxXxxxXxxx", dur=0.7)
    vc = c.celli(s, "celli", short=True, vol=104)
    cb = c.basses(s, "basses", short=True, vol=102)
    for a, b in drive:
        c.pattern_line(vc, s, a, ch(a, b), ["R", "R", "5", "R"], ref=45, steps=8, vel=98, accents="XxxxXxxx",
                       dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), ["R"], ref=33, steps=8, vel=96, accents="XxxxXxxx", dur=0.8)
    c.clip_pulse_line(s, "synth", 0, ch(0, 8), ["R", "8", "5", "8", "10", "8", "5", "8"], ref=57, vel=0.6,
                      gate=0.4, bright=0.7)
    c.clip_pulse_line(s, "synth", 32, ch(32, 48), ["R", "8", "5", "8"], ref=57, vel=0.45, gate=0.4, bright=0.6)
    c.clip_bass_line(s, "bass", 32, ch(32, 48), [None, "R", "R", "R"], ref=45, vel=0.8, gate=0.6)

    # --- the propeller drone (a low pulse that never stops) -----------------------------------------
    s.clip("drone", B(0), synth.drone(33, s.sec(B(24)), 0.12, bright=0.45))
    s.clip("drone", B(32), synth.drone(33, s.sec(B(24)), 0.12, bright=0.45))
    s.clip("drone", B(24), synth.drone(36, s.sec(B(8)), 0.1, bright=0.3, seed=7))

    # --- horns, trumpets, brass -------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    hn.mel(B(8), MOTIF, vel=96)
    hn.mel(B(12), MOTIF2, vel=100)
    hn.mel(B(32), MOTIF, vel=106, shift=12)
    hn.mel(B(36), MOTIF2, vel=108)
    hn.mel(B(40), MOTIF, vel=108, shift=12)
    hn.mel(B(44), STORM[STORM.index("A4:1 C5"):], vel=110, shift=-12)
    c.expr_curve(hn, s, [(8, 112), (24, 112), (24.01, 90), (31, 112), (32, 126), (56, 126)])
    tb = c.trombones(s, vol=104)
    tb.mel(B(8), MOTIF, vel=94, shift=-12)
    tb.mel(B(32), MOTIF, vel=104)
    tb.mel(B(40), MOTIF, vel=106)
    tu = c.tuba(s, vol=100)
    for k in list(range(16, 24)) + list(range(48, 56)):
        tu.note(B(k), 1.9, c.ctone(at(k), "R", 33), 98)
        tu.note(B(k) + 2, 1.9, c.ctone(at(k, 0.6), "R", 33), 92)
    tp = c.trumpets(s, vol=100)
    tp.mel(B(16), STORM, vel=100)
    tp.mel(B(48), STORM, vel=106)
    tp.mel(B(24), CALL, vel=84)
    tp.mel(B(36), MOTIF2, vel=104, shift=12)
    br = c.brass_section(s, vol=100)
    for k in list(range(16, 24)) + list(range(48, 56)):
        v1, v2 = c.voicing(at(k), 60, 4), c.voicing(at(k, 0.6), 60, 4)
        br.chord(B(k) + 0.5, 0.3, v1, 104)
        br.chord(B(k) + 1.5, 0.3, v1, 100)
        br.chord(B(k) + 3, 0.6, v2, 108)
    c.pad_chords(br, s, 32, ch(32, 48), center=60, count=4, vel=84)

    # --- choir, tremolo, flutes ---------------------------------------------------------------------------
    cho = c.choir(s, vol=104)
    c.pad_chords(cho, s, 16, ch(16, 24), center=62, count=3, vel=86)
    c.pad_chords(cho, s, 24, ch(24, 32), center=64, count=3, vel=70)
    c.pad_chords(cho, s, 40, ch(40, 56), center=64, count=3, vel=94)
    c.expr_curve(cho, s, [(16, 100), (24, 80), (31.9, 116), (40, 108), (56, 120)])
    tr = c.tremolo(s, vol=96)
    c.pad_chords(tr, s, 24, ch(24, 32), center=76, count=3, vel=78)
    c.expr_curve(tr, s, [(24, 70), (31.9, 124), (32, 70)])
    fl = c.wind(s, "flutes", 73, vol=92, pan=0.25, ens=2)
    c.pattern_line(fl, s, 24, ch(24, 32), ["12", None, "10", None, "8", None, None, None], ref=81, steps=8,
                   vel=78, dur=1.6)
    for k in range(24, 32, 4):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(at(k), 64, 4), s.sec(16), 0.7, cutoff=2200))

    # --- drums and thunder -------------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=118)
    tlo = c.taiko(s, "taiko_lo", vol=116)
    thi = c.taiko(s, "taiko_hi", vol=104, pan=0.3)
    kit = c.orch_kit(s, vol=102)
    tm = c.timpani(s, vol=118)
    for a, b in drive:
        for bar in range(a, b):
            if bar < 8:
                tlo.hits(bar, 1, "X.......X.......", 40, vel=96)
                continue
            last = bar % 4 == 3
            bd.hits(bar, 1, "X..x....X..x....", 36, vel=108)
            tlo.hits(bar, 1, "X..x..x.X..x..x." if not last else "X..x..x.X.x.xRRR", 40, vel=108)
            thi.hits(bar, 1, "..x...x...x.x.x.", 47, vel=94)
            kit.hits(bar, 1, "....X.......X..o" if not last else "....X.......XrRR", 38, vel=98)
    for bar in range(24, 32):
        tlo.hits(bar, 1, "X...............", 40, vel=80)
    kit.roll(B(31), B(32), 38, 30, 118, rate=8)
    kit.roll(B(55) + 2, B(56), 38, 40, 110, rate=8)
    for bar in (8, 16, 32, 40, 48):
        kit.note(B(bar), 3, 57, 116)
    for k in range(8, 56, 2):
        if 24 <= k < 32:
            continue
        tm.note(B(k), 1.5, c.ctone(at(k), "R", 45), 104)
    tm.roll(B(15), B(16), 45, 50, 118, rate=8)
    for bb in c.pattern_beats(s, 8, 16, "X..x....X..x....") + c.pattern_beats(s, 32, 24, "X..x....X..x...."):
        s.duck(bb, 0.75)
    c.thumps(s, c.pattern_beats(s, 32, 16, "X.......X......."), vel=0.5)
    c.clip_hats(s, 32, 24, "xoxoXoxoxoxoXoxo", vel=0.7)
    for bar, v in ((0, 1.0), (4, 0.7), (16, 1.1), (24, 0.9), (32, 1.2), (44, 0.9), (48, 1.1)):  # thunder
        c.boom_at(s, B(bar), vel=v, f0=55.0, f1=26.0, dur=4.0, noise=0.6)
    c.riser_to(s, B(16), 4, vel=0.4)
    c.riser_to(s, B(32), 8, vel=0.5)
    c.swell_to(s, B(8), 2, vel=0.5)
    c.swell_to(s, B(56), 2, vel=0.45)
    return s
