"""Column names from source keys (snake_case) and the unit each key carries (spec 2.1: the unit sits in the column name).

UNIT_BY_KEY: the key's unit suffix; a key already ending in its unit (caliberMm, warheadKg) keeps its name.
UNITLESS: keys known to be counts, levels, shares, multipliers, flags or names (no unit). Any other numeric key goes to
Don_vi_chua_ro (file 00) so a person can say what it measures.
"""
from __future__ import annotations

import re

SECONDS = {
    "cooldown", "burstInterval", "clipReload", "reload", "dropDelay", "delay", "duration", "warn", "recharge",
    "rearmTime", "attackHold", "stillAfter", "every", "halt", "regenDelay", "domeSeconds", "skillCooldown",
    "salvoMergeSeconds", "fadeIn", "intro", "strikeWindow", "timeLimit", "starTime", "seconds", "holdSeconds",
    "surviveSeconds", "flareRecharge", "launchSeconds", "dropWarn", "showdownCutoff", "floorT4", "floor406",
    "floorT5", "grace", "mainSeconds", "miniSeconds", "convoyInterval", "fleeDelay",
    "dive", "stun", "exposed", "earlySeconds",
    # the bomb-run fix: weapons[*].stick
    "interval", "fallTime", "straightTime", "bayOpen",
}
METRES = {
    "range", "minRange", "splash", "edge", "radius", "vision", "length", "width", "height", "altitude", "ceiling",
    "groundRange", "minReach", "groundMinReach", "orbitRadius", "reach", "leash", "repairReach", "enemyRadius", "flareOffset",
    "proximityFuze", "airReach", "dropRadius", "standoff", "blast", "pad", "depth", "core", "spacing", "stillVision",
    "metresWide", "metresHigh", "area", "x", "y", "z", "distance", "gap", "offset", "sightRange",
    # the bomb-run fix: weapons[*].stick
    "lead", "jitterAcross", "jitterAlong", "safety", "exit",
}
METRES_PER_SECOND = {"speed", "projectileSpeed", "escapeSpeed", "transitSpeed", "climb", "descend", "releaseSpeed"}
DEGREES_PER_SECOND = {"turnRate", "turretTurnRate"}
DEGREES = {"heading", "turretArc", "arc", "angle", "pitch", "yaw"}

UNIT_BY_KEY: dict[str, tuple[str, str]] = {}
for _k in SECONDS:
    UNIT_BY_KEY[_k] = ("s", "s")
for _k in METRES:
    UNIT_BY_KEY[_k] = ("m", "m")
for _k in METRES_PER_SECOND:
    UNIT_BY_KEY[_k] = ("m_s", "m/s")
for _k in DEGREES_PER_SECOND:
    UNIT_BY_KEY[_k] = ("deg_s", "deg/s")
for _k in DEGREES:
    UNIT_BY_KEY[_k] = ("deg", "deg")
# keys that name their unit already
OWN_UNIT = {"caliberMm": "mm", "warheadKg": "kg", "powerKw": "kW", "energyMj": "MJ", "hp": "hp", "cp": "CP",
            "rebuildCp": "CP", "enemyCp": "CP", "playerCp": "CP", "baseCp": "CP"}

UNITLESS = {
    # counts
    "count", "charges", "burst", "bombs", "minTargets", "barrels", "clip", "ammo", "load", "cap", "caps", "slots", "points", "stock", "units",
    "shells", "rockets", "missiles", "drones", "lines", "small", "medium", "large", "utility", "level", "number",
    "segments", "campLines", "fortressLines", "maxShown", "maxPerSide", "flareCharges", "bountyCap", "escortCap",
    "bossRushCut", "bossRushMin", "mounts", "guns", "act", "chapter", "reward", "coins", "xp", "prints", "salvo",
    "flares", "rank", "index", "version", "tier", "pen", "armour", "armor", "airCap", "airCapFree", "order",
    "priority", "week", "waves", "squads", "killsNeeded", "convoyCount", "convoyNeeded", "protectNeeded", "hqLevel",
    "reinforcements", "playerCap", "starLosses", "value", "bounty", "helperBounty", "marks", "stops", "at",
    # shares, multipliers, chances, levels
    "mult", "scale", "damageScale", "overlap", "hpScale", "costScale", "share", "chance", "outgoingDamageMult", "weaponDamage",
    "stillCamo", "damage", "fireRate", "airDamage", "strikeTaken", "strikeCap", "strikeOver", "partsShare",
    "powerRatio", "otherShare", "budget", "blueprintChance", "flareDecoyChance", "reachScale", "leadCap", "thermobaric",
    "penetration", "Ground", "Air", "Structure", "durability", "breakerMultiplier", "rubbleSlow", "hqRescue",
    "aaHit", "bossHp", "bossDamage", "spotBonus", "spotSpread", "repair", "flareResist", "impactScale",
    "projectileScale", "regen", "dome", "airScale", "aiAirShare", "income", "playerIncome", "enemyIncome", "health",
    "fallbackHealth", "fleeAt", "targetHealth", "bigAttackScale", "from", "to", "jamResist", "exposedTaken", "toughness",
    "captureRate", "boost", "weight", "factor", "ratio", "slow", "amount", "threshold", "epic", "legendary",
    "epic2", "legendary2", "strength", "top", "top2", "penaltyTop", "minRarity", "rearm", "airRepair", "airRearm",
    "supply", "revealBase", "mainShare",
}


def snake(key: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", str(key))
    s = re.sub(r"(?<=[A-Z])([A-Z][a-z])", r"_\1", s)
    s = re.sub(r"[^0-9A-Za-z]+", "_", s).strip("_").lower()
    return s or "x"


def column_for(key: str, prefix: str = "") -> tuple[str, str]:
    """(column name, unit label) for a source key under a column prefix."""
    base = snake(key)
    if key in OWN_UNIT:
        return prefix + base, OWN_UNIT[key]
    unit = UNIT_BY_KEY.get(key)
    if unit:
        suffix, label = unit
        name = base if base.endswith("_" + suffix) else f"{base}_{suffix}"
        return prefix + name, label
    return prefix + base, ""


def known_unitless(key: str) -> bool:
    return key in UNITLESS or str(key).isdigit()
