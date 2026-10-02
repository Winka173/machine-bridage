"""Prompt 25 importer, B1: model sizes (sheet "Kiểm tra từng mục", rows "Kích thước model"; see import_xlsx.py).

A vehicle's drawn size is data: "modelSize" [length, width, height] in metres, the model's whole box (gun included, as
the sheet measures it). The game fits the model's length to it (VehicleView.DrawScaleOf), so an old model and one
rebuilt at another size are drawn the same. The rest follows from it:
  * "scale" is kept to match the model the game has (a model the B2 model agent rebuilt: the box it was built at,
    DECISIONS 25B2; any other: its .glb in Resources/Models), so every place that draws by the data's scale alone (air
    drops, strike aircraft) agrees; an aircraft's scale is over the 0.85 it is drawn at (VehicleView.AirShrink);
  * the hull ("length", "width", which the loader multiplies by the scale; the capsule's radius is 0.46 x the width)
    is the rebuilt model's own hull footprint, else the old hull resized with the sheet's box, so it keeps its share
    of the drawn length and width; aircraft keep theirs (their hit radius), as does every hit radius;
  * a boss is sized by its "size" (BossTemplates.Resize: the scale, the hit radius, parts, mounts, ramp and death blast
    together, over the model's own units, which B2 keeps), and its active protection and crash with it; a variant of a
    resized boss keeps its own drawn size.
Rows: "Đổi" takes the sheet's box ("dài ≥ N m": that length, the box's shape kept), "Giữ" records the size drawn now; a
model B2 rebuilt is drawn at its built box (B2 built it to the sheet's target, 0.8 x real on the ground, 0.4 x real in
the air), which wins over the row. Towers keep their sizes (the sheet: "vừa cỡ ô").
"""
from __future__ import annotations

import collections
import math
import os
import re

import glb_bounds as G
import import_xlsx as X

SHEET = "Kiểm tra từng mục"
AIR_SHRINK = 0.85  # VehicleView.AirShrink (DECISIONS 21H)

# DECISIONS 25B2: the box each model was rebuilt at by the model agent (for "scale": 1.0), and its hull footprint
# (length, width) on the ground; aircraft keep their hit radius as their hull. They are merged after this step: a model
# listed here is measured from this box, not from the .glb in the tree (the same box once B2's models are in).
BUILT_B2 = {
    "main_battle_tank": ((7.79, 3.07, 2.30), (6.10, 3.07)),
    "twin_tank": ((8.96, 3.53, 2.64), (7.02, 3.53)),
    "flame_tank": ((7.12, 2.66, 1.87), (5.75, 2.66)),
    "armored_car": ((4.78, 2.08, 1.49), (4.44, 2.08)),
    "scout_jeep": ((2.64, 1.40, 1.41), (2.64, 1.40)),
    "fpv_carrier": ((7.41, 2.04, 2.88), (7.41, 2.04)),
    "lancet_truck": ((7.41, 2.02, 2.70), (7.41, 2.02)),
    "command_vehicle": ((5.64, 2.08, 2.14), (5.64, 2.08)),
    "fighter_jet": ((8.64, 5.85, 2.15), None),
    "attack_helicopter": ((6.35, 4.44, 2.02), None),
    "swarm_carrier": ((11.93, 16.30, 4.79), None),
    "sky_gunship": ((11.93, 16.30, 4.82), None),
    "daedalus": ((37.08, 20.42, 12.80), None),
}

