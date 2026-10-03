"""The NEED_CODE_CHECK cells the game's own code computes, filled from game.json (`--game-json`).

ExportGameDoc (lane B) writes game.json with a top-level `balancePack`: one key per sheet it answers (tunables, interception,
roundGroups, secondRounds, flaresPerRelease, weaponFlight, vehicles, openingSquads, aircraftShotBand, boss, towers, economy,
dialogue, missions, matchEnd, cutscene, audio, wrecks, models, previews, defaultSettings, strikes, defenceWaves). The bomb sheets
(Bom_*) join file 01 after the formulas run, so their cells are filled by fill_late (pack.add_bom_sheets). Each handler below maps one key to the
cells it answers, by sheet and row id; a cell the game.json has no value for stays NEED_CODE_CHECK (listed in _qa and
SELF_CHECK.md), a cell the game says has no meaning becomes KHONG_AP_DUNG with the reason in Schema.ly_do_khong_ap_dung.
The six sheets that were one marker row (settings, cutscene moments, match end, wrecks, previews, mixer) become real sheets.
"""
from __future__ import annotations

import collections

from .model import KHONG_AP_DUNG, NEED_CODE_CHECK
from .scrub import scrub_str


def _sheets(ctx, base: str):
    return [(fid, s) for fid, b in ctx.books.items() for s in b.sheets.values() if s.base_name == base]


class Filler:
    def __init__(self, ctx, bp: dict):
        self.ctx, self.bp, self.filled, self.kad = ctx, bp, 0, 0

    def sheet(self, base: str):
        got = _sheets(self.ctx, base)
        return got[0] if got else (None, None)

    def put(self, fid, sh, rid, col, value) -> bool:
        r = sh.rows.get(rid)
        if r is None or r.values.get(col) != NEED_CODE_CHECK:
            return False
        r.values[col] = value
        self.filled += 1
        return True

    def not_applicable(self, base: str, col: str, reason: str):
        fid, sh = self.sheet(base)
        if sh is None:
            return
        for rid, r in sh.rows.items():
            if r.values.get(col) == NEED_CODE_CHECK:
                r.values[col] = KHONG_AP_DUNG
                self.kad += 1
        self.ctx.kad[(fid, sh.name, col)] = scrub_str(reason)

    def replace_marker(self, base: str, cols: list[tuple], rows: list[tuple], desc: str, nguon: str):
        """A one-row marker sheet becomes the sheet it stood for: cols [(name, meaning, unit)], rows [(id, {col: value})]."""
        fid, sh = self.sheet(base)
        if sh is None or not rows:
            return
        for r in list(sh.rows.values()):
            sh.rows.pop(r.id)
        for c in ("trang_thai", "ghi_chu"):
            sh.cols.pop(c, None)
        for name, meaning, unit in cols:
            sh.col(name, meaning=meaning, unit=unit, auto=False)
        for rid, vals in rows:
            r = sh.row(str(rid), nguon)
            r.values.update(vals)
            self.filled += 1
        sh.desc = desc
        sh.layer = "A"


