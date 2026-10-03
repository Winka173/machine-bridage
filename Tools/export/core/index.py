"""File 00 (Machine_Brigade_00_Index): README, the file and sheet lists, Schema, coverage, versions, sources, Khong_xuat,
unclear units, foreign keys; plus COVERAGE.md. Built after every domain file and check."""
from __future__ import annotations

import collections
import json

from . import paths as P
from .model import MARKER, Book, natural_key

INDEX_ID = "00_chi_muc"

MARKERS_DOC = [
    ("o_trong", "Ô trống: không áp dụng cho dòng này."),
    ("CHUA_AP", "CHUA_AP:prompt_N: phần việc của prompt N chưa chạy, ô sẽ được điền khi nó chạy."),
    ("NEED_CODE_CHECK", "NEED_CODE_CHECK: giá trị chỉ mã C# tính ra; bộ xuất chưa đọc được (cần đọc mã hoặc ExportGameDoc)."),
    ("NEED_SOURCE", "NEED_SOURCE: thông số ngoài đời chưa có nguồn trong repo (spec 12.1); không điền từ trí nhớ."),
    ("danh_sach", "Danh sách đơn giản trong một ô ngăn bằng ';' (danh sách lồng: phần tử trong ngăn bằng ',')."),
    ("don_vi", "Đơn vị nằm ở tên cột (_s giây, _m mét, _m_s mét/giây, _deg_s độ/giây, _mm, _kg, hp, cp); ô số chỉ có số."),
    ("nguon", "Cột nguon: file nguồn + đường dẫn khóa (hoặc file C# + bảng) sinh ra dòng."),
    ("raw_json", "Cột raw_json: nguyên bản ghi gốc để khôi phục (danh sách con quá dài: thay bằng '<sheet con: khóa>')."),
    ("id", "Cột đầu là id ổn định (cùng id với dữ liệu); sheet con: <id cha>/<id hoặc thứ tự>."),
    ("so_voi_ban_goc", "so_voi_ban_goc: giong / doi / moi so với bản gốc ở Phien_ban.ban_goc; cột <tên>_truoc / <tên>_sau chỉ điền khi đổi."),
    ("sap_xep", "Dòng sắp theo id (thứ tự tự nhiên), cột theo thứ tự cố định: id, cột khai báo, cột tự sinh (A-Z), nguon, raw_json."),
]


def _std(sheet):
    return sheet


