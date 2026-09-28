using System.Collections.Generic;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// A made-up player part-way through the campaign, for the screenshot tool and the UI checks:
    /// rank 12, some coins, chapters 1 and 2 won and chapter 3 begun (their cards unlocked), a few
    /// cards levelled, crates to open, equipment worn and in the inventory, one daily challenge done
    /// and waiting to be claimed. It never saves, and <see cref="Restore"/> puts everything back.
    /// </summary>
    internal static class DemoProfile
    {
        private static bool _unlockAll;
        private static bool _active;

        public static void Use()
        {
            if (!_active) _unlockAll = Progression.TestUnlockAll;
            _active = true;
            Progression.TestUnlockAll = false;
            PlayerProfile.LoadForTests("{}");
            PlayerProfile.AddCoins(12450);
            var xp = 420;
            for (var level = 1; level < 12; level++) xp += PlayerProfile.XpForLevel(level);
            PlayerProfile.AddXp(xp);
            var won = 0;
            foreach (var m in Campaign.All)
            {
                if (m.Side) continue;
                if (m.Chapter > 3 || (m.Chapter == 3 && won >= 23)) break;
                PlayerProfile.RecordMission(m.Id, won % 4 == 0 ? 2 : 3, won % 5 == 0 ? 1 : 0);
                foreach (var id in m.Unlocks) PlayerProfile.Unlock(id);
                if (m.Chapter > 0) PlayerProfile.MarkChapterSeen(m.Chapter);
                won++;
            }
            foreach (var (id, prints) in new[] { ("main_battle_tank", 60), ("attack_helicopter", 30), ("mlrs", 45), ("aa_vehicle", 12) })
                PlayerProfile.AddBlueprints(id, prints);
            PlayerProfile.TryRankUp("main_battle_tank");
            PlayerProfile.TryRankUp("main_battle_tank");
            PlayerProfile.AddCrate(CrateKind.Battle, 2);
            PlayerProfile.AddCrate(CrateKind.Silver);
            var rng = new System.Random(20260928);
            var worn = new List<GearItem>();
            for (var i = 0; i < 14; i++)
            {
                var item = Gear.Create((Rarity)(i % 5), rng, 5000 + i, BranchMask.All);
                item.level = 1 + i % 6 * 3;
                PlayerProfile.AddGear(item);
                if (i < 5) worn.Add(item);
            }
            foreach (var item in worn) PlayerProfile.Equip(Gear.BranchOf(GameContent.LoadCatalog().Vehicles["main_battle_tank"]), item);
            var tasks = DailyMissions.Current;
            if (tasks.Count > 0) PlayerProfile.AddDailyProgress(DailyMissions.Today, 0, tasks[0].Target, tasks[0].Target);
            if (tasks.Count > 1) PlayerProfile.AddDailyProgress(DailyMissions.Today, 1, tasks[1].Target / 2, tasks[1].Target);
        }

        public static void Restore()
        {
            if (!_active) return;
            _active = false;
            Progression.TestUnlockAll = _unlockAll;
            PlayerProfile.Load();
        }
    }
}
