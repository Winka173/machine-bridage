#!/usr/bin/env python
"""Flight feel (05/10, lane B): raw -> family -> variant -> runtime effective projectile speed for every weapon.
Replicates Catalog.cs: weapon "inherits" chain (child over parent, the parent already family-resolved), then the weapon's
"weaponFamily" row on top (a family row wins over the weapon's own line; "" opts out). Variants (weaponVariantId) carry no
speed in the table. Cross-checked against Docs/export/game_snapshot.json balancePack.weaponFlight (the Unity runtime value).
Usage: python Tools/balance/flight_feel_audit.py [--csv out.csv]"""
import collections, json, sys, os
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
        # 5th element (06/10, validator v2): explicit "weaponFamily": "" opt-out *with* the weapon's own projectileSpeed
        # line -- the data shape a boss/ship weapon uses to intentionally diverge from what it would otherwise inherit.
        explicit_optout = w.get("weaponFamily") == ""
        info[w["id"]] = (w.get("projectileSpeed"), fid, fams.get(r.get("weaponFamily") or "", {}).get("projectileSpeed"),
                         w.get("inherits", ""), explicit_optout)
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

# ============================================================================================================
# Validator v2 (06/10, owner answer 3 to Docs/prompts/balance_final_answers_vi.md). Replaces the old flat
# TOO_FAST_FOR_CLASS / TOO_SLOW_FOR_CLASS / TOO_FAST_AT_GEAR_CAP / OWNER_EXCEPTION / ok vocabulary and the per-id
# EXCEPTIONS dict with three buckets and five reason codes. No projectile speed changes; no per-id exceptions: every
# "pass" below comes from the weapon's class and data shape (boss-prefix + explicit family opt-out), never its id.
# ============================================================================================================
BUCKETS = ("HARD_FAIL", "YELLOW_FEEL", "PASS_INTENTIONAL_SHORT_RANGE")  # "ok": no issue at all (kept for continuity)
REASON_CODES = ("CANONICAL_SHORT_RANGE", "INHERITANCE_MISMATCH", "TOO_FAST_FOR_CLASS", "TOO_SLOW_FOR_CLASS",
                "INTENTIONAL_BOSS_OVERRIDE")

# Owner's approximate hard-fail-fast floors (typical/max-range flight time, seconds; TACTICAL_MISSILE also needs its
# half-range floor, both conditions AND'd). Classes absent here have no new hard floor: they only get the old BANDS
# as a non-blocking YELLOW_FEEL / PASS_INTENTIONAL_SHORT_RANGE, same as before this refactor.
HARD_FLOOR_HALF = {"TACTICAL_MISSILE": 0.25}
HARD_FLOOR_MAX = {"TACTICAL_MISSILE": 0.45, "AIR_DEFENCE_SHORT": 0.18, "AIR_DEFENCE_MISSILE": 0.22,
                   "ROCKET_ARTILLERY": 0.45, "MORTAR": 0.60, "HOWITZER": 0.60}
HEAVY_240_FLOOR = 0.75      # 240 mm mortar/howitzer: its own higher floor (actual-arc time), not the plain MORTAR 0.60
HEAVY_240_BAND_HI = 2.2     # owner: "target band can extend to ~2.2 s" -- informational upper edge, not a fail ceiling
# Mortar/howitzer "actual-arc time": at the one elevation that is always correct for a weapon's own *listed* range at its
# own speed with no drag (45 deg, the classic max-range angle), only the horizontal speed component (v*cos(theta)) covers
# ground, so arc time = straight time / cos(45 deg) = straight time * sqrt(2). No gravity constant is needed at that angle
# (unlike CombatSystem.Bombs.cs BombGravity, which is tuned for a vertical bomb drop, not a mortar's lobbed arc).
ARC_FACTOR = 2 ** 0.5
# Existing file convention (see "boss_rockets"/"p26_"/"train_grad" membership checks in feel_class above): a naming
# pattern across the whole class of boss/special units, not a per-id list.
BOSS_PREFIXES = ("p26_", "pt14_", "nyx_", "scylla_", "boss_", "train_")

