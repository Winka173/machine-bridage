"""Prompt 34 L3: warnings by escape time, the data and the validator (DECISIONS "Prompt 34 L3").

    python Tools/balance/p34_warnings.py           # validate (exit 1 on a problem)
    python Tools/balance/p34_warnings.py --write   # also write the salvo's warning and its ring (a second run changes nothing)

The rule: every T4+ round warns max(the tier's floor, 0.5 s + core / 4.5 m/s) before it lands, at most 6 s. The floors are
T4 2.5 s, the 406 mm 3.5 s, and 4 s for the 800 mm and the other T5 super weapons. `WeaponDef.EscapeWarning` holds the same formula.
  * A boss's own guns: the Sim keeps the round in the air for at least the warning (CombatSystem.Launch), so their check
    is that the round is not guided (a guided round has no fixed fall point) and has a core to warn of.
  * A ship's salvo (the 406 mm): `salvo.warn` >= the formula for its weapon's family and the salvo's radius; its warning
    support's ring is the edge (`radius`) with the core inside (`blast`).
  * Cruise missiles (T4): `cruise.warn` >= the formula for their radius.
  * Gungnir's bombard (T5, 3 s) is the named exception: prompt 29 G1 fixed its pattern and prompt 34 gives it its family
    and tier only. It is reported, not failed.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import p34_families as F  # noqa: E402
import p34_boss_families as B  # noqa: E402
from jsonc_edit import Doc, Entry  # noqa: E402

FLOOR_T4, FLOOR_406, FLOOR_T5 = 2.5, 3.5, 4.0
ESCAPE, CAP = 4.5, 6.0
EXCEPTIONS = {"rail_supergun": "prompt 29 G1 keeps Gungnir's bombard as it is (3 s); prompt 34 gives it family and tier only"}


def escape(tier, family, core):
    if tier < 4:
        return 0.0
    floor = FLOOR_406 if family == "cal_406" else FLOOR_T5 if tier >= 5 else FLOOR_T4
    return min(CAP, max(floor, 0.5 + max(0.0, core) / ESCAPE))


def warn_needed_up(x):
    """The formula's value rounded up to a tenth (the data's precision)."""
    import math
    return math.ceil(x * 10 - 1e-9) / 10


def check(data):
    ws = F.Weapons(data)
    assign = F.assignment(ws)
    built, users = B.boss_users(data)
    problems, notes = [], []
    for wid, us in sorted(users.items()):
        if wid not in ws.raw:
            continue
        fam, var, tier = assign[wid]
        if tier < 4:
            continue
        w = ws.resolve(wid)
        guided = w.get("projectile") in ("Missile", "Drone")
        if w.get("laid"):
            continue
        if guided:
            notes.append(f"{wid} (T{tier}, guided): no fixed fall point, no ring")
        elif float(w.get("splash", 0)) <= 0:
            problems.append(f"{wid} (T{tier}): no core to warn of")
    for bid, b in built.items():
        s = b.get("salvo")
        if isinstance(s, dict) and s.get("weapon") in ws.raw:
            fam, _, tier = assign[s["weapon"]]
            need = escape(tier, fam, s.get("radius", 7))
            if s.get("warn", 2.6) + 1e-6 < need:
                problems.append(f"{bid}.salvo: warn {s.get('warn')} s < {need:.2f} s ({fam}, core {s.get('radius')} m)")
        c = b.get("cruise")
        if isinstance(c, dict) and c.get("weapon") in ws.raw:
            fam, _, tier = assign[c["weapon"]]
            need = escape(tier, fam, c.get("radius", 16))
            if c.get("warn", 4.5) + 1e-6 < need:
                problems.append(f"{bid}.cruise: warn {c.get('warn', 4.5)} s < {need:.2f} s")
        bo = b.get("bombard")
        if isinstance(bo, dict) and bo.get("weapon") in ws.raw:
            fam, _, tier = assign[bo["weapon"]]
            w = ws.resolve(bo["weapon"])
            need = escape(tier, fam, w.get("splash", 0))
            if bo.get("warn", 3) + 1e-6 < need:
                msg = f"{bid}.bombard: warn {bo.get('warn', 3)} s < {need:.2f} s"
                (notes if bid in EXCEPTIONS else problems).append(msg + (f" (exception: {EXCEPTIONS[bid]})" if bid in EXCEPTIONS else ""))
    return problems, notes


def write(doc: Doc):
    data = doc.data()
    built, _ = B.boss_users(data)
    ws = F.Weapons(data)
    assign = F.assignment(ws)
    changed = 0
    for v in data["vehicles"]:
        s = v.get("salvo")
        if not isinstance(s, dict) or s.get("weapon") not in ws.raw:
            continue
        fam, _, tier = assign[s["weapon"]]
        need = warn_needed_up(escape(tier, fam, s.get("radius", 7)))
        if s.get("warn", 2.6) < need:
            def fn(e: Entry, need=need):
                sub = e.sub("salvo")
                sub.set("warn", need, after="every")
                e.set_raw("salvo", sub.text)
            if doc.edit("vehicles", v["id"], fn):
                changed += 1
        # The warning's ring is the edge, its core inside (StrikeEffects draws `radius`, EscapeWarnings the core `blast`).
        sup = s.get("warning")
        if sup:
            edge = s.get("edge") or min(20, 2 * s.get("radius", 7))

            def fs(e: Entry, edge=edge, core=s.get("radius", 7)):
                e.set("radius", edge, after="kind")
                e.set("blast", core, after="radius")
            if doc.edit("supports", sup, fs):
                changed += 1
    return changed


def main():
    doc = Doc(F.PATH)
    if "--write" in sys.argv:
        n = write(doc)
        doc.save()
        print(f"{n} entries written")
    problems, notes = check(doc.data())
    for n in notes:
        print("note:", n)
    for p in problems:
        print("PROBLEM:", p)
    print("warnings: OK" if not problems else f"warnings: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
