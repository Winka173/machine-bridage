"""The design document's full fix L10 sections (Docs/prompts/fix_full_vi.txt "Lượt 10" and the owner's PDF rules A-E;
DECISIONS "Sửa lỗi tổng hợp L9.7/L10 (lane C)"). Every number is read from the data, never written by hand: balance.json now
and at 07444b14 (git show), the ExportGameDoc export (game.json: the weapons as the game resolves them, "fixDoc" with the
warning / munition rules, the effects by tier and the audio mix), the balance tools (full_weapon_audit's real rates,
fix_boss_weapons' boss rows before and after), Docs/checks, Docs/audio, Docs/models and the effect recipes in the code.

    build_doc.py calls: section10_fix (10j-10n: boss rates, families, munition behaviour, warning rings, effects),
    ballistics_extra (the "Đường đạn" table's new columns), appendix (section 20: A-E) and the card helpers.

Images (build_doc's image dir, `<img>`); a missing one is a grey "shot pending" box naming the file it waits for:
    <img>/fx/<key>/fire_0s.png, fire_0.2s.png, fire_1s.png, impact_0s.png, impact_0.5s.png, impact_2s.png, impact_10s.png,
        impact_30s.png, salvo.png, salvo_impact.png; <img>/fx/index.json        (MachineBrigade.Editor.EffectShots.FxBatch:
        <key> = tier_T0..tier_T5 or the weapon id)
    <img>/scan/<model>.png and <model>_old.png                                  (ModelScan.RenderBatch, the L8 scan)
    <img>/scan_after/<model>.png                                                (ModelScan after the L8 rebuilds, -mbScan)
"""
from __future__ import annotations

import csv
import html
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Tools' / 'balance'))

BASE = '07444b14'
BALANCE_REL = 'Assets/MachineBrigade/Resources/Data/balance.json'
SCRIPTS = ROOT / 'Assets' / 'MachineBrigade' / 'Scripts'
FIRE_MOMENTS = ('0', '0.2', '1')
IMPACT_MOMENTS = ('0', '0.5', '2', '10', '30')
REF_TARGETS = [('main_battle_tank', 'Tăng chủ lực'), ('heavy_tank', 'Tăng hạng nặng'), ('ifv', 'Xe chiến đấu bộ binh'),
               ('armored_car', 'Xe bọc thép bánh lốp')]
SLOW_SPEED = 4.5          # the prompt's slow reference vehicle (m/s)
SPACING = 8.0             # the splash proxy: five reference vehicles 8 m apart
TYPE_VI = {'Kinetic': 'Động năng', 'ArmorPiercing': 'Xuyên giáp', 'HighExplosive': 'Nổ mạnh', 'Fire': 'Lửa', 'Flak': 'Phòng không',
           'ShapedCharge': 'Nổ lõm', 'Fragmentation': 'Mảnh', 'Energy': 'Năng lượng'}
TARGET_VI = {'Ground': 'mặt đất', 'Air': 'trên không', 'All': 'tất cả'}

_CACHE: dict = {}


# --------------------------------------------------------------------------------------------- helpers

def _e(s):
    return html.escape(str(s if s is not None else ''))


def _n(x, d=1):
    """A number the Vietnamese way (comma decimals, no trailing zeros); '—' for None."""
    if x is None or x == '':
        return '—'
    try:
        v = float(x)
    except (TypeError, ValueError):
        return _e(x)
    if math.isinf(v) or math.isnan(v):
        return '—'
    s = f"{v:,.{d}f}".replace(',', ' ')
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')


