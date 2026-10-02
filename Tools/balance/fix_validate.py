"""Full fix prompt L9: the validators for items 1-6 and 8 in one rerunnable run (DECISIONS "Sửa lỗi tổng hợp L9").

    python Tools/balance/fix_validate.py            # check every item (exit 1 on a failure); rewrites Docs/checks/fix_validate.json
    python Tools/balance/fix_validate.py 3 5        # only these items

Each item is also an EditMode test (`FixValidatorTests`), which runs in the build on the loaded catalog; this script reads the same
data (balance.json, the GLBs, the audio analyser's numbers) so the two give the same verdict. Item 7 (models) runs the pass 8
scorer (Tools/models/scan_prep.py); its test reads the "models" block this script writes.

1  The card's calibre / warhead is data: every weapon line carries one display field at most (caliberMm mm, warheadKg kg,
   powerKw kW, energyMj MJ), the one its family means (`fix_calibre.check`); no field mixes mm and kg.
2  Boss weapons of one weaponFamilyId (and variant) fire the same round everywhere: damage, core, edge, projectile speed. A
   variant needs a reason in weaponFamilyTable (`p34_validate.families`); the lines a boss shares with a player unit and
   Gungnir's own 40 mm guns are recorded exceptions.
3  No TOO FAST / TOO SLOW / UNIT against the real rate (`full_weapon_audit`) outside the recorded list (its `WAIT_NOTES`, with
   the reason, and Docs/balance/player_weapon_waitlist.md). The C# test reads Docs/checks/fix_validate.json (every used
   weapon's rounds a cycle and cycle: it fails when the data no longer matches, i.e. this script must be rerun).
4  A declared target layer takes damage from some round (`target_mask_check`).
5  Weapons from 203 mm (guns), 300 mm (rockets) and 400 kg (bombs) warn: tier T4+, a warning at least the escape formula of the
   warningRules block, the ring the damage area (the edge when it has two layers, else the core); the block itself holds the
   formula's floors; the bosses' laid salvos and cruise missiles likewise (`p34_warnings.check`, `p34_validate.rings`).
6  Every barrel of a gun that fires together has its Muzzle_b<k> (`p34_validate.muzzles`); every flare unit has >= 2
   Mount_Flare_* nodes on its model (and its _hd twin) and the flares are spawned from them (the view's source).
7  Models (Docs/models/MODEL_STANDARD.md, `scan_prep.score` in memory): the LOD0 triangles against the class budget (over budget is
   INFO only, the owner's rule of 02/10: the model is kept; under the floor is listed too), the Part_* / merged-node roles each class
   needs, the main weapon's muzzle and the run-time LOD1 (ModelScan's Builds/scan/<id>.json: triangles1 > 0; the 35-65 % band is
   a note). The pass 8 scores (Docs/models/scan/static_scores.csv) are the recorded list: a part missing there is backlog (a
   renaming job when the sheet shows it modelled inside a merged node, a rebuild when the visual grade is Kém); a part missing
   now and not recorded fails, and so does a main muzzle or a LOD1 that went missing. Scan dir: MB_SCAN_DIR, else the runner's
   Builds/scan, else ./Builds/scan; with none, LOD presence is a note.
8  No clip outside the armour-hit group is a "keng", and the per-size audio table rises (`Tools/sfx/analyze_sfx.py --check`,
   run in memory here).
"""
from __future__ import annotations

import collections
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import full_weapon_audit as W  # noqa: E402
import fix_calibre as C  # noqa: E402
import p34_barrels as R  # noqa: E402
import p34_boss_families as B  # noqa: E402
import p34_families as F  # noqa: E402
import p34_validate as V  # noqa: E402
import p34_warnings as PW  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

ROOT = F.ROOT
OUT = os.path.join(ROOT, "Docs", "checks", "fix_validate.json")
MODELS = V.MODELS
SCRIPTS = V.SCRIPTS

# Lines a boss shares with something else, or that are frozen: left out of item 2 with the reason (also in the audit's FAMILY_EXCEPT).
FAMILY_SHARED = dict(W.FAMILY_EXCEPT)

