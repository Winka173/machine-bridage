using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Boss design workbook 09/10 (Docs/bosses/design_0910): the structural rules over the shipped data, the sheet 10 health targets, the
    /// carriers' hardpoints, the single 50 % phase, the capped summons and the parts that stop them. Written for the lead's targeted
    /// run; the same rules also run headless (Tools/simbuild/regress: bossrules, bosssmoke).
    /// </summary>
    public class BossDesign0910Tests
    {
        private const float Step = 0.05f;
        private static readonly HitInfo Blow = new(null, -1, null, default, HitKind.None, false);

        private static Catalog C => GameContent.LoadCatalog();

        /// <summary>Sheet 10 "HP thiết kế hiện tại" (data hp): the Excel's value x (1 - nerf), once.</summary>
        private static readonly Dictionary<string, int> Hp = new()
        {
            ["argus"] = 74695, ["armored_train"] = 29729, ["bastion_mk0"] = 15160, ["behemoth"] = 23190, ["behemoth_inferno"] = 19373,
            ["behemoth_mk0"] = 26696, ["behemoth_mk2"] = 42131, ["behemoth_tempest"] = 29729, ["coeus"] = 74695, ["command_airship"] = 155642,
            ["daedalus"] = 181878, ["drone_mothership"] = 58834, ["earth_borer"] = 56700, ["fenrir"] = 23586, ["fortress_bastion"] = 16783,
            ["hydra"] = 64024, ["hyperion"] = 213434, ["icarus_mk0"] = 74695, ["ixion"] = 69077, ["kraken"] = 127486, ["landing_hovercraft"] = 42131,
            ["leviathan"] = 39463, ["locust"] = 35950, ["mega_gunship"] = 23586, ["mobile_fortress"] = 29368, ["moloch"] = 60821,
            ["monster"] = 102440, ["nuke_train"] = 82976, ["nyx"] = 29729, ["scylla"] = 29729, ["silver_bug"] = 213434, ["theia"] = 74695, ["typhon"] = 127486,
        };

        [Test]
        public void TheCatalogKeepsTheWorkbooksStructuralRules()
        {
            var breaches = BossDesignRules.Check(C);
            Assert.IsEmpty(breaches, string.Join("\n", breaches));
        }

        [Test]
        public void EveryBossHasItsSheetTenHealthAndNothingIsNerfedTwice()
        {
            var catalog = C;
            foreach (var pair in Hp)
            {
                var def = catalog.Vehicle(pair.Key);
                // data hp x toughness.bosses (0.85) x the mini rank's share (0.55): the toughness and the rank share are the old rules, not a second nerf.
                var expected = pair.Value * 0.85f * (def.Rank == BossRank.Mini ? 0.55f : 1f);
                Assert.AreEqual(expected, def.MaxHp, expected * 0.002f + 1f, pair.Key + ": sheet 10 health");
            }
        }

        [Test]
        public void KrakenHasThirteenHardpointsLeviathanTwentyTwoAndTheDeckIsNotAGun()
        {
            var catalog = C;
            Assert.AreEqual(13, catalog.Vehicle("kraken").Mounts.Count);
            Assert.AreEqual(22, catalog.Vehicle("leviathan").Mounts.Count);
            var deck = catalog.Vehicle("kraken").Parts.First(p => p.Kind == "flightdeck");
            Assert.IsEmpty(deck.Mounts, "the flight deck carries no gun mount");
            Assert.Contains("kraken_jets", deck.Skills.ToList(), "it carries the launches");
        }

        [Test]
        public void TheRocAndArgusBombsAreAboutAHalfAndAFewTenthsOfTheirOldPunch()
        {
            var catalog = C;
            var old = catalog.Weapons["p26_roc_main_roc_bombs"];
            foreach (var id in new[] { "command_airship", "argus" })
            {
                var boss = catalog.Vehicle(id);
                var bomb = boss.Mounts[0].Weapon;
                var net = bomb.Damage * boss.WeaponDamage / (old.Damage * 1f);
                Assert.LessOrEqual(bomb.SplashRadius, old.SplashRadius * 0.85f + 1e-3f, id + ": blast radius 75-85 %");
                Assert.LessOrEqual(bomb.Damage / old.Damage, 0.52f, id + ": damage per bomb about 35-50 % (before the gun nerf)");
                Assert.Less(net, 0.6f, id + ": net damage per bomb");
            }
        }

        [Test]
        public void ADeploymentPartBrokenStaysBrokenAndASelfRepairNeverMendsIt()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 4);
            var boss = world.SpawnVehicle("fortress_bastion", 1, new Vector2(0f, 40f), 0f);
            var door = boss.Def.PartIndex("deploy_door");
            Assert.GreaterOrEqual(door, 0, "the gate exists");
            world.Bosses.Break(boss, door);
            Assert.AreEqual(-1, world.Bosses.Patch(boss, 0.5f), "the only broken part is the gate: nothing to mend");
            Assert.IsTrue(boss.IsPartBroken(door));
        }

        [Test]
        public void ThePhaseBeginsOnceAcrossTheMarkAndNeverAgainAfterAHeal()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 5);
            var boss = world.SpawnVehicle("leviathan", 1, new Vector2(0f, 60f), 0f);
            boss.Hp = boss.MaxHp * 0.52f;
            world.Damage.Apply(boss, boss.MaxHp * 0.3f, DamageType.HighExplosive, Blow);
            var begins = world.Events.Count(e => e.Kind == SimEventKind.BossPhase && e.Mount == 1);
            Assert.AreEqual(1, begins, "one big blow across the mark: one phase");
            for (var t = 0f; t < 6f; t += Step)
            {
                world.Step(Step);
                begins += world.Events.Count(e => e.Kind == SimEventKind.BossPhase && e.Mount == 1);
                world.ClearEvents();
            }
            boss.Hp = boss.MaxHp * 0.9f;
            world.Step(Step);
            boss.Hp = boss.MaxHp * 0.4f;
            for (var t = 0f; t < 6f; t += Step)
            {
                world.Step(Step);
                begins += world.Events.Count(e => e.Kind == SimEventKind.BossPhase && e.Mount == 1);
                world.ClearEvents();
            }
            Assert.AreEqual(1, begins, "a heal and a second dip do not start it again");
            Assert.AreEqual(1, boss.Phase);
        }

        [Test]
        public void TheCarriersJetsAreCappedAndAFullFlightSkipsTheCallInsteadOfQueuing()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 6);
            var kraken = world.SpawnVehicle("kraken", 1, new Vector2(0f, 60f), 0f);
            for (var i = 0; i < 4; i++)
            {
                var t = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-20f + i * 13f, 0f), 0f);
                world.MakeSparring(t);
                t.HoldFire = true;
            }
            var max = 0;
            for (var t = 0f; t < 240f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                max = System.Math.Max(max, world.Vehicles.Count(v => v.IsAlive && v.Team == 1 && v.Def.Id == "stealth_naval_strike" && !v.IsEscort));
            }
            Assert.LessOrEqual(max, 4, "at most four jets alive");
            Assert.Greater(max, 0, "and some did take off");
        }

        [Test]
        public void TheSixNewMinisAreRegisteredWithTheirParentChassis()
        {
            var catalog = C;
            foreach (var pair in BossDesignRules.NewMinis)
            {
                var def = catalog.Vehicle(pair.Key);
                Assert.AreEqual(BossRank.Mini, def.Rank, pair.Key);
                Assert.AreEqual(pair.Value, def.Mounts.Count, pair.Key + ": hardpoints (sheet 05)");
                Assert.IsTrue(Game.Hud.Strings.Has("unit." + pair.Key), pair.Key + " has a name");
            }
            CollectionAssert.IsSubsetOf(BossDesignRules.NewMinis.Keys.ToList(), BossRushRules.Everyone().ToList(), "Boss Rush may bring them");
        }
    }
}
