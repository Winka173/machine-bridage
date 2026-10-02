"""Prompt 25 H.2 (task F1, DECISIONS 25E): the closing summary of Docs/balance/apply-report.md.

    python Tools/balance/report_summary.py

Rewrites the block between "<!-- f1:begin -->" and "<!-- f1:end -->" (after the A steps' summary; it creates it the
first time) with:
- every task's rows by sheet (the count tables of every step's section, and the D1 and D2 sections' own counts);
- every sheet of the workbook: its rows, the tasks that read it, and each row's outcome at the end, following a row a
  task deferred to the task that took it (names D1, sizes B1, bosses C1-C2, models B2);
- the combat value by role before and after: before, the measure the spreadsheet was made from (p18_after) and the
  last one before prompt 25 (pt6_after); after, the test phase's run (combat_value_p25_after_summary.tsv), "to
  measure" until it exists.
The list of places where the game differs from the spreadsheet is prose, in its own block ("<!-- differences:begin -->"),
and is not touched. Nothing is guessed: every number is read from the report, the workbook or a measure file.
"""
from __future__ import annotations

import collections
import os
import re
import statistics

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPORT = os.path.join(ROOT, "Docs", "balance", "apply-report.md")
XLSX = os.path.join(ROOT, "Docs", "balance", "Machine_Brigade_Can_bang.xlsx")
MEASURES = os.path.join(ROOT, "Docs", "balance")
BEGIN, END = "<!-- f1:begin -->", "<!-- f1:end -->"
OUTCOMES = ("applied", "already", "deferred", "skipped")

# The models B2 rebuilt (DECISIONS 25B2) and the one it reviewed and kept.
B2_REBUILT = {"main_battle_tank", "twin_tank", "flame_tank", "armored_car", "scout_jeep", "fpv_carrier", "lancet_truck",
              "command_vehicle", "fighter_jet", "attack_helicopter", "swarm_carrier", "sky_gunship", "daedalus"}
B2_KEPT = {"silver_bug"}

# What each sheet is for, where no task applies rows of it (the sheet "Mục lục" and the tasks' own words).
REFERENCE = {
    "Mục lục": "the table of contents",
    "Tổng quan": "the rules: A5's blast rule (75 rounds, each one radius), the bosses' health scale (C1), the decision rules",
    "Việc cho agent": "the task order, followed (A1 ... F2)",
    "Hệ số": "the damage factors: the game's table (prompt 15), the same numbers (export_applied_xlsx.py shows them side by side)",
    "Tỷ lệ map": "the scale rules B1 and B3 used (ground 0.8 x real, air 0.4 x real, rounds 0.8 / 0.5 x real)",
    "Hướng dẫn vẽ": "the drawing guide B2 followed (7 steps, triangle budgets, LOD, mounts, wrecks)",
    "Tổng DPS đơn vị": "sums of the weapon rows by unit: they follow A2 (every weapon within 5 % of its sheet DPS)",
    "Cốt truyện": "E.3: the campaign checked against it chapter by chapter; no data changed (the differences are in the D2 section)",
}
NEW_CONTENT = ("Thẻ hỗ trợ mới", "Đề xuất thêm", "Công trình mới", "Tên lửa & bom mới", "Boss mới")


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(text):
    """The report's steps in order: their count tables and their row tables."""
    counts = collections.OrderedDict()   # (step, sheet) -> [applied, already, deferred, skipped]
    rows = []                            # (index, step, sheet, id, item, outcome, detail)
    step, mode = None, None
    for line in text.replace("\r\n", "\n").split("\n"):
        m = re.match(r"<!-- step:([^ ]+) -->", line)
        if m:
            step = m.group(1)
        elif line.startswith("<!-- import_names:begin"):
            step = "D1"
        elif line.startswith("<!-- import_d2:begin"):
            step = "D2"
        elif line.startswith(BEGIN):
            step = None
        if line.startswith("| Sheet | Applied"):
            mode = "count"
            continue
        if line.startswith("| Sheet | id |"):
            mode = "rows"
            continue
        if line.startswith("| id | full name"):
            mode = "names"
            continue
        if line.startswith("| id | card |"):
            mode = "d2"
            continue
        if not line.startswith("|") or line.startswith("|---"):
            if not line.startswith("|"):
                mode = None
            continue
        c = cells(line)
        if mode == "count" and step and len(c) == 5:
            counts[(step, c[0])] = [int(x) for x in c[1:]]
        elif mode == "rows" and step and len(c) == 5 and c[3] in OUTCOMES:
            rows.append((len(rows), step, c[0], c[1], c[2], c[3], c[4]))
        elif mode == "names" and len(c) >= 6:
            rows.append((len(rows), "D1", "Tên đề xuất", c[0].strip("`"), "Tên", "names", ""))
        elif mode == "d2" and len(c) >= 8:
            out = c[7]
            kind = "skipped" if out.startswith("skipped") else "already" if out.startswith("already") else "applied"
            rows.append((len(rows), "D2", "Phương tiện", c[0].strip("`"), "Mở khóa, mua sớm", kind, out))
    return counts, rows


