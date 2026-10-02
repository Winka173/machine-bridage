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


def block(data) -> list[str]:
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
    out += ["  },", END]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    data = {
        # The World Model's own cadence and cell (prompt 28 A.1 and M.1; the sheet has no row for them).
        "world": {"rate": param(2, 1, 4, "AI tick time (M.5)", "prompt 28 A.1/M.1: about twice a second"),
                  "cell": param(10, 6, 16, "AI tick time (M.5)", "prompt 28 A.1: 10 m cells to start")},
        "params": ai_params(wb),
        "economy": economy(wb),
    }
    new = block(data)
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
