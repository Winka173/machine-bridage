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
                "[[Scout jeep]] · very light armour · fast and cheap\n" +
                "How it fights: a short-range machine gun fired on the move. Its long sight [[spots]] enemies, and it [[captures]] points at double speed.\n" +
                "Strong / weak: beats [[artillery]] and support trucks caught alone; loses to any armoured car, tank or tower.\n" +
                "Tip: send two early to grab empty points, then keep them ahead of your artillery as spotters.",
                "[[Xe trinh sát hạng nhẹ]] · giáp rất mỏng · nhanh và rẻ\n" +
                "Cách đánh: súng máy tầm gần, vừa chạy vừa bắn. Nhìn xa để [[phát hiện]] địch cho cả quân, [[chiếm cứ điểm]] nhanh gấp đôi.\n" +
                "Mạnh / yếu: diệt được [[pháo binh]] và xe hỗ trợ đi lẻ; thua mọi xe bọc thép, xe tăng và tháp canh.\n" +
                "Mẹo: tung hai chiếc đầu trận để chiếm cứ điểm trống, sau đó cho đi trước làm mắt cho pháo binh."),
            ["guide.armored_car"] = (
                "[[Armoured car]] · light armour · fast raider\n" +
                "How it fights: a 25 mm autocannon fired on the move at ground and air, best on [[light vehicles]] and helicopters; [[captures]] points 2× as fast.\n" +
                "Strong / weak: beats scouts, artillery, [[AA trucks]] and support vehicles; its rounds bounce off tanks and towers, which beat it.\n" +
                "Tip: go round the flank of the enemy line to hunt their artillery and support trucks.",
                "[[Xe bọc thép bánh lốp]] · giáp nhẹ · đột kích nhanh\n" +
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
                "[[Amphibious light tank]] · heavy armour · cheap and quick\n" +
                "How it fights: a 57 mm [[armour-piercing]] gun on the move, the shortest-ranged tank; its coaxial MG shoots [[aircraft]] once the ground is clear.\n" +
                "Strong / weak: beats [[light vehicles]], scouts and AA trucks; loses to heavier tanks, tank hunters and attack helicopters.\n" +
                "Tip: a cheap early answer to enemy armoured cars; swap it for battle tanks once you have the CP.",
                "[[Tăng nhẹ lội nước]] · giáp dày · rẻ và nhanh\n" +
                "Cách đánh: pháo 57 mm [[xuyên giáp]] vừa chạy vừa bắn, tầm ngắn nhất trong các xe tăng; súng đồng trục bắn [[máy bay]] khi mặt đất đã sạch.\n" +
                "Mạnh / yếu: thắng [[xe nhẹ]], trinh sát và xe phòng không; thua tăng nặng hơn, xe diệt tăng và trực thăng tấn công.\n" +
                "Mẹo: lựa chọn rẻ để chặn xe bọc thép địch đầu trận; có CP thì thay bằng tăng chủ lực."),
            ["guide.main_battle_tank"] = (
                "[[Main battle tank]] · heavy armour · the backbone of the army\n" +
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
                "[[Twin-gun tank]] · heavy armour · tank hunter\n" +
                "How it fights: two 120 mm guns fire almost together, a [[double shot]] at 34 m, then a long reload (7 s); a quick turret, faster than the heavy tank; front armour 3.\n" +
                "Strong / weak: its opening shot wins duels with battle tanks and heavy tanks; slow to fire again, so tank hunters, helicopters and groups of light vehicles wear it down.\n" +
                "Tip: open the fight with it on the enemy's heaviest tank, then let the others cover its reload.",
                "[[Tăng hai nòng]] · giáp dày · săn tăng\n" +
                "Cách đánh: hai pháo 120 mm bắn gần như cùng lúc, một [[phát đôi]] ở 34 m, rồi nạp lâu (7 giây); tháp xoay nhanh, chạy nhanh hơn tăng nặng; giáp trước cấp 3.\n" +
                "Mạnh / yếu: phát mở màn thắng tay đôi với tăng chủ lực và tăng nặng; bắn lại chậm, nên xe diệt tăng, trực thăng và bầy xe nhẹ bào mòn được nó.\n" +
                "Mẹo: cho nó mở màn vào chiếc tăng nặng nhất của địch, để các xe khác che lúc nó nạp đạn."),
            ["guide.turtle_tank"] = (
                "[[Turtle tank]] · heavy armour under a steel shed · drone-proof\n" +
                "How it fights: a 120 mm gun that cannot turn: it aims with the whole hull. The shed stops 80% of [[drone]] damage; its roller sets off [[mines]].\n" +
                "Strong / weak: walks through FPV swarms, Lancets and minefields, and beats light vehicles; heavy tanks and tank destroyers beat it.\n" +
                "Tip: lead with it against drone carriers and minelayers; it is slow, so keep the others behind it.",
                "[[Tăng mái che]] · giáp dày dưới mái thép · chống drone\n" +
                "Cách đánh: pháo 120 mm không xoay được, phải quay cả thân để ngắm. Mái thép chặn 80% sát thương [[drone]], trục lăn kích nổ [[mìn]] vô hại.\n" +
                "Mạnh / yếu: đi xuyên bầy FPV, Lancet và bãi mìn, thắng xe nhẹ; thua tăng hạng nặng và xe diệt tăng.\n" +
                "Mẹo: cho đi đầu khi địch có xe drone và xe rải mìn; nó chậm, để các xe khác theo sau."),
            ["guide.bmpt"] = (
                "[[Tank support vehicle]] · heavy armour · many guns\n" +
                "How it fights: twin 30 mm cannons (ground and air), paired Ataka [[anti-tank missiles]] from 40 m, and [[grenade launchers]] firing to both sides.\n" +
                "Strong / weak: clears [[light vehicles]], scouts, helicopters and AA round your tanks, and hurts tanks; heavy tanks and tank hunters beat it.\n" +
                "Tip: drive it next to your battle tanks: it kills what they are bad at hitting.",
                "[[Xe hỗ trợ tăng]] · giáp dày · nhiều vũ khí\n" +
                "Cách đánh: pháo đôi 30 mm (bắn cả đất lẫn trời), [[tên lửa chống tăng]] Ataka bắn cặp từ 40 m, và [[súng phóng lựu]] bắn sang hai bên.\n" +
                "Mạnh / yếu: dọn [[xe nhẹ]], trinh sát, trực thăng và phòng không quanh xe tăng ta, hại được cả xe tăng; thua tăng nặng và xe diệt tăng.\n" +
                "Mẹo: cho chạy cạnh tăng chủ lực: nó hạ những gì xe tăng khó bắn trúng."),
            ["guide.heavy_tank"] = (
                "[[Heavy tank]] · thick armour · breakthrough\n" +
                "How it fights: a 152 mm gun that loads [[armour-piercing]] for armour and [[high explosive]] for structures and groups of light vehicles on its own; a 30 mm autocannon beside it answers [[helicopters]]. Front armour 4, sides 3.\n" +
                "Strong / weak: outlasts every tank in a head-on fight and hits [[fortifications]] hardest; slow, so [[tank hunters]], artillery and aircraft are its bane.\n" +
                "Tip: the spearhead against defences and the anchor of a line; escort it with AA and never send it alone.",
                "[[Tăng hạng nặng]] · giáp rất dày · đột phá\n" +
                "Cách đánh: pháo 152 mm tự đổi [[đạn xuyên]] khi bắn xe có giáp và [[đạn nổ mạnh]] khi bắn công trình hoặc cụm xe nhẹ; pháo 30 mm bên cạnh đáp trả [[trực thăng]]. Giáp trước cấp 4, hông cấp 3.\n" +
                "Mạnh / yếu: trụ lâu nhất khi đối đầu và phá [[công sự]] mạnh nhất; chậm, nên sợ [[xe diệt tăng]], pháo binh và máy bay.\n" +
                "Mẹo: làm mũi nhọn đánh công sự và giữ tuyến; cho phòng không đi kèm và đừng để đi một mình."),
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
                "[[Siege mortar]] · thick front armour · slow · 15 CP\n" +
                "How it fights: two modes. On its tracks it is a [[tank]] whose 105 mm gun fires on the move. Standing with an enemy in reach, or on guard, it [[sieges]] in 2.5 s: braces down, turret up, and a 240 mm mortar lobs 450-damage bombs from 16 to 70 m with a 9 m blast, 2× on towers and buildings; 10 bombs, then a reload. It packs up in 2.5 s to move, or when enemies get inside its 16 m.\n" +
                "Strong / weak: shells [[fortifications]], tank lines and packed groups from beyond their reach; fast vehicles that get inside its minimum reach, aircraft and flank attacks catch it sieged.\n" +
                "Tip: let it siege just outside the enemy's reach with a screen in front; it cannot fire while it sieges or packs up.",
                "[[Pháo cối công thành]] · giáp trước dày · chậm · 15 CP\n" +
                "Cách đánh: hai chế độ. Khi di chuyển là một [[xe tăng]] có pháo 105 mm bắn khi đang chạy. Dừng lại khi có địch trong tầm, hoặc khi canh giữ, nó [[vào thế công thành]] trong 2,5 giây: hạ chân chống, nâng tháp pháo, cối 240 mm ném đạn 450 sát thương xa từ 16 đến 70 m, nổ rộng 9 m, gấp đôi lên tháp và công trình; 10 quả rồi nạp lại. Thu lại mất 2,5 giây để đi tiếp, hoặc khi địch lọt vào trong 16 m.\n" +
                "Mạnh / yếu: nã [[công sự]], tuyến xe tăng và đội hình dày từ ngoài tầm của chúng; sợ xe nhanh lọt vào trong tầm tối thiểu, máy bay và bị đánh vào sườn khi đang công thành.\n" +
                "Mẹo: cho nó vào thế ngay ngoài tầm địch, có quân chắn phía trước; khi đang hạ hay thu chân chống nó không bắn được."),
            ["guide.armored_bulldozer"] = (
                "[[Armoured bulldozer]] · heavy armour · breaks bases open\n" +
                "How it fights: only a roof machine gun; its [[blade]] rams towers, bunkers and buildings at [[three times]] the damage (4 m), ploughs [[dragon's teeth]] flat as it drives into them and takes half a mine's blast.\n" +
                "Strong / weak: the best at tearing down defences up close; it barely scratches tanks, and tank hunters, ATGMs and anything that outranges it kill it on the way in.\n" +
                "Tip: send it in front of the tanks when they push into a base; it does not clear mines (that is the engineer's job) and it is no substitute for a turtle tank as the line's shield.",
                "[[Xe ủi bọc thép]] · giáp dày · phá mở căn cứ\n" +
                "Cách đánh: chỉ có súng máy trên nóc; [[lưỡi ủi]] húc tháp, lô cốt và nhà cửa với sát thương [[gấp ba]] (4 m), ủi phẳng [[răng rồng]] khi lao qua, và chỉ nhận một nửa sức nổ của mìn.\n" +
                "Mạnh / yếu: phá công sự ở cự ly gần tốt nhất; gần như không làm gì được xe tăng, và xe diệt tăng, tên lửa chống tăng cùng mọi thứ bắn xa hơn diệt nó trên đường lao vào.\n" +
                "Mẹo: cho đi trước xe tăng khi tấn công vào căn cứ; nó không gỡ mìn (việc của công binh) và không thay được tăng rùa để che chắn cho đội hình."),
            ["guide.tank_destroyer"] = (
                "[[Tank destroyer]] · heavy armour · long range (40 m)\n" +
                "How it fights: a 125 mm [[armour-piercing]] gun (as on the 2S25 Sprut), fired on the move, that outranges battle tanks and reloads faster; plus a roof MG.\n" +
                "Strong / weak: kills [[tanks]], heavy tanks and [[bosses]] from outside their reach; fears artillery, and light cars that close in.\n" +
                "Tip: keep it just behind your tanks so it fires first; the best answer to heavy armour and bosses.",
                "[[Pháo chống tăng tự hành]] · giáp dày · tầm xa (40 m)\n" +
                "Cách đánh: pháo 125 mm [[xuyên giáp]] (như pháo tự hành 2S25), vừa chạy vừa bắn, xa hơn và nạp nhanh hơn pháo tăng chủ lực; súng máy nóc cho mục tiêu nhỏ.\n" +
                "Mạnh / yếu: hạ [[xe tăng]], tăng hạng nặng và [[boss]] từ ngoài tầm với của chúng; sợ pháo binh và xe nhẹ áp sát.\n" +
                "Mẹo: để ngay sau hàng xe tăng để nó bắn trước; khắc tinh của thiết giáp nặng và boss."),
            ["guide.fpv_carrier"] = (
                "[[FPV drone carrier]] · light armour · tank hunter at long range\n" +
                "How it fights: stops and launches [[kamikaze drones]] one after another, every few seconds, that dive onto armour 12–75 m away; sixteen, then a short reload.\n" +
                "Strong / weak: wrecks [[tanks]] and heavy tanks from afar; APS tanks, laser AA and jammers stop its drones, and turtle tanks shrug them off.\n" +
                "Tip: fire from behind your line at the enemy's heaviest tanks, well out of reach of their guns.",
                "[[Xe phóng drone FPV]] · giáp mỏng · diệt tăng tầm xa\n" +
                "Cách đánh: dừng lại rồi phóng lần lượt từng chiếc [[drone cảm tử]], vài giây một chiếc, lao xuống xe bọc thép cách 12–75 m; hết mười sáu chiếc thì nạp lại một lúc.\n" +
                "Mạnh / yếu: phá nát [[xe tăng]] và tăng nặng từ xa; tăng APS, xe la-de phòng không và xe gây nhiễu chặn drone, tăng mái che gần như miễn nhiễm.\n" +
                "Mẹo: bắn từ sau tuyến ta vào xe tăng nặng nhất của địch, giữ ngoài tầm pháo của chúng."),
            ["guide.lancet_truck"] = (
                "[[Loitering munition truck]] · light armour · long reach (85 m)\n" +
                "How it fights: stops and launches Lancet [[drones]] one at a time that fly up to 85 m and dive onto a target: [[double damage]] on artillery and on anything parked for 3 s; six, then a reload.\n" +
                "Strong / weak: made for [[artillery]], launchers and SAMs behind the line, and parked tanks; APS, laser AA and jammers stop its drones.\n" +
                "Tip: let scouts, a UAV scan or a counter-battery radar find the enemy's guns, then send the Lancets after them.",
                "[[Xe phóng đạn lảng vảng]] · giáp mỏng · tầm với xa (85 m)\n" +
                "Cách đánh: dừng lại rồi phóng từng chiếc [[drone]] Lancet bay tới 85 m rồi lao xuống mục tiêu: [[gấp đôi sát thương]] lên pháo binh và mọi xe đứng yên quá 3 giây; sáu chiếc rồi nạp lại.\n" +
                "Mạnh / yếu: chuyên diệt [[pháo binh]], giàn phóng và tên lửa phòng không phía sau tuyến, cả xe tăng đứng yên; tăng APS, xe la-de phòng không và xe gây nhiễu chặn được drone.\n" +
                "Mẹo: cho trinh sát, UAV quét hoặc radar phản pháo tìm pháo địch trước, rồi thả Lancet săn chúng."),
            ["guide.railgun_truck"] = (
                "[[Railgun truck]] · light armour · very long range (90 m)\n" +
                "How it fights: stands still and [[charges]] for 0.9 s (the coils glow), then fires a slug that [[pierces]] every vehicle on its line, out to 90 m.\n" +
                "Strong / weak: cuts through lines of [[tanks]] and heavy tanks from far away; slow to fire, and anything that reaches it wins.\n" +
                "Tip: line it up on a road or a choke point where enemies come single file; give it spotters.",
                "[[Xe pháo điện từ]] · giáp mỏng · tầm rất xa (90 m)\n" +
                "Cách đánh: đứng yên [[nạp năng lượng]] 0,9 giây (cuộn dây phát sáng), rồi bắn viên đạn [[xuyên thủng]] mọi xe trên đường bay, xa tới 90 m.\n" +
                "Mạnh / yếu: xuyên thủng cả hàng [[xe tăng]] và tăng nặng từ rất xa; bắn chậm, bị áp sát là thua.\n" +
                "Mẹo: ngắm dọc con đường hoặc cửa ải nơi địch đi thành hàng; cần đồng đội soi mục tiêu."),
            ["guide.vbied"] = (
                "[[Armoured car bomb]] · welded armour · one-shot kamikaze\n" +
                "How it fights: races into the enemy and [[blows itself up]]: 700 damage over 7.5 m, [[half]] on towers and buildings. Shot on the way, it still explodes where it dies.\n" +
                "Strong / weak: wrecks artillery, support trucks and [[groups]] of light vehicles; fast guns and armoured cars stop it, and a base shrugs off a stream of them.\n" +
                "Tip: send it behind a tank push or through smoke so it reaches its target in one piece.",
                "[[Xe bom bọc thép]] · giáp hàn · dùng một lần\n" +
                "Cách đánh: lao thẳng vào địch rồi [[tự nổ]]: 700 sát thương trong bán kính 7,5 m, [[một nửa]] lên tháp và công trình. Bị bắn hạ giữa đường thì nổ ngay tại chỗ.\n" +
                "Mạnh / yếu: phá nát pháo binh, xe hỗ trợ và [[cụm xe nhẹ]]; súng bắn nhanh và xe bọc thép chặn được nó, và căn cứ chịu được cả dòng xe bom.\n" +
                "Mẹo: cho chạy sau đợt xe tăng hoặc xuyên qua màn khói để tới mục tiêu nguyên vẹn."),

            // Artillery.
            ["guide.mortar_carrier"] = (
                "[[Mortar carrier]] · light armour · cheap indirect fire (55 m)\n" +
                "How it fights: stops and lobs 120 mm [[high-explosive]] bombs over walls and houses; its sight is short, so it fires at what allies spot.\n" +
                "Strong / weak: good against [[towers]], tank hunters and armour standing still; helpless against anything that reaches it.\n" +
                "Tip: its minimum range is only 10 m, closer than the big guns; tuck it behind houses.",
                "[[Xe cối tự hành]] · giáp mỏng · hỏa lực cầu vồng giá rẻ (55 m)\n" +
                "Cách đánh: dừng lại rồi bắn đạn cối 120 mm [[nổ mạnh]] qua tường và nhà; tầm nhìn ngắn nên bắn vào mục tiêu đồng đội phát hiện.\n" +
                "Mạnh / yếu: tốt với [[tháp canh]], xe diệt tăng và thiết giáp đứng yên; bó tay khi bị áp sát.\n" +
                "Mẹo: tầm tối thiểu chỉ 10 m, gần hơn các pháo lớn; hãy nấp sau nhà cửa."),
            ["guide.artillery"] = (
                "[[SP howitzer]] · light armour · long range (90 m)\n" +
                "How it fights: stops, lobs three 155 mm [[high-explosive]] shells over cover, then [[moves 15-20 m]] before it fires again, so counter-battery fire lands on an empty spot; it cannot hit closer than 25 m.\n" +
                "Strong / weak: breaks towers, heavy tanks and tank hunters from afar, and on a [[marked]] target (a laser designator, a counter-battery radar, a UAV scan) its shells barely scatter; scouts, armoured cars and aircraft that reach it win easily.\n" +
                "Tip: pair it with a recon UAV or a laser designator: marked targets are hit almost dead on.",
                "[[Lựu pháo tự hành]] · giáp mỏng · tầm xa (90 m)\n" +
                "Cách đánh: dừng lại, nã ba quả đạn 155 mm [[nổ mạnh]] cầu vồng qua vật cản rồi [[dời 15–20 m]] mới bắn tiếp, nên đạn phản pháo rơi vào chỗ trống; không bắn được gần hơn 25 m.\n" +
                "Mạnh / yếu: phá công sự, tăng hạng nặng và xe diệt tăng từ xa, bắn mục tiêu [[bị đánh dấu]] (chỉ thị la-de, radar phản pháo, UAV quét) gần như không tản mát; trinh sát, xe bọc thép và máy bay áp sát là nó thua.\n" +
                "Mẹo: đi cùng UAV trinh sát hoặc chỉ thị la-de: mục tiêu bị đánh dấu trúng gần như tuyệt đối."),
            ["guide.rocket_technical"] = (
                "[[Rocket technical]] · paper armour · cheap and fast\n" +
                "How it fights: stops and fires a loose [[salvo]] of eight rockets up to 48 m; six salvos, then it reloads standing still. A machine gun too.\n" +
                "Strong / weak: hits [[towers]] and groups on the cheap; it dies to almost any gun that reaches it.\n" +
                "Tip: it is fast and [[captures]] points at double speed: use it early, then keep it well back.",
                "[[Bán tải rốc-két]] · giáp mỏng như giấy · rẻ và nhanh\n" +
                "Cách đánh: dừng lại rồi phóng một [[loạt]] tám rốc-két khá tản mát tới 48 m; hết sáu loạt phải đứng yên nạp lại. Có thêm súng máy.\n" +
                "Mạnh / yếu: phá [[tháp canh]] và cụm địch với giá rẻ; chết trước gần như mọi khẩu súng với tới nó.\n" +
                "Mẹo: xe nhanh, [[chiếm cứ điểm]] nhanh gấp đôi: dùng sớm, sau đó giữ thật xa phía sau."),
            ["guide.mlrs"] = (
                "[[Guided MLRS]] · light armour · very long range (110 m)\n" +
                "How it fights: stops and fires an accurate [[salvo]] of six rockets from up to 110 m; after four salvos it must [[reload]] standing still.\n" +
                "Strong / weak: wrecks towers, heavy tanks and gun lines from beyond their reach; anything fast that gets close kills it.\n" +
                "Tip: aim it at clustered enemies or defences, with an engineer nearby to re-arm it faster.",
                "[[Pháo phản lực dẫn đường]] · giáp mỏng · tầm rất xa (110 m)\n" +
                "Cách đánh: dừng lại rồi phóng một [[loạt]] sáu rốc-két chính xác từ tới 110 m; sau bốn loạt phải đứng yên [[nạp đạn]].\n" +
                "Mạnh / yếu: phá công sự, tăng hạng nặng và trận địa pháo từ ngoài tầm với; bất kỳ xe nhanh nào áp sát cũng hạ được nó.\n" +
                "Mẹo: nhắm vào chỗ địch tụ đông hoặc công trình; để xe công binh gần đó giúp nạp đạn nhanh hơn."),
            ["guide.thermobaric_launcher"] = (
                "[[Thermobaric launcher]] · heavy armour · short-range area killer\n" +
                "How it fights: stops and fires twelve [[thermobaric]] rockets that blanket an area 12–38 m away; four salvos, then a reload standing still.\n" +
                "Strong / weak: wipes out [[groups]], towers and anything bunched up; it must get fairly close, and aircraft catch it easily.\n" +
                "Tip: its armour lets it follow the tanks: roll it up behind them and fire into the point the enemy holds.",
                "[[Pháo phản lực nhiệt áp]] · giáp dày · hủy diệt vùng ở tầm gần\n" +
                "Cách đánh: dừng lại rồi phóng 12 rốc-két [[nhiệt áp]] phủ kín một vùng cách 12–38 m; bốn loạt rồi phải đứng yên nạp lại.\n" +
                "Mạnh / yếu: quét sạch [[cụm địch]], tháp canh và mọi thứ đứng dồn; phải tiến khá gần, dễ bị máy bay bắt.\n" +
                "Mẹo: giáp đủ dày để đi sau xe tăng: tiến sát sau lưng chúng rồi nã vào cứ điểm địch đang giữ."),
            ["guide.heavy_rocket_artillery"] = (
                "[[Heavy MLRS]] · light armour · extreme range (140 m)\n" +
                "How it fights: stops and fires twelve 300 mm [[rockets]] 30–140 m away, with big blasts; three salvos, then a long reload in place.\n" +
                "Strong / weak: hits [[fortifications]], artillery and massed armour from across the map; defenceless if anything reaches it.\n" +
                "Tip: it outranges almost everything: keep it in your corner of the map and give it [[spotters]].",
                "[[Pháo phản lực hạng nặng]] · giáp mỏng · tầm cực xa (140 m)\n" +
                "Cách đánh: dừng lại rồi phóng 12 [[rốc-két]] 300 mm vào vùng cách 30–140 m, sức nổ lớn; ba loạt rồi nạp lại lâu tại chỗ.\n" +
                "Mạnh / yếu: đánh [[công sự]], pháo binh và cụm thiết giáp từ bên kia bản đồ; không có khả năng tự vệ khi bị áp sát.\n" +
                "Mẹo: bắn xa hơn gần như mọi thứ: giữ ở góc căn cứ và cho [[trinh sát]] soi mục tiêu."),
            ["guide.ballistic_launcher"] = (
                "[[Tactical ballistic launcher]] · light armour · reaches almost the whole map\n" +
                "How it fights: stops and launches a pair of [[ballistic missiles]] at targets 40–180 m away, each a huge blast; two pairs, then a long reload.\n" +
                "Strong / weak: erases [[fortifications]], artillery parks and big groups; slow to fire and helpless up close.\n" +
                "Tip: save it for the biggest crowd of enemies or a key tower; allies must see the target first.",
                "[[Xe phóng tên lửa chiến thuật]] · giáp mỏng · với gần hết bản đồ\n" +
                "Cách đánh: dừng lại rồi phóng một cặp [[tên lửa đạn đạo]] vào mục tiêu cách 40–180 m, mỗi quả nổ cực lớn; hai cặp rồi nạp lại lâu.\n" +
                "Mạnh / yếu: xóa sổ [[công sự]], trận địa pháo và cụm quân đông; bắn chậm và bó tay khi bị áp sát.\n" +
                "Mẹo: để dành cho cụm địch đông nhất hoặc tháp quan trọng; đồng đội phải thấy mục tiêu trước."),
            ["guide.shahed_truck"] = (
                "[[Long-range drone launcher]] · light armour · strikes across the map (150 m)\n" +
                "How it fights: stops and sends slow [[kamikaze drones]] up to 150 m away one at a time, every few seconds, best at [[structures]].\n" +
                "Strong / weak: breaks towers, turrets and parked artillery far away; APS and laser AA shoot the slow drones down, jammers throw them off.\n" +
                "Tip: in Siege mode, aim it at the towers your tanks cannot reach yet.",
                "[[Xe phóng drone cảm tử tầm xa]] · giáp mỏng · đánh khắp bản đồ (150 m)\n" +
                "Cách đánh: dừng lại rồi phóng lần lượt từng chiếc [[drone cảm tử]] bay chậm xa tới 150 m, vài giây một chiếc, chuyên đánh [[công trình]].\n" +
                "Mạnh / yếu: phá tháp canh, ụ pháo và pháo binh đứng yên ở xa; APS và xe la-de phòng không bắn hạ drone chậm, xe gây nhiễu làm chúng lạc.\n" +
                "Mẹo: ở chế độ Công thành, nhắm vào những tháp mà xe tăng ta chưa với tới."),

            // Air defence.
            ["guide.zu23_technical"] = (
                "[[Flak technical]] · paper armour · fast pickup\n" +
                "How it fights: a twin 23 mm [[flak]] gun fired on the move at aircraft and light ground targets (32 m); [[captures]] points at double speed.\n" +
                "Strong / weak: tears up [[helicopters]], drones and scouts; tanks and armoured cars kill it in seconds.\n" +
                "Tip: an early, cheap answer to enemy helicopters; buy a proper AA vehicle later.",
                "[[Bán tải cao xạ]] · giáp mỏng như giấy · bán tải nhanh\n" +
                "Cách đánh: pháo đôi 23 mm [[cao xạ]] vừa chạy vừa bắn máy bay và xe nhẹ (32 m); [[chiếm cứ điểm]] nhanh gấp đôi.\n" +
                "Mạnh / yếu: xé nát [[trực thăng]], drone và trinh sát; xe tăng và xe bọc thép hạ nó trong vài giây.\n" +
                "Mẹo: đối sách rẻ và sớm trước trực thăng địch; về sau hãy mua xe phòng không thật sự."),
            ["guide.aa_vehicle"] = (
                "[[Self-propelled AA gun]] · light armour · guns and a missile\n" +
                "How it fights: twin 35 mm [[flak]] guns (36 m) fired on the move, and a short-range [[missile]] (44 m) that only goes for aircraft.\n" +
                "Strong / weak: tears apart [[helicopters]], drones and jets; its flak barely scratches armour, so tanks and armoured cars beat it.\n" +
                "Tip: keep one with every tank group: cheap insurance against enemy helicopters.",
                "[[Pháo cao xạ tự hành]] · giáp mỏng · pháo và tên lửa\n" +
                "Cách đánh: pháo đôi 35 mm [[cao xạ]] (36 m) bắn khi đang chạy, kèm [[tên lửa]] tầm ngắn (44 m) chỉ nhắm máy bay.\n" +
                "Mạnh / yếu: xé nát [[trực thăng]], drone và máy bay phản lực; đạn cao xạ gần như vô hại với giáp nên thua xe tăng và xe bọc thép.\n" +
                "Mẹo: kèm một chiếc với mỗi cụm xe tăng: rẻ mà chặn được trực thăng địch."),
            ["guide.heavy_aa"] = (
                "[[Gun–missile AA]] · light armour · fires on the move\n" +
                "How it fights: four 30 mm [[flak]] barrels (42 m) and anti-air [[missiles]] (44 m), fired on the move; its 60 m sight spots aircraft early.\n" +
                "Strong / weak: the best mobile shield against [[helicopters]] and jets; tanks and armoured cars beat it on the ground.\n" +
                "Tip: move it with the main group, so helicopters and attack jets never get a free run.",
                "[[Xe phòng không pháo – tên lửa]] · giáp mỏng · vừa chạy vừa bắn\n" +
                "Cách đánh: bốn nòng 30 mm [[cao xạ]] (42 m) và [[tên lửa]] phòng không (44 m), bắn cả khi đang chạy; tầm nhìn 60 m thấy máy bay từ sớm.\n" +
                "Mạnh / yếu: lá chắn di động tốt nhất trước [[trực thăng]] và máy bay; trên mặt đất thua xe tăng và xe bọc thép.\n" +
                "Mẹo: cho đi cùng đội hình chính để trực thăng và cường kích địch không được tự do tấn công."),
            ["guide.sam_launcher"] = (
                "[[Medium-range SAM]] · light armour · long-range air defence (55 m)\n" +
                "How it fights: stops and fires [[missiles]] in pairs at [[aircraft]] up to 55 m away; only a roof machine gun for the ground.\n" +
                "Strong / weak: swats helicopters, jets and bombers far out, even stand-off attack helicopters; tanks and armoured cars that reach it win easily.\n" +
                "Tip: park it behind the front line: one launcher covers a wide piece of sky.",
                "[[Xe tên lửa phòng không tầm trung]] · giáp mỏng · tầm xa (55 m)\n" +
                "Cách đánh: dừng lại rồi phóng [[tên lửa]] từng cặp vào [[máy bay]] cách tới 55 m; chỉ có súng máy nóc để đánh mặt đất.\n" +
                "Mạnh / yếu: bắn rụng trực thăng, máy bay phản lực và oanh tạc cơ từ xa, kể cả trực thăng tấn công bắn từ xa; xe tăng, xe bọc thép áp sát là nó thua.\n" +
                "Mẹo: đặt sau tuyến đầu: một bệ phóng che được cả một vùng trời rộng."),
            ["guide.iron_beam"] = (
                "[[Laser AA]] · light armour · shoots rounds down\n" +
                "How it fights: its [[laser]] burns down one drone, missile or rocket (artillery rockets too) aimed within 30 m of it every 1.2 s; between them it fires at aircraft (45 m).\n" +
                "Strong / weak: shields a group from ATGMs, Lancets, rocket artillery and helicopter missiles; shells and bullets pass, and it has nothing for the ground.\n" +
                "Tip: park it in the middle of your tanks when the enemy relies on missiles, drones or rockets.",
                "[[Xe la-de phòng không]] · giáp mỏng · bắn hạ đạn bay tới\n" +
                "Cách đánh: tia [[la-de]] đốt hạ một drone, tên lửa hoặc rốc-két (cả rốc-két pháo binh) nhắm vào trong vòng 30 m quanh nó, cứ 1,2 giây một quả; giữa các lần đó nó bắn máy bay (45 m).\n" +
                "Mạnh / yếu: che cả cụm quân khỏi tên lửa chống tăng, Lancet, pháo phản lực và tên lửa trực thăng; đạn pháo và đạn súng bay qua được, và nó không có gì đánh mặt đất.\n" +
                "Mẹo: đỗ giữa đội xe tăng khi địch dựa vào tên lửa, drone hoặc rốc-két."),

            // Support vehicles.
            ["guide.engineer_vehicle"] = (
                "[[Engineering vehicle]] · heavy armour · repairs\n" +
                "How it fights: only a roof MG; it [[repairs]] friendly vehicles within 14 m (2.5% health a second) and friendly towers at half that, clears the mines it sees, and breaks obstacles, slowly (the bulldozer is the quick way).\n" +
                "Strong / weak: keeps a tank line and a held base alive much longer; alone it fights poorly, and scouts or armoured cars pick it off.\n" +
                "Tip: park it just behind the front or among the towers you hold; the [[ammo carrier]] is the one that reloads launchers.",
                "[[Xe công binh]] · giáp dày · sửa chữa\n" +
                "Cách đánh: chỉ có súng máy nóc; [[sửa chữa]] xe ta trong vòng 14 m (2,5% máu mỗi giây) và tháp ta chậm bằng nửa, gỡ mìn nó thấy, phá vật cản nhưng chậm (xe ủi phá nhanh hơn).\n" +
                "Mạnh / yếu: giúp tuyến xe tăng và căn cứ đang giữ trụ lâu hơn hẳn; tự đánh thì yếu, trinh sát và xe bọc thép dễ bắt nạt nó.\n" +
                "Mẹo: đỗ ngay sau tuyến đầu hoặc giữa các tháp đang giữ; nạp đạn cho bệ phóng là việc của [[xe tiếp đạn]]."),
            ["guide.ammo_carrier"] = (
                "[[Ammo carrier]] · light armour · forward rearm point\n" +
                "How it fights: only a roof MG; empty launchers and missile carriers within 14 m [[reload three times as fast]], and helicopters within 12 m take their missiles and rockets on [[twice as fast]].\n" +
                "Strong / weak: keeps rocket artillery and helicopters firing; thin-skinned and it blows up hard, so keep it out of the fight.\n" +
                "Tip: park it behind the launchers; your commander sends empty launchers to it when the drive is quicker than reloading in place.",
                "[[Xe tiếp đạn]] · giáp mỏng · điểm nạp tiền phương\n" +
                "Cách đánh: chỉ có súng máy nóc; bệ phóng và xe tên lửa hết đạn trong vòng 14 m [[nạp nhanh gấp ba]], trực thăng trong vòng 12 m hồi tên lửa và rốc-két [[nhanh gấp đôi]].\n" +
                "Mạnh / yếu: giữ pháo phản lực và trực thăng bắn liên tục; giáp mỏng và nổ rất mạnh, nên giữ xa chỗ giao tranh.\n" +
                "Mẹo: đỗ sau các bệ phóng; chỉ huy tự đưa bệ phóng hết đạn tới nó khi đi tới đó nhanh hơn nạp tại chỗ."),
            ["guide.ew_jammer"] = (
                "[[EW jammer]] · light armour · scrambles guided weapons\n" +
                "How it fights: a roof MG only; enemy guided [[missiles]], drones and fire support aimed into its 32 m [[jamming]] bubble go wide.\n" +
                "Strong / weak: counters ATGM carriers, drone trucks, attack helicopters and enemy strikes; useless against guns and shells.\n" +
                "Tip: keep it in the middle of your army against missile- and drone-heavy enemies.",
                "[[Xe gây nhiễu điện tử]] · giáp mỏng · gây nhiễu vũ khí dẫn đường\n" +
                "Cách đánh: chỉ có súng máy nóc; [[tên lửa]], drone và hỏa lực yểm trợ của địch nhắm vào vùng [[gây nhiễu]] 32 m đều bị lệch.\n" +
                "Mạnh / yếu: khắc chế xe tên lửa chống tăng, xe drone, trực thăng và đòn yểm trợ địch; vô dụng trước súng và đạn pháo thường.\n" +
                "Mẹo: giữ ở giữa đội hình khi địch dùng nhiều tên lửa và drone."),
            ["guide.mine_layer"] = (
                "[[Minelayer]] · light armour · area denial\n" +
                "How it fights: a roof MG; as it drives it drops an [[anti-tank mine]] every 6 s (up to 8), and enemy vehicles that roll over one blow up.\n" +
                "Strong / weak: punishes [[tanks]] and columns that keep to one road; turtle tanks' rollers clear mines, and aircraft ignore them.\n" +
                "Tip: drive it back and forth across the lane the enemy uses, or round your objective.",
                "[[Xe rải mìn]] · giáp mỏng · khóa khu vực\n" +
                "Cách đánh: có súng máy nóc; khi chạy, cứ 6 giây thả một quả [[mìn chống tăng]] (tối đa 8), xe địch cán phải là nổ tung.\n" +
                "Mạnh / yếu: trừng phạt [[xe tăng]] và đoàn xe đi theo một lối; tăng mái che có trục lăn phá mìn, máy bay thì không sợ.\n" +
                "Mẹo: chạy qua lại trên con đường địch hay đi, hoặc quanh cứ điểm của ta."),
            ["guide.smoke_carrier"] = (
                "[[Smoke carrier]] · light armour · hides the army\n" +
                "How it fights: a roof MG; whenever an enemy is in range it lays an 11 m [[smoke]] cloud round itself that no one can see through.\n" +
                "Strong / weak: shields tanks and slow vehicles as they close in on [[long-range guns]]; it fights poorly itself.\n" +
                "Tip: lead a push with it towards tank destroyers or ATGM carriers so your tanks get close.",
                "[[Xe thả khói]] · giáp mỏng · che giấu đội quân\n" +
                "Cách đánh: có súng máy nóc; mỗi khi địch trong tầm, nó phủ [[màn khói]] 11 m quanh mình, không ai nhìn xuyên qua được.\n" +
                "Mạnh / yếu: che chở xe tăng và xe chậm khi áp sát [[pháo tầm xa]] của địch; tự nó đánh rất yếu.\n" +
                "Mẹo: cho chạy đầu đội hình khi tiến vào xe diệt tăng hoặc xe tên lửa chống tăng để xe tăng ta áp sát được."),

            // Helicopters.
            ["guide.scout_heli"] = (
                "[[Armed scout helicopter]] · very fast · fragile\n" +
                "How it fights: darts in with [[miniguns]] (short range, can hit aircraft too) and a seven-rocket pod; its sharp eyes [[spot]] for the army.\n" +
                "Strong / weak: shreds scouts, [[light vehicles]] and support trucks; tanks shrug it off, and any AA kills it quickly.\n" +
                "Tip: use it to hunt enemy support trucks and artillery behind their lines, away from AA.",
                "[[Trực thăng trinh sát vũ trang]] · rất nhanh · mong manh\n" +
                "Cách đánh: lao vào với [[súng máy nhiều nòng]] (tầm gần, bắn được cả máy bay) và giàn 7 rốc-két; mắt tinh giúp [[soi mục tiêu]] cho cả quân.\n" +
                "Mạnh / yếu: xé nát trinh sát, [[xe nhẹ]] và xe hỗ trợ; xe tăng gần như miễn nhiễm, gặp phòng không là rụng nhanh.\n" +
                "Mẹo: dùng để săn xe hỗ trợ và pháo binh sau lưng địch, tránh xa phòng không."),
            ["guide.attack_helicopter"] = (
                "[[Attack helicopter]] · flying · stand-off tank killer (55 m)\n" +
                "How it fights: Hellfire Longbow [[anti-tank missiles]] in pairs from 55 m; it hovers at the edge of that reach, round the side away from short-range anti-air; a 30 mm gun and rockets up close, two Stingers at aircraft; [[flares]].\n" +
                "Strong / weak: kills [[tanks]], heavy tanks and artillery from outside the reach of flak and short-range SAMs; long-range SAMs, long-range SAM sites and fighters outrange it.\n" +
                "Tip: it keeps its own distance: pair it with something that deals with long-range SAMs (a SEAD strike, artillery).",
                "[[Trực thăng tấn công]] · bay · diệt tăng từ xa (55 m)\n" +
                "Cách đánh: [[tên lửa chống tăng]] Hellfire Longbow bắn cặp từ 55 m; nó treo ở rìa tầm đó, vòng sang phía tránh phòng không tầm ngắn; pháo 30 mm và rốc-két khi gần, 2 Stinger bắn máy bay; có [[mồi nhiệt]].\n" +
                "Mạnh / yếu: hạ [[xe tăng]], tăng nặng và pháo binh từ ngoài tầm pháo cao xạ và tên lửa tầm ngắn; xe tên lửa phòng không tầm xa, trạm PK tầm xa và tiêm kích bắn xa hơn nó.\n" +
                "Mẹo: nó tự giữ khoảng cách: đi kèm thứ xử lý được tên lửa tầm xa (đòn SEAD, pháo binh)."),
            ["guide.gunship_heli"] = (
                "[[Armoured gunship helicopter]] · flying IFV · can take objectives\n" +
                "How it fights: opens with big [[rocket]] salvos, then a fixed 30 mm cannon and ATGMs; [[door gunners]] fire out of both sides. Drops flares.\n" +
                "Strong / weak: wrecks light vehicles, scouts and towers; AA vehicles and fighters are its danger, but it takes a lot to bring down.\n" +
                "Tip: the only helicopter that [[captures]] points: send it to grab an undefended objective across the map.",
                "[[Trực thăng vũ trang bọc giáp]] · xe bộ binh bay · chiếm được cứ điểm\n" +
                "Cách đánh: mở màn bằng loạt [[rốc-két]] lớn, rồi pháo 30 mm cố định và tên lửa chống tăng; [[xạ thủ]] bắn từ hai cửa hông. Có mồi nhiệt.\n" +
                "Mạnh / yếu: phá nát xe nhẹ, trinh sát và tháp canh; sợ xe phòng không và tiêm kích, nhưng rất lì đòn.\n" +
                "Mẹo: trực thăng duy nhất [[chiếm được cứ điểm]]: đưa nó đi chiếm điểm trống ở xa bên kia bản đồ."),

            // Fixed-wing aircraft and drones.
            ["guide.recon_drone"] = (
                "[[Recon UAV]] · flying · the longest sight in the game\n" +
                "How it fights: flies high with a 90 m sight, [[spotting]] targets for the whole army, and a light guided [[missile]] (50 m) for ground targets.\n" +
                "Strong / weak: picks off scouts and artillery, and lets your big guns fire at full range; fragile, any AA or fighter kills it.\n" +
                "Tip: pair it with howitzers, rocket artillery or ballistic missiles so they can hit what they cannot see.",
                "[[UAV trinh sát]] · bay · tầm nhìn xa nhất trò chơi\n" +
                "Cách đánh: bay cao với tầm nhìn 90 m, [[soi mục tiêu]] cho cả đội quân, kèm một [[tên lửa]] dẫn đường nhẹ (50 m) đánh mặt đất.\n" +
                "Mạnh / yếu: bắn tỉa trinh sát và pháo binh, giúp pháo ta bắn hết tầm; mong manh, gặp phòng không hay tiêm kích là rơi.\n" +
                "Mẹo: kết hợp với lựu pháo, pháo phản lực hoặc tên lửa đạn đạo để chúng bắn trúng thứ chúng không tự thấy."),
            ["guide.strike_drone"] = (
                "[[Strike UAV]] · flying · long sight\n" +
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
                "[[Attack jet]] · armoured · not a fighter\n" +
                "How it fights: [[strafing runs]] with its 30 mm cannon, 80 mm rocket pods and 250 kg [[bombs]] ({{stick}}), and two Kh-29 [[anti-tank missiles]] from 40 m; two R-60s only for self-defence against aircraft; [[flares]].\n" +
                "Strong / weak: smashes light vehicles, tanks, heavy tanks, artillery and [[towers]], and takes more hits than other jets; AA vehicles, SAMs and enemy fighters still bring it down.\n" +
                "Tip: send it at the enemy's armour push once their AA is thinned out; to clear the sky buy a fighter.",
                "[[Máy bay cường kích]] · bọc giáp · không phải tiêm kích\n" +
                "Cách đánh: bổ nhào [[càn quét]] bằng pháo 30 mm, giàn rốc-két 80 mm và [[bom]] 250 kg ({{stick}}), kèm hai [[tên lửa chống tăng]] Kh-29 từ 40 m; hai R-60 chỉ để tự vệ trước máy bay; có [[mồi nhiệt]].\n" +
                "Mạnh / yếu: đập nát xe nhẹ, xe tăng, tăng nặng, pháo binh và [[công sự]], chịu đòn tốt hơn máy bay khác; xe phòng không, tên lửa phòng không và tiêm kích địch vẫn hạ được.\n" +
                "Mẹo: tung vào mũi thiết giáp địch khi phòng không của chúng đã thưa; muốn giành bầu trời hãy mua tiêm kích."),
            ["guide.heavy_bomber"] = (
                "[[Strategic bomber]] · flying · carpet of bombs\n" +
                "How it fights: flies over and lays a stick of heavy [[bombs]] along its track ({{stick}}); fires [[cruise missiles]] from 110 m; tail guns shoot at aircraft.\n" +
                "Strong / weak: flattens [[towers]], artillery and groups of light vehicles; SAMs and fighters are its danger.\n" +
                "Tip: send it at enemy defences and gun lines once your fighters or AA have cleared the sky.",
                "[[Oanh tạc cơ chiến lược]] · bay · rải thảm bom\n" +
                "Cách đánh: bay qua và rải một dải [[bom]] nặng dọc đường bay ({{stick}}); phóng [[tên lửa hành trình]] từ 110 m; súng đuôi bắn máy bay.\n" +
                "Mạnh / yếu: san phẳng [[công sự]], pháo binh và cụm xe nhẹ; sợ tên lửa phòng không và tiêm kích.\n" +
                "Mẹo: tung vào công sự và trận địa pháo địch sau khi tiêm kích hoặc phòng không ta đã dọn sạch bầu trời."),
            ["guide.stealth_bomber"] = (
                "[[Stealth bomber]] · flying · hard to see\n" +
                "How it fights: three huge [[bombs]] per pass and JASSM missiles from 90 m; [[stealth]]: seen only close up, or just after it fires.\n" +
                "Strong / weak: destroys [[fortifications]], heavy tanks and artillery; once spotted, SAMs and fighters can still kill it.\n" +
                "Tip: use it on the enemy's best-defended point, where other aircraft would be shot down.",
                "[[Oanh tạc cơ tàng hình]] · bay · khó phát hiện\n" +
                "Cách đánh: mỗi lượt thả ba quả [[bom]] cực lớn, phóng tên lửa JASSM từ 90 m; [[tàng hình]]: chỉ bị thấy ở gần hoặc ngay sau khi bắn.\n" +
                "Mạnh / yếu: phá hủy [[công sự]], tăng hạng nặng và pháo binh; một khi lộ diện, tên lửa phòng không và tiêm kích vẫn hạ được.\n" +
                "Mẹo: dùng đánh vào cứ điểm phòng thủ mạnh nhất của địch, nơi máy bay khác sẽ bị bắn rơi."),
            ["guide.sky_gunship"] = (
                "[[Airborne gunship]] · flying · circles its target\n" +
                "How it fights: flies to where you send it and [[orbits]] the enemy there anticlockwise, about 22 m out, its 105, 40 and 25 mm guns all firing out of its left side at once.\n" +
                "Strong / weak: grinds down [[light vehicles]], tanks, artillery and towers; it cannot hit aircraft, so SAMs and fighters are its bane.\n" +
                "Tip: send it over a big ground fight after your AA or fighters have dealt with the enemy's.",
                "[[Pháo hạm bay]] · bay · lượn vòng quanh mục tiêu\n" +
                "Cách đánh: bay tới nơi bạn chỉ định và [[bay vòng]] ngược chiều kim đồng hồ quanh địch ở đó, cách chừng 22 m, pháo 105, 40 và 25 mm cùng bắn một lúc từ bên trái.\n" +
                "Mạnh / yếu: nghiền nát [[xe nhẹ]], xe tăng, pháo binh và tháp; không bắn được máy bay nên sợ tên lửa phòng không và tiêm kích.\n" +
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
                "How it fights: a 125 mm gun that hits from 46 m; with a target in range it fires a rapid [[barrage]] (2.2× rate), and pops [[smoke]] when hurt.\n" +
                "Strong / weak: deadly to tanks and heavy tanks; artillery, aircraft and fast light vehicles that close in beat it.\n" +
                "Tip: don't drive tanks straight at it; hit it with artillery or a helicopter, or rush it with armoured cars.",
                "[[Pháo chống tăng tinh nhuệ]] · chỉ phe địch · bắn xa hơn mọi xe tăng (46 m)\n" +
                "Cách đánh: pháo 125 mm bắn từ 46 m; có mục tiêu trong tầm là [[bắn dồn dập]] (nhanh gấp 2,2 lần), bị thương thì thả [[khói]].\n" +
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
                "Mạnh / yếu: phá nát xe tăng và tăng nặng từ xa; tăng APS, xe la-de phòng không và xe gây nhiễu chặn drone, xe nhanh áp sát là hạ được.\n" +
                "Mẹo: thấy vòng vàng thì dàn xe tăng ra, tung xe bọc thép hoặc trực thăng lao thẳng vào nó."),
            ["guide.elite_attack_jet"] = (
                "[[Elite attack jet]] · enemy only · long-lasting flares\n" +
                "How it fights: the attack jet's cannon, rockets and bombs ({{stick}}), with 60% more health; its [[flares]] come back every 14 s and last twice as long.\n" +
                "Strong / weak: guts ground columns and towers; flak guns ignore flares, and fighters catch it.\n" +
                "Tip: missiles struggle against it: answer with [[flak]] (AA vehicle, Tunguska) or a fighter.",
                "[[Cường kích tinh nhuệ]] · chỉ phe địch · mồi nhiệt bền\n" +
                "Cách đánh: pháo, rốc-két và bom như máy bay cường kích ({{stick}}), máu nhiều hơn 60%; [[mồi nhiệt]] 14 giây lại có và kéo dài gấp đôi.\n" +
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
                "Cách đánh: đạn 155 mm như lựu pháo tự hành, tầm 25–90 m, đánh đau hơn 15%, máu nhiều hơn 60%; có mục tiêu là [[bắn dồn dập]], cứ ba phát lại chạy 15–20 m.\n" +
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
                "[[Wheeled tank destroyer]] · light armour · fast (12 m/s)\n" +
                "How it fights: a 120 mm [[armour-piercing]] gun (as on the Centauro II) on the move out to 38 m, about 70 damage a second on heavy armour, [[+25%]] on a flank or rear.\n" +
                "Strong / weak: runs round tank lines and punishes their sides; its thin armour loses any straight fight with a tank, and autocannons shred it.\n" +
                "Tip: send it round the flank while your tanks hold the front: every hit on a side counts double work.",
                "[[Pháo xung kích bánh lốp]] · giáp mỏng · nhanh (12 m/s)\n" +
                "Cách đánh: pháo 120 mm [[xuyên giáp]] (như Centauro II) vừa chạy vừa bắn tới 38 m, khoảng 70 sát thương mỗi giây lên giáp dày, [[+25%]] khi trúng hông hoặc đuôi.\n" +
                "Mạnh / yếu: chạy vòng tuyến xe tăng và trừng phạt hai bên sườn; giáp mỏng nên đấu thẳng với tăng là thua, pháo tự động xé nát nó.\n" +
                "Mẹo: vòng qua sườn trong lúc xe tăng giữ mặt trước: phát nào trúng hông cũng đáng giá."),
            ["guide.counter_battery_radar"] = (
                "[[Counter-battery radar]] · light armour · finds the enemy's guns\n" +
                "How it fights: a roof MG only; any enemy artillery that fires within 120 m of it is [[revealed]] to your side for 8 s, and your artillery does [[+15%]] to it.\n" +
                "Strong / weak: turns the enemy's guns into targets for your own artillery, Lancets and aircraft; useless where the enemy has no artillery.\n" +
                "Tip: bring it with your own artillery or Lancets against an army of guns and rockets.",
                "[[Xe radar phản pháo]] · giáp mỏng · tìm pháo địch\n" +
                "Cách đánh: chỉ có súng máy trên nóc; pháo địch nào khai hỏa trong vòng 120 m quanh nó bị [[lộ vị trí]] với phe ta trong 8 giây, và pháo binh ta gây [[+15%]] sát thương lên nó.\n" +
                "Mạnh / yếu: biến pháo địch thành mục tiêu cho pháo, Lancet và máy bay của ta; vô dụng khi địch không có pháo binh.\n" +
                "Mẹo: mang theo cùng pháo binh hoặc Lancet khi địch dựa vào pháo và rốc-két."),
            ["guide.long_sam"] = (
                "[[Long-range SAM]] · light armour · 95 m reach\n" +
                "How it fights: stops and fires one big missile every 8 s at [[aircraft only]] out to 95 m (600 damage, not closer than 20 m).\n" +
                "Strong / weak: outranges every aircraft's weapons, bombers and gunships included; helpless on the ground and inside 20 m, so it needs cover.\n" +
                "Tip: keep it well behind your line with short-range AA close by for anything that slips under it.",
                "[[Xe tên lửa phòng không tầm xa]] · giáp mỏng · tầm 95 m\n" +
                "Cách đánh: dừng lại rồi phóng một tên lửa lớn mỗi 8 giây, [[chỉ bắn máy bay]], xa tới 95 m (600 sát thương, không bắn gần hơn 20 m).\n" +
                "Mạnh / yếu: bắn xa hơn vũ khí của mọi máy bay, cả oanh tạc cơ và pháo hạm bay; bất lực trước mặt đất và trong vòng 20 m nên cần được che chắn.\n" +
                "Mẹo: để xa sau tuyến quân, có phòng không tầm ngắn ở gần cho thứ gì lọt xuống thấp."),
            ["guide.atgm_tower"] = (
                "[[ATGM tower]] · fixed defence · anti-tank (50 m)\n" +
                "How it fights: a twin Kornet launcher fires [[anti-tank missiles]] in pairs out to 50 m.\n" +
                "Strong / weak: stops tanks and heavy armour at range; APS and laser AA take its missiles, and artillery outranges it.\n" +
                "Tip: shell it from beyond 50 m, or bring a Trophy APS tank or a laser AA with the push.",
                "[[Tháp tên lửa chống tăng]] · công sự cố định · chống tăng (50 m)\n" +
                "Cách đánh: bệ phóng Kornet đôi bắn [[tên lửa chống tăng]] theo cặp xa tới 50 m.\n" +
                "Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và xe la-de phòng không bắn hạ được tên lửa của nó, pháo binh bắn xa hơn nó.\n" +
                "Mẹo: nã pháo từ ngoài 50 m, hoặc cho tăng có APS hay xe la-de phòng không đi cùng đợt tấn công."),
            ["guide.uav_scan"] = (
                "[[UAV scan]] · recon · {{cp}} CP\n" +
                "How it fights: a drone circles the mark for {{duration}} s and shows [[everything within {{radius}} m]] to your side: stealth aircraft, hidden guns and mines too.\n" +
                "Strong / weak: cheap eyes for artillery and for a push into the unknown; it deals no damage.\n" +
                "Tip: call it on an objective before the army goes in, or where something unseen is shooting at you.",
                "[[UAV quét]] · trinh sát · {{cp}} CP\n" +
                "Cách đánh: một drone lượn vòng trên điểm đánh dấu trong {{duration}} giây và cho phe ta thấy [[mọi thứ trong {{radius}} m]]: cả máy bay tàng hình, pháo ẩn và mìn.\n" +
                "Mạnh / yếu: đôi mắt rẻ cho pháo binh và cho một đợt tiến vào nơi chưa rõ; không gây sát thương.\n" +
                "Mẹo: gọi lên cứ điểm trước khi quân tiến vào, hoặc nơi có thứ gì vô hình đang bắn quân ta."),
            ["guide.remote_mines"] = (
                "[[Remote mines]] · area denial · {{cp}} CP\n" +
                "How it fights: rockets scatter [[{{count}} anti-tank mines]] within {{radius}} m of the mark; each blows up under the first enemy vehicle over it, and they clear themselves after {{duration}} s.\n" +
                "Strong / weak: stops a push on a road or a point; scouts, engineers and a UAV scan see them, and aircraft fly over.\n" +
                "Tip: lay them across the way the enemy is coming, not on top of them.",
                "[[Mìn rải từ xa]] · chặn khu vực · {{cp}} CP\n" +
                "Cách đánh: rốc-két rải [[{{count}} quả mìn chống tăng]] trong vòng {{radius}} m quanh điểm đánh dấu; mỗi quả nổ dưới xe địch đầu tiên đi qua, và tự hủy sau {{duration}} giây.\n" +
                "Mạnh / yếu: chặn một đợt tiến theo đường hoặc vào cứ điểm; trinh sát, công binh và UAV quét nhìn thấy chúng, máy bay bay qua đầu.\n" +
                "Mẹo: rải ngang đường địch đang tới, không phải ngay trên đầu chúng."),
            ["guide.field_tower"] = (
                "[[Field tower]] · fixed defence by air · {{cp}} CP\n" +
                "How it fights: a [[guard tower]] is dropped by parachute on the mark and fights for {{duration}} s; from card rank {{unitRank}} it is an [[ATGM tower]]. Never into the enemy's camp.\n" +
                "Strong / weak: holds a point you just took or plugs a gap in the line; artillery and heavy guns knock it down.\n" +
                "Tip: drop it on a point the enemy is about to counter-attack.",
                "[[Tháp dã chiến]] · công sự thả dù · {{cp}} CP\n" +
                "Cách đánh: một [[tháp canh]] được thả dù xuống điểm đánh dấu và chiến đấu trong {{duration}} giây; từ cấp {{unitRank}} của thẻ là [[tháp tên lửa chống tăng]]. Không bao giờ thả vào căn cứ địch.\n" +
                "Mạnh / yếu: giữ cứ điểm vừa chiếm hoặc bịt lỗ hổng trên tuyến; pháo binh và pháo nặng hạ được nó.\n" +
                "Mẹo: thả xuống cứ điểm mà địch sắp phản công."),
            ["guide.sead_strike"] = (
                "[[SEAD strike]] · anti-radiation missile · {{cp}} CP\n" +
                "How it fights: a jet fires an anti-radiation missile at the [[enemy air defence]] nearest the mark (within {{radius}} m): {{damage}} damage, and it is [[knocked out]] for {{duration}} s.\n" +
                "Strong / weak: opens the sky for your aircraft; wasted where there is no anti-air.\n" +
                "Tip: call it just before your helicopters or bombers go in.",
                "[[Đòn SEAD]] · tên lửa chống bức xạ · {{cp}} CP\n" +
                "Cách đánh: máy bay phóng tên lửa chống bức xạ vào [[phòng không địch]] gần điểm đánh dấu nhất (trong {{radius}} m): {{damage}} sát thương, và nó [[tê liệt]] {{duration}} giây.\n" +
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
                "[[C-RAM interceptor]] · medium tower · shoots rounds down\n" +
                "How it fights: shoots down rockets, missiles, drones and about a third of the shells aimed within 35 m, two interceptors at a time; its 20 mm gatling fires at nothing else, not even aircraft.\n" +
                "Strong / weak: shields the base from artillery, rockets and drones; it has nothing for vehicles on the ground.\n" +
                "Tip: put it where the enemy's artillery would hurt most, among your towers. At rank 7 [[Iron Dome]] trades the gatling for interceptor missiles (60 m, six at a time, not direct fire); Centurion keeps the quick close-in guard.",
                "[[Trạm đánh chặn C-RAM]] · tháp vừa · bắn hạ đạn bay tới\n" +
                "Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 mm chỉ bắn đạn bay tới, không bắn máy bay.\n" +
                "Mạnh / yếu: che căn cứ khỏi pháo binh, rốc-két và drone; không có gì đánh xe mặt đất.\n" +
                "Mẹo: đặt nơi pháo địch sẽ gây hại nhất, giữa các tháp của ta. Ở hạng 7, [[Vòm Sắt]] đổi súng nhiều nòng lấy tên lửa đánh chặn (60 m, sáu quả một lượt, không chặn đạn bắn thẳng); Centurion giữ vai trò che chắn tầm gần bắn nhanh."),
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
                "How it fights: vehicles within 35 m of your HQ mend 1.5% of their health a second, even in the middle of a fight.\n" +
                "Strong / weak: keeps a defending army on its feet; it does nothing for vehicles out in the field.\n" +
                "Tip: pair it with a base that fights at home (Defend, Siege, a pressed Conquest).",
                "[[Xưởng sửa chữa]] · mô-đun tiện ích\n" +
                "Cách đánh: xe trong vòng 35 m quanh sở chỉ huy hồi 1,5% máu mỗi giây, kể cả giữa trận.\n" +
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
                "How it fights: aircraft over it repair 3% a second and rearm; they come back to it when out of ammunition (no trip home for being hurt).\n" +
                "Strong / weak: keeps helicopters and jets flying longer; they still have to fly out to fight and can be shot down on the way.\n" +
                "Tip: take it with two or more aircraft in the deck.",
                "[[Sân bay dã chiến]] · mô-đun tiện ích\n" +
                "Cách đánh: máy bay bay trên nó hồi 3% máu mỗi giây và nạp đạn; chúng về đây khi hết đạn (không còn bay về vì bị thương).\n" +
                "Mạnh / yếu: giúp trực thăng và máy bay bay được lâu hơn; chúng vẫn phải ra trận và có thể bị bắn rơi trên đường.\n" +
                "Mẹo: mang theo khi bộ bài có từ hai máy bay trở lên."),
            ["guide.logistics_station"] = (
                "[[Logistics station]] · utility module\n" +
                "How it fights: your army's supply grows by 8 CP: income drops only once the army is past its supply.\n" +
                "Strong / weak: lets a big army keep its full income; nothing for a small one.\n" +
                "Tip: take it when your deck is full of expensive vehicles.",
                "[[Trạm hậu cần]] · mô-đun tiện ích\n" +
                "Cách đánh: mức tiếp tế của quân ta tăng thêm 8 CP: thu nhập chỉ giảm khi quân vượt mức tiếp tế.\n" +
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
                "How it fights: lands {{delay}} s after its warning circle shows, its blast {{blast}} m.\n" +
                "Strong / weak: wrecks light vehicles and groups; aircraft are safe.\n" +
                "Tip: move out of the circle, or destroy the gun.",
                "[[Đạn siêu pháo]] · của pháo đài · một quả đạn cực lớn\n" +
                "Cách đánh: rơi xuống {{delay}} giây sau khi vòng cảnh báo hiện, vụ nổ {{blast}} m.\n" +
                "Mạnh / yếu: phá nát xe nhẹ và đám đông; máy bay an toàn.\n" +
                "Mẹo: chạy khỏi vòng tròn, hoặc phá khẩu pháo."),
            ["guide.spawn_bastion"] = (
                "[[Camp bastion]] · fixed defence · guards a base\n" +
                "How it fights: never moves; a twin heavy gun fires two-shot [[volleys]] out to 40 m.\n" +
                "Strong / weak: very tough, with heavy armour rather than a building's, so [[armour-piercing]] guns work best; beats light vehicles and tanks.\n" +
                "Tip: don't attack it head on; artillery and heavy guns from beyond 40 m, or aircraft, wear it down.",
                "[[Tháp căn cứ]] · công sự cố định · bảo vệ căn cứ\n" +
                "Cách đánh: đứng yên; pháo nặng hai nòng bắn [[loạt đôi]] tới 40 m.\n" +
                "Mạnh / yếu: cực lì, giáp dày như xe tăng chứ không phải giáp công trình nên đạn [[xuyên giáp]] hiệu quả nhất; thắng xe nhẹ và xe tăng.\n" +
                "Mẹo: đừng đánh trực diện; dùng pháo binh, pháo nặng từ ngoài 40 m, hoặc máy bay để bào dần."),
            ["guide.heavy_turret"] = (
                "[[Heavy gun turret]] · fixed defence · twin 155 mm (50 m)\n" +
                "How it fights: a slow-turning twin 155 mm turret that fires two-shot [[high-explosive]] volleys out to 50 m.\n" +
                "Strong / weak: wrecks light vehicles, groups and tanks in its arc; as a [[structure]] it takes 1.5× from high explosive, little from bullets.\n" +
                "Tip: siege guns, howitzers and rocket artillery outrange it; its turret turns slowly, so come at it from two sides.",
                "[[Tháp pháo hạng nặng]] · công sự cố định · pháo đôi 155 mm (50 m)\n" +
                "Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn [[loạt đôi]] đạn nổ mạnh tới 50 m.\n" +
                "Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong góc bắn; là [[công trình]] nên ăn 1,5× sát thương nổ mạnh, sợ ít đạn súng máy.\n" +
                "Mẹo: pháo cối công thành, lựu pháo và pháo phản lực bắn xa hơn nó; tháp xoay chậm nên hãy đánh từ hai hướng."),
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
                "[[Long-range SAM site]] · fixed defence · long-range air defence (62 m)\n" +
                "How it fights: its search radar sees 85 m, and it launches [[missiles]] in pairs at [[aircraft]] up to 62 m away; nothing for the ground.\n" +
                "Strong / weak: outranges almost every aircraft; any ground force can drive up and destroy it.\n" +
                "Tip: send tanks or artillery at it first; keep aircraft away until it is gone.",
                "[[Trạm tên lửa phòng không tầm xa]] · công sự cố định · phòng không tầm xa (62 m)\n" +
                "Cách đánh: radar nhìn xa 85 m, phóng [[tên lửa]] từng cặp vào [[máy bay]] cách tới 62 m; không có gì để đánh mặt đất.\n" +
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
                "How it fights: a heavy MG (30 m, also at aircraft); its 60 m sight [[spots]] your army for the enemy's guns.\n" +
                "Strong / weak: stops scouts and [[light vehicles]]; the weakest tower, it falls fast to tanks and high explosive.\n" +
                "Tip: knock it out early with a tank or artillery so it stops spotting for the defence.",
                "[[Tháp canh]] · công sự cố định · nhẹ nhưng nhìn xa\n" +
                "Cách đánh: súng máy nặng (30 m, bắn cả máy bay); tầm nhìn 60 m giúp [[soi]] quân ta cho pháo địch.\n" +
                "Mạnh / yếu: chặn trinh sát và [[xe nhẹ]]; là tháp yếu nhất, gục nhanh trước xe tăng và đạn nổ mạnh.\n" +
                "Mẹo: hạ nó sớm bằng xe tăng hoặc pháo binh để địch mất tai mắt."),
            ["guide.gun_turret"] = (
                "[[Gun turret]] · fixed defence · tank gun (32 m)\n" +
                "How it fights: a battle tank's 120 mm [[armour-piercing]] gun on a fixed mount.\n" +
                "Strong / weak: beats tanks and light vehicles that drive into its 32 m reach; outranged by tank destroyers and artillery.\n" +
                "Tip: stay outside 32 m and let a [[tank destroyer]] (40 m) or artillery break it.",
                "[[Tháp pháo]] · công sự cố định · pháo xe tăng (32 m)\n" +
                "Cách đánh: pháo 120 mm [[xuyên giáp]] của tăng chủ lực đặt trên bệ cố định.\n" +
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
                "How it fights: lobs six-rocket [[salvos]] on an arc at ground targets 8–55 m away, over walls and cover (from the yard onto attackers at the wall).\n" +
                "Strong / weak: punishes groups of light vehicles and artillery; tanks take its rockets well, and HE shells wreck it.\n" +
                "Tip: spread out as you come in and rush it with tanks: inside 8 m it cannot fire at all.",
                "[[Dàn rốc-két]] · công sự cố định · phóng loạt (55 m)\n" +
                "Cách đánh: phóng [[loạt]] sáu rốc-két theo đường cầu vồng vào mục tiêu mặt đất cách 8–55 m, vượt qua tường và vật che (từ sân trong vào quân địch đã áp sát tường).\n" +
                "Mạnh / yếu: trừng phạt cụm xe nhẹ và pháo binh; xe tăng chịu rốc-két khá tốt, đạn nổ mạnh phá nó nhanh.\n" +
                "Mẹo: dàn quân khi tiến vào và dùng xe tăng lao tới: trong vòng 8 m nó không bắn được gì."),
            ["guide.mg_bunker"] = (
                "[[MG bunker]] · fixed defence · heavy machine gun\n" +
                "How it fights: a fast heavy machine gun (32 m, also at aircraft).\n" +
                "Strong / weak: mows down scouts and [[light vehicles]]; it barely scratches tanks.\n" +
                "Tip: send tanks, not light vehicles; a flame tank or artillery cracks it fast.",
                "[[Lô cốt súng máy]] · công sự cố định · súng máy nặng\n" +
                "Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay).\n" +
                "Mạnh / yếu: quét sạch trinh sát và [[xe nhẹ]]; gần như không làm xước xe tăng.\n" +
                "Mẹo: đưa xe tăng vào, đừng dùng xe nhẹ; tăng phun lửa hoặc pháo binh phá nó rất nhanh."),
            ["guide.artillery_emplacement"] = (
                "[[Artillery emplacement]] · fixed defence · long range (90 m)\n" +
                "How it fights: a howitzer that shells ground targets 25–90 m away whenever the defence can see them; nothing for close defence.\n" +
                "Strong / weak: hurts anything that stops inside its range; it cannot hit closer than 25 m, and it is fairly fragile.\n" +
                "Tip: rush it with fast vehicles: inside 25 m its gun cannot fire at you. Kill its [[spotters]] first.",
                "[[Trận địa pháo]] · công sự cố định · tầm xa (90 m)\n" +
                "Cách đánh: lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe thủ nhìn thấy; không có gì tự vệ ở gần.\n" +
                "Mạnh / yếu: gây đau cho mọi thứ dừng lại trong tầm; không bắn được gần hơn 25 m, và khá mỏng manh.\n" +
                "Mẹo: dùng xe nhanh lao vào: trong vòng 25 m pháo của nó chịu thua. Diệt [[tai mắt]] của nó trước."),

            // Mission units and bosses.
            ["guide.hover_gunboat"] = (
                "[[Escort hovercraft]] · boss escort · fast\n" +
                "How it fights: a six-barrel 30 mm gun on a small air-cushion hull; it runs beside the landing hovercraft over land and water.\n" +
                "Strong / weak: fast and hard to pin down, but thinly armoured: any tank or autocannon stops it.\n" +
                "Tip: kill the one marking targets first (the escort mark over it): the hovercraft's guns fall tighter while it lives.",
                "[[Xuồng đệm khí hộ tống]] · hộ tống boss · nhanh\n" +
                "Cách đánh: pháo 30 mm sáu nòng trên thân đệm khí nhỏ; nó chạy cạnh tàu đệm khí đổ bộ trên cả đất liền lẫn mặt nước.\n" +
                "Mạnh / yếu: nhanh, khó bắt, nhưng giáp mỏng: xe tăng hay pháo tự động nào cũng hạ được.\n" +
                "Mẹo: hạ chiếc đang đánh dấu mục tiêu trước (dấu hộ tống trên nó): khi nó còn, pháo của tàu đệm khí bắn chụm hơn."),
            ["guide.supply_truck"] = (
                "[[Supply truck]] · mission unit · slow convoy\n" +
                "How it fights: only a light machine gun; it drives its route to the depot and cannot take objectives.\n" +
                "Strong / weak: armoured enough to take some hits, but it cannot fight back against anything real.\n" +
                "Tip: in [[convoy]] missions, clear the road ahead with tanks and keep AA with the trucks.",
                "[[Xe tải tiếp tế]] · đơn vị nhiệm vụ · đoàn xe chậm\n" +
                "Cách đánh: chỉ có súng máy nhẹ; nó chạy theo lộ trình tới kho và không chiếm được cứ điểm.\n" +
                "Mạnh / yếu: đủ giáp để chịu vài phát, nhưng không đánh lại được thứ gì đáng kể.\n" +
                "Mẹo: trong nhiệm vụ [[hộ tống]], dùng xe tăng dọn đường phía trước và cho phòng không đi cùng xe tải."),
            ["guide.behemoth"] = (
                "[[Boss]] · land battleship · heavy armour\n" +
                "How it fights: twin main guns (40 m), a 120 mm, flak, [[missiles]] that hit ground and air (45 m) and a twin Kornet launcher behind the main turret; calls two elite tanks at 70%.\n" +
                "Strong / weak: crushes light vehicles and tanks; [[tank hunters]] are its bane, and its armour shrugs off bullets.\n" +
                "Tip: fight it from beyond 45 m; at half health it [[rages]] (faster fire), and below 35% it raises a shield now and then.",
                "[[Boss]] · chiến hạm mặt đất · giáp dày\n" +
                "Cách đánh: pháo chính hai nòng (40 m), pháo 120 mm, pháo cao xạ, [[tên lửa]] bắn cả đất lẫn trời (45 m) và bệ Kornet đôi sau tháp chính; còn 70% máu gọi 2 tăng tinh nhuệ.\n" +
                "Mạnh / yếu: nghiền nát xe nhẹ và xe tăng; khắc tinh là [[xe diệt tăng]], giáp dày khiến đạn súng máy vô dụng.\n" +
                "Mẹo: đánh từ ngoài 45 m; còn nửa máu nó [[nổi điên]] (bắn nhanh hơn), dưới 35% thỉnh thoảng bật khiên."),
            ["guide.behemoth_inferno"] = (
                "[[Boss]] · flame Behemoth · burns everything close\n" +
                "How it fights: twin [[flame projectors]] (20 m) set the ground on fire; a thermobaric rocket box hits 10–46 m; it calls two elite tanks at 70%.\n" +
                "Strong / weak: melts light vehicles and tanks that get close; weak to [[aircraft]], since it has only one flak gun.\n" +
                "Tip: keep your distance: tank destroyers and artillery from beyond 46 m, attack helicopters and jets from above.",
                "[[Boss]] · Behemoth phun lửa · thiêu mọi thứ ở gần\n" +
                "Cách đánh: hai [[súng phun lửa]] lớn (20 m) đốt cháy mặt đất; hộp rốc-két nhiệt áp đánh tầm 10–46 m; còn 70% máu gọi 2 tăng tinh nhuệ.\n" +
                "Mạnh / yếu: thiêu chảy xe nhẹ và xe tăng tới gần; yếu trước [[máy bay]] vì chỉ có một khẩu pháo cao xạ.\n" +
                "Mẹo: giữ khoảng cách: xe diệt tăng và pháo binh bắn từ ngoài 46 m, trực thăng tấn công và cường kích đánh từ trên cao."),
            ["guide.behemoth_tempest"] = (
                "[[Boss]] · railgun Behemoth · long range (80 m)\n" +
                "How it fights: a [[railgun]] charges for a second (the coils glow), then [[pierces]] a whole line to 80 m; two coilguns hit ground and air (55 m).\n" +
                "Strong / weak: punishes vehicles lined up in a column; close in, its EMP (22 m) stuns ground vehicles, and it shields itself when hurt.\n" +
                "Tip: spread out and close in from several sides; when the coils glow, get out of the line it is aiming along.",
                "[[Boss]] · Behemoth pháo điện từ · tầm xa (80 m)\n" +
                "Cách đánh: [[pháo điện từ]] nạp năng lượng một giây (cuộn dây sáng lên) rồi [[xuyên thủng]] cả hàng tới 80 m; hai pháo điện từ bắn đất lẫn trời (55 m).\n" +
                "Mạnh / yếu: trừng phạt xe đi thành hàng dọc; ở gần, EMP (22 m) làm choáng xe mặt đất, và nó bật khiên khi bị thương.\n" +
                "Mẹo: dàn quân và áp sát từ nhiều hướng; khi cuộn dây sáng lên, hãy tránh khỏi đường ngắm của nó."),
            ["guide.mobile_fortress"] = (
                "[[Boss]] · mobile fortress · very slow\n" +
                "How it fights: two 203 mm howitzers (60 m), rocket boxes, flak, a twin 30 mm anti-drone turret and missiles; an [[EMP]] stuns ground vehicles in 22 m; two heavy tanks and an engineer that mends it escort it, another engineer at half health.\n" +
                "Strong / weak: shreds light vehicles and tanks that crowd it; [[tank hunters]] and heavy artillery wear it down.\n" +
                "Tip: fight from beyond 22 m so the EMP misses, and expect a doubled rate of fire below 40% health.",
                "[[Boss]] · pháo đài di động · cực chậm\n" +
                "Cách đánh: hai lựu pháo 203 mm (60 m), hộp rốc-két, pháo cao xạ, tháp 30 mm đôi chống drone và tên lửa; [[EMP]] làm choáng xe mặt đất trong 22 m; hộ tống là 2 tăng nặng và 1 xe công binh sửa cho nó, còn nửa máu thêm 1 xe công binh.\n" +
                "Mạnh / yếu: xé nát xe nhẹ và xe tăng dồn quanh nó; [[xe diệt tăng]] và pháo hạng nặng bào dần được nó.\n" +
                "Mẹo: đánh từ ngoài 22 m để né EMP, và coi chừng dưới 40% máu nó bắn nhanh gấp đôi."),
            ["guide.fortress_hive"] = (
                "[[Boss]] · drone fortress · deadly to aircraft\n" +
                "How it fights: no big gun: [[drone swarms]] from two racks (70 m), a SAM battery (62 m) and flak for the sky, and strike UAVs sent out.\n" +
                "Strong / weak: shreds [[aircraft]]; its drones hurt tanks, but tanks and artillery are what break it.\n" +
                "Tip: leave your aircraft at home; bring APS tanks or laser AA against the drones, then grind it down with tanks and artillery.",
                "[[Boss]] · pháo đài drone · tử thần của máy bay\n" +
                "Cách đánh: không có pháo lớn: hai giàn phóng [[bầy drone]] tới 70 m, dàn tên lửa (62 m) và pháo cao xạ giữ bầu trời, còn thả thêm UAV tấn công.\n" +
                "Mạnh / yếu: xé nát [[máy bay]]; drone của nó hại được xe tăng, nhưng xe tăng và pháo binh mới là thứ hạ được nó.\n" +
                "Mẹo: để máy bay ở nhà; mang tăng APS hoặc xe la-de phòng không chặn drone, rồi dùng xe tăng và pháo binh bào dần."),
            ["guide.fortress_bastion"] = (
                "[[Boss]] · the toughest fortress · heavy mortar (80 m)\n" +
                "How it fights: a heavy [[mortar]] hits 12–80 m out, four 40 mm autocannon turrets (28 m) cover every side, two NSV machine guns its flanks; it [[patches]] itself up once at half.\n" +
                "Strong / weak: its autocannons shred light vehicles that come close; its armour stops bullets, and its mortar cannot hit inside 12 m.\n" +
                "Tip: bring tank hunters and heavy guns, and keep your burst damage for after its one repair.",
                "[[Boss]] · pháo đài lì đòn nhất · cối hạng nặng (80 m)\n" +
                "Cách đánh: khẩu [[cối]] hạng nặng bắn tầm 12–80 m, bốn tháp pháo tự động 40 mm (28 m) phủ mọi hướng, hai súng máy NSV giữ hai bên hông, còn nửa máu nó [[tự vá giáp]] một lần.\n" +
                "Mạnh / yếu: pháo tự động xé nát xe nhẹ tới gần; giáp dày chặn đạn súng máy, cối không bắn được trong vòng 12 m.\n" +
                "Mẹo: mang xe diệt tăng và pháo hạng nặng, để dành hỏa lực dồn cho sau lần tự vá duy nhất của nó."),
            ["guide.armored_train"] = (
                "[[Boss]] · armoured train · follows the rails\n" +
                "How it fights: two heavy guns (42 m), a rocket box, two flak guns and an MG; it hides in [[smoke]] when shot and [[patches]] up 20% once, at half health.\n" +
                "Strong / weak: its guns kill tanks and light vehicles near the track; it cannot leave the rails.\n" +
                "Tip: set up tank hunters and artillery along the line ahead of it, more than 45 m from the track.",
                "[[Boss]] · đoàn tàu bọc thép · chạy theo đường ray\n" +
                "Cách đánh: hai pháo nặng (42 m), hộp rốc-két, hai pháo cao xạ và súng máy; bị bắn thì núp trong [[khói]], còn nửa máu thì [[tự vá]] 20% một lần.\n" +
                "Mạnh / yếu: pháo của nó diệt xe tăng và xe nhẹ gần đường ray; nó không thể rời đường ray.\n" +
                "Mẹo: bố trí xe diệt tăng và pháo binh dọc tuyến đường phía trước nó, cách đường ray hơn 45 m."),
            ["guide.nuke_train"] = (
                "[[Boss]] · missile train · a race against the countdown\n" +
                "How it fights: twin heavy guns (40 m), a 152 mm gun car and three flak guns; it hides in [[smoke]] when shot; a rocket car and a long-range SAM car ride behind it, and armoured escorts run beside the rails.\n" +
                "Strong / weak: its guns wreck anything near the track; it cannot leave the rails and carries no missiles to fight with.\n" +
                "Tip: hit it hard and early with artillery and tank hunters; it must be stopped before it reaches the launch site.",
                "[[Boss]] · đoàn tàu tên lửa · chạy đua với đồng hồ\n" +
                "Cách đánh: pháo nặng hai nòng (40 m), toa pháo 152 mm và ba pháo cao xạ; bị bắn thì núp trong [[khói]]; phía sau có toa rốc-két và toa SAM tầm xa, xe bọc thép hộ tống chạy dọc đường ray.\n" +
                "Mạnh / yếu: pháo của nó phá nát mọi thứ gần đường ray; nó không rời được đường ray và không có tên lửa để đánh.\n" +
                "Mẹo: dùng pháo binh và xe diệt tăng đánh mạnh và sớm; phải chặn nó trước khi tới bãi phóng."),
            ["guide.mega_gunship"] = (
                "[[Boss]] · giant helicopter · flying\n" +
                "How it fights: two rocket pods, two 30 mm guns, a minigun and a 12.7 mm door gun each side; [[flares]] often, two attack helicopters and a scout that marks targets escort it, and it rages at 50%.\n" +
                "Strong / weak: tank guns and artillery cannot touch it: only [[anti-air]] and fighters hurt it.\n" +
                "Tip: mass flak (AA vehicles, Tunguskas), since guns ignore its flares, and add fighters for the escort helicopters.",
                "[[Boss]] · trực thăng khổng lồ · bay\n" +
                "Cách đánh: hai giàn rốc-két, hai pháo 30 mm, một súng máy nhiều nòng và mỗi bên cửa một súng máy 12,7 mm; thả [[mồi nhiệt]] liên tục, hộ tống là 2 trực thăng tấn công và 1 trực thăng trinh sát vũ trang đánh dấu mục tiêu, 50% thì nổi điên.\n" +
                "Mạnh / yếu: pháo xe tăng và pháo binh không chạm được nó: chỉ [[phòng không]] và tiêm kích gây sát thương.\n" +
                "Mẹo: dồn pháo cao xạ (xe phòng không, Tunguska) vì đạn pháo không bị mồi nhiệt lừa, thêm tiêm kích để diệt trực thăng hộ tống."),
            ["guide.drone_mothership"] = (
                "[[Boss]] · flying drone carrier · the most health of any boss\n" +
                "How it fights: cannons and swarms of kamikaze [[drones]] from three bays (70 m) at the ground, flak for aircraft; every 30 s it launches three [[strike UAVs]].\n" +
                "Strong / weak: floods the ground with drones; only anti-air and fighters can damage it, and it shields itself at half health.\n" +
                "Tip: mass flak and SAMs under it, APS tanks or laser AA against its drones, and fighters to clear the strike UAVs.",
                "[[Boss]] · tàu mẹ drone biết bay · nhiều máu nhất trong các boss\n" +
                "Cách đánh: pháo và bầy [[drone cảm tử]] từ ba khoang phóng (70 m) đánh mặt đất, pháo cao xạ chống máy bay; cứ 30 giây phóng ra 3 [[UAV tấn công]].\n" +
                "Mạnh / yếu: nhấn chìm mặt đất bằng drone; chỉ phòng không và tiêm kích gây sát thương được, còn nửa máu thì bật khiên.\n" +
                "Mẹo: dồn pháo cao xạ và tên lửa phòng không bên dưới, tăng APS hoặc la-de chặn drone, tiêm kích dọn UAV tấn công."),
            ["guide.silver_bug"] = (
                "[[Boss]] · orbital spacecraft · tungsten rods from orbit\n" +
                "How it fights: a main laser turret and two coilguns hit the ground from high or low altitude; drop pods land vehicles; every 45 s seven [[tungsten rods]] fall from its satellite (nine once it has crashed).\n" +
                "Altitude: it opens in low orbit, out of reach, then keeps to a fixed schedule of high-altitude phases (only long-range SAMs, long-range SAM sites and fighters reach it) and low-altitude phases (anything that hits aircraft, plus railguns); below 30% health it crashes and fights on as a ground fortress, four ordinary gun turrets on the wreck.\n" +
                "Strong / weak: its belly (armour 2) is exposed at low altitude; its two point-defence lasers pick off some of your SAMs and missiles.\n" +
                "Tip: keep long-range anti-air ready for its high passes, mass everything else for the low ones, shoot down its drop pods before they land, and break its satellite uplink to cancel a rod rain.",
                "[[Boss]] · phi thuyền quỹ đạo · thanh vonfram từ quỹ đạo\n" +
                "Cách đánh: tháp la-de chính và hai pháo coilgun bắn xuống mặt đất ở cả tầng cao lẫn tầng thấp; khoang đổ bộ thả xe xuống; cứ 60 giây có 7 [[thanh vonfram]] rơi từ vệ tinh của nó (khi đã rơi xuống đất: 9 thanh mỗi 50 giây).\n" +
                "Tầng độ cao: mở màn ở quỹ đạo thấp, ngoài tầm bắn; sau đó lặp cố định tầng cao (chỉ PK tầm xa, trạm PK tầm xa và tiêm kích bắn tới) và tầng thấp (mọi vũ khí bắn được máy bay, cộng pháo điện từ); dưới 30% máu nó rơi xuống thành pháo đài mặt đất, bốn tháp pháo thường trên xác.\n" +
                "Mạnh / yếu: bụng nó (giáp cấp 2) lộ ra ở tầng thấp; hai tháp la-de phòng thủ điểm của nó bắn hạ bớt SAM và tên lửa của ta.\n" +
                "Mẹo: giữ phòng không tầm xa sẵn sàng cho các đợt tầng cao, dồn mọi vũ khí khác vào các đợt tầng thấp, bắn hạ khoang đổ bộ trước khi chúng chạm đất, và phá ăng-ten liên kết vệ tinh để hủy một đợt mưa thanh vonfram."),
            ["guide.sky_fortress"] = (
                "[[Boss]] · airborne gunship · circles high\n" +
                "How it fights: [[orbits]] its prey, a 105 mm, two 40 mm and a 25 mm firing from its left side (50–58 m), plus Griffins; nothing for aircraft.\n" +
                "Strong / weak: destroys ground forces caught under its orbit; only [[anti-air]] and fighters can reach it.\n" +
                "Tip: build flak and SAMs early and add fighters, which its guns cannot hit; two escort fighters and a UAV that marks your units fly with it (kill the UAV: its guns fall wider), two more fighters at half health.",
                "[[Boss]] · pháo hạm bay · bay vòng trên cao\n" +
                "Cách đánh: [[bay vòng]] quanh mục tiêu, pháo 105 mm, hai 40 mm và một 25 mm bắn từ bên trái (50–58 m), kèm Griffin; không bắn được máy bay.\n" +
                "Mạnh / yếu: hủy diệt quân mặt đất nằm dưới vòng bay; chỉ [[phòng không]] và tiêm kích với tới nó.\n" +
                "Mẹo: xây cao xạ và tên lửa phòng không sớm, thêm tiêm kích vì pháo của nó không bắn được máy bay; bay kèm là 2 tiêm kích và 1 UAV đánh dấu quân ta (hạ UAV thì pháo của nó bắn lệch hơn), còn nửa máu thêm 2 tiêm kích."),

            ["guide.rail_supergun"] = (
                "[[Mini boss]] · rail electromagnetic gun · stays put at the edge of the field\n" +
                "How it fights: every 25 s one electromagnetic [[slug]] at your biggest group of ground vehicles, anywhere on the map: it goes through up to five vehicles in a line (1,000 each) and blasts where it hits the last (2,000 in a 12 m core, 40% out to 20 m); a red ring marks the aim [[3 s]] ahead. Walls, cannon and flak towers and a [[fire-control post]] guard its bed; two 40 mm guns cover it.\n" +
                "Strong / weak: it punishes an army that bunches up; it cannot move, and once its fire-control post falls its shells land wide.\n" +
                "Tip: keep moving and spread out when the ring shows; break the fire-control post first, then push in with tanks behind the artillery.",
                "[[Mini boss]] · pháo điện từ đường ray · đứng yên ở mép chiến trường\n" +
                "Cách đánh: cứ 25 giây một phát [[điện từ]] vào cụm xe mặt đất đông nhất của bạn, ở bất cứ đâu trên bản đồ: nó xuyên qua tối đa năm xe trên một đường thẳng (1.000 mỗi xe) rồi nổ ở xe cuối (2.000 trong lõi 12 m, còn 40% tới rìa 20 m); vòng đỏ báo điểm ngắm trước [[3 giây]]. Tường, tháp pháo, tháp phòng không và [[trạm chỉ thị mục tiêu]] bảo vệ nền pháo; hai khẩu 40 mm che chắn.\n" +
                "Mạnh / yếu: trừng phạt đội quân dồn cục; không di chuyển được, và mất trạm chỉ thị thì đạn rơi lệch xa.\n" +
                "Mẹo: luôn di chuyển và tản ra khi thấy vòng đỏ; phá trạm chỉ thị trước, rồi cho xe tăng tiến vào sau pháo binh."),
            ["guide.earth_borer"] = (
                "[[Boss]] · boring machine · attacks from below\n" +
                "How it fights: it [[dives]], bores unseen and untouchable to under your biggest group of ground vehicles, the ground [[cracks]] for 2 s, then it breaks out in a quake that stuns everything on the ground within 15 m. Its drill and two cannons finish the job.\n" +
                "Strong / weak: deadly to a tight group of tanks; right after it breaks out it takes [[half as much again]] for 6 s, and aircraft are never under it.\n" +
                "Tip: move out of the cracks at once, then turn everything on it while it is exposed.",
                "[[Boss]] · máy khoan · tấn công từ dưới đất\n" +
                "Cách đánh: [[chui xuống đất]], khoan ngầm không bị nhắm tới dưới cụm xe mặt đất đông nhất của bạn, mặt đất [[nứt]] 2 giây rồi nó trồi lên gây rung chấn làm choáng mọi xe mặt đất trong 15 m. Mũi khoan và hai khẩu pháo kết liễu nốt.\n" +
                "Mạnh / yếu: cực nguy hiểm với cụm xe tăng dày; ngay sau khi trồi lên nó nhận [[thêm 50%]] sát thương trong 6 giây, và máy bay không bao giờ nằm dưới nó.\n" +
                "Mẹo: rời khỏi vết nứt ngay, rồi dồn hỏa lực vào nó lúc nó lộ thân."),
            ["guide.command_airship"] = (
                "[[Boss]] · flying battleship · four engines, two drone bays, a radar\n" +
                "How it fights: twin 57 mm [[flak]] turrets, two twin 30 mm under the belly, drones from two [[bays]] and a strike UAV from each now and then. Every part has its own health: the hull takes [[no damage]] until two engines are down.\n" +
                "Strong / weak: only [[anti-air]] and fighters reach it; break a bay and its drones stop, break the [[radar]] and its flak scatters wide.\n" +
                "Tip: shoot the engines first to open the hull, then the radar; bring flak and SAMs, and fighters for its strike UAVs.",
                "[[Boss]] · chiến hạm bay · bốn động cơ, hai nhà chứa drone, một radar\n" +
                "Cách đánh: hai tháp [[pháo phòng không]] 57 mm, hai tháp 30 mm đôi dưới bụng, drone từ hai [[nhà chứa]] và thỉnh thoảng mỗi nhà chứa thả một UAV tấn công. Mỗi bộ phận có máu riêng: thân [[không nhận sát thương]] cho tới khi hai động cơ bị phá.\n" +
                "Mạnh / yếu: chỉ [[phòng không]] và tiêm kích với tới; phá nhà chứa thì ngừng thả drone, phá [[radar]] thì pháo phòng không của nó bắn lệch.\n" +
                "Mẹo: bắn động cơ trước để mở thân, rồi tới radar; mang pháo cao xạ và tên lửa phòng không, thêm tiêm kích để diệt UAV."),
            ["guide.landing_hovercraft"] = (
                "[[Boss]] · air-cushion landing craft · lands troops\n" +
                "How it fights: it runs its route along the coast; every 35 s it stops, drops its [[ramp]] and lands 3 or 4 vehicles, five times at most. Four six-barrel CIWS guard it against ground and air (two of them shoot down missiles and rockets) and two 140 mm rocket launchers shell the shore.\n" +
                "Strong / weak: every landing it makes grows the enemy army; it is big and slow to turn, and anything that hits it on its way in cuts the landings short.\n" +
                "Tip: meet it before its first landing with tank hunters and artillery, and keep a reserve for the troops it has already put ashore.",
                "[[Boss]] · tàu đệm khí đổ bộ · thả quân lên bờ\n" +
                "Cách đánh: chạy theo lộ trình dọc bờ biển; cứ 35 giây dừng lại, hạ [[cửa đổ bộ]] và thả 3–4 xe lên bờ, tối đa năm lần. Bốn pháo CIWS sáu nòng che chắn cả đất lẫn trời (hai khẩu bắn hạ tên lửa và rốc-két) và hai dàn rốc-két 140 mm bắn phá bờ.\n" +
                "Mạnh / yếu: mỗi lần đổ bộ là địch thêm quân; nó to và xoay chậm, đánh trúng nó trên đường tới là cắt bớt số lần đổ bộ.\n" +
                "Mẹo: đón đầu nó trước lần đổ bộ đầu tiên bằng xe diệt tăng và pháo binh, và giữ lực lượng dự bị cho số quân đã lên bờ."),
            ["guide.leviathan"] = (
                "[[Boss]] · battleship at sea · shells the coast, runs when beaten\n" +
                "How it fights: three triple 406 mm turrets lay [[salvos]] on the shore, one gun a turret, marked ahead, sweeping along it, and fire all nine along a strip through your base as its super weapon; two triple 155 mm fire on their own, eight 25 mm mounts and a medium-range SAM at aircraft; cruise missiles at your groups and your base; [[CIWS]] shoots down missiles, rockets and drones (never shells, bullets or beams). Phase 2 it comes in close, lands tanks and launches helicopters; phase 3 it runs for open sea: sink it before the clock runs out.\n" +
                "Strong / weak: its sides are armour [[4]], its deck only [[2]]: artillery, bombs, rocket artillery and top attacks hit the deck; tank guns reach it only from the pier heads, when it comes in close.\n" +
                "Tip: hold the lighthouse and the coastal batteries; bring artillery and aircraft; break the CIWS (or its cruiser and corvette) before sending missiles, a main turret when the broadside is marked, and the engine room before it runs.",
                "[[Boss]] · chiến hạm trên biển · nã pháo vào bờ, bỏ chạy khi thua\n" +
                "Cách đánh: ba tháp pháo ba nòng 406 mm bắn [[loạt]] vào bờ, mỗi tháp một nòng, có cảnh báo trước và quét dần dọc bờ, và bắn cả chín nòng theo dải qua căn cứ khi tung siêu vũ khí; hai tháp ba nòng 155 mm tự bắn, tám bệ 25 mm và một bệ tên lửa phòng không tầm trung bắn máy bay; tên lửa hành trình đánh vào cụm quân và căn cứ; [[CIWS]] bắn hạ tên lửa, rốc-két và drone (không chặn đạn pháo, đạn súng hay Năng lượng). Pha 2 nó áp sát, đổ bộ xe tăng và thả trực thăng; pha 3 nó chạy ra khơi: đánh chìm nó trước khi hết giờ.\n" +
                "Mạnh / yếu: hông tàu giáp cấp [[4]], boong chỉ cấp [[2]]: pháo binh, bom, pháo phản lực và đòn đánh nóc đánh vào boong; pháo xe tăng chỉ với tới khi nó áp sát, đứng ở đầu cầu tàu.\n" +
                "Mẹo: giữ ngọn hải đăng và trận địa pháo bờ biển; mang pháo binh và máy bay; phá CIWS (hoặc tuần dương hạm và tàu hộ vệ) trước khi dùng tên lửa, phá một tháp pháo chính khi loạt bắn mạn được đánh dấu, và phá buồng máy trước khi nó bỏ chạy."),
            ["guide.sea_corvette"] = (
                "[[Leviathan's fleet]] · escort corvette · guards the flagship\n" +
                "How it fights: a 76 mm gun on the shore; a CIWS that shoots down missiles and drones aimed at it or at Leviathan within 32 m. It keeps station between Leviathan and the shore.\n" +
                "Strong / weak: sides armour 3, deck 1; sink it first and your aircraft and missiles reach the flagship.",
                "[[Hạm đội Leviathan]] · tàu hộ vệ · bảo vệ tàu chính\n" +
                "Cách đánh: pháo 76 mm bắn vào bờ; CIWS bắn hạ tên lửa và drone nhắm vào nó hoặc vào Leviathan trong vòng 32 m. Nó giữ vị trí chắn giữa Leviathan và bờ.\n" +
                "Mạnh / yếu: hông giáp cấp 3, boong cấp 1; đánh chìm nó trước thì máy bay và tên lửa của bạn đánh được tàu chính."),
            ["guide.sea_cruiser"] = (
                "[[Leviathan's fleet]] · missile cruiser · screens the flagship\n" +
                "How it fights: two twin 203 mm turrets on the shore; two CIWS that shoot down missiles and drones aimed at it or at Leviathan within 30 m. It keeps station between Leviathan and the shore, and closer in when it runs.\n" +
                "Strong / weak: sides armour 3, deck 2; it is the first ship in reach, and sunk it opens the flagship to your missiles.",
                "[[Hạm đội Leviathan]] · tuần dương hạm tên lửa · che chắn tàu chính\n" +
                "Cách đánh: hai tháp pháo nòng đôi 203 mm bắn vào bờ; hai CIWS bắn hạ tên lửa và drone nhắm vào nó hoặc vào Leviathan trong vòng 30 m. Nó giữ vị trí giữa Leviathan và bờ, áp sát hơn khi tàu chính bỏ chạy.\n" +
                "Mạnh / yếu: hông giáp cấp 3, boong cấp 2; nó là tàu đầu tiên trong tầm bắn, đánh chìm nó thì tên lửa của bạn đánh được tàu chính."),
            ["guide.missile_boat"] = (
                "[[Leviathan's fleet]] · fast attack boat · raids the pier heads\n" +
                "How it fights: it waits out on the sea, dashes in to a pier head, fires a salvo of 80 mm rockets and runs back out.\n" +
                "Strong / weak: fast but thin-skinned (armour 1): anything on the pier heads hits it while it is close in.",
                "[[Hạm đội Leviathan]] · xuồng tên lửa cao tốc · đánh vào đầu cầu tàu\n" +
                "Cách đánh: chờ ngoài khơi, lao vào sát đầu cầu tàu, bắn một loạt rốc-két 80 mm rồi quay ra.\n" +
                "Mạnh / yếu: nhanh nhưng giáp mỏng (cấp 1): mọi xe đứng ở đầu cầu tàu đều bắn trúng nó khi nó áp sát."),
            ["guide.landing_craft"] = (
                "[[Leviathan's fleet]] · landing craft · puts tanks on the beach\n" +
                "How it fights: from Leviathan's well deck to a beach, two tanks off, and back for more; three trips at most.\n" +
                "Strong / weak: slow and lightly armed; sink it on the way in and its tanks go down with it.",
                "[[Hạm đội Leviathan]] · tàu đổ bộ · đưa xe tăng lên bãi\n" +
                "Cách đánh: từ khoang đổ bộ của Leviathan tới bãi cát, thả hai xe tăng rồi quay về lấy thêm; tối đa ba chuyến.\n" +
                "Mạnh / yếu: chậm và ít vũ khí; đánh chìm nó trên đường vào thì xe tăng chìm theo."),
            ["guide.supreme_command"] = (
                "[[Boss]] · super-heavy headquarters · makes its army stronger\n" +
                "How it fights: only two light machine guns; every enemy unit within [[40 m]] of it hits [[20% harder]] and fires 20% faster. An elite guard rides with it, and more come at 60%.\n" +
                "Strong / weak: its army is far more dangerous near it; on its own it barely fights back and cannot outrun anything.\n" +
                "Tip: pull the fight away from it, or strike it from range with artillery and aircraft; kill it and its whole army weakens at once.",
                "[[Boss]] · sở chỉ huy siêu nặng · làm quân mình mạnh lên\n" +
                "Cách đánh: chỉ có hai súng máy nhẹ; mọi quân địch trong [[40 m]] quanh nó tăng [[20% sát thương]] và 20% tốc độ bắn. Có cận vệ tinh nhuệ đi kèm, còn 60% máu thì gọi thêm.\n" +
                "Mạnh / yếu: quân địch gần nó nguy hiểm hơn nhiều; bản thân nó gần như không đánh lại được và không chạy thoát được thứ gì.\n" +
                "Mẹo: kéo trận đánh ra xa nó, hoặc đánh nó từ xa bằng pháo binh và máy bay; hạ nó là cả đạo quân yếu đi ngay."),

            // Fire support cards.
            ["guide.artillery_barrage"] = (
                "[[Artillery barrage]] · fire support · {{cp}} CP\n" +
                "How it fights: {{delay}} s after you tap, {{count}} [[shells]] rain on a {{radius}} m circle over {{duration}} s, each a high-explosive blast.\n" +
                "Strong / weak: good against groups, [[towers]] and parked artillery; fast vehicles drive out of it, and it cannot hit aircraft.\n" +
                "Tip: aim at enemies that stand and fight or sit capturing a point; it never hurts your own vehicles.",
                "[[Pháo kích]] · hỏa lực yểm trợ · {{cp}} CP\n" +
                "Cách đánh: {{delay}} giây sau khi chạm, {{count}} quả [[đạn pháo]] rơi xuống vùng tròn {{radius}} m trong {{duration}} giây, mỗi quả là một vụ nổ mạnh.\n" +
                "Mạnh / yếu: tốt với cụm địch, [[tháp canh]] và pháo binh đứng yên; xe nhanh chạy thoát được, và không đánh được máy bay.\n" +
                "Mẹo: nhắm vào địch đang đứng giao chiến hoặc đang chiếm điểm; nó không bao giờ gây hại cho xe ta."),
            ["guide.airstrike"] = (
                "[[Airstrike]] · a line of bombs · {{cp}} CP\n" +
                "How it fights: {{delay}} s after you call it, a jet drops {{count}} [[bombs]] along a {{length}} m line, {{width}} m wide, in the direction you [[drag]]; from card [[rank {{rank}}]] the line is {{linePercent}}% longer ({{rankLength}} m, {{rankCount}} bombs).\n" +
                "Strong / weak: hits columns and towers along a road hard; a single vehicle off the line escapes, and aircraft are immune.\n" +
                "Tip: drag it along the enemy's line of advance so every bomb finds a target.",
                "[[Không kích]] · một hàng bom · {{cp}} CP\n" +
                "Cách đánh: {{delay}} giây sau khi gọi, máy bay thả {{count}} quả [[bom]] dọc một đường {{length}} m, rộng {{width}} m, theo hướng bạn [[kéo]]; từ [[cấp {{rank}}]] của thẻ, đường bom dài hơn {{linePercent}}% ({{rankLength}} m, {{rankCount}} quả).\n" +
                "Mạnh / yếu: đánh mạnh vào đoàn xe và tháp canh dọc đường; xe lẻ nằm ngoài hàng bom sẽ thoát, máy bay thì miễn nhiễm.\n" +
                "Mẹo: kéo dọc theo hướng tiến quân của địch để quả bom nào cũng trúng."),
            ["guide.cruise_missile"] = (
                "[[Cruise missile]] · one huge blast · {{cp}} CP\n" +
                "How it fights: after a {{delay}} s warning, one [[missile]] strikes the spot with a {{blast}} m blast.\n" +
                "Strong / weak: the best way to wipe out a crowd or a cluster of [[defences]]; moving targets may drive off before it lands.\n" +
                "Tip: fire it where enemies stand still: a captured objective, a siege line, parked artillery. Enemy jammers throw it off.",
                "[[Tên lửa hành trình]] · một vụ nổ cực lớn · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây cảnh báo, một quả [[tên lửa]] đánh xuống điểm chọn với vụ nổ bán kính {{blast}} m.\n" +
                "Mạnh / yếu: cách tốt nhất để xóa sổ một cụm quân hoặc cụm [[công sự]]; mục tiêu đang chạy có thể thoát trước khi nó rơi.\n" +
                "Mẹo: bắn vào nơi địch đứng yên: cứ điểm đang chiếm, tuyến công thành, pháo binh đang đỗ. Xe gây nhiễu địch làm nó lệch."),
            // Prompt 25 F2 batch C (DECISIONS 25F2-C): new support cards.
            ["guide.glide_bomb_strike"] = (
                "[[Glide bomb strike]] · {{count}} stand-off bombs · {{cp}} CP\n" +
                "How it fights: after a {{delay}} s warning, {{count}} [[glide bombs]] fall on the spot ({{blast}} m blast each); unlike an airstrike, no aircraft flies over the target, but a heavy interceptor can still shoot a bomb down.\n" +
                "Strong / weak: reaches a target behind short-range air defence; a heavy SAM or C-RAM can take a bomb out before it lands.\n" +
                "Tip: call it on dug-in defences an airstrike's jet could not survive flying over.",
                "[[Đòn bom lượn]] · {{count}} quả bom tầm xa · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây cảnh báo, {{count}} quả [[bom lượn]] rơi xuống điểm chọn (mỗi quả nổ bán kính {{blast}} m); khác không kích, không có máy bay bay qua mục tiêu, nhưng hệ đánh chặn hạng nặng vẫn bắn hạ được bom.\n" +
                "Mạnh / yếu: đánh trúng mục tiêu sau lưng phòng không tầm gần; SAM hạng nặng hoặc C-RAM vẫn có thể hạ một quả trước khi rơi.\n" +
                "Mẹo: dùng cho công sự kiên cố mà máy bay không kích không sống nổi khi bay qua."),
            ["guide.guided_shell_strike"] = (
                "[[Guided shell]] · one pinpoint round · {{cp}} CP\n" +
                "How it fights: after a {{delay}} s warning, one [[Excalibur/Krasnopol-class]] shell lands exactly on the spot, no scatter ({{blast}} m blast).\n" +
                "Strong / weak: certain against a target standing still; a moving vehicle can simply drive off before it lands.\n" +
                "Tip: call it the moment an enemy gun or vehicle parks; a barrage's 6 rounds scatter, this one does not.",
                "[[Đạn pháo dẫn đường]] · một phát trúng đích · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây cảnh báo, một quả đạn kiểu [[Excalibur/Krasnopol]] rơi đúng điểm chọn, không tản mát (nổ bán kính {{blast}} m).\n" +
                "Mạnh / yếu: chắc chắn trúng mục tiêu đứng yên; xe đang di chuyển có thể lái đi trước khi đạn rơi.\n" +
                "Mẹo: gọi ngay khi pháo hoặc xe địch vừa đỗ lại; pháo kích 6 phát tản mát, thẻ này thì không."),
            ["guide.cluster_at_strike"] = (
                "[[AT cluster bomb]] · {{count}} homing bomblets · {{cp}} CP\n" +
                "How it fights: after a {{delay}} s warning, up to {{count}} top-attack bomblets each find the nearest distinct enemy vehicle in the circle and strike its roof; aircraft and buildings are not hit.\n" +
                "Strong / weak: wipes out a whole cluster of tanks at once; wasted against a single vehicle or a fortified position.\n" +
                "Tip: call it on a column or a mass of armour, not on towers.",
                "[[Bom chùm chống tăng]] · {{count}} đầu đạn tự tìm · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây cảnh báo, tối đa {{count}} đầu đạn con đánh nóc, mỗi đầu đạn tự tìm một xe địch khác nhau trong vùng; không đánh máy bay và công trình.\n" +
                "Mạnh / yếu: xóa sổ cả cụm xe tăng cùng lúc; phí phạm nếu chỉ có một xe hoặc công sự kiên cố.\n" +
                "Mẹo: dùng cho đoàn xe hoặc cụm thiết giáp, không dùng cho tháp canh."),
            ["guide.uav_loiter_strike_support"] = (
                "[[Loitering UAV strike]] · circles for {{duration}} s · {{cp}} CP\n" +
                "How it fights: an [[attack UAV]] circles the point for {{duration}} s, firing at the strongest enemy vehicle it can reach; unlike every other card here, its strike is not instant.\n" +
                "Strong / weak: keeps pressure on a fight as it develops; enemy air defence can shoot the drone down and end it early.\n" +
                "Tip: call it as a fight starts, with cover against enemy anti-air.",
                "[[UAV lượn tấn công]] · lượn {{duration}} giây · {{cp}} CP\n" +
                "Cách đánh: một [[UAV tấn công]] lượn trên điểm chọn trong {{duration}} giây, tự bắn vào xe địch mạnh nhất trong tầm; khác mọi thẻ khác ở đây, đòn này không tức thì.\n" +
                "Mạnh / yếu: giữ áp lực suốt trận đánh đang diễn ra; phòng không địch bắn hạ được UAV, kết thúc sớm.\n" +
                "Mẹo: gọi ngay khi trận đánh bắt đầu, có người che chắn phòng không địch."),
            ["guide.ammo_resupply"] = (
                "[[Ammo resupply]] · instant refill · {{cp}} CP\n" +
                "How it fights: every friendly vehicle within {{radius}} m has its weapons refilled at once, no waiting.\n" +
                "Strong / weak: keeps artillery and aircraft in the fight when their stores run dry; useless on a vehicle that is not limited on ammunition.\n" +
                "Tip: call it on your howitzers and strike aircraft once their rate of fire drops.",
                "[[Thả dù tiếp đạn]] · nạp đầy ngay · {{cp}} CP\n" +
                "Cách đánh: mọi xe ta trong vòng {{radius}} m được nạp đầy đạn ngay lập tức, không phải chờ.\n" +
                "Mạnh / yếu: giữ pháo binh và máy bay tiếp tục chiến đấu khi hết đạn; vô dụng với xe không giới hạn đạn.\n" +
                "Mẹo: gọi cho lựu pháo và máy bay tấn công của bạn khi tốc độ bắn giảm."),
            ["guide.jam_storm"] = (
                "[[Jamming storm]] · {{radius}} m circle · {{cp}} CP\n" +
                "How it fights: after a {{delay}} s warning, every enemy drone in the circle is downed at once, and the circle then hides everything inside it for {{duration}} s.\n" +
                "Strong / weak: stops a drone swarm cold and blinds the enemy's view of what you do there; ground vehicles and towers are untouched.\n" +
                "Tip: call it over a drone launch site, or over your own advance to cover it.",
                "[[Bão gây nhiễu]] · vùng {{radius}} m · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây cảnh báo, mọi drone địch trong vùng rơi ngay, và vùng đó bị che khuất trong {{duration}} giây.\n" +
                "Mạnh / yếu: chặn đứng bầy drone và che mắt địch trong vùng đó; xe mặt đất và tháp canh không bị ảnh hưởng.\n" +
                "Mẹo: gọi trên điểm phóng drone địch, hoặc che chắn cho đợt tiến quân của bạn."),
            ["guide.illum_flare_strike"] = (
                "[[Illumination flare]] · {{radius}} m circle · {{cp}} CP\n" +
                "How it fights: a flare lights the circle for {{duration}} s, showing your side everything inside it, night or fog alike (as a UAV scan).\n" +
                "Strong / weak: the cheapest way to fight blind weather or the dark; a UAV scan shows stealth too, and costs more.\n" +
                "Tip: call it before pushing into a dark or foggy sector.",
                "[[Pháo sáng chiếu sáng]] · vùng {{radius}} m · {{cp}} CP\n" +
                "Cách đánh: pháo sáng chiếu vùng này trong {{duration}} giây, cho phe ta thấy mọi thứ trong đó, dù đêm hay sương mù (như UAV quét).\n" +
                "Mạnh / yếu: cách rẻ nhất để đối phó thời tiết xấu hoặc đêm tối; UAV quét còn thấy cả tàng hình nhưng đắt hơn.\n" +
                "Mẹo: gọi trước khi tiến vào khu vực tối hoặc nhiều sương mù."),
            ["guide.decoy_paradrop"] = (
                "[[Decoy paradrop]] · 3 fake tanks · {{cp}} CP\n" +
                "How it fights: 3 [[inflatable tank decoys]] land on the spot; the enemy takes them for real tanks and fires on them until it spots the trick, or for {{duration}} s.\n" +
                "Strong / weak: pulls fire off your real vehicles for free; a scout, radar or UAV scan up close sees through it at once (as the inflatable decoy tower does).\n" +
                "Tip: drop it on your flank just before a push, to pull the enemy's eye the wrong way.",
                "[[Mồi nhử thả dù]] · 3 xe tăng giả · {{cp}} CP\n" +
                "Cách đánh: 3 [[xe tăng bơm hơi]] rơi xuống điểm chọn; địch tưởng thật và bắn vào chúng cho tới khi phát hiện ra, hoặc hết {{duration}} giây.\n" +
                "Mạnh / yếu: hút hỏa lực khỏi xe thật miễn phí; trinh sát, radar hoặc UAV quét ở gần phát hiện ra ngay (như tháp mồi nhử bơm hơi).\n" +
                "Mẹo: thả ở sườn trận địa ngay trước một đợt tiến công, để đánh lạc hướng mắt địch."),
            ["guide.instant_counter_battery"] = (
                "[[Instant counter-battery]] · punishes enemy guns · {{cp}} CP\n" +
                "How it fights: after a {{delay}} s warning, every enemy artillery piece that fired in the last 10 s, anywhere within {{radius}} m, takes {{count}} rounds of {{blast}} m blasts.\n" +
                "Strong / weak: a real threat to enemy artillery that just opened up; a gun that has not fired recently is safe.\n" +
                "Tip: call it the moment enemy shells start landing on your side.",
                "[[Phản pháo tức thì]] · trừng phạt pháo địch · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây cảnh báo, mọi khẩu pháo địch vừa bắn trong 10 giây qua, ở bất kỳ đâu trong {{radius}} m, bị {{count}} loạt nổ bán kính {{blast}} m.\n" +
                "Mạnh / yếu: mối đe dọa thật với pháo địch vừa khai hỏa; khẩu nào chưa bắn gần đây thì an toàn.\n" +
                "Mẹo: gọi ngay khi đạn pháo địch bắt đầu rơi vào phe ta."),
            ["guide.drone_intercept_strike"] = (
                "[[Drone intercept strike]] · {{count}} interceptors · {{cp}} CP\n" +
                "How it fights: up to {{count}} small missiles each find the nearest distinct enemy drone in the circle and take it down; nothing else is hit.\n" +
                "Strong / weak: dumps a whole drone swarm or loitering-munition wave at once; useless against anything that is not a drone.\n" +
                "Tip: call it the moment a drone swarm shows on the minimap.",
                "[[Đòn tên lửa đánh chặn drone]] · {{count}} tên lửa nhỏ · {{cp}} CP\n" +
                "Cách đánh: tối đa {{count}} tên lửa nhỏ, mỗi quả tự tìm một drone địch khác nhau trong vùng và hạ nó; không đánh thứ gì khác.\n" +
                "Mạnh / yếu: dập cả bầy drone hoặc đợt đạn lảng vảng cùng lúc; vô dụng với bất cứ thứ gì không phải drone.\n" +
                "Mẹo: gọi ngay khi bầy drone địch hiện trên minimap."),
            ["guide.chaff_strike"] = (
                "[[Radar chaff]] · {{radius}} m circle · {{cp}} CP\n" +
                "How it fights: for {{duration}} s, the circle denies lock-on the same way a smoke screen does — built on the same zone, so it works exactly like one.\n" +
                "Strong / weak: opens a corridor for your own aircraft to fly through; a smoke screen already does the same job for ground sightlines and lasers, so pick whichever fits the target.\n" +
                "Tip: call it along the flight path you want your planes to take.",
                "[[Rải nhiễu radar]] · vùng {{radius}} m · {{cp}} CP\n" +
                "Cách đánh: trong {{duration}} giây, vùng này chặn khóa mục tiêu giống hệt màn khói — dùng chung một vùng che, nên hoạt động y hệt màn khói.\n" +
                "Mạnh / yếu: mở hành lang cho máy bay ta bay qua; màn khói cũng làm được việc này cho tầm nhìn mặt đất và laser, chọn thẻ nào hợp mục tiêu hơn.\n" +
                "Mẹo: gọi dọc đường bay bạn muốn máy bay mình đi qua."),
            ["guide.smoke_screen"] = (
                "[[Smoke screen]] · blocks sight · {{cp}} CP\n" +
                "How it fights: after {{delay}} s a {{radius}} m cloud stands for {{duration}} s; no one can see into or through it, so guns lose their [[line of sight]].\n" +
                "Strong / weak: saves units from long-range guns, ATGMs and railguns; it does no damage, and at point-blank range fighting goes on.\n" +
                "Tip: drop it between your advancing tanks and the enemy's [[tank destroyers]], or over a unit pulling back.",
                "[[Màn khói]] · che tầm nhìn · {{cp}} CP\n" +
                "Cách đánh: sau {{delay}} giây, đám khói {{radius}} m đứng trong {{duration}} giây; không ai nhìn vào hay xuyên qua được, súng pháo mất [[tầm nhìn]].\n" +
                "Mạnh / yếu: cứu quân ta khỏi pháo tầm xa, tên lửa chống tăng và pháo điện từ; không gây sát thương, sát sạt nhau thì vẫn đánh được.\n" +
                "Mẹo: thả giữa xe tăng ta đang tiến và [[xe diệt tăng]] địch, hoặc che cho xe đang rút lui."),
            ["guide.repair_drop"] = (
                "[[Repair]] · heals an area · {{cp}} CP\n" +
                "How it fights: repairs your vehicles within {{radius}} m by {{percent}}% of their health, spread over {{duration}} s.\n" +
                "Strong / weak: turns a close fight when your army is [[bunched up]]; wasted on units spread far apart.\n" +
                "Tip: call it on your tank line in the middle of the fight, not after it.",
                "[[Sửa chữa]] · hồi máu theo vùng · {{cp}} CP\n" +
                "Cách đánh: sửa cho xe ta trong vòng {{radius}} m tổng cộng {{percent}}% máu, rải đều trong {{duration}} giây.\n" +
                "Mạnh / yếu: lật ngược trận giằng co khi quân ta [[đứng gần nhau]]; phí nếu quân dàn quá rộng.\n" +
                "Mẹo: gọi xuống tuyến xe tăng ngay giữa trận, đừng đợi đánh xong."),
            ["guide.napalm_strike"] = (
                "[[Napalm strike]] · a line of fire · {{cp}} CP\n" +
                "How it fights: a jet lays {{count}} [[fire]] bombs along a {{length}} m line in the direction you drag; the ground is left burning.\n" +
                "Strong / weak: fire burns [[light vehicles]] (125%) and buildings; heavy armour takes only half, and aircraft none.\n" +
                "Tip: drag it through a column of light vehicles or a row of towers.",
                "[[Bom napalm]] · một hàng lửa · {{cp}} CP\n" +
                "Cách đánh: máy bay thả {{count}} quả [[bom lửa]] dọc đường {{length}} m theo hướng bạn kéo; mặt đất bị đốt cháy.\n" +
                "Mạnh / yếu: lửa thiêu [[xe nhẹ]] (125%) và nhà cửa; giáp dày chỉ nhận một nửa, máy bay thì không hề hấn gì.\n" +
                "Mẹo: kéo xuyên qua một đoàn xe nhẹ hoặc một dãy tháp canh."),
            ["guide.air_raid"] = (
                "[[Air raid]] · battle event · hits both sides\n" +
                "How it fights: a neutral bomber wave lays {{count}} [[bombs]] along a {{length}} m line over the busiest fight, {{delay}} s after the warning.\n" +
                "Strong / weak: hurts everyone under it, yours and theirs alike; only aircraft are safe.\n" +
                "Tip: when the warning shows, [[pull back]] from the main fight and let the bombs land on the enemy.",
                "[[Không kích bất ngờ]] · sự kiện trận đấu · trúng cả hai phe\n" +
                "Cách đánh: một đợt máy bay trung lập rải {{count}} quả [[bom]] dọc đường {{length}} m lên chỗ giao tranh ác liệt nhất, {{delay}} giây sau cảnh báo.\n" +
                "Mạnh / yếu: gây sát thương mọi thứ bên dưới, cả ta lẫn địch; chỉ máy bay là an toàn.\n" +
                "Mẹo: khi thấy cảnh báo, [[rút quân]] khỏi điểm nóng và để bom rơi trúng địch."),

            // Items: single use, bought with coins.
            ["guide.moab"] = (
                "[[MOAB]] · item · the biggest blast in the game\n" +
                "How it fights: one use; {{delay}} s after you tap, a huge bomb levels everything within about {{blast}} m.\n" +
                "Strong / weak: wipes out whole groups and towers and takes a big bite out of a [[boss]]; aircraft are safe.\n" +
                "Tip: save it for a boss, or for the moment a huge enemy wave [[bunches up]] on an objective.",
                "[[Bom MOAB]] · vật phẩm · vụ nổ lớn nhất trò chơi\n" +
                "Cách đánh: dùng một lần; {{delay}} giây sau khi chạm, quả bom khổng lồ san phẳng mọi thứ trong khoảng {{blast}} m.\n" +
                "Mạnh / yếu: xóa sổ cả cụm quân và tháp canh, cắn một miếng lớn vào máu [[boss]]; máy bay thì an toàn.\n" +
                "Mẹo: để dành cho boss, hoặc lúc cả đợt địch [[dồn cục]] trên một cứ điểm."),
            ["guide.cluster_strike"] = (
                "[[Cluster bombs]] · item · covers a wide strip\n" +
                "How it fights: one use; {{count}} [[bomblets]] carpet a {{length}} m strip, {{width}} m wide, in the direction you drag.\n" +
                "Strong / weak: great against spread-out light vehicles and artillery; each bomblet is small, so heavy tanks take little.\n" +
                "Tip: drag it along the enemy's rear, where their [[artillery]] and support trucks sit.",
                "[[Bom chùm]] · vật phẩm · phủ một dải rộng\n" +
                "Cách đánh: dùng một lần; {{count}} [[bom con]] rải thảm một dải dài {{length}} m, rộng {{width}} m, theo hướng bạn kéo.\n" +
                "Mạnh / yếu: rất tốt với xe nhẹ và pháo binh dàn trải; mỗi bom con nhỏ nên tăng hạng nặng ít hề hấn.\n" +
                "Mẹo: kéo dọc phía sau đội hình địch, nơi [[pháo binh]] và xe hỗ trợ của chúng đứng."),
            ["guide.reinforcements"] = (
                "[[Airdropped armour]] · item · {{units}} free vehicles\n" +
                "How it fights: one use; {{delay}} s after you tap, two battle tanks and an IFV [[drop in]] at that spot, at no CP cost.\n" +
                "Strong / weak: puts a strong group anywhere at once; once down, they are ordinary vehicles.\n" +
                "Tip: drop them on an [[objective]] you must hold, or right behind the enemy's artillery.",
                "[[Tiếp viện thả dù]] · vật phẩm · {{units}} xe miễn phí\n" +
                "Cách đánh: dùng một lần; {{delay}} giây sau khi chạm, hai tăng chủ lực và một xe chiến đấu bộ binh [[thả dù]] xuống điểm đó, không tốn CP.\n" +
                "Mạnh / yếu: có ngay một cụm quân mạnh ở bất kỳ đâu; tiếp đất rồi thì là xe bình thường.\n" +
                "Mẹo: thả xuống [[cứ điểm]] cần giữ, hoặc ngay sau lưng pháo binh địch."),
            ["guide.field_repair"] = (
                "[[Field repair]] · item · heals the whole army\n" +
                "How it fights: one use; every vehicle you have, anywhere on the map, [[repairs]] {{percent}}% of its health over {{duration}} s.\n" +
                "Strong / weak: turns a losing battle around; wasted if your army is still healthy.\n" +
                "Tip: use it in the middle of a big fight, when most of your vehicles are [[damaged]].",
                "[[Sửa chữa toàn quân]] · vật phẩm · hồi máu cả đội quân\n" +
                "Cách đánh: dùng một lần; mọi xe của ta, ở bất kỳ đâu trên bản đồ, được [[hồi]] {{percent}}% máu trong {{duration}} giây.\n" +
                "Mạnh / yếu: lật ngược trận đang thua; phí nếu quân ta còn khỏe.\n" +
                "Mẹo: dùng giữa trận đánh lớn, khi phần lớn xe ta đã [[mất máu]]."),
            ["guide.emp_blast"] = (
                "[[EMP blast]] · item · stuns the enemy\n" +
                "How it fights: one use; {{delay}} s after you tap, every enemy ground vehicle within {{radius}} m is [[stunned]] for {{duration}} s: no driving, no firing.\n" +
                "Strong / weak: freezes a whole enemy push; aircraft and bosses are not affected.\n" +
                "Tip: fire it on the enemy's tank line, then hit the frozen group with artillery or an [[airstrike]].",
                "[[Bom EMP]] · vật phẩm · làm tê liệt địch\n" +
                "Cách đánh: dùng một lần; {{delay}} giây sau khi chạm, mọi xe mặt đất địch trong {{radius}} m bị [[choáng]] {{duration}} giây: không chạy, không bắn.\n" +
                "Mạnh / yếu: đóng băng cả một đợt tấn công của địch; không tác dụng với máy bay và boss.\n" +
                "Mẹo: ném vào tuyến xe tăng địch, rồi nện cụm bị đóng băng bằng pháo binh hoặc [[không kích]]."),
            ["guide.shield_dome"] = (
                "[[Shield dome]] · item · protects your army\n" +
                "How it fights: one use; your vehicles within {{radius}} m take {{percent}}% less damage for {{duration}} s.\n" +
                "Strong / weak: saves a group from a boss, a barrage or a big strike; it only covers vehicles inside when it goes up.\n" +
                "Tip: drop it on your [[tank line]] just as a big fight starts.",
                "[[Khiên vòm]] · vật phẩm · che chắn quân ta\n" +
                "Cách đánh: dùng một lần; xe ta trong vòng {{radius}} m giảm {{percent}}% sát thương nhận vào trong {{duration}} giây.\n" +
                "Mạnh / yếu: cứu cụm quân khỏi boss, loạt pháo hoặc đòn đánh lớn; chỉ che những xe đứng bên trong lúc khiên bật lên.\n" +
                "Mẹo: thả lên [[tuyến xe tăng]] ngay khi trận đánh lớn bắt đầu."),
            ["guide.gunship_support"] = (
                "[[Gunship on call]] · item · an airborne gunship for {{duration}} s\n" +
                "How it fights: one use; a sky gunship arrives and [[orbits]] for {{duration}} s, firing its 105, 40 and 25 mm guns at ground targets.\n" +
                "Strong / weak: devastating on ground forces; it cannot hit aircraft, and enemy SAMs and fighters can shoot it down.\n" +
                "Tip: call it over the main ground fight once the enemy's [[anti-air]] is cleared.",
                "[[Pháo đài bay yểm trợ]] · vật phẩm · pháo hạm bay trong {{duration}} giây\n" +
                "Cách đánh: dùng một lần; pháo đài bay tới và [[bay vòng]] {{duration}} giây, pháo 105, 40 và 25 mm nã vào mục tiêu mặt đất.\n" +
                "Mạnh / yếu: tàn phá quân mặt đất; không bắn được máy bay, tên lửa phòng không và tiêm kích địch có thể bắn hạ nó.\n" +
                "Mẹo: gọi xuống trận đánh chính khi [[phòng không]] địch đã bị dọn sạch."),

            // Prompt 17 C: the new units and towers.
            ["guide.stealth_fighter"] = (
                "[[Stealth fighter]] · no armour · hunts aircraft and air defences\n" +
                "How it fights: [[stealth]]: enemies see it at 40% of their sight, and for 2.5 s after it fires; radar stations, guard towers and UAV scans show it. Four AIM-120s at aircraft, two GBU-39s it drops on anti-air vehicles and towers, a 25 mm gun.\n" +
                "Strong / weak: clears the sky and the SAMs before your strike aircraft come; it carries less than a fighter and goes back to rearm sooner.\n" +
                "Tip: send it ahead of your bombers; radars, guard towers and scans are what find it.",
                "[[Tiêm kích tàng hình]] · không giáp · săn máy bay và phòng không\n" +
                "Cách đánh: [[tàng hình]]: địch chỉ thấy ở 40% tầm nhìn, và trong 2,5 giây sau mỗi lần khai hỏa; trạm radar, tháp canh và UAV quét làm lộ nó. Bốn tên lửa AIM-120 đánh máy bay, hai bom GBU-39 thả vào xe và tháp phòng không, pháo 25 mm.\n" +
                "Mạnh / yếu: dọn sạch bầu trời và SAM trước khi máy bay cường kích tới; mang ít đạn hơn tiêm kích thường nên về hồi đạn sớm hơn.\n" +
                "Mẹo: cho bay trước đoàn oanh tạc; radar, tháp canh và UAV quét là thứ tìm ra nó."),
            ["guide.wingman_drone"] = (
                "[[Wingman drone]] · no armour · escort drone\n" +
                "How it fights: flies on its leader's wing (the nearest manned aircraft within 120 m; with none it patrols over the front) with two AIM-9s; an enemy anti-air missile aimed at its leader turns onto it four times in ten.\n" +
                "Strong / weak: keeps your fighters and bombers alive for a few more missiles; alone it is weak, and a fighter shoots it down easily.\n" +
                "Tip: buy it once you fly manned aircraft; it does not count against the six-aircraft cap (at most four a side).",
                "[[Drone hộ vệ]] · không giáp · drone hộ tống\n" +
                "Cách đánh: bay kèm cánh máy bay dẫn (máy bay có người lái gần nhất trong 120 m; không có thì tuần tra trên chiến tuyến) với hai tên lửa AIM-9; tên lửa phòng không địch nhắm vào máy bay dẫn có bốn phần mười cơ hội chuyển sang nó.\n" +
                "Mạnh / yếu: giúp tiêm kích và oanh tạc cơ sống thêm vài quả tên lửa; một mình thì yếu, tiêm kích địch bắn hạ dễ.\n" +
                "Mẹo: mua khi đã có máy bay có người lái; không tính vào trần sáu máy bay (tối đa bốn chiếc mỗi phe)."),
            ["guide.laser_tank"] = (
                "[[Laser tank destroyer]] · heavy armour in front · burns through armour\n" +
                "How it fights: an [[energy]] beam (40 m) that ramps from x0.3 to x2 over 6 s on one target and starts again on a new one; it pierces the thickest armour.\n" +
                "Strong / weak: melts heavy tanks and bosses; APS, reactive armour and cages do nothing to it, but smoke cuts the beam by 80% and a swarm of small vehicles keeps it at its weakest.\n" +
                "Tip: keep it on one big target, and screen it from light vehicles.",
                "[[Xe la-de diệt tăng]] · giáp dày mặt trước · đốt thủng giáp\n" +
                "Cách đánh: tia [[năng lượng]] (40 m) tăng từ ×0,3 lên ×2 trong 6 giây trên cùng một mục tiêu, đổi mục tiêu thì về lại mức thấp; xuyên cả giáp dày nhất.\n" +
                "Mạnh / yếu: nung chảy xe tăng nặng và boss; APS, giáp phản ứng nổ và lồng chắn không cản được, nhưng màn khói cắt 80% tia và bầy xe nhỏ giữ nó ở mức yếu nhất.\n" +
                "Mẹo: giữ nó trên một mục tiêu lớn, và che nó khỏi xe hạng nhẹ."),
            ["guide.shield_carrier"] = (
                "[[Shield carrier]] · thin armour · shields the front\n" +
                "How it fights: a [[shield dome]] of 12 m round it soaks up 1,000 damage of shells, bullets, bombs and missiles for everything of ours inside, then breaks; it comes back 20 s after its last hit. A roof MG.\n" +
                "Strong / weak: lets a tank line close in under fire; energy weapons go straight through, a dome never stacks with another, and the carrier itself is thin-skinned.\n" +
                "Tip: keep it just behind the leading tanks; enemies already inside the dome are not stopped by it.",
                "[[Xe phát khiên]] · giáp mỏng · che tuyến đầu\n" +
                "Cách đánh: [[vòm khiên]] 12 m quanh xe hấp thụ 1.000 sát thương từ đạn pháo, đạn súng, bom và tên lửa cho mọi đơn vị phe ta bên trong, rồi vỡ; hồi lại 20 giây sau đòn cuối. Có súng máy nóc.\n" +
                "Mạnh / yếu: giúp tuyến xe tăng áp sát dưới làn đạn; vũ khí năng lượng xuyên thẳng qua, nhiều vòm không cộng dồn, và bản thân xe giáp mỏng.\n" +
                "Mẹo: giữ ngay sau các xe tăng dẫn đầu; địch đã vào trong vòm thì vòm không chặn được."),
            ["guide.bunker_vehicle"] = (
                "[[Deployable bunker]] · medium armour, heavy dug in · holds ground\n" +
                "How it fights: on its tracks a 105 mm gun and a coaxial MG within a front arc; stopped with an enemy in reach, or on guard at a point or a choke, it [[digs in]] (3 s, no firing): front armour level 4, 44 m reach, turret all round. Ordered away, it packs up (3 s) first.\n" +
                "Strong / weak: an anchor for a point or a siege line; slow to react, and artillery and aircraft strike its thin roof.\n" +
                "Tip: send it where the line should hold; the icon over it shows digging in and dug in.",
                "[[Xe công sự triển khai]] · giáp vừa, dày khi triển khai · giữ trận địa\n" +
                "Cách đánh: khi di chuyển có pháo 105 mm và súng máy đồng trục trong cung phía trước; dừng lại khi có địch trong tầm, hoặc canh giữ cứ điểm hay điểm nghẽn, thì [[triển khai]] (3 giây, không bắn): giáp trước cấp 4, tầm 44 m, tháp xoay 360°. Khi được lệnh đi, nó thu lại trước (3 giây).\n" +
                "Mạnh / yếu: làm chốt cho cứ điểm hoặc tuyến công thành; phản ứng chậm, pháo binh và máy bay đánh vào nóc mỏng.\n" +
                "Mẹo: đưa tới nơi tuyến cần trụ lại; biểu tượng trên xe cho biết đang triển khai hay đã triển khai."),
            ["guide.swarm_carrier"] = (
                "[[Drone mothership aircraft]] · light armour · a drone swarm anywhere\n" +
                "How it fights: flies over the target, releasing its eight [[FPV drones]] (shaped charge, top attack) one after another, each to its own target, and drops two guided bombs from the same bay as it passes; its stores come back over 16 s.\n" +
                "Strong / weak: puts a swarm where no FPV carrier or drone hangar reaches; fighters and SAMs shoot it down, and C-RAMs, laser AA, EW towers and jammers stop its drones.\n" +
                "Tip: send it in when the enemy's anti-air is busy; the drones do not take your aircraft slots.",
                "[[Máy bay mẹ thả drone]] · giáp mỏng · bầy drone tới mọi nơi\n" +
                "Cách đánh: bay qua mục tiêu, thả lần lượt tám [[drone FPV]] (nổ lõm, đánh nóc), mỗi chiếc một mục tiêu, và thả thêm hai bom dẫn đường từ cùng khoang khi bay qua; kho đạn hồi lại trong 16 giây.\n" +
                "Mạnh / yếu: đưa bầy drone tới nơi xe drone FPV hay nhà chứa drone không với tới; tiêm kích và SAM bắn hạ được nó, còn C-RAM, xe la-de phòng không, tháp EW và xe gây nhiễu chặn được drone.\n" +
                "Mẹo: tung ra khi phòng không địch đang bận; drone không chiếm chỗ máy bay của ta."),
            ["guide.shield_tower"] = (
                "[[Shield generator]] · large tower · shields part of the base\n" +
                "How it fights: no gun; a [[shield dome]] of 25 m soaks up 3,000 damage of shells, bombs, bullets and missiles for everything of ours under it, then breaks; it is back 30 s after its last hit.\n" +
                "Strong / weak: keeps the towers round it standing through a barrage; energy weapons go through, domes do not stack, and the generator is the enemy's first target.\n" +
                "Tip: put it among your strongest towers; at rank 7 a branch makes the dome smaller and tougher, or quicker to come back.",
                "[[Máy phát khiên]] · tháp lớn · che một phần căn cứ\n" +
                "Cách đánh: không có súng; [[vòm khiên]] 25 m hấp thụ 3.000 sát thương từ đạn pháo, bom, đạn súng và tên lửa cho mọi thứ phe ta bên dưới, rồi vỡ; hồi lại 30 giây sau đòn cuối.\n" +
                "Mạnh / yếu: giữ các tháp quanh nó đứng vững qua trận pháo kích; vũ khí năng lượng xuyên qua, nhiều vòm không cộng dồn, và máy phát là mục tiêu đầu tiên của địch.\n" +
                "Mẹo: đặt giữa những tháp mạnh nhất; nhánh hạng 7 cho vòm nhỏ mà bền hơn, hoặc hồi lại nhanh hơn."),
            ["guide.cp_relay"] = (
                "[[CP relay]] · small tower · economy\n" +
                "How it fights: no gun; [[+0.1 CP a second]] for its side, a second relay +0.06, a third nothing; it pays nothing for 5 s after a hit.\n" +
                "Strong / weak: more CP for a quiet base; it takes a small defence slot, and enemy attackers go for it first.\n" +
                "Tip: two at most in a base, never on an outpost; weigh it against the tower it replaces.",
                "[[Trạm tiếp tế CP]] · tháp nhỏ · kinh tế\n" +
                "Cách đánh: không có súng; [[+0,1 CP mỗi giây]] cho phe mình, trạm thứ hai +0,06, trạm thứ ba không thêm gì; bị bắn thì ngừng trả 5 giây.\n" +
                "Mạnh / yếu: thêm CP cho căn cứ yên ổn; chiếm một ô phòng thủ nhỏ, và quân địch tấn công căn cứ sẽ nhắm nó trước.\n" +
                "Mẹo: tối đa hai trạm mỗi căn cứ, không đặt ở tiền đồn; cân nhắc với tòa tháp mà nó thay chỗ."),
            // Prompt 25 F2 batch A (DECISIONS 25F2-A): the balance sheet's new units and structures.
            ["guide.heavy_flak_tower"] = (
                "[[Heavy flak tower]] · medium tower · heavy air bursts\n" +
                "How it fights: a big shell every 2 s, bursting 6 m wide at aircraft out to 70 m; lowered, it hits tanks out to 50 m.\n" +
                "Strong / weak: breaks up [[bombers]] and tight formations; too slow for lone jets and drones.\n" +
                "Tip: pair it with quick AA guns that take the helicopters.",
                "[[Tháp cao xạ hạng nặng]] · tháp ô vừa · đạn nổ trên không\n" +
                "Cách đánh: 2 giây một phát lớn, nổ trên không rộng 6 m, tầm 70 m; hạ nòng bắn xe tăng trong 50 m.\n" +
                "Mạnh / yếu: bẻ gãy [[oanh tạc cơ]] và tốp máy bay dày; quá chậm với tiêm kích lẻ và drone.\n" +
                "Mẹo: đặt cạnh pháo phòng không bắn nhanh để lo trực thăng."),
            ["guide.aa_gun_vehicle"] = (
                "[[40 mm AA gun vehicle]] · light armour · steady flak\n" +
                "How it fights: four [[proximity-fused]] rounds a second on the move, out to 48 m.\n" +
                "Strong / weak: beats helicopters, drones and light cars; tanks shrug it off.\n" +
                "Tip: keep it with the front line against helicopters.",
                "[[Xe cao xạ 40 mm]] · giáp nhẹ · cao xạ nhịp đều\n" +
                "Cách đánh: bốn phát [[ngòi cận đích]] mỗi giây, vừa chạy vừa bắn, tầm 48 m.\n" +
                "Mạnh / yếu: thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhiễm.\n" +
                "Mẹo: đi cùng tuyến đầu để chống trực thăng."),
            ["guide.shorad_vehicle"] = (
                "[[Light SAM vehicle]] · very light armour · one big ripple\n" +
                "How it fights: eight [[heat-seeking missiles]] in one ripple out to 44 m, on the move, then a 15 s reload.\n" +
                "Strong / weak: swats helicopters and drones in one burst; flares fool some, and it dies to anything on the ground.\n" +
                "Tip: save the ripple for a helicopter pair.",
                "[[Xe tên lửa phòng không nhẹ]] · giáp rất mỏng · xả một loạt\n" +
                "Cách đánh: tám [[tên lửa tầm nhiệt]] một loạt, tầm 44 m, vừa chạy vừa bắn, rồi nạp 15 giây.\n" +
                "Mạnh / yếu: hạ trực thăng và drone trong một loạt; pháo sáng lừa được vài quả, dưới đất thứ gì cũng diệt được nó.\n" +
                "Mẹo: dành loạt tên lửa cho một cặp trực thăng."),
            ["guide.microwave_vehicle"] = (
                "[[Anti-drone microwave vehicle]] · light armour · a swarm at once\n" +
                "How it fights: every 8 s a [[microwave pulse]] downs every enemy drone in a 60° cone out to 30 m; vehicles are unharmed.\n" +
                "Strong / weak: wipes out FPV swarms and drone aircraft; useless against anything else.\n" +
                "Tip: park it beside your tanks where the drones dive.",
                "[[Xe vi sóng chống drone]] · giáp nhẹ · diệt cả bầy\n" +
                "Cách đánh: mỗi 8 giây một [[xung vi sóng]] làm rơi mọi drone địch trong hình nón 60°, tầm 30 m; xe không hề hấn.\n" +
                "Mạnh / yếu: quét sạch bầy FPV và máy bay drone; vô dụng với mọi thứ khác.\n" +
                "Mẹo: đỗ cạnh xe tăng ta, nơi drone lao xuống."),
            ["guide.at_gun_emplacement"] = (
                "[[Anti-tank gun emplacement]] · small tower · cheap tank killer\n" +
                "How it fights: an [[armour-piercing]] shot every 5 s out to 38 m, only 45° either side of its front; the gun turns slowly.\n" +
                "Strong / weak: stops tanks that come head on; artillery and flanking cars kill it.\n" +
                "Tip: face it down the road the enemy armour takes.",
                "[[Ụ pháo chống tăng]] · tháp ô nhỏ · diệt tăng giá rẻ\n" +
                "Cách đánh: 5 giây một phát [[xuyên giáp]], tầm 38 m, chỉ trong 45° hai bên phía trước; pháo xoay chậm.\n" +
                "Mạnh / yếu: chặn xe tăng lao thẳng tới; pháo binh và xe vòng sườn diệt được nó.\n" +
                "Mẹo: quay mặt nó về con đường thiết giáp địch đi."),
            ["guide.nlos_atgm_vehicle"] = (
                "[[Beyond-sight ATGM vehicle]] · light armour · anti-tank artillery\n" +
                "How it fights: a heavy missile every 10 s out to 90 m, [[over cover]] onto the roof, at what its side sees.\n" +
                "Strong / weak: kills tanks from behind a hill; blind alone, slow to fire.\n" +
                "Tip: pair it with a scout or a UAV scan.",
                "[[Xe tên lửa chống tăng ngoài tầm nhìn]] · giáp nhẹ · pháo binh chống tăng\n" +
                "Cách đánh: 10 giây một tên lửa lớn, tầm 90 m, [[bay vòng qua vật cản]] đánh nóc, vào mục tiêu phe ta nhìn thấy.\n" +
                "Mạnh / yếu: diệt xe tăng từ sau đồi; tự đi thì mù, bắn chậm.\n" +
                "Mẹo: đi cặp với trinh sát hoặc UAV quét."),
            ["guide.radar_atgm_vehicle"] = (
                "[[Radar-guided ATGM vehicle]] · medium armour · sees through smoke\n" +
                "How it fights: two heavy missiles 0.6 s apart out to 50 m, then 9 s; its [[radar sees through smoke]].\n" +
                "Strong / weak: beats tanks hiding in smoke; APS stops some missiles.\n" +
                "Tip: bring it against smoke carriers.",
                "[[Xe tên lửa chống tăng dẫn radar]] · giáp vừa · nhìn xuyên khói\n" +
                "Cách đánh: hai tên lửa lớn cách nhau 0,6 giây, tầm 50 m, rồi nạp 9 giây; [[radar nhìn xuyên khói]].\n" +
                "Mạnh / yếu: thắng xe tăng nấp trong khói; APS chặn được vài quả.\n" +
                "Mẹo: đem ra đối đầu xe tạo khói."),
            ["guide.recoilless_jeep"] = (
                "[[Recoilless rifle jeep]] · no armour · hit and run\n" +
                "How it fights: one heavy [[HEAT round]] every 6.7 s out to 32 m; parked, it is hard to see until it fires.\n" +
                "Strong / weak: ambushes tanks from the flank for 3 CP; anything that fires back kills it.\n" +
                "Tip: hit a tank in the side, then drive off.",
                "[[Xe jeep súng không giật]] · không giáp · đánh rồi chạy\n" +
                "Cách đánh: 6,7 giây một phát [[nổ lõm]] nặng, tầm 32 m; đỗ yên thì khó thấy cho tới khi bắn.\n" +
                "Mạnh / yếu: phục kích xe tăng từ sườn chỉ với 3 CP; thứ gì bắn trả cũng hạ được nó.\n" +
                "Mẹo: bắn vào sườn một chiếc tăng rồi chạy."),
            ["guide.airborne_vehicle"] = (
                "[[Airborne fighting vehicle]] · light armour · behind the lines\n" +
                "How it fights: tap its card, then ground your side sees: it lands by [[parachute]] in 6 s; anti-air can shoot it on the way down.\n" +
                "Strong / weak: takes empty points and hits artillery from behind; loses to tanks.\n" +
                "Tip: tap the card twice to send it to the drop zone instead.",
                "[[Xe đổ bộ đường không]] · giáp nhẹ · sau lưng địch\n" +
                "Cách đánh: chạm thẻ rồi chạm vùng phe ta nhìn thấy: nó [[nhảy dù]] xuống trong 6 giây; phòng không bắn được khi còn dưới dù.\n" +
                "Mạnh / yếu: chiếm cứ điểm trống, đánh pháo binh từ phía sau; thua xe tăng.\n" +
                "Mẹo: chạm thẻ hai lần để đưa nó về bãi thả."),
            ["guide.wheeled_howitzer"] = (
                "[[Shoot-and-scoot howitzer]] · no armour · fire and move\n" +
                "How it fights: four 155 mm shells in 6 s out to 90 m, then it [[drives off]] at once and reloads for 25 s.\n" +
                "Strong / weak: counter-battery fire lands on empty ground; its thin hull dies fast.\n" +
                "Tip: keep it far back behind a scout.",
                "[[Pháo bánh lốp bắn rồi chạy]] · không giáp · bắn rồi đổi chỗ\n" +
                "Cách đánh: bốn phát 155 mm trong 6 giây, tầm 90 m, rồi [[chạy ngay]] và nạp lại 25 giây.\n" +
                "Mạnh / yếu: phản pháo rơi vào chỗ trống; thân mỏng, dễ chết.\n" +
                "Mẹo: giữ thật xa phía sau, có trinh sát đi trước."),
            ["guide.sp_mortar"] = (
                "[[Turreted SP mortar]] · medium armour · a rain of bombs\n" +
                "How it fights: four 120 mm bombs out to 60 m that [[land at the same moment]], then 10 s.\n" +
                "Strong / weak: crushes a group before it can scatter; loses to tanks up close.\n" +
                "Tip: aim it at groups your scouts find.",
                "[[Cối tự hành tháp kín]] · giáp vừa · mưa đạn cối\n" +
                "Cách đánh: bốn quả cối 120 mm, tầm 60 m, [[rơi xuống cùng lúc]], rồi nghỉ 10 giây.\n" +
                "Mạnh / yếu: nghiền một cụm quân trước khi kịp tản ra; áp sát thì thua xe tăng.\n" +
                "Mẹo: nhắm vào các cụm quân trinh sát tìm thấy."),
            ["guide.glide_bomber"] = (
                "[[Long-range glide bomber]] · light armour · bombs from far off\n" +
                "How it fights: releases a [[glide bomb]] from 90 m and turns away; the bomb glides onto the target at 20 m/s.\n" +
                "Strong / weak: hits towers and groups outside short-range AA; point defences can shoot the bombs down.\n" +
                "Tip: send it at fixed defences, with fighters over it.",
                "[[Máy bay ném bom lượn tầm xa]] · giáp nhẹ · ném bom từ xa\n" +
                "Cách đánh: thả [[bom lượn]] từ cách 90 m rồi quay đi; bom lượn 20 m/s xuống mục tiêu.\n" +
                "Mạnh / yếu: đánh tháp và cụm quân ngoài tầm phòng không gần; hệ đánh chặn bắn hạ được bom.\n" +
                "Mẹo: tung vào công sự cố định, có tiêm kích che."),
            ["guide.recon_jet"] = (
                "[[High-speed recon jet]] · no armour · one big look\n" +
                "How it fights: no weapons; [[one straight pass]] across the map shows a strip 60 m wide for 20 s, stealth too, then it leaves.\n" +
                "Strong / weak: finds artillery, hidden guns and decoys; flies too high for all but long-range SAMs and fighters.\n" +
                "Tip: call it just before a barrage.",
                "[[Máy bay trinh sát tốc độ cao]] · không giáp · một lần nhìn lớn\n" +
                "Cách đánh: không vũ khí; [[bay thẳng một lượt]] ngang map, làm lộ dải rộng 60 m trong 20 giây, cả tàng hình, rồi rời trận.\n" +
                "Mạnh / yếu: tìm pháo binh, ụ súng ẩn và mồi nhử; bay cao, chỉ tên lửa tầm xa và tiêm kích với tới.\n" +
                "Mẹo: gọi ngay trước một trận pháo kích."),
            ["guide.interceptor_jet"] = (
                "[[Interceptor]] · no armour · bomber killer\n" +
                "How it fights: dashes in and fires two [[very long-range missiles]] from 90 m, big aircraft first; nothing inside 15 m.\n" +
                "Strong / weak: kills bombers and gunships early; loses a close dogfight.\n" +
                "Tip: hold it back for the enemy's bombers.",
                "[[Tiêm kích đánh chặn]] · không giáp · diệt oanh tạc cơ\n" +
                "Cách đánh: lao vào, bắn hai [[tên lửa tầm siêu xa]] từ 90 m, ưu tiên máy bay lớn; không bắn trong 15 m.\n" +
                "Mạnh / yếu: diệt oanh tạc cơ và pháo hạm bay từ sớm; thua khi quần thảo gần.\n" +
                "Mẹo: giữ lại chờ oanh tạc cơ của địch."),
            ["guide.radar_scout"] = (
                "[[Radar scout car]] · light armour · stands watch\n" +
                "How it fights: sees 50 m moving; standing 2 s it raises its [[radar mast]]: 80 m, and it all but hides.\n" +
                "Strong / weak: spots for artillery from afar and unmasks decoys; weak on the move.\n" +
                "Tip: park it on a flank and leave it there.",
                "[[Xe trinh sát bọc thép radar mặt đất]] · giáp nhẹ · đứng gác\n" +
                "Cách đánh: khi chạy nhìn 50 m; đứng yên 2 giây thì dựng [[cột radar]]: nhìn 80 m và gần như ẩn.\n" +
                "Mạnh / yếu: chỉ điểm cho pháo binh từ xa, lật tẩy mồi nhử; di chuyển thì yếu.\n" +
                "Mẹo: đỗ ở cánh và để yên đó."),
            ["guide.blast_wall"] = (
                "[[Gabion blast wall]] · small structure · cover for towers\n" +
                "How it fights: no gun, no obstacle; towers up to 10 m behind it take [[30 % less]] direct fire.\n" +
                "Strong / weak: keeps front towers alive against tanks; shells and bombs come over it.\n" +
                "Tip: put it in front of your best tower.",
                "[[Tường chắn đạn]] · công trình ô nhỏ · che cho tháp\n" +
                "Cách đánh: không súng, không chặn đường; tháp trong 10 m sau nó nhận ít hơn [[30%]] sát thương bắn thẳng.\n" +
                "Mạnh / yếu: giữ tháp tuyến đầu trước xe tăng; đạn cầu vồng và bom vẫn vượt qua.\n" +
                "Mẹo: đặt trước tháp mạnh nhất."),
            ["guide.inflatable_decoy"] = (
                "[[Inflatable decoy]] · small structure · draws the fire\n" +
                "How it fights: looks like a [[gun turret]]; the enemy shoots it until their scouts, radars, drones or scans find it out.\n" +
                "Strong / weak: wastes the enemy's shells and missiles for little; almost no health.\n" +
                "Tip: put it where the first shells would land.",
                "[[Mồi nhử bơm hơi]] · công trình ô nhỏ · hút hỏa lực\n" +
                "Cách đánh: trông như [[tháp pháo]]; địch bắn vào nó cho tới khi trinh sát, radar, drone hoặc UAV quét lật tẩy.\n" +
                "Mạnh / yếu: làm địch phí đạn pháo và tên lửa; gần như không có máu.\n" +
                "Mẹo: đặt nơi loạt pháo đầu tiên sẽ rơi."),
            ["guide.fire_control_centre"] = (
                "[[Fire-control centre]] · utility module · links the towers\n" +
                "How it fights: towers within 30 m hit [[12 % harder]] and gang up on one target.\n" +
                "Strong / weak: turns a tower cluster into one block; useless for towers spread thin.\n" +
                "Tip: put your best guns within its 30 m.",
                "[[Trung tâm điều khiển hỏa lực]] · mô-đun tiện ích · liên kết tháp\n" +
                "Cách đánh: tháp trong 30 m gây thêm [[12%]] sát thương và dồn hỏa lực vào một mục tiêu.\n" +
                "Mạnh / yếu: biến cụm tháp thành một khối; vô dụng khi tháp đặt thưa.\n" +
                "Mẹo: đặt các khẩu mạnh nhất trong vòng 30 m."),
            ["guide.searchlight"] = (
                "[[Battlefield searchlight]] · small structure · light in the dark\n" +
                "How it fights: at [[night and in fog]] your side sees everything within 35 m of it; enemies there shoot 20 % worse.\n" +
                "Strong / weak: turns night attacks against the attacker; does nothing by day.\n" +
                "Tip: take it for night and fog battles.",
                "[[Đèn pha chiến trường]] · công trình ô nhỏ · ánh sáng đêm\n" +
                "Cách đánh: [[ban đêm và trong sương mù]], phe ta thấy mọi thứ trong 35 m quanh nó; địch trong vùng bắn kém 20%.\n" +
                "Mạnh / yếu: biến trận đêm thành bất lợi cho kẻ tấn công; ban ngày vô dụng.\n" +
                "Mẹo: mang theo cho trận đêm và sương mù."),
            ["guide.barrage_balloon"] = (
                "[[Radar aerostat]] · small structure · AA that never fires\n" +
                "How it fights: enemy bombing within 40 m of it [[scatters 50 % wider]]; enemy helicopters keep out; it also [[shows aircraft]] within 45 m, stealth ones too.\n" +
                "Strong / weak: spoils bombing runs on the base; guided bombs do not care.\n" +
                "Tip: put it over the towers you most want to keep.",
                "[[Khí cầu neo radar]] · công trình ô nhỏ · phòng không không bắn\n" +
                "Cách đánh: bom địch ném trong 40 m quanh nó [[tản mát thêm 50%]]; trực thăng địch tránh vùng; nó còn [[làm lộ máy bay]] trong 45 m, cả máy bay tàng hình.\n" +
                "Mạnh / yếu: phá các lượt ném bom vào căn cứ; bom dẫn đường không bị ảnh hưởng.\n" +
                "Mẹo: đặt trên những tháp cần giữ nhất."),
            ["guide.visual_jammer"] = (
                "[[Visual jammer]] · utility module · hides the base\n" +
                "How it fights: enemies see nothing of yours within 35 m of it from further than [[15 m]], unless they are scouts.\n" +
                "Strong / weak: artillery cannot find what it covers; scouts and UAV scans see through it.\n" +
                "Tip: put your towers and artillery inside its 35 m.",
                "[[Máy tạo nhiễu tầm nhìn]] · mô-đun tiện ích · che căn cứ\n" +
                "Cách đánh: địch không thấy gì của ta trong 35 m quanh nó nếu xa hơn [[15 m]], trừ trinh sát.\n" +
                "Mạnh / yếu: pháo binh không tìm được thứ nó che; trinh sát và UAV quét nhìn xuyên.\n" +
                "Mẹo: đặt tháp và pháo binh trong vòng 35 m."),
            ["guide.fibre_fpv_carrier"] = (
                "[[Fibre-optic FPV carrier]] · light armour · drones jammers cannot stop\n" +
                "How it fights: flies one [[fibre-optic drone]] at a time onto armour out to 60 m, one every 6 s; no jammer scrambles it.\n" +
                "Strong / weak: beats tanks behind jammers; point defences still take its drones.\n" +
                "Tip: bring it when the enemy leans on jammers.",
                "[[Xe phóng drone FPV cáp quang]] · giáp nhẹ · không thể gây nhiễu\n" +
                "Cách đánh: điều khiển từng chiếc [[drone cáp quang]] lao vào xe bọc thép, tầm 60 m, 6 giây một chiếc; gây nhiễu vô tác dụng.\n" +
                "Mạnh / yếu: thắng xe tăng núp sau xe gây nhiễu; hệ đánh chặn vẫn hạ được drone.\n" +
                "Mẹo: mang theo khi địch dùng nhiều gây nhiễu."),
            ["guide.interceptor_drone_vehicle"] = (
                "[[Interceptor drone vehicle]] · light armour · drones against drones\n" +
                "How it fights: an [[interceptor drone]] every 4 s out to 60 m at drones and helicopters, and at enemy drones in flight.\n" +
                "Strong / weak: thins out FPV swarms and helicopters; jets fly past untouched.\n" +
                "Tip: keep it beside your tanks and artillery.",
                "[[Xe drone đánh chặn]] · giáp nhẹ · drone chống drone\n" +
                "Cách đánh: 4 giây một [[drone đánh chặn]], tầm 60 m, vào drone và trực thăng, cả drone địch đang bay tới.\n" +
                "Mạnh / yếu: làm mỏng bầy FPV và trực thăng; máy bay phản lực bay qua vô sự.\n" +
                "Mẹo: giữ cạnh xe tăng và pháo binh ta."),
            ["guide.troop_shelter"] = (
                "[[Troop shelter]] · medium structure · shelter from shells\n" +
                "How it fights: your vehicles within 15 m take [[half]] from shells, mortars, bombs and strikes; not direct fire.\n" +
                "Strong / weak: keeps defenders alive through a barrage; no help against tanks.\n" +
                "Tip: gather your defenders round it when the shells come.",
                "[[Hầm che quân]] · công trình ô vừa · tránh đạn pháo\n" +
                "Cách đánh: xe ta trong 15 m nhận [[một nửa]] sát thương pháo, cối, bom và không kích; không che đạn bắn thẳng.\n" +
                "Mạnh / yếu: giữ quân phòng thủ sống qua trận pháo kích; vô dụng trước xe tăng.\n" +
                "Mẹo: kéo quân phòng thủ về quanh nó khi đạn pháo tới."),
            ["guide.flare_tower"] = (
                "[[Flare tower]] · small structure · light in bursts\n" +
                "How it fights: at [[night and in fog]], every 15 s a flare over the nearest enemy within 40 m shows everything within 30 m.\n" +
                "Strong / weak: finds night raiders, stealth too; does nothing by day.\n" +
                "Tip: pair it with a searchlight on night maps.",
                "[[Tháp pháo sáng]] · công trình ô nhỏ · chiếu sáng theo đợt\n" +
                "Cách đánh: [[ban đêm và trong sương mù]], 15 giây một quả pháo sáng trên địch gần nhất trong 40 m, làm lộ mọi thứ trong 30 m.\n" +
                "Mạnh / yếu: tìm quân đột kích đêm, cả tàng hình; ban ngày vô dụng.\n" +
                "Mẹo: đi cặp với đèn pha ở map đêm."),
            ["guide.laser_ad_station"] = (
                "[[Laser anti-drone station]] · medium tower · never runs dry\n" +
                "How it fights: a [[laser]] at drones only out to 40 m, and interceptors for rockets and mortar bombs; smoke cuts it by 80 %.\n" +
                "Strong / weak: shuts down drone swarms and rocket rain; useless against aircraft and tanks.\n" +
                "Tip: keep your own smoke away from it.",
                "[[Trạm phòng không laser chống drone]] · tháp ô vừa · không bao giờ hết đạn\n" +
                "Cách đánh: [[laser]] chỉ bắn drone, tầm 40 m, cùng bộ đánh chặn rốc-két và đạn cối; khói làm tia yếu 80%.\n" +
                "Mạnh / yếu: dập bầy drone và mưa rốc-két; vô dụng trước máy bay và xe tăng.\n" +
                "Mẹo: giữ khói của ta tránh xa nó."),
            ["guide.aa_gun_tower"] = (
                "[[40 mm AA gun]] · medium tower · steady flak\n" +
                "How it fights: four [[proximity-fused]] rounds a second out to 48 m, at aircraft and light vehicles.\n" +
                "Strong / weak: beats helicopters, drones and light cars; tanks shrug it off.\n" +
                "Tip: the middle AA gun, between the quick flak and the heavy flak.",
                "[[Pháo phòng không 40 mm]] · tháp ô vừa · cao xạ nhịp đều\n" +
                "Cách đánh: bốn phát [[ngòi cận đích]] mỗi giây, tầm 48 m, bắn cả máy bay lẫn xe nhẹ.\n" +
                "Mạnh / yếu: thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhiễm.\n" +
                "Mẹo: khẩu ở giữa, giữa cao xạ bắn nhanh và cao xạ hạng nặng."),
            // (batch A guides: new entries above)
            // Prompt 25 F2 batch B (DECISIONS 25F2-B): short cards for the 33 Thấp-priority stand-ins (dx23 not in this pass).
            ["guide.aa_57mm_vehicle"] = ("[[57 mm AA vehicle]] · heavier flak\n" + "Two rounds a second, out to 52 m; hits light vehicles too.",
                "[[Xe phòng không 57 mm]] · cao xạ đòn nặng\n" + "Hai phát mỗi giây, tầm 52 m; trúng được cả xe nhẹ."),
            ["guide.mine_rocket_truck"] = ("[[Mine-laying rocket truck]] · area denial\n" + "Seeds a minefield ahead; no direct damage.",
                "[[Xe pháo phản lực rải mìn]] · khóa hướng tiến\n" + "Rải mìn phía trước; không gây sát thương trực tiếp."),
            ["guide.prop_attack_plane"] = ("[[Light prop attack plane]] · cheap, slow, low\n" + "A gun and rockets against light vehicles; buy several.",
                "[[Máy bay cường kích cánh quạt]] · rẻ, chậm, bay thấp\n" + "Súng và rốc-két trị xe nhẹ; mua theo tốp."),
            ["guide.light_attack_heli"] = ("[[Light attack helicopter]] · fast, thin armour\n" + "A few ATGMs and a gun; hit a flank, then pull back.",
                "[[Trực thăng tấn công hạng nhẹ]] · nhanh, giáp mỏng\n" + "Vài tên lửa chống tăng và súng máy; đánh sườn rồi rút."),
            ["guide.next_gen_tank"] = ("[[Next-generation tank]] · double-charge APS\n" + "Shrugs off the first two incoming rockets or shells.",
                "[[Tăng thế hệ mới]] · APS hai lần\n" + "Chặn được hai phát tên lửa hoặc đạn pháo đầu tiên."),
            ["guide.demolition_line_vehicle"] = ("[[Demolition-line vehicle]] · mine roller\n" + "Mines ahead of it go off harmlessly; opens the way in.",
                "[[Xe phá mìn bằng dây nổ]] · con lăn phá mìn\n" + "Mìn phía trước nổ vô hại; mở đường tấn công."),
            ["guide.combat_wreck_car"] = ("[[Wreck-turret car]] · goes out loud\n" + "A bigger cook-off blast when it falls, for now.",
                "[[Xe khi hỏng thành công sự]] · nổ lớn khi hết máu\n" + "Đợt này nổ mạnh hơn khi bị hạ."),
            ["guide.drone_hijack_vehicle"] = ("[[Drone-hijack vehicle]] · anti-drone pulse\n" + "Downs enemy drones in a cone, for now (no side-flip yet).",
                "[[Xe chiếm quyền drone]] · xung chống drone\n" + "Hạ drone địch trong hình nón; chưa lật được phe."),
            ["guide.manpads_tower"] = ("[[MANPADS post]] · cheap small-slot AA\n" + "Short-ranged Stingers, aircraft and helicopters only.",
                "[[Tổ tên lửa vác vai]] · phòng không ô nhỏ rẻ\n" + "Tên lửa Stinger tầm ngắn, chỉ bắn máy bay và trực thăng."),
            ["guide.river_patrol_boat"] = ("[[River patrol boat]] · fast, light\n" + "Controls a river; a machine gun and a grenade launcher.",
                "[[Tàu tuần tra sông]] · nhanh, nhẹ\n" + "Kiểm soát mặt sông; súng máy và súng phóng lựu."),
            ["guide.river_gunboat"] = ("[[River gunboat]] · floating artillery\n" + "Slow; a 100 mm gun for the shore.",
                "[[Pháo hạm sông]] · pháo binh nổi\n" + "Chậm; pháo 100 mm bắn phá bờ."),
            ["guide.coastal_ashm_vehicle"] = ("[[Coastal AShM vehicle]] · very long reach\n" + "A slow-reloading heavy missile, strongest at distant targets.",
                "[[Xe tên lửa chống hạm bờ biển]] · tầm rất xa\n" + "Tên lửa nặng nạp chậm, mạnh nhất ở mục tiêu xa."),
            ["guide.auto_loader_howitzer"] = ("[[Auto-loading howitzer]] · four rounds at once\n" + "A burst that lands together, then a long reload.",
                "[[Lựu pháo nạp tự động]] · bốn phát cùng lúc\n" + "Loạt đạn rơi cùng lúc, rồi nạp lâu."),
            ["guide.amphib_light_vehicle"] = ("[[Amphibious light vehicle]] · beach landing\n" + "An autocannon against light vehicles, for coastal maps.",
                "[[Xe lội nước tốc độ cao]] · đổ bộ từ biển\n" + "Pháo tự động trị xe nhẹ, dùng ở map ven biển."),
            ["guide.airborne_light_tank"] = ("[[Airborne light tank]] · drops behind the line\n" + "A 105 mm gun, thin armour, parachutes in wherever its side sees.",
                "[[Tăng nhẹ thả dù]] · rơi sau lưng địch\n" + "Pháo 105 mm, giáp mỏng, thả dù ở nơi phe ta nhìn thấy."),
            ["guide.stealth_naval_strike"] = ("[[Stealth carrier strike jet]] · precision only\n" + "Two guided bombs against buildings and parked targets; no gun.",
                "[[Cường kích tàng hình trên hạm]] · chỉ đánh chính xác\n" + "Hai bom dẫn đường trị công trình và xe đứng yên; không pháo."),
            ["guide.twin_rotor_gunship"] = ("[[Twin-rotor gunship]] · low, slow firepower\n" + "Between the attack helicopter and the Sky Fortress; easy to hit.",
                "[[Pháo hạm trực thăng hai rô-to]] · hỏa lực bay thấp\n" + "Giữa trực thăng vũ trang và Pháo hạm bay; dễ bị bắn trúng."),
            ["guide.ground_drone_carrier"] = ("[[Ground drone carrier]] · cheap scout, for now\n" + "Its three minion robots are not modelled yet.",
                "[[Xe chỉ huy robot mặt đất]] · trinh sát rẻ, tạm thời\n" + "Ba robot con chưa được làm."),
            ["guide.mobile_repair_vehicle"] = ("[[Mobile repair vehicle]] · wide, slow repair\n" + "A bigger radius than the engineer, a slower rate.",
                "[[Xe sửa chữa lưu động]] · sửa rộng, chậm\n" + "Vùng sửa rộng hơn công binh, tốc độ chậm hơn."),
            ["guide.radar_support_vehicle"] = ("[[Mobile AA radar]] · far-seeing scout, for now\n" + "Its AA-range bonus is not modelled yet.",
                "[[Xe radar phòng không di động]] · trinh sát tầm xa, tạm thời\n" + "Phần cộng tầm bắn cho PK chưa được làm."),
            ["guide.towed_at_gun"] = ("[[Towed anti-tank gun]] · glass cannon\n" + "Long reach, hard-hitting, no armour.",
                "[[Pháo chống tăng kéo cỡ lớn]] · mạnh nhưng mong manh\n" + "Bắn xa, mạnh, không giáp."),
            ["guide.flare_searchlight_tower"] = ("[[Flare tower]] · cheap night light\n" + "Every 15 s at night, a flare over the nearest enemy lights up round it.",
                "[[Tháp pháo sáng]] · chiếu sáng đêm rẻ\n" + "Mỗi 15 giây ban đêm, một quả pháo sáng trên đầu địch gần nhất."),
            ["guide.recoilless_gun_tower"] = ("[[Recoilless gun post]] · cheap AT, short reach\n" + "Weaker than the anti-tank gun emplacement, but cheaper.",
                "[[Ụ súng không giật]] · chống tăng rẻ, tầm ngắn\n" + "Yếu hơn ụ pháo chống tăng nhưng rẻ hơn."),
            ["guide.bunker_shelter_tower"] = ("[[Bunker]] · rainbow-proof\n" + "Vehicles of its side nearby take half from shells, mortars, bombs and strikes.",
                "[[Hầm ngầm che quân]] · chống pháo kích\n" + "Xe phe ta gần đó nhận ít hơn một nửa sát thương từ pháo, cối, bom, không kích."),
            ["guide.dazzler_vehicle"] = ("[[Laser dazzler vehicle]] · plays as a jammer\n" + "Throws off nearby enemy fire, for now.",
                "[[Xe laser chói lóa]] · chơi như xe gây nhiễu\n" + "Làm nhiễu loạn hỏa lực địch gần đó, tạm thời."),
            ["guide.ground_cruise_missile_vehicle"] = ("[[Ground cruise missile vehicle]] · very long reach\n" + "Two slow missiles; the enemy has time to shoot them down.",
                "[[Xe phóng tên lửa hành trình]] · tầm rất xa\n" + "Hai tên lửa chậm; địch có thời gian bắn hạ."),
            ["guide.aerial_tanker"] = ("[[Aerial tanker]] · unarmed, for now\n" + "Its endurance bonus for nearby aircraft is not modelled yet.",
                "[[Máy bay tiếp dầu]] · không vũ trang, tạm thời\n" + "Phần cộng thời gian bay cho máy bay phe ta chưa được làm."),
            ["guide.heavy_lift_helicopter"] = ("[[Heavy-lift helicopter]] · unarmed transport, for now\n" + "Airlifting a tower anywhere seen is not modelled yet.",
                "[[Trực thăng cẩu tháp]] · vận tải không vũ trang, tạm thời\n" + "Việc cẩu tháp đặt tùy nơi chưa được làm."),
            ["guide.gps_jammer_vehicle"] = ("[[GPS jammer vehicle]] · plays as a jammer\n" + "Throws off nearby enemy fire, for now.",
                "[[Xe gây nhiễu định vị]] · chơi như xe gây nhiễu\n" + "Làm nhiễu loạn hỏa lực địch gần đó, tạm thời."),
            ["guide.drone_net_tower"] = ("[[Drone net corridor]] · cheap, passive\n" + "Drones flying through are downed; vehicles pass freely.",
                "[[Lưới chắn drone]] · rẻ, thụ động\n" + "Drone bay qua bị hạ; xe đi qua bình thường."),
            ["guide.one_shot_atgm_tower"] = ("[[One-shot ATGM battery]] · one big volley\n" + "Eight Kornets against a big push, then it's spent.",
                "[[Bệ tên lửa phòng thủ một lần]] · một loạt lớn\n" + "Tám tên lửa Kornet chặn đợt tấn công lớn, rồi hết đạn."),
            // (batch B guides: new entries above)
            // Prompt 20 M: the two new battlefields.
            ["guide.map.openpit"] = (
                "[[Deepcut Mine]] · desert battlefield · a pit in three rings\n" +
                "How it fights: three broken rings of rock step down to the pit floor (the centre point), with ramps through each; the 14 m [[haul road]] winds round the upper bench and crosses the floor, and flank roads run past the spoil heaps to the crusher plant and the ore loadout on the rim (the side points).\n" +
                "Strong / weak: favours [[artillery]] and long guns on the rim looking down the benches, and armour that holds the ramps; fast raiders are slowed by the rings and do best on the flank roads.\n" +
                "Tip: hold the ramps, not the floor: the side that keeps them decides who gets down; the plants' buildings are good cover for anti-tank vehicles.",
                "[[Deepcut Mine]] · chiến trường sa mạc · hố mỏ ba vành\n" +
                "Cách đánh: ba vành đá đứt quãng hạ dần xuống đáy hố (cứ điểm giữa), vành nào cũng có dốc xuống; [[đường vận quặng]] rộng 14 m vòng quanh bậc trên rồi băng qua đáy hố, còn các đường sườn chạy qua bãi thải tới nhà máy nghiền và bãi xuất quặng trên miệng hố (hai cứ điểm bên).\n" +
                "Mạnh / yếu: có lợi cho [[pháo binh]] và pháo tầm xa đứng trên miệng hố nhìn xuống các bậc, cùng thiết giáp giữ được các dốc; xe đột kích nhanh bị các vành đá cản bước, nên mạnh nhất trên các đường sườn.\n" +
                "Mẹo: giữ các dốc chứ đừng giữ đáy hố: bên nào nắm được dốc sẽ quyết định ai được xuống; nhà xưởng của hai nhà máy là chỗ nấp tốt cho xe chống tăng."),
            ["guide.map.orbitalgate"] = (
                "[[Skygate Array]] · snow battlefield · a spaceport with an open centre\n" +
                "How it fights: the centre point is a 60 m [[drop-pod field]] with no cover at all, ringed by floodlights and an apron road; a launch pad on either flank (the side points) is packed with gantries, fuel tanks and blockhouses, and a radar post stands astride each camp's road to the field.\n" +
                "Strong / weak: the open field favours [[long-range]] guns, artillery and aircraft and punishes anything caught crossing it; the pads and the pine woods between the lanes favour short-range armour and ambushes.\n" +
                "Tip: take the pads first and cross the field only in force, under smoke; drop pods come down in the open, so keep guns on its edge.",
                "[[Skygate Array]] · chiến trường tuyết · sân bay vũ trụ trống ở giữa\n" +
                "Cách đánh: cứ điểm giữa là [[bãi đáp khoang đổ bộ]] rộng 60 m, hoàn toàn không có chỗ nấp, viền quanh bằng đèn pha và đường sân đỗ; hai bệ phóng ở hai bên sườn (hai cứ điểm bên) dày đặc giàn phóng, bồn nhiên liệu và lô cốt, còn mỗi trạm ra-đa nằm chắn ngang đường từ căn cứ ra bãi đáp.\n" +
                "Mạnh / yếu: bãi trống có lợi cho pháo [[tầm xa]], pháo binh và máy bay, và trừng phạt mọi thứ bị bắt gặp giữa bãi; bệ phóng và rừng thông giữa các tuyến có lợi cho thiết giáp tầm gần và phục kích.\n" +
                "Mẹo: chiếm bệ phóng trước, chỉ băng qua bãi khi đủ đông và có khói che; khoang đổ bộ đáp xuống chỗ trống, nên hãy đặt súng quanh mép bãi."),
        };
    }
}
