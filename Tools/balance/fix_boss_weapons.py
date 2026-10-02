"""Full fix prompt L3: the boss weapons at their real cadence, the DPS as the result (DECISIONS "Sửa lỗi tổng hợp L3").

    python Tools/balance/fix_boss_weapons.py                      # dry run: the plan and the per-boss table
    python Tools/balance/fix_boss_weapons.py --write              # save balance.json, the report and the reasons
    python Tools/balance/fix_boss_weapons.py --write --only behemoth   # only the weapons that boss owns (commit per boss)

This replaces prompt 34 L2 (`p34_boss_families.py`, retired): that pass kept the prompt 26 DPS of every weapon and solved
the cadence from it, so the big guns fired 3-12 times faster than real. Here:
  1. The family's round stays as prompt 34 put it (weaponFamilyTable "boss": damage, core, edge; one speed and damage type
     a family), the same on every boss.
  2. The cadence is the real one, family by family (CADENCE below): the wave 1 proposal of the sheet "Vũ khí đề xuất"
     where it is not too fast or too slow against the real rate (full_weapon_audit's rule), else the real rate itself.
     An autoloaded gun is never faster than its real maximum.
  3. The DPS is what comes out. A boss whose sustained ground DPS falls more than 20 % is made up with more barrels firing
     together (twin / triple mounts, MAKEUP below) or more mounts, never with a shorter reload. What cannot be made up is
     reported. The boss health formula (P x t x 0.6) is not touched.
The first run stores today's numbers in Tools/balance/fix_boss_before.json; every later run reports against them.
Left alone: Gungnir's weapons (only its main gun's name and calibre display, fix rule 8), the weapons a boss shares with a
player vehicle or a tower (the player rule: Docs/balance/player_weapon_waitlist.md), the 406 mm salvo (every 60 s, prompt
34's trial table: 1.4 x the real gap after the 30 % rule, within the window), the super weapons and the laid cruise missiles.
"""
from __future__ import annotations

import collections
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import full_weapon_audit as W  # noqa: E402
import p26_ab as A  # noqa: E402
import p34_families as F  # noqa: E402
import steps_c as S  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

ROOT = F.ROOT
BEFORE = os.path.join(HERE, "fix_boss_before.json")
REPORT = os.path.join(ROOT, "Docs", "balance", "boss_weapon_families.md")
REASONS = W.REASONS
MAKEUP_FROM = 0.8   # a boss whose ground DPS falls under 80 % of before is made up

SINGLE = {"burst": 1, "clip": 0, "clipReload": 0, "barrels": 1, "salvoMode": "RIPPLE"}


def single(cd):
    return dict(SINGLE, cooldown=cd)


def salvo(n, bi, cd):
    return {"burst": n, "burstInterval": bi, "cooldown": cd, "clip": 0, "clipReload": 0, "barrels": 1, "salvoMode": "RIPPLE"}


def magazine(n, cd, change):
    return {"clip": n, "cooldown": cd, "clipReload": change, "burst": 1, "barrels": 1, "salvoMode": "RIPPLE"}


def volley(barrels, cd):
    return {"burst": 1, "barrels": barrels, "salvoMode": "SIMULTANEOUS", "cooldown": cd, "clip": 0, "clipReload": 0}


