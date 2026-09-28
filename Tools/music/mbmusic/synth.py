"""Numpy synth voices for the hybrid (non-orchestral) layers.

All voices return float32 arrays, mono ``(n,)`` or stereo ``(n, 2)``, at
:data:`mbmusic.SR`. They are deterministic for a given ``seed``.
"""

from __future__ import annotations

import functools
import math

import numpy as np
from scipy import signal

from . import SR
from .dsp import biquad


def mtof(p: float) -> float:
    return 440.0 * 2 ** ((p - 69) / 12)


# ----------------------------------------------------------------------------
# Oscillators and envelopes
# ----------------------------------------------------------------------------

def _blep(t: np.ndarray, dt: np.ndarray) -> np.ndarray:
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    y[m] = x * x + x + x + 1
    return y


def saw(freq, n: int, phase: float = 0.0) -> np.ndarray:
    """Band-limited (PolyBLEP) sawtooth. ``freq`` may be a scalar or per-sample array."""
    f = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    dt = f / SR
    ph = (phase + np.cumsum(dt) - dt[0]) % 1.0
    return (2 * ph - 1 - _blep(ph, dt)).astype(np.float32)


def square(freq, n: int, phase: float = 0.0, pw: float = 0.5) -> np.ndarray:
    f = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    dt = f / SR
    ph = (phase + np.cumsum(dt) - dt[0]) % 1.0
    y = np.where(ph < pw, 1.0, -1.0) + _blep(ph, dt) - _blep((ph - pw) % 1.0, dt)
    return y.astype(np.float32)


def sine(freq, n: int, phase: float = 0.0) -> np.ndarray:
    f = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    ph = phase + 2 * np.pi * (np.cumsum(f) - f[0]) / SR
    return np.sin(ph).astype(np.float32)


def adsr(n: int, a: float, d: float, s: float, r: float, gate: float | None = None) -> np.ndarray:
    """ADSR envelope of ``n`` samples; the release starts at ``gate`` seconds."""
    t = np.arange(n) / SR
    g = gate if gate is not None else n / SR - r
    env = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6) * 3))
    env_at_gate = float(np.interp(g, t, env)) if g < n / SR else s
    rel = env_at_gate * np.exp(-(t - g) / max(r, 1e-6) * 4)
    env = np.where(t < g, env, rel)
    return env.astype(np.float32)


def fade(x: np.ndarray, fin: float = 0.002, fout: float = 0.005) -> np.ndarray:
    y = np.array(x, dtype=np.float32, copy=True)
    a, b = int(fin * SR), int(fout * SR)
    if a:
        y[:a] *= np.linspace(0, 1, a, dtype=np.float32)[:, None] if y.ndim == 2 else np.linspace(0, 1, a, dtype=np.float32)
    if b:
        y[-b:] *= np.linspace(1, 0, b, dtype=np.float32)[:, None] if y.ndim == 2 else np.linspace(1, 0, b, dtype=np.float32)
    return y


