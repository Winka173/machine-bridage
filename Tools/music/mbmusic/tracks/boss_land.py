"""boss_land: "Iron Bastion" - land fortresses and super-heavy tanks. G harmonic minor, 76 BPM, 36 bars.

A slow, gothic march of steel with a church organ. Form (bars): A 0-7 organ
pedal and chords, anvils, a heavy 3+3+2 march in the low drums | B 8-15 the
brass chorale over low-string riffs | C 16-23 the fortress fires: choir, war
drums doubled, the Neapolitan Ab | D 24-31 climax: organ, choir and brass
together | E 32-35 the march again, into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Gm", "Eb", "Cm", "D"]
P2 = ["Gm", "Ab", "D", "D"]
P3 = ["Cm", "Gm", "Eb", "D"]
P4 = ["Cm", "Ab", "D", "D"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P1 + P2  # D 24-31
          + P4)  # E 32-35

CHORALE = "G4:2 A4:1 Bb4:1 | G4:3 Eb4:1 | Eb4:2 D4:1 C4:1 | D4:4 | G4:2 A4:1 Bb4:1 | C5:2 Ab4:2 | A4:2 F#4:2 | F#4:4"
UPPER = "Eb5:3 D5:1 | Bb4:4 | G4:2 Bb4:2 | A4:4 | D5:3 Bb4:1 | C5:4 | C5:2 A4:2 | A4:4"
RIFF = ["R", None, None, "R", None, None, "R", None, "R", None, None, "R", None, None, "-5", None]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("boss_land", bpm=76, bars=36, seed=151, tail_beats=16)
    s.master = {"hall_rt": 3.6, "hall_gain": 1.1, "glue": (-24.0, 2.0, 0.02, 0.3)}
    c.setup_stems(s, gains={"ost": 1.0, "str_lo": 2.0, "str_hi": -2.0, "horns": 2.0, "brass": 0.0,
                            "low_brass": 1.0, "choir": -1.0, "drums": -3.0, "snare": -4.0, "timp": -1.0,
                            "cym": -9.0, "sub": -11.0, "fx": -10.0, "metal": -16.0, "keys": -3.0,
                            "drone": -12.0})
    c.setup_extra(s)
    s.stem("organ", gain_db=-3.0, eq=[("hp2", 40), ("peak", 300, 1.0, -2.0), ("peak", 2500, 1.0, 1.0)],
           hall=0.5, width=1.2, mono_below=120)
    B = s.bar

    # --- organ: pedal, chords ----------------------------------------------------------------------
    org = s.part("organ", 19, stem="organ", volume=96, ens=1, human_t=0.002, human_v=2)
    ped = s.part("organ_ped", 19, stem="organ", volume=100, ens=1, human_t=0.002, human_v=2)
    c.pad_chords(org, s, 0, ch(0, 8), center=62, count=4, vel=80)
    c.pad_chords(org, s, 24, ch(24, 36), center=64, count=5, vel=92)
    for k in list(range(0, 8)) + list(range(24, 36)):
        ped.note(B(k), 3.9, c.ctone(CHORDS[k], "R", 31), 92)
        ped.note(B(k), 3.9, c.ctone(CHORDS[k], "R", 43), 84)
    org.ramp(B(0), B(1), 70, 110)
    org.ramp(B(31), B(32), 127, 96)

    # --- low strings riff -------------------------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=110)
    cb = c.basses(s, "basses", short=True, vol=108)
    for a, b, v in ((8, 16, 100), (16, 24, 106), (24, 32, 110), (32, 36, 100)):
        c.pattern_line(vc, s, a, ch(a, b), RIFF, ref=43, vel=v, dur=1.6)
        c.pattern_line(cb, s, a, ch(a, b), RIFF, ref=31, vel=v, dur=1.6)
    vla = c.spiccato(s, "violas", vol=98)
    c.pattern_line(vla, s, 16, ch(16, 32), ["R", "5", "8", "5"], ref=55, vel=92, accents="XxxxXxxxXxxxXxxx",
                   dur=0.7)

    # --- brass chorale ------------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    tb = c.trombones(s, vol=108)
    tu = c.tuba(s, vol=104)
    hn.mel(B(8), CHORALE, vel=98)
    tb.mel(B(8), CHORALE, vel=96, shift=-12)
    hn.mel(B(24), CHORALE, vel=110)
    tb.mel(B(24), CHORALE, vel=108, shift=-12)
    tp = c.trumpets(s, vol=100)
    tp.mel(B(24), UPPER, vel=104)
    c.expr_curve(hn, s, [(8, 112), (16, 104), (24, 127), (32, 120)])
    for k in range(8, 32):
        tu.note(B(k), 3.6, c.ctone(CHORDS[k], "R", 31), 98)
    br = c.brass_section(s, vol=102)
    for k in range(16, 24):
        v = c.voicing(CHORDS[k], 60, 4)
        br.chord(B(k), 0.6, v, 112)
        br.chord(B(k) + 1.5, 0.4, v, 104)
        br.chord(B(k) + 2.5, 1.2, v, 108)
    for k in range(32, 36):
        br.chord(B(k), 0.5, c.voicing(CHORDS[k], 58, 4), 104)

    # --- choir -------------------------------------------------------------------------------------------
    cho = c.choir(s, vol=106)
    c.pad_chords(cho, s, 16, ch(16, 24), center=60, count=3, vel=92)
    c.pad_chords(cho, s, 24, ch(24, 32), center=64, count=4, vel=100)
    cho.mel(B(16), UPPER, vel=90, shift=-12)
    c.expr_curve(cho, s, [(16, 104), (24, 124), (32, 90)])
    tr = c.tremolo(s, vol=98)
    c.pad_chords(tr, s, 8, ch(8, 16), center=74, count=3, vel=72)
    c.expr_curve(tr, s, [(8, 70), (15.9, 118), (16, 80)])

    # --- steel: anvils, braams ---------------------------------------------------------------------------
    for k in range(0, 36):
        for off in (0, 1.5, 3) if k < 8 or k >= 32 else (3,):
            s.clip("metal", B(k) + off, synth.clang(60 if off else 55, 0.9, 1.4, seed=(k + int(off)) % 4))
    for k in list(range(8, 32, 2)):
        r = c.ctone(CHORDS[k], "R", 31)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(6), 0.7, open_time=0.4, seed=k, bright=1.0))
    s.clip("drone", B(32), synth.drone(31, s.sec(B(12)), 0.12, bright=0.35))

    # --- drums: the march ----------------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=122)
    tlo = c.taiko(s, "taiko_lo", vol=118)
    tmid = c.taiko(s, "taiko_mid", vol=108, pan=-0.3)
    thi = c.taiko(s, "taiko_hi", vol=100, pan=0.3)
    kit = c.orch_kit(s, vol=102)
    tm = c.timpani(s, vol=120)
    march = "X..X..X.X..X..X."
    for bar in range(0, 36):
        big = 16 <= bar < 32
        last = bar % 4 == 3
        bd.hits(bar, 1, "X.....X.X.......", 36, vel=116 if big else 106)
        tlo.hits(bar, 1, march if not last else "X..X..X.X.x.xRRR", 38, vel=112 if big else 100)
        if bar >= 8:
            kit.hits(bar, 1, "....X.......X..." if not big else "....X..o....X.oo", 38, vel=96)
        if big:
            tmid.hits(bar, 1, "..x...x...x...x.", 43, vel=96)
            thi.hits(bar, 1, "xoxoxoxoxoxoxoxo" if not last else "xoxoxoxoxxxxRRRR", 48, vel=86)
    for k in range(0, 36, 1):
        tm.note(B(k), 1.4, c.ctone(CHORDS[k], "R", 43), 104 if 16 <= k < 32 else 94)
    tm.roll(B(15), B(16), 43, 40, 120, rate=8)
    kit.roll(B(23), B(24), 38, 40, 118, rate=8)
    for bar in (8, 16, 24):
        kit.note(B(bar), 3, 57, 116)
    for bb in c.pattern_beats(s, 0, 36, "X.....X.X......."):
        s.duck(bb, 0.7)
    c.thumps(s, c.pattern_beats(s, 16, 16, "X.....X.X......."), vel=0.55, f0=100.0, f1=40.0, decay=0.35)
    for bar, v in ((0, 1.0), (8, 1.0), (16, 1.2), (24, 1.25), (32, 0.9)):
        c.boom_at(s, B(bar), vel=v, f0=60.0, f1=26.0)
    c.riser_to(s, B(16), 8, vel=0.4, tone=0.3, tone_pitch=31)
    c.swell_to(s, B(24), 4, vel=0.55)
    return s