# family key: (the cadence, the boss weapons that fire it, the reason (a) / (b))
CADENCE = {
    "2a65": (volley(2, 8.98), ["p26_behemoth_main_be152"],
             "wave 1 gun_behemoth: the twin 2A65, 2 rounds every 8.98 s (real 7-8 rpm a gun, Msta-B): passes (b)"),
    "rh120": (single(7.5), ["p26_behemoth_tiny_be120", "p26_behemoth_direct_be120", "p26_moloch_direct_mo120ap", "p26_moloch_main_mo120"],
              "real Rh-120 with a loader, 8 rpm (7.5 s); wave 1's 5.1 s is too fast after the 30 % rule"),
    "2a46": (single(7.5), ["p26_jotunn_direct_jo125", "p26_nemesis_direct_ne125", "p26_ixion_125"],
             "real 2A46 with its autoloader, 8 rpm (7.5 s); wave 1's 5.56 s is too fast after the 30 % rule"),
    "2a44": (single(24), ["p26_jotunn_jo203"],
             "real 2S7M Malka 2.5 rpm (24 s); wave 1's 9.44 s is too fast"),
    "2b8": (single(60), ["p26_bastion_sec_b240"],
            "real 2S4 Tyulpan ~1 rpm (60 s); wave 1's 10 s is too fast"),
    "m284": (single(15), ["p26_bastion_main_b155"],
             "real M109A7 4 rpm (15 s) at its maximum; wave 1's 12.5 s is too fast after the 30 % rule"),
    "d10": (single(8.6), ["p26_bastion_direct_b100"], "real D-10 4-7 rpm (8.6 s at 7)"),
    "152rail": (single(7.5), ["p26_nemesis_main_ne152"],
                "a 152 mm railway gun of the 2A65 class, 8 rpm (7.5 s); the 4-round 0.5 s salvo was 6 x too fast"),
    "b38": (single(8), ["train_gun"], "real B-38 5-7.5 rpm (8 s at 7.5); wave 1's 5.11 s is too fast"),
    "155_60": (volley(3, 10.5), ["p26_leviathan_sec_lev155"],
               "wave 1 naval_155_triple: the triple turret, 3 rounds every 10.5 s (real ~5 rpm a gun): passes (b)"),
    "ak130": (volley(2, 3.0), ["naval_130_twin"],
              "real AK-130 10-40 rpm a barrel: 20 rpm (3 s), practical; 4.75 s was too slow"),
    "a192": (single(3.0), ["p26_leviathan_direct_lev127"], "an A-192 class 130 mm, 30 rpm max: 20 rpm practical (3 s)"),
    "ak100": (salvo(2, 1.0, 2.5), ["p26_typhon_direct_ty100"],
              "wave 1 naval_100's pair every 3.5 s, the rounds 1 s apart (AK-100 60 rpm; wave 1's 0.5 s is twice the real rate)"),
    "au220": (salvo(4, 0.5, 2.79), ["p26_typhon_sec_ty57", "p26_daedalus_sec_dae57", "p26_kronos_direct_kr57",
                                    "p26_matriarch_tiny_mothership_cannon"],
              "wave 1 mothership_cannon: 4 rounds 0.5 s apart every 4.29 s (AU-220M 120 rpm)"),
    "2a42": (salvo(10, 0.1111, 1.5), ["p26_matriarch_sec_autocannon_30", "p26_kronos_close_autocannon_30"],
             "wave 1 autocannon_30: 10 rounds at 540 rpm every 2.5 s (2A42 550-800 rpm)"),
    "2a42x2": (salvo(12, 0.0833, 1.45), ["p26_roc_close_twin_30_bmpt"],
               "wave 1 twin_30_bmpt: 12 rounds at 720 rpm, 1.45 s after (wave 1's 1.5 s is a hair over 2 x the practical rate)"),
    "patriot": (salvo(2, 3.0, 8.0), ["sam_battery"],
                "MIM-104 Patriot: the pair ~3 s apart (est.; 0.45 s was too fast), the 11 s cycle kept"),
    "grad": (None, ["p26_behemoth_sec_be_rockets", "p26_nemesis_sec_boss_rockets", "p26_kronos_close_boss_rockets", "boss_rockets"],
             "wave 1 boss_rockets: rockets 0.5 s apart (BM-21: 40 in 20 s), 2.44 s after the ripple; each pod keeps its rockets"),
    "smerch": (None, ["p26_jotunn_sec_jo_rockets"],
               "real BM-30 Smerch 12 rockets in 38 s (3.17 s apart), wave 1 rockets_300mm's 15.76 s after the ripple"),
    "kornet": (single(20), ["p26_behemoth_tiny_boss_missiles", "p26_matriarch_direct_ma_atgm"],
               "real 9M133 Kornet 3 rpm (20 s); wave 1's 6.39 s is too fast"),
    "kornet2": (salvo(2, 0.6, 19.4), ["p26_behemoth_tiny_kornet_twin", "p26_bastion_tiny_kornet_twin", "p26_roc_direct_roc_atgm"],
                "a twin Kornet launcher: the pair 0.6 s apart, every 20 s (3 rpm a rail); 55.6 s was too slow"),
    "bofors": (magazine(10, 0.2, 1.52), ["p26_bastion_tiny_autocannon_40", "p26_icarus_close_autocannon_40"],
               "wave 1 autocannon_40: 10 rounds at 300 rpm, changed in 1.52 s (Bofors L/70 240-330 rpm)"),
    "nsv": (magazine(100, 0.0833, 5.0), ["p26_bastion_close_boss_hmg", "p26_ixion_mg", "boss_hmg"],
            "wave 1 boss_hmg: 100 rounds at 720 rpm, changed in 5 s (NSV 700-800 rpm)"),
    "zu23": (magazine(50, 0.04, 3.0), ["p26_bastion_tiny_zu23", "p26_moloch_tiny_zu23"],
             "wave 1 zu23: 50 rounds at 1,500 rpm, changed in 3 s (ZU-23-2 2 x 800-1,000 rpm)"),
    "gdf": (magazine(41, 0.05, 3.38), ["p26_behemoth_close_boss_flak", "p26_jotunn_close_boss_flak", "p26_matriarch_close_boss_flak",
                                       "p26_nemesis_close_boss_flak", "p26_moloch_close_boss_flak"],
            "wave 1 boss_flak: 41 rounds at 1,200 rpm, changed in 3.38 s (twin Oerlikon GDF 2 x 550 rpm)"),
    "2a38": (magazine(160, 0.025, 3.0), ["p26_jotunn_tiny_twin_30_flak"],
             "wave 1 twin_30_flak: 160 rounds at 2,400 rpm, changed in 3 s (2A38M 4,060-5,000 rpm the pair)"),
    "m102": (single(6), ["p26_roc_roc105"], "real M102 10 rpm (6 s); wave 1's 2.74 s is too fast after the 30 % rule"),
    "2a70": (single(6), ["borer_cannon"], "real 2A70 10 rpm (6 s); 2.08 s was too fast"),
    "ogon": (None, ["hover_rockets"], "A-22 Ogon 140 mm: est. 0.5 s a rocket (0.1 s was too fast), the 22 s pause kept"),
}
RIPPLE = {"grad": 0.5, "smerch": 3.17, "ogon": 0.5}
PAUSE = {"grad": 2.44, "smerch": 15.76}

