"""Prompt 34 L6: the tiered battle sounds, synthesised offline (no recordings, no AI audio).

    python Tools/sfx/build_sfx.py              # every bank -> Assets/MachineBrigade/Resources/Audio/p34/<bank>/<bank>_<n>.ogg
    python Tools/sfx/build_sfx.py shot_t5 wreck_ship   # only these banks
    python Tools/sfx/build_sfx.py --list       # the banks, their variants and lengths

Same way as Tools/music: numpy and scipy write the samples, soundfile encodes Ogg Vorbis (mono, 44.1 kHz). Nothing here
ships with the game; only the .ogg files do. Every clip is built from noise, sines and filters with a fixed seed, so a
rebuild gives the same files. Licence: the clips are original works of this repository (Docs/ASSET_LICENSES.md).

Each shot is THREE LAYERS PREMIXED into one clip (the prompt's "one file, not three AudioSources a shot"):
  1. the mechanism near the gun: breech, bolt or rail clank (short, bright),
  2. the report: the crack and the body of the blast, lower and longer by tier,
  3. the tail: the echo off the ground and the slap-back, long and rumbling at T4-T5 (the "rung tram").
Blasts by tier and round (HE, AP, HEAT, thermobaric), small-arms clusters (many guns as one sound), wrecks by class (tank,
wheeled, truck, artillery, aircraft, helicopter, ship, drone), trains (horn, rails loop), ships (horn, engine loop) and
crashing aircraft (the fall, the impact). Loudness: every clip is peak-normalised to -1 dBFS; the game's banks set the
levels (AudioDirector.P34).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

SR = 44100
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Audio' / 'p34'


# ------------------------------------------------------------------------------------------------------------- DSP


def n(seconds: float) -> int:
    return max(1, int(round(seconds * SR)))


def t_axis(seconds: float) -> np.ndarray:
    return np.arange(n(seconds)) / SR


def noise(rng, seconds: float) -> np.ndarray:
    return rng.standard_normal(n(seconds)).astype(np.float64)


def filt(x: np.ndarray, kind: str, f, order: int = 2) -> np.ndarray:
    """Butterworth low / high / band pass (f in Hz; a pair for band)."""
    nyq = SR * 0.5
    if kind == 'band':
        lo, hi = f
        sos = signal.butter(order, [max(10.0, lo) / nyq, min(hi, nyq * 0.98) / nyq], btype='band', output='sos')
    else:
        sos = signal.butter(order, min(max(10.0, f), nyq * 0.98) / nyq, btype='low' if kind == 'low' else 'high', output='sos')
    return signal.sosfilt(sos, x)


def sweep_low(x: np.ndarray, f0: float, f1: float, steps: int = 24) -> np.ndarray:
    """A low pass whose cutoff glides from f0 to f1 over the clip (blocks crossfaded)."""
    out = np.zeros_like(x)
    edges = np.linspace(0, len(x), steps + 1).astype(int)
    for k in range(steps):
        a, b = edges[k], edges[k + 1]
        f = f0 * (f1 / f0) ** (k / max(1, steps - 1))
        pad = min(a, 2048)
        seg = filt(x[a - pad:b], 'low', f)[pad:]
        out[a:b] = seg
    return out


def env_exp(seconds: float, decay: float, attack: float = 0.002) -> np.ndarray:
    t = t_axis(seconds)
    e = np.exp(-t / max(1e-4, decay))
    if attack > 0:
        e *= np.clip(t / attack, 0, 1)
    return e


def place(dst: np.ndarray, src: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    if i >= len(dst):
        return
    m = min(len(src), len(dst) - i)
    dst[i:i + m] += src[:m] * gain


def damped(freqs, decays, seconds: float, rng, amps=None) -> np.ndarray:
    """Inharmonic ringing (metal): damped sines with random phases."""
    t = t_axis(seconds)
    out = np.zeros_like(t)
    amps = amps or [1.0] * len(freqs)
    for f, d, a in zip(freqs, decays, amps):
        out += a * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi)) * np.exp(-t / d)
    return out


def thump(seconds: float, f0: float, f1: float, decay: float) -> np.ndarray:
    """A falling sine: the chest-thump under a big report (f0 -> f1 Hz)."""
    t = t_axis(seconds)
    f = f1 + (f0 - f1) * np.exp(-t / (decay * 0.35))
    phase = 2 * math.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t / decay) * np.clip(t / 0.004, 0, 1)


def echoes(x: np.ndarray, rng, taps, lowpass: float) -> np.ndarray:
    """Discrete slap-back echoes (delay s, gain), each duller than the dry sound."""
    total = len(x) + n(max(d for d, _ in taps) + 0.05)
    out = np.zeros(total)
    out[:len(x)] += x
    wet = filt(x, 'low', lowpass)
    for d, g in taps:
        place(out, wet * g, d + rng.uniform(-0.01, 0.01))
    return out


def fade_out(x: np.ndarray, seconds: float = 0.05) -> np.ndarray:
    k = min(len(x), n(seconds))
    x = x.copy()
    x[-k:] *= np.linspace(1, 0, k) ** 2
    return x


def finish(x: np.ndarray, peak_db: float = -1.0) -> np.ndarray:
    x = filt(x, 'high', 25)
    x = fade_out(x, 0.04)
    peak = np.max(np.abs(x)) or 1.0
    return (x / peak * 10 ** (peak_db / 20)).astype(np.float32)


def fit(x: np.ndarray, seconds: float) -> np.ndarray:
    out = np.zeros(n(seconds))
    m = min(len(x), len(out))
    out[:m] = x[:m]
    return out


# ------------------------------------------------------------------------------------------------------- the layers

# By tier (T0 .. T5): the report's body (low-pass cutoff Hz, decay s), the thump (start, end Hz, decay s, level), the tail
# (decay s, level, cutoff Hz) and the clip's length (s).
REPORT = [(6500, 0.035), (4500, 0.07), (2600, 0.16), (1700, 0.3), (1300, 0.55), (1000, 0.9)]
THUMP = [(0, 0, 0.0, 0.0), (180, 90, 0.05, 0.25), (150, 70, 0.1, 0.4), (130, 60, 0.18, 0.45), (110, 50, 0.32, 0.5), (95, 45, 0.55, 0.55)]
TAIL = [(0.08, 0.15, 2500), (0.18, 0.25, 1800), (0.4, 0.35, 1300), (0.8, 0.5, 1000), (1.6, 0.7, 800), (2.6, 0.85, 650)]
LENGTH = [0.35, 0.6, 1.1, 1.8, 3.0, 4.6]


def mechanism(rng, tier: int) -> np.ndarray:
    """Layer 1: the gun's own works near it: a bolt's clack, a breech's slam (bigger guns lower and later)."""
    seconds = 0.12 + 0.05 * tier
    x = np.zeros(n(seconds + 0.2))
    clicks = 2 if tier <= 1 else 3
    for k in range(clicks):
        at = 0.0 if k == 0 else rng.uniform(0.02, 0.06) + 0.03 * tier * k / clicks
        burst = filt(noise(rng, 0.012), 'high', 2500 - 300 * min(tier, 5)) * env_exp(0.012, 0.003)
        place(x, burst, at, 0.6 if k else 1.0)
    base = 900 / (1 + 0.45 * tier)
    ring = damped([base * 1.0, base * 1.63, base * 2.71, base * 4.13], [0.03 + 0.012 * tier] * 4, seconds, rng, [1, 0.6, 0.4, 0.25])
    place(x, ring, 0.004 + 0.01 * tier, 0.5)
    return x


