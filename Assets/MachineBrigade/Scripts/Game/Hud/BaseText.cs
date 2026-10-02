using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 32 L4-L8: the base system's new words in English and Vietnamese (the HQ types and their skill, the HQ's
    /// damage marks, the opening squads, the ammunition handbook's frame). Numbers are filled from the data.
    /// </summary>
    public static class BaseText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- L4: HQ types
            ["hq.type.fortress"] = ("Fortress", "Pháo đài"),
            ["hq.type.garrison"] = ("Garrison", "Đồn trú"),
            ["hq.type.shield"] = ("Shield", "Lá chắn"),
            ["hq.branch.ground"] = ("ground guns", "pháo mặt đất"),
            ["hq.branch.air"] = ("anti-air guns", "pháo phòng không"),
            ["hq.type.fortress.info"] = ("Guns on the HQ ({branch}): {share}% of a medium tower's fire at this HQ level.",
                "Vũ khí trên nhà chính ({branch}): {share}% hỏa lực một tháp vừa ở cấp nhà chính này."),
            ["hq.type.garrison.info"] = ("A squad stocked every {every} s (two at most) turns out when enemies enter the base; up to {cap} CP of it alive. It never leaves the base and goes back in after {clear} s of quiet.",
                "Mỗi {every} s tích một tổ (tối đa hai), tự ra khi địch vào căn cứ; tối đa {cap} CP còn sống. Không rời căn cứ, rút vào sau {clear} s yên tĩnh."),
            ["hq.type.shield.info"] = ("A point-defence dome over the base ({share}% of a medium C-RAM: missiles, drones, rockets, part of the shells; never tank shells); towers unhit for {delay} s mend {regen}% a second.",
                "Vòm phòng thủ điểm trên căn cứ ({share}% một C-RAM vừa: tên lửa, drone, rốc-két, một phần đạn pháo; không chặn đạn pháo xe tăng); tháp không trúng đạn {delay} s hồi {regen}% máu mỗi giây."),
            ["hq.skill.fortress"] = ("Barrage", "Loạt bắn"),
            ["hq.skill.garrison"] = ("Alarm", "Báo động"),
            ["hq.skill.shield"] = ("Dome", "Vòm khiên"),
            ["hq.skill.fortress.tip"] = ("Focused barrage: three heavy rounds on the point you tap. Every {cooldown} s.",
                "Loạt bắn tập trung: ba phát mạnh vào điểm bạn chạm. Mỗi {cooldown} s."),
            ["hq.skill.garrison.tip"] = ("Alarm: every stocked squad turns out now ({stock} ready). Every {cooldown} s.",
                "Báo động: mọi tổ đã tích ra ngay ({stock} tổ sẵn sàng). Mỗi {cooldown} s."),
            ["hq.skill.shield.tip"] = ("Emergency dome: for {seconds} s the base's dome absorbs {share}% of the HQ's health. Every {cooldown} s.",
                "Vòm khiên khẩn cấp: trong {seconds} s vòm hấp thụ {share}% máu tối đa của nhà chính. Mỗi {cooldown} s."),
            ["target.hqSkill"] = ("Tap where the HQ's barrage lands", "Chạm vào nơi loạt bắn của nhà chính rơi xuống"),
            ["camp.hqType"] = ("HQ type: {type} · tap to change", "Kiểu nhà chính: {type} · chạm để đổi"),
            ["camp.hqTypeFortress"] = ("{type} ({branch})", "{type} ({branch})"),
            ["hq.news.title"] = ("HQ types", "Kiểu nhà chính"),
            ["news.hqType"] = ("The HQ doctrine is now the HQ type: Fortress, Garrison or Shield. Choose one free on the Base screen (tap the HQ).",
                "Học thuyết nhà chính nay là kiểu nhà chính: Pháo đài, Đồn trú hoặc Lá chắn. Chọn miễn phí ở màn Căn cứ (chạm vào nhà chính)."),
            ["unit.headquarters.fortress_ground"] = ("Headquarters · Fortress", "Sở chỉ huy · Pháo đài"),
            ["unit.headquarters.fortress_air"] = ("Headquarters · AA Fortress", "Sở chỉ huy · Pháo đài phòng không"),
            ["unit.headquarters.shield"] = ("Headquarters · Shield", "Sở chỉ huy · Lá chắn"),
            ["short.headquarters.fortress_ground"] = ("Fortress HQ", "SCH Pháo đài"),
            ["short.headquarters.fortress_air"] = ("AA Fortress", "Pháo đài PK"),
            ["short.headquarters.shield"] = ("Shield HQ", "SCH Lá chắn"),

            // The HQ's damage marks (50 %: a warning only, no loss of function; 25 %: a warning and one free rebuild).
            ["alert.hq.half.ours"] = ("Our HQ is at half strength", "Nhà chính của ta còn một nửa máu"),
            ["alert.hq.half.theirs"] = ("The enemy HQ is at half strength", "Nhà chính địch còn một nửa máu"),
            ["alert.hq.quarter.ours"] = ("Our HQ is badly hit: a tower is flown back in", "Nhà chính của ta bị đánh nặng: một tháp được thả lại"),
            ["alert.hq.quarter.theirs"] = ("The enemy HQ is badly hit", "Nhà chính địch bị đánh nặng"),
            ["alert.hq.garrison.ours"] = ("The garrison turns out", "Quân đồn trú xuất kích"),
            ["alert.hq.garrison.theirs"] = ("Enemy garrison turning out", "Quân đồn trú địch xuất kích"),
            ["alert.hq.dome.ours"] = ("Emergency dome up", "Vòm khiên khẩn cấp đã bật"),
            ["alert.hq.dome.theirs"] = ("Enemy emergency dome up", "Địch bật vòm khiên khẩn cấp"),
        };
    }
}
