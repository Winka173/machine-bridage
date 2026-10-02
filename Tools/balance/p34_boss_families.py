"""Prompt 34 L2: the boss family table applied to the boss weapons, keeping each weapon's DPS (DECISIONS "Prompt 34 L2").

    python Tools/balance/p34_boss_families.py                 # dry run: the plan and the per-boss check
    python Tools/balance/p34_boss_families.py --write         # save balance.json and Docs/balance/boss_weapon_families.md
    python Tools/balance/p34_boss_families.py --write --only leviathan   # only the weapons that boss owns (commit per boss)

The DPS here is static and on paper: no simulation, no measurement.

  1. targetDPS = the weapon's sustained DPS on one target before prompt 34: the rounds of a cycle (salvo or magazine) over the
     cycle (`steps_c.sustained`), before the boss's own factors (weaponDamage, rank, phases), which do not change. A ship's
     salvo counts as turrets x shells x damage / every.
  2. The family's round (weaponFamilyTable "boss": damage, core, edge) goes on the weapon, together with the family's
     speed and damage type (the most common among its boss members). The new cycle = the new damage of a cycle / targetDPS.
     The gaps inside a salvo or magazine stay as designed; the cooldown (or a magazine's change) takes the rest. A
     variant (weaponVariantId) takes the family's damage only and keeps its own round (speed, type, blast).
  3. Area bonus: a core more than 1.25 times the old one makes the cycle that much longer (new core / old core; an old
     core under 2 m counts as 2 m, a direct hit's own reach). A smaller core never shortens the cycle.

The first run stores the numbers from before in Tools/balance/p34_boss_baseline.json, and every later run starts from
them, so a rerun changes nothing (and never applies the area bonus twice).

Left alone: Gungnir (rail_supergun: only its family and tier T5, prompt 29 G1), so the weapons it carries stay as they are
on every boss; weapons a boss shares with player vehicles (prompt 34: player weapons do not change); laid weapons other
than the 406 mm salvo; the big attacks (super weapons: prompt 26 B6's numbers) and the cruise missiles (not in the table).
"""
from __future__ import annotations

import collections
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import p26_ab as A  # noqa: E402
import steps_c as S  # noqa: E402
import p34_families as F  # noqa: E402
from jsonc_edit import Doc, Entry  # noqa: E402

ROOT = F.ROOT
BASELINE = os.path.join(HERE, "p34_boss_baseline.json")
REPORT = os.path.join(ROOT, "Docs", "balance", "boss_weapon_families.md")

FROZEN_BOSSES = {"rail_supergun"}  # Gungnir: family and tier only
OLD_CORE_FLOOR = 2.0
BONUS_FROM = 1.25
MIN_CLIP_CHANGE = 0.5
MAX_RATE = 1.0 / 60.0  # the simulation carries up to 60 rounds a second
SALVO_WEAPON = "p26_leviathan_lev406"
SALVO_SHELLS = 3       # a turret's three barrels fire together (prompt 34 L2 / L4)


def resolved(ws: F.Weapons, wid):
    return ws.resolve(wid)


def numbers(w):
    """The fields the DPS and the family touch, from a resolved weapon line."""
    return {k: w.get(k, d) for k, d in (("damage", 0), ("cooldown", 1.0), ("burst", 1), ("burstInterval", 0.1), ("clip", 0),
                                        ("clipReload", 0.0), ("ammo", 0), ("reload", 0.0), ("splash", 0.0), ("edge", 0.0),
                                        ("projectileSpeed", None), ("damageType", "Kinetic"), ("targets", "Ground"),
                                        ("laid", False), ("weaponFamily", None))}


def boss_users(data):
    built = A.expand(data)
    users = collections.defaultdict(list)   # weapon -> [(boss, mount)]
    for bid, b in built.items():
        for k, wid in enumerate(S.mounts_of(b)):
            if wid:
                users[wid].append((bid, k))
    return built, users


def player_users(data, built):
    out = set()
    for v in data["vehicles"]:
        if v["id"] in built:
            continue
        for wid in [v.get("weapon")] + [m.get("weapon") for m in v.get("secondary") or []]:
            if wid:
                out.add(wid)
    return out


def children(data):
    kids = collections.defaultdict(list)
    for w in data["weapons"]:
        if w.get("inherits"):
            kids[w["inherits"]].append(w["id"])
    for r in (data.get("secondRounds") or {}).get("rounds", []):
        if r.get("inherits"):
            kids[r["inherits"]].append(r["id"])
    return kids


