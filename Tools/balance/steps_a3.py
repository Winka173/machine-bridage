"""Prompt 25 importer, A3: weapon families by real name (see import_xlsx.py)."""
from __future__ import annotations

import collections
import os
import re

import import_xlsx as X

INTRO = ("Weapons that are the same real weapon (the same real name once a mount's qualifier in brackets is dropped, "
         "the same damage type, round, size, and lobbed or direct) form a family in `weaponFamilies`: its speed, blast "
         "radius, round model and round weight (the tracer's and the report's) are written once there and every "
         "member takes them. A family's value is the sheet's most common proposal among its members (the current one "
         "where the sheet has none); where members disagreed, the report says which moved.")

# Names the sheet counts as one weapon: "mọi Hellfire", the AIM-9 and the AIM-9X, the Oerlikon KDA on the Gepard and
# on the boss's twin mount.
ALIASES = {"AGM-114L Hellfire Longbow": "AGM-114 Hellfire", "AIM-9X Sidewinder": "AIM-9 Sidewinder",
           "Oerlikon KDA 35 mm": "Oerlikon 35 mm"}

TAB = "\t"
NL = "\n"
FAMILIES_TSV = os.path.join(X.ROOT, "Docs", "balance", "weapon_families.tsv")


def real_name(real):
    """A weapon's real name without its mount in brackets, aliases folded (BalanceSheetTests.FamilyKey mirrors it)."""
    name = re.sub(r"\s*\([^)]*\)\s*$", "", real).strip()
    return ALIASES.get(name, name)


def real_key(w):
    real = w.get("real")
    if not real:
        return None
    lobbed = (w.get("minRange", 0) or 0) > 0 or w.get("projectile") in ("Bomb", "Drone")
    return (real_name(real), w.get("damageType"), w.get("projectile", "Shell"), float(w.get("size", 0) or 0), lobbed,
            "cluster" in w)


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "_", text.lower())
    return s.strip("_")


def mode(values, weight=None):
    """The most common value. A tie goes to the value whose weapons the most cards carry (<weight>: value -> how much
    its carriers weigh; a player's card over a tower over a boss), then to the largest (a blast never shrinks)."""
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    counts = collections.Counter(vals)
    top = max(counts.values())
    tied = [v for v, n in counts.items() if n == top]
    if weight and len(tied) > 1:
        best = max(weight.get(v, 0) for v in tied)
        tied = [v for v in tied if weight.get(v, 0) == best]
    try:
        return max(tied)
    except TypeError:
        return sorted(tied, key=str)[0]


def carriers_weight(g, wid):
    """How much a weapon's carriers weigh in a tie: a card a player fields 1, a tower 0.3, a boss or escort 0.1."""
    total = 0.0
    for vid in g.users(wid):
        v = g.vehicles_raw[vid]
        total += 0.1 if g.is_boss(vid) or v.get("cp", 0) == 0 and not v.get("static") else 0.3 if v.get("static") else 1.0
    return total


def weighted(g, members, values):
    """value -> the carriers' weight of the members that hold it."""
    w = collections.defaultdict(float)
    for m, v in zip(members, values):
        if v is not None:
            w[v] += carriers_weight(g, m)
    return w


def families_of(g):
    groups = {}
    for wid in g.raw_weapons:
        if wid == "none":
            continue
        k = real_key(g.weapon(wid, family=False))
        if k:
            groups.setdefault(k, []).append(wid)
    return {k: v for k, v in groups.items() if len(v) > 1}


