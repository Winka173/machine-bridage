using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 8 H: every elite on one footing (1.6 times the health, 1.25 times the damage, one or
    /// two of the elite skills), the new elites, the budget that replaced the chance (share of the
    /// spending and cap by difficulty, a general's favoured cards, waves), refunds at the elite
    /// price, the bounty and blueprints, and the elite edge taken out of the campaign's enemy pace.
    /// </summary>
    public class ElitePrompt8Tests
    {
        private static Catalog C => GameContent.LoadCatalog();

        private static SimWorld Conquest(int seed = 8)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed);
            new ConquestMode(new ConquestRules { BaseDefences = false, Outposts = false }).Setup(world);
            return world;
        }

        /// <summary>Buys <paramref name="n"/> of the cards in turn for the enemy, a second of battle between buys (deliveries land).</summary>
        private static List<string> Buy(SimWorld world, int n, params string[] cards)
        {
            world.TryGetEconomy(1, out var economy);
            var before = world.VehicleList.Select(v => v.Id).ToHashSet();
            for (var i = 0; i < n; i++)
            {
                economy.Cp = 300f;
                Assert.IsTrue(world.Submit(Command.Deploy(1, cards[i % cards.Length])).Accepted, $"buy {i}");
                for (var t = 0; t < 20; t++)
                {
                    world.Step(0.05f);
                    world.ClearEvents();
                }
            }
            for (var t = 0; t < 100; t++)
            {
                world.Step(0.05f);
                world.ClearEvents();
            }
            return world.VehicleList.Where(v => v.Team == 1 && !before.Contains(v.Id)).Select(v => v.Def.Id).ToList();
        }

        // ------------------------------------------------------------------ H.1 and H.2: one footing

        [Test]
        public void EveryEliteIsOnTheSameFooting()
        {
            var catalog = C;
            var elites = catalog.Vehicles.Values.Where(v => v.Elite && v.EliteOf != null).ToList();
            // Single-skill elites whose skill is worth more: a smaller damage scale keeps them in the power band.
            var scale = new Dictionary<string, float>
            {
                ["elite_fpv_carrier"] = 1.1f, ["elite_attack_jet"] = 1f, ["elite_long_sam"] = 1.2f, ["elite_artillery"] = 1.15f,
            };
            Assert.GreaterOrEqual(elites.Count, 12, "the eight elites and the four new ones");
            foreach (var e in elites)
            {
                var b = catalog.Vehicle(e.EliteOf);
                Assert.AreEqual(b.MaxHp * 1.6f, e.MaxHp, b.MaxHp * 0.02f, e.Id + ": 60% more health than " + b.Id);
                Assert.AreEqual(scale.TryGetValue(e.Id, out var own) ? own : 1.25f, e.DamageScale, 1e-3f, e.Id + ": 25% more damage (or its own scale)");
                Assert.AreEqual(1f, b.DamageScale, 1e-3f, b.Id + " as it was");
                Assert.AreEqual((int)Math.Round(b.CpCost * 1.6f), e.ArmyCost, e.Id + " costs 1.6 times " + b.Id);
                var skills = e.Skills.Count(s => s.Id.StartsWith("elite_", StringComparison.Ordinal));
                Assert.That(skills, Is.InRange(1, 2), e.Id + ": one or two elite skills");
                // A skill that fits the class: flares only on aircraft.
                foreach (var s in e.Skills)
                    if (s.Kind == SkillKind.Flares) Assert.IsTrue(e.Flying, e.Id + " is no aircraft for flares");
                Assert.IsTrue(Game.Hud.Strings.Has("unit." + e.Id) && Game.Hud.Strings.Has("guide." + e.Id), e.Id + " has a name and a guide entry");
            }
            CollectionAssert.AreEqual(new[] { "elite_emp" }, catalog.Vehicle("elite_apc").Skills.Select(s => s.Id).ToArray(),
                "the EW carrier keeps one of its two skills (the EMP)");
            foreach (var (id, of, skill) in new[]
            {
                ("elite_fpv_carrier", "fpv_carrier", "elite_barrage"), ("elite_attack_jet", "attack_jet", "elite_flares"),
                ("elite_long_sam", "long_sam", "elite_overdrive"), ("elite_artillery", "artillery", "elite_barrage"),
            })
            {
                var e = catalog.Vehicle(id);
                Assert.AreEqual(of, e.EliteOf);
                Assert.AreEqual(of, e.Model, id + " wears its base card's model");
                CollectionAssert.AreEqual(new[] { skill }, e.Skills.Select(s => s.Id).ToArray(), id);
                Assert.AreEqual(id, catalog.EliteVariant(of), of + " has its elite now");
                Assert.AreEqual(0, e.CpCost, "never bought");
            }
        }

        [Test]
        public void AnEliteHitsAQuarterHarderThanItsGunAlone()
        {
            var world = Lab.Field(3);
            var elite = world.SpawnVehicle("elite_mbt", 1, new Vector2(0f, 0f), 0f);
            var plain = world.SpawnVehicle("main_battle_tank", 1, new Vector2(40f, 0f), 0f);
            Assert.AreEqual(1.25f, elite.Def.DamageScale, 1e-3f);
            Assert.AreEqual(1f, plain.Def.DamageScale, 1e-3f);
            // The elite's 125 mm has about the 120 mm's damage a second (trimmed to hold the power band):
            // the scale is the difference.
            var ratio = elite.Def.Weapon.Damage / elite.Def.Weapon.Cooldown / (plain.Def.Weapon.Damage / plain.Def.Weapon.Cooldown);
            Assert.AreEqual(1f, ratio, 0.05f);
        }

        // ------------------------------------------------------------------ H.3: the budget

        [Test]
        public void TheBudgetAndCapRiseWithDifficulty()
        {
            var rules = C.Elites;
            var keys = new[] { "Easy", "Normal", "Hard", "Heroic", "Iron" };
            var shares = keys.Select(rules.BudgetFor).ToArray();
            var caps = keys.Select(rules.CapFor).ToArray();
            CollectionAssert.AreEqual(new[] { 0.05f, 0.10f, 0.15f, 0.20f, 0.25f }, shares);
            CollectionAssert.AreEqual(new[] { 1, 2, 3, 4, 5 }, caps);
            Assert.AreEqual(1.6f, rules.CostScale, 1e-3f);
            Assert.AreEqual("Heroic", ModeSession.EliteKey("Normal", 1));
            Assert.AreEqual("Iron", ModeSession.EliteKey("Easy", 2));
            Assert.AreEqual("Hard", ModeSession.EliteKey("Hard", 0));
        }

        [Test]
        public void WithoutABudgetNoEliteComes()
        {
            var world = Conquest();
            var got = Buy(world, 20, "main_battle_tank");
            Assert.AreEqual(20, got.Count);
            Assert.IsFalse(got.Any(id => C.Vehicle(id).Elite), "no budget, no elites (the player's side never has one)");
        }

        [Test]
        public void AnEliteIsPaidForAtItsPrice()
        {
            var world = Conquest();
            var budget = world.Elites(1);
            budget.Share = 1f;
            budget.Cap = 5;
            world.TryGetEconomy(1, out var economy);
            economy.Cp = 100f;
            Assert.IsTrue(world.Submit(Command.Deploy(1, "main_battle_tank")).Accepted);
            var price = C.Vehicle("elite_mbt").ArmyCost;
            Assert.AreEqual(11, price);
            Assert.AreEqual(100f - price, economy.Cp, 0.01f, "the base card's 7 CP and the 4 more of the elite's 11");
            Assert.AreEqual(1, budget.Promoted);
            // Too poor for the difference: the plain card comes.
            economy.Cp = 8f;
            Assert.IsTrue(world.Submit(Command.Deploy(1, "main_battle_tank")).Accepted);
            Assert.AreEqual(1f, economy.Cp, 0.01f);
            Assert.AreEqual(1, budget.Promoted);
        }

        [Test]
        public void TheBudgetKeepsElitesToTheirShareAndCap()
        {
            foreach (var key in new[] { "Normal", "Iron" })
            {
                var world = Conquest();
                var budget = world.Elites(1);
                budget.Share = C.Elites.BudgetFor(key);
                budget.Cap = C.Elites.CapFor(key);
                var got = Buy(world, 26, "main_battle_tank", "ifv", "heavy_tank");
                var elites = got.Count(id => C.Vehicle(id).Elite);
                Assert.Greater(elites, 0, key + ": elites come once the spending allows");
                Assert.LessOrEqual(elites, budget.Cap, key + ": never more than the cap out at once");
                Assert.LessOrEqual(budget.EliteSpent, budget.Share * budget.Spent + 0.01f, key + ": within the share");
                TestContext.WriteLine($"{key}: {elites} elites of {got.Count}, {budget.EliteSpent:0} of {budget.Spent:0} CP");
            }
        }

        [Test]
        public void HarderDifficultiesFieldMoreElites()
        {
            int Elites(string key)
            {
                var world = Conquest();
                var budget = world.Elites(1);
                budget.Share = C.Elites.BudgetFor(key);
                budget.Cap = 99;
                return Buy(world, 26, "main_battle_tank", "ifv").Count(id => C.Vehicle(id).Elite);
            }
            var easy = Elites("Easy");
            var iron = Elites("Iron");
            Assert.Greater(iron, easy, $"Iron {iron} against Easy {easy}");
        }

        [Test]
        public void AGeneralMakesElitesOfHisFavouredCardsFirst()
        {
            var world = Conquest();
            var budget = world.Elites(1);
            budget.Share = 0.2f;
            budget.Cap = 99;
            budget.General = C.Generals["varga"];
            var got = Buy(world, 26, "main_battle_tank", "ifv");
            var tanks = got.Count(id => id == "elite_mbt");
            var carriers = got.Count(id => id == "elite_apc");
            Assert.Greater(tanks, carriers, $"Varga favours his tanks: {tanks} elite tanks, {carriers} elite carriers");
        }

        [Test]
        public void GeneralsAreInTheData()
        {
            var catalog = C;
            var varga = catalog.Generals["varga"];
            CollectionAssert.Contains(varga.Deck, "armored_bulldozer");
            Assert.IsTrue(varga.Prefers(catalog.Vehicle("main_battle_tank")) && varga.Prefers(catalog.Vehicle("heavy_tank")));
            Assert.IsFalse(varga.Prefers(catalog.Vehicle("ifv")));
            Assert.IsTrue(catalog.Generals["orlov"].Prefers(catalog.Vehicle("artillery")));
            Assert.IsTrue(catalog.Generals["sen"].Prefers(catalog.Vehicle("fpv_carrier")));
            Assert.IsTrue(catalog.Generals["quaden"].Prefers(catalog.Vehicle("attack_helicopter")));
            Assert.IsTrue(catalog.Generals["quaden"].Prefers(catalog.Vehicle("attack_jet")));
            Assert.IsFalse(catalog.Generals["quaden"].Prefers(catalog.Vehicle("main_battle_tank")));
        }

        [Test]
        public void AWaveFollowsTheBudgetToo()
        {
            var world = Conquest();
            var budget = world.Elites(1);
            budget.Share = 0.25f;
            budget.Cap = 99;
            var sent = new List<string>();
            for (var i = 0; i < 40; i++) sent.Add(world.Economy.ForWave(1, "main_battle_tank"));
            var elites = sent.Count(id => id == "elite_mbt");
            Assert.Greater(elites, 3);
            Assert.LessOrEqual(budget.EliteSpent, 0.25f * budget.Spent + 0.01f);
            // A siege's late wave raises the share (and the cap with it).
            var late = Conquest();
            late.Elites(1).Share = 0.1f;
            late.Elites(1).Cap = 2;
            var many = 0;
            for (var i = 0; i < 20; i++) if (late.Economy.ForWave(1, "main_battle_tank", 0.6f) == "elite_mbt") many++;
            Assert.Greater(many, 2, "the late wave's share lifts the cap too");
        }

        // ------------------------------------------------------------------ H.4: refunds

        [Test]
        public void AnEliteKillRefundsAtTheElitePrice()
        {
            float Gain(string victimId)
            {
                var world = Lab.Field(5);
                var killer = new TeamEconomy(0, 0f, income: 0f, bank: 500f);
                world.EnableEconomy(killer);
                var victim = world.SpawnVehicle(victimId, 1, new Vector2(0f, 0f), 0f);
                victim.LastAttackerTeam = 0;
                victim.LastHitTime = world.Time;
                world.Economy.OnVehicleDestroyed(victim);
                return killer.Cp;
            }
            var elite = Gain("elite_mbt");
            var plain = Gain("main_battle_tank");
            Assert.Greater(plain, 0f);
            Assert.AreEqual(11f / 7f, elite / plain, 0.01f, "the refund is at the elite's 11 CP, not the tank's 7");
        }

        // ------------------------------------------------------------------ H.5: rewards

        [Test]
        public void EliteKillsPayABountyForTheFirstFewAndSometimesABlueprint()
        {
            var catalog = C;
            var reward = new MatchReward { Coins = 100 };
            var rows = new List<(string label, string value)>();
            Rewards.AddElites(reward, rows, Enumerable.Repeat("main_battle_tank", 7).ToList(), catalog, 3);
            Assert.AreEqual(100 + catalog.Elites.BountyCap * catalog.Elites.Coins, reward.Coins, "the first four pay");
            Assert.IsTrue(rows.Count >= 1);
            var none = new MatchReward { Coins = 100 };
            Rewards.AddElites(none, rows, new List<string>(), catalog, 3);
            Assert.AreEqual(100, none.Coins);
            // About one in sixteen drops a blueprint of its base card, and only of a card the player can own.
            var drops = 0;
            for (var seed = 0; seed < 400; seed++)
            {
                var r = new MatchReward();
                Rewards.AddElites(r, null, new List<string> { "main_battle_tank", "heavy_tank", "ifv" }, catalog, seed);
                drops += r.Blueprints.Count;
                Assert.IsTrue(r.Blueprints.All(id => MatchSettings.AllVehicles.Contains(id)));
            }
            Assert.AreEqual(catalog.Elites.BlueprintChance, drops / 1200f, 0.025f);
        }

        // ------------------------------------------------------------------ H.3: the enemy's pace

        [Test]
        public void TheEliteBudgetIsPartOfTheEnemysPace()
        {
            var rules = C.Elites;
            var edge = rules.PowerEdge(rules.BudgetFor("Iron"));
            Assert.AreEqual(0.25f * (2f / 1.6f - 1f), edge, 1e-3f);
            var matched = new VehicleBoost(1.3f, 1.3f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f);
            var less = EnemyScaling.WithElites(matched, edge);
            Assert.AreEqual(1.3f * 1.3f / (1f + edge), less.Hp * less.Damage, 0.01f, "the elites' edge comes out of the matched boost");
            var none = EnemyScaling.WithElites(new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f), edge);
            Assert.AreEqual(1f, none.Hp, 1e-4f, "never weaker than the plain card");
            Assert.AreEqual(1f, none.Damage, 1e-4f);
        }
    }
}
