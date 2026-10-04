"""Prompt 32 L2: the towers' rebuild prices from the data (static, theoretical; no sim).

    python Tools/balance/p32_tower_prices.py            # writes Docs/balance/p32_tower_prices.md
    python Tools/balance/p32_tower_prices.py --apply    # also writes "rebuildCp" (and the stat cuts) into balance.json

For each tower card of the roster and each of its branches:
1. effectiveHP = health / the median effective multiplier of four reference threats (kinetic direct fire, high explosive
   (a gun's HE or HE second round), shaped charge, artillery HE), each the median weapon of the card vehicles in the
   tower size's price band; multiplier = damage type x structure (thermobaric HE: 2.0 instead of 1.5, never on top) x
   penetration against the tower's front armour.
2. roleDPS = the tower's sustained damage a second on its role's target (air: aircraft; at: a heavy vehicle; light: a
   light vehicle; ground / multi: the mean of light and heavy), with the round its gun loads for that target (its second
   round's rule, as CombatSystem.RoundIndexFor; a branch carries elite-only rounds) and the switch to it once per 30 s
   engagement, every mount that can hit the target, the damage type, penetration and the weapon's armour bonuses.
3. equivalentCP = sqrt((effectiveHP / effectiveHP per CP of the role's vehicles) x (roleDPS / DPS per CP of them)),
   each "per CP" the median over the card vehicles of the role (same threats, same target).
4. x the standing factor by reach: <= 30 m 0.575, <= 50 m 0.625, beyond or indirect fire 0.725.
5. baseRebuildCP = ROUND_HALF_UP(equivalentCP x factor x 1.25), clamped small 3-6, medium 5-11, large 9-18.
6. Utility towers: interceptors (C-RAM, anti-drone) by coverage x interceptions a minute; protectors (shield, shelter) by
   damage prevented a minute; the CP relay by the CP it pays over an expected life; jammers, lighting, decoys,
   obstacles and mines at the size's floor. Their scales are anchored on the provisional table (DECISIONS).
REBALANCE_STATS: a small tower whose unclamped equivalentCP passes 8 gets outgoingDamageMult = (8 / eq)^2 (DPS down,
health kept), so its equivalentCP comes to 8. The steel fortress (HOLD): above 15, its health comes down (steps of 10)
until the price is 13-15.
"""
from __future__ import annotations

import math
import os
import statistics
import sys
from decimal import ROUND_HALF_UP, Decimal

sys.path.insert(0, os.path.dirname(__file__))
from jsonc_edit import Doc, loads  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
OUT = os.path.join(ROOT, "Docs", "balance", "p32_tower_prices.md")

CAPS = {"Small": (3, 6), "Medium": (5, 11), "Large": (9, 18)}
BANDS = {"Small": (3, 8), "Medium": (5, 12), "Large": (9, 20)}
ENGAGEMENT = 30.0
SMALL_EQ_CAP = 11.0  # owner 2026-10-02: cap 8 -> 11. Do not rerun --apply blindly: it reads the already-cut DPS and re-prices heavy_turret and atgm_tower.multi.
FORTRESS = "heavy_turret.bastion"

