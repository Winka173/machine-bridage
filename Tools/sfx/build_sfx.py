"""Fix pass L7: the battle sound library by size, premixed offline (no AI audio). Replaces prompt 34 L6's tiered builder.

    python Tools/sfx/build_sfx.py              # every bank -> Assets/MachineBrigade/Resources/Audio/sfx/<bank>/<bank>_<n>.ogg
    python Tools/sfx/build_sfx.py shot_s3 hit_metal_heavy   # only these banks
    python Tools/sfx/build_sfx.py --list       # the banks, their groups and sizes; writes nothing

Writes, besides the clips: Tools/sfx/library.json (each bank's group, size class and table row, read by analyze_sfx.py and
render_mix.py) and Resources/Audio/sfx/envelopes.txt (each clip's 50 Hz RMS envelope, read by the game's Effects compressor).

Every shot and blast is ONE FILE premixed from three layers (no extra AudioSource a shot):
  1. the main layer: the report or the blast itself. Where the recorded Sonniss clip of the old banks was better (every gun
     from 20 mm, every blast; Resources/Audio/CREDITS.md, Sonniss GDC licence: modification allowed, no attribution) it is
     restored as this layer, pitched down for the bigger sizes; the small arms, the hits, engines, horns and warnings are
     synthesised from noise, sines and filters with fixed seeds;
  2. the sub layer: energy under ~150 Hz (a falling sine thump and low noise), its share of the clip set per size (rising);
  3. the tail: ground reflections (slap-back taps) and a rolling low tail, longer per size.
The low part of the three (under 150 Hz) is scaled until the clip's sub share meets its size's target; the clip is then
brought to its size's loudness (momentary max LUFS, rising with size) through a look-ahead limiter at -1 dBFS, so the size,
not a 6 ms crack, sets how loud a clip hits (prompt 34 L6 peak-normalised every clip: Docs/audio/diagnosis.md).

No clip outside the armour-metal group rings: there are no damped sines between 2 and 6 kHz anywhere else (the keng the
owner heard was prompt 34's blast_ap bell on every kinetic landing). Play-test 13: a kinetic round on armour it does not go
through plays hit_armour_light / heavy / glance (a knock and sparks, no ring); hit_metal_light / heavy are the rare ricochet's
whine (the armour_metal group).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_sfx as az  # noqa: E402

SR = 44100
ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Audio'
OUT = AUDIO / 'sfx'
LIBRARY = ROOT / 'Tools' / 'sfx' / 'library.json'

SIZES = az.SIZES  # s0 <= 14.5, s1 20-40, s2 57-105, s3 120-155, s4 203-240, bomb, s406 (big rockets / >= 406), super

# Per size (index in SIZES): loudness the clip hits at (momentary max LUFS), the share of its energy under 150 Hz (%), the
# tail's decay (s). The shots and the blasts each rise steadily (analyze_sfx --check).
SHOT_LUFS = [-21.0, -19.0, -16.5, -14.5, -13.0, None, -11.5, -10.5]
SHOT_SUB = [6.0, 18.0, 38.0, 53.0, 61.0, None, 70.0, 76.0]
SHOT_TAIL = [0.05, 0.12, 0.25, 0.42, 0.62, None, 0.85, 1.1]
BLAST_LUFS = [-22.0, -18.0, -15.5, -13.5, -12.0, -11.0, -10.0, -9.0]
BLAST_SUB = [12.0, 30.0, 45.0, 55.0, 62.0, 67.0, 72.0, 78.0]
BLAST_TAIL = [0.08, 0.2, 0.33, 0.5, 0.7, 0.85, 1.05, 1.7]


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


def env_exp(seconds: float, decay: float, attack: float = 0.002) -> np.ndarray:
    t = t_axis(seconds)
    e = np.exp(-t / max(1e-4, decay))
    if attack > 0:
        e *= np.clip(t / attack, 0, 1)
    return e


def place(dst: np.ndarray, src: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    if i >= len(dst) or i < 0:
        return
    m = min(len(src), len(dst) - i)
    dst[i:i + m] += src[:m] * gain


def fit(x: np.ndarray, seconds: float) -> np.ndarray:
    out = np.zeros(n(seconds))
    m = min(len(x), len(out))
    out[:m] = x[:m]
    return out


def thump(seconds: float, f0: float, f1: float, decay: float) -> np.ndarray:
    """A falling sine: the chest-thump under a report or a blast (f0 -> f1 Hz)."""
    t = t_axis(seconds)
    f = f1 + (f0 - f1) * np.exp(-t / (decay * 0.35))
    phase = 2 * math.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t / decay) * np.clip(t / 0.004, 0, 1)


def sweep_low(x: np.ndarray, f0: float, f1: float, steps: int = 24) -> np.ndarray:
    """A low pass whose cutoff glides from f0 to f1 over the clip."""
    out = np.zeros_like(x)
    edges = np.linspace(0, len(x), steps + 1).astype(int)
    for k in range(steps):
        a, b = edges[k], edges[k + 1]
        f = f0 * (f1 / f0) ** (k / max(1, steps - 1))
        pad = min(a, 2048)
        out[a:b] = filt(x[a - pad:b], 'low', f)[pad:]
    return out


def loop_bed(x: np.ndarray, cross: float = 0.3) -> np.ndarray:
    k = n(cross)
    head, body = x[:k], x[k:].copy()
    ramp = np.linspace(0, 1, k)
    body[-k:] = body[-k:] * (1 - ramp) + head * ramp
    return body


_RECORDED = {}


def recorded(folder: str, k: int) -> np.ndarray:
    """A recorded clip of the old banks (Resources/Audio/<folder>/<folder>_<k>.ogg), mono at 44.1 kHz (a copy)."""
    files = sorted((AUDIO / folder).glob(f'{folder}_*.ogg'))
    path = files[k % len(files)]
    if path not in _RECORDED:
        x, sr = sf.read(str(path), dtype='float64', always_2d=True)
        x = x.mean(axis=1)
        _RECORDED[path] = signal.resample_poly(x, SR, sr) if sr != SR else x
    return _RECORDED[path].copy()


def pitched(x: np.ndarray, ratio: float) -> np.ndarray:
    """Played slower (ratio < 1: lower and longer), as a bigger gun or blast."""
    if abs(ratio - 1) < 1e-3:
        return x
    return signal.resample_poly(x, 100, int(round(100 * ratio)))


def taps_for(size: int):
    """Slap-back echoes (delay s, gain) off the ground and what stands round: more and later with size."""
    base = [(0.09, 0.3), (0.21, 0.2), (0.38, 0.14), (0.62, 0.1), (0.95, 0.08), (1.4, 0.06), (1.9, 0.05), (2.5, 0.04)]
    stretch = 1 + 0.12 * size
    return [(d * stretch, g) for d, g in base[:1 + size]]


def tail_layer(rng, seconds: float, decay: float, cut: float, size: int, src: np.ndarray | None = None) -> np.ndarray:
    """Layer 3: the tail: echoes of the main layer (duller each) and a rolling low bed, longer by size."""
    x = np.zeros(n(seconds))
    if src is not None:
        wet = filt(src, 'low', cut)
        for d, g in taps_for(size):
            place(x, wet * g, d + rng.uniform(-0.01, 0.01))
    bed_len = min(seconds, decay * 6 + 0.1)
    bed = filt(noise(rng, bed_len), 'low', cut * 0.6, 4) * env_exp(bed_len, decay, 0.05)
    roll = filt(noise(rng, bed_len), 'low', 120, 4) * env_exp(bed_len, decay * 1.25, 0.12)
    place(x, bed * 0.25 + roll * (0.2 + 0.05 * size), 0.03)
    return x


def sub_layer(rng, seconds: float, f0: float, f1: float, decay: float) -> np.ndarray:
    """Layer 2: the weight under 150 Hz: a falling sine thump and a low noise swell."""
    x = np.zeros(n(seconds))
    place(x, thump(min(seconds, decay * 7), f0, f1, decay), 0.0, 1.0)
    swell = min(seconds, decay * 8)
    place(x, filt(noise(rng, swell), 'low', 90, 4) * env_exp(swell, decay * 1.5, 0.01), 0.0, 1.2)
    return x


def limiter(x: np.ndarray, ceiling_db: float = -1.0, look: float = 0.003, release: float = 0.08) -> np.ndarray:
    """A look-ahead peak limiter: instant attack over the look-ahead, a smooth release, never over the ceiling."""
    ceiling = 10 ** (ceiling_db / 20)
    need = np.minimum(1.0, ceiling / np.maximum(np.abs(x), 1e-9))
    w = max(1, int(look * SR))
    held = minimum_filter1d(need, size=2 * w + 1, mode='nearest')
    # Release: a one-pole rise back towards 1, never above what the look-ahead needs (run backwards-free, block-wise).
    a = math.exp(-1.0 / (release * SR))
    g = signal.lfilter([1 - a], [1, -a], held, zi=[held[0] * a])[0]
    g = np.minimum(g, held)
    g = np.convolve(g, np.ones(w) / w, mode='same')
    return np.clip(x * np.minimum(g, held), -ceiling, ceiling)


def match_sub(x: np.ndarray, target: float | None) -> np.ndarray:
    """The low part (under 150 Hz) scaled until the clip's share of energy under 150 Hz meets the target (%)."""
    if target is None:
        return x
    # Zero-phase, so the rest (x - lo) is a true complement with next to nothing under 150 Hz.
    lo = signal.sosfiltfilt(signal.butter(4, 150 / (SR * 0.5), btype='low', output='sos'), x)
    hi = x - lo
    a, b = 0.0, 40.0
    for _ in range(22):
        k = (a + b) / 2
        if az.sub_share(hi + k * lo, SR) < target:
            a = k
        else:
            b = k
    return hi + (a + b) / 2 * lo