def build(ctx, meta: dict, per_source, unmapped, per_file, fk_results, planned: dict, built: list[str]) -> Book:
    book = Book(ctx, INDEX_ID, "Chỉ mục", "Mục lục, Schema, độ phủ, phiên bản, nguồn của bộ xuất")
    readme = book.sheet("README", "Đọc trước", "Cách đọc và chạy bộ xuất")
    readme.col("noi_dung", meaning="nội dung")
    mlf = book.sheet("Muc_luc_file", "Mục lục file", "Mọi file lĩnh vực (spec 1)")
    for c in ("tieu_de", "file_xlsx", "trang_thai", "so_sheet", "so_dong", "mo_ta"):
        mlf.col(c)
    mls = book.sheet("Muc_luc_sheet", "Mục lục sheet", "Mọi sheet: tên ASCII và tên tiếng Việt")
    for c in ("file", "sheet", "ten_viet", "lop", "sheet_cha", "so_dong", "so_cot", "mo_ta"):
        mls.col(c)
    schema = book.sheet("Schema", "Schema", "Mọi cột của mọi sheet ở mọi file")
    for c in ("file", "sheet", "cot", "thu_tu_cot", "kieu", "don_vi", "enum", "y_nghia", "nguon_khoa", "cong_thuc",
              "khoa_ngoai", "bat_buoc", "tu_sinh"):
        schema.col(c)
    phu = book.sheet("Phu", "Độ phủ theo sheet", "Số dòng, cột, ô trống, ô đánh dấu của mỗi sheet")
    for c in ("file", "sheet", "so_dong", "so_cot", "so_la_anh_xa", "so_o_trong", "so_o_chua_ap", "so_o_need_code_check",
              "so_o_need_source", "so_cot_tu_sinh"):
        phu.col(c)
    pb = book.sheet("Phien_ban", "Phiên bản", "Hash nguồn, commit, phiên bản luật, bản gốc so sánh")
    pb.col("gia_tri")
    nd = book.sheet("Nguon_du_lieu", "Nguồn dữ liệu", "Mọi nguồn quét tự động (spec 3.1) và độ phủ lá của nó")
    for c in ("loai", "kich_thuoc_byte", "sha256", "so_la", "so_la_anh_xa", "so_la_khong_xuat", "so_la_cho",
              "so_la_chua_anh_xa", "file_linh_vuc", "trang_thai"):
        nd.col(c)
    nk = book.sheet("Nguon_khong_doc_duoc", "Nguồn không đọc được", "Nguồn lỗi khi đọc, kèm lý do")
    nk.col("ly_do")
    kx = book.sheet("Khong_xuat", "Không xuất", "Trường bị loại (spec 8) và lý do")
    for c in ("nguon_mau", "mau_duong_dan", "ly_do", "so_la", "so_nguon", "khai_bao_o"):
        kx.col(c)
    cho = book.sheet("Cho_anh_xa", "Chờ ánh xạ", "Lá thuộc file lĩnh vực chưa xuất (lượt sau)")
    for c in ("nguon_mau", "mau_duong_dan", "file_se_xuat", "so_la", "so_nguon", "ghi_chu"):
        cho.col(c)
    dv = book.sheet("Don_vi_chua_ro", "Đơn vị chưa rõ", "Cột số mà bộ xuất chưa biết đơn vị")
    for c in ("file", "sheet", "cot", "vi_du"):
        dv.col(c)
    kn = book.sheet("Khoa_ngoai", "Khóa ngoại", "Mọi khóa ngoại và kết quả test (spec 2.2)")
    for c in ("file", "sheet", "cot", "dich", "dich_chua_xuat", "so_gia_tri", "so_loi", "ket_qua", "vi_du_loi"):
        kn.col(c)
    kc = book.sheet("Kiem_cong_thuc", "Kiểm công thức", "Lớp B: công thức Excel == giá trị mã game (port Python, sai số 1e-6); "
                    "input chép == file nguồn (spec 2.2, 2.3, 9.4)")
    for c in ("loai", "file", "sheet", "cot", "so_dong", "so_khop", "so_khong_kiem", "so_loi", "lech_lon_nhat", "doi_chieu",
              "ket_qua", "vi_du_loi"):
        kc.col(c)
    vd = book.sheet("Van_de", "Vấn đề", "Cảnh báo của lần xuất (cột ghi hai lần, sheet tự sinh, id trùng)")
    vd.col("noi_dung")

    src_index = "Tools/export (core/index.py)"

    # README -------------------------------------------------------------------------------------------------------
    lines = [
        ("muc_dich", "Bộ xuất toàn bộ dữ liệu cấu hình và cân bằng của Machine Brigade, chia theo lĩnh vực (spec Docs/prompts/export_full_vi.txt)."),
        ("chay", "python Tools/export/export.py [--out DIR] [--base REF] [--strict]: xuất, kiểm độ phủ khóa, khóa ngoại, bí mật."),
        ("chay_kiem", "python Tools/export/export.py coverage | fk: chỉ chạy một kiểm tra (không ghi file)."),
        ("chay_so_sanh", "python Tools/export/export.py diff <thư mục|commit A> <thư mục|commit B>: Docs/export/diff_<A>_<B>/ (lượt 7)."),
        ("chay_tu_kiem", "python Tools/export/export.py check: xuất hai lần, 9 kiểm của spec 9, 00_chi_muc/SELF_CHECK.md (lượt 8, CI)."),
        ("thu_muc", "00_chi_muc (file này, COVERAGE.md, MANIFEST.json, README.md), xlsx/, csv/<file>/<sheet>.csv; md/, images/, pdf/ ở lượt 6."),
        ("lop", "Lớp A = dữ liệu gốc; lớp B = suy ra (công thức sống, lượt 5); lớp C = báo cáo; kv = khối cài đặt (một dòng một lá)."),
        ("file_da_xuat", ";".join(built)),
    ] + MARKERS_DOC + [(f"ghi_chu_{i + 1}", f"{t}: {x}") for i, (t, x) in enumerate(ctx.notes)]
    for k, text in lines:
        r = readme.row(k, src_index)
        r.set("noi_dung", text)

    # Phien_ban ------------------------------------------------------------------------------------------------------
    for k, v in meta.items():
        r = pb.row(k, src_index)
        r.set("gia_tri", v)
    bal_sid = "Assets/MachineBrigade/Resources/Data/balance.json"
    if bal_sid in ctx.sources and isinstance(ctx.sources[bal_sid].data, dict) and "version" in ctx.sources[bal_sid].data:
        r = pb.row("balance_version", f"{bal_sid}: version")
        r.set("gia_tri", ctx.sources[bal_sid].data["version"], bal_sid, ("version",))

    # Nguon_du_lieu / Nguon_khong_doc_duoc ---------------------------------------------------------------------------
    files_by_source = collections.defaultdict(set)
    for (sid, _path), where in ctx.cov.mapped.items():
        files_by_source[sid].add(where[0])
    for rule in ctx.pending:
        for sid in rule.sources:
            files_by_source[sid].add(rule.target + " (chờ)")
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
        r.set("so_la_cho", st.get("pending", 0))
        r.set("so_la_chua_anh_xa", st.get("unmapped", 0))
        r.set("file_linh_vuc", ";".join(sorted(files_by_source.get(sid, ()))))
        if not s.readable:
            status = "KHONG_DOC_DUOC"
        elif st.get("unmapped"):
            status = "THIEU"
        elif st.get("pending"):
            status = "CHO"
        else:
            status = "DU"
        r.set("trang_thai", status)
        if not s.readable:
            rr = nk.row(sid, sid)
            rr.set("ly_do", s.error or "không đọc được")
    for sid, why in ctx.unreadable:
        if sid not in nk.rows:
            rr = nk.row(sid, sid)
            rr.set("ly_do", why)

    # Khong_xuat / Cho_anh_xa ----------------------------------------------------------------------------------------
    for i, rule in enumerate(ctx.excluded):
        r = kx.row(f"KX{i + 1:03d}", rule.origin or src_index)
        r.set("nguon_mau", rule.source_glob)
        r.set("mau_duong_dan", rule.pattern)
        r.set("ly_do", rule.reason)
        r.set("so_la", rule.leaves)
        r.set("so_nguon", len(rule.sources))
        r.set("khai_bao_o", rule.origin)
    for i, rule in enumerate(ctx.pending):
        r = cho.row(f"CHO{i + 1:03d}", rule.origin)
        r.set("nguon_mau", rule.source_glob)
        r.set("mau_duong_dan", rule.pattern)
        r.set("file_se_xuat", rule.target)
        r.set("so_la", rule.leaves)
        r.set("so_nguon", len(rule.sources))
        r.set("ghi_chu", rule.reason)

    # Khoa_ngoai -----------------------------------------------------------------------------------------------------
    for res in fk_results:
        r = kn.row(f"{res['file']}/{res['sheet']}/{res['column']}", "core/fk.py")
        r.set("file", res["file"])
        r.set("sheet", res["sheet"])
        r.set("cot", res["column"])
        r.set("dich", res["targets"])
        r.set("dich_chua_xuat", res["targets_missing"])
        r.set("so_gia_tri", res["values"])
        r.set("so_loi", res["errors"])
        r.set("ket_qua", res["status"])
        r.set("vi_du_loi", res["examples"])

    # Kiem_cong_thuc -------------------------------------------------------------------------------------------------
    for res in getattr(ctx, "formula_checks", []):
        r = kc.row(f"{res['kind']}/{res['file']}/{res['sheet']}/{res['column']}", "core/formula.py")
        for k, c in (("kind", "loai"), ("file", "file"), ("sheet", "sheet"), ("column", "cot"), ("rows", "so_dong"),
                     ("match", "so_khop"), ("unchecked", "so_khong_kiem"), ("errors", "so_loi"), ("max_diff", "lech_lon_nhat"),
                     ("reference", "doi_chieu"), ("status", "ket_qua"), ("examples", "vi_du_loi")):
            r.set(c, res[k])

    # Van_de ---------------------------------------------------------------------------------------------------------
    for i, text in enumerate(ctx.issues + [f"lá ánh xạ hai lần: {d[0]} {d[1]}: {d[2]} và {d[3]}" for d in ctx.cov.duplicates]):
        r = vd.row(f"V{i + 1:04d}", src_index)
        r.set("noi_dung", text)

    # Muc_luc_file ---------------------------------------------------------------------------------------------------
    all_books = dict(ctx.books)
    all_books[INDEX_ID] = book
    for fid, title in [(INDEX_ID, "Chỉ mục")] + list(planned.items()):
        r = mlf.row(fid, src_index)
        b = all_books.get(fid)
        r.set("tieu_de", title)
        if b is not None:
            r.set("file_xlsx", f"00_chi_muc/Machine_Brigade_00_Index_{meta['ngay']}.xlsx" if fid == INDEX_ID
                  else f"xlsx/{fid}.xlsx")
            r.set("trang_thai", "DA_XUAT")
            r.set("mo_ta", b.desc)
        else:
            r.set("trang_thai", "CHUA_XUAT")
            r.set("mo_ta", "chờ lượt sau (Docs/export/PLAN.md)")

    # Schema, Muc_luc_sheet, Don_vi_chua_ro (columns are final now) --------------------------------------------------
    for b in all_books.values():
        for s in b.sheets.values():
            s.infer_kinds()
    for fid in sorted(all_books):
        b = all_books[fid]
        for sname, s in b.sheets.items():
            for k, cname in enumerate(s.column_order()):
                c = s.cols.get(cname)
                r = schema.row(f"{fid}/{sname}/{cname}", src_index)
                r.set("file", fid)
                r.set("sheet", sname)
                r.set("cot", cname)
                r.set("thu_tu_cot", k + 1)
                if c is None:  # nguon / raw_json
                    r.set("kieu", "text")
                    r.set("y_nghia", "file + khóa nguồn của dòng" if cname == "nguon" else "nguyên bản ghi gốc (JSON)")
                    continue
                r.set("kieu", c.kind or "")
                r.set("don_vi", c.unit)
                r.set("enum", ";".join(c.enum) if isinstance(c.enum, (list, tuple)) else (c.enum or ""))
                r.set("y_nghia", c.meaning)
                r.set("nguon_khoa", c.source_note or _sources_text(c.sources))
                r.set("cong_thuc", c.formula or "")
                r.set("khoa_ngoai", ";".join(c.fk))
                r.set("bat_buoc", bool(c.required))
                r.set("tu_sinh", bool(c.auto))
                if c.unit_unknown and not c.unit and (c.kind in ("int", "number")):
                    sample = next((rw.values.get(cname) for rw in s.sorted_rows()
                                   if isinstance(rw.values.get(cname), (int, float))), "")
                    d = dv.row(f"{fid}/{sname}/{cname}", src_index)
                    d.set("file", fid)
                    d.set("sheet", sname)
                    d.set("cot", cname)
                    d.set("vi_du", sample)

    # Muc_luc_sheet / Phu: the index's own counts are known once every row above exists; Muc_luc_sheet and Phu get
    # one row per sheet, so their own row count is the number of sheets.
    n_sheets = sum(len(b.sheets) for b in all_books.values())
    for fid in sorted(all_books):
        b = all_books[fid]
        for sname, s in b.sheets.items():
            rows_n = n_sheets if (fid == INDEX_ID and sname in ("Muc_luc_sheet", "Phu")) else len(s.rows)
            r = mls.row(f"{fid}/{sname}", src_index)
            r.set("file", fid)
            r.set("sheet", sname)
            r.set("ten_viet", s.title_vi)
            r.set("lop", s.layer if s.kind != "kv" else "A_kv")
            r.set("sheet_cha", s.parent.name if s.parent is not None else "")
            r.set("so_dong", rows_n)
            r.set("so_cot", len(s.column_order()))
            r.set("mo_ta", s.desc)
            p = phu.row(f"{fid}/{sname}", src_index)
            p.set("file", fid)
            p.set("sheet", sname)
            p.set("so_dong", rows_n)
            p.set("so_cot", len(s.column_order()))
            cnt = collections.Counter()
            cols = [c for c in s.column_order() if c not in ("nguon", "raw_json")]
            for rw in s.rows.values():
                for c in cols:
                    v = rw.values.get(c)
                    if v is None or v == "":
                        cnt["blank"] += 1
                    elif isinstance(v, str) and MARKER.match(v):
                        cnt[v.split(":")[0]] += 1
            p.set("so_la_anh_xa", sum(1 for (_sid, _p), w in ctx.cov.mapped.items() if w[0] == fid and w[1] == sname))
            p.set("so_o_trong", cnt["blank"])
            p.set("so_o_chua_ap", cnt["CHUA_AP"])
            p.set("so_o_need_code_check", cnt["NEED_CODE_CHECK"])
            p.set("so_o_need_source", cnt["NEED_SOURCE"])
            p.set("so_cot_tu_sinh", sum(1 for c in s.cols.values() if c.auto))
    for s in book.sheets.values():
        s.infer_kinds()
    return book


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


