"""Prompt 23 E: the mission events of every campaign mission, chapter by chapter (the library is events.py).

E.1: each chapter's missions play events in its spirit, A.2's counts (a mission 2-4, a big operation 5-8, an interlude's mission
2-3; a side mission counts as a mission), with the signature events the spec names for each chapter and interludes II and III
(events.SIGNATURES; the ferries and the held miners come in the option of the chapter's story choice that plays them). E.2: every
chapter with an enemy general has the general take the field in one of its missions. E.3: no two missions in a row play one set
of events. H.8: the six story moments' follow-up lines (DialogueRules.MomentKeys has the keys). The build checks all of it
(events.check).

A stage's events run over that stage (their times count from its start); an operation's own over the whole operation. Events go
on an operation's first stage and on the stages after its choice, never on the two it chooses between, so every play meets them.
Every number is a starting point for the testing phase's five-seed sweeps (DECISIONS 23E).
"""

import campaign_kit as kit
from campaign_kit import T
from events import add, add_stage


def general(name=None, **params):
    """The enemy general takes the field (D.2): the mission's own, or <name> (a general the mission is not tied to)."""
    if name:
        params['general'] = name
    return {'id': 'general_field', 'params': params} if params else 'general_field'


def intercept(intel):
    """D.3's convoy of files, carrying one of prompt 22 D.7's intel files (it goes into the dossier once the trucks are stopped)."""
    return {'id': 'intercept_files', 'reward': {'intel': intel}}


def sized(eid, size):
    return {'id': eid, 'params': {'size': size}}


def at(eid, seconds):
    return {'id': eid, 'trigger': {'at': seconds}}


def fog():
    """Fog rolling in (the sea fog's words: every battlefield it turns on is by the water or in a valley)."""
    return 'sea_fog'


# ====================================================================== chapter 1: Coast of Fire (Brandt)
# The enemy's landing craft strike back from the sea; the Accord's second landing wave comes up the beach; Brandt comes out of
# his fortress once (c1m08).

add('c1m01', sized('landing_assault', 4), 'accord_landing')
add('c1m02', 'landing_assault', 'nadia_intel', 'rain_sets_in')
add('c1m03', 'enemy_wave', 'loot_drop', 'accord_wave')
add('c1s1', 'nadia_intel', 'skies_clear')
add('c1m04', 'enemy_wave_late', 'supply_drop', 'rain_sets_in')
add('c1m05', 'accord_artillery', 'loot_repair')
add('c1m06', 'enemy_barrage', 'accord_relief', 'skies_clear')
add('c1m08', general('brandt'), intercept('c1.inspection'), 'enemy_wave')
add('c1m09', 'enemy_air_raid', 'accord_wave', fog())
add('c1m10', 'hawk_strike', 'supply_drop')
add_stage('c1m10', 'depot', 'enemy_wave')
add_stage('c1m10', 'bastion', 'accord_artillery')
add_stage('c1m10', 'counter', 'enemy_counterattack', 'accord_landing')

# ====================================================================== chapter 2: Black Gold (Varga)
# Neutral oil convoys cross the sand; Thorne's army fights beside the brigade for the first time (c2m06); Varga shows himself
# at Dunebreak (c2m04).

add('c2m01', 'oil_convoy', 'enemy_wave', 'sandstorm')
add('c2m02', 'enemy_wave_late', 'loot_drop', 'accord_wave')
add('c2m03', 'neutral_convoy', 'enemy_barrage')
add('c2s1', 'nadia_intel', 'loot_drop')
add('c2m04', general(), intercept('c2.order'), 'oil_convoy')
add('c2m05', 'hawk_strike', 'skies_clear')
add('c2m06', 'thorne_support', 'enemy_wave', 'nadia_intel')
add('c2m07', 'enemy_counterattack', 'supply_drop')
add('c2s2', 'air_wave', 'loot_repair')
add('c2m08', 'enemy_wave', 'thorne_support', 'supply_raid')
add('c2m09', 'enemy_barrage', 'accord_artillery', 'loot_drop')
add('c2m10', 'sandstorm')
add_stage('c2m10', 'fields', 'oil_convoy')
add_stage('c2m10', 'counter', 'accord_wave')
add('c2m11', 'thorne_support', 'hawk_strike')
add_stage('c2m11', 'wells', 'oil_convoy')
add_stage('c2m11', 'oasis', 'enemy_wave')
add_stage('c2m11', 'caravan', 'enemy_barrage')
add_stage('c2m11', 'behemoth', 'skies_clear')