# Kept as they are, with the reason the audit shows (WAVE 1 / FAMILY): {weapon: reason}
KEPT = {
    "p26_roc_main_roc_bombs": "a 400 kg bomb stick from an airship's bay: no real rate for the bay's reload; the 35.4 s cycle kept",
    "p26_matriarch_ma_drones": "a six-drone swarm: no real rate and no wave 1 row (wave 1's mothership_drones is a 4-drone salvo)",
    "p26_icarus_main_ic_coil": "a 64 MJ coilgun, its own family (rail_heavy_coilgun): no real rate",
    "p26_leviathan_lev406": "the 406 mm salvo every 60 s (prompt 34's trial table; 1.4 x the real gap after the 30 % rule)",
    "p26_daedalus_direct_dae_laser": "a laser: no real rate", "p26_icarus_direct_ic_laser": "a laser: no real rate",
    "p26_icarus_sec_orbital_laser": "a laser: no real rate",
    "autocannon_40": "Gungnir's 40 mm guns: frozen (fix rule 8); their 1 m burst is Gungnir's own",
    "gunship_105": "shared with the player's AC-130: the player rule (Docs/balance/player_weapon_waitlist.md)",
}

# Make-up (rule 5): more barrels firing together, by the real mount or wave 1. {weapon: (barrels, why)}; applied on top of
# CADENCE. Each barrel gets its own Muzzle_b<k> on the model (Tools/blender/mb_fix_barrels.py).
MAKEUP = {
    "p26_behemoth_direct_be120": (2, "a twin Rh-120 (wave 1's gun_120_twin)"),
    "p26_moloch_main_mo120": (2, "a twin Rh-120 (wave 1's gun_120_twin)"),
    "p26_moloch_direct_mo120ap": (2, "a twin Rh-120 (wave 1's gun_120_twin)"),
    "p26_typhon_sec_ty57": (2, "a twin 57 mm deck mount (as the real AK-725 twin 57 mm)"),
    "p26_daedalus_sec_dae57": (2, "a twin 57 mm belly mount (as the real AK-725 twin 57 mm)"),
    "p26_bastion_direct_b100": (2, "the twin D-10 casemates the fortress model already has"),
}
# Make-up with more tubes on a rocket launcher (a ripple: no muzzle per tube): {weapon: (tubes, why)}
TUBES = {
    "p26_behemoth_sec_be_rockets": (40, "a full BM-21 pack of 40 tubes (8 before)"),
    "p26_nemesis_sec_boss_rockets": (40, "a full BM-21 pack of 40 tubes (13 before)"),
}

