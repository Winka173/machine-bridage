"""Prompt 26, pass 1 (A and B): the bosses' health, armour, phases and weapons in balance.json (DECISIONS 26AB).

Run from this folder: `python p26_ab.py` (a second run changes nothing: every value is written whole). No measurement is
made: the DPS it solves for is the sheet's formula on paper (steps_c.boss_dps), against armour 3, before the rank scale.

  * A1-A3 health: the prompt's table (main 22,000 / 35,000 / 63,000 / 100,000 / 150,000 at chapters 1 / 3 / 6 / 9 / 12, minis
    9,000 / 14,000 / 25,000 / 38,000 / 57,000), straight lines between, to the nearest 50, over the bosses' toughness (0.85)
    and a mini's rank share (0.55) as 25C did.
  * A5 armour (main front 5, side 3, rear 2; a mini's front at most 4) and the phase marks (40 / 35 / 25, a mini 55 / 45).
  * B1-B2 target DPS by chapter and the mix main 45 / secondary 25 / direct 20 / close 10 %: each main boss's mounts are given
    a role and a weapon (new "p26_*" weapons with the prompt's starting numbers); each role's damage is then scaled so the
    role's share of the boss's DPS comes out as the mix says (an empty role's share goes to the others).
  * Minis and the batch D bosses: `weaponDamage` is solved so their ordinary DPS is the chapter's target (a mini 65 %).
  * B6 the super weapons' numbers, cycle (45-50 s) and warning (3-4 s).
"""
from __future__ import annotations

import copy
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import steps_c as S  # noqa: E402
from jsonc_edit import Doc, fmt  # noqa: E402

PATH = os.path.join(HERE, "..", "..", "Assets", "MachineBrigade", "Resources", "Data", "balance.json")

TOUGH = 0.85
MINI_SHARE = 0.55

# ------------------------------------------------------------------------------------------------ chapters and targets

ANCHORS_MAIN = [(1, 22000), (3, 35000), (6, 63000), (9, 100000), (12, 150000)]
ANCHORS_MINI = [(1, 9000), (3, 14000), (6, 25000), (9, 38000), (12, 57000)]
DPS_MAIN = [600, 650, 700, 800, 850, 1000, 1100, 1200, 1300, 1400, 1500, 1600]

# The chapter each boss is met at first (the interludes 13, 14, 15 sit after chapters 3, 6, 9).
MAINS = {"fortress_bastion": 1, "behemoth": 2, "mobile_fortress": 3, "leviathan": 4, "drone_mothership": 5, "moloch": 6,
         "nuke_train": 7, "kronos": 8, "typhon": 9, "command_airship": 10, "daedalus": 11, "silver_bug": 12,
         "monster": 8, "kraken": 9, "garuda": 10, "hyperion": 12}
MINIS = {"bastion_mk0": 1, "behemoth_inferno": 2, "mega_gunship": 3, "fenrir": 3, "behemoth_mk0": 3.5, "behemoth_tempest": 4,
         "armored_train": 4, "scylla": 4, "nyx": 4, "locust": 5, "fortress_hive": 5, "stymphalos": 5, "landing_hovercraft": 6,
         "behemoth_mk2": 6, "cerberus": 6, "supreme_command": 7, "ixion": 8, "earth_borer": 8, "caspian": 9, "hydra": 9,
         "morrigan": 9.5, "sky_fortress": 10, "icarus_mk0": 10, "argus": 10, "rail_supergun": 11}


def cd(cycle, burst, interval):
    """The cooldown that makes a burst of `burst` rounds `interval` apart a cycle of `cycle` seconds."""
    return round(max(0.05, cycle - (burst - 1) * interval), 3)


def line(anchors, x):
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def round50(v):
    return int(round(v / 50.0)) * 50


def shown_hp(vid):
    if vid in MAINS:
        return round50(line(ANCHORS_MAIN, MAINS[vid]))
    return round50(line(ANCHORS_MINI, MINIS[vid]))


def data_hp(vid):
    """What the data holds: the shown health over the toughness, and over a mini's share."""
    if vid in MAINS:
        return round50(shown_hp(vid) / TOUGH)
    return round50(shown_hp(vid) / (TOUGH * MINI_SHARE))


def target_dps(vid):
    if vid in MAINS:
        return line([(i + 1, t) for i, t in enumerate(DPS_MAIN)], MAINS[vid])
    return 0.65 * line([(i + 1, t) for i, t in enumerate(DPS_MAIN)], MINIS[vid])


# ------------------------------------------------------------------------------------------------ the main bosses' sets

SHARES = {"main": 0.45, "sec": 0.25, "direct": 0.20, "close": 0.10}

