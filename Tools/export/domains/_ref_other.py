"""Pass 10 for files 05-11 (spec 12.2): modes, AI, campaign and dialogue, maps, effects and sound, models, meta.

Repo sources only: the AI research workbook (tactics, roles: doctrine and game columns), DECISIONS phrases (Conquest's bleed
"Company of Heroes style"), the audio credits 09/Am_thanh already holds, reference_real.json and the Blender notes for the
models. Everything else is NEED_SOURCE for the owner to fill. These files have no real-world number to compare, so their
<name>_so_sanh_that is one KHONG_CO row (file 10: the model sizes are compared in 02 / 03 / 04 against the data's modelSize).
"""
from __future__ import annotations

import collections
import re

from core.formula import F
from core.model import NEED_SOURCE

from . import _ref_common as C
from . import _refsrc as S
from ._ref_units import name_of, num

NS = NEED_SOURCE


def _row(sh, rid, ent, nguon_text, loai, missing_col, vals, why=""):
    vals = dict(vals)
    vals.setdefault("loai_tham_chieu", loai)
    if loai == NS:
        vals.setdefault("do_tin_cay", NS)
        vals.setdefault("ly_do", why or "repo không có tham chiếu cho mục này")
        if missing_col:
            vals[missing_col] = NS
    return C.put_row(sh, rid, ent, nguon_text, vals)


def _other_txt(other) -> str:
    return (" (tham khảo khác: " + "; ".join(a + (f" ({b})" if b else "") for a, b in other) + ")") if other else ""


def _ai_sources(reg):
    """The 'Nguồn' sheet of the AI research workbook: each a Nguon row with its URL. {keyword: nguon id}."""
    out = {}
    for r in S.xlsx_rows(S.AI_RESEARCH, "Nguồn"):
        title, url = S.text(r.get("Nguồn")), S.text(r.get("Link"))
        if not title:
            continue
        loai = ("wikipedia" if "wikipedia.org" in url else "wiki_game" if ("wiki" in url) else
                "nha_phat_hanh_game" if url else "tai_lieu_repo")
        nid = reg.add(loai, title, url=url, trich_tu=S.AI_RESEARCH, ghi_chu=S.text(r.get("Ý chính"))[:300])
        key = title.split("·")[0].strip()
        out[key] = nid
    return out


def _match_sources(text: str, ai_src: dict) -> list[str]:
    t = (text or "").lower()
    hits = [nid for key, nid in ai_src.items() if key.lower() in t]
    if ("yểm hộ luân phiên" in t or "bounding" in t) and "Bounding overwatch" in ai_src:
        hits.append(ai_src["Bounding overwatch"])
    return list(dict.fromkeys(hits))