# ====================================================================== chapter 3: The Long Winter (Orlov)
# Orlov masses his guns on one place and answers our guns; snowstorms roll in mid-battle; Orlov on the field for the duel (c3m09).

add('c3m01', 'orlov_barrage', 'accord_wave')
add('c3m02', 'counter_battery', 'enemy_wave', 'nadia_intel')
add('c3m11', 'orlov_barrage', 'loot_drop', 'skies_clear')
add('c3m03', 'snowstorm', 'enemy_wave_late', 'supply_drop')
add('c3s1', 'nadia_intel', 'snowstorm')
add('c3m04', 'orlov_barrage', 'accord_relief', 'snowstorm')
add('c3m05', 'snowstorm', 'hawk_strike')
add('c3m06', 'counter_battery', intercept('c3.tables'), 'enemy_wave')
add('c3m12', 'enemy_wave', 'snowstorm', 'supply_drop')
add('c3m07', 'orlov_barrage', 'protect_civilians', 'snowstorm')
add('c3s2', 'accord_artillery', 'loot_repair')
add('c3m08', 'enemy_air_raid', 'snowstorm')
add('c3m09', general(), 'orlov_barrage', 'counter_battery')
add('c3m10', 'orlov_barrage', 'snowstorm')
add_stage('c3m10', 'radar', 'counter_battery')
add_stage('c3m10', 'fortress', 'hawk_strike')
add_stage('c3m10', 'gate', 'enemy_counterattack', 'accord_wave')

# ====================================================================== interlude I: Blueprints (Varga)
# The Foundry's files leave in Hegemon trucks; Varga comes for his blueprints in person (i1m04).

add('i1m01', intercept('i1.initials'), 'enemy_wave')
add('i1m02', 'nadia_intel', 'rain_sets_in')
add('i1m03', 'loot_repair', 'accord_artillery')
add('i1m04', general(), 'supply_raid', 'supply_drop')

# ====================================================================== chapter 4: Iron Harbor (Kessler)
# Landing ships from the sea and Kessler's trains; the families' column to the ferries in the harbour option of the chapter's
# choice (c4m18), Kessler himself running for the boats in the other (c4m17), and on the field in the storm duel (c4m09).

add('c4m01', 'rail_reinforcements', 'accord_wave', 'rain_sets_in')
add('c4m02', 'landing_assault', 'nadia_intel')
add('c4m03', 'landing_assault', 'hawk_strike', 'skies_clear')
add('c4s1', 'rail_reinforcements', 'loot_drop')
add('c4m04', 'nadia_intel', 'rail_reinforcements')
add('c4m05', 'landing_assault', 'accord_artillery')
add('c4m12', intercept('c4.balance'), 'rail_reinforcements', fog())
add('c4m07', 'landing_assault', 'supply_raid', 'accord_relief')
add('c4s2', 'loot_drop', 'cloud_over')
add('c4m16', 'rail_reinforcements', 'nadia_intel', 'rain_sets_in')
add('c4m08', 'rail_reinforcements', 'enemy_barrage')
add('c4m13', 'enemy_wave_late', 'supply_drop', 'skies_clear')
add('c4m09', general(), 'landing_assault', 'hawk_strike')
add('c4m10', 'rail_reinforcements')
add_stage('c4m10', 'yard', 'landing_assault')
add_stage('c4m10', 'quay', 'accord_wave')
# D.8, used once at a turning point: as the chapter's choice comes up, Kessler runs for the harbour and Kade sends the brigade
# after the rail yard instead of holding on.
add('c4m14', 'rail_reinforcements', 'enemy_air_raid',
    {'id': 'plan_change', 'trigger': {'progress': 0.6}, 'plan': {'goal': 'Capture', 'points': ['town']},
     'lines': {'start': 'radio.khai.ev.planChange.kessler.start'}})
add('c4m17', general(), 'landing_assault')
add('c4m18', 'ferries', 'enemy_barrage', 'accord_relief')
add('c4m06', 'landing_assault', 'skies_clear')
add('c4m15', 'landing_assault', 'accord_wave', fog())
add('c4m11', 'landing_assault', 'hawk_strike', 'supply_drop')
add_stage('c4m11', 'lighthouse', fog())
add_stage('c4m11', 'village', 'accord_wave')
add_stage('c4m11', 'leviathan', 'accord_artillery')

# ====================================================================== chapter 5: Burning Canopy (Venn)
# Drone swarms from several directions; Venn's electronic storms; Venn on the field for the duel (c5m09).

