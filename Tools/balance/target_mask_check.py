"""Prompt 29 appendix: the weapon target-mask check, read statically from balance.json (no Unity).

    python Tools/balance/target_mask_check.py            # writes Docs/checks/target_mask.md, exit 1 on a finding

For every gun (a weapon a vehicle mounts or that is no other gun's second round, does damage and is not intercept-only) and every
layer its "targets" declares (Air; Ground, which covers vehicles and structures), the highest damage-type multiplier over
the rounds valid for that layer (its own round when it reaches the layer, and each second round whose rule takes the layer
and whose round reaches it) must be above 0 against aircraft (Air), ground vehicles (Ground) and structures (Ground). A
second round whose rule no target can ever meet is listed too: it cannot reach the layer its rule names, it is elite-only
and no elite or rank-7 branch carries the gun, or an earlier round of the same gun takes every target it would (the first
round whose rule suits a target wins, CombatSystem.RoundIndexFor). It mirrors TargetMaskTests (EditMode), which checks the
loaded catalog the same way. Only the two weapons of the appendix were fixed (B6-mask); everything else is reported.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from jsonc_edit import loads  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
OUT = os.path.join(ROOT, "Docs", "checks", "target_mask.md")

USE = {"air": 1, "ground": 2, "armour": 4, "light": 8, "structure": 16, "cluster": 32, "any": 3}
AIR, GROUND, ARMOUR, LIGHT, STRUCTURE, CLUSTER = 1, 2, 4, 8, 16, 32
# Target situations a gun meets (CombatSystem.Suits): flying; a structure; an armoured or a light vehicle, alone or clustered.
SITUATIONS = [
    ("aircraft", True, lambda u: u & AIR),
    ("structure", False, lambda u: u & (GROUND | STRUCTURE)),
    ("armour", False, lambda u: u & (GROUND | ARMOUR)),
    ("armour, clustered", False, lambda u: u & (GROUND | ARMOUR | CLUSTER)),
    ("light", False, lambda u: u & (GROUND | LIGHT)),
    ("light, clustered", False, lambda u: u & (GROUND | LIGHT | CLUSTER)),
]


def resolve(entries):
    by = {e["id"]: e for e in entries if "id" in e}
    memo = {}

    def r(e, depth=0):
        if e["id"] in memo:
            return memo[e["id"]]
        if "inherits" not in e or depth > 4:
            out = dict(e)
        else:
            base = dict(r(by[e["inherits"]], depth + 1))
            base.update(e)
            out = base
        memo[e["id"]] = out
        return out

    return {e["id"]: r(e) for e in entries if "id" in e}


def layers(w):
    t = w.get("targets", "Ground")
    return {"All": (True, True), "Air": (True, False), "Ground": (False, True)}.get(t, (False, True))


def can_target(w, flying):
    if w.get("interceptOnly"):
        return False
    a, g = layers(w)
    return a if flying else g


def type_of(table, w, kind):
    dt = w.get("damageType", "Kinetic")
    v = table[dt][kind]
    if kind == "Structure" and w.get("thermobaric") and dt == "HighExplosive":
        v = max(table.get("thermobaric", 2.0), v)
    return v


def refs(obj, out):
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            refs(v, out)


def main():
    d = loads(open(BALANCE, encoding="utf-8").read())
    table = d["damageTable"]
    raw = d["weapons"] + d.get("secondRounds", {}).get("rounds", [])
    weapons = resolve(raw)
    rounds_of: dict[str, list] = {}
    for wid, w in weapons.items():
        if "he" in w and w["he"] in weapons:
            rounds_of.setdefault(wid, []).append((weapons[w["he"]], LIGHT | STRUCTURE, False))
        if "air" in w and w["air"] in weapons:
            rounds_of.setdefault(wid, []).append((weapons[w["air"]], AIR, False))
    round_ids = set()
    for e in d.get("secondRounds", {}).get("rounds", []):
        use = 0
        for word in e.get("for", []):
            use |= USE[word]
        rounds_of.setdefault(e["roundOf"], []).append((weapons[e["id"]], use, bool(e.get("elite"))))
        round_ids.add(e["id"])
    for lst in rounds_of.values():
        for r, _, _ in lst:
            round_ids.add(r["id"])
    vehicles = resolve(d["vehicles"])
    carriers: dict[str, list] = {}
    for v in vehicles.values():
        s = set()
        refs({k: x for k, x in v.items() if k != "id"}, s)
        for wid in s & set(weapons):
            carriers.setdefault(wid, []).append(v)

    mask, unmet = [], []
    for wid in sorted(weapons):
        w = weapons[wid]
        # A second round is checked as its gun's; one a vehicle also mounts as its own gun is checked as a gun too.
        if wid in round_ids and wid not in carriers:
            continue
        if float(w.get("damage", 0) or 0) <= 0 or w.get("interceptOnly"):
            continue
        air, ground = layers(w)
        second = rounds_of.get(wid, [])

        def best(kind, flying):
            vals = [type_of(table, w, kind)] if can_target(w, flying) else []
            for r, use, _ in second:
                takes = (use & AIR) if flying else (use & ~AIR)
                if takes and can_target(r, flying):
                    vals.append(type_of(table, r, kind))
            return max(vals) if vals else 0.0

        used = ", ".join(sorted(v["id"] for v in carriers.get(wid, []))) or "no carrier"
        if air and best("Air", True) <= 0:
            mask.append((wid, "aircraft", w.get("damageType"), w.get("targets"), used))
        if ground and best("Ground", False) <= 0:
            mask.append((wid, "ground vehicles", w.get("damageType"), w.get("targets"), used))
        if ground and best("Structure", False) <= 0:
            mask.append((wid, "structures", w.get("damageType"), w.get("targets"), used))

        elite_carrier = any(v.get("elite") or v.get("branchOf") for v in carriers.get(wid, []))
        for k, (r, use, elite) in enumerate(second):
            why = None
            if elite and not elite_carrier:
                why = "elite-only, and no elite or rank-7 branch carries the gun"
            else:
                wins = False
                for _, flying, rule in SITUATIONS:
                    for j, (r2, use2, elite2) in enumerate(second):
                        if elite2 and not elite and not elite_carrier:
                            continue
                        if not can_target(r2, flying) or not rule(use2):
                            continue
                        if j == k:
                            wins = True
                        break
                    if wins:
                        break
                if not wins:
                    reach = [n for n, f, rule in SITUATIONS if rule(use) and can_target(r, f)]
                    why = "its round reaches no target its rule names" if not reach else "an earlier round takes every target it would"
            if why:
                unmet.append((wid, r["id"], "+".join(x for x in USE if x != "any" and USE[x] & use), why))

    lines = [
        "# Target-mask check (prompt 29 appendix)",
        "",
        "Written by `python Tools/balance/target_mask_check.py` from balance.json (a static read, no Unity); the same check is",
        "`TargetMaskTests` (EditMode) on the loaded catalog. A gun's declared layer (Air; Ground = vehicles and structures)",
        "with a highest damage-type multiplier of 0 over its valid rounds is listed under 1; a second round whose rule can",
        "never be met under 2. Fixed in this pass (B6-mask, `Tools/balance/p29_apply.py`, `Docs/balance/manifest_p29_appendix.json`):",
        "`gun_100_river` and `gun_155_crusader` All -> Ground (high explosive does 0 to aircraft; neither has a second round that",
        "reaches aircraft). Everything below is reported only (the appendix: no rebalance of second rounds here).",
        "",
        f"## 1. Declared layer with no damage ({len(mask)})",
        "",
    ]
    if mask:
        lines += ["| weapon | layer | damage type | targets | carried by |", "|---|---|---|---|---|"]
        lines += [f"| `{a}` | {b} | {c} | {t} | {u} |" for a, b, c, t, u in mask]
    else:
        lines.append("None.")
    lines += ["", f"## 2. Second rounds whose rule is never met ({len(unmet)})", ""]
    if unmet:
        lines += ["| gun | round | for | why |", "|---|---|---|---|"]
        lines += [f"| `{a}` | `{b}` | {c} | {w} |" for a, b, c, w in unmet]
    else:
        lines.append("None.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{len(mask)} mask findings, {len(unmet)} unmet rounds -> {OUT}")
    return 1 if mask or unmet else 0


if __name__ == "__main__":
    sys.exit(main())
