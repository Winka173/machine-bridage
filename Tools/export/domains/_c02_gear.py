"""02_phuong_tien, layer C (gear book, 04/10, lane A; owner: "đem ra 1 file riêng, đầy đủ" — gear as one complete,
stand-alone file): sheets built straight from the equipment code (Arsenal.cs, GearCatalog.cs, GearCatalog.Tower.cs,
Gear.Model.cs, Gear.Tower.cs, PlayerProfile.Arsenal.cs) rather than from balance.json (gear carries no balance.json
block at all: every number lives in these C# files), so the gear book (core/pack.py PACK["10_trang_bi"]) shows the
whole system, not only the stat tables d02_phuong_tien.py already reads with cs_table: the coin cost of every level,
the merge rule, what a crate rolls and costs, and an EN/VI name for every catalogue id.

Read only: nothing here changes a game value. A row's `nguon` cites the C# file and line (hand-authored rows; no
NEED_CODE_CHECK marker, same as domains/_c06.py's AI layer C)."""
from __future__ import annotations

from core.model import KHONG_AP_DUNG
from core.units import snake

from . import _balance as B

GEAR = "Assets/MachineBrigade/Scripts/Game/Match/GearCatalog.cs"
GEAR_TOWER = "Assets/MachineBrigade/Scripts/Game/Match/GearCatalog.Tower.cs"
ARSENAL = "Assets/MachineBrigade/Scripts/Game/Match/Arsenal.cs"
PROFILE_ARSENAL = "Assets/MachineBrigade/Scripts/Game/Match/PlayerProfile.Arsenal.cs"

RARITY = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
LEVEL_CAP = [5, 10, 15, 20, 25]  # Arsenal.cs Gear.LevelCap


# ------------------------------------------------------------------------------------------------- Trang_bi_nang_cap
def _level_cost(book):
    s = book.sheet("Trang_bi_nang_cap", "Trang bị: giá nâng cấp theo cấp",
                   "Arsenal.cs Gear.LevelCost / Gear.Spent: xu để lên mỗi cấp (30 x cấp hiện tại, 0 khi đã ở trần của "
                   "độ hiếm) và tổng xu đã tiêu từ cấp 1 tới cấp đó (hoàn lại nếu trang bị bị ghép làm phế liệu, xem "
                   "Trang_bi_ghep). Một dòng một cấp của một độ hiếm (5+10+15+20+25 = 75 dòng)", layer="C")
    s.col("do_hiem", meaning="độ hiếm (Rarity)", enum=RARITY)
    s.col("cap", meaning="cấp (1 = thấp nhất)")
    s.col("cap_tran", meaning="cấp trần của độ hiếm này (Gear.LevelCap)")
    s.col("xu_len_cap_sau", unit="xu", meaning="xu để lên cấp kế tiếp (30 x cấp hiện tại; 0 nếu đã ở cấp trần, "
          "Gear.LevelCost)")
    s.col("xu_da_tieu_toi_day", unit="xu", meaning="tổng xu đã tiêu từ cấp 1 tới cấp này (Gear.Spent)")
    cite = f"{ARSENAL}:180,221,224-229"
    for ri, rarity in enumerate(RARITY):
        cap = LEVEL_CAP[ri]
        spent = 0
        for level in range(1, cap + 1):
            r = s.row(f"{rarity}/{level}", cite)
            r.set("do_hiem", rarity)
            r.set("cap", level)
            r.set("cap_tran", cap)
            r.set("xu_len_cap_sau", 30 * level if level < cap else 0)
            r.set("xu_da_tieu_toi_day", spent)
            spent += 30 * level


