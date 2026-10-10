"""boss_orbital: "Orbital Lance" - spacecraft and orbital bosses. E Lydian, 108 BPM, 48 bars.

Cold, bright and alien: the raised fourth (A#) and the flat-six turn
(C, D) over synth arps, a crystal pad, an electronic kit and the orchestra.
Form (bars): A 0-7 shimmering arps, crystal pad, sub pulse | B 8-15 the
choir states the theme | C 16-23 the beat drops: electronic kit, brass laser
stabs, string counter-line | D 24-31 breakdown: piano, pad, countdown ticks |
E 32-43 climax: brass and choir theme over everything | F 44-47 into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["E", "F#", "E", "F#"]
P2 = ["C", "D", "E", "E"]
P3 = ["G#m", "C#m", "A", "B"]
P4 = ["C", "D", "Bsus4>B", "B"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P3 + P4  # C 16-23
          + P2 + P3  # D 24-31
          + P1 + P2 + P3  # E 32-43
          + P4)  # F 44-47

THEME = ("B4:1.5 E5:0.5 F#5:2 | A#5:2 G#5:1 F#5:1 | E5:1.5 B4:0.5 G#5:2 | F#5:4 |"
         " G5:1.5 E5:0.5 C5:2 | F#5:1.5 D5:0.5 A5:2 | G#5:2 B5:2 | E5:4")
COUNTER = "D#5:2 B4:2 | E5:2 G#5:2 | E5:2 C#5:2 | D#5:4 | E5:2 G5:2 | F#5:2 A5:2 | B5:2 A5:2 | D#5:4"
ARP = ["R", "5", "8", "9", "12", "9", "8", "5"]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("boss_orbital", bpm=108, bars=48, seed=171, tail_beats=16)
    s.master = {"hall_rt": 3.2, "hall_gain": 1.05, "delay_beats": 0.75, "delay_feedback": 0.45}
    c.setup_stems(s, gains={"ost": 1.0, "str_lo": 0.0, "str_hi": -2.0, "horns": 2.0, "brass": 0.0,
                            "low_brass": -1.0, "choir": -1.0, "drums": -5.0, "timp": -3.0, "cym": -9.0,
                            "synth": -8.0, "bass": -12.0, "sub": -10.0, "fx": -8.0, "keys": 0.0,
                            "pad": -10.0, "hats": -11.0, "drone": -12.0})
    c.setup_extra(s, gains={"kit": -4.0, "lead": -5.0})
    B = s.bar
    bpb = s.beats_per_bar

    # --- arps and pads ------------------------------------------------------------------------------------
    for a, b, v in ((0, 16, 0.55), (16, 24, 0.65), (32, 48, 0.6)):
        c.clip_pulse_line(s, "synth", a, ch(a, b), ARP, ref=64, vel=v, gate=0.45, bright=0.9, decay=0.2)
    c.clip_pulse_line(s, "synth", 24, ch(24, 32), ["R", None, "12", None, "9", None, "8", None], ref=64,
                      vel=0.5, gate=0.6, bright=0.5, decay=0.4)
    crys = c.synth_lead(s, "crystal", 98, stem="pad", vol=96)  # FX 3 crystal
    c.pad_chords(crys, s, 0, ch(0, 8), center=76, count=3, vel=72)
    c.pad_chords(crys, s, 24, ch(24, 32), center=76, count=3, vel=70)
    c.pad_chords(crys, s, 44, ch(44, 48), center=76, count=3, vel=70)
    for k in list(range(0, 8, 2)) + list(range(24, 32, 2)) + list(range(32, 48, 2)):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(at(k), 60, 4), s.sec(8), 0.7 if k < 32 else 0.85,
                                               cutoff=1800 if k < 32 else 2400))
    s.clip("drone", B(44), synth.drone(28, s.sec(B(12)), 0.11, bright=0.5))

    # --- sub pulse and bass ----------------------------------------------------------------------------------
    c.clip_bass_line(s, "bass", 0, ch(0, 8), ["R", None, None, None], ref=40, vel=0.7, gate=0.9, cutoff=500)
    c.clip_bass_line(s, "bass", 8, ch(8, 24), ["R", None, "R", "R"], ref=40, vel=0.8, gate=0.6)
    c.clip_bass_line(s, "bass", 32, ch(32, 48), ["R", "R", "8", "R"], ref=40, vel=0.85, gate=0.55)
    cb = c.basses(s, "basses", vol=100)
    for k in range(8, 48):
        for frac, sym in c.split_bar(CHORDS[k]):
            cb.note(B(k) + frac * bpb, bpb / len(CHORDS[k].split(">")) - 0.1, c.ctone(sym, "R", 40),
                    80 if 24 <= k < 32 else 92)

    # --- the theme: choir, then brass -------------------------------------------------------------------------
    cho = c.choir(s, vol=106)
    cho.mel(B(8), THEME, vel=90, shift=-12)
    cho2 = c.choir(s, "choir_pad", vol=96, ohh=True)
    c.pad_chords(cho2, s, 8, ch(8, 24), center=60, count=3, vel=72)
    c.pad_chords(cho2, s, 32, ch(32, 44), center=64, count=3, vel=88)
    cho.mel(B(32), THEME, vel=100, shift=-12)
    c.expr_curve(cho, s, [(8, 110), (32, 124), (44, 124)])
    hn = c.horns(s, vol=106)
    tp = c.trumpets(s, vol=100)
    hn.mel(B(32), THEME, vel=108, shift=-12)
    tp.mel(B(32), THEME, vel=104)
    hn.mel(B(40), COUNTER[:COUNTER.index("| E5:2 G5")], vel=108, shift=-12)
    tp.mel(B(40), COUNTER[:COUNTER.index("| E5:2 G5")], vel=106)
    c.expr_curve(hn, s, [(16, 110), (32, 126), (48, 126)])
    br = c.brass_section(s, vol=102)
    for k in range(16, 24):  # laser stabs
        v = c.voicing(at(k), 62, 4)
        for off in (0, 0.75, 1.5, 3.0):
            br.chord(B(k) + off, 0.3, v if off < 3 else c.voicing(at(k, 0.9), 62, 4), 110 if off == 0 else 100)
    tb = c.trombones(s, vol=102)
    tu = c.tuba(s, vol=98)
    for k in list(range(16, 24)) + list(range(32, 44)):
        tb.chord(B(k), 3.8, [c.ctone(at(k), "R", 40), c.ctone(at(k), "5", 40)], 92)
        tu.note(B(k), 3.8, c.ctone(at(k), "R", 28), 92)

    # --- strings ------------------------------------------------------------------------------------------------
    vn = c.strings(s, "violins", vol=100)
    vn.mel(B(16), COUNTER, vel=94)
    vn.mel(B(40), COUNTER[:COUNTER.index("| E5:2 G5")], vel=100, shift=12)
    sp = c.spiccato(s, "spic", vol=96)
    c.pattern_line(sp, s, 32, ch(32, 44), ["R", "5", "8", "5"], ref=64, vel=94, accents="XxxxXxxxXxxxXxxx",
                   dur=0.7)
    hs = c.strings(s, "hi_str", slow=True, vol=90)
    c.pad_chords(hs, s, 8, ch(8, 16), center=76, count=3, vel=66)

    # --- piano and glock in the breakdown ----------------------------------------------------------------------
    pno = c.piano(s, vol=92)
    pno.mel(B(24), "G5:1.5 E5:0.5 C5:2 | F#5:1.5 D5:0.5 A5:2 | G#5:2 B5:2 | E5:4 |"
                   " D#5:2 B4:2 | E5:2 G#5:2 | E5:2 C#5:2 | D#5:4", vel=82)
    c.pad_chords(pno, s, 24, ch(24, 32), center=55, count=3, vel=60)
    gl = c.mallets(s, "glock", 9, vol=76, pan=0.3)
    c.pattern_line(gl, s, 0, ch(0, 8), ["12", None, None, "9", None, None, "8", None], ref=88, steps=8, vel=60,
                   dur=1.5)
    c.clip_ticks(s, 28, 4, "X.x.x.x.", vel=1.6)

    # --- drums: electronic kit with the orchestra ---------------------------------------------------------------
    ek = c.drum_kit(s, "ekit", 25, vol=104)  # TR-808 kit
    tlo = c.taiko(s, "taiko", vol=112)
    tm = c.timpani(s, vol=114)
    for a, b in ((16, 24), (32, 44)):
        for bar in range(a, b):
            last = bar % 4 == 3
            ek.hits(bar, 1, "X.....X...X.....", 36, vel=110)
            ek.hits(bar, 1, "....X.......X..." if not last else "....X.......XXXX", 38, vel=100)
            ek.hits(bar, 1, "x.xxx.x.x.xxx.xx", 42, vel=76)
            tlo.hits(bar, 1, "X.......X..x....", 40, vel=104)
    for bar in range(8, 16):
        ek.hits(bar, 1, "X.......X.......", 36, vel=96)
        ek.hits(bar, 1, "..x...x...x...x.", 42, vel=66)
    for bar in range(44, 48):
        ek.hits(bar, 1, "X...X...X...X...", 36, vel=100)
    ek.hits(47, 1, "....X...X.X.XXXX", 38, vel=104)
    for k in range(16, 44, 2):
        if 24 <= k < 32:
            continue
        tm.note(B(k), 1.4, c.ctone(at(k), "R", 40), 98)
    tm.roll(B(31), B(32), 40, 40, 116, rate=8)
    for bb in c.pattern_beats(s, 16, 8, "X.....X...X.....") + c.pattern_beats(s, 32, 12, "X.....X...X....."):
        s.duck(bb, 0.8)
    c.thumps(s, c.pattern_beats(s, 16, 8, "X.......X.......") + c.pattern_beats(s, 32, 12, "X.......X......."),
             vel=0.5)
    c.clip_hats(s, 32, 12, "xoxoXoxoxoxoXoxo", vel=0.6)
    for k in (16, 32, 40):
        r = c.ctone(at(k), "R", 28)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(6), 0.75, open_time=0.3, seed=k, bright=1.3))
    for bar, v in ((0, 0.7), (8, 0.8), (16, 1.1), (24, 0.7), (32, 1.2), (40, 1.0)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(16), 4, vel=0.45, f0=500.0, f1=12000.0)
    c.riser_to(s, B(32), 8, vel=0.5, f0=400.0, f1=12000.0)
    c.swell_to(s, B(8), 2, vel=0.4)
    c.swell_to(s, B(48), 4, vel=0.4)
    return s