def build_05_11(R, out: dict):
    ctx, reg, books = R.ctx, R.reg, R.ctx.books
    N_AI = reg.repo(S.AI_RESEARCH, "Nghiên cứu AI (Machine_Brigade_AI_Research.xlsx)")
    ai_src = _ai_sources(reg)
    R.ai_src = ai_src

    # ------------------------------------------------------------------ 05 modes
    b = books["05_che_do_kinh_te"]
    sh = C.ref_sheet(b, "Che_do_tham_chieu", "Chế độ: tham chiếu game", "Mỗi chế độ một dòng: game tham khảo, cơ chế giữ / đổi",
                     ["05_che_do_kinh_te/Che_do"], [("co_che_giu_nguyen", "", "cơ chế giữ như game gốc"),
                                                    ("co_che_doi", "", "cơ chế đổi so với game gốc")])
    bleed = S.decisions_find(R.dec, "(`Bleed`, Company of Heroes style)")
    for e, r in sorted(b.sheets["Che_do"].rows.items(), key=lambda x: str(x[0])):
        disp = r.values.get("ten_che_do") or str(e)
        if e == "conquest" and bleed:
            _row(sh, e, e, f"{S.DECISIONS}: {bleed[1]}", "game", None, {
                "ten_hien_thi": disp, "ten_game": "Company of Heroes", "co_che_game": "Bleed: bên giữ ít cứ điểm hơn bị trừ dần",
                "co_che_giu_nguyen": "trừ dần bên giữ ít cứ điểm hơn", "co_che_doi": NS, "do_tin_cay": "ban_dau_doan",
                "nguon_id": R.N_DEC, "diem_giong": f"DECISIONS mục '{bleed[1]}': Conquest đã trừ dần bên giữ ít điểm hơn"})
        else:
            _row(sh, e, e, "spec 12.2 (05)", NS, "ten_game", {"ten_hien_thi": disp, "co_che_giu_nguyen": "", "co_che_doi": ""})
    out["05"] = (sh, C.marker_compare(b, "Che_do_so_sanh_that", "Chế độ: so sánh với thật",
                                      "chế độ chơi không có thông số ngoài đời để đối chiếu"))

    # ------------------------------------------------------------------ 06 AI
    b = books["06_ai"]
    sh = C.ref_sheet(b, "AI_tham_chieu", "AI: học thuyết và game tham khảo", "Chiến thuật, vai trò AI, tướng địch: học thuyết "
                     "quân sự (nghiên cứu AI), game AI tham khảo, kiểu chỉ huy",
                     ["06_ai/Chien_thuat", "06_ai/AI_vai_tro", "06_ai/AI_tuong"],
                     [("hoc_thuyet_quan_su", "", "học thuyết quân sự (cột 'Ngoài đời' / 'Học thuyết ngoài đời' của nghiên cứu AI)"),
                      ("kieu_chi_huy", "", "kiểu chỉ huy lấy ý (tướng địch)")])
    tactics = {S.text(r.get("Chiến thuật")).lower(): r for r in S.xlsx_rows(S.AI_RESEARCH, "Chiến thuật")}
    roles = {S.text(r.get("Mã")): r for r in S.xlsx_rows(S.AI_RESEARCH, "Vai trò")}
    R.doctrine = []
    for e, r in sorted(b.sheets["Chien_thuat"].rows.items(), key=lambda x: str(x[0])):
        disp = r.values.get("name") or str(e)
        src = tactics.get(str(disp).strip().lower())
        rid = f"chien_thuat/{e}"
        if src is None:
            _row(sh, rid, e, "spec 12.2 (06)", NS, "hoc_thuyet_quan_su", {"ten_hien_thi": disp})
            continue
        doc, game = S.text(src.get("Ngoài đời")), S.text(src.get("Tham khảo game"))
        items, other = S.games_only(S.split_items(game))
        ids = [N_AI] + _match_sources(doc + " " + game + " " + disp, ai_src)
        _row(sh, rid, e, f"{S.AI_RESEARCH}: Chiến thuật '{disp}'", "hoc_thuyet_quan_su" if doc else ("game" if items else NS),
             "hoc_thuyet_quan_su", {
                 "ten_hien_thi": disp, "hoc_thuyet_quan_su": doc or NS, "ten_game": C.join(g for g, _m in items),
                 "co_che_game": C.join(m or "chọn chiến thuật" for _g, m in items), "diem_giong": S.text(src.get("Hành vi cốt lõi")) + _other_txt(other),
                 "diem_khac_co_chu_dich": S.text(src.get("Tác động lên AI"))[:300],
                 "do_tin_cay": "da_kiem_chung" if len(ids) > 1 else "ban_dau_doan", "nguon_id": C.join(ids)})
        if doc:
            R.doctrine.append((doc, S.text(src.get("Hành vi cốt lõi")), f"06_ai/Chien_thuat/{e}", ids))
    for e, r in sorted(b.sheets["AI_vai_tro"].rows.items(), key=lambda x: str(x[0])):
        src = roles.get(str(e))
        rid = f"vai_tro/{e}"
        if src is None:
            _row(sh, rid, e, "spec 12.2 (06)", NS, "hoc_thuyet_quan_su", {"ten_hien_thi": str(e)})
            continue
        doc, game = S.text(src.get("Học thuyết ngoài đời")), S.text(src.get("Tham khảo game"))
        items, other = S.games_only(S.split_items(game))
        ids = [N_AI] + _match_sources(doc + " " + game, ai_src)
        disp = S.text(src.get("Vai trò")) or str(e)
        _row(sh, rid, e, f"{S.AI_RESEARCH}: Vai trò {e}", "hoc_thuyet_quan_su" if doc else ("game" if items else NS),
             "hoc_thuyet_quan_su", {
                 "ten_hien_thi": disp, "hoc_thuyet_quan_su": doc[:500] or NS, "ten_game": C.join(g for g, _m in items),
                 "co_che_game": C.join(m or "hành vi vai trò" for _g, m in items),
                 "diem_giong": S.text(src.get("Hành vi đặc biệt"))[:300] + _other_txt(other),
                 "do_tin_cay": "da_kiem_chung" if len(ids) > 1 else "ban_dau_doan", "nguon_id": C.join(ids)})
        if doc:
            R.doctrine.append((f"Vai trò {disp}", doc, f"06_ai/AI_vai_tro/{e}", ids))
    for e, r in sorted(b.sheets["AI_tuong"].rows.items(), key=lambda x: str(x[0])):
        _row(sh, f"tuong/{e}", e, "spec 12.2 (06): tướng địch", NS, "kieu_chi_huy",
             {"ten_hien_thi": str(e), "hoc_thuyet_quan_su": ""})
    out["06"] = (sh, C.marker_compare(b, "AI_so_sanh_that", "AI: so sánh với thật",
                                      "AI không có thông số ngoài đời để đối chiếu (học thuyết là văn bản)"))

    # ------------------------------------------------------------------ 07 campaign, dialogue
    b = books["07_chien_dich_cot_truyen"]
    sh = C.ref_sheet(b, "Chien_dich_tham_chieu", "Chiến dịch: tham chiếu lịch sử / phim / game", "Mỗi chương, nhiệm vụ, màn bộ "
                     "bài game một dòng: tham chiếu lịch sử hoặc phim / game, mã màn",
                     ["07_chien_dich_cot_truyen/Chuong", "07_chien_dich_cot_truyen/Nhiem_vu",
                      "07_chien_dich_cot_truyen/Bo_bai_game"], [("ma_man", "", "mã màn / nhiệm vụ")])
    for sname, pre in (("Chuong", "chuong"), ("Nhiem_vu", "nhiem_vu"), ("Bo_bai_game", "bo_bai")):
        for e, r in sorted(b.sheets[sname].rows.items(), key=lambda x: str(x[0])):
            _row(sh, f"{pre}/{e}", e, f"spec 12.2 (07): {sname}", NS, "ten_game",
                 {"ten_hien_thi": name_of(r), "ma_man": str(r.values.get("nhiem_vu_id") or e)},
                 "repo không ghi tham chiếu lịch sử / phim / game cho mục này")
    tv = C.ref_sheet(b, "Thoai_tham_chieu", "Thoại: nhân vật và giọng lấy ý", "Mỗi nhân vật một dòng: nhân vật / giọng lấy "
                     "ý (chỉ mức ý tưởng)", ["07_chien_dich_cot_truyen/Nhan_vat"], [("giong_lay_y", "", "giọng / tính cách lấy ý")])
    for e, r in sorted(b.sheets["Nhan_vat"].rows.items(), key=lambda x: str(x[0])):
        _row(tv, e, e, "spec 12.2 (07 Thoại)", NS, "giong_lay_y", {"ten_hien_thi": name_of(r)},
             "repo không ghi nhân vật / giọng lấy ý")
    out["07"] = (sh, C.marker_compare(b, "Chien_dich_so_sanh_that", "Chiến dịch: so sánh với thật",
                                      "chiến dịch và thoại không có thông số ngoài đời để đối chiếu"), tv)

    # ------------------------------------------------------------------ 08 maps
    b = books["08_ban_do"]
    sh = C.ref_sheet(b, "Ban_do_tham_chieu", "Bản đồ: khu vực và game tham khảo", "Mỗi biome và bản đồ gốc một dòng: khu vực "
                     "địa lý / biome thật lấy ý, địa danh, game tham khảo cơ chế bản đồ",
                     ["08_ban_do/Ban_do_biome", "08_ban_do/Ban_do"],
                     [("ban_do_goc", "", "bản đồ gốc (các biến thể chế độ dùng chung)"),
                      ("khu_vuc_dia_ly_that", "", "khu vực địa lý / biome thật lấy ý"),
                      ("dia_danh_that", "", "địa danh, đường ray, cảng thật lấy ý")])
    for e, r in sorted(b.sheets["Ban_do_biome"].rows.items(), key=lambda x: str(x[0])):
        _row(sh, f"biome/{e}", e, "spec 12.2 (08): biome", NS, "khu_vuc_dia_ly_that", {"ten_hien_thi": str(e), "dia_danh_that": ""})
    bases = collections.defaultdict(list)
    for e, r in b.sheets["Ban_do"].rows.items():
        bases[str(r.values.get("ban_do_goc") or e)].append(str(e))
    for base in sorted(bases):
        ex = sorted(bases[base])[0]
        _row(sh, f"ban_do/{base}", ex, "spec 12.2 (08): bản đồ gốc", NS, "khu_vuc_dia_ly_that",
             {"ten_hien_thi": base, "ban_do_goc": base, "dia_danh_that": NS})
    out["08"] = (sh, C.marker_compare(b, "Ban_do_so_sanh_that", "Bản đồ: so sánh với thật",
                                      "bản đồ không có thông số ngoài đời để đối chiếu"))

    # ------------------------------------------------------------------ 09 effects, sound
    b = books["09_hieu_ung_am_thanh"]
    sh = C.ref_sheet(b, "Hieu_ung_tham_chieu", "Hiệu ứng và âm thanh: nguồn và tham chiếu", "Mỗi bậc VFX và mỗi nhóm âm thanh "
                     "(nhóm × bậc cỡ) một dòng: nguồn ghi âm / tổng hợp, giấy phép, đặc điểm tiếng thật, game tham chiếu cảm giác",
                     ["09_hieu_ung_am_thanh/VFX_bac", "09_hieu_ung_am_thanh/Am_thanh"],
                     [("clip_ids", "", "các clip của nhóm (09/Am_thanh)"),
                      ("nguon_am_thanh", "", "nguồn: gói ghi âm / tổng hợp bằng script (09/Am_thanh.nguon_goc)"),
                      ("giay_phep", "", "giấy phép (09/Am_thanh.giay_phep)"),
                      ("dac_diem_tieng_that", "", "đặc điểm tiếng thật theo bậc cỡ")])
    sh.cols["clip_ids"].fk = ["09_hieu_ung_am_thanh/Am_thanh"]
    for e in sorted(b.sheets["VFX_bac"].rows, key=str):
        _row(sh, f"vfx/{e}", e, "spec 12.2 (09): VFX theo bậc", NS, "ten_mau_that",
             {"ten_hien_thi": f"VFX bậc {e}", "dac_diem_tieng_that": ""}, "repo không ghi nguồn hình ảnh / video thật cho bậc này")
    N_CRED = reg.repo("Assets/MachineBrigade/Resources/Audio/CREDITS.md", "Audio/CREDITS.md (nguồn và giấy phép âm thanh)")
    N_LIC = reg.repo(S.LICENSES, "ASSET_LICENSES.md (giấy phép tài sản)")
    groups = collections.defaultdict(list)
    for e, r in b.sheets["Am_thanh"].rows.items():
        groups[(str(r.values.get("nhom") or "khac"), str(r.values.get("bac_co") or "-"))].append((str(e), r))
    for (grp, tier), items in sorted(groups.items()):
        items.sort()
        packs, lic, ids = [], [], [N_CRED, N_LIC]
        for _e, r in items:
            ng = str(r.values.get("nguon_goc") or "")
            m = re.match(r'^(.*?):\s*"', ng)
            if m:
                ids.append(reg.add("thu_vien_am_thanh", m.group(1).strip(), trich_tu="09_hieu_ung_am_thanh/Am_thanh"))
                packs.append(m.group(1).strip())
            elif ng:
                packs.append(ng)
            if r.values.get("giay_phep"):
                lic.append(str(r.values["giay_phep"]))
        _row(sh, f"am_thanh/{grp}/{tier}", items[0][0], "09_hieu_ung_am_thanh/Am_thanh (nguon_goc, giay_phep)", NS,
             "dac_diem_tieng_that", {"ten_hien_thi": f"âm thanh {grp} {tier}", "clip_ids": ";".join(e for e, _r in items),
                                     "nguon_am_thanh": C.join(sorted(set(packs)))[:1000], "giay_phep": C.join(sorted(set(lic))),
                                     "nguon_id": C.join(ids)},
             "nguồn ghi âm / tổng hợp đã có; đặc điểm tiếng thật của hệ thống tương ứng chưa có nguồn")
    out["09"] = (sh, C.marker_compare(b, "Hieu_ung_so_sanh_that", "Hiệu ứng: so sánh với thật",
                                      "chưa có số đo tiếng / hình thật để đối chiếu (đặc điểm tiếng thật: NEED_SOURCE)"))

    # ------------------------------------------------------------------ 10 models
    b = books["10_model_tai_san"]
    sh = C.ref_sheet(b, "Model_tham_chieu", "Model: tài liệu tham chiếu hình dạng và kích thước", "Mỗi model có mẫu thật một "
                     "dòng: tài liệu hình dạng / kích thước (chỉ nguồn và URL, không nhúng ảnh), kích thước thật (tra sống "
                     "Kich_thuoc_that), ghi chú script Blender và spec prompt 35",
                     ["10_model_tai_san/Kich_thuoc_that", "10_model_tai_san/Model"],
                     [("tai_lieu_hinh_dang", "", "tài liệu hình dạng / kích thước như nguồn repo ghi"),
                      ("url_tham_khao", "", "URL ảnh / bản vẽ tham khảo (chỉ URL, không lưu ảnh)"),
                      ("ngoai_doi_dai_m", "m", "dài thật (tra sống Kich_thuoc_that)"),
                      ("ngoai_doi_rong_m", "m", "rộng thật"), ("ngoai_doi_cao_m", "m", "cao thật"),
                      ("ghi_chu_dung_model", "", "docstring script Blender / spec prompt 35")])
    for col in ("ngoai_doi_dai_m", "ngoai_doi_rong_m", "ngoai_doi_cao_m"):
        sh.col(col, formula="INDEX/MATCH Kich_thuoc_that", source_note="python: tra sống Kich_thuoc_that")
    kt, mdl = b.sheets.get("Kich_thuoc_that"), b.sheets.get("Model")
    ids = sorted(set(kt.rows if kt else []) | {i for i in R.builders if mdl and i in mdl.rows}
                 | {i for i in R.specs if mdl and i in mdl.rows}, key=str)
    for e in ids:
        v = kt.rows[e].values if kt and e in kt.rows else {}
        conf = v.get("conf", "")
        nguon = [R.N_SIZES] if v else []
        tins = []
        if v:
            cited, external = reg.cite(str(v.get("source", "")), S.REAL_SIZES)
            nguon += cited
            tins = ["da_kiem_chung"] if conf == "high" and external else ["uoc_dinh"] if conf == "approx" else []
        ref_name = str(v.get("ref", "") or "")
        loai = "gia_tuong" if conf == "inspiration" else ("doi_that" if ref_name else NS)
        notes = [f"{x['file']}: {x['text']}" for x in R.builders.get(e, [])]
        for x in R.builders.get(e, []):
            nguon.append(reg.repo(x["file"], f"script Blender {x['file'].rsplit('/', 1)[-1]} (docstring)"))
        real_names = []
        if e in R.specs:
            sid, d = R.specs[e]
            real_names = [str(x) for x in d.get("real", [])]
            notes.append(f"{sid}: confidence = {d.get('confidence', '')}")
            nguon.append(reg.repo(sid, f"spec dựng lại {e} (prompt 35)"))
            if loai == NS and real_names:
                loai = "doi_that"
        vals = {"ten_hien_thi": e, "ten_mau_that": v.get("ref", "") or C.join(real_names),
                "tai_lieu_hinh_dang": str(v.get("source", "")), "url_tham_khao": C.real_blank(loai),
                "ghi_chu_dung_model": " || ".join(notes)[:1500], "nguon_id": C.join(nguon)}
        for col, src in (("ngoai_doi_dai_m", "size_dai_m"), ("ngoai_doi_rong_m", "size_rong_m"), ("ngoai_doi_cao_m", "size_cao_m")):
            x = num(v.get(src)) if v else None
            vals[col] = F(C.look("Kich_thuoc_that", src), expect=x, ref="python: Kich_thuoc_that") if x is not None \
                else C.real_blank(loai)
        if loai == "gia_tuong":
            vals["ly_do"] = f"reference_real.json: {v.get('source', '')} (thiết kế giả tưởng trên mẫu '{v.get('ref', '')}')"
            vals["ly_do_khac"] = "gia_tuong"
        vals["do_tin_cay"] = C.reliability(loai, False, tins)
        _row(sh, e, e, f"{S.REAL_SIZES}: units.{e}", loai, "ten_mau_that" if loai == NS else None, vals,
             "chưa có mẫu thật trong reference_real.json / spec")
    out["10"] = (sh, C.marker_compare(b, "Model_so_sanh_that", "Model: so sánh với thật",
                                      "kích thước model so với mẫu thật nằm ở 02/Phuong_tien_so_sanh_that, 03/Boss_so_sanh_that, "
                                      "04/Can_cu_so_sanh_that (modelSize của dữ liệu; tỷ lệ hình W/L, H/L theo MODEL_STANDARD 3.1)"))

    # ------------------------------------------------------------------ 11 meta
    b = books["11_meta_giao_dien"]
    sh = C.ref_sheet(b, "Meta_tham_chieu", "Meta: game tham khảo cơ chế", "Mỗi cơ chế ngoài trận một dòng (theo sheet): game "
                     "tham khảo (nâng hạng, hòm đồ, nhiệm vụ ngày...)", [], [("sheet_lien_quan", "", "sheet của file 11")])
    for s in ("Nang_hang", "Hom_do", "Trang_bi_hang", "Cua_hang", "Nhiem_vu_ngay", "Skin", "Mo_khoa", "Thanh_tuu", "Mutator_tuan",
              "Thu_hang", "Thuong", "Huong_dan", "Cai_dat_mac_dinh"):
        if s in b.sheets:
            _row(sh, s, s, f"spec 12.2 (11): {s}", NS, "ten_game", {"ten_hien_thi": b.sheets[s].title_vi, "sheet_lien_quan": s},
                 "repo không ghi game tham khảo cho cơ chế này")
    out["11"] = (sh, C.marker_compare(b, "Meta_so_sanh_that", "Meta: so sánh với thật",
                                      "meta không có thông số ngoài đời để đối chiếu"))
    return out
