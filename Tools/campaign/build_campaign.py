"""Builds the story campaign: Resources/Data/campaign.json and Scripts/Game/Hud/CampaignText.cs.

    python Tools/campaign/build_campaign.py [--report <dir>]

The missions are written in act1.py, act2.py and act3.py, laid out in twelve chapters by act4.py
(prompt 20), in chapters of 9-18 missions and three interludes by act5.py-act8.py (prompt 22), the
story's choices and story loot by act9.py (prompt 22 D), the people and chapters in story.py. This script turns reversed missions round, gives every mission its
pay (the economy curve of Docs/DECISIONS.md section 4, 19A for twelve chapters), checks the campaign's
rules and writes both files. --report also writes the economy table there.

CampaignText.cs holds hand-localised words: a key it already has keeps its words, unless the sources
mark the key fresh (campaign_kit.retext); new keys come from the sources.
"""

import copy
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)

import campaign_kit as kit  # noqa: E402
import story  # noqa: E402
import act1  # noqa: E402,F401
import act2  # noqa: E402,F401
import act3  # noqa: E402,F401
import act4  # noqa: E402,F401
import act5  # noqa: E402,F401
import act6  # noqa: E402,F401
import act7  # noqa: E402,F401
import act8  # noqa: E402,F401
import act9  # noqa: E402,F401

DATA = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Resources', 'Data')
TEXT_CS = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Scripts', 'Game', 'Hud', 'CampaignText.cs')

GOALS = {'Capture', 'Hold', 'Destroy', 'Escort', 'Survive', 'Boss', 'Intercept', 'Hunt', 'Recon', 'Protect', 'ShootDown',
         'Outpost', 'Relieve', 'Evacuate', 'Duel'}

# The cards a new player owns (Progression.StarterVehicles / StarterSupports / StarterTowers).
STARTERS = ['scout_jeep', 'armored_car', 'ifv', 'light_tank', 'main_battle_tank', 'aa_vehicle', 'artillery',
            'artillery_barrage', 'smoke_screen', 'guard_tower', 'mg_bunker', 'aa_turret', 'gun_turret']
MODULES = {'repair_bay', 'ammo_depot', 'airfield', 'logistics_station', 'radar_station'}
# Cards that shoot at aircraft from the ground (and the fighter), for the anti-air rule.
ANTI_AIR = {'aa_vehicle', 'sam_launcher', 'heavy_aa', 'zu23_technical', 'long_sam', 'fighter_jet', 'aa_turret', 'missile_battery', 'iron_beam'}
FLYING_BOSSES = {'mega_gunship', 'drone_mothership', 'sky_fortress', 'silver_bug', 'command_airship',
                 'locust', 'argus', 'icarus_mk0', 'daedalus', 'morrigan'}
CHAPTERS = 12
ACT_IV = 10  # the first chapter of act IV
# Prompt 22 E: the bosses and battlefields P22-content builds (a mission on one says so: "awaits").
PENDING_BOSSES = {'behemoth_mk0', 'morrigan'}
PENDING_MAPS = {'foundry', 'veyra_old_quarter'}
VEHICLES = set()


def balance_vehicles():
    """The vehicle ids balance.json defines (a boss slot without one is fought as its fallback)."""
    text = open(os.path.join(DATA, 'balance.json'), encoding='utf-8').read()
    return set(re.findall(r'\{\s*"id":\s*"([a-z0-9_]+)"', text))


def fail(msg):
    raise SystemExit('campaign: ' + msg)


# ------------------------------------------------------------------------------------------ reversed missions

def turn_xy(o, xk='x', zk='z'):
    if xk in o and zk in o:
        o[xk], o[zk] = round(-o[xk], 2), round(-o[zk], 2)


def turn_heading(o):
    if 'heading' in o:
        o['heading'] = (o['heading'] + 180) % 360


def turn_flat(values):
    return [round(-v, 2) for v in values]


def turn_area(a):
    return {'minX': round(-a['maxX'], 2), 'minZ': round(-a['maxZ'], 2), 'maxX': round(-a['minX'], 2), 'maxZ': round(-a['minZ'], 2)}