INTRO = {
    "B1": ("Every \"Kích thước model\" row of \"Kiểm tra từng mục\": the vehicle's drawn box goes into the data (modelSize, "
           "length x width x height in metres; the game fits the model's length to it), with its scale for the model the "
           "game has and its hull (collision) in step. \"Đổi\" takes the sheet's box, \"Giữ\" records today's; a model the "
           "B2 model agent rebuilt (DECISIONS 25B2) is drawn at its built box, the sheet's target (0.8 x real on the "
           "ground, 0.4 x real in the air). Bosses' \"Kích thước\" rows resize the boss (its size). Towers' rows are counted, "
           "not listed: they keep their sizes."),
    "B3": ("Every row of \"Kích thước đạn\": a round's drawn length (its model x its scale, as the sheet measures it: "
           "0.8 x real launched from the ground, 0.5 x real from an aircraft, 0.8 m at least) goes into the data "
           "(roundLength; the game fits whichever model flies it to that length), with projectileScale for the model the "
           "game has. A row stands for every weapon the design document drew with the same model at the same scale (it "
           "lists one row a model and scale, under its first weapon) that fires the same round: a shell row its whole "
           "group, another row its weapon's family. The 203 mm shells take 1.3 x the 155 mm's length (prompt 25 C.3); "
           "the Kh-29L and the GBU-39 fly models of their own (ASSET_DEBT: until they are built, the Maverick and the "
           "GBU-12 stand in, at the new lengths). \"Giữ\" rows keep their rounds."),
    "C4": ("Prompt 25 C.4. The unit: balance.json gives turn rates in degrees a second (its header), VehicleDef keeps "
           "radians a second (SimMath.DegToRad on load); the design document printed the radians under a degrees label, "
           "which is why the sheet reads 60 deg/s as 1. Its column is in degrees now (Tools/docs/programme.py). The "
           "sheet's \"turret faster than the hull\" rows (\"1 / 2\" in radians a second: the hull kept, the turret "
           "2 rad/s, 115 deg/s) were applied by A1 Trung; they are checked here. The other turn-rate rows are counted, "
           "not listed: \"Giữ\"."),
}


def run(step, wr, wb, report):
    if step == "B1":
        b1(wr, wb, report)
        return "B1: model sizes (sheet Kiểm tra từng mục)"
    if step == "B3":
        b3(wr, wb, report)
        return "B3: round sizes (sheet Kích thước đạn)"
    if step == "C4":
        c4(wr, wb, report)
        return "C.4: turn rates (sheets Kiểm tra từng mục, Thay đổi chi tiết)"
    return None


# ----------------------------------------------------------------------------------------------------------------
# Models and how they are drawn


def model_of(g, vid):
    """The model a vehicle is drawn with (Catalog: its own "model", else its parent's, else its id)."""
    v = g.vehicles_raw[vid]
    if v.get("model"):
        return v["model"]
    parent = v.get("inherits") or v.get("variantOf")
    return model_of(g, parent) if parent in g.vehicles_raw else vid


def box_of(model):
    """(length, width, height) of a model at scale 1: its B2 built box, else its .glb's; None without a model."""
    if model in BUILT_B2:
        return BUILT_B2[model][0]
    return G.length_width_height(model)


def shrink(v):
    return AIR_SHRINK if v.get("flying") and not v.get("boss") else 1.0


def boss_scale(g, vid):
    """A boss's drawn scale: its data scale x its size (BossTemplates.Resize), a variant's over its base's."""
    v = g.vehicles_raw[vid]
    if v.get("variantOf") in g.vehicles_raw:
        return boss_scale(g, v["variantOf"]) * float((v.get("variant") or {}).get("size", 0.7))
    return float(v.get("scale", 1) or 1) * float(v.get("size", 1) or 1)


def drawn_now(g, vid):
    """The box a vehicle is drawn at today: its modelSize, else its model in the tree (its .glb) at its draw scale."""
    v = g.vehicle(vid)
    if v.get("modelSize"):
        return tuple(float(x) for x in v["modelSize"])
    box = G.length_width_height(model_of(g, vid))
    if box is None:
        return None
    k = boss_scale(g, vid) if (v.get("boss") or v.get("rank")) else float(v.get("scale", 1) or 1) * shrink(v)
    return tuple(x * k for x in box)


def r2(x):
    return round(float(x) + 1e-9, 2)


def box_text(b):
    return " x ".join(X.fmt(r2(x)) for x in b)


# ----------------------------------------------------------------------------------------------------------------
# B1


