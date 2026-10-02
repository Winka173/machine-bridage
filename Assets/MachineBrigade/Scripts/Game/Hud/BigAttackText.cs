using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 18: the words of the bosses' big attacks (prompt 25 C1: the twelve main bosses' super weapons; a mini boss has none), by the keys their ids give (BigAttackDef): each attack's
    /// name, the short notice when it is cancelled, its radio line (the boss's general where it has one; prompt 23
    /// turns these into one subtitle line), and its Guide lines (how it works, how to get out of it, how to stop
    /// it); who each is for; the boss bar's tooltip; the new parts. Nothing to show is in the data or the sim.
    /// </summary>
    public static class BigAttackText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- general
            ["guide.bigattack"] = ("Super weapon", "Siêu vũ khí"),
            ["guide.bigattack.rule"] = ("A main boss's one super weapon, telegraphed (a mini boss has none): its zone lights up with a countdown and the part that fires it glows on the boss bar. Break that part during the warning to cancel it; your units in the zone get out on their own if they can make it in time.",
                "Siêu vũ khí của boss chủ lực, có cảnh báo (mini boss không có): vùng trúng sáng lên kèm đếm ngược và bộ phận phóng đòn nhấp nháy trên thanh máu boss. Phá bộ phận đó trong lúc cảnh báo để hủy đòn; quân ta trong vùng tự chạy ra nếu kịp."),
            ["guide.bigattack.stats"] = ("{hits} · warning {warning} s · every {seconds} s", "{hits} · cảnh báo {warning} giây · hồi {seconds} giây"),
            ["guide.bigattack.hits"] = ("{count} × {damage} {type}, penetration {level}", "{count} × {damage} {type}, xuyên cấp {level}"),
            ["guide.bigattack.late"] = ("phase {phase}: {count} rounds, every {seconds} s", "pha {phase}: {count} phát, hồi {seconds} giây"),
            ["guide.bigattack.drop"] = ("{count|# vehicle|# vehicles} landed", "{count} xe đổ bộ"),
            ["guide.bigattack.buff"] = ("+{percent}% damage and +{percent2}% fire rate for {seconds} s within {metres} m", "+{percent}% sát thương và +{percent2}% tốc độ bắn trong {seconds} giây, bán kính {metres} m"),
            ["guide.bigattack.how"] = ("How it works", "Cách hoạt động"),
            ["guide.bigattack.dodge"] = ("Getting out of it", "Cách né"),
            ["guide.bigattack.stop"] = ("Stopping it", "Cách ngắt"),
            ["guide.bigattack.target"] = ("Meant for", "Mục tiêu chính"),
            ["guide.bigattack.target.light"] = ("vehicles with no to medium armour, and towers", "xe giáp không có tới vừa, và tháp"),
            ["guide.bigattack.target.heavy"] = ("heavily armoured tanks", "xe tăng giáp dày"),
            ["guide.bigattack.target.mixed"] = ("mixed groups and towers", "cụm quân hỗn hợp và tháp"),
            ["guide.bigattack.target.base"] = ("your base: HQ, towers and the units in it", "căn cứ: HQ, tháp và quân trong căn cứ"),
            ["guide.bigattack.target.still"] = ("groups standing still, and towers", "cụm quân đứng yên và tháp"),
            ["guide.bigattack.target.thin"] = ("unarmoured and thin-skinned vehicles close to it", "xe không giáp và giáp mỏng đứng gần boss"),
            ["guide.bigattack.target.army"] = ("your whole army", "cả đội quân của bạn"),
            ["guide.bigattack.target.armour"] = ("tanks and armoured vehicles, through the roof", "xe tăng và xe có giáp, đánh vào nóc"),
            ["guide.bigattack.target.beach"] = ("the units holding the beach", "quân giữ bãi cát"),
            ["guide.bigattack.target.tanks"] = ("tanks", "xe tăng"),
            ["guide.bigattack.target.packed"] = ("tightly packed groups", "cụm quân đứng dồn"),
            ["guide.bigattack.target.defences"] = ("towers, gates, buildings and units moving in", "tháp, cổng, công trình và quân đang tiến vào"),
            ["hud.bigAttack"] = ("Its super weapon: the ring fills as it gets ready; lit, it is charging (break the flashing part!)",
                "Siêu vũ khí của boss: vòng đầy dần khi sắp sẵn sàng; sáng lên là đang nạp (phá bộ phận đang nhấp nháy!)"),
            ["part.erector"] = ("missile erector", "bệ phóng tên lửa"),
            ["part.bombbay"] = ("bomb bay", "khoang bom"),
            ["part.fx.bigattack"] = ("its super weapon goes with it", "boss mất siêu vũ khí"),
            ["radio.part.erector"] = ("Command: {boss}'s missile erector is wrecked. No more tactical missiles!", "Chỉ huy: bệ phóng tên lửa của {boss} đã bị phá. Hết tên lửa chiến thuật!"),
            ["radio.part.bombbay"] = ("Command: {boss}'s bomb bay is gone. It cannot bomb us any more!", "Chỉ huy: khoang bom của {boss} đã bị phá. Nó không thả bom được nữa!"),
            ["toast.bigattack.down"] = ("Shot down!", "Đã bắn hạ!"),

            // ---------------------------------------------------------------- prompt 25 C1 (DECISIONS 25C): the twelve main bosses' super weapons
            // ---------------------------------------------------------------- Behemoth
            ["bigattack.behemoth_barrage"] = ("Main Gun Barrage", "Loạt pháo chính dồn"),
            ["bigattack.behemoth_barrage.cancelled"] = ("Barrage cancelled", "Đã hủy loạt pháo chính"),
            ["radio.bigattack.behemoth_barrage"] = ("Command: the Behemoth's main gun is ranging on you. Clear the circle!", "Chỉ huy: pháo chính của Behemoth đang ngắm vào ta. Ra khỏi vòng tròn!"),
            ["guide.bigattack.behemoth_barrage.how"] = ("Three pairs of 152 mm high-explosive shells, 600 each, over a 14 m circle: each lands in its own red ring (8.5 m core at full damage, 17 m edge at 40%), drawn 3.5 s ahead. Every 45 s.", "Ba loạt, mỗi loạt hai quả 152 mm nổ mạnh, mỗi quả 600, rải trong vòng tròn bán kính 14 m: mỗi quả rơi vào vòng đỏ riêng (lõi 8,5 m đủ sát thương, rìa 17 m còn 40%), vạch trước 3,5 giây. Cứ 45 giây."),
            ["guide.bigattack.behemoth_barrage.dodge"] = ("Step out of the six rings: each blast reaches 8 m.", "Bước ra khỏi sáu vòng tròn: mỗi vụ nổ lan 8 m."),
            ["guide.bigattack.behemoth_barrage.stop"] = ("Break the main gun during the warning.", "Phá pháo chính trong lúc cảnh báo."),

            // ---------------------------------------------------------------- Nemesis
            ["bigattack.doomsday_missile"] = ("Doomsday Missile", "Tên lửa Tận thế"),
            ["bigattack.doomsday_missile.cancelled"] = ("Missile launch cancelled", "Đã hủy phóng tên lửa"),
            ["radio.bigattack.doomsday_missile"] = ("Command: Nemesis is raising a missile! Break the erector or get your air defence ready!", "Chỉ huy: Nemesis đang dựng tên lửa! Phá bệ phóng hoặc sẵn sàng phòng không!"),
            ["guide.bigattack.doomsday_missile.how"] = ("Four seconds to raise it, then a thermobaric missile at your HQ or your biggest group, a flight clock on it (6 s, longer from far off): 3,500 in the 18 m core, 40% out to 20 m, much more on buildings. Every 50 s.", "Bốn giây dựng bệ phóng, rồi một tên lửa nhiệt áp bay vào HQ hoặc cụm quân lớn nhất, có đồng hồ bay (6 giây, xa hơn thì lâu hơn): 3.500 trong lõi 18 m, còn 40% tới rìa 20 m, mạnh hơn nhiều lên công trình. Cứ 50 giây một lần."),
            ["guide.bigattack.doomsday_missile.dodge"] = ("Scatter your units away from the marked landing point before the clock runs out.", "Dàn quân ra khỏi điểm rơi được đánh dấu trước khi hết giờ."),
            ["guide.bigattack.doomsday_missile.stop"] = ("Break the erector while it rises, or shoot the missile down in flight (600 health): PAC-3 and Iron Dome batteries, and any anti-air, C-RAM or point-defence laser under it.", "Phá bệ phóng trong lúc dựng, hoặc bắn hạ tên lửa trên đường bay (máu 600): khẩu đội PAC-3 và Vòm Sắt, cùng mọi phòng không, C-RAM hay la-de PK bên dưới."),

            // ---------------------------------------------------------------- Jötunn
            ["bigattack.fortress_203_barrage"] = ("203 mm Barrage", "Loạt pháo 203 mm"),
            ["bigattack.fortress_203_barrage.cancelled"] = ("203 mm barrage cancelled", "Đã hủy loạt pháo 203 mm"),
            ["radio.bigattack.fortress_203_barrage"] = ("Command: Jötunn is laying both 203 mm howitzers on you. Clear the circle!", "Chỉ huy: Jötunn đang ngắm cả hai lựu pháo 203 mm vào ta. Ra khỏi vòng tròn!"),
            ["guide.bigattack.fortress_203_barrage.how"] = ("Four 203 mm shells, 900 each (10 m core, 20 m edge at 40%), over a 14 m circle, two from each howitzer; 4 s of warning. Every 50 s.", "Bốn quả 203 mm, mỗi quả 900 (lõi 10 m, rìa 20 m còn 40%), rải trong vòng tròn bán kính 14 m, mỗi lựu pháo hai quả; cảnh báo 4 giây. Cứ 50 giây."),
            ["guide.bigattack.fortress_203_barrage.dodge"] = ("Leave the circle, or sit it out under a shield dome: shields take the blasts.", "Rời khỏi vòng, hoặc núp dưới vòm khiên: khiên hấp thụ được."),
            ["guide.bigattack.fortress_203_barrage.stop"] = ("Break a howitzer: each brings two of the four shells.", "Phá một lựu pháo: mỗi khẩu góp hai trong bốn quả."),

            // ---------------------------------------------------------------- Icarus (prompt 19: tungsten rods from orbit)
            ["bigattack.bug_rod_rain"] = ("Tungsten Rod Rain", "Mưa thanh vonfram"),
            ["bigattack.bug_rod_rain.cancelled"] = ("Rod rain cancelled", "Đã hủy mưa thanh vonfram"),
            ["radio.bigattack.bug_rod_rain"] = ("Command: rods incoming from its satellite. Get out of the rings!", "Chỉ huy: thanh vonfram đang rơi từ vệ tinh của nó. Ra khỏi các vòng tròn ngay!"),
            ["guide.bigattack.bug_rod_rain.how"] = ("Seven tungsten rods drop on your groups, heavy tanks first, from the satellite it leaves in orbit: 1,800 kinetic each, very high penetration, 7 m radius, with 4 s of light columns first; every 45 s. Crashed, in phase 3: nine.", "Bảy thanh vonfram rơi xuống các cụm quân, ưu tiên xe tăng giáp dày, từ vệ tinh nó để lại trên quỹ đạo: 1.800 động năng mỗi thanh, xuyên rất cao, bán kính 7 m, có 4 giây cột sáng cảnh báo; cứ 45 giây. Khi đã rơi xuống, ở pha 3: chín thanh."),
            ["guide.bigattack.bug_rod_rain.dodge"] = ("Get out of the rings; smoke and APS do not stop them. Shield domes absorb part of the hit while they hold.", "Ra khỏi các vòng tròn; khói và APS không chặn được. Vòm khiên hấp thụ một phần sát thương trong lúc còn hoạt động."),
            ["guide.bigattack.bug_rod_rain.stop"] = ("Break the satellite uplink during the warning to cancel that rod; break it for good and no more rods fall until a self-repair puts it back. It can be hit at high or low altitude, and on the ground.", "Phá ăng-ten liên kết vệ tinh trong lúc cảnh báo để hủy thanh đang rơi; phá hẳn thì hết mưa thanh vonfram cho tới khi nó tự vá lại. Ăng-ten bắn được ở tầng cao, tầng thấp, và cả khi đã rơi xuống đất."),

            // ---------------------------------------------------------------- Ixion (prompt 26 D.1: its crush charge, a secondary weapon, not a super weapon)
            ["bigattack.ixion_crush_charge"] = ("Crush Charge", "Lao nghiền"),
            ["bigattack.ixion_crush_charge.cancelled"] = ("Charge stopped", "Đã chặn cú lao"),
            ["radio.bigattack.ixion_crush_charge"] = ("Command: Ixion is lining up its ram. Clear the line!", "Chỉ huy: Ixion đang ngắm đường lao. Ra khỏi đường thẳng!"),
            ["guide.bigattack.ixion_crush_charge.how"] = ("The mine truck charges down a line shown 2 s ahead: about 900 to every vehicle on it (less with armour) and a 1 s stun; its turret keeps firing. About every 10 s.", "Xe tải mỏ lao theo một đường thẳng báo trước 2 giây: khoảng 900 lên mọi xe trên đường (giảm theo giáp) và choáng 1 giây; tháp pháo vẫn bắn. Cứ khoảng 10 giây."),
            ["guide.bigattack.ixion_crush_charge.dodge"] = ("Step off the line to the side before the warning ends.", "Bước ngang ra khỏi đường thẳng trước khi hết cảnh báo."),
            ["guide.bigattack.ixion_crush_charge.stop"] = ("Break a front tyre: the charge swerves and stops.", "Phá một lốp trước: cú lao lệch và dừng."),

            // ---------------------------------------------------------------- Bastion
            ["bigattack.bastion_420_shell"] = ("420 mm Mortar", "Pháo cối 420 mm"),
            ["bigattack.bastion_420_shell.cancelled"] = ("420 mm shell cancelled", "Đã hủy phát cối 420 mm"),
            ["radio.bigattack.bastion_420_shell"] = ("Command: the Bastion is loading its heavy mortar. Get out of the red ring!", "Chỉ huy: Bastion đang nạp khẩu cối hạng nặng. Ra khỏi vòng đỏ!"),
            ["guide.bigattack.bastion_420_shell.how"] = ("One 420 mm mortar bomb: 2,000 in the 10 m core, 40% out to 20 m, twice as hard on buildings and towers; a red ring 4 s ahead. Every 45 s.", "Một quả cối 420 mm: 2.000 trong lõi 10 m, còn 40% tới rìa 20 m, gấp đôi lên công trình và tháp; vòng đỏ báo trước 4 giây. Cứ 45 giây."),
            ["guide.bigattack.bastion_420_shell.dodge"] = ("Leave the red ring, or keep your units under a shield generator's dome: it absorbs the blast.", "Ra khỏi vòng đỏ, hoặc giữ quân dưới vòm của máy phát khiên: vòm hấp thụ được vụ nổ."),
            ["guide.bigattack.bastion_420_shell.stop"] = ("Break the mortar: the attack goes with it (until its one self-repair).", "Phá khẩu cối: mất luôn đòn này (tới lần tự vá duy nhất của nó)."),

            // ---------------------------------------------------------------- Matriarch
            ["bigattack.carrier_heavy_bomb"] = ("Heavy Glide Bomb", "Bom trượt hạng nặng"),
            ["bigattack.carrier_heavy_bomb.cancelled"] = ("Glide bomb cancelled", "Đã hủy bom trượt"),
            ["radio.bigattack.carrier_heavy_bomb"] = ("Command: the carrier has stopped overhead with its bomb bay open. Hit it now!", "Chỉ huy: tàu mẹ dừng ngay trên đầu, khoang bom đã mở. Đánh nó ngay!"),
            ["guide.bigattack.carrier_heavy_bomb.how"] = ("One heavy glide bomb from its bay: 1,600 in the 16 m core, 40% out to 20 m, twice as hard on buildings and towers; it glides slowly to the ring, 3 s at least. Every 45 s.", "Một quả bom trượt hạng nặng từ khoang bom: 1.600 trong lõi 16 m, còn 40% tới rìa 20 m, gấp đôi lên công trình và tháp; bom lượn chậm tới vòng đánh dấu, ít nhất 3 giây. Cứ 45 giây."),
            ["guide.bigattack.carrier_heavy_bomb.dodge"] = ("Move out of the ring; while its bay is open your anti-air hits the carrier 30% harder.", "Chạy ra khỏi vòng; khi khoang bom mở, phòng không trúng tàu mẹ mạnh hơn 30%."),
            ["guide.bigattack.carrier_heavy_bomb.stop"] = ("Break the bomb bay, or shoot the bomb down as it glides (250 health): anti-air, C-RAM, point-defence lasers.", "Phá khoang bom, hoặc bắn hạ quả bom khi nó lượn (máu 250): phòng không, C-RAM, la-de PK."),

            // ---------------------------------------------------------------- Roc
            ["bigattack.airship_carpet"] = ("Carpet Bombing", "Rải thảm"),
            ["bigattack.airship_carpet.cancelled"] = ("Carpet bombing cancelled", "Đã hủy rải thảm"),
            ["radio.bigattack.airship_carpet"] = ("Wolff: \"Bomb doors open. Sixteen for the ground below.\"", "Wolff: \"Mở khoang bom. Mười sáu quả cho mặt đất bên dưới.\""),
            ["guide.bigattack.airship_carpet.how"] = ("Sixteen 250 kg bombs, 400 each (7 m core, 14 m edge at 40%), in an 80 × 12 m strip along its course; 4 s of warning. Every 50 s.", "Mười sáu quả bom 250 kg, mỗi quả 400 (lõi 7 m, rìa 14 m còn 40%), thành dải 80 × 12 m theo đường bay; cảnh báo 4 giây. Cứ 50 giây."),
            ["guide.bigattack.airship_carpet.dodge"] = ("Step off the strip sideways, out from under its course.", "Bước ngang ra khỏi dải, tránh khỏi đường bay của nó."),
            ["guide.bigattack.airship_carpet.stop"] = ("Break the bomb bay.", "Phá khoang bom."),

            // ---------------------------------------------------------------- Leviathan
            ["bigattack.leviathan_volley"] = ("Nine-Gun Broadside", "Loạt bắn mạn chín nòng"),
            ["bigattack.leviathan_volley.cancelled"] = ("Broadside cancelled", "Đã hủy loạt bắn mạn"),
            ["radio.bigattack.leviathan_volley"] = ("Kessler: \"All turrets, train on their headquarters. Full broadside.\"", "Kessler: \"Mọi tháp pháo, quay về sở chỉ huy của chúng. Bắn cả mạn.\""),
            ["guide.bigattack.leviathan_volley.how"] = ("Nine 406 mm shells, 950 each (12 m core, 20 m edge at 40%), from its three main turrets along a 60 × 12 m strip through your base, a third harder on buildings; 4 s of warning. Every 50 s.", "Chín quả đạn 406 mm, mỗi quả 950 (lõi 12 m, rìa 20 m còn 40%), từ ba tháp pháo chính rải theo dải 60 × 12 m qua căn cứ, mạnh hơn một phần ba lên công trình; cảnh báo 4 giây. Cứ 50 giây."),
            ["guide.bigattack.leviathan_volley.dodge"] = ("Move units out of the marked strip; shells cannot be shot down, so spread out.", "Đưa quân ra khỏi dải đánh dấu; đạn pháo không bắn hạ được, nên hãy dàn quân ra."),
            ["guide.bigattack.leviathan_volley.stop"] = ("Break a main turret during the warning (armour 4: tank hunters, artillery, bombs): each one broken takes its three shells away.", "Phá một tháp pháo chính trong lúc cảnh báo (giáp cấp 4: xe diệt tăng, pháo binh, bom): mỗi tháp bị phá bớt ba quả đạn."),

            // Prompt 25 F2 batch D: the four new main bosses' super weapons.
            ["bigattack.kraken_air_raid"] = ("Air Raid", "Đợt không kích"),
            ["bigattack.kraken_air_raid.cancelled"] = ("Air raid cancelled", "Đã hủy đợt không kích"),
            ["radio.bigattack.kraken_air_raid"] = ("Kessler: \"Deck crews, clear the bombers. Twelve for the shore.\"", "Kessler: \"Đội boong, thả máy bay ném bom. Mười hai quả cho bờ biển.\""),
            ["guide.bigattack.kraken_air_raid.how"] = ("Twelve bombs, 400 each (9 m core, 18 m edge at 40%), in a 90 × 14 m strip along its heading; 4 s of warning. Every 50 s.", "Mười hai quả bom, mỗi quả 400 (lõi 9 m, rìa 18 m còn 40%), thành dải 90 × 14 m theo hướng tàu; cảnh báo 4 giây. Mỗi 50 giây."),
            ["guide.bigattack.kraken_air_raid.dodge"] = ("Step out of the red strip sideways.", "Bước ngang ra khỏi dải đỏ."),
            ["guide.bigattack.kraken_air_raid.stop"] = ("Break the flight deck during the warning: the raid and the aircraft stop.", "Phá boong cất cánh trong lúc cảnh báo: đợt không kích và máy bay đều dừng."),
            ["bigattack.monster_800_shell"] = ("800 mm Shell", "Đạn 800 mm"),
            ["bigattack.monster_800_shell.cancelled"] = ("800 mm shell cancelled", "Đã hủy phát đạn 800 mm"),
            ["radio.bigattack.monster_800_shell"] = ("Orlov: \"Elevate the barrel. One round.\"", "Orlov: \"Nâng nòng. Một phát.\""),
            ["guide.bigattack.monster_800_shell.how"] = ("One 800 mm shell: 4,000 in the 20 m core, 40% out to 20 m, twice as hard on buildings; the barrel rises slowly, a red ring shows for 4 s. Every 50 s.", "Một quả đạn 800 mm: 4.000 trong lõi 20 m, còn 40% tới rìa 20 m, nặng gấp đôi với công trình; nòng nâng từ từ, vòng đỏ hiện 4 giây. Mỗi 50 giây."),
            ["guide.bigattack.monster_800_shell.dodge"] = ("Leave the red ring; it is wide, so go early.", "Ra khỏi vòng đỏ; vòng rất rộng nên đi sớm."),
            ["guide.bigattack.monster_800_shell.stop"] = ("Break the mortar (the barrel): the shell goes with it.", "Phá khẩu cối (nòng): mất luôn phát đạn."),
            ["bigattack.garuda_carpet"] = ("Carpet Run", "Rải thảm"),
            ["bigattack.garuda_carpet.cancelled"] = ("Carpet run cancelled", "Đã hủy lượt rải thảm"),
            ["radio.bigattack.garuda_carpet"] = ("Raven: \"Bay open. Twenty down the line.\"", "Raven: \"Mở khoang. Hai mươi quả dọc đường bay.\""),
            ["guide.bigattack.garuda_carpet.how"] = ("Twenty bombs, 350 each (7 m core, 14 m edge at 40%), in a 100 × 14 m strip along its course; 4 s of warning. Every 50 s.", "Hai mươi quả bom, mỗi quả 350 (lõi 7 m, rìa 14 m còn 40%), thành dải 100 × 14 m theo đường bay; cảnh báo 4 giây. Mỗi 50 giây."),
            ["guide.bigattack.garuda_carpet.dodge"] = ("Step off the strip sideways.", "Bước ngang ra khỏi dải."),
            ["guide.bigattack.garuda_carpet.stop"] = ("Break the bomb bay.", "Phá khoang bom."),
            ["bigattack.hyperion_sun_beam"] = ("Sun Beam", "Tia mặt trời"),
            ["bigattack.hyperion_sun_beam.cancelled"] = ("Sun beam cancelled", "Đã hủy tia mặt trời"),
            ["radio.bigattack.hyperion_sun_beam"] = ("Aurel: \"Mirrors aligned. Hold still, it will be over quickly.\"", "Aurel: \"Gương đã thẳng hàng. Đứng yên, sẽ nhanh thôi.\""),
            ["guide.bigattack.hyperion_sun_beam.how"] = ("A beam burns a 70 × 6 m strip for 4 s, 500 a second; 4 s of warning. Every 50 s.", "Một tia đốt dải 70 × 6 m trong 4 giây, 500 mỗi giây; cảnh báo 4 giây. Mỗi 50 giây."),
            ["guide.bigattack.hyperion_sun_beam.dodge"] = ("Leave the narrow strip at once.", "Rời ngay dải hẹp."),
            ["guide.bigattack.hyperion_sun_beam.stop"] = ("Break the main laser during the warning.", "Phá tia la-de chính trong lúc cảnh báo."),
        };
    }
}