# Canonical master speeds (Docs/prompts/balance_master_final_spec.md secs 3-5), by weaponFamily id, for the ids the
# spec names unambiguously. balance.json already carries these numbers (an earlier prompt applied the spec); this
# dict is a regression guard only -- it flags INHERITANCE_MISMATCH if a future edit silently pushes one back (the
# spec's own example: "fix any inheritance that silently pushes [aircraft rockets] back to ~180 m/s").
CANONICAL_FAMILY_SPEED = {
    "agm_114_hellfire": 70, "9m133_kornet": 70, "9m317_buk": 120, "mim_104_patriot_pac_2": 130, "aim_9_sidewinder": 100,
    "bm_21_grad_122_mm": 80, "bm_21_grad_122_mm_2": 80, "m31_gmlrs_227_mm": 85, "m31_gmlrs_227_mm_mlrs": 85,
    "tos_1a_220_mm_thermobaric": 65, "apkws": 80, "nsm_oniks": 80, "2b11_120_mm": 45, "2b8_240_mm": 40,
    "2b8_240_mm_boss": 40, "hydra_70_mm": 95, "hydra_70_mm_jet": 100, "s_8_80_mm": 95, "s_8_80_mm_boat": 90,
}


def is_boss_override(i, explicit_optout, raw):
    """Structural boss-override signal (no per-id list): a boss/special-prefixed weapon that explicitly opts out of
    its family ("weaponFamily": "") *and* carries its own projectileSpeed line -- the data shape every boss/ship
    intentional exception in the spec (sec 3) and the boss mortar/howitzer/rocket rows are already built from."""
    return i.startswith(BOSS_PREFIXES) and explicit_optout and raw is not None


def classify(i, r, info5, sp, rng, cls, tmin, thalf, tmax):
    """One of HARD_FAIL / YELLOW_FEEL / "ok" / PASS_INTENTIONAL_SHORT_RANGE, with at most one reason code.
    Primary signal = typical/max-range flight time; half-range is secondary (only the ATGM AND rule uses it)."""
    raw, fid, fsp, inh, explicit_optout = info5
    is_240 = cls == "MORTAR" and ("240" in (r.get("weaponFamily") or "") or "240" in i)
    arc_tmax = tmax * ARC_FACTOR if tmax is not None and cls in ("MORTAR", "HOWITZER") else tmax

    fam_id = r.get("weaponFamily") or ""
    canon = CANONICAL_FAMILY_SPEED.get(fam_id)
    if canon is not None and sp and abs(sp - canon) > 0.5:
        return "HARD_FAIL", "INHERITANCE_MISMATCH"

    if is_boss_override(i, explicit_optout, raw):
        return "PASS_INTENTIONAL_SHORT_RANGE", "INTENTIONAL_BOSS_OVERRIDE"

    if tmax is None:
        return "ok", ""

    explicit_cls = cls in HARD_FLOOR_MAX
    # The arc-inflated time only ever helps a slow-lobbed shell clear the *fast* hard-fail floor; it is never used
    # against the upper (too-slow) side, where the straight range/speed time (the Sim's own flight model) stays the
    # one source of truth (owner: "a projectile fast only because of short range should not force a speed increase" --
    # the same reasoning means a long one should not be judged against an even longer, arc-inflated number).
    floor_check_t = arc_tmax if cls in ("MORTAR", "HOWITZER") else tmax

    hard = False
    if is_240:
        hard = floor_check_t is not None and floor_check_t < HEAVY_240_FLOOR
    elif cls == "TACTICAL_MISSILE":
        hard = (thalf is not None and tmax is not None and thalf < HARD_FLOOR_HALF["TACTICAL_MISSILE"]
                and tmax < HARD_FLOOR_MAX["TACTICAL_MISSILE"])
    elif cls in HARD_FLOOR_MAX:
        hard = floor_check_t is not None and floor_check_t < HARD_FLOOR_MAX[cls]
    if hard:
        return "HARD_FAIL", "TOO_FAST_FOR_CLASS"

    band = BANDS.get(cls)
    if not band:
        return "ok", ""
    lo, hi = band
    half_min = HALF_MIN.get(cls)

    if lo and tmax < lo:
        if explicit_cls:
            return "PASS_INTENTIONAL_SHORT_RANGE", "CANONICAL_SHORT_RANGE"
        return "YELLOW_FEEL", "TOO_FAST_FOR_CLASS"
    if not explicit_cls and half_min and thalf is not None and thalf < half_min:
        return "YELLOW_FEEL", "TOO_FAST_FOR_CLASS"
    if hi and tmax > hi:
        if is_240 and tmax <= HEAVY_240_BAND_HI:
            return "ok", ""
        return "YELLOW_FEEL", "TOO_SLOW_FOR_CLASS"
    return "ok", ""


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


