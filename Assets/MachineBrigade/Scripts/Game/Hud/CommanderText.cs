using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 22 F: the commanders' words in English and Vietnamese (prompt 21's rules: named placeholders, names as
    /// <c>{@token}</c>). A strength's and a weakness's numbers come from the commander's data (<see cref="Values"/>), so
    /// the text follows the balance. A story character's name is the story's own (<c>char.&lt;portrait&gt;.name</c>).
    /// </summary>
    public static class CommanderText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            // ---------------------------------------------------------------- screens
            ["cmdr.title"] = ("Commander", "Chỉ huy"),
            ["cmdr.pickTitle"] = ("Choose a commander", "Chọn chỉ huy"),
            ["cmdr.sub"] = ("One passive strength and one small weakness, on for the whole battle.", "Một điểm mạnh thụ động và một điểm yếu nhỏ, có tác dụng suốt trận."),
            ["cmdr.strength"] = ("Strength", "Điểm mạnh"),
            ["cmdr.weakness"] = ("Weakness", "Điểm yếu"),
            ["cmdr.suits"] = ("Suits: {style}", "Hợp với: {style}"),
            ["cmdr.unlock.chapter"] = ("Opens in chapter {chapter}", "Mở ở chương {chapter}"),
            ["cmdr.unlock.after"] = ("Opens once chapter {chapter} is done", "Mở sau khi xong chương {chapter}"),
            ["cmdr.unlock.interlude"] = ("Opens in Interlude {number}", "Mở ở Xen kẽ {number}"),
            ["cmdr.chosen"] = ("In command", "Đang chỉ huy"),
            ["cmdr.choose"] = ("Take command", "Nhận chỉ huy"),
            ["cmdr.forced"] = ("This mission is led by {name}.", "Nhiệm vụ này do {name} chỉ huy."),
            ["cmdr.general"] = ("Enemy general: {name}", "Tướng địch: {name}"),
            ["cmdr.yours"] = ("Your commander: {name}", "Chỉ huy của bạn: {name}"),
            ["cmdr.change"] = ("Change commander", "Đổi chỉ huy"),
            ["cmdr.none"] = ("None.", "Không có."),
            ["cmdr.line"] = ("{label}: {text}", "{label}: {text}"),
            ["cmdr.family.Combat"] = ("Combat", "Chiến đấu"),
            ["cmdr.family.Economy"] = ("Economy", "Kinh tế"),
            ["cmdr.family.General"] = ("Enemy general", "Tướng địch"),
            ["cmdr.dossier.tab"] = ("Commanders", "Chỉ huy"),
            ["cmdr.dossier.yours"] = ("Your commanders", "Chỉ huy phe ta"),
            ["cmdr.dossier.generals"] = ("Enemy generals", "Tướng địch"),
            ["cmdr.dossier.notFaced"] = ("Not faced yet.", "Chưa đối đầu."),
            ["cmdr.hud"] = ("Commander {name}: tap for the strength and weakness", "Chỉ huy {name}: chạm để xem điểm mạnh và điểm yếu"),
            ["cmdr.sandbox"] = ("Commander", "Chỉ huy"),
            ["cmdr.sandbox.none"] = ("No commander", "Không có chỉ huy"),
            ["cmdr.quote"] = ("{name}: {line}", "{name}: {line}"),

            // ---------------------------------------------------------------- deck styles
            ["cmdr.style.Balanced"] = ("Balanced decks", "Bộ bài cân bằng"),
            ["cmdr.style.Sustain"] = ("Engineers and a base that holds", "Công binh và căn cứ vững"),
            ["cmdr.style.Air"] = ("Aircraft and helicopters", "Máy bay và trực thăng"),
            ["cmdr.style.Recon"] = ("Scouts and marked targets", "Trinh sát và đánh dấu mục tiêu"),
            ["cmdr.style.Drones"] = ("Drones", "Drone"),
            ["cmdr.style.Blitz"] = ("Fast vehicles, early pushes", "Xe nhanh, tấn công sớm"),
            ["cmdr.style.Fortress"] = ("Towers and field towers", "Tháp và tháp dã chiến"),
            ["cmdr.style.Artillery"] = ("Artillery", "Pháo binh"),
            ["cmdr.style.LongGame"] = ("Long battles", "Trận dài"),
            ["cmdr.style.Points"] = ("Taking and holding points", "Chiếm và giữ cứ điểm"),
            ["cmdr.style.Swarm"] = ("Many cheap vehicles", "Nhiều xe rẻ"),
            ["cmdr.style.Heavy"] = ("A few dear, heavy vehicles", "Ít xe đắt, hạng nặng"),
            ["cmdr.style.Attrition"] = ("Trading kills", "Đổi quân, hạ nhiều địch"),
            ["cmdr.style.Hoard"] = ("Saving up for big buys", "Tích CP để mua xe lớn"),

            // ---------------------------------------------------------------- the new people (the story's own keep char.<id>.name)
            ["cmdr.mendez.name"] = ("Captain {@mendez}", "Đại úy {@mendez}"),
            ["cmdr.dahl.name"] = ("Major {@dahl}", "Thiếu tá {@dahl}"),
            ["cmdr.brenn.name"] = ("Major {@brenn}", "Thiếu tá {@brenn}"),
            ["cmdr.adler.name"] = ("Captain {@adler}", "Đại úy {@adler}"),
            ["cmdr.varro.name"] = ("Captain {@varro}", "Đại úy {@varro}"),
            ["cmdr.reyn.name"] = ("Colonel {@reyn}", "Đại tá {@reyn}"),
            ["cmdr.quist.name"] = ("Sergeant Major {@quist}", "Thượng sĩ nhất {@quist}"),
            ["cmdr.okoye.name"] = ("Captain {@okoye}", "Đại úy {@okoye}"),
            ["cmdr.mendez.role"] = ("Airborne assault, the rapid-reaction force", "Đột kích đường không, lực lượng phản ứng nhanh"),
            ["cmdr.dahl.role"] = ("Brigade artillery", "Pháo binh lữ đoàn"),
            ["cmdr.brenn.role"] = ("The brigade's quartermaster", "Sĩ quan hậu cần lữ đoàn"),
            ["cmdr.adler.role"] = ("Forward recon and point capture", "Trinh sát tiền phương, chiếm cứ điểm"),
            ["cmdr.varro.role"] = ("Motor pool and mass reinforcements", "Đội xe và tiếp viện số đông"),
            ["cmdr.reyn.role"] = ("Heavy armour reserve", "Thiết giáp hạng nặng dự bị"),
            ["cmdr.quist.role"] = ("Salvage and recovery", "Thu hồi và tận dụng chiến lợi phẩm"),
            ["cmdr.okoye.role"] = ("The brigade's treasurer", "Quản lý ngân quỹ lữ đoàn"),
            ["cmdr.mendez.bio"] = ("{@mendez} jumps with the first wave and is on the ground before the enemy knows the drop has started.",
                "{@mendez} nhảy cùng đợt đầu và đã tiếp đất trước khi địch biết đợt thả dù bắt đầu."),
            ["cmdr.dahl.bio"] = ("{@dahl} counts in grid squares and seconds of flight. He has never seen most of what his guns hit.",
                "{@dahl} tính bằng ô tọa độ và giây bay của đạn. Phần lớn những gì pháo của anh bắn trúng, anh chưa từng nhìn thấy."),
            ["cmdr.brenn.bio"] = ("{@brenn} keeps the brigade's books. Every shell has a price, and he knows it.",
                "{@brenn} giữ sổ sách của lữ đoàn. Mỗi quả đạn đều có giá, và ông biết rõ giá đó."),
            ["cmdr.adler.bio"] = ("{@adler} plants a flag on every hill he takes, and pays his crews from what the hill brings in.",
                "{@adler} cắm cờ trên mọi ngọn đồi chiếm được và trả lương cho kíp xe bằng những gì ngọn đồi mang lại."),
            ["cmdr.varro.bio"] = ("{@varro} never waits for the perfect tank. She sends ten good-enough ones instead.",
                "{@varro} không bao giờ chờ chiếc xe tăng hoàn hảo. Cô gửi mười chiếc đủ tốt thay vào đó."),
            ["cmdr.reyn.bio"] = ("{@reyn} would rather field three machines he trusts than a dozen he does not.",
                "{@reyn} thà ra trận với ba cỗ máy ông tin tưởng còn hơn một tá cỗ máy ông không tin."),
            ["cmdr.quist.bio"] = ("{@quist} walks the field after every battle. What the enemy leaves behind, she turns into the next attack.",
                "{@quist} đi khắp chiến trường sau mỗi trận. Những gì địch bỏ lại, cô biến thành đợt tấn công tiếp theo."),
            ["cmdr.okoye.bio"] = ("{@okoye} lets the purse fill before she spends it, then spends it all at once.",
                "{@okoye} để ngân quỹ đầy rồi mới tiêu, và tiêu cùng một lúc."),

            // ---------------------------------------------------------------- call signs (a title where there is none)
            ["cmdr.kade.call"] = ("{@iron}", "{@iron}"),
            ["cmdr.lind.call"] = ("Chief engineer", "Kỹ sư trưởng"),
            ["cmdr.reyes.call"] = ("{@hawk}", "{@hawk}"),
            ["cmdr.kerr.call"] = ("Intelligence", "Tình báo"),
            ["cmdr.venn.call"] = ("{@queen}", "{@queen}"),
            ["cmdr.mendez.call"] = ("{@rush}", "{@rush}"),
            ["cmdr.brandt.call"] = ("{@bulwark}", "{@bulwark}"),
            ["cmdr.dahl.call"] = ("{@longshot}", "{@longshot}"),
            ["cmdr.brenn.call"] = ("{@ledger}", "{@ledger}"),
            ["cmdr.adler.call"] = ("{@flag}", "{@flag}"),
            ["cmdr.varro.call"] = ("{@tide}", "{@tide}"),
            ["cmdr.reyn.call"] = ("{@crown}", "{@crown}"),
            ["cmdr.quist.call"] = ("{@magpie}", "{@magpie}"),
            ["cmdr.okoye.call"] = ("{@vault}", "{@vault}"),
            ["cmdr.gen.brandt.call"] = ("{@bulwark}", "{@bulwark}"),
            ["cmdr.gen.varga.call"] = ("{@anvil}", "{@anvil}"),
            ["cmdr.gen.orlov.call"] = ("{@winter}", "{@winter}"),
            ["cmdr.gen.kessler.call"] = ("{@maelstrom}", "{@maelstrom}"),
            ["cmdr.gen.sen.call"] = ("{@queen}", "{@queen}"),
            ["cmdr.gen.quaden.call"] = ("{@raven}", "{@raven}"),
            ["cmdr.gen.hung.call"] = ("{@titan}", "{@titan}"),
            ["cmdr.gen.aurel.call"] = ("{@sol}", "{@sol}"),

            // ---------------------------------------------------------------- strengths and weaknesses (F.2, F.3)
            ["cmdr.kade.strength"] = ("Whole army +{damage}% damage and +{health}% health.", "Toàn quân +{damage}% sát thương và +{health}% máu."),
            ["cmdr.kade.weakness"] = ("None.", "Không có."),
            ["cmdr.lind.strength"] = ("Repair bays and engineers repair {repair}% faster; engineers cost {price}% less CP.",
                "Trạm sửa chữa và công binh sửa nhanh hơn {repair}%; công binh rẻ hơn {price}% CP."),
            ["cmdr.lind.weakness"] = ("Aircraft and helicopters −{damage}% damage.", "Máy bay và trực thăng −{damage}% sát thương."),
            ["cmdr.reyes.strength"] = ("Aircraft and helicopters +{damage}% damage and +{health}% health, and rearm {reload}% faster; air cap +{aircraft}; fire support recharges {support}% faster.",
                "Máy bay và trực thăng +{damage}% sát thương và +{health}% máu, hồi đạn nhanh hơn {reload}%; trần máy bay +{aircraft}; yểm trợ hồi nhanh hơn {support}%."),
            ["cmdr.reyes.weakness"] = ("Towers −{health}% health.", "Tháp −{health}% máu."),
            ["cmdr.kerr.strength"] = ("+{vision}% sight; sees stealth {detect}% farther; exposed enemies take {exposed}% more damage.",
                "+{vision}% tầm nhìn; phát hiện tàng hình từ xa hơn {detect}%; địch đang bị lộ nhận thêm {exposed}% sát thương."),
            ["cmdr.kerr.weakness"] = ("Heavy vehicles −{health}% health.", "Xe hạng nặng −{health}% máu."),
            ["cmdr.venn.strength"] = ("Every drone +{health}% health and +{damage}% damage; your drones are jammed {jam}% less.",
                "Mọi drone +{health}% máu và +{damage}% sát thương; drone ta bị gây nhiễu ít hơn {jam}%."),
            ["cmdr.venn.weakness"] = ("Tanks −{damage}% damage.", "Xe tăng −{damage}% sát thương."),
            ["cmdr.mendez.strength"] = ("Vehicles +{speed}% speed; scouts and light vehicles +{health}% health; drops land {drop}% faster.",
                "Xe +{speed}% tốc độ; trinh sát và xe nhẹ +{health}% máu; thả dù nhanh hơn {drop}%."),
            ["cmdr.mendez.weakness"] = ("Whole army −{health}% health.", "Toàn quân −{health}% máu."),
            ["cmdr.brandt.strength"] = ("Towers +{health}% health and +{damage}% damage; air-dropped towers cost {price}% less CP.",
                "Tháp +{health}% máu và +{damage}% sát thương; tháp thả dù rẻ hơn {price}% CP."),
            ["cmdr.brandt.weakness"] = ("Vehicles −{speed}% speed.", "Xe −{speed}% tốc độ."),
            ["cmdr.dahl.strength"] = ("Artillery +{damage}% damage, +{range}% range and +{health}% health; fire support recharges {support}% faster.",
                "Pháo binh +{damage}% sát thương, +{range}% tầm bắn và +{health}% máu; yểm trợ hồi nhanh hơn {support}%."),
            ["cmdr.dahl.weakness"] = ("Direct-fire vehicles −{damage}% damage.", "Xe bắn thẳng −{damage}% sát thương."),
            ["cmdr.brenn.strength"] = ("CP income +{income}%; supply +{supply}%.", "Thu nhập CP +{income}%; trần tiếp tế +{supply}%."),
            ["cmdr.brenn.weakness"] = ("Whole army −{damage}% damage.", "Toàn quân −{damage}% sát thương."),
            ["cmdr.adler.strength"] = ("Each capture point pays {points}% more CP; captures {capture}% faster.",
                "Mỗi cứ điểm cho thêm {points}% CP; chiếm nhanh hơn {capture}%."),
            ["cmdr.adler.weakness"] = ("In a battle without capture points, income −{nopoints}%.", "Ở chế độ không có cứ điểm, thu nhập −{nopoints}%."),
            ["cmdr.varro.strength"] = ("Vehicles of {cheap} CP or less cost {price}% less; supply +{supply}%.",
                "Xe giá từ {cheap} CP trở xuống rẻ hơn {price}%; trần tiếp tế +{supply}%."),
            ["cmdr.varro.weakness"] = ("Whole army −{health}% health.", "Toàn quân −{health}% máu."),
            ["cmdr.reyn.strength"] = ("Tanks, heavy vehicles and vehicles of {dear} CP or more +{health}% health; vehicles of {dear} CP or more +{damage}% damage.",
                "Xe tăng, xe hạng nặng và xe giá từ {dear} CP trở lên +{health}% máu; xe giá từ {dear} CP trở lên +{damage}% sát thương."),
            ["cmdr.reyn.weakness"] = ("Every vehicle costs {price}% more CP.", "Mọi xe đắt hơn {price}% CP."),
            ["cmdr.quist.strength"] = ("Kills refund {refund}% of their CP instead of {refundFrom}% (every refund stays within {refundCap}%).",
                "Hạ địch hoàn {refund}% CP thay vì {refundFrom}% (mọi khoản hoàn vẫn trong trần {refundCap}%)."),
            ["cmdr.quist.weakness"] = ("Your own losses refund no CP.", "Xe ta bị hạ không được hoàn CP."),
            ["cmdr.okoye.strength"] = ("CP bank from {bankFrom} to {bankTo}; with {threshold} CP or more banked, income +{rich}%.",
                "Trần CP tích trữ từ {bankFrom} lên {bankTo}; khi đang có từ {threshold} CP trở lên, thu nhập +{rich}%."),
            ["cmdr.okoye.weakness"] = ("Income −{early}% for the first {seconds} seconds.", "{seconds} giây đầu trận thu nhập −{early}%."),
            ["cmdr.gen.brandt.strength"] = ("Towers +{health}% health.", "Tháp +{health}% máu."),
            ["cmdr.gen.brandt.weakness"] = ("Vehicles −{speed}% speed.", "Xe −{speed}% tốc độ."),
            ["cmdr.gen.varga.strength"] = ("Tanks and heavy vehicles +{health}% health.", "Xe tăng và xe hạng nặng +{health}% máu."),
            ["cmdr.gen.varga.weakness"] = ("Aircraft −{damage}% damage.", "Máy bay −{damage}% sát thương."),
            ["cmdr.gen.orlov.strength"] = ("Artillery +{range}% range and {spread}% less spread.", "Pháo binh +{range}% tầm, tản mát ít hơn {spread}%."),
            ["cmdr.gen.orlov.weakness"] = ("Light vehicles −{health}% health.", "Xe nhẹ −{health}% máu."),
            ["cmdr.gen.kessler.strength"] = ("Reinforcements cost {price}% less CP; ships +{health}% health.", "Tiếp viện rẻ hơn {price}% CP; tàu +{health}% máu."),
            ["cmdr.gen.kessler.weakness"] = ("Towers −{health}% health.", "Tháp −{health}% máu."),
            ["cmdr.gen.sen.strength"] = ("Drones +{health}% health.", "Drone +{health}% máu."),
            ["cmdr.gen.sen.weakness"] = ("Tanks −{damage}% damage.", "Xe tăng −{damage}% sát thương."),
            ["cmdr.gen.quaden.strength"] = ("Aircraft +{damage}% damage; air cap +{aircraft}.", "Máy bay +{damage}% sát thương; trần máy bay +{aircraft}."),
            ["cmdr.gen.quaden.weakness"] = ("Ground vehicles −{damage}% damage.", "Xe mặt đất −{damage}% sát thương."),
            ["cmdr.gen.hung.strength"] = ("Whole army +{damage}% damage; units under half health +{wounded}% more.",
                "Toàn quân +{damage}% sát thương; quân dưới 50% máu được thêm {wounded}% sát thương."),
            ["cmdr.gen.hung.weakness"] = ("None.", "Không có."),
            ["cmdr.gen.aurel.strength"] = ("Energy weapons +{damage}% damage; shields +{health}% health.", "Vũ khí Năng lượng +{damage}% sát thương; khiên +{health}% máu."),
            ["cmdr.gen.aurel.weakness"] = ("Light vehicles −{health}% health.", "Xe nhẹ −{health}% máu."),

            // ---------------------------------------------------------------- radio: the battle's start, a win, a loss (F.4)
            ["cmdr.kade.radio.start"] = ("{@iron} to all units: by the book, and home by dark.", "{@iron} gọi toàn đơn vị: đánh bài bản, về trước khi trời tối."),
            ["cmdr.kade.radio.win"] = ("Good work. The brigade holds the line.", "Làm tốt lắm. Lữ đoàn giữ vững trận tuyến."),
            ["cmdr.kade.radio.loss"] = ("Pull back and regroup. We come back stronger.", "Rút về và tập hợp lại. Ta sẽ quay lại mạnh hơn."),
            ["cmdr.lind.radio.start"] = ("Engineers are on the net. Bring them back broken, I will send them out whole.",
                "Công binh đã vào vị trí. Xe hỏng cứ mang về, tôi trả lại xe lành."),
            ["cmdr.lind.radio.win"] = ("Not a bolt wasted. Nice work.", "Không phí một con ốc. Làm tốt lắm."),
            ["cmdr.lind.radio.loss"] = ("Too much scrap, not enough time. Next round.", "Quá nhiều sắt vụn, quá ít thời gian. Lần sau."),
            ["cmdr.reyes.radio.start"] = ("{@hawk} is airborne. Keep their guns busy and leave the sky to me.", "{@hawk} đã cất cánh. Cứ giữ chân pháo địch, bầu trời để tôi lo."),
            ["cmdr.reyes.radio.win"] = ("The sky is ours. Heading home.", "Bầu trời là của ta. Quay về căn cứ."),
            ["cmdr.reyes.radio.loss"] = ("My wings are shot. Pulling out.", "Cánh bị bắn nát rồi. Rút thôi."),
            ["cmdr.kerr.radio.start"] = ("Their positions are on your map. Hit what I mark.", "Vị trí địch đã có trên bản đồ. Bắn vào chỗ tôi đánh dấu."),
            ["cmdr.kerr.radio.win"] = ("Just as the file said. Closing it.", "Đúng như hồ sơ. Đóng hồ sơ."),
            ["cmdr.kerr.radio.loss"] = ("We read them wrong. I will find out why.", "Ta đọc sai địch rồi. Tôi sẽ tìm ra lý do."),
            ["cmdr.venn.radio.start"] = ("My drones are up. Let them take the risks.", "Drone của tôi đã lên. Để chúng gánh rủi ro thay người."),
            ["cmdr.venn.radio.win"] = ("Swarm recalled. Clean work.", "Gọi bầy drone về. Gọn gàng."),
            ["cmdr.venn.radio.loss"] = ("The swarm is gone. I will build another.", "Bầy drone mất rồi. Tôi sẽ dựng bầy khác."),
            ["cmdr.mendez.radio.start"] = ("{@rush} here. Drop fast, hit first, do not stop.", "{@rush} đây. Thả nhanh, đánh trước, đừng dừng lại."),
            ["cmdr.mendez.radio.win"] = ("Faster than they could blink.", "Nhanh hơn cái chớp mắt của chúng."),
            ["cmdr.mendez.radio.loss"] = ("Too far, too fast. Fall back.", "Đi xa quá, nhanh quá. Lùi lại."),
            ["cmdr.brandt.radio.start"] = ("{@bulwark} on the line. Walls first, then we talk.", "{@bulwark} vào vị trí. Dựng tường trước, rồi hãy bàn."),
            ["cmdr.brandt.radio.win"] = ("Not one tower fell. That is how it is done.", "Không một tòa tháp nào đổ. Phải thế chứ."),
            ["cmdr.brandt.radio.loss"] = ("The line broke. It will not break twice.", "Phòng tuyến vỡ rồi. Sẽ không vỡ lần thứ hai."),
            ["cmdr.dahl.radio.start"] = ("{@longshot} has the grid. Give me targets.", "{@longshot} đã có tọa độ. Cho tôi mục tiêu."),
            ["cmdr.dahl.radio.win"] = ("Guns cooling. Target area clear.", "Pháo đang nguội. Khu mục tiêu đã sạch."),
            ["cmdr.dahl.radio.loss"] = ("They got under our guns. Moving the battery.", "Chúng lọt vào gầm pháo rồi. Chuyển trận địa."),
            ["cmdr.brenn.radio.start"] = ("{@ledger} has the books open. Spend it well.", "{@ledger} đã mở sổ sách. Tiêu cho khéo."),
            ["cmdr.brenn.radio.win"] = ("The numbers add up. A good battle.", "Sổ sách khớp. Một trận tốt."),
            ["cmdr.brenn.radio.loss"] = ("We ran at a loss. We balance it next time.", "Trận này lỗ. Lần sau ta cân lại sổ."),
            ["cmdr.adler.radio.start"] = ("{@flag} here. Every point we hold pays for the next wave.", "{@flag} đây. Mỗi cứ điểm giữ được là tiền cho đợt sau."),
            ["cmdr.adler.radio.win"] = ("Our flags are up on every hill.", "Cờ ta cắm trên mọi ngọn đồi."),
            ["cmdr.adler.radio.loss"] = ("We lost the ground. We will take it back.", "Mất đất rồi. Ta sẽ lấy lại."),
            ["cmdr.varro.radio.start"] = ("{@tide} rolling in. Numbers win wars.", "{@tide} đang tràn tới. Quân đông thắng trận."),
            ["cmdr.varro.radio.win"] = ("The tide came in, and they went under.", "Thủy triều dâng, và chúng chìm cả."),
            ["cmdr.varro.radio.loss"] = ("The tide goes out. It always comes back.", "Triều rút rồi. Nó luôn dâng lại."),
            ["cmdr.reyn.radio.start"] = ("{@crown} speaking. Few machines, but the best ones.", "{@crown} đây. Ít xe, nhưng là xe tốt nhất."),
            ["cmdr.reyn.radio.win"] = ("Quality told, as it always does.", "Chất lượng đã lên tiếng, như mọi khi."),
            ["cmdr.reyn.radio.loss"] = ("Even the best can be outnumbered.", "Xe tốt nhất cũng có lúc bị áp đảo."),
            ["cmdr.quist.radio.start"] = ("{@magpie} here. Everything they lose, we pocket.", "{@magpie} đây. Địch mất gì, ta nhặt nấy."),
            ["cmdr.quist.radio.win"] = ("A good haul today.", "Hôm nay nhặt được nhiều."),
            ["cmdr.quist.radio.loss"] = ("They picked us clean. Never again.", "Chúng nhặt sạch của ta. Không có lần sau."),
            ["cmdr.okoye.radio.start"] = ("{@vault} here. Patience first, then one big blow.", "{@vault} đây. Kiên nhẫn trước, rồi một đòn lớn."),
            ["cmdr.okoye.radio.win"] = ("Every CP paid for itself.", "Từng CP đều đáng đồng tiền."),
            ["cmdr.okoye.radio.loss"] = ("We held too much for too long.", "Ta giữ quá nhiều, quá lâu."),
        };

        // ------------------------------------------------------------------ what a commander is called and does

        /// <summary>Its name with rank: the story's own for a story character or a general, else the commander's.</summary>
        public static string Name(CommanderDef c)
        {
            if (c.IsGeneral && Strings.Has("char." + c.General + ".name")) return Strings.Get("char." + c.General + ".name");
            if (Strings.Has("cmdr." + c.Id + ".name")) return Strings.Get("cmdr." + c.Id + ".name");
            return Strings.Get("char." + c.Portrait + ".name");
        }

        public static string Call(CommanderDef c) => Strings.Get("cmdr." + c.Id + ".call");

        /// <summary>Its role: the commander's own line, or the story character's.</summary>
        public static string Role(CommanderDef c)
        {
            if (Strings.Has("cmdr." + c.Id + ".role")) return Strings.Get("cmdr." + c.Id + ".role");
            var key = "char." + (c.IsGeneral ? c.General : c.Portrait) + ".role";
            return Strings.Has(key) ? Strings.Get(key) : Strings.Get("cmdr.family." + c.Family);
        }

        public static string Strength(CommanderDef c) => Strings.Format("cmdr." + c.Id + ".strength", Values(c, true));

        public static string Weakness(CommanderDef c) => Strings.Format("cmdr." + c.Id + ".weakness", Values(c, false));

        public static string Style(CommanderDef c) => Strings.Format("cmdr.suits", ("style", Strings.Get("cmdr.style." + c.Style)));

        /// <summary>A radio speaker's name: a story character's, else a commander's (a new commander speaks under its own id).</summary>
        public static string SpeakerName(string speaker)
        {
            if (Strings.Has("char." + speaker + ".name")) return Strings.Get("char." + speaker + ".name");
            foreach (var c in Commanders.All)
                if (c.Portrait == speaker || c.Id == speaker) return Name(c);
            return Strings.Get("char.hq.name");
        }

        /// <summary>Where a locked commander opens: "Opens in chapter 4", "Opens once chapter 5 is done", "Opens in Interlude II".</summary>
        public static string Unlock(CommanderDef c)
        {
            var u = c.Unlock ?? "";
            if (u.StartsWith("i") && int.TryParse(u.Substring(1), out var interlude))
                return Strings.Format("cmdr.unlock.interlude", ("number", Roman(interlude)));
            var after = u.EndsWith("+");
            var digits = u.Trim('c', '+');
            int.TryParse(digits, out var chapter);
            return Strings.Format(after ? "cmdr.unlock.after" : "cmdr.unlock.chapter", ("chapter", Math.Max(1, chapter)));
        }

        private static string Roman(int n) => n switch { 1 => "I", 2 => "II", 3 => "III", 4 => "IV", _ => n.ToString() };

        /// <summary>
        /// The numbers of a strength (<paramref name="strength"/>) or a weakness, as whole percentages by name: the
        /// unit lines of that sign by stat, and the side-wide numbers.
        /// </summary>
        public static (string name, object value)[] Values(CommanderDef c, bool strength)
        {
            var list = new List<(string, object)>();
            var seen = new HashSet<string>();
            void Add(string name, float value)
            {
                if (seen.Add(name)) list.Add((name, Mathf.RoundToInt(Mathf.Abs(value))));
            }
            foreach (var l in c.Lines)
            {
                if (l.Value > 0f != strength) continue;
                var name = l.Stat switch
                {
                    StatId.Damage => "damage", StatId.Health => "health", StatId.Speed => "speed", StatId.Range => "range", StatId.Vision => "vision",
                    StatId.Spread => "spread", StatId.MagazineReload => "reload", StatId.CaptureRate => "capture", StatId.SummonPower => "escort",
                    _ => l.Stat.ToString().ToLowerInvariant(),
                };
                Add(name, l.Value * 100f);
            }
            foreach (var p in c.Prices) Add("price", (p.Scale - 1f) * 100f);
            Add("income", (c.Income - 1f) * 100f);
            Add("points", (c.PointIncome - 1f) * 100f);
            Add("nopoints", (1f - c.NoPointsIncome) * 100f);
            Add("rich", (c.RichIncome - 1f) * 100f);
            Add("threshold", c.RichAt);
            Add("early", (1f - c.EarlyIncome) * 100f);
            Add("seconds", c.EarlySeconds);
            Add("bankFrom", 30f);
            Add("bankTo", 30f + c.BankBonus);
            Add("supply", (c.Supply - 1f) * 100f);
            Add("aircraft", c.AirCap);
            Add("refund", c.KillRefund * 100f);
            Add("refundFrom", 25f);
            Add("refundCap", 45f);
            Add("drop", (1f - c.Delivery) * 100f);
            Add("support", (1f - c.StrikeCooldown) * 100f);
            Add("repair", (c.Repair - 1f) * 100f);
            Add("detect", (c.StealthSight - 1f) * 100f);
            Add("exposed", (c.ExposedTaken - 1f) * 100f);
            Add("jam", c.JamResist * 100f);
            Add("wounded", (c.LowHpDamage - 1f) * 100f);
            Add("cheap", CommanderRules.CheapAt);
            Add("dear", CommanderRules.DearAt);
            return list.ToArray();
        }
    }
}