# Each weapon: (inherits, fields). "weaponFamily": "" keeps it out of its parent's family (the family would set its blast).
NOFAM = {"weaponFamily": ""}
WEAPONS = {
    # Bastion
    "b155": ("casemate_155", {**NOFAM, "real": "M284 155 mm (Bastion)", "damage": 540, "cooldown": 2, "burst": 1, "splash": 8.5, "edge": 17, "pen": 4}),
    "b240": ("boss_mortar", {**NOFAM, "real": "2B8 240 mm", "damage": 750, "cooldown": 5, "splash": 10, "edge": 20}),
    "b100": ("gun_120mm", {**NOFAM, "real": "D-10 100 mm", "size": 100, "damage": 240, "cooldown": 4, "pen": 5, "splash": 0, "range": 36}),
    # Behemoth
    "be152": ("gun_behemoth", {"real": "2A65 152 mm", "damage": 590, "cooldown": 2, "burst": 1, "splash": 8.5, "edge": 17}),
    "be_rockets": ("boss_rockets", {"real": "BM-21 Grad 122 mm (dorsal)", "damage": 160, "burst": 8, "burstInterval": 0.3, "cooldown": cd(8, 8, 0.3), "splash": 5, "edge": 10}),
    "be120": ("gun_120mm", {**NOFAM, "real": "Rh-120 L/44 120 mm", "damage": 260, "cooldown": 4, "pen": 5, "splash": 0}),
    # Jotunn
    "jo203": ("boss_howitzer", {"real": "2A44 203 mm", "damage": 790, "cooldown": 5, "splash": 10, "edge": 20}),
    "jo_rockets": ("boss_rockets", {"real": "BM-30 Smerch 300 mm (pod)", "damage": 110, "burst": 8, "burstInterval": 0.3, "cooldown": cd(10, 8, 0.3), "splash": 5, "edge": 10}),
    "jo125": ("gun_120mm", {**NOFAM, "real": "2A46 125 mm", "size": 125, "damage": 280, "cooldown": 2, "pen": 5, "splash": 0, "range": 38}),
    # Leviathan
    "lev406": ("leviathan_460", {**NOFAM, "real": "Type 94 406 mm/50 (triple)", "size": 406, "damage": 1200, "cooldown": 10, "splash": 12, "edge": 20}),
    "lev155": ("naval_155_triple", {**NOFAM, "real": "155 mm/60 (triple)", "damage": 170, "burst": 3, "burstInterval": 0.25, "cooldown": cd(5, 3, 0.25), "splash": 8.5, "edge": 17}),
    "lev127": ("naval_100", {**NOFAM, "real": "AK-127 127 mm", "size": 127, "damageType": "Kinetic", "damage": 320, "burst": 1, "cooldown": 2, "pen": 5, "splash": 0}),
    # Matriarch
    "ma_drones": ("mothership_drones", {**NOFAM, "real": "ZALA Lancet-3 swarm", "damage": 320, "burst": 6, "burstInterval": 0.2, "cooldown": cd(5, 6, 0.2), "splash": 3, "edge": 6}),
    "ma_atgm": ("boss_missiles", {**NOFAM, "real": "9M133 Kornet", "damage": 340, "cooldown": 2, "pen": 5, "range": 55}),
    # Moloch
    "mo120": ("gun_120mm", {**NOFAM, "real": "Rh-120 L/44 120 mm HE", "damageType": "HighExplosive", "damage": 225, "cooldown": 2, "pen": 4, "splash": 5, "edge": 10}),
    "mo120ap": ("gun_120mm", {**NOFAM, "real": "Rh-120 L/44 120 mm AP", "damage": 240, "cooldown": 2, "pen": 5, "splash": 0}),
    # Nemesis
    "ne152": ("gun_behemoth", {"real": "152 mm railcar gun", "damage": 620, "burst": 4, "burstInterval": 0.5, "cooldown": cd(5, 4, 0.5), "splash": 8.5, "edge": 17}),
    "ne125": ("gun_120mm", {**NOFAM, "real": "2A46 125 mm", "size": 125, "damage": 280, "cooldown": 2, "pen": 5, "splash": 0, "range": 38}),
    # Kronos
    "kr57": ("gun_57mm", {**NOFAM, "real": "AU-220 57 mm (automatic)", "damage": 100, "burst": 2, "burstInterval": 0.1, "cooldown": 1.4, "pen": 5}),
    # Typhon
    "ty57": ("gun_57mm", {**NOFAM, "real": "AU-220 57 mm (deck)", "damageType": "HighExplosive", "damage": 130, "burst": 2, "burstInterval": 0.1, "cooldown": 1.4, "pen": 3, "splash": 3, "edge": 6, "range": 40}),
    "ty100": ("naval_100", {**NOFAM, "real": "AK-100 100 mm (deck)", "damage": 600, "burst": 1, "cooldown": 2.5, "pen": 4, "splash": 5, "edge": 10}),
    # Roc
    "roc_bombs": ("boss_howitzer", {**NOFAM, "real": "bomb-bay stick 400 kg", "damage": 400, "burst": 8, "burstInterval": 0.3, "cooldown": cd(5, 8, 0.3), "splash": 5, "edge": 10,
                                    "range": 45, "minRange": 0, "topAttack": True}),
    "roc105": ("gunship_105", {"real": "M102 105 mm (gondola)", "damage": 700, "cooldown": 2, "splash": 6, "edge": 12}),
    "roc_atgm": ("boss_missiles", {**NOFAM, "real": "Kornet (dropped from the bay)", "damage": 300, "cooldown": 2, "pen": 5, "range": 55}),
    # Daedalus
    "dae57": ("gun_57mm", {**NOFAM, "real": "AU-220 57 mm (belly)", "damageType": "HighExplosive", "damage": 120, "burst": 2, "burstInterval": 0.2, "cooldown": 2.3, "pen": 4, "splash": 3.5, "edge": 7}),
    "dae_laser": ("orbital_laser", {"real": "targeting laser (300 kW)", "size": 300, "damage": 40}),
    # Icarus
    "ic_coil": ("coilgun", {"real": "coilgun (64 MJ)", "size": 64, "damage": 1440, "burst": 1, "cooldown": 2, "pierce": True, "pierceMax": 4, "pen": 5}),
    "ic_laser": ("orbital_laser", {"real": "laser tower (300 kW)", "size": 300, "damage": 40}),
}

