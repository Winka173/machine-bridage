"""Prompt 32 L4: the three HQ types compared on paper (static, theoretical; no sim).

    python Tools/balance/p32_hq_types.py            # writes Docs/balance/p32_hq_types.md
    python Tools/balance/p32_hq_types.py --apply    # also writes the fitted coefficients into balance.json (base.hqTypes)

"Defensive value a minute of the base under attack", in CP: damage dealt + damage prevented (each over the health a CP
of the vehicles it lands on buys) + the baseCP of the temporary troops. The prompt's targets by HQ level:
1: 4-5, 2: 5-6, 3: 6-7, 4: 7-8, 5: 8-9. A type off a band has its coefficient table refitted (--apply) and the change
goes into DECISIONS "Prompt 32 L4/L5/L6/L8".

Fortress: the added gun (the HQ def's mounts past the plain HQ's) at its level's scale (damage and cadence each the
root: DPS x scale), on its role's target (ground: the mean of a light and a heavy vehicle; anti-air: an aircraft), busy
DUTY of the minute; plus the barrage skill (three rounds x damage x scale, VICTIMS vehicles in each blast, once a
cooldown).
Garrison: the squad's baseCP turned out a minute of attack over an ATTACK_MINUTES attack: the stock it starts with (two,
as the alive cap allows), then one squad an interval; the alarm turns the stock out at once (no more troops).
Shield: rounds the dome takes (INCOMING eligible rounds a minute, in salvos of SALVO: its interceptors over the salvo,
at most all), each the median eligible round's damage; towers mending (the level's towers, their median health, the
level's rate, mending REGEN_DUTY of the minute); the emergency dome (its share of the HQ's health, ABSORB_USE of it used,
once a cooldown).
"""
from __future__ import annotations

import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(__file__))
from jsonc_edit import Doc  # noqa: E402
from p32_tower_prices import BALANCE, ROOT, Model, front  # noqa: E402

OUT = os.path.join(ROOT, "Docs", "balance", "p32_hq_types.md")
TARGETS = {1: (4, 5), 2: (5, 6), 3: (6, 7), 4: (7, 8), 5: (8, 9)}

# Assumptions (DECISIONS): a minute of the base under attack.
DUTY = 0.5            # share of the minute the Fortress gun has a target of its kind in reach
VICTIMS = 1.5         # vehicles one barrage round's blast catches
ATTACK_MINUTES = 2.0  # how long an attack on the base lasts (the garrison's stock spread over it)
INCOMING = 12.0       # rounds a minute aimed into the base that a C-RAM may take (missiles, drones, rockets, shells)
SALVO = 6.0           # rounds arriving together (a salvo, a drone wave)
REGEN_DUTY = 0.5      # share of the minute a hurt tower goes unhit long enough to mend
ABSORB_USE = 0.75     # share of the emergency dome actually used before it lapses


