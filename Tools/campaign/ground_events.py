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
