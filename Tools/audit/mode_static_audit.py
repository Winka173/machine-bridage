"""Prompt 30 L8: the static mode audit (sheet "Chế độ"): four ledgers per mode at 25/50/75/100 % of its target length.

    python Tools/audit/mode_static_audit.py

Writes Docs/checks/mode_static_audit.md. Theory only: nothing is simulated and no win rate is predicted. Each side's
strength at a moment is the sum of
  - Economy: CP the side can have spent by then (start CP + income x the global income scale x seconds, plus point
    income where points pay, on an even split of the points); bank caps do not limit it because CP is spent as it comes;
  - Free / scripted: waves, airlifts and bosses that cost the side nothing, as CP-equivalents (a vehicle at its base CP;
    a boss at its health over the roster's health per CP);
  - Static: fixed defences at start (hardpoints, towers, the fortress), as CP-equivalents the same way;
  - Tempo: the path from the drop zone to the first objective at a medium tank's speed (seconds), from
    Docs/checks/map_audit.csv; reported beside the strength, not added to it.
The band is the enemy's strength over the player's. Symmetric modes: a gap over 30 % RED, 20-30 % YELLOW. Asymmetric
modes (Assault, Siege, Defend, Survival, Boss Rush, Weekly) are reported by role and never held to 1:1. Every number
comes from the code and data named in MODES; Normal difficulty.
"""
from __future__ import annotations

import csv
import os
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "Docs", "checks", "mode_static_audit.md")
MAP_CSV = os.path.join(ROOT, "Docs", "checks", "map_audit.csv")
TANK_SPEED = 6.5  # main_battle_tank speed (m/s)

# Read from the code (Game/Match/ModeSessions.cs, Sim/Modes) and balance.json: start CP, income (per second, before the
# global economy.income scale), the target length (the sheet's range, its middle) and what else each side gets.
MODES = {
    "Conquest": {"symmetric": True, "minutes": (6, 10), "player": (14, 1.0), "enemy": (14, 1.0 * 1.18),
                 "points": 3, "pointIncome": 0.15, "src": "ConquestSession: StartCp 14, PointIncome 0.15, enemy income x1.18"},
    "Deathmatch": {"symmetric": True, "minutes": (6, 9), "player": (18, 1.35), "enemy": (18, 1.2),
                   "src": "DeathmatchSession: 18/1.35 vs 18/1.2"},
    "KingOfTheHill": {"symmetric": True, "minutes": (6, 9), "player": (16, 1.2), "enemy": (16, 1.1), "holder": 0.35,
                      "src": "KingOfTheHillSession: 16/1.2 vs 16/1.1; the holder +0.35/s"},
    "Assault": {"symmetric": False, "minutes": (8, 12), "player": (20, 1.45), "enemy": (32, 1.3), "sectorCp": 8, "sectors": 3,
                "sectorBonus": 0.25, "src": "AssaultSession: attacker 20/1.45, defender 32/1.3, 8 CP and +0.25/s a sector; sector defences not counted"},
    "Siege": {"symmetric": False, "minutes": (10, 15), "player": (38, 2.4), "enemy": (20, 0.8), "fortressSlots": 31,
              "src": "SiegeSession: attacker 38/2.4, defender 20/0.8; fortress hardpoints from the maps (31)"},
    "Weekly": {"symmetric": False, "minutes": (10, 15), "player": (38, 2.4), "enemy": (20, 0.8), "fortressSlots": 31,
               "src": "as Siege (broken rings stay broken over the week: not modelled)"},
    "Defend": {"symmetric": False, "minutes": (11, 13), "player": (30, 1.35), "enemy": (22, 1.1), "playerTowers": True,
               "waves": {"first": 70, "every": 70, "start": 3, "growth": 1.8, "max": 36},
               "src": "DefendSession: defender 30/1.35 + its base; attacker 22/1.1 + waves 3 + 1.8/wave every 70 s"},
    "Survival": {"symmetric": False, "minutes": (8, 12), "player": (16, 0.9), "enemy": (0, 0.0),
                 "waves": {"first": 20, "every": 30, "start": 3, "growth": 0.9, "max": 48}, "bosses": {5: "mini", 10: "main"},
                 "src": "SurvivalSession / SandboxMode: player 16/0.9; waves 3 + 0.9/wave every 30 s from 20 s; bosses at 5 and 10"},
    "BossRush": {"symmetric": False, "minutes": (15, 25), "player": (30, 1.5), "enemy": (0, 0.0), "bossesPer": 10,
                 "src": "BossRushSession: player 30/1.5; ten bosses over the run"},
}
WAVE_ROSTER = ["light_tank", "scout_jeep", "armored_car", "ifv", "rocket_technical", "main_battle_tank", "attack_helicopter",
               "tank_destroyer", "flame_tank", "scout_heli", "mortar_carrier", "artillery", "aa_vehicle", "mlrs",
               "heavy_tank", "attack_jet"]


def balance():
    sys.path.insert(0, os.path.join(ROOT, "Tools", "ai"))
    import export_applied_xlsx as E  # noqa: E402
    return E.balance()