# ------------------------------------------------------------------------------------------------------- handlers
def h_interception(f: Filler):
    ic = f.bp.get("interception") or {}
    fid, sh = f.sheet("Khac_che")
    if sh is None:
        return
    kinds = ic.get("kinds") or []
    have = set()
    for car in ic.get("carriers") or []:
        have.add(car["id"])
        for k in kinds:
            f.put(fid, sh, car["id"], f"chan_{k}", (car.get("blocks") or {}).get(k, ""))
    cols = [c[len("chan_"):] for c in sh.cols if c.startswith("chan_")]
    upgrades = {u["id"]: u for u in ic.get("upgrades") or []}
    retrofit = [rid for rid in sh.rows if rid not in have and rid in upgrades]
    if retrofit:
        # Only flares and APS are a vehicle's self-defence: a RETROFIT_ELIGIBLE vehicle has APS only with the Trophy module.
        # chan_* is the vehicle as it comes (no APS: nothing blocked); the upgrade's own blocks go in chan_khi_nang_cap.
        sh.col("aps_nang_cap", meaning="APS có được nhờ nâng cấp (mô-đun đặc biệt Trophy, GearSystem.TrophyAps): bán kính, số đạn chặn, "
                                       "giây hồi một đạn chặn; trống: không có nâng cấp APS", auto=False)
        sh.col("chan_khi_nang_cap", meaning="chặn được gì khi lắp nâng cấp APS (loại đạn:co/khong/mot_phan); các cột chan_* là xe "
                                            "khi chưa lắp", auto=False)
        for rid in retrofit:
            u = upgrades[rid]
            row = sh.rows[rid]
            for k in cols:
                f.put(fid, sh, rid, f"chan_{k}", "khong")
            row.values["aps_nang_cap"] = f"{u.get('module', '')}: r {u.get('radius', '')} m, {u.get('charges', '')} đạn chặn, " \
                                         f"{u.get('recharge', '')} s/đạn chặn ({u.get('capability', '')})"
            blocks = u.get("blocks") or {}
            row.values["chan_khi_nang_cap"] = ";".join(f"{k}:{blocks.get(k, 'khong')}" for k in cols)
    for rid, row in sh.rows.items():
        for k in cols:
            if k not in kinds and rid in have:
                # a kind the intercept code never takes (a bullet, a beam): nothing blocks it
                f.put(fid, sh, rid, f"chan_{k}", "khong")
            elif rid not in have and not row.values.get("he_phong_ve"):
                f.put(fid, sh, rid, f"chan_{k}", "khong")  # no defence system: nothing blocks


def h_round_groups(f: Filler):
    rg = f.bp.get("roundGroups") or {}
    fid, sh = f.sheet("Hanh_vi_dan_nhom")
    if sh is None:
        return
    rules = rg.get("rules") or {}
    groups = {g["kind"]: g for g in rg.get("groups") or []}
    per_row = {g["projectile"]: g for g in rg.get("projectileGroups") or []}
    # the sheet counts weapons by projectile kind; the game's projectileGroups are those rows exactly. An older game.json has
    # only the interception groups: then a row is the weighted mean of the groups it spans
    which = {"Bomb": ["bomb"], "Bullet": ["other"], "Flame": ["other"], "Drone": ["drone"],
             "Missile": ["directMissile", "heavyMissile"], "Rocket": ["directRocket", "artilleryRocket"],
             "Shell": ["mortarShell", "artilleryShell", "tankShell"]}
    if per_row:
        which = {pid: [pid] for pid in per_row}
        groups = per_row
        for c, m in (("cach_nham", "cách nhắm của nhóm (tỷ lệ vũ khí dẫn đường / đón đầu, đếm trên chính dạng đạn này)"),
                     ("co_canh_bao", "tỷ lệ vũ khí của dạng đạn này có vòng cảnh báo"),
                     ("thoi_gian_bay_toi_da_s", "thời gian bay tới tầm lâu nhất trong các vũ khí của dạng đạn này")):
            if c in sh.cols:
                sh.cols[c].meaning = m
    if "tuong_tac_gay_nhieu" in sh.cols:
        sh.cols["tuong_tac_gay_nhieu"].meaning = (
            "tương tác với xe gây nhiễu địch (CombatSystem.Launch): đạn dẫn đường (tên lửa, drone) bắn từ hoặc nhắm vào điểm trong "
            "vòng nhiễu thì trượt; trừ vũ khí jamProof và tướng có ưu thế drone; hỏa lực hỗ trợ gọi vào vòng nhiễu rơi rộng "
            f"×{rules.get('jamStrikeScatter', '')}; drone bầy của boss mất mục tiêu với xác suất {rules.get('jamSwarmChance', '')}")
    for pid, names in which.items():
        gs = [groups[n] for n in names if n in groups]
        w = sum(g["weapons"] for g in gs)
        if not w:
            continue

        def mean(key):
            return sum(g[key] * g["weapons"] for g in gs) / w

        pct = lambda x: f"{x * 100:.0f}%"  # noqa: E731
        lead = rules.get("leadCapSeconds", "")
        h = mean("homing")
        f.put(fid, sh, pid, "cach_nham", "dẫn đường (homing)" if h > 0.999 else
              f"đón đầu (led, trần {lead} s)" if h < 0.001 else f"dẫn đường {pct(h)} vũ khí, còn lại đón đầu (trần {lead} s)")
        f.put(fid, sh, pid, "khi_no", f"nổ lan {pct(mean('splashing'))} vũ khí" +
              (f"; ngòi cận đích {rules['proximityFuzeM']} m" if pid in ("Missile", "Drone") and "proximityFuzeM" in rules else ""))
        f.put(fid, sh, pid, "khi_truot", f"quá tầm × {rules.get('missReachScale', '')} tự hủy; đạn dẫn bằng mắt mất kẻ bắn hoặc "
                                          "tầm nhìn thì mất" if h > 0 else f"quá tầm × {rules.get('missReachScale', '')} tự hủy")
        f.put(fid, sh, pid, "co_canh_bao", f"{pct(mean('warns'))} vũ khí có vòng cảnh báo")
        f.put(fid, sh, pid, "thoi_gian_bay_toi_da_s", round(max(g["maxFlightSeconds"] for g in gs), 4))
        f.put(fid, sh, pid, "tuong_tac_phao_sang", f"pháo sáng mồi {pct(mean('flareTakes'))} vũ khí (xác suất "
                                                      f"{rules.get('flareDecoyChance', '')})")
        f.put(fid, sh, pid, "tuong_tac_aps", f"APS chặn được {pct(mean('apsEligible'))}, CIWS {pct(mean('ciwsEligible'))} "
                                              f"vũ khí")
        if all("jamTakes" in g for g in gs):
            j = mean("jamTakes")
            miss = f"trượt {_num(rules.get('jamMissMinM'), 0)}–{_num(rules.get('jamMissMinM'), rules.get('jamMissSpreadM'))} m"
            f.put(fid, sh, pid, "tuong_tac_gay_nhieu",
                  "không bị nhiễu (không phải đạn dẫn đường)" if j < 0.001 else
                  f"bị nhiễu {pct(j)} vũ khí (đạn dẫn đường trong vòng nhiễu địch: {miss})")


