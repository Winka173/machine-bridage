"""The design document's prompt 25 additions (DECISIONS 25E): table 9b's support value (E2) and "vs cluster" (E3)
columns, and F1's new columns and tables: each unit's description, shape and unlock; every weapon's DPS by armour
level 0-5, against aircraft and against structures; missile flight speed and time; model and round sizes; the main
bosses' super weapons. build_doc.py and programme.py call these with the exported game (game.json).

An older export lacks some fields (description, unlock, dpsAir, superWeapon...): every reader falls back on what the
export already had, on balance.json, or on "—".
"""
import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
BALANCE_DIR = ROOT / 'Docs' / 'balance'
sys.path.insert(0, str(ROOT / 'Tools' / 'balance'))
import jsonc_edit  # noqa: E402

DASH = '—'

# The combat-value measure the document shows, newest first: the test phase's run after prompt 25 (MB_CV_TAG=p25_after),
# else the last one before it (play-test 6), else the balance pass after prompt 18 (the one the balance sheet read).
MEASURES = ['p25_after', 'pt6_after', 'p18_after']

_balance = None


def balance():
    """balance.json, parsed once (comments and all)."""
    global _balance
    if _balance is None:
        _balance = jsonc_edit.loads((DATA / 'balance.json').read_text(encoding='utf-8'))
    return _balance


def _resolved(items, key_id):
    """An entry of balance.json's list with its 'inherits' (or a boss variant's 'variantOf') chain laid under it."""
    by_id = {x['id']: x for x in items}
    seen = {}

    def get(i):
        if i in seen:
            return seen[i]
        x = dict(by_id.get(i, {}))
        parent = x.get('inherits') or x.get('variantOf')
        if parent in by_id and parent != i:
            base = dict(get(parent))
            base.update(x)
            x = base
        seen[i] = x
        return x
    return get(key_id) if key_id in by_id else {}


def weapon_data(wid):
    """A weapon as the game reads it: its inherits chain, then its family's shared fields on top (Catalog.WeaponEntries)."""
    w = _resolved(balance().get('weapons', []), wid)
    fam = {x['id']: x for x in balance().get('weaponFamilies', [])}.get(w.get('weaponFamily'))
    if fam:
        w = dict(w)
        w.update({k: x for k, x in fam.items() if k not in ('id', 'real')})
    return w


def vehicle_data(vid):
    return _resolved(balance().get('vehicles', []), vid)


def f(x, n=1):
    """A number as the document writes it: a comma decimal, no trailing zeros; '—' for none."""
    if x in (None, ''):
        return DASH
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not math.isfinite(x):
        return DASH
    t = f"{x:,.{n}f}".replace(',', ' ').replace('.', ',').replace(' ', '.')
    if ',' in t:
        t = t.rstrip('0').rstrip(',')
    return t


# ---------------------------------------------------------------------------------------------------------------- E3

GAP = 4.0          # metres between the cluster's five vehicles (prompt 25 F.3)
EDGE = 0.25        # DamageSystem.EdgeFalloff: a blast's damage at its edge
SPREAD = (0.85, 1.15)   # DamageSystem.ResolveImpact: a blast's reach varies by up to 15 %
CLUSTER = [(0.0, 0.0), (GAP, 0.0), (-GAP, 0.0), (0.0, GAP), (0.0, -GAP)]   # a quincunx: the aim point's vehicle and four round it
SIDE_LEVEL = 0     # the light class's side (ArmourLevels.Vehicle(1)): the face a neighbour turns to a blast beside it


def penetration(table, pen, armour, overmatch=True):
    """DamageTable.Penetration: the multiplier of a round of a penetration against a face of an armour level."""
    steps = table.get('penetration') or [1.2, 1, 0.85, 0.65, 0.4, 0.15, 0.08]
    last = len(steps) - 1
    step = 2 - (pen - armour)
    if not overmatch:
        step = max(1, step)
    if step <= 0:
        return steps[0]
    if step >= last:
        return steps[last]
    low = int(math.floor(step))
    t = step - low
    return steps[low] + (steps[min(last, low + 1)] - steps[low]) * t


