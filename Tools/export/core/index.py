"""00_index.xlsx of the pack (Muc_luc_file, Muc_luc_sheet, Schema, Phien_ban) and the QA workbook (_qa/qa.xlsx, never in the
pack): coverage per source, Khong_xuat, foreign keys, formula checks, the cells still NEED_CODE_CHECK, the sheets left out.
"""
from __future__ import annotations

import collections

from . import pack
from .model import MARKER, Book, natural_key

INDEX_ID = "00_index"
BULK_ZIP = "bulk.zip"
SRC = "Tools/export (core/index.py)"


def bulk_name(fid: str, sheet: str) -> str:
    return f"{fid}__{sheet}.csv"


def _sources_text(sources: set) -> str:
    if not sources:
        return ""
    by_src = collections.defaultdict(set)
    for sid, pat in sources:
        by_src[sid].add(pat)
    parts = []
    for sid in sorted(by_src):
        pats = sorted(by_src[sid], key=natural_key)
        if len(pats) > 4:
            prefix = _common_prefix(pats)
            pats = [(prefix + "…") if prefix else f"{len(pats)} mẫu"]
        parts.append(f"{sid}: {', '.join(pats)}")
    return " | ".join(parts)


def _common_prefix(items: list[str]) -> str:
    a, b = min(items), max(items)
    k = 0
    while k < min(len(a), len(b)) and a[k] == b[k]:
        k += 1
    return a[:k]


def editable(c) -> bool:
    """A raw column: it holds data leaves of a JSON data file under Assets/, is no formula and no python analysis."""
    if c is None or c.formula or (c.source_note or "").startswith("python:") or not c.sources:
        return False
    return all(sid.startswith("Assets/") and ".json" in sid for sid, _p in c.sources)


