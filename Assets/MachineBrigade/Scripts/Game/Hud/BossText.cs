using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 20 pass 2 (DECISIONS 19E): the boss ranks' words, the new bosses' names, Guide cards, parts tips and
    /// radio lines, their big attacks, their new part kinds, and the radio lines of the bosses that now have one
    /// (every boss speaks for its general, prompt 20 K). The existing bosses' renames are prompt 20 pass 1's (it
    /// owns their "unit." keys); the new bosses are named here on its "Name · subtitle" rule.
    /// </summary>
    public static class BossText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- ranks (F.4, G.4)
            ["boss.rank.main"] = ("Boss", "Boss"),
            ["boss.rank.mini"] = ("Mini boss", "Mini boss"),

            // ---------------------------------------------------------------- the boss file (play-test 6, DECISIONS 21B)
            ["guide.boss.file"] = ("Boss file: {boss}", "Hồ sơ boss: {boss}"),
            ["guide.boss.fileButton"] = ("Boss file", "Hồ sơ boss"),
            ["guide.boss.close"] = ("Close", "Đóng"),
            ["guide.boss.noCard"] = ("A boss is no card: no level, equipment or CP cost. Its numbers at campaign strength.",
                "Boss không phải thẻ: không có cấp, trang bị hay giá CP. Chỉ số ở sức mạnh chiến dịch."),
            ["guide.boss.numbers"] = ("Numbers", "Chỉ số"),
            ["guide.boss.armour"] = ("Armour: front {front}, side {side}, rear {rear}, top {top}", "Giáp: trước {front}, hông {side}, sau {rear}, nóc {top}"),
            ["guide.boss.partStats"] = ("armour {armour} · {hp} health", "giáp {armour} · {hp} máu"),
            ["guide.boss.partCount"] = ("{count|# part|# parts} to break", "{count} bộ phận có thể phá"),
            ["guide.boss.escorts"] = ("Escorts", "Hộ tống"),
            ["guide.boss.escorts.none"] = ("It fights alone.", "Boss chiến đấu một mình."),
            ["guide.boss.escorts.arrive"] = ("Arriving with it: {units}", "Đến cùng boss: {units}"),
            ["guide.boss.escorts.phases"] = ("{count|# more wave|# more waves} at its phase changes", "Thêm {count} đợt khi boss đổi pha"),

            // ---------------------------------------------------------------- names
            ["unit.moloch"] = ("Moloch · Mobile Factory", "Moloch · Nhà máy di động"),
            ["unit.daedalus"] = ("Daedalus · Orbital Lander", "Daedalus · Tàu đổ bộ quỹ đạo"),
            ["unit.kronos"] = ("Kronos · Mining Excavator", "Kronos · Máy xúc mỏ"),
            ["unit.typhon"] = ("Typhon · Missile Submarine", "Typhon · Tàu ngầm tên lửa"),
            ["unit.ixion"] = ("Ixion · Giant Wheel", "Ixion · Xe bánh khổng lồ"),
            ["unit.caspian"] = ("Caspian · Ekranoplan", "Caspian · Tàu bay sát mặt nước"),
            ["unit.bastion_mk0"] = ("Bastion Mk.0 · Prototype Fortress", "Bastion Mk.0 · Pháo đài nguyên mẫu"),
            ["unit.fenrir"] = ("Fenrir · Vanguard", "Fenrir · Xe tiên phong"),
            ["unit.scylla"] = ("Scylla · Destroyer", "Scylla · Tàu khu trục"),
            ["unit.locust"] = ("Locust · Drone Tender", "Locust · Tàu con drone"),
            ["unit.behemoth_mk2"] = ("Behemoth Mk.II · Upgraded Behemoth", "Behemoth Mk.II · Behemoth nâng cấp"),
            ["unit.icarus_mk0"] = ("Icarus Mk.0 · Prototype Spacecraft", "Icarus Mk.0 · Phi thuyền nguyên mẫu"),
            ["unit.argus"] = ("Argus · Scout Airship", "Argus · Khí cầu trinh sát"),
            ["short.moloch"] = ("Moloch", "Moloch"),
            ["short.daedalus"] = ("Daedalus", "Daedalus"),
            ["short.kronos"] = ("Kronos", "Kronos"),
            ["short.typhon"] = ("Typhon", "Typhon"),
            ["short.ixion"] = ("Ixion", "Ixion"),
            ["short.caspian"] = ("Caspian", "Caspian"),
            ["short.bastion_mk0"] = ("Bastion Mk.0", "Bastion Mk.0"),
            ["short.fenrir"] = ("Fenrir", "Fenrir"),
            ["short.scylla"] = ("Scylla", "Scylla"),
            ["short.locust"] = ("Locust", "Locust"),
            ["short.behemoth_mk2"] = ("Behemoth Mk.II", "Behemoth Mk.II"),
            ["short.icarus_mk0"] = ("Icarus Mk.0", "Icarus Mk.0"),
            ["short.argus"] = ("Argus", "Argus"),

            // ---------------------------------------------------------------- role notes
            ["note.moloch"] = ("Varga's tracked factory: four 120 mm turrets, flak, and two workshop doors that keep sending out vehicles. Front armour 4, sides 3, rear 2.", "Nhà máy bánh xích của Varga: bốn tháp pháo 120 mm, cao xạ và hai cửa xưởng liên tục thả xe ra. Giáp trước cấp 4, hông 3, sau 2."),
            ["note.daedalus"] = ("Aurel's troop lander: drops pods without pause, two 30 mm guns, point-defence lasers. Upper hull 3, belly 2.", "Tàu đổ bộ của Aurel: thả khoang đổ bộ liên tục, hai pháo 30 mm, tháp la-de phòng thủ. Thân trên cấp 3, bụng 2."),
            ["note.kronos"] = ("A giant bucket-wheel excavator on a fixed route to your base, crushing walls and towers. Reaching your HQ loses the mission.", "Máy xúc bánh gầu khổng lồ chạy theo đường cố định về căn cứ ta, nghiền cả tường và tháp. Tới HQ là thua nhiệm vụ."),
            ["note.typhon"] = ("A missile submarine: out of reach while submerged, surfaces on a schedule; launches missiles at your base from under water.", "Tàu ngầm tên lửa: lặn thì không bắn tới được, nổi lên theo lịch; phóng tên lửa vào căn cứ ta từ dưới nước."),
            ["note.ixion"] = ("A Tsar Tank of a wheel: rolls fast and straight, crushes light vehicles, turns very slowly.", "Xe bánh khổng lồ kiểu xe tăng Sa hoàng: lăn nhanh theo đường thẳng, nghiền xe nhẹ, xoay rất chậm."),
            ["note.caspian"] = ("A sea monster of an ekranoplan: fast passes along the coast, then away; anti-ship missiles at your base.", "Tàu bay sát mặt nước \"quái vật biển\": lao dọc bờ từng lượt rồi vòng ra xa; tên lửa chống hạm đánh vào căn cứ."),
            ["note.bastion_mk0"] = ("The first Bastion: a mortar and two 40 mm guns on tracks, crawling towards your base.", "Bastion đầu tiên: một khẩu cối và hai pháo 40 mm trên xích, bò dần về căn cứ ta."),
            ["note.fenrir"] = ("Orlov's fast raider: two rocket boxes and flak; it dashes in, fires and pulls back.", "Xe đột kích nhanh của Orlov: hai hộp rốc-két và cao xạ; lao vào bắn rồi rút."),
            ["note.scylla"] = ("Kessler's destroyer on the near-shore lane: one main turret, missile cells, a CIWS. Tank guns reach it from the piers.", "Tàu khu trục của Kessler trên tuyến gần bờ: một tháp pháo chính, ống phóng tên lửa, CIWS. Pháo xe tăng bắn tới từ đầu cầu tàu."),
            ["note.locust"] = ("A thin-skinned drone tender: launches drones without pause. Bring anti-air.", "Tàu con drone vỏ mỏng: thả drone liên tục. Mang phòng không theo."),
            ["note.behemoth_mk2"] = ("Varga's upgraded Behemoth under ice-coated armour (front 4): main gun, two flak guns, a protection system.", "Behemoth nâng cấp của Varga, giáp phủ băng (trước cấp 4): pháo chính, hai cao xạ, hệ thống bảo vệ chủ động."),
            ["note.icarus_mk0"] = ("Aurel's prototype spacecraft: high and low on a fixed schedule, never in orbit; a laser turret and a pod bay.", "Phi thuyền nguyên mẫu của Aurel: đổi tầng cao và thấp theo lịch cố định, không lên quỹ đạo; tháp la-de và khoang đổ bộ."),
            ["note.argus"] = ("A scout airship: while it lives the enemy's artillery falls far tighter. Flak and a radar.", "Khí cầu trinh sát: khi nó còn, pháo binh địch bắn chính xác hơn nhiều. Cao xạ và radar."),

            // ---------------------------------------------------------------- Guide cards
            ["guide.moloch"] = (
                "[[Boss]] · mobile factory · builds an army as it comes\n" +
                "How it fights: crawls down the mission's road; its two [[workshop doors]] send out 1-2 vehicles every 20 s (light tanks and IFVs, battle tanks from phase 2), one more each minute, never more than six alive. Four 120 mm turrets and flak cover it.\n" +
                "Strong / weak: front armour [[4]], sides 3, rear [[2]]: the doors are at the back, and so is its weak armour. Broken tracks slow it.\n" +
                "Tip: flank it and break both doors first: it stops building, and its big attack is only the shells.",
                "[[Boss]] · nhà máy di động · vừa đi vừa sinh quân\n" +
                "Cách đánh: bò chậm theo đường của nhiệm vụ; hai [[cửa xưởng]] cứ 20 giây thả 1–2 xe (xe tăng nhẹ và xe bộ binh, từ pha 2 thêm tăng chủ lực), mỗi phút thêm một xe mỗi lượt, tối đa sáu xe còn sống. Bốn tháp pháo 120 mm và cao xạ che chắn.\n" +
                "Mạnh / yếu: giáp trước cấp [[4]], hông 3, sau [[2]]: cửa xưởng ở phía sau, giáp mỏng cũng ở đó. Phá cụm xích thì nó chậm lại.\n" +
                "Mẹo: vòng ra sau, phá cả hai cửa trước: nó ngừng sinh xe, đòn lớn chỉ còn loạt pháo."),
            ["guide.daedalus"] = (
                "[[Boss]] · orbital lander · a rain of drop pods\n" +
                "How it fights: about 10 s in orbit (out of reach), then high and low on a fixed schedule, never back to orbit. Its three [[pod bays]] drop pods of 1-2 vehicles without pause (at most eight alive), each pod a target as it falls. In phase 3 it stops low with every bay open.\n" +
                "Strong / weak: its own guns are weaker than Icarus's; upper hull [[3]], belly [[2]]. Point-defence lasers take missiles aimed at it.\n" +
                "Tip: shoot the pods down and break the bays: each one lost slows the drops, and the mass drop falls short.",
                "[[Boss]] · tàu đổ bộ quỹ đạo · mưa khoang đổ bộ\n" +
                "Cách đánh: khoảng 10 giây trên quỹ đạo (không bắn tới được), sau đó đổi tầng cao và thấp theo lịch cố định, không lên lại quỹ đạo. Ba [[cửa thả khoang]] thả liên tục khoang chở 1–2 xe (tối đa tám xe còn sống); khoang đang rơi bắn hạ được. Pha 3 nó dừng hẳn ở tầng thấp, mở toàn bộ khoang.\n" +
                "Mạnh / yếu: tự nó bắn yếu hơn Icarus; thân trên cấp [[3]], bụng [[2]]. Tháp la-de phòng thủ chặn tên lửa bắn vào nó.\n" +
                "Mẹo: bắn hạ khoang đang rơi và phá cửa thả: mỗi cửa mất là thả chậm hơn, đòn đổ bộ lớn cũng hụt đi."),
            ["guide.kronos"] = (
                "[[Boss]] · mining excavator · crushes its way to your HQ\n" +
                "How it fights: very slowly down a fixed route to your base; its [[bucket wheel]] crushes everything in front of it, walls and towers too. If it reaches your HQ the mission is lost. Phase 2 it goes faster; phase 3 the wheel spins up and throws rock round it.\n" +
                "Strong / weak: wheel armour [[4]], body 3, track units [[2]]. Each track unit broken slows it.\n" +
                "Tip: break the tracks to buy time, and the [[boom]] to stop its sweep; do not build walls in its way.",
                "[[Boss]] · máy xúc mỏ · nghiền đường tới HQ\n" +
                "Cách đánh: chạy rất chậm theo đường cố định về căn cứ ta; [[bánh gầu]] nghiền mọi thứ phía trước, cả tường lẫn tháp. Tới được HQ là thua nhiệm vụ. Pha 2 nó đi nhanh hơn; pha 3 bánh gầu quay nhanh và hất đá vụn ra xung quanh.\n" +
                "Mạnh / yếu: bánh gầu giáp cấp [[4]], thân 3, cụm xích [[2]]. Mỗi cụm xích bị phá là nó chậm lại.\n" +
                "Mẹo: phá cụm xích để câu giờ, phá [[cần gầu]] để chặn đòn quét; đừng xây tường chắn đường nó."),
            ["guide.typhon"] = (
                "[[Boss]] · missile submarine · strikes from under the sea\n" +
                "How it fights: submerged (out of reach) and surfaced (a target on the water) on each phase's schedule, coming up somewhere else each time; bubbles mark the spot first. Surfaced, it fires cruise missiles and guards itself with a SAM. Phase 3 it stays up and adds a 100 mm deck gun.\n" +
                "Strong / weak: hull armour [[4]], sail and deck [[2]]: artillery, bombs and top attacks hit the deck.\n" +
                "Tip: park artillery and aircraft for the bubbles; break the [[launch doors]] during a warning (they open above the water) or shoot the missiles down.",
                "[[Boss]] · tàu ngầm tên lửa · đánh từ dưới biển\n" +
                "Cách đánh: lặn (không bắn tới được) và nổi (mục tiêu trên mặt nước) theo lịch từng pha, mỗi lần nổi ở một chỗ khác; bong bóng báo trước chỗ nổi. Khi nổi nó phóng tên lửa hành trình và tự vệ bằng tên lửa phòng không. Pha 3 nổi hẳn, thêm pháo boong 100 mm.\n" +
                "Mạnh / yếu: thân giáp cấp [[4]], tháp chỉ huy và boong [[2]]: pháo binh, bom và đòn đánh nóc đánh vào boong.\n" +
                "Mẹo: chờ sẵn pháo binh và máy bay chỗ bong bóng; phá [[cửa ống phóng]] lúc cảnh báo (cửa mở trên mặt nước) hoặc bắn hạ tên lửa."),
            ["guide.ixion"] = (
                "[[Mini boss]] · giant wheel · rolls over your line\n" +
                "How it fights: rolls fast and straight on two huge [[wheels]], crushing vehicles in its way (light ones worst), and turns very slowly. Its 76 mm gun fires from the hub.\n" +
                "Strong / weak: the rear [[steering wheel]] is armour 1, its weak point; a big wheel broken makes it circle and slow down.\n" +
                "Tip: step aside from its line and hit it from the flanks as it turns.",
                "[[Mini boss]] · xe bánh khổng lồ · lăn qua đội hình ta\n" +
                "Cách đánh: lăn nhanh theo đường thẳng trên hai [[bánh lớn]], nghiền xe trên đường (xe nhẹ nặng nhất), xoay rất chậm. Pháo 76 mm bắn từ giữa trục.\n" +
                "Mạnh / yếu: [[bánh lái sau]] giáp cấp 1, là điểm yếu; phá một bánh lớn thì nó quay vòng và chậm lại.\n" +
                "Mẹo: tránh khỏi đường lăn và đánh vào hông khi nó xoay."),
            ["guide.caspian"] = (
                "[[Mini boss]] · ekranoplan · fast passes along the coast\n" +
                "How it fights: skims in along the coast for about 6 s at a time, then swings out to sea for about 20 s; a target on the water. Its big attack is four anti-ship missiles at the shore and your base.\n" +
                "Strong / weak: thin armour; the nose [[engines]] broken slow it down.\n" +
                "Tip: keep fast-firing guns on the shore for its passes, and anti-air or C-RAM for the missiles.",
                "[[Mini boss]] · tàu bay sát mặt nước · lao dọc bờ từng lượt\n" +
                "Cách đánh: lao dọc bờ khoảng 6 giây mỗi lượt rồi vòng ra xa khoảng 20 giây; là mục tiêu trên mặt nước. Đòn lớn là bốn tên lửa chống hạm vào bờ và căn cứ ta.\n" +
                "Mạnh / yếu: giáp mỏng; phá [[cụm động cơ]] ở mũi thì nó chậm lại.\n" +
                "Mẹo: để sẵn pháo bắn nhanh trên bờ đón lượt lao, và phòng không hoặc C-RAM cho tên lửa."),
            ["guide.bastion_mk0"] = (
                "[[Mini boss]] · prototype fortress · crawls at your base\n" +
                "How it fights: the first Bastion off Brandt's line: a heavy [[mortar]] and two 40 mm turrets on tracks, crawling slowly towards your base.\n" +
                "Strong / weak: thick front, slow; the turrets are its only close defence.\n" +
                "Tip: break the mortar and it is harmless at range.",
                "[[Mini boss]] · pháo đài nguyên mẫu · bò về căn cứ ta\n" +
                "Cách đánh: chiếc Bastion đầu tiên của Brandt: một [[khẩu cối]] hạng nặng và hai tháp pháo 40 mm trên xích, bò chậm về phía căn cứ ta.\n" +
                "Mạnh / yếu: mặt trước dày, chậm; hai tháp pháo là thứ phòng thủ gần duy nhất.\n" +
                "Mẹo: phá khẩu cối là nó hết nguy hiểm từ xa."),
            ["guide.fenrir"] = (
                "[[Mini boss]] · vanguard · hit and run\n" +
                "How it fights: fast: it dashes in, empties two [[rocket boxes]] and pulls back; flak keeps helicopters off.\n" +
                "Strong / weak: far lighter than Jötunn; it cannot hold ground.\n" +
                "Tip: catch it as it pulls back, with tank hunters on its line of retreat.",
                "[[Mini boss]] · xe tiên phong · đánh nhanh rút nhanh\n" +
                "Cách đánh: nhanh: lao vào, xả hai [[hộp rốc-két]] rồi rút; cao xạ đuổi trực thăng.\n" +
                "Mạnh / yếu: nhẹ hơn Jötunn nhiều; không giữ trận địa được.\n" +
                "Mẹo: đón nó lúc rút, đặt xe diệt tăng trên đường rút."),
            ["guide.scylla"] = (
                "[[Mini boss]] · destroyer · close to the shore\n" +
                "How it fights: faster than Leviathan, on the near-shore lane: one main turret shells the shore, missile cells fire cruise missiles, a CIWS takes missiles and drones.\n" +
                "Strong / weak: close enough for tank guns on the pier heads.\n" +
                "Tip: hold the piers with tanks and break the [[CIWS]] before sending missiles.",
                "[[Mini boss]] · tàu khu trục · sát bờ\n" +
                "Cách đánh: nhanh hơn Leviathan, chạy tuyến gần bờ: một tháp pháo chính nã vào bờ, ống phóng bắn tên lửa hành trình, CIWS chặn tên lửa và drone.\n" +
                "Mạnh / yếu: đủ gần để pháo xe tăng ở đầu cầu tàu bắn tới.\n" +
                "Mẹo: giữ cầu tàu bằng xe tăng, phá [[CIWS]] trước khi dùng tên lửa."),
            ["guide.locust"] = (
                "[[Mini boss]] · drone tender · drones without end\n" +
                "How it fights: its [[drone bay]] launches drones without pause; flak on its back.\n" +
                "Strong / weak: a very thin hull (armour 1): anti-air brings it down fast.\n" +
                "Tip: break the drone bay and it has nothing left.",
                "[[Mini boss]] · tàu con drone · drone không dứt\n" +
                "Cách đánh: [[khoang drone]] thả drone liên tục; cao xạ trên lưng.\n" +
                "Mạnh / yếu: thân rất mỏng (giáp cấp 1): phòng không hạ nó nhanh.\n" +
                "Mẹo: phá khoang drone là nó hết đòn."),
            ["guide.behemoth_mk2"] = (
                "[[Mini boss]] · upgraded Behemoth · ice-coated armour\n" +
                "How it fights: Varga's upgrade after the Behemoth fell: its main gun, two flak guns and a protection system that shoots down missiles.\n" +
                "Strong / weak: front armour [[4]] under the ice; sides and rear far thinner.\n" +
                "Tip: flank it; break the [[protection system]] before sending missiles.",
                "[[Mini boss]] · Behemoth nâng cấp · giáp phủ băng\n" +
                "Cách đánh: bản nâng cấp của Varga sau khi Behemoth gục: pháo chính, hai cao xạ và hệ thống bảo vệ chủ động bắn hạ tên lửa.\n" +
                "Mạnh / yếu: mặt trước giáp cấp [[4]] dưới lớp băng; hông và sau mỏng hơn nhiều.\n" +
                "Mẹo: đánh vào hông; phá [[hệ thống bảo vệ]] trước khi dùng tên lửa."),
            ["guide.icarus_mk0"] = (
                "[[Mini boss]] · prototype spacecraft · your first look at Project Icarus\n" +
                "How it fights: never in orbit: high and low on a fixed schedule. A [[laser turret]] and a [[pod bay]]; its satellite link calls down three tungsten rods.\n" +
                "Strong / weak: at high altitude only long-range anti-air and fighters reach it; low, every anti-air weapon does.\n" +
                "Tip: wait for its low windows; break the uplink to stop the rods.",
                "[[Mini boss]] · phi thuyền nguyên mẫu · lần đầu thấy Dự án Icarus\n" +
                "Cách đánh: không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. Một [[tháp la-de]] và một [[khoang đổ bộ]]; liên kết vệ tinh gọi ba thanh vonfram.\n" +
                "Mạnh / yếu: ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng thấp mọi vũ khí phòng không đều tới.\n" +
                "Mẹo: chờ lúc nó xuống thấp; phá ăng-ten liên kết để chặn thanh vonfram."),
            ["guide.argus"] = (
                "[[Mini boss]] · scout airship · directs the enemy's guns\n" +
                "How it fights: while it lives, the enemy's artillery falls about half as wide; its big attack calls a barrage on a marked area. Flak guns and a [[radar]].\n" +
                "Strong / weak: slow and big; only anti-air and fighters reach it.\n" +
                "Tip: break the radar and the enemy's artillery scatters again.",
                "[[Mini boss]] · khí cầu trinh sát · chỉ điểm cho pháo địch\n" +
                "Cách đánh: khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa; đòn lớn gọi một loạt pháo vào vùng có cảnh báo. Cao xạ và [[radar]].\n" +
                "Mạnh / yếu: chậm và to; chỉ phòng không và tiêm kích bắn tới.\n" +
                "Mẹo: phá radar là pháo binh địch lại bắn tản mát."),

            // ---------------------------------------------------------------- parts tips
            ["guide.parts.tip.moloch"] = ("Tip: flank it for the [[workshop doors]] at the back (armour 2): each one broken halves what it builds, both stop it; the [[tracks]] slow it.", "Mẹo: vòng ra sau đánh [[cửa xưởng]] (giáp cấp 2): phá một cửa là sinh xe giảm một nửa, phá cả hai là ngừng hẳn; phá [[cụm xích]] để làm chậm."),
            ["guide.parts.tip.daedalus"] = ("Tip: break the [[drop-pod bays]] (each one slows the drops; the mass drop falls as three pods with one gone) and the [[point-defence lasers]] before sending missiles.", "Mẹo: phá [[cửa thả khoang]] (mỗi cửa mất là thả chậm hơn; mất một cửa thì đòn đổ bộ lớn chỉ còn ba khoang) và [[tháp la-de phòng thủ]] trước khi dùng tên lửa."),
            ["guide.parts.tip.kronos"] = ("Tip: the four [[track units]] (armour 2) each slow it; the [[boom]] carries its sweep; the [[bucket wheel]] (armour 4) is what crushes.", "Mẹo: mỗi [[cụm xích]] (giáp cấp 2) bị phá là nó chậm lại; [[cần gầu]] mang đòn quét; [[bánh gầu]] (giáp cấp 4) là thứ nghiền."),
            ["guide.parts.tip.typhon"] = ("Tip: the [[launch doors]] carry its missiles (they show above the water during a warning); the [[sail]] aims its SAM; the [[sonar]] its fire control.", "Mẹo: [[cửa ống phóng]] mang tên lửa (lộ trên mặt nước lúc cảnh báo); [[tháp chỉ huy]] ngắm tên lửa phòng không; [[sô-na]] là hệ điều khiển hỏa lực."),
            ["guide.parts.tip.ixion"] = ("Tip: the rear [[steering wheel]] is armour 1; a [[big wheel]] broken during its charge warning throws it off its line.", "Mẹo: [[bánh lái sau]] giáp cấp 1; phá một [[bánh lớn]] lúc nó cảnh báo cú lao là cú lao bị chệch và dừng."),
            ["guide.parts.tip.caspian"] = ("Tip: break the [[missile launcher]] on its back to stop the volley; the nose [[engines]] slow its passes.", "Mẹo: phá [[bệ tên lửa]] trên lưng để chặn loạt tên lửa; phá [[cụm động cơ]] ở mũi để các lượt lao chậm lại."),
            ["guide.parts.tip.bastion_mk0"] = ("Tip: break the [[mortar]] first; the two turrets only reach close.", "Mẹo: phá [[khẩu cối]] trước; hai tháp pháo chỉ bắn gần."),
            ["guide.parts.tip.fenrir"] = ("Tip: each [[rocket box]] broken halves its rain; its flak is all it has against aircraft.", "Mẹo: mỗi [[hộp rốc-két]] bị phá là mưa rốc-két giảm một nửa; cao xạ là thứ duy nhất chống máy bay."),
            ["guide.parts.tip.scylla"] = ("Tip: break the [[missile cells]] for its cruise missiles and the [[CIWS]] before sending missiles.", "Mẹo: phá [[ống phóng tên lửa]] để chặn tên lửa hành trình, phá [[CIWS]] trước khi dùng tên lửa."),
            ["guide.parts.tip.locust"] = ("Tip: its [[drone bay]] is everything it has.", "Mẹo: [[khoang drone]] là tất cả những gì nó có."),
            ["guide.parts.tip.behemoth_mk2"] = ("Tip: the [[main gun]] is its punch; the [[protection system]] shoots down two missiles a volley.", "Mẹo: [[pháo chính]] là đòn mạnh nhất; [[hệ thống bảo vệ]] bắn hạ hai tên lửa mỗi loạt."),
            ["guide.parts.tip.icarus_mk0"] = ("Tip: the [[satellite uplink]] carries the rods, the [[pod bay]] the drops.", "Mẹo: [[ăng-ten liên kết]] mang thanh vonfram, [[khoang đổ bộ]] mang các đợt thả."),
            ["guide.parts.tip.argus"] = ("Tip: the [[radar]] directs the enemy's guns and carries its barrage call.", "Mẹo: [[radar]] chỉ điểm cho pháo địch và mang đòn gọi pháo."),

            // ---------------------------------------------------------------- new part kinds
            ["part.door"] = ("workshop door", "cửa xưởng"),
            ["part.tracks"] = ("track unit", "cụm xích"),
            ["part.bucketwheel"] = ("bucket wheel", "bánh gầu"),
            ["part.boom"] = ("boom", "cần gầu"),
            ["part.cab"] = ("control cab", "buồng điều khiển"),
            ["part.sail"] = ("sail", "tháp chỉ huy"),
            ["part.launchdoors"] = ("launch doors", "cửa ống phóng"),
            ["part.rudder"] = ("rudder", "bánh lái"),
            ["part.sonar"] = ("sonar", "sô-na"),
            ["part.wheel"] = ("big wheel", "bánh lớn"),
            ["part.steerwheel"] = ("steering wheel", "bánh lái sau"),
            ["part.wing"] = ("wing", "cánh"),
            ["part.casemate"] = ("casemate gun", "pháo lô cốt"),
            ["part.fx.stop.factory"] = ("its workshop builds less (nothing once both doors are broken)", "xưởng sinh ít xe hơn (ngừng hẳn khi cả hai cửa bị phá)"),
            ["part.fx.stop.crush"] = ("it crushes nothing in its way", "nó không còn nghiền được gì trên đường"),
            ["part.fx.stop.spotaura"] = ("the enemy's artillery scatters as usual again", "pháo binh địch lại bắn tản mát như thường"),
            ["radio.part.door"] = ("Command: one of {boss}'s workshop doors is down. It is building half as much!", "Chỉ huy: một cửa xưởng của {boss} đã bị phá. Nó chỉ sinh được một nửa số xe!"),
            ["radio.part.bucketwheel"] = ("Command: {boss}'s bucket wheel has stopped. It cannot crush anything now!", "Chỉ huy: bánh gầu của {boss} đã ngừng quay. Nó không nghiền được gì nữa!"),
            ["radio.part.boom"] = ("Command: {boss}'s boom is down: no more sweeps!", "Chỉ huy: cần gầu của {boss} đã gãy: hết đòn quét!"),
            ["radio.part.cab"] = ("Command: {boss}'s control cab is burning. It steers badly now.", "Chỉ huy: buồng điều khiển của {boss} đang cháy. Nó lái rất vụng."),
            ["radio.part.sail"] = ("Command: {boss}'s sail is wrecked: its SAM is firing blind.", "Chỉ huy: tháp chỉ huy của {boss} tan nát: tên lửa phòng không của nó bắn mù."),
            ["radio.part.launchdoors"] = ("Command: {boss}'s launch doors are jammed shut on one side!", "Chỉ huy: một cụm cửa ống phóng của {boss} đã kẹt cứng!"),
            ["radio.part.wheel"] = ("Command: {boss} has lost a wheel. It is going round in circles!", "Chỉ huy: {boss} đã mất một bánh. Nó đang quay vòng!"),
            ["radio.part.engines"] = ("Command: {boss}'s engines are burning. It is slowing down!", "Chỉ huy: cụm động cơ của {boss} đang cháy. Nó chậm lại rồi!"),
            ["radio.part.antiship"] = ("Command: {boss}'s missile launcher is gone. No more volleys!", "Chỉ huy: bệ tên lửa của {boss} đã bị phá. Hết loạt tên lửa!"),

            // ---------------------------------------------------------------- arrival lines (prompt 20 K: each boss speaks for its general)
            ["radio.brandt.bastion"] = ("Brandt: \"Bastion is rolling. Nothing has ever taken a fortress that walks.\"", "Brandt: \"Bastion lăn bánh. Chưa ai hạ nổi một pháo đài biết đi.\""),
            ["radio.brandt.bastion_mk0"] = ("Brandt: \"The prototype will do. Grind them down, slowly.\"", "Brandt: \"Bản nguyên mẫu là đủ. Nghiền chúng từ từ.\""),
            ["radio.varga.behemoth"] = ("Varga: \"Behemoth is on the field. Get out of its way or under it.\"", "Varga: \"Behemoth ra trận. Tránh đường, hoặc nằm dưới xích nó.\""),
            ["radio.varga.moloch"] = ("Varga: \"Moloch builds as it rolls. Every one you kill, I make two.\"", "Varga: \"Moloch vừa đi vừa đúc xe. Các người diệt một, ta làm ra hai.\""),
            ["radio.varga.inferno"] = ("Varga: \"Inferno, burn the road clean.\"", "Varga: \"Inferno, đốt sạch con đường.\""),
            ["radio.varga.behemoth_mk2"] = ("Varga: \"You broke one Behemoth. This one wears winter.\"", "Varga: \"Các người phá được một Behemoth. Con này khoác cả mùa đông.\""),
            ["radio.orlov.fortress"] = ("Orlov: \"Jötunn is moving. Winter walks with it.\"", "Orlov: \"Jötunn đang tiến. Mùa đông đi cùng nó.\""),
            ["radio.orlov.fenrir"] = ("Orlov: \"Fenrir, bite and run. Do not stay to be caught.\"", "Orlov: \"Fenrir, cắn rồi chạy. Đừng ở lại cho chúng tóm.\""),
            ["radio.orlov.supergun"] = ("Orlov: \"Gungnir has the range. One shell, one grave.\"", "Orlov: \"Gungnir đã có tầm. Một phát đạn, một nấm mồ.\""),
            ["radio.orlov.supergun.half"] = ("Orlov: \"Loaders, faster. Let the barrel glow.\"", "Orlov: \"Nạp đạn nhanh lên. Cho nòng đỏ rực lên.\""),
            ["radio.kessler.tempest"] = ("Kessler: \"Tempest, charge the rail. One line, one pass.\"", "Kessler: \"Tempest, nạp pháo điện từ. Một đường, một phát.\""),
            ["radio.kessler.juggernaut"] = ("Kessler: \"Juggernaut is on the line. Keep to the timetable.\"", "Kessler: \"Juggernaut đã lên tuyến. Chạy đúng giờ.\""),
            ["radio.kessler.scylla"] = ("Kessler: \"Scylla, close the shore. Let them see you coming.\"", "Kessler: \"Scylla, áp sát bờ. Cho chúng thấy ngươi đang tới.\""),
            ["radio.kessler.scylla.sunk"] = ("Kessler: \"Scylla is gone... note it in the log.\"", "Kessler: \"Scylla mất rồi... ghi vào nhật ký.\""),
            ["radio.sen.matriarch"] = ("Dr Venn: \"Matriarch, open the hives. Let the children play.\"", "Tiến sĩ Venn: \"Matriarch, mở tổ. Cho lũ con đi chơi.\""),
            ["radio.sen.hive"] = ("Dr Venn: \"The Hive is awake. Keep your aircraft home.\"", "Tiến sĩ Venn: \"Tổ ong đã thức. Giữ máy bay của các người ở nhà đi.\""),
            ["radio.sen.locust"] = ("Dr Venn: \"Locust, swarm. Numbers are my armour.\"", "Tiến sĩ Venn: \"Locust, xuất bầy. Số đông là lớp giáp của ta.\""),
            ["radio.hung.nemesis"] = ("{@lyhan}: \"Nemesis is on the rails. When it stops, the sky opens.\"", "{@lyhan}: \"Nemesis đã lên đường ray. Khi nó dừng, bầu trời sẽ mở.\""),
            ["radio.hung.kronos"] = ("{@lyhan}: \"Kronos eats mountains. Your base is a smaller meal.\"", "{@lyhan}: \"Kronos ăn cả núi. Căn cứ của các người chỉ là bữa nhẹ.\""),
            ["radio.hung.kronos.phase2"] = ("{@lyhan}: \"Full power to the tracks.\"", "{@lyhan}: \"Dồn hết công suất cho xích.\""),
            ["radio.hung.kronos.phase3"] = ("{@lyhan}: \"Spin the wheel up. Let the rock fly.\"", "{@lyhan}: \"Quay bánh gầu hết cỡ. Cho đá bay.\""),
            ["radio.hung.typhon"] = ("{@lyhan}: \"Typhon is under you, Colonel. You will not see it until it is too late.\"", "{@lyhan}: \"Typhon ở ngay dưới chân các người, đại tá. Thấy được nó thì đã muộn.\""),
            ["radio.hung.typhon.sunk"] = ("{@lyhan}: \"Typhon... flood the tubes. Let it take its secrets down.\"", "{@lyhan}: \"Typhon... cho nước tràn ống phóng. Để nó mang bí mật xuống đáy.\""),
            ["radio.hung.ixion"] = ("{@lyhan}: \"Ixion does not turn. Neither will I.\"", "{@lyhan}: \"Ixion không quay đầu. Ta cũng vậy.\""),
            ["radio.hung.caspian"] = ("{@lyhan}: \"Caspian, skim the coast. Low and fast.\"", "{@lyhan}: \"Caspian, lướt dọc bờ. Thấp và nhanh.\""),
            ["radio.hung.caspian.sunk"] = ("{@lyhan}: \"The sea monster is down. Recall the boats.\"", "{@lyhan}: \"Quái vật biển gục rồi. Gọi xuồng về.\""),
            ["radio.hung.borer"] = ("{@lyhan}: \"Tartarus is under the ridge. Listen to the ground.\"", "{@lyhan}: \"Tartarus đang dưới sườn núi. Hãy nghe mặt đất.\""),
            ["radio.hung.borer.half"] = ("{@lyhan}: \"Deeper, faster. Break them from below.\"", "{@lyhan}: \"Sâu hơn, nhanh hơn. Đập chúng từ bên dưới.\""),
            ["radio.quaden.harpy"] = ("Raven: \"Harpy, over the ridge. Hunt.\"", "Raven: \"Harpy, vượt qua sườn đồi. Săn đi.\""),
            ["radio.quaden.spectre"] = ("Raven: \"Spectre is circling. Nothing moves down there without my say.\"", "Raven: \"Spectre đang lượn vòng. Dưới đó không gì nhúc nhích nếu ta chưa cho.\""),
            ["radio.quaden.argus"] = ("Raven: \"Argus sees for the guns. Every shell will find you.\"", "Raven: \"Argus nhìn thay cho pháo. Viên đạn nào cũng sẽ tìm ra các người.\""),
            ["radio.quaden.airship.phase2"] = ("Raven: \"Bring the gun pods round. Wider sweeps.\"", "Raven: \"Quay các khoang pháo lại. Quét rộng hơn.\""),
            ["radio.aurel.daedalus"] = ("Aurel: \"Daedalus is in orbit. The sky will deliver my army.\"", "Aurel: \"Daedalus đã vào quỹ đạo. Bầu trời sẽ mang quân ta xuống.\""),
            ["radio.aurel.daedalus.descend"] = ("Aurel: \"Descending. Open the first bays.\"", "Aurel: \"Hạ độ cao. Mở các khoang đầu tiên.\""),
            ["radio.aurel.daedalus.phase2"] = ("Aurel: \"Faster drops. Do not let them breathe.\"", "Aurel: \"Thả nhanh hơn. Đừng để chúng kịp thở.\""),
            ["radio.aurel.daedalus.phase3"] = ("Aurel: \"All stop. Every bay open. Empty the ship.\"", "Aurel: \"Dừng hẳn. Mở mọi khoang. Thả hết quân.\""),
            ["radio.aurel.icarus_mk0"] = ("Aurel: \"You are looking at the future, Colonel. A prototype, but the future.\"", "Aurel: \"Các người đang nhìn thấy tương lai, đại tá. Một bản nguyên mẫu, nhưng là tương lai.\""),
            ["radio.aurel.icarus_mk0.phase2"] = ("Aurel: \"Test complete. Bring it home in one piece.\"", "Aurel: \"Thử nghiệm xong. Đưa nó về nguyên vẹn.\""),

            // ---------------------------------------------------------------- big attacks
            ["bigattack.moloch_factory_dump"] = ("Workshop Dump", "Xả xưởng"),
            ["bigattack.moloch_factory_dump.cancelled"] = ("Workshop dump cut short", "Đã chặn xả xưởng"),
            ["radio.bigattack.moloch_factory_dump"] = ("Varga: \"Open every door. Send them all.\"", "Varga: \"Mở hết các cửa. Thả tất cả ra.\""),
            ["guide.bigattack.moloch_factory_dump.how"] = ("Every door opens: six vehicles at once, with eight 152 mm high-explosive shells (300 each, 6 m) on your nearest group.", "Mọi cửa cùng mở: sáu xe một lúc, kèm tám phát pháo 152 mm nổ mạnh (mỗi phát 300, bán kính 6 m) vào cụm quân gần nhất."),
            ["guide.bigattack.moloch_factory_dump.dodge"] = ("Move your group off the marked area; be ready for six more vehicles.", "Đưa cụm quân ra khỏi vùng đánh dấu; sẵn sàng đón thêm sáu xe."),
            ["guide.bigattack.moloch_factory_dump.stop"] = ("Break a workshop door during the warning: only half come out; both broken, only the shells.", "Phá một cửa xưởng lúc cảnh báo: chỉ ra một nửa; phá cả hai thì chỉ còn loạt pháo."),
            ["bigattack.daedalus_mass_drop"] = ("Orbital Mass Drop", "Đổ bộ ồ ạt từ quỹ đạo"),
            ["bigattack.daedalus_mass_drop.cancelled"] = ("Mass drop called off", "Đã chặn đợt đổ bộ"),
            ["radio.bigattack.daedalus_mass_drop"] = ("Aurel: \"All pods on that group. Land on them.\"", "Aurel: \"Mọi khoang vào cụm đó. Đáp thẳng lên đầu chúng.\""),
            ["guide.bigattack.daedalus_mass_drop.how"] = ("Six pods fall together on one group: 400 kinetic each (high penetration, 5 m) on landing, then each lets a vehicle out.", "Sáu khoang cùng rơi vào một cụm quân: mỗi khoang chạm đất gây 400 động năng (xuyên cao, bán kính 5 m) rồi thả một xe."),
            ["guide.bigattack.daedalus_mass_drop.dodge"] = ("Scatter the marked group; heavy armour does not save it.", "Tản cụm quân bị đánh dấu ra; giáp dày cũng không cứu được."),
            ["guide.bigattack.daedalus_mass_drop.stop"] = ("Break a pod bay during the warning: only three pods fall.", "Phá một cửa thả khoang lúc cảnh báo: chỉ còn ba khoang rơi."),
            ["bigattack.kronos_bucket_sweep"] = ("Bucket Sweep", "Quét gầu"),
            ["bigattack.kronos_bucket_sweep.cancelled"] = ("Bucket sweep stopped", "Đã chặn đòn quét gầu"),
            ["radio.bigattack.kronos_bucket_sweep"] = ("Command: Kronos is swinging its wheel. Clear its front!", "Chỉ huy: Kronos đang vung bánh gầu. Tránh khỏi phía trước nó!"),
            ["guide.bigattack.kronos_bucket_sweep.how"] = ("The wheel sweeps a 120° arc 25 m in front of it: about 1 200 kinetic (high penetration) to every unit, double on buildings and towers.", "Bánh gầu quét cung 120° dài 25 m phía trước: khoảng 1.200 động năng (xuyên cao) mỗi đơn vị, gấp đôi lên công trình và tháp."),
            ["guide.bigattack.kronos_bucket_sweep.dodge"] = ("Get out of the marked arc in front of it; attack it from the sides and rear.", "Ra khỏi cung đánh dấu phía trước; đánh vào hông và sau."),
            ["guide.bigattack.kronos_bucket_sweep.stop"] = ("Break the boom (during the warning or before).", "Phá cần gầu (lúc cảnh báo hoặc trước đó)."),
            ["bigattack.typhon_underwater_launch"] = ("Underwater Launch", "Phóng tên lửa từ dưới nước"),
            ["bigattack.typhon_underwater_launch.cancelled"] = ("Launch aborted", "Đã chặn đợt phóng"),
            ["radio.bigattack.typhon_underwater_launch"] = ("{@lyhan}: \"Launch depth. Three for their headquarters.\"", "{@lyhan}: \"Lên độ sâu phóng. Ba quả cho sở chỉ huy của chúng.\""),
            ["guide.bigattack.typhon_underwater_launch.how"] = ("Three missiles at your base: about 500 high explosive each (8 m), double on buildings; a clock shows their flight after the warning.", "Ba tên lửa vào căn cứ ta: mỗi quả khoảng 500 nổ mạnh (bán kính 8 m), gấp đôi lên công trình; sau cảnh báo có đồng hồ bay."),
            ["guide.bigattack.typhon_underwater_launch.dodge"] = ("Move units off the marked points; towers cannot move, so cover them.", "Đưa quân ra khỏi các điểm đánh dấu; tháp không di chuyển được nên hãy che chắn."),
            ["guide.bigattack.typhon_underwater_launch.stop"] = ("Break the launch doors during the warning (they show above the water), or shoot the missiles down (250 health each).", "Phá cửa ống phóng lúc cảnh báo (cửa lộ trên mặt nước), hoặc bắn hạ tên lửa (mỗi quả 250 máu)."),
            ["bigattack.ixion_crush_charge"] = ("Crushing Charge", "Lao nghiền"),
            ["bigattack.ixion_crush_charge.cancelled"] = ("Charge thrown off its line", "Cú lao đã bị chệch"),
            ["radio.bigattack.ixion_crush_charge"] = ("Command: Ixion is lining up a charge. Off the marked line!", "Chỉ huy: Ixion đang lấy đà lao. Ra khỏi đường đánh dấu!"),
            ["guide.bigattack.ixion_crush_charge.how"] = ("It charges straight down a marked 80 m line: about 900 to every unit on it, stunned for 2 s.", "Nó lao thẳng theo đường đánh dấu dài 80 m: khoảng 900 mỗi đơn vị trên đường, choáng 2 giây."),
            ["guide.bigattack.ixion_crush_charge.dodge"] = ("Step sideways off the line: it cannot turn.", "Bước ngang ra khỏi đường: nó không xoay kịp."),
            ["guide.bigattack.ixion_crush_charge.stop"] = ("Break a big wheel during the warning: the charge slews off and stops.", "Phá một bánh lớn lúc cảnh báo: cú lao bị chệch và dừng."),
            ["bigattack.caspian_antiship_volley"] = ("Anti-Ship Volley", "Loạt tên lửa chống hạm"),
            ["bigattack.caspian_antiship_volley.cancelled"] = ("Volley cancelled", "Đã chặn loạt tên lửa"),
            ["radio.bigattack.caspian_antiship_volley"] = ("{@lyhan}: \"Four for the shore. Fire.\"", "{@lyhan}: \"Bốn quả vào bờ. Bắn.\""),
            ["guide.bigattack.caspian_antiship_volley.how"] = ("Four anti-ship missiles at the shore and your base: about 500 high explosive each (high penetration).", "Bốn tên lửa chống hạm vào bờ và căn cứ ta: mỗi quả khoảng 500 nổ mạnh (xuyên cao)."),
            ["guide.bigattack.caspian_antiship_volley.dodge"] = ("Move units off the marked points.", "Đưa quân ra khỏi các điểm đánh dấu."),
            ["guide.bigattack.caspian_antiship_volley.stop"] = ("Break the missile launcher, or shoot the missiles down (220 health each).", "Phá bệ tên lửa, hoặc bắn hạ tên lửa (mỗi quả 220 máu)."),
            ["bigattack.bastion_mk0_mortar"] = ("Mortar Barrage", "Pháo cối tổng lực"),
            ["bigattack.bastion_mk0_mortar.cancelled"] = ("Mortar barrage cancelled", "Đã hủy pháo cối tổng lực"),
            ["radio.bigattack.bastion_mk0_mortar"] = ("Command: the prototype's mortar is walking three bombs at us. Watch the marks!", "Chỉ huy: cối của bản nguyên mẫu đang bắn ba quả tiến dần về phía ta. Để ý các điểm đánh dấu!"),
            ["guide.bigattack.bastion_mk0_mortar.how"] = ("Three 240 mm bombs walking down a line; double on buildings and towers.", "Ba quả cối 240 mm tiến dần theo một đường; gấp đôi lên công trình và tháp."),
            ["guide.bigattack.bastion_mk0_mortar.dodge"] = ("Each point has its own countdown: step aside from the line.", "Mỗi điểm có đếm ngược riêng: bước ngang ra khỏi đường."),
            ["guide.bigattack.bastion_mk0_mortar.stop"] = ("Break the mortar during the warning.", "Phá khẩu cối lúc cảnh báo."),
            ["bigattack.fenrir_rocket_rain"] = ("Rocket Rain", "Mưa rốc-két"),
            ["bigattack.fenrir_rocket_rain.cancelled"] = ("Rocket rain cancelled", "Đã chặn mưa rốc-két"),
            ["radio.bigattack.fenrir_rocket_rain"] = ("Orlov: \"Sixteen, then home.\"", "Orlov: \"Mười sáu quả, rồi về.\""),
            ["guide.bigattack.fenrir_rocket_rain.how"] = ("Sixteen 122 mm rockets over a circle round your group, eight from each box.", "Mười sáu rốc-két 122 mm rải khắp vùng tròn quanh cụm quân, mỗi hộp tám quả."),
            ["guide.bigattack.fenrir_rocket_rain.dodge"] = ("Leave the marked circle.", "Ra khỏi vùng tròn đánh dấu."),
            ["guide.bigattack.fenrir_rocket_rain.stop"] = ("Break a rocket box during the warning: half the rain; both, none.", "Phá một hộp rốc-két lúc cảnh báo: còn một nửa; phá cả hai thì hết."),
            ["bigattack.scylla_cruise"] = ("Cruise Missiles", "Tên lửa hành trình"),
            ["bigattack.scylla_cruise.cancelled"] = ("Cruise missiles cancelled", "Đã chặn tên lửa hành trình"),
            ["radio.bigattack.scylla_cruise"] = ("Kessler: \"Three from Scylla. Their base.\"", "Kessler: \"Ba quả từ Scylla. Căn cứ của chúng.\""),
            ["guide.bigattack.scylla_cruise.how"] = ("Three cruise missiles at your HQ, towers and groups in the base, twice as hard on buildings.", "Ba tên lửa hành trình vào HQ, tháp và cụm quân trong căn cứ, gấp đôi lên công trình."),
            ["guide.bigattack.scylla_cruise.dodge"] = ("Move units off the marked points; cover the towers.", "Đưa quân ra khỏi điểm đánh dấu; che chắn các tháp."),
            ["guide.bigattack.scylla_cruise.stop"] = ("Break the missile cells during the warning, or shoot the missiles down.", "Phá ống phóng lúc cảnh báo, hoặc bắn hạ tên lửa."),
            ["bigattack.locust_swarm"] = ("Drone Swarm", "Bầy drone"),
            ["bigattack.locust_swarm.cancelled"] = ("Drone swarm cancelled", "Đã chặn bầy drone"),
            ["radio.bigattack.locust_swarm"] = ("Dr Venn: \"Ten more. Find the heavy ones.\"", "Tiến sĩ Venn: \"Thêm mười con. Tìm lũ xe nặng.\""),
            ["guide.bigattack.locust_swarm.how"] = ("Ten drones dive on the heaviest vehicles of a group, from the roof.", "Mười drone bổ nhào vào các xe nặng nhất của một cụm, đánh từ nóc."),
            ["guide.bigattack.locust_swarm.dodge"] = ("Keep anti-air, C-RAM or jammers with your heavy tanks.", "Để phòng không, C-RAM hoặc xe gây nhiễu đi cùng xe tăng nặng."),
            ["guide.bigattack.locust_swarm.stop"] = ("Break the drone bay during the warning, or shoot the drones down.", "Phá khoang drone lúc cảnh báo, hoặc bắn hạ drone."),
            ["bigattack.behemoth_mk2_barrage"] = ("Main Gun Barrage", "Loạt pháo chính"),
            ["bigattack.behemoth_mk2_barrage.cancelled"] = ("Barrage cancelled", "Đã chặn loạt pháo"),
            ["radio.bigattack.behemoth_mk2_barrage"] = ("Varga: \"Four rounds. Make them count.\"", "Varga: \"Bốn phát. Phát nào cũng phải trúng.\""),
            ["guide.bigattack.behemoth_mk2_barrage.how"] = ("Four heavy rounds from the main gun over your group.", "Bốn phát pháo nặng từ pháo chính vào cụm quân."),
            ["guide.bigattack.behemoth_mk2_barrage.dodge"] = ("Leave the marked circle.", "Ra khỏi vùng tròn đánh dấu."),
            ["guide.bigattack.behemoth_mk2_barrage.stop"] = ("Break the main gun during the warning.", "Phá pháo chính lúc cảnh báo."),
            ["bigattack.icarus_mk0_rods"] = ("Tungsten Rods", "Mưa thanh vonfram"),
            ["bigattack.icarus_mk0_rods.cancelled"] = ("Rods called off", "Đã chặn thanh vonfram"),
            ["radio.bigattack.icarus_mk0_rods"] = ("Aurel: \"Three rods. A demonstration.\"", "Aurel: \"Ba thanh. Coi như trình diễn.\""),
            ["guide.bigattack.icarus_mk0_rods.how"] = ("Three tungsten rods, one on each of your densest groups (the heaviest armour first), from the roof.", "Ba thanh vonfram, mỗi thanh vào một cụm quân đông nhất (giáp dày nhất trước), đánh từ nóc."),
            ["guide.bigattack.icarus_mk0_rods.dodge"] = ("Get out of the rings.", "Ra khỏi các vòng đánh dấu."),
            ["guide.bigattack.icarus_mk0_rods.stop"] = ("Break the satellite uplink during the warning.", "Phá ăng-ten liên kết vệ tinh lúc cảnh báo."),
            ["bigattack.argus_fire_call"] = ("Fire Call", "Gọi pháo"),
            ["bigattack.argus_fire_call.cancelled"] = ("Fire call cut off", "Đã chặn đòn gọi pháo"),
            ["radio.bigattack.argus_fire_call"] = ("Raven: \"Argus to the batteries: grid marked. Fire for effect.\"", "Raven: \"Argus gọi các khẩu đội: đã đánh dấu tọa độ. Bắn hiệu quả.\""),
            ["guide.bigattack.argus_fire_call.how"] = ("It calls the enemy's artillery on a marked area: ten shells over 4 s.", "Nó gọi pháo binh địch vào vùng đánh dấu: mười quả trong 4 giây."),
            ["guide.bigattack.argus_fire_call.dodge"] = ("Leave the marked circle.", "Ra khỏi vùng tròn đánh dấu."),
            ["guide.bigattack.argus_fire_call.stop"] = ("Break the radar during the warning.", "Phá radar lúc cảnh báo."),

            // ---------------------------------------------------------------- prompt 20 pass 3: Boss Hunt (N)
            ["hunt.full"] = ("Full Boss Hunt", "Săn trùm toàn tập"),
            ["hunt.full.kicker"] = ("FULL BOSS HUNT", "SĂN TRÙM TOÀN TẬP"),
            ["hunt.full.sub"] = ("Every boss of the story, in order", "Mọi boss của cốt truyện, theo thứ tự"),
            ["hunt.fullSub"] = ("{count|# boss|# bosses} in story order", "{count} boss theo cốt truyện"),
            ["hunt.full.rules"] = ("All {count} main and mini bosses of the chapters open, in story order. A checkpoint after every boss: play it over as many sittings as you like. After each main boss, pick a combat support. Ranked by total time.",
                "Toàn bộ {count} boss chủ lực và mini boss của các chương đang mở, theo đúng thứ tự cốt truyện. Có điểm hồi sinh sau mỗi boss: chơi dần qua bao nhiêu lần cũng được. Sau mỗi boss chủ lực, chọn một hỗ trợ tác chiến. Xếp hạng theo tổng thời gian."),
            ["hunt.full.locked"] = ("Opens once chapter {chapter}'s operation is won.", "Mở khi thắng chiến dịch lớn của chương {chapter}."),
            ["hunt.full.reward"] = ("First clear: {coins|# coin|# coins} and a legendary crate", "Lần đầu hoàn thành: {coins} xu và một hòm huyền thoại"),
            ["hunt.weekly.rules"] = ("{count|# boss|# bosses} this week: {minis|# mini boss|# mini bosses} leading to {mains|# main boss|# main bosses}, each stronger than the last. A 20 s rest between bosses repairs part of your army; after each main boss, pick one of three combat supports and keep a checkpoint. {minutes|# minute|# minutes} on the clock.",
                "{count} boss tuần này: {minis} mini boss dẫn tới {mains} boss chủ lực, boss sau mạnh hơn boss trước. Nghỉ 20 giây giữa các boss, quân được sửa một phần; sau mỗi boss chủ lực, chọn một trong ba hỗ trợ tác chiến và lưu điểm hồi sinh. Đồng hồ {minutes} phút."),
            ["hunt.weekly.reward"] = ("First clear this week: {coins|# coin|# coins}", "Lần đầu hoàn thành trong tuần: {coins} xu"),
            ["hunt.roster"] = ("This week's bosses", "Boss tuần này"),
            ["hunt.fullRoster"] = ("In story order", "Theo thứ tự cốt truyện"),
            ["hunt.restTitle"] = ("Rest · army repaired {percent}%", "Nghỉ · quân được sửa {percent}%"),
            ["hunt.next"] = ("Next: {card}", "Tiếp theo: {card}"),
            ["hunt.held"] = ("Supports: {supports}", "Hỗ trợ: {supports}"),
            ["hunt.pickTitle"] = ("Choose a combat support", "Chọn hỗ trợ tác chiến"),
            ["hunt.pick"] = ("Take it", "Chọn"),
            ["hunt.pickAuto"] = ("The first is taken in {seconds} s. It lasts for the rest of the run.", "Sau {seconds} giây sẽ tự chọn cái đầu tiên. Hỗ trợ giữ tới hết lượt."),
            ["hunt.checkpointToast"] = ("Checkpoint kept", "Đã lưu điểm hồi sinh"),
            ["hunt.checkpoint"] = ("Checkpoint: {defeated} of {count|# boss|# bosses} down", "Điểm hồi sinh: đã hạ {defeated}/{count} boss"),
            ["hunt.continue"] = ("Continue", "Tiếp tục"),
            ["hunt.restart"] = ("Start over", "Chơi lại từ đầu"),
            ["hunt.best"] = ("Best total times", "Tổng thời gian tốt nhất"),
            ["hunt.noTimes"] = ("No clear yet.", "Chưa hoàn thành lần nào."),
            ["hunt.time"] = ("Total time", "Tổng thời gian"),
            ["hunt.newBest"] = ("New best time", "Kỷ lục mới"),
            ["hunt.firstClear"] = ("First clear", "Lần đầu hoàn thành"),
            ["hunt.supportsTitle"] = ("Combat supports", "Hỗ trợ tác chiến"),
            ["hunt.support.hull"] = ("Reinforced Hulls", "Gia cố thân xe"),
            ["hunt.support.hull.info"] = ("Your army's health +15%, vehicles landed later too.", "Máu toàn quân +15%, cả xe tới sau."),
            ["hunt.support.gunnery"] = ("Gunnery Drills", "Huấn luyện pháo thủ"),
            ["hunt.support.gunnery.info"] = ("Your army's damage +10%.", "Sát thương toàn quân +10%."),
            ["hunt.support.loaders"] = ("Fast Loaders", "Nạp đạn nhanh"),
            ["hunt.support.loaders.info"] = ("Your army fires 12% faster.", "Toàn quân bắn nhanh hơn 12%."),
            ["hunt.support.engines"] = ("Tuned Engines", "Tinh chỉnh động cơ"),
            ["hunt.support.engines.info"] = ("Your army drives 12% faster.", "Toàn quân chạy nhanh hơn 12%."),
            ["hunt.support.regen"] = ("Field Repairs", "Sửa chữa dã chiến"),
            ["hunt.support.regen.info"] = ("Out of fire, every vehicle mends 1% of its health a second.", "Khi không trúng đạn, mỗi xe tự hồi 1% máu mỗi giây."),
            ["hunt.support.rapid"] = ("Rapid Tasking", "Điều phối nhanh"),
            ["hunt.support.rapid.info"] = ("Support card cooldowns 25% shorter.", "Hồi chiêu thẻ hỗ trợ ngắn hơn 25%."),
            ["hunt.support.logistics"] = ("Supply Convoy", "Đoàn tiếp tế"),
            ["hunt.support.logistics.info"] = ("CP income +20%.", "Thu nhập CP +20%."),
            ["hunt.support.warchest"] = ("War Chest", "Quỹ chiến tranh"),
            ["hunt.support.warchest.info"] = ("35 CP now.", "Nhận ngay 35 CP."),
            ["hunt.support.supply"] = ("Extra Crews", "Thêm kíp lái"),
            ["hunt.support.supply.info"] = ("Army cap +6.", "Giới hạn quân +6."),
            ["hunt.support.workshop"] = ("Mobile Workshop", "Xưởng lưu động"),
            ["hunt.support.workshop.info"] = ("Rests repair twice as much.", "Giờ nghỉ sửa quân gấp đôi."),
            ["hunt.support.bounty"] = ("Bounty Contracts", "Hợp đồng săn thưởng"),
            ["hunt.support.bounty.info"] = ("CP bounties for bosses +50%.", "Tiền thưởng CP khi hạ boss +50%."),
            ["hunt.support.airdrop"] = ("Free Reinforcements", "Tiếp viện miễn phí"),
            ["hunt.support.airdrop.info"] = ("Three of your deck's dearest vehicles land now, free.", "Ba xe đắt nhất trong bộ bài được thả xuống ngay, miễn phí."),

            // ---------------------------------------------------------------- prompt 20 pass 3: dossier and Guide (O.3, O.5)
            ["guide.boss.general"] = ("General {general}", "Tướng {general}"),
            ["guide.boss.variantOf"] = ("Variant of {unit}", "Biến thể của {unit}"),
            ["guide.boss.variants"] = ("Its variants", "Các biến thể"),
            ["guide.boss.open"] = ("Guide", "Hướng dẫn"),
            ["guide.boss.chapters"] = ("Fought in chapter {chapter}", "Gặp ở chương {chapter}"),
            ["dossier.maps"] = ("Battlefields", "Chiến trường"),
            ["guide.maps.open"] = ("Battlefields", "Chiến trường"),
            ["guide.map.chapters"] = ("Campaign: chapter {chapter}", "Chiến dịch: chương {chapter}"),
            ["guide.map.skirmish"] = ("Skirmish only", "Chỉ ở giao tranh"),
            ["campaign.minis"] = ("{count|# mini boss|# mini bosses}", "{count} mini boss"),
        };
    }
}