def reverse(m):
    """A mission written from the player's corner, turned round onto the battlefield for a reversed map."""
    for u in m.get('units', []):
        turn_xy(u)
        turn_heading(u)
    for key in ('boss', 'convoy'):
        if key in m:
            turn_xy(m[key])
            turn_heading(m[key])
            if 'route' in m[key]:
                m[key]['route'] = turn_flat(m[key]['route'])
    for h in m.get('hunt', []):
        turn_xy(h)
        turn_heading(h)
        if 'route' in h:
            h['route'] = turn_flat(h['route'])
    if 'waves' in m and 'spawns' in m['waves']:
        m['waves']['spawns'] = turn_flat(m['waves']['spawns'])
    turn_xy(m, 'targetX', 'targetZ')
    if 'playArea' in m:
        m['playArea'] = turn_area(m['playArea'])
    if 'ally' in m:
        a = m['ally']
        turn_xy(a)
        turn_heading(a)
        for u in a.get('units', []) + a.get('structures', []):
            turn_xy(u)
            turn_heading(u)
    for s in m.get('stages', []):
        reverse(s)
        for e in s.get('events', []):
            turn_xy(e)
            if 'area' in e:
                e['area'] = turn_area(e['area'])


# ------------------------------------------------------------------------------------------ the economy

COINS = [0, 50, 100, 200, 400, 700, 1200, 2000, 3200, 5000]
PRINTS = [0, 2, 4, 8, 12, 20, 30, 45, 65, 90]
DECK = 14  # 8 cards + 6 towers


def xp_for_level(level):
    return 300 + 200 * (max(1, level) - 1)


def pay_base(missions):
    """Unscaled pay by position: later missions pay more; bosses and operations more again; side missions a little more than their main."""
    index = 0
    last_main = None
    for m in missions:
        if m.get('side'):
            base = last_main
            m['_coins'], m['_prints'] = base[0] * 1.15, base[1] * 0.6
            continue
        # Prompt 22 D.5: an option of a story choice pays from the mission that offers it (act9.PAY) and moves nobody's pay.
        if m.get('branch'):
            k_coins, k_prints = m.get('_pay', (1.0, 1.0))
            m['_coins'], m['_prints'] = last_main[0] * k_coins, last_main[1] * k_prints
            continue
        # Prompt 22: a set piece of stages (not the chapter's operation) pays between a boss and an operation.
        kind = 2.4 if m.get('operation') else 1.8 if m.get('stages') else 1.5 if m['goal'] in ('Boss', 'Intercept') else 1.0
        coins = (1.0 + index / 30.0) * kind
        prints = (1.0 + index / 22.0) * kind
        m['_coins'], m['_prints'] = coins, prints
        last_main = (coins, prints)
        # An epilogue (prompt 16) pays like the chapter's boss where it stands and moves nobody else's pay.
        if not m.get('epilogue'):
            index += 1


def simulate(missions, coin_scale, print_scale, stars=2):
    """
    A player who plays only the campaign, winning each mission once with two stars: coins (mission,
    stars, the silver crate of a first clear, rank-up bonuses from XP) and blueprints (the mission's
    for the main deck, the silver crate's share of them, side missions' universal ones), spent at once
    on the main deck's lowest card. Returns the average deck rank after each mission.
    """
    coins, xp, level = 0.0, 0.0, 1
    prints = 0.0  # per card of the main deck (split evenly)
    universal = 0.0
    ranks = [1] * DECK
    unlocked = len(STARTERS)
    out = []
    for m in missions:
        # Prompt 22 D.5: only one option of a choice is played; the tune leaves them out (the rest is paid as before).
        if m.get('branch'):
            out.append((m['id'], out[-1][1] if out else 1.0, coins, level))
            continue
        c = round(m['_coins'] * coin_scale / 5) * 5
        p = round(m['_prints'] * print_scale)
        coins += c + 50 * stars + 300
        xp += c * 0.8 + 30 * stars
        while xp >= xp_for_level(level):
            xp -= xp_for_level(level)
            level += 1
            coins += 150 * level
        unlocked += len(m.get('unlocks', []))
        prints += (p + 15.0 * min(1.0, DECK / max(1, unlocked))) / DECK
        universal += m.get('rarePrints', 0)
        while True:
            i = min(range(DECK), key=lambda k: ranks[k])
            r = ranks[i]
            if r >= 10:
                break
            need_c, need_p = COINS[r], PRINTS[r]
            # The deck's blueprints are shared out evenly; a card short of its own takes universal ones.
            own = prints - sum(PRINTS[1:r])  # what this card still holds of its even share
            if coins < need_c or own + universal < need_p:
                break
            coins -= need_c
            if own < need_p:
                universal -= need_p - own
            ranks[i] += 1
        out.append((m['id'], sum(ranks) / DECK, coins, level))
    return out


