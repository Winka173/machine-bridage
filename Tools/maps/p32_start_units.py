"""Prompt 32 L6: marks the generated maps' generic start units ("start": true), in place (idempotent).

    python Tools/maps/p32_start_units.py           # marks them
    python Tools/maps/p32_start_units.py --check   # only counts (exit 1 if any is unmarked)

The generic start units are build_maps.py's CONQUEST_UNITS and SURVIVAL_UNITS (scout jeeps, IFVs, light and main
battle tanks, howitzers on both sides): the precheck (Docs/checks/p32_precheck.md, item 2) found the units seen at a
match's start come from them. In the modes with opening squads they are replaced by the squads (SimWorld.MapUnits); a
campaign mission keeps them (MissionMode reads every unit). A siege's fortress defences (towers) are never marked.
build_maps.py writes the flag itself from now on.
"""
from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "maps")
START_DEFS = ("scout_jeep", "ifv", "light_tank", "main_battle_tank", "artillery")
UNIT = re.compile(r'\{"def": "(' + "|".join(START_DEFS) + r')", "team": [01], "x": -?[0-9.]+, "z": -?[0-9.]+, "heading": -?[0-9.]+\}')


def main():
    check = "--check" in sys.argv
    marked = unmarked = files = 0
    for path in sorted(glob.glob(os.path.join(MAPS, "*.json"))):
        text = open(path, encoding="utf-8", newline="").read()
        units = text.find('"units": [')
        if units < 0:
            continue
        end = text.find("]", units)
        block = text[units:end]
        n = len(UNIT.findall(block))
        if n == 0:
            continue
        files += 1
        unmarked += n
        if check:
            continue
        block2 = UNIT.sub(lambda m: m.group(0)[:-1] + ', "start": true}', block)
        open(path, "w", encoding="utf-8", newline="").write(text[:units] + block2 + text[end:])
        marked += n
    already = 0
    for path in glob.glob(os.path.join(MAPS, "*.json")):
        already += open(path, encoding="utf-8").read().count('"start": true')
    print(f"{files} map files, {unmarked} unmarked start units, {marked} marked now, {already} marked in all")
    if check and unmarked:
        sys.exit(1)


if __name__ == "__main__":
    main()
