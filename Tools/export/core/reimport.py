"""Pass 9 (spec 10): the reverse import. The owner's edits in an exported xlsx become a change manifest; nothing else.

    python Tools/export/export.py import <export folder | edited xlsx> --dry-run [--out DIR] [--base REF]

How an edit is found: the export is rebuilt from the current tree (the same base ref as the export, read from its
00_chi_muc/MANIFEST.json) and every cell of the xlsx is compared with the cell the exporter writes now. A cell that differs
and also differs from the export's own csv copy (csv/<file>/<sheet>.csv, when the folder has it) is an edit. A cell that
matches the export's csv but not the current tree is drift (the data moved since the export), not an edit.

Which edits become entries: only a cell that maps to exactly one leaf of a JSON data file under Assets/ (the coverage
mapping, inverted per cell: Row.mark is recorded while the export builds), and whose shown value is that leaf's value as is.
Everything else is rejected with its reason: id / nguon / raw_json / link / order columns, layer B formulas, derived or
copied columns (no source leaf), list cells (several leaves), converted values, code constants and other source kinds,
new rows, unknown columns or sheets.

The manifest (import/manifest_import.json + .md) uses prompt 29's columns (Docs/balance/manifest_v2.json, read by
Tools/balance/p29_apply.py): bundle_id, entity_id, field_path, ..., expected_before, new_value, ..., status = DECIDE;
bundles {bundle_id, Đối tượng, Số dòng, Trạng thái = DECIDE, Cần viết code, depends_on}. field_path is the data file's real
key path (vehicles[12].cp) with data_file, id_path (vehicles[id=light_tank].cp) and c01_path (the prompt 29 path, when one
maps 1:1) beside it. precondition_now is prompt 29's R2 outcome against the current data: OK / ALREADY_APPLIED / CONFLICT.
This module never writes a data file: changes reach the data only through the manifest apply path (DECISIONS, pass 9).
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.utils import get_column_letter

from . import model
from . import paths as P
from . import repo
from .sources import get as leaf_get
from .write import csv_value

COLUMNS = ["bundle_id", "entity_id", "field_path", "unit", "value_type", "known_good", "expected_before", "new_value",
           "tolerance", "derivation", "status", "scope", "requires_code", "depends_on", "owner_decision_id", "validation",
           "reason", "source", "data_file", "id_path", "c01_path", "precondition_now"]
FIXED = {"nguon": "nguon (where the row comes from) is written by the exporter",
         "raw_json": "raw_json (the source record) is written by the exporter"}
EDITABLE_ROOT = "Assets/"  # game data files; Tools/ JSON is tooling, not a game value
# The prompt 29 C01 paths (Tools/balance/p29_apply.py UNIT_FIELDS / WEAPON_FIELDS) that equal one balance.json key as is.
# Health is left out: C01 'hp' is in-battle health (hp x toughness), not the data key.
C01_VEHICLE = {"cp": "cost", "speed": "speed", "outgoingDamageMult": "outgoingDamageMult", "dropDelay": "dropDelaySec",
               "flareCharges": "flare.maxCharges", "flareRecharge": "flare.rechargeSec"}
C01_APS = {"recharge": "interception.rechargeSec", "charges": "interception.maxCharges",
           "shells": "interception.shellChance", "rockets": "interception.blocks.artilleryRocket"}
C01_WEAPON = {"targets": "targets"}
BALANCE = "Assets/MachineBrigade/Resources/Data/balance.json"


class Reference:
    """The export rebuilt from the current tree, with the per-cell source leaves recorded."""

    def __init__(self, ex, base_ref: str | None):
        self.cells: dict[tuple, list] = {}
        orig = model.Row.mark
        cells = self.cells

        def mark(row, src, path, col):
            orig(row, src, path, col)
            cells.setdefault((row.sheet.book.file_id, row.sheet.name, str(row.id), col), []).append((src, path))

        model.Row.mark = mark
        try:
            self.ctx, *_ = ex.build(base_ref)
        finally:
            model.Row.mark = orig
        self.base_ref = base_ref
        self.tables: dict[tuple, tuple] = {}

    def table(self, fid: str, sname: str):
        key = (fid, sname)
        if key not in self.tables:
            s = self.ctx.books[fid].sheets[sname]
            header, rows = s.table()
            self.tables[key] = (s, header, {str(line[0]): line for line in rows})
        return self.tables[key]


# ---------------------------------------------------------------------- inputs
def resolve_inputs(target: Path):
    """(export root or None, [xlsx files]). A folder: its xlsx/ (or the folder itself); a file: that xlsx."""
    if target.is_dir():
        sub = target / "xlsx"
        files = sorted((sub if sub.is_dir() else target).glob("*.xlsx"))
        root = target if (target / "00_chi_muc").is_dir() or sub.is_dir() else None
    else:
        files = [target]
        root = target.parent.parent if target.parent.name == "xlsx" else None
    files = [f for f in files if not f.name.startswith(("~$", "Machine_Brigade_00_Index"))]
    return root, files


def export_meta(root: Path | None) -> dict:
    p = root / "00_chi_muc" / "MANIFEST.json" if root else None
    if p is None or not p.is_file():
        return {}
    m = json.loads(p.read_text("utf-8"))
    return {k: m.get(k, "") for k in ("ngay", "commit", "ban_goc", "balance_sha256", "campaign_sha256")}


def base_from_meta(meta: dict) -> str | None:
    """The export's base ref: 'origin/main (9198a675)' -> 9198a675 (the commit it resolved to then)."""
    m = re.search(r"\(([0-9a-f]{6,40})\)", meta.get("ban_goc") or "")
    if m and repo.resolve_ref(m.group(1)):
        return m.group(1)
    return None


