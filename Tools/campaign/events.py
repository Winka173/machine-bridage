"""Prompt 23 A: the library of mission events (campaign.json "eventLibrary"), read by MissionDef and run by MissionEventSystem.

A mission plays events by naming them: m['missionEvents'] = ['enemy_wave', {'id': 'general_field', 'trigger': {'progress': 0.5}}].
An object names a library entry and lays its fields over it (the trigger, params, notices, lines and reward field by field);
"as" gives a second copy of one entry its own id. A plan change names the stage it moves on to ("stage") or a new goal
("plan": the mission's fields to change). Part E (putting events into every campaign mission) uses add() below.

Every number is a starting point for the testing phase's five-seed sweeps (DECISIONS 23A).
"""

import campaign_kit as kit

# The C.3 table: directions an enemy wave comes from, seconds of warning, an allied wave's share of an enemy wave's strength
# (prompt 13's combat value), the enemy waves' size, elites, most allied waves a mission, a general's escorts, and the step
# added to the act for the general's elite-or-mini-boss rule (D.2: a mini boss once act + step reaches miniFrom).
RULES = {
    'difficulty': {
        'Easy': {'directions': [1, 2], 'warning': 15, 'ally': 0.70, 'waveScale': 0.7, 'elites': False, 'allyWaves': -1, 'escorts': 2, 'step': 0},
        'Normal': {'directions': [2, 2], 'warning': 10, 'ally': 0.50, 'waveScale': 1.0, 'elites': False, 'allyWaves': -1, 'escorts': 3, 'step': 1},
        'Hard': {'directions': [2, 3], 'warning': 8, 'ally': 0.30, 'waveScale': 1.15, 'elites': False, 'allyWaves': -1, 'escorts': 4, 'step': 2},
        'VeryHard': {'directions': [3, 4], 'warning': 6, 'ally': 0.15, 'waveScale': 1.3, 'elites': True, 'allyWaves': 1, 'escorts': 5, 'step': 3},
    },
    # C.1: what each general sends and how it comes; D.2: the card whose elite they drive, the chapter of their last battle.
    'generals': {
        'varga': {'roster': ['light_tank', 'main_battle_tank', 'heavy_tank', 'tank_destroyer', 'twin_tank'], 'delivery': ['edge'],
                  'elite': 'heavy_tank', 'lastChapter': 12},
        'orlov': {'roster': ['mlrs', 'artillery', 'mortar_carrier', 'heavy_rocket_artillery', 'aa_vehicle'], 'delivery': ['edge'],
                  'elite': 'mlrs', 'lastChapter': 11},
        'kessler': {'roster': ['ifv', 'wheeled_gun', 'main_battle_tank', 'mine_layer', 'sam_launcher'], 'delivery': ['sea', 'rail', 'landing', 'edge'],
                    'elite': 'main_battle_tank', 'lastChapter': 12},
        'sen': {'roster': ['strike_drone', 'fpv_carrier', 'lancet_truck', 'recon_drone', 'ew_jammer'], 'delivery': ['edge', 'air'],
                'elite': 'fpv_carrier', 'lastChapter': 5},
        'quaden': {'roster': ['attack_helicopter', 'gunship_heli', 'attack_jet', 'strike_drone'], 'delivery': ['edge'],
                   'elite': 'attack_jet', 'lastChapter': 10},
        # Thorne's columns are the Accord's own, turned.
        'hung': {'roster': ['main_battle_tank', 'heavy_tank', 'ifv', 'bmpt', 'aa_vehicle'], 'delivery': ['edge', 'landing'],
                 'elite': 'heavy_tank', 'lastChapter': 9},
        'aurel': {'roster': ['strike_drone', 'fpv_carrier', 'heavy_tank', 'bmpt', 'railgun_truck'], 'delivery': ['pods', 'air', 'edge'],
                  'elite': 'heavy_tank', 'lastChapter': 12},
    },
    'genericRoster': ['armored_car', 'ifv', 'light_tank', 'main_battle_tank', 'aa_vehicle', 'mlrs'],
    'accordRoster': ['main_battle_tank', 'ifv', 'armored_car', 'aa_vehicle', 'tank_destroyer', 'light_tank'],
    # C.4: reinforcements alive at once, outside the army caps (a low-end phone's budget: to measure in the testing phase).
    'caps': {'enemy': 16, 'ally': 10},
    'nearSight': 45,
    'miniFrom': 4,
    'retreatAt': 0.3,
    'weatherSight': {'Clear': 1.0, 'Overcast': 1.0, 'Rain': 0.9, 'Storm': 0.8, 'Snow': 0.85, 'Fog': 0.7, 'Sandstorm': 0.75, 'Night': 0.75},
}