def master(x: np.ndarray, lufs: float, sub: float | None, fade: float = 0.06) -> np.ndarray:
    """Sub share, the size's loudness through a gentle saturation and the limiter, the fades; float32."""
    x = filt(x, 'high', 25)
    x = match_sub(x, sub)
    for _ in range(4):
        _, mmax = az.loudness(x, SR)
        x = x * 10 ** ((lufs - mmax) / 20)
        peak = np.max(np.abs(x))
        if peak > 1.0:
            x = np.tanh(x / peak * 1.5) * peak / 1.5 * (1.5 / np.tanh(1.5))
        x = limiter(x)
    if fade > 0:
        k = min(len(x), n(fade))
        x[-k:] *= np.linspace(1, 0, k) ** 2
        k = min(len(x), n(0.002))
        x[:k] *= np.linspace(0, 1, k)
    return x.astype(np.float32)


def trim_tail(x: np.ndarray, floor_db: float = -66.0, keep: float = 0.05) -> np.ndarray:
    """Cuts the silence at the end (under floor_db for good), keeping a short fade."""
    env = az.envelope_db(x, SR)
    above = np.nonzero(env > floor_db)[0]
    end = min(len(x), int((above[-1] + 1) * 0.01 * SR + keep * SR)) if len(above) else len(x)
    y = x[:end].copy()
    k = min(len(y), n(keep))
    y[-k:] *= np.linspace(1, 0, k) ** 2
    return y


# --------------------------------------------------------------------------------------------- the shots and blasts


def crack(rng, seconds: float = 0.004, hp: float = 1800) -> np.ndarray:
    return filt(noise(rng, seconds), 'high', hp) * env_exp(seconds, seconds * 0.25, 0.0002)


def small_arms(rng) -> np.ndarray:
    """<= 14.5 mm: the supersonic crack, the muzzle blast's short body, a click of the bolt (noise only: no ringing)."""
    x = np.zeros(n(0.5))
    place(x, crack(rng, 0.003, 2500), 0.0, 1.4)
    place(x, filt(noise(rng, 0.25), 'band', (180, 3200), 2) * env_exp(0.25, 0.022, 0.0008), 0.0005, 1.6)
    place(x, filt(noise(rng, 0.01), 'band', (700, 2600)) * env_exp(0.01, 0.002), rng.uniform(0.03, 0.05), 0.25)
    return x


def gun(rng, size: int, k: int) -> np.ndarray:
    """A gun's shot by size: the main layer (recorded where it was better), the sub, the tail."""
    if size == 0:
        main = small_arms(rng)
    elif size == 1:
        main = recorded('autocannon', k)
    elif size == 2:
        main = recorded('cannon', k)
    elif size == 3:
        main = recorded('heavy_cannon', k)
    elif size == 4:
        main = pitched(recorded('heavy_cannon', k + 1), 0.82)
        place(main, pitched(recorded('cannon', k), 0.8), 0.0, 0.35)
    elif size == 6:
        main = pitched(recorded('heavy_cannon', k), 0.66)
        place(main, pitched(recorded('explosion_large', k), 0.9), 0.0, 0.45)
    else:  # super: the 800 mm, the railguns of the bosses
        main = pitched(recorded('heavy_cannon', k + 2), 0.55)
        place(main, pitched(recorded('explosion_huge', k), 0.85), 0.0, 0.6)
        place(main, crack(rng, 0.006, 1500), 0.0, 0.8)
    decay = SHOT_TAIL[size]
    seconds = max(len(main) / SR, decay * 6.5 + 0.2) + 0.1
    x = np.zeros(n(seconds))
    place(x, main, 0.0)
    place(x, sub_layer(rng, seconds, 160 - 12 * size, 70 - 4 * size, 0.04 + 0.06 * size), 0.002, 1.0)
    place(x, tail_layer(rng, seconds, decay, 1800 - 160 * size, size, main), 0.0)
    return trim_tail(master(x, SHOT_LUFS[size], SHOT_SUB[size]))


def he_main(size: int, k: int) -> np.ndarray:
    if size == 1:
        return recorded('explosion_small', k)
    if size == 2:
        return recorded('explosion_medium', k)
    if size == 3:
        return recorded('explosion_large', k)
    if size == 4:
        x = pitched(recorded('explosion_large', k + 1), 0.86)
        place(x, recorded('explosion_huge', k), 0.0, 0.35)
        return x
    if size == 5:  # bombs
        x = recorded('explosion_huge', k)
        place(x, pitched(recorded('explosion_large', k + 2), 0.8), 0.0, 0.5)
        return x
    if size == 6:
        return pitched(recorded('explosion_huge', k), 0.85)
    # Super weapons: two huge blasts, slower, and a third slower still rolling back off the hills.
    roll = pitched(recorded('explosion_huge', k + 2), 0.5)
    x = np.zeros(len(roll) + n(0.4))
    place(x, pitched(recorded('explosion_huge', k), 0.72), 0.0)
    place(x, pitched(recorded('explosion_huge', k + 1), 0.6), 0.04, 0.6)
    place(x, roll, 0.35, 0.4)
    return x


def blast(rng, size: int, k: int, main: np.ndarray | None = None, lufs_shift: float = 0.0, sub_shift: float = 0.0) -> np.ndarray:
    """A blast by size: main (recorded), the sub (deeper and longer by size), earth falling back, the tail."""
    main = he_main(size, k) if main is None else main
    decay = BLAST_TAIL[size]
    seconds = max(len(main) / SR, decay * 6.5 + 0.3) + 0.1
    x = np.zeros(n(seconds))
    place(x, main, 0.0)
    place(x, sub_layer(rng, seconds, 130 - 9 * size, 58 - 4 * size, 0.08 + 0.07 * size), 0.0, 1.0)
    # Earth and fragments coming back down: dull ticks (band noise, never a ringing sine).
    for _ in range(int(6 + 8 * size)):
        tick = filt(noise(rng, 0.012), 'band', (300, 2200)) * env_exp(0.012, 0.003)
        place(x, tick, rng.uniform(0.15, 0.3 + 0.3 * size), rng.uniform(0.01, 0.04))
    place(x, tail_layer(rng, seconds, decay, 1500 - 120 * size, size, main), 0.0)
    return trim_tail(master(x, BLAST_LUFS[size] + lufs_shift, min(95.0, BLAST_SUB[size] + sub_shift)))


