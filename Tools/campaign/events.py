"""Prompt 23 A: the library of mission events (campaign.json "eventLibrary"), read by MissionDef and run by MissionEventSystem.

A mission plays events by naming them: m['missionEvents'] = ['enemy_wave', {'id': 'general_field', 'trigger': {'progress': 0.5}}].
An object names a library entry and lays its fields over it (the trigger, params, notices, lines and reward field by field);
"as" gives a second copy of one entry its own id. A plan change names the stage it moves on to ("stage") or a new goal
("plan": the mission's fields to change). Part E puts events into every campaign mission (act10.py) with add() and add_stage().

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
        # Prompt 23 E.2: Brandt holds chapter 1's coast; his last battle as the enemy is its operation.
        'brandt': {'roster': ['armored_car', 'ifv', 'main_battle_tank', 'wheeled_gun', 'light_tank'], 'delivery': ['edge'],
                   'elite': 'main_battle_tank', 'lastChapter': 1},
        'varga': {'roster': ['light_tank', 'main_battle_tank', 'heavy_tank', 'tank_destroyer', 'twin_tank'], 'delivery': ['edge'],
                  'elite': 'heavy_tank', 'lastChapter': 12},
        'orlov': {'roster': ['mlrs', 'artillery', 'mortar_carrier', 'heavy_rocket_artillery', 'aa_vehicle'], 'delivery': ['edge'],
                  'elite': 'mlrs', 'lastChapter': 11},
        'kessler': {'roster': ['ifv', 'wheeled_gun', 'main_battle_tank', 'mine_layer', 'sam_launcher'], 'delivery': ['sea', 'rail', 'landing', 'edge'],
                    'elite': 'main_battle_tank', 'lastChapter': 12},
        'sen': {'roster': ['strike_drone', 'fpv_carrier', 'recon_drone', 'ew_jammer'], 'delivery': ['edge', 'air'],
                'elite': 'fpv_carrier', 'lastChapter': 5},
        # E.1: Raven takes the field in the Harpy (play-test 14: Morrigan was deleted; interlude III: he hunts Hawk in it).
        'quaden': {'roster': ['attack_helicopter', 'attack_jet', 'strike_drone'], 'delivery': ['edge'],
                   'elite': 'attack_jet', 'minis': ['mega_gunship'], 'lastChapter': 10},
        # Thorne's columns are the Accord's own, turned.
        'hung': {'roster': ['main_battle_tank', 'heavy_tank', 'ifv', 'aa_vehicle'], 'delivery': ['edge', 'landing'],
                 'elite': 'heavy_tank', 'lastChapter': 9},
        'aurel': {'roster': ['strike_drone', 'fpv_carrier', 'heavy_tank', 'ifv', 'railgun_truck'], 'delivery': ['pods', 'air', 'edge'],
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
    E('enemy_all_directions', 'EnemyWave', {'at': 200}, {'size': 12, 'directions': 4},
      notices={'warn': 'event.enemyWave.all.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.all.warn'}),
    E('landing_assault', 'EnemyWave', {'at': 120}, {'size': 6, 'delivery': ['sea', 'landing']},
      notices={'warn': 'event.enemyWave.sea.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.sea.warn'}),
    E('rail_reinforcements', 'EnemyWave', {'at': 180}, {'size': 6, 'delivery': ['rail']},
      notices={'warn': 'event.enemyWave.rail.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.rail.warn'}),
    E('drone_swarm', 'EnemyWave', {'at': 140}, {'size': 8, 'roster': ['strike_drone', 'fpv_carrier', 'recon_drone']},
      notices={'warn': 'event.enemyWave.drones.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.drones.warn'}),
    E('drop_pods', 'EnemyWave', {'at': 160}, {'size': 6, 'delivery': ['pods'], 'roster': ['heavy_tank', 'fpv_carrier', 'ifv']},
      notices={'warn': 'event.enemyWave.pods.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.pods.warn'}),
    E('air_wave', 'EnemyWave', {'at': 160}, {'size': 5, 'roster': ['attack_helicopter', 'attack_jet']},
      notices={'warn': 'event.enemyWave.air.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.air.warn'}),
    E('accord_wave', 'AllyWave', {'at': 240}),
    E('accord_relief', 'AllyWave', {'outnumbered': 1.6, 'at': 90}),
    # E.1 (chapter 1): the Accord's second landing wave, driving up the beach behind the brigade.
    E('accord_landing', 'AllyWave', {'at': 200}, {'delivery': 'edge'},
      notices={'start': 'event.allyWave.landing.start'}, lines={'start': 'radio.khai.ev.allyWave.landing.start'}),
    # E.1 (chapter 2): Thorne's army fights beside the brigade for the first time.
    E('thorne_support', 'AllyWave', {'at': 180}, {'roster': ['main_battle_tank', 'heavy_tank', 'ifv', 'aa_vehicle', 'tank_destroyer']},
      speaker='hung', notices={'start': 'event.allyWave.thorne.start'}, lines={'start': 'radio.hung.ev.allyWave.thorne.start'}),
    # E.1 (chapter 6): Brandt, on our side now, raises a line of towers in front of the brigade.
    E('brandt_line', 'AllyWave', {'at': 60}, {'line': True, 'roster': ['gun_turret', 'mg_bunker', 'gun_turret', 'aa_turret']},
      speaker='brandt', notices={'start': 'event.allyWave.brandt.start'}, lines={'start': 'radio.brandt.ev.allyWave.brandt.start'}),
    # E.1 (chapter 7): Veyra's militia, a couple of vehicles at a time from anywhere on our side of the city.
    E('militia', 'AllyWave', {'at': 80, 'every': 75, 'times': 4},
      {'count': 2, 'scatter': True, 'delivery': 'edge', 'roster': ['rocket_technical', 'zu23_technical', 'scout_jeep', 'armored_car']},
      notices={'start': 'event.allyWave.militia.start'}, lines={'start': 'radio.khai.ev.allyWave.militia.start'}),
    # Chapter 12's Total Offensive: every old ally at once (Brandt's armour, Venn's drones, Hawk's air wing, Mara's Behemoth), the
    # only allied wave as strong as the enemy's, under the enemy's cap instead of the allies'.
    E('total_offensive', 'AllyWave', {'after': 'enemy_all_directions', 'delay': 3},
      {'share': 1.0, 'of': 'enemy_all_directions', 'cap': 16, 'max': 16, 'delivery': 'edge',
       'rosters': ['heavy_tank,tank_destroyer,main_battle_tank', 'strike_drone,fpv_carrier', 'attack_jet,attack_helicopter',
                   'mara_behemoth']},
      priority=0, notices={'start': 'event.allyWave.offensive.start'}, lines={'start': 'radio.khai.ev.allyWave.offensive.start'}),
    # E.1 (chapter 7): Thorne's columns, turned (Accord vehicles now on the enemy's side).
    E('turned_columns', 'EnemyWave', {'at': 25}, {'size': 6, 'general': 'hung'},
      notices={'warn': 'event.enemyWave.turned.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.turned.warn'}),
    # E.1 (interlude II): Locust's hunting packs close on Venn from several sides.
    E('hunters', 'EnemyWave', {'at': 130}, {'size': 6, 'directions': 3, 'roster': ['strike_drone', 'fpv_carrier', 'recon_drone']},
      notices={'warn': 'event.enemyWave.hunters.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.hunters.warn'}),
    # D.1: fire support.
    E('enemy_barrage', 'Barrage', {'at': 200}, {'salvos': 3, 'radius': 18}),
    E('enemy_air_raid', 'AirRaid', {'at': 180}),
    E('counter_battery', 'CounterBattery', {'at': 60}, {'still': 20, 'lead': 5, 'cooldown': 45}),
    E('hawk_strike', 'AllyAirStrike', {'at': 200}),
    # E.1 (chapter 3): Orlov masses his guns on one place, announced in his own voice.
    E('orlov_barrage', 'Barrage', {'at': 170}, {'salvos': 5, 'radius': 14}, speaker='orlov',
      notices={'warn': 'event.barrage.orlov.warn'}, lines={'warn': 'radio.orlov.ev.barrage.orlov.warn'}),
    # E.1 (chapter 10): Raven's bombers come again and again.
    E('air_raids', 'AirRaid', {'at': 120, 'every': 110, 'times': 3}),
    # E.1 (chapter 11): the satellite's small test rod (prompt 18's big-attack rules, one rod: the warning, a ring, a kinetic hit).
    E('test_rod', 'OrbitalStrike', {'at': 160}, {'damage': 900, 'radius': 6, 'fall': 4, 'look': 'leviathan_shell'},
      notices={'warn': 'event.orbitalStrike.warn'}, lines={'warn': 'radio.linh.ev.orbitalStrike.warn'}),
    E('accord_artillery', 'AllyArtillery', {'at': 150}, {'salvos': 3}),
    # D.2: the general on the field (the push-back pays).
    E('general_field', 'GeneralField', {'progress': 0.4}, reward={'cp': 15, 'coins': 100}),
    # D.3: side objectives (optional, timed; E names the intel file an interception pays).
    E('intercept_files', 'SideObjective', {'at': 150}, {'type': 'intercept', 'count': 3, 'seconds': 120}, reward={'coins': 150}),
    # E.1 (chapter 4, the harbour option): the families' column to the ferries. E.1 (chapter 8, the rescue option): miners held in
    # a camp, who join the fight once freed.
    E('ferries', 'SideObjective', {'at': 90}, {'type': 'protect', 'count': 4, 'need': 3, 'seconds': 180}, reward={'coins': 200, 'prints': 2},
      notices={'start': 'event.sideObjective.ferries.start', 'done': 'event.sideObjective.ferries.done', 'fail': 'event.sideObjective.ferries.fail'},
      lines={'start': 'radio.linh.ev.sideObjective.ferries.start', 'done': 'radio.linh.ev.sideObjective.ferries.done',
             'fail': 'radio.linh.ev.sideObjective.ferries.fail'}),
    E('miners_held', 'SideObjective', {'at': 100}, {'type': 'rescue', 'count': 3, 'seconds': 150, 'size': 4,
                                                    'column': ['rocket_technical', 'scout_jeep', 'zu23_technical']}, reward={'join': True},
      notices={'start': 'event.sideObjective.miners.start', 'done': 'event.sideObjective.miners.done', 'fail': 'event.sideObjective.miners.fail'},
      lines={'start': 'radio.varro.ev.sideObjective.miners.start', 'done': 'radio.varro.ev.sideObjective.miners.done',
             'fail': 'radio.varro.ev.sideObjective.miners.fail'}),
    E('rescue_convoy', 'SideObjective', {'at': 120}, {'type': 'rescue', 'count': 3, 'seconds': 150, 'size': 4}, reward={'join': True}),
    E('protect_civilians', 'SideObjective', {'at': 90}, {'type': 'protect', 'count': 4, 'need': 3, 'seconds': 180}, reward={'coins': 200, 'prints': 2}),
    # D.4: the economy.
    E('neutral_convoy', 'NeutralConvoy', {'at': 120}, {'count': 3, 'cp': 8}),
    # E.1 (chapter 2): a neutral oil convoy crossing the desert.
    E('oil_convoy', 'NeutralConvoy', {'at': 110}, {'count': 4, 'cp': 10},
      notices={'start': 'event.neutralConvoy.oil.start'}, lines={'start': 'radio.linh.ev.neutralConvoy.oil.start'}),
    E('loot_drop', 'LootDrop', {'at': 100}, {'cp': 12}),
    E('loot_repair', 'LootDrop', {'at': 100}, {'repair': 0.3}),
    E('supply_raid', 'SupplyRaid', {'at': 240}, {'size': 4}),
    # D.5-D.6: logistics and intelligence.
    E('supply_drop', 'SupplyDrop', {'at': 180, 'every': 150, 'times': 2}),
    E('nadia_intel', 'IntelReveal', {'at': 90}, {'seconds': 8, 'radius': 30}),
    E('ew_blackout', 'Blackout', {'at': 150}, {'seconds': 20}),
    # D.7-D.8: a mini boss, a new plan (the mission names its stage or plan).
    E('mini_boss', 'MiniBoss', {'progress': 0.5}),
    # E.1 (chapter 8): Tartarus, Thorne's earth borer, comes up out of the ground mid-battle.
    E('tartarus', 'MiniBoss', {'progress': 0.45}, {'boss': ['earth_borer'], 'surface': True},
      notices={'warn': 'event.miniBoss.tartarus.warn'}, lines={'warn': 'radio.linh.ev.miniBoss.tartarus.warn'}),
    # E.1 (interlude III): the Harpy, with Raven aboard, hunting Hawk (play-test 14: Morrigan was deleted).
    E('harpy_hunt', 'MiniBoss', {'progress': 0.4}, {'boss': ['mega_gunship']},
      notices={'warn': 'event.miniBoss.harpy.warn'}, lines={'warn': 'radio.linh.ev.miniBoss.harpy.warn'}),
    E('plan_change', 'PlanChange', {'progress': 0.5}, priority=0),
    # D.9: the weather turns (20-30 s).
    E('snowstorm', 'WeatherShift', {'at': 180}, {'to': 'Snow', 'seconds': 25}),
    E('sea_fog', 'WeatherShift', {'at': 150}, {'to': 'Fog', 'seconds': 25}),
    E('storm_front', 'WeatherShift', {'at': 180}, {'to': 'Storm', 'seconds': 25}),
    E('nightfall', 'WeatherShift', {'at': 240}, {'to': 'Night', 'seconds': 30}),
    E('sandstorm', 'WeatherShift', {'at': 180}, {'to': 'Sandstorm', 'seconds': 25}),
    E('rain_sets_in', 'WeatherShift', {'at': 150}, {'to': 'Rain', 'seconds': 20}),
    E('skies_clear', 'WeatherShift', {'at': 200}, {'to': 'Clear', 'seconds': 25}),
    E('cloud_over', 'WeatherShift', {'at': 170}, {'to': 'Overcast', 'seconds': 20}),
    # E.1 (chapter 6, the Hollow Dam): Varga's ceasefire until noon; whoever fires first loses their reward.
    E('ceasefire', 'Ceasefire', {'at': 3}, {'seconds': 150, 'size': 4, 'enemyCp': 20}, reward={'cp': 20, 'coins': 150}, priority=0,
      notices={'start': 'event.ceasefire.start', 'end': 'event.ceasefire.end', 'broken': 'event.ceasefire.broken',
               'betrayed': 'event.ceasefire.betrayed'},
      lines={'start': 'radio.khai.ev.ceasefire.start', 'end': 'radio.varga.ev.ceasefire.end', 'broken': 'radio.varga.ev.ceasefire.broken',
             'betrayed': 'radio.khai.ev.ceasefire.betrayed'}),
]

KINDS = {'EnemyWave', 'AllyWave', 'Barrage', 'AirRaid', 'CounterBattery', 'AllyAirStrike', 'AllyArtillery', 'GeneralField', 'SideObjective',
         'NeutralConvoy', 'LootDrop', 'SupplyRaid', 'SupplyDrop', 'IntelReveal', 'Blackout', 'MiniBoss', 'PlanChange', 'WeatherShift',
         'Ceasefire', 'OrbitalStrike'}

# A.2: how many events a mission plays: a mission 2-4, a chapter's big operation 5-8, an interlude's mission 2-3. A side mission
# counts as a mission (E.1: every mission). An operation counts the events one play of it meets (its first stage, the longer
# of the two it chooses between, the stages after).
COUNTS = {'mission': (2, 4), 'operation': (5, 8), 'interlude': (2, 3)}
COUNT_CHECK = True

# E.1: the signature events each chapter must play somewhere (library ids), and E.2's general on the field (every chapter whose
# story names an enemy general; interlude II's enemy has none: the Locusts hunt on their own).
SIGNATURES = {
    1: ['landing_assault', 'accord_landing'],
    2: ['oil_convoy', 'thorne_support'],
    3: ['orlov_barrage', 'snowstorm'],
    4: ['landing_assault', 'rail_reinforcements', 'ferries'],
    5: ['drone_swarm', 'ew_blackout'],
    6: ['enemy_all_directions', 'ceasefire', 'brandt_line'],
    7: ['turned_columns', 'militia'],
    8: ['tartarus', 'miners_held'],
    9: ['landing_assault', 'sea_fog'],
    10: ['air_raids', 'hawk_strike', 'nightfall'],
    11: ['drop_pods', 'test_rod'],
    12: ['enemy_all_directions', 'total_offensive'],
    14: ['hunters'],
    15: ['harpy_hunt', 'nightfall'],
}
# E.1: the events tied to prompt 22's story choices, by the option that plays them (the chapter's choice decides whether they come).
CHOICE_EVENTS = {'ferries': 'harbour', 'miners_held': 'rescue'}
# D.6: the electronic storm is Venn's while she is the enemy and Aurel's.
BLACKOUT_GENERALS = {'sen', 'aurel'}


def library():
    return {'rules': RULES, 'events': EVENTS}


def add(mid, *refs):
    """Part E: a mission's events (library ids, or dicts naming one with overrides)."""
    kit.mission(mid).setdefault('missionEvents', []).extend(refs)


