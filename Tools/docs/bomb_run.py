"""The design document's "Ném bom rải thảm" section (the bomb-run fix, Docs/prompts/bomb_run_vi.txt pass 4; DECISIONS "Ném bom
rải thảm"). Every number is read from the data, never written by hand: the stick block of each bomb weapon in balance.json
(weapons[*].stick, after inherits), the carriers from the ExportGameDoc export (game.json), the before / after drop traces of
Docs/export/bom_2026-10-03 (Tools/export/bom.py compare_rows: before = vet_tha_truoc_luot2.csv, the pass 0 trace; after =
vet_tha_unity.csv, the Unity trace after the fix) and the stick pictures of EffectShots.FxBatch.

    build_doc.py calls section(game, h, imgdir).
    python Tools/docs/bomb_run.py > out.html      # the section alone, for a look (no pictures, no carriers)

Images (build_doc's image dir; a missing one is a grey "shot pending" box naming the file it waits for):
    <img>/fx/stick_heavy_bomber/before_impact_0s.png, before_impact_1s.png, before_impact_3s.png, after_impact_0s.png,
        after_impact_1s.png, after_impact_3s.png; the same under fx/stick_command_airship/
        (MachineBrigade.Editor.EffectShots.FxBatch -mbFxIds sticks: Assets/MachineBrigade/Scripts/Editor/EffectShots.Sticks.cs)
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Tools' / 'export'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import fix_full  # noqa: E402

BALANCE = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json'
MOMENTS = ('0', '1', '3')
SUBJECTS = (('stick_heavy_bomber', 'Oanh tạc cơ chiến lược (bomber_payload, 7 × FAB-500)'),
            ('stick_command_airship', 'Khí cầu chỉ huy, khoang bom chính (p26_roc_main_roc_bombs, 8 × 400 kg)'))
MODE_VI = {'STICK': 'rải thảm', 'POINT': 'một điểm', 'PATTERN': 'hình khác'}
DROP_VI = {'OVERFLY': 'bay qua, rơi tự do', 'BAY': 'khoang boss, quanh điểm nhắm'}
HEADING_VI = {'APPROACH': 'hướng vào', 'AXIS': 'trục chính cụm'}
WARN_VI = {'NONE': 'không', 'RING': 'vòng', 'STICK_RECT': 'chữ nhật cả dải'}
FORMATION_VI = {'hang_doc_8m': 'hàng dọc 8 m', 'cum_8m': 'cụm 8 m'}


def _e(s):
    return html.escape(str(s if s is not None else ''))


def _weapons():
    """{id: resolved weapon dict} for every weapon with a stick block (inherits followed for the stick and the burst)."""
    from core import jsonc
    data = jsonc.loads(BALANCE.read_text(encoding='utf-8-sig'))
    by_id = {w['id']: w for w in data.get('weapons', [])}

    def field(w, key, seen=()):
        if key in w or not w.get('inherits') or w['inherits'] in seen:
            return w.get(key)
        return field(by_id.get(w['inherits'], {}), key, seen + (w['id'],))

    out = {}
    for wid, w in by_id.items():
        stick = field(w, 'stick')
        if stick:
            out[wid] = {'stick': stick, 'burst': field(w, 'burst'), 'real': field(w, 'real'), 'warheadKg': field(w, 'warheadKg')}
    return out


def _carriers(game):
    if not game:
        return {}
    try:
        return {wid: owners for wid, (_, owners, _) in fix_full.game_weapons(game).items()}
    except (KeyError, TypeError, ValueError):
        return {}


def card_words(stick: dict) -> str:
    """The aircraft card's words for a stick, as StickLines.Words writes them (Vietnamese)."""
    n = int(stick.get('bombs') or 0)
    spacing = float(stick.get('spacing') or 0)
    return f"thả {n} quả, cách nhau {fix_full._n(spacing, 1)} m, dải {fix_full._n(max(0, n - 1) * spacing, 1)} m"


