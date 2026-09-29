using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 22 F and its checks in G: every commander's and general's passive applies to the units and the economy it
    /// names and keeps to the loadout's caps; commanders open with the story and a mission's own commander is kept; a
    /// mission's general brings their passive; the AI buys what suits its commander; the Sandbox's sides take theirs;
    /// the pick is saved and an old save starts with Kade; every text is there in both languages.
    /// </summary>
    public class CommanderPassiveTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld World() =>
            new(Catalog, new MapDefinition("test", 200f,
                new[] { new TeamStart(0, new Vector2(0f, -80f)), new TeamStart(1, new Vector2(0f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>(),
                new[] { new CapturePointDef("mid", "mid", new Vector2(0f, 0f), 8f) }));

        private static CommanderDef C(string id) => Commanders.Get(id);

        /// <summary>A buyable, non-boss def the reach takes in (towers: a fixed tower), for the line checks.</summary>
        private static VehicleDef Sample(CommanderReach reach) =>
            Catalog.Vehicles.Values.OrderBy(d => d.Id).FirstOrDefault(d => CommanderRules.Reaches(reach, d) && (reach == CommanderReach.Towers ? d.Static : reach == CommanderReach.Ships || (d.Card && d.CpCost > 0)));

        private static VehicleDef Def(string id) => Catalog.Vehicles[id];

        // ------------------------------------------------------------------ the roster (F.2, F.3)

        [Test]
        public void FourteenCommandersAndEightGeneralsAsTheSpecListsThem()
        {
            Assert.AreEqual(14, Commanders.All.Count);
            Assert.AreEqual(8, Commanders.Generals.Count);
            Assert.AreEqual(22, Commanders.All.Concat(Commanders.Generals).Select(c => c.Id).Distinct().Count(), "ids are unique");
            Assert.AreEqual(8, Commanders.All.Count(c => c.Family == CommanderFamily.Combat));
            Assert.AreEqual(6, Commanders.All.Count(c => c.Family == CommanderFamily.Economy));
            var unlocks = new Dictionary<string, string>
            {
                ["kade"] = "c1", ["lind"] = "c2", ["reyes"] = "c3", ["kerr"] = "c4", ["venn"] = "c5+", ["mendez"] = "i2", ["brandt"] = "c6", ["dahl"] = "c7",
                ["brenn"] = "i1", ["adler"] = "c4", ["varro"] = "c8", ["reyn"] = "i3", ["quist"] = "c8", ["okoye"] = "c10",
            };
            foreach (var (id, unlock) in unlocks) Assert.AreEqual(unlock, C(id).Unlock, id);
            // Every general the campaign names has its passive (Brandt's for chapter 1 once the story ties it).
            foreach (var g in GeneralDef.ListFromJson(Resources.Load<TextAsset>("Data/campaign").text))
                Assert.IsNotNull(Commanders.General(g.Id), "general " + g.Id);
            Assert.IsNotNull(Commanders.General("brandt"));
            Assert.AreEqual(Commanders.Default, "kade");
        }

        [Test]
        public void TheCapsTheCommanderCountsTowardsAreTheLoadoutsOwn()
        {
            foreach (var stat in new[] { StatId.Damage, StatId.FireRate, StatId.Health, StatId.Speed, StatId.Range, StatId.Vision, StatId.Spread, StatId.MagazineReload,
                         StatId.CaptureRate, StatId.SummonPower })
                Assert.AreEqual(GearCatalog.StatCap[(int)stat], CommanderRules.DefaultCaps[(int)stat], 1e-6f, stat.ToString());
        }

        // ------------------------------------------------------------------ unit lines and caps

        [Test]
        public void EveryUnitLineReachesItsUnitsAndNoOthers()
        {
            foreach (var c in Commanders.All.Concat(Commanders.Generals))
                foreach (var line in c.Lines)
                {
                    var def = Sample(line.Reach);
                    Assert.IsNotNull(def, $"{c.Id}: no unit is {line.Reach}");
                    var merged = CommanderRules.Merge(VehicleBoost.None, c, def, null);
                    var expected = c.Line(line.Stat, def);
                    Assert.AreEqual(expected, merged.Stat(line.Stat), 1e-5f, $"{c.Id} {line.Stat} on {def.Id}");
                    if (line.Stat == StatId.Health) Assert.AreEqual(1f + expected, merged.Hp, 1e-5f, $"{c.Id} health on {def.Id}");
                    if (line.Stat == StatId.Damage) Assert.AreEqual(1f + expected, merged.Damage, 1e-5f, $"{c.Id} damage on {def.Id}");
                    if (line.Stat == StatId.Speed) Assert.AreEqual(1f + expected, merged.Speed, 1e-5f, $"{c.Id} speed on {def.Id}");
                }
            // Reaches that must stay apart.
            Assert.IsFalse(CommanderRules.Reaches(CommanderReach.Aircraft, Def("recon_drone")), "a drone is not an aircraft");
            Assert.IsTrue(CommanderRules.Reaches(CommanderReach.Drones, Def("fpv_carrier")), "the FPV launcher is a drone unit's damage");
            Assert.IsFalse(CommanderRules.Reaches(CommanderReach.DirectFire, Def("artillery")));
            Assert.IsTrue(CommanderRules.Reaches(CommanderReach.DirectFire, Def("main_battle_tank")));
            Assert.IsTrue(CommanderRules.Reaches(CommanderReach.Cheap, Def("light_tank")));
            Assert.IsTrue(CommanderRules.Reaches(CommanderReach.Dear, Def("heavy_tank")));
            Assert.IsFalse(CommanderRules.Fields(Catalog.Vehicles.Values.First(d => d.Boss)), "bosses are never reached");
            Assert.IsFalse(CommanderRules.Fields(Def(Catalog.Base.HqId)), "nor an HQ");
        }

        [Test]
        public void AStrengthCountsTowardsTheCapAndAWeaknessComesOffAfterIt()
        {
            var tank = Def("main_battle_tank");
            VehicleBoost Gear(float damage)
            {
                var stats = new float[(int)StatId.Count];
                stats[(int)StatId.Damage] = damage;
                return new VehicleBoost(1.1f, 1.1f * (1f + damage), 1f, 1f, 1f, 0f, SpecialModule.None, 0f, stats);
            }
            // Kade's +5 % on a loadout already at the 25 % cap adds nothing; at 22 % it tops it up to 25 %.
            var full = CommanderRules.Merge(Gear(0.25f), C("kade"), tank, GearCatalog.StatCap);
            Assert.AreEqual(0.25f, full.Stat(StatId.Damage), 1e-5f);
            Assert.AreEqual(1.1f * 1.25f, full.Damage, 1e-4f, "the rank's bonus is kept, the cap holds");
            var near = CommanderRules.Merge(Gear(0.22f), C("kade"), tank, GearCatalog.StatCap);
            Assert.AreEqual(0.25f, near.Stat(StatId.Damage), 1e-5f);
            // Ledger's weakness comes off after the cap.
            var ledger = CommanderRules.Merge(Gear(0.25f), C("brenn"), tank, GearCatalog.StatCap);
            Assert.AreEqual(0.20f, ledger.Stat(StatId.Damage), 1e-5f);
            // Winter's +15 % range is above the 12 % cap: alone it gives all of it, gear adds nothing past it.
            var gun = Def("artillery");
            Assert.AreEqual(0.15f, CommanderRules.Merge(VehicleBoost.None, C("gen.orlov"), gun, GearCatalog.StatCap).Stat(StatId.Range), 1e-5f);
            var ranged = new float[(int)StatId.Count];
            ranged[(int)StatId.Range] = 0.1f;
            Assert.AreEqual(0.15f, CommanderRules.Merge(new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, ranged), C("gen.orlov"), gun,
                GearCatalog.StatCap).Stat(StatId.Range), 1e-5f);
            // A unit no line reaches keeps its boost as it was.
            var untouched = CommanderRules.Merge(Gear(0.1f), C("reyes"), tank, GearCatalog.StatCap);
            Assert.AreEqual(0.1f, untouched.Stat(StatId.Damage), 1e-5f);
        }

        [Test]
        public void ASidesUnitsEnterWithTheirCommandersLines()
        {
            var world = World();
            world.SetCommander(0, C("kade"));
            world.SetCommander(1, C("kerr"));
            var ours = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-10f, -40f), 0f);
            var theirs = world.SpawnVehicle("main_battle_tank", 1, new Vector2(10f, 40f), 0f);
            var plain = world.SpawnVehicle("main_battle_tank", 2, new Vector2(40f, 0f), 0f);
            Assert.AreEqual(plain.MaxHp * 1.05f, ours.MaxHp, 0.01f, "Kade: +5 % health");
            Assert.AreEqual(1.05f, ours.DamageBoost, 1e-4f, "Kade: +5 % damage");
            Assert.AreEqual(1.15f, theirs.VisionFactor, 1e-4f, "Kerr: +15 % sight");
            // Rush: faster vehicles, and a boss is never reached.
            world.SetCommander(0, C("mendez"));
            var fast = world.SpawnVehicle("light_tank", 0, new Vector2(-20f, -40f), 0f);
            Assert.AreEqual(1.1f, fast.SpeedFactor, 1e-4f);
            var bossId = Catalog.Vehicles.Values.First(d => d.Boss && !d.Flying).Id;
            var boss = world.SpawnVehicle(bossId, 0, new Vector2(0f, -60f), 0f);
            Assert.AreEqual(Catalog.Vehicle(bossId).MaxHp, boss.MaxHp, 1f, "a boss keeps its health");
        }

        // ------------------------------------------------------------------ the economy's passives

        private static TeamEconomy Economy(SimWorld world, string commander, float cp = 10f, IReadOnlyList<string> deck = null)
        {
            world.SetCommander(0, C(commander));
            var economy = new TeamEconomy(0, cp, income: 1f, bank: 30f, vehicles: deck);
            world.EnableEconomy(economy);
            return economy;
        }

        [Test]
        public void EconomyCommandersChangeIncomePricesAndTheBank()
        {
            var ledger = Economy(World(), "brenn");
            var world = World();
            var none = new TeamEconomy(0, 10f, income: 1f, bank: 30f);
            world.EnableEconomy(none);
            world.Step(0.05f);
            var brennWorld = World();
            ledger = Economy(brennWorld, "brenn");
            brennWorld.Step(0.05f);
            Assert.AreEqual(none.Earning * 1.1f, ledger.Earning, 1e-4f, "Ledger: +10 % income");

            // Vault: the bank from 30 to 45; +10 % from 20 CP; -10 % in the first 90 s.
            var vaultWorld = World();
            var vault = Economy(vaultWorld, "okoye", cp: 25f);
            Assert.AreEqual(45f, vault.Bank);
            vaultWorld.Step(0.05f);
            Assert.AreEqual(1.1f * 0.9f, vault.CommanderIncome, 1e-4f, "rich and early at once");
            // Flag: points pay a quarter more; without any points in play income drops 5 %.
            var flagWorld = World();
            var flag = Economy(flagWorld, "adler");
            flag.Bonus = 0.5f;
            flagWorld.Step(0.05f);
            Assert.AreEqual(0.95f, flag.CommanderIncome, 1e-4f, "no point has been fought over");
            PointCapture.Tick(flagWorld, new ObjectiveState(new CapturePointDef("mid", "mid", Vector2.Zero, 8f)), 0.05f, 10f);
            flagWorld.Step(0.05f);
            Assert.AreEqual(1f, flag.CommanderIncome, 1e-4f);
            Assert.AreEqual((flag.Income + 0.5f * C("adler").PointIncome * flag.IncomeScale) * flag.Upkeep * flag.CatchUp, flag.Earning, 1e-4f);
            Assert.Greater(C("adler").PointIncome, 1f);

            // Prices: Tide's cheap vehicles, Crown's dearer army, Lind's engineers, Bulwark's field towers, Maelstrom's reinforcements.
            Assert.AreEqual(3f * 0.85f, Economy(World(), "varro").PriceOf("light_tank", 3), 1e-4f);
            Assert.AreEqual(12f, Economy(World(), "varro").PriceOf("heavy_tank", 12), 1e-4f);
            Assert.AreEqual(12f * 1.1f, Economy(World(), "reyn").PriceOf("heavy_tank", 12), 1e-4f);
            Assert.AreEqual(3f * 0.8f, Economy(World(), "lind").PriceOf("engineer_vehicle", 3), 1e-4f);
            Assert.AreEqual(6f * 0.8f, Economy(World(), "brandt").PriceOf("field_tower", 6), 1e-4f);
            var kessler = Economy(World(), "kade");
            var kw = World();
            kw.SetCommander(0, C("gen.kessler"));
            var k = new TeamEconomy(0, 10f);
            kw.EnableEconomy(k);
            Assert.AreEqual(7f * 0.9f, k.PriceOf("main_battle_tank", 7), 1e-4f);
            Assert.AreEqual(7f, kessler.PriceOf("main_battle_tank", 7), 1e-4f, "Kade changes no price");
            // Tide's supply: +15 %.
            var tideWorld = World();
            var tide = Economy(tideWorld, "varro");
            var plainWorld = World();
            var plain = new TeamEconomy(0, 10f);
            plainWorld.EnableEconomy(plain);
            Assert.AreEqual(Mathf.RoundToInt(plain.ArmyCap * 1.15f), tide.ArmyCap, 1);
        }

        [Test]
        public void ADeploymentChargesTheCommandersPriceAndRushDropsFaster()
        {
            var world = World();
            var tide = Economy(world, "varro", cp: 10f, deck: new[] { "light_tank" });
            Assert.IsTrue(world.Submit(MachineBrigade.Sim.Commands.Command.Deploy(0, "light_tank")).Accepted);
            Assert.AreEqual(10f - Def("light_tank").CpCost * 0.85f, tide.Cp, 1e-3f, "a fractional price is charged exactly");

            float DropSeconds(string commander)
            {
                var w = World();
                Economy(w, commander, cp: 20f, deck: new[] { "light_tank" });
                w.Submit(MachineBrigade.Sim.Commands.Command.Deploy(0, "light_tank"));
                var ev = w.Events.First(e => e.Kind == MachineBrigade.Sim.Events.SimEventKind.DeploymentQueued);
                return ev.Value;
            }
            Assert.AreEqual(DropSeconds("kade") * 0.75f, DropSeconds("mendez"), 1e-3f, "Rush: drops 25 % faster");
        }

        [Test]
        public void MagpieRefundsMoreForKillsWithinTheCapAndNothingForLosses()
        {
            Assert.AreEqual(0.35f, EconomySystem.KillShare(1f, 1f, C("quist").KillRefund), 1e-5f);
            Assert.AreEqual(0.45f, EconomySystem.KillShare(1.5f, 1.2f, C("quist").KillRefund), 1e-5f, "never past the 45 % cap");
            Assert.IsFalse(C("quist").LossRefund);
            Assert.IsTrue(C("kade").LossRefund);
        }

        [Test]
        public void SideWidePassivesWorkInTheWorld()
        {
            var world = World();
            world.SetCommander(0, C("reyes"));
            world.SetCommander(1, C("gen.quaden"));
            Assert.AreEqual(TeamEconomy.MaxAircraft + 1, world.Economy.AircraftCap(0), "Hawk: air cap +1");
            Assert.AreEqual(TeamEconomy.MaxAircraft + 1, world.Economy.AircraftCap(1), "Raven: air cap +1");
            var heli = world.SpawnVehicle("attack_helicopter", 0, new Vector2(0f, -50f), 0f);
            Assert.AreEqual(1.15f, world.RearmScaleOf(heli), 1e-5f, "Hawk: aircraft rearm 15 % faster");
            Assert.AreEqual(1f, world.RearmScaleOf(world.SpawnVehicle("mlrs", 0, new Vector2(10f, -50f), 0f)), 1e-5f, "ground units as before");
            // Lind's repairs, Kerr's sight on stealth, Titan's wounded, Kerr's marked targets.
            world.SetCommander(0, C("lind"));
            Assert.AreEqual(1.25f, world.RepairScaleOf(0), 1e-5f);
            world.SetCommander(0, C("kerr"));
            Assert.AreEqual(1.25f, world.StealthSightOf(0), 1e-5f);
            Assert.AreEqual(1f, world.StealthSightOf(1), 1e-5f);
            world.SetCommander(1, C("gen.hung"));
            var wounded = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 50f), 0f);
            var target = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 20f), 0f);
            Assert.AreEqual(1f, world.CommanderOutgoing(wounded, 1, target), 1e-5f, "at full health");
            wounded.Hp = wounded.MaxHp * 0.4f;
            Assert.AreEqual(1.1f, world.CommanderOutgoing(wounded, 1, target), 1e-5f, "Titan: +10 % under half health");
            target.Statuses[(int)StatusKind.Mark].Until = world.Time + 10.0;
            target.Statuses[(int)StatusKind.Mark].Team = 1;
            var marked = world.SpawnVehicle("main_battle_tank", 1, new Vector2(20f, 50f), 0f);
            marked.Statuses[(int)StatusKind.Mark].Until = world.Time + 10.0;
            marked.Statuses[(int)StatusKind.Mark].Team = 0;
            var ours = world.SpawnVehicle("main_battle_tank", 0, new Vector2(20f, 20f), 0f);
            Assert.AreEqual(1.05f, world.CommanderOutgoing(ours, 0, marked), 1e-5f, "Kerr: +5 % on a marked enemy");
            // Venn's drones shrug off about 30 % of the jamming (deterministic by the world's seed).
            world.SetCommander(0, C("venn"));
            var drone = world.SpawnVehicle("recon_drone", 0, new Vector2(-20f, -50f), 0f);
            var shrugged = 0;
            for (var i = 0; i < 2000; i++)
                if (world.ShrugsJam(drone, drone.Def.Weapon)) shrugged++;
            Assert.AreEqual(0.3f, shrugged / 2000f, 0.04f);
            Assert.IsFalse(world.ShrugsJam(ours, ours.Def.Weapon), "a tank's rounds are not drones");
        }

        // ------------------------------------------------------------------ locked, forced, the enemy's general

        [Test]
        public void CommandersOpenWithTheStoryAndAMissionsOwnIsKept()
        {
            var all = Progression.TestUnlockAll;
            Progression.TestUnlockAll = false;
            DemoProfile.Use();
            try
            {
                Assert.IsTrue(CommanderPick.Unlocked(C("kade")), "Kade from the start");
                Assert.IsTrue(CommanderPick.Reached("c1"));
                foreach (var c in Commanders.All)
                    Assert.AreEqual(CommanderPick.Reached(c.Unlock) || c.Id == "kade", CommanderPick.Unlocked(c), c.Id);
                Assert.IsFalse(CommanderPick.Unlocked(C("gen.varga")), "a general is never the player's");
                var locked = Commanders.All.FirstOrDefault(c => !CommanderPick.Unlocked(c));
                if (locked != null)
                {
                    Assert.AreEqual("kade", CommanderPick.Resolve(locked.Id), "a locked pick falls back to Kade");
                    Assert.IsFalse(CommanderPick.Pick(locked.Id));
                }
                // A story mission's own commander is kept whether or not it is open; the player's pick is not asked.
                var duel = new MissionDef { Id = "test", Commander = "reyes", General = "quaden" };
                Assert.IsTrue(CommanderPick.Forced(duel));
                Assert.AreEqual("reyes", CommanderPick.ForBattle(duel).Id);
                Assert.AreEqual("gen.quaden", CommanderPick.EnemyFor(duel).Id, "the mission's general brings their passive");
                var free = new MissionDef { Id = "free" };
                Assert.IsFalse(CommanderPick.Forced(free));
                Assert.IsNull(CommanderPick.EnemyFor(free), "an untied mission has none");
                Assert.IsNull(CommanderPick.EnemyFor(null), "nor another mode");
                Assert.IsFalse(CommanderPick.Forced(new MissionDef { Id = "bad", Commander = "gen.varga" }), "a general cannot lead the player");
            }
            finally
            {
                DemoProfile.Restore();
                Progression.TestUnlockAll = all;
            }
        }

        [Test]
        public void EveryMissionTiedToAGeneralBringsTheirPassive()
        {
            foreach (var m in Campaign.All)
            {
                var g = CommanderPick.EnemyFor(m);
                if (m.General == null) Assert.IsNull(g, m.Id);
                else Assert.AreEqual("gen." + m.General, g?.Id, m.Id);
                if (m.Commander != null) Assert.IsNotNull(Commanders.Get(m.Commander), m.Id + ": its commander exists");
            }
        }

        // ------------------------------------------------------------------ AI (F.5)

        [Test]
        public void TheAiBuysWhatSuitsItsCommander()
        {
            Assert.Greater(CommanderRules.Fit(C("reyes"), Def("attack_helicopter")), CommanderRules.Fit(C("reyes"), Def("main_battle_tank")));
            Assert.Greater(CommanderRules.Fit(C("dahl"), Def("artillery")), CommanderRules.Fit(C("dahl"), Def("main_battle_tank")));
            Assert.Greater(CommanderRules.Fit(C("varro"), Def("light_tank")), CommanderRules.Fit(C("varro"), Def("heavy_tank")));
            Assert.Greater(CommanderRules.Fit(C("gen.varga"), Def("heavy_tank")), CommanderRules.Fit(C("gen.varga"), Def("attack_helicopter")));
            Assert.Greater(CommanderRules.SupportFit(C("brandt"), Catalog.Supports["field_tower"]), 0f);

            var deck = new[] { "main_battle_tank", "artillery", "light_tank", "attack_helicopter" };
            Dictionary<string, float> Scores(string commander)
            {
                var world = World();
                world.SetCommander(0, C(commander));
                world.EnableEconomy(new TeamEconomy(0, 0.5f, income: 0f, bank: 30f, vehicles: deck));
                world.EnableEconomy(new TeamEconomy(1, 0f, income: 0f, bank: 30f, vehicles: deck));
                var ai = new ConquestAi(null, 0, 1, AiDifficulty.Hard, 5) { BuyScores = new Dictionary<string, float>() };
                for (var i = 0; i < 60 && ai.BuyScores.Count == 0; i++)
                {
                    ai.Tick(world, 0.05f);
                    world.Step(0.05f);
                }
                return ai.BuyScores;
            }
            var dahl = Scores("dahl");
            var kade = Scores("kade");
            Assert.IsNotEmpty(dahl);
            var gain = (dahl["artillery"] - dahl["main_battle_tank"]) - (kade["artillery"] - kade["main_battle_tank"]);
            var expected = (CommanderRules.Fit(C("dahl"), Def("artillery")) - CommanderRules.Fit(C("dahl"), Def("main_battle_tank"))) * ConquestAi.CommanderFitWeight;
            Assert.AreEqual(expected, gain, 0.05f, "Longshot's artillery rises in the buying scores by its fit");
            Assert.Greater(gain, 1f);
        }

        // ------------------------------------------------------------------ the Sandbox (F.1)

        [Test]
        public void EachSandboxSideTakesItsCommander()
        {
            var s = new SandboxScenario { Fog = false };
            s.Sides[0].Commander = "reyes";
            s.Sides[1].Commander = "gen.varga";
            s.Units.Add(new SandboxUnit { Def = "attack_helicopter", Team = 0, X = 0f, Y = -20f });
            s.Units.Add(new SandboxUnit { Def = "heavy_tank", Team = 1, X = 0f, Y = 20f });
            var back = SandboxScenario.FromJson(s.ToJson());
            Assert.AreEqual("reyes", back.Sides[0].Commander, "saved with the scenario");
            Assert.AreEqual("gen.varga", back.Sides[1].Commander);
            Assert.AreEqual("", SandboxScenario.FromJson(new SandboxScenario().ToJson()).Sides[0].Commander, "none by default");
            var world = new SimWorld(Catalog, SandboxMaps.Flat(), s.Seed);
            var battle = new SandboxBattle(back);
            battle.Setup(world);
            Assert.AreEqual("reyes", world.CommanderOf(0)?.Id);
            Assert.AreEqual("gen.varga", world.CommanderOf(1)?.Id);
            world.TryGetVehicle(new MachineBrigade.Sim.Core.EntityId(battle.Spawned[1]), out var tank);
            Assert.AreEqual(Def("heavy_tank").MaxHp * 1.1f, tank.MaxHp, 1f, "Anvil: +10 % on a heavy");
            Assert.IsTrue(CommanderPick.SandboxChoices(true).Count == 1 + 14 + 8, "none, the fourteen and the eight generals");
        }

        // ------------------------------------------------------------------ save and migration

        [Test]
        public void ThePickIsSavedAndAnOldSaveStartsWithKade()
        {
            var had = PlayerPrefs.HasKey(CommanderPick.PrefKey);
            var was = PlayerPrefs.GetString(CommanderPick.PrefKey, "");
            var all = Progression.TestUnlockAll;
            Progression.TestUnlockAll = true;
            try
            {
                PlayerPrefs.DeleteKey(CommanderPick.PrefKey);
                CommanderPick.Load();
                Assert.AreEqual("kade", CommanderPick.Chosen, "a save from before commanders");
                Assert.IsTrue(CommanderPick.Pick("reyes"));
                CommanderPick.Load();
                Assert.AreEqual("reyes", CommanderPick.Chosen, "read back");
                PlayerPrefs.SetString(CommanderPick.PrefKey, "someone_removed");
                CommanderPick.Load();
                Assert.AreEqual("kade", CommanderPick.Chosen, "an unknown id");
                PlayerPrefs.SetString(CommanderPick.PrefKey, "gen.varga");
                CommanderPick.Load();
                Assert.AreEqual("kade", CommanderPick.Chosen, "a general's id");
                Assert.IsFalse(CommanderPick.Pick("gen.varga"));
            }
            finally
            {
                if (had) PlayerPrefs.SetString(CommanderPick.PrefKey, was);
                else PlayerPrefs.DeleteKey(CommanderPick.PrefKey);
                CommanderPick.Load();
                Progression.TestUnlockAll = all;
            }
        }

        // ------------------------------------------------------------------ words (prompt 21's rules)

        [Test]
        public void EveryCommanderIsNamedAndDescribedInBothLanguages()
        {
            var was = Strings.Vietnamese;
            try
            {
                foreach (var vi in new[] { false, true })
                {
                    Strings.Vietnamese = vi;
                    foreach (var c in Commanders.All.Concat(Commanders.Generals))
                    {
                        var texts = new List<string> { CommanderText.Name(c), CommanderText.Call(c), CommanderText.Strength(c), CommanderText.Weakness(c), CommanderText.Role(c) };
                        if (!c.IsGeneral)
                        {
                            texts.Add(CommanderText.Style(c));
                            texts.Add(CommanderText.Unlock(c));
                            foreach (var when in new[] { "start", "win", "loss" }) texts.Add(Strings.Get("cmdr." + c.Id + ".radio." + when));
                        }
                        foreach (var t in texts)
                        {
                            Assert.IsFalse(string.IsNullOrWhiteSpace(t), $"{c.Id} ({(vi ? "vi" : "en")})");
                            Assert.IsFalse(t.Contains("{") || t.Contains("}") || t.StartsWith("cmdr.") || t.StartsWith("char."), $"{c.Id} ({(vi ? "vi" : "en")}): \"{t}\"");
                        }
                    }
                    Strings.Vietnamese = false;
                    Assert.AreEqual("Whole army +5% damage and +5% health.", CommanderText.Strength(C("kade")));
                    Assert.AreEqual("CP bank from 30 to 45; with 20 CP or more banked, income +10%.", CommanderText.Strength(C("okoye")));
                    Assert.AreEqual("Opens once chapter 5 is done", CommanderText.Unlock(C("venn")));
                    Assert.AreEqual("Opens in Interlude II", CommanderText.Unlock(C("mendez")));
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }
    }
}
