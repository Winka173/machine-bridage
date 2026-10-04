"""The design document's prompt 31 sections (DECISIONS "Prompt 31 L6"): "Màn bộ bài game" (each game-made deck: its status,
the 8 vehicle and 2 support cards with the loaned ones marked, the placed allies and the special rules) and "Biến cố" (the
battlefield events of prompt 31 L3 and L5: missions, when, what they change, their prebuilt ground states). Read straight
from campaign.json and the rule words in Strings.cs, so the document shows what the data holds (build_doc.py calls section).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
STRINGS = ROOT / 'Assets' / 'MachineBrigade' / 'Scripts' / 'Game' / 'Hud' / 'Strings.cs'

STATUS_VI = {'MAKE_FIRST': 'Làm trước', 'MAKE_LATER': 'Làm sau', 'READY': 'Sẵn sàng'}

# The events of prompt 31 in the sheet's words, with what each changes (the data gives the missions, times and sites).
EVENTS_VI = [
    ('sandstorm_turn', 'Bão cát đổi hướng', 'Gió đổi hướng, bão cát tràn qua một nửa bản đồ: tầm nhìn nửa đó giảm, nửa kia quang hơn; '
     'cảnh bão chỉ phủ nửa có bão.'),
    ('factory_alarm', 'Báo động nhà máy', 'Bị phát hiện thì còi báo động: cổng xưởng cán đóng (trạng thái dựng sẵn), đồn binh kéo tới.'),
    ('city_blackout', 'Mất điện thành phố', 'Đèn đường tắt, đêm xuống; mọi tháp nối lưới điện của cả hai phe ngừng 90 giây.'),
    ('betrayal_warning', 'Phản bội (báo trước)', 'Các cánh quân của Thorne được đánh dấu và có thoại 10 giây trước khi quay súng.'),
    ('orbital_pods', 'Khoang đổ bộ quỹ đạo', 'Ba khoang đáp xuống ba điểm dựng sẵn, dựng thành tháp địch; tháp bị phá thì điểm đó mở lại.'),
    ('tide_turn', 'Triều lên/xuống', 'Mỗi 150 giây bãi cạn phía đông ngập rồi khô lại (hai trạng thái dựng sẵn).'),
    ('bridge_collapse', 'Cầu sập', 'Cây cầu phía đông sập ở mốc thời gian; cầu lớn và chỗ nước cạn phía tây vẫn qua được.'),
    ('crane_fall', 'Cần cẩu đổ', 'Bắn sập cần cẩu trung lập thì cần trục đổ dọc bến, chặn lối giữa của bến (trạng thái dựng sẵn).'),
    ('ice_crack', 'Hồ băng nứt', 'Xe hạng vừa và nặng (theo hạng trọng lượng, không theo CP) ở trên hồ quá 10 giây làm nứt băng '
     'và bị chậm 40% trong 8 giây.'),
    ('dam_breach', 'Đập nứt', 'Nước sông dưới đập dâng ba mức dựng sẵn, chỉ lên không xuống: giữa chỗ nước cạn, cả chỗ nước cạn, '
     'rồi hai bờ trũng.'),
    ('mine_collapse', 'Sập hầm mỏ', 'Hầm phía đông bắc sập, hầm cũ phía tây nam được phá mở (một lần đổi trạng thái).'),
    ('lava_flow', 'Dung nham', 'Dòng dung nham cắt nhánh đông bắc của đường đắp phía tây sau 3 phút.'),
    ('forest_fire', 'Cháy rừng', 'Một mặt lửa dựng sẵn theo gió đốt lần lượt bốn dải rừng (lửa, cháy xe, khói chắn tầm nhìn) rồi tắt; '
     'dải đang cháy là vùng cấm, xe trong đó bị đẩy ra.'),
]


def _json(path):
    return json.loads(re.sub(r'^\s*//.*$', '', path.read_text(encoding='utf-8'), flags=re.M))


def _rules_vi():
    """fixeddeck.rule.<id> -> the Vietnamese words (Strings.cs)."""
    out = {}
    pattern = re.compile(r'\["fixeddeck\.rule\.(\w+)"\]\s*=\s*\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)')
    for m in pattern.finditer(STRINGS.read_text(encoding='utf-8')):
        out[m.group(1)] = m.group(3)
    return out


def _names(game):
    names = {}
    for group in ('vehicles', 'elites', 'bosses', 'supports', 'towers'):
        for v in game.get(group, []) or []:
            if isinstance(v, dict) and 'id' in v:
                names[v['id']] = v.get('name') or v['id']
    return names


def _refs(m):
    """Every event a mission names: (reference, stage id or None)."""
    out = [(r, None) for r in m.get('missionEvents', [])]
    for s in m.get('stages', []):
        out += [(r, s.get('stage')) for r in s.get('missionEvents', [])]
    return out


def _when(trigger):
    parts = []
    if 'at' in trigger:
        parts.append(f"{trigger['at']:g} giây")
    if trigger.get('every'):
        parts.append(f"lặp mỗi {trigger['every']:g} giây" + (f", {trigger['times']} lần" if trigger.get('times') else ''))
    if trigger.get('spotted'):
        parts.append('khi bị phát hiện')
    if 'propDown' in trigger:
        parts.append('khi ' + str(trigger['propDown'].get('def', 'vật thể')) + ' bị phá')
    if 'after' in trigger:
        parts.append('sau ' + str(trigger['after']))
    return ', '.join(parts) or '—'


def section(game, h):
    esc, table = h['esc'], h['table']
    camp = _json(DATA / 'campaign.json')
    missions = camp.get('missions', [])
    rules = _rules_vi()
    names = _names(game)

    def card(cid, loaned):
        text = esc(names.get(cid, cid))
        return f"<b>{text}</b> (mượn)" if cid in loaned else text

    rows = []
    for m in missions:
        d = m.get('fixedDeck')
        if not d:
            continue
        loaned = set(d.get('loanedCards', []))
        allies = []
        for a in d.get('placedAllies', []):
            label = names.get(a.get('def', ''), a.get('def', ''))
            if a.get('name'):
                label = f"{a['name']} ({label})"
            if a.get('convoy'):
                label += ', là đoàn hộ tống'
            if a.get('lossIfDestroyed') or a.get('convoy'):
                label += ', thua nếu bị phá'
            allies.append(esc(label))
        rows.append([f"<b>{esc(m['id'])}</b>", esc(STATUS_VI.get(d.get('status', ''), d.get('status', ''))),
                     ', '.join(card(c, loaned) for c in d.get('vehicleIds', [])),
                     ', '.join(card(c, loaned) for c in d.get('supportIds', [])),
                     '<br>'.join(allies) or '—',
                     '<br>'.join(esc(rules.get(r, r)) for r in d.get('specialRules', [])) or '—'])
    decks = ("<div class='section'><h2>Prompt 31: Màn bộ bài game</h2>"
             "<p>23 màn dùng bộ bài do game định sẵn (8 thẻ xe + 2 thẻ hỗ trợ, không sửa được, hạng thẻ theo đường cong hạng của "
             "chương, không trang bị). Thẻ chưa mở khóa là thẻ <b>mượn</b> (\"Mượn trong nhiệm vụ này\"): dùng được trong màn, không "
             "mở khóa vĩnh viễn, tối đa 2 thẻ một màn (c1m01: 4, vì người chơi mới chỉ có 4 thẻ xe); các thẻ khóa khác của bảng "
             "được thay bằng thẻ đã mở cùng vai trò. Đồng minh đặt sẵn không chiếm ô thẻ, do AI đồng minh điều khiển theo lệnh "
             "Tấn công/Phòng thủ chung. Mục tiêu gốc của mọi màn giữ nguyên.</p>"
             + table(['Màn', 'Trạng thái', 'Thẻ xe', 'Thẻ hỗ trợ', 'Đồng minh đặt sẵn', 'Luật riêng'], rows, 'dps') + '</div>')

    lib = {e['id']: e for e in camp.get('eventLibrary', {}).get('events', [])}
    erows = []
    for eid, name, what in EVENTS_VI:
        e = lib.get(eid)
        if e is None:
            continue
        where, sites = [], []
        for m in missions:
            for r, stage in _refs(m):
                rid = r if isinstance(r, str) else r.get('id')
                if rid != eid:
                    continue
                own = r if isinstance(r, dict) else {}
                trigger = {**e.get('trigger', {}), **own.get('trigger', {})}
                where.append(f"{esc(m['id'])}{' (' + esc(stage) + ')' if stage else ''}: {esc(_when(trigger))}")
                params = {**e.get('params', {}), **own.get('params', {})}
                for s in m.get('navStates', []):
                    if s['id'] == params.get('navSite') or s['id'] in params.get('sites', []):
                        states = ' → '.join(st['name'] for st in s['states'])
                        sites.append(f"{esc(m['id'])}: {esc(s['id'])} ({esc(states)})")
        erows.append([f"<b>{esc(name)}</b>", esc(e.get('kind', '')), '<br>'.join(where) or '—', esc(what), '<br>'.join(sites) or '—'])
    events = ("<div class='section'><h2>Prompt 31: Biến cố</h2>"
              "<p>Mọi biến cố đổi đường đi dùng trạng thái đường đi <b>dựng sẵn</b> (dựng và kiểm khi tải trận, không khoét lúc chạy), "
              "chỉ đổi ở ranh giới tick, mọi trạng thái đều còn đường vòng (kiểm lúc dựng chiến dịch và lúc tải trận), không nhốt xe "
              "(xe trên vùng vừa đóng được đặt ra ngoài), cảnh báo 8-12 giây bằng thông báo hệ thống và dấu trên bản đồ nhỏ (thoại chỉ "
              "là phụ), xảy ra theo đồng hồ trận hoặc điều kiện nên chơi lại cho cùng kết quả. Mây thấp bỏ (cần lối chơi theo độ cao). "
              "c9m02 và c7m17 là chiến trường đảo chiều nên không dùng trạng thái dựng sẵn; giữ biến cố cũ.</p>"
              + table(['Biến cố', 'Loại', 'Màn: lúc nào', 'Thay đổi', 'Trạng thái dựng sẵn'], erows, 'dps') + '</div>')
    return decks + events
