"""battle_6: "Concrete Canyon" - urban street fight, hybrid rock-orchestral. C# minor, 132 BPM, 60 bars.

Form (bars): A 0-7 synth pulse, hats, palm-muted guitar chugs | B 8-23 main
riff (two distorted guitars, pick bass, rock kit) under the string theme |
C 24-31 half-time breakdown: piano, pad, choir | D 32-47 climax: the theme in
trumpets and horns over the riff, string 16ths | E 48-55 syncopated stab
bridge | F 56-59 build back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["C#m", "A", "E", "B"]
P2 = ["C#m", "A", "F#m", "G#"]
P3 = ["A", "B", "C#m", "C#m"]
P4 = ["F#m", "A", "G#", "G#"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P2 + P1 + P2  # D 32-47
          + P3 + P4  # E 48-55
          + P1)  # F 56-59

THEME = ("G#4:1.5 E4:0.5 C#5:2 | B4:1 A4:1 E4:2 | G#4:1.5 B4:0.5 E5:2 | D#5:3 B4:1 |"
         " G#4:1.5 E4:0.5 C#5:2 | E5:1 C#5:1 A4:2 | F#4:1.5 A4:0.5 C#5:2 | B#4:2 G#4:2")
PIANO = "E5:2 C#5:2 | D#5:2 F#5:2 | E5:4 | r:4 | C#5:2 A4:2 | E5:2 C#5:2 | B#4:2 D#5:2 | G#4:4"
RIFF = "X..x.xx.X..x.xX."
CHUG = "x.xxx.xxx.xxx.xx"
STAB = "X..X..X...X.X..."


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def power(part, s: Song, bar0: int, chords: list[str], pattern: str, ref: int, vel: int) -> None:
    """Power chords (root, fifth, octave) on a 16-step pattern: 'X' rings, 'x' is palm-muted."""
    step = s.beats_per_bar / 16
    for k, sym in enumerate(chords):
        r = c.ctone(sym, "R", ref)
        for i, ch_ in enumerate(pattern):
            if ch_ == ".":
                continue
            ring = ch_ == "X"
            dur = step * (2.6 if ring else 0.55)
            part.chord(s.bar(bar0 + k) + i * step, dur, [r, r + 7, r + 12] if ring else [r, r + 7],
                       vel if ring else int(vel * 0.82))


def build() -> Song:
    s = Song("battle_6", bpm=132, bars=60, seed=91, tail_beats=16)
    s.master = {"hall_rt": 1.9, "delay_beats": 0.75, "delay_feedback": 0.35}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": -1.0, "str_hi": -1.0, "horns": 2.0, "brass": -1.0,
                            "low_brass": -3.0, "choir": -5.0, "drums": -6.0, "timp": -4.0, "cym": -10.0,
                            "synth": -10.0, "bass": -6.0, "sub": -11.0, "fx": -10.0, "keys": 3.0,
                            "pad": -12.0, "hats": -12.0})
    c.setup_extra(s, gains={"gtr": -4.0, "kit": -3.0})
    B = s.bar
    riff = [(8, 24), (32, 48)]

    # --- guitars and bass ----------------------------------------------------------------------
    g1 = c.guitar(s, "gtr_l", 30, vol=96, pan=-0.55, ens=1)
    g2 = c.guitar(s, "gtr_r", 30, vol=96, pan=0.55, ens=1)
    for a, b in riff:
        power(g1, s, a, ch(a, b), RIFF, ref=37, vel=100)
        power(g2, s, a, ch(a, b), RIFF, ref=37, vel=96)
    power(g1, s, 0, ch(0, 8), CHUG, ref=37, vel=98)
    power(g2, s, 0, ch(0, 8), CHUG, ref=37, vel=94)
    power(g1, s, 48, ch(48, 56), STAB, ref=37, vel=104)
    power(g2, s, 48, ch(48, 56), STAB, ref=37, vel=100)
    power(g1, s, 56, ch(56, 60), CHUG, ref=37, vel=104)
    power(g2, s, 56, ch(56, 60), CHUG, ref=37, vel=100)
    eb = c.e_bass(s, vol=100)
    for a, b in riff + [(4, 8), (56, 60)]:
        c.pattern_line(eb, s, a, ch(a, b), ["R", None, "R", "R", None, "R", "R", None, "R", None, "R", "R", None,
                                            "R", "8", None], ref=37, vel=100, dur=0.8)
    c.pattern_line(eb, s, 48, ch(48, 56), ["R", None, None, "R", None, None, "R", None, None, None, "R", None,
                                           "R", None, None, None], ref=37, vel=104, dur=1.6)
    c.pattern_line(eb, s, 24, ch(24, 32), ["R", None, None, None], ref=37, steps=4, vel=84, dur=3.8)

    # --- synth pulse and pad -----------------------------------------------------------------------
    c.clip_pulse_line(s, "synth", 0, ch(0, 8), ["R", "R", "8", "R", "R", "8", "R", "5"], ref=49, vel=0.6,
                      gate=0.45, bright=0.35, vel_curve=lambda k: 0.45 + 0.04 * k)
    c.clip_pulse_line(s, "synth", 24, ch(24, 32), ["R", "5", "8", "10"], ref=61, vel=0.5, gate=0.4, bright=0.6,
                      steps=16)
    for k in range(24, 32, 2):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(CHORDS[k], 62, 4), s.sec(8), 0.8, cutoff=1300))

    # --- strings ---------------------------------------------------------------------------------------
    vn = c.strings(s, "violins", vol=100)
    vn.mel(B(8), THEME, vel=88)
    vn.mel(B(16), THEME, vel=96, shift=12)
    lo = c.celli(s, "celli", vol=98)
    lo.mel(B(16), THEME, vel=90, shift=-12)
    sp = c.spiccato(s, "spic", vol=98)
    c.pattern_line(sp, s, 32, ch(32, 48), ["8", "5", "10", "5"], ref=61, steps=16,
                   accents="XxxxXxxxXxxxXxxx", vel=96, dur=0.7)
    c.pattern_line(sp, s, 56, ch(56, 60), ["R", "5", "8", "5"], ref=61, steps=16,
                   accents="XxxxXxxxXxxxXxxx", vel=96, dur=0.7, vel_curve=lambda k: 90 + 4 * k)
    c.pattern_line(lo, s, 0, ch(0, 8), ["R"], ref=49, steps=1, vel=84, dur=0.98)
    hs = c.strings(s, "hi_str", slow=True, vol=92)
    c.pad_chords(hs, s, 0, ch(0, 8), center=68, count=3, vel=66)
    c.pad_chords(hs, s, 56, ch(56, 60), center=70, count=3, vel=82)
    c.pad_chords(hs, s, 24, ch(24, 32), center=68, count=3, vel=70)
    c.pad_chords(hs, s, 32, ch(32, 48), center=74, count=3, vel=78)

    # --- brass ---------------------------------------------------------------------------------------------
    tp = c.trumpets(s, vol=100)
    hn = c.horns(s, vol=104)
    tp.mel(B(32), THEME, vel=102)
    tp.mel(B(40), THEME, vel=108)
    hn.mel(B(32), THEME, vel=100, shift=-12)
    hn.mel(B(40), THEME, vel=104, shift=-12)
    c.expr_curve(hn, s, [(0, 120), (48, 124)])
    br = c.brass_section(s, vol=98)
    for k in range(48, 56):
        v = c.voicing(CHORDS[k], 62, 4)
        for i, ch_ in enumerate(STAB):
            if ch_ == "X":
                br.chord(B(k) + i * 0.25, 0.35, v, 108)
    tb = c.trombones(s, vol=100)
    for k in range(32, 48):
        tb.chord(B(k), 3.6, [c.ctone(CHORDS[k], "R", 49), c.ctone(CHORDS[k], "5", 49)], 82)

    # --- piano and choir in the breakdown ---------------------------------------------------------------
    pno = c.piano(s, vol=92)
    pno.mel(B(24), PIANO, vel=84)
    c.pad_chords(pno, s, 24, ch(24, 32), center=57, count=3, vel=62, beats=4)
    cho = c.choir(s, vol=96)
    c.pad_chords(cho, s, 28, ch(28, 32), center=62, count=3, vel=72)
    c.pad_chords(cho, s, 40, ch(40, 48), center=64, count=3, vel=84)

    # --- kit ----------------------------------------------------------------------------------------------
    kit = c.drum_kit(s, "rock", 0, vol=104)
    for bar in range(0, 8):
        kit.hits(bar, 1, "x.x.x.x.x.x.x.x.", 42, vel=84 + 2 * bar)
        kit.hits(bar, 1, "X...X...X...X..." if bar >= 4 else "X.......X.......", 36, vel=100)
        if bar >= 4:
            kit.hits(bar, 1, "....x.......x...", 37, vel=80)
    for a, b in riff:
        for bar in range(a, b):
            last = bar % 4 == 3
            kit.hits(bar, 1, "X.....x.X.x...x." if not last else "X.....x.X.x.....", 36, vel=112)
            kit.hits(bar, 1, "....X.......X..." if not last else "....X.......XxXX", 38, vel=112)
            kit.hits(bar, 1, "x.x.x.x.x.x.x.x.", 42 if a == 8 else 51, vel=86)  # hats in B, ride in D
    for bar in range(24, 32):
        kit.hits(bar, 1, "X.........x.....", 36, vel=96)
        kit.hits(bar, 1, "........X.......", 38, vel=98)
        kit.hits(bar, 1, "x...x...x...x...", 42, vel=70)
    for bar in range(48, 56):
        kit.hits(bar, 1, STAB, 36, vel=110)
        kit.hits(bar, 1, "....X.......X...", 38, vel=108)
        kit.hits(bar, 1, "x.x.x.x.x.x.x.x.", 46, vel=70)
    for bar in range(56, 60):
        kit.hits(bar, 1, "X...X...X...X...", 36, vel=100 + 3 * (bar - 56))
        kit.hits(bar, 1, "....X.......X..." if bar < 59 else "X.X.X.X.XXXXXXXX", 38, vel=100)
    kit.hits(31, 1, "............XXXX", 45, vel=104)
    kit.hits(47, 1, "........XX..XXXX", 47, vel=108)
    for bar in (8, 16, 32, 40, 48):
        kit.note(B(bar), 2, 49, 112)
    tlo = c.taiko(s, "taiko", vol=110)
    for bar in range(32, 48):
        tlo.hits(bar, 1, "X.......X..x....", 40, vel=100)
    for bar in range(56, 60):
        tlo.hits(bar, 1, "X.x.X.x.X.x.X.x." if bar < 59 else "X.x.X.x.XxXxRRRR", 40, vel=96 + 4 * (bar - 56))
    br.ramp(B(56), B(60), 60, 120)
    for k in range(56, 60):
        br.chord(B(k), 3.9, c.voicing(CHORDS[k], 60, 4), 96)
    for bb in c.pattern_beats(s, 8, 16, "X.....x.X.x...x.") + c.pattern_beats(s, 32, 16, "X.....x.X.x...x."):
        s.duck(bb, 0.6)
    c.clip_hats(s, 32, 16, "..x...x...x...x.", vel=0.5)
    for bar, v in ((8, 0.9), (24, 0.8), (32, 1.1), (48, 1.0)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(32), 8, vel=0.45)
    c.riser_to(s, B(60), 4, vel=0.35)
    c.swell_to(s, B(8), 2, vel=0.45)
    return s
