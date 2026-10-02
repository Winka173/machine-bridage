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
