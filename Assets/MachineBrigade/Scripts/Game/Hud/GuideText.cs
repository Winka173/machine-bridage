using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>The detail page's Guide tab: what every vehicle and fire support is for, how it fights and how to use it, in English and Vietnamese. [[word]] marks a key word (drawn highlighted).</summary>
    public static class GuideText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // Ground vehicles the player can buy.
            ["guide.scout_jeep"] = (
                "[[Scout]] · very light armour · fast and cheap\n" +
                "How it fights: a short-range machine gun fired on the move. Its long sight [[spots]] enemies, and it [[captures]] points at double speed.\n" +
                "Strong / weak: beats [[artillery]] and support trucks caught alone; loses to any armoured car, tank or tower.\n" +
                "Tip: send two early to grab empty points, then keep them ahead of your artillery as spotters.",
                "[[Trinh sát]] · giáp rất mỏng · nhanh và rẻ\n" +
                "Cách đánh: súng máy tầm gần, vừa chạy vừa bắn. Nhìn xa để [[phát hiện]] địch cho cả quân, [[chiếm cứ điểm]] nhanh gấp đôi.\n" +
                "Mạnh / yếu: diệt được [[pháo binh]] và xe hỗ trợ đi lẻ; thua mọi xe bọc thép, xe tăng và tháp canh.\n" +
                "Mẹo: tung hai chiếc đầu trận để chiếm cứ điểm trống, sau đó cho đi trước làm mắt cho pháo binh."),
            ["guide.armored_car"] = (
                "[[Armoured car]] · light armour · fast raider\n" +
                "How it fights: a 25 mm autocannon fired on the move at ground and air, best on [[light vehicles]] and helicopters; [[captures]] points 2× as fast.\n" +
                "Strong / weak: beats scouts, artillery, [[AA trucks]] and support vehicles; its rounds bounce off tanks and towers, which beat it.\n" +
                "Tip: go round the flank of the enemy line to hunt their artillery and support trucks.",
                "[[Xe bọc thép]] · giáp nhẹ · đột kích nhanh\n" +
                "Cách đánh: pháo 25 mm vừa chạy vừa bắn cả đất lẫn trời, mạnh nhất với [[xe nhẹ]] và trực thăng; [[chiếm cứ điểm]] nhanh gấp đôi.\n" +
                "Mạnh / yếu: thắng trinh sát, pháo binh, [[xe phòng không]] và xe hỗ trợ; đạn nảy khỏi xe tăng và tháp canh nên thua chúng.\n" +
                "Mẹo: vòng qua sườn tuyến địch để săn pháo binh và xe hỗ trợ phía sau."),
            ["guide.ifv"] = (
                "[[Infantry fighting vehicle]] · light armour · all-rounder\n" +
                "How it fights: an autocannon on the move for light targets and aircraft, a TOW [[anti-tank missile]] (34 m) for tanks; [[captures]] points 3× as fast and pops [[smoke]] when shot at.\n" +
                "Strong / weak: beats scouts, [[light vehicles]], artillery and AA, and chips at tanks; a tank in a straight fight still wins.\n" +
                "Tip: a good [[second line]] behind your tanks: it fills the gaps and takes points while they fight.",
                "[[Xe chiến đấu bộ binh]] · giáp nhẹ · đa năng\n" +
                "Cách đánh: pháo tự động vừa chạy vừa bắn xe nhẹ và máy bay, kèm [[tên lửa chống tăng]] TOW (34 m) cho xe tăng; [[chiếm cứ điểm]] nhanh gấp 3, bị bắn thì tự thả [[khói]].\n" +
                "Mạnh / yếu: thắng trinh sát, [[xe nhẹ]], pháo binh và phòng không, gây sát thương cả xe tăng; đấu tay đôi với tăng vẫn thua.\n" +
                "Mẹo: [[tuyến hai]] lý tưởng sau xe tăng: lấp chỗ hở và chiếm điểm trong lúc xe tăng giao chiến."),
            ["guide.light_tank"] = (
                "[[Light tank]] · heavy armour · cheap and quick\n" +
                "How it fights: a 57 mm [[armour-piercing]] gun on the move, the shortest-ranged tank; its coaxial MG shoots [[aircraft]] once the ground is clear.\n" +
                "Strong / weak: beats [[light vehicles]], scouts and AA trucks; loses to heavier tanks, tank hunters and attack helicopters.\n" +
                "Tip: a cheap early answer to enemy armoured cars; swap it for battle tanks once you have the CP.",
                "[[Tăng hạng nhẹ]] · giáp dày · rẻ và nhanh\n" +
                "Cách đánh: pháo 57 mm [[xuyên giáp]] vừa chạy vừa bắn, tầm ngắn nhất trong các xe tăng; súng đồng trục bắn [[máy bay]] khi mặt đất đã sạch.\n" +
                "Mạnh / yếu: thắng [[xe nhẹ]], trinh sát và xe phòng không; thua tăng nặng hơn, xe diệt tăng và trực thăng tấn công.\n" +
                "Mẹo: lựa chọn rẻ để chặn xe bọc thép địch đầu trận; có CP thì thay bằng tăng chủ lực."),
            ["guide.main_battle_tank"] = (
                "[[Battle tank]] · heavy armour · the backbone of the army\n" +
                "How it fights: a 120 mm [[armour-piercing]] gun fired on the move, a roof MG, and a coaxial MG that shoots [[aircraft]] once the ground is clear.\n" +
                "Strong / weak: beats [[light vehicles]], scouts and AA; loses to heavy tanks, tank hunters and helicopters.\n" +
                "Tip: lead every push with two or three, with a tank hunter behind them and AA close by.",
                "[[Tăng chủ lực]] · giáp dày · xương sống của đội quân\n" +
                "Cách đánh: pháo 120 mm [[xuyên giáp]] vừa chạy vừa bắn ở tầm trung, súng máy trên nóc, súng đồng trục bắn [[máy bay]] khi mặt đất đã sạch.\n" +
                "Mạnh / yếu: thắng [[xe nhẹ]], trinh sát và phòng không; thua tăng hạng nặng, xe diệt tăng và trực thăng.\n" +
                "Mẹo: dẫn đầu mỗi đợt tiến công bằng 2–3 chiếc, xe diệt tăng theo sau và phòng không ở gần."),
            ["guide.flame_tank"] = (
                "[[Flame tank]] · heavy armour · very short range (13 m)\n" +
                "How it fights: a [[flamethrower]] that must get very close; the stream of fire splashes over groups, deadly to [[light vehicles]] and [[bunkers]].\n" +
                "Strong / weak: melts light armour, scouts and towers up close; tanks and anything that outranges it kill it on the way in.\n" +
                "Tip: send it through towns or smoke, so it reaches the enemy before it is shot to pieces.",
                "[[Tăng phun lửa]] · giáp dày · tầm cực gần (13 m)\n" +
                "Cách đánh: [[súng phun lửa]] phải áp sát mới bắn; luồng lửa lan ra cả nhóm, cực mạnh với [[xe nhẹ]] và [[lô cốt]].\n" +
                "Mạnh / yếu: thiêu rụi xe nhẹ, trinh sát và tháp canh khi áp sát; xe tăng và mọi thứ bắn xa hơn hạ nó trước khi tới nơi.\n" +
                "Mẹo: cho đi qua phố xá hoặc màn khói để áp sát địch trước khi bị bắn nát."),
            ["guide.twin_tank"] = (
                "[[Twin-barrel tank]] · heavy armour · burst damage\n" +
                "How it fights: two 105 mm guns fire one right after the other, a heavy [[double shot]] at 34 m, then reload; coaxial and roof MGs.\n" +
                "Strong / weak: outguns battle tanks, [[light vehicles]] and AA; loses to heavy tanks, tank hunters and helicopters.\n" +
                "Tip: its double shot finishes damaged tanks fast; keep an engineer behind it to stay in the fight.",
                "[[Tăng hai nòng]] · giáp dày · sát thương dồn\n" +
                "Cách đánh: hai pháo 105 mm bắn nối tiếp: một [[phát đôi]] cực mạnh ở 34 m rồi nạp đạn; có súng máy đồng trục và trên nóc.\n" +
                "Mạnh / yếu: áp đảo tăng chủ lực, [[xe nhẹ]] và phòng không; thua tăng hạng nặng, xe diệt tăng và trực thăng.\n" +
                "Mẹo: phát đôi kết liễu xe tăng đã yếu rất nhanh; kèm xe công binh phía sau để nó trụ lâu."),
            ["guide.turtle_tank"] = (
                "[[Turtle tank]] · heavy armour under a steel shed · drone-proof\n" +
                "How it fights: a 120 mm gun that cannot turn: it aims with the whole hull. The shed stops 80% of [[drone]] damage; its roller sets off [[mines]].\n" +
                "Strong / weak: walks through FPV swarms, Lancets and minefields, and beats light vehicles; heavy tanks and tank destroyers beat it.\n" +
                "Tip: lead with it against drone carriers and mine layers; it is slow, so keep the others behind it.",
                "[[Xe tăng rùa]] · giáp dày dưới mái thép · chống drone\n" +
                "Cách đánh: pháo 120 mm không xoay được, phải quay cả thân để ngắm. Mái thép chặn 80% sát thương [[drone]], trục lăn kích nổ [[mìn]] vô hại.\n" +
                "Mạnh / yếu: đi xuyên bầy FPV, Lancet và bãi mìn, thắng xe nhẹ; thua tăng hạng nặng và xe diệt tăng.\n" +
                "Mẹo: cho đi đầu khi địch có xe drone và xe rải mìn; nó chậm, để các xe khác theo sau."),
            ["guide.bmpt"] = (
                "[[Tank support]] · heavy armour · many guns\n" +
                "How it fights: twin 30 mm cannons (ground and air), paired Ataka [[anti-tank missiles]] from 40 m, and [[grenade launchers]] firing to both sides.\n" +
                "Strong / weak: clears [[light vehicles]], scouts, helicopters and AA round your tanks, and hurts tanks; heavy tanks and tank hunters beat it.\n" +
                "Tip: drive it next to your battle tanks: it kills what they are bad at hitting.",
                "[[Xe yểm trợ tăng]] · giáp dày · nhiều vũ khí\n" +
                "Cách đánh: pháo đôi 30 mm (bắn cả đất lẫn trời), [[tên lửa chống tăng]] Ataka bắn cặp từ 40 m, và [[súng phóng lựu]] bắn sang hai bên.\n" +
                "Mạnh / yếu: dọn [[xe nhẹ]], trinh sát, trực thăng và phòng không quanh xe tăng ta, hại được cả xe tăng; thua tăng nặng và xe diệt tăng.\n" +
                "Mẹo: cho chạy cạnh tăng chủ lực: nó hạ những gì xe tăng khó bắn trúng."),
            ["guide.heavy_tank"] = (
                "[[Heavy tank]] · thick armour · slow\n" +
                "How it fights: a 152 mm gun that smashes tanks and [[fortifications]], with a 30 mm autocannon beside it that can answer [[helicopters]].\n" +
                "Strong / weak: beats battle tanks, light vehicles and towers head on; [[tank hunters]], artillery and aircraft are its bane.\n" +
                "Tip: the spearhead against defences; it is slow, so escort it with AA and never send it alone.",
                "[[Tăng hạng nặng]] · giáp rất dày · chậm\n" +
                "Cách đánh: pháo 152 mm đập nát xe tăng và [[công sự]], kèm pháo 30 mm bên cạnh để đáp trả [[trực thăng]].\n" +
                "Mạnh / yếu: thắng tăng chủ lực, xe nhẹ và tháp canh khi đối đầu; sợ [[xe diệt tăng]], pháo binh và máy bay.\n" +
                "Mẹo: làm mũi nhọn đánh công sự; nó chậm, nên cho phòng không đi kèm và đừng để đi một mình."),
            ["guide.titan_tank"] = (
                "[[Super-heavy tank]] · the toughest tank · very slow and costly\n" +
                "How it fights: twin 140 mm guns fire a two-shot [[volley]] out to 40 m, backed by an anti-tank missile and two machine guns.\n" +
                "Strong / weak: crushes tanks, light vehicles and [[fortifications]]; [[tank hunters]], artillery and aircraft wear it down.\n" +
                "Tip: an anchor for a big push; guard it with AA against helicopters.",
                "[[Siêu tăng]] · xe tăng lì nhất · rất chậm và đắt\n" +
                "Cách đánh: pháo đôi 140 mm bắn [[loạt đôi]] tới 40 m, kèm tên lửa chống tăng và hai súng máy.\n" +
                "Mạnh / yếu: nghiền nát xe tăng, xe nhẹ và [[công sự]]; bị [[xe diệt tăng]], pháo binh và máy bay bào dần.\n" +
                "Mẹo: làm trụ cho đợt tấn công lớn; phải có phòng không đi kèm để che trực thăng."),
            ["guide.siege_tank"] = (
                "[[Siege gun]] · heavy armour · very slow · 12 CP\n" +
                "How it fights: stops and fires 203 mm [[bunker-buster]] shells up to 62 m, beyond most towers: 2.4× damage on towers and buildings (about 155 a second); 12 rounds, then a reload.\n" +
                "Strong / weak: cracks [[fortifications]] and tank lines; tank hunters, artillery and aircraft are its threats, and it can chase nothing.\n" +
                "Tip: made for bases and [[Siege]]: park it just outside the towers' reach and let it take them apart.",
                "[[Tăng công thành]] · giáp dày · cực chậm · 12 CP\n" +
                "Cách đánh: dừng lại rồi nã đạn 203 mm [[phá boong-ke]] xa tới 62 m, ngoài tầm hầu hết tháp: gấp 2,4 lần sát thương lên tháp và công trình (khoảng 155 mỗi giây); 12 phát rồi nạp lại.\n" +
                "Mạnh / yếu: đập vỡ [[công sự]] và tuyến xe tăng; sợ xe diệt tăng, pháo binh và máy bay, và không đuổi được ai.\n" +
                "Mẹo: sinh ra để đánh căn cứ và chế độ [[Công thành]]: đỗ ngay ngoài tầm của tháp và để nó tháo dỡ từng cái."),
            ["guide.armored_bulldozer"] = (
                "[[Armoured bulldozer]] · heavy armour · breaks bases open\n" +
                "How it fights: only a roof machine gun; its [[blade]] rams towers, bunkers and buildings at [[three times]] the damage (4 m), ploughs [[dragon's teeth]] flat as it drives into them and takes half a mine's blast.\n" +
                "Strong / weak: the best at tearing down defences up close; it barely scratches tanks, and tank hunters, ATGMs and anything that outranges it kill it on the way in.\n" +
                "Tip: send it in front of the tanks when they push into a base; it does not clear mines (that is the sapper's job) and it is no substitute for a turtle tank as the line's shield.",
                "[[Xe ủi bọc thép]] · giáp dày · phá mở căn cứ\n" +
                "Cách đánh: chỉ có súng máy trên nóc; [[lưỡi ủi]] húc tháp, lô cốt và nhà cửa với sát thương [[gấp ba]] (4 m), ủi phẳng [[răng rồng]] khi lao qua, và chỉ nhận một nửa sức nổ của mìn.\n" +
                "Mạnh / yếu: phá công sự ở cự ly gần tốt nhất; gần như không làm gì được xe tăng, và xe diệt tăng, tên lửa chống tăng cùng mọi thứ bắn xa hơn diệt nó trên đường lao vào.\n" +
                "Mẹo: cho đi trước xe tăng khi tấn công vào căn cứ; nó không gỡ mìn (việc của công binh CT) và không thay được xe rùa để che chắn cho đội hình."),
            ["guide.tank_destroyer"] = (
                "[[Tank hunter]] · heavy armour · long range (40 m)\n" +
                "How it fights: a long 105 mm [[armour-piercing]] gun, fired on the move, that outranges battle tanks and hits far harder; plus a roof MG.\n" +
                "Strong / weak: kills [[tanks]], heavy tanks and [[bosses]] from outside their reach; fears artillery, and light cars that close in.\n" +
                "Tip: keep it just behind your tanks so it fires first; the best answer to heavy armour and bosses.",
                "[[Diệt tăng]] · giáp dày · tầm xa (40 m)\n" +
                "Cách đánh: pháo 105 mm nòng dài [[xuyên giáp]], vừa chạy vừa bắn, xa hơn và mạnh hơn hẳn pháo tăng chủ lực; súng máy nóc cho mục tiêu nhỏ.\n" +
                "Mạnh / yếu: hạ [[xe tăng]], tăng hạng nặng và [[trùm]] từ ngoài tầm với của chúng; sợ pháo binh và xe nhẹ áp sát.\n" +
                "Mẹo: để ngay sau hàng xe tăng để nó bắn trước; khắc tinh của thiết giáp nặng và trùm."),
            ["guide.atgm_carrier"] = (
                "[[Missile tank hunter]] · light armour · long range (42 m)\n" +
                "How it fights: two guided [[anti-tank missiles]] at a time from 42 m, beyond a battle tank's gun, even on the move; a roof MG for light targets.\n" +
                "Strong / weak: kills tanks and heavy tanks before they can shoot back; APS tanks and [[jammers]] stop its missiles, autocannons shred it.\n" +
                "Tip: keep it behind your front line: the tanks soak up the fire while it shoots.",
                "[[Diệt tăng tên lửa]] · giáp mỏng · tầm xa (42 m)\n" +
                "Cách đánh: mỗi lượt phóng hai [[tên lửa chống tăng]] dẫn đường từ 42 m, xa hơn pháo tăng chủ lực, bắn được khi chạy; súng máy nóc cho xe nhẹ.\n" +
                "Mạnh / yếu: hạ xe tăng và tăng nặng trước khi chúng kịp bắn trả; tăng APS và [[xe gây nhiễu]] chặn tên lửa, pháo tự động xé nát nó.\n" +
                "Mẹo: giữ sau tuyến đầu để xe tăng hứng đạn còn nó thì bắn."),
            ["guide.fpv_carrier"] = (
                "[[FPV drone carrier]] · light armour · tank hunter at long range\n" +
                "How it fights: stops and launches a swarm of four [[kamikaze drones]] that dive onto armour 12–75 m away; four swarms, then a reload.\n" +
                "Strong / weak: wrecks [[tanks]] and heavy tanks from afar; APS tanks, laser AA and jammers stop its drones, and turtle tanks shrug them off.\n" +
                "Tip: fire from behind your line at the enemy's heaviest tanks, well out of reach of their guns.",
                "[[Xe phóng drone FPV]] · giáp mỏng · diệt tăng tầm xa\n" +
                "Cách đánh: dừng lại rồi phóng bầy bốn [[drone cảm tử]] lao xuống xe bọc thép cách 12–75 m; bốn đợt rồi nạp lại.\n" +
                "Mạnh / yếu: phá nát [[xe tăng]] và tăng nặng từ xa; tăng APS, la-de phòng không và xe gây nhiễu chặn drone, xe tăng rùa gần như miễn nhiễm.\n" +
                "Mẹo: bắn từ sau tuyến ta vào xe tăng nặng nhất của địch, giữ ngoài tầm pháo của chúng."),
            ["guide.lancet_truck"] = (
                "[[Artillery hunter]] · light armour · long reach (85 m)\n" +
                "How it fights: stops and launches Lancet [[drones]] one at a time that fly up to 85 m and dive onto a target: [[double damage]] on artillery and on anything parked for 3 s; six, then a reload.\n" +
                "Strong / weak: made for [[artillery]], launchers and SAMs behind the line, and parked tanks; APS, laser AA and jammers stop its drones.\n" +
                "Tip: let scouts, a UAV scan or a counter-battery radar find the enemy's guns, then send the Lancets after them.",
                "[[Săn pháo binh]] · giáp mỏng · tầm với xa (85 m)\n" +
                "Cách đánh: dừng lại rồi phóng từng chiếc [[drone]] Lancet bay tới 85 m rồi lao xuống mục tiêu: [[gấp đôi sát thương]] lên pháo binh và mọi xe đứng yên quá 3 giây; sáu chiếc rồi nạp lại.\n" +
                "Mạnh / yếu: chuyên diệt [[pháo binh]], giàn phóng và tên lửa phòng không phía sau tuyến, cả xe tăng đứng yên; tăng APS, la-de phòng không và xe gây nhiễu chặn được drone.\n" +
                "Mẹo: cho trinh sát, UAV quét hoặc radar phản pháo tìm pháo địch trước, rồi thả Lancet săn chúng."),
            ["guide.railgun_truck"] = (
                "[[Railgun]] · light armour · very long range (90 m)\n" +
                "How it fights: stands still and [[charges]] for 0.9 s (the coils glow), then fires a slug that [[pierces]] every vehicle on its line, out to 90 m.\n" +
                "Strong / weak: cuts through lines of [[tanks]] and heavy tanks from far away; slow to fire, and anything that reaches it wins.\n" +
                "Tip: line it up on a road or a choke point where enemies come single file; give it spotters.",
                "[[Súng điện từ]] · giáp mỏng · tầm rất xa (90 m)\n" +
                "Cách đánh: đứng yên [[nạp năng lượng]] 0,9 giây (cuộn dây phát sáng), rồi bắn viên đạn [[xuyên thủng]] mọi xe trên đường bay, xa tới 90 m.\n" +
                "Mạnh / yếu: xuyên thủng cả hàng [[xe tăng]] và tăng nặng từ rất xa; bắn chậm, bị áp sát là thua.\n" +
                "Mẹo: ngắm dọc con đường hoặc cửa ải nơi địch đi thành hàng; cần đồng đội soi mục tiêu."),
            ["guide.vbied"] = (
                "[[Car bomb]] · welded armour · one-shot kamikaze\n" +
                "How it fights: races into the enemy and [[blows itself up]]: 700 damage over 7.5 m, [[half]] on towers and buildings. Shot on the way, it still explodes where it dies.\n" +
                "Strong / weak: wrecks artillery, support trucks and [[groups]] of light vehicles; fast guns and armoured cars stop it, and a base shrugs off a stream of them.\n" +
                "Tip: send it behind a tank push or through smoke so it reaches its target in one piece.",
                "[[Xe bom tự sát]] · giáp hàn · dùng một lần\n" +
                "Cách đánh: lao thẳng vào địch rồi [[tự nổ]]: 700 sát thương trong bán kính 7,5 m, [[một nửa]] lên tháp và công trình. Bị bắn hạ giữa đường thì nổ ngay tại chỗ.\n" +
                "Mạnh / yếu: phá nát pháo binh, xe hỗ trợ và [[cụm xe nhẹ]]; súng bắn nhanh và xe bọc thép chặn được nó, và căn cứ chịu được cả dòng xe bom.\n" +
                "Mẹo: cho chạy sau đợt xe tăng hoặc xuyên qua màn khói để tới mục tiêu nguyên vẹn."),

            // Artillery.
            ["guide.mortar_carrier"] = (
                "[[Mortar]] · light armour · cheap indirect fire (55 m)\n" +
                "How it fights: stops and lobs 120 mm [[high-explosive]] bombs over walls and houses; its sight is short, so it fires at what allies spot.\n" +
                "Strong / weak: good against [[towers]], tank hunters and armour standing still; helpless against anything that reaches it.\n" +
                "Tip: its minimum range is only 10 m, closer than the big guns; tuck it behind houses.",
                "[[Súng cối]] · giáp mỏng · hỏa lực cầu vồng giá rẻ (55 m)\n" +
                "Cách đánh: dừng lại rồi bắn đạn cối 120 mm [[nổ mạnh]] qua tường và nhà; tầm nhìn ngắn nên bắn vào mục tiêu đồng đội phát hiện.\n" +
                "Mạnh / yếu: tốt với [[tháp canh]], xe diệt tăng và thiết giáp đứng yên; bó tay khi bị áp sát.\n" +
                "Mẹo: tầm tối thiểu chỉ 10 m, gần hơn các pháo lớn; hãy nấp sau nhà cửa."),
            ["guide.artillery"] = (
                "[[Artillery]] · light armour · long range (90 m)\n" +
                "How it fights: stops, lobs three 155 mm [[high-explosive]] shells over cover, then [[moves 15-20 m]] before it fires again, so counter-battery fire lands on an empty spot; it cannot hit closer than 25 m.\n" +
                "Strong / weak: breaks towers, heavy tanks and tank hunters from afar, and on a [[marked]] target (a laser designator, a counter-battery radar, a UAV scan) its shells barely scatter; scouts, armoured cars and aircraft that reach it win easily.\n" +
                "Tip: pair it with a recon drone or a laser designator: marked targets are hit almost dead on.",
                "[[Pháo binh]] · giáp mỏng · tầm xa (90 m)\n" +
                "Cách đánh: dừng lại, nã ba quả đạn 155 mm [[nổ mạnh]] cầu vồng qua vật cản rồi [[dời 15–20 m]] mới bắn tiếp, nên đạn phản pháo rơi vào chỗ trống; không bắn được gần hơn 25 m.\n" +
                "Mạnh / yếu: phá công sự, tăng hạng nặng và xe diệt tăng từ xa, bắn mục tiêu [[bị đánh dấu]] (chỉ thị la-de, radar phản pháo, UAV quét) gần như không tản mát; trinh sát, xe bọc thép và máy bay áp sát là nó thua.\n" +
                "Mẹo: đi cùng UAV trinh sát hoặc chỉ thị la-de: mục tiêu bị đánh dấu trúng gần như tuyệt đối."),
            ["guide.rocket_technical"] = (
                "[[Rocket pickup]] · paper armour · cheap and fast\n" +
                "How it fights: stops and fires a loose [[salvo]] of eight rockets up to 48 m; six salvos, then it reloads standing still. A machine gun too.\n" +
                "Strong / weak: hits [[towers]] and groups on the cheap; it dies to almost any gun that reaches it.\n" +
                "Tip: it is fast and [[captures]] points at double speed: use it early, then keep it well back.",
                "[[Bán tải rốc-két]] · giáp mỏng như giấy · rẻ và nhanh\n" +
                "Cách đánh: dừng lại rồi phóng một [[loạt]] tám rốc-két khá tản mát tới 48 m; hết sáu loạt phải đứng yên nạp lại. Có thêm súng máy.\n" +
                "Mạnh / yếu: phá [[tháp canh]] và cụm địch với giá rẻ; chết trước gần như mọi khẩu súng với tới nó.\n" +
                "Mẹo: xe nhanh, [[chiếm cứ điểm]] nhanh gấp đôi: dùng sớm, sau đó giữ thật xa phía sau."),
            ["guide.mlrs"] = (
                "[[Rocket artillery]] · light armour · very long range (110 m)\n" +
                "How it fights: stops and fires an accurate [[salvo]] of six rockets from up to 110 m; after four salvos it must [[reload]] standing still.\n" +
                "Strong / weak: wrecks towers, heavy tanks and gun lines from beyond their reach; anything fast that gets close kills it.\n" +
                "Tip: aim it at clustered enemies or defences, with an engineer nearby to re-arm it faster.",
                "[[Pháo phản lực]] · giáp mỏng · tầm rất xa (110 m)\n" +
                "Cách đánh: dừng lại rồi phóng một [[loạt]] sáu rốc-két chính xác từ tới 110 m; sau bốn loạt phải đứng yên [[nạp đạn]].\n" +
                "Mạnh / yếu: phá công sự, tăng hạng nặng và trận địa pháo từ ngoài tầm với; bất kỳ xe nhanh nào áp sát cũng hạ được nó.\n" +
                "Mẹo: nhắm vào chỗ địch tụ đông hoặc công trình; để xe công binh gần đó giúp nạp đạn nhanh hơn."),
            ["guide.thermobaric_launcher"] = (
                "[[Thermobaric launcher]] · heavy armour · short-range area killer\n" +
                "How it fights: stops and fires twelve [[thermobaric]] rockets that blanket an area 12–38 m away; four salvos, then a reload standing still.\n" +
                "Strong / weak: wipes out [[groups]], towers and anything bunched up; it must get fairly close, and aircraft catch it easily.\n" +
                "Tip: its armour lets it follow the tanks: roll it up behind them and fire into the point the enemy holds.",
                "[[Pháo nhiệt áp]] · giáp dày · hủy diệt vùng ở tầm gần\n" +
                "Cách đánh: dừng lại rồi phóng 12 rốc-két [[nhiệt áp]] phủ kín một vùng cách 12–38 m; bốn loạt rồi phải đứng yên nạp lại.\n" +
                "Mạnh / yếu: quét sạch [[cụm địch]], tháp canh và mọi thứ đứng dồn; phải tiến khá gần, dễ bị máy bay bắt.\n" +
                "Mẹo: giáp đủ dày để đi sau xe tăng: tiến sát sau lưng chúng rồi nã vào cứ điểm địch đang giữ."),
            ["guide.heavy_rocket_artillery"] = (
                "[[Heavy rocket artillery]] · light armour · extreme range (140 m)\n" +
                "How it fights: stops and fires twelve 300 mm [[rockets]] 30–140 m away, with big blasts; three salvos, then a long reload in place.\n" +
                "Strong / weak: hits [[fortifications]], artillery and massed armour from across the map; defenceless if anything reaches it.\n" +
                "Tip: it outranges almost everything: keep it in your corner of the map and give it [[spotters]].",
                "[[Pháo phản lực hạng nặng]] · giáp mỏng · tầm cực xa (140 m)\n" +
                "Cách đánh: dừng lại rồi phóng 12 [[rốc-két]] 300 mm vào vùng cách 30–140 m, sức nổ lớn; ba loạt rồi nạp lại lâu tại chỗ.\n" +
                "Mạnh / yếu: đánh [[công sự]], pháo binh và cụm thiết giáp từ bên kia bản đồ; không có khả năng tự vệ khi bị áp sát.\n" +
                "Mẹo: bắn xa hơn gần như mọi thứ: giữ ở góc căn cứ và cho [[trinh sát]] soi mục tiêu."),
            ["guide.ballistic_launcher"] = (
                "[[Ballistic missile launcher]] · light armour · reaches almost the whole map\n" +
                "How it fights: stops and launches a pair of [[ballistic missiles]] at targets 40–180 m away, each a huge blast; two pairs, then a long reload.\n" +
                "Strong / weak: erases [[fortifications]], artillery parks and big groups; slow to fire and helpless up close.\n" +
                "Tip: save it for the biggest crowd of enemies or a key tower; allies must see the target first.",
                "[[Tên lửa đạn đạo]] · giáp mỏng · với gần hết bản đồ\n" +
                "Cách đánh: dừng lại rồi phóng một cặp [[tên lửa đạn đạo]] vào mục tiêu cách 40–180 m, mỗi quả nổ cực lớn; hai cặp rồi nạp lại lâu.\n" +
                "Mạnh / yếu: xóa sổ [[công sự]], trận địa pháo và cụm quân đông; bắn chậm và bó tay khi bị áp sát.\n" +
                "Mẹo: để dành cho cụm địch đông nhất hoặc tháp quan trọng; đồng đội phải thấy mục tiêu trước."),
            ["guide.shahed_truck"] = (
                "[[Shahed launcher]] · light armour · strikes across the map (150 m)\n" +
                "How it fights: stops and sends five slow [[kamikaze drones]] up to 150 m away, best at [[structures]]; one salvo, then a long reload.\n" +
                "Strong / weak: breaks towers, turrets and parked artillery far away; APS and laser AA shoot the slow drones down, jammers throw them off.\n" +
                "Tip: in Siege mode, aim it at the towers your tanks cannot reach yet.",
                "[[Xe phóng Shahed]] · giáp mỏng · đánh khắp bản đồ (150 m)\n" +
                "Cách đánh: dừng lại rồi phóng năm [[drone cảm tử]] bay chậm xa tới 150 m, chuyên đánh [[công trình]]; một loạt rồi nạp lại lâu.\n" +
                "Mạnh / yếu: phá tháp canh, ụ pháo và pháo binh đứng yên ở xa; APS và la-de phòng không bắn hạ drone chậm, xe gây nhiễu làm chúng lạc.\n" +
                "Mẹo: ở chế độ Công thành, nhắm vào những tháp mà xe tăng ta chưa với tới."),

            // Air defence.
            ["guide.zu23_technical"] = (
                "[[Cheap anti-air]] · paper armour · fast pickup\n" +
                "How it fights: a twin 23 mm [[flak]] gun fired on the move at aircraft and light ground targets (32 m); [[captures]] points at double speed.\n" +
                "Strong / weak: tears up [[helicopters]], drones and scouts; tanks and armoured cars kill it in seconds.\n" +
                "Tip: an early, cheap answer to enemy helicopters; buy a proper AA vehicle later.",
                "[[Phòng không giá rẻ]] · giáp mỏng như giấy · bán tải nhanh\n" +
                "Cách đánh: pháo đôi 23 mm [[cao xạ]] vừa chạy vừa bắn máy bay và xe nhẹ (32 m); [[chiếm cứ điểm]] nhanh gấp đôi.\n" +
                "Mạnh / yếu: xé nát [[trực thăng]], drone và trinh sát; xe tăng và xe bọc thép hạ nó trong vài giây.\n" +
                "Mẹo: đối sách rẻ và sớm trước trực thăng địch; về sau hãy mua xe phòng không thật sự."),
            ["guide.aa_vehicle"] = (
                "[[Anti-air]] · light armour · guns and a missile\n" +
                "How it fights: twin 35 mm [[flak]] guns (36 m) fired on the move, and a short-range [[missile]] (44 m) that only goes for aircraft.\n" +
                "Strong / weak: tears apart [[helicopters]], drones and jets; its flak barely scratches armour, so tanks and armoured cars beat it.\n" +
                "Tip: keep one with every tank group: cheap insurance against enemy helicopters.",
                "[[Phòng không]] · giáp mỏng · pháo và tên lửa\n" +
                "Cách đánh: pháo đôi 35 mm [[cao xạ]] (36 m) bắn khi đang chạy, kèm [[tên lửa]] tầm ngắn (44 m) chỉ nhắm máy bay.\n" +
                "Mạnh / yếu: xé nát [[trực thăng]], drone và máy bay phản lực; đạn cao xạ gần như vô hại với giáp nên thua xe tăng và xe bọc thép.\n" +
                "Mẹo: kèm một chiếc với mỗi cụm xe tăng: rẻ mà chặn được trực thăng địch."),
            ["guide.heavy_aa"] = (
                "[[Gun-missile air defence]] · light armour · fires on the move\n" +
                "How it fights: four 30 mm [[flak]] barrels (42 m) and anti-air [[missiles]] (44 m), fired on the move; its 60 m sight spots aircraft early.\n" +
                "Strong / weak: the best mobile shield against [[helicopters]] and jets; tanks and armoured cars beat it on the ground.\n" +
                "Tip: move it with the main group, so helicopters and attack jets never get a free run.",
                "[[Pháo tên lửa phòng không]] · giáp mỏng · vừa chạy vừa bắn\n" +
                "Cách đánh: bốn nòng 30 mm [[cao xạ]] (42 m) và [[tên lửa]] phòng không (44 m), bắn cả khi đang chạy; tầm nhìn 60 m thấy máy bay từ sớm.\n" +
                "Mạnh / yếu: lá chắn di động tốt nhất trước [[trực thăng]] và máy bay; trên mặt đất thua xe tăng và xe bọc thép.\n" +
                "Mẹo: cho đi cùng đội hình chính để trực thăng và cường kích địch không được tự do tấn công."),
            ["guide.sam_launcher"] = (
                "[[SAM launcher]] · light armour · long-range air defence (55 m)\n" +
                "How it fights: stops and fires [[missiles]] in pairs at [[aircraft]] up to 55 m away; only a roof machine gun for the ground.\n" +
                "Strong / weak: swats helicopters, jets and bombers far out, even the Ka-52; tanks and armoured cars that reach it win easily.\n" +
                "Tip: park it behind the front line: one launcher covers a wide piece of sky.",
                "[[Tên lửa phòng không]] · giáp mỏng · tầm xa (55 m)\n" +
                "Cách đánh: dừng lại rồi phóng [[tên lửa]] từng cặp vào [[máy bay]] cách tới 55 m; chỉ có súng máy nóc để đánh mặt đất.\n" +
                "Mạnh / yếu: bắn rụng trực thăng, máy bay phản lực và oanh tạc cơ từ xa, kể cả Ka-52; xe tăng, xe bọc thép áp sát là nó thua.\n" +
                "Mẹo: đặt sau tuyến đầu: một bệ phóng che được cả một vùng trời rộng."),
            ["guide.iron_beam"] = (
                "[[Point defence laser]] · light armour · shoots rounds down\n" +
                "How it fights: its [[laser]] burns down one drone, missile or rocket (artillery rockets too) aimed within 30 m of it every 1.2 s; between them it fires at aircraft (45 m).\n" +
                "Strong / weak: shields a group from ATGMs, Lancets, rocket artillery and helicopter missiles; shells and bullets pass, and it has nothing for the ground.\n" +
                "Tip: park it in the middle of your tanks when the enemy relies on missiles, drones or rockets.",
                "[[La-de phòng thủ điểm]] · giáp mỏng · bắn hạ đạn bay tới\n" +
                "Cách đánh: tia [[la-de]] đốt hạ một drone, tên lửa hoặc rốc-két (cả rốc-két pháo binh) nhắm vào trong vòng 30 m quanh nó, cứ 1,2 giây một quả; giữa các lần đó nó bắn máy bay (45 m).\n" +
                "Mạnh / yếu: che cả cụm quân khỏi tên lửa chống tăng, Lancet, pháo phản lực và tên lửa trực thăng; đạn pháo và đạn súng bay qua được, và nó không có gì đánh mặt đất.\n" +
                "Mẹo: đỗ giữa đội xe tăng khi địch dựa vào tên lửa, drone hoặc rốc-két."),

            // Support vehicles.
            ["guide.engineer_vehicle"] = (
                "[[Engineer]] · heavy armour · repairs and re-arms\n" +
                "How it fights: only a roof MG; it [[repairs]] friendly vehicles within 14 m (2.5% health a second) and [[re-arms]] their launchers.\n" +
                "Strong / weak: keeps a tank line alive much longer; alone it fights poorly, and scouts or armoured cars pick it off.\n" +
                "Tip: park it just behind the front, or beside rocket artillery so empty launchers reload faster.",
                "[[Xe công binh]] · giáp dày · sửa chữa và tiếp đạn\n" +
                "Cách đánh: chỉ có súng máy nóc; [[sửa chữa]] xe ta trong vòng 14 m (2,5% máu mỗi giây) và [[tiếp đạn]] cho bệ phóng.\n" +
                "Mạnh / yếu: giúp tuyến xe tăng trụ lâu hơn hẳn; tự đánh thì yếu, trinh sát và xe bọc thép dễ bắt nạt nó.\n" +
                "Mẹo: đỗ ngay sau tuyến đầu, hoặc cạnh pháo phản lực để bệ phóng hết đạn nạp lại nhanh hơn."),
            ["guide.sapper"] = (
                "[[Fortification sapper]] · heavy armour · repairs defences\n" +
                "How it fights: a roof MG; it slowly [[repairs]] friendly towers, turrets and bunkers within 12 m (0.6% health a second). It cannot fix vehicles.\n" +
                "Strong / weak: keeps your [[defences]] standing when you hold a line; on its own it beats nothing.\n" +
                "Tip: park it among the towers you hold; to repair vehicles, bring an engineer instead.",
                "[[Công binh công trình]] · giáp dày · sửa công sự\n" +
                "Cách đánh: có súng máy nóc; [[sửa chữa]] chậm tháp, ụ pháo và lô cốt phe ta trong vòng 12 m (0,6% máu mỗi giây). Không sửa được xe.\n" +
                "Mạnh / yếu: giữ [[công sự]] phe ta đứng vững khi phòng thủ; tự đánh thì không thắng được ai.\n" +
                "Mẹo: đỗ giữa các tháp ta đang giữ; muốn sửa xe thì mang xe công binh."),
            ["guide.ew_jammer"] = (
                "[[EW jammer]] · light armour · scrambles guided weapons\n" +
                "How it fights: a roof MG only; enemy guided [[missiles]], drones and fire support aimed into its 32 m [[jamming]] bubble go wide.\n" +
                "Strong / weak: counters ATGM carriers, drone trucks, attack helicopters and enemy strikes; useless against guns and shells.\n" +
                "Tip: keep it in the middle of your army against missile- and drone-heavy enemies.",
                "[[Tác chiến điện tử]] · giáp mỏng · gây nhiễu vũ khí dẫn đường\n" +
                "Cách đánh: chỉ có súng máy nóc; [[tên lửa]], drone và hỏa lực yểm trợ của địch nhắm vào vùng [[gây nhiễu]] 32 m đều bị lệch.\n" +
                "Mạnh / yếu: khắc chế xe tên lửa chống tăng, xe drone, trực thăng và đòn yểm trợ địch; vô dụng trước súng và đạn pháo thường.\n" +
                "Mẹo: giữ ở giữa đội hình khi địch dùng nhiều tên lửa và drone."),
            ["guide.mine_layer"] = (
                "[[Mine layer]] · light armour · area denial\n" +
                "How it fights: a roof MG; as it drives it drops an [[anti-tank mine]] every 6 s (up to 8), and enemy vehicles that roll over one blow up.\n" +
                "Strong / weak: punishes [[tanks]] and columns that keep to one road; turtle tanks' rollers clear mines, and aircraft ignore them.\n" +
                "Tip: drive it back and forth across the lane the enemy uses, or round your objective.",
                "[[Xe rải mìn]] · giáp mỏng · khóa khu vực\n" +
                "Cách đánh: có súng máy nóc; khi chạy, cứ 6 giây thả một quả [[mìn chống tăng]] (tối đa 8), xe địch cán phải là nổ tung.\n" +
                "Mạnh / yếu: trừng phạt [[xe tăng]] và đoàn xe đi theo một lối; xe tăng rùa có trục lăn phá mìn, máy bay thì không sợ.\n" +
                "Mẹo: chạy qua lại trên con đường địch hay đi, hoặc quanh cứ điểm của ta."),
            ["guide.smoke_carrier"] = (
                "[[Smoke carrier]] · light armour · hides the army\n" +
                "How it fights: a roof MG; whenever an enemy is in range it lays an 11 m [[smoke]] cloud round itself that no one can see through.\n" +
                "Strong / weak: shields tanks and slow vehicles as they close in on [[long-range guns]]; it fights poorly itself.\n" +
                "Tip: lead a push with it towards tank destroyers or ATGM carriers so your tanks get close.",
                "[[Xe tạo khói]] · giáp mỏng · che giấu đội quân\n" +
                "Cách đánh: có súng máy nóc; mỗi khi địch trong tầm, nó phủ [[màn khói]] 11 m quanh mình, không ai nhìn xuyên qua được.\n" +
                "Mạnh / yếu: che chở xe tăng và xe chậm khi áp sát [[pháo tầm xa]] của địch; tự nó đánh rất yếu.\n" +
                "Mẹo: cho chạy đầu đội hình khi tiến vào xe diệt tăng hoặc xe tên lửa chống tăng để xe tăng ta áp sát được."),

            // Helicopters.
            ["guide.scout_heli"] = (
                "[[Scout helicopter]] · very fast · fragile\n" +
                "How it fights: darts in with [[miniguns]] (short range, can hit aircraft too) and a seven-rocket pod; its sharp eyes [[spot]] for the army.\n" +
                "Strong / weak: shreds scouts, [[light vehicles]] and support trucks; tanks shrug it off, and any AA kills it quickly.\n" +
                "Tip: use it to hunt enemy support trucks and artillery behind their lines, away from AA.",
                "[[Trực thăng trinh sát]] · rất nhanh · mong manh\n" +
                "Cách đánh: lao vào với [[súng máy nhiều nòng]] (tầm gần, bắn được cả máy bay) và giàn 7 rốc-két; mắt tinh giúp [[soi mục tiêu]] cho cả quân.\n" +
                "Mạnh / yếu: xé nát trinh sát, [[xe nhẹ]] và xe hỗ trợ; xe tăng gần như miễn nhiễm, gặp phòng không là rụng nhanh.\n" +
                "Mẹo: dùng để săn xe hỗ trợ và pháo binh sau lưng địch, tránh xa phòng không."),
            ["guide.attack_helicopter"] = (
                "[[Attack helicopter]] · flying · tank killer\n" +
                "How it fights: hovers, firing Hellfire [[anti-tank missiles]] at armour, a 30 mm gun and rockets at the rest, two Stingers at aircraft; [[flares]].\n" +
                "Strong / weak: kills [[tanks]], heavy tanks and artillery that have no AA cover; AA vehicles and fighters bring it down fast.\n" +
                "Tip: send it where enemy AA is dead or busy, and pull it back the moment flak hits it.",
                "[[Trực thăng tấn công]] · bay · sát thủ diệt tăng\n" +
                "Cách đánh: bay treo, phóng Hellfire [[chống tăng]] vào giáp dày, pháo 30 mm và rốc-két cho mục tiêu khác, 2 Stinger bắn máy bay; có [[mồi nhiệt]].\n" +
                "Mạnh / yếu: diệt [[xe tăng]], tăng nặng và pháo binh không có phòng không che; xe phòng không và tiêm kích hạ nó rất nhanh.\n" +
                "Mẹo: đưa vào nơi phòng không địch đã bị diệt hoặc đang bận, rút ngay khi dính đạn cao xạ."),
            ["guide.gunship_heli"] = (
                "[[Flying IFV]] · heavy helicopter · can take objectives\n" +
                "How it fights: opens with big [[rocket]] salvos, then a fixed 30 mm cannon and ATGMs; [[door gunners]] fire out of both sides. Drops flares.\n" +
                "Strong / weak: wrecks light vehicles, scouts and towers; AA vehicles and fighters are its danger, but it takes a lot to bring down.\n" +
                "Tip: the only helicopter that [[captures]] points: send it to grab an undefended objective across the map.",
                "[[Xe bộ binh bay]] · trực thăng hạng nặng · chiếm được cứ điểm\n" +
                "Cách đánh: mở màn bằng loạt [[rốc-két]] lớn, rồi pháo 30 mm cố định và tên lửa chống tăng; [[xạ thủ]] bắn từ hai cửa hông. Có mồi nhiệt.\n" +
                "Mạnh / yếu: phá nát xe nhẹ, trinh sát và tháp canh; sợ xe phòng không và tiêm kích, nhưng rất lì đòn.\n" +
                "Mẹo: trực thăng duy nhất [[chiếm được cứ điểm]]: đưa nó đi chiếm điểm trống ở xa bên kia bản đồ."),
            ["guide.heavy_attack_heli"] = (
                "[[Stand-off sniper]] · heavy attack helicopter · long range (55 m)\n" +
                "How it fights: [[Vikhr]] missiles in pairs from 55 m at armour and at [[helicopters]]; it hovers at the edge of that reach, round the side away from short-range anti-air; a side 30 mm and S-8 rockets up close.\n" +
                "Strong / weak: kills tanks and heavy tanks from outside the reach of flak and short-range SAMs; long-range SAMs, the Patriot and fighters outrange it.\n" +
                "Tip: it keeps its own distance: pair it with something that deals with long-range SAMs (a SEAD strike, artillery).",
                "[[Bắn tỉa từ xa]] · trực thăng tấn công hạng nặng · tầm xa (55 m)\n" +
                "Cách đánh: tên lửa [[Vikhr]] bắn cặp từ 55 m vào thiết giáp và cả [[trực thăng]]; nó treo ở rìa tầm đó, vòng sang phía tránh phòng không tầm ngắn; pháo 30 mm hông và rốc-két S-8 khi gần.\n" +
                "Mạnh / yếu: hạ xe tăng, tăng nặng từ ngoài tầm của pháo cao xạ và tên lửa tầm ngắn; tên lửa phòng không tầm xa, Patriot và tiêm kích bắn xa hơn nó.\n" +
                "Mẹo: nó tự giữ khoảng cách: đi kèm thứ xử lý được tên lửa tầm xa (đòn SEAD, pháo binh)."),

            // Fixed-wing aircraft and drones.
            ["guide.recon_drone"] = (
                "[[Recon drone]] · flying · the longest sight in the game\n" +
                "How it fights: flies high with a 90 m sight, [[spotting]] targets for the whole army, and a light guided [[missile]] (50 m) for ground targets.\n" +
                "Strong / weak: picks off scouts and artillery, and lets your big guns fire at full range; fragile, any AA or fighter kills it.\n" +
                "Tip: pair it with howitzers, rocket artillery or ballistic missiles so they can hit what they cannot see.",
                "[[UAV trinh sát]] · bay · tầm nhìn xa nhất trò chơi\n" +
                "Cách đánh: bay cao với tầm nhìn 90 m, [[soi mục tiêu]] cho cả đội quân, kèm một [[tên lửa]] dẫn đường nhẹ (50 m) đánh mặt đất.\n" +
                "Mạnh / yếu: bắn tỉa trinh sát và pháo binh, giúp pháo ta bắn hết tầm; mong manh, gặp phòng không hay tiêm kích là rơi.\n" +
                "Mẹo: kết hợp với lựu pháo, pháo phản lực hoặc tên lửa đạn đạo để chúng bắn trúng thứ chúng không tự thấy."),
            ["guide.strike_drone"] = (
                "[[Strike drone]] · flying · long sight\n" +
                "How it fights: flies high, firing Hellfire [[missiles]] from 48 m and four [[guided bombs]]; it has no weapon against aircraft.\n" +
                "Strong / weak: picks off tanks, heavy tanks and artillery; slow and fragile, it falls to any AA or fighter.\n" +
                "Tip: its 62 m sight also makes it a [[spotter]] for your artillery; keep it clear of enemy SAMs.",
                "[[UAV tấn công]] · bay · nhìn xa\n" +
                "Cách đánh: bay cao, phóng [[tên lửa]] Hellfire từ 48 m và bốn quả [[bom dẫn đường]]; không có vũ khí chống máy bay.\n" +
                "Mạnh / yếu: bắn tỉa xe tăng, tăng nặng và pháo binh; chậm và mỏng, gặp phòng không hay tiêm kích là rơi.\n" +
                "Mẹo: tầm nhìn 62 m biến nó thành [[trinh sát]] cho pháo binh; tránh xa tên lửa phòng không địch."),
            ["guide.fighter_jet"] = (
                "[[Fighter]] · the fastest aircraft · hunts aircraft\n" +
                "How it fights: [[air-to-air missiles]] from 60 m, dogfight missiles, a cannon; it [[intercepts]] aircraft far from its post and can hover to fire.\n" +
                "Strong / weak: the counter to [[helicopters]], bombers, gunships and jets; almost harmless to ground units, and SAMs still kill it.\n" +
                "Tip: buy one as soon as the enemy puts anything in the air; it clears the sky for your own aircraft.",
                "[[Tiêm kích]] · máy bay nhanh nhất · săn máy bay\n" +
                "Cách đánh: [[tên lửa không đối không]] từ 60 m, tên lửa cận chiến và pháo; [[đánh chặn]] máy bay địch ở xa vị trí gác, có thể lơ lửng để bắn.\n" +
                "Mạnh / yếu: khắc tinh của [[trực thăng]], oanh tạc cơ và mọi máy bay; gần như vô hại với mặt đất, vẫn sợ tên lửa phòng không.\n" +
                "Mẹo: mua ngay khi địch đưa bất cứ thứ gì lên trời; nó dọn sạch bầu trời cho máy bay của ta."),
            ["guide.attack_jet"] = (
                "[[Ground-attack jet]] · fast · not a fighter\n" +
                "How it fights: makes [[strafing runs]] with its cannon, 20-rocket pods and two heavy [[bombs]]; two R-60s only for self-defence against aircraft.\n" +
                "Strong / weak: smashes light vehicles, tanks, artillery and [[towers]]; AA vehicles, SAMs and enemy fighters kill it.\n" +
                "Tip: to clear the sky buy a fighter jet; send the Su-25 at ground targets once enemy AA is thinned out.",
                "[[Cường kích]] · nhanh · không phải tiêm kích\n" +
                "Cách đánh: bổ nhào [[càn quét]] bằng pháo, giàn 20 rốc-két và hai quả [[bom]] nặng; hai tên lửa R-60 chỉ để tự vệ trước máy bay.\n" +
                "Mạnh / yếu: đập nát xe nhẹ, xe tăng, pháo binh và [[công sự]]; sợ xe phòng không, tên lửa phòng không và tiêm kích địch.\n" +
                "Mẹo: muốn giành bầu trời hãy mua tiêm kích; Su-25 chỉ nên đánh mặt đất khi phòng không địch đã thưa."),
            ["guide.tank_buster"] = (
                "[[Tank buster]] · armoured jet · gun runs\n" +
                "How it fights: dives in [[gun runs]] with the 30 mm GAU-8, fires Maverick [[missiles]] from 40 m and rockets; two AIM-9s only for self-defence.\n" +
                "Strong / weak: shreds [[tanks]], heavy tanks and light vehicles; tougher than other jets, but AA and fighters still bring it down.\n" +
                "Tip: send it at the enemy's armour push; bring a fighter along if they have aircraft.",
                "[[Cường kích diệt tăng]] · máy bay bọc giáp · bổ nhào xả pháo\n" +
                "Cách đánh: bổ nhào [[xả pháo]] GAU-8 30 mm, phóng [[tên lửa]] Maverick từ 40 m và rốc-két; hai AIM-9 chỉ để tự vệ.\n" +
                "Mạnh / yếu: xé nát [[xe tăng]], tăng nặng và xe nhẹ; lì hơn máy bay khác, nhưng phòng không và tiêm kích vẫn hạ được.\n" +
                "Mẹo: tung vào mũi tiến công thiết giáp của địch; mang thêm tiêm kích nếu địch có máy bay."),
            ["guide.heavy_bomber"] = (
                "[[Heavy bomber]] · flying · carpet of bombs\n" +
                "How it fights: flies over and lays a line of twelve heavy [[bombs]]; fires [[cruise missiles]] from 110 m; tail guns shoot at aircraft.\n" +
                "Strong / weak: flattens [[towers]], artillery and groups of light vehicles; SAMs and fighters are its danger.\n" +
                "Tip: send it at enemy defences and gun lines once your fighters or AA have cleared the sky.",
                "[[Oanh tạc cơ]] · bay · rải thảm bom\n" +
                "Cách đánh: bay qua và thả một hàng 12 quả [[bom]] nặng; phóng [[tên lửa hành trình]] từ 110 m; súng đuôi bắn máy bay.\n" +
                "Mạnh / yếu: san phẳng [[công sự]], pháo binh và cụm xe nhẹ; sợ tên lửa phòng không và tiêm kích.\n" +
                "Mẹo: tung vào công sự và trận địa pháo địch sau khi tiêm kích hoặc phòng không ta đã dọn sạch bầu trời."),
            ["guide.stealth_bomber"] = (
                "[[Stealth bomber]] · flying · hard to see\n" +
                "How it fights: three huge [[bombs]] per pass and JASSM missiles from 90 m; [[stealth]]: seen only close up, or just after it fires.\n" +
                "Strong / weak: destroys [[fortifications]], heavy tanks and artillery; once spotted, SAMs and fighters can still kill it.\n" +
                "Tip: use it on the enemy's best-defended point, where other aircraft would be shot down.",
                "[[Máy bay tàng hình]] · bay · khó phát hiện\n" +
                "Cách đánh: mỗi lượt thả ba quả [[bom]] cực lớn, phóng tên lửa JASSM từ 90 m; [[tàng hình]]: chỉ bị thấy ở gần hoặc ngay sau khi bắn.\n" +
                "Mạnh / yếu: phá hủy [[công sự]], tăng hạng nặng và pháo binh; một khi lộ diện, tên lửa phòng không và tiêm kích vẫn hạ được.\n" +
                "Mẹo: dùng đánh vào cứ điểm phòng thủ mạnh nhất của địch, nơi máy bay khác sẽ bị bắn rơi."),
            ["guide.sky_gunship"] = (
                "[[Sky gunship]] · flying · circles its target\n" +
                "How it fights: [[orbits]] its target, firing 105, 40 and 25 mm guns out of its left side from 50–58 m, plus Griffin missiles.\n" +
                "Strong / weak: grinds down [[light vehicles]], tanks and artillery; it cannot hit aircraft, so SAMs and fighters are its bane.\n" +
                "Tip: call it over a big ground fight after your AA or fighters have dealt with the enemy's.",
                "[[Pháo đài bay]] · bay · lượn vòng quanh mục tiêu\n" +
                "Cách đánh: [[bay vòng]] quanh mục tiêu, pháo 105, 40 và 25 mm bắn từ bên trái ở tầm 50–58 m, kèm tên lửa Griffin.\n" +
                "Mạnh / yếu: nghiền nát [[xe nhẹ]], xe tăng và pháo binh; không bắn được máy bay nên sợ tên lửa phòng không và tiêm kích.\n" +
                "Mẹo: đưa vào trận đánh lớn trên mặt đất sau khi phòng không hoặc tiêm kích ta đã xử lý phòng không địch."),

            // Elite enemy variants (never bought): tips on beating them.
            ["guide.elite_mbt"] = (
                "[[Elite battle tank]] · enemy only · tougher, with skills\n" +
                "How it fights: a 125 mm gun that hits a quarter harder than a battle tank's, with 60% more health; under fire it raises a [[shield]] (30% less damage for 5 s).\n" +
                "Strong / weak: beats battle tanks and light vehicles one on one; tank hunters and helicopters bring it down.\n" +
                "Tip: its shield lasts 5 s and needs 20 s to come back: let it fade, then hit hard with [[tank hunters]].",
                "[[Tăng chủ lực tinh nhuệ]] · chỉ phe địch · lì hơn, có kỹ năng\n" +
                "Cách đánh: pháo 125 mm đánh đau hơn tăng chủ lực một phần tư, máu nhiều hơn 60%; khi bị bắn thì bật [[khiên]] (giảm 30% sát thương trong 5 giây).\n" +
                "Mạnh / yếu: thắng tăng chủ lực và xe nhẹ khi đấu tay đôi; xe diệt tăng và trực thăng hạ được nó.\n" +
                "Mẹo: khiên chỉ kéo dài 5 giây và 20 giây mới có lại: chờ khiên tắt rồi dồn hỏa lực [[xe diệt tăng]]."),
            ["guide.elite_heavy_tank"] = (
                "[[Elite heavy tank]] · enemy only · very tough\n" +
                "How it fights: a 152 mm gun with a big blast, a quarter harder-hitting, with 60% more health; with a target in range it goes into [[overdrive]] (faster, firing faster, for 6 s).\n" +
                "Strong / weak: crushes battle tanks, light vehicles and towers; tank hunters, artillery and aircraft are how you kill it.\n" +
                "Tip: meet its overdrive from out of its reach (tank destroyers at 40 m, artillery), then close in once it has spent it.",
                "[[Tăng hạng nặng tinh nhuệ]] · chỉ phe địch · cực lì\n" +
                "Cách đánh: pháo 152 mm sức nổ lớn, đánh đau hơn một phần tư, máu nhiều hơn 60%; có mục tiêu trong tầm là [[tăng tốc]] (chạy nhanh, bắn dồn trong 6 giây).\n" +
                "Mạnh / yếu: nghiền nát tăng chủ lực, xe nhẹ và tháp canh; muốn hạ phải dùng xe diệt tăng, pháo binh và máy bay.\n" +
                "Mẹo: đón đợt tăng tốc của nó từ ngoài tầm (xe diệt tăng bắn 40 m, pháo binh), rồi áp sát khi nó đã dùng xong."),
            ["guide.elite_tank_destroyer"] = (
                "[[Elite tank destroyer]] · enemy only · outranges every tank (46 m)\n" +
                "How it fights: a 105 mm gun that hits from 46 m; with a target in range it fires a rapid [[barrage]] (2.2× rate), and pops [[smoke]] when hurt.\n" +
                "Strong / weak: deadly to tanks and heavy tanks; artillery, aircraft and fast light vehicles that close in beat it.\n" +
                "Tip: don't drive tanks straight at it; hit it with artillery or a helicopter, or rush it with armoured cars.",
                "[[Pháo chống tăng tinh nhuệ]] · chỉ phe địch · bắn xa hơn mọi xe tăng (46 m)\n" +
                "Cách đánh: pháo 105 mm bắn từ 46 m; có mục tiêu trong tầm là [[bắn dồn dập]] (nhanh gấp 2,2 lần), bị thương thì thả [[khói]].\n" +
                "Mạnh / yếu: cực nguy hiểm với xe tăng và tăng nặng; thua pháo binh, máy bay và xe nhẹ nhanh áp sát.\n" +
                "Mẹo: đừng cho xe tăng lao thẳng vào nó; dùng pháo binh, trực thăng hoặc xe bọc thép đánh áp sát."),
            ["guide.elite_attack_helicopter"] = (
                "[[Elite attack helicopter]] · enemy only · paired Hellfires\n" +
                "How it fights: Hellfire [[missiles]] in pairs at armour, plus a gun, rockets and Stingers; long-lasting [[flares]], and a rapid barrage in range.\n" +
                "Strong / weak: hunts tanks, heavy tanks and artillery; AA vehicles, SAMs and fighters kill it.\n" +
                "Tip: flares only fool missiles: [[flak]] guns (AA vehicle, Tunguska) are the surest answer.",
                "[[Trực thăng tinh nhuệ]] · chỉ phe địch · Hellfire bắn cặp\n" +
                "Cách đánh: phóng [[tên lửa]] Hellfire từng cặp vào thiết giáp, kèm pháo, rốc-két và Stinger; [[mồi nhiệt]] lâu hơn, bắn dồn dập khi có mục tiêu.\n" +
                "Mạnh / yếu: săn xe tăng, tăng nặng và pháo binh; thua xe phòng không, tên lửa phòng không và tiêm kích.\n" +
                "Mẹo: mồi nhiệt chỉ lừa được tên lửa: pháo [[cao xạ]] (xe phòng không, Tunguska) chắc ăn hơn cả."),
            ["guide.elite_mlrs"] = (
                "[[Elite rocket launcher]] · enemy only · cluster rockets\n" +
                "How it fights: stops and fires sixteen [[cluster rockets]] 20–75 m out, each scattering five bomblets; a rapid [[barrage]] with targets in range.\n" +
                "Strong / weak: carpets groups of light vehicles, towers and artillery; defenceless against anything that reaches it.\n" +
                "Tip: spread your vehicles out, then send scouts, armoured cars or aircraft straight at it.",
                "[[Pháo phản lực tinh nhuệ]] · chỉ phe địch · rốc-két chùm\n" +
                "Cách đánh: dừng lại rồi phóng 16 [[rốc-két chùm]] cách 20–75 m, mỗi quả tung năm bom con; [[bắn dồn dập]] khi có mục tiêu trong tầm.\n" +
                "Mạnh / yếu: rải thảm cụm xe nhẹ, tháp canh và pháo binh; không tự vệ được trước bất cứ thứ gì áp sát.\n" +
                "Mẹo: dàn quân ra, rồi tung trinh sát, xe bọc thép hoặc máy bay đánh thẳng vào nó."),
            ["guide.elite_grad"] = (
                "[[Elite Grad]] · enemy only · cluster salvo (78 m)\n" +
                "How it fights: stops and fires sixteen [[cluster rockets]] 18–78 m out, each scattering four bomblets; a faster [[barrage]] with targets in range.\n" +
                "Strong / weak: saturates groups of light vehicles, towers and artillery; weak against tanks and helpless up close.\n" +
                "Tip: never bunch up inside its range; rush it with fast vehicles or aircraft.",
                "[[Grad tinh nhuệ]] · chỉ phe địch · loạt rốc-két chùm (78 m)\n" +
                "Cách đánh: dừng lại rồi phóng dồn 16 [[rốc-két chùm]] cách 18–78 m, mỗi quả tung bốn bom con; [[bắn dồn dập]] khi có mục tiêu.\n" +
                "Mạnh / yếu: phủ kín cụm xe nhẹ, tháp canh và pháo binh; yếu với xe tăng và bó tay khi bị áp sát.\n" +
                "Mẹo: đừng bao giờ đứng dồn cục trong tầm của nó; tung xe nhanh hoặc máy bay đánh thẳng vào."),
            ["guide.elite_aa"] = (
                "[[Elite anti-air]] · enemy only · airburst flak (46 m)\n" +
                "How it fights: twin 35 mm [[airburst]] guns with a wide blast out to 46 m, plus a missile; it goes into [[overdrive]] with targets in range.\n" +
                "Strong / weak: shreds helicopters, jets and drones; its flak barely hurts armour, so tanks and armoured cars beat it.\n" +
                "Tip: keep your aircraft away until tanks or artillery have killed it.",
                "[[Phòng không tinh nhuệ]] · chỉ phe địch · đạn nổ trên không (46 m)\n" +
                "Cách đánh: pháo đôi 35 mm [[nổ trên không]] lan rộng, tầm 46 m, kèm tên lửa; [[tăng tốc]] bắn dồn khi có mục tiêu trong tầm.\n" +
                "Mạnh / yếu: xé nát trực thăng, máy bay phản lực và drone; đạn cao xạ gần như vô hại với giáp nên thua xe tăng, xe bọc thép.\n" +
                "Mẹo: giữ máy bay ta tránh xa cho tới khi xe tăng hoặc pháo binh hạ được nó."),
            ["guide.elite_apc"] = (
                "[[Elite EW carrier]] · enemy only · stuns with EMP\n" +
                "How it fights: the IFV's autocannon and anti-tank missile, a quarter harder-hitting; enemies within 14 m get hit by an [[EMP]] that [[stuns]] them for 3.5 s.\n" +
                "Strong / weak: beats light vehicles, scouts and AA, and its missiles hurt tanks; massed tanks and tank hunters beat it.\n" +
                "Tip: fight it from beyond 14 m (tank destroyers, artillery, aircraft) so the EMP never reaches you.",
                "[[Xe bọc thép tinh nhuệ]] · chỉ phe địch · gây choáng bằng EMP\n" +
                "Cách đánh: pháo tự động và tên lửa chống tăng của xe chiến đấu bộ binh, đánh đau hơn một phần tư; địch vào trong 14 m là dính [[EMP]], bị [[choáng]] 3,5 giây.\n" +
                "Mạnh / yếu: thắng xe nhẹ, trinh sát và phòng không, tên lửa còn hại được xe tăng; thua cụm xe tăng đông và xe diệt tăng.\n" +
                "Mẹo: đánh từ ngoài 14 m (xe diệt tăng, pháo binh, máy bay) để EMP không chạm tới quân ta."),
            // Prompt 8 H.2: elites of cards that had none (the base card's model in dark armour and gold trim).
            ["guide.elite_fpv_carrier"] = (
                "[[Elite FPV carrier]] · enemy only · drone swarms, faster\n" +
                "How it fights: the FPV carrier's [[kamikaze drones]] 12–75 m out, a tenth harder-hitting, with 60% more health; with armour in range it launches in a rapid [[barrage]] (2.2× rate for 6 s).\n" +
                "Strong / weak: wrecks tanks and heavy tanks from afar; APS tanks, laser AA and jammers stop its drones, and fast vehicles that reach it kill it.\n" +
                "Tip: spread your tanks when the gold ring shows up, and send armoured cars or a helicopter straight at it.",
                "[[Xe phóng drone FPV tinh nhuệ]] · chỉ phe địch · bầy drone dồn dập\n" +
                "Cách đánh: [[drone cảm tử]] như xe phóng FPV, tầm 12–75 m, đánh đau hơn một phần mười, máu nhiều hơn 60%; có thiết giáp trong tầm là phóng [[dồn dập]] (nhanh gấp 2,2 lần trong 6 giây).\n" +
                "Mạnh / yếu: phá nát xe tăng và tăng nặng từ xa; tăng APS, la-de phòng không và xe gây nhiễu chặn drone, xe nhanh áp sát là hạ được.\n" +
                "Mẹo: thấy vòng vàng thì dàn xe tăng ra, tung xe bọc thép hoặc trực thăng lao thẳng vào nó."),
            ["guide.elite_attack_jet"] = (
                "[[Elite attack jet]] · enemy only · long-lasting flares\n" +
                "How it fights: the attack jet's cannon, rockets and bombs, with 60% more health; its [[flares]] come back every 14 s and last twice as long.\n" +
                "Strong / weak: guts ground columns and towers; flak guns ignore flares, and fighters catch it.\n" +
                "Tip: missiles struggle against it: answer with [[flak]] (AA vehicle, Tunguska) or a fighter.",
                "[[Cường kích tinh nhuệ]] · chỉ phe địch · mồi nhiệt bền\n" +
                "Cách đánh: pháo, rốc-két và bom như máy bay cường kích, máu nhiều hơn 60%; [[mồi nhiệt]] 14 giây lại có và kéo dài gấp đôi.\n" +
                "Mạnh / yếu: xé nát đoàn xe mặt đất và tháp canh; pháo cao xạ không bị mồi nhiệt lừa, tiêm kích đuổi kịp nó.\n" +
                "Mẹo: tên lửa khó hạ nó: đáp trả bằng [[cao xạ]] (xe phòng không, Tunguska) hoặc tiêm kích."),
            ["guide.elite_long_sam"] = (
                "[[Elite long-range SAM]] · enemy only · 95 m reach, overdrive\n" +
                "How it fights: the long-range SAM's big missile at [[aircraft only]], a fifth harder-hitting, with 60% more health; with aircraft in range it goes into [[overdrive]] (faster reloads for 6 s).\n" +
                "Strong / weak: closes the sky to helicopters, jets and bombers; helpless on the ground and inside 20 m.\n" +
                "Tip: keep your aircraft home and kill it with tanks, artillery or a fast raid on the ground.",
                "[[Tên lửa phòng không tầm xa tinh nhuệ]] · chỉ phe địch · tầm 95 m, tăng tốc\n" +
                "Cách đánh: tên lửa lớn như bản thường, [[chỉ bắn máy bay]], đánh đau hơn một phần năm, máu nhiều hơn 60%; có máy bay trong tầm là [[tăng tốc]] (nạp nhanh hơn trong 6 giây).\n" +
                "Mạnh / yếu: khóa kín bầu trời với trực thăng, máy bay và oanh tạc cơ; bất lực trước mặt đất và trong vòng 20 m.\n" +
                "Mẹo: giữ máy bay ta ở nhà, hạ nó bằng xe tăng, pháo binh hoặc một đòn đánh nhanh trên mặt đất."),
            ["guide.elite_artillery"] = (
                "[[Elite SP howitzer]] · enemy only · shoot-and-scoot, barrage\n" +
                "How it fights: the SP howitzer's 155 mm shells 25–90 m out, 15% harder-hitting, with 60% more health; with targets in range a rapid [[barrage]], and it moves 15–20 m after every three rounds.\n" +
                "Strong / weak: breaks massed light vehicles and towers; counter-battery fire misses it once it has moved, and anything that reaches it wins.\n" +
                "Tip: don't sit still inside its range; send fast vehicles or aircraft to where it went, not where it fired from.",
                "[[Pháo tự hành tinh nhuệ]] · chỉ phe địch · bắn rồi chạy, bắn dồn\n" +
                "Cách đánh: đạn 155 mm như pháo tự hành, tầm 25–90 m, đánh đau hơn 15%, máu nhiều hơn 60%; có mục tiêu là [[bắn dồn dập]], cứ ba phát lại chạy 15–20 m.\n" +
                "Mạnh / yếu: phá cụm xe nhẹ và tháp canh; phản pháo trượt khi nó đã đổi chỗ, thứ gì áp sát được là thắng.\n" +
                "Mẹo: đừng đứng yên trong tầm của nó; tung xe nhanh hoặc máy bay tới chỗ nó vừa chạy tới, không phải chỗ nó vừa bắn."),

            // Fixed defences: tips on breaking them.
            ["guide.command_vehicle"] = (
                "[[Command vehicle]] · light armour · leads the army · one per side\n" +
                "How it fights: a roof MG only; friendly vehicles within 25 m [[fire 10% faster]]; after [[standing still 5 s]] it is a forward drop zone, and new vehicles land beside it.\n" +
                "Strong / weak: makes every group round it stronger and brings reinforcements to the front; it dies fast to anything that reaches it.\n" +
                "Tip: park it just behind the tanks at the objective, out of the enemy's line of fire.",
                "[[Xe chỉ huy]] · giáp mỏng · dẫn dắt đội quân · mỗi phe một chiếc\n" +
                "Cách đánh: chỉ có súng máy trên nóc; quân ta trong 25 m [[bắn nhanh hơn 10%]]; [[đứng yên 5 giây]] là thành bãi thả dù tiền tuyến, quân mới đáp xuống cạnh nó.\n" +
                "Mạnh / yếu: làm mọi cụm quân quanh nó mạnh hơn và đưa quân tiếp viện ra tận tiền tuyến; thứ gì với tới cũng hạ nó nhanh.\n" +
                "Mẹo: đỗ ngay sau đội xe tăng ở cứ điểm, ngoài tầm bắn thẳng của địch."),
            ["guide.wheeled_gun"] = (
                "[[Wheeled tank hunter]] · light armour · fast (12 m/s)\n" +
                "How it fights: a 105 mm [[armour-piercing]] gun on the move out to 38 m, about 65 damage a second on heavy armour, [[+25%]] on a flank or rear.\n" +
                "Strong / weak: runs round tank lines and punishes their sides; its thin armour loses any straight fight with a tank, and autocannons shred it.\n" +
                "Tip: send it round the flank while your tanks hold the front: every hit on a side counts double work.",
                "[[Pháo bánh lốp diệt tăng]] · giáp mỏng · nhanh (12 m/s)\n" +
                "Cách đánh: pháo 105 mm [[xuyên giáp]] vừa chạy vừa bắn tới 38 m, khoảng 65 sát thương mỗi giây lên giáp dày, [[+25%]] khi trúng hông hoặc đuôi.\n" +
                "Mạnh / yếu: chạy vòng tuyến xe tăng và trừng phạt hai bên sườn; giáp mỏng nên đấu thẳng với tăng là thua, pháo tự động xé nát nó.\n" +
                "Mẹo: vòng qua sườn trong lúc xe tăng giữ mặt trước: phát nào trúng hông cũng đáng giá."),
            ["guide.counter_battery_radar"] = (
                "[[Counter-battery radar]] · light armour · finds the enemy's guns\n" +
                "How it fights: a roof MG only; any enemy artillery that fires within 120 m of it is [[revealed]] to your side for 8 s, and your artillery does [[+15%]] to it.\n" +
                "Strong / weak: turns the enemy's guns into targets for your own artillery, Lancets and aircraft; useless where the enemy has no artillery.\n" +
                "Tip: bring it with your own artillery or Lancets against an army of guns and rockets.",
                "[[Radar phản pháo]] · giáp mỏng · tìm pháo địch\n" +
                "Cách đánh: chỉ có súng máy trên nóc; pháo địch nào khai hỏa trong vòng 120 m quanh nó bị [[lộ vị trí]] với phe ta trong 8 giây, và pháo binh ta gây [[+15%]] sát thương lên nó.\n" +
                "Mạnh / yếu: biến pháo địch thành mục tiêu cho pháo, Lancet và máy bay của ta; vô dụng khi địch không có pháo binh.\n" +
                "Mẹo: mang theo cùng pháo binh hoặc Lancet khi địch dựa vào pháo và rốc-két."),
            ["guide.long_sam"] = (
                "[[Long-range SAM]] · light armour · 95 m reach\n" +
                "How it fights: stops and fires one big missile every 8 s at [[aircraft only]] out to 95 m (600 damage, not closer than 20 m).\n" +
                "Strong / weak: outranges every aircraft's weapons, bombers and gunships included; helpless on the ground and inside 20 m, so it needs cover.\n" +
                "Tip: keep it well behind your line with short-range AA close by for anything that slips under it.",
                "[[Tên lửa phòng không tầm xa]] · giáp mỏng · tầm 95 m\n" +
                "Cách đánh: dừng lại rồi phóng một tên lửa lớn mỗi 8 giây, [[chỉ bắn máy bay]], xa tới 95 m (600 sát thương, không bắn gần hơn 20 m).\n" +
                "Mạnh / yếu: bắn xa hơn vũ khí của mọi máy bay, cả oanh tạc cơ và pháo hạm bay; bất lực trước mặt đất và trong vòng 20 m nên cần được che chắn.\n" +
                "Mẹo: để xa sau tuyến quân, có phòng không tầm ngắn ở gần cho thứ gì lọt xuống thấp."),
            ["guide.atgm_tower"] = (
                "[[ATGM tower]] · fixed defence · anti-tank (50 m)\n" +
                "How it fights: a twin Kornet launcher fires [[anti-tank missiles]] in pairs out to 50 m.\n" +
                "Strong / weak: stops tanks and heavy armour at range; APS and laser AA take its missiles, and artillery outranges it.\n" +
                "Tip: shell it from beyond 50 m, or bring a Trophy APS tank or an Iron Beam with the push.",
                "[[Tháp tên lửa chống tăng]] · công sự cố định · chống tăng (50 m)\n" +
                "Cách đánh: bệ phóng Kornet đôi bắn [[tên lửa chống tăng]] theo cặp xa tới 50 m.\n" +
                "Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và la-de phòng không bắn hạ được tên lửa của nó, pháo binh bắn xa hơn nó.\n" +
                "Mẹo: nã pháo từ ngoài 50 m, hoặc cho tăng có APS hay Iron Beam đi cùng đợt tấn công."),
            ["guide.uav_scan"] = (
                "[[UAV scan]] · recon · 2 CP\n" +
                "How it fights: a drone circles the mark for 10 s and shows [[everything within 30 m]] to your side: stealth aircraft, hidden guns and mines too.\n" +
                "Strong / weak: cheap eyes for artillery and for a push into the unknown; it deals no damage.\n" +
                "Tip: call it on an objective before the army goes in, or where something unseen is shooting at you.",
                "[[UAV quét]] · trinh sát · 2 CP\n" +
                "Cách đánh: một drone lượn vòng trên điểm đánh dấu trong 10 giây và cho phe ta thấy [[mọi thứ trong 30 m]]: cả máy bay tàng hình, pháo ẩn và mìn.\n" +
                "Mạnh / yếu: đôi mắt rẻ cho pháo binh và cho một đợt tiến vào nơi chưa rõ; không gây sát thương.\n" +
                "Mẹo: gọi lên cứ điểm trước khi quân tiến vào, hoặc nơi có thứ gì vô hình đang bắn quân ta."),
            ["guide.remote_mines"] = (
                "[[Remote mines]] · area denial · 5 CP\n" +
                "How it fights: rockets scatter [[8 anti-tank mines]] within 12 m of the mark; each blows up under the first enemy vehicle over it, and they clear themselves after 60 s.\n" +
                "Strong / weak: stops a push on a road or a point; scouts, engineers and a UAV scan see them, and aircraft fly over.\n" +
                "Tip: lay them across the way the enemy is coming, not on top of them.",
                "[[Mìn rải từ xa]] · chặn khu vực · 5 CP\n" +
                "Cách đánh: rốc-két rải [[8 quả mìn chống tăng]] trong vòng 12 m quanh điểm đánh dấu; mỗi quả nổ dưới xe địch đầu tiên đi qua, và tự hủy sau 60 giây.\n" +
                "Mạnh / yếu: chặn một đợt tiến theo đường hoặc vào cứ điểm; trinh sát, công binh và UAV quét nhìn thấy chúng, máy bay bay qua đầu.\n" +
                "Mẹo: rải ngang đường địch đang tới, không phải ngay trên đầu chúng."),
            ["guide.field_tower"] = (
                "[[Field tower]] · fixed defence by air · 6 CP\n" +
                "How it fights: a [[guard tower]] is dropped by parachute on the mark and fights for 60 s; from card rank 5 it is an [[ATGM tower]]. Never into the enemy's camp.\n" +
                "Strong / weak: holds a point you just took or plugs a gap in the line; artillery and heavy guns knock it down.\n" +
                "Tip: drop it on a point the enemy is about to counter-attack.",
                "[[Tháp dã chiến]] · công sự thả dù · 6 CP\n" +
                "Cách đánh: một [[tháp canh]] được thả dù xuống điểm đánh dấu và chiến đấu trong 60 giây; từ cấp 5 của thẻ là [[tháp tên lửa chống tăng]]. Không bao giờ thả vào căn cứ địch.\n" +
                "Mạnh / yếu: giữ cứ điểm vừa chiếm hoặc bịt lỗ hổng trên tuyến; pháo binh và pháo nặng hạ được nó.\n" +
                "Mẹo: thả xuống cứ điểm mà địch sắp phản công."),
            ["guide.sead_strike"] = (
                "[[SEAD strike]] · anti-radiation missile · 7 CP\n" +
                "How it fights: a jet fires an anti-radiation missile at the [[enemy air defence]] nearest the mark (within 20 m): 500 damage, and it is [[knocked out]] for 8 s.\n" +
                "Strong / weak: opens the sky for your aircraft; wasted where there is no anti-air.\n" +
                "Tip: call it just before your helicopters or bombers go in.",
                "[[Đòn SEAD]] · tên lửa chống bức xạ · 7 CP\n" +
                "Cách đánh: máy bay phóng tên lửa chống bức xạ vào [[phòng không địch]] gần điểm đánh dấu nhất (trong 20 m): 500 sát thương, và nó [[tê liệt]] 8 giây.\n" +
                "Mạnh / yếu: mở đường trên trời cho máy bay ta; phí công nếu không có phòng không.\n" +
                "Mẹo: gọi ngay trước khi trực thăng hoặc oanh tạc cơ của ta xông vào."),
            ["guide.ew_tower"] = (
                "[[EW tower]] · small tower · jams, does not shoot\n" +
                "How it fights: guided missiles, drones and fire support aimed within 30 m of it go wide; it has no gun.\n" +
                "Strong / weak: blunts ATGMs, Lancets and strikes on the base; anything that just drives up and shoots kills it.\n" +
                "Tip: put it by the towers the enemy's missiles go for; branches: a 45 m drone jammer, or a spoofer that finds guns.",
                "[[Tháp gây nhiễu EW]] · tháp nhỏ · gây nhiễu, không bắn\n" +
                "Cách đánh: tên lửa điều khiển, drone và hỏa lực yểm trợ nhắm vào trong vòng 30 m quanh nó bị lệch; không có súng.\n" +
                "Mạnh / yếu: làm cùn tên lửa chống tăng, Lancet và các đòn không kích vào căn cứ; thứ gì chỉ cần lái tới bắn là hạ được nó.\n" +
                "Mẹo: đặt cạnh các tháp mà tên lửa địch hay nhắm; nhánh: máy gây nhiễu drone 45 m, hoặc máy đánh lừa radar tìm pháo."),
            ["guide.dragons_teeth"] = (
                "[[Dragon's teeth]] · small obstacle · blocks the way\n" +
                "How it fights: rows of concrete teeth that no vehicle drives through; it fights nothing and is shot at last.\n" +
                "Strong / weak: turns an approach into a detour under your guns; engineers breach it three times as fast.\n" +
                "Tip: close the gap the enemy will come through; the wire branch slows instead of blocking.",
                "[[Răng rồng]] · vật cản nhỏ · chặn đường\n" +
                "Cách đánh: các hàng khối bê tông không xe nào đi qua được; không đánh gì và bị bắn sau cùng.\n" +
                "Mạnh / yếu: biến lối vào thành đường vòng dưới họng súng của ta; công binh phá nhanh gấp ba.\n" +
                "Mẹo: bịt lỗ hổng địch sẽ đi qua; nhánh rào thép gai thì làm chậm thay vì chặn."),
            ["guide.minefield"] = (
                "[[Minefield]] · small obstacle · eight mines\n" +
                "How it fights: eight anti-tank mines within 5 m, laid again every 45 s; the field itself is no target.\n" +
                "Strong / weak: punishes vehicles that rush in; scouts, engineers and a UAV scan see the mines, and engineers clear them.\n" +
                "Tip: put it on the road into your base, behind the guns that make the enemy slow down.",
                "[[Bãi mìn]] · vật cản nhỏ · tám quả mìn\n" +
                "Cách đánh: tám quả mìn chống tăng trong vòng 5 m, rải lại mỗi 45 giây; bãi mìn không phải mục tiêu.\n" +
                "Mạnh / yếu: trừng phạt xe lao vào ồ ạt; trinh sát, công binh và UAV quét thấy mìn, công binh gỡ được.\n" +
                "Mẹo: đặt trên đường vào căn cứ, sau các họng súng buộc địch phải chậm lại."),
            ["guide.c_ram"] = (
                "[[C-RAM]] · medium tower · shoots rounds down\n" +
                "How it fights: shoots down rockets, missiles, drones and about a third of the shells aimed within 35 m, two interceptors at a time; a 20 mm gatling at aircraft.\n" +
                "Strong / weak: shields the base from artillery, rockets and drones; it has nothing for vehicles on the ground.\n" +
                "Tip: put it where the enemy's artillery would hurt most, among your towers.",
                "[[Trạm C-RAM]] · tháp vừa · bắn hạ đạn bay tới\n" +
                "Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 mm bắn máy bay.\n" +
                "Mạnh / yếu: che căn cứ khỏi pháo binh, rốc-két và drone; không có gì đánh xe mặt đất.\n" +
                "Mẹo: đặt nơi pháo địch sẽ gây hại nhất, giữa các tháp của ta."),
            ["guide.gun_pit"] = (
                "[[Hidden gun pit]] · medium tower · ambush\n" +
                "How it fights: a 105 mm gun down in a hole: while no enemy is within 35 m it cannot fire, takes 60 % less damage and shows only to scouts, radars and scans; then it rises and fires.\n" +
                "Strong / weak: surprises tanks that come close; artillery with a spotter, or a UAV scan, finds and breaks it.\n" +
                "Tip: put it where the enemy has to pass close; the Ambush branch doubles its first shot.",
                "[[Ụ pháo ẩn]] · tháp vừa · phục kích\n" +
                "Cách đánh: pháo 105 mm dưới hố: khi không có địch trong 35 m thì không bắn, chịu ít hơn 60 % sát thương và chỉ lộ với trinh sát, radar và UAV quét; địch tới gần thì trồi lên nhả đạn.\n" +
                "Mạnh / yếu: bất ngờ với xe tăng tới gần; pháo binh có trinh sát, hoặc UAV quét, tìm ra và phá được nó.\n" +
                "Mẹo: đặt nơi địch buộc phải đi sát qua; nhánh Phục kích gấp đôi phát đầu."),
            ["guide.drone_hangar"] = (
                "[[Drone hangar]] · large tower · FPV drones\n" +
                "How it fights: sends two FPV kamikaze drones every 20 s at enemies out to 70 m, heavy on armour and structures.\n" +
                "Strong / weak: wears down whatever sits outside the other towers' reach; APS, lasers and jammers stop its drones.\n" +
                "Tip: the Lancet branch reaches 85 m and hunts artillery; the Swarm branch sends four at a time.",
                "[[Nhà chứa drone]] · tháp lớn · drone FPV\n" +
                "Cách đánh: cứ 20 giây phóng hai drone FPV cảm tử vào địch xa tới 70 m, mạnh lên giáp và công trình.\n" +
                "Mạnh / yếu: bào mòn thứ gì đứng ngoài tầm các tháp khác; APS, la-de và máy gây nhiễu chặn được drone.\n" +
                "Mẹo: nhánh Lancet bắn tới 85 m và săn pháo binh; nhánh Bầy đàn phóng bốn chiếc một lần."),
            ["guide.repair_bay"] = (
                "[[Repair bay]] · utility module\n" +
                "How it fights: vehicles within 35 m of your HQ mend 1.5 % of their health a second, even in the middle of a fight.\n" +
                "Strong / weak: keeps a defending army on its feet; it does nothing for vehicles out in the field.\n" +
                "Tip: pair it with a base that fights at home (Defend, Siege, a pressed Conquest).",
                "[[Xưởng sửa chữa]] · mô-đun tiện ích\n" +
                "Cách đánh: xe trong vòng 35 m quanh sở chỉ huy hồi 1,5 % máu mỗi giây, kể cả giữa trận.\n" +
                "Mạnh / yếu: giữ quân phòng thủ đứng vững; không giúp gì xe ở ngoài chiến trường.\n" +
                "Mẹo: dùng khi căn cứ phải đánh tại nhà (Phòng thủ, Công thành, Chiếm cứ điểm bị ép)."),
            ["guide.ammo_depot"] = (
                "[[Ammunition depot]] · utility module\n" +
                "How it fights: vehicles rearm at home twice as fast.\n" +
                "Strong / weak: great for launchers and artillery that empty their magazines; it blows up hard when destroyed.\n" +
                "Tip: take it with an army of rocket artillery.",
                "[[Kho đạn]] · mô-đun tiện ích\n" +
                "Cách đánh: xe nạp đạn tại căn cứ nhanh gấp đôi.\n" +
                "Mạnh / yếu: rất hợp với giàn phóng và pháo binh hay hết đạn; nổ rất mạnh khi bị phá.\n" +
                "Mẹo: mang theo khi bộ bài nhiều pháo phản lực."),
            ["guide.airfield"] = (
                "[[Airfield]] · utility module\n" +
                "How it fights: aircraft over it repair 3 % a second and rearm; your commander sends them back below 35 % health or empty.\n" +
                "Strong / weak: keeps helicopters and jets flying longer; they still have to fly out to fight and can be shot down on the way.\n" +
                "Tip: take it with two or more aircraft in the deck.",
                "[[Sân bay dã chiến]] · mô-đun tiện ích\n" +
                "Cách đánh: máy bay bay trên nó hồi 3 % máu mỗi giây và nạp đạn; chỉ huy tự đưa chúng về khi dưới 35 % máu hoặc hết đạn.\n" +
                "Mạnh / yếu: giúp trực thăng và máy bay bay được lâu hơn; chúng vẫn phải ra trận và có thể bị bắn rơi trên đường.\n" +
                "Mẹo: mang theo khi bộ bài có từ hai máy bay trở lên."),
            ["guide.logistics_station"] = (
                "[[Logistics station]] · utility module\n" +
                "How it fights: your army's supply grows by 8 CP before upkeep slows your income.\n" +
                "Strong / weak: lets a big army keep its full income; nothing for a small one.\n" +
                "Tip: take it when your deck is full of expensive vehicles.",
                "[[Trạm hậu cần]] · mô-đun tiện ích\n" +
                "Cách đánh: mức tiếp tế của quân ta tăng thêm 8 CP trước khi phí duy trì làm giảm thu nhập.\n" +
                "Mạnh / yếu: cho đội quân lớn giữ nguyên thu nhập; vô ích với đội quân nhỏ.\n" +
                "Mẹo: mang theo khi bộ bài toàn xe đắt tiền."),
            ["guide.radar_station"] = (
                "[[Radar station]] · utility module\n" +
                "How it fights: anything inside your base shows, stealth and hidden units too, and enemy guns firing within 120 m show for 8 s.\n" +
                "Strong / weak: exposes stealth bombers and hidden guns over your base; it cannot see beyond it.\n" +
                "Tip: take it against stealth aircraft and artillery-heavy enemies.",
                "[[Trạm radar]] · mô-đun tiện ích\n" +
                "Cách đánh: mọi thứ trong căn cứ đều lộ, kể cả tàng hình và ẩn nấp, và pháo địch khai hỏa trong 120 m bị lộ 8 giây.\n" +
                "Mạnh / yếu: làm lộ oanh tạc cơ tàng hình và pháo ẩn trên căn cứ; không nhìn được ra ngoài.\n" +
                "Mẹo: mang theo khi địch dùng máy bay tàng hình và nhiều pháo binh."),
            ["guide.headquarters"] = (
                "[[Headquarters]] · fixed defence · the heart of a base\n" +
                "How it fights: a twin heavy gun fires two-shot [[volleys]] out to 40 m, twin 30 mm flak and a coaxial MG cover the sky; new vehicles are dropped round it.\n" +
                "Strong / weak: very tough; in Conquest, King of the Hill and Deathmatch it [[cannot fall]], in Assault and Siege it is the [[target]], in Defend and Endless losing it loses the battle.\n" +
                "Tip: its [[HQ level]] (1–5) opens the small, medium and large hardpoints and the utility slots of the base; fill them with towers on the Army tab's Base screen.",
                "[[Sở chỉ huy]] · công sự cố định · trái tim của căn cứ\n" +
                "Cách đánh: pháo nặng hai nòng bắn [[loạt đôi]] tới 40 m, pháo phòng không đôi 30 mm và súng máy đồng trục canh bầu trời; quân mới được thả dù quanh nó.\n" +
                "Mạnh / yếu: cực lì; ở Chiếm cứ điểm, Giữ đồi và Tử chiến nó [[không thể bị phá]], ở Tấn công và Công thành nó là [[mục tiêu]], ở Phòng thủ và Vô tận mất nó là thua.\n" +
                "Mẹo: [[cấp sở chỉ huy]] (1–5) mở các ô tháp nhỏ, vừa, lớn và ô tiện ích của căn cứ; đặt tháp vào chúng ở màn Căn cứ trong thẻ Quân đội."),
            ["guide.super_gun"] = (
                "[[Super-gun]] · fixed defence · the fortress's giant gun\n" +
                "How it fights: on a countdown shown at the top of the screen it fires one huge [[shell]] at the attackers' thickest knot (their camp when nobody is out), 4 s after the warning circle shows.\n" +
                "Strong / weak: one shell wrecks a column of light vehicles; it has no gun for anything near it.\n" +
                "Tip: [[spread out]] when the countdown runs low; destroying it is a side objective that pays CP at once and coins at the end.",
                "[[Siêu pháo]] · công sự cố định · khẩu pháo khổng lồ của pháo đài\n" +
                "Cách đánh: theo đồng hồ đếm ngược ở đầu màn hình, nó bắn một quả [[đạn cực lớn]] vào chỗ quân tấn công đông nhất (vào trại nếu không ai ở ngoài), 4 giây sau khi vòng cảnh báo hiện ra.\n" +
                "Mạnh / yếu: một phát xóa sổ cả đoàn xe nhẹ; nó không có súng bắn gần.\n" +
                "Mẹo: [[tản quân]] khi đồng hồ sắp hết; phá được nó là nhiệm vụ phụ, thưởng CP ngay và xu cuối trận."),
            ["guide.super_gun_shell"] = (
                "[[Super-gun shell]] · the fortress's · one huge round\n" +
                "How it fights: lands 4 s after its warning circle shows, 15 m across.\n" +
                "Strong / weak: wrecks light vehicles and groups; aircraft are safe.\n" +
                "Tip: move out of the circle, or destroy the gun.",
                "[[Đạn siêu pháo]] · của pháo đài · một quả đạn cực lớn\n" +
                "Cách đánh: rơi xuống 4 giây sau khi vòng cảnh báo hiện, rộng 15 m.\n" +
                "Mạnh / yếu: phá nát xe nhẹ và đám đông; máy bay an toàn.\n" +
                "Mẹo: chạy khỏi vòng tròn, hoặc phá khẩu pháo."),
            ["guide.spawn_bastion"] = (
                "[[Camp bastion]] · fixed defence · guards a base\n" +
                "How it fights: never moves; a twin heavy gun fires two-shot [[volleys]] out to 40 m, and a coaxial MG also fires at aircraft.\n" +
                "Strong / weak: very tough, with heavy armour rather than a building's, so [[armour-piercing]] guns work best; beats light vehicles and tanks.\n" +
                "Tip: don't attack it head on; artillery and heavy guns from beyond 40 m, or aircraft, wear it down.",
                "[[Tháp căn cứ]] · công sự cố định · bảo vệ căn cứ\n" +
                "Cách đánh: đứng yên; pháo nặng hai nòng bắn [[loạt đôi]] tới 40 m, kèm súng máy đồng trục bắn được cả máy bay.\n" +
                "Mạnh / yếu: cực lì, giáp dày như xe tăng chứ không phải giáp công trình nên đạn [[xuyên giáp]] hiệu quả nhất; thắng xe nhẹ và xe tăng.\n" +
                "Mẹo: đừng đánh trực diện; dùng pháo binh, pháo nặng từ ngoài 40 m, hoặc máy bay để bào dần."),
            ["guide.heavy_turret"] = (
                "[[Coastal turret]] · fixed defence · twin 155 mm (50 m)\n" +
                "How it fights: a slow-turning twin 155 mm turret that fires two-shot [[high-explosive]] volleys out to 50 m, plus a coaxial MG.\n" +
                "Strong / weak: wrecks light vehicles, groups and tanks in its arc; as a [[structure]] it takes 1.5× from high explosive, little from bullets.\n" +
                "Tip: siege guns, howitzers and rocket artillery outrange it; its turret turns slowly, so come at it from two sides.",
                "[[Tháp pháo bờ biển]] · công sự cố định · pháo đôi 155 mm (50 m)\n" +
                "Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn [[loạt đôi]] đạn nổ mạnh tới 50 m, kèm súng máy đồng trục.\n" +
                "Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong góc bắn; là [[công trình]] nên ăn 1,5× sát thương nổ mạnh, sợ ít đạn súng máy.\n" +
                "Mẹo: tăng công thành, lựu pháo và pháo phản lực bắn xa hơn nó; tháp xoay chậm nên hãy đánh từ hai hướng."),
            ["guide.flak_tower"] = (
                "[[Flak tower]] · fixed defence · closes the sky (46 m)\n" +
                "How it fights: quad [[flak]] guns out to 46 m and an anti-air missile; it fires at ground targets too, but flak does little to them.\n" +
                "Strong / weak: deadly to every [[helicopter]] and jet; almost harmless to tanks, and weak to high explosive.\n" +
                "Tip: kill it with tanks and artillery before sending in any aircraft.",
                "[[Tháp phòng không lớn]] · công sự cố định · khóa bầu trời (46 m)\n" +
                "Cách đánh: bốn nòng [[cao xạ]] tới 46 m kèm tên lửa phòng không; cũng bắn mục tiêu mặt đất nhưng gây rất ít sát thương.\n" +
                "Mạnh / yếu: tử thần với mọi [[trực thăng]] và máy bay; gần như vô hại với xe tăng, sợ đạn nổ mạnh.\n" +
                "Mẹo: dùng xe tăng và pháo binh hạ nó trước khi tung máy bay vào."),
            ["guide.missile_battery"] = (
                "[[Missile battery]] · fixed defence · long-range air defence (62 m)\n" +
                "How it fights: its search radar sees 85 m, and it launches [[missiles]] in pairs at [[aircraft]] up to 62 m away; only an MG for the ground.\n" +
                "Strong / weak: outranges almost every aircraft; any ground force can drive up and destroy it.\n" +
                "Tip: send tanks or artillery at it first; keep aircraft away until it is gone.",
                "[[Dàn tên lửa]] · công sự cố định · phòng không tầm xa (62 m)\n" +
                "Cách đánh: radar nhìn xa 85 m, phóng [[tên lửa]] từng cặp vào [[máy bay]] cách tới 62 m; chỉ có súng máy để đánh mặt đất.\n" +
                "Mạnh / yếu: bắn xa hơn gần như mọi máy bay; nhưng bất kỳ lực lượng mặt đất nào cũng áp sát và phá được nó.\n" +
                "Mẹo: dùng xe tăng hoặc pháo binh diệt nó trước; máy bay tránh xa cho tới khi nó bị hạ."),
            ["guide.point_tower"] = (
                "[[Watchtower]] · fixed defence · guards an objective\n" +
                "How it fights: a heavy MG (30 m, also at aircraft) and a [[grenade launcher]]; in Conquest it is [[neutral]], shoots both sides and rebuilds.\n" +
                "Strong / weak: stops scouts and light vehicles; tanks shrug off its bullets, and high explosive brings it down fast.\n" +
                "Tip: in Assault it serves whoever holds the point; take it with tanks and artillery, not light cars.",
                "[[Tháp canh điểm]] · công sự cố định · canh giữ cứ điểm\n" +
                "Cách đánh: súng máy nặng (30 m, bắn cả máy bay) và [[súng phóng lựu]]. Ở chế độ Giữ cứ điểm nó [[trung lập]], bắn cả hai phe, bị phá sẽ dựng lại.\n" +
                "Mạnh / yếu: chặn trinh sát và xe nhẹ; xe tăng gần như miễn nhiễm đạn của nó, đạn nổ mạnh hạ nó rất nhanh.\n" +
                "Mẹo: ở chế độ Công phá nó thuộc phe giữ điểm; đánh bằng xe tăng và pháo binh, đừng dùng xe nhẹ."),
            ["guide.guard_tower"] = (
                "[[Guard tower]] · fixed defence · light and far-seeing\n" +
                "How it fights: a heavy MG (30 m, also at aircraft) and a grenade launcher; its 60 m sight [[spots]] your army for the enemy's guns.\n" +
                "Strong / weak: stops scouts and [[light vehicles]]; the weakest tower, it falls fast to tanks and high explosive.\n" +
                "Tip: knock it out early with a tank or artillery so it stops spotting for the defence.",
                "[[Tháp canh]] · công sự cố định · nhẹ nhưng nhìn xa\n" +
                "Cách đánh: súng máy nặng (30 m, bắn cả máy bay) và súng phóng lựu; tầm nhìn 60 m giúp [[soi]] quân ta cho pháo địch.\n" +
                "Mạnh / yếu: chặn trinh sát và [[xe nhẹ]]; là tháp yếu nhất, gục nhanh trước xe tăng và đạn nổ mạnh.\n" +
                "Mẹo: hạ nó sớm bằng xe tăng hoặc pháo binh để địch mất tai mắt."),
            ["guide.gun_turret"] = (
                "[[Gun turret]] · fixed defence · tank gun (32 m)\n" +
                "How it fights: a battle tank's 120 mm [[armour-piercing]] gun on a fixed mount, plus a coaxial MG.\n" +
                "Strong / weak: beats tanks and light vehicles that drive into its 32 m reach; outranged by tank destroyers and artillery.\n" +
                "Tip: stay outside 32 m and let a [[tank destroyer]] (40 m) or artillery break it.",
                "[[Tháp pháo]] · công sự cố định · pháo xe tăng (32 m)\n" +
                "Cách đánh: pháo 120 mm [[xuyên giáp]] của tăng chủ lực đặt trên bệ cố định, kèm súng máy đồng trục.\n" +
                "Mạnh / yếu: thắng xe tăng và xe nhẹ lọt vào tầm 32 m; bị xe diệt tăng và pháo binh bắn xa hơn.\n" +
                "Mẹo: đứng ngoài 32 m, để [[xe diệt tăng]] (40 m) hoặc pháo binh phá nó."),
            ["guide.aa_turret"] = (
                "[[AA turret]] · fixed defence · anti-aircraft (42 m)\n" +
                "How it fights: twin 30 mm [[flak]] cannons out to 42 m and an anti-air missile (44 m); it fires at the ground too, to little effect.\n" +
                "Strong / weak: shreds [[helicopters]] and jets; ground forces take it apart easily.\n" +
                "Tip: clear it with tanks or artillery before your aircraft fly in.",
                "[[Tháp phòng không]] · công sự cố định · chống máy bay (42 m)\n" +
                "Cách đánh: pháo đôi 30 mm [[cao xạ]] tới 42 m và tên lửa phòng không (44 m); cũng bắn mặt đất nhưng chẳng mấy tác dụng.\n" +
                "Mạnh / yếu: xé nát [[trực thăng]] và máy bay; lực lượng mặt đất phá nó dễ dàng.\n" +
                "Mẹo: dọn nó bằng xe tăng hoặc pháo binh trước khi máy bay ta bay vào."),
            ["guide.rocket_turret"] = (
                "[[Rocket battery]] · fixed defence · rocket salvos (55 m)\n" +
                "How it fights: fires eight-rocket [[salvos]] at ground targets 8–55 m away, plus a machine gun for anything that gets too close.\n" +
                "Strong / weak: punishes groups of light vehicles and artillery; tanks take its rockets well, and HE shells wreck it.\n" +
                "Tip: spread out as you come in and rush it with tanks: inside 8 m only its [[machine gun]] can fire.",
                "[[Dàn rốc-két]] · công sự cố định · phóng loạt (55 m)\n" +
                "Cách đánh: phóng [[loạt]] tám rốc-két vào mục tiêu mặt đất cách 8–55 m, kèm súng máy cho kẻ áp sát.\n" +
                "Mạnh / yếu: trừng phạt cụm xe nhẹ và pháo binh; xe tăng chịu rốc-két khá tốt, đạn nổ mạnh phá nó nhanh.\n" +
                "Mẹo: dàn quân khi tiến vào và dùng xe tăng lao tới: trong vòng 8 m nó chỉ còn [[súng máy]]."),
            ["guide.mg_bunker"] = (
                "[[MG bunker]] · fixed defence · machine gun and ATGM\n" +
                "How it fights: a fast heavy machine gun (32 m, also at aircraft) and a slow-firing [[anti-tank missile]] post (34 m).\n" +
                "Strong / weak: mows down scouts and [[light vehicles]]; its missile hurts tanks, but only once every 14 s.\n" +
                "Tip: send tanks, not light vehicles; a flame tank or artillery cracks it fast.",
                "[[Lô cốt súng máy]] · công sự cố định · súng máy và tên lửa chống tăng\n" +
                "Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay) và bệ [[tên lửa chống tăng]] bắn chậm (34 m).\n" +
                "Mạnh / yếu: quét sạch trinh sát và [[xe nhẹ]]; tên lửa hại được xe tăng nhưng 14 giây mới bắn một lần.\n" +
                "Mẹo: đưa xe tăng vào, đừng dùng xe nhẹ; tăng phun lửa hoặc pháo binh phá nó rất nhanh."),
            ["guide.artillery_emplacement"] = (
                "[[Artillery emplacement]] · fixed defence · long range (90 m)\n" +
                "How it fights: a howitzer that shells ground targets 25–90 m away whenever the defence can see them; a machine gun for close defence.\n" +
                "Strong / weak: hurts anything that stops inside its range; it cannot hit closer than 25 m, and it is fairly fragile.\n" +
                "Tip: rush it with fast vehicles: inside 25 m its gun cannot fire at you. Kill its [[spotters]] first.",
                "[[Trận địa pháo]] · công sự cố định · tầm xa (90 m)\n" +
                "Cách đánh: lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe thủ nhìn thấy; có súng máy tự vệ ở gần.\n" +
                "Mạnh / yếu: gây đau cho mọi thứ dừng lại trong tầm; không bắn được gần hơn 25 m, và khá mỏng manh.\n" +
                "Mẹo: dùng xe nhanh lao vào: trong vòng 25 m pháo của nó chịu thua. Diệt [[tai mắt]] của nó trước."),

            // Mission units and bosses.
            ["guide.supply_truck"] = (
                "[[Supply truck]] · mission unit · slow convoy\n" +
                "How it fights: only a light machine gun; it drives its route to the depot and cannot take objectives.\n" +
                "Strong / weak: armoured enough to take some hits, but it cannot fight back against anything real.\n" +
                "Tip: in [[convoy]] missions, clear the road ahead with tanks and keep AA with the trucks.",
                "[[Xe tiếp tế]] · đơn vị nhiệm vụ · đoàn xe chậm\n" +
                "Cách đánh: chỉ có súng máy nhẹ; nó chạy theo lộ trình tới kho và không chiếm được cứ điểm.\n" +
                "Mạnh / yếu: đủ giáp để chịu vài phát, nhưng không đánh lại được thứ gì đáng kể.\n" +
                "Mẹo: trong nhiệm vụ [[hộ tống]], dùng xe tăng dọn đường phía trước và cho phòng không đi cùng xe tải."),
            ["guide.behemoth"] = (
                "[[Boss]] · land battleship · heavy armour\n" +
                "How it fights: twin main guns (40 m), a 120 mm, flak and [[missiles]] that hit ground and air (45 m); calls two elite tanks at 70%.\n" +
                "Strong / weak: crushes light vehicles and tanks; [[tank hunters]] are its bane, and its armour shrugs off bullets.\n" +
                "Tip: fight it from beyond 45 m; at half health it [[rages]] (faster fire), and below 35% it raises a shield now and then.",
                "[[Trùm]] · chiến hạm mặt đất · giáp dày\n" +
                "Cách đánh: pháo chính hai nòng (40 m), pháo 120 mm, pháo cao xạ và [[tên lửa]] bắn cả đất lẫn trời (45 m); còn 70% máu gọi 2 tăng tinh nhuệ.\n" +
                "Mạnh / yếu: nghiền nát xe nhẹ và xe tăng; khắc tinh là [[xe diệt tăng]], giáp dày khiến đạn súng máy vô dụng.\n" +
                "Mẹo: đánh từ ngoài 45 m; còn nửa máu nó [[nổi điên]] (bắn nhanh hơn), dưới 35% thỉnh thoảng bật khiên."),
            ["guide.behemoth_inferno"] = (
                "[[Boss]] · flame Behemoth · burns everything close\n" +
                "How it fights: twin [[flame projectors]] (20 m) set the ground on fire; a thermobaric rocket box hits 10–46 m; it calls two elite tanks at 70%.\n" +
                "Strong / weak: melts light vehicles and tanks that get close; weak to [[aircraft]], since it has only one flak gun.\n" +
                "Tip: keep your distance: tank destroyers and artillery from beyond 46 m, attack helicopters and jets from above.",
                "[[Trùm]] · Behemoth phun lửa · thiêu mọi thứ ở gần\n" +
                "Cách đánh: hai [[súng phun lửa]] lớn (20 m) đốt cháy mặt đất; hộp rốc-két nhiệt áp đánh tầm 10–46 m; còn 70% máu gọi 2 tăng tinh nhuệ.\n" +
                "Mạnh / yếu: thiêu chảy xe nhẹ và xe tăng tới gần; yếu trước [[máy bay]] vì chỉ có một khẩu pháo cao xạ.\n" +
                "Mẹo: giữ khoảng cách: xe diệt tăng và pháo binh bắn từ ngoài 46 m, trực thăng tấn công và cường kích đánh từ trên cao."),
            ["guide.behemoth_tempest"] = (
                "[[Boss]] · railgun Behemoth · long range (80 m)\n" +
                "How it fights: a [[railgun]] charges for a second (the coils glow), then [[pierces]] a whole line to 80 m; two coilguns hit ground and air (55 m).\n" +
                "Strong / weak: punishes vehicles lined up in a column; close in, its EMP (22 m) stuns ground vehicles, and it shields itself when hurt.\n" +
                "Tip: spread out and close in from several sides; when the coils glow, get out of the line it is aiming along.",
                "[[Trùm]] · Behemoth pháo điện từ · tầm xa (80 m)\n" +
                "Cách đánh: [[pháo điện từ]] nạp năng lượng một giây (cuộn dây sáng lên) rồi [[xuyên thủng]] cả hàng tới 80 m; hai pháo điện từ bắn đất lẫn trời (55 m).\n" +
                "Mạnh / yếu: trừng phạt xe đi thành hàng dọc; ở gần, EMP (22 m) làm choáng xe mặt đất, và nó bật khiên khi bị thương.\n" +
                "Mẹo: dàn quân và áp sát từ nhiều hướng; khi cuộn dây sáng lên, hãy tránh khỏi đường ngắm của nó."),
            ["guide.mobile_fortress"] = (
                "[[Boss]] · mobile fortress · very slow\n" +
                "How it fights: a howitzer (60 m), rocket boxes, flak and missiles; an [[EMP]] stuns ground vehicles in 22 m; two elite heavy tanks join at 66%.\n" +
                "Strong / weak: shreds light vehicles and tanks that crowd it; [[tank hunters]] and heavy artillery wear it down.\n" +
                "Tip: fight from beyond 22 m so the EMP misses, and expect a doubled rate of fire below 40% health.",
                "[[Trùm]] · pháo đài di động · cực chậm\n" +
                "Cách đánh: lựu pháo (60 m), hộp rốc-két, pháo cao xạ và tên lửa; [[EMP]] làm choáng xe mặt đất trong 22 m; 66% máu gọi 2 tăng nặng tinh nhuệ.\n" +
                "Mạnh / yếu: xé nát xe nhẹ và xe tăng dồn quanh nó; [[xe diệt tăng]] và pháo hạng nặng bào dần được nó.\n" +
                "Mẹo: đánh từ ngoài 22 m để né EMP, và coi chừng dưới 40% máu nó bắn nhanh gấp đôi."),
            ["guide.fortress_hive"] = (
                "[[Boss]] · drone fortress · deadly to aircraft\n" +
                "How it fights: no big gun: [[drone swarms]] from two racks (70 m), a SAM battery (62 m) and flak for the sky, and strike drones sent out.\n" +
                "Strong / weak: shreds [[aircraft]]; its drones hurt tanks, but tanks and artillery are what break it.\n" +
                "Tip: leave your aircraft at home; bring APS tanks or laser AA against the drones, then grind it down with tanks and artillery.",
                "[[Trùm]] · pháo đài drone · tử thần của máy bay\n" +
                "Cách đánh: không có pháo lớn: hai giàn phóng [[bầy drone]] tới 70 m, dàn tên lửa (62 m) và pháo cao xạ giữ bầu trời, còn thả thêm UAV tấn công.\n" +
                "Mạnh / yếu: xé nát [[máy bay]]; drone của nó hại được xe tăng, nhưng xe tăng và pháo binh mới là thứ hạ được nó.\n" +
                "Mẹo: để máy bay ở nhà; mang tăng APS hoặc la-de phòng không chặn drone, rồi dùng xe tăng và pháo binh bào dần."),
            ["guide.fortress_bastion"] = (
                "[[Boss]] · the toughest fortress · heavy mortar (80 m)\n" +
                "How it fights: a heavy [[mortar]] hits 12–80 m out, four 40 mm autocannon turrets (28 m) cover every side; it [[patches]] itself up once at half.\n" +
                "Strong / weak: its autocannons shred light vehicles that come close; its armour stops bullets, and its mortar cannot hit inside 12 m.\n" +
                "Tip: bring tank hunters and heavy guns, and keep your burst damage for after its one repair.",
                "[[Trùm]] · pháo đài lì đòn nhất · cối hạng nặng (80 m)\n" +
                "Cách đánh: khẩu [[cối]] hạng nặng bắn tầm 12–80 m, bốn tháp pháo tự động 40 mm (28 m) phủ mọi hướng, còn nửa máu nó [[tự vá giáp]] một lần.\n" +
                "Mạnh / yếu: pháo tự động xé nát xe nhẹ tới gần; giáp dày chặn đạn súng máy, cối không bắn được trong vòng 12 m.\n" +
                "Mẹo: mang xe diệt tăng và pháo hạng nặng, để dành hỏa lực dồn cho sau lần tự vá duy nhất của nó."),
            ["guide.armored_train"] = (
                "[[Boss]] · armoured train · follows the rails\n" +
                "How it fights: two heavy guns (42 m), a rocket box, flak and an MG; it hides in [[smoke]] when shot and [[patches]] up 20% once, at half health.\n" +
                "Strong / weak: its guns kill tanks and light vehicles near the track; it cannot leave the rails.\n" +
                "Tip: set up tank hunters and artillery along the line ahead of it, more than 45 m from the track.",
                "[[Trùm]] · đoàn tàu bọc thép · chạy theo đường ray\n" +
                "Cách đánh: hai pháo nặng (42 m), hộp rốc-két, pháo cao xạ và súng máy; bị bắn thì núp trong [[khói]], còn nửa máu thì [[tự vá]] 20% một lần.\n" +
                "Mạnh / yếu: pháo của nó diệt xe tăng và xe nhẹ gần đường ray; nó không thể rời đường ray.\n" +
                "Mẹo: bố trí xe diệt tăng và pháo binh dọc tuyến đường phía trước nó, cách đường ray hơn 45 m."),
            ["guide.nuke_train"] = (
                "[[Boss]] · missile train · a race against the countdown\n" +
                "How it fights: twin heavy guns (40 m) and two flak guns; it hides in [[smoke]] when shot, and at 60% calls four elite EW carriers with [[EMP]].\n" +
                "Strong / weak: its guns wreck anything near the track; it cannot leave the rails and carries no missiles to fight with.\n" +
                "Tip: hit it hard and early with artillery and tank hunters; it must be stopped before it reaches the launch site.",
                "[[Trùm]] · đoàn tàu tên lửa · chạy đua với đồng hồ\n" +
                "Cách đánh: pháo nặng hai nòng (40 m) và hai pháo cao xạ; bị bắn thì núp trong [[khói]], còn 60% máu gọi 4 xe bọc thép tinh nhuệ có [[EMP]].\n" +
                "Mạnh / yếu: pháo của nó phá nát mọi thứ gần đường ray; nó không rời được đường ray và không có tên lửa để đánh.\n" +
                "Mẹo: dùng pháo binh và xe diệt tăng đánh mạnh và sớm; phải chặn nó trước khi tới bãi phóng."),
            ["guide.mega_gunship"] = (
                "[[Boss]] · giant helicopter · flying\n" +
                "How it fights: rockets, two 30 mm guns, twin miniguns and missiles; [[flares]] often, three elite helicopters at 60%, and it rages at 50%.\n" +
                "Strong / weak: tank guns and artillery cannot touch it: only [[anti-air]] and fighters hurt it.\n" +
                "Tip: mass flak (AA vehicles, Tunguskas), since guns ignore its flares, and add fighters for the escort helicopters.",
                "[[Trùm]] · trực thăng khổng lồ · bay\n" +
                "Cách đánh: rốc-két, hai pháo 30 mm, cặp súng máy nhiều nòng và tên lửa; thả [[mồi nhiệt]] liên tục, 60% máu gọi 3 trực thăng tinh nhuệ, 50% thì nổi điên.\n" +
                "Mạnh / yếu: pháo xe tăng và pháo binh không chạm được nó: chỉ [[phòng không]] và tiêm kích gây sát thương.\n" +
                "Mẹo: dồn pháo cao xạ (xe phòng không, Tunguska) vì đạn pháo không bị mồi nhiệt lừa, thêm tiêm kích để diệt trực thăng hộ tống."),
            ["guide.drone_mothership"] = (
                "[[Boss]] · flying drone carrier · the most health of any boss\n" +
                "How it fights: cannons and swarms of kamikaze [[drones]] (70 m) at the ground, flak for aircraft; every 30 s it launches three [[strike drones]].\n" +
                "Strong / weak: floods the ground with drones; only anti-air and fighters can damage it, and it shields itself at half health.\n" +
                "Tip: mass flak and SAMs under it, APS tanks or laser AA against its drones, and fighters to clear the strike drones.",
                "[[Trùm]] · tàu mẹ drone biết bay · nhiều máu nhất trong các trùm\n" +
                "Cách đánh: pháo và bầy [[drone cảm tử]] (70 m) đánh mặt đất, pháo cao xạ chống máy bay; cứ 30 giây phóng ra 3 [[UAV tấn công]].\n" +
                "Mạnh / yếu: nhấn chìm mặt đất bằng drone; chỉ phòng không và tiêm kích gây sát thương được, còn nửa máu thì bật khiên.\n" +
                "Mẹo: dồn pháo cao xạ và tên lửa phòng không bên dưới, tăng APS hoặc la-de chặn drone, tiêm kích dọn UAV tấn công."),
            ["guide.silver_bug"] = (
                "[[Boss]] · flying saucer · laser and coilguns\n" +
                "How it fights: a [[laser]] burns a line on the ground (36 m); charged coilguns hit ground and air (55 m); flak, drones and an [[EMP]] within 12 m.\n" +
                "Strong / weak: only anti-air and fighters damage it; it shields itself at half health and calls four strike drones at 66%.\n" +
                "Tip: keep ground units spread and more than 12 m away; mass flak and SAMs, and fire fighters' missiles from beyond 55 m.",
                "[[Trùm]] · đĩa bay · la-de và pháo điện từ\n" +
                "Cách đánh: tia [[la-de]] thiêu một đường trên mặt đất (36 m); pháo điện từ bắn cả đất lẫn trời (55 m); pháo cao xạ, drone, [[EMP]] trong 12 m.\n" +
                "Mạnh / yếu: chỉ phòng không và tiêm kích gây sát thương được; còn nửa máu thì bật khiên, 66% máu gọi 4 UAV tấn công.\n" +
                "Mẹo: dàn quân mặt đất, đứng cách nó hơn 12 m; dồn cao xạ và tên lửa phòng không, tiêm kích bắn từ ngoài 55 m."),
            ["guide.sky_fortress"] = (
                "[[Boss]] · AC-130 gunship · circles high\n" +
                "How it fights: [[orbits]] its prey, a 105 mm, two 40 mm and a 25 mm firing from its left side (50–58 m), plus Griffins; nothing for aircraft.\n" +
                "Strong / weak: destroys ground forces caught under its orbit; only [[anti-air]] and fighters can reach it.\n" +
                "Tip: build flak and SAMs early and add fighters, which its guns cannot hit; three escort helicopters join at 60%.",
                "[[Trùm]] · pháo hạm AC-130 · bay vòng trên cao\n" +
                "Cách đánh: [[bay vòng]] quanh mục tiêu, pháo 105 mm, hai 40 mm và một 25 mm bắn từ bên trái (50–58 m), kèm Griffin; không bắn được máy bay.\n" +
                "Mạnh / yếu: hủy diệt quân mặt đất nằm dưới vòng bay; chỉ [[phòng không]] và tiêm kích với tới nó.\n" +
                "Mẹo: xây cao xạ và tên lửa phòng không sớm, thêm tiêm kích vì pháo của nó không bắn được máy bay; 60% máu có 3 trực thăng hộ tống."),

            ["guide.rail_supergun"] = (
                "[[Boss]] · railway gun · stays put at the edge of the field\n" +
                "How it fights: every 20 s one 80 cm [[shell]] at your biggest group of ground vehicles, anywhere on the map; a red ring marks where it lands [[3 s]] ahead. Walls, cannon and flak towers and a [[fire-control post]] guard its bed; two 40 mm guns cover it.\n" +
                "Strong / weak: it punishes an army that bunches up; it cannot move, and once its fire-control post falls its shells land wide.\n" +
                "Tip: keep moving and spread out when the ring shows; break the fire-control post first, then push in with tanks behind the artillery.",
                "[[Trùm]] · pháo đường ray · đứng yên ở mép chiến trường\n" +
                "Cách đánh: cứ 20 giây một quả [[đạn 80 cm]] vào cụm xe mặt đất đông nhất của bạn, ở bất cứ đâu trên bản đồ; vòng đỏ báo chỗ rơi trước [[3 giây]]. Tường, tháp pháo, tháp phòng không và [[trạm chỉ thị mục tiêu]] bảo vệ nền pháo; hai khẩu 40 mm che chắn.\n" +
                "Mạnh / yếu: trừng phạt đội quân dồn cục; không di chuyển được, và mất trạm chỉ thị thì đạn rơi lệch xa.\n" +
                "Mẹo: luôn di chuyển và tản ra khi thấy vòng đỏ; phá trạm chỉ thị trước, rồi cho xe tăng tiến vào sau pháo binh."),
            ["guide.earth_borer"] = (
                "[[Boss]] · boring machine · attacks from below\n" +
                "How it fights: it [[dives]], bores unseen and untouchable to under your biggest group of ground vehicles, the ground [[cracks]] for 2 s, then it breaks out in a quake that stuns everything on the ground within 15 m. Its drill and two cannons finish the job.\n" +
                "Strong / weak: deadly to a tight group of tanks; right after it breaks out it takes [[half as much again]] for 6 s, and aircraft are never under it.\n" +
                "Tip: move out of the cracks at once, then turn everything on it while it is exposed.",
                "[[Trùm]] · máy khoan · tấn công từ dưới đất\n" +
                "Cách đánh: [[chui xuống đất]], khoan ngầm không bị nhắm tới dưới cụm xe mặt đất đông nhất của bạn, mặt đất [[nứt]] 2 giây rồi nó trồi lên gây rung chấn làm choáng mọi xe mặt đất trong 15 m. Mũi khoan và hai khẩu pháo kết liễu nốt.\n" +
                "Mạnh / yếu: cực nguy hiểm với cụm xe tăng dày; ngay sau khi trồi lên nó nhận [[thêm 50%]] sát thương trong 6 giây, và máy bay không bao giờ nằm dưới nó.\n" +
                "Mẹo: rời khỏi vết nứt ngay, rồi dồn hỏa lực vào nó lúc nó lộ thân."),
            ["guide.command_airship"] = (
                "[[Boss]] · flying battleship · four engines, two drone bays, a radar\n" +
                "How it fights: twin 57 mm [[flak]] turrets, drones from two [[bays]] and a strike drone from each now and then. Every part has its own health: the hull takes [[no damage]] until two engines are down.\n" +
                "Strong / weak: only [[anti-air]] and fighters reach it; break a bay and its drones stop, break the [[radar]] and its flak scatters wide.\n" +
                "Tip: shoot the engines first to open the hull, then the radar; bring flak and SAMs, and fighters for its strike drones.",
                "[[Trùm]] · chiến hạm bay · bốn động cơ, hai nhà chứa drone, một radar\n" +
                "Cách đánh: hai tháp [[pháo phòng không]] 57 mm, drone từ hai [[nhà chứa]] và thỉnh thoảng mỗi nhà chứa thả một UAV tấn công. Mỗi bộ phận có máu riêng: thân [[không nhận sát thương]] cho tới khi hai động cơ bị phá.\n" +
                "Mạnh / yếu: chỉ [[phòng không]] và tiêm kích với tới; phá nhà chứa thì ngừng thả drone, phá [[radar]] thì pháo phòng không của nó bắn lệch.\n" +
                "Mẹo: bắn động cơ trước để mở thân, rồi tới radar; mang pháo cao xạ và tên lửa phòng không, thêm tiêm kích để diệt UAV."),
            ["guide.landing_hovercraft"] = (
                "[[Boss]] · air-cushion landing craft · lands troops\n" +
                "How it fights: it runs its route along the coast; every 35 s it stops, drops its [[ramp]] and lands 3 or 4 vehicles, five times at most. Two six-barrel CIWS guard it against ground and air.\n" +
                "Strong / weak: every landing it makes grows the enemy army; it is big and slow to turn, and anything that hits it on its way in cuts the landings short.\n" +
                "Tip: meet it before its first landing with tank hunters and artillery, and keep a reserve for the troops it has already put ashore.",
                "[[Trùm]] · tàu đệm khí đổ bộ · thả quân lên bờ\n" +
                "Cách đánh: chạy theo lộ trình dọc bờ biển; cứ 35 giây dừng lại, hạ [[cửa đổ bộ]] và thả 3–4 xe lên bờ, tối đa năm lần. Hai pháo CIWS sáu nòng che chắn cả đất lẫn trời.\n" +
                "Mạnh / yếu: mỗi lần đổ bộ là địch thêm quân; nó to và xoay chậm, đánh trúng nó trên đường tới là cắt bớt số lần đổ bộ.\n" +
                "Mẹo: đón đầu nó trước lần đổ bộ đầu tiên bằng xe diệt tăng và pháo binh, và giữ lực lượng dự bị cho số quân đã lên bờ."),
            ["guide.supreme_command"] = (
                "[[Boss]] · super-heavy headquarters · makes its army stronger\n" +
                "How it fights: only two light machine guns; every enemy unit within [[40 m]] of it hits [[20 % harder]] and fires 20 % faster. An elite guard rides with it, and more come at 60 %.\n" +
                "Strong / weak: its army is far more dangerous near it; on its own it barely fights back and cannot outrun anything.\n" +
                "Tip: pull the fight away from it, or strike it from range with artillery and aircraft; kill it and its whole army weakens at once.",
                "[[Trùm]] · sở chỉ huy siêu nặng · làm quân mình mạnh lên\n" +
                "Cách đánh: chỉ có hai súng máy nhẹ; mọi quân địch trong [[40 m]] quanh nó tăng [[20% sát thương]] và 20% tốc độ bắn. Có cận vệ tinh nhuệ đi kèm, còn 60% máu thì gọi thêm.\n" +
                "Mạnh / yếu: quân địch gần nó nguy hiểm hơn nhiều; bản thân nó gần như không đánh lại được và không chạy thoát được thứ gì.\n" +
                "Mẹo: kéo trận đánh ra xa nó, hoặc đánh nó từ xa bằng pháo binh và máy bay; hạ nó là cả đạo quân yếu đi ngay."),

            // Fire support cards.
            ["guide.artillery_barrage"] = (
                "[[Artillery barrage]] · fire support · 5 CP\n" +
                "How it fights: 1.5 s after you tap, twelve [[shells]] rain on a 10 m circle over 4 s, each a high-explosive blast.\n" +
                "Strong / weak: good against groups, [[towers]] and parked artillery; fast vehicles drive out of it, and it cannot hit aircraft.\n" +
                "Tip: aim at enemies that stand and fight or sit capturing a point; it never hurts your own vehicles.",
                "[[Pháo kích]] · hỏa lực yểm trợ · 5 CP\n" +
                "Cách đánh: 1,5 giây sau khi chạm, mười hai quả [[đạn pháo]] rơi xuống vùng tròn 10 m trong 4 giây, mỗi quả là một vụ nổ mạnh.\n" +
                "Mạnh / yếu: tốt với cụm địch, [[tháp canh]] và pháo binh đứng yên; xe nhanh chạy thoát được, và không đánh được máy bay.\n" +
                "Mẹo: nhắm vào địch đang đứng giao chiến hoặc đang chiếm điểm; nó không bao giờ gây hại cho xe ta."),
            ["guide.airstrike"] = (
                "[[Airstrike]] · a line of bombs · 8 CP\n" +
                "How it fights: 2 s after you call it, a jet drops eight [[bombs]] along a 60 m line in the direction you [[drag]]; from card [[rank 7]] the line is 40% longer (84 m, eleven bombs).\n" +
                "Strong / weak: hits columns and towers along a road hard; a single vehicle off the line escapes, and aircraft are immune.\n" +
                "Tip: drag it along the enemy's line of advance so every bomb finds a target.",
                "[[Không kích]] · một hàng bom · 8 CP\n" +
                "Cách đánh: 2 giây sau khi gọi, máy bay thả tám quả [[bom]] dọc một đường 60 m theo hướng bạn [[kéo]]; từ [[cấp 7]] của thẻ, đường bom dài hơn 40% (84 m, mười một quả).\n" +
                "Mạnh / yếu: đánh mạnh vào đoàn xe và tháp canh dọc đường; xe lẻ nằm ngoài hàng bom sẽ thoát, máy bay thì miễn nhiễm.\n" +
                "Mẹo: kéo dọc theo hướng tiến quân của địch để quả bom nào cũng trúng."),
            ["guide.cruise_missile"] = (
                "[[Cruise missile]] · one huge blast · 14 CP\n" +
                "How it fights: after a 3 s warning, one [[missile]] strikes the spot with an 18 m blast.\n" +
                "Strong / weak: the best way to wipe out a crowd or a cluster of [[defences]]; moving targets may drive off before it lands.\n" +
                "Tip: fire it where enemies stand still: a captured objective, a siege line, parked artillery. Enemy jammers throw it off.",
                "[[Tên lửa hành trình]] · một vụ nổ cực lớn · 14 CP\n" +
                "Cách đánh: sau 3 giây cảnh báo, một quả [[tên lửa]] đánh xuống điểm chọn với vụ nổ bán kính 18 m.\n" +
                "Mạnh / yếu: cách tốt nhất để xóa sổ một cụm quân hoặc cụm [[công sự]]; mục tiêu đang chạy có thể thoát trước khi nó rơi.\n" +
                "Mẹo: bắn vào nơi địch đứng yên: cứ điểm đang chiếm, tuyến công thành, pháo binh đang đỗ. Xe gây nhiễu địch làm nó lệch."),
            ["guide.smoke_screen"] = (
                "[[Smoke screen]] · blocks sight · 2 CP\n" +
                "How it fights: after 1 s a 12 m cloud stands for 12 s; no one can see into or through it, so guns lose their [[line of sight]].\n" +
                "Strong / weak: saves units from long-range guns, ATGMs and railguns; it does no damage, and at point-blank range fighting goes on.\n" +
                "Tip: drop it between your advancing tanks and the enemy's [[tank destroyers]], or over a unit pulling back.",
                "[[Màn khói]] · che tầm nhìn · 2 CP\n" +
                "Cách đánh: sau 1 giây, đám khói 12 m đứng trong 12 giây; không ai nhìn vào hay xuyên qua được, súng pháo mất [[tầm nhìn]].\n" +
                "Mạnh / yếu: cứu quân ta khỏi pháo tầm xa, tên lửa chống tăng và pháo điện từ; không gây sát thương, sát sạt nhau thì vẫn đánh được.\n" +
                "Mẹo: thả giữa xe tăng ta đang tiến và [[xe diệt tăng]] địch, hoặc che cho xe đang rút lui."),
            ["guide.repair_drop"] = (
                "[[Repair]] · heals an area · 4 CP\n" +
                "How it fights: repairs your vehicles within 12 m by 40% of their health, spread over 6 s.\n" +
                "Strong / weak: turns a close fight when your army is [[bunched up]]; wasted on units spread far apart.\n" +
                "Tip: call it on your tank line in the middle of the fight, not after it.",
                "[[Sửa chữa]] · hồi máu theo vùng · 4 CP\n" +
                "Cách đánh: sửa cho xe ta trong vòng 12 m tổng cộng 40% máu, rải đều trong 6 giây.\n" +
                "Mạnh / yếu: lật ngược trận giằng co khi quân ta [[đứng gần nhau]]; phí nếu quân dàn quá rộng.\n" +
                "Mẹo: gọi xuống tuyến xe tăng ngay giữa trận, đừng đợi đánh xong."),
            ["guide.napalm_strike"] = (
                "[[Napalm strike]] · a line of fire · 9 CP\n" +
                "How it fights: a jet lays ten [[fire]] bombs along a 55 m line in the direction you drag; the ground is left burning.\n" +
                "Strong / weak: fire burns [[light vehicles]] (125%) and buildings; heavy armour takes only half, and aircraft none.\n" +
                "Tip: drag it through a column of light vehicles or a row of towers.",
                "[[Bom napalm]] · một hàng lửa · 9 CP\n" +
                "Cách đánh: máy bay thả mười quả [[bom lửa]] dọc đường 55 m theo hướng bạn kéo; mặt đất bị đốt cháy.\n" +
                "Mạnh / yếu: lửa thiêu [[xe nhẹ]] (125%) và nhà cửa; giáp dày chỉ nhận một nửa, máy bay thì không hề hấn gì.\n" +
                "Mẹo: kéo xuyên qua một đoàn xe nhẹ hoặc một dãy tháp canh."),
            ["guide.air_raid"] = (
                "[[Air raid]] · battle event · hits both sides\n" +
                "How it fights: a neutral bomber wave lays fourteen [[bombs]] along a 70 m line over the busiest fight, 4 s after the warning.\n" +
                "Strong / weak: hurts everyone under it, yours and theirs alike; only aircraft are safe.\n" +
                "Tip: when the warning shows, [[pull back]] from the main fight and let the bombs land on the enemy.",
                "[[Không kích bất ngờ]] · sự kiện trận đấu · trúng cả hai phe\n" +
                "Cách đánh: một đợt máy bay trung lập rải mười bốn quả [[bom]] dọc đường 70 m lên chỗ giao tranh ác liệt nhất, 4 giây sau cảnh báo.\n" +
                "Mạnh / yếu: gây sát thương mọi thứ bên dưới, cả ta lẫn địch; chỉ máy bay là an toàn.\n" +
                "Mẹo: khi thấy cảnh báo, [[rút quân]] khỏi điểm nóng và để bom rơi trúng địch."),

            // Items: single use, bought with coins.
            ["guide.moab"] = (
                "[[MOAB]] · item · the biggest blast in the game\n" +
                "How it fights: one use; 4 s after you tap, a huge bomb levels everything within about 27 m.\n" +
                "Strong / weak: wipes out whole groups and towers and takes a big bite out of a [[boss]]; aircraft are safe.\n" +
                "Tip: save it for a boss, or for the moment a huge enemy wave [[bunches up]] on an objective.",
                "[[Bom MOAB]] · vật phẩm · vụ nổ lớn nhất trò chơi\n" +
                "Cách đánh: dùng một lần; 4 giây sau khi chạm, quả bom khổng lồ san phẳng mọi thứ trong khoảng 27 m.\n" +
                "Mạnh / yếu: xóa sổ cả cụm quân và tháp canh, cắn một miếng lớn vào máu [[trùm]]; máy bay thì an toàn.\n" +
                "Mẹo: để dành cho trùm, hoặc lúc cả đợt địch [[dồn cục]] trên một cứ điểm."),
            ["guide.cluster_strike"] = (
                "[[Cluster bombs]] · item · covers a wide strip\n" +
                "How it fights: one use; forty [[bomblets]] carpet a 60 m strip, 20 m wide, in the direction you drag.\n" +
                "Strong / weak: great against spread-out light vehicles and artillery; each bomblet is small, so heavy tanks take little.\n" +
                "Tip: drag it along the enemy's rear, where their [[artillery]] and support trucks sit.",
                "[[Bom chùm]] · vật phẩm · phủ một dải rộng\n" +
                "Cách đánh: dùng một lần; bốn mươi [[bom con]] rải thảm một dải dài 60 m, rộng 20 m, theo hướng bạn kéo.\n" +
                "Mạnh / yếu: rất tốt với xe nhẹ và pháo binh dàn trải; mỗi bom con nhỏ nên tăng hạng nặng ít hề hấn.\n" +
                "Mẹo: kéo dọc phía sau đội hình địch, nơi [[pháo binh]] và xe hỗ trợ của chúng đứng."),
            ["guide.reinforcements"] = (
                "[[Airdropped armour]] · item · three free vehicles\n" +
                "How it fights: one use; 3 s after you tap, two battle tanks and an IFV [[drop in]] at that spot, at no CP cost.\n" +
                "Strong / weak: puts a strong group anywhere at once; once down, they are ordinary vehicles.\n" +
                "Tip: drop them on an [[objective]] you must hold, or right behind the enemy's artillery.",
                "[[Tiếp viện thả dù]] · vật phẩm · ba xe miễn phí\n" +
                "Cách đánh: dùng một lần; 3 giây sau khi chạm, hai tăng chủ lực và một xe chiến đấu bộ binh [[thả dù]] xuống điểm đó, không tốn CP.\n" +
                "Mạnh / yếu: có ngay một cụm quân mạnh ở bất kỳ đâu; tiếp đất rồi thì là xe bình thường.\n" +
                "Mẹo: thả xuống [[cứ điểm]] cần giữ, hoặc ngay sau lưng pháo binh địch."),
            ["guide.field_repair"] = (
                "[[Field repair]] · item · heals the whole army\n" +
                "How it fights: one use; every vehicle you have, anywhere on the map, [[repairs]] half its health over 5 s.\n" +
                "Strong / weak: turns a losing battle around; wasted if your army is still healthy.\n" +
                "Tip: use it in the middle of a big fight, when most of your vehicles are [[damaged]].",
                "[[Sửa chữa toàn quân]] · vật phẩm · hồi máu cả đội quân\n" +
                "Cách đánh: dùng một lần; mọi xe của ta, ở bất kỳ đâu trên bản đồ, được [[hồi]] một nửa máu trong 5 giây.\n" +
                "Mạnh / yếu: lật ngược trận đang thua; phí nếu quân ta còn khỏe.\n" +
                "Mẹo: dùng giữa trận đánh lớn, khi phần lớn xe ta đã [[mất máu]]."),
            ["guide.emp_blast"] = (
                "[[EMP blast]] · item · stuns the enemy\n" +
                "How it fights: one use; 2 s after you tap, every enemy ground vehicle within 20 m is [[stunned]] for 6 s: no driving, no firing.\n" +
                "Strong / weak: freezes a whole enemy push; aircraft and bosses are not affected.\n" +
                "Tip: fire it on the enemy's tank line, then hit the frozen group with artillery or an [[airstrike]].",
                "[[Bom EMP]] · vật phẩm · làm tê liệt địch\n" +
                "Cách đánh: dùng một lần; 2 giây sau khi chạm, mọi xe mặt đất địch trong 20 m bị [[choáng]] 6 giây: không chạy, không bắn.\n" +
                "Mạnh / yếu: đóng băng cả một đợt tấn công của địch; không tác dụng với máy bay và trùm.\n" +
                "Mẹo: ném vào tuyến xe tăng địch, rồi nện cụm bị đóng băng bằng pháo binh hoặc [[không kích]]."),
            ["guide.shield_dome"] = (
                "[[Shield dome]] · item · protects your army\n" +
                "How it fights: one use; your vehicles within 16 m take 70% less damage for 10 s.\n" +
                "Strong / weak: saves a group from a boss, a barrage or a big strike; it only covers vehicles inside when it goes up.\n" +
                "Tip: drop it on your [[tank line]] just as a big fight starts.",
                "[[Khiên vòm]] · vật phẩm · che chắn quân ta\n" +
                "Cách đánh: dùng một lần; xe ta trong vòng 16 m giảm 70% sát thương nhận vào trong 10 giây.\n" +
                "Mạnh / yếu: cứu cụm quân khỏi trùm, loạt pháo hoặc đòn đánh lớn; chỉ che những xe đứng bên trong lúc khiên bật lên.\n" +
                "Mẹo: thả lên [[tuyến xe tăng]] ngay khi trận đánh lớn bắt đầu."),
            ["guide.gunship_support"] = (
                "[[Gunship on call]] · item · an AC-130 for 30 s\n" +
                "How it fights: one use; a sky gunship arrives and [[orbits]] for 30 s, firing its 105, 40 and 25 mm guns at ground targets.\n" +
                "Strong / weak: devastating on ground forces; it cannot hit aircraft, and enemy SAMs and fighters can shoot it down.\n" +
                "Tip: call it over the main ground fight once the enemy's [[anti-air]] is cleared.",
                "[[Pháo đài bay yểm trợ]] · vật phẩm · AC-130 trong 30 giây\n" +
                "Cách đánh: dùng một lần; pháo đài bay tới và [[bay vòng]] 30 giây, pháo 105, 40 và 25 mm nã vào mục tiêu mặt đất.\n" +
                "Mạnh / yếu: tàn phá quân mặt đất; không bắn được máy bay, tên lửa phòng không và tiêm kích địch có thể bắn hạ nó.\n" +
                "Mẹo: gọi xuống trận đánh chính khi [[phòng không]] địch đã bị dọn sạch."),
        };
    }
}
