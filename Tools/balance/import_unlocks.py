"""Prompt 25 D2 and E.3: the unlock route, the early-buy prices and the story loot of the balance spreadsheet.

    python Tools/balance/import_unlocks.py snapshot   # once, before anything changes: the economy as it was
    python Tools/balance/import_unlocks.py            # apply, rebuild the campaign, check it, write the report

Reads Docs/balance/Machine_Brigade_Can_bang.xlsx (openpyxl, computed values):

- sheet "Phương tiện", columns "Mở khóa đề xuất" (where a vehicle card opens: "Có sẵn", "Chương N", "Xen kẽ I", story
  loot) and "Mua sớm" (the coins that open it before its mission is won; "Không mua sớm được" for story loot). It writes
  Tools/campaign/unlocks_sheet.json (the campaign scripts read it: Tools/campaign/act11.py moves the cards) and the block
  between "<unlock-sheet>" and "</unlock-sheet>" in Assets/MachineBrigade/Scripts/Game/Match/Progression.cs (the starter
  vehicles, the early-buy prices, the story loot and the cards a new player no longer starts with). Then it rebuilds
  campaign.json (build_campaign.py --no-texts: CampaignText.cs is hand-localised and stays as it is).
- sheets "Đề xuất thêm", "Công trình mới", "Tên lửa & bom mới", "Thẻ hỗ trợ mới" (and "Boss mới"), column "Mở khóa đề
  xuất": none of those items exists yet, so each one's planned shop price and source goes into the notes of
  Docs/backlog/new_content.json (through Tools/balance/new_content_tracker.py; the statuses are not touched).
- sheet "Cốt truyện" (E.3): each chapter's battlefields, bosses, story loot and the commanders it opens, against
  campaign.json, Commanders.cs and the story loot (Narrative.Data.cs).

The economy (prompts 7 and 20) is computed from data, not simulated: the coins a campaign-only player earns in each
chapter against the early-buy prices of the cards the chapter opens, before (the snapshot) and after. Everything goes to
Docs/balance/apply-report.md between "<!-- import_d2:begin -->" and "<!-- import_d2:end -->". A second run changes nothing.
"""

import json
import os
import re
import subprocess
import sys
import unicodedata

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)

from jsonc_edit import loads  # noqa: E402
import new_content_tracker as tracker  # noqa: E402

XLSX = os.path.join(ROOT, 'Docs', 'balance', 'Machine_Brigade_Can_bang.xlsx')
DATA = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Resources', 'Data')
SCRIPTS = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Scripts')
HUD = os.path.join(SCRIPTS, 'Game', 'Hud')
PROGRESSION = os.path.join(SCRIPTS, 'Game', 'Match', 'Progression.cs')
NARRATIVE_DATA = os.path.join(SCRIPTS, 'Game', 'Match', 'Narrative.Data.cs')
COMMANDERS = os.path.join(SCRIPTS, 'Sim', 'Content', 'Commanders.cs')
SHEET_JSON = os.path.join(ROOT, 'Tools', 'campaign', 'unlocks_sheet.json')
TEST_DATA = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Tests', 'EditMode', 'UnlockSheetData.cs')
BUILD = os.path.join(ROOT, 'Tools', 'campaign', 'build_campaign.py')
REPORT = os.path.join(ROOT, 'Docs', 'balance', 'apply-report.md')
BEFORE = os.path.join(ROOT, 'Docs', 'balance', 'economy_d2_before.json')
AFTER = os.path.join(ROOT, 'Docs', 'balance', 'economy_d2_after.json')
BEGIN, END = '<!-- import_d2:begin -->', '<!-- import_d2:end -->'
BLOCK_BEGIN, BLOCK_END = '// <unlock-sheet>', '// </unlock-sheet>'

ROMAN = {'I': 1, 'II': 2, 'III': 3}
INTERLUDE = 12  # interlude N is chapter 12 + N (campaign.json)
STARS = 2  # the economy's player wins each mission once with two stars (build_campaign.simulate)


def fail(msg):
    raise SystemExit('import_unlocks: ' + msg)


def norm(s):
    return unicodedata.normalize('NFC', str(s or '')).strip()


def rows_of(wb, name):
    rows = list(wb[name].iter_rows(values_only=True))
    head = [norm(h) for h in rows[0]]
    return [dict(zip(head, r)) for r in rows[1:] if any(c is not None for c in r)]


def coins(text):
    """ "1.500 xu" -> 1500 (the sheet writes thousands with a dot)."""
    m = re.search(r'(\d{1,3}(?:\.\d{3})*|\d+)\s*xu', norm(text))
    return int(m.group(1).replace('.', '')) if m else None


def fmt(n):
    return f'{n:,}'


# ------------------------------------------------------------------------------------------ the game's data

def campaign():
    text = open(os.path.join(DATA, 'campaign.json'), encoding='utf-8').read()
    return json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))


def balance():
    return loads(open(os.path.join(DATA, 'balance.json'), encoding='utf-8').read())


def cp_table():
    """Every vehicle's and support's CP (a vehicle that inherits reads its base's)."""
    b = balance()
    vehicles = {v['id']: v for v in b['vehicles']}

    def cp(v):
        while 'cp' not in v and v.get('inherits') in vehicles:
            v = vehicles[v['inherits']]
        return v.get('cp', 5)
    table = {vid: cp(v) for vid, v in vehicles.items()}
    table.update({s['id']: s.get('cp', 5) for s in b['supports']})
    return table, vehicles


