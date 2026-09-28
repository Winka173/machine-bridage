using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 8 J: the risky combinations measured (Twin Feed on the big guns, ricochet and shredder
    /// on flak, cluster on bombs, modules on cheap cards, War Profiteer with the Quartermaster set,
    /// the Wolfpack swarm, the SP gun with a designator and counter-battery radar, the Phoenix,
    /// Unbreakable and emergency-kit stack), the armoured bulldozer against the turtle tank as a
    /// damage sponge, the SP gun's shoot-and-scoot, and a one-tower base in Legendary tower gear
    /// against the mixed base in the same gear. MB_BALANCE=1; the tables go to MB_LAB_OUT.
    /// </summary>
    public class EquipmentRiskLab
    {
        private static VehicleBoost T(TraitId id) => Lab.Traits(GearCatalog.Trait(id).At(Rarity.Legendary));

        [Test, Category("Balance"), Timeout(7200000)]
        public void RiskyCombinations()
        {
            Lab.Gate();
            var sb = new StringBuilder();
            sb.AppendLine("| combination | on | measure | plain | with | change |");
            sb.AppendLine("|---|---|---|---|---|---|");
            void Duel(string name, string shooter, string[] targets, VehicleBoost boost, int count = 2)
            {
                var d = new Lab.Duel { Shooter = shooter, Targets = targets, Count = count };
                var plain = Lab.Dps(d, 3);
                var with = Lab.Dps(new Lab.Duel { Shooter = shooter, Targets = targets, Count = count, Boost = _ => boost }, 3);
                sb.AppendLine($"| {name} | {count} x {shooter} | damage a second | {plain:0} | {with:0} | {Lab.Pct(with / Math.Max(1f, plain) - 1f)} |");
            }
            var armour = new[] { "main_battle_tank", "ifv", "light_tank" };
            var air = new[] { "attack_helicopter", "scout_heli", "attack_helicopter" };
            var ground = new[] { "main_battle_tank", "ifv", "armored_car" };
            Duel("Twin Feed", "main_battle_tank", armour, T(TraitId.TwinFeed));
            Duel("Twin Feed", "railgun_truck", armour, T(TraitId.TwinFeed));
            Duel("Ricochet shells", "aa_vehicle", air, T(TraitId.RicochetShells));
            Duel("Ricochet shells", "heavy_aa", air, T(TraitId.RicochetShells));
            Duel("Shredder rounds", "aa_vehicle", air, T(TraitId.ShredderRounds));
            Duel("Cluster warhead", "heavy_bomber", ground, T(TraitId.ClusterWarhead), 1);
            Duel("Cluster warhead", "mlrs", ground, T(TraitId.ClusterWarhead));
            // The same on a tight group (3.5 m apart), where bomblets count most.
            foreach (var (card, n) in new[] { ("heavy_bomber", 1), ("mlrs", 2), ("artillery", 2) })
            {
                var group = new[] { "ifv", "armored_car", "light_tank", "ifv", "armored_car", "light_tank" };
                var plain = Lab.Dps(new Lab.Duel { Shooter = card, Targets = group, Count = n, Spacing = 3.5f }, 3);
                var with = Lab.Dps(new Lab.Duel { Shooter = card, Targets = group, Count = n, Spacing = 3.5f, Boost = _ => T(TraitId.ClusterWarhead) }, 3);
                sb.AppendLine($"| Cluster warhead (tight group) | {n} x {card} | damage a second | {plain:0} | {with:0} | {Lab.Pct(with / Math.Max(1f, plain) - 1f)} |");
            }
            // A module on a cheap card is scaled to its price (clamp(CP / 7, 0.4, 1.3)).
            var escort = Lab.Module(SpecialModule.DroneEscort, 2f, 20f);
            foreach (var card in new[] { "scout_jeep", "main_battle_tank", "heavy_tank" })
            {
                var plain = Lab.Dps(new Lab.Duel { Shooter = card, Targets = ground, Count = 1 }, 3);
                var with = Lab.Dps(new Lab.Duel { Shooter = card, Targets = ground, Count = 1, Boost = _ => escort }, 3);
                var cp = Lab.Catalog.Vehicle(card).CpCost;
                sb.AppendLine($"| Drone escort (Legendary) | 1 x {card} ({cp} CP) | damage a second, added per CP | {plain:0} | {with:0} | {(with - plain) / cp:+0.0;-0.0} a CP |");
            }
            // War Profiteer and the Quartermaster four-piece: the kill refund's cap holds.
            var profiteer = GearCatalog.Module(SpecialModule.WarProfiteer).Legendary;
            var quartermaster = GearCatalog.Brand(8).FourPiece.A;
            var share = EconomySystem.KillShare(1f, 1f + profiteer + quartermaster);
            sb.AppendLine($"| War Profiteer + Quartermaster 4 | any | kill refund share | {EconomySystem.KillShare(1f, 1f):0.00} | {share:0.00} | capped at {EconomySystem.KillRefundCap:0.00} |");
            var loss = Math.Min(EconomySystem.LossRefundCap, GearCatalog.Brand(8).FourPiece.B);
            sb.AppendLine($"| Quartermaster 4 (own loss) | any | loss refund share | 0.00 | {loss:0.00} | capped at {EconomySystem.LossRefundCap:0.00} |");
            // The Wolfpack set on a swarm of cheap cards.
            var wolf = GearCatalog.Brand(12);
            Duel("Wolfpack 2 + 4", "scout_jeep", ground, Lab.Traits(wolf.TwoPiece, wolf.FourPiece), 6);
            Duel("Wolfpack 2 + 4", "main_battle_tank", armour, Lab.Traits(wolf.TwoPiece, wolf.FourPiece), 3);
            // The SP gun with a designator (its marked targets: near-zero scatter) and counter-battery radar.
            Duel("Laser designator", "artillery", ground, T(TraitId.LaserDesignator));
            Duel("Designator + counter-battery radar", "artillery", ground,
                Lab.Traits(GearCatalog.Trait(TraitId.LaserDesignator).At(Rarity.Legendary), GearCatalog.Trait(TraitId.CounterBatteryRadar).At(Rarity.Legendary)));
            // The survival stack on a heavy tank (no chaining: each saves once in its own window).
            var attackers = new[] { "main_battle_tank", "main_battle_tank", "tank_destroyer" };
            var stack = Lab.Traits(GearCatalog.Trait(TraitId.Unbreakable).At(Rarity.Legendary), GearCatalog.Trait(TraitId.EmergencyRepairKit).At(Rarity.Legendary),
                GearCatalog.Brand(11).FourPiece);
            var soak = new Lab.Soak { Target = "heavy_tank", Attackers = attackers };
            var alone = Lab.TimePerLife(soak, 3);
            var stacked = Lab.TimePerLife(new Lab.Soak { Target = "heavy_tank", Attackers = attackers, Boost = _ => stack }, 3);
            sb.AppendLine($"| Unbreakable + emergency kit + Phoenix 4 | heavy_tank | seconds alive a life | {alone:0.0} | {stacked:0.0} | {Lab.Pct(stacked / alone - 1f)} |");
            var unbreakable = Lab.TimePerLife(new Lab.Soak { Target = "heavy_tank", Attackers = attackers, Boost = _ => T(TraitId.Unbreakable) }, 3);
            sb.AppendLine($"| Unbreakable alone | heavy_tank | seconds alive a life | {alone:0.0} | {unbreakable:0.0} | {Lab.Pct(unbreakable / alone - 1f)} |");
            Lab.Write("risky_combos", sb.ToString());
        }

        /// <summary>
        /// Every unique line outside the weapon and loader slots, and every module, at Legendary on one
        /// card of each branch: what it adds to the duel's damage a second and to the soak's time alive
        /// (the bigger of the two is its value; I.11 wants most between +10 % and +25 %). "n/a": the
        /// line does not fit the branch.
        /// </summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void DefensiveLinesAndModules()
        {
            Lab.Gate();
            var cards = new (GearBranch branch, string card, string[] targets, string[] attackers)[]
            {
                (GearBranch.Armor, "main_battle_tank", new[] { "main_battle_tank", "ifv", "light_tank" }, new[] { "main_battle_tank", "ifv", "atgm_carrier" }),
                (GearBranch.Light, "ifv", new[] { "ifv", "armored_car", "light_tank" }, new[] { "main_battle_tank", "ifv", "armored_car" }),
                (GearBranch.Artillery, "artillery", new[] { "main_battle_tank", "ifv", "armored_car" }, new[] { "ifv", "armored_car", "scout_jeep" }),
                (GearBranch.Air, "attack_helicopter", new[] { "main_battle_tank", "ifv", "armored_car" }, new[] { "aa_vehicle", "aa_vehicle", "heavy_aa" }),
            };
            var duelBase = cards.ToDictionary(c => c.card, c => Lab.Dps(new Lab.Duel { Shooter = c.card, Targets = c.targets }, 3));
            var soakBase = cards.ToDictionary(c => c.card, c => Lab.TimePerLife(new Lab.Soak { Target = c.card, Attackers = c.attackers }, 3));
            var sb = new StringBuilder("| line or module |");
            foreach (var c in cards) sb.Append($" {c.branch} ({c.card}): damage / time alive |");
            sb.AppendLine();
            sb.Append("|---|");
            foreach (var _ in cards) sb.Append("---|");
            sb.AppendLine();
            void Measure(string name, VehicleNeed need, VehicleBoost boost)
            {
                sb.Append($"| {name} |");
                foreach (var c in cards)
                {
                    if (!VehicleFit.Fits(need, c.branch))
                    {
                        sb.Append(" n/a |");
                        continue;
                    }
                    var dmg = Lab.Gain(new Lab.Duel { Shooter = c.card, Targets = c.targets }, _ => boost, 3, duelBase[c.card]);
                    var alive = Lab.Toughness(new Lab.Soak { Target = c.card, Attackers = c.attackers }, _ => boost, 3, soakBase[c.card]);
                    sb.Append($" {Lab.Pct(dmg)} / {Lab.Pct(alive)} |");
                }
                sb.AppendLine();
            }
            foreach (var t in GearCatalog.Traits)
            {
                if (Gear.IsTower(t.Slot) || t.Slot is GearSlot.Weapon or GearSlot.Loader) continue;
                Measure(t.Key, t.Needs, Lab.Traits(t.At(Rarity.Legendary)));
            }
            foreach (var m in GearCatalog.Modules)
                Measure("module " + m.Key, m.Needs, Lab.Module(m.Module, m.Legendary, m.Legendary2));
            sb.AppendLine();
            sb.AppendLine("Lines that act outside a duel or a soak (sight, stealth, capture, speed on the march, economy) read near zero here; their value is described in DECISIONS.md section 8.");
            Lab.Write("defensive_lines", sb.ToString());
        }

        /// <summary>
        /// The armoured bulldozer and the turtle tank under the same fire: the bulldozer must not be
        /// the better sponge for the line (A.1), while it is the best close-range wrecker of structures.
        /// </summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void TheBulldozerIsNoBetterSpongeThanTheTurtle()
        {
            Lab.Gate();
            var sb = new StringBuilder();
            sb.AppendLine("| card | CP | health | seconds alive a life (mixed fire) | a CP | (tank fire) | a CP |");
            sb.AppendLine("|---|---|---|---|---|---|---|");
            var results = new Dictionary<string, float>();
            foreach (var card in new[] { "armored_bulldozer", "turtle_tank", "heavy_tank" })
            {
                var def = Lab.Catalog.Vehicle(card);
                var mixed = Lab.TimePerLife(new Lab.Soak { Target = card }, 3);
                var tanks = Lab.TimePerLife(new Lab.Soak { Target = card, Attackers = new[] { "main_battle_tank", "main_battle_tank", "tank_destroyer" } }, 3);
                results[card] = mixed;
                results[card + " tanks"] = tanks;
                sb.AppendLine($"| {card} | {def.CpCost} | {def.MaxHp:0} | {mixed:0.0} | {mixed / def.CpCost:0.00} | {tanks:0.0} | {tanks / def.CpCost:0.00} |");
            }
            Lab.Write("bulldozer_sponge", sb.ToString());
            // Within one salvo of the attackers (5 %): deaths fall on their salvos, so a few hundred health either way
            // often changes nothing; with the same health, the turtle's drone armour and mine immunity are its edge.
            Assert.LessOrEqual(results["armored_bulldozer"], results["turtle_tank"] * 1.05f, "the turtle stays the better sponge under mixed fire");
            Assert.LessOrEqual(results["armored_bulldozer tanks"], results["turtle_tank tanks"] * 1.05f, "and under tank fire");
            Assert.LessOrEqual(Lab.Catalog.Vehicle("armored_bulldozer").MaxHp, Lab.Catalog.Vehicle("turtle_tank").MaxHp, "no more health than the turtle");
        }

        /// <summary>The SP gun's damage a second with shoot-and-scoot against the same gun held in place (the move's cost).</summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void ShootAndScootCostsLittleFire()
        {
            Lab.Gate();
            var ground = new[] { "main_battle_tank", "ifv", "armored_car" };
            var scoots = Lab.Dps(new Lab.Duel { Shooter = "artillery", Targets = ground, Moving = false }, 3);
            var held = Lab.Dps(new Lab.Duel
            {
                Shooter = "artillery", Targets = ground, Moving = false,
                Each = (world, shooters, targets) => { foreach (var s in shooters) s.ScootShots = 0; },
            }, 3);
            Lab.Write("sp_scoot", $"| SP howitzer | damage a second |\n|---|---|\n| held in place | {held:0} |\n| shoot-and-scoot | {scoots:0} ({Lab.Pct(scoots / held - 1f)}) |\n");
            Assert.Greater(scoots, held * 0.75f, "the move costs at most a quarter of its fire");
        }

        /// <summary>
        /// A base of one tower in Legendary tower gear against the mixed base in the same gear (I.9):
        /// gear must not make a one-tower base the answer to everything.
        /// </summary>
        [Test, Category("Balance"), Timeout(7200000)]
        public void LegendaryTowerGearDoesNotCrownAOneTowerBase()
        {
            Lab.Gate();
            var catalog = Lab.Catalog;
            var rng = new Random(11);
            var gear = new Dictionary<string, VehicleBoost>();
            VehicleBoost GearFor(VehicleDef def)
            {
                if (def.Fort is not { Kind: FortKind.Tower }) return VehicleBoost.None;
                if (gear.TryGetValue(def.Id, out var b)) return b;
                var need = new[] { TowerFit.Of(def) };
                var pieces = new List<GearItem>();
                foreach (var slot in Gear.TowerSlots)
                {
                    GearItem piece = null;
                    for (var tries = 0; tries < 200 && piece == null; tries++)
                    {
                        var p = Gear.CreateTower(Rarity.Legendary, rng, 1 + tries, need);
                        if ((GearSlot)p.slot == slot) piece = p;
                    }
                    if (piece != null) pieces.Add(piece);
                }
                return gear[def.Id] = Gear.TowerBoost(10, pieces);
            }
            var bases = new Dictionary<string, BaseLoadout> { ["mixed"] = BaseBalanceTests.Mixed() };
            foreach (var t in new[] { "gun_turret", "atgm_tower", "rocket_turret", "heavy_turret" }) bases["only " + t] = BaseBalanceTests.OnlyOf(catalog, t);
            var sb = new StringBuilder("| base (Legendary tower gear) |");
            foreach (var e in BaseBalanceTests.Enemies.Keys) sb.Append($" {e} |");
            sb.AppendLine();
            sb.Append("|---|");
            foreach (var _ in BaseBalanceTests.Enemies.Keys) sb.Append("---|");
            sb.AppendLine();
            var table = new Dictionary<(string, string), float>();
            foreach (var (name, loadout) in bases)
            {
                sb.Append($"| {name} |");
                foreach (var (enemy, army) in BaseBalanceTests.Enemies)
                {
                    var score = Enumerable.Range(1, 3).Average(s => BaseBalanceTests.Battle(catalog, loadout, army, s, 5f, out _, GearFor));
                    table[(name, enemy)] = score;
                    sb.Append($" {score:0.00} |");
                }
                sb.AppendLine();
            }
            sb.AppendLine();
            sb.AppendLine("Score: HQ health left plus share of the attackers destroyed (0-2), 3 seeds, 5 minutes.");
            Lab.Write("tower_gear_mono", sb.ToString());
            foreach (var name in bases.Keys.Where(n => n != "mixed"))
                Assert.IsTrue(BaseBalanceTests.Enemies.Keys.Any(e => bases.Keys.Any(o => o != name && table[(o, e)] > table[(name, e)])),
                    $"{name} in Legendary gear is not the best base against every army");
        }
    }
}