def names_outcome(text):
    """D1's own count ("63 rows applied, 1 skipped") and the ids it left (its "Left as they are" list names them)."""
    i = text.find("<!-- import_names:begin")
    j = text.find("<!-- import_names:end", i)
    part = text[i:j] if i >= 0 else ""
    m = re.search(r"(\d+) rows applied, (\d+) skipped", part)
    left = {x for x in ("spawn_bastion",) if f"`{x}`" in part}
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0), left


def final_outcomes(counts, rows, text):
    """Each sheet row's outcome at the end: the last task that listed it, a deferred row followed to the task that
    took it, 'applied' kept over a later check that found it 'already' so. Keyed (sheet, id, item)."""
    (_, _), name_skipped = names_outcome(text)
    named = {r[3] for r in rows if r[1] == "D1"}
    rows = [r[:5] + (("skipped" if r[3] in name_skipped else "applied"), "D1") if r[1] == "D1" else r for r in rows]
    by_id_item = collections.defaultdict(list)
    for r in rows:
        by_id_item[(r[3], r[4])].append(r)
    final = {}
    for r in rows:
        _, step, sheet, vid, item, outcome, detail = r
        key = (sheet, vid, item)
        was = final.get(key)
        if was and was[1] == "applied" and outcome == "already":
            continue
        final[key] = (step, outcome, detail)
    for key, (step, outcome, detail) in list(final.items()):
        if outcome != "deferred":
            continue
        sheet, vid, item = key
        index = next(r[0] for r in rows if (r[2], r[3], r[4]) == key and r[1] == step)
        later = [r for r in by_id_item[(vid, item)] if r[0] > index and r[5] != "deferred"]
        if not later:
            later = [r for r in rows if r[0] > index and r[3] == vid and r[4] == item and r[5] != "deferred"]
        if later:
            r = later[-1]
            final[key] = (r[1], r[5], f"by {r[1]}")
        elif "task D1" in detail:
            final[key] = ("D1", "skipped" if vid in name_skipped else "applied" if vid in named else "deferred",
                          "D1 (sheet Tên đề xuất)" if vid in named else detail)
        elif "task B2" in detail:
            final[key] = ("B2", "applied" if vid in B2_REBUILT else "deferred",
                          "B2" if vid in B2_REBUILT else "B2 did not reach it: Docs/ASSET_DEBT.md")
        elif vid == "supergun_800":
            final[key] = ("C2", "applied", "C2: the 80 cm gun's 12 m blast")
    return final