# Item 6: flare units whose model is not yet built with Mount_Flare_* points, with why. Fixing one fails the test until it is
# taken off this list (the list stays the truth).
FLARE_KNOWN_MISSING = {
    "stymphalos": "the Stymphalos model was built after the flare kit (Tools/blender/mb_flare_mounts.FLARE_UNITS has no entry): "
                  "waits for a Blender rebuild (pass 8's model work)",
}


def weapons_resolved(data):
    ws = F.Weapons(data)
    return ws, {raw["id"]: ws.resolve(raw["id"]) for raw in data["weapons"]}


# ------------------------------------------------------------------------------------------------------------- 1


def item1(data, ctx):
    problems = list(C.check(data))
    ws, res = ctx["ws"], ctx["res"]
    for wid, w in res.items():
        fields = [k for k in C.FIELDS if w.get(k)]
        if len(fields) > 1:
            problems.append(f"{wid}: mixes {fields}")
        cal = w.get("caliberMm") or 0
        kg = w.get("warheadKg") or 0
        if cal and kg:
            problems.append(f"{wid}: both mm and kg")
        # The real name's own calibre ("152 mm", "9M723 ... (700 kg)") must not contradict the field it prints.
        m = re.search(r"\((\d+(?:\.\d+)?) kg\)", w.get("real") or "")
        if m and cal:
            problems.append(f"{wid}: its name says {m.group(1)} kg but the card prints {cal:g} mm")
    return problems, []


# ------------------------------------------------------------------------------------------------------------- 2


def item2(data, ctx):
    problems = list(V.families(data))
    notes = []
    rows = ctx["rows"]
    groups = collections.defaultdict(list)
    for r in rows:
        w = r["w"]
        us = r["users"]
        if not us or w.get("damage", 0) <= 0 or not w.get("weaponFamilyId"):
            continue
        if not any(g == "boss" for g, _, _ in us):
            continue
        if any(g != "boss" for g, _, _ in us) or r["id"] in FAMILY_SHARED:
            notes.append(f"{r['id']}: shared with a player unit or frozen ({FAMILY_SHARED.get(r['id'], 'player rule')}): not in the family check")
            continue
        groups[(w["weaponFamilyId"], w.get("weaponVariantId") or "")].append(r)
    table = {t["id"]: t for t in data.get("weaponFamilyTable", [])}
    for (fam, var), items in sorted(groups.items()):
        sig = {(i["w"].get("damage"), i["w"].get("splash", 0), i["w"].get("edge", 0), i["w"].get("projectileSpeed")) for i in items}
        if len(sig) > 1:
            problems.append(f"{fam}/{var or '-'}: bosses differ in damage / core / edge / speed: " + "; ".join(
                f"{i['id']} {i['w'].get('damage')}/{i['w'].get('splash', 0)}/{i['w'].get('edge', 0)}/{i['w'].get('projectileSpeed')}" for i in items))
        if var and not (table.get(fam, {}).get("variants") or {}).get(var):
            problems.append(f"{fam}/{var}: a variant with no reason in weaponFamilyTable")
    return problems, sorted(set(notes))


# ------------------------------------------------------------------------------------------------------------- 3

RATE_FLAGS = ("TOO FAST", "TOO SLOW", "UNIT")


def recorded_ids():
    out = {}
    for ids, note in W.WAIT_NOTES:
        for i in ids:
            out[i] = note
    return out


def item3(data, ctx):
    recorded = recorded_ids()
    problems, notes = [], []
    export = {}
    for r in ctx["rows"]:
        if not r["users"]:
            continue
        nb = r["nb"]
        flags = [f for f in r["flags"] if f in RATE_FLAGS]
        reason = recorded.get(r["id"]) if flags else None
        export[r["id"]] = {"n": nb["n"], "cycle": round(nb["cycle"], 3), "flags": flags, "reason": reason or ""}
        if flags and reason is None:
            problems.append(f"{r['id']} ({r['w'].get('real') or '-'}): {', '.join(flags)} x{(r['ratio'] or 0):.2f} against the source, not on the recorded list")
        elif flags:
            notes.append(f"{r['id']}: {', '.join(flags)} x{(r['ratio'] or 0):.2f} (recorded)")
    # The recorded list may not carry a weapon that no longer fails (it would hide a regression).
    still = {i for i, e in export.items() if e["flags"]}
    stale = sorted(i for i in recorded if i in export and i not in still)
    ctx["rates"] = export
    ctx["stale_recorded"] = stale
    return problems, [f"{len(still)} recorded flags ({len([n for n in notes])}); recorded but no longer flagged: {', '.join(stale) or 'none'}"]