def sweep_filter(x: np.ndarray, cutoff: np.ndarray, kind: str = "lp", q: float = 0.9, block: int = 64,
                 stages: int = 1) -> np.ndarray:
    """Time-varying biquad filter: coefficients updated every ``block`` samples."""
    nn = len(x)
    y = np.empty(nn, np.float32)
    zi = np.zeros((stages, 2))
    for k in range(0, nn, block):
        f = float(cutoff[min(k + block // 2, nn - 1)])
        sos = np.concatenate([biquad(kind, max(20.0, f), q)] * stages, axis=0)
        seg, zi = signal.sosfilt(sos, x[k:k + block], zi=zi)
        y[k:k + block] = seg
    return y


def pan(x: np.ndarray, p: float) -> np.ndarray:
    """Equal-power pan of a mono signal, ``p`` in -1..1."""
    a = (p + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], axis=1).astype(np.float32) * math.sqrt(2)


# ----------------------------------------------------------------------------
# Voices
# ----------------------------------------------------------------------------

@functools.lru_cache(maxsize=512)
def pulse_note(pitch: int, dur: float, vel: float = 1.0, bright: float = 1.0, detune: float = 0.08,
               decay: float = 0.12, seed: int = 0) -> np.ndarray:
    """Plucky synth-pulse note: two detuned saws + sub square, filter envelope."""
    rel = 0.06
    nn = int((dur + rel) * SR)
    f = mtof(pitch)
    x = 0.5 * saw(f * 2 ** (detune / 12), nn, 0.1 * seed) + 0.5 * saw(f * 2 ** (-detune / 12), nn, 0.37)
    x += 0.35 * square(f / 2, nn)
    t = np.arange(nn) / SR
    cut = 180 + (400 + 5200 * bright * vel) * np.exp(-t / decay)
    y = sweep_filter(x, cut, "lp", 1.1, stages=2)
    env = adsr(nn, 0.003, dur * 0.6, 0.55, rel, gate=dur)
    return (y * env * vel * 0.5).astype(np.float32)


@functools.lru_cache(maxsize=256)
def bass_note(pitch: int, dur: float, vel: float = 1.0, drive: float = 0.4, cutoff: float = 900.0) -> np.ndarray:
    """Hybrid synth bass: saw + sine sub, short filter blip, soft drive (mono)."""
    rel = 0.05
    nn = int((dur + rel) * SR)
    f = mtof(pitch)
    t = np.arange(nn) / SR
    x = 0.6 * saw(f, nn) + 0.9 * sine(f, nn) + 0.25 * saw(f * 1.004, nn, 0.5)
    cut = 120 + cutoff * vel * np.exp(-t / 0.09) + 180
    y = sweep_filter(x, cut, "lp", 0.8, stages=2)
    y = np.tanh(y * (1 + 3 * drive)) / (1 + drive)
    env = adsr(nn, 0.002, 0.2, 0.8, rel, gate=dur)
    return (y * env * vel * 0.6).astype(np.float32)


def braam(pitches, dur: float, vel: float = 1.0, open_time: float = 0.6, seed: int = 3,
          bright: float = 1.0) -> np.ndarray:
    """Trailer 'braam': stacked detuned saws, opening filter, drive, stereo."""
    rng = np.random.default_rng(seed)
    nn = int((dur + 1.2) * SR)
    t = np.arange(nn) / SR
    out = np.zeros((nn, 2), np.float32)
    for p in pitches:
        f = mtof(p)
        for v in range(6):
            det = rng.uniform(-0.12, 0.12)
            drift = 1 + 0.0015 * np.sin(2 * np.pi * rng.uniform(0.1, 0.4) * t + rng.uniform(0, 6))
            osc = saw(f * 2 ** (det / 12) * drift, nn, rng.uniform())
            pn = rng.uniform(-0.8, 0.8)
            out += pan(osc, pn) * (1 / 6)
    cut = 90 + 2600 * bright * (1 - np.exp(-t / open_time)) * np.exp(-np.maximum(0, t - dur * 0.5) / (dur * 0.6))
    for ch in range(2):
        out[:, ch] = sweep_filter(out[:, ch], cut, "lp", 1.0, block=128, stages=2)
    out = np.tanh(out * 2.2) / 1.6
    sub = sine(mtof(min(pitches)), nn) * 0.55
    out += sub[:, None]
    env = adsr(nn, 0.03, dur * 0.8, 0.7, 1.0, gate=dur)
    return (out * env[:, None] * vel).astype(np.float32)


def boom(dur: float = 2.5, f0: float = 78.0, f1: float = 34.0, vel: float = 1.0, seed: int = 5,
         noise: float = 0.35) -> np.ndarray:
    """Cinematic sub impact: pitch-dropping sine, click and rumble."""
    rng = np.random.default_rng(seed)
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.09)
    body = sine(f, nn) * np.exp(-t / 0.55)
    click = rng.standard_normal(nn) * np.exp(-t / 0.006)
    click = signal.sosfilt(signal.butter(2, 3500, "lowpass", fs=SR, output="sos"), click)
    rum = rng.standard_normal((nn, 2))
    rum = signal.sosfilt(signal.butter(2, [40, 220], "bandpass", fs=SR, output="sos"), rum, axis=0)
    rum *= (np.exp(-t / 0.9) * (1 - np.exp(-t / 0.02)))[:, None]
    y = (body + 0.25 * click)[:, None] + noise * rum * 2.5
    return fade((y * vel * 0.9).astype(np.float32), 0.0005, 0.2)


def thump(vel: float = 1.0, f0: float = 120.0, f1: float = 52.0, decay: float = 0.28) -> np.ndarray:
    """Short low drum reinforcement (layer under taiko hits)."""
    nn = int((decay * 4) * SR)
    t = np.arange(nn) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.03)
    y = sine(f, nn) * np.exp(-t / decay)
    y = np.tanh(1.6 * y) / 1.2
    return fade((y * vel).astype(np.float32), 0.0003, 0.05)


