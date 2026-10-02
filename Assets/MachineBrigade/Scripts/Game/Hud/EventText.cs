using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 23 A-D: the mission events' words, English and Vietnamese: the notices for the top-edge queue
    /// ("event.&lt;kind&gt;[.&lt;variant&gt;].&lt;moment&gt;", placeholders {seconds} and {dir}) and the lines the events say
    /// ("radio.&lt;speaker&gt;.ev.&lt;kind&gt;[.&lt;variant&gt;].&lt;moment&gt;"; see MissionEventSystem.NoticeKey and LineKey). The
    /// story's names are prompt 22's, as <c>{@id}</c> tokens.
    /// </summary>
    public static class EventText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // Where a threat comes from (a notice's {dir}), along the line from our camp to the enemy's.
            ["event.dir.front"] = ("from the front", "từ phía trước"),
            ["event.dir.left"] = ("on the left flank", "ở cánh trái"),
            ["event.dir.right"] = ("on the right flank", "ở cánh phải"),
            ["event.dir.rear"] = ("from behind", "từ phía sau"),
            ["result.sideObjectives"] = ("Side objectives", "Mục tiêu phụ"),

            // C: reinforcements.
            ["event.enemyWave.warn"] = ("Enemy reinforcements in {seconds} s, {dir}", "Viện quân địch tới sau {seconds} giây, {dir}"),
            ["event.allyWave.start"] = ("Meridian Accord reinforcements are coming in", "Tiếp viện của Meridian Accord đang tới"),
            ["radio.linh.ev.enemyWave.warn"] = ("Enemy column on the move. They will be on us in seconds.", "Một đoàn quân địch đang tiến tới. Vài giây nữa là chúng ập vào ta."),
            ["radio.khai.ev.allyWave.start"] = ("The Accord is sending a column. Make room for them.", "Accord gửi tới một cánh quân. Nhường chỗ cho họ."),

            // D.1: fire support.
            ["event.barrage.warn"] = ("Enemy guns ranging on our position: move in {seconds} s", "Pháo địch đang căn vào vị trí ta: rời đi trong {seconds} giây"),
            ["event.airRaid.warn"] = ("Enemy bombers inbound in {seconds} s", "Máy bay ném bom địch tới sau {seconds} giây"),
            ["event.counterBattery.warn"] = ("Counter-battery fire on our guns in {seconds} s: move them", "Địch phản pháo vào pháo ta sau {seconds} giây: dời pháo đi"),
            ["event.allyAirStrike.start"] = ("{@dieuhau}'s air strike is going in", "Đợt không kích của {@dieuhau} đang lao vào"),
            ["event.allyArtillery.start"] = ("Accord artillery is firing in support", "Pháo binh Accord đang bắn yểm trợ"),
            ["radio.linh.ev.barrage.warn"] = ("Their spotters have us. Shells on the way, spread out!", "Trinh sát của chúng đã thấy ta. Đạn pháo đang tới, giãn ra!"),
            ["radio.linh.ev.airRaid.warn"] = ("Bombers on the scope, low and fast. Get under cover!", "Máy bay ném bom trên màn radar, bay thấp và nhanh. Tìm chỗ nấp!"),
            ["radio.linh.ev.counterBattery.warn"] = ("Our guns have fired from one spot too long. They have found them.", "Pháo ta bắn từ một chỗ quá lâu. Chúng đã tìm ra rồi."),
            ["radio.dieuhau.ev.allyAirStrike.start"] = ("Rolling in. Keep your heads down, this one is loud.", "Tôi lao vào đây. Cúi đầu xuống, đợt này ồn lắm."),
            ["radio.khai.ev.allyArtillery.start"] = ("Accord guns are with us. Push under their shells.", "Pháo Accord đang yểm trợ ta. Tiến lên dưới làn đạn của họ."),

            // D.2: the general on the field.
            ["event.generalField.warn"] = ("The enemy general is coming onto the field in {seconds} s, {dir}", "Tướng địch sắp ra trận sau {seconds} giây, {dir}"),
            ["event.generalField.start"] = ("The enemy general has taken the field", "Tướng địch đã ra trận"),
            ["event.generalField.retreat"] = ("The enemy general is pulling back", "Tướng địch đang rút lui"),
            ["event.generalField.done"] = ("The enemy general is down", "Tướng địch đã bị hạ"),
            ["radio.linh.ev.generalField.warn"] = ("Command signal moving up. The general is coming in person.", "Tín hiệu chỉ huy đang tiến lên. Chính viên tướng đang tới."),
            ["radio.varga.ev.generalField.start"] = ("Enough watching. Let us see who drives better, Colonel.", "Xem thế là đủ rồi. Để xem ai lái giỏi hơn, đại tá."),
            ["radio.varga.ev.generalField.retreat"] = ("Well fought. I will take my machine home.", "Đánh hay lắm. Tôi sẽ đưa cỗ máy của mình về."),
            ["radio.orlov.ev.generalField.start"] = ("I will correct your fire myself. From close up.", "Ta sẽ tự tay điều chỉnh làn đạn. Từ cự ly gần."),
            ["radio.orlov.ev.generalField.retreat"] = ("The numbers have changed. Falling back to the next line.", "Số liệu đã thay đổi. Rút về tuyến sau."),
            ["radio.kessler.ev.generalField.start"] = ("If you want something done on schedule, do it yourself.", "Muốn việc gì đúng lịch thì phải tự làm."),
            ["radio.kessler.ev.generalField.retreat"] = ("This is no longer profitable. I am leaving.", "Việc này không còn lời nữa. Ta đi đây."),
            ["radio.sen.ev.generalField.start"] = ("I will guide the swarm myself. It listens to me.", "Tôi sẽ tự dẫn bầy drone. Chúng nghe lời tôi."),
            ["radio.sen.ev.generalField.retreat"] = ("Not today. The swarm comes home with me.", "Không phải hôm nay. Bầy drone về cùng tôi."),
            ["radio.quaden.ev.generalField.start"] = ("Clear the sky. I am coming down to finish this.", "Dọn trời đi. Ta xuống để kết thúc chuyện này."),
            ["radio.quaden.ev.generalField.retreat"] = ("Breaking off. We will meet again up high.", "Tách ra. Ta sẽ gặp lại trên cao."),
            ["radio.hung.ev.generalField.start"] = ("You wanted to see me, {@khai}. Here I am.", "Anh muốn gặp tôi, {@khai}. Tôi đây."),
            ["radio.hung.ev.generalField.retreat"] = ("Not here. Not yet. Pull back.", "Không phải ở đây. Chưa phải lúc. Rút lui."),
            ["radio.aurel.ev.generalField.start"] = ("Some decisions should not be delegated.", "Có những quyết định không nên giao cho người khác."),
            ["radio.aurel.ev.generalField.retreat"] = ("An acceptable loss. Withdraw my vehicle.", "Một tổn thất chấp nhận được. Rút xe của tôi về."),

            // D.3: side objectives.
            // F.3: the side objective's row on the mission bar (short: the clock and the count show beside it).
            ["event.sideObjective.intercept.row"] = ("Stop the files convoy", "Chặn đoàn xe hồ sơ"),
            ["event.sideObjective.rescue.row"] = ("Rescue the allied column", "Cứu đoàn xe đồng minh"),
            ["event.sideObjective.protect.row"] = ("See the civilians through", "Hộ tống đoàn xe dân sự"),
            ["event.sideObjective.intercept.start"] = ("Side objective: stop the convoy with the files before it leaves ({seconds} s)", "Mục tiêu phụ: chặn đoàn xe chở hồ sơ trước khi nó rời đi ({seconds} giây)"),
            ["event.sideObjective.intercept.done"] = ("The files are ours", "Hồ sơ đã về tay ta"),
            ["event.sideObjective.intercept.fail"] = ("The convoy with the files got away", "Đoàn xe chở hồ sơ đã thoát"),
            ["event.sideObjective.rescue.start"] = ("Side objective: break the ring round the allied column ({seconds} s)", "Mục tiêu phụ: phá vòng vây quanh đoàn xe đồng minh ({seconds} giây)"),
            ["event.sideObjective.rescue.done"] = ("The allied column is free and joins the fight", "Đoàn xe đồng minh đã thoát vây và vào trận cùng ta"),
            ["event.sideObjective.rescue.fail"] = ("The allied column is lost", "Đoàn xe đồng minh đã mất"),
            ["event.sideObjective.protect.start"] = ("Side objective: see the civilian convoy across ({seconds} s)", "Mục tiêu phụ: hộ tống đoàn xe dân sự qua bản đồ ({seconds} giây)"),
            ["event.sideObjective.protect.done"] = ("The civilians are through", "Đoàn xe dân sự đã qua an toàn"),
            ["event.sideObjective.protect.fail"] = ("The civilian convoy did not make it", "Đoàn xe dân sự không qua được"),
            ["radio.khai.ev.sideObjective.intercept.start"] = ("That convoy carries their files. I want them before they leave the map.", "Đoàn xe đó chở hồ sơ của chúng. Tôi muốn có chúng trước khi xe rời bản đồ."),
            ["radio.khai.ev.sideObjective.intercept.done"] = ("Good. {@linh} will want to read those tonight.", "Tốt. Tối nay {@linh} sẽ muốn đọc chỗ đó."),
            ["radio.khai.ev.sideObjective.intercept.fail"] = ("They got away with it. Back to the main job.", "Chúng thoát rồi. Quay lại việc chính."),
            ["radio.khai.ev.sideObjective.rescue.start"] = ("An Accord column is cut off. Break them out if you can.", "Một cánh quân Accord bị vây. Phá vây cho họ nếu làm được."),
            ["radio.khai.ev.sideObjective.rescue.done"] = ("They are out, and they are staying to fight with us.", "Họ thoát rồi, và họ ở lại chiến đấu cùng ta."),
            ["radio.khai.ev.sideObjective.rescue.fail"] = ("We were too late for them.", "Ta tới quá muộn với họ."),
            ["radio.khai.ev.sideObjective.protect.start"] = ("Civilians on the road. Nobody shoots at them while we are here.", "Có dân thường trên đường. Không ai được bắn vào họ khi ta còn ở đây."),
            ["radio.khai.ev.sideObjective.protect.done"] = ("They made it. That matters more than the ground.", "Họ qua được rồi. Điều đó quan trọng hơn mảnh đất này."),
            ["radio.khai.ev.sideObjective.protect.fail"] = ("We lost them. Remember this one.", "Ta đã để mất họ. Hãy nhớ lấy chuyện này."),

            // D.4: the economy.
            ["event.neutralConvoy.start"] = ("A neutral supply convoy is crossing: whoever knocks it out takes its CP", "Một đoàn tiếp tế trung lập đi ngang: bên nào hạ được sẽ nhận CP"),
            ["event.lootDrop.start"] = ("A loot crate is coming down in the middle: hold it to take it", "Một thùng chiến lợi phẩm đang rơi xuống giữa bản đồ: giữ nó để lấy"),
            ["event.lootDrop.done"] = ("We took the loot crate", "Ta đã lấy được thùng chiến lợi phẩm"),
            ["event.lootDrop.fail"] = ("The enemy took the loot crate", "Địch đã lấy thùng chiến lợi phẩm"),
            ["event.supplyRaid.warn"] = ("An enemy raid is heading for our supplies in {seconds} s, {dir}", "Một toán địch đang nhắm vào kho tiếp tế của ta sau {seconds} giây, {dir}"),
            ["event.supplyRaid.done"] = ("The raid on our supplies is beaten off", "Đã đẩy lui toán đánh kho tiếp tế"),
            ["event.supplyRaid.fail"] = ("The raiders hit our supplies", "Toán địch đã phá kho tiếp tế của ta"),
            ["radio.linh.ev.neutralConvoy.start"] = ("A supply column with no flag is crossing. Its load goes to whoever stops it.", "Một đoàn tiếp tế không cờ đang đi ngang. Hàng của nó thuộc về bên nào chặn được."),
            ["radio.linh.ev.supplyRaid.warn"] = ("A fast group is going round us, straight for our supplies.", "Một toán cơ động đang vòng qua ta, nhắm thẳng vào kho tiếp tế."),

            // D.5-D.6: logistics and intelligence.
            ["event.supplyDrop.start"] = ("Supply drop: repairs and ammunition for the units under it", "Thả dù tiếp tế: sửa chữa và nạp đạn cho quân ta bên dưới"),
            ["event.intelReveal.start"] = ("{@linh} marks an enemy position: in sight for {seconds} s", "{@linh} đánh dấu vị trí địch: hiện rõ trong {seconds} giây"),
            ["event.blackout.warn"] = ("Electronic storm in {seconds} s: the minimap and radar will go dark", "Bão nhiễu điện tử sau {seconds} giây: bản đồ nhỏ và radar sẽ tắt"),
            ["event.blackout.start"] = ("Minimap and radar down: {seconds} s", "Bản đồ nhỏ và radar đã tắt: {seconds} giây"),
            ["event.blackout.end"] = ("Minimap and radar are back", "Bản đồ nhỏ và radar đã hoạt động lại"),
            ["radio.khai.ev.supplyDrop.start"] = ("Supplies coming down on you. Refit and get back in.", "Tiếp tế đang thả xuống chỗ các anh. Sửa xe, nạp đạn rồi vào lại."),
            ["radio.linh.ev.intelReveal.start"] = ("I have them. Marking their position now, you will not have long.", "Tôi thấy chúng rồi. Đang đánh dấu vị trí, các anh không có nhiều thời gian đâu."),
            ["radio.linh.ev.blackout.warn"] = ("Jamming building up on every band. We are about to go blind.", "Nhiễu đang dâng lên trên mọi tần số. Ta sắp bị mù rồi."),
            ["radio.linh.ev.blackout.end"] = ("Picture is back. I can see again.", "Hình ảnh đã về. Tôi thấy lại được rồi."),

            // D.7: the mini boss.
            ["event.miniBoss.warn"] = ("A mini boss is coming in {seconds} s, {dir}", "Một mini boss sắp tới sau {seconds} giây, {dir}"),
            ["radio.linh.ev.miniBoss.warn"] = ("Something big on the sensors. Bigger than a tank.", "Có thứ gì rất lớn trên cảm biến. Lớn hơn một chiếc xe tăng."),
            ["radio.varga.ev.miniBoss.start"] = ("Meet one of my children, Colonel.", "Gặp một đứa con của tôi đi, đại tá."),
            ["radio.orlov.ev.miniBoss.start"] = ("Target acquired. Send in the heavy piece.", "Đã khóa mục tiêu. Đưa khẩu hạng nặng vào."),
            ["radio.kessler.ev.miniBoss.start"] = ("An expensive answer. You have earned it.", "Một câu trả lời đắt giá. Ngươi xứng đáng với nó."),
            ["radio.sen.ev.miniBoss.start"] = ("The hive has woken. I am sorry.", "Tổ drone đã thức giấc. Tôi xin lỗi."),
            ["radio.quaden.ev.miniBoss.start"] = ("Look up, Colonel. You have company.", "Nhìn lên đi, đại tá. Ông có khách đấy."),
            ["radio.hung.ev.miniBoss.start"] = ("You taught me what it takes. Here it is.", "Anh đã dạy tôi cần những gì. Đây."),
            ["radio.aurel.ev.miniBoss.start"] = ("Deploy the asset. Invoice the damage later.", "Tung vũ khí vào. Tính thiệt hại sau."),

            // D.8: a new plan.
            ["event.planChange.start"] = ("New orders from {@khai}: the objective has changed", "Lệnh mới từ {@khai}: mục tiêu đã thay đổi"),
            ["radio.khai.ev.planChange.start"] = ("Change of plan. Forget the old objective, here is the new one.", "Đổi kế hoạch. Quên mục tiêu cũ đi, đây là mục tiêu mới."),

            // D.9: the weather turns.
            ["event.weatherShift.snow.warn"] = ("A snowstorm is rolling in: sight falls in {seconds} s", "Bão tuyết đang kéo tới: tầm nhìn giảm sau {seconds} giây"),
            ["event.weatherShift.fog.warn"] = ("Fog is coming in: sight falls in {seconds} s", "Sương mù đang kéo tới: tầm nhìn giảm sau {seconds} giây"),
            ["event.weatherShift.storm.warn"] = ("A storm front is coming: sight falls in {seconds} s", "Một cơn giông đang tới: tầm nhìn giảm sau {seconds} giây"),
            ["event.weatherShift.night.warn"] = ("Night is falling: sight falls in {seconds} s", "Trời đang tối dần: tầm nhìn giảm sau {seconds} giây"),
            ["event.weatherShift.sandstorm.warn"] = ("A sandstorm is coming: sight falls in {seconds} s", "Bão cát đang kéo tới: tầm nhìn giảm sau {seconds} giây"),
            ["event.weatherShift.rain.warn"] = ("Rain sets in within {seconds} s", "Trời sắp mưa sau {seconds} giây"),
            ["event.weatherShift.clear.warn"] = ("The weather is clearing in {seconds} s", "Trời sắp quang đãng sau {seconds} giây"),
            ["event.weatherShift.overcast.warn"] = ("Cloud is coming over in {seconds} s", "Mây sắp kéo tới sau {seconds} giây"),
            ["radio.linh.ev.weatherShift.snow.warn"] = ("Snowstorm coming in. We will lose sight of them soon.", "Bão tuyết đang kéo tới. Ta sắp mất dấu chúng rồi."),
            ["radio.linh.ev.weatherShift.fog.warn"] = ("Fog off the water. Keep close, keep talking.", "Sương mù từ mặt nước tràn vào. Đi sát nhau, giữ liên lạc."),
            ["radio.linh.ev.weatherShift.storm.warn"] = ("Storm front on the radar. It is going to get rough.", "Có giông trên radar. Sắp vất vả rồi đây."),
            ["radio.linh.ev.weatherShift.night.warn"] = ("Light is going. Watch for muzzle flashes.", "Trời tối dần. Để ý ánh lửa đầu nòng."),
            ["radio.linh.ev.weatherShift.sandstorm.warn"] = ("Sand wall coming. Close the hatches.", "Một bức tường cát đang tới. Đóng hết cửa xe lại."),
            ["radio.linh.ev.weatherShift.rain.warn"] = ("Rain moving in. The ground will get heavy.", "Mưa đang tới. Mặt đất sẽ nặng lầy."),
            ["radio.linh.ev.weatherShift.clear.warn"] = ("It is clearing up. They will see us coming now.", "Trời đang quang dần. Giờ chúng sẽ thấy ta tới."),
            ["radio.linh.ev.weatherShift.overcast.warn"] = ("Cloud coming over. Our aircraft will fly lower.", "Mây đang kéo tới. Máy bay của ta sẽ phải bay thấp hơn."),

            // Prompt 31 L3: the events that change the battlefield (each warned 8-12 s ahead, its places on the minimap).
            ["event.sandstormTurn.warn"] = ("The wind is turning: the sandstorm rolls over the marked half in {seconds} s", "Gió đang đổi hướng: bão cát tràn qua nửa bản đồ được đánh dấu sau {seconds} giây"),
            ["event.sandstormTurn.end"] = ("The sandstorm is passing: sight comes back", "Bão cát đang qua: tầm nhìn trở lại"),
            ["event.groundChange.warn"] = ("The way ahead closes in {seconds} s: find another route", "Lối đi phía trước sẽ bị chặn sau {seconds} giây: tìm đường khác"),
            ["event.groundChange.start"] = ("The way is closed: the routes go round it", "Lối đi đã bị chặn: đường đi vòng qua"),
            ["radio.linh.ev.groundChange.warn"] = ("Something is closing across the road ahead. Plan another way through.", "Có thứ gì đang chắn ngang đường phía trước. Tính đường khác mà qua."),
            ["event.groundChange.alarm.warn"] = ("Alarm! The rolling-mill gate shuts in {seconds} s", "Báo động! Cổng xưởng cán sẽ đóng sau {seconds} giây"),
            ["event.groundChange.alarm.start"] = ("The mill gate is shut: go round by the other lanes", "Cổng xưởng cán đã đóng: đi vòng qua các lối khác"),
            ["radio.linh.ev.groundChange.alarm.warn"] = ("They have seen us. Sirens all over the works, and the mill gate is coming down.", "Chúng thấy ta rồi. Còi báo động khắp xưởng, cổng xưởng cán đang hạ xuống."),
            ["event.enemyWave.alarm.warn"] = ("The alarm brings the garrison in {seconds} s, {dir}", "Báo động gọi đồn binh tới sau {seconds} giây, {dir}"),
            ["radio.linh.ev.enemyWave.alarm.warn"] = ("The whole garrison is awake now. Here they come.", "Cả đồn binh đã thức dậy. Chúng tới kìa."),
            ["radio.linh.ev.sandstormTurn.warn"] = ("The wind has swung round. The sand is coming our way, and their side is clearing.", "Gió đã quay chiều. Cát đang đổ về phía ta, còn phía bên kia đang quang dần."),
        };
    }
}
