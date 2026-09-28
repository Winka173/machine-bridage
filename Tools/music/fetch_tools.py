"""Download the offline tools the music build needs (not shipped with the game).

* FluidSynth 2.6.1 Windows x64 binary (LGPL-2.1; only used as an offline
  renderer). On Linux/macOS install ``fluidsynth`` with your package manager
  instead; it is picked up from PATH.
* FluidR3_GM.sf2 (MIT licence, Frank Wen) from the Debian
  ``fluid-soundfont-gm`` package, together with its copyright file.

Files go to the cache dir (``MB_MUSIC_CACHE``, default outside the repo; see
``mbmusic/paths.py``). Every download is checked against a SHA-256 hash.
"""

from __future__ import annotations

import hashlib
import io
import os
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mbmusic.paths import cache_dir  # noqa: E402

FS_URL = "https://github.com/FluidSynth/fluidsynth/releases/download/v2.6.1/fluidsynth-v2.6.1-win10-x64-cpp11.zip"
FS_SHA256 = "fab7a2e4b85675b66970f97a39bbc239729c5e0f237198b5922a6a73cbc8677c"
DEB_URL = "http://deb.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont-gm_3.1-6_all.deb"
DEB_SHA256 = "9965fbcc6acee17d6f72b685d28c7f968ec64eba14645445b476d5c6cc2eee4c"
SF2_SHA256 = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def _get(url: str, sha: str) -> bytes:
    print(f"downloading {url}")
    with urllib.request.urlopen(url) as r:
        data = r.read()
    got = hashlib.sha256(data).hexdigest()
    if got != sha:
        raise SystemExit(f"SHA-256 mismatch for {url}: {got}")
    return data


def _ar_members(data: bytes):
    """Minimal reader for the ``ar`` archive format used by .deb packages."""
    if data[:8] != b"!<arch>\n":
        raise SystemExit("not a .deb/ar archive")
    pos = 8
    while pos < len(data):
        hdr = data[pos:pos + 60]
        name = hdr[:16].decode().strip().rstrip("/")
        size = int(hdr[48:58].decode().strip())
        yield name, data[pos + 60:pos + 60 + size]
        pos += 60 + size + (size & 1)


def fetch_fluidsynth(dest: Path) -> None:
    exe = dest / "fluidsynth-v2.6.1-win10-x64-cpp11" / "bin" / "fluidsynth.exe"
    if exe.exists():
        print(f"ok: {exe}")
        return
    if os.name != "nt":
        print("non-Windows host: install FluidSynth with your package manager (apt install fluidsynth / brew "
              "install fluid-synth); build_music.py finds it on PATH.")
        return
    data = _get(FS_URL, FS_SHA256)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(dest)
    print(f"ok: {exe}")


def fetch_soundfont(dest: Path) -> None:
    sf2 = dest / "FluidR3_GM.sf2"
    if sf2.exists() and hashlib.sha256(sf2.read_bytes()).hexdigest() == SF2_SHA256:
        print(f"ok: {sf2}")
        return
    deb = _get(DEB_URL, DEB_SHA256)
    for name, body in _ar_members(deb):
        if not name.startswith("data.tar"):
            continue
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:*") as t:
            for m in t.getmembers():
                base = m.name.rsplit("/", 1)[-1]
                if base == "FluidR3_GM.sf2":
                    sf2.write_bytes(t.extractfile(m).read())
                elif m.name.endswith("fluid-soundfont-gm/copyright"):
                    (dest / "FluidR3_GM.copyright.txt").write_bytes(t.extractfile(m).read())
                elif m.name.endswith("fluid-soundfont-gm/README"):
                    (dest / "FluidR3_GM.README.txt").write_bytes(t.extractfile(m).read())
    if hashlib.sha256(sf2.read_bytes()).hexdigest() != SF2_SHA256:
        raise SystemExit("extracted SoundFont hash mismatch")
    print(f"ok: {sf2}")


def main() -> int:
    dest = cache_dir()
    print(f"cache dir: {dest}")
    fetch_fluidsynth(dest)
    fetch_soundfont(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
