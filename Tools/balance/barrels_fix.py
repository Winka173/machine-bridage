"""Barrels (owner 06/10, DECISIONS "## Barrels: battleship triple turrets + audit"): every multi-barrel gun turret fires its
barrels together, and the data's barrels match the barrels the model shows (Tools/assets/barrel_audit.py finds them).

    python Tools/balance/barrels_fix.py           # dry run: the plan, every DPS before / after
    python Tools/balance/barrels_fix.py --write   # save balance.json and Docs/models/barrel_fix.json (a rerun changes nothing)

Each changed gun becomes "barrels": N, "salvoMode": "SIMULTANEOUS" and keeps its DPS (WeaponDef.SustainedDps) by one of:

  D  (a single-shot gun, burst 1, no magazine; the battleship rule): every barrel fires a round of damage / N at the old
     cooldown, so a volley still does the old round's damage and the DPS is unchanged. The look and sound stay the
     calibre's ("roundWeight" = the old round's damage, unless the weapon's family already sets it).
  C  (a boss's single-shot gun whose round is its family's boss round, Tools/balance/p34_boss_families.py; fix_validate
     item 2 holds every boss line of a family to one round): the round keeps its damage and the cooldown grows N times,
     so the DPS is unchanged (a volley does N rounds).
  V  (a gun that fired its barrels as a salvo, burst B = k x N): burst B / N volleys of N rounds, N x burstInterval
     apart (each barrel keeps its own pace); the cooldown takes (N - 1) x burstInterval more, so the cycle, the rounds a
     cycle and the DPS are unchanged.
  S  (a stream gun firing from a magazine): N rounds a volley at N x the cooldown, so the rounds a second, the tracers
     and the DPS are unchanged; the magazine counts volleys (round(clip / N)) and its reload is set so a whole cycle's
     damage over its time is the old DPS exactly (WeaponDef.RoundsPerCycle = clip x barrels).

A shared weapon whose carriers show different barrels gets a unit's own variant (new lines below, "mountWeapons" or the
unit's own list). A line that inherits from a changed one and is not in the plan keeps its numbers (pinned on its own
line); a second round of a changed gun follows the gun's new cadence (its DPS is checked too); a guided round goes one
at a time (one barrel).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import p34_families as F  # noqa: E402
from jsonc_edit import Doc, Entry  # noqa: E402

OUT = os.path.join(ROOT, "Docs", "models", "barrel_fix.json")

# weapon -> (barrels, method, carriers)
PLAN = {
    "naval_406_bs": (3, "D", "battleship: the Iowa triple 406 mm turrets (model rebuilt with three barrels a turret)"),
    "aa_25_triple": (3, "S", "leviathan: the Type 96 25 mm triples"),
    "boss_flak": (2, "S", "mara_behemoth (and the bosses' close flak lines that inherit it): the Oerlikon 35 mm twin"),
    "p26_matriarch_close_boss_flak": (4, "S", "drone_mothership, locust: the model's flak mounts are quads"),
    "p26_behemoth_close_boss_flak": (2, "S", "behemoth, behemoth_mk2: the Oerlikon 35 mm twin"),
    "p26_jotunn_close_boss_flak": (2, "S", "mobile_fortress, fenrir: the Oerlikon 35 mm twin"),
    "p26_moloch_close_boss_flak": (2, "S", "moloch: the Oerlikon 35 mm twin"),
    "bunker_hmg_twin": (2, "S", "mg_bunker.twin: the NSV 12.7 mm twin"),
    "flak_35": (2, "S", "aa_vehicle: the Gepard's two KDA 35 mm"),
    "pt14_th_v35": (2, "S", "theia: the ventral twin 35 mm"),
    "flak_quad": (4, "S", "aa_turret.flak: the ZSU-23-4 quad"),
    "gun_57_auto": (2, "S", "gun_turret.auto: the AU-220 57 mm twin (two barrels, ripple before)"),
    "twin_30_flak": (4, "S", "heavy_aa: two 2A38 twins, four barrels at one muzzle"),
    "hq_flak": (2, "S", "headquarters (and its HQ types): the 2A38 twin"),
    "tower_flak_30": (2, "S", "aa_turret: the 2A38 twin"),
    "p26_jotunn_tiny_twin_30_flak": (2, "S", "mobile_fortress: the 2A38 twin"),
    "p26_bastion_close_boss_hmg": (2, "S", "fortress_bastion, monster: the model's twin HMG mounts"),
    "p26_bastion_tiny_zu23": (2, "S", "fortress_bastion, monster: the ZU-23-2 (two barrels, ripple before)"),
    "p26_moloch_tiny_zu23": (2, "S", "moloch: the ZU-23-2 (two barrels, ripple before)"),
    "zu23_cheap": (2, "S", "zu23_technical: the ZU-23-2 (two barrels, ripple before)"),
    "scylla_2m7": (2, "S", "scylla: the 2M-7 twin 14.5 mm (two barrels, ripple before)"),
    "scylla_ak230": (2, "S", "scylla: the AK-230 twin 30 mm (two barrels, ripple before)"),
    "p26_icarus_close_autocannon_40": (2, "S", "silver_bug: the twin Bofors 40 mm"),
    "gun_120_twin": (2, "V", "twin_tank: the twin Rh-120"),
    "gun_behemoth": (2, "V", "mara_behemoth: the 2A65 152 mm twin"),
    "pt14_hp_155": (2, "V", "hyperion: the 155 mm twin turrets"),
    "pt14_co_v76": (2, "V", "coeus: the ventral twin 76 mm"),
    "pt14_sb_v30": (2, "V", "silver_bug: the ventral twin 30 mm"),
    "p26_matriarch_tiny_mothership_cannon": (2, "V", "drone_mothership: the twin AU-220 57 mm"),
    "p26_behemoth_tiny_be120": (2, "D", "behemoth: the twin 120 mm turret"),
    "p26_leviathan_direct_lev127": (2, "C", "leviathan, kraken: the twin 127 mm (nyx, scylla keep a single: p26_lev127_single)"),
    "p26_nemesis_main_ne152": (2, "D", "nuke_train: the twin 152 mm railcar gun (Main_cannon, Main_cannon_2)"),
    # Unit variants (new lines): (source, extra fields), then planned like the rest.
    "mara_120_twin": (2, "D", "mara_behemoth: the behemoth model's twin 120 mm (main_battle_tank keeps gun_120mm)"),
    "p26_hydra_ty100_twin": (2, "V", "hydra: the twin 100 mm deck gun (typhon keeps its single)"),
    "train_boss_flak_quad": (4, "S", "armored_train: the model's quad 35 mm mounts"),
}
# new weapon lines: id -> (inherits, after, extra fields)
NEW = {
    "mara_120_twin": ("gun_120mm", "gun_120mm", {"real": "Rh-120 L/44 120 mm (twin)"}),
    "p26_hydra_ty100_twin": ("p26_typhon_direct_ty100", "p26_typhon_direct_ty100", {"real": "AK-100 100 mm (deck, twin)"}),
    "train_boss_flak_quad": ("boss_flak", "boss_flak", {"real": "Oerlikon 35 mm (quad)"}),
    # Singles that keep today's numbers where a shared line became a twin / triple.
    "p26_kraken_aa25": ("aa_25_triple", "aa_25_triple", {}),
    "p26_lev127_single": ("p26_leviathan_direct_lev127", "p26_leviathan_direct_lev127", {}),
}
# unit -> {mount index: weapon} ("mountWeapons" on a boss or a boss variant; "secondary" on a plain unit)
UNITS = {
    "armored_train": {3: "train_boss_flak_quad", 5: "train_boss_flak_quad"},
    "kraken": {k: "p26_kraken_aa25" for k in range(7, 15)},
    "hydra": {2: "p26_hydra_ty100_twin"},
    "nyx": {1: "p26_lev127_single", 2: "p26_lev127_single"},
    "scylla": {1: "p26_lev127_single"},
    "mara_behemoth": {1: "mara_120_twin"},
}
EXTRA = {"naval_406_bs": {"real": "Mk 7 406 mm/50 (battleship, triple turret x3)"}}
KEYS = ("barrels", "salvoMode", "damage", "cooldown", "burst", "burstInterval", "clip", "clipReload")


def stats(w):
    """The numbers WeaponDef reads (defaults as Catalog's)."""
    return {
        "barrels": int(w.get("barrels", 1)),
        "simultaneous": w.get("salvoMode") == "SIMULTANEOUS",
        "damage": float(w.get("damage", 0)),
        "cooldown": float(w.get("cooldown", 1)),
        "burst": int(w.get("burst", 1)),
        "burstInterval": float(w.get("burstInterval", 0.1)),
        "clip": int(w.get("clip", 0) or 0),
        "clipReload": float(w.get("clipReload", 0) or 0),
        "roundWeight": float(w.get("roundWeight") or w.get("damage", 0)),
    }


def dps(s):
    """WeaponDef.SustainedDps (prompt 34 L4 and this pass: a magazine counts volleys)."""
    rpp = s["barrels"] if s["simultaneous"] else 1
    if s["clip"] > 0:
        rounds, cycle = s["clip"] * rpp, (s["clip"] - 1) * s["cooldown"] + s["clipReload"]
    else:
        rounds, cycle = s["burst"] * rpp, s["cooldown"] + (s["burst"] - 1) * s["burstInterval"]
    return s["damage"] * rounds / max(0.05, cycle)


def volley(s):
    """Damage one trigger pull fires (every barrel of a simultaneous gun)."""
    return s["damage"] * (s["barrels"] if s["simultaneous"] else 1)


def fields_for(s, n, method):
    """The new fields of a gun with stats s as an n-barrel simultaneous gun by method D, V or S."""
    f = {"barrels": n, "salvoMode": "SIMULTANEOUS"}
    if method == "D":
        assert s["burst"] == 1 and s["clip"] == 0, s
        f["damage"] = round(s["damage"] / n, 4)
        f["_roundWeight"] = s["roundWeight"]
    elif method == "C":
        assert s["burst"] == 1 and s["clip"] == 0, s
        f["cooldown"] = round(s["cooldown"] * n, 4)
    elif method == "V":
        assert s["clip"] == 0 and s["burst"] % n == 0 and s["burst"] >= n, s
        b = s["burst"] // n
        f["burst"] = b
        if b > 1:
            f["burstInterval"] = round(s["burstInterval"] * n, 4)
        f["cooldown"] = round(s["cooldown"] + (n - 1) * s["burstInterval"], 4)
    elif method == "S":
        assert s["clip"] > 0 and s["burst"] == 1, s
        old = dps(s)
        clip = max(1, int(round(s["clip"] / n)))
        cd = round(s["cooldown"] * n, 4)
        reload = clip * n * s["damage"] / old - (clip - 1) * cd
        assert reload > 0.2, (s, reload)
        f.update(cooldown=cd, clip=clip, clipReload=round(reload, 4))
    return f


def set_line(doc, wid, fields, rounds):
    def fn(e: Entry):
        for k, v in fields.items():
            e.set(k, v, after=F._after(e))
    if wid in rounds:
        return F.set_in_rounds(doc, wid, fields)
    return doc.edit("weapons", wid, fn)


def resolve_all(data):
    ws = F.Weapons(data)
    return ws, {wid: stats(ws.resolve(wid)) for wid in ws.raw}


def unit_edits(doc, data):
    by_id = {v["id"]: v for v in data["vehicles"]}
    changed = []
    for uid, swaps in UNITS.items():
        v = by_id[uid]
        boss = v.get("boss") is True or "frame" in v or "rank" in v or isinstance(v.get("variantOf"), str)
        if boss:
            mw = dict(v.get("mountWeapons") or {})
            for k, wid in swaps.items():
                mw[str(k)] = wid
            mw = dict(sorted(mw.items(), key=lambda kv: int(kv[0])))
            if doc.edit("vehicles", uid, lambda e, mw=mw: e.set("mountWeapons", mw, after="id")):
                changed.append(f"{uid}: mountWeapons {swaps}")
        else:
            def fn(e: Entry, swaps=swaps):
                sec = e.get("secondary")
                for k, wid in swaps.items():
                    sec[k - 1]["weapon"] = wid
                raw = e.raw("secondary")
                new = "[ " + ", ".join("{ " + ", ".join(f'"{a}": {json.dumps(b)}' for a, b in s.items()) + " }" for s in sec) + " ]"
                if json.loads(new) != json.loads(raw):
                    e.set_raw("secondary", new)
            if doc.edit("vehicles", uid, fn):
                changed.append(f"{uid}: secondary {swaps}")
    return changed


def main():
    write = "--write" in sys.argv
    path = F.PATH
    doc = Doc(path)
    data0 = doc.data()
    ws0, before = resolve_all(data0)
    rounds0 = set(ws0.rounds)
    # 1. the new lines (copies of today's numbers until step 2 changes them)
    for wid, (src, after, extra) in NEW.items():
        if wid in ws0.raw:
            continue
        fields = {"id": wid, "inherits": src}
        fields.update(extra)
        line = "{ " + ", ".join(f'"{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in fields.items()) + " }"
        doc.insert_after("weapons", after, line)
    for wid, extra in EXTRA.items():
        set_line(doc, wid, extra, rounds0)
    # The singles keep today's numbers of their source, pinned (the source changes below).
    pins = {}
    for wid, (src, _, _) in NEW.items():
        if wid not in PLAN and wid not in ws0.raw:
            s = before[src]
            pins[wid] = {"barrels": 1, "salvoMode": "RIPPLE", "damage": s["damage"], "cooldown": s["cooldown"],
                         "clip": s["clip"], "clipReload": s["clipReload"], "burst": s["burst"]}
            if not s["clip"]:
                del pins[wid]["clip"], pins[wid]["clipReload"]
    # 2. the plan, from each line's numbers today (a new line from its source's)
    plan_fields = {}
    for wid, (n, method, _) in PLAN.items():
        s = before.get(wid) or before[NEW[wid][0]]
        if wid in before and s["barrels"] == n and s["simultaneous"]:
            continue  # done (a rerun)
        f = fields_for(s, n, method)
        rw = f.pop("_roundWeight", None)
        full = F.Weapons(doc.data()).resolve(wid)   # with the family's roundWeight on top
        if rw is not None and "roundWeight" not in full:
            f["roundWeight"] = rw
        plan_fields[wid] = f
    for wid, f in {**pins, **plan_fields}.items():
        set_line(doc, wid, f, rounds0)
    # 3. lines that inherit a changed one and are not in the plan keep today's numbers; guided rounds one barrel
    for _ in range(4):
        ws1, after = resolve_all(doc.data())
        drift = {}
        for wid, s in after.items():
            if wid in PLAN or wid in NEW or wid not in before:
                continue
            r = ws1.raw[wid]
            gun = r.get("roundOf")
            follows = gun in PLAN and not (r.get("round") == "guided" or r.get("guided"))
            b = before[wid]
            if follows:
                # A round follows its gun's barrels and cadence; a D gun's round splits its damage the same way.
                if PLAN[gun][1] == "D" and abs(s["damage"] - b["damage"] / PLAN[gun][0]) > 1e-3:
                    drift[wid] = {"damage": round(b["damage"] / PLAN[gun][0], 4)}
                continue
            diff = {k: b[k] for k in ("barrels", "damage", "cooldown", "burst", "burstInterval", "clip", "clipReload")
                    if abs(s[k] - b[k]) > 1e-6}
            if s["simultaneous"] != b["simultaneous"]:
                diff["salvoMode"] = "SIMULTANEOUS" if b["simultaneous"] else "RIPPLE"
            if diff:
                drift[wid] = diff
        if not drift:
            break
        for wid, f in drift.items():
            set_line(doc, wid, f, ws1.rounds)
            print(f"pinned {wid}: {f}")
    changed_units = unit_edits(doc, doc.data())
    # 4. the proof: DPS before / after for every changed line and round
    ws2, after = resolve_all(doc.data())
    report, bad = [], []
    for wid, s in after.items():
        src = wid if wid in before else NEW.get(wid, (None,))[0]
        b = before.get(src)
        if b is None:
            continue
        if wid in before and all(abs(s[k] - b[k]) < 1e-9 for k in s if k != "simultaneous") and s["simultaneous"] == b["simultaneous"]:
            continue
        d0, d1 = dps(b), dps(s)
        row = dict(weapon=wid, source=src if src != wid else None, method=PLAN.get(wid, (0, "pin" if wid in NEW else "round"))[1],
                   barrels=[b["barrels"], s["barrels"]], simultaneous=[b["simultaneous"], s["simultaneous"]],
                   damage=[b["damage"], s["damage"]], cooldown=[b["cooldown"], s["cooldown"]], burst=[b["burst"], s["burst"]],
                   clip=[b["clip"], s["clip"]], clipReload=[b["clipReload"], s["clipReload"]],
                   volley=[round(volley(b), 3), round(volley(s), 3)], dps=[round(d0, 3), round(d1, 3)],
                   roundWeight=[b["roundWeight"], s["roundWeight"]], carriers=PLAN.get(wid, (0, 0, ""))[2])
        report.append(row)
        if abs(d1 - d0) > 0.002 * max(1.0, d0):
            bad.append(f"{wid}: DPS {d0:.3f} -> {d1:.3f}")
    for r in sorted(report, key=lambda r: r["weapon"]):
        print(f"{r['weapon']:38s} {r['method']:5s} barrels {r['barrels'][0]}->{r['barrels'][1]} dmg {r['damage'][0]:g}->{r['damage'][1]:g}"
              f" cd {r['cooldown'][0]:g}->{r['cooldown'][1]:g} burst {r['burst'][0]}->{r['burst'][1]} clip {r['clip'][0]}->{r['clip'][1]}"
              f" volley {r['volley'][0]:g}->{r['volley'][1]:g} DPS {r['dps'][0]:.2f}->{r['dps'][1]:.2f}")
    for c in changed_units:
        print("unit", c)
    for b in bad:
        print("DPS CHANGED:", b)
    print(f"{len(report)} lines changed, {len(bad)} DPS changes")
    if bad:
        sys.exit(1)
    if write:
        doc.save()
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump({"about": "Tools/balance/barrels_fix.py: every line it changed, before -> after (DPS = WeaponDef.SustainedDps)",
                       "weapons": sorted(report, key=lambda r: r["weapon"]), "units": changed_units}, fh, indent=1,
                      ensure_ascii=False)
        print("written")


if __name__ == "__main__":
    main()
