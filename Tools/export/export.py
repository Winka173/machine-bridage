"""Machine Brigade: export every game data value into per-domain files (Docs/prompts/export_full_vi.txt).

    python Tools/export/export.py [--out DIR] [--base REF] [--strict] [--date YYYY-MM-DD]
    python Tools/export/export.py coverage [--strict]     # the leaf-path coverage test only (writes nothing)
    python Tools/export/export.py fk                      # the foreign-key test only (writes nothing)
    python Tools/export/export.py diff <dirA|refA> <dirB|refB> [--out DIR]   # pass 7: Docs/export/diff_<A>_<B>/
    python Tools/export/export.py check [--out DIR]       # pass 8: export, the 9 self-checks of spec 9, SELF_CHECK.md
    python Tools/export/export.py import <export dir | xlsx> --dry-run [--out DIR]   # pass 9: edits -> change manifest

Read only: no game value is changed. Output: Docs/export/<date>_<commit>/ (date = the HEAD commit's date, so a rerun on
the same commit and data rewrites the same files byte for byte; README.md and MANIFEST.json carry the run's time).
Exit code: 0 pass; 1 an unmapped leaf, a leaf mapped twice, a failed foreign key, a layer B formula off its game value, an
input_<name> copy off its source file, or a secret in an output; 2 (--strict) leaves still pending on files not built yet.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import importlib
import json
import platform
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

import openpyxl  # noqa: E402

from core import fk as FK  # noqa: E402
from core import formula as FX  # noqa: E402
from core import index as IX  # noqa: E402
from core import repo, secrets  # noqa: E402
from core.context import Context  # noqa: E402
from core.write import write_csv, write_xlsx  # noqa: E402
from domains import DOMAINS, PLANNED  # noqa: E402
from domains import _pending  # noqa: E402

TOOL_VERSION = "1"
BALANCE = "Assets/MachineBrigade/Resources/Data/balance.json"
CAMPAIGN = "Assets/MachineBrigade/Resources/Data/campaign.json"


def build(base_ref: str | None, lenient: bool = False):
    """lenient (the diff of an old tree): a domain that fails to build (a source or helper the old tree lacks) is left
    out and listed in 00/Van_de instead of stopping the run."""
    ctx = Context(base_ref=base_ref)
    for glob, pattern, target, note in _pending.CLAIMS:
        ctx.claim(glob, pattern, target, note)
    for name in DOMAINS:
        mod = importlib.import_module(f"domains.{name}")
        if not lenient:
            mod.build(ctx)
            continue
        try:
            mod.build(ctx)
        except Exception as e:  # noqa: BLE001 - reported, the file is left out
            ctx.books.pop(getattr(mod, "FILE_ID", name), None)
            why = str(e)
            for root in (str(repo.ROOT).replace("\\", "\\\\"), str(repo.ROOT), repo.ROOT.as_posix()):
                why = why.replace(root, "<repo>")
            ctx.issue(f"lenient: {name} not built ({type(e).__name__}: {why[:160]})")
            print(f"lenient: {name} not built ({type(e).__name__})")
    built = set(ctx.books) | {IX.INDEX_ID}
    # balance.json's version lands in 00/Phien_ban (marked here: coverage is evaluated before the index is built)
    if BALANCE in ctx.sources and ctx.sources[BALANCE].readable and "version" in ctx.sources[BALANCE].data:
        ctx.cov.mark(BALANCE, ("version",), IX.INDEX_ID, "Phien_ban", "gia_tri")
    per_source, unmapped, per_file = ctx.cov.evaluate(ctx.sources, ctx.excluded, ctx.pending, built)
    fk_results = FK.check(ctx.books)
    FX.run(ctx)  # layer B: resolve and evaluate the formulas, formula == _game and input copy == source (ctx.formula_checks)
    return ctx, per_source, unmapped, per_file, fk_results


def summary(ctx, per_source, unmapped, fk_results, strict: bool) -> int:
    tot = collections.Counter()
    for st in per_source.values():
        tot.update(st)
    print(f"sources {len(per_source)}  leaves {tot['leaves']}  mapped {tot['mapped']}  khong_xuat {tot['khong_xuat']}  "
          f"pending {tot['pending']}  unmapped {tot['unmapped']}  mapped twice {len(ctx.cov.duplicates)}")
    code = 0
    if unmapped:
        code = 1
        print("UNMAPPED leaves (source | pattern | count | claimed by):")
        for (sid, pat, target), n in sorted(unmapped.items()):
            print(f"  {sid} | {pat} | {n} | {target}")
    if ctx.cov.duplicates:
        code = 1
        print("Leaves mapped to two columns:")
        for d in ctx.cov.duplicates[:50]:
            print("  ", *d)
    fk_counts = collections.Counter(r["status"] for r in fk_results)
    print(f"foreign keys: {dict(sorted(fk_counts.items()))}")
    for r in fk_results:
        if r["status"] == "FAIL":
            code = 1
            print(f"  FK FAIL {r['file']}/{r['sheet']}.{r['column']} -> {r['targets']}: {r['errors']} ({r['examples']})")
    fx = getattr(ctx, "formula_checks", [])
    fx_counts = collections.Counter(r["status"] for r in fx)
    print(f"layer B checks (formula == game / python, input == source): {dict(sorted(fx_counts.items()))}  "
          f"cells {sum(r['rows'] for r in fx)}")
    for r in fx:
        if r["status"] == "FAIL":
            code = 1
            print(f"  {r['kind']} FAIL {r['file']}/{r['sheet']}.{r['column']}: {r['rows'] - r['match'] - r['unchecked']} off "
                  f"(max diff {r['max_diff']:.3g}): {r['examples']}")
    if strict and tot["pending"] and code == 0:
        code = 2
        print("strict: pending leaves remain")
    return code


def write_all(ctx, per_source, unmapped, per_file, fk_results, out: Path, meta: dict, strict: bool) -> list:
    index_book = IX.build(ctx, meta, per_source, unmapped, per_file, fk_results, PLANNED, sorted(ctx.books))
    # start clean: only folders this tool writes
    for sub in ("00_chi_muc", "xlsx", "csv"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    books = dict(ctx.books)
    for fid, book in sorted(books.items()):
        sheets = []
        for sname, s in book.sheets.items():
            header, rows = s.table()
            formula_cols = {c.name for c in s.cols.values() if c.formula}
            sheets.append((sname, header, rows, formula_cols))
            write_csv(out / "csv" / fid / f"{sname}.csv", *s.table(values=True))
        write_xlsx(out / "xlsx" / f"{fid}.xlsx", sheets)
    sheets = []
    for sname, s in index_book.sheets.items():
        header, rows = s.table()
        sheets.append((sname, header, rows, set()))
        write_csv(out / "csv" / IX.INDEX_ID / f"{sname}.csv", header, rows)
    write_xlsx(out / "00_chi_muc" / f"Machine_Brigade_00_Index_{meta['ngay']}.xlsx", sheets)
    (out / "00_chi_muc" / "COVERAGE.md").write_bytes(
        IX.coverage_md(meta, per_source, unmapped, per_file, books, ctx, strict).encode("utf-8"))
    hits = secrets.scan_dir(out)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    readme = [
        "# Machine Brigade: bộ xuất dữ liệu", "",
        f"Xuất lúc {now} (UTC) từ commit {meta['commit']} (nhánh {repo.branch()}).", "",
        "Chạy lại: `python Tools/export/export.py` (một lệnh; cùng dữ liệu cho cùng file, trừ README.md và MANIFEST.json).",
        "Đọc trước: 00_chi_muc/Machine_Brigade_00_Index_<ngày>.xlsx, sheet README và Muc_luc_sheet; độ phủ: COVERAGE.md.",
        "", f"Kiểm bí mật: {'KHÔNG có chuỗi khớp mẫu bí mật' if not hits else str(len(hits)) + ' chuỗi khớp mẫu bí mật (FAIL)'}.", "",
    ]
    (out / "00_chi_muc" / "README.md").write_bytes("\n".join(readme).encode("utf-8"))
    files = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "MANIFEST.json" and p.parent.name != "__pycache__":
            files.append({"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size,
                          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest = {"generated_utc": now, "branch": repo.branch(), "tool": f"Tools/export v{TOOL_VERSION}", **meta,
                "secret_hits": len(hits), "files": files}
    (out / "00_chi_muc" / "MANIFEST.json").write_bytes(
        json.dumps(manifest, ensure_ascii=False, indent=1).encode("utf-8"))
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="export", choices=["export", "coverage", "fk", "diff", "check", "import"])
    ap.add_argument("targets", nargs="*", help="diff: two export folders or git refs (A then B); import: one export folder or xlsx")
    ap.add_argument("--out", help="output folder (default Docs/export/<date>_<commit>)")
    ap.add_argument("--base", default="origin/main",
                    help="git ref of the earlier version for the _truoc / _sau columns (default origin/main: the last release)")
    ap.add_argument("--date", help="the folder's date (default: the HEAD commit's date)")
    ap.add_argument("--strict", action="store_true", help="fail on leaves still pending on files not built yet")
    ap.add_argument("--lenient", action="store_true",
                    help="leave out a domain that fails to build (an old tree for diff) instead of stopping")
    ap.add_argument("--dry-run", action="store_true", help="import: write the change manifest only (the only import mode)")
    args = ap.parse_args(argv)
    if args.command == "diff":
        if len(args.targets) != 2:
            ap.error("diff takes two export folders or git refs")
        from core import diff
        return diff.main(args.targets[0], args.targets[1], args.out)
    if args.command == "import":
        from core import reimport
        return reimport.main(args, sys.modules[__name__])
    if args.command == "check":
        from core import selfcheck
        return selfcheck.main(args, sys.modules[__name__])

    base = repo.resolve_ref(args.base) if args.base else None
    ctx, per_source, unmapped, per_file, fk_results = build(args.base if base else None, args.lenient)
    code = summary(ctx, per_source, unmapped, fk_results, args.strict)
    if args.command != "export":
        return code

    commit = repo.head_commit()
    date = args.date or repo.head_date()
    scanned = sorted({s.id.split("#")[0] for s in ctx.sources.values()})
    dirty = repo.dirty_paths(["Assets", "Tools"])
    dirty_sources = [p for p in dirty if p in scanned]
    out = Path(args.out) if args.out else repo.ROOT / "Docs" / "export" / f"{date}_{commit}"
    if not out.is_absolute():
        out = repo.ROOT / out
    meta = {
        "ngay": date, "commit": commit, "ban_goc": f"{args.base} ({base})" if base else "",
        "nguon_chua_commit": ";".join(dirty_sources),
        "balance_sha256": ctx.sources[BALANCE].sha256() if BALANCE in ctx.sources else "",
        "campaign_sha256": ctx.sources[CAMPAIGN].sha256() if CAMPAIGN in ctx.sources else "",
        "cong_cu": f"Tools/export v{TOOL_VERSION}", "python": platform.python_version(), "openpyxl": openpyxl.__version__,
    }
    hits = write_all(ctx, per_source, unmapped, per_file, fk_results, out, meta, args.strict)
    try:
        shown = out.relative_to(repo.ROOT).as_posix()
    except ValueError:
        shown = out.name
    print(f"wrote {shown}")
    if hits:
        print(f"SECRET SCAN: {len(hits)} hits")
        for h in hits[:20]:
            print("  ", *h)
        code = code or 1
    return code


if __name__ == "__main__":
    sys.exit(main())