def h_second_rounds(f: Filler):
    sr = f.bp.get("secondRounds") or {}
    fid, sh = f.sheet("Dan_thay_the")
    if sh is None:
        return
    by = {(r["weapon"], r["round"]): r for r in sr.get("rounds") or []}
    for rid, row in sh.rows.items():
        v = row.values
        key = (v.get("vu_khi_goc"), v.get("dan_id"))
        r = by.get(key)
        if r is None:
            continue
        f.put(fid, sh, rid, "dieu_kien_tu_doi", r["use"] + (" (chỉ tinh nhuệ)" if r.get("eliteOnly") else ""))
        f.put(fid, sh, rid, "thoi_gian_doi_s", r.get("switchSeconds", ""))
        f.put(fid, sh, rid, "thoi_gian_giu_s", sr.get("roundHoldSeconds", ""))


def h_flares(f: Filler):
    fid, sh = f.sheet("Phao_sang")
    for e in f.bp.get("flaresPerRelease") or []:
        if sh is not None:
            f.put(fid, sh, e["id"], "so_qua_moi_lan", f"{e['flaresMin']};{e['flaresMax']}")


def h_ripple(f: Filler):
    f.not_applicable("Vu_khi", "lech_nong_s",
                     "súng nhiều nòng kiểu RIPPLE bắn từng viên nối tiếp theo nhịp bắn (khoang_phat_trong_loat_s), không có độ "
                     "lệch riêng; WeaponDef.BarrelGap 0,07 s chỉ là độ lệch hình của kiểu SIMULTANEOUS, không ảnh hưởng lối chơi")


def h_weapon_flight(f: Filler):
    fid, sh = f.sheet("Vu_khi")
    if sh is None:
        return
    for e in f.bp.get("weaponFlight") or []:
        f.put(fid, sh, e["id"], "thoi_gian_bay_toi_tam_s_game", e.get("flightAtRangeSeconds", ""))


