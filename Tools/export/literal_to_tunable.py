"""literal_to_tunable (balance pack 2 pass 2, owner spec Docs/prompts/export_pack2_vi.txt §2.1; owner 09/10).

Moves gameplay literals of the C# (Assets/MachineBrigade/Scripts/Sim/**, Game/Match/**) into
Assets/MachineBrigade/Resources/Data/tunables.json with their values unchanged. The C# side is done by the Roslyn tool
Tools/export/mbconst (a real C# parser and semantic model, never a regex): each listed literal token is replaced by
`global::MachineBrigade.Sim.Content.SimTunables.<Domain>.<Owner>.<Name>`, the field is generated in
Sim/Content/SimTunables.Pass2.<Domain>.cs with the literal as its default (same C# type and f / m / d suffix; a negated
literal "-x" is replaced whole and the key holds -x), and tunables.json gets the key with value = the literal.

    python Tools/export/literal_to_tunable.py build
        write Tools/export/mbconst/MbConst.csproj (git-ignored; Roslyn of the installed .NET SDK) and build the tool
    python Tools/export/literal_to_tunable.py plan [--out Tools/export/pack2/pass2]
        scan_constants rows "de_xuat_dua_ra_du_lieu = co" joined with the Roslyn scan (reachability from the simulation's
        entry points, context, key names) -> <out>/moves_<lane>.csv (one row a literal) and <out>/excluded.csv (reason each)
    python Tools/export/literal_to_tunable.py move --csv <list> [--dry-run]
        the list: CSV with at least file,line,literal,key (file under Scripts/, line 1-based; optional col = 1-based column
        of the literal token, occurrence, unit, kind, linh_vuc, note). Refuses (writes nothing) a row it cannot do safely.
    python Tools/export/literal_to_tunable.py check --base <rev> [--out <md>]
        §2.2 a-e (mbconst check: token / tree diff, default == json == literal, one literal a key, Roslyn compile of Sim +
        Game with the Unity DLLs, expression types), then `dotnet build Tools/simbuild/Sim.csproj` and the export mapping
        of tunables.json -> Docs/export/current/_qa/equivalence.md (the _qa folder is not committed)
    python Tools/export/literal_to_tunable.py status
        scan_constants "co" rows per lane (what is left)

No Unity, no tests, no export.py (DECISIONS "Pack 2 pass 2 (09/10)").
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "Tools/export/mbconst"
DLL = TOOL / "bin/Debug/net9.0/mbconst.dll"
SCRIPTS = "Assets/MachineBrigade/Scripts"
TUNABLES = ROOT / "Assets/MachineBrigade/Resources/Data/tunables.json"
PASS2 = ROOT / "Tools/export/pack2/pass2"
LANES = ("weapons", "vehicles", "boss", "bases", "modes_campaign", "ai_rest")

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <!-- Balance pack 2: the Roslyn tool behind Tools/export/literal_to_tunable.py (git-ignored: *.csproj). Uses the Roslyn
       that ships inside the .NET SDK (no NuGet download). -->
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <AssemblyName>mbconst</AssemblyName>
    <RootNamespace>MbConst</RootNamespace>
    <InvariantGlobalization>true</InvariantGlobalization>
    <NoWarn>$(NoWarn);CS8618;CS0649</NoWarn>
    <SdkRoslynDir Condition="'$(SdkRoslynDir)' == ''">$(NetCoreRoot)sdk\\$(NETCoreSdkVersion)\\Roslyn\\bincore\\</SdkRoslynDir>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="Microsoft.CodeAnalysis"><HintPath>$(SdkRoslynDir)Microsoft.CodeAnalysis.dll</HintPath></Reference>
    <Reference Include="Microsoft.CodeAnalysis.CSharp"><HintPath>$(SdkRoslynDir)Microsoft.CodeAnalysis.CSharp.dll</HintPath></Reference>
  </ItemGroup>
</Project>
"""

