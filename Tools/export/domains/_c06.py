"""06_ai, layer C (AI book, 04/10): sheets built straight from the AI code and design comments rather than from
balance.json, so the pack shows the whole AI, not only its data: the decision flow of the three layers (general / squad /
unit), target priority (tower modes, boss behaviour weights), the difficulty's AiSkill, the anti-stuck / anti-idle rules,
the aircraft rearm / attack-pass cycle, and every named AI constant still inline in C# (not yet in tunables.json).

Read only: nothing here changes a game value. A row's `nguon` cites the C# file and line (core/packcheck's NEED_CODE_CHECK
machinery does not apply: these are prose + code citations, not balance.json leaves)."""
from __future__ import annotations

import re

from core.repo import ROOT

from . import _layer_b as LB

AI_DIR = "Assets/MachineBrigade/Scripts/Sim/AI/"
AI_FILES = ["Commander.cs", "Commander.Units.cs", "ConquestAi.cs", "ConquestAi.P17.cs", "ConquestAi.P25A.cs",
            "ConquestAi.P28.cs", "ConquestAi.Sandbox.cs", "DecisionLog.cs", "SquadLayer.Units.cs", "SquadLayer.Walls.cs",
            "Squads.cs", "TacticalAi.cs", "TowerModes.cs", "WorldModel.cs"]