def falloff(distance, radius, thermobaric=False, spread=True):
    """DamageSystem.ApplyFalloff at a vehicle's edge this far from the blast, over the blast's random reach."""
    if radius <= 0:
        return 0.0
    edge = (1 + EDGE) * 0.5 if thermobaric else EDGE
    reaches = [radius * (SPREAD[0] + (SPREAD[1] - SPREAD[0]) * k / 30) for k in range(31)] if spread else [radius]
    total = 0.0
    for r in reaches:
        if distance <= r:
            total += 1 - (1 - edge) * min(1.0, distance / r)
    return total / len(reaches)


def _target_radius(game):
    for v in game.get('vehicles', []):
        if v['id'] == 'armored_car':
            return float(v.get('raw', {}).get('Radius', 2.0) or 2.0)
    return 2.0


_bomblets = {}


def _bomblet_share(cluster, radius_t):
    """Mean summed falloff one bomblet of a cluster round lays on the five vehicles (DamageSystem.Scatter), by a
    fixed-seed draw over its scatter: a calculation from the data, not a sim run."""
    key = (cluster.get('radius'), cluster.get('splash'), radius_t)
    if key in _bomblets:
        return _bomblets[key]
    rng = random.Random(25)
    spread, r = float(cluster.get('radius', 4)), float(cluster.get('splash', 2))
    n, total = 4000, 0.0
    for _ in range(n):
        a = rng.random() * math.tau
        reach = spread * math.sqrt(0.15 + 0.85 * rng.random())
        x, y = math.cos(a) * reach, math.sin(a) * reach
        for cx, cy in CLUSTER:
            d = max(0.0, math.hypot(x - cx, y - cy) - radius_t)
            total += falloff(d, r, spread=False)
    _bomblets[key] = total / n
    return _bomblets[key]


def cluster_dps(v, game):
    """E3: a unit's damage a second against five light vehicles 4 m apart (a quincunx), every round aimed at the middle
    one: its direct hit as in table 9 (vs light), and its blast on the four round it with the falloff, the splash's
    penetration (at most 1 on the ground, Armour.SplashPenetration) against their sides and its type's factor on the
    ground; a cluster round's bomblets on all five. Returns (vs the cluster, vs one vehicle)."""
    table = game.get('damageTable', {})
    single = float((v.get('dpsVs') or {}).get('Light', 0) or 0)
    total = single
    radius_t = _target_radius(game)
    for w in v.get('weapons', []):
        if w.get('targets') == 'Air' or not (w.get('damage') or 0) > 0:
            continue
        dps = float(w.get('dps', 0) or 0)
        ground = float((table.get(w.get('type'), {}) or {}).get('Ground', 1) or 0)
        splash = float(w.get('splash', 0) or 0)
        if splash > 0:
            share = sum(falloff(max(0.0, math.hypot(x, y) - radius_t), splash, bool(w.get('thermobaric')))
                        for x, y in CLUSTER[1:])
            total += dps * share * penetration(table, min(float(w.get('pen', 0) or 0), 1), SIDE_LEVEL) * ground
        c = weapon_data(w['id']).get('cluster')
        if c:
            rounds = dps / float(w['damage'])
            per = float(c.get('count', 1)) * float(c.get('damage', 0)) * _bomblet_share(c, radius_t)
            he = float((table.get('HighExplosive', {}) or {}).get('Ground', 1) or 1)
            total += rounds * per * penetration(table, min(float(c.get('pen', 2)), 1), SIDE_LEVEL) * he
    return total, single


def cluster_cell(v, game):
    total, single = cluster_dps(v, game)
    if total <= 0:
        return DASH
    return f"{total:.0f}" + (f" (×{f(total / single, 1)})" if single > 0 and total > single * 1.005 else '')


# ---------------------------------------------------------------------------------------------------------------- E2

