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
import prompt25  # noqa: E402
import prompt26  # noqa: E402
import prompt27  # noqa: E402
import measure_stamp  # noqa: E402
import prompt29  # noqa: E402
import prompt32  # noqa: E402
import prompt31  # noqa: E402
import prompt32_base  # noqa: E402
import prompt34  # noqa: E402
import prompt33  # noqa: E402
import fix_full  # noqa: E402
import bomb_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
GEAR_ART = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Gear'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

CLASS_VI = {'Scout': 'Trinh sát', 'Light': 'Xe nhẹ', 'Tank': 'Xe tăng', 'Heavy': 'Hạng nặng', 'TankHunter': 'Diệt tăng',
            'Artillery': 'Pháo binh', 'AntiAir': 'Phòng không', 'Support': 'Hỗ trợ', 'Aircraft': 'Không quân', 'Helicopter': 'Trực thăng',
            'Plane': 'Máy bay', 'Defense': 'Công sự', 'Boss': 'Boss'}
ARMOR_VI = {'Light': 'Nhẹ', 'Heavy': 'Nặng', 'Air': 'Máy bay', 'Structure': 'Công trình'}
TYPE_VI = {'Kinetic': 'Động năng', 'ArmorPiercing': 'Xuyên giáp', 'HighExplosive': 'Nổ mạnh', 'Fire': 'Lửa', 'Flak': 'Phòng không',
           'ShapedCharge': 'Nổ lõm', 'Fragmentation': 'Mảnh', 'Energy': 'Năng lượng'}
TARGET_VI = {'Ground': 'Mặt đất', 'Air': 'Trên không', 'All': 'Tất cả'}
# Prompt 15: armour levels, faces, weapon forms, the effect columns and the threats (Matchup in the game).
LEVEL_VI = ['Không giáp', 'Mỏng', 'Vừa', 'Dày', 'Rất dày', 'Siêu dày']   # 5: a boss's plate (DECISIONS 21G)
FACE_VI = [('front', 'Trước'), ('side', 'Hông'), ('rear', 'Sau'), ('top', 'Nóc')]
FORM_VI = {'None': '—', 'BulletSmall': 'đạn súng', 'BulletBig': 'đạn súng (cỡ lớn)', 'BeltedAutocannon': 'đạn pháo động năng (pháo tự động)',
           'Dart': 'đạn pháo động năng', 'DoubleDart': 'đạn pháo động năng (≥120 mm)', 'Rail': 'đạn pháo động năng (điện từ)',
           'HeShell': 'đạn pháo nổ mạnh', 'MortarBomb': 'đạn pháo nổ mạnh (cối)', 'Grenade': 'đạn pháo nổ mạnh (lựu đạn 40 mm)',
           'SuperShell': 'đạn pháo nổ mạnh (800 mm)', 'Airburst': 'đạn nổ trên không', 'RocketSmall': 'rốc-két', 'RocketBig': 'rốc-két (cỡ lớn)',
           'Atgm': 'tên lửa chống tăng', 'Sam': 'tên lửa phòng không', 'Cruise': 'tên lửa hành trình', 'Ballistic': 'tên lửa đạn đạo',
           'Bomb': 'bom thường', 'GuidedBomb': 'bom dẫn đường', 'Cluster': 'bom chùm', 'HeavyBomb': 'bom hạng nặng', 'CarBomb': 'bom hạng nặng (xe bom)',
           'Fpv': 'drone (FPV)', 'Shahed': 'drone (Shahed)', 'Lancet': 'drone (Lancet)', 'Flame': 'lửa', 'Napalm': 'lửa (napalm)',
           'Energy': 'năng lượng', 'Blade': 'cận chiến (lưỡi ủi)', 'Drill': 'cận chiến (mũi khoan)'}
COLUMN_VI = {'Armour0': 'giáp 0', 'Armour1': 'giáp 1', 'Armour2': 'giáp 2', 'Armour3': 'giáp 3', 'Armour4': 'giáp 4', 'Armour5': 'giáp 5',
             'Air': 'trên không', 'Structure': 'công trình'}
THREAT_VI = {'SmallArms': 'súng bộ binh', 'HeavyMachineGuns': 'súng máy hạng nặng', 'Fire': 'lửa', 'Fragmentation': 'mảnh', 'Autocannons': 'pháo tự động',
             'HighExplosive': 'nổ mạnh', 'Energy': 'năng lượng', 'TopAttack': 'đánh nóc', 'ShapedCharges': 'nổ lõm', 'TankGuns': 'pháo xe tăng'}
GOOD_AT, POOR_AT = 0.6, 0.12   # Matchup.GoodAt / PoorAt
# What each unit was modelled on (real systems, films or games), keyed by unit id; see unit_refs.json's "_about".
UNIT_REFS = json.loads((Path(__file__).resolve().parent / 'unit_refs.json').read_text(encoding='utf-8'))

# A base tower's (and its branches') slot size and rebuild price, filled from game['base'] when the build starts.
TOWER_INFO = {}
SIZE_VI = {'Small': 'nhỏ', 'Medium': 'vừa', 'Large': 'lớn', 'Utility': 'tiện ích'}


def unlock_text(route, coins):
    """How a card is had: a starter, a premium card bought with coins, or a campaign card won or bought early."""
    if route == 'Starter':
        return 'có sẵn từ đầu'
    money = f"{coins:,}".replace(',', '.')
    if route == 'Premium':
        return f"thẻ cao cấp, mua {money} xu"
    return f"thắng màn mở khóa trong chiến dịch, hoặc mua sớm {money} xu"


def price_of(v):
    """A unit's price: the stat cell and the line under it (play-test 8: every card, tower, elite and boss says it)."""
    raw = v.get('raw', {})
    if raw.get('Boss'):
        return '—', 'boss, không phải thẻ: không mua, không gọi được'
    if raw.get('Elite'):
        cp = raw.get('ArmyCost', 0)
        return f"{cp} CP (địch)", f"địch trả {cp} CP trong ngân sách để đưa nó ra; hạ nó được hoàn CP theo giá này"
    if v['id'] in TOWER_INFO:
        t = TOWER_INFO[v['id']]
        return (f"xây lại {t.get('rebuildCp', 0)} CP",
                f"tháp ô {SIZE_VI.get(t.get('size'), t.get('size', ''))} của căn cứ; bị phá thì xây lại {t.get('rebuildCp', 0)} CP sau {t.get('rebuildSeconds', 0):g} s; "
                f"mở khóa: {unlock_text(v.get('route'), v.get('coins', 0))}")
    if raw.get('Static'):
        return '—', 'công sự trung lập hoặc của bản đồ, không mua được'
    if not raw.get('Card', True):
        return '—', 'không phải thẻ: đến từ vật phẩm, hỗ trợ hoặc kịch bản'
    return f"{v['cost']} CP", f"{v['cost']} CP mỗi lần gọi; mở khóa: {unlock_text(v.get('route'), v.get('coins', 0))}"
# DamageTable's penetration steps (DECISIONS 20X): the round's level over the face's.
PEN_STEP_VI = ['hơn từ 2 cấp', 'hơn 1 cấp', 'ngang cấp', 'thiếu 1 cấp', 'thiếu 2 cấp', 'thiếu từ 3 cấp']


def level(n):
    return f"{n} ({LEVEL_VI[n]})" if isinstance(n, int) and 0 <= n < len(LEVEL_VI) else str(n)


def armour_text(v):
    """A unit's armour: one level when every face is the same, else each face; 'công trình' on structures."""
    a = v.get('armour') or {}
    faces = [a.get(k, 0) for k, _ in FACE_VI]
    text = f"cấp {level(faces[0])}" if len(set(faces)) == 1 else ' · '.join(f"{name} {level(a.get(k, 0))}" for k, name in FACE_VI)
    return text + (' · công trình' if v.get('armor') == 'Structure' else '')


def front_level(v):
    a = v.get('armour') or {}
    return level(a.get('front', 0))


def weapon_tags(w):
    tags = []
    if w.get('topAttack'):
        tags.append('đánh nóc')
    if w.get('guided'):
        tags.append('dẫn đường')
    if w.get('splash') or w.get('splashes'):
        tags.append('nổ lan')
    if w.get('thermobaric'):
        tags.append('Nhiệt áp')
    return tags


def form_cell(w):
    return esc(FORM_VI.get(w.get('form', ''), w.get('form', ''))) + ''.join(f"<span class='tag'>{esc(t)}</span>" for t in weapon_tags(w))


def verdict(x):
    return '✓' if x >= GOOD_AT else '~' if x >= POOR_AT else '✕'


