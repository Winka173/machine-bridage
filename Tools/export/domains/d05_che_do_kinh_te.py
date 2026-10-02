"""05_che_do_kinh_te, layer A: modes and match rules, campaign stars, leaderboards (endless), Operations (score, tiers,
weekly, mutators), the economy (balance.json economy, campaign economy), difficulty."""
from __future__ import annotations

from core.model import NEED_CODE_CHECK

from . import _balance as B
from . import _lane_c as C

FILE_ID = "05_che_do_kinh_te"
TITLE = "Chế độ và kinh tế"
DESC = "Chế độ và luật trận, sao chiến dịch, bảng xếp hạng (vô hạn), Tác chiến (điểm, bậc, tuần, mutator), kinh tế, độ khó"

OPS = C.DATA + "operations.json"
# matchRules.modes id -> the game's mode name (GameMode / economy.bankByMode / aiModeProfiles.modes / neutrals.modes)
MODE_NAME = {"assault": "Assault", "bossrush": "BossRush", "conquest": "Conquest", "deathmatch": "Deathmatch",
             "defend": "Defend", "endless": "Endless", "hill": "KingOfTheHill", "operations": "Operation",
             "showdown": "Showdown", "siege": "Siege", "survival": "Survival", "weekly": "Weekly"}
DIFFICULTIES = ["Easy", "Normal", "Hard", "VeryHard"]


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    camp = ctx.data(C.CAMPAIGN)
    eco = d.get("economy") or {}
    rules = d.get("matchRules") or {}
    profiles = (d.get("aiModeProfiles") or {}).get("modes") or {}
    neutral_modes = (d.get("neutrals") or {}).get("modes") or {}

    # ------------------------------------------------------------------ Che_do
    cd = book.sheet("Che_do", "Chế độ", "matchRules.modes: mỗi chế độ một dòng (luật thắng / thua, giờ, hiệp phụ, điểm, bắt kịp)")
    cd.col("ten_che_do", meaning="tên chế độ trong mã (GameMode: khóa của bankByMode / aiModeProfiles.modes)")
    cd.col("kho_cp", unit="CP", meaning="economy.bankByMode.<chế độ>: kho CP [người chơi; địch] (ngăn ';')")
    cd.col("cp_khoi_dau_nhan_he_so", meaning="chế độ có trong economy.startCp.modes (CP khởi đầu x startCp.scale)")
    cd.col("ho_so_ai", meaning="aiModeProfiles.modes.<chế độ> (06)", fk=["06_ai/AI_ho_so_che_do"])
    cd.col("trung_lap", meaning="neutrals.modes.<chế độ>: loại trung lập (08)")
    start_modes = set((eco.get("startCp") or {}).get("modes") or [])
    for mid, rec in (rules.get("modes") or {}).items():
        path = ("matchRules", "modes", mid)
        r = cd.row(mid, B.nguon(path), raw=rec)
        name = MODE_NAME.get(mid, mid[:1].upper() + mid[1:])
        r.set("ten_che_do", name)
        bank = (eco.get("bankByMode") or {}).get(name)
        if bank is not None:
            C.scalar_or_list(r, "kho_cp", bank, B.BALANCE, ("economy", "bankByMode", name))
        r.set("cp_khoi_dau_nhan_he_so", name in start_modes)
        r.set("ho_so_ai", profiles.get(name, ""))
        r.set("trung_lap", ";".join(neutral_modes.get(name, [])))
        # text.timeLimit is the rules card's text ("10 phút"), not seconds: no unit suffix (spec 9.6)
        r.flatten(rec, B.BALANCE, path, aliases={"text.timeLimit": "text_time_limit"}, units={"text.timeLimit": ""})
    for name, bank in (eco.get("bankByMode") or {}).items():
        if name not in MODE_NAME.values():
            r = cd.row(name.lower(), B.nguon(("economy", "bankByMode", name)), raw=bank)
            r.set("ten_che_do", name)
            C.scalar_or_list(r, "kho_cp", bank, B.BALANCE, ("economy", "bankByMode", name))

    # ------------------------------------------------------------------ Sao_chien_dich
    sc = book.sheet("Sao_chien_dich", "Sao chiến dịch theo mục tiêu",
                    "matchRules.starMastery (sao thứ 2: làm chủ mục tiêu) và starThird (sao thứ 3) theo kiểu mục tiêu; "
                    "starTime / starLosses của từng nhiệm vụ ở 07/Nhiem_vu")
    goals = list(dict.fromkeys(list((rules.get("starMastery") or {})) + list((rules.get("starThird") or {}))))
    for g in goals:
        r = sc.row(g, B.nguon(("matchRules", "starMastery", g)))
        for key, prefix in (("starMastery", "sao2_"), ("starThird", "sao3_")):
            rec = (rules.get(key) or {}).get(g)
            if isinstance(rec, dict):
                r.flatten(rec, B.BALANCE, ("matchRules", key, g), prefix=prefix)

    # ------------------------------------------------------------------ Vo_han (leaderboards)
    vh = book.sheet("Vo_han", "Vô hạn và bảng xếp hạng",
                    "matchRules.leaderboards: thứ tự xếp hạng ('-' giảm dần, '+' tăng dần) của các chế độ vô hạn / tuần; "
                    "hệ số tăng, boss xen kẽ, thưởng: luật chế độ ở Che_do (endless, bossrush) và mã (NEED_CODE_CHECK)")
    vh.col("thu_tu_xep_hang", meaning="khóa xếp hạng theo thứ tự ưu tiên (ngăn ';')")
    vh.col("he_so_tang_thuong", meaning="hệ số tăng, thưởng, trần ngày, huy hiệu (PlayerProfile.Endless.cs)")
    for k, lst in (rules.get("leaderboards") or {}).items():
        r = vh.row(k, B.nguon(("matchRules", "leaderboards", k)), raw=lst)
        C.scalar_or_list(r, "thu_tu_xep_hang", lst, B.BALANCE, ("matchRules", "leaderboards", k))
        r.set("he_so_tang_thuong", NEED_CODE_CHECK)
    extra = {k: v for k, v in rules.items() if k not in ("modes", "starMastery", "starThird", "leaderboards")}
    if extra:
        kv = book.kv_sheet("Luat_tran_khac", "Luật trận: khóa khác", "matchRules: khóa ngoài modes / sao / bảng xếp hạng")
        book.kv_rows(kv, extra, B.BALANCE, ("matchRules",), "matchRules")

    # ------------------------------------------------------------------ Kinh_te
    kt = book.kv_sheet("Kinh_te", "Kinh tế", "balance.json economy (trừ bankByMode: ở Che_do) và campaign.json economy")
    book.kv_rows(kt, {k: v for k, v in eco.items() if k not in ("bankByMode", "enemyScalingQuick")}, B.BALANCE,
                 ("economy",), "economy", prefix=("economy",))
    if "economy" in camp:
        book.kv_rows(kt, camp["economy"], C.CAMPAIGN, ("economy",), "campaign.economy", prefix=("campaign", "economy"))
    for rid, text in (("ma.tiep_te_cong_thuc", "tiếp tế: công thức, ngưỡng, đường phạt, tối đa -75 %"),
                      ("ma.hoan_cp_khi_ha", "hoàn CP khi hạ, bắt kịp, thưởng rút lui, thưởng bộ phận boss, thứ tự áp")):
        r = kt.row(rid, "Assets/MachineBrigade/Scripts/Sim (mã kinh tế)")
        r.values["nhom"] = "ma"
        r.values["khoa"] = text
        r.set("gia_tri_chu", NEED_CODE_CHECK)

    # ------------------------------------------------------------------ Do_kho
    dk = book.sheet("Do_kho", "Độ khó", "Mỗi độ khó một dòng: economy.enemyScalingQuick (hệ số địch trận nhanh) và "
                    "campaign eventLibrary.rules.difficulty (biến cố theo độ khó); tham số AI theo độ khó ở 06/AI_tham_so")
    dk.col("he_so_dich_tran_nhanh", meaning="economy.enemyScalingQuick.<độ khó>")
    quick = eco.get("enemyScalingQuick") or {}
    ev_diff = ((camp.get("eventLibrary") or {}).get("rules") or {}).get("difficulty") or {}
    for i, diff in enumerate(list(dict.fromkeys(DIFFICULTIES + list(quick) + list(ev_diff)))):
        r = dk.row(diff, B.nguon(("economy", "enemyScalingQuick", diff)))
        r.set("thu_tu", i)
        if diff in quick:
            r.set("he_so_dich_tran_nhanh", quick[diff], B.BALANCE, ("economy", "enemyScalingQuick", diff))
        if isinstance(ev_diff.get(diff), dict):
            r.flatten(ev_diff[diff], C.CAMPAIGN, ("eventLibrary", "rules", "difficulty", diff), prefix="bien_co_")

    # ------------------------------------------------------------------ Operations (Diem_tac_chien, bac, mutator)
    ops = ctx.data(OPS) if OPS in ctx.sources else {}
    dt = book.kv_sheet("Diem_tac_chien", "Điểm Tác chiến", "operations.json score (điểm thắng, giờ, máu HQ, tổn thất) và weekly")
    book.kv_rows(dt, {k: v for k, v in ops.items() if k not in ("tiers", "mutators")}, OPS, (), "operations")
    tb = book.sheet("Tac_chien_bac", "Tác chiến: bậc", "operations.json tiers: hệ số địch, thu nhập, điểm, thẻ hỗ trợ")
    C.records(tb, ops.get("tiers"), OPS, ("tiers",))
    mu = book.sheet("Mutator", "Mutator", "operations.json mutators: mỗi mutator một dòng (hệ số, cờ, loại trừ)")
    mu.col("excludes", meaning="mutator không đi cùng (ngăn ';')", fk=["05_che_do_kinh_te/Mutator"])
    C.records(mu, ops.get("mutators"), OPS, ("mutators",))