add('c5m01', 'drone_swarm', 'accord_wave')
add('c5m02', 'ew_blackout', 'drone_swarm', 'nadia_intel')
add('c5m03', 'air_wave', 'rain_sets_in')
add('c5s1', 'nadia_intel', 'storm_front')
add('c5m04', 'drone_swarm', 'supply_drop', 'cloud_over')
add('c5m08', 'ew_blackout', 'protect_civilians', 'accord_relief')
add('c5m12', 'drone_swarm', 'loot_drop', 'storm_front')
add('c5m05', 'ew_blackout', 'hawk_strike')
add('c5m06', 'drone_swarm', 'accord_artillery', 'enemy_air_raid')
add('c5m11', intercept('c5.notebook'), 'ew_blackout')
add('c5m07', 'air_wave', 'drone_swarm', 'supply_drop')
add('c5s2', 'drone_swarm', 'supply_raid')
add('c5m13', 'drone_swarm', 'ew_blackout', 'accord_wave')
add('c5m09', general(), 'drone_swarm', 'hawk_strike')
add('c5m10', 'drone_swarm', 'ew_blackout')
add_stage('c5m10', 'causeways', 'nadia_intel')
add_stage('c5m10', 'plant', 'accord_artillery')
add_stage('c5m10', 'swarm', {'id': 'drone_swarm', 'params': {'size': 10, 'directions': 4}, 'trigger': {'at': 60}})
add_stage('c5m10', 'mothership', 'hawk_strike')

# ====================================================================== chapter 6: Counterstrike (Varga)
# Counterattacks from every direction; Brandt, on our side now, raises lines of towers; the Hollow Dam's ceasefire clock
# (c6m14); Varga on the field at the dam (c6m06).

add('c6m01', sized('enemy_all_directions', 9), 'brandt_line', 'supply_drop')
add('c6m13', 'enemy_counterattack', 'accord_wave', 'skies_clear')
add('c6m02', 'enemy_wave', 'brandt_line', fog())
add('c6m16', intercept('c6.board'), 'enemy_wave_late', 'skies_clear')
add('c6m11', sized('enemy_all_directions', 9), 'accord_relief')
add('c6m03', 'enemy_barrage', 'brandt_line', 'hawk_strike')
add('c6s1', 'air_wave', 'loot_repair')
add('c6m05', 'accord_artillery', 'snowstorm')
add('c6m12', 'landing_assault', 'nadia_intel', 'storm_front')
add('c6m08', 'accord_landing', 'loot_drop')
add('c6m07', 'enemy_counterattack', 'brandt_line')
add('c6m04', 'enemy_wave', 'accord_wave', fog())
add('c6m06', general(), 'supply_raid', 'supply_drop')
add('c6s2', 'nadia_intel', 'rain_sets_in')
add('c6m09', 'enemy_barrage', 'brandt_line', 'snowstorm')
add('c6m15', sized('enemy_all_directions', 9), 'nadia_intel')
add('c6m14', 'ceasefire', 'supply_drop', 'cloud_over')
add('c6m10', 'enemy_all_directions', 'brandt_line')
add_stage('c6m10', 'crest', 'accord_artillery')
add_stage('c6m10', 'monster', 'hawk_strike')
add_stage('c6m10', 'relief', 'enemy_counterattack', 'supply_drop')

# H.8, the Hollow Dam: Varga gives his word, Kade answers, then Kade calls the ceasefire: three lines of one story moment
# (Kade's answer comes right after Varga's line now, not 8 s in).
for r in kit.mission('c6m14')['radio']:
    if r['key'] == 'radio.khai.c6m14.2':
        r['at'] = 2

# ====================================================================== interlude II: The Queen's Choice
# Locust's hunting packs close on Venn from several sides in every mission (the Locusts themselves are two missions' bosses);
# the story names no general for the interlude, so none takes the field.

add('i2m01', 'hunters', 'rain_sets_in')
add('i2m02', 'hunters', 'supply_drop')
add('i2m03', 'hunters', 'accord_relief', 'nightfall')
add('i2m04', 'hunters', 'nadia_intel')

# ====================================================================== chapter 7: Veyra (Aurel's guard; Thorne turns)
# The city's militia joins in, a couple of vehicles at a time; in the operation Thorne turns, his columns come at us under the
# enemy's flag and Thorne takes the field himself (the betrayal stage).

