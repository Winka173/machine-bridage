"""Small music-theory helpers: note names, chord symbols and voicings."""

from __future__ import annotations

import re

_LETTER = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_NOTE_RE = re.compile(r"^([A-Ga-g])([#b]*)(-?\d+)$")


def n(name: str | int) -> int:
    """Note name to MIDI number. ``'C4'`` is 60, ``'F#2'``, ``'Bb3'`` work."""
    if isinstance(name, int):
        return name
    m = _NOTE_RE.match(name.strip())
    if not m:
        raise ValueError(f"bad note name {name!r}")
    letter, acc, octv = m.groups()
    pc = _LETTER[letter.upper()] + acc.count("#") - acc.count("b")
    return 12 * (int(octv) + 1) + pc


CHORD_TYPES = {
    "": (0, 4, 7),
    "M": (0, 4, 7),
    "m": (0, 3, 7),
    "5": (0, 7),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "msus2": (0, 2, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "7": (0, 4, 7, 10),
    "m7": (0, 3, 7, 10),
    "maj7": (0, 4, 7, 11),
    "add9": (0, 4, 7, 14),
    "madd9": (0, 3, 7, 14),
    "m9": (0, 3, 7, 10, 14),
    "mb6": (0, 3, 7, 8),
    "b5": (0, 4, 6),
    "cl": (0, 1, 7),  # cluster: root, minor second, fifth (dissonant)
    "phr": (0, 1, 5, 7),  # phrygian cluster
}

_CHORD_RE = re.compile(r"^([A-G])([#b]?)(.*)$")


def chord(sym: str) -> tuple[int, tuple[int, ...]]:
    """Parse a chord symbol like ``'Dm'``, ``'Bb'``, ``'F#sus4'`` or ``'C/E'``.

    Returns ``(root_pitch_class, intervals)``. A slash bass is ignored here;
    use :func:`bass_pc` to read it.
    """
    main = sym.split("/")[0]
    m = _CHORD_RE.match(main)
    if not m:
        raise ValueError(f"bad chord {sym!r}")
    letter, acc, qual = m.groups()
    root = (_LETTER[letter] + (1 if acc == "#" else -1 if acc == "b" else 0)) % 12
    if qual not in CHORD_TYPES:
        raise ValueError(f"unknown chord quality {qual!r} in {sym!r}")
    return root, CHORD_TYPES[qual]


def bass_pc(sym: str) -> int:
    if "/" in sym:
        b = sym.split("/")[1]
        m = _CHORD_RE.match(b)
        letter, acc, _ = m.groups()
        return (_LETTER[letter] + (1 if acc == "#" else -1 if acc == "b" else 0)) % 12
    return chord(sym)[0]


def bass(sym: str, low: int = 28) -> int:
    """Lowest MIDI pitch >= ``low`` whose pitch class is the chord's bass."""
    pc = bass_pc(sym)
    p = low + ((pc - low) % 12)
    return p


def root(sym: str, near: int) -> int:
    """Chord root in the octave closest to ``near``."""
    pc = chord(sym)[0]
    base = near - ((near - pc) % 12)
    return base if near - base <= 6 else base + 12


def tones(sym: str, lo: int, hi: int) -> list[int]:
    """All chord tones between ``lo`` and ``hi`` inclusive, ascending."""
    r, iv = chord(sym)
    pcs = {(r + i) % 12 for i in iv}
    return [p for p in range(lo, hi + 1) if p % 12 in pcs]


def voicing(sym: str, center: int, count: int = 4, prev: list[int] | None = None) -> list[int]:
    """A close voicing of ``count`` notes around ``center``.

    With ``prev`` the voicing is chosen to move as little as possible from the
    previous chord (simple voice leading).
    """
    cand = tones(sym, center - 12, center + 12)
    best, best_cost = None, 1e9
    for i in range(len(cand) - count + 1):
        v = cand[i:i + count]
        if len({p % 12 for p in v}) < min(count, len(chord(sym)[1])):
            continue
        mid = sum(v) / count
        cost = abs(mid - center)
        if prev:
            cost = 0.35 * cost + sum(min(abs(p - q) for q in prev) for p in v) / count
        if cost < best_cost:
            best, best_cost = v, cost
    return best or cand[:count]


def spread(sym: str, bass_note: int, top: int, count: int = 5) -> list[int]:
    """An open orchestral voicing: bass root, fifth above, then close tones up to ``top``."""
    r, iv = chord(sym)
    b = bass_note - ((bass_note - r) % 12)
    out = [b]
    if 7 in iv:
        out.append(b + 7)
    upper = [p for p in tones(sym, b + 12, top)]
    out += upper[-(count - len(out)):] if count > len(out) else []
    return sorted(set(out))


SCALES = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "harm": (0, 2, 3, 5, 7, 8, 11),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
}


def degree(key_root: int, mode: str, deg: int) -> int:
    """Scale degree (0-based, may be negative or > 6) as a MIDI pitch from ``key_root``."""
    sc = SCALES[mode]
    octv, d = divmod(deg, len(sc))
    return key_root + 12 * octv + sc[d]
