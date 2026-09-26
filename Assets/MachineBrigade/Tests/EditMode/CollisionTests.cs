using System;
using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Vehicles collide as hulls (capsules along their heading) and do not drive through each other.</summary>
    public class CollisionTests
    {
        /// <summary>How deep two hulls sink into each other, in metres (0 when apart).</summary>
        private static float Penetration(Vehicle a, Vehicle b)
        {
            Spine(a, out var a0, out var a1);
            Spine(b, out var b0, out var b1);
            var best = float.MaxValue;
            // Sampled closest distance between the two spines (plenty precise for a test).
            for (var i = 0; i <= 8; i++)
            for (var j = 0; j <= 8; j++)
                best = MathF.Min(best, Vector2.Distance(Vector2.Lerp(a0, a1, i / 8f), Vector2.Lerp(b0, b1, j / 8f)));
            return MathF.Max(0f, a.Def.HullRadius + b.Def.HullRadius - best);
        }

        private static void Spine(Vehicle v, out Vector2 a, out Vector2 b)
        {
            var half = new Vector2(MathF.Sin(v.Heading), MathF.Cos(v.Heading)) * v.Def.HullHalf;
            a = v.Position - half;
            b = v.Position + half;
        }

        /// <summary>An empty 100 m field with the real vehicle catalog.</summary>
        private static SimWorld OpenField() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 100f,
                new[] { new TeamStart(0, new Vector2(-40f, -40f)), new TeamStart(1, new Vector2(40f, 40f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        [Test]
        public void ColumnOfTanksQueuesInsteadOfPilingUp()
        {
            var world = OpenField();
            var ids = new List<EntityId>();
            for (var i = 0; i < 6; i++) ids.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 4f - 10f, -30f), 0f).Id);
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 0, ids.ToArray(), new Vector2(0f, 20f)));
            var worst = 0f;
            for (var t = 0f; t < 25f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                for (var i = 0; i < ids.Count; i++)
                for (var j = i + 1; j < ids.Count; j++)
                {
                    world.TryGetVehicle(ids[i], out var a);
                    world.TryGetVehicle(ids[j], out var b);
                    worst = MathF.Max(worst, Penetration(a, b));
                }
            }
            Assert.Less(worst, 0.6f, "a group converging on one point packs round it without driving into each other");
        }

        [Test]
        public void TanksDrivingHeadOnPassWithoutOverlapping()
        {
            var world = OpenField();
            var a = world.SpawnVehicle("heavy_tank", 0, new Vector2(0f, -20f), 0f);
            var b = world.SpawnVehicle("heavy_tank", 0, new Vector2(0.5f, 20f), MathF.PI);
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 0, new[] { a.Id }, new Vector2(0f, 30f)));
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 0, new[] { b.Id }, new Vector2(0.5f, -30f)));
            var worst = 0f;
            for (var t = 0f; t < 20f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                worst = MathF.Max(worst, Penetration(a, b));
            }
            Assert.Less(worst, 0.6f, "head-on tanks steer round each other instead of driving through");
            Assert.Greater(a.Position.Y, 25f, "the first tank got past");
            Assert.Less(b.Position.Y, -25f, "and so did the second");
        }

        [Test]
        public void HullsStayApartThroughAWholeBattle()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 77);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            var ai0 = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5);
            var ai1 = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 6);
            int samples = 0, deep = 0;
            var worst = 0f;
            for (var t = 0f; t < 6 * 60 && mode.Result == null; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                ai0.Tick(world, TestWorlds.Step);
                ai1.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if ((int)(t / TestWorlds.Step) % 20 != 0) continue;
                var list = world.VehicleList;
                for (var i = 0; i < list.Count; i++)
                for (var j = i + 1; j < list.Count; j++)
                {
                    var a = list[i];
                    var b = list[j];
                    if (!a.IsAlive || !b.IsAlive || a.Flying || b.Flying) continue;
                    if (Vector2.Distance(a.Position, b.Position) > a.Def.HullBound + b.Def.HullBound) continue;
                    samples++;
                    var p = Penetration(a, b);
                    worst = MathF.Max(worst, p);
                    if (p > 0.8f) deep++;
                }
            }
            Debug.Log($"Hull contacts sampled {samples}, deep overlaps {deep}, worst {worst:0.00} m");
            Assert.Less(deep, Math.Max(3, samples / 50), "hulls rarely sink more than 0.8 m into each other");
        }
    }
}
