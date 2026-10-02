using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 34 L9 (DECISIONS "Prompt 34 L8 / L9 (lead pass, 2026-10-02)"): the validators the Python run
    /// (`Tools/balance/p34_validate.py`) also checks, on the catalog as the game builds it. Rules 1 and 2 are
    /// `Prompt34Tests` L1-L3 (one family one round, every variant's reason, every T4+ round's warning); rule 5 is
    /// `Prompt34PreviewTests`. Here: 3 the rings are the damage area, 4 every barrel fired together has its muzzle,
    /// 6 no wreck or model brings a collider; and the stress scene's definition. Written under the owner's rule of
    /// 30/09 and not run until the test phase.
    /// </summary>
    public class Prompt34ValidatorTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        // ------------------------------------------------------------------------------------------------ 3. rings

        [Test]
        public void AWeaponsRingsAreItsOwnCoreAndEdge()
        {
            foreach (var w in C.Weapons.Values.Where(w => w.SplashRadius > 0f))
            {
                Assert.AreEqual(Mathf.Max(w.SplashRadius, w.SplashEdge), w.WarnRadius, 1e-4f, w.Id + ": the edge ring is the blast's reach");
                Assert.That(w.WarnRadius, Is.GreaterThanOrEqualTo(w.SplashRadius), w.Id);
            }
        }

        [Test]
        public void EveryWarnedBossRoundHasAFixedTwoLayerBlast()
        {
            // An ordinary blast's reach varies by up to 15 % (DamageSystem); a two-layer one is fixed, so its rings are exact.
            var loose = new List<string>();
            foreach (var boss in C.Vehicles.Values.Where(v => v.Boss))
                foreach (var m in boss.Mounts)
                {
                    var w = m.Weapon;
                    if (w.WarnSeconds <= 0f || w.Guided || w.Laid || w.SplashRadius <= 0f) continue;
                    if (w.SplashEdge <= w.SplashRadius) loose.Add(boss.Id + "." + w.Id);
                }
            Assert.That(loose, Is.Empty, "T4+ boss rounds whose ring would not be their exact area:\n" + string.Join("\n", loose.Distinct()));
        }

        [Test]
        public void ACruiseMissilesWarningShowsItsBlast()
        {
            var c = C;
            foreach (var v in c.Vehicles.Values.Where(v => v.Cruise?.Warning != null))
            {
                Assert.That(c.TryGetSupport(v.Cruise.Warning, out var mark), Is.True, v.Id + ": " + v.Cruise.Warning);
                var blast = ExplosionDef.TwoLayer(v.Cruise.Damage, v.Cruise.Radius, ExplosionTier.Ultimate);
                var edge = blast.Edge > blast.Radius ? blast.Edge : blast.Radius;
                Assert.AreEqual(edge, mark.Radius, 0.01f, v.Id + ": the ring is the edge");
                Assert.AreEqual(v.Cruise.Radius, mark.BlastRadius, 0.01f, v.Id + ": the inner ring is the core");
            }
        }

        [Test]
        public void ASalvosWarningShowsItsShellsBlast()
        {
            var c = C;
            foreach (var v in c.Vehicles.Values.Where(v => v.Salvo?.Warning != null))
            {
                Assert.That(c.TryGetSupport(v.Salvo.Warning, out var mark), Is.True, v.Id);
                var blast = v.Salvo.Blast(ExplosionTier.Huge);
                var edge = blast.Edge > blast.Radius ? blast.Edge : blast.Radius;
                Assert.AreEqual(edge, mark.Radius, 0.01f, v.Id + ": the ring is the edge");
                Assert.AreEqual(v.Salvo.Radius, mark.BlastRadius, 0.01f, v.Id + ": the inner ring is the core");
            }
        }

        // ------------------------------------------------------------------------------------------------ 4. muzzles

        private static readonly Regex Barrel = new(@"^Muzzle_b\d+_");

        /// <summary>Models whose guns that fire together have no barrels to put a muzzle on (DECISIONS "Prompt 34 L4").</summary>
        private static readonly HashSet<string> NoBarrels = new() { "kraken" };

        [Test]
        public void EveryBarrelFiredTogetherHasItsMuzzle()
        {
            var missing = new List<string>();
            var checkedAny = false;
            foreach (var v in C.Vehicles.Values)
            {
                var together = v.Mounts.Where(m => m.Weapon.Simultaneous && m.Weapon.Barrels > 1).ToList();
                if (together.Count == 0 || NoBarrels.Contains(v.Model ?? v.Id)) continue;
                var model = Resources.Load<GameObject>("Models/" + (v.Model ?? v.Id));
                if (model == null) continue; // drawn with another model (a variant, a branch): its base is checked
                checkedAny = true;
                foreach (var m in together)
                {
                    var muzzles = model.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("Muzzle_" + m.Slot)).ToList();
                    var best = muzzles.Count == 0 ? 0 : muzzles.Max(t => t.Cast<Transform>().Count(k => Barrel.IsMatch(k.name)));
                    if (best < m.Weapon.Barrels) missing.Add(v.Id + "." + m.Slot + ": " + best + " of " + m.Weapon.Barrels);
                }
            }
            Assert.That(checkedAny, Is.True, "some model fires its barrels together");
            Assert.That(missing, Is.Empty, string.Join("\n", missing));
        }

        // ------------------------------------------------------------------------------------------------ 6. wrecks

        [Test]
        public void NoModelBringsACollider()
        {
            // Wrecks and their torn-off pieces are the vehicle's own model parts (WreckBreakup moves them, adds nothing).
            var with = Resources.LoadAll<GameObject>("Models").Where(g => g.GetComponentsInChildren<Collider>(true).Length > 0).Select(g => g.name).ToList();
            Assert.That(with, Is.Empty, "models with colliders: " + string.Join(", ", with));
        }

        // ------------------------------------------------------------------------------------------------ the stress scene

        [Test]
        public void TheStressSceneIsTheLeviathanSmerchBombsAnd32ASide()
        {
            var c = C;
            Assert.AreEqual(32, P34StressCheck.PerSide);
            foreach (var id in P34StressCheck.Bosses) Assert.That(c.Vehicles.ContainsKey(id), Is.True, id);
            foreach (var id in P34StressCheck.Roster) Assert.That(c.Vehicles.ContainsKey(id), Is.True, id);
            bool Carries(string boss, string family) => c.Vehicles[boss].Mounts.Any(m => m.Weapon.WeaponFamilyId == family);
            Assert.That(c.Vehicles["leviathan"].Salvo, Is.Not.Null, "the 406 mm salvo");
            Assert.That(Carries("mobile_fortress", "rkt_smerch_300"), Is.True, "Jötunn's Smerch");
            Assert.That(Carries("command_airship", "bomb_400"), Is.True, "Roc's 400 kg bombs");
            Assert.That(MatchSettings.AllMaps.Any(m => m.Id == "lighthousebay"), Is.True, "the sea map it runs on");
        }
    }
}
