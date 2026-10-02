"""Prompt 28: generates the AI data in balance.json from the owner's research sheet (Docs/ai/Machine_Brigade_AI_Research.xlsx).

    python Tools/ai/import_ai_xlsx.py          # rewrites the generated "ai" block of balance.json
    python Tools/ai/import_ai_xlsx.py --dry    # prints the block, writes nothing

Like Tools/balance/import_xlsx.py (prompt 25): every number comes from the sheet (openpyxl, data_only); the script holds
only the rules that map a row onto the data. The block sits between two marker comments and is replaced as a whole, so
running the script twice changes nothing the second time; nothing outside the markers is touched.

Pass 1 (DECISIONS "28 1"): the parameter frame (L.1): sheet "Tham số AI" -> ai.params, sheet "Cân bằng kinh tế" ->
ai.economy, each parameter { value, min, max, metric, reason }. Later passes add their sheets (squad states,
tactics, ...) here.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX = os.path.join(ROOT, "Docs", "ai", "Machine_Brigade_AI_Research.xlsx")
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")

BEGIN = "  // <generated ai: Tools/ai/import_ai_xlsx.py, do not edit by hand>"
END = "  // </generated ai>"
# The block's place the first time (before this section); later runs replace it where it is.
ANCHOR = '  "generals": {'

# Qualitative levels of the sheet on a weight scale (1 = the standard thresholds; DECISIONS "28 1").
LEVELS = {"thấp": 0.5, "vừa": 1.0, "cao": 1.5, "rất cao": 2.0, "theo chiến thuật": 1.0, "có": 1.0, "không": 0.0,
          "mua ngay": 0.0, "để dành tới ngưỡng": 1.0}


def num(text) -> float:
    if isinstance(text, (int, float)):
        return float(text)
    return float(str(text).strip().lstrip("~×").replace(",", "."))


def nums(text) -> list[float]:
    return [num(m) for m in re.findall(r"\d+(?:[.,]\d+)?", str(text or ""))]


def first(text) -> float:
    """The first number of a cell ('1,2 (theo chiến thuật)', '~6%/s', '×0,5'), else its level word."""
    n = nums(text)
    if n:
        return n[0]
    key = str(text).strip().lower()
    if key.startswith("bằng"):  # 'Bằng lõi nổ của vũ khí mạnh nhất đã biết': x1 of the core
        return 1.0
    if key not in LEVELS:
        sys.exit(f"Tham số AI: no rule for the value '{text}'")
    return LEVELS[key]


# Sheet row -> key, and the factor turning the sheet's unit into the data's (percent -> share).
PARAMS = [
    ("Ngưỡng tấn công", "attackThreshold", 1),
    ("Ngưỡng chuyển tuyến", "fallbackRatio", 1),
    ("Ngưỡng chênh để đổi hành động", "switchMargin", 1),
    ("Thời gian cam kết tối thiểu", "minCommit", 1),
    ("Thời gian đánh giá lại khi đứng yên", "idleReassess", 1),
    ("Thời gian kẹt trước khi xử lý", "stuckTime", 1),
    ("Hồi chiêu Emergency Reposition", "emergencyCooldown", 1),
    ("Ngưỡng địch áp đảo", "overwhelmRatio", 1),
    ("Tốc độ giảm độ tin cậy", "confidenceDecay", 0.01),
    ("Khoảng cách dàn ra trước bắn lan", "splashSpread", 1),
    ("Độ trễ phản ứng", "reactionDelay", 1),
    ("Trọng số đánh sườn", "flankWeight", 1),
    ("Trọng số dồn hỏa lực", "focusWeight", 1),
    ("Gắn kết đội", "cohesion", 1),
    ("Chuẩn bị bằng pháo", "artilleryPrep", 1),
    ("Ngưỡng đưa máy bay", "airAaLimit", 1),
    ("Giữ lửa", "holdFire", 0.01),
    ("Phân bổ quân", "mainEffort", 0.01),
    ("Chi tiêu CP", "cpSaving", 1),
    ("Hồi chiêu đổi chiến thuật", "tacticCooldown", 1),
    ("Thời gian chuyển tiếp chiến thuật", "tacticTransition", 1),
]


def rows(wb, name):
    return [r for r in wb[name].iter_rows(values_only=True) if any(c is not None for c in r)]


def param(value, lo, hi, metric, reason):
    lo, hi = min(lo, hi), max(lo, hi)
    return {"value": round(value, 4), "min": round(lo, 4), "max": round(hi, 4),
            "metric": str(metric or "").strip(), "reason": str(reason or "").strip().replace("—", "")}


def ai_params(wb):
    head, *body = rows(wb, "Tham số AI")
    out, seen = {}, set()
    for name, key, scale in PARAMS:
        row = next((r for r in body if str(r[0]).startswith(name)), None)
        if row is None:
            sys.exit(f"Tham số AI: no row '{name}'")
        seen.add(row[0])
        out[key] = param(first(row[2]) * scale, first(row[3]) * scale, first(row[4]) * scale, row[5], row[6])
    extra = [r[0] for r in body if r[0] not in seen]
    if extra:
        sys.exit(f"Tham số AI: rows without a rule: {extra}")
    return out


def economy(wb):
    table = rows(wb, "Cân bằng kinh tế")
    by = {str(r[0]).strip(): r for r in table if r[0] is not None}

    def cell(label):
        row = next((r for k, r in by.items() if k.startswith(label)), None)
        if row is None:
            sys.exit(f"Cân bằng kinh tế: no row '{label}'")
        return row

    metrics = {str(r[0]).strip(): r[0] for r in table if r[0] and str(r[0]).startswith(("Số quân", "Tỷ lệ", "FPS"))}
    army = next(k for k in metrics if k.startswith("Số quân trung bình"))
    fights = next(k for k in metrics if k.startswith("Tỷ lệ thời gian có giao tranh"))
    fps = next(k for k in metrics if k.startswith("FPS"))

    def fixed(label, metric):
        row = cell(label)
        v = num(row[1])
        return param(v, v, v, metric, row[5])

    out = {
        "baseIncome": fixed("Thu nhập CP gốc", army),
        "perPoint": fixed("Thêm mỗi cứ điểm", army),
        "groundCap": fixed("Trần quân mặt đất", fps),
        "airCap": fixed("Trần máy bay", fps),
        "stockCap": fixed("Trần CP tích trữ", army),
        "attackThreshold": fixed("Ngưỡng tấn công của tướng AI", fights),
        "useOrLoseThreshold": fixed("Ngưỡng tấn công thấp nhất", army),
        "useOrLoseRamp": fixed("Thời gian giảm ngưỡng", army),
    }
    # 'Chỉ huy Vault: 45'
    vault = nums(cell("Trần CP tích trữ")[5])
    out["stockCapVault"] = param(vault[0], vault[0], vault[0], army, cell("Trần CP tích trữ")[5])
    # Escalation tiers: the first from its cell, the later ones from its note ('khoảng 50, 70, 90 s').
    esc = cell("Mốc bậc 1")
    out["escalation"] = [param(t, t, t, fights, esc[5]) for t in [num(esc[1])] + nums(esc[5])]
    # Army bands (% of the cap -> income factor); a note's trial range ('thử 0,85–1,0') is the factor's min-max.
    bands = []
    for label in ("Ít quân", "Vừa", "Đông"):
        r = cell(label)
        trial = nums(r[5])[-2:]  # the note's trial range, its last two numbers
        lo, hi = trial if len(trial) == 2 else (num(r[3]), num(r[3]))
        band = param(num(r[3]), lo, hi, army, r[5])
        band["from"], band["to"] = num(r[1]) / 100, num(r[2]) / 100
        bands.append(band)
    out["armyBands"] = bands
    # Final phase rule: '2 phút cuối, điểm từ cứ điểm ×2'.
    final = cell("Pha cuối")
    text = " ".join(str(c) for c in final[1:] if c)
    m = re.search(r"(\d+) phút cuối.*?×(\d+)", text)
    if m:
        out["finalPhase"] = param(int(m.group(1)) * 60, int(m.group(1)) * 60, int(m.group(1)) * 60, fights, text)
        out["finalPhaseScale"] = param(int(m.group(2)), int(m.group(2)), int(m.group(2)), fights, text)
    return out



# ----------------------------------------------------------------------------------------------------------------
# Passes 2-5: behaviour data (balance.json "aiBehaviour"): squad states, roles, units, tactics, generals, towers, bosses.

STATES = ["TRAVEL", "APPROACH", "COMBAT", "OVERWATCH", "FLANK", "HOLD", "REGROUP"]
PRIORITY = {"thấp": 1, "vừa": 2, "cao": 3}

# The sheet's tactic names -> ids (the code's names; DECISIONS "28 2").
TACTICS = {
    "Cân bằng": "balanced", "Tấn công chớp nhoáng": "blitz", "Hỏa lực áp đảo": "firepower",
    "Phòng thủ chiều sâu": "depth", "Bao vây": "encircle", "Yểm hộ luân phiên": "bounding", "Phục kích": "ambush",
    "Bắn và chạy": "hit_and_run", "Tập trung đột phá": "breakthrough", "Phân tán": "dispersal",
    "Ưu thế trên không": "air_superiority", "Chế áp phòng không trước": "sead", "Tiêu hao": "attrition",
    "Săn đầu": "decapitation", "Bảo vệ căn cứ": "base_defence", "Tổng tấn công": "all_out",
}
# The sheet's commander call signs -> commander ids (NameText: the call sign after each name).
COMMANDERS = {"Kade": "kade", "Rush": "mendez", "Longshot": "dahl", "Bulwark": "brandt", "Flag": "adler", "Nadia": "kerr",
              "Crown": "reyn", "Venn": "venn", "Hawk": "reyes", "Magpie": "quist", "Vault": "okoye", "Ledger": "brenn", "Tide": "varro"}
GROUPS = ["Armour", "Light", "AntiTank", "Artillery", "AntiAir", "Helicopter", "Plane", "Support"]

# The sheet "Công trình" rows -> the tower ids they cover.
TOWERS = {
    "Tháp canh": ["guard_tower"], "Lô cốt súng máy": ["mg_bunker"],
    "Tháp phòng không": ["aa_gun_tower", "aa_turret", "heavy_flak_tower", "manpads_tower"], "Tháp gây nhiễu EW": ["ew_tower"],
    "Tháp pháo": ["gun_turret"], "Tháp ATGM": ["atgm_tower", "one_shot_atgm_tower", "recoilless_gun_tower", "at_gun_emplacement"],
    "Dàn rốc-két": ["rocket_turret"], "Trạm C-RAM / Vòm Sắt": ["c_ram", "laser_ad_station"],
    "Trận địa pháo": ["artillery_emplacement"], "Patriot": ["missile_battery"], "Nhà chứa drone": ["drone_hangar"],
    "Tháp pháo hạng nặng": ["heavy_turret", "coastal_battery"], "Máy phát khiên": ["shield_tower"],
}
MODES = {"gần nhất": "Nearest", "mạnh nhất": "Strongest", "yếu nhất": "Weakest", "đầu đoàn": "Lead",
         "máy bay trước": "AirFirst", "cụm đông nhất": "Cluster", "pháo binh trước": "ArtilleryFirst",
         "đạn bay vào công trình quan trọng nhất": "ShieldKey", "đạn gần nhất": "NearestRound",
         "máy bay lớn nhất": "BiggestAircraft", "tên lửa trước (pac-3)": "MissilesFirst", "(không bắn)": "None"}
# The sheet "Kiểu hành vi boss" names -> boss ids (balance.json: each boss's bigAttack).
BOSSES = {"Bastion": "fortress_bastion", "Behemoth": "behemoth", "Jötunn": "mobile_fortress", "Leviathan": "leviathan",
          "Matriarch": "drone_mothership", "Moloch": "moloch", "Nemesis": "nuke_train", "Kronos": "kronos", "Typhon": "typhon",
          "Roc": "command_airship", "Daedalus": "daedalus", "Icarus": "silver_bug"}
BEHAVIOURS = {"area denial": "AreaDenial", "anti-blob": "AntiBlob", "anti-air": "AntiAir", "anti-artillery": "AntiArtillery",
              "core protection": "CoreProtection", "flank punishment": "FlankPunishment"}
# A role's "khi bị áp đảo" column -> the short move it makes (D.3), by the first keyword found.
OVERWHELMED = [("khói", "Smoke"), ("vật che", "Cover"), ("dời vị trí", "Scoot"), ("đổi vị trí", "Shift"), ("đổi chỗ", "Shift"),
               ("lùi", "Shift"), ("về nạp", "Rearm"), ("đổi hướng", "Shift"), ("dời tâm", "Shift"), ("đổi vùng", "Shift")]


def states(wb):
    out = {}
    for r in rows(wb, "Trạng thái đội")[1:]:
        if r[0] not in STATES:
            sys.exit(f"Trạng thái đội: unknown state {r[0]}")
        out[r[0]] = {"priority": PRIORITY[str(r[4]).strip().lower()], "commit": first(r[5])}
    if len(out) != len(STATES):
        sys.exit("Trạng thái đội: a state is missing")
    return out


def roles(wb):
    out, names = {}, {}
    for r in rows(wb, "Vai trò")[1:]:
        engage = [n / 100 for n in nums(r[5]) if n > 1][:2]
        move = next((m for k, m in OVERWHELMED if k in str(r[8]).lower()), "Hold")
        out[r[0]] = {"engage": engage if len(engage) == 2 else [], "overwhelmed": move}
        names[str(r[1]).strip()] = r[0]
    return out, names


def units(wb, role_names):
    out, names = {}, {}
    for r in rows(wb, "Phương tiện")[1:]:
        role = role_names.get(str(r[2]).strip())
        if role is None:
            sys.exit(f"Phương tiện: {r[0]} has an unknown role {r[2]}")
        out[r[0]] = role
        names[str(r[1]).strip().lower()] = r[0]
    return out, names


def modules(core, impact):
    """A tactic's behaviour modules from its 'Tác động lên AI' text: numbers where the sheet gives them, keywords else."""
    t = str(impact).lower()
    m = {}
    if (x := re.search(r"ngưỡng tấn công[^;]*?(\d+,\d+)(?: → (\d+,\d+))?", t)):
        m["attackThreshold"] = num(x.group(2) or x.group(1))
    if "không chờ xe chậm" in t:
        m["cohesion"] = 0
    if "trọng số đánh sườn tăng" in t or "đánh sườn sâu" in t:
        m["flank"] = 1.6
    if "chia 2–3 đội" in t:
        m["pincer"] = 1
    if "giảm dồn hỏa lực" in t:
        m["focus"] = 0.5
    if (x := re.search(r"≥ (\d+)% quân", t)):
        m["mainEffort"] = num(x.group(1)) / 100
    if (x := re.search(r"khoảng cách tối thiểu giữa xe ×(\d+)", t)):
        m["spread"] = num(x.group(1))
    if (x := re.search(r"giữ lửa tới khi địch vào ~(\d+)% tầm", t)):
        m["holdFire"] = num(x.group(1)) / 100
        m["stance"] = "HoldFire"
    if (x := re.search(r"khoảng cách giao chiến (\d+)–(\d+)% tầm", t)):
        m["engage"] = [num(x.group(1)) / 100, num(x.group(2)) / 100]
    if (x := re.search(r"lùi khi địch vào (\d+)% tầm", t)):
        m["kite"] = num(x.group(1)) / 100
    if (x := re.search(r"chờ (\d+) đợt pháo", t)):
        m["artilleryPrep"] = num(x.group(1))
    if (x := re.search(r"dưới (\d+,\d+) lần", t)):
        m["fallback"] = num(x.group(1))
    if (x := re.search(r"phản công khi sức mạnh ta ≥ (\d+,\d+)", t)):
        m["counterattack"] = num(x.group(1))
    if (x := re.search(r"tốc độ tiến giảm ~(\d+)%", t)):
        m["pace"] = 1 - num(x.group(1)) / 100
    if "chia 2 nhóm" in t:
        m["bounding"] = 1
    if "đội giữ điểm" in t or "đội giữ trong vùng căn cứ" in t:
        m["hold"] = 1
    if "trong vùng căn cứ" in t:
        m["holdBase"] = 1
    if "chờ tới khi máy bay địch bị hạ" in t:
        m["waitAir"] = 1
    if "để dành cp" in t:
        m["cpSaving"] = 1
    if "mọi đội cùng tấn công" in t:
        m["together"] = 1
    if "ưu tiên vũ khí tầm xa" in t:
        m["engage"] = m.get("engage", [0.9, 1.0])
    if "tầm xa" in t and "giữ khoảng cách" in t:
        m["standoff"] = 1
    if "ưu tiên mục tiêu: phòng không" in t:
        m["targets"] = ["AntiAir"]
    if "ưu tiên mục tiêu: xe hỗ trợ" in t:
        m["targets"] = ["Support", "Artillery"]
    if "tháp ưu tiên chế độ đầu đoàn" in t:
        m["towerMode"] = "Lead"
    if "xe hạng nặng đi đầu" in t:
        m["heavyLead"] = 1
    if "bỏ giữ các điểm phụ" in t:
        m["dropSecondary"] = 1
    if "dùng thẻ chế áp" in t:
        m["seadCards"] = 1
    if "thẻ hỗ trợ dồn cùng lúc" in t:
        m["massSupport"] = 1
    return m