def thermo(rng, size: int, k: int) -> np.ndarray:
    """Thermobaric: the small pop that throws the fuel, then the ignition's long WHOOMP and roar over a recorded blast."""
    seconds = 2.6 + 0.8 * (size - 3)
    x = np.zeros(n(seconds))
    place(x, filt(noise(rng, 0.03), 'band', (400, 3000)) * env_exp(0.03, 0.008), 0.0, 0.4)
    roar_len = seconds - 0.15
    roar = sweep_low(noise(rng, roar_len), 220, 1300, 16)
    t = t_axis(roar_len)
    place(x, roar * np.clip(t / 0.08, 0, 1) * np.exp(-t / (0.5 + 0.25 * (size - 3))), 0.15, 1.2)
    place(x, he_main(size, k), 0.14, 0.8)
    return blast(rng, size, k, main=x, lufs_shift=0.6, sub_shift=6.0)


def heat(rng, size: int, k: int) -> np.ndarray:
    """A shaped charge: a sharp crack and the jet's hiss (broadband) over a smaller blast."""
    main = recorded('explosion_small' if size <= 2 else 'explosion_medium', k)
    place(main, crack(rng, 0.006, 1800), 0.0, 1.2)
    place(main, filt(noise(rng, 0.16), 'band', (2500, 9000)) * env_exp(0.16, 0.04, 0.003), 0.002, 0.35)
    return blast(rng, size, k, main=main, lufs_shift=-1.0, sub_shift=-8.0)


def airburst(rng, size: int, k: int) -> np.ndarray:
    """A proximity or time-fused burst in the air: a sharp pop, fragments whizzing, little earth (less sub)."""
    main = recorded('flak', k)
    if size >= 2:
        main = pitched(main, 0.85 if size == 2 else 0.72)
        place(main, recorded('explosion_small', k), 0.0, 0.4 if size == 2 else 0.7)
    for _ in range(8 + 4 * size):
        place(main, filt(noise(rng, 0.05), 'band', (900, 5000)) * env_exp(0.05, 0.015, 0.01), rng.uniform(0.02, 0.4), rng.uniform(0.02, 0.06))
    return blast(rng, size, k, main=main, lufs_shift=-1.5, sub_shift=-12.0)


# ------------------------------------------------------------- play-test 12 (lane C): machine guns and autocannons
#
# The owner (play-test 12, 03/10): "machine gun and autocannon sounds are very bad ... where a sound is bad, refer back to the
# old sounds". Yesterday's build (f5e565d3) played prompt 34 L6's synthesised p34/shot_t0, shot_t1 and smallarms_cluster at
# bank levels 0.38, 0.46 and 0.55. Fix pass L7 replaced them (a new noise-only small-arms shot through a limiter, the
# recorded Sonniss autocannon with a sub layer and slap-back taps) and played every bank at 1: the machine guns came out
# ~9.6 dB louder than yesterday and the autocannons ~6.9 dB, against ~2 dB for the tank and artillery shots the owner likes.
# Here yesterday's generator is restored as it was (same code, same seeds: shot_t0 / shot_t1 / smallarms_cluster rebuild
# yesterday's clips), at yesterday's bank level plus the ~2 dB L7 gave the big guns, so the balance is yesterday's again.

P34_REPORT = [(6500, 0.035), (4500, 0.07)]
P34_THUMP = [(0, 0, 0.0, 0.0), (180, 90, 0.05, 0.25)]
P34_TAIL = [(0.08, 0.15, 2500), (0.18, 0.25, 1800)]
P34_LENGTH = [0.35, 0.6]

# Yesterday's bank levels (AudioDirector.P34 at f5e565d3) and the lift L7 gave the tank / artillery shots over yesterday's
# effective level (57-105 mm +3.3 dB, 120-155 mm +1.8, 203-240 mm +1.0): the small arms and autocannons follow it.
P34_BANK = {'shot_t0': 0.38, 'shot_t1': 0.46, 'smallarms_cluster': 0.55}
PT12_LIFT = 10 ** (2.0 / 20)


def p34_damped(freqs, decays, seconds: float, rng, amps=None) -> np.ndarray:
    t = t_axis(seconds)
    out = np.zeros_like(t)
    amps = amps or [1.0] * len(freqs)
    for f, d, a in zip(freqs, decays, amps):
        out += a * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi)) * np.exp(-t / d)
    return out


def p34_echoes(x: np.ndarray, rng, taps, lowpass: float) -> np.ndarray:
    total = len(x) + n(max(d for d, _ in taps) + 0.05)
    out = np.zeros(total)
    out[:len(x)] += x
    wet = filt(x, 'low', lowpass)
    for d, g in taps:
        place(out, wet * g, d + rng.uniform(-0.01, 0.01))
    return out


def p34_finish(x: np.ndarray, peak_db: float = -1.0) -> np.ndarray:
    x = filt(x, 'high', 25)
    k = min(len(x), n(0.04))
    x = x.copy()
    x[-k:] *= np.linspace(1, 0, k) ** 2
    peak = np.max(np.abs(x)) or 1.0
    return x / peak * 10 ** (peak_db / 20)


def p34_mechanism(rng, tier: int) -> np.ndarray:
    """The bolt's clack near the gun (yesterday's layer 1; its partials fall 20 dB in under 0.1 s: no keng)."""
    seconds = 0.12 + 0.05 * tier
    x = np.zeros(n(seconds + 0.2))
    for k in range(2):
        at = 0.0 if k == 0 else rng.uniform(0.02, 0.06) + 0.03 * tier * k / 2
        burst = filt(noise(rng, 0.012), 'high', 2500 - 300 * tier) * env_exp(0.012, 0.003)
        place(x, burst, at, 0.6 if k else 1.0)
    base = 900 / (1 + 0.45 * tier)
    ring = p34_damped([base * 1.0, base * 1.63, base * 2.71, base * 4.13], [0.03 + 0.012 * tier] * 4, seconds, rng, [1, 0.6, 0.4, 0.25])
    place(x, ring, 0.004 + 0.01 * tier, 0.5)
    return x


def p34_report(rng, tier: int) -> np.ndarray:
    """The crack and the body of the muzzle blast (yesterday's layer 2)."""
    cut, decay = P34_REPORT[tier]
    seconds = decay * 6 + 0.05
    sharp = filt(noise(rng, 0.006), 'high', 1500) * env_exp(0.006, 0.0015, 0.0003)
    body = filt(noise(rng, seconds), 'low', cut, 4) * env_exp(seconds, decay, 0.0015)
    x = fit(sharp, seconds) * (1.2 - 0.12 * tier) + body * 1.4
    f0, f1, d, lvl = P34_THUMP[tier]
    if lvl > 0:
        x += thump(seconds, f0, f1, d) * lvl * 1.6
    return x


def p34_tail(rng, tier: int) -> np.ndarray:
    """The echo off the ground (yesterday's layer 3)."""
    decay, level, cut = P34_TAIL[tier]
    seconds = decay * 3.5 + 0.1
    return filt(noise(rng, seconds), 'low', cut, 4) * env_exp(seconds, decay, 0.06) * level


def p34_shot(rng, tier: int) -> np.ndarray:
    """Yesterday's T0 / T1 shot (prompt 34 L6 gun_shot), peak -1 dBFS before its bank level."""
    seconds = P34_LENGTH[tier]
    x = np.zeros(n(seconds + 1.0))
    place(x, p34_mechanism(rng, tier), 0.0, 0.55)
    rep = p34_report(rng, tier)
    taps = [(0.11 + 0.03 * tier, 0.32), (0.27 + 0.05 * tier, 0.18)]
    place(x, p34_echoes(rep, rng, taps, 1800 - 220 * tier), 0.01)
    place(x, p34_tail(rng, tier), 0.02)
    return p34_finish(fit(x, seconds))


def p34_dry(rng, tier: int) -> np.ndarray:
    """One round of a rotary gun: yesterday's bolt and report without the per-round echo (the burst gets one echo)."""
    seconds = P34_LENGTH[tier] * 0.6
    x = np.zeros(n(seconds))
    place(x, p34_mechanism(rng, tier), 0.0, 0.45)
    place(x, p34_report(rng, tier), 0.002)
    return p34_finish(fit(x, seconds))


