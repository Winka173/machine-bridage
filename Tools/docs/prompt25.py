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