def add_stage(mid, stage, *refs):
    """Part E: the events of one stage of a staged mission (they run over that stage; their times count from its start)."""
    for s in kit.mission(mid)['stages']:
        if s['stage'] == stage:
            s.setdefault('missionEvents', []).extend(refs)
            return
    raise SystemExit(f'events: {mid} has no stage {stage}')


def ref_id(r):
    return r if isinstance(r, str) else r.get('id')


def played(m):
    """The events one play of a mission meets: its own, its stages' but for the stage it did not choose (the longer counted)."""
    stages = m.get('stages', [])
    alternatives = {c['next'] for s in stages for c in s.get('choices', [])}
    refs = list(m.get('missionEvents', []))
    longest = []
    for s in stages:
        own = s.get('missionEvents', [])
        if s['stage'] in alternatives:
            longest = own if len(own) > len(longest) else longest
        else:
            refs += own
    return refs + longest


def every_ref(m):
    """Every event a mission names (its own and every stage's), with the holder's weather and the stage it is in (or None)."""
    out = [(r, None) for r in m.get('missionEvents', [])]
    for s in m.get('stages', []):
        out += [(r, s) for r in s.get('missionEvents', [])]
    return out


def event_set(m):
    return tuple(sorted(ref_id(r) for r, _ in every_ref(m)))