# Data fixes that go with this pass: {weapon: fields}
RENAMES = {
    "p26_icarus_main_ic_coil": {"real": "heavy coilgun (64 MJ)", "weaponFamilyId": "rail_heavy_coilgun"},
    "p26_typhon_sec_ty57": {"real": "AU-220 57 mm (twin deck mount)"},
    "p26_daedalus_sec_dae57": {"real": "AU-220 57 mm (twin belly mount)"},
    "p26_bastion_direct_b100": {"real": "D-10 100 mm (twin casemate)"},
    "p26_behemoth_direct_be120": {"real": "Rh-120 L/44 120 mm (twin)"},
    "p26_moloch_main_mo120": {"real": "Rh-120 L/44 120 mm HE (twin)"},
    "p26_moloch_direct_mo120ap": {"real": "Rh-120 L/44 120 mm AP (twin)"},
}
NEW_FAMILIES = [("rail_heavy_coilgun", "heavy coilgun (64 MJ)", 3)]


def cadence_of(key, w):
    fields, _ids, _why = CADENCE[key]
    if fields is not None:
        return dict(fields)
    n = TUBES[w["id"]][0] if w["id"] in TUBES else int(w.get("burst", 1))
    f = salvo(n, RIPPLE[key], PAUSE.get(key, float(w.get("cooldown", 1.0))))
    return f


def plan(data):
    ws = F.Weapons(data)
    edits, reasons = {}, {}
    for key, (_f, ids, why) in CADENCE.items():
        for wid in ids:
            w = ws.resolve(wid)
            f = cadence_of(key, w)
            if wid in MAKEUP:
                b, mwhy = MAKEUP[wid]
                f.update({"barrels": b, "salvoMode": "SIMULTANEOUS", "clip": 0, "clipReload": 0})
                why = why + "; made up: " + mwhy
            if wid in TUBES:
                why = why + "; made up: " + TUBES[wid][1]
            edits[wid] = f
            reasons[wid] = why
    for wid, f in RENAMES.items():
        edits.setdefault(wid, {}).update(f)
    for wid, why in KEPT.items():
        reasons.setdefault(wid, why)
    return ws, edits, reasons


def changed_fields(ws, wid, f):
    """The fields that differ from the resolved line (0 / RIPPLE / 1 defaults count as absent)."""
    w = ws.resolve(wid)
    defaults = {"clip": 0, "clipReload": 0, "burst": 1, "barrels": 1, "salvoMode": "RIPPLE", "burstInterval": 0.1}
    out = {k: v for k, v in f.items() if w.get(k, defaults.get(k)) != v}
    p25 = w.get("weaponFamily")
    if out and p25 and p25 in ws.p25:
        block = ws.p25[p25]
        if any(k in block for k in out):
            out["weaponFamily"] = ""
            for k in block:
                if k not in ("id", "real") and k not in out:
                    out[k] = w.get(k)
    return out


def pins(data, ws, edits, boss_ids):
    """Lines that inherit a changed weapon and are not changed themselves (a player's, a tower's, an unused line) keep
    their old values: {line: fields}."""
    kids = collections.defaultdict(list)
    for w in data["weapons"]:
        if w.get("inherits"):
            kids[w["inherits"]].append(w["id"])
    out = {}
    for wid, f in edits.items():
        todo = list(kids.get(wid, []))
        while todo:
            c = todo.pop()
            todo += kids.get(c, [])
            if c in edits:
                continue
            cw = ws.resolve(c)
            for k in f:
                old = cw.get(k, {"clip": 0, "clipReload": 0, "burst": 1, "barrels": 1, "salvoMode": "RIPPLE"}.get(k))
                if k not in ws.raw[c] and old != f[k]:
                    out.setdefault(c, {})[k] = old
    return out


