"""Prompt 30 L2: the speakers' roles and allowed triggers (sheet "Giọng nhân vật") as data.

    python Tools/story/import_speakers.py

Writes Assets/MachineBrigade/Resources/Data/script/speakers.json: for each speaker id (the game's ids, Docs/STORY.md)
its speakerRole words and its allowedTriggers keys (the sheet's notes in brackets dropped; "như trên" = the enemy
generals' set), plus the triggers any mission's main speaker may take and those anyone may take when the script says
so (the sheet "Điểm kích hoạt", column "Ai nói": "Người nói chính", "Theo kịch bản", "Theo sự kiện").
"""
from __future__ import annotations

import json
import os
import re

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX = os.path.join(ROOT, "Docs", "story", "Machine_Brigade_Cot_truyen_Che_do_v2.xlsx")
OUT = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "script", "speakers.json")

# The sheet's names -> the game's speaker ids.
IDS = {"Kade": "khai", "Mara": "mai", "Reyes": "dieuhau", "Nadia": "linh", "Thorne": "hung", "Brandt": "brandt",
       "Brenn": "brenn", "Mendez": "mendez", "Dahl": "dahl", "Varro": "varro", "Quist": "quist", "Reyn": "reyn",
       "Okoye": "okoye", "Adler": "adler", "Venn": "sen", "Varga": "varga", "Orlov": "orlov", "Kessler": "kessler",
       "Wolff": "quaden", "Aurel": "aurel"}
GENERAL = ["mission_start", "boss_spawn", "victory", "defeat"]
KNOWN = {"mission_start", "phase_start", "phase_end", "objective_progress", "point_captured", "point_lost", "boss_spawn",
         "boss_phase_change", "boss_part_destroyed", "boss_hp", "superweapon_warning", "general_tactic_change",
         "expensive_unit_lost", "first_unit_type_seen", "hq_below_50", "critical_failure_imminent", "momentum_high_once",
         "ally_arrives", "ally_late", "enemy_reinforcement", "neutral_captured", "event_triggered",
         "objective_stall_90s", "timer_60s", "victory", "defeat", "time"}
# Command (the brigade's HQ voice) is not in the sheet: system-like reports only.
HQ = {"roles": ["command net"], "triggers": ["objective_progress", "event_triggered", "enemy_reinforcement", "timer_60s"]}
MAIN = ["mission_start", "victory", "defeat", "critical_failure_imminent", "momentum_high_once", "objective_stall_90s"]
SCRIPTED = ["phase_start", "phase_end", "objective_progress", "boss_phase_change", "event_triggered", "time"]


def triggers(cell: str) -> list[str]:
    text = re.sub(r"\([^)]*\)", "", cell)
    out = []
    if text.strip().startswith("như trên") or "general lines" in text:
        out += GENERAL
    for k in re.findall(r"[a-z_0-9]+", text):
        if k in KNOWN and k not in out:
            out.append(k)
        if k == "defeat/victory":
            pass
    if "defeat/victory" in text or "victory/defeat" in text:
        out += [k for k in ("victory", "defeat") if k not in out]
    if "boss_hp" in text:
        out.append("boss_hp")
    return out


def main():
    ws = openpyxl.load_workbook(XLSX, data_only=True)["Giọng nhân vật"]
    speakers = {}
    for r in ws.iter_rows(min_row=3, values_only=True):
        if not r[0] or str(r[0]) == "Nhân vật":
            continue
        name = str(r[0])
        sid = next((v for k, v in IDS.items() if k in name), None)
        if sid is None:
            raise SystemExit(f"no id for {name}")
        roles = [x.strip() for x in str(r[8] or "").split(",") if x.strip()]
        speakers[sid] = {"name": name, "roles": roles, "triggers": triggers(str(r[9] or ""))}
    # Aurel: on the radio himself only from chapter 11 (one line a chapter before, through a device).
    speakers["aurel"]["triggers"] = GENERAL
    speakers["aurel"]["note"] = "direct from chapter 11; before, at most one line a chapter through a device"
    speakers["hung"]["note"] = "ally_late only before chapter 7"
    speakers["hq"] = {"name": "Command", **HQ}
    data = {"speakers": speakers, "mainTriggers": MAIN, "scriptedTriggers": SCRIPTED}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for k, v in speakers.items():
        print(k, v["triggers"])


if __name__ == "__main__":
    main()