def E(eid, kind, trigger, params=None, **more):
    e = {'id': eid, 'kind': kind, 'trigger': trigger}
    if params:
        e['params'] = params
    e.update(more)
    return e


EVENTS = [
    # C: reinforcements.
    E('enemy_wave', 'EnemyWave', {'at': 150}, {'size': 6}),
    E('enemy_wave_late', 'EnemyWave', {'progress': 0.6}, {'size': 8}),
    E('enemy_counterattack', 'EnemyWave', {'progress': 0.8}, {'size': 10}),
    E('enemy_all_directions', 'EnemyWave', {'at': 200}, {'size': 12, 'directions': 4}),
    E('landing_assault', 'EnemyWave', {'at': 120}, {'size': 6, 'delivery': ['sea', 'landing']}),
    E('rail_reinforcements', 'EnemyWave', {'at': 180}, {'size': 6, 'delivery': ['rail']}),
    E('drone_swarm', 'EnemyWave', {'at': 140}, {'size': 8, 'roster': ['strike_drone', 'fpv_carrier', 'lancet_truck', 'recon_drone']}),
    E('drop_pods', 'EnemyWave', {'at': 160}, {'size': 6, 'delivery': ['pods'], 'roster': ['heavy_tank', 'bmpt', 'fpv_carrier', 'ifv']}),
    E('air_wave', 'EnemyWave', {'at': 160}, {'size': 5, 'roster': ['attack_helicopter', 'gunship_heli', 'attack_jet']}),
    E('accord_wave', 'AllyWave', {'at': 240}),
    E('accord_relief', 'AllyWave', {'outnumbered': 1.6, 'at': 90}),
    # Chapter 12's Total Offensive: the only allied wave as strong as the enemy's.
    E('total_offensive', 'AllyWave', {'progress': 0.7}, {'share': 1.0, 'of': 'enemy_all_directions'}, priority=0),
    # D.1: fire support.
    E('enemy_barrage', 'Barrage', {'at': 200}, {'salvos': 3, 'radius': 18}),
    E('enemy_air_raid', 'AirRaid', {'at': 180}),
    E('counter_battery', 'CounterBattery', {'at': 60}, {'still': 20, 'lead': 5, 'cooldown': 45}),
    E('hawk_strike', 'AllyAirStrike', {'at': 200}),
    E('accord_artillery', 'AllyArtillery', {'at': 150}, {'salvos': 3}),
    # D.2: the general on the field (the push-back pays).
    E('general_field', 'GeneralField', {'progress': 0.4}, reward={'cp': 15, 'coins': 100}),
    # D.3: side objectives (optional, timed; E names the intel file an interception pays).
    E('intercept_files', 'SideObjective', {'at': 150}, {'type': 'intercept', 'count': 3, 'seconds': 120}, reward={'coins': 150}),
    E('rescue_convoy', 'SideObjective', {'at': 120}, {'type': 'rescue', 'count': 3, 'seconds': 150, 'size': 4}, reward={'join': True}),
    E('protect_civilians', 'SideObjective', {'at': 90}, {'type': 'protect', 'count': 4, 'need': 3, 'seconds': 180}, reward={'coins': 200, 'prints': 2}),
    # D.4: the economy.
    E('neutral_convoy', 'NeutralConvoy', {'at': 120}, {'count': 3, 'cp': 8}),
    E('loot_drop', 'LootDrop', {'at': 100}, {'cp': 12}),
    E('loot_repair', 'LootDrop', {'at': 100}, {'repair': 0.3}),
    E('supply_raid', 'SupplyRaid', {'at': 240}, {'size': 4}),
    # D.5-D.6: logistics and intelligence.
    E('supply_drop', 'SupplyDrop', {'at': 180, 'every': 150, 'times': 2}),
    E('nadia_intel', 'IntelReveal', {'at': 90}, {'seconds': 8, 'radius': 30}),
    E('ew_blackout', 'Blackout', {'at': 150}, {'seconds': 20}),
    # D.7-D.8: a mini boss, a new plan (the mission names its stage or plan).
    E('mini_boss', 'MiniBoss', {'progress': 0.5}),
    E('plan_change', 'PlanChange', {'progress': 0.5}, priority=0),
    # D.9: the weather turns (20-30 s).
    E('snowstorm', 'WeatherShift', {'at': 180}, {'to': 'Snow', 'seconds': 25}),
    E('sea_fog', 'WeatherShift', {'at': 150}, {'to': 'Fog', 'seconds': 25}),
    E('storm_front', 'WeatherShift', {'at': 180}, {'to': 'Storm', 'seconds': 25}),
    E('nightfall', 'WeatherShift', {'at': 240}, {'to': 'Night', 'seconds': 30}),
    E('sandstorm', 'WeatherShift', {'at': 180}, {'to': 'Sandstorm', 'seconds': 25}),
    E('rain_sets_in', 'WeatherShift', {'at': 150}, {'to': 'Rain', 'seconds': 20}),
    E('skies_clear', 'WeatherShift', {'at': 200}, {'to': 'Clear', 'seconds': 25}),
]