# ------------------------------------------------------------------------------------------------ the policy (§3.1)
# scan_constants proposes "co" by name and folder; the Roslyn scan classifies each literal (gameplay / visual / infra /
# index / already_data, with its reason). A row is moved when the Roslyn scan calls it gameplay, unless a rule below
# proves it is not (presentation, meta progression, index, RNG salt, structure); a row the Roslyn scan excluded is moved
# anyway when its reason is a false positive of the scan's name rules (FORCE_MOVE). Doubt counts as gameplay.

# Game/Match files whose numbers never reach the simulation (owner: Game/Match moves only Sim-affecting numbers)
GAME_EXCLUDE_FILES = {
    "Game/Match/Dialogue.cs": "presentation: radio / dialogue pacing on the HUD; the simulation never reads it",
    "Game/Match/RadioDirector.cs": "presentation: radio line pacing and its RNG seed; the simulation never reads it",
    "Game/Match/ReactiveRadio.cs": "presentation: radio line pacing; the simulation never reads it",
    "Game/Match/Narrative.cs": "campaign chapter numbers (ids compared with ==), not quantities",
    "Game/Match/Narrative.Data.cs": "campaign chapter number of an intel entry (an id), not a quantity",
    "Game/Match/DailyMissions.cs": "meta progression: daily mission goals / coin rewards in the menu and their day seed; not the simulation",
    "Game/Match/P34StressCheck.cs": "developer stress check (P34StressCheck), not shipped gameplay",
    "Game/Match/Skins.cs": "cosmetic (camouflage pattern scale)",
    "Game/Match/WeeklyFortress.cs": "calendar arithmetic (ISO week id and week -> map index)",
    "Game/Match/MatchRunner.Warnings.cs": "presentation: the warning ring's on-screen lifetime (view)",
    "Game/Match/MatchRunner.BossParts.cs": "presentation: toast seconds",
    "Game/Match/MatchRunner.Ending.cs": "presentation: the end-of-match note's timing",
    "Game/Match/MatchRunner.MissionEvents.cs": "presentation: toast seconds, arrow threshold, haptics",
    "Game/Match/MatchRunner.cs": "presentation: toast seconds and the tower art's bar count",
    "Game/Match/MatchRunner.Dialogue.cs": "presentation: how often the dialogue director re-checks for a boss (frames)",
    "Game/Match/ShowdownSession.cs": "presentation (toast seconds) and the after-battle coin reward",
    "Game/Match/PlayerCommander.cs": "input geometry: half the support line's length at the tap point",
}
# (file, member) pairs inside otherwise-gameplay Game/Match files
GAME_EXCLUDE_MEMBERS = {
    ("Game/Match/ModeSessions.cs", "Outcome"): "after-battle coin / reward arithmetic (Rewards.Quick minutes, coins per boss, tier cap): meta, not the simulation",
    ("Game/Match/ModeSessions.cs", "UpdateHud"): "presentation: HUD stage number and percent",
    ("Game/Match/Gear.Fit.cs", "Unhide"): "RNG salt (stream id of RngFor), not a quantity",
    ("Game/Match/Gear.Fit.cs", "MakeFit"): "RNG salt (stream id of RngFor), not a quantity",
    ("Game/Match/Gear.Model.cs", "NormalSlots"): "structure: the number of equipment slots (screens, save format and arrays size by it)",
    ("Game/Match/Gear.Tower.cs", "TowerSlotCount"): "structure: the number of tower equipment slots (screens and save format size by it)",
    ("Game/Match/Gear.Model.cs", "TraitCandidates"): "menu: how many trait cards the forge offers (a UI choice count)",
    ("Game/Match/Gear.Model.cs", "RollTrait"): "menu: how many trait cards the forge offers (a UI choice count)",
    ("Game/Match/Gear.Tower.cs", "TowerTraitCandidates"): "menu: how many trait cards the forge offers (a UI choice count)",
}
# a literal value on a line of these members that is an index bound (rarity 0-4, tier 0-2)
INDEX_BOUNDS = {
    ("Game/Match/Gear.Model.cs", "4"): "index bound: rarity 0-4 (five rarities, the Top[] arrays' last index)",
    ("Game/Match/Gear.Tower.cs", "4"): "index bound: rarity 0-4 (five rarities, the Top[] arrays' last index)",
    ("Game/Match/ModeSessions.cs", "1e-3f"): "math: float epsilon of a 'not exactly 1' test",
}
# Sim rows the Roslyn scan left out by a name rule that misfires here: moved anyway
FORCE_MOVE = [
    (re.compile(r"^Format code"), lambda c: "Formation" in c["file"] or "Formation" in c["member"],
     "the scan's 'Format' rule matched 'Formation': squad formation spacing is gameplay"),
    (re.compile(r"^Mix code"), lambda c: c["member"] == "EnemyMix",
     "the scan's 'Mix' rule matched EnemyMix: the AI's estimate of the enemy army mix is gameplay, not a hash"),
    (re.compile(r"^presentation value"), lambda c: c["file"].startswith("Sim/AI/"),
     "the AI's own estimate (DamageTable.Effective) decides a target: gameplay"),
    (re.compile(r"^default of a data read"), lambda c: True,
     "the fallback of a data read (used when a data block leaves the field out): moved like pass 1's Catalog.P25A defaults"),
    (re.compile(r"^Parse code"), lambda c: (c["file"], int(c["line"])) in PARSE_GAMEPLAY,
     "a clamp / default applied to a data value while parsing: gameplay"),
    (re.compile(r"not reachable from the simulation"), lambda c: not TOOLING_UNREACHABLE(c),
     "the call graph found no simulation caller, but the number belongs to gameplay data / rules (doubt counts as gameplay)"),
    (re.compile(r"^0 / 1 / -1"), lambda c: c["context"] == "table",
     "an element of a value table (its 0 / 1 are values like the other elements, not an identity)"),
    (re.compile(r"^loop start / step"), lambda c: (c["file"], int(c["line"])) == ("Sim/Bosses/BossSystem.cs", 167),
     "half the sea lane's patrol width decides where a boss ship's goal may fall: gameplay, not a loop step"),
]
PARSE_GAMEPLAY = {
    ("Sim/Content/Catalog.Extra.cs", 138), ("Sim/Content/Catalog.Extra.cs", 228),
    ("Sim/Content/Catalog.P25A.cs", 274), ("Sim/Content/Catalog.P25A.cs", 286), ("Sim/Content/Catalog.P25A.cs", 294),
    ("Sim/Content/Catalog.P25A.cs", 313), ("Sim/Content/Catalog.P25A.cs", 318), ("Sim/Content/Catalog.P25A.cs", 328),
    ("Sim/Content/Catalog.P25A.cs", 344), ("Sim/Content/Catalog.P25A.cs", 345), ("Sim/Content/Catalog.P25A.cs", 354),
    ("Sim/Content/Catalog.P25A.cs", 361),
    ("Sim/Content/HqTypeRules.cs", 179), ("Sim/Content/HqTypeRules.cs", 228), ("Sim/Content/EscortDefs.cs", 247),
    ("Sim/Content/BaseRules.cs", 220), ("Sim/Content/BaseRules.cs", 245), ("Sim/Content/AiBehaviour.cs", 202),
    ("Sim/Content/WeaponDef.Stick.cs", 129),
}
TOOLING_FILES = ("Sim/Sandbox/", "Sim/Navigation/MapStressScenes.cs", "Sim/Navigation/WeatherPresentation.cs",
                 "Sim/AI/P5/ReasonCodes.cs")
