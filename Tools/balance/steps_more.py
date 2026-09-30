"""Prompt 25 importer, steps A2 onwards (see import_xlsx.py)."""
from __future__ import annotations

import import_xlsx as X

INTRO = {
    "A2": "Every row of \"Vũ khí đề xuất\" (the proposal columns: damage, fire mode, rate, rounds a burst or magazine, "
          "rest, reach, speed, blast, penetration), then the loadouts of \"Đơn vị – vũ khí\" (mounts kept 0 dropped, "
          "the new weapons). A cadence the game already fires within 3 % of the sheet's sustained DPS, in the same "
          "mode and rounds, stays as it is. Rows of \"Đơn vị – vũ khí\" that keep a mount without a note are counted, "
          "not listed.",
}


def run(step, wr, wb, report, weapon_rows, unit_rows, refs=None):
    if step == "A2":
        a2(wr, report, weapon_rows, unit_rows)
        return "A2: sheets Vũ khí đề xuất and Đơn vị – vũ khí"
    if step == "A3":
        import steps_a3
        INTRO["A3"] = steps_a3.INTRO
        steps_a3.run(wr, wb, report, weapon_rows)
        # A member that inherits a member of another family sees that family only once it exists: run again until
        # nothing moves (the first pass's report stands).
        for _ in range(3):
            before = wr.doc.text
            steps_a3.run(wr, wb, X.Report(), weapon_rows)
            if wr.doc.text == before:
                break
        return "A3: weapon families (sheets Tốc độ tên lửa, Vũ khí đề xuất)"
    if step == "A4":
        a4(wr, wb, report, weapon_rows)
        return "A4: sheet Tốc độ tên lửa"
    return None


INTRO["A4"] = ("The sheet's proposed speed for every missile, rocket and drone it lists. A family member's speed is its "
               "family's (A3); where the sheet's row for one member differs from its family, the report says so. The "
               "sheet's ranges are checked against the weapon sheet's (A2 applied those).")


def a4(wr, wb, report, weapon_rows):
    g = wr.game
    step = "A4"
    sh = "Tốc độ tên lửa"
    _, rows = X.sheet(wb, sh)
    for r in rows:
        wid, rng, speed, ratio = r[0], r[4], r[8], r[10]
        if not wid:
            continue
        if wid not in g.raw_weapons:
            report.add(step, sh, wid, "speed", "skipped", "no such weapon id in balance.json")
            continue
        w = g.weapon(wid)
        fam = g.weapon(wid, family=False).get("weaponFamily")
        notes = []
        if ratio is not None and ratio < 1.2:
            notes.append(f"{ratio:.2f} x its fastest target ({r[7]} m/s), below the sheet's 1.2-1.5")
        if rng is not None and not X.close(float(rng), w.get("range")):
            notes.append(f"the sheet's range {X.fmt(float(rng))} differs from the weapon sheet's {X.fmt(w.get('range'))} (A2 kept)")
        if X.close(w.get("projectileSpeed"), float(speed)):
            report.add(step, sh, wid, "speed", "already", f"{X.fmt(float(speed))} m/s" + ("; " + "; ".join(notes) if notes else ""))
        elif fam:
            report.add(step, sh, wid, "speed", "skipped",
                       f"the sheet's {X.fmt(float(speed))} m/s; its family {fam} flies {X.fmt(w.get('projectileSpeed'))} (A3)" + ("; " + "; ".join(notes) if notes else ""))
        else:
            wr.weapon_field(wid, "projectileSpeed", float(speed))
            report.add(step, sh, wid, "speed", "applied", f"{X.fmt(float(speed))} m/s" + ("; " + "; ".join(notes) if notes else ""))