# ------------------------------------------------------------------------------------------------ the per-boss table

def mount_rows(ws, b):
    rows = []
    for k, wid in enumerate(S.mounts_of(b)):
        if not wid or wid not in ws.raw:
            continue
        w = ws.resolve(wid)
        nb = W.numbers(w)
        laid = bool(w.get("laid"))
        rows.append({"mount": k, "id": wid, "real": w.get("real"), "fam": w.get("weaponFamilyId"), "damage": w.get("damage", 0),
                     "core": w.get("splash", 0), "edge": w.get("edge", 0), "n": nb["n"], "barrels": nb["barrels"], "sim": nb["sim"],
                     "cycle": nb["cycle"], "dps": 0.0 if laid else nb["dps"], "air": w.get("targets", "Ground") == "Air", "laid": laid})
    s = b.get("salvo")
    if isinstance(s, dict) and s.get("weapon"):
        turrets = sum(1 for p in b.get("parts") or [] if p.get("kind") == "maingun")
        rows.append({"mount": "salvo", "id": s["weapon"], "real": "406 mm salvo", "fam": "cal_406", "damage": s.get("damage"),
                     "core": s.get("radius"), "edge": s.get("edge"), "n": turrets * s.get("shells", 3), "barrels": 3, "sim": True,
                     "cycle": s.get("every"), "dps": turrets * s.get("shells", 3) * s.get("damage", 0) / s.get("every", 60),
                     "air": False, "laid": False})
    return rows


def snapshot(data):
    ws = F.Weapons(data)
    built = A.expand(data)
    return {bid: mount_rows(ws, b) for bid, b in built.items()}


def totals(rows):
    g = sum(r["dps"] for r in rows if not r["air"])
    a = sum(r["dps"] for r in rows if r["air"])
    return g, a


ARMOUR = {}   # boss -> (before, after): the DPS against armour 3 (prompt 26's measure), filled by armour3()


def armour3(data, before, after):
    """Each boss's DPS on armour 3: a mount's DPS x its type and penetration factor (p26_ab) x weaponDamage (not laid)."""
    ws = F.Weapons(data)
    built = A.expand(data)
    for bid, b in built.items():
        wd = b.get("weaponDamage", 1)
        fac = {}
        for k, wid in enumerate(S.mounts_of(b)):
            if not wid or wid not in ws.raw:
                continue
            w = ws.resolve(wid)
            f = A.TYPES.get(w.get("damageType", "Kinetic"), 1.0) * S.pen_step(A.PENS, int(w.get("pen", 0)) - 3)
            fac[(k, wid)] = f * (1 if w.get("laid") else wd)
        fac[("salvo", A.expand(data)[bid].get("salvo", {}).get("weapon") if isinstance(b.get("salvo"), dict) else None)] = 1.0

        def eff(rows):
            return sum(r["dps"] * fac.get((r["mount"], r["id"]), 1.0) for r in rows if not r["air"])
        ARMOUR[bid] = (eff(before.get(bid, [])), eff(after.get(bid, [])))