SUPPORT_KEYS = ('repair', 'rearm', 'airRearm', 'jammer', 'dome')
SUPPORT_COLUMNS = ('repaired', 'resupplied', 'decoyed', 'shielded', 'support')


def measure_path():
    """The combat-value summary the document reads: the first of MEASURES on disk, else the newest file."""
    for tag in MEASURES:
        p = BALANCE_DIR / f'combat_value_{tag}_summary.tsv'
        if p.exists():
            return p
    runs = sorted(BALANCE_DIR.glob('combat_value_*_summary.tsv'), key=lambda p: p.stat().st_mtime)
    return runs[-1] if runs else None


def read_tsv(path):
    if not path or not Path(path).exists():
        return []
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    if not lines:
        return []
    head = lines[0].split('\t')
    return [dict(zip(head, line.split('\t'))) for line in lines[1:] if line.strip()]


def support_rows(summary_path):
    """E2's measures by vehicle id: the summary's support columns, else the run's own file beside it (same tag)."""
    rows = {}
    for c in read_tsv(summary_path):
        if any(c.get(k) for k in SUPPORT_COLUMNS):
            rows[c['id']] = c
    if summary_path:
        extra = Path(str(summary_path).replace('_summary.tsv', '_support.tsv'))
        for c in read_tsv(extra):
            rows.setdefault(c['id'], c)
            for k, x in c.items():
                rows[c['id']].setdefault(k, x)
    return rows


def supporters(game):
    """Card vehicles with a repair, rearm, jamming or shield aura (CombatValueMeasure.Supporter), by balance.json."""
    out = []
    for v in game.get('vehicles', []):
        d = vehicle_data(v['id'])
        if any(k in d for k in SUPPORT_KEYS):
            out.append((v, d))
    return out


def mechanism(d):
    """A support vehicle's auras in words (balance.json)."""
    bits = []
    if 'repair' in d:
        r = d['repair']
        bits.append(f"sửa {f(r.get('rate', 0) * 100, 1)}% máu/s trong {f(r.get('radius', 0))} m")
    if 'rearm' in d:
        r = d['rearm']
        bits.append(f"nạp đạn trong {f(r.get('radius', 0))} m (1 viên mỗi {f(r.get('rate', 0))} s, nạp tại chỗ nhanh ×3)")
    if 'airRearm' in d:
        r = d['airRearm']
        bits.append(f"trực thăng nạp đạn cạnh xe (trong {f(r.get('radius', 0))} m)")
    if 'jammer' in d:
        bits.append(f"gây nhiễu đạn dẫn đường trong {f(d['jammer'])} m")
    if 'dome' in d:
        r = d['dome']
        bits.append(f"khiên {f(r.get('hp', 0), 0)} máu, bán kính {f(r.get('radius', 0))} m, đầy lại sau {f(r.get('recharge', 0))} s")
    return '; '.join(bits)


