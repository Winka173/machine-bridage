"""Fix pass L7: objective numbers for every battle sound (rerunnable; no Unity).

    python Tools/sfx/analyze_sfx.py                      # every clip under Resources/Audio (not Music) -> Docs/audio/metrics.md + .json
    python Tools/sfx/analyze_sfx.py --rev 01f19757~1     # the clips as they were at a git revision (read with git show)
    python Tools/sfx/analyze_sfx.py --json-only out.json # numbers only
    python Tools/sfx/analyze_sfx.py --check              # exit 1 when a clip outside the armour-hit group is a "keng" or the size table does not rise

Per clip:
  * loudness: integrated LUFS (ITU-R BS.1770-4: K-weighting, 400 ms blocks, -70 LUFS and -10 LU gates; a clip shorter than a
    block is measured as one block of its own length) and the momentary maximum (the loudest 400 ms; what a one-shot "hits" at);
  * peak: sample peak and a 4x oversampled true peak, dBFS;
  * sub: the share of the clip's energy under 150 Hz (%);
  * tail: seconds from the peak until the 10 ms envelope falls 40 dB under it and stays there;
  * keng: a narrow peak between 2 and 6 kHz that rings on. The spectrum of the part 30-400 ms after the onset is compared with
    its own 1/3-octave median; the strongest 2-6 kHz bin's prominence over that median (dB) and the time the bin itself takes
    to fall 20 dB (s); a bin more than KENG_FLOOR dB under the window's loudest is not heard and is skipped. keng = prominence >= KENG_PROMINENCE dB and decay >= KENG_DECAY s and a -6 dB width under KENG_WIDTH Hz.

The size table reads Tools/sfx/library.json (written by build_sfx.py): each bank's group and size class; it must rise steadily
(louder, deeper, longer) from <= 14.5 mm to the super weapons, for the shots and for the blasts.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Audio'
LIBRARY = ROOT / 'Tools' / 'sfx' / 'library.json'
OUT_DIR = ROOT / 'Docs' / 'audio'

KENG_BAND = (2000.0, 6000.0)
KENG_PROMINENCE = 12.0  # dB over the 1/3-octave median
KENG_DECAY = 0.12  # s for the peak bin to fall 20 dB
KENG_WIDTH = 160.0  # Hz, the peak's -6 dB width
KENG_FLOOR = 30.0  # dB: a peak further than this under the window's loudest bin is not heard as a ring

SIZES = ['s0', 's1', 's2', 's3', 's4', 'bomb', 's406', 'super']
SIZE_NAMES = {
    's0': '<= 14.5 mm', 's1': '20-40 mm', 's2': '57-105 mm', 's3': '120-155 mm', 's4': '203-240 mm',
    'bomb': 'bombs', 's406': 'big rockets / >= 406 mm', 'super': 'super weapons',
}


# ------------------------------------------------------------------------------------------------------- loading


def load_bytes(data: bytes):
    x, sr = sf.read(io.BytesIO(data), dtype='float64', always_2d=True)
    return x.mean(axis=1), sr


def load(path: Path):
    return load_bytes(path.read_bytes())


def clips_at(rev: str | None):
    """(relative name, samples, rate) for every clip under Resources/Audio but Music; at a git revision when given."""
    if rev is None:
        for p in sorted(AUDIO.rglob('*.ogg')):
            rel = p.relative_to(AUDIO).as_posix()
            if rel.startswith('Music/'):
                continue
            x, sr = load(p)
            yield rel, x, sr
        return
    prefix = 'Assets/MachineBrigade/Resources/Audio/'
    names = subprocess.run(['git', 'ls-tree', '-r', '--name-only', rev, prefix], cwd=ROOT, capture_output=True, text=True,
                           check=True).stdout.split()
    for name in sorted(names):
        if not name.endswith('.ogg') or name[len(prefix):].startswith('Music/'):
            continue
        data = subprocess.run(['git', 'show', f'{rev}:{name}'], cwd=ROOT, capture_output=True, check=True).stdout
        if data.startswith(b'version https://git-lfs'):
            continue
        x, sr = load_bytes(data)
        yield name[len(prefix):], x, sr


# ------------------------------------------------------------------------------------------------------- measures


def k_weight(x: np.ndarray, sr: int) -> np.ndarray:
    """BS.1770 K-weighting: the high shelf (+4 dB over ~1.5 kHz) and the RLB high pass, by the standard's analogue prototypes."""
    # Stage 1: high shelf.
    f0, g, q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    k = math.tan(math.pi * f0 / sr)
    vh = 10 ** (g / 20)
    vb = vh ** 0.4996667741545416
    a0 = 1 + k / q + k * k
    b = [(vh + vb * k / q + k * k) / a0, 2 * (k * k - vh) / a0, (vh - vb * k / q + k * k) / a0]
    a = [1, 2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0]
    y = signal.lfilter(b, a, x)
    # Stage 2: high pass.
    f0, q = 38.13547087602444, 0.5003270373238773
    k = math.tan(math.pi * f0 / sr)
    a0 = 1 + k / q + k * k
    a = [1, 2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0]
    return signal.lfilter([1, -2, 1], a, y)


