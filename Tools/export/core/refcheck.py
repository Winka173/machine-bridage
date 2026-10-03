"""Pass 10 (spec 12.6): the reference layer's checks and reliability shares, for COVERAGE.md and SELF_CHECK.md.

Input: {file: {sheet: (header, rows)}} (the csv read back, or the books' tables); values compared as text.
"""
from __future__ import annotations

import collections

NS = "NEED_SOURCE"
REF_FILE = "13_tham_chieu_nguon"
TIN = ["da_kiem_chung", "uoc_dinh", "ban_dau_doan", NS]
ENTITIES = [("xe", "02_phuong_tien", "Xe"), ("vũ khí", "01_vu_khi_dan", "Vu_khi"), ("tháp", "04_can_cu_thap", "Thap"),
            ("boss", "03_boss", "Boss"), ("nhà chính", "04_can_cu_thap", "Nha_chinh"), ("tường", "04_can_cu_thap", "Tuong")]
REAL_COLS = ("quoc_gia", "nam_dua_vao_su_dung")


def _s(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _dicts(books, fid, sheet):
    h, rows = books.get(fid, {}).get(sheet, ([], []))
    return [{k: _s(v) for k, v in zip(h, r)} for r in rows]


def ref_sheets(books):
    return [(fid, s) for fid in sorted(books) for s in sorted(books[fid])
            if s.endswith("_tham_chieu") and "loai_tham_chieu" in books[fid][s][0]]


def cmp_sheets(books):
    return [(fid, s) for fid in sorted(books) for s in sorted(books[fid]) if s.endswith("_so_sanh_that")]


def run(books) -> dict:
    out = {"gaps": [], "lines": []}
    if REF_FILE not in books:
        out["status"] = "CHUA_AP"
        out["lines"] = ["File 13_tham_chieu_nguon chưa xuất (lượt 10).", ""]
        return out
    refs = {(f, s): _dicts(books, f, s) for f, s in ref_sheets(books)}
    L = out["lines"]
    # 1. coverage of the entities
    L += ["**1. Phủ thực thể** (mỗi xe, vũ khí, tháp, boss, nhà chính, tường có dòng tham chiếu; gia_tuong phải có ly_do):", "",
          "| loại | số thực thể | có dòng | có tham chiếu | NEED_SOURCE | gia_tuong | gia_tuong thiếu ly_do |", "|---|---:|---:|---:|---:|---:|---:|"]
    for label, fid, sheet in ENTITIES:
        ids = {r.get("id", "") for r in _dicts(books, fid, sheet)}
        rows = [r for (f, _s2), rs in refs.items() if f == fid for r in rs if r.get("entity_id") in ids]
        have = {r["entity_id"] for r in rows}
        known = {r["entity_id"] for r in rows if r.get("loai_tham_chieu") not in ("", NS)}
        ns = {r["entity_id"] for r in rows if r.get("loai_tham_chieu") == NS} - known
        gt = [r for r in rows if r.get("loai_tham_chieu") == "gia_tuong"]
        gt_bad = [r for r in gt if not r.get("ly_do")]
        L.append(f"| {label} | {len(ids)} | {len(have & ids)} | {len(known)} | {len(ns)} | {len(gt)} | {len(gt_bad)} |")
        if ids - have:
            out["gaps"].append(f"{len(ids - have)} {label} không có dòng tham chiếu")
        if gt_bad:
            out["gaps"].append(f"{len(gt_bad)} {label} gia_tuong thiếu ly_do")
    L.append("")
    # 2. nguon_id
    nguon = {r.get("id", ""): r for r in _dicts(books, REF_FILE, "Nguon_tham_chieu")}
    orphans, refs_n = collections.Counter(), 0
    for fid, sheets in books.items():
        for s, (h, rows) in sheets.items():
            if "nguon_id" not in h:
                continue
            i = h.index("nguon_id")
            for r in rows:
                for x in _s(r[i] if i < len(r) else "").split(";"):
                    if x:
                        refs_n += 1
                        if x not in nguon:
                            orphans[f"{fid}/{s}"] += 1
    no_doc = [k for k, r in nguon.items() if not r.get("url") and not r.get("tieu_de")]
    no_url = [k for k, r in nguon.items() if not r.get("url")]
    unused = [k for k, r in nguon.items() if r.get("so_lan_dung") in ("0", "")]
    L += [f"**2. Nguồn:** {len(nguon)} dòng Nguon_tham_chieu; {refs_n} lần trỏ nguon_id; mồ côi (nguon_id không có ở "
          f"Nguon_tham_chieu): {sum(orphans.values())}" + (f" ({dict(orphans)})" if orphans else "") +
          f"; nguồn không có URL lẫn tiêu đề: {len(no_doc)}; có tiêu đề in rõ nhưng không URL (repo không ghi URL): "
          f"{len(no_url)}; nguồn không ai trỏ: {len(unused)}.", ""]
    if orphans:
        out["gaps"].append(f"{sum(orphans.values())} nguon_id mồ côi")
    if no_doc:
        out["gaps"].append(f"{len(no_doc)} nguồn không URL / tiêu đề")
    # 3. real-world columns
    bad = []
    cells = collections.Counter()
    for (fid, s), rows in refs.items():
        for r in rows:
            for c, v in r.items():
                if not (c.startswith("ngoai_doi_") or c in REAL_COLS) or c.startswith("ngoai_doi_nguon") or c == "ngoai_doi_bang_can_bang":
                    continue
                if v == NS:
                    cells["NEED_SOURCE"] += 1
                elif v:
                    cells["có giá trị"] += 1
                    if not r.get("nguon_id"):
                        bad.append(f"{fid}/{s}/{r.get('id')}.{c}")
    L += [f"**3. Cột thông số ngoài đời** (ngoai_doi_*, quoc_gia, nam_dua_vao_su_dung): {cells['có giá trị']} ô có giá trị "
          f"(mỗi ô trên dòng có nguon_id), {cells['NEED_SOURCE']} ô NEED_SOURCE; ô có giá trị mà dòng không có nguon_id: "
          f"{len(bad)}" + (f" ({'; '.join(bad[:10])})" if bad else "") + ".", ""]
    if bad:
        out["gaps"].append(f"{len(bad)} ô thông số ngoài đời không có nguon_id")
    # 4. borrowed mechanics
    mech = _dicts(books, REF_FILE, "Tham_chieu_game_co_che")
    by_game = collections.defaultdict(set)
    for m in mech:
        for sh in m.get("dan_den_sheet", "").split(";"):
            by_game[m.get("ten_game", "").lower()].add(sh.strip())
    missing, n_borrow = [], 0
    for (fid, s), rows in refs.items():
        for r in rows:
            for g in r.get("ten_game", "").split(";"):
                if not g or g == NS:
                    continue
                n_borrow += 1
                if f"{fid}/{s}" not in by_game.get(g.lower(), set()):
                    missing.append(f"{fid}/{s}/{r.get('id')}: {g}")
    L += [f"**4. Cơ chế lấy ý từ game:** {len(mech)} dòng Tham_chieu_game_co_che; {n_borrow} lần một dòng tham chiếu nêu game; "
          f"thiếu dòng cơ chế: {len(missing)}" + (f" ({'; '.join(missing[:10])})" if missing else "") + ".", ""]
    if missing:
        out["gaps"].append(f"{len(missing)} game lấy ý thiếu dòng Tham_chieu_game_co_che")
    # 5. co_lech_lon
    L += ["**5. So sánh game với thật** (co_lech_lon = ngoài khoảng mà không có chủ đích):", "",
          "| sheet | dòng | ngoài khoảng có chủ đích (có ly_do) | co_lech_lon | trong đó có ly_do | có dòng Cho_quyet | không ly_do, không Cho_quyet |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    tot = collections.Counter()
    for fid, s in cmp_sheets(books):
        rows = _dicts(books, fid, s)
        if rows and "co_lech_lon" not in rows[0]:
            continue
        lech = [r for r in rows if r.get("co_lech_lon", "").lower() == "true"]
        chu = [r for r in rows if r.get("co_chu_dich", "").lower() == "true"]
        with_why = [r for r in lech if r.get("ly_do")]
        cq = [r for r in lech if r.get("cho_quyet_id")]
        none = [r for r in lech if not r.get("ly_do") and not r.get("cho_quyet_id")]
        tot.update(rows=len(rows), chu=len(chu), lech=len(lech), why=len(with_why), cq=len(cq), none=len(none))
        L.append(f"| {fid}/{s} | {len(rows)} | {len(chu)} | {len(lech)} | {len(with_why)} | {len(cq)} | {len(none)} |")
    L += [f"| tổng | {tot['rows']} | {tot['chu']} | {tot['lech']} | {tot['why']} | {tot['cq']} | {tot['none']} |", ""]
    out["co_lech_lon"] = dict(tot)
    if tot["none"]:
        out["gaps"].append(f"{tot['none']} dòng co_lech_lon không có ly_do lẫn Cho_quyet")
    # 6. reliability shares
    L += ["**6. Độ tin cậy theo lĩnh vực** (dòng của các sheet <tên>_tham_chieu):", "",
          "| file | dòng | da_kiem_chung | uoc_dinh | ban_dau_doan | NEED_SOURCE | gia_tuong (loại) |", "|---|---:|---:|---:|---:|---:|---:|"]
    share = {}
    allc = collections.Counter()
    for fid in sorted({f for f, _s2 in refs}):
        c = collections.Counter()
        g = 0
        for (f, _s2), rows in refs.items():
            if f != fid:
                continue
            for r in rows:
                c[r.get("do_tin_cay", "")] += 1
                g += r.get("loai_tham_chieu") == "gia_tuong"
        n = sum(c.values())
        allc.update(c)
        share[fid] = {k: c[k] for k in TIN} | {"rows": n, "gia_tuong": g}
        L.append(f"| {fid} | {n} | " + " | ".join(f"{c[k]} ({c[k] / n:.0%})" if n else "0" for k in TIN) + f" | {g} |")
    n = sum(allc.values())
    L += [f"| tổng | {n} | " + " | ".join(f"{allc[k]} ({allc[k] / n:.0%})" if n else "0" for k in TIN) + " | |", ""]
    tn = _dicts(books, REF_FILE, "Thieu_nguon")
    prio = collections.Counter(r.get("uu_tien", "") for r in tn)
    L += [f"Thiếu nguồn (13/Thieu_nguon): {len(tn)} ô NEED_SOURCE (ưu tiên 1: {prio.get('1', 0)}, 2: {prio.get('2', 0)}, "
          f"3: {prio.get('3', 0)}).", ""]
    out["share"], out["need_source"], out["thieu_nguon"] = share, allc[NS], len(tn)
    out["status"] = "DAT" if not out["gaps"] else "CHUA_DAT"
    return out


def from_ctx_books(books) -> dict:
    """The books of an export run as {file: {sheet: (header, values)}} for the sheets run() reads."""
    want = {"Nguon_tham_chieu", "Tham_chieu_game_co_che", "Thieu_nguon", "Xe", "Vu_khi", "Thap", "Boss", "Nha_chinh", "Tuong"}
    out = {}
    for fid, b in books.items():
        for s, sh in b.sheets.items():
            if s in want or s.endswith(("_tham_chieu", "_so_sanh_that")) or "nguon_id" in sh.cols:
                out.setdefault(fid, {})[s] = sh.table(values=True)
    return out
