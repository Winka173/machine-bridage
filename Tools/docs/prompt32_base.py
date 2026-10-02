"""Prompt 32 L9: the design document's base-system sections, in Vietnamese and English, every number from balance.json
and the map files (no number written by hand): section 6 (the 22-tower roster and its branches, rebuilding and its
prices, walls, HQ types), section 7 (Defend and Endless by HQ level), Showdown, section 14 (starting CP and opening
squads). build_doc.py calls base_system before prompt32.ammo_handbook.

    python Tools/docs/prompt32_base.py > base.html   # the sections alone (a quick look; the PDF is build_doc.py's)
"""
from __future__ import annotations

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "balance"))
from p32_tower_prices import Model  # noqa: E402

MAPS = os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "MachineBrigade", "Resources", "Data", "maps")


def _table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table class='{cls}'><tr>{head}</tr>{body}</table>"


def _pct(x):
    return f"{x * 100:.1f}".rstrip("0").rstrip(".") + "%"


def _num(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _name(game, vid):
    if game:
        for v in game.get("vehicles", []):
            if v.get("id") == vid:
                return v.get("name", vid)
    return vid


def _walls_on_maps():
    maps = lines = segs = 0
    for f in sorted(os.listdir(MAPS)):
        if not f.endswith(".json"):
            continue
        text = open(os.path.join(MAPS, f), encoding="utf-8").read()
        m = json.loads(re.sub(r"^\s*//.*$", "", text, flags=re.M))
        if m.get("walls"):
            maps += 1
            lines += len(m["walls"])
            segs += sum(len(l["segments"]) for l in m["walls"])
    return maps, lines, segs


def base_system(game=None, h=None):
    esc = (h or {}).get("esc", html.escape)
    table = (h or {}).get("table", _table)
    m = Model()
    d, V = m.d, m.V
    b = d["base"]
    out = ["<div class='section'><h2>Hệ căn cứ (prompt 32) / The base system (prompt 32)</h2>",
           "<p>Sinh từ dữ liệu (balance.json, các file bản đồ). / Generated from the data (balance.json, the map files).</p>"]

    # 6a: the roster and the branches
    rows = []
    for card in b["roster"]:
        v = V.get(card, {})
        cells = [esc(_name(game, card)) + f" <small>({esc(card)})</small>", esc(v.get("fort", {}).get("size", "")), str(v.get("rebuildCp", "-"))]
        branches = v.get("branches", [])
        for i in range(2):
            if i < len(branches):
                bv = V.get(branches[i], {})
                cells.append(esc(_name(game, branches[i])) + f" <small>{esc(bv.get('towerRole', ''))}, {bv.get('rebuildCp', '-')} CP</small>")
            elif v.get("noBranch"):
                cells.append("<i>không nhánh / no branch</i> <small>" + esc(v.get("towerRole", "")) + "</small>")
            else:
                cells.append("-")
        rows.append(cells)
    out.append("<h3>6a. Roster 22 tháp và nhánh / The 22-tower roster and its branches</h3>")
    out.append(table(["Tháp / Tower", "Cỡ / Size", "Xây lại / Rebuild CP", "Nhánh A / Branch A", "Nhánh B / Branch B"], rows))
    out.append("<p>Hai nhánh của một tháp khác nhau về việc làm (towerRole riêng), không chỉ về số. / The two branches of a card "
               "differ in what they do (their own towerRole), not only in numbers.</p>")

    # 6b: rebuilding
    r = b["rebuild"]
    rows = [[esc(s), str(r[s]["cp"]), f"{r[s]['cooldown']} s", f"{r[s].get('drop', r.get('delay', 4))} s"] for s in ("small", "medium", "large")]
    out.append("<h3>6b. Xây lại tháp / Rebuilding towers</h3>")
    out.append(table(["Cỡ / Size", "Giá mặc định / Default CP", "Hồi / Cooldown", "Thả / Drop"], rows))
    radius, rescue, cutoff = r.get("enemyRadius", 20), int(r.get("hqRescue", 0.25) * 100), r.get("showdownCutoff", 600)
    out.append(f"<p>Không gọi khi xe địch trong {radius} m; nhà chính còn {rescue}% máu: tháp nhỏ hoặc vừa rẻ nhất đã đổ xây lại miễn phí, một "
               f"lần; Đối công: không xây lại sau {cutoff} s. Giá riêng từng tháp (rebuildCp) ở bảng 6a. / No drop with an enemy within {radius} m; "
               f"at {rescue}% HQ health the cheapest fallen small or medium tower comes back free, once; Showdown: no rebuilding after {cutoff} s. "
               f"Each tower's own price (rebuildCp) is in table 6a.</p>")

    # 6c: walls
    w = b["walls"]
    rows = []
    for key, t in w["types"].items():
        dv = V.get(t["def"], {})
        trade = ("cổng hẹp (đoạn thêm) / narrow gate (extra segment)" if t.get("extra")
                 else "một tháp nhỏ của căn cứ / one of the base's small towers" if t.get("gun") else "cổng rộng / wide gate")
        rows.append([esc(key), _num(float(t.get("durability", 1))), str(dv.get("hp", "-")), str(dv.get("armour", "-")), trade])
    maps, lines, segs = _walls_on_maps()
    slow = int(float(w.get("rubbleSlow", 0.2)) * 100)
    breaker = _num(float(w.get("breakerMultiplier", 1.5)))
    ai = ", ".join(f"{k} {v}" for k, v in w.get("ai", {}).items())
    out.append("<h3>6c. Tường / Walls</h3>")
    out.append(table(["Loại / Type", "Độ bền / Durability", "Máu đoạn / Segment hp", "Giáp / Armour", "Đánh đổi / Trade-off"], rows))
    out.append(f"<p>Tối đa {w.get('campLines', 2)} tuyến mỗi trại, {w.get('fortressLines', 3)} tuyến lùi ở Phòng thủ; 3-5 đoạn 12 x 2 m mỗi tuyến; "
               f"{maps} bản đồ, {lines} tuyến, {segs} đoạn. INTACT/RUBBLE theo trạng thái NavGrid dựng sẵn, đổi ở tick sau khi đoạn bị phá; gạch vụn đi "
               f"qua được, chậm {slow}%. Xe phá tường x{breaker} chỉ lên tường. Đội AI chọn cổng hay phá tường theo routeCost + threatCost + "
               f"breachTimeCost. AI địch: {esc(ai)}. / Up to {w.get('campLines', 2)} lines a camp, {w.get('fortressLines', 3)} fall-back lines in "
               f"Defend; 3-5 segments of 12 x 2 m a line; {maps} maps, {lines} lines, {segs} segments. INTACT/RUBBLE on prebuilt NavGrid states, "
               f"switched at the tick after a segment falls; rubble is passable, {slow}% slower. Wall breakers x{breaker} on walls only. AI squads "
               f"choose the gate or a breach by routeCost + threatCost + breachTimeCost (aiModeProfile wallRoute).</p>")

    # 6d: HQ types
    q = b["hqTypes"]
    rows = []
    for lvl in range(5):
        rows.append([str(lvl + 1), _pct(q["fortress"]["scale"][lvl]), _pct(q["fortress"]["airScale"][lvl]),
                     f"{int(q['garrison']['every'][lvl])} s, {q['garrison']['caps'][lvl]} CP", _pct(q["shield"]["scale"][lvl]), _pct(q["shield"]["dome"][lvl])])
    out.append("<h3>6d. Kiểu nhà chính / HQ types</h3>")
    out.append(table(["HQ", "Pháo đài (đất) / Fortress ground", "Pháo đài (PK) / Fortress AA", "Đồn trú / Garrison", "Lá chắn / Shield",
                      "Vòm khẩn / Dome"], rows))
    out.append(f"<p>Một kỹ năng, hồi {q.get('skillCooldown', 120)} s, một nút trên HUD. AI: {esc(', '.join(f'{k} {v}' for k, v in q.get('ai', {}).items()))}. "
               f"/ One skill, {q.get('skillCooldown', 120)} s cooldown, one HUD button.</p>")

    # 7: Defend and Endless by HQ level
    rows = [[str(ref["level"]), esc(", ".join(ref.get("small", []))), esc(", ".join(ref.get("medium", []))), esc(", ".join(ref.get("large", []))),
             esc(", ".join(ref.get("utilities", [])))] for ref in b.get("reference", [])]
    out.append("<h3>7. Phòng thủ / Vô tận theo cấp nhà chính / Defend and Endless by HQ level</h3>")
    out.append("<p>Sức đợt = ReferenceBasePower(cấp nhà chính) x độ khó x đường cong đợt x tiến độ chiến dịch. / Wave strength = "
               "ReferenceBasePower(HQ level) x difficulty x wave curve x campaign progress. Căn cứ tham chiếu / The reference bases:</p>")
    out.append(table(["HQ", "Nhỏ / Small", "Vừa / Medium", "Lớn / Large", "Mô-đun / Modules"], rows))

    # Showdown
    sd = d["matchRules"]["modes"].get("showdown")
    if sd:
        out.append("<h3>Chế độ Đối công / Showdown</h3>")
        out.append(table(["Trường / Field", "Luật / Rule"], [[esc(k), esc(v)] for k, v in sd.get("text", {}).items()]))
        out.append("<p>" + esc(", ".join(f"{k} {v}" for k, v in sd.get("numbers", {}).items())) + "</p>")
        out.append("<p>Bản đồ (300 x 300 đối xứng) / Maps (300 x 300 symmetric): " + esc(", ".join(sd.get("lists", {}).get("maps", []))) + ".</p>")

    # 14: starting CP and opening squads
    o = d["openingSquads"]
    sc = d["economy"]["startCp"]
    share = int(float(o.get("share", 0.6)) * 100)
    out.append("<h3>14. CP khởi đầu và đội mở màn / Starting CP and opening squads</h3>")
    out.append(f"<p>CP khởi đầu x{_num(float(sc['scale']))} ở {esc(', '.join(sc['modes']))}. Đội mở màn: mỗi vai lấy thẻ rẻ nhất của bộ bài, tối đa "
               f"{share}% CP khởi đầu. / Starting CP x{_num(float(sc['scale']))} in those modes; each role takes the deck's cheapest card of the role, "
               f"within {share}% of the starting CP.</p>")
    out.append(table(["Chỉ huy / Commander", "Vai / Roles"], [[esc(k), esc(", ".join(v) or "-")] for k, v in o.get("commanders", {}).items()]))
    out.append(table(["Tướng địch / Enemy general", "Vai / Roles"], [[esc(k), esc(", ".join(v) or "-")] for k, v in o.get("generals", {}).items()]))
    out.append("</div>")
    return "".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(base_system())
