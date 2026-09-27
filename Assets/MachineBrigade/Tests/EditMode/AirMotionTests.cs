using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Aircraft attacking ground targets must fly smoothly: no shuffling back and forth and no
    /// wagging of the nose from one simulation step to the next, which the view shows as jitter
    /// (aircraft are drawn without the ground vehicles' smoothing filter).
    /// </summary>
    public class AirMotionTests
    {
        private sealed class Meter
        {
            private readonly Dictionary<EntityId, (Vector2 p, Vector2 d, float h, float dh)> _last = new();
            public readonly Dictionary<string, (int moves, int shakes, int swings, int steps)> ByDef = new();

            public void Sample(IReadOnlyList<Vehicle> list)
            {
                foreach (var v in list)
                {
                    if (!v.IsAlive || !v.Flying) continue;
                    if (!_last.TryGetValue(v.Id, out var last))
                    {
                        _last[v.Id] = (v.Position, Vector2.Zero, v.Heading, 0f);
                        continue;
                    }
                    ByDef.TryGetValue(v.Def.Id, out var c);
                    c.steps++;
                    var d = v.Position - last.p;
                    var dh = SimMath.WrapAngle(v.Heading - last.h);
                    if (d.Length() > 0.01f && last.d.Length() > 0.01f)
                    {
                        c.moves++;
                        if (Vector2.Dot(d, last.d) < -0.3f * d.Length() * last.d.Length()) c.shakes++;
                    }
                    if (MathF.Abs(dh) > 0.004f && MathF.Abs(last.dh) > 0.004f && MathF.Sign(dh) != MathF.Sign(last.dh)) c.swings++;
                    ByDef[v.Def.Id] = c;
                    _last[v.Id] = (v.Position, d, v.Heading, dh);
                }
            }

            public string Report() => string.Join("; ", ByDef.OrderBy(p => p.Key)
                .Select(p => $"{p.Key}: steps {p.Value.steps}, moves {p.Value.moves}, shakes {p.Value.shakes}, swings {p.Value.swings}"));
        }

        private static SimWorld OpenField() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        [Test]
        public void AircraftAttackingGroundTargetsFlySmoothly()
        {
            var world = OpenField();
            var catalog = world.Catalog;
            var flyers = catalog.Vehicles.Values.Where(d => d.Flying && !d.Boss && d.CpCost > 0).Select(d => d.Id).OrderBy(id => id).ToList();
            var ids = new List<EntityId>();
            for (var i = 0; i < flyers.Count; i++)
                ids.Add(world.SpawnVehicle(flyers[i], 0, new Vector2(-50f + i % 5 * 6f, -50f + i / 5 * 6f), 0.8f).Id);
            // A spread of tough ground targets that do not shoot back (they keep the attack going).
            for (var i = 0; i < 6; i++)
            {
                var target = world.SpawnVehicle("heavy_tank", 1, new Vector2(10f + i % 3 * 12f, 10f + i / 3 * 12f), 3.9f);
                target.HpScale = 1000f;
                target.Hp = target.MaxHp;
            }
            world.Submit(new Command(CommandType.AttackMove, 0, ids.ToArray(), new Vector2(20f, 20f)));
            var meter = new Meter();
            for (var t = 0f; t < 60f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                meter.Sample(world.VehicleList);
            }
            Debug.Log("AIR MOTION " + meter.Report());
            foreach (var pair in meter.ByDef)
            {
                var c = pair.Value;
                // A hovering helicopter's last-metre corrections may reverse now and then (up to one
                // move in twenty, which shifts with the random stream): that is not jitter.
                Assert.LessOrEqual(c.shakes, Math.Max(12, c.moves / 20), $"{pair.Key} shuffles back and forth");
                Assert.LessOrEqual(c.swings, Math.Max(6, c.steps / 40), $"{pair.Key} wags its nose");
            }
        }
    }
}
