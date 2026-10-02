"""07_chien_dich_cot_truyen, layer A: chapters, missions (and their stages, units, radio, events, nav states), the
dialogue (every line one row), speakers, dialogue triggers, game decks (fixed decks), the event library, the release
switches and the source script text."""
from __future__ import annotations

import re

from core.model import NEED_CODE_CHECK, child_rows, chua_ap

from . import _b07
from . import _lane_c as C

FILE_ID = "07_chien_dich_cot_truyen"
TITLE = "Chiến dịch và cốt truyện"
DESC = "Chương, nhiệm vụ (giai đoạn, quân, radio, biến cố, trạng thái nav), thoại (mỗi câu một dòng), nhân vật, trigger, " \
       "bộ bài game, thư viện biến cố, phát hành, kịch bản gốc"

CAMP = C.CAMPAIGN
SCRIPT = C.DATA + "script/"
SPEAKERS = SCRIPT + "speakers.json"
RELEASE = C.DATA + "release.json"
STORY_TXT = "Tools/story/script/"
MISSION_FK = ["07_chien_dich_cot_truyen/Nhiem_vu"]
EVENT_FK = ["07_chien_dich_cot_truyen/Bien_co"]
SPEAKER_FK = ["07_chien_dich_cot_truyen/Nhan_vat"]
MAP_FK = ["08_ban_do/Ban_do_goc"]
BOSS_FK = ["03_boss/Boss"]