def cs_list(text, name):
    m = re.search(name + r'\s*=\s*\{([^}]*)\}', text)
    return re.findall(r'"([a-z0-9_.]+)"', m.group(1)) if m else []


def cs_prices(text, name):
    m = re.search(name + r'\s*=\s*new\(\)\s*\{(.*?)\};', text, flags=re.S)
    return {k: int(v) for k, v in re.findall(r'\["([a-z0-9_.]+)"\]\s*=\s*(\d+)', m.group(1))} if m else {}


def shop_rules():
    """What Progression.cs sells as it stands: the starters, the premium prices, the early-buy table (none before D2)."""
    text = open(PROGRESSION, encoding='utf-8').read()
    return {
        'starters': cs_list(text, 'StarterVehicles') + cs_list(text, 'StarterSupports') + cs_list(text, 'StarterTowers'),
        'premium': cs_prices(text, 'PremiumPrices'),
        'early': cs_prices(text, 'EarlyPrices'),
        'items': set(cs_prices(text, 'ItemPrices')),
    }


def story_loot():
    text = open(NARRATIVE_DATA, encoding='utf-8').read()
    m = re.search(r'Loot\s*=\s*\{(.*?)\};', text, flags=re.S)
    return dict(re.findall(r'\("([a-z0-9_]+)", "([a-z0-9]+)"\)', m.group(1)))


def texts():
    """Every hand-localised text (key -> (en, vi)) of the Hud tables."""
    table = {}
    line = re.compile(r'\["([^"]+)"\]\s*=\s*\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)')
    for name in os.listdir(HUD):
        if name.endswith('.cs'):
            for key, en, vi in line.findall(open(os.path.join(HUD, name), encoding='utf-8').read()):
                table.setdefault(key, (en, vi))
    names = open(os.path.join(HUD, 'NameText.Commanders.cs'), encoding='utf-8').read()
    for key, name in re.findall(r'\("(name\.[a-z_]+)", "([^"]+)"\)', names):
        table.setdefault(key, (name, name))
    return table


def resolve(text, table):
    """ "{@foundry}" -> "Foundry"."""
    return re.sub(r'\{@([a-z_]+)\}', lambda m: table.get('name.' + m.group(1), (m.group(1),))[0], text)


# ------------------------------------------------------------------------------------------ the sheet "Phương tiện"

def chapter_of(text):
    """Where the sheet opens a card: 0 a starter, N a chapter, 12 + N interlude N, None no card."""
    t = norm(text)
    if t.startswith('Có sẵn'):
        return 0
    m = re.search(r'Xen kẽ (III|II|I)\b', t)
    if m:
        return INTERLUDE + ROMAN[m.group(1)]
    m = re.search(r'[Cc]hương (\d+)', t)
    if m:
        return int(m.group(1))
    return None


def read_vehicles(wb):
    cards = []
    for r in rows_of(wb, 'Phương tiện'):
        vid = norm(r['id'])
        proposal, early = norm(r['Mở khóa đề xuất']), norm(r['Mua sớm'])
        chapter = chapter_of(proposal)
        loot = 'chiến lợi phẩm' in proposal.lower() or 'không mua sớm' in early.lower()
        cards.append({'id': vid, 'name': norm(r['Tên']), 'now': norm(r['Mở khóa hiện tại']), 'proposal': proposal,
                      'earlyText': early, 'chapter': chapter, 'loot': loot, 'early': None if loot else coins(early),
                      'cp': r['CP']})
    return cards


def sheet_plan(cards, card_ids):
    starters, chapters, early, loot, not_cards = [], {}, {}, [], {}
    for c in cards:
        if c['chapter'] is None:
            not_cards[c['id']] = c['proposal']
            continue
        if c['id'] not in card_ids:
            fail(f"{c['id']}: the sheet opens it, and it is no card")
        if c['chapter'] == 0:
            starters.append(c['id'])
            continue
        chapters[c['id']] = c['chapter']
        if c['loot']:
            loot.append(c['id'])
        elif c['early'] is None:
            fail(f"{c['id']}: opens in chapter {c['chapter']} with no early price")
        else:
            early[c['id']] = c['early']
    return {'starters': starters, 'chapters': chapters, 'early': early, 'loot': loot, 'notCards': not_cards}


def write_sheet_json(plan):
    data = {'_about': 'Generated by Tools/balance/import_unlocks.py from the sheet "Phương tiện" of '
                      'Docs/balance/Machine_Brigade_Can_bang.xlsx (prompt 25 D2): edit the sheet and run the script. '
                      'chapters: 1-12, 13-15 the interludes. Read by Tools/campaign/act11.py.', **plan}
    open(SHEET_JSON, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def write_test_data(cards):
    """The sheet's route for Prompt25UnlockTests (the tests cannot read the workbook)."""
    lines = ['// Generated by Tools/balance/import_unlocks.py from the sheet "Phương tiện" of Docs/balance/Machine_Brigade_Can_bang.xlsx.',
             '// Edit the sheet or the script, not this file.',
             'namespace MachineBrigade.Tests', '{',
             '    /// <summary>Prompt 25 D2: where the balance spreadsheet opens each vehicle card (Prompt25UnlockTests).</summary>',
             '    internal static class UnlockSheetData', '    {',
             '        /// <summary>Each card: the chapter that opens it (0 a starter; 13-15 the interludes), its early price (0: none), story loot.</summary>',
             '        internal static readonly (string id, int chapter, int early, bool loot)[] Cards =', '        {']
    for c in cards:
        if c['chapter'] is not None:
            lines.append(f'            ("{c["id"]}", {c["chapter"]}, {c["early"] or 0}, {"true" if c["loot"] else "false"}),')
    lines += ['        };', '', '        /// <summary>Rows of the sheet that are no card (a boss escort, a mission unit).</summary>',
              '        internal static readonly string[] NotCards = { ' + ', '.join(f'"{c["id"]}"' for c in cards if c['chapter'] is None) + ' };',
              '    }', '}', '']
    open(TEST_DATA, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))