add('c7m01', 'militia', 'enemy_wave')
add('c7m03', 'militia', 'enemy_barrage', 'skies_clear')
add('c7s1', 'nadia_intel', 'rain_sets_in')
add('c7m16', 'militia', 'enemy_wave_late', 'nadia_intel')
add('c7m04', 'protect_civilians', 'militia', 'ew_blackout')
add('c7m05', 'militia', 'accord_artillery')
add('c7m07', 'enemy_wave', 'nadia_intel', 'rain_sets_in')
add('c7m12', 'militia', 'loot_drop', fog())
add('c7m15', 'nadia_intel', 'militia')
add('c7m13', 'militia', 'hawk_strike')
add('c7m14', 'enemy_wave_late', 'supply_raid', 'militia')
add('c7m02', intercept('c7.letters'), 'ew_blackout')
add('c7m17', 'militia', 'enemy_barrage', 'rain_sets_in')
add('c7m06', 'drop_pods', 'militia', 'supply_drop')
add('c7m11', 'air_wave', 'militia')
add('c7m09', 'enemy_wave', 'accord_artillery', 'cloud_over')
add('c7m18', 'drop_pods', 'militia', 'ew_blackout')
add('c7m08', 'militia', 'enemy_air_raid', 'rain_sets_in')
add('c7m10', 'militia')
add_stage('c7m10', 'bridgeheads', 'nadia_intel')
add_stage('c7m10', 'palace', 'accord_artillery')
add_stage('c7m10', 'betrayal', 'turned_columns', general('hung', form='elite'))
add_stage('c7m10', 'nemesis', 'hawk_strike')

# ====================================================================== chapter 8: Underworld (Thorne)
# Tartarus comes up out of the ground mid-battle before it is hunted down (c8m05); the held miners in the rescue option of the
# chapter's choice (c8m13); Thorne on the field at Red Rock (c8m03).

add('c8m01', 'enemy_wave', 'loot_drop')
add('c8m02', 'tartarus', 'supply_drop')
add('c8m03', general(), 'enemy_wave', 'sandstorm')
add('c8s1', 'nadia_intel', 'sandstorm')
add('c8m11', 'tartarus', 'loot_drop', 'sandstorm')
add('c8m04', 'enemy_counterattack', 'supply_drop', 'skies_clear')
add('c8m05', 'accord_artillery', 'rain_sets_in')
add('c8m06', 'enemy_wave_late', 'accord_relief', fog())
add('c8m12', intercept('c8.letter'), 'nadia_intel')
add('c8m07', 'supply_raid', 'hawk_strike')
add('c8s2', 'air_wave', 'loot_drop')
add('c8m08', 'nadia_intel', 'enemy_barrage', 'skies_clear')
add('c8m09', 'enemy_barrage', 'accord_artillery', 'sandstorm')
add('c8m13', 'miners_held', 'enemy_wave')
add('c8m14', 'enemy_counterattack', 'supply_drop', 'sandstorm')
add('c8m10', 'enemy_wave', 'hawk_strike')
add_stage('c8m10', 'fields', 'nadia_intel')
add_stage('c8m10', 'refinery', 'accord_artillery')
add_stage('c8m10', 'counter', 'enemy_counterattack', 'supply_drop')
# Play-test 14: Tartarus tunnels up under the fight when Moloch is down to 60 %.
add_stage('c8m10', 'inferno', {'id': 'tartarus', 'trigger': {'bossHealth': 0.6}})

# ====================================================================== chapter 9: Rough Water (Thorne)
# Landings from the sea and sea fog rolling in; Thorne on the field in the fog at Ironport (c9m06).

add('c9m01', 'landing_assault', 'accord_wave')
add('c9m02', 'landing_assault', fog(), 'nadia_intel')
add('c9m03', 'enemy_barrage', fog())
add('c9s1', 'landing_assault', 'loot_drop')
add('c9m04', 'landing_assault', 'hawk_strike', 'skies_clear')
add('c9m05', 'accord_artillery', 'storm_front')
add('c9m11', intercept('c9.timetable'), fog())
add('c9m06', general(), 'landing_assault', 'supply_drop')
add('c9m12', 'landing_assault', 'loot_drop', 'storm_front')
add('c9m13', 'landing_assault', 'accord_relief', 'skies_clear')
add('c9m07', 'protect_civilians', fog(), 'enemy_wave')
add('c9s2', 'landing_assault', 'nadia_intel')
add('c9m08', 'supply_raid', fog())
add('c9m14', 'landing_assault', 'supply_drop', fog())
add('c9m09', 'landing_assault', 'hawk_strike', fog())
add('c9m10', 'landing_assault', 'hawk_strike')
add_stage('c9m10', 'yard', 'nadia_intel')
add_stage('c9m10', 'factories', 'accord_wave')
add_stage('c9m10', 'tempest', 'accord_artillery')
add_stage('c9m10', 'quay', 'enemy_counterattack')

# ====================================================================== interlude III: Hawk and Raven (Raven)
# The Harpy hunts Hawk, with Raven himself aboard in the relief (i3m03); the light goes as they search.