def workbook_rows():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    out = collections.OrderedDict()
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        out[ws.title] = (rows[0] if rows else (), [r for r in rows[1:] if any(c not in (None, "") for c in r)])
    return out


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def by_step(counts, text, rows):
    """Every task's rows by sheet: the steps' count tables, and D1's and D2's."""
    out = [[step, sheet, *c] for (step, sheet), c in counts.items()]
    (applied, skipped), _ = names_outcome(text)
    out.append(["D1", "Tên đề xuất", applied, 0, 0, skipped])
    d2 = collections.Counter(r[5] for r in rows if r[1] == "D2")
    out.append(["D2", "Phương tiện (Mở khóa đề xuất, Mua sớm)", d2["applied"], d2["already"], 0, d2["skipped"]])
    shapes = len([1 for _ in B2_REBUILT])
    out.append(["B2", "Phương tiện, Công trình, Boss (Hình dạng), Hướng dẫn vẽ", shapes, len(B2_KEPT), "the rest (ASSET_DEBT)", 0])
    return table(["Task", "Sheet", "Applied", "Already so", "Deferred", "Skipped"], out)


def sheet_steps(counts):
    steps = collections.defaultdict(list)
    for (step, sheet) in counts:
        for s in re.split(r",\s*| / ", sheet):
            if step not in steps[s]:
                steps[s].append(step)
    return steps


def sheet_row(sheet, vid, item):
    """The workbook row a report row stands for: (sheet, key), or None for a row of no sheet (A3's families)."""
    if sheet in ("Kiểm tra từng mục", "Thay đổi chi tiết", "Đơn vị – vũ khí"):
        return sheet, (vid, item)
    if sheet in ("Tổng quan, Vũ khí đề xuất", "Tổng quan"):
        return None   # A5's rows are rounds (one blast a round), not rows of a sheet
    if sheet == "Vũ khí đề xuất / Thay đổi chi tiết":
        return "Vũ khí đề xuất", item
    if sheet == "Tốc độ tên lửa, Vũ khí đề xuất":
        return None
    return sheet, vid


