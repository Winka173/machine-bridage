"""Prompt 25 D1: the unit names of the balance spreadsheet into the localisation tables.

    python Tools/balance/import_names.py [--check]

Reads the sheet "Tên đề xuất" of Docs/balance/Machine_Brigade_Can_bang.xlsx (openpyxl, computed values): for each
unit id its full name, its short name (the HUD and the card tray) and its English name. It then edits the hand-
localised C# tables in Assets/MachineBrigade/Scripts/Game/Hud in place, key by key (never regenerating a file, and
never CampaignText.cs as a whole):

- unit.<id> (the full name) and short.<id> (the short name), both languages;
- the name at the head of the unit's guide (guide.<id>, "[[Name]] · ..."), so the guide names the unit as its card does;
- the unit's reference line (note.<id>) where the real model the card was named after moves to (the camouflage rule of
  prompt 24: the real model belongs on the sub-line, not in the card's name; prompt 24's sub-line is not built yet);
- every other text that names the unit by its old name: an old name that is only a name is replaced everywhere, keeping
  its case; an old name that is also an everyday word or a weapon ("xe phòng không", "tên lửa phòng không",
  "artillery") is replaced only where a text names the card (the list PROSE below).

English names follow the game's style (glossary): sentence case and British spelling ("Armoured car"), acronyms kept.
The sheet has no English short name: EN_SHORT gives them. A short name must fit one line of a card (15 letters,
LocalisationScanTests); VI_SHORT lists the sheet's short names changed for that or to keep two cards apart.

The names before the first run are kept in Tools/balance/names_before.json (written once), so the script can be run
again: a second run changes nothing. It also writes the test data of NameSheetTests
(Assets/MachineBrigade/Tests/EditMode/NameSheetData.cs: the names and the old names to scan for) and its own section of
Docs/balance/apply-report.md. --check changes no file and prints what the scan finds.
"""

import json
import os
import re
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
XLSX = os.path.join(ROOT, 'Docs', 'balance', 'Machine_Brigade_Can_bang.xlsx')
SHEET = 'Tên đề xuất'
HUD = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Scripts', 'Game', 'Hud')
BALANCE = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Resources', 'Data', 'balance.json')
CAMPAIGN_SOURCES = os.path.join(ROOT, 'Tools', 'campaign')
BEFORE = os.path.join(HERE, 'names_before.json')
TEST_DATA = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Tests', 'EditMode', 'NameSheetData.cs')
REPORT = os.path.join(ROOT, 'Docs', 'balance', 'apply-report.md')

# The tables Strings.Entries reads, in its order.
TABLES = ['Strings', 'GuideText', 'CampaignText', 'UnitText', 'BigAttackText', 'OrbitalText', 'BossText',
          'SandboxText', 'CommanderText', 'NameText', 'StoryText', 'DialogueText', 'EventText']

SHORT_MAX = 15

# Rows left as they are, with the reason (the report lists them).
SKIP = {
    'spawn_bastion': 'the sheet proposes no name ("kiểm tra còn dùng không"): the bastion is only the fallback of '
                     'ModeSupport.Build when the catalogue has no HQ, which the shipped content always has; its old '
                     'name stays until the base system drops it',
}

