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

import math

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
}


def run(step, wr, wb, report):
    if step == "B1":
        b1(wr, wb, report)
        return "B1: model sizes (sheet Kiểm tra từng mục)"
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