KINDS = {'EnemyWave', 'AllyWave', 'Barrage', 'AirRaid', 'CounterBattery', 'AllyAirStrike', 'AllyArtillery', 'GeneralField', 'SideObjective',
         'NeutralConvoy', 'LootDrop', 'SupplyRaid', 'SupplyDrop', 'IntelReveal', 'Blackout', 'MiniBoss', 'PlanChange', 'WeatherShift'}

# A.2: how many events a mission plays: a mission 2-4, a chapter's big operation 5-8, an interlude's mission 2-3. Part E switches
# the count check on once every mission has its events.
COUNTS = {'mission': (2, 4), 'operation': (5, 8), 'interlude': (2, 3)}
COUNT_CHECK = False


def library():
    return {'rules': RULES, 'events': EVENTS}


def add(mid, *refs):
    """Part E: a mission's events (library ids, or dicts naming one with overrides)."""
    kit.mission(mid).setdefault('missionEvents', []).extend(refs)


def check(missions, vehicles, fail, interludes):
    """Every reference names a library event; a plan change says where it goes; the rosters are real vehicles; A.2's counts once E is in."""
    ids = {e['id'] for e in EVENTS}
    if len(ids) != len(EVENTS):
        fail('events: an id twice in the library')
    for e in EVENTS:
        if e['kind'] not in KINDS:
            fail(f"events: {e['id']} has kind {e['kind']}")
        for key in ('roster',):
            for v in e.get('params', {}).get(key, []):
                if v not in vehicles:
                    fail(f"events: {e['id']} names {v}, which balance.json does not define")
    for g, row in RULES['generals'].items():
        for v in row['roster'] + [row['elite']]:
            if v not in vehicles:
                fail(f'events: general {g} sends {v}, which balance.json does not define')
    for v in RULES['genericRoster'] + RULES['accordRoster']:
        if v not in vehicles:
            fail(f'events: roster vehicle {v} is not in balance.json')
    kinds = {e['id']: e['kind'] for e in EVENTS}
    for m in missions:
        holders = [(m, m.get('missionEvents', []))] + [(s, s.get('missionEvents', [])) for s in m.get('stages', [])]
        total = 0
        for holder, refs in holders:
            total += len(refs)
            for r in refs:
                rid = r if isinstance(r, str) else r.get('id')
                if rid not in ids:
                    fail(f"{m['id']}: event {rid} is not in the library")
                if kinds.get(rid) == 'PlanChange' and (isinstance(r, str) or not ('stage' in r or 'plan' in r)):
                    fail(f"{m['id']}: a plan change names its stage or its new plan")
        if COUNT_CHECK and not m.get('side'):
            lo, hi = COUNTS['operation' if m.get('operation') else 'interlude' if m['chapter'] in interludes else 'mission']
            if not lo <= total <= hi:
                fail(f"{m['id']}: {total} events (want {lo}-{hi})")