add('i3m01', 'air_wave', 'nadia_intel')
add('i3m02', 'nightfall', 'supply_drop')
add('i3m03', general(), 'accord_relief')
add('i3m04', 'harpy_hunt', 'nightfall', 'supply_drop')

# ====================================================================== chapter 10: War in the Sky (Raven)
# Raven's bombers come again and again; Hawk strikes back; the light goes over Skyhold; Raven on the field for the duel (c10m09),
# in a jet of his own after the Harpy's loss.

add('c10m01', 'air_raids', 'hawk_strike')
add('c10m02', intercept('c10.test'), 'nightfall')
add('c10m11', 'air_raids', 'accord_relief', 'nightfall')
add('c10m03', 'air_raids', 'hawk_strike', 'protect_civilians')
add('c10m04', 'air_wave', 'hawk_strike')
add('c10s1', 'air_raids', 'loot_drop')
add('c10m05', 'hawk_strike', 'nightfall')
add('c10m06', 'air_raids', 'nadia_intel', 'nightfall')
add('c10m13', 'air_wave', 'hawk_strike', 'snowstorm')
add('c10m08', 'hawk_strike', 'supply_drop')
add('c10m14', 'air_raids', 'accord_wave', 'nightfall')
add('c10m07', 'air_wave', 'hawk_strike', 'nightfall')
add('c10s2', 'nadia_intel', 'nightfall')
add('c10m12', 'hawk_strike', 'loot_repair')
add('c10m09', general(form='elite'), 'air_raids', 'hawk_strike')
add('c10m10', 'air_raids', 'hawk_strike')
add_stage('c10m10', 'radars', 'nadia_intel')
add_stage('c10m10', 'airship', 'accord_artillery')
add_stage('c10m10', 'crow', 'air_wave')
add_stage('c10m10', 'counter', 'enemy_counterattack', 'nightfall')

# ====================================================================== chapter 11: Skygate (Aurel; Orlov's last guns)
# Drop pods falling from orbit; the first satellite test-fires a small rod; Orlov on the field in the snow before his last
# battle (c11m03).

add('c11m01', 'drop_pods', 'accord_wave')
add('c11m02', intercept('c11.memo'), 'ew_blackout')
add('c11m03', general('orlov'), 'drop_pods', 'snowstorm')
add('c11s1', 'drop_pods', 'loot_drop')
add('c11m04', 'test_rod', 'nadia_intel')
add('c11m05', 'orlov_barrage', 'counter_battery', 'drop_pods')
add('c11m06', 'drop_pods', 'test_rod', 'supply_drop')
add('c11m07', 'supply_raid', 'drop_pods')
add('c11m11', 'drop_pods', 'hawk_strike', 'skies_clear')
add('c11m08', 'air_wave', 'snowstorm')
add('c11m09', 'drop_pods', 'ew_blackout', 'accord_artillery')
add('c11m12', 'drop_pods', 'skies_clear')
add('c11m13', 'test_rod', 'nadia_intel', 'snowstorm')
add('c11m10', 'drop_pods', 'hawk_strike')
add_stage('c11m10', 'radar', 'ew_blackout')
add_stage('c11m10', 'fortress', 'accord_artillery')
add_stage('c11m10', 'gate', 'test_rod', 'enemy_counterattack')

# ====================================================================== chapter 12: Helion (Aurel; Varga and Kessler's last)
# Enemy reinforcements from every direction; in the operation's Varga stage, the Total Offensive: every old ally at once, as
# strong as the enemy's wave from every side it answers; Varga on the field before his last battle (c12m03).

add('c12m01', sized('enemy_all_directions', 10), 'accord_wave')
add('c12m05', 'drop_pods', 'hawk_strike')
add('c12m03', general(), 'enemy_all_directions', 'accord_artillery')
add('c12m02', 'landing_assault', 'hawk_strike', fog())
add('c12m04', 'enemy_all_directions', 'drop_pods', 'ew_blackout')
add('c12m07', 'drop_pods', 'nadia_intel', 'sandstorm')
add('c12m06', intercept('c12.last'), 'enemy_all_directions', 'accord_relief')
add('c12m08', 'test_rod', 'drop_pods', 'skies_clear')
add('c12m09', 'enemy_all_directions', 'supply_raid', 'accord_wave')
add('c12m10', 'hawk_strike', 'ew_blackout')
add_stage('c12m10', 'approach', 'nadia_intel')
# The enemy's wave from every side is warned as the stage begins; the Total Offensive answers it a few seconds after it lands.
add_stage('c12m10', 'command', at('enemy_all_directions', 1), 'total_offensive')
add_stage('c12m10', 'countdown', 'drop_pods')

