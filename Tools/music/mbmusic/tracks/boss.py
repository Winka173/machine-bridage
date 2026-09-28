"""boss: "Colossus" - heavy, dissonant, huge drums. B minor/Phrygian, 92 BPM, 48 bars.

Form (bars): A 0-7 chromatic ostinato on a B pedal, braams, war drums |
B 8-15 dissonant brass motif | C 16-23 choir, high tremolo clusters, driving
taiko 16ths | D 24-31 breakdown: metal hits, drone, distant horn calls |
E 32-43 climax | F 44-47 massive fill back into A.
"""

from __future__ import annotations

from ..score import Song
from .. import synth
from . import common as c

P1 = ["Bm", "C", "Bm", "C"]
P2 = ["G", "F", "Bm", "F#"]
P3 = ["Bm", "G", "Em", "F"]
P4 = ["Em", "F", "F#", "F#"]
CHORDS = (P1 + P1  # A 0-7
          + P1 + P2  # B 8-15
          + P2 + P3  # C 16-23
          + P3 + P4  # D 24-31
          + P1 + P2 + P1  # E 32-43
          + P4)  # F 44-47

MOTIF = ("B3:2 C4:1 B3:1 | F4:3 E4:1 | D4:2 C4:1 B3:1 | A#3:4 |"
         " G4:2 F#4:1 G4:1 | A4:2 F4:2 | F#4:3 E4:0.5 D4:0.5 | C#4:2 A#3:2")
CALL = "F#4:3 G4:1 | F#4:4 | E4:3 F4:1 | E4:4 | B3:2 C4:2 | C4:4 | C#4:4 | C#4:2 A#3:2"
# chromatic 16th ostinato, semitones above the chord root (Phrygian colour)
OST = [0, 0, 1, 0, 0, 0, 3, 1, 0, 0, 1, 0, 6, 5, 3, 1]


def ch(a: int, b: int) -> list[str]:
    return CHORDS[a:b]


