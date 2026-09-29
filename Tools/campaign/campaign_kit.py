"""The toolkit the campaign chapters are written with (see build_campaign.py).

Every mission is written in the standard frame of the battlefields: side 0's camp in the south-west
corner (-108.75, -108.75), side 1's in the north-east, the objectives west (north-west), town
(the centre) and east (south-east). A reversed mission (the player coming back from the other side)
is written as the player sees it and turned half round here, so "near the player's camp" stays
near the player's camp.

Texts are collected as they are written: T(key, en, vi). Vietnamese is the game's main language and
is written as such, not translated word for word.
"""

import math

TEXTS = {}
MISSIONS = []
ORDER_NOTES = []


def T(key, en, vi):
    """A player-facing text, both languages. The same key twice must say the same thing."""
    if key in TEXTS and TEXTS[key] != (en, vi):
        raise SystemExit(f'text {key} written twice with different words')
    TEXTS[key] = (en, vi)
    return key


# ---------------------------------------------------------------------------------------------- the ground

CAMP = (-108.75, -108.75)
ENEMY_CAMP = (108.75, 108.75)

# Where each map's objectives are (map data; the same template everywhere, a little apart).
POINTS = {
    'ashfield': {'west': (-56.25, 86.25), 'town': (0, 0), 'east': (56.25, -86.25)},
    'dunebreak': {'west': (-56.25, 86.25), 'town': (0, 0), 'east': (56.25, -86.25)},
    'frostpeak': {'west': (-56.25, 86.25), 'town': (0, 0), 'east': (56.25, -86.25)},
    'ironport': {'west': (-56.25, 90.0), 'town': (0, 0), 'east': (56.25, -86.25)},
    'redrock': {'west': (-56.25, 86.25), 'town': (0, 0), 'east': (56.25, -86.25)},
    'whiteout': {'west': (-71.25, 71.25), 'town': (0, 0), 'east': (71.25, -71.25)},
    'greenvale': {'west': (-60.0, 86.25), 'town': (0, 0), 'east': (60.0, -86.25)},
    'rustyard': {'west': (-63.75, 86.25), 'town': (0, 0), 'east': (63.75, -86.25)},
    'emberridge': {'west': (-73.1, 60.0), 'town': (0, 0), 'east': (73.1, -60.0)},
    'junglepass': {'west': (-75.0, 63.75), 'town': (0, 0), 'east': (75.0, -63.75)},
    'skyhold': {'west': (-75.0, 63.75), 'town': (0, 0), 'east': (75.0, -63.75)},
    'metrocity': {'west': (-67.5, 67.5), 'town': (0, 0), 'east': (67.5, -67.5)},
    # The four battlefields built for the story (their files come with the maps branch).
    'landingbeach': {'west': (-52.0, 84.0), 'town': (0, 0), 'east': (58.0, -92.0)},
    'hydrodam': {'west': (-40.0, 64.0), 'town': (0, 0), 'east': (36.0, -98.0)},
    'capital': {'west': (-84.0, 100.0), 'town': (0, 0), 'east': (84.0, -100.0)},
    'launchsite': {'west': (-50.0, 80.0), 'town': (0, 0), 'east': (50.0, -80.0)},
}

NEW_MAPS = {'landingbeach', 'hydrodam', 'capital', 'launchsite'}

# The weather each battlefield can have (MatchSettings.AllMaps; the new maps like their kin).
WEATHER = {
    'ashfield': {'Clear', 'Overcast', 'Rain', 'Storm', 'Fog', 'Night'},
    'dunebreak': {'Clear', 'Sandstorm', 'Overcast', 'Night'},
    'frostpeak': {'Snow', 'Clear', 'Overcast', 'Fog', 'Night'},
    'ironport': {'Clear', 'Overcast', 'Rain', 'Storm', 'Fog', 'Night'},
    'redrock': {'Clear', 'Sandstorm', 'Night'},
    'whiteout': {'Snow', 'Fog', 'Clear', 'Night'},
    'greenvale': {'Clear', 'Overcast', 'Rain', 'Storm', 'Fog', 'Night'},
    'rustyard': {'Clear', 'Overcast', 'Rain', 'Fog', 'Night'},
    'emberridge': {'Night', 'Clear', 'Overcast', 'Fog', 'Storm'},
    'junglepass': {'Clear', 'Rain', 'Fog', 'Storm', 'Overcast', 'Night'},
    'skyhold': {'Clear', 'Overcast', 'Rain', 'Fog', 'Night'},
    'metrocity': {'Night', 'Clear', 'Rain', 'Overcast', 'Fog', 'Storm'},
    'landingbeach': {'Clear', 'Overcast', 'Rain', 'Storm', 'Fog', 'Night'},
    'hydrodam': {'Clear', 'Overcast', 'Rain', 'Storm', 'Fog', 'Night'},
    'capital': {'Night', 'Clear', 'Rain', 'Overcast', 'Fog', 'Storm'},
    'launchsite': {'Clear', 'Sandstorm', 'Overcast', 'Night'},
    'lighthousebay': {'Overcast', 'Clear', 'Fog', 'Rain', 'Storm', 'Night'},
}