def h_vehicles(f: Filler):
    vs = {v["id"]: v for v in (f.bp.get("vehicles") or {}).get("vehicles") or []}
    fx, xe = f.sheet("Xe")
    fy, sr = f.sheet("Xe_suy_ra")
    for vid, v in vs.items():
        u = v.get("unlock") if isinstance(v.get("unlock"), dict) else {}
        if xe is not None:
            f.put(fx, xe, vid, "mau_trong_tran_hp", v.get("hpInBattle", ""))
            f.put(fx, xe, vid, "nhom_gia", v.get("priceGroup", ""))
            f.put(fx, xe, vid, "hoi_tu_ve_s", v.get("selfDefenceRechargeSeconds", ""))
            if u.get("route"):
                f.put(fx, xe, vid, "mo_khoa", unlock_text(u))
            elif xe.rows.get(vid) is not None and xe.rows[vid].values.get("loai_thuc_the") == "tinh_nhue":
                f.put(fx, xe, vid, "mo_khoa", KHONG_AP_DUNG)
                f.ctx.kad[(fx, xe.name, "mo_khoa")] = "xe tinh nhuệ không phải thẻ bài (Card = false): không có đường mở khóa"
        if sr is not None:
            f.put(fy, sr, vid, "nhom_gia", v.get("priceGroup", ""))
            f.put(fy, sr, vid, "he_so_gia", v.get("priceFactor", ""))
            f.put(fy, sr, vid, "thuong_suc_manh", v.get("powerBonus", ""))
            f.put(fy, sr, vid, "tha_du_theo_nhom_s", v.get("dropByGroupSeconds", ""))


def unlock_text(u: dict) -> str:
    bits = [u["route"]]
    if u.get("mission"):
        bits.append(f"nhiệm vụ {u['mission']}")
    if u.get("storyLoot"):
        bits.append("chiến lợi phẩm cốt truyện")
    if u.get("earlyBuy"):
        bits.append("mua sớm")
    if u.get("price"):
        bits.append(f"{u['price']} xu")
    return "; ".join(bits)


def h_towers(f: Filler):
    fid, sh = f.sheet("Thap")
    if sh is None:
        return
    for t in f.bp.get("towers") or []:
        f.put(fid, sh, t["id"], "the_cu_gop_vao", t.get("card", ""))
        f.put(fid, sh, t["id"], "co_can_bang", t.get("balanceCut", ""))
        f.put(fid, sh, t["id"], "mo_khoa", t.get("unlockRoute", ""))
        f.put(fid, sh, t["id"], "hoi_tu_ve_s", t.get("selfDefenceRechargeSeconds", ""))


def h_opening(f: Filler):
    fid, sh = f.sheet("Doi_mo_man_suy_ra")
    modes = f.bp.get("openingSquads") or []
    if sh is None or not modes:
        return
    for rid, row in sh.rows.items():
        base = row.values.get("base_cp_uoc_tinh_game")
        if not isinstance(base, (int, float)):
            continue
        parts = []
        for m in modes:
            if not m.get("startCp"):
                continue
            parts.append(f"{m['mode']}:{round(min(m.get('maxShare', 0.6), base / m['startCp']) * 100, 1)}")
        f.put(fid, sh, rid, "phan_tram_cp_khoi_dau", ";".join(parts))


def h_aircraft_band(f: Filler):
    b = f.bp.get("aircraftShotBand") or {}
    if b.get("status") == KHONG_AP_DUNG:
        f.not_applicable("May_bay_so_phat", "dai_muc_tieu", b.get("reason", ""))


