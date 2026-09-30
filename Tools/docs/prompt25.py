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
    steps = table.get('penetration') or [1.2, 1, 0.85, 0.5, 0.25, 0.1]
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