def support_table(game, h, summary_path):
    """E2's sub-table of 9b: what each support vehicle does for its side, '—' until the test phase measures it."""
    e, table = h['esc'], h['table']
    measured = support_rows(summary_path)
    rows = []
    for v, d in supporters(game):
        c = measured.get(v['id'], {})

        def cell(k, n=0):
            return f(c.get(k), n) if c.get(k) not in (None, '') else DASH
        share = c.get('decoyShare')
        decoy = cell('decoyed', 1) + (f" ({float(share) * 100:.0f}%)" if share not in (None, '') else '')
        rows.append([f"<b>{e(v['name'])}</b>", str(v['cost']), e(mechanism(d)), cell('repaired'), cell('resupplied'), decoy,
                     cell('shielded'), cell('support')])
    return ("<h3>Giá trị hỗ trợ (E2)</h3><p>Xe hỗ trợ không gây sát thương nên giá trị thực chiến bỏ sót chúng. Phép đo riêng "
            "(<code>CombatValueMeasure.MeasureTheSupportVehicles</code>, và <code>MeasureTheRoster</code> ghi vào cùng bảng tổng hợp): một xe đi cùng "
            "hai tăng chủ lực, một xe bộ binh, một pháo phản lực và một trực thăng tấn công, do AI chiến thuật dẫn, đánh một nhóm bắn tên lửa dẫn đường và "
            "bắn thẳng (hai BMPT, một tăng chủ lực, một trực thăng tấn công; hết đợt này 3 giây có đợt sau) trong 3 phút. Ghi: <b>máu sửa được</b>, "
            "<b>đạn nạp thêm</b> (viên: băng vơi được nạp đầy, phần thời gian nạp tại chỗ được rút ngắn quy ra viên, đạn trực thăng nạp cạnh xe), "
            "<b>tên lửa hút được</b> (đạn dẫn đường của địch bị gây nhiễu lúc phóng, và phần trăm trên mọi đạn dẫn đường địch bắn), <b>sát thương khiên chặn</b>. "
            "Giá trị hỗ trợ / CP = (máu sửa + khiên chặn + sát thương của số đạn nạp thêm và của tên lửa bị hút) × hệ số sống sót / CP, cùng thang với "
            "giá trị thực chiến. Ô \"—\": chưa đo (chờ phase kiểm tra).</p>"
            + table(['Xe', 'CP', 'Cơ chế', 'Máu sửa', 'Đạn nạp thêm (viên)', 'Tên lửa hút (quả)', 'Khiên chặn', 'Giá trị hỗ trợ / CP'], rows, 'dps'))


# ---------------------------------------------------------------------------------------------------------------- F1

def _guide_lines(text):
    """The Guide card's lines under its head ([[Name]] · ...): how it fights, strong / weak, the tip."""
    lines = [re.sub(r'\[\[(.+?)\]\]', r'\1', x).strip() for x in (text or '').split('\n')]
    return [x for x in lines[1:] if x]


def description(v):
    """F1: a unit's description: the export's, else its Guide card's how-it-fights and strong / weak lines."""
    if v.get('description'):
        return v['description']
    lines = _guide_lines(v.get('guide', ''))
    keep = [re.sub(r'^(Cách đánh|Mạnh / yếu|How it fights|Strong / weak):\s*', '', x) for x in lines
            if not re.match(r'^(Mẹo|Tip)\b', x)]
    return ' '.join(keep[:2]) or v.get('note', '')


_shapes = None


def shapes():
    """The balance sheet's "Hình dạng (cho AI vẽ)" by id (Tools/docs/unit_sheet.json, written by unit_sheet.py)."""
    global _shapes
    if _shapes is None:
        p = Path(__file__).resolve().parent / 'unit_sheet.json'
        _shapes = json.loads(p.read_text(encoding='utf-8')).get('units', {}) if p.exists() else {}
    return _shapes


def shape(v):
    return (shapes().get(v['id']) or {}).get('shape', '')


def _roman(n):
    return {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}.get(n, str(n))


def unlock(v, game):
    """F1: how a card is had, from the export's unlock (mission, chapter, early price, story loot), else from its route,
    price and the campaign's unlock lists (matched by name)."""
    raw = v.get('raw', {})
    if raw.get('Boss') or raw.get('Elite'):
        return ''
    u = v.get('unlock')
    route = v.get('route', '')
    if route == 'Starter':
        return 'có sẵn từ đầu'
    if route == 'Premium':
        return f"thẻ cao cấp, {f(v.get('coins', 0), 0)} xu"
    mission, chapter, loot = None, None, False
    if isinstance(u, dict):
        mission, chapter, loot = u.get('mission') or None, u.get('chapter'), bool(u.get('storyLoot'))
        name = u.get('missionName', '')
    else:
        name = ''
        for m in game.get('campaign', []):
            if v['name'] in (m.get('unlocks') or []):
                mission, chapter, name = m['id'], m.get('chapter'), m.get('name', '')
                break
    if not mission:
        return 'nhánh mở ở hạng 7 của tháp' if '.' in v['id'] else 'không mở trong chiến dịch'
    where = (f"Xen kẽ {_roman(int(mission[1]))}" if re.match(r'^i\d', mission) else f"chương {chapter}") + f", nhiệm vụ {mission}"
    if name:
        where += f" ({name})"
    if loot:
        return where + '; chiến lợi phẩm cốt truyện, không bán'
    coins = (u or {}).get('price', v.get('coins', 0)) if isinstance(u, dict) else v.get('coins', 0)
    return where + (f"; mua sớm {f(coins, 0)} xu" if coins else '')