def rank_at(result, missions, chapter):
    """The average rank as a chapter begins (after the last mission before it)."""
    first = next(i for i, m in enumerate(missions) if m['chapter'] == chapter)
    return result[first - 1][1] if first > 0 else 1.0


def tune(missions):
    """Scales coins and blueprints so the main deck is about rank 7 as act IV begins, and a little over 8 by the end."""
    pay_base(missions)
    best = None
    # The ranks follow the blueprints (the coins of stars and crates are enough), so the coin scale stays at its
    # floor, the old campaign's pay; prompt 22: 187 missions pay fewer blueprints each than 144 did, so that search starts lower.
    for cs in [x / 10 for x in range(10, 60)]:
        for ps in [x / 4 for x in range(2, 60)]:
            r = simulate(missions, cs * 100, ps)
            at4 = rank_at(r, missions, ACT_IV)
            end = r[-1][1]
            score = abs(at4 - 7.0) * 3 + abs(end - 8.2)
            if best is None or score < best[0]:
                best = (score, cs * 100, ps)
    _, cs, ps = best
    for m in missions:
        m['coins'] = int(round(m['_coins'] * cs / 5) * 5)
        m['xp'] = int(round(m['_coins'] * cs * 0.8 / 5) * 5)
        m['prints'] = int(round(m['_prints'] * ps))
    return cs, ps, simulate(missions, cs, ps)


def cut(missions, last_act):
    """
    The campaign a build with acts I to <last_act> switched on plays (prompt 20 C; an interlude goes
    with the act before it, prompt 22): the later acts' missions gone, their cards, modules and HQ
    levels paid by the last chapter's operation (the Game layer does the same, Campaign.All).
    """
    last = last_act * 3
    kept = [copy.deepcopy(m) for m in missions if story.ACT_OF[m['chapter']] <= last_act]
    op = next(m for m in kept if m['chapter'] == last and m.get('operation'))
    for m in missions:
        if story.ACT_OF[m['chapter']] > last_act:
            op['unlocks'] = op.get('unlocks', []) + m.get('unlocks', [])
    return kept


def release_scales(missions, cs, ps):
    """
    The pay scale a shorter release uses so its deck ends near rank 7 too (D.3): acts I-II and I-III.
    Coins, XP and blueprints of every mission are multiplied by it.
    """
    scales = {}
    for last_act in (2, 3):
        kept = cut(missions, last_act)
        best = None
        for k in [x / 100 for x in range(100, 301, 2)]:  # a shorter release never pays less
            end = simulate(kept, cs * k, ps * k)[-1][1]
            if best is None or abs(end - 7.0) < best[0]:
                best = (abs(end - 7.0), k, end)
        scales[last_act] = (best[1], best[2])
    return scales


# ------------------------------------------------------------------------------------------ rules

def signature(m):
    return {
        'direction': bool(m.get('reversed')),
        'weather': m['weather'],
        'goal': m['goal'],
        'area': json.dumps(m.get('playArea'), sort_keys=True),
        'base': (m.get('variant', 'conquest'), m.get('playerBase', 'None'), m.get('enemyBase', 'None')),
    }


