using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Fix prompt L5 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): which rounds warn and for how long (data warningRules), and
    /// the gate that draws at most six rings besides the super weapons, by the Settings choice. Written, not run (the owner's
    /// rule).
    /// </summary>
    public class WarningRingTests
    {
        private static Catalog Shipped => GameContent.LoadCatalog();

        [Test]
        public void TheWarningTimeFollowsTheFormulaWithItsFloorsAndCap()
        {
            var r = Shipped.Warnings;
            Assert.AreEqual(0f, r.Seconds(3, "cal_152_155", 6f), 1e-4f, "below T4: no warning");
            Assert.AreEqual(2.5f, r.Seconds(4, "cal_203", 4f), 1e-4f, "T4 floor 2.5 s");
            Assert.AreEqual(0.5f + 12f / 4.5f, r.Seconds(4, "cal_203", 12f), 1e-3f, "escape term over the floor");
            Assert.AreEqual(3.5f, r.Seconds(5, "cal_406", 6f), 1e-4f, "406 mm floor 3.5 s");
            Assert.AreEqual(4f, r.Seconds(5, "cal_800", 6f), 1e-4f, "super weapons 4 s");
            Assert.AreEqual(6f, r.Seconds(5, "cal_800", 60f), 1e-4f, "capped at 6 s");
        }

        [Test]
        public void GuidedRoundsAndSmallShellsNeverWarn()
        {
            var c = Shipped;
            foreach (var w in c.Weapons.Values)
            {
                // Play-test 13 (lane C): IsBig sorts the big rounds; ordinary fire itself warns of none (below).
                Assert.IsFalse(c.Warnings.Warns(w), w.Id + ": a gun's ordinary fire has no ring and no added flight (warningRules.normalFire)");
                if (!c.Warnings.IsBig(w)) continue;
                Assert.IsFalse(w.Guided, w.Id + ": a guided round chases its target, no ring");
                Assert.IsFalse(w.GuidedRocket, w.Id + ": a guided rocket, no ring");
                Assert.Greater(w.SplashRadius, 0f, w.Id + ": a ring is its blast");
                if (w.Tier >= 0) Assert.GreaterOrEqual(w.Tier, 4, w.Id + ": T4 and up only");
                Assert.GreaterOrEqual(w.WarnSeconds, 2.5f - 1e-4f, w.Id + ": at least the floor (a T4 without a family too)");
                Assert.LessOrEqual(w.WarnSeconds, 6f + 1e-4f, w.Id + ": at most the cap");
                Assert.AreEqual(w.SplashEdge > w.SplashRadius ? w.SplashEdge : w.SplashRadius, w.WarnRadius, 1e-4f,
                    w.Id + ": the ring is the real damage area");
            }
            Assert.IsFalse(c.Warnings.IsBig(c.Weapons["hellfire_standoff"]), "Hellfire");
            Assert.IsFalse(c.Warnings.IsBig(c.Weapons["heli_rockets"]), "Hydra 70 mm");
        }

        [Test]
        public void TheGateShowsSixAndAlwaysTheSuperWeapons()
        {
            var gate = new WarningGate { MaxShown = 6, PlayerTeam = 0 };
            var keys = new object[10];
            for (var i = 0; i < keys.Length; i++)
            {
                keys[i] = new object();
                gate.Offer(keys[i], new Vector3(i * 20f, 0f, 0f), 8f, WarningKind.Round);
            }
            var super = new object();
            gate.Offer(super, new Vector3(300f, 0f, 0f), 20f, WarningKind.Super);
            gate.Resolve(null, Vector3.zero);
            Assert.AreEqual(7, gate.ShownCount, "six rings and the super weapon");
            Assert.IsTrue(gate.Shown(keys[0], WarningKind.Round), "the nearest the view first");
            Assert.IsFalse(gate.Shown(keys[9], WarningKind.Round), "the farthest only on the minimap");
            Assert.IsTrue(gate.Shown(super, WarningKind.Super));
        }

        [Test]
        public void OffKeepsTheSuperWeaponsAndImportantNeedsAThreat()
        {
            var gate = new WarningGate { MaxShown = 6, PlayerTeam = 0, Level = 2 };
            var round = new object();
            var super = new object();
            gate.Offer(round, Vector3.zero, 8f, WarningKind.Round);
            gate.Offer(super, Vector3.zero, 20f, WarningKind.Super);
            gate.Resolve(null, Vector3.zero);
            Assert.IsFalse(gate.Shown(round, WarningKind.Round), "Off: no ordinary ring");
            Assert.IsTrue(gate.Shown(super, WarningKind.Super), "Off keeps the super weapons");
            gate.Level = 1;
            gate.Offer(round, Vector3.zero, 8f, WarningKind.Round);
            gate.Resolve(null, Vector3.zero);
            Assert.IsFalse(gate.Shown(round, WarningKind.Round), "Important only: a ring over none of our units is not shown");
        }
    }
}