TOOLING_MEMBERS = {("Sim/Navigation/GameplayTopology.Ground.cs", "Audit"), ("Sim/Navigation/GameplayTopology.Ground.cs", "Fairness"),
                   ("Sim/Navigation/GameplayTopology.Gates.cs", "BuildWarnings"), ("Sim/Navigation/CoverGrid.cs", "MemoryBytes"),
                   ("Sim/Navigation/NavGrid.cs", "MemoryBytes"), ("Sim/Navigation/CoverGrid.cs", ".ctor"),
                   ("Sim/Navigation/NavGrid.cs", ".ctor"), ("Sim/Movement/TrafficCoordinator.cs", "DebugOf"),
                   ("Sim/Content/Matchup.cs", "ThreatProfile"), ("Sim/Content/Matchup.cs", "ColumnCount"),
                   ("Sim/Content/TierDefs.cs", "Verdict"), ("Sim/Content/WeaponDef.P34.cs", "BarrelGap")}


def TOOLING_UNREACHABLE(c) -> bool:
    return c["file"].startswith(TOOLING_FILES) or (c["file"], c["member"]) in TOOLING_MEMBERS


TOOLING_REASON = ("not reachable from the simulation and part of a tool (sandbox lab, map stress scenes, topology audits, "
                  "debug / memory readouts, handbook matrix, barrel spacing of the model)")

