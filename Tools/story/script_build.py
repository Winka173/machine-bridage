"""Prompt 30 L2/L7: builds and checks the in-battle script.

    python Tools/story/script_build.py            # every chapter source there is
    python Tools/story/script_build.py --check    # validate only, write nothing

Sources: Tools/story/script/chNN.txt (one per chapter, in play order 1, 2, 3, 13, 4, 5, 6, 14, 7, 8, 9, 15, 10, 11, 12):

    # a comment
    @c1m01 main=khai                         a mission and its main speaker (L5)
    mission_start | khai | 1 | Vietnamese text || English text
    point_captured:town | adler | 3 | ...    trigger:arg (the arg of the trigger: a point id, "1/2", a unit id, ...)
    time@45 | linh | 2 | ...                 a line 45 s in
    point_lost | adler | 3r | ...            "r": may repeat (20 s apart); else once

Writes Assets/MachineBrigade/Resources/Data/script/chNN.json (keys script.<mission>.<nn>) and Docs/story/script_stats.md.
The validator (errors stop the build, warnings are listed in the stats):
  - budget (L1): lines per mission against its kind (short/side 4-8, normal 6-10, boss and big operation 10-16);
  - length (L3): Vietnamese soft 70-90 / hard 110 characters, English soft 55-75 / hard 90; and the render budget:
    at most RENDER_LINES lines of RENDER_CHARS characters (the smallest supported screen with the portrait, Large
    font; the real render width is checked in Unity, see LOCAL_TODO), by word wrap;
  - a line said word for word in two missions (L8; only the shared generic reactions may repeat);
  - a trigger outside the speaker's allowedTriggers (speakers.json), unless the main speaker takes a main trigger or the
    trigger is scripted (phase, objective, boss phase, event, time);
  - a missing language; a proper name in one language and not the other (L6: names are not translated);
  - the story's guard rails (L9): no "Icarus" before chapter 5's end or in chapter 8; Ellis named in chapters 3 and
    15 before chapter 10; Thorne's betrayal not before chapter 7.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "Tools", "story", "script")
OUT = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "script")
CAMPAIGN = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "campaign.json")
STATS = os.path.join(ROOT, "Docs", "story", "script_stats.md")

PLAY_ORDER = [1, 2, 3, 13, 4, 5, 6, 14, 7, 8, 9, 15, 10, 11, 12]
VI_SOFT, VI_HARD, EN_SOFT, EN_HARD = (70, 90), 110, (55, 75), 90
# The render budget by characters until the Unity check: two lines of the strip at the smallest supported screen.
RENDER_LINES, RENDER_CHARS = 2, 58
BUDGET = {"short": (4, 8), "normal": (6, 10), "boss": (10, 16)}
NAMES = ["Kade", "Mara", "Hawk", "Nadia", "Thorne", "Brandt", "Varga", "Orlov", "Kessler", "Venn", "Raven", "Wolff",
         "Aurel", "Brenn", "Adler", "Mendez", "Dahl", "Varro", "Quist", "Reyn", "Okoye", "Ellis", "Crown", "Vault",
         "Longshot", "Magpie", "Behemoth", "Morrigan", "Albatross", "Icarus", "Leviathan", "Jötunn", "Harpy",
         "Bastion", "Matriarch", "Hive", "Locust", "Typhon", "Caspian", "Scylla", "Tempest", "Juggernaut", "Kronos",
         "Tartarus", "Ixion", "Atlas", "Nemesis", "Spectre", "Argus", "Gungnir", "Daedalus", "Moloch", "Charybdis",
         "Inferno", "Fenrir", "Helion", "Skygate", "Skyhold", "Veyra", "Ashfield", "Dunebreak", "Ironport", "Hegemon",
         "Accord", "Hollow Dam", "Deepcut", "Foundry", "Mirewood", "Stormbeach", "Greenvale", "Whiteout", "Frostpeak",
         "Red Rock", "Rust Yard", "Beacon Bay", "Emberridge", "Salt Flats"]


def load_campaign():
    with open(CAMPAIGN, encoding="utf-8") as f:
        text = re.sub(r"^\s*//.*$", "", f.read(), flags=re.M)
    return json.loads(text)


def kind_of(m: dict) -> str:
    """short (side), boss (a boss mission, the chapter's operation), else normal."""
    if m.get("side"):
        return "short"
    if m.get("operation") or m.get("goal") == "Boss" or m.get("boss"):
        return "boss"
    return "normal"


def parse(path: str):
    missions, lines, errors = {}, [], []
    current = None
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("@"):
                head = s[1:].split()
                current = head[0]
                opts = dict(x.split("=", 1) for x in head[1:] if "=" in x)
                missions[current] = {"main": opts.get("main")}
                continue
            parts = [p.strip() for p in s.split("|", 3)]
            if current is None or len(parts) != 4 or "||" not in parts[3]:
                errors.append(f"{os.path.basename(path)}:{n}: bad line")
                continue
            trig, speaker, prio, texts = parts
            vi, en = (t.strip() for t in texts.split("||", 1))
            at = None
            if "@" in trig:
                trig, at = trig.split("@", 1)
            arg = None
            if ":" in trig:
                trig, arg = trig.split(":", 1)
            repeat = prio.endswith("r")
            lines.append({"mission": current, "trigger": trig, "arg": arg, "at": float(at) if at else None,
                          "speaker": speaker, "priority": int(prio.rstrip("r")), "once": not repeat, "vi": vi, "en": en,
                          "src": f"{os.path.basename(path)}:{n}"})
    return missions, lines, errors


def wrapped(text: str) -> int:
    return len(textwrap.wrap(text, RENDER_CHARS)) or 1


def validate(chapter_files, campaign, speakers):
    by_id = {m["id"]: m for m in campaign["missions"]}
    errors, warnings = [], []
    seen_text = {}
    allowed = speakers["speakers"]
    main_trig, scripted = set(speakers["mainTriggers"]), set(speakers["scriptedTriggers"])
    known_triggers = {"mission_start", "time", "phase_start", "phase_end", "objective_progress", "point_captured",
                      "point_lost", "boss_spawn", "boss_phase_change", "boss_part_destroyed", "boss_hp",
                      "superweapon_warning", "general_tactic_change", "expensive_unit_lost", "first_unit_type_seen",
                      "hq_below_50", "critical_failure_imminent", "momentum_high_once", "ally_arrives", "ally_late",
                      "enemy_reinforcement", "neutral_captured", "event_triggered", "objective_stall_90s", "timer_60s",
                      "victory", "defeat"}
    stats = []
    ellis = {}
    for chapter, (missions, lines) in chapter_files.items():
        for mid, meta in missions.items():
            if mid not in by_id:
                errors.append(f"{mid}: not in campaign.json")
                continue
            mine = [l for l in lines if l["mission"] == mid]
            kind = kind_of(by_id[mid])
            lo, hi = BUDGET[kind]
            if not lo <= len(mine) <= hi:
                errors.append(f"{mid}: {len(mine)} lines, budget {lo}-{hi} ({kind})")
            main = meta.get("main")
            if main and main not in allowed:
                errors.append(f"{mid}: unknown main speaker {main}")
            stats.append((chapter, mid, kind, len(mine), main, sum(1 for l in mine if len(l["vi"]) > VI_SOFT[1]),
                          sum(1 for l in mine if len(l["en"]) > EN_SOFT[1])))
        for l in lines:
            where = f'{l["src"]} {l["mission"]}'
            if l["trigger"] not in known_triggers:
                errors.append(f"{where}: unknown trigger {l['trigger']}")
            sp = allowed.get(l["speaker"])
            if sp is None:
                errors.append(f"{where}: unknown speaker {l['speaker']}")
            else:
                main = missions.get(l["mission"], {}).get("main")
                ok = (l["trigger"] in sp["triggers"] or l["trigger"] in scripted or
                      (l["speaker"] == main and l["trigger"] in main_trig))
                if not ok:
                    errors.append(f"{where}: {l['speaker']} may not speak on {l['trigger']}")
            if not l["vi"] or not l["en"]:
                errors.append(f"{where}: missing a language")
            if len(l["vi"]) > VI_HARD:
                errors.append(f"{where}: Vietnamese {len(l['vi'])} > {VI_HARD}")
            if len(l["en"]) > EN_HARD:
                errors.append(f"{where}: English {len(l['en'])} > {EN_HARD}")
            for lang in ("vi", "en"):
                if wrapped(l[lang]) > RENDER_LINES:
                    errors.append(f"{where}: {lang} wraps to {wrapped(l[lang])} lines at {RENDER_CHARS} characters")
            if len(l["vi"]) > VI_SOFT[1] or len(l["en"]) > EN_SOFT[1]:
                warnings.append(f"{where}: over the soft length ({len(l['vi'])} / {len(l['en'])})")
            for name in NAMES:
                in_en = re.search(rf"\b{re.escape(name)}\b", l["en"]) is not None
                in_vi = re.search(rf"\b{re.escape(name)}\b", l["vi"]) is not None
                if in_en != in_vi:
                    errors.append(f"{where}: proper name {name} in one language only")
            for lang in ("vi", "en"):
                key = l[lang].lower()
                if key in seen_text and seen_text[key] != l["mission"]:
                    errors.append(f"{where}: same {lang} line as {seen_text[key]}")
                seen_text.setdefault(key, l["mission"])
            text = l["vi"] + " " + l["en"]
            if "Icarus" in text and (chapter in (1, 2, 3, 13, 4, 8) or (chapter == 5 and l["trigger"] != "victory")):
                errors.append(f"{where}: Icarus named before its reveal (end of chapter 5) or in chapter 8")
            if re.search(r"\b(Raven|Wolff)\b", text) and chapter in (1, 2, 3, 13, 4, 5, 6, 14, 7, 8, 9):
                errors.append(f"{where}: Raven named before chapter 15 (chapter 3 shows only the black insignia)")
            if "Ellis" in text:
                ellis.setdefault(chapter, 0)
                ellis[chapter] += 1
            if re.search(r"phản bội|betray", text, re.I) and chapter in (1, 2, 3, 13, 4, 5, 6, 14):
                errors.append(f"{where}: the betrayal named before chapter 7")
    done = set(chapter_files)
    if 10 in done:
        for c in (3, 15):
            if c in done and not ellis.get(c):
                errors.append(f"chapter {c}: Ellis must be named before the payoff in chapter 10")
        if not ellis.get(10):
            errors.append("chapter 10: Ellis's payoff missing")
    return errors, warnings, stats


def write_stats(stats, warnings):
    by_chapter = {}
    for s in stats:
        by_chapter.setdefault(s[0], []).append(s)
    out = ["# Script statistics (prompt 30 L7)", "",
           "Generated by `Tools/story/script_build.py`. Lines per mission against the budget of its kind (L1: short 4-8, "
           "normal 6-10, boss/operation 10-16); \"long\" counts lines over the soft length (Vietnamese 90, English 75).", ""]
    total = 0
    for chapter in PLAY_ORDER:
        if chapter not in by_chapter:
            continue
        rows = by_chapter[chapter]
        n = sum(r[3] for r in rows)
        total += n
        out += [f"## Chapter {chapter}: {n} lines, {len(rows)} missions", "",
                "| Mission | Kind | Lines | Main speaker | Long VI | Long EN |", "|---|---|---|---|---|---|"]
        out += [f"| {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |" for r in rows]
        out.append("")
    out.insert(4, f"Total: {total} lines in {len(stats)} missions.\n")
    if warnings:
        out += ["## Warnings", ""] + [f"- {w}" for w in warnings] + [""]
    with open(STATS, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with open(os.path.join(OUT, "speakers.json"), encoding="utf-8") as f:
        speakers = json.load(f)
    campaign = load_campaign()
    chapters, parse_errors = {}, []
    for path in sorted(glob.glob(os.path.join(SRC, "ch*.txt"))):
        chapter = int(re.search(r"ch(\d+)", path).group(1))
        missions, lines, errs = parse(path)
        parse_errors += errs
        chapters[chapter] = (missions, lines)
    errors, warnings, stats = validate(chapters, campaign, speakers)
    errors = parse_errors + errors
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings, {sum(len(l) for _, l in chapters.values())} lines")
    if args.check:
        sys.exit(1 if errors else 0)
    for chapter, (missions, lines) in chapters.items():
        counters = {}
        out_lines = []
        for l in lines:
            counters[l["mission"]] = counters.get(l["mission"], 0) + 1
            row = {"mission": l["mission"], "trigger": l["trigger"], "speaker": l["speaker"], "priority": l["priority"],
                   "once": l["once"], "key": f'script.{l["mission"]}.{counters[l["mission"]]:02d}', "en": l["en"], "vi": l["vi"]}
            if l["arg"] is not None:
                row["arg"] = l["arg"]
            if l["at"] is not None:
                row["at"] = l["at"]
            out_lines.append(row)
        data = {"chapter": chapter, "missions": missions, "lines": out_lines}
        with open(os.path.join(OUT, f"ch{chapter:02d}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=0)
            f.write("\n")
    write_stats(stats, warnings)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
