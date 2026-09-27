"""Builds the design-review document (HTML, then PDF through Edge) from the game's own numbers.

    python Tools/docs/build_doc.py <game.json> <images dir> <out.pdf>

game.json comes from the ExportGameDoc EditMode test (MB_EXPORT=<path>). The images directory
holds: veh/<model>.png (Tools/blender/preview_assets.py hero renders), shots/*.png (device or
emulator screenshots, named by section), maps/<id>.png (Tools/maps/plot_map.py). Equipment
pictures are read straight from Assets/MachineBrigade/Resources/UI/Gear.
"""
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
GEAR_ART = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Gear'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

CLASS_VI = {'Scout': 'Trinh sát', 'Light': 'Xe nhẹ', 'Tank': 'Xe tăng', 'Heavy': 'Hạng nặng', 'TankHunter': 'Diệt tăng',
            'Artillery': 'Pháo binh', 'AntiAir': 'Phòng không', 'Support': 'Hỗ trợ', 'Aircraft': 'Không quân', 'Helicopter': 'Trực thăng',
            'Plane': 'Máy bay', 'Defense': 'Công sự', 'Boss': 'Boss'}
ARMOR_VI = {'Light': 'Nhẹ', 'Heavy': 'Nặng', 'Air': 'Máy bay', 'Structure': 'Công trình'}
TYPE_VI = {'Kinetic': 'Động năng', 'ArmorPiercing': 'Xuyên giáp', 'HighExplosive': 'Nổ mạnh', 'Fire': 'Lửa', 'Flak': 'Phòng không'}
TARGET_VI = {'Ground': 'Mặt đất', 'Air': 'Trên không', 'All': 'Tất cả'}
SLOT_VI = {'Weapon': 'Vũ khí', 'Loader': 'Nạp đạn', 'Armor': 'Giáp', 'Optics': 'Quang học', 'Engine': 'Động cơ', 'Repair': 'Sửa chữa',
           'Special': 'Đặc biệt'}
RARITY_VI = ['Thường', 'Khá', 'Hiếm', 'Sử thi', 'Huyền thoại']
RARITY_COL = ['#8c969c', '#7fae5a', '#4f8fd8', '#9b6cd9', '#e9b949']
GOAL_VI = {'Capture': 'Chiếm cứ điểm', 'Hold': 'Giữ cứ điểm', 'Destroy': 'Phá hủy', 'Escort': 'Hộ tống', 'Survive': 'Trụ vững',
           'Boss': 'Tiêu diệt boss', 'Intercept': 'Chặn tàu', 'Hunt': 'Săn mục tiêu', 'Recon': 'Trinh sát', 'Protect': 'Bảo vệ',
           'ShootDown': 'Bắn hạ máy bay'}


def esc(s):
    return html.escape(str(s))


def num(v, d=0):
    if isinstance(v, (int, float)):
        return f'{v:,.{d}f}'.replace(',', '.') if d == 0 else f'{v:.{d}f}'
    return esc(v)


def pct_list(values):
    return ' / '.join(f'{v * 100:g}%' for v in values)


def fill(text, values):
    """Puts the trait's numbers (Epic/Legendary) into its effect text."""
    def one(m):
        i = int(m.group(1))
        return values[i] if i < len(values) else m.group(0)
    return re.sub(r'\{(\d+)\}', one, text)


def img(path, cls='', alt=''):
    p = Path(path)
    if not p.exists():
        return ''
    return f'<img class="{cls}" src="{p.as_uri()}" alt="{esc(alt)}">'