# ------------------------------------------------------------------------------------------------- AI_luong_quyet_dinh
def _flow(book):
    s = book.sheet("AI_luong_quyet_dinh", "Luồng quyết định theo lớp",
                   "Prompt 28: AI 3 lớp (tướng AiCommander -> đội SquadLayer -> đơn vị TacticalAi) cộng mô hình thế giới "
                   "WorldModel và nhật ký quyết định DecisionLog. Một dòng một bước: điều kiện kích hoạt và kết quả, "
                   "theo đúng thứ tự mã chạy (TickLayered)", layer="C")
    s.col("lop", meaning="lớp AI", enum=["TheGioi", "Tuong", "Doi", "DonVi", "NhatKy"])
    s.col("buoc", meaning="tên bước / quyết định")
    s.col("dieu_kien", meaning="điều kiện kích hoạt (ngưỡng, sự kiện)")
    s.col("ket_qua", meaning="kết quả / hành động")
    s.col("nguon_ma", meaning="file:dòng trong Sim/AI (hoặc file khác)")
    rows = [
        ("TheGioi", "Luoi_moi_de_doa", "Mỗi tick, cập nhật lưới mờ (blur) 8 nhóm lực (ForceGroup) x 4 kiểu đe dọa "
         "(ThreatKind: AntiAir, AntiTank, Artillery, Splash), 8x8 ô", "Knowledge Unknown / Present / ConfirmedAbsent "
         "mỗi ô: 'chưa thấy' khác 'chắc chắn không có'", "WorldModel.cs:13-50,195-211"),
        ("TheGioi", "Su_kien_tinh_bao", "Trinh sát phát hiện biến động", "Ghi IntelEventKind: Threat / Opportunity / "
         "Window / Mismatch / ObjectivePressure, nuôi StrategicIntent của tướng", "WorldModel.cs:35-42"),
        ("Tuong", "Khoi_tao", "Chưa có AiCommander (đầu trận)", "Tạo AiCommander: chiến thuật = hồ sơ chế độ có "
         "generalTactic (hoặc chế độ Weekly/Operation) -> ưa thích của tướng (aiBehaviour.generals); khác -> balanced; "
         "rồi lọc qua AllowedTactic (hồ sơ cho phép gì)", "ConquestAi.P28.cs:33-45"),
        ("Tuong", "The_phong_thu", "Stance == Defend, hoặc hồ sơ Engagement = AvoidUnlessBlocking và chưa có báo động "
         "(!Alarm)", "Commander.Defending = true: mọi đội giữ, không đuổi địch", "ConquestAi.P28.cs:48-49"),
        ("Tuong", "Lap_y_dinh", "Mỗi lần Tick (~1 s)", "StrategicIntent: mục tiêu chính/phụ, kiểu (attack/hold/flank/"
         "breakthrough/pincer/wait), có mở cửa sổ tấn công (AttackWindow) hay không và vì sao (WindowReason)",
         "Commander.cs:56-66"),
        ("Tuong", "Doi_chien_thuat", "AiSkill.Switching (Never / WhenLosing / Counter) cho phép, còn cooldown hay "
         "FreeSwitch (giữa 2 boss của Boss Rush)", "RequestTactic -> AllowedTactic lọc theo tactics/flags của hồ sơ chế "
         "độ (AI_ho_so_che_do); TacticSwitchResult: Done/Same/Cooldown/Unknown/NotAllowed", "Commander.cs:71-80"),
        ("Tuong", "Xin_ho_tro", "Commander.SupportWanted(world) trả về nhu cầu (khói trên đội bị pháo, SEAD trước cửa "
         "sổ không quân...)", "Mua/kích thẻ hỗ trợ cùng loại nếu sẵn sàng (Ready)", "ConquestAi.P28.cs:54-68"),
        ("Tuong", "Mua_quan", "Mỗi lá được NewCardScore (P17 C) và P25CardScore (P25 F2-A) chấm điểm theo tình huống "
         "(wingman cần máy bay, dome cần quân đông, SEAD cần phòng không địch mạnh, drone-killer cần có drone...)",
         "Chọn lá điểm cao nhất trong CP còn lại của tactic; thả dù rơi gần điểm chưa chiếm nếu đơn vị có Paradrop",
         "ConquestAi.P17.cs; ConquestAi.P25A.cs"),
        ("Tuong", "Giao_viec_doi", "Tướng chia quân theo SquadTask (TaskKind Primary/Secondary/Reserve; Objective; "
         "Hold; Window; FlankSide)", "Mỗi đội (Squad) tự chọn CÁCH làm (SquadLayer), tướng chỉ chọn CÁI GÌ/Ở ĐÂU",
         "Squads.cs:49-70"),
        ("Doi", "Trang_thai_doi", "Hết thời gian cam kết (aiBehaviour.states.<state>.commit, sheet AI_trang_thai) hoặc "
         "có sự kiện khẩn (mất mục tiêu chính, đòn lớn của địch, đổi pha boss)", "Chuyển 1 trong 7 trạng thái: Travel, "
         "Approach, Combat, Overwatch, Flank, Hold, Regroup (không có Retreat riêng)", "Squads.cs:13-20"),
        ("Doi", "Hanh_dong_doi", "Theo trạng thái + StrategicIntent + AttackThreshold (tỷ lệ quân nhà/địch cần để đánh, "
         "giảm bởi 'dùng hoặc mất' khi hồ sơ có advancePressure)", "1 trong 9 hành động: Attack, Hold, FlankLeft, "
         "FlankRight, Overwatch, Reposition, Support, Join, Regroup", "Squads.cs:22-33; Commander.cs:140-150"),
        ("Doi", "Doi_hinh", "Theo hành động đã chọn", "1 trong 5 đội hình: Travel, Spread, Hold, Flank, Regroup",
         "Squads.cs:39-47"),
        ("DonVi", "Vai_tro", "aiBehaviour.units.<đơn_vị> (sheet AI_don_vi)", "Vai trò AI (sheet AI_vai_tro): ngưỡng "
         "giao chiến riêng, phản ứng khi bị áp đảo (giữ nguyên / lùi / đổi mục tiêu)", "AiBehaviour.cs; TacticalAi.cs"),
        ("DonVi", "Chong_ket", "Đứng im quá lâu, không có gì để bắn (xem sheet AI_chong_ket)", "Tự đi về phía địch gần "
         "nhất đã biết, hoặc mục tiêu, bỏ qua đợi đội hình", "TacticalAi.cs:67-79,1464-1473"),
        ("DonVi", "Tiep_te_may_bay", "Máy bay hết đạn / máu thấp (xem sheet AI_may_bay_tiep_te)", "Về sân bay nạp lại, "
         "hoặc nạp đạn tại chỗ trong lúc nghỉ trận đánh", "TacticalAi.cs:471-560,770-822"),
        ("NhatKy", "Vi_sao", "Mỗi quyết định có điểm (AiCommander/Squad/đơn vị chấm nhiều lựa chọn)", "Giữ lựa chọn + "
         "điểm, 3 điểm cộng lớn nhất, 2 điểm trừ lớn nhất, á quân (Why, J.2); người xem đọc 'VÌ SAO'", "DecisionLog.cs:"
         "27-85"),
        ("NhatKy", "Canh_bao_doi_chieu", "Một đội đổi hành động/trạng thái/mục tiêu quá WarnPerMinute lần/phút (mặc "
         "định 6)", "Gắn cờ 'churning' (Churning), cảnh báo người xem AI đang phân vân quá nhiều", "DecisionLog.cs:"
         "118-171"),
    ]
    for lop, buoc, dk, kq, cite in rows:
        r = s.row(f"{lop}/{buoc}", f"Sim/AI: {cite}")
        r.set("lop", lop)
        r.set("buoc", buoc)
        r.set("dieu_kien", dk)
        r.set("ket_qua", kq)
        r.set("nguon_ma", cite)


