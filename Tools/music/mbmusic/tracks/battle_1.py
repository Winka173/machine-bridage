"""battle_1: "Armored Advance" - driving straight 16ths. E minor, 128 BPM, 72 bars.

Form (bars): A 0-7 groove | B 8-23 horn theme x2 | C 24-31 breakdown (arp,
tremolo, horn chorale) | D 32-47 climax (trumpets + horns, choir) |
E 48-55 low-brass riff, half-time | F 56-71 theme again, fill back into A.
"""

from __future__ import annotations

from ..score import Song
from . import common as c

THEME = ("E4:0.75 E4:0.25 B4:2 A4:0.5 G4:0.5 | E4:0.75 G4:0.25 C5:2 B4:0.5 A4:0.5 |"
         " B4:0.75 B4:0.25 D5:2 C5:0.5 B4:0.5 | A4:3 F#4:1 | E4:0.75 E4:0.25 B4:2 A4:0.5 G4:0.5 |"
         " E5:2 D5:1 C5:1 | C5:1.5 B4:0.5 A4:1 C5:1 | B4:2.5 F#4:0.5 D#5:1")
CHORALE = "E4:4 | E4:4 | G4:4 | G4:4 | A4:4 | G4:4 | F#4:4 | F#4:3 D#4:1"

P1 = ["Em", "C", "G", "D"]
P2 = ["Em", "C", "Am", "B"]
P3 = ["C", "D", "Em", "Em"]
P4 = ["Am", "C", "B", "B"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P2 + P1 + P2  # D 32-47
          + P3 + P4  # E 48-55
          + P1 + P2 + P1 + P2)  # F 56-71

