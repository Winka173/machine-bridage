"""battle_8: "Total Offensive" - all-out attack, the fastest battle track. Bb minor, 150 BPM, 72 bars.

Form (bars): A 0-7 snare cadence, spiccato 16ths, taiko | B 8-23 dotted
trumpet fanfare | C 24-31 broad horn and choir counter-theme, the lift
through C major | D 32-39 hybrid drop: braams, synth arps, half-time |
E 40-55 climax: the counter-theme with everything | F 56-63 the fanfare up
high | G 64-71 drive with a snare build back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Bbm", "Bbm", "Gb", "Ab"]
P2 = ["Ebm", "Gb", "F", "F"]
P3 = ["Db", "Ab", "Bbm", "Gb"]
P4 = ["Ebm", "Db", "Csus4>C", "F"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P2  # D 32-39
          + P3 + P4 + P3 + P4  # E 40-55
          + P1 + P2  # F 56-63
          + P1 + P2)  # G 64-71

FANFARE = ("Bb4:0.75 Bb4:0.25 F5:1 Bb4:0.75 Bb4:0.25 Db5:1 | C5:0.75 Bb4:0.25 Ab4:1 F4:2 |"
           " Gb4:0.75 Bb4:0.25 Db5:1 Gb5:2 | F5:1 Eb5:1 C5:2 | Eb5:0.75 Eb5:0.25 Gb5:1 Bb5:2 |"
           " Ab5:1 Gb5:1 Db5:2 | C5:3 A4:1 | C5:2 F5:2")
COUNTER = "F4:2 Ab4:2 | Eb5:3 C5:1 | Db5:2 F5:2 | Db5:3 Bb4:1 | Bb4:2 Gb4:2 | Ab4:2 F4:2 | F4:2 E4:2 | F4:4"
CADENCE = "X.xxX.x.X.xxX.xx"
OST = ["R", "R", "5", "R", "8", "R", "5", "R"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("battle_8", bpm=150, bars=72, seed=111, tail_beats=16)
    s.master = {"hall_rt": 2.0, "delay_beats": 0.5, "delay_feedback": 0.35}
    c.setup_stems(s, gains={"ost": 3.0, "str_lo": 0.0, "str_hi": -2.0, "horns": 3.0, "brass": 0.0,
                            "low_brass": -1.0, "choir": -3.0, "drums": -4.0, "snare": -2.0, "timp": -2.0,
                            "cym": -9.0, "synth": -10.0, "bass": -14.0, "sub": -10.0, "fx": -10.0,
                            "hats": -11.0, "pad": -13.0})
    B = s.bar
    drive = [(0, 32), (40, 72)]

    # --- spiccato 16ths and low strings ------------------------------------------------------------
    sp = c.spiccato(s, "spic", vol=104)
    for a, b in drive:
        c.pattern_line(sp, s, a, ch(a, b), OST, ref=58, vel=100, accents="XxxxXxxxXxxxXxxx", dur=0.7)
    c.pattern_line(sp, s, 32, ch(32, 40), ["R", None, "R", None], ref=58, vel=92, dur=0.8)
    vn = c.spiccato(s, "violins", vol=96, pan=0.15)
    for a, b in ((16, 24), (40, 56), (64, 72)):
        c.pattern_line(vn, s, a, ch(a, b), ["8", "10", "12", "10"], ref=70, vel=88, accents="Xxxx", dur=0.7)
    vc = c.celli(s, "celli", short=True, vol=104)
    cb = c.basses(s, "basses", short=True, vol=104)
    for a, b in drive:
        c.pattern_line(vc, s, a, ch(a, b), ["R", "R"], ref=46, steps=8, vel=98, accents="XxXxXxXx", dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), ["R", "R"], ref=34, steps=8, vel=98, accents="XxXxXxXx", dur=0.8)
    for k in range(32, 40):
        vc.note(B(k), 1.8, c.ctone(at(k), "R", 46), 104)
        cb.note(B(k), 1.8, c.ctone(at(k), "R", 34), 104)

    # --- the fanfare -----------------------------------------------------------------------------------
    tp = c.trumpets(s, vol=102)
    tp.mel(B(8), FANFARE, vel=100)
    tp.mel(B(16), FANFARE, vel=106)
    tp.mel(B(56), FANFARE, vel=110)
    hn = c.horns(s, vol=106)
    hn.mel(B(16), FANFARE, vel=96, shift=-12)
    hn.mel(B(24), COUNTER, vel=100)
    hn.mel(B(40), COUNTER, vel=106)
    hn.mel(B(48), COUNTER, vel=110)
    hn.mel(B(56), FANFARE, vel=104, shift=-12)
    c.expr_curve(hn, s, [(0, 120), (40, 126), (72, 126)])
    tp.mel(B(48), COUNTER, vel=104, shift=12)
    br = c.brass_section(s, vol=100)
    for a, b in ((8, 24), (56, 64)):
        for k in range(a, b):
            v = c.voicing(at(k), 62, 4)
            br.chord(B(k) + 1.5, 0.3, v, 100)
            br.chord(B(k) + 3.5, 0.3, v, 96)
    c.pad_chords(br, s, 40, ch(40, 56), center=60, count=4, vel=88)
    tb = c.trombones(s, vol=102)
    tu = c.tuba(s, vol=100)
    tb.mel(B(24), COUNTER, vel=96, shift=-12)
    for k in range(40, 56):
        tb.chord(B(k), 1.8, [c.ctone(at(k), "R", 46), c.ctone(at(k), "5", 46)], 96)
        tb.chord(B(k) + 2, 1.8, [c.ctone(at(k, 0.6), "R", 46), c.ctone(at(k, 0.6), "5", 46)], 92)
        tu.note(B(k), 3.8, c.ctone(at(k), "R", 34), 96)

    # --- choir and high strings ---------------------------------------------------------------------
    cho = c.choir(s, vol=104)
    c.pad_chords(cho, s, 24, ch(24, 32), center=62, count=3, vel=84)
    c.pad_chords(cho, s, 40, ch(40, 56), center=65, count=3, vel=94)
    hs = c.strings(s, "hi_str", slow=True, vol=92)
    c.pad_chords(hs, s, 24, ch(24, 32), center=74, count=3, vel=74)
    c.pad_chords(hs, s, 56, ch(56, 64), center=74, count=3, vel=80)

    # --- hybrid drop -----------------------------------------------------------------------------------
    c.clip_pulse_line(s, "synth", 32, ch(32, 40), ["R", "5", "8", "10", "12", "10", "8", "5"], ref=58, vel=0.7,
                      gate=0.5, bright=0.8)
    c.clip_pulse_line(s, "synth", 64, ch(64, 72), ["R", "8", "5", "8"], ref=58, vel=0.5, gate=0.45, bright=0.55,
                      vel_curve=lambda k: 0.4 + 0.04 * k)
    c.clip_bass_line(s, "bass", 32, ch(32, 40), [None, "R", "R", "R"], ref=46, vel=0.85, gate=0.6)
    for k in range(32, 40, 2):
        r = c.ctone(at(k), "R", 34)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(6), 0.7, open_time=0.3, seed=k, bright=1.1))
    for k in range(32, 40, 4):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(at(k), 62, 4), s.sec(16), 0.8, cutoff=1600))

    # --- drums --------------------------------------------------------------------------------------------
    kit = c.orch_kit(s, vol=104)
    bd = c.concert_bd(s, vol=118)
    tlo = c.taiko(s, "taiko_lo", vol=116)
    thi = c.taiko(s, "taiko_hi", vol=104, pan=0.3)
    tm = c.timpani(s, vol=116)
    for a, b in drive:
        for bar in range(a, b):
            last = bar % 4 == 3
            kit.hits(bar, 1, CADENCE if not last else "X.xxX.x.XrXrRRRR", 38, vel=96)
            bd.hits(bar, 1, "X.......X.......", 36, vel=104)
            tlo.hits(bar, 1, "X..x..x.X..x..x.", 40, vel=104)
            if 24 <= bar < 32 or 40 <= bar < 56:
                thi.hits(bar, 1, "x.x.x.x.x.x.xxxx" if last else "..x...x...x...x.", 47, vel=94)
    for bar in range(32, 40):
        bd.hits(bar, 1, "X.........X.....", 36, vel=112)
        tlo.hits(bar, 1, "X.........x.....", 40, vel=110)
        kit.hits(bar, 1, "........X.......", 38, vel=106)
        s.clip("snare", B(bar) + 2, synth.clap(), gain=0.6)
    kit.roll(B(31), B(32), 38, 40, 118, rate=8)
    kit.roll(B(39), B(40), 38, 40, 118, rate=8)
    kit.roll(B(70), B(72), 38, 30, 116, rate=8)
    for bar in (0, 8, 24, 32, 40, 48, 56):
        kit.note(B(bar), 2, 57, 114)
    for k in range(8, 72, 2):
        if 32 <= k < 40:
            continue
        tm.note(B(k), 1.4, c.ctone(at(k), "R", 41), 100)
    for bb in c.pattern_beats(s, 0, 32, "X.......X.......") + c.pattern_beats(s, 40, 32, "X.......X.......") + \
            c.pattern_beats(s, 32, 8, "X.........X....."):
        s.duck(bb, 0.75)
    c.thumps(s, c.pattern_beats(s, 32, 8, "X.........X....."), vel=0.6)
    for a, b in ((32, 40), (40, 56)):
        c.clip_hats(s, a, b - a, "xoxoXoxoxoxoXoxo", vel=0.75)
    for bar, v in ((0, 0.9), (8, 0.9), (24, 1.0), (32, 1.2), (40, 1.1), (56, 1.0)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(32), 8, vel=0.45)
    c.riser_to(s, B(40), 4, vel=0.4)
    c.riser_to(s, B(72), 8, vel=0.4)
    c.swell_to(s, B(24), 2, vel=0.5)
    return s