def _table(h, head, rows, cls='dps'):
    t = (h or {}).get('table')
    if t:
        return t(head, rows, cls)
    hh = ''.join(f'<th>{_e(c)}</th>' for c in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f"<table class='{cls}'><thead><tr>{hh}</tr></thead><tbody>{body}</tbody></table>"


def _ba(before, after, d=1, fmt=None):
    """Two cells, before and after; the after one bold when it changed."""
    f = fmt or (lambda v: _n(v, d))
    b, a = f(before), f(after)
    return [b, f"<b>{a}</b>" if b != a else a]


def _pending(path, label=''):
    return (f"<div class='pending'><div>shot pending</div><code>{_e(path)}</code>"
            + (f"<div>{_e(label)}</div>" if label else '') + "</div>")


def _shot(h, imgdir, rel, label=''):
    """The image at <imgdir>/<rel> through build_doc's img(), else a grey 'shot pending' box naming the file."""
    path = Path(imgdir) / rel
    tag = h['img'](path, 'fx', label) if path.exists() and h and h.get('img') else ''
    return tag or _pending(rel, label)


def _git_show(rev, rel):
    try:
        out = subprocess.run(['git', 'show', f'{rev}:{rel}'], capture_output=True, cwd=ROOT, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.decode('utf-8') if out.returncode == 0 else None


def ctx():
    """Current and 07444b14 balance data, resolved weapons, the audit rows and the boss rows (computed once)."""
    if _CACHE:
        return _CACHE
    import full_weapon_audit as W
    import p34_families as F
    from jsonc_edit import Doc, loads
    cur = Doc(F.PATH).data()
    W.DATA.update(cur)
    rows, built, ws = W.audit(cur)
    old = None
    txt = _git_show(BASE, BALANCE_REL)
    if txt:
        try:
            old = loads(txt)
        except Exception:  # noqa: BLE001 - an unreadable old file only loses the before columns
            old = None
    ows = F.Weapons(old) if old else None
    old_ids = {w['id'] for w in old['weapons']} if old else set()
    old_users = {}
    if old:
        try:
            old_users = W.users(old, W.A.expand(old))
        except Exception:  # noqa: BLE001
            old_users = {}
    _CACHE.update(W=W, F=F, cur=cur, rows={r['id']: r for r in rows}, built=built, ws=ws, old=old, ows=ows, old_ids=old_ids,
                  old_users=old_users)
    return _CACHE


def _old(wid):
    c = ctx()
    if not c['ows'] or wid not in c['old_ids']:
        return None
    try:
        return c['ows'].resolve(wid)
    except Exception:  # noqa: BLE001
        return None


def _old_numbers(wid):
    w = _old(wid)
    if w is None:
        return None, None, None
    W = ctx()['W']
    nb = W.numbers(w)
    try:
        _, ref, ratio = W.flags_rate(w, nb, W.real_entry(w))
    except Exception:  # noqa: BLE001
        ref, ratio = '', None
    return w, nb, ratio


def game_weapons(game):
    """{weapon id: (first entry in game.json, [carrier names], [(carrier id, slot, aim, main)])} over every group."""
    if 'gw' in _CACHE and _CACHE.get('gw_of') is id(game):
        return _CACHE['gw']
    out = {}
    for group in ('vehicles', 'itemVehicles', 'elites', 'bosses', 'towers'):
        for v in game.get(group, []):
            for w in v.get('weapons', []):
                e = out.setdefault(w['id'], [w, [], []])
                e[1].append(v.get('short') or v.get('name') or v['id'])
                e[2].append((v['id'], w.get('slot', ''), w.get('aim', ''), w.get('mainMount', None), group))
    _CACHE['gw'] = out
    _CACHE['gw_of'] = id(game)
    return out


def _raw(w):
    return (w or {}).get('raw') or {}


def _cal(w):
    return w.get('caliberMm', _raw(w).get('CaliberMm')) or 0


def _cal_of(wid, w):
    """The calibre from the export, else from balance.json (an export older than full fix L2 has none)."""
    r = ctx()['rows'].get(wid)
    return _cal(w) or (r['w'].get('caliberMm') if r else 0) or 0


def _tier_of(wid, w):
    """The weapon's tier: the export's, else its family's in weaponFamilyTable; 3 when neither says."""
    t = w.get('tier', _raw(w).get('Tier'))
    if t is not None and t >= 0:
        return int(t)
    r = ctx()['rows'].get(wid)
    fam = r['w'].get('weaponFamilyId') if r else None
    tiers = {x['id']: x.get('tier') for x in ctx()['cur'].get('weaponFamilyTable', [])}
    return int(tiers.get(fam, 3) if tiers.get(fam) is not None else 3)


def _kg(w):
    return w.get('warheadKg', _raw(w).get('WarheadKg')) or 0


def _cycle(w):
    return w.get('cycle', _raw(w).get('CycleSeconds')) or 0


def _rpc(w):
    return w.get('roundsPerCycle', _raw(w).get('RoundsPerCycle')) or 0


def _barrels(w):
    return w.get('barrels', _raw(w).get('Barrels')) or 1


def _family(w):
    return w.get('familyId') or _raw(w).get('WeaponFamilyId') or ''


def _mount_node(slot, aim, main):
    if main and (aim or 'Turret') == 'Turret':
        return 'Turret / Muzzle_' + (slot or 'main')
    return f"Mount_{slot}" if aim == 'Free' else f"Muzzle_{slot or 'main'}"


def real_rate(wid):
    """(max rpm, practical rpm, source, game / real ratio) from full_weapon_audit's REAL table, or Nones."""
    r = ctx()['rows'].get(wid)
    if not r or not r.get('real'):
        return None, None, '', None
    real = r['real']
    return real.get('rpm'), real.get('prac'), real.get('src', ''), r.get('ratio')


def changed_ids():
    """Weapons whose cadence, damage, blast, barrels, calibre or family differ from 07444b14 (the fix's changes)."""
    if 'changed' in _CACHE:
        return _CACHE['changed']
    c = ctx()
    W = c['W']
    # The numbers that play (not the display fields caliberMm / warheadKg or the family labels, which every line gained).
    keys = ('damage', 'splash', 'edge', 'cooldown', 'burst', 'burstInterval', 'clip', 'clipReload', 'barrels', 'salvoMode',
            'projectileSpeed', 'range', 'minRange', 'damageType', 'pen', 'ammo', 'reload')
    default = {'burst': 1, 'barrels': 1, 'salvoMode': 'RIPPLE', 'burstInterval': 0.1, 'cooldown': 1.0}
    out = set()
    for wid, r in c['rows'].items():
        o = _old(wid)
        if o is None:
            out.add(wid)
            continue
        w = r['w']
        if any((w.get(k) or default.get(k, 0)) != (o.get(k) or default.get(k, 0)) for k in keys):
            out.add(wid)
            continue
        if abs(W.numbers(w)['cycle'] - W.numbers(o)['cycle']) > 1e-6:
            out.add(wid)
    _CACHE['changed'] = out
    return out


def ballistics_extra(wid, w):
    """The 'Đường đạn' table's new cells for one weapon (L10 item 1): calibre, warhead, family, barrels, cycle, real rate,
    sustained DPS and whether this fix changed it."""
    rpm, prac, src, _ = real_rate(wid)
    rate = f"{_n(rpm, 0)}" + (f" / {_n(prac, 0)}" if prac else '') if rpm else '—'
    return {'cal': _n(_cal(w), 1) if _cal(w) else '—', 'kg': _n(_kg(w), 1) if _kg(w) else '—', 'family': _e(_family(w) or '—'),
            'barrels': str(_barrels(w)), 'cycle': _n(_cycle(w), 2) if _cycle(w) else '—', 'real': rate,
            'dps': _n(w.get('dps'), 0), 'changed': wid in changed_ids()}


# --------------------------------------------------------------------------------------------- cards (L10 items 8-9)

def card_rate(w):
    """'loạt N · chu kỳ X s' for a salvo or magazine, else 'mỗi X s' (L10 item 8)."""
    n, cycle = _rpc(w), _cycle(w)
    if not cycle:
        return '—'
    if n and n > 1:
        return f"loạt {n} · chu kỳ {_n(cycle, 2)} s"
    return f"mỗi {_n(cycle, 2)} s"


def card_size(w):
    if _cal(w):
        return f"{_n(_cal(w), 1)} mm"
    if _kg(w):
        return f"{_n(_kg(w), 1)} kg"
    raw = _raw(w)
    if raw.get('PowerKw'):
        return f"{_n(raw['PowerKw'], 0)} kW"
    if raw.get('EnergyMj'):
        return f"{_n(raw['EnergyMj'], 0)} MJ"
    return '—'


def card_blast(w):
    core, edge = float(w.get('splash', 0) or 0), float(w.get('splashEdge', 0) or 0)
    if core <= 0:
        return '—'
    return f"{_n(core, 1)} / {_n(edge, 1)} m" if edge > core else f"{_n(core, 1)} m"


# --------------------------------------------------------------------------------------------- 10j-10n (L10 items 2-7)

def section10_fix(game, h):
    c = ctx()
    gw = game_weapons(game)
    out = ["<div class='section'><h2>10j. Sửa lỗi tổng hợp: nhịp bắn boss, họ vũ khí, hành vi đạn, vòng cảnh báo, hiệu ứng</h2>"
           "<p>Sinh từ dữ liệu (balance.json, bản xuất của game, công cụ cân bằng). Cột <i>trước</i> là dữ liệu ở commit "
           f"<code>{BASE}</code> (trước prompt 27 và lần sửa này); <b>đậm</b> là số đã đổi.</p>"]
    # Item 2: the boss weapons (p26_*): new cadence, full cycle, barrels.
    rows = []
    for wid in sorted(x for x in c['rows'] if x.startswith('p26_')):
        r = c['rows'][wid]
        if not r['users']:
            continue
        w, nb = r['w'], r['nb']
        o, onb, _ = _old_numbers(wid)
        g = gw.get(wid, [{}])[0]
        rows.append([f"<code>{_e(wid)}</code>", _e(w.get('real') or ''), _e(w.get('weaponFamilyId') or ''),
                     *_ba(onb['barrels'] if onb else None, nb['barrels'], 0), _e(w.get('salvoMode') or 'RIPPLE'),
                     *_ba(onb['n'] if onb else None, nb['n'], 0), *_ba(onb['cycle'] if onb else None, nb['cycle'], 2),
                     *_ba(onb['dps'] if onb else None, nb['dps'], 0), _n(g.get('dps'), 0)])
    out.append(f"<h3>Nhịp bắn vũ khí boss (p26_*, {len(rows)} vũ khí)</h3><p>Số phát mỗi chu kỳ tính mọi nòng; DPS trên giấy là một "
               "chu kỳ chia thời gian chu kỳ (cả nạp bệ); DPS trong game nhân thêm hệ số sát thương của boss.</p>"
               + _table(h, ['Vũ khí', 'Tên thật', 'Họ', 'Nòng trước', 'Nòng sau', 'Chế độ loạt', 'Phát/chu kỳ trước', 'Phát/chu kỳ sau',
                            'Chu kỳ trước (s)', 'Chu kỳ sau (s)', 'DPS giấy trước', 'DPS giấy sau', 'DPS trong game'], rows))
    # Item 4: weapon families.
    fams = c['cur'].get('weaponFamilyTable', [])
    members = {}
    for wid, r in c['rows'].items():
        if r['users'] and r['w'].get('weaponFamilyId'):
            members.setdefault(r['w']['weaponFamilyId'], []).append(r)
    frows = []
    for f in fams:
        ms = members.get(f['id'], [])
        boss = [m for m in ms if any(g == 'boss' for g, _, _ in m['users'])]
        pick = (boss or ms or [None])[0]
        w = pick['w'] if pick else {}
        real = (pick or {}).get('real') or {}
        cal = w.get('caliberMm') or w.get('warheadKg')
        unit = 'mm' if w.get('caliberMm') else 'kg' if w.get('warheadKg') else ''
        frows.append([f"<code>{_e(f['id'])}</code>", _e(f.get('name', '')), f"T{f.get('tier', '?')}",
                      _n(f.get('bossDamage', w.get('damage')), 0), _n(f.get('bossCore', w.get('splash')), 1), _n(f.get('bossEdge', w.get('edge')), 1),
                      f"{_n(cal, 1)} {unit}" if cal else '—', str(len(ms)),
                      _e(', '.join(sorted((f.get('variants') or {}).keys())) or '—'), _e(real.get('src', '') or '—')])
    out.append(f"<h3>Họ vũ khí ({len(frows)})</h3><p>weaponFamilyTable: sát thương mỗi phát (boss), lõi / rìa, cỡ của vũ khí mẫu (của boss nếu có), "
               "số dòng vũ khí đang dùng, các biến thể (mỗi biến thể có lý do trong bảng), nguồn ngoài đời của nhịp bắn (full_weapon_audit).</p>"
               + _table(h, ['Họ', 'Tên', 'Bậc', 'Sát thương / phát', 'Lõi (m)', 'Rìa (m)', 'Cỡ', 'Số vũ khí', 'Biến thể', 'Nguồn ngoài đời'], frows))
    out.append(munition_section(game, h))
    out.append(warning_section(game, h))
    out.append(effects_life_section(game, h))
    out.append('</div>')
    return '\n'.join(out)


def _md_tables(path):
    """[(heading, header cells, rows)] of every pipe table in a Markdown file."""
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').splitlines()
    out, heading, i = [], '', 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#'):
            heading = line.lstrip('#').strip()
        if line.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s\-|:]+\|$', lines[i + 1].strip()):
            head = [x.strip() for x in line.strip().strip('|').split('|')]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')])
                i += 1
            out.append((heading, head, rows))
            continue
        i += 1
    return out


def munition_section(game, h):
    """Item 5: munition behaviour by group (Docs/checks/munition_behavior.md, read from the code before and after pass 4) and the flare rules."""
    tables = _md_tables(ROOT / 'Docs' / 'checks' / 'munition_behavior.md')
    after = next((t for t in tables if t[0].startswith('After')), None)
    before = next((t for t in tables if not t[0].startswith('After')), None)
    m = ((game.get('fixDoc') or {}).get('munitionRules')) or ctx()['cur'].get('munitionRules', {})

    def pair(v, key):
        x = v.get(key)
        return f"{x[0]}–{x[1]}" if isinstance(x, list) and len(x) == 2 else '—'

    rules = [
        ['Một lần thả pháo sáng', f"kéo lệch {_n((m.get('FlareDecoyChance', m.get('flareDecoyChance', 0.35))) * 100, 0)}% tên lửa hồng ngoại × (1 − kháng pháo sáng), mỗi tên lửa một lần thử"],
        ['Tên lửa bị lừa nổ ở', f"{_n(m.get('FlareOffset', m.get('flareOffset')), 0)} m sau / cạnh máy bay (luôn ngoài ngòi nổ)"],
        ['Ngòi nổ cận đích (tên lửa phòng không)', f"{_n(m.get('ProximityFuze', m.get('proximityFuze')), 0)} m"],
        ['Tự hủy khi mục tiêu xa hơn', f"tầm × {_n(m.get('ReachScale', m.get('reachScale')), 2)}"],
        ['Đạn không dẫn đường đón trước', f"tối đa {_n(m.get('LeadCap', m.get('leadCap')), 1)} s chuyển động của mục tiêu"],
        ['Số pháo sáng mỗi lần thả', f"tiêm kích {pair(m, 'flaresFighter')}, trực thăng {pair(m, 'flaresHelicopter')}, máy bay lớn {pair(m, 'flaresLarge')}"],
        ['Pháo sáng cháy', f"{pair(m, 'flareBurn')} s"],
        ['Dẫn đường radar (pháo sáng vô hiệu)', _e(', '.join(m.get('radarGuided') or []) or '—')],
        ['Dẫn đường theo tầm nhìn người bắn', _e(', '.join(m.get('sightGuided') or []) or '—')],
        ['Điểm phát pháo sáng', 'các nút Mount_Flare_* của model (≥ 2 mỗi đơn vị có pháo sáng; fix_validate mục 6)'],
    ]
    out = ["<h3>Hành vi đạn</h3><p>Theo nhóm, đọc từ mã (Docs/checks/munition_behavior.md: trước và sau lượt 4).</p>"]
    if after:
        out.append('<h4>Sau lần sửa</h4>' + _table(h, ['Nhóm', 'Cách nhắm', 'Khi nào nổ', 'Khi nào trượt', 'Vòng cảnh báo'], [[_e(x) for x in r] for r in after[2]]))
    if before:
        out.append('<h4>Trước lần sửa</h4>' + _table(h, ['Nhóm', 'Cách nhắm', 'Khi nào nổ', 'Vì sao trượt (trước)', 'Vòng (trước)'], [[_e(x) for x in r[:5]] for r in before[2]]))
    out.append('<h4>Luật pháo sáng và đạn bay</h4>' + _table(h, ['Luật', 'Giá trị'], rules, ''))
    return '\n'.join(out)


def warning_section(game, h):
    """Item 6: the warning rings' display rules and the time formula (warningRules)."""
    r = ((game.get('fixDoc') or {}).get('warningRules')) or {}
    d = ctx()['cur'].get('warningRules', {})

    def v(key, dkey):
        return r.get(key, d.get(dkey))

    rows = [
        ['Vũ khí có cảnh báo', f"pháo từ {_n(v('GunMinMm', 'gunMinMm'), 0)} mm, rốc-két từ {_n(v('RocketMinMm', 'rocketMinMm'), 0)} mm, bom từ "
                               f"{_n(v('BombMinKg', 'bombMinKg'), 0)} kg (bậc T4+ của họ); không bao giờ đạn dẫn đường hay tia"],
        ['Thời gian cảnh báo', f"min({_n(v('Cap', 'cap'), 1)} s, max(sàn, {_n(v('Base', 'base'), 1)} s + lõi / {_n(v('EscapeSpeed', 'escapeSpeed'), 1)} m/s))"],
        ['Sàn', f"T4 {_n(v('FloorT4', 'floorT4'), 1)} s · 406 mm {_n(v('Floor406', 'floor406'), 1)} s · T5 {_n(v('FloorT5', 'floorT5'), 1)} s"],
        ['Vòng vẽ', 'đúng vùng sát thương: rìa khi vụ nổ có hai lớp, nếu không thì lõi'],
        ['Hiện cùng lúc', f"tối đa {_n(v('MaxShown', 'maxShown'), 0)} vòng (siêu vũ khí luôn hiện thêm)"],
        ['Gộp loạt', f"đạn của một bệ bắn trong {_n(v('SalvoMerge', 'salvoMergeSeconds'), 2)} s có vòng chạm nhau gộp thành một vòng"],
        ['Hiện dần', f"{_n(v('FadeIn', 'fadeIn'), 2)} s"],
    ]
    # Every warned weapon's ring and time, from the export.
    wrows = []
    for wid, (w, owners, _) in sorted(game_weapons(game).items()):
        if not w.get('warns'):
            continue
        core = float(w.get('splash', 0) or 0)
        t_out = core / SLOW_SPEED
        wrows.append([f"<code>{_e(wid)}</code>", _e(', '.join(sorted(set(owners)))[:60]), f"T{w.get('tier', '?')}", _n(core, 1),
                      _n(w.get('warnRadius'), 1), _n(w.get('warnSeconds'), 2), _n(t_out, 2),
                      'ĐỦ' if float(w.get('warnSeconds') or 0) + 1e-6 >= t_out else 'THIẾU'])
    return ("<h3>Vòng cảnh báo</h3>" + _table(h, ['Luật', 'Giá trị'], rows, '')
            + (f"<h4>Vũ khí có cảnh báo ({len(wrows)})</h4>"
               + _table(h, ['Vũ khí', 'Trên', 'Bậc', 'Lõi (m)', 'Vòng (m)', 'Cảnh báo (s)', 'Ra khỏi lõi ở 4,5 m/s (s)', 'Thoát'], wrows)
               if wrows else "<p class='muted'>Bản xuất chưa có cột cảnh báo (chạy lại ExportGameDoc).</p>"))


def effects_life_section(game, h):
    """Item 7: explosion and smoke lifetimes by tier, the camera shake rules."""
    fx = (game.get('fixDoc') or {}).get('effects') or {}
    tiers = fx.get('tiers') or []
    if not tiers:
        return "<h3>Hiệu ứng theo bậc</h3><p class='muted'>Bản xuất chưa có khối fixDoc (chạy lại ExportGameDoc).</p>"
    rows = [[f"T{t['tier']}", _n(t['fireballLife'], 2), f"{_n(t['smokeMin'], 1)}–{_n(t['smokeMax'], 1)}", _n(t['crater'], 0) if t['crater'] else '—',
             _n(t['shake'], 2) if t['shake'] else '—', _n(t['shotShake'], 2) if t['shotShake'] else '—',
             str(t['fullCap']) if t['fullCap'] >= 0 else 'không giới hạn'] for t in tiers]
    return ("<h3>Hiệu ứng: thời gian tồn tại theo bậc, rung camera</h3>"
            + _table(h, ['Bậc', 'Cầu lửa (s)', 'Khói / bụi (s)', 'Hố / vết cháy (s)', 'Rung khi nổ', 'Rung khi bắn', 'Tối đa đầy đủ cùng lúc'], rows)
            + f"<p>Rung camera chỉ từ T4, chỉ khi vụ nổ trên màn hình và trong {_n(fx.get('shakeReach'), 0)} m quanh tâm nhìn; giảm một nửa ở "
              f"{_n(fx.get('shakeFalloff'), 0)} m; cộng dồn tối đa {_n(fx.get('shakeCap'), 2)}; phát bắn rung {_n(fx.get('shotShare'), 2)} lần vụ nổ; "
              "tắt được trong Cài đặt. Chi tiết theo khoảng cách nhìn: đầy đủ dưới "
              f"{_n(fx.get('nearView'), 0)} m, giảm ({_n((fx.get('reducedShare') or 0) * 100, 0)}% hạt) dưới {_n(fx.get('midView'), 0)} m, xa thì chỉ chớp và vòng.</p>")


# --------------------------------------------------------------------------------------------- section 20: A-E

def appendix(game, h, imgdir):
    out = ["<div class='section'><h2>21. Sửa lỗi tổng hợp: phụ lục A–E</h2>"
           "<p>Phần xuất tài liệu của lượt 10 (chủ dự án, 02/10). Mọi số sinh từ dữ liệu; ảnh do Unity dựng (EffectShots.FxBatch, ModelScan). "
           f"Cột <i>trước</i> là dữ liệu ở commit <code>{BASE}</code>.</p>",
           section_a(game, h), section_b(game, h), section_c(game, h, imgdir), section_d(game, h), section_e(game, h, imgdir), "</div>"]
    return '\n'.join(out)


def _carriers_turret(ids, data, built=None):
    """The first carrier's turret turn rate (degrees a second, balance.json; inherits followed)."""
    veh = {v['id']: v for v in data.get('vehicles', [])}
    if built:
        veh.update(built)

    def field(v, key, depth=0):
        if v is None or depth > 8:
            return None
        if key in v:
            return v[key]
        return field(veh.get(v.get('inherits') or v.get('variantOf') or ''), key, depth + 1)

    for i in ids:
        x = field(veh.get(i), 'turretTurnRate')
        if x:
            return x
    return None


def section_a(game, h):
    """A: every weapon a unit carries, one row, before -> after in separate columns, split into eight tables."""
    c = ctx()
    gw = game_weapons(game)
    ids = sorted(wid for wid, r in c['rows'].items() if r['users'] or wid in gw)
    t1, t2, t3, t4, t5, t6, t7, t8 = ([] for _ in range(8))
    old = c['old'] or {}
    for wid in ids:
        r = c['rows'].get(wid)
        w = r['w'] if r else {}
        nb = r['nb'] if r else c['W'].numbers(w)
        g = (gw.get(wid) or [{}, [], []])
        gx, owners, mounts = g[0], g[1], g[2]
        o, onb, oratio = _old_numbers(wid)
        o = o or {}
        mark = ' ★' if wid in changed_ids() else ''
        name = f"<code>{_e(wid)}</code>{mark}"
        users = r['users'] if r else []
        carriers = sorted({u for _, u, _ in users}) or sorted({m[0] for m in mounts})
        ocarriers = sorted({u for _, u, _ in c['old_users'].get(wid, [])})
        nodes = sorted({_mount_node(s, a, mm) for _, s, a, mm, _ in mounts}) if mounts else []
        t1.append([name, _e(w.get('real') or gx.get('real') or ''), *_ba(o.get('weaponFamilyId') or '—', w.get('weaponFamilyId') or '—', fmt=_e),
                   *_ba(o.get('weaponVariantId') or '—', w.get('weaponVariantId') or '—', fmt=_e),
                   _e(', '.join(ocarriers)[:80] or '—'), _e(', '.join(carriers)[:80] or '—'), _e(', '.join(nodes) or '—')])
        second = ', '.join(x.get('id', '') for x in gx.get('secondRounds') or []) or '—'
        t2.append([name, *_ba(o.get('caliberMm') or (o.get('size') if o.get('family') in ('tank_gun', 'howitzer', 'mortar', 'autocannon', 'mg', 'naval_gun', 'rocket') else None),
                               w.get('caliberMm'), 1),
                   *_ba(o.get('warheadKg'), w.get('warheadKg'), 1), *_ba(TYPE_VI.get(o.get('damageType'), o.get('damageType') or '—'),
                                                                        TYPE_VI.get(w.get('damageType'), w.get('damageType') or '—'), fmt=_e),
                   *_ba(o.get('pen'), w.get('pen'), 0), *_ba(o.get('projectile') or o.get('form') or 'Shell', w.get('projectile') or w.get('form') or 'Shell', fmt=_e),
                   _e(second)])
        gap_after = 0.07 if nb.get('sim') and nb['barrels'] > 1 else (w.get('burstInterval') if nb['barrels'] > 1 else None)
        gap_before = (0.07 if onb.get('sim') and onb['barrels'] > 1 else (o.get('burstInterval') if onb['barrels'] > 1 else None)) if onb else None
        t3.append([name, *_ba(onb['barrels'] if onb else None, nb['barrels'], 0), *_ba(o.get('salvoMode') or ('RIPPLE' if o else '—'), w.get('salvoMode') or 'RIPPLE', fmt=_e),
                   *_ba(gap_before, gap_after, 2), *_ba(onb['n'] if onb else None, nb['n'], 0), *_ba(onb['inner'] if onb else None, nb['inner'], 2),
                   *_ba(onb['pause'] if onb else None, nb['pause'], 2), *_ba(onb['cycle'] if onb else None, nb['cycle'], 2)])
        lv = gx.get('dpsVsLevel') or []
        paper = nb['dps']
        game_dps = float(gx.get('dps') or 0)

        def level(i):
            return paper * lv[i] / game_dps if lv and game_dps > 0 and i < len(lv) else None

        dmg_o, dmg = o.get('damage'), w.get('damage', gx.get('damage'))
        t4.append([name, *_ba(dmg_o, dmg, 0), *_ba(dmg_o * onb['n'] if dmg_o is not None and onb else None, (dmg or 0) * nb['n'], 0),
                   *_ba(onb['dps'] if onb else None, paper, 0), _n(level(0), 0), _n(level(2), 0), _n(level(4), 0), _n(level(len(lv) - 1) if lv else None, 0)])
        core_o, core = o.get('splash'), w.get('splash', gx.get('splash'))
        t5.append([name, *_ba(core_o, core, 1), *_ba(o.get('edge'), w.get('edge'), 1), _n(gx.get('warnSeconds'), 2) if gx.get('warns') else '—',
                   'có' if gx.get('warns') else 'không'])
        spd_o, spd = o.get('projectileSpeed'), w.get('projectileSpeed')
        rng_o, rng = o.get('range'), w.get('range')
        t6.append([name, *_ba(spd_o, spd, 0), *_ba(rng_o / spd_o if spd_o and rng_o else None, rng / spd if spd and rng else None, 2),
                   *_ba(rng_o, rng, 0), *_ba(o.get('minRange'), w.get('minRange'), 0),
                   *_ba(TARGET_VI.get(o.get('targets') or 'Ground', o.get('targets')) if o else None, TARGET_VI.get(w.get('targets') or 'Ground', w.get('targets')), fmt=_e)])
        arcs = sorted({f"{_n(x.get('arcCentreDeg'), 0)}° ± {_n(x.get('arcHalfDeg'), 0)}°"
                       for x in [gx] if x.get('arcHalfDeg')}) if gx else []
        t7.append([name, *_ba(_carriers_turret(ocarriers, old) if old else None, _carriers_turret(carriers, c['cur'], c['built']), 0),
                   _e(', '.join(arcs) or 'không giới hạn')])
        rpm, prac, src, ratio = real_rate(wid)
        t8.append([name, _n(rpm, 0), _n(prac, 0), _e(src or '—'), *_ba(oratio, ratio, 2)])
    head = lambda *cols: ['Vũ khí', *cols]  # noqa: E731
    ba = lambda label: [f"{label} trước", f"{label} sau"]  # noqa: E731
    return ("<h3>A. Bảng vũ khí đầy đủ</h3>"
            f"<p>{len(ids)} vũ khí (mọi boss, xe, tháp), một dòng mỗi vũ khí; ★ đã đổi trong lần sửa này; mỗi cột có <i>trước</i> và <i>sau</i>. "
            "Chu kỳ đầy đủ: (băng − 1) × hồi + thay băng, hoặc hồi + (loạt − 1) × khoảng cách loạt. DPS duy trì: một mục tiêu, trên giấy, mọi nòng, "
            "trước hệ số riêng của boss; lên giáp 0 / 2 / 4 và công trình nhân hệ số loại đạn và xuyên của game. Độ lệch giữa nòng: 0,07 s khi bắn "
            "cùng lúc (khung hình chớp), khoảng cách loạt khi bắn lần lượt.</p>"
            "<h4>A1. Định danh</h4>" + _table(h, head('Tên thật', *ba('Họ'), *ba('Biến thể'), *ba('Xe mang'), 'Bệ (Mount_* / Muzzle_*)'), t1)
            + "<h4>A2. Cỡ và đạn</h4>" + _table(h, head(*ba('Cỡ (mm)'), *ba('Đầu nổ (kg)'), *ba('Loại sát thương'), *ba('Xuyên'), *ba('Dạng đạn'), 'Đạn thay thế'), t2)
            + "<h4>A3. Nòng và loạt</h4>" + _table(h, head(*ba('Số nòng'), *ba('salvoMode'), *ba('Lệch nòng (s)'), *ba('Phát / loạt'),
                                                          *ba('Cách trong loạt (s)'), *ba('Nạp (s)'), *ba('Chu kỳ (s)')), t3)
            + "<h4>A4. Sát thương</h4>" + _table(h, head(*ba('Mỗi phát'), *ba('Mỗi loạt'), *ba('DPS 1 mục tiêu'), 'DPS giáp 0', 'DPS giáp 2',
                                                        'DPS giáp 4', 'DPS công trình'), t4)
            + "<h4>A5. Nổ và cảnh báo</h4>" + _table(h, head(*ba('Lõi (m)'), *ba('Rìa (m)'), 'Cảnh báo (s)', 'Có vòng cảnh báo'), t5)
            + "<h4>A6. Đường đạn</h4>" + _table(h, head(*ba('Tốc độ (m/s)'), *ba('Bay hết tầm (s)'), *ba('Tầm (m)'), *ba('Tầm tối thiểu (m)'), *ba('Mục tiêu')), t6)
            + "<h4>A7. Tháp xoay</h4>" + _table(h, head(*ba('Xoay tháp (°/s)'), 'Góc bắn giới hạn'), t7)
            + "<h4>A8. Ngoài đời</h4>" + _table(h, head('Nhịp tối đa (phát/phút)', 'Duy trì (phát/phút)', 'Nguồn', *ba('Tỷ lệ game / ngoài đời')), t8))


# --------------------------------------------------------------------------------------------- B

def _target_seconds(bid, mini):
    """Prompt 26's kill-time target by the chapter the boss is met in (p26_ab): mains 2.5 -> 4 min, minis 60 -> 90 s."""
    try:
        import p26_ab as A
        ch = A.MAINS.get(bid) or A.MINIS.get(bid)
    except Exception:  # noqa: BLE001
        ch = None
    if ch is None:
        return None
    k = (min(12.0, max(1.0, float(ch))) - 1.0) / 11.0
    return 60 + 30 * k if mini else 150 + 90 * k


def section_b(game, h):
    """B: per boss: health, target time, DPS before / after and how it was made up, shots and times to kill the reference
    targets, the splash proxy, escape, against the player's weapon of the same family."""
    c = ctx()
    try:
        import fix_boss_weapons as FB
        before = json.loads(Path(FB.BEFORE).read_text(encoding='utf-8')) if Path(FB.BEFORE).exists() else {}
        after = FB.snapshot(c['cur'])
        makeup = dict(getattr(FB, 'MAKEUP', {}))
        tubes = dict(getattr(FB, 'TUBES', {}))
    except Exception:  # noqa: BLE001
        FB, before, after, makeup, tubes = None, {}, {}, {}, {}
    refs = {v['id']: v for v in game.get('vehicles', [])}
    towers = [t for t in game.get('towers', []) if (t.get('size') or '') == 'Medium' and not (t.get('raw') or {}).get('Boss')]
    tower = sorted(towers, key=lambda t: t['id'])[0] if towers else None
    targets = [(refs[i], label) for i, label in REF_TARGETS if i in refs] + ([(tower, f"Tháp vừa ({tower.get('name', tower['id'])})")] if tower else [])
    player = {}
    for v in game.get('vehicles', []):
        for w in v.get('weapons', []):
            if _family(w):
                player.setdefault(_family(w), (v, w))
    out = ["<h3>B. Tóm tắt từng boss</h3>"
           "<p>Số đòn để hạ: máu ÷ sát thương một phát lên giáp mặt trước (hệ số loại đạn và xuyên của game, cả hệ số sát thương của boss); "
           "dồn hỏa lực: máu ÷ tổng DPS duy trì của mọi bệ lên giáp đó. Nổ lan: 5 xe tham chiếu cách nhau 8 m, theo hàng (−16…16 m) và theo cụm "
           "(một xe giữa, bốn xe cách 8 m), nổ đúng xe giữa. Thoát: thời gian cảnh báo so với thời gian ra khỏi lõi của xe chậm 4,5 m/s đứng ở tâm. "
           "Mục tiêu thời gian hạ: prompt 26 (chủ lực 2,5 phút ở chương 1 tới 4 phút ở chương 12; mini 60 tới 90 giây).</p>"]
    for v in game.get('bosses', []):
        raw = v.get('raw') or {}
        bid = v['id']
        mini = bool(raw.get('MiniBoss'))
        ground = [w for w in v.get('weapons', []) if w.get('targets') != 'Air']
        g_after = sum(float(w.get('dps') or 0) for w in ground)
        b_rows = before.get(bid) or before.get(raw.get('VariantOf') or '') or []
        g_before = sum(r['dps'] for r in b_rows if not r.get('air'))
        paper_after = sum(r['dps'] for r in (after.get(bid) or []) if not r.get('air')) if after else None
        mult = raw.get('OutgoingDamageMult', 1) or 1
        fixes = [f"{_e(wid)}: {_e(why)}" for wid, (_, why) in makeup.items() if any(w['id'] == wid for w in v.get('weapons', []))]
        fixes += [f"{_e(wid)}: {_e(why)}" for wid, (_, why) in tubes.items() if any(w['id'] == wid for w in v.get('weapons', []))]
        if abs(mult - 1) > 1e-3:
            fixes.append(f"hệ số sát thương ra ×{_n(mult, 3)} (chủ dự án: 80–120% DPS mặt đất trước)")
        tgt = _target_seconds(bid, mini)
        out.append(f"<h4>{_e(v['name'])} <span class='muted'>({_e(bid)}, {'mini' if mini else 'chủ lực'})</span></h4>"
                   + _table(h, ['Máu', 'Mục tiêu thời gian hạ', 'DPS mặt đất trước (giấy)', 'DPS mặt đất sau (giấy)', 'DPS trong game', 'Cách bù'],
                            [[_n(v.get('hp'), 0), f"{_n(tgt, 0)} s" if tgt else '—', _n(g_before, 0) if b_rows else '—', _n(paper_after, 0),
                              _n(g_after, 0), '<br>'.join(fixes) or '—']], ''))
        seen = {}
        for w in ground:
            if float(w.get('damage') or 0) > 0:
                seen.setdefault(w['id'], [w, 0])[1] += 1
        rows = []
        for wid, (w, count) in seen.items():
            eff = w.get('effect') or []
            dmg = float(w.get('damage') or 0) * (1 if (_raw(w).get('Laid')) else float(raw.get('WeaponDamage', 1) or 1)) * float(mult)
            cells = [f"<code>{_e(wid)}</code>" + (f" ×{count}" if count > 1 else ''), _e(w.get('name', ''))]
            for t, _ in targets:
                hp = float(t.get('hp') or 0)
                level = int((t.get('armour') or {}).get('front', 0))
                col = (len(eff) - 1) if t is tower else min(level, len(eff) - 3) if eff else 0
                per = dmg * (eff[col] if eff else 1)
                cells.append(str(math.ceil(hp / per)) if per > 0 else '∞')
            core, edge = float(w.get('splash') or 0), float(w.get('splashEdge') or 0)
            line = [abs(x) for x in (-2 * SPACING, -SPACING, 0, SPACING, 2 * SPACING)]
            cluster = [0, SPACING, SPACING, SPACING, SPACING]

            def hit(ds):
                return f"{sum(1 for d in ds if d <= core)} / {sum(1 for d in ds if core < d <= max(core, edge))}" if core > 0 else '—'

            warn = float(w.get('warnSeconds') or 0)
            out_s = core / SLOW_SPEED if core > 0 else 0
            esc = ('ĐỦ' if warn + 1e-6 >= out_s else 'THIẾU') if w.get('warns') else ('không cảnh báo' if core > 0 else '—')
            fam = _family(w)
            pv = player.get(fam)
            cmp_ = (f"{_e(pv[0].get('short') or pv[0]['name'])}: {_n(pv[1].get('damage'), 0)} / phát, lõi {_n(pv[1].get('splash'), 1)} m, "
                    f"chu kỳ {_n(_cycle(pv[1]), 2)} s") if pv else '—'
            rows.append(cells + [hit(line), hit(cluster), esc, cmp_])
        if rows:
            out.append(_table(h, ['Vũ khí', 'Tên'] + [f"Số đòn: {label}" for _, label in targets]
                              + ['Nổ lan hàng (lõi / rìa)', 'Nổ lan cụm (lõi / rìa)', 'Thoát', 'Vũ khí người chơi cùng họ'], rows))
        kills = []
        for t, label in targets:
            level = int((t.get('armour') or {}).get('front', 0))
            total = 0.0
            for w in ground:
                lv = w.get('dpsVsLevel') or []
                if lv:
                    total += float(lv[-1] if t is tower else lv[min(level, len(lv) - 3)])
            kills.append(f"{_e(label)} {_n(float(t.get('hp') or 0) / total, 1)} s" if total > 0 else f"{_e(label)} —")
        out.append(f"<p><b>Dồn toàn bộ hỏa lực:</b> {' · '.join(kills)}.</p>")
    return '\n'.join(out)


# --------------------------------------------------------------------------------------------- C

def _recipes():
    """Per tier (2-5): the redrawn blast's sizes from ExplosionEffect.Tiers.cs (largest fireball, column top, crater glow,
    dust ring, flash, quads emitted), read from the code."""
    if 'recipes' in _CACHE:
        return _CACHE['recipes']
    path = SCRIPTS / 'Game' / 'Effects' / 'ExplosionEffect.Tiers.cs'
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    body = text.split('CreateTier(int tier', 1)[1].split('CreateTierFire', 1)[0] if 'CreateTier(int tier' in text else ''
    cases = re.split(r'\n\s*(case (\d+):|default: // T5)', body)
    out = {}
    num = r'(-?\d+(?:\.\d+)?)f?'
    i = 1
    while i < len(cases):
        label = cases[i]
        tier = int(cases[i + 1]) if cases[i + 1] else 5
        chunk = cases[i + 2] if i + 2 < len(cases) else ''
        i += 3
        fire = [float(m.group(3)) for m in re.finditer(r'Fireball\((\d+), new Vector2\(' + num + ', ' + num + r'\)', chunk)]
        lives = [float(m.group(2)) for m in re.finditer(r'Fireball\(\d+, new Vector2\([^)]*\), new Vector2\(' + num + ', ' + num + r'\)', chunk)]
        cols = [(int(m.group(1)), float(m.group(3)), float(m.group(5))) for m in
                re.finditer(r'Column\((\d+), new Vector2\(' + num + ', ' + num + r'\), new Vector2\([^)]*\), ' + num + ', ' + num + r'\)', chunk)]
        cap = re.search(r'const float cap = ' + num, chunk)
        crater = re.search(r'CraterGlow\(' + num + ', ' + num + r'\)', chunk)
        dust = [float(m.group(1)) for m in re.finditer(r'(?:DustRing|OuterDust)\(' + num, chunk)]
        flash = re.search(r'Flash\(' + num + r'\)', chunk)
        counts = sum(int(m.group(1)) for m in re.finditer(r'\.(?:Fireball|Dust|Dirt|Debris|BurningDebris|Embers|Smoke|Sparks|Column)\((\d+)', chunk))
        counts += sum(int(m.group(2)) for m in re.finditer(r'\.(?:DustRing|OuterDust)\(' + num + r', (\d+)\)', chunk))
        top = max([0.5 + (n - 1) * step + size * (1 + 0.08 * (n - 1)) * 0.5 for n, size, step in cols], default=0)
        if cap:
            top = max(top, float(cap.group(1)))
        out[tier] = {'fireball': max(fire, default=0), 'fireLife': max(lives, default=0), 'columnTop': top,
                     'crater': float(crater.group(1)) if crater else 0, 'craterLife': float(crater.group(2)) if crater else 0,
                     'dust': max(dust, default=0), 'flash': float(flash.group(1)) if flash else 0, 'quads': counts, 'label': label}
    _CACHE['recipes'] = out
    return out


def _fx_index(imgdir):
    p = Path(imgdir) / 'fx' / 'index.json'
    if not p.exists():
        return {}
    try:
        return {j['key']: j for j in json.loads(p.read_text(encoding='utf-8')).get('jobs', [])}
    except (OSError, ValueError, KeyError):
        return {}


def _overlay(tier, core):
    nominal = 2.5 if tier <= 2 else 5 if tier == 3 else 9 if tier == 4 else 14
    return min(1.6, max(0.8, core / nominal)) if core > 0 else 1.0


def _fx_row(label, tier, core, edge, T, R):
    t = T.get(tier) or {}
    r = R.get(tier) or {}
    s = _overlay(tier, core)
    shock = edge if edge > core else core
    crater = max(4.0, (core if core > 0 else 4.0) * (1.5 if tier >= 5 else 1.2)) if tier >= 4 else (r.get('crater', 0) * s if r else 0)
    return [label, f"T{tier}", f"{_n(core, 1)} / {_n(edge, 1)}" if core else '—',
            f"{_n(t.get('flash'), 1)} m · {_n(t.get('flashLife'), 2)} s" if t.get('flash') else '—',
            f"{t.get('puffs', 0)} × {_n(t.get('puffSize'), 1)} m" if t.get('puffs') else '—',
            _n(t.get('dustRing'), 0) if t.get('dustRing') else '—', _n(t.get('water'), 0) if t.get('water') else '—',
            f"{_n(r.get('fireball', 0) * s, 1)} m · {_n(t.get('fireballLife'), 2)} s" if r else (f"— · {_n(t.get('fireballLife'), 2)} s" if t else '—'),
            f"{_n(r.get('columnTop', 0) * s, 0)} m · {_n(t.get('smokeMin'), 0)}–{_n(t.get('smokeMax'), 0)} s" if r else (
                f"— · {_n(t.get('smokeMin'), 1)}–{_n(t.get('smokeMax'), 1)} s" if t else '—'),
            _n(shock, 1) if tier >= 4 and shock else '—',
            f"{_n(crater, 1)} m · {_n(t.get('crater'), 0)} s" if t.get('crater') else '—',
            _n(t.get('shake'), 2) if t.get('shake') else '—', str(r.get('quads', 0)) if r else '—',
            ('đầy đủ ≤ ' + str(t['fullCap'])) if t.get('fullCap', -1) >= 0 else 'đầy đủ']


def section_c(game, h, imgdir):
    """C: the effects table per tier and per weapon of 120 mm and up, the shots at fixed moments (EffectShots.FxBatch)."""
    fx = (game.get('fixDoc') or {}).get('effects') or {}
    T = {t['tier']: t for t in fx.get('tiers') or []}
    R = _recipes()
    index = _fx_index(imgdir)
    head = ['', 'Bậc', 'Lõi / rìa (m)', 'Chớp đầu nòng', 'Khói đầu nòng', 'Vòng bụi khi bắn (m)', 'Sóng nước (m)', 'Cầu lửa (đường kính · thời gian)',
            'Cột khói (cao · tồn tại)', 'Sóng xung kích (m, = rìa)', 'Hố / vết cháy', 'Rung camera', 'Số hạt (overlay)', 'LOD']
    rows = [_fx_row(f"<b>T{t}</b> (mẫu: {_e((index.get(f'tier_T{t}') or {}).get('weapon', '—'))})", t,
                    float((index.get(f'tier_T{t}') or {}).get('core', 0) or 0), float((index.get(f'tier_T{t}') or {}).get('edge', 0) or 0), T, R)
            for t in range(6)]
    big = []
    for wid, (w, owners, mounts) in sorted(game_weapons(game).items()):
        if float(_cal_of(wid, w)) >= 120:
            big.append((wid, w, owners, mounts))
    wrows = [_fx_row(f"<code>{_e(wid)}</code> <span class='muted'>{_n(_cal_of(wid, w), 0)} mm</span>", _tier_of(wid, w),
                     float(w.get('splash') or 0), float(w.get('splashEdge') or 0), T, R) for wid, w, _, _ in big]
    out = ["<h3>C. Hiệu ứng bắn và nổ</h3>"
           "<p>Số theo bậc đọc từ mã (TierFx, EffectLife: khối fixDoc của bản xuất) và công thức nổ (ExplosionEffect.Tiers.cs; T0–T1 không có lớp vẽ lại). "
           "Cỡ lớp vẽ lại = cỡ thiết kế × lõi / lõi danh định của bậc (0,8–1,6). Sóng xung kích vẽ đúng trên rìa (T4) và trên lõi rồi rìa (T5).</p>",
           _table(h, head, rows),
           f"<h4>Vũ khí từ 120 mm ({len(wrows)})</h4>", _table(h, head, wrows)]
    # The shots: every tier, every boss weapon of 203 mm and up, and any other weapon whose folder the lead rendered.
    keys = [f"tier_T{t}" for t in range(6)]
    for wid, w, _, mounts in big:
        boss = any(m[4] == 'bosses' for m in mounts)
        if (boss and float(_cal_of(wid, w)) >= 203) or (Path(imgdir) / 'fx' / wid).exists():
            keys.append(wid)
    out.append("<h4>Ảnh hiệu ứng</h4><p>Nền lưới 1 m (vạch đậm mỗi 5 m), một Tăng chủ lực đứng cạnh làm thước, vòng lõi đỏ và rìa cam vẽ chồng. "
               "Hàng trên: lúc bắn 0 / 0,2 / 1 s; hàng dưới: lúc nổ 0 / 0,5 / 2 / 10 / 30 s; vũ khí nhiều nòng thêm một loạt (chớp từng nòng, mọi điểm rơi) "
               "và lúc loạt đó rơi. Ảnh: <code>MachineBrigade.Editor.EffectShots.FxBatch</code>.</p>")
    for key in keys:
        job = index.get(key) or {}
        cap = (f"{key}: {job.get('weapon', '')} trên {job.get('carrier', '')}" if job else key)
        cells = [_shot(h, imgdir, f"fx/{key}/fire_{m}s.png", f"bắn +{m} s") for m in FIRE_MOMENTS]
        cells += [_shot(h, imgdir, f"fx/{key}/impact_{m}s.png", f"nổ +{m} s") for m in IMPACT_MOMENTS]
        salvo = job.get('barrels', 1) and int(job.get('barrels', 1)) > 1 or (Path(imgdir) / 'fx' / key / 'salvo.png').exists()
        if salvo:
            cells += [_shot(h, imgdir, f"fx/{key}/salvo.png", 'một loạt'), _shot(h, imgdir, f"fx/{key}/salvo_impact.png", 'loạt rơi')]
        out.append(f"<div class='fxblock'><div class='caption'><b>{_e(cap)}</b></div><div class='fxgrid'>"
                   + ''.join(f"<div class='fxcell'>{x}</div>" for x in cells) + "</div></div>")
    return '\n'.join(out)


# --------------------------------------------------------------------------------------------- D

def _credits():
    p = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Audio' / 'CREDITS.md'
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^\| `([^`]+)` \| [^|]* \| ([^|]*) \| ([^|]*) \| ([^|]*) \|', line)
        if m:
            out[m.group(1)] = (m.group(2).strip(), m.group(3).strip(), m.group(4).strip())
    return out


def _loud_moments(path, top=12, gap=1.5, within=6.0):
    """The loudest moments of a sample mix: 400 ms momentary loudness (K-weighted, Tools/sfx/analyze_sfx), peaks within
    `within` dB of the file's maximum, at least `gap` s apart, the loudest `top`. [(seconds, LUFS)]."""
    try:
        sys.path.insert(0, str(ROOT / 'Tools' / 'sfx'))
        import numpy as np
        import analyze_sfx as A
        x, sr = A.load(path)
    except Exception:  # noqa: BLE001 - no numpy / soundfile: the table says so
        return None
    y = A.k_weight(x, sr)
    block, hop = int(0.4 * sr), int(0.1 * sr)
    if len(y) < block:
        return []
    powers = np.array([np.mean(y[i:i + block] ** 2) for i in range(0, len(y) - block + 1, hop)])
    lk = -0.691 + 10 * np.log10(np.maximum(powers, 1e-20))
    peak = float(lk.max())
    order = np.argsort(-lk)
    picked = []
    for i in order:
        if lk[i] < peak - within or len(picked) >= top:
            break
        t = (i * hop + block / 2) / sr
        if all(abs(t - p) >= gap for p, _ in picked):
            picked.append((t, float(lk[i])))
    return sorted(picked)


def section_d(game, h):
    """D (and L10 item 10): the library by group, the mixer, voices and priorities, the per-clip table, the three sample mixes."""
    audio = ROOT / 'Docs' / 'audio'
    metrics = json.loads((audio / 'metrics.json').read_text(encoding='utf-8')) if (audio / 'metrics.json').exists() else {}
    lib_path = ROOT / 'Tools' / 'sfx' / 'library.json'
    lib = json.loads(lib_path.read_text(encoding='utf-8')).get('banks', {}) if lib_path.exists() else {}
    mix = ((game.get('fixDoc') or {}).get('audio')) or {}
    credits = _credits()
    out = ["<h3>D. Âm thanh</h3>"]
    groups = {}
    for bank, b in sorted(lib.items()):
        groups.setdefault(b.get('group', '?'), []).append(f"{bank}" + (f" ({b.get('size')})" if b.get('size') else '') + (' · ghi âm giữ nguyên' if b.get('kept') else ''))
    out.append("<h4>Thư viện theo nhóm (Tools/sfx/library.json)</h4>" + _table(h, ['Nhóm', 'Kho (bậc cỡ)'], [[_e(g), _e(', '.join(v))] for g, v in sorted(groups.items())], ''))
    if mix:
        pr = mix.get('priorities') or {}
        rows = [['Nhóm trộn', _e(' / '.join(mix.get('groups') or []))],
                ['Số kênh hiệu ứng', f"{mix.get('effectVoices')} (cắt theo ưu tiên khi hết)"],
                ['Ưu tiên (cao thắng)', _e(' > '.join(f"{k} {v}" for k, v in sorted(pr.items(), key=lambda kv: -kv[1])))],
                ['Nén (Effects)', f"ngưỡng {_n(mix.get('compressorThreshold'), 2)}, tỷ lệ {_n(mix.get('compressorRatio'), 1)}:1, "
                                  f"tấn công {_n((mix.get('compressorAttack') or 0) * 1000, 0)} ms, nhả {_n((mix.get('compressorRelease') or 0) * 1000, 0)} ms"],
                ['Giới hạn', f"trần {_n(mix.get('limiterCeiling'), 2)} (≈ −1 dBFS)"],
                ['Suy giảm theo khoảng cách', f"({_n(mix.get('refDistance'), 0)} m / khoảng cách)^0,7, độ cao tính {_n(mix.get('heightShare'), 2)}; ngoài màn hình ×{_n(mix.get('offScreenGain'), 2)}"],
                ['Gộp súng nhỏ', f"từ {mix.get('clusterFrom')} phát trong {_n(mix.get('clusterRadius'), 0)} m / {_n(mix.get('clusterWindow'), 2)} s"],
                ['Trần tiếng kim loại', f"{_n(mix.get('metalPerSecond'), 1)}/s, dồn {_n(mix.get('metalBurst'), 0)}, cách ≥ {_n(mix.get('metalMinGap'), 2)} s"],
                ['Tầm nghe thêm theo cỡ', _e(', '.join(f"{s['size']} +{_n(s['carry'], 0)} m" for s in mix.get('sizes') or []))]]
        out.append("<h4>Mixer, kênh, ưu tiên (mã: SoundLibrary, AudioDirector)</h4>" + _table(h, ['', 'Giá trị'], rows, ''))
    sizes = metrics.get('sizes') or []
    if sizes:
        srows = [[_e(s['size']), _e(s.get('name', ''))] + [(_n(s[r][k], 1) if r in s else '—') for r in ('shot', 'blast') for k in ('lufs_mmax', 'sub150', 'tail')]
                 for s in sizes]
        out.append("<h4>Bảng số đo theo cỡ (Docs/audio/metrics.json)</h4>"
                   + _table(h, ['Cỡ', '', 'Bắn: LUFS max', 'Bắn: % dưới 150 Hz', 'Bắn: đuôi (s)', 'Nổ: LUFS max', 'Nổ: % dưới 150 Hz', 'Nổ: đuôi (s)'], srows))
    crow = []
    for rel, m in sorted((metrics.get('clips') or {}).items()):
        bank = rel.rsplit('/', 1)[0]
        b = lib.get(bank.split('/', 1)[1] if bank.startswith('sfx/') else bank, {})
        key = rel if rel in credits else None
        if key:
            src = f"{credits[key][0]} · {credits[key][1][:60]}"
            lic = credits[key][2]
        elif rel.startswith('sfx/'):
            recorded = b.get('kept') or b.get('group') in ('blast', 'blast_air', 'blast_thermo', 'blast_heat') or (b.get('group') in ('shot', 'launch') and b.get('size') not in ('s0',))
            src = 'Sonniss (lớp chính) + sub / đuôi tổng hợp (build_sfx.py)' if recorded else 'tổng hợp (Tools/sfx/build_sfx.py)'
            lic = 'Sonniss GDC (không cần ghi công)' if recorded else 'bản gốc'
        else:
            src, lic = '—', '—'
        crow.append([f"<code>{_e(rel)}</code>", _e(b.get('group', bank)), _e(b.get('size', '—')), _n(m.get('lufs'), 1), _n(m.get('true_peak', m.get('peak')), 1),
                     _n(m.get('sub150'), 1), _n(m.get('tail'), 2), 'CÓ' if m.get('keng') else 'không', _e(src), _e(lic)])
    out.append(f"<h4>Từng clip ({len(crow)})</h4>"
               + _table(h, ['Clip', 'Nhóm', 'Bậc cỡ', 'Độ to (LUFS)', 'Đỉnh (dBTP)', '% năng lượng dưới 150 Hz', 'Đuôi (s)', '"Keng"', 'Nguồn', 'Giấy phép'], crow))
    samples = audio / 'samples'
    mixes = json.loads((samples / 'mixes.json').read_text(encoding='utf-8')) if (samples / 'mixes.json').exists() else {}
    srows = []
    for ogg in sorted(samples.glob('*.ogg')) if samples.exists() else []:
        mm = mixes.get(ogg.stem, {})
        moments = _loud_moments(ogg)
        text = ('không đọc được (thiếu numpy / soundfile)' if moments is None
                else ', '.join(f"{_n(t, 1)} s ({_n(l, 1)} LUFS)" for t, l in moments) or '—')
        srows.append([f"<code>{_e(ogg.relative_to(ROOT).as_posix())}</code>", _n(mm.get('seconds'), 0), _n(mm.get('lufs'), 1), _n(mm.get('lufs_mmax'), 1),
                      f"{mm.get('played', '—')} / {mm.get('events', '—')}", _n(mm.get('max_busy'), 0), _e(text)])
    out.append("<h4>Ba file ghi âm thử và các tiếng lớn</h4><p>Tiếng lớn: độ to tức thời 400 ms (K-weighted), trong 6 dB của đỉnh file, cách nhau ≥ 1,5 s.</p>"
               + _table(h, ['File', 'Dài (s)', 'LUFS', 'LUFS max', 'Phát / sự kiện', 'Kênh bận tối đa', 'Thời điểm tiếng lớn'], srows))
    return '\n'.join(out)


# --------------------------------------------------------------------------------------------- E

def _visual_rows():
    p = ROOT / 'Docs' / 'models' / 'scan' / 'visual_scores.md'
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^\| `([^`]+)`', line)
        if m:
            cells = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(cells) >= 9:
                out[m.group(1)] = {'class': cells[1], 'visual': cells[5], 'reason': cells[6], 'oldnew': cells[7], 'final': cells[8]}
    return out


def _rebuilt():
    p = ROOT / 'Docs' / 'models' / 'scan' / 'visual_scores.md'
    if not p.exists():
        return []
    text = p.read_text(encoding='utf-8')
    part = text.split('## Rebuilt in this pass', 1)[1] if '## Rebuilt in this pass' in text else ''
    return re.findall(r'^\| `([^`]+)` \| ([^|]+) \|', part, re.M)


def section_e(game, h, imgdir):
    """E (and L10 item 11): MODEL_STANDARD, every model's score with its three-angle sheet, the worse-than-old list,
    before / after for the 15 L8 rebuilds, sky_gunship and every structure, tower and HQ."""
    scores = ROOT / 'Docs' / 'models' / 'scan' / 'static_scores.csv'
    static = {}
    if scores.exists():
        with scores.open(encoding='utf-8', newline='') as fh:
            static = {r['model']: r for r in csv.DictReader(fh)}
    vis = _visual_rows()
    check = {}
    fv = ROOT / 'Docs' / 'checks' / 'fix_validate.json'
    if fv.exists():
        try:
            check = json.loads(fv.read_text(encoding='utf-8')).get('models') or {}
        except ValueError:
            check = {}
    grades = check.get('grades') or {}
    std = ROOT / 'Docs' / 'models' / 'MODEL_STANDARD.md'
    budgets = [t for t in _md_tables(std) if t[0].startswith('1.')]
    out = ["<h3>E. Model</h3><p>Tiêu chuẩn: Docs/models/MODEL_STANDARD.md (tam giác LOD0 theo lớp; vượt ngân sách thì giữ, chỉ ghi thông tin; "
           "LOD1 ≈ 50% dựng lúc chạy, LOD2 là impostor; Part_* hoặc nút gộp theo lớp; Muzzle_* mỗi nòng, Mount_* mỗi bệ tự ngắm, ≥ 2 Mount_Flare; "
           "tỷ lệ trong 10% so với bản thật). Điểm: tĩnh (static_scores.csv) và nhìn (visual_scores.md), cuối cùng lấy điểm thấp hơn.</p>"]
    if budgets:
        out.append(_table(h, budgets[0][1], [[_e(x) for x in r] for r in budgets[0][2]], ''))
    s = check.get('summary') or {}
    if s:
        out.append(f"<p><b>Kiểm tra lượt 9 mục 7</b> (Tools/balance/fix_validate.py 7): {s.get('models')} model; vượt ngân sách {s.get('overBudgetInfo')} "
                   f"(thông tin, giữ nguyên); dưới mức sàn {s.get('underBudget')}; thiếu phần ở {s.get('withMissingParts')} model "
                   f"({s.get('missingPartsTotal')}: đổi tên / tách nút {s.get('renamingBacklog')}, làm lại {s.get('rebuildBacklog')}); LOD1 có ở "
                   f"{s.get('scanned')} model đã quét, ngoài 35–65% ở {s.get('lod1OutsideBand')}; lỗi {s.get('failures')}.</p>")
    rows = []
    for model in sorted(set(static) | set(vis)):
        st, vi, gr = static.get(model, {}), vis.get(model, {}), grades.get(model, {})
        rows.append([f"<code>{_e(model)}</code>", _e(st.get('class', vi.get('class', ''))), _n(st.get('triangles'), 0),
                     f"{_n(st.get('budgetMin'), 0)}–{_n(st.get('budgetMax'), 0)}", _e(st.get('budgetStatus', '')),
                     _e(' '.join(gr.get('partsMissing', [])) or st.get('partsMissing', '') or '—'),
                     _e('; '.join(x for x in (st.get('muzzlesMissing'), st.get('mountsMissing')) if x) or '—'),
                     _e(st.get('propFlag') or '—'), _e(st.get('staticGrade', '')), _e(vi.get('visual', '')), _e(vi.get('oldnew', '')), f"<b>{_e(vi.get('final', ''))}</b>"])
    out.append(f"<h4>Bảng chấm mọi model ({len(rows)})</h4>"
               + _table(h, ['Model', 'Lớp', 'Tam giác', 'Ngân sách', 'Trạng thái', 'Part_* thiếu', 'Mount / Muzzle thiếu', 'Sai tỷ lệ', 'Tĩnh', 'Nhìn',
                            'Cũ / mới', 'Cuối'], rows))
    wt = ROOT / 'Docs' / 'models' / 'scan' / 'visual_scores.md'
    if wt.exists():
        text = wt.read_text(encoding='utf-8')
        part = text.split('## Worse than old', 1)[1].split('##', 1)[0] if '## Worse than old' in text else ''
        items = [re.sub(r'\s+', ' ', x).strip() for x in re.split(r'\n- ', part) if x.strip()]
        out.append("<h4>Bản xấu đi đã xử lý</h4><ul>" + ''.join(f"<li>{_e(x.lstrip('- '))}</li>" for x in items) + "</ul>")

    def sheet(m):
        after = Path(imgdir) / 'scan_after' / f"{m}.png"
        return f"scan_after/{m}.png" if after.exists() else f"scan/{m}.png"

    rebuilt = _rebuilt()
    if rebuilt:
        out.append(f"<h4>Trước / sau: {len(rebuilt)} model làm lại ở lượt 8</h4>")
        for m, tri in rebuilt:
            out.append(f"<div class='pair'><div class='caption'><b>{_e(m)}</b> · tam giác {_e(tri.strip())}</div><div class='grid2'>"
                       f"<div>{_shot(h, imgdir, f'scan/{m}.png', 'trước (lượt 8)')}</div><div>{_shot(h, imgdir, f'scan_after/{m}.png', 'sau')}</div></div></div>")
    must = ['sky_gunship'] + sorted(m for m, r in static.items() if r.get('class') in ('tower', 'structure', 'hq', 'obstacle') and not m.endswith(('_a', '_b')))
    out.append(f"<h4>Trước / sau bắt buộc: Pháo hạm bay và công trình ({len(must)})</h4><p>Trước: bản trước prompt 27 (commit {BASE}, "
               "<code>scan/&lt;id&gt;_old.png</code>); sau: model hiện tại. Model mới sau commit đó không có ảnh trước.</p>")
    for m in must:
        out.append(f"<div class='pair'><div class='caption'><b>{_e(m)}</b> · {_e((vis.get(m) or {}).get('oldnew', ''))}</div><div class='grid2'>"
                   f"<div>{_shot(h, imgdir, f'scan/{m}_old.png', 'trước prompt 27')}</div><div>{_shot(h, imgdir, sheet(m), 'hiện tại')}</div></div></div>")
    out.append(f"<h4>Ảnh 3 góc mọi model ({len(rows)})</h4><p>Mỗi tấm: góc chơi (nghiêng 52°), cạnh bên, phía sau; cỡ trong trận (ModelScan).</p><div class='grid2'>")
    for model in sorted(set(static) | set(vis)):
        out.append(f"<div class='fxcell'>{_shot(h, imgdir, sheet(model), model)}<div class='galcap'>{_e(model)} · {_e((vis.get(model) or {}).get('final', ''))}</div></div>")
    out.append('</div>')
    return '\n'.join(out)


# --------------------------------------------------------------------------------------------- text from the code (L10 items 13, 17)

def legend_mission(game):
    """The mission whose win opens the Operations' Legend tier (Operations.LegendMission) and its name."""
    p = SCRIPTS / 'Game' / 'Match' / 'Operations.cs'
    m = re.search(r'LegendMission\s*=\s*"([^"]+)"', p.read_text(encoding='utf-8')) if p.exists() else None
    mid = m.group(1) if m else ''
    name = next((x.get('name', '') for x in game.get('campaign', []) if x.get('id') == mid), '')
    return mid, name


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    g = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')) if len(sys.argv) > 1 else {}
    print(section10_fix(g, None)[:2000])
