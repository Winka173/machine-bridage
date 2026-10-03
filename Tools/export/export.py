"""Machine Brigade: the balance pack (Docs/prompts/export_pack_vi.txt) in Docs/export/current/.

    python Tools/export/export.py [--out DIR] [--base REF] [--game-json PATH] [--strict]   # write the pack (overwrites)
    python Tools/export/export.py check [--out DIR] [--game-json PATH] [--strict]    # export twice, run every test, _qa/SELF_CHECK.md
    python Tools/export/export.py coverage | fk                                      # one test, writes nothing
    python Tools/export/export.py import <pack dir | xlsx> --dry-run [--out DIR]     # edited cells -> change manifest
    python Tools/export/export.py diff <dirA|refA> <dirB|refB> [--out DIR]           # writes <pack>/_qa/diff/
    python Tools/export/export.py pdf [--out DIR]                                    # writes <pack>/_qa/<name>.pdf

The pack is README.md, 00_index.xlsx, eight xlsx + md pairs, bulk.zip and images/ (and nothing else); the run's own tests
write to <pack>/_qa/ (not committed). A rerun on the same commit and data rewrites every file byte for byte.
Read only: no game value is changed. Exit code: 0 pass; 1 an unmapped leaf, a leaf mapped twice, a failed foreign key, a
formula off its game value, a secret in an output; 2 (--strict) a NEED_CODE_CHECK cell left.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import importlib
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

from core import fk as FK  # noqa: E402
from core import formula as FX  # noqa: E402
from core import index as IX  # noqa: E402
from core import pack, repo, secrets  # noqa: E402
from core.context import Context  # noqa: E402
from core.write import ZIP_DATE, csv_value, write_csv, write_xlsx  # noqa: E402
from domains import DOMAINS  # noqa: E402
from domains import _pending  # noqa: E402

TOOL_VERSION = "2"
BALANCE = "Assets/MachineBrigade/Resources/Data/balance.json"
CAMPAIGN = "Assets/MachineBrigade/Resources/Data/campaign.json"
DEFAULT_BASE = "5f5b3247"  # the commit before balance wave 2 (prompt 29): the _truoc / _sau columns compare against it
DEFAULT_OUT = Path("Docs") / "export" / "current"


def build(base_ref: str | None, lenient: bool = False, game: dict | None = None):
    """The nine domain books, regrouped into the pack's eight (core/pack.py), with coverage, foreign keys and formulas
    checked on the result. lenient (the diff of an old tree): a domain that fails to build is left out and listed."""
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
    pack.restructure(ctx, game)
    built = set(ctx.books) | {IX.INDEX_ID}
    per_source, unmapped, per_file = ctx.cov.evaluate(ctx.sources, ctx.excluded, ctx.pending, built)
    fk_results = FK.check(ctx.books)
    FX.run(ctx)  # formulas: resolve and evaluate; formula == game value, input copy == source (ctx.formula_checks)
    pack.freeze_bulk_references(ctx)
    pack.add_bom_sheets(ctx)
    pack.add_map_summary(ctx)
    for b in ctx.books.values():
        for s in b.sheets.values():
            s.infer_kinds()
    ctx.ncc = pack.need_code_check(ctx)
    return ctx, per_source, unmapped, per_file, fk_results


def summary(ctx, per_source, unmapped, fk_results, strict: bool) -> int:
    tot = collections.Counter()
    for st in per_source.values():
        tot.update(st)
    print(f"sources {len(per_source)}  leaves {tot['leaves']}  mapped {tot['mapped']}  khong_xuat {tot['khong_xuat']}  "
          f"unmapped {tot['unmapped']}  mapped twice {len(ctx.cov.duplicates)}")
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
        if r["status"] != "OK":
            code = 1
            print(f"  FK {r['status']} {r['file']}/{r['sheet']}.{r['column']} -> {r['targets']}: {r['errors']} ({r['examples']})")
    fx = getattr(ctx, "formula_checks", [])
    fx_counts = collections.Counter(r["status"] for r in fx)
    print(f"formulas (formula == game / python, input == source): {dict(sorted(fx_counts.items()))}  cells {sum(r['rows'] for r in fx)}")
    for r in fx:
        if r["status"] != "OK":
            code = 1
            print(f"  {r['kind']} {r['status']} {r['file']}/{r['sheet']}.{r['column']}: "
                  f"{r['rows'] - r['match'] - r['unchecked']} off (max diff {r['max_diff']:.3g}): {r['examples']}")
    by = collections.Counter(f"{f}/{s}" for f, s, *_ in ctx.ncc)
    print(f"NEED_CODE_CHECK cells left: {len(ctx.ncc)} in {len(by)} sheets"
          + (f" (filled from game.json: {getattr(ctx, 'game_filled', 0)})" if getattr(ctx, "game_filled", 0) else ""))
    if strict and ctx.ncc and code == 0:
        code = 2
        print("strict: NEED_CODE_CHECK cells remain")
    return code


# ------------------------------------------------------------------------------------------------------ the writers
def bulk_zip(ctx) -> bytes:
    """Every bulk sheet as <file>__<sheet>.csv in one zip: sorted names, fixed dates, so equal data gives equal bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        items = sorted((IX.bulk_name(fid, s.name), s) for fid, b in ctx.books.items() for s in b.sheets.values() if s.bulk)
        for name, s in items:
            header, rows = s.table(values=True)
            tmp = io.StringIO()
            w = csv.writer(tmp, lineterminator="\n")
            w.writerow(header)
            for line in rows:
                w.writerow([csv_value(v) for v in line])
            zi = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            zi.create_system = 0
            z.writestr(zi, tmp.getvalue().encode("utf-8"))
    return buf.getvalue()