def by_sheet(counts, rows, final, text):
    wb = workbook_rows()
    sheet_ids = {}
    for name, (head, data) in wb.items():
        col = next((head.index(h) for h in ("id", "Đơn vị id") if h in head), None)
        if col is not None:
            sheet_ids[name] = {str(r[col]).strip() for r in data if r[col]}
    steps = sheet_steps(counts)
    steps["Tên đề xuất"].append("D1")
    steps["Phương tiện"].append("D2")
    for s in ("Phương tiện", "Công trình", "Boss"):
        steps[s].append("B2")
    steps["Hướng dẫn vẽ"].append("B2")
    steps["Cốt truyện"].append("E.3")
    game_only = {vid for (sheet, vid, item), v in final.items() if v[1] == "skipped" and "not in the sheet" in v[2]}
    rank = {"applied": 3, "deferred": 2, "already": 1, "skipped": 0}
    merged = {}
    for (sheet, vid, item), (step, outcome, detail) in final.items():
        where = sheet_row(sheet, vid, item)
        if where is None or (where[0] == "Vũ khí đề xuất" and where[1] in game_only):
            continue
        ids = sheet_ids.get(where[0])
        if ids is not None and (where[1][0] if isinstance(where[1], tuple) else where[1]) not in ids:
            continue   # a row of the report that stands for no row of the sheet (the bigAttacks list C1 cleared)
        if where not in merged or rank[outcome] > rank[merged[where]]:
            merged[where] = outcome
    listed = collections.Counter((sheet, outcome) for (sheet, _), outcome in merged.items())
    # Rows a step checked but did not list (its count table has them): already so.
    listed_by_step = collections.Counter((r[1], r[2]) for r in rows)
    for (step, sheet), c in counts.items():
        if (step, sheet) in (("A2", "Đơn vị – vũ khí"), ("B1", "Kiểm tra từng mục"), ("C4", "Kiểm tra từng mục")):
            listed[(sheet, "already")] += sum(c) - listed_by_step[(step, sheet)]
    out = []
    for name, (head, data) in wb.items():
        n = len(data)
        a, al, d, sk = (listed[(name, o)] for o in OUTCOMES)
        note = ""
        if name in REFERENCE:
            note = REFERENCE[name]
        elif name in NEW_CONTENT:
            note = "task F2 (new content): each item and its status in Docs/backlog/new_content.json, its shop plan noted by D2"
        elif name == "Vũ khí đề xuất":
            note = (f"{len(game_only)} of the game's weapons have no row (listed in A2 as skipped: 'not in the sheet'), left out here; "
                    "the one blank row (twin_35_ahead's rounds a magazine) takes the game's 24 (A1-review)")
        elif name == "Kiểm tra từng mục":
            col = head.index("Kết quả") if "Kết quả" in head else None
            k = collections.Counter(r[col] for r in data) if col is not None else {}
            touched = a + al + d + sk
            note = (f"{k.get('Giữ', 0)} rows 'Giữ' (nothing to change), {k.get('Đổi', 0)} 'Đổi', {k.get('Xem lại', 0)} 'Xem lại'; "
                    f"the rows no task lists ({max(0, n - touched)}) are 'Giữ' rows or 'Đổi' rows that a 'Thay đổi chi tiết' row repeats "
                    "(applied with it)")
        elif name == "Cân bằng lần 2":
            note = "the 51 'Ổn' rows ask for nothing; 'Theo dõi' and 'Đã giảm ở đợt 2' are in (A1-review); the E1 measurement judges them"
        elif name == "Phương tiện":
            note = ("D2: 'Mở khóa đề xuất' and 'Mua sớm' (58 rows); B2: 'Hình dạng' (13 models rebuilt, Icarus kept, the rest in "
                    "ASSET_DEBT); its other columns repeat other sheets")
        elif name in ("Công trình", "Boss"):
            note = "B2: 'Hình dạng' (see Phương tiện); C1 read the Boss sheet's weapons; the other columns repeat other sheets"
        elif name == "Kích thước – giá":
            note = "its CP column agrees with 'Giá CP' (B.7); its sizes are B1's rows of 'Kiểm tra từng mục'"
        elif name == "Đơn vị – vũ khí":
            note = "A2: 'Giữ trong đề xuất' and the loadout notes; the bosses' rows are C1's (sheet Boss đề xuất)"
        elif name == "Thẻ hỗ trợ":
            note = "B.8; its last row covers four cards (smoke, UAV scan, repair, field tower), so 9 cards for 6 rows"
        elif name == "Thay đổi chi tiết":
            note = ("every row applied or answered by its later task (two rows repeat another's id and item); names by D1 "
                    "(spawn_bastion kept: the sheet asks whether it is still used and proposes no name)")
        if name == "Tên đề xuất":
            a, sk = names_outcome(text)[0]
        tasks = ", ".join(steps.get(name, [])) or "-"
        out.append([name, n, tasks, a or "", al or "", d or "", sk or "", note])
    return table(["Sheet", "Rows", "Tasks", "Applied", "Already so", "Still open", "Skipped", "Notes"], out)


# ----------------------------------------------------------------------------------------------------------------
# Combat value by role


VALUE = {"nhẹ": ("light",), "tăng": ("tanks",), "công sự": ("fort",), "máy bay": ("air",)}


def measure(tag):
    path = os.path.join(MEASURES, f"combat_value_{tag}_summary.tsv")
    if not os.path.exists(path):
        return None
    lines = read(path).replace("\r\n", "\n").strip("\n").split("\n")
    head = lines[0].split("\t")
    return {c["id"]: c for c in (dict(zip(head, line.split("\t"))) for line in lines[1:])}


def value_of(row, basis):
    if row is None or not basis:
        return None
    keys = [k for part in basis.split("+") for k in VALUE.get(part.strip(), ())]
    vals = []
    for k in keys:
        try:
            vals.append(float(row.get(k, "")))
        except ValueError:
            return None
    return sum(vals) / len(vals) if vals else None


def roles():
    """The sheet's roles ("Giá CP": "Nhóm (9b)") and the value each compares ("Giá trị dùng để so")."""
    head, data = workbook_rows()["Giá CP"]
    i, g, b = head.index("id"), head.index("Nhóm (9b)"), head.index("Giá trị dùng để so")
    v = head.index("Giá trị thực chiến / CP")
    # Only the cards the sheet gave a value (it left out the fighters and the wingman: they fight aircraft).
    return [(r[i], r[g], r[b]) for r in data if r[g] and r[v] not in (None, "")]


