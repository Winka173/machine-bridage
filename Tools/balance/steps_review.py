"""Prompt 25 importer, A1-review: the rows the first pass left for a measurement, applied (see import_xlsx.py).

The owner, 30/09: "các chỗ nào cần xem lại thì cứ đổi luôn, cho đúng với công thức trong đó, và mọi thứ trong đó cứ
thêm hết sửa hết, rồi ta sẽ loại trừ sau nếu dư thừa" (change whatever needs a review, to the sheet's formulas; add and
change everything in it; what is too much is taken out later). So every row that waited for the test phase is applied
with the sheet's numbers and formulas, and so is every row a step had deferred or skipped for any reason but a later
task (bosses C1 and C2, names D1, models B2):
  * "Xem lại" (Kiểm tra từng mục): speeds and vision take the sheet's number; health its formula, the class's median
    health a CP (its "Lớp" in "Phương tiện", the vehicles of the class the sheet does not flag) times the vehicle's CP;
  * "Theo dõi" and "Đã giảm ở đợt 2" (Cân bằng lần 2) name no number: what they rest on (the CP, the round-2 cuts) is in;
  * the changes a measurement was to judge (their words and numbers disagree) stand as applied, the numbers' side;
  * the Skyranger's AHEAD gun (the one weapon row with a blank cell): its rounds a magazine are the game's (the row keeps
    the gun, the cell is blank), and its cadence follows the sheet's formula like every other weapon's (A2);
  * weapons the sheet does not list are the game's own (A2's new ones among them, created there);
  * "Đổi" rows of "Kiểm tra từng mục" no "Thay đổi chi tiết" row repeats: checked against the data, applied where they
    are not in, skipped where they contradict the sheet itself.
"""
from __future__ import annotations

import re
import statistics

import import_xlsx as X
import steps_more as M

STEP = "A1-review"
CHECK = "Kiểm tra từng mục"
SECOND = "Cân bằng lần 2"

INTRO = ("The owner's rule of 30/09 (after the first pass): every row that waited for a measurement is applied with the "
         "sheet's numbers and formulas, and every row a step deferred or skipped for any reason but a later task (bosses "
         "C1-C2, names D1, models B2). Health rows take the sheet's formula: the class's median health a CP (the \"Lớp\" of "
         "\"Phương tiện\", over the class's vehicles the sheet does not flag) times the vehicle's CP. \"Đổi\" rows of "
         "\"Kiểm tra từng mục\" that no \"Thay đổi chi tiết\" row repeats are checked against the data here.")


def run(wr, wb, report, weapon_rows):
    xem_lai(wr, wb, report)
    second_round(wr, wb, report)
    measured(wr, report)
    ahead(wr, report, weapon_rows)
    not_in_sheet(wr, report, weapon_rows)
    unrepeated(wr, wb, report)


# ----------------------------------------------------------------------------------------------------------------