def build_index(ctx, meta: dict, hashes: dict, images: list[str]) -> Book:
    """hashes: {pack path: sha256} of every file in the pack except 00_index.xlsx itself."""
    book = Book(ctx, INDEX_ID, "Chỉ mục", "Mục lục file, mục lục sheet, Schema có đơn vị, phiên bản và băm file")
    mlf = book.sheet("Muc_luc_file", "Mục lục file", "Mọi file của gói và nội dung của nó")
    for c in ("tieu_de", "xlsx", "md", "so_sheet_xlsx", "so_sheet_bulk", "so_dong", "mo_ta"):
        mlf.col(c)
    mls = book.sheet("Muc_luc_sheet", "Mục lục sheet", "Mọi sheet: tên ASCII, tên tiếng Việt, nằm ở xlsx hay bulk.zip")
    for c in ("file", "sheet", "ten_viet", "lop", "sheet_cha", "vi_tri", "so_dong", "so_cot", "mo_ta"):
        mls.col(c)
    schema = book.sheet("Schema", "Schema", "Mọi cột của mọi sheet: kiểu, đơn vị, nguồn khóa, công thức, sửa được hay không")
    for c in ("file", "sheet", "cot", "thu_tu_cot", "kieu", "don_vi", "enum", "y_nghia", "nguon_khoa", "cong_thuc",
              "khoa_ngoai", "bat_buoc", "tu_sinh", "sua_duoc", "ly_do_khong_ap_dung"):
        schema.col(c)
    pb = book.sheet("Phien_ban", "Phiên bản", "Ngày, commit, băm balance.json và campaign.json, băm sha256 từng file của gói")
    pb.col("gia_tri")

    # Phien_ban -------------------------------------------------------------------------------------------------
    for k, v in meta.items():
        r = pb.row(k, SRC)
        r.set("gia_tri", v)
    bal = "Assets/MachineBrigade/Resources/Data/balance.json"
    if bal in ctx.sources and isinstance(ctx.sources[bal].data, dict) and "version" in ctx.sources[bal].data:
        r = pb.row("balance_version", f"{bal}: version")
        r.set("gia_tri", ctx.sources[bal].data["version"], bal, ("version",))
    tun = "Assets/MachineBrigade/Resources/Data/tunables.json"
    if tun in ctx.sources and isinstance(ctx.sources[tun].data, dict) and "version" in ctx.sources[tun].data:
        r = pb.row("tunables_version", f"{tun}: version")
        r.set("gia_tri", ctx.sources[tun].data["version"], tun, ("version",))
    for path in sorted(hashes):
        r = pb.row(f"sha256:{path}", SRC)
        r.set("gia_tri", hashes[path])
    pb.row("sha256:00_index.xlsx", SRC).set("gia_tri", "(file này: không tự ghi băm của mình)")

    # Muc_luc_file ------------------------------------------------------------------------------------------------
    rows = [("README.md", "README", "", "", 0, 0, 0, "Cách đọc, cây thư mục, nhập ngược, lệnh"),
            (INDEX_ID, "Chỉ mục", "00_index.xlsx", "", 4, 0, 0, book.desc)]
    for fid, b in ctx.books.items():
        xs = [s for s in b.sheets.values() if not s.bulk]
        bs = [s for s in b.sheets.values() if s.bulk]
        rows.append((fid, b.title_vi, f"{fid}.xlsx", f"{fid}.md", len(xs), len(bs),
                     sum(len(s.rows) for s in b.sheets.values()), b.desc))
    rows.append((BULK_ZIP, "CSV lớn", "", "", 0, sum(1 for b in ctx.books.values() for s in b.sheets.values() if s.bulk),
                 sum(len(s.rows) for b in ctx.books.values() for s in b.sheets.values() if s.bulk),
                 "Bố cục bản đồ, văn bản thoại và chuỗi địa phương hóa, nút model: mỗi CSV một tên <file>__<sheet>.csv"))
    rows.append(("images/", "Ảnh", "", "", 0, 0, len(images), "Chỉ ảnh mà một file md dẫn tới; tên có tiền tố file"))
    for k, title, xl, md, nx, nb, nrow, desc in rows:
        r = mlf.row(k, SRC)
        r.set("tieu_de", title)
        r.set("xlsx", xl)
        r.set("md", md)
        r.set("so_sheet_xlsx", nx)
        r.set("so_sheet_bulk", nb)
        r.set("so_dong", nrow)
        r.set("mo_ta", desc)

    # Muc_luc_sheet and Schema -----------------------------------------------------------------------------------
    all_books = dict(ctx.books)
    all_books[INDEX_ID] = book
    for b in all_books.values():
        for s in b.sheets.values():
            s.infer_kinds()
    n_sheets = sum(len(b.sheets) for b in all_books.values())
    for fid in sorted(all_books):
        b = all_books[fid]
        for sname, s in b.sheets.items():
            where = f"bulk.zip:{bulk_name(fid, sname)}" if s.bulk else (f"{fid}.xlsx" if fid != INDEX_ID else "00_index.xlsx")
            n = n_sheets if (fid == INDEX_ID and sname == "Muc_luc_sheet") else len(s.rows)
            r = mls.row(f"{fid}/{sname}", SRC)
            r.set("file", fid)
            r.set("sheet", sname)
            r.set("ten_viet", s.title_vi)
            r.set("lop", s.layer if s.kind != "kv" else "A_kv")
            r.set("sheet_cha", s.parent.name if s.parent is not None else "")
            r.set("vi_tri", where)
            r.set("so_dong", n)
            r.set("so_cot", len(s.column_order()))
            r.set("mo_ta", s.desc)
            kad = {c: why for (f, sn, c), why in getattr(ctx, "kad", {}).items() if f == fid and sn == sname}
            for k, cname in enumerate(s.column_order()):
                c = s.cols.get(cname)
                sr = schema.row(f"{fid}/{sname}/{cname}", SRC)
                sr.set("file", fid)
                sr.set("sheet", sname)
                sr.set("cot", cname)
                sr.set("thu_tu_cot", k + 1)
                if c is None:  # nguon / raw_json
                    sr.set("kieu", "text")
                    sr.set("y_nghia", "file + khóa nguồn của dòng" if cname == "nguon" else "nguyên bản ghi gốc (JSON), chỉ để đối chiếu")
                    sr.set("sua_duoc", "khong")
                    continue
                sr.set("kieu", c.kind or "")
                sr.set("don_vi", pack.schema_unit(s, c))
                sr.set("enum", ";".join(c.enum) if isinstance(c.enum, (list, tuple)) else (c.enum or ""))
                sr.set("y_nghia", c.meaning)
                sr.set("nguon_khoa", c.source_note or _sources_text(c.sources))
                sr.set("cong_thuc", c.formula or "")
                sr.set("khoa_ngoai", ";".join(c.fk))
                sr.set("bat_buoc", bool(c.required))
                sr.set("tu_sinh", bool(c.auto))
                sr.set("sua_duoc", "co" if editable(c) and cname != s.id_col and cname != s.parent_col else "khong")
                sr.set("ly_do_khong_ap_dung", kad.get(cname, ""))
    for s in book.sheets.values():
        s.infer_kinds()
    return book


