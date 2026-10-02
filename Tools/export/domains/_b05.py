"""05_che_do_kinh_te, layer B (pass 5 part 2): Che_do_thoi_luong (each mode's theoretical length from its score rule,
bleed and clock), Kinh_te_suy_ra (CP a side has earned by 25 / 50 / 75 / 100 % of that length, by mode and difficulty)
and Kiem_tinh_che_do (the static mode audit's four books, Tools/audit/mode_static_audit.py: economy, free / scripted
forces, static defences, tempo; the two sides' strength band, gap %, GREEN / YELLOW / RED).

The start CP, income and clocks of a quick mode are C# literals of its session (Game/Match/ModeSessions.cs and the
Sim/Modes rules): each is read from the C# by a pattern (cited file:line; NEED_CODE_CHECK when the pattern no longer
matches). balance.json numbers are referenced live from Che_do / Kinh_te. Theory only: upkeep, the catch-up, kills,
commanders, events and the AI's spending are not modelled (stated in Schema)."""
from __future__ import annotations

import csv
import statistics
import sys

from core.formula import q, ref as R
from core.model import NEED_CODE_CHECK
from core.repo import ROOT

from . import _balance as B
from . import _game as G
from . import _layer_b as LB

MS = LB.SCRIPTS + "Game/Match/ModeSessions.cs"
SHOW = LB.SCRIPTS + "Game/Match/ShowdownSession.cs"
QM = LB.SCRIPTS + "Sim/Modes/QuickModes.cs"
CQ = LB.SCRIPTS + "Sim/Modes/ConquestMode.cs"
SG = LB.SCRIPTS + "Sim/Modes/SiegeModes.cs"
SB = LB.SCRIPTS + "Sim/Modes/SandboxMode.cs"
SDM = LB.SCRIPTS + "Sim/Modes/ShowdownMode.cs"
ECO = LB.SCRIPTS + "Sim/Economy/EconomySystem.cs"
AI = LB.SCRIPTS + "Sim/AI/ConquestAi.cs"
HUNTS = LB.SCRIPTS + "Game/Match/BossHunts.cs"
AUDIT = "Tools/audit/mode_static_audit.py"
MAP_CSV = "Docs/checks/map_audit.csv"
DIFFS = ["Easy", "Normal", "Hard", "VeryHard"]
SHARES = (25, 50, 75, 100)
N = r"([\d.]+)f"


def _side_literals(ctx):
    """{mode: {player_cp, player_income: {diff: x}, enemy_cp: {diff: x}, enemy_income, enemy_mode, bonus, cites}} from the
    C# sessions (Normal-independent unless the C# switches on the difficulty)."""
    out = {}

    def pair(path, pat, after, what):
        g, line = LB.cs_find(ctx, path, pat, after=after, what=what)
        return (None, f"{path} (không tìm thấy: {what})") if g is None else ([float(x) for x in g], f"{LB.short(path)}:{line}")

    def every(x):
        return {d: x for d in DIFFS}

    # Conquest: ConquestRules.StartCp, TeamEconomy's default income, the enemy's x1.18, PointIncome per point held
    cp, c1 = LB.cs_num(ctx, CQ, r"public float StartCp \{ get; set; \} = " + N, what="ConquestRules.StartCp")
    inc, c2 = LB.cs_num(ctx, ECO, r"float startCp = [\d.]+f, float income = " + N, what="TeamEconomy income default")
    k, c3 = LB.cs_num(ctx, MS, r"enemy\.ScaleIncome\(" + N + r"\)", after="class ConquestSession", what="Conquest enemy x")
    g, c4 = pair(MS, r"Bleed = " + N + r", PointIncome = " + N, "class ConquestSession", "Conquest PointIncome")
    out["conquest"] = {"player_cp": every(cp), "player_income": every(inc), "enemy_cp": every(cp), "enemy_income": inc,
                       "enemy_mode": k, "bonus": (g[1] * 1.5 if g else NEED_CODE_CHECK),
                       "bonus_note": "PointIncome x 1,5 cứ điểm (chia đều 3 cứ điểm)", "cites": [c1, c2, c3, c4]}
    for mode, cls, path in (("deathmatch", "class DeathmatchSession", MS), ("hill", "class HillSession", MS),
                            ("showdown", "class ShowdownSession", SHOW)):
        g, c = pair(path, r"Player = PlayerSide\(" + N + ", " + N + r"\), Enemy = EnemySide\(" + N + ", " + N, cls, f"{mode} sides")
        g = g or [NEED_CODE_CHECK] * 4
        out[mode] = {"player_cp": every(g[0]), "player_income": every(g[1]), "enemy_cp": every(g[2]), "enemy_income": g[3],
                     "enemy_mode": 1.0, "bonus": 0.0, "bonus_note": "", "cites": [c]}
    hb, ch = LB.cs_num(ctx, QM, r"e0\.Bonus = hill\.Owner == PlayerTeam \? " + N, what="Hill holder bonus")
    out["hill"]["bonus"] = hb * 0.5 if isinstance(hb, float) else hb
    out["hill"]["bonus_note"] = "bên giữ đồi +0,35 CP/s, mỗi bên giữ một nửa thời gian"
    out["hill"]["cites"].append(ch)
    g, c = pair(MS, r"Attacker = PlayerSide\(" + N + ", " + N + r"\), Defender = EnemySide\(" + N + ", " + N,
                "class AssaultSession", "Assault sides")
    g = g or [NEED_CODE_CHECK] * 4
    out["assault"] = {"player_cp": every(g[0]), "player_income": every(g[1]), "enemy_cp": every(g[2]), "enemy_income": g[3],
                      "enemy_mode": 1.0, "bonus": 0.0, "bonus_note": "thưởng khu (8 CP, +0,25 CP/s mỗi khu) không tính",
                      "cites": [c]}
    for mode in ("defend", "endless"):
        gp, cp_ = pair(MS, r"var defender = PlayerSide\(" + N + ", " + N + r"\)", "class DefendSession", "Defend player")
        ge, ce = pair(MS, r"var attacker = EnemySide\(" + N + ", " + N, "class DefendSession", "Defend enemy")
        gp, ge = gp or [NEED_CODE_CHECK] * 2, ge or [NEED_CODE_CHECK] * 2
        out[mode] = {"player_cp": every(gp[0]), "player_income": every(gp[1]), "enemy_cp": every(ge[0]),
                     "enemy_income": ge[1], "enemy_mode": 1.0, "bonus": 0.0, "bonus_note": "", "cites": [cp_, ce]}
    gp, cp_ = pair(MS, r"var attacker = PlayerSide\(" + N + ", " + N + r"\)", "class WeeklySession", "Weekly player")
    ge, ce = pair(MS, r"Defender = EnemySide\(" + N + ", " + N, "class WeeklySession", "Weekly enemy")
    gp, ge = gp or [NEED_CODE_CHECK] * 2, ge or [NEED_CODE_CHECK] * 2
    out["weekly"] = {"player_cp": every(gp[0]), "player_income": every(gp[1]), "enemy_cp": every(ge[0]), "enemy_income": ge[1],
                     "enemy_mode": 1.0, "bonus": 0.0, "bonus_note": "", "cites": [cp_, ce]}
    gp, cp_ = pair(MS, r"var attacker = PlayerSide\(" + N + ", " + N + r"\)", "class SiegeSession", "Siege player")
    ge, ce = pair(MS, r"EnemySide\(hard \? " + N + " : " + N + ", " + N, "class SiegeSession", "Siege enemy")
    gp, ge = gp or [NEED_CODE_CHECK] * 2, ge or [NEED_CODE_CHECK] * 3
    out["siege"] = {"player_cp": every(gp[0]), "player_income": every(gp[1]),
                    "enemy_cp": {"Easy": ge[1], "Normal": ge[1], "Hard": ge[0], "VeryHard": ge[0]}, "enemy_income": ge[2],
                    "enemy_mode": 1.0, "bonus": 0.0, "bonus_note": "", "cites": [cp_, ce]}
    g, c = pair(MS, r"PlayerSide\(" + N + r", Difficulty switch \{ AiDifficulty\.VeryHard => " + N +
                r", AiDifficulty\.Hard => " + N + r", _ => " + N, "class BossRushSession", "Boss Rush player")
    g = g or [NEED_CODE_CHECK] * 4
    out["bossrush"] = {"player_cp": every(g[0]), "player_income": {"Easy": g[3], "Normal": g[3], "Hard": g[2], "VeryHard": g[1]},
                       "enemy_cp": None, "enemy_income": None, "enemy_mode": None, "bonus": 0.0,
                       "bonus_note": "thưởng boss (8 CP mỗi 25 % máu, 12 khi hạ) không tính", "cites": [c]}
    g, c = pair(MS, r"TeamEconomy\(PlayerTeam, " + N + ", income: " + N, "class SurvivalSession", "Survival player")
    g = g or [NEED_CODE_CHECK] * 2
    out["survival"] = {"player_cp": every(g[0]), "player_income": every(g[1]), "enemy_cp": None, "enemy_income": None,
                       "enemy_mode": None, "bonus": 0.0, "bonus_note": "", "cites": [c]}
    return out