def cs_array(ids):
    return '{ ' + ', '.join(f'"{i}"' for i in ids) + ' }'


def write_progression(plan, former):
    raw = open(PROGRESSION, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    text = raw.replace('\r\n', '\n')
    a, b = text.find(BLOCK_BEGIN), text.find(BLOCK_END)
    if a < 0 or b < 0:
        fail('Progression.cs has no <unlock-sheet> block')
    ind = ' ' * 8
    prices = [f'{ind}    ["{k}"] = {v},' for k, v in sorted(plan['early'].items(), key=lambda kv: (plan['chapters'][kv[0]], kv[1], kv[0]))]
    block = [
        BLOCK_BEGIN + ' Generated by Tools/balance/import_unlocks.py from the sheet "Phương tiện" (prompt 25 D2).',
        f'{ind}public static readonly string[] StarterVehicles = {cs_array(plan["starters"])};',
        '',
        f'{ind}/// <summary>The cards a new player no longer starts with (prompt 25 D2); a save from before keeps them (roster version 6).</summary>',
        f'{ind}public static readonly string[] FormerStarters = {cs_array(former)};',
        '',
        f'{ind}/// <summary>The sheet\'s story loot: won with its story beat, never sold (<see cref="CanBuyEarly"/>).</summary>',
        f'{ind}public static readonly string[] SheetLoot = {cs_array(plan["loot"])};',
        '',
        f'{ind}/// <summary>The sheet\'s "Mua sớm": coins that open a campaign vehicle before its mission is won.</summary>',
        f'{ind}private static readonly Dictionary<string, int> EarlyPrices = new()',
        f'{ind}{{',
        *prices,
        f'{ind}}};',
        f'{ind}',
    ]
    new = (text[:a] + '\n'.join(block) + text[b:]).replace('\n', nl)
    if new != raw:
        open(PROGRESSION, 'w', encoding='utf-8', newline='').write(new)


# ------------------------------------------------------------------------------------------ the new content's shop plan

SOURCES = [
    ('hoặc thưởng nhiệm vụ phụ', 'or a side-mission reward'),
    ('hoặc thưởng sự kiện', 'or an event reward'),
    ('hoặc thưởng thẻ mùa', 'or a season-pass reward'),
    ('hoặc thưởng chương', 'or a chapter reward'),
    ('hoặc rơi từ hòm', 'or a crate drop'),
]


def shop_note(unlock, slot=None, cp=None):
    """The planned shop price and source of one new item, in English."""
    u = norm(unlock)
    if u.startswith('Theo mùa'):
        return ('25D2 plan: not sold in the shop. A main boss is its season\'s boss, a mini boss a weekly event '
                '("Ra mắt đề xuất").')
    prices = [(int(p.replace('.', '')), cond) for p, cond in re.findall(r'(\d{1,3}(?:\.\d{3})*)\s*xu(?:\s*\(([^)]*)\))?', u)]
    if not prices:
        fail(f'no price in "{u}"')
    price, why = prices[0][0], ''
    if len(prices) > 1:
        s = norm(slot).lower()
        if cp is not None:  # "1.500 xu (CP ≤ 5) / 2.500 xu (CP ≥ 6)"
            price, why = (prices[0][0], f'{cp} CP, so the CP 5 or less price') if cp <= 5 else (prices[1][0], f'{cp} CP, so the CP 6 or more price')
        elif 'nhỏ' in s:
            price, why = prices[0][0], 'a small slot'
        elif s:
            price, why = prices[1][0], 'a medium slot' if 'vừa' in s else 'a utility slot'
    kind = 'as equipment for the units that fire it' if 'đồ trang bị' in u else ''
    extra = [en for vi, en in SOURCES if vi in u]
    parts = [f'{fmt(price)} coins in the shop' + (f' ({why})' if why else '') + (f', {kind}' if kind else '')]
    return '25D2 plan: ' + ', '.join(parts + extra) + '.'


def new_content_notes(wb):
    by_name = {}
    for sheet, name_col, slot_col, cp_col in [('Đề xuất thêm', 'Tên đề xuất', 'Ô / CP', None), ('Công trình mới', 'Tên', 'Ô', None),
                                              ('Tên lửa & bom mới', 'Tên', None, None), ('Thẻ hỗ trợ mới', 'Thẻ', None, 'CP'),
                                              ('Boss mới', 'Tên · dòng phụ', None, None)]:
        col = 'Ra mắt đề xuất' if sheet == 'Boss mới' else 'Mở khóa đề xuất'
        for r in rows_of(wb, sheet):
            name = norm(r.get(name_col))
            if not name:
                continue
            slot = norm(r.get(slot_col)) if slot_col else None
            if slot and 'CP' in slot:  # "5 CP": a vehicle, one price
                slot = None
            if sheet == 'Công trình mới' and slot:
                slot = 'Ô ' + slot.lower()
            note = shop_note(r[col], slot, r.get(cp_col) if cp_col else None)
            by_name.setdefault(name.lower(), []).append((sheet, note))
    items = tracker.load().get('items', [])
    notes, clash = {}, []
    for i in items:
        found = by_name.get(norm(i['name']).lower())
        if not found:
            fail(f"tracker item {i['key']} {i['name']}: in no sheet")
        # An item in two sheets ("Đề xuất thêm" and "Công trình mới"): the same price in both, the note that names more sources.
        price = lambda n: re.search(r'([\d,]+) coins', n).group(1) if 'coins' in n else n  # noqa: E731
        if len({price(n) for _, n in found}) > 1:
            clash.append((i['key'], i['name'], found))
        notes[i['key']] = max((n for _, n in found), key=len)
    return notes, clash


# ------------------------------------------------------------------------------------------ the economy (prompts 7, 20)

def economy(label):
    """Per chapter in the order of play: coins a campaign-only player earns, and the early-buy price of what it opens."""
    camp, rules = campaign(), shop_rules()
    cps, vehicles = cp_table()
    loot = story_loot()
    early_table = rules['early']
    order = [c['number'] for c in camp['chapters']]

    def is_tower(cid):
        v = vehicles.get(cid)
        return v is not None and v.get('fort') is not None

    def price(cid):
        if cid in rules['premium']:
            return rules['premium'][cid]
        return early_table.get(cid, 300 + 150 * cps.get(cid, 5))

    def buyable(cid):
        # The shop sells early the vehicles and supports the campaign opens (towers are won, not bought); D2: not story loot.
        return (not is_tower(cid)) and '.' not in cid and cid not in rules['premium'] and not (early_table and cid in loot)

    xp_need = lambda lv: 300 + 200 * (max(1, lv) - 1)  # noqa: E731
    total, xp, level = 0, 0.0, 1
    rows = []
    for c in order:
        ms = [m for m in camp['missions'] if m['chapter'] == c and not m.get('branch')]
        earned = 0
        for m in ms:
            got = m['coins'] + 50 * STARS + 300
            xp += m['xp'] + 30 * STARS
            while xp >= xp_need(level):
                xp -= xp_need(level)
                level += 1
                got += 150 * level
            earned += got
        before = total
        total += earned
        cards = [u for m in ms for u in m.get('unlocks', []) if '.' not in u and u in cps]
        sold = [u for u in cards if buyable(u)]
        rows.append({'chapter': c, 'coins': earned, 'before': before, 'total': total, 'cards': len(cards),
                     'sold': len(sold), 'price': sum(price(u) for u in sold), 'ids': cards})
    premium = sorted(rules['premium'].items())
    starters = [s for s in rules['starters'] if s in cps and not is_tower(s)]
    ranks = rank_curve(camp, len(rules['starters']))
    for r in rows:
        r['rank'] = ranks.get(r['chapter'])
    out = {'label': label, 'rows': rows, 'premium': premium, 'starters': starters, 'build': build_line()}
    return out


# build_campaign.simulate's tables: coins and blueprints for each rank of a card, and the main deck (8 cards and 6 towers).
RANK_COINS = [0, 50, 100, 200, 400, 700, 1200, 2000, 3200, 5000]
RANK_PRINTS = [0, 2, 4, 8, 12, 20, 30, 45, 65, 90]
DECK = 14


def rank_curve(camp, owned):
    """
    The main deck's average rank at the end of each chapter, for a campaign-only player (build_campaign.simulate on the
    built pay: two stars a mission, the first clear's crate, the level bonuses; the crate's blueprints shared among the
    cards owned). <owned> is how many cards a new player has.
    """
    total, xp, level, prints, universal = 0.0, 0.0, 1, 0.0, 0.0
    ranks = [1] * DECK
    unlocked = owned
    end = {}
    for m in camp['missions']:
        if m.get('branch'):
            continue
        c, p = m['coins'], m['prints']
        total += c + 50 * STARS + 300
        xp += c * 0.8 + 30 * STARS
        while xp >= 300 + 200 * (level - 1):
            xp -= 300 + 200 * (level - 1)
            level += 1
            total += 150 * level
        unlocked += len(m.get('unlocks', []))
        prints += (p + 15.0 * min(1.0, DECK / max(1, unlocked))) / DECK
        universal += m.get('rarePrints', 0)
        while True:
            i = min(range(DECK), key=lambda k: ranks[k])
            r = ranks[i]
            if r >= 10:
                break
            own = prints - sum(RANK_PRINTS[1:r])
            if total < RANK_COINS[r] or own + universal < RANK_PRINTS[r]:
                break
            total -= RANK_COINS[r]
            if own < RANK_PRINTS[r]:
                universal -= RANK_PRINTS[r] - own
            ranks[i] += 1
        end[m['chapter']] = round(sum(ranks) / DECK, 2)
    return end


def build_line():
    """The campaign builder's own economy line (its prompt-7 rank tune), from a dry build that writes nothing."""
    res = subprocess.run([sys.executable, BUILD, '--dry'], capture_output=True, text=True, encoding='utf-8', cwd=ROOT)
    if res.returncode:
        fail('build_campaign --dry: ' + res.stdout + res.stderr)
    return [ln.strip() for ln in res.stdout.splitlines() if 'coin scale' in ln or 'only: pay' in ln]


# ------------------------------------------------------------------------------------------ E.3: the story sheet

def e3_check(wb):
    camp, table = campaign(), texts()
    loot = story_loot()
    by_number = {c['number']: c for c in camp['chapters']}
    map_name = {k[4:]: resolve(v[0], table) for k, v in table.items() if k.startswith('map.') and k.count('.') == 1}
    name_map = {v.lower(): k for k, v in map_name.items()}

    def proper(unit):
        full = table.get('unit.' + unit, (unit,))[0]
        return full.split(' · ')[0]
    bosses = {m.get('boss', {}).get('def') for m in camp['missions']} | {s.get('boss', {}).get('def') for m in camp['missions'] for s in m.get('stages', [])}
    for c in camp['chapters']:
        bosses |= {c.get('main')} | set(c.get('minis', []))
    boss_names = {proper(b): b for b in bosses if b}
    # Commanders: id -> the names the sheet may call them by (first name, last name, call sign) and the chapter that opens them.
    cmd_text = open(COMMANDERS, encoding='utf-8').read()
    unlocks = dict(re.findall(r'Combat\("([a-z]+)", "[a-z]+", "([a-z0-9+]+)"', cmd_text))
    unlocks.update(dict(re.findall(r'Econ\("([a-z]+)", "([a-z0-9+]+)"', cmd_text)))
    unlocks.update(dict(re.findall(r'Id = "([a-z]+)", Family = CommanderFamily\.\w+, Portrait = "[a-z]+", Unlock = "([a-z0-9+]+)"', cmd_text)))
    alias = {}
    for cid in unlocks:
        person = table.get('name.' + cid, ('',))[0]
        call = resolve(table.get(f'cmdr.{cid}.call', ('',))[0], table)
        for word in person.split() + [call]:
            if word and word[0].isupper():
                alias[word.lower()] = cid

    def unlock_chapter(code):
        m = re.match(r'([ci])(\d+)', code)
        return int(m.group(2)) + (INTERLUDE if m.group(1) == 'i' else 0)
    cmd_at = {}
    for cid, code in unlocks.items():
        cmd_at.setdefault(unlock_chapter(code), set()).add(cid)
    loot_at = {}
    for card, mid in loot.items():
        m = next(x for x in camp['missions'] if x['id'] == mid)
        loot_at.setdefault(m['chapter'], set()).add(card)
    # A loot card by the names it goes by: the sheet's ("Xe súng điện từ") and the game's after D1 ("Xe pháo điện từ").
    vehicle_names = {}
    for r in rows_of(wb, 'Phương tiện'):
        vid = norm(r['id'])
        for n in (norm(r['Tên']), table.get('unit.' + vid, ('', ''))[1]):
            if n:
                vehicle_names[n.lower()] = vid

    def loot_card(phrase):
        p = phrase.strip().lower()
        fits = [(len(n), vid) for n, vid in vehicle_names.items() if p in n or n in p]
        return max(fits)[1] if fits else '?' + phrase.strip()

    def names_in(body):
        """The bosses a sheet text names: the longest name first (Behemoth Mk.II is not also Behemoth), not in quotes."""
        found, text = set(), body
        for n in sorted(boss_names, key=len, reverse=True):
            pattern = r'(?<![\w."])' + re.escape(n) + r'(?![\w"])(?!\.\w)'
            if re.search(pattern, text):
                found.add(boss_names[n])
                text = re.sub(pattern, '#', text)
        return found

    out = []
    for r in rows_of(wb, 'Cốt truyện'):
        part, item, body = norm(r['Phần']), norm(r['Mục']), norm(r['Nội dung'])
        m = re.match(r'Chương (\d+) · (.+?) \((\d+)(?: \+ (\d+))?\)', item) or re.match(r'(.+?) \((\d+)\)', item)
        if part.startswith('Xen kẽ'):
            number = INTERLUDE + ROMAN[part.split()[-1]]
            title, n_main, n_side = re.match(r'(.+?) \((\d+)\)', item).group(1), int(re.search(r'\((\d+)', item).group(1)), 0
        elif item.startswith('Chương'):
            number, title, n_main, n_side = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4) or 0)
        else:
            continue
        c = by_number[number]
        ms = [x for x in camp['missions'] if x['chapter'] == number]
        game = {
            'title': table.get(f'chapter.{number}.title', ('',))[0],
            'counts': (sum(1 for x in ms if not x.get('side') and not x.get('branch')), sum(1 for x in ms if x.get('side'))),
            'maps': sorted({x['map'] for x in ms}),
            'main': c.get('main'),
            'minis': sorted(c.get('minis', [])),
            'loot': sorted(loot_at.get(number, set())),
            'commanders': sorted(cmd_at.get(number, set())),
            'missions': [{'id': x['id'], 'map': x['map']} for x in ms],
        }
        sheet_maps_text = re.search(r'Map: ([^.]+)\.', body)
        sheet_maps = []
        for name in (sheet_maps_text.group(1).split(',') if sheet_maps_text else []):
            name = re.sub(r'\s*\(.*?\)', '', name).strip()
            sheet_maps.append(name_map.get(name.lower(), '?' + name))
        main = re.search(r'Boss(?: cuối)?: ([^.;]+?)(?: rơi khỏi bầu trời)?\.', body)
        main = main.group(1).strip() if main else None
        named = names_in(body)
        loot_text = re.search(r'Chiến lợi phẩm: ([^.(]+)', body)
        sheet_loot = sorted({loot_card(x) for x in re.split(r',| và ', loot_text.group(1))} if loot_text else set())
        opens = re.search(r'Mở: ([^.]+)\.', body)
        sheet_cmd = set()
        for w in (re.split(r',| và ', opens.group(1)) if opens else []):
            w = w.replace('chỉ huy', '').strip()
            sheet_cmd.add(alias.get(w.lower(), '?' + w))
        sheet = {'title': title, 'counts': (n_main, n_side), 'maps': sorted(sheet_maps), 'main': boss_names.get(main, '?' + main) if main else None,
                 'named': sorted(named), 'loot': sheet_loot, 'commanders': sorted(sheet_cmd)}
        out.append((number, item, sheet, game))
    return out