def riser(dur: float, vel: float = 1.0, f0: float = 300.0, f1: float = 9000.0, seed: int = 9,
          tone: float = 0.25, tone_pitch: float = 48) -> np.ndarray:
    """Noise riser that ends exactly at ``dur`` (place it so it ends on a downbeat)."""
    rng = np.random.default_rng(seed)
    nn = int(dur * SR)
    u = np.linspace(0, 1, nn)
    cut = f0 * (f1 / f0) ** (u ** 1.6)
    out = np.zeros((nn, 2), np.float32)
    for ch in range(2):
        nz = rng.standard_normal(nn).astype(np.float32)
        out[:, ch] = sweep_filter(nz, cut, "bp", 1.4, block=128)
    if tone:
        fr = mtof(tone_pitch) * 2 ** (2.0 * u ** 1.5)
        tn = saw(fr, nn) + saw(fr * 1.5, nn, 0.3) * 0.5
        tn = sweep_filter(tn, cut * 0.5 + 200, "lp", 0.8, block=128)
        out += tone * pan(tn, 0.0) * 0.5
    env = (u ** 2.2)
    out *= env[:, None] * vel
    return fade(out, 0.01, 0.012)


def reverse_swell(dur: float, vel: float = 1.0, seed: int = 11, lp: float = 6000.0) -> np.ndarray:
    """Reverse-cymbal style swell (decaying filtered noise, time reversed)."""
    rng = np.random.default_rng(seed)
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    nz = rng.standard_normal((nn, 2))
    nz = signal.sosfilt(signal.butter(2, [1800, lp], "bandpass", fs=SR, output="sos"), nz, axis=0)
    y = nz * np.exp(-t / (dur * 0.35))[:, None]
    return fade((y[::-1] * vel * 0.8).astype(np.float32), 0.02, 0.006)


@functools.lru_cache(maxsize=64)
def hat(open_: bool = False, vel: float = 1.0, seed: int = 1) -> np.ndarray:
    """Metallic hi-hat (six detuned squares + noise, band-passed)."""
    rng = np.random.default_rng(seed)
    dec = 0.16 if open_ else 0.035
    nn = int(dec * 6 * SR)
    t = np.arange(nn) / SR
    ratios = (2.0, 3.0, 4.16, 5.43, 6.79, 8.21)
    m = sum(square(205.3 * r, nn, rng.uniform()) for r in ratios) / 6
    m = m + 0.6 * rng.standard_normal(nn)
    m = signal.sosfilt(signal.butter(2, [6500, 13000], "bandpass", fs=SR, output="sos"), m)
    y = m * np.exp(-t / dec) * vel
    return fade(y.astype(np.float32), 0.0005, 0.01)


@functools.lru_cache(maxsize=64)
def tick(pitch: float = 84.0, vel: float = 1.0) -> np.ndarray:
    """Clock-like tick: short sine blip plus a noise click."""
    nn = int(0.09 * SR)
    t = np.arange(nn) / SR
    y = sine(mtof(pitch), nn) * np.exp(-t / 0.012)
    nz = np.random.default_rng(int(pitch)).standard_normal(nn) * np.exp(-t / 0.003) * 0.3
    nz = signal.sosfilt(signal.butter(2, 2500, "highpass", fs=SR, output="sos"), nz)
    return fade(((y + nz) * vel * 0.6).astype(np.float32), 0.0003, 0.01)


