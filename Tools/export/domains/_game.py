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
DIRECT_ROW = [1.2, 1.0, 0.85, 0.65, 0.4, 0.15, 0.08]   # SimTunables DamageTable.DefaultPenetration (combat final 04/10)
TOP_ROW = [1.15, 1.1, 0.95, 0.75, 0.5, 0.25, 0.12]     # SimTunables DamageTable.DefaultTopAttack (combat final 04/10)
SPLASH_ROW = [1.10, 1.08, 1.05, 1.00, 0.85, 0.65, 0.45, 0.25, 0.0]   # DamageTable.DefaultSplash (splash 04/10)
OVER_ROW = [1.00, 0.95, 0.85, 0.75]                                  # DamageTable.DefaultOver (overpenetration 04/10)
STEPS = 7


def _expand(row: list) -> list[float]:
    """DamageTable.cs Expand: 7 values; an old 6-value row repeats its last step, a 5-value row has no overmatch step."""
    skip = 1 if len(row) == 5 else 0
    return [float(row[min(max(k - skip, 0), len(row) - 1)]) for k in range(STEPS)]


def pen_row(table: dict) -> list[float]:
    """DamageTable.cs constructor: the direct penetration row (damageTable.penetration), 7 steps +2 .. -4."""
    return _expand(list(table.get("penetration") or DIRECT_ROW))


def top_row(table: dict) -> list[float]:
    """DamageTable.cs constructor: the top attack row (damageTable.topAttack), 7 steps +2 .. -4 against the roof."""
    return _expand(list(table.get("topAttack") or TOP_ROW))


def _read(row: list[float], p: float, armour: float, overmatch: bool) -> float:
    """DamageTable.cs Read: whole levels read the row, a part level lies between its neighbours."""
    last = STEPS - 1
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


def penetration(table: dict, p: float, armour: float, overmatch: bool = True) -> float:
    """DamageTable.cs Penetration: the direct table (no overmatch on a roof struck without top attack, on aircraft)."""
    return _read(pen_row(table), p, armour, overmatch)


def top_attack(table: dict, p: float, roof: float) -> float:
    """DamageTable.cs TopAttack: the top attack table against the roof's level, no cap."""
    return _read(top_row(table), p, roof, True)


def armour_mult(table: dict, p: float, armour: float, kind: str, roof: bool, top: bool) -> float:
    """DamageTable.cs ArmourMultiplier: aircraft -> direct, no overmatch; top attack (ground, structure) -> top attack
    table only; else direct (no overmatch on the roof). One table, never both."""
    if kind == "Air":
        return penetration(table, p, armour, False)
    if top:
        return top_attack(table, p, armour)
    return penetration(table, p, armour, not roof)


def weapon_armour_mult(table: dict, w: dict, armour: float, kind: str, from_above: bool = False) -> float:
    """armour_mult for a weapon (its topAttack flag, its roof by Armour.cs StrikesTop)."""
    return armour_mult(table, pen(w), armour, kind, from_above or strikes_top(w), bool(w.get("topAttack")))


def type_of(table: dict, w: dict, kind: str) -> float:
    """DamageTable.cs TypeOf: the damage type's multiplier on Ground / Air / Structure; the thermobaric tag replaces
    high explosive's structure value (damageTable.thermobaric, not multiplied with it)."""
    dt = w.get("damageType")
    if w.get("thermobaric") and kind == "Structure" and dt == "HighExplosive":
        return float(table.get("thermobaric", 2.0))
    return float((table.get(dt) or {}).get(kind, 0.0))


def splash_row(table: dict) -> list[float]:
    """DamageTable.cs: the splash falloff row (damageTable.splashFalloff), 9 steps: centre, core 0-25 / 25-50 / 50-100 %,
    edge 0-25 / 25-50 / 50-75 / 75-100 %, outside."""
    return [float(x) for x in (table.get("splashFalloff") or SPLASH_ROW)]


def over_row(table: dict) -> list[float]:
    """DamageTable.cs: the kinetic overpenetration row (damageTable.overpenetration): +2 or less, +3, +4, +5 or more."""
    return [float(x) for x in (table.get("overpenetration") or OVER_ROW)]