def b1(wr, wb, report):
    g = wr.game
    step = "B1"
    _, rows = X.sheet(wb, SHEET)
    for r in rows:
        item = str(r[2] or "")
        if item.startswith("Kích thước model"):
            vehicle_row(wr, report, step, r)
        elif item == "Kích thước":
            vid = r[0]
            base = vid.split(".")[0]
            if base in g.vehicles_raw and g.is_boss(base) and r[4] == "Đổi":
                boss_row(wr, report, step, r, rows)
            else:
                why = "a boss: kept" if base in g.vehicles_raw and g.is_boss(base) else "a tower: kept (the sheet: fits its slot)"
                report.add(step, SHEET, vid, item, "already" if base in g.vehicles_raw else "skipped",
                           why if base in g.vehicles_raw else "no such id in balance.json", listed=False)


def vehicle_row(wr, report, step, r):
    g = wr.game
    vid, item, cur_text, result, prop = r[0], r[2], r[3], r[4], r[5]
    if vid not in g.vehicles_raw:
        report.add(step, SHEET, vid, item, "skipped", "no such vehicle id in balance.json")
        return
    v = g.vehicle(vid)
    model = model_of(g, vid)
    box = box_of(model)
    if box is None:
        report.add(step, SHEET, vid, item, "skipped", f"no model {model} to size")
        return
    now = drawn_now(g, vid)
    notes = []
    if model in BUILT_B2:
        target = BUILT_B2[model][0]
        notes.append(f"B2 rebuilt it at {box_text(target)}, the sheet's target (DECISIONS 25B2)")
        if result == "Đổi":
            notes.append(f"the row: {prop}")
        else:
            notes.append(f"the row kept {cur_text}")
    elif result == "Đổi":
        n = X.nums(prop)
        if "≥" in str(prop) and n:
            k = max(1.0, n[0] / now[0])  # at least that long, its shape kept
            target = tuple(x * k for x in now)
            notes.append(f"the row: {prop}")
        elif len(n) >= 3:
            target = tuple(n[:3])
        else:
            report.add(step, SHEET, vid, item, "skipped", f"no box in the proposal '{prop}'")
            return
    else:
        target = now
    target = tuple(r2(x) for x in target)
    old = {k: v.get(k) for k in ("modelSize", "scale", "length", "width")}
    scale_old = float(v.get("scale", 1) or 1)
    scale = round(target[0] / (box[0] * shrink(v)), 4)
    if X.close(scale, scale_old, 0.005):
        scale = scale_old  # within half a percent: the scale the data had
    changed = []

    def fn(e):
        after = "scale" if e.has("scale") else "id"
        if e.get("modelSize") != list(target):
            e.set("modelSize", list(target), after=after)
            changed.append(f"modelSize {box_text(target)}")
        if not X.close(scale, scale_old, 1e-6) or (not e.has("scale") and scale != 1):
            e.set("scale", scale)
            changed.append(f"scale {X.fmt(scale_old)} -> {X.fmt(scale)}")
        if v.get("flying"):
            return  # an aircraft's hull is its hit radius
        hull = hull_for(g, vid, model, now, target, scale_old)
        if hull is None:
            return
        was = [float(v[k]) * scale_old if k in v else None for k in ("length", "width")]
        for key, want in zip(("length", "width"), hull):
            val = r2(want / scale)
            if not X.close(val, v.get(key), 1e-6):
                e.set(key, val, after="radius" if e.has("radius") else after)
        if None in was or any(abs(h / w - 1) > 0.005 for h, w in zip(hull, was)):
            old_hull = "from its radius" if None in was else box_text(was)
            changed.append(f"hull {old_hull} -> {box_text(hull)} m")

    wr.doc.edit("vehicles", vid, fn)
    g.refresh()
    drawn = tuple(x * target[0] / box[0] for x in box)  # the model the game has, fitted to the length
    off = [(n, d, t) for n, d, t in zip(("width", "height"), drawn[1:], target[1:]) if abs(d / t - 1) > 0.1]
    if off:
        DISAGREE.append((vid, model, target, drawn))
        notes.append("its model, fitted to the length, is " + ", ".join(f"{X.fmt(r2(d))} m {n}" for n, d, t in off))
    if result == "Giữ" and model not in BUILT_B2:
        outcome = "already"
        detail = f"kept at {box_text(target)}"
    else:
        outcome = "applied" if changed or old["modelSize"] != list(target) else "already"
        detail = f"{box_text(now)} -> {box_text(target)}"
    if changed:
        detail += "; " + ", ".join(changed)
    if notes:
        detail += "; " + "; ".join(notes)
    report.add(step, SHEET, vid, item, outcome, detail)