def parameter_table(game, h):
    weapons = _weapons()
    carriers = _carriers(game)
    head = ['Vũ khí', 'Mang bởi', 'Chế độ', 'Cách thả', 'n', 'Khoảng (m)', 'Dải (m)', 'Nhịp (s)', 'Tốc độ thả (m/s)', 'Rơi (s)',
            'Dẫn đầu (m)', 'Hướng dải', 'Tâm', 'Lõi / khoảng', 'Rộng (m)', 'An toàn (m)', 'Bay thẳng (s)', 'Cảnh báo', 'Thẻ']
    rows = []
    for wid in sorted(weapons, key=lambda k: (weapons[k]['stick'].get('mode') != 'STICK', k)):
        s = weapons[wid]['stick']
        laid = s.get('mode') == 'STICK' and int(s.get('bombs') or 0) > 1
        owners = carriers.get(wid) or []
        rows.append([f"<code>{_e(wid)}</code>" + (f"<br><span class='muted'>{_e(weapons[wid]['real'])}</span>" if weapons[wid].get('real') else ''),
                     _e(', '.join(owners[:4]) + (' …' if len(owners) > 4 else '')) or '—',
                     _e(MODE_VI.get(s.get('mode'), s.get('mode'))), _e(DROP_VI.get(s.get('drop'), s.get('drop'))),
                     str(s.get('bombs', '')), fix_full._n(s.get('spacing'), 1), fix_full._n(s.get('length'), 1),
                     fix_full._n(s.get('interval'), 3), fix_full._n(s.get('releaseSpeed'), 1), fix_full._n(s.get('fallTime'), 2),
                     fix_full._n(s.get('lead'), 1), _e(HEADING_VI.get(s.get('heading'), s.get('heading'))),
                     'giữa' if s.get('anchor') == 'CENTER' else 'đầu', fix_full._n(s.get('overlap'), 2), fix_full._n(s.get('width'), 1),
                     fix_full._n(s.get('safety'), 1), fix_full._n(s.get('straightTime'), 2),
                     _e(WARN_VI.get(s.get('warnShape'), s.get('warnShape'))), _e(card_words(s)) if laid else '—'])
    return fix_full._table(h, head, rows)


def compare_table(h):
    import bom
    before = bom.read_trace(ROOT / bom.BEFORE)
    after = bom.read_trace(ROOT / bom.AFTER)
    if not before or not after:
        return f"<div class='pending'><div>chờ vết thả</div><code>{_e(bom.BEFORE)} / {_e(bom.AFTER)}</code></div>"
    header, rows = bom.compare_rows(before, after)
    head = ['Vũ khí / đơn vị', 'Số bom', 'Điểm rơi khác nhau', 'Độ dài dải (m)']
    for f in bom.COMPARE_FORMATIONS:
        head.append(f"Xe trúng, {FORMATION_VI.get(f.lower(), f)} (/5)")
    out = []
    for r in rows:
        d = dict(zip(header, r))
        if d['so_bom'] in ('', None) or float(d['so_bom'] or 0) < 2:
            continue  # a single bomb: no stick, nothing changed
        line = [f"<code>{_e(d['vu_khi_id'])}</code> / {_e(d['don_vi_id'])}", fix_full._n(d['so_bom'], 0)]
        line += [' → '.join(fix_full._ba(d['diem_roi_truoc'], d['diem_roi_sau'], 1))]
        line += [' → '.join(fix_full._ba(d['do_dai_dai_truoc_m'], d['do_dai_dai_sau_m'], 1))]
        for f in bom.COMPARE_FORMATIONS:
            k = f.lower()
            line.append(' → '.join(fix_full._ba(d[f'xe_trung_{k}_truoc'], d[f'xe_trung_{k}_sau'], 1)))
        out.append(line)
    return fix_full._table(h, head, out)