# ------------------------------------------------------------------------------------------------ AI_muc_tieu_uu_tien
def _targets(book):
    s = book.sheet("AI_muc_tieu_uu_tien", "Mục tiêu ưu tiên",
                   "Prompt 28 E (tháp) và F.2 (boss): hệ số nhân thêm vào điểm mục tiêu đã có (CombatSystem), theo "
                   "TowerMode của tháp hoặc BossBehaviour của boss. Điểm càng cao càng được ưu tiên bắn trước", layer="C")
    s.col("loai", meaning="thap / boss", enum=["thap", "boss"])
    s.col("kieu", meaning="TowerMode hoặc BossBehaviour (tên enum trong mã, không phải id tháp/boss)")
    s.col("cong_thuc", meaning="hệ số nhân vào điểm mục tiêu (python, port từ C#)")
    s.col("dieu_kien", meaning="khi nào áp dụng / ghi chú")
    s.col("nguon_ma", meaning="file:dòng")
    rows = [
        ("thap", "Nearest", "1 / (1 + 2*khoang_cach/tam_ban)", "NearestRound, ShieldKey dùng chung công thức này",
         "Combat/CombatSystem.P28Structures.cs:36"),
        ("thap", "Strongest", "sqrt(max(0.5, suc_manh_muc_tieu))", "StrengthOf: ước lượng sức mạnh từ TeamIntel",
         "Combat/CombatSystem.P28Structures.cs:37"),
        ("thap", "Weakest", "1.6 - hp_share + 200/max(50,hp)", "Ưu tiên máu thấp, thưởng thêm khi máu tuyệt đối nhỏ",
         "Combat/CombatSystem.P28Structures.cs:38"),
        ("thap", "Lead", "Lead(thap, muc_tieu) [dẫn bắn]", "Hàm Lead(): ưu tiên mục tiêu dễ đón đầu",
         "Combat/CombatSystem.P28Structures.cs:39"),
        ("thap", "AirFirst", "3 nếu bay, 1 nếu không", "Dùng chung công thức với MissilesFirst",
         "Combat/CombatSystem.P28Structures.cs:40"),
        ("thap", "BiggestAircraft", "nếu bay: 1 + maxHp/300; nếu không: 0.5", "Phạt nặng mục tiêu mặt đất",
         "Combat/CombatSystem.P28Structures.cs:41"),
        ("thap", "Cluster", "1 + 0.5*so_dong_quanh(8m)", "Crowd(): đếm địch trong bán kính 8 m",
         "Combat/CombatSystem.P28Structures.cs:42"),
        ("thap", "ArtilleryFirst", "3 nếu vũ khí có tầm tối thiểu (pháo), 1 nếu không", "",
         "Combat/CombatSystem.P28Structures.cs:43"),
        ("thap", "MissilesFirst", "chỉ bắn đạn Missile/Rocket (loại khác bị loại hẳn, không phải hệ số)", "Lọc cứng, "
         "không phải nhân điểm", "Combat/CombatSystem.P28Structures.cs:135"),
        ("thap", "ShieldKey", "công thức Nearest, cộng: chỉ nhắm vào thứ phá khiên của boss nếu từ boss bắn ra", "",
         "Combat/CombatSystem.P28Structures.cs:136-137"),
        ("thap", "Default_None", "1 (không đổi điểm)", "Default: dùng mode mặc định của tháp (aiBehaviour.towers); "
         "None: tắt lọc đặc biệt", "AI/TowerModes.cs:11-23"),
        ("boss", "AntiBlob", "1 + 0.4*so_dong_quanh(10m)", "Ưu tiên đám đông dày đặc", "Bosses/BossSystem.P28.cs:105; "
         "Combat/CombatSystem.P28Structures.cs:117"),
        ("boss", "AntiAir", "2.5 nếu bay, 1 nếu không", "", "Combat/CombatSystem.P28Structures.cs:118"),
        ("boss", "AntiArtillery", "3 nếu vũ khí có tầm tối thiểu; 1.3 nếu đứng yên; 1 nếu đang di chuyển", "",
         "Bosses/BossSystem.P28.cs:103; Combat/CombatSystem.P28Structures.cs:119"),
        ("boss", "CoreProtection", "2 (boss)/1.8 (khác) nếu mục tiêu đang nhắm vào 'lõi' trong 30 m, 1 nếu không", "",
         "Bosses/BossSystem.P28.cs:106; Combat/CombatSystem.P28Structures.cs:120"),
        ("boss", "FlankPunishment", "2.2 nếu mục tiêu đánh từ sau lưng (Behind), 1 nếu không", "",
         "Bosses/BossSystem.P28.cs:107; Combat/CombatSystem.P28Structures.cs:121"),
        ("boss", "AreaDenial", "1.6 nếu mục tiêu đứng yên, 1 nếu đang di chuyển", "Phạt đứng một chỗ (giữ bãi)",
         "Bosses/BossSystem.P28.cs:104; Combat/CombatSystem.P28Structures.cs:122"),
    ]
    for loai, kieu, ct, dk, cite in rows:
        r = s.row(f"{loai}/{kieu}", f"Sim: {cite}")
        r.set("loai", loai)
        r.set("kieu", kieu)
        r.set("cong_thuc", ct)
        r.set("dieu_kien", dk)
        r.set("nguon_ma", cite)