def report(rng, tier: int) -> np.ndarray:
    """Layer 2: the crack and the body of the blast at the muzzle."""
    cut, decay = REPORT[tier]
    seconds = decay * 6 + 0.05
    crack = filt(noise(rng, 0.006), 'high', 1500) * env_exp(0.006, 0.0015, 0.0003)
    body = filt(noise(rng, seconds), 'low', cut, 4) * env_exp(seconds, decay, 0.0015)
    x = fit(crack, seconds) * (1.2 - 0.12 * tier) + body * 1.4
    f0, f1, d, lvl = THUMP[tier]
    if lvl > 0:
        x += thump(seconds, f0, f1, d) * lvl * 1.6
    return x


def tail(rng, tier: int) -> np.ndarray:
    """Layer 3: the echo off the ground and the slap-back; at T4-T5 a long rolling rumble."""
    decay, level, cut = TAIL[tier]
    seconds = decay * 3.5 + 0.1
    bed = filt(noise(rng, seconds), 'low', cut, 4) * env_exp(seconds, decay, 0.06) * level
    if tier >= 4:
        rumble = filt(noise(rng, seconds), 'low', 90, 4) * env_exp(seconds, decay * 1.3, 0.15)
        # Phones play little under 150 Hz: the rumble stays under the mid body, not over it.
        bed += rumble * (0.45 if tier >= 5 else 0.3)
    return bed