# ------------------------------------------------------------------------------------------------------ Trang_bi_ghep
def _merge(book):
    s = book.sheet("Trang_bi_ghep", "Trang bị: luật ghép",
                   "Arsenal.cs Gear.CanMerge / PlayerProfile.Arsenal.cs TryMerge, MergeAll: ghép 3 trang bị cùng ô và "
                   "cùng độ hiếm (dưới Huyền thoại) thành 1 trang bị độ hiếm kế tiếp; cùng luật cho trang bị xe và "
                   "trang bị tháp (ô riêng, không mang bộ). Một dòng một bước, theo đúng thứ tự mã chạy", layer="C")
    s.col("buoc", meaning="tên bước")
    s.col("dieu_kien", meaning="điều kiện")
    s.col("ket_qua", meaning="kết quả")
    s.col("nguon_ma", meaning="file:dòng")
    rows = [
        ("Dieu_kien_ghep", "2 trang bị khác, cùng ô (slot) và cùng độ hiếm với trang bị đang chọn, độ hiếm dưới "
         "Huyền thoại (Legendary)", "Gear.CanMerge(a, b) = true: đủ điều kiện để TryMerge thành công",
         f"{ARSENAL}:232-233"),
        ("Can_du_3", "TryMerge(item): tìm trong cả túi trang bị (PlayerProfile.Arsenal A.gear) những cái CanMerge với "
         "item", "Cần ít nhất 2 cái khác tìm được (same.Count>=2); không đủ thì trả về null (không ghép được)",
         f"{PROFILE_ARSENAL}:695-699"),
        ("Chon_2_doi_tac", "Có nhiều hơn 2 ứng viên cùng ô/độ hiếm", "Sắp theo Worth giảm dần, lấy 2 cái Worth cao "
         "nhất ghép cùng item đang chọn thành bộ ba", f"{PROFILE_ARSENAL}:700-702"),
        ("Cong_thuc_worth", "So 3 mảnh trong bộ ba để chọn mảnh GIỮ lại", "Worth(g) = (đang trang bị ? 1000 : 0) + "
         "cấp hiện tại; Worth cao nhất được giữ, 2 mảnh còn lại thành phế liệu", f"{PROFILE_ARSENAL}:701-705,725"),
        ("Go_phe_lieu", "2 mảnh không được giữ (phế liệu)", "Gỡ khỏi loadout xe (A.loadout) và trang bị tháp đang "
         "mang (A.towerGear), rồi xoá khỏi túi trang bị (A.gear)", f"{PROFILE_ARSENAL}:706-716"),
        ("Hoan_xu", "Mỗi mảnh phế liệu", "Hoàn lại Gear.Spent(mảnh) xu — tổng xu đã tiêu nâng cấp mảnh đó, xem "
         "Trang_bi_nang_cap cột xu_da_tieu_toi_day; mảnh Common cấp 1 (chưa nâng cấp) hoàn 0", f"{ARSENAL}:224-229"),
        ("Len_do_hiem", "Mảnh được giữ", "rarity += 1; cấp hiện tại hạ về Gear.LevelCap[độ hiếm mới] nếu đang cao hơn "
         "trần mới (không mất xu, chỉ hạ số cấp hiển thị)", f"{PROFILE_ARSENAL}:717-718"),
        ("Giu_nguyen", "Mảnh được giữ", "Giữ nguyên loại trang bị gốc (base type), toàn bộ dòng phụ (sub-stat) và "
         "đặc tính (trait) đã có", f"{PROFILE_ARSENAL}:719 (comment); Gear.Model.cs Promote"),
        ("Cuon_them", "Mảnh được giữ, ngay sau khi lên độ hiếm", "Gear.Promote: rải thêm 1 ô dòng phụ nếu độ hiếm mới "
         "cho phép nhiều hơn (SubCount[độ hiếm]); nếu vừa chạm Epic và chưa có đặc tính, rải đặc tính mới (RollTrait)",
         "Assets/MachineBrigade/Scripts/Game/Match/Gear.Model.cs:330-335"),
        ("Ghep_tu_dong", "Người chơi bấm 'ghép tất cả' (MergeAll)", "Lặp tối đa 50 lượt: mỗi lượt tìm trang bị độ "
         "hiếm THẤP NHẤT còn đủ 2 đối tác để ghép và ghép nó trước; dừng khi không còn gì ghép được",
         f"{PROFILE_ARSENAL}:728-743"),
        ("Trang_bi_thap", "Trang bị tháp (ô TowerWeapon / TowerStructure / TowerSystems)", "Dùng đúng luật trên (cùng "
         "CanMerge, TryMerge); trang bị tháp không mang brand nên không có bộ (set) để giữ hay mất khi ghép",
         "Assets/MachineBrigade/Scripts/Game/Match/Gear.Tower.cs:9-14 (comment)"),
    ]
    for buoc, dk, kq, cite in rows:
        r = s.row(buoc, cite)
        r.set("buoc", buoc)
        r.set("dieu_kien", dk)
        r.set("ket_qua", kq)
        r.set("nguon_ma", cite)


# --------------------------------------------------------------------------------------------------- Trang_bi_thung
CRATE_KINDS = ["Battle", "Silver", "Gold", "Legendary"]
CRATE_ODDS = [  # Arsenal.cs Crates.Odds: Common, Uncommon, Rare, Epic, Legendary
    [0.70, 0.25, 0.045, 0.005, 0.0],
    [0.50, 0.35, 0.12, 0.028, 0.002],
    [0.20, 0.42, 0.28, 0.085, 0.015],
    [0.0, 0.25, 0.45, 0.24, 0.06],
]
CRATE_ROLLS = [1, 2, 4, 6]
CRATE_COINS_LOW = [60, 250, 800, 2000]
CRATE_COINS_HIGH = [120, 350, 1000, 2500]
CRATE_PRINT_COUNT = [6, 15, 45, 120]
CRATE_PRINT_CARDS = [1, 2, 3, 4]
CRATE_GOLD_GUARANTEED = [0.0, 0.0, 0.81, 0.16, 0.03]
CRATE_LEGENDARY_GUARANTEED = [0.0, 0.0, 0.0, 0.8, 0.2]
CRATE_EPIC_PITY = [0, 0, 5, 0]
CRATE_LEGENDARY_PITY = [0, 0, 25, 4]
CRATE_COIN_PRICE = [0, 900, 3000, 8000]
CRATE_TOWER_SHARE = [0.2, 0.2, 0.2, 0.2]