def load_csv(root: Path | None, fid: str, sname: str):
    p = root / "csv" / fid / f"{sname}.csv" if root else None
    if p is None or not p.is_file():
        return None
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return None
    header = rows[0]
    return {line[0]: dict(zip(header, line)) for line in rows[1:] if line}


# ---------------------------------------------------------------------- values
def norm(v):
    """A comparable form: ('n', float) numbers, ('b', bool), ('s', text); empty = ('s', '')."""
    if hasattr(v, "template"):  # a layer B formula cell: its text, as written
        v = v.text or v.template
    if v is None:
        return ("s", "")
    if isinstance(v, bool):
        return ("b", v)
    if isinstance(v, (int, float)):
        return ("n", float(v))
    v = ILLEGAL_CHARACTERS_RE.sub("", str(v))
    if v.startswith("="):  # a formula: Excel may respace or recase it on save
        v = re.sub(r"\s+", "", v).upper()
    return ("s", v)


def same(a, b) -> bool:
    na, nb = norm(a), norm(b)
    if na[0] == nb[0] == "n":
        return math.isclose(na[1], nb[1], rel_tol=1e-12, abs_tol=1e-12)
    return na == nb


def kind_of(v) -> str:
    return "bool" if isinstance(v, bool) else "int" if isinstance(v, int) else "float" if isinstance(v, float) else \
        "text" if isinstance(v, str) else "null" if v is None else type(v).__name__


def coerce(x, cur):
    """The cell's value in the leaf's type, or raises ValueError."""
    if isinstance(cur, bool):
        if isinstance(x, bool):
            return x
        if isinstance(x, str) and x.strip().lower() in ("true", "false"):
            return x.strip().lower() == "true"
        raise ValueError(f"'{x}' is not true / false")
    if isinstance(cur, (int, float)):
        if x is None or isinstance(x, bool):
            raise ValueError("an empty or true/false cell in a number column")
        n = float(x.strip()) if isinstance(x, str) else float(x)
        if not math.isfinite(n):
            raise ValueError("not a finite number")
        return int(n) if n.is_integer() and (isinstance(cur, int) or isinstance(x, int)) else n
    if isinstance(cur, str):
        if x is None:
            raise ValueError("an empty cell (clearing a text value is not supported)")
        return x if isinstance(x, str) else csv_value(x)
    if cur is None:
        if x is None:
            raise ValueError("an empty cell")
        return x
    raise ValueError(f"the leaf is a {kind_of(cur)}")


def parse_csv_text(text: str, cur):
    """The export-time value from its csv text, read in the current leaf's type (falls back to the current value)."""
    try:
        if isinstance(cur, bool):
            return text == "TRUE"
        if isinstance(cur, int):
            n = float(text)
            return int(n) if n.is_integer() else n
        if isinstance(cur, float):
            return float(text)
        if cur is None:
            return None if text == "" else text
        return text
    except ValueError:
        return cur