def _buy_profile(ctx):
    """BuyProfile.For(difficulty).Income (Sim/AI/ConquestAi.cs): the enemy's income by difficulty (its last argument)."""
    out = {}
    for d, pat in (("Easy", r"AiDifficulty\.Easy => new BuyProfile\(([^)]*)\)"), ("Normal", r"AiDifficulty\.Normal => new BuyProfile\(([^)]*)\)"),
                   ("Hard", r"AiDifficulty\.Hard => new BuyProfile\(([^)]*)\)"), ("VeryHard", r"_ => new BuyProfile\(([^)]*)\)")):
        g, line = LB.cs_find(ctx, AI, pat, after="public static BuyProfile For", what=f"BuyProfile {d}")
        out[d] = (float(g[0].split(",")[-1].strip().rstrip("f")), f"{LB.short(AI)}:{line}") if g else (NEED_CODE_CHECK, AI)
    return out


def _clock_literals(ctx):
    """Clock literals at Normal by mode (C#): start, stage bonuses, bank cap; the waves' timing (Survival)."""
    lit = {}
    g, l1 = LB.cs_find(ctx, MS, r"Difficulty switch \{ AiDifficulty\.VeryHard => " + N + r", AiDifficulty\.Hard => " + N +
                       r", AiDifficulty\.Easy => " + N + r", _ => " + N, after="class AssaultSession", what="Assault clock")
    lit["assault_start"] = (float(g[3]) if g else NEED_CODE_CHECK, f"{LB.short(MS)}:{l1}")
    g, l2 = LB.cs_find(ctx, MS, r"Difficulty switch \{ AiDifficulty\.VeryHard => " + N + r", AiDifficulty\.Hard => " + N +
                       r", AiDifficulty\.Easy => " + N + r", _ => " + N, after="class SiegeSession", what="Siege clock")
    g2, l3 = LB.cs_find(ctx, MS, r"StageBonus = new\[\] \{ " + N + ", " + N + r" \}, MaxBank = " + N, after="class SiegeSession",
                        what="Siege stage bonus")
    lit["siege"] = (float(g[3]) if g else NEED_CODE_CHECK, (float(g2[0]) + float(g2[1])) if g2 else NEED_CODE_CHECK, float(g2[2]) if g2 else NEED_CODE_CHECK,
                    f"{LB.short(MS)}:{l2}, {l3}")
    g, l4 = LB.cs_find(ctx, MS, r"StartSeconds = hard \? " + N + " : easy \\? " + N + " : " + N + r", StageBonus = new\[\] \{ " + N +
                       ", " + N + r" \}, MaxBank = " + N, after="class DefendSession", what="Defend clock")
    lit["defend"] = (float(g[2]) if g else NEED_CODE_CHECK, (float(g[3]) + float(g[4])) if g else NEED_CODE_CHECK, float(g[5]) if g else NEED_CODE_CHECK,
                     f"{LB.short(MS)}:{l4}")
    g, l5 = LB.cs_find(ctx, MS, r"StartSeconds = " + N + ", StartStage", after="class WeeklySession", what="Weekly clock")
    g2, l6 = LB.cs_find(ctx, SG, r"public float\[\] StageBonus \{ get; set; \} = \{ " + N + ", " + N + r" \};\s*public float MaxBank \{ get; set; \} = " + N,
                        after="class SiegeRules", what="SiegeRules defaults")
    lit["weekly"] = (float(g[0]) if g else NEED_CODE_CHECK, (float(g2[0]) + float(g2[1])) if g2 else NEED_CODE_CHECK, float(g2[2]) if g2 else NEED_CODE_CHECK,
                     f"{LB.short(MS)}:{l5}, {LB.short(SG)}:{l6}")
    first, c7 = LB.cs_num(ctx, SB, r"const float FirstWaveDelay = " + N, what="Survival first wave")
    every, c8 = LB.cs_num(ctx, SB, r"const float WaveInterval = " + N, what="Survival wave interval")
    lit["survival"] = (first, every, f"{c7}, {c8}")
    mins, c9 = LB.cs_num(ctx, HUNTS, r"const float WeeklyMinutes = " + N, what="BossHunts.WeeklyMinutes")
    lit["bossrush"] = (mins * 60.0 if isinstance(mins, float) else mins, c9)
    # which rules' Apply reads matchRules "timeLimit" (the others keep their C# clock)
    reads = {}
    for mode, path, after, until in (("conquest", CQ, "public void Apply", "}"), ("deathmatch", QM, 'RulesId { get; set; } = "deathmatch"', "public"),
                                     ("hill", QM, 'RulesId { get; set; } = "hill"', "public"), ("showdown", SDM, "public void Apply", "}"),
                                     ("siege", SG, "public void Apply", "/// <summary>"), ("weekly", SG, "public void Apply", "/// <summary>"),
                                     ("defend", SG, "public void Apply", "/// <summary>")):
        text = LB.cs_text(path)
        i = text.find(after)
        j = text.find("\n        }", i) if i >= 0 else -1
        reads[mode] = i >= 0 and '"timeLimit"' in text[i:j if j > 0 else None]
    reads["assault"] = False  # AssaultRules.Apply reads "start" (StartSeconds = start x the difficulty's clock / 300)
    lit["reads"] = reads
    return lit