# -------------------------------------------------------------------------------------------------------- AI_do_kho
def _difficulty(book):
    s = book.sheet("AI_do_kho_ky_nang", "Độ khó: kỹ năng AI (AiSkill)",
                   "Commander.cs AiSkill.For: độ khó đổi độ trễ phản ứng, quên dần, độ trải quân trước khi dính splash, "
                   "tần suất đánh vu hồi, tần suất tập trung hỏa lực, và cách đổi chiến thuật giữa trận. normal/min/max "
                   "đọc từ balance.json ai.params.reactionDelay (sheet AI_tham_so)", layer="C")
    s.col("do_kho", fk=["05_che_do_kinh_te/Do_kho"], meaning="độ khó")
    s.col("reaction_delay", meaning="độ trễ phản ứng (s): Easy = max; Normal = giá trị gốc; Hard = gốc - (gốc-min)*0.6; "
          "VeryHard = min")
    s.col("decay_scale", meaning="tốc độ quên mục tiêu đã thấy (nhân vào thời gian nhớ; 1 = gốc)")
    s.col("spread", meaning="mức trải quân trước khi dính splash (1 = gốc, Easy 0.5 = trải kém hơn)")
    s.col("flank", meaning="tần suất đánh vu hồi (1 = gốc)")
    s.col("focus", meaning="tần suất tập trung hỏa lực (1 = gốc; Easy 0 = không tập trung)")
    s.col("doi_chien_thuat", meaning="TacticSwitching giữa trận", enum=["Never", "WhenLosing", "Counter"])
    cite = "Sim/AI/Commander.cs:33-50"
    rows = [
        ("Easy", "max", 1.5, 0.5, 0.5, 0.0, "Never"),
        ("Normal", "normal (ai.params.reactionDelay)", 1.0, 1.0, 1.0, 1.0, "Never"),
        ("Hard", "normal - (normal-min)*0.6", 0.85, 1.0, 1.3, 1.3, "WhenLosing"),
        ("VeryHard", "min", 0.6, 1.0, 1.3, 1.3, "Counter"),
    ]
    for do_kho, rd, decay, spread, flank, focus, sw in rows:
        r = s.row(do_kho, cite)
        r.set("do_kho", do_kho)
        r.set("reaction_delay", rd)
        r.set("decay_scale", decay)
        r.set("spread", spread)
        r.set("flank", flank)
        r.set("focus", focus)
        r.set("doi_chien_thuat", sw)


