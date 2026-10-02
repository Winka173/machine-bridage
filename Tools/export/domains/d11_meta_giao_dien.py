"""11_meta_giao_dien, layer A: data outside the battle: rank-up prices, crates and drop odds, shop packs, daily missions,
skins, unlocks, starter cards, the menu's map list, base-map pictures, the ammunition handbook examples, and every other
literal table of the meta C# files (auto-found); absent features (achievements, telemetry, tutorial) said so."""
from __future__ import annotations

from core.model import NEED_CODE_CHECK, chua_ap

from . import _balance as B
from . import _lane_c as C

FILE_ID = "11_meta_giao_dien"
TITLE = "Meta và giao diện"
DESC = "Nâng hạng, hòm đồ và tỷ lệ rơi, cửa hàng, nhiệm vụ ngày, skin, mở khóa, thẻ khởi đầu, danh sách bản đồ menu, " \
       "ảnh bản đồ căn cứ, sổ tay đạn, mọi bảng hằng C# của meta; thành tựu / telemetry / hướng dẫn (không có hoặc chờ)"

MATCH = "Assets/MachineBrigade/Scripts/Game/Match/"
ARSENAL = MATCH + "Arsenal.cs"
DAILY = MATCH + "DailyMissions.cs"
SKINS = MATCH + "Skins.cs"
SETTINGS = MATCH + "MatchSettings.cs"
UNLOCKS = "Tools/campaign/unlocks_sheet.json"
BASES_UI = "Assets/MachineBrigade/Resources/UI/Bases/"
# the meta files whose literal tables are exported (every static readonly literal array, found by C.cs_arrays)
META_FILES = ["Arsenal.cs", "DailyMissions.cs", "Rewards.cs", "Progression.cs", "Skins.cs", "WeeklyFortress.cs",
              "Operations.cs", "Ads.cs", "GraphicsOptions.cs", "MatchSettings.cs", "Haptics.cs", "PlayerProfile.cs",
              "PlayerProfile.Arsenal.cs", "PlayerProfile.BasePlans.cs", "PlayerProfile.Endless.cs", "PlayerProfile.HqType.cs",
              "PlayerProfile.Hunt.cs", "PlayerProfile.Operations.cs", "PlayerProfile.Story.cs", "PlayerProfile.Tactics.cs",
              "PlayerProfile.TowerGear.cs", "PlayerProfile.Walls.cs"]


