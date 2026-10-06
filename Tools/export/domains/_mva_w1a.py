"""08_ban_do (pack 06_ban_do) + 06_ai (pack 09_ai), layer C, map / visual / audio W1-A / W2-A (06/10): the generated
GameplayTopology outputs of Tools/maps/topogen (Docs/maps/*.json: never hand-authored, the canonical map JSON stays the
authority), read as data:

* Ban_do_dia_hinh_tong: per map file: components, chokes, lanes, positions, staging, shore regions, load gates, warnings.
* Ban_do_diem_nghen (spec E), Ban_do_lan_chien_thuat (F), Ban_do_kiem_tra_tuyen (D1), Ban_do_cong_bang_bai_tha (G),
  Ban_do_vi_tri_chien_thuat (J), Ban_do_khu_tap_ket (I), Ban_do_pha_tuong (O), Ban_do_vung_ban_bo (K),
  Ban_do_tuyen_bien_dong_hoc (L/N), Ban_do_quay_tau (M), Ban_do_canh_bao (U: the warning registry with status / owner / reason),
  Ban_do_ngu_nghia_dia_hinh (P), Thoi_tiet_trinh_bay (Q: presentation only; visibility stays Thoi_tiet).
* Ban_do_tiep_can_muc_tieu (spec H, lane W2-A): objective approach routes by role (Primary/Secondary/Flank/Shortest/Safest/
  HeavyCompatible), artillery-support and defender-fallback regions.
* Ban_do_nghiem_thu (spec CI map rows + BW + H + I, lane W2-A): the acceptance row pass/fail/detail Tools/maps/topogen measures
  per map, the same rows the EditMode tests (MapTopologyW1ATests / MapTopologyW2ATests) assert.
* Ban_do_canh_ap_luc (spec BT, lane W2-A): the six map stress scene definitions and their resolved focus; render/audio metrics
  are recorded by the final part in Unity play, not here.
* 06_ai AI_dia_hinh_tieu_thu: which AI code reads which GameplayTopology field (P0-B feasibility, P1 traffic, P2 fire support).

Read only: nothing here changes a game value. A missing output file is reported (ctx.issue) and its sheets stay empty."""
from __future__ import annotations

import json

from core.repo import ROOT

DOCS = "Docs/maps/"
GEN = "Tools/maps/topogen"


def _load(ctx, name):
    p = ROOT / (DOCS + name)
    if not p.exists():
        ctx.issue(f"08 MVA W1-A: {DOCS}{name} missing (run {GEN})")
        return {}
    return json.loads(p.read_text("utf-8"))


