"""The RED map fixes (lead pass, 2026-10-02; DECISIONS "RED map fixes (lead pass, 2026-10-02)"): the props that sealed
off a walkable pocket (prompt 30's audit, Tools/audit/map_audit.py, "RED connectivity") moved, dropped or, where the
pocket is dead ground inside the fortress works, filled with indestructible blockers so it is no longer a trap.

    python Tools/maps/red_fixes.py            # applies the fixes to the generated map files (idempotent)
    python Tools/maps/red_fixes.py --check    # only checks, writes nothing (exit 1 when a file would change)
    python Tools/maps/red_fixes.py swamp      # one battlefield's files

Works on the generated map files, a prop per line as build_maps.dump writes them. build_maps.py runs it before the
wall lines (p32_walls.py) and longmap.py before its access check, so a rebuild keeps the fixes. A fix whose prop is not
in the file (a rebuild placed the dressing differently) is reported and skipped: the audit then says whether that
file still has a pocket.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAPS = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Resources', 'Data', 'maps')


def drop(kind, x, z):
    return ('drop', kind, x, z)


def move(kind, x, z, to_x, to_z):
    return ('move', kind, x, z, to_x, to_z)


def add(kind, x, z, rot=0):
    return ('add', kind, x, z, rot)


# Border Bridge (Conquest, Sandbox): the wreck north of the south-side workshop closed the nook between the workshop's
# garage and the wrecks; without it the nook opens north (8 m). The north side has no such nook: both sides now match.
BORDERBRIDGE = [drop('wreck_tank', -19.0, -69.5)]
# Ember Ridge (Conquest, Sandbox, long): the nook by the lava rift (cliff east, spires west, lava south) was shut by a
# wreck and a rock at its neck; the wreck goes and the rock steps 2.5 m west: an 8 m neck north to the open basalt.
EMBERRIDGE = [drop('wreck_car', -32.0, 79.5), move('basalt_rock_c', -34.7, 71.25, -37.2, 71.25)]
# The classic fortress's back corner (coral isles, swamp): the dead ground between the keep's walls, the hangars, the
# outer works and the map edge, with blast walls (revetments) and a boulder, all indestructible.
CORAL_FILL = [add('revetment', 142.0, 89.0, 90), add('revetment', 134.0, 81.0, 90), add('revetment', 142.0, 77.5, 90),
              add('revetment', 141.0, 94.0), add('revetment', 142.0, 123.0, 90), add('revetment', 145.0, 131.0, 90),
              add('revetment', 141.0, 116.0), add('revetment', 89.0, 142.0), add('revetment', 72.0, 141.0, 90),
              add('revetment', 81.0, 134.0), add('revetment', 71.0, 142.0), add('revetment', 89.0, 146.0),
              add('revetment', 127.0, 142.0), add('boulders', 115.0, 147.0)]
SWAMP_FILL = [add('revetment', 142.0, 89.0, 90), add('revetment', 134.0, 81.0, 90), add('revetment', 142.0, 77.5, 90),
              add('revetment', 141.0, 96.0), add('revetment', 133.0, 142.0), add('revetment', 120.0, 141.0, 90),
              add('revetment', 142.0, 127.0, 90), add('revetment', 135.0, 140.0), add('revetment', 141.0, 116.0),
              add('revetment', 89.0, 142.0), add('boulders', 75.0, 142.5), add('revetment', 81.0, 134.0),
              add('revetment', 89.0, 144.0)]
FIXES = {
    'borderbridge_conquest': BORDERBRIDGE,
    'borderbridge_sandbox': BORDERBRIDGE,
    'emberridge_conquest': EMBERRIDGE,
    'emberridge_sandbox': EMBERRIDGE,
    'emberridge_long': EMBERRIDGE,
    # Open-Pit Mine (Siege): a sandbag line shut the strip behind the ore loadout (factory, tank, pipes, the outline);
    # without it the strip opens north, 6 m wide.
    'openpit_siege': [drop('sandbags', 100.2, -77.95)],
    'coralisles_siege': CORAL_FILL,
    'swamp_siege': SWAMP_FILL,
}

PROP = re.compile(r'^    (\{"def": .*\}),?$')


def same(p, kind, x, z):
    return p['def'] == kind and abs(p['x'] - x) < 0.05 and abs(p['z'] - z) < 0.05


def fix_text(text, fixes, notes):
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    start = lines.index('  "props": [') + 1
    end = start
    while PROP.match(lines[end]):
        end += 1
    props = [json.loads(PROP.match(l).group(1)) for l in lines[start:end]]
    for f in fixes:
        op, kind, x, z = f[:4]
        hit = [i for i, p in enumerate(props) if same(p, kind, x, z)]
        if op == 'drop':
            if hit:
                del props[hit[0]]
        elif op == 'move':
            if hit:
                props[hit[0]]['x'], props[hit[0]]['z'] = f[4], f[5]
            elif not any(same(p, kind, f[4], f[5]) for p in props):
                notes.append(f'{kind} at ({x}, {z}) not found')
        elif op == 'add' and not hit:
            props.append({'def': kind, 'x': x, 'z': z, **({'rot': f[4]} if f[4] else {})})
    body = [f'    {json.dumps(p)},' for p in props]
    body[-1] = body[-1][:-1]
    return nl.join(lines[:start] + body + lines[end:])


def main(args):
    check = '--check' in args
    ids = [a for a in args if not a.startswith('--')]
    changed = 0
    for name, fixes in FIXES.items():
        if ids and not any(name.startswith(i) for i in ids):
            continue
        path = os.path.join(MAPS, name + '.json')
        if not os.path.exists(path):
            continue
        text = open(path, encoding='utf-8', newline='').read()
        notes = []
        new = fix_text(text, fixes, notes)
        for n in notes:
            print(f'NOTE {name}: {n}')
        if new != text:
            changed += 1
            print(f'{name}: {"would change" if check else "fixed"}')
            if not check:
                open(path, 'w', encoding='utf-8', newline='').write(new)
    print(f'{changed} map files {"would change" if check else "written"}')
    return 1 if check and changed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