def readme(meta: dict, ctx, images: list[str]) -> str:
    n_x = sum(1 for b in ctx.books.values() for s in b.sheets.values() if not s.bulk)
    n_b = sum(1 for b in ctx.books.values() for s in b.sheets.values() if s.bulk)
    files = "\n".join(f"├── {fid}.xlsx  +  {fid}.md      {title}" for fid, (title, _o, _d) in pack.PACK.items())
    return f"""# Machine Brigade: gói cân bằng

Xuất từ commit {meta['commit']} (ngày {meta['ngay']}); so sánh `_truoc` / `_sau` với bản {meta['ban_goc']}. Gói chỉ phục vụ cân
bằng: giá trị cấu hình sửa được, cột suy ra để cân bằng (DPS, máu trên CP, số phát để hạ, so với ngoài đời), tham chiếu ngoài đời
và game. Ghi đè mỗi lần chạy; lịch sử nằm trong git.

## Cây thư mục (19 file và images/)

```
current/
├── README.md
├── 00_index.xlsx   Muc_luc_file, Muc_luc_sheet, Schema (có đơn vị), Phien_ban (băm sha256 từng file)
{files}
├── bulk.zip        {n_b} CSV lớn (bố cục bản đồ, thoại, chuỗi địa phương hóa, nút model): <file>__<sheet>.csv
└── images/         {len(images)} ảnh phẳng, tiền tố file; chỉ ảnh mà một md dẫn tới
```

## Cách đọc

- Bắt đầu ở 00_index.xlsx: `Muc_luc_file` (mỗi file có gì), `Muc_luc_sheet` ({n_x} sheet trong xlsx, {n_b} trong bulk.zip),
  `Schema` (mỗi cột: kiểu, đơn vị `don_vi`, nguồn khóa, công thức, `sua_duoc`), `Phien_ban` (ngày, commit, băm balance.json và
  campaign.json, băm từng file).
- 01_chien_dau: vũ khí, đạn, phương tiện, thẻ hỗ trợ, trang bị, commander, đội mở màn, ném bom. 02_boss, 03_can_cu: boss, tháp.
  04_che_do_kinh_te_ai: chế độ, độ khó, kinh tế, AI, meta, giao diện. 05_chien_dich: chương, nhiệm vụ, biến cố.
  06_ban_do: bản đồ (mỗi bản đồ một dòng tóm tắt trong `Ban_do_tom_tat`; bố cục đầy đủ trong bulk.zip).
  07_hinh_anh_am_thanh_model: hiệu ứng, âm thanh, model. 08_tham_chieu: nguồn ngoài đời, cơ chế game, học thuyết.
- Mỗi md chỉ có luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng; bảng lớn ghi "xem sheet").
- Cột `_game` là giá trị mà mã game tính ra; cột công thức Excel sống tính lại từ cột dữ liệu gốc cùng file. Sheet `input_<tên>`
  là bản chép của sheet nguồn để công thức đọc cùng file: sửa ở sheet nguồn.
- Dấu hiệu thiếu dữ liệu: `NEED_SOURCE` (thông số ngoài đời chưa có nguồn), `KHONG_AP_DUNG` (ô vô nghĩa cho dòng đó; lý do ở
  `Schema.ly_do_khong_ap_dung`), `NEED_CODE_CHECK` (chỉ mã C# tính; ExportGameDoc điền khi chạy với game.json). Đơn vị
  `khong_ro` trong Schema: mã và chú thích không nói rõ.

## Cân bằng lại: nhập ngược (5 dòng)

1. Sửa số trong cột dữ liệu gốc của file xlsx (cột `Schema.sua_duoc` = co); không sửa id, nguon, raw_json, cột công thức, cột `_game`.
2. `python Tools/export/export.py import Docs/export/current --dry-run` (hoặc một file xlsx đã sửa): so với dữ liệu hiện tại.
3. Ra `_qa/import/manifest_import.json` và `.md` (bundle_id, entity_id, field_path, expected_before, new_value, status = DECIDE).
4. Đặt status APPLY cho dòng muốn áp, rồi `python Tools/balance/p29_apply.py --manifest <json> --dry-run`; OK / ALREADY_APPLIED / CONFLICT.
5. Chạy lại không `--dry-run` để áp theo gói; không bao giờ sửa balance.json trực tiếp.

## Lệnh

`python Tools/export/export.py` (ghi gói), `check` (xuất hai lần và chạy mọi test, ghi `_qa/SELF_CHECK.md`), `pdf` (ghi
`_qa/*.pdf`), `diff <A> <B>` (ghi `_qa/diff/`), `import <gói|xlsx> --dry-run`, `--game-json <game.json>` (điền ô
NEED_CODE_CHECK từ ExportGameDoc). Thư mục `_qa/` chỉ sinh khi chạy, không commit.
"""