# Role of each card family (a branch takes its card's unless named): the target its DPS is read on and the vehicles it
# is compared with; "util:<kind>" for the utility formulas.
ROLE = {
    "guard_tower": "light", "mg_bunker": "light", "aa_turret": "air",
    "ew_tower": "util:floor", "cp_relay": "util:relay",
    "atgm_tower": "at", "gun_turret": "at", "gun_turret.auto": "light", "c_ram": "util:intercept",
    "rocket_turret": "ground", "laser_ad_station": "util:intercept",
    "heavy_turret": "at", "heavy_turret.coastal": "ground", "missile_battery": "air", "drone_hangar": "multi",
    "shield_tower": "util:protect",
}
# Utility anchors (the provisional table): the def whose value maps to the provisional price.
# Play-test 14: the troop shelter (the old protect anchor, 5) is deleted; the shield tower anchors at its provisional 9.
ANCHORS = {"intercept": ("c_ram", 5), "protect": ("shield_tower", 9)}
PROVISIONAL = {
    "aa_turret": 6, "aa_turret.flak": 6, "aa_turret.sam": 6, "mg_bunker": 6, "mg_bunker.twin": 6, "mg_bunker.flame": 6,
    "guard_tower": 4, "guard_tower.watch": 4, "guard_tower.nest": 4,
    "gun_turret.auto": 7, "laser_ad_station.laser": 7, "gun_turret.long": 6,
    "rocket_turret": 6, "rocket_turret.cluster": 6, "rocket_turret.guided": 6,
    "atgm_tower": 5, "atgm_tower.top": 5, "atgm_tower.multi": 5, "c_ram": 5, "c_ram.centurion": 5, "c_ram.dome": 5,
    FORTRESS: 17, "missile_battery": 12, "missile_battery.lrr": 11,
    "missile_battery.pac3": 9, "heavy_turret": 10, "heavy_turret.coastal": 11, "drone_hangar": 9, "drone_hangar.lancet": 9,
    "drone_hangar.swarm": 9, 
    "shield_tower": 9, "shield_tower.bulwark": 9, "shield_tower.ward": 9,
}
SMALL_UNARMED = 3
RELAY_LIFE = 120.0  # seconds an exposed CP relay is expected to stand (assumption, DECISIONS)
PROTECT_INCOMING = 60.0  # damage a second a protector's zone takes under attack (reference)
PROTECT_COVERED = 3  # towers or vehicles a protector covers (reference)


