"""Prompt 31 L3 (DECISIONS "Prompt 31 L3"): the five FIRST events of the sheet "Biến cố", the missions that play them and the
prebuilt ground states they switch (nav_states.py checks those over the map data; Sim/Navigation/NavStates.cs builds them).

Every event here warns 8-12 s ahead (MissionEventSystem clamps the lead for these kinds) with a system notice and its places
on the minimap; the line is extra. Each happens on the step its trigger decides (a time, the enemy spotting the player, another
event), so a replay of the same seed and commands meets it on the same step; any ground it changes is a site of the mission's
"navStates", switched at a tick boundary.
"""

import campaign_kit as kit
import events
from events import E

# The kinds of prompt 31 L3 (MissionEventKind in EventDefs.cs).
events.KINDS |= {'GroundChange', 'SandstormTurn', 'CityBlackout', 'BetrayalWarning', 'OrbitalPods'}

LIBRARY = []


def library(*entries):
    LIBRARY.extend(entries)
    events.EVENTS.extend(entries)


def nav_site(mid, site):
    kit.mission(mid).setdefault('navStates', []).append(site)


def replace_event(mid, old, new, stage=None):
    """Swaps one of a mission's (or a stage's) events for another in its place (the counts stay)."""
    m = kit.mission(mid)
    holder = m if stage is None else next(s for s in m['stages'] if s['stage'] == stage)
    refs = holder.get('missionEvents', [])
    for i, r in enumerate(refs):
        if events.ref_id(r) == old:
            refs[i] = new
            return
    raise SystemExit(f'ground_events: {mid} plays no {old}')


# ---------------------------------------------------------------------- Bão cát đổi hướng (the sandstorm turns): c2m06, c12m07
# The wind swings round and the storm rolls over the half of the map the player's main group stands in (the existing weather
# sight: SimWorld.StormSight); the far half clears a little where the storm was already over everything. No ground changes.
library(E('sandstorm_turn', 'SandstormTurn', {'at': 200}, {'half': 'player', 'sight': 0.6, 'clear': 1.0, 'seconds': 25, 'hold': 150},
          lead=10))
# Red Rock is already in a sandstorm (c2m06's weather): the turn thickens it over our half and thins it over theirs.
events.add('c2m06', {'id': 'sandstorm_turn', 'params': {'sight': 0.65, 'clear': 1.25}})
# Dunebreak at night (c12m07): the sandstorm that rolled over the whole map now comes over one half, after the wind turns.
replace_event('c12m07', 'sandstorm', {'id': 'sandstorm_turn', 'trigger': {'at': 180}})


# ---------------------------------------------------------------------- Báo động nhà máy (the factory alarm): i1m01
# The infiltration of the Foundry: once the enemy sees one of the brigade's vehicles (from 30 s in), the alarm sounds, the
# rolling-mill gate (the lane east of the casting hall, x 42-50) shuts 10 s later, and the garrison's reinforcements follow.
# The gate's two states are built at load; the lanes round the mill stay open (nav_states.py, NavStates.Validate).
library(E('factory_alarm', 'GroundChange', {'spotted': True, 'at': 30}, {'navSite': 'mill_gate', 'navState': 'shut'}, lead=10,
          notices={'warn': 'event.groundChange.alarm.warn', 'start': 'event.groundChange.alarm.start'},
          lines={'warn': 'radio.linh.ev.groundChange.alarm.warn'}),
        E('alarm_wave', 'EnemyWave', {'after': 'factory_alarm', 'delay': 4}, {'size': 6},
          notices={'warn': 'event.enemyWave.alarm.warn'}, lines={'warn': 'radio.linh.ev.enemyWave.alarm.warn'}))
nav_site('i1m01', {'id': 'mill_gate', 'initial': 'open', 'states': [
    {'name': 'open'},
    {'name': 'shut', 'blocks': [{'x': 46, 'z': 0, 'w': 10, 'd': 2}]}]})
# The garrison's wave comes on the alarm, not on a clock (the sheet: one mistake changes the battle).
replace_event('i1m01', 'enemy_wave', 'factory_alarm')
events.add('i1m01', 'alarm_wave')


