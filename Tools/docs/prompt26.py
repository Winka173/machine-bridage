"""The design document's second-round table (prompt 25 G), the bosses' blasts, phases and sizes (prompt 26 B/C) and the Boss Hunt (prompt 26 E).

Read from the export's fields: a weapon's secondRounds, splash / splashEdge / edgeShare, a boss's phaseData and modelSize, and the hunt block.
"""
from prompt25 import f

TYPE_NAMES = {'Kinetic': 'Động năng', 'ArmorPiercing': 'Xuyên giáp', 'HighExplosive': 'Nổ mạnh', 'Fire': 'Lửa', 'Flak': 'Phòng không',
              'ShapedCharge': 'Nổ lõm', 'Fragmentation': 'Mảnh', 'Energy': 'Năng lượng'}
GROUPS = ('vehicles', 'elites', 'bosses', 'towers', 'itemVehicles')


def rounds_section(game, h):
    """Section 10f: every gun's second round (DECISIONS 25G): what it loads, for what, the change time and the gun's own round."""
    e, table = h['esc'], h['table']
    carriers = {}
    for group in GROUPS:
        for v in game.get(group, []):
            for w in v.get('weapons', []):
                carriers.setdefault(w['id'], set()).add(v.get('short') or v['name'])
    seen, rows = set(), []
    for group in GROUPS:
        for v in game.get(group, []):
            for w in v.get('weapons', []):
                if not w.get('secondRounds') or w['id'] in seen:
                    continue
                seen.add(w['id'])
                own = f"{f(w['damage'], 0)} / {f(w['splash'], 1) if w['splash'] else '—'}"
                for r in w['secondRounds']:
                    rows.append([f"<b>{e(w['name'])}</b><br><span class='muted'>{e(w['id'])}</span>", e(', '.join(sorted(carriers[w['id']]))[:60]),
                                 f"{e(r['kind'])}<br><span class='muted'>{e(r['id'])}</span>", e(TYPE_NAMES.get(r['type'], r['type'])), str(r['pen']),
                                 f(r['damage'], 0), f(r['splash'], 1) if r['splash'] else '—', e(r['use']),
                                 'tinh nhuệ / hạng 7' if r['elite'] else 'mọi xe', f"{f(r['switch'], 1)} s", own])
    return ("<div class='section'><h2>10f. Đạn thay thế (hai loại đạn)</h2>"
            "<p>Prompt 25 G: nhiều súng nạp được loại đạn thứ hai; súng tự chọn theo mục tiêu (xe giáp, xe nhẹ, máy bay, công trình), "
            "đổi đạn mất thời gian nạp của chính súng (tối thiểu 0,5 s) và giữ loại đạn ít nhất 2 s. Nhịp bắn, tầm và băng đạn vẫn là của súng; "
            "chỉ loại sát thương, xuyên, sát thương, nổ lan và dạng đạn đổi. Cột cuối là đạn gốc của súng (sát thương / nổ lan m). Biểu tượng đổi đạn nằm trên ô vũ khí "
            "của thẻ, trang chi tiết xe và bảng hiệu ứng. Chưa cân bằng lại: số theo file Excel và số của súng.</p>"
            f"<h3>{len(rows)} loại đạn thay thế của {len(seen)} loại súng</h3>"
            + table(['Súng', 'Xe mang', 'Đạn thay', 'Loại sát thương', 'Xuyên', 'Sát thương', 'Nổ lan (m)', 'Dùng khi', 'Ai mang', 'Đổi đạn', 'Đạn gốc'], rows, 'dps')
            + "</div>")


def boss_blast_section(game, h):
    """Section 10g: each boss's blasts as core / edge (prompt 26 B.3), its phases, armour and size."""
    e, table = h['esc'], h['table']
    blast_rows, phase_rows = [], []
    for v in game.get('bosses', []):
        raw = v.get('raw', {})
        seen = {}
        for w in v.get('weapons', []):
            core, edge = float(w.get('splash', 0) or 0), float(w.get('splashEdge', 0) or 0)
            if core > 0 or edge > 0:
                seen.setdefault(w['id'], (w, core, edge))
        for wid, (w, core, edge) in seen.items():
            share = round(float(w.get('edgeShare', 0.4)) * 100)
            # Full fix L10 item 3: the family's numbers as they are now and the warning time (0: none).
            warn = float(w.get('warnSeconds', (w.get('raw') or {}).get('WarnSeconds', 0)) or 0)
            blast_rows.append([f"<b>{e(v['name'])}</b>", e(w['name']), e(w.get('familyId') or (w.get('raw') or {}).get('WeaponFamilyId') or '—'),
                               f(w['damage'], 0), e(TYPE_NAMES.get(w['type'], w['type'])),
                               f"{f(core, 1)} m" if core else '—', f"{f(edge, 1)} m ({share}% sát thương)" if edge else 'một lớp, giảm dần',
                               f"{f(warn, 2)} s" if warn > 0 else 'không'])
        a = v.get('armour') or {}
        size = v.get('modelSize') or []
        phases = '<br>'.join(f"{p['at'] * 100:g}%: sát thương ×{p['damage']:g}, tốc độ ×{p['speed']:g}, nhận sát thương ×{p['armor']:g}, nhịp bắn ×{p['fireRate']:g}"
                             + (f", hồi {p['heal'] * 100:g}% máu" if p.get('heal') else '') for p in v.get('phaseData') or []) or '—'
        phase_rows.append([f"<b>{e(v['name'])}</b>", 'mini' if raw.get('MiniBoss') else 'chủ lực', f"{float(v.get('hp', 0) or 0):,.0f}".replace(',', '.'),
                           f"{a.get('front', 0)}/{a.get('side', 0)}/{a.get('rear', 0)}/{a.get('top', 0)}",
                           ' × '.join(f(x, 0) for x in size[:3]) if size else '—', phases])
    return ("<div class='section'><h2>10g. Boss: vụ nổ hai lớp, pha, giáp và cỡ (prompt 26)</h2>"
            "<p>Prompt 26: vũ khí nổ của boss có hai lớp. <b>Lõi</b> (bán kính nổ của vũ khí) nhận đủ sát thương; <b>rìa</b> (gấp đôi lõi, tối đa 20 m) nhận 40% sát thương. "
            "Vũ khí không có rìa nổ một lớp, giảm dần theo khoảng cách. Máu, vũ khí và cỡ của boss được làm lại theo chương (mục tiêu hạ boss chủ lực từ 2,5 phút ở chương 1 tới 4 phút "
            "ở chương 12, mini boss 60 đến 90 giây); Ixion và Gungnir được làm lại; mỗi boss có mốc thời đại ở dòng Tham khảo của thẻ. "
            "Pha: hệ số nhân vào từ mốc máu đó trở đi.</p>"
            f"<h3>Vụ nổ lõi / rìa của boss ({len(blast_rows)} vũ khí)</h3>"
            + table(['Boss', 'Vũ khí', 'Họ vũ khí', 'Sát thương', 'Loại', 'Lõi (đủ sát thương)', 'Rìa', 'Cảnh báo'], blast_rows, 'dps')
            + f"<h3>Pha, giáp và cỡ model ({len(phase_rows)} boss)</h3>"
            + table(['Boss', 'Cấp', 'Máu', 'Giáp T/H/S/N', 'Cỡ model (m)', 'Pha'], phase_rows, 'dps')
            + "</div>")