def check(missions, vehicles, fail, interludes, chapters=None, weather=None, boss_of=None):
    """
    Every reference names a library event; a plan change says where it goes; the rosters are real vehicles; A.2's counts; E.1's
    signature events; E.2's general on the field in every chapter; E.3: no two missions in a row play one set of events; and each
    event can happen where it is put (a general to take the field, a base to raid, weather the battlefield has).
    """
    ids = {e['id'] for e in EVENTS}
    if len(ids) != len(EVENTS):
        fail('events: an id twice in the library')
    lib = {e['id']: e for e in EVENTS}
    for e in EVENTS:
        if e['kind'] not in KINDS:
            fail(f"events: {e['id']} has kind {e['kind']}")
        for key in ('roster', 'boss', 'column'):
            for v in e.get('params', {}).get(key, []):
                if v not in vehicles:
                    fail(f"events: {e['id']} names {v}, which balance.json does not define")
        for group in e.get('params', {}).get('rosters', []):
            for v in group.split(','):
                if v not in vehicles:
                    fail(f"events: {e['id']} names {v}, which balance.json does not define")
    for g, row in RULES['generals'].items():
        for v in row['roster'] + [row['elite']] + row.get('minis', []):
            if v not in vehicles:
                fail(f'events: general {g} sends {v}, which balance.json does not define')
    for v in RULES['genericRoster'] + RULES['accordRoster']:
        if v not in vehicles:
            fail(f'events: roster vehicle {v} is not in balance.json')
    kinds = {e['id']: e['kind'] for e in EVENTS}
    for m in missions:
        for r, stage in every_ref(m):
            rid = ref_id(r)
            if rid not in ids:
                fail(f"{m['id']}: event {rid} is not in the library")
            e = dict(lib[rid])
            if isinstance(r, dict):
                e['params'] = {**lib[rid].get('params', {}), **r.get('params', {})}
            params = e.get('params', {})
            if kinds.get(rid) == 'PlanChange' and (isinstance(r, str) or not ('stage' in r or 'plan' in r)):
                fail(f"{m['id']}: a plan change names its stage or its new plan")
            kind = kinds[rid]
            general = params.get('general') or m.get('general')
            if kind == 'GeneralField' and not general:
                fail(f"{m['id']}: {rid} has no general to take the field")
            if kind == 'MiniBoss':
                if not params.get('boss') and not general:
                    fail(f"{m['id']}: {rid} has no mini boss and no general to send one")
                bosses = boss_of(m) if boss_of else set()
                if set(params.get('boss', [])) & bosses:
                    fail(f"{m['id']}: {rid} brings the mission's own boss")
            if kind == 'SupplyRaid' and m.get('playerBase', 'None') == 'None':
                fail(f"{m['id']}: {rid} raids a base the mission does not give the player")
            if kind == 'Blackout' and general not in BLACKOUT_GENERALS:
                fail(f"{m['id']}: the electronic storm is Venn's or Aurel's, not {general}'s")
            if kind == 'WeatherShift' and weather is not None:
                to = params.get('to')
                own = m['weather']
                if to == own or to not in weather.get(m['map'], {to}):
                    fail(f"{m['id']}: {rid} turns {own} to {to}, which {m['map']} cannot show or already has")
            if rid in CHOICE_EVENTS and m.get('option') != CHOICE_EVENTS[rid]:
                fail(f"{m['id']}: {rid} belongs to the story choice's {CHOICE_EVENTS[rid]} option")
        if COUNT_CHECK:
            total = len(played(m))
            lo, hi = COUNTS['operation' if m.get('operation') else 'interlude' if m['chapter'] in interludes else 'mission']
            if not lo <= total <= hi:
                fail(f"{m['id']}: {total} events (want {lo}-{hi})")
    if not COUNT_CHECK:
        return
    # E.1: the chapters' signature events; E.2: a general on the field in every chapter with one (not only in a choice's option).
    for c, sig in SIGNATURES.items():
        named = {ref_id(r) for m in missions if m['chapter'] == c for r, _ in every_ref(m)}
        for rid in sig:
            if rid not in named:
                fail(f'chapter {c}: E.1 wants {rid} in one of its missions')
    for c, general in (chapters or {}).items():
        if not general:
            continue
        if not any(kinds[ref_id(r)] == 'GeneralField' for m in missions if m['chapter'] == c and not m.get('branch') for r, _ in every_ref(m)):
            fail(f'chapter {c}: E.2 wants the enemy general on the field in one of its missions')
    # E.3: no two missions in a row with one set of events (in the order of play; a side mission after the one it follows).
    order = [m for m in missions if not m.get('side')]
    by_id = {m['id']: m for m in missions}
    pairs = list(zip(order, order[1:])) + [(by_id[m['after']], m) for m in missions if m.get('side') and m.get('after') in by_id]
    for a, b in pairs:
        if event_set(a) == event_set(b):
            fail(f"{a['id']} and {b['id']} play one set of events ({', '.join(event_set(a))})")