# Vehicles whose model, fitted to its length, is more than 10 % off the sheet's width or height (B2's to redraw).
DISAGREE = []


def hull_for(g, vid, model, now, target, scale_old):
    """The hull (collision) length and width in metres: B2's built footprint, else the old hull resized with the box."""
    v = g.vehicle(vid)
    if model in BUILT_B2 and BUILT_B2[model][1]:
        return BUILT_B2[model][1]
    if "length" not in v or "width" not in v:
        return None
    k = (target[0] / now[0], target[1] / now[1])
    hull = (float(v["length"]) * scale_old, float(v["width"]) * scale_old)
    if any(abs(x - 1) >= 0.005 for x in k):
        hull = (hull[0] * k[0], hull[1] * k[1])
    # Never longer or wider than the box it is drawn in (a hull that stood out of its old model is brought inside).
    capped = (min(target[0], hull[0]), min(target[1], hull[1]))
    if all(abs(x - 1) < 0.005 for x in k) and capped == hull:
        return None  # the size is kept: so is the hull
    return capped


def boss_row(wr, report, step, r, rows):
    """A boss's "Kích thước" row: its size so its drawn length is the sheet's; its variants keep theirs."""
    g = wr.game
    vid, item, prop = r[0], r[2], r[5]
    model = model_of(g, vid)
    box = box_of(model)
    n = X.nums(prop)
    if box is None or not n:
        report.add(step, SHEET, vid, item, "skipped", f"no model or no length in '{prop}'")
        return
    v = g.vehicles_raw[vid]
    base = float(v.get("scale", 1) or 1)
    size_old = float(v.get("size", 1) or 1)
    want = n[0]
    size = round(want / (box[0] * base), 3)
    ratio = size / size_old
    # The variants' drawn size before this change (kept).
    variants = {k: drawn_now(g, k) for k, w in g.vehicles_raw.items() if w.get("variantOf") == vid}
    changed = []
    if not X.close(size, size_old, 1e-6):
        def fn(e):
            e.set("size", size, after="frame" if e.has("frame") else "id")
            if e.has("aps") and e.get("aps"):
                a = e.get("aps")
                e.set_sub("aps", "radius", round(float(a["radius"]) * ratio, 1))
                changed.append(f"active protection {X.fmt(a['radius'])} -> {X.fmt(round(float(a['radius']) * ratio, 1))} m")
            if e.has("tiers") and (e.get("tiers") or {}).get("crash"):
                t = e.sub("tiers")
                c = t.sub("crash")
                crash = c.get("radius")
                if crash:
                    c.set("radius", round(float(crash) * math.sqrt(ratio), 1))
                    changed.append(f"crash blast {X.fmt(crash)} -> {X.fmt(round(float(crash) * math.sqrt(ratio), 1))} m")
                if c.has("debrisAt"):
                    c.set_raw("debrisAt", X.fmt([[round(x * ratio, 1) for x in p] for p in c.get("debrisAt")]))
                    changed.append("crash debris spread with the hull")
                t.set_raw("crash", c.text)
                e.set_raw("tiers", t.text)
        wr.doc.edit("vehicles", vid, fn)
        g.refresh()
        changed.insert(0, f"size {X.fmt(size_old)} -> {X.fmt(size)}")
    for k, before in variants.items():
        w = g.vehicles_raw[k]
        vs_old = float((w.get("variant") or {}).get("size", 0.7))
        vs = round(before[0] / (box_of(model_of(g, k))[0] * boss_scale(g, vid)), 3)
        if not X.close(vs, vs_old, 1e-6):
            wr.doc.edit("vehicles", k, lambda e: e.set_sub("variant", "size", vs))
            g.refresh()
            changed.append(f"{k} (variant) size {X.fmt(vs_old)} -> {X.fmt(vs)}, kept at {X.fmt(r2(before[0]))} m")
    drawn = tuple(x * size * base for x in box)
    detail = f"{box_text(drawn)} (the row: {prop})"
    if model in BUILT_B2:
        detail += f"; measured on B2's rebuilt model, {box_text(BUILT_B2[model][0])} at scale 1"
    if changed:
        detail += "; " + ", ".join(changed)
    report.add(step, SHEET, vid, item, "applied" if changed else "already", detail)