# --------------------------------------------------------------------------------------------------------------- QA
def build_qa(ctx, meta: dict, per_source, unmapped, per_file, fk_results, ncc: list[tuple]) -> Book:
    book = Book(ctx, "qa", "QA", "Kiểm tra của lần xuất (chỉ sinh khi chạy, không nằm trong gói)")
    nd = book.sheet("Nguon_du_lieu", "Nguồn dữ liệu", "Mọi nguồn quét tự động và độ phủ lá của nó")
    for c in ("loai", "kich_thuoc_byte", "sha256", "so_la", "so_la_anh_xa", "so_la_khong_xuat", "so_la_chua_anh_xa",
              "file_linh_vuc", "trang_thai"):
        nd.col(c)
    nk = book.sheet("Nguon_khong_doc_duoc", "Nguồn không đọc được", "Nguồn lỗi khi đọc, kèm lý do")
    nk.col("ly_do")
    kx = book.sheet("Khong_xuat", "Không xuất", "Trường bị loại và lý do")
    for c in ("nguon_mau", "mau_duong_dan", "ly_do", "so_la", "so_nguon", "khai_bao_o"):
        kx.col(c)
    cho = book.sheet("Cho_anh_xa", "Chờ ánh xạ", "Lá thuộc file chưa dựng")
    for c in ("nguon_mau", "mau_duong_dan", "file_se_xuat", "so_la", "so_nguon", "ghi_chu"):
        cho.col(c)
    kn = book.sheet("Khoa_ngoai", "Khóa ngoại", "Mọi khóa ngoại và kết quả test")
    for c in ("file", "sheet", "cot", "dich", "dich_chua_xuat", "so_gia_tri", "so_loi", "ket_qua", "vi_du_loi"):
        kn.col(c)
    kc = book.sheet("Kiem_cong_thuc", "Kiểm công thức", "Công thức Excel == giá trị mã game; input chép == file nguồn")
    for c in ("loai", "file", "sheet", "cot", "so_dong", "so_khop", "so_khong_kiem", "so_loi", "lech_lon_nhat", "doi_chieu",
              "ket_qua", "vi_du_loi"):
        kc.col(c)
    vd = book.sheet("Van_de", "Vấn đề", "Cảnh báo của lần xuất")
    vd.col("noi_dung")
    phu = book.sheet("Phu", "Độ phủ theo sheet", "Số dòng, cột, ô trống, ô đánh dấu của mỗi sheet")
    for c in ("file", "sheet", "so_dong", "so_cot", "so_la_anh_xa", "so_o_trong", "so_o_need_code_check", "so_o_need_source",
              "so_o_khong_ap_dung", "so_cot_tu_sinh"):
        phu.col(c)
    nc = book.sheet("Need_code_check", "Ô còn NEED_CODE_CHECK", "Ô mà chỉ mã C# tính ra và ExportGameDoc chưa điền")
    for c in ("file", "sheet", "dong", "cot"):
        nc.col(c)
    og = book.sheet("Ngoai_goi", "Sheet ngoài gói", "Sheet của bộ xuất không vào gói (mục 2.1, 2.5, 4) và số lá nguồn của nó")
    for c in ("ly_do", "so_dong", "so_la_nguon"):
        og.col(c)

    files_by_source = collections.defaultdict(set)
    for (sid, _path), where in ctx.cov.mapped.items():
        files_by_source[sid].add(where[0])
    for sid in sorted(ctx.sources):
        s = ctx.sources[sid]
        st = per_source.get(sid, collections.Counter())
        r = nd.row(sid, sid)
        r.set("loai", s.kind)
        r.set("kich_thuoc_byte", s.size)
        r.set("sha256", s.sha256() if s.kind != "cs_table" else "")
        r.set("so_la", st.get("leaves", 0))
        r.set("so_la_anh_xa", st.get("mapped", 0))
        r.set("so_la_khong_xuat", st.get("khong_xuat", 0))
        r.set("so_la_chua_anh_xa", st.get("unmapped", 0))
        r.set("file_linh_vuc", ";".join(sorted(files_by_source.get(sid, ()))))
        r.set("trang_thai", "KHONG_DOC_DUOC" if not s.readable else "THIEU" if st.get("unmapped") else "DU")
        if not s.readable:
            nk.row(sid, sid).set("ly_do", s.error or "không đọc được")
    for sid, why in ctx.unreadable:
        if sid not in nk.rows:
            nk.row(sid, sid).set("ly_do", why)
    for i, rule in enumerate(ctx.excluded):
        r = kx.row(f"KX{i + 1:03d}", rule.origin or SRC)
        for k, v in (("nguon_mau", rule.source_glob), ("mau_duong_dan", rule.pattern), ("ly_do", rule.reason),
                     ("so_la", rule.leaves), ("so_nguon", len(rule.sources)), ("khai_bao_o", rule.origin)):
            r.set(k, v)
    for i, rule in enumerate(ctx.pending):
        r = cho.row(f"CHO{i + 1:03d}", rule.origin)
        for k, v in (("nguon_mau", rule.source_glob), ("mau_duong_dan", rule.pattern), ("file_se_xuat", rule.target),
                     ("so_la", rule.leaves), ("so_nguon", len(rule.sources)), ("ghi_chu", rule.reason)):
            r.set(k, v)
    for res in fk_results:
        r = kn.row(f"{res['file']}/{res['sheet']}/{res['column']}", "core/fk.py")
        for k, v in (("file", res["file"]), ("sheet", res["sheet"]), ("cot", res["column"]), ("dich", res["targets"]),
                     ("dich_chua_xuat", res["targets_missing"]), ("so_gia_tri", res["values"]), ("so_loi", res["errors"]),
                     ("ket_qua", res["status"]), ("vi_du_loi", res["examples"])):
            r.set(k, v)
    for res in getattr(ctx, "formula_checks", []):
        r = kc.row(f"{res['kind']}/{res['file']}/{res['sheet']}/{res['column']}", "core/formula.py")
        for k, c in (("kind", "loai"), ("file", "file"), ("sheet", "sheet"), ("column", "cot"), ("rows", "so_dong"),
                     ("match", "so_khop"), ("unchecked", "so_khong_kiem"), ("errors", "so_loi"), ("max_diff", "lech_lon_nhat"),
                     ("reference", "doi_chieu"), ("status", "ket_qua"), ("examples", "vi_du_loi")):
            r.set(c, res[k])
    for i, text in enumerate(ctx.issues + [f"lá ánh xạ hai lần: {d[0]} {d[1]}: {d[2]} và {d[3]}" for d in ctx.cov.duplicates]):
        vd.row(f"V{i + 1:04d}", SRC).set("noi_dung", text)
    for i, (fid, sname, rid, col) in enumerate(ncc):
        r = nc.row(f"N{i + 1:05d}", SRC)
        r.set("file", fid)
        r.set("sheet", sname)
        r.set("dong", rid)
        r.set("cot", col)
    for fid, name, why, n in ctx.dropped:
        r = og.row(f"{fid}/{name}", SRC)
        r.set("ly_do", why)
        r.set("so_dong", n)
        r.set("so_la_nguon", ctx.cov.out_leaves.get(name, 0))
    for name, s in ctx.qa_sheets.items():
        r = og.row(f"12_he_thong_trang_thai/{name}", SRC)
        r.set("ly_do", ctx.out_sheets.get(name, ""))
        r.set("so_dong", len(s.rows))
        r.set("so_la_nguon", ctx.cov.out_leaves.get(name, 0))
    for fid, b in sorted(ctx.books.items()):
        for sname, s in b.sheets.items():
            p = phu.row(f"{fid}/{sname}", SRC)
            p.set("file", fid)
            p.set("sheet", sname)
            p.set("so_dong", len(s.rows))
            p.set("so_cot", len(s.column_order()))
            cnt = collections.Counter()
            for rw in s.rows.values():
                for c in s.column_order():
                    if c in ("nguon", "raw_json"):
                        continue
                    v = rw.values.get(c)
                    if v is None or v == "":
                        cnt["blank"] += 1
                    elif isinstance(v, str) and MARKER.match(v):
                        cnt[v] += 1
            p.set("so_la_anh_xa", sum(1 for w in ctx.cov.mapped.values() if w[0] == fid and w[1] == sname))
            p.set("so_o_trong", cnt["blank"])
            p.set("so_o_need_code_check", cnt["NEED_CODE_CHECK"])
            p.set("so_o_need_source", cnt["NEED_SOURCE"])
            p.set("so_o_khong_ap_dung", cnt["KHONG_AP_DUNG"])
            p.set("so_cot_tu_sinh", sum(1 for c in s.cols.values() if c.auto))
    for s in book.sheets.values():
        s.infer_kinds()
    return book