def table(head, rows, cls=''):
    h = ''.join(f'<th>{esc(c)}</th>' for c in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


CSS = """
@page { size: A4; margin: 14mm 12mm 16mm 12mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1e2428; font-size: 10.5pt; line-height: 1.42; }
h1 { font-size: 26pt; margin: 0 0 6pt 0; letter-spacing: 1pt; }
h2 { font-size: 17pt; margin: 0 0 8pt 0; padding-bottom: 4pt; border-bottom: 3px solid #f2a33a; page-break-after: avoid; }
h3 { font-size: 12.5pt; margin: 14pt 0 5pt 0; page-break-after: avoid; }
h4 { font-size: 11pt; margin: 8pt 0 3pt 0; }
p { margin: 3pt 0 6pt 0; }
.section { page-break-before: always; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover .kicker { color: #d48a24; font-weight: 700; letter-spacing: 3pt; font-size: 11pt; }
.cover img { width: 100%; margin: 14pt 0; border: 1px solid #ccc; }
.muted { color: #69747b; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt 0; font-size: 8.8pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #242c32; color: #edeae3; text-align: left; padding: 3pt 5pt; font-weight: 600; }
td { border-bottom: 1px solid #dde1e3; padding: 3pt 5pt; vertical-align: top; }
tbody tr:nth-child(even) td { background: #f5f6f7; }
.shot { width: 100%; border: 1px solid #c9cdd0; margin: 4pt 0 2pt 0; }
.caption { font-size: 8.5pt; color: #69747b; margin-bottom: 10pt; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8pt; }
.card { border: 1px solid #d5d9dc; padding: 8pt; page-break-inside: avoid; margin-bottom: 8pt; }
.card .head { display: grid; grid-template-columns: 170pt 1fr; gap: 10pt; }
.card img.thumb { width: 170pt; height: 96pt; object-fit: cover; border: 1px solid #e0e3e5; background: #6b7775; }
.card .name { font-size: 13pt; font-weight: 700; }
.card .meta { font-size: 8.8pt; color: #4a555c; }
.card .note { font-size: 9pt; margin-top: 3pt; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2pt 10pt; font-size: 9pt; margin-top: 4pt; }
.stats b { font-weight: 700; }
.chip { display: inline-block; padding: 0 5pt; border: 1px solid #c9cdd0; border-radius: 2px; font-size: 8.5pt; margin: 1pt 2pt 1pt 0; }
.gearicon { width: 34pt; height: 34pt; vertical-align: middle; }
.dps td.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
.map { page-break-inside: avoid; margin-bottom: 10pt; }
.map img { width: 100%; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; }
.rar { display: inline-block; width: 9pt; height: 9pt; border-radius: 1px; margin-right: 3pt; vertical-align: middle; }
.toc li { margin: 2pt 0; }
"""


def vehicle_card(v, imgdir):
    weapons = [[esc(w['id']), TYPE_VI.get(w['type'], w['type']), num(w['damage']) + (f" ×{w['burst']}" if w['burst'] > 1 else ''),
                f"{w['cooldown']:g} s", f"{w['range']:g} m" + (f" (tối thiểu {w['minRange']:g})" if w['minRange'] > 0 else ''),
                TARGET_VI.get(w['targets'], w['targets']), f"{w['dps']:.0f}"] for w in v['weapons']]
    d = v['dpsVs']
    stats = (f"<div class='stats'><div>Máu <b>{num(v['hp'])}</b></div><div>Giáp <b>{ARMOR_VI.get(v['armor'], v['armor'])}</b></div>"
             f"<div>Tốc độ <b>{v['speed']:g} m/s</b></div><div>Giá <b>{v['cost']} CP</b></div>"
             f"<div>Tầm nhìn <b>{v['vision']:g} m</b></div><div>DPS vs nhẹ <b>{d['Light']:.0f}</b></div>"
             f"<div>DPS vs nặng <b>{d['Heavy']:.0f}</b></div><div>DPS vs máy bay <b>{d['Air']:.0f}</b></div></div>")
    skills = ''.join(f"<span class='chip'>{esc(s)}</span>" for s in v['skills'])
    thumb = img(Path(imgdir) / 'veh' / (v['model'] + '.png'), 'thumb', v['name'])
    return (f"<div class='card'><div class='head' style='{'' if thumb else 'grid-template-columns: 1fr'}'>{thumb}"
            f"<div><div class='name'>{esc(v['name'])}</div><div class='meta'>{CLASS_VI.get(v['class'], v['class'])}"
            f"{' · bay' if v['flying'] else ''} · id <code>{esc(v['id'])}</code></div>{stats}"
            f"<div class='note'>{esc(v['note'])}</div>{('<div>' + skills + '</div>') if skills else ''}</div></div>"
            + (table(['Vũ khí', 'Loại', 'Sát thương', 'Hồi', 'Tầm', 'Mục tiêu', 'DPS'], weapons) if weapons else '') + "</div>")


def build(game, imgdir):
    imgdir = Path(imgdir)
    shots = imgdir / 'shots'
    balance = json.loads(re.sub(r'//.*', '', (DATA / 'balance.json').read_text(encoding='utf-8')))
    out = [f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Machine Brigade - Design review</title><style>{CSS}</style></head><body>']

    # ------------------------------------------------------------------ cover and contents
    out.append("<div class='cover'><div class='kicker'>TÀI LIỆU THIẾT KẾ · REVIEW</div><h1>MACHINE BRIGADE</h1>"
               f"<p class='muted'>Game chiến thuật thời gian thực trên mobile, chỉ có phương tiện quân sự · bản {date.today().isoformat()}</p>"
               f"{img(shots / 'home.png', 'shot')}"
               "<p>Tài liệu này lấy số liệu trực tiếp từ dữ liệu game (balance.json, campaign.json, mã nguồn), gồm: các chế độ chơi, chiến dịch, "
               "toàn bộ phương tiện với chỉ số và DPS, vũ khí, tháp canh, boss, hỗ trợ hỏa lực, hệ thống trang bị, kinh tế, bản đồ và giao diện.</p></div>")
    out.append("<div class='section'><h2>Mục lục</h2><ol class='toc'><li>Tổng quan</li><li>Chế độ chơi</li><li>Chiến dịch</li>"
               "<li>Phương tiện (thẻ chi tiết)</li><li>Bảng DPS tổng hợp</li><li>Vũ khí và bảng sát thương</li><li>Tháp canh, xe tinh nhuệ và boss</li>"
               "<li>Hỗ trợ hỏa lực</li><li>Trang bị</li><li>Kinh tế</li><li>Bản đồ</li><li>AI và hệ thống</li><li>Giao diện</li></ol></div>")

    # ------------------------------------------------------------------ overview
    out.append("<div class='section'><h2>1. Tổng quan</h2>"
               "<p><b>Thể loại:</b> RTS / auto-battler trên điện thoại (màn ngang). Người chơi chỉ huy một binh đoàn phương tiện: xe tăng, xe bọc thép, "
               "pháo, phòng không, trực thăng, máy bay. Trận đấu phần lớn tự chạy: chỉ huy AI của người chơi tự mua quân (Tự mua) và tự gọi hỏa lực (Yểm trợ); "
               "người chơi can thiệp bằng lệnh Tấn công / Phòng thủ, chọn thẻ để triển khai, gọi hỏa lực vào điểm chọn.</p>"
               "<p><b>Vòng lặp:</b> điểm chỉ huy (CP) tăng theo thời gian và cứ điểm giữ được → mua phương tiện từ bộ bài (8 xe + 2 hỗ trợ) → phương tiện "
               "được thả dù xuống bãi thả của phe → chiến đấu tự động theo hệ thống khắc chế giáp/đạn → hạ địch được hoàn một phần CP.</p>"
               "<p><b>Ngoài trận:</b> lên hạng thẻ (bản thiết kế + xu), trang bị theo nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân), hòm đồ, chiến dịch 23 nhiệm vụ, "
               "sự kiện (pháo đài tuần, săn boss, vô tận, sinh tồn). Một loại tiền duy nhất: xu.</p>"
               f"<p><b>Bản đồ:</b> 12 chiến trường 300 × 300 m, mỗi bản có phiên bản chiếm cứ điểm, sinh tồn và công thành. "
               f"<b>Mô phỏng:</b> cố định 20 tick/giây, xác định (deterministic), tách khỏi phần hình ảnh.</p>"
               f"{img(shots / 'battle1.png', 'shot')}<div class='caption'>Trong trận: bản đồ nhỏ (góc trái), thanh nhiệm vụ, nút lệnh (phải), khay thẻ và CP (dưới).</div>"
               f"{img(shots / 'battle2.png', 'shot')}<div class='caption'>Bản đồ sa mạc Dune Break sau khi phóng to 50%; nhà cửa đã chỉnh tỷ lệ so với xe.</div></div>")

    # ------------------------------------------------------------------ modes
    desc = {
        'Conquest': 'Hai phe tranh 3 cứ điểm; giữ nhiều cứ điểm hơn thì điểm đối phương giảm dần; hết điểm là thua.',
        'Survival': 'Không căn cứ, không tháp: chỉ quân của bạn chống các đợt địch ngày càng mạnh; bị quét sạch hoặc để địch chiếm bãi là thua.',
        'Deathmatch': 'Tử chiến: hạ đủ số điểm tiêu diệt trước.',
        'KingOfTheHill': 'Vua đồi: giữ cứ điểm trung tâm để tích điểm.',
        'Assault': 'Công phá: người chơi đánh chiếm lần lượt 3 khu phòng thủ (A, B, C) trong quỹ thời gian; mỗi khu chiếm được cộng thêm giờ.',
        'Campaign': 'Chiến dịch 23 nhiệm vụ (xem phần 3).',
        'Siege': 'Công thành 3 giai đoạn: phá trạm radar tuyến ngoài → phá máy phát khiên trong tường → san phẳng sở chỉ huy; boss canh giữ xuất hiện ở giai đoạn 3.',
        'BossRush': 'Săn trùm: lần lượt 5 boss (Behemoth, Mega Gunship, Mobile Fortress, Drone Mothership, Silver Bug) kèm hộ tống.',
        'Defend': 'Phòng thủ căn cứ: pháo đài (tường, cổng, tháp, sở chỉ huy) là của bạn; địch công thành theo đúng 3 giai đoạn và được thả thêm các đợt quân; giữ tới khi địch hết giờ.',
        'Weekly': 'Pháo đài tuần: một cuộc công thành mà vòng thành đã phá được giữ nguyên cả tuần; thắng lần đầu trong tuần có thưởng.',
        'Endless': 'Vô tận: pháo đài của bạn trước các đợt địch không ngừng (mỗi 55 giây, to dần, tinh nhuệ dần); lưu kỷ lục đợt xa nhất.',
    }
    rows = [[f"<b>{esc(m['name'] or m['id'])}</b>", esc(m['sub']), esc(desc.get(m['id'], ''))] for m in game['modes']]
    out.append("<div class='section'><h2>2. Chế độ chơi</h2>" + table(['Chế độ', 'Tóm tắt', 'Luật'], rows)
               + "<p>Độ khó Dễ / Thường / Khó ảnh hưởng thu nhập và bộ bài của AI địch, tỷ lệ xe tinh nhuệ (10% / 25%) và hệ số thưởng (×0.7 / ×1 / ×1.45). "
               "Thời tiết (nắng, âm u, mưa, bão, tuyết, bão cát, sương mù, đêm) đổi dần trong 8 giây và ảnh hưởng tầm nhìn/hình ảnh.</p>"
               f"<div class='two'><div>{img(shots / 'siege.png', 'shot')}<div class='caption'>Công thành.</div></div>"
               f"<div>{img(shots / 'defend.png', 'shot')}<div class='caption'>Phòng thủ căn cứ.</div></div></div>"
               f"<div class='two'><div>{img(shots / 'boss.png', 'shot')}<div class='caption'>Boss.</div></div>"
               f"<div>{img(shots / 'hunt.png', 'shot')}<div class='caption'>Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ.</div></div></div></div>")

    # ------------------------------------------------------------------ campaign
    rows = [[m['id'], f"<b>{esc(m['name'])}</b><br><span class='muted'>{esc(m['brief'])}</span>", esc(m['map']),
             GOAL_VI.get(m['goal'], m['goal']) + (f"<br><span class='muted'>{esc(m['boss'])}</span>" if m['boss'] else ''),
             esc(m['difficulty']), f"{m['coins']} xu · {m['xp']} XP", esc(', '.join(m['unlocks']))] for m in game['campaign']]
    out.append("<div class='section'><h2>3. Chiến dịch</h2>"
               "<p>23 nhiệm vụ trên 12 bản đồ; cứ 3 nhiệm vụ có một trận boss. Mỗi nhiệm vụ có 3 sao (thắng, dưới thời gian, ít tổn thất hoặc thử thách riêng), "
               "3 cấp độ (Thường, Anh hùng: địch +30% CP/thu nhập, Thép: thêm cắt thu nhập của bạn và bỏ hỏa lực). "
               "Địch được <b>scale theo sức mạnh kho vũ khí của người chơi</b> (80% lợi thế trung bình của bộ bài, cả boss) và <b>được chi viện</b> bằng dù khi "
               "quân còn dưới 60% đỉnh hoặc khi người chơi vượt mốc tiến độ (cách nhau 75 giây, to dần, ưu tiên phòng không nếu người chơi nhiều máy bay).</p>"
               "<p>Loại nhiệm vụ: chiếm, giữ, phá hủy, hộ tống, trụ vững, boss, chặn tàu, săn mục tiêu (xe đánh dấu đi tuần), trinh sát (đưa xe vào từng cứ điểm 3 giây), "
               "bảo vệ công trình, bắn hạ máy bay.</p>"
               + table(['#', 'Nhiệm vụ', 'Bản đồ', 'Mục tiêu', 'Độ khó', 'Thưởng', 'Mở khóa'], rows)
               + f"{img(shots / 'campaign.png', 'shot')}<div class='caption'>Màn chiến dịch.</div></div>")

    # ------------------------------------------------------------------ vehicles
    groups = {}
    for v in game['vehicles']:
        key = 'Không quân' if v['flying'] else CLASS_VI.get(v['class'], v['class'])
        groups.setdefault(key, []).append(v)
    out.append("<div class='section'><h2>4. Phương tiện</h2><p>Chỉ số gốc (hạng 1, chưa trang bị). DPS = sát thương mỗi loạt / chu kỳ bắn, cộng mọi vũ khí, "
               "nhân hệ số giáp (phần 6). Hạng thẻ cộng +5% máu và sát thương mỗi hạng (tối đa hạng 10: +45%).</p>")
    for key, vs in groups.items():
        out.append(f"<h3>{esc(key)} ({len(vs)})</h3>")
        out.extend(vehicle_card(v, imgdir) for v in vs)
    out.append('</div>')

    # ------------------------------------------------------------------ DPS table
    rows = [[f"<b>{esc(v['short'])}</b>", CLASS_VI.get(v['class'], v['class']), ARMOR_VI.get(v['armor'], v['armor']), num(v['hp']), v['cost'],
             f"{v['speed']:g}", f"{max((w['range'] for w in v['weapons']), default=0):g}",
             f"{v['dpsVs']['Light']:.0f}", f"{v['dpsVs']['Heavy']:.0f}", f"{v['dpsVs']['Air']:.0f}", f"{v['dpsVs']['Structure']:.0f}",
             f"{(v['dpsVs']['Heavy'] / max(1, v['cost'])):.1f}"] for v in game['vehicles']]
    out.append("<div class='section'><h2>5. Bảng DPS tổng hợp</h2>"
               + table(['Xe', 'Lớp', 'Giáp', 'Máu', 'CP', 'Tốc độ', 'Tầm', 'DPS nhẹ', 'DPS nặng', 'DPS bay', 'DPS công trình', 'DPS nặng / CP'], rows, 'dps') + '</div>')

    # ------------------------------------------------------------------ weapons
    dt = game['damageTable']
    armors = ['Light', 'Heavy', 'Air', 'Structure']
    rows = [[TYPE_VI.get(t, t)] + [f"×{dt[t][a]:g}" for a in armors] for t in dt]
    weapons = {}
    for group in ('vehicles', 'elites', 'bosses', 'towers'):
        for v in game[group]:
            for w in v['weapons']:
                weapons.setdefault(w['id'], (w, v['short']))
    wrows = [[f"<code>{esc(w['id'])}</code>", TYPE_VI.get(w['type'], w['type']), num(w['damage']), w['burst'], f"{w['cooldown']:g}",
              f"{w['range']:g}", f"{w['minRange']:g}" if w['minRange'] else '', f"{w['splash']:g}" if w['splash'] else '',
              TARGET_VI.get(w['targets'], w['targets']), w['projectile'], f"{w['dps']:.0f}", esc(owner)] for w, owner in sorted(weapons.values(), key=lambda x: x[0]['id'])]
    out.append("<div class='section'><h2>6. Vũ khí và bảng sát thương</h2><h3>Hệ số sát thương theo loại đạn và loại giáp</h3>"
               + table(['Loại đạn'] + [ARMOR_VI[a] for a in armors], rows)
               + "<p>Giáp có hướng (giáp mặt trước dày hơn hông/sau), đạn lệch theo tầm và chuyển động, pháo có tầm tối thiểu. Máy bay có pháo sáng, "
               "xe có hệ thống đánh chặn chủ động (APS) chặn tên lửa/drone, tàng hình chỉ lộ ở 40% tầm nhìn khi không bắn.</p>"
               f"<h3>Toàn bộ vũ khí ({len(wrows)})</h3>"
               + table(['Vũ khí', 'Loại', 'Sát thương', 'Loạt', 'Hồi (s)', 'Tầm', 'Tối thiểu', 'Nổ lan', 'Mục tiêu', 'Đạn', 'DPS', 'Trên xe'], wrows) + '</div>')

    # ------------------------------------------------------------------ towers, elites, bosses
    def simple_rows(vs):
        return [[f"<b>{esc(v['name'])}</b>", ARMOR_VI.get(v['armor'], v['armor']), num(v['hp']), f"{v['speed']:g}",
                 esc(', '.join(w['id'] for w in v['weapons'])), f"{v['dpsVs']['Light']:.0f} / {v['dpsVs']['Heavy']:.0f} / {v['dpsVs']['Air']:.0f}",
                 esc(', '.join(v['skills']))] for v in vs]
    head = ['Tên', 'Giáp', 'Máu', 'Tốc độ', 'Vũ khí', 'DPS nhẹ/nặng/bay', 'Kỹ năng']
    out.append("<div class='section'><h2>7. Tháp canh, xe tinh nhuệ và boss</h2>"
               "<h3>Tháp và công sự</h3><p>Tháp cố định chặn lưới đường đi khi xuất hiện; trong Chiếm cứ điểm mỗi cứ điểm có tháp trung lập bắn mọi phe và dựng lại "
               "sau một thời gian; căn cứ có ụ phòng thủ (bastion) bất tử.</p>" + table(head, simple_rows(game['towers']))
               + "<h3>Xe tinh nhuệ</h3><p>Phiên bản tân trang: máu, sát thương và kỹ năng cao hơn, thanh máu vàng; địch có 10–25% xác suất nhận bản tinh nhuệ.</p>"
               + table(head, simple_rows(game['elites']))
               + "<h3>Boss</h3>" + ''.join(vehicle_card(v, imgdir) for v in game['bosses']) + '</div>')

    # ------------------------------------------------------------------ supports
    rows = [[f"<b>{esc(s['name'])}</b><br><span class='muted'>{esc(s['info'])}</span>", esc(s['kind']), s['cost'], f"{s['cooldown']:g} s",
             num(s['damage']) if s['damage'] else '', f"{s['radius']:g}" if s['radius'] else '', s['count'] or '',
             f"{s['duration']:g}" if s['duration'] else ''] for s in game['supports']]
    out.append("<div class='section'><h2>8. Hỗ trợ hỏa lực</h2><p>Thẻ hỗ trợ trong bộ bài (2 ô), gọi vào một điểm trên bản đồ; không gọi được vào vùng căn cứ địch; "
               "vật phẩm dùng một lần mua bằng xu.</p>" + table(['Hỗ trợ', 'Loại', 'CP', 'Hồi', 'Sát thương', 'Bán kính', 'Số lượng', 'Thời gian'], rows) + '</div>')

    # ------------------------------------------------------------------ gear
    g = game['gear']
    rar = ''.join(f"<span class='chip'><span class='rar' style='background:{RARITY_COL[i]}'></span>{RARITY_VI[i]} · cấp tối đa {g['levelCap'][i]}</span>"
                  for i in range(5))
    base_rows = []
    for b in g['bases']:
        icon = img(GEAR_ART / (b['id'] + '.png'), 'gearicon')
        implicit = fill(b['implicitName'], ['']) if b['implicitName'] else b['implicit']
        base_rows.append([icon, f"<b>{esc(b['name'] or b['id'])}</b>" + (' <span class="chip">đánh đổi</span>' if b['tradeOff'] else ''),
                          SLOT_VI.get(b['slot'], b['slot']), esc(implicit.replace('+%', '').strip()), pct_list(b['top'])])
    trait_rows = []
    for t in g['traits']:
        e = [f"{v * 100:g}" if isinstance(v, float) and v < 5 else f"{v:g}" for v in t['epic']]
        l = [f"{v * 100:g}" if isinstance(v, float) and v < 5 else f"{v:g}" for v in t['legendary']]
        values = [f"{a}/{b}" for a, b in zip(e, l)]
        trait_rows.append([f"<b>{esc(t['name'] or t['key'])}</b>", SLOT_VI.get(t['slot'], t['slot']), esc(fill(t['effect'], values))])
    mod_rows = [[img(GEAR_ART / (m['key'] + '.png'), 'gearicon'), f"<b>{esc(m['name'] or m['key'])}</b>", esc(fill(m['effect'], [f"{m['epic']:g}/{m['legendary']:g}"]))]
                for m in g['modules']]
    brand_rows = [[f"<b>{esc(b['name'])}</b>", esc(b['bonuses'])] for b in g['brands']]
    out.append("<div class='section'><h2>9. Trang bị</h2>"
               "<p>Mỗi nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân) có 7 ô: Vũ khí, Nạp đạn, Giáp, Quang học, Động cơ, Sửa chữa và Đặc biệt. "
               "Một món gồm: <b>loại đồ</b> (có dòng ẩn riêng), <b>chỉ số chính</b> tăng theo cấp (40% → 100%), <b>0/1/2/2/2 chỉ số phụ</b> theo độ hiếm "
               "(lăn 60–100%, có thanh chất lượng, tăng ở cấp 5/10/15/20), <b>một dòng unique</b> ở Sử thi và Huyền thoại (chọn 1 trong 3 khi ghép lên Sử thi), "
               "và <b>một thương hiệu</b> (bộ 2 món và 4 món). Ghép 3 món cùng ô cùng độ hiếm để lên bậc. Mỗi chỉ số có trần cho cả bộ.</p>"
               f"<p>{rar}</p>" + img(Path(imgdir) / 'shots' / 'gear.png', 'shot')
               + "<div class='caption'>Màn trang bị.</div>"
               + f"<h3>Loại đồ ({len(base_rows)})</h3>" + table(['', 'Loại', 'Ô', 'Dòng ẩn', 'Giá trị ở cấp tối đa (Thường → Huyền thoại)'], base_rows)
               + f"<h3>Dòng unique ({len(trait_rows)}) — giá trị Sử thi/Huyền thoại</h3>" + table(['Dòng', 'Ô', 'Hiệu ứng'], trait_rows)
               + f"<h3>Module đặc biệt ({len(mod_rows)})</h3>" + table(['', 'Module', 'Hiệu ứng (Sử thi/Huyền thoại)'], mod_rows)
               + f"<h3>Thương hiệu / bộ ({len(brand_rows)})</h3>" + table(['Thương hiệu', 'Thưởng bộ 2 và bộ 4'], brand_rows) + '</div>')

    # ------------------------------------------------------------------ economy
    e = game['economy']
    econ = balance.get('economy', {})
    rank_rows = [[i + 1, f"{e['rankBonus'][i] * 100:g}%", num(e['rankCoins'][i]) if i < len(e['rankCoins']) else '—',
                  e['rankPrints'][i] if i < len(e['rankPrints']) else '—'] for i in range(len(e['rankBonus']))]
    crate_names = ['Chiến trường', 'Bạc', 'Vàng', 'Huyền thoại']
    crate_rows = [[crate_names[i], num(e['crateCoinPrice'][i]) if e['crateCoinPrice'][i] else 'miễn phí / thưởng', e['crateRolls'][i],
                   f"{e['crateCoinsLow'][i]}–{e['crateCoinsHigh'][i]}", ' · '.join(f"{RARITY_VI[r]} {p * 100:g}%" for r, p in enumerate(e['crateOdds'][i]) if p > 0)]
                  for i in range(4)]
    pack_rows = [[esc(p['id']), num(p['coins']), esc(p['price'])] for p in e['coinPacks']]
    out.append("<div class='section'><h2>10. Kinh tế</h2><h3>Trong trận</h3>"
               f"<p><b>CP (điểm chỉ huy):</b> khởi đầu thường 12–34 CP tùy chế độ, thu nhập ~1 CP/giây × hệ số chung {econ.get('income', 1):g}, "
               "+0.25 CP/giây cho mỗi cứ điểm giữ được, kho tối đa 30 CP. <b>Tiếp tế:</b> quân vượt mức tiếp tế (24 CP × "
               f"{econ.get('supply', 1):g}) thì thu nhập giảm (tối đa −75%). <b>Hạ địch:</b> hoàn 25% giá xe bị hạ cho phe hạ. "
               "<b>Bắt kịp:</b> phe bị áp đảo được tăng thu nhập tới +50%. <b>Giới hạn:</b> 32 xe, 6 máy bay. Xe mua được thả dù sau 3,5 giây.</p>"
               "<h3>Ngoài trận (một loại tiền: xu)</h3>"
               "<p>Thưởng trận nhanh: thắng 120 / hòa 70 / thua 40 xu + 1,5 xu mỗi xe hạ (tối đa 120) + 4 xu mỗi phút (tối đa 15), × hệ số độ khó; XP = 80% xu. "
               "Sinh tồn/Vô tận: 30 + 18 × số đợt + 1,5 × số xe hạ. Nhiệm vụ: thưởng theo sao và cấp độ. Thử thách hằng ngày 3 nhiệm vụ.</p>"
               "<h3>Hạng thẻ</h3>" + table(['Hạng', 'Thưởng máu/sát thương', 'Xu lên hạng tiếp', 'Bản thiết kế'], rank_rows)
               + "<h3>Hòm đồ</h3><p>Giữ nguyên mua bằng xu (quyết định của chủ dự án). Có cơ chế bảo hiểm (pity) cho Sử thi/Huyền thoại, tỷ lệ công khai trong game.</p>"
               + table(['Hòm', 'Giá (xu)', 'Số món', 'Xu kèm', 'Tỷ lệ độ hiếm mỗi món'], crate_rows)
               + "<h3>Gói xu</h3>" + table(['Gói', 'Xu', 'Giá'], pack_rows)
               + f"{img(shots / 'shop.png', 'shot')}<div class='caption'>Cửa hàng.</div></div>")

    # ------------------------------------------------------------------ maps
    out.append("<div class='section'><h2>11. Bản đồ</h2><p>12 chiến trường 300 × 300 m (đã phóng to 50%), đường viền không đều; phần ngoài viền vẫn được dựng "
               "như bản đồ (nhà, rừng, đá) chỉ để trang trí, ranh giới là đường đứt nét. Phiên bản công thành đặt pháo đài 3 vòng ở góc đông bắc: tuyến ngoài "
               "(boong-ke, tháp, trạm radar), vòng tường (cổng 10 m, máy phát khiên), thành trong (sở chỉ huy, boss canh giữ). Khoảng 11 loại tháp và công sự.</p>")
    for m in game['maps']:
        out.append(f"<div class='map'><h3>{esc(m['name'])} <span class='muted'>· {esc(m['theme'])}</span></h3><p>{esc(m['sub'])}</p>"
                   f"{img(imgdir / 'maps' / (m['id'] + '.png'), '')}</div>")
    out.append(f"<h3>Pháo đài (Ashfield, bản công thành)</h3>{img(imgdir / 'maps' / 'ashfield_siege.png', '')}</div>")

    # ------------------------------------------------------------------ AI and systems
    out.append("<div class='section'><h2>12. AI và hệ thống</h2><ul>"
               "<li><b>Chỉ huy AI</b> (cho cả hai phe): chọn mục tiêu, tập hợp quân rồi tiến theo nhóm, giữ/chiếm cứ điểm, gọi hỏa lực vào cụm địch (không vào quân mình), "
               "mua quân khắc chế (địch nhiều máy bay → mua phòng không, nhiều giáp → mua diệt tăng...).</li>"
               "<li><b>Giao thông:</b> bản đồ làn đường (đường, lộ trình chính, lối hẹp, cổng), cấm đỗ ở cổng/lối hẹp, xe đang đỗ nhường đường theo ưu tiên, "
               "nhóm cùng đích không bắt nhau nhường, luân phiên qua cổng, tìm đường vòng có tính chi phí khi bị kẹt.</li>"
               "<li><b>Chiến đấu:</b> giáp có hướng, tầm tối thiểu cho pháo, đạn xuyên (railgun), laser, tên lửa dẫn đường, pháo sáng, APS, tàng hình, EMP, khói, mìn, "
               "xe tự sát, drone, rơi máy bay gây sát thương, xác xe cháy.</li>"
               "<li><b>Trang bị trong trận:</b> 42 dòng unique móc vào các sự kiện bắn, trúng, hạ, chết, đứng yên, đổi mục tiêu; hệ thống trạng thái (cháy, chậm, "
               "xé giáp, đánh dấu, khiên); hiện chữ nhỏ trên xe khi kích hoạt.</li>"
               "<li><b>Chiến dịch:</b> địch scale theo kho vũ khí người chơi, chi viện bằng dù, dấu mục tiêu trên chiến trường và bản đồ nhỏ.</li>"
               "<li><b>Kiểm thử:</b> 362 bài test tự động (338 chạy, 24 bài cân bằng/xuất dữ liệu chạy tay). Cân bằng chiến dịch chạy 5 seed mỗi nhiệm vụ.</li></ul></div>")

    # ------------------------------------------------------------------ UI
    ui = [('home.png', 'Trang chủ: trận đấu AI làm nền, cột thẻ bên phải, nút XUẤT KÍCH.'), ('army.png', 'Quân đội: bộ bài và bộ sưu tập.'),
          ('detail.png', 'Chi tiết phương tiện: mô hình 3D xoay, chỉ số, vũ khí, xem bắn, trang bị.'), ('gear.png', 'Trang bị.'),
          ('setup.png', 'Thiết lập trận: chế độ, bản đồ, độ khó, thời tiết.'), ('events.png', 'Sự kiện.'), ('shop.png', 'Cửa hàng.'),
          ('settings.png', 'Cài đặt đồ họa và âm thanh.'), ('result.png', 'Màn kết quả trận.'),
          ('edge.png', 'Mép bản đồ: đường ranh giới và cảnh ngoài viền.')]
    out.append("<div class='section'><h2>13. Giao diện</h2><p>Phong cách “Field Command”: nền xám thép trong suốt trên trận đấu, viền mảnh, góc vuông, một màu nhấn cam "
               "cho hành động chính (góc vát), chữ in hoa hẹp. Thanh điều hướng dọc bên trái.</p>")
    for name, cap in ui:
        tag = img(shots / name, 'shot')
        if tag:
            out.append(f"{tag}<div class='caption'>{esc(cap)}</div>")
    out.append('</div></body></html>')
    return '\n'.join(out)


def main():
    game_json, imgdir, pdf = sys.argv[1], sys.argv[2], sys.argv[3]
    game = json.loads(Path(game_json).read_text(encoding='utf-8'))
    page = Path(pdf).with_suffix('.html')
    page.write_text(build(game, imgdir), encoding='utf-8')
    subprocess.run([EDGE, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={Path(pdf).resolve()}', page.resolve().as_uri()],
                   check=True, timeout=600)
    print('wrote', pdf)


if __name__ == '__main__':
    main()
