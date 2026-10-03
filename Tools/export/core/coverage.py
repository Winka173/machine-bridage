"""The leaf-path coverage test (spec 3.3).

Every leaf of every source must be exported into exactly one column of one sheet, or sit in Khong_xuat with a reason.
A leaf claimed by a domain file not built yet (domains/_pending.py) counts as pending: allowed while the file is not
registered, a failure once it is (the lane must then map it). --strict fails on pending leaves too (the final self-check).
"""
from __future__ import annotations

import collections
import fnmatch

from . import paths as P


class Rule:
    def __init__(self, source_glob: str, pattern: str, reason: str, target: str = "", origin: str = ""):
        self.source_glob = source_glob
        self.pattern = pattern
        self.reason = reason
        self.target = target  # pending rules: the domain file that will export it
        self.origin = origin
        self.leaves = 0
        self.sources: set[str] = set()

    def fits_source(self, sid: str) -> bool:
        return fnmatch.fnmatchcase(sid, self.source_glob)


class Coverage:
    def __init__(self):
        self.mapped: dict[tuple[str, tuple], tuple[str, str, str]] = {}
        self.duplicates: list[tuple[str, str, str, str]] = []
        self.out_reasons: dict[str, str] = {}   # pack: sheets left out of the pack (their leaves count as Khong_xuat)
        self.out_leaves = collections.Counter()  # sheet -> leaves

    def mark(self, sid: str, path: tuple, file_id: str, sheet: str, col: str):
        key = (sid, path)
        where = (file_id, sheet, col)
        old = self.mapped.get(key)
        if old is not None and old != where:
            self.duplicates.append((sid, P.to_str(path), "/".join(old), "/".join(where)))
            return
        self.mapped[key] = where

    def evaluate(self, sources: dict, excluded: list[Rule], pending: list[Rule], built: set[str]):
        """Per source: leaves, mapped, Khong_xuat, pending, unmapped (with the unmapped patterns)."""
        per_source = {}
        unmapped = collections.Counter()
        per_file = collections.Counter()
        for sid, src in sources.items():
            ex = [r for r in excluded if r.fits_source(sid)]
            pe = [r for r in pending if r.fits_source(sid)]
            stats = collections.Counter()
            if not src.readable:
                per_source[sid] = stats
                continue
            cache: dict[tuple, object] = {}
            for path in src.leaves():
                stats["leaves"] += 1
                where = self.mapped.get((sid, path))
                if where is not None and where[0] == "_ngoai_goi":
                    stats["khong_xuat"] += 1
                    self.out_leaves[where[1]] += 1
                    continue
                if where is not None:
                    stats["mapped"] += 1
                    per_file[where[0]] += 1
                    continue
                g = P.general(path)
                hit = cache.get(g, 0)
                if hit == 0:
                    hit = next((r for r in ex if P.matches(r.pattern, g)), None)
                    if hit is None:
                        hit = next((r for r in pe if P.matches(r.pattern, g)), None)
                    cache[g] = hit
                if hit is not None and hit in ex:
                    stats["khong_xuat"] += 1
                    hit.leaves += 1
                    hit.sources.add(sid)
                elif hit is not None and hit.target not in built:
                    stats["pending"] += 1
                    hit.leaves += 1
                    hit.sources.add(sid)
                else:
                    stats["unmapped"] += 1
                    unmapped[(sid, P.to_str(g), hit.target if hit is not None else "")] += 1
            per_source[sid] = stats
        return per_source, unmapped, per_file
