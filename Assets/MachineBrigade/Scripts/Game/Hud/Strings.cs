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
        };

        public static bool Vietnamese { get; set; } = Application.systemLanguage == SystemLanguage.Vietnamese;

        public static string Get(string key) =>
            Table.TryGetValue(key, out var text) ? (Vietnamese ? text.vi : text.en) : key;

        public static string Format(string key, params object[] args) => string.Format(Get(key), args);

        public static string Error(CommandError error) => Get("err." + error);

        public static string Unit(string defId) => Get("unit." + defId);
    }
}