# ------------------------------------------------------------------------------------------------------ AI_chong_ket
def _antistuck(book):
    s = book.sheet("AI_chong_ket", "Chống kẹt / chống đứng im",
                   "TacticalAi.cs (Play-test 6, DECISIONS 21G): hằng số và luật chống một đơn vị hay cả đội đứng mãi "
                   "không làm gì (kẹt ở hàng chờ, kẹt ở rìa bản đồ, kẹt khi bị áp đảo)", layer="C")
    s.col("ten", meaning="tên hằng số / luật")
    s.col("gia_tri", meaning="giá trị", unit="s")
    s.col("y_nghia", meaning="ý nghĩa")
    s.col("nguon_ma", meaning="file:dòng")
    rows = [
        ("StaleIdle", 12.0, "Đơn vị đứng im, không có gì để bắn, quá 12 s: tự đi về phía địch gần nhất đã biết, hoặc "
         "mục tiêu (bỏ qua chờ đội hình tập hợp)", "TacticalAi.cs:77,1466-1473"),
        ("Patience", 30.0, "Đội bị áp đảo (outmatched) lùi/giữ quá 30 s mà chưa đuổi kịp quân: vẫn xông vào (chờ mãi "
         "thì thua vì hết giờ)", "TacticalAi.cs:130-132,381"),
        ("FallBackHold", 12.0, "Một đợt lùi (fall back) kéo dài tối thiểu 12 s, để quân không nhấp nhô vào/ra tầm bắn "
         "liên tục", "TacticalAi.cs:126,379"),
        ("RecoveredFraction", 0.6, "Đơn vị đã lùi hồi phục đủ 60% máu (hoặc hết FallBackSeconds) thì nhập lại đội",
         "TacticalAi.cs:38,736"),
        ("EdgePatience", 70.0, "Đội chờ ở rìa bản đồ (gom pháo/đợi đủ mạnh) quá 70 s: xông vào nếu còn đủ sức so với "
         "tháp (ngưỡng nới từ StrongEnough xuống còn hệ số 1)", "TacticalAi.cs:227,1290"),
        ("ClusterSize", 3.0, "Kích thước cụm tối thiểu khi gom đội hình (dùng ở cả tướng và đội)", "ConquestAi.cs:99; "
         "TacticalAi.cs:34"),
        ("EdgeMargin", 6.0, "Khoảng lùi khỏi rìa bản đồ khi định vị trí đứng", "TacticalAi.cs:35"),
    ]
    for ten, gt, yn, cite in rows:
        r = s.row(ten, f"Sim/AI/{cite}")
        r.set("ten", ten)
        r.set("gia_tri", gt)
        r.set("y_nghia", yn)
        r.set("nguon_ma", cite)


# ------------------------------------------------------------------------------------------------- AI_may_bay_tiep_te
def _aircraft(book):
    s = book.sheet("AI_may_bay_tiep_te", "Máy bay: vòng tiếp tế / nghỉ giữa đợt đánh",
                   "TacticalAi.cs: khi một máy bay (hoặc xe có kho đạn HasStores) rời vị trí để nạp lại, khi nó nạp tại "
                   "chỗ trong lúc nghỉ, và khi nó quay lại sân bay sửa chữa (Refit)", layer="C")
    s.col("buoc", meaning="tên bước")
    s.col("dieu_kien", meaning="điều kiện")
    s.col("ket_qua", meaning="kết quả")
    s.col("nguon_ma", meaning="file:dòng")
    rows = [
        ("SendToRearm", "Súng chính hết đạn (launcher rỗng) hoặc xe có AirRearm/RearmAura", "Tìm điểm tiếp tế gần nhất "
         "(RearmAura bạn x0.6 bán kính, hoặc điểm tập kết (rally) trong 12 m, hoặc kho tiếp tế); bay/đi tới đó",
         "TacticalAi.cs:473-496"),
        ("RearmInLulls", "Đang chiến đấu (Supply.Fighting), kho đạn dưới ngưỡng thấp (SupplySystem.LowShare), chưa yêu "
         "cầu nạp, không có mục tiêu và chưa bắn được 4 s (lúc trận đang 'lặng')", "Gửi lệnh Rearm để nạp đầy khi đang "
         "nghỉ, sẵn sàng cho đợt đánh kế", "TacticalAi.cs:559-568"),
        ("Refit", "Máy bay (Flying) máu dưới RefitUntil (90%) lần đầu, hoặc đang trong danh sách refit và chưa hồi đủ "
         "90% máu", "Rời về sân bay; ở lại danh sách _refitting tới khi Hp >= MaxHp*0.9 thì rời nhóm, bay lại nhiệm vụ",
         "TacticalAi.cs:518-546"),
        ("HuntRearming", "HuntSupply bật (vai trò săn tiếp tế) và phát hiện xe tiếp tế / sửa chữa của địch (AirRepair "
         "hoặc AirRearm)", "Điều máy bay/pháo rảnh gần nhất đi diệt xe tiếp tế địch trước (cắt tiếp tế đối phương)",
         "TacticalAi.cs:794-822"),
        ("KhongDan", "Launcher mặt đất hết đạn (OutOfAmmo), không bay", "Đứng yên nạp lại, hoặc đi tới xe tiếp tế gần "
         "nếu có, không tham chiến trong lúc đó", "TacticalAi.cs:772-787"),
    ]
    for buoc, dk, kq, cite in rows:
        r = s.row(buoc, f"Sim/AI/{cite}")
        r.set("buoc", buoc)
        r.set("dieu_kien", dk)
        r.set("ket_qua", kq)
        r.set("nguon_ma", cite)


