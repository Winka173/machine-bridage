"""The design document's prompt 33 part of section 15 (DECISIONS "Prompt 33 L2 view / L7"): the four zones, the edge types
per battlefield, the terrain tags, the landmarks, the rails, the sea routes and the twelve validators' results. Read from
the map files, map_dressing.json and Tools/maps/validate_p33.py's last full run (Docs/maps/validate_p33.json; a quick
run when there is none), so the document shows what the data holds (build_doc.py calls section15).

    python Tools/docs/prompt33.py > out.html     # the section alone, for a look
"""
from __future__ import annotations

import html
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Tools' / 'maps'))

import check_access as ca  # noqa: E402

DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
MAPS = DATA / 'maps'
DRESSING = DATA / 'map_dressing.json'
RESULTS = ROOT / 'Docs' / 'maps' / 'validate_p33.json'

TYPE_VI = {'LAND': 'đất', 'SEA': 'biển', 'RIVER': 'sông', 'CLIFF': 'vách', 'URBAN': 'đô thị'}
MOD_VI = {'HARBOR': 'cảng', 'INDUSTRIAL': 'công nghiệp', 'URBAN': 'đô thị'}
SHORE_VI = {'BEACH': 'bãi', 'CLIFF': 'vách', 'QUAY': 'cầu cảng'}
TAG_VI = [
    ('ROAD', 'Đường', 'tốc độ +20 %'),
    ('ROUGH', 'Gồ ghề', 'tốc độ −15 % (đô thị, đổ nát, sỏi đá; chỗ nấp vẫn do nhà / vật thể)'),
    ('FOREST', 'Rừng', 'tốc độ −25 %; tầm nhìn của địch lên xe trong rừng ×0,7'),
    ('SHALLOW_WATER', 'Nước nông', 'xe thường −50 %; xe lội nước và đệm khí không chậm'),
]
CHECK_VI = {
    1: 'Kiểu cạnh khớp vành ngoài (không nhà / rừng phía biển)',
    2: 'Vành ngoài phủ khung camera mọi tỷ lệ, không khoảng trống thế giới',
    3: 'Vật trang trí không collider, không vào hệ tầm nhìn',
    4: 'Không vật thể lối chơi trong dải viền',
    5: 'Đường bộ, ray, sông, bờ biển, tuyến biển liên tục ra ngoài',
    6: 'Mọi viện quân kịch bản có cổng vào',
    7: 'check_access.py pass (khoảng trống xe lớn)',
    8: 'Vùng tag địa hình hợp lệ (không chồng, không rỗng)',
    9: 'Kết nối RailSpline và SeaRouteGraph',
    10: 'Chỗ cắt đường ray cảnh báo ≥ mức tối thiểu',
    11: 'Không điểm nghẽn đơn khóa quá ~nửa bản đồ',
    12: 'Thời điểm đi vào (viện quân, tàu hỏa, tàu biển) cố định',
}


def _esc(s):
    return html.escape(str(s))