# ====================================================================== H.8: the story moments' follow-up lines
# Each moment plays two or three lines in a row (DialogueRules.MomentKeys and StoryKeys). Two moments had one line only; these are
# their answers, a few seconds after.


def stage_line(mid, stage, speaker, key, en, vi, at_seconds):
    for s in kit.mission(mid)['stages']:
        if s['stage'] == stage:
            s['events'].append({'at': str(at_seconds), 'kind': 'Radio', 'key': T(f'radio.{speaker}.{mid}.{key}', en, vi)})
            return
    raise SystemExit(f'act10: {mid} has no stage {stage}')


stage_line('c5m10', 'swarm', 'khai', 's3b', 'Understood, Doctor. Brigade, dig in and hold.', 'Rõ, tiến sĩ. Lữ đoàn, bám trụ và giữ vững.', 3)
stage_line('c9m10', 'tempest', 'linh', 's4b', 'That is {@lyhan} on the bridge. He came to finish it himself.',
           'Đó là {@lyhan} trên đài chỉ huy. Ông ta tự tới để kết thúc.', 2)

# ====================================================================== the new events' words (E.1)
# Notices ("event.<kind>.<variant>.<moment>", placeholders {seconds} and {dir}) and lines ("radio.<speaker>.ev.<kind>...") of the
# library entries prompt 23 E added; the story's names as {@id} tokens. At most two lines of the dialogue on the narrowest screen.