def plan(g, wb, weapon_rows):
    """(family id, entry, members, members' values without families) for every family."""
    _, trows = X.sheet(wb, "Tốc độ tên lửa")
    missile_speed = {r[0]: r[8] for r in trows if r[0]}
    groups = families_of(g)
    ids = {}
    for k in sorted(groups, key=lambda k: (k[0], str(k[1]), str(k[2]), k[3], k[4], k[5])):
        base = slug(k[0])
        fid, n = base, 2
        while fid in ids.values():
            fid = f"{base}_{n}"
            n += 1
        ids[k] = fid
    out = []
    for k, fid in ids.items():
        members = groups[k]
        # The members' values as the game reads them (their family's once there is one, so a second run is a no-op).
        plain = {m: g.weapon(m) for m in members}
        sheet_speed = [missile_speed.get(m) or (weapon_rows[m][X.W_SPEED] if m in weapon_rows else None) for m in members]
        cur_speed = [plain[m].get("projectileSpeed") for m in members]
        speed = mode(sheet_speed, weighted(g, members, sheet_speed)) or mode(cur_speed, weighted(g, members, cur_speed))
        sheet_splash = [weapon_rows[m][X.W_SPLASH] if m in weapon_rows else None for m in members]
        cur_splash = [plain[m].get("splash", 0) or 0 for m in members]
        if any(v is not None for v in sheet_splash):
            splash = mode(sheet_splash, weighted(g, members, sheet_splash))
        else:
            splash = mode(cur_splash, weighted(g, members, cur_splash))
        counts = collections.Counter()
        for m in members:
            model = plain[m].get("projectileModel")
            if model:
                counts[model] += 1 + 0.001 * len(g.users(m))
        e = {"id": fid, "real": k[0], "projectileSpeed": speed, "splash": splash or 0}
        if counts:
            e["projectileModel"] = counts.most_common(1)[0][0]
        weights = [plain[m].get("roundWeight") or plain[m].get("damage") for m in members]
        if len(set(weights)) > 1:
            e["roundWeight"] = max(weights)  # the heaviest look and report: a round is never drawn smaller
        elif "roundWeight" in g.families.get(fid, {}):
            e["roundWeight"] = g.families[fid]["roundWeight"]
        out.append((fid, e, members, plain))
    return out


def number(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


def run(wr, wb, report, weapon_rows):
    g = wr.game
    doc = wr.doc
    step = "A3"
    sh = "Tốc độ tên lửa, Vũ khí đề xuất"
    entries = plan(g, wb, weapon_rows)
    lines = ["["]
    for i, (fid, e, members, plain) in enumerate(entries):
        lines.append("    " + X.fmt({k: number(v) for k, v in e.items()}) + ("," if i < len(entries) - 1 else ""))
    lines.append("  ]")
    body = NL.join(lines)
    if doc.has_section("weaponFamilies"):
        s0, e0 = doc._section("weaponFamilies")
        doc.text = doc.text[:s0] + body + doc.text[e0 + 1:]
    else:
        head = ("  // Prompt 25 A3 (DECISIONS 25A): weapon families. Every weapon that is the same real weapon (its real name without its\n"
                "  // mount in brackets, its damage type, round, size, lobbed or direct) takes its family's speed, blast radius, round\n"
                "  // model and round weight from here (\"weaponFamily\" on the weapon; \"\" keeps a weapon that inherits a member out of it).\n"
                "  // A weapon's own line keeps what differs (reach, rate, load). Written by Tools/balance/import_xlsx.py.\n")
        at = doc.text.index("\n  // projectile: Shell (default)")
        doc.text = doc.text[:at + 1] + head + '  "weaponFamilies": ' + body + ",\n\n" + doc.text[at + 1:]
    g.refresh()
    member_of = {m: fid for fid, e, members, plain in entries for m in members}
    for fid, e, members, plain in entries:
        moved = []
        for m in members:
            def fn(ent, fid=fid, e=e):
                ent.set("weaponFamily", fid)
                for key in X.FAMILY_KEYS:
                    if key in e:
                        ent.remove(key)
            doc.edit("weapons", m, fn)
            for key in X.FAMILY_KEYS:
                if key not in e:
                    continue
                before = plain[m].get(key, 0 if key == "splash" else None)
                if key == "roundWeight":
                    before = plain[m].get("roundWeight") or plain[m].get("damage")
                if not X.close(before, e[key]):
                    moved.append(f"{m} {key} {X.fmt(before)} -> {X.fmt(number(e[key]))}")
        g.refresh()
        detail = f"{', '.join(members)}: speed {X.fmt(number(e['projectileSpeed']))}, blast {X.fmt(number(e['splash']))}"
        if "projectileModel" in e:
            detail += f", model {e['projectileModel']}"
        if moved:
            detail += "; moved: " + "; ".join(moved)
        report.add(step, sh, fid, "family", "applied" if moved else "already", detail)
    for wid, w in g.raw_weapons.items():
        parent = w.get("inherits")
        if parent and wid not in member_of and g.weapon(parent, family=False).get("weaponFamily") \
                and w.get("weaponFamily") != "":
            doc.edit("weapons", wid, lambda ent: ent.set("weaponFamily", ""))
            report.add(step, sh, wid, "family", "applied", f"inherits {parent} but is another weapon: kept out of its family")
    g.refresh()
    tsv = ["# Generated by Tools/balance/import_xlsx.py (A3): each weapon family and its members.",
           TAB.join(["family", "real", "members"])]
    for fid, e, members, plain in entries:
        tsv.append(TAB.join([fid, e["real"], ",".join(members)]))
    with open(FAMILIES_TSV, "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(tsv) + NL)