def effect_table(w):
    """The main weapon against the armour levels (0-5: 5 a boss's plate), aircraft and structures, with the game's ✓ ~ ✕."""
    row = w.get('effect') or []
    if len(row) < 7:
        return ''
    head = ['Hiệu quả: ' + (w.get('name') or w['id'])] + [f'Giáp {i}' for i in range(len(row) - 2)] + ['Trên không', 'Công trình']
    cells = [f"xuyên {w.get('pen', 0)}"] + [f"{verdict(x)} ×{x:.2f}".rstrip('0').rstrip('.') for x in row]
    return table(head, [cells], 'eff')
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
LONG_MAPS = len(list((Path(__file__).resolve().parents[2] / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'maps').glob('*_long.json')))
SIZES = {'thumb': 640, 'gearicon': 128, 'shot': 1500, 'fx': 560, '': 1300}


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
.grid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5pt; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5pt; }
.grid2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5pt; }
.galcell { break-inside: avoid; background: #fff; border: 1px solid #ddd; padding: 3pt; text-align: center; }
.galcell img.gal { width: 100%; height: 110pt; object-fit: contain; }
.galcap { font-size: 8pt; margin-top: 2pt; }
table.eff { font-size: 8pt; margin-top: 3pt; }
table.eff td, table.eff th { padding: 1.5pt 3pt; text-align: center; }
.tag { display: inline-block; font-size: 7pt; background: #e8eef5; color: #2f5d8a; border-radius: 3pt; padding: 0 3pt; margin-left: 3pt; }
.behav { font-size: 8.5pt; margin-top: 4pt; border-left: 2px solid #5b7fa6; padding-left: 5pt; }
.behav ul { margin: 2pt 0 0 0; padding-left: 12pt; }
.behav li { margin: 1pt 0; }
.behav .hl { color: #2f5d8a; font-weight: 700; }
.fxblock { page-break-inside: avoid; margin-bottom: 8pt; }
.fxgrid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3pt; }
.fxcell { break-inside: avoid; text-align: center; }
.fxcell img.fx, .pair img.fx { width: 100%; border: 1px solid #c9cdd0; }
.pending { background: #c8cbcd; color: #4a4f53; font-size: 7pt; min-height: 52pt; display: flex; flex-direction: column;
           justify-content: center; align-items: center; text-align: center; padding: 3pt; word-break: break-all; }
.pending code { font-size: 6.5pt; }
.pair { page-break-inside: avoid; margin-bottom: 6pt; }
"""


def guide_html(text):
    """The Guide tab's four lines, key words ([[word]]) highlighted."""
    if not text:
        return ''
    lines = [re.sub(r'\[\[(.+?)\]\]', lambda m: f"<span class='hl'>{m.group(1)}</span>", esc(line)) for line in text.split('\n')]
    return "<div class='guide'>" + ''.join(f"<div>{'<b>' + l + '</b>' if i == 0 else l}</div>" for i, l in enumerate(lines)) + "</div>"


def lines_html(title, lines, cls):
    """A titled list of short lines (Behaviour, Ammo), key words ([[word]]) highlighted."""
    if not lines:
        return ''
    items = ''.join('<li>' + re.sub(r'\[\[(.+?)\]\]', lambda m: f"<span class='hl'>{m.group(1)}</span>", esc(l)) + '</li>' for l in lines)
    return f"<div class='{cls}'><b>{esc(title)}</b><ul>{items}</ul></div>"


def weapon_cycle(w):
    """A weapon's cycle in words: a magazine and its change, a burst, or a single shot and its cooldown."""
    if w.get('clip'):
        return f"băng {w['clip']} viên, {1 / max(0.001, w['cooldown']):.0f} viên/s, thay {w['clipReload']:g} s"
    if w['burst'] > 1:
        return f"loạt {w['burst']}, hồi {w['cooldown']:g} s"
    return f"hồi {w['cooldown']:g} s"


def refs_text(v):
    """'<real> · <media> — note' for a unit, found by its id, else by its model id; '' when neither has an entry."""
    r = UNIT_REFS.get(v['id']) or UNIT_REFS.get(v.get('model', ''))
    if not r:
        return ''
    parts = [', '.join(r.get('real', [])), ', '.join(r.get('media', []))]
    text = ' · '.join(p for p in parts if p)
    return text + (f" — {r['note']}" if r.get('note') else '')


def vehicle_card(v, imgdir):
    # Full fix L10 item 8: calibre or warhead, the cadence as "loạt N · chu kỳ X s" / "mỗi X s", barrels, core / edge, sustained DPS.
    weapons = [[esc(w.get('name') or w['id']), TYPE_VI.get(w['type'], w['type']), str(w.get('pen', 0)), form_cell(w), esc(fix_full.card_size(w)),
                num(w['damage']), str(fix_full._barrels(w)), esc(fix_full.card_rate(w)) if fix_full._cycle(w) else weapon_cycle(w), esc(fix_full.card_blast(w)),
                f"{w['range']:g} m" + (f" (tối thiểu {w['minRange']:g})" if w['minRange'] > 0 else ''),
                TARGET_VI.get(w['targets'], w['targets']), f"{w['dps']:.0f}"] for w in v['weapons']]
    main = max(v['weapons'], key=lambda w: w['dps'], default=None)
    strong = ', '.join(COLUMN_VI.get(c, c) for c in v.get('strongVs', []))
    weak = ', '.join(THREAT_VI.get(t, t) for t in v.get('weakTo', []))
    matchup = ((f"<div class='note'><b>Mạnh với:</b> {esc(strong)}</div>" if strong else '')
               + (f"<div class='note'><b>Yếu trước:</b> {esc(weak)}</div>" if weak else ''))
    ammo = list(v.get('ammo') or []) + [f"{w.get('name') or w['id']}: xuyên [[{w.get('pen', 0)}]], {FORM_VI.get(w.get('form', ''), w.get('form', ''))}"
                                        + (' (' + ', '.join(weapon_tags(w)) + ')' if weapon_tags(w) else '') for w in v['weapons']]
    d = v['dpsVs']
    stats = (f"<div class='stats'><div>Máu <b>{num(v['hp'])}</b></div><div>Giáp trước <b>{front_level(v)}</b></div>"
             f"<div>Tốc độ <b>{v['speed']:g} m/s</b></div><div>Giá <b>{esc(price_of(v)[0])}</b></div>"
             f"<div>Tầm nhìn <b>{v['vision']:g} m</b></div><div>DPS vs nhẹ <b>{d['Light']:.0f}</b></div>"
             f"<div>DPS vs nặng <b>{d['Heavy']:.0f}</b></div><div>DPS vs máy bay <b>{d['Air']:.0f}</b></div></div>")
    skills = ''.join(f"<span class='chip'>{esc(s)}</span>" for s in v['skills'])
    refs = refs_text(v)
    ref_html = f"<div class='note'><b>Tham khảo:</b> {esc(refs)}</div>" if refs else ''
    # The game's own card render (Resources/UI/Cards, 512 px, transparent), else a hero render.
    card = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Cards' / (v['model'] + '.png')
    thumb = img(card, 'thumb', v['name']) if card.exists() else img(Path(imgdir) / 'veh' / (v['model'] + '.png'), 'thumb', v['name'])
    return (f"<div class='card'><div class='head' style='{'' if thumb else 'grid-template-columns: 1fr'}'>{thumb}"
            f"<div><div class='name'>{esc(v['name'])}</div><div class='meta'>{CLASS_VI.get(v['class'], v['class'])}"
            f"{' · bay' if v['flying'] else ''} · id <code>{esc(v['id'])}</code></div>{stats}"
            f"<div class='note'><b>Giá:</b> {esc(price_of(v)[1])}</div>"
            f"<div class='note'><b>Giáp:</b> {esc(armour_text(v))}</div>"
            f"{ref_html}{matchup}"
            f"{guide_html(v.get('guide', ''))}<div class='note'>{esc(v['note'])}</div>{('<div>' + skills + '</div>') if skills else ''}</div></div>"
            + (table(['Vũ khí', 'Loại', 'Xuyên', 'Dạng · dấu', 'Cỡ / đầu nổ', 'Sát thương / phát', 'Nòng', 'Nhịp bắn', 'Lõi / rìa', 'Tầm', 'Mục tiêu',
                      'DPS duy trì'], weapons) if weapons else '')
            + (effect_table(main) if main else '')
            + "<div class='two'>" + lines_html('Hành vi', v.get('behavior'), 'behav') + lines_html('Đạn và nạp đạn', ammo, 'behav') + "</div>"
            + "</div>")


def difficulty_table():
    """The four difficulty levels, read from DECISIONS 13C's table so it follows the design notes."""
    text = (ROOT / 'Docs' / 'DECISIONS.md').read_text(encoding='utf-8')
    m = re.search(r'^\| \| Easy \| Normal \| Hard \| Very Hard \|\n\|[-|]+\|\n((?:\|.*\|\n)+)', text, re.M)
    if not m:
        return ''
    label = {'Noise (randomness of a pick)': 'Độ ngẫu nhiên khi chọn quân', 'Counters what it has seen': 'Mua khắc chế thứ đã thấy',
             'Keeps its role shares': 'Giữ tỷ lệ vai trò', 'Weighs value per CP (part A)': 'Coi trọng giá trị / CP',
             'Saves for the big cards (per CP of price)': 'Để dành cho thẻ lớn (theo CP)', 'Deck': 'Bộ bài', 'Income': 'Thu nhập',
             'Decision every': 'Ra quyết định mỗi', 'Elite share of its spending (cap)': 'Phần chi cho tinh nhuệ (trần)', 'Rewards': 'Thưởng',
             'Base (HQ level)': 'Căn cứ (cấp HQ)'}
    words = {'at random': 'ngẫu nhiên', 'by roles and value': 'theo vai trò và giá trị', 'by roles': 'theo vai trò', 'against the player\'s deck': 'nhắm bộ bài người chơi'}
    rows = []
    for line in m.group(1).strip().splitlines():
        cells = [c.strip() for c in line.strip('|').split('|')]
        vals = []
        for c in cells[1:]:
            for en, vi in words.items():
                c = c.replace(en, vi)
            vals.append(esc(c.replace('**', '')))
        rows.append([esc(label.get(cells[0], cells[0]))] + vals)
    return table(['', 'Dễ', 'Thường', 'Khó', 'Cực khó'], rows)


def build(game, imgdir):
    for t in game.get('base', {}).get('towers', []):
        TOWER_INFO[t['id']] = t
        for b in t.get('branches', []):
            TOWER_INFO.setdefault(b['id'], t)
    imgdir = Path(imgdir)
    shots = imgdir / 'shots'
    ui = imgdir / 'ui'
    mp = {m['id']: m['name'] for m in game['maps']}
    bn = {v['id']: v['name'] for v in game['bosses']}
    balance = json.loads(re.sub(r'//.*', '', (DATA / 'balance.json').read_text(encoding='utf-8')))
    out = [f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Machine Brigade - Design review</title><style>{CSS}</style></head><body>']

    # ------------------------------------------------------------------ cover and contents
    out.append("<div class='cover'><div class='kicker'>TÀI LIỆU THIẾT KẾ · REVIEW</div><h1>MACHINE BRIGADE</h1>"
               f"<p class='muted'>Game chiến thuật thời gian thực trên mobile, chỉ có phương tiện quân sự · bản {date.today().isoformat()}</p>"
               f"{img(ui / 'screen-home-vi-16x9.png', 'shot')}"
               "<p>Tài liệu này lấy số liệu trực tiếp từ dữ liệu game (balance.json, campaign.json, mã nguồn), gồm: các chế độ chơi, "
               "chiến dịch cốt truyện, nhiệm vụ nhiều giai đoạn, Tác chiến, căn cứ và tháp, Công thành / Phòng thủ, toàn bộ phương tiện với chỉ số và DPS, vũ khí, tháp canh, "
               "xe tinh nhuệ, boss và bộ phận boss, hỗ trợ hỏa lực, hệ thống trang bị, kinh tế, bản đồ, giao diện và các phép đo còn chờ phase kiểm tra.</p></div>")
    out.append("<div class='section'><h2>Mục lục</h2><ol class='toc'><li>Tổng quan</li><li>Chế độ chơi</li><li>Chiến dịch</li>"
               "<li>Nhiệm vụ nhiều giai đoạn</li><li>Tác chiến</li><li>Căn cứ và tháp</li><li>Công thành và Phòng thủ</li>"
               "<li>Phương tiện (thẻ chi tiết; 8b miêu tả, hình dạng, mở khóa)</li><li>Bảng DPS tổng hợp</li><li>Vũ khí và bảng sát thương (10c-10i: tầm nổ, boss, đạn thay thế, boss hai lớp nổ, Săn trùm, họ vũ khí và cảnh báo; 10j: nhịp bắn boss, họ vũ khí, hành vi đạn, vòng cảnh báo, hiệu ứng)</li><li>Tháp canh, xe tinh nhuệ và boss</li>"
               "<li>Hỗ trợ hỏa lực</li><li>Trang bị</li><li>Kinh tế</li><li>Bản đồ</li><li>AI và hệ thống (16b: hiệu ứng và âm thanh theo bậc, xác vỡ, màn xem trước)</li><li>Kiểm thử và phép đo còn lại</li>"
               "<li>Giao diện</li><li>Hình ảnh</li><li>Sửa lỗi tổng hợp: A bảng vũ khí đầy đủ, B từng boss, C hiệu ứng có ảnh, D âm thanh, E model</li></ol></div>")

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
               f"<p><b>Bản đồ:</b> {len(game['maps'])} chiến trường 300 × 300 m, mỗi bản có phiên bản chiếm cứ điểm, sinh tồn và công thành; "
               f"{LONG_MAPS} bản dài 300 × 480 m (căn cứ nhiều lớp) cho Công thành, Phòng thủ, Vô tận và Pháo đài tuần. "
               f"<b>Mô phỏng:</b> cố định 20 tick/giây, xác định (deterministic), tách khỏi phần hình ảnh.</p>"
               f"{img(shots / 'battle1.png', 'shot')}<div class='caption'>Trong trận (ảnh 3D; HUD ở ảnh này là bản trước phase 10, HUD mới ở phần 18): bản đồ nhỏ, thanh nhiệm vụ, nút lệnh, khay thẻ và CP.</div>"
               f"{img(shots / 'battle2.png', 'shot')}<div class='caption'>Bản đồ sa mạc {mp.get('dunebreak', 'Đồi Cát')} sau khi phóng to 50%; nhà cửa đã chỉnh tỷ lệ so với xe.</div></div>")

    # ------------------------------------------------------------------ modes
    desc = {
        'Conquest': 'Hai phe tranh 3 cứ điểm; giữ nhiều cứ điểm hơn thì điểm đối phương giảm dần; hết điểm là thua.',
        'Survival': 'Không căn cứ, không tháp: chỉ quân của bạn chống các đợt địch ngày càng mạnh; bị quét sạch hoặc để địch chiếm bãi là thua.',
        'Deathmatch': 'Tử chiến: hạ đủ số điểm tiêu diệt trước.',
        'KingOfTheHill': 'Vua đồi: giữ cứ điểm trung tâm để tích điểm.',
        'Assault': 'Công phá: người chơi đánh chiếm lần lượt 3 khu phòng thủ (A, B, C) trong quỹ thời gian; mỗi khu chiếm được cộng thêm giờ.',
        'Campaign': f"Chiến dịch {len(game['chapters'])} chương, {len(game['campaign'])} nhiệm vụ (xem phần 3); chơi lại các trận lớn ở Tác chiến (phần 5).",
        'Siege': 'Công thành: pháo đài chiếm 45% bản đồ, 3 giai đoạn (trạm radar tuyến ngoài → máy phát khiên trong tường → sở chỉ huy), cổng, tường sập, vòm khiên, '
                 'siêu pháo, chi viện bằng tàu hỏa hoặc đường băng (phần 7).',
        'BossRush': (f"Săn trùm (Boss Hunt): tuần này {game['hunt']['weekly']} boss ({game['hunt']['weeklyMains']} chủ lực) tăng dần, máu boss theo sức mạnh bộ bài; "
                     f"chế độ toàn bộ {game['hunt']['full']} boss theo thứ tự cốt truyện; hỗ trợ tác chiến tối đa +{game['hunt']['cap'] * 100:g}% (xem phần 10h). "
                     'Thưởng thêm 2 CP mỗi bộ phận boss bị phá.') if game.get('hunt') else 'Săn trùm.',
        'Defend': 'Phòng thủ: pháo đài là loadout căn cứ của bạn, ba tuyến lùi (mất tuyến được thưởng CP rút lui) và sở chỉ huy là trận chốt; đợt địch hiện trước bằng icon.',
        'Weekly': 'Pháo đài tuần: một cuộc công thành mà vòng thành đã phá được giữ nguyên cả tuần; thắng lần đầu trong tuần có thưởng.',
        'Endless': 'Vô tận: pháo đài của bạn trước các đợt địch không ngừng (mỗi 55 giây, to dần, tinh nhuệ dần); lưu kỷ lục đợt xa nhất.',
    }
    rows = [[f"<b>{esc(m['name'] or m['id'])}</b>", esc(m['sub']), esc(desc.get(m['id'], ''))] for m in game['modes']]
    out.append("<div class='section'><h2>2. Chế độ chơi</h2>" + table(['Chế độ', 'Tóm tắt', 'Luật'], rows)
               + "<p>Bốn độ khó Dễ / Thường / Khó / Cực khó ảnh hưởng AI địch, thu nhập, xe tinh nhuệ và thưởng:</p>" + difficulty_table() + "<p>"
               "Thời tiết (nắng, âm u, mưa, bão, tuyết, bão cát, sương mù, đêm) đổi dần trong 8 giây và ảnh hưởng tầm nhìn/hình ảnh.</p>"
               f"<div class='two'><div>{img(shots / 'siege.png', 'shot')}<div class='caption'>Công thành.</div></div>"
               f"<div>{img(shots / 'defend.png', 'shot')}<div class='caption'>Phòng thủ căn cứ.</div></div></div>"
               f"<div class='two'><div>{img(shots / 'boss.png', 'shot')}<div class='caption'>Boss.</div></div>"
               f"<div>{img(shots / 'hunt.png', 'shot')}<div class='caption'>Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ.</div></div></div></div>")

    # ------------------------------------------------------------------ campaign and the programme (prompts 1-6)
    h = {'esc': esc, 'table': table, 'img': img, 'num': num, 'guide_html': guide_html, 'GOAL_VI': GOAL_VI}
    # Prompt 29 S08 (R10): a measured section goes to the appendix "Lịch sử đo" unless its stamp matches today's data.
    history = []
    modes = programme.modes_and_ai(game, h)
    history.append(modes)  # 2b: numbers measured by hand in prompt 13, no stamp
    # Prompt 30 pass 9: the four acts, match rules by mode, endless, neutrals, dialogue strip, match end.
    out.append(programme.prompt30(game, h))
    out.append(programme.campaign(game, h))
    out.append(programme.multistage(game, h))
    out.append(programme.operations(game, h))
    out.append(programme.bases(game, h))
    out.append(programme.siege(game, h))
    out.append(programme.late_programme(game, h, imgdir))
    out.append(programme.mission_events(game, h))

    # ------------------------------------------------------------------ vehicles
    groups = {}
    for v in game['vehicles']:
        key = 'Không quân' if v['flying'] else CLASS_VI.get(v['class'], v['class'])
        groups.setdefault(key, []).append(v)
    out.append("<div class='section'><h2>8. Phương tiện</h2><p>Chỉ số gốc (hạng 1, chưa trang bị). DPS = sát thương mỗi loạt / chu kỳ bắn, cộng mọi vũ khí, "
               "nhân hệ số giáp (phần 10). Hạng thẻ cộng +5% máu và sát thương mỗi hạng (tối đa hạng 10: +45%).</p>"
               "<p><b>Nguồn tham khảo.</b> Dòng \"Tham khảo\" trên mỗi thẻ (xe, xe tinh nhuệ, tháp, nhánh hạng 7, boss) ghi hệ thống ngoài đời thật "
               "và phim hoặc game mà model được dựng theo, lấy từ Tools/docs/unit_refs.json. Tệp này tổng hợp từ các tham chiếu chủ dự án yêu cầu "
               "trong DECISIONS.md (19R, 19U, 20V, 20Y, 21H), chú thích của các script dựng model Blender, tên thật của vũ khí trong balance.json "
               "và kiến thức chung về khí tài; mục ghi \"ước đoán\" là suy đoán, chưa có nguồn ghi rõ.</p>")
    out.append(f"{img(imgdir / 'shots' / 'hd.png', 'shot')}<div class='caption'>Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất.</div>")
    for key, vs in groups.items():
        out.append(f"<h3>{esc(key)} ({len(vs)})</h3>")
        out.extend(vehicle_card(v, imgdir) for v in vs)
    out.append('</div>')
    # Prompt 25 F1 (DECISIONS 25E): every unit's description, shape note and unlock.
    out.append(prompt25.unit_sheet_rows(game, h))

    # ------------------------------------------------------------------ DPS table
    rows = [[f"<b>{esc(v['short'])}</b>", CLASS_VI.get(v['class'], v['class']), front_level(v), num(v['hp']), v['cost'],
             f"{v['speed']:g}", f"{max((w['range'] for w in v['weapons']), default=0):g}",
             f"{v['dpsVs']['Light']:.0f}", f"{v['dpsVs']['Heavy']:.0f}", f"{v['dpsVs']['Air']:.0f}", f"{v['dpsVs']['Structure']:.0f}",
             f"{(v['dpsVs']['Heavy'] / max(1, v['cost'])):.1f}"] for v in game['vehicles']]
    out.append("<div class='section'><h2>9. Bảng DPS tổng hợp</h2>"
               + table(['Xe', 'Lớp', 'Giáp trước', 'Máu', 'CP', 'Tốc độ', 'Tầm', 'DPS nhẹ', 'DPS nặng', 'DPS bay', 'DPS công trình', 'DPS nặng / CP'], rows, 'dps') + '</div>')

    # Prompt 34 L9: firing, blasts and sound by tier, wrecks by class, the previews' settings.
    out.append(prompt34.section16(game, h))
    out.append(prompt29.round2(game, h))
    # Prompt 32 L8: the ammunition handbook (VI + EN), generated from balance.json as the game's Dossier tab.
    # Prompt 32 L9: the base system's sections (roster, branches, rebuilding, walls, HQ types, Defend by level, Showdown,
    # starting CP and opening squads), before the handbook.
    out.append(prompt32_base.base_system(game, h))
    out.append(prompt32.ammo_handbook(game, h))
    out.append(prompt34.handbook_tiers(game, h))
    cv = programme.combat_value(game, h)
    if cv and measure_stamp.matches(prompt25.measure_path()):
        out.append(cv)
    elif cv:
        history.append(cv)

    # ------------------------------------------------------------------ weapons
    dt = game['damageTable']
    armors = ['Ground', 'Air', 'Structure']
    rows = [[TYPE_VI.get(t, t)] + [f"×{dt[t][a]:g}" for a in armors] for t in dt if isinstance(dt[t], dict)]
    pens = dt.get('penetration', [])
    weapons = {}
    branch_names = {b['id']: f"{t['name']} · {b['name']}" for t in game['base']['towers'] for b in t['branches']}
    for group in ('vehicles', 'elites', 'bosses', 'towers'):
        for v in game[group]:
            owner = branch_names.get(v['id']) or (v['short'] if not str(v['short']).startswith('support.') else v['name'])
            for w in v['weapons']:
                weapons.setdefault(w['id'], (w, owner))
    def volley(w):
        return f"băng {w['clip']} · thay {w['clipReload']:g} s" if w.get('clip') else w['burst']
    wrows = [[f"<code>{esc(w['id'])}</code>", TYPE_VI.get(w['type'], w['type']), str(w.get('pen', 0)), form_cell(w), num(w['damage']), volley(w), f"{w['cooldown']:g}",
              f"{w['speed']:g}" if w.get('speed') else '',
              f"{w['range']:g}", f"{w['minRange']:g}" if w['minRange'] else '', f"{w['splash']:g}" if w['splash'] else '',
              TARGET_VI.get(w['targets'], w['targets']), f"{w['dps']:.0f}", esc(owner)] for w, owner in sorted(weapons.values(), key=lambda x: x[0]['id'])]
    counters = [
        ['Giáp phản ứng nổ (mô-đun)', 'Nổ lõm: giảm 40% (Sử thi) / 55% (Huyền thoại) một phát; đầu nổ song song xuyên qua', 'Động năng, nổ mạnh, mọi loại khác; mìn'],
        ['Khối phản ứng nổ (dòng đặc biệt)', 'Nổ lõm: nửa một phát, mỗi lần một khối', 'Đạn động năng'],
        ['Lồng chắn (Slat Cage, lưới chắn; mái che của xe rùa trước drone)', 'Phần nổ lõm của rốc-két, tên lửa và drone', 'Đạn động năng, đạn pháo HEAT, nổ nhiệt áp, mìn'],
        ['APS (Trophy, phòng thủ điểm)', 'Tên lửa, drone, rốc-két bắn thẳng (laser phòng thủ điểm và C-RAM thêm rốc-két pháo binh; C-RAM một phần đạn pháo)',
         'Đạn pháo xe tăng, đạn súng, tia năng lượng; laser phòng thủ điểm khi ở trong khói hoặc bắn vào khói'],
        ['Pháo sáng', 'Tên lửa (theo độ kháng pháo sáng của đầu dò)', 'Drone, đạn súng, đạn phòng không, tia năng lượng'],
        ['Khói', '80% sát thương của tia năng lượng bắn vào hoặc bắn ra', 'Mọi loại khác'],
        ['Gây nhiễu', 'Đạn dẫn đường (tên lửa, drone) bay lệch', 'Đạn không dẫn đường, tia năng lượng'],
        ['Khiên (xe mang khiên, tháp khiên)', 'Mọi phát trúng quân ở trong vòm, tới khi khiên vỡ', 'Năng lượng'],
    ]
    legend = img(imgdir / 'ui' / 'kit-combat-icons.png', 'shot')
    out.append("<div class='section'><h2>10. Vũ khí và bảng sát thương</h2><h3>Hệ số sát thương theo loại đạn và loại giáp</h3>"
               + table(['Loại đạn'] + [{'Ground': 'Mặt đất', 'Air': 'Trên không', 'Structure': 'Công trình'}[a] for a in armors], rows)
               + "<p>Prompt 15: mỗi mặt giáp (trước, hông, sau, nóc) có cấp 0–4 (boss tới cấp 5, giáp siêu dày: DECISIONS 21G), mỗi vũ khí có cấp xuyên 0–4. "
               "Sát thương nhân theo cấp xuyên so với cấp giáp của mặt trúng đạn: "
               + esc(', '.join(f"{name} ×{m:g}" for name, m in zip(PEN_STEP_VI if len(pens) == len(PEN_STEP_VI) else [f"bước {i}" for i in range(len(pens))], pens)))
               + f"; đầu nổ nhiệt áp ×{dt.get('thermobaric', 1):g} (xem DECISIONS 14A). Bảng hiệu quả và ký hiệu ✓ ~ ✕ của từng xe nằm ở thẻ xe (phần 8).</p>"
               + "<p>Giáp có hướng (giáp mặt trước dày hơn hông/sau), đạn lệch theo tầm và chuyển động, pháo có tầm tối thiểu. Máy bay có pháo sáng, "
               "xe có hệ thống đánh chặn chủ động (APS) chặn tên lửa/drone, tàng hình chỉ lộ ở 40% tầm nhìn khi không bắn. "
               f"Ký hiệu: ✓ hệ số từ {GOOD_AT:g} trở lên, ~ từ {POOR_AT:g}, ✕ thấp hơn (cùng ngưỡng với giao diện trong game).</p>"
               "<h3>Khắc chế: phòng vệ chặn loại đạn nào</h3>" + table(['Phòng vệ', 'Chặn hoặc giảm', 'Không chặn'], counters)
               + "<p class='muted'>Luật này được test <code>ArmourTests.CountersFollowTheTable</code> kiểm tra (bảng gốc ở DECISIONS 14A C.9).</p>"
               + (f"<h3>Icon giáp và dạng vũ khí</h3>{legend}<div class='caption'>Bộ icon trong game (prompt 15): cấp giáp, dạng vũ khí, dấu phụ.</div>" if legend else '')
               + f"<h3>Toàn bộ vũ khí ({len(wrows)})</h3>"
               + table(['Vũ khí', 'Loại', 'Xuyên', 'Dạng · dấu', 'Sát thương', 'Loạt / băng', 'Hồi (s)', 'Tốc độ đạn', 'Tầm', 'Tối thiểu', 'Nổ lan', 'Mục tiêu', 'DPS', 'Trên xe'], wrows, 'dps') + '</div>')
    out.append(programme.rates_and_ballistics(game, h))
    out.append(programme.blast_radii(game, h))
    out.append(programme.boss_summary(game, h))
    # Prompt 25 F1: DPS by armour level, missile flight, model and round sizes, the main bosses' super weapons.
    out.append(prompt25.f1_section(game, h))
    # Prompt 25 G / 26: second rounds, the bosses' two-layer blasts and phases, the Boss Hunt.
    out.append(prompt26.rounds_section(game, h))
    out.append(prompt26.boss_blast_section(game, h))
    out.append(prompt26.hunt_section(game, h))
    # Prompt 34 L9: weapon families and tiers, the bosses' family rounds, radii and warnings.
    out.append(prompt34.section10(game, h))
    # Full fix L10 items 2-7: the boss weapons' cadence, the families, munition behaviour, warning rings, effect lifetimes.
    out.append(fix_full.section10_fix(game, h))
    out.append(prompt27.section(game, h))
    # Prompt 31 L6: the game-made decks and the battlefield events.
    out.append(prompt31.section(game, h))

    # ------------------------------------------------------------------ towers, elites, bosses
    def simple_rows(vs):
        return [[f"<b>{esc(v['name'])}</b>", esc(price_of(v)[0]), esc(armour_text(v)), num(v['hp']), f"{v['speed']:g}",
                 esc(', '.join(w['id'] for w in v['weapons'])), f"{v['dpsVs']['Light']:.0f} / {v['dpsVs']['Heavy']:.0f} / {v['dpsVs']['Air']:.0f}",
                 esc(', '.join(v['skills'])), esc(refs_text(v))] for v in vs]
    head = ['Tên', 'Giá', 'Giáp', 'Máu', 'Tốc độ', 'Vũ khí', 'DPS nhẹ/nặng/bay', 'Kỹ năng', 'Tham khảo']

    def tower_groups(towers):
        # A tower's branch variants (aa_turret.flak) follow their tower, named after it and the branch.
        base = {t['id']: t for t in towers}
        branch = {b['id']: (t['id'], b['name']) for t in game['base']['towers'] for b in t['branches']}
        ordered = []
        for t in towers:
            if t['id'] in branch:
                continue
            ordered.append(t)
            for bid, (owner, bname) in branch.items():
                if owner == t['id'] and bid in base:
                    ordered.append(dict(base[bid], name=f"{t['name']} · nhánh {bname}", size=t.get('size', '')))
        towers = ordered
        sizes = [('Small', 'Tháp ô nhỏ'), ('Medium', 'Tháp ô vừa'), ('Large', 'Tháp ô lớn')]
        known = {s for s, _ in sizes}
        return [(label, [t for t in towers if t.get('size') == s]) for s, label in sizes] + \
               [('Công sự khác (trung lập, pháo đài, boss)', [t for t in towers if t.get('size') not in known])]
    out.append("<div class='section'><h2>11. Tháp canh, xe tinh nhuệ và boss</h2>"
               "<h3>Tháp và công sự</h3><p>Tháp cố định chặn lưới đường đi khi xuất hiện; trong Chiếm cứ điểm mỗi cứ điểm có tháp trung lập bắn mọi phe và dựng lại "
               "sau một thời gian; mỗi phe có sở chỉ huy (HQ) có máu (phá được hay không tùy chế độ, phần 6). Tháp của căn cứ người chơi xếp theo cỡ ô (phần 6), có hạng, nhánh ở hạng 7 và 3 ô đồ.</p>"
               + ''.join(f"<h4>{esc(label)} ({len(ts)})</h4>" + ''.join(vehicle_card(t, imgdir) for t in ts)
                         for label, ts in tower_groups(game['towers']) if ts)
               + "<h3>Xe tinh nhuệ</h3><p>Phiên bản tân trang: +60% máu, +25% sát thương, 1–2 kỹ năng tinh nhuệ, thanh máu vàng và vòng vàng trên bản đồ nhỏ; "
               "sức mạnh thực đo được 1,8–2,2 lần bản thường. Địch không còn nhận tinh nhuệ theo xác suất mà theo <b>ngân sách</b>: tinh nhuệ giá 1,6 lần, phần chi tiêu "
               "theo độ khó (Dễ 5%, Thường 10%, Khó 15%, Anh hùng 20%, Thép 25%), trần 1–5 xe cùng lúc; tướng ưu tiên loại xe của mình. Hạ tinh nhuệ hoàn CP theo giá thật "
               "và thưởng một ít xu, có tỷ lệ nhỏ rơi bản thiết kế.</p>"
               + table(head, simple_rows(game['elites']))
               + "<h3>Boss</h3>" + programme.boss_rules(game, h)
               + ''.join(vehicle_card(v, imgdir) + programme.boss_parts(v, h)
                         + (f"<p class='muted'>{esc(v['bossFile'])}</p>" if v.get('bossFile') else '') for v in game['bosses']) + '</div>')

    # ------------------------------------------------------------------ supports
    def support_price(s):
        if s.get('consumable'):
            return f"vật phẩm: {s.get('coins', 0):,}".replace(',', '.') + f" xu / {game['economy'].get('itemPack', 2)} cái"
        if s.get('eventOnly') or not s['cost']:
            return 'không phải thẻ (boss, sự kiện)'
        return f"{s['cost']} CP; mở khóa: {unlock_text(s.get('route'), s.get('coins', 0))}"
    rows = [[f"<b>{esc(s['name'])}</b><br><span class='muted'>{esc(s['info'])}</span>{guide_html(s.get('guide', ''))}", esc(s['kind']), esc(support_price(s)), f"{s['cooldown']:g} s",
             num(s['damage']) if s['damage'] else '', f"{s['radius']:g}" if s['radius'] else '', s['count'] or '',
             f"{s['duration']:g}" if s['duration'] else ''] for s in game['supports']]
    out.append("<div class='section'><h2>12. Hỗ trợ hỏa lực</h2><p>Thẻ hỗ trợ trong bộ bài (2 ô), gọi vào một điểm trên bản đồ; không gọi được vào vùng căn cứ địch; "
               "vật phẩm dùng một lần mua bằng xu. Mỗi thẻ hỗ trợ có clip Xem bắn riêng (gọi hỏa lực lên một cụm mục tiêu).</p>"
               + table(['Hỗ trợ', 'Loại', 'Giá', 'Hồi', 'Sát thương', 'Bán kính', 'Số lượng', 'Thời gian'], rows)
               + f"{img(imgdir / 'r6' / 'supports.png', 'shot')}<div class='caption'>Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, "
               "ném bom rải thảm, MOAB, bom chùm, máy bay pháo, EMP, khói, tiếp tế, chi viện).</div></div>")
    out.append(programme.price_list(game, h, unlock_text))
    out.append(programme.commanders(game, h))

    out.append(programme.ammo_system(game, h))

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
               f"<p>{rar}</p>" + img(ui / 'screen-army-gear-vi-16x9.png', 'shot')
               + "<div class='caption'>Quân đội › Trang bị: chọn một ô là hiện ngay các món hợp lệ và so sánh với món đang gắn.</div>"
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
               + f"{img(ui / 'screen-shop-crates-vi-16x9.png', 'shot')}<div class='caption'>Cửa hàng › Hòm: ảnh hòm, nội dung, tỷ lệ và giá trên từng ô.</div></div>")

    # ------------------------------------------------------------------ maps
    out.append(f"<div class='section'><h2>15. Bản đồ</h2><p>{len(game['maps'])} chiến trường 300 × 300 m, cộng {LONG_MAPS} bản dài 300 × 480 m (phần 7b) (8 bản đồ mới: " + ', '.join(mp.get(i, i) for i in ('landingbeach', 'hydrodam', 'capital', 'launchsite', 'saltflat', 'borderbridge', 'swamp', 'coralisles')) + ")"
               ", đường viền không đều; phần ngoài viền vẫn được dựng "
               "như bản đồ (nhà, rừng, đá) chỉ để trang trí, ranh giới là đường đứt nét. Mỗi trại có sở chỉ huy và ô tháp nhỏ/vừa/lớn/tiện ích; mỗi cứ điểm có tiền đồn. "
               "Phiên bản công thành đặt pháo đài chiếm 45% bản đồ ở đông bắc (phần 7).</p>")
    for m in game['maps']:
        out.append(f"<div class='map'><h3>{esc(m['name'])} <span class='muted'>· {esc(m['theme'])}</span></h3><p>{esc(m['sub'])}</p>"
                   f"{img(imgdir / 'maps' / (m['id'] + '.png'), '')}</div>")
    # Prompt 33 L7: 15g, the four zones, edge types, terrain tags, landmarks, rails, sea routes and the validators.
    out.append(prompt33.section15(game, h))
    out.append(f"<h3>Pháo đài ({mp.get('ashfield', 'Đồng Tro')}, bản công thành)</h3>{img(imgdir / 'maps' / 'ashfield_siege.png', '')}</div>")

    # ------------------------------------------------------------------ AI and systems
    out.append("<div class='section'><h2>16. AI và hệ thống</h2><ul>"
               "<li><b>Chỉ huy AI</b> (cho cả hai phe): chọn mục tiêu, tập hợp quân rồi tiến theo nhóm, giữ/chiếm cứ điểm, gọi hỏa lực vào cụm địch (không vào quân mình), "
               "mua quân khắc chế (địch nhiều máy bay → mua phòng không, nhiều giáp → mua diệt tăng...).</li>"
               "<li><b>Giao thông:</b> bản đồ làn đường (đường, lộ trình chính, lối hẹp, cổng), cấm đỗ ở cổng/lối hẹp, xe đang đỗ nhường đường theo ưu tiên, "
               "nhóm cùng đích không bắt nhau nhường, luân phiên qua cổng, tìm đường vòng có tính chi phí khi bị kẹt.</li>"
               "<li><b>Xe kẹt (prompt 12):</b> bộ phát hiện xe kẹt (xe có đích mà 8 giây không đi quá 2,5 m) ghi lại lý do, vị trí, "
               "vật xung quanh và dữ liệu phát lại; chạy trong bản build nội bộ, báo cáo có bản đồ nhiệt ở Docs/stuck-report. "
               "Đã sửa tận gốc: đích luôn quy về vùng xe tới được (không tìm đường tới túi kín hay sau cổng đóng), ô đội hình ở cùng phía tường "
               "và không chéo nhau, hai xe đối đầu ngoài bãi trống thì một xe tránh sang bên, lách xe không lao vào tường, "
               "đường đi qua chỗ vừa bị chặn (tháp mới dựng) được tính lại ngay, tháp hạ xuống đẩy xe ra khỏi chân tháp, "
               "xe pháo đài canh giữ xuất hiện ở chỗ rộng. Pháo đài: cửa phụ và cổng mở của thành trong là cổng đôi 18 m, "
               "sân sau cổng để trống, và mọi bãi thả, cổng, mục tiêu có đường rộng 3 ô cho xe lớn nhất khi mọi cổng đóng và mọi ô hardpoint "
               "đầy tháp lớn nhất (công cụ dựng map tự bỏ vật cản; Tools/maps/check_access.py kiểm tra mọi map). "
               "Lưới an toàn: sau 10 giây xe kẹt được đặt ra chỗ trống, hoặc tạm đi xuyên xe phe mình, hoặc nhích lên theo đường; mỗi lần đều ghi vào báo cáo.</li>"
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

    out.append(programme.feedback(game, h))
    out.append(programme.testing(game, {'esc': esc}))

    # ------------------------------------------------------------------ UI (phase 10)
    def pair(a, ca, b, cb):
        ta, tb = img(ui / a, 'shot'), img(ui / b, 'shot')
        return (f"<div class='two'><div>{ta}<div class='caption'>{esc(ca)}</div></div>"
                f"<div>{tb}<div class='caption'>{esc(cb)}</div></div></div>")
    def one(a, ca):
        t = img(ui / a, 'shot')
        return f"{t}<div class='caption'>{esc(ca)}</div>" if t else ''
    out.append("<div class='section'><h2>18. Giao diện</h2>"
               "<p>Phong cách <b>Field Command 2.0</b> (phase 10): nền xám thép phẳng, viền 1 px, góc vuông, một màu nhấn cam cho hành động chính (góc vát), "
               "chữ Barlow / Barlow Condensed (đủ dấu tiếng Việt). Mọi màn dựng trên một bộ token màu và chữ chung và một thư viện thành phần (nút, thẻ, tab, "
               "ô chọn, công tắc, thanh chỉ số, hộp thoại, thông báo). Điều hướng 5 mục bên trái: Trang chủ, Chiến dịch, Tác chiến, Quân đội, Cửa hàng; "
               "thanh trên cùng có cấp, kinh nghiệm, xu và cài đặt. Ảnh thẻ render từ mô hình 3D thật. Mỗi màn được kiểm tra tự động ở 4 tỉ lệ màn hình "
               "(16:9, 19,5:9 tai thỏ, 20:9 đục lỗ, 4:3) và cỡ chữ Lớn: không chữ bị cắt, không thành phần chồng nhau, vùng chạm đủ lớn. "
               "Tên gọi tiếng Việt thống nhất (mỗi bản đồ một tên, xu, ngụy trang, rốc-két, la-de).</p>"
               "<p><b>Prompt 11:</b> HUD gọn trong trận (mặc định bật, tắt được trong Cài đặt): khi giao tranh HUD chỉ chiếm 26-28 % màn hình 16:9 "
               "và 21-23 % ở 20:9 (HUD đầy đủ 51-64 %). Mọi xe, tháp, công trình, thẻ hỗ trợ và vật phẩm có tên ngắn (tối đa khoảng 14 ký tự) "
               "dùng ở chỗ chật; mọi thẻ có vùng tên cao cố định 2 dòng nên ảnh, CP và cấp luôn thẳng hàng. Khiên vẽ lại bằng một shader.</p>"
               "<p><b>Prompt 14:</b> ngoài trận mọi cỡ tính theo point của máy (thanh trên 44 pt, thanh bên 72 pt với icon 23 pt, tab 40 pt, nút 44 pt, "
               "nút chính 53 pt, chữ 19 / 18 / 14 / 13 / 11 pt, cỡ Lớn gấp 1,2), thẻ trong danh sách nhỏ hơn 22 %; nội dung chiếm 70-89 % màn hình 16:9 và 20:9. "
               "Màn Căn cứ là ảnh chụp thật từ trên xuống của trại trên từng bản đồ, mũi tên đỏ là hướng địch tới, ô tháp đúng vị trí thật với cỡ 1 / 1,4 / 2, "
               "ô tiện ích hình lục giác; phủ tầm bắn (mặt đất cam, trên không xanh nhạt), chụm hai ngón để phóng to. Một bố trí chính áp cho cả 20 bản đồ theo "
               "vị trí (cổng, vòng ngoài, vòng trong, cạnh SCH, phía sau), bản đồ nào cần thì chỉnh riêng; 3 bộ căn cứ; tự xếp theo cách AI địch xếp. "
               "Sức mạnh căn cứ là đúng con số dùng để tính độ mạnh các đợt địch. Tiền đồn có tab riêng. Mỗi tháp có icon riêng.</p>")
    out.append("<h3>Trang chủ và thiết lập trận</h3>"
               + one('screen-home-vi-16x9.png', 'Trang chủ: trận AI làm nền, nhiệm vụ chiến dịch tiếp theo, thử thách hôm nay, bộ bài, bốn ô chọn chế độ / chiến trường / độ khó / thời tiết và nút XUẤT KÍCH.')
               + pair('screen-setup-mode-vi-16x9.png', 'Chọn chế độ: tên đầy đủ và mô tả một dòng.',
                      'screen-setup-map-vi-16x9.png', 'Chọn chiến trường: có ảnh xem trước.'))
    out.append("<h3>Chiến dịch</h3>"
               + pair('screen-campaign-vi-16x9.png', f"Chiến dịch: {len(game['chapters'])} chương (ảnh chụp trước prompt 20).", 'screen-campaign-chapter-vi-16x9.png', 'Một chương: nhiệm vụ, tướng địch, phần thưởng.')
               + pair('screen-briefing-vi-16x9.png', 'Briefing trước nhiệm vụ.', 'screen-dossier-vi-16x9.png', 'Hồ sơ nhân vật.'))
    out.append("<h3>Tác chiến</h3>" + one('screen-operations-vi-16x9.png', 'Tác chiến: chiến dịch của tuần (mutator), chiến dịch lớn chơi lại, Pháo đài tuần, Săn trùm, thử thách; '
                                                                                'mỗi mục có ảnh, luật, đồng hồ đổi mới và phần thưởng; chọn cấp độ ngay trong màn.'))
    out.append("<h3>Quân đội</h3>"
               + one('screen-army-deck-vi-16x9.png', 'Bộ bài: thẻ render 3D, tổng quan bộ bài, độ phủ vai trò (thiếu vai trò thì báo đỏ), chỉ huy.')
               + one('screen-army-towers-vi-16x9.png', 'Tháp và mô-đun: thẻ render 3D xếp theo cỡ, tên cao cố định 2 dòng, cấp và dòng mở khóa thẳng hàng; góc thẻ là icon riêng của tháp.'))
    out.append("<h3>Căn cứ và tiền đồn (prompt 14)</h3>"
               + one('screen-army-base-vi-16x9.png', 'Căn cứ: trên cùng là cấp SCH và dòng lên cấp tiếp theo, chọn bản đồ (có ảnh trong danh sách), 3 bộ căn cứ và Tự xếp; tự lưu. '
                                                   'Bên trái là khay tháp theo cỡ (Nhỏ / Vừa / Lớn / Tiện ích), tháp chưa mở bị mờ kèm nơi mở khóa. Giữa là ảnh thật của trại: '
                                                   'mũi tên đỏ là hướng địch tới, ô đúng vị trí và cỡ thật, ô trống ghi cỡ bằng chữ, ô khóa ghi cấp SCH cần. Bên phải là tổng quan '
                                                   'khi chưa chọn gì; dưới cùng là độ phủ căn cứ (thiếu thì báo đỏ), sức mạnh căn cứ và số ô đã dùng.')
               + pair('screen-army-base-picked-vi-16x9.png', 'Chọn một tháp: chỉ số so với tháp cùng cỡ, tầm bắn đất / không và tầm tối thiểu, vòng tầm bắn trên bản đồ, '
                                                             'tab Nhánh / Trang bị, nút Thay, Gỡ và Chi tiết.',
                      'screen-army-base-ranges-vi-16x9.png', 'Hiện tầm bắn: vùng phủ mặt đất (cam) và trên không (xanh nhạt) của cả căn cứ.')
               + pair('screen-army-outpost-vi-16x9.png', 'Tiền đồn: tab riêng, hai ô (nhỏ và vừa) quanh cứ điểm, khay tháp và mô tả cách tiền đồn hoạt động.',
                      'screen-army-base-vi-large-16x9.png', 'Căn cứ ở cỡ chữ Lớn: hai công tắc trên bản đồ chỉ còn icon.')
               + pair('screen-army-base-vi-20x9-punchhole.png', 'Căn cứ ở 20:9.', 'screen-army-base-vi-4x3.png', 'Căn cứ ở 4:3.')
               + one('kit-tower-icons.png', 'Icon riêng cho mỗi tháp và mô-đun (prompt 14 I), nhánh dùng icon của tháp gốc.')
               + one('basemaps-sheet.png', 'Ảnh trại trên 20 bản đồ, chụp từ trên xuống, kèm mũi tên hướng địch tới.'))
    out.append("<h3>Chi tiết phương tiện, tháp và công trình</h3>"
               + one('screen-detail-vi-16x9.png', 'Chi tiết phương tiện: mô hình 3D xoay, thanh chỉ số tách gốc / trang bị / cấp sau, vạch trung bình của nhóm; các tab Hướng dẫn, Vũ khí, Xem bắn, Trang bị.')
               + pair('screen-detail-tower-vi-16x9.png', 'Chi tiết tháp (mới): mô hình, chỉ số so với tháp cùng cỡ, vũ khí, Xem bắn, hạng, nhánh và 3 ô đồ.',
                      'screen-detail-module-vi-16x9.png', 'Chi tiết công trình tiện ích (mới): tác dụng cho căn cứ.'))
    out.append("<h3>Biểu tượng giáp và vũ khí (prompt 15)</h3>"
               "<p>Bộ biểu tượng vẽ mới hoàn toàn theo nét của Field Command 2.0, không dùng số và không dựa vào màu: 57 hình, không hình nào trùng hình khác "
               "(test so dữ liệu nét). <b>Giáp</b> 5 cấp đầy dần như pin: nét đứt (không giáp), viền mảnh, viền đôi, tô nửa dưới, tô kín có đinh tán; máy bay là "
               "khiên có cánh, tháp và công trình là khiên vân gạch. <b>Dạng vũ khí</b> 30 hình theo dạng đạn thật, với đạn động năng hình cho biết độ xuyên "
               "(viên tròn, viên đạn, đạn có đai, mũi tên xuyên, mũi tên đầu kép, mũi tên có vòng điện). <b>Dấu loại sát thương</b> ở góc chip: nón lõm có tia, hình nổ, "
               "ngọn lửa, chùm chấm, tia sáng; nhiệt áp có dấu riêng; động năng không có dấu. <b>Dấu phụ</b> (chỉ ở màn chi tiết và tooltip): đánh nóc, dẫn đường, nổ lan. "
               "Cỡ nhỏ nhất 34 px = 18,7 pt. Hiện ở: hàng dưới mọi thẻ xe, tháp và công trình (giáp mặt trước và 2 chip, \"+N\" nếu còn; thẻ gọn 1 chip), khay căn cứ và "
               "tiền đồn, màn chi tiết (sơ đồ giáp theo hướng, chip ở tab Vũ khí, bảng hiệu quả, dòng Mạnh với / Yếu trước tạo từ dữ liệu), giữ thẻ trong trận, dải xe "
               "đang chọn, tooltip khi chạm địch (✓ ~ ✕ cho từng xe trong bộ bài), bộ phận trùm, hàng 5 khiên ở độ phủ bộ bài và căn cứ, trang chú thích kèm bảng khắc chế. "
               "Cài đặt \"Hiện số chi tiết\" (mặc định tắt) thêm cấp và hệ số vào tooltip.</p>"
               + one('kit-combat-icons.png', 'Toàn bộ biểu tượng ở cỡ nhỏ nhất (18,7 pt), mỗi hình kèm tên, và vài chip mẫu có dấu loại sát thương ở góc.')
               + one('kit-combat-icons-small.png', 'Cùng bảng trên màn nhỏ nhất (1280 x 720, mỗi điểm ảnh panel là một điểm ảnh thật).')
               + pair('screen-detail-armour-vi-16x9.png', 'Màn chi tiết: sơ đồ giáp theo hướng (viền mỗi mặt dày theo cấp giáp), Mạnh với / Yếu trước tạo tự động.',
                      'screen-detail-weapons-vi-16x9.png', 'Tab Vũ khí: chip cạnh tên vũ khí, bảng hiệu quả với tiêu đề là 5 khiên, máy bay và công trình, mỗi ô là hệ số thật.')
               + pair('screen-army-deck-vi-16x9.png', 'Bộ bài: hàng giáp và chip dưới mỗi thẻ, hàng 5 khiên \"Giáp xuyên được\" cạnh tổng quan.',
                      'battle-hud-enemy-vi-16x9.png', 'Chạm vào địch: giáp của nó và ✓ ~ ✕ cho từng xe trong bộ bài; giữ một thẻ trong khay hiện giáp và mọi chip.')
               + one('screen-legend-vi-full.png', 'Trang chú thích (từ tab Hướng dẫn và Cài đặt): mọi biểu tượng, sơ đồ giáp, dấu, ký hiệu và bảng khắc chế.'))
    out.append("<h3>Cửa hàng và cài đặt</h3>"
               + pair('screen-shop-deals-vi-16x9.png', 'Ưu đãi.', 'screen-shop-skins-vi-16x9.png', 'Ngụy trang (trước đây là Skin).')
               + pair('screen-shop-units-vi-16x9.png', 'Đơn vị.', 'screen-shop-items-vi-16x9.png', 'Vật phẩm dùng một lần.')
               + one('screen-settings-vi-16x9.png', 'Cài đặt: đồ họa, âm thanh, điều khiển, ngôn ngữ và cỡ chữ Thường / Lớn.'))
    out.append("<h3>Trong trận: HUD gọn (prompt 11)</h3>"
               + one('battle-hud-mission-vi-16x9.png', 'Đánh trùm: thanh máu trùm hẹp một nửa với vạch pha và hàng bộ phận nhỏ; nhiệm vụ và đồng hồ gộp một dải ở mép trên; '
                                                     'thông báo nhỏ dưới dải, tự tắt sau khoảng 3 giây; khay thẻ thấp hơn 35 %: ảnh, CP và tên ngắn một dòng (giữ thẻ để xem tên đầy đủ); '
                                                     'phạt tiếp tế là chip nhỏ trên ô CP, chỉ hiện khi bị phạt.')
               + pair('battle-hud-boss-open-vi-16x9.png', 'Chạm thanh máu trùm để mở rộng tạm thời: số máu và các bộ phận cỡ đầy đủ, chạm bộ phận để bắn tập trung.',
                      'battle-hud-score-vi-16x9.png', 'Chiếm cứ điểm: dải điểm hai phe, cứ điểm và đồng hồ; bản đồ nhỏ hơn 40 % với hai nút nhỏ ở góc; Tấn công / Phòng thủ là một nút gạt icon, '
                                                      'Tự mua và Yểm trợ là hai icon bật/tắt; xe đang chọn là một dải ngay trên khay thẻ; gợi ý chỉ ở vài trận đầu.')
               + pair('battle-hud-siege-vi-16x9.png', 'Công thành: giai đoạn, tiến độ, đồng hồ, đếm ngược siêu pháo.',
                      'battle-hud-defend-vi-16x9.png', 'Phòng thủ: tuyến, đợt, siêu pháo ta, đợt tới kèm thành phần; nút đưa tháp trở lại.')
               + pair('battle-hud-waves-vi-16x9.png', 'Sinh tồn: quân ta, địch, đợt và đếm ngược trong một dải; đang nhắm hỗ trợ hỏa lực.',
                      'battle-hud-score-full-vi-16x9.png', 'HUD đầy đủ (tắt HUD gọn trong Cài đặt) để so sánh.')
               + pair('battle-choice-vi-16x9.png', 'Lựa chọn giữa các giai đoạn (tự chọn sau 15 giây).', 'battle-pause-vi-16x9.png', 'Tạm dừng.')
               + pair('battle-result-win-vi-16x9.png', 'Kết quả thắng: TIẾP TỤC là nút chính, nhận đôi xu cạnh số xu.',
                      'battle-result-loss-vi-16x9.png', 'Kết quả thua: tiêu đề là tên nhiệm vụ, điểm ghi rõ phe, 1-2 gợi ý rút từ trận và nút mở bộ bài; CHƠI LẠI là nút chính.')
               + pair('battle-result-checkpoint-vi-16x9.png', 'Thua ở nhiệm vụ nhiều giai đoạn: chơi lại từ điểm lưu.', 'battle-result-endless-vi-16x9.png', 'Kết quả Vô tận: đợt xa nhất.'))
    out.append("<h3>Bốn tỉ lệ màn hình và cỡ chữ Lớn</h3>"
               + pair('screen-home-vi-19.5x9-notch.png', '19,5:9 có tai thỏ: nội dung tránh vùng an toàn.', 'screen-home-vi-20x9-punchhole.png', '20:9 có lỗ camera và thanh cử chỉ.')
               + pair('screen-home-vi-4x3.png', '4:3 (máy tính bảng).', 'screen-home-vi-large-16x9.png', 'Cỡ chữ Lớn.')
               + pair('battle-hud-mission-vi-4x3.png', 'HUD ở 4:3.', 'battle-hud-mission-en-16x9.png', 'HUD tiếng Anh.')
               + pair('battle-hud-siege-vi-20x9-punchhole.png', 'HUD gọn ở 20:9.', 'battle-hud-mission-vi-large-16x9.png', 'HUD gọn, cỡ chữ Lớn: tên thẻ được xuống 2 dòng.'))
    out.append("<h3>Bộ thành phần</h3>"
               + pair('kit-tokens-vi-16x9.png', 'Token màu và chữ.', 'kit-buttons-vi-16x9.png', 'Nút.')
               + pair('kit-cards-vi-16x9.png', 'Thẻ.', 'kit-controls-vi-16x9.png', 'Điều khiển: tab, ô chọn, công tắc, thanh trượt.'))
    tag = img(shots / 'edge.png', 'shot')
    if tag:
        out.append(f"<h3>Mép bản đồ</h3>{tag}<div class='caption'>Đường ranh giới và cảnh ngoài viền.</div>")
    out.append('</div>')
    # ------------------------------------------------------------------ round 6 pictures
    r6 = imgdir / 'r6'
    pics = [('munitions_1.png', 'Mô hình đạn: tên lửa chống tăng và phòng không vác vai.'), ('munitions_2.png', 'Tên lửa không đối không, phòng không, không đối đất.'),
            ('munitions_3.png', 'Rocket.'), ('munitions_4.png', 'Bom và drone.'), ('munitions_5.png', 'Đạn pháo, đạn cối, đạn xuyên, đạn railgun.'),
            ('new_models.png', 'Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre.'),
            ('flame.png', 'Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen.'), ('railgun.png', 'Railgun: nạp năng lượng, tia sáng lưu lại.'),
            ('boss_death.png', 'Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích.'), ('muzzle_audit.png', 'Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra.')]
    out.append("<div class='section'><h2>19. Hình ảnh</h2>")
    shield = img(Path(__file__).resolve().parents[2] / 'Docs' / 'art' / 'shields' / 'shields.png', 'shot')
    if shield:
        out.append(f"{shield}<div class='caption'>Khiên vẽ lại (prompt 11): vòm lưới lục giác sáng ở viền, giữa trong suốt; địch đỏ cam, ta xanh; "
                   "gợn sóng chỗ trúng đạn, chập chờn khi máy phát khiên hư, sụp vỡ khi tắt; bong bóng quanh xe và trùm; bản rút gọn cho đồ họa Thấp.</div>")
    for name, cap in pics:
        tag = img(r6 / name, 'shot')
        if tag:
            out.append(f"{tag}<div class='caption'>{esc(cap)}</div>")
    out.append('</div>')
    out.append(programme.gallery(game, h, imgdir))
    # Full fix L10 and the owner's PDF rules A-E (02/10): the weapon table, the bosses, effects with shots, audio, models.
    out.append(fix_full.appendix(game, h, imgdir))
    # The bomb-run fix, pass 4: the stick parameters, before / after and the stick pictures (bomb_run.py).
    out.append(bomb_run.section(game, h, imgdir))
    if history:
        out.append("<div class='section'><h2>Phụ lục: Lịch sử đo</h2><p>Các bảng đo dưới đây đo trên dữ liệu hoặc luật khác bản hiện tại "
                   f"(prompt 29 R10). Bảng 9b: {esc(measure_stamp.describe(prompt25.measure_path()))}. Bảng 2b: đo tay ở prompt 13, không có dấu hash.</p></div>")
        out.extend(history)
    out.append('</body></html>')
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