def h_boss(f: Filler):
    b = f.bp.get("boss") or {}
    fid, sh = f.sheet("Boss")
    t = b.get("timeToKillSeconds") or {}
    if sh is not None and t:
        for rid, row in sh.rows.items():
            kind = {"mini": "Mini", "main": "Main"}.get(row.values.get("phan_loai"))
            if kind and f"weekly{kind}" in t:
                f.put(fid, sh, rid, "thoi_gian_ha_muc_tieu_s", f"tuan:{t[f'weekly{kind}']};day_du:{t[f'full{kind}']}")
    comp = b.get("compensation") or {}
    if comp.get("status") == KHONG_AP_DUNG:
        f.not_applicable("Boss_dps", "cach_bu", comp.get("reason", ""))
    fh, hs = f.sheet("Sanhunt")
    hunt = b.get("hunt") or {}
    if hs is not None:
        for e in hunt.get("bosses") or []:
            f.put(fh, hs, e["id"], "phong_khong", bool(e.get("airDefence")))
    weeks = hunt.get("weeks") or []
    if hs is not None and weeks:
        year = hunt.get("weeksYear", "")
        seen = collections.defaultdict(list)  # boss -> [(week number, place in the run)]
        for w in weeks:
            for place, bid in enumerate(w.get("run") or [], 1):
                seen[bid].append((int(w["week"]) % 100, place))
        for rid in hs.rows:
            got = seen.get(rid, [])
            f.put(fh, hs, rid, "tuan", f"{len(got)}/{len(weeks)} tuần" + (": " + ",".join(f"W{wk:02d}#{pl}" for wk, pl in got)
                                                                       if got else ""))
        if "tuan" in hs.cols:
            hs.cols["tuan"].meaning = (
                f"boss có trong Săn trùm tuần nào của năm ISO {year} (BossHunts.Weekly(năm×100+tuần), cùng kết quả mọi máy): "
                "số tuần / tổng số tuần, rồi từng tuần Wnn#vị trí trong danh sách 10 boss của tuần")


def h_economy(f: Filler):
    e = f.bp.get("economy") or {}
    fid, sh = f.sheet("Kinh_te")
    if sh is not None and e:
        f.put(fid, sh, "ma.tiep_te_cong_thuc", "gia_tri_chu", e.get("formula", ""))
        catch = ";".join(f"{c['ownOverRival']}:{c['incomeBoost']}" for c in e.get("catchUpCurve") or [])
        up = ";".join(f"{c['armyOverSupply']}:{c['incomeKept']}" for c in e.get("upkeepCurve") or [])
        f.put(fid, sh, "ma.hoan_cp_khi_ha", "gia_tri_chu",
              f"kill_share {e.get('killShare')}; tran_hoan_khi_ha {e.get('killRefundCap')}; tran_hoan_khi_mat "
              f"{e.get('lossRefundCap')}; duong_bat_kip (ban/doi_thu:tang_thu_nhap) {catch}; duong_phat_tiep_te "
              f"(quan/tiep_te:thu_nhap_giu) {up}")
    fv, vh = f.sheet("Vo_han")
    if vh is not None and "coinDecay" in (e.get("endless") or {}):
        for rid in vh.rows:
            f.put(fv, vh, rid, "he_so_tang_thuong", e["endless"]["coinDecay"])


def h_dialogue(f: Filler):
    d = f.bp.get("dialogue") or {}
    portrait = {s["id"]: bool(s.get("portrait")) for s in (d.get("speakers") or []) + (d.get("characters") or [])}
    fid, sh = f.sheet("Nhan_vat")
    if sh is not None:
        for rid in sh.rows:
            if rid in portrait:
                f.put(fid, sh, rid, "chan_dung", portrait[rid])
    ft, tr = f.sheet("Trigger_thoai")
    if tr is not None:
        for t in d.get("triggers") or []:
            f.put(ft, tr, t["trigger"], "hoi_chieu_so_lan", f"mot_lan:{t.get('onceLines', 0)};lap:{t.get('repeatLines', 0)}")
    if tr is not None:
        for rid, row in tr.rows.items():
            if row.values.get("hoi_chieu_so_lan") == NEED_CODE_CHECK and row.values.get("so_cau") == 0:
                f.put(ft, tr, rid, "hoi_chieu_so_lan", "mot_lan:0;lap:0")
    fl, th = f.sheet("Thoai")
    mv = d.get("maxVisibleLines") or {}
    worst = max((mv.get(k, {}).get("maxLinesVi", 0) for k in ("raised", "normal")), default=0)
    worst = max([worst] + [mv.get(k, {}).get("maxLinesEn", 0) for k in ("raised", "normal")])
    per_line = mv.get("perLine") or {}
    if th is not None and (worst or per_line):
        for rid, row in th.rows.items():
            key = row.values.get("khoa_loc") or rid
            f.put(fl, th, rid, "so_dong_hien_thi_toi_da", per_line.get(key, per_line.get(rid, worst)) if per_line else worst)
            sp = row.values.get("nguoi_noi")
            if sp in portrait:
                f.put(fl, th, rid, "chan_dung", portrait[sp])
        th.cols["so_dong_hien_thi_toi_da"].meaning = (
            f"số dòng câu thoại này chiếm (tiếng Việt hoặc Anh, lấy số lớn) ở dải hẹp nhất, cỡ chữ {mv.get('fontSizePx', '')} px, "
            f"có chân dung ({mv.get('method', '')})" if per_line else
            f"số dòng tối đa của dòng thoại tệ nhất ({mv.get('raised', {}).get('worstKey', '')}) ở dải hẹp nhất, cỡ chữ "
            f"{mv.get('fontSizePx', '')} px, có chân dung ({mv.get('method', '')}); cùng một số cho mọi dòng (game.json cũ không có "
            "số từng dòng)")


