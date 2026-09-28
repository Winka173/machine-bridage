"""Mixing and mastering DSP in numpy/scipy.

Every processor works on float32 stereo arrays shaped ``(n, 2)``. For looping
tracks the signal is treated as periodic: filters and dynamics are run with a
wrap-around pre-roll and convolution is circular, so the last sample flows
into the first exactly as it will when the game loops the clip.
"""

from __future__ import annotations

import math

import numpy as np
import pyloudnorm
from scipy import fft as sfft
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d

from . import SR


# ----------------------------------------------------------------------------
# Biquads (RBJ audio EQ cookbook)
# ----------------------------------------------------------------------------

def biquad(kind: str, f: float, q: float = 0.7071, gain_db: float = 0.0) -> np.ndarray:
    f = min(f, SR * 0.49)
    w0 = 2 * math.pi * f / SR
    cw, sw = math.cos(w0), math.sin(w0)
    alpha = sw / (2 * q)
    A = 10 ** (gain_db / 40)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        a = [1 + alpha, -2 * cw, 1 - alpha]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        a = [1 + alpha, -2 * cw, 1 - alpha]
    elif kind == "bp":
        b = [alpha, 0, -alpha]
        a = [1 + alpha, -2 * cw, 1 - alpha]
    elif kind == "peak":
        b = [1 + alpha * A, -2 * cw, 1 - alpha * A]
        a = [1 + alpha / A, -2 * cw, 1 - alpha / A]
    elif kind in ("ls", "hs"):
        sq = 2 * math.sqrt(A) * alpha
        if kind == "ls":
            b = [A * ((A + 1) - (A - 1) * cw + sq), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sq)]
            a = [(A + 1) + (A - 1) * cw + sq, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sq]
        else:
            b = [A * ((A + 1) + (A - 1) * cw + sq), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sq)]
            a = [(A + 1) - (A - 1) * cw + sq, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sq]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    return np.concatenate([b, a])[None, :]


def eq_sos(specs) -> np.ndarray | None:
    """``specs``: list of ``(kind, freq, q, gain_db)``; 'hp2'/'lp2' = two cascaded sections."""
    secs = []
    for s in specs:
        kind, f = s[0], s[1]
        q = s[2] if len(s) > 2 else 0.7071
        g = s[3] if len(s) > 3 else 0.0
        if kind in ("hp2", "lp2"):
            secs.append(biquad(kind[:2], f, 0.541))
            secs.append(biquad(kind[:2], f, 1.307))
        else:
            secs.append(biquad(kind, f, q, g))
    return np.concatenate(secs, axis=0) if secs else None


# ----------------------------------------------------------------------------
# Loop-aware processing context
# ----------------------------------------------------------------------------

class Ctx:
    """Processing context. ``loop=True`` makes every operation periodic."""

    def __init__(self, loop: bool, pad_seconds: float = 2.0):
        self.loop = loop
        self.pad = int(pad_seconds * SR)

    def _wrap(self, x: np.ndarray, fn) -> np.ndarray:
        if not self.loop:
            return fn(x)
        p = min(self.pad, len(x))
        ext = np.concatenate([x[-p:], x, x[:p]], axis=0)
        y = fn(ext)
        return y[p:p + len(x)]

    def filt(self, x: np.ndarray, sos) -> np.ndarray:
        if sos is None:
            return x
        return self._wrap(x, lambda z: signal.sosfilt(sos, z, axis=0).astype(np.float32))

    def dyn(self, x: np.ndarray, fn) -> np.ndarray:
        return self._wrap(x, fn)

    def conv(self, x: np.ndarray, ir: np.ndarray) -> np.ndarray:
        """Channel-wise convolution (``ir`` is ``(m, 2)``); output has len(x) samples."""
        nx = len(x)
        if self.loop:
            X = sfft.rfft(x, n=nx, axis=0)
            irp = ir[:nx] if len(ir) > nx else ir
            H = sfft.rfft(irp, n=nx, axis=0)
            return sfft.irfft(X * H, n=nx, axis=0).astype(np.float32)
        nfft = sfft.next_fast_len(nx + len(ir) - 1)
        X = sfft.rfft(x, n=nfft, axis=0)
        H = sfft.rfft(ir, n=nfft, axis=0)
        return sfft.irfft(X * H, n=nfft, axis=0)[:nx].astype(np.float32)


def fold(x: np.ndarray, n: int) -> np.ndarray:
    """Fold everything after ``n`` samples back onto the start (loop tail wrap)."""
    out = np.array(x[:n], dtype=np.float32, copy=True)
    k = n
    while k < len(x):
        seg = x[k:k + n]
        out[:len(seg)] += seg
        k += n
    return out