def _crates(book):
    s = book.sheet("Trang_bi_thung", "Trang bị: hòm và tỷ lệ rơi",
                   "Arsenal.cs Crates: mỗi lượt quay rơi 1 trong 5 độ hiếm (bảng tỷ lệ riêng theo hòm; hòm Vàng và "
                   "Huyền thoại bảo đảm lượt đầu), rồi 1 trong 2 loại (trang bị xe hay trang bị tháp, theo ty_le_thap); "
                   "có dồn may (pity): chắc rơi Sử thi+ / Huyền thoại trong vòng N hòm. Một dòng một loại hòm (4 dòng)",
                   layer="C")
    s.col("gia_xu", unit="xu", meaning="giá mua bằng xu (0 = không bán; hòm Trận thắng chỉ có khi thắng trận)")
    s.col("so_luot_quay", meaning="số lượt rơi trang bị mỗi hòm (Rolls)")
    s.col("xu_thap", unit="xu", meaning="xu nhận được, đầu dưới của khoảng (CoinsLow)")
    s.col("xu_cao", unit="xu", meaning="xu nhận được, đầu trên của khoảng (CoinsHigh)")
    s.col("so_blueprint", meaning="tổng blueprint chia cho các lá bài đang sở hữu (PrintCount)")
    s.col("so_la_duoc_chia", meaning="số lá bài khác nhau được chia blueprint (PrintCards)")
    s.col("ty_le_thap", unit="%", meaning="phần trăm lượt rơi là trang bị tháp thay vì trang bị xe (TowerShare)")
    s.col("dong_may_su_thi_hom", meaning="chắc rơi Sử thi trở lên trong vòng bấy nhiêu hòm (EpicPity; 0 = không có)")
    s.col("dong_may_huyen_thoai_hom", meaning="chắc rơi Huyền thoại trong vòng bấy nhiêu hòm (LegendaryPity; 0 = "
          "không có)")
    for rarity in RARITY:
        s.col(f"ty_le_{rarity.lower()}", unit="%", meaning=f"tỷ lệ độ hiếm {rarity} ở một lượt rơi thường (Odds)")
    s.col("dam_bao_vong_dau", meaning="độ hiếm thấp nhất bảo đảm ở lượt rơi đầu tiên (KHONG_AP_DUNG: không có bảo "
          "đảm riêng, lượt đầu dùng chung bảng tỷ lệ thường)")
    cite = f"{ARSENAL}:413-444"
    for k, kind in enumerate(CRATE_KINDS):
        r = s.row(kind, cite)
        r.set("gia_xu", CRATE_COIN_PRICE[k])
        r.set("so_luot_quay", CRATE_ROLLS[k])
        r.set("xu_thap", CRATE_COINS_LOW[k])
        r.set("xu_cao", CRATE_COINS_HIGH[k])
        r.set("so_blueprint", CRATE_PRINT_COUNT[k])
        r.set("so_la_duoc_chia", CRATE_PRINT_CARDS[k])
        r.set("ty_le_thap", round(CRATE_TOWER_SHARE[k] * 100, 1))
        r.set("dong_may_su_thi_hom", CRATE_EPIC_PITY[k])
        r.set("dong_may_huyen_thoai_hom", CRATE_LEGENDARY_PITY[k])
        for ri, rarity in enumerate(RARITY):
            r.set(f"ty_le_{rarity.lower()}", round(CRATE_ODDS[k][ri] * 100, 2))
        if kind == "Gold":
            r.set("dam_bao_vong_dau", "Rare+ (GoldGuaranteed: " + ";".join(str(x) for x in CRATE_GOLD_GUARANTEED) + ")")
        elif kind == "Legendary":
            r.set("dam_bao_vong_dau",
                  "Epic+ (LegendaryGuaranteed: " + ";".join(str(x) for x in CRATE_LEGENDARY_GUARANTEED) + ")")
        else:
            r.set("dam_bao_vong_dau", KHONG_AP_DUNG)