def report(before, after, reasons):
    out = ["# Boss weapon families: before and after (full fix prompt L3)", "",
           "Written by `Tools/balance/fix_boss_weapons.py` (it replaces prompt 34 L2's `p34_boss_families.py`, retired). Before =",
           "the data after prompt 34 (stored in `Tools/balance/fix_boss_before.json`): each weapon's cadence solved from the old",
           "prompt 26 DPS. After = the real cadence family by family (wave 1 where it passes the real rate, else the real rate),",
           "the family's round unchanged; the DPS is the result. DPS on paper: a cycle's rounds over the cycle, every barrel,",
           "before the boss's own factors (weaponDamage, rank, phases). Ground = every mount that can fire at the ground; air =",
           "the anti-air-only mounts. No battle was run. Health: unchanged (the formula P x t x 0.6 is not recalculated).", "",
           "## The family table (boss scale) and the cadence", "",
           "| family | weapons | cadence | why |", "|---|---|---|---|"]
    for key, (f, ids, why) in CADENCE.items():
        if f is None:
            cad = f"ripple {RIPPLE[key]} s apart, {PAUSE.get(key, 'own')} s after"
        elif f.get("salvoMode") == "SIMULTANEOUS":
            cad = f"{f['barrels']} barrels together every {f['cooldown']} s"
        elif f.get("clip"):
            cad = f"{f['clip']} rounds {f['cooldown']} s apart, changed in {f['clipReload']} s"
        elif f.get("burst", 1) > 1:
            cad = f"{f['burst']} rounds {f['burstInterval']} s apart, {f['cooldown']} s after"
        else:
            cad = f"one round every {f['cooldown']} s"
        out.append(f"| {key} | {', '.join('`' + i + '`' for i in ids)} | {cad} | {why} |")
    out += ["", "## Per boss", ""]
    summary = []
    for bid in after:
        b0 = before.get(bid, [])
        b1 = after[bid]
        g0, a0 = totals(b0)
        g1, a1 = totals(b1)
        ratio = g1 / g0 if g0 else 1.0
        made = sorted({r["id"] for r in b1 if r["id"] in MAKEUP or r["id"] in TUBES})
        summary.append((bid, g0, g1, ratio, a0, a1, made))
        out.append(f"### {bid}")
        out.append("")
        out.append(f"Ground DPS **{g0:.0f} -> {g1:.0f}** ({ratio * 100:.0f} %); anti-air only {a0:.0f} -> {a1:.0f}."
                   + (f" Made up: {', '.join('`' + m + '` ' + mk_words(m) for m in made)}." if made else "")
                   + (" **Not made up within 20 %** (see below)." if ratio < MAKEUP_FROM else ""))
        out.append("")
        out.append("| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |")
        out.append("|---|---|---|---|---|---|")
        old = {(r["mount"], r["id"]): r for r in b0}
        for r in b1:
            o = old.get((r["mount"], r["id"]), r)
            bar = f" ({r['barrels']} together)" if r["sim"] and r["barrels"] > 1 else ""
            laid = " (laid)" if r["laid"] else ""
            out.append(f"| {r['mount']} | `{r['id']}` | {r['fam']} | {o['damage']:g} x {o['n']} / {o['cycle']:.2f} s = {o['dps']:.0f}{laid} "
                       f"| {r['damage']:g} x {r['n']}{bar} / {r['cycle']:.2f} s = {r['dps']:.0f}{laid} | {r['core']:g} / {r['edge']:g} |")
        out.append("")
    out += ["## Totals", "",
            "Ground = the raw sustained DPS (the rule's measure, as prompt 34's table). Armour 3 = prompt 26's measure: each mount's",
            "DPS x its damage type and penetration against armour 3 (p26_ab's tables) x the boss's weaponDamage, for the owner.", "",
            "| boss | ground before | ground after | after / before | armour 3 before -> after | anti-air before -> after | make-up |",
            "|---|---|---|---|---|---|---|"]
    for bid, g0, g1, ratio, a0, a1, made in summary:
        mk = ", ".join(f"`{m}` {mk_words(m)}" for m in made) or "-"
        flag = " **(< 80 %)**" if ratio < MAKEUP_FROM else ""
        e0, e1 = ARMOUR.get(bid, (0.0, 0.0))
        out.append(f"| {bid} | {g0:.0f} | {g1:.0f} | {ratio * 100:.0f} %{flag} | {e0:.0f} -> {e1:.0f} | {a0:.0f} -> {a1:.0f} | {mk} |")
    out += ["", "## Kept as they are", ""]
    for wid, why in KEPT.items():
        out.append(f"- `{wid}`: {why}.")
    out.append("")
    return "\n".join(out), summary


