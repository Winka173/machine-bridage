"""Pass 9 check (spec 10): the reverse import.

    python Tools/export/tests/test_import_demo.py [export folder]

Without a folder it first exports into a temp folder (about a minute). Then:
  1. importing the unedited export gives 0 entries and 0 rejections;
  2. the demo: 01_vu_khi_dan.xlsx and 02_phuong_tien.xlsx copied to a temp folder, three cells edited with openpyxl
     (a weapon's damage, a vehicle's cost, a derived column), imported: exactly 2 DECIDE entries and 1 rejection;
  3. import without --dry-run refuses; no data file changed.
Writes only in temp folders. Exit code 0 = pass.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import openpyxl  # noqa: E402

import export as ex  # noqa: E402
from core import reimport  # noqa: E402
from core.repo import ROOT  # noqa: E402

DATA = ROOT / "Assets" / "MachineBrigade" / "Resources" / "Data"
# (file, sheet, row id, column, kind): raw, raw, derived. The raw columns are the data keys (damage, cp); the named
# columns beside them (sat_thuong_moi_phat, base_cp) are resolved values (inheritance, defaults) and are rejected too.
EDITS = [
    ("01_vu_khi_dan", "Vu_khi", "gun_120mm", "damage", "weapon damage"),
    ("02_phuong_tien", "Xe", "light_tank", "cp", "vehicle cost"),
    ("02_phuong_tien", "Xe_suy_ra", "light_tank", "dps_tren_cp", "derived"),
]


def data_hash() -> str:
    h = hashlib.sha256()
    for p in sorted(DATA.rglob("*.json")):
        h.update(p.read_bytes())
    return h.hexdigest()


def edit_cell(path: Path, sheet: str, rid: str, col: str):
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    header = [c.value for c in ws[1]]
    ci = header.index(col) + 1
    for row in ws.iter_rows(min_row=2):
        if str(row[0].value) == rid:
            cell = row[ci - 1]
            old = cell.value
            cell.value = (old if isinstance(old, (int, float)) and not isinstance(old, bool) else 0) + 1
            wb.save(path)
            return old, cell.value
    raise SystemExit(f"{sheet}: no row {rid}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("export", nargs="?", help="an export folder (default: export into a temp folder first)")
    args = ap.parse_args()
    fails = []
    work = Path(tempfile.mkdtemp(prefix="mb_import_check_"))
    before = data_hash()
    try:
        if args.export:
            exp = Path(args.export).resolve()
        else:
            exp = work / "export"
            print("export into a temp folder ...")
            subprocess.run([sys.executable, str(HERE / "export.py"), "--out", str(exp)], check=True, capture_output=True)
        base = reimport.base_from_meta(reimport.export_meta(exp))
        ref = reimport.Reference(ex, base)

        # 1. the unedited export
        man = reimport.scan(ref, exp)
        print(f"1. unedited export: {len(man['rows'])} entries, {len(man['rejected'])} rejected, "
              f"{man['notes']['cells_compared']} cells compared")
        if man["rows"] or man["rejected"]:
            fails.append(f"unedited export gave {len(man['rows'])} entries / {len(man['rejected'])} rejections")

        # 2. the demo
        demo = work / "demo"
        demo.mkdir()
        for fid in sorted({e[0] for e in EDITS}):
            shutil.copy(exp / "xlsx" / f"{fid}.xlsx", demo / f"{fid}.xlsx")
        for fid, sheet, rid, col, kind in EDITS:
            old, new = edit_cell(demo / f"{fid}.xlsx", sheet, rid, col)
            print(f"   edit {fid}/{sheet} {rid}.{col} ({kind}): {old} -> {new}")
        man = reimport.scan(ref, demo)
        reimport.write(man, work / "demo_out")
        rows, rej = man["rows"], man["rejected"]
        print(f"2. demo: {len(rows)} entries, {len(rej)} rejected")
        for r in rows:
            print(f"   {r['bundle_id']}: {r['field_path']} ({r['id_path']}) {r['expected_before']} -> {r['new_value']} "
                  f"status {r['status']}, precondition {r['precondition_now']}, c01 {r['c01_path'] or '-'}")
        for r in rej:
            print(f"   rejected {r['sheet']}!{r['cell']} {r['column']}: {r['reason']}")
        if len(rows) != 2 or any(r["status"] != "DECIDE" or r["precondition_now"] != "OK" for r in rows):
            fails.append("demo: expected 2 DECIDE entries with precondition OK")
        paths = {r["id_path"] for r in rows}
        if paths != {"weapons[id=gun_120mm].damage", "vehicles[id=light_tank].cp"}:
            fails.append(f"demo: entries at {sorted(paths)}")
        if any(set(r) != set(reimport.COLUMNS) for r in rows):
            fails.append("demo: an entry without the manifest columns")
        if len(man["bundles"]) != 2 or any(b["Trạng thái"] != "DECIDE" for b in man["bundles"]):
            fails.append("demo: expected 2 bundles in DECIDE")
        if len(rej) != 1 or rej[0]["column"] != "dps_tren_cp" or not rej[0]["reason"].startswith("derived"):
            fails.append("demo: expected 1 rejection of the derived column dps_tren_cp")

        # 3. no direct write
        code = reimport.main(argparse.Namespace(dry_run=False, targets=[str(demo)], out=None, base=None), ex)
        if code == 0:
            fails.append("import without --dry-run did not refuse")
        if data_hash() != before:
            fails.append("a data file changed")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("PASS" if not fails else "FAIL: " + "; ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
