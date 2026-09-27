using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Defend and Endless: the siege map's fortress is the player's base, and the enemy lays
    /// siege to it; the player holds until the clock runs out (Defend) or the HQ falls (Endless).
    /// </summary>
    public class DefendModeTests
    {
        private const float Step = 0.05f;

        private static (SimWorld world, SiegeMode mode) Fortress(bool endless, float seconds = 300f)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_siege"), seed: 4);
            var mode = new SiegeMode(new SiegeRules
            {
                PlayerDefends = true, Endless = endless, StartSeconds = seconds, WaveSeconds = 20f,
                Attacker = new SideSetup { StartCp = 0f, Income = 0.01f, Vehicles = new[] { "main_battle_tank", "apc" } },
                Defender = new SideSetup { StartCp = 20f, Income = 1f },
            });
            mode.Setup(world);
            return (world, mode);
        }

        [Test]
        public void TheFortressAndItsGunsAreThePlayers()
        {
            var (world, mode) = Fortress(endless: false);
            Assert.AreEqual(SiegeMode.PlayerTeam, mode.Defender);
            Assert.AreEqual(SiegeMode.EnemyTeam, mode.Attacker);
            Assert.IsTrue(mode.Fortress.HasValue);
            int ours = 0, theirs = 0;
            foreach (var v in world.VehicleList)
                if (v.Def.Static)
                {
                    if (v.Team == 0) ours++;
                    else if (v.Team == 1) theirs++;
                }
            Assert.Greater(ours, 4, "the fortress guns are the player's");
            Assert.AreEqual(0, theirs, "the enemy has no guns of its own");
            world.TryGetRally(0, out var home);
            world.TryGetRally(1, out var camp);
            var hq = mode.Fortress.Value;
            Assert.Less(Vector2.Distance(home, hq), Vector2.Distance(camp, hq), "the player's drop zone is the fortress");
            Assert.IsTrue(world.TryGetProp(mode.Target(world), out var objective) && objective.IsAlive, "the enemy has an objective to go for");
        }

        [Test]
        public void HoldingUntilTheClockRunsOutWins()
        {
            var (world, mode) = Fortress(endless: false, seconds: 30f);
            for (var t = 0f; t < 40f && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.AreEqual(SiegeMode.PlayerTeam, mode.Result?.WinningTeam, "the attacker ran out of time: the defender wins");
        }

        [Test]
        public void EndlessWavesKeepComingAndGrow()
        {
            var (world, mode) = Fortress(endless: true);
            var queued = 0;
            var alerts = 0;
            for (var t = 0f; t < 70f && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind == SimEventKind.DeploymentQueued && e.Team == 1) queued++;
                    if (e.Kind == SimEventKind.FortressAlert && e.DefId == "base.wave") alerts++;
                }
                world.ClearEvents();
            }
            Assert.IsNull(mode.Result, "no clock in Endless, and an enemy between waves has not lost");
            Assert.AreEqual(3, mode.Wave, "a wave every 20 seconds (the first a little sooner)");
            Assert.AreEqual(3, alerts);
            Assert.AreEqual(3 + 4 + 5, queued, "each wave one bigger than the last");
        }
    }
}