def tactics(wb, unit_names):
    head, *body = rows(wb, "Chiến thuật")
    out, missing = [], []
    for r in body:
        tid = TACTICS.get(str(r[0]).strip())
        if tid is None:
            sys.exit(f"Chiến thuật: no id for '{r[0]}'")
        cp = [num(x) / 100 for x in r[9:17]]
        if abs(sum(cp) - 1) > 0.01:
            sys.exit(f"Chiến thuật {tid}: CP shares sum to {sum(cp)}")
        prefer = []
        for name in re.split(r"[,.:;]", str(r[8] or "")):
            n = re.sub(r"\(.*?\)", "", name).strip().lower()
            if n.startswith("tránh"):
                break  # what follows 'Tránh' is to avoid, not to buy
            if not n or n.startswith(( "theo ai", "để dành", "nhiều xe", "thêm", "loadout", "không ưu tiên")):
                continue
            ids = [i for k, i in unit_names.items() if k == n or k.startswith(n)]
            if ids:
                prefer += [i for i in ids if i not in prefer]
            else:
                missing.append(f"{tid}: {name.strip()}")
        unlock = str(r[22] or "").strip()
        chapter = int(nums(unlock)[0]) if "Chương" in unlock else 0
        interlude = 1 if "Xen kẽ" in unlock else 0
        fits = [COMMANDERS[c.strip()] for c in re.split(r"[,/]", str(r[23] or "")) if c.strip() in COMMANDERS]
        merge = TACTICS.get(str(r[3] or "").replace("Kiểm tra với", "").strip())
        def named(cell):
            return [i for name, i in TACTICS.items() if name in str(cell or "")]
        out.append({"id": tid, "name": str(r[0]).strip(), "cp": [round(x, 4) for x in cp], "prefer": prefer,
                    "counters": named(r[20]), "counteredBy": named(r[21]),
                    "chapter": chapter, "interlude": interlude, "commanders": fits, "checkWith": merge or "",
                    "modules": modules(r[1], r[7])})
    return out, missing


