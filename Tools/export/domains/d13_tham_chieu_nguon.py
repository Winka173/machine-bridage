"""13_tham_chieu_nguon (pass 10, spec 12): the real-world and game reference layer.

Built last (it reads every other file): adds <name>_tham_chieu and <name>_so_sanh_that to files 01-11 (_ref_units.py for
01-04, _ref_other.py for 05-11), then this file's sheets: Nguon_tham_chieu (every document a repo note names, and the repo
documents themselves), Tham_chieu_game_co_che, Tham_chieu_hoc_thuyet, Thieu_nguon, Tai_lieu_ban_quyen, plus
Tham_chieu_de_xuat (the reference columns of the proposal sheets of the balance workbook) and Tham_chieu_decisions (the
"References" passages of DECISIONS). A co_lech_lon row with no reason gets a line in 12/Cho_quyet. No web lookup (the owner's
call, 03/10): only repo data; NEED_SOURCE where the repo has nothing. Read only: no game value is changed.
"""
from __future__ import annotations

import collections
import re

from core.model import NEED_SOURCE

from . import _ref_common as C
from . import _ref_other as O
from . import _ref_units as U
from . import _refsrc as S

FILE_ID = "13_tham_chieu_nguon"
TITLE = "Tham chiếu ngoài đời và game (nguồn)"
DESC = ("Nguồn tham chiếu, cơ chế lấy từ game, học thuyết, danh sách thiếu nguồn, tài liệu bản quyền (spec 12.3; chỉ dữ liệu "
        "trong repo, không tra web)")
PRIORITY = {"01": 1, "02": 1, "03": 1, "04": 2}
GAME_WORDS = ("StarCraft", "World of Tanks", "War Thunder", "Battlefield", "Wargame", "Company of Heroes", "Halo", "Warhammer",
              "Gears of War", "Metal Gear", "Ace Combat", "Red Alert", "Supreme Commander", "Command & Conquer", "Mass Effect")
FILM_WORDS = ("Star Wars", "Star Destroyer", "The Expanse", "Galactica", "Venator")


def ref_sheets(ctx):
    """[(file, sheet)] of every <name>_tham_chieu sheet built."""
    return [(fid, s) for fid in sorted(ctx.books) for s in ctx.books[fid].sheets if s.endswith("_tham_chieu")]


