"""Python ports of the game's own formulas (C#) that layer B of files 01-04 checks its Excel formulas against.

Each function names the C# it ports. The C# works in float (32 bit); these ports work in double, so a value may differ
from the game's in the 7th significant digit (the 1e-6 test compares formula with port, both double).
Records are the resolved balance.json records (_balance.resolved_weapons / resolved_vehicles / boss_built).
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------------------------------------- weapons
GUIDED = ("Missile", "Drone")


def f(w: dict, key: str, default=0.0) -> float:
    v = w.get(key, default)
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else float(default)


def i(w: dict, key: str, default=0) -> int:
    v = w.get(key, default)
    return int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else int(default)


def projectile(w) -> str:
    return w.get("projectile") or "Shell"


def default_pen(w: dict) -> int:
    """Sim/Content/Armour.cs DefaultPenetration(WeaponDef): by family and size (data "size"), else by damage type."""
    size, fam, dt = f(w, "size"), w.get("family"), w.get("damageType")
    if fam == "mg":
        return 1 if size >= 12 else 0
    if fam == "autocannon":
        if dt == "Fragmentation":
            return 2 if size >= 30 else 1
        return 3 if size >= 57 else 2
    table = {
        "grenade": lambda: 2, "tank_gun": lambda: 4 if size >= 120 else 3 if size >= 76 else 2,
        "howitzer": lambda: 4 if size >= 200 else 3 if size >= 150 else 2, "mortar": lambda: 4 if size >= 200 else 2,
        "rocket": lambda: 3 if size >= 200 else 2, "atgm": lambda: 4 if size >= 26 else 3,
        "aa_missile": lambda: 3 if size >= 20 else 2, "bomb": lambda: 4 if size >= 900 else 3 if size >= 500 else 2,
        "cruise": lambda: 3, "ballistic": lambda: 4,
        "drone": lambda: (4 if size >= 3 else 3) if dt == "ShapedCharge" else 3,
        "flame": lambda: 2 if size >= 3 else 1, "laser": lambda: 3 if size >= 150 else 2, "railgun": lambda: 4,
        "melee": lambda: 3, "special": lambda: 4,
    }
    if fam in table:
        return table[fam]()
    return {"ShapedCharge": 4, "Energy": 2}.get(dt, 1)


def pen(w: dict) -> int:
    """Definitions.cs WeaponDef.Penetration: data "pen" (0-5), else DefaultPenetration."""
    return max(0, min(5, i(w, "pen"))) if "pen" in w else default_pen(w)


def indirect(w) -> bool:
    """Definitions.cs WeaponDef.Indirect: minRange > 0, lofted, a bomb or a drone."""
    return f(w, "minRange") > 0 or bool(w.get("lofted")) or projectile(w) in ("Bomb", "Drone")


def strikes_top(w) -> bool:
    """Armour.cs StrikesTop: topAttack or Indirect."""
    return bool(w.get("topAttack")) or indirect(w)


def can_target(w, flying: bool) -> bool:
    """Definitions.cs WeaponDef.CanTarget: not interceptOnly and the target layer in "targets" (Ground / Air / All)."""
    t = w.get("targets") or "Ground"
    layers = {"Ground": (False, True), "Air": (True, False), "All": (True, True)}.get(t, (False, False))
    return not w.get("interceptOnly") and (layers[0] if flying else layers[1])


def rounds_per_pull(w) -> int:
    """WeaponDef.P34.cs RoundsPerPull: every barrel of a SIMULTANEOUS gun, else 1."""
    return max(1, i(w, "barrels", 1)) if w.get("salvoMode") == "SIMULTANEOUS" else 1


def rounds_per_cycle(w) -> int:
    """Definitions.cs RoundsPerCycle: the magazine, else burst x rounds a pull."""
    clip = i(w, "clip")
    return clip if clip > 0 else i(w, "burst", 1) * rounds_per_pull(w)


def cycle_seconds(w) -> float:
    """Definitions.cs CycleSeconds."""
    clip = i(w, "clip")
    if clip > 0:
        return (clip - 1) * f(w, "cooldown") + f(w, "clipReload")
    return f(w, "cooldown") + (i(w, "burst", 1) - 1) * f(w, "burstInterval", 0.1)


def magazine_reload(w) -> float:
    """Definitions.cs MagazineReload: reload, else clamp(ammo x cooldown x 0.4, 10, 28)."""
    r = f(w, "reload")
    return r if r > 0 else min(28.0, max(10.0, i(w, "ammo") * f(w, "cooldown") * 0.4))


def volley(w) -> float:
    """Combat/FirePower.cs Volley: damage x max(1, RoundsPerCycle)."""
    return f(w, "damage") * max(1, rounds_per_cycle(w))


def on_paper(w, load: int = 0, rearm: float = 0.0) -> float:
    """Combat/FirePower.cs OnPaper (load: carrier.LoadOf(w), rearm: carrier.RearmTime)."""
    dmg = f(w, "damage")
    if dmg <= 0:
        return 0.0
    cycle = max(0.05, cycle_seconds(w))
    per = volley(w)
    if load > 0:
        pulls = max(1.0, math.ceil(load / max(1, i(w, "burst", 1))))
        return dmg * load / (cycle * pulls + max(0.0, rearm))
    ammo = i(w, "ammo")
    if ammo > 0:
        return per * ammo / (cycle * ammo + magazine_reload(w))
    return per / cycle


def sustained(w, carrier: dict | None = None, ground: bool = True) -> float:
    """Combat/FirePower.cs Sustained (ground) / SustainedAir (ground False) with a carrier's LoadOf, RearmTime,
    WeaponDamage (not on a laid weapon, not at aircraft) and OutgoingDamageMult."""
    if carrier is None:
        return on_paper(w)
    v = on_paper(w, carrier["load"], carrier["rearm"])
    if ground and not w.get("laid"):
        v *= carrier["weapon_damage"]
    return v * carrier["outgoing"]


# ---------------------------------------------------------------------------------------------------------- damage table
def pen_row(table: dict) -> list[float]:
    """DamageTable.cs constructor: 6 values, a 5-value row padded at the front (no overmatch step)."""
    row = list(table.get("penetration") or [1.2, 1.0, 0.85, 0.55, 0.25, 0.1])
    skip = 6 - len(row)
    return [float(row[max(0, k - skip)]) for k in range(6)]


def penetration(table: dict, p: float, armour: float, overmatch: bool = True) -> float:
    """DamageTable.cs Penetration."""
    row = pen_row(table)
    last = 5
    step = 2.0 - (p - armour)
    if not overmatch:
        step = max(1.0, step)
    if step <= 0:
        return row[0]
    if step >= last:
        return row[last]
    lo = int(math.floor(step))
    t = step - lo
    return row[lo] + (row[min(last, lo + 1)] - row[lo]) * t


def type_of(table: dict, w: dict, kind: str) -> float:
    """DamageTable.cs TypeOf: the damage type's multiplier on Ground / Air / Structure (thermobaric HE on structures)."""
    dt = w.get("damageType")
    v = float((table.get(dt) or {}).get(kind, 0.0))
    if w.get("thermobaric") and kind == "Structure" and dt == "HighExplosive":
        v = max(float(table.get("thermobaric", 2.0)), v)
    return v