def generals(wb):
    text = " ".join(str(c) for r in rows(wb, "Tính năng chọn chiến thuật") if str(r[0]).startswith("Tướng địch") for c in r[1:] if c)
    out = {}
    for name, tactic in re.findall(r"(\w+): ([^;()]+)", text):
        t = TACTICS.get(re.split(r" với| như", tactic)[0].strip())
        if t:
            out[name.lower()] = t
    # Prompt 28 H.7 (not in the sheet): Brandt and a mission without a general use Defence in depth or Balanced.
    out.setdefault("brandt", "depth")
    out.setdefault("default", "balanced")
    return out


def towers(wb):
    out = {}
    for r in rows(wb, "Công trình")[1:]:
        ids = TOWERS.get(str(r[0]).strip())
        if ids is None:
            sys.exit(f"Công trình: no ids for '{r[0]}'")
        default = MODES.get(str(r[1]).strip().lower())
        options = [MODES[o.strip().lower()] for o in str(r[2] or "").split(",") if o.strip().lower() in MODES]
        if default is None:
            sys.exit(f"Công trình {r[0]}: unknown mode '{r[1]}'")
        for i in ids:
            out[i] = {"mode": default, "modes": options}
    return out


def bosses(wb):
    out = {}
    for r in rows(wb, "Kiểu hành vi boss")[1:]:
        bid = BOSSES.get(str(r[0]).strip())
        kinds = [BEHAVIOURS[k.strip().lower()] for k in str(r[1]).split(",") if k.strip().lower() in BEHAVIOURS]
        if bid is None or not kinds:
            sys.exit(f"Kiểu hành vi boss: cannot map '{r[0]}' / '{r[1]}'")
        out[bid] = kinds
    return out