# ----------------------------------------------------------------------------
# Reverb / delay impulse responses
# ----------------------------------------------------------------------------

def make_ir(rt60: float = 2.4, length: float | None = None, predelay: float = 0.02, seed: int = 7,
            bands=((0, 250, 1.25), (250, 1600, 1.0), (1600, 5000, 0.72), (5000, None, 0.42)),
            onset: float = 0.012, early: int = 14, early_span: float = 0.07, hp: float = 120.0) -> np.ndarray:
    """Synthetic stereo reverb impulse response with frequency-dependent decay."""
    length = length or min(6.0, rt60 * 1.35 + 0.2)
    nn = int(length * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(nn) / SR
    ir = np.zeros((nn, 2), np.float32)
    for ch in range(2):
        noise = rng.standard_normal(nn)
        acc = np.zeros(nn)
        for lo, hi, mult in bands:
            if lo == 0:
                sos = signal.butter(4, hi, "lowpass", fs=SR, output="sos")
            elif hi is None:
                sos = signal.butter(4, lo, "highpass", fs=SR, output="sos")
            else:
                sos = signal.butter(4, [lo, hi], "bandpass", fs=SR, output="sos")
            acc += signal.sosfilt(sos, noise) * 10 ** (-3 * t / (rt60 * mult))
        acc *= 1 - np.exp(-t / onset)
        rms0 = float(np.sqrt(np.mean(acc[:int(0.2 * SR)] ** 2)) + 1e-12)
        for _ in range(early):  # sparse early reflections
            d = rng.uniform(0.004, early_span)
            i = int(d * SR)
            if i < nn:
                acc[i] += rng.choice([-1.0, 1.0]) * rng.uniform(0.3, 1.0) * (1 - d / early_span) * rms0 * 25
        ir[:, ch] = acc
    if hp:
        ir = signal.sosfilt(signal.butter(2, hp, "highpass", fs=SR, output="sos"), ir, axis=0)
    pd = int(predelay * SR)
    ir = np.concatenate([np.zeros((pd, 2)), ir], axis=0)
    ir /= np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True))
    return ir.astype(np.float32)


def pingpong_ir(delay_s: float, feedback: float = 0.45, repeats: int = 6, lp: float = 4500.0) -> np.ndarray:
    d = int(delay_s * SR)
    nn = d * (repeats + 1) + 1
    ir = np.zeros((nn, 2), np.float32)
    g = 1.0
    for k in range(1, repeats + 1):
        ir[k * d, (k - 1) % 2] = g
        g *= feedback
    sos = signal.butter(2, lp, "lowpass", fs=SR, output="sos")
    return signal.sosfilt(sos, ir, axis=0).astype(np.float32)


# ----------------------------------------------------------------------------
# Dynamics
# ----------------------------------------------------------------------------

def _smooth_blocks(level_db: np.ndarray, att: float, rel: float, block: int) -> np.ndarray:
    """One-pole attack/release smoothing over a block-rate control signal."""
    a = math.exp(-block / (att * SR))
    r = math.exp(-block / (rel * SR))
    out = np.empty_like(level_db)
    s = float(level_db[0])
    for i, v in enumerate(level_db.tolist()):
        c = a if v > s else r
        s = c * s + (1 - c) * v
        out[i] = s
    return out


def compress(x: np.ndarray, thresh_db: float, ratio: float, attack: float = 0.02, release: float = 0.25,
             knee_db: float = 6.0, block: int = 32, makeup_db: float = 0.0, sidechain_hp: float = 90.0) -> np.ndarray:
    """RMS feed-forward stereo-linked compressor (block-rate control)."""
    det = x
    if sidechain_hp:
        det = signal.sosfilt(signal.butter(2, sidechain_hp, "highpass", fs=SR, output="sos"), x, axis=0)
    mono = np.mean(det ** 2, axis=1)
    nb = len(mono) // block
    if nb == 0:
        return x
    ms = mono[:nb * block].reshape(nb, block).mean(axis=1)
    lvl = 10 * np.log10(ms + 1e-12)
    lvl = _smooth_blocks(lvl, attack, release, block)
    over = lvl - thresh_db
    gr = np.where(over <= -knee_db / 2, 0.0,
                  np.where(over >= knee_db / 2, over * (1 - 1 / ratio),
                           (1 - 1 / ratio) * (over + knee_db / 2) ** 2 / (2 * knee_db)))
    g_db = -gr + makeup_db
    centers = (np.arange(nb) + 0.5) * block
    g = 10 ** (np.interp(np.arange(len(x)), centers, g_db) / 20)
    return (x * g[:, None]).astype(np.float32)