# The kind of each difference (DECISIONS 25D2): "fixed" a slip in the game's data, corrected; "known" one an earlier decision
# explains or the check's own reading (a name that is no boss fight); "owner" a difference of story or structure for the
# owner to decide. (chapter, check, words in the difference) -> (kind, why).
E3_KNOWN = [
    (1, 'counts', '', 'known', 'DECISIONS 22A raised chapter 1 from 8 to 9 main missions'),
    (13, 'mini bosses', 'names Behemoth', 'known', "no boss: the sheet's \"bản thiết kế Behemoth\" is the blueprints Mara takes back"),
    (6, 'mini bosses', 'names Behemoth', 'known', 'no boss: the captured Behemoth the brigade escorts (c6m03, prompt 22 C.4)'),
    (12, 'mini bosses', 'names Behemoth', 'known', "no boss: Mara's Behemoth, the ally of the last battle (prompt 22 E.4)"),
    (7, 'mini bosses', 'Juggernaut', 'known', 'prompt 22 B.6 brings Inferno and Juggernaut back in the streets of chapter 7'),
    (10, 'mini bosses', 'Morrigan', 'known', "the sheet's Hawk-Raven duel is Morrigan's fight (c10m12, prompt 22 C.4)"),
    (11, 'mini bosses', 'Locust', 'known', 'prompt 22 C.4: "Locust bay trên đầu" in chapter 11; the summary leaves it out'),
    (12, 'mini bosses', 'Locust', 'owner', "prompt 20's boss slots (story.CHAPTER_BOSSES) put a Locust in chapter 12 (c12m05); "
                                           'neither the sheet nor prompt 22 names one there'),
    (12, 'loot', '', 'owner', "prompt 22 D.6's fifth story loot, Kessler's cruise missiles (c12m02); the sheet lists four (never sold either)"),
    (0, 'maps', '', 'owner', "prompt 4's map reuse in prompt 20's layout: the missions named fight on battlefields the summary "
                             'does not list'),
]