# ------------------------------------------------------------------------------------------------------------- 4


def item4(data, ctx):
    import target_mask_check as T
    T.main()
    with open(T.OUT, encoding="utf-8") as fh:
        m = re.search(r"## 1\. Declared layer with no damage \((\d+)\)", fh.read())
    n = int(m.group(1)) if m else -1
    problems = [f"{n} weapons declare a target layer no round can damage (Docs/checks/target_mask.md)"] if n != 0 else []
    return problems, ["the second-round list of target_mask.md is reported there (elite-only rounds), not a failure"]


# ------------------------------------------------------------------------------------------------------------- 5


def warns_py(w, rules, tier):
    """Mirror of WarningRules.Warns (the data's tier decides when the weapon has a family)."""
    if w.get("projectile") in ("Missile", "Drone") or w.get("laid") or w.get("beam") or float(w.get("splash", 0) or 0) <= 0:
        return False
    if tier is not None:
        return tier >= 4
    kind = w.get("projectile") or "Shell"
    size = float(w.get("size", 0) or 0)
    return (kind == "Shell" and size >= rules["gunMinMm"]) or (kind == "Bomb" and size >= rules["bombMinKg"]) or (
        kind == "Rocket" and size >= rules["rocketMinMm"])


def item5(data, ctx):
    rules = data["warningRules"]
    problems, notes = [], []
    if rules["floorT4"] < 2.5 or rules["floor406"] < 3.5 or rules["floorT5"] < 4 or rules["base"] < 0.5 or rules["escapeSpeed"] > 4.5:
        problems.append("warningRules: a floor or the escape term is under the prompt's (2.5 / 3.5 / 4 s, 0.5 s + core / 4.5 m/s)")
    if rules["cap"] > 6 or rules["cap"] < 4:
        problems.append(f"warningRules.cap {rules['cap']} (the prompt: at most 6 s, and the T5 floor is 4)")
    tiers = {t["id"]: t["tier"] for t in data.get("weaponFamilyTable", [])}
    for wid, w in ctx["res"].items():
        fam = w.get("weaponFamilyId")
        tier = tiers.get(fam)
        size = float(w.get("caliberMm") or 0)
        kg = float(w.get("warheadKg") or 0)
        kind = w.get("projectile") or "Shell"
        big = (kind == "Shell" and size >= rules["gunMinMm"]) or (kind == "Rocket" and size >= rules["rocketMinMm"]) or (
            kind == "Bomb" and kg >= rules["bombMinKg"])
        edge, core = float(w.get("edge", 0) or 0), float(w.get("splash", 0) or 0)
        warned = warns_py(w, rules, tier)
        if big and core > 0 and not (w.get("laid") or w.get("beam") or kind in ("Missile", "Drone")) and not warned:
            problems.append(f"{wid}: {size:g} mm / {kg:g} kg but its family {fam} is T{tier}: no warning")
        if not warned:
            continue
        if edge and edge < core:
            problems.append(f"{wid}: edge {edge:g} m under its core {core:g} m (the ring is the damage area)")
        floor = rules["floor406"] if fam == "cal_406" else rules["floorT5"] if (tier or 4) >= 5 else rules["floorT4"]
        need = min(rules["cap"], max(floor, rules["base"] + core / rules["escapeSpeed"]))
        if need < PW.escape(tier if tier is not None else 4, fam, core) - 1e-6:
            problems.append(f"{wid}: the block's formula gives {need:.2f} s, under the prompt's {PW.escape(tier or 4, fam, core):.2f} s")
    p, n = PW.check(data)
    problems += p
    notes += n
    problems += V.rings(data)
    return problems, notes