def small_shot(tier: int, k: int, ratio: float = 1.0, level: float = 1.0) -> np.ndarray:
    """shot_s0 / shot_s1: yesterday's clip k (k >= 3: a new variant), at yesterday's level and the L7 lift."""
    old = f'shot_t{tier}'
    x = p34_shot(np.random.default_rng(seed_of(old, k)), tier) * P34_BANK[old] * PT12_LIFT * level
    if abs(ratio - 1) > 1e-3:
        x = pitched(x, ratio)
    return x.astype(np.float32)


def p34_cluster(guns: int, k: int) -> np.ndarray:
    """Yesterday's small-arms cluster (several machine guns near and far as one sound), at its level and the L7 lift."""
    rng = np.random.default_rng(seed_of('smallarms_cluster', k))
    seconds = 1.6
    x = np.zeros(n(seconds + 0.5))
    for _ in range(guns):
        rate = rng.uniform(9, 16)
        far = rng.uniform(0, 1)
        start = rng.uniform(0, 0.4)
        stop = rng.uniform(0.8, seconds)
        tt = start
        while tt < stop:
            rep = p34_report(rng, 0)
            shot = rep + fit(p34_mechanism(rng, 0), len(rep) / SR) * 0.3
            shot = filt(shot, 'low', 7000 - 5000 * far)
            place(x, shot, tt, (1.0 - 0.6 * far) * rng.uniform(0.7, 1.0))
            tt += 1.0 / rate * rng.uniform(0.85, 1.15)
    place(x, p34_tail(rng, 1) * 0.5, 0.0)
    return (p34_finish(fit(x, seconds)) * P34_BANK['smallarms_cluster'] * PT12_LIFT).astype(np.float32)


# Rapid fire (AudioDirector: one burst a shooter, SoundLibrary.Bursts): bank -> (tier, cyclic rate the clip is built at,
# rounds in one segment, the loudest a segment may hit, momentary max LUFS). The game retriggers a shooter's burst after its
# segment (rounds / rate, scaled by the pitch that matches the gun's own rate), so the rhythm is the gun's, even, and never
# the 20 Hz Sim tick's; a segment is about a third of a second, so a burst stops soon after the gun does.
BURSTS = {
    'burst_s0_10': (0, 10.0, 3, -20.5), 'burst_s0_16': (0, 16.0, 5, -19.5), 'burst_s0_55': (0, 55.0, 18, -18.5),
    'burst_s1_10': (1, 10.0, 3, -17.5), 'burst_s1_22': (1, 22.0, 7, -16.5), 'burst_s1_35': (1, 35.0, 12, -16.0),
    'burst_s1_55': (1, 55.0, 18, -15.5),
}


def burst(name: str, k: int) -> np.ndarray:
    """A burst segment: rounds at the cyclic rate (a mechanical rhythm: 1 % timing jitter, a little level play), each a fresh
    yesterday-style round; a rotary gun's rounds dry, with one echo and tail for the burst. Each round is at the single shot's
    level, so a burst is their true sum, held under the bank's cap by the limiter; no ring outside the bolt's short clack."""
    tier, rate, rounds, cap = BURSTS[name]
    rng = np.random.default_rng(seed_of(name, k))
    rotary = rate > 20
    single = P34_BANK[f'shot_t{tier}'] * PT12_LIFT
    seg = rounds / rate
    x = np.zeros(n(seg + P34_LENGTH[tier] + 0.8))
    for i in range(rounds):
        at = i / rate + (rng.uniform(-0.01, 0.01) / rate if i else 0.0)
        one = p34_dry(rng, tier) if rotary else p34_shot(rng, tier)
        place(x, one, at, single * rng.uniform(0.86, 1.0) * (0.7 if rotary else 1.0))
    if rotary:
        # The burst's own echo off the ground and its tail (yesterday's taps and bed, once for the whole burst).
        dry = x.copy()
        taps = [(0.11 + 0.03 * tier, 0.3), (0.27 + 0.05 * tier, 0.16)]
        x = p34_echoes(dry, rng, taps, 1800 - 220 * tier)[:len(x)]
        bed = p34_tail(rng, tier)
        for j in range(3):
            place(x, bed * single * 0.8, seg * j / 3 + 0.02)
    x = filt(x, 'high', 25)
    _, mmax = az.loudness(x, SR)
    if mmax > cap:
        x *= 10 ** ((cap - mmax) / 20)
    if np.max(np.abs(x)) > 0.89:
        x = limiter(x)
    return trim_tail(x, -60.0, 0.04).astype(np.float32)


# ----------------------------------------------------------------------------------- play-test 12: missiles and rockets
#
# The owner: "missiles sound almost like tanks". L7's launches were a recorded launch pitched down, with a gun's falling-sine
# thump (sub_layer) and a gun's slap-back taps (tail_layer) mastered to 18-45 % under 150 Hz: a boom, as a tank's. A launch
# is now a rocket motor: the ignition crack (and an ATGM's eject pop before its motor lights), the booster's roar with the
# motor's crackle (sparse impulses: the sound of a solid motor), a cutoff gliding down as it flies off, then the sustainer's
# thin hiss going away; under it a low rumble of the exhaust, never a falling sine; a diffuse air tail, never discrete taps.

# kind -> (booster s, recede s, roar's low edge Hz, crackles a second, hiss s, eject pop, rumble, momentary max LUFS, sub %)
LAUNCHES = {
    'launch_atgm': (0.22, 0.8, 320.0, 160.0, 1.1, 1.3, 0.15, -17.0, 7.0),
    'launch_sam': (0.55, 1.0, 220.0, 420.0, 0.8, 0.5, 0.35, -15.5, 11.0),
    'launch_s2': (0.16, 0.5, 260.0, 260.0, 0.5, 0.7, 0.25, -16.5, 9.0),
    'launch_s3': (0.42, 1.0, 160.0, 520.0, 0.7, 0.6, 0.55, -14.5, 17.0),
    'launch_big': (0.85, 1.7, 100.0, 700.0, 0.9, 0.5, 0.9, -12.0, 27.0),
    'launch_cruise': (0.75, 1.1, 130.0, 600.0, 0.9, 0.5, 0.7, -12.5, 22.0),
}


def crackle(rng, seconds: float, rate: float, hp: float = 1200.0) -> np.ndarray:
    """A solid motor's crackle: sparse signed impulses, high-passed (broadband ticks, no tone)."""
    x = np.zeros(n(seconds))
    count = max(1, int(rate * seconds))
    idx = rng.integers(0, len(x), count)
    x[idx] = rng.uniform(0.3, 1.0, count) * rng.choice([-1.0, 1.0], count)
    return filt(x, 'high', hp)


def motor(rng, seconds: float, lo: float, rate: float) -> np.ndarray:
    """The motor's roar: band noise with a rough 20-60 Hz flutter and the crackle on top."""
    body = filt(noise(rng, seconds), 'band', (lo, 7000), 2)
    flutter = filt(noise(rng, seconds), 'low', 45, 2)
    flutter /= (np.std(flutter) or 1.0)
    body = body / (np.std(body) or 1.0) * (1 + 0.3 * flutter)
    return body + crackle(rng, seconds, rate) * 2.5


