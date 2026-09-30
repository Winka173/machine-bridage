using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 17 C: one behaviour test for each new unit and tower (the brief's E list): the stealth fighter's
    /// reveal and detection, the wingman pulling missiles, the laser's ramp and its reset, the shield domes (they
    /// absorb, energy goes through, they never add up), the bunker vehicle's states and timings, the swarm
    /// carrier's drones outside the aircraft cap, and the CP relay's pay, its two-a-base cap and that the AI does
    /// not take it everywhere.
    /// </summary>
    public class Prompt17ContentTests
    {
        private static SimWorld Field(float size = 240f) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-100f, -100f)), new TeamStart(1, new Vector2(100f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        /// <summary>Steps the world; <paramref name="each"/> runs after every step with its events.</summary>
        private static void Run(SimWorld world, float seconds, System.Action<SimEvent> seen = null, System.Action each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                if (seen != null)
                    foreach (var e in world.Events) seen(e);
                world.ClearEvents();
                each?.Invoke();
            }
        }

        /// <summary>A hit of <paramref name="damage"/> on <paramref name="v"/> by a round that pierces anything (a 120 mm dart, a laser, a 203 mm shell), from far off to the north.
        /// <paramref name="round"/> names another round (prompt 25: the main battle tank's front is 4, which the long 120 mm's pen 5 pierces whole).</summary>
        private static float Hit(SimWorld world, Vehicle v, float damage, DamageType type, string round = null)
        {
            var weapon = world.Catalog.Weapons[round ?? type switch { DamageType.Energy => "focus_laser", DamageType.HighExplosive => "gun_203_siege", _ => "gun_120mm" }];
            return world.Damage.Apply(v, damage, type, new MachineBrigade.Sim.Combat.HitInfo(null, 1, weapon, v.Position + new Vector2(0f, 60f), MachineBrigade.Sim.Combat.HitKind.Direct, false));
        }

        private static void Pin(Vehicle v, Vector2 at, float heading)
        {
            v.Position = at;
            v.Heading = heading;
        }

        [Test]
        public void TheStealthFighterShowsOnlyCloseUpAfterFiringOrToScansAndRadar()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            var spotter = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var stealth = world.SpawnVehicle("stealth_fighter", 1, new Vector2(20f, 0f), 0f);
            var plain = world.SpawnVehicle("fighter_jet", 1, new Vector2(-20f, 0f), 0f);
            // Held fire, so that only the test decides when it fires (its bombs could reach the tank).
            stealth.HoldFire = true;
            world.Submit(new Command(CommandType.Stop, 1, new[] { stealth.Id, plain.Id }));
            void Hold()
            {
                Pin(stealth, new Vector2(20f, 0f), 0f);
                Pin(plain, new Vector2(-20f, 0f), 0f);
                spotter.Hp = spotter.MaxHp;
            }
            Run(world, 1f, each: Hold);
            Assert.IsTrue(plain.IsVisibleTo(0), "a fighter 20 m off a tank that sees 30 m shows");
            Assert.IsFalse(stealth.IsVisibleTo(0), "the stealth fighter does not (it shows at 0.4 of a spotter's sight)");
            stealth.LastFiredAt = world.Time;
            Run(world, 0.2f, each: Hold);
            Assert.IsTrue(stealth.IsVisibleTo(0), "its bay doors open as it fires: it shows");
            Run(world, 3f, each: Hold);
            Assert.IsFalse(stealth.IsVisibleTo(0), "and is gone again a few seconds later");
            Assert.IsTrue(world.Submit(Command.Strike(0, "uav_scan", new Vector2(20f, 0f))).Accepted);
            Run(world, 2.5f, each: Hold);
            Assert.IsTrue(stealth.IsVisibleTo(0), "a UAV scan shows it");

            // A base's radar station: stealth over the base shows.
            var catalog = GameContent.LoadCatalog();
            var based = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            var b = based.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Utilities = { "radar_station" } }, BaseRole.Anchor);
            var over = based.SpawnVehicle("stealth_fighter", 1, b.HqPosition + new Vector2(10f, 0f), 0f);
            based.Submit(new Command(CommandType.Stop, 1, new[] { over.Id }));
            Run(based, 1f, each: () => Pin(over, b.HqPosition + new Vector2(10f, 0f), 0f));
            Assert.IsTrue(over.IsVisibleTo(0), "a radar station shows stealth over its base");
        }

        [Test]
        public void TheWingmanFliesWithItsLeaderAndPullsSomeMissilesOntoItself()
        {
            var world = Field();
            var fighter = world.SpawnVehicle("fighter_jet", 1, new Vector2(0f, 40f), 0f);
            var wingman = world.SpawnVehicle("wingman_drone", 1, new Vector2(8f, 30f), 0f);
            var sam = world.SpawnVehicle("sam_launcher", 0, new Vector2(0f, 0f), 0f);
            var second = world.SpawnVehicle("sam_launcher", 0, new Vector2(10f, 0f), 0f);
            world.Submit(new Command(CommandType.Stop, 1, new[] { fighter.Id }));
            // Neither can be shot down here (a Buk takes a wingman in one hit): the test counts where the missiles go.
            world.MakeSparring(fighter);
            world.MakeSparring(wingman);
            var atFighter = 0;
            var atWingman = 0;
            void Seen(SimEvent e)
            {
                if (e.Kind != SimEventKind.WeaponFired || (e.Entity != sam.Id && e.Entity != second.Id)) return;
                if (e.Other == fighter.Id) atFighter++;
                else if (e.Other == wingman.Id) atWingman++;
            }
            // The launchers are told to shoot the fighter only: a missile at the wingman was pulled onto it.
            void Hold()
            {
                fighter.Hp = fighter.MaxHp;
                wingman.Hp = wingman.MaxHp;
                sam.Hp = sam.MaxHp;
                second.Hp = second.MaxHp;
                Pin(fighter, new Vector2(0f, 40f), 1.57f);
                fighter.Speed = 0f;
                if (world.Tick % 20 == 1) world.Submit(new Command(CommandType.Attack, 0, new[] { sam.Id, second.Id }, default, fighter.Id));
            }
            Run(world, 3f, Seen, Hold);
            Assert.AreEqual(fighter.Id, wingman.WingLeader, "the wingman takes the nearest manned aircraft of its side as its leader");
            Assert.Less(Vector2.Distance(wingman.Position, fighter.Position), 35f, "and keeps near it");
            Run(world, 60f, Seen, Hold);
            Assert.Greater(atFighter + atWingman, 6, "the launchers fired");
            Assert.Greater(atWingman, 0, "some missiles aimed at the fighter turned onto its wingman");
            Assert.Greater(atFighter, 0, "not all of them");
            Assert.AreEqual(1, world.Economy.AircraftCount(1), "the wingman is outside the aircraft cap");
        }

        [Test]
        public void TheLaserRampsUpOnOneTargetAndStartsAgainOnAnother()
        {
            var world = Field();
            var laser = world.SpawnVehicle("laser_tank", 0, Vector2.Zero, 0f);
            var first = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 25f), 3.14159f);
            var second = world.SpawnVehicle("main_battle_tank", 1, new Vector2(8f, 25f), 3.14159f);
            world.MakeDummy(first);
            world.MakeDummy(second);
            var hits = new List<(double at, EntityId who, float damage)>();
            Run(world, 0.1f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { laser.Id }, default, first.Id));
            Run(world, 9f, e =>
            {
                if (e.Kind == SimEventKind.Damaged && (e.Entity == first.Id || e.Entity == second.Id)) hits.Add((world.Time, e.Entity, e.Value));
            });
            var onFirst = hits.Where(h => h.who == first.Id).ToList();
            Assert.Greater(onFirst.Count, 40, "the beam stays on its target");
            var opening = onFirst[0].damage;
            var peak = onFirst.Max(h => h.damage);
            Assert.AreEqual(2f / 0.3f, peak / opening, 0.7f, "x0.3 at first, x2 after six seconds on the same target");
            Assert.Less(onFirst.First(h => h.damage >= peak * 0.99f).at - onFirst[0].at, 6.5, "at full power within about six seconds");
            hits.Clear();
            world.Submit(new Command(CommandType.Attack, 0, new[] { laser.Id }, default, second.Id));
            Run(world, 2f, e =>
            {
                if (e.Kind == SimEventKind.Damaged && e.Entity == second.Id) hits.Add((world.Time, e.Entity, e.Value));
            });
            Assert.IsNotEmpty(hits, "it turns on the new target");
            Assert.AreEqual(opening, hits[0].damage, opening * 0.15f, "a new target starts again at x0.3");
        }

        [Test]
        public void TheShieldCarriersDomeTakesHitsButNotEnergyAndDomesNeverAddUp()
        {
            var world = Field();
            var carrier = world.SpawnVehicle("shield_carrier", 0, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(5f, 0f), 0f);
            var outside = world.SpawnVehicle("main_battle_tank", 0, new Vector2(20f, 0f), 0f);
            Run(world, 0.2f);
            var full = carrier.DomeHp;
            Assert.AreEqual(1000f, full, 1f, "the dome is up at full when it arrives");
            var hp = tank.Hp;
            Hit(world, tank, 400f, DamageType.Kinetic, "turret_gun_120_long");
            Assert.AreEqual(hp, tank.Hp, 0.01f, "a tank 5 m from the carrier takes nothing: the dome does");
            Assert.AreEqual(full - 400f, carrier.DomeHp, 1f);
            var far = outside.Hp;
            Hit(world, outside, 100f, DamageType.Kinetic);
            Assert.Less(outside.Hp, far, "20 m away is outside the 12 m dome");
            Hit(world, tank, 150f, DamageType.Energy);
            Assert.Less(tank.Hp, hp, "energy goes through the dome");
            Assert.AreEqual(full - 400f, carrier.DomeHp, 1f, "and does not touch it");

            // Two domes over one tank: one takes a hit, and what it cannot take goes through (not to the second).
            var second = world.SpawnVehicle("shield_carrier", 0, new Vector2(8f, 3f), 0f);
            Run(world, 0.1f);
            hp = tank.Hp;
            var left = carrier.DomeHp;
            var fuller = second.DomeHp >= left ? second : carrier;
            var other = fuller == second ? carrier : second;
            Hit(world, tank, 1300f, DamageType.Kinetic, "turret_gun_120_long");
            Assert.AreEqual(0f, fuller.DomeHp, 1f, "the dome with the most left takes the hit and breaks");
            Assert.AreEqual(other == carrier ? left : 1000f, other.DomeHp, 1f, "the other dome is not touched: domes never add up");
            Assert.Less(tank.Hp, hp - 100f, "what the breaking dome could not take hits the tank");
            Assert.IsFalse(fuller.DomeUp);
            // Back at full 20 s after its last hit.
            Run(world, 19f);
            Assert.IsFalse(fuller.DomeUp, "still down before 20 s");
            Run(world, 1.5f);
            Assert.IsTrue(fuller.DomeUp, "back after 20 s");
            Assert.AreEqual(1000f, fuller.DomeHp, 1f);

            // In battle: an enemy tank's rounds on the covered tank land on the dome.
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(5f, 28f), 3.14159f);
            hp = tank.Hp;
            var dome = carrier.DomeHp + second.DomeHp;
            world.Submit(new Command(CommandType.Attack, 1, new[] { enemy.Id }, default, tank.Id));
            Run(world, 12f, each: () => { carrier.Hp = carrier.MaxHp; second.Hp = second.MaxHp; enemy.Hp = enemy.MaxHp; });
            Assert.Less(carrier.DomeHp + second.DomeHp, dome, "the enemy's shells hit the dome");
            Assert.AreEqual(hp, tank.Hp, 0.01f, "not the tank under it");
        }

        [Test]
        public void TheShieldGeneratorCoversPartOfTheBaseAndIsWhatTheEnemyShootsFirst()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(SlotSize.Large, catalog.Vehicles["shield_tower"].Fort.Size, "a large-slot tower");
            var branches = TowerCards.Branches(catalog, "shield_tower");
            Assert.AreEqual(2, branches.Count, "two rank-7 branches");
            // The tower-branch rework (DECISIONS 19T): A a stronger dome over the same area, B no dome but tower shields.
            Assert.AreEqual(catalog.Vehicles["shield_tower"].Dome.Radius, catalog.Vehicles["shield_tower.bulwark"].Dome.Radius, 0.01f, "the shield dome covers the area...");
            Assert.Greater(catalog.Vehicles["shield_tower.bulwark"].Dome.Hp, catalog.Vehicles["shield_tower"].Dome.Hp, "...and is tougher");
            Assert.IsNull(catalog.Vehicles["shield_tower.ward"].Dome, "the tower shields branch has no dome");
            Assert.IsNotNull(catalog.Vehicles["shield_tower.ward"].Wards, "but a shield on every tower near it");

            var world = Field();
            var generator = world.SpawnVehicle("shield_tower", 0, Vector2.Zero, 0f);
            world.AnchorDefence(generator);
            var covered = world.SpawnVehicle("gun_turret", 0, new Vector2(18f, 0f), 0f);
            world.AnchorDefence(covered);
            var bare = world.SpawnVehicle("gun_turret", 0, new Vector2(34f, 0f), 0f);
            world.AnchorDefence(bare);
            Run(world, 0.2f);
            var hp = covered.Hp;
            Hit(world, covered, 500f, DamageType.HighExplosive);
            Assert.AreEqual(hp, covered.Hp, 0.01f, "a tower 18 m from the generator is under its 25 m dome");
            hp = bare.Hp;
            Hit(world, bare, 500f, DamageType.HighExplosive);
            Assert.Less(bare.Hp, hp, "34 m is not");

            // An enemy with the generator and a covered tower in reach goes for the generator.
            var attacker = world.SpawnVehicle("main_battle_tank", 1, new Vector2(9f, 26f), 3.14159f);
            world.Submit(new Command(CommandType.Stop, 1, new[] { attacker.Id }));
            Run(world, 1f, each: () => { covered.Hp = covered.MaxHp; generator.Hp = generator.MaxHp; attacker.Hp = attacker.MaxHp; });
            Assert.AreEqual(generator.Id, attacker.Target, "the generator first");
            // The enemy base picker places it (a large slot) now and then.
            var placed = Enumerable.Range(1, 30).Count(seed => BaseLoadout.ForAi(catalog, "Hard", "default", seed).Large.Contains("shield_tower"));
            Assert.Greater(placed, 0, "the AI puts a shield generator in its base");
        }

        [Test]
        public void TheBunkerVehicleDigsInAndPacksUpInThreeSecondsEach()
        {
            var world = Field();
            var bunker = world.SpawnVehicle("bunker_vehicle", 0, Vector2.Zero, 0f);
            var target = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 28f), 3.14159f);
            world.MakeDummy(target);
            world.Submit(new Command(CommandType.Stop, 0, new[] { bunker.Id }));
            var fired = new List<double>();
            void Seen(SimEvent e)
            {
                if (e.Kind == SimEventKind.WeaponFired && e.Entity == bunker.Id) fired.Add(world.Time);
            }
            Assert.AreEqual(2f, bunker.ArmourOn(ArmorFace.Front), "front level 2 on its tracks");
            double began = -1, dug = -1;
            Run(world, 6f, Seen, () =>
            {
                if (began < 0 && bunker.Deploy == DeployState.Deploying) began = world.Time;
                if (dug < 0 && bunker.Deploy == DeployState.Deployed) dug = world.Time;
            });
            Assert.Greater(began, 0, "standing with an enemy in its dug-in reach, it digs in");
            Assert.AreEqual(3.0, dug - began, 0.11, "in 3 s");
            Assert.IsFalse(fired.Any(t => t >= began && t < dug), "not firing while it digs in");
            Assert.AreEqual(4f, bunker.ArmourOn(ArmorFace.Front), "dug in: front two levels thicker");
            Assert.AreEqual(1.3f, bunker.RangeFactor, 1e-3f, "and 30 % more reach");
            Assert.IsTrue(fired.Any(t => t > dug), "dug in, it fires again");

            fired.Clear();
            var at = bunker.Position;
            world.Submit(new Command(CommandType.Move, 0, new[] { bunker.Id }, new Vector2(-30f, 0f)));
            double packed = -1;
            var start = world.Time;
            Run(world, 5f, Seen, () =>
            {
                if (packed < 0 && bunker.Deploy == DeployState.Mobile) packed = world.Time;
                if (bunker.Deploy == DeployState.Packing)
                {
                    Assert.AreEqual(2f, bunker.ArmourOn(ArmorFace.Front), "packing up it has its moving armour");
                    Assert.Less(Vector2.Distance(bunker.Position, at), 0.05f, "and does not move");
                }
            });
            Assert.AreEqual(3.0, packed - start, 0.2, "packing up takes 3 s");
            Assert.IsFalse(fired.Any(t => t < packed), "not firing while it packs up");
            Assert.Greater(Vector2.Distance(bunker.Position, at), 1f, "then it drives");
        }

        [Test]
        public void TheSwarmCarrierReleasesItsDronesOverTheTargetOutsideTheAircraftCap()
        {
            var world = Field();
            var carrier = world.SpawnVehicle("swarm_carrier", 0, new Vector2(0f, -60f), 0f);
            var others = Enumerable.Range(0, 5).Select(i => world.SpawnVehicle("scout_heli", 0, new Vector2(-90f + i * 6f, -90f), 0f)).ToList();
            world.Submit(new Command(CommandType.Stop, 0, others.Select(o => o.Id).ToArray()));
            var group = Enumerable.Range(0, 4).Select(i => world.SpawnVehicle("armored_car", 1, new Vector2(-9f + i * 6f, 20f), 0f)).ToList();
            foreach (var g in group) world.MakeDummy(g);
            Assert.AreEqual(6, world.Economy.AircraftCount(0), "the side has its six aircraft up");
            world.Submit(new Command(CommandType.Attack, 0, new[] { carrier.Id }, default, group[1].Id));
            var drones = new List<EntityId>();
            var at = new List<double>();
            var most = 0;
            // Play-test 6 (DECISIONS 21F): the drones go one after another, all through its passes (it was all eight at once).
            Run(world, 45f, e =>
            {
                if (e.Kind != SimEventKind.WeaponFired || e.Entity != carrier.Id || e.DefId != "swarm_drones") return;
                drones.Add(e.Other);
                at.Add(world.Time);
            }, () =>
            {
                carrier.Hp = carrier.MaxHp;
                most = System.Math.Max(most, world.Economy.AircraftCount(0));
            });
            Assert.GreaterOrEqual(drones.Count, 8, "a full load's eight FPV drones and more");
            Assert.GreaterOrEqual(drones.Distinct().Count(), 3, "they spread over the group, each to its own target");
            Assert.AreEqual(6, most, "the drones never count as aircraft");
            Assert.IsTrue(at.Zip(at.Skip(1), (x, y) => y - x).All(gap => gap > 0.5), "one at a time, never a wave");
        }

        [Test]
        public void TheCpRelayPaysTwoToABaseNotOnOutpostsAndIsNoMustPick()
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            world.EnableEconomy(new TeamEconomy(0, 0f, income: 1f, bank: 500f));
            var loadout = new BaseLoadout { HqLevel = 5, Small = { "cp_relay", "cp_relay", "cp_relay" } };
            Assert.AreEqual(2, loadout.Fitted(catalog).Small.Count(id => id == "cp_relay"), "two relays to a base: a third slot is left empty");
            world.Bases.Establish(0, loadout, BaseRole.Anchor);
            var relays = world.Bases.Towers(0).Where(t => t.Def.Relay != null).ToList();
            Assert.AreEqual(2, relays.Count);
            Run(world, 1f);
            world.TryGetEconomy(0, out var economy);
            Assert.AreEqual(0.1f + 0.06f, economy.Relay, 1e-4f, "+0.1 CP a second, the second relay +0.06");
            var cp = economy.Cp;
            Run(world, 10f);
            Assert.AreEqual((economy.Income + 0.16f * economy.IncomeScale) * 10f, economy.Cp - cp, 0.3f, "paid on top of the income");
            relays[0].LastHitTime = world.Time;
            Run(world, 0.1f);
            Assert.That(economy.Relay, Is.InRange(0.059f, 0.101f), "a relay under fire pays nothing for a while (the other still does)");
            Run(world, 5.5f);
            Assert.AreEqual(0.16f, economy.Relay, 1e-4f, "then pays again");
            Assert.IsFalse(BaseLayout.Fits(catalog, "cp_relay", LoadoutSlot.Outpost(0)), "never on an outpost");

            // The enemy AI puts relays in some of its bases, never more than two, and not in every one.
            var withRelay = 0;
            for (var seed = 1; seed <= 40; seed++)
            {
                var ai = BaseLoadout.ForAi(catalog, "Hard", "default", seed).Fitted(catalog);
                var n = ai.Towers.Count(id => id == "cp_relay");
                Assert.LessOrEqual(n, 2, $"seed {seed}");
                if (n > 0) withRelay++;
            }
            Assert.Greater(withRelay, 0, "the AI takes relays sometimes");
            Assert.Less(withRelay, 40, "but not in every base");
        }
    }
}
