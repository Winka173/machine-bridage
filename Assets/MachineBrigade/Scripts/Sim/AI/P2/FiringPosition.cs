#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>The Part D1 terms of one position (each 0-1), for the debug and the tests.</summary>
    public struct PositionTerms
    {
        public float Uptime, Cover, HullDown, Observation, Escape, Support, Threat, Splash, Congestion, LaneBlock, CounterBattery, Total;

        public override string ToString() =>
            $"total {Total:0.00}: uptime {Uptime:0.0} cover {Cover:0.0} hullDown {HullDown:0.0} obs {Observation:0.0} escape {Escape:0.0} support {Support:0.0} " +
            $"- threat {Threat:0.0} splash {Splash:0.0} crowd {Congestion:0.0} lane {LaneBlock:0.0} cb {CounterBattery:0.0}";
    }

    /// <summary>
    /// AI MASTER P2 Part D: terrain / cover / firing-position intelligence.
    /// <c>PositionScore = WeaponUptime + CoverValue + HullDownValue + Elevation/Observation + EscapeRoute + FriendlySupportCoverage
    /// - EnemyThreat - SplashDensityRisk - Congestion - FriendlyFireLaneBlocking - CounterBatteryRisk</c>, weights by role.
    /// The sim's ground is flat: hull-down (D2) is low cover (a prop that stops vehicles but not fire: sandbags, tank traps,
    /// low walls, pipelines) in the cone towards the threat 1.5-7 m in front, the line to the target still clear; observation
    /// (D3) is clear lines of sight round the spot; dead ground (D4) for indirect fire is cover from the known direct-fire
    /// enemies. D5: a chosen spot is reserved (<see cref="PositionReservations"/>) so four units do not pick the same point.
    /// </summary>
    public static class FiringPositionScorer
    {
        /// <summary>Role factors on the weights: hull-down for TD / MBT / heavy, observation for recon and long direct fire, dead ground for indirect.</summary>
        private static (float hullDown, float observation, float cover, float cb) RoleFactors(DoctrineRole role) => role switch
        {
            DoctrineRole.TankDestroyer => (1f, 1f, 1f, 0f),
            DoctrineRole.MainBattle => (1f, 0.4f, 1f, 0f),
            DoctrineRole.Recon => (0.2f, 1.5f, 0.6f, 0f),
            DoctrineRole.FireSupport => (0f, 0f, 1.5f, 1f),
            DoctrineRole.AntiAir => (0.2f, 0.6f, 0.8f, 0.5f),
            _ => (0.3f, 0.4f, 1f, 0f),
        };

        /// <summary>Part D1's score of <paramref name="p"/> for <paramref name="v"/> to fire at <paramref name="target"/> with the threat at <paramref name="threat"/>.</summary>
        public static float Score(SimWorld world, Vehicle v, Vector2 p, Vector2 target, Vector2 threat, DoctrineRole role, out PositionTerms t)
        {
            t = default;
            var w = Tun.Position.Weights;
            float W(int i) => i < w.Length ? w[i] : 0f;
            var weapon = v.Def.Weapon;
            var indirect = weapon.MinRange > 0f;
            var intel = world.Intel.Peek(v.Team);
            var (fHull, fObs, fCover, fCb) = RoleFactors(role);
            // Uptime: the target in reach (and in the line of fire for direct weapons).
            var d = Vector2.Distance(p, target);
            var inReach = d <= weapon.Range && d >= weapon.MinRange;
            t.Uptime = inReach && (indirect || Clear(world, p, target)) ? 1f : inReach ? global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreInReachTrue : 0f;
            // Cover: share of the known direct-fire enemies within twice our reach whose line to the spot is blocked.
            var seen = 0;
            var blocked = 0;
            foreach (var o in world.VehicleList)
            {
                if (!o.IsAlive || o.Team == v.Team || o.Team < 0 || o.Flying || o.Def.Weapon.Damage <= 0f || o.Def.Weapon.MinRange > 0f || !o.IsVisibleTo(v.Team)) continue;
                if (Vector2.DistanceSquared(o.Position, p) > weapon.Range * weapon.Range * global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreRangeScale) continue;
                seen++;
                if (!Clear(world, o.Position, p)) blocked++;
                if (seen >= 8) break;
            }
            t.Cover = seen > 0 ? blocked / (float)seen : 0f;
            t.HullDown = HullDown(world, p, threat, target) ? 1f : 0f;
            // Observation: clear 30 m lines round the spot.
            var clear = 0;
            for (var k = 0; k < 8; k++)
                if (Clear(world, p, p + SimMath.Forward(k * MathF.PI / 4f) * 30f)) clear++;
            t.Observation = clear / 8f;
            var exits = 0;
            for (var k = 0; k < 8; k++)
                if (world.Grid.IsWalkable(p + SimMath.Forward(k * MathF.PI / 4f) * 10f)) exits++;
            t.Escape = exits / 8f;
            var friends = 0;
            var crowd = 0;
            var lane = false;
            foreach (var f in world.VehicleList)
            {
                if (f == v || !f.IsAlive || f.Team != v.Team || f.Flying || f.Def.Static) continue;
                var dd = Vector2.DistanceSquared(f.Position, p);
                if (dd < 25f * 25f) friends++;
                if (dd < 6f * 6f) crowd++;
                // Standing in a friend's line of fire (Part D "FriendlyFireLaneBlocking").
                if (!lane && world.TryGetVehicle(f.Target, out var ft) && InLine(f.Position, ft.Position, p, v.Radius + 1f)) lane = true;
            }
            t.Support = MathF.Min(1f, friends / global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreFriendsDivisor);
            t.Congestion = MathF.Min(1f, crowd / global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreCrowdDivisor);
            t.LaneBlock = lane ? 1f : 0f;
            if (intel != null)
            {
                t.Threat = MathF.Min(1f, intel.ThreatAt(ThreatKind.AntiTank, p) / global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreThreatAtDivisor);
                t.Splash = MathF.Min(1f, intel.ThreatAt(ThreatKind.Splash, p) / global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreThreatAtDivisor);
                t.CounterBattery = MathF.Min(1f, intel.ThreatAt(ThreatKind.Artillery, p) / global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreThreatAtDivisor);
            }
            t.Total = W(0) * t.Uptime + W(1) * fCover * t.Cover + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI) * fHull * t.HullDown + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI2) * fObs * t.Observation + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI3) * t.Escape +
                      W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI4) * t.Support - W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI5) * t.Threat - W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI6) * t.Splash - W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI7) * t.Congestion - W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI8) * t.LaneBlock - W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.ScoreI9) * fCb * t.CounterBattery;
            return t.Total;
        }

        /// <summary>D2: low cover in the cone towards the threat, close in front of the spot, with the target still in a clear line.</summary>
        public static bool HullDown(SimWorld world, Vector2 p, Vector2 threat, Vector2 target)
        {
            var to = threat - p;
            if (to.LengthSquared() < 1f) return false;
            var dir = Vector2.Normalize(to);
            var cos = MathF.Cos(SimMath.DegToRad(Tun.Position.HullDownConeDeg));
            var min = Tun.Position.HullDownMin;
            var max = Tun.Position.HullDownMax;
            var found = false;
            foreach (var prop in world.Props)
            {
                if (!prop.IsAlive || !prop.Def.BlocksMovement || prop.Def.BlocksFire) continue;
                var rel = prop.Position - p;
                var dist = rel.Length();
                if (dist < min || dist > max + prop.Radius) continue;
                if (Vector2.Dot(rel / dist, dir) < cos) continue;
                found = true;
                break;
            }
            return found && Clear(world, p, target);
        }

        /// <summary>
        /// The best position within ai.position.searchRadius of <paramref name="slot"/> (the slot itself counts), not reserved by
        /// another unit; the pick is reserved for <paramref name="v"/>. Logs POSITION_HULL_DOWN when it is a hull-down spot.
        /// </summary>
        public static Vector2 Best(SimWorld world, Vehicle v, Vector2 slot, Vector2 target, Vector2 threat, DoctrineRole role)
        {
            var reservations = world.Positions;
            var best = slot;
            var bestScore = Score(world, v, slot, target, threat, role, out var bestTerms);
            var r = Tun.Position.SearchRadius;
            for (var ring = 1; ring <= 2; ring++)
                for (var k = 0; k < 8; k++)
                {
                    var p = world.Map.Clamp(slot + SimMath.Forward(k * MathF.PI / 4f + ring * 0.39f) * (r * ring * 0.5f), 4f);
                    if (!world.Grid.IsWalkable(p) || world.Lanes.NoParkAt(p) || reservations.ReservedByOther(p, v.Id)) continue;
                    var s = Score(world, v, p, target, threat, role, out var terms);
                    if (s <= bestScore + 0.05f) continue;
                    best = p;
                    bestScore = s;
                    bestTerms = terms;
                }
            reservations.Reserve(best, v.Id);
            if (bestTerms.HullDown > 0f && !reservations.WasHullDown(v.Id))
            {
                reservations.MarkHullDown(v.Id, true);
                P2Reasons.Unit(world, v, DecisionKind.Action, P2Reasons.PositionHullDown, $"({best.X:0},{best.Y:0})");
            }
            else if (bestTerms.HullDown <= 0f) reservations.MarkHullDown(v.Id, false);
            return best;
        }

        /// <summary>D4: how many known direct-fire enemies (at most 4) have <paramref name="p"/> in reach and in a clear line.</summary>
        public static int DirectExposure(SimWorld world, int team, Vector2 p)
        {
            var n = 0;
            foreach (var o in world.VehicleList)
            {
                if (!o.IsAlive || o.Team == team || o.Team < 0 || o.Flying || o.Def.Weapon.Damage <= 0f || o.Def.Weapon.MinRange > 0f || !o.IsVisibleTo(team)) continue;
                var reach = o.Def.Weapon.Range + global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.DirectExposureRangeAdd;
                if (Vector2.DistanceSquared(o.Position, p) > reach * reach || !Clear(world, o.Position, p)) continue;
                if (++n >= 4) break;
            }
            return n;
        }

        private static bool Clear(SimWorld world, Vector2 from, Vector2 to) => !world.Cover.TryFirstHit(from, to, 1.5f, 1.5f, null, out _);

        private static bool InLine(Vector2 from, Vector2 to, Vector2 p, float width)
        {
            var d = to - from;
            var length = d.Length();
            if (length < global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.InLineLengthMax) return false;
            var dir = d / length;
            var rel = p - from;
            var along = Vector2.Dot(rel, dir);
            if (along <= global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.InLineAlongMax || along >= length - global::MachineBrigade.Sim.Content.SimTunables.Ai.FiringPositionScorer.InLineLengthSub) return false;
            return MathF.Abs(rel.X * dir.Y - rel.Y * dir.X) < width;
        }
    }

    /// <summary>Part D5: reserved firing positions (cover spots, hull-down points), one owner each, for a few seconds.</summary>
    public sealed class PositionReservations
    {
        private readonly SimWorld _world;
        private readonly List<(Vector2 at, EntityId owner, double until)> _held = new();
        private readonly Dictionary<EntityId, bool> _hullDown = new();

        internal PositionReservations(SimWorld world) => _world = world;

        public int Count => _held.Count;

        public bool ReservedByOther(Vector2 p, EntityId self)
        {
            var now = _world.Time;
            var r = Tun.Position.ReserveRadius;
            foreach (var h in _held)
                if (h.owner.Value != self.Value && h.until > now && Vector2.DistanceSquared(h.at, p) < r * r &&
                    _world.TryGetVehicle(h.owner, out var o) && o.IsAlive) return true;
            return false;
        }

        public void Reserve(Vector2 p, EntityId owner)
        {
            var now = _world.Time;
            _held.RemoveAll(h => h.owner.Value == owner.Value || h.until <= now);
            _held.Add((p, owner, now + Tun.Position.ReserveSeconds));
        }

        internal bool WasHullDown(EntityId id) => _hullDown.TryGetValue(id, out var b) && b;

        internal void MarkHullDown(EntityId id, bool on) => _hullDown[id] = on;
    }
}