def splash_step_at(distance: float, core: float, edge: float) -> int:
    """DamageTable.cs SplashStepAt: r = 0 the centre; coreProgress r / core up to 0.25, 0.50, 1.00 (inclusive); then
    edgeProgress (r - core) / (edge - core) up to 0.25, 0.50, 0.75, under 1.00; else outside. No division by zero."""
    if distance != distance:
        return 8
    distance = max(0.0, distance)
    core = core if core > 0 else 0.0
    edge = edge if edge > 0 else 0.0
    if not max(core, edge) > 0:
        return 8
    if distance == 0:
        return 0
    if distance <= core:
        p = distance / core
        return 1 if p <= 0.25 else 2 if p <= 0.5 else 3
    if edge > core and distance < edge:
        p = (distance - core) / (edge - core)
        return 4 if p <= 0.25 else 5 if p <= 0.5 else 6 if p <= 0.75 else 7
    return 8


def splash_falloff(table: dict, distance: float, core: float, edge: float) -> float:
    """DamageTable.cs SplashFalloff (a blast's damage only, never a direct hit's)."""
    return splash_row(table)[splash_step_at(distance, core, edge)]


def overpenetrates(w: dict) -> bool:
    """DamageTable.cs Overpenetrates: a Kinetic weapon that is not a top attack."""
    return w.get("damageType") == "Kinetic" and not w.get("topAttack")


def overpenetration(table: dict, p: float, armour: float) -> float:
    """DamageTable.cs Overpenetration: by penetration - armour, +2 or less / +3 / +4 / +5 or more; a part level between."""
    row = over_row(table)
    diff = p - armour
    if diff != diff or diff <= 2:
        return row[0]
    if diff >= 2 + len(row) - 1:
        return row[-1]
    x = diff - 2
    lo = int(math.floor(x))
    return row[lo] + (row[min(len(row) - 1, lo + 1)] - row[lo]) * (x - lo)


def over_mult(table: dict, w: dict, p: float, armour: float) -> float:
    """The overpenetration factor of a weapon's direct hit (1 unless overpenetrates)."""
    return overpenetration(table, p, armour) if overpenetrates(w) else 1.0


def effective(table: dict, w: dict, armour: float, kind: str, from_above: bool = False) -> float:
    """DamageTable.cs Effective(weapon, armour, kind, fromAbove): the armour multiplier (one table) x a direct Kinetic
    round's overpenetration (04/10) x the damage type."""
    return weapon_armour_mult(table, w, armour, kind, from_above) * over_mult(table, w, pen(w), armour) * type_of(table, w, kind)


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


# ---------------------------------------------------------------------------------------------------------- 05: economy
def f32(x: float) -> float:
    """A C# float value as a double (the 32-bit rounding of a literal like 1.16f)."""
    import struct
    return struct.unpack("f", struct.pack("f", float(x)))[0]


def round_half_up(x: float) -> int:
    """Sim/Core/SimMath.cs RoundHalfUp(double): away from zero at .5."""
    from decimal import ROUND_HALF_UP, Decimal
    return int(Decimal(repr(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def start_cp(cp: float, scale: float, listed: bool) -> float:
    """Sim/Content/OpeningRules.cs StartCp(mode, cp): cp x startCp.scale rounded half up where the mode is listed (cp > 0,
    scale != 1); else cp. The scale is a float (Math.Max(0.1f, s.Float("scale"))) widened to double."""
    s = max(0.1, f32(scale))
    if listed and cp > 0 and s != 1.0:
        return float(round_half_up(cp * s))
    return float(cp)


def earning(income: float, bonus: float, scale: float) -> float:
    """Sim/Economy/EconomySystem.cs TeamEconomy.Earning with upkeep 1, catch-up 1 and no commander:
    (Income + Bonus x IncomeScale), Income = _income x IncomeScale; IncomeScale = economy.income (SimWorld.EnableEconomy)
    times every ScaleIncome factor (ModeSession.Create: BuyProfile.For(difficulty).Income; ConquestSession: 1.18)."""
    return income * scale + bonus * scale
