"""Full fix prompt L1: the audit of every weapon (DECISIONS "Sửa lỗi tổng hợp L1"). Report only: it changes no data.

    python Tools/balance/full_weapon_audit.py              # writes Docs/checks/full_weapon_audit.md
    python Tools/balance/full_weapon_audit.py --baseline   # also stores today's flag counts as "before"
                                                           # (Tools/balance/full_weapon_audit_before.json)

Every weapon line of balance.json (bosses, player vehicles, towers and structures; the support cards in their own
table), against (a) the sheet "Vũ khí đề xuất" of Docs/balance/Machine_Brigade_Can_bang.xlsx (wave 1: mode, rounds a
second, rounds a magazine or salvo, the pause) and (b) the real system's rate of fire (REAL below, each with its source).
The wave 2 balance files are not a source for the cadence (they only give DPS a vehicle).

Per weapon: id, real name, weaponFamilyId, calibre or warhead (data / card), mode, rounds a cycle, the interval inside the
salvo, the pause, the full cycle, the sustained DPS (a cycle's rounds over the cycle, every barrel of a SIMULTANEOUS gun,
a launcher's reload counted), against (a) and (b), and which prompts touched it.

The six flags (the prompt's L1):
  TOO FAST   the time a barrel takes for one round (cycle x barrels / rounds; a salvo's own interval too) under 0.6 x the
             real gap between two rounds at the real maximum rate; for guns other than machine guns, autocannons and AA
             guns the real gap first gets the game's rule "30 % slower" (x 1 / 0.7).
  TOO SLOW   over 2 x the same reference (machine guns, autocannons and AA guns: their practical rate, since they fire in
             bursts; rockets: the ripple interval only; aircraft stores: never, they rearm on the field).
  UNIT       rounds a minute read as a second (a 40-80 x gap), a salvo whose pause is shorter than its own interval
             (interval and cycle swapped), or a twin / triple gun fired as one barrel (the barrels counted once).
  WAVE 1     the cycle (or the rounds a cycle) more than 20 % off the wave 1 proposal with no reason recorded.
  FAMILY     the same real weapon (its variant aside) with a different damage, core, edge, speed or damage type on two bosses.
  DISPLAY    the card's calibre or cadence differs from the data (the card is read the way the C# reads it today).
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import p26_ab as A  # noqa: E402
import p34_families as F  # noqa: E402
import steps_c as S  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

ROOT = F.ROOT
SHEET = os.path.join(ROOT, "Docs", "balance", "Machine_Brigade_Can_bang.xlsx")
REPORT = os.path.join(ROOT, "Docs", "checks", "full_weapon_audit.md")
BEFORE = os.path.join(HERE, "full_weapon_audit_before.json")
REASONS = os.path.join(HERE, "fix_weapon_reasons.json")   # written by fix_boss_weapons.py (L3): {weapon: reason}
HUD = os.path.join(ROOT, "Assets", "MachineBrigade", "Scripts", "Game", "Hud")

FLAGS = ("TOO FAST", "TOO SLOW", "UNIT", "WAVE 1", "FAMILY", "DISPLAY")
SLOWER = 0.7          # the game's rule: guns other than MGs, autocannons and AA fire 30 % slower than real
FAST, SLOW = 0.6, 2.0

# ------------------------------------------------------------------------------------------------ (b) the real rates
# (pattern on the real name, lower case; rounds a minute at the maximum rate, a gun / tube / rail; practical rate or None;
#  kind; mount: guns on the mount when the name does not say "twin" / "triple" / "quad"; source)
# kind: mg, ac (autocannon, grenade MG), aa (AA gun), gun (tank gun, howitzer, mortar, naval gun: the 30 % rule),
#       rocket (the ripple), missile, bomb, drone. Sources: manufacturers' and armies' figures as given in Jane's and the
#       Wikipedia articles named (read 2026-10-02); "est." where no figure is published.
REAL = [
    (r"m2 browning", 600, 40, "mg", 1, "US Army FM 3-22.65: cyclic 450-600, rapid 40 rpm"),
    (r"\bm3p?\b 12\.7", 1200, 200, "mg", 1, "Wikipedia 'M3 Browning' (AN/M3): 1,100-1,250 rpm"),
    (r"nsv 12\.7", 800, 100, "mg", 1, "Wikipedia 'NSV machine gun': 700-800 cyclic, 100 practical"),
    (r"pkt|m240", 800, 250, "mg", 1, "Wikipedia 'PK machine gun' (PKT 700-800, practical 250); M240 650-950"),
    (r"gshg 7\.62", 6000, None, "mg", 1, "Wikipedia 'GShG-7.62': 3,500 / 6,000 rpm"),
    (r"m134", 6000, None, "mg", 1, "Wikipedia 'M134 Minigun': 2,000-6,000 rpm (3,000 on helicopters)"),
    (r"mk 19", 375, 60, "ac", 1, "US Army FM 3-22.27: 325-375 cyclic, 60 rapid"),
    (r"m242", 500, 200, "ac", 1, "Wikipedia 'M242 Bushmaster': 200 or 500 rpm"),
    (r"2a42", 800, 300, "ac", 1, "Wikipedia '2A42': 550-800 high, 200-300 low rpm"),
    (r"2a38", 2500, 1000, "aa", 2, "Wikipedia '2A38': 4,060-5,000 rpm the twin mount"),
    (r"ak-630", 5000, 1000, "aa", 1, "Wikipedia 'AK-630': 4,000-5,000 rpm, 2,000-round belt"),
    (r"au-220|2a91|2a87", 120, 80, "ac", 1, "Wikipedia 'AU-220M': 80-120 rpm"),
    (r"57 mm \(2a91\)", 120, 80, "ac", 1, "Wikipedia 'AU-220M' (2A91): 120 rpm"),
    (r"s-60 57", 120, 70, "aa", 1, "Wikipedia 'AZP S-60': 105-120 cyclic, 70 practical"),
    (r"bofors l/60|l/60 40", 120, 80, "aa", 1, "Wikipedia 'Bofors 40 mm L/60': 120 rpm"),
    (r"bofors", 330, 120, "aa", 1, "Wikipedia 'Bofors 40 mm L/70': 240-330 rpm"),
    (r"gau-12", 4200, None, "ac", 1, "Wikipedia 'GAU-12 Equalizer': 3,600-4,200 rpm (1,800 on the AC-130U)"),
    (r"gau-22", 3300, None, "ac", 1, "Wikipedia 'GAU-22/A': 3,300 rpm"),
    (r"gau-8", 3900, None, "ac", 1, "Wikipedia 'GAU-8 Avenger': 3,900 rpm"),
    (r"gsh-23", 3400, None, "ac", 1, "Wikipedia 'Gryazev-Shipunov GSh-23': 3,000-3,400 rpm (GSh-23V)"),
    (r"gsh-30-2", 3000, None, "ac", 1, "Wikipedia 'GSh-30-2': 3,000 rpm"),
    (r"gsh-30k", 2600, None, "ac", 1, "Wikipedia 'GSh-30-2' (GSh-30K): 2,000-2,600 rpm"),
    (r"m230", 625, 300, "ac", 1, "Wikipedia 'M230 chain gun': 625 rpm"),
    (r"phalanx|m61", 4500, None, "aa", 1, "Wikipedia 'Phalanx CIWS': 4,500 rpm (C-RAM)"),
    (r"kda 35", 550, 300, "aa", 2, "Wikipedia 'Oerlikon GDF' / 'Gepard': 2 x 550 rpm"),
    (r"skyranger|35 mm ahead", 1000, 400, "aa", 1, "Rheinmetall Skyranger 30/35: 1,000 rpm, 20-24-round AHEAD bursts"),
    (r"oerlikon 35", 550, 300, "aa", 1, "Wikipedia 'Oerlikon GDF': 550 rpm a gun (the twin: 1,100)"),
    (r"type 96 25", 260, 130, "aa", 1, "Wikipedia 'Type 96 25 mm AT/AA gun': 220-260 rpm a barrel"),
    (r"zsu-23-4", 1000, 400, "aa", 4, "Wikipedia 'ZSU-23-4 Shilka': 4 x 850-1,000 rpm"),
    (r"zu-23-2", 1000, 400, "aa", 2, "Wikipedia 'ZU-23-2': 2 x 800-1,000 rpm"),
    # tank guns
    (r"rh-120|rh 120", 8, 6, "gun", 1, "the sheet's 'Ngoài đời': Rh-120 6-8 rpm with a loader (Wikipedia 'Rheinmetall 120 mm gun')"),
    (r"2a46|125 mm smoothbore", 8, 7, "gun", 1, "Wikipedia '2A46': 7-8 rpm with the autoloader"),
    (r"2a75", 7, 7, "gun", 1, "Wikipedia '2S25 Sprut-SD': ~7 rpm"),
    (r"2a70", 10, 8, "gun", 1, "Wikipedia '2A70': 10 rpm (100 mm), BMP-3"),
    (r"2a83", 10, 8, "gun", 1, "Object 195 / T-14 152 mm, est. ~10 rpm (the sheet)"),
    (r"b-38", 7.5, 5, "gun", 1, "Wikipedia '15.2 cm/57 B-38': 5-7.5 rpm"),
    (r"centauro", 8, 6, "gun", 1, "Centauro II 120 mm, manual: 6-8 rpm (the sheet)"),
    (r"d-10", 7, 4, "gun", 1, "Wikipedia 'D-10 tank gun' (T-55): 4-7 rpm"),
    (r"\bl7\b|105 mm low-recoil", 10, 6, "gun", 1, "Wikipedia 'Royal Ordnance L7': 6-10 rpm"),
    (r"m40 106", 5, 1, "gun", 1, "Wikipedia 'M40 recoilless rifle': 1 rpm sustained, ~5 rpm short bursts"),
    (r"spg-9", 6, 4, "gun", 1, "Wikipedia 'SPG-9': 5-6 rpm"),
    (r"mt-12", 14, 6, "gun", 1, "Wikipedia 'MT-12 Rapira': 6-14 rpm"),
    (r"npzk 140", 10, 8, "gun", 1, "NPzK 140 mm (experimental), est. 10 rpm with an autoloader (Leclerc-class)"),
    # howitzers, naval guns, mortars
    (r"m284 155|smart 155|bonus", 4, 1, "gun", 1, "US Army M109A7 fact file: 4 rpm for 3 min, 1 rpm sustained"),
    (r"155 mm l/52", 10, 3, "gun", 1, "Wikipedia 'PzH 2000': 10 rpm (3 in 9 s burst)"),
    (r"crusader", 12, 6, "gun", 1, "Wikipedia 'XM2001 Crusader': 10-12 rpm"),
    (r"155 mm/60", 5, 4, "gun", 1, "Wikipedia '15.5 cm/60 3rd Year Type' (Mogami): ~5 rpm a gun"),
    (r"2a65", 8, 6, "gun", 1, "Wikipedia '2A65 Msta-B': 7-8 rpm"),
    (r"152 mm railcar", 8, 6, "gun", 1, "a 152 mm railway mount of the 2A65 class, est. 7-8 rpm"),
    (r"2a44", 2.5, 1, "gun", 1, "Wikipedia '2S7 Pion': 1.5 rpm (2S7M Malka 2.5)"),
    (r"m110 203", 2, 1, "gun", 1, "Wikipedia 'M110 howitzer': 1.5-2 rpm"),
    (r"mk 71", 12, 12, "gun", 1, "Wikipedia '8\"/55 caliber Mark 71': 12 rpm"),
    (r"mk 7 406", 2, 2, "gun", 1, "Wikipedia '16\"/50 caliber Mark 7': 2 rpm a gun"),
    (r"mk 45", 20, 16, "gun", 1, "Wikipedia '5\"/54 caliber Mark 45': 16-20 rpm"),
    (r"ak-130", 40, 20, "gun", 1, "Wikipedia 'AK-130': 10-40 rpm a barrel"),
    (r"ak-127", 30, 20, "gun", 1, "the A-192 'Armat' 130 mm class, 30 rpm (Wikipedia 'A-192')"),
    (r"ak-100", 60, 30, "gun", 1, "Wikipedia 'AK-100 (naval gun)': 60 rpm"),
    (r"a-190", 80, 40, "gun", 1, "Wikipedia 'A-190': 80 rpm"),
    (r"ks-19", 15, 10, "aa", 1, "Wikipedia 'KS-19': 15 rpm"),
    (r"m102 105", 10, 3, "gun", 1, "the sheet's 'Ngoài đời': M102 10 rpm (Wikipedia 'M102 howitzer')"),
    (r"oto melara 76", 120, 80, "gun", 1, "Wikipedia 'OTO Melara 76 mm': 80-120 rpm (Super Rapid)"),
    (r"2b11", 15, 10, "gun", 1, "Wikipedia '2B11': 15 rpm"),
    (r"amos", 13, 10, "gun", 1, "Wikipedia 'AMOS': 26 rpm the twin-barrel turret"),
    (r"2b8 240", 1, 1, "gun", 1, "Wikipedia '2S4 Tyulpan': ~1 rpm"),
    (r"super-gun 800", 0.067, 0.067, "gun", 1, "Schwerer Gustav 800 mm: ~14 rounds a day (est. 1 every 15 min)"),
    # rockets: the ripple, rounds a minute
    (r"bm-21|grad|122 mm thermobaric", 120, None, "rocket", 1, "Wikipedia 'BM-21 Grad': 40 rockets in 20 s"),
    (r"tos-1a", 240, None, "rocket", 1, "Wikipedia 'TOS-1': 24 rockets in 6-12 s"),
    (r"smerch|9m55", 19, None, "rocket", 1, "Wikipedia 'BM-30 Smerch': 12 rockets in 38 s"),
    (r"a-22 ogon", 120, None, "rocket", 1, "A-22 Ogon 140 mm (Zubr hovercraft), est. 0.5 s a rocket"),
    (r"gmlrs", 12, None, "rocket", 1, "Wikipedia 'M270 MLRS': 12 rockets in under a minute"),
    (r"hydra 70|s-8 80|apkws", 900, None, "rocket", 1, "rocket pods: ripples of 0.05-0.12 s (DECISIONS 19R)"),
    (r"type 63 107", 100, None, "rocket", 1, "Wikipedia 'Type 63 MRL': 12 rockets in 7-9 s"),
    # missiles: a launcher's (a rail's) rate
    (r"kornet", 3, 3, "atgm", 1, "Wikipedia '9M133 Kornet': 2-3 rpm"),
    (r"konkurs", 3, 2, "atgm", 1, "Wikipedia '9M113 Konkurs': 2-3 rpm"),
    (r"tow-2|bgm-71", 3, 2, "atgm", 1, "Wikipedia 'BGM-71 TOW': ~3 rpm"),
    (r"9m117|gun-launched", 4, 3, "atgm", 1, "the gun's own rate with a loaded missile, est. 4 rpm"),
    (r"ataka|khrizantema|vikhr", 4, 3, "atgm", 1, "Shturm / Ataka / Khrizantema launchers: est. 3-4 rpm a rail"),
    (r"spike nlos", 6, 4, "atgm", 1, "Spike NLOS launcher, est. 4-6 rpm"),
    (r"hellfire|griffin|maverick|kh-29|mam-l|agm-88", 60, 10, "atgm", 1, "air-launched: ripples ~1 s apart, est. 6 s an aimed shot"),
    (r"9m317|buk", 15, 15, "missile", 1, "Wikipedia 'Buk missile system': 4 s between launches"),
    (r"patriot|pac-2|pac-3", 20, 20, "missile", 1, "Wikipedia 'MIM-104 Patriot': ripples a few seconds apart (est. 3 s)"),
    (r"48n6", 20, 6, "missile", 1, "Wikipedia 'S-400': 3 s between launches"),
    (r"57e6", 40, 12, "missile", 1, "Wikipedia 'Pantsir': 2 missiles ~1.5 s apart (est.)"),
    (r"stinger|starstreak", 20, 10, "missile", 1, "Avenger / Stormer: ~3 s between rounds (est.); a MANPADS team 6-10 s"),
    (r"igla", 20, 10, "missile", 1, "air-launched Igla-V pairs, est. 3 s"),
    (r"tamir", 60, 30, "missile", 1, "Iron Dome: launches 1-2 s apart (DECISIONS 19R)"),
    (r"aim-9|aim-120|r-60|r-37", 60, None, "missile", 1, "air-to-air: ~1 s between launches (est.)"),
    (r"kalibr|jassm|kh-101|nsm|oniks|tomahawk|typhon", 20, 6, "missile", 1, "cruise missiles: ~3 s between launches (est.)"),
    (r"iskander", 2, 2, "missile", 1, "Wikipedia '9K720 Iskander': two missiles within a minute"),
    # bombs, drones: the release interval of a stick, a launcher's rate (none published: no rate flag)
    (r"fab-|gbu-|jdam|cbu-|odab|bomb-bay|bomb", 600, None, "bomb", 1, "a stick's release, 0.1 s and up (est.)"),
]
NO_RATE = {"flame", "laser", "railgun", "melee", "special", "drone"}
GUN_FAMS = {"mg", "autocannon", "tank_gun", "howitzer", "mortar", "naval_gun", "grenade", "recoilless"}
WARHEAD_FAMS = {"atgm", "aa_missile", "missile", "cruise", "cruise_missile", "ballistic", "bomb", "drone"}

# The missiles whose data "size" is the missile's own mass: their warhead (Wikipedia, read 2026-10-02).
WARHEAD = {
    "bgm-71 tow-2": 5.9, "gun-launched atgm": 4.5, "starstreak / stinger shorad": 1, "fim-92 stinger": 1, "57e6": 20,
    "agm-114 hellfire": 9, "agm-114l hellfire longbow": 9, "9m133 kornet": 7, "kornet": 7, "agm-176 griffin": 5.9,
    "kh-29l": 320, "9m120 ataka": 7.4, "9k121 vikhr": 8, "agm-65 maverick": 57, "9m113 konkurs": 2.7,
    "tamir interceptor": 11, "patriot pac-3 mse": 7, "3m-54 kalibr": 200, "agm-88 harm": 68, "nsm / p-800 oniks": 250,
    "nsm coastal defence": 120, "9m723 iskander": 480, "r-37m": 60, "9k38 igla-v": 1.2,
}
# Where the warhead figure comes from, for the card's note.
WARHEAD_NOTE = "Wikipedia (each missile's article)"


def mult_of(real: str, wid: str = "") -> int:
    r = real.lower()
    for word, n in (("quad", 4), ("triple", 3), ("twin", 2), ("2 x", 2)):
        if word in r:
            return n
    return 1


def real_entry(w):
    real = (w.get("real") or "").lower()
    for pat, rpm, prac, kind, mount, src in REAL:
        if re.search(pat, real):
            return {"rpm": rpm, "prac": prac, "kind": kind, "mount": mount, "src": src}
    return None


def caliber_of(w):
    """(calibre mm, warhead kg, power kW, energy MJ) the data means, from the explicit fields or the family and size."""
    if any(k in w for k in ("caliberMm", "warheadKg", "powerKw", "energyMj")):
        return w.get("caliberMm"), w.get("warheadKg"), w.get("powerKw"), w.get("energyMj")
    fam, size = w.get("family"), w.get("size")
    if not size:
        return None, None, None, None
    if fam in GUN_FAMS or fam == "rocket":
        return size, None, None, None
    if fam in WARHEAD_FAMS:
        base = F.real_base(w).lower()
        return None, WARHEAD.get(base, size), None, None
    if fam == "laser":
        return None, None, size, None
    if fam == "railgun":
        return None, None, None, size
    if fam == "special" and size >= 800:
        return size, None, None, None
    return None, None, None, None


# ------------------------------------------------------------------------------------------------ the numbers

def numbers(w):
    """The cadence of a resolved line: mode, rounds a cycle (all barrels), rounds a pull, interval, pause, cycle, DPS."""
    clip, burst = int(w.get("clip", 0) or 0), int(w.get("burst", 1) or 1)
    cd, bi, cr = float(w.get("cooldown", 1.0)), float(w.get("burstInterval", 0.1)), float(w.get("clipReload", 0.0))
    sim = w.get("salvoMode") == "SIMULTANEOUS"
    barrels = int(w.get("barrels", 1) or 1)
    pull = barrels if sim else 1
    if clip > 0:
        mode, n, inner, pause, cycle = "magazine", clip, cd, cr, (clip - 1) * cd + cr
    elif burst > 1:
        mode, n, inner, pause, cycle = "salvo", burst * pull, bi, cd, cd + (burst - 1) * bi
    else:
        mode, n, inner, pause, cycle = "single", pull, None, cd, cd
    cycle = max(0.05, cycle)
    dmg = float(w.get("damage", 0) or 0)
    ammo = int(w.get("ammo", 0) or 0)
    dps = dmg * n / cycle
    if ammo > 0:
        dps = dmg * n * ammo / (cycle * ammo + float(w.get("reload", 0.0)))
    return {"mode": mode, "n": n, "pull": pull, "inner": inner, "pause": pause, "cycle": cycle, "dps": dps,
            "barrels": barrels, "sim": sim, "ammo": ammo, "load": int(w.get("load", 0) or 0)}


def flags_rate(w, nb, real):
    """TOO FAST / TOO SLOW / UNIT from (b). Returns (flags, the reference in words, ratio)."""
    out, note = [], ""
    if real is None or w.get("family") in NO_RATE or w.get("laid") and w.get("family") in ("special", "cruise", "cruise_missile"):
        return out, "no real rate", None
    kind = real["kind"]
    one_shot = float(w.get("clipReload", 0) or 0) >= 1e5
    mount = max(real["mount"], mult_of(w.get("real") or ""))
    if kind == "atgm":
        mount = max(mount, nb["n"] if nb["mode"] == "salvo" and nb["n"] <= 4 else 1)   # a twin or quad launcher's rails
    guns = nb["barrels"] if nb["sim"] else mount   # the barrels the data's rounds come out of
    gap = 60.0 / real["rpm"]                        # one barrel's real gap at the maximum rate
    ref = gap / SLOWER if kind == "gun" else gap
    prac_rpm = real.get("prac") or (real["rpm"] / 10.0 if kind in ("mg", "ac", "aa") else real["rpm"])
    prac = 60.0 / prac_rpm / (SLOWER if kind == "gun" else 1.0)
    per = nb["cycle"] * guns / max(1, nb["n"])      # the game's time a barrel takes for one round
    if nb["ammo"] > 0:
        per = (nb["cycle"] * nb["ammo"] + float(w.get("reload", 0.0))) * guns / max(1, nb["n"] * nb["ammo"])
    # Inside a salvo a barrel fires twice only when the salvo has more rounds than barrels (a twin launcher's pair is one each).
    inner = nb["inner"] * guns / max(1, nb["pull"]) if nb["inner"] and nb["n"] > guns else None
    if nb["mode"] == "magazine" or kind in ("mg", "ac", "aa"):  # a stream's barrels take turns
        inner = nb["inner"] * mount if nb["inner"] else None
    note = f"{real['rpm']:g} rpm{' x' + str(mount) if mount > 1 else ''}"
    ratio = per / ref
    if kind == "rocket":
        if inner is not None:
            ratio = inner / ref
            if inner < FAST * ref:
                out.append("TOO FAST")
            elif inner > SLOW * ref:
                out.append("TOO SLOW")
        return out, note + " (ripple)", ratio
    fast = per < FAST * ref or (inner is not None and inner < FAST * ref)
    if nb["load"] > 0 or kind == "bomb" or one_shot:
        # aircraft stores, bombs, a one-shot site: only the salvo's own interval (they rearm over the field)
        fast = inner is not None and inner < FAST * ref
        if fast:
            out.append("TOO FAST")
        return out, note + " (stores)", (inner / ref if inner else None)
    if fast:
        out.append("TOO FAST")
    slow_ref = prac if kind in ("mg", "ac", "aa", "missile", "atgm") else ref
    if per > SLOW * slow_ref:
        out.append("TOO SLOW")
    # UNIT: a 60 x gap; a salvo's pause shorter than its own interval; a twin / triple single gun fired as one barrel.
    if nb["n"] == 1 and (40 <= ratio <= 80 or 1 / 80 <= ratio <= 1 / 40):
        out.append("UNIT")
    elif nb["mode"] == "salvo" and nb["pause"] < nb["inner"] - 1e-6:
        out.append("UNIT")
    elif kind == "gun" and mult_of(w.get("real") or "", w["id"]) > 1 and not nb["sim"] and nb["n"] == 1:
        out.append("UNIT")
    return out, note, ratio


# ------------------------------------------------------------------------------------------------ (a) the sheet

# Weapons that are not in the sheet under their own id: the wave 1 row of the same real weapon.
SHEET_ALIAS = {
    "p26_behemoth_main_be152": "gun_behemoth", "p26_behemoth_tiny_be120": "gun_120mm", "p26_behemoth_direct_be120": "gun_120mm",
    "p26_behemoth_tiny_boss_missiles": "boss_missiles", "p26_behemoth_tiny_kornet_twin": "kornet_twin",
    "p26_bastion_tiny_kornet_twin": "kornet_twin", "p26_matriarch_direct_ma_atgm": "boss_missiles",
    "p26_roc_direct_roc_atgm": "boss_missiles", "p26_behemoth_sec_be_rockets": "boss_rockets",
    "p26_nemesis_sec_boss_rockets": "boss_rockets", "p26_kronos_close_boss_rockets": "boss_rockets",
    "p26_jotunn_jo203": "boss_howitzer", "p26_jotunn_sec_jo_rockets": "rockets_300mm", "p26_jotunn_direct_jo125": "gun_125_elite",
    "p26_nemesis_direct_ne125": "gun_125_elite", "p26_ixion_125": "gun_125_elite", "p26_jotunn_tiny_twin_30_flak": "twin_30_flak",
    "p26_matriarch_tiny_mothership_cannon": "mothership_cannon",
    "p26_matriarch_sec_autocannon_30": "autocannon_30", "p26_kronos_close_autocannon_30": "autocannon_30",
    "p26_nemesis_main_ne152": "gun_152_he", "p26_icarus_sec_orbital_laser": "orbital_laser",
    "p26_icarus_close_autocannon_40": "autocannon_40", "p26_bastion_sec_b240": "boss_mortar",
    "p26_bastion_tiny_autocannon_40": "autocannon_40", "p26_bastion_close_boss_hmg": "boss_hmg", "p26_bastion_main_b155": "casemate_155",
    "p26_bastion_tiny_zu23": "zu23", "p26_moloch_tiny_zu23": "zu23", "p26_roc_close_twin_30_bmpt": "twin_30_bmpt",
    "p26_roc_roc105": "gunship_105", "p26_leviathan_sec_lev155": "naval_155_triple", "p26_moloch_main_mo120": "gun_120mm",
    "p26_moloch_direct_mo120ap": "gun_120mm", "p26_daedalus_sec_dae57": "mothership_cannon", "p26_kronos_direct_kr57": "mothership_cannon",
    "p26_typhon_sec_ty57": "mothership_cannon", "p26_typhon_direct_ty100": "naval_100", "p26_ixion_mg": "boss_hmg",
}


# One real weapon whose boss lines may differ (FAMILY), with the reason: left out of the family check, listed in the report.
FAMILY_EXCEPT = {
    "autocannon_40": "Gungnir's own 40 mm guns (their 1 m burst): Gungnir is frozen but for its main gun's name (fix rule 8)",
    "gunship_105": "the player's AC-130 gun, carried by Sky Fortress too: player weapons wait for the owner",
}


def load_sheet():
    try:
        import openpyxl
    except ImportError:
        return {}
    wb = openpyxl.load_workbook(SHEET, data_only=True, read_only=True)
    ws = wb["Vũ khí đề xuất"]
    out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]:
            continue
        mode, rps, n, pause = r[12], r[14], r[16], r[18]
        try:
            rps, n, pause = float(rps or 0), int(n or 1), float(pause or 0)
        except (TypeError, ValueError):
            continue
        if mode == "từng phát" or n <= 1:
            cycle = pause
        else:
            cycle = (n - 1) / rps + pause if rps > 0 else pause
        out[r[0]] = {"real": r[1], "mode": mode, "rps": rps, "n": max(1, n), "pause": pause, "cycle": cycle,
                     "damage": r[10], "src": r[38]}
    return out


def sheet_row(sheet, ws, wid):
    if wid in sheet:
        return wid, sheet[wid]
    a = SHEET_ALIAS.get(wid)
    if a and a in sheet:
        return a, sheet[a]
    raw = ws.raw.get(wid, {})
    seen = 0
    while raw.get("inherits") and seen < 5:
        p = raw["inherits"]
        if p in sheet:
            return p, sheet[p]
        raw = ws.raw.get(p, {})
        seen += 1
    return None, None


# ------------------------------------------------------------------------------------------------ the card

def card_reads_fields():
    """True once the card reads caliberMm / warheadKg (L2) instead of the id's digits."""
    try:
        with open(os.path.join(HUD, "WeaponInfo.cs"), encoding="utf-8") as fh:
            return "CaliberMm" in fh.read()
    except OSError:
        return False


