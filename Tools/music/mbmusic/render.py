"""Offline FluidSynth rendering with a content-addressed WAV cache."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from . import SR
from .paths import cache_dir, build_dir

FS_VERSION = "2.6.1"
SF2_NAME = "FluidR3_GM.sf2"
# FluidSynth processes audio in 64-sample blocks; a note-on at tick 0 starts
# sounding one block later. Removing it keeps MIDI stems aligned with clips.
FS_LATENCY = 64


def find_fluidsynth() -> str:
    env = os.environ.get("MB_FLUIDSYNTH")
    if env and Path(env).exists():
        return env
    local = cache_dir() / f"fluidsynth-v{FS_VERSION}-win10-x64-cpp11" / "bin" / "fluidsynth.exe"
    if local.exists():
        return str(local)
    on_path = shutil.which("fluidsynth")
    if on_path:
        return on_path
    raise FileNotFoundError("FluidSynth not found; run `python fetch_tools.py` or set MB_FLUIDSYNTH")


def find_soundfont() -> str:
    env = os.environ.get("MB_SOUNDFONT")
    if env and Path(env).exists():
        return env
    local = cache_dir() / SF2_NAME
    if local.exists():
        return str(local)
    raise FileNotFoundError("FluidR3_GM.sf2 not found; run `python fetch_tools.py` or set MB_SOUNDFONT")


def render_midi(midi_bytes: bytes, n_samples: int, gain: float = 0.5) -> np.ndarray:
    """Render MIDI bytes to a float32 stereo array of exactly ``n_samples``."""
    fs = find_fluidsynth()
    sf2 = find_soundfont()
    args = ["-ni", "-q", "-r", str(SR), "-O", "float", "-T", "wav", "-g", f"{gain}",
            "-o", "synth.reverb.active=0", "-o", "synth.chorus.active=0",
            "-o", "synth.polyphony=2048", "-o", "synth.sample-rate=%d" % SR]
    key = hashlib.sha256(midi_bytes + " ".join(args).encode() + Path(sf2).name.encode()).hexdigest()[:24]
    out_dir = build_dir() / "fs_cache"
    out_dir.mkdir(parents=True, exist_ok=True)
    wav = out_dir / f"{key}.wav"
    if not wav.exists():
        mid = out_dir / f"{key}.mid"
        mid.write_bytes(midi_bytes)
        tmp = out_dir / f"{key}.tmp.wav"
        subprocess.run([fs, *args, "-F", str(tmp), sf2, str(mid)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(tmp, wav)
        mid.unlink(missing_ok=True)
    x, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    assert sr == SR, sr
    x = x[FS_LATENCY:]
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    out = np.zeros((n_samples, 2), dtype=np.float32)
    m = min(n_samples, len(x))
    out[:m] = x[:m]
    return out