# literals that C# requires to be compile-time constants, or that are indexes / bit widths: never moved (reason each)
CONSTANT_CONTEXT = {
    "pattern": "C# pattern (is >= a and < b): needs a compile-time constant; here an index / team / stage bound",
    "case label": "C# case label: needs a compile-time constant (an id)",
    "attribute argument": "C# attribute argument: needs a compile-time constant",
    "enum member": "enum value (an id)",
}
MANUAL_EXCLUDE = {
    ("Sim/Combat/DamageSystem.cs", "0.4f"): "dead parameter: DamageSystem.Splash's edgeShare is no longer read (its doc says so; the splash row replaced it)",
    # (file, line, literal): reason
    ("Sim/Content/Armour.cs", "5"): "structure: the number of armour levels (ArmourLevels.Max, a const that sizes tables: Levels = Max + 1)",
    ("Sim/Content/DamageTable.cs", "7"): "structure: the penetration table's column count (PenetrationSteps, used in a pattern and table sizes)",
    ("Sim/Core/SimClock.cs", "20"): "the simulation's time base (20 ticks a second): every tick count in the data assumes it; not a balance value",
    ("Sim/Core/SimClock.cs", "5"): "frame budget of the fixed-step clock (steps caught up a frame): engine infrastructure",
}


# literals the Roslyn scan calls gameplay that are math, geometry, structure or infrastructure (each rule a reason)
GEOMETRY_OPERAND = re.compile(r"(?i)(length|width|depth|breadth|extent|stick)(scale)?$")
STRUCTURE_LINES = {
    # (file, line): reason; the table's shape, not its values
    ("Sim/Content/DamageTable.cs", 53): "structure: the splash row's step count (the row's length; changing it breaks every table)",
    ("Sim/Content/DamageTable.cs", 56): "structure: the overpenetration row's step count (the row's length)",
    ("Sim/Content/DamageTable.cs", 90): "structure: the data row's accepted length (a 5-entry row skips its first column)",
    ("Sim/Content/DamageTable.cs", 171): "structure: the penetration row's column offset (column 2 = penetration equals armour)",
    ("Sim/Content/DamageTable.cs", 257): "structure: the overpenetration row starts 2 columns past the penetration row (one convention, three uses)",
    ("Sim/Content/DamageTable.cs", 258): "structure: the overpenetration row starts 2 columns past the penetration row (one convention, three uses)",
    ("Sim/Content/DamageTable.cs", 259): "structure: the overpenetration row starts 2 columns past the penetration row (one convention, three uses)",
}
STRUCTURE_RESULTS = {
    # (file, line): the integer results of these lines are step indexes (the thresholds on them stay data)
    ("Sim/Content/DamageTable.cs", 229): "index: the splash step number this distance falls in (the thresholds are data)",
    ("Sim/Content/DamageTable.cs", 234): "index: the splash step number this distance falls in (the thresholds are data)",
}
MATH_MEMBERS = {
    ("Sim/Combat/CombatSystem.Bombs.cs", "StickDirection"): "math: the principal axis of a point cloud (0.5 x atan2(2 cxy, cxx - cyy)), not a tunable",
    ("Sim/Combat/CombatSystem.Bombs.cs", "BombFall"): "physics: free-fall time sqrt(2 h / g) (its 4 m floor is data)",
}


