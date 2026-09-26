using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Plays the shipped sandbox with the real content and opponent, headless.</summary>
    public class SandboxBattleTests
    {
        [Test]
        public void EnemyWaveReachesThePlayerAndFights()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_sandbox"), seed: 1234);
            var mode = new SandboxMode();
            mode.Setup(world);
            var ai = new TacticalAi(SandboxMode.EnemyTeam, SandboxMode.PlayerTeam, seed: 1234);
            var playerHp = TeamHp(world, SandboxMode.PlayerTeam);

            const float step = 0.05f;
            for (var i = 0; i < 90 / step; i++)
            {
                mode.Tick(world, step);
                ai.Tick(world, step);
                world.Step(step);
                world.ClearEvents();
                if (i % 100 == 0) Debug.Log($"t={i * step:0}s {Describe(world)}");
            }

            Assert.Less(TeamHp(world, SandboxMode.PlayerTeam), playerHp, "the enemy should have attacked within 90 s");
        }

        private static float TeamHp(SimWorld world, int team)
        {
            var hp = 0f;
            foreach (var v in world.Vehicles)
                if (v.IsAlive && v.Team == team) hp += v.Hp;
            return hp;
        }

        private static string Describe(SimWorld world)
        {
            var text = "";
            foreach (var v in world.Vehicles)
                if (v.Team == SandboxMode.EnemyTeam)
                    text += $"{v.Def.Id}:{v.Order.Kind}({v.Position.X:0},{v.Position.Y:0}) ";
            return text;
        }
    }
}