def xem_lai(wr, wb, report):
    g = wr.game
    _, rows = X.sheet(wb, CHECK)
    _, vrows = X.sheet(wb, "Phương tiện")
    klass = {r[0]: r[2] for r in vrows}
    flagged = {r[0] for r in rows if r[4] == "Xem lại" and r[2] == "Máu"}
    for r in rows:
        if r[4] != "Xem lại":
            continue
        vid, item, cur, prop = r[0], r[2], r[3], r[5]
        if vid not in g.vehicles_raw:
            report.add(STEP, CHECK, vid, item, "skipped", "no such vehicle id in balance.json")
            continue
        v = g.vehicle(vid)
        # "applied" against the sheet's own "Hiện tại" (what the first pass kept), so a re-run reports the same.
        if item == "Tốc độ":
            want = X.nums(prop)[-1]
            wr.vehicle_field(vid, "speed", want)
            report.add(STEP, CHECK, vid, item, "applied" if not X.close(float(cur), want) else "already",
                       f"speed {X.fmt(cur)} -> {X.fmt(want)} m/s (the sheet: {prop})")
        elif item == "Tầm nhìn":
            want = X.nums(prop)[-1]
            wr.vehicle_field(vid, "vision", want)
            report.add(STEP, CHECK, vid, item, "applied" if not X.close(float(cur), want) else "already",
                       f"vision {X.fmt(cur)} -> {X.fmt(want)} m (the sheet: {prop})")
        elif item == "Máu":
            c = klass.get(vid)
            members = [m for m, k in klass.items() if k == c and m in g.vehicles_raw and m not in flagged
                       and (g.vehicle(m).get("cp") or 0) > 0 and g.vehicle(m).get("hp")]
            median = statistics.median(float(g.vehicle(m)["hp"]) / float(g.vehicle(m)["cp"]) for m in members)
            want = round(median * float(v["cp"]))
            t = g.toughness
            before = round(float(cur) / t)  # the sheet shows health after the vehicles' toughness
            wr.vehicle_field(vid, "hp", want)
            report.add(STEP, CHECK, vid, item, "applied" if before != want else "already",
                       f"health {X.fmt(before)} -> {X.fmt(want)} ({X.fmt(round(before * t))} -> {X.fmt(round(want * t))} after toughness x{X.fmt(t)}): "
                       f"the class \"{c}\"'s median {X.fmt(round(median, 1))} a CP x its {X.fmt(v['cp'])} CP (the sheet: {prop}; "
                       f"the median over {', '.join(members)})")
        else:
            report.add(STEP, CHECK, vid, item, "skipped", f"no rule for the item '{item}'")


def second_round(wr, wb, report):
    g = wr.game
    _, rows = X.sheet(wb, SECOND)
    for r in rows:
        vid, verdict = r[0], r[9]
        if verdict not in ("Theo dõi", "Đã giảm ở đợt 2") or vid not in g.vehicles_raw:
            continue
        cp = g.vehicle(vid).get("cp")
        if verdict == "Theo dõi":
            detail = (f"the row names no number (its words: {r[10]}); the price it rests on, {X.fmt(r[4])} CP after round 1, is in "
                      f"(the data: {X.fmt(cp)})")
        else:
            detail = (f"the row names no number; the round-2 cuts it points to are in (A1: {ROUND_TWO.get(vid, 'its rows')}), "
                      f"{X.fmt(cp)} CP")
        report.add(STEP, SECOND, vid, verdict, "already", detail)


ROUND_TWO = {
    "attack_jet": "one FAB-250 a load, 18 CP, the GSh-30-2's 70-round magazine",
    "heavy_bomber": "seven FAB-500s a sortie, the Kh-101's speed and blast",
}


# The changes a measurement was to judge (steps_more.TO_MEASURE), with the numbers before and after.
MEASURED = {
    "zu23": "sustained 143 -> 70 a second (7 a round, 25 a second, 50 a magazine, 3 s)",
    "twin_30_flak": "sustained 252 -> 171 a second",
    "tower_flak_30": "sustained 193 -> 131 a second (the sheet's anti-aircraft value 300 -> 240 was its aim)",
    "hq_flak": "sustained 157 -> 140 a second",
    "scout_rockets": "24 -> 6 Hydras a load, 5 CP",
    "flamethrower": "23.5 -> 21 a tick on every target",
}


def measured(wr, report):
    g = wr.game
    for vid, wid, why in M.TO_MEASURE:
        if vid in g.vehicles_raw:
            report.add(STEP, "Vũ khí đề xuất / Thay đổi chi tiết", vid, wid or "card", "applied",
                       f"{MEASURED.get(wid, '')}: the sheet's numbers stand (A1, A2), no measurement pending ({why})")


