"""The export run: sources, books, coverage marks, Khong_xuat and pending rules, issues."""
from __future__ import annotations

from pathlib import Path

from . import cs, rules
from .coverage import Coverage, Rule
from .model import Book
from .repo import ROOT
from .sources import Source, discover


class Context:
    def __init__(self, base_ref: str | None = None):
        self.sources: dict[str, Source] = discover()
        self.books: dict[str, Book] = {}
        self.cov = Coverage()
        self.excluded: list[Rule] = [Rule(g, p, r, origin="core/rules.py") for g, p, r in rules.SHARED]
        self.pending: list[Rule] = []
        self.issues: list[str] = []
        self.unreadable: list[tuple[str, str]] = []
        self.unclassified: list[tuple[str, str, str]] = []  # (source, path, why) for 12/Khac_chua_phan_loai
        self.notes: list[tuple[str, str]] = []              # (topic, text) for the README
        self.base_ref = base_ref
        self.cache: dict = {}

    # ------------------------------------------------------------------ books
    def book(self, file_id: str, title_vi: str, desc: str = "") -> Book:
        if file_id in self.books:
            return self.books[file_id]
        b = Book(self, file_id, title_vi, desc)
        self.books[file_id] = b
        return b

    # ------------------------------------------------------------------ sources
    def src(self, sid: str) -> Source:
        s = self.sources.get(sid)
        if s is None:
            raise KeyError(f"source {sid} not found (discovery walks {', '.join(['Assets', 'Tools'])})")
        return s

    def data(self, sid: str):
        s = self.src(sid)
        if s.data is None:
            raise RuntimeError(f"{sid} unreadable: {s.error}")
        return s.data

    def cs_table(self, path: str, array: str, extra: list[str] | None = None):
        """A C# literal table as a source (id '<path>#<array>'): (source id, rows, line numbers)."""
        sid = f"{path}#{array}"
        if sid in self.sources:
            s = self.sources[sid]
            return sid, s.data["rows"], s.data["lines"]
        text = (ROOT / path).read_text("utf-8-sig")
        extra_text = "\n".join((ROOT / e).read_text("utf-8-sig") for e in (extra or []))

        def load(_src):
            rows, lines = cs.read_array(text, array, extra_text)
            return {"rows": rows, "lines": lines}

        s = Source(sid, "cs_table", ROOT / path, loader=load)
        self.sources[sid] = s
        if s.data is None:
            self.unreadable.append((sid, s.error or "unreadable"))
            return sid, [], []
        return sid, s.data["rows"], s.data["lines"]

    def cs_custom(self, sid: str, path: str, extractor):
        """A C# table built by a domain's own regex over a method body (values set imperatively, not a literal array):
        (source id, rows, line numbers). `extractor(text) -> (rows, lines)`."""
        if sid in self.sources:
            s = self.sources[sid]
            return sid, s.data["rows"], s.data["lines"]
        text = (ROOT / path).read_text("utf-8-sig")

        def load(_src):
            rows, lines = extractor(text)
            return {"rows": rows, "lines": lines}

        s = Source(sid, "cs_table", ROOT / path, loader=load)
        self.sources[sid] = s
        if s.data is None:
            self.unreadable.append((sid, s.error or "unreadable"))
            return sid, [], []
        return sid, s.data["rows"], s.data["lines"]

    # ------------------------------------------------------------------ rules
    def exclude(self, source_glob: str, pattern: str, reason: str, origin: str = ""):
        self.excluded.append(Rule(source_glob, pattern, reason, origin=origin))

    def claim(self, source_glob: str, pattern: str, target: str, note: str = ""):
        self.pending.append(Rule(source_glob, pattern, note, target=target, origin="domains/_pending.py"))

    def issue(self, text: str, once: bool = False):
        if once and text in self.issues:
            return
        self.issues.append(text)

    def note(self, topic: str, text: str):
        self.notes.append((topic, text))
