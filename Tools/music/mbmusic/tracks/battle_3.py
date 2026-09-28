"""battle_3: "Air Superiority" - hybrid electronic/orchestral. G minor, 138 BPM, 80 bars.

Form (bars): A 0-7 arp + kick + hats | B 8-23 string 8ths, synth-brass theme |
C 24-31 half-time braams and choir | D 32-47 full theme (trumpets/horns),
four-on-the-floor | E 48-55 filtered breakdown + riser | F 56-71 climax with
string counter-melody | G 72-79 half-time turnaround back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Gm", "Eb", "Bb", "F"]
P2 = ["Gm", "Eb", "Cm", "D"]
P3 = ["Eb", "F", "Gm", "Gm"]
P4 = ["Cm", "Eb", "D", "D"]
CHORDS = (P1 + P2  # A 0-7
          + P1 + P2 + P1 + P2  # B 8-23
          + P3 + P4  # C 24-31
          + P1 + P2 + P1 + P2  # D 32-47
          + P3 + P4  # E 48-55
          + P1 + P2 + P1 + P2  # F 56-71
          + P3 + P4)  # G 72-79

THEME = ("G4:0.75 Bb4:0.75 D5:1.5 C5:0.5 Bb4:0.5 | G4:0.75 Bb4:0.75 Eb5:1.5 D5:0.5 C5:0.5 |"
         " D5:0.75 F5:0.75 F5:1 Eb5:0.5 D5:1 | C5:3 A4:1 | G4:0.75 Bb4:0.75 D5:1.5 C5:0.5 Bb4:0.5 |"
         " G5:1.5 F5:0.5 Eb5:1 D5:1 | C5:0.75 Eb5:0.75 G5:1.5 F5:0.5 Eb5:0.5 | D5:2 F#5:1 A5:1")
COUNTER = "Bb5:4 | G5:4 | F5:4 | A5:4 | Bb5:4 | Bb5:4 | G5:4 | A5:2 F#5:2"
ARP = ["R", "5", "8", "10", "8", "5", "R", "5", "8", "10", "12", "10", "8", "5", "8", "10"]
HATS = "xoXoxoXoxoXoxoXx"


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("battle_3", bpm=138, bars=80, seed=41, tail_beats=16)
    s.master = {"hall_rt": 2.1, "delay_beats": 0.75, "delay_feedback": 0.38}
    c.setup_stems(s, gains={"ost": 2.0, "str_lo": 0.0, "str_hi": -1.0, "horns": 2.0, "brass": -1.0,
                            "low_brass": -2.0, "choir": -3.0, "drums": -4.0, "snare": -3.0, "timp": -3.0,
                            "cym": -9.0, "synth": -8.0, "bass": -15.0, "sub": -12.0, "fx": -10.0, "hats": -11.0,
                            "pad": -12.0, "keys": 2.0},
                  synth={"duck": 0.5, "delay": 0.22})
    B = s.bar
    four = [(0, 8), (32, 48), (56, 72)]
    half = [(24, 32), (72, 80)]

    # --- synth arp, bass, pad ---------------------------------------------------
    for a, b in [(0, 24), (32, 48), (56, 72)]:
        c.clip_pulse_line(s, "synth", a, ch(a, b), ARP, ref=67, vel=0.62 if a == 0 else 0.55, gate=0.55,
                          bright=0.75, decay=0.1, accents="XoxoXoxoXoxoXoxo")
    c.clip_pulse_line(s, "synth", 48, ch(48, 56), ARP, ref=67, vel=0.6, gate=0.5, steps=16, accents="XoxoXoxoXoxoXoxo",
                      bright=0.3, decay=0.08, vel_curve=lambda k: 0.45 + 0.05 * k)
    for a, b in four + [(8, 24)]:
        c.clip_bass_line(s, "bass", a, ch(a, b), [None, "R", "R", "R"], ref=43, vel=0.8, gate=0.6, cutoff=1100)
    for a, b in half:
        c.clip_bass_line(s, "bass", a, ch(a, b), ["R", None, None, None, None, None, None, None,
                                                   "R", None, None, "R", None, None, "8", None], ref=43, vel=0.9,
                         gate=1.8)
    for k in range(48, 56, 2):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(CHORDS[k], 62, 4), s.sec(8), 0.9, cutoff=1400))
    for k in range(0, 8, 2):
        s.clip("pad", B(k), synth.supersaw_pad(c.voicing(CHORDS[k], 62, 3), s.sec(8), 0.6, cutoff=1100))

    # --- strings ------------------------------------------------------------------------
    sp = c.spiccato(s, "spic", vol=102)
    for a, b in [(8, 24), (32, 48), (56, 72)]:
        c.pattern_line(sp, s, a, ch(a, b), ["R", "5", "8", "5"], ref=55, vel=90 if a == 8 else 98, steps=8,
                       accents="XxxX", dur=0.75)
    vc = c.celli(s, "celli", short=True, vol=104)
    cb = c.basses(s, "basses", short=True, vol=100)
    for a, b in [(8, 24), (32, 48), (56, 72)]:
        c.pattern_line(vc, s, a, ch(a, b), ["R"], ref=45, vel=92, steps=8, accents="XxXx", dur=0.8)
        c.pattern_line(cb, s, a, ch(a, b), ["R"], ref=36, vel=92, steps=8, accents="XxXx", dur=0.8)
    hs = c.strings(s, "counter", vol=100)
    hs.mel(B(56), COUNTER, vel=88)
    hs.mel(B(64), COUNTER, vel=96)
    c.expr_curve(hs, s, [(56, 100), (64, 116), (72, 116)])
    tr = c.tremolo(s, vol=100)
    for a, b in half:
        c.pad_chords(tr, s, a, ch(a, b), center=67, count=4, vel=86)

    # --- brass ------------------------------------------------------------------------------
    sb = c.synth_brass(s, vol=96)
    sb.mel(B(8), THEME, vel=90)
    sb.mel(B(16), THEME, vel=96)
    hn = c.horns(s, vol=104)
    hn.mel(B(16), THEME, vel=92, shift=-12)
    hn.mel(B(32), THEME, vel=102, shift=-12)
    hn.mel(B(40), THEME, vel=106, shift=-12)
    hn.mel(B(56), THEME, vel=104, shift=-12)
    hn.mel(B(64), THEME, vel=108, shift=-12)
    tp = c.trumpets(s, vol=100)
    tp.mel(B(32), THEME, vel=100)
    tp.mel(B(40), THEME, vel=106)
    tp.mel(B(64), THEME, vel=104)
    br = c.brass_section(s, vol=100)
    for a, b in [(8, 24), (56, 64)]:
        for k in range(a, b):
            br.chord(B(k) + 1.5, 0.3, c.voicing(CHORDS[k], 60, 4), 96)
            br.chord(B(k) + 3.0, 0.3, c.voicing(CHORDS[k], 60, 4), 90)
    c.pad_chords(br, s, 32, ch(32, 48), center=60, count=4, vel=84)
    tb = c.trombones(s, vol=100)
    tu = c.tuba(s, vol=100)
    for a, b in half:
        for k in range(a, b):
            v = [c.ctone(CHORDS[k], "R", 43), c.ctone(CHORDS[k], "5", 43), c.ctone(CHORDS[k], "8", 43)]
            tb.chord(B(k), 1.8, v, 108)
            tb.chord(B(k) + 2, 1.8, v, 100)
            tu.note(B(k), 3.8, c.ctone(CHORDS[k], "R", 31), 104)
        for k in range(a, b, 2):
            r = c.ctone(CHORDS[k], "R", 31)
            s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(6), 0.55, open_time=0.5, seed=k))

    # --- choir ----------------------------------------------------------------------------------
    cho = c.choir(s, vol=104)
    for a, b in half + [(40, 48), (64, 72)]:
        c.pad_chords(cho, s, a, ch(a, b), center=62, count=3, vel=88)

    # --- piano in the breakdown ----------------------------------------------------------------
    pno = c.piano(s, vol=90)
    c.pattern_line(pno, s, 48, ch(48, 56), ["8", None, "5", None, "10", None, "5", None], ref=67, vel=74,
                   steps=8, dur=2.5)

    # --- drums ------------------------------------------------------------------------------------
    kit = c.orch_kit(s, vol=104)
    tlo = c.taiko(s, "taiko_lo", vol=114)
    thi = c.taiko(s, "taiko_hi", vol=106, pan=0.3)
    bd = c.concert_bd(s, vol=116)
    tm = c.timpani(s, vol=116)
    for a, b in four:
        kicks = c.pattern_beats(s, a, b - a, "X...X...X...X...")
        c.thumps(s, kicks, vel=0.75, f0=150.0, f1=50.0, decay=0.22)
        for bar in range(a, b):
            for off in (1, 3):
                s.clip("snare", B(bar) + off, synth.clap(), gain=0.6)
            kit.hits(bar, 1, "....X.......X...", 38, vel=90)
            last = (bar - a) % 4 == 3
            tlo.hits(bar, 1, "X.....x...x.....", 40, vel=96)
            thi.hits(bar, 1, "......x.x.xxRRRR" if last else "..x.......x...x.", 47, vel=86)
        c.clip_hats(s, a, b - a, HATS, vel=0.8)
    for bar in range(8, 24):  # B: broken beat, no four-on-the-floor
        last = (bar - 8) % 4 == 3
        c.thumps(s, c.pattern_beats(s, bar, 1, "X.....X...X....."), vel=0.7, f0=150.0, f1=50.0, decay=0.22)
        s.clip("snare", B(bar) + 1, synth.clap(), gain=0.55)
        s.clip("snare", B(bar) + 3, synth.clap(), gain=0.55)
        kit.hits(bar, 1, "....X.......X..o", 38, vel=86)
        tlo.hits(bar, 1, "X.....x...x.....", 40, vel=94)
        thi.hits(bar, 1, "..x.x.x.xxxxRRRR" if last else "..x...x.....x.x.", 47, vel=84)
    c.clip_hats(s, 8, 16, "x.X.x.X.x.X.x.XX", vel=0.7)
    for a, b in half:
        for bar in range(a, b):
            bd.hits(bar, 1, "X.......X.......", 36, vel=112)
            tlo.hits(bar, 1, "X.....x.X.....x.", 40, vel=110)
            kit.hits(bar, 1, "........X.......", 38, vel=104)
            s.clip("snare", B(bar) + 2, synth.clap(), gain=0.7)
            thi.hits(bar, 1, "..............RR" if bar % 2 else "..x.......x.....", 47, vel=94)
            s.duck(B(bar), 1.0)
            s.duck(B(bar) + 2, 0.7)
    tlo.hits(55, 1, "X.x.x.x.xxxxRRRR", 40, vel=100)
    kit.roll(B(55), B(56), 38, 40, 112, rate=8)
    kit.roll(B(79) + 2, B(80), 38, 60, 115, rate=8)
    for bar in (0, 8, 24, 32, 56, 72):
        kit.note(B(bar), 2, 57, 112)
    for bar in (16, 40, 64):
        kit.note(B(bar), 2, 55, 96)
    for bar in list(range(32, 48, 4)) + list(range(56, 72, 4)):
        tm.note(B(bar), 1.5, c.ctone(CHORDS[bar], "R", 43), 100)
    tm.roll(B(31), B(32), 43, 50, 115)
    for bar, v in ((0, 0.8), (24, 1.1), (32, 1.0), (56, 1.1), (72, 1.0)):
        c.boom_at(s, B(bar), vel=v)
    c.riser_to(s, B(56), 8, vel=0.45)
    c.riser_to(s, B(24), 4, vel=0.35)
    c.riser_to(s, B(80), 4, vel=0.3)
    c.swell_to(s, B(32), 2, vel=0.5)
    return s