def e3_kind(number, what, text):
    for n, w, words, kind, why in E3_KNOWN:
        if w == what and n in (number, 0) and words in text:
            return kind, why
    return 'owner', ''


def e3_rows(results):
    table = texts()

    def boss(b):
        return table.get('unit.' + b, (b,))[0].split(' · ')[0] if b else '-'

    def mapn(m):
        return resolve(table.get('map.' + m, (m,))[0], table)
    lines = []
    for number, item, sheet, game in results:
        diffs = []
        if norm(sheet['title']).lower() != norm(game['title']).lower():
            diffs.append(('title', f"sheet \"{sheet['title']}\", game \"{game['title']}\""))
        if sheet['counts'] != game['counts']:
            diffs.append(('counts', f"sheet {sheet['counts'][0]} + {sheet['counts'][1]}, game {game['counts'][0]} + {game['counts'][1]} (main + side, story choices' options apart)"))
        if set(sheet['maps']) != set(game['maps']):
            extra = sorted(set(game['maps']) - set(sheet['maps']))
            missing = sorted(set(sheet['maps']) - set(game['maps']))
            on = lambda m: ', '.join(x['id'] for x in game['missions'] if x['map'] == m)  # noqa: E731
            diffs.append(('maps', '; '.join(filter(None, [
                ('the game also fights on ' + ', '.join(f'{mapn(m)} ({on(m)})' for m in extra)) if extra else '',
                ('the sheet also names ' + ', '.join(mapn(m) for m in missing)) if missing else '']))))
        if sheet['main'] != game['main']:
            diffs.append(('main boss', f"sheet {boss(sheet['main']) if sheet['main'] and not sheet['main'].startswith('?') else sheet['main']}, game {boss(game['main'])}"))
        slots = set(game['minis']) | ({game['main']} if game['main'] else set())
        unnamed = sorted(set(game['minis']) - set(sheet['named']))
        not_here = sorted(set(sheet['named']) - slots)
        if unnamed:
            diffs.append(('mini bosses', 'the sheet does not name ' + ', '.join(boss(b) for b in unnamed)))
        if not_here:
            diffs.append(('mini bosses', 'the sheet names ' + ', '.join(boss(b) for b in not_here) + ", which are not this chapter's boss slots"))
        if sheet['loot'] != game['loot']:
            diffs.append(('loot', f"sheet {', '.join(sheet['loot']) or 'none'}, game {', '.join(game['loot']) or 'none'}"))
        if sheet['commanders'] != game['commanders']:
            diffs.append(('commanders', f"sheet {', '.join(sheet['commanders']) or 'none'}, game {', '.join(game['commanders']) or 'none'}"))
        lines.append((number, item, sheet, game, diffs))
    return lines


