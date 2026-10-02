"""Prompt 28 appendix B: the AI profile of every mode and mission type (aiModeProfile), as data.

    python Tools/ai/import_ai_modes.py [--dry]

Reads the sheet "AI theo chế độ" of Docs/story/Machine_Brigade_Cot_truyen_Che_do_v2.xlsx and writes balance.json
"aiModeProfiles" between its markers: one profile per row (controllers, allowed tactics, stall / spend / advance /
support policies, objective policy and the player's auto AI as text, leash, target mask, phase overrides, special
flags) and the assignment of every mode tag and every campaign.json mission goal to a profile. What the sheet gives
as prose (escort anchor, recon engagement, defender side, leash region) is filled in here from its notes; the
profile ids and assignments are this script's. Checks that every goal used in campaign.json has a profile.
"""
from __future__ import annotations

import argparse
import json
import os
import re

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX = os.path.join(ROOT, "Docs", "story", "Machine_Brigade_Cot_truyen_Che_do_v2.xlsx")
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
CAMPAIGN = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "campaign.json")
BEGIN = "  // <generated ai modes: Tools/ai/import_ai_modes.py, do not edit by hand>"
END = "  // </generated ai modes>"
ANCHOR = "  // </generated ai>"

# Sheet row (by its first words) -> profile id.
ROWS = [
    ("Giữ cứ điểm", "conquest"),
    ("Tử chiến", "deathmatch"),
    ("Vua đồi", "hill"),
    ("Công phá", "assault"),
    ("Công thành", "siege"),
    ("Phòng thủ", "defend"),
    ("Sinh tồn", "survival"),
    ("Săn trùm", "bossrush"),
    ("Chiến dịch: chiếm", "capture"),
    ("Chiến dịch: giữ", "hold"),
    ("Chiến dịch: hộ tống", "escort"),
    ("Chiến dịch: bảo vệ", "protect"),
    ("Chiến dịch: trinh sát", "recon"),
    ("Chiến dịch: săn mục tiêu", "hunt"),
    ("Chiến dịch: bắn hạ", "shootdown"),
    ("Chiến dịch: lập tiền đồn", "outpost"),
    ("Chiến dịch: giải vây", "relieve"),
    ("Chiến dịch lớn", "operation"),
    ("Màn bộ bài", "fixed_deck"),
]

# The world's mode tags (SimWorld.ModeTag) and the campaign's mission goals (MissionDef.MissionGoal).
MODES = {"Conquest": "conquest", "Sandbox": "conquest", "Deathmatch": "deathmatch", "KingOfTheHill": "hill",
         "Assault": "assault", "Siege": "siege", "Weekly": "siege", "Defend": "defend", "Endless": "defend",
         "Survival": "survival", "BossRush": "bossrush", "Operation": "operation", "FixedDeck": "fixed_deck"}
GOALS = {"Capture": "capture", "Destroy": "capture", "Duel": "capture", "Hold": "hold", "Survive": "hold",
         "Escort": "escort", "Evacuate": "escort", "Protect": "protect", "Recon": "recon", "Hunt": "hunt",
         "Intercept": "hunt", "ShootDown": "shootdown", "Outpost": "outpost", "Relieve": "relieve", "Boss": "bossrush"}

# "nhóm thủ": the defensive tactics (Docs/ai/TACTICS.md).
DEFENSIVE = ["depth", "base_defence", "attrition", "ambush", "balanced"]
TACTIC_NAMES = {"Phục kích": "ambush", "Bảo vệ căn cứ": "base_defence"}

# What the sheet says in prose, as fields (the appendix's mandatory rules).
EXTRA = {
    # Defending side: "ai" the AI's commander holds, "player" the player holds; the defender never gets stall pressure.
    "assault": {"defender": "ai", "leashRegion": "zone", "leashDistance": 40},
    "siege": {"defender": "ai", "leashRegion": "defenceLayer", "leashDistance": 30},
    "defend": {"defender": "player"},
    "survival": {"defender": "player"},
    "hold": {"defender": "player"},
    "protect": {"defender": "player", "autoAi": "protectTarget"},
    "escort": {"escort": {"anchor": "convoyCentre", "maxAdvanceDistance": 30, "rearGuardWeight": 0.3,
                          "threatToConvoyWeight": 2.0, "noChaseOutsideLeash": True, "safeZoneRadius": 12},
               "autoAi": "escort"},
    "recon": {"engagement": "AvoidUnlessBlocking", "noChase": True,
              "phaseOverrides": [{"when": "alert", "profile": "capture"}]},
    "relieve": {"autoAi": "breakSiege"},
    "outpost": {"phaseOverrides": [{"when": "step:clear", "stall": "Both"}, {"when": "step:capture", "stall": "Both"},
                                   {"when": "step:build", "stall": "ObjectiveStallOnly"},
                                   {"when": "step:hold", "stall": "AttackerOnly"}]},
    "deathmatch": {"flags": ["riskWeightByUnitValue"]},
    "bossrush": {"flags": ["noGeneralTactic"]},
    "fixed_deck": {"inherits": True},
    # "theo giai đoạn": the operation's phases override; between phases it plays like a capture mission.
    "operation": {"spend": True, "advance": True},
}


def flag(text: str) -> str:
    """ON/OFF/— and the sheet's qualified forms ("ON (thủ)") as a bool, or "phase" for "theo giai đoạn/bước"."""
    t = text.strip().lower()
    if t.startswith("on"):
        return "on"
    if t.startswith("theo controller"):
        # Siege: the garrison is a ConquestAi that buys with CP (SiegeModes Defender.Build), so it spends.
        return "on"
    if t.startswith("theo") or t.startswith("kế thừa"):
        return "inherit"
    return "off"