def turn(p, reversed_):
    """A spot in the player's frame, on the battlefield (turned half round for a reversed mission)."""
    return (-p[0], -p[1]) if reversed_ else (p[0], p[1])


def pt(map_id, point):
    return POINTS[map_id][point]


def toward(a, b, share):
    return (a[0] + (b[0] - a[0]) * share, a[1] + (b[1] - a[1]) * share)


def ring(centre, radius, count, start=0.0):
    out = []
    for i in range(count):
        a = start + 2 * math.pi * i / count
        out.append((round(centre[0] + math.cos(a) * radius, 2), round(centre[1] + math.sin(a) * radius, 2)))
    return out


def flat(points):
    out = []
    for p in points:
        out += [round(p[0], 2), round(p[1], 2)]
    return out


# ---------------------------------------------------------------------------------------------- building blocks

def units(team, defs, around, radius=6.0, heading=None, reversed_=False, start=0.0):
    """Units of one side round a spot (the player's frame)."""
    spots = ring(around, radius, len(defs), start) if len(defs) > 1 else [around]
    out = []
    for d, s in zip(defs, spots):
        x, z = turn(s, reversed_)
        h = heading if heading is not None else (45 if team == 0 else 225)
        if reversed_:
            h = (h + 180) % 360
        out.append({'def': d, 'team': team, 'x': round(x, 2), 'z': round(z, 2), 'heading': h})
    return out


def waves(roster, first=40, interval=45, size=2, grow=0.4, max_size=5, max_alive=14, spawns=None, reversed_=False):
    w = {'first': first, 'interval': interval, 'size': size, 'grow': grow, 'maxSize': max_size, 'maxAlive': max_alive, 'roster': roster}
    if spawns:
        w['spawns'] = flat([turn(s, reversed_) for s in spawns])
    return w


def scripted(def_id, at, route=None, heading=225, reversed_=False, **extra):
    x, z = turn(at, reversed_)
    o = {'def': def_id, 'x': round(x, 2), 'z': round(z, 2), 'heading': (heading + 180) % 360 if reversed_ else heading}
    if route:
        o['route'] = flat([turn(p, reversed_) for p in route])
    o.update(extra)
    return o


def radio(on, key, arg=None, at=None):
    r = {'key': key}
    if at is not None:
        r['at'] = at
    else:
        r['on'] = on
    if arg:
        r['arg'] = arg
    return r


def area(min_p, max_p, reversed_=False):
    a, b = turn(min_p, reversed_), turn(max_p, reversed_)
    return {'minX': round(min(a[0], b[0]), 2), 'minZ': round(min(a[1], b[1]), 2), 'maxX': round(max(a[0], b[0]), 2), 'maxZ': round(max(a[1], b[1]), 2)}


# ---------------------------------------------------------------------------------------------- missions

class Line:
    """A radio line: who speaks, when, both languages."""

    def __init__(self, speaker, on, en, vi, arg=None, at=None):
        self.speaker, self.on, self.en, self.vi, self.arg, self.at = speaker, on, en, vi, arg, at


def say(speaker, on, en, vi, arg=None, at=None):
    return Line(speaker, on, en, vi, arg, at)


def add_mission(m, name, brief, fragment, lines=(), stages_text=None, choices_text=None):
    """
    Registers a mission: its data (a dict in campaign.json's shape), its name and briefing, the
    dossier fragment it adds (title, text) and its radio lines; an operation's stage titles and
    choice texts.
    """
    mid = m['id']
    T(f'mission.{mid}.name', *name)
    T(f'mission.{mid}.brief', *brief)
    T(f'mission.{mid}.fragment.title', *fragment[0])
    T(f'mission.{mid}.fragment', *fragment[1])
    rad = list(m.get('radio', []))
    for i, line in enumerate(lines):
        key = f'radio.{line.speaker}.{mid}.{i + 1}'
        T(key, line.en, line.vi)
        rad.append(radio(line.on, key, line.arg, line.at))
    if rad:
        m['radio'] = rad
    for stage, text in (stages_text or {}).items():
        T(f'stage.{mid}.{stage}', *text)
    for key, (title, info) in (choices_text or {}).items():
        T(f'choice.{mid}.{key}', *title)
        T(f'choice.{mid}.{key}.info', *info)
    MISSIONS.append(m)
    return m