# ----------------------------------------------------------------------------------------------------------------
# B3: round sizes ("Kích thước đạn")

ROUND_SHEET = "Kích thước đạn"
# Round models the sheet asks for ("cần model riêng") that are not built yet (ASSET_DEBT), and the model that flies for
# each until it is: WeaponEffects.RoundStandIns mirrors it.
STAND_IN = {"kh29l": "maverick", "gbu39": "gbu12"}
RATIO_203 = 1.3  # prompt 25 C.3: 203 mm rounds are drawn 1.3 x the 155 mm's
ROUNDS_TSV = os.path.join(X.ROOT, "Docs", "balance", "round_sizes.tsv")
RULE_203 = "the 203 mm rule"


def native(model):
    """A round model's length at scale 1 (its stand-in's while it is not built); None without either."""
    b = G.length_width_height(model) if model else None
    if b is None and model in STAND_IN:
        b = G.length_width_height(STAND_IN[model])
    return b[0] if b else None


def drawn_round(g, wid):
    """How long a weapon's round is drawn (before the view's legibility boost, WeaponEffects.SizeOf)."""
    w = g.weapon(wid)
    if w.get("roundLength"):
        return float(w["roundLength"])
    n = native(w.get("projectileModel"))
    return n * float(w.get("projectileScale", 1) or 1) if n else None


def is_shell(w):
    return (w.get("projectile") or "Shell") == "Shell"


def model_id(real):
    """A round model's id from its real name: "Kh-29L" -> kh29l, "GBU-39 SDB (110 kg)" -> gbu39."""
    return re.sub(r"[^a-z0-9]", "", str(real).split()[0].lower())


def own_family(g, wid):
    fam = g.raw_weapons[wid].get("weaponFamily")
    return fam if fam in g.families else None


def calibre(g, wid):
    return float(g.weapon(wid).get("size", 0) or 0)