def unit_sheet_rows(game, h, groups=('vehicles', 'towers', 'bosses')):
    """F1: one row a unit: its description, its shape note (the sheet's drawing brief) and its unlock."""
    e, table = h['esc'], h['table']
    out = []
    label = {'vehicles': 'Phương tiện', 'towers': 'Tháp và công sự', 'bosses': 'Boss'}
    for g in groups:
        rows = []
        for v in game.get(g, []):
            rows.append([f"<b>{e(v['name'])}</b><br><code>{e(v['id'])}</code>", e(description(v)), e(shape(v) or DASH),
                         e(unlock(v, game) or DASH)])
        if rows:
            out.append(f"<h3>{label[g]} ({len(rows)})</h3>" + table(['Đơn vị', 'Miêu tả', 'Hình dạng (bản vẽ)', 'Mở khóa'], rows))
    return ("<div class='section'><h2>8b. Miêu tả, hình dạng và mở khóa</h2><p>Miêu tả: dòng Cách đánh và Mạnh / yếu của thẻ Hướng dẫn trong game. "
            "Hình dạng: cột \"Hình dạng (cho AI vẽ)\" của file cân bằng (sheet Phương tiện, Công trình, Boss), bản mô tả để dựng model "
            "(Tools/docs/unit_sheet.json). Mở khóa: theo dữ liệu chiến dịch sau prompt 25 D2 (màn mở, giá mua sớm, chiến lợi phẩm cốt truyện).</p>"
            + ''.join(out) + "</div>")


LEVELS = 6   # armour levels 0-5 (5: a boss's plate)


def weapon_owners(game):
    weapons, owners = {}, {}
    for group in ('vehicles', 'itemVehicles', 'elites', 'bosses', 'towers'):
        for v in game.get(group, []):
            for w in v.get('weapons', []):
                weapons.setdefault(w['id'], w)
                owners.setdefault(w['id'], []).append(v.get('short') or v['name'])
    return weapons, owners


def _bonus(w, armor):
    m = 1.0
    for b in w.get('bonuses', []) or []:
        if b.get('armor') == armor and not b.get('class') and not (b.get('still') or 0) > 0 and not b.get('flank'):
            m *= float(b.get('mult', 1) or 1)
    return m


def dps_by_level(w):
    """A weapon's sustained DPS against armour levels 0-5, aircraft and structures (its effect row, Matchup.EffectRow,
    times its sustained DPS; against aircraft its air DPS, FirePower.SustainedAir; an armour-class bonus counts in)."""
    if w.get('dpsVsLevel'):
        return [float(x or 0) for x in w['dpsVsLevel']]   # the export's (ExportGameDoc.DpsByLevel)
    row = w.get('effect') or []
    dps = float(w.get('dps', 0) or 0)
    air = float(w.get('dpsAir', dps) or 0)
    out = []
    for i in range(LEVELS):
        k = row[i] if i < len(row) else 0
        out.append(dps * k * _bonus(w, 'Heavy' if i >= 3 else 'Light'))
    out.append(air * (row[LEVELS] if len(row) > LEVELS else 0) * _bonus(w, 'Air'))
    out.append(dps * (row[LEVELS + 1] if len(row) > LEVELS + 1 else 0) * _bonus(w, 'Structure'))
    return out