# ------------------------------------------------------------------------------------------------------------- 6


def glb_nodes(model):
    path = os.path.join(MODELS, model + ".glb")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        b = fh.read()
    n = struct.unpack_from("<I", b, 12)[0]
    return [x.get("name", "") for x in json.loads(b[20:20 + n])["nodes"]]


def flare_units(data):
    built, _ = B.boss_users(data)
    veh = {v["id"]: v for v in data["vehicles"]}
    veh.update(built)
    kinds = {s["id"] for s in data["skills"] if s.get("kind") == "Flares"}

    def res(v, d=0):
        if "inherits" in v and v["inherits"] in veh and d < 5:
            b = dict(res(veh[v["inherits"]], d + 1))
            b.update(v)
            return b
        return v

    out = {}
    for vid, v in veh.items():
        r = res(v)
        if r.get("flareCharges") or set(r.get("skills") or []) & kinds:
            # An elite draws its original's model (VehicleDef.Model is set from EliteOf at load).
            model = V.model_of(veh, v)
            if r.get("eliteOf") and not r.get("model"):
                model = V.model_of(veh, veh.get(r["eliteOf"], v))
            out[vid] = model
    return out


def item6(data, ctx):
    problems = list(V.muzzles(data))
    notes = []
    units = flare_units(data)
    for vid, model in sorted(units.items()):
        for m in (model, model + "_hd"):
            nodes = glb_nodes(m)
            if nodes is None:
                if m == model:
                    problems.append(f"{vid}: model '{m}' is not built")
                continue
            count = sum(1 for x in nodes if x.startswith("Mount_Flare_"))
            if count >= 2:
                if vid in FLARE_KNOWN_MISSING:
                    problems.append(f"{vid}: now has {count} Mount_Flare_* points: take it off FLARE_KNOWN_MISSING")
            elif vid in FLARE_KNOWN_MISSING:
                notes.append(f"{vid} ({m}): {count} Mount_Flare_* (known: {FLARE_KNOWN_MISSING[vid]})")
            else:
                problems.append(f"{vid}: model '{m}' has {count} Mount_Flare_* nodes (needs >= 2)")
    # The flares are spawned from them: the view reads the Mount_Flare_* nodes first and the release uses the view's points.
    fx = open(os.path.join(SCRIPTS, "Game", "Views", "VehicleView.FxPoints.cs"), encoding="utf-8").read()
    mun = open(os.path.join(SCRIPTS, "Game", "Effects", "EffectsDirector.Munitions.cs"), encoding="utf-8").read()
    if not re.search(r"FlarePoints\s*=>\s*_flarePoints\s*\?\?=\s*FlareMounts\(\)", fx) or "IsFlareMount" not in fx:
        problems.append("VehicleView.FlarePoints no longer reads the Mount_Flare_* nodes first")
    if ".FlarePoints" not in mun:
        problems.append("EffectsDirector.Munitions no longer spawns the flares from the view's FlarePoints")
    ctx["flare_units"] = units
    return problems, notes + [f"{len(units)} flare units"]


# ------------------------------------------------------------------------------------------------------------- 7

SCAN_DIRS = [os.environ.get("MB_SCAN_DIR") or "", r"C:/Users/Winka/Projects/MachineBrigade-runner/Builds/scan", os.path.join(ROOT, "Builds", "scan")]
RECORDED_SCORES = os.path.join(ROOT, "Docs", "models", "scan", "static_scores.csv")
VISUAL_SCORES = os.path.join(ROOT, "Docs", "models", "scan", "visual_scores.md")


def scan_dir():
    for d in SCAN_DIRS:
        if d and os.path.isdir(d) and any(n.endswith(".json") for n in os.listdir(d)):
            return d
    return None