def b3(wr, wb, report):
    import steps_a3 as F
    g = wr.game
    step = "B3"
    _, rows = X.sheet(wb, ROUND_SHEET)
    groups = collections.defaultdict(list)  # (model, scale) -> weapons: one row of the design document's round table
    for wid in g.raw_weapons:
        w = g.weapon(wid)
        if w.get("projectileModel"):
            groups[(w["projectileModel"], float(w.get("projectileScale", 1) or 1))].append(wid)

    targets = {}  # weapon -> (length, its own new model or None)
    row_of = {}   # weapon -> the row (its weapon id) that set it
    kept = []     # the weapons of the "Giữ" rows
    others = {}   # row -> weapons of its group that fire another round (left as they are)
    for r in rows:
        model, wid, real, cur, result, reason = r[0], r[1], r[2], r[3], r[10], str(r[11] or "")
        if wid not in g.raw_weapons:
            report.add(step, ROUND_SHEET, wid, real, "skipped", "no such weapon id in balance.json")
            continue
        w = g.weapon(wid)
        group = groups[(w.get("projectileModel"), float(w.get("projectileScale", 1) or 1))]
        if result != "Đổi":
            kept += group
            report.add(step, ROUND_SHEET, wid, real, "already",
                       f"kept: {X.fmt(cur)} m ({model} x {X.fmt(float(w.get('projectileScale', 1) or 1))}; the rule gives "
                       f"{X.fmt(round(float(r[8]), 2))} m)")
            continue
        if is_shell(w):
            members = list(group)  # every shell drawn alike: the row is theirs
        elif own_family(g, wid):
            fam = own_family(g, wid)
            members = [m for m in g.raw_weapons if own_family(g, m) == fam]
        else:
            name = F.real_name(w.get("real") or "")
            members = [m for m in group if F.real_name(g.weapon(m).get("real") or "") == name]
        new_model = model_id(real) if "model riêng" in reason else None
        for m in members:
            targets[m] = (float(r[8]), new_model if m == wid else None)
            row_of[m] = wid
        others[wid] = [m for m in group if m not in members]

    OTHERS_BEFORE.clear()
    OTHERS_BEFORE.update({m: drawn_round(g, m) for ms in others.values() for m in ms})

    # The 203 mm shells: 1.3 x the 155 mm's length, the 155 mm as this step leaves it.
    def length_now(m):
        return targets[m][0] if m in targets else drawn_round(g, m)

    shells = [m for m in g.raw_weapons if g.weapon(m).get("projectileModel") == "shell_155"]
    l155 = collections.Counter(round(length_now(m), 3) for m in shells if calibre(g, m) == 155 and length_now(m)).most_common(1)
    l155 = l155[0][0] if l155 else None
    if l155:
        for m in shells:
            if calibre(g, m) == 203:
                targets[m] = (round(RATIO_203 * l155, 3), None)
                row_of.setdefault(m, RULE_203)

    # Write: on a family when all its members take one length, else on each weapon's own line.
    moved = collections.defaultdict(list)  # row -> what moved
    by_family = collections.defaultdict(list)
    for m in targets:
        if own_family(g, m):
            by_family[own_family(g, m)].append(m)
    done = set()
    for fam, ms in by_family.items():
        members = [m for m in g.raw_weapons if own_family(g, m) == fam]
        values = {targets[m] for m in members if m in targets}
        if set(members) != set(ms) or len(values) != 1:
            continue
        length, new_model = next(iter(values))
        if new_model:
            continue
        model = g.families[fam].get("projectileModel") or g.weapon(members[0]).get("projectileModel")
        scale = round(length / native(model), 4)
        before = {m: drawn_round(g, m) for m in members}
        entry = g.families[fam]
        if not (X.close(entry.get("roundLength"), length, 1e-6) and X.close(entry.get("projectileScale"), scale, 1e-6)):
            def fn(e, length=length, scale=scale):
                # In A3's order (it writes the families again on every run): after the round weight, else the model.
                after = next(k for k in ("roundWeight", "projectileModel", "splash") if e.has(k))
                e.set("roundLength", length, after=after)
                e.set("projectileScale", scale, after="roundLength")
            wr.doc.edit("weaponFamilies", fam, fn)
            for m in members:
                wr.doc.edit("weapons", m, lambda e: [e.remove(k) for k in X.ROUND_KEYS])
            g.refresh()
            for m in members:
                moved[row_of[m]].append(f"{m} {X.fmt(round(before[m] or 0, 2))} -> {X.fmt(length)} m")
        done.update(members)
    for m in sorted(targets):
        if m in done:
            continue
        length, new_model = targets[m]
        w = g.weapon(m)
        model = new_model or w.get("projectileModel")
        scale = round(length / native(model), 4)
        before = drawn_round(g, m)
        want = {"projectileModel": new_model} if new_model else {}
        want.update({"roundLength": length, "projectileScale": scale})
        change = {k: v for k, v in want.items() if not X.close(w.get(k), v, 1e-6)}
        if not change:
            continue

        def fn(e, change=change):
            for k, v in change.items():
                e.set(k, v, after="projectileModel" if e.has("projectileModel") and k != "projectileModel" else "id")
        wr.doc.edit("weapons", m, fn)
        g.refresh()
        text = f"{m} {X.fmt(round(before or 0, 2))} -> {X.fmt(length)} m"
        if new_model:
            text += (f", a model of its own, {new_model} (it flew {w.get('projectileModel')}; "
                     f"{STAND_IN.get(new_model, new_model)} stands in until it is built)")
        moved[row_of[m]].append(text)

    # The report: a line a row, and one a 203 mm shell no row names.
    for r in rows:
        wid, real, result = r[1], r[2], r[10]
        if wid not in g.raw_weapons or result != "Đổi":
            continue
        members = sorted(m for m in targets if row_of.get(m) == wid)
        detail = (f"{X.fmt(r[3])} -> {X.fmt(round(float(r[8]), 3))} m (launched from {r[6]}: {X.fmt(r[7])} x its real "
                  f"{X.fmt(r[4])} m, 0.8 m at least)")
        if calibre(g, wid) == 203 and l155:
            detail += (f"; a 203 mm shell: {X.fmt(targets[wid][0])} m, {X.fmt(RATIO_203)} x the 155 mm's {X.fmt(l155)} m "
                       f"(prompt 25 C.3), not the row's rule")
        detail += "; weapons: " + ", ".join(members)
        follow = [m for m in others.get(wid, []) if not X.close(drawn_round(g, m), OTHERS_BEFORE.get(m), 1e-3)]
        stay = [m for m in others.get(wid, []) if m not in follow]
        if follow:
            detail += "; another round on the same model and scale that inherits a member, so follows it: " + ", ".join(follow)
        if stay:
            detail += "; another round on the same model and scale, kept: " + ", ".join(stay)
        if moved.get(wid):
            detail += "; moved: " + "; ".join(moved[wid])
        report.add(step, ROUND_SHEET, wid, real, "applied" if moved.get(wid) else "already", detail)
    for m in sorted(targets):
        if row_of.get(m) == RULE_203:
            report.add(step, ROUND_SHEET, m, g.weapon(m).get("real"), "applied" if moved.get(RULE_203) else "already",
                       f"no row of its own; the 203 mm rule: {X.fmt(targets[m][0])} m")

    # What the tests check (SizeSheetTests): every round this step set and the kept rows' rounds, with their lengths.
    tsv = ["# Generated by Tools/balance/import_xlsx.py (B3): each weapon of the sheet \"Kích thước đạn\", the model it "
           "flies and its drawn length in metres (model x scale, before the view's legibility boost).",
           "\t".join(["weapon", "model", "length", "source"])]
    for m in sorted(set(targets) | set(kept)):
        w = g.weapon(m)
        tsv.append("\t".join([m, w.get("projectileModel") or "", X.fmt(round(drawn_round(g, m), 3)), "B3" if m in targets else "kept"]))
    with open(ROUNDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(tsv) + "\n")