# English short names (the sheet has none): the English name when it fits, else the card's word for it.
EN_SHORT = {
    'hover_gunboat': 'Hovercraft', 'armored_car': 'Armoured car', 'ifv': 'IFV', 'supply_truck': 'Supply truck',
    'engineer_vehicle': 'Engineer', 'smoke_carrier': 'Smoke carrier', 'ammo_carrier': 'Ammo carrier',
    'counter_battery_radar': 'CB radar', 'ew_jammer': 'Jammer', 'mine_layer': 'Minelayer', 'command_vehicle': 'Command',
    'shield_carrier': 'Shield carrier', 'scout_jeep': 'Scout', 'vbied': 'Car bomb', 'light_tank': 'Light tank',
    'flame_tank': 'Flame tank', 'turtle_tank': 'Turtle tank', 'bmpt': 'Tank support', 'rocket_technical': 'Rocket pickup',
    'mortar_carrier': 'Mortar', 'artillery': 'SP howitzer', 'mlrs': 'Guided MLRS', 'shahed_truck': 'Kamikaze drones',
    'thermobaric_launcher': 'Thermobaric', 'ballistic_launcher': 'Ballistic', 'heavy_rocket_artillery': 'Heavy MLRS',
    'siege_tank': 'Siege mortar', 'zu23_technical': 'Flak technical', 'aa_vehicle': 'AA gun', 'sam_launcher': 'Medium SAM',
    'heavy_aa': 'Gun–missile AA', 'iron_beam': 'Laser AA', 'long_sam': 'Long-range SAM', 'scout_heli': 'Scout heli',
    'recon_drone': 'Recon UAV', 'wingman_drone': 'Wingman', 'strike_drone': 'Strike UAV', 'swarm_carrier': 'Mothership',
    'attack_helicopter': 'Attack heli', 'fighter_jet': 'Fighter', 'stealth_fighter': 'Stealth fighter',
    'gunship_heli': 'Gunship heli', 'attack_jet': 'Attack jet', 'stealth_bomber': 'Stealth bomber', 'heavy_bomber': 'Bomber',
    'sky_gunship': 'Gunship', 'bunker_vehicle': 'Bunker', 'armored_bulldozer': 'Bulldozer', 'main_battle_tank': 'Battle tank',
    'twin_tank': 'Twin-gun tank', 'heavy_tank': 'Heavy tank', 'titan_tank': 'Super tank', 'fpv_carrier': 'FPV drones',
    'lancet_truck': 'Loiter munition', 'wheeled_gun': 'Wheeled gun', 'tank_destroyer': 'Tank destroyer',
    'railgun_truck': 'Railgun', 'laser_tank': 'Laser tank', 'c_ram': 'C-RAM', 'drone_hangar': 'Drone hangar',
    'heavy_turret': 'Heavy gun', 'missile_battery': 'SAM site', 'bulwark_post': 'Gun post',
}

# The sheet's Vietnamese short names changed, with the reason.
VI_SHORT = {
    'ballistic_launcher': ('TL chiến thuật', '"Tên lửa chiến thuật" is 19 letters, over the 15 of one card line; "TL" is '
                                             'the short names\' abbreviation of "tên lửa"'),
    'wheeled_gun': ('Pháo xung kích', '"Bánh lốp diệt tăng" is 18 letters; the first words of the full name instead'),
    'missile_battery': ('Trạm PK tầm xa', '"PK tầm xa" is the long-range SAM vehicle\'s short name too; the tower keeps '
                                          'the "Trạm" of its full name'),
}

# English words of the sheet respelt the glossary's way (British spelling).
BRITISH = {'Armored': 'Armoured', 'armored': 'armoured'}

# Reference lines (note.<id>) that take the real model the old name carried. A note already naming it is left.
NOTES = {
    'zu23_technical': ('A ZU-23-2 on a pickup: a twin 23 mm anti-aircraft gun, cheap, fast, tears up helicopters, drones and light vehicles.',
                       'ZU-23-2 trên bán tải: pháo phòng không đôi 23 mm, rẻ, nhanh, xé nát trực thăng, drone và xe nhẹ.'),
    'bmpt': ('A BMPT Terminator: twin 30 mm cannons, Ataka missiles and grenade launchers on both front fenders firing to the sides. Escorts tanks.',
             'BMPT Terminator: pháo đôi 30 mm, tên lửa Ataka và súng phóng lựu hai bên chắn bùn bắn sang ngang. Hộ tống xe tăng.'),
    'iron_beam': ('An Iron Beam laser: an endless beam at aircraft, and it shoots down rockets, missiles and drones aimed within 30 m of it. No weapon for the ground.',
                  'La-de kiểu Iron Beam: tia bắn liên tục vào máy bay, và bắn hạ rốc-két, tên lửa, drone nhắm vào trong vòng 30 m. Không có vũ khí đánh mặt đất.'),
    'railgun_truck': ('A railgun: a slug that goes through every vehicle on its line (420 each) from 90 m. Must stand still; slow to fire.',
                      'Pháo điện từ: viên đạn xuyên qua mọi xe trên đường bay (420 mỗi xe) từ 90 m. Phải đứng yên; bắn chậm.'),
    # A new key: the tower had no reference line.
    'missile_battery': ('A Patriot-style battery: a search radar and long-range anti-aircraft missiles fired in pairs.',
                        'Trạm kiểu Patriot: radar tìm kiếm và tên lửa phòng không tầm xa bắn theo cặp.'),
}

# Old names that are also everyday words or weapons: replaced only through PROSE and the guide's head, and scanned
# only where a text writes them as a card's name (the head of a guide, or capitalised in mid-sentence).
GENERIC = {
    'vi': {'armored_car', 'scout_jeep', 'artillery', 'mlrs', 'aa_vehicle', 'sam_launcher', 'long_sam', 'scout_heli',
           'tank_destroyer', 'counter_battery_radar'},
    'en': {'artillery', 'mlrs', 'aa_vehicle', 'light_tank', 'heavy_bomber', 'swarm_carrier', 'c_ram'},
}