def dps_table(game, h):
    """F1: every weapon's DPS by armour level 0-5, against aircraft and against structures."""
    e, table = h['esc'], h['table']
    weapons, owners = weapon_owners(game)
    rows = []
    for wid in sorted(weapons):
        w = weapons[wid]
        if not (w.get('damage') or 0) > 0:
            continue
        cells = dps_by_level(w)
        rows.append([f"<code>{e(wid)}</code>", e(w.get('real') or w.get('name') or ''), e(', '.join(sorted(set(owners[wid])))[:60]),
                     str(w.get('pen', '')), f"{float(w.get('dps', 0) or 0):.0f}"] + [f"{x:.0f}" if x > 0.05 else DASH for x in cells])
    return (f"<h3>DPS theo cấp giáp ({len(rows)} vũ khí)</h3><p>DPS duy trì (prompt 13: cả loạt, băng, thay băng, nạp bệ) nhân hệ số của vũ khí lên "
            "từng cấp giáp 0–5 (5 là giáp boss), lên máy bay và lên công trình (loại sát thương × bước xuyên, bảng hiệu quả ✓ ~ ✕ của thẻ xe; đạn đánh nóc "
            "tính vào nóc). Mặt trúng là mặt trước ở cấp đó. Thưởng theo lớp giáp (ví dụ phá công sự) tính luôn; thưởng theo loại xe, đứng yên hay đánh sườn "
            "ghi ở thẻ xe.</p>"
            + table(['Vũ khí', 'Tên', 'Trên', 'Xuyên', 'DPS duy trì'] + [f'Giáp {i}' for i in range(LEVELS)] + ['Trên không', 'Công trình'], rows, 'dps'))


MISSILE_FORMS = {'Atgm', 'Sam', 'Cruise', 'Ballistic', 'Fpv', 'Shahed', 'Lancet'}


def missile_table(game, h):
    """F1: every missile's (and guided drone's) flight speed and flight time to its longest reach."""
    e, table = h['esc'], h['table']
    weapons, owners = weapon_owners(game)
    fastest = max((float(v.get('speed', 0) or 0) for g in ('vehicles', 'bosses') for v in game.get(g, []) if v.get('flying')), default=0)
    rows = []
    for wid in sorted(weapons):
        w = weapons[wid]
        raw = w.get('raw', {})
        if w.get('projectile') not in ('Missile', 'Drone') and w.get('form') not in MISSILE_FORMS:
            continue
        speed = float(w.get('speed') or raw.get('ProjectileSpeed', 0) or 0)
        rng = float(w.get('range', 0) or 0)
        flight = w.get('flightTime') or (rng / speed if speed else 0)
        aa = w.get('targets') in ('Air', 'All')
        rows.append([f"<code>{e(wid)}</code>", e(w.get('real') or ''), e(', '.join(sorted(set(owners[wid])))[:60]),
                     e(str(w.get('form', ''))), f(speed, 0), f(rng, 0), f(flight, 2),
                     f(speed / fastest, 2) if aa and fastest else DASH, f(raw.get('FlareResist', 0), 2) if raw.get('FlareResist') else DASH])
    return (f"<h3>Tên lửa: tốc độ bay và thời gian bay ({len(rows)})</h3><p>Tốc độ bay (m/s) và thời gian bay tới tầm xa nhất (tầm / tốc độ; tên lửa "
            "dẫn đường bay một thời gian định lúc phóng và trúng nơi mục tiêu đang đứng khi tới). Cột nhanh hơn: tốc độ tên lửa phòng không so với máy bay "
            f"nhanh nhất trong game ({f(fastest, 0)} m/s; file cân bằng nhắm 1,2–1,5 lần mục tiêu nhanh nhất cần bắt).</p>"
            + table(['Vũ khí', 'Tên thật', 'Trên', 'Dạng', 'Tốc độ bay (m/s)', 'Tầm (m)', 'Bay hết tầm (s)', 'Nhanh hơn máy bay (lần)', 'Kháng pháo sáng'],
                    rows, 'dps'))


