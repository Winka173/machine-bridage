#!/usr/bin/env python
"""Flight feel (05/10, lane B): raw -> family -> variant -> runtime effective projectile speed for every weapon.
Replicates Catalog.cs: weapon "inherits" chain (child over parent, the parent already family-resolved), then the weapon's
"weaponFamily" row on top (a family row wins over the weapon's own line; "" opts out). Variants (weaponVariantId) carry no
speed in the table. Cross-checked against Docs/export/game_snapshot.json balancePack.weaponFlight (the Unity runtime value).
Usage: python Tools/balance/flight_feel_audit.py [--csv out.csv]"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "export"))
from core import jsonc

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BAL = os.path.join(ROOT, "Assets/MachineBrigade/Resources/Data/balance.json")
SNAP = os.path.join(ROOT, "Docs/export/game_snapshot.json")


def load():
    return jsonc.loads(open(BAL, encoding="utf-8").read())


def resolve_all(root):
    sr = root.get("secondRounds", {})
    fams = {f["id"]: f for f in root.get("weaponFamilies", []) + sr.get("families", [])}
    ws = root["weapons"] + sr.get("rounds", [])
    by = {w["id"]: w for w in ws if "id" in w}
    out, info = {}, {}

    def fin(w):
        fid = w.get("weaponFamily")
        if fid:
            f = fams[fid]
            m = dict(w)
            for k, v in f.items():
                if k not in ("id", "real"):
                    m[k] = v
            return m
        return w

    def res(w, d=0):
        if "inherits" not in w:
            return fin(w)
        m = dict(res(by[w["inherits"]], d + 1))
        m.update(w)
        return fin(m)

    for w in ws:
        if "id" not in w:
            continue
        r = res(w)
        fid = w.get("weaponFamily", "(inherited)" if "inherits" in w else "")
        out[w["id"]] = r
        info[w["id"]] = (w.get("projectileSpeed"), fid, fams.get(r.get("weaponFamily") or "", {}).get("projectileSpeed"), w.get("inherits", ""))
    return out, info


# ---- class-based effective flight-time validator (spec sections 22-24, 42-43) ----
# Bands = normal max-range flight time in seconds (lo, hi); None: not validated. Extension classes (marked *) are not in the
# spec's enum: they carry the spec's own final speeds at the game's ranges (aircraft rockets, naval direct, anti-ship, ballistic).
BANDS = {
    # Balance master final (06/10, spec 6): the final bands (max-range flight, seconds). AIR_DEFENCE_SHORT is the spec's
    # "short AAM / MANPADS"; AIR_DEFENCE_MISSILE its "medium / long SAM / AAM" (SHORAD 100 m/s and up).
    "DIRECT_FAST": (0.15, 0.45), "DIRECT_BULLET": None, "TACTICAL_MISSILE": (0.55, 1.00), "AIR_DEFENCE_SHORT": (0.30, 0.65),
    "AIR_DEFENCE_MISSILE": (0.40, 0.80), "ROCKET_ARTILLERY": (0.70, 1.60), "MORTAR": (0.90, 2.00), "HOWITZER": (0.90, 2.00),
    "CRUISE": (1.20, None), "DRONE": None, "BOMB": None, "AIRCRAFT_ROCKET": (0.25, 0.65), "NAVAL_DIRECT": (0.60, 2.00),
    "ANTI_SHIP_MISSILE": (0.80, 1.80), "BALLISTIC_MISSILE": (0.60, None), "BEAM_OR_MELEE": None,
}
# spec 6: a tactical / guided missile is flagged when its half-range flight is under ~0.30 s (unless exempted)
HALF_MIN = {"TACTICAL_MISSILE": 0.30, "AIR_DEFENCE_SHORT": 0.15, "AIR_DEFENCE_MISSILE": 0.20, "ANTI_SHIP_MISSILE": 0.40}
SHORT_AAM = ("stinger_atas", "stinger_post", "igla_v", "r60", "wvr_aam")
GEAR_CAP = 0.30     # GearCatalog.cs: ProjectileSpeed stat cap; GearSystem.cs applies it to the main weapon (arm 0) only
MIN_RANGE_SHARE = 0.25  # flight at the "minimum" distance of a weapon with no minRange: a quarter of its reach


def feel_class(i, r):
    pj, fam = r.get("projectile"), r.get("family")
    if pj == "Drone": return "DRONE"
    if pj == "Bomb" or fam == "bomb": return "BOMB"
    if pj == "Flame" or fam in ("laser", "melee", "special"): return "BEAM_OR_MELEE"
    if fam in ("cruise", "cruise_missile"): return "CRUISE"
    if fam == "ballistic": return "BALLISTIC_MISSILE"
    if fam == "aa_missile": return "AIR_DEFENCE_SHORT" if i in SHORT_AAM or r.get("inherits") in SHORT_AAM else "AIR_DEFENCE_MISSILE"
    if i == "anti_ship_missile" or r.get("weaponFamily") == "nsm_oniks" or "anti_ship_missile" in str(r.get("inherits", "")) or i in ("pt14_hp_nsm", "scylla_kh35"): return "ANTI_SHIP_MISSILE"
    if pj == "Missile" or fam == "atgm": return "TACTICAL_MISSILE"
    if pj == "Rocket":
        return "ROCKET_ARTILLERY" if (r.get("minRange", 0) or 0) > 0 or "boss_rockets" in i or "_rockets" in i and i.startswith("p26_") or "train_grad" in i else "AIRCRAFT_ROCKET"
    if fam == "mortar": return "MORTAR"
    if i.startswith(("naval_", "cruiser_", "leviathan_", "gun_100_river")) or "lev" in i or "_ty100" in i or i.startswith("pt14_hp_") or i.startswith("pt14_co_") or i == "nyx_ags_155":
        return "NAVAL_DIRECT"
    if fam == "howitzer" and ((r.get("minRange", 0) or 0) > 0 or r.get("lobs") or "coast" in i or "casemate" in i or "siege" in i): return "HOWITZER"
    if pj in (None, "Shell") and fam in ("tank_gun", "howitzer", "recoilless", "autocannon"): return "DIRECT_FAST" if fam != "autocannon" else "DIRECT_BULLET"
    if pj in ("Bullet", None): return "DIRECT_BULLET"
    return "DIRECT_FAST"


# owner-spec speeds that put a weapon outside the generic band at the game's range (spec 23: "audit targets, not hard caps")
EXCEPTIONS = {
    "pt14_co_spike": "NLOS Spike: range 80 at the spec's ATGM floor 75 m/s (1.07 s)",
}


def analyse(res, info, snap=None):
    out = {}
    for i, r in res.items():
        sp = r.get("projectileSpeed") or 0
        rng = r.get("range") or 0
        mn = r.get("minRange", 0) or 0
        cls = feel_class(i, r)
        band = BANDS[cls]
        dmin = mn if mn > 0 else rng * MIN_RANGE_SHARE
        t = lambda d, v: round(d / v, 3) if v else None
        cap = sp * (1 + GEAR_CAP)
        warn = []
        if band and sp and rng:
            lo, hi = band
            tmax, thalf = rng / sp, rng * 0.5 / sp
            if tmax < lo or thalf < HALF_MIN.get(cls, lo * 0.5): warn.append("TOO_FAST_FOR_CLASS")
            if hi and tmax > hi: warn.append("TOO_SLOW_FOR_CLASS")
            if rng / cap < lo * 0.75: warn.append("TOO_FAST_AT_GEAR_CAP")
        if warn and i in EXCEPTIONS: warn = ["OWNER_EXCEPTION"]
        raw, fid, fsp, inh = info[i]
        src = ("family %s" % r.get("weaponFamily") if r.get("weaponFamily") and fsp is not None else
               ("own line" if raw is not None and not inh else ("inherited from %s" % inh if inh else "own line")))
        if inh and raw is not None and not (r.get("weaponFamily") and fsp is not None): src = "own line (over %s)" % inh
        out[i] = dict(effectiveProjectileSpeedMps=sp, effectiveSpeedAtGearCapMps=round(cap, 1), flightTimeMinRangeS=t(dmin, sp),
                      flightTimeHalfRangeS=t(rng / 2, sp), flightTimeMaxRangeS=t(rng, sp), flightTimeMaxRangeAtGearCapS=t(rng, cap),
                      projectileFeelClass=cls, projectileSpeedWarning=";".join(warn) or "ok", speedInheritanceSource=src,
                      salvoSpacingM=round(sp * (r.get("burstInterval", 0.1) or 0), 1) if (r.get("burst", 1) or 1) > 1 and r.get("projectile") in ("Rocket", "Missile") else None)
    return out


def main():
    root = load()
    res, info = resolve_all(root)
    snap = {r["id"]: r for r in json.load(open(SNAP, encoding="utf-8"))["balancePack"]["weaponFlight"]}
    rows = []
    for i, r in res.items():
        raw, fid, fsp, inh = info[i]
        run = r.get("projectileSpeed")
        sn = snap.get(i, {}).get("speed")
        reason = ""
        if raw is None: reason = "no own line (inherits %s)" % inh
        elif fsp is not None and fsp != raw: reason = "family '%s' row overrides own line" % r.get("weaponFamily")
        elif run != raw: reason = "inherited from %s" % inh
        rows.append((i, raw, r.get("weaponFamily") or "", fsp, inh, run, sn, reason, r.get("range"), r.get("minRange", 0), r.get("projectile"), r.get("family")))
    if "--csv" in sys.argv:
        import csv
        with open(sys.argv[sys.argv.index("--csv") + 1], "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow("id raw family familySpeed inherits runtime exported reason range minRange projectile famRole".split()); w.writerows(rows)
    bad = [r for r in rows if r[6] is not None and r[5] != r[6]]
    print("weapons", len(rows), "weapons whose runtime speed now differs from the (stale) Unity snapshot:", len(bad))
    for r in bad[:20]: print("  ", r[:8])
    an = analyse(res, info)
    wn = {i: a for i, a in an.items() if a["projectileSpeedWarning"] != "ok"}
    print("validator warnings:", len(wn))
    for i, a in wn.items(): print("  ", i, a["projectileFeelClass"], a["effectiveProjectileSpeedMps"], a["flightTimeMinRangeS"], a["flightTimeHalfRangeS"], a["flightTimeMaxRangeS"], a["projectileSpeedWarning"])
    dead = [r for r in rows if r[1] is not None and r[3] is not None and r[1] != r[3]]
    print("own projectileSpeed line differs from its family row (dead value; the family wins):", len(dead), [r[0] for r in dead])
    mism = [r for r in rows if r[1] is not None and r[5] is not None and abs(r[1] - r[5]) / max(1, r[1]) > 0.25]
    print("raw vs runtime differ >25 pct:", len(mism))
    return rows


if __name__ == "__main__":
    main()