def build() -> Song:
    s = Song("boss", bpm=92, bars=48, seed=51, tail_beats=16)
    s.master = {"hall_rt": 2.8, "glue": (-24.0, 2.0, 0.02, 0.25)}
    c.setup_stems(s, gains={"ost": 1.0, "str_lo": 2.0, "str_hi": -3.0, "horns": 2.0, "brass": 0.0,
                            "low_brass": 1.0, "choir": -1.0, "drums": -4.0, "snare": -4.0, "timp": -1.0,
                            "cym": -9.0, "synth": -12.0, "sub": -12.0, "fx": -10.0, "metal": -13.0,
                            "drone": -12.0, "hats": -14.0})
    B = s.bar
    bpb = s.beats_per_bar

    def pedal(k: int) -> str:
        """Section A/B/E sit on a B pedal for P1; other bars follow the chord root."""
        return "Bm" if CHORDS[k] in ("Bm", "C") else CHORDS[k]

    # --- ostinato: celli + basses + low spiccato -------------------------------------
    vc = c.celli(s, "celli", short=True, vol=110)
    cb = c.basses(s, "basses", short=True, vol=106)
    lsp = c.spiccato(s, "violas", vol=96)
    for k in list(range(0, 24)) + list(range(32, 48)):
        sym = pedal(k)
        vel = 96 if k < 8 else 104
        c.pattern_line(vc, s, k, [sym], OST, ref=47, vel=vel, accents="XxxxXxxxXxxxXxxx", dur=0.8)
        c.pattern_line(cb, s, k, [sym], OST, ref=35, vel=vel, accents="XxxxXxxxXxxxXxxx", dur=0.8)
        c.pattern_line(lsp, s, k, [sym], OST, ref=59, vel=vel - 8, accents="XxxxXxxxXxxxXxxx", dur=0.7)
    for k in range(24, 32):  # breakdown: pulsing pedal only
        c.pattern_line(cb, s, k, [CHORDS[k]], [0, None, None, None], ref=35, vel=90, dur=3.5)

    # --- brass ----------------------------------------------------------------------------------
    hn = c.horns(s, vol=106)
    tb = c.trombones(s, vol=106)
    hn.mel(B(8), MOTIF, vel=100)
    tb.mel(B(8), MOTIF, vel=100, shift=-12)
    hn.mel(B(24), CALL, vel=70)
    hn.mel(B(32), MOTIF, vel=112)
    tb.mel(B(32), MOTIF, vel=112, shift=-12)
    hn.mel(B(40), MOTIF[:MOTIF.index("A#3:4") + 5], vel=112)
    tb.mel(B(40), MOTIF[:MOTIF.index("A#3:4") + 5], vel=112, shift=-12)
    c.expr_curve(hn, s, [(0, 120), (24, 120), (24.01, 84), (31, 110), (32, 127), (48, 127)])
    tu = c.tuba(s, vol=104)
    for k in list(range(8, 24)) + list(range(32, 48)):
        tu.note(B(k), 1.9, c.ctone(pedal(k), "R", 35), 100)
        tu.note(B(k) + 2, 1.9, c.ctone(pedal(k), "R", 35), 92)
    tp = c.trumpets(s, vol=100)
    br = c.brass_section(s, vol=104)
    # dissonant stabs: root + minor second + fifth clusters on off-beats
    for k in list(range(16, 24)) + list(range(32, 44)):
        r = c.ctone(pedal(k), "R", 59)
        cl = [r, r + 1, r + 7]
        br.chord(B(k) + 1.5, 0.35, cl, 108)
        br.chord(B(k) + 3.5, 0.35, cl, 100)
        if k % 2 == 1:
            tp.chord(B(k) + 3.5, 0.4, [r + 12, r + 13], 104)
    for k in range(44, 48):  # fill: stabs on every chord change
        v = c.voicing(CHORDS[k], 62, 4)
        for off in (0, 1.5, 3):
            br.chord(B(k) + off, 0.5, v, 116)
            tp.chord(B(k) + off, 0.5, [c.ctone(CHORDS[k], "R", 72), c.ctone(CHORDS[k], "b2", 72)], 110)

    # --- choir and high strings --------------------------------------------------------------
    cho = c.choir(s, vol=108, ohh=True)
    c.pad_chords(cho, s, 16, ch(16, 24), center=57, count=3, vel=92)
    c.pad_chords(cho, s, 32, ch(32, 48), center=60, count=3, vel=100)
    cho2 = c.choir(s, "choir_hi", vol=100)
    for k in range(32, 44, 2):
        r = c.ctone(pedal(k), "R", 71)
        cho2.chord(B(k), 7.8, [r, r + 1], 84)
    tr = c.tremolo(s, vol=102)
    for k in range(16, 24):
        r = c.ctone(CHORDS[k], "R", 78)
        tr.chord(B(k), bpb, [r, r + 1, r + 6], 80)
    for k in range(24, 32):
        tr.chord(B(k), bpb, [c.ctone(CHORDS[k], "R", 66), c.ctone(CHORDS[k], "b2", 66)], 66)
    for k in range(32, 48):
        r = c.ctone(CHORDS[k], "R", 78)
        tr.chord(B(k), bpb, [r, r + 1, r + 7], 92)
    c.expr_curve(tr, s, [(16, 80), (23.9, 120), (24, 70), (31.9, 118), (32, 100), (48, 120)])

    # --- braams, drone, metal ---------------------------------------------------------------
    for k in list(range(0, 24, 2)) + list(range(32, 44, 2)):
        r = c.ctone(pedal(k), "R", 35)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 12], s.sec(5), 0.7 if k >= 8 else 0.6, open_time=0.4,
                                        seed=k + 3, bright=1.2))
    for k in range(44, 48):
        r = c.ctone(CHORDS[k], "R", 35)
        s.clip("sub", B(k), synth.braam([r, r + 7, r + 13], s.sec(3.5), 0.75, open_time=0.25, seed=k))
    s.clip("drone", B(24), synth.drone(35, s.sec(B(8)), 0.13, bright=0.5))
    for k in range(0, 48):
        if 24 <= k < 32:
            for off in (0, 1.5, 3):
                s.clip("metal", B(k) + off, synth.clang(64 if off else 59, 0.8, 1.2, seed=k % 3))
        elif k % 2 == 1:
            s.clip("metal", B(k) + 3, synth.clang(62, 1.0, 1.5, seed=1))

    # --- drums --------------------------------------------------------------------------------
    bd = c.concert_bd(s, vol=120)
    tlo = c.taiko(s, "taiko_lo", vol=118)
    thi = c.taiko(s, "taiko_hi", vol=108, pan=0.3)
    tmid = c.taiko(s, "taiko_mid", vol=108, pan=-0.3)
    kit = c.orch_kit(s, vol=104)
    tm = c.timpani(s, vol=120)
    for k in range(0, 16):
        last = k % 4 == 3
        bd.hits(k, 1, "X.......X.......", 36, vel=116)
        tlo.hits(k, 1, "X..x..x.X..x.x.." if not last else "X..x..x.X.x.xRRR", 38, vel=116)
        tmid.hits(k, 1, "....x.......x..x", 43, vel=92)
        if k >= 8:
            thi.hits(k, 1, "..x...x...x...x.", 48, vel=88)
    for k in list(range(16, 24)) + list(range(32, 44)):
        last = k % 4 == 3
        bd.hits(k, 1, "X..X..X.X..X..X.", 36, vel=114)
        tlo.hits(k, 1, "X..x..X.X..x..X.", 38, vel=114)
        thi.hits(k, 1, "xoxoXoxoxoxoXoxo" if not last else "xoxoXoxoxxxxRRRR", 48, vel=96)
        tmid.hits(k, 1, "....X.......X...", 43, vel=100)
    for k in range(24, 32):
        bd.hits(k, 1, "X...............", 36, vel=90 + 2 * (k - 24))
        tmid.hits(k, 1, "........x.....x." if k < 30 else "x...x...x.x.xxxx", 43, vel=84 + 3 * (k - 24))
    for k in range(44, 48):
        bd.hits(k, 1, "X.....X.....X...", 36, vel=120)
        tlo.hits(k, 1, "X.....X.....X.xx" if k < 47 else "X.x.X.x.RRRRRRRR", 38, vel=118)
        thi.hits(k, 1, "..xx..xx..xxRRRR", 48, vel=104)
    kit.roll(B(15), B(16), 38, 50, 110, rate=8)
    kit.roll(B(31), B(32), 38, 40, 118, rate=8)
    kit.roll(B(47), B(48), 38, 60, 120, rate=8)
    for bar in (0, 8, 16, 32, 40, 44):
        kit.note(B(bar), 3, 57, 118)
    for k in range(0, 48, 2):
        if 24 <= k < 32:
            continue
        tm.note(B(k), 1.5, c.ctone(pedal(k), "R", 43), 108)
    tm.roll(B(30), B(32), 47, 30, 120, rate=8)
    for k in range(44, 48):
        tm.note(B(k), 1, c.ctone(CHORDS[k], "R", 43), 120)
        tm.note(B(k) + 1.5, 1, c.ctone(CHORDS[k], "R", 43), 116)
        tm.note(B(k) + 3, 1, c.ctone(CHORDS[k], "R", 43), 116)
    for bb in c.pattern_beats(s, 0, 16, "X.......X.......") + c.pattern_beats(s, 16, 8, "X..X..X.X..X..X.") + \
            c.pattern_beats(s, 32, 12, "X..X..X.X..X..X.") + c.pattern_beats(s, 44, 4, "X.....X.....X..."):
        s.duck(bb, 0.8)
    c.thumps(s, c.pattern_beats(s, 32, 12, "X.......X......."), vel=0.6, f0=110.0, f1=45.0, decay=0.35)
    for bar, v in ((0, 1.1), (8, 1.0), (16, 1.1), (24, 0.8), (32, 1.25), (40, 1.1), (44, 1.0)):
        c.boom_at(s, B(bar), vel=v, f0=70.0, f1=30.0)
    for a, b in ((16, 24), (32, 48)):
        c.clip_hats(s, a, b - a, "xoxoXoxoxoxoXoxo", vel=0.7, pan_spread=0.4)
    c.riser_to(s, B(32), 8, vel=0.45, tone=0.3, tone_pitch=35)
    c.riser_to(s, B(48), 4, vel=0.4, tone=0.2, tone_pitch=35)
    c.swell_to(s, B(16), 2, vel=0.5)
    return s