def model_size(v):
    """F1: a unit's model size from the data (modelSize: length x width x height, m), '—' when the data gives none."""
    s = v.get('modelSize')
    if not s:
        raw = v.get('raw', {})
        s = [raw.get('ModelLength', 0), raw.get('ModelWidth', 0), raw.get('ModelHeight', 0)]
    if not s or not (s[0] or 0) > 0:
        s = vehicle_data(v['id']).get('modelSize')   # an export from before prompt 25 B1: balance.json's
    if not s or not (s[0] or 0) > 0:
        return DASH
    return ' × '.join(f(x, 2) for x in s)


def round_length(w):
    x = w.get('roundLength')
    if x is None:
        x = w.get('raw', {}).get('RoundLength')
    if x is None:
        x = weapon_data(w['id']).get('roundLength', 0)   # an export from before prompt 25 B3: balance.json's
    return f(x, 2) if (x or 0) > 0 else DASH


def sizes_table(game, h):
    """F1: every unit's model size (data) and every weapon's round length (data)."""
    e, table = h['esc'], h['table']
    rows = []
    for g, label in (('vehicles', 'xe'), ('itemVehicles', 'vật phẩm'), ('elites', 'tinh nhuệ'), ('bosses', 'boss'), ('towers', 'tháp')):
        for v in game.get(g, []):
            ms = model_size(v)
            if ms == DASH:
                continue
            raw = v.get('raw', {})
            rows.append([e(v['name']), label, ms, f(raw.get('Length', 0), 2), f(raw.get('Width', 0), 2)])
    weapons, owners = weapon_owners(game)
    rrows = []
    for wid in sorted(weapons):
        w = weapons[wid]
        rl = round_length(w)
        if rl == DASH:
            continue
        rrows.append([f"<code>{e(wid)}</code>", e(w.get('real') or ''), e(str(w.get('raw', {}).get('ProjectileModel', '') or '')), rl,
                      e(', '.join(sorted(set(owners[wid])))[:60])])
    return (f"<h3>Kích thước model theo dữ liệu ({len(rows)} đơn vị)</h3><p>modelSize (prompt 25 B1): hộp của model kể cả nòng, dài × rộng × cao (m), "
            "theo sheet Kiểm tra từng mục (mặt đất 0,8 × thật, trên không 0,4 × thật); game vẽ model khớp chiều dài này. Thân va chạm: dài và rộng.</p>"
            + table(['Đơn vị', 'Loại', 'Model: dài × rộng × cao (m)', 'Thân: dài (m)', 'Thân: rộng (m)'], rows, 'dps')
            + f"<h3>Kích thước đạn theo dữ liệu ({len(rrows)} vũ khí)</h3><p>roundLength (prompt 25 B3): chiều dài đạn vẽ (m): 0,8 × thật khi phóng từ mặt "
            "đất, 0,5 × thật từ máy bay, tối thiểu 0,8 m; đạn 203 mm bằng 1,3 lần 155 mm. Game vẽ model đạn khớp chiều dài này.</p>"
            + table(['Vũ khí', 'Tên thật', 'Model đạn', 'Dài đạn (m)', 'Trên'], rrows, 'dps'))


_attack_words = None


def attack_words():
    """The super weapons' Vietnamese words from the Hud text tables (for an export that predates 'superWeapon')."""
    global _attack_words
    if _attack_words is None:
        _attack_words = {}
        for p in sorted((ROOT / 'Assets' / 'MachineBrigade' / 'Scripts' / 'Game' / 'Hud').glob('*Text*.cs')):
            for key, en, vi in re.findall(r'\["([^"]+)"\]\s*=\s*\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)', p.read_text(encoding='utf-8')):
                if 'bigattack.' in key:
                    _attack_words.setdefault(key, vi.replace('\\"', '"'))
    return _attack_words


SHAPE_VI = {'circle': 'loạt nổ', 'strip': 'dải bom', 'line': 'đường thẳng', 'sweep': 'quét', 'swarm': 'bầy drone', 'missile': 'tên lửa',
            'drop': 'thả quân', 'buff': 'tăng lực', 'quake': 'động đất', 'rods': 'thanh tungsten từ vệ tinh', 'arc': 'quét hình quạt'}