def gun_shot(rng, tier: int) -> np.ndarray:
    seconds = LENGTH[tier]
    x = np.zeros(n(seconds + 1.0))
    place(x, mechanism(rng, tier), 0.0, 0.35 if tier >= 3 else 0.55)
    rep = report(rng, tier)
    taps = [(0.11 + 0.03 * tier, 0.32), (0.27 + 0.05 * tier, 0.18)] + ([(0.6 + 0.15 * tier, 0.12)] if tier >= 3 else [])
    place(x, echoes(rep, rng, taps, 1800 - 220 * tier), 0.01)
    place(x, tail(rng, tier), 0.02)
    return finish(fit(x, seconds))


def launch(rng, tier: int) -> np.ndarray:
    """A rocket or missile leaving its tube: the ignition's pop and the motor's whoosh climbing away (T4-T5 a roar)."""
    seconds = 1.0 + 0.45 * tier
    x = np.zeros(n(seconds))
    place(x, filt(noise(rng, 0.02), 'band', (600, 5000)) * env_exp(0.02, 0.006), 0.0, 1.0)
    whoosh = noise(rng, seconds)
    whoosh = sweep_low(whoosh, 5000 / (1 + 0.15 * tier), 600 / (1 + 0.2 * tier))
    t = t_axis(seconds)
    shape = np.clip(t / 0.05, 0, 1) * np.exp(-t / (0.35 + 0.18 * tier))
    x += whoosh * shape * 1.2
    if tier >= 4:
        x += filt(noise(rng, seconds), 'low', 140, 4) * np.exp(-t / (0.5 + 0.2 * tier)) * np.clip(t / 0.08, 0, 1) * 1.6
    place(x, tail(rng, max(1, tier - 1)) * 0.7, 0.05)
    return finish(x)


def blast_he(rng, tier: int) -> np.ndarray:
    """A high-explosive round landing: crack, body, the earth and fragments raining back, the rumble (by tier)."""
    seconds = [0.4, 0.8, 1.5, 2.4, 3.6, 5.4][tier]
    x = np.zeros(n(seconds + 1))
    cut, decay = REPORT[min(5, tier)]
    body = filt(noise(rng, decay * 7), 'low', cut * 0.8, 4) * env_exp(decay * 7, decay * 1.3, 0.002)
    place(x, filt(noise(rng, 0.008), 'high', 1200) * env_exp(0.008, 0.002), 0.0, 1.0)
    place(x, body, 0.0, 1.6)
    f0, f1, d, lvl = THUMP[max(1, tier)]
    place(x, thump(d * 6, f0 * 0.9, f1 * 0.85, d * 1.2), 0.0, lvl * 1.8)
    # Earth and fragments coming back down: sparse dull ticks over a second or two.
    rain = int(10 + 14 * tier)
    for _ in range(rain):
        at = rng.uniform(0.15, 0.25 + 0.35 * tier)
        tick = filt(noise(rng, 0.01), 'band', (500, 3500)) * env_exp(0.01, 0.003)
        place(x, tick, at, rng.uniform(0.05, 0.18))
    place(x, tail(rng, tier), 0.03, 1.0)
    return finish(fit(x, seconds))