# role -> mounts (indices of the boss as built); "swap": mount -> new weapon key; "fixed": DPS the weapon numbers do not carry.
SETS = {
    "fortress_bastion": {
        "roles": {"main": [8], "sec": [0], "direct": [1, 2], "close": [6, 7]}, "tiny": [3, 4, 5, 9, 10],
        "swap": {8: "b155", 0: "b240", 1: "b100", 2: "b100"}},
    "behemoth": {
        "roles": {"main": [0], "sec": [9], "direct": [7, 8], "close": [2, 3]}, "tiny": [1, 4, 5, 6],
        "swap": {0: "be152", 9: "be_rockets", 1: "be120", 7: "be120", 8: "be120"}, "wake": [9]},
    "mobile_fortress": {
        "roles": {"main": [0, 7], "sec": [1, 2], "direct": [5], "close": [3, 4]}, "tiny": [6],
        "swap": {0: "jo203", 7: "jo203", 1: "jo_rockets", 2: "jo_rockets", 5: "jo125"}, "wake": [1, 2]},
    "leviathan": {
        "roles": {"main": [0, 1, 2], "sec": [3, 4], "direct": [5, 6], "close": [7, 8, 9, 10, 11, 12, 13, 14]},
        "swap": {0: "lev406", 1: "lev406", 2: "lev406", 3: "lev155", 4: "lev155", 5: "lev127", 6: "lev127"}, "wake": [3, 4]},
    "drone_mothership": {
        "roles": {"main": [1], "sec": [6, 7], "direct": [5, 8], "close": [2, 3]}, "tiny": [0, 4],
        "swap": {1: "ma_drones", 5: "ma_atgm", 8: "ma_atgm"}, "wake": [4, 6, 7]},
    "moloch": {
        "roles": {"main": [0, 3], "direct": [4, 5], "close": [6]}, "tiny": [1, 2],
        "swap": {0: "mo120", 3: "mo120", 4: "mo120ap", 5: "mo120ap"}},
    "nuke_train": {
        "roles": {"main": [0], "sec": [3], "direct": [5], "close": [1, 2, 6]},
        "swap": {0: "ne152", 5: "ne125"}, "wake": [3]},
    "kronos": {
        "roles": {"main": [3], "sec": [], "direct": [1, 2], "close": [0, 4, 5]},
        "swap": {1: "kr57", 2: "kr57"},
        # the bucket wheel (1080 every 2 s) and the thrown rock (3 x 500 every 5 s) are the crusher's, not a mount's numbers
        "fixed": {"main": 540.0, "sec": 300.0}},
    "typhon": {
        "roles": {"sec": [1, 2], "direct": [3], "close": [0]},
        "swap": {3: "ty100"}, "fixed": {"main": 584.0}},
    "command_airship": {
        "roles": {"main": [0, 1], "sec": [6, 7], "direct": [2, 3], "close": [4, 5]},
        "swap": {0: "roc_bombs", 1: "roc_bombs", 6: "roc105", 7: "roc105", 2: "roc_atgm", 3: "roc_atgm"}, "wake": [6, 7]},
    "daedalus": {
        "roles": {"sec": [1, 2], "direct": [0, 3]},
        "swap": {1: "dae57", 2: "dae57", 0: "dae_laser", 3: "dae_laser"}, "fixed": {"main": 675.0}},
    "silver_bug": {
        "roles": {"main": [1, 2], "sec": [0], "direct": [3, 4], "close": [5, 6]},
        "swap": {1: "ic_coil", 2: "ic_coil", 3: "ic_laser", 4: "ic_laser"}},
}