def a2(wr, report, weapon_rows, unit_rows):
    g = wr.game
    step = "A2"
    for wid, row in weapon_rows.items():
        X.apply_weapon_row(wr, row, report, step)
    # Loadouts: every unit with a mount dropped, added or changed by a note.
    sh = "Đơn vị – vũ khí"
    units = []
    for r in unit_rows:
        if r[0] not in units:
            units.append(r[0])
    a1_notes = ("Thêm 1 AIM-120", "Hydra:", "FAB-250:", "Bỏ bom SDB", "Đổi Hellfire")
    for vid in units:
        rows = [r for r in unit_rows if r[0] == vid]
        if vid not in g.vehicles_raw:
            report.add(step, sh, vid, "unit", "skipped", "no such vehicle id in balance.json")
            continue
        busy = [r for r in rows if r[5] == 0 or r[12]]
        if not busy:
            for r in rows:
                report.add(step, sh, vid, r[3], "already", "kept", listed=False)
            continue
        notes = {str(r[12] or "") for r in rows}
        if any(n.startswith(a1_notes) for n in notes) and not any(r[5] == 0 and r[3] not in ("guided_bomb",) for r in rows) \
                and not any(str(r[12] or "").startswith("Vũ khí thêm") and r[3] != "jassm" for r in rows):
            report.add(step, sh, vid, "loadout", "already", "its A1 row applied it (" + "; ".join(n.split(" — ")[0] for n in notes if n) + ")")
            continue
        if any(n.startswith("Giữ Stinger phụ") for n in notes):
            report.add(step, sh, vid, "sam", "already", "the Stinger stays (" + next(n for n in notes if n) + ")")
            continue
        X.loadout(wr, vid, unit_rows, report, step)
    # The DPS check the test makes, here too: every row the game fires within 5 % of the sheet's sustained DPS.
    for wid, row in weapon_rows.items():
        want = X.sheet_dps(row)
        if wid not in g.raw_weapons:
            continue
        got = X.cadence(g.weapon(wid))[3]
        if not want:
            report.add(step, "Vũ khí đề xuất", wid, "DPS check", "skipped", f"the sheet's DPS is {want!r}: a cadence cell is empty")
        elif abs(got / want - 1) > 0.05:
            report.add(step, "Vũ khí đề xuất", wid, "DPS check", "skipped", f"game {got:.1f} vs sheet {want:.1f}")
    write_expectations(weapon_rows)
    for wid in g.raw_weapons:
        if wid not in weapon_rows and wid != "none":
            report.add(step, "Vũ khí đề xuất", wid, "weapon", "skipped", "not in the sheet: left as it is (families and the blast rule still apply)", listed=True)


EXPECT = X.os.path.join(X.ROOT, "Docs", "balance", "sheet_dps.tsv")

# Weapons whose sustained DPS was set apart from the sheet's after a measurement (DECISIONS 25A): id -> (DPS, reason).
DPS_OVERRIDES = {}


def write_expectations(weapon_rows):
    """The sheet's sustained DPS column, for BalanceSheetTests (the test cannot read the workbook)."""
    lines = ["# Generated by Tools/balance/import_xlsx.py from Machine_Brigade_Can_bang.xlsx, sheet Vũ khí đề xuất:",
             "# the column 'DPS duy trì đề xuất' (damage x rounds / (rounds / rate + rest)). BalanceSheetTests holds every",
             "# weapon's WeaponDef.SustainedDps within 5 % of it. An empty DPS carries the reason it is not checked.",
             TAB.join(["id", "dps", "note"])]
    for wid, row in weapon_rows.items():
        want = X.sheet_dps(row)
        note = ""
        if wid in DPS_OVERRIDES:
            want, note = DPS_OVERRIDES[wid]
        if not want:
            lines.append(TAB.join([wid, "", "the sheet's DPS is empty (its rounds a magazine cell is blank): the game's cadence stands"]))
        else:
            lines.append(TAB.join([wid, f"{want:.3f}", note]))
    with open(EXPECT, "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(lines) + NL)


TAB = chr(9)
NL = chr(10)