def id_path(data, path: tuple) -> str:
    """vehicles[12].cp -> vehicles[id=light_tank].cp (list items that carry a text id)."""
    out, node = [], data
    for seg in path:
        if isinstance(seg, int):
            item = node[seg] if isinstance(node, list) and seg < len(node) else None
            out.append(f"[id={item['id']}]" if isinstance(item, dict) and isinstance(item.get("id"), str) else f"[{seg}]")
        else:
            s = P.to_str((seg,))
            out.append("." + s if out and not s.startswith("[") else s)
        node = node[seg]
    return "".join(out)


def c01_path(sid: str, data, path: tuple) -> str:
    if sid != BALANCE or len(path) < 3 or not isinstance(path[1], int):
        return ""
    item = data[path[0]][path[1]]
    eid = item.get("id") if isinstance(item, dict) else None
    if not isinstance(eid, str):
        return ""
    rest = path[2:]
    if path[0] == "vehicles":
        if len(rest) == 1 and rest[0] in C01_VEHICLE:
            return f"units.{eid}.{C01_VEHICLE[rest[0]]}"
        if len(rest) == 2 and rest[0] == "aps" and rest[1] in C01_APS:
            return f"units.{eid}.{C01_APS[rest[1]]}"
    if path[0] == "weapons" and len(rest) == 1 and rest[0] in C01_WEAPON:
        return f"weapons.{eid}.{C01_WEAPON[rest[0]]}"
    return ""


def precondition(cur, expected, new) -> str:
    """Prompt 29 R2: ALREADY_APPLIED (current == new), OK (current == expected_before), else CONFLICT."""
    if same(cur, new):
        return "ALREADY_APPLIED"
    if same(cur, expected):
        return "OK"
    return "CONFLICT"