def stall(text: str) -> str:
    t = text.strip()
    for key, value in (("ATTACKER_ONLY", "AttackerOnly"), ("OBJECTIVE_STALL_ONLY", "ObjectiveStallOnly"),
                       ("BOTH", "Both"), ("OFF", "Off")):
        if t.startswith(key):
            return value
    if t.startswith("theo bước"):
        return "ObjectiveStallOnly"
    return "Inherit" if t.startswith("kế thừa") else "Both"


def controllers(text: str) -> list[str]:
    found = [c for c in ("COMMANDER", "WAVE_DIRECTOR", "FORTRESS", "BOSS", "STATIC") if c in text]
    if text.startswith("nhiều controller"):
        found = ["COMMANDER", "WAVE_DIRECTOR", "FORTRESS", "BOSS", "STATIC"]
    return [{"COMMANDER": "Commander", "WAVE_DIRECTOR": "WaveDirector", "FORTRESS": "Fortress", "BOSS": "Boss",
             "STATIC": "Static"}[c] for c in found]


def tactics(text: str) -> tuple[list[str], bool]:
    """The allowed tactic ids ("*" all) and whether the general's preference applies."""
    t = text.strip()
    if t.startswith("tất cả"):
        return ["*"], False
    if t.startswith("nhóm thủ"):
        return DEFENSIVE, False
    if t.startswith("theo tướng"):
        return ["*"], True
    if t.startswith("kế thừa"):
        return ["*"], False
    named = [TACTIC_NAMES[n.strip()] for n in re.split(r",", t) if n.strip() in TACTIC_NAMES]
    return named, False


def profiles(wb) -> dict:
    ws = wb["AI theo chế độ"]
    out = {}
    for r in ws.iter_rows(min_row=3, values_only=True):
        if not r[0] or str(r[0]).startswith("Chế độ /"):
            continue
        name = str(r[0]).strip()
        pid = next((p for prefix, p in ROWS if name.startswith(prefix)), None)
        if pid is None:
            raise SystemExit(f"unknown row: {name}")
        cells = ["" if c is None else str(c).strip() for c in r]
        allowed, general = tactics(cells[2])
        if cells[1].startswith("COMMANDER theo tướng") or cells[1].startswith("kế thừa"):
            general = general or cells[1].startswith("COMMANDER theo tướng")
        support = "Normal"
        if "DISABLED_UNTIL_ALERT" in cells[6] or "DISABLED_UNTIL_ALERT" in cells[7]:
            support = "DisabledUntilAlert"
        p = {
            "name": name,
            "controllers": controllers(cells[1]),
            "tactics": allowed,
            "generalTactic": general,
            "stall": stall(cells[3]),
            "spend": flag(cells[4]) == "on",
            "advance": flag(cells[5]) == "on",
            "support": support,
            "engagement": "Normal",
            "defender": "none",
            "targetMask": ["enemy"],
            "objectivePolicy": cells[6] if cells[6] != "—" else "",
            "autoAiNote": cells[7] if cells[7] != "—" else "",
        }
        if flag(cells[4]) == "inherit" or flag(cells[5]) == "inherit":
            p["phased"] = True
        p.update(EXTRA.get(pid, {}))
        out[pid] = p
    return out


def check_goals(assign: dict, data: dict):
    with open(CAMPAIGN, encoding="utf-8") as f:
        text = f.read()
    goals = set(re.findall(r'"goal"\s*:\s*"(\w+)"', text))
    missing = sorted(g for g in goals if g not in assign["goals"])
    if missing:
        raise SystemExit(f"campaign goals without a profile: {missing}")
    for k, v in list(assign["goals"].items()) + list(assign["modes"].items()):
        if v not in data:
            raise SystemExit(f"{k} -> {v}: no such profile")
    print(f"{len(goals)} campaign goals, all with a profile")


def block(data: dict, assign: dict) -> list[str]:
    out = [BEGIN,
           "  // Prompt 28 appendix B: the AI profile of each mode and mission type (sheet \"AI theo chế độ\"), and which",
           "  // profile each mode tag and campaign goal plays (Docs/DECISIONS.md \"28 appendix\").",
           '  "aiModeProfiles": {',
           '    "profiles": {']
    items = list(data.items())
    out += [f'      "{k}": {json.dumps(v, ensure_ascii=False)}{"" if i == len(items) - 1 else ","}' for i, (k, v) in enumerate(items)]
    out += ["    },",
            f'    "modes": {json.dumps(assign["modes"], ensure_ascii=False)},',
            f'    "goals": {json.dumps(assign["goals"], ensure_ascii=False)}',
            "  },",
            END]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    data = profiles(openpyxl.load_workbook(XLSX, data_only=True))
    assign = {"modes": MODES, "goals": GOALS}
    check_goals(assign, data)
    new = block(data, assign)
    if args.dry:
        print("\n".join(new))
        return
    with open(BALANCE, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if BEGIN in lines:
        a, b = lines.index(BEGIN), lines.index(END)
        lines[a:b + 1] = new
    else:
        a = lines.index(ANCHOR) + 1
        lines[a:a] = new
    with open(BALANCE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"{len(data)} profiles -> {os.path.relpath(BALANCE, ROOT)}")


if __name__ == "__main__":
    main()