def _cell(v):
    if v is None:
        return ""
    if isinstance(v, list):
        if v and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            return ";".join(str(x) for x in v)
        return ";".join(str(_cell(x)) if not isinstance(x, list) else ",".join(str(y) for y in x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return v


def _table(book, name, title, desc, cols, rows, src):
    """cols: (column, json key, meaning, unit); rows: (row id, map id, dict)."""
    s = book.sheet(name, title, f"{desc} ({DOCS}{src}, sinh bởi {GEN})", layer="C")
    s.col("ban_do", meaning="file bản đồ (Ban_do.id)")
    for c, _k, m, u in cols:
        s.col(c, meaning=m, unit=u)
    for rid, mid, d in rows:
        r = s.row(rid, f"{DOCS}{src} (maps.{mid})")
        r.set("ban_do", mid)
        for c, k, _m, _u in cols:
            r.set(c, _cell(d.get(k)))
    return s


def _each(data, key):
    for mid in sorted((data.get("maps") or {})):
        for i, d in enumerate(data["maps"][mid].get(key) or []):
            yield mid, i, d


def build(ctx, book):
    topo = _load(ctx, "GameplayTopology.json")
    conn = _load(ctx, "MapConnectivity.json")
    pos = _load(ctx, "TacticalPositions.json")
    naval = _load(ctx, "NavalRouteAudit.json")
    fair = _load(ctx, "SpawnFairnessAudit.json")
    reg = _load(ctx, "MapWarningRegistry.json")
    appr = _load(ctx, "ObjectiveApproaches.json")
    acc = _load(ctx, "MapAcceptance.json")
    stress = _load(ctx, "STRESS_SCENES.json")

    # ------------------------------------------------------------------ per map summary
    warn_n = {}
    for w in reg.get("warnings") or []:
        mid = w["warningId"].split(":")[0]
        warn_n[mid] = warn_n.get(mid, 0) + 1
    rows = []
    for mid in sorted((topo.get("maps") or {})):
        m = topo["maps"][mid]
        gates = m.get("loadGates") or []
        p = (pos.get("maps") or {}).get(mid, {})
        n = (naval.get("maps") or {}).get(mid, {})
        rows.append((mid, mid, {
            "ground": m.get("ground"), "naval": m.get("naval"), "amphibious": m.get("amphibious"),
            "chokes": len(m.get("chokes") or []), "lanes": len(m.get("lanes") or []), "breaches": len(m.get("breaches") or []),
            "positions": len(p.get("positions") or []), "staging": len(p.get("staging") or []),
            "shore": len(n.get("shoreFireRegions") or []),
            "gates": f"{sum(1 for g in gates if g.get('pass'))}/{len(gates)}",
            "gatesFailed": [g["gate"] for g in gates if not g.get("pass")], "warnings": warn_n.get(mid, 0)}))
    _table(book, "Ban_do_dia_hinh_tong", "Bản đồ: địa hình chiến thuật (tổng)",
           "Mỗi file bản đồ: số thành phần liên thông theo miền, điểm nghẽn, làn, vị trí, khu tập kết, vùng bắn bờ, cổng nạp (spec BW), cảnh báo",
           [("tp_mat_dat", "ground", "số thành phần liên thông mặt đất", ""), ("tp_bien", "naval", "số thành phần liên thông biển", ""),
            ("tp_luong_cu", "amphibious", "số thành phần lưỡng cư", ""), ("so_diem_nghen", "chokes", "số điểm nghẽn chiến thuật", ""),
            ("so_lan", "lanes", "số làn chiến thuật", ""), ("so_doan_tuong_pha", "breaches", "số đoạn tường có dữ liệu phá", ""),
            ("so_vi_tri", "positions", "số vị trí chiến thuật", ""), ("so_khu_tap_ket", "staging", "số khu tập kết", ""),
            ("so_vung_ban_bo", "shore", "số vùng bắn từ bờ", ""), ("cong_nap", "gates", "cổng nạp đạt / tổng (spec BW)", ""),
            ("cong_nap_truot", "gatesFailed", "cổng nạp trượt", ""), ("so_canh_bao", "warnings", "số cảnh báo trong sổ (spec U)", "")],
           rows, "GameplayTopology.json")

    # ------------------------------------------------------------------ chokes, lanes, breaches
    _table(book, "Ban_do_diem_nghen", "Bản đồ: điểm nghẽn chiến thuật (spec E)",
           "Điểm nghẽn: loại, bề rộng dùng được, số xe song song theo hạng, lưu lượng, hai chiều, vùng xếp hàng A/B; cùng số đo với các lối của TrafficCoordinator",
           [("ma", "id", "id điểm nghẽn (thứ tự lối giao thông)", ""), ("loai", "type", "Gate / Bridge / StreetCanyon / WallBreach / RiverCrossing / RailCrossing / HarborThroat / NaturalTerrainGap", ""),
            ("hinh", "shape", "dạng lối giao thông (Gate / Choke / Bridge / NarrowRoad)", ""), ("tam", "centre", "tâm (x;z)", "m"),
            ("rong_mo_m", "openWidth", "bề rộng ô mở (tâm thân xe)", "m"), ("rong_dung_duoc_m", "usableWidthM", "bề rộng vật lý dùng được", "m"),
            ("dai_m", "length", "chiều dài", "m"), ("xe_nhe_song_song", "maxLightSideBySide", "xe nhẹ song song tối đa", ""),
            ("xe_vua_song_song", "maxMediumSideBySide", "xe vừa song song tối đa", ""), ("xe_nang_song_song", "maxHeavySideBySide", "xe nặng song song tối đa", ""),
            ("luu_luong_xe_s", "estimatedThroughput", "xe vừa qua mỗi giây", "1/s"), ("hai_chieu", "oppositeTrafficAllowed", "cho hai chiều cùng lúc", ""),
            ("hang_lon_nhat", "largestClass", "hạng xe lớn nhất lọt", ""), ("then_chot", "critical", "nằm trên tuyến chính", ""),
            ("hang_a_an_toan", "queueASafe", "vùng xếp hàng A an toàn (spec E2)", ""), ("hang_a_van_de", "queueAIssue", "lý do vùng A không an toàn", ""),
            ("hang_b_an_toan", "queueBSafe", "vùng xếp hàng B an toàn", ""), ("hang_b_van_de", "queueBIssue", "lý do vùng B không an toàn", "")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(topo, "chokes")], "GameplayTopology.json")
    _table(book, "Ban_do_lan_chien_thuat", "Bản đồ: làn chiến thuật (spec F)",
           "Làn: loại (Main / Secondary / Flank / Service / BossCorridor), bề rộng, chiều, hạng xe hỗ trợ, tốc độ dự kiến, điểm nghẽn phụ thuộc, mục tiêu phủ, cấm đỗ",
           [("ma", "id", "id làn", ""), ("loai", "kind", "loại làn", ""), ("tu", "from", "từ (anchor)", ""), ("den", "to", "đến (anchor)", ""),
            ("dai_m", "lengthM", "chiều dài", "m"), ("rong_p10_m", "laneWidth", "bề rộng P10", "m"), ("rong_min_m", "minWidth", "bề rộng hẹp nhất", "m"),
            ("chieu", "directionality", "TwoWay / Alternating", ""), ("hang_xe", "vehicleClassSupport", "hạng xe lớn nhất đi được cả làn", ""),
            ("toc_do_m_s", "expectedTravelSpeed", "tốc độ xe vừa dự kiến", "m/s"), ("diem_nghen", "chokeDependency", "id điểm nghẽn đi qua", ""),
            ("muc_tieu", "objectiveCoverage", "mục tiêu làn đi qua", ""), ("luu_luong_xe_s", "trafficCapacity", "xe vừa mỗi giây", "1/s"),
            ("cam_do", "parkingForbidden", "pháo / hỗ trợ không đỗ trên làn", "")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(topo, "lanes")], "GameplayTopology.json")
    _table(book, "Ban_do_pha_tuong", "Bản đồ: dữ liệu phá tường (spec O)",
           "Mỗi đoạn tường: tuyến bị chặn, quãng đường tiết kiệm khi phá, hạng xe lớn có thêm lối, mục tiêu có thêm lối, còn lối khác, tháp phòng thủ phủ",
           [("ma", "id", "id đoạn", ""), ("chu", "owner", "chủ tường", ""), ("vong", "ring", "vòng", ""), ("tam", "centre", "tâm", "m"),
            ("rong_lo_m", "openingWidthM", "bề rộng lỗ khi phá", "m"), ("tuyen_bi_chan", "blockedRouteIds", "tuyến bị đoạn này làm dài", ""),
            ("tiet_kiem_m", "pathCostReductionOnDestroy", "quãng đường tiết kiệm lớn nhất", "m"), ("hang_xe_them", "heavyAccessGained", "hạng xe chỉ qua được khi phá", ""),
            ("them_loi_muc_tieu", "objectiveAccessGained", "mục tiêu có thêm lối", ""), ("con_loi_khac", "alternateRouteExists", "còn lối qua cổng", ""),
            ("thap_phu", "defensiveTowerCoverage", "tháp / đoạn súng trong tầm", "")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(topo, "breaches")], "GameplayTopology.json")

    # ------------------------------------------------------------------ routes, spawns
    _table(book, "Ban_do_kiem_tra_tuyen", "Bản đồ: tuyến theo hạng xe (spec D1)",
           "Bãi thả -> mục tiêu theo hạng Light / Medium / Heavy / SuperHeavy / Boss: tới được, chiều dài, bề rộng thông hẹp nhất, chỗ quay, cổng, cầu",
           [("tu", "from", "từ", ""), ("den", "to", "đến", ""), ("hang", "class", "hạng xe", ""), ("toi_duoc", "reachable", "tới được", ""),
            ("dai_m", "lengthM", "chiều dài", "m"), ("rong_min_m", "minClearWidthM", "bề rộng thông hẹp nhất", "m"),
            ("cho_quay_min_m", "minTurnSpaceM", "bán kính chỗ quay hẹp nhất ở góc (trống: không góc)", "m"),
            ("cong_min_m", "gateMinWidthM", "cổng hẹp nhất (trống: không qua cổng)", "m"), ("cau_min_m", "bridgeMinWidthM", "cầu hẹp nhất", "m"),
            ("quay_vua", "turnsFit", "mọi góc đủ chỗ xoay", "")],
           [(f"{mid}/{d['from']}>{d['to']}/{d['class']}", mid, d) for mid, _i, d in _each(conn, "routes")], "MapConnectivity.json")
    _table(book, "Ban_do_cong_bang_bai_tha", "Bản đồ: công bằng bãi thả (spec G)",
           "Mỗi bãi thả: tầm bắn thẳng của địch vào bãi / lối ra, phủ pháo, quãng tới chỗ nấp, bề rộng lối ra, lối khác, sức chứa, ETA, cờ G1",
           [("bai_tha", "spawn", "bãi thả", ""), ("doi", "team", "đội", ""), ("lo_bai", "enemyDirectLOSAtSpawn", "tỷ lệ bãi bị địch bắn thẳng", "share"),
            ("lo_loi_ra", "enemyDirectLOSAtExit", "tỷ lệ lối ra bị bắn thẳng", "share"), ("phu_phao", "enemyArtilleryCoverageAtSpawn", "tỷ lệ bãi trong tầm pháo từ bãi địch", "share"),
            ("toi_cho_nap_m", "spawnToFirstCoverM", "quãng tới chỗ nấp đầu tiên", "m"), ("rong_loi_ra_m", "spawnExitWidthM", "tổng bề rộng lối ra (trống: mở mọi phía)", "m"),
            ("loi_hep_nhat_m", "narrowestExitM", "lối ra hẹp nhất", "m"), ("loi_khac", "alternateExitCount", "số lối ra thêm", ""),
            ("suc_chua", "spawnQueueCapacity", "xe vừa chứa được", ""), ("eta_dich_s", "enemyRushETA", "giây địch tới bãi", "s"),
            ("eta_muc_tieu_s", "friendlyObjectiveETA", "giây tới mục tiêu gần nhất", "s"), ("co", "flags", "cờ G1", "")],
           [(f"{mid}/{d['spawn']}", mid, d) for mid, _i, d in _each(fair, "spawns")], "SpawnFairnessAudit.json")

    # ------------------------------------------------------------------ positions, staging
    _table(book, "Ban_do_vi_tri_chien_thuat", "Bản đồ: vị trí chiến thuật (spec J)",
           "Vị trí sinh ra: DirectFire / ArtilleryPocket / ReconObservation / HullDown (chỉ sau vật che thấp thật), điểm và các thành phần điểm",
           [("ma", "id", "id", ""), ("loai", "kind", "loại", ""), ("doi", "team", "đội (-1: cả hai)", ""), ("vi_tri", "position", "vị trí", "m"),
            ("doi_tuong", "subject", "mục tiêu / làn theo dõi", ""), ("diem", "score", "điểm", ""), ("thanh_phan", "terms", "thành phần điểm (JSON)", "")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(pos, "positions")], "TacticalPositions.json")
    _table(book, "Ban_do_khu_tap_ket", "Bản đồ: khu tập kết (spec I)",
           "Khu tập kết: sức chứa xe nhẹ / nặng, che chắn, phơi lộ, khoảng tới mục tiêu, số làn",
           [("ma", "id", "id", ""), ("doi", "team", "đội", ""), ("muc_tieu", "objective", "mục tiêu", ""), ("tam", "centre", "tâm", "m"),
            ("ban_kinh_m", "radius", "bán kính", "m"), ("chua_nhe", "capacityLight", "sức chứa xe nhẹ", ""), ("chua_nang", "capacityHeavy", "sức chứa xe nặng", ""),
            ("che_chan", "coverScore", "tỷ lệ ô cạnh vật che", "share"), ("phoi_lo", "threatExposure", "phơi lộ", "share"),
            ("toi_muc_tieu_m", "distanceToObjective", "khoảng tới mục tiêu", "m"), ("so_lan", "lanesAvailable", "số làn trong 25 m", "")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(pos, "staging")], "TacticalPositions.json")

    # ------------------------------------------------------------------ sea
    _table(book, "Ban_do_vung_ban_bo", "Bản đồ: vùng bắn từ bờ (spec K)",
           "Đoạn bờ quân mặt đất đứng tới được và khoảng tới làn tàu: 'không xuống nước' khác 'không ảnh hưởng mặt nước'",
           [("ma", "id", "id", ""), ("tp_mat_dat", "groundComponentId", "thành phần mặt đất", ""), ("tu_u", "fromU", "u đầu đoạn bờ", "m"),
            ("den_u", "toU", "u cuối", "m"), ("tam", "centre", "tâm", "m"), ("so_o", "cells", "số ô", ""), ("lan_gan", "nearestLane", "làn gần nhất", ""),
            ("toi_lan_min_m", "minDistanceToNavalLane", "khoảng tới làn gần nhất", "m"), ("toi_lan_max_m", "maxDistanceToNavalLane", "khoảng xa nhất", "m"),
            ("do_cao", "elevation", "độ cao (Sim phẳng: 0)", "m"), ("chat_luong_tam_nhin", "losQuality", "tỷ lệ tia tới làn không bị che", "share"),
            ("che_chan", "coverScore", "tỷ lệ ô cạnh vật che", "share"), ("tam_huu_ich_m", "maxUsefulWeaponRange", "tầm vũ khí quá mức này không thêm gì", "m")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(naval, "shoreFireRegions")], "NavalRouteAudit.json")
    _table(book, "Ban_do_tuyen_bien_dong_hoc", "Bản đồ: tuyến biển động học (spec L, N)",
           "Nút SeaRouteGraph: bề rộng, bán kính cua, chỗ ngang hai bên, cỡ tàu khuyên dùng, chỗ tránh, an toàn cho boss, phơi lộ từ bờ",
           [("ma", "id", "id nút", ""), ("loai", "kind", "Track / Holding / Exit", ""), ("lan", "lane", "làn", ""), ("vi_tri", "position", "vị trí", "m"),
            ("tp_bien", "component", "thành phần biển", ""), ("rong_m", "width", "bề rộng hành lang", "m"), ("ban_kinh_cua_m", "curveRadiusM", "bán kính cua (trống: thẳng)", "m"),
            ("cho_trai_m", "broadsideRoomLeft", "nước phía bờ", "m"), ("cho_phai_m", "broadsideRoomRight", "nước phía khơi", "m"),
            ("ban_kinh_tau_max_m", "maxRecommendedShipRadius", "bán kính thân tàu khuyên dùng", "m"), ("dai_tau_max_m", "maxRecommendedShipLength", "dài tàu khuyên dùng", "m"),
            ("cho_tranh", "passingAllowed", "có chỗ tránh / vượt", ""), ("vung_tranh", "passingBay", "nút chờ gần nhất", ""),
            ("an_toan_boss", "bossSafe", "an toàn cho mọi tàu boss", ""), ("phoi_lo_bo", "shoreThreatExposure", "khẩu đội và vùng bờ với tới", "")],
           [(f"{mid}/{d['id']}", mid, d) for mid, _i, d in _each(naval, "nodes")], "NavalRouteAudit.json")
    _table(book, "Ban_do_quay_tau", "Bản đồ: kiểm bán kính quay tàu (spec M)",
           "Mỗi tàu x thao tác (đổi làn, vào vịnh chờ, quay đầu cuối tuần tra, cua gắt): Rmin = tốc độ / tốc độ góc, cần = Rmin x hệ số an toàn, có, đạt / được giảm nhẹ",
           [("tau", "ship", "tàu", ""), ("boss", "boss", "là boss", ""), ("thao_tac", "manoeuvre", "thao tác", ""), ("o_dau", "where", "nút / làn", ""),
            ("toc_do_m_s", "speed", "tốc độ dữ liệu", "m/s"), ("quay_do_s", "turnRateDeg", "tốc độ quay", "deg/s"), ("rmin_m", "rmin", "Rmin", "m"),
            ("can_m", "required", "bán kính cần", "m"), ("co_m", "available", "bán kính tuyến cho", "m"), ("dat", "pass", "đạt", ""),
            ("giam_nhe", "mitigated", "bộ điều khiển xử lý (quay chậm / nhìn trước)", ""), ("ghi_chu", "note", "ghi chú", "")],
           [(f"{mid}/{d['ship']}/{d['manoeuvre']}/{d['where']}/{i}", mid, d) for mid, i, d in _each(naval, "turnAudit")], "NavalRouteAudit.json")

    # ------------------------------------------------------------------ warning registry
    _table(book, "Ban_do_canh_bao", "Bản đồ: sổ cảnh báo (spec U)",
           "Mọi cảnh báo bản đồ (bản kiểm tĩnh + GameplayTopology) với trạng thái OPEN / FIXED / ACCEPTED_INTENTIONAL / PLAYTEST_REQUIRED, người phụ trách và lý do "
           "(Docs/maps/map_warning_reviews.json; không tự sửa YELLOW)",
           [("ma", "warningId", "id cảnh báo", ""), ("muc", "severity", "RED / YELLOW / INFO", ""), ("ma_loai", "code", "mã", ""),
            ("chi_so", "metric", "chỉ số", ""), ("gia_tri", "value", "giá trị đo", ""), ("nguong", "threshold", "ngưỡng", ""),
            ("trang_thai", "status", "trạng thái", ""), ("phu_trach", "owner", "người phụ trách", ""), ("ly_do", "acceptedReason", "lý do", ""),
            ("phien_ban_xet", "lastReviewedVersion", "phiên bản xét gần nhất", ""), ("nguon_canh_bao", "source", "nguồn cảnh báo", "")],
           [(w["warningId"], w["warningId"].split(":")[0], w) for w in reg.get("warnings") or []], "MapWarningRegistry.json")

    # ------------------------------------------------------------------ objective approaches (spec H), acceptance (spec CI/BW/H/I), lane W2-A
    appr_rows = []
    for mid in sorted((appr.get("maps") or {})):
        for s in appr["maps"][mid].get("sets") or []:
            for r in s.get("routes") or []:
                d = dict(r)
                d["objective"] = s.get("objective")
                d["team"] = s.get("team")
                d["setId"] = s.get("id")
                d["artillerySupport"] = s.get("artillerySupport")
                d["defenderFallback"] = s.get("defenderFallback")
                appr_rows.append((f"{mid}/{s['id']}/{r['id']}", mid, d))
    _table(book, "Ban_do_tiep_can_muc_tieu", "Bản đồ: tuyến tiếp cận mục tiêu (spec H)",
           "Mỗi mục tiêu x đội tấn công: các tuyến tiếp cận riêng biệt với vai trò (Primary/Secondary/Flank/Shortest/Safest/HeavyCompatible), "
           "khu phủ pháo của đội tấn công, khu rút của đội phòng thủ",
           [("ma", "id", "id tuyến", ""), ("tap_hop", "setId", "id tập hợp tiếp cận (đội + mục tiêu)", ""), ("muc_tieu", "objective", "mục tiêu", ""),
            ("doi", "team", "đội tấn công", ""), ("vai_tro", "roles", "vai trò tuyến", ""), ("dai_m", "lengthM", "chiều dài", "m"),
            ("eta_s", "etaSeconds", "giây xe vừa đi hết", "s"), ("phoi_lo", "exposure", "tỷ lệ ô không có che (spec H)", "share"),
            ("rong_min_m", "minWidthM", "bề rộng hẹp nhất", "m"), ("hang_xe", "vehicleClassSupport", "hạng xe lớn nhất đi hết tuyến", ""),
            ("diem_nghen", "chokeIds", "điểm nghẽn trên tuyến", ""), ("lan", "laneId", "làn chiến thuật theo (trống: không)", ""),
            ("goc_toi_do", "arrivalBearingDeg", "góc tới mục tiêu (0 = +z, theo kim đồng hồ)", "deg"),
            ("khu_phao", "artillerySupport", "khu phủ pháo của đội tấn công (JSON)", ""), ("khu_rut", "defenderFallback", "khu rút của đội phòng thủ (JSON)", "")],
           appr_rows, "ObjectiveApproaches.json")

    acc_rows = []
    for mid in sorted((acc.get("maps") or {})):
        for r in acc["maps"][mid].get("rows") or []:
            acc_rows.append((f"{mid}/{r['row']}", mid, r))
    _table(book, "Ban_do_nghiem_thu", "Bản đồ: hàng nghiệm thu (spec CI bản đồ + BW + H + I)",
           "Mỗi hàng nghiệm thu bản đồ: đạt hay không, chi tiết khi trượt (Tools/maps/topogen Acceptance; cùng hàng với EditMode "
           "MapTopologyW1ATests / MapTopologyW2ATests)",
           [("dong", "row", "tên hàng nghiệm thu", ""), ("dat", "pass", "đạt", ""), ("chi_tiet", "detail", "chi tiết khi trượt", "")],
           acc_rows, "MapAcceptance.json")

    stress_rows = [(s["id"], s["map"], s) for s in stress.get("scenes") or []]
    _table(book, "Ban_do_canh_ap_luc", "Bản đồ: cảnh áp lực hiệu năng (spec BT)",
           "6 cảnh lặp lại (48v48 phố hẹp, 48v48 sa mạc mở, boss biển + hộ tống, công thành, bão thời tiết, mật độ xác xe tối đa); "
           "đo bản đồ ở đây (EditMode), đo dựng hình / âm thanh ở phần cuối (Unity play)",
           [("ma", "id", "id cảnh", ""), ("ten", "title", "tên", ""), ("che_do", "mode", "conquest / siege", ""),
            ("moi_ben", "perSide", "xe mỗi bên", ""), ("thoi_tiet", "weather", "thời tiết trình bày", ""),
            ("xac_xe", "wreckSeed", "số xác xe gieo", ""), ("tieu_diem", "focus", "loại tiêu điểm yêu cầu", ""),
            ("tieu_diem_giai", "focusResolved", "tiêu điểm đã giải trên bản đồ này", ""), ("tai_diem", "focusAt", "vị trí tiêu điểm", "m"),
            ("khoi_dong_s", "warmupSeconds", "giây khởi động bỏ qua", "s"), ("do_s", "seconds", "giây đo", "s"), ("seed", "seed", "seed", ""),
            ("cong_cu", "harness", "công cụ đo", "")],
           stress_rows, "STRESS_SCENES.json")

    # ------------------------------------------------------------------ terrain semantics, weather presentation
    g = topo.get("global") or {}
    _table(book, "Ban_do_ngu_nghia_dia_hinh", "Bản đồ: ngữ nghĩa địa hình (spec P)",
           "Mỗi tag địa hình: chi phí di chuyển (TerrainRules), bám đường, ngụy trang (rừng: 1 - forestSight), che mắt, che đạn thẳng (0: Sim không có), "
           "phơi pháo, hợp mìn, hull-down (0: mặt phẳng), phạt xe lớn; siêu dữ liệu, không buff chiến đấu",
           [(c, c, m, "") for c, m in (("movementCost", "chi phí di chuyển"), ("traction", "bám đường"), ("concealment", "ngụy trang"),
                                        ("visualCover", "che mắt"), ("directFireCover", "che đạn thẳng"), ("artilleryExposure", "phơi pháo"),
                                        ("mineSuitability", "hợp đặt mìn"), ("hullDownPotential", "tiềm năng hull-down"), ("largeVehiclePenalty", "phạt xe lớn"))],
           [(d["tag"], "*", d) for d in g.get("terrainSemantics") or []], "GameplayTopology.json")
    _table(book, "Thoi_tiet_trinh_bay", "Thời tiết: siêu dữ liệu trình bày (spec Q)",
           "Chỉ trình bày (sương, ánh sáng, mây, mưa, tuyết, gió, sét, bụi, vệt khói, chớp nòng, lọc thấp, tăng cảnh báo, hồ sơ âm thanh); hệ số tầm nhìn giữ ở Thoi_tiet",
           [(c, c, c, "") for c in ("fogDensity", "ambientLight", "cloudiness", "rainIntensity", "snowIntensity", "windStrength", "windDirectionDeg",
                                     "lightningIntensity", "dustIntensity", "contrailVisibility", "muzzleFlashVisibility", "lowpassEnvironmentAmount",
                                     "telegraphBoost", "ambientAudioProfile", "reverbProfile")],
           [(d["weather"], "*", d) for d in g.get("weatherPresentation") or []], "GameplayTopology.json")


# AI code that reads GameplayTopology instead of inferring geometry itself (lane W1-A).
CONSUMERS = [
    ("traffic_passages", "Sim/Movement/TrafficCoordinator.cs BuildPassages", "GameplayTopology.Chokes",
     "lối giao thông (cổng, nghẽn, cầu, đường hẹp) lấy từ điểm nghẽn chiến thuật; số đo chuyển nguyên từ BuildDoorways / BuildChokes"),
    ("feasibility_lane", "Sim/AI/EngagementFeasibility.cs Observed", "GameplayTopology.LaneStretch",
     "đoạn làn tàu tuần tra để chấm vùng phủ, quy tắc cũ chuyển sang lớp địa hình"),
    ("feasibility_size", "Sim/AI/EngagementFeasibility.cs Evaluate", "GameplayTopology.SizeClassReaches",
     "hạng xe phải lọt tuyến (maps.topology.sizeClassFeasibility, mặc định tắt: hành vi P0-B giữ nguyên)"),
    ("fire_support_parking", "Sim/AI/P2/FireSupportAnchor.cs Valid", "GameplayTopology.ParkingAllowed", "điểm neo pháo không đỗ ở cửa / miệng cửa"),
    ("fire_support_escape", "Sim/AI/P2/FireSupportAnchor.cs Score", "GameplayTopology.EscapeRoutes", "lối thoát 8 hướng, 12 m"),
    ("fire_support_traffic", "Sim/AI/P2/FireSupportAnchor.cs Score", "GameplayTopology.TransitConflict", "phạt đỗ trên tuyến chính / đường"),
    ("fire_support_transit_count", "Sim/AI/P2/FireSupportAnchor.cs Set", "MapTelemetry.AnchorSet", "đếm neo pháo, neo trong vùng cấm (spec BW 7)"),
]


def build_ai(ctx, book):
    s = book.sheet("AI_dia_hinh_tieu_thu", "AI: dùng địa hình chiến thuật",
                   "Mã AI đọc GameplayTopology (Sim/Navigation/GameplayTopology*.cs, lane W1-A) thay vì tự suy hình học", layer="C")
    s.col("ma_nguon", meaning="tệp / hàm AI")
    s.col("truong", meaning="trường / hàm GameplayTopology đọc")
    s.col("y_nghia", meaning="dùng để làm gì")
    for rid, code, field, meaning in CONSUMERS:
        r = s.row(rid, f"Assets/MachineBrigade/Scripts/{code.split(' ')[0]}")
        r.set("ma_nguon", code)
        r.set("truong", field)
        r.set("y_nghia", meaning)