# ---------------------------------------------------------------------- the scan
def scan(ref: Reference, target: Path) -> dict:
    root, files = resolve_inputs(target)
    meta = export_meta(root)
    rows_out, rejected, notes = [], [], {"cells_compared": 0, "drift_cells": 0, "rows_missing": 0, "columns_missing": 0}
    warnings = []
    srcs = ref.ctx.sources
    now = {"commit": repo.head_commit(),
           "balance_sha256": srcs[BALANCE].sha256() if BALANCE in srcs else "",
           "campaign_sha256": srcs["Assets/MachineBrigade/Resources/Data/campaign.json"].sha256()
           if "Assets/MachineBrigade/Resources/Data/campaign.json" in srcs else ""}
    if not meta:
        warnings.append("no 00_chi_muc/MANIFEST.json beside the xlsx: the baseline is the current tree (base ref "
                        f"{ref.base_ref or 'none'}); expected_before is the current value")
    else:
        for k in ("balance_sha256", "campaign_sha256"):
            if meta.get(k) and meta[k] != now[k]:
                warnings.append(f"{k.split('_')[0]}.json changed since the export ({meta['commit']}): a cell that still "
                                f"shows the export's value is drift, not an edit; preconditions may be CONFLICT")
    digest = hashlib.sha256()

    def reject(fid, sname, cell, rid, col, before, after, why):
        rejected.append({"file": f"{fid}.xlsx", "sheet": sname, "cell": cell, "entity_id": rid, "column": col,
                         "before": before if not hasattr(before, "template") else (before.text or before.template),
                         "after": after, "reason": why})

    for xf in files:
        digest.update(xf.read_bytes())
        fid = xf.stem
        if fid not in ref.ctx.books:
            reject(fid, "", "", "", "", "", "", f"{xf.name}: not a domain file of this export")
            continue
        book = ref.ctx.books[fid]
        wb = load_workbook(xf, read_only=True)
        try:
            for ws in wb.worksheets:
                sname = ws.title
                it = ws.iter_rows(values_only=True)
                header = list(next(it, []) or [])
                if sname not in book.sheets:
                    if any(any(v not in (None, "") for v in line) for line in it):
                        reject(fid, sname, "", "", "", "", "", "sheet not in the export (new sheets are not imported)")
                    continue
                sheet, ref_header, ref_rows = ref.table(fid, sname)
                old_csv = load_csv(root, fid, sname)
                pos = {h: i for i, h in enumerate(ref_header)}
                notes["columns_missing"] += sum(1 for h in ref_header if h not in header)
                seen = set()
                for rnum, line in enumerate(it, start=2):
                    if not line or all(v in (None, "") for v in line):
                        continue
                    rid = str(line[0]) if line[0] is not None else ""
                    ref_line = ref_rows.get(rid)
                    if ref_line is None or rid in seen:
                        why = "duplicate id in the sheet" if rid in seen else \
                            "row id not in the export (adding rows or editing an id is not imported)"
                        reject(fid, sname, f"A{rnum}", rid, header[0] if header else "", "", line[0], why)
                        continue
                    seen.add(rid)
                    old_line = old_csv.get(rid) if old_csv else None
                    for ci, h in enumerate(header):
                        if h is None or ci >= len(line):
                            continue
                        x = line[ci]
                        cell = f"{get_column_letter(ci + 1)}{rnum}"
                        if h not in pos:
                            if x not in (None, ""):
                                reject(fid, sname, cell, rid, h, "", x, "column not in the export (new columns are not imported)")
                            continue
                        before = ref_line[pos[h]]
                        notes["cells_compared"] += 1
                        if same(x, before):
                            continue
                        if old_line is not None and h in old_line and csv_value(x) == old_line[h] \
                                and not (isinstance(x, str) and x.startswith("=")):
                            notes["drift_cells"] += 1
                            continue
                        c = sheet.cols.get(h)
                        if h == sheet.id_col:
                            reject(fid, sname, cell, rid, h, before, x, "id column: ids are not editable")
                            continue
                        if h in FIXED:
                            reject(fid, sname, cell, rid, h, before, x, FIXED[h] + "; not editable")
                            continue
                        if h in (sheet.parent_col, "thu_tu") and sheet.parent is not None:
                            reject(fid, sname, cell, rid, h, before, x, "link / order column of a child sheet: not editable")
                            continue
                        if (c is not None and c.formula) or hasattr(before, "template"):
                            reject(fid, sname, cell, rid, h, before, x,
                                   "derived column (layer B formula): edit the raw columns it reads")
                            continue
                        leaves = ref.cells.get((fid, sname, rid, h), [])
                        if not leaves:
                            raw = [k for k in ref_header if k != h and len(ref.cells.get((fid, sname, rid, k), [])) == 1
                                   and same(ref_line[pos[k]], before) and before not in (None, "")]
                            hint = f" (raw column with this value: {', '.join(raw[:3])})" if raw else ""
                            reject(fid, sname, cell, rid, h, before, x, "derived column: no source leaf (computed, "
                                   f"resolved or copied by the exporter); edit the raw column{hint}")
                            continue
                        if len(leaves) > 1:
                            reject(fid, sname, cell, rid, h, before, x,
                                   f"list cell: {len(leaves)} source leaves in one cell; edit the list in the data file")
                            continue
                        sid, path = leaves[0]
                        src = srcs.get(sid)
                        if src is None or src.kind != "json" or not sid.startswith(EDITABLE_ROOT) or not src.readable:
                            kind = src.kind if src is not None else "unknown"
                            reject(fid, sname, cell, rid, h, before, x,
                                   f"source {sid} ({kind}) is not a game data JSON file: change it in its own file / code")
                            continue
                        cur = leaf_get(src.data, path)
                        if not same(before, cur) or isinstance(cur, (dict, list)):
                            reject(fid, sname, cell, rid, h, before, x,
                                   f"the column shows a converted value ({before!r}, data {cur!r}): edit not mapped")
                            continue
                        try:
                            new = coerce(x, cur)
                        except ValueError as e:
                            reject(fid, sname, cell, rid, h, before, x, f"value: {e}")
                            continue
                        exp = parse_csv_text(old_line[h], cur) if old_line is not None and h in old_line else cur
                        fpath = P.to_str(path)
                        rows_out.append({
                            "bundle_id": f"XL{fid[:2]}-{sname}-{rid}", "entity_id": rid, "field_path": fpath,
                            "unit": (c.unit if c is not None else "") or "", "value_type": kind_of(new), "known_good": "",
                            "expected_before": exp, "new_value": new, "tolerance": 0,
                            "derivation": f"Excel edit {fid}.xlsx {sname}!{cell} (column {h})", "status": "DECIDE",
                            "scope": "data", "requires_code": False, "depends_on": "", "owner_decision_id": "",
                            "validation": f"{fpath} == new_value", "reason": "", "source": f"{fid}.xlsx > {sname}!{cell}",
                            "data_file": sid, "id_path": id_path(src.data, path), "c01_path": c01_path(sid, src.data, path),
                            "precondition_now": precondition(cur, exp, new),
                        })
                notes["rows_missing"] += sum(1 for k in ref_rows if k not in seen)
        finally:
            wb.close()

    bundles = {}
    for r in rows_out:
        b = bundles.setdefault(r["bundle_id"], {"bundle_id": r["bundle_id"], "Đối tượng": r["entity_id"], "Số dòng": 0,
                                                "Trạng thái": "DECIDE", "Cần viết code": "Không", "depends_on": ""})
        b["Số dòng"] += 1
    if notes["rows_missing"]:
        warnings.append(f"{notes['rows_missing']} export rows are missing from the xlsx: deleting rows is not imported (ignored)")
    return {"source": target.name, "sha256": digest.hexdigest(), "kind": "export_import (Tools/export import, pass 9)",
            "export": meta, "current": now, "base_ref": ref.base_ref or "", "warnings": warnings, "notes": notes,
            "columns": COLUMNS, "rows": rows_out, "bundles": list(bundles.values()), "rejected": rejected}


