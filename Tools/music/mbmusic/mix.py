"""Render a :class:`~mbmusic.score.Song` to a mastered stereo array."""

from __future__ import annotations

import time

import numpy as np

from . import SR
from . import dsp
from .render import render_midi
from .score import Song

DEFAULT_MASTER = {
    "target_lufs": -16.0,
    "ceiling_db": -1.6,  # sample-peak ceiling; leaves room for Vorbis overshoot (decoded peak <= -1 dBFS)
    "hall_rt": 2.6,
    "hall_predelay": 0.028,
    "hall_gain": 1.0,
    "room_rt": 0.85,
    "room_gain": 1.0,
    "delay_beats": 0.75,
    "delay_feedback": 0.42,
    "eq": [("hp2", 28.0), ("ls", 45.0, 0.7, -1.5), ("peak", 280.0, 0.8, -0.5), ("peak", 3500.0, 0.7, 1.0),
           ("hs", 6000.0, 0.6, 2.5)],
    "mono_below": 110.0,
    "glue": (-23.0, 1.8, 0.03, 0.30),  # threshold dB (at -20 LUFS pre-level), ratio, attack, release
}


def _log(msg: str) -> None:
    print(msg, flush=True)


def mix(song: Song, verbose: bool = True, stems_out: dict | None = None) -> np.ndarray:
    t_start = time.time()
    cfg = dict(DEFAULT_MASTER)
    cfg.update(song.master)
    total = song.total_samples
    n_loop = song.loop_samples
    ctx = dsp.Ctx(loop=song.loop)
    n_out = n_loop if song.loop else total

    # 1) render every stem on the full timeline, then fold the tail for loops
    raw: dict[str, np.ndarray] = {}
    for name in song.stems:
        buf = np.zeros((total, 2), np.float32)
        midi = song.midi_for_stem(name)
        if midi:
            buf += render_midi(midi, total)
        if song.loop:
            buf = dsp.fold(buf, n_loop)
        for stem, beat, a in song.clips:
            if stem != name:
                continue
            i0 = int(round(song.sec(beat) * SR))
            if song.loop:  # wrap clips around the loop point
                k = 0
                while k < len(a):
                    j = (i0 + k) % n_loop
                    m = min(len(a) - k, n_loop - j)
                    buf[j:j + m] += a[k:k + m]
                    k += m
            else:
                if i0 < 0:
                    a, i0 = a[-i0:], 0
                m = min(len(a), total - i0)
                if m > 0:
                    buf[i0:i0 + m] += a[:m]
        raw[name] = buf

    # 2) per-stem processing and sends
    out = np.zeros((n_out, 2), np.float32)
    sends = {"hall": np.zeros_like(out), "room": np.zeros_like(out), "delay": np.zeros_like(out)}
    triggers = [(song.sec(b), s) for b, s in song.duck_beats]
    report = []
    for name, st in song.stems.items():
        x = raw[name] * np.float32(10 ** (st.gain_db / 20))
        if not np.any(x):
            continue
        x = ctx.filt(x, dsp.eq_sos(st.eq))
        if st.drive:
            x = dsp.saturate(x, st.drive)
        if st.mono_below:
            x = dsp.mono_below(ctx, x, st.mono_below)
        if st.width != 1.0:
            x = dsp.width(x, st.width)
        if st.duck and triggers:
            env = dsp.duck_env(len(x), triggers, st.duck, st.duck_release,
                               period=n_loop if song.loop else None)
            x = x * env[:, None]
        out += x
        sends["hall"] += x * st.hall
        sends["room"] += x * st.room
        sends["delay"] += x * st.delay
        if stems_out is not None:
            stems_out[name] = x
        rms = dsp.db(float(np.sqrt(np.mean(x ** 2)) + 1e-12))
        report.append((name, rms))

    # 3) shared effects
    if np.any(sends["hall"]):
        ir = dsp.make_ir(cfg["hall_rt"], predelay=cfg["hall_predelay"], seed=song.seed * 13 + 1)
        out += ctx.conv(sends["hall"], ir) * cfg["hall_gain"]
    if np.any(sends["room"]):
        ir = dsp.make_ir(cfg["room_rt"], predelay=0.006, seed=song.seed * 13 + 2, early=20, early_span=0.035,
                         bands=((0, 300, 1.1), (300, 2500, 1.0), (2500, None, 0.6)))
        out += ctx.conv(sends["room"], ir) * cfg["room_gain"]
    if np.any(sends["delay"]):
        ir = dsp.pingpong_ir(song.sec(cfg["delay_beats"]), cfg["delay_feedback"])
        out += ctx.conv(sends["delay"], ir)

    # 4) master bus
    x = ctx.filt(out, dsp.eq_sos(cfg["eq"]))
    if cfg["mono_below"]:
        x = dsp.mono_below(ctx, x, cfg["mono_below"])
    pre = dsp.lufs(x)
    x = x * np.float32(10 ** ((-20.0 - pre) / 20))
    th, ratio, att, rel = cfg["glue"]
    x = ctx.dyn(x, lambda z: dsp.compress(z, th, ratio, att, rel))
    g = 10 ** ((cfg["target_lufs"] - dsp.lufs(x)) / 20)
    y = x
    for _ in range(4):
        y = ctx.dyn(x * np.float32(g), lambda z: dsp.limiter(z, cfg["ceiling_db"]))
        err = cfg["target_lufs"] - dsp.lufs(y)
        if abs(err) < 0.05:
            break
        g *= 10 ** (err / 20)
    pre_lim = x * np.float32(g)
    blk = int(0.4 * SR)
    nb = len(y) // blk
    if nb:
        a = np.sqrt(np.mean(pre_lim[:nb * blk].reshape(nb, blk, 2) ** 2, axis=(1, 2)) + 1e-12)
        b = np.sqrt(np.mean(y[:nb * blk].reshape(nb, blk, 2) ** 2, axis=(1, 2)) + 1e-12)
        gr = 20 * np.log10(b / a)
        lim_info = f"limiter GR per 0.4 s block: median {np.median(gr):+.2f} dB, worst {gr.min():+.2f} dB"
    else:
        lim_info = ""
    if not song.loop:
        y = _trim_tail(y, max_seconds=cfg.get("max_seconds", 9.5))
    if verbose:
        _log(f"  [{song.name}] mixed in {time.time() - t_start:.1f}s; stems (RMS dBFS before master gain):")
        for name, r in sorted(report, key=lambda z: -z[1]):
            _log(f"      {name:<14s} {r:7.1f}")
        _log(f"  [{song.name}] {len(y) / SR:.2f}s  {dsp.lufs(y):.2f} LUFS  peak {dsp.db(float(np.abs(y).max())):.2f} dBFS"
             f"  master gain {dsp.db(g):+.1f} dB")
        _log(f"  [{song.name}] {lim_info}")
    return y


def _trim_tail(y: np.ndarray, floor_db: float = -66.0, fade_s: float = 0.6, max_seconds: float = 9.5) -> np.ndarray:
    """Cut a one-shot where it decays below ``floor_db`` (or at ``max_seconds``) with a smooth fade."""
    a = np.max(np.abs(y), axis=1)
    thr = 10 ** (floor_db / 20)
    idx = np.nonzero(a > thr)[0]
    end = int(idx[-1]) + 1 if len(idx) else len(y)
    end = min(end, int(max_seconds * SR))
    y = y[:end].copy()
    f = min(len(y), int(fade_s * SR))
    y[-f:] *= (np.cos(np.linspace(0, np.pi / 2, f, dtype=np.float32)) ** 2)[:, None]
    return y