OTHERS_BEFORE = {}  # the drawn length of the rows' other rounds before B3 writes


# ----------------------------------------------------------------------------------------------------------------
# C.4: turn rates


def c4(wr, wb, report):
    g = wr.game
    step = "C4"
    for sheet_name in (SHEET, "Thay đổi chi tiết"):
        _, rows = X.sheet(wb, sheet_name)
        for r in rows:
            vid, item = r[0], str(r[2] or "")
            if not item.startswith("Tốc độ xoay"):
                continue
            result, prop = (r[4], r[5]) if sheet_name == SHEET else ("Đổi", r[4])
            if vid not in g.vehicles_raw:
                report.add(step, sheet_name, vid, item, "skipped", "no such vehicle id in balance.json")
                continue
            v = g.vehicle(vid)
            hull, turret = v.get("turnRate"), v.get("turretTurnRate")
            if result != "Đổi":
                report.add(step, sheet_name, vid, item, "already", f"kept ({r[3]} rad/s)", listed=False)
                continue
            n = X.nums(prop)
            want = round(n[1] * X.DEG_PER_RAD) if len(n) > 1 else None
            ok = want is not None and abs(float(turret) - want) <= 1
            detail = (f"hull {X.fmt(hull)} deg/s ({X.fmt(round(float(hull) / X.DEG_PER_RAD, 2))} rad/s, the row's {X.fmt(n[0])}), "
                      f"turret {X.fmt(turret)} deg/s = {X.fmt(round(float(turret) / X.DEG_PER_RAD, 2))} rad/s (the row's {X.fmt(n[1])}), "
                      "turret faster than the hull")
            if ok:
                report.add(step, sheet_name, vid, item, "already", detail + "; applied by A1 Trung")
            else:
                wr.vehicle_field(vid, "turretTurnRate", want)
                report.add(step, sheet_name, vid, item, "applied", f"turretTurnRate {X.fmt(turret)} -> {X.fmt(want)} deg/s")
