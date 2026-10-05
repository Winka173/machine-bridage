"""09_ai (+ 02_boss, 04_che_do_kinh_te_ai), layer C, AI MASTER P5 (05/10): the AI MASTER data read straight from its canonical
sources, so a regenerated pack always shows the AI the game runs:

* AI_ma_ly_do: the one reason-code registry (Sim/AI/P5/ReasonCodes.cs, `ReasonCodes.All`): code, namespace, lane, alias, meaning.
* AI_hoc_thuyet_che_do (+ 04 Che_do_hoc_thuyet_AI): Part I mode doctrines, resolved through their inheritance from
  `ModeCombatDoctrine.Build()` and the ModeDoctrine defaults (Sim/AI/P2/ModeCombatDoctrine.cs), and the mode tag / campaign goal map.
* AI_hoc_thuyet_vai_tro: Part B role target ladders (`CombatRoleDoctrine.Worth`, Sim/AI/P2/CombatRoleDoctrine.cs): role, rung,
  condition, factor (RankTop x RankStep^(rung-1) from tunables ai.roleDoctrine).
* AI_nhom_hang_so: the tunables.json groups of the AI (ai.*, bosses.bossBrain): keys, lane, where the values are (Hang_so_ai /
  Hang_so_boss carry every value already, core/tunables.py).
* AI_nhip_cap_nhat / AI_giam_sat_suc_khoe: Part P update budget and Part K health monitor (rows citing the code).
* 02 Boss_ma_ly_do: the BOSS_* / NAVAL_* codes of the registry.

Read only: nothing here changes a game value. A doctrine or ladder construct the regexes do not know is listed under the sheet's
`nguon` as unreadable rather than guessed."""
from __future__ import annotations

import json
import re

from core.repo import ROOT

AI = "Assets/MachineBrigade/Scripts/Sim/AI/"
REG = AI + "P5/ReasonCodes.cs"
MODE = AI + "P2/ModeCombatDoctrine.cs"
ROLE = AI + "P2/CombatRoleDoctrine.cs"
TUN = "Assets/MachineBrigade/Resources/Data/tunables.json"


def _text(path: str) -> str:
    return (ROOT / path).read_text("utf-8-sig")


