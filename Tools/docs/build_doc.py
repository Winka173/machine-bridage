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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import programme  # noqa: E402

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


CACHE = None
SIZES = {'thumb': 640, 'gearicon': 128, 'shot': 1500, '': 1300}


def img(path, cls='', alt=''):
    """An image, shrunk and saved as JPEG in the cache (PNG kept for small icons with transparency)."""
    from PIL import Image
    p = Path(path)
    if not p.exists():
        return ''
    width = SIZES.get(cls, 1300)
    icon = cls == 'gearicon'
    out = CACHE / (p.parent.name + '_' + p.stem + ('.png' if icon else '.jpg'))
    if not out.exists():
        im = Image.open(p)
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        if icon:
            im.save(out)
        else:
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[3] if im.mode == 'RGBA' else None)
            bg.save(out, quality=84, optimize=True)
    return f'<img class="{cls}" src="{out.as_uri()}" alt="{esc(alt)}">'


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
.card img.thumb { width: 170pt; height: 120pt; object-fit: contain; border: 1px solid #e0e3e5; background: #ffffff; }
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
.guide { font-size: 9pt; margin-top: 3pt; border-left: 2px solid #f2a33a; padding-left: 5pt; }
.guide div { margin: 1pt 0; }
.guide .hl { color: #b86e0b; font-weight: 700; }
"""


def guide_html(text):
    """The Guide tab's four lines, key words ([[word]]) highlighted."""
    if not text:
        return ''
    lines = [re.sub(r'\[\[(.+?)\]\]', lambda m: f"<span class='hl'>{m.group(1)}</span>", esc(line)) for line in text.split('\n')]
    return "<div class='guide'>" + ''.join(f"<div>{'<b>' + l + '</b>' if i == 0 else l}</div>" for i, l in enumerate(lines)) + "</div>"


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
    # The game's own card render (Resources/UI/Cards, 512 px, transparent), else a hero render.
    card = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Cards' / (v['model'] + '.png')
    thumb = img(card, 'thumb', v['name']) if card.exists() else img(Path(imgdir) / 'veh' / (v['model'] + '.png'), 'thumb', v['name'])
    return (f"<div class='card'><div class='head' style='{'' if thumb else 'grid-template-columns: 1fr'}'>{thumb}"
            f"<div><div class='name'>{esc(v['name'])}</div><div class='meta'>{CLASS_VI.get(v['class'], v['class'])}"
            f"{' · bay' if v['flying'] else ''} · id <code>{esc(v['id'])}</code></div>{stats}"
            f"{guide_html(v.get('guide', ''))}<div class='note'>{esc(v['note'])}</div>{('<div>' + skills + '</div>') if skills else ''}</div></div>"
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
               "<li>Nhiệm vụ nhiều giai đoạn</li><li>Tác chiến</li><li>Căn cứ và tháp</li><li>Công thành và Phòng thủ</li>"
               "<li>Phương tiện (thẻ chi tiết)</li><li>Bảng DPS tổng hợp</li><li>Vũ khí và bảng sát thương</li><li>Tháp canh, xe tinh nhuệ và boss</li>"
               "<li>Hỗ trợ hỏa lực</li><li>Trang bị</li><li>Kinh tế</li><li>Bản đồ</li><li>AI và hệ thống</li><li>Kiểm thử và phép đo còn lại</li>"
               "<li>Giao diện</li><li>Hình ảnh</li></ol></div>")

    # ------------------------------------------------------------------ overview
    out.append("<div class='section'><h2>1. Tổng quan</h2>"
               "<p><b>Thể loại:</b> RTS / auto-battler trên điện thoại (màn ngang). Người chơi chỉ huy một binh đoàn phương tiện: xe tăng, xe bọc thép, "
               "pháo, phòng không, trực thăng, máy bay. Trận đấu phần lớn tự chạy: chỉ huy AI của người chơi tự mua quân (Tự mua) và tự gọi hỏa lực (Yểm trợ); "
               "người chơi can thiệp bằng lệnh Tấn công / Phòng thủ, chọn thẻ để triển khai, gọi hỏa lực vào điểm chọn.</p>"
               "<p><b>Vòng lặp:</b> điểm chỉ huy (CP) tăng theo thời gian và cứ điểm giữ được → mua phương tiện từ bộ bài (8 xe + 2 hỗ trợ) → phương tiện "
               "được thả dù xuống bãi thả của phe → chiến đấu tự động theo hệ thống khắc chế giáp/đạn → hạ địch được hoàn một phần CP.</p>"
               f"<p><b>Ngoài trận:</b> lên hạng thẻ (bản thiết kế + xu), trang bị theo nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân), căn cứ (loadout tháp theo ô cỡ), "
               f"hòm đồ, chiến dịch {len(game['campaign'])} nhiệm vụ trong {len(game['chapters'])} chương, Tác chiến (chơi lại chiến dịch lớn, 4 cấp độ, mutator tuần), "
               "Pháo đài tuần, Săn trùm, Vô tận, Sinh tồn. Một loại tiền duy nhất: xu.</p>"
               f"<p><b>Bản đồ:</b> {len(game['maps'])} chiến trường 300 × 300 m, mỗi bản có phiên bản chiếm cứ điểm, sinh tồn và công thành. "
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
        'Campaign': 'Chiến dịch 9 chương, 108 nhiệm vụ (xem phần 3); chơi lại các trận lớn ở Tác chiến (phần 5).',
        'Siege': 'Công thành: pháo đài chiếm 45% bản đồ, 3 giai đoạn (trạm radar tuyến ngoài → máy phát khiên trong tường → sở chỉ huy), cổng, tường sập, vòm khiên, '
                 'siêu pháo, chi viện bằng tàu hỏa hoặc đường băng (phần 7).',
        'BossRush': 'Săn trùm: lần lượt 5 loại boss kèm hộ tống, mỗi loại bốc ngẫu nhiên 1 biến thể: xe tăng siêu nặng (Behemoth / Inferno / Tempest), '
                    'trực thăng-máy bay pháo (Chim sắt / Spectre), pháo đài di động (Pháo đài băng / Hive / Bastion), phi thuyền drone, đĩa bay Silver Bug. '
                    'Thưởng CP khi boss mất 25/50/75% máu (8 CP mỗi mốc) và 12 CP khi hạ; không có không kích ngẫu nhiên.',
        'Defend': 'Phòng thủ: pháo đài là loadout căn cứ của bạn, ba tuyến lùi (mất tuyến được thưởng CP rút lui) và sở chỉ huy là trận chốt; đợt địch hiện trước bằng icon.',
        'Weekly': 'Pháo đài tuần: một cuộc công thành mà vòng thành đã phá được giữ nguyên cả tuần; thắng lần đầu trong tuần có thưởng.',
        'Endless': 'Vô tận: pháo đài của bạn trước các đợt địch không ngừng (mỗi 55 giây, to dần, tinh nhuệ dần); lưu kỷ lục đợt xa nhất.',
    }
    rows = [[f"<b>{esc(m['name'] or m['id'])}</b>", esc(m['sub']), esc(desc.get(m['id'], ''))] for m in game['modes']]
    out.append("<div class='section'><h2>2. Chế độ chơi</h2>" + table(['Chế độ', 'Tóm tắt', 'Luật'], rows)
               + "<p>Độ khó Dễ / Thường / Khó ảnh hưởng thu nhập và bộ bài của AI địch, ngân sách xe tinh nhuệ (5–25% chi tiêu, trần 1–5 xe cùng lúc) và hệ số thưởng (×0.7 / ×1 / ×1.45). "
               "Thời tiết (nắng, âm u, mưa, bão, tuyết, bão cát, sương mù, đêm) đổi dần trong 8 giây và ảnh hưởng tầm nhìn/hình ảnh.</p>"
               f"<div class='two'><div>{img(shots / 'siege.png', 'shot')}<div class='caption'>Công thành.</div></div>"
               f"<div>{img(shots / 'defend.png', 'shot')}<div class='caption'>Phòng thủ căn cứ.</div></div></div>"
               f"<div class='two'><div>{img(shots / 'boss.png', 'shot')}<div class='caption'>Boss.</div></div>"
               f"<div>{img(shots / 'hunt.png', 'shot')}<div class='caption'>Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ.</div></div></div></div>")

    # ------------------------------------------------------------------ campaign and the programme (prompts 1-6)
    h = {'esc': esc, 'table': table, 'img': img, 'num': num, 'guide_html': guide_html, 'GOAL_VI': GOAL_VI}
    out.append(programme.campaign(game, h))
    out.append(programme.multistage(game, h))
    out.append(programme.operations(game, h))
    out.append(programme.bases(game, h))
    out.append(programme.siege(game, h))

    # ------------------------------------------------------------------ vehicles
    groups = {}
    for v in game['vehicles']:
        key = 'Không quân' if v['flying'] else CLASS_VI.get(v['class'], v['class'])
        groups.setdefault(key, []).append(v)
    out.append("<div class='section'><h2>8. Phương tiện</h2><p>Chỉ số gốc (hạng 1, chưa trang bị). DPS = sát thương mỗi loạt / chu kỳ bắn, cộng mọi vũ khí, "
               "nhân hệ số giáp (phần 10). Hạng thẻ cộng +5% máu và sát thương mỗi hạng (tối đa hạng 10: +45%).</p>")
    out.append(f"{img(imgdir / 'shots' / 'hd.png', 'shot')}<div class='caption'>Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất.</div>")
    for key, vs in groups.items():
        out.append(f"<h3>{esc(key)} ({len(vs)})</h3>")
        out.extend(vehicle_card(v, imgdir) for v in vs)
    out.append('</div>')

    # ------------------------------------------------------------------ DPS table
    rows = [[f"<b>{esc(v['short'])}</b>", CLASS_VI.get(v['class'], v['class']), ARMOR_VI.get(v['armor'], v['armor']), num(v['hp']), v['cost'],
             f"{v['speed']:g}", f"{max((w['range'] for w in v['weapons']), default=0):g}",
             f"{v['dpsVs']['Light']:.0f}", f"{v['dpsVs']['Heavy']:.0f}", f"{v['dpsVs']['Air']:.0f}", f"{v['dpsVs']['Structure']:.0f}",
             f"{(v['dpsVs']['Heavy'] / max(1, v['cost'])):.1f}"] for v in game['vehicles']]
    out.append("<div class='section'><h2>9. Bảng DPS tổng hợp</h2>"
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
    out.append("<div class='section'><h2>10. Vũ khí và bảng sát thương</h2><h3>Hệ số sát thương theo loại đạn và loại giáp</h3>"
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
    out.append("<div class='section'><h2>11. Tháp canh, xe tinh nhuệ và boss</h2>"
               "<h3>Tháp và công sự</h3><p>Tháp cố định chặn lưới đường đi khi xuất hiện; trong Chiếm cứ điểm mỗi cứ điểm có tháp trung lập bắn mọi phe và dựng lại "
               "sau một thời gian; căn cứ có ụ phòng thủ (bastion) bất tử.</p>" + table(head, simple_rows(game['towers']))
               + "<h3>Xe tinh nhuệ</h3><p>Phiên bản tân trang: +60% máu, +25% sát thương, 1–2 kỹ năng tinh nhuệ, thanh máu vàng và vòng vàng trên bản đồ nhỏ; "
               "sức mạnh thực đo được 1,8–2,2 lần bản thường. Địch không còn nhận tinh nhuệ theo xác suất mà theo <b>ngân sách</b>: tinh nhuệ giá 1,6 lần, phần chi tiêu "
               "theo độ khó (Dễ 5%, Thường 10%, Khó 15%, Anh hùng 20%, Thép 25%), trần 1–5 xe cùng lúc; tướng ưu tiên loại xe của mình. Hạ tinh nhuệ hoàn CP theo giá thật "
               "và thưởng một ít xu, có tỷ lệ nhỏ rơi bản thiết kế.</p>"
               + table(head, simple_rows(game['elites']))
               + "<h3>Boss</h3><p>Boss có bộ phận riêng (máu riêng, gắn vũ khí hoặc kỹ năng; vỡ thì vũ khí đó im và thân mất thêm máu; chỉ phát trúng trực tiếp làm hại "
               "bộ phận) và boss cuối chương có thanh máu nhiều pha. Số bộ phận và vạch pha ghi trên từng thẻ.</p>"
               + ''.join(vehicle_card(v, imgdir) + (f"<p class='muted'>Bộ phận: {esc(', '.join(p['kind'] for p in v['parts']))}" if v.get('parts') else "<p class='muted'>")
                         + (f" · pha ở {', '.join(f'{x * 100:g}%' for x in v['phases'])}" if v.get('phases') else '') + (f" · {esc(v['bossFile'])}" if v.get('bossFile') else '')
                         + "</p>" for v in game['bosses']) + '</div>')

    # ------------------------------------------------------------------ supports
    rows = [[f"<b>{esc(s['name'])}</b><br><span class='muted'>{esc(s['info'])}</span>{guide_html(s.get('guide', ''))}", esc(s['kind']), s['cost'], f"{s['cooldown']:g} s",
             num(s['damage']) if s['damage'] else '', f"{s['radius']:g}" if s['radius'] else '', s['count'] or '',
             f"{s['duration']:g}" if s['duration'] else ''] for s in game['supports']]
    out.append("<div class='section'><h2>12. Hỗ trợ hỏa lực</h2><p>Thẻ hỗ trợ trong bộ bài (2 ô), gọi vào một điểm trên bản đồ; không gọi được vào vùng căn cứ địch; "
               "vật phẩm dùng một lần mua bằng xu. Mỗi thẻ hỗ trợ có clip Xem bắn riêng (gọi hỏa lực lên một cụm mục tiêu).</p>"
               + table(['Hỗ trợ', 'Loại', 'CP', 'Hồi', 'Sát thương', 'Bán kính', 'Số lượng', 'Thời gian'], rows)
               + f"{img(imgdir / 'r6' / 'supports.png', 'shot')}<div class='caption'>Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, "
               "ném bom rải thảm, MOAB, bom chùm, máy bay pháo, EMP, khói, tiếp tế, chi viện).</div></div>")

    # ------------------------------------------------------------------ gear
    g = game['gear']
    rar = ''.join(f"<span class='chip'><span class='rar' style='background:{RARITY_COL[i]}'></span>{RARITY_VI[i]} · cấp tối đa {g['levelCap'][i]}</span>"
                  for i in range(5))
    base_rows = []
    for b in g['bases']:
        icon = img(GEAR_ART / (b['id'] + '.png'), 'gearicon')
        values = ' / '.join(b.get('lines') or [f"{v * 100:g}%" for v in b['top']])
        penalty = f"<br><span class='muted'>{esc(b['penaltyLine'])}</span>" if b.get('penaltyLine') else ''
        base_rows.append([icon, f"<b>{esc(b['name'] or b['id'])}</b>" + (' <span class="chip">đánh đổi</span>' if b['tradeOff'] else ''),
                          SLOT_VI.get(b['slot'], b['slot']), esc(b['implicitName']) + penalty, esc(values)])
    trait_rows = []
    for t in g['traits']:
        e = [f"{v * 100:g}" if isinstance(v, float) and v < 5 else f"{v:g}" for v in t['epic']]
        l = [f"{v * 100:g}" if isinstance(v, float) and v < 5 else f"{v:g}" for v in t['legendary']]
        values = [f"{a}/{b}" for a, b in zip(e, l)]
        effect = (f"<b>Sử thi:</b> {esc(t['effectEpic'])}<br><b>Huyền thoại:</b> {esc(t['effectLegendary'])}" if t.get('effectEpic')
                  else esc(fill(t['effect'], values)))
        trait_rows.append([f"<b>{esc(t['name'] or t['key'])}</b>", SLOT_VI.get(t['slot'], t['slot']), effect])
    def share(v):
        return f"{v * 100:g}" if 0 < v < 1 else f"{v:g}"
    mod_rows = [[img(GEAR_ART / (m['key'] + '.png'), 'gearicon'), f"<b>{esc(m['name'] or m['key'])}</b>",
                 esc(fill(m['effect'], [f"{share(m['epic'])}/{share(m['legendary'])}"]))] for m in g['modules']]
    brand_rows = [[f"<b>{esc(b['name'])}</b>", esc(b['bonuses'])] for b in g['brands']]
    out.append("<div class='section'><h2>13. Trang bị</h2>"
               "<p>Mỗi nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân) có 7 ô: Vũ khí, Nạp đạn, Giáp, Quang học, Động cơ, Sửa chữa và Đặc biệt. "
               "Một món gồm: <b>loại đồ</b> (có dòng ẩn riêng), <b>chỉ số chính</b> tăng theo cấp (40% → 100%), <b>0/1/2/2/2 chỉ số phụ</b> theo độ hiếm "
               "(lăn 60–100%, có thanh chất lượng, tăng ở cấp 5/10/15/20), <b>một dòng unique</b> ở Sử thi và Huyền thoại (chọn 1 trong 3 khi ghép lên Sử thi), "
               "và <b>một thương hiệu</b> (bộ 2 món và 4 món). Ghép 3 món cùng ô cùng độ hiếm để lên bậc. Mỗi chỉ số có trần cho cả bộ.</p>"
               f"<p>{rar}</p>" + img(Path(imgdir) / 'shots' / 'gear.png', 'shot')
               + "<div class='caption'>Màn trang bị.</div>"
               + f"<h3>Loại đồ ({len(base_rows)})</h3>" + table(['', 'Loại', 'Ô', 'Dòng ẩn (Huyền thoại, cấp tối đa)', 'Thường → Huyền thoại'], base_rows)
               + f"<h3>Dòng unique ({len(trait_rows)})</h3>" + table(['Dòng', 'Ô', 'Hiệu ứng'], trait_rows)
               + f"<h3>Module đặc biệt ({len(mod_rows)})</h3>" + table(['', 'Module', 'Hiệu ứng (Sử thi/Huyền thoại)'], mod_rows)
               + f"<h3>Thương hiệu / bộ ({len(brand_rows)})</h3>" + table(['Thương hiệu', 'Thưởng bộ 2 và bộ 4'], brand_rows) + '</div>')

    # ------------------------------------------------------------------ economy
    e = game['economy']
    econ = balance.get('economy', {})
    rank_rows = [[i + 1, f"{e['rankBonus'][i] * 100:g}%", f"−{e['rankCut'][i] / 100:g}%" if e.get('rankCut') and e['rankCut'][i] else '—',
                  num(e['rankCoins'][i]) if i < len(e['rankCoins']) else '—',
                  e['rankPrints'][i] if i < len(e['rankPrints']) else '—'] for i in range(len(e['rankBonus']))]
    cost_rows = [[c['cost'], c['rank7'], c['rank9']] for c in e.get('callCost', [])]
    mode_econ = [
        ['Chiếm cứ điểm, Tử chiến, Vua đồi', '18 CP', '1,35 × 0,95', 'Hai phe như nhau'],
        ['Công phá (Assault)', '16 CP', '1,2 × 0,95', ''],
        ['Công thành (người chơi tấn công)', '34 CP (kho 40)', '1,8 × 0,95', 'Thưởng CP mỗi giai đoạn'],
        ['Phòng thủ / Vô tận (người chơi giữ)', '24 CP', '1,2 × 0,95', 'Vô tận: người chơi +2%/đợt (tối đa +30%), địch +4%/đợt'],
        ['Sinh tồn', '16 CP', '0,9 × 0,95', 'Chỉ có quân, không căn cứ'],
        ['Săn trùm (Boss Rush)', '40 CP (kho 45)', '2,0 × 0,95 (Khó 1,75)', '8 CP ở mỗi mốc 75/50/25% máu boss + 12 CP khi hạ'],
        ['Chiến dịch', 'theo nhiệm vụ', 'theo nhiệm vụ × 0,95', 'Địch nhận 80% mức giảm giá bộ bài của người chơi thành thu nhập'],
    ]
    crate_names = ['Chiến trường', 'Bạc', 'Vàng', 'Huyền thoại']
    crate_rows = [[crate_names[i], num(e['crateCoinPrice'][i]) if e['crateCoinPrice'][i] else 'miễn phí / thưởng', e['crateRolls'][i],
                   f"{e['crateCoinsLow'][i]}–{e['crateCoinsHigh'][i]}", ' · '.join(f"{RARITY_VI[r]} {p * 100:g}%" for r, p in enumerate(e['crateOdds'][i]) if p > 0)]
                  for i in range(4)]
    pack_rows = [[esc(p['id']), num(p['coins']), esc(p['price'])] for p in e['coinPacks']]
    out.append("<div class='section'><h2>14. Kinh tế</h2><h3>Trong trận</h3>"
               f"<p><b>CP (điểm chỉ huy):</b> khởi đầu thường 12–34 CP tùy chế độ, thu nhập ~1 CP/giây × hệ số chung {econ.get('income', 1):g}, "
               "+0.25 CP/giây cho mỗi cứ điểm giữ được, kho tối đa 30 CP. <b>Tiếp tế:</b> quân vượt mức tiếp tế (24 CP × "
               f"{econ.get('supply', 1):g}) thì thu nhập giảm (tối đa −75%). <b>Hạ địch:</b> hoàn 25% giá xe bị hạ cho phe hạ. "
               "<b>Bắt kịp:</b> phe bị áp đảo được tăng thu nhập tới +50%. <b>Giới hạn:</b> 32 xe, 6 máy bay. Xe mua được thả dù sau 3,5 giây.</p>"
               "<h3>Ngoài trận (một loại tiền: xu)</h3>"
               "<p>Thưởng trận nhanh: thắng 120 / hòa 70 / thua 40 xu + 1,5 xu mỗi xe hạ (tối đa 120) + 4 xu mỗi phút (tối đa 15), × hệ số độ khó; XP = 80% xu. "
               "Sinh tồn/Vô tận: 30 + 18 × số đợt + 1,5 × số xe hạ. Nhiệm vụ: thưởng theo sao và cấp độ. Thử thách hằng ngày 3 nhiệm vụ.</p>"
               "<h3>Thu nhập theo chế độ (vòng 6: tăng vừa phải 12–26%)</h3>"
               "<p>Hệ số chung: thu nhập 0,85 → <b>0,95</b>, tiếp tế 0,9 → <b>1,05</b> (nhiều xe trên sân hơn khoảng 12%). Tham khảo: elixir của Clash Royale "
               "(tăng x2/x3 cuối trận), Potential của Arknights (giảm giá nhỏ theo bậc, có trần), Boss Rush của BTD6 (thưởng khi gây sát thương cho boss). "
               "Tiêm kích 12 → 10 CP, cường kích 13 CP, xe rùa 8 CP; pháo phòng không của boss 27 → 21 sát thương/viên; máy bay VTOL không dừng lơ lửng "
               "trong tầm pháo phòng không; AI không mua tiêm kích khi địch không có máy bay.</p>"
               + table(['Chế độ', 'CP khởi đầu', 'Thu nhập (CP/giây)', 'Ghi chú'], mode_econ)
               + "<h3>Hạng thẻ</h3><p>Từ hạng 7 thẻ rẻ hơn 5%, từ hạng 9 rẻ hơn 10% khi gọi (làm tròn CP nguyên, thẻ ≤ 5 CP không đổi). Giá trị quân, "
               "phí tiếp tế và tiền hoàn khi bị hạ vẫn tính theo giá gốc.</p>"
               + table(['Hạng', 'Thưởng máu/sát thương', 'Giảm giá gọi', 'Xu lên hạng tiếp', 'Bản thiết kế'], rank_rows)
               + table(['Giá gốc (CP)', 'Hạng 7–8', 'Hạng 9–10'], cost_rows)
               + "<h3>Hòm đồ</h3><p>Giữ nguyên mua bằng xu (quyết định của chủ dự án). Có cơ chế bảo hiểm (pity) cho Sử thi/Huyền thoại, tỷ lệ công khai trong game.</p>"
               + table(['Hòm', 'Giá (xu)', 'Số món', 'Xu kèm', 'Tỷ lệ độ hiếm mỗi món'], crate_rows)
               + "<h3>Gói xu</h3>" + table(['Gói', 'Xu', 'Giá'], pack_rows)
               + f"{img(shots / 'shop.png', 'shot')}<div class='caption'>Cửa hàng.</div></div>")

    # ------------------------------------------------------------------ maps
    out.append(f"<div class='section'><h2>15. Bản đồ</h2><p>{len(game['maps'])} chiến trường 300 × 300 m (8 bản đồ mới: Bãi Đổ Bộ, Đập Thủy Điện, Thủ Đô, Bãi Phóng Silver Bug, "
               "Sa Mạc Muối, Cầu Biên Giới, Đầm Lầy, Quần Đảo San Hô), đường viền không đều; phần ngoài viền vẫn được dựng "
               "như bản đồ (nhà, rừng, đá) chỉ để trang trí, ranh giới là đường đứt nét. Mỗi trại có sở chỉ huy và ô tháp nhỏ/vừa/lớn/tiện ích; mỗi cứ điểm có tiền đồn. "
               "Phiên bản công thành đặt pháo đài chiếm 45% bản đồ ở đông bắc (phần 7).</p>")
    for m in game['maps']:
        out.append(f"<div class='map'><h3>{esc(m['name'])} <span class='muted'>· {esc(m['theme'])}</span></h3><p>{esc(m['sub'])}</p>"
                   f"{img(imgdir / 'maps' / (m['id'] + '.png'), '')}</div>")
    out.append(f"<h3>Pháo đài (Ashfield, bản công thành)</h3>{img(imgdir / 'maps' / 'ashfield_siege.png', '')}</div>")

    # ------------------------------------------------------------------ AI and systems
    out.append("<div class='section'><h2>16. AI và hệ thống</h2><ul>"
               "<li><b>Chỉ huy AI</b> (cho cả hai phe): chọn mục tiêu, tập hợp quân rồi tiến theo nhóm, giữ/chiếm cứ điểm, gọi hỏa lực vào cụm địch (không vào quân mình), "
               "mua quân khắc chế (địch nhiều máy bay → mua phòng không, nhiều giáp → mua diệt tăng...).</li>"
               "<li><b>Giao thông:</b> bản đồ làn đường (đường, lộ trình chính, lối hẹp, cổng), cấm đỗ ở cổng/lối hẹp, xe đang đỗ nhường đường theo ưu tiên, "
               "nhóm cùng đích không bắt nhau nhường, luân phiên qua cổng, tìm đường vòng có tính chi phí khi bị kẹt.</li>"
               "<li><b>Chiến đấu:</b> giáp có hướng, tầm tối thiểu cho pháo, đạn xuyên (railgun), laser, tên lửa dẫn đường, pháo sáng, APS, tàng hình, EMP, khói, mìn, "
               "xe tự sát, drone, rơi máy bay gây sát thương, xác xe cháy.</li>"
               "<li><b>Trang bị trong trận:</b> 42 dòng unique móc vào các sự kiện bắn, trúng, hạ, chết, đứng yên, đổi mục tiêu; hệ thống trạng thái (cháy, chậm, "
               "xé giáp, đánh dấu, khiên); hiện chữ nhỏ trên xe khi kích hoạt.</li>"
               "<li><b>Chiến dịch:</b> địch scale theo kho vũ khí người chơi, chi viện bằng dù, dấu mục tiêu trên chiến trường và bản đồ nhỏ.</li>"
               "<li><b>Nhịp bắn (vòng 6):</b> các vũ khí của một xe không bao giờ bắn cùng lúc: súng máy nghỉ quanh mỗi phát pháo/tên lửa và mỗi loạt, "
               "hai súng máy thay phiên, vũ khí nặng đã ngắm được ưu tiên. Súng (trừ súng máy, pháo phòng không) bắn chậm hơn 30% và mạnh hơn tương ứng "
               "(giữ nguyên DPS). Pháo phòng không bắn loạt 8–16 viên (16–25 viên/giây) rồi nghỉ. Xe tăng hết mục tiêu mặt đất thì dùng súng máy đồng trục "
               "bắn máy bay. Railgun nạp năng lượng 0,9 giây rồi bắn xuyên hàng.</li>"
               "<li><b>Đạn và vụ nổ:</b> 35 mô hình đạn riêng (TOW, Kornet, Ataka, Hellfire, Stinger, Igla, Pantsir, AIM-9, R-60, AIM-120, Patriot, Buk, Maverick, "
               "JASSM, Hydra, S-8, Grad, GMLRS, TOS, Mk 84, FAB, GBU-12, JDAM, Lancet, Shahed, đạn xuyên, đạn nổ lõm, đạn pháo 155, đạn cối, đạn railgun); "
               "tên lửa rời bệ chậm rồi tăng tốc (1–1,5 giây cho phát bắn 40–60 m). Vụ nổ theo loại: đạn xuyên tóe lửa, đạn lõm chớp sáng, đạn nổ tung đất và khói đen, "
               "nhiệt áp bùng quả cầu lửa thứ hai, bom có vòng sóng xung kích và cột bụi; boss nổ nhiều đợt rồi lóe trắng toàn màn hình.</li>"
               "<li><b>Âm thanh:</b> nhạc nền tự sáng tác bằng script (Tools/music: MIDI + FluidSynth + SoundFont FluidR3 giấy phép MIT, không dùng AI): "
               "menu, 3 bản trận đấu, công thành, boss, thắng, thua; có mức âm lượng nhạc riêng. Clip Xem bắn có tiếng súng.</li>"
               "<li><b>Bản đồ nhỏ:</b> hiện mọi xe địch (ngoài tầm nhìn thì mờ), boss là vòng đỏ nhấp nháy.</li>"
               "<li><b>LOD:</b> xe nhỏ trên màn hình dùng mô hình đơn giản hóa (31% tam giác, 3,6 lượt vẽ thay vì 22), rất nhỏ thì thành thẻ impostor chiếu sáng lại; "
               "100 xe trong khung: 741 nghìn → 255 nghìn tam giác.</li>"
               "<li><b>Kiểm thử:</b> xem phần 17.</li>"
               "<li><b>Đồ họa:</b> URP, mức Thấp/Vừa/Cao/Tùy chỉnh; Cao có shadow map 4096, bóng mềm, MSAA 4x và model chi tiết cho 12 xe phổ biến nhất.</li></ul></div>")

    out.append(programme.testing(game, {'esc': esc}))

    # ------------------------------------------------------------------ UI
    ui = [('home.png', 'Trang chủ: trận đấu AI làm nền, cột thẻ bên phải, nút XUẤT KÍCH.'), ('army.png', 'Quân đội: bộ bài và bộ sưu tập.'),
          ('detail.png', 'Chi tiết phương tiện: mô hình 3D xoay, chỉ số, vũ khí, xem bắn, trang bị.'), ('guide.png', 'Tab Hướng dẫn (mới): vai trò, cách đánh, mạnh/yếu, mẹo; từ khóa tô màu.'), ('gear.png', 'Trang bị.'),
          ('setup.png', 'Thiết lập trận: chế độ, bản đồ, độ khó, thời tiết.'), ('events.png', 'Sự kiện.'), ('shop.png', 'Cửa hàng.'),
          ('settings.png', 'Cài đặt đồ họa và âm thanh.'), ('result.png', 'Màn kết quả trận.'),
          ('edge.png', 'Mép bản đồ: đường ranh giới và cảnh ngoài viền.')]
    out.append("<div class='section'><h2>18. Giao diện</h2><p>Phong cách “Field Command”: nền xám thép trong suốt trên trận đấu, viền mảnh, góc vuông, một màu nhấn cam "
               "cho hành động chính (góc vát), chữ in hoa hẹp. Thanh điều hướng dọc bên trái.</p>")
    for name, cap in ui:
        tag = img(shots / name, 'shot')
        if tag:
            out.append(f"{tag}<div class='caption'>{esc(cap)}</div>")
    # ------------------------------------------------------------------ round 6 pictures
    r6 = imgdir / 'r6'
    pics = [('munitions_1.png', 'Mô hình đạn: tên lửa chống tăng và phòng không vác vai.'), ('munitions_2.png', 'Tên lửa không đối không, phòng không, không đối đất.'),
            ('munitions_3.png', 'Rocket.'), ('munitions_4.png', 'Bom và drone.'), ('munitions_5.png', 'Đạn pháo, đạn cối, đạn xuyên, đạn railgun.'),
            ('new_models.png', 'Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre.'),
            ('flame.png', 'Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen.'), ('railgun.png', 'Railgun: nạp năng lượng, tia sáng lưu lại.'),
            ('boss_death.png', 'Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích.'), ('muzzle_audit.png', 'Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra.')]
    out.append("<div class='section'><h2>19. Hình ảnh</h2>")
    for name, cap in pics:
        tag = img(r6 / name, 'shot')
        if tag:
            out.append(f"{tag}<div class='caption'>{esc(cap)}</div>")
    out.append('</div></body></html>')
    return '\n'.join(out)


def main():
    game_json, imgdir, pdf = sys.argv[1], sys.argv[2], sys.argv[3]
    global CACHE
    CACHE = Path(imgdir) / 'cache'
    CACHE.mkdir(exist_ok=True)
    game = json.loads(Path(game_json).read_text(encoding='utf-8'))
    page = Path(pdf).with_suffix('.html')
    page.write_text(build(game, imgdir), encoding='utf-8')
    subprocess.run([EDGE, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={Path(pdf).resolve()}', page.resolve().as_uri()],
                   check=True, timeout=600)
    print('wrote', pdf)


if __name__ == '__main__':
    main()