def _audit(ctx):
    """Tools/audit/mode_static_audit.py: its MODES table and constants (ported on the exporter's balance.json read)."""
    sys.path.insert(0, str(ROOT / "Tools" / "audit"))
    try:
        import mode_static_audit as A  # noqa: WPS433
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"05 Kiem_tinh_che_do: {AUDIT} unreadable ({type(e).__name__}: {e})")
        return None, {}
    finally:
        sys.path.pop(0)
    b = B.bal(ctx)
    vehicles = {v["id"]: v for v in b["vehicles"]}
    roster = [vehicles[i] for i in A.WAVE_ROSTER if i in vehicles]
    k = {"mean_cp": statistics.mean(v.get("cp", 0) for v in roster),
         "hp_per_cp": statistics.mean(v.get("hp", 0) / max(1, v.get("cp", 1)) for v in roster)}
    towers = [v for v in b["vehicles"] if v.get("static") and v.get("fort") and v.get("hp")]
    k["tower_eq"] = statistics.mean(v["hp"] for v in towers) / k["hp_per_cp"] if towers else 10.0
    k["mini_eq"] = vehicles.get("bastion_mk0", {}).get("hp", 6000) / k["hp_per_cp"]
    k["main_eq"] = vehicles.get("behemoth", {}).get("hp", 15000) / k["hp_per_cp"]
    levels = b.get("base", {}).get("levels", [])
    k["base_towers"] = sum(levels[2].get(x, 0) for x in ("small", "medium", "large")) if len(levels) > 2 else 7
    return A, k


def _tempo(mode):
    """mode_static_audit.tempo as numbers: median path drop zone -> first objective / the tank's 6.5 m/s, per side."""
    p = ROOT / MAP_CSV
    if not p.exists():
        return "", ""
    suffix = "_siege" if mode in ("Siege", "Weekly") else "_long" if mode == "Defend" else "_conquest"
    rows = [r for r in csv.DictReader(p.open(encoding="utf-8")) if r["map"].endswith(suffix)]
    out = []
    for key in ("pathToObjective0", "pathToObjective1"):
        vals = [float(r[key]) for r in rows if r[key]]
        out.append(statistics.median(vals) / 6.5 if vals else "")
    return tuple(out)


MODE_ID = {"Conquest": "conquest", "Deathmatch": "deathmatch", "KingOfTheHill": "hill", "Assault": "assault", "Siege": "siege",
           "Weekly": "weekly", "Defend": "defend", "Survival": "survival", "BossRush": "bossrush"}