def _table(head, rows):
    h = ''.join(f'<th>{_esc(c)}</th>' for c in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


def _maps():
    return {f.stem: ca.load(f) for f in sorted(MAPS.glob('*.json'))
            if f.stem.rsplit('_', 1)[-1] in ('conquest', 'sandbox', 'siege', 'long')}


def _side_text(m, side):
    parts = []
    for s in m['edges']['segments']:
        if s['side'] != side:
            continue
        t = TYPE_VI.get(s['type'], s['type'])
        extra = [MOD_VI[s['modifier']]] if s.get('modifier') else []
        if s.get('shore'):
            extra.append(SHORE_VI.get(s['shore'], s['shore']))
        parts.append(t + (f" ({', '.join(extra)})" if extra else ''))
    out = []
    for p in parts:
        if not out or out[-1] != p:
            out.append(p)
    return ' / '.join(out)


def _results():
    if RESULTS.exists():
        return json.loads(RESULTS.read_text(encoding='utf-8')), 'lần chạy đầy đủ gần nhất'
    import validate_p33 as v  # noqa: E402
    return [r.as_dict() for r in v.run(quick=True, verbose=False)], 'chạy nhanh (không gồm mục 7 và 11)'


def section15(game, h=None):
    esc = (h or {}).get('esc', _esc)
    table = (h or {}).get('table', _table)
    names = {m['id']: m['name'] for m in game.get('maps', [])} if game else {}
    maps = _maps()
    dressing = json.loads(DRESSING.read_text(encoding='utf-8'))
    cam = dressing['camera']
    out = ["<h3>15g. Bốn vùng, kiểu cạnh, địa hình, địa danh, đường ray, tuyến biển (prompt 33)</h3>"]

    # The four zones.
    out.append("<h4>Bốn vùng của bản đồ</h4>")
    out.append(table(['Vùng', 'Ở đâu', 'Nội dung', 'Lối chơi'], [
        ['1. Vùng chơi', 'hình chữ nhật của bản đồ', 'navmesh, cứ điểm, căn cứ, tháp, chỗ nấp, vật chặn tầm nhìn, tag địa hình', 'Có'],
        ['2. Dải viền', '12–20 m ngoài mép (theo bản đồ)', 'chuyển cảnh: gờ đất, mương, vách, bãi, mép nước, góc dựng sẵn', 'Không'],
        ['3. Vành ngoài', f"{cam['ringSquare']:.0f} m quanh bản vuông; {cam['ringLongSide']:.0f} / {cam['ringLongEnd']:.0f} m "
                          "bên / đầu bản dài", 'trang trí instancing theo seed cố định; nửa xa dùng HLOD', 'Không; không collider, không chặn tầm nhìn'],
        ['4. Chân trời', 'ngoài vành', 'dãy núi thô, biển xa, đảo mờ, tàu xa, mặt đất chân trời, sương', 'Không'],
    ]))
    out.append(f"<p>Bề rộng vành = khung nhìn camera lớn nhất (trực giao, nghiêng {cam['tiltDegrees']:.0f}°, zoom xa nhất "
               f"{cam['maxZoomSquare']:.0f} / {cam['maxZoomLong']:.0f}, tỷ lệ 4:3, 16:9, 20:9, camera không xoay) + 15 %: tầm với "
               f"{cam['reachSquare']:.1f} m (vuông), {cam['reachLongSide']:.1f} / {cam['reachLongEnd']:.1f} m (dài).</p>")

    # Edge types per battlefield (the conquest file, the long file where it differs).
    out.append("<h4>Kiểu cạnh (edgeType) theo chiến trường</h4><p>Phía BIỂN: mặt nước tới chân trời, sóng, bóng tàu xa, đảo mờ, "
               "không nhà, rừng, đất; bờ chuyển tiếp theo kiểu bờ (bãi: dải sóng vỗ; vách: đá trụ; cầu cảng: tường kè, cần cẩu, "
               "container). SÔNG chảy tiếp ra ngoài; VÁCH dựng thành vách đá; ĐÔ THỊ là thành phố của theme. Góc giao giữa hai "
               "kiểu dùng 10 tài sản góc dựng sẵn. Đường bộ, ray (tới cửa hầm), sông, bờ biển và tuyến biển (phao) kéo dài ra "
               "vành ngoài.</p>")
    rows = []
    pieces = Counter()
    for stem, m in maps.items():
        for c in m['edges']['corners']:
            pieces[c['piece']] += 1
        if not stem.endswith('_conquest'):
            continue
        fam = stem[:-len('_conquest')]
        sides = [_side_text(m, s) for s in ('N', 'E', 'S', 'W')]
        rows.append([esc(names.get(fam, fam))] + [esc(s) for s in sides])
    out.append(table(['Chiến trường', 'Bắc', 'Đông', 'Nam', 'Tây'], rows))
    out.append("<p>Tài sản góc (số lần trong 100 file): " + ', '.join(f"{esc(k)} {v}" for k, v in pieces.most_common()) + ".</p>")

    # Terrain tags.
    cells = Counter()
    total = 0
    for m in maps.values():
        x0, z0, x1, z1 = (m['bounds'] if m.get('bounds') else (-m['size'] / 2, -m['size'] / 2, m['size'] / 2, m['size'] / 2))
        total += (x1 - x0) * (z1 - z0)
        for zone in m.get('terrain', {}).get('zones', []):
            flat = zone['rects']
            cells[zone['tag']] += sum((flat[i + 2] - flat[i]) * (flat[i + 3] - flat[i + 1]) for i in range(0, len(flat), 4))
    out.append("<h4>Tag địa hình</h4>")
    out.append(table(['Tag', 'Tên', 'Tác dụng', 'Phủ (cả 100 file)'],
                     [[t, esc(n), esc(e), f"{cells[t] / total * 100:.1f} %".replace('.', ',')] for t, n, e in TAG_VI]))
    out.append("<p>Chi phí đường tĩnh theo tag (không đổi theo tick). DEEP_FORD để sau: bộ tìm đường chưa có chi phí theo loại xe.</p>")

    # Landmarks.
    spots = defaultdict(dict)
    for lm in dressing.get('landmarks', []):
        spots[lm['map']][lm['id']] = lm
    rows = []
    for stem, m in maps.items():
        if not stem.endswith('_conquest'):
            continue
        fam = stem[:-len('_conquest')]
        cells_ = []
        for lm in m.get('landmarks', []):
            label = esc(lm['name']['vi'])
            if lm.get('model'):
                label += ' <span class="muted">(mô hình trang trí)</span>'
            cells_.append(label)
        rows.append([esc(names.get(fam, fam))] + [' · '.join(cells_)])
    out.append("<h4>Địa danh</h4><p>Mỗi chiến trường 3 địa danh (landmarkId, tên song ngữ, khớp thoại prompt 30). Địa danh không có "
               "vật thể trên bản đồ được dựng bằng mô hình trang trí (không collider) ở chỗ trống gần nhất, tránh cứ điểm, đường, "
               "ray, cổng.</p>")
    out.append(table(['Chiến trường', 'Địa danh'], rows))

    # Rails and sea routes.
    rows = []
    for stem, m in maps.items():
        for r in m.get('rails', []):
            pts = list(zip(r['points'][0::2], r['points'][1::2]))
            length = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** .5 for a, b in zip(pts, pts[1:]))
            rows.append([esc(stem), esc(r['id']), f"{length:.0f} m", f"{r.get('playTo', length) - r.get('playFrom', 0):.0f} m",
                         str(len(r.get('crossings', [])))])
    out.append("<h4>Đường ray (RailSpline)</h4><p>Lớp riêng, không phải navmesh: từ cửa hầm ngoài bản đồ qua dải viền, cổng vào, tới "
               "điểm dừng; Juggernaut, Nemesis, Gungnir và tàu chi viện Công thành chạy trên ray. Chỗ cắt đường bộ: MỞ → CẢNH BÁO "
               "(≥ 4 s) → ĐÓNG → TÀU QUA → MỞ.</p>")
    out.append(table(['File', 'Tuyến', 'Dài', 'Trong vùng chơi', 'Chỗ cắt'], rows))
    rows = []
    for stem, m in maps.items():
        g = m.get('seaRoutes')
        if g:
            kinds = Counter(n.get('kind') for n in g['nodes'])
            rows.append([esc(stem), str(len(g['nodes'])), str(kinds.get('holding', 0)), str(kinds.get('exit', 0)), str(len(g['segments']))])
    out.append("<h4>Tuyến tàu biển (SeaRouteGraph)</h4><p>Tàu lớn đi trên đồ thị tuyến (đoạn, nút, vịnh tránh), giữ đoạn hiện tại và "
               "đoạn kế, khoảng cách tối thiểu nửa thân tàu này + nửa thân tàu trước + 10 m, ưu tiên cố định.</p>")
    out.append(table(['File', 'Nút', 'Nút chờ', 'Lối ra', 'Đoạn'], rows))

    # The validators.
    results, how = _results()
    rows = [[str(r['check']), esc(CHECK_VI.get(r['check'], r['name'])), str(r['checked']), str(len(r['errors'])),
             str(len(r['warnings']))] for r in results]
    out.append(f"<h4>12 validator (Tools/maps/validate_p33.py, {esc(how)})</h4>")
    out.append(table(['#', 'Kiểm', 'Số mục', 'Lỗi', 'Cảnh báo'], rows))
    out.append("<p>Ảnh mép bản đồ ở zoom xa nhất cho mỗi biome: cần ảnh chụp từ Unity (ghi trong LOCAL_TODO).</p>")
    return ''.join(out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print(section15({}))
