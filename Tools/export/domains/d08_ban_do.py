"""08_ban_do, layer A: the 100 map files (25 maps x 4 variants) with everything in them (drop zones, points, bases and
base cells, walls, fortress cells, edges, entry gates, terrain tags, landmarks, rails, sea routes, neutrals, props,
decor, roads, placed units), the base maps and biomes of map_dressing.json, prop types, neutral rules and weather."""
from __future__ import annotations

import re

from core.model import child_rows

from . import _balance as B
from . import _b08
from . import _lane_c as C

FILE_ID = "08_ban_do"
TITLE = "Bản đồ"
DESC = "100 file bản đồ (25 bản đồ x 4 biến thể): bãi thả, cứ điểm, căn cứ, tường, pháo đài, cạnh, cổng vào, tag địa hình, " \
       "địa danh, ray, tuyến biển, trung lập, vật thể, trang trí, đường, quân đặt sẵn; bản đồ gốc, biome, loại vật thể, thời tiết"

MAPS = C.DATA + "maps/"
DRESSING = C.DATA + "map_dressing.json"
VARIANTS = ("_conquest", "_long", "_sandbox", "_siege")  # Views/MapDressing.cs Modes
MAP_FK = ["08_ban_do/Ban_do"]


def _base_of(map_id: str) -> tuple[str, str]:
    for v in VARIANTS:
        if map_id.endswith(v):
            return map_id[: -len(v)], v[1:]
    return map_id, ""


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    camp = ctx.data(C.CAMPAIGN)
    dress = ctx.data(DRESSING) if DRESSING in ctx.sources else {}
    map_sids = sorted(s for s in ctx.sources if re.fullmatch(re.escape(MAPS) + r"[^/]+\.json", s))

    # ------------------------------------------------------------------ Ban_do (+ every child list)
    bd = book.sheet("Ban_do", "Bản đồ", "Mỗi file bản đồ một dòng (25 bản đồ x 4 biến thể conquest / long / sandbox / siege): "
                    "kích thước, chủ đề, viền, ô địa hình, đường biên, vòng công thành, pháo đài, biển, tuyến boss")
    bd.col("ban_do_goc", meaning="bản đồ gốc (map_dressing maps[].id)", fk=["08_ban_do/Ban_do_goc"])
    bd.col("bien_the", meaning="biến thể: conquest / long / sandbox / siege", enum=[v[1:] for v in VARIANTS])
    bd.col("tep", meaning="file nguồn")

    def sub(name, title, desc, parent=bd, **fk):
        s = book.sheet(name, title, desc, parent=parent)
        for col, targets in fk.items():
            s.col(col, fk=targets)
        return s

    vec = {"stop": ["x_m", "z_m"]}
    teams = sub("Ban_do_bai_tha", "Bản đồ: bãi thả", "teams[]: bãi thả quân của mỗi đội")
    points = sub("Ban_do_cu_diem", "Bản đồ: cứ điểm", "points[]: cứ điểm (tên, vị trí, bán kính)")
    outposts = sub("Ban_do_cu_diem_tien_don", "Cứ điểm: ô tiền đồn", "points[].outpost[]: ô tháp của tiền đồn", parent=points)
    units = sub("Ban_do_quan", "Bản đồ: quân đặt sẵn", "units[]: quân đặt sẵn lúc vào trận", **{"def": C.VEHICLE_FK})
    bases = sub("Ban_do_can_cu", "Bản đồ: căn cứ", "bases[]: căn cứ mỗi đội (nhà chính)")
    slots = sub("Ban_do_can_cu_o", "Căn cứ: ô", "bases[].slots[]: ô xây (loại, cỡ, hướng)", parent=bases)
    walls = sub("Ban_do_tuong", "Bản đồ: tuyến tường", "walls[]: tuyến tường (chủ, vòng, bán kính, cổng)")
    wsegs = sub("Ban_do_tuong_doan", "Tuyến tường: đoạn", "walls[].segments[]: đoạn tường (súng, thêm)", parent=walls)
    fslots = sub("Ban_do_phao_dai_o", "Pháo đài: ô", "fortress.slots[]: ô của căn cứ nhiều lớp (vòng, chỗ, cỡ)")
    segs = sub("Ban_do_canh", "Bản đồ: cạnh", "edges.segments[]: kiểu cạnh (edgeType), biến đổi (edgeModifier), bờ")
    corners = sub("Ban_do_goc_canh", "Bản đồ: góc cạnh", "edges.corners[]: góc nối hai cạnh")
    links = sub("Ban_do_lien_ket_canh", "Bản đồ: lối ra cạnh", "edges.links[]: đường / ray / biển ra khỏi bản đồ")
    gates = sub("Ban_do_cong_vao", "Bản đồ: cổng vào", "entryGates[]: cổng vào (vị trí, hướng vào, visualIngress, ray)")
    tags = sub("Ban_do_tag_dia_hinh", "Bản đồ: tag địa hình", "terrain.zones[].rects: mỗi hình chữ nhật một dòng (x0, z0, x1, z1)")
    lms = sub("Ban_do_dia_danh", "Bản đồ: địa danh", "landmarks[]: landmarkId, tên Việt / Anh, bí danh, vị trí")
    neutrals = sub("Ban_do_trung_lap", "Bản đồ: trung lập", "neutrals[]: loại, vị trí (luật: Trung_lap_luat)")
    props = sub("Ban_do_vat_the", "Bản đồ: vật thể", "props[]: mỗi vật thể một dòng (loại, vị trí, xoay, trung lập)",
                **{"def": ["08_ban_do/Vat_the_loai"]})
    decor = sub("Ban_do_trang_tri", "Bản đồ: trang trí", "decor[]: vật trang trí (không lối chơi)")
    roads = sub("Ban_do_duong", "Bản đồ: đường", "roads[]: đường (điểm x;z nối tiếp, rộng)")
    rails = sub("Ban_do_rail", "Bản đồ: ray", "rails[]: RailSpline (điểm, đoạn chơi, chỗ cắt đường)")
    xings = sub("Ban_do_rail_giao_cat", "Ray: chỗ cắt đường", "rails[].crossings[]", parent=rails)
    nodes = sub("Ban_do_tuyen_bien", "Bản đồ: tuyến biển (nút)", "seaRoutes.nodes[]: SeaRouteGraph nút (làn, kiểu)")
    sroutes = sub("Ban_do_tuyen_bien_doan", "Tuyến biển: đoạn", "seaRoutes.segments[]: đoạn nối hai nút")
    batts = sub("Ban_do_bien_phao", "Biển: khẩu đội bờ", "sea.batteries[]")
    lands = sub("Ban_do_bien_do_bo", "Biển: điểm đổ bộ", "sea.landings[]")
    lanes = sub("Ban_do_bien_lan", "Biển: làn tàu", "sea.lanes[]")
    sroutes.col("nut_a", meaning="nút đầu (<bản đồ>/<nút>)", fk=["08_ban_do/Ban_do_tuyen_bien"])
    sroutes.col("nut_b", meaning="nút cuối (<bản đồ>/<nút>)", fk=["08_ban_do/Ban_do_tuyen_bien"])
    for c in ("x0_m", "z0_m", "x1_m", "z1_m"):
        tags.col(c, unit="m", meaning="góc hình chữ nhật (TerrainTags.cs: x0, z0, x1, z1)")
    tags.col("tag", meaning="tag địa hình")

    def tag_rows(row, zones, src, path):
        for zi, z in enumerate(zones):
            zp = path + (zi,)
            rects = z.get("rects") or []
            others = {k: v for k, v in z.items() if k not in ("rects",)}
            n = max(1, len(rects) // 4)
            for q in range(n):
                r = tags.row(f"{row.id}/{zi}/{q}", C.nguon(src, zp + ("rects",)), raw=rects[q * 4: q * 4 + 4])
                r.set(tags.parent_col, row.id)
                r.set("thu_tu", zi)
                for k, v in others.items():
                    C.scalar_or_list(r, k if k == "tag" else f"vung_{k}", v, src, zp + (k,))
                if not rects:
                    r.set("x0_m", "", src, zp + ("rects",))
                for c, name in enumerate(("x0_m", "z0_m", "x1_m", "z1_m")):
                    i = q * 4 + c
                    if i < len(rects):
                        r.set(name, rects[i], src, zp + ("rects", i))

    def ids_of(sheet):
        # child with a parent-scoped id: ids repeat across the 4 variants of a map
        return lambda row, items, src, p: child_rows(sheet, row, items, src, p)

    children = {
        "teams": ids_of(teams), "units": ids_of(units),
        "points": lambda row, items, src, p: child_rows(points, row, items, src, p, children={"outpost": ids_of(outposts)}),
        "bases": lambda row, items, src, p: child_rows(bases, row, items, src, p, children={"slots": ids_of(slots)}),
        "walls": lambda row, items, src, p: child_rows(walls, row, items, src, p, children={"segments": ids_of(wsegs)}),
        "fortress.slots": ids_of(fslots),
        "edges.segments": ids_of(segs), "edges.corners": ids_of(corners), "edges.links": ids_of(links),
        "entryGates": ids_of(gates), "terrain.zones": tag_rows, "landmarks": ids_of(lms), "neutrals": ids_of(neutrals),
        "props": ids_of(props), "decor": ids_of(decor), "roads": ids_of(roads),
        "rails": lambda row, items, src, p: child_rows(rails, row, items, src, p, children={"crossings": ids_of(xings)}),
        "seaRoutes.nodes": ids_of(nodes), "seaRoutes.segments": ids_of(sroutes),
        "sea.batteries": ids_of(batts), "sea.landings": ids_of(lands), "sea.lanes": ids_of(lanes),
    }
    summary = []
    for sid in map_sids:
        m = ctx.data(sid)
        mid = m.get("id") or sid.rsplit("/", 1)[-1][:-5]
        base, variant = _base_of(mid)
        r = bd.row(mid, sid, raw=m)
        r.set("ban_do_goc", base)
        r.set("bien_the", variant)
        r.set("tep", sid.rsplit("/", 1)[-1])
        r.flatten(m, sid, (), children=children, vectors=vec)
        summary.append((mid, sid, m))

    # node ids of the sea graph are per map: nut_a / nut_b point at the node rows (<map>/<node id>)
    for r in sroutes.rows.values():
        for c in ("a", "b"):
            v = r.values.get(c)
            r.set(f"nut_{c}", f"{r.values[sroutes.parent_col]}/{v}" if v not in (None, "") else "")
    # ------------------------------------------------------------------ Ban_do_cu_diem_bai_tha_can_cu (counts)
    tom = book.sheet("Ban_do_cu_diem_bai_tha_can_cu", "Bản đồ: cứ điểm, bãi thả, căn cứ, tường (đếm)",
                     "Mỗi bản đồ: số cứ điểm, bãi thả, căn cứ, ô căn cứ, tuyến tường, ô pháo đài, cổng vào, vật thể (đếm từ "
                     "các sheet con)")
    tom.col("ban_do", meaning="bản đồ", fk=MAP_FK)
    for mid, sid, m in summary:
        r = tom.row(mid, sid)
        r.set("ban_do", mid)
        r.set("so_cu_diem", len(m.get("points") or []))
        r.set("so_bai_tha", len(m.get("teams") or []))
        r.set("so_can_cu", len(m.get("bases") or []))
        r.set("so_o_can_cu", sum(len(b.get("slots") or []) for b in m.get("bases") or []))
        r.set("so_tuyen_tuong", len(m.get("walls") or []))
        r.set("so_o_phao_dai", len((m.get("fortress") or {}).get("slots") or []))
        r.set("so_cong_vao", len(m.get("entryGates") or []))
        r.set("so_lan_ra_canh", len((m.get("edges") or {}).get("links") or []))
        r.set("so_vat_the", len(m.get("props") or []))

    # ------------------------------------------------------------------ map_dressing.json
    bg = book.sheet("Ban_do_goc", "Bản đồ gốc", "map_dressing.json maps[]: 25 bản đồ gốc (biome, mật độ, đồi, hào, seed)")
    bg.col("biome", fk=["08_ban_do/Ban_do_biome"])
    bg.col("bien_the", meaning="file bản đồ của bản đồ gốc (ngăn ';')", fk=MAP_FK)
    for r, _x, _p in C.records(bg, dress.get("maps"), DRESSING, ("maps",)):
        r.set("bien_the", ";".join(mid for mid, _s, _m in summary if _base_of(mid)[0] == r.id))
    bm = book.sheet("Ban_do_biome", "Biome", "map_dressing.json biomes[]: dải, vòng, bộ trang trí theo vùng")
    C.records(bm, dress.get("biomes"), DRESSING, ("biomes",))
    dm = book.sheet("Ban_do_dia_danh_mo_hinh", "Địa danh: mô hình", "map_dressing.json landmarks[]: mô hình địa danh, vị trí, xoay, tỷ lệ")
    dm.col("map", fk=MAP_FK)
    for i, lm in enumerate(dress.get("landmarks") or []):
        r = dm.row(f"{lm.get('map', '')}/{lm.get('id', i)}", C.nguon(DRESSING, ("landmarks", i)), raw=lm)
        r.flatten(lm, DRESSING, ("landmarks", i), aliases={"id": "id_goc"})
    tl = book.kv_sheet("Ban_do_trang_tri_luat", "Trang trí: luật", "map_dressing.json camera, edges, version")
    book.kv_rows(tl, {k: v for k, v in dress.items() if k not in ("maps", "biomes", "landmarks")}, DRESSING, (), "map_dressing")

    # ------------------------------------------------------------------ prop types, neutral rules, weather
    vl = book.sheet("Vat_the_loai", "Loại vật thể", "balance.json props[]: máu, giáp, kích thước, chặn đường / đạn, nổ khi vỡ")
    C.records(vl, d.get("props"), B.BALANCE, ("props",))
    neu = d.get("neutrals") or {}
    nl = book.kv_sheet("Trung_lap_luat", "Trung lập: luật", "balance.json neutrals: số liệu (bán kính, thời gian chiếm, sửa, nổ) và loại theo chế độ")
    book.kv_rows(nl, neu, B.BALANCE, ("neutrals",), "neutrals")
    tt = book.sheet("Thoi_tiet", "Thời tiết", "campaign.json eventLibrary.rules.weatherSight (hệ số tầm nhìn) và số nhiệm vụ dùng")
    tt.col("he_so_tam_nhin", meaning="hệ số tầm nhìn (weatherSight)")
    tt.col("so_nhiem_vu", meaning="số nhiệm vụ có thời tiết này (missions[].weather)")
    sight = ((camp.get("eventLibrary") or {}).get("rules") or {}).get("weatherSight") or {}
    uses: dict[str, int] = {}
    for m in camp.get("missions") or []:
        uses[m.get("weather", "")] = uses.get(m.get("weather", ""), 0) + 1
    for w in sorted(set(sight) | {k for k in uses if k}):
        r = tt.row(w, C.nguon(C.CAMPAIGN, ("eventLibrary", "rules", "weatherSight", w)))
        if w in sight:
            r.set("he_so_tam_nhin", sight[w], C.CAMPAIGN, ("eventLibrary", "rules", "weatherSight", w))
        r.set("so_nhiem_vu", uses.get(w, 0))

    # ------------------------------------------------------------------ layer B (lane B, pass 5 part 2)
    _b08.build(ctx, book)
