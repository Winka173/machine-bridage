#!/usr/bin/env python
"""Balance master final (06/10, Docs/prompts/balance_master_final_spec.md): applies every canonical change to balance.json
in place (Tools/balance/jsonc_edit.py: comments and untouched lines stay byte for byte) and writes the old -> new log.
Idempotent guard: refuses to run twice (checks the Hellfire family row).
Usage: python Tools/balance/balance_final_apply.py [--log out.json]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import jsonc_edit as J  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BAL = os.path.join(ROOT, "Assets/MachineBrigade/Resources/Data/balance.json")
doc = J.Doc(BAL)
LOG = []


def half_up(x, nd=0):
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(1).scaleb(-nd)
    v = float(Decimal(str(round(x, 9))).quantize(q, rounding=ROUND_HALF_UP))
    return int(v) if nd == 0 else v


def setf(section, id_, key, new, why, sub=None):
    e = doc.entry(section, id_)
    if e is None:
        raise KeyError(f"{section}: {id_}")
    old = (e.sub(sub).get(key) if e.has(sub) else None) if sub else e.get(key)
    if sub:
        e.set_sub(sub, key, new)
    else:
        e.set(key, new)
    doc.put(section, id_, e)
    LOG.append({"section": section, "id": id_, "field": f"{sub}.{key}" if sub else key, "old": old, "new": new, "why": why})


def nested(id_):
    """(start, end) of the one object whose text starts with {"id": "<id_>" anywhere (a second round, a nested row)."""
    import re
    hits = [m.start() for m in re.finditer(r'\{\s*"id"\s*:\s*"' + re.escape(id_) + '"', doc.text)]
    assert len(hits) == 1, (id_, len(hits))
    return hits[0], J._match(doc.text, hits[0]) + 1


def nset(id_, key, new, why):
    s, e = nested(id_)
    ent = J.Entry(doc.text[s:e])
    old = ent.get(key)
    ent.set(key, new)
    doc.text = doc.text[:s] + ent.text + doc.text[e:]
    LOG.append({"section": "secondRounds.rounds", "id": id_, "field": key, "old": old, "new": new, "why": why})


def mul(section, id_, key, factor, why, nd=0, sub=None, default=None):
    e = doc.entry(section, id_)
    cur = (e.sub(sub).get(key) if sub else e.get(key))
    if cur is None:
        cur = default
    if cur is None:
        raise KeyError(f"{section}.{id_}.{key}: no value to scale")
    setf(section, id_, key, half_up(cur * factor, nd), f"{why} (x{factor})", sub)


W, V, FAM, SUP = "weapons", "vehicles", "weaponFamilies", "supports"

if doc.entry(FAM, "agm_114_hellfire").get("projectileSpeed") == 70:
    sys.exit("already applied (agm_114_hellfire family row is 70)")

# ---------------------------------------------------------------- 1-3. projectile speed (spec 3, 4, 5)
S = "spec 3 final missile speed"
setf(FAM, "agm_114_hellfire", "projectileSpeed", 70, S + ": Hellfire family (hellfire_standoff, hellfire_volley, drone_missile)")
setf(FAM, "9m133_kornet", "projectileSpeed", 70, S + ": Kornet family (tower/twin/top/multi/one-shot, atgm_heavy, boss_missiles + copies)")
setf(W, "atgm", "projectileSpeed", 70, S + ": TOW family (BGM-71 TOW-2)")
setf(W, "gun_launched_atgm", "projectileSpeed", 70, S + ": gun-launched ATGM")
setf(W, "pt14_th_jagm", "projectileSpeed", 70, S + ": JAGM = Hellfire family (own line over drone_missile)")
setf(W, "vikhr", "projectileSpeed", 75, S + ": Vikhr")
setf(W, "maverick", "projectileSpeed", 75, S + ": Maverick")
setf(W, "kh29", "projectileSpeed", 75, S + ": Kh-29")
setf(FAM, "apkws", "projectileSpeed", 80, S + "/4: APKWS family row (the runtime source)")
setf(W, "apkws_rocket", "projectileSpeed", 80, S + "/4: APKWS own line kept equal to its family row")
setf(FAM, "nsm_oniks", "projectileSpeed", 80, S + ": anti-ship family row (the runtime source)")
setf(W, "anti_ship_missile", "projectileSpeed", 80, S + ": anti-ship own line kept equal to its family row")
setf(W, "pt14_hp_nsm", "projectileSpeed", 80, S + ": anti-ship (Hyperion's NSM, own line over anti_ship_missile)")
setf(W, "scylla_kh35", "projectileSpeed", 80, S + ": anti-ship (Scylla's Kh-35, own line over anti_ship_missile)")
setf(W, "stinger_atas", "projectileSpeed", 90, S + ": Stinger ATAS")
setf(W, "stinger_post", "projectileSpeed", 90, S + ": Stinger (MANPADS post)")
setf(W, "igla_v", "projectileSpeed", 90, S + ": Igla-V")
setf(W, "r60", "projectileSpeed", 95, S + ": R-60")
setf(FAM, "aim_9_sidewinder", "projectileSpeed", 100, S + ": AIM-9 / WVR family row (wvr_aam)")
setf(W, "sam", "projectileSpeed", 100, S + ": generic SHORAD")
setf(W, "tamir", "projectileSpeed", 105, S + ": Tamir")
setf(W, "missile_57e6", "projectileSpeed", 110, S + ": Pantsir 57E6")
setf(W, "air_to_air", "projectileSpeed", 120, S + ": AMRAAM")
setf(FAM, "9m317_buk", "projectileSpeed", 120, S + ": Buk player family row (buk_launcher, sam_long)")
setf(FAM, "mim_104_patriot_pac_2", "projectileSpeed", 130, S + ": Patriot player family row (patriot, sam_battery_lrr)")
setf(W, "sam_pac3", "projectileSpeed", 130, S + ": Patriot player (PAC-3 branch, own line over sam_battery)")
setf(W, "sam_48n6", "projectileSpeed", 140, S + ": S-400 / 48N6")
X = "spec 3 boss-specific intentional exception (KEEP, restored)"
setf(W, "sam_post", "projectileSpeed", 80, X + ": boss/ship sam_post Buk")
setf(W, "sam_battery", "projectileSpeed", 95, X + ": Nemesis sam_battery Patriot (nuke_train only)")
R = "spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored)"
for wid in ("boss_rockets", "p26_behemoth_be_rockets", "p26_jotunn_jo_rockets", "p26_nemesis_sec_boss_rockets", "pt14_train_grad"):
    setf(W, wid, "projectileSpeed", 65, R)
setf(W, "pt14_ixion_grad", "projectileSpeed", 65, R + ": Ixion's Grad (own line; it opted out of the Grad family)", )
setf(W, "hover_rockets", "projectileSpeed", 65, R + ": landing hovercraft's 140 mm boss barrage (85 was outside the 65-80 boss band)")

# ---------------------------------------------------------------- 4. bombs (spec 8) and aircraft (spec 9)
mul(W, "jet_bombs", "damage", 1.25, "spec 8 conventional aircraft bomb (FAB-250)")
mul(W, "bomber_payload", "damage", 1.30, "spec 8 heavy-bomber conventional payload (FAB-500)")
mul(W, "stealth_payload", "damage", 1.20, "spec 8 guided bomb / JDAM (GBU-31)")
mul(W, "guided_bomb", "damage", 1.20, "spec 8 guided bomb (GBU-39 SDB)")
A = "spec 9 aircraft HP"
for vid in ("fighter_jet", "stealth_fighter", "attack_jet", "elite_attack_jet", "stealth_naval_strike"):
    mul(V, vid, "hp", 1.15, A + ": fighter / attack jet / stealth fighter")
for vid in ("attack_helicopter", "elite_attack_helicopter", "scout_heli"):
    mul(V, vid, "hp", 1.15, A + ": attack / scout helicopter")
for vid in ("twin_rotor_gunship", "sky_gunship"):
    mul(V, vid, "hp", 1.15, A + ": heavy / twin-rotor gunship")
for vid in ("heavy_bomber", "stealth_bomber"):
    mul(V, vid, "hp", 1.20, A + ": heavy bomber")
mul(V, "swarm_carrier", "hp", 1.15, A + ": large airborne carrier")
G = "spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon)"
for wid, nd in (("hellfire_standoff", 0), ("hellfire_volley", 0), ("apkws_rocket", 0), ("kh29", 0),
                ("heli_gun", 1), ("heli_rockets", 1), ("minigun", 1), ("scout_rockets", 1), ("jet_cannon", 1), ("s8_pods", 1)):
    mul(W, wid, "damage", 1.08, G, nd)
# Boss copies that inherit a buffed aircraft gun keep their damage (boss damage KEEP): pinned on their own lines.
setf(W, "boss_heli_gun", "damage", 22, "spec 13 boss damage KEEP: pinned (it inherits heli_gun, which the aircraft pass raises)")
setf(W, "boss_minigun", "damage", 5.5, "spec 13 boss damage KEEP: pinned (it inherits minigun, which the aircraft pass raises)")
mul(V, "sky_gunship", "outgoingDamageMult", 1.08, "spec 9 ground-attack output: sky gunship (all three guns ground attack; gunship_105 is shared with a boss part)", 4)

# ---------------------------------------------------------------- 5. ground vehicles (spec 10)
GV = "spec 10 ground"
for vid in ("main_battle_tank", "elite_mbt", "next_gen_tank"):
    mul(V, vid, "hp", 1.05, GV + ": Main Battle Tank HP")
for vid in ("heavy_tank", "elite_heavy_tank"):
    mul(V, vid, "hp", 1.08, GV + ": Heavy Tank HP")
mul(V, "heavy_tank", "outgoingDamageMult", 1.05, GV + ": Heavy Tank damage", 4)
setf(V, "elite_heavy_tank", "outgoingDamageMult", 1.05, GV + ": Heavy Tank damage (x1.05; the elite had no own multiplier)")
for vid in ("tank_destroyer", "elite_tank_destroyer"):
    mul(V, vid, "hp", 1.05, GV + ": Tank Destroyer HP")
mul(V, "flame_tank", "hp", 1.08, GV + ": Flame Tank HP")
for vid in ("armored_bulldozer", "engineer_vehicle", "demolition_line_vehicle"):
    mul(V, vid, "hp", 1.10, GV + ": breacher / bulldozer / engineer assault HP")

# ---------------------------------------------------------------- 6. towers (spec 11) and structures (spec 12)
T = "spec 11 tower"
for vid in ("guard_tower", "mg_bunker", "recoilless_gun_tower"):
    mul(V, vid, "hp", 1.20, T + ": small combat HP")
for vid, has in (("guard_tower", False), ("mg_bunker", True), ("mg_bunker.twin", True), ("mg_bunker.flame", True), ("recoilless_gun_tower", False)):
    if has:
        mul(V, vid, "outgoingDamageMult", 1.08, T + ": small combat damage", 4)
    else:
        setf(V, vid, "outgoingDamageMult", 1.08, T + ": small combat damage (x1.08)")
for vid in ("atgm_tower", "gun_turret", "rocket_turret", "one_shot_atgm_tower"):
    mul(V, vid, "hp", 1.25, T + ": medium combat HP")
    setf(V, vid, "outgoingDamageMult", 1.1, T + ": medium combat damage (x1.10)")
for vid in ("heavy_turret", "heavy_turret.bastion", "drone_hangar"):
    mul(V, vid, "hp", 1.30, T + ": large combat HP")
for vid in ("heavy_turret", "drone_hangar"):
    setf(V, vid, "outgoingDamageMult", 1.1, T + ": large combat damage (x1.10)")
mul(V, "aa_turret", "hp", 1.20, T + ": AA gun / SAM tower, small (HP by size, damage KEEP)")
mul(V, "manpads_tower", "hp", 1.20, T + ": SAM tower, small (HP by size, damage KEEP)")
mul(V, "aa_gun_tower", "hp", 1.25, T + ": AA gun tower, medium (HP by size, damage KEEP)")
mul(V, "missile_battery", "hp", 1.30, T + ": SAM tower, large (HP by size, damage KEEP)")
for vid in ("c_ram", "laser_ad_station", "drone_net_tower"):
    mul(V, vid, "hp", 1.15, T + ": C-RAM / laser / point defence HP (raw damage KEEP)")
for vid in ("ew_tower", "flare_tower", "flare_searchlight_tower", "barrage_balloon"):
    mul(V, vid, "hp", 1.15, T + ": EW / radar / flare utility HP")
ST = "spec 12 structure"
for vid in ("airfield", "repair_bay", "logistics_station", "vehicle_hangar", "aircraft_hangar", "cp_relay", "targeting_station"):
    mul(V, vid, "hp", 1.20, ST + " HP")
mul(V, "fire_control_centre", "hp", 1.25, ST + " HP: fire control centre")
mul(V, "super_gun", "hp", 1.15, ST + " HP: super gun (destructible objective)")
mul(V, "headquarters", "hp", 1.05, ST + " HP: HQ (its three HQ types inherit it)")
for vid in ("shield_tower", "shield_tower.ward"):
    mul(V, vid, "hp", 1.10, ST + " HP: Shield Tower body (dome / ward pool KEEP)")

# ---------------------------------------------------------------- 7. bosses (spec 13)
root = doc.data()
for v in root["vehicles"]:
    boss = v.get("boss") is True or isinstance(v.get("variantOf"), str) or "frame" in v or "rank" in v
    if not boss:
        continue
    rank = v.get("rank") or ("mini" if v.get("variantOf") else "main")
    mul(V, v["id"], "hp", 1.08 if rank == "main" else 1.05, f"spec 13 {rank} boss hull HP (armour KEEP)")
mul(V, "nyx", "outgoingDamageMult", 1.10, "spec 13 Nyx outgoing damage", 4)
mul(V, "nyx", "damage", 1.10, "spec 13 Nyx outgoing damage: its Tomahawk cruise strike (laid by NavalSystem, outside outgoingDamageMult)", sub="cruise")
mul(V, "scylla", "outgoingDamageMult", 1.08, "spec 13 Scylla outgoing damage", 4)
mul(V, "scylla", "damage", 1.08, "spec 13 Scylla outgoing damage: its Kalibr cruise strike (laid by NavalSystem, outside outgoingDamageMult)", sub="cruise")

# ---------------------------------------------------------------- 8. fire support (spec 14, 15)
FS = "spec 14 fire support"
mul(W, "mortar_120", "damage", 1.10, FS + ": 120 mm mortar damage")
mul(W, "amos_120", "damage", 1.10, FS + ": AMOS damage (salvo, cooldown KEEP)")
# 240 mm: the family row holds the splash (it beats the weapon's own line); the boss mortar keeps 9 m on a row of its own.
fam = doc.entry(FAM, "2b8_240_mm")
boss_row = J.Entry(fam.text)
boss_row.set("id", "2b8_240_mm_boss")
doc.insert_after(FAM, "2b8_240_mm", boss_row.text)
LOG.append({"section": FAM, "id": "2b8_240_mm_boss", "field": "(new row)", "old": None, "new": json.loads(J.strip_comments(boss_row.text)),
            "why": "spec 13/14: boss_mortar keeps its 9 m splash (boss damage KEEP) when the 240 mm row goes to 10 m"})
setf(W, "boss_mortar", "weaponFamily", "2b8_240_mm_boss", "spec 13 boss damage KEEP: boss_mortar off the player 240 mm row (same speed, model, 9 m)")
setf(FAM, "2b8_240_mm", "splash", 10, FS + ": 240 mm splash 9 -> 10 (mortar_240, siege_mortar_240; damage KEEP)")
for fid in ("m284_155_mm_2", "m284_155_mm_ext", "m284_155_mm_fixed"):
    mul(FAM, fid, "splash", 1.10, FS + ": howitzer effective splash (family row; raw damage, Pen KEEP)", 1)
mul(W, "howitzer_fixed", "edge", 1.10, FS + ": howitzer two-layer edge (howitzer_ext inherits it)", 1)
# Guided artillery splash KEEP: the guided rounds' family rows carry no splash, so they inherit their gun's: pinned.
# Guided artillery splash KEEP: their own family rows (secondRounds.families) hold 7 m; the fixed guided round inherits its
# gun's two-layer edge, so it is pinned on its own line.
nset("howitzer_fixed_guided", "edge", 14, "spec 14 guided artillery splash KEEP: edge pinned (it inherits howitzer_fixed's edge, raised)")
mul(W, "gun_203_siege", "splash", 1.10, FS + ": heavy 203 mm howitzer splash (own line, no family)", 1)
# Standard MLRS (the mlrs card's M31 salvo) on a row of its own: the GMLRS tower branch keeps 4.5 m (it takes the tower damage buff).
fam = doc.entry(FAM, "m31_gmlrs_227_mm")
mlrs_row = J.Entry(fam.text)
mlrs_row.set("id", "m31_gmlrs_227_mm_mlrs")
mlrs_row.set("splash", 4.9)
doc.insert_after(FAM, "m31_gmlrs_227_mm", mlrs_row.text)
LOG.append({"section": FAM, "id": "m31_gmlrs_227_mm_mlrs", "field": "(new row)", "old": None, "new": json.loads(J.strip_comments(mlrs_row.text)),
            "why": "spec 14 standard MLRS coverage +9 % (splash 4.5 -> 4.9); turret_gmlrs (tower) stays on m31_gmlrs_227_mm"})
setf(W, "mlrs_rockets", "weaponFamily", "m31_gmlrs_227_mm_mlrs", FS + ": MLRS card salvo on its own row (coverage)")
mul(W, "grad_cluster", "radius", 1.10, FS + ": cluster MLRS coverage +10 % (bomblet damage KEEP)", 1, sub="cluster")
mul(W, "mlrs_elite", "radius", 1.10, FS + ": cluster MLRS coverage +10 % (bomblet damage KEEP)", 1, sub="cluster")
# Artillery Barrage support card: coverage lever only (blast radius x1.10; a hit counts out to blast + the target's hull,
# so +5 % radius gave only +5 % in the headless measure, +10 % radius gives about +10 %); the scripted barrages get a
# separate event support with the old values.
old = doc.entry(SUP, "artillery_barrage")
scripted = J.Entry(old.text)
scripted.set("id", "scripted_barrage")
scripted.set("event", True, after="pen")
scripted.remove("cp")
doc.insert_after(SUP, "hq_barrage", scripted.text)
LOG.append({"section": SUP, "id": "scripted_barrage", "field": "(new event support)", "old": None, "new": json.loads(J.strip_comments(scripted.text)),
            "why": "spec 15: scripted campaign / battle-event / siege barrages keep the old artillery_barrage values"})
setf(SUP, "artillery_barrage", "blast", 7.7, "spec 15 artillery_barrage ~+10 % total strike value: blast radius 7 -> 7.7 (coverage lever only; measured +9.9 % on a 4-IFV group, +10.7 % on a spread group, +13.7 % on one tank); count, damage, cooldown KEEP")

doc.save()
out = sys.argv[sys.argv.index("--log") + 1] if "--log" in sys.argv else os.path.join(ROOT, "Docs/balance/balance_final_changes.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(LOG, f, indent=1, ensure_ascii=False)
print("changes", len(LOG), "->", out)