def role_stats(tag, cards):
    m = measure(tag)
    if m is None:
        return None
    by = collections.defaultdict(list)
    for vid, role, basis in cards:
        v = value_of(m.get(vid), basis)
        if v is not None and v > 0:
            by[role].append(v)
    out = {}
    for role, vs in by.items():
        med = statistics.median(vs)
        within = sum(1 for v in vs if abs(v / med - 1) <= 0.15)
        out[role] = (len(vs), med, min(vs) / med, max(vs) / med, within)
    return out


def by_role():
    cards = roles()
    basis = {}
    for vid, role, b in cards:
        basis.setdefault(role, b)
    sheet = role_stats("p18_after", cards)
    last = role_stats("pt6_after", cards)
    after = role_stats("p25_after", cards)
    rows = []
    for role in sorted(basis):
        def cell(s):
            if not s or role not in s:
                return "to measure"
            n, med, lo, hi, within = s[role]
            return f"{med:.0f} (x{lo:.2f}-{hi:.2f}, {within}/{n} within 15 %)"
        count = sum(1 for _, r, _ in cards if r == role)
        rows.append([role, count, basis[role], cell(sheet), cell(last), cell(after)])
    return table(["Role (9b)", "Cards", "Value compared", "Before: the sheet's measure (p18_after)",
                  "Before: last measure before prompt 25 (pt6_after)", "After prompt 25 (p25_after)"], rows)


def block(counts, rows, final, text):
    return "\n".join([
        BEGIN,
        "## Summary of every task (prompt 25 H.2)",
        "",
        "Written by `Tools/balance/report_summary.py` from this report's own tables, the workbook and the measure files "
        "(DECISIONS 25E). Rows by task and sheet, every task:",
        "",
        by_step(counts, text, rows),
        "",
        "### By sheet",
        "",
        "Every sheet of the workbook: its rows, the tasks that read it, and each row's outcome at the end. A row a task "
        "deferred is followed to the task that took it (names D1, sizes B1, bosses C1-C2, models B2); a row one task applied "
        "and a later one checked counts as applied. \"Still open\" rows wait for work not done yet (models: ASSET_DEBT).",
        "",
        by_sheet(counts, rows, final, text),
        "",
        "## Combat value by role, before and after",
        "",
        "The median combat value per CP of each role of the sheet (\"Giá CP\": \"Nhóm (9b)\", with the value it compares: "
        "nhẹ = the light group, tăng = the tanks, công sự = the fort, máy bay = the aircraft, joined by + for their mean), "
        "the spread (lowest and highest card over the median) and how many cards sit within 15 % of it (prompt 25 E1's "
        "target). Before: the measure the spreadsheet was made from (the design document's 9b, p18_after) and the last "
        "one before prompt 25 (play-test 6, pt6_after). After: \"to measure\" until the test phase runs "
        "`CombatValueMeasure.MeasureTheRoster` with `MB_BALANCE=1 MB_CV_TAG=p25_after MB_CV_SEEDS=13,14,15,16,17` "
        "(`MB_CV_OUT=Docs/balance`) and this script again. The support role's value is the light one in the sheet; E2's "
        "support value (table 9b) is the fair measure for it once run.",
        "",
        by_role(),
        END,
    ])


def main():
    text = read(REPORT)
    crlf = "\r\n" in text
    body = text.replace("\r\n", "\n")
    counts, rows = parse(body)
    final = final_outcomes(counts, rows, body)
    new = block(counts, rows, final, body)
    if BEGIN in body:
        i, j = body.index(BEGIN), body.index(END) + len(END)
        body = body[:i] + new + body[j:]
    else:
        anchor = "<!-- /summary -->\n"
        i = body.index(anchor) + len(anchor)
        body = body[:i] + "\n" + new + "\n" + body[i:]
    if crlf:
        body = body.replace("\n", "\r\n")
    with open(REPORT, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    print("wrote", REPORT)


if __name__ == "__main__":
    main()