# ---------------------------------------------------------------------- Mất điện thành phố (the city blackout): c7m11
# The capital's grid fails: the street lights go out (night rolls in over 25 s, the weather sight of Night) and every tower on
# the grid, the player's and the enemy's (MissionEventSystem.GridTowers: radars, searchlights, lasers, shields, fire control),
# is knocked out for 90 s until the backup power comes on. No ground changes.
library(E('city_blackout', 'CityBlackout', {'at': 240}, {'seconds': 25, 'outage': 90}, lead=10))
events.add('c7m11', 'city_blackout')


# ---------------------------------------------------------------------- Phản bội (the betrayal, warned): c7m10
# Thorne turns when the Square's 180 s hold ends (the betrayal stage's Betrayal at its start). New: the warning before it, in
# the Square's last seconds: his columns marked on the minimap and Nadia's line 10 s ahead (the trigger at 168 s, the lead
# 10 s), so the turn is a betrayal the player saw coming, not a coin toss.
library(E('betrayal_warning', 'BetrayalWarning', {'at': 168}, lead=10, priority=0,
          notices={'warn': 'event.betrayalWarning.warn'}, lines={'warn': 'radio.linh.ev.betrayalWarning.warn'}))
events.add_stage('c7m10', 'square', 'betrayal_warning')


# ---------------------------------------------------------------------- Khoang đổ bộ quỹ đạo (the orbital drop pods): c11m10
# In the Skygate's fortress stage Daedalus drops three pods that stand up as new enemy structures (its existing pod drop's warning
# rings, then a gun turret, a missile battery and an anti-air turret). Each lands on a prebuilt site ("clear" -> "landed", the
# tower's square: SimWorld.StaticFootprint, max(length, width) x 0.8) checked at load; a tower destroyed opens its site again.
PODS = [('pod_site_1', 20, 60, 'gun_turret', 4.0), ('pod_site_2', 60, 20, 'missile_battery', 7.2), ('pod_site_3', -10, 90, 'aa_turret', 3.6)]
library(E('orbital_pods', 'OrbitalPods', {'at': 60}, {'sites': [p[0] for p in PODS], 'towers': [p[3] for p in PODS], 'fall': 6}, lead=10,
          notices={'warn': 'event.orbitalPods.warn', 'start': 'event.orbitalPods.start'}, lines={'warn': 'radio.linh.ev.orbitalPods.warn'}))
for site, x, z, _, size in PODS:
    nav_site('c11m10', {'id': site, 'initial': 'clear', 'states': [
        {'name': 'clear'},
        {'name': 'landed', 'blocks': [{'x': x, 'z': z, 'w': size, 'd': size}]}]})
events.add_stage('c11m10', 'fortress', 'orbital_pods')


# Prompt 31 L4 (c5m03's rule droneCanopy): Venn's swarms come as the warned drone_swarm in place of the air wave.
replace_event('c5m03', 'air_wave', 'drone_swarm')


# Prompt 31 L4 (c6m14's rule ceasefireFaction): Varga's sworn column is a ceasefire faction for the whole battle.
replace_event('c6m14', 'ceasefire', {'id': 'ceasefire', 'params': {'seconds': 900, 'faction': True}})


# ====================================================================== Prompt 31 L5: the LATER events (DECISIONS "Prompt 31 L5")
# The same rules as the FIRST ones: prebuilt ground states, a switch at a tick boundary, a way round in every state (checked at
# build time here and at load in the game), nobody trapped, warned 8-12 s ahead with the places on the minimap. GroundChange's
# "cycle" walks a site's states in order (the tide in and out; "wrap": false stops at the last), "text" picks the words by the
# state coming in ("event.groundChange.<text>.<state>.warn").

# ---------------------------------------------------------------------- Triều lên/xuống (the tide): c1m01
# Every 150 s (the sheet: 120-180) the tide turns on the landing beach: at high water the eastern shoal (the fords below the
# cliffs, x -10..142) floods and the beach road along it closes; at low water it dries and opens again. The fords by the
# player's camp (the utility slots at x -73 and -45) stay out of it, and the dunes keep every point joined at high water.
# c9m02 (the same beach) is a reversed battlefield: nav states there are refused by the build, so it keeps its events.
library(E('tide_turn', 'GroundChange', {'at': 150, 'every': 150}, {'navSite': 'shoal', 'cycle': True, 'text': 'tide'}, lead=10))
nav_site('c1m01', {'id': 'shoal', 'initial': 'low', 'states': [
    {'name': 'low'},
    {'name': 'high', 'blocks': [{'x': 66, 'z': -130, 'w': 152, 'd': 12}]}]})