def descendants(kids, wid):
    out, todo = [], list(kids.get(wid, []))
    while todo:
        c = todo.pop()
        out.append(c)
        todo += kids.get(c, [])
    return out


def nice_s(x):
    return round(x, 3) if x < 10 else round(x, 2)


def solve_cycle(old, new_damage, target, bonus):
    """The new cadence fields for a weapon whose round becomes new_damage: (fields, achieved DPS before the bonus, note)."""
    n = old["clip"] if old["clip"] > 0 else old["burst"]
    per = new_damage * max(1, n)
    cycle = per / target * bonus if target > 0 else None
    fields, note = {}, ""
    if cycle is None:
        return fields, 0.0, "no DPS"
    if old["clip"] > 0:
        firing = (old["clip"] - 1) * old["cooldown"]
        cr = cycle - firing
        if cr >= MIN_CLIP_CHANGE:
            fields["clipReload"] = nice_s(cr)
        else:
            # The magazine cannot be fired off fast enough at its old cadence: a faster cadence, the change kept short.
            cr = min(old["clipReload"], max(MIN_CLIP_CHANGE, cycle * 0.25))
            cd = max(MAX_RATE, (cycle - cr) / max(1, old["clip"] - 1))
            fields["cooldown"] = round(cd, 4)
            fields["clipReload"] = nice_s(cr)
            note = f"cadence {old['cooldown']} -> {fields['cooldown']} s (the magazine's change alone could not keep the DPS)"
        cd = fields.get("cooldown", old["cooldown"])
        real_cycle = (old["clip"] - 1) * cd + fields["clipReload"]
    elif old["burst"] > 1:
        gaps = (old["burst"] - 1) * old["burstInterval"]
        cd = cycle - gaps
        if cd >= 0.1:
            fields["cooldown"] = nice_s(cd)
        else:
            bi = max(0.05, (cycle - 0.1) / (old["burst"] - 1))
            fields["burstInterval"] = round(bi, 3)
            fields["cooldown"] = 0.1
            note = f"salvo interval {old['burstInterval']} -> {fields['burstInterval']} s"
        real_cycle = fields["cooldown"] + (old["burst"] - 1) * fields.get("burstInterval", old["burstInterval"])
    else:
        fields["cooldown"] = nice_s(max(0.05, cycle))
        real_cycle = fields["cooldown"]
    return fields, per / max(0.05, real_cycle), note


def family_round(base, members, fam):
    """The family's speed and damage type: the most common among its boss members before prompt 34 (ties: the faster)."""
    speeds = collections.Counter(base[w]["projectileSpeed"] for w in members)
    types = collections.Counter(base[w]["damageType"] for w in members)
    speed = sorted(speeds.items(), key=lambda kv: (-kv[1], -(kv[0] or 0)))[0][0]
    dtype = types.most_common(1)[0][0]
    t = F.FAMILIES[fam]
    if t[3] and t[3]["core"] > 0 and fam not in ("cal_35",):
        dtype = "HighExplosive"
    if fam.endswith("_ap") or fam == "atgm_kornet":
        dtype = {"atgm_kornet": "ShapedCharge"}.get(fam, "Kinetic")
    return speed, dtype


def plan(data, base):
    ws = F.Weapons(data)
    assign = F.assignment(ws)
    built, users = boss_users(data)
    players = player_users(data, built)
    frozen_w = {w for w, us in users.items() if any(b in FROZEN_BOSSES for b, _ in us)}
    kids = children(data)
    table = {t[0]: t for t in F.TABLE if t[3]}
    rows, skipped = {}, {}
    members = collections.defaultdict(list)
    for wid in users:
        if wid not in ws.raw:
            continue
        fam, var, _ = assign[wid]
        if fam in table and not var and wid not in frozen_w and wid not in players:
            members[fam].append(wid)
    for wid in sorted(users):
        if wid not in ws.raw:
            continue
        fam, var, tier = assign[wid]
        if fam not in table:
            continue
        if wid in frozen_w:
            skipped[wid] = "Gungnir carries it (rail_supergun: family and tier only)"
            continue
        if wid in players:
            skipped[wid] = "a player vehicle carries it too (player weapons do not change)"
            continue
        old = base.get(wid) or numbers(resolved(ws, wid))
        if old["laid"] and wid != SALVO_WEAPON:
            skipped[wid] = "laid by the boss system"
            continue
        row = table[fam][3]
        new = {"damage": row["damage"]}
        if not var:
            speed, dtype = family_round(base, [m for m in members[fam] if m in base] or [wid], fam)
            new["splash"] = row["core"]
            new["edge"] = row["edge"]
            if speed is not None:
                new["projectileSpeed"] = speed
            new["damageType"] = dtype
        old_core = old["splash"]
        new_core = new.get("splash", old_core)
        ratio = new_core / max(OLD_CORE_FLOOR, old_core) if new_core > 0 else 0.0
        bonus = ratio if ratio > BONUS_FROM else 1.0
        target = S.sustained(old)
        if wid == SALVO_WEAPON:
            rows[wid] = {"fam": fam, "var": var, "old": old, "new": new, "bonus": bonus, "target": target, "cad": {},
                         "dps": None, "note": "the ship's salvo (below)"}
            continue
        cad, dps, note = solve_cycle(old, row["damage"], target, bonus)
        rows[wid] = {"fam": fam, "var": var, "old": old, "new": new, "bonus": bonus, "target": target, "cad": cad,
                     "dps": dps, "note": note}
    return ws, assign, built, users, players, kids, rows, skipped