SHORT = {"fortress_bastion": "bastion", "behemoth": "behemoth", "mobile_fortress": "jotunn", "leviathan": "leviathan",
         "drone_mothership": "matriarch", "moloch": "moloch", "nuke_train": "nemesis", "kronos": "kronos", "typhon": "typhon",
         "command_airship": "roc", "daedalus": "daedalus", "silver_bug": "icarus"}

TYPES = {"Kinetic": 1.0, "ShapedCharge": 1.0, "HighExplosive": 1.0, "Fire": 1.5, "Fragmentation": 0.5, "Energy": 1.0}
PENS = {2: 1.2, 1: 1.0, 0: 0.85, -1: 0.5, -2: 0.25, -3: 0.1}


# ------------------------------------------------------------------------------------------------ the game's data in python

class Game:
    def __init__(self, data):
        self.data = data
        self.families = {f["id"]: f for f in data.get("weaponFamilies", [])}
        self._w = {}
        self._n = -1
        self._raw = {}

    @property
    def raw_weapons(self):
        # The plan adds weapons as it goes: the index follows the list.
        if self._n != len(self.data["weapons"]):
            self._raw = {w["id"]: w for w in self.data["weapons"]}
            self._n = len(self.data["weapons"])
            self._w.clear()
        return self._raw

    def weapon(self, wid):
        self.raw_weapons
        if wid in self._w:
            return self._w[wid]
        w = dict(self.raw_weapons[wid])
        if "inherits" in w:
            base = dict(self.weapon(w["inherits"]))
            base.update(w)
            w = base
        if w.get("weaponFamily") in self.families:
            for k, v in self.families[w["weaponFamily"]].items():
                if k not in ("id", "real"):
                    w[k] = v
        self._w[wid] = w
        return w


def expand(data):
    """steps_c.expand with prompt 26's "mountWeapons" applied where BossTemplates applies it."""
    library = data.get("bossParts", {})
    before, out = {}, {}

    def swaps(d):
        mw = d.pop("mountWeapons", None)
        if not mw:
            return
        for k, wid in mw.items():
            k = int(k)
            if k == 0:
                d["weapon"] = wid
            else:
                d["secondary"][k - 1]["weapon"] = wid

    for pass_ in (0, 1):
        for v in data["vehicles"]:
            variant = isinstance(v.get("variantOf"), str)
            if variant != (pass_ == 1):
                continue
            if not variant and not (v.get("boss") is True or "frame" in v or "rank" in v):
                continue
            if variant:
                d = copy.deepcopy(before[v["variantOf"]])
                for k in S.NOT_INHERITED + ("mountWeapons",):
                    d.pop(k, None)
                rules = v.get("variant") or {}
                if "keep" in rules:
                    keep = set(rules["keep"])
                    S._strip(d, lambda i: i in keep)
                if "drop" in rules:
                    drop = set(rules["drop"])
                    S._strip(d, lambda i: i not in drop)
                for p in d.get("parts") or []:
                    if p.get("id") in (rules.get("tune") or {}):
                        p.update(rules["tune"][p["id"]])
                for k, val in v.items():
                    if k == "variant":
                        continue
                    if isinstance(val, dict) and isinstance(d.get(k), dict):
                        d[k] = S._merge(d[k], val)
                    else:
                        d[k] = copy.deepcopy(val)
                d["boss"] = True
                d.setdefault("rank", "mini")
            else:
                d = S._build(copy.deepcopy(v), library)
                if d.get("dropParts"):
                    drop = set(d["dropParts"])
                    S._strip(d, lambda i: i not in drop)
            swaps(d)
            before[d["id"]] = copy.deepcopy(d)
            d.setdefault("rank", "main")
            out[d["id"]] = d
    return out


def per_mount(g, b):
    """[(weapon id, vs-armour-3 DPS at its own numbers, laid)] for each mount of a built boss."""
    out = []
    ids = [b.get("weapon")] + [m.get("weapon") for m in b.get("secondary") or []]
    for wid in ids:
        if not wid or wid not in g.raw_weapons:
            out.append((wid, 0.0, False))
            continue
        w = g.weapon(wid)
        v = S.vs_armour3(w, TYPES, PENS)
        if w.get("melee") and w.get("laid"):
            out.append((wid, 0.0, True))
            continue
        out.append((wid, v, bool(w.get("laid"))))
    return out


TINY = 0.2


def retune(w, k, cadence=True):
    """The fields that give weapon `w` k times its DPS: a slower or a faster cadence first (the listed rounds keep their size
    within reason), then the damage for the rest."""
    d0, cd0 = w["damage"], w.get("cooldown", 1.0)
    fields = {}
    if cadence and cd0 >= 1.0 and not w.get("clip") and not w.get("ammo") and not w.get("beam") and abs(k - 1.0) > 0.15:
        cd1 = min(cd0 * 3.0, max(1.0, cd0 / 2.5, cd0 / k))
        cd1 = round(cd1 * 2) / 2 if cd1 >= 2 else round(cd1 * 10) / 10
        if abs(cd1 - cd0) > 1e-6:
            s0 = S.sustained(w)
            s1 = S.sustained({**w, "cooldown": cd1})
            fields["cooldown"] = cd1
            d0 = d0 * k * s0 / s1
            fields["damage"] = nice(d0)
            return fields
    fields["damage"] = nice(d0 * k)
    return fields