def blast_ap(rng, tier: int) -> np.ndarray:
    """An armour-piercing round striking: a hard metallic crack, the plate ringing, a spit of sparks."""
    seconds = 0.6 + 0.25 * tier
    x = np.zeros(n(seconds))
    place(x, filt(noise(rng, 0.005), 'high', 2500) * env_exp(0.005, 0.0012), 0.0, 1.3)
    base = 1900 / (1 + 0.25 * tier)
    ring = damped([base, base * 1.41, base * 2.23, base * 3.07, base * 4.9], [0.08 + 0.04 * tier] * 5, seconds, rng, [1, 0.8, 0.55, 0.35, 0.2])
    x += ring * 0.45
    x += filt(noise(rng, seconds), 'low', 1200, 4) * env_exp(seconds, 0.05 + 0.04 * tier) * 0.9
    sparks = filt(noise(rng, 0.25), 'high', 5000) * env_exp(0.25, 0.06)
    place(x, sparks, 0.01, 0.25)
    place(x, tail(rng, max(0, tier - 1)) * 0.6, 0.02)
    return finish(x)


def blast_heat(rng) -> np.ndarray:
    """A shaped charge: a sharp crack, the jet's hiss stabbing through, a small body."""
    seconds = 1.1
    x = np.zeros(n(seconds))
    place(x, filt(noise(rng, 0.006), 'high', 1800) * env_exp(0.006, 0.0015), 0.0, 1.3)
    place(x, filt(noise(rng, 0.18), 'band', (2500, 9000)) * env_exp(0.18, 0.05, 0.004), 0.002, 0.6)
    x += filt(noise(rng, seconds), 'low', 1700, 4) * env_exp(seconds, 0.12) * 1.2
    x += thump(seconds, 160, 60, 0.1) * 0.6
    place(x, tail(rng, 2) * 0.7, 0.02)
    return finish(x)


def blast_thermo(rng, tier: int) -> np.ndarray:
    """Thermobaric: the small pop that throws the fuel, then the ignition's long WHOOMP and roar."""
    seconds = 2.2 + 0.8 * (tier - 3)
    x = np.zeros(n(seconds))
    place(x, filt(noise(rng, 0.03), 'band', (400, 3000)) * env_exp(0.03, 0.008), 0.0, 0.5)
    roar_len = seconds - 0.15
    roar = sweep_low(noise(rng, roar_len), 220, 1300, 16)
    t = t_axis(roar_len)
    shape = np.clip(t / 0.08, 0, 1) * np.exp(-t / (0.5 + 0.25 * (tier - 3)))
    place(x, roar * shape, 0.15, 1.6)
    place(x, thump(1.4, 90, 30, 0.35), 0.15, 1.3)
    place(x, tail(rng, tier), 0.2)
    return finish(x)


def cluster(rng, guns: int) -> np.ndarray:
    """Small arms as one sound: several machine guns and rifles firing at once, near and far (prompt's "cụm")."""
    seconds = 1.6
    x = np.zeros(n(seconds + 0.5))
    for g in range(guns):
        rate = rng.uniform(9, 16)
        far = rng.uniform(0, 1)
        start = rng.uniform(0, 0.4)
        stop = rng.uniform(0.8, seconds)
        tt = start
        while tt < stop:
            rep = report(rng, 0)
            shot = rep + fit(mechanism(rng, 0), len(rep) / SR) * 0.3
            shot = filt(shot, 'low', 7000 - 5000 * far)
            place(x, shot, tt, (1.0 - 0.6 * far) * rng.uniform(0.7, 1.0))
            tt += 1.0 / rate * rng.uniform(0.85, 1.15)
    place(x, tail(rng, 1) * 0.5, 0.0)
    return finish(fit(x, seconds))