class HqModel(Model):
    def __init__(self):
        super().__init__()
        self.base = self.d["base"]
        self.rules = self.base["hqTypes"]
        g = self.group("multi") or self.cards
        self.hp_cp_ground = statistics.median(float(v["hp"]) * self.tough / float(v["cp"]) for v in g)
        air = [v for v in self.cards if self.vclass(v) in set(self.d["branches"]["Air"])]
        self.hp_cp_air = statistics.median(float(v["hp"]) * self.tough / float(v["cp"]) for v in air) if air else self.hp_cp_ground

    def level_table(self, key, sub, level):
        t = self.rules[key][sub]
        return float(t[min(level, len(t)) - 1]) if isinstance(t, list) else float(t)

    # -- Fortress ----------------------------------------------------------------------------------------------------
    def fortress(self, level, branch="ground"):
        f = self.level_table("fortress", "airScale" if branch == "air" and "airScale" in self.rules["fortress"] else "scale", level)
        hq = self.V[self.rules["fortress"][branch]]
        plain = self.V[self.base["hq"]]
        extra = dict(hq)
        extra["weapon"] = "none"
        extra["secondary"] = (hq.get("secondary") or [])[len(plain.get("secondary") or []):]
        extra["outgoingDamageMult"] = 1
        if branch == "air":
            dps = self.dps_on(extra, "air", self.target_armour("air"))
            hp_cp = self.hp_cp_air
        else:
            dps = 0.5 * (self.dps_on(extra, "light", self.target_armour("light")) + self.dps_on(extra, "heavy", self.target_armour("heavy")))
            hp_cp = self.hp_cp_ground
        gun = dps * f * 60.0 * DUTY / hp_cp
        b = next(s for s in self.d["supports"] if s["id"] == self.rules["fortress"]["barrage"])
        mult = 0.5 * (self.pen(float(b.get("pen", 0)), self.target_armour("light"), overmatch=False) +
                      self.pen(float(b.get("pen", 0)), self.target_armour("heavy"), overmatch=False)) * self.table[b.get("damageType", "HighExplosive")]["Ground"]
        per_use = float(b["count"]) * float(b["damage"]) * f * mult * VICTIMS
        barrage = per_use * 60.0 / float(self.rules["skillCooldown"]) / self.hp_cp_ground
        return gun + barrage, dict(scale=f, dps=dps, gun=gun, barrage=barrage)

    # -- Garrison ----------------------------------------------------------------------------------------------------
    def garrison(self, level):
        g = self.rules["garrison"]
        every = self.level_table("garrison", "every", level)
        squad = g["squads"][min(level, len(g["squads"])) - 1]["units"]
        cp = sum(float(self.raw_v[u]["cp"]) for u in squad)
        cap = float(g["caps"][min(level, len(g["caps"])) - 1])
        stocked = min(float(g.get("stock", 2)) * cp, max(cp, math.floor(cap / cp) * cp))
        later = cp * ATTACK_MINUTES * 60.0 / every
        value = (stocked + later) / ATTACK_MINUTES
        return value, dict(squad="+".join(squad), squad_cp=cp, every=every, cap=cap)

    # -- Shield ------------------------------------------------------------------------------------------------------
    def shield(self, level):
        s = self.rules["shield"]
        k = self.level_table("shield", "scale", level)
        hq = self.V[s["hq"]]
        charges = max(1, min(int(hq["aps"]["charges"]), round(float(s.get("charges", 4)) * k)))
        taken = min(1.0, charges / SALVO)
        rounds = []
        for v in self.cards:
            w = self.W[v["weapon"]]
            if w.get("damageType") == "Energy" or w.get("beam"):
                continue
            guided = w.get("guided") or w.get("projectile") in ("Missile", "Drone")
            rocket = w.get("projectile") == "Rocket"
            shell = w.get("projectile") == "Shell" and float(w.get("minRange", 0)) > 0
            if guided or rocket or shell:
                rounds.append(float(w.get("damage", 0)) * (float(hq["aps"].get("shells", 0.3)) if shell else 1.0))
        dmg = statistics.median(r for r in rounds if r > 0) if rounds else 200.0
        prevented = INCOMING * taken * dmg / self.hp_cp_ground
        lv = self.base["levels"][level - 1]
        towers = lv["small"] + lv["medium"] + lv["large"]
        tower_hp = statistics.median(float(self.V[t]["hp"]) * self.tough for t in self.base["roster"] if "hp" in self.V[t])
        regen = self.level_table("shield", "regen", level)
        mend = towers * tower_hp * regen * 60.0 * REGEN_DUTY / self.hp_cp_ground
        dome_share = self.level_table("shield", "dome", level)
        hq_hp = float(self.V[self.base["hq"]]["hp"]) * self.tough
        dome = dome_share * hq_hp * ABSORB_USE * 60.0 / float(self.rules["skillCooldown"]) / self.hp_cp_ground
        return prevented + mend + dome, dict(scale=k, charges=charges, taken=taken, round=dmg, prevented=prevented, mend=mend, dome=dome)


def band(level, value):
    lo, hi = TARGETS[level]
    return "in" if lo <= value <= hi else ("low" if value < lo else "high")


def fit(values, base_table, kind):
    """A coefficient table that brings each level's value to its band's middle, the value taken as proportional to it
    (the Fortress's and the Shield's scale), rounded to 0.05."""
    out = []
    for level in range(1, 6):
        mid = sum(TARGETS[level]) / 2.0
        v = values[level - 1]
        c = float(base_table[level - 1]) * (mid / v if v > 0 else 1.0)
        out.append(round(round(c / 0.05) * 0.05, 2))
    return out


def run(m):
    rows = {"fortress": [], "fortress_air": [], "garrison": [], "shield": []}
    for level in range(1, 6):
        rows["fortress"].append(m.fortress(level, "ground"))
        rows["fortress_air"].append(m.fortress(level, "air"))
        rows["garrison"].append(m.garrison(level))
        rows["shield"].append(m.shield(level))
    return rows


def table(rows):
    out = ["| HQ level | target | Fortress (ground) | Fortress (anti-air) | Garrison | Shield |", "|---|---|---|---|---|---|"]
    for level in range(1, 6):
        cells = [f"{rows[k][level - 1][0]:.1f} ({band(level, rows[k][level - 1][0])})" for k in ("fortress", "fortress_air", "garrison", "shield")]
        out.append(f"| {level} | {TARGETS[level][0]}-{TARGETS[level][1]} | " + " | ".join(cells) + " |")
    return out