def rocket_launch(name: str, k: int) -> np.ndarray:
    burn, recede, lo, rate, hiss, pop, rumble, lufs, sub = LAUNCHES[name]
    rng = np.random.default_rng(seed_of(name, k))
    burn *= rng.uniform(0.9, 1.1)
    span = burn + recede
    extra = 1.6 if name == 'launch_cruise' else 0.0
    x = np.zeros(n(span + hiss + extra + 0.6))
    # 1. Ignition: the crack, and an ATGM's (a small rocket's) eject pop just before its motor lights.
    place(x, crack(rng, 0.004, 2000), 0.0, 1.0)
    place(x, filt(noise(rng, 0.06), 'band', (250, 2500)) * env_exp(0.06, 0.012, 0.0005), 0.0, pop)
    lit = 0.06 if name in ('launch_atgm', 'launch_s2') else 0.01
    # 2. The booster: swells in 40 ms, holds over its burn, fades and dulls as it flies off.
    t = t_axis(span)
    shape = np.clip(t / 0.04, 0, 1) * np.where(t < burn, 1.0, np.exp(-(t - burn) / (recede * 0.35)))
    roar = sweep_low(motor(rng, span, lo, rate) * shape, 7500, 1100, 20)
    place(x, roar, lit, 0.5)
    # 3. The sustainer's hiss going away (the round in flight).
    h = filt(noise(rng, hiss), 'band', (2500, 9000), 2) * env_exp(hiss, hiss * 0.4, 0.05)
    place(x, sweep_low(h, 9000, 3000, 10), lit + burn * 0.6, 0.25)
    # 4. The exhaust's rumble under the booster (low noise, never a falling sine: that is a gun's thump).
    place(x, filt(noise(rng, span), 'low', 160, 4) * shape, lit, rumble)
    # 5. A cruise missile's turbojet taking over from its booster: a broad whoosh under 2.5 kHz, fading off.
    if extra:
        jt = t_axis(extra + 0.6)
        jet = filt(noise(rng, extra + 0.6), 'band', (350, 2500), 2) * np.clip(jt / 0.3, 0, 1) * np.exp(-jt / (extra * 0.55))
        place(x, sweep_low(jet, 2500, 900, 12), lit + burn * 0.8, 0.3)
    # 6. The air: a diffuse dull tail (no discrete slap-back taps).
    tail_len = 0.4 + recede
    place(x, filt(noise(rng, tail_len), 'low', 900, 2) * env_exp(tail_len, recede * 0.45, 0.08), lit + burn, 0.08 + 0.04 * rumble)
    return trim_tail(master(x, lufs, sub))


def missile_hiss(k: int) -> np.ndarray:
    """A missile or a rocket coming in, just before it lands: a hiss swelling and brightening as it nears (noise only)."""
    rng = np.random.default_rng(seed_of('missile_hiss', k))
    seconds = 0.5 + 0.05 * k
    t = t_axis(seconds)
    swell = (t / seconds) ** 2 * np.clip((seconds - t) / 0.02, 0, 1)
    h = sweep_low(filt(noise(rng, seconds), 'band', (1200, 9000), 2), 2500, 9000, 10)
    x = h * swell + filt(noise(rng, seconds), 'band', (300, 1200), 2) * swell * 0.35
    return master(x, -21.0, 3.0, fade=0.01)


# ----------------------------------------------------------------------------------------------------------- hits

# Play-test 12: the light hits (up to 40 mm: every machine-gun and autocannon round that lands) 3.5 dB down: at -22 LUFS a
# round's landing was as loud as the gun (yesterday's impact was at -28 effective); the heavy hits (tank guns) unchanged.
PT12_LIGHT_HIT = -3.5


def metal_ring(rng, base: float, seconds: float, decay: float) -> np.ndarray:
    """The armour plate ringing: the ONLY damped inharmonic sines of the library (group armour_metal)."""
    t = t_axis(seconds)
    out = np.zeros_like(t)
    for ratio, amp, dk in ((1.0, 1.0, 1.0), (1.47, 0.6, 0.8), (2.09, 0.4, 0.6), (2.76, 0.25, 0.45)):
        out += amp * np.sin(2 * math.pi * base * ratio * t + rng.uniform(0, 6.28)) * np.exp(-t / (decay * dk))
    return out


def glide_band(rng, seconds: float, f0: float, f1: float, width: float = 0.18) -> np.ndarray:
    """Noise through a narrow band whose centre glides f0 -> f1 (a ricochet's whine: the spinning, tumbling slug)."""
    x = noise(rng, seconds)
    out = np.zeros_like(x)
    steps = max(8, int(seconds / 0.012))
    edges = np.linspace(0, len(x), steps + 1).astype(int)
    for i in range(steps):
        a, b = edges[i], edges[i + 1]
        f = f0 * (f1 / f0) ** (i / max(1, steps - 1))
        pad = min(a, 2048)
        out[a:b] = filt(x[a - pad:b], 'band', (f * (1 - width), f * (1 + width)), 2)[pad:]
    return out


def sparks(rng, seconds: float, gain: float, decay: float) -> np.ndarray:
    """The spray of sparks and spall off a struck plate: a fizz above 5 kHz and a scatter of tiny ticks (noise only)."""
    x = filt(noise(rng, seconds), 'high', 5500, 2) * env_exp(seconds, decay, 0.001) * gain
    for _ in range(int(seconds * 60)):
        place(x, filt(noise(rng, 0.004), 'high', 3000) * env_exp(0.004, 0.001), rng.uniform(0.005, seconds * 0.8), rng.uniform(0.05, 0.2) * gain)
    return x


# Play-test 13: a round on armour it does not go through is a hit, not a bell. Thick armour is a heavily damped mass: a
# bullet goes "tack", an autocannon round "crack-thunk", a tank round a hard deep slam, each with a spray of sparks and no
# ring. The ricochet's whine is the rare exception (hit_metal_*, the only armour_metal group left).
def hit_armour(rng, kind: str, k: int) -> np.ndarray:
    """kind: 'light' (machine gun, autocannon up to 40 mm), 'heavy' (a tank gun level with the armour) or 'glance' (a heavy
    round against armour far beyond it: shorter and lighter, the slug shatters or skids off)."""
    seconds = {'light': 0.35, 'heavy': 0.8, 'glance': 0.45}[kind]
    x = np.zeros(n(seconds))
    place(x, crack(rng, 0.003 if kind == 'light' else 0.005, 2200), 0.0, 1.5)
    if kind == 'light':
        # the "tack": a bright, very short knock of the plate's surface
        place(x, filt(noise(rng, 0.06), 'band', (700, 3200), 2) * env_exp(0.06, 0.008, 0.0004), 0.0, 1.0)
        place(x, filt(noise(rng, 0.08), 'band', (250, 900), 2) * env_exp(0.08, 0.014, 0.0008), 0.0, 0.5)
        place(x, sparks(rng, 0.2, 0.18, 0.05), 0.003)
    elif kind == 'heavy':
        # the slam: a broad knock through the hull, a short chest thump, spall rattling off
        place(x, filt(noise(rng, 0.3), 'band', (120, 2200), 2) * env_exp(0.3, 0.05, 0.0008), 0.0, 1.6)
        place(x, thump(0.4, 120, 55, 0.07), 0.0, 1.0)
        place(x, sparks(rng, 0.5, 0.22, 0.12), 0.004)
        for _ in range(7):
            place(x, filt(noise(rng, 0.02), 'band', (400, 3000)) * env_exp(0.02, 0.005), rng.uniform(0.04, 0.35), rng.uniform(0.08, 0.2))
    else:
        # the glance: a hard crack-clack, less body and bass than the slam
        place(x, filt(noise(rng, 0.15), 'band', (350, 2800), 2) * env_exp(0.15, 0.025, 0.0006), 0.0, 1.3)
        place(x, thump(0.2, 170, 100, 0.03), 0.0, 0.45)
        place(x, sparks(rng, 0.35, 0.22, 0.08), 0.003)
    lufs, sub = {'light': (-21.5, 5.0), 'heavy': (-16.0, 24.0), 'glance': (-18.5, 10.0)}[kind]
    return trim_tail(master(x, lufs, sub))


def hit_metal(rng, heavy: bool, k: int) -> np.ndarray:
    """A real ricochet, rare (play-test 13): the tick off the plate, then the slug's whine falling away as it tumbles off."""
    seconds = 0.75 if heavy else 0.5
    x = np.zeros(n(seconds))
    place(x, crack(rng, 0.003, 2500), 0.0, 1.2)
    place(x, filt(noise(rng, 0.05), 'band', (600, 2800), 2) * env_exp(0.05, 0.008, 0.0004), 0.0, 0.6)
    span = seconds - 0.03
    f0 = rng.uniform(2600, 3400) if not heavy else rng.uniform(1500, 1900)
    whine = glide_band(rng, span, f0, f0 * (0.38 if heavy else 0.45)) * env_exp(span, span * 0.35, 0.03)
    place(x, whine, 0.02, 1.4)
    place(x, sparks(rng, 0.15, 0.12, 0.04), 0.002)
    return trim_tail(master(x, -19.0 if heavy else -22.0, 6.0 if heavy else 3.0))