def pop_chain(rng, pops: int, spacing, tier: int, crackle: float) -> np.ndarray:
    """A chain of blasts (cargo going up, ammunition cooking off)."""
    seconds = spacing[1] * pops + 1.6
    x = np.zeros(n(seconds))
    at = 0.0
    for k in range(pops):
        place(x, blast_he(rng, tier if k == 0 else max(1, tier - 1)), at, 1.0 if k == 0 else rng.uniform(0.45, 0.75))
        at += rng.uniform(*spacing)
    for _ in range(int(40 * crackle)):
        place(x, filt(noise(rng, 0.006), 'high', 3000) * env_exp(0.006, 0.0015), rng.uniform(0.2, seconds - 0.3), rng.uniform(0.05, 0.25))
    return finish(x)


def metal_clang(rng, base: float, seconds: float, decay: float) -> np.ndarray:
    return damped([base, base * 1.52, base * 2.37, base * 3.6], [decay, decay * 0.8, decay * 0.6, decay * 0.4], seconds, rng, [1, 0.7, 0.45, 0.3])


def wreck(rng, kind: str) -> np.ndarray:
    if kind == 'tank':
        # The hull goes up, the turret is thrown with a deep clang, the fire takes hold.
        x = np.zeros(n(3.2))
        place(x, blast_he(rng, 3), 0.0, 1.0)
        place(x, metal_clang(rng, 210, 1.2, 0.35), 0.18, 0.5)
        place(x, metal_clang(rng, 160, 1.0, 0.3), 1.5, 0.35)
        place(x, filt(noise(rng, 2.2), 'band', (300, 3000)) * env_exp(2.2, 0.9, 0.3) * 0.25, 0.6)
        return finish(x)
    if kind == 'wheeled':
        # A tyre bursting, the frame crunching over, a wheel bouncing away.
        x = np.zeros(n(2.4))
        place(x, blast_he(rng, 2), 0.0, 0.9)
        place(x, filt(noise(rng, 0.05), 'band', (300, 4000)) * env_exp(0.05, 0.015), 0.12, 0.8)
        for k in range(4):
            place(x, filt(noise(rng, 0.12), 'band', (200, 1500)) * env_exp(0.12, 0.05), 0.5 + 0.18 * k, 0.5 - 0.08 * k)
        place(x, metal_clang(rng, 340, 0.6, 0.12), 0.7, 0.3)
        return finish(x)
    if kind == 'truck':
        return pop_chain(rng, 4, (0.25, 0.5), 3, 0.6)
    if kind == 'artillery':
        return pop_chain(rng, 6, (0.18, 0.4), 3, 1.0)
    if kind == 'aircraft':
        x = np.zeros(n(3.4))
        place(x, blast_he(rng, 4), 0.0, 1.0)
        for _ in range(30):
            place(x, metal_clang(rng, rng.uniform(400, 1600), 0.3, 0.05), rng.uniform(0.2, 2.2), rng.uniform(0.04, 0.12))
        return finish(x)
    if kind == 'heli':
        # The crash and the rotor blades beating themselves to pieces, slowing.
        x = np.zeros(n(3.0))
        place(x, blast_he(rng, 3), 0.0, 1.0)
        at, gap = 0.1, 0.045
        while at < 1.8:
            place(x, filt(noise(rng, 0.02), 'band', (300, 2500)) * env_exp(0.02, 0.006), at, 0.35)
            at += gap
            gap *= 1.09
        return finish(x)
    if kind == 'ship':
        # Steel groaning as the hull breaks, a deep boom, water rushing in.
        seconds = 4.5
        t = t_axis(seconds)
        x = np.zeros(n(seconds))
        groan_f = 100 + 30 * np.sin(2 * math.pi * 0.35 * t)  # steel groans in the mids too (phone speakers)
        groan = np.sin(2 * math.pi * np.cumsum(groan_f) / SR) * (0.6 + 0.4 * np.sin(2 * math.pi * 7 * t))
        x += filt(groan + 0.5 * np.sign(groan) * np.abs(groan) ** 3, 'low', 700) * np.clip(t / 0.6, 0, 1) * np.exp(-t / 2.5) * 0.9
        place(x, blast_he(rng, 4), 0.3, 0.8)
        place(x, metal_clang(rng, 95, 2.5, 0.9), 0.9, 0.4)
        water = filt(noise(rng, 3.0), 'band', (150, 2500)) * env_exp(3.0, 1.2, 0.4)
        place(x, water, 1.3, 0.5)
        return finish(x)
    if kind == 'drone':
        x = np.zeros(n(0.8))
        place(x, blast_he(rng, 1), 0.0, 1.0)
        place(x, filt(noise(rng, 0.03), 'high', 2000) * env_exp(0.03, 0.008), 0.03, 0.5)
        return finish(x)
    raise ValueError(kind)