def rhu(x):
    return int(Decimal(str(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def load():
    d = loads(open(BALANCE, encoding="utf-8").read())
    raw_w = {w["id"]: w for w in d["weapons"] + d.get("secondRounds", {}).get("rounds", [])}
    raw_v = {v["id"]: v for v in d["vehicles"]}

    def resolve(raw):
        memo = {}

        def r(k, depth=0):
            if k in memo:
                return memo[k]
            e = raw[k]
            out = dict(e)
            if "inherits" in e and depth < 5 and e["inherits"] in raw:
                out = dict(r(e["inherits"], depth + 1))
                out.update(e)
            memo[k] = out
            return out
        return {k: r(k) for k in raw}

    W, V = resolve(raw_w), resolve(raw_v)
    rounds = {}
    for wid, w in W.items():
        if w.get("he") in W:
            rounds.setdefault(wid, []).append((W[w["he"]], {"light", "structure"}, False, 0.0))
        if w.get("air") in W:
            rounds.setdefault(wid, []).append((W[w["air"]], {"air"}, False, 0.0))
    for r in d.get("secondRounds", {}).get("rounds", []):
        rounds.setdefault(r["roundOf"], []).append((W[r["id"]], set(r.get("for", [])), bool(r.get("elite")), float(r.get("switch", 0))))
    return d, W, V, raw_v, rounds


def front(v):
    a = v.get("armour", 0)
    return a[0] if isinstance(a, list) else a


def layers(w):
    return {"All": (True, True), "Air": (True, False), "Ground": (False, True)}.get(w.get("targets", "Ground"), (False, True))


def can_target(w, flying):
    if w.get("interceptOnly"):
        return False
    a, g = layers(w)
    return a if flying else g


class Model:
    def __init__(self):
        self.d, self.W, self.V, self.raw_v, self.rounds = load()
        t = self.d["damageTable"]
        self.table = t
        self.pen_steps = t["penetration"]
        self.top_steps = t.get("topAttack") or self.pen_steps   # combat final 04/10: the top attack table
        self.thermo = t.get("thermobaric", 2.0)
        self.tough = self.d["toughness"]["vehicles"]
        self.cards = [v for v in self.V.values() if self.is_card_vehicle(v)]

    # -- damage --------------------------------------------------------------------------------------------------
    def type_of(self, w, kind):
        dt = w.get("damageType", "Kinetic")
        if kind == "Structure" and w.get("thermobaric") and dt == "HighExplosive":
            return self.thermo   # replaces high explosive's structure value (combat final 04/10)
        return self.table[dt][kind]

    def pen(self, pen, armour, overmatch=True, steps=None):
        """DamageTable.Penetration (steps None: the direct row) or DamageTable.TopAttack (steps: the top attack row)."""
        steps = steps or self.pen_steps
        last = len(steps) - 1
        step = 2.0 - (pen - armour)
        if not overmatch:
            step = max(1.0, step)
        if step <= 0:
            return steps[0]
        if step >= last:
            return steps[last]
        lo = int(math.floor(step))
        f = step - lo
        return steps[lo] + (steps[min(last, lo + 1)] - steps[lo]) * f

    def armour_mult(self, w, armour, kind, roof=False):
        """DamageTable.ArmourMultiplier: aircraft direct (no overmatch); topAttack the top attack row; else direct
        (no overmatch on the roof)."""
        p, top = float(w.get("pen", 0)), bool(w.get("topAttack"))
        if kind == "Air":
            return self.pen(p, armour, overmatch=False)
        if top:
            return self.pen(p, armour, steps=self.top_steps)
        return self.pen(p, armour, overmatch=not roof)

    def mult(self, w, armour, kind, armor_class=None):
        m = self.armour_mult(w, armour, kind) * self.type_of(w, kind)
        for b in w.get("bonuses", []) or []:
            if armor_class and b.get("armor") == armor_class:
                m *= float(b.get("mult", 1))
        return m

    @staticmethod
    def sustained(w):
        dmg = float(w.get("damage", 0) or 0)
        if dmg <= 0:
            return 0.0
        clip, burst = int(w.get("clip", 0)), int(w.get("burst", 1))
        cd, bi = float(w.get("cooldown", 1)), float(w.get("burstInterval", 0.1))
        cycle = (clip - 1) * cd + float(w.get("clipReload", 0)) if clip > 0 else cd + (burst - 1) * bi
        cycle = max(0.05, cycle)
        per = dmg * (clip if clip > 0 else burst)
        ammo = int(w.get("ammo", 0))
        if ammo > 0:
            reload = float(w.get("reload", 0)) or min(28.0, max(10.0, ammo * cd * 0.4))
            return per * ammo / (cycle * ammo + reload)
        return per / cycle

    @staticmethod
    def switch_seconds(gun, r_switch):
        if r_switch > 0:
            return r_switch
        reload = float(gun.get("clipReload", 0)) if int(gun.get("clip", 0)) > 0 else float(gun.get("cooldown", 1))
        return max(0.5, reload)

    def round_for(self, gun, target, branch):
        """The round the gun loads for a target ("air", "heavy", "light", "structure") and its switch time."""
        flying = target == "air"
        for r, use, elite, sw in self.rounds.get(gun["id"], []):
            if elite and not branch:
                continue
            if not can_target(r, flying):
                continue
            ok = ("air" in use or "any" in use) if flying else bool(
                {"ground", "any"} & use or (target == "heavy" and "armour" in use) or (target == "light" and "light" in use)
                or (target == "structure" and "structure" in use))
            if ok:
                return r, self.switch_seconds(gun, sw)
        return gun, 0.0

    def mounts(self, v):
        out = []
        if v.get("weapon") in self.W and v.get("weapon") != "none":
            out.append(self.W[v["weapon"]])
        for s in v.get("secondary", []) or []:
            if isinstance(s, dict) and s.get("weapon") in self.W:
                out.append(self.W[s["weapon"]])
        return out

    def dps_on(self, v, target, armour, branch=False):
        kind = "Air" if target == "air" else "Ground"
        cls = {"air": "Air", "heavy": "Heavy", "light": "Light"}[target]
        total = 0.0
        for gun in self.mounts(v):
            r, sw = self.round_for(gun, target, branch)
            if not can_target(r, target == "air"):
                continue
            prey = r.get("prey", "Any")
            if prey in ("Drones", "Rotors") and target != "air":
                continue
            if prey == "Light" and target != "light":
                continue
            dps = self.sustained(r) * self.mult(r, armour, kind, cls)
            if r is not gun and sw > 0:
                dps *= ENGAGEMENT / (ENGAGEMENT + sw)
            total += dps
        return total * float(v.get("outgoingDamageMult", 1))

    # -- vehicles ------------------------------------------------------------------------------------------------
    def is_card_vehicle(self, v):
        return (float(v.get("cp", 0) or 0) > 0 and not v.get("static") and not v.get("boss") and not v.get("elite")
                and not v.get("eliteOf") and not v.get("naval") and not v.get("navalOnly") and v.get("weapon") in self.W)

    def vclass(self, v):
        if v.get("class"):
            return v["class"]
        w = self.W[v["weapon"]]
        flying = v.get("flying") or v.get("move") in ("air", "heli", "plane")
        if flying:
            return "Plane" if v.get("fixedWing") else "Helicopter"
        if float(w.get("minRange", 0)) > 0:
            return "Artillery"
        if not can_target(w, False) or w.get("damageType") == "Fragmentation":
            return "AntiAir"
        if front(v) >= 3:
            return "Heavy" if float(v.get("hp", 0)) * self.tough >= 1400 else "Tank"
        return "Scout" if float(v.get("speed", 0)) >= 11 else "Light"

    def group(self, role):
        b = self.d["branches"]
        if role == "air":
            want = {"AntiAir"}
        elif role == "at":
            want = set(b["Armor"])
        elif role == "light":
            want = {"Light", "Scout"}
        elif role == "ground":
            want = set(b["Artillery"])
        else:
            want = set(b["Armor"]) | set(b["Light"]) | set(b["Artillery"])
        return [v for v in self.cards if self.vclass(v) in want]

    def target_armour(self, target):
        """Median front armour of the card vehicles a role's target stands for: aircraft; heavy (front 3+, the
        heavy ground class); light (front 2 or less on the ground)."""
        b = self.d["branches"]
        if target == "air":
            pool = [v for v in self.cards if self.vclass(v) in set(b["Air"])]
        elif target == "heavy":
            pool = [v for v in self.cards if self.vclass(v) not in set(b["Air"]) and front(v) >= 3]
        else:
            pool = [v for v in self.cards if self.vclass(v) not in set(b["Air"]) and front(v) <= 2]
        return statistics.median(front(v) for v in pool)

    # -- threats -------------------------------------------------------------------------------------------------
    def threats(self, size):
        lo, hi = BANDS[size]
        band = [v for v in self.cards if lo <= float(v["cp"]) <= hi and self.vclass(v) not in ("Plane", "Helicopter")]
        pools = {"kinetic": [], "he": [], "shaped": [], "artillery": []}
        for v in band:
            w = self.W[v["weapon"]]
            if w.get("melee") or w.get("laid") or not can_target(w, False) or float(w.get("damage", 0) or 0) <= 0:
                continue
            dt, indirect = w.get("damageType"), self.vclass(v) == "Artillery" or float(w.get("minRange", 0)) > 0
            if indirect:
                if dt == "HighExplosive":
                    pools["artillery"].append(w)
                continue
            if dt == "Kinetic":
                pools["kinetic"].append(w)
                for r, use, _, _ in self.rounds.get(w["id"], []):
                    if r.get("damageType") == "HighExplosive":
                        pools["he"].append(r)
            elif dt == "HighExplosive":
                pools["he"].append(w)
            elif dt == "ShapedCharge" and w.get("family") != "cruise_missile":
                pools["shaped"].append(w)
        picks = {}
        for k, pool in pools.items():
            pool = sorted({w["id"]: w for w in pool}.values(), key=lambda w: (float(w.get("pen", 0)), w["id"]))
            picks[k] = pool[len(pool) // 2] if pool else None
        return picks

    def eff_hp(self, v, picks, kind):
        ms = [self.mult(w, front(v), kind) for w in picks.values() if w]
        m = statistics.median(ms) if ms else 1.0
        return float(v.get("hp", 0)) * self.tough / max(1e-6, m)

    # -- towers --------------------------------------------------------------------------------------------------
    def role_of(self, tid):
        if tid in ROLE:
            return ROLE[tid]
        card = self.V[tid].get("branchOf")
        return ROLE.get(card, "multi")

    def reach_factor(self, v):
        ws = self.mounts(v)
        if not ws:
            return 0.575, 0.0
        r = max(float(w.get("range", 0)) for w in ws)
        indirect = any(float(w.get("minRange", 0)) > 0 or w.get("projectile") in ("Rocket",) and float(w.get("minRange", 0)) > 0 for w in ws)
        if indirect or r > 50:
            return 0.725, r
        return (0.575 if r <= 30 else 0.625), r

    def role_dps(self, v, role, branch):
        if role == "air":
            return self.dps_on(v, "air", self.target_armour("air"), branch)
        if role == "at":
            return self.dps_on(v, "heavy", self.target_armour("heavy"), branch)
        if role == "light":
            return self.dps_on(v, "light", self.target_armour("light"), branch)
        return 0.5 * (self.dps_on(v, "light", self.target_armour("light"), branch) + self.dps_on(v, "heavy", self.target_armour("heavy"), branch))

    def equivalent(self, tid):
        v = self.V[tid]
        size = v["fort"]["size"]
        role = self.role_of(tid)
        picks = self.threats(size)
        hp = self.eff_hp(v, picks, "Structure")
        branch = v.get("branchOf") is not None
        dps = self.role_dps(v, role, branch)
        group = self.group(role) or self.cards
        hp_cp = statistics.median(self.eff_hp(g, picks, "Ground") / float(g["cp"]) for g in group)
        dps_cp = statistics.median(max(1e-6, self.role_dps(g, role, False)) / float(g["cp"]) for g in group)
        eq = math.sqrt(max(0.0, (hp / hp_cp) * (dps / dps_cp)))
        return eq, hp, dps, hp_cp, dps_cp, picks, len(group)

    def utility_value(self, kind, v):
        if kind == "intercept":
            aps = v.get("aps")
            if aps:
                per_min = float(aps.get("charges", 1)) * 60.0 / max(0.1, float(aps.get("reload", 0)) or float(aps.get("recharge", 1)) * float(aps.get("charges", 1)) or 1.0)
                per_min = min(per_min, 120.0)
                return (float(aps.get("radius", 30)) / 35.0) ** 2 * per_min
            w = self.W.get(v.get("weapon"))
            if w and float(w.get("damage", 0)) > 0:
                return (float(w.get("range", 15)) / 35.0) ** 2 * min(120.0, 60.0 / max(0.1, float(w.get("cooldown", 1))))
            return 0.0
        if kind == "protect":
            if v.get("dome"):
                dome = v["dome"]
                return min(PROTECT_INCOMING, float(dome["hp"]) / float(dome.get("recharge", 30))) * 60.0 * (float(dome["radius"]) / 25.0) ** 2
            if v.get("wards"):
                wd = v["wards"]
                return min(PROTECT_INCOMING, PROTECT_COVERED * float(wd["hp"]) / max(6.0, float(wd.get("recharge", 6)) * 5)) * 60.0
            if v.get("shelter"):
                sh = v["shelter"]
                return PROTECT_INCOMING * float(sh.get("cut", 0.5)) * 60.0 * (float(sh["radius"]) / 15.0) ** 2 * 0.5
        return 0.0

    def price(self, tid):
        v = self.V[tid]
        size = v["fort"]["size"]
        lo, hi = CAPS[size]
        role = self.role_of(tid)
        note = ""
        if role.startswith("util:"):
            kind = role[5:]
            if kind == "floor":
                return dict(tid=tid, size=size, role=role, eq=None, factor=None, raw=lo, price=lo, note="size floor")
            if kind == "relay":
                relay = v.get("relay") or {}
                cp = float(relay.get("income", 0)) * float(self.d["economy"].get("income", 1)) * RELAY_LIFE
                p = max(lo, min(hi, rhu(cp)))
                return dict(tid=tid, size=size, role=role, eq=cp, factor=None, raw=cp, price=p, note=f"{cp:.1f} CP in {RELAY_LIFE:.0f} s")
            anchor, anchor_price = ANCHORS[kind]
            base_val = self.utility_value(kind, self.V[anchor])
            val = self.utility_value(kind, v)
            raw = anchor_price * math.sqrt(val / base_val) if base_val > 0 else lo
            p = max(lo, min(hi, rhu(raw)))
            return dict(tid=tid, size=size, role=role, eq=val, factor=None, raw=raw, price=p, note=f"value {val:.0f} vs {anchor} {base_val:.0f}")
        eq, hp, dps, hp_cp, dps_cp, picks, n = self.equivalent(tid)
        factor, reach = self.reach_factor(v)
        raw = eq * factor * 1.25
        p = max(lo, min(hi, rhu(raw)))
        return dict(tid=tid, size=size, role=role, eq=eq, factor=factor, raw=raw, price=p, hp=hp, dps=dps, hp_cp=hp_cp,
                    dps_cp=dps_cp, reach=reach, n=n, picks=picks, note=note)


def defs_of_roster(m):
    out = []
    for card in m.d["base"]["roster"]:
        out.append(card)
        out += m.raw_v[card].get("branches", [])
    return out


def main():
    apply = "--apply" in sys.argv
    m = Model()
    rows = [m.price(t) for t in defs_of_roster(m)]
    # REBALANCE_STATS: small towers past eq 8, DPS cut to bring eq to 8.
    cuts, fortress = {}, None
    for r in rows:
        if r["size"] == "Small" and r.get("eq") and r["factor"] and r["eq"] > SMALL_EQ_CAP:
            cuts[r["tid"]] = round((SMALL_EQ_CAP / r["eq"]) ** 2, 4)
    for r in rows:
        if r["tid"] == FORTRESS:
            fortress = dict(r)
            if r["price"] > 15:
                v = m.V[FORTRESS]
                sec = list(v.get("secondary", []))
                v["secondary"] = sec[:-1] if len(sec) > 1 else sec
                steps = [("one roof MG fewer", m.price(FORTRESS))]
                hp0, floor_hp = float(v["hp"]), float(m.V["heavy_turret"]["hp"])
                hp = hp0
                p = steps[-1][1]
                while p["price"] > 15 and hp - 10 >= floor_hp:
                    hp -= 10
                    v["hp"] = hp
                    p = m.price(FORTRESS)
                steps.append((f"health {hp0:.0f} -> {hp:.0f} (not under the base turret's {floor_hp:.0f})", p))
                fortress.update(steps=steps, hp_from=hp0, hp_to=hp, reached=p["price"] <= 15)
                # Restore: the cut is applied only if it reaches 13-15 (else HOLD for the owner).
                v["secondary"] = sec
                v["hp"] = hp0
    after = {}
    for tid, k in cuts.items():
        m.V[tid]["outgoingDamageMult"] = float(m.V[tid].get("outgoingDamageMult", 1)) * k
        after[tid] = m.price(tid)
    # Report.
    L = ["# Prompt 32 L2: tower rebuild prices (Tools/balance/p32_tower_prices.py)", "",
         "A static read of balance.json (no sim). Columns: equivalentCP (unclamped), the standing factor, the raw price",
         "(equivalentCP x factor x 1.25), the clamped baseRebuildCP, the provisional price of the prompt and the gap.",
         "Utility rows: their value and the anchor (see the script's docstring; DECISIONS \"Prompt 32 L0/L1/L2\").", "",
         "| def | size | role | eq CP | factor | raw | price | provisional | gap | note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        prov = PROVISIONAL.get(r["tid"], SMALL_UNARMED if r["size"] == "Small" and r["role"].startswith("util") else None)
        gap = "" if prov is None else f"{r['price'] - prov:+d}"
        eq = "" if r["eq"] is None or r["role"].startswith("util") else f"{r['eq']:.2f}"
        fac = "" if not r["factor"] else f"{r['factor']:.3f}"
        flag = " REBALANCE_STATS" if r["tid"] in cuts else ""
        note = r["note"] or (f"HP {r['hp']:.0f} eff, DPS {r['dps']:.1f}, reach {r['reach']:.0f} m, vs {r['n']} vehicles" if "hp" in r else "")
        L.append(f"| `{r['tid']}` | {r['size'][0]} | {r['role']} | {eq} | {fac} | {r['raw']:.2f} | {r['price']} | {'' if prov is None else prov} | {gap} | {note}{flag} |")
    L += ["", "## Reference threats by size band (median weapon of the card vehicles in the band, by penetration)", ""]
    for size in ("Small", "Medium", "Large"):
        picks = m.threats(size)
        L.append(f"- {size} (cp {BANDS[size][0]}-{BANDS[size][1]}): " + ", ".join(f"{k} `{w['id'] if w else '-'}`" for k, w in picks.items()))
    L += ["", "Reference targets (median front armour): air " + str(m.target_armour("air")) + ", heavy " + str(m.target_armour("heavy")) +
          ", light " + str(m.target_armour("light")) + ".", "", "## REBALANCE_STATS (small towers past equivalentCP 8)", ""]
    if cuts:
        L += ["| def | eq before | outgoingDamageMult | eq after | price after |", "|---|---|---|---|---|"]
        for tid, k in cuts.items():
            b = next(r for r in rows if r["tid"] == tid)
            L.append(f"| `{tid}` | {b['eq']:.2f} | {k} | {after[tid]['eq']:.2f} | {after[tid]['price']} |")
    else:
        L.append("None.")
    L += ["", "## Steel fortress (HOLD)", ""]
    if fortress:
        if "steps" in fortress:
            L.append(f"Formula price {fortress['price']} (raw {fortress['raw']:.2f}, > 15). Tried in order:")
            for what, p in fortress["steps"]:
                L.append(f"- {what}: raw {p['raw']:.2f}, price {p['price']}")
            L.append("Reached 13-15: " + ("yes, applied." if fortress["reached"] else
                     "no. Not applied: the cut that would reach 15 leaves the steel fortress weaker than the base heavy turret; HOLD stays with the owner."))
        else:
            L.append(f"Formula price {fortress['price']} (raw {fortress['raw']:.2f}): 15 or less, no change; HOLD stays the owner's call.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("\n".join(L))
    if apply:
        doc = Doc(BALANCE)
        final = {r["tid"]: (after[r["tid"]]["price"] if r["tid"] in after else r["price"]) for r in rows}
        if fortress and fortress.get("reached"):
            final[FORTRESS] = fortress["steps"][-1][1]["price"]
            doc.edit("vehicles", FORTRESS, lambda e: (e.set("hp", int(fortress["hp_to"])),
                                                      e.set("secondary", m.raw_v[FORTRESS]["secondary"][:-1])))
        for tid, p in final.items():
            doc.edit("vehicles", tid, lambda e, p=p: e.set("rebuildCp", p))
        for tid, k in cuts.items():
            doc.edit("vehicles", tid, lambda e, k=m.V[tid]["outgoingDamageMult"]: e.set("outgoingDamageMult", round(k, 4)))
        # A card's cut is inherited by its branches: a branch not cut itself keeps 1.
        for tid in final:
            card = m.raw_v[tid].get("branchOf")
            if card in cuts and tid not in cuts and "outgoingDamageMult" not in m.raw_v[tid]:
                doc.edit("vehicles", tid, lambda e: e.set("outgoingDamageMult", 1))
        doc.save()
        print("applied")


if __name__ == "__main__":
    main()
