#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Prompt 28 D.6 and D.7, the unit logic of the vehicles outside squads (once a second): artillery fires and moves
    /// (shoot and scoot for every gun, not only those with a scoot of their own) and keeps off the spots counter-battery
    /// fire found; aircraft come in from the side with the least known anti-air and do not circle in dense anti-air.
    /// </summary>
    public sealed partial class AiCommander
    {
        private const int ScootShots = 3;
        private const int MarkedKept = 12;

        private readonly Dictionary<EntityId, (double lastFired, int shots, float hp)> _guns = new();
        private readonly List<Vector2> _marked = new();
        private readonly Dictionary<EntityId, (Vector2 target, double until)> _approach = new();
        private readonly Dictionary<EntityId, double> _inAntiAir = new();

        /// <summary>Spots where own artillery was hit while enemy guns were known (D.6: avoided when moving).</summary>
        public IReadOnlyList<Vector2> MarkedSpots => _marked;

        private void UnitsOutsideSquads(SimWorld world, TeamIntel intel)
        {
            var enemyGuns = false;
            foreach (var c in intel.Contacts)
                if (c.Artillery || c.Unit.Contains("counter_battery")) enemyGuns = true;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Team || v.Def.Static || v.Scripted || v.IsEscort || v.Garrison || v.UnderPlayerControl(world.Time)) continue;
                // AI MASTER P4 spec 174-178: SEAD, risk routing, CAP, handoff, bomber packages first; the old approach logic otherwise.
                if (v.Flying)
                {
                    if (!AirP4(world, intel, v)) Aircraft(world, intel, v);
                }
                // AI MASTER P3 spec 143-145: fire missions for every gun, shoot-and-scoot for those without a scoot of their own.
                else if (v.Def.Weapon.MinRange > 0f && CoordinationP3 != null) ArtilleryP3(world, intel, v, enemyGuns);
                else if (v.Def.Weapon.MinRange > 0f && v.Def.Scoot == null) Artillery(world, v, enemyGuns);
            }
        }

        private void Artillery(SimWorld world, Vehicle v, bool enemyGuns)
        {
            if (!_guns.TryGetValue(v.Id, out var g)) g = (v.LastFiredAt, 0, v.Hp);
            if (v.LastFiredAt > g.lastFired) g = (v.LastFiredAt, g.shots + 1, g.hp);
            // Hit while standing and enemy guns are about: this spot is marked.
            if (v.Hp < g.hp - 1f && !v.IsMoving && enemyGuns)
            {
                _marked.Add(v.Position);
                if (_marked.Count > MarkedKept) _marked.RemoveAt(0);
            }
            g.hp = v.Hp;
            var marked = Near(v.Position, 15f);
            if ((g.shots >= ScootShots && enemyGuns) || (marked && g.shots > 0))
            {
                if (!v.IsMoving && !v.HasPath && Scoot(world, v)) g.shots = 0;
            }
            _guns[v.Id] = g;
        }

        private bool Scoot(SimWorld world, Vehicle v)
        {
            var aim = world.TryGetVehicle(v.Target, out var target) ? target.Position : v.Position + SimMath.Forward(v.Heading) * 50f;
            var back = aim - v.Position;
            back = back.LengthSquared() > 0.01f ? -Vector2.Normalize(back) : -SimMath.Forward(v.Heading);
            var side = new Vector2(back.Y, -back.X);
            // Across the line of fire, sides alternating by the gun's id and the time, then angled back; never a marked spot.
            var first = ((v.Id.Value + (int)world.Time / global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ScootTimeDivisor) & 1) == 0 ? 1f : -1f;
            Vector2[] tries = { side * first, -side * first, Vector2.Normalize(side * first + back), back };
            foreach (var dir in tries)
            {
                var spot = world.Map.Clamp(v.Position + dir * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ScootDirScale, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ScootMargin);
                if (!world.Grid.IsWalkable(spot) || Near(spot, 15f)) continue;
                var reach = Vector2.Distance(spot, aim);
                if (target != null && (reach > v.Def.Weapon.Range - global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ScootRangeSub || reach < v.Def.Weapon.MinRange + global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ScootMinRangeAdd)) continue;
                world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, spot));
                world.AiLog.Add(new DecisionEntry(world.Time, Team, AiLayer.Unit, v.Id.Value, DecisionKind.Action, "artillery scoot"));
                return true;
            }
            return false;
        }

        private bool Near(Vector2 p, float radius)
        {
            foreach (var m in _marked)
                if (Vector2.Distance(m, p) < radius) return true;
            return false;
        }

        private void Aircraft(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var now = world.Time;
            var here = intel.ThreatAt(ThreatKind.AntiAir, v.Position);
            // Not circling to death in dense anti-air: idle there 10 s without firing, it leaves to the clearest side.
            if (here > TeamIntel.StrengthOf(v) * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftStrengthOfScale && now - v.LastFiredAt > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftNowMin)
            {
                if (!_inAntiAir.TryGetValue(v.Id, out var since)) _inAntiAir[v.Id] = since = now;
                if (now - since >= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftNowMin2)
                {
                    var best = v.Position;
                    var bestThreat = here;
                    for (var k = 0; k < 8; k++)
                    {
                        var p = world.Map.Clamp(v.Position + SimMath.Forward(k * MathF.PI / 4f) * 60f, 10f);
                        var t = intel.ThreatAt(ThreatKind.AntiAir, p);
                        if (t < bestThreat)
                        {
                            best = p;
                            bestThreat = t;
                        }
                    }
                    _inAntiAir.Remove(v.Id);
                    if (best != v.Position)
                    {
                        world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, best));
                        world.AiLog.Add(new DecisionEntry(now, Team, AiLayer.Unit, v.Id.Value, DecisionKind.Emergency, "aircraft leaves dense anti-air"));
                    }
                    return;
                }
            }
            else _inAntiAir.Remove(v.Id);

            // An approach under way: on to the target once at the waypoint (or after its time).
            if (_approach.TryGetValue(v.Id, out var a))
            {
                if (now >= a.until || Vector2.Distance(v.Position, v.Order.Point) < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftDistanceMax || v.Order.Kind != OrderKind.Move)
                {
                    _approach.Remove(v.Id);
                    if (v.Order.Kind == OrderKind.Move) world.Submit(new Command(CommandType.AttackMove, Team, new[] { v.Id }, a.target));
                }
                return;
            }
            if (v.Order.Kind != OrderKind.AttackMove) return;
            var goal = v.Order.Point;
            if (intel.ThreatAt(ThreatKind.AntiAir, goal) <= 0f || Vector2.Distance(v.Position, goal) < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftDistanceMax2) return;
            // The least defended of three approaches 50 m out (straight, 60 degrees either side), by the anti-air on the way.
            var inbound = Vector2.Normalize(goal - v.Position);
            float Cost(Vector2 w) => intel.ThreatAt(ThreatKind.AntiAir, w) + intel.ThreatAt(ThreatKind.AntiAir, (w + v.Position) * 0.5f);
            var direct = Cost(goal - inbound * 50f);
            Vector2? pick = null;
            var pickCost = direct * 0.7f;
            foreach (var angle in new[] { global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftAngle1, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftAngle2 })
            {
                var c = MathF.Cos(angle);
                var s = MathF.Sin(angle);
                var rotated = new Vector2(inbound.X * c - inbound.Y * s, inbound.X * s + inbound.Y * c);
                var w = world.Map.Clamp(goal - rotated * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftRotatedScale, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftMargin);
                var cost = Cost(w);
                if (cost < pickCost)
                {
                    pick = w;
                    pickCost = cost;
                }
            }
            if (pick is not { } waypoint) return;
            _approach[v.Id] = (goal, now + global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AircraftNowAdd);
            world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, waypoint));
        }
    }
}