# ------------------------------------------------------------------------------------------ the report

def label(n):
    return f'Interlude {"I" * (n - INTERLUDE)}' if n > INTERLUDE else f'Chapter {n}'


def route_of(camp):
    where = {}
    order = {c['number']: i for i, c in enumerate(camp['chapters'])}
    for m in camp['missions']:
        for u in m.get('unlocks', []):
            where[u] = (m['chapter'], m['id'])
    return where, order


def write_report(cards, plan, before_route, after_route, former, before, after, notes, clash, e3, orphans):
    table = texts()

    def name(cid):
        return table.get('unit.' + cid, (cid,))[0]
    cps = cp_table()[0]
    rules_before = before.get('rules', {})
    lines = [BEGIN, '## D2: unlocks, early buy, story loot (sheet Phương tiện) and E.3 (sheet Cốt truyện)', '',
             'Applied by `Tools/balance/import_unlocks.py` (prompt 25 D2, DECISIONS 25D2). The route moves are '
             '`Tools/campaign/act11.py`; `campaign.json` was rebuilt from the scripts (`build_campaign.py --no-texts`).', '']
    applied = sum(1 for c in cards if c['chapter'] is not None)
    lines += [f"Rows: {len(cards)}. Applied {applied}, skipped {len(cards) - applied} (not cards).", '',
              '| id | card | before: route | before: early price | sheet: opens | sheet: early price | after: mission | outcome |',
              '|---|---|---|---|---|---|---|---|']
    for c in cards:
        cid = c['id']
        b = before_route.get(cid)
        was_start = cid in rules_before.get('starters', [])
        was_prem = rules_before.get('premium', {}).get(cid)
        b_route = 'starter' if was_start else f'premium {fmt(was_prem)}' if was_prem else f'{label(b[0])}, {b[1]}' if b else 'no mission'
        b_price = '-' if was_start or was_prem or c['chapter'] is None else fmt(300 + 150 * cps.get(cid, 5))
        if c['chapter'] is None:
            lines.append(f"| `{cid}` | {name(cid)} | {b_route} | - | {c['proposal']} | - | - | skipped: not a card (the sheet's own words) |")
            continue
        a = after_route.get(cid)
        sheet_at = 'starter' if c['chapter'] == 0 else label(c['chapter']) + (' (story loot)' if c['loot'] else '')
        a_at = 'starter' if c['chapter'] == 0 else f'{a[1]}' if a else 'NONE'
        changed = (b_route != ('starter' if c['chapter'] == 0 else f'{label(a[0])}, {a[1]}' if a else ''))
        outcome = 'applied' if changed or (c['early'] and b_price != fmt(c['early'])) else 'already so'
        if c['loot']:
            outcome = 'applied: no longer for sale (its story beat was already so)' if not changed else 'applied; not for sale'
        lines.append(f"| `{cid}` | {name(cid)} | {b_route} | {b_price} | {sheet_at} | {fmt(c['early']) if c['early'] else '-'} | {a_at} | {outcome} |")
    lines += ['', f"Starters: {', '.join(plan['starters'])} (were {', '.join(s for s in rules_before.get('starters', []) if s in {c['id'] for c in cards})}). "
              f"A save from before keeps {', '.join(former)} (roster version 6).", '',
              'Cards the sheet does not cover, placed by the D2 rule (DECISIONS 25D2): ' +
              '; '.join(f'`{k}` {label(v[0])}, {v[1]}' for k, v in orphans.items()) + '.', '']
    # The economy.
    lines += ['### Economy (prompts 7 and 20), computed from the data', '',
              'A campaign-only player who wins each mission once with two stars (the pay of `build_campaign.simulate`: the mission\'s '
              'coins, 50 a star, 300 for the first clear\'s crate, the level bonuses). "Opens" is what the chapter unlocks (vehicles, '
              'supports, towers and base modules); "on sale" are the vehicles and supports the shop sells early, and "price" what '
              'buying all of them early costs (towers and modules are won, not sold; after D2 story loot is not sold either). '
              '"Rank" is the main deck\'s average rank at the chapter\'s end (the builder\'s model, `build_campaign.simulate`).', '',
              '| Chapter | Coins in it | Coins before it | Opens (before / after) | On sale (before / after) | Early price (before / after) | Price / coins in it (before / after) | Rank (before / after) |',
              '|---|---|---|---|---|---|---|---|']
    for rb, ra in zip(before['rows'], after['rows']):
        pb = rb['price'] / max(1, rb['coins'])
        pa = ra['price'] / max(1, ra['coins'])
        lines.append(f"| {label(ra['chapter'])} | {fmt(ra['coins'])}" + (f" (was {fmt(rb['coins'])})" if ra['coins'] != rb['coins'] else '') +
                     f" | {fmt(ra['before'])} | {rb['cards']} / {ra['cards']} | {rb['sold']} / {ra['sold']} | {fmt(rb['price'])} / {fmt(ra['price'])} | {pb:.2f} / {pa:.2f} | {rb.get('rank', 0):.2f} / {ra.get('rank', 0):.2f} |")
    tb, ta = before['rows'][-1], after['rows'][-1]
    sb, sa = sum(r['price'] for r in before['rows']), sum(r['price'] for r in after['rows'])
    lines += ['', f"The whole campaign pays {fmt(ta['total'])} coins (was {fmt(tb['total'])}). Buying every card on sale early: "
              f"{fmt(sa)} (was {fmt(sb)}), {sa / ta['total']:.0%} of the campaign's coins (was {sb / tb['total']:.0%}). Premium: "
              + (', '.join(f'`{k}` {fmt(v)}' for k, v in after['premium']) or 'none') + ' (was ' + ', '.join(f'`{k}` {fmt(v)}' for k, v in before['premium']) +
              f", {fmt(sum(v for _, v in before['premium']))} in all).", '',
              "The builder's rank tune (prompt 7: the main deck about rank 7 as act IV begins; prompt 20: acts I-II alone end near 7):", '',
              '- before: ' + '; '.join(before['build']), '- after: ' + '; '.join(after['build']), '']
    # The new content.
    lines += ['### New content: the shop plan (Docs/backlog/new_content.json notes)', '',
              f'{len(notes)} items: each note is its planned price and source from the column "Mở khóa đề xuất" (the statuses are unchanged; '
              'nothing is built). Where a sheet gives two prices, the item\'s slot or CP picks one.', '']
    counts = {}
    for n in notes.values():
        counts[n] = counts.get(n, 0) + 1
    lines += ['| Plan | Items |', '|---|---|'] + [f'| {n[len("25D2 plan: "):]} | {k} |' for n, k in sorted(counts.items(), key=lambda kv: -kv[1])]
    if clash:
        lines += ['', 'Two sheets price one item differently (the note naming more sources is kept): ' + '; '.join(f'{k} {n}' for k, n, _ in clash) + '.']
    # E.3.
    lines += ['', '### E.3: the campaign against the sheet "Cốt truyện"', '',
              'Chapter by chapter: title, main and side missions, battlefields, the main boss and the mini bosses the sheet names, the story '
              'loot and the commanders the chapter opens. Kinds: "known", explained by an earlier decision or no boss fight at all; '
              '"owner", a difference of story or structure left for the owner. No row is a data slip, so no data was changed '
              '(DECISIONS 25D2).', '',
              '| Chapter | Check | Difference | Kind |', '|---|---|---|---|']
    none = []
    for number, item, sheet, game, diffs in e3:
        if not diffs:
            none.append(label(number))
        for what, text in diffs:
            kind, why = e3_kind(number, what, text)
            lines.append(f"| {label(number)} | {what} | {text} | {kind}{': ' + why if why else ''} |")
    lines += ['', 'No difference: ' + (', '.join(none) if none else 'none') + '.', '', END]
    text = open(REPORT, encoding='utf-8').read()
    block = '\n'.join(lines)
    if BEGIN in text:
        text = text[:text.index(BEGIN)] + block + text[text.index(END) + len(END):]
    else:
        text = text.rstrip('\n') + '\n\n' + block + '\n'
    open(REPORT, 'w', encoding='utf-8', newline='\n').write(text)



