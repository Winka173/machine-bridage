"""Objective QA for the rendered music (no ears required).

For every .ogg in the music folder (or the files given) this reports:

* duration, sample rate, channels, file size and bitrate
* integrated loudness (ITU-R BS.1770 via pyloudnorm), sample peak and 4x true peak
* clipping (samples at or above -0.1 dBFS) and DC offset per channel
* loop seam continuity: sample jump at the wrap versus the typical jump,
  RMS of the 50 ms either side of the seam, and the spectral distance of the
  0.5 s either side of the seam compared with the median over the track
* spectral balance: share of energy per band and the 2-8 kHz "harshness" share
* silence gaps: longest run of 3 s short-term loudness below -40 LUFS
* a spectrogram PNG with a short-term loudness curve (written to the build dir)

Usage: python Tools/music/analyze_music.py [files...] [--png-dir DIR] [--json FILE]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy import signal  # noqa: E402

from mbmusic import dsp  # noqa: E402
from mbmusic.paths import MUSIC_OUT, build_dir  # noqa: E402

LOOPING = {"menu", "battle_1", "battle_2", "battle_3", "boss", "siege"}
BANDS = [(20, 60, "sub"), (60, 250, "low"), (250, 2000, "mid"), (2000, 8000, "presence"), (8000, 20000, "air")]


def _db(v: float) -> float:
    return 20 * math.log10(max(v, 1e-12))


def band_shares(x: np.ndarray, sr: int) -> dict[str, float]:
    m = x.mean(axis=1)
    f, pxx = signal.welch(m, sr, nperseg=8192)
    tot = pxx[(f >= 20) & (f <= 20000)].sum()
    return {name: float(pxx[(f >= lo) & (f < hi)].sum() / tot) for lo, hi, name in BANDS}


def short_term(x: np.ndarray, sr: int, win: float = 3.0, hop: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """Approximate short-term loudness (K-weighted, ungated) over time."""
    import pyloudnorm
    meter = pyloudnorm.Meter(sr)
    # K-weighting filters from pyloudnorm's meter
    y = x.astype(np.float64)
    for _, flt in meter._filters.items():
        y = flt.apply_filter(y)
    p = np.mean(y ** 2, axis=1)
    w, h = int(win * sr), int(hop * sr)
    cs = np.concatenate([[0.0], np.cumsum(p)])
    starts = np.arange(0, max(1, len(p) - w + 1), h)
    ms = (cs[starts + w] - cs[starts]) / w
    return starts / sr + win / 2, -0.691 + 10 * np.log10(ms + 1e-12)


def _band_levels(a: np.ndarray, sr: int) -> np.ndarray:
    """Third-octave band levels (dB) of a stereo segment, 40 Hz - 16 kHz."""
    m = a.mean(axis=1) * np.hanning(len(a))
    s = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / sr)
    edges = 40 * 2 ** (np.arange(0, 29) / 3)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (f >= lo) & (f < hi)
        out.append(10 * np.log10(s[sel].sum() + 1e-12))
    return np.array(out)


def _click_ratio(x: np.ndarray, i: int, sr: int) -> float:
    """High-passed energy in 4 ms around ``i`` relative to the surrounding 200 ms (dB)."""
    sos = signal.butter(4, 5000, "highpass", fs=sr, output="sos")
    w = int(0.1 * sr)
    seg = np.concatenate([x[i - w:], x[:i + w]]) if i < w else x[i - w:i + w]
    h = signal.sosfiltfilt(sos, seg.mean(axis=1))
    c = int(0.002 * sr)
    core = np.mean(h[w - c:w + c] ** 2)
    around = np.mean(np.concatenate([h[:w - c], h[w + c:]]) ** 2)
    return 10 * np.log10((core + 1e-15) / (around + 1e-15))


def seam_report(x: np.ndarray, sr: int, meta: dict | None = None) -> dict:
    """Continuity of the wrap from the last sample back to the first."""
    d = np.abs(np.diff(x, axis=0)).max(axis=1)
    jump = float(np.abs(x[0] - x[-1]).max())
    typical = float(np.percentile(d, 99.9))
    w = int(0.05 * sr)
    rms_end = _db(float(np.sqrt(np.mean(x[-w:] ** 2))))
    rms_start = _db(float(np.sqrt(np.mean(x[:w] ** 2))))
    seg = int(0.5 * sr)
    wrap = np.concatenate([x[-seg:], x[:seg]])

    def dist(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.mean(np.abs(_band_levels(a, sr) - _band_levels(b, sr))))

    seam = dist(wrap[:seg], wrap[seg:])
    if meta:  # compare the seam with the song's own 4-bar phrase downbeats
        phrase = 4 * meta["beats_per_bar"] * 60.0 / meta["bpm"]
        pts = [int(round(k * phrase * sr)) for k in range(1, int(meta["bars"] // 4))]
        pts = [i for i in pts if seg <= i <= len(x) - seg]
    else:
        pts = list(np.random.default_rng(0).integers(seg, len(x) - seg, 60))
    ref = np.array([dist(x[i - seg:i], x[i:i + seg]) for i in pts])
    clicks = np.array([_click_ratio(x, int(i), sr) for i in pts])
    return {"jump": jump, "p999_step": typical, "rms_end_db": rms_end, "rms_start_db": rms_start,
            "band_dist_seam_db": seam, "band_dist_median_db": float(np.median(ref)),
            "band_dist_p90_db": float(np.percentile(ref, 90)),
            "seam_percentile": float((ref < seam).mean() * 100),
            "click_seam_db": _click_ratio(x, 0, sr), "click_p90_db": float(np.percentile(clicks, 90))}


def spectrogram_png(x: np.ndarray, sr: int, path: Path, title: str, st_t, st_l) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = x.mean(axis=1)
    f, t, S = signal.spectrogram(m, sr, nperseg=4096, noverlap=3072, scaling="spectrum")
    S = 10 * np.log10(S + 1e-14)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    keep = f <= 16000
    a1.pcolormesh(t, f[keep], S[keep], shading="auto", cmap="magma", vmin=S.max() - 90, vmax=S.max())
    a1.set_yscale("symlog", linthresh=200)
    a1.set_ylim(30, 16000)
    a1.set_ylabel("Hz")
    a1.set_title(title)
    a2.plot(st_t, st_l, lw=1.2)
    a2.axhline(-16, color="gray", lw=0.8, ls="--")
    a2.set_ylim(-45, -5)
    a2.set_ylabel("ST LUFS")
    a2.set_xlabel("seconds")
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


def analyze(path: Path, png_dir: Path) -> dict:
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    name = path.stem
    info = sf.info(str(path))
    size = path.stat().st_size
    dur = len(x) / sr
    tp = float(dsp.true_peak_env(x).max())
    res = {
        "file": path.name, "seconds": round(dur, 3), "sr": sr, "channels": x.shape[1],
        "bytes": size, "kbps": round(size * 8 / dur / 1000, 1), "format": f"{info.format}/{info.subtype}",
        "lufs": round(dsp.lufs(x), 2), "peak_dbfs": round(_db(float(np.abs(x).max())), 2),
        "true_peak_dbtp": round(_db(tp), 2),
        "clipped_samples": int(np.sum(np.abs(x) >= 10 ** (-0.1 / 20))),
        "dc_offset": [round(float(v), 6) for v in x.mean(axis=0)],
        "bands": {k: round(v, 4) for k, v in band_shares(x, sr).items()},
        "stereo_corr": round(float(np.corrcoef(x[:, 0], x[:, 1])[0, 1]), 3),
        "side_to_mid_db": round(_db(float(np.std(x[:, 0] - x[:, 1]))) - _db(float(np.std(x[:, 0] + x[:, 1]))), 1),
    }
    st_t, st_l = short_term(x, sr)
    quiet = st_l < -40
    longest, run = 0, 0
    for q in quiet:
        run = run + 1 if q else 0
        longest = max(longest, run)
    res["longest_quiet_s"] = round(longest * 0.5, 1)
    res["st_lufs_range"] = [round(float(np.percentile(st_l, 10)), 1), round(float(np.percentile(st_l, 95)), 1)]
    if name in LOOPING:
        mp = build_dir() / "preview" / f"{name}.json"
        meta = json.loads(mp.read_text()) if mp.exists() else None
        res["seam"] = {k: round(v, 4) for k, v in seam_report(x, sr, meta).items()}
    png_dir.mkdir(parents=True, exist_ok=True)
    spectrogram_png(x, sr, png_dir / f"{name}.png", f"{name}  {dur:.1f}s  {res['lufs']} LUFS", st_t, st_l)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--png-dir", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    files = args.files or sorted(MUSIC_OUT.glob("*.ogg"))
    png_dir = args.png_dir or build_dir() / "qa"
    out = []
    for f in files:
        r = analyze(f, png_dir)
        out.append(r)
        seam = r.get("seam")
        print(f"{r['file']:<14s} {r['seconds']:7.2f}s {r['bytes'] / 1e6:5.2f}MB {r['kbps']:5.1f}kbps "
              f"{r['lufs']:6.2f}LUFS pk {r['peak_dbfs']:6.2f} tp {r['true_peak_dbtp']:6.2f} clip {r['clipped_samples']} "
              f"dc {max(abs(v) for v in r['dc_offset']):.5f} quiet {r['longest_quiet_s']}s "
              f"ST[{r['st_lufs_range'][0]},{r['st_lufs_range'][1]}]")
        b = r["bands"]
        print(f"{'':14s} bands sub {b['sub']:.3f} low {b['low']:.3f} mid {b['mid']:.3f} "
              f"pres {b['presence']:.3f} air {b['air']:.4f}  stereo corr {r['stereo_corr']:.2f} "
              f"side/mid {r['side_to_mid_db']:.1f} dB")
        if seam:
            print(f"{'':14s} seam jump {seam['jump']:.4f} (p99.9 step {seam['p999_step']:.4f}) "
                  f"rms end/start {seam['rms_end_db']:.1f}/{seam['rms_start_db']:.1f} dB "
                  f"band dist {seam['band_dist_seam_db']:.2f} dB (median {seam['band_dist_median_db']:.2f}, "
                  f"p90 {seam['band_dist_p90_db']:.2f}, pct {seam['seam_percentile']:.0f}) "
                  f"click {seam['click_seam_db']:.1f} dB (p90 {seam['click_p90_db']:.1f})")
    if args.json:
        args.json.write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