events.add('c1m01', 'tide_turn')


# ---------------------------------------------------------------------- Cầu sập (the bridge falls): i2m03
# Lý Hàn's sappers bring the east bridge down at 150 s of the hold (x 122 over the river, z -25..25): the great bridge (the point
# held) and the west ford stay. A time mark only: the sheet's "or when shot enough" wants a bridge with health, and the bridge
# is a prop the game never damages (1,000,000 hp), so it is left out. c7m17 (the capital) is reversed: refused by the build.
# The interlude plays three events at most: the bridge takes nightfall's place (hunters, chapter 14's signature, and the
# Accord's relief stay).
library(E('bridge_collapse', 'GroundChange', {'at': 150}, {'navSite': 'east_bridge', 'navState': 'down', 'text': 'bridge'}, lead=10))
nav_site('i2m03', {'id': 'east_bridge', 'initial': 'standing', 'states': [
    {'name': 'standing'},
    {'name': 'down', 'blocks': [{'x': 122, 'z': 0, 'w': 9, 'd': 50}]}]})
replace_event('i2m03', 'nightfall', 'bridge_collapse')


# ---------------------------------------------------------------------- Cần cẩu đổ (the crane falls): c4m05, c4m02
# The dock's neutral gantry crane (-7.5, 131.25 on Ironport) can be shot down (an attack order or a strike; 2,000 hp). Once it is
# destroyed (the new trigger "propDown": the prop of that def nearest the point, within 8 m), it buckles: 10 s later its boom
# comes down east along the quay (x 2..32, z 128.5..133.5) and closes the quay's middle lane for good; the lanes north and south
# of it stay. It falls along the quay, not south, so the rail line at z 106.8 (c4m05's train, the rail deliveries) is never
# crossed. The crane's own footprint opens as any destroyed building's does.
library(E('crane_fall', 'GroundChange', {'propDown': {'def': 'gantry_crane', 'x': -7.5, 'z': 131.25}},
          {'navSite': 'crane', 'navState': 'fallen', 'text': 'crane'}, lead=10))
for mid in ('c4m05', 'c4m02'):
    nav_site(mid, {'id': 'crane', 'initial': 'standing', 'states': [
        {'name': 'standing'},
        {'name': 'fallen', 'blocks': [{'x': 17, 'z': 131, 'w': 30, 'd': 5}]}]})
    events.add(mid, 'crane_fall')


# ---------------------------------------------------------------------- Hồ băng nứt (the lake ice cracks): c3m04
# The Whiteout's frozen lake (the town point at (0, 0), the ice 30 m round it) is the outpost held for 180 s. From 20 s in (warned
# 10 s), a vehicle that breaks ice (VehicleDef.BreaksIce: its weight class, Medium or Heavy, from its armour and health or the
# data's "weightClass"; never its CP) that has been on the ice 10 s is slowed 40 % for 8 s as it gives, and again every 10 s it
# stays; both sides alike. No ground closes (a slow, never a trap), so there is no nav site.
events.KINDS |= {'IceCrack'}
library(E('ice_crack', 'IceCrack', {'at': 20}, {'x': 0, 'z': 0, 'radius': 30, 'seconds': 10, 'slow': 0.4, 'slowFor': 8}, lead=10))
events.add('c3m04', 'ice_crack')


# ---------------------------------------------------------------------- Đập nứt (the dam cracks): c6m10, c6m14
# The Hollow Dam's wall cracks and the river below it rises in three steps (the sheet's three prebuilt levels, "cycle" without
# "wrap": the water never goes down in the battle): "rising" floods the middle of the southern ford (x -10..18, z -105..-95; its
# north and south edges still cross), "high" the whole ford (z -114..-86), "flood" also the low banks either side of the river
# below the bridge (x -21..-15 and 11..17, z -84..-20, clear of the town's outpost slot at (17, -13)). The bridge (the town
# point) and the dam's crest road stay above the water: every level keeps the three points and both camps joined
# (nav_states.py; the game checks again at load).
DAM_FORD = {'x': 4, 'z': -100, 'w': 28, 'd': 28}
DAM_SITE = {'id': 'flood', 'initial': 'dry', 'states': [
    {'name': 'dry'},
    {'name': 'rising', 'blocks': [{'x': 4, 'z': -100, 'w': 28, 'd': 10}]},
    {'name': 'high', 'blocks': [DAM_FORD]},
    {'name': 'flood', 'blocks': [DAM_FORD, {'x': -18, 'z': -52, 'w': 6, 'd': 64}, {'x': 14, 'z': -52, 'w': 6, 'd': 64}]}]}