def check_muzzles(data):
    """Every boss weapon whose barrels fire together has, on each carrier's own model, a Muzzle_<slot> with a Muzzle_b<k> per
    barrel (as Prompt34ValidatorTests.EveryBarrelFiredTogetherHasItsMuzzle; a carrier drawn with another model is its base's)."""
    import re
    import struct
    models = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Models")
    ws = F.Weapons(data)
    built = A.expand(data)
    problems = []
    for bid, b in built.items():
        model = b.get("model") or bid
        path = os.path.join(models, model + ".glb")
        if model in ("kraken",) or not os.path.exists(path):
            continue
        mounts = [(b.get("slot") or b.get("mainSlot") or "main", b.get("weapon"))] +                  [(m.get("slot"), m.get("weapon")) for m in b.get("secondary") or []]
        with open(path, "rb") as fh:
            raw = fh.read()
        n = struct.unpack_from("<I", raw, 12)[0]
        nodes = json.loads(raw[20:20 + n])["nodes"]
        for slot, wid in mounts:
            if not wid or wid not in ws.raw:
                continue
            w = ws.resolve(wid)
            barrels = int(w.get("barrels", 1) or 1)
            if w.get("salvoMode") != "SIMULTANEOUS" or barrels < 2:
                continue
            best = 0
            for nd in nodes:
                if (nd.get("name") or "").startswith("Muzzle_" + str(slot)):
                    kids = [nodes[c].get("name", "") for c in nd.get("children", [])]
                    best = max(best, sum(1 for k in kids if re.match(r"^Muzzle_b\d+_", k)))
            if best < barrels:
                problems.append(f"{bid} ({model}).{slot} {wid}: {best} barrel muzzles of {barrels}")
    return problems


def mk_words(m):
    return f"{MAKEUP[m][0]} barrels together" if m in MAKEUP else f"{TUBES[m][0]} tubes"


def owner_of(built, wid):
    for bid, b in built.items():
        if wid in S.mounts_of(b):
            return bid
    return None


def main():
    write = "--write" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    doc = Doc(F.PATH)
    data = doc.data()
    if os.path.exists(BEFORE):
        with open(BEFORE, encoding="utf-8") as fh:
            before = json.load(fh)
    else:
        before = snapshot(data)
        if write:
            with open(BEFORE, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(before, fh, indent=1)
    ws, edits, reasons = plan(data)
    built = A.expand(data)
    boss_ids = set(built)
    pinned = pins(data, ws, edits, boss_ids)
    changed = 0
    for wid, f in edits.items():
        if only and owner_of(built, wid) != only:
            continue
        cf = changed_fields(ws, wid, f)
        if cf and F.set_on(doc, wid, cf, ws.rounds):
            changed += 1
        for c, pf in pinned.items():
            if ws.raw[c].get("inherits") == wid or c in pinned:
                pass
    for c, pf in pinned.items():
        if F.set_on(doc, c, pf, ws.rounds):
            changed += 1
    if not only or only == "silver_bug":
        # The heavy coilgun's own family in the table.
        t = doc.text
        for fid, name, tier in NEW_FAMILIES:
            if f'"id": "{fid}"' not in t:
                anchor = '    { "id": "rail_coilgun"'
                line = f'    {{ "id": "{fid}", "name": "{name}", "tier": {tier} }},\n'
                if anchor in t:
                    i = t.index(anchor)
                    doc.text = t[:i] + line + t[i:]
                else:
                    i = t.index('    { "id": "wpn_none"')
                    doc.text = t[:i] + line + t[i:]
                changed += 1
    print(f"{changed} lines changed{' (' + only + ')' if only else ''}")
    for p in check_muzzles(doc.data()):
        print("MUZZLES:", p)
    after = snapshot(doc.data())
    armour3(doc.data(), before, after)
    text, summary = report(before, after, reasons)
    for bid, g0, g1, ratio, a0, a1, made in summary:
        mark = " <80%" if ratio < MAKEUP_FROM else ""
        print(f"{bid:20s} ground {g0:6.0f} -> {g1:6.0f} ({ratio * 100:4.0f} %){mark}  air {a0:5.0f} -> {a1:5.0f}")
    if write:
        doc.save()
        with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        old = {}
        if os.path.exists(REASONS):
            with open(REASONS, encoding="utf-8") as fh:
                old = json.load(fh)
        old.update(reasons)
        with open(REASONS, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(old, fh, indent=1, sort_keys=True, ensure_ascii=False)
        print("written")


if __name__ == "__main__":
    main()
