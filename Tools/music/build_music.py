"""Compose, render, master and encode the Machine Brigade soundtrack.

Usage (from the repo root or anywhere):

    python Tools/music/fetch_tools.py            # once: FluidSynth + SoundFont
    python Tools/music/build_music.py            # all tracks -> Assets/.../Audio/Music/*.ogg
    python Tools/music/build_music.py menu boss  # selected tracks only
    python Tools/music/build_music.py --wav-only # preview WAVs in the build dir, no .ogg

Outputs go to ``Assets/MachineBrigade/Resources/Audio/Music``; preview WAVs,
the FluidSynth render cache and QA files go to the build dir (see
``mbmusic/paths.py``).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

from mbmusic import SR  # noqa: E402
from mbmusic.mix import mix  # noqa: E402
from mbmusic.paths import MUSIC_OUT, build_dir  # noqa: E402
from mbmusic.tracks import TRACKS, build  # noqa: E402

OGG_QUALITY = 0.5  # Vorbis quality 0..1 (libsndfile maps compression_level = 1 - quality)


def encode_ogg(y: np.ndarray, path: Path, quality: float = OGG_QUALITY) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.ogg")
    # libsndfile's Vorbis encoder overflows the stack on large single writes
    # (seen on Windows), so feed it in small blocks.
    with sf.SoundFile(str(tmp), "w", SR, y.shape[1], format="OGG", subtype="VORBIS",
                      compression_level=1.0 - quality) as f:
        for k in range(0, len(y), 4096):
            f.write(y[k:k + 4096])
    tmp.replace(path)


def _kweight(x: np.ndarray) -> np.ndarray:
    import pyloudnorm
    y = x.astype(np.float64)
    for flt in pyloudnorm.Meter(SR)._filters.values():
        y = flt.apply_filter(y)
    return y


def stem_table(song, stems: dict, y: np.ndarray, block_bars: int = 4) -> None:
    """Per-stem K-weighted level (LUFS-like, ungated) per block of bars, for balancing."""
    blk = int(round(song.sec(song.beats_per_bar * block_bars) * SR))
    nb = int(np.ceil(len(y) / blk))
    print("  stem loudness (K-weighted dB, pre master gain) per %d-bar block:" % block_bars)
    print("  %-10s" % "bar" + "".join(f"{i * block_bars:>5d}" for i in range(nb)))
    rows = sorted(stems.items()) + [("MASTER", y)]
    for name, x in rows:
        k = _kweight(x)
        row = []
        for i in range(nb):
            seg = k[i * blk:(i + 1) * blk]
            ms = float(np.mean(np.sum(seg ** 2, axis=1))) if len(seg) else 0.0
            row.append(f"{-0.691 + 10 * np.log10(ms):5.0f}" if ms > 1e-10 else "    .")
        print("  %-10s" % name + "".join(row))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tracks", nargs="*", help=f"subset of: {', '.join(TRACKS)}")
    ap.add_argument("--wav-only", action="store_true", help="write preview WAVs only")
    ap.add_argument("--quality", type=float, default=OGG_QUALITY, help="Vorbis quality 0..1 (default 0.5)")
    ap.add_argument("--out", type=Path, default=MUSIC_OUT, help="output folder for .ogg files")
    ap.add_argument("--stems", action="store_true", help="print per-stem RMS per 4-bar block (mix balancing)")
    args = ap.parse_args()
    names = args.tracks or list(TRACKS)
    for nm in names:
        if nm not in TRACKS:
            ap.error(f"unknown track {nm!r}")
    prev = build_dir() / "preview"
    prev.mkdir(parents=True, exist_ok=True)
    for nm in names:
        t0 = time.time()
        print(f"== {nm}", flush=True)
        song = build(nm)
        stems = {} if args.stems else None
        y = mix(song, stems_out=stems)
        if stems:
            stem_table(song, stems, y)
        sf.write(str(prev / f"{nm}.wav"), y, SR, subtype="FLOAT")
        meta = {"bpm": song.bpm, "beats_per_bar": song.beats_per_bar, "bars": song.bars, "loop": song.loop}
        (prev / f"{nm}.json").write_text(json.dumps(meta))
        if not args.wav_only:
            out = args.out / f"{nm}.ogg"
            encode_ogg(y, out, args.quality)
            print(f"  -> {out}  ({out.stat().st_size / 1e6:.2f} MB, {len(y) / SR:.2f}s) in {time.time() - t0:.0f}s",
                  flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