library(E('dam_breach', 'GroundChange', {'at': 300, 'every': 150, 'times': 3}, {'navSite': 'flood', 'cycle': True, 'wrap': False, 'text': 'dam'},
          lead=10))
# c6m10 (the operation on the dam): the wall cracks five minutes in, under the general's assault (7 events of 5-8).
nav_site('c6m10', DAM_SITE)
events.add('c6m10', 'dam_breach')
# c6m14 (the evacuation under the ceasefire, 900 s): sooner, so the three levels come inside its clock (4 events of 2-4).
nav_site('c6m14', DAM_SITE)
events.add('c6m14', {'id': 'dam_breach', 'trigger': {'at': 240, 'every': 150, 'times': 3}})


# ---------------------------------------------------------------------- Sập hầm mỏ (the mine collapses): c8m10
# Kronos pit's two adits through the rock, mirrored across the pit: the north-east one (x 28..42, z 52..64, the enemy's side) is
# open when the battle starts and the south-west one (x -42..-28, z -64..-52, by our camp) is sealed. At 240 s the north-east
# adit caves in and the miners blast the south-west one open (one switch of one site: "north" -> "south"; the minimap marks
# both). Neither adit is the only way between its two sides of the rock, so each state keeps the battlefield joined.
library(E('mine_collapse', 'GroundChange', {'at': 240}, {'navSite': 'adits', 'navState': 'south', 'text': 'mine'}, lead=10))
nav_site('c8m10', {'id': 'adits', 'initial': 'north', 'states': [
    {'name': 'north', 'blocks': [{'x': -35, 'z': -58, 'w': 15, 'd': 6}]},
    {'name': 'south', 'blocks': [{'x': 35, 'z': 58, 'w': 15, 'd': 6}]}]})
events.add('c8m10', 'mine_collapse')


# ---------------------------------------------------------------------- Dung nham (the lava flow): c5m10
# Three minutes in, a lava flow from the ridge's vents comes down over the west causeway road where it leaves the west causeway's
# field for the north-east (x -62..-38, z 74..82) and the lane stays under lava. The field keeps its way out south (the road
# back to the ridge's foot), the north spur keeps its own way east (a sliver by the flow, under the 6-cell allowance, is put
# out at the switch).
library(E('lava_flow', 'GroundChange', {'at': 180}, {'navSite': 'lava', 'navState': 'cut', 'text': 'lava'}, lead=10))
nav_site('c5m10', {'id': 'lava', 'initial': 'clear', 'states': [
    {'name': 'clear'},
    {'name': 'cut', 'blocks': [{'x': -50, 'z': 78, 'w': 24, 'd': 8}]}]})
events.add('c5m10', 'lava_flow')


# ---------------------------------------------------------------------- Cháy rừng (the forest fire): c5m13
# The sheet's riskiest event, made safe the same way: no fire that spreads cell by cell (a simulation of its own, chance in its
# spread, its cost), but a prebuilt wind-driven front. At 150 s of the temple's hold a fire catches in the jungle south-west of
# it and the south wind drives it north in four 12 m strips (x -85..-35, from z -46 to 2), one every 30 s: the strip burning is
# closed ground (whoever is on it burns, 40 a second for 6 s, and is put out of it), its smoke drifts north (two clouds that
# stop every side's sight), the strip behind it is ash and open again; then it burns out. The next strip is warned 10 s ahead
# on the minimap. Every strip leaves the temple and both camps joined (nav_states.py; the game again at load).
events.KINDS |= {'ForestFire'}
FIRE_STRIPS = [-40, -28, -16, -4]
library(E('forest_fire', 'ForestFire', {'at': 150}, {'navSite': 'fire', 'every': 30, 'dps': 40, 'burn': 6, 'windX': 0, 'windZ': 1},
          lead=10))
nav_site('c5m13', {'id': 'fire', 'initial': 'none', 'states': [{'name': 'none'}] +
         [{'name': f'front{k + 1}', 'blocks': [{'x': -60, 'z': z, 'w': 50, 'd': 12}]} for k, z in enumerate(FIRE_STRIPS)] +
         [{'name': 'out'}]})
events.add('c5m13', 'forest_fire')