# ------------------------------------------------------------------------------------------ main

def card_ids():
    """The vehicle cards of the deck and the collection (MatchSettings.AllVehicles)."""
    text = open(os.path.join(SCRIPTS, 'Game', 'Match', 'MatchSettings.cs'), encoding='utf-8').read()
    m = re.search(r'AllVehicles\s*=\s*\{(.*?)\};', text, flags=re.S)
    return set(re.findall(r'"([a-z0-9_]+)"', re.sub(r'//.*', '', m.group(1))))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'snapshot':
        data = economy('before')
        data['rules'] = {k: (sorted(v) if isinstance(v, set) else v) for k, v in shop_rules().items()}
        data['route'] = {k: list(v) for k, v in route_of(campaign())[0].items()}
        json.dump(data, open(BEFORE, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        print('economy before:', data['build'])
        return
    if not os.path.exists(BEFORE):
        fail('run "snapshot" first, on the data before D2')
    before = json.load(open(BEFORE, encoding='utf-8'))
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    cards = read_vehicles(wb)
    plan = sheet_plan(cards, card_ids())
    old = before['rules']['starters']
    plan['starters'].sort(key=lambda s: old.index(s) if s in old else len(old))  # a new player's deck keeps its order
    former = [s for s in old if any(c['id'] == s and c['chapter'] not in (0, None) for c in cards)]
    write_sheet_json(plan)
    write_progression(plan, former)
    write_test_data(cards)
    res = subprocess.run([sys.executable, BUILD, '--no-texts'], capture_output=True, text=True, encoding='utf-8', cwd=ROOT)
    print(res.stdout.strip().splitlines()[0] if res.stdout else '', res.stderr.strip())
    if res.returncode:
        fail('build_campaign: ' + res.stdout + res.stderr)
    notes, clash = new_content_notes(wb)
    tracker.set_notes(notes)
    after = economy('after')
    json.dump(after, open(AFTER, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    camp = campaign()
    after_route = route_of(camp)[0]
    before_route = {k: tuple(v) for k, v in before['route'].items()}
    orphans = {k: after_route[k] for k in ('minefield', 'missile_battery') if k in after_route}
    e3 = e3_rows(e3_check(wb))
    write_report(cards, plan, before_route, after_route, former, before, after, notes, clash, e3, orphans)
    for number, item, sheet, game, diffs in e3:
        for what, text in diffs:
            print(f'E.3 {label(number)}: {what}: {text}')
    print('economy after:', after['build'])


if __name__ == '__main__':
    main()