def loudness(x: np.ndarray, sr: int):
    """(integrated LUFS, momentary max LUFS)."""
    y = k_weight(x, sr)
    block = int(0.4 * sr)
    if len(y) < block:
        ms = float(np.mean(y ** 2)) if len(y) else 0.0
        v = -0.691 + 10 * math.log10(ms) if ms > 0 else -120.0
        return v, v
    hop = block // 4
    powers = np.array([np.mean(y[i:i + block] ** 2) for i in range(0, len(y) - block + 1, hop)])
    with np.errstate(divide='ignore'):
        lk = -0.691 + 10 * np.log10(np.maximum(powers, 1e-20))
    mmax = float(lk.max())
    gated = powers[lk > -70]
    if len(gated) == 0:
        return -120.0, mmax
    rel = -0.691 + 10 * math.log10(gated.mean()) - 10
    gated = powers[(lk > -70) & (lk > rel)]
    return -0.691 + 10 * math.log10(gated.mean()), mmax


def db(v: float) -> float:
    return 20 * math.log10(v) if v > 1e-12 else -120.0


def peaks(x: np.ndarray):
    sample = float(np.max(np.abs(x))) if len(x) else 0.0
    true = float(np.max(np.abs(signal.resample_poly(x, 4, 1)))) if len(x) else 0.0
    return db(sample), db(max(sample, true))


def sub_share(x: np.ndarray, sr: int, cut: float = 150.0) -> float:
    spec = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    total = spec[freqs >= 20].sum()
    return float(spec[(freqs >= 20) & (freqs < cut)].sum() / total * 100) if total > 0 else 0.0


def envelope_db(x: np.ndarray, sr: int, ms: float = 10.0) -> np.ndarray:
    w = max(1, int(sr * ms / 1000))
    frames = len(x) // w
    if frames == 0:
        return np.array([db(float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0)])
    r = np.sqrt(np.mean(x[:frames * w].reshape(frames, w) ** 2, axis=1))
    return 20 * np.log10(np.maximum(r, 1e-9))


def tail_seconds(x: np.ndarray, sr: int, drop: float = 40.0) -> float:
    env = envelope_db(x, sr)
    top = int(np.argmax(env))
    above = np.nonzero(env[top:] > env[top] - drop)[0]
    last = above[-1] if len(above) else 0
    return float(last * 0.01)