# ---------------------------------------------------------------------- output
def _md(v) -> str:
    return str(v).replace("|", "\\|").replace("\n", " ")[:200]


def write(man: dict, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest_import.json").write_bytes(json.dumps(man, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
    lines = [f"# Import manifest: {man['source']}", "",
             f"Made {dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()} (UTC) by "
             "`python Tools/export/export.py import <export> --dry-run`; commit " + man["current"]["commit"] + ".",
             "Nothing was written to the data. Set a bundle's Trạng thái (and its rows' status) to APPLY to accept it; "
             "the apply path is prompt 29's (Tools/balance/p29_apply.py, see DECISIONS 'pass 9').", ""]
    lines += [f"- warning: {w}" for w in man["warnings"]]
    lines += ["", f"Entries: {len(man['rows'])} (bundles {len(man['bundles'])}); rejected: {len(man['rejected'])}; "
              f"cells compared {man['notes']['cells_compared']}, drift {man['notes']['drift_cells']}.", "",
              "| bundle_id | entity_id | field_path | expected_before | new_value | status | precondition_now | c01_path |",
              "|---|---|---|---|---|---|---|---|"]
    for r in man["rows"]:
        lines.append("| " + " | ".join(_md(r[k]) for k in ("bundle_id", "entity_id", "field_path", "expected_before",
                                                             "new_value", "status", "precondition_now", "c01_path")) + " |")
    if man["rejected"]:
        lines += ["", "## Rejected edits", "", "| file | sheet | cell | entity | column | before | after | reason |",
                  "|---|---|---|---|---|---|---|---|"]
        for r in man["rejected"]:
            lines.append("| " + " | ".join(_md(r[k]) for k in ("file", "sheet", "cell", "entity_id", "column", "before",
                                                                 "after", "reason")) + " |")
    (out / "manifest_import.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def main(args, ex) -> int:
    if not args.dry_run:
        print("import: only --dry-run exists. It writes a manifest; the data changes only through the manifest apply path "
              "(rows set to APPLY, preconditions OK / ALREADY_APPLIED / CONFLICT, per bundle). Nothing was written.")
        return 2
    if len(args.targets) != 1:
        print("import takes one export folder or one edited xlsx")
        return 2
    target = Path(args.targets[0])
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    if not target.exists():
        print(f"import: {target.name} not found")
        return 2
    root, files = resolve_inputs(target)
    if not files:
        print(f"import: no xlsx in {target.name}")
        return 2
    meta = export_meta(root)
    base = base_from_meta(meta) if meta else (repo.resolve_ref(args.base) if args.base else None)
    ref = Reference(ex, base)
    man = scan(ref, target)
    out = Path(args.out) if args.out else (root or target.parent) / "import"
    if not out.is_absolute():
        out = repo.ROOT / out
    write(man, out)
    for w in man["warnings"]:
        print("warning:", w)
    print(f"import (dry run): {len(man['rows'])} entries in {len(man['bundles'])} bundles (status DECIDE), "
          f"{len(man['rejected'])} rejected; wrote {out.name}/manifest_import.json and .md")
    for r in man["rejected"][:20]:
        print(f"  rejected {r['file']} {r['sheet']}!{r['cell']} ({r['column']}): {r['reason']}")
    return 0
