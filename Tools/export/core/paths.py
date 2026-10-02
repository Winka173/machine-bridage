"""Leaf paths: a tuple of keys (str) and list indices (int), their text form and wildcard patterns.

Text form: vehicles[12].deathExplosion.damage; a key that is not an identifier is quoted: base.ai.styles.aurel["heavy_turret.bastion"].
Patterns (coverage rules, Khong_xuat, pending claims) are written the same way with wildcards:
  [*]  any list index           *   any one key            **  any number of segments (zero or more)
e.g. vehicles[*].parts[*].**   bossParts.*.weapon   **
"""
from __future__ import annotations

import fnmatch
import re
from functools import lru_cache

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ANY_INDEX = "[*]"
ANY_KEY = "*"
ANY_DEPTH = "**"


def to_str(path: tuple) -> str:
    out = []
    for seg in path:
        if isinstance(seg, int):
            out.append(f"[{seg}]")
        elif seg == ANY_INDEX:
            out.append("[*]")
        elif IDENT.match(seg):
            out.append(("." if out else "") + seg)
        else:
            out.append('["' + seg.replace('"', '\\"') + '"]')
    return "".join(out)


def general(path: tuple) -> tuple:
    """The path with every index replaced by [*] (the pattern a leaf belongs to)."""
    return tuple(ANY_INDEX if isinstance(s, int) else s for s in path)


def general_str(path: tuple) -> str:
    return to_str(general(path))


_TOKEN = re.compile(r'\["((?:[^"\\]|\\.)*)"\]|\[\*\]|\[(\d+)\]|\.?([^.\[\]]+)')


@lru_cache(maxsize=None)
def parse(pattern: str) -> tuple:
    if pattern in ("", ANY_DEPTH):
        return (ANY_DEPTH,) if pattern else ()
    segs = []
    pos = 0
    while pos < len(pattern):
        m = _TOKEN.match(pattern, pos)
        if not m or m.end() == pos:
            raise ValueError(f"bad path pattern {pattern!r} at {pos}")
        if m.group(1) is not None:
            segs.append(m.group(1).replace('\\"', '"'))
        elif m.group(0) == "[*]":
            segs.append(ANY_INDEX)
        elif m.group(2) is not None:
            segs.append(int(m.group(2)))
        else:
            segs.append(m.group(3))
        pos = m.end()
    return tuple(segs)


def _seg_ok(p, s) -> bool:
    if p == ANY_INDEX:
        return s == ANY_INDEX or isinstance(s, int)
    if p == ANY_KEY:
        return isinstance(s, str) and s != ANY_INDEX
    if isinstance(p, int):
        return s == p
    if isinstance(p, str) and "*" in p:
        return isinstance(s, str) and s != ANY_INDEX and fnmatch.fnmatchcase(s.lower(), p.lower())
    return p == s


@lru_cache(maxsize=None)
def _match(pat: tuple, gen: tuple) -> bool:
    if not pat:
        return not gen
    head = pat[0]
    if head == ANY_DEPTH:
        rest = pat[1:]
        return any(_match(rest, gen[k:]) for k in range(len(gen) + 1))
    if not gen:
        return False
    return _seg_ok(head, gen[0]) and _match(pat[1:], gen[1:])


def matches(pattern: str, gen_path: tuple) -> bool:
    """Whether a generalised path (indices as [*]) fits a pattern."""
    return _match(parse(pattern), gen_path)