def strike_words(s):
    """One strike of a big attack in words (balance.json bigAttacks)."""
    shape = str(s.get('shape', '')).lower()
    parts = s.get('parts') or []
    count = s.get('count') or (s.get('perPart', 1) * max(1, len(parts)))
    bits = [SHAPE_VI.get(shape, shape)]
    if shape == 'drop':
        bits.append(f"{s.get('max') or count} xe")
        if s.get('damage'):
            bits.append(f"{count} × {f(s['damage'], 0)}")
    elif shape == 'arc':
        bits.append(f"{f(s.get('width', 0), 0)}° × {f(s.get('radius', 0))} m, {f(s.get('damage', 0), 0)}")
    elif s.get('damage'):
        bits.append(f"{count} × {f(s['damage'], 0)}")
    if shape not in ('arc',) and s.get('radius'):
        bits.append(f"nổ {f(s['radius'])} m")
    if s.get('length'):
        bits.append(f"dải {f(s['length'])} × {f(s.get('width', 0))} m")
    elif s.get('area'):
        bits.append(f"trong vòng {f(s['area'])} m")
    if s.get('hp'):
        bits.append(f"{f(s['hp'], 0)} máu, bắn hạ được")
    return ', '.join(b for b in bits if b)


def super_table(game, h):
    """F1: the main bosses' super weapons (prompt 25 C1): name, what it does, cycle, warning and how to stop it."""
    e, table = h['esc'], h['table']
    data = balance()
    attacks = {a['id']: a for a in data.get('bigAttacks', [])}
    words = attack_words()
    rows = []
    for v in game.get('bosses', []):
        raw = v.get('raw', {})
        sw = v.get('superWeapon') or {}
        aid = sw.get('id') or vehicle_data(v['id']).get('bigAttack')
        if not aid or raw.get('MiniBoss'):
            continue
        a = attacks.get(aid, {})
        strikes = [strike_words(s) for s in a.get('strikes', [])]
        lt = a.get('late') if isinstance(a.get('late'), dict) else None
        late = f"; từ pha {lt.get('phase', 0) + 1}: {lt.get('count', '')} phát, hồi {f(lt.get('cooldown'))} s" if lt else ''
        name = sw.get('name') or words.get('bigattack.' + aid, aid)
        how = sw.get('how') or words.get(f'guide.bigattack.{aid}.how', '')
        stop = sw.get('stop') or words.get(f'guide.bigattack.{aid}.stop', '')
        dodge = sw.get('dodge') or words.get(f'guide.bigattack.{aid}.dodge', '')
        rows.append([f"<b>{e(v['name'])}</b>", f"<b>{e(name)}</b><br><span class='muted'>{e(how)}</span>", e('; '.join(strikes)) + e(late),
                     f"{f(a.get('cooldown', sw.get('cooldown')))} s", f"{f(a.get('warn', sw.get('warn')))} s", e(dodge), e(stop)])
    return (f"<h3>Siêu vũ khí của boss chủ lực ({len(rows)})</h3><p>Prompt 25 C1: chỉ {len(rows)} boss chủ lực có siêu vũ khí (đòn lớn của prompt 18 với số của "
            "file cân bằng); mini boss không có. Mỗi siêu vũ khí có âm cảnh báo riêng. Số ở đây là số gốc; trong trận cộng hệ số của cấp boss chủ lực "
            "(sát thương ×1,2, hồi ×0,85) và của độ khó.</p>"
            + table(['Boss', 'Siêu vũ khí', 'Gồm', 'Hồi', 'Cảnh báo', 'Cách né', 'Cách ngắt'], rows))


def f1_section(game, h):
    """F1's weapon and size tables, one section (10e) after the weapons."""
    return ("<div class='section'><h2>10e. DPS theo cấp giáp, tên lửa, kích thước và siêu vũ khí (prompt 25)</h2>"
            + dps_table(game, h) + missile_table(game, h) + sizes_table(game, h) + super_table(game, h) + "</div>")
