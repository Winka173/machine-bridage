"""Prompt 32 L1: the tower roster 32 -> 22 and the branch rule, written into balance.json (in place, comments kept).

    python Tools/balance/p32_roster.py          # applies (idempotent: a second run changes nothing)
    python Tools/balance/p32_roster.py --check  # only validates the data (exit 1 on a finding)

The roster ("base.roster"), each card's "branches" (A/B) or "noBranch", a "towerRole" tag on every branch (and on a
card without branches), the new branch rows of the merged cards (each inherits the tower it absorbs), the removed
branch rows of the cards left without branches, the 57 mm branch made a light-vehicle gun (no aircraft), the AA
tower's B branch made the Stinger post, the minefield's one kind (the AT branch's mines), and the AI base styles moved
onto the surviving cards. The check is the same as TowerRosterP32Tests (EditMode).
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from jsonc_edit import Doc, loads  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")

# The 22 cards: (card, size, branches A/B with their role tags, or the card's own role when it has no branch).
ROSTER = [
    # small (10)
    ("guard_tower", "Small", [("guard_tower.watch", "observation_reach"), ("guard_tower.nest", "autocannon_25")]),
    ("mg_bunker", "Small", [("mg_bunker.twin", "mg_twin"), ("mg_bunker.flame", "flame_close")]),
    ("at_gun_emplacement", "Small", [("at_gun_emplacement.long", "at_gun_long_narrow"), ("at_gun_emplacement.recoilless", "at_recoilless_wide")]),
    ("aa_turret", "Small", [("aa_turret.flak", "aa_gun_23_drones_helis"), ("aa_turret.sam", "aa_manpads_aircraft")]),
    ("ew_tower", "Small", [("ew_tower.drone", "jam_drones_guided"), ("ew_tower.spoof", "radar_spoof_counterbattery")]),
    ("dragons_teeth", "Small", [("dragons_teeth.hedgehog", "obstacle_block"), ("dragons_teeth.wire", "wire_slow")]),
    ("minefield", "Small", "mines_at"),
    ("cp_relay", "Small", "cp_income"),
    ("searchlight", "Small", [("searchlight.beam", "light_area"), ("searchlight.flare", "light_flare_waves")]),
    ("inflatable_decoy", "Small", [("inflatable_decoy.inflatable", "decoy_draw_fire"), ("inflatable_decoy.balloon", "balloon_scatter_reveal")]),
    # medium (7)
    ("atgm_tower", "Medium", [("atgm_tower.top", "atgm_top_attack"), ("atgm_tower.multi", "atgm_multi")]),
    ("gun_turret", "Medium", [("gun_turret.long", "gun_sniper_120"), ("gun_turret.auto", "gun_57_light")]),
    ("c_ram", "Medium", [("c_ram.centurion", "intercept_close_fast"), ("c_ram.dome", "intercept_far_slow")]),
    ("rocket_turret", "Medium", [("rocket_turret.cluster", "rockets_cluster"), ("rocket_turret.guided", "rockets_guided")]),
    ("heavy_flak_tower", "Medium", [("heavy_flak_tower.heavy", "aa_heavy_flak_area"), ("heavy_flak_tower.bofors", "aa_40_steady")]),
    ("laser_ad_station", "Medium", [("laser_ad_station.laser", "antidrone_laser"), ("laser_ad_station.net", "antidrone_net")]),
    ("troop_shelter", "Medium", "shelter_troops"),
    # large (5)
    ("heavy_turret", "Large", [("heavy_turret.coastal", "gun_coastal_long"), ("heavy_turret.bastion", "fortress_close_defence")]),
    ("missile_battery", "Large", [("missile_battery.pac3", "intercept_heavy_missiles"), ("missile_battery.lrr", "sam_long_radar")]),
    ("drone_hangar", "Large", [("drone_hangar.lancet", "drone_loitering"), ("drone_hangar.swarm", "drone_fpv_swarm")]),
    ("artillery_emplacement", "Large", [("artillery_emplacement.cb", "counter_battery"), ("artillery_emplacement.mortar", "mortar_lobbed")]),
    ("shield_tower", "Large", [("shield_tower.bulwark", "shield_dome"), ("shield_tower.ward", "tower_shields")]),
]

# New branch rows of the merged cards: (branch id, the row it inherits, extra fields). Each takes the absorbed tower's line.
NEW_BRANCHES = {
    "at_gun_emplacement.long": ("at_gun_emplacement", {}),
    "at_gun_emplacement.recoilless": ("recoilless_gun_tower", {}),
    "searchlight.beam": ("searchlight", {}),
    "searchlight.flare": ("flare_tower", {}),
    "inflatable_decoy.inflatable": ("inflatable_decoy", {}),
    "inflatable_decoy.balloon": ("barrage_balloon", {}),
    "heavy_flak_tower.heavy": ("heavy_flak_tower", {}),
    "heavy_flak_tower.bofors": ("aa_gun_tower", {}),
    "laser_ad_station.laser": ("laser_ad_station", {}),
    # The net corridor fights in the medium card's slot.
    "laser_ad_station.net": ("drone_net_tower", {"fort": {"size": "Medium"}}),
}

# Old card -> the card it was folded into; cards retired from the roster (kept as map and mission structures).
MERGED = {
    "recoilless_gun_tower": "at_gun_emplacement",
    "manpads_tower": "aa_turret",
    "flare_tower": "searchlight",
    "flare_searchlight_tower": "searchlight",
    "barrage_balloon": "inflatable_decoy",
    "aa_gun_tower": "heavy_flak_tower",
    "drone_net_tower": "laser_ad_station",
    "bunker_shelter_tower": "troop_shelter",
}
RETIRED = ["blast_wall", "one_shot_atgm_tower"]
# Branch rows of the cards left without branches.
REMOVED_BRANCHES = ["minefield.at", "minefield.scatter", "cp_relay.hardened", "cp_relay.loot"]


def remove_entry(doc: Doc, name: str, id_: str) -> bool:
    for i, s, e in doc._entries(name):
        if i != id_:
            continue
        t = doc.text
        line_start = t.rindex("\n", 0, s) + 1
        j = e
        while j < len(t) and t[j] in " \t":
            j += 1
        if j < len(t) and t[j] == ",":
            j += 1
        eol = t.index("\n", j)
        doc.text = t[:line_start] + t[eol + 1:]
        return True
    return False


def fmt_obj(d: dict) -> str:
    return "{ " + ", ".join(f"{json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in d.items()) + " }"


def apply():
    doc = Doc(BALANCE)
    data = doc.data()
    vehicles = {v["id"]: v for v in data["vehicles"]}

    # Removed branch rows.
    for b in REMOVED_BRANCHES:
        remove_entry(doc, "vehicles", b)

    # New branch rows, after their card (A then B).
    for card, _, branches in ROSTER:
        if isinstance(branches, str):
            continue
        after = card
        for bid, role in branches:
            ids = doc.ids("vehicles")
            if bid in NEW_BRANCHES and bid not in ids:
                parent, extra = NEW_BRANCHES[bid]
                row = {"id": bid, "inherits": parent, "branchOf": card}
                row.update(extra)
                row["towerRole"] = role
                doc.insert_after("vehicles", after, fmt_obj(row))
            after = bid if bid in doc.ids("vehicles") else after

    # Cards: their branches or noBranch; branch rows: their role tags.
    for card, _, branches in ROSTER:
        if isinstance(branches, str):
            role = branches
            doc.edit("vehicles", card, lambda e, r=role: (e.remove("branches"), e.set("noBranch", True), e.set("towerRole", r)))
            continue
        doc.edit("vehicles", card, lambda e, b=[x for x, _ in branches]: (e.remove("noBranch"), e.set("branches", b)))
        for bid, role in branches:
            doc.edit("vehicles", bid, lambda e, r=role: e.set("towerRole", r))

    # The minefield's one kind: the AT branch's mines (its count and its relaying rhythm).
    at_mines = vehicles.get("minefield.at", {}).get("mines")
    if at_mines:
        doc.edit("vehicles", "minefield", lambda e: e.set("mines", at_mines))

    # The 57 mm branch: light vehicles only, no aircraft (its air-burst round goes).
    doc.edit("weapons", "gun_57_auto", lambda e: (e.remove("air"), e.set("targets", "Ground"), e.set("prey", "Light")))
    # The AA tower's B branch: the Stinger post (the MANPADS tower it absorbs), out-reaching the 23 mm A branch (46 m).
    if "stinger_post" not in doc.ids("weapons"):
        doc.insert_after("weapons", "sam", fmt_obj({"id": "stinger_post", "inherits": "sam", "real": "FIM-92 Stinger (tower post)", "range": 56}))
    doc.edit("vehicles", "aa_turret.sam", lambda e: (e.set("weapon", "stinger_post"), e.set("vision", 60)))

    # The Iron Beam vehicle and the fixed laser site stop no shells (the balance file v2's APS sheet; prompt 29 left it).
    for vid in ("iron_beam", "laser_ad_station"):
        doc.edit("vehicles", vid, lambda e: e.set_sub("aps", "shells", 0))

    # The roster.
    roster = [c for c, _, _ in ROSTER]
    m = re.search(r'\n(    )"hq": "headquarters",[^\n]*\n', doc.text)
    line = '    "roster": ' + json.dumps(roster) + ",\n"
    if '"roster":' in doc.text[:doc.text.index('"levels"')]:
        doc.text = re.sub(r'    "roster": \[[^\]]*\],\n', line.replace("\\", "\\\\"), doc.text, count=1)
    else:
        doc.text = doc.text[:m.end()] + "    // Prompt 32 L1 (DECISIONS \"Prompt 32 L0/L1/L2\"): the player's 22 tower cards (10 small, 7 medium, 5 large).\n" + line + doc.text[m.end():]

    # AI base styles: a merged card's weight goes to the card it became (the larger one kept); retired cards and removed
    # branches drop out.
    def restyle(match):
        name, body = match.group(1), match.group(2)
        try:
            w = json.loads(body)
        except ValueError:
            return match.group(0)
        out = {}
        for k, v in w.items():
            if k in RETIRED or k in REMOVED_BRANCHES:
                continue
            k2 = MERGED.get(k, k)
            out[k2] = max(out.get(k2, 0), v)
        return f'"{name}": {fmt_obj(out)}'

    s, e = doc._section("base")
    block = doc.text[s:e]
    st = block.index('"styles"')
    styles = re.sub(r'"([a-z_]+)": (\{[^{}]*\})', restyle, block[st:])
    doc.text = doc.text[:s] + block[:st] + styles + doc.text[s + len(block):]
    doc.save()
    return check()


def check() -> int:
    d = loads(open(BALANCE, encoding="utf-8").read())
    raw = {v["id"]: v for v in d["vehicles"]}

    def res(v, depth=0):
        if "inherits" in v and depth < 5:
            b = dict(res(raw[v["inherits"]], depth + 1))
            b.update(v)
            return b
        return v

    vs = {k: res(v) for k, v in raw.items()}
    errors = []
    roster = d["base"].get("roster", [])
    sizes = {"Small": 0, "Medium": 0, "Large": 0}
    roles: dict[str, str] = {}
    for card in roster:
        v = vs.get(card)
        if v is None or "fort" not in v:
            errors.append(f"{card}: not a tower")
            continue
        sizes[v["fort"]["size"]] += 1
        own = raw[card]
        if own.get("noBranch"):
            if own.get("branches"):
                errors.append(f"{card}: noBranch and branches")
            tags = [own.get("towerRole")]
        else:
            br = own.get("branches", [])
            if len(br) != 2 or len(set(br)) != 2:
                errors.append(f"{card}: needs two branches or noBranch, has {br}")
                continue
            tags = []
            for b in br:
                if b not in vs:
                    errors.append(f"{card}: unknown branch {b}")
                    continue
                if vs[b].get("branchOf") != card:
                    errors.append(f"{b}: branchOf {vs[b].get('branchOf')}, not {card}")
                if vs[b]["fort"]["size"] != v["fort"]["size"]:
                    errors.append(f"{b}: size {vs[b]['fort']['size']}, its card {v['fort']['size']}")
                tags.append(raw[b].get("towerRole"))
            if len(tags) == 2 and tags[0] == tags[1]:
                errors.append(f"{card}: both branches do {tags[0]}")
        for t in tags:
            if not t:
                errors.append(f"{card}: a branch without a towerRole")
            elif t in roles and roles[t] != card:
                errors.append(f"{card}: role {t} is also {roles[t]}'s")
            else:
                roles[t] = card
    for k, v in vs.items():
        if v.get("branchOf") in roster and k not in raw[v["branchOf"]].get("branches", []):
            errors.append(f"{k}: a branch row of {v['branchOf']} its card does not declare")
    if len(roster) != 22 or sizes != {"Small": 10, "Medium": 7, "Large": 5}:
        errors.append(f"roster {len(roster)} cards, sizes {sizes} (want 22: 10 / 7 / 5)")
    for gone in list(MERGED) + RETIRED:
        if gone in roster:
            errors.append(f"{gone}: still a card")
    for e in errors:
        print("ERROR", e)
    print(f"roster {len(roster)} cards {sizes}, {len(roles)} role tags, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else apply())