def keng(x: np.ndarray, sr: int):
    """(prominence dB, decay s, width Hz, frequency Hz, is keng) of the strongest narrow 2-6 kHz peak after the onset."""
    env = envelope_db(x, sr, 2.0)
    onset = int(np.argmax(env > env.max() - 20)) * int(sr * 0.002)
    a, b = onset + int(0.03 * sr), onset + int(0.4 * sr)
    seg = x[a:min(b, len(x))]
    if len(seg) < 2048:
        return 0.0, 0.0, 0.0, 0.0, False
    f, t, z = signal.stft(x[a:], sr, nperseg=2048, noverlap=1536)
    mag = np.abs(z)
    span = max(1, int(round((0.4 - 0.03) / (t[1] - t[0]))) if len(t) > 1 else 1)
    avg = 20 * np.log10(np.maximum(mag[:, :span].mean(axis=1), 1e-12))
    band = np.nonzero((f >= KENG_BAND[0]) & (f <= KENG_BAND[1]))[0]
    best = (0.0, 0.0, 0.0, 0.0, False)
    loudest = float(avg.max())
    # 1/3-octave running median as the "smooth" spectrum a ring would stand out of.
    for i in band:
        lo, hi = np.searchsorted(f, f[i] / 2 ** (1 / 6)), np.searchsorted(f, f[i] * 2 ** (1 / 6))
        med = float(np.median(avg[lo:max(lo + 1, hi)]))
        prom = avg[i] - med
        if prom <= best[0] or avg[i] < loudest - KENG_FLOOR:
            continue
        # A local maximum only.
        if avg[i] < avg[max(0, i - 1)] or avg[i] < avg[min(len(avg) - 1, i + 1)]:
            continue
        j0 = i
        while j0 > 0 and avg[j0] > avg[i] - 6:
            j0 -= 1
        j1 = i
        while j1 < len(avg) - 1 and avg[j1] > avg[i] - 6:
            j1 += 1
        width = float(f[j1] - f[j0])
        track = 20 * np.log10(np.maximum(mag[i], 1e-12))
        k0 = int(np.argmax(track[:span]))
        fall = np.nonzero(track[k0:] < track[k0] - 20)[0]
        decay = float((fall[0] if len(fall) else len(track) - k0) * (t[1] - t[0])) if len(t) > 1 else 0.0
        best = (float(prom), decay, width, float(f[i]), prom >= KENG_PROMINENCE and decay >= KENG_DECAY and width <= KENG_WIDTH)
    return best


def analyse(x: np.ndarray, sr: int) -> dict:
    lufs, mmax = loudness(x, sr)
    peak, true = peaks(x)
    prom, decay, width, freq, is_keng = keng(x, sr)
    return {
        'seconds': round(len(x) / sr, 3), 'lufs': round(lufs, 1), 'lufs_mmax': round(mmax, 1), 'peak': round(peak, 1),
        'true_peak': round(true, 1), 'sub150': round(sub_share(x, sr), 1), 'tail': round(tail_seconds(x, sr), 2),
        'keng_prominence': round(prom, 1), 'keng_decay': round(decay, 3), 'keng_width': round(width, 0), 'keng_hz': round(freq, 0),
        'keng': bool(is_keng),
    }


# ------------------------------------------------------------------------------------------------------- report


# What each size played before this pass (prompt 34 L6's banks; Docs/audio/diagnosis.md): the shot, and the blast or hit.
BEFORE_MAP = {
    's0': ('p34/shot_t0', 'impact_metal'), 's1': ('p34/shot_t1', 'p34/blast_he_t1'), 's2': ('p34/shot_t2', 'p34/blast_he_t2'),
    's3': ('p34/shot_t3', 'p34/blast_he_t3'), 's4': ('p34/shot_t4', 'p34/blast_he_t4'), 'bomb': (None, 'p34/blast_he_t4'),
    's406': ('p34/shot_t5', 'p34/blast_he_t5'), 'super': ('p34/shot_t5', 'p34/blast_he_t5'),
}


def bank_of(rel: str) -> str:
    parts = rel.split('/')
    return '/'.join(parts[:-1]) if len(parts) > 1 else parts[0]


def library():
    if not LIBRARY.exists():
        return {}
    return json.loads(LIBRARY.read_text(encoding='utf-8'))['banks']


def size_table(per_bank: dict, lib: dict):
    """Per size class: the shot's and the blast's mean numbers (from the library's banks marked 'size_row')."""
    rows = []
    for size in SIZES:
        row = {'size': size, 'name': SIZE_NAMES[size]}
        for role in ('shot', 'blast'):
            names = [b for b, meta in lib.items() if meta.get('size') == size and meta.get('row') == role]
            ms = [per_bank[f'sfx/{b}'] for b in names if f'sfx/{b}' in per_bank]
            if ms:
                row[role] = {k: round(float(np.mean([m[k] for m in ms])), 2) for k in ('lufs_mmax', 'lufs', 'sub150', 'tail')}
                row[role]['banks'] = names
        rows.append(row)
    return rows