def nice(x):
    if x >= 100:
        return int(round(x / 5.0)) * 5
    if x >= 20:
        return int(round(x))
    if x >= 5:
        return round(x * 2) / 2
    return round(x, 2)


# ------------------------------------------------------------------------------------------------ the plan

class Plan:
    """The edits to the file, each also applied to a copy of the data in memory (so the DPS is solved on the result)."""

    def __init__(self, doc, data):
        self.doc = doc
        self.data = copy.deepcopy(data)
        self.vehicles = {v["id"]: v for v in self.data["vehicles"]}
        self.new_weapons = []   # (after id, dict)
        self.vehicle_edits = {}  # id -> {key: value}
        self.weapon_edits = {}   # weapon id -> {key: value}
        self.attack_edits = {}   # big attack id -> fn(entry)
        self.text_edits = []     # (old, new) in the file's text

    def set(self, vid, key, value):
        self.vehicle_edits.setdefault(vid, {})[key] = value
        self.vehicles[vid][key] = copy.deepcopy(value)

    def add_weapon(self, wid, inherits, fields, after):
        w = {"id": wid, "inherits": inherits, **fields}
        self.new_weapons.append((after, w))
        self.data["weapons"].append(w)

    def has_weapon(self, wid):
        return any(w["id"] == wid for w in self.data["weapons"])


def weapon_line(w):
    return "{ " + ", ".join(f'{json.dumps(k)}: {fmt(v)}' for k, v in w.items()) + " }"


