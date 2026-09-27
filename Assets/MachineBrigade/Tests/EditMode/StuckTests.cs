using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Whole AI battles on every map: ground vehicles with an order must not sit still for long
    /// with nothing to shoot (stuck on a wall, in a corner of the map's outline, or chasing a
    /// point they cannot reach).
    /// </summary>
    public class StuckTests
    {
        private static IEnumerable<string> Maps() => MatchSettings.AllMaps.Select(m => m.Id);

        private const float Window = 15f;

        [Test, TestCaseSource(nameof(Maps))]
        public void GroundUnitsDoNotStallOnTheirWay(string map)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_conquest"), seed: 31);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            var ai0 = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5);
            var ai1 = new ConquestAi(mode, 1, 0, AiDifficulty.Hard, 6);
            var history = new Dictionary<EntityId, Queue<(float t, Vector2 p, float h, float s, int i)>>();
            var reported = new HashSet<EntityId>();
            // The last time each vehicle was not on its way somewhere (idle, holding, fighting): a
            // unit is only stalled if it has been ordered far away, with nothing to shoot, for the
            // whole window, however often the orders changed (a fresh order is not a stall).
            var free = new Dictionary<EntityId, float>();
            var stalls = new List<string>();
            var boundary = world.Map.Boundary;
            for (var t = 0f; t < 6 * 60 && mode.Result == null; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                ai0.Tick(world, TestWorlds.Step);
                ai1.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if ((int)(t / TestWorlds.Step) % 10 != 0) continue;
                foreach (var v in world.VehicleList)
                {
                    if (!v.IsAlive || v.Def.Flying || v.Def.Static || v.Scripted) continue;
                    if (!history.TryGetValue(v.Id, out var trail)) history[v.Id] = trail = new Queue<(float, Vector2, float, float, int)>();
                    trail.Enqueue((t, v.Position, v.Heading, v.Speed, v.PathIndex));
                    while (trail.Count > 0 && trail.Peek().t < t - Window) trail.Dequeue();
                    var order = v.Order;
                    var busy = order.Kind is OrderKind.Move or OrderKind.AttackMove or OrderKind.Retreat &&
                               Vector2.Distance(order.Point, v.Position) > 8f && !v.Target.IsValid;
                    if (!busy || !free.ContainsKey(v.Id)) free[v.Id] = t;
                    if (!busy || t - free[v.Id] < Window || trail.Peek().t > t - Window + 0.6f) continue;
                    var span = trail.Max(s => Vector2.Distance(s.p, v.Position));
                    if (span > 1.5f || !reported.Add(v.Id)) continue;
                    var edge = boundary.Count > 2 ? EdgeDistance(boundary, v.Position) : float.NaN;
                    var near = world.VehicleList.Where(o => o != v && o.IsAlive && !o.Flying && Vector2.Distance(o.Position, v.Position) < 9f)
                        .Select(o => $"{o.Def.Id}{(o.Team == v.Team ? "" : "(foe)")}@{Vector2.Distance(o.Position, v.Position):0.0}{(o.HasPath ? "p" : "")}{(o.Def.Static ? "S" : "")}");
                    var props = world.Props.Where(o => o.IsAlive && o.Def.BlocksMovement && Vector2.Distance(o.Position, v.Position) < 10f)
                        .Select(o => $"{o.Def.Id}@{Vector2.Distance(o.Position, v.Position):0}");
                    var next = v.HasPath ? v.Path[v.PathIndex] : v.Position;
                    var engaged = world.TryGetVehicle(v.Engaged, out var foe) && foe.IsAlive
                        ? $"{foe.Def.Id}{(foe.Flying ? "(air)" : "")}{(foe.Def.Static ? "(static)" : "")} d{Vector2.Distance(foe.Position, v.Position) - foe.Radius:0.0}/r{v.Def.Weapon.Range:0} " +
                          $"vis {foe.IsVisibleTo(v.Team)} lof {world.HasLineOfFire(v, foe, v.Def.Weapon)} cd {v.Cooldown:0.0}"
                        : "none";
                    stalls.Add($"{v.Def.Id}#{v.Id.Value} t{t:0} at ({v.Position.X:0},{v.Position.Y:0}) edge {edge:0.0} m, " +
                               $"order {order.Kind} to ({order.Point.X:0},{order.Point.Y:0}) {(world.Map.InsideBoundary(order.Point) ? "inside" : "OUTSIDE")}; " +
                               $"path {(v.HasPath ? $"{v.PathIndex}/{v.Path.Count} next ({next.X:0},{next.Y:0})" : "none")}, strikes {v.StuckStrikes}, " +
                               $"engaged {engaged}, speed {v.Speed:0.0}, walkable {world.Grid.IsWalkable(v.Position)}; near [{string.Join(" ", near)}]; props [{string.Join(" ", props)}]" +
                               "\n      trace " + string.Join(" ", trail.Where((_, k) => k % 5 == 0).Select(s =>
                                   $"({s.p.X:0.0},{s.p.Y:0.0} h{s.h * 57.3f:0} v{s.s:0.0} i{s.i})")) +
                               $"\n      turn {v.Def.TurnRate * 57.3f:0}/s speed {v.Def.Speed:0.0} hull {v.Def.Length:0.0}x{v.Def.Width:0.0} blockedAhead {!world.Grid.IsWalkable(v.Position + MachineBrigade.Sim.Core.SimMath.Forward(v.Heading) * 1f)}");
                }
            }
            Debug.Log($"STALLS {map}: {stalls.Count}\n  " + string.Join("\n  ", stalls));
            if (stalls.Count > 0) TraceAgain(map, stalls);
            Assert.LessOrEqual(stalls.Count, 2, $"{map}: ground units stalled on their way:\n  " + string.Join("\n  ", stalls));
        }

        /// <summary>
        /// Replays the same battle (the simulation is deterministic) and records, with the calling
        /// code, every change to the first stalled vehicles' path and order in the 20 s before
        /// they stalled.
        /// </summary>
        private static void TraceAgain(string map, List<string> stalls)
        {
            var targets = new Dictionary<int, float>();
            foreach (var line in stalls.Take(3))
            {
                var m = System.Text.RegularExpressions.Regex.Match(line, @"#(\d+) t(\d+)");
                targets[int.Parse(m.Groups[1].Value)] = float.Parse(m.Groups[2].Value);
            }
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_conquest"), seed: 31);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            var ai0 = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5);
            var ai1 = new ConquestAi(mode, 1, 0, AiDifficulty.Hard, 6);
            var log = new List<string>();
            var now = 0f;
            var last = new Dictionary<int, string>();
            Vehicle.PathTrace = (veh, reason) =>
            {
                if (!targets.TryGetValue(veh.Id.Value, out var at) || now < at - 20f || now > at + 1f) return;
                var frames = new System.Diagnostics.StackTrace(1, false).GetFrames() ?? Array.Empty<System.Diagnostics.StackFrame>();
                var stack = string.Join(" < ", frames.Take(5).Select(f => f.GetMethod()?.DeclaringType?.Name + "." + f.GetMethod()?.Name));
                var entry = reason.Split(' ')[0] + " | " + stack;
                if (last.TryGetValue(veh.Id.Value, out var previous) && previous == entry) return;
                last[veh.Id.Value] = entry;
                log.Add($"#{veh.Id.Value} t{now:0.00} ({veh.Position.X:0.0},{veh.Position.Y:0.0}) {reason} | {stack}");
            };
            try
            {
                var end = targets.Values.Max() + 1f;
                for (var t = 0f; t < end && mode.Result == null; t += TestWorlds.Step)
                {
                    now = t;
                    mode.Tick(world, TestWorlds.Step);
                    ai0.Tick(world, TestWorlds.Step);
                    ai1.Tick(world, TestWorlds.Step);
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                }
            }
            finally
            {
                Vehicle.PathTrace = null;
            }
            Debug.Log($"TRACE {map}:\n  " + string.Join("\n  ", log.Take(120)));
        }

        private static float EdgeDistance(IReadOnlyList<Vector2> poly, Vector2 p)
        {
            var best = float.MaxValue;
            for (var i = 0; i < poly.Count; i++)
            {
                var a = poly[i];
                var b = poly[(i + 1) % poly.Count];
                var ab = b - a;
                var k = Math.Clamp(Vector2.Dot(p - a, ab) / Math.Max(1e-6f, ab.LengthSquared()), 0f, 1f);
                best = Math.Min(best, Vector2.Distance(p, a + ab * k));
            }
            return best;
        }
    }
}