def _line(lines, i):
    return lines[i] if i < len(lines) else ""


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    done: set[tuple[str, str]] = set()

    def table(path, array):
        done.add((path, array))
        return ctx.cs_table(path, array)

    # ------------------------------------------------------------------ Nang_hang (Arsenal.Coins / Prints)
    nh = book.sheet("Nang_hang", "Giá nâng hạng", "Arsenal.cs Coins / Prints: xu và bản thiết kế cho mỗi lần lên hạng (hạng 1-10)")
    nh.col("hang", meaning="hạng sau khi nâng (chỉ số + 1)")
    nh.col("xu", meaning="xu (Arsenal.Coins[i])")
    nh.col("ban_thiet_ke", meaning="bản thiết kế (Arsenal.Prints[i])")
    for array, col in (("Coins", "xu"), ("Prints", "ban_thiet_ke")):
        sid, rows, lines = table(ARSENAL, array)
        for i, v in enumerate(rows):
            r = nh.rows.get(i + 1) or nh.row(i + 1, f"{ARSENAL}:{_line(lines, i)} ({array})")
            r.set("hang", i + 1)
            r.set(col, v, sid, (i,))

    # ------------------------------------------------------------------ Hom_do (crates)
    hd = book.sheet("Hom_do", "Hòm đồ và tỷ lệ rơi", "Arsenal.cs: mỗi bậc hòm một dòng (số lượt, xu thấp / cao, số bản thiết kế, "
                    "số thẻ, giá xu, bảo hiểm Sử thi / Huyền thoại, phần tháp, tỷ lệ theo độ hiếm)")
    hd.col("bac_hom", meaning="bậc hòm (chỉ số)")
    for j in range(5):
        hd.col(f"ty_le_{j}", meaning=f"Arsenal.Odds[bậc][{j}]: tỷ lệ rơi của độ hiếm thứ {j} (thứ tự độ hiếm trong Arsenal.cs)")
    for array in ("Rolls", "CoinsLow", "CoinsHigh", "PrintCount", "PrintCards", "CoinPrice", "EpicPity", "LegendaryPity",
                  "TowerShare", "Odds"):
        sid, rows, lines = table(ARSENAL, array)
        col = B_snake(array)
        for i, v in enumerate(rows):
            r = hd.rows.get(i) or hd.row(i, f"{ARSENAL}:{_line(lines, i)} ({array})")
            r.set("bac_hom", i)
            if isinstance(v, list):
                for j, x in enumerate(v):
                    r.set(f"ty_le_{j}", x, sid, (i, j))
            else:
                r.set(col, v, sid, (i,))

    # ------------------------------------------------------------------ Trang_bi_hang (rarity tables)
    th = book.sheet("Trang_bi_hang", "Trang bị theo độ hiếm", "Arsenal.cs LevelCap / Top / Cap / GoldGuaranteed / LegendaryGuaranteed: "
                    "mỗi chỉ số một dòng theo bảng nguồn (bang / chi_so)")
    th.col("bang", meaning="bảng C#")
    th.col("chi_so", meaning="chỉ số trong bảng")
    for array in ("LevelCap", "Top", "Cap", "GoldGuaranteed", "LegendaryGuaranteed"):
        sid, rows, lines = table(ARSENAL, array)
        for i, v in enumerate(rows):
            r = th.row(f"{array}/{i}", f"{ARSENAL}:{_line(lines, i)} ({array}[{i}])", raw=v)
            r.set("bang", array)
            r.set("chi_so", i)
            C.cs_element_row(r, v, sid, (i,))

    # ------------------------------------------------------------------ Cua_hang (Packs)
    ch = book.sheet("Cua_hang", "Cửa hàng", "Arsenal.cs Packs: gói xu (id, số xu, giá hiển thị)")
    sid, rows, lines = table(ARSENAL, "Packs")
    for i, v in enumerate(rows):
        r = ch.row(v[0] if isinstance(v, list) and v else i, f"{ARSENAL}:{_line(lines, i)} (Packs[{i}])", raw=v)
        for j, name in enumerate(("id_goi", "xu", "gia_hien_thi")):
            if isinstance(v, list) and j < len(v):
                r.set(name, v[j], sid, (i, j))

    # ------------------------------------------------------------------ Nhiem_vu_ngay (DailyMissions.Pool)
    nn = book.sheet("Nhiem_vu_ngay", "Nhiệm vụ ngày", "DailyMissions.cs Pool: loại, mục tiêu theo bậc (ngăn ';'), thưởng xu")
    sid, rows, lines = table(DAILY, "Pool")
    for i, v in enumerate(rows):
        r = nn.row(v[0] if isinstance(v, list) and v else i, f"{DAILY}:{_line(lines, i)} (Pool[{i}])", raw=v)
        for j, name in enumerate(("loai", "muc_tieu", "thuong_xu")):
            if isinstance(v, list) and j < len(v):
                C.scalar_or_list(r, name, v[j], sid, (i, j))

    # ------------------------------------------------------------------ Skin, Ban_do_menu (dict tables)
    sk = book.sheet("Skin", "Skin", "Skins.cs All: id, giá, màu")
    sid, rows, lines = table(SKINS, "All")
    for i, v in enumerate(rows):
        r = sk.row(v.get("id", i) if isinstance(v, dict) else i, f"{SKINS}:{_line(lines, i)} (All[{i}])", raw=v)
        C.cs_element_row(r, v, sid, (i,))
    bm = book.sheet("Ban_do_menu", "Bản đồ trên menu", "MatchSettings.cs AllMaps: id, chủ đề, biểu tượng, thời tiết có thể")
    bm.col("id", fk=["08_ban_do/Ban_do_goc"])
    sid, rows, lines = table(SETTINGS, "AllMaps")
    for i, v in enumerate(rows):
        r = bm.row(v.get("id", i) if isinstance(v, dict) else i, f"{SETTINGS}:{_line(lines, i)} (AllMaps[{i}])", raw=v)
        C.cs_element_row(r, v, sid, (i,))

    # ------------------------------------------------------------------ Meta_bang_hang (every other meta table)
    mb = book.sheet("Meta_bang_hang", "Bảng hằng meta (C#)", "Mọi bảng static readonly còn lại của các file meta (tự tìm): "
                    "mỗi phần tử một dòng (bang = <file>#<mảng>)")
    mb.col("bang", meaning="<file>#<mảng>")
    mb.col("chi_so", meaning="chỉ số phần tử")
    for f in META_FILES:
        path = MATCH + f
        if not (ctx_root_exists(path)):
            continue
        for array in C.cs_arrays(path):
            if (path, array) in done:
                continue
            sid, rows, lines = table(path, array)
            for i, v in enumerate(rows):
                r = mb.row(f"{f[:-3]}#{array}/{i}", f"{path}:{_line(lines, i)} ({array}[{i}])", raw=v)
                r.set("bang", f"{f[:-3]}#{array}")
                r.set("chi_so", i)
                C.cs_element_row(r, v, sid, (i,))

    # ------------------------------------------------------------------ Mo_khoa (unlocks_sheet.json)
    if UNLOCKS in ctx.sources:
        u = ctx.data(UNLOCKS)
        mk = book.sheet("Mo_khoa", "Mở khóa", "Tools/campaign/unlocks_sheet.json: thẻ -> chương mở khóa; thẻ mở khi thắng nhiệm vụ: "
                        "07/Nhiem_vu.unlocks")
        mk.col("the", meaning="thẻ", fk=C.UNIT_FK)
        mk.col("chuong", meaning="chương mở khóa", fk=["07_chien_dich_cot_truyen/Chuong"])
        for key, block in u.items():
            if not isinstance(block, dict):
                continue
            for card, v in block.items():
                r = mk.row(f"{key}.{card}", C.nguon(UNLOCKS, (key, card)), raw=v)
                r.set("the", card)
                r.set("chuong" if key == "chapters" else key, v, UNLOCKS, (key, card))
        rest = {k: v for k, v in u.items() if not isinstance(v, dict)}
        if rest:
            kv = book.kv_sheet("Mo_khoa_chung", "Mở khóa: ghi chú", "unlocks_sheet.json: khóa ngoài bảng")
            book.kv_rows(kv, rest, UNLOCKS, (), "unlocks_sheet")

    # ------------------------------------------------------------------ Anh_can_cu (UI/Bases/*.json)
    ac = book.sheet("Anh_can_cu", "Ảnh bản đồ căn cứ", "Resources/UI/Bases/*.json: ảnh nhìn từ trên của căn cứ trên màn Căn cứ "
                    "(bản đồ, tâm, hướng, bãi thả, HQ, mét mỗi ảnh, viền, mũi tên)")
    ac.col("map", fk=["08_ban_do/Ban_do_goc"])
    ao = book.sheet("Anh_can_cu_vien", "Ảnh căn cứ: viền", "outline[]: điểm viền căn cứ trên ảnh", parent=ac)
    aa = book.sheet("Anh_can_cu_mui_ten", "Ảnh căn cứ: mũi tên", "arrows[]: mũi tên hướng tấn công trên ảnh", parent=ac)
    for sid in sorted(s for s in ctx.sources if s.startswith(BASES_UI) and s.endswith(".json")):
        rec = ctx.data(sid)
        r = ac.row(sid.rsplit("/", 1)[-1][:-5], sid, raw=rec)
        r.flatten(rec, sid, (), children={"outline": C.child(ao), "arrows": C.child(aa)})

    # ------------------------------------------------------------------ So_tay_dan (balance handbook)
    st = book.kv_sheet("So_tay_dan", "Sổ tay đạn", "balance.json handbook: xe mẫu bắn và xe mẫu bị bắn của sổ tay đạn trên giao diện")
    book.kv_rows(st, d.get("handbook") or {}, B.BALANCE, ("handbook",), "handbook")

    # ------------------------------------------------------------------ absent / later
    absent = "Không có trong mã và dữ liệu (tìm 03/10: 0 file C# nhắc tới)"
    C.marker_sheet(book, "Thanh_tuu", "Thành tựu", "Thành tựu", "KHONG_CO", absent + " 'Achievement'", "Assets/MachineBrigade/Scripts")
    C.marker_sheet(book, "Telemetry", "Telemetry", "Sự kiện và tham số telemetry", "KHONG_CO",
                   "Không có hệ telemetry (chỉ SandboxSession.cs nhắc chữ 'Telemetry')", "Assets/MachineBrigade/Scripts/Game/Match/SandboxSession.cs")
    C.marker_sheet(book, "Huong_dan", "Hướng dẫn người chơi", "Trải nghiệm người chơi mới", chua_ap(24),
                   "prompt 24 (trải nghiệm người chơi mới) đang hoãn; gợi ý trong trận: 07/Nhiem_vu_goi_y, chữ: 10/Dia_phuong_hoa (tip.*, guide.*)",
                   "Docs/prompts/prompt24_vi.txt")
    C.marker_sheet(book, "Cai_dat_mac_dinh", "Cài đặt mặc định", "Vòng cảnh báo, thoại, rung camera, cỡ chữ, đồ họa...",
                   chua_ap("xuat_luot5"), "hằng mặc định trong GraphicsOptions.cs, Haptics.cs, PlayerProfile.cs (lượt 5: Hang_so_trong_ma); "
                   "các mảng lựa chọn đồ họa ở Meta_bang_hang (GraphicsOptions#...)", MATCH + "GraphicsOptions.cs")
    C.marker_sheet(book, "Mutator_tuan", "Mutator tuần", "Mutator tuần của Tác chiến", "XEM_05",
                   "dữ liệu ở 05_che_do_kinh_te/Mutator (operations.json); chọn theo tuần: Operations.cs (NEED_CODE_CHECK)",
                   C.DATA + "operations.json")
    C.marker_sheet(book, "Thu_hang", "Thứ hạng", "Bảng xếp hạng", "XEM_05", "thứ tự xếp hạng ở 05_che_do_kinh_te/Vo_han "
                   "(matchRules.leaderboards); không có bảng xếp hạng trực tuyến", B.BALANCE + ": matchRules.leaderboards")
    C.marker_sheet(book, "Thuong", "Thưởng", "Thưởng trận / chiến dịch", NEED_CODE_CHECK,
                   "xu / XP / bản thiết kế mỗi nhiệm vụ: 07/Nhiem_vu (coins, xp, prints, rarePrints); thưởng trận nhanh: Rewards.cs",
                   MATCH + "Rewards.cs")


def B_snake(name: str) -> str:
    from core.units import snake
    return snake(name)


def ctx_root_exists(path: str) -> bool:
    from core.repo import ROOT
    return (ROOT / path).exists()
