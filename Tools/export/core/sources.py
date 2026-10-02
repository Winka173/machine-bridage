"""Source discovery (spec 3.1): every data file under the scanned roots, found by walking, never listed by hand.

A source has a repo-relative id, a kind, a parsed form and its leaves (the paths the coverage test walks).
Kinds and their leaves:
  json       every scalar and every empty list / object (JSON with comments read as JSONC)
  csv        rows[i].<column>
  txt        lines[i] (non-blank lines)
  glb        nodes[i].name, materials[i].name, meshes[i].name, triangles (the model's triangle count)
  yaml       Unity YAML (.asset / .prefab / .unity / .mixer / .controller): docs[i].<key path>
  audio      file (the clip itself; its row lives in 09)
  cs_strings a C# text table: ["key"].en / ["key"].vi
  cs_table   a C# literal table a domain parses (registered by the domain through Context.cs_table)
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

from . import jsonc
from .repo import ROOT, rel

SCAN_ROOTS = ["Assets", "Tools"]
SKIP_DIRS = {"__pycache__", ".git", "Library", "Temp", "Logs", "obj", "UserSettings", "node_modules"}
# Output of this tool is never an input.
SKIP_PREFIXES = ("Docs/export/",)

KIND_BY_EXT = {
    ".json": "json", ".jsonc": "json",
    ".csv": "csv", ".tsv": "csv",
    ".txt": "txt",
    ".glb": "glb",
    ".asset": "yaml", ".prefab": "yaml", ".unity": "yaml", ".mixer": "yaml", ".controller": "yaml",
    ".wav": "audio", ".ogg": "audio", ".mp3": "audio", ".aif": "audio", ".aiff": "audio", ".flac": "audio",
}
CS_STRING_ENTRY = re.compile(r'^\s*\["([^"\\]+)"\]\s*=\s*\(', re.M)


class Source:
    def __init__(self, sid: str, kind: str, path: Path | None = None, loader=None, note: str = ""):
        self.id = sid
        self.kind = kind
        self.path = path
        self._loader = loader
        self._data = None
        self._loaded = False
        self.error: str | None = None
        self.note = note
        self.size = path.stat().st_size if path is not None and path.exists() else 0

    # ------------------------------------------------------------------ content
    def raw(self) -> bytes:
        return self.path.read_bytes() if self.path is not None else b""

    def sha256(self) -> str:
        if self.path is None:
            return ""
        return hashlib.sha256(self.raw()).hexdigest()

    @property
    def data(self):
        if not self._loaded:
            self._loaded = True
            try:
                self._data = self._loader(self) if self._loader else _LOADERS[self.kind](self)
            except Exception as e:  # unreadable: listed in Nguon_khong_doc_duoc
                self.error = f"{type(e).__name__}: {e}"
                self._data = None
        return self._data

    @property
    def readable(self) -> bool:
        return self.data is not None and self.error is None

    # ------------------------------------------------------------------ leaves
    def leaves(self):
        """Yields every leaf path (tuple)."""
        d = self.data
        if d is None:
            return
        if self.kind in ("json", "yaml"):
            yield from json_leaves(d, ())
        elif self.kind == "cs_table":  # the rows; their line numbers are where they sit, not data
            yield from json_leaves(d["rows"], ())
        elif self.kind == "csv":
            for i, row in enumerate(d):
                for k in row:
                    yield ("rows", i, k)
        elif self.kind == "txt":
            for i, line in enumerate(d):
                if line.strip():
                    yield ("lines", i)
        elif self.kind == "glb":
            for key in ("nodes", "materials", "meshes"):
                for i, _ in enumerate(d.get(key, [])):
                    yield (key, i, "name")
            yield ("triangles",)
        elif self.kind == "audio":
            yield ("file",)
        elif self.kind == "cs_strings":
            for key in d:
                yield (key, "en")
                yield (key, "vi")


def json_leaves(node, path: tuple):
    if isinstance(node, dict):
        if not node:
            yield path
        for k, v in node.items():
            yield from json_leaves(v, path + (k,))
    elif isinstance(node, list):
        if not node:
            yield path
        for i, v in enumerate(node):
            yield from json_leaves(v, path + (i,))
    else:
        yield path


def get(node, path: tuple):
    for seg in path:
        node = node[seg]
    return node


# ---------------------------------------------------------------------- loaders
def _load_json(src: Source):
    return jsonc.loads(src.raw().decode("utf-8-sig"))


def _load_csv(src: Source):
    text = src.raw().decode("utf-8-sig")
    delim = "\t" if src.id.endswith(".tsv") else ","
    return list(csv.DictReader(io.StringIO(text), delimiter=delim))


def _load_txt(src: Source):
    return src.raw().decode("utf-8-sig", "replace").splitlines()


def _load_glb(src: Source):
    """The glTF JSON chunk and the triangle count, read with Tools/assets/glb_analyze.read_glb (the model checker's reader)."""
    sys.path.insert(0, str(ROOT / "Tools" / "assets"))
    try:
        import glb_analyze  # noqa: WPS433
    finally:
        sys.path.pop(0)
    doc, _ = glb_analyze.read_glb(src.path)
    tris = 0
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if prim.get("mode", 4) != 4:
                continue
            if "indices" in prim:
                tris += doc["accessors"][prim["indices"]]["count"] // 3
            elif "POSITION" in prim.get("attributes", {}):
                tris += doc["accessors"][prim["attributes"]["POSITION"]]["count"] // 3
    return {
        "nodes": [n.get("name", "") for n in doc.get("nodes", [])],
        "materials": [m.get("name", "") for m in doc.get("materials", [])],
        "meshes": [m.get("name", "") for m in doc.get("meshes", [])],
        "triangles": tris,
    }


_YAML_DOC = re.compile(r"^--- !u!(\d+) &(-?\d+)")
_YAML_LINE = re.compile(r"^(\s*)(- )?([^:#][^:]*?):(?:\s+(.*))?$")


def _load_yaml(src: Source):
    """Unity YAML, enough for leaves: each document a nested dict of its 'key: value' lines (lists by '- ')."""
    docs = []
    stack: list[tuple[int, object]] = []
    for line in src.raw().decode("utf-8", "replace").splitlines():
        if line.startswith("%"):
            continue
        m = _YAML_DOC.match(line)
        if m:
            root: dict = {"_class": int(m.group(1)), "_file_id": m.group(2)}
            docs.append(root)
            stack = [(-1, root)]
            continue
        if not stack or not line.strip():
            continue
        lm = _YAML_LINE.match(line)
        if not lm:
            continue
        indent = len(lm.group(1)) + (2 if lm.group(2) else 0)
        key, value = lm.group(3).strip(), (lm.group(4) or "").strip()
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if lm.group(2):  # a list item starting with "key: value"
            lst = parent.setdefault("_items", []) if isinstance(parent, dict) else parent
            item: dict = {}
            lst.append(item)
            parent = item
        if isinstance(parent, dict):
            if value:
                parent[key] = value
            else:
                child: dict = {}
                parent[key] = child
                stack.append((indent, child))
    return {"docs": docs}


def _load_audio(src: Source):
    return {"file": src.id}


def _load_cs_strings(src: Source):
    from . import cs
    return cs.read_string_table(src.raw().decode("utf-8-sig"))


_LOADERS = {
    "json": _load_json, "csv": _load_csv, "txt": _load_txt, "glb": _load_glb, "yaml": _load_yaml,
    "audio": _load_audio, "cs_strings": _load_cs_strings,
}


# ---------------------------------------------------------------------- discovery
def discover() -> dict[str, Source]:
    """Every source under SCAN_ROOTS, by repo-relative id (sorted)."""
    found: dict[str, Source] = {}
    for root_name in SCAN_ROOTS:
        base = ROOT / root_name
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                p = Path(dirpath) / name
                sid = rel(p)
                if sid.startswith(SKIP_PREFIXES) or name.endswith(".meta"):
                    continue
                ext = p.suffix.lower()
                kind = KIND_BY_EXT.get(ext)
                if kind is None and ext == ".cs":
                    try:
                        text = p.read_text("utf-8-sig", errors="replace")
                    except OSError:
                        continue
                    if "Scripts/Game/Hud/" in sid or "Scripts/" in sid:
                        if len(CS_STRING_ENTRY.findall(text)) >= 3 and "(string en, string vi)" in text:
                            kind = "cs_strings"
                if kind is None:
                    continue
                found[sid] = Source(sid, kind, p)
    return dict(sorted(found.items()))