# Old names that begin with an acronym or a proper name ("AC-130 Gunship", "Patriot battery"): their case cannot say
# where a sentence starts, so they are replaced through PROSE and the guide's head only (they are still scanned
# everywhere).
PROPER_START = {
    'en': {'sky_gunship', 'sam_launcher', 'bmpt', 'zu23_technical', 'ew_jammer', 'missile_battery', 'iron_beam',
           'titan_tank', 'shahed_truck'},
    'vi': {'bmpt'},
}

# Old names whose replacement would run into the next word (the reference line's "focused-laser tank destroyer").
NOT_BEFORE = {'Focused-laser tank': ' destroyer'}

# English plurals that are not the name plus "s".
PLURALS = {'Patriot battery': 'Patriot batteries', 'Long-range SAM site': 'long-range SAM sites',
           'Escort hovercraft': 'Escort hovercraft', 'Gun–missile AA': 'Gun–missile AA', 'Heavy MLRS': 'Heavy MLRS'}

# Texts that name a unit by an old everyday-word name or by its real model: (key, language, old, new).
PROSE = [
    # The Patriot battery by its old name.
    ('guide.attack_helicopter', 'en', 'long-range SAMs, the Patriot and fighters', 'long-range SAMs, long-range SAM sites and fighters'),
    ('guide.attack_helicopter', 'vi', 'tên lửa phòng không tầm xa, Patriot và tiêm kích', 'xe tên lửa phòng không tầm xa, trạm PK tầm xa và tiêm kích'),
    ('branch.aa_turret.sam.info', 'en', '(the Patriot reaches furthest)', '(the long-range SAM site reaches furthest)'),
    ('branch.aa_turret.sam.info', 'vi', '(Patriot bắn xa nhất)', '(trạm PK tầm xa bắn xa nhất)'),
    ('guide.silver_bug', 'en', 'only long-range SAMs, Patriot batteries and fighters', 'only long-range SAMs, long-range SAM sites and fighters'),
    ('guide.silver_bug', 'vi', 'chỉ SAM tầm xa, dàn Patriot và tiêm kích', 'chỉ PK tầm xa, trạm PK tầm xa và tiêm kích'),
    ('guide.tiers.high', 'en', 'only long-range SAMs, Patriot batteries,', 'only long-range SAMs, long-range SAM sites,'),
    ('guide.tiers.high', 'vi', 'chỉ SAM tầm xa, dàn Patriot, tiêm kích', 'chỉ PK tầm xa, trạm PK tầm xa, tiêm kích'),
    # The laser AA vehicle by its real model.
    ('guide.atgm_tower', 'en', 'or an Iron Beam with the push', 'or a laser AA with the push'),
    ('guide.atgm_tower', 'vi', 'hay Iron Beam đi cùng', 'hay xe la-de phòng không đi cùng'),
    # The airborne gunship (the aircraft card and the item that calls one in) by its real model.
    ('item.gunship_support.info', 'en', 'An AC-130 gunship fights', 'An airborne gunship fights'),
    ('guide.gunship_support', 'en', '· item · an AC-130 for', '· item · an airborne gunship for'),
    ('guide.gunship_support', 'vi', '· vật phẩm · AC-130 trong', '· vật phẩm · pháo hạm bay trong'),
    ('guide.sky_fortress', 'en', '[[Boss]] · AC-130 gunship ·', '[[Boss]] · airborne gunship ·'),
    # The heavy gunship's guide: its old name was the head's second word; the head's old name takes its place.
    ('guide.gunship_heli', 'en', '· heavy helicopter ·', '· flying IFV ·'),
    ('guide.gunship_heli', 'vi', '· trực thăng hạng nặng ·', '· xe bộ binh bay ·'),
    # The turtle tank by its old short name, the scout helicopter as a boss's escort.
    ('guide.armored_bulldozer', 'vi', 'không thay được xe rùa', 'không thay được tăng rùa'),
    ('guide.mega_gunship', 'vi', '1 trực thăng trinh sát đánh dấu', '1 trực thăng trinh sát vũ trang đánh dấu'),
    # The SP howitzer by its old name.
    ('guide.elite_artillery', 'vi', 'đạn 155 mm như pháo tự hành,', 'đạn 155 mm như lựu pháo tự hành,'),
]