def _script_files(ctx):
    return sorted(sid for sid in ctx.sources if re.fullmatch(re.escape(SCRIPT) + r"ch\d+\.json", sid))


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    camp = ctx.data(CAMP)
    scripts = [(sid, ctx.data(sid)) for sid in _script_files(ctx)]

    # ------------------------------------------------------------------ Chuong
    ch = book.sheet("Chuong", "Chương", "campaign.json chapters: 15 chương (hồi, bản đồ, tướng, boss chủ lực / mini, truyện tranh)")
    ch.col("maps", meaning="bản đồ của chương (ngăn ';')", fk=MAP_FK)
    ch.col("main", meaning="boss chủ lực", fk=BOSS_FK)
    ch.col("minis", meaning="boss mini (ngăn ';')", fk=BOSS_FK)
    ch.col("general", meaning="tướng địch", fk=["06_ai/AI_tuong"])
    ch.col("tep_thoai_chuong", meaning="số chương ghi trong file thoại script/chNN.json (chapter)")
    ch.col("tep_thoai", meaning="file thoại của chương")
    ch.col("so_cau_thoai", meaning="số câu thoại trong file thoại của chương")
    for i, c in enumerate(camp.get("chapters") or []):
        r = ch.row(c.get("number", i + 1), C.nguon(CAMP, ("chapters", i)), raw=c)
        r.flatten(c, CAMP, ("chapters", i))
    for sid, s in scripts:
        n = s.get("chapter")
        r = ch.rows.get(n)
        if r is None:
            r = ch.row(n, sid)
        r.set("tep_thoai_chuong", n, sid, ("chapter",))
        r.set("tep_thoai", sid.rsplit("/", 1)[-1])
        r.set("so_cau_thoai", len(s.get("lines") or []))

    # ------------------------------------------------------------------ Nhiem_vu (+ children)
    nv = book.sheet("Nhiem_vu", "Nhiệm vụ", "campaign.json missions: 193 nhiệm vụ (chương, mục tiêu, bản đồ, giờ, boss, thời tiết, "
                    "bộ bài địch, sao, biến cố); người nói chính từ script/chNN.json missions.<id>.main")
    nv.col("chapter", meaning="chương", fk=["07_chien_dich_cot_truyen/Chuong"])
    nv.col("map", meaning="bản đồ (id gốc, 08/Ban_do_goc)", fk=MAP_FK)
    nv.col("general", meaning="tướng địch", fk=["06_ai/AI_tuong"])
    nv.col("enemy_deck", meaning="bộ bài địch (ngăn ';')", fk=C.UNIT_FK)
    nv.col("unlocks", meaning="thẻ mở khóa khi thắng (ngăn ';')", fk=C.UNIT_FK)
    nv.col("after", meaning="nhiệm vụ phải xong trước", fk=MISSION_FK)
    nv.col("boss_def", meaning="boss của nhiệm vụ", fk=BOSS_FK)
    nv.col("nguoi_noi_chinh", meaning="người nói chính (script/chNN.json missions.<id>.main)", fk=SPEAKER_FK)
    nv.col("bo_bai_game", meaning="có bộ bài game (fixedDeck): xem Bo_bai_game")
    nv.col("so_cau_thoai", meaning="số câu thoại của nhiệm vụ (Thoai)")
    nv.col("trang_thai_kich_ban", meaning="trạng thái kịch bản (Docs/story; chưa có trong dữ liệu)")

    def sub(name, title, desc, parent, **fk):
        s = book.sheet(name, title, desc, parent=parent)
        for col, targets in fk.items():
            s.col(col, fk=targets)
        return s

    quan = sub("Nhiem_vu_quan", "Nhiệm vụ: quân đặt sẵn", "missions[].units: quân đặt sẵn (đội, vị trí, hướng)", nv, **{"def": C.UNIT_FK})
    radio = sub("Nhiem_vu_radio", "Nhiệm vụ: radio", "missions[].radio: khóa câu radio, lúc phát", nv)
    san = sub("Nhiem_vu_san", "Nhiệm vụ: mục tiêu săn", "missions[].hunt: đơn vị phải săn và tuyến", nv, **{"def": C.UNIT_FK})
    tips = sub("Nhiem_vu_goi_y", "Nhiệm vụ: gợi ý", "missions[].tips: khóa gợi ý, lúc hiện", nv)
    ally_u = sub("Nhiem_vu_dong_minh", "Nhiệm vụ: quân đồng minh", "missions[].ally.units", nv, **{"def": C.UNIT_FK})
    ally_s = sub("Nhiem_vu_dong_minh_cong_trinh", "Nhiệm vụ: công trình đồng minh", "missions[].ally.structures", nv,
                 **{"def": C.UNIT_FK})
    ally_r = sub("Nhiem_vu_dong_minh_tiep_vien", "Nhiệm vụ: tiếp viện đồng minh", "missions[].ally.reinforcements", nv,
                 units=C.UNIT_FK)
    ev = sub("Nhiem_vu_bien_co", "Nhiệm vụ: biến cố", "missions[].missionEvents: id biến cố (thư viện) hoặc bản ghi ghi đè",
             nv, bien_co=EVENT_FK)
    gd = sub("Nhiem_vu_giai_doan", "Nhiệm vụ: giai đoạn", "missions[].stages: mục tiêu, CP, lựa chọn, sóng địch, biến cố mỗi giai đoạn", nv)
    gd_ev = sub("Nhiem_vu_giai_doan_su_kien", "Giai đoạn: sự kiện", "stages[].events: radio, quân, hỗ trợ", gd, units=C.UNIT_FK)
    gd_ch = sub("Nhiem_vu_giai_doan_lua_chon", "Giai đoạn: lựa chọn", "stages[].choices: khóa và giai đoạn kế", gd)
    gd_be = sub("Nhiem_vu_giai_doan_bien_co", "Giai đoạn: biến cố", "stages[].missionEvents", gd, bien_co=EVENT_FK)
    ns = sub("Nhiem_vu_nav_state", "Nhiệm vụ: trạng thái nav dựng sẵn", "missions[].navStates: vùng đổi trạng thái (thủy triều, cầu)", nv)
    ns_t = sub("Nhiem_vu_nav_state_trang_thai", "Trạng thái nav: các trạng thái", "navStates[].states", ns)
    ns_b = sub("Nhiem_vu_nav_chan", "Trạng thái nav: khối chặn", "navStates[].states[].blocks: hình chữ nhật chặn", ns_t)

    def events_cb(sheet):
        def cb(row, items, src, path):
            for j, item in enumerate(items):
                tag = item if isinstance(item, str) else item.get("id", j)
                r = sheet.row(f"{row.id}/{j}", C.nguon(src, path + (j,)), raw=item)
                r.set(sheet.parent_col, row.id)
                r.set("thu_tu", j)
                if isinstance(item, dict):
                    r.set("bien_co", item.get("id", ""))
                    r.flatten(item, src, path + (j,), skip=("id",))
                    if "id" in item:
                        r.mark(src, path + (j, "id"), "bien_co")
                else:
                    r.set("bien_co", tag, src, path + (j,))
        return cb

    stage_children = {"events": C.child(gd_ev), "choices": C.child(gd_ch),
                      "missionEvents": events_cb(gd_be)}
    nav_children = {"states": lambda row, items, src, p: child_rows(
        ns_t, row, items, src, p, children={"blocks": C.child(ns_b)})}
    deck_sheet = book.sheet("Bo_bai_game", "Bộ bài game", "missions[].fixedDeck: 23 màn bộ bài cố định (8 xe, 2 hỗ trợ, "
                            "đồng minh đặt sẵn, thẻ mượn, luật riêng, trạng thái)")
    deck_sheet.col("nhiem_vu_id", meaning="nhiệm vụ", fk=MISSION_FK, required=True)
    deck_sheet.col("vehicle_ids", meaning="8 xe (ngăn ';')", fk=C.UNIT_FK)
    deck_sheet.col("support_ids", meaning="2 thẻ hỗ trợ (ngăn ';')", fk=C.SUPPORT_FK)
    deck_sheet.col("loaned_cards", meaning="thẻ mượn (ngăn ';')", fk=C.UNIT_FK)
    deck_sheet.col("muc_tieu_goc_giu", meaning="mục tiêu gốc giữ hay không (Tools/campaign/p31_objectives_baseline.json, 12/Lich_su_do)")
    allies = book.sheet("Bo_bai_game_dong_minh", "Bộ bài game: đồng minh đặt sẵn", "fixedDeck.placedAllies", parent=deck_sheet)
    allies.col("def", fk=C.UNIT_FK)

    main_speaker = {}
    for sid, s in scripts:
        for mid, rec in (s.get("missions") or {}).items():
            main_speaker[mid] = (sid, rec)
    line_count = {}
    for _sid, s in scripts:
        for ln in s.get("lines") or []:
            line_count[ln.get("mission")] = line_count.get(ln.get("mission"), 0) + 1

    for i, m in enumerate(camp.get("missions") or []):
        path = ("missions", i)
        r = nv.row(m["id"], C.nguon(CAMP, path), raw=m)
        r.flatten(m, CAMP, path, skip=("fixedDeck",), children={
            "units": C.child(quan), "radio": C.child(radio), "hunt": C.child(san),
            "tips": C.child(tips), "ally.units": C.child(ally_u), "ally.structures": C.child(ally_s),
            "ally.reinforcements": C.child(ally_r), "missionEvents": events_cb(ev),
            "stages": lambda row, items, src, p: child_rows(gd, row, items, src, p, children=stage_children),
            "navStates": lambda row, items, src, p: child_rows(ns, row, items, src, p, children=nav_children),
        })
        r.set("bo_bai_game", "fixedDeck" in m)
        r.set("so_cau_thoai", line_count.get(m["id"], 0))
        r.set("trang_thai_kich_ban", NEED_CODE_CHECK)
        if m["id"] in main_speaker:
            ssid, rec = main_speaker[m["id"]]
            for k, v in rec.items():
                col = "nguoi_noi_chinh" if k == "main" else f"kich_ban_{k}"
                r.set(col, v, ssid, ("missions", m["id"], k))
        fd = m.get("fixedDeck")
        if isinstance(fd, dict):
            dr = deck_sheet.row(m["id"], C.nguon(CAMP, path + ("fixedDeck",)), raw=fd)
            dr.set("nhiem_vu_id", m["id"])
            dr.set("muc_tieu_goc_giu", NEED_CODE_CHECK)
            dr.flatten(fd, CAMP, path + ("fixedDeck",), children={"placedAllies": C.child(allies)})
    for mid, (ssid, rec) in main_speaker.items():
        if mid not in nv.rows:
            r = nv.row(mid, ssid)
            for k, v in rec.items():
                r.set("nguoi_noi_chinh" if k == "main" else f"kich_ban_{k}", v, ssid, ("missions", mid, k))

    # ------------------------------------------------------------------ Thoai (every line one row)
    th = book.sheet("Thoai", "Thoại", "script/chNN.json lines: mọi câu thoại một dòng (nhiệm vụ, thứ tự, trigger, điều kiện, "
                    "người nói, ưu tiên, một lần / lặp, văn bản Việt / Anh, số ký tự)")
    th.col("nhiem_vu_id", meaning="nhiệm vụ", fk=MISSION_FK)
    th.col("thu_tu", meaning="thứ tự câu trong file thoại (0 = đầu)")
    th.col("trigger", meaning="trigger", fk=["07_chien_dich_cot_truyen/Trigger_thoai"])
    th.col("nguoi_noi", meaning="người nói", fk=SPEAKER_FK)
    th.col("khoa_loc", meaning="khóa câu (key)")
    th.col("uu_tien", meaning="ưu tiên P1-P4 (priority)")
    th.col("mot_lan_hay_lap", meaning="true = một lần (once)")
    th.col("dieu_kien_arg", meaning="tham số trigger (arg: cứ điểm, mục tiêu)")
    th.col("dieu_kien_at_s", unit="s", meaning="thời điểm (at)")
    th.col("van_ban_vi", meaning="văn bản tiếng Việt")
    th.col("van_ban_en", meaning="văn bản tiếng Anh")
    th.col("so_ky_tu_vi", meaning="số ký tự tiếng Việt")
    th.col("so_ky_tu_en", meaning="số ký tự tiếng Anh")
    th.col("so_dong_hien_thi_toi_da", meaning="số dòng hiển thị tối đa (đo trên giao diện)")
    th.col("chan_dung", meaning="chân dung người nói (UI Narrative)")
    th.col("tep", meaning="file thoại")
    aliases = {"mission": "nhiem_vu_id", "trigger": "trigger", "speaker": "nguoi_noi", "key": "khoa_loc",
               "priority": "uu_tien", "once": "mot_lan_hay_lap", "arg": "dieu_kien_arg", "at": "dieu_kien_at_s",
               "vi": "van_ban_vi", "en": "van_ban_en"}
    triggers_used: dict[str, int] = {}
    for sid, s in scripts:
        for j, ln in enumerate(s.get("lines") or []):
            rid = ln.get("key") or f"{sid.rsplit('/', 1)[-1]}:{j}"
            r = th.row(rid, C.nguon(sid, ("lines", j)), raw=ln)
            r.set("thu_tu", j)
            r.set("tep", sid.rsplit("/", 1)[-1])
            r.flatten(ln, sid, ("lines", j), aliases=aliases)
            r.set("so_ky_tu_vi", len(ln.get("vi") or ""))
            r.set("so_ky_tu_en", len(ln.get("en") or ""))
            r.set("so_dong_hien_thi_toi_da", NEED_CODE_CHECK)
            r.set("chan_dung", NEED_CODE_CHECK)
            t = ln.get("trigger")
            if t:
                triggers_used[t] = triggers_used.get(t, 0) + 1
        rest = {k: v for k, v in s.items() if k not in ("lines", "missions", "chapter")}
        if rest:
            kv = book.sheets.get("Thoai_tep_khac") or book.kv_sheet("Thoai_tep_khac", "Thoại: khóa khác của file", "khóa ngoài lines")
            book.kv_rows(kv, rest, sid, (), sid.rsplit("/", 1)[-1], prefix=(sid.rsplit("/", 1)[-1],))

    # ------------------------------------------------------------------ Nhan_vat, Trigger_thoai
    sp = ctx.data(SPEAKERS) if SPEAKERS in ctx.sources else {}
    nh = book.sheet("Nhan_vat", "Nhân vật", "script/speakers.json: tên, vai (roles), trigger được phép, ghi chú")
    nh.col("triggers", meaning="trigger được phép (ngăn ';')", fk=["07_chien_dich_cot_truyen/Trigger_thoai"])
    nh.col("chan_dung", meaning="chân dung (UI Narrative)")
    for r, _x, _p in C.keyed(nh, sp.get("speakers"), SPEAKERS, ("speakers",)):
        r.set("chan_dung", NEED_CODE_CHECK)
    tr = book.sheet("Trigger_thoai", "Trigger thoại", "speakers.json mainTriggers / scriptedTriggers và mọi trigger câu thoại dùng; "
                    "ưu tiên, hồi chiêu, số lần: luật trong mã (Dialogue.cs)")
    tr.col("loai", meaning="main / scripted / chi_dung (chỉ thấy trong câu thoại) / nhan_vat (chỉ trong triggers của nhân vật)")
    tr.col("so_cau", meaning="số câu thoại dùng trigger")
    tr.col("hoi_chieu_so_lan", meaning="hồi chiêu và số lần (mã)")
    names = {}
    for key, kind in (("mainTriggers", "main"), ("scriptedTriggers", "scripted")):
        for j, t in enumerate(sp.get(key) or []):
            names.setdefault(t, (kind, key, j))
    allowed = {t for rec in (sp.get("speakers") or {}).values() if isinstance(rec, dict) for t in rec.get("triggers") or []}
    for t in sorted(set(names) | set(triggers_used) | allowed):
        kind, key, j = names.get(t, ("chi_dung" if t in triggers_used else "nhan_vat", None, None))
        r = tr.row(t, C.nguon(SPEAKERS, (key, j)) if key else "script/chNN.json lines[].trigger")
        r.set("loai", kind)
        if key:
            r.mark(SPEAKERS, (key, j), "id")
        r.set("so_cau", triggers_used.get(t, 0))
        r.set("hoi_chieu_so_lan", NEED_CODE_CHECK)
    for key in ("mainTriggers", "scriptedTriggers"):
        for j, t in enumerate(sp.get(key) or []):
            if names.get(t, (None, key, j))[1:] != (key, j):  # a trigger listed twice: its second place
                tr.rows[t].mark(SPEAKERS, (key, j), "loai")
    rest = {k: v for k, v in sp.items() if k not in ("speakers", "mainTriggers", "scriptedTriggers")}
    if rest:
        kv = book.kv_sheet("Nhan_vat_khac", "Nhân vật: khóa khác", "speakers.json: khóa ngoài speakers / triggers")
        book.kv_rows(kv, rest, SPEAKERS, (), "speakers.json")

    # ------------------------------------------------------------------ Bien_co (+ rules)
    lib = camp.get("eventLibrary") or {}
    bc = book.sheet("Bien_co", "Biến cố", "campaign.json eventLibrary.events: cơ chế (kind), báo trước, câu radio, thông báo, "
                    "tham số, trigger, thưởng")
    bc.col("nhiem_vu_dung", meaning="nhiệm vụ dùng (missionEvents, ngăn ';')", fk=MISSION_FK)
    used: dict[str, list] = {}
    for m in camp.get("missions") or []:
        evs = list(m.get("missionEvents") or [])
        for stg in m.get("stages") or []:
            evs += list(stg.get("missionEvents") or [])
        for e in evs:
            eid = e if isinstance(e, str) else (e.get("id") if isinstance(e, dict) else None)
            if eid and m["id"] not in used.setdefault(eid, []):
                used[eid].append(m["id"])
    for r, item, _p in C.records(bc, lib.get("events"), CAMP, ("eventLibrary", "events")):
        r.set("nhiem_vu_dung", ";".join(used.get(r.id, [])))
    bl = book.kv_sheet("Bien_co_luat", "Biến cố: luật chung", "eventLibrary.rules (trừ difficulty: 05/Do_kho; weatherSight: 08/Thoi_tiet)")
    book.kv_rows(bl, {k: v for k, v in (lib.get("rules") or {}).items() if k not in ("difficulty", "weatherSight")}, CAMP,
                 ("eventLibrary", "rules"), "eventLibrary.rules")
    rest = {k: v for k, v in lib.items() if k not in ("events", "rules")}
    if rest:
        book.kv_rows(bl, rest, CAMP, ("eventLibrary",), "eventLibrary", prefix=("eventLibrary",))
    other = {k: v for k, v in camp.items()
             if k not in ("chapters", "missions", "eventLibrary", "generals", "economy") and not k.startswith("migration")}
    if other:
        kv = book.kv_sheet("Chien_dich_khac", "Chiến dịch: khóa khác", "campaign.json: khóa chưa có sheet riêng")
        book.kv_rows(kv, other, CAMP, (), "campaign")

    # ------------------------------------------------------------------ Phat_hanh (release.json)
    if RELEASE in ctx.sources:
        ph = book.kv_sheet("Phat_hanh", "Phát hành", "release.json: hồi phát hành, chương tắt, cách hiện chương tắt")
        book.kv_rows(ph, ctx.data(RELEASE), RELEASE, (), "release")

    # ------------------------------------------------------------------ Kich_ban_goc (Tools/story/script/*.txt)
    kb = book.sheet("Kich_ban_goc", "Kịch bản gốc", "Tools/story/script/chNN.txt: mọi dòng không trống (công cụ dựng ra "
                    "script/chNN.json); dòng '#' là ghi chú, '@' mở nhiệm vụ, còn lại 'trigger | người nói | ưu tiên | vi || en'")
    kb.col("tep", meaning="file kịch bản")
    kb.col("dong_so", meaning="số dòng trong file (1 = đầu)")
    kb.col("loai", meaning="ghi_chu / nhiem_vu / cau", enum=["ghi_chu", "nhiem_vu", "cau"])
    kb.col("noi_dung", meaning="nguyên văn dòng")
    for sid in sorted(s for s in ctx.sources if s.startswith(STORY_TXT) and s.endswith(".txt")):
        stem = sid.rsplit("/", 1)[-1][:-4]
        for j, line in enumerate(ctx.data(sid)):
            if not line.strip():
                continue
            r = kb.row(f"{stem}:{j + 1:04d}", C.nguon(sid, ("lines", j)))
            r.set("tep", stem)
            r.set("dong_so", j + 1)
            s = line.strip()
            r.set("loai", "ghi_chu" if s.startswith("#") else "nhiem_vu" if s.startswith("@") else "cau")
            r.set("noi_dung", line, sid, ("lines", j))

    # ------------------------------------------------------------------ code-only sheets
    C.marker_sheet(book, "Ket_tran", "Kết trận", "Chuỗi kết trận: bước, thời lượng, áp dụng (prompt 30; mã MatchRunner.Ending.cs)",
                   chua_ap("xuat_luot5"), "đọc hằng trong Assets/MachineBrigade/Scripts/Game/Match/MatchRunner.Ending.cs",
                   "Assets/MachineBrigade/Scripts/Game/Match/MatchRunner.Ending.cs")
    C.marker_sheet(book, "Cutscene_khoanh_khac", "Khoảnh khắc chậm", "6 khoảnh khắc chậm x0,5 (mã Cinematics.cs)",
                   chua_ap("xuat_luot5"), "đọc hằng và điều kiện trong Assets/MachineBrigade/Scripts/Game/Match/Cinematics.cs",
                   "Assets/MachineBrigade/Scripts/Game/Match/Cinematics.cs")

    # ------------------------------------------------------------------ layer B (lane B, pass 5 part 2)
    _b07.build(ctx, book, camp)
