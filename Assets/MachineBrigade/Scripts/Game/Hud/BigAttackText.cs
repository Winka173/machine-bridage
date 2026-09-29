using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 18: the words of the bosses' big attacks, by the keys their ids give (BigAttackDef): each attack's
    /// name, the short notice when it is cancelled, its radio line (the boss's general where it has one; prompt 23
    /// turns these into one subtitle line), and its Guide lines (how it works, how to get out of it, how to stop
    /// it); who each is for; the boss bar's tooltip; the new parts. Nothing to show is in the data or the sim.
    /// </summary>
    public static class BigAttackText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- general
            ["guide.bigattack"] = ("Big attack", "Đòn lớn"),
            ["guide.bigattack.rule"] = ("One big attack, telegraphed: its zone lights up with a countdown and the part that fires it glows on the boss bar. Break that part during the warning to cancel it; your units in the zone get out on their own if they can make it in time.",
                "Một đòn lớn có cảnh báo: vùng trúng sáng lên kèm đếm ngược và bộ phận phóng đòn nhấp nháy trên thanh máu boss. Phá bộ phận đó trong lúc cảnh báo để hủy đòn; quân ta trong vùng tự chạy ra nếu kịp."),
            ["guide.bigattack.stats"] = ("{hits} · warning {warning} s · every {seconds} s", "{hits} · cảnh báo {warning} giây · hồi {seconds} giây"),
            ["guide.bigattack.hits"] = ("{count} × {damage} {type}, penetration {level}", "{count} × {damage} {type}, xuyên cấp {level}"),
            ["guide.bigattack.drop"] = ("{count|# vehicle|# vehicles} landed", "{count} xe đổ bộ"),
            ["guide.bigattack.buff"] = ("+{percent} % damage and +{percent2} % fire rate for {seconds} s within {metres} m", "+{percent} % sát thương và +{percent2} % tốc độ bắn trong {seconds} giây, bán kính {metres} m"),
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
            ["hud.bigAttack"] = ("Its big attack: the ring fills as it gets ready; lit, it is charging (break the flashing part!)",
                "Đòn lớn của boss: vòng đầy dần khi sắp sẵn sàng; sáng lên là đang nạp (phá bộ phận đang nhấp nháy!)"),
            ["part.erector"] = ("missile erector", "bệ phóng tên lửa"),
            ["part.bombbay"] = ("bomb bay", "khoang bom"),
            ["part.fx.bigattack"] = ("its big attack goes with it", "boss mất đòn lớn"),
            ["radio.part.erector"] = ("Command: {boss}'s missile erector is wrecked. No more tactical missiles!", "Chỉ huy: bệ phóng tên lửa của {boss} đã bị phá. Hết tên lửa chiến thuật!"),
            ["radio.part.bombbay"] = ("Command: {boss}'s bomb bay is gone. It cannot bomb us any more!", "Chỉ huy: khoang bom của {boss} đã bị phá. Nó không thả bom được nữa!"),
            ["toast.bigattack.down"] = ("Shot down!", "Đã bắn hạ!"),

            // ---------------------------------------------------------------- 1 Iron Train
            ["bigattack.train_broadside"] = ("Full-Train Broadside", "Loạt pháo toàn đoàn"),
            ["bigattack.train_broadside.cancelled"] = ("Broadside cancelled", "Đã hủy loạt pháo"),
            ["radio.bigattack.train_broadside"] = ("Command: Juggernaut is laying both gun cars on you. Get off the marked strip!", "Chỉ huy: Juggernaut đang dồn cả hai toa pháo vào ta. Ra khỏi dải đánh dấu!"),
            ["guide.bigattack.train_broadside.how"] = ("Both gun cars fire six 152 mm HE shells into a 60 × 12 m strip along the rails.", "Hai toa pháo bắn sáu quả 152 mm nổ mạnh xuống một dải 60 × 12 m dọc đường ray."),
            ["guide.bigattack.train_broadside.dodge"] = ("Step off the strip sideways: it is only 12 m wide.", "Bước ngang ra khỏi dải: nó chỉ rộng 12 m."),
            ["guide.bigattack.train_broadside.stop"] = ("Break a gun car: each brings three of the six shells.", "Phá toa pháo: mỗi toa góp ba trong sáu phát."),

            // ---------------------------------------------------------------- 2 Tempest
            ["bigattack.tempest_rail"] = ("Full-Charge Railgun Shot", "Phát pháo điện từ nạp đầy"),
            ["bigattack.tempest_rail.cancelled"] = ("Railgun shot cancelled", "Đã hủy phát pháo điện từ"),
            ["radio.bigattack.tempest_rail"] = ("Command: the Tempest's coils are charging. Get off the red line!", "Chỉ huy: cuộn dây của Tempest đang nạp. Ra khỏi tia ngắm đỏ!"),
            ["guide.bigattack.tempest_rail.how"] = ("One slug through everything on a 90 m line; each vehicle behind takes 15 % less than the one before. Smoke does not stop it.", "Một viên đạn xuyên qua mọi thứ trên đường thẳng 90 m; mỗi xe phía sau nhận ít hơn 15 % so với xe trước. Khói không chặn được."),
            ["guide.bigattack.tempest_rail.dodge"] = ("Move off the red aiming line, it is only 3 m wide; do not line up behind each other.", "Rời khỏi tia ngắm đỏ, nó chỉ rộng 3 m; đừng xếp hàng nối đuôi nhau."),
            ["guide.bigattack.tempest_rail.stop"] = ("Break the railgun during the charge; an EMP delays the shot by 2 s.", "Phá pháo điện từ trong lúc nạp; EMP làm chậm thêm 2 giây."),

            // ---------------------------------------------------------------- 3 Behemoth
            ["bigattack.behemoth_barrage"] = ("Main Gun Barrage", "Loạt pháo chính"),
            ["bigattack.behemoth_barrage.cancelled"] = ("Barrage cancelled", "Đã hủy loạt pháo chính"),
            ["radio.bigattack.behemoth_barrage"] = ("Command: the Behemoth's main gun is ranging on you. Clear the circle!", "Chỉ huy: pháo chính của Behemoth đang ngắm vào ta. Ra khỏi vòng tròn!"),
            ["guide.bigattack.behemoth_barrage.how"] = ("Three pairs of 203 mm HE shells scattered over a 14 m circle.", "Ba loạt, mỗi loạt hai quả 203 mm nổ mạnh, rải trong vòng tròn bán kính 14 m."),
            ["guide.bigattack.behemoth_barrage.dodge"] = ("Spread out and leave the circle: the blasts reach 8 m past where they land.", "Dàn quân và rời vòng tròn: vụ nổ lan 8 m quanh chỗ rơi."),
            ["guide.bigattack.behemoth_barrage.stop"] = ("Break the main gun.", "Phá pháo chính."),

            // ---------------------------------------------------------------- 4 Doomsday Train
            ["bigattack.doomsday_missile"] = ("Tactical Missile", "Tên lửa chiến thuật"),
            ["bigattack.doomsday_missile.cancelled"] = ("Missile launch cancelled", "Đã hủy phóng tên lửa"),
            ["radio.bigattack.doomsday_missile"] = ("Command: Nemesis is raising a missile! Break the erector or get your air defence ready!", "Chỉ huy: Nemesis đang dựng tên lửa! Phá bệ phóng hoặc sẵn sàng phòng không!"),
            ["guide.bigattack.doomsday_missile.how"] = ("Five seconds to raise it, then a slow thermobaric missile flies about 12 s at your HQ or your biggest group: 2 500 at the centre, 30 % at 18 m, much more on buildings.", "Năm giây dựng bệ phóng, rồi một tên lửa nhiệt áp bay chậm khoảng 12 giây vào HQ hoặc cụm quân lớn nhất: 2.500 ở tâm, 30 % ở rìa 18 m, mạnh hơn nhiều lên công trình."),
            ["guide.bigattack.doomsday_missile.dodge"] = ("Scatter your units away from the marked landing point before the clock runs out.", "Dàn quân ra khỏi điểm rơi được đánh dấu trước khi hết giờ."),
            ["guide.bigattack.doomsday_missile.stop"] = ("Break the erector while it rises, or shoot the missile down in flight (600 health): anti-air, C-RAM, point-defence lasers.", "Phá bệ phóng trong 5 giây dựng bệ, hoặc bắn hạ tên lửa trên đường bay (máu 600): phòng không, C-RAM, La-de PK."),

            // ---------------------------------------------------------------- 5 Rail Supergun
            ["bigattack.supergun_heavy"] = ("Super-Heavy Shell", "Phát đạn siêu nặng"),
            ["bigattack.supergun_heavy.cancelled"] = ("Super-heavy shell cancelled", "Đã hủy phát đạn siêu nặng"),
            ["radio.bigattack.supergun_heavy"] = ("Kessler: \"Stand still for me. One shell will do.\"", "Kessler: \"Đứng yên đó. Một phát là đủ.\""),
            ["guide.bigattack.supergun_heavy.how"] = ("One super-heavy shell anywhere on the map: 1 800 at the centre, falling off to 20 m, and the ground burns for 8 s. Its ordinary shots go on.", "Một phát đạn siêu nặng tới bất cứ đâu trên bản đồ: 1.800 ở tâm, giảm dần tới 20 m, mặt đất cháy 8 giây. Các phát bắn thường vẫn tiếp tục."),
            ["guide.bigattack.supergun_heavy.dodge"] = ("It picks groups standing still: keep moving and leave the ring.", "Nó nhắm vào cụm quân đứng yên: tiếp tục di chuyển và rời khỏi vòng."),
            ["guide.bigattack.supergun_heavy.stop"] = ("Break the fire-control post: the shell then lands up to 15 m off (the ring grows to match). Breaking the gun ends it.", "Phá trạm chỉ thị mục tiêu: phát bắn lệch tới 15 m (vòng cảnh báo rộng ra tương ứng). Phá khẩu pháo thì mất hẳn đòn."),

            // ---------------------------------------------------------------- 6 Inferno
            ["bigattack.inferno_firestorm"] = ("Sea of Fire", "Biển lửa"),
            ["bigattack.inferno_firestorm.cancelled"] = ("Sea of fire cancelled", "Đã hủy biển lửa"),
            ["radio.bigattack.inferno_firestorm"] = ("Command: the Inferno is about to set everything round it alight. Get back 18 m!", "Chỉ huy: Inferno sắp đốt cháy mọi thứ quanh nó. Lùi ra 18 m!"),
            ["guide.bigattack.inferno_firestorm.how"] = ("Both flamethrowers flood an 18 m ring round it: a burst of fire and the ground burning for 10 s.", "Hai súng phun lửa phủ kín vòng 18 m quanh boss: một đợt lửa và mặt đất cháy 10 giây."),
            ["guide.bigattack.inferno_firestorm.dodge"] = ("Fight it from beyond 18 m; do not drive back in while the ground burns.", "Đánh từ ngoài 18 m; đừng quay lại khi mặt đất còn cháy."),
            ["guide.bigattack.inferno_firestorm.stop"] = ("Break a flamethrower: each covers one half of the ring.", "Phá súng phun lửa: mỗi súng phụ trách một nửa vòng."),

            // ---------------------------------------------------------------- 7 Supreme Commander
            ["bigattack.supreme_offensive"] = ("General Offensive", "Tổng tiến công"),
            ["bigattack.supreme_offensive.cancelled"] = ("Offensive cancelled", "Đã hủy tổng tiến công"),
            ["radio.bigattack.supreme_offensive"] = ("{@lyhan}: \"All units, general offensive! And bring the bombers in!\"", "{@lyhan}: \"Toàn quân, tổng tiến công! Gọi máy bay ném bom vào!\""),
            ["guide.bigattack.supreme_offensive.how"] = ("For 12 s every enemy within 60 m hits 35 % harder and fires 25 % faster, and a bomber lays eight 250 kg bombs in a 50 × 10 m strip on your biggest group.", "Trong 12 giây mọi quân địch trong 60 m gây thêm 35 % sát thương và bắn nhanh hơn 25 %, kèm máy bay ném tám quả bom 250 kg thành dải 50 × 10 m vào cụm quân lớn nhất."),
            ["guide.bigattack.supreme_offensive.dodge"] = ("Leave the strip; pull back from the boosted units until it wears off.", "Rời khỏi dải bom; lùi khỏi quân địch được tăng sức cho tới khi hết hiệu lực."),
            ["guide.bigattack.supreme_offensive.stop"] = ("Break the antenna: the offensive and its everyday aura go with it.", "Phá ăng-ten: mất cả tổng tiến công lẫn hào quang thường."),

            // ---------------------------------------------------------------- 8 Hive
            ["bigattack.hive_swarm"] = ("All-Out Swarm", "Bầy drone tổng lực"),
            ["bigattack.hive_swarm.cancelled"] = ("Swarm cancelled", "Đã hủy bầy drone"),
            ["radio.bigattack.hive_swarm"] = ("Command: the Hive's racks are opening. Twenty drones incoming: air defence up!", "Chỉ huy: giàn phóng của Hive đang mở nắp. Hai mươi drone sắp tới: bật phòng không!"),
            ["guide.bigattack.hive_swarm.how"] = ("Twenty kamikaze drones split between the tanks and armour of your biggest group, striking the roof.", "Hai mươi drone cảm tử chia nhau đánh vào nóc xe tăng và xe giáp của cụm quân lớn nhất."),
            ["guide.bigattack.hive_swarm.dodge"] = ("You cannot outrun them: bring APS, C-RAM, point-defence lasers, jammers and flak.", "Không thể chạy thoát: dùng APS, C-RAM, La-de PK, gây nhiễu và pháo phòng không."),
            ["guide.bigattack.hive_swarm.stop"] = ("Break a rack during the warning: each launches ten drones.", "Phá giàn phóng trong lúc cảnh báo: mỗi giàn mười drone."),

            // ---------------------------------------------------------------- 9 Landing Hovercraft
            ["bigattack.hover_assault"] = ("Mass Landing", "Đổ bộ ồ ạt"),
            ["bigattack.hover_assault.cancelled"] = ("Landing cancelled", "Đã hủy đổ bộ"),
            ["radio.bigattack.hover_assault"] = ("Kessler: \"Soften the beach, then put everything ashore.\"", "Kessler: \"Dọn bãi đi, rồi đổ bộ toàn bộ lên bờ.\""),
            ["guide.bigattack.hover_assault.how"] = ("24 rockets over a 40 × 20 m stretch of beach, then six vehicles off the ramp (at most six of them alive at once).", "24 rốc-két rải trên vùng bãi 40 × 20 m, rồi sáu xe đổ bộ từ cửa (tối đa sáu xe còn sống cùng lúc)."),
            ["guide.bigattack.hover_assault.dodge"] = ("Pull back off the marked beach and meet the landing party as it comes up.", "Lùi khỏi bãi được đánh dấu và đón đánh quân đổ bộ khi chúng lên bờ."),
            ["guide.bigattack.hover_assault.stop"] = ("Break the rocket launchers to stop the rockets; break the ramp to stop the landing.", "Phá dàn rốc-két thì mất phần rốc-két; phá cửa đổ bộ thì mất phần đổ bộ."),

            // ---------------------------------------------------------------- 10 Ice Fortress
            ["bigattack.fortress_rocket_rain"] = ("Rocket Rain", "Mưa rốc-két"),
            ["bigattack.fortress_rocket_rain.cancelled"] = ("Rocket rain cancelled", "Đã hủy mưa rốc-két"),
            ["radio.bigattack.fortress_rocket_rain"] = ("Command: Jötunn is loading both rocket boxes. Shields up, or clear the circle!", "Chỉ huy: Jötunn đang nạp cả hai hộp rốc-két. Bật khiên hoặc ra khỏi vòng!"),
            ["guide.bigattack.fortress_rocket_rain.how"] = ("32 rockets of 122 mm come down over 4 s in a 25 m circle.", "32 rốc-két 122 mm rơi trong 4 giây xuống vòng tròn bán kính 25 m."),
            ["guide.bigattack.fortress_rocket_rain.dodge"] = ("Leave the circle, or sit it out under a shield dome: shields take the blasts.", "Rời khỏi vòng, hoặc núp dưới vòm khiên: khiên hấp thụ được."),
            ["guide.bigattack.fortress_rocket_rain.stop"] = ("Break a rocket box: each holds 16 rockets.", "Phá hộp rốc-két: mỗi hộp 16 quả."),

            // ---------------------------------------------------------------- 11 Silver Bug (prompt 19: tungsten rods from orbit, replacing the old laser sweep)
            ["bigattack.bug_rod_rain"] = ("Tungsten Rod Rain", "Mưa thanh vonfram"),
            ["bigattack.bug_rod_rain.cancelled"] = ("Rod rain cancelled", "Đã hủy mưa thanh vonfram"),
            ["radio.bigattack.bug_rod_rain"] = ("Command: rods incoming from its satellite. Get out of the rings!", "Chỉ huy: thanh vonfram đang rơi từ vệ tinh của nó. Ra khỏi các vòng tròn ngay!"),
            ["guide.bigattack.bug_rod_rain.how"] = ("Five tungsten rods drop on your groups, heavy tanks first: 1,600 kinetic each, very high penetration, 6 m radius, with 4 s of light columns first. The first comes from the craft itself in the opening; every one after comes from the satellite it leaves in orbit. Every 60 s, in every phase and at every altitude.", "Năm thanh vonfram rơi xuống các cụm quân của bạn, ưu tiên xe tăng giáp dày: 1.600 động năng mỗi thanh, xuyên rất cao, bán kính 6 m, có 4 giây cột sáng cảnh báo trước. Thanh đầu tiên rơi từ chính phi thuyền trong đoạn mở màn; các thanh sau đều từ vệ tinh nó để lại trên quỹ đạo. Hồi chiêu 60 giây, dùng được ở mọi pha và mọi tầng độ cao."),
            ["guide.bigattack.bug_rod_rain.dodge"] = ("Get out of the rings; smoke and APS do not stop them. Shield domes absorb part of the hit while they hold.", "Ra khỏi các vòng tròn; khói và APS không chặn được. Vòm khiên hấp thụ một phần sát thương trong lúc còn hoạt động."),
            ["guide.bigattack.bug_rod_rain.stop"] = ("Break the satellite uplink during the warning to cancel that rod; break it for good and no more rods fall until a self-repair puts it back. It can be hit at high or low altitude, and on the ground.", "Phá ăng-ten liên kết vệ tinh trong lúc cảnh báo để hủy thanh đang rơi; phá hẳn thì hết mưa thanh vonfram cho tới khi nó tự vá lại. Ăng-ten bắn được ở tầng cao, tầng thấp, và cả khi đã rơi xuống đất."),

            // ---------------------------------------------------------------- 12 Earth Worm
            ["bigattack.borer_quake"] = ("Earthquake", "Địa chấn"),
            ["bigattack.borer_quake.cancelled"] = ("Earthquake cancelled", "Đã hủy địa chấn"),
            ["radio.bigattack.borer_quake"] = ("Varga: \"Feel that? That is the ground giving way under you.\"", "Varga: \"Thấy chưa? Đất đang sụt dưới chân các người.\""),
            ["guide.bigattack.borer_quake.how"] = ("It dives, bores under your biggest group and the ground cracks for 3 s; then a quake: 700 at the centre, 30 % at 16 m, and 3 s stunned. Not aircraft.", "Nó lặn xuống, đào tới dưới cụm quân lớn nhất, mặt đất nứt trong 3 giây; rồi địa chấn: 700 ở tâm, 30 % ở rìa 16 m, choáng 3 giây. Không tác dụng lên máy bay."),
            ["guide.bigattack.borer_quake.dodge"] = ("When the cracks spread, drive out of the circle; do not bunch up.", "Khi vết nứt lan ra, lái ra khỏi vòng; đừng đứng dồn."),
            ["guide.bigattack.borer_quake.stop"] = ("Break the drill beforehand: it can no longer dive.", "Phá mũi khoan từ trước: nó không lặn được nữa."),

            // ---------------------------------------------------------------- 13 Bastion
            ["bigattack.bastion_mortar_walk"] = ("Walking Mortar Barrage", "Pháo cối tổng lực"),
            ["bigattack.bastion_mortar_walk.cancelled"] = ("Mortar barrage cancelled", "Đã hủy pháo cối tổng lực"),
            ["radio.bigattack.bastion_mortar_walk"] = ("Command: the Bastion's 240 mm is walking a barrage towards us. Watch the marked points!", "Chỉ huy: cối 240 mm của Bastion đang bắn tiến dần về phía ta. Để ý các điểm đánh dấu!"),
            ["guide.bigattack.bastion_mortar_walk.how"] = ("Six 240 mm bombs, one every 0.7 s, walking down a 60 m line; twice as hard on buildings and towers.", "Sáu quả cối 240 mm, cứ 0,7 giây một quả, tiến dần theo đường dài 60 m; gấp đôi sát thương lên công trình và tháp."),
            ["guide.bigattack.bastion_mortar_walk.dodge"] = ("Each point has its own countdown: step aside from the line.", "Mỗi điểm có đếm ngược riêng: bước ngang ra khỏi đường."),
            ["guide.bigattack.bastion_mortar_walk.stop"] = ("Break the mortar.", "Phá khẩu cối."),

            // ---------------------------------------------------------------- 14 Spectre
            ["bigattack.spectre_orbit"] = ("Ring of Fire", "Vòng bắn tổng lực"),
            ["bigattack.spectre_orbit.cancelled"] = ("Spectre broke off", "Spectre đã bỏ dở đòn"),
            ["radio.bigattack.spectre_orbit"] = ("Command: the Spectre is coming down into a tight orbit. All anti-air on it!", "Chỉ huy: Spectre đang hạ thấp bay vòng hẹp. Mọi phòng không nhắm vào nó!"),
            ["guide.bigattack.spectre_orbit.how"] = ("For 8 s every gun on one 15 m circle: the 105 mm, both 40 mm and the 25 mm.", "Trong 8 giây mọi khẩu pháo dồn vào một vòng 15 m: 105 mm, hai khẩu 40 mm và 25 mm."),
            ["guide.bigattack.spectre_orbit.dodge"] = ("Leave the circle; it flies low and slow meanwhile, and your anti-air hits it 50 % harder.", "Rời khỏi vòng; trong lúc đó nó bay thấp và chậm, phòng không của ta trúng mạnh hơn 50 %."),
            ["guide.bigattack.spectre_orbit.stop"] = ("Break the 105 mm to take most of the sting out, or do 8 % of its health while it circles and it breaks off.", "Phá pháo 105 mm để giảm mạnh sát thương, hoặc gây đủ 8 % máu trong lúc nó bay vòng thì nó bỏ dở."),

            // ---------------------------------------------------------------- 15 Iron Bird
            ["bigattack.ironbird_rocket_run"] = ("Rocket Run", "Loạt rốc-két theo đường thẳng"),
            ["bigattack.ironbird_rocket_run.cancelled"] = ("Rocket run cancelled", "Đã hủy loạt rốc-két"),
            ["radio.bigattack.ironbird_rocket_run"] = ("Command: Harpy is lining up a rocket run. Get off its line!", "Chỉ huy: Harpy đang lấy hướng bắn rốc-két. Ra khỏi đường bay của nó!"),
            ["guide.bigattack.ironbird_rocket_run.how"] = ("48 rockets of 80 mm down a 70 × 8 m line.", "48 rốc-két 80 mm dọc đường bay dài 70 m, rộng 8 m."),
            ["guide.bigattack.ironbird_rocket_run.dodge"] = ("Step off the line sideways: it is only 8 m wide.", "Bước ngang ra khỏi đường bay: nó chỉ rộng 8 m."),
            ["guide.bigattack.ironbird_rocket_run.stop"] = ("Break a rocket pod: each holds 24.", "Phá hộp rốc-két: mỗi hộp 24 quả."),

            // ---------------------------------------------------------------- 16 Hive Carrier
            ["bigattack.carrier_heavy_bomb"] = ("Bunker-Buster Bomb", "Bom xuyên phá"),
            ["bigattack.carrier_heavy_bomb.cancelled"] = ("Bomb run cancelled", "Đã hủy thả bom"),
            ["radio.bigattack.carrier_heavy_bomb"] = ("Command: the carrier has stopped overhead with its bomb bay open. Hit it now!", "Chỉ huy: tàu mẹ dừng ngay trên đầu, khoang bom đã mở. Đánh nó ngay!"),
            ["guide.bigattack.carrier_heavy_bomb.how"] = ("One 900 kg penetrating bomb: 850 at the centre, falling off to 14 m, twice as hard on buildings and towers.", "Một quả bom xuyên phá 900 kg: 850 ở tâm, giảm dần tới 14 m, gấp đôi lên công trình và tháp."),
            ["guide.bigattack.carrier_heavy_bomb.dodge"] = ("Move out from under it; while its bay is open your anti-air hits it 30 % harder.", "Chạy ra khỏi vùng dưới nó; khi khoang bom mở, phòng không trúng mạnh hơn 30 %."),
            ["guide.bigattack.carrier_heavy_bomb.stop"] = ("Break the bomb bay.", "Phá khoang bom."),

            // ---------------------------------------------------------------- 17 Command Airship
            ["bigattack.airship_carpet"] = ("Carpet Bombing", "Rải thảm"),
            ["bigattack.airship_carpet.cancelled"] = ("Carpet bombing cancelled", "Đã hủy rải thảm"),
            ["radio.bigattack.airship_carpet"] = ("Wolff: \"Bomb doors open. Twelve for the ground below.\"", "Wolff: \"Mở khoang bom. Mười hai quả cho mặt đất bên dưới.\""),
            ["guide.bigattack.airship_carpet.how"] = ("Twelve 250 kg bombs in a 70 × 12 m strip along its course.", "Mười hai quả bom 250 kg thành dải 70 × 12 m theo đường bay."),
            ["guide.bigattack.airship_carpet.dodge"] = ("Step off the strip sideways, out from under its course.", "Bước ngang ra khỏi dải, tránh khỏi đường bay của nó."),
            ["guide.bigattack.airship_carpet.stop"] = ("Break the bomb bay.", "Phá khoang bom."),

            // ---------------------------------------------------------------- 18 Leviathan
            ["bigattack.leviathan_volley"] = ("Cruise Missile Volley", "Loạt tên lửa hành trình"),
            ["bigattack.leviathan_volley.cancelled"] = ("Missile volley cancelled", "Đã hủy loạt tên lửa"),
            ["radio.bigattack.leviathan_volley"] = ("Kessler: \"Launch cells open. Six for their base.\"", "Kessler: \"Mở ống phóng. Sáu quả cho căn cứ của chúng.\""),
            ["guide.bigattack.leviathan_volley.how"] = ("Six cruise missiles at your HQ, towers and groups in the base, about 8 s in flight, twice as hard on buildings.", "Sáu tên lửa hành trình vào HQ, tháp và quân trong căn cứ, bay khoảng 8 giây, gấp đôi lên công trình."),
            ["guide.bigattack.leviathan_volley.dodge"] = ("Move units off the marked landing points; towers cannot move, so cover them.", "Đưa quân ra khỏi các điểm rơi được đánh dấu; tháp không chạy được nên hãy bảo vệ chúng."),
            ["guide.bigattack.leviathan_volley.stop"] = ("Break the launch cells during the warning, or shoot the missiles down (250 health each): anti-air, C-RAM, point-defence lasers.", "Phá ống phóng trong lúc cảnh báo, hoặc bắn hạ từng tên lửa (máu 250): phòng không, C-RAM, La-de PK."),
        };
    }
}