def analyse(res, info, snap=None):
    out = {}
    for i, r in res.items():
        sp = r.get("projectileSpeed") or 0
        rng = r.get("range") or 0
        mn = r.get("minRange", 0) or 0
        cls = feel_class(i, r)
        dmin = mn if mn > 0 else rng * MIN_RANGE_SHARE
        t = lambda d, v: round(d / v, 3) if v else None
        cap = sp * (1 + GEAR_CAP)
        tmin, thalf, tmax = t(dmin, sp), t(rng / 2, sp), t(rng, sp)
        bucket, reason = classify(i, r, info[i], sp, rng, cls, tmin, thalf, tmax)
        is_240 = cls == "MORTAR" and ("240" in (r.get("weaponFamily") or "") or "240" in i)
        arc_tmax = round(tmax * ARC_FACTOR, 3) if tmax is not None and cls in ("MORTAR", "HOWITZER") else None
        raw, fid, fsp, inh, _optout = info[i]
        src = ("family %s" % r.get("weaponFamily") if r.get("weaponFamily") and fsp is not None else
               ("own line" if raw is not None and not inh else ("inherited from %s" % inh if inh else "own line")))
        if inh and raw is not None and not (r.get("weaponFamily") and fsp is not None): src = "own line (over %s)" % inh
        out[i] = dict(effectiveProjectileSpeedMps=sp, effectiveSpeedAtGearCapMps=round(cap, 1), flightTimeMinRangeS=tmin,
                      flightTimeHalfRangeS=thalf, flightTimeMaxRangeS=tmax, flightTimeMaxRangeAtGearCapS=t(rng, cap),
                      flightTimeMaxRangeArcS=arc_tmax if is_240 or cls in ("MORTAR", "HOWITZER") else None,
                      projectileFeelClass=cls, validationBucket=bucket, reasonCode=reason,
                      projectileSpeedWarning=bucket if bucket != "ok" else "ok",  # back-compat alias (exporter column)
                      speedInheritanceSource=src,
                      salvoSpacingM=round(sp * (r.get("burstInterval", 0.1) or 0), 1) if (r.get("burst", 1) or 1) > 1 and r.get("projectile") in ("Rocket", "Missile") else None)
    return out


def main():
    root = load()
    res, info = resolve_all(root)
    snap = {r["id"]: r for r in json.load(open(SNAP, encoding="utf-8"))["balancePack"]["weaponFlight"]}
    rows = []
    for i, r in res.items():
        raw, fid, fsp, inh, _optout = info[i]
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
    buckets = collections.Counter(a["validationBucket"] for a in an.values())
    print("validator v2 buckets:", dict(buckets))
    hard = {i: a for i, a in an.items() if a["validationBucket"] == "HARD_FAIL"}
    print("HARD_FAIL:", len(hard), sorted(hard))
    for i, a in sorted(hard.items()):
        print("  ", i, a["projectileFeelClass"], a["effectiveProjectileSpeedMps"], a["flightTimeHalfRangeS"],
              a["flightTimeMaxRangeS"], a["flightTimeMaxRangeArcS"], a["reasonCode"])
    yellow = {i: a for i, a in an.items() if a["validationBucket"] == "YELLOW_FEEL"}
    print("YELLOW_FEEL:", len(yellow), sorted(yellow))
    passi = {i: a for i, a in an.items() if a["validationBucket"] == "PASS_INTENTIONAL_SHORT_RANGE"}
    print("PASS_INTENTIONAL_SHORT_RANGE:", len(passi), sorted(passi))
    dead = [r for r in rows if r[1] is not None and r[3] is not None and r[1] != r[3]]
    print("own projectileSpeed line differs from its family row (dead value; the family wins):", len(dead), [r[0] for r in dead])
    mism = [r for r in rows if r[1] is not None and r[5] is not None and abs(r[1] - r[5]) / max(1, r[1]) > 0.25]
    print("raw vs runtime differ >25 pct:", len(mism))
    return rows


if __name__ == "__main__":
    main()