def visual_grades():
    """{model: visual grade} from the pass 8 visual table (its 6th column)."""
    out = {}
    if not os.path.exists(VISUAL_SCORES):
        return out
    for line in open(VISUAL_SCORES, encoding="utf-8"):
        m = re.match(r"^\| `([^`]+)`", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6:
                out[m.group(1)] = cells[5]
    return out


def item7(data, ctx):
    import csv
    import tempfile
    from pathlib import Path
    sys.path.insert(0, os.path.join(ROOT, "Tools", "models"))
    import scan_prep as S

    sd = scan_dir()
    tmp = Path(tempfile.gettempdir()) / "fix_validate_static_scores.csv"
    rows = S.score(Path(sd) if sd else Path(ROOT) / "Builds" / "scan", out=tmp, quiet=True)
    recorded = {}
    if os.path.exists(RECORDED_SCORES):
        with open(RECORDED_SCORES, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                recorded[r["model"]] = r
    visual = visual_grades()
    problems, notes = [], []
    over, under, rename, rebuild, lod_band, unscanned, fixed = [], [], {}, {}, [], [], []
    for r in rows:
        m = r["model"]
        rec = recorded.get(m)
        tris, lo, hi = int(r["triangles"]), int(r["budgetMin"]), int(r["budgetMax"])
        if tris > hi:
            over.append({"model": m, "class": r["budgetClass"], "triangles": tris, "max": hi, "over": r["overPct"]})
        elif tris < lo:
            under.append({"model": m, "class": r["budgetClass"], "triangles": tris, "min": lo})
        parts = set(r["partsMissing"].split())
        known = set(rec["partsMissing"].split()) if rec else set()
        new = sorted(parts - known)
        if new:
            problems.append(f"{m} ({r['class']}): required parts missing that the pass 8 scores did not record: {', '.join(new)}")
        old_parts = sorted(parts & known)
        if old_parts:
            # Modelled but not named (the sheet shows it inside a merged node): rename / split; a visual Kém: rebuild.
            (rebuild if visual.get(m) == "Kém" else rename)[m] = old_parts
        gone = sorted(known - parts)
        if gone:
            fixed.append(f"{m}: {', '.join(gone)}")
        main_mz = [x for x in r["muzzlesMissing"].split("; ") if "(main)" in x]
        if main_mz and not (rec and "(main)" in rec.get("muzzlesMissing", "")):
            problems.append(f"{m}: main muzzle missing ({main_mz[0]})")
        elif main_mz:
            notes.append(f"{m}: main muzzle missing (recorded in the pass 8 backlog: {main_mz[0]})")
        scan = os.path.join(sd, m + ".json") if sd else None
        if scan and os.path.exists(scan):
            try:
                with open(scan, encoding="utf-8") as fh:
                    sj = json.load(fh)
            except (OSError, ValueError):
                sj = {}
            if not sj.get("triangles1"):
                problems.append(f"{m}: no run-time LOD1 in its scan ({os.path.basename(scan)}: triangles1 = {sj.get('triangles1')})")
            elif r["lod1Share"] != "" and not (S.LOD1_BAND[0] <= float(r["lod1Share"]) <= S.LOD1_BAND[1]):
                lod_band.append(f"{m} {float(r['lod1Share']):.0%}")
        else:
            unscanned.append(m)
    gone_models = sorted(set(recorded) - {r["model"] for r in rows})
    summary = {"models": len(rows), "overBudgetInfo": len(over), "underBudget": len(under),
               "withMissingParts": sum(1 for r in rows if r["partsMissing"]),
               "missingPartsTotal": sum(len(r["partsMissing"].split()) for r in rows),
               "renamingBacklog": len(rename), "rebuildBacklog": len(rebuild), "lod1OutsideBand": len(lod_band),
               "scanned": len(rows) - len(unscanned), "notScanned": len(unscanned), "failures": len(problems), "scanDir": sd or ""}
    notes.append(f"{len(rows)} models; over budget {len(over)} (INFO, kept: owner rule 02/10); under the floor {len(under)}")
    notes.append(f"missing parts on {summary['withMissingParts']} models ({summary['missingPartsTotal']}): renaming backlog {len(rename)}, "
                 f"rebuild backlog {len(rebuild)} (recorded by pass 8)")
    notes.append(f"LOD1: {summary['scanned']} scanned, outside 35-65 % on {len(lod_band)} (note); not scanned: "
                 + (", ".join(unscanned) if unscanned else "none") + ("" if sd else " (no scan dir: LOD presence not checked)"))
    if fixed:
        notes.append("recorded parts now present (rerun scan_prep.py to refresh static_scores.csv): " + "; ".join(fixed))
    if gone_models:
        notes.append("recorded models no longer scored: " + ", ".join(gone_models))
    ctx["models"] = {
        "summary": summary,
        "overBudgetInfo": over, "underBudget": under,
        "renamingBacklog": rename, "rebuildBacklog": rebuild,
        "lod1OutsideBand": lod_band, "notScanned": unscanned,
        "failures": problems,
        "grades": {r["model"]: {"class": r["class"], "triangles": int(r["triangles"]), "budget": f"{r['budgetMin']}-{r['budgetMax']}",
                                "budgetStatus": r["budgetStatus"], "partsMissing": r["partsMissing"].split(),
                                "lod1Share": r["lod1Share"], "staticGrade": r["staticGrade"], "visualGrade": visual.get(r["model"], "")}
                   for r in rows},
    }
    return problems, notes


# ------------------------------------------------------------------------------------------------------------- 8


def item8(data, ctx):
    sys.path.insert(0, os.path.join(ROOT, "Tools", "sfx"))
    import numpy as np  # noqa: F401
    import analyze_sfx as A

    clips = A.run()
    lib = A.library()
    per_bank = {}
    for rel, m in clips.items():
        per_bank.setdefault(A.bank_of(rel), []).append(m)
    per_bank = {b: {k: float(np.mean([m[k] for m in ms])) for k in ("lufs_mmax", "lufs", "sub150", "tail")} for b, ms in per_bank.items()}
    rows = A.size_table(per_bank, lib)
    problems = [f"audio size table does not rise: {p}" for p in A.rises(rows, "shot") + A.rises(rows, "blast")]
    problems += [f"keng outside the armour-hit group: {c}" for c in A.keng_outside_armour(clips, lib)]
    return problems, [f"{len(clips)} clips analysed"]


# ------------------------------------------------------------------------------------------------------------- run

ITEMS = {1: item1, 2: item2, 3: item3, 4: item4, 5: item5, 6: item6, 7: item7, 8: item8}
TITLES = {1: "calibre / warhead is data", 2: "same family, same round", 3: "rates against the source", 4: "declared targets can be damaged",
          5: "warnings and rings", 6: "muzzles and flare mounts", 7: "models: budget (info), parts, LOD", 8: "audio: no keng, size table rises"}


def main(argv):
    want = [int(a) for a in argv if a.isdigit()] or list(ITEMS)
    data = Doc(F.PATH).data()
    W.DATA.update(data)
    rows, built, ws = W.audit(data)
    ctx = {"rows": rows, "built": built, "ws": ws, "res": weapons_resolved(data)[1]}
    failed = 0
    for k in want:
        problems, notes = ITEMS[k](data, ctx)
        for n in notes:
            print(f"note [{k}]: {n}")
        for p in problems:
            print(f"FAIL [{k}]: {p}")
        failed += bool(problems)
        print(f"{k} {TITLES[k]}: {'OK' if not problems else str(len(problems)) + ' problems'}")
    if 3 in want or 7 in want:
        # Each run refreshes the blocks of the items it ran and keeps the others (item 3: weapons; item 7: models).
        out = {}
        if os.path.exists(OUT):
            try:
                with open(OUT, encoding="utf-8") as fh:
                    out = json.load(fh)
            except (OSError, ValueError):
                out = {}
        out["note"] = ("Written by Tools/balance/fix_validate.py. weapons (item 3): each weapon a unit carries, its rounds a cycle and cycle, "
                       "the audit's rate flags and the recorded reason; FixValidatorTests fails when the data no longer matches: rerun the "
                       "script. models (item 7): the model check (over budget is info only, the owner's rule), the backlogs and the failures.")
        if 3 in want:
            out["recordedRateFlags"] = ctx.get("rates", {}) and {i: e["reason"] for i, e in ctx["rates"].items() if e["flags"]}
            out["weapons"] = ctx.get("rates", {})
        if 7 in want and "models" in ctx:
            out["models"] = ctx["models"]
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
