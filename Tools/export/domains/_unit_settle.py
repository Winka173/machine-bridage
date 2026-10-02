"""Units of columns of files 01-04 that 00/Don_vi_chua_ro listed and the C# settles (pass 5, read only).

Each entry: the unit ('' = none: a multiplier, share, count, index or level) and where the code says so. The column keeps
its name (spec 2.1 puts the unit in the name; renaming source-key columns would break their coverage marks): Schema's
don_vi carries the unit and y_nghia the citation. Columns the code does not settle stay in Don_vi_chua_ro for the owner."""
from __future__ import annotations

C = "Sim/Content/"
NONE = ""
_SHARED = {  # vehicles[] fields shared by Xe, Boss, Thap, Mo_dun_tien_ich
    "marked_spread": (NONE, C + "VehicleDef.Extra.cs MarkedSpread (hệ số độ tản)"),
    "jammer": ("m", C + "Definitions.cs Jammer (bán kính)"),
    "drone_armor": (NONE, C + "Definitions.cs DroneArmor (tỷ lệ sát thương drone lọt qua)"),
    "mine_armor": (NONE, C + "VehicleDef.Extra.cs MineArmor (tỷ lệ sát thương mìn lọt qua)"),
    "forward_drop": ("s", C + "Definitions.cs ForwardDrop (giây đứng yên)"),
    "paradrop_base_keep_out": ("m", C + "Catalog.P25A.cs BaseKeepOut (khoảng cách tới HQ địch)"),
    "deploy_tank_mount": (NONE, C + "VehicleDef.P17.cs TankMount (chỉ số bệ)"),
    "mines_interval": ("s", C + "SkillDef.cs MineLayerDef Interval (một mìn mỗi khoảng)"),
    "mines_max": (NONE, C + "SkillDef.cs MineLayerDef Max (số mìn)"),
    "mines_trigger": ("m", C + "SkillDef.cs MineLayerDef Trigger (khoảng cách kích nổ)"),
    "mines_spread": ("m", C + "SkillDef.cs MineLayerDef Spread (mét quanh bãi mìn)"),
    "mines_life": ("s", C + "SkillDef.cs MineLayerDef Life (giây)"),
    "counter_battery_bonus": (NONE, C + "Definitions.cs CounterBattery bonus (tỷ lệ sát thương thêm)"),
    "reveal_air": ("m", C + "TowerBranchDefs.cs RevealAir (mét)"),
    "naval_dash_every": ("s", C + "Catalog.Naval.cs DashEvery"),
    "naval_dash_hold": ("s", C + "Catalog.Naval.cs DashHold"),
}
_PHASE = (NONE, "chỉ số pha (0 = pha đầu, -1 = không bao giờ): " + C + "BigAttackDefs.cs LatePhase / TierDefs.cs HaltPhase / NavalDefs.cs EscapePhase")
_FIRST = ("s", "giây sau khi boss xuất hiện tới lần đầu (đi cặp với every): " + C + "BigAttackDefs.cs First, Catalog.Extra.cs / Catalog.P19.cs / Catalog.Naval.cs First")
_BOSS = {
    **{c: _PHASE for c in ("wake_phase", "cruise_phase", "craft_phase", "naval_escape_phase", "tiers_halt_phase",
                           "crush_debris_phase", "burrow_stop_phase")},
    **{c: _FIRST for c in ("tiers_hijack_first", "pods_first", "bombard_first", "burrow_first", "landing_first",
                           "salvo_first", "cruise_first", "craft_first", "factory_first")},
    "duel_vanish_every": ("s", C + "Catalog.P22.cs VanishEvery"), "duel_vanish_seconds": ("s", C + "Catalog.P22.cs VanishSeconds"),
    "naval_pass_in": ("s", C + "NavalDefs.cs PassIn"), "naval_pass_out": ("s", C + "NavalDefs.cs PassOut"),
    "spot_aura": (NONE, C + "Catalog.P20.cs SpotAura (tỷ lệ tản)"),
    "crush_structure": (NONE, C + "BigAttackDefs.cs Structure (hệ số lên công trình)"),
    "crush_debris_every": ("s", C + "Catalog.P20.cs DebrisEvery"), "crush_debris_radius": ("m", C + "Catalog.P20.cs DebrisRadius"),
    "crush_debris_damage": ("hp", C + "Catalog.P20.cs DebrisDamage"),
    "tiers_armour_hull": (NONE, C + "TierDefs.cs Hull (mức giáp)"), "tiers_armour_belly": (NONE, C + "TierDefs.cs Belly (mức giáp)"),
    "tiers_armour_grounded": (NONE, C + "TierDefs.cs Grounded (mức giáp)"),
    "size": (NONE, C + "BossTemplates.cs Resize (hệ số cỡ)"), "variant_size": (NONE, C + "BossTemplates.cs Variant size (hệ số cỡ)"),
    "variant_tint_r": (NONE, "màu 0-1"), "variant_tint_g": (NONE, "màu 0-1"), "variant_tint_b": (NONE, "màu 0-1"),
}
_PART = {"turn": (NONE, C + "BossDefs.cs Turn (hệ số)"), "cadence": (NONE, C + "BossDefs.cs Cadence (hệ số)"),
         "break_damage": (NONE, C + "BossDefs.cs BreakDamage (tỷ lệ máu)"), "fail": (NONE, C + "BossDefs.cs Fail (tỷ lệ)"),
         "attach": (NONE, C + "BossDefs.cs Attachment (chỉ số)")}
