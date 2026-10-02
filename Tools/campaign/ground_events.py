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