def hit_pen(rng, heavy: bool, k: int) -> np.ndarray:
    """A round going through armour: a heavy, dull impact (a punch and a crunch inside), no ring."""
    x = np.zeros(n(1.2 if heavy else 0.6))
    place(x, crack(rng, 0.004, 1500), 0.0, 0.8)
    place(x, filt(noise(rng, 0.4), 'band', (150, 1400), 2) * env_exp(0.4, 0.08 if heavy else 0.04, 0.002), 0.0, 1.6)
    place(x, thump(0.8, 120 if heavy else 150, 50 if heavy else 70, 0.12 if heavy else 0.06), 0.0, 1.4)
    for _ in range(6 if heavy else 3):
        place(x, filt(noise(rng, 0.03), 'band', (200, 1800)) * env_exp(0.03, 0.008), rng.uniform(0.03, 0.25), rng.uniform(0.1, 0.3))
    if heavy:
        place(x, recorded('explosion_small', k) * 0.35, 0.02)
    return trim_tail(master(x, -15.0 if heavy else -19.0 + PT12_LIGHT_HIT, 40.0 if heavy else 22.0))


def hit_ground(rng, heavy: bool, k: int) -> np.ndarray:
    """A round into the earth: a soft thud and a spray of soil."""
    x = np.zeros(n(1.0 if heavy else 0.45))
    place(x, thump(0.5, 110 if heavy else 150, 45 if heavy else 70, 0.08 if heavy else 0.03), 0.0, 1.0)
    place(x, filt(noise(rng, 0.5), 'low', 1600 if heavy else 2400, 2) * env_exp(0.5, 0.07 if heavy else 0.03, 0.003), 0.0, 1.0)
    for _ in range(12 if heavy else 5):
        place(x, filt(noise(rng, 0.01), 'band', (300, 2500)) * env_exp(0.01, 0.003), rng.uniform(0.05, 0.6 if heavy else 0.25),
              rng.uniform(0.04, 0.12))
    if heavy:
        place(x, recorded('explosion_small', k + 1) * 0.3, 0.0)
    return trim_tail(master(x, -17.0 if heavy else -22.0 + PT12_LIGHT_HIT, 35.0 if heavy else 12.0))


def hit_concrete(rng, heavy: bool, k: int) -> np.ndarray:
    """A round into a building or a bunker: a hard crack, chips and grit raining down, dust (noise grains: no ring)."""
    x = np.zeros(n(1.2 if heavy else 0.55))
    place(x, crack(rng, 0.005, 1200), 0.0, 1.3)
    place(x, filt(noise(rng, 0.3), 'band', (250, 3000), 2) * env_exp(0.3, 0.05 if heavy else 0.025, 0.001), 0.0, 1.3)
    place(x, thump(0.5, 130, 60, 0.07 if heavy else 0.035), 0.0, 0.8)
    for _ in range(20 if heavy else 8):
        place(x, filt(noise(rng, 0.008), 'band', (1000, 4500)) * env_exp(0.008, 0.002), rng.uniform(0.04, 0.8 if heavy else 0.35),
              rng.uniform(0.03, 0.1))
    if heavy:
        place(x, recorded('debris', k) * 0.4, 0.05)
    return trim_tail(master(x, -16.0 if heavy else -21.0 + PT12_LIGHT_HIT, 25.0 if heavy else 10.0))


# --------------------------------------------------------------------------------- wrecks, crashes, the rest


def low_clang(rng, base: float, seconds: float, decay: float) -> np.ndarray:
    """A heavy part landing (a turret, a wheel): a low, dull knock, its partials kept under 1.6 kHz."""
    t = t_axis(seconds)
    out = np.zeros_like(t)
    for ratio, amp in ((1.0, 1.0), (1.52, 0.5), (2.37, 0.25)):
        out += amp * np.sin(2 * math.pi * base * ratio * t + rng.uniform(0, 6.28)) * np.exp(-t / decay)
    return filt(out + filt(noise(rng, seconds), 'low', 700) * np.exp(-t / (decay * 0.5)), 'low', 1600, 4)


def wreck(rng, kind: str, k: int) -> np.ndarray:
    x = np.zeros(n(4.5))
    if kind == 'tank':
        place(x, blast(rng, 3, k), 0.0, 1.0)
        place(x, low_clang(rng, 180, 1.0, 0.25), 0.2, 0.35)
        place(x, filt(noise(rng, 2.5), 'band', (200, 2000)) * env_exp(2.5, 0.9, 0.3) * 0.08, 0.6)
        lufs, sub = -12.5, 58.0
    elif kind == 'wheeled':
        place(x, blast(rng, 2, k), 0.0, 1.0)
        place(x, filt(noise(rng, 0.05), 'band', (300, 3000)) * env_exp(0.05, 0.015), 0.12, 0.4)
        for j in range(4):
            place(x, filt(noise(rng, 0.12), 'band', (200, 1200)) * env_exp(0.12, 0.05), 0.5 + 0.18 * j, 0.2 - 0.03 * j)
        lufs, sub = -14.0, 48.0
    elif kind in ('truck', 'artillery'):
        at = 0.0
        for j in range(4 if kind == 'truck' else 6):
            place(x, blast(rng, 3 if j == 0 else 2, k + j), at, 1.0 if j == 0 else rng.uniform(0.35, 0.6))
            at += rng.uniform(0.25, 0.5) if kind == 'truck' else rng.uniform(0.18, 0.4)
        lufs, sub = (-13.0, 55.0) if kind == 'truck' else (-12.5, 57.0)
    elif kind == 'aircraft':
        place(x, blast(rng, 4, k), 0.0, 1.0)
        for _ in range(14):
            place(x, low_clang(rng, rng.uniform(150, 420), 0.3, 0.06), rng.uniform(0.2, 2.2), rng.uniform(0.03, 0.08))
        lufs, sub = -11.5, 62.0
    elif kind == 'heli':
        place(x, blast(rng, 3, k), 0.0, 1.0)
        at, gap = 0.1, 0.045
        while at < 1.8:
            place(x, filt(noise(rng, 0.02), 'band', (250, 1800)) * env_exp(0.02, 0.006), at, 0.25)
            at += gap
            gap *= 1.09
        lufs, sub = -12.5, 58.0
    elif kind == 'ship':
        t = t_axis(4.5)
        groan_f = 100 + 30 * np.sin(2 * math.pi * 0.35 * t)
        groan = np.sin(2 * math.pi * np.cumsum(groan_f) / SR) * (0.6 + 0.4 * np.sin(2 * math.pi * 7 * t))
        x += filt(groan, 'low', 600) * np.clip(t / 0.6, 0, 1) * np.exp(-t / 2.5) * 0.3
        place(x, blast(rng, 6, k), 0.3, 1.0)
        place(x, filt(noise(rng, 3.0), 'band', (150, 2000)) * env_exp(3.0, 1.2, 0.4), 1.3, 0.08)
        lufs, sub = -10.5, 72.0
    elif kind == 'drone':
        x = np.zeros(n(1.2))
        place(x, blast(rng, 1, k), 0.0, 1.0)
        lufs, sub = -18.5, 28.0
    else:
        raise ValueError(kind)
    return trim_tail(master(x, lufs, sub))


def crash_fall(rng) -> np.ndarray:
    """A shot-down aircraft coming down: an engine's falling whine (under 1 kHz) and the air tearing past."""
    seconds = 2.8
    t = t_axis(seconds)
    f = 700 * (0.35 + 0.65 * np.exp(-t / 1.4))
    whine = np.sin(2 * math.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * math.pi * np.cumsum(f) / SR)
    wind = sweep_low(noise(rng, seconds), 600, 3500, 12)
    return master(whine * 0.25 * np.clip(t / 0.2, 0, 1) + wind * 0.6 * np.clip(t / 1.5, 0, 1), -15.0, 8.0)