WORDS = {
    # C: the chapters' reinforcements.
    'event.enemyWave.sea.warn': ("Enemy landing craft from the sea in {seconds} s, {dir}", "Xuồng đổ bộ địch từ biển tới sau {seconds} giây, {dir}"),
    'event.enemyWave.rail.warn': ("An enemy train brings reinforcements in {seconds} s, {dir}", "Tàu hỏa địch chở viện quân tới sau {seconds} giây, {dir}"),
    'event.enemyWave.drones.warn': ("A drone swarm closes in {seconds} s, {dir}", "Bầy drone ập tới sau {seconds} giây, {dir}"),
    'event.enemyWave.pods.warn': ("Drop pods falling from orbit in {seconds} s, {dir}", "Khoang đổ bộ rơi từ quỹ đạo sau {seconds} giây, {dir}"),
    'event.enemyWave.air.warn': ("Enemy aircraft inbound in {seconds} s, {dir}", "Máy bay địch tới sau {seconds} giây, {dir}"),
    'event.enemyWave.all.warn': ("Enemy reinforcements from every direction in {seconds} s", "Viện quân địch từ mọi hướng tới sau {seconds} giây"),
    'event.enemyWave.turned.warn': ("Accord columns under the enemy's flag in {seconds} s, {dir}", "Đoàn quân Accord mang cờ địch tới sau {seconds} giây, {dir}"),
    'event.enemyWave.hunters.warn': ("Locust's hunting packs close in {seconds} s, from several sides", "Các bầy săn của Locust ập tới sau {seconds} giây, từ nhiều phía"),
    'radio.linh.ev.enemyWave.sea.warn': ("Landing craft off the beach. They are coming back at us from the sea.", "Xuồng đổ bộ ngoài bãi. Chúng đánh ngược vào ta từ biển."),
    'radio.linh.ev.enemyWave.rail.warn': ("A train on the line, heavy and fast. Kessler is sending more.", "Có tàu trên tuyến ray, nặng và nhanh. Kessler đang gửi thêm quân."),
    'radio.linh.ev.enemyWave.drones.warn': ("Swarm on the scope, splitting up. They will come from everywhere.", "Bầy drone trên màn hình, đang tách ra. Chúng sẽ tới từ khắp nơi."),
    'radio.linh.ev.enemyWave.pods.warn': ("Pods falling from orbit. Watch the sky and keep moving.", "Khoang đổ bộ đang rơi từ quỹ đạo. Để ý bầu trời và di chuyển liên tục."),
    'radio.linh.ev.enemyWave.air.warn': ("Aircraft inbound, low over the ridge. Anti-air, get ready.", "Máy bay địch đang tới, bay thấp qua sườn núi. Phòng không, chuẩn bị."),
    'radio.linh.ev.enemyWave.all.warn': ("Contacts on every side. They are throwing everything at us.", "Có địch ở mọi phía. Chúng đang dồn mọi thứ vào ta."),
    'radio.linh.ev.enemyWave.turned.warn': ("Accord markings on those tanks. They are {@lyhan}'s now.", "Xe tăng kia mang phù hiệu Accord. Giờ chúng là của {@lyhan}."),
    'radio.linh.ev.enemyWave.hunters.warn': ("Locust has sent its packs. They are coming for Venn from all sides.", "Locust đã thả các bầy săn. Chúng nhắm vào Venn từ mọi phía."),
    'event.allyWave.landing.start': ("The Accord's second landing wave is coming ashore", "Đợt đổ bộ thứ hai của Accord đang lên bờ"),
    'event.allyWave.thorne.start': ("{@lyhan}'s army is coming in beside us", "Đạo quân của {@lyhan} đang tiến vào sát cánh cùng ta"),
    'event.allyWave.brandt.start': ("Brandt's engineers are raising a line of towers ahead of us", "Công binh của Brandt đang dựng một tuyến tháp trước mặt ta"),
    'event.allyWave.militia.start': ("{@lamthanh}'s militia joins the fight", "Dân quân {@lamthanh} vào trận cùng ta"),
    'event.allyWave.offensive.start': ("All-out attack: every old ally is joining the fight", "Tổng tấn công: mọi đồng minh cũ cùng vào trận"),
    'radio.khai.ev.allyWave.landing.start': ("The second wave is ashore. Push up the beach with them.", "Đợt hai đã lên bờ. Cùng họ tiến lên khỏi bãi biển."),
    'radio.hung.ev.allyWave.thorne.start': ("Titan's army, {@khai}. We fight together today.", "Đạo quân Titan đây, {@khai}. Hôm nay ta cùng chiến đấu."),
    'radio.brandt.ev.allyWave.brandt.start': ("I know every wall Varga wants back. He will not get this one.", "Tôi thuộc từng bức tường Varga muốn đòi lại. Bức này hắn không lấy được."),
    'radio.khai.ev.allyWave.militia.start': ("{@lamthanh}'s own people are joining in. Cover them.", "Chính người dân {@lamthanh} đang vào trận. Yểm trợ cho họ."),
    'radio.khai.ev.allyWave.offensive.start': ("All-out attack! Brandt, Venn, {@dieuhau}, {@mai}: everything, now!", "Tổng tấn công! Brandt, Venn, {@dieuhau}, {@mai}: tất cả, ngay bây giờ!"),
    # D.1-D.2: Orlov's guns, the test rod, Brandt on the field.
    'event.barrage.orlov.warn': ("Orlov's guns are massing on our position: move in {seconds} s", "Pháo của Orlov đang dồn vào vị trí ta: rời đi trong {seconds} giây"),
    'radio.orlov.ev.barrage.orlov.warn': ("Fire mission. All batteries on one grid square. Yours.", "Nhiệm vụ bắn. Toàn bộ khẩu đội vào một ô lưới. Ô của ngươi."),
    'event.orbitalStrike.warn': ("Satellite test fire: a rod falls on our position in {seconds} s", "Vệ tinh bắn thử: một thanh vonfram rơi vào vị trí ta sau {seconds} giây"),
    'radio.linh.ev.orbitalStrike.warn': ("The satellite is locking on to us. A small test rod. Scatter anyway!", "Vệ tinh đang khóa vào ta. Một thanh thử loại nhỏ. Vẫn phải tản ra!"),
    'radio.brandt.ev.generalField.start': ("Walls are not enough today. I will hold this coast myself.", "Hôm nay tường thành không đủ. Ta sẽ tự tay giữ bờ biển này."),
    'radio.brandt.ev.generalField.retreat': ("Back to the fortress. The walls will finish this.", "Rút về pháo đài. Tường thành sẽ kết thúc chuyện này."),
    'radio.brandt.ev.miniBoss.start': ("Bring out the Bastion's little sister.", "Đưa em gái của Bastion ra đây."),
    # D.3-D.4: the ferries, the miners, the oil convoy.
    'event.sideObjective.ferries.start': ("Side objective: see the families to the ferries ({seconds} s)", "Mục tiêu phụ: đưa các gia đình ra tới phà ({seconds} giây)"),
    'event.sideObjective.ferries.done': ("The families are aboard the ferries", "Các gia đình đã lên phà"),
    'event.sideObjective.ferries.fail': ("The families did not reach the ferries", "Các gia đình không tới được phà"),
    'radio.linh.ev.sideObjective.ferries.start': ("Families heading for the ferries. Keep the road open for them.", "Các gia đình đang ra phà. Giữ đường thông cho họ."),
    'radio.linh.ev.sideObjective.ferries.done': ("They are aboard. The ferries are casting off.", "Họ lên phà rồi. Phà đang nhổ neo."),
    'radio.linh.ev.sideObjective.ferries.fail': ("We lost the road to the quay. They did not make it.", "Ta mất con đường ra cầu tàu. Họ không kịp tới."),
    'event.sideObjective.miners.start': ("Side objective: free the miners held in the camp ({seconds} s)", "Mục tiêu phụ: giải thoát thợ mỏ bị giữ trong lán ({seconds} giây)"),
    'event.sideObjective.miners.done': ("The miners are free and join the fight", "Thợ mỏ đã được giải thoát và vào trận cùng ta"),
    'event.sideObjective.miners.fail': ("The miners were moved out of reach", "Thợ mỏ đã bị đưa đi mất"),
    'radio.varro.ev.sideObjective.miners.start': ("Miners held in that camp. Break the guard and they are with us.", "Thợ mỏ bị giữ trong lán kia. Phá vòng canh là họ theo ta."),
    'radio.varro.ev.sideObjective.miners.done': ("They are out, and they want to fight. Give them a road.", "Họ ra được rồi, và họ muốn chiến đấu. Mở đường cho họ."),
    'radio.varro.ev.sideObjective.miners.fail': ("They moved the miners. We were too slow.", "Chúng đã chuyển thợ mỏ đi. Ta chậm quá."),
    'event.neutralConvoy.oil.start': ("A neutral oil convoy is crossing: whoever knocks it out takes its CP", "Một đoàn xe dầu trung lập đi ngang: bên nào hạ được sẽ nhận CP"),
    'radio.linh.ev.neutralConvoy.oil.start': ("Oil tankers, no flag, crossing the sand. The oil goes to whoever stops them.", "Xe chở dầu không cờ đang băng qua cát. Dầu thuộc về bên nào chặn được."),
    # D.7: Tartarus and the Harpy (play-test 14: Morrigan was deleted).
    'event.miniBoss.tartarus.warn': ("The ground is shaking: Tartarus surfaces in {seconds} s", "Mặt đất rung chuyển: Tartarus trồi lên sau {seconds} giây"),
    'radio.linh.ev.miniBoss.tartarus.warn': ("Seismic readings under us. Something is digging up. Tartarus!", "Địa chấn ngay dưới chân ta. Có thứ gì đang đào lên. Tartarus!"),
    'event.miniBoss.harpy.warn': ("The Harpy is coming over us in {seconds} s, {dir}", "Harpy bay tới phía ta sau {seconds} giây, {dir}"),
    'radio.linh.ev.miniBoss.harpy.warn': ("{@quaden}'s gunship on the scope. The Harpy is hunting {@dieuhau}.", "Pháo hạm bay của {@quaden} trên radar. Harpy đang săn {@dieuhau}."),
    # D.8: the one plan change (c4m14).
    'radio.khai.ev.planChange.kessler.start': ("Kessler is running for the harbour. New orders: take the rail yard, now.", "Kessler đang chạy ra bến cảng. Lệnh mới: chiếm bãi đường ray, ngay."),
    # E.1: the Hollow Dam's ceasefire.
    'event.ceasefire.start': ("Ceasefire for {seconds} s: do not fire on Varga's column", "Ngừng bắn {seconds} giây: không bắn vào cánh quân của Varga"),
    'event.ceasefire.end': ("The ceasefire is over: Varga's column is coming", "Hết giờ ngừng bắn: cánh quân của Varga đang tới"),
    'event.ceasefire.broken': ("We fired first: the ceasefire's reward is lost", "Ta đã bắn trước: mất phần thưởng ngừng bắn"),
    'event.ceasefire.betrayed': ("The enemy broke the ceasefire: its reward is ours", "Địch đã phá lệnh ngừng bắn: phần thưởng thuộc về ta"),
    'radio.khai.ev.ceasefire.start': ("All units, hold your fire. Nobody shoots at Varga's column.", "Toàn đơn vị, ngừng bắn. Không ai được bắn vào cánh quân của Varga."),
    'radio.varga.ev.ceasefire.end': ("Time is up, Colonel. My guns are free again.", "Hết giờ rồi, đại tá. Pháo của tôi được bắn lại rồi."),
    'radio.varga.ev.ceasefire.broken': ("You fired first, Colonel. I had hoped for better.", "Ông bắn trước, đại tá. Tôi đã mong ông khá hơn thế."),
    'radio.khai.ev.ceasefire.betrayed': ("They broke the ceasefire. Return fire!", "Chúng phá lệnh ngừng bắn. Bắn trả!"),
}
for _key, (_en, _vi) in WORDS.items():
    T(_key, _en, _vi)