def write_all(ctx, per_source, unmapped, per_file, fk_results, out: Path, meta: dict, strict: bool) -> list:
    from core import packdoc
    # start clean: only what this tool writes
    for name in ("images", "_qa"):
        if (out / name).exists():
            shutil.rmtree(out / name)
    for p in list(out.glob("*.xlsx")) + list(out.glob("*.md")) + [out / "bulk.zip"]:
        if p.exists():
            p.unlink()
    out.mkdir(parents=True, exist_ok=True)
    for fid, book in sorted(ctx.books.items()):
        sheets = []
        for sname, s in book.sheets.items():
            if s.bulk:
                continue
            header, rows = s.table()
            sheets.append((sname, header, rows, {c.name for c in s.cols.values() if c.formula}))
        write_xlsx(out / f"{fid}.xlsx", sheets)
    (out / "bulk.zip").write_bytes(bulk_zip(ctx))
    res = packdoc.build(ctx, meta, out)
    print(f"docs: {len(res['md'])} md, {len(res['images'])} pictures")
    (out / "README.md").write_bytes(readme(meta, ctx, res["images"]).encode("utf-8"))
    hashes = {}
    for p in sorted(out.rglob("*")):
        if p.is_file() and not p.relative_to(out).as_posix().startswith("_qa/"):
            hashes[p.relative_to(out).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    index = IX.build_index(ctx, meta, hashes, res["images"])
    write_xlsx(out / "00_index.xlsx", [(n, *s.table(), set()) for n, s in index.sheets.items()])
    # QA: only for the run, never committed
    qa = out / "_qa"
    qa.mkdir(exist_ok=True)
    qbook = IX.build_qa(ctx, meta, per_source, unmapped, per_file, fk_results, ctx.ncc)
    write_xlsx(qa / "qa.xlsx", [(n, *s.table(), set()) for n, s in qbook.sheets.items()])
    (qa / "COVERAGE.md").write_bytes(IX.coverage_md(meta, per_source, unmapped, per_file, ctx.books, ctx, strict,
                                                    ctx.ncc).encode("utf-8"))
    for name, s in ctx.qa_sheets.items():
        write_csv(qa / f"{name}.csv", *s.table(values=True))
    return secrets.scan_dir(out)


def meta_of(args, ctx, base) -> dict:
    dirty = repo.dirty_paths(["Assets", "Tools"])
    scanned = sorted({s.id.split("#")[0] for s in ctx.sources.values()})
    return {
        "ngay": args.date or repo.head_date(), "commit": repo.head_commit(), "ban_goc": f"{args.base} ({base})" if base else "",
        "nguon_chua_commit": ";".join(p for p in dirty if p in scanned),
        "balance_sha256": ctx.sources[BALANCE].sha256() if BALANCE in ctx.sources else "",
        "campaign_sha256": ctx.sources[CAMPAIGN].sha256() if CAMPAIGN in ctx.sources else "",
        "game_json_sha256": hashlib.sha256(Path(args.game_json).read_bytes()).hexdigest() if args.game_json else "",
        "o_dien_tu_game_json": getattr(ctx, "game_filled", 0),
        "cong_cu": f"Tools/export v{TOOL_VERSION}",
    }


def load_game(path: str | None) -> dict | None:
    return json.loads(Path(path).read_text("utf-8-sig")) if path else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="export",
                    choices=["export", "coverage", "fk", "diff", "check", "import", "pdf"])
    ap.add_argument("targets", nargs="*", help="diff: two pack folders or git refs (A then B); import: one pack folder or xlsx")
    ap.add_argument("--out", help=f"the pack folder (default {DEFAULT_OUT.as_posix()})")
    ap.add_argument("--base", default=DEFAULT_BASE,
                    help=f"git ref of the earlier version for the _truoc / _sau columns (default {DEFAULT_BASE}: the commit "
                    "before balance wave 2)")
    ap.add_argument("--date", help="the pack's date (default: the HEAD commit's date)")
    ap.add_argument("--strict", action="store_true", help="fail (exit 2) while a NEED_CODE_CHECK cell is left")
    ap.add_argument("--game-json", help="the game.json ExportGameDoc wrote: fills the NEED_CODE_CHECK cells it has a value for")
    ap.add_argument("--lenient", action="store_true", help="leave out a domain that fails to build (an old tree for diff)")
    ap.add_argument("--dry-run", action="store_true", help="import: write the change manifest only (the only import mode)")
    ap.add_argument("--structure-only", action="store_true", help="check: only the structure tests on an existing pack")
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else DEFAULT_OUT
    if not out.is_absolute():
        out = repo.ROOT / out
    args.out_dir = out
    if args.command == "diff":
        if len(args.targets) != 2:
            ap.error("diff takes two pack folders or git refs")
        from core import diff
        return diff.main(args.targets[0], args.targets[1], str(out / "_qa" / "diff"))
    if args.command == "import":
        from core import reimport
        return reimport.main(args, sys.modules[__name__])
    if args.command == "check":
        from core import packcheck
        return packcheck.main(args, sys.modules[__name__])
    if args.command == "pdf":
        from core import pdfpack
        return pdfpack.main(args)

    base = repo.resolve_ref(args.base) if args.base else None
    game = load_game(args.game_json)
    ctx, per_source, unmapped, per_file, fk_results = build(args.base if base else None, args.lenient, game)
    code = summary(ctx, per_source, unmapped, fk_results, args.strict)
    if args.command != "export":
        return code
    meta = meta_of(args, ctx, base)
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
