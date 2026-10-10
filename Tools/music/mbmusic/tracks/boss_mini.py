"""boss_mini: "Vanguard Hunter" - the mini bosses' track (the "mini" rank's music). B minor, 120 BPM, 52 bars.

Lighter and quicker than the main bosses' tracks: a hunting motif in short
notes over string 16ths and a snare-led groove. Form (bars): A 0-7 string
16ths, snare, taiko | B 8-23 the motif in horns, then trumpets | C 24-31
half-time: low brass answer, choir | D 32-47 climax, the motif in canon |
E 48-51 into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Bm", "G", "Bm", "F#"]
P2 = ["Em", "G", "F#sus4>F#", "F#"]
P3 = ["G", "A", "Bm", "Bm"]
P4 = ["Em", "A", "F#", "F#"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P2 + P1 + P2  # D 32-47
          + P1)  # E 48-51

MOTIF = ("B3:0.5 B3:0.5 D4:0.5 F#4:1.5 E4:0.5 D4:0.5 | D4:0.5 D4:0.5 G4:0.5 B4:1.5 A4:0.5 G4:0.5 |"
         " F#4:1 B4:1 F#4:1 D4:1 | C#4:2 A#3:2 |"
         " E4:0.5 E4:0.5 G4:0.5 B4:1.5 A4:0.5 G4:0.5 | D5:2 B4:2 | B4:2 A#4:2 | F#4:4")
ANSWER = "G3:2 B3:2 | A3:2 C#4:2 | D4:3 C#4:1 | B3:4 | G3:2 B3:2 | C#4:2 E4:2 | C#4:2 A#3:2 | F#3:4"


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def at(k: int, frac: float = 0.0) -> str:
    return c.sym_at(CHORDS[k], frac)


def build() -> Song:
    s = Song("boss_mini", bpm=120, bars=52, seed=191, tail_beats=16)
    s.master = {"hall_rt": 2.3}
    c.setup_stems(s, gains={"ost": 3.0, "str_lo": 0.0, "str_hi": -2.0, "horns": 3.0, "brass": -1.0,
                            "low_brass": 0.0, "choir": -4.0, "drums": -5.0, "snare": -2.0, "timp": -3.0,
                            "cym": -9.0, "synth": -12.0, "bass": -15.0, "sub": -11.0, "fx": -10.0,
                            "hats": -12.0, "metal": -15.0})
    B = s.bar
    drive = [(0, 24), (32, 52)]

    # --- strings -----------------------------------------------------------------------------------------
    sp = c.spiccato(s, "spic", vol=104)
    for a, b in drive:
        c.pattern_line(sp, s, a, ch(a, b), ["R", "5", "R", "8", "R", "5", "10", "5"], ref=59, vel=98,
                       accents="XxxxXxxxXxxxXxxx", dur=0.7)
    c.pattern_line(sp, s, 24, ch(24, 32), ["R", None, "5", None], ref=59, steps=8, vel=88, dur=0.8)
    vc = c.celli(s, "celli", short=True, vol=104)
    cb = c.basses(s, "basses", short=True, vol=102)
    for a, b in drive:
        c.pattern_line(vc, s, a, ch(a, b), ["R", None, "R", "R"], ref=47, steps=8, vel=96, accents="XxxxXxxx",
                       dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), ["R", None, "R", "R"], ref=35, steps=8, vel=96, accents="XxxxXxxx",
                       dur=0.8)
    hs = c.strings(s, "hi_str", slow=True, vol=92)
    c.pad_chords(hs, s, 16, ch(16, 24), center=74, count=3, vel=72)
    c.pad_chords(hs, s, 40, ch(40, 48), center=76, count=3, vel=80)

    # --- the motif -----------------------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    tp = c.trumpets(s, vol=100)
    hn.mel(B(8), MOTIF, vel=98)
    tp.mel(B(16), MOTIF, vel=100, shift=12)
    hn.mel(B(16), MOTIF, vel=96)
    hn.mel(B(32), MOTIF, vel=106)
    tp.mel(B(32) + 1, MOTIF, vel=102, shift=12)  # a beat behind: a hunting canon
    hn.mel(B(40), MOTIF, vel=108)
    tp.mel(B(40), MOTIF, vel=106, shift=12)
    c.expr_curve(hn, s, [(8, 114), (24, 100), (32, 124), (52, 124)])
    tb = c.trombones(s, vol=104)
    tu = c.tuba(s, vol=100)
    tb.mel(B(24), ANSWER, vel=104)
    tu.mel(B(24), ANSWER, vel=100, shift=-12)
    for k in range(32, 48):
        tb.chord(B(k), 1.8, [c.ctone(at(k), "R", 47), c.ctone(at(k), "5", 47)], 92)
        tu.note(B(k), 1.8, c.ctone(at(k), "R", 35), 92)
    br = c.brass_section(s, vol=98)
    for k in list(range(8, 24)) + list(range(32, 48)):
        br.chord(B(k) + 1.5, 0.3, c.voicing(at(k), 62, 4), 98)
        br.chord(B(k) + 3.5, 0.3, c.voicing(at(k, 0.9), 62, 4), 94)

    # --- choir ------------------------------------------------------------------------------------------
    cho = c.choir(s, vol=100)
    c.pad_chords(cho, s, 24, ch(24, 32), center=62, count=3, vel=84)
    c.pad_chords(cho, s, 40, ch(40, 48), center=64, count=3, vel=88)

    # --- drums ------------------------------------------------------------------------------------------------
    kit = c.orch_kit(s, vol=104)
    bd = c.concert_bd(s, vol=116)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=102, pan=0.3)
    tm = c.timpani(s, vol=116)
    for a, b in drive:
        for bar in range(a, b):
            last = bar % 4 == 3
            kit.hits(bar, 1, "x.ox.oxox.oxx.ox" if not last else "x.ox.oxoXrXrRRRR", 38, vel=96)
            bd.hits(bar, 1, "X.......X.......", 36, vel=104)
            tlo.hits(bar, 1, "X..x....X..x..x.", 40, vel=104)
            if bar >= 8:
                thi.hits(bar, 1, "....x.......x.x.", 47, vel=92)
    for bar in range(24, 32):
        bd.hits(bar, 1, "X.........X.....", 36, vel=108)
        tlo.hits(bar, 1, "X.........x.....", 40, vel=104)
        kit.hits(bar, 1, "........X.......", 38, vel=100)
    kit.roll(B(31), B(32), 38, 40, 116, rate=8)
    for bar in (8, 16, 24, 32, 40, 48):
        kit.note(B(bar), 2, 57, 112)
    for k in range(8, 52, 2):
        if 24 <= k < 32:
            continue
        tm.note(B(k), 1.4, c.ctone(at(k), "R", 42), 98)
    for bb in c.pattern_beats(s, 0, 24, "X.......X.......") + c.pattern_beats(s, 32, 20, "X.......X......."):
        s.duck(bb, 0.7)
    c.clip_hats(s, 32, 16, "xoxoXoxoxoxoXoxo", vel=0.7)
    for k in (25, 27, 29, 31):
        s.clip("metal", B(k) + 3, synth.clang(64, 0.9, 1.2, seed=k % 3))
    for bar, v in ((0, 0.8), (8, 0.9), (24, 1.0), (32, 1.1), (48, 0.8)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(32), 8, vel=0.45)
    c.riser_to(s, B(52), 4, vel=0.35)
    c.swell_to(s, B(8), 2, vel=0.45)
    return s
