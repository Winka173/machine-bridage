"""Builds the story campaign: Resources/Data/campaign.json and Scripts/Game/Hud/CampaignText.cs.

    python Tools/campaign/build_campaign.py [--report <dir>]

The missions are written in act1.py, act2.py and act3.py, the people and chapters in story.py.
This script turns reversed missions round, gives every mission its pay (the economy curve of
Docs/DECISIONS.md section 4), checks the campaign's rules and writes both files. --report also
writes the economy table and chart there.
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
FLYING_BOSSES = {'mega_gunship', 'drone_mothership', 'sky_fortress', 'silver_bug', 'command_airship'}


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
        kind = 2.4 if m.get('operation') else 1.5 if m['goal'] in ('Boss', 'Intercept') or m['id'].endswith('m05') else 1.0
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
    """Scales coins and blueprints so the main deck is about rank 7 as act III begins, and a little over 8 by the end."""
    pay_base(missions)
    best = None
    for cs in [x / 10 for x in range(10, 60)]:
        for ps in [x / 4 for x in range(4, 60)]:
            r = simulate(missions, cs * 100, ps)
            at3 = rank_at(r, missions, 7)
            end = r[-1][1]
            score = abs(at3 - 7.0) * 3 + abs(end - 8.2)
            if best is None or score < best[0]:
                best = (score, cs * 100, ps)
    _, cs, ps = best
    for m in missions:
        m['coins'] = int(round(m['_coins'] * cs / 5) * 5)
        m['xp'] = int(round(m['_coins'] * cs * 0.8 / 5) * 5)
        m['prints'] = int(round(m['_prints'] * ps))
    return cs, ps, simulate(missions, cs, ps)


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
    ids = [m['id'] for m in missions]
    if len(set(ids)) != len(ids):
        fail('duplicate ids')
    main = [m for m in missions if not m.get('side')]
    side = [m for m in missions if m.get('side')]
    # A chapter's epilogue (prompt 16: Leviathan after chapter 4's operation) is a main mission outside the count.
    core = [m for m in main if not m.get('epilogue')]
    if len(core) != 90 or len(side) != 18:
        fail(f'{len(core)} main and {len(side)} side missions (want 90 and 18)')
    for e in main:
        if e.get('epilogue') and e['goal'] != 'Boss':
            fail(f"{e['id']}: an epilogue is a boss fight")
    owned = set(STARTERS)
    per_chapter = {}
    for m in missions:
        if m['goal'] not in GOALS:
            fail(f"{m['id']}: goal {m['goal']}")
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
        bosses = [m.get('boss', {}).get('def')] + [s.get('boss', {}).get('def') for s in m.get('stages', [])]
        for b in bosses:
            if b in FLYING_BOSSES:
                aa = len(owned & ANTI_AIR)
                if aa < 4:
                    fail(f"{m['id']}: flying boss {b} with only {aa} anti-air cards unlocked")
        if m.get('operation'):
            st = m.get('stages', [])
            if not any(s.get('choices') for s in st):
                fail(f"{m['id']}: an operation needs a choice")
            if len(st) < 4:
                fail(f"{m['id']}: an operation of {len(st)} stages")
    for c, n in sorted(per_chapter.items()):
        if not 5 <= n <= 7:
            fail(f'chapter {c} unlocks {n} cards')
    modules = [u for m in missions for u in m.get('unlocks', []) if u in MODULES]
    if sorted(modules) != sorted(MODULES):
        fail(f'modules {modules}')
    for c in range(1, 10):
        ms = [m for m in missions if m['chapter'] == c and not m.get('side') and not m.get('epilogue')]
        if len(ms) != 10:
            fail(f'chapter {c} has {len(ms)} main missions')
        if not ms[9].get('operation') or not ms[9].get('stages'):
            fail(f'chapter {c}: the tenth mission is its operation')
        if ms[4]['goal'] not in ('Boss', 'Intercept'):
            fail(f'chapter {c}: the fifth mission is a boss')
    levels = sorted(m['hqLevel'] for m in missions if m.get('hqLevel'))
    if levels != [1, 2, 3, 4, 5]:
        fail(f'HQ levels {levels}')
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
    return owned


# ------------------------------------------------------------------------------------------ writing

def cs_string(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def write_texts():
    lines = ['// Generated by Tools/campaign/build_campaign.py: edit the script, not this file.',
             'using System.Collections.Generic;', '',
             'namespace MachineBrigade.Game.Hud', '{',
             '    /// <summary>The story campaign\'s texts (missions, radio, stages, choices, chapters, the dossier), English and Vietnamese.</summary>',
             '    public static class CampaignText', '    {',
             '        public static readonly Dictionary<string, (string en, string vi)> Table = new()', '        {']
    for key in sorted(kit.TEXTS):
        en, vi = kit.TEXTS[key]
        if '...' in en or '...' in vi:
            en, vi = en.replace('...', '…'), vi.replace('...', '…')
        lines.append(f'            [{cs_string(key)}] = ({cs_string(en)}, {cs_string(vi)}),')
    lines += ['        };', '', '        /// <summary>The speakers that have a portrait (Resources/UI/Portraits/&lt;id&gt;.png).</summary>',
              '        public static readonly string[] Speakers = { ' + ', '.join(cs_string(s) for s in story.SPEAKERS) + ' };',
              '    }', '}', '']
    open(TEXT_CS, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(lines))


def compact(value, indent=6):
    return json.dumps(value, ensure_ascii=False, separators=(', ', ': '))


def write_json(missions):
    chapters = [{'number': n, 'act': act, 'maps': maps, **({'general': g} if g else {})} for n, act, _, maps, g, _, _ in story.CHAPTERS]
    generals = [{'id': gid, 'deck': deck, 'supports': sup, 'style': style, 'stance': stance} for gid, deck, sup, style, stance, _, _ in story.GENERALS]
    out = ['// The story campaign (prompt 4): nine chapters in three acts, 90 main missions and 18 side missions.',
           '// Generated by Tools/campaign/build_campaign.py from act1.py, act2.py, act3.py and story.py: edit those, not this file.',
           '{', '  "chapters": [']
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
    for c in range(1, 10):
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
    # Chapter order: each chapter's main missions, then its side missions.
    missions.sort(key=lambda m: (m['chapter'], 1 if m.get('side') else 0, m['id']))
    for m in missions:
        if m.get('reversed'):
            reverse(m)
    check(missions)
    cs, ps, result = tune(missions)
    write_json(missions)
    write_texts()
    folder = sys.argv[sys.argv.index('--report') + 1] if '--report' in sys.argv else None
    rows = report(missions, cs, ps, result, folder) if folder else None
    at3 = rank_at(result, missions, 7)
    print(f'{len(missions)} missions, {len(kit.TEXTS)} texts; coin scale {cs:.0f}, blueprint scale {ps:.2f}; '
          f'deck rank {at3:.2f} as act III begins, {result[-1][1]:.2f} at the end')
    if rows:
        for r in rows:
            print('  chapter', r[0], 'coins', r[2], 'so far', r[3], 'prints', r[4], 'rank', round(r[6], 2), 'level', r[7])


if __name__ == '__main__':
    main()
