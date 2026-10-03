using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 5 (DECISIONS 20W): the autocannons' five-second streams, the jets' tail chase, the slower rockets and
    /// drones, the C-RAM's bursts, and the siege tank's two modes.
    /// </summary>
    public class PlayTest5Tests
    {
        private static SimWorld Field(int seed = 3) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 260f,
                new[] { new TeamStart(0, new Vector2(-110f, -110f)), new TeamStart(1, new Vector2(110f, 110f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        /// <summary>The longest run of a weapon's rounds (gaps of at most <paramref name="gap"/> s), in seconds.</summary>
        private sealed class Runs
        {
            private readonly Dictionary<string, (double start, double last)> _run = new();
            public readonly Dictionary<string, double> Longest = new();
            public readonly Dictionary<string, int> Rounds = new();

            public void Fired(string weapon, double at, double gap)
            {
                Rounds[weapon] = (Rounds.TryGetValue(weapon, out var n) ? n : 0) + 1;
                var run = _run.TryGetValue(weapon, out var r) && at - r.last <= gap ? (r.start, at) : (at, at);
                _run[weapon] = run;
                Longest[weapon] = System.Math.Max(Longest.TryGetValue(weapon, out var l) ? l : 0, run.Item2 - run.Item1);
            }

            public int Of(string w) => Rounds.TryGetValue(w, out var n) ? n : 0;
            public double StreamOf(string w) => Longest.TryGetValue(w, out var l) ? l : 0;
        }

        private static readonly string[] Autocannons =
        {
            "autocannon_30", "ifv_30", "flak_35", "autocannon_25", "jet_cannon", "twin_30_flak", "zu23", "twin_30_bmpt",
            "fighter_cannon", "twin_35_ahead", "heli_gun", "gunship_25mm", "gunship_40mm",
        };

        [Test]
        public void EveryVehicleAutocannonFiresAboutFiveSecondsThenChangesInAboutOne()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in Autocannons)
            {
                var w = catalog.Weapons[id];
                Assert.That((w.Clip - 1) * w.Cooldown, Is.InRange(4.8f, 5.2f), $"{id}: seconds of fire");
                Assert.AreEqual(1f, w.ClipReload, 1e-4f, $"{id}: the change");
            }
        }

        [Test]
        public void TheAntiAirVehicleStreamsForSecondsAtAHelicopter()
        {
            var world = Field();
            var aa = world.SpawnVehicle("aa_vehicle", 0, new Vector2(0f, -20f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 12f), 3.14f);
            world.MakeDummy(heli);
            heli.HoldFire = true;
            var runs = new Runs();
            for (var t = 0f; t < 20f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == aa.Id) runs.Fired(e.DefId, world.Time, 0.4);
                world.ClearEvents();
                heli.Hp = heli.MaxHp;
            }
            Assert.GreaterOrEqual(runs.StreamOf("flak_35"), 4.3, "the Gepard streams for about five seconds");
            Assert.Greater(runs.Of("flak_35"), 50, "and changes in about a second");
        }

        [Test]
        public void AFighterGetsOnAJetsTailAndStreamsItsCannon()
        {
            var world = Field();
            world.RevealAll = true;
            var fighter = world.SpawnVehicle("fighter_jet", 0, new Vector2(-40f, -80f), 0f);
            var jet = world.SpawnVehicle("attack_jet", 1, new Vector2(0f, 20f), 0f);
            jet.HoldFire = true;
            jet.HpScale = 50f;
            jet.Hp = jet.MaxHp;
            world.Submit(new Command(CommandType.Move, 1, new[] { jet.Id }, new Vector2(0f, 100f)));
            world.Submit(new Command(CommandType.Attack, 0, new[] { fighter.Id }, jet.Position, jet.Id));
            var runs = new Runs();
            var onTail = 0f;
            for (var t = 0f; t < 45f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == fighter.Id) runs.Fired(e.DefId, world.Time, 0.36);
                world.ClearEvents();
                jet.Hp = jet.MaxHp;
                if (fighter.OnTail) onTail += TestWorlds.Step;
            }
            Assert.Greater(onTail, 8f, "it sits on the jet's tail for a good part of the chase");
            Assert.GreaterOrEqual(runs.StreamOf("fighter_cannon"), 3.0, "and streams its cannon on it");
        }

        [Test]
        public void RocketsAndDronesFlyAtTheirNewSpeeds()
        {
            var w = GameContent.LoadCatalog().Weapons;
            var sam = w["sam"].ProjectileSpeed;
            foreach (var id in new[] { "thermobaric_rockets", "rockets_300mm", "turret_rockets", "turret_rockets_cluster", "turret_thermobaric", "turret_gmlrs" })
                Assert.AreEqual(sam, w[id].ProjectileSpeed, 1e-3f, id + " at the SAM's speed");
            // Play-test 6 (DECISIONS 21F): the attack jet's rockets and missiles another 20 % slower (36, 17.25 and 18 here).
            Assert.AreEqual(20.2f, w["s8_pods"].ProjectileSpeed, 1e-3f, "the attack jet's rockets slower (play-test 7: 30 % more)");
            Assert.AreEqual(9.7f, w["kh29"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(10.1f, w["r60"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(15.6f, w["mothership_drones"].ProjectileSpeed, 1e-3f, "the mothership's drones 40 % slower");
        }

        [Test]
        public void TheCRamStreamsABurstAtEveryRoundItDrops()
        {
            var world = Field();
            world.RevealAll = true;
            var target = world.SpawnVehicle("gun_turret", 0, Vector2.Zero, 0f);
            world.AnchorDefence(target);
            world.MakeSparring(target);
            target.HoldFire = true;
            var cram = world.SpawnVehicle("c_ram", 0, new Vector2(8f, -6f), 0f);
            world.AnchorDefence(cram);
            world.MakeSparring(cram);
            var mlrs = world.SpawnVehicle("mlrs", 1, new Vector2(0f, 60f), 3.14f);
            world.MakeSparring(mlrs);
            world.Submit(new Command(CommandType.Attack, 1, new[] { mlrs.Id }, target.Position, target.Id));
            var burst = new List<double>();
            var bursts = new List<int>();
            for (var t = 0f; t < 40f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Entity != cram.Id) continue;
                    if (e.Kind == SimEventKind.PointDefenceFired) burst.Add(world.Time);
                    if (e.Kind == SimEventKind.Intercepted)
                    {
                        var since = world.Time - 0.5;
                        bursts.Add(burst.Count(b => b >= since) * 3);
                    }
                }
                world.ClearEvents();
            }
            Assert.Greater(bursts.Count, 3, "it takes rockets down");
            Assert.That(bursts.Min(), Is.GreaterThanOrEqualTo(12), "each after a stream of rounds, never one shot: " + string.Join(",", bursts));
        }

        // ------------------------------------------------------------------ the siege tank

        [Test]
        public void TheSiegeTankSiegesForWhatItsMortarReachesAndOnlyTheMortarFires()
        {
            var world = Field();
            var siege = world.SpawnVehicle("siege_tank", 0, new Vector2(0f, -30f), 0f);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 30f), 3.14f);
            world.MakeDummy(enemy);
            enemy.HoldFire = true;
            enemy.VisibleToMask |= 1;
            var fired = new List<string>();
            var siegedAt = -1.0;
            for (var t = 0f; t < 25f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                enemy.VisibleToMask |= 1;
                if (siegedAt < 0 && siege.Deploy == DeployState.Deployed) siegedAt = world.Time;
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == siege.Id) fired.Add(e.DefId);
                world.ClearEvents();
                enemy.Hp = enemy.MaxHp;
            }
            Assert.That(siegedAt, Is.InRange(2.5, 6.0), "it sieges: a second standing, then 2.5 s of work");
            Assert.Greater(fired.Count(f => f == "siege_mortar_240"), 1, "the mortar shells the tank 60 m away");
            Assert.IsFalse(fired.Contains("siege_gun_105"), "the tank gun does not fire sieged (nor could it reach)");
        }

        [Test]
        public void TheSiegeTankFightsWithItsGunOnTheMoveAndNeverSiegesThere()
        {
            var world = Field();
            var siege = world.SpawnVehicle("siege_tank", 0, new Vector2(-10f, -40f), 0f);
            var enemy = world.SpawnVehicle("armored_car", 1, new Vector2(12f, 0f), 3.14f);
            world.MakeDummy(enemy);
            enemy.HoldFire = true;
            world.Submit(new Command(CommandType.Move, 0, new[] { siege.Id }, new Vector2(-10f, 40f)));
            var fired = new List<string>();
            var sieged = false;
            for (var t = 0f; t < 14f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                sieged |= siege.Deploy != DeployState.Mobile;
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == siege.Id) fired.Add(e.DefId);
                world.ClearEvents();
                enemy.Hp = enemy.MaxHp;
            }
            Assert.IsFalse(sieged, "on a move order it stays on its tracks");
            Assert.Greater(fired.Count(f => f == "siege_gun_105"), 1, "its 105 mm fires on the move");
            Assert.IsFalse(fired.Contains("siege_mortar_240"), "the mortar only sieged");
        }

        [Test]
        public void TheSiegeTankPacksUpToMoveAndWhenRushedInsideItsMortarsReach()
        {
            var world = Field();
            var siege = world.SpawnVehicle("siege_tank", 0, new Vector2(0f, -30f), 0f);
            var far = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 30f), 3.14f);
            world.MakeDummy(far);
            far.HoldFire = true;
            far.VisibleToMask |= 1;
            for (var t = 0f; t < 8f; t += TestWorlds.Step) world.Step(TestWorlds.Step);
            Assert.AreEqual(DeployState.Deployed, siege.Deploy, "sieged on the tank 60 m off");
            // The far tank goes; a car drives up inside the mortar's 16 m.
            world.RemoveQuietly(far);
            var car = world.SpawnVehicle("armored_car", 1, new Vector2(4f, -22f), 3.14f);
            world.MakeDummy(car);
            car.HoldFire = true;
            var gun = 0;
            var packed = false;
            for (var t = 0f; t < 12f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                packed |= siege.Deploy == DeployState.Packing;
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == siege.Id && e.DefId == "siege_gun_105") gun++;
                world.ClearEvents();
                car.Hp = car.MaxHp;
            }
            Assert.IsTrue(packed, "with nothing left to shell and a car inside its reach it packs up");
            Assert.Greater(gun, 0, "and fights it with its 105 mm");
            // Sieged again on a far target, then ordered on: it packs up and drives.
            world.RemoveQuietly(car);
            var other = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 35f), 3.14f);
            world.MakeDummy(other);
            other.HoldFire = true;
            other.VisibleToMask |= 1;
            for (var t = 0f; t < 8f; t += TestWorlds.Step) world.Step(TestWorlds.Step);
            Assert.AreEqual(DeployState.Deployed, siege.Deploy);
            var from = siege.Position;
            world.Submit(new Command(CommandType.Move, 0, new[] { siege.Id }, new Vector2(-40f, -40f)));
            for (var t = 0f; t < 1.5f; t += TestWorlds.Step) world.Step(TestWorlds.Step);
            Assert.AreEqual(DeployState.Packing, siege.Deploy, "a move order: it packs up first");
            Assert.Less(Vector2.Distance(from, siege.Position), 0.1f, "and does not drive while it does");
            for (var t = 0f; t < 6f; t += TestWorlds.Step) world.Step(TestWorlds.Step);
            Assert.AreEqual(DeployState.Mobile, siege.Deploy);
            Assert.Greater(Vector2.Distance(from, siege.Position), 3f, "then it drives");
        }

        [Test]
        public void TheSiegeTankCountsAsArtilleryForTheCounters()
        {
            var def = GameContent.LoadCatalog().Vehicle("siege_tank");
            Assert.AreEqual(UnitClass.Artillery, def.Class);
            Assert.Greater(def.Weapon.MinRange, 0f, "its main weapon is the mortar (the AI's artillery)");
            var weak = Counters.WeakVs(def.Class);
            foreach (var c in new[] { UnitClass.Light, UnitClass.Scout, UnitClass.Plane, UnitClass.Helicopter })
                CollectionAssert.Contains(weak, c, $"{c} catch it sieged");
            CollectionAssert.Contains(Counters.StrongVs(def).ToList(), UnitClass.Defense);
            Assert.IsTrue(def.Deploy is { Siege: true, TankMount: 1 });
            Assert.IsNotNull(Progression.UnlockMission("siege_tank"), "won in the campaign");
        }
    }
}