def card_shows_cycle():
    """True once the detail page's weapon line shows the full cycle (L3)."""
    try:
        with open(os.path.join(HUD, "MenuScreen.Detail.cs"), encoding="utf-8") as fh:
            return "CycleSeconds" in fh.read()
    except OSError:
        return False


GUN_KINDS = ("gun", "autocannon", "howitzer", "mortar", "rockets")


def card_kind(w):
    """WeaponInfo.Kind's kind, as the C# works it out."""
    wid, proj = w["id"], w.get("projectile", "Shell")
    fam = w.get("family")
    if fam == "laser" and card_reads_fields():
        return "laser"
    if proj == "Flame":
        return "flame"
    if proj == "Bomb":
        return "guidedbomb" if "guided" in wid else "bombs"
    if proj == "Drone":
        return "drones"
    if proj == "Missile":
        return "ballistic" if "ballistic" in wid else ("sam" if w.get("targets") == "Air" else "atgm")
    if proj == "Rocket":
        return "thermobaric" if "thermobaric" in wid else ("rockets" if w.get("minRange", 0) > 0 or w.get("indirect") else "rocketpod")
    if proj == "Bullet":
        if any(k in wid for k in ("autocannon", "flak", "gunship_25", "gunship_40", "fighter_cannon", "jet_cannon", "heli_gun")):
            return "autocannon"
        if "agl" in wid:
            return "grenades"
        if any(k in wid for k in ("hmg", "minigun", "gatling", "gau", "tail_guns")):
            return "hmg"
        return "mg"
    if "mortar" in wid:
        return "mortar"
    return "howitzer" if (w.get("minRange", 0) > 0 or "howitzer" in wid) else "gun"