def main():
    doc = Doc(PATH)
    data = doc.data()
    plan = Plan(doc, data)
    g = Game(plan.data)
    report = []

    existing = {w["id"] for w in data["weapons"]}

    # ---- the main bosses' sets
    for vid, spec in SETS.items():
        short = SHORT[vid]
        # 1. the new weapons at their listed numbers, and the swaps
        swaps = {}
        for mount, key in spec["swap"].items():
            wid = f"p26_{short}_{key}"
            swaps[mount] = wid
            if not plan.has_weapon(wid):
                base, fields = WEAPONS[key]
                plan.add_weapon(wid, base, copy.deepcopy(fields), after="boss_missiles")
        if vid == "typhon":
            # two partless 57 mm guns beside the Buk and the deck gun: raw secondary mounts (the deck gun's index moves to 3)
            wid = f"p26_{short}_ty57"
            base, fields = WEAPONS["ty57"]
            plan.add_weapon(wid, base, copy.deepcopy(fields), after="boss_missiles")
            plan.set(vid, "secondary", [{"weapon": wid, "slot": "gun", "aim": "Free"}, {"weapon": wid, "slot": "gun", "aim": "Free"}])
            plan.set(vid, "wake", {"phase": 2, "mounts": [3]})
        if swaps:
            plan.set(vid, "mountWeapons", {str(k): w for k, w in sorted(swaps.items())})
        if vid != "typhon" and spec.get("wake"):
            plan.set(vid, "wake", {"phase": 1, "mounts": spec["wake"]})
        plan.set(vid, "weaponDamage", 1)

        # 2. the roles' targets and the scale each role's weapons need
        built = expand(plan.data)[vid]
        mounts = per_mount(g, built)
        T = target_dps(vid)
        fixed_roles = spec.get("fixed", {})
        roles = {r: list(m) for r, m in spec["roles"].items()}
        for r in fixed_roles:
            roles.setdefault(r, [])
        raw = {}
        for r, idx in roles.items():
            raw[r] = (sum(mounts[i][1] for i in idx if not mounts[i][2]),
                      sum(mounts[i][1] for i in idx if mounts[i][2]) + fixed_roles.get(r, 0.0))
        live = {r: SHARES[r] for r in roles if raw[r][0] > 0 or raw[r][1] > 0}
        total_share = sum(live.values())
        tiny = list(spec.get("tiny", []))
        tiny_dps = sum(mounts[i][1] * TINY for i in tiny if not mounts[i][2])
        scales = {}
        for r in live:
            troll = (T - tiny_dps) * live[r] / total_share
            scaled, fixed = raw[r]
            k = (troll - fixed) / scaled if scaled > 0 else 1.0
            scales[r] = (k, troll, fixed, scaled)
        report.append(f"== {vid} (T {T:.0f}); roles " + ", ".join(f"{r} {t[1]:.0f}" for r, t in scales.items()))
        # 3. write each role's weapons at the scale (a new weapon id per role and base weapon)
        final = {}
        for r, idx in roles.items():
            if r not in scales:
                continue
            k = scales[r][0]
            for i in idx:
                wid = mounts[i][0]
                if mounts[i][2] or not wid or mounts[i][1] <= 0:
                    continue
                final[i] = (r, wid, k)
        for i in tiny:
            if mounts[i][1] > 0 and not mounts[i][2]:
                final[i] = ("tiny", mounts[i][0], TINY)
        new_swaps = dict(plan.vehicles[vid].get("mountWeapons") or {})
        made = {}
        for i, (r, wid, k) in final.items():
            if abs(k - 1.0) < 0.04:
                continue
            w = g.weapon(wid)
            fields = retune(w, k, r != "tiny")
            sid = f"p26_{short}_{r}_{re.sub('^p26_' + short + '_', '', wid)}"
            if sid not in made:
                made[sid] = True
                if not plan.has_weapon(sid):
                    plan.add_weapon(sid, wid, {**NOFAM, **fields} if w.get("weaponFamily") in g.families else fields, after="boss_missiles")
                else:
                    for x in plan.data["weapons"]:
                        if x["id"] == sid:
                            x.update(fields)
                    for _, x in plan.new_weapons:
                        if x["id"] == sid:
                            x.update(fields)
                g._w.pop(sid, None)
            new_swaps[str(i)] = sid
        g._w.clear()
        plan.set(vid, "mountWeapons", dict(sorted(new_swaps.items(), key=lambda kv: int(kv[0]))))
        # 4. check
        built = expand(plan.data)[vid]
        mounts = per_mount(g, built)
        sums = {}
        for r, idx in roles.items():
            sums[r] = sum(mounts[i][1] for i in idx) + fixed_roles.get(r, 0.0)
        sums["tiny"] = sum(mounts[i][1] for i in tiny)
        total = sum(sums.values())
        report.append("   got " + ", ".join(f"{r} {v:.0f}" for r, v in sums.items()) + f" = {total:.0f}")
        for i, (wid, v, laid) in enumerate(mounts):
            if v > 0 or laid:
                w = g.weapon(wid)
                report.append(f"     {i:2d} {wid:38s} {w.get('damage')}x{w.get('burst', 1)}/{w.get('cooldown')} pen {w.get('pen')} splash {w.get('splash')} -> {v:.0f}{' laid' if laid else ''}")

    # ---- a mini boss fights from its first second: no mount of its parent's second phase sleeps on it
    for vid in MINIS:
        parent = plan.vehicles[vid].get("variantOf")
        if parent in SETS and (SETS[parent].get("wake") or parent == "typhon") and "wake" not in (plan.vehicles[vid]):
            plan.set(vid, "wake", None)

    # ---- everyone else's weaponDamage: mini bosses and the batch D bosses
    built_all = expand(plan.data)
    for vid in list(MINIS) + [m for m in MAINS if m not in SETS]:
        b = built_all[vid]
        mounts = per_mount(g, b)
        scaled = sum(v for _, v, laid in mounts if not laid)
        fixed = sum(v for _, v, laid in mounts if laid)
        cruise = b.get("cruise")
        if cruise and b.get("naval") is not None:
            w = g.weapon(cruise["weapon"]) if cruise.get("weapon") in g.raw_weapons else {}
            fixed += cruise.get("damage", 520) / cruise.get("every", 48) * PENS.get(int(w.get("pen", 3)) - 3, 1.0)
        T = target_dps(vid)
        wd = max(0.2, (T - fixed) / scaled) if scaled > 0 else 1.0
        note = ""
        if vid in MINIS and wd > MAX_MINI_WEAPON_DAMAGE:
            note = f" (capped from {wd:.2f}: its fire is mostly not a mount's)"
            wd = MAX_MINI_WEAPON_DAMAGE
        plan.set(vid, "weaponDamage", round(wd, 3))
        report.append(f"{vid:20s} T {T:6.0f} scaled {scaled:6.0f} fixed {fixed:5.0f} -> weaponDamage {wd:.3f}{note}")

    extras(plan, report)

    # ---- write
    written = set(w["id"] for w in doc.data()["weapons"])
    prev = "boss_missiles"
    for after, w in plan.new_weapons:
        if w["id"] in written:
            doc.edit("weapons", w["id"], lambda e, w=w: [e.set(k, v) for k, v in w.items() if k != "id"])
            continue
        doc.insert_after("weapons", prev, weapon_line(w))
        prev = w["id"]
        written.add(w["id"])
    for wid, fields in plan.weapon_edits.items():
        doc.edit("weapons", wid, lambda e, fields=fields: [e.set(k, v) for k, v in fields.items()])
    for vid, edits in plan.vehicle_edits.items():
        def apply(e, edits=edits):
            for k, v in edits.items():
                e.set(k, v)
        doc.edit("vehicles", vid, apply)
    for aid, fn in plan.attack_edits.items():
        doc.edit("bigAttacks", aid, fn)
    crlf = "\r\n" in doc.text
    for old, new in plan.text_edits:
        if crlf:
            old, new = old.replace("\n", "\r\n"), new.replace("\n", "\r\n")
        if new in doc.text:
            continue
        if old not in doc.text:
            raise SystemExit("text edit found nothing: " + old[:80])
        doc.text = doc.text.replace(old, new)
    print("\n".join(report))
    if "--write" in sys.argv:
        print("file changed" if doc.save() else "file unchanged")
    else:
        print("dry run (--write saves)")