def pictures(h, imgdir):
    blocks = []
    for key, label in SUBJECTS:
        cells = []
        for stage, stage_vi in (('before', 'trước'), ('after', 'sau')):
            cells += [fix_full._shot(h, imgdir, f"fx/{key}/{stage}_impact_{m}s.png", f"{stage_vi}, nổ +{m} s") for m in MOMENTS]
        blocks.append(f"<div class='fxblock'><div class='caption'><b>{_e(label)}</b>: hàng trên trước khi sửa, hàng dưới sau khi sửa</div>"
                      "<div class='fxgrid'>" + ''.join(f"<div class='fxcell'>{x}</div>" for x in cells) + "</div></div>")
    return '\n'.join(blocks)


def section(game, h, imgdir):
    out = ["<div class='section'><h2>22. Ném bom rải thảm</h2>",
           "<p>Lỗi cũ: bom của máy bay ném bom nằm dồn một chỗ. Oanh tạc cơ chiến lược thả 7 quả cách nhau chỉ tốc độ × 0,2 s "
           "(≈ 3,5 m, dải ~20 m, lõi 10 m chồng lõi); khoang bom của boss bay như đạn pháo và nhắm cả loạt vào một điểm. "
           "Bản sửa: mỗi vũ khí thả bom có khối <code>stick</code> trong dữ liệu; quả thứ i rơi tại đầu dải + hướng × i × khoảng + lệch "
           "(theo seed), khoảng = 1,1 × lõi, nhịp = khoảng / tốc độ lúc thả; dải theo hướng bay hoặc trục chính của cụm mục tiêu "
           "(trong ±45°); an toàn quân ta xét từng quả; ít mục tiêu thì thả max(2, ⌈n/3⌉) quả; máy bay giữ thẳng hướng và độ cao "
           "suốt dải. Sát thương mỗi lượt, số bom mỗi lượt và chu kỳ không đổi. Bom dẫn đường giữ một điểm.</p>",
           "<p>Hình ảnh (lượt 3): cửa khoang mở (heavy_bomber, command_airship: chốt bản lề Part_bay_door_L/R), từng quả rơi đúng nhịp "
           "kèm vệt, nổ nối nhau dọc dải theo luật bậc T0–T5 (quả xa camera của dải dài nhẹ hơn trong ngân sách hiệu ứng), một hình chữ "
           "nhật cảnh báo cho cả dải (viền mảnh, nền mờ, dải lõi đậm, vòng đếm ngược của quả kế tiếp) tắt dần theo từng đoạn, "
           "âm nổ rải theo dải với một đuôi vang chung.</p>",
           "<h3>Tham số dải theo vũ khí</h3>",
           "<p>Từ <code>balance.json</code> weapons[*].stick (sau inherits). Cột Thẻ: câu thẻ máy bay sinh từ dữ liệu (StickLines).</p>",
           parameter_table(game, h),
           "<h3>Trước / sau (vết thả, trung bình 3 seed)</h3>",
           "<p>Trước = vết thả lượt 0 (<code>Docs/export/bom_2026-10-03/vet_tha_truoc_luot2.csv</code>); sau = vết thả Unity sau bản sửa "
           "(<code>vet_tha_unity.csv</code>). Hai đội hình chuẩn: 5 xe cách nhau 8 m thành hàng dọc đường bay, và 5 xe thành cụm 8 m, "
           "đặt quanh điểm nhắm; xe trúng = trong lõi hoặc rìa của ít nhất một quả (xe là điểm).</p>",
           compare_table(h),
           "<h3>Ảnh dải nổ trước / sau</h3>",
           "<p>Nền lưới 1 m (vạch đậm mỗi 5 m), một Tăng chủ lực đứng cạnh làm thước, vòng lõi đỏ và rìa cam của từng quả. Lúc quả đầu "
           "nổ, sau 1 s và sau 3 s. Ảnh: <code>MachineBrigade.Editor.EffectShots.FxBatch</code> (<code>-mbFxIds sticks</code>).</p>",
           pictures(h, imgdir), "</div>"]
    return '\n'.join(out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print(section({}, None, ROOT / 'Docs' / 'doc-images'))
