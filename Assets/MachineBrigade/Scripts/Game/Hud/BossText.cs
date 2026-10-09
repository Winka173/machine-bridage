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
            ["unit.typhon"] = ("Typhon · Missile Submarine", "Typhon · Tàu ngầm tên lửa"),
            ["unit.ixion"] = ("Ixion · Armoured Mine Truck", "Ixion · Xe tải mỏ bọc thép"),
            ["unit.bastion_mk0"] = ("Bastion Mk.0 · Prototype Fortress", "Bastion Mk.0 · Pháo đài nguyên mẫu"),
            ["unit.fenrir"] = ("Fenrir · Vanguard", "Fenrir · Xe tiên phong"),
            ["unit.scylla"] = ("Scylla · Destroyer", "Scylla · Tàu khu trục"),
            ["unit.locust"] = ("Locust · Drone Tender", "Locust · Tàu con drone"),
            ["unit.roc_gunship"] = ("Roc Arsenal · Combat Airship", "Roc Arsenal · Khí cầu chiến đấu"),
            ["unit.daedalus_assault"] = ("Daedalus Assault · Assault Lander", "Daedalus Assault · Tàu đổ bộ xung kích"),
            ["unit.icarus_interceptor"] = ("Icarus Sentinel · Interceptor Ship", "Icarus Sentinel · Phi thuyền đánh chặn"),
            ["unit.matriarch_flak"] = ("Matriarch Wasp · Flak Drone Ship", "Matriarch Wasp · Tàu phòng không drone"),
            ["unit.jotunn_artillery"] = ("Jötunn Mortar · Mortar Fortress", "Jötunn Mortar · Pháo đài bắn cầu"),
            ["unit.bastion_aa"] = ("Bastion Flak · Anti-Air Fortress", "Bastion Flak · Pháo đài phòng không"),
            ["unit.behemoth_mk2"] = ("Behemoth Mk.II · Upgraded Behemoth", "Behemoth Mk.II · Behemoth nâng cấp"),
            ["unit.icarus_mk0"] = ("Icarus Mk.0 · Prototype Spacecraft", "Icarus Mk.0 · Phi thuyền nguyên mẫu"),
            ["unit.argus"] = ("Argus · Scout Airship", "Argus · Khí cầu trinh sát"),
            ["short.moloch"] = ("Moloch", "Moloch"),
            ["short.daedalus"] = ("Daedalus", "Daedalus"),
            ["short.typhon"] = ("Typhon", "Typhon"),
            ["short.ixion"] = ("Ixion", "Ixion"),
            ["short.bastion_mk0"] = ("Bastion Mk.0", "Bastion Mk.0"),
            ["short.fenrir"] = ("Fenrir", "Fenrir"),
            ["short.scylla"] = ("Scylla", "Scylla"),
            ["short.locust"] = ("Locust", "Locust"),
            ["short.roc_gunship"] = ("Roc Arsenal", "Roc Arsenal"),
            ["short.daedalus_assault"] = ("Daedalus Assault", "Daedalus Assault"),
            ["short.icarus_interceptor"] = ("Icarus Sentinel", "Icarus Sentinel"),
            ["short.matriarch_flak"] = ("Matriarch Wasp", "Matriarch Wasp"),
            ["short.jotunn_artillery"] = ("Jötunn Mortar", "Jötunn Mortar"),
            ["short.bastion_aa"] = ("Bastion Flak", "Bastion Flak"),
            ["short.behemoth_mk2"] = ("Behemoth Mk.II", "Behemoth Mk.II"),
            ["short.icarus_mk0"] = ("Icarus Mk.0", "Icarus Mk.0"),
            ["short.argus"] = ("Argus", "Argus"),

            // ---------------------------------------------------------------- role notes
            ["note.moloch"] = ("Varga's tracked factory: four 120 mm turrets, flak, and two workshop doors that keep sending out vehicles. Front armour 4, sides 3, rear 2.", "Nhà máy bánh xích của Varga: bốn tháp pháo 120 mm, cao xạ và hai cửa xưởng liên tục thả xe ra. Giáp trước cấp 4, hông 3, sau 2."),
            ["note.daedalus"] = ("Aurel's troop lander: drops pods without pause, two targeting lasers, twin 57 mm and 25 mm rotary guns under the hull, point-defence lasers. Upper hull 3, belly 2.", "Tàu đổ bộ của Aurel: thả khoang đổ bộ liên tục, hai la-de ngắm bắn, pháo đôi 57 mm và pháo nòng xoay 25 mm dưới bụng, tháp la-de phòng thủ. Thân trên cấp 3, bụng 2."),
            ["note.typhon"] = ("A missile submarine: out of reach while submerged, surfaces on a schedule; launches missiles at your base from under water.", "Tàu ngầm tên lửa: lặn thì không bắn tới được, nổi lên theo lịch; phóng tên lửa vào căn cứ ta từ dưới nước."),
            ["note.ixion"] = ("An armoured BelAZ-75710 mine truck: a 125 mm turret, a crushing charge about every 45 seconds, mines dropped behind it when it turns; it turns very slowly.", "Xe tải mỏ BelAZ-75710 bọc thép: tháp pháo 125 mm, cứ khoảng 45 giây lại lao nghiền, rải mìn phía sau khi rẽ; xoay rất chậm."),
            ["note.bastion_mk0"] = ("The first Bastion: a mortar and two 40 mm guns on tracks, crawling towards your base.", "Bastion đầu tiên: một khẩu cối và hai pháo 40 mm trên xích, bò dần về căn cứ ta."),
            ["note.fenrir"] = ("Orlov's fast raider: two rocket boxes and flak; it dashes in, fires and pulls back.", "Xe đột kích nhanh của Orlov: hai hộp rốc-két và cao xạ; lao vào bắn rồi rút."),
            ["note.scylla"] = ("Kessler's destroyer on the near-shore lane: one main turret, missile cells, a CIWS. Tank guns reach it from the piers.", "Tàu khu trục của Kessler trên tuyến gần bờ: một tháp pháo chính, ống phóng tên lửa, CIWS. Pháo xe tăng bắn tới từ đầu cầu tàu."),
            ["note.locust"] = ("A thin-skinned drone tender: launches drones without pause. Bring anti-air.", "Tàu con drone vỏ mỏng: thả drone liên tục. Mang phòng không theo."),
            ["note.roc_gunship"] = ("A gunship cut from the Roc's hull: heavy twin guns and flak, no bombs and no drones.", "Khinh khí cầu chiến đấu cắt từ thân Roc: pháo đôi hạng nặng và cao xạ, không bom, không drone."),
            ["note.daedalus_assault"] = ("A light assault lander: close guns, point-defence lasers and one slow drop-pod bay.", "Tàu đổ bộ xung kích nhẹ: pháo cận chiến, laser phòng thủ điểm và một khoang thả xe chậm."),
            ["note.icarus_interceptor"] = ("A fast interceptor with laser towers and anti-air missile pods; it hunts aircraft first.", "Phi thuyền đánh chặn nhanh: tháp laser và tên lửa phòng không, ưu tiên săn máy bay."),
            ["note.matriarch_flak"] = ("A drone tender armed for the air: flak guns, CIWS and a few small drones.", "Tàu mang drone thiên về phòng không: cao xạ, CIWS và vài drone nhỏ."),
            ["note.jotunn_artillery"] = ("A mobile fortress turned to mortars: it lobs shells over cover; close in under its arc.", "Pháo đài di động chuyên cối: bắn vòng qua vật cản; áp sát để tránh cung đạn."),
            ["note.bastion_aa"] = ("A fortress thick with flak and missiles: deadly to aircraft, thin against tanks.", "Pháo đài dày cao xạ và tên lửa: chết chóc với máy bay, mỏng với xe tăng."),
            ["note.behemoth_mk2"] = ("Varga's upgraded Behemoth under ice-coated armour (front 4): main gun, two flak guns, a protection system.", "Behemoth nâng cấp của Varga, giáp phủ băng (trước cấp 4): pháo chính, hai cao xạ, hệ thống bảo vệ chủ động."),
            ["note.icarus_mk0"] = ("Aurel's prototype spacecraft: high and low on a fixed schedule, never in orbit; a laser turret, two 40 mm test guns under the hull, a pod bay and a point-defence laser.", "Phi thuyền nguyên mẫu của Aurel: đổi tầng cao và thấp theo lịch cố định, không lên quỹ đạo; tháp la-de, hai pháo thử 40 mm dưới bụng, khoang đổ bộ và la-de phòng thủ điểm."),
            ["note.argus"] = ("A scout airship: while it lives the enemy's artillery falls far tighter. Flak, rockets and bombs.", "Khí cầu trinh sát: khi nó còn, pháo binh địch bắn chính xác hơn nhiều. Cao xạ, rocket và bom."),

            // ---------------------------------------------------------------- Guide cards
            ["guide.moloch"] = (
                "[[Boss]] · mobile factory · builds an army as it comes\n" +
                "How it fights: crawls down the mission's road; its two [[workshop doors]] send out 1-2 vehicles every 20 s (light tanks and IFVs, battle tanks from phase 2), one more each minute, never more than six alive. Four 120 mm turrets, flak and two ZU-23 on the roof cover it.\n" +
                "Strong / weak: front armour [[4]], sides 3, rear [[2]]: the doors are at the back, and so is its weak armour. Broken tracks slow it.\n" +
                "Tip: flank it and break both doors first: it stops building, and its super weapon is only the shells.",
                "[[Boss]] · nhà máy di động · vừa đi vừa sinh quân\n" +
                "Cách đánh: bò chậm theo đường của nhiệm vụ; hai [[cửa xưởng]] cứ 20 giây thả 1–2 xe (xe tăng nhẹ và xe bộ binh, từ pha 2 thêm tăng chủ lực), mỗi phút thêm một xe mỗi lượt, tối đa sáu xe còn sống. Bốn tháp pháo 120 mm, cao xạ và hai ZU-23 trên nóc che chắn.\n" +
                "Mạnh / yếu: giáp trước cấp [[4]], hông 3, sau [[2]]: cửa xưởng ở phía sau, giáp mỏng cũng ở đó. Phá cụm xích thì nó chậm lại.\n" +
                "Mẹo: vòng ra sau, phá cả hai cửa trước: nó ngừng sinh xe, siêu vũ khí chỉ còn loạt pháo."),
            ["guide.daedalus"] = (
                "[[Boss]] · orbital lander · a rain of drop pods\n" +
                "How it fights: about 10 s in orbit (out of reach), then high and low on a fixed schedule, never back to orbit. Its three [[pod bays]] drop pods of 1-2 vehicles without pause (at most eight alive), each pod a target as it falls. In phase 3 it stops low with every bay open. Two targeting lasers, two twin 57 mm turrets and two 25 mm rotary guns fire down from under it.\n" +
                "Strong / weak: its own guns are weaker than Icarus's; upper hull [[3]], belly [[2]]. Point-defence lasers take missiles aimed at it.\n" +
                "Tip: shoot the pods down and break the bays: each one lost slows the drops, and the mass drop falls short.",
                "[[Boss]] · tàu đổ bộ quỹ đạo · mưa khoang đổ bộ\n" +
                "Cách đánh: khoảng 10 giây trên quỹ đạo (không bắn tới được), sau đó đổi tầng cao và thấp theo lịch cố định, không lên lại quỹ đạo. Ba [[cửa thả khoang]] thả liên tục khoang chở 1–2 xe (tối đa tám xe còn sống); khoang đang rơi bắn hạ được. Pha 3 nó dừng hẳn ở tầng thấp, mở toàn bộ khoang. Hai la-de ngắm bắn, hai tháp pháo đôi 57 mm và hai pháo nòng xoay 25 mm bắn xuống từ dưới bụng.\n" +
                "Mạnh / yếu: tự nó bắn yếu hơn Icarus; thân trên cấp [[3]], bụng [[2]]. Tháp la-de phòng thủ chặn tên lửa bắn vào nó.\n" +
                "Mẹo: bắn hạ khoang đang rơi và phá cửa thả: mỗi cửa mất là thả chậm hơn, đòn đổ bộ lớn cũng hụt đi."),
            ["guide.typhon"] = (
                "[[Boss]] · missile submarine · strikes from under the sea\n" +
                "How it fights: submerged (out of reach) and surfaced (a target on the water) on each phase's schedule, coming up somewhere else each time; bubbles mark the spot first. Surfaced, it fires a short-range cruise missile every 12 s and guards itself with a SAM. Phase 3 it stays up and adds a 100 mm deck gun.\n" +
                "Strong / weak: hull armour [[4]], sail and deck [[2]]: artillery, bombs and top attacks hit the deck.\n" +
                "Tip: park artillery and aircraft for the bubbles; break the [[launch doors]] during a warning (they open above the water) or shoot the missiles down.",
                "[[Boss]] · tàu ngầm tên lửa · đánh từ dưới biển\n" +
                "Cách đánh: lặn (không bắn tới được) và nổi (mục tiêu trên mặt nước) theo lịch từng pha, mỗi lần nổi ở một chỗ khác; bong bóng báo trước chỗ nổi. Khi nổi nó phóng tên lửa hành trình tầm ngắn mỗi 12 giây và tự vệ bằng tên lửa phòng không. Pha 3 nổi hẳn, thêm pháo boong 100 mm.\n" +
                "Mạnh / yếu: thân giáp cấp [[4]], tháp chỉ huy và boong [[2]]: pháo binh, bom và đòn đánh nóc đánh vào boong.\n" +
                "Mẹo: chờ sẵn pháo binh và máy bay chỗ bong bóng; phá [[cửa ống phóng]] lúc cảnh báo (cửa mở trên mặt nước) hoặc bắn hạ tên lửa."),
            ["guide.ixion"] = (
                "[[Mini boss]] · armoured mine truck · rams your line\n" +
                "How it fights: an armoured mine truck (BelAZ-75710) that drives straight at about 7 m/s and turns very slowly. Its welded 125 mm turret turns all round and loads a high-explosive shell against a crowd (10 m blast, 5 m core) and an armour-piercing one against a single target, about 780 every 2 s; about every 45 s it charges down a line shown [[2 s]] ahead for about 900 and a 1 s stun, the turret firing all the while; two roof 12.7 mm machine guns; when it turns it drops a strip of six mines behind it that last 20 s.\n" +
                "Strong / weak: armour 4 in front, 3 on the sides, 2 behind and on top; the four [[rear tyres]] are armour 1, its weak point; break a [[front tyre]] and its charge swerves and stops, both and it circles very slowly; break the [[hull turret]] and it loses its gun, the [[cab]] and the machine guns stop.\n" +
                "Tip: step off the charge line, hit its flanks and rear as it turns, and keep clear of the mine strip.",
                "[[Mini boss]] · xe tải mỏ bọc thép · húc vào đội hình ta\n" +
                "Cách đánh: xe tải mỏ bọc thép (BelAZ-75710) chạy thẳng khoảng 7 m/s và xoay rất chậm. Tháp pháo 125 mm hàn trên thùng xoay 360°, nạp đạn nổ mạnh với đám đông (nổ lõi 5 m, rìa 10 m) và đạn xuyên với mục tiêu đơn lẻ, khoảng 780 mỗi 2 giây; cứ khoảng 45 giây nó lao theo đường thẳng báo trước [[2 giây]], khoảng 900 và choáng 1 giây, tháp pháo vẫn bắn trong lúc lao; hai súng máy 12,7 mm trên nóc; khi rẽ nó đổ ra sau một dải sáu quả mìn tồn tại 20 giây.\n" +
                "Mạnh / yếu: giáp trước 4, hông 3, sau và nóc 2; bốn [[lốp sau]] giáp cấp 1 là điểm yếu; phá một [[lốp trước]] thì cú lao lệch và dừng, phá cả hai thì nó quay vòng rất chậm; phá [[tháp pháo trên thùng]] là mất pháo, phá [[ca-bin]] là súng máy ngừng bắn.\n" +
                "Mẹo: tránh khỏi đường lao, đánh vào hông và đuôi khi nó xoay, và tránh dải mìn."),
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
                "How it fights: faster than Leviathan, on the near-shore lane: a twin 130 mm AK-130 shells the shore, its missile cells fire an anti-ship missile every 15 s, a CIWS takes missiles and drones.\n" +
                "Strong / weak: close enough for tank guns on the pier heads.\n" +
                "Tip: hold the piers with tanks and break the [[CIWS]] before sending missiles.",
                "[[Mini boss]] · tàu khu trục · sát bờ\n" +
                "Cách đánh: nhanh hơn Leviathan, chạy tuyến gần bờ: pháo AK-130 130 mm đôi nã vào bờ, ống phóng bắn tên lửa chống hạm mỗi 15 giây, CIWS chặn tên lửa và drone.\n" +
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
            ["guide.roc_gunship"] = (
                "[[Mini boss]] · Roc Arsenal
" +
                "How it fights: A gunship cut from the Roc's hull: heavy twin guns and flak, no bombs and no drones.
" +
                "Strong / weak: many small guns, each its own part; break them one by one.
" +
                "Tip: it has no super weapon; keep tanks spread and flank it.",
                "[[Mini boss]] · Roc Arsenal
" +
                "Cách đánh: Khinh khí cầu chiến đấu cắt từ thân Roc: pháo đôi hạng nặng và cao xạ, không bom, không drone.
" +
                "Mạnh / yếu: nhiều súng nhỏ, mỗi khẩu là một bộ phận; phá từng cái một.
" +
                "Mẹo: không có siêu vũ khí; đừng để xe dồn cục, đánh vòng sau."),
            ["guide.daedalus_assault"] = (
                "[[Mini boss]] · Daedalus Assault
" +
                "How it fights: A light assault lander: close guns, point-defence lasers and one slow drop-pod bay.
" +
                "Strong / weak: many small guns, each its own part; break them one by one.
" +
                "Tip: it has no super weapon; keep tanks spread and flank it.",
                "[[Mini boss]] · Daedalus Assault
" +
                "Cách đánh: Tàu đổ bộ xung kích nhẹ: pháo cận chiến, laser phòng thủ điểm và một khoang thả xe chậm.
" +
                "Mạnh / yếu: nhiều súng nhỏ, mỗi khẩu là một bộ phận; phá từng cái một.
" +
                "Mẹo: không có siêu vũ khí; đừng để xe dồn cục, đánh vòng sau."),
            ["guide.icarus_interceptor"] = (
                "[[Mini boss]] · Icarus Sentinel
" +
                "How it fights: A fast interceptor with laser towers and anti-air missile pods; it hunts aircraft first.
" +
                "Strong / weak: many small guns, each its own part; break them one by one.
" +
                "Tip: it has no super weapon; keep tanks spread and flank it.",
                "[[Mini boss]] · Icarus Sentinel
" +
                "Cách đánh: Phi thuyền đánh chặn nhanh: tháp laser và tên lửa phòng không, ưu tiên săn máy bay.
" +
                "Mạnh / yếu: nhiều súng nhỏ, mỗi khẩu là một bộ phận; phá từng cái một.
" +
                "Mẹo: không có siêu vũ khí; đừng để xe dồn cục, đánh vòng sau."),
            ["guide.matriarch_flak"] = (
                "[[Mini boss]] · Matriarch Wasp
" +
                "How it fights: A drone tender armed for the air: flak guns, CIWS and a few small drones.
" +
                "Strong / weak: many small guns, each its own part; break them one by one.
" +
                "Tip: it has no super weapon; keep tanks spread and flank it.",
                "[[Mini boss]] · Matriarch Wasp
" +
                "Cách đánh: Tàu mang drone thiên về phòng không: cao xạ, CIWS và vài drone nhỏ.
" +
                "Mạnh / yếu: nhiều súng nhỏ, mỗi khẩu là một bộ phận; phá từng cái một.
" +
                "Mẹo: không có siêu vũ khí; đừng để xe dồn cục, đánh vòng sau."),
            ["guide.jotunn_artillery"] = (
                "[[Mini boss]] · Jötunn Mortar
" +
                "How it fights: A mobile fortress turned to mortars: it lobs shells over cover; close in under its arc.
" +
                "Strong / weak: many small guns, each its own part; break them one by one.
" +
                "Tip: it has no super weapon; keep tanks spread and flank it.",
                "[[Mini boss]] · Jötunn Mortar
" +
                "Cách đánh: Pháo đài di động chuyên cối: bắn vòng qua vật cản; áp sát để tránh cung đạn.
" +
                "Mạnh / yếu: nhiều súng nhỏ, mỗi khẩu là một bộ phận; phá từng cái một.
" +
                "Mẹo: không có siêu vũ khí; đừng để xe dồn cục, đánh vòng sau."),
            ["guide.bastion_aa"] = (
                "[[Mini boss]] · Bastion Flak
" +
                "How it fights: A fortress thick with flak and missiles: deadly to aircraft, thin against tanks.
" +
                "Strong / weak: many small guns, each its own part; break them one by one.
" +
                "Tip: it has no super weapon; keep tanks spread and flank it.",
                "[[Mini boss]] · Bastion Flak
" +
                "Cách đánh: Pháo đài dày cao xạ và tên lửa: chết chóc với máy bay, mỏng với xe tăng.
" +
                "Mạnh / yếu: nhiều súng nhỏ, mỗi khẩu là một bộ phận; phá từng cái một.
" +
                "Mẹo: không có siêu vũ khí; đừng để xe dồn cục, đánh vòng sau."),
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
                "How it fights: never in orbit: high and low on a fixed schedule. A [[laser turret]], two 40 mm test guns firing down from under the hull, a [[pod bay]] and a [[point-defence laser]] that picks off missiles.\n" +
                "Strong / weak: at high altitude only long-range anti-air and fighters reach it; low, every anti-air weapon does.\n" +
                "Tip: wait for its low windows; break the point-defence laser before sending missiles.",
                "[[Mini boss]] · phi thuyền nguyên mẫu · lần đầu thấy Dự án Icarus\n" +
                "Cách đánh: không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. Một [[tháp la-de]], hai pháo thử 40 mm bắn xuống từ dưới bụng, một [[khoang đổ bộ]] và một [[la-de phòng thủ điểm]] bắn hạ tên lửa.\n" +
                "Mạnh / yếu: ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng thấp mọi vũ khí phòng không đều tới.\n" +
                "Mẹo: chờ lúc nó xuống thấp; phá la-de phòng thủ điểm trước khi dùng tên lửa."),
            ["guide.argus"] = (
                "[[Mini boss]] · scout airship · directs the enemy's guns\n" +
                "How it fights: while it lives, the enemy's artillery falls about half as wide. Flak guns, rockets and bombs.\n" +
                "Strong / weak: slow and big; only anti-air and fighters reach it.\n" +
                "Tip: its [[drone bay]] and engines are all it has to break.",
                "[[Mini boss]] · khí cầu trinh sát · chỉ điểm cho pháo địch\n" +
                "Cách đánh: khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa. Cao xạ, rocket và bom.\n" +
                "Mạnh / yếu: chậm và to; chỉ phòng không và tiêm kích bắn tới.\n" +
                "Mẹo: [[khoang drone]] và động cơ là tất cả những gì cần phá."),

            // ---------------------------------------------------------------- parts tips
            ["guide.parts.tip.moloch"] = ("Tip: flank it for the [[workshop doors]] at the back (armour 2): each one broken halves what it builds, both stop it; the [[tracks]] slow it.", "Mẹo: vòng ra sau đánh [[cửa xưởng]] (giáp cấp 2): phá một cửa là sinh xe giảm một nửa, phá cả hai là ngừng hẳn; phá [[cụm xích]] để làm chậm."),
            ["guide.parts.tip.daedalus"] = ("Tip: break the [[drop-pod bays]] (each one slows the drops; the mass drop falls as three pods with one gone) and the [[point-defence lasers]] before sending missiles.", "Mẹo: phá [[cửa thả khoang]] (mỗi cửa mất là thả chậm hơn; mất một cửa thì đòn đổ bộ lớn chỉ còn ba khoang) và [[tháp la-de phòng thủ]] trước khi dùng tên lửa."),
            ["guide.parts.tip.typhon"] = ("Tip: the [[launch doors]] carry its missiles (they show above the water during a warning); the [[sail]] aims its SAM; the [[sonar]] its fire control.", "Mẹo: [[cửa ống phóng]] mang tên lửa (lộ trên mặt nước lúc cảnh báo); [[tháp chỉ huy]] ngắm tên lửa phòng không; [[sô-na]] là hệ điều khiển hỏa lực."),
            ["guide.parts.tip.ixion"] = ("Tip: break the [[hull turret]] and the 125 mm is gone; break a [[front tyre]] and its charge swerves and stops; the [[rear tyres]] are armour 1; break the [[cab]] and the machine guns stop.", "Mẹo: phá [[tháp pháo trên thùng]] là mất pháo 125 mm; phá một [[lốp trước]] thì cú lao lệch và dừng; [[lốp sau]] giáp cấp 1; phá [[ca-bin]] là súng máy ngừng bắn."),
            ["guide.parts.tip.bastion_mk0"] = ("Tip: break the [[mortar]] first; the two turrets only reach close.", "Mẹo: phá [[khẩu cối]] trước; hai tháp pháo chỉ bắn gần."),
            ["guide.parts.tip.fenrir"] = ("Tip: each [[rocket box]] broken halves its rockets; its flak is all it has against aircraft.", "Mẹo: mỗi [[hộp rốc-két]] bị phá là rốc-két của nó giảm một nửa; cao xạ là thứ duy nhất chống máy bay."),
            ["guide.parts.tip.scylla"] = ("Tip: break the [[missile cells]] for its cruise missiles and the [[CIWS]] before sending missiles.", "Mẹo: phá [[ống phóng tên lửa]] để chặn tên lửa hành trình, phá [[CIWS]] trước khi dùng tên lửa."),
            ["guide.parts.tip.locust"] = ("Tip: its [[drone bay]] is everything it has.", "Mẹo: [[khoang drone]] là tất cả những gì nó có."),
            ["guide.parts.tip.roc_gunship"] = ("Tip: break its guns and its [[engine]] first; it carries no radar.", "Mẹo: phá súng và [[động cơ]] trước; nó không có radar."),
            ["guide.parts.tip.daedalus_assault"] = ("Tip: break its guns and its [[engine]] first; it carries no radar.", "Mẹo: phá súng và [[động cơ]] trước; nó không có radar."),
            ["guide.parts.tip.icarus_interceptor"] = ("Tip: break its guns and its [[engine]] first; it carries no radar.", "Mẹo: phá súng và [[động cơ]] trước; nó không có radar."),
            ["guide.parts.tip.matriarch_flak"] = ("Tip: break its guns and its [[engine]] first; it carries no radar.", "Mẹo: phá súng và [[động cơ]] trước; nó không có radar."),
            ["guide.parts.tip.jotunn_artillery"] = ("Tip: break its guns and its [[engine]] first; it carries no radar.", "Mẹo: phá súng và [[động cơ]] trước; nó không có radar."),
            ["guide.parts.tip.bastion_aa"] = ("Tip: break its guns and its [[engine]] first; it carries no radar.", "Mẹo: phá súng và [[động cơ]] trước; nó không có radar."),
            ["guide.parts.tip.behemoth_mk2"] = ("Tip: the [[main gun]] is its punch; the [[protection system]] shoots down two missiles a volley.", "Mẹo: [[pháo chính]] là đòn mạnh nhất; [[hệ thống bảo vệ]] bắn hạ hai tên lửa mỗi loạt."),
            ["guide.parts.tip.icarus_mk0"] = ("Tip: the [[point-defence laser]] is its protection, the [[pod bay]] its drops.", "Mẹo: [[la-de phòng thủ điểm]] là lớp bảo vệ, [[khoang đổ bộ]] mang các đợt thả."),
            ["guide.parts.tip.argus"] = ("Tip: its [[drone bay]] sends the scout drones; break it to stop them.", "Mẹo: [[khoang drone]] thả drone trinh sát; phá nó là hết."),

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
            ["part.wheel"] = ("front tyre", "lốp trước"),
            ["part.reartyre"] = ("rear tyre", "lốp sau"),
            ["part.hulltower"] = ("hull turret", "tháp pháo trên thùng"),
            ["part.steerwheel"] = ("steering wheel", "bánh lái sau"),
            ["part.wing"] = ("wing", "cánh"),
            ["part.casemate"] = ("casemate gun", "pháo lô cốt"),
            ["part.fx.stop.factory"] = ("its workshop builds less (nothing once both doors are broken)", "xưởng sinh ít xe hơn (ngừng hẳn khi cả hai cửa bị phá)"),
            ["part.fx.stop.crush"] = ("it crushes nothing in its way", "nó không còn nghiền được gì trên đường"),
            ["part.fx.stop.spotaura"] = ("the enemy's artillery scatters as usual again", "pháo binh địch lại bắn tản mát như thường"),
            ["radio.part.door"] = ("Command: one of {boss}'s workshop doors is down. It is building half as much!", "Chỉ huy: một cửa xưởng của {boss} đã bị phá. Nó chỉ sinh được một nửa số xe!"),
            ["radio.part.sail"] = ("Command: {boss}'s sail is wrecked: its SAM is firing blind.", "Chỉ huy: tháp chỉ huy của {boss} tan nát: tên lửa phòng không của nó bắn mù."),
            ["radio.part.launchdoors"] = ("Command: {boss}'s launch doors are jammed shut on one side!", "Chỉ huy: một cụm cửa ống phóng của {boss} đã kẹt cứng!"),
            ["radio.part.wheel"] = ("Command: {boss} has lost a wheel. It is going round in circles!", "Chỉ huy: {boss} đã mất một bánh. Nó đang quay vòng!"),

            // ---------------------------------------------------------------- arrival lines (prompt 20 K: each boss speaks for its general)
            ["radio.brandt.bastion"] = ("Brandt: \"Bastion is rolling. Nothing has ever taken a fortress that walks.\"", "Brandt: \"Bastion lăn bánh. Chưa ai hạ nổi một pháo đài biết đi.\""),
            ["radio.brandt.bastion_mk0"] = ("Brandt: \"The prototype will do. Grind them down, slowly.\"", "Brandt: \"Bản nguyên mẫu là đủ. Nghiền chúng từ từ.\""),
            ["radio.varga.behemoth"] = ("Varga: \"Behemoth is on the field. Get out of its way or under it.\"", "Varga: \"Behemoth ra trận. Tránh đường, hoặc nằm dưới xích nó.\""),
            ["radio.varga.moloch"] = ("Varga: \"Moloch builds as it rolls. Every one you kill, I make two.\"", "Varga: \"Moloch vừa đi vừa đúc xe. Các người diệt một, ta làm ra hai.\""),
            ["radio.varga.inferno"] = ("Varga: \"Inferno, burn the road clean.\"", "Varga: \"Inferno, đốt sạch con đường.\""),
            ["radio.varga.behemoth_mk2"] = ("Varga: \"You broke one Behemoth. This one wears winter.\"", "Varga: \"Các người phá được một Behemoth. Con này khoác cả mùa đông.\""),
            ["radio.orlov.fortress"] = ("Orlov: \"Jötunn is moving. Winter walks with it.\"", "Orlov: \"Jötunn đang tiến. Mùa đông đi cùng nó.\""),
            ["radio.orlov.fenrir"] = ("Orlov: \"Fenrir, bite and run. Do not stay to be caught.\"", "Orlov: \"Fenrir, cắn rồi chạy. Đừng ở lại cho chúng tóm.\""),
            ["radio.kessler.tempest"] = ("Kessler: \"Tempest, charge the rail. One line, one pass.\"", "Kessler: \"Tempest, nạp pháo điện từ. Một đường, một phát.\""),
            ["radio.kessler.juggernaut"] = ("Kessler: \"Juggernaut is on the line. Keep to the timetable.\"", "Kessler: \"Juggernaut đã lên tuyến. Chạy đúng giờ.\""),
            ["radio.kessler.scylla"] = ("Kessler: \"Scylla, close the shore. Let them see you coming.\"", "Kessler: \"Scylla, áp sát bờ. Cho chúng thấy ngươi đang tới.\""),
            ["radio.kessler.scylla.sunk"] = ("Kessler: \"Scylla is gone... note it in the log.\"", "Kessler: \"Scylla mất rồi... ghi vào nhật ký.\""),
            ["radio.sen.matriarch"] = ("Dr Venn: \"Matriarch, open the hives. Let the children play.\"", "Tiến sĩ Venn: \"Matriarch, mở tổ. Cho lũ con đi chơi.\""),
            ["radio.sen.locust"] = ("Dr Venn: \"Locust, swarm. Numbers are my armour.\"", "Tiến sĩ Venn: \"Locust, xuất bầy. Số đông là lớp giáp của ta.\""),
            ["radio.hung.nemesis"] = ("{@lyhan}: \"Nemesis is on the rails. When it stops, the sky opens.\"", "{@lyhan}: \"Nemesis đã lên đường ray. Khi nó dừng, bầu trời sẽ mở.\""),
            ["radio.hung.typhon"] = ("{@lyhan}: \"Typhon is under you, Colonel. You will not see it until it is too late.\"", "{@lyhan}: \"Typhon ở ngay dưới chân các người, đại tá. Thấy được nó thì đã muộn.\""),
            ["radio.hung.typhon.sunk"] = ("{@lyhan}: \"Typhon... flood the tubes. Let it take its secrets down.\"", "{@lyhan}: \"Typhon... cho nước tràn ống phóng. Để nó mang bí mật xuống đáy.\""),
            ["radio.hung.ixion"] = ("{@lyhan}: \"Ixion does not turn. Neither will I.\"", "{@lyhan}: \"Ixion không quay đầu. Ta cũng vậy.\""),
            ["radio.hung.borer"] = ("{@lyhan}: \"Tartarus is under the ridge. Listen to the ground.\"", "{@lyhan}: \"Tartarus đang dưới sườn núi. Hãy nghe mặt đất.\""),
            ["radio.hung.borer.half"] = ("{@lyhan}: \"Deeper, faster. Break them from below.\"", "{@lyhan}: \"Sâu hơn, nhanh hơn. Đập chúng từ bên dưới.\""),
            ["radio.quaden.harpy"] = ("Raven: \"Harpy, over the ridge. Hunt.\"", "Raven: \"Harpy, vượt qua sườn đồi. Săn đi.\""),
            // Play-test 14: Raven fights the Skyhold duel in the Harpy (Morrigan was deleted).
            ["radio.quaden.harpy.duel"] = ("Raven: \"Just you and me, Hawk. No escorts, no guns on the ground.\"", "Raven: \"Chỉ có ta và cậu, Hawk. Không hộ tống, không súng dưới đất.\""),
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
            ["guide.bigattack.moloch_factory_dump.how"] = ("Its workshop doors open for 4 s, then every door lets out: six vehicles at once, with eight 152 mm high-explosive shells (350 each, 6 m core, 12 m edge, falling off) on your nearest group. Every 50 s.", "Cửa xưởng mở 4 giây, rồi mọi cửa cùng xả: sáu xe một lúc, kèm tám phát pháo 152 mm nổ mạnh (mỗi phát 350, lõi 6 m, rìa 12 m, giảm dần) vào cụm quân gần nhất. Cứ 50 giây."),
            ["guide.bigattack.moloch_factory_dump.dodge"] = ("Move your group off the marked area; be ready for six more vehicles.", "Đưa cụm quân ra khỏi vùng đánh dấu; sẵn sàng đón thêm sáu xe."),
            ["guide.bigattack.moloch_factory_dump.stop"] = ("Break a workshop door during the warning: only half come out; both broken, only the shells.", "Phá một cửa xưởng lúc cảnh báo: chỉ ra một nửa; phá cả hai thì chỉ còn loạt pháo."),
            ["bigattack.daedalus_mass_drop"] = ("Orbital Mass Drop", "Đổ bộ ồ ạt từ quỹ đạo"),
            ["bigattack.daedalus_mass_drop.cancelled"] = ("Mass drop called off", "Đã chặn đợt đổ bộ"),
            ["radio.bigattack.daedalus_mass_drop"] = ("Aurel: \"All pods on that group. Land on them.\"", "Aurel: \"Mọi khoang vào cụm đó. Đáp thẳng lên đầu chúng.\""),
            ["guide.bigattack.daedalus_mass_drop.how"] = ("Eight pods fall together on one group: 600 kinetic each (high penetration, 6 m core, 12 m edge, falling off) on landing, then each lets a vehicle out; 4 s of warning. Every 50 s.", "Tám khoang cùng rơi vào một cụm quân: mỗi khoang chạm đất gây 600 động năng (xuyên cao, lõi 6 m, rìa 12 m, giảm dần) rồi thả một xe; cảnh báo 4 giây. Cứ 50 giây."),
            ["guide.bigattack.daedalus_mass_drop.dodge"] = ("Scatter the marked group; heavy armour does not save it.", "Tản cụm quân bị đánh dấu ra; giáp dày cũng không cứu được."),
            ["guide.bigattack.daedalus_mass_drop.stop"] = ("Break a pod bay during the warning: only four pods fall.", "Phá một cửa thả khoang lúc cảnh báo: chỉ còn bốn khoang rơi."),
            ["bigattack.typhon_underwater_launch"] = ("Underwater Launch", "Phóng tên lửa từ dưới nước"),
            ["bigattack.typhon_underwater_launch.cancelled"] = ("Launch aborted", "Đã chặn đợt phóng"),
            ["radio.bigattack.typhon_underwater_launch"] = ("{@lyhan}: \"Launch depth. Six for their headquarters.\"", "{@lyhan}: \"Lên độ sâu phóng. Sáu quả cho sở chỉ huy của chúng.\""),
            ["guide.bigattack.typhon_underwater_launch.how"] = ("Six missiles at your base: about 700 high explosive each (9 m core, 18 m edge, falling off), double on buildings; a clock shows their flight after the 4 s warning. Every 50 s.", "Sáu tên lửa vào căn cứ ta: mỗi quả khoảng 700 nổ mạnh (lõi 9 m, rìa 18 m, giảm dần), gấp đôi lên công trình; sau 4 giây cảnh báo có đồng hồ bay. Cứ 50 giây."),
            ["guide.bigattack.typhon_underwater_launch.dodge"] = ("Move units off the marked points; towers cannot move, so cover them.", "Đưa quân ra khỏi các điểm đánh dấu; tháp không di chuyển được nên hãy che chắn."),
            ["guide.bigattack.typhon_underwater_launch.stop"] = ("Break the launch doors during the warning (they show above the water), or shoot the missiles down (250 health each).", "Phá cửa ống phóng lúc cảnh báo (cửa lộ trên mặt nước), hoặc bắn hạ tên lửa (mỗi quả 250 máu)."),

            // ---------------------------------------------------------------- prompt 20 pass 3: Boss Hunt (N)
            ["hunt.full"] = ("Full Boss Hunt", "Săn trùm toàn tập"),
            ["hunt.full.kicker"] = ("FULL BOSS HUNT", "SĂN TRÙM TOÀN TẬP"),
            ["hunt.full.sub"] = ("Every boss of the story, in order", "Mọi boss của cốt truyện, theo thứ tự"),
            ["hunt.fullSub"] = ("{count|# boss|# bosses} in story order", "{count} boss theo cốt truyện"),
            ["hunt.full.rules"] = ("All {count} main and mini bosses of the chapters open, in story order. A checkpoint after every boss: play it over as many sittings as you like. Every boss is a fresh battle: your army is not kept and you start with the same CP; only your combat supports go on (picked after each main boss, up to +40% army strength, then only play-changing ones). Ranked by total time.",
                "Toàn bộ {count} boss chủ lực và mini boss của các chương đang mở, theo đúng thứ tự cốt truyện. Có điểm hồi sinh sau mỗi boss: chơi dần qua bao nhiêu lần cũng được. Mỗi boss là một trận mới: quân không được giữ và bạn bắt đầu với cùng lượng CP; chỉ hỗ trợ tác chiến được giữ (chọn sau mỗi boss chủ lực, tối đa +40% sức mạnh đội quân, sau đó chỉ còn các hỗ trợ đổi cách chơi). Xếp hạng theo tổng thời gian."),
            ["hunt.full.locked"] = ("Opens once chapter {chapter}'s operation is won.", "Mở khi thắng chiến dịch lớn của chương {chapter}."),
            ["hunt.full.reward"] = ("First clear: {coins|# coin|# coins} and a legendary crate", "Lần đầu hoàn thành: {coins} xu và một hòm huyền thoại"),
            ["hunt.weekly.rules"] = ("{count|# boss|# bosses} this week: {minis|# mini boss|# mini bosses} leading to {mains|# main boss|# main bosses}, each stronger than the last. Boss health follows the strength of the deck you bring. A 15 s rest between bosses repairs 30% of your surviving army and keeps half of your CP; after each main boss, pick one of three combat supports (up to +40% army strength in all) and keep a checkpoint. {minutes|# minute|# minutes} on the clock.",
                "{count} boss tuần này: {minis} mini boss dẫn tới {mains} boss chủ lực, boss sau mạnh hơn boss trước. Máu boss theo sức mạnh bộ bài bạn mang. Nghỉ 15 giây giữa các boss, xe còn sống được sửa 30% và giữ 50% CP; sau mỗi boss chủ lực (tối đa +40% sức mạnh đội quân từ hỗ trợ), chọn một trong ba hỗ trợ tác chiến và lưu điểm hồi sinh. Đồng hồ {minutes} phút."),
            ["hunt.weekly.reward"] = ("First clear this week: {coins|# coin|# coins}", "Lần đầu hoàn thành trong tuần: {coins} xu"),
            ["hunt.roster"] = ("This week's bosses", "Boss tuần này"),
            ["hunt.fullRoster"] = ("In story order", "Theo thứ tự cốt truyện"),
            ["hunt.restTitle"] = ("Rest · army repaired {percent}%", "Nghỉ · quân được sửa {percent}%"),
            // Prompt 26 E3: the full hunt fights every boss in a fresh battle (no army kept, so nothing to repair).
            ["hunt.restFresh"] = ("Rest · the next boss is a fresh battle", "Nghỉ · boss sau là một trận mới"),
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
            // Play-test 6 (DECISIONS 21G): the endless run after the last boss.
            ["hunt.endless.title"] = ("Every boss down. Carry on?", "Đã hạ mọi boss. Đánh tiếp?"),
            ["hunt.endless.stop"] = ("End the hunt", "Kết thúc"),
            ["hunt.endless.stop.info"] = ("Take the win and the rewards now.", "Nhận chiến thắng và phần thưởng ngay."),
            ["hunt.endless.go"] = ("Endless", "Vô tận"),
            ["hunt.endless.go.info"] = ("The bosses come again, each one tougher with more escorts, until your army falls. The win is kept and every boss pays.",
                "Boss quay lại lần nữa, con sau mạnh hơn và đông hộ tống hơn, tới khi quân bạn gục. Chiến thắng vẫn giữ, mỗi boss hạ đều có thưởng."),
            ["hunt.endless.auto"] = ("The hunt ends in {seconds} s unless you carry on.", "Sau {seconds} giây sẽ kết thúc nếu bạn không đánh tiếp."),
            ["hunt.endless.detail"] = ("Endless · {count|# boss|# bosses} down", "Vô tận · đã hạ {count} boss"),
            ["hunt.endless.row"] = ("Endless bosses", "Boss vô tận"),
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
            // ---------------------------------------------------------------- prompt 22 E (DECISIONS 22E): new maps, bosses and the ally
            // (Kept here, beside the bosses' other words, so the story pass's renames and these additions never touch the same lines.)
            ["map.foundry"] = ("{@foundry}", "{@foundry}"),
            ["map.foundry.sub"] = ("Tank works · Industrial", "Xưởng xe tăng · Công nghiệp"),
            ["map.veyra_old_quarter"] = ("{@veyra_old_quarter}", "{@veyra_old_quarter}"),
            ["map.veyra_old_quarter.sub"] = ("Old town · Urban", "Phố cổ · Đô thị"),
            ["guide.map.foundry"] = (
                "[[{@foundry}]] · industrial battlefield · an indoor tank works\n" +
                "How it fights: Hegemon's old tank works, solid blocks of sheds and workshops cut by 10 m [[factory lanes]]: every way across is a narrow passage between walls. The casting hall at the centre (the centre point) opens only where the lanes run in; the press shop and the rolling mill (the side points) are walled yards with one doorway a side.\n" +
                "Strong / weak: favours short-range armour, flamers and anti-tank vehicles waiting at the lane corners; long guns and artillery see little down the lanes, and big hulls queue in the doorways.\n" +
                "Tip: hold the lane crossings round the hall, not the hall floor; bring a few light vehicles to take the yards through the side doors while the heavies hold the lanes.",
                "[[{@foundry}]] · chiến trường công nghiệp · xưởng xe tăng trong nhà\n" +
                "Cách đánh: xưởng xe tăng cũ của Hegemon, các dãy nhà xưởng liền khối bị cắt bởi các [[lối xưởng]] rộng 10 m: lối nào đi qua cũng là một hành lang hẹp giữa hai bức tường. Xưởng đúc ở giữa (cứ điểm giữa) chỉ mở ở chỗ các lối chạy vào; xưởng dập và xưởng cán (hai cứ điểm bên) là những sân có tường bao, mỗi mặt một cửa.\n" +
                "Mạnh / yếu: có lợi cho thiết giáp tầm gần, xe phun lửa và xe chống tăng chờ ở góc lối; pháo tầm xa và pháo binh nhìn được rất ít trong các lối hẹp, còn xe lớn phải xếp hàng ở cửa.\n" +
                "Mẹo: giữ các ngã tư quanh xưởng đúc chứ đừng giữ sàn xưởng; mang theo vài xe nhẹ để chiếm các sân qua cửa bên trong khi xe nặng giữ các lối."),
            ["guide.map.veyra_old_quarter"] = (
                "[[{@veyra_old_quarter}]] · city battlefield · narrow streets and squares\n" +
                "How it fights: the capital's old town: 10 m [[streets]] that bend round the old plots between tall houses, opening on squares. The cathedral square is the centre point; the market square and the clock square are the side points; four small piazzas along the way.\n" +
                "Strong / weak: favours armour that holds a street corner, anti-tank ambushes and mortars that drop over the roofs; the squares are killing grounds for anything caught crossing them in the open.\n" +
                "Tip: clear the houses' corners before a square, and cross it under smoke; the bends hide what waits round them, so lead with a scout.",
                "[[{@veyra_old_quarter}]] · chiến trường đô thị · phố hẹp và quảng trường\n" +
                "Cách đánh: khu phố cổ của thủ đô: các [[con phố]] rộng 10 m uốn quanh những lô đất cũ giữa các dãy nhà cao, mở ra các quảng trường. Quảng trường nhà thờ lớn là cứ điểm giữa; quảng trường chợ và quảng trường tháp đồng hồ là hai cứ điểm bên; dọc đường có bốn quảng trường nhỏ.\n" +
                "Mạnh / yếu: có lợi cho thiết giáp giữ góc phố, xe chống tăng phục kích và súng cối bắn qua mái nhà; quảng trường là bãi giết cho mọi thứ bị bắt gặp giữa chỗ trống.\n" +
                "Mẹo: dọn các góc nhà trước khi vào quảng trường, và băng qua dưới màn khói; khúc cua che mất thứ đang chờ phía sau, nên cho xe trinh sát đi đầu."),

            // Behemoth Mk.0: Varga's prototype Behemoth, a variant made from the Behemoth's data.
            ["unit.behemoth_mk0"] = ("Behemoth Mk.0 · Prototype Behemoth", "Behemoth Mk.0 · Behemoth nguyên mẫu"),
            ["short.behemoth_mk0"] = ("Behemoth Mk.0", "Behemoth Mk.0"),
            ["note.behemoth_mk0"] = ("Varga's first Behemoth off the factory line: its main gun, two flank guns and a rocket pod; no flak, no protection system.", "Behemoth đầu tiên của Varga ra khỏi dây chuyền: pháo chính, hai pháo sườn và một giàn rốc-két; không có pháo cao xạ, không có hệ thống bảo vệ chủ động."),
            ["guide.behemoth_mk0"] = (
                "[[Mini boss]] · prototype Behemoth · unfinished\n" +
                "How it fights: the Behemoth's first build, slower than the finished one: its main gun, two flank guns and a rocket pod on the same hull.\n" +
                "Strong / weak: front armour [[3]]; no flak and no protection system, so aircraft and missiles meet nothing.\n" +
                "Tip: bring aircraft and missiles; break the [[main gun]], its heaviest gun.",
                "[[Mini boss]] · Behemoth nguyên mẫu · chưa hoàn thiện\n" +
                "Cách đánh: bản lắp đầu tiên của Behemoth, chậm hơn bản hoàn chỉnh: pháo chính, hai pháo sườn và một giàn rốc-két trên cùng thân xe.\n" +
                "Mạnh / yếu: mặt trước giáp cấp [[3]]; không có pháo cao xạ và hệ thống bảo vệ chủ động, nên máy bay và tên lửa không gặp cản trở nào.\n" +
                "Mẹo: mang máy bay và tên lửa; phá [[pháo chính]], khẩu mạnh nhất của nó."),
            ["guide.parts.tip.behemoth_mk0"] = ("Tip: the [[main gun]] is its heaviest gun; with both [[flank guns]] broken it only fires ahead.", "Mẹo: [[pháo chính]] là khẩu mạnh nhất; phá cả hai [[pháo sườn]] thì nó chỉ còn bắn được phía trước."),
            ["radio.varga.behemoth_mk0"] = ("Varga: \"The first one off the line. Let's see if it runs.\"", "Varga: \"Chiếc đầu tiên ra khỏi dây chuyền. Xem nó có chạy được không.\""),

            // Big attacks' targets.
            ["guide.bigattack.target.air"] = ("your aircraft and anti-air", "máy bay và xe phòng không của bạn"),
            ["guide.bigattack.target.aironly"] = ("your aircraft", "máy bay của bạn"),

            // Mara's Behemoth: a scripted ally of chapter 12's last battle (never a card).
            ["unit.mara_behemoth"] = ("{@mai}'s Behemoth · Allied Behemoth", "{@mai}'s Behemoth · Behemoth đồng minh"),
            ["short.mara_behemoth"] = ("{@mai}'s Behemoth", "Behemoth của {@mai}"),
            ["note.mara_behemoth"] = ("A Behemoth rebuilt by {@mai} in our colours, fighting beside us in the last battle.", "Một chiếc Behemoth được {@mai} dựng lại mang màu cờ của ta, chiến đấu bên ta trong trận cuối."),

            // Prompt 25 F2 batch D: the eight new bosses (stand-ins, DECISIONS 25F2-D).
            ["unit.kraken"] = ("Kraken · Aircraft Carrier", "Kraken · Tàu sân bay"),
            ["short.kraken"] = ("Kraken", "Kraken"),
            ["note.kraken"] = ("Kessler's new flagship: the longest ship afloat, a flat flight deck with aircraft parked on it and a CIWS ring.", "Soái hạm mới của Kessler: con tàu dài nhất mặt nước, boong phẳng đỗ đầy máy bay và một vòng CIWS."),
            ["guide.kraken"] = (
                "[[Boss]] · aircraft carrier · air raids from the sea\n" +
                "How it fights: a stand-in hull for now (Leviathan's guns, missile cells and CIWS). Its [[flight deck]] launches stealth strike jets two at a time (four up at most, every 40 s) and attack helicopters, and every 50 s it calls an air raid.\n" +
                "Strong / weak: the longest, toughest hull afloat; the elevator deck is thin (armour 2).\n" +
                "Tip: break the [[flight deck]] and the aircraft stop coming; during the 4 s warning leave the long red strip.",
                "[[Boss]] · tàu sân bay · không kích từ biển\n" +
                "Cách đánh: tạm dùng thân tàu Leviathan (pháo, ống phóng tên lửa và CIWS). [[Boong cất cánh]] phóng tiêm kích tàng hình từng cặp (tối đa bốn chiếc, mỗi 40 giây) và trực thăng tấn công, và cứ 50 giây nó gọi một đợt không kích.\n" +
                "Mạnh / yếu: thân tàu dài và dày nhất mặt nước; boong thang máy mỏng (giáp 2).\n" +
                "Mẹo: phá [[boong cất cánh]] là máy bay hết xuất kích; trong 4 giây cảnh báo hãy ra khỏi dải đỏ dài."),
            ["guide.parts.tip.kraken"] = ("Tip: the [[flight deck]] feeds its aircraft and carries the air raid; break it first. The [[CIWS]] shoot missiles down before they land.", "Mẹo: [[boong cất cánh]] nuôi máy bay và mang đòn không kích; phá nó trước. [[CIWS]] bắn hạ tên lửa trước khi chúng trúng."),
            ["radio.kessler.kraken"] = ("Kessler: \"Kraken, launch everything. Let the sky do the work.\"", "Kessler: \"Kraken, thả hết máy bay. Để bầu trời làm việc.\""),
            ["unit.monster"] = ("Monster · 800 mm Self-Propelled Gun", "Monster · Pháo tự hành 800 mm"),
            ["short.monster"] = ("Monster", "Monster"),
            ["note.monster"] = ("A steel mountain on tracks with one 800 mm gun: very slow, and the gun is a part with its own health.", "Một khối thép khổng lồ trên xích với một nòng 800 mm: rất chậm, và nòng là bộ phận có máu riêng."),
            ["guide.monster"] = (
                "[[Boss]] · super-heavy self-propelled gun · one shell a minute\n" +
                "How it fights: a stand-in hull for now (the Bastion's turrets and mortar, bigger). It crawls, and every 80 s its 800 mm gun rises and fires one 4,000-damage shell with a 20 m blast.\n" +
                "Strong / weak: enormous armour and health, but slower than any boss.\n" +
                "Tip: leave the red ring the 6 s it is shown; break the [[mortar]] (the long barrel) and the shell is gone.",
                "[[Boss]] · pháo tự hành siêu nặng · mỗi phút một phát\n" +
                "Cách đánh: tạm dùng thân Bastion (tháp pháo và khẩu cối, to hơn). Nó bò rất chậm, cứ 80 giây nòng 800 mm nâng lên bắn một quả 4.000 sát thương, nổ lan 20 m.\n" +
                "Mạnh / yếu: giáp và máu khổng lồ, nhưng chậm hơn mọi boss.\n" +
                "Mẹo: ra khỏi vòng đỏ trong 6 giây nó hiện; phá [[khẩu cối]] (nòng dài) là mất đòn này."),
            ["guide.parts.tip.monster"] = ("Tip: the [[mortar]] is the long barrel with its own health; break it and the 800 mm shell is gone. The four turrets only defend.", "Mẹo: [[khẩu cối]] là nòng dài có máu riêng; phá nó là hết quả đạn 800 mm. Bốn tháp pháo chỉ để tự vệ."),
            ["radio.orlov.monster"] = ("Orlov: \"Monster, advance. Nothing on that field is worth a second shell.\"", "Orlov: \"Monster, tiến lên. Chẳng thứ gì trên chiến trường đáng một phát thứ hai.\""),
            ["unit.hyperion"] = ("Hyperion · Heavy Cruiser", "Hyperion · Tuần dương hạm hạng nặng"),
            ["short.hyperion"] = ("Hyperion", "Hyperion"),
            ["note.hyperion"] = ("Aurel's heavy space cruiser: a forked armoured prow with the sun-beam projector slung under it, twin 155 mm turrets, missile cells, laser batteries and 127 mm guns under the hull. It never comes down.", "Tuần dương hạm vũ trụ hạng nặng của Aurel: mũi bọc giáp chẻ đôi, máy chiếu tia mặt trời treo dưới mũi, tháp pháo đôi 155 mm, ô phóng tên lửa, dàn la-de và pháo 127 mm dưới bụng. Không bao giờ hạ xuống."),
            ["guide.hyperion"] = (
                "[[Boss]] · heavy space cruiser · never lands\n" +
                "How it fights: stays on the high tier. Two twin 155 mm turrets on the prow, two missile cells on its flanks, laser batteries and 127 mm guns under the hull firing down; point-defence lasers guard it, it drops two landing pods a minute, and every 65 s the projector under its prow burns a 70 × 6 m strip for 4 s.\n" +
                "Strong / weak: it never comes to the low tier, so only long-range missiles and electromagnetic guns reach it.\n" +
                "Tip: keep long-range missiles and railguns ready; leave the strip at once when the warning shows.",
                "[[Boss]] · tuần dương hạm vũ trụ hạng nặng · không bao giờ hạ xuống\n" +
                "Cách đánh: luôn ở tầng cao. Hai tháp pháo đôi 155 mm trên mũi, hai ô phóng tên lửa hai bên sườn, dàn la-de và pháo 127 mm dưới bụng bắn xuống; tháp la-de phòng thủ điểm che chắn, mỗi phút thả hai khoang đổ bộ, cứ 65 giây máy chiếu dưới mũi đốt dải 70 × 6 m trong 4 giây.\n" +
                "Mạnh / yếu: không bao giờ xuống tầng thấp, chỉ tên lửa tầm xa và pháo điện từ với tới.\n" +
                "Mẹo: giữ sẵn tên lửa tầm xa và pháo ray; rời dải ngay khi có cảnh báo."),
            ["guide.parts.tip.hyperion"] = ("Tip: the [[main laser]] (the projector under the prow) carries the sun beam; break it and the beam is gone. The [[point-defence lasers]] shoot your missiles down.", "Mẹo: [[la-de chính]] (máy chiếu dưới mũi) mang đòn tia mặt trời; phá nó là hết tia. [[Tháp la-de phòng thủ]] bắn hạ tên lửa của bạn."),
            ["radio.aurel.hyperion"] = ("Aurel: \"Hyperion is awake. The sun has a new tenant, Colonel.\"", "Aurel: \"Hyperion đã thức. Mặt trời có người thuê mới, đại tá.\""),
            ["radio.aurel.hyperion.phase2"] = ("Aurel: \"All batteries, open fire. You will not like the next hour.\"", "Aurel: \"Mọi dàn pháo, khai hỏa. Các người sẽ không thích giờ tới.\""),
            ["radio.aurel.hyperion.phase3"] = ("Aurel: \"Hull breached on three decks. It still burns, Colonel.\"", "Aurel: \"Thủng vỏ ba tầng boong. Nó vẫn đốt được, đại tá.\""),
            // Play-test 14 wave R4: Hyperion's two mini-boss variants.
            ["unit.theia"] = ("Theia · Escort Carrier", "Theia · Tàu sân bay hộ tống"),
            ["short.theia"] = ("Theia", "Theia"),
            ["note.theia"] = ("Hyperion's escort carrier: a drone swarm from its ventral bay, drop pods, missile pods, 35 mm guns under the hull, a dorsal laser turret and two point-defence lasers. High and low on a fixed schedule.", "Tàu sân bay hộ tống của Hyperion: bầy drone từ khoang bụng, khoang đổ bộ, bệ tên lửa, pháo 35 mm dưới bụng, một tháp la-de trên lưng và hai la-de phòng thủ điểm. Đổi tầng cao và thấp theo lịch cố định."),
            ["guide.theia"] = (
                "[[Mini boss]] · escort carrier · Hyperion's sister ship\n" +
                "How it fights: never in orbit: high and low on a fixed schedule. Its [[drone bay]] launches a drone swarm and drops a landing pod every 30 s; two missile pods, twin 35 mm guns under the hull, a [[laser turret]] and two [[point-defence lasers]] that pick off missiles and aircraft.\n" +
                "Strong / weak: at high altitude only long-range anti-air and fighters reach it; low, every anti-air weapon does. Its drones hit tanks from above.\n" +
                "Tip: keep anti-air with your armour; break the drone bay in a low window.",
                "[[Mini boss]] · tàu sân bay hộ tống · tàu chị em của Hyperion\n" +
                "Cách đánh: không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. [[Khoang drone]] thả bầy drone và cứ 30 giây một khoang đổ bộ; hai bệ tên lửa, pháo đôi 35 mm dưới bụng, một [[tháp la-de]] và hai [[la-de phòng thủ điểm]] bắn hạ tên lửa và máy bay.\n" +
                "Mạnh / yếu: ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng thấp mọi vũ khí phòng không đều tới. Drone của nó đánh xe tăng từ trên xuống.\n" +
                "Mẹo: giữ phòng không đi cùng xe bọc thép; phá khoang drone trong lúc nó xuống thấp."),
            ["guide.parts.tip.theia"] = ("Tip: the [[drone bay]] launches the swarm and the pods; the [[point-defence lasers]] shoot your missiles down.", "Mẹo: [[khoang drone]] thả bầy drone và khoang đổ bộ; [[la-de phòng thủ điểm]] bắn hạ tên lửa của bạn."),
            ["radio.aurel.theia"] = ("Aurel: \"Theia, launch everything. Hyperion wants the sky clear.\"", "Aurel: \"Theia, phóng hết. Hyperion muốn bầu trời sạch bóng.\""),
            ["radio.aurel.theia.phase2"] = ("Aurel: \"Recover what is left and launch again.\"", "Aurel: \"Thu hồi những gì còn lại rồi phóng tiếp.\""),
            ["unit.coeus"] = ("Coeus · Gunship Cruiser", "Coeus · Tuần dương hạm pháo kích"),
            ["short.coeus"] = ("Coeus", "Coeus"),
            ["note.coeus"] = ("Hyperion's gunship: a twin 203 mm dorsal turret that hits like artillery, twin 76 mm guns under the hull, Spike missiles, no missile defence. High and low on a fixed schedule.", "Tàu pháo kích của Hyperion: tháp pháo đôi 203 mm trên lưng bắn như pháo binh, pháo đôi 76 mm dưới bụng, tên lửa Spike, không có phòng thủ tên lửa. Đổi tầng cao và thấp theo lịch cố định."),
            ["guide.coeus"] = (
                "[[Mini boss]] · gunship cruiser · Hyperion's sister ship\n" +
                "How it fights: never in orbit: high and low on a fixed schedule. Its [[main gun]], a twin 203 mm turret, shells your vehicles every few seconds; two twin 76 mm turrets fire down from its belly and two Spike launchers reach far.\n" +
                "Strong / weak: no protection system and no point defence: missiles reach it at every height. Its [[engines]] carry it: break them and it slows.\n" +
                "Tip: spread your vehicles out of a line; bring missiles.",
                "[[Mini boss]] · tuần dương hạm pháo kích · tàu chị em của Hyperion\n" +
                "Cách đánh: không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. [[Pháo chính]] là tháp pháo đôi 203 mm, cứ vài giây nã đạn vào xe của bạn; hai tháp pháo đôi 76 mm bắn xuống từ bụng và hai bệ Spike bắn xa.\n" +
                "Mạnh / yếu: không có hệ thống bảo vệ, không có la-de phòng thủ điểm: tên lửa với tới ở mọi tầng. [[Động cơ]] đưa nó đi: phá là nó chậm lại.\n" +
                "Mẹo: dàn xe ra, đừng xếp thành hàng; mang tên lửa theo."),
            ["guide.parts.tip.coeus"] = ("Tip: the [[main gun]] is its heaviest blow; break the [[engines]] to slow it.", "Mẹo: [[pháo chính]] là đòn nặng nhất; phá [[động cơ]] để nó chậm lại."),
            ["radio.aurel.coeus"] = ("Aurel: \"Coeus, find their column and walk your fire along it.\"", "Aurel: \"Coeus, tìm đoàn xe của chúng và rải hỏa lực dọc theo nó.\""),
            ["radio.aurel.coeus.phase2"] = ("Aurel: \"All shells to the main turret. Everything else can wait.\"", "Aurel: \"Dồn đạn cho tháp pháo chính. Mọi thứ khác chờ đó.\""),
            ["unit.nyx"] = ("Nyx · Stealth Destroyer", "Nyx · Tàu khu trục tàng hình"),
            ["short.nyx"] = ("Nyx", "Nyx"),
            ["note.nyx"] = ("A wave-piercing, pyramid-topped destroyer: a 155 mm gun turret firing every 8 s, hidden until it fires or a radar or drone lights it.", "Tàu khu trục mũi xuyên sóng, thượng tầng hình kim tự tháp: tháp pháo 155 mm bắn mỗi 8 giây, ẩn mình đến khi bắn hoặc bị radar hay drone soi."),
            ["guide.nyx"] = (
                "[[Mini boss]] · stealth destroyer · unseen until it fires\n" +
                "How it fights: a stand-in hull for now (a small Leviathan). A 155 mm gun turret (AGS) fires two shells every 8 s, two [[CIWS]] take missiles and drones, an anti-ship missile follows. It is [[stealthy]]: seen only close up or just after it fires.\n" +
                "Strong / weak: hard to see; thin for its size.\n" +
                "Tip: keep radar or a drone over the water so it is seen; break the [[CIWS]] before sending missiles.",
                "[[Mini boss]] · tàu khu trục tàng hình · chỉ lộ khi bắn\n" +
                "Cách đánh: tạm dùng thân Leviathan thu nhỏ. Tháp pháo 155 mm (AGS) bắn hai phát mỗi 8 giây, hai [[CIWS]] chặn tên lửa và drone, rồi tới tên lửa chống hạm. Nó [[tàng hình]]: chỉ thấy ở gần hoặc ngay sau khi bắn.\n" +
                "Mạnh / yếu: khó thấy; mỏng so với kích cỡ.\n" +
                "Mẹo: giữ radar hoặc drone trên mặt nước để thấy nó; phá [[CIWS]] trước khi dùng tên lửa."),
            ["guide.parts.tip.nyx"] = ("Tip: the [[CIWS]] stop your missiles; the missile cells carry its anti-ship missile.", "Mẹo: [[CIWS]] chặn tên lửa của bạn; ống phóng mang tên lửa chống hạm của nó."),
            ["radio.kessler.nyx"] = ("Kessler: \"Nyx, run silent. Speak only when you fire.\"", "Kessler: \"Nyx, chạy im lặng. Chỉ lên tiếng khi khai hỏa.\""),
            ["unit.hydra"] = ("Hydra · Attack Submarine", "Hydra · Tàu ngầm tấn công"),
            ["short.hydra"] = ("Hydra", "Hydra"),
            ["note.hydra"] = ("A small attack submarine with vertical launch tubes along its back: it surfaces to fire cruise missiles, and dives and surfaces faster than Typhon.", "Tàu ngầm tấn công nhỏ có ống phóng dọc trên lưng: nổi lên phóng tên lửa hành trình, lặn và nổi nhanh hơn Typhon."),
            ["guide.hydra"] = (
                "[[Mini boss]] · attack submarine · surfaces to strike\n" +
                "How it fights: Typhon's smaller, quicker sister (a deck gun and launch doors). It dives and surfaces on a short schedule, fires only when up, and sends a cruise missile every 16 s.\n" +
                "Strong / weak: out of reach while submerged; a thin hull.\n" +
                "Tip: wait for the bubbles; break the [[launch doors]] to stop the missiles.",
                "[[Mini boss]] · tàu ngầm tấn công · nổi lên để đánh\n" +
                "Cách đánh: chiếc nhỏ và nhanh hơn cùng lớp Typhon (pháo boong và cửa ống phóng). Nó lặn rồi nổi theo lịch ngắn, chỉ bắn khi nổi, và phóng tên lửa hành trình mỗi 16 giây.\n" +
                "Mạnh / yếu: lúc lặn không đánh tới được; thân mỏng.\n" +
                "Mẹo: chờ bong bóng; phá [[cửa ống phóng]] để chặn tên lửa."),
            ["guide.parts.tip.hydra"] = ("Tip: the [[launch doors]] carry its missiles; the deck gun only shoots when it is up.", "Mẹo: [[cửa ống phóng]] mang tên lửa của nó; pháo boong chỉ bắn khi nổi."),
            ["radio.hung.hydra"] = ("{@lyhan}: \"Hydra, rise and release. Cut one head, there are six more.\"", "{@lyhan}: \"Hydra, nổi lên và thả. Chặt một đầu, còn sáu đầu nữa.\""),
        };
    }
}
