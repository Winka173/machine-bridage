using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Deathmatch, King of the Hill and Assault played out AI against AI with the shipped content.</summary>
    public class QuickModeTests
    {
        private static SideSetup Side(float cp, float income) => new()
        {
            StartCp = cp, Income = income, Vehicles = MatchSettings.AllVehicles, Supports = MatchSettings.AllSupports,
        };

        private static (int kills, float minutes) Play(SimWorld world, IGameMode mode, ConquestAi a, ConquestAi b, float limitMinutes)
        {
            var kills = 0;
            var seconds = 0f;
            const float step = 0.05f;
            for (; seconds < limitMinutes * 60f && mode.Result == null; seconds += step)
            {
                mode.Tick(world, step);
                a.Tick(world, step);
                b.Tick(world, step);
                world.Step(step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.VehicleDestroyed) kills++;
                world.ClearEvents();
            }
            return (kills, seconds / 60f);
        }

        [Test]
        public void DeathmatchEndsWhenASideReachesTheKillTarget()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("dunebreak_conquest"), seed: 31);
            var mode = new DeathmatchMode(new DeathmatchRules { KillTarget = 25, Player = Side(18f, 1.35f), Enemy = Side(18f, 1.35f) });
            mode.Setup(world);
            var (kills, minutes) = Play(world, mode, new ConquestAi(null, 0, 1, AiDifficulty.Hard, 3), new ConquestAi(null, 1, 0, AiDifficulty.Normal, 4), 14f);
            Debug.Log($"Deathmatch: {minutes:0.0} min, kills {mode.Kills(0)}:{mode.Kills(1)}, destroyed {kills}");
            Assert.IsNotNull(mode.Result, "a deathmatch ends");
            Assert.IsTrue(mode.Kills(0) >= 25 || mode.Kills(1) >= 25 || world.Time >= 12 * 60, "by the kill target or the clock");
        }

        [Test]
        public void KingOfTheHillIsDecidedAtTheCentre()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 32);
            var mode = new KingOfTheHillMode(new KingOfTheHillRules { Player = Side(16f, 1.2f), Enemy = Side(16f, 1.2f) });
            mode.Setup(world);
            Assert.AreEqual(1, mode.Points.Count, "one hill");
            Assert.AreEqual("town", mode.Points[0].Def.Id);
            var (kills, minutes) = Play(world, mode, new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5), new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 6), 16f);
            Debug.Log($"King of the Hill: {minutes:0.0} min, score {mode.Score(0)}:{mode.Score(1)}, destroyed {kills}");
            Assert.IsNotNull(mode.Result, "the hill battle ends");
            Assert.Greater(mode.Score(0) + mode.Score(1), 30, "the hill is held for real");
            Assert.Greater(kills, 10, "and fought over");
        }

        [Test]
        public void AssaultStartsWithTheDefenderHoldingEverything()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ironport_conquest"), seed: 33);
            var mode = new AssaultMode(new AssaultRules
            {
                Attacker = Side(20f, 1.45f), Defender = Side(26f, 1.05f),
            });
            mode.Setup(world);
            foreach (var p in mode.Points) Assert.AreEqual(1, p.Owner, "the defender owns every objective at the start");
            Assert.AreEqual(3, mode.SectorCount, "three sectors");
            Assert.AreEqual(2, mode.SectorPoints(1).Count, "B has two points");
            Assert.IsFalse(mode.SectorPoints(0)[0].Locked, "only the front sector is live");
            Assert.IsTrue(mode.SectorPoints(1).All(p => p.Locked) && mode.SectorPoints(2).All(p => p.Locked));
            world.TryGetRally(0, out var from);
            world.TryGetRally(1, out var to);
            var depth = new float[3];
            for (var s = 0; s < 3; s++)
                depth[s] = mode.SectorPoints(s).Average(p => System.Numerics.Vector2.Distance(p.Def.Position, from));
            Assert.Less(depth[0], depth[1], "sectors lie one behind the other");
            Assert.Less(depth[1], depth[2]);
            Assert.GreaterOrEqual(System.Numerics.Vector2.Distance(mode.SectorPoints(2)[0].Def.Position, to), 40f, "C well short of the camp");
            Assert.GreaterOrEqual(world.VehicleList.Count(v => v.Team == 1 && v.Def.Static), 7, "each sector dug in");
            var attacker = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 7) { Stance = CommanderStance.Attack };
            var defender = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 8) { Stance = CommanderStance.Defend };
            var (kills, minutes) = Play(world, mode, attacker, defender, 18f);
            Debug.Log($"Assault: {minutes:0.0} min, sector {mode.Sector + 1}/{mode.SectorCount}, taken {mode.Taken}/{mode.Points.Count}, result {mode.Result?.WinningTeam}, destroyed {kills}");
            Assert.IsNotNull(mode.Result, "an assault ends by capture or by the clock");
            Assert.Greater(kills, 10, "there is a real fight");
        }

        [Test]
        public void DefendIsTheSameBreakthroughWithTheSidesSwapped()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 34);
            var mode = new AssaultMode(new AssaultRules
            {
                PlayerDefends = true, StartSeconds = 360f, Attacker = Side(28f, 1.5f), Defender = Side(20f, 1.1f),
            });
            mode.Setup(world);
            Assert.AreEqual(1, mode.Attacker);
            Assert.AreEqual(0, mode.Defender);
            foreach (var p in mode.Points) Assert.AreEqual(0, p.Owner, "the player holds every sector at the start");
            world.TryGetRally(0, out var home);
            var depth = new float[3];
            for (var s = 0; s < 3; s++) depth[s] = mode.SectorPoints(s).Average(p => System.Numerics.Vector2.Distance(p.Def.Position, home));
            Assert.Greater(depth[0], depth[1], "sector A is the farthest from the player's camp");
            Assert.Greater(depth[1], depth[2], "and C the nearest");
            Assert.GreaterOrEqual(world.VehicleList.Count(v => v.Team == 0 && v.Def.Static), 7, "the player's sectors are dug in");
            var attacker = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 9) { Stance = CommanderStance.Attack };
            var defender = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 10) { Stance = CommanderStance.Defend };
            var (kills, minutes) = Play(world, mode, attacker, defender, 18f);
            Debug.Log($"Defend: {minutes:0.0} min, enemy at sector {mode.Sector + 1}/{mode.SectorCount}, result {mode.Result?.WinningTeam}, destroyed {kills}");
            Assert.IsNotNull(mode.Result, "a defence ends");
            Assert.Greater(kills, 10, "there is a real fight");
        }
    }
}