# Old short names that are only names (the scan looks for them everywhere); the others are everyday words.
OLD_SHORT_SCANNED = {
    'vi': {'turtle_tank': 'Xe rùa', 'heavy_rocket_artillery': 'Phản lực 300', 'recon_drone': 'UAV do thám',
           'hover_gunboat': 'Xuồng cao tốc'},
    'en': {'heavy_aa': 'Gun-SAM', 'smoke_carrier': 'Smoke car', 'ammo_carrier': 'Ammo truck', 'sky_gunship': 'AC-130 Gunship'},
}

KEY = re.compile(r'\[\s*"([^"\\]+)"\s*\]\s*=\s*\(')


# ---------------------------------------------------------------------------------------------- the C# tables

def read_literal(s, i):
    """The C# string literal at s[i] ('"'): its value and the index after it."""
    j, out = i + 1, []
    while True:
        c = s[j]
        if c == '\\':
            n = s[j + 1]
            if n == 'u':
                out.append(chr(int(s[j + 2:j + 6], 16)))
                j += 6
                continue
            out.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\', "'": "'", '0': '\0'}[n])
            j += 2
            continue
        if c == '"':
            return ''.join(out), j + 1
        out.append(c)
        j += 1


def encode(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t') + '"'


def skip_space(s, i):
    while True:
        while i < len(s) and s[i] in ' \t\r\n':
            i += 1
        if s.startswith('//', i):
            i = s.index('\n', i)
        elif s.startswith('/*', i):
            i = s.index('*/', i) + 2
        else:
            return i


def read_expr(s, i):
    """A string expression ("a" + "b"): its literals as (value, start, end)."""
    parts = []
    i = skip_space(s, i)
    while i < len(s) and s[i] == '"':
        value, end = read_literal(s, i)
        parts.append([value, i, end])
        i = skip_space(s, end)
        if s[i] != '+':
            break
        i = skip_space(s, i + 1)
    return parts, i


class Table:
    """One C# text table: its entries ["key"] = ("en", "vi"), each language a list of literals, edited in place."""

    def __init__(self, name):
        self.name = name
        self.path = os.path.join(HUD, name + '.cs')
        self.source = open(self.path, encoding='utf-8').read()
        self.entries = {}
        for m in KEY.finditer(self.source):
            en, i = read_expr(self.source, m.end())
            if not en or self.source[i] != ',':
                continue
            vi, j = read_expr(self.source, i + 1)
            if not vi or self.source[skip_space(self.source, j)] != ')':
                continue
            self.entries[m.group(1)] = {'en': en, 'vi': vi, 'start': m.start(), 'end': skip_space(self.source, j) + 1,
                                        'changed': False, 'new': False}
        self.inserts = []

    def text(self, key, lang):
        return ''.join(p[0] for p in self.entries[key][lang])

    def edit(self, key, lang, fn):
        """Applies fn to each literal of a language; returns whether any changed."""
        changed = False
        for part in self.entries[key][lang]:
            new = fn(part[0])
            if new != part[0]:
                part[0] = new
                changed = True
        if changed:
            self.entries[key]['changed'] = True
        return changed

    def set(self, key, en, vi):
        e = self.entries[key]
        if self.text(key, 'en') == en and self.text(key, 'vi') == vi:
            return False
        e['en'] = [[en, None, None]]
        e['vi'] = [[vi, None, None]]
        e['changed'] = e['whole'] = True
        return True

    def insert_after(self, after_key, key, en, vi):
        self.inserts.append((after_key, key, en, vi))
        self.entries[key] = {'en': [[en, None, None]], 'vi': [[vi, None, None]], 'new': True, 'changed': True}

    def write(self):
        s = self.source
        edits = []
        for key, e in self.entries.items():
            if not e['changed'] or e['new']:
                continue
            if e.get('whole'):
                open_paren = s.index('(', s.index(']', e['start']))
                edits.append((open_paren, e['end'], '(' + encode(e['en'][0][0]) + ', ' + encode(e['vi'][0][0]) + ')'))
                continue
            for lang in ('en', 'vi'):
                for value, start, end in e[lang]:
                    raw = s[start:end]
                    if read_literal(raw, 0)[0] != value:
                        if '\\u' in raw:
                            raise SystemExit(f'{self.name} {key}: a changed literal with a \\u escape')
                        edits.append((start, end, encode(value)))
        for after_key, key, en, vi in self.inserts:
            e = self.entries[after_key]
            line_end = s.index('\n', e['end'])
            indent = re.match(r'[ \t]*', s[s.rindex('\n', 0, e['start']) + 1:]).group(0)
            edits.append((line_end, line_end, '\n' + indent + f'["{key}"] = (' + encode(en) + ', ' + encode(vi) + '),'))
        for start, end, text in sorted(edits, key=lambda x: x[0], reverse=True):
            s = s[:start] + text + s[end:]
        if s != self.source:
            with open(self.path, 'w', encoding='utf-8', newline='') as f:
                f.write(s)
            return True
        return False


# ---------------------------------------------------------------------------------------------- names

def sentence_case(name):
    """The sheet's Title Case English as the game writes names: the first word capitalised, acronyms kept, British spelling."""
    words = name.split(' ')
    out = []
    for i, word in enumerate(words):
        parts = re.split(r'([-–])', word)
        fixed = []
        for j, p in enumerate(parts):
            if p in '-–' or re.fullmatch(r'[A-Z0-9]{2,}', p) or re.fullmatch(r'[A-Z]-[A-Z]+', p):
                fixed.append(p)
            elif i == 0 and j == 0:
                fixed.append(p[:1].upper() + p[1:].lower())
            else:
                fixed.append(p.lower())
        out.append(''.join(fixed))
    s = ' '.join(out)
    for us, gb in BRITISH.items():
        s = re.sub(r'\b' + us + r'\b', gb, s)
    return s


def title_case(text):
    words = [w for w in text.split(' ') if w[:1].isalpha()]
    return len(words) > 1 and all(w[:1].isupper() for w in words)


def with_case(match, new, old):
    """new written with the case of the text it replaces: UPPER, Title Case, capitalised or lower case."""
    letters = [c for c in match if c.isalpha()]
    if letters and all(c.isupper() for c in letters) and not all(c.isupper() for c in old if c.isalpha()):
        return new.upper()
    if title_case(match) and not title_case(old):
        return ' '.join(w[:1].upper() + w[1:] for w in new.split(' '))
    if match[:1].isupper():
        return new[:1].upper() + new[1:]
    first = new.split(' ')[0]
    return new if re.fullmatch(r'[A-Z0-9]{2,}', first) else new[:1].lower() + new[1:]


def name_pattern(old, lang):
    """A whole-word match of an old name (English: an optional plural s)."""
    tail = r'(s?)' if lang == 'en' else r'()'
    return re.compile(r'(?<![\w-])' + re.escape(old) + tail + r'(?![\w-])', re.IGNORECASE)


def protected_spans(text, protected, old):
    spans = []
    low = text.lower()
    for p in protected:
        pl = p.lower()
        if pl == old.lower():
            continue
        i = low.find(pl)
        while i >= 0:
            spans.append((i, i + len(p)))
            i = low.find(pl, i + 1)
    return spans


def replace_name(text, old, new, lang, protected):
    """Replaces every whole-word old name in text by new, keeping its case, but not inside a protected (current) name."""
    pat = name_pattern(old, lang)
    old_plural = PLURALS.get(old)
    if not pat.search(text) and not (old_plural and name_pattern(old_plural, lang).search(text)):
        return text
    spans = protected_spans(text, protected, old)
    plural = PLURALS.get(new, new + 's')

    def sub(m):
        if any(a <= m.start() and m.end() <= b for a, b in spans):
            return m.group(0)
        if old in NOT_BEFORE and text.startswith(NOT_BEFORE[old], m.end()):
            return m.group(0)
        return with_case(m.group(0), plural if m.group(1) else new, old)

    text = pat.sub(sub, text)
    if old_plural:
        text = name_pattern(old_plural, lang).sub(lambda m: with_case(m.group(0), plural, old), text)
    return text


def find_old(text, old, lang, mode, protected):
    """Where an old name is left: anywhere ('any'), written as a card's name ('card': a guide's head, or capitalised in
    mid-sentence), or at a guide's head ('head')."""
    if old.lower() not in text.lower() and not (old in PLURALS and PLURALS[old].lower() in text.lower()):
        return []
    spans = protected_spans(text, protected, old)
    hits = []
    if mode == 'any':
        pats = [name_pattern(old, lang)] + ([name_pattern(PLURALS[old], lang)] if old in PLURALS else [])
        for pat in pats:
            for m in pat.finditer(text):
                if any(a <= m.start() and m.end() <= b for a, b in spans):
                    continue
                if old in NOT_BEFORE and text.startswith(NOT_BEFORE[old], m.end()):
                    continue
                hits.append(m.start())
        return hits
    if '[[' + old + ']]' in text:
        hits.append(text.index('[[' + old + ']]'))
    if mode == 'head':
        return hits
    for m in re.finditer(r'(?<![\w-])' + re.escape(old) + r'(?![\w-])', text):
        if any(a <= m.start() and m.end() <= b for a, b in spans):
            continue
        before = text[:m.start()].rstrip(' ')
        if before and before[-1] not in '.:!?\n([“"·–—-*' and not before.endswith('[['):
            hits.append(m.start())
    return hits


def read_sheet():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    head = rows[0]
    assert head[:5] == ('id', 'Tên hiện tại', 'Tên đầy đủ đề xuất', 'Tên ngắn (HUD, khay thẻ)', 'Tên tiếng Anh'), head
    out = []
    for r in rows[1:]:
        if not r or not r[0]:
            continue
        out.append({'id': str(r[0]).strip(), 'current': r[1], 'vi': r[2], 'vi_short': r[3], 'en': r[4], 'why': r[5] or ''})
    return out


def game_ids():
    source = open(BALANCE, encoding='utf-8').read()
    return set(re.findall(r'"id"\s*:\s*"([^"]+)"', source))


def guide_head(text):
    m = re.match(r'\[\[(.+?)\]\]', text)
    return m.group(1) if m else None


def cs_string(s):
    return encode(s)


def main():
    check = '--check' in sys.argv
    rows = read_sheet()
    ids = game_ids()
    tables = {t: Table(t) for t in TABLES}

    def where(key):
        for t in TABLES:
            if key in tables[t].entries:
                return tables[t]
        return None

    applied, skipped = [], []
    for r in rows:
        if r['id'] in SKIP:
            skipped.append((r, SKIP[r['id']]))
        elif r['id'] not in ids:
            skipped.append((r, 'the id is not in the game data'))
        elif not where('unit.' + r['id']):
            skipped.append((r, 'the unit has no name key'))
        else:
            applied.append(r)

    # The names before the first run.
    if os.path.exists(BEFORE):
        before = json.load(open(BEFORE, encoding='utf-8'))
    else:
        before = {}
        for r in applied:
            i = r['id']
            t = where('unit.' + i)
            entry = {'unit': [t.text('unit.' + i, 'en'), t.text('unit.' + i, 'vi')]}
            s = where('short.' + i)
            if s:
                entry['short'] = [s.text('short.' + i, 'en'), s.text('short.' + i, 'vi')]
            g = where('guide.' + i)
            if g:
                entry['guide'] = [guide_head(g.text('guide.' + i, 'en')), guide_head(g.text('guide.' + i, 'vi'))]
            before[i] = entry
        if not check:
            with open(BEFORE, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(before, f, ensure_ascii=False, indent=1)
                f.write('\n')

    # The new names.
    names = {}
    problems = []
    for r in applied:
        i = r['id']
        en = sentence_case(r['en'])
        vi = r['vi'].strip()
        vi_short = VI_SHORT[i][0] if i in VI_SHORT else r['vi_short'].strip()
        en_short = EN_SHORT[i]
        for lang, s in (('en', en_short), ('vi', vi_short)):
            if len(s) > SHORT_MAX:
                problems.append(f'{i}: the {lang} short name "{s}" is {len(s)} letters (at most {SHORT_MAX})')
        names[i] = {'en': en, 'vi': vi, 'en_short': en_short, 'vi_short': vi_short}
        if before[i]['unit'][1] != r['current']:
            problems.append(f'{i}: the sheet\'s current name "{r["current"]}" is not the game\'s "{before[i]["unit"][1]}"')
    for lang in ('en', 'vi'):
        for kind in ('', '_short'):
            seen = {}
            for i, n in names.items():
                seen.setdefault(n[lang + kind], []).append(i)
            for name, who in seen.items():
                if len(who) > 1:
                    problems.append(f'{lang}{kind} "{name}" is the name of {", ".join(who)}')

    # 1. The card names.
    changes = []
    for i, n in names.items():
        t = where('unit.' + i)
        if t.set('unit.' + i, n['en'], n['vi']):
            changes.append(f'unit.{i}')
        s = where('short.' + i)
        if s is None:
            problems.append(f'{i}: no short.{i} key')
        elif s.set('short.' + i, n['en_short'], n['vi_short']):
            changes.append(f'short.{i}')

    # 2. The reference lines.
    for i, (en, vi) in NOTES.items():
        key = 'note.' + i
        t = where(key)
        if t is None:
            u = where('unit.' + i)
            u.insert_after('unit.' + i, key, en, vi)
            changes.append(key + ' (new)')
        elif t.set(key, en, vi):
            changes.append(key)

    # 3. The texts that name a unit by an old everyday-word name or its real model.
    for key, lang, old, new in PROSE:
        t = where(key)
        if t is None:
            problems.append(f'PROSE: no key {key}')
            continue
        text = t.text(key, lang)
        if old in text:
            if t.edit(key, lang, lambda v, o=old, n=new: v.replace(o, n)):
                changes.append(f'{key} ({lang})')
            else:
                problems.append(f'PROSE: "{old}" runs over two literals of {key} ({lang})')
        elif new not in text:
            problems.append(f'PROSE: "{old}" is not in {key} ({lang})')

    # 4. The guide's head names the unit as its card does.
    for i, n in names.items():
        t = where('guide.' + i)
        if t is None:
            continue
        for lang, name in (('en', n['en']), ('vi', n['vi'])):
            first = t.entries['guide.' + i][lang][0]
            head = guide_head(first[0])
            if head is None:
                problems.append(f'guide.{i} ({lang}) has no [[name]] at its head')
            elif head != name:
                first[0] = '[[' + name + ']]' + first[0][len(head) + 4:]
                t.entries['guide.' + i]['changed'] = True
                changes.append(f'guide.{i} head ({lang})')

    # The names now written (protected from the old-name replacement: "Xe công sự" inside "Xe công sự triển khai").
    def current_names():
        out = set()
        for t in tables.values():
            for key in t.entries:
                if key.startswith(('unit.', 'short.')):
                    out.add(t.text(key, 'en'))
                    out.add(t.text(key, 'vi'))
        return out

    protected = current_names()

    # 5. The old names that are only names, everywhere else.
    olds = []  # (id, lang, old, new, mode)
    for i, n in names.items():
        b = before[i]
        for lang, li in (('en', 0), ('vi', 1)):
            old = b['unit'][li]
            new = n[lang]
            if old.lower() == new.lower():
                continue
            mode = 'card' if i in GENERIC[lang] else 'any'
            # An old full name that is now the short name (the counter-battery radar, the C-RAM) is still said: only the
            # guide's head may not use it.
            if old in (n['en_short'], n['vi_short']):
                mode = 'head'
            olds.append((i, lang, old, new, mode))
        for lang, table in OLD_SHORT_SCANNED.items():
            if i in table:
                olds.append((i, lang, table[i], n[lang + '_short'], 'any'))
    own = {}
    for i in names:
        own.setdefault(i, set()).update({'unit.' + i, 'short.' + i, 'note.' + i})
    for i, lang, old, new, mode in olds:
        if mode != 'any' or i in PROPER_START[lang]:
            continue
        for t in tables.values():
            for key in t.entries:
                if key in own[i] or key.startswith(('unit.', 'short.')) and key.split('.', 1)[1] in names:
                    continue
                if t.edit(key, lang, lambda v, o=old, n=new, l=lang: replace_name(v, o, n, l, protected)):
                    changes.append(f'{key} ({lang}): {old} -> {new}')

    # 6. The campaign's sources say what CampaignText.cs says (a key there keeps its words, but the sources should match).
    source_edits = []
    if not check:
        for name in sorted(os.listdir(CAMPAIGN_SOURCES)):
            if not name.endswith('.py'):
                continue
            path = os.path.join(CAMPAIGN_SOURCES, name)
            src = open(path, encoding='utf-8').read()
            new_src = src
            for i, lang, old, new, mode in olds:
                if mode == 'any' and i not in PROPER_START[lang]:
                    new_src = replace_name(new_src, old, new, lang, protected)
            if new_src != src:
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    f.write(new_src)
                source_edits.append(name)

    # The scan (NameSheetTests.NoOldNameIsLeft does the same).
    left = []
    for i, lang, old, new, mode in olds:
        for t in tables.values():
            for key in t.entries:
                if key in own[i]:
                    continue
                text = t.text(key, lang)
                for pos in find_old(text, old, lang, mode, protected):
                    left.append(f'{t.name} {key} ({lang}, {mode}): "{old}" in "…{text[max(0, pos - 30):pos + len(old) + 30]}…"')
    for i, n in names.items():
        t = where('guide.' + i)
        if t:
            for lang in ('en', 'vi'):
                if guide_head(t.text('guide.' + i, lang)) != n[lang]:
                    left.append(f'guide.{i} ({lang}) does not open with the unit\'s name')

    if not check:
        written = [t.name for t in tables.values() if t.write()]
        write_test_data(names, olds)
        write_report(applied, skipped, names, before)
        print('tables written:', ', '.join(written) or 'none')
        if source_edits:
            print('campaign sources:', ', '.join(source_edits))
    print(f'{len(applied)} rows applied, {len(skipped)} skipped; {len(changes)} edits')
    for c in changes:
        print('  ', c)
    for p in problems:
        print('PROBLEM', p)
    for l in left:
        print('LEFT', l)
    return 1 if problems or left else 0


def write_test_data(names, olds):
    lines = [
        '// Generated by Tools/balance/import_names.py from the sheet "Tên đề xuất" of Docs/balance/Machine_Brigade_Can_bang.xlsx.',
        '// Edit the sheet or the script, not this file.',
        'namespace MachineBrigade.Tests',
        '{',
        '    /// <summary>Prompt 25 D1: the names of the balance spreadsheet, and the old names no text may use (NameSheetTests).</summary>',
        '    internal static class NameSheetData',
        '    {',
        '        /// <summary>Each unit\'s one name: full and short, English and Vietnamese.</summary>',
        '        internal static readonly (string id, string en, string vi, string enShort, string viShort)[] Names =',
        '        {',
    ]
    for i, n in names.items():
        lines.append(f'            ({cs_string(i)}, {cs_string(n["en"])}, {cs_string(n["vi"])}, {cs_string(n["en_short"])}, {cs_string(n["vi_short"])}),')
    lines += [
        '        };',
        '',
        '        /// <summary>',
        '        /// The old names: "any" ones are only names and may be written nowhere (but in the unit\'s own name keys and reference',
        '        /// line); "card" ones are everyday words too and may not be written as a card\'s name (a guide\'s head, or',
        '        /// capitalised in mid-sentence).',
        '        /// </summary>',
        '        internal static readonly (string id, bool english, string old, string mode)[] OldNames =',
        '        {',
    ]
    for i, lang, old, new, mode in olds:
        lines.append(f'            ({cs_string(i)}, {"true" if lang == "en" else "false"}, {cs_string(old)}, {cs_string(mode)}),')
    lines += [
        '        };',
        '',
        '        /// <summary>Old names that stop before these words are part of another text ("focused-laser tank destroyer").</summary>',
        '        internal static readonly (string old, string next)[] NotBefore =',
        '        {',
    ]
    for old, nxt in NOT_BEFORE.items():
        lines.append(f'            ({cs_string(old)}, {cs_string(nxt)}),')
    lines += [
        '        };',
        '',
        '        /// <summary>English plurals that are not the name plus "s".</summary>',
        '        internal static readonly (string name, string plural)[] Plurals =',
        '        {',
    ]
    for name, plural in PLURALS.items():
        lines.append(f'            ({cs_string(name)}, {cs_string(plural)}),')
    lines += ['        };', '    }', '}', '']
    with open(TEST_DATA, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


BEGIN, END = '<!-- import_names:begin -->', '<!-- import_names:end -->'


def write_report(applied, skipped, names, before):
    out = [BEGIN, '## Tên đề xuất', '',
           f'Applied by `Tools/balance/import_names.py` (prompt 25 D1, DECISIONS 25D1): {len(applied)} rows applied, '
           f'{len(skipped)} skipped. A row applies its full name, its short name and its English name to `unit.<id>` and '
           '`short.<id>`, the head of `guide.<id>`, and every text that named the unit by its old name.', '',
           '| id | full name (vi) | short (vi) | English | English short | before |', '|---|---|---|---|---|---|']
    for r in applied:
        n = names[r['id']]
        b = before[r['id']]
        was = f'{b["unit"][1]} / {b["unit"][0]}'
        out.append(f'| `{r["id"]}` | {n["vi"]} | {n["vi_short"]} | {n["en"]} | {n["en_short"]} | {was} |')
    out += ['', 'Changed from the sheet:', '']
    for i, (s, why) in VI_SHORT.items():
        out.append(f'- `{i}` short name "{s}": {why}.')
    out.append('- English names in sentence case and British spelling (the glossary): "Armored Car" is "Armoured car". '
               'English short names are the script\'s (the sheet has none).')
    out += ['', 'Skipped:', '']
    for r, why in skipped:
        out.append(f'- `{r["id"]}` ({r["current"]}): {why}.')
    out += ['', END]
    section = '\n'.join(out)
    text = open(REPORT, encoding='utf-8').read() if os.path.exists(REPORT) else '# Balance spreadsheet: apply report\n'
    if BEGIN in text:
        text = text[:text.index(BEGIN)] + section + text[text.index(END) + len(END):]
    else:
        text = text.rstrip('\n') + '\n\n' + section + '\n'
    with open(REPORT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


if __name__ == '__main__':
    sys.exit(main())