def _math_rule(c, src_line: str):
    """A reason when this literal is math / geometry / structure / infrastructure, else None."""
    f, lit, ctx = c["file"], c["literal"], c["context"]
    v = _number(lit)
    ln = int(c["line"])
    col = int(c["col"]) - 1
    before = src_line[:col]
    if (f, ln) in STRUCTURE_LINES:
        return STRUCTURE_LINES[(f, ln)]
    if (f, ln) in STRUCTURE_RESULTS and ctx == "conditional" and c["type"] == "int":
        return STRUCTURE_RESULTS[(f, ln)]
    if (f, c["member"]) in MATH_MEMBERS and (c["member"] != "BombFall" or v == 2):
        return MATH_MEMBERS[(f, c["member"])]
    if v is not None and v != 0 and abs(v) <= 1e-3 and (ctx in ("math_max", "math_min", "math_clamp", "compare", "subtract", "add", "equals")
                                                         or "e-" in lit.lower()):
        return "math: a float epsilon (guards a division or a 'not zero' test)"
    if v is not None and abs(v) >= 1e6:
        return "sentinel: a huge number meaning 'none' / 'never' (not a quantity)"
    if v in (31, 32, 63, 64) and re.search(r"<<|>>", src_line):
        return "bit width: the team bit mask / a 32-bit shift"
    if re.search(r"\.Count\s*>\s*" + re.escape(lit) + r"\)\s*\w+\.Clear\(\)", src_line):
        return "infrastructure: a cache's size cap (memory), not gameplay"
    if re.search(r"new\s+(System\.)?Random\(", src_line) and ctx in ("multiply", "add"):
        return "RNG seed salt: an arbitrary constant mixed into a seed"
    if v in (2, 3) and re.search(r"\(3f?\s*-\s*2f?\s*\*\s*\w+\)", src_line) and ctx in ("subtract", "multiply"):
        return "math: smoothstep 3u^2 - 2u^3"
    if ctx == "math_round":
        return "math: rounding digits"
    if v == 0.5 and ctx == "subtract" and re.search(r"NextDouble\(\)\)?\s*-\s*$", before):
        return "math: a random draw centred on 0 (r - 0.5)"
    if v is not None and 0 < v <= 0.01 and ctx == "compare" and re.search(r"Length(Squared)?\(\)\s*[<>]=?\s*" + re.escape(lit), src_line):
        return "math: a zero-length guard (a vector is normalised only when it is longer than this)"
    if v == 0.01 and ctx == "add" and re.search(r"[<>]", src_line):
        return "math: a float tolerance on a comparison"
    if v == 3 and re.search(r"poly\.Count\s*<\s*3", src_line):
        return "math: a polygon needs three points"
    if v == 2 and ctx == "compound_assign" and re.search(r"\+=\s*2\)", src_line) and "flat" in src_line:
        return "data format: x, z pairs"
    if ctx == "modulo" and v == 2:
        return "math: parity (even / odd: alternate sides, or x, z pairs in the data)"
    if ctx == "modulo" and v in (90, 180, 360):
        return "math: an angle's quadrant"
    if "FormatException" in src_line and ctx in ("equals", "compare", "modulo"):
        return "data format check: the parser's expected count (a malformed file throws)"
    if ctx == "equals" and v == 2 and re.search(r"\.Count\s*==\s*2\s*\?\s*\w+\[0\]", src_line):
        return "data format: a [min, max] pair"
    if ctx == "equals" and re.search(r"_teams\.Count\s*!=\s*2", src_line):
        return "structure: a battle has two teams"
    if ctx == "equals" and re.search(r"(?i)(stage|phase|kind|index|slot)$", c["name_hint"][:-2] if c["name_hint"].endswith("Is") else c["name_hint"]):
        return "index: an id / stage / phase number compared with == (not a quantity)"
    if ".Append(" in src_line and ("Sandbox" in f or "ToString(Inv)" in src_line):
        return "text / save format of a scenario (serialisation)"
    if v == 2 and ctx == "multiply" and re.search(r"(?i)radius(scale)?$", c["name_hint"]):
        return "geometry: a diameter (2 x a radius)"
    if v == 0.5 and ctx == "multiply":
        hint = c["name_hint"]
        if GEOMETRY_OPERAND.search(hint) or re.search(r"(?i)(length|width|depth)\s*\*\s*$", before):
            return "geometry: half of a length / width / depth (a box's half-extent; the §3.5 whitelist's math constant)"
        if re.search(r"-\s*1\)\s*\*\s*$", before):
            return "geometry: centring k - (n - 1) / 2 of a row of n slots (math)"
    return None


