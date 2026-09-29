using System.Collections.Generic;
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
    /// Test feedback 2 (DECISIONS 12F): aircraft use their weapons' reach and magazines. A fighter
    /// hovers on a helicopter and streams its cannon, an attack jet hangs on a tank with its nose on
    /// it, passes over and comes round again, neither hangs inside a flak gun's reach, and an attack
    /// helicopter comes in until its gun reaches.
    /// </summary>
    public class AirAttackTests
    {
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 240f,
                new[] { new TeamStart(0, new Vector2(-100f, -100f)), new TeamStart(1, new Vector2(100f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 3);

        private sealed class Log
        {
            public readonly Dictionary<string, int> Rounds = new();
            public readonly Dictionary<string, double> Longest = new();
            private readonly Dictionary<string, (double start, double last)> _run = new();
            public float Slowest = float.MaxValue, SlowestInHold = float.MaxValue;
            public int Holds, ClosePasses;

            public void Fired(string weapon, double at)
            {
                Rounds[weapon] = (Rounds.TryGetValue(weapon, out var n) ? n : 0) + 1;
                var run = _run.TryGetValue(weapon, out var r) && at - r.last <= 0.36 ? (r.start, at) : (at, at);
                _run[weapon] = run;
                Longest[weapon] = System.Math.Max(Longest.TryGetValue(weapon, out var l) ? l : 0, run.Item2 - run.Item1);
            }

            public int Of(string weapon) => Rounds.TryGetValue(weapon, out var n) ? n : 0;
            public double StreamOf(string weapon) => Longest.TryGetValue(weapon, out var l) ? l : 0;
        }

        /// <summary>Sends <paramref name="shooter"/> at <paramref name="target"/> (which never fires back or dies) and logs its attack.</summary>
        private static Log Attack(SimWorld world, Vehicle shooter, Vehicle target, float seconds)
        {
            world.MakeDummy(target);
            target.HoldFire = true;
            world.Submit(new Command(CommandType.AttackMove, 0, new[] { shooter.Id }, target.Position));
            var log = new Log();
            bool wasHold = false, wasClose = false;
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == shooter.Id) log.Fired(e.DefId, world.Time);
                world.ClearEvents();
                target.Hp = target.MaxHp;
                if (world.Time < 2.0) continue;
                log.Slowest = System.MathF.Min(log.Slowest, shooter.Speed);
                if (shooter.InAttackHold) log.SlowestInHold = System.MathF.Min(log.SlowestInHold, shooter.Speed);
                if (shooter.InAttackHold && !wasHold) log.Holds++;
                wasHold = shooter.InAttackHold;
                var close = Vector2.Distance(shooter.Position, target.Position) < 10f;
                if (close && !wasClose) log.ClosePasses++;
                wasClose = close;
            }
            return log;
        }

        [Test]
        public void TheFighterHoversOnAHelicopterAndStreamsItsCannonUntilItDies()
        {
            var world = Field();
            var fighter = world.SpawnVehicle("fighter_jet", 0, new Vector2(0f, -35f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 35f), 3.14f);
            var log = Attack(world, fighter, heli, 30f);
            Assert.Less(log.SlowestInHold, fighter.Def.Speed * 0.05f, "it hovers");
            Assert.GreaterOrEqual(log.StreamOf("fighter_cannon"), 3.0, "its cannon streams most of a magazine at a time");
            // Play-test 6 (DECISIONS 21F): out of flak it no longer breaks away every hold, it hangs on the helicopter until it dies.
            Assert.GreaterOrEqual(log.Holds, 1, "it holds on the helicopter");
            Assert.Greater(log.Of("fighter_cannon"), 150, "and keeps streaming on it instead of looping away");
            Assert.Greater(log.Of("wvr_aam") + log.Of("air_to_air"), 3, "its missiles are fired too");
        }

        [Test]
        public void AnAttackJetHangsOnATankThenPassesOverItAndComesRound()
        {
            var world = Field();
            var jet = world.SpawnVehicle("attack_jet", 0, new Vector2(0f, -35f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 35f), 3.14f);
            var log = Attack(world, jet, tank, 30f);
            Assert.Less(log.SlowestInHold, jet.Def.Speed * 0.3f, "it slows to a crawl on the target");
            Assert.Greater(log.Slowest, jet.Def.Speed * 0.1f, "but never stops dead (it is no VTOL)");
            Assert.GreaterOrEqual(log.StreamOf("jet_cannon"), 1.8, "its cannon streams for seconds, not a blip");
            Assert.GreaterOrEqual(log.Of("jet_bombs"), 2, "its bombs still drop");
            Assert.Greater(log.Of("s8_pods"), 0, "and its rockets fire");
            Assert.GreaterOrEqual(log.Holds, 3, "it comes round for more");
            Assert.GreaterOrEqual(log.ClosePasses, 3, "each hold ends passing over the target");
        }

        [Test]
        public void NoJetHangsInsideAFlakGunsReach()
        {
            var world = Field();
            var jet = world.SpawnVehicle("attack_jet", 0, new Vector2(0f, -35f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 35f), 3.14f);
            var flak = world.SpawnVehicle("aa_vehicle", 1, new Vector2(8f, 40f), 3.14f);
            world.MakeDummy(flak);
            var log = Attack(world, jet, tank, 20f);
            Assert.Greater(log.Holds, 0, "it still attacks");
            Assert.GreaterOrEqual(log.SlowestInHold, jet.Def.Speed * 0.45f, "under flak it makes a quicker run instead of hanging there");
        }

        [Test]
        public void AnAttackHelicopterComesInUntilItsGunReaches()
        {
            var world = Field();
            var heli = world.SpawnVehicle("attack_helicopter", 0, new Vector2(0f, -25f), 0f);
            var ifv = world.SpawnVehicle("ifv", 1, new Vector2(0f, 25f), 3.14f);
            var log = Attack(world, heli, ifv, 20f);
            Assert.Greater(log.Of("heli_gun"), 20, "its gun fires (it no longer holds at its missile's reach)");
            Assert.Greater(log.Of(heli.Def.Weapon.Id), 1, "and its missiles");
            Assert.Less(Vector2.Distance(heli.Position, ifv.Position) - ifv.Radius, heli.Def.Mounts[1].Weapon.Range, "it hovers within its gun's reach");
        }
    }
}
