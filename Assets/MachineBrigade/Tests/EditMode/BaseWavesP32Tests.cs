using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L5 (DECISIONS "Prompt 32 L4/L5/L6/L8"): the Defend and Endless waves come from ReferenceBasePower by the
    /// defender's HQ level (five reference loadouts in the data), never from the player's own base, which is only shown.
    /// Written, not run.
    /// </summary>
    public class BaseWavesP32Tests
    {
        private static Catalog _catalog;
        private static Catalog C => _catalog ??= GameContent.LoadCatalog();

        private static SiegeMode Defend(BaseLoadout loadout, float progress = 1f)
        {
            var world = new SimWorld(C, GameContent.LoadMap("greenvale_siege"), seed: 5);
            var rules = new SiegeRules
            {
                PlayerDefends = true, ScaleToBase = true, WaveSeconds = 60f, ProgressScale = progress, FortressLoadout = loadout,
                Attacker = new SideSetup { StartCp = 0f, Income = 0.01f, Vehicles = new[] { "armored_car" } },
                Defender = new SideSetup { StartCp = 0f, Income = 0.01f, Bank = 200f },
            };
            var mode = new SiegeMode(rules);
            mode.Setup(world);
            return mode;
        }

        [Test]
        public void TheDataHasAReferenceBaseForEveryHqLevel()
        {
            var levels = new bool[6];
            foreach (var r in C.Base.Reference)
            {
                levels[r.HqLevel] = true;
                foreach (var id in r.Towers) Assert.IsTrue(C.Vehicles.ContainsKey(id), id);
                foreach (var id in r.Utilities) Assert.IsTrue(C.Vehicles.ContainsKey(id), id);
            }
            for (var level = 1; level <= 5; level++) Assert.IsTrue(levels[level], $"HQ level {level}");
        }

        [Test]
        public void ReferenceBasePowerGrowsWithTheHqLevel()
        {
            for (var level = 2; level <= 5; level++)
                Assert.Greater(BaseStrength.ReferencePower(C, level), BaseStrength.ReferencePower(C, level - 1), $"HQ {level}");
        }

        [Test]
        public void ThePlayersOwnBaseDoesNotSizeTheWaves()
        {
            var bare = Defend(new BaseLoadout { HqLevel = 3 });
            var full = Defend(new BaseLoadout
            {
                HqLevel = 3, Small = { "guard_tower", "mg_bunker", "aa_turret", "ew_tower" }, Medium = { "gun_turret", "atgm_tower" },
                Large = { "heavy_turret" }, Utilities = { "repair_bay" },
            });
            Assert.AreEqual(3, bare.ReferenceLevel);
            Assert.AreEqual(bare.WaveScaleNow, full.WaveScaleNow, 1e-5f, "the same HQ level, the same waves");
            Assert.Greater(full.BaseScore, bare.BaseScore, "the base's own strength is still read (shown)");
            Assert.AreEqual(BaseStrength.WaveScale(BaseStrength.ReferenceScore(C, 3)), bare.WaveScaleNow, 1e-5f);
        }

        [Test]
        public void TheWavesFollowTheHqLevelAndTheCampaignProgress()
        {
            var low = Defend(new BaseLoadout { HqLevel = 1 });
            var high = Defend(new BaseLoadout { HqLevel = 5 });
            Assert.GreaterOrEqual(high.WaveScaleNow, low.WaveScaleNow);
            var later = Defend(new BaseLoadout { HqLevel = 1 }, progress: 1.2f);
            Assert.AreEqual(low.WaveScaleNow * 1.2f, later.WaveScaleNow, 1e-4f, "x the campaign progress factor");
        }
    }
}