def drone(pitch: int, dur: float, vel: float = 1.0, seed: int = 21, bright: float = 0.35) -> np.ndarray:
    """Dark evolving low drone (stereo), fades in and out over its length."""
    rng = np.random.default_rng(seed)
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    f = mtof(pitch)
    out = np.zeros((nn, 2), np.float32)
    for k in range(4):
        det = rng.uniform(-0.07, 0.07)
        osc = saw(f * 2 ** (det / 12), nn, rng.uniform())
        out += pan(osc, rng.uniform(-0.7, 0.7)) * 0.25
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + rng.uniform(0, 6))
    cut = 110 + 900 * bright * lfo
    for ch in range(2):
        out[:, ch] = sweep_filter(out[:, ch], cut, "lp", 0.7, block=256, stages=2)
    out += 0.6 * sine(f, nn)[:, None]
    env = np.minimum(1, np.minimum(t / 1.5, (dur - t) / 1.5)).clip(0, 1)
    return (out * env[:, None] * vel).astype(np.float32)


def supersaw_pad(pitches, dur: float, vel: float = 1.0, seed: int = 31, cutoff: float = 1800.0,
                 attack: float = 0.8, release: float = 1.5) -> np.ndarray:
    """Wide supersaw pad chord for the hybrid tracks."""
    rng = np.random.default_rng(seed)
    nn = int((dur + release) * SR)
    t = np.arange(nn) / SR
    out = np.zeros((nn, 2), np.float32)
    for p in pitches:
        f = mtof(p)
        for v in range(5):
            det = (v - 2) * 0.09 + rng.uniform(-0.02, 0.02)
            out += pan(saw(f * 2 ** (det / 12), nn, rng.uniform()), (v - 2) / 2.2) * 0.2
    lfo = 1 + 0.15 * np.sin(2 * np.pi * 0.2 * t)
    for ch in range(2):
        out[:, ch] = sweep_filter(out[:, ch], cutoff * lfo, "lp", 0.7, block=256, stages=2)
    env = adsr(nn, attack, 1.0, 0.85, release, gate=dur)
    return (out * env[:, None] * vel / max(1, len(pitches)) ** 0.5).astype(np.float32)


@functools.lru_cache(maxsize=32)
def clap(vel: float = 1.0, seed: int = 4) -> np.ndarray:
    """Layered hand-clap: three short noise bursts and a short tail."""
    rng = np.random.default_rng(seed)
    nn = int(0.35 * SR)
    t = np.arange(nn) / SR
    env = np.zeros(nn)
    for k, d in enumerate((0.0, 0.009, 0.018)):
        tt = np.clip(t - d, 0, None)
        env += (t >= d) * np.exp(-tt / 0.004) * (0.8 + 0.1 * k)
    env += (t >= 0.02) * np.exp(-np.clip(t - 0.02, 0, None) / 0.07) * 0.6
    nz = rng.standard_normal((nn, 2))
    nz = signal.sosfilt(signal.butter(2, [900, 4200], "bandpass", fs=SR, output="sos"), nz, axis=0)
    return fade((nz * env[:, None] * vel * 1.4).astype(np.float32), 0.0003, 0.02)


@functools.lru_cache(maxsize=32)
def clang(pitch: float = 64.0, vel: float = 1.0, decay: float = 1.4, seed: int = 8) -> np.ndarray:
    """Metallic anvil/plate hit (modal synthesis): the 'machine' colour."""
    rng = np.random.default_rng(seed)
    nn = int(decay * 3 * SR)
    t = np.arange(nn) / SR
    f0 = mtof(pitch)
    ratios = (1.0, 2.32, 2.76, 4.25, 5.40, 6.9, 8.93, 11.2)
    y = np.zeros(nn)
    for k, r in enumerate(ratios):
        a = 1.0 / (1 + 0.6 * k)
        d = decay / (1 + 0.45 * k)
        y += a * np.sin(2 * np.pi * f0 * r * (1 + rng.uniform(-0.004, 0.004)) * t + rng.uniform(0, 6)) * np.exp(-t / d)
    hit = rng.standard_normal(nn) * np.exp(-t / 0.004)
    hit = signal.sosfilt(signal.butter(2, 2000, "highpass", fs=SR, output="sos"), hit)
    y = y * 0.3 + 0.35 * hit
    left = y
    right = np.concatenate([np.zeros(int(0.0007 * SR)), y])[:nn]
    return fade((np.stack([left, right], axis=1) * vel).astype(np.float32), 0.0002, 0.05)