def effective(table: dict, w: dict, armour: float, kind: str, from_above: bool = False) -> float:
    """DamageTable.cs Effective(weapon, armour, kind, fromAbove): penetration (overmatch unless roof or aircraft) x type."""
    roof = from_above or strikes_top(w)
    return penetration(table, pen(w), armour, not roof and kind != "Air") * type_of(table, w, kind)


# ---------------------------------------------------------------------------------------------------------- warnings
def warns(w: dict, tier: int, rules: dict) -> bool:
    """Content/FixRules.cs WarningRules.Warns."""
    guided_rocket = projectile(w) == "Rocket" and (bool(w.get("guided")) or w.get("weaponVariantId") == "guided")
    if projectile(w) in GUIDED or guided_rocket or w.get("beam") or w.get("laid") or f(w, "splash") <= 0:
        return False
    if tier >= 0:
        return tier >= 4
    size = f(w, "size")
    return {"Shell": size >= f(rules, "gunMinMm", 203), "Bomb": size >= f(rules, "bombMinKg", 400),
            "Rocket": size >= f(rules, "rocketMinMm", 300)}.get(projectile(w), False)


def warn_seconds(w: dict, tier: int, rules: dict) -> float:
    """WeaponDef.P34.cs WarnSeconds -> FixRules.cs WarningRules.Seconds (Parse: escapeSpeed >= 0.1, cap >= 0.5)."""
    t = 4 if tier < 0 and warns(w, tier, rules) else tier
    if t < 4:
        return 0.0
    floor = f(rules, "floor406", 3.5) if w.get("weaponFamilyId") == "cal_406" else f(rules, "floorT5", 4) if t >= 5 \
        else f(rules, "floorT4", 2.5)
    esc = max(0.1, f(rules, "escapeSpeed", 4.5))
    cap = max(0.5, f(rules, "cap", 6))
    return min(cap, max(floor, f(rules, "base", 0.5) + max(0.0, f(w, "splash")) / max(0.1, esc)))