def horn(rng, freqs, seconds: float) -> np.ndarray:
    """A horn chord: rich (sawtooth-like) tones, a soft attack, slight vibrato, a short release."""
    t = t_axis(seconds)
    x = np.zeros_like(t)
    for k, f in enumerate(freqs):
        fv = f * (1 + 0.004 * np.sin(2 * math.pi * (4.5 + 0.3 * k) * t))
        ph = 2 * math.pi * np.cumsum(fv) / SR
        x += sum(np.sin(ph * h) / h for h in range(1, 9)) * (0.9 ** k)
    a = np.clip(t / 0.08, 0, 1) * np.clip((seconds - t) / 0.25, 0, 1)
    x = filt(x, 'low', 2500) * a
    return finish(echoes(x, rng, [(0.35, 0.25), (0.8, 0.12)], 1500))


def loop_bed(x: np.ndarray, cross: float = 0.3) -> np.ndarray:
    """Makes a clip loop seamlessly: its last `cross` seconds crossfaded into its start."""
    k = n(cross)
    head, body = x[:k], x[k:].copy()
    ramp = np.linspace(0, 1, k)
    body[-k:] = body[-k:] * (1 - ramp) + head * ramp
    return body


def rails_loop(rng) -> np.ndarray:
    """A train on the rails: the clack-clack of the joints over a rolling rumble (loops)."""
    seconds = 4.3
    x = filt(noise(rng, seconds), 'low', 400, 4) * 0.35
    x += filt(noise(rng, seconds), 'band', (900, 3000)) * 0.05
    at = 0.05
    while at < seconds - 0.3:
        for pair in (0.0, 0.11):
            clack = filt(noise(rng, 0.04), 'band', (250, 2500)) * env_exp(0.04, 0.012)
            place(x, clack + metal_clang(rng, 520, 0.04, 0.015) * 0.3, at + pair, 0.9)
        at += 0.62
    return finish(loop_bed(x, 0.3))


def engine_loop(rng) -> np.ndarray:
    """A ship's engines and the sea along its hull: a low throb over wash (loops)."""
    seconds = 4.3
    t = t_axis(seconds)
    throb = np.sin(2 * math.pi * 38 * t) * (0.6 + 0.4 * np.sin(2 * math.pi * 3.5 * t)) + 0.4 * np.sin(2 * math.pi * 76 * t)
    x = filt(throb, 'low', 200) * 0.7 + filt(noise(rng, seconds), 'band', (200, 1800)) * 0.25
    return finish(loop_bed(x, 0.3))


def crash_fall(rng) -> np.ndarray:
    """A shot-down aircraft coming down: an engine's falling whine and the air tearing past."""
    seconds = 2.8
    t = t_axis(seconds)
    f = 900 * (0.35 + 0.65 * np.exp(-t / 1.4))
    whine = np.sin(2 * math.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * math.pi * np.cumsum(f) / SR)
    wind = sweep_low(noise(rng, seconds), 600, 3500, 12)
    x = whine * 0.35 * np.clip(t / 0.2, 0, 1) + wind * 0.6 * np.clip(t / 1.5, 0, 1)
    return finish(x)