# ---------------------------------------------------------------------------------------------------- AI_hang_so_ma
_CONST_LINE = re.compile(
    r"(?:private|public|internal)\s+(?:static\s+)?(?:readonly\s+)?const\s+(int|float|double|bool)\s+([^;]+);")
_ARRAY_LINE = re.compile(
    r"(?:private|public|internal)\s+static\s+readonly\s+(float|int|double)\[\]\s+(\w+)\s*=\s*\{([^}]*)\};")


def _doc_above(lines: list[str], line_no: int) -> str:
    """The /// summary directly above a 1-based line number, cleaned of XML tags."""
    out = []
    i = line_no - 2
    while i >= 0 and lines[i].strip().startswith("///"):
        out.insert(0, lines[i].strip().lstrip("/").strip())
        i -= 1
    text = " ".join(out)
    text = re.sub(r"</?summary>", "", text)
    text = re.sub(r"<see cref=\"[^\"]*\"\s*/?>", "", text)
    text = re.sub(r"<paramref name=\"([^\"]*)\"\s*/?>", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def _constants(book):
    s = book.sheet("AI_hang_so_ma", "Hằng số AI còn trong mã",
                   "Mọi hằng số đặt tên (const / static readonly mảng số) của 14 file Sim/AI chưa dọn sang "
                   "tunables.json (khác Hang_so_ai: đó là hằng số ĐÃ dọn sang dữ liệu). Quét tĩnh bằng regex mỗi lần "
                   "build (Tools/export/domains/_c06.py); hằng số nào dọn sang data sẽ tự biến mất khỏi sheet này",
                   layer="C")
    s.col("file", meaning="file trong Sim/AI")
    s.col("dong", meaning="số dòng khai báo")
    s.col("ten", meaning="tên hằng số")
    s.col("kieu", meaning="kiểu C#")
    s.col("gia_tri", meaning="giá trị (chuỗi, kể cả mảng 'a;b;c')")
    s.col("y_nghia", meaning="tóm tắt /// summary ngay trên khai báo (trống nếu mã không có)")
    seen = set()
    for fname in AI_FILES:
        path = AI_DIR + fname
        text = (ROOT / path).read_text("utf-8-sig")
        lines = text.splitlines()
        for m in _CONST_LINE.finditer(text):
            kind, body = m.group(1), m.group(2)
            line_no = text.count("\n", 0, m.start()) + 1
            for part in body.split(","):
                part = part.strip()
                if "=" not in part:
                    continue
                name, _, value = part.partition("=")
                name, value = name.strip(), value.strip()
                if not name:
                    continue
                rid = f"{fname}:{name}"
                if rid in seen:
                    continue
                seen.add(rid)
                r = s.row(rid, f"{AI_DIR}{fname}:{line_no}")
                r.set("file", fname)
                r.set("dong", line_no)
                r.set("ten", name)
                r.set("kieu", kind)
                r.set("gia_tri", value)
                r.set("y_nghia", _doc_above(lines, line_no))
        for m in _ARRAY_LINE.finditer(text):
            kind, name, body = m.group(1), m.group(2), m.group(3)
            line_no = text.count("\n", 0, m.start()) + 1
            rid = f"{fname}:{name}"
            if rid in seen:
                continue
            seen.add(rid)
            vals = ";".join(v.strip() for v in body.split(",") if v.strip())
            r = s.row(rid, f"{AI_DIR}{fname}:{line_no}")
            r.set("file", fname)
            r.set("dong", line_no)
            r.set("ten", name)
            r.set("kieu", f"{kind}[]")
            r.set("gia_tri", vals)
            r.set("y_nghia", _doc_above(lines, line_no))


def build(ctx, book):
    _flow(book)
    _targets(book)
    _difficulty(book)
    _antistuck(book)
    _aircraft(book)
    _constants(book)
