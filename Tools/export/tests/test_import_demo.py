"""Pass 5 check: the reverse import of the pack.

    python Tools/export/tests/test_import_demo.py [pack folder]

Without a folder it first exports into a temp folder (about two minutes). Then:
  1. importing the unedited pack gives 0 entries and 0 rejections;
  2. 01_chien_dau.xlsx copied to a temp folder with ONE raw cell edited (a weapon's damage): exactly 1 DECIDE entry, 0 rejected;
  3. the same with a second edit in a derived column: still 1 entry, and 1 rejection naming the derived column;
  4. import without --dry-run refuses; no data file changed.
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
    ("01_chien_dau", "Vu_khi", "gun_120mm", "damage", "weapon damage (raw)"),
    ("01_chien_dau", "Xe_suy_ra", "light_tank", "dps_tren_cp", "derived"),
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

        # 2. one raw edit -> exactly one manifest row
        one = work / "one"
        one.mkdir()
        shutil.copy(exp / "01_chien_dau.xlsx", one / "01_chien_dau.xlsx")
        fid, sheet, rid, col, kind = EDITS[0]
        old, new = edit_cell(one / f"{fid}.xlsx", sheet, rid, col)
        print(f"   edit {fid}/{sheet} {rid}.{col} ({kind}): {old} -> {new}")
        man = reimport.scan(ref, one)
        rows, rej = man["rows"], man["rejected"]
        print(f"2. one raw cell edited: {len(rows)} entries, {len(rej)} rejected")
        for r in rows:
            print(f"   {r['bundle_id']}: {r['field_path']} ({r['id_path']}) {r['expected_before']} -> {r['new_value']} "
                  f"status {r['status']}, precondition {r['precondition_now']}")
        if len(rows) != 1 or rej or rows[0]["status"] != "DECIDE" or rows[0]["precondition_now"] != "OK"                 or rows[0]["id_path"] != "weapons[id=gun_120mm].damage" or set(rows[0]) != set(reimport.COLUMNS):
            fails.append(f"one edit: expected exactly 1 DECIDE entry at weapons[id=gun_120mm].damage, got {len(rows)} / {len(rej)} rejected")

        # 3. a derived cell too: still one entry, one rejection
        demo = work / "demo"
        demo.mkdir()
        shutil.copy(exp / "01_chien_dau.xlsx", demo / "01_chien_dau.xlsx")
        for fid, sheet, rid, col, kind in EDITS:
            edit_cell(demo / f"{fid}.xlsx", sheet, rid, col)
        man = reimport.scan(ref, demo)
        reimport.write(man, work / "demo_out")
        rows, rej = man["rows"], man["rejected"]
        print(f"3. raw + derived edited: {len(rows)} entries, {len(rej)} rejected")
        for r in rej:
            print(f"   rejected {r['sheet']}!{r['cell']} {r['column']}: {r['reason']}")
        if len(rows) != 1 or len(man["bundles"]) != 1 or man["bundles"][0]["Trạng thái"] != "DECIDE":
            fails.append("raw + derived: expected 1 entry in 1 bundle in DECIDE")
        if len(rej) != 1 or rej[0]["column"] != "dps_tren_cp" or not rej[0]["reason"].startswith("derived"):
            fails.append("raw + derived: expected 1 rejection of the derived column dps_tren_cp")

        # 4. no direct write
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