def crash_impact(rng) -> np.ndarray:
    x = np.zeros(n(3.2))
    place(x, blast_he(rng, 4), 0.0, 1.0)
    for _ in range(24):
        place(x, metal_clang(rng, rng.uniform(250, 1200), 0.35, 0.06), rng.uniform(0.15, 2.0), rng.uniform(0.04, 0.12))
    return finish(x)


# ------------------------------------------------------------------------------------------------------- the banks

def banks():
    """bank name -> (variants, builder(rng, k))."""
    b = {}
    for tier in range(6):
        b[f'shot_t{tier}'] = (3, lambda rng, k, tier=tier: gun_shot(rng, tier))
    for tier in range(2, 6):
        b[f'launch_t{tier}'] = (2, lambda rng, k, tier=tier: launch(rng, tier))
    for tier in range(1, 6):
        b[f'blast_he_t{tier}'] = (3, lambda rng, k, tier=tier: blast_he(rng, tier))
    for tier in range(1, 5):
        b[f'blast_ap_t{tier}'] = (2, lambda rng, k, tier=tier: blast_ap(rng, tier))
    b['blast_heat'] = (2, lambda rng, k: blast_heat(rng))
    b['blast_thermo_t3'] = (2, lambda rng, k: blast_thermo(rng, 3))
    b['blast_thermo_t4'] = (2, lambda rng, k: blast_thermo(rng, 4))
    b['smallarms_cluster'] = (3, lambda rng, k: cluster(rng, 4 + k))
    for kind in ('tank', 'wheeled', 'truck', 'artillery', 'aircraft', 'heli', 'ship', 'drone'):
        b[f'wreck_{kind}'] = (2, lambda rng, k, kind=kind: wreck(rng, kind))
    b['train_horn'] = (2, lambda rng, k: horn(rng, [311.1, 370.0, 466.2] if k == 0 else [277.2, 349.2, 415.3], 1.9))
    b['train_rails'] = (1, lambda rng, k: rails_loop(rng))
    b['ship_horn'] = (1, lambda rng, k: horn(rng, [110.0, 138.6], 2.6))
    b['ship_engine'] = (1, lambda rng, k: engine_loop(rng))
    b['crash_fall'] = (2, lambda rng, k: crash_fall(rng))
    b['crash_impact'] = (2, lambda rng, k: crash_impact(rng))
    return b


def seed_of(name: str, k: int) -> int:
    return (sum(ord(c) * (i + 1) for i, c in enumerate(name)) * 131 + k * 7919) % (2 ** 31)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('only', nargs='*', help='banks to build (default: all)')
    ap.add_argument('--list', action='store_true', help='list the banks and write nothing')
    args = ap.parse_args(argv)
    all_banks = banks()
    unknown = [o for o in args.only if o not in all_banks]
    if unknown:
        sys.exit(f'unknown banks: {unknown}')
    total = 0
    for name, (variants, build) in all_banks.items():
        if args.only and name not in args.only:
            continue
        folder = OUT / name
        if not args.list:
            folder.mkdir(parents=True, exist_ok=True)
        for k in range(variants):
            clip = build(np.random.default_rng(seed_of(name, k)), k)
            path = folder / f'{name}_{k + 1}.ogg'
            if args.list:
                print(f'{name}_{k + 1}: {len(clip) / SR:.2f} s')
                continue
            sf.write(str(path), clip, SR, format='OGG', subtype='VORBIS')
            total += path.stat().st_size
            print(f'WROTE {path.relative_to(ROOT)}: {len(clip) / SR:.2f} s')
    if not args.list:
        print(f'P34_SFX_COMPLETE {total / 1024:.0f} KB')


if __name__ == '__main__':
    main()
