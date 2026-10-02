"""Prompt 29 pass 0: exports the Manifest sheet of the round-2 balance file (v2) for the code.

    python Tools/balance/p29_manifest.py

Writes Docs/balance/manifest_v2.json: the sheet's header names, every row as an object (values as the sheet holds them,
formulas already computed: openpyxl data_only), the bundles sheet (status, requires_code, depends_on) and the sha256 of
the source xlsx. From here on the apply tool (p29_apply.py) reads only this export; re-export when the xlsx changes.
"""
from __future__ import annotations

import hashlib
import json
import os

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX = os.path.join(ROOT, "Docs", "balance", "Machine_Brigade_Can_bang_dot2_v2.xlsx")
OUT = os.path.join(ROOT, "Docs", "balance", "manifest_v2.json")


def plain(v):
    """A cell as JSON: numbers stay numbers (ints when whole), text stays text, empty is null."""
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def table(ws, header_row):
    rows = [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
    head = [str(c) if c is not None else "" for c in rows[header_row]]
    out = []
    for r in rows[header_row + 1:]:
        out.append({head[i]: plain(c) for i, c in enumerate(r) if i < len(head) and head[i]})
    return head, out


def main():
    with open(XLSX, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    # The Manifest sheet has a note on its first row; the header is the second.
    head, rows = table(wb["Manifest"], 1)
    _, bundles = table(wb["Gói"], 0)
    data = {
        "source": os.path.relpath(XLSX, ROOT).replace("\\", "/"),
        "sha256": digest,
        "columns": head,
        "rows": rows,
        "bundles": bundles,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(rows)} manifest rows, {len(bundles)} bundles, sha256 {digest[:12]} -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