def h_missions(f: Filler):
    fid, sh = f.sheet("Nhiem_vu")
    ms = f.bp.get("missions") or []
    if sh is not None:
        for m in ms:
            f.put(fid, sh, m["id"], "trang_thai_kich_ban", m.get("scriptStatus", ""))
    reason = next((m["deckGoal"] for m in ms if str(m.get("deckGoal", "")).startswith(KHONG_AP_DUNG)), "")
    if reason:
        f.not_applicable("Bo_bai_game", "muc_tieu_goc_giu", reason.split(":", 1)[-1].strip())


def h_defence_waves(f: Filler):
    d = f.bp.get("defenceWaves") or {}
    fid, sh = f.sheet("Dot_phong_thu")
    if sh is None or not d:
        return
    for lv in d.get("levels") or []:
        rid = f"hq{lv['level']}"
        f.put(fid, sh, rid, "he_so_do_kho", round(float(lv.get("waveScale", 0)), 4))
        waves = (lv.get("waves") or {}).get("Normal") or []
        f.put(fid, sh, rid, "duong_cong_dot", ";".join(str(n) for n in waves))
    if "he_so_do_kho" in sh.cols:
        sh.cols["he_so_do_kho"].meaning = (
            "hệ số cỡ đợt của Phòng thủ theo căn cứ tham chiếu của cấp HQ (BaseStrength.WaveScale(ReferenceScore)): "
            "clamp((điểm / 100)^mũ, min, max), tham số ở tunables modes.baseStrengthRules; thu nhập bên tấn công × căn bậc hai của nó")
    if "duong_cong_dot" in sh.cols:
        sh.cols["duong_cong_dot"].meaning = (
            f"số xe đợt 1..{d.get('waveCount', '')} ở Thường (SiegeMode.WaveSize: min(trần, round((đầu + tăng × (n-1)) × hệ số))); "
            "số của Dễ / Khó ở game.json balancePack.defenceWaves, tham số ở tunables modes.defendWaves")