def coverage_md(meta: dict, per_source, unmapped, per_file, books: dict, ctx, strict: bool) -> str:
    tot = collections.Counter()
    for st in per_source.values():
        tot.update(st)
    lines = [
        "# COVERAGE (độ phủ khóa, spec 3.3 và 3.5)",
        "",
        f"Commit {meta['commit']}, bản gốc so sánh {meta.get('ban_goc', '')}. Lá = mọi giá trị lá của mọi nguồn (Nguon_du_lieu).",
        "",
        "| Mục | Số |",
        "|---|---|",
        f"| Nguồn | {len(per_source)} |",
        f"| Lá | {tot['leaves']} |",
        f"| Đã ánh xạ vào một cột | {tot['mapped']} |",
        f"| Khong_xuat (có lý do) | {tot['khong_xuat']} |",
        f"| Chờ file lĩnh vực chưa xuất | {tot['pending']} |",
        f"| Chưa ánh xạ (FAIL) | {tot['unmapped']} |",
        f"| Lá ánh xạ hai nơi (FAIL) | {len(ctx.cov.duplicates)} |",
        "",
        "## Theo file lĩnh vực",
        "",
        "| File | Lá đã ánh xạ | Sheet | Dòng | Ô trống | CHUA_AP | NEED_CODE_CHECK |",
        "|---|---|---|---|---|---|---|",
    ]
    for fid in sorted(books):
        b = books[fid]
        rows = sum(len(s.rows) for s in b.sheets.values())
        blank = chua = ncc = 0
        for s in b.sheets.values():
            cols = [c for c in s.column_order() if c not in ("nguon", "raw_json")]
            for rw in s.rows.values():
                for c in cols:
                    v = rw.values.get(c)
                    if v is None or v == "":
                        blank += 1
                    elif isinstance(v, str) and v.startswith("CHUA_AP:"):
                        chua += 1
                    elif v == "NEED_CODE_CHECK":
                        ncc += 1
        lines.append(f"| {fid} | {per_file.get(fid, 0)} | {len(b.sheets)} | {rows} | {blank} | {chua} | {ncc} |")
    lines += ["", "## Khong_xuat", "", "| Nguồn | Mẫu | Lá | Lý do |", "|---|---|---|---|"]
    for rule in ctx.excluded:
        if rule.leaves:
            lines.append(f"| {rule.source_glob} | `{rule.pattern}` | {rule.leaves} | {rule.reason} |")
    lines += ["", "## Chờ file lĩnh vực chưa xuất", "", "| Nguồn | Mẫu | File | Lá |", "|---|---|---|---|"]
    for rule in ctx.pending:
        if rule.leaves:
            lines.append(f"| {rule.source_glob} | `{rule.pattern}` | {rule.target} | {rule.leaves} |")
    lines += ["", "## Chưa ánh xạ", ""]
    if unmapped:
        lines += ["| Nguồn | Mẫu lá | Lá | Thuộc file |", "|---|---|---|---|"]
        for (sid, pat, target), n in sorted(unmapped.items()):
            lines.append(f"| {sid} | `{pat}` | {n} | {target} |")
    else:
        lines.append("Không có.")
    unread = [(sid, s.error) for sid, s in sorted(ctx.sources.items()) if not s.readable] + list(ctx.unreadable)
    lines += ["", "## Nguồn không đọc được", ""]
    lines += [f"- {sid}: {why}" for sid, why in unread] or ["Không có."]
    from . import refcheck
    ref = refcheck.run(refcheck.from_ctx_books(books))
    lines += ["", "## Lớp tham chiếu ngoài đời và game (spec 12.6, lượt 10)", "",
              f"Trạng thái: {ref['status']}" + (f" ({'; '.join(ref['gaps'])})" if ref["gaps"] else "") + ". Chỉ dữ liệu trong "
              "repo (không tra web); thiếu nguồn ghi NEED_SOURCE.", ""] + ref["lines"]
    lines += ["", f"Chế độ kiểm: {'strict (lá chờ cũng FAIL)' if strict else 'thường (lá chờ file chưa xuất được phép)'}.", ""]
    return "\n".join(lines)
