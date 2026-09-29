using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 19: the orbital boss's words (Silver Bug, Aurel's orbital spacecraft): the altitude
    /// tiers, its Guide section, Aurel's and HQ's radio chatter (prompt 23 turns these into one
    /// subtitle line), and the toasts that mark a tier change, a drop-pod wave, and a drone hijack.
    /// Its parts and big attack live next to the other bosses', in Strings.cs and BigAttackText.cs.
    /// </summary>
    public static class OrbitalText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- altitude tiers
            ["tier.orbit"] = ("Low orbit", "Quỹ đạo thấp"),
            ["tier.high"] = ("High altitude", "Tầng cao"),
            ["tier.low"] = ("Low altitude", "Tầng thấp"),
            ["tier.ground"] = ("Crashed", "Đã rơi"),
            ["tier.shift"] = ("Changing altitude", "Đang đổi tầng"),
            ["hud.tier"] = ("Its altitude now, and the wait to the next change.", "Tầng độ cao hiện tại của nó, và thời gian tới lần đổi tầng tiếp theo."),
            ["hud.tier.next"] = ("{tier} in {seconds} s", "{tier} sau {seconds} giây"),
            ["hud.tier.reach"] = ("Can hit it now", "Bắn tới được ngay bây giờ"),
            ["hud.tier.none"] = ("Nothing in your deck reaches it now", "Không thẻ nào trong bộ bài bắn tới được lúc này"),
            ["hud.tier.partial"] = ("only a secondary weapon reaches it", "chỉ vũ khí phụ bắn tới được nó"),

            // ---------------------------------------------------------------- guide
            ["guide.tiers"] = ("Altitude tiers", "Tầng độ cao"),
            ["guide.tiers.rule"] = ("It keeps to a fixed schedule whatever you do; only this boss and its falling drop pods use altitude tiers.", "Nó bám theo lịch cố định bất kể bạn làm gì; chỉ boss này và các khoang đổ bộ đang rơi của nó dùng khái niệm tầng độ cao."),
            ["guide.tiers.orbit"] = ("Low orbit: only in the opening, about 15 s. Nothing in your deck reaches it there.", "Quỹ đạo thấp: chỉ trong đoạn mở màn, khoảng 15 giây. Không vũ khí nào của bạn bắn tới được."),
            ["guide.tiers.high"] = ("High altitude: only long-range SAMs, Patriot batteries, fighters and stealth fighters reach it.", "Tầng cao: chỉ SAM tầm xa, dàn Patriot, tiêm kích và tiêm kích tàng hình bắn tới được."),
            ["guide.tiers.low"] = ("Low altitude: every weapon that can hit aircraft or helicopters reaches it, plus railguns against this boss only.", "Tầng thấp: mọi vũ khí bắn được máy bay hoặc trực thăng đều bắn tới, cộng thêm pháo điện từ chỉ riêng với boss này."),
            ["guide.tiers.shift"] = ("Changing altitude takes about 3-4 s; while it does, it is hit as at the lower of the two tiers.", "Đổi tầng mất khoảng 3-4 giây; trong lúc đó nó bị bắn theo tầng thấp hơn trong hai tầng."),
            ["guide.tiers.phase1"] = ("Phase 1 (100-70 %): about {high} s high, then {low} s low.", "Pha 1 (100-70 %): khoảng {high} giây ở tầng cao, rồi {low} giây ở tầng thấp."),
            ["guide.tiers.phase2"] = ("Phase 2 (70-30 %): {high} s high, then {low} s low, where it stops to charge: your main chance.", "Pha 2 (70-30 %): {high} giây ở tầng cao, rồi {low} giây ở tầng thấp, nơi nó dừng lại nạp năng lượng: cơ hội chính của bạn."),
            ["guide.tiers.pods"] = ("Drop pods: shoot them down while they fall (low tier, about 400 health) and the vehicles inside never land. At most six of its landed vehicles are alive at once.", "Khoang đổ bộ: bắn hạ trong lúc đang rơi (tầng thấp, khoảng 400 máu) thì xe bên trong không xuống được. Tối đa sáu xe đổ bộ của nó còn sống cùng lúc."),
            ["guide.tiers.crash"] = ("Below 30 % its engine fails: it crashes at a set point mid-map and fights on as a ground fortress with guns all round. Its satellite uplink can still call down rods.", "Dưới 30 % máu, động cơ của nó hỏng: nó rơi xuống một điểm định sẵn giữa bản đồ và trở thành pháo đài mặt đất với súng quay ra mọi hướng. Ăng-ten liên kết vệ tinh vẫn có thể gọi thanh vonfram."),
            ["guide.tiers.armour"] = ("Upper hull armour is level 4, its belly level 2, its engines 1-2. At low altitude its belly faces you.", "Giáp thân trên cấp 4, giáp bụng cấp 2, động cơ cấp 1-2. Ở tầng thấp, bụng nó quay ra hướng bạn."),
            ["guide.tiers.hijack"] = ("Very Hard only, phase 3: it seizes your drones for a few seconds. Drones in reach of your jamming vehicles and EW towers are safe.", "Chỉ độ khó Cực khó, pha 3: nó chiếm quyền điều khiển drone của bạn trong vài giây. Drone trong tầm xe gây nhiễu và tháp EW của bạn thì an toàn."),
            ["guide.tiers.nohigh"] = ("No long-range anti-air? Fight it at low altitude, shoot down its pods, and finish it once it is on the ground.", "Không có phòng không tầm xa? Hãy đánh nó ở tầng thấp, bắn hạ khoang đổ bộ, và kết liễu khi nó đã rơi xuống đất."),

            // ---------------------------------------------------------------- radio (second word is the speaker)
            ["radio.aurel.bug.appear"] = ("Icarus is in orbit, Colonel. Look up.", "Icarus đã vào quỹ đạo, đại tá. Ngẩng đầu lên mà xem."),
            ["radio.aurel.bug.descend"] = ("Coming down to greet you personally. The satellite stays up there — insurance.", "Tôi đang hạ xuống để chào ông tận nơi. Vệ tinh ở lại trên đó — của để dành."),
            ["radio.aurel.bug.phase2"] = ("You have scratched the paintwork, Colonel. I will need more than that.", "Ông mới chỉ làm xước lớp sơn thôi, đại tá. Cần nhiều hơn thế."),
            ["radio.aurel.bug.phase3"] = ("My engine. That is not in the forecast either.", "Động cơ của tôi. Cũng không có trong dự báo."),
            ["radio.aurel.bug.crash"] = ("Brace, Colonel. I intend to land on someone's paperwork.", "Bám chắc vào, đại tá. Tôi định rơi thẳng xuống đống giấy tờ của ai đó."),
            ["radio.aurel.bug.down"] = ("Well. The forecast was wrong about you, Colonel.", "À. Dự báo đã sai về ông, đại tá."),
            ["radio.aurel.bug.hijack"] = ("Those drones are mine now, Colonel. Borrowed, with interest.", "Đám drone đó giờ là của tôi, đại tá. Mượn tạm, có lãi."),
            ["radio.hq.bug.hijack"] = ("Command: it is seizing our drones! Get them under jammer cover, now!", "Chỉ huy: nó đang chiếm quyền điều khiển drone của ta! Đưa chúng vào vùng che của xe gây nhiễu ngay!"),

            // ---------------------------------------------------------------- toasts
            ["toast.tier.descend"] = ("It is leaving orbit!", "Nó đang rời quỹ đạo!"),
            ["toast.tier.crash"] = ("It is coming down!", "Nó đang rơi xuống!"),
            ["toast.pods"] = ("Drop pods incoming: shoot them down!", "Khoang đổ bộ đang rơi: bắn hạ chúng!"),
            ["toast.hijack"] = ("Your drones are being seized!", "Drone của bạn đang bị chiếm quyền điều khiển!"),
            ["loading.toArena"] = ("Redeploying to its battlefield", "Chuyển tới chiến trường của nó"),
        };
    }
}