def fields_for(ws, wid, r):
    """The line's new fields: the round and the cadence where they differ, and out of a prompt 25 family whose block would
    override them (the block's other fields copied onto the line, so nothing else moves)."""
    w = ws.resolve(wid)
    f = {k: v for k, v in list(r["new"].items()) + list(r["cad"].items()) if w.get(k, 0 if k in ("splash", "edge") else None) != v}
    if not f:
        return {}
    p25 = w.get("weaponFamily")
    if p25 and p25 in ws.p25:
        block = ws.p25[p25]
        if any(k in block for k in f):
            f["weaponFamily"] = ""
            for k in block:
                if k not in ("id", "real") and k not in f:
                    f[k] = w.get(k)
    return f


def salvo_plan(built):
    """{boss: (old salvo, new fields, old DPS, new DPS)} for the bosses whose salvo fires the 406 mm."""
    out = {}
    row = F.FAMILIES["cal_406"][3]
    for bid, b in built.items():
        s = b.get("salvo")
        if not isinstance(s, dict) or s.get("weapon") != SALVO_WEAPON:
            continue
        turrets = sum(1 for p in b.get("parts") or [] if p.get("kind") == "maingun")
        old_dps = turrets * s.get("shells", 3) * s.get("damage", 300) / s.get("every", 10)
        new_every = turrets * SALVO_SHELLS * row["damage"] / old_dps
        bonus = 1.0
        old_core = s.get("radius", 7)
        if row["core"] > old_core * BONUS_FROM:
            bonus = row["core"] / old_core
        new = {"shells": SALVO_SHELLS, "damage": row["damage"], "radius": row["core"], "edge": row["edge"],
               "every": round(new_every * bonus, 1)}
        out[bid] = (s, new, old_dps, turrets * SALVO_SHELLS * row["damage"] / new["every"], turrets)
    return out


def cycle_of(old, cad):
    cd = cad.get("cooldown", old["cooldown"])
    if old["clip"] > 0:
        return (old["clip"] - 1) * cd + cad.get("clipReload", old["clipReload"])
    return cd + (old["burst"] - 1) * cad.get("burstInterval", old["burstInterval"])


def owner_of(users, wid, order):
    bs = [b for b, _ in users[wid]]
    return min(bs, key=lambda b: order.index(b)) if bs else None


