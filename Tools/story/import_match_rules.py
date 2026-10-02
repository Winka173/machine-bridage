"""Prompt 30 L4: the match rules of every mode (sheet "Luật trận") and the campaign's star rules, as data.

    python Tools/story/import_match_rules.py [--dry]

Writes balance.json "matchRules" between its markers (after the AI mode profiles): per mode the seven fields of the
schema (winCondition, loseCondition, timeLimit, overtimeRule, drawRule, scoreRule, catchUpPolicy) as the sheet words
them, and the numbers the code reads (`numbers`); the campaign stars (★1 the win, ★2 the mission type's mastery by goal,
★3 the mission's own challenge, else a default by goal); the leaderboards' sort orders (several keys, no formula).
The numbers are the sheet's; where the sheet says "as now" the current value is written and named here.
"""
from __future__ import annotations

import argparse
import json
import os

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX = os.path.join(ROOT, "Docs", "story", "Machine_Brigade_Cot_truyen_Che_do_v2.xlsx")
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
BEGIN = "  // <generated match rules: Tools/story/import_match_rules.py, do not edit by hand>"
END = "  // </generated match rules>"
ANCHOR = "  // </generated ai modes>"

ROWS = {"Giữ cứ điểm": "conquest", "Tử chiến": "deathmatch", "Vua đồi": "hill", "Công phá": "assault",
        "Công thành": "siege", "Phòng thủ": "defend", "Sinh tồn": "survival", "Vô tận": "endless", "Săn trùm": "bossrush",
        "Pháo đài tuần": "weekly", "Tác chiến": "operations"}
FIELDS = ["winCondition", "loseCondition", "timeLimit", "overtimeRule", "drawRule", "scoreRule", "catchUpPolicy"]

# The numbers each mode's code reads (seconds, points). catchUpMax: the catch-up's ceiling (EconomySystem, +50 % now).
NUMBERS = {
    "conquest": {"points": 500, "bleed": 0.8, "killTicketFactor": 0, "timeLimit": 600, "finalPhase": 120,
                 "finalScale": 2, "overtime": 60, "catchUpMax": 0.25},
    "deathmatch": {"target": 480, "killCap": 18, "timeLimit": 540, "overtime": 60, "catchUpMax": 0.25},
    "hill": {"target": 170, "perSecond": 1, "timeLimit": 540, "overtime": 60, "catchUpMax": 0.5},
    "assault": {"start": 240, "sectorBonus": 150, "maxBank": 300, "overtime": 60, "catchUpMax": 0.5},
    "siege": {"timeLimit": 1080, "overtime": 60},
    "defend": {"timeLimit": 720},
    "survival": {"waves": 10, "miniBossWave": 5, "bossWave": 10},
    "endless": {},
    "bossrush": {"bosses": 10, "timeLimit": 1800},
    "weekly": {"overtime": 60},
    "operations": {"losses": 2000, "lossesAtZeroCp": 150},
}

# ★2: the mission type's mastery (sheet: "hộ tống ≥ 4/5 xe, giữ ≥ X% thời gian"); never a loss condition, never fragile.
MASTERY = {
    "Escort": {"kind": "ConvoyShare", "value": 0.8}, "Evacuate": {"kind": "ConvoyShare", "value": 0.8},
    "Hold": {"kind": "HoldShare", "value": 0.8}, "Outpost": {"kind": "HoldShare", "value": 0.8},
    "Survive": {"kind": "HqShare", "value": 0.5}, "Protect": {"kind": "ProtectShare", "value": 0.75},
    "Capture": {"kind": "LossShare", "value": 0.4}, "Destroy": {"kind": "LossShare", "value": 0.4},
    "Hunt": {"kind": "LossShare", "value": 0.4}, "Intercept": {"kind": "LossShare", "value": 0.4},
    "ShootDown": {"kind": "LossShare", "value": 0.4}, "Relieve": {"kind": "AllyHqShare", "value": 0.5},
    "Boss": {"kind": "BossParts", "value": 2}, "Duel": {"kind": "HqShare", "value": 0.5},
    "Recon": {"kind": "ReconQuiet", "value": 0.67},
}
# ★3 when a mission has no challenge of its own: a side task by goal (the mission's own challenge always wins).
THIRD = {
    "Escort": {"kind": "Kills", "value": 10}, "Evacuate": {"kind": "Kills", "value": 10},
    "Hold": {"kind": "Kills", "value": 15}, "Outpost": {"kind": "Kills", "value": 12},
    "Survive": {"kind": "Kills", "value": 20}, "Protect": {"kind": "Kills", "value": 15},
    "Capture": {"kind": "Kills", "value": 10}, "Destroy": {"kind": "NoStrikes"}, "Hunt": {"kind": "Kills", "value": 10},
    "Intercept": {"kind": "NoStrikes"}, "ShootDown": {"kind": "Kills", "value": 12}, "Relieve": {"kind": "Kills", "value": 12},
    "Boss": {"kind": "NoAircraft"}, "Duel": {"kind": "Kills", "value": 15}, "Recon": {"kind": "NoStrikes"},
}
# Leaderboards: keys in order, each "-" descending, "+" ascending (sheet "Luật trận", "Vô hạn").
LEADERBOARDS = {
    "endless": ["-waves", "-killedBaseCp", "-seconds"],
    "defendEndless": ["-waves", "-killedBaseCp", "-seconds"],
    "survivalEndless": ["-waves", "-killedBaseCp", "-seconds"],
    "bossrush": ["-bosses", "+seconds", "-parts"],
    "bossrushEndless": ["-bosses", "+seconds", "-parts"],
    "weekly": ["-cleared", "+attempts", "+seconds"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    ws = openpyxl.load_workbook(XLSX, data_only=True)["Luật trận"]
    modes = {}
    for r in ws.iter_rows(min_row=3, values_only=True):
        if not r[0] or r[0] == "Chế độ":
            continue
        mid = ROWS.get(str(r[0]).strip())
        if mid is None:
            raise SystemExit(f"unknown row {r[0]}")
        modes[mid] = {"text": {f: str(r[i + 1] or "") for i, f in enumerate(FIELDS)}, "numbers": NUMBERS[mid]}
    missing = set(NUMBERS) - set(modes)
    if missing:
        raise SystemExit(f"rows missing: {missing}")
    out = [BEGIN,
           "  // Prompt 30 L4: each mode's match rules (sheet \"Luật trận\"), the campaign's stars and the leaderboards' orders.",
           '  "matchRules": {', '    "modes": {']
    items = list(modes.items())
    out += [f'      "{k}": {json.dumps(v, ensure_ascii=False)}{"" if i == len(items) - 1 else ","}' for i, (k, v) in enumerate(items)]
    out += ["    },",
            f'    "starMastery": {json.dumps(MASTERY)},',
            f'    "starThird": {json.dumps(THIRD)},',
            f'    "leaderboards": {json.dumps(LEADERBOARDS)}',
            "  },", END]
    if args.dry:
        print("\n".join(out))
        return
    with open(BALANCE, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if BEGIN in lines:
        a, b = lines.index(BEGIN), lines.index(END)
        lines[a:b + 1] = out
    else:
        a = lines.index(ANCHOR) + 1
        lines[a:a] = out
    with open(BALANCE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"{len(modes)} modes -> balance.json matchRules")


if __name__ == "__main__":
    main()