def check(missions):
    global VEHICLES
    VEHICLES = balance_vehicles()
    ids = [m['id'] for m in missions]
    if len(set(ids)) != len(ids):
        fail('duplicate ids')
    # Prompt 22 D.5: the options of a story choice are counted apart (one of them is played; checked below).
    main = [m for m in missions if not m.get('side') and not m.get('branch')]
    side = [m for m in missions if m.get('side')]
    for m in missions:
        if m.get('storyChoice'):
            options = [b for b in missions if b.get('branch') == m['storyChoice']]
            at = missions.index(m)
            if len(options) != 2 or len({b['option'] for b in options}) != 2 or missions[at + 1:at + 3] != options:
                fail(f"{m['id']}: choice {m['storyChoice']} wants two options right after it")
            for b in options:
                if b.get('unlocks') or b.get('side') or b.get('operation') or b['chapter'] != m['chapter']:
                    fail(f"{b['id']}: an option of a choice unlocks no card and is a main mission of its chapter")
    if any(b.get('branch') and not any(m.get('storyChoice') == b['branch'] for m in missions) for b in missions):
        fail('an option of a choice no mission offers')
    # Prompt 22 B: every chapter's counts (story.COUNTS), 9-18 main missions a chapter, four an interlude.
    for c, (n_main, n_side) in story.COUNTS.items():
        ms = [m for m in main if m['chapter'] == c]
        ss = [m for m in side if m['chapter'] == c]
        if len(ms) != n_main or len(ss) != n_side:
            fail(f'chapter {c}: {len(ms)} main and {len(ss)} side missions (want {n_main} and {n_side})')
        if c in story.INTERLUDES:
            if n_main != 4 or any(m.get('operation') for m in ms):
                fail(f'interlude {c}: four missions and no operation')
        elif not 9 <= n_main <= 18:
            fail(f'chapter {c}: {n_main} main missions (9-18)')
        if any(m.get('epilogue') for m in ms):
            fail(f'chapter {c}: no epilogue after the operation any more (prompt 22)')
    # Campaign order is chapter order (story.ORDER), and no two missions in a row on one map with one set-up.
    seq = [story.ORDER.index(m['chapter']) for m in missions]
    if seq != sorted(seq):
        fail('missions out of chapter order')
    for a, b in zip(missions, missions[1:]):
        if a['map'] == b['map'] and signature(a) == signature(b):
            fail(f"{a['id']} and {b['id']} in a row on {a['map']} with one set-up")
    owned = set(STARTERS)
    per_chapter = {}
    for m in missions:
        if m['goal'] not in GOALS:
            fail(f"{m['id']}: goal {m['goal']}")
        if (m['map'] in PENDING_MAPS) != any(a == 'map:' + m['map'] for a in m.get('awaits', [])):
            fail(f"{m['id']}: a mission on {m['map']} awaits it, and only then")
        if m['weather'] not in kit.WEATHER[m['map']]:
            fail(f"{m['id']}: {m['weather']} is not weather {m['map']} has")
        if m.get('side') and m.get('unlocks'):
            fail(f"{m['id']}: side missions pay blueprints or tower equipment, not cards")
        if m.get('side') and not (m.get('rarePrints') or m.get('towerGear')):
            fail(f"{m['id']}: a side mission pays rare blueprints or tower equipment")
        for u in m.get('unlocks', []):
            if u in owned:
                fail(f"{m['id']}: {u} unlocked twice")
            owned.add(u)
            # A tower branch opened (prompt 16: the long-range coastal battery) is no card.
            if u not in MODULES and '.' not in u:
                per_chapter[m['chapter']] = per_chapter.get(m['chapter'], 0) + 1
        bosses = [m.get('boss', {})] + [s.get('boss', {}) for s in m.get('stages', [])]
        for b in bosses:
            if not b:
                continue
            # A boss slot pass 2 has not built is fought as its fallback (prompt 20).
            if b['def'] not in VEHICLES and b.get('fallback') not in VEHICLES:
                fail(f"{m['id']}: boss {b['def']} has no def and no fallback that exists")
            if b['def'] in PENDING_BOSSES and 'boss:' + b['def'] not in m.get('awaits', []):
                fail(f"{m['id']}: {b['def']} comes from part E; the mission awaits it")
            if b['def'] in FLYING_BOSSES or b.get('fallback') in FLYING_BOSSES:
                aa = len(owned & ANTI_AIR)
                if aa < 4:
                    fail(f"{m['id']}: flying boss {b} with only {aa} anti-air cards unlocked")
        if m.get('operation'):
            st = m.get('stages', [])
            if not any(s.get('choices') for s in st):
                fail(f"{m['id']}: an operation needs a choice")
            if len(st) < 4:
                fail(f"{m['id']}: an operation of {len(st)} stages")
    for c in range(1, CHAPTERS + 1):
        n = per_chapter.get(c, 0)
        if not 4 <= n <= 7:
            fail(f'chapter {c} unlocks {n} cards')
    for c in story.INTERLUDES:
        if per_chapter.get(c, 0):
            fail(f'interlude {c} unlocks cards (the route stays in the chapters)')
    modules = [u for m in missions for u in m.get('unlocks', []) if u in MODULES]
    if sorted(modules) != sorted(MODULES):
        fail(f'modules {modules}')
    # Prompt 22 B.1: a chapter's last main mission is its operation (prompt 5's frame) and fights its main boss;
    # the only operation of the chapter. B.5: a set piece besides it in every chapter.
    for c in range(1, CHAPTERS + 1):
        ms = [m for m in missions if m['chapter'] == c and not m.get('side') and not m.get('branch')]
        last = ms[-1]
        if not last.get('operation') or not last.get('stages'):
            fail(f'chapter {c}: the last mission is its operation')
        if [m['id'] for m in ms if m.get('operation')] != [last['id']]:
            fail(f'chapter {c}: one operation, the last mission')
        if story.CHAPTER_BOSSES[c][0] not in {s.get('boss', {}).get('def') for s in last['stages']}:
            fail(f'chapter {c}: the operation fights {story.CHAPTER_BOSSES[c][0]}')
        if not any(m.get('setPiece') for m in ms if m is not last):
            fail(f'chapter {c}: a set piece besides the operation')
    levels = sorted((m['hqLevel'], m['chapter']) for m in missions if m.get('hqLevel'))
    if levels != [(1, 1), (2, 3), (3, 6), (4, 9), (5, 11)]:
        fail(f'HQ levels {levels} (want levels 1-5 in chapters 1, 3, 6, 9 and 11)')
    # Every chapter's boss slots are fought in it (a mission's or a stage's boss, by id).
    for c, (main, minis) in story.CHAPTER_BOSSES.items():
        fought = {b.get('def') for m in missions if m['chapter'] == c
                  for b in [m.get('boss', {})] + [s.get('boss', {}) for s in m.get('stages', [])] if b}
        for slot in ([main] if main else []) + minis:
            if slot not in fought:
                fail(f'chapter {c}: boss {slot} is fought in none of its missions')
    legacy = sorted(m['legacy'] for m in missions if m.get('legacy'))
    if legacy != sorted(f'm{i:02d}' for i in range(23)):
        fail(f'legacy ids {legacy}')
    # Map reuse: two missions on one map differ in at least two of direction, base, weather, area, goal.
    for i, a in enumerate(missions):
        for b in missions[i + 1:]:
            if a['map'] != b['map']:
                continue
            sa, sb = signature(a), signature(b)
            diff = [k for k in sa if sa[k] != sb[k]]
            if len(diff) < 2:
                fail(f"{a['id']} and {b['id']} on {a['map']} differ only in {diff}")
    for s in side:
        if s.get('after') not in ids or next(m for m in missions if m['id'] == s['after']).get('side'):
            fail(f"{s['id']}: after {s.get('after')}")
    # Prompt 22 B: a moved mission lands on one that exists, and no id is moved twice.
    for old, new in story.MOVES22.items():
        if new not in ids or old in ids:
            fail(f'move {old} -> {new}')
    return owned