def _crates_extra(book):
    kv = book.kv_sheet("Trang_bi_thung_nguon", "Trang bị: blueprint vạn năng và nguồn hòm hàng ngày",
                        "Arsenal.cs Crates.Open (blueprint vạn năng kèm hòm Vàng/Huyền thoại) và DailyCrates (hòm "
                        "miễn phí mỗi ngày: thắng trận, xem quảng cáo)")
    cite1 = f"{ARSENAL}:473-474"
    for nhom, khoa, so, chu, don_vi in [
        ("hom_vang", "ty_le_blueprint_van_nang", 0.1, "", "phần (0.1 = 10%)"),
        ("hom_vang", "so_blueprint_van_nang_khi_trung", 5, "", ""),
        ("hom_huyen_thoai", "so_blueprint_van_nang_luon_co", 10, "", ""),
    ]:
        r = kv.row(f"{nhom}/{khoa}", cite1)
        r.set("nhom", nhom)
        r.set("khoa", khoa)
        r.set("gia_tri_so", so)
        r.set("gia_tri_chu", chu)
        r.set("don_vi", don_vi)
    cite2 = f"{ARSENAL}:561-568"
    for nhom, khoa, so, chu, don_vi in [
        ("hang_ngay", "so_hom_thang_tran_toi_da_ngay", 5, "", "hòm/ngày"),
        ("hang_ngay", "so_hom_quang_cao_toi_da_ngay", 3, "", "hòm/ngày"),
        ("hang_ngay", "khoang_cach_hom_quang_cao", 10, "", "phút"),
        ("hang_ngay", "hom_quang_cao_dau_tien", "", "Silver", ""),
        ("hang_ngay", "hom_quang_cao_tiep_theo", "", "Battle", ""),
    ]:
        r = kv.row(f"{nhom}/{khoa}", cite2)
        r.set("nhom", nhom)
        r.set("khoa", khoa)
        r.set("gia_tri_so", so)
        r.set("gia_tri_chu", chu)
        r.set("don_vi", don_vi)


# ----------------------------------------------------------------------------------------------------- Trang_bi_ten
def _names(ctx, book):
    s = book.sheet("Trang_bi_ten", "Trang bị: tên Anh/Việt theo id",
                   "Tên hiển thị (chuỗi HUD) của mọi id trang bị: loại cơ bản xe, mô-đun, đặc tính, dòng phụ, bộ, "
                   "loại cơ bản tháp, đặc tính tháp. Một dòng một id, tra chuỗi theo đúng thứ tự khoá mà "
                   "domains/d02_phuong_tien.py dùng cho cột ten_vi của từng sheet gốc (khoá đầu tiên có chuỗi thắng)",
                   layer="C")
    s.col("loai", meaning="loại mục", enum=["co_ban", "mo_dun", "dac_tinh", "dong_phu", "bo", "co_ban_thap",
                                             "dac_tinh_thap"])
    s.col("khoa_chuoi_uu_tien", meaning="khoá chuỗi thử trước nhất (không hẳn là khoá thật sự khớp: xem "
          "domains/d02_phuong_tien.py cho các khoá dự phòng)")
    s.col("ten_en", meaning="tên tiếng Anh")
    s.col("ten_vi", meaning="tên tiếng Việt")

    def add(loai, path, array, key, name_prefix, id_suffix="", extra=None):
        sid, rows, lines = ctx.cs_table(path, array, extra=extra)
        for i, rowd in enumerate(rows):
            rid = str(rowd.get(key, i))
            sn = snake(rid)
            en, vi = B.name_of(ctx, name_prefix + rid, name_prefix + sn, f"trait.{sn}", f"stat.line.{sn}", f"special.{sn}")
            cite = f"{path}:{lines[i] if i < len(lines) else ''} ({array}[{i}])"
            r = s.row(f"{loai}/{rid}{id_suffix}", cite)
            r.set("loai", loai)
            r.set("khoa_chuoi_uu_tien", name_prefix + rid)
            r.set("ten_en", en)
            r.set("ten_vi", vi)

    add("co_ban", GEAR, "Bases", "id", "gear.base.")
    add("mo_dun", GEAR, "Modules", "module", "special.")
    add("dac_tinh", GEAR, "Traits", "id", "trait.")
    add("dong_phu", GEAR, "Subs", "stat", "stat.line.")
    add("bo", GEAR, "Brands", "id", "set.")
    add("co_ban_thap", GEAR_TOWER, "TowerBases", "id", "gear.base.", extra=[GEAR])
    add("dac_tinh_thap", GEAR_TOWER, "TowerTraits", "id", "trait.", id_suffix="@thap", extra=[GEAR])


def build(ctx, book):
    _level_cost(book)
    _merge(book)
    _crates(book)
    _crates_extra(book)
    _names(ctx, book)