_CMD = {c: (NONE, C + "CommanderDefs.cs (hệ số / tỷ lệ)") for c in (
    "repair", "air_rearm", "strike_cooldown", "stealth_sight", "exposed_taken", "jam_resist", "delivery", "income", "supply",
    "point_income", "no_points_income", "kill_refund", "rich_income", "early_income", "low_hp_damage")}
_CMD.update({"rich_at": ("CP", C + "CommanderDefs.cs RichAt"), "bank_bonus": ("CP", C + "CommanderDefs.cs BankBonus"),
             "early_seconds": ("s", C + "CommanderDefs.cs EarlySeconds")})

SETTLED = {
    ("01_vu_khi_dan", "Vu_khi"): {
        "charge": ("s", C + "Definitions.cs Charge (giây nạp trước mỗi phát)"),
        "swarm": ("m", C + "WeaponDef.P17.cs SwarmReach (mét quanh điểm nhắm)"),
        "pierce_max": (NONE, C + "BossDefs.cs PierceMax (số xe)"),
        "round_length": ("m", C + "Definitions.cs RoundLength (mét)"),
        "round_weight": ("hp", C + "Definitions.cs RoundWeight (nặng như sát thương này)"),
    },
    ("01_vu_khi_dan", "Dong_vu_khi"): {
        "round_length": ("m", C + "Definitions.cs RoundLength (mét)"),
        "round_weight": ("hp", C + "Definitions.cs RoundWeight (nặng như sát thương này)"),
    },
    ("01_vu_khi_dan", "Vu_khi_he_so_thuong"): {"still": ("s", C + "SkillDef.cs StillFor (giây đứng yên)")},
    ("02_phuong_tien", "Xe"): _SHARED,
    ("02_phuong_tien", "The_ho_tro"): {"unit_rank": (NONE, C + "SupportDef.cs UnitRank (hạng thẻ)")},
    ("02_phuong_tien", "Commander"): _CMD,
    ("03_boss", "Boss"): {**_SHARED, **_BOSS},
    ("03_boss", "Boss_air"): {"phase": _PHASE},
    ("03_boss", "Boss_bo_phan"): _PART,
    ("03_boss", "Boss_bien_the_chinh"): {"break_damage": _PART["break_damage"]},
    ("03_boss", "Boss_ham_doi"): {"abeam": ("m", C + "NavalDefs.cs Abeam (mét)")},
    ("03_boss", "Boss_sieu_vu_khi"): {"first": _FIRST, "late_phase": _PHASE},
    ("03_boss", "Boss_sieu_vu_khi_don"): {
        "falloff": (NONE, C + "BigAttackDefs.cs Falloff (tỷ lệ ở rìa)"), "per_part": (NONE, C + "BigAttackDefs.cs PerPart (số viên)"),
        "cut": (NONE, C + "BigAttackDefs.cs Cut (tỷ lệ còn lại)"), "structure": (NONE, C + "BigAttackDefs.cs Structure (hệ số)"),
        "seats": (NONE, C + "BigAttackDefs.cs Seats (số xe)")},
    ("04_can_cu_thap", "Thap"): _SHARED,
    ("04_can_cu_thap", "Mo_dun_tien_ich"): _SHARED,
    ("04_can_cu_thap", "Nha_chinh_kieu"): {"clear": ("s", C + "HqTypeRules.cs GarrisonClear (giây)")},
    ("04_can_cu_thap", "Xay_lai"): {"drop": ("s", C + "BaseRules.cs rebuild drop (giây thả)")},
}


def apply(book) -> int:
    """Settles the columns of this book listed above; returns how many."""
    n = 0
    for (fid, sheet), cols in SETTLED.items():
        if fid != book.file_id or sheet not in book.sheets:
            continue
        s = book.sheets[sheet]
        for col, (unit, cite) in cols.items():
            c = s.cols.get(col)
            if c is None or not c.unit_unknown:
                continue
            c.unit = unit
            c.unit_unknown = False
            c.meaning = (c.meaning + " " if c.meaning else "") + f"[đơn vị: {unit or 'không (hệ số / tỷ lệ / số đếm)'}; đọc mã {cite}]"
            n += 1
    return n