# ------------------------------------------------------------------------------------------ writing

def cs_string(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


TABLE_LINE = re.compile(r'^\s*\["((?:[^"\\]|\\.)*)"\] = \(("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*")\),\s*$')


def table_in_file():
    """CampaignText.cs as it is: key -> (en, vi) as C# literals, untouched."""
    table = {}
    if os.path.exists(TEXT_CS):
        for line in open(TEXT_CS, encoding='utf-8').read().splitlines():
            m = TABLE_LINE.match(line)
            if m:
                table[m.group(1)] = (m.group(2), m.group(3))
    return table


# A key of one mission's words (its name, briefing, fragment, radio lines, stages and choices).
MISSION_KEY = re.compile(r'^(?:mission|stage|choice)\.((?:c\d+[ms]|i\d+m)\d+)\.|^radio\.[a-z]+\.((?:c\d+[ms]|i\d+m)\d+)\.')


def write_texts(missions):
    kept = table_in_file()
    # Prompt 22: the words of a mission no longer in the campaign go (their keys are not the sources' any more), and so
    # does a mission's radio line no mission or stage plays any more (a line rewritten under a new key).
    live = {m['id'] for m in missions}
    played = {r['key'] for m in missions for r in m.get('radio', [])}
    played |= {e['key'] for m in missions for s in m.get('stages', []) for e in s.get('events', []) if e.get('kind') == 'Radio'}
    for key in sorted(set(kept) | set(kit.TEXTS)):
        mk = MISSION_KEY.match(key)
        if not mk:
            continue
        gone = (mk.group(1) or mk.group(2)) not in live and key not in kit.TEXTS
        silent = key.startswith('radio.') and key not in played
        if gone or silent:
            kept.pop(key, None)
            kit.TEXTS.pop(key, None)
    lines = ['// Generated by Tools/campaign/build_campaign.py: edit the sources, not this file (a key already here keeps',
             "// its hand-localised words unless the sources mark it fresh; see the script's notes).",
             'using System.Collections.Generic;', '',
             'namespace MachineBrigade.Game.Hud', '{',
             '    /// <summary>The story campaign\'s texts (missions, radio, stages, choices, chapters, the dossier), English and Vietnamese.</summary>',
             '    public static class CampaignText', '    {',
             '        public static readonly Dictionary<string, (string en, string vi)> Table = new()', '        {']
    for key in sorted(set(kit.TEXTS) | set(kept)):
        if key in kept and key not in kit.FRESH:
            en, vi = kept[key]
        else:
            en, vi = kit.TEXTS[key]
            if '...' in en or '...' in vi:
                en, vi = en.replace('...', '…'), vi.replace('...', '…')
            en, vi = cs_string(en), cs_string(vi)
        lines.append(f'            [{cs_string(key)}] = ({en}, {vi}),')
    lines += ['        };', '', '        /// <summary>The speakers that have a portrait (Resources/UI/Portraits/&lt;id&gt;.png).</summary>',
              '        public static readonly string[] Speakers = { ' + ', '.join(cs_string(s) for s in story.SPEAKERS) + ' };',
              '    }', '}', '']
    open(TEXT_CS, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(lines))


def compact(value, indent=6):
    return json.dumps(value, ensure_ascii=False, separators=(', ', ': '))


def write_json(missions, scales):
    chapters = [{'number': n, 'act': act, **({'interlude': il} if il else {}), 'maps': maps, **({'general': g} if g else {}),
                 **({'main': story.CHAPTER_BOSSES[n][0]} if story.CHAPTER_BOSSES[n][0] else {}), 'minis': story.CHAPTER_BOSSES[n][1], 'comic': f'comic.{n}'}
                for n, act, il, _, maps, g, _, _ in story.CHAPTERS]
    generals = [{'id': gid, 'deck': deck, 'supports': sup, 'style': style, 'stance': stance} for gid, deck, sup, style, stance, _, _ in story.GENERALS]
    n_main = sum(1 for m in missions if not m.get('side') and not m.get('branch'))
    n_branch = sum(1 for m in missions if m.get('branch'))
    out = [f'// The story campaign (prompts 4, 20 and 22): twelve chapters in four acts and three interludes, {n_main} main missions, '
           f'{len(missions) - n_main - n_branch} side missions and {n_branch} missions of the story choices (one of each two is played).',
           '// Generated by Tools/campaign/build_campaign.py from act1.py-act9.py and story.py: edit those, not this file.',
           '{',
           "  // Prompt 20 B.3: where the nine-chapter campaign's missions went, for a save made before (PlayerProfile.MigrateCampaign).",
           '  "migration": ' + compact({'moves': story.MOVES, 'chaptersSeen': {str(k): v for k, v in story.CHAPTERS_SEEN.items()}, 'hq': story.OLD_HQ}) + ',',
           "  // Prompt 22 B: where a mission of the twelve chapters of ten went (a save of campaign version 3).",
           '  "migration22": ' + compact({'moves': story.MOVES22}) + ',',
           '  // Prompt 20 D.3: a release with only acts I-II (or I-III) switched on pays every mission this much more.',
           '  "economy": ' + compact({'payScale': {str(a): round(k, 2) for a, (k, _) in scales.items()}}) + ',',
           '  "chapters": [']
    out += ['    ' + compact(c) + (',' if i < len(chapters) - 1 else '') for i, c in enumerate(chapters)]
    out += ['  ],', '  "generals": [']
    out += ['    ' + compact(g) + (',' if i < len(generals) - 1 else '') for i, g in enumerate(generals)]
    out += ['  ],', '  "missions": [']
    keys = ['id', 'chapter', 'side', 'after', 'map', 'variant', 'reversed', 'weather', 'goal']
    for i, m in enumerate(missions):
        clean = {k: v for k, v in m.items() if not k.startswith('_')}
        ordered = {k: clean[k] for k in keys if k in clean}
        ordered.update({k: v for k, v in clean.items() if k not in ordered})
        out.append('    ' + compact(ordered) + (',' if i < len(missions) - 1 else ''))
    out += ['  ]', '}', '']
    open(os.path.join(DATA, 'campaign.json'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(out))


def report(missions, cs, ps, result, folder):
    os.makedirs(folder, exist_ok=True)
    rows = []
    cum_c = cum_p = 0
    for c in story.ORDER:
        ms = [m for m in missions if m['chapter'] == c]
        coins = sum(m['coins'] for m in ms)
        prints = sum(m['prints'] for m in ms)
        cum_c += coins
        cum_p += prints
        last = max(i for i, m in enumerate(missions) if m['chapter'] == c)
        rows.append((c, len(ms), coins, cum_c, prints, cum_p, result[last][1], result[last][3]))
    with open(os.path.join(folder, 'campaign_economy.md'), 'w', encoding='utf-8') as f:
        f.write(f'coin scale {cs:.0f}, blueprint scale {ps:.2f}\n\n')
        f.write('| Chapter | Missions | Coins | Coins so far | Deck blueprints | Blueprints so far | Deck rank at the end | Player level |\n')
        f.write('|---|---|---|---|---|---|---|---|\n')
        for r in rows:
            f.write(f'| {r[0]} | {r[1]} | {r[2]:,} | {r[3]:,} | {r[4]:,} | {r[5]:,} | {r[6]:.1f} | {r[7]} |\n')
        f.write('\n| Mission | Coins | XP | Deck blueprints | Rare | Tower piece | Rank after |\n|---|---|---|---|---|---|---|\n')
        for m, (mid, rank, _, _) in zip(missions, result):
            f.write(f"| {mid} | {m['coins']} | {m['xp']} | {m['prints']} | {m.get('rarePrints', '')} | {m.get('towerGear', '')} | {rank:.2f} |\n")
    json.dump({'rows': rows, 'curve': [(mid, rank) for mid, rank, _, _ in result]}, open(os.path.join(folder, 'campaign_economy.json'), 'w'))
    return rows


def main():
    missions = copy.deepcopy(kit.MISSIONS)
    # Chapter order (story.ORDER, the interludes after the chapter before them): each chapter's main missions in the
    # order act8.ORDER plays them, then its side missions.
    place = {mid: i for ids in act8.ORDER.values() for i, mid in enumerate(ids)}
    missions.sort(key=lambda m: (story.ORDER.index(m['chapter']), 1 if m.get('side') else 0, place.get(m['id'], 99), m['id']))
    for m in missions:
        if m.get('reversed'):
            reverse(m)
    check(missions)
    cs, ps, result = tune(missions)
    scales = release_scales(missions, cs, ps)
    write_json(missions, scales)
    write_texts(missions)
    folder = sys.argv[sys.argv.index('--report') + 1] if '--report' in sys.argv else None
    rows = report(missions, cs, ps, result, folder) if folder else None
    at4 = rank_at(result, missions, ACT_IV)
    print(f'{len(missions)} missions, {len(kit.TEXTS)} texts; coin scale {cs:.0f}, blueprint scale {ps:.2f}; '
          f'deck rank {at4:.2f} as act IV begins, {result[-1][1]:.2f} at the end')
    print('  main/side by chapter: ' + ', '.join(f"{c}: {sum(1 for m in missions if m['chapter'] == c and not m.get('side'))}/"
                                                f"{sum(1 for m in missions if m['chapter'] == c and m.get('side'))}" for c in story.ORDER))
    for a, (k, end) in scales.items():
        print(f'  acts I-{"II" if a == 2 else "III"} only: pay x{k:.2f}, deck rank {end:.2f} at the end')
    if rows:
        for r in rows:
            print('  chapter', r[0], 'coins', r[2], 'so far', r[3], 'prints', r[4], 'rank', round(r[6], 2), 'level', r[7])


if __name__ == '__main__':
    main()
