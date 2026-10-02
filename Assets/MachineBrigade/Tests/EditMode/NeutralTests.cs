using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 30 L6: the neutral sites (V1) on the battlefields: at most two kinds a battlefield, mirrored on the symmetric
    /// versions, and the kinds each mode switches on. Data checks only. Written in the cloud, not yet run.
    /// </summary>
    public class NeutralTests
    {
        private static readonly string[] Maps =
        {
            "ashfield", "borderbridge", "capital", "coralisles", "dunebreak", "emberridge", "foundry", "frostpeak", "greenvale", "hydrodam",
            "ironport", "junglepass", "landingbeach", "launchsite", "lighthousebay", "metrocity", "openpit", "orbitalgate", "redrock",
            "rustyard", "saltflat", "skyhold", "swamp", "veyra_old_quarter", "whiteout",
        };

        [Test]
        public void SymmetricBattlefieldsHaveMirroredSitesOfAtMostTwoKinds()
        {
            foreach (var id in Maps)
            {
                var map = GameContent.LoadMap(id + "_conquest");
                var kinds = map.Neutrals.Select(n => n.Kind).Distinct().ToList();
                Assert.LessOrEqual(kinds.Count, 2, id);
                foreach (var site in map.Neutrals)
                    Assert.IsTrue(map.Neutrals.Any(o => o.Kind == site.Kind && Vector2.Distance(o.At, -site.At) < 0.1f), $"{id}: {site.Kind} mirrored");
            }
        }

        [Test]
        public void ModesSwitchOnTheSheetsKinds()
        {
            var rules = GameContent.LoadCatalog().Neutrals;
            Assert.That(rules.KindsFor("Conquest"), Has.Member("radar"));
            Assert.That(rules.KindsFor("Conquest"), Has.Member("workshop"));
            Assert.That(rules.KindsFor("Deathmatch"), Has.Member("ammo_depot"));
            Assert.That(rules.KindsFor("Siege"), Has.Member("aa_site"));
            Assert.AreEqual(0, rules.KindsFor("BossRush").Count, "Boss Rush adds none");
            Assert.AreEqual(0, rules.KindsFor("Campaign").Count, "the campaign's battlefields keep their story");
            Assert.AreEqual(14f, rules.Get("workshop.radius", 0f));
        }
    }
}
