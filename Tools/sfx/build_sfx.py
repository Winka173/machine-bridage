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
owner heard was prompt 34's blast_ap bell on every kinetic landing). Metal is two banks only, hit_metal_light / heavy, for a
kinetic round that strikes armour and does not go through.
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
SHOT_SUB = [5.0, 16.0, 32.0, 45.0, 55.0, None, 64.0, 72.0]
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


LAUNCH = {2: (-16.5, 18.0), 3: (-14.5, 30.0), 6: (-12.0, 45.0)}


def launch(rng, size: int, k: int) -> np.ndarray:
    """A rocket or a missile leaving its tube or rail: the ignition, the motor's roar going away (recorded), the sub, the tail."""
    main = recorded('rocket_launch' if size <= 2 else 'missile_launch', k)
    if size >= 3:
        main = pitched(main, 0.9 if size == 3 else 0.75)
        seconds = len(main) / SR
        t = t_axis(seconds)
        roar = filt(noise(rng, seconds), 'low', 160 if size == 3 else 110, 4)
        place(main, roar * np.clip(t / 0.06, 0, 1) * np.exp(-t / (0.5 + 0.12 * size)), 0.0, 0.8)
    decay = SHOT_TAIL[min(4, size)]
    seconds = max(len(main) / SR, decay * 6 + 0.3)
    x = np.zeros(n(seconds))
    place(x, main, 0.0)
    place(x, sub_layer(rng, seconds, 110, 50, 0.08 + 0.05 * size), 0.0, 0.7)
    place(x, tail_layer(rng, seconds, decay, 1500, size, main), 0.0)
    lufs, sub = LAUNCH[size]
    return trim_tail(master(x, lufs, sub))


# ----------------------------------------------------------------------------------------------------------- hits


def metal_ring(rng, base: float, seconds: float, decay: float) -> np.ndarray:
    """The armour plate ringing: the ONLY damped inharmonic sines of the library (group armour_metal)."""
    t = t_axis(seconds)
    out = np.zeros_like(t)
    for ratio, amp, dk in ((1.0, 1.0, 1.0), (1.47, 0.6, 0.8), (2.09, 0.4, 0.6), (2.76, 0.25, 0.45)):
        out += amp * np.sin(2 * math.pi * base * ratio * t + rng.uniform(0, 6.28)) * np.exp(-t / (decay * dk))
    return out


def hit_metal(rng, heavy: bool, k: int) -> np.ndarray:
    """A kinetic round glancing off armour it does not pierce: a hard clank, the plate ringing briefly, a spit of sparks."""
    seconds = 0.9 if heavy else 0.5
    x = np.zeros(n(seconds))
    place(x, crack(rng, 0.004, 2000), 0.0, 1.2)
    place(x, metal_ring(rng, rng.uniform(380, 520) if heavy else rng.uniform(900, 1300), seconds, 0.09 if heavy else 0.05), 0.001, 0.5)
    place(x, filt(noise(rng, 0.2), 'low', 900, 4) * env_exp(0.2, 0.05 if heavy else 0.025), 0.0, 1.2 if heavy else 0.6)
    place(x, filt(noise(rng, 0.15), 'high', 5000) * env_exp(0.15, 0.04), 0.01, 0.15)
    if heavy:
        place(x, thump(0.4, 140, 70, 0.06), 0.0, 0.6)
    return trim_tail(master(x, -16.0 if heavy else -20.0, 18.0 if heavy else 6.0))


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
    return trim_tail(master(x, -15.0 if heavy else -19.0, 40.0 if heavy else 22.0))


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
    return trim_tail(master(x, -17.0 if heavy else -22.0, 35.0 if heavy else 12.0))


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
    return trim_tail(master(x, -16.0 if heavy else -21.0, 25.0 if heavy else 10.0))


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


def cluster(rng, guns: int) -> np.ndarray:
    """Small arms as one sound: several machine guns and rifles at once, near and far (the prompt's "cụm")."""
    seconds = 1.8
    x = np.zeros(n(seconds + 0.5))
    for _ in range(guns):
        rate, far = rng.uniform(9, 16), rng.uniform(0, 1)
        tt, stop = rng.uniform(0, 0.4), rng.uniform(0.9, seconds)
        while tt < stop:
            place(x, filt(small_arms(rng), 'low', 7000 - 5000 * far), tt, (1.0 - 0.6 * far) * rng.uniform(0.7, 1.0))
            tt += 1.0 / rate * rng.uniform(0.85, 1.15)
    place(x, tail_layer(rng, seconds + 0.5, 0.15, 1500, 1), 0.0, 0.5)
    return master(fit(x, seconds), -16.0, 10.0)


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
    for name, size in {'shot_s0': 0, 'shot_s1': 1, 'shot_s2': 2, 'shot_s3': 3, 'shot_s4': 4, 'shot_s406': 6, 'shot_super': 7}.items():
        b[name] = ('shot', SIZES[size], 'shot', 3 if size < 6 else 2, lambda rng, k, s=size: gun(rng, s, k))
    for name, size in {'launch_s2': 2, 'launch_s3': 3, 'launch_big': 6}.items():
        b[name] = ('launch', SIZES[size], None, 2, lambda rng, k, s=size: launch(rng, s, k))
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
    for kind in ('tank', 'wheeled', 'truck', 'artillery', 'aircraft', 'heli', 'ship', 'drone'):
        b[f'wreck_{kind}'] = ('wreck', None, None, 2, lambda rng, k, kind=kind: wreck(rng, kind, k))
    b['crash_fall'] = ('aircraft', None, None, 2, lambda rng, k: crash_fall(rng))
    b['crash_impact'] = ('aircraft', None, None, 2, lambda rng, k: crash_impact(rng, k))
    b['smallarms_cluster'] = ('shot', 's0', None, 3, lambda rng, k: cluster(rng, 4 + k))
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