def true_peak_env(x: np.ndarray, os_factor: int = 4, chunk: int = 1 << 19) -> np.ndarray:
    """Per-sample peak of the 4x oversampled signal (approximate true peak)."""
    nn = len(x)
    out = np.empty(nn, np.float32)
    guard = 64
    for k in range(0, nn, chunk):
        a, b = max(0, k - guard), min(nn, k + chunk + guard)
        up = signal.resample_poly(x[a:b].astype(np.float32), os_factor, 1, axis=0)
        pk = np.max(np.abs(up), axis=1)
        pk = pk[:(b - a) * os_factor].reshape(b - a, os_factor).max(axis=1)
        out[k:min(nn, k + chunk)] = pk[k - a:k - a + min(chunk, nn - k)]
    return out


def limiter(x: np.ndarray, ceiling_db: float = -1.2, lookahead: float = 0.004, release: float = 0.09,
            block: int = 16) -> np.ndarray:
    """Look-ahead brick-wall limiter on 4x oversampled peaks."""
    thr = 10 ** (ceiling_db / 20)
    peak = true_peak_env(x)
    need = np.minimum(1.0, thr / (peak + 1e-12))
    la = max(1, int(lookahead * SR))
    gmin = minimum_filter1d(need, size=2 * la + 1, mode="nearest")
    nb = int(math.ceil(len(gmin) / block))
    pad = nb * block - len(gmin)
    gb = np.concatenate([gmin, np.ones(pad)]).reshape(nb, block).min(axis=1)
    r = math.exp(-block / (release * SR))
    out = np.empty(nb)
    s = 1.0
    for i, v in enumerate(gb.tolist()):
        if v < s:
            s = v  # instant attack (look-ahead already applied)
        else:
            s = min(v, 1.0 - (1.0 - s) * r)  # exponential release
        out[i] = s
    g = np.repeat(out, block)[:len(x)]
    g = uniform_filter1d(g, size=la, mode="nearest")
    y = x * g[:, None]
    return np.clip(y, -thr, thr).astype(np.float32)


def saturate(x: np.ndarray, amount: float) -> np.ndarray:
    """Gentle tanh saturation, level-compensated for small signals."""
    if amount <= 0:
        return x
    k = 1 + 6 * amount
    return (np.tanh(k * x) / k).astype(np.float32)


# ----------------------------------------------------------------------------
# Stereo tools and sidechain
# ----------------------------------------------------------------------------

def width(x: np.ndarray, w: float) -> np.ndarray:
    if w == 1.0:
        return x
    m = (x[:, 0] + x[:, 1]) * 0.5
    s = (x[:, 0] - x[:, 1]) * 0.5 * w
    return np.stack([m + s, m - s], axis=1).astype(np.float32)


def mono_below(ctx: Ctx, x: np.ndarray, f: float) -> np.ndarray:
    """Remove side-channel content below ``f`` (keeps the low end centred)."""
    m = (x[:, 0] + x[:, 1]) * 0.5
    s = (x[:, 0] - x[:, 1]) * 0.5
    s = ctx.filt(s[:, None], eq_sos([("hp2", f)]))[:, 0]
    return np.stack([m + s, m - s], axis=1).astype(np.float32)


def duck_env(n: int, triggers: list[tuple[float, float]], depth: float, release: float,
             attack: float = 0.004, period: int | None = None) -> np.ndarray:
    """Sidechain gain curve: dips by ``depth`` at each trigger ``(seconds, strength)``.

    With ``period`` the curve wraps around (for looping tracks).
    """
    env = np.zeros(n, np.float32)
    att_n = max(1, int(attack * SR))
    rel_n = int(release * 5 * SR)
    seg0 = np.concatenate([np.linspace(0, 1, att_n, endpoint=False),
                           np.exp(-np.arange(rel_n) / (release * SR))]).astype(np.float32)
    offsets = [-period, 0, period] if period else [0]
    for sec, strength in triggers:
        j0 = int(round(sec * SR)) - att_n
        for off in offsets:
            j = j0 + off
            a, b = max(0, j), min(n, j + len(seg0))
            if a < b:
                env[a:b] = np.maximum(env[a:b], strength * seg0[a - j:b - j])
    return 1 - depth * np.clip(env, 0, 1)


# ----------------------------------------------------------------------------
# Loudness
# ----------------------------------------------------------------------------

_meter = None


def lufs(x: np.ndarray) -> float:
    global _meter
    if _meter is None:
        _meter = pyloudnorm.Meter(SR)
    return float(_meter.integrated_loudness(np.asarray(x, dtype=np.float64)))


def db(v: float) -> float:
    return 20 * math.log10(max(v, 1e-12))