OST = ["R", "R", "5", "R", "R", "5", "R", "8"]
ACC332 = "XxxXxxXxXxxXxxXx"
HATS = "xoxoXoxoxoxoXoxo"


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("battle_1", bpm=128, bars=72, seed=21, tail_beats=16)
    s.master = {"hall_rt": 2.3}
    c.setup_stems(s, gains={"ost": 4.0, "str_lo": 0.0, "str_hi": -2.0, "horns": 4.0, "brass": 0.0,
                            "low_brass": -1.0, "choir": -4.0, "drums": -4.0, "snare": -3.0, "timp": -2.0,
                            "cym": -9.0, "synth": -11.0, "bass": -15.0, "sub": -10.0, "fx": -10.0, "hats": -11.0})
    B = s.bar
    groove = [(0, 8), (8, 24), (32, 48), (56, 72)]

    # --- string ostinato ----------------------------------------------------
    sp = c.spiccato(s, "spic", vol=104)
    for a, b in groove:
        vel = 94 if a == 0 else 96 if a in (8, 56) else 104
        c.pattern_line(sp, s, a, ch(a, b), OST, ref=52, vel=vel, accents=ACC332, dur=0.7)
    c.pattern_line(sp, s, 48, ch(48, 56), ["R", None, "R", None], ref=52, vel=90, dur=0.8)
    vn = c.spiccato(s, "violins", vol=96, pan=0.1)
    for a, b in [(16, 24), (32, 48), (64, 72)]:
        c.pattern_line(vn, s, a, ch(a, b), ["8", "5", "10", "5"], ref=64, vel=86, accents="Xxxx", dur=0.7)

    # --- low strings, 8ths ------------------------------------------------------
    vc = c.celli(s, "celli", short=True, vol=104)
    cb = c.basses(s, "basses", short=True, vol=104)
    for a, b in groove:
        vel = 90 if a == 0 else 96
        c.pattern_line(vc, s, a, ch(a, b), ["R"], ref=45, vel=vel, steps=8, accents="XxxXxxXx", dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), ["R"], ref=33, vel=vel, steps=8, accents="XxxXxxXx", dur=0.8)

    # --- E: low brass riff --------------------------------------------------------
    riff = ["R", None, None, "R", None, None, "R", None, "R", None, None, "R", None, None, "-5", "R"]
    tb = c.trombones(s, vol=104)
    tu = c.tuba(s, vol=100)
    c.pattern_line(tb, s, 48, ch(48, 56), riff, ref=50, vel=104, dur=2.6)
    c.pattern_line(tu, s, 48, ch(48, 56), riff, ref=38, vel=100, dur=2.6)
    c.pattern_line(vc, s, 48, ch(48, 56), riff, ref=48, vel=100, dur=2.4)
    c.pattern_line(cb, s, 48, ch(48, 56), riff, ref=38, vel=100, dur=2.4)
    # climax low brass support
    for k in range(32, 48):
        tb.chord(B(k), 3.6, [c.ctone(CHORDS[k], "R", 45), c.ctone(CHORDS[k], "5", 45)], 84)
        tu.note(B(k), 3.6, c.ctone(CHORDS[k], "R", 33), 84)

    # --- horns / trumpets -----------------------------------------------------------
    hn = c.horns(s, vol=106)
    hn.mel(B(8), THEME, vel=92)
    hn.mel(B(16), THEME, vel=100)
    hn.mel(B(24), CHORALE, vel=74)
    hn.mel(B(32), THEME, vel=104, shift=-12)
    hn.mel(B(40), THEME, vel=108, shift=-12)
    hn.mel(B(56), THEME, vel=100)
    hn.mel(B(64), THEME, vel=106)
    c.expr_curve(hn, s, [(0, 110), (24, 110), (24.01, 84), (30, 110), (32, 124), (72, 124)])
    tp = c.trumpets(s, vol=100)
    tp.mel(B(32), THEME, vel=100)
    tp.mel(B(40), THEME, vel=108)
    tp.mel(B(64), THEME, vel=100)

    # --- brass chords and stabs --------------------------------------------------------
    br = c.brass_section(s, vol=100)
    for a, b in [(8, 24), (56, 72)]:
        for k in range(a, b):
            v = c.voicing(CHORDS[k], 60, 4)
            for off in (1.5, 3.5):
                br.chord(B(k) + off, 0.3, v, 100)
    c.pad_chords(br, s, 32, ch(32, 48), center=60, count=4, vel=84)
    for k in range(48, 56):
        br.chord(B(k), 0.4, c.voicing(CHORDS[k], 62, 4), 110)
        br.chord(B(k) + 2.5, 0.4, c.voicing(CHORDS[k], 62, 4), 104)

    # --- sustained strings / choir ---------------------------------------------------------
    hs = c.strings(s, "hi_str", slow=True, vol=92)
    c.pad_chords(hs, s, 32, ch(32, 48), center=74, count=3, vel=76)
    c.pad_chords(hs, s, 64, ch(64, 72), center=74, count=3, vel=76)
    tr = c.tremolo(s, vol=100)
    c.pad_chords(tr, s, 24, ch(24, 32), center=64, count=4, vel=74)
    c.pad_chords(tr, s, 48, ch(48, 56), center=72, count=3, vel=86)
    c.expr_curve(tr, s, [(24, 70), (30, 100), (31.9, 118), (32, 80), (48, 96), (56, 120)])
    cho = c.choir(s, vol=104)
    c.pad_chords(cho, s, 24, ch(24, 32), center=62, count=3, vel=64)
    c.pad_chords(cho, s, 32, ch(32, 48), center=64, count=3, vel=86)
    c.pad_chords(cho, s, 48, ch(48, 56), center=60, count=3, vel=90)

    # --- synth layers --------------------------------------------------------------------
    for a, b in groove:
        c.clip_bass_line(s, "bass", a, ch(a, b), [None, "R", "R", "R"], ref=40, vel=0.8, gate=0.6)
    c.clip_pulse_line(s, "synth", 24, ch(24, 32), ["R", "5", "8", "10", "12", "10", "8", "5"], ref=64,
                      vel=0.7, gate=0.55, bright=0.7, vel_curve=lambda k: 0.45 + 0.07 * k)
    c.clip_pulse_line(s, "synth", 56, ch(56, 72), ["R", "5", "8", "5"], ref=64, vel=0.45, gate=0.5, bright=0.6)

    # --- drums ----------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=118)
    tlo = c.taiko(s, "taiko_lo", vol=116)
    thi = c.taiko(s, "taiko_hi", vol=106, pan=0.25)
    kit = c.orch_kit(s, vol=104)
    tm = c.timpani(s, vol=118)
    bd.hits(0, 8, "X.......X.......", 36, vel=100)
    tlo.hits(0, 8, "X.....x.x.......", 40, vel=96)
    thi.hits(0, 7, "....x.......x.x.", 47, vel=84)
    thi.hits(7, 1, "....x...x.x.xxxx", 47, vel=92)
    for a, b in [(8, 24), (32, 48), (56, 72)]:
        big = a == 32
        for bar in range(a, b):
            last = (bar - a) % 4 == 3
            bd.hits(bar, 1, "X.....x.X.......", 36, vel=108 if big else 102)
            tlo.hits(bar, 1, "X..x..x.X..x..x." if big else "X..x..x.X...x.x.", 40, vel=106)
            thi.hits(bar, 1, "x.x.x.x.xxxxRRRR" if last else "..x...x...x...xx", 47, vel=94)
            kit.hits(bar, 1, "..o.X...o..oX.oo" if last else "..o.X...o..oX...", 38, vel=96)
    for bar in range(48, 56):  # half-time
        bd.hits(bar, 1, "X.........x.....", 36, vel=112)
        tlo.hits(bar, 1, "X.....x...x.....", 40, vel=108)
        kit.hits(bar, 1, "........X.......", 38, vel=104)
        thi.hits(bar, 1, "..........x.xRRR" if bar % 2 else "..............x.", 47, vel=96)
    for bar in range(24, 32, 2):  # breakdown pulses
        tlo.hits(bar, 1, "X...............", 40, vel=84)
    tlo.hits(31, 1, "X.....x.x.x.xxxx", 40, vel=96)
    kit.roll(B(31), B(32), 38, 40, 110, rate=8)
    kit.roll(B(71), B(72), 38, 50, 112, rate=8)
    for bar in (0, 8, 32, 48, 56):
        kit.note(B(bar), 2, 57, 112)
    for bar in (16, 40, 64):
        kit.note(B(bar), 2, 55, 96)
    for bar in list(range(8, 24, 4)) + list(range(32, 48, 4)) + list(range(56, 72, 4)):
        tm.note(B(bar), 1.5, c.ctone(CHORDS[bar], "R", 43), 100)
    tm.roll(B(23), B(24), 40, 50, 110)
    tm.roll(B(47), B(48), 40, 50, 115)
    tm.roll(B(55) + 2, B(56), 40, 60, 115)
    for bb in c.pattern_beats(s, 0, 24, "X.....x.X.......", chars="Xx") + \
            c.pattern_beats(s, 32, 16, "X.....x.X.......", chars="Xx") + \
            c.pattern_beats(s, 48, 8, "X.........x.....", chars="Xx") + \
            c.pattern_beats(s, 56, 16, "X.....x.X.......", chars="Xx"):
        s.duck(bb, 0.8)
    c.thumps(s, c.pattern_beats(s, 32, 16, "X.......X......."), vel=0.5)
    for a, b in groove:
        c.clip_hats(s, a, b - a, HATS, vel=0.8 if a else 0.75)
    for bar, v in ((0, 0.9), (8, 0.9), (24, 0.7), (32, 1.1), (48, 1.0), (56, 0.9)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(32), 8, vel=0.4)
    c.riser_to(s, B(72), 4, vel=0.35)
    c.swell_to(s, B(8), 2, vel=0.5)
    c.swell_to(s, B(56), 2, vel=0.5)
    return s