def main():
    apply = "--apply" in sys.argv
    m = HqModel()
    before = run(m)
    lines = ["# Prompt 32 L4: the HQ types compared (static)", "",
             "Written by `Tools/balance/p32_hq_types.py` from balance.json (no sim). Value = CP-equivalent a minute of the base",
             "under attack (damage dealt + damage prevented over the health a CP buys, + the temporary troops' baseCP).",
             f"Health a CP buys: ground {m.hp_cp_ground:.0f}, aircraft {m.hp_cp_air:.0f} (median card vehicle, health x toughness).",
             f"Assumptions: gun busy {DUTY:.0%} of the minute; {VICTIMS} vehicles a barrage blast; a {ATTACK_MINUTES:.0f}-minute attack;",
             f"{INCOMING:.0f} C-RAM-eligible rounds a minute in salvos of {SALVO:.0f}; towers mend {REGEN_DUTY:.0%} of the minute;",
             f"{ABSORB_USE:.0%} of the emergency dome used.", "", "## With the data's coefficients", ""]
    lines += table(before)
    lines += ["", "Parts (level: Fortress ground gun + barrage | anti-air gun + barrage | Garrison squad, CP, interval | Shield "
              "intercepts + mending + dome):", ""]
    for level in range(1, 6):
        f, fa, g, s = (before[k][level - 1][1] for k in ("fortress", "fortress_air", "garrison", "shield"))
        lines.append(f"- HQ {level}: Fortress x{f['scale']} gun {f['gun']:.1f} + barrage {f['barrage']:.1f} | AA gun {fa['gun']:.1f} + {fa['barrage']:.1f} | "
                     f"Garrison {g['squad']} ({g['squad_cp']:.0f} CP, every {g['every']:.0f} s, cap {g['cap']:.0f}) | Shield x{s['scale']} "
                     f"{s['charges']} interceptors ({s['taken']:.0%} of a salvo) {s['prevented']:.1f} + mending {s['mend']:.1f} + dome {s['dome']:.1f}")
    rules = m.rules
    fitted = {}
    off = lambda k: any(band(level, before[k][level - 1][0]) != "in" for level in range(1, 6))

    def refit(tables, evaluate, digits, inverse=False):
        """Per HQ level, one factor on every table named (the prompt's progression kept within a level), found by a few
        proportional steps on the model itself (the Shield's interceptors are whole numbers)."""
        base = {t: [float(x) for x in rules[t[0]][t[1]]] for t in tables}
        for t in tables:
            rules[t[0]][t[1]] = list(base[t])
        for level in range(1, 6):
            mid = sum(TARGETS[level]) / 2.0
            c = 1.0
            for _ in range(8):
                for t in tables:
                    rules[t[0]][t[1]][level - 1] = round(base[t][level - 1] * c, digits[t])
                v = evaluate(level)
                if v <= 0 or abs(v - mid) < 0.05:
                    break
                c *= (v / mid) if inverse else (mid / v)
        for t in tables:
            fitted[f"{t[0]}.{t[1]}"] = rules[t[0]][t[1]]

    if off("fortress"):
        refit([("fortress", "scale")], lambda L: m.fortress(L, "ground")[0], {("fortress", "scale"): 2})
    if off("fortress_air"):
        # The anti-air branch gets its own table (from the prompt's), its fragmentation rounds being worth more on aircraft.
        rules["fortress"]["airScale"] = list(rules["fortress"].get("airScale") or [0.5, 0.65, 0.8, 1.0, 1.2])
        refit([("fortress", "airScale")], lambda L: m.fortress(L, "air")[0], {("fortress", "airScale"): 2})
    if off("shield"):
        refit([("shield", "scale"), ("shield", "regen"), ("shield", "dome")], lambda L: m.shield(L)[0],
              {("shield", "scale"): 2, ("shield", "regen"): 5, ("shield", "dome"): 3})
    if off("garrison"):
        rules["garrison"]["every"] = [float(rules["garrison"]["every"])] * 5 if not isinstance(rules["garrison"]["every"], list) else rules["garrison"]["every"]
        refit([("garrison", "every")], lambda L: m.garrison(L)[0], {("garrison", "every"): -1}, inverse=True)
    if fitted:
        lines += ["", "## Refitted coefficients (per HQ level, each type's tables by one factor)", ""]
        for k, v in fitted.items():
            lines.append(f"- `base.hqTypes.{k}`: {v}")
        after = run(m)
        lines += ["", "## With the refitted coefficients", ""]
        lines += table(after)
    else:
        lines += ["", "Every type is in its band: no coefficient changed."]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if apply and fitted:
        text = open(BALANCE, encoding="utf-8").read()
        for k, v in fitted.items():
            t, sub = k.split(".")
            text = replace_in_block(text, t, sub, v)
        open(BALANCE, "w", encoding="utf-8").write(text)
        print("applied:", ", ".join(fitted))


def replace_in_block(text, block, key, value):
    """Replaces "key": [...] / number inside base.hqTypes.<block> (one line each, comments kept)."""
    i = text.index('"hqTypes": {')
    j = text.index(f'"{block}": {{', i)
    k = text.index(f'"{key}": ', j)
    start = k + len(f'"{key}": ')
    if text[start] == "[":
        end = text.index("]", start) + 1
    else:
        end = start
        while text[end] not in ",}\n":
            end += 1
    v = "[" + ", ".join(str(x) for x in value) + "]" if isinstance(value, list) else str(value)
    return text[:start] + v + text[end:]


if __name__ == "__main__":
    main()
