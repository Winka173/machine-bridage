using System.Collections.Generic;
using MachineBrigade.Sim.Commands;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Player-facing text in English and Vietnamese. The language follows the device, like
    /// Sticky-Wall. A settings override and the Unity Localization tables come with the menus.
    /// </summary>
    public static class Strings
    {
        private static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            ["brand.top"] = ("MACHINE", "MACHINE"),
            ["brand.bottom"] = ("B R I G A D E", "B R I G A D E"),
            ["stat.allies"] = ("ALLIES", "QUÂN TA"),
            ["stat.enemies"] = ("ENEMIES", "ĐỊCH"),
            ["stat.wave"] = ("WAVE", "ĐỢT"),
            ["stat.next"] = ("NEXT WAVE", "ĐỢT SAU"),
            ["mission.kicker"] = ("OPERATION 01  /  SANDBOX", "CHIẾN DỊCH 01  /  SA BÀN"),
            ["mission.title"] = ("Ashfield.", "Ashfield."),
            ["mission.sub"] = ("HOLD THE LINE  ·  WAVES INCOMING", "GIỮ VỮNG TRẬN ĐỊA  ·  ĐỊCH ĐANG ĐẾN"),
            ["panel.selection"] = ("SELECTION", "ĐANG CHỌN"),
            ["panel.selected"] = ("{0} SELECTED", "{0} XE"),
            ["panel.none"] = ("No vehicles selected", "Chưa chọn xe"),
            ["panel.noneHint"] = ("Tap a vehicle, or use Army", "Chạm vào xe, hoặc bấm Quân đội"),
            ["panel.mixed"] = ("Battle group", "Cụm chiến đấu"),
            ["panel.hp"] = ("{0} / {1} HP", "{0} / {1} HP"),
            ["cmd.attackMove"] = ("Attack-move", "Tiến công"),
            ["cmd.stop"] = ("Stop", "Dừng"),
            ["cmd.retreat"] = ("Retreat", "Rút lui"),
            ["cmd.reinforce"] = ("Reinforce", "Tiếp viện"),
            ["cmd.reinforceReady"] = ("+2 vehicles", "+2 xe"),
            ["cmd.reinforceWait"] = ("Ready in {0}s", "Sẵn sàng sau {0}s"),
            ["tool.army"] = ("Army", "Quân đội"),
            ["tool.box"] = ("Box", "Quét chọn"),
            ["hint"] = ("Tap to select  ·  Drag to pan  ·  Pinch to zoom", "Chạm để chọn  ·  Kéo để di chuyển  ·  Chụm để thu phóng"),
            ["hint.attackMove"] = ("Tap the ground to attack-move", "Chạm xuống đất để tiến công"),
            ["hint.box"] = ("Drag to box-select your vehicles", "Kéo để quét chọn xe"),
            ["toast.reinforceWait"] = ("Reinforcements are not ready", "Tiếp viện chưa sẵn sàng"),
            ["toast.start"] = ("Enemy armour sighted. Select your vehicles and attack.", "Phát hiện thiết giáp địch. Chọn xe và tấn công."),
            ["toast.wave"] = ("Wave {0} incoming", "Đợt {0} đang tới"),
            ["err.NoUnits"] = ("Select your vehicles first", "Hãy chọn xe trước"),
            ["err.InvalidTarget"] = ("That can't be attacked", "Không thể tấn công mục tiêu này"),
            ["err.TargetNotVisible"] = ("Target not visible", "Không nhìn thấy mục tiêu"),
            ["err.OutOfBounds"] = ("Outside the battlefield", "Ngoài chiến trường"),
            ["err.InvalidPoint"] = ("Invalid destination", "Điểm đến không hợp lệ"),
            ["err.NoRallyPoint"] = ("No rally point", "Không có điểm tập kết"),
            ["err.MatchOver"] = ("The match is over", "Trận đấu đã kết thúc"),
            ["unit.scout_jeep"] = ("Scout jeep", "Xe trinh sát"),
            ["unit.light_tank"] = ("Light tank", "Tăng hạng nhẹ"),
            ["unit.main_battle_tank"] = ("Main battle tank", "Tăng chủ lực"),
            ["unit.artillery"] = ("Artillery", "Pháo tự hành"),
            ["unit.apc"] = ("APC", "Xe bọc thép"),
            ["unit.flame_tank"] = ("Flame tank", "Tăng phun lửa"),
            ["unit.mlrs"] = ("Rocket launcher", "Pháo phản lực"),
            ["unit.aa_vehicle"] = ("Anti-air", "Xe phòng không"),
            ["unit.attack_helicopter"] = ("Gunship", "Trực thăng tấn công"),
            ["support.artillery_barrage"] = ("Barrage", "Pháo kích"),
            ["support.airstrike"] = ("Airstrike", "Không kích"),
            ["support.cruise_missile"] = ("Cruise missile", "Tên lửa hành trình"),
            ["support.smoke_screen"] = ("Smoke", "Màn khói"),
            ["support.repair_drop"] = ("Repair", "Sửa chữa"),
            ["stat.tickets"] = ("TICKETS", "ĐIỂM"),
            ["stat.cp"] = ("CP", "CP"),
            ["stat.army"] = ("ARMY {0}/{1}", "QUÂN {0}/{1}"),
            ["point.west"] = ("A", "A"),
            ["point.town"] = ("B", "B"),
            ["point.east"] = ("C", "C"),
            ["mission.conquest.kicker"] = ("OPERATION 02  /  CONQUEST", "CHIẾN DỊCH 02  /  GIỮ CỨ ĐIỂM"),
            ["mission.conquest.sub"] = ("HOLD MORE POINTS THAN THE ENEMY", "GIỮ NHIỀU CỨ ĐIỂM HƠN ĐỊCH"),
            ["mission.survival.kicker"] = ("OPERATION 01  /  SURVIVAL", "CHIẾN DỊCH 01  /  SINH TỒN"),
            ["toast.conquestStart"] = ("Capture the points. Buy vehicles and strikes from the deck below.", "Chiếm cứ điểm. Mua xe và yểm trợ ở thanh bên dưới."),
            ["toast.deployed"] = ("{0} on the way", "{0} đang tới"),
            ["toast.captured"] = ("Point {0} captured", "Đã chiếm cứ điểm {0}"),
            ["toast.lost"] = ("Point {0} lost", "Mất cứ điểm {0}"),
            ["toast.enemyStrike"] = ("Enemy {0} incoming!", "Địch gọi {0}!"),
            ["toast.airDefence"] = ("Enemy aircraft: bring anti-air", "Máy bay địch: hãy dùng xe phòng không"),
            ["target.hint"] = ("Tap the battlefield to call {0}", "Chạm vào chiến trường để gọi {0}"),
            ["target.cancel"] = ("Cancel", "Hủy"),
            ["err.UnknownCard"] = ("Not in your deck", "Không có trong bộ bài"),
            ["err.NotEnoughCp"] = ("Not enough CP", "Không đủ CP"),
            ["err.ArmyAtCapacity"] = ("Army at capacity", "Quân đã đầy"),
            ["err.OnCooldown"] = ("Not ready yet", "Chưa sẵn sàng"),
            ["err.NotAvailable"] = ("Not available in this mode", "Không dùng được ở chế độ này"),
            ["result.victory"] = ("VICTORY", "CHIẾN THẮNG"),
            ["result.defeat"] = ("DEFEAT", "THẤT BẠI"),
            ["result.draw"] = ("DRAW", "HÒA"),
            ["result.over"] = ("THE LINE HAS FALLEN", "TRẬN ĐỊA ĐÃ THẤT THỦ"),
            ["result.kills"] = ("Destroyed", "Tiêu diệt"),
            ["result.losses"] = ("Lost", "Tổn thất"),
            ["result.time"] = ("Time", "Thời gian"),
            ["result.waves"] = ("Waves held", "Số đợt trụ được"),
            ["result.again"] = ("Play again", "Chơi lại"),
            ["result.menu"] = ("Main menu", "Về menu"),
            ["menu.play"] = ("Deploy", "Xuất kích"),
            ["menu.mode"] = ("MODE", "CHẾ ĐỘ"),
            ["menu.conquest"] = ("Conquest", "Giữ cứ điểm"),
            ["menu.conquestSub"] = ("Take and hold 3 objectives", "Chiếm và giữ 3 cứ điểm"),
            ["menu.survival"] = ("Survival", "Sinh tồn"),
            ["menu.survivalSub"] = ("Hold out against endless waves", "Trụ vững trước các đợt tấn công"),
            ["menu.difficulty"] = ("DIFFICULTY", "ĐỘ KHÓ"),
            ["menu.easy"] = ("Easy", "Dễ"),
            ["menu.normal"] = ("Normal", "Thường"),
            ["menu.hard"] = ("Hard", "Khó"),
            ["menu.weather"] = ("WEATHER", "THỜI TIẾT"),
            ["menu.clear"] = ("Clear", "Nắng"),
            ["menu.overcast"] = ("Overcast", "Nhiều mây"),
            ["menu.rain"] = ("Rain", "Mưa"),
            ["menu.storm"] = ("Storm", "Bão"),
            ["menu.random"] = ("Random", "Ngẫu nhiên"),
            ["menu.deck"] = ("Deck", "Bộ bài"),
            ["menu.deckTitle"] = ("YOUR DECK  ·  {0}/{1} VEHICLES  ·  {2}/{3} SUPPORT", "BỘ BÀI  ·  {0}/{1} XE  ·  {2}/{3} YỂM TRỢ"),
            ["menu.settings"] = ("Settings", "Cài đặt"),
            ["menu.back"] = ("Back", "Quay lại"),
            ["menu.tagline"] = ("Command the armour. Break the line.", "Chỉ huy thiết giáp. Phá vỡ phòng tuyến."),
            ["settings.volume"] = ("Sound volume", "Âm lượng"),
            ["settings.quality"] = ("Effects quality", "Chất lượng hiệu ứng"),
            ["settings.high"] = ("High", "Cao"),
            ["settings.eco"] = ("Eco", "Tiết kiệm"),
            ["settings.motion"] = ("Reduced motion", "Giảm chuyển động"),
            ["settings.fps"] = ("Show FPS", "Hiện FPS"),
            ["settings.language"] = ("Language", "Ngôn ngữ"),
            ["settings.auto"] = ("Auto", "Tự động"),
            ["settings.on"] = ("On", "Bật"),
            ["settings.off"] = ("Off", "Tắt"),
            ["pause.title"] = ("PAUSED", "TẠM DỪNG"),
            ["panel.commander"] = ("COMMANDER", "CHỈ HUY"),
            ["stance.attack"] = ("Attack", "Tấn công"),
            ["stance.defend"] = ("Defend", "Phòng thủ"),
            ["auto.deploy"] = ("Auto buy", "Tự mua xe"),
            ["auto.strike"] = ("Auto support", "Tự yểm trợ"),
            ["toast.focus"] = ("Army converging on point {0}", "Quân ta dồn về cứ điểm {0}"),
            ["toast.focusClear"] = ("The commander picks targets", "Chỉ huy tự chọn mục tiêu"),
            ["toast.attack"] = ("Stance: attack", "Thế trận: tấn công"),
            ["toast.defend"] = ("Stance: defend", "Thế trận: phòng thủ"),
            ["hint.auto"] = ("Your army fights on its own  ·  Tap A B C to point it  ·  Tap a vehicle to take control",
                "Quân ta tự chiến đấu  ·  Chạm A B C để chỉ hướng  ·  Chạm xe để điều khiển tay"),
            ["pause.resume"] = ("Resume", "Tiếp tục"),
        };

        public static bool Vietnamese { get; set; } = Application.systemLanguage == SystemLanguage.Vietnamese;

        public static string Get(string key) =>
            Table.TryGetValue(key, out var text) ? (Vietnamese ? text.vi : text.en) : key;

        public static string Format(string key, params object[] args) => string.Format(Get(key), args);

        public static string Error(CommandError error) => Get("err." + error);

        public static string Unit(string defId) => Get("unit." + defId);

        public static string Support(string defId) => Get("support." + defId);

        /// <summary>Vehicle or support card name.</summary>
        public static string Card(string defId) => Table.ContainsKey("unit." + defId) ? Unit(defId) : Support(defId);
    }
}