def build(ctx):
    reg = S.Registry()
    R = U.Ctx(ctx, reg)
    U.build_01(R, ctx.books["01_vu_khi_dan"])
    U.build_02_04(R)
    O.build_05_11(R, {})
    book = ctx.book(FILE_ID, TITLE, DESC)

    # ------------------------------------------------------------------ Cho_quyet lines (12) for unexplained deviations
    cq = ctx.books["12_he_thong_trang_thai"].sheets["Cho_quyet"]
    for i, (fid, sname, rid, txt) in enumerate(sorted(R.cho_quyet), 1):
        qid = f"TC{i:04d}"
        r = cq.row(qid, f"{FILE_ID} (lượt 10): {fid}/{sname} dòng {rid}")
        r.set("dong", "")
        r.set("muc", "")
        r.set("noi_dung", f"co_lech_lon chưa có lý do: {fid}/{sname} {rid}: {txt}")
        ctx.books[fid].sheets[sname].rows[rid].values["cho_quyet_id"] = qid

    # ------------------------------------------------------------------ Tham_chieu_game_co_che
    cc = book.sheet("Tham_chieu_game_co_che", "Cơ chế lấy ý từ game", "Mỗi cơ chế lấy ý từ game một dòng (spec 12.3): từ các "
                    "sheet tham chiếu 01-11, nghiên cứu AI, bảng cân bằng (đề xuất), DECISIONS")
    for col, m in (("ten_game", "game"), ("co_che", "cơ chế (ngắn)"), ("nhom", "kinh_te / AI / ban_do / che_do / UI / meta / "
                   "model / hieu_ung / vu_khi"), ("diem_giong", "điểm giống"), ("diem_khac_co_chu_dich", "điểm khác có chủ đích"),
                   ("ly_do", "lý do"), ("cam_giac_khac_khi_choi", "cảm giác khác khi chơi"),
                   ("muc_ap_dung", "nguyen_ban / sua / chi_lay_y / de_xuat (chưa có trong game)"),
                   ("dan_den_sheet", "file / sheet liên quan (ngăn ';')"), ("thuc_the", "thực thể dùng (ngăn ';', cắt 60)"),
                   ("nguon_id", "nguồn")):
        cc.col(col, meaning=m, fk=C.NGUON_FK if col == "nguon_id" else None)
    agg = {}

    def add_mech(game, mech, nhom, sheet_ref, entity, nguon, muc="chi_lay_y", giong="", khac="", cam="", ly=""):
        game = S.text(game)
        if not game or game == NEED_SOURCE or not S.game_like(game):
            return
        mech = S.text(mech) or "(không ghi cơ chế)"
        key = (nhom, S.slug(game, 40), S.slug(mech, 60))
        a = agg.setdefault(key, {"ten_game": game, "co_che": mech, "nhom": nhom, "sheets": set(), "ents": set(), "nguon": set(),
                                 "muc": muc, "giong": giong, "khac": khac, "cam": cam, "ly": ly})
        a["sheets"].add(sheet_ref)
        if entity:
            a["ents"].add(str(entity))
        a["nguon"] |= {x for x in nguon if x}

    nhom_of = {"01": "vu_khi", "02": "model", "03": "model", "04": "AI", "05": "che_do", "06": "AI", "07": "chien_dich",
               "08": "ban_do", "09": "hieu_ung", "10": "model", "11": "meta"}
    for fid, sname in ref_sheets(ctx):
        sh = ctx.books[fid].sheets[sname]
        for rid, r in sh.rows.items():
            games = str(r.values.get("ten_game") or "").split(";")
            mechs = str(r.values.get("co_che_game") or "").split(";")
            if not any(g and g != NEED_SOURCE for g in games):
                continue
            nguon = str(r.values.get("nguon_id") or "").split(";")
            for i, g in enumerate(games):
                m = mechs[i] if i < len(mechs) else ""
                nh = nhom_of[fid[:2]]
                if fid[:2] == "04" and m.startswith("hình dáng"):
                    nh = "model"
                add_mech(g, m, nh, f"{fid}/{sname}", r.values.get("entity_id"), nguon,
                         muc="chi_lay_y", giong=str(r.values.get("diem_giong") or "")[:200],
                         khac=str(r.values.get("diem_khac_co_chu_dich") or "")[:200])
    N_AI = reg.repo(S.AI_RESEARCH, "Nghiên cứu AI (Machine_Brigade_AI_Research.xlsx)")
    for kind, ref, behave in getattr(R, "tower_research", []):
        for g, m in S.split_items(ref):
            add_mech(g, m or f"chọn mục tiêu của {kind}", "AI", "04_can_cu_thap/Can_cu_tham_chieu; 06_ai/AI_thap", kind, [N_AI],
                     giong=behave[:200])
    for r in S.xlsx_rows(S.AI_RESEARCH, "Boss"):
        for g, m in S.split_items(S.text(r.get("Tham khảo"))):
            add_mech(g, m or "hành vi boss", "AI", "06_ai/AI_boss; 03_boss/Boss_tham_chieu", S.text(r.get("Nhóm"))[:60], [N_AI],
                     giong=S.text(r.get("Hành vi AI"))[:200])
    for r in S.xlsx_rows(S.AI_RESEARCH, "Kỹ thuật AI"):
        for g, _m in S.split_items(S.text(r.get("Game đã dùng"))):
            if g.lower().startswith(("phổ biến", "nhiều")):
                continue
            add_mech(g, S.text(r.get("Kỹ thuật")), "AI", "06_ai/AI_tham_so", "", [N_AI] + O._match_sources(g, R.ai_src),
                     giong=S.text(r.get("Cách dùng trong game"))[:200])
    for sheet, key_col, val_col in (("Tổng quan", "Mục", "Nội dung"), ("Tính năng chọn chiến thuật", "Mục", "Mô tả")):
        for r in S.xlsx_rows(S.AI_RESEARCH, sheet):
            t = S.text(r.get(val_col))
            m = re.search(r"Tham khảo[^:]*:?\s*(.*)$", t)
            if not m:
                continue
            for g in GAME_WORDS + ("Hearts of Iron IV", "Command: Modern Operations"):
                if g in m.group(1):
                    add_mech(g, f"{S.text(r.get(key_col))}: {m.group(1)[:160]}", "UI" if "chọn" in t.lower() else "AI",
                             "06_ai/Chien_thuat", "", [N_AI] + O._match_sources(g, R.ai_src))

    # proposals of the balance workbook (not in the game yet)
    dx = book.sheet("Tham_chieu_de_xuat", "Đề xuất: tham chiếu ngoài đời / game", "Các sheet đề xuất của bảng cân bằng (Đề xuất "
                    "thêm, Công trình mới, Tên lửa & bom mới, Boss mới, Thẻ hỗ trợ mới): mẫu thật, game, cảm giác khác (chưa có "
                    "trong game)")
    for col, m in (("sheet_nguon", "sheet của Machine_Brigade_Can_bang.xlsx"), ("ten_de_xuat", "tên đề xuất"),
                   ("ten_mau_that", "tham khảo ngoài đời"), ("ten_game", "tham khảo game"),
                   ("cam_giac_khac_khi_choi", "cảm giác khác"), ("do_tin_cay", "độ tin"), ("nguon_id", "nguồn")):
        dx.col(col, meaning=m, fk=C.NGUON_FK if col == "nguon_id" else None)
    for sheet, name_col, real_col, game_col, feel_col in (
            ("Đề xuất thêm", "Tên đề xuất", "Tham khảo ngoài đời (mẫu)", "Tham khảo game (tên)", "Cảm giác khác khi chơi (so với)"),
            ("Công trình mới", "Tên", "Tham khảo ngoài đời", "Tham khảo game", "Cảm giác khác"),
            ("Tên lửa & bom mới", "Tên", "Tham khảo ngoài đời", None, "Cảm giác khác"),
            ("Boss mới", "Tên · dòng phụ", "Mẫu thật", "Tham khảo game", None),
            ("Thẻ hỗ trợ mới", "Thẻ", "Tham khảo", None, None)):
        for i, r in enumerate(S.xlsx_rows(S.CAN_BANG, sheet)):
            name = S.text(r.get(name_col))
            if not name:
                continue
            rid = f"{S.slug(sheet, 20)}/{i:03d}"
            row = dx.row(rid, f"{S.CAN_BANG}: {sheet} dòng {i + 2}")
            game = S.text(r.get(game_col)) if game_col else ""
            row.set("sheet_nguon", sheet)
            row.set("ten_de_xuat", name)
            row.set("ten_mau_that", S.text(r.get(real_col)))
            row.set("ten_game", game)
            row.set("cam_giac_khac_khi_choi", S.text(r.get(feel_col)) if feel_col else "")
            row.set("do_tin_cay", "uoc_dinh")
            row.set("nguon_id", R.N_CB)
            for g, m in S.split_items(game):
                add_mech(g, m or name, "de_xuat", f"{FILE_ID}/Tham_chieu_de_xuat", name, [R.N_CB], muc="de_xuat",
                         cam=row.values["cam_giac_khac_khi_choi"][:200])

    # DECISIONS "References" passages
    dr = book.sheet("Tham_chieu_decisions", "Tham chiếu trong DECISIONS", "Mọi đoạn '**References**' của Docs/DECISIONS.md: "
                    "mục, dòng, văn bản (của nhóm, cắt 600), game / phim nêu tên")
    for col, m in (("muc", "mục ## chứa đoạn"), ("muc_con", "mục ###"), ("dong", "số dòng"), ("van_ban", "văn bản (cắt 600)"),
                   ("game_phim_nhac_den", "game / phim nhắc đến (theo danh sách tên cố định)"), ("nguon_id", "nguồn")):
        dr.col(col, meaning=m, fk=C.NGUON_FK if col == "nguon_id" else None)
    for i, p in enumerate(S.decisions_references(R.dec), 1):
        works = [g for g in GAME_WORDS + FILM_WORDS if g in p["van_ban"]]
        row = dr.row(f"REF{i:03d}", f"{S.DECISIONS}:{p['dong']}")
        row.set("muc", p["muc"])
        row.set("muc_con", p["muc_con"])
        row.set("dong", p["dong"])
        row.set("van_ban", p["van_ban"])
        row.set("game_phim_nhac_den", ";".join(works))
        row.set("nguon_id", R.N_DEC)
        txt = p["van_ban"].lower()
        nh = "hieu_ung" if any(w in txt for w in ("burning", "flak", "smoke", "fire", "flame")) else (
            "vu_khi" if "harm" in txt or "sead" in txt else "model")
        for g in works:
            if g in GAME_WORDS:
                add_mech(g, f"DECISIONS {p['muc_con'] or p['muc']}"[:120], nh, f"{FILE_ID}/Tham_chieu_decisions", f"REF{i:03d}",
                         [R.N_DEC])
    for (nh, gs, ms), a in sorted(agg.items()):
        r = cc.row(f"{nh}/{gs}/{ms}", "; ".join(sorted(a["sheets"])))
        r.set("ten_game", a["ten_game"])
        r.set("co_che", a["co_che"])
        r.set("nhom", nh)
        r.set("diem_giong", a["giong"])
        r.set("diem_khac_co_chu_dich", a["khac"])
        r.set("ly_do", a["ly"])
        r.set("cam_giac_khac_khi_choi", a["cam"])
        r.set("muc_ap_dung", a["muc"])
        r.set("dan_den_sheet", ";".join(sorted(a["sheets"])))
        ents = sorted(a["ents"])
        r.set("thuc_the", ";".join(ents[:60]) + (f";…(+{len(ents) - 60})" if len(ents) > 60 else ""))
        r.set("nguon_id", C.join(sorted(a["nguon"])))

    # ------------------------------------------------------------------ Tham_chieu_hoc_thuyet
    ht = book.sheet("Tham_chieu_hoc_thuyet", "Học thuyết quân sự và thuật ngữ", "Học thuyết / thuật ngữ quân sự dùng cho AI "
                    "(nghiên cứu AI: cột 'Ngoài đời' của Chiến thuật, 'Học thuyết ngoài đời' của Vai trò) kèm nguồn")
    for col, m in (("thuat_ngu", "học thuyết / thuật ngữ"), ("mo_ta", "mô tả (văn bản repo, cắt 500)"),
                   ("dung_o", "file / sheet / thực thể dùng"), ("do_tin_cay", "độ tin"), ("nguon_id", "nguồn")):
        ht.col(col, meaning=m, fk=C.NGUON_FK if col == "nguon_id" else None)
    for term, desc, where, ids in sorted(getattr(R, "doctrine", [])):
        rid = S.slug(where.split("/", 1)[1], 60)
        r = ht.row(rid, f"{S.AI_RESEARCH} ({where})")
        r.set("thuat_ngu", term)
        r.set("mo_ta", desc[:500])
        r.set("dung_o", where)
        r.set("do_tin_cay", "da_kiem_chung" if len(ids) > 1 else "ban_dau_doan")
        r.set("nguon_id", C.join(ids))

    # ------------------------------------------------------------------ Thieu_nguon
    tn = book.sheet("Thieu_nguon", "Thiếu nguồn", "Mọi ô NEED_SOURCE của các sheet tham chiếu (spec 12.3), xếp theo độ ưu tiên "
                    "(1: xe, vũ khí, boss; 2: căn cứ và tháp; 3: còn lại) rồi lĩnh vực, thực thể, cột")
    for col, m in (("uu_tien", "1 xe / vũ khí / boss, 2 căn cứ / tháp, 3 còn lại"), ("file", "file lĩnh vực"),
                   ("sheet", "sheet tham chiếu"), ("dong_id", "id dòng"), ("entity_id", "thực thể"), ("cot", "cột thiếu"),
                   ("ten_hien_thi", "tên"), ("ten_mau_that", "mẫu thật đã biết (giúp tìm nguồn)")):
        tn.col(col, meaning=m)
    for fid, sname in ref_sheets(ctx):
        sh = ctx.books[fid].sheets[sname]
        pr = PRIORITY.get(fid[:2], 3)
        for rid, r in sh.rows.items():
            for col in sh.column_order():
                if r.values.get(col) == NEED_SOURCE:
                    row = tn.row(f"P{pr}/{fid}/{sname}/{rid}/{col}", f"{fid}/{sname}")
                    row.set("uu_tien", pr)
                    row.set("file", fid)
                    row.set("sheet", sname)
                    row.set("dong_id", str(rid))
                    row.set("entity_id", str(r.values.get("entity_id") or ""))
                    row.set("cot", col)
                    row.set("ten_hien_thi", str(r.values.get("ten_hien_thi") or ""))
                    tm = r.values.get("ten_mau_that")
                    row.set("ten_mau_that", "" if tm == NEED_SOURCE else str(tm or ""))

    # ------------------------------------------------------------------ Nguon_tham_chieu
    used = collections.Counter()
    for fid in ctx.books:
        for s in ctx.books[fid].sheets.values():
            if "nguon_id" not in s.cols:
                continue
            for r in s.rows.values():
                for x in str(r.values.get("nguon_id") or "").split(";"):
                    if x:
                        used[x] += 1
    ng = book.sheet("Nguon_tham_chieu", "Nguồn tham chiếu", "Mọi tài liệu mà ghi chú trong repo nêu tên, và chính các tài liệu "
                    "repo mang ghi chú (spec 12.3). URL chỉ khi repo ghi; ngày truy cập theo nguồn repo (bảng REAL: 2026-10-02)")
    for col, m in (("loai", "tai_lieu_repo / tai_lieu_quan_su_chinh_thuc / nha_san_xuat / nha_phat_hanh_game / wikipedia / "
                    "bai_bao / wiki_game / thu_vien_am_thanh"), ("tieu_de", "tiêu đề như nguồn repo ghi"),
                   ("tac_gia_to_chuc", "tác giả / tổ chức (khi repo ghi)"), ("nam", "năm (khi repo ghi)"),
                   ("url", "URL (chỉ khi repo ghi)"), ("ngay_truy_cap", "ngày truy cập (khi repo ghi)"),
                   ("do_tin_cay", "1 chính thức / nhà sản xuất, 2 thứ cấp uy tín, 3 cộng đồng / ghi chú nội bộ"),
                   ("duong_dan_repo", "đường dẫn trong repo (tài liệu repo)"), ("trich_tu", "tài liệu repo nêu nguồn này"),
                   ("so_lan_dung", "số ô nguon_id trỏ tới"), ("ghi_chu", "ghi chú")):
        ng.col(col, meaning=m)
    for nid in sorted(reg.rows):
        d = reg.rows[nid]
        r = ng.row(nid, d["trich_tu"] or d["duong_dan_repo"] or "pass 10")
        for k in ("loai", "tieu_de", "tac_gia_to_chuc", "nam", "url", "ngay_truy_cap", "do_tin_cay", "duong_dan_repo", "trich_tu"):
            r.set(k, d[k])
        r.set("so_lan_dung", used.get(nid, 0))
        if nid == R.N_REFS and isinstance(R.refs, dict) and "_about" in R.refs:
            r.set("ghi_chu", R.refs["_about"], S.UNIT_REFS, ("_about",))
        else:
            r.set("ghi_chu", d["ghi_chu"])

    # ------------------------------------------------------------------ Tai_lieu_ban_quyen
    bq = book.sheet("Tai_lieu_ban_quyen", "Tài liệu và tác phẩm có bản quyền", "Nguồn ngoài và game / phim được nhắc: chỉ dùng "
                    "ý tưởng và thông số (sự kiện), không dùng văn bản, ảnh, tên, logo, mô hình (spec 12.5)")
    for col, m in (("loai", "tai_lieu / game / phim_truyen"), ("ten", "tên"), ("nguon_id", "nguồn (tài liệu)"),
                   ("cach_dung", "cách được dùng"), ("dung_o", "sheet nhắc tới (ngăn ';')")):
        bq.col(col, meaning=m, fk=C.NGUON_FK if col == "nguon_id" else None)
    rule = "chỉ ý tưởng và thông số (sự kiện); không chép văn bản, ảnh, tên, logo, mô hình; không lưu ảnh trong repo"
    for nid in sorted(reg.rows):
        d = reg.rows[nid]
        if d["loai"] == "tai_lieu_repo":
            continue
        r = bq.row(f"tai_lieu/{nid}", d["trich_tu"] or "pass 10")
        r.set("loai", "tai_lieu")
        r.set("ten", d["tieu_de"])
        r.set("nguon_id", nid)
        r.set("cach_dung", rule)
        r.set("dung_o", d["trich_tu"])
    works = collections.defaultdict(set)
    for fid, sname in ref_sheets(ctx):
        for r in ctx.books[fid].sheets[sname].rows.values():
            for col, kind in (("ten_game", "game"), ("ten_phim_truyen", "phim_truyen")):
                for w in str(r.values.get(col) or "").split(";"):
                    if w and w != NEED_SOURCE:
                        works[(kind, w)].add(f"{fid}/{sname}")
    for a in agg.values():
        works[("game", a["ten_game"])] |= a["sheets"]
    seen = set()
    for (kind, w), where in sorted(works.items()):
        rid = f"{kind}/{S.slug(w, 60)}"
        n = 2
        while rid in seen:
            rid = f"{kind}/{S.slug(w, 60)}_{n}"
            n += 1
        seen.add(rid)
        r = bq.row(rid, "; ".join(sorted(where))[:200])
        r.set("loai", kind)
        r.set("ten", w)
        r.set("nguon_id", "")
        r.set("cach_dung", "chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn bản, ảnh, âm thanh hay mô hình của tác phẩm")
        r.set("dung_o", ";".join(sorted(where)))

    # unit_refs keys used
    left = sorted(k for k in (R.refs if isinstance(R.refs, dict) else {}) if k not in R.used_refs)
    for k in left:
        ctx.issue(f"{S.UNIT_REFS}: key {k} not exported (no tham_chieu row)")
    return book
