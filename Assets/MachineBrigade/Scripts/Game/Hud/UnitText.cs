using System.Collections.Generic;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The words of the generated unit lines (prompt 13 G, <see cref="UnitLines"/>): ammunition and
    /// behaviour, English and Vietnamese. The numbers come from the data.
    /// </summary>
    public static class UnitText
    {
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            ["detail.behaviour"] = ("Behaviour", "Hành vi"),
            ["detail.more"] = ("More", "Xem thêm"),
            ["detail.less"] = ("Less", "Thu gọn"),

            ["settings.ammoIcons"] = ("Ammo icons", "Biểu tượng đạn"),
            ["settings.ammoIcons.all"] = ("All units", "Mọi đơn vị"),
            ["settings.ammoIcons.air"] = ("Aircraft only", "Chỉ máy bay"),
            ["hud.stores.bombs"] = ("Bombs {0}/{1}", "Bom {0}/{1}"),
            ["hud.stores.missiles"] = ("Missiles {0}/{1}", "Tên lửa {0}/{1}"),
            ["hud.stores.rockets"] = ("Rockets {0}/{1}", "Rốc-két {0}/{1}"),
            ["hud.stores.rounds"] = ("Ammo {0}/{1}", "Đạn {0}/{1}"),

            ["detail.ammoIcons"] = ("Ammo icons", "Biểu tượng đạn"),
            ["icons.low"] = ("Yellow magazine: running low (under 20 %)", "Băng đạn vàng: sắp hết đạn (dưới 20 %)"),
            ["icons.empty"] = ("Red magazine, blinking: empty", "Băng đạn đỏ nhấp nháy: hết đạn"),
            ["icons.leaving"] = ("Grey arrow: flying out to its holding pattern", "Mũi tên xám: đang ra vòng chờ"),
            ["icons.rearming"] = ("Green ring: rearming, filling with the stores; dim at the slow rate, bright at the full one",
                "Vòng xanh: đang hồi đạn, đầy dần theo lượng đạn; mờ khi hồi chậm, sáng khi hồi đầy đủ"),
            ["icons.full"] = ("A short flash of the ring: full again", "Vòng lóe sáng: đã đầy đạn"),
            ["icons.enemy"] = ("Enemies show only empty and flying out", "Địch chỉ hiện hết đạn và đang ra vòng chờ"),
            ["tip.ammoIcons"] = ("Aircraft carry bombs, missiles and rockets that run out and come back on the field. Beside the health bar: a yellow magazine is running low, a red one empty, a grey arrow flies out to rearm, a green ring fills as the stores come back.",
                "Máy bay mang bom, tên lửa và rốc-két có hạn, hồi dần ngay trên chiến trường. Cạnh thanh máu: băng đạn vàng là sắp hết, đỏ là hết, mũi tên xám là đang ra vòng chờ, vòng xanh đầy dần khi đang hồi đạn."),

            // ---------------------------------------------------------------- a weapon
            ["ul.weapon"] = ("{0}: {1}, hits {2}", "{0}: {1}, bắn {2}"),
            ["ul.type.Kinetic"] = ("kinetic", "động năng"),
            ["ul.type.ArmorPiercing"] = ("armour-piercing", "xuyên giáp"),
            ["ul.type.HighExplosive"] = ("high explosive", "nổ mạnh"),
            ["ul.type.Flak"] = ("flak", "phòng không"),
            ["ul.type.Fire"] = ("fire", "lửa"),
            ["ul.damage"] = ("{0} damage a round", "Sát thương {0} mỗi phát"),
            ["ul.damageBurst"] = ("{0} damage a round, {1} rounds a salvo", "Sát thương {0} mỗi phát, {1} phát mỗi loạt"),
            ["ul.range"] = ("Range {0} m", "Tầm bắn {0} m"),
            ["ul.rangeMin"] = ("Range {0} m, not closer than {1} m", "Tầm bắn {0} m, tối thiểu {1} m"),
            ["ul.splash"] = ("{0}, splash {1} m", "{0}, nổ lan {1} m"),
            ["ul.endless"] = ("Never runs out", "Không bao giờ hết đạn"),
            ["ul.clip"] = ("Magazine of {0}, changed in place in {1} s", "Băng {0} viên, thay băng tại chỗ {1} giây"),
            ["ul.shots"] = ("{0} shots, reloaded in place while standing still ({1} s for all)", "{0} phát, nạp lại tại chỗ khi đứng yên ({1} giây cho đủ)"),
            ["ul.salvos"] = ("{0} salvos, reloaded in place while standing still ({1} s for all)", "{0} loạt, nạp lại tại chỗ khi đứng yên ({1} giây cho đủ)"),
            ["ul.stores"] = ("{0} {1} when full", "{0} {1} khi đầy đạn"),
            ["ul.storesRefill"] = ("Refills on the field: full in {0} s at its holding pattern, half as fast while attacking or in danger",
                "Hồi dần trên chiến trường: đầy trong {0} giây ở vòng chờ, chậm gấp đôi khi đang tấn công hoặc trong vùng nguy hiểm"),
            ["ul.storesFaster"] = ("Faster at the landing pad (x{0}) and over the HQ (x{1})", "Nhanh hơn ở Bãi đáp (x{0}) và trên sở chỉ huy (x{1})"),
            ["ul.storesCarrier"] = ("Faster at the landing pad (x{0}), over the HQ (x{1}) and beside an ammunition carrier (x{2})",
                "Nhanh hơn ở Bãi đáp (x{0}), trên sở chỉ huy (x{1}) và cạnh Xe tiếp đạn (x{2})"),
            ["ul.noun.Bomb"] = ("bombs", "quả bom"),
            ["ul.noun.Missile"] = ("missiles", "tên lửa"),
            ["ul.noun.Rocket"] = ("rockets", "rốc-két"),
            ["ul.noun.Drone"] = ("drones", "drone"),
            ["ul.noun.other"] = ("rounds", "viên"),

            // ---------------------------------------------------------------- how it moves and fights
            ["ul.move.static"] = ("Stands in place and fires at anything in reach", "Đứng yên tại chỗ, bắn mọi mục tiêu trong tầm"),
            ["ul.move.kamikaze"] = ("Goes straight for its target and blows up on it", "Lao thẳng vào mục tiêu và tự nổ"),
            ["ul.move.orbit"] = ("Circles its target, firing from the side", "Bay vòng quanh mục tiêu, bắn từ mạn"),
            ["ul.move.bomber"] = ("Flies over its target and drops its bombs in a run", "Bay qua mục tiêu và thả bom theo lượt"),
            ["ul.move.interceptor"] = ("Hunts enemy aircraft", "Săn máy bay địch"),
            ["ul.move.strike"] = ("Dives on its target and fires, then turns for another pass", "Bổ nhào xả hỏa lực vào mục tiêu, rồi vòng lại lượt khác"),
            ["ul.move.hover"] = ("Hovers at the edge of its range and fires", "Treo trên không ở rìa tầm bắn và nhả đạn"),
            ["ul.move.artillery"] = ("Stops to fire, from {0}-{1} m; needs its own or a friend's sight of the target",
                "Dừng lại mới bắn, từ {0}-{1} m; cần ta nhìn thấy mục tiêu (tự nó hoặc quân bạn)"),
            ["ul.move.standoff"] = ("Keeps to the edge of its range", "Giữ khoảng cách ở rìa tầm bắn"),
            ["ul.move.onTheMove"] = ("Fires on the move", "Vừa chạy vừa bắn"),
            ["ul.move.stops"] = ("Stops to fire", "Dừng lại mới bắn"),
            ["ul.move.building"] = ("Stands in place and serves its side", "Đứng yên tại chỗ, phục vụ phe ta"),
            ["ul.move.support"] = ("Keeps behind the front with the vehicles it serves", "Đi sau tuyến đầu, cạnh các xe nó phục vụ"),

            // ---------------------------------------------------------------- after firing
            ["ul.after.scoot"] = ("Moves {1}-{2} m after every {0} salvos", "Bắn {0} loạt rồi dời vị trí {1}-{2} m"),
            ["ul.after.clip"] = ("Changes its magazine after {0} rounds", "Bắn hết {0} viên thì thay băng"),
            ["ul.after.pass"] = ("After each pass it turns round and comes in again", "Sau mỗi lượt nó vòng lại và vào lượt mới"),

            // ---------------------------------------------------------------- target priority
            ["ul.target.strong"] = ("Goes for {0} first", "Ưu tiên {0}"),
            ["ul.target.bomber"] = ("Picks groups of vehicles and buildings; never bombs near our own units", "Ưu tiên cụm xe và công trình; không ném bom gần quân ta"),
            ["ul.target.air"] = ("Aircraft first", "Ưu tiên máy bay"),

            // ---------------------------------------------------------------- withdrawal
            ["ul.leave.stores"] = ("Out of stores, it finishes its attack, then flies to its holding pattern behind our line; back in with half its stores",
                "Hết đạn thì làm xong lượt tấn công, rồi ra vòng chờ sau tuyến quân ta; quay lại khi hồi được một nửa"),
            ["ul.leave.bomber"] = ("Goes in only with two thirds of its bombs; short of that it waits at its holding pattern",
                "Chỉ vào lượt ném khi có đủ 2/3 số bom; thiếu thì chờ ở vòng chờ"),
            ["ul.leave.hurt"] = ("Badly hurt, it flies to the landing pad (else the HQ) to mend", "Máu thấp thì bay về Bãi đáp (không có thì về sở chỉ huy) để sửa"),
            ["ul.leave.launcher"] = ("Empty, it reloads where it stands, or goes to an ammunition carrier or home when that is quicker",
                "Hết đạn thì nạp lại tại chỗ, hoặc tới Xe tiếp đạn hay về nhà khi nhanh hơn"),

            // ---------------------------------------------------------------- skills
            ["ul.skill"] = ("{0}: {1}", "{0}: {1}"),
            ["ul.skill.Repair"] = ("Self-repair", "Tự sửa"),
            ["ul.skill.Shield"] = ("Shield", "Khiên"),
            ["ul.skill.Smoke"] = ("Smoke", "Khói"),
            ["ul.skill.Overdrive"] = ("Overdrive", "Tăng tốc"),
            ["ul.skill.Barrage"] = ("Barrage", "Bắn dồn"),
            ["ul.skill.Flares"] = ("Flares", "Pháo sáng"),
            ["ul.skill.Summon"] = ("Reinforcements", "Gọi quân"),
            ["ul.skill.Emp"] = ("EMP", "EMP"),
            ["ul.skill.Patch"] = ("Patch-up", "Vá bộ phận"),
            ["ul.when.Always"] = ("whenever ready (every {0} s)", "mỗi khi sẵn sàng (mỗi {0} giây)"),
            ["ul.when.HpBelow"] = ("below {1} % health (every {0} s)", "khi máu dưới {1} % (mỗi {0} giây)"),
            ["ul.when.UnderFire"] = ("when under fire (every {0} s)", "khi bị bắn (mỗi {0} giây)"),
            ["ul.when.EnemyInRange"] = ("when an enemy is in reach (every {0} s)", "khi có địch trong tầm (mỗi {0} giây)"),
            ["ul.when.MissileIncoming"] = ("when a missile comes at it (every {0} s)", "khi có tên lửa lao tới (mỗi {0} giây)"),
            ["ul.when.PartBroken"] = ("when a part breaks", "khi một bộ phận bị phá"),
            ["ul.aps"] = ("APS: shoots down missiles, drones and direct-fire rockets aimed within {0} m ({1} at a time, one back every {2} s)",
                "APS: bắn hạ tên lửa, drone và rốc-két bắn thẳng nhắm vào trong {0} m ({1} lần liền, hồi một lần mỗi {2} giây)"),
            ["ul.apsRockets"] = ("It also takes artillery rockets", "Bắn hạ cả rốc-két pháo binh"),
            ["ul.apsShells"] = ("And {0} % of shells", "Và {0} % số đạn pháo"),
            ["ul.jammer"] = ("Jams enemy guided weapons and fire support within {0} m", "Gây nhiễu vũ khí dẫn đường và hỏa lực yểm trợ địch trong {0} m"),
            ["ul.repairAura"] = ("Repairs friendly vehicles within {0} m ({1} % of their health a second; towers half that)",
                "Sửa xe ta trong {0} m ({1} % máu mỗi giây; tháp một nửa)"),
            ["ul.rearmAura"] = ("Launchers within {0} m get one shot back every {1} s on top of their own reload", "Xe phóng trong {0} m được thêm một phát mỗi {1} giây ngoài tốc độ nạp của nó"),
            ["ul.airRearm"] = ("Helicopters within {0} m take their stores on {1} times as fast", "Trực thăng trong {0} m hồi đạn nhanh gấp {1} lần"),
            ["ul.mines"] = ("Lays a mine every {0} s (up to {1})", "Rải một quả mìn mỗi {0} giây (tối đa {1})"),
            ["ul.counterBattery"] = ("Finds enemy guns firing within {0} m", "Định vị pháo địch đang bắn trong {0} m"),
            ["ul.stealth"] = ("Hard to see: enemies spot it at {0} % of their sight", "Khó phát hiện: địch chỉ thấy ở {0} % tầm nhìn"),
            ["ul.hidden"] = ("Hidden until it fires", "Ẩn mình cho tới khi khai hỏa"),

            // ---------------------------------------------------------------- base modules
            ["ul.pad"] = ("Aircraft within {0} m take their stores on {1} times as fast and mend {2} % of their health a second",
                "Máy bay trong {0} m hồi đạn nhanh gấp {1} lần và hồi {2} % máu mỗi giây"),
            ["ul.airCap"] = ("{0} more aircraft up at once for its side", "Thêm {0} máy bay được bay cùng lúc cho phe ta"),
            ["ul.moduleRearm"] = ("Launchers in the base reload {0} times as fast", "Xe phóng trong căn cứ nạp đạn nhanh gấp {0} lần"),
            ["ul.moduleRepair"] = ("Repairs vehicles in the base", "Sửa xe trong căn cứ"),
            ["ul.moduleSupply"] = ("{0} more army supply", "Thêm {0} sức chứa quân"),
        };
    }
}
