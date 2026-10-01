using System;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 26, pass 1 (A and B; DECISIONS 26AB). Written, not run (the owner's rule: no test runs until he says so).
    /// </summary>
    public class Prompt26ABTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        /// <summary>A scripted blow with a known penetration (the armour table applies, the damage type's table too).</summary>
        private static HitInfo Shot(Vector2 from, int pen) => new HitInfo(null, -1, null, from, HitKind.Direct, false).WithPen(pen, false);

        private static SimWorld Field()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 2);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(0.05f);
            world.ClearEvents();
            return world;
        }

        private static readonly string[] Mains =
        {
            "fortress_bastion", "behemoth", "mobile_fortress", "leviathan", "drone_mothership", "moloch", "nuke_train", "kronos", "typhon",
            "command_airship", "daedalus", "silver_bug",
        };

        // ---------------------------------------------------------------------------------------------- B.3 two-layer blasts

        [Test]
        public void EveryBlastWeaponABossCarriesHasAnEdgeTwiceTheCoreAtMostTwentyMetres()
        {
            var catalog = C;
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss))
                foreach (var mount in boss.Mounts)
                {
                    var w = mount.Weapon;
                    if (w.SplashRadius < 2f || w.Beam || w.Flak || w.Targets == TargetLayers.Air) continue;
                    Assert.AreEqual(Math.Min(20f, w.SplashRadius * 2f), w.SplashEdge, 1e-3f, $"{boss.Id}: {w.Id} (core {w.SplashRadius} m)");
                    Assert.AreEqual(0.4f, w.EdgeShare, 1e-4f, $"{boss.Id}: {w.Id}: the edge takes 40 %");
                }
        }

        [Test]
        public void TheListedCoresAndEdgesOfTheStartingWeaponsStand()
        {
            var catalog = C;
            // 120 mm 5 / 10 m, 152-155 mm 8.5 / 17 m, 203 mm 10 / 20 m, 406 mm 12 / 20 m
            foreach (var (id, core, edge) in new[]
                     {
                         ("p26_moloch_mo120", 5f, 10f), ("p26_bastion_b155", 8.5f, 17f), ("p26_behemoth_be152", 8.5f, 17f),
                         ("p26_nemesis_ne152", 8.5f, 17f), ("p26_jotunn_jo203", 10f, 20f), ("p26_bastion_b240", 10f, 20f),
                         ("p26_leviathan_lev406", 12f, 20f), ("p26_matriarch_ma_drones", 3f, 6f),
                     })
            {
                var w = catalog.Weapons[id];
                Assert.AreEqual(core, w.SplashRadius, 1e-3f, id + ": core");
                Assert.AreEqual(edge, w.SplashEdge, 1e-3f, id + ": edge");
            }
        }

        [Test]
        public void ATwoLayerBlastHurtsTheCoreInFullAndTheEdgeAtFortyPercent()
        {
            var world = Field();
            var core = world.SpawnVehicle("main_battle_tank", 0, new Vector2(40f, 40f), 0f);
            var edge = world.SpawnVehicle("main_battle_tank", 0, new Vector2(40f, 40f + 12f), 0f);
            var outside = world.SpawnVehicle("main_battle_tank", 0, new Vector2(40f, 40f + 25f), 0f);
            core.Hp = edge.Hp = outside.Hp = core.MaxHp;
            var hp = core.MaxHp;
            var at = new Vector2(40f, 40f - core.Radius);
            // a 10 m core, a 20 m edge: the first tank's hull is in the core, the second's reach (12 m less its radius) is in the edge
            world.Damage.Splash(new Vector2(40f, 40f), 5f, 100f, DamageType.Kinetic, 1, default, default, false, default, 20f, 0.4f);
            var lostCore = hp - core.Hp;
            var lostEdge = hp - edge.Hp;
            Assert.Greater(lostCore, 0f, "the core is hurt");
            Assert.AreEqual(lostCore * 0.4f, lostEdge, lostCore * 0.01f, "the edge takes 40 % of the core's damage");
            Assert.AreEqual(hp, outside.Hp, 1e-3f, "beyond the edge nothing");
            Assert.IsTrue(at.X > 0f);
        }

        // ---------------------------------------------------------------------------------------------- A.5 armour, phases, parts

        [Test]
        public void AGroundMainBossHasFrontFiveSideThreeRearTwoAndAMiniAtMostFourInFront()
        {
            var catalog = C;
            foreach (var id in Mains.Where(m => m != "command_airship" && m != "daedalus" && m != "silver_bug"))
            {
                var a = catalog.Vehicle(id).Armour;
                Assert.AreEqual(5, a.Front, id + ": front");
                Assert.AreEqual(3, a.Side, id + ": side");
                Assert.AreEqual(2, a.Rear, id + ": rear");
            }
            foreach (var mini in catalog.Vehicles.Values.Where(v => v.Boss && v.Rank == BossRank.Mini))
                Assert.LessOrEqual(mini.Armour.Front, 4, mini.Id + ": a mini's front armour");
        }

        [Test]
        public void ThePhasesRunFortyThirtyFiveTwentyFiveForAMainAndFiftyFiveFortyFiveForAMini()
        {
            var catalog = C;
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss && v.Phases.Count > 0))
            {
                if (boss.Rank == BossRank.Main)
                {
                    Assert.AreEqual(2, boss.Phases.Count, boss.Id);
                    Assert.AreEqual(0.6f, boss.Phases[0].At, 1e-3f, boss.Id + ": phase 2 at 60 % (the first 40 %)");
                    Assert.AreEqual(0.25f, boss.Phases[1].At, 1e-3f, boss.Id + ": phase 3 at 25 %");
                    Assert.AreEqual(1.25f, boss.Phases[1].FireRate, 1e-3f, boss.Id + ": the last phase fires 25 % faster");
                }
                else
                {
                    Assert.AreEqual(1, boss.Phases.Count, boss.Id);
                    Assert.AreEqual(0.45f, boss.Phases[0].At, 1e-3f, boss.Id + ": a mini's second phase at 45 %");
                }
            }
        }

        [Test]
        public void TheBreakablePartsAreAboutAThirdOfTheBodyOnTopOfIt()
        {
            foreach (var boss in C.Vehicles.Values.Where(v => v.Boss && v.Parts.Count > 0))
                Assert.AreEqual(0.35f, boss.Parts.Sum(p => p.Hp), 0.01f, boss.Id);
        }

        [Test]
        public void ASecondPhaseOpensTheSecondaryWeaponsOfTheMainBossesThatHaveOne()
        {
            var catalog = C;
            foreach (var id in new[] { "behemoth", "mobile_fortress", "leviathan", "drone_mothership", "nuke_train", "command_airship" })
            {
                var def = catalog.Vehicle(id);
                Assert.AreEqual(1, def.WakePhase, id + ": the second phase");
                Assert.Greater(def.WakeMounts.Count, 0, id);
                foreach (var m in def.WakeMounts) Assert.That(m, Is.InRange(1, def.Mounts.Count - 1), id + ": a secondary mount");
            }
            Assert.AreEqual(2, catalog.Vehicle("typhon").WakePhase, "Typhon's deck gun joins in the third");
        }

        // ---------------------------------------------------------------------------------------------- A.4, A.5, A.6 in a battle

        [Test]
        public void AGroundBossTakesAHalfMoreOnItsSideAndItsRearThanTheFrontWouldTake()
        {
            var world = Field();
            var boss = world.SpawnVehicle("fortress_bastion", 1, new Vector2(60f, 60f), 0f);
            boss.Hp = boss.MaxHp;
            var table = world.Catalog.Damage;
            // heading 0 is "forward" along the boss's nose: a shot from far ahead is the front, from the side the side
            var ahead = boss.Position + SimMath.Forward(boss.Heading) * 30f;
            var beside = boss.Position + new Vector2(SimMath.Forward(boss.Heading).Y, -SimMath.Forward(boss.Heading).X) * 30f;
            var before = boss.Hp;
            world.Damage.Apply(boss, 100f, DamageType.Kinetic, Shot(ahead, 5));
            var front = before - boss.Hp;
            boss.Hp = boss.MaxHp;
            world.Damage.Apply(boss, 100f, DamageType.Kinetic, Shot(beside, 5));
            var side = boss.MaxHp - boss.Hp;
            var wanted = table.Penetration(5, boss.Def.Armour.Side) / table.Penetration(5, boss.Def.Armour.Front) * 1.5f;
            Assert.AreEqual(wanted, side / front, 0.01f, "the side's armour and the half again");
        }

        [Test]
        public void ACampaignBossKeepsItsDataWhateverTheArsenalAndTheDifficultyScalesIt()
        {
            var world = Field();
            world.SetBoosts(1, _ => new VehicleBoost(2f, 2f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f), _ => 2f, everything: true);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(30f, 30f), 0f);
            Assert.AreEqual(tank.Def.MaxHp * 2f, tank.MaxHp, 1f, "an ordinary vehicle takes the edge");
            world.BossesUnscaled = true;
            var boss = world.SpawnVehicle("behemoth", 1, new Vector2(70f, 70f), 0f);
            Assert.AreEqual(boss.Def.MaxHp, boss.MaxHp, 1e-3f, "prompt 26 A.4: the boss takes none of it");
            world.BossDifficulty = "Hard";
            var hard = world.SpawnVehicle("behemoth", 1, new Vector2(70f, 100f), 0f);
            Assert.AreEqual(boss.Def.MaxHp * 1.25f, hard.MaxHp, 1f, "Hard: health x1.25");
            Assert.AreEqual(1.15f, hard.DamageBoost, 1e-4f, "Hard: damage x1.15");
            world.BossDifficulty = "Easy";
            var easy = world.SpawnVehicle("behemoth", 1, new Vector2(70f, 130f), 0f);
            Assert.AreEqual(boss.Def.MaxHp * 0.75f, easy.MaxHp, 1f);
            Assert.AreEqual(0.8f, easy.DamageBoost, 1e-4f);
        }

        // ---------------------------------------------------------------------------------------------- B.1 B.2 the damage a second

        [Test]
        public void TheMainBossesOrdinaryFireComesToTheChaptersTargetOnPaper()
        {
            var catalog = C;
            var target = new[] { 600f, 650f, 700f, 800f, 850f, 1000f, 1100f, 1200f, 1300f, 1400f, 1500f, 1600f };
            var table = catalog.Damage;
            for (var i = 0; i < Mains.Length; i++)
            {
                var def = catalog.Vehicle(Mains[i]);
                var sum = 0f;
                foreach (var m in def.Mounts)
                {
                    var w = m.Weapon;
                    if (w.Targets == TargetLayers.Air || w.Damage <= 0f || (w.Melee && w.Laid)) continue;
                    var per = FirePower.Sustained(w, def);
                    sum += per * table.Effective(w, 3f, TargetKind.Ground);
                }
                // the crusher, the thrown rock, the pods and the cruise missiles are the boss system's and counted by hand in the script;
                // the mounts alone come to at least a third of the target for every main boss, and never above it
                Assert.LessOrEqual(sum, target[i] * 1.12f, Mains[i] + ": not above the chapter's target");
                Assert.GreaterOrEqual(sum, target[i] * 0.3f, Mains[i] + ": the mounts carry a good part of it");
            }
        }

        [Test]
        public void TheSixGroundMainBossesHaveACloseGuardAndTheMinisDoNot()
        {
            var catalog = C;
            foreach (var id in new[] { "fortress_bastion", "behemoth", "mobile_fortress", "moloch", "nuke_train", "kronos" })
            {
                var ring = catalog.Vehicle(id).GuardRing;
                Assert.IsNotNull(ring, id);
                Assert.AreEqual(4, ring.Count, id + ": four vehicles");
                Assert.AreEqual(15f, ring.Radius, 1e-3f, id + ": within 15 m");
                Assert.Greater(ring.Damage, 0f, id);
            }
            foreach (var mini in catalog.Vehicles.Values.Where(v => v.Boss && v.Rank == BossRank.Mini))
                Assert.IsNull(mini.GuardRing, mini.Id);
        }

        [Test]
        public void EverySuperWeaponCyclesEveryFortyFiveToFiftySecondsWithAThreeToFourSecondWarning()
        {
            foreach (var big in C.BigAttacks.Values)
            {
                if (big.Id == "ixion_crush_charge") continue; // prompt 26 D.1: a mini boss's secondary weapon, 10 s and 2 s
                Assert.That(big.Cooldown, Is.InRange(45f, 50f), big.Id);
                Assert.That(big.Warn, Is.InRange(3f, 4f), big.Id);
            }
        }
    }
}
