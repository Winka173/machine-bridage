using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 28: the words of the tactics (H.4: name, core behaviour, strong and weak when, counters, unlock), the HUD
    /// hint line (B.7), tactic-switch lines (H.8), tower targeting modes (E.1), fire stances (H.9), the upkeep factor and
    /// pressure tiers (I.2, I.6), and the AI viewer's "VÌ SAO" words (J.2), in English and Vietnamese. The tactics'
    /// Vietnamese texts are the research sheet's.
    /// </summary>
    public static class TacticText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- screens
            ["tactic.title"] = ("Tactic", "Chiến thuật"),
            ["tactic.pickTitle"] = ("Choose a tactic", "Chọn chiến thuật"),
            ["tactic.core"] = ("Core behaviour", "Hành vi cốt lõi"),
            ["tactic.strong"] = ("Strong when", "Mạnh khi"),
            ["tactic.weak"] = ("Weak when", "Yếu khi"),
            ["tactic.buys"] = ("Buys first", "Ưu tiên mua"),
            ["tactic.mix"] = ("Force mix (CP)", "Tỷ lệ lực lượng (CP)"),
            ["tactic.counters"] = ("Counters: {list}", "Khắc chế được: {list}"),
            ["tactic.counteredBy"] = ("Countered by: {list}", "Bị khắc chế bởi: {list}"),
            ["tactic.suits"] = ("Suits your commander", "Hợp với chỉ huy của bạn"),
            ["tactic.unlock.chapter"] = ("Opens in chapter {chapter}", "Mở ở chương {chapter}"),
            ["tactic.unlock.interlude"] = ("Opens in Interlude {number}", "Mở ở Xen kẽ {number}"),
            ["tactic.general"] = ("Enemy general's favourite: {tactic}", "Chiến thuật ưa thích của tướng địch: {tactic}"),
            ["tactic.enemyNow"] = ("Enemy tactic: {tactic}", "Chiến thuật địch: {tactic}"),
            ["tactic.enemyUnknown"] = ("Enemy tactic: unknown (scout them)", "Chiến thuật địch: chưa rõ (cần trinh sát)"),
            ["tactic.switch"] = ("Switch tactic", "Đổi chiến thuật"),
            ["tactic.cooldown"] = ("Ready in {seconds} s", "Sẵn sàng sau {seconds} giây"),
            ["tactic.transition"] = ("Regrouping for the new tactic", "Đang gom quân theo chiến thuật mới"),
            ["tactic.squad"] = ("Squad tactic", "Chiến thuật của đội"),
            ["tactic.squadShared"] = ("Side's tactic", "Theo chiến thuật chung"),

            ["tactic.group.Armour"] = ("Tanks, heavy", "Tăng, hạng nặng"),
            ["tactic.group.Light"] = ("Light, IFVs", "Xe nhẹ, xe bộ binh"),
            ["tactic.group.AntiTank"] = ("Tank hunters, AT drones", "Diệt tăng, drone chống tăng"),
            ["tactic.group.Artillery"] = ("Artillery, rockets", "Pháo binh, tên lửa đất đối đất"),
            ["tactic.group.AntiAir"] = ("Anti-air", "Phòng không"),
            ["tactic.group.Helicopter"] = ("Helicopters", "Trực thăng"),
            ["tactic.group.Plane"] = ("Aircraft", "Máy bay"),
            ["tactic.group.Support"] = ("Support", "Hỗ trợ"),

            // ---------------------------------------------------------------- the 16 tactics
            ["tactic.balanced.name"] = ("Balanced", "Cân bằng"),
            ["tactic.balanced.core"] = ("Combined arms, no leaning either way.", "Phối hợp nhiều vai trò, không thiên lệch."),
            ["tactic.balanced.strong"] = ("Every situation, at a middling level.", "Mọi tình huống ở mức vừa."),
            ["tactic.balanced.weak"] = ("Stands out nowhere.", "Không nổi trội ở đâu."),

            ["tactic.blitz.name"] = ("Blitz", "Tấn công chớp nhoáng"),
            ["tactic.blitz.core"] = ("Keeps the momentum and strikes before the enemy can dig in.", "Giữ đà tiến, đánh trước khi địch kịp dựng phòng tuyến."),
            ["tactic.blitz.strong"] = ("The enemy has no line yet; short maps.", "Địch chưa kịp dựng phòng tuyến; map ngắn."),
            ["tactic.blitz.weak"] = ("Defence in depth, ambushes, minefields.", "Gặp phòng thủ chiều sâu, phục kích, bãi mìn."),

            ["tactic.firepower.name"] = ("Overwhelming Fire", "Hỏa lực áp đảo"),
            ["tactic.firepower.core"] = ("Artillery clears the way, then the advance.", "Pháo dọn đường rồi mới tiến."),
            ["tactic.firepower.strong"] = ("The enemy stands still, many structures.", "Địch đứng yên, nhiều công trình."),
            ["tactic.firepower.weak"] = ("The enemy moves fast or spreads out.", "Địch tiến nhanh hoặc phân tán."),

            ["tactic.depth.name"] = ("Defence in Depth", "Phòng thủ chiều sâu"),
            ["tactic.depth.core"] = ("Absorbs the attack over several lines, then strikes back.", "Hấp thụ đợt tấn công qua nhiều tuyến, rồi phản công."),
            ["tactic.depth.strong"] = ("Defend mode, long maps, layered bases.", "Chế độ Phòng thủ, map dài, căn cứ nhiều lớp."),
            ["tactic.depth.weak"] = ("Constant long-range artillery.", "Đối thủ dùng pháo binh tầm xa liên tục."),

            ["tactic.encircle.name"] = ("Encirclement", "Bao vây"),
            ["tactic.encircle.core"] = ("Hits flank and rear from two directions at once.", "Đánh hai hướng cùng lúc vào hông và sau."),
            ["tactic.encircle.strong"] = ("The enemy is bunched in one place; wide maps.", "Địch dồn ở một chỗ, map rộng."),
            ["tactic.encircle.weak"] = ("A breakthrough on one squad while the army is split.", "Địch tập trung đột phá vào một đội khi quân ta bị chia."),

            ["tactic.bounding.name"] = ("Bounding Overwatch", "Yểm hộ luân phiên"),
            ["tactic.bounding.core"] = ("Slow and safe: one group always covers the other.", "Tiến chậm, an toàn, một nhóm luôn yểm hộ."),
            ["tactic.bounding.strong"] = ("Unknown ground, ambushes ahead.", "Tiến qua vùng chưa rõ, có phục kích."),
            ["tactic.bounding.weak"] = ("Speed matters; artillery on the standing group.", "Cần tốc độ, đối thủ dùng pháo binh vào nhóm đứng yên."),

            ["tactic.ambush.name"] = ("Ambush", "Phục kích"),
            ["tactic.ambush.core"] = ("Hidden and disciplined: one volley together.", "Ẩn và kỷ luật hỏa lực, phát đầu đồng loạt."),
            ["tactic.ambush.strong"] = ("The enemy rushes in without scouts.", "Địch tiến nhanh, không trinh sát."),
            ["tactic.ambush.weak"] = ("Scouts, UAV sweeps, bounding overwatch.", "Địch có trinh sát, UAV quét, yểm hộ luân phiên."),

            ["tactic.hit_and_run.name"] = ("Hit and Run", "Bắn và chạy"),
            ["tactic.hit_and_run.core"] = ("Fights at full reach and never lets the enemy close.", "Giữ cự ly tối đa, không để địch áp sát."),
            ["tactic.hit_and_run.strong"] = ("Faster and longer-ranged than the enemy.", "Đội nhanh hơn, tầm xa hơn địch."),
            ["tactic.hit_and_run.weak"] = ("A faster enemy, aircraft, narrow maps.", "Địch nhanh hơn, có máy bay, map hẹp."),

            ["tactic.breakthrough.name"] = ("Breakthrough", "Tập trung đột phá"),
            ["tactic.breakthrough.core"] = ("Nearly everything on one point to punch through.", "Dồn gần hết quân vào một điểm để chọc thủng."),
            ["tactic.breakthrough.strong"] = ("A thinly spread enemy.", "Địch dàn mỏng."),
            ["tactic.breakthrough.weak"] = ("Many splash weapons; attacked from both sides.", "Địch có nhiều vũ khí bắn lan, bị bao vây hai bên."),

            ["tactic.dispersal.name"] = ("Dispersal", "Phân tán"),
            ["tactic.dispersal.core"] = ("Spreads wide to blunt splash and super weapons.", "Dàn rộng để vô hiệu bắn lan và siêu vũ khí."),
            ["tactic.dispersal.strong"] = ("Bosses, artillery, bombs.", "Gặp boss, pháo binh, bom."),
            ["tactic.dispersal.weak"] = ("Head-on against a tight group.", "Đánh trực diện với đội gom chặt."),

            ["tactic.air_superiority.name"] = ("Air Superiority", "Ưu thế trên không"),
            ["tactic.air_superiority.core"] = ("Wins the sky first, then sends the ground forces.", "Tạo cửa sổ trên không rồi mới đưa đội mặt đất."),
            ["tactic.air_superiority.strong"] = ("The enemy relies on aircraft.", "Địch dựa vào máy bay."),
            ["tactic.air_superiority.weak"] = ("The enemy has no aircraft (wasted CP).", "Địch không có máy bay (phí CP)."),

            ["tactic.sead.name"] = ("SEAD First", "Chế áp phòng không trước"),
            ["tactic.sead.core"] = ("Hunts the anti-air before anything else.", "Săn phòng không trước mọi thứ."),
            ["tactic.sead.strong"] = ("Heavy enemy anti-air, strong own air power.", "Địch có nhiều phòng không, ta mạnh về không quân."),
            ["tactic.sead.weak"] = ("Little enemy anti-air.", "Địch ít phòng không."),

            ["tactic.attrition.name"] = ("Attrition", "Tiêu hao"),
            ["tactic.attrition.core"] = ("Trades ground for time and harasses from range.", "Đổi lãnh thổ lấy thời gian, quấy rối từ xa."),
            ["tactic.attrition.strong"] = ("Long battles, Endless, Defend.", "Trận dài, Vô tận, Phòng thủ."),
            ["tactic.attrition.weak"] = ("Timed objectives, scored Deathmatch.", "Mục tiêu có hạn giờ, Tử chiến tính điểm."),

            ["tactic.decapitation.name"] = ("Decapitation", "Săn đầu"),
            ["tactic.decapitation.core"] = ("Strikes deep at support, artillery and command.", "Đánh sâu vào hỗ trợ, pháo, chỉ huy."),
            ["tactic.decapitation.strong"] = ("The enemy leans on support and guns.", "Địch dựa vào hỗ trợ và pháo."),
            ["tactic.decapitation.weak"] = ("A strong front line blocks the way.", "Địch có tiền tuyến mạnh chặn đường."),

            ["tactic.base_defence.name"] = ("Base Defence", "Bảo vệ căn cứ"),
            ["tactic.base_defence.core"] = ("Holds around the base and its towers.", "Giữ quanh căn cứ và tháp."),
            ["tactic.base_defence.strong"] = ("Defend, the weekly Fortress.", "Phòng thủ, Pháo đài tuần."),
            ["tactic.base_defence.weak"] = ("Modes with points away from the base.", "Chế độ giữ cứ điểm ngoài căn cứ."),

            ["tactic.all_out.name"] = ("All-Out Assault", "Tổng tấn công"),
            ["tactic.all_out.core"] = ("Saves up, then throws one big wave at once.", "Để dành rồi tung một đợt lớn cùng lúc."),
            ["tactic.all_out.strong"] = ("The enemy has no time to change tactic.", "Địch chưa kịp đổi chiến thuật."),
            ["tactic.all_out.weak"] = ("Hit early, before the CP is saved.", "Bị đánh sớm trước khi đủ CP."),

            // ---------------------------------------------------------------- switching (H.6, H.8)
            ["tactic.line.switched"] = ("Switching to {tactic}. Squads regroup first.", "Chuyển sang {tactic}. Các đội gom lại trước."),
            ["tactic.line.enemySwitched"] = ("Scouts report: the enemy switched to {tactic}.", "Trinh sát báo: địch đổi sang {tactic}."),
            ["tactic.line.cooldown"] = ("Not yet: the last switch was too recent.", "Chưa được: vừa đổi chiến thuật."),

            // ---------------------------------------------------------------- hint line (B.7)
            ["aihint.bigAttack"] = ("A big attack is coming down: clear the ring.", "Đòn lớn sắp rơi: rời khỏi vòng cảnh báo."),
            ["aihint.strike"] = ("Enemy fire support incoming.", "Hỏa lực yểm trợ của địch sắp tới."),
            ["aihint.airInbound"] = ("Enemy aircraft inbound.", "Máy bay địch đang tới."),
            ["aihint.overwhelmed"] = ("A squad is outmatched.", "Một đội đang bị áp đảo."),
            ["aihint.needAntiAir"] = ("Short of anti-air against their aircraft.", "Thiếu phòng không trước máy bay địch."),
            ["aihint.needAntiTank"] = ("Short of anti-tank against their armour.", "Thiếu chống tăng trước xe tăng địch."),
            ["aihint.enemyArtillery"] = ("Enemy artillery just showed itself.", "Pháo địch vừa lộ vị trí."),
            ["aihint.opportunity"] = ("A valuable target is in sight.", "Có mục tiêu giá trị trong tầm nhìn."),
            ["aihint.window"] = ("An opening: their defence has a gap.", "Có sơ hở: phòng tuyến địch vừa hở."),
            ["aihint.losingPoint"] = ("A point is under pressure.", "Một cứ điểm đang bị ép."),
            ["aihint.stuck"] = ("A squad is stuck.", "Một cụm quân đang kẹt."),
            ["aihint.settings"] = ("AI hints", "Gợi ý của AI"),

            // ---------------------------------------------------------------- tower modes (E.1)
            ["tower.mode.title"] = ("Targeting", "Chọn mục tiêu"),
            ["tower.mode.Default"] = ("Default", "Mặc định"),
            ["tower.mode.Nearest"] = ("Nearest", "Gần nhất"),
            ["tower.mode.Strongest"] = ("Strongest", "Mạnh nhất"),
            ["tower.mode.Weakest"] = ("Weakest", "Yếu nhất"),
            ["tower.mode.Lead"] = ("Leading enemy", "Đầu đoàn"),
            ["tower.mode.AirFirst"] = ("Aircraft first", "Máy bay trước"),
            ["tower.mode.Cluster"] = ("Biggest cluster", "Cụm đông nhất"),
            ["tower.mode.ArtilleryFirst"] = ("Artillery first", "Pháo binh trước"),
            ["tower.mode.ShieldKey"] = ("Rounds at key structures", "Đạn bay vào công trình quan trọng nhất"),
            ["tower.mode.NearestRound"] = ("Nearest round", "Đạn gần nhất"),
            ["tower.mode.BiggestAircraft"] = ("Biggest aircraft", "Máy bay lớn nhất"),
            ["tower.mode.MissilesFirst"] = ("Missiles first", "Tên lửa trước"),
            ["tower.mode.None"] = ("Does not fire", "Không bắn"),

            // ---------------------------------------------------------------- fire stances (H.9)
            ["fire.stance.title"] = ("Fire stance", "Thế giữ lửa"),
            ["fire.stance.Free"] = ("Fire at will", "Bắn tự do"),
            ["fire.stance.Confirmed"] = ("Confirmed targets only", "Chỉ bắn mục tiêu xác nhận"),
            ["fire.stance.HoldFire"] = ("Hold fire", "Giữ lửa"),

            // ---------------------------------------------------------------- economy (I.2, I.6, I.7)
            ["upkeep.factor"] = ("Upkeep: income x{factor}", "Phí duy trì: thu nhập x{factor}"),
            ["upkeep.why"] = ("A big army earns less CP.", "Quân càng đông, CP càng ít."),
            ["pressure.tier1"] = ("Points are worth more while nobody fights.", "Cứ điểm tăng giá trị khi không ai giao tranh."),
            ["pressure.tier2"] = ("A supply crate drops in the middle.", "Kho chiến lợi phẩm rơi ở vùng giữa."),
            ["pressure.tier3"] = ("Artillery shells the side sitting back.", "Pháo kích vào bên đang thụ động."),
            ["pressure.tier4"] = ("Both armies are spotted: fight!", "Hai bên bị lộ vị trí: giao chiến!"),
            ["pressure.final"] = ("Final phase: points count double.", "Pha cuối: điểm từ cứ điểm x2."),

            // ---------------------------------------------------------------- AI viewer (J), internal
            ["aiview.title"] = ("AI viewer", "Công cụ xem AI"),
            ["aiview.why"] = ("Why", "Vì sao"),
            ["aiview.runnerUp"] = ("Runner-up: {action} {score}", "Đứng thứ hai: {action} {score}"),
            ["aiview.churn"] = ("Changing its mind too often", "Đổi quyết định quá nhiều"),
            ["aiview.layer.influence"] = ("Influence", "Ảnh hưởng"),
            ["aiview.layer.threat"] = ("Threat", "Mối đe dọa"),
            ["aiview.layer.confidence"] = ("Information age", "Tuổi thông tin"),
            ["aiview.layer.front"] = ("Front and chokepoints", "Tiền tuyến và điểm nghẽn"),
            ["aiview.layer.events"] = ("Events", "Sự kiện"),
            ["aiview.layer.squads"] = ("Squads", "Đội"),
            ["aiview.layer.economy"] = ("Upkeep and income", "Phí duy trì và thu nhập"),

            ["squad.state.Travel"] = ("Travel", "Di chuyển"),
            ["squad.state.Approach"] = ("Approach", "Tiếp cận"),
            ["squad.state.Combat"] = ("Combat", "Giao chiến"),
            ["squad.state.Overwatch"] = ("Overwatch", "Yểm hộ"),
            ["squad.state.Flank"] = ("Flank", "Đánh sườn"),
            ["squad.state.Hold"] = ("Hold", "Giữ"),
            ["squad.state.Regroup"] = ("Regroup", "Gom quân"),
            ["squad.action.Attack"] = ("Attack", "Tấn công"),
            ["squad.action.Hold"] = ("Hold", "Giữ"),
            ["squad.action.FlankLeft"] = ("Flank left", "Đánh sườn trái"),
            ["squad.action.FlankRight"] = ("Flank right", "Đánh sườn phải"),
            ["squad.action.Overwatch"] = ("Overwatch", "Yểm hộ"),
            ["squad.action.Reposition"] = ("Reposition", "Đổi vị trí"),
            ["squad.action.Support"] = ("Support", "Hỗ trợ đội bạn"),
            ["squad.action.Join"] = ("Join", "Nhập đội"),
            ["squad.action.Regroup"] = ("Regroup", "Gom quân"),

            ["why.ratio"] = ("Strength against the enemy", "Sức mạnh so với địch"),
            ["why.undefended"] = ("No enemy known there", "Chưa thấy địch ở đó"),
            ["why.window"] = ("Attack window", "Cửa sổ tấn công"),
            ["why.highValue"] = ("Valuable target", "Mục tiêu giá trị"),
            ["why.primary"] = ("Main effort", "Hướng chính"),
            ["why.counterattack"] = ("Strong enough to strike back", "Đủ mạnh để phản công"),
            ["why.holdTactic"] = ("The tactic holds", "Chiến thuật giữ"),
            ["why.lowConfidence"] = ("Old information", "Thông tin cũ"),
            ["why.routeThreat"] = ("Threat on the way", "Mối đe dọa trên đường"),
            ["why.notGathered"] = ("Squad not gathered", "Đội chưa gom đủ"),
            ["why.transition"] = ("Tactic changing", "Đang đổi chiến thuật"),
            ["why.waitAir"] = ("Waiting for the sky", "Chờ trên không"),
            ["why.artilleryPrep"] = ("Waiting for the barrage", "Chờ pháo dọn đường"),
            ["why.holdTask"] = ("Ordered to hold", "Nhiệm vụ giữ"),
            ["why.ambush"] = ("Ambush", "Phục kích"),
            ["why.waiting"] = ("Waiting for friends", "Chờ đồng đội"),
            ["why.losingPoint"] = ("Losing the point", "Đang mất cứ điểm"),
            ["why.inSplash"] = ("Standing in splash", "Đứng trong vùng bắn lan"),
            ["why.weakFlank"] = ("Weak enemy flank", "Sườn địch yếu"),
            ["why.mobile"] = ("Mobile squad", "Đội cơ động"),
            ["why.flankTactic"] = ("The tactic flanks", "Chiến thuật ưa đánh sườn"),
            ["why.pincer"] = ("Pincer side", "Hướng bao vây"),
            ["why.cohesionRisk"] = ("Risk of losing cohesion", "Rủi ro mất gắn kết"),
            ["why.reserveThatWay"] = ("Enemy reserve that way", "Quân dự bị địch ở hướng đó"),
            ["why.unknownGround"] = ("Friends cross unknown ground", "Đội bạn qua vùng chưa rõ"),
            ["why.bounding"] = ("Bounding overwatch", "Yểm hộ luân phiên"),
            ["why.fallbackLine"] = ("Back to the next line", "Chuyển về tuyến sau"),
            ["why.underFire"] = ("Under fire here", "Đang bị bắn ở đây"),
            ["why.focusing"] = ("Focus fire working", "Đang dồn hỏa lực hiệu quả"),
            ["why.friendLosing"] = ("A friendly squad is losing", "Đội bạn đang bất lợi"),
            ["why.free"] = ("Nothing to do here", "Đang rảnh"),
            ["why.leavesTask"] = ("Leaves the main task", "Rời nhiệm vụ chính"),
            ["why.belowMinimum"] = ("Squad too small", "Đội dưới số xe tối thiểu"),
            ["why.scattered"] = ("Squad scattered", "Đội phân tán"),
            ["why.tacticChanged"] = ("Tactic just changed", "Vừa đổi chiến thuật"),
        };

        /// <summary>A tactic's name in the current language.</summary>
        public static string Name(TacticDef t) => Strings.Get("tactic." + t.Id + ".name");

        public static string Core(TacticDef t) => Strings.Get("tactic." + t.Id + ".core");

        public static string Strong(TacticDef t) => Strings.Get("tactic." + t.Id + ".strong");

        public static string Weak(TacticDef t) => Strings.Get("tactic." + t.Id + ".weak");

        /// <summary>"Opens in chapter 3" (empty for a tactic open from the start).</summary>
        public static string Unlock(TacticDef t) =>
            t.Interlude > 0 ? Strings.Format("tactic.unlock.interlude", ("number", t.Interlude))
            : t.Chapter > 1 ? Strings.Format("tactic.unlock.chapter", ("chapter", t.Chapter))
            : "";

        /// <summary>The tactics this one counters, by name, joined.</summary>
        public static string Counters(AiBehaviour data, TacticDef t) => Strings.Format("tactic.counters", ("list", Join(data, t.Counters)));

        public static string CounteredBy(AiBehaviour data, TacticDef t) => Strings.Format("tactic.counteredBy", ("list", Join(data, t.CounteredBy)));

        private static string Join(AiBehaviour data, IReadOnlyList<string> ids)
        {
            var names = new List<string>();
            foreach (var id in ids)
                if (data.HasTactic(id)) names.Add(Name(data.Tactic(id)));
            return names.Count > 0 ? string.Join(", ", names) : "-";
        }
    }
}