def coverage_md(meta: dict, per_source, unmapped, per_file, books: dict, ctx, strict: bool, ncc: list) -> str:
    tot = collections.Counter()
    for st in per_source.values():
        tot.update(st)
    lines = ["# COVERAGE (độ phủ khóa)", "",
             f"Commit {meta['commit']}, bản gốc so sánh {meta.get('ban_goc', '')}. Lá = mọi giá trị lá của mọi nguồn.", "",
             "| Mục | Số |", "|---|---|", f"| Nguồn | {len(per_source)} |", f"| Lá | {tot['leaves']} |",
             f"| Đã ánh xạ vào một cột (xlsx hoặc bulk.zip) | {tot['mapped']} |",
             f"| Khong_xuat (có lý do, gồm sheet ngoài gói) | {tot['khong_xuat']} |",
             f"| Chưa ánh xạ (FAIL) | {tot['unmapped']} |", f"| Lá ánh xạ hai nơi (FAIL) | {len(ctx.cov.duplicates)} |", "",
             "## Theo file", "", "| File | Lá đã ánh xạ | Sheet xlsx | Sheet bulk | Dòng | NEED_CODE_CHECK |", "|---|---|---|---|---|---|"]
    by_file = collections.Counter(f for f, *_ in ncc)
    for fid in sorted(books):
        b = books[fid]
        lines.append(f"| {fid} | {per_file.get(fid, 0)} | {sum(1 for s in b.sheets.values() if not s.bulk)} | "
                     f"{sum(1 for s in b.sheets.values() if s.bulk)} | {sum(len(s.rows) for s in b.sheets.values())} | "
                     f"{by_file.get(fid, 0)} |")
    lines += ["", "## Sheet ngoài gói (lá của chúng tính là Khong_xuat)", "", "| Sheet | Lý do | Lá |", "|---|---|---|"]
    for name, why in sorted(ctx.cov.out_reasons.items()):
        lines.append(f"| {name} | {why} | {ctx.cov.out_leaves.get(name, 0)} |")
    lines += ["", "## Khong_xuat theo luật", "", "| Nguồn | Mẫu | Lá | Lý do |", "|---|---|---|---|"]
    for rule in ctx.excluded:
        if rule.leaves:
            lines.append(f"| {rule.source_glob} | `{rule.pattern}` | {rule.leaves} | {rule.reason} |")
    lines += ["", "## Chưa ánh xạ", ""]
    if unmapped:
        lines += ["| Nguồn | Mẫu lá | Lá | Thuộc file |", "|---|---|---|---|"]
        for (sid, pat, target), n in sorted(unmapped.items()):
            lines.append(f"| {sid} | `{pat}` | {n} | {target} |")
    else:
        lines.append("Không có.")
    unread = [(sid, s.error) for sid, s in sorted(ctx.sources.items()) if not s.readable] + list(ctx.unreadable)
    lines += ["", "## Nguồn không đọc được", ""] + ([f"- {sid}: {why}" for sid, why in unread] or ["Không có."])
    lines += ["", f"Chế độ kiểm: {'strict' if strict else 'thường'}.", ""]
    return "\n".join(lines)