def boss_edge(w: dict) -> float:
    """Content/Catalog.cs WithEdge (a boss's blast weapons): edge = min(MaxEdge 20, 2 x core) unless the weapon already has
    an edge, a core under 2 m, a beam, flak (autocannon fragmentation, not interceptOnly) or air-only targets."""
    edge, core = f(w, "edge"), f(w, "splash")
    flak = w.get("family") == "autocannon" and w.get("damageType") == "Fragmentation" and not w.get("interceptOnly")
    if edge > 0 or core < 2 or w.get("beam") or flak or (w.get("targets") or "Ground") == "Air":
        return edge
    e = min(20.0, core * 2)
    return e if e > core else edge


# ---------------------------------------------------------------------------------------------------------- carriers
def default_rearm(v: dict, main: dict | None) -> float:
    """Content/Catalog.cs DefaultRearm."""
    if not v.get("flying"):
        return 0.0
    if not v.get("fixedWing") or v.get("drone"):
        return 8.5
    if v.get("interceptor"):
        return 11.0
    return 21.0 if main is not None and projectile(main) == "Bomb" else 14.0


def carrier(v: dict, w: dict | None, boss: bool = False, damage_scale_rank: float | None = None) -> dict:
    """The carrier fields FirePower reads: LoadOf (Definitions.cs: flying and not a boss: loads[weapon] else weapon.load),
    RearmTime (data or DefaultRearm), WeaponDamage and OutgoingDamageMult (Catalog.Extra.cs ParseExtras clamps)."""
    load = 0
    if v.get("flying") and not boss and w is not None:
        loads = v.get("loads") if isinstance(v.get("loads"), dict) else {}
        load = int(loads[w["id"]]) if w.get("id") in loads else i(w, "load")
    rearm = f(v, "rearmTime") if "rearmTime" in v else default_rearm(v, w)
    return {"load": load, "rearm": rearm,
            "weapon_damage": min(10.0, max(0.1, f(v, "weaponDamage", 1.0))),
            "outgoing": min(10.0, max(0.1, f(v, "outgoingDamageMult", 1.0)))}


def boss_damage_scale(b: dict, ranks: dict) -> float:
    """BossTemplates.cs Rank (a boss without its own damageScale takes its rank's) + Catalog.Extra.cs ParseExtras
    (clamp 0.1-5) / FinishExtras (none: 1 for a boss)."""
    ds = b.get("damageScale")
    if ds is None:
        ds = ((ranks or {}).get(b.get("rank", "main")) or {}).get("damageScale")
    return min(5.0, max(0.1, float(ds))) if isinstance(ds, (int, float)) else 1.0


# ---------------------------------------------------------------------------------------------------------- base
def rebuild_cost(tower: dict, rebuild: dict) -> int:
    """Content/BaseRules.cs RebuildCost: the tower's rebuildCp (TowerRoster.cs: max(0, int)), else its size's cp."""
    own = max(0, i(tower, "rebuildCp"))
    if own > 0:
        return own
    size = ((tower.get("fort") or {}) if isinstance(tower.get("fort"), dict) else {}).get("size", "Small")
    return i((rebuild or {}).get(str(size).lower()) or {}, "cp")


def opening_eligible(v: dict) -> bool:
    """Modes/OpeningSquads.cs Eligible: baseCP > 0, not static, not a boss, not an elite, no fort, not a ship."""
    return (i(v, "cp") > 0 and not v.get("static") and not v.get("boss") and not v.get("elite") and "fort" not in v
            and "naval" not in v)


def opening_cheapest(role, vehicles: dict):
    """Modes/OpeningSquads.cs Pick, one role with an empty deck: the cheapest eligible card (baseCP, then id) among the
    role's ids, or among every card of at most maxCp. Returns (id, cp) or None."""
    best = None
    if isinstance(role, dict):
        cap = max(0, i(role, "maxCp"))
        pool = [k for k in vehicles] if cap > 0 else []
    else:
        cap, pool = 0, list(role)
    for vid in pool:
        v = vehicles.get(vid)
        if v is None or not opening_eligible(v):
            continue
        cp = i(v, "cp")
        if cap > 0 and cp > cap:
            continue
        if best is None or cp < best[1] or (cp == best[1] and vid < best[0]):
            best = (vid, cp)
    return best