def h_bomb_sheets(f: Filler):
    """Bom_vu_khi / Bom_canh_bao / Bom_don_vi (added after the formulas: fill_late)."""
    st = f.bp.get("strikes") or {}
    if not st:
        return
    sup = {s["id"]: s for s in st.get("supports") or []}
    big = {b["id"]: b for b in st.get("bigAttacks") or []}
    car = {c["id"]: c for c in st.get("carriers") or []}

    def edge(rid):
        if rid in sup:
            return sup[rid].get("edgeRadius", 0)
        strikes = (big.get(rid) or {}).get("strikes") or []
        return round(float(strikes[0].get("edgeRadius", 0)), 3) if strikes else None

    for base, col in (("Bom_vu_khi", "ria_m"), ("Bom_canh_bao", "ban_kinh_ria_m")):
        fid, sh = f.sheet(base)
        if sh is None:
            continue
        for rid in sh.rows:
            e = edge(rid)
            if e is not None:
                f.put(fid, sh, rid, col, e)
        if col in sh.cols:
            sh.cols[col].meaning = (
                "bán kính rìa nổ (lớp ngoài, ăn edgeShare sát thương). Thẻ hỗ trợ: 0, nổ một lớp, sát thương giảm dần tới "
                "rimShare ở mép (DamageSystem.Splash, tunables weapons.damageRules.edgeFalloff); siêu vũ khí boss: BigStrikeDef.EdgeRadius "
                "(gấp đôi lõi, tối đa 20 m)")
    fid, sh = f.sheet("Bom_vu_khi")
    if sh is not None:
        for rid in sh.rows:
            if rid in sup:
                f.put(fid, sh, rid, "loai_sat_thuong", sup[rid].get("type", ""))
    fid, sh = f.sheet("Bom_don_vi")
    if sh is None:
        return
    no_drop, no_rearm = False, False
    for rid in sh.rows:
        if rid in sup:
            alt = sup[rid].get("releaseAltitude", 0) or 0
            if f.put(fid, sh, rid, "do_cao_tha_m", alt if alt > 0 else KHONG_AP_DUNG) and not alt > 0:
                no_drop = True
        c = car.get(rid)
        if c is not None:
            if f.put(fid, sh, rid, "nap_lai_s", c.get("rearmSeconds", "") if c.get("loaded") else KHONG_AP_DUNG) and not c.get("loaded"):
                no_rearm = True
    if no_drop:
        f.ctx.kad[(fid, sh.name, "do_cao_tha_m")] = scrub_str(
            "thẻ hỗ trợ không có máy bay thả bom: bom lượn bay tới như tên lửa hành trình (StrikeEffects.LaunchCruise), bom con chống "
            "tăng (Homing) rơi thẳng lên xe; độ cao của thẻ ném bom là hình (StrikeEffects.ReleaseAltitude), mô phỏng không dùng")
    if no_rearm:
        f.ctx.kad[(fid, sh.name, "nap_lai_s")] = scrub_str(
            "boss không có kho bom (VehicleDef.LoadOf = 0 với boss): không về nạp, bắn theo thời gian nạp của vũ khí (cooldown)")


def _num(a, b) -> str:
    try:
        return f"{float(a) + float(b):g}"
    except (TypeError, ValueError):
        return ""


def h_models(f: Filler):
    m = f.bp.get("models") or {}
    if m.get("status") == KHONG_AP_DUNG:
        f.not_applicable("Model", "tam_giac_lod", m.get("reason", ""))


# the marker sheets that become real sheets ------------------------------------------------------------------------
def h_default_settings(f: Filler):
    d = f.bp.get("defaultSettings") or {}
    if d:
        f.replace_marker("Cai_dat_mac_dinh", [("gia_tri", "giá trị mặc định của cài đặt (PlayerProfile / Graph)", ""),
                                              ("kieu", "kiểu: bool / int / float / text", "")],
                         [(k, {"gia_tri": v, "kieu": _kind(v)}) for k, v in d.items()],
                         "Cài đặt mặc định của người chơi mới (âm lượng, đồ họa, rung, hỗ trợ, ngôn ngữ), đọc từ mã bởi ExportGameDoc",
                         "game.json balancePack.defaultSettings")


def h_cutscene(f: Filler):
    d = f.bp.get("cutscene") or {}
    if d:
        f.replace_marker("Cutscene_khoanh_khac", [("gia_tri", "giá trị", ""), ("don_vi", "đơn vị", "")],
                         [(k, {"gia_tri": v, "don_vi": "s" if k.endswith("Seconds") else ""}) for k, v in d.items()],
                         "Khoảnh khắc điện ảnh: bật mặc định, thời lượng tối đa, vào ra mờ, tỷ lệ", "game.json balancePack.cutscene")


def h_match_end(f: Filler):
    d = f.bp.get("matchEnd") or {}
    if d:
        rows = [(k["kind"], {"giay": k.get("seconds"), "chuyen_dong_cham": bool(k.get("slowMotion"))}) for k in d.get("kinds") or []]
        rows.append(("bo_qua_sau_giay", {"giay": d.get("skipAfterSeconds"), "chuyen_dong_cham": ""}))
        f.replace_marker("Ket_tran", [("giay", "thời lượng màn kết trận theo loại", "s"),
                                      ("chuyen_dong_cham", "có chuyển động chậm", "")], rows,
                         "Màn kết trận: thời lượng và chuyển động chậm theo loại (thắng lớn đầu tiên, thắng đầu, chơi lại, thua), "
                         "thời gian cho phép bỏ qua", "game.json balancePack.matchEnd")


