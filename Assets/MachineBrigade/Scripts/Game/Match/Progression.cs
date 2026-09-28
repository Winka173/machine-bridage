using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>How a card becomes available.</summary>
    public enum CardRoute
    {
        /// <summary>Owned from the start.</summary>
        Starter,

        /// <summary>Won in the campaign, or unlocked early for coins.</summary>
        Campaign,

        /// <summary>Bought with coins only.</summary>
        Premium,
    }

    /// <summary>
    /// Which cards a new player has, which the campaign hands out (and what unlocking one early
    /// costs), and the premium units and strikes sold for coins.
    /// </summary>
    public static class Progression
    {
        /// <summary>
        /// TEST BUILDS ONLY: every card (vehicles, strikes, premium units) and every doctrine is
        /// unlocked, so the whole roster can be tried. Set it to false before a release build (see
        /// Docs/RELEASE_CHECKLIST.md); the campaign and shop unlocks then work as designed.
        /// </summary>
        public static bool TestUnlockAll = true;

        public static readonly string[] StarterVehicles =
            { "scout_jeep", "armored_car", "ifv", "light_tank", "main_battle_tank", "aa_vehicle", "artillery" };

        public static readonly string[] StarterSupports = { "artillery_barrage", "smoke_screen" };

        /// <summary>The towers a new base has: light towers and the gun turret (HQ level 1 opens three small slots and one medium).</summary>
        public static readonly string[] StarterTowers = { "guard_tower", "mg_bunker", "aa_turret", "gun_turret" };

        private static readonly Dictionary<string, int> PremiumPrices = new()
        {
            ["titan_tank"] = 3000,
            ["heavy_bomber"] = 4000,
            ["stealth_bomber"] = 5000,
            ["siege_tank"] = 4500,
            ["ballistic_launcher"] = 5000,
            ["heavy_attack_heli"] = 3500,
            ["napalm_strike"] = 1500,
        };

        /// <summary>Single-use items for sale: price for a pack of <see cref="ItemPack"/>.</summary>
        private static readonly Dictionary<string, int> ItemPrices = new()
        {
            ["moab"] = 1200,
            ["cluster_strike"] = 600,
            ["reinforcements"] = 900,
            ["field_repair"] = 500,
            ["emp_blast"] = 700,
            ["shield_dome"] = 600,
            ["gunship_support"] = 1000,
        };

        public static readonly string[] Items =
            { "moab", "cluster_strike", "reinforcements", "field_repair", "emp_blast", "shield_dome", "gunship_support" };

        /// <summary>Items come in packs of this many.</summary>
        public const int ItemPack = 2;

        public static int ItemPrice(string id) => ItemPrices.TryGetValue(id, out var price) ? price : 800;

        public static bool IsItem(string id) => ItemPrices.ContainsKey(id);

        /// <summary>Doctrines: the first is free, the others are bought with coins (owned as "doctrine.&lt;id&gt;").</summary>
        public const int DoctrinePrice = 1500;

        public static bool DoctrineOwned(string id) => TestUnlockAll || id == "armor" || PlayerProfile.Owns("doctrine." + id);

        public static bool IsStarter(string id) =>
            System.Array.IndexOf(StarterVehicles, id) >= 0 || System.Array.IndexOf(StarterSupports, id) >= 0 ||
            System.Array.IndexOf(StarterTowers, id) >= 0;

        public static bool IsPremium(string id) => PremiumPrices.ContainsKey(id);

        public static CardRoute Route(string id) => IsStarter(id) ? CardRoute.Starter : IsPremium(id) ? CardRoute.Premium : CardRoute.Campaign;

        /// <summary>Coins for a premium card, or for unlocking a campaign card before winning it.</summary>
        public static int Price(string id, Catalog catalog)
        {
            if (PremiumPrices.TryGetValue(id, out var premium)) return premium;
            var cp = catalog.Vehicles.TryGetValue(id, out var v) ? v.CpCost : catalog.TryGetSupport(id, out var s) ? s.CpCost : 5;
            return 300 + 150 * cp;
        }

        /// <summary>The campaign mission that unlocks a card, or null.</summary>
        public static MissionDef UnlockMission(string id)
        {
            foreach (var mission in Campaign.All)
                foreach (var unlock in mission.Unlocks)
                    if (unlock == id) return mission;
            return null;
        }

        public static bool Available(string id) => PlayerProfile.IsUnlocked(id);
    }

    /// <summary>
    /// The story campaign (prompt 4): nine chapters in three acts, each ten main missions (the fifth
    /// a boss, the tenth the chapter's big operation) and two side missions, in order; which ones
    /// the player may start, and what the progress so far opens (HQ levels, the Operations tiers).
    /// </summary>
    public static class Campaign
    {
        private static IReadOnlyList<MissionDef> _all;
        private static IReadOnlyList<ChapterDef> _chapters;
        private static IReadOnlyList<GeneralDef> _generals;

        public static IReadOnlyList<MissionDef> All => _all ??= GameContent.LoadCampaign();

        public static IReadOnlyList<ChapterDef> Chapters => _chapters ??= ChapterDef.ListFromJson(GameContent.CampaignJson);

        public static IReadOnlyList<GeneralDef> Generals => _generals ??= GeneralDef.ListFromJson(GameContent.CampaignJson);

        /// <summary>The last chapter.</summary>
        public static int ChapterCount => Chapters.Count;

        public static ChapterDef Chapter(int number)
        {
            foreach (var c in Chapters)
                if (c.Number == number) return c;
            return null;
        }

        public static GeneralDef General(string id)
        {
            if (id == null) return null;
            foreach (var g in Generals)
                if (g.Id == id) return g;
            return null;
        }

        /// <summary>A chapter's missions in campaign order (its ten main missions, then its side missions).</summary>
        public static List<MissionDef> MissionsOf(int chapter, bool? side = null)
        {
            var list = new List<MissionDef>();
            foreach (var m in All)
                if (m.Chapter == chapter && (side == null || m.Side == side.Value)) list.Add(m);
            return list;
        }

        /// <summary>A chapter's big operation (its tenth main mission).</summary>
        public static MissionDef OperationOf(int chapter)
        {
            MissionDef last = null;
            foreach (var m in All)
                if (m.Chapter == chapter && !m.Side) last = m;
            return last;
        }

        /// <summary>A mission's number within its chapter: "3-5", a side mission "3-S1".</summary>
        public static string Label(MissionDef mission)
        {
            if (mission == null) return "";
            if (mission.Chapter <= 0) return (IndexOf(mission.Id) + 1).ToString();
            var n = 0;
            foreach (var m in All)
            {
                if (m.Chapter != mission.Chapter || m.Side != mission.Side) continue;
                n++;
                if (m.Id == mission.Id) break;
            }
            return mission.Side ? $"{mission.Chapter}-S{n}" : $"{mission.Chapter}-{n}";
        }

        /// <summary>
        /// The HQ levels the campaign has opened: the highest a won mission gave (the first comes with
        /// the first outpost in chapter 1); every level in a test build.
        /// </summary>
        public static int HqLevelCap
        {
            get
            {
                if (Progression.TestUnlockAll) return MaxHqLevel;
                var level = 1;
                foreach (var m in All)
                    if (m.HqLevel > level && PlayerProfile.Completed(m.Id)) level = m.HqLevel;
                return level;
            }
        }

        public const int MaxHqLevel = 5;

        /// <summary>The HQ level a player who has won every main mission before this one has (1 before the first).</summary>
        public static int HqLevelAt(MissionDef mission)
        {
            var level = 1;
            foreach (var m in All)
            {
                if (m.Id == mission.Id) break;
                if (!m.Side && m.HqLevel > level) level = m.HqLevel;
            }
            return level;
        }

        /// <summary>The mission that opens an HQ level, or null.</summary>
        public static MissionDef HqLevelMission(int level)
        {
            foreach (var m in All)
                if (m.HqLevel == level) return m;
            return null;
        }

        /// <summary>
        /// The Operations mode's tiers (prompt 6): Normal from the first chapter's operation, Heroic
        /// after chapter 3's, Iron after chapter 6's, Legend once the campaign's last operation is won.
        /// </summary>
        public static int OperationsTierOpen
        {
            get
            {
                var tier = -1;
                foreach (var (chapter, t) in new[] { (1, 0), (3, 1), (6, 2), (9, 3) })
                    if (OperationOf(chapter) is { } op && PlayerProfile.Completed(op.Id)) tier = t;
                return tier;
            }
        }

        /// <summary>The battlefield of a mission, from the other side when it returns reversed.</summary>
        public static MapDefinition LoadMap(MissionDef mission)
        {
            var map = GameContent.LoadMap(mission.Map + "_" + mission.Variant);
            return mission.Reversed ? map.Reversed() : map;
        }

        /// <summary>Whether a mission's battlefield is in this build (the tests skip one that is not).</summary>
        public static bool MapExists(MissionDef mission) =>
            UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + mission.Map + "_" + mission.Variant) != null;

        /// <summary>
        /// The card rank a player who plays only the campaign reaches by a mission (Docs/DECISIONS.md,
        /// section 4: the economy curve): 1 at the start, 7 by the start of act III, 8 at the end.
        /// </summary>
        public static float ExpectedRank(MissionDef mission)
        {
            var index = IndexOf(mission.Id);
            var actThree = 0;
            for (var i = 0; i < All.Count; i++)
                if (All[i].Chapter >= 7)
                {
                    actThree = i;
                    break;
                }
            if (actThree <= 0) return 1f + 6f * index / System.Math.Max(1, All.Count - 1);
            if (index <= actThree) return 1f + 6f * index / actThree;
            return 7f + (float)(index - actThree) / System.Math.Max(1, All.Count - 1 - actThree);
        }

        /// <summary>
        /// The deck power (see EnemyScaling.Power) a mission is tuned for: the campaign is meant to be
        /// played climbing from rank 1 cards at its start to about rank 7 by act III, so each mission
        /// asks for the power of the ranks expected by then; hard missions and the Heroic and Iron
        /// tiers ask for more.
        /// </summary>
        public static int RecommendedPower(MissionDef mission, int tier = 0)
        {
            var rank = ExpectedRank(mission);
            var edge = 1f + 0.05f * (rank - 1f);
            var hard = mission.Difficulty switch { "Hard" => 1.06f, "Easy" => 0.96f, _ => 1f };
            var tierFactor = tier switch { 1 => 1.08f, 2 => 1.16f, _ => 1f };
            return (int)System.Math.Round(100f * edge * hard * tierFactor / 5f) * 5;
        }

        /// <summary>A mission by its id, or by the id it had in the old campaign (a saved choice, a debug flag).</summary>
        public static MissionDef Get(string id)
        {
            foreach (var m in All)
                if (m.Id == id) return m;
            foreach (var m in All)
                if (m.Legacy != null && m.Legacy == id) return m;
            return null;
        }

        public static int IndexOf(string id)
        {
            for (var i = 0; i < All.Count; i++)
                if (All[i].Id == id) return i;
            var legacy = Get(id);
            return legacy != null && legacy.Id != id ? IndexOf(legacy.Id) : -1;
        }

        /// <summary>
        /// Whether a mission may be started: one already won always; a main mission once the main
        /// mission before it is won (the first of a chapter once the chapter before it is finished);
        /// a side mission once the main mission it follows is won.
        /// </summary>
        public static bool IsOpen(int index)
        {
            if (index < 0 || index >= All.Count) return false;
            var mission = All[index];
            if (PlayerProfile.Completed(mission.Id)) return true;
            if (mission.Side) return mission.After == null || PlayerProfile.Completed(mission.After);
            for (var i = index - 1; i >= 0; i--)
                if (!All[i].Side && !All[i].Optional) return PlayerProfile.Completed(All[i].Id);
            return true;
        }

        /// <summary>A chapter has been reached: its first main mission is open.</summary>
        public static bool ChapterOpen(int chapter)
        {
            var first = MissionsOf(chapter, side: false);
            return first.Count > 0 && IsOpen(IndexOf(first[0].Id));
        }

        /// <summary>A chapter is finished: its big operation is won.</summary>
        public static bool ChapterDone(int chapter) => OperationOf(chapter) is { } op && PlayerProfile.Completed(op.Id);

        /// <summary>The next mission to play: the first main mission not yet won that is open (or the last).</summary>
        public static int Next
        {
            get
            {
                for (var i = 0; i < All.Count; i++)
                    if (!All[i].Side && !PlayerProfile.Completed(All[i].Id) && IsOpen(i)) return i;
                for (var i = 0; i < All.Count; i++)
                    if (!PlayerProfile.Completed(All[i].Id)) return i;
                return All.Count - 1;
            }
        }

        /// <summary>
        /// The mission "Next mission" leads to after one is won: the following main mission (a side
        /// mission leads back to the first main mission still to win); -1 at the end.
        /// </summary>
        public static int NextAfter(string id)
        {
            var index = IndexOf(id);
            if (index < 0) return -1;
            for (var i = index + 1; i < All.Count; i++)
                if (!All[i].Side && !PlayerProfile.Completed(All[i].Id)) return i;
            for (var i = index + 1; i < All.Count; i++)
                if (!All[i].Side) return i;
            return -1;
        }

        public static int Won
        {
            get
            {
                var won = 0;
                foreach (var m in All)
                    if (PlayerProfile.Completed(m.Id)) won++;
                return won;
            }
        }
    }
}