def crash_impact(rng, k: int) -> np.ndarray:
    x = np.zeros(n(4.0))
    place(x, blast(rng, 4, k), 0.0, 1.0)
    for _ in range(12):
        place(x, low_clang(rng, rng.uniform(150, 400), 0.35, 0.06), rng.uniform(0.15, 2.0), rng.uniform(0.03, 0.08))
    return trim_tail(master(x, -11.5, 62.0))


def horn(rng, freqs, seconds: float, lufs: float) -> np.ndarray:
    """A horn chord: rich tones under 1.7 kHz (no 2-6 kHz partials to ring), a soft attack, slight vibrato, two echoes."""
    t = t_axis(seconds)
    x = np.zeros_like(t)
    for k, f in enumerate(freqs):
        fv = f * (1 + 0.004 * np.sin(2 * math.pi * (4.5 + 0.3 * k) * t))
        ph = 2 * math.pi * np.cumsum(fv) / SR
        x += sum(np.sin(ph * h) / h for h in range(1, 9) if f * h < 1700) * (0.9 ** k)
    a = np.clip(t / 0.08, 0, 1) * np.clip((seconds - t) / 0.25, 0, 1)
    x = filt(x, 'low', 1500, 6) * a + filt(noise(rng, seconds), 'band', (200, 4000)) * 0.004 * a
    y = np.zeros(n(seconds + 1.2))
    place(y, x, 0.0)
    for d, g in ((0.35, 0.25), (0.8, 0.12)):
        place(y, filt(x, 'low', 1000), d, g)
    return master(y, lufs, None)


def rails_loop(rng) -> np.ndarray:
    """A train on the rails: the clack-clack of the joints over a rolling rumble (loops; noise knocks, no ring)."""
    seconds = 4.3
    x = filt(noise(rng, seconds), 'low', 400, 4) * 0.35 + filt(noise(rng, seconds), 'band', (900, 3000)) * 0.04
    at = 0.05
    while at < seconds - 0.3:
        for pair in (0.0, 0.11):
            clack = filt(noise(rng, 0.04), 'band', (200, 2000)) * env_exp(0.04, 0.012)
            place(x, clack + low_clang(rng, 260, 0.04, 0.015) * 0.3, at + pair, 0.9)
        at += 0.62
    return master(loop_bed(x, 0.3), -20.0, 25.0, fade=0.0)


def engine_loop(rng, fundamental: float, firing: float, roar: tuple, clatter: float, lufs: float, sub: float) -> np.ndarray:
    """An engine at work (loops): a diesel's firing pulses and hum, the road or track noise, a track's clatter (noise knocks)."""
    seconds = 4.3
    t = t_axis(seconds)
    pulses = np.zeros_like(t)
    at = 0.0
    while at < seconds:
        pulses[int(at * SR)] = rng.uniform(0.7, 1.0)
        at += rng.uniform(0.97, 1.03) / firing
    body = filt(signal.lfilter([1], [1, -0.995], pulses), 'low', 320, 4)
    hum = np.sin(2 * math.pi * fundamental * t) * 0.3 + np.sin(2 * math.pi * fundamental * 2 * t) * 0.15
    x = body / (np.max(np.abs(body)) or 1) + hum + filt(noise(rng, seconds), 'band', roar, 2) * 0.25
    at = 0.0
    while clatter > 0 and at < seconds - 0.05:
        place(x, filt(noise(rng, 0.02), 'band', (250, 1800)) * env_exp(0.02, 0.006), at, clatter)
        at += rng.uniform(0.06, 0.11)
    return master(loop_bed(x, 0.3), lufs, sub, fade=0.0)


def ship_engine(rng) -> np.ndarray:
    seconds = 4.3
    t = t_axis(seconds)
    throb = np.sin(2 * math.pi * 38 * t) * (0.6 + 0.4 * np.sin(2 * math.pi * 3.5 * t)) + 0.4 * np.sin(2 * math.pi * 76 * t)
    x = filt(throb, 'low', 200) * 0.7 + filt(noise(rng, seconds), 'band', (200, 1800)) * 0.25
    return master(loop_bed(x, 0.3), -19.0, 70.0, fade=0.0)


def flare(rng) -> np.ndarray:
    """Flares out: three quick pops of the cartridges and the hiss of the burning flares falling away (broadband)."""
    x = np.zeros(n(1.6))
    for j in range(3):
        at = 0.07 * j + rng.uniform(0, 0.02)
        place(x, filt(noise(rng, 0.03), 'band', (250, 2500)) * env_exp(0.03, 0.006), at, 1.0)
        place(x, thump(0.12, 180, 90, 0.02), at, 0.4)
        hiss = filt(noise(rng, 1.2), 'band', (2500, 9000), 2) * env_exp(1.2, 0.35, 0.03)
        place(x, sweep_low(hiss, 9000, 3000, 8), at + 0.02, 0.18)
    return trim_tail(master(x, -18.0, 8.0))


def whistle(rng, big: bool) -> np.ndarray:
    """An incoming shell whistling down onto where it lands: a falling tone (under 2 kHz) in air noise, louder as it nears."""
    seconds = 1.6 if big else 1.25
    t = t_axis(seconds)
    f0, f1 = (1100, 380) if big else (1700, 650)
    f = f1 + (f0 - f1) * (1 - t / seconds) ** 1.4
    swell = (t / seconds) ** 2
    x = (np.sin(2 * math.pi * np.cumsum(f) / SR) * 0.6 * swell + filt(noise(rng, seconds), 'band', (300, 2500), 2) * swell * 0.4)
    if big:
        x += filt(noise(rng, seconds), 'low', 140, 4) * swell * 0.8
    x *= np.clip((seconds - t) / 0.03, 0, 1)
    return master(x, -16.0 if big else -19.0, 30.0 if big else 4.0, fade=0.01)


# --------------------------------------------------------------------------------------------------- the banks