def h_wrecks(f: Filler):
    d = f.bp.get("wrecks") or []
    if d:
        f.replace_marker("Xac_vo", [("tran_day_du", "số xác vỡ đầy đủ tối đa cùng lúc", ""),
                                    ("song_toi_thieu_s", "thời gian xác tồn tại ngắn nhất", "s"),
                                    ("song_toi_da_s", "thời gian xác tồn tại dài nhất", "s"),
                                    ("song_boss_s", "thời gian xác boss tồn tại", "s")],
                         [(w["tier"], {"tran_day_du": w.get("fullCap"), "song_toi_thieu_s": w.get("lifeMinSeconds"),
                                       "song_toi_da_s": w.get("lifeMaxSeconds"), "song_boss_s": w.get("bossLifeSeconds")})
                          for w in d], "Xác vỡ theo bậc đồ họa: trần đầy đủ và thời gian sống", "game.json balancePack.wrecks")


def h_previews(f: Filler):
    d = f.bp.get("previews") or []
    if d:
        f.replace_marker("Xem_truoc", [("canh", "cảnh nền của màn xem trước (mặt đất, biển, bệ tháp, không...)", "")],
                         [(p["id"], {"canh": p.get("setting", "")}) for p in d],
                         "Màn xem trước của từng đơn vị: cảnh nền", "game.json balancePack.previews")


def h_audio(f: Filler):
    d = f.bp.get("audio") or {}
    if d:
        rows = [(f"am_luong.{k}", {"loai": "am_luong_mac_dinh", "gia_tri": v}) for k, v in (d.get("volumes") or {}).items()]
        rows += [(f"nhom.{g}", {"loai": "nhom_kenh", "gia_tri": ""}) for g in d.get("groups") or []]
        f.replace_marker("Am_thanh_mixer", [("loai", "am_luong_mac_dinh / nhom_kenh", ""),
                                            ("gia_tri", "âm lượng mặc định 0-1 (chỉ cho am_luong_mac_dinh)", "")],
                         rows, "Mixer âm thanh: nhóm kênh và âm lượng mặc định", "game.json balancePack.audio")


def _kind(v) -> str:
    return "bool" if isinstance(v, bool) else "int" if isinstance(v, int) else "float" if isinstance(v, float) else "text"


HANDLERS = [h_interception, h_round_groups, h_second_rounds, h_flares, h_ripple, h_weapon_flight, h_vehicles, h_towers, h_opening,
            h_aircraft_band, h_boss, h_economy, h_dialogue, h_missions, h_defence_waves, h_models, h_default_settings, h_cutscene,
            h_match_end, h_wrecks, h_previews, h_audio]
LATE_HANDLERS = [h_bomb_sheets]  # sheets added after the formulas (pack.add_bom_sheets)


def fill(ctx, game: dict) -> int:
    return _run(ctx, game, HANDLERS, report_errors=True)


def fill_late(ctx, game: dict) -> int:
    """The bomb sheets' cells (they join 01_chien_dau after the formulas run)."""
    return _run(ctx, game, LATE_HANDLERS, report_errors=False)


def _run(ctx, game: dict, handlers, report_errors: bool) -> int:
    bp = game.get("balancePack") or {}
    f = Filler(ctx, bp)
    errors = []
    for h in handlers:
        try:
            h(f)
        except (KeyError, TypeError, ValueError) as e:  # a handler the game.json does not fit: its cells stay NEED_CODE_CHECK
            errors.append(f"{h.__name__}: {type(e).__name__} {e}")
    if report_errors:
        for k, v in bp.items():
            if isinstance(v, dict) and "error" in v:
                errors.append(f"game.json balancePack.{k}: {v['error']}")
    for e in errors:
        ctx.issue("gamefill: " + e)
    ctx.game_not_applicable = getattr(ctx, "game_not_applicable", 0) + f.kad if not report_errors else f.kad
    return f.filled