MAX_MINI_WEAPON_DAMAGE = 6.0

# the super weapons (B.6, B.7): cycle 45-50 s, warning 3-4 s, the listed rounds
ATTACKS = {
    "bastion_420_shell": {"cooldown": 45, "warn": 4, "strike": {"damage": 2000, "radius": 10}},
    "behemoth_barrage": {"cooldown": 45, "warn": 3.5, "strike": {"count": 6, "damage": 600, "radius": 8.5}},
    "fortress_203_barrage": {"cooldown": 50, "warn": 4, "strike": {"perPart": 2, "damage": 900, "radius": 10}},
    "leviathan_volley": {"cooldown": 50, "warn": 4, "strike": {"perPart": 3, "damage": 950, "radius": 12}},
    "carrier_heavy_bomb": {"cooldown": 45, "warn": 3.5, "strike": {"damage": 1600, "radius": 16}},
    "moloch_factory_dump": {"cooldown": 50, "warn": 4, "strike": {"damage": 350}, "second": True},
    "doomsday_missile": {"cooldown": 50, "warn": 4, "strike": {"damage": 3500, "radius": 18}},
    "kronos_bucket_sweep": {"cooldown": 45, "warn": 4, "strike": {"damage": 2500}},
    "typhon_underwater_launch": {"cooldown": 50, "warn": 4, "strike": {"count": 6, "damage": 700}},
    "airship_carpet": {"cooldown": 50, "warn": 4, "strike": {"count": 16, "damage": 400}},
    "daedalus_mass_drop": {"cooldown": 50, "warn": 4, "strike": {"count": 8, "damage": 600}},
    "bug_rod_rain": {"cooldown": 45, "warn": 4, "strike": {"count": 7, "damage": 1800}, "late": {"phase": 2, "cooldown": 45, "count": 9}},
    "kraken_air_raid": {"cooldown": 50, "warn": 4, "strike": {}},
    "monster_800_shell": {"cooldown": 50, "warn": 4, "strike": {}},
    "garuda_carpet": {"cooldown": 50, "warn": 4, "strike": {}},
    "hyperion_sun_beam": {"cooldown": 50, "warn": 4, "strike": {}},
}


