"""The design document's prompt 29 section "Cân bằng đợt 2": the repriced cards (price, health, damage factor, drop
time), flares and APS by unit, and the Gungnir. Read straight from balance.json and the apply log, so it shows what the
data holds now (build_doc.py calls round2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Tools' / 'ai'))
import export_applied_xlsx as E  # noqa: E402  (balance.json without comments)

STATE = ROOT / 'Docs' / 'balance' / 'apply_state_p29.json'


def round2(game, h):
    esc, table = h['esc'], h['table']
    data = E.balance()
    tough = data['toughness']
    applied = set(json.loads(STATE.read_text(encoding='utf-8'))) if STATE.exists() else set()
    names = {v['id']: v.get('name', v['id']) for group in ('vehicles', 'elites', 'bosses') for v in game.get(group, [])}
    veh = {v['id']: v for v in data['vehicles']}
    rows = []
    for b in sorted(applied):
        if not b.startswith('B1-'):
            continue
        v = veh.get(b[3:])
        if not v:
            continue
        hp = round(v.get('hp', 0) * tough['vehicles'])
        rows.append([esc(names.get(v['id'], v['id'])), str(v.get('cp', '')), f"{hp:,}".replace(',', '.'),
                     f"{v.get('outgoingDamageMult', 1):.3f}".replace('.', ','), f"{v.get('dropDelay', 3.5):g}".replace('.', ',')])
    flares = [[esc(names.get(v['id'], v['id'])), str(v['flareCharges']), f"{v.get('flareRecharge', '') or 'theo kỹ năng'}"]
              for v in data['vehicles'] if v.get('flareCharges')]
    aps = [[esc(names.get(v['id'], v['id'])), esc(v.get('apsCapability', '—')), esc(v.get('interceptionMode', 'tự suy ra')),
            f"{v['aps'].get('charges', '')} / {v['aps'].get('recharge', v['aps'].get('reload', ''))} s / {v['aps'].get('radius', '')} m" if v.get('aps') else '—']
           for v in data['vehicles'] if v.get('aps') or 'apsCapability' in v]
    g = veh.get('rail_supergun', {})
    bomb = g.get('bombard', {})
    return ("<div class='section'><h2>Cân bằng đợt 2</h2>"
            "<p>Áp từ manifest của file cân bằng đợt 2 (bản v2) bằng <code>Tools/balance/p29_apply.py</code>; nhật ký ở "
            "<code>Docs/balance/apply_log_p29.md</code>. Máu hiển thị = máu dữ liệu × độ lì (2,2). Hệ số sát thương nhân mọi vũ khí "
            "của xe, không sửa vũ khí dùng chung.</p>"
            + table(['Xe', 'CP', 'Máu', 'Hệ số sát thương', 'Thả dù (s)'], rows, 'dps')
            + "<h3>Pháo sáng (số lần dự trữ)</h3><p>Hồi một lần khi ở vòng chờ, nạp đầy khi về Bãi đáp hoặc sở chỉ huy. "
              "Mồi bẫy nhiệt: +1 lần, hồi nhanh hơn 25%, chỉ cho đơn vị đã có pháo sáng.</p>"
            + table(['Đơn vị', 'Số lần', 'Hồi 1 lần (s)'], flares, 'dps')
            + "<h3>APS</h3><p>SELF_APS chỉ chặn tên lửa dẫn đường, drone, rốc-két bắn thẳng. Trophy: NONE không gắn; "
              "RETROFIT_ELIGIBLE 2 lần, hồi 20 s; BUILT_IN +1 lần, hồi ×0,75. Boss và tháp giữ số riêng.</p>"
            + table(['Thực thể', 'Khả năng', 'Chế độ', 'Lần / hồi / bán kính'], aps, 'dps')
            + "<h3>Gungnir</h3><p>Boss chủ lực chương 11: máu " + f"{round(g.get('hp', 0) * tough['bosses']):,}".replace(',', '.')
            + f"; siêu vũ khí mỗi {bomb.get('every', '?')} s, nhắm toàn bản đồ, cảnh báo {bomb.get('warn', 3)} s có đường ngắm; "
              f"xuyên tối đa {bomb.get('pierceMax', 5)} xe × " + f"{bomb.get('pierceDamage', 1000):,}".replace(',', '.') + " rồi nổ 2.000 ở xe cuối (lõi 12 m, rìa 20 m, giảm dần theo bảng giảm nổ lan); "
              "không bắn máy bay, không chặn được, pháo sáng và APS không có tác dụng.</p></div>")
