"""Prompt 25 importer, A5: blast radius from the round (see import_xlsx.py).

The sheet "Tổng quan": radius ~ 10 m x (mass / 500 kg)^(1/3), the FAB-500 at 10 m, and one radius for one round on
every carrier, except where the sheet gives a number. So:
  1. A round (the real name without its mount, damage type, size, a cluster or not) takes the sheet's number where the
     weapon sheet gives one for any of its weapons (the most common; a tie by the cards that carry it, then the
     largest), on every weapon that fires it, lobbed or flat.
  2. A round the sheet gives no number for, weighed in kilograms (bombs, missiles, drones), takes the rule.
  3. A shell or rocket the sheet gives no number for (its size a calibre) scales from its family's rounds the sheet
     does number: a shell's mass goes with the cube of its calibre, so the rule's radius goes with the calibre; between
     two numbered calibres it is read off the line between them, beyond them scaled from the nearest.
A boss system's own round (family "special", or one the boss system lays) is left to task C1.
"""
from __future__ import annotations

import collections

import import_xlsx as X
import steps_a3 as F

INTRO = ("One blast radius for one round (its real name without the mount, damage type, size, a cluster or not) on every "
         "weapon that fires it: the weapon sheet's number where it gives one, else the rule of \"Tổng quan\" (10 m x "
         "(mass / 500 kg)^(1/3)) for rounds weighed in kilograms, else the calibre scale of the sheet's own numbers for "
         "the round's family (a shell's radius goes with its calibre). A family's radius is written on the family (A3).")

KG_FAMILIES = {"bomb", "cruise", "ballistic", "drone", "atgm", "aa_missile"}
# Rounds a later step sets from its own sheet (C1: the Scylla's AK-130 from "Boss đề xuất").
LATER = {"naval_130_twin": "C1 (sheet Boss đề xuất)"}


def round_key(w):
    real = w.get("real")
    if not real:
        return None
    return (F.real_name(real), w.get("damageType"), float(w.get("size", 0) or 0), "cluster" in w)


def rule(kg):
    return 10.0 * (kg / 500.0) ** (1.0 / 3.0)


def half(v):
    return round(v * 2) / 2


def calibre_scale(size, refs):
    """The radius a calibre takes from (calibre, radius) references of its family."""
    below = [r for r in refs if r[0] <= size]
    above = [r for r in refs if r[0] >= size]
    if below and above:
        lo = max(below)
        hi = min(above)
        if hi[0] == lo[0]:
            return lo[1], f"the sheet's {X.fmt(lo[1])} m at {X.fmt(lo[0])} mm"
        v = lo[1] + (size - lo[0]) / (hi[0] - lo[0]) * (hi[1] - lo[1])
        return v, f"between the sheet's {X.fmt(lo[1])} m at {X.fmt(lo[0])} mm and {X.fmt(hi[1])} m at {X.fmt(hi[0])} mm"
    near = min(refs, key=lambda r: abs(r[0] - size))
    return near[1] * size / near[0], f"the sheet's {X.fmt(near[1])} m at {X.fmt(near[0])} mm, scaled by calibre"


def run(wr, wb, report, weapon_rows):
    g = wr.game
    doc = wr.doc
    step = "A5"
    sh = "Tổng quan, Vũ khí đề xuất"
    rounds = collections.defaultdict(list)
    for wid in g.raw_weapons:
        if wid == "none":
            continue
        w = g.weapon(wid)
        k = round_key(w)
        if k:
            rounds[k].append(wid)
    # The sheet's numbers by prompt 13 family, for the calibre scale: (calibre, radius).
    refs = collections.defaultdict(set)
    for wid, row in weapon_rows.items():
        if wid in g.raw_weapons and row[X.W_SPLASH]:
            w = g.weapon(wid)
            refs[(w.get("family"), w.get("damageType"), bool(w.get("thermobaric")))].add((float(w.get("size", 0) or 0), float(row[X.W_SPLASH])))
    for k in sorted(rounds, key=lambda k: (k[0], str(k[1]), k[2], k[3])):
        members = rounds[k]
        if all(m in LATER for m in members):
            report.add(step, sh, ", ".join(members), "blast", "deferred", "set by task " + LATER[members[0]])
            continue
        ws = {m: g.weapon(m) for m in members}
        current = {m: float(ws[m].get("splash", 0) or 0) for m in members}
        first = ws[members[0]]
        sheet_numbers = [weapon_rows[m][X.W_SPLASH] if m in weapon_rows else None for m in members]
        if not any(current.values()) and not any(sheet_numbers):
            continue
        if (first.get("family") == "special" or any(ws[m].get("laid") for m in members)) and not any(v is not None for v in sheet_numbers):
            report.add(step, sh, ", ".join(members), "blast", "deferred", "a boss system's own round the sheet gives no number for: task C1")
            continue
        if any(v is not None for v in sheet_numbers):
            target = F.mode(sheet_numbers, F.weighted(g, members, sheet_numbers))
            source = "the weapon sheet"
        elif first.get("family") in KG_FAMILIES:
            target = half(rule(k[2]))
            source = f"the rule: {X.fmt(k[2])} kg"
        else:
            fam_refs = refs.get((first.get("family"), first.get("damageType"), bool(first.get("thermobaric"))))
            if not fam_refs:
                report.add(step, sh, ", ".join(members), "blast", "skipped",
                           f"no sheet number for its family ({first.get('family')}, {first.get('damageType')}) to scale from: kept {X.fmt(max(current.values()))} m")
                continue
            v, how = calibre_scale(k[2], sorted(fam_refs))
            target = half(v)
            source = how
        if not target:
            continue
        moved = []
        for m in members:
            if X.close(current[m], target):
                continue
            fam = g.weapon(m, family=False).get("weaponFamily")
            if fam:
                def fn(e, t=target):
                    e.set("splash", t, after="projectileSpeed")
                doc.edit("weaponFamilies", fam, fn)
            else:
                wr.weapon_field(m, "splash", target)
            g.refresh()
            moved.append(f"{m} {X.fmt(current[m])} -> {X.fmt(target)}")
        name = f"{k[0]} ({k[1]}, {X.fmt(k[2])}{', cluster' if k[3] else ''})"
        report.add(step, sh, name, "blast", "applied" if moved else "already",
                   f"{X.fmt(target)} m from {source}: {', '.join(members)}" + ("; moved: " + "; ".join(moved) if moved else ""))