def main():
    write = "--write" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    doc = Doc(F.PATH)
    data = doc.data()
    if os.path.exists(BASELINE):
        with open(BASELINE, encoding="utf-8") as fh:
            base = json.load(fh)
    else:
        ws0 = F.Weapons(data)
        built0, users0 = boss_users(data)
        base = {wid: numbers(ws0.resolve(wid)) for wid in users0 if wid in ws0.raw}
        base["__salvo__"] = {bid: copy.deepcopy(b["salvo"]) for bid, b in built0.items() if isinstance(b.get("salvo"), dict)}
        if write:
            with open(BASELINE, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(base, fh, indent=1, sort_keys=True)
    ws, assign, built, users, players, kids, rows, skipped = plan(data, base)
    order = list(built.keys())
    # Pins: a child line of a changed weapon that is not itself a boss weapon (nor a second round of one) keeps its old values.
    pins = {}
    for wid, r in rows.items():
        for c in descendants(kids, wid):
            if c in ws.rounds or (c in users and c not in players):
                continue
            cw = ws.resolve(c)
            for k in list(r["new"]) + list(r["cad"]) + ["weaponFamily"]:
                if k not in ws.raw[c] and cw.get(k) is not None:
                    pins.setdefault(c, {})[k] = cw.get(k)
    changed = 0
    for wid, r in rows.items():
        if only and owner_of(users, wid, order) != only:
            continue
        f = fields_for(ws, wid, r)
        if wid == SALVO_WEAPON and ws.resolve(wid).get("cooldown") != 60:
            f["cooldown"] = 60
        if f and F.set_on(doc, wid, f, ws.rounds):
            changed += 1
        for c in descendants(kids, wid):
            if c in pins:
                F.set_on(doc, c, pins[c], ws.rounds)
    # Second rounds of a changed gun fire at the gun's cadence: a round of a table family takes the family's round (a
    # variant its damage only); any other round keeps its DPS (its damage scaled by the gun's new cycle over the old).
    for rid, rraw in ws.rounds.items():
        gun = rraw.get("roundOf") or rraw.get("inherits")
        if gun not in rows or (only and owner_of(users, gun, order) != only):
            continue
        fam, var, _ = assign[rid]
        rw = ws.resolve(rid)
        t = F.FAMILIES.get(fam)
        g = rows[gun]
        if t and t[3]:
            f = {"damage": t[3]["damage"]}
            if not var:
                f.update({"splash": t[3]["core"], "edge": t[3]["edge"]})
        else:
            old_cycle = cycle_of(g["old"], {})
            new_cycle = cycle_of(g["old"], g["cad"])
            base_dmg = (base.get(rid) or {}).get("damage", rw.get("damage"))
            f = {"damage": round(base_dmg * new_cycle / old_cycle, 1)}
        f = {k: v for k, v in f.items() if rw.get(k, 0) != v}
        if f and F.set_on(doc, rid, f, ws.rounds):
            changed += 1
    salvos = salvo_plan(built)
    for bid, (s, new, *_r) in salvos.items():
        if only and only != bid:
            continue
        if bid not in [v["id"] for v in data["vehicles"]] or "salvo" not in next(v for v in data["vehicles"] if v["id"] == bid):
            continue  # inherited (Kraken takes Leviathan's)

        def fn(e: Entry, new=new):
            sub = e.sub("salvo")
            for k, v in new.items():
                sub.set(k, v, after="every")
            e.set_raw("salvo", sub.text)
        if doc.edit("vehicles", bid, fn):
            changed += 1
    print(f"{changed} lines changed{' (' + only + ')' if only else ''}")
    report = per_boss(ws, assign, built, users, rows, skipped, base, salvos)
    problems = validate(doc.data())
    for p in problems:
        print("VALIDATOR:", p)
    if write:
        doc.save()
        with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
        print("written")
    else:
        print(report[:6000])


def per_boss(ws, assign, built, users, rows, skipped, base, salvos):
    out = ["# Boss weapon families: before and after (prompt 34 L2)", "",
           "Written by `Tools/balance/p34_boss_families.py` from `Tools/balance/p34_boss_baseline.json` (the numbers before).",
           "The DPS is on paper: a weapon's sustained DPS on one target (a cycle's rounds over the cycle), before the boss's own",
           "factors (weaponDamage, rank, phases), which this pass does not change. Each changed weapon keeps its DPS, except",
           "where the family's core grew more than 1.25 times, which lengthens the cycle by the same ratio (the \"bonus\" column).",
           "No battle was run.", "",
           "## The family table (boss scale)", "",
           "| family | tier | damage a round | core / edge (m) |", "|---|---|---|---|"]
    for fid, name, tier, boss, _v in F.TABLE:
        if boss:
            ce = "-" if boss["core"] == 0 else f"{boss['core']:g} / {boss['edge']:g}" if boss["edge"] else f"{boss['core']:g} (one layer)"
            out.append(f"| {name} (`{fid}`) | T{tier} | {boss['damage']:g} | {ce} |")
    out += ["", "## Per boss", ""]
    tot = {}
    for bid, b in built.items():
        lines, before, after = [], 0.0, 0.0
        for k, wid in enumerate(S.mounts_of(b)):
            if not wid or wid not in ws.raw:
                continue
            old = base.get(wid) or numbers(ws.resolve(wid))
            if old.get("laid"):
                continue
            d0 = S.sustained(old)
            r = rows.get(wid)
            if r and r["dps"] is not None:
                d1 = r["dps"]
                n = old["clip"] if old["clip"] > 0 else old["burst"]
                cd = r["cad"]
                cyc = ((old["clip"] - 1) * cd.get("cooldown", old["cooldown"]) + cd.get("clipReload", old["clipReload"])) if old["clip"] > 0 \
                    else cd.get("cooldown", old["cooldown"]) + (old["burst"] - 1) * cd.get("burstInterval", old["burstInterval"])
                c0 = ((old["clip"] - 1) * old["cooldown"] + old["clipReload"]) if old["clip"] > 0 else old["cooldown"] + (old["burst"] - 1) * old["burstInterval"]
                nc = r["new"].get("splash", old["splash"])
                ne = r["new"].get("edge", old["edge"])
                lines.append(f"| {k} | `{wid}` | {r['fam']}{'/' + r['var'] if r['var'] else ''} | {old['damage']:g} x {n} / {c0:.2f} s = {d0:.0f} "
                             f"| {old['splash']:g} / {old['edge']:g} | {r['new']['damage']:g} x {n} / {cyc:.2f} s = {d1:.0f} | {nc:g} / {ne:g} "
                             f"| {'x' + format(r['bonus'], '.2f') if r['bonus'] > 1 else ''} | {r['note']} |")
            else:
                d1 = d0
                why = skipped.get(wid, "not in the table" if assign[wid][0] not in {t[0] for t in F.TABLE if t[3]} else "")
                lines.append(f"| {k} | `{wid}` | {assign[wid][0]}{'/' + assign[wid][1] if assign[wid][1] else ''} | {d0:.0f} | | unchanged | | | {why} |")
            if old.get("targets", "Ground") != "Air":
                before += d0
                after += d1
        sv = salvos.get(bid)
        if sv:
            s, new, od, nd, turrets = sv
            lines.append(f"| salvo | `{SALVO_WEAPON}` | cal_406 | {turrets} x {s.get('shells')} x {s.get('damage')} / {s.get('every')} s = {od:.0f} "
                         f"| {s.get('radius')} / 20 | {turrets} x {new['shells']} x {new['damage']} / {new['every']} s = {nd:.0f} | {new['radius']} / {new['edge']} | | barrels together |")
            before += od
            after += nd
        if not lines:
            continue
        tot[bid] = (before, after)
        out.append(f"### {bid}")
        out.append("")
        out.append(f"Ground DPS on paper (anti-air mounts left out): **{before:.0f} -> {after:.0f}** ({(after / before * 100 if before else 100):.0f} %).")
        out.append("")
        out.append("| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        out += lines
        out.append("")
    out += ["## Totals", "", "| boss | before | after | after / before |", "|---|---|---|---|"]
    for bid, (b0, b1) in tot.items():
        out.append(f"| {bid} | {b0:.0f} | {b1:.0f} | {b1 / b0 * 100 if b0 else 100:.0f} % |")
    out += ["", "## Left alone", ""]
    for wid, why in sorted(skipped.items()):
        out.append(f"- `{wid}`: {why}.")
    out.append("")
    return "\n".join(out)


def validate(data):
    """Prompt 34 L9 rule 1 (here for L2): within a family (variants aside) every boss weapon this pass changed has the same
    round: damage, speed, core, edge, damage type."""
    ws = F.Weapons(data)
    assign = F.assignment(ws)
    built, users = boss_users(data)
    players = player_users(data, built)
    frozen = {w for w, us in users.items() if any(b in FROZEN_BOSSES for b, _ in us)}
    groups = collections.defaultdict(list)
    for wid in users:
        if wid not in ws.raw or wid in players or wid in frozen:
            continue
        fam, var, _ = assign[wid]
        t = F.FAMILIES.get(fam)
        if not t or not t[3]:
            continue
        w = ws.resolve(wid)
        if w.get("laid") and wid != SALVO_WEAPON:
            continue
        key = (w.get("damage"),) if var else (w.get("damage"), w.get("projectileSpeed"), w.get("splash", 0), w.get("edge", 0), w.get("damageType"))
        groups[(fam, var)].append((key, wid))
    problems = []
    for (fam, var), items in groups.items():
        keys = {k for k, _ in items}
        if len(keys) > 1:
            problems.append(f"{fam}/{var or ''}: " + "; ".join(f"{k} {w}" for k, w in items))
    return problems


if __name__ == "__main__":
    main()