def _rel(path: str) -> str:
    return path[len(SCRIPTS) + 1:] if path.startswith(SCRIPTS + "/") else path


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", **kw)


def build(_args=None) -> int:
    proj = TOOL / "MbConst.csproj"
    if not proj.exists():
        proj.write_text(CSPROJ, "utf-8")
    r = _run(["dotnet", "build", str(proj), "-nologo", "-v", "q", "-clp:NoSummary"], capture_output=True)
    errors = [l for l in (r.stdout + r.stderr).splitlines() if "error CS" in l]
    print(f"build mbconst: exit {r.returncode}, {len(errors)} error line(s)")
    for l in errors[:10]:
        print("  " + l.strip())
    return r.returncode


def _tool(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    if not DLL.exists() and build() != 0:
        raise SystemExit("mbconst does not build")
    return _run(["dotnet", str(DLL), *args], capture_output=capture)


# ------------------------------------------------------------------------------------------------ plan

def _scan_co():
    sys.path.insert(0, str(ROOT / "Tools/export"))
    from scan_constants import scan  # noqa: E402
    return [r for r in scan(ROOT) if r["de_xuat_dua_ra_du_lieu"] == "co"]


def _number(text: str):
    t = text.lstrip("-").rstrip("fFdDmMuUlL")
    try:
        v = float(t) if not t.lower().startswith("0x") else float(int(t, 16))
    except ValueError:
        return None
    return v


def _join(co, cand):
    """Each scan_constants row -> its Roslyn literal(s): so_cung by line + value + column; a declaration by its line."""
    by = collections.defaultdict(list)
    for c in cand:
        by[(c["file"], int(c["line"]))].append(c)
    out, miss = [], []
    for r in co:
        f, ln = _rel(r["tep"]), r["dong"]
        cs = by.get((f, ln), [])
        if r["loai"] == "so_cung" and isinstance(r["gia_tri"], (int, float)):
            v = abs(float(r["gia_tri"]))
            m = [c for c in cs if _number(c["literal"]) == v]
            if len(m) > 1:
                m = [c for c in m if abs(int(c["col"]) - r["cot"]) <= 1] or m[:1]
            m = m[:1]
        else:
            m = cs  # a const / static readonly declaration: every literal of its initializer
        if not m:
            miss.append(r)
        for c in m:
            out.append((r, c))
    return out, miss


_LINES: dict = {}


def _source_line(f: str, ln: int) -> str:
    if f not in _LINES:
        _LINES[f] = (ROOT / SCRIPTS / f).read_text("utf-8-sig").splitlines()
    lines = _LINES[f]
    return lines[ln - 1] if 0 < ln <= len(lines) else ""


def _decide(r, c):
    """('move', lane, how-note) or ('exclude', reason)."""
    f, member, lit = c["file"], c["member"], c["literal"]
    if f.startswith("Game/"):
        if f in GAME_EXCLUDE_FILES:
            return "exclude", GAME_EXCLUDE_FILES[f]
        if (f, member) in GAME_EXCLUDE_MEMBERS:
            return "exclude", GAME_EXCLUDE_MEMBERS[(f, member)]
        if (f, lit) in INDEX_BOUNDS:
            return "exclude", INDEX_BOUNDS[(f, lit)]
        if f == "Game/Match/ModeSessions.cs" and member == "Build" and "MissionTier" in c["line_text"]:
            return "exclude", "index bound: mission tier 0-2"
    if (f, lit) in MANUAL_EXCLUDE:
        return "exclude", MANUAL_EXCLUDE[(f, lit)]
    cls, reason = c["class"], c["reason"]
    m = _math_rule(c, _source_line(f, int(c["line"])))
    if m:
        return "exclude", m
    if cls != "gameplay":
        for rx, test, why in FORCE_MOVE:
            if rx.search(reason) and test(c):
                break
        else:
            if "not reachable" in reason and TOOLING_UNREACHABLE(c):
                return "exclude", TOOLING_REASON
            return "exclude", f"{cls}: {reason}"
    mode = c["mode"]
    if mode.startswith("manual:"):
        why = mode[7:]
        for k, text in CONSTANT_CONTEXT.items():
            if why.startswith(k):
                return "exclude", text
        if why.startswith(("static array table", "static initializer is an expression")):
            pass  # the move tool's --static-init handles these (read once at type initialisation)
        elif why.startswith("parameter default"):
            pass  # the move tool's --param-defaults: "T x = lit" -> "T? x = null" + "(x ?? field)" in the body
        else:
            return "manual", why
    lane = c["lane"] or "ai_rest"
    return "move", lane


def _unit(c) -> str:
    """The scan's unit, except for a pure factor (x ... Scale / Divisor / Factor) and a share."""
    name = c["key"].rsplit(".", 1)[-1]
    if re.search(r"(Scale|Divisor|Factor|Mult|Multiplier)\d*$", name):
        return "x"
    if re.search(r"(Share|Chance|Odds)\d*$", name):
        return "share"
    return c["unit"]


def plan(args) -> int:
    out = Path(args.out) if args.out else PASS2
    out.mkdir(parents=True, exist_ok=True)
    scan_dir = ROOT / "Temp/literal_to_tunable"
    scan_dir.mkdir(parents=True, exist_ok=True)
    if not args.reuse_scan:
        r = _tool("scan", "--out", str(scan_dir / "pass1"), "--lists", str(scan_dir / "lists"), capture=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            return 1
    cand = list(csv.DictReader(open(scan_dir / "pass1/candidates.csv", encoding="utf-8-sig")))
    co = _scan_co()
    pairs, miss = _join(co, cand)
    moves = collections.defaultdict(list)
    excluded, manual = [], []
    seen = set()
    for r, c in pairs:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        d = _decide(r, c)
        if d[0] == "move":
            moves[d[1]].append(c)
        elif d[0] == "exclude":
            excluded.append((c, d[1]))
        else:
            manual.append((c, d[1]))
    head = ["file", "line", "col", "literal", "key", "unit", "kind", "linh_vuc", "mode", "note", "context"]
    dom = {"weapons": "01", "vehicles": "02", "bosses": "03", "bases": "04", "modes": "05", "ai": "06", "campaign": "07", "maps": "08"}
    for lane in LANES:
        rows = sorted(moves.get(lane, []), key=lambda c: (c["file"], int(c["line"]), int(c["col"])))
        with open(out / f"moves_{lane}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(head)
            for c in rows:
                mode = "pass2:" + (c["mode"][7:] if c["mode"].startswith("manual:") else c["mode"])
                w.writerow([c["file"], c["line"], c["col"], c["literal"], c["key"], _unit(c), c["group"],
                            dom.get(c["key"].split(".")[0], ""), mode, "", f"{c['context']}: {c['line_text'][:150]}"])
    with open(out / "excluded.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "line", "col", "literal", "member", "reason", "line_text"])
        for c, why in sorted(excluded + manual, key=lambda x: (x[0]["file"], int(x[0]["line"]), int(x[0]["col"]))):
            w.writerow([c["file"], c["line"], c["col"], c["literal"], c["member"], why, " ".join(c["line_text"].split())[:160]])
    print(f"plan: {len(co)} scan rows 'co', {len(pairs)} literal(s) joined, {len(miss)} not found by Roslyn")
    for lane in LANES:
        print(f"  moves_{lane}.csv: {len(moves.get(lane, []))}")
    print(f"  excluded.csv: {len(excluded)} excluded, {len(manual)} manual (left with a reason or hand-edited)")
    for r in miss[:20]:
        print("  not found:", _rel(r["tep"]), r["dong"], r["gia_tri"], r["ngu_canh"][:80])
    return 0


# ------------------------------------------------------------------------------------------------ move

def move(args) -> int:
    rows = list(csv.DictReader(open(args.csv, encoding="utf-8-sig")))
    need = {"file", "line", "literal", "key"}
    if rows and not need <= set(rows[0]):
        raise SystemExit(f"{args.csv}: needs columns {sorted(need)}")
    cmd = ["move", "--csv", str(Path(args.csv).resolve()), "--fileset", "pass2", "--signed", "--static-init", "--param-defaults"]
    if args.dry_run:
        cmd.append("--dry-run")
    r = _tool(*cmd, capture=True)
    text = r.stdout + r.stderr
    lines = text.splitlines()
    print("\n".join(lines[-12:] if r.returncode == 0 else lines[:80]))
    return r.returncode


# ------------------------------------------------------------------------------------------------ check

def _export_mapping() -> list[str]:
    """Every leaf of tunables.json is one the export maps (core/tunables.py: group -> owner -> name -> the five fields)."""
    sys.path.insert(0, str(ROOT / "Tools/export"))
    from core.jsonc import strip  # noqa: E402
    from core.tunables import GROUPS  # noqa: E402
    data = json.loads(strip(TUNABLES.read_text("utf-8")))
    problems = []
    fields = {"value", "unit", "kind", "linh_vuc", "code"}
    for group, block in data.items():
        if group == "version":
            continue
        if group not in GROUPS:
            problems.append(f"group '{group}' has no sheet in core/tunables.py GROUPS")
            continue
        for owner, items in block.items():
            for name, entry in items.items():
                if not isinstance(entry, dict) or "value" not in entry:
                    problems.append(f"{group}.{owner}.{name}: not an object with 'value'")
                elif set(entry) - fields:
                    problems.append(f"{group}.{owner}.{name}: field(s) the export does not map: {sorted(set(entry) - fields)}")
    return problems


def check(args) -> int:
    out = Path(args.out) if args.out else ROOT / "Docs/export/current/_qa/equivalence.md"
    r = _tool("check", "--base", args.base, "--out", str(out), "--dotnet", capture=True)
    tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
    sim = _run(["dotnet", "build", "Tools/simbuild/Sim.csproj", "-nologo", "-v", "q", "-clp:NoSummary"], capture_output=True)
    log = sim.stdout + sim.stderr
    errs = sorted(set(re.findall(r"error CS\d+[^\r\n]*", log)))
    warns = sorted(set(re.findall(r"warning (CS\d+)", log)))
    mapping = _export_mapping()
    with open(out, "a", encoding="utf-8") as fh:
        fh.write("\n## dotnet build Tools/simbuild/Sim.csproj (working tree)\n\n")
        fh.write(f"exit {sim.returncode}; {len(errs)} error(s); warning ids: {', '.join(warns) or 'none'}\n\n")
        for e in errs[:20]:
            fh.write(f"- {e}\n")
        fh.write("\n## export mapping of tunables.json (Tools/export/core/tunables.py)\n\n")
        fh.write("PASS: every leaf is mapped\n" if not mapping else "FAIL:\n" + "".join(f"- {p}\n" for p in mapping))
    for d in (ROOT / "Temp/simbuild",):
        pass  # the build output stays under Temp/ (git-ignored)
    print("\n".join(tail))
    print(f"dotnet build Sim.csproj: exit {sim.returncode}, {len(errs)} error(s); export mapping: {'PASS' if not mapping else 'FAIL ' + str(len(mapping))}")
    return 0 if r.returncode == 0 and sim.returncode == 0 and not errs and not mapping else 1


# ------------------------------------------------------------------------------------------------ status

def status(_args) -> int:
    co = _scan_co()
    c = collections.Counter()
    for r in co:
        p = _rel(r["tep"]).split("/")
        c["/".join(p[:2]) if len(p) > 2 else p[0]] += 1
    print(f"scan_constants 'co' rows: {len(co)}")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")
    return 0


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p = sub.add_parser("plan")
    p.add_argument("--out")
    p.add_argument("--reuse-scan", action="store_true", help="reuse Temp/literal_to_tunable/pass1 (no new Roslyn scan)")
    p = sub.add_parser("move")
    p.add_argument("--csv", required=True)
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("check")
    p.add_argument("--base", required=True)
    p.add_argument("--out")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    return {"build": build, "plan": plan, "move": move, "check": check, "status": status}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