def build(ctx, book, d):
    cd = book.sheets["Che_do"]
    kt = book.sheets["Kinh_te"]
    eco = d.get("economy") or {}
    nums = {mid: ((d.get("matchRules") or {}).get("modes") or {}).get(mid, {}).get("numbers") or {} for mid in cd.rows}
    sides = _side_literals(ctx)
    buy = _buy_profile(ctx)
    lit = _clock_literals(ctx)

    def num(mid, col):
        v = cd.rows[mid].values.get(col)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else ""

    # ------------------------------------------------------------------ Che_do_thoi_luong
    tl = book.sheet("Che_do_thoi_luong", "Chế độ: thời lượng lý thuyết", "Thời lượng lý thuyết mỗi chế độ ở độ khó Bình thường: "
                    "giờ của dữ liệu (matchRules.numbers) và của mã (đồng hồ quỹ giờ, thưởng giai đoạn, trần quỹ), hiệp phụ, "
                    "thắng sớm nhất theo công thức điểm / bleed; thời lượng tham chiếu cho Kinh_te_suy_ra", layer="B")
    tl.col("id", fk=["05_che_do_kinh_te/Che_do"], meaning="chế độ (Che_do.id)")
    data_cols = (
        ("doc_gio_du_lieu", "", "Rules.Apply của chế độ đọc matchRules.numbers.timeLimit (port: tìm khóa \"timeLimit\" trong Apply ở C#)"),
        ("gio_bat_dau_ma_s", "s", "đồng hồ lúc vào trận ở Bình thường, số trong mã (Assault: số của độ khó, game dùng numbers.start x số / 300; "
                                  "Siege / Defend / Weekly: StartSeconds; Boss Rush: BossHunts.WeeklyMinutes x 60)"),
        ("thuong_giai_doan_s", "s", "tổng thưởng giờ khi qua giai đoạn trong mã (Siege / Defend / Weekly: StageBonus)"),
        ("tran_quy_ma_s", "s", "trần quỹ giờ trong mã (MaxBank)"),
        ("dot_dau_s", "s", "Sinh tồn: đợt đầu (SandboxMode.FirstWaveDelay)"),
        ("cach_dot_s", "s", "Sinh tồn: khoảng giữa hai đợt (SandboxMode.WaveInterval)"),
        ("nguon_ma", "", "file:dòng của các số trong mã"))
    for c, unit, m in data_cols:
        tl.col(c, unit=unit, meaning=m, source_note="C#: " + m)
    X = lambda col: R("Che_do", col)  # noqa: E731
    isn = lambda e: f"ISNUMBER({e})"  # noqa: E731
    T = {
        "gio_du_lieu_s": f"=IF({isn(X('numbers_time_limit_s'))},{X('numbers_time_limit_s')},{q('')})",
        "hiep_phu_s": f"=IF({isn(X('numbers_overtime'))},{X('numbers_overtime')},0)+IF({isn(X('numbers_sudden_death'))},{X('numbers_sudden_death')},0)",
        "gio_vao_tran_s": (f"=IF(AND({{doc_gio_du_lieu}},{isn('{gio_du_lieu_s}')}),{{gio_du_lieu_s}},IF({isn(X('numbers_start'))},"
                       f"{X('numbers_start')}*{{gio_bat_dau_ma_s}}/300,IF({isn('{gio_bat_dau_ma_s}')},{{gio_bat_dau_ma_s}},{q('')})))"),
        "quy_cong_them_s": (f"=IF({isn(X('numbers_sector_bonus'))},2*MIN({X('numbers_sector_bonus')},{X('numbers_max_bank')}),"
                            f"IF({isn('{thuong_giai_doan_s}')},MIN({{thuong_giai_doan_s}},2*{{tran_quy_ma_s}}),0))"),
        "thoi_luong_toi_da_s": f"=IF({isn('{gio_vao_tran_s}')},{{gio_vao_tran_s}}+{{quy_cong_them_s}}+{{hiep_phu_s}},{q('')})",
        "thang_som_nhat_s": (f"=IF({isn(X('numbers_bleed'))},IF({X('numbers_points')}/({X('numbers_bleed')}*3)<={X('numbers_time_limit_s')}-"
                             f"{X('numbers_final_phase')},{X('numbers_points')}/({X('numbers_bleed')}*3),{X('numbers_time_limit_s')}-"
                             f"{X('numbers_final_phase')}+({X('numbers_points')}-{X('numbers_bleed')}*3*({X('numbers_time_limit_s')}-"
                             f"{X('numbers_final_phase')}))/({X('numbers_bleed')}*3*{X('numbers_final_scale')})),"
                             f"IF({isn(X('numbers_per_second'))},{X('numbers_target')}/{X('numbers_per_second')},{q('')}))"),
        "so_ha_toi_thieu": f"=IF({isn(X('numbers_kill_cap'))},CEILING({X('numbers_target')}/{X('numbers_kill_cap')},1),{q('')})",
        "dot_cuoi_bat_dau_s": f"=IF({isn('{dot_dau_s}')},{{dot_dau_s}}+({X('numbers_waves')}-1)*{{cach_dot_s}},{q('')})",
        "thoi_luong_tham_chieu_s": (f"=IF({isn('{thoi_luong_toi_da_s}')},{{thoi_luong_toi_da_s}},IF({isn('{dot_cuoi_bat_dau_s}')},"
                                    f"{{dot_cuoi_bat_dau_s}},{q('')}))"),
        "lech_gio_du_lieu_s": (f"=IF(AND({isn('{gio_du_lieu_s}')},{isn('{gio_bat_dau_ma_s}')},NOT({{doc_gio_du_lieu}})),{{gio_du_lieu_s}}-"
                               f"({{gio_bat_dau_ma_s}}+{{quy_cong_them_s}}),{q('')})"),
    }
    META = {
        "gio_du_lieu_s": ("s", "giờ ghi trong dữ liệu (Che_do.numbers_time_limit_s)"),
        "hiep_phu_s": ("s", "hiệp phụ + đột tử (numbers.overtime + numbers.suddenDeath)"),
        "gio_vao_tran_s": ("s", "đồng hồ game dùng lúc vào trận: giờ dữ liệu nếu Apply đọc nó; Assault numbers.start x hệ số; còn lại số trong mã"),
        "quy_cong_them_s": ("s", "giờ cộng thêm tối đa: Assault 2 khu x min(sectorBonus, maxBank); quỹ giai đoạn min(tổng thưởng, 2 x trần)"),
        "thoi_luong_toi_da_s": ("s", "thời lượng tối đa lý thuyết: đồng hồ + giờ cộng thêm + hiệp phụ (mỗi thưởng đến đúng lúc hết giờ)"),
        "thang_som_nhat_s": ("s", "thắng sớm nhất: Conquest giữ cả 3 cứ điểm từ đầu (points / (bleed x 3), pha cuối x finalScale); "
                                  "Vua đồi target / perSecond"),
        "so_ha_toi_thieu": ("", "Tử chiến: số xe địch tối thiểu phải hạ (target / killCap, làm tròn lên)"),
        "dot_cuoi_bat_dau_s": ("s", "Sinh tồn: lúc đợt cuối bắt đầu (đợt đầu + (waves - 1) x khoảng đợt)"),
        "thoi_luong_tham_chieu_s": ("s", "thời lượng tham chiếu cho Kinh_te_suy_ra (100 %): thời lượng tối đa, Sinh tồn lúc đợt cuối; "
                                         "trống: không giới hạn (Vô tận) hoặc theo nhiệm vụ (Tác chiến)"),
        "lech_gio_du_lieu_s": ("s", "giờ dữ liệu - (đồng hồ mã + giờ cộng thêm) khi Apply không đọc giờ dữ liệu (khác 0: số dữ liệu chỉ để đọc)"),
    }
    for c, t in T.items():
        LB.declare(tl, c, t, "Che_do numbers + số trong mã (Game/Match/ModeSessions.cs, Sim/Modes)", unit=META[c][0],
                   meaning=META[c][1], game=False)
    ref_len = {}
    for mid in sorted(cd.rows):
        x = tl.row(mid, f"05/Che_do ({mid}) + C# của chế độ")
        reads = lit["reads"].get(mid, False)
        x.set("doc_gio_du_lieu", reads)
        start = bonus = cap = first = every = ""
        cites = []
        if mid == "assault":
            start, c = lit["assault_start"]
            cites.append(c)
        elif mid in ("siege", "defend", "weekly"):
            start, bonus, cap, c = lit[mid]
            cites.append(c)
        elif mid == "bossrush":
            start, c = lit["bossrush"]
            cites.append(c)
        elif mid == "survival":
            first, every, c = lit["survival"]
            cites.append(c)
        for col, v in (("gio_bat_dau_ma_s", start), ("thuong_giai_doan_s", bonus), ("tran_quy_ma_s", cap), ("dot_dau_s", first),
                       ("cach_dot_s", every)):
            x.set(col, v)
        x.set("nguon_ma", "; ".join(cites))
        # the Python of the same rule (the reference of each formula)
        tlim = num(mid, "numbers_time_limit_s")
        ot = (num(mid, "numbers_overtime") or 0.0) + (num(mid, "numbers_sudden_death") or 0.0)
        fl = lambda v: isinstance(v, float)  # noqa: E731
        if reads and fl(tlim):
            game = tlim
        elif fl(num(mid, "numbers_start")) and fl(start):
            game = num(mid, "numbers_start") * start / 300
        elif fl(start):
            game = start
        else:
            game = ""
        if fl(num(mid, "numbers_sector_bonus")):
            extra = 2 * min(num(mid, "numbers_sector_bonus"), num(mid, "numbers_max_bank"))
        elif fl(bonus):
            extra = min(bonus, 2 * cap)
        else:
            extra = 0.0
        mx = game + extra + ot if fl(game) else ""
        if fl(num(mid, "numbers_bleed")):
            p, b_, fp, fs = num(mid, "numbers_points"), num(mid, "numbers_bleed"), num(mid, "numbers_final_phase"), num(mid, "numbers_final_scale")
            early = p / (b_ * 3) if p / (b_ * 3) <= tlim - fp else tlim - fp + (p - b_ * 3 * (tlim - fp)) / (b_ * 3 * fs)
        elif fl(num(mid, "numbers_per_second")):
            early = num(mid, "numbers_target") / num(mid, "numbers_per_second")
        else:
            early = ""
        kills = float(-(-num(mid, "numbers_target") // num(mid, "numbers_kill_cap"))) if fl(num(mid, "numbers_kill_cap")) else ""
        last = first + (num(mid, "numbers_waves") - 1) * every if fl(first) and fl(every) else ""
        refl = mx if fl(mx) else last
        gap = tlim - (start + extra) if fl(tlim) and fl(start) and not reads else ""
        ref_len[mid] = refl
        for c, v in (("gio_du_lieu_s", tlim), ("hiep_phu_s", ot), ("gio_vao_tran_s", game), ("quy_cong_them_s", extra),
                     ("thoi_luong_toi_da_s", mx), ("thang_som_nhat_s", early), ("so_ha_toi_thieu", kills),
                     ("dot_cuoi_bat_dau_s", last), ("thoi_luong_tham_chieu_s", refl), ("lech_gio_du_lieu_s", gap)):
            LB.put(x, c, T[c], v, game=False)

    # ------------------------------------------------------------------ Kinh_te_suy_ra
    ks = book.sheet("Kinh_te_suy_ra", "Kinh tế suy ra", "CP mỗi bên đã kiếm được (CP khởi đầu + thu nhập x thời gian) ở 25 / 50 / 75 / "
                    "100 % thời lượng tham chiếu (Che_do_thoi_luong), theo chế độ x độ khó; thu nhập theo TeamEconomy.Earning "
                    "(upkeep, bắt kịp, commander, hạ xe, biến cố không tính); Tác chiến / chiến dịch: theo nhiệm vụ (07)", layer="B")
    ks.col("id", meaning="<chế độ>/<độ khó>")
    ks.col("che_do", fk=["05_che_do_kinh_te/Che_do"], meaning="chế độ")
    ks.col("do_kho", fk=["05_che_do_kinh_te/Do_kho"], meaning="độ khó")
    for c, unit, m in (("cp_khoi_dau_nguoi_choi_ma", "CP", "CP khởi đầu người chơi trong mã của phiên chế độ (trước startCp.scale)"),
                       ("thu_nhap_nguoi_choi_ma_cp_s", "CP/s", "thu nhập người chơi trong mã (trước economy.income)"),
                       ("cp_khoi_dau_dich_ma", "CP", "CP khởi đầu địch trong mã (trống: địch không có kinh tế)"),
                       ("thu_nhap_dich_ma_cp_s", "CP/s", "thu nhập địch trong mã"),
                       ("he_so_dich_che_do", "", "ScaleIncome riêng của chế độ cho địch (Giữ cứ điểm 1,18)"),
                       ("he_so_dich_do_kho", "", "BuyProfile.For(độ khó).Income (Sim/AI/ConquestAi.cs; ModeSession.Create nhân thu nhập địch)"),
                       ("thuong_muc_tieu_cp_s", "CP/s", "thưởng mục tiêu mỗi bên giả định chia đều (TeamEconomy.Bonus; ghi chú ở ghi_chu)"),
                       ("ghi_chu", "", "giả định của dòng"), ("nguon_ma", "", "file:dòng của các số trong mã")):
        ks.col(c, unit=unit, meaning=m, source_note="C#: " + m)
    K = lambda rid: R("Kinh_te", "gia_tri_so", rid)  # noqa: E731
    name = f"{R('Che_do', 'ten_che_do', 'MODE')}"
    listed = f"ISNUMBER(FIND({q(';')}&{name}&{q(';')},{q(';')}&{R('Kinh_te', 'gia_tri_chu', 'economy.startCp.modes')}&{q(';')}))"
    scale_s = K("economy.startCp.scale")

    def start_f(col):
        return (f"=IF({isn('{' + col + '}')},IF(AND({listed},{{{col}}}>0,{scale_s}<>1),ROUND({{{col}}}*{scale_s},0),{{{col}}}),{q('')})")
    KT = {
        "cp_khoi_dau_nguoi_choi": start_f("cp_khoi_dau_nguoi_choi_ma"),
        "cp_khoi_dau_dich": start_f("cp_khoi_dau_dich_ma"),
        "thu_nhap_nguoi_choi_cp_s": f"=({{thu_nhap_nguoi_choi_ma_cp_s}}+{{thuong_muc_tieu_cp_s}})*{K('economy.income')}",
        "thu_nhap_dich_cp_s": (f"=IF({isn('{thu_nhap_dich_ma_cp_s}')},({{thu_nhap_dich_ma_cp_s}}+{{thuong_muc_tieu_cp_s}})*"
                               f"{K('economy.income')}*{{he_so_dich_che_do}}*{{he_so_dich_do_kho}},{q('')})"),
        "thoi_luong_tham_chieu_s": f"={R('Che_do_thoi_luong', 'thoi_luong_tham_chieu_s', 'MODE')}",
    }
    KM = {
        "cp_khoi_dau_nguoi_choi": ("CP", "CP khởi đầu người chơi game dùng (x startCp.scale, làm tròn nửa lên, nếu chế độ có trong startCp.modes)",
                                   "Sim/Content/OpeningRules.cs StartCp (SimWorld.EnableEconomy)"),
        "cp_khoi_dau_dich": ("CP", "CP khởi đầu địch game dùng", "Sim/Content/OpeningRules.cs StartCp (SimWorld.EnableEconomy)"),
        "thu_nhap_nguoi_choi_cp_s": ("CP/s", "thu nhập người chơi mỗi giây (upkeep 1, bắt kịp 1, không commander)",
                                     "Sim/Economy/EconomySystem.cs TeamEconomy.Earning"),
        "thu_nhap_dich_cp_s": ("CP/s", "thu nhập địch mỗi giây (x hệ số chế độ x hệ số độ khó)",
                               "Sim/Economy/EconomySystem.cs TeamEconomy.Earning + ScaleIncome (ModeSession.Create, ConquestSession)"),
    }
    for c, (unit, m, ref_) in KM.items():
        LB.declare(ks, c, KT[c], ref_, unit=unit, meaning=m)
    LB.declare(ks, "thoi_luong_tham_chieu_s", KT["thoi_luong_tham_chieu_s"], "Che_do_thoi_luong.thoi_luong_tham_chieu_s",
               unit="s", meaning="thời lượng tham chiếu của chế độ (100 %)", game=False)
    for side, start, inc in (("nguoi_choi", "cp_khoi_dau_nguoi_choi", "thu_nhap_nguoi_choi_cp_s"), ("dich", "cp_khoi_dau_dich", "thu_nhap_dich_cp_s")):
        for p in SHARES:
            KT[f"cp_{side}_{p}"] = (f"=IF(AND({isn('{thoi_luong_tham_chieu_s}')},{isn('{' + start + '}')}),{{{start}}}+{{{inc}}}*"
                                    f"{p / 100}*{{thoi_luong_tham_chieu_s}},{q('')})")
            LB.declare(ks, f"cp_{side}_{p}", KT[f"cp_{side}_{p}"], f"CP khởi đầu + thu nhập x {p} % thời lượng", unit="CP",
                       meaning=f"CP {'người chơi' if side == 'nguoi_choi' else 'địch'} đã kiếm được ở {p} % thời lượng", game=False)
    KT["ty_le_dich_nguoi_choi_100"] = f"=IF(AND({isn('{cp_dich_100}')},{isn('{cp_nguoi_choi_100}')}),{{cp_dich_100}}/{{cp_nguoi_choi_100}},{q('')})"
    LB.declare(ks, "ty_le_dich_nguoi_choi_100", KT["ty_le_dich_nguoi_choi_100"], "cp_dich_100 / cp_nguoi_choi_100", game=False,
               meaning="CP địch / CP người chơi ở 100 %")
    income = float(eco.get("income", 1.0))
    sc = (eco.get("startCp") or {})
    start_modes = set(sc.get("modes") or [])
    for mid in sorted(sides):
        if mid not in cd.rows:
            continue
        s = sides[mid]
        nm = cd.rows[mid].values.get("ten_che_do")
        for dname in DIFFS:
            rid = f"{mid}/{dname}"
            x = ks.row(rid, f"C#: {'; '.join(s['cites'])}; {buy[dname][1]}")
            x.set("che_do", mid)
            x.set("do_kho", dname)
            pc, pi = s["player_cp"][dname], s["player_income"][dname]
            ec = s["enemy_cp"][dname] if s["enemy_cp"] else ""
            ei = s["enemy_income"] if s["enemy_income"] is not None else ""
            em = s["enemy_mode"] if s["enemy_mode"] is not None else ""
            ed = buy[dname][0] if s["enemy_cp"] else ""
            bonus = s["bonus"]
            for c, v in (("cp_khoi_dau_nguoi_choi_ma", pc), ("thu_nhap_nguoi_choi_ma_cp_s", pi), ("cp_khoi_dau_dich_ma", ec),
                         ("thu_nhap_dich_ma_cp_s", ei), ("he_so_dich_che_do", em), ("he_so_dich_do_kho", ed),
                         ("thuong_muc_tieu_cp_s", bonus), ("ghi_chu", s["bonus_note"]),
                         ("nguon_ma", "; ".join(s["cites"] + ([buy[dname][1]] if s["enemy_cp"] else [])))):
                x.set(c, v)
            ok = all(isinstance(v, float) for v in (pc, pi, bonus))
            sp = G.start_cp(pc, float(sc.get("scale", 1.0)), nm in start_modes) if ok else NEED_CODE_CHECK
            ip = G.earning(pi, bonus, income) if ok else NEED_CODE_CHECK
            okd = all(isinstance(v, float) for v in (ec, ei, em, ed))
            se = G.start_cp(ec, float(sc.get("scale", 1.0)), nm in start_modes) if okd else ""
            ie = G.earning(ei, bonus, income * em * ed) if okd else ""
            for c, v in (("cp_khoi_dau_nguoi_choi", sp), ("cp_khoi_dau_dich", se), ("thu_nhap_nguoi_choi_cp_s", ip),
                         ("thu_nhap_dich_cp_s", ie)):
                LB.put(x, c, KT[c].replace("MODE", mid), v)
            L = ref_len.get(mid, "")
            LB.put(x, "thoi_luong_tham_chieu_s", KT["thoi_luong_tham_chieu_s"].replace("MODE", mid), L, game=False)
            vals = {}
            for side, a, b_ in (("nguoi_choi", sp, ip), ("dich", se, ie)):
                for p in SHARES:
                    v = a + b_ * (p / 100) * L if isinstance(L, float) and isinstance(a, float) and isinstance(b_, float) else ""
                    vals[f"cp_{side}_{p}"] = v
                    LB.put(x, f"cp_{side}_{p}", KT[f"cp_{side}_{p}"], v, game=False)
            r_ = vals["cp_dich_100"] / vals["cp_nguoi_choi_100"] if vals["cp_dich_100"] != "" and vals["cp_nguoi_choi_100"] else ""
            LB.put(x, "ty_le_dich_nguoi_choi_100", KT["ty_le_dich_nguoi_choi_100"], r_, game=False)

    # ------------------------------------------------------------------ Kiem_tinh_che_do (4 books)
    A, k = _audit(ctx)
    if A is None:
        return
    kc = book.sheet("Kiem_tinh_che_do", "Kiểm tĩnh chế độ (4 sổ)", "Bốn sổ của kiểm tĩnh chế độ (Tools/audit/mode_static_audit.py, prompt 30 L8) "
                    "ở 25 / 50 / 75 / 100 % thời lượng mục tiêu, Bình thường: Kinh tế (CP khởi đầu + thu nhập x giây, từ Kinh_te_suy_ra), "
                    "Quân miễn phí / kịch bản (đợt, boss: CP tương đương), Sức mạnh tĩnh (tháp, pháo đài), Nhịp (giây từ bãi thả tới mục "
                    "tiêu đầu); dải = địch / người chơi; chế độ đối xứng: lệch > 30 % RED, 20-30 % YELLOW", layer="B")
    kc.col("id", meaning="<chế độ>/<phần trăm>")
    kc.col("che_do", fk=["05_che_do_kinh_te/Che_do"], meaning="chế độ")
    for c, unit, m in (("phan_tram", "%", "mốc phần trăm thời lượng mục tiêu"),
                       ("doi_xung", "", "chế độ đối xứng (so 1:1); bất đối xứng: báo theo vai, không xếp màu"),
                       ("thoi_luong_muc_tieu_s", "s", "thời lượng mục tiêu: giữa khoảng phút thiết kế của bản kiểm (MODES.minutes)"),
                       ("mien_phi_nguoi_choi_cp", "CP", "sổ 2: quân miễn phí / kịch bản của người chơi (CP tương đương)"),
                       ("mien_phi_dich_cp", "CP", "sổ 2: đợt (số xe x CP trung bình của đội hình đợt) và boss (máu / máu mỗi CP) của địch"),
                       ("tinh_nguoi_choi_cp", "CP", "sổ 3: phòng thủ cố định của người chơi (tháp căn cứ cấp 3 x CP tương đương một tháp)"),
                       ("tinh_dich_cp", "CP", "sổ 3: phòng thủ cố định của địch (ô pháo đài x CP tương đương một tháp)"),
                       ("nhip_nguoi_choi_s", "s", "sổ 4: trung vị quãng đường bãi thả -> mục tiêu đầu / 6,5 m/s (Docs/checks/map_audit.csv)"),
                       ("nhip_dich_s", "s", "sổ 4: như trên, bên địch")):
        kc.col(c, unit=unit, meaning=m, source_note=f"python: {AUDIT}" + (" + Docs/checks/map_audit.csv" if c.startswith("nhip") else ""))
    ksr = lambda col: R("Kinh_te_suy_ra", col, "MODE/Normal")  # noqa: E731
    KC = {
        "t_s": "={phan_tram}/100*{thoi_luong_muc_tieu_s}",
        "kinh_te_nguoi_choi_cp": f"={ksr('cp_khoi_dau_nguoi_choi')}+{ksr('thu_nhap_nguoi_choi_cp_s')}*{{t_s}}",
        "kinh_te_dich_cp": f"=IF({isn(ksr('cp_khoi_dau_dich'))},{ksr('cp_khoi_dau_dich')}+{ksr('thu_nhap_dich_cp_s')}*{{t_s}},0)",
        "tong_nguoi_choi_cp": "={kinh_te_nguoi_choi_cp}+{mien_phi_nguoi_choi_cp}+{tinh_nguoi_choi_cp}",
        "tong_dich_cp": "={kinh_te_dich_cp}+{mien_phi_dich_cp}+{tinh_dich_cp}",
        "dai_suc_manh": "={tong_dich_cp}/MAX(0.000001,{tong_nguoi_choi_cp})",
        "lech_pct": "=({dai_suc_manh}-1)*100",
        "trang_thai": (f"=IF({{doi_xung}},IF(ABS({{lech_pct}})>30,{q('RED')},IF(ABS({{lech_pct}})>20,{q('YELLOW')},{q('GREEN')})),"
                       f"{q('THEO_VAI')})"),
    }
    KCM = {"t_s": ("s", "giây ở mốc"), "kinh_te_nguoi_choi_cp": ("CP", "sổ 1: CP người chơi có thể đã tiêu (Kinh_te_suy_ra, Bình thường)"),
           "kinh_te_dich_cp": ("CP", "sổ 1: CP địch có thể đã tiêu"), "tong_nguoi_choi_cp": ("CP", "sức mạnh người chơi = sổ 1 + 2 + 3"),
           "tong_dich_cp": ("CP", "sức mạnh địch = sổ 1 + 2 + 3"), "dai_suc_manh": ("", "dải sức mạnh: địch / người chơi"),
           "lech_pct": ("%", "lệch % (dải - 1) x 100"), "trang_thai": ("", "GREEN / YELLOW / RED (đối xứng), THEO_VAI (bất đối xứng)")}
    for c, t in KC.items():
        LB.declare(kc, c, t, f"{AUDIT} (sổ, dải, ngưỡng 20 / 30 %)", unit=KCM[c][0], meaning=KCM[c][1], game=False,
                   enum=["GREEN", "YELLOW", "RED", "THEO_VAI"] if c == "trang_thai" else None)
    for mode, m in A.MODES.items():
        mid = MODE_ID.get(mode)
        if f"{mid}/Normal" not in ks.rows:
            continue
        lo, hi = m["minutes"]
        length = (lo + hi) / 2 * 60
        tp, te = _tempo(mode)
        kr = ks.rows[f"{mid}/Normal"].values
        for share in SHARES:
            t = length * share / 100
            # books 2 and 3 as the audit computes them
            ef = es = ps = 0.0
            if "waves" in m:
                w = m["waves"]
                n = max(0, int((t - w["first"]) // w["every"]) + 1) if t >= w["first"] else 0
                if mode == "Survival":
                    n = min(n, 10)
                ef = sum(min(w["max"], w["start"] + w["growth"] * (j - 1)) for j in range(1, n + 1)) * k["mean_cp"]
                for wave, kind in m.get("bosses", {}).items():
                    if n >= wave:
                        ef += k["mini_eq"] if kind == "mini" else k["main_eq"]
            if "bossesPer" in m:
                ef = m["bossesPer"] * (share / 100) * (k["mini_eq"] + k["main_eq"]) / 2
            if "fortressSlots" in m:
                es = m["fortressSlots"] * k["tower_eq"]
            if m.get("playerTowers"):
                ps = k["base_towers"] * k["tower_eq"]
            x = kc.row(f"{mid}/{share}", f"{AUDIT} MODES['{mode}'] + 05/Kinh_te_suy_ra ({mid}/Normal)")
            x.set("che_do", mid)
            for c, v in (("phan_tram", float(share)), ("doi_xung", bool(m["symmetric"])), ("thoi_luong_muc_tieu_s", length),
                         ("mien_phi_nguoi_choi_cp", 0.0), ("mien_phi_dich_cp", ef), ("tinh_nguoi_choi_cp", ps), ("tinh_dich_cp", es),
                         ("nhip_nguoi_choi_s", tp), ("nhip_dich_s", te)):
                x.set(c, v)
            sp = LB.F_value(kr.get("cp_khoi_dau_nguoi_choi"))
            ip = LB.F_value(kr.get("thu_nhap_nguoi_choi_cp_s"))
            se = LB.F_value(kr.get("cp_khoi_dau_dich"))
            ie = LB.F_value(kr.get("thu_nhap_dich_cp_s"))
            pe = sp + ip * t if isinstance(sp, float) and isinstance(ip, float) else NEED_CODE_CHECK
            ee = se + ie * t if isinstance(se, float) and isinstance(ie, float) else 0.0
            tot_p = pe + ps if isinstance(pe, float) else ""
            tot_e = ee + ef + es
            band = tot_e / max(1e-6, tot_p) if isinstance(tot_p, float) else ""
            gap = (band - 1) * 100 if band != "" else ""
            flag = ("RED" if abs(gap) > 30 else "YELLOW" if abs(gap) > 20 else "GREEN") if m["symmetric"] and gap != "" else "THEO_VAI"
            for c, v in (("t_s", t), ("kinh_te_nguoi_choi_cp", pe), ("kinh_te_dich_cp", ee), ("tong_nguoi_choi_cp", tot_p),
                         ("tong_dich_cp", tot_e), ("dai_suc_manh", band), ("lech_pct", gap), ("trang_thai", flag)):
                LB.put(x, c, KC[c].replace("MODE", mid), v, game=False)