def extras(plan, report):
    """Health, armour, phases, ranks, difficulty, the super weapons and the bosses' own mechanisms."""
    for vid in list(MAINS) + list(MINIS):
        plan.set(vid, "hp", data_hp(vid))

    # armour: a main boss front 5 / side 3 / rear 2 (an aircraft or a tiered craft keeps its own), a mini's front at most 4
    built = expand(plan.data)
    for vid in MAINS:
        b = built[vid]
        if b.get("flying") or b.get("tiers") or vid == "garuda":
            continue
        a = b.get("armour")
        top = a[3] if isinstance(a, list) and len(a) > 3 else (a if isinstance(a, (int, float)) else 2)
        plan.set(vid, "armour", [5, 3, 2, top])
    built = expand(plan.data)
    for vid in MINIS:
        a = built[vid].get("armour")
        front = a[0] if isinstance(a, list) else a
        if front is None or front <= 4:
            continue
        plan.set(vid, "armour", [4] + a[1:] if isinstance(a, list) else 4)
        report.append(f"armour {vid}: front {front} -> 4")

    # phases of the bosses that carry their own: a main 40 / 35 / 25 (the last 25 % fires faster), a mini 55 / 45
    for vid in ("command_airship", "leviathan", "kronos"):
        phases = copy.deepcopy(plan.vehicles[vid]["phases"])
        phases[0]["at"], phases[1]["at"] = 0.6, 0.25
        phases[1]["fireRate"] = 1.25
        plan.set(vid, "phases", phases)
    for vid in ("rail_supergun", "earth_borer", "landing_hovercraft", "supreme_command"):
        phases = copy.deepcopy(plan.vehicles[vid]["phases"])
        phases[0]["at"] = 0.45
        plan.set(vid, "phases", phases)

    t = plan.text_edits
    t.append(('"phases": [ { "at": 0.7, "transform": 2.5, "damage": 1.1 }, { "at": 0.3, "transform": 3, "damage": 1.2, "speed": 1.1 } ] },',
              '"phases": [ { "at": 0.6, "transform": 2.5, "damage": 1.1 }, { "at": 0.25, "transform": 3, "damage": 1.2, "speed": 1.1, "fireRate": 1.25 } ] },'))
    t.append(('"phases": [ { "at": 0.5, "transform": 2, "damage": 1.15 } ] }', '"phases": [ { "at": 0.45, "transform": 2, "damage": 1.15 } ] }'))
    t.append(('"main": { "intro": 6, "music": "boss", "reward": 1,', '"main": { "intro": 6, "music": "boss", "reward": 1, "partsShare": 0.35,'))
    t.append(('"mini": { "hp": 0.55, "damageScale": 1.2,', '"mini": { "hp": 0.55, "partsShare": 0.35, "damageScale": 1.2,'))
    # the tiered crafts' marks (40 / 35 / 25), the Icarus Mk.0's (55 / 45)
    t.append(('"marks": [0.7, 0.3]', '"marks": [0.6, 0.25]'))
    t.append(('"crash": null, "hijack": null, "marks": [0.5]', '"crash": null, "hijack": null, "marks": [0.45]'))
    # A.6: the difficulty's factors on the enemy's bosses; the big attacks take the damage from the boss itself
    t.append(('''      "Easy":     { "damage": 0.8, "cooldown": 1.2, "warn": 1 },
      "Normal":   { "damage": 1,   "cooldown": 1,   "warn": 0 },
      "Hard":     { "damage": 1,   "cooldown": 0.9, "warn": 0 },
      "VeryHard": { "damage": 1.1, "cooldown": 0.8, "warn": 0 },
      "Heroic":   { "damage": 1.1, "cooldown": 0.8, "warn": 0 },
      "Iron":     { "damage": 1.1, "cooldown": 0.8, "warn": 0 }''',
              '''      // Prompt 26 A.6: "bossHp" and "bossDamage" are the enemy boss's own health and damage factors by difficulty (its big
      // attack takes the damage factor with the rest of its fire, so "damage" here is 1 for all); cooldown and warning as before.
      "Easy":     { "damage": 1, "cooldown": 1.2, "warn": 1, "bossHp": 0.75, "bossDamage": 0.8 },
      "Normal":   { "damage": 1, "cooldown": 1,   "warn": 0, "bossHp": 1,    "bossDamage": 1 },
      "Hard":     { "damage": 1, "cooldown": 0.9, "warn": 0, "bossHp": 1.25, "bossDamage": 1.15 },
      "VeryHard": { "damage": 1, "cooldown": 0.8, "warn": 0, "bossHp": 1.5,  "bossDamage": 1.3 },
      "Heroic":   { "damage": 1, "cooldown": 0.8, "warn": 0, "bossHp": 1.5,  "bossDamage": 1.3 },
      "Iron":     { "damage": 1, "cooldown": 0.8, "warn": 0, "bossHp": 1.5,  "bossDamage": 1.3 }'''))

    # the super weapons
    for aid, spec in ATTACKS.items():
        def fn(e, spec=spec):
            e.set("cooldown", spec["cooldown"])
            e.set("warn", spec["warn"])
            strikes = e.get("strikes")
            index = 1 if spec.get("second") else 0
            strikes[index].update(spec["strike"])
            e.set("strikes", strikes)
            if "late" in spec:
                e.set("late", spec["late"])
        plan.attack_edits[aid] = fn

    # the bosses' own mechanisms
    kr = copy.deepcopy(plan.vehicles["kronos"]["crush"])
    kr.update({"debrisPhase": 1, "debrisEvery": 5, "debrisDamage": 500})
    plan.set("kronos", "crush", kr)
    plan.weapon_edits["bucket_wheel"] = {"damage": 1080, "cooldown": 2}
    ty = copy.deepcopy(plan.vehicles["typhon"]["cruise"])
    ty.update({"every": 2.5, "damage": 1460})
    plan.set("typhon", "cruise", ty)
    lv = copy.deepcopy(plan.vehicles["leviathan"]["salvo"])
    lv.update({"every": 10, "damage": 1200, "radius": 12, "weapon": "p26_leviathan_lev406"})
    plan.set("leviathan", "salvo", lv)
    pods = copy.deepcopy(plan.vehicles["daedalus"]["pods"])
    pods.update({"count": 3, "everyByPhase": [8, 6.5, 5], "damage": 1125, "radius": 6, "stun": 1})
    plan.set("daedalus", "pods", pods)
    bu = copy.deepcopy(plan.vehicles["earth_borer"]["burrow"])
    bu.update({"radius": 6})
    plan.set("earth_borer", "burrow", bu)
    plan.weapon_edits["naval_130_twin"] = {"splash": 5}
    cs = copy.deepcopy(plan.vehicles["caspian"]["cruise"])
    cs.update({"every": 13, "damage": 700, "radius": 7})
    plan.set("caspian", "cruise", cs)


if __name__ == "__main__":
    main()