def hunt_section(game, h):
    """Section 10h: the Boss Hunt (DECISIONS 26E): the week, the full hunt, the supports and the tiers."""
    e, table = h['esc'], h['table']
    hunt = game.get('hunt') or {}
    if not hunt:
        return ''
    sup_rows = [[e(x['name']), f"<code>{e(x['id'])}</code>", e(x['info']), f"+{x['strength'] * 100:g}%" if x['strength'] > 0 else 'đổi cách chơi, không tính vào trần']
                for x in hunt.get('supports', [])]
    tiers = [['Dễ', '×0,8', '×0,9'], ['Thường', '×1', '×1'], ['Khó (Anh dũng)', '×1,3', '×1,15'], ['Rất khó (Thép)', '×1,6', '×1,3']]
    minis = hunt['weekly'] - hunt['weeklyMains']
    rules = [
        "<b>Sức mạnh P:</b> đo một lần lúc bắt đầu từ bộ bài mang theo (sát thương giấy mỗi giây của các thẻ chiến đấu, tính cả hạng thẻ, trang bị và chỉ huy) × 10 xe ra trận × 0,3 trúng boss, "
        "tối thiểu 60. Máu boss = P × thời gian mục tiêu × 0,6 × hệ số m × hệ số bậc; sát thương boss là của dữ liệu × m × hệ số bậc.",
        f"<b>Tuần:</b> {hunt['weekly']} boss ({hunt['weeklyMains']} chủ lực, {minis} mini; nhóm 3, 2, 2 mini dẫn tới mỗi boss chủ lực), mục tiêu mini {hunt['miniSeconds']:g} s, "
        f"chủ lực {hunt['mainSeconds'] / 60:.1f} phút; m = 1 + {hunt['weeklyStep']:g} × số thứ tự (×1 tới ×1,54); nghỉ 15 s giữa các boss, quân sống sót được sửa 30% và chỉ giữ 50% CP; "
        "điểm hồi sinh sau mỗi boss chủ lực; đồng hồ 30 phút.",
        f"<b>Toàn bộ:</b> {hunt['full']} boss ({hunt['fullMains']} chủ lực) theo thứ tự cốt truyện, chủ lực 2,5 phút, mini 1 phút; m từ ×{hunt['fullFrom']:g} tới ×{hunt['fullTo']:g}; "
        "điểm hồi sinh và lưu sau mỗi boss; mỗi boss là một trận mới (không giữ quân, CP khởi đầu như nhau), chỉ hỗ trợ tác chiến được giữ.",
        f"<b>Hỗ trợ tác chiến:</b> sau mỗi boss chủ lực chọn 1 trong 3; tổng sức mạnh quân từ hỗ trợ tối đa +{hunt['cap'] * 100:g}%; khi đã chạm trần chỉ còn các hỗ trợ đổi cách chơi (thẻ bắn nhanh hơn, thả xe).",
        "<b>Bậc:</b> bốn độ khó của bảng chọn là bốn bậc (bảng dưới). Chưa làm: bậc Huyền thoại và các biến thể (mutator) cho Săn trùm.",
    ]
    return ("<div class='section'><h2>10h. Săn trùm (Boss Hunt)</h2>"
            "<p>Prompt 26 E: máu boss theo sức mạnh bộ bài; mọi số dưới đây là giá trị khởi đầu, chờ đo ở phase kiểm tra.</p><ul>"
            + ''.join(f'<li>{r}</li>' for r in rules) + "</ul>"
            f"<h3>Lời trong game</h3><p class='muted'>Tuần: {e(hunt.get('weeklyRules', ''))}</p><p class='muted'>Toàn bộ: {e(hunt.get('fullRules', ''))}</p>"
            "<h3>Bậc độ khó</h3>" + table(['Bậc', 'Máu boss', 'Sát thương boss'], tiers)
            + f"<h3>Hỗ trợ tác chiến ({len(sup_rows)})</h3>" + table(['Hỗ trợ', 'Id', 'Tác dụng', 'Sức mạnh quân'], sup_rows)
            + "</div>")