def tempo(mode):
    """Median seconds from a drop zone to its first objective on the battlefields this mode uses."""
    if not os.path.exists(MAP_CSV):
        return "-"
    suffix = "_siege" if mode in ("Siege", "Weekly") else "_long" if mode == "Defend" else "_conquest"
    rows = [r for r in csv.DictReader(open(MAP_CSV, encoding="utf-8")) if r["map"].endswith(suffix)]
    out = []
    for key in ("pathToObjective0", "pathToObjective1"):
        vals = [float(r[key]) for r in rows if r[key]]
        out.append(f"{statistics.median(vals) / TANK_SPEED:.0f} s" if vals else "-")
    return " / ".join(out)


def main():
    b = balance()
    scale = b["economy"]["income"]
    vehicles = {v["id"]: v for v in b["vehicles"]}
    roster = [vehicles[i] for i in WAVE_ROSTER if i in vehicles]
    mean_cp = statistics.mean(v.get("cp", 0) for v in roster)
    hp_per_cp = statistics.mean(v.get("hp", 0) / max(1, v.get("cp", 1)) for v in roster)
    towers = [v for v in b["vehicles"] if v.get("static") and v.get("fort") and v.get("hp")]
    tower_eq = statistics.mean(v["hp"] for v in towers) / hp_per_cp if towers else 10.0
    mini_eq = vehicles.get("bastion_mk0", {}).get("hp", 6000) / hp_per_cp
    main_eq = vehicles.get("behemoth", {}).get("hp", 15000) / hp_per_cp
    levels = b.get("base", {}).get("levels", [])
    base_towers = sum(levels[2].get(k, 0) for k in ("small", "medium", "large")) if len(levels) > 2 else 7
    out = ["# Mode static audit (prompt 30 L8, theory only)", "",
           "Generated by `Tools/audit/mode_static_audit.py`. Four ledgers per mode (Economy, Free/scripted, Static, Tempo) "
           "at 25/50/75/100 % of the mode's target length (the middle of the sheet's range), Normal difficulty. Strength is "
           "in CP-equivalents; the band is enemy / player. **No win rate is predicted.** Old measured numbers belong in "
           "the design document's measurement history, not here.", "",
           f"Constants: global income scale {scale}; wave vehicle {mean_cp:.1f} CP on average (Survival's roster); a "
           f"fixed defence ≈ {tower_eq:.1f} CP and a mini boss ≈ {mini_eq:.0f}, a main boss ≈ {main_eq:.0f} CP by health "
           f"per CP of that roster; a player base at level 3 ≈ {base_towers} towers.", "",
           "Limits: CP that could be spent is not CP that is spent well; bank caps, supply upkeep, the catch-up, the "
           "underdog help, card ranks, commanders, events and the AI's choices are not modelled; Assault's sector "
           "defences and Weekly's carried-over damage are left out.", ""]
    flags = []
    for mode, m in MODES.items():
        lo, hi = m["minutes"]
        length = (lo + hi) / 2 * 60
        out += [f"## {mode} ({lo}-{hi} min, {'symmetric' if m['symmetric'] else 'asymmetric'})", "", f"Source: {m['src']}.", "",
                "| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |",
                "|---|---|---|---|---|---|---|---|---|"]
        for share in (0.25, 0.5, 0.75, 1.0):
            t = length * share
            pe = m["player"][0] + m["player"][1] * scale * t
            ee = m["enemy"][0] + m["enemy"][1] * scale * t
            if "points" in m:
                half = m["points"] / 2 * m["pointIncome"] * scale * t
                pe += half
                ee += half
            if "holder" in m:
                pe += m["holder"] / 2 * scale * t
                ee += m["holder"] / 2 * scale * t
            if "sectorCp" in m:
                taken = min(m["sectors"], int(share * m["sectors"]))
                pe += taken * m["sectorCp"] + m["sectorBonus"] * scale * t * (taken / 2)
            pf = ef = ps = es = 0.0
            if "waves" in m:
                w = m["waves"]
                n = max(0, int((t - w["first"]) // w["every"]) + 1) if t >= w["first"] else 0
                if mode == "Survival":
                    n = min(n, 10)
                ef = sum(min(w["max"], w["start"] + w["growth"] * (k - 1)) for k in range(1, n + 1)) * mean_cp
                for wave, kind in m.get("bosses", {}).items():
                    if n >= wave:
                        ef += mini_eq if kind == "mini" else main_eq
            if "bossesPer" in m:
                ef = m["bossesPer"] * share * (mini_eq + main_eq) / 2
            if "fortressSlots" in m:
                es = m["fortressSlots"] * tower_eq
            if m.get("playerTowers"):
                ps = base_towers * tower_eq
            p, e = pe + pf + ps, ee + ef + es
            band = e / max(1e-6, p)
            flag = "-"
            if m["symmetric"]:
                gap = abs(1 - band)
                flag = "RED" if gap > 0.30 else "YELLOW" if gap > 0.20 else "GREEN"
                if flag != "GREEN":
                    flags.append(f"{mode} at {int(share * 100)} %: {flag} ({band:.2f})")
            out.append(f"| {int(share * 100)} | {pe:.0f} | {pf:.0f} | {ps:.0f} | {ee:.0f} | {ef:.0f} | {es:.0f} | {band:.2f} | {flag} |")
        out += ["", f"Tempo (drop zone to first objective, player / enemy): {tempo(mode)}.", ""]
    out.insert(10, "**Flags:** " + ("; ".join(flags) if flags else "no symmetric mode outside 20 %.") + "\n")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(flags) or "no flags")


if __name__ == "__main__":
    main()