def card_calibre(w, cal):
    """The calibre the card prints: the id's digits today (WeaponInfo.Calibre), the data's field after L2."""
    kind = card_kind(w)
    if card_reads_fields():
        c, k, kw, mj = cal
        if c:
            return f"{c:g} mm"
        if k:
            return f"{k:g} kg"
        if kw:
            return f"{kw:g} kW"
        return ""
    m = re.search(r"(\d{2,3})", w["id"])
    if m and int(m.group(1)) >= 20 and kind in GUN_KINDS:
        return m.group(1) + " mm"
    return ""


def card_seconds(w, nb):
    """The "every X s" the detail page prints: the pause after the last round today, the full cycle after L3."""
    if card_shows_cycle():
        return nb["cycle"]
    return float(w.get("clipReload", 0.0)) if int(w.get("clip", 0) or 0) > 0 else float(w.get("cooldown", 1.0))


# ------------------------------------------------------------------------------------------------ users

def users(data, built):
    """{weapon: [(group, unit, mount)]}: group boss / player / tower (towers, structures, utility modules)."""
    ids = {w["id"] for w in data["weapons"]}
    out = collections.defaultdict(list)
    for bid, b in built.items():
        for k, wid in enumerate(S.mounts_of(b)):
            if wid:
                out[wid].append(("boss", bid, k))
        for key in ("salvo", "cruise", "bombard"):
            if isinstance(b.get(key), dict) and b[key].get("weapon"):
                out[b[key]["weapon"]].append(("boss", bid, key))

    def strings(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k != "id":
                    yield from strings(v)
        elif isinstance(node, list):
            for v in node:
                yield from strings(v)
        elif isinstance(node, str):
            yield node

    for v in data["vehicles"]:
        if v["id"] in built:
            continue
        group = "tower" if "fort" in v or (v.get("inherits") and "." in v["id"]) else "player"
        mounts = [v.get("weapon")] + [m.get("weapon") for m in v.get("secondary") or []]
        for k, wid in enumerate(mounts):
            if wid:
                out[wid].append((group, v["id"], k))
        for s in set(strings(v)) - set(mounts):
            if s in ids:
                out[s].append((group, v["id"], "other"))
    return out


def touched(wid, raw, p34_base, barrels_ids):
    t = []
    if wid.startswith("p26_"):
        t.append("26 B")
    if raw.get("weaponFamilyId") or raw.get("weaponVariantId"):
        t.append("34 L1")
    if wid in p34_base:
        t.append("34 L2")
    if wid in barrels_ids:
        t.append("34 L4")
    for k in ("caliberMm", "warheadKg", "powerKw", "energyMj"):
        if k in raw:
            t.append("fix L2")
            break
    return t


# ------------------------------------------------------------------------------------------------ the audit

def audit(data):
    ws = F.Weapons(data)
    built = A.expand(data)
    us = users(data, built)
    sheet = load_sheet()
    reasons = {}
    if os.path.exists(REASONS):
        with open(REASONS, encoding="utf-8") as fh:
            reasons = json.load(fh)
    p34_base = {}
    p34 = os.path.join(HERE, "p34_boss_baseline.json")
    if os.path.exists(p34):
        with open(p34, encoding="utf-8") as fh:
            p34_base = json.load(fh)
    try:
        import p34_barrels
        barrels_ids = set(p34_barrels.TARGETS)
    except Exception:  # noqa: BLE001
        barrels_ids = set()
    rows = []
    for raw in data["weapons"]:
        wid = raw["id"]
        w = ws.resolve(wid)
        nb = numbers(w)
        real = real_entry(w)
        flags, ref, ratio = flags_rate(w, nb, real)
        sid, srow = sheet_row(sheet, ws, wid)
        wave1 = ""
        if srow:
            off = abs(nb["cycle"] / srow["cycle"] - 1) if srow["cycle"] > 0 else 0
            # A twin gun's magazine is a box a barrel (ZU-23-2: 2 x 50, prompt 35 owner decision 2): the sheet's rounds a barrel.
            n_off = srow["n"] != nb["n"] and not (srow["n"] == nb["n"] * 1 or (nb["sim"] and srow["n"] == nb["barrels"]) or
                                                  (nb["mode"] == "magazine" and srow["n"] * nb["barrels"] == nb["n"]))
            if (off > 0.2 or n_off) and wid not in reasons:
                flags.append("WAVE 1")
            wave1 = f"`{sid}`: {srow['n']} / {srow['cycle']:.2f} s"
        cal = caliber_of(w)
        u = us.get(wid, [])
        shown_cal = card_calibre(w, cal)
        want = cal[0] if cal[0] else None
        display = []
        if u and w.get("damage", 0) > 0:
            if shown_cal and want and shown_cal != f"{want:g} mm":
                display.append(f"card {shown_cal}, data {want:g} mm")
            if shown_cal and not want and shown_cal.endswith("mm"):
                display.append(f"card {shown_cal}, no calibre")
            if not card_reads_fields() and card_kind(w) == "gun" and any(m not in (0, "other") and isinstance(m, int) and m > 0 for _, _, m in u):
                display.append("'Main gun' on a side mount")
            sec = card_seconds(w, nb)
            if abs(sec - nb["cycle"]) > 0.05 * nb["cycle"] + 0.01 and w.get("family") not in ("laser",):
                display.append(f"every {sec:.2f} s shown, cycle {nb['cycle']:.2f} s")
        if display:
            flags.append("DISPLAY")
        rows.append({"id": wid, "w": w, "nb": nb, "real": real, "ref": ref, "ratio": ratio, "flags": flags, "wave1": wave1,
                     "cal": cal, "card": shown_cal, "display": display, "users": u, "touched": touched(wid, raw, p34_base, barrels_ids),
                     "reason": reasons.get(wid, "")})
    # FAMILY: the same real weapon (variant aside) differs between bosses.
    groups = collections.defaultdict(list)
    for r in rows:
        if any(g == "boss" for g, _, _ in r["users"]) and r["w"].get("damage", 0) > 0 and r["id"] not in FAMILY_EXCEPT:
            w = r["w"]
            groups[(F.real_base(w).lower(), w.get("weaponVariantId") or "")].append(r)
    for key, items in groups.items():
        sigs = {(i["w"].get("damage"), i["w"].get("splash", 0), i["w"].get("edge", 0), i["w"].get("projectileSpeed"), i["w"].get("damageType"))
                for i in items}
        if len(sigs) > 1:
            for i in items:
                i["flags"].append("FAMILY")
                i["family_note"] = "; ".join(f"`{j['id']}` {j['w'].get('damage')}/{j['w'].get('splash', 0)}/{j['w'].get('edge', 0)}/"
                                            f"{j['w'].get('projectileSpeed')}/{j['w'].get('damageType')}" for j in items)
    return rows, built, ws


def counts(rows, group=None):
    c = collections.Counter()
    for r in rows:
        if group and not any(g == group for g, _, _ in r["users"]):
            continue
        for f in set(r["flags"]):
            c[f] += 1
    return {f: c.get(f, 0) for f in FLAGS}


def fmt_cal(cal):
    c, k, kw, mj = cal
    return f"{c:g} mm" if c else f"{k:g} kg" if k else f"{kw:g} kW" if kw else f"{mj:g} MJ" if mj else "-"


def report(rows, built, ws, before):
    now = {g: counts(rows, g) for g in ("boss", "player", "tower")}
    now["all"] = counts(rows)
    out = ["# Full weapon audit (full fix prompt L1)", "",
           "Written by `Tools/balance/full_weapon_audit.py` (rerun it after any balance change). Report only. Sources: (a) the",
           "sheet \"Vũ khí đề xuất\" of `Docs/balance/Machine_Brigade_Can_bang.xlsx` (wave 1); (b) the real rates in the tool's",
           "`REAL` table, each with its source. The flags are defined at the top of the tool. A weapon carried by no unit is",
           "listed but counts in \"all\" only. The DPS is on paper (a cycle's rounds over the cycle, every barrel, a launcher's",
           "reload counted), before a boss's own factors.", "",
           "## Flag counts", "",
           "| group | " + " | ".join(FLAGS) + " |", "|---|" + "---|" * len(FLAGS)]
    for g in ("boss", "player", "tower", "all"):
        b = (before or {}).get(g)
        cells = []
        for f in FLAGS:
            cells.append(f"{b[f]} -> {now[g][f]}" if b else f"{now[g][f]}")
        out.append(f"| {g} | " + " | ".join(cells) + " |")
    if before:
        out.append("")
        out.append("Before = the counts stored with `--baseline` (L1, before L2 and L3); after = this run.")
    out += ["", "## Every weapon", "",
            "Columns: weapon (real name) | family | calibre or warhead: data / card | mode: rounds a cycle, interval, pause, cycle | "
            "sustained DPS | (b) real rate, game / reference | (a) wave 1: rounds / cycle | users | touched by | flags.", ""]
    order = {"boss": 0, "player": 1, "tower": 2}
    def key(r):
        gs = [order[g] for g, _, _ in r["users"]] or [9]
        return (min(gs), r["id"])
    for grp, title in ((0, "Boss weapons"), (1, "Player vehicles"), (2, "Towers and structures"), (9, "Carried by no unit")):
        sel = [r for r in rows if key(r)[0] == grp]
        if not sel:
            continue
        out += [f"### {title} ({len(sel)})", "",
                "| weapon | family | cal. data / card | cadence | DPS | (b) | (a) | users | touched | flags |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(sel, key=key):
            w, nb = r["w"], r["nb"]
            cad = f"{nb['mode']} {nb['n']}" + (f" x{nb['barrels']} SIM" if nb["sim"] else "")
            if nb["inner"]:
                cad += f", {nb['inner']:.3g} s"
            cad += f", +{nb['pause']:.3g} s = {nb['cycle']:.2f} s"
            rb = f"{r['ref']}" + (f", x{r['ratio']:.2f}" if r["ratio"] else "")
            if r["real"]:
                rb += f" ({r['real']['src']})"
            us = sorted({u for _, u, _ in r["users"]})
            ustr = ", ".join(us[:4]) + (f" +{len(us) - 4}" if len(us) > 4 else "")
            fl = ", ".join(sorted(set(r["flags"])))
            extra = []
            if r["display"]:
                extra.append("; ".join(r["display"]))
            if r.get("family_note") and "FAMILY" in r["flags"]:
                extra.append("family: " + r["family_note"])
            if r["reason"]:
                extra.append("reason: " + r["reason"])
            if extra:
                fl += " (" + " / ".join(extra) + ")"
            fam = (w.get("weaponFamilyId") or "") + ("/" + w["weaponVariantId"] if w.get("weaponVariantId") else "")
            out.append(f"| `{r['id']}` ({w.get('real') or '-'}) | {fam} | {fmt_cal(r['cal'])} / {r['card'] or '-'} | {cad} | "
                       f"{nb['dps']:.0f} | {rb} | {r['wave1'] or '-'} | {ustr or '-'} | {', '.join(r['touched']) or '-'} | {fl or 'ok'} |")
        out.append("")
    out += ["## Left out of the family check", ""] + [f"- `{k}`: {v}." for k, v in FAMILY_EXCEPT.items()] + [""]
    out += ["## Support cards", "", "Not weapons: a card's strike (count x damage every cooldown, blast radius). No real rate applies.", "",
            "| card | kind | count x damage | blast | cooldown |", "|---|---|---|---|---|"]
    for s in DATA["supports"]:
        if s.get("damage"):
            out.append(f"| `{s['id']}` | {s.get('kind')} | {s.get('count', 1)} x {s.get('damage')} | {s.get('blast', '-')} | {s.get('cooldown', '-')} s |")
    out.append("")
    return "\n".join(out), now


DATA = {}
WAITLIST = os.path.join(ROOT, "Docs", "balance", "player_weapon_waitlist.md")

# Why a flagged player or tower weapon is left for the owner (the player rule: fix only clear errors, keep the DPS).
WAIT_NOTES = [
    ({"gun_105_long", "gun_105_apfsds", "gun_125_elite", "gun_105_wheeled", "gun_105_bunker", "gun_203_siege", "boss_howitzer",
      "boss_mortar", "train_gun", "borer_cannon", "gunship_105", "gunship_40mm"},
     "DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage)"),
    ({"mlrs_rockets", "mlrs_elite", "rockets_300mm", "ballistic_missile", "turret_gmlrs"},
     "DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight)"),
    ({"gun_120mm", "gun_120_twin", "gun_125_armata_ke", "gun_152", "gun_152_he", "gun_152_heat", "howitzer", "howitzer_ext", "mortar_120",
      "naval_76", "gun_57mm", "buk_launcher", "sam_long", "sam_post", "kornet_twin", "tower_kornet", "kornet_multi", "kornet_top",
      "atgm_heavy", "boss_missiles", "flak_35", "twin_30_bmpt"},
     "DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call"),
    ({"howitzer_fixed", "howitzer_cb", "mortar_240_fixed", "turret_gun_120", "turret_gun_120_long", "turret_gun_120_auto", "gun_pit_105",
      "flak_88", "spg9_73mm", "gun_155_twin_fort", "gun_155_twin_ap", "gun_155_twin_coastlr", "gun_155_coastal", "gun_155_twin",
      "gun_155_twin_long", "casemate_155", "one_shot_kornet"},
     "a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose"),
    ({"patriot", "sam_battery_lrr", "sam_pac3", "tamir", "cruise_missile_ground", "jassm", "avenger_stingers", "amos_120", "caesar_155",
      "gun_155_crusader", "nsm_coastal", "anti_ship_missile", "uav_loiter_missile", "spike_nlos", "khrizantema", "vikhr",
      "hellfire_standoff", "hellfire_volley"},
     "the real reference is an estimate (no published launch interval): not a clear error"),
    ({"siege_gun_105", "siege_mortar_240", "recoilless_106", "gun_105_ags", "gun_140_twin", "gun_100_river"},
     "a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error"),
]


def wait_note(wid):
    for ids, note in WAIT_NOTES:
        if wid in ids:
            return note
    return "flagged, intent unknown: waits for the owner"


def waitlist(rows):
    out = ["# Player and tower weapons waiting for the owner (full fix prompt L3, rule 9)", "",
           "Written by `Tools/balance/full_weapon_audit.py`. The player rule: fix only clear unit errors and clear too-fast /",
           "too-slow cadences, keeping the DPS (player balance waits for prompt 29's follow-up). Changed in this pass:",
           "`turret_rockets` and `turret_rockets_cluster` (the BM-21's real 0.5 s between rockets, the cycle and the DPS kept).",
           "Everything below is still flagged by the audit and was left as it is, with the reason.", "",
           "| weapon | carriers | flags | game / reference | why left |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["id"]):
        groups = {g for g, _, _ in r["users"]}
        flags = sorted(set(r["flags"]) - {"WAVE 1", "DISPLAY", "FAMILY"})
        if not flags or "boss" in groups and not (groups - {"boss"}) or not (groups & {"player", "tower"}):
            continue
        us = sorted({u for g, u, _ in r["users"] if g != "boss"})
        ratio = f"x{r['ratio']:.2f}" if r["ratio"] else "-"
        out.append(f"| `{r['id']}` ({r['w'].get('real') or '-'}) | {', '.join(us[:4])}{' +' + str(len(us) - 4) if len(us) > 4 else ''} | "
                   f"{', '.join(flags)} | {ratio} | {wait_note(r['id'])} |")
    out.append("")
    return "\n".join(out)


def main():
    doc = Doc(F.PATH)
    data = doc.data()
    DATA.update(data)
    rows, built, ws = audit(data)
    before = None
    if os.path.exists(BEFORE) and "--baseline" not in sys.argv:
        with open(BEFORE, encoding="utf-8") as fh:
            before = json.load(fh)
    text, now = report(rows, built, ws, before)
    if "--baseline" in sys.argv:
        with open(BEFORE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(now, fh, indent=1)
    with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    with open(WAITLIST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(waitlist(rows))
    for g, c in now.items():
        print(g, " ".join(f"{k}={v}" for k, v in c.items()))
    print("written", os.path.relpath(REPORT, ROOT))


if __name__ == "__main__":
    main()