def banks():
    """bank -> (group, size class or None, size-table row or None, variants, builder(rng, k))."""
    b = {}
    for name, size in {'shot_s2': 2, 'shot_s3': 3, 'shot_s4': 4, 'shot_s406': 6, 'shot_super': 7}.items():
        b[name] = ('shot', SIZES[size], 'shot', 3 if size < 6 else 2, lambda rng, k, s=size: gun(rng, s, k))
    # Play-test 12: the machine guns and autocannons on yesterday's voice (4 variants: yesterday's 3 and a new one), their
    # rapid-fire bursts, the 57 mm autocannon (yesterday's 30 mm pitched down), and the launches by family.
    b['shot_s0'] = ('shot', 's0', 'shot', 4, lambda rng, k: small_shot(0, k))
    b['shot_s1'] = ('shot', 's1', 'shot', 4, lambda rng, k: small_shot(1, k))
    b['shot_ac57'] = ('shot', 's2', None, 3, lambda rng, k: small_shot(1, k, 0.84, 1.6))
    for name, (tier, _, _, _) in BURSTS.items():
        b[name] = ('shot', SIZES[tier], None, 3, lambda rng, k, nm=name: burst(nm, k))
    for name in LAUNCHES:
        size = {'launch_atgm': 2, 'launch_sam': 2, 'launch_s2': 2, 'launch_s3': 3}.get(name, 6)
        b[name] = ('launch', SIZES[size], None, 3, lambda rng, k, nm=name: rocket_launch(nm, k))
    b['missile_hiss'] = ('launch', None, None, 2, lambda rng, k: missile_hiss(k))
    for name, size in {'blast_he_s1': 1, 'blast_he_s2': 2, 'blast_he_s3': 3, 'blast_he_s4': 4, 'blast_bomb': 5, 'blast_he_s406': 6,
                       'blast_super': 7}.items():
        b[name] = ('blast', SIZES[size], 'blast', 3 if size < 6 else 2, lambda rng, k, s=size: blast(rng, s, k))
    for name, size in {'blast_thermo_s3': 3, 'blast_thermo_s4': 4}.items():
        b[name] = ('blast_thermo', SIZES[size], None, 2, lambda rng, k, s=size: thermo(rng, s, k))
    for name, size in {'blast_heat_s2': 2, 'blast_heat_s3': 3}.items():
        b[name] = ('blast_heat', SIZES[size], None, 2, lambda rng, k, s=size: heat(rng, s, k))
    for name, size in {'blast_air_s1': 1, 'blast_air_s2': 2, 'blast_air_s3': 3}.items():
        b[name] = ('blast_air', SIZES[size], None, 2, lambda rng, k, s=size: airburst(rng, s, k))
    b['hit_ground_light'] = ('hit_ground', 's0', 'blast', 3, lambda rng, k: hit_ground(rng, False, k))
    b['hit_ground_heavy'] = ('hit_ground', 's2', None, 3, lambda rng, k: hit_ground(rng, True, k))
    b['hit_concrete_light'] = ('hit_concrete', 's0', None, 3, lambda rng, k: hit_concrete(rng, False, k))
    b['hit_concrete_heavy'] = ('hit_concrete', 's2', None, 3, lambda rng, k: hit_concrete(rng, True, k))
    b['hit_pen_light'] = ('hit_pen', 's1', None, 3, lambda rng, k: hit_pen(rng, False, k))
    b['hit_pen_heavy'] = ('hit_pen', 's3', None, 3, lambda rng, k: hit_pen(rng, True, k))
    b['hit_metal_light'] = ('armour_metal', 's1', None, 3, lambda rng, k: hit_metal(rng, False, k))
    b['hit_metal_heavy'] = ('armour_metal', 's3', None, 3, lambda rng, k: hit_metal(rng, True, k))
    b['hit_armour_light'] = ('hit_armour', 's1', None, 4, lambda rng, k: hit_armour(rng, 'light', k))
    b['hit_armour_heavy'] = ('hit_armour', 's3', None, 3, lambda rng, k: hit_armour(rng, 'heavy', k))
    b['hit_armour_glance'] = ('hit_armour', 's2', None, 3, lambda rng, k: hit_armour(rng, 'glance', k))
    for kind in ('tank', 'wheeled', 'truck', 'artillery', 'aircraft', 'heli', 'ship', 'drone'):
        b[f'wreck_{kind}'] = ('wreck', None, None, 2, lambda rng, k, kind=kind: wreck(rng, kind, k))
    b['crash_fall'] = ('aircraft', None, None, 2, lambda rng, k: crash_fall(rng))
    b['crash_impact'] = ('aircraft', None, None, 2, lambda rng, k: crash_impact(rng, k))
    b['smallarms_cluster'] = ('shot', 's0', None, 3, lambda rng, k: p34_cluster(4 + k, k))
    b['engine_tracked'] = ('engine', None, None, 1, lambda rng, k: engine_loop(rng, 32, 24, (150, 900), 0.12, -21.0, 55.0))
    b['engine_wheeled'] = ('engine', None, None, 1, lambda rng, k: engine_loop(rng, 46, 38, (300, 1600), 0.0, -23.0, 40.0))
    b['engine_heavy'] = ('engine', None, None, 1, lambda rng, k: engine_loop(rng, 26, 19, (120, 700), 0.05, -20.0, 62.0))
    b['ship_engine'] = ('ship', None, None, 1, lambda rng, k: ship_engine(rng))
    b['ship_horn'] = ('ship', None, None, 1, lambda rng, k: horn(rng, [110.0, 138.6], 2.6, -13.0))
    b['train_horn'] = ('train', None, None, 2, lambda rng, k: horn(rng, [311.1, 370.0, 466.2] if k == 0 else [277.2, 349.2, 415.3], 1.9, -13.5))
    b['train_rails'] = ('train', None, None, 1, lambda rng, k: rails_loop(rng))
    b['flare_pop'] = ('flare', None, None, 2, lambda rng, k: flare(rng))
    b['warn_whistle'] = ('warning', None, None, 3, lambda rng, k: whistle(rng, False))
    b['warn_whistle_big'] = ('warning', None, None, 2, lambda rng, k: whistle(rng, True))
    return b


# Kept as recorded (better than a synthesis; Resources/Audio/CREDITS.md): listed in library.json for the metrics and mixes.
KEPT = {
    'jet_loop': 'aircraft', 'jet_pass': 'aircraft', 'rotor_loop': 'helicopter', 'debris': 'wreck', 'collapse': 'wreck', 'flame': 'shot',
    'fire_loop': 'ambience', 'wind_loop': 'ambience', 'rain_loop': 'ambience', 'thunder': 'ambience', 'siren': 'warning',
    'mg': 'shot', 'autocannon': 'shot', 'cannon': 'shot', 'heavy_cannon': 'shot', 'rocket_launch': 'launch', 'missile_launch': 'launch',
    'flak': 'blast_air', 'explosion_small': 'blast', 'explosion_medium': 'blast', 'explosion_large': 'blast', 'explosion_huge': 'blast',
}


def write_ogg(path: Path, clip: np.ndarray) -> None:
    """Ogg Vorbis, mono, 44.1 kHz, written in blocks (libsndfile's Vorbis encoder overflows its stack on a long clip in one call)."""
    with sf.SoundFile(str(path), 'w', SR, 1, format='OGG', subtype='VORBIS') as f:
        for i in range(0, len(clip), 8192):
            f.write(clip[i:i + 8192])


def seed_of(name: str, k: int) -> int:
    return (sum(ord(c) * (i + 1) for i, c in enumerate(name)) * 131 + k * 7919) % (2 ** 31)


def envelope(clip: np.ndarray) -> list:
    """The clip's RMS at 50 Hz (linear, x1000, rounded): the Effects compressor's estimate of what a voice plays."""
    w = SR // 50
    frames = max(1, len(clip) // w)
    r = np.sqrt(np.mean(np.asarray(clip[:frames * w], dtype=np.float64).reshape(frames, w) ** 2, axis=1))
    return [int(round(v * 1000)) for v in r]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('only', nargs='*', help='banks to build (default: all)')
    ap.add_argument('--list', action='store_true', help='list the banks and write nothing')
    args = ap.parse_args(argv)
    all_banks = banks()
    unknown = [o for o in args.only if o not in all_banks]
    if unknown:
        sys.exit(f'unknown banks: {unknown}')
    lib = {name: {'group': g, 'size': s, 'row': r, 'variants': v} for name, (g, s, r, v, _) in all_banks.items()}
    lib.update({name: {'group': g, 'size': None, 'row': None, 'kept': True} for name, g in KEPT.items()})
    if args.list:
        for name, meta in lib.items():
            print(name, meta)
        return
    env_path = OUT / 'envelopes.txt'
    envelopes = {}
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            if line and not line.startswith('#'):
                key, rest = line.split(' ', 1)
                envelopes[key] = rest
    total = 0
    for name, (group, size, row, variants, build) in all_banks.items():
        if args.only and name not in args.only:
            continue
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        for k in range(variants):
            clip = build(np.random.default_rng(seed_of(name, k)), k)
            path = folder / f'{name}_{k + 1}.ogg'
            write_ogg(path, clip)
            envelopes[f'{name}_{k + 1}'] = ' '.join(str(v) for v in envelope(clip))
            total += path.stat().st_size
            print(f'WROTE {path.relative_to(ROOT).as_posix()}: {len(clip) / SR:.2f} s')
    for name in KEPT:
        for p in sorted((AUDIO / name).glob('*.ogg')):
            envelopes[p.stem] = ' '.join(str(v) for v in envelope(recorded(name, int(p.stem.rsplit('_', 1)[1]) - 1)))
    head = "# Fix pass L7: each clip's RMS at 50 Hz (x1000), by clip name; written by Tools/sfx/build_sfx.py for the Effects compressor.\n"
    env_path.write_text(head + '\n'.join(f'{k} {v}' for k, v in sorted(envelopes.items())) + '\n', encoding='utf-8')
    LIBRARY.write_text(json.dumps({'note': 'Fix pass L7: the sound library (Tools/sfx/build_sfx.py); sizes ' + ', '.join(
        f'{s} = {az.SIZE_NAMES[s]}' for s in SIZES), 'banks': lib}, indent=1), encoding='utf-8')
    print(f'SFX_COMPLETE {total / 1024:.0f} KB')


if __name__ == '__main__':
    main()