def _line(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _tunables() -> dict:
    raw = _text(TUN)
    raw = re.sub(r"^\s*//.*$", "", raw, flags=re.M)
    return json.loads(raw)


# ------------------------------------------------------------------------------------------------------------ registry
_CODE = re.compile(r'new ReasonCode\("([A-Z0-9_]+)",\s*"([A-Z_]+)",\s*"(\w+)",\s*"((?:[^"\\]|\\.)*)"(?:,\s*"([^"]*)")?\)')


def codes():
    text = _text(REG)
    out = []
    for m in _CODE.finditer(text):
        out.append(dict(code=m.group(1), ns=m.group(2), lane=m.group(3), meaning=m.group(4), alias=m.group(5) or "",
                        line=_line(text, m.start())))
    return out


def _codes_sheet(book, name, title, desc, rows):
    s = book.sheet(name, title, desc, layer="C")
    s.col("nhom", meaning="namespace (Part O: PURCHASE, TARGET, POSITION, ROUTE, TRAFFIC, JAM, COMBAT_IDLE, FORMATION, MODE, BOSS, "
                         "NAVAL, SUPPORT, AIR, ARTILLERY, OBJECTIVE, WATCHDOG; thêm SQUAD, ROLE, COMBAT)")
    s.col("lane", meaning="lane AI MASTER ghi mã này (P0A, P0B, P0C, P1, P2, P3, P4, P5)")
    s.col("bi_danh", meaning="tên cũ cùng nghĩa (động từ dòng mua của mục 94: BUY / REJECT / PLAN / RESERVE, hoặc khóa yếu tố điểm)")
    s.col("y_nghia", meaning="mã nói gì (tiếng Anh như trong mã)")
    for c in rows:
        r = s.row(c["code"], f"{REG}:{c['line']}")
        r.set("nhom", c["ns"])
        r.set("lane", c["lane"])
        r.set("bi_danh", c["alias"])
        r.set("y_nghia", c["meaning"])
    return s


# ------------------------------------------------------------------------------------------------------------ mode doctrines
_PROP = re.compile(r"public\s+(\w+)\s+(\w+)\s*\{\s*get;\s*internal\s+set;\s*\}(?:\s*=\s*([^;]+);)?")
_ADD = re.compile(r'Add\("(\w+)",\s*("?\w+"?),\s*d\s*=>\s*')
_ASSIGN = re.compile(r"d\.(\w+)\s*(\|?=)\s*([^;]+);")
_MAP = re.compile(r'\["(\w+)"\]\s*=\s*"(\w+)"')


def _clean(v: str) -> str:
    v = re.sub(r"\s+", " ", v.strip())
    v = re.sub(r"\b(?:FrontlinePolicy|FireSupportPolicy|PursuitPolicy|RepositionTrigger)\.", "", v)
    v = re.sub(r"(\d)f\b", r"\1", v)
    return v.replace(" | ", "|")


def doctrines():
    """[(id, inherits, {field: value}, line)] in the order Build() adds them, inheritance resolved."""
    text = _text(MODE)
    cls = text[text.index("public sealed class ModeDoctrine"):text.index("internal ModeDoctrine Copy")]
    defaults = {}
    for m in _PROP.finditer(cls):
        name, init = m.group(2), m.group(3)
        if name in ("Id", "Inherits"):
            continue
        defaults[name] = _clean(init) if init else ("false" if m.group(1) == "bool" else "")
    build = text[text.index("private static Dictionary<string, ModeDoctrine> Build()"):]
    build = build[:build.index("return t;")]
    table = {"balanced_objective": dict(defaults)}
    out = [("balanced_objective", "", dict(defaults), _line(text, text.index("var basis = new ModeDoctrine")))]
    adds = list(_ADD.finditer(build))
    base_at = text.index("private static Dictionary<string, ModeDoctrine> Build()")
    for i, m in enumerate(adds):
        did, parent = m.group(1), m.group(2).strip('"')
        parent = "balanced_objective" if parent == "Base" else parent
        end = adds[i + 1].start() if i + 1 < len(adds) else len(build)
        body = build[m.end():end]
        fields = dict(table.get(parent, defaults))
        for a in _ASSIGN.finditer(body):
            name, op, val = a.group(1), a.group(2), _clean(a.group(3))
            fields[name] = f"{fields.get(name, '')}|{val}" if op == "|=" else val
        table[did] = fields
        out.append((did, parent, fields, _line(text, base_at + m.start())))
    tags = {k: v for k, v in _MAP.findall(text[text.index("ModeTags"):text.index("Goals = new")])}
    goals = {k: v for k, v in _MAP.findall(text[text.index("Goals = new"):text.index("public static string Resolve")])}
    return out, tags, goals, sorted(defaults)


def _doctrine_sheet(book, name, title):
    rows, tags, goals, fields = doctrines()
    s = book.sheet(name, title, "Part I ModeCombatDoctrine: một dòng một học thuyết (BalancedObjectiveDoctrine gốc + kế thừa I15), "
                   "đã giải kế thừa; đọc thẳng từ ModeCombatDoctrine.Build() mỗi lần xuất. Cột che_do / muc_tieu: thẻ chế độ "
                   "và kiểu mục tiêu chiến dịch dẫn tới học thuyết này (Resolve)", layer="C")
    s.col("ke_thua", meaning="học thuyết cha (I15: gốc + chế độ + pha, không sao chép)")
    s.col("che_do", meaning="thẻ chế độ (world.ModeTag) dùng học thuyết này (ngăn ';')")
    s.col("muc_tieu", meaning="kiểu mục tiêu chiến dịch (aiModeProfiles.goals) dùng học thuyết này (ngăn ';')")
    for f in fields:
        s.col(f, meaning=f"ModeDoctrine.{f}")
    for did, parent, values, line in rows:
        r = s.row(did, f"{MODE}:{line}")
        r.set("ke_thua", parent)
        r.set("che_do", ";".join(sorted(k for k, v in tags.items() if v == did)))
        r.set("muc_tieu", ";".join(sorted(k for k, v in goals.items() if v == did)))
        for f in fields:
            r.set(f, values.get(f, ""))
    return s


# ------------------------------------------------------------------------------------------------------------ role ladders
_CASE = re.compile(r"case DoctrineRole\.(\w+):")
_IFRET = re.compile(r"^if \((.+)\) return (.+);$")
_RUNG = re.compile(r"^Rung\((\d+), (\d+)\)$")


def _statements(block: str):
    """The block's lines, an if spread over lines joined into one."""
    out, cur = [], ""
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if cur:
            cur += " " + line
            if line.endswith(";"):
                out.append(cur)
                cur = ""
            continue
        if line.startswith("if (") and not line.endswith(";"):
            cur = line
            continue
        out.append(line)
    return out


def ladders(rank_top: float, rank_step: float, last_resort: float):
    text = _text(ROLE)
    start = text.index("public static float Worth(")
    body = text[start:text.index("internal static bool Clustered", start)]
    cases = list(_CASE.finditer(body))
    rows = []
    for i, m in enumerate(cases):
        role = m.group(1)
        end = cases[i + 1].start() if i + 1 < len(cases) else body.index("default:")
        block = body[m.end():end]
        lines = _statements(block)
        rule = " ".join(x.lstrip("/").strip() for x in lines if x.startswith("//"))
        line_no = _line(text, start + m.start())
        k = 0
        for st in lines:
            if st.startswith("//"):
                continue
            mi = _IFRET.match(st)
            if mi:
                cond, val = "if " + mi.group(1), mi.group(2).strip()
            elif " => " in st and st.endswith(","):
                cond, val = (x.strip() for x in st[:-1].rsplit(" => ", 1))
            elif st.startswith("return ") and "switch" not in st:
                cond, val = "(còn lại)", st[len("return "):].rstrip(";").strip()
            else:
                continue
            k += 1
            mr = _RUNG.match(val)
            if mr and int(mr.group(1)) > 0:
                n = int(mr.group(1))
                factor, label = round(rank_top * rank_step ** (n - 1), 4), f"{n}/{mr.group(2)}"
            elif mr:
                n = int(mr.group(2)) + 1
                factor, label = round(rank_top * rank_step ** (n - 1), 4), f"dưới bậc cuối ({mr.group(2)})"
            elif val in ("LastResort()", "Tun.RoleDoctrine.LastResort"):
                factor, label = last_resort, "phương án cuối (LastResort; nguy cấp: dưới bậc cuối)" if val.endswith("()") else "phương án cuối"
            else:
                factor, label = "", val.replace("Tun.RoleDoctrine.", "")
            cond = re.sub(r"TargetClass\.", "", cond).replace(" or ", " | ")
            rows.append(dict(id=f"{role}/{k}", role=role, cond=cond, rung=label, factor=factor, rule=rule, line=line_no))
    return rows


def _ladder_sheet(book, tun):
    rd = (tun.get("ai") or {}).get("roleDoctrine") or {}
    get = lambda k, d: (rd.get(k) or {}).get("value", d)  # noqa: E731
    top, step, last = get("rankTop", 1.6), get("rankStep", 0.8), get("lastResort", 0.35)
    s = book.sheet("AI_hoc_thuyet_vai_tro", "Học thuyết vai trò: thang mục tiêu",
                   f"Part B CombatRoleDoctrine.Worth: mỗi vai trò một thang ưu tiên mục tiêu cho vũ khí chính; hệ số bậc n = "
                   f"rankTop x rankStep^(n-1) = {top} x {step}^(n-1) (tunables ai.roleDoctrine), phương án cuối = {last}. Đọc thẳng "
                   "từ mã mỗi lần xuất; mục tiêu không khả thi đã bị loại trước (bộ lọc P0-A)", layer="C")
    s.col("vai_tro", meaning="DoctrineRole")
    s.col("dieu_kien", meaning="lớp mục tiêu (TargetClass) hoặc điều kiện, theo thứ tự mã xét")
    s.col("bac", meaning="bậc / số bậc của thang")
    s.col("he_so", meaning="hệ số nhân lên điểm mục tiêu")
    s.col("quy_tac", meaning="chú thích quy tắc trong mã (mục Part B)")
    for x in ladders(top, step, last):
        r = s.row(x["id"], f"{ROLE}:{x['line']}")
        r.set("vai_tro", x["role"])
        r.set("dieu_kien", x["cond"])
        r.set("bac", x["rung"])
        r.set("he_so", x["factor"])
        r.set("quy_tac", x["rule"])
    return s


# ------------------------------------------------------------------------------------------------------------ tunable groups
_LANE = re.compile(r"\((AI MASTER [^)]+)\)")


def _groups_sheet(book, tun):
    s = book.sheet("AI_nhom_hang_so", "Nhóm hằng số AI (tunables.json)",
                   "Mỗi nhóm của tunables.json 'ai' (và bosses.bossBrain): số khóa, lane, sheet chứa giá trị (Hang_so_ai của "
                   "09_ai, Hang_so_boss của 02_boss); giá trị từng khóa nằm ở đó, không chép lại", layer="C")
    s.col("khoi", meaning="khối trong tunables.json")
    s.col("nhom", meaning="nhóm (lớp chủ)")
    s.col("so_khoa", meaning="số hằng số")
    s.col("lane", meaning="lane AI MASTER (theo cột code), trống: hằng số cũ dọn từ mã")
    s.col("sheet_gia_tri", meaning="sheet chứa từng giá trị")
    s.col("khoa", meaning="tên các khóa (ngăn ';')")
    blocks = [("ai", k, v, "09_ai/Hang_so_ai") for k, v in (tun.get("ai") or {}).items()]
    bb = (tun.get("bosses") or {}).get("bossBrain")
    if bb:
        blocks.append(("bosses", "bossBrain", bb, "02_boss/Hang_so_boss"))
    for block, group, items, where in blocks:
        lanes = sorted({m.group(1) for e in items.values() if isinstance(e, dict) for m in [_LANE.search(str(e.get("code", "")))] if m})
        r = s.row(f"{block}.{group}", f"{TUN}: {block}.{group}")
        r.set("khoi", block)
        r.set("nhom", group)
        r.set("so_khoa", len(items))
        r.set("lane", ";".join(lanes))
        r.set("sheet_gia_tri", where)
        r.set("khoa", ";".join(items))
    return s


# ------------------------------------------------------------------------------------------------------------ Part P / Part K
_BUDGET = [
    ("Steering", "10 Hz (ORCA-lite so le theo id), mỗi bước cho phần lái", "ai.navigation.orcaLite; ai.traffic.*",
     "Movement/MovementSystem*.cs; P1", "Steering"),
    ("Tactical", "4 Hz watchdog; TacticalAi theo ai.tacticalAi.decisionInterval", "ai.combatWatchdog.*; ai.tacticalAi.decisionInterval",
     "AI/CombatActivityWatchdog.cs; AI/TacticalAi.cs", "Tactical; Watchdog; Targeting"),
    ("Squad", "lớp đội 4 Hz (ai.squadLayer.interval 0.25 s, hai phe lệch nửa nhịp); mỗi đội nghĩ 2 Hz theo nhóm so le "
     "(ai.budget.squadBuckets 2), né vòng cảnh báo mỗi nhịp", "ai.squadLayer.interval; ai.budget.squadBuckets",
     "AI/Squads.cs Tick; AI/P5/AiBudget.cs AiCadence", "Squad"),
    ("Commander", "1 Hz, hai phe lệch 0.5 s (P2 gán việc, P3 phối hợp, P4 kế hoạch)", "(cố định 1 s)", "AI/Commander.cs Tick/Pass",
     "Commander"),
    ("Procurement", "theo độ khó 2.2 / 1.1 / 0.6 / 0.45 s (giữ: là đòn bẩy phản ứng của độ khó); kế hoạch mua 16 tránh chấm lại "
     "cả bộ bài mỗi lần", "(ConquestAi.Interval)", "AI/ConquestAi.cs Buy", "Procurement"),
    ("HealthMonitor", "1 Hz, lệch 0.5 s sau tướng", "ai.health.periodS", "AI/P5/AiHealthMonitor.cs", "HealthMonitor"),
    ("Forecast", "theo sự kiện + cache 0.75 s (P4)", "ai.forecast.cacheS", "AI/P4/Planning.cs", "Commander"),
    ("Spatial", "lưới đều 10 m (mục 98: 8-12 m), dựng lại tối đa 1 lần / bước sau di chuyển; đếm cụm / đám đông thay cho quét "
     "toàn bộ xe", "ai.budget.spatialCell", "AI/P5/AiBudget.cs AiSpatialIndex", "Targeting"),
    ("Counters", "bộ đếm thời gian theo hệ (tắt mặc định; harness 48v48 bật)", "ai.budget.perfCounters", "AI/P5/AiBudget.cs AiPerfCounters",
     "(tất cả)"),
]

_HEALTH = [
    ("armedIdleWithoutReason", "CombatWatch.Unexplained", "ai.health.idleTripShare", "ép kiểm mục tiêu / lời giải bắn, làm mới "
     "trạng thái chiến đấu, ghi 3 lý do hàng đầu", "WATCHDOG_IDLE_AUDIT; WATCHDOG_IDLE_TOP_REASONS"),
    ("squadsNoDamageSeconds", "đội có tiếp xúc mà không thành viên nào bắn", "ai.health.squadNoDamageS; contactMargin",
     "đánh giá lại hành động (idle reassess), phát lại đích (tuyến mới), chọn lại neo hỏa lực", "WATCHDOG_SQUAD_ZERO_UTILIZATION"),
    ("stalledObjectiveAssignments", "đội có mục tiêu không lại gần quá stallS", "ai.health.stallS; progressM; arriveRadius",
     "đánh giá lại hành động và tuyến", "WATCHDOG_SQUAD_STALLED_OBJECTIVE"),
    ("blockedUnits", "xe mặt đất đang đi ở bậc kẹt >= 3", "ai.health.blockedTripShare; blockedMinUnits",
     "đội có nửa thành viên kẹt: phát lại đích (điều phối giao thông chọn hành lang khác)", "WATCHDOG_TRAFFIC_ESCALATION"),
    ("severeUnstuckEvents", "Traffic.Stats.SevereUnstuck", "(mục tiêu Part S <= 1 / 10 xe-phút)", "đếm (P1 đã có thang gỡ kẹt)",
     "SEVERE_UNSTUCK"),
    ("ordersPerUnitPerMinute", "lệnh đơn vị gửi vào thế giới / phút / xe (phe AI)", "-", "đếm", "-"),
    ("targetSwitchesPerMinute", "DecisionLog.Totals (mục tiêu) / phút / đội", "-", "đếm", "-"),
    ("squadActionSwitchesPerMinute", "DecisionLog.Totals (hành động) / phút / đội; đội đang 'churning'", "ai.health.churnCommitScale; "
     "churnDampS", "cam kết x1.5 trong 30 s", "WATCHDOG_CHURN_DAMPED"),
    ("noMapInfluencePurchases", "luôn 0: thẻ không ảnh hưởng bản đồ bị loại trước khi chấm (P0-B)", "-", "-", "PURCHASE_NO_MAP_INFLUENCE"),
    ("lowUtilizationUnitClasses", "AdaptationTracker.LowClasses (P4)", "ai.adaptation.lowUtilization; lowUtilizationS",
     "hệ số mua của P4 tác động", "WATCHDOG_LOW_UTILIZATION_CLASSES"),
    ("combatAnomalies", "CombatWatch.Anomalies", "-", "watchdog P0-A tự phục hồi", "WATCHDOG_COMBAT_ANOMALY"),
    ("deadlockCycles", "Traffic.Stats.Deadlocks", "-", "P1 phá chu trình", "TRAFFIC_DEADLOCK_CYCLE"),
    ("navalReverseAttempts", "BossBrains.NavalReverseEvents + NavalReverseRefused", "ai.health.strictAssertions",
     "lỗi cứng khi debug; bộ điều khiển rẽ / giảm tốc / đổi làn", "NAVAL_REVERSE_FORBIDDEN"),
]


def _budget_sheet(book):
    s = book.sheet("AI_nhip_cap_nhat", "Nhịp cập nhật và ngân sách AI",
                   "Part P / mục 3, 98: tần số từng lớp, cơ chế so le / cache, khóa tunables và mục bộ đếm thời gian "
                   "(AiPerfSection) mà harness 48v48 báo cáo", layer="C")
    for c, m in (("lop", "lớp / hệ"), ("nhip", "tần số và cách so le"), ("khoa", "khóa tunables"), ("nguon_ma", "mã"),
                 ("bo_dem", "mục AiPerfSection")):
        s.col(c, meaning=m)
    for lop, nhip, khoa, ma, dem in _BUDGET:
        r = s.row(lop, f"Sim/{ma}")
        for c, v in (("lop", lop), ("nhip", nhip), ("khoa", khoa), ("nguon_ma", ma), ("bo_dem", dem)):
            r.set(c, v)


def _health_sheet(book):
    s = book.sheet("AI_giam_sat_suc_khoe", "Giám sát sức khỏe AI (Part K)",
                   "AiHealthMonitor (1 Hz, trên các watchdog): chỉ số, nguồn, ngưỡng, hành động phục hồi (chỉ đánh giá lại "
                   "hợp lệ, không gian lận) và mã ghi nhật ký", layer="C")
    for c, m in (("chi_so", "chỉ số Part K"), ("nguon_so", "đọc từ đâu"), ("nguong", "khóa ngưỡng"), ("phuc_hoi", "phục hồi (K1)"),
                 ("ma", "mã ghi")):
        s.col(c, meaning=m)
    for chi, nguon, nguong, phuc, ma in _HEALTH:
        r = s.row(chi, "Sim/AI/P5/AiHealthMonitor.cs")
        for c, v in (("chi_so", chi), ("nguon_so", nguon), ("nguong", nguong), ("phuc_hoi", phuc), ("ma", ma)):
            r.set(c, v)


# ------------------------------------------------------------------------------------------------------------ build
def build(ctx, book):
    tun = _tunables()
    all_codes = codes()
    _codes_sheet(book, "AI_ma_ly_do", "Mã lý do AI (một bảng đăng ký)",
                 "Part O: mọi mã lý do các lane AI MASTER ghi vào DecisionLog, đọc từ ReasonCodes.All (Sim/AI/P5/ReasonCodes.cs); "
                 "test AIMasterP5 kiểm mọi hằng số mã của các lane đều có ở đây và nhật ký một trận không có mã lạ",
                 all_codes)
    _doctrine_sheet(book, "AI_hoc_thuyet_che_do", "Học thuyết chiến đấu theo chế độ")
    _ladder_sheet(book, tun)
    _groups_sheet(book, tun)
    _budget_sheet(book)
    _health_sheet(book)
    boss = ctx.books.get("03_boss")
    if boss is not None:
        _codes_sheet(boss, "Boss_ma_ly_do", "Mã lý do AI của boss / tàu",
                     "BOSS_* / NAVAL_* của bảng đăng ký mã (09_ai/AI_ma_ly_do): dòng nhật ký của bộ não boss (mục 96), pha, "
                     "lệnh cấm lùi tàu", [c for c in all_codes if c["ns"] in ("BOSS", "NAVAL")])
    modes = ctx.books.get("05_che_do_kinh_te")
    if modes is not None:
        _doctrine_sheet(modes, "Che_do_hoc_thuyet_AI", "Chế độ: học thuyết chiến đấu AI")