def behaviour(wb):
    role_data, role_names = roles(wb)
    unit_data, unit_names = units(wb, role_names)
    tactic_data, missing = tactics(wb, unit_names)
    if missing:
        print("Ưu tiên mua names with no vehicle (left out):\n  " + "\n  ".join(missing))
    return {"states": states(wb), "roles": role_data, "units": unit_data, "tactics": tactic_data,
            "generals": generals(wb), "towers": towers(wb), "bosses": bosses(wb)}


def block(data, behaviour_data=None) -> list[str]:
    def line(key, value, indent, last):
        return f'{" " * indent}"{key}": {json.dumps(value, ensure_ascii=False)}{"" if last else ","}'

    out = [BEGIN,
           "  // Prompt 28: the AI parameter frame (L.1). Each parameter: value (the starting point, not final), min-max",
           "  // (the sweep range), metric (what the sweep measures) and reason (the sheet's tuning note).",
           '  "ai": {']
    sections = list(data.items())
    for si, (name, entries) in enumerate(sections):
        out.append(f'    "{name}": {{')
        items = list(entries.items())
        for i, (k, v) in enumerate(items):
            last = i == len(items) - 1
            if isinstance(v, list):
                out.append(f'      "{k}": [')
                out += [f'        {json.dumps(x, ensure_ascii=False)}{"" if j == len(v) - 1 else ","}' for j, x in enumerate(v)]
                out.append("      ]" + ("" if last else ","))
            else:
                out.append(line(k, v, 6, last))
        out.append("    }" + ("" if si == len(sections) - 1 else ","))
    out.append("  },")
    if behaviour_data is not None:
        out += ["  // Prompt 28 passes 2-5: the squad states, roles, units, tactics, generals' tactics, tower modes and boss",
                "  // behaviour types of the research sheet (see Docs/ai/TACTICS.md).",
                '  "aiBehaviour": {']
        items = list(behaviour_data.items())
        for i, (k, v) in enumerate(items):
            last = i == len(items) - 1
            if isinstance(v, list):
                out.append(f'    "{k}": [')
                out += [f'      {json.dumps(x, ensure_ascii=False)}{"" if j == len(v) - 1 else ","}' for j, x in enumerate(v)]
                out.append("    ]" + ("" if last else ","))
            elif isinstance(v, dict) and all(isinstance(x, (dict, list)) for x in v.values()):
                out.append(f'    "{k}": {{')
                sub = list(v.items())
                out += [f'      "{a}": {json.dumps(b, ensure_ascii=False)}{"" if j == len(sub) - 1 else ","}' for j, (a, b) in enumerate(sub)]
                out.append("    }" + ("" if last else ","))
            else:
                out.append(f'    "{k}": {json.dumps(v, ensure_ascii=False)}{"" if last else ","}')
        out.append("  },")
    out.append(END)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    data = {
        # The World Model's own cadence and cell (prompt 28 A.1 and M.1; the sheet has no row for them).
        "world": {"rate": param(2, 1, 4, "AI tick time (M.5)", "prompt 28 A.1/M.1: about twice a second"),
                  "cell": param(10, 6, 16, "AI tick time (M.5)", "prompt 28 A.1: 10 m cells to start"),
                  # The World Model's own detection thresholds (A.1, A.4; the sheet gives none, DECISIONS "28 1").
                  "highValue": param(1.5, 1.2, 2.5, "Số mục tiêu giá trị bị hạ", "a contact this many times the mean known strength is high value"),
                  "splashMin": param(2, 1, 4, "Số xe bị hạ bởi bắn lan mỗi phút", "a weapon with a blast this wide (m) paints the splash threat"),
                  "eventLife": param(8, 4, 15, "Số lần đổi hành động mỗi phút của đội", "seconds an event lasts unless refreshed"),
                  "airShare": param(0.25, 0.15, 0.4, "Số máy bay bị hạ mỗi lượt", "MISMATCH: enemy aircraft share of its strength"),
                  "aaShare": param(0.1, 0.05, 0.2, "Số máy bay bị hạ mỗi lượt", "MISMATCH: own anti-air share below this"),
                  "armourShare": param(0.4, 0.3, 0.6, "Thời gian hạ mục tiêu", "MISMATCH: enemy armour share of its strength"),
                  "atShare": param(0.15, 0.1, 0.3, "Thời gian hạ mục tiêu", "MISMATCH: own anti-tank share below this"),
                  # Pass 5 (I.6, not in the sheet): what counts as a big fight, and what a point is worth under pressure.
                  "bigFight": param(600, 300, 1500, "Tỷ lệ thời gian có giao tranh", "health lost by both sides in 5 s that resets the pressure tiers"),
                  "escalationPoints": param(1.5, 1.25, 2, "Tỷ lệ thời gian có giao tranh", "tier 1: points' income and bleed x this"),
                  "churnWarn": param(6, 3, 12, "Số lần đổi hành động mỗi phút của đội", "switches a minute per squad above which the viewer warns (J.3)")},
        "params": ai_params(wb),
        "economy": economy(wb),
    }
    new = block(data, behaviour(wb))
    if args.dry:
        print("\n".join(new))
        return
    with open(BALANCE, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if BEGIN in lines:
        a, b = lines.index(BEGIN), lines.index(END)
        lines[a:b + 1] = new
    else:
        a = lines.index(ANCHOR)
        lines[a:a] = new
    with open(BALANCE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"ai block: {len(new)} lines, {len(data['params'])} params, {len(data['economy'])} economy entries")


if __name__ == "__main__":
    main()
