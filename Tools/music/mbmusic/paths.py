"""Filesystem locations used by the music tools.

* ``MB_MUSIC_CACHE``: downloaded FluidSynth + SoundFont (default: outside the
  repo, ``%LOCALAPPDATA%/MachineBrigade/music-cache`` or
  ``~/.cache/machinebrigade-music``).
* ``MB_MUSIC_BUILD``: render cache, preview WAVs and QA images
  (default: ``<cache>/build``).
"""

from __future__ import annotations

import os
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = TOOLS_DIR.parent.parent
MUSIC_OUT = REPO_ROOT / "Assets" / "MachineBrigade" / "Resources" / "Audio" / "Music"


def cache_dir() -> Path:
    env = os.environ.get("MB_MUSIC_CACHE")
    if env:
        p = Path(env)
    elif os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        p = Path(os.environ["LOCALAPPDATA"]) / "MachineBrigade" / "music-cache"
    else:
        p = Path.home() / ".cache" / "machinebrigade-music"
    p.mkdir(parents=True, exist_ok=True)
    return p


def build_dir() -> Path:
    env = os.environ.get("MB_MUSIC_BUILD")
    p = Path(env) if env else cache_dir() / "build"
    p.mkdir(parents=True, exist_ok=True)
    return p
