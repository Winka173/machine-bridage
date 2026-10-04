"""The design document's prompt 34 sections (DECISIONS "Prompt 34 L8 / L9"), read from balance.json through the prompt 34
balance tools, so the document shows what the data holds (build_doc.py calls them):

* section10: 10i, the weapon families and their tiers, each boss weapon's family round (damage, core, edge, cycle), the
  warnings by escape time;
* section16: 16b, firing, blast and sound by tier, wrecks by class, the previews' settings;
* handbook_tiers: the ammunition handbook's T0-T5 tiers (VI + EN, as the game's handbook entry "tiers").

    python Tools/docs/prompt34.py > out.html     # the three sections alone, for a look
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Tools' / 'balance'))

import p34_families as F  # noqa: E402
import p34_boss_families as B  # noqa: E402
import p34_warnings as W  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

MAX_EDGE = 20.0


def _data():
    return Doc(F.PATH).data()


def _n(x, d=1):
    s = f"{float(x):,.{d}f}".replace(',', ' ')
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')


def _table(head, rows, cls=''):
    h = ''.join(f'<th>{c}</th>' for c in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f"<table class='{cls}'><tr>{h}</tr>{body}</table>"


def _helpers(h):
    return (h or {}).get('esc', html.escape), (h or {}).get('table', _table)


# --------------------------------------------------------------------------------------------- 10i

def section10(game=None, h=None):
    e, table = _helpers(h)
    data = _data()
    ws = F.Weapons(data)
    assign = F.assignment(ws)
    fams = data.get('weaponFamilyTable', [])
    used = {}
    for wid, (fam, var, _) in assign.items():
        used.setdefault(fam, 0)
        used[fam] += 1
    fam_rows = []
    for t in sorted(fams, key=lambda t: (t.get('tier', 0), t['id'])):
        boss = t.get('boss') or {}
        variants = '<br>'.join(f"<code>{e(k)}</code>: {e(v)}" for k, v in (t.get('variants') or {}).items()) or '—'
        fam_rows.append([f"<code>{e(t['id'])}</code>", e(t.get('name', '')), f"T{t.get('tier', 0)}",
                         _n(boss['damage'], 0) if 'damage' in boss else '—',
                         (f"{_n(boss.get('core', 0))} / {_n(boss.get('edge', 0))} m" if 'damage' in boss else '—'),
                         str(used.get(t['id'], 0)), variants])

    built, users = B.boss_users(data)
    boss_rows = []
    for bid in sorted(built):
        b = built[bid]
        seen = set()
        for wid in [w for w in B.S.mounts_of(b) if w]:
            if wid in seen or wid not in ws.raw:
                continue
            seen.add(wid)
            w = ws.resolve(wid)
            fam, var, tier = assign[wid]
            core = float(w.get('splash', 0) or 0)
            edge = float(w.get('edge', 0) or 0) or (min(MAX_EDGE, 2 * core) if core else 0)
            cd = float(w.get('cooldown', 0) or 0)
            guided = w.get('projectile') in ('Missile', 'Drone')
            warn = W.escape(tier, fam, core) if (tier >= 4 and not guided and not w.get('laid') and core > 0) else 0
            boss_rows.append([f"<b>{e(bid)}</b>", e(w.get('real') or wid), f"<code>{e(fam)}{'/' + e(var) if var else ''}</code>", f"T{tier}",
                              _n(w.get('damage', 0), 0), f"{_n(core)} / {_n(edge)} m" if core else '—',
                              f"{_n(cd)} s" if cd else '—', f"{_n(warn, 2)} s" if warn else '—'])
    for bid in sorted(built):
        s = built[bid].get('salvo')
        if isinstance(s, dict) and s.get('weapon'):
            boss_rows.append([f"<b>{e(bid)}</b>", f"loạt {e(s['weapon'])} ({s.get('shells', 3)} quả một tháp)", '<code>cal_406</code>', 'T5',
                              _n(s.get('damage', 0), 0), f"{_n(s.get('radius', 7))} / {_n(s.get('edge') or min(MAX_EDGE, 2 * s.get('radius', 7)))} m",
                              f"{_n(s.get('every', 10))} s", f"{_n(s.get('warn', 2.6), 2)} s"])

    warn_rows = []
    for t in sorted(fams, key=lambda t: (t.get('tier', 0), t['id'])):
        if t.get('tier', 0) < 4:
            continue
        boss = t.get('boss') or {}
        core = float(boss.get('core', 0) or 0)
        warn_rows.append([f"<code>{e(t['id'])}</code>", e(t.get('name', '')), f"T{t['tier']}", f"{_n(core)} m" if core else '—',
                          f"{_n(W.escape(t['tier'], t['id'], core), 2)} s"])
    return ("<div class='section'><h2>10i. Họ vũ khí, bảng boss, bán kính và cảnh báo (prompt 34)</h2>"
            "<p>Mỗi vũ khí có <code>weaponFamilyId</code> (súng: lớp cỡ nòng; còn lại: vũ khí thật) và <code>weaponVariantId</code> khi đạn "
            "hay cách bắn khác (có lý do trong bảng). Bậc T0–T5 theo họ. Ở boss, cùng họ là cùng viên đạn (sát thương, lõi, rìa, tốc độ, loại); "
            "DPS của từng vũ khí giữ nguyên bằng chu kỳ dài hơn, và lõi rộng hơn 1,25 lần thì chu kỳ dài thêm đúng tỉ lệ đó. "
            "Vũ khí người chơi chỉ gắn nhãn (danh sách lệch: Docs/checks/player_weapon_family.md). Kiểm: <code>Tools/balance/p34_validate.py</code>.</p>"
            f"<h3>Họ vũ khí ({len(fam_rows)})</h3>"
            + table(['Họ', 'Tên', 'Bậc', 'Sát thương (boss)', 'Lõi / rìa (boss)', 'Số vũ khí', 'Biến thể và lý do'], fam_rows, 'dps')
            + f"<h3>Vũ khí boss theo họ ({len(boss_rows)})</h3>"
            "<p>Sát thương một viên; nổ giảm theo khoảng cách (bảng giảm nổ lan 04/10: lõi 110 / 108 / 105 / 100%, từ lõi ra rìa 85 / 65 / 45 / 25%, ngoài rìa 0). Hồi: thời gian hồi của vũ khí (loạt và băng giữ nhịp riêng). "
            "Cảnh báo: thời gian đạn T4+ không dẫn đường báo chỗ rơi (đạn ở trên không ít nhất bấy lâu).</p>"
            + table(['Boss', 'Vũ khí', 'Họ', 'Bậc', 'Sát thương', 'Lõi / rìa', 'Hồi', 'Cảnh báo'], boss_rows, 'dps')
            + "<h3>Cảnh báo theo khả năng thoát</h3>"
            "<p>Đạn T4+ của boss báo max(sàn, 0,5 s + lõi / 4,5 m/s), tối đa 6 s; sàn T4 2,5 s, 406 mm 3,5 s, siêu vũ khí T5 4 s. "
            "Vòng hiển thị là đúng vùng sát thương: vòng ngoài là rìa, vòng trong là lõi (tên lửa hành trình: lõi và rìa của vụ nổ hai lớp). "
            "Gungnir giữ 3 s (ngoại lệ có tên: prompt 29 G1).</p>"
            + table(['Họ', 'Tên', 'Bậc', 'Lõi (boss)', 'Cảnh báo'], warn_rows, 'dps')
            + "</div>")


# --------------------------------------------------------------------------------------------- 16b

TIER_ROWS = [
    ('T0', 'Chớp mảnh của vũ khí', 'Nổ nhỏ (công thức Small)', '—', 'shot_t0: tiếng giòn 35 ms, đuôi 0,08 s; súng nhỏ thành cụm đấu súng'),
    ('T1', 'Khói mỏng', 'Nổ nhỏ, đạn nổ trên không giữ chùm mảnh', '—', 'shot_t1; cụm đấu súng từ khẩu thứ ba trong 20 m'),
    ('T2', 'Chớp vừa, khói ngắn', 'Cầu lửa nhỏ nóng, bụi và đất', '—', 'shot_t2, blast_he_t2; ưu tiên 25-30'),
    ('T3', 'Chớp lớn cháy lâu, cầu lửa đầu nòng, khói dài, vòng bụi, thân xe giật lùi', 'Cầu lửa vừa, cột bụi 5 cuộn, hố sáng nhỏ', '—',
     'shot_t3, blast_he_t3; ưu tiên 40 gần'),
    ('T4', 'Chớp rất lớn, hai cầu lửa, khói cuộn, vòng áp suất, mặt đất sáng; tàu: vòng nước và bụi nước',
     'Cầu lửa cuộn lớn, cột 8 cuộn, mảnh văng, hai váy bụi; sóng xung kích trên rìa', 'Rung 0,22 (chỉ trên màn hình, trong 90 m)',
     'shot_t4, blast_he_t4, tiếng rền dưới; ưu tiên 50 gần'),
    ('T5', 'Chớp sáng cả cảnh, khói rất dài, vòng áp suất đôi, hai vòng nước',
     'Cầu lửa rất lớn, cột 10 cuộn thành mũ nấm nhỏ, mảnh xa, ba váy bụi, hố sáng 12 s; vòng trên lõi rồi rìa', 'Rung 0,6',
     'shot_t5, blast_he_t5; ưu tiên 60 (giữ 8 kênh cuối cho cảnh báo và T5 / boss)'),
]

WRECK_ROWS = [
    ('Xích (tăng; cả tàu hỏa)', 'Tháp pháo văng, thân cháy'),
    ('Bánh lốp', 'Hai bánh văng xoáy, khung lật nghiêng hoặc ngửa trong 0,9 s'),
    ('Xe tải', 'Hàng nổ dây chuyền 4-6 tiếng dọc thùng, thùng cháy'),
    ('Pháo', 'Đạn trong xe nổ 6-9 tiếng, cột lửa 2-3,5 s, tháp văng một nửa số lần'),
    ('Tiêm kích', 'Mất một cánh kéo lửa, xoáy ốc rơi'),
    ('Trực thăng', 'Rotor đuôi văng, rotor chính bay mất, xoay ngày càng nhanh'),
    ('Máy bay lớn', 'Mất cánh, động cơ cháy, rơi dài và nghiêng'),
    ('Tàu', 'Nghiêng, gãy đôi (từ 24 m) và chìm; xuồng lật'),
    ('Drone', 'Một tiếng nổ nhỏ, không còn gì'),
]

PREVIEW_ROWS = [
    ('Mặt đất', 'Đất theo biome của bản đồ đang chọn (mặc định ôn đới)', 'Xe mặt đất, boss mặt đất'),
    ('Biển', 'Mặt biển có sóng, mục tiêu đứng trên bờ phía trước', 'Tàu, xuồng, boss biển'),
    ('Mép nước', 'Nửa sau trên nước, nửa trước trên bờ', 'Xe lội nước, đệm khí'),
    ('Đường ray', 'Đoạn ray (đá ballast, tà vẹt, hai ray, ụ chặn)', 'Tàu hỏa, Juggernaut, Nemesis, Gungnir'),
    ('Trên không', 'Bay vòng / lơ lửng, đất ở phía dưới', 'Máy bay, trực thăng, boss bay'),
    ('Ô căn cứ', 'Bệ bê tông, viền tối, dấu góc', 'Tháp'),
    ('Bờ biển', 'Pháo bờ biển trên bệ ở bờ, một tàu ngoài biển làm mục tiêu', 'Khẩu đội bờ biển'),
]


def section16(game=None, h=None):
    e, table = _helpers(h)
    return ("<div class='section'><h2>16b. Hiệu ứng, âm thanh theo bậc, xác vỡ, màn xem trước (prompt 34)</h2>"
            "<p>Hình và tiếng chỉ là hiển thị, không đổi kết quả mô phỏng. Hiệu ứng bậc được <b>vẽ lại</b> và chồng lên vụ nổ sẵn có của viên đạn "
            "(không vụ nổ nào nhỏ đi). Giới hạn chi tiết đầy đủ cùng lúc: T5 1, T4 3, T3 6; xa camera thì rút gọn (dưới 70 m đầy đủ, dưới 140 m 45%). "
            "Âm thanh tổng hợp bằng script (Tools/sfx/build_sfx.py, không dùng AI), mỗi phát ba lớp trộn sẵn: cơ cấu, tiếng nổ, đuôi vang. "
            "32 kênh, từ 24 kênh bận thì tiếng mới dưới ưu tiên 60 chỉ chiếm kênh kém quan trọng nhất. Số liệu cảnh thử tải: Docs/balance/p34_stress_counts.json "
            "(cảnh <code>-mb-play -mb-lighthousebay -mb-p34stress</code>; FPS: NEED PROFILE).</p>"
            "<h3>Bắn, nổ và tiếng theo bậc</h3>"
            + table(['Bậc', 'Phát bắn', 'Vụ nổ', 'Camera', 'Tiếng'], [[e(x) for x in r] for r in TIER_ROWS], 'dps')
            + "<h3>Xác vỡ theo lớp xe</h3><p>Xác sống 30-45 s (boss 90 s), cháy 40% thời gian đó; tối đa khoảng 12 xác đầy đủ gần camera "
            "(Trung bình 9, Thấp 6), để lại vết cháy. Mảnh vỡ chỉ là hình: không có collider, không chặn đường hay tầm nhìn.</p>"
            + table(['Lớp', 'Cách vỡ'], [[e(x) for x in r] for r in WRECK_ROWS], 'dps')
            + "<h3>Màn xem trước theo môi trường</h3><p>Xem bắn, chi tiết xe / boss / tháp: đơn vị đứng đúng chỗ của nó. Cảnh tạm đúng loại "
            "cho tới khi tài sản biome, mặt nước và đường ray của prompt 33 được gộp vào. Bắn thử dùng đúng hiệu ứng và tiếng theo bậc; "
            "mỗi viên nổ hiện vòng rìa và lõi đúng cỡ vùng sát thương.</p>"
            + table(['Môi trường', 'Cảnh', 'Đơn vị'], [[e(x) for x in r] for r in PREVIEW_ROWS], 'dps')
            + "</div>")


# --------------------------------------------------------------------------------------------- handbook tiers

TIER_TEXT = {
    0: ('Súng nhỏ: chớp mảnh, tiếng nổ giòn ngắn.', 'Small arms: a thin flash and a short crack.'),
    1: ('Pháo tự động: chớp nhỏ, khói mỏng; nhiều súng cùng bắn nghe thành một trận đấu súng.',
        'Autocannon: a small flash and thin smoke; many guns at once are heard as one firefight.'),
    2: ('Pháo vừa và rocket nhẹ: chớp vừa, quả cầu lửa nhỏ, bụi và đất tung lên.',
        'Medium guns and light rockets: a medium flash, a small hot fireball, dust and earth thrown up.'),
    3: ('Pháo nặng: chớp lớn, cầu lửa đầu nòng, khói dài và chậm, cột bụi; thân xe giật lùi.',
        'Heavy guns: a big flash and muzzle fireball, long slow smoke, a dust column; the hull rocks back.'),
    4: ('Pháo rất nặng, Smerch, bom 400 kg: chớp rất lớn, cầu lửa cuộn, sóng xung kích trên mép vụ nổ, máy quay rung ngắn.',
        'Very heavy guns, Smerch, 400 kg bombs: a very big flash, a rolling fireball, a shockwave on the blast\'s edge, a short camera shake.'),
    5: ('Siêu vũ khí: chớp sáng cả cảnh, đám mây hình nấm nhỏ, vòng trên lõi rồi trên mép, rung mạnh nhất.',
        'Super weapons: a flash that lights the scene, a small mushroom cloud, rings on the core then the edge, the strongest shake.'),
}


def handbook_tiers(game=None, h=None):
    e, table = _helpers(h)
    fams = _data().get('weaponFamilyTable', [])
    rows = []
    for t in range(6):
        names = [f.get('name', f['id']) for f in sorted(fams, key=lambda f: f['id']) if f.get('tier', 0) == t]
        shown = ', '.join(names[:6]) + (f" (+{len(names) - 6})" if len(names) > 6 else '')
        rows.append([f"T{t}", e(shown or '—'), e(TIER_TEXT[t][0]), e(TIER_TEXT[t][1])])
    return ("<div class='section'><h2>Sổ tay đạn: bậc T0–T5 / Calibre tiers</h2>"
            "<p>Như mục \"Bậc cỡ nòng T0–T5\" của Sổ tay đạn trong game. Bậc lấy theo họ: càng to thì mỗi phát càng mạnh, nổ, hình và tiếng càng lớn, "
            "bù bằng thời gian nạp dài hơn. Đạn T4 và T5 của boss báo chỗ rơi ít nhất 0,5 s + lõi / 4,5 m/s (T4 ít nhất 2,5 s). "
            "/ A round's tier comes from its family; a boss's T4-T5 rounds warn at least 0.5 s + core / 4.5 m/s.</p>"
            + table(['Bậc', 'Họ', 'Hình và tiếng', 'Look and sound'], rows, 'dps') + "</div>")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(section10() + section16() + handbook_tiers())