def ahead(wr, report, weapon_rows):
    """The Skyranger's AHEAD gun: its blank rounds cell is the game's magazine, and its cadence the sheet's formula."""
    g = wr.game
    wid = "twin_35_ahead"
    row = weapon_rows.get(wid)
    if row is None or wid not in g.raw_weapons:
        return
    w = g.weapon(wid)
    rounds = int(w.get("clip") or w.get("burst") or 1)
    row = list(row)
    if row[X.W_N] is None:
        row[X.W_N] = rounds
    if row[X.W_N0] is None:
        row[X.W_N0] = rounds
    X.apply_weapon_row(wr, row, X.Report(), STEP)
    want = X.sheet_dps(row)
    w = g.weapon(wid)
    after = X.cadence(w)[3]
    # Before, as the sheet has it: its rest (the game's change time before this step).
    before = dict(w, clipReload=row[X.W_REST0])
    report.add(STEP, "Vũ khí đề xuất", wid, "cadence", "applied" if not X.close(w.get("clipReload"), row[X.W_REST0]) else "already",
               f"rounds a magazine: the game's {rounds} (the row keeps the gun; its cell is blank); the sheet's formula "
               f"(damage x rounds / (rounds / rate + rest)) gives {want:.1f} a second: clipReload {X.fmt(row[X.W_REST0])} -> "
               f"{X.fmt(w.get('clipReload'))} (rest + one gap, A2's rule), {X.cadence(before)[3]:.1f} -> {after:.1f} a second")
    # The DPS test's row (A2 wrote it blank).
    lines = open(M.EXPECT, encoding="utf-8").read().splitlines()
    out = [M.TAB.join([wid, f"{want:.3f}", "rounds a magazine: the game's (the sheet's cell is blank), in its formula"])
           if ln.split(M.TAB)[0] == wid else ln for ln in lines]
    with open(M.EXPECT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def not_in_sheet(wr, report, weapon_rows):
    g = wr.game
    created = {"gun_launched_atgm": "the light tank's gun-launched missile", "missile_57e6": "the Pantsir's 57E6"}
    for wid in g.raw_weapons:
        if wid in weapon_rows or wid == "none":
            continue
        users = g.users(wid)
        if wid in created:
            detail = f"A2's new weapon ({created[wid]}), created from the change note and mounted: {', '.join(users)}"
        else:
            detail = "the game's own weapon, not in the sheet: nothing to apply (its family and blast rule reach it)"
        report.add(STEP, "Vũ khí đề xuất", wid, "weapon", "already", detail, listed=wid in created)


def unrepeated(wr, wb, report):
    """ "Đổi" rows of "Kiểm tra từng mục" that no row of "Thay đổi chi tiết" repeats (A1 read only that sheet)."""
    import json
    g = wr.game
    _, rows = X.sheet(wb, CHECK)
    _, trows = X.sheet(wb, "Thay đổi chi tiết")
    repeated = {(r[0], str(r[2])) for r in trows}
    refs = json.load(open(X.REFS, encoding="utf-8"))
    vision_of = {r[0]: r for r in rows if r[2] == "Tầm nhìn"}
    for r in rows:
        vid, item, cur, result, prop = r[0], str(r[2] or ""), r[3], r[4], str(r[5] or "")
        if result != "Đổi" or (vid, item) in repeated:
            continue
        if item.startswith(("Kích thước", "Tốc độ xoay", "Tên")):
            continue  # B1, C4, D1
        base = vid.split(".")[0]
        if base not in g.vehicles_raw:
            report.add(STEP, CHECK, vid, item, "skipped", "no such id in balance.json")
            continue
        if g.is_boss(base):
            report.add(STEP, CHECK, vid, item, "deferred", "a boss: task C1 (sheet Boss đề xuất)")
            continue
        v = g.vehicle(vid)
        n = X.nums(prop)
        outcome, detail = "already", ""
        if item.startswith("Giá ("):
            ok = n and X.close(float(v.get("cp", 0)), n[0])
            outcome, detail = ("already", f"{X.fmt(v.get('cp'))} CP (B.7)") if ok else ("skipped", f"the data has {v.get('cp')} CP")
            if not ok and n:
                wr.vehicle_field(vid, "cp", int(n[0]))
                outcome, detail = "applied", f"cp {v.get('cp')} -> {int(n[0])}"
        elif item.startswith("Máu"):
            m = re.search(r"máu\s*([\d.,]+)|([\d.,]+)\s*máu", prop) or re.search(r"([\d.,]+)", prop)
            want = X.num(next(x for x in m.groups() if x))
            data = round(want / g.toughness)
            if abs(float(v["hp"]) * g.toughness / want - 1) <= 0.01:
                detail = f"health {X.fmt(v['hp'])} ({X.fmt(round(v['hp'] * g.toughness))} after toughness): the sheet's {X.fmt(want)}"
            else:
                before = v["hp"]
                wr.vehicle_field(vid, "hp", data)
                outcome, detail = "applied", f"health {X.fmt(before)} -> {X.fmt(data)} (the sheet's {X.fmt(want)} after toughness)"
        elif item.startswith("Giáp"):
            m = re.search(r"trước\s*(\d)\s*/\s*hông\s*(\d)\s*/\s*sau\s*(\d)\s*/\s*nóc\s*(\d)", prop)
            faces = [int(x) for x in m.groups()] if m else None
            if faces is None:
                m = re.search(r"giáp\s*(\d)", prop)
                faces = [int(m.group(1))] if m else None
            have = X.armour_faces(v)
            if faces and have[:len(faces)] == faces:
                detail = f"armour {'/'.join(map(str, have))}: the sheet's {prop}"
            elif faces:
                new = faces if len(faces) == 4 else [faces[0]] + have[1:]
                before = v.get("armour")
                wr.vehicle_field(vid, "armour", new)
                outcome, detail = "applied", f"armour {before} -> {new}"
            else:
                outcome, detail = "skipped", f"no armour levels in '{prop}'"
        elif item.startswith("Tốc độ"):
            want = n[0]
            if X.close(float(v.get("speed", 0)), want):
                detail = f"speed {X.fmt(v.get('speed'))} m/s: the sheet's {prop}"
            else:
                before = v.get("speed")
                wr.vehicle_field(vid, "speed", want)
                outcome, detail = "applied", f"speed {X.fmt(before)} -> {X.fmt(want)} m/s"
        elif item.startswith("Tầm bắn"):
            vis = vision_of.get(vid)
            m = re.findall(r"tầm\s*(?:\d+\s*→\s*)?(\d+)", prop) or re.findall(r"(\d+)\s*m", prop)
            want = float(m[-1]) if m else None
            ranges = {w: g.weapon(w).get("range") for w in g.mounts(vid)}
            if vis is not None and str(vis[5] or "") == prop:
                outcome = "skipped"
                detail = (f"the row repeats the vision row's proposal ({prop}); the weapon sheet keeps the guns' ranges "
                          f"({', '.join(f'{w} {X.fmt(x)} m' for w, x in ranges.items())}, 'Giữ'), and the sheet's range order "
                          "(machine gun < autocannon < tank gun < anti-tank missile, Tỷ lệ map) would break: a contradiction in "
                          "the sheet, left for the owner")
            elif want is not None and any(X.close(float(x or 0), want) for x in ranges.values()):
                w = next(w for w, x in ranges.items() if X.close(float(x or 0), want))
                detail = f"{w} reaches {X.fmt(want)} m (A2's weapon row)"
            else:
                outcome, detail = "skipped", f"no mount reaches {want} m ({ranges})"
        elif item.startswith("Tham khảo"):
            if "T-14" in prop:
                real = refs.get(vid, {}).get("real", [])
                ok = not any("T-14" in x for x in real)
                outcome, detail = ("already" if ok else "skipped"), f"references {real}" + ("" if ok else ": T-14 still there")
            else:
                outcome, detail = "deferred", "the model and its reference: task B2 (the model agent)"
        else:
            outcome, detail = "skipped", f"no rule for the item '{item}'"
        report.add(STEP, CHECK, vid, item, outcome, f"{detail} (was {cur}; the row: {prop})")