def rises(rows, role: str):
    """The steps where the table does not rise (louder, deeper, longer)."""
    bad = []
    prev = None
    for r in rows:
        m = r.get(role)
        if m is None:
            continue
        if prev is not None:
            for key in ('lufs_mmax', 'sub150', 'tail'):
                if m[key] <= prev[1][key]:
                    bad.append(f'{role} {key}: {prev[0]} {prev[1][key]} -> {r["size"]} {m[key]}')
        prev = (r['size'], m)
    return bad


def keng_outside_armour(clips: dict, lib: dict):
    out = []
    for rel, m in clips.items():
        if not m['keng']:
            continue
        bank = bank_of(rel)
        group = lib.get(bank[4:], {}).get('group') if bank.startswith('sfx/') else None
        if group != 'armour_metal':
            out.append(rel)
    return out


def write_md(clips: dict, rows, problems, kengs, path: Path, title: str, before: dict | None):
    banks = {}
    for rel, m in clips.items():
        banks.setdefault(bank_of(rel), []).append(m)
    lines = [f'# {title}', '',
             'Written by `python Tools/sfx/analyze_sfx.py` (rerunnable; the numbers come from the .ogg files, nothing by hand).',
             'LUFS: ITU-R BS.1770-4 integrated; M-max: the loudest 400 ms (what a one-shot hits at). Peak: sample / 4x true peak, dBFS.',
             'Sub: share of the energy under 150 Hz. Tail: s from the peak until the 10 ms envelope stays 40 dB under it.',
             f'Keng: a 2-6 kHz peak at least {KENG_PROMINENCE:.0f} dB over its 1/3-octave median, under {KENG_WIDTH:.0f} Hz wide, '
             f'that takes at least {KENG_DECAY * 1000:.0f} ms to fall 20 dB (measured 30-400 ms after the onset; bins more than {KENG_FLOOR:.0f} dB under the loudest are not heard and skipped).', '']
    lines += ['## Per size (must rise: louder, deeper, longer)', '',
              '| size | shot M-max | shot sub % | shot tail s | blast M-max | blast sub % | blast tail s |', '|---|---|---|---|---|---|---|']
    for r in rows:
        s, b = r.get('shot'), r.get('blast')
        f = lambda m, k: f'{m[k]:.1f}' if m else '-'
        lines.append(f'| {r["name"]} | {f(s, "lufs_mmax")} | {f(s, "sub150")} | {f(s, "tail")} | {f(b, "lufs_mmax")} | {f(b, "sub150")} | {f(b, "tail")} |')
    lines += ['', 'Rising check: ' + ('every step rises.' if not problems else 'FAILS: ' + '; '.join(problems)), '',
              'Keng outside the armour-metal group: ' + (', '.join(kengs) if kengs else 'none.'), '']
    if before:
        bb = {}
        for rel, m in before.items():
            bb.setdefault(bank_of(rel), []).append(m)
        mean = lambda bank, k: float(np.mean([m[k] for m in bb[bank]])) if bank in bb else None
        lines += ['## Per size before this pass (prompt 34 L6 banks, as the game played them) and after', '',
                  '| size | before shot (bank) | M-max | sub % | tail s | after shot M-max | sub % | tail s | before blast / hit (bank) | M-max | sub % | tail s | keng | after blast M-max | sub % | tail s |',
                  '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for r in rows:
            shot_b, blast_b = BEFORE_MAP[r['size']]
            s_now, b_now = r.get('shot'), r.get('blast')
            f = lambda v: '-' if v is None else f'{v:.1f}'
            kb = sum(m['keng'] for m in bb.get(blast_b, []))
            lines.append(f"| {r['name']} | {shot_b or '-'} | {f(mean(shot_b, 'lufs_mmax'))} | {f(mean(shot_b, 'sub150'))} | {f(mean(shot_b, 'tail'))} | "
                         f"{f(s_now and s_now['lufs_mmax'])} | {f(s_now and s_now['sub150'])} | {f(s_now and s_now['tail'])} | "
                         f"{blast_b} | {f(mean(blast_b, 'lufs_mmax'))} | {f(mean(blast_b, 'sub150'))} | {f(mean(blast_b, 'tail'))} | {kb}/{len(bb.get(blast_b, []))} | "
                         f"{f(b_now and b_now['lufs_mmax'])} | {f(b_now and b_now['sub150'])} | {f(b_now and b_now['tail'])} |")
        lines += ['', 'Before, the 20-40 mm to 203-240 mm kinetic rounds without a blast (autocannons, tank guns, railguns) landed on '
                  '`p34/blast_ap_t1..t4`, the T0 machine guns on `impact_metal`, whatever they struck.', '']
        lines += ['## Before / after (bank means)', '', '| bank (before) | M-max | sub % | tail s | keng clips |', '|---|---|---|---|---|']
        for bank in sorted(bb):
            ms = bb[bank]
            lines.append(f'| {bank} | {np.mean([m["lufs_mmax"] for m in ms]):.1f} | {np.mean([m["sub150"] for m in ms]):.1f} | '
                         f'{np.mean([m["tail"] for m in ms]):.2f} | {sum(m["keng"] for m in ms)}/{len(ms)} |')
        lines.append('')
    lines += ['## Every clip', '', '| clip | s | LUFS | M-max | peak | true peak | sub % | tail s | keng dB / ms / Hz | keng |',
              '|---|---|---|---|---|---|---|---|---|---|']
    for rel in sorted(clips):
        m = clips[rel]
        lines.append(f'| {rel} | {m["seconds"]:.2f} | {m["lufs"]:.1f} | {m["lufs_mmax"]:.1f} | {m["peak"]:.1f} | {m["true_peak"]:.1f} | '
                     f'{m["sub150"]:.1f} | {m["tail"]:.2f} | {m["keng_prominence"]:.0f} / {m["keng_decay"] * 1000:.0f} / {m["keng_hz"]:.0f} | '
                     f'{"KENG" if m["keng"] else ""} |')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def run(rev=None):
    return {rel: analyse(x, sr) for rel, x, sr in clips_at(rev)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rev', help='analyse the clips at this git revision')
    ap.add_argument('--json-only', help='write only this JSON file')
    ap.add_argument('--before', help='a JSON file from an earlier run (e.g. --rev 01f19757~1) for the before / after table')
    ap.add_argument('--check', action='store_true', help='exit 1 on a keng outside the armour group or a size table that does not rise')
    args = ap.parse_args(argv)
    clips = run(args.rev)
    if args.json_only:
        Path(args.json_only).write_text(json.dumps(clips, indent=1), encoding='utf-8')
        print(f'ANALYSED {len(clips)} clips -> {args.json_only}')
        return 0
    lib = library()
    per_bank = {}
    for rel, m in clips.items():
        per_bank.setdefault(bank_of(rel), []).append(m)
    per_bank = {b: {k: float(np.mean([m[k] for m in ms])) for k in ('lufs_mmax', 'lufs', 'sub150', 'tail')} for b, ms in per_bank.items()}
    rows = size_table(per_bank, lib)
    problems = rises(rows, 'shot') + rises(rows, 'blast')
    kengs = keng_outside_armour(clips, lib)
    before = json.loads(Path(args.before).read_text(encoding='utf-8')) if args.before else None
    write_md(clips, rows, problems, kengs, OUT_DIR / 'metrics.md', 'Audio metrics (fix pass L7; play-test 12 lane C)', before)
    (OUT_DIR / 'metrics.json').write_text(json.dumps({'clips': clips, 'sizes': rows, 'not_rising': problems, 'keng_outside_armour': kengs},
                                                     indent=1), encoding='utf-8')
    print(f'ANALYSED {len(clips)} clips; not rising: {len(problems)}; keng outside armour: {len(kengs)}')
    for p in problems + kengs:
        print('  ' + p)
    return 1 if args.check and (problems or kengs) else 0


if __name__ == '__main__':
    sys.exit(main())
