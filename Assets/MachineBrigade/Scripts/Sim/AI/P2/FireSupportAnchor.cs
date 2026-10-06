#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>What the tactical AI knows when it places its fire support (its own picture: fog-fair).</summary>
    public readonly struct FireSupportContext
    {
        public FireSupportContext(Vector2 front, Vector2 objective, Vector2 forward, bool contact, Vector2? enemyCentre, Func<Vector2, bool>? exposed)
        {
            Front = front;
            Objective = objective;
            Forward = forward;
            Contact = contact;
            EnemyCentre = enemyCentre;
            Exposed = exposed;
        }

        /// <summary>The friendly front (the main body's leading edge).</summary>
        public Vector2 Front { get; }

        /// <summary>The tactical objective (the point to take or hold, the enemy cluster, the camp).</summary>
        public Vector2 Objective { get; }

        /// <summary>Front to objective, normalised.</summary>
        public Vector2 Forward { get; }

        public bool Contact { get; }

        /// <summary>The known (seen) enemy ground centre, if any.</summary>
        public Vector2? EnemyCentre { get; }

        /// <summary>Inside a known fixed defence's reach (the tactical AI's rule); null: nothing known.</summary>
        public Func<Vector2, bool>? Exposed { get; }
    }

    /// <summary>One fire class's anchor (Part J), its reference and why it was set.</summary>
    public sealed class FireSupportAnchorState
    {
        public FireClass Class { get; internal set; }
        public Vector2 Point { get; internal set; }
        public Vector2 Reference { get; internal set; }
        public double Since { get; internal set; } = double.NegativeInfinity;
        public string Reason { get; internal set; } = "";
        public FireSupportPolicy Policy { get; internal set; }
        public int Sets { get; internal set; }
        internal int Generation = -1, GridVersion = -1, Pocket;
        internal float Range, MinRange;
        internal Vector2 Approach;
        internal readonly List<Vector2> Pockets = new();
        internal double LastFired = double.NegativeInfinity;
        internal float Hp = -1f;
    }

    /// <summary>
    /// AI MASTER P2 Part J: FireSupportAnchor. Artillery, mortars, MLRS and ballistic launchers do not follow the squad
    /// centroid: each fire class of a side has an anchor, set from the mode doctrine's policy (Part I) at the class's Part I1
    /// band of its usable reach behind the front / objective / convoy / boss context, scored by
    /// <c>ObjectiveCoverage + EnemyApproachCoverage + FriendlyFrontCoverage + AAProtection + EscapeRoute + CounterBatterySafety
    /// - Threat - Congestion - MinRangeViolation - Spawn/TrafficBlocking</c> (weights ai.fireSupport.weights), and kept until a
    /// reposition trigger of the doctrine fires (front moved / range band lost / objective uncovered, utilization, counter-
    /// battery, terrain change, phase change, rotation, wave direction, pocket compromised). The pieces of a class stand on
    /// slots ai.fireSupport.slotSpacing apart round it, off the roads and doorways. Deterministic: id order, sim clock.
    /// </summary>
    public sealed class FireSupportDirector
    {
        private readonly int _team;
        private readonly Dictionary<FireClass, FireSupportAnchorState> _anchors = new();
        private readonly List<Vehicle> _class = new();

        public FireSupportDirector(int team) => _team = team;

        public FireSupportAnchorState? AnchorOf(FireClass c) => _anchors.TryGetValue(c, out var a) ? a : null;

        /// <summary>AI MASTER P5 Part K: forget the anchors so each class picks its anchor afresh (the health monitor's recovery).</summary>
        internal void Refresh() => _anchors.Clear();

        /// <summary>Part I1's fire class of a launcher (mortar, artillery, MLRS, very-long-range).</summary>
        public static FireClass ClassOf(SimWorld world, Vehicle v)
        {
            var role = world.Catalog.AiData.RoleOf(v.Def.Id)?.Id;
            var range = v.Def.Weapon.Range;
            if (role == "Strike" || range >= Tun.ModeDoctrine.LongRangeMin) return FireClass.LongRange;
            if (role == "MLRS") return FireClass.Mlrs;
            if (range <= Tun.ModeDoctrine.MortarMaxRange || v.Def.Id.IndexOf("mortar", StringComparison.Ordinal) >= 0) return FireClass.Mortar;
            return FireClass.Artillery;
        }

        /// <summary>
        /// Where <paramref name="piece"/> should stand: its class's anchor (set or repositioned now if a trigger fired) and its
        /// slot round it. <paramref name="pieces"/>: every fire-support piece of the side (any order).
        /// </summary>
        public Vector2? Stand(SimWorld world, Vehicle piece, IReadOnlyList<Vehicle> pieces, in FireSupportContext ctx)
        {
            var cls = ClassOf(world, piece);
            _class.Clear();
            foreach (var p in pieces)
                if (p.IsAlive && ClassOf(world, p) == cls) _class.Add(p);
            if (_class.Count == 0) _class.Add(piece);
            _class.Sort((a, b) => a.Id.Value.CompareTo(b.Id.Value));
            if (!_anchors.TryGetValue(cls, out var state)) _anchors[cls] = state = new FireSupportAnchorState { Class = cls };
            var doctrine = world.Doctrine.For(_team);
            var range = float.MaxValue;
            var minRange = 0f;
            foreach (var p in _class)
            {
                range = MathF.Min(range, p.Def.Weapon.Range);
                minRange = MathF.Max(minRange, p.Def.Weapon.MinRange);
            }
            state.Range = range;
            state.MinRange = minRange;
            var (reference, back, approach) = Reference(world, doctrine, ctx, range);
            var reason = Trigger(world, doctrine, state, reference, approach, ctx);
            if (reason != null) Set(world, doctrine, state, reference, back, approach, ctx, reason);
            return Slot(world, state, piece);
        }

        // ------------------------------------------------------------------------------------------------ reference

        /// <summary>The policy's reference point (the "target / front context"), the way back to own side, the enemy's approach.</summary>
        private (Vector2 reference, Vector2 back, Vector2 approach) Reference(SimWorld world, ModeDoctrine d, in FireSupportContext ctx, float range)
        {
            var forward = ctx.Forward.LengthSquared() > 0.01f ? Vector2.Normalize(ctx.Forward) : Vector2.UnitY;
            var approach = ctx.EnemyCentre is { } e && Vector2.DistanceSquared(e, ctx.Objective) > 1f ? Vector2.Normalize(e - ctx.Objective) : forward;
            Vector2 reference;
            Vector2 back;
            switch (d.FireSupport)
            {
                case FireSupportPolicy.ObjectiveCover:
                {
                    reference = ctx.Objective;
                    back = world.TryGetRally(_team, out var home) && Vector2.DistanceSquared(home, reference) > 1f ? Vector2.Normalize(home - reference) : -forward;
                    if (ctx.EnemyCentre.HasValue) back = Normalize(back - approach, back);
                    break;
                }
                case FireSupportPolicy.DefenceLine:
                case FireSupportPolicy.Quiet:
                case FireSupportPolicy.PreparedPockets:
                    // The expected contact line a little out from the defended point; launchers stand behind it.
                    reference = ctx.Objective + approach * 15f;
                    back = -approach;
                    break;
                case FireSupportPolicy.ConvoyLeapfrog:
                {
                    if (Convoy(world, out var centre, out var heading))
                    {
                        reference = centre + heading * 20f;
                        back = -heading;
                    }
                    else goto default;
                    break;
                }
                case FireSupportPolicy.BossPredict:
                {
                    var boss = NearestBoss(world, ctx.Front);
                    if (boss == null) goto default;
                    reference = boss.Position + SimMath.Forward(boss.Heading) * boss.Speed * Tun.FireSupport.PredictSeconds;
                    back = Normalize(ctx.Front - reference, -forward);
                    break;
                }
                case FireSupportPolicy.SiegeLayers:
                {
                    var tower = NearestDefence(world, ctx.Front, range * 2f);
                    if (tower == null) goto default;
                    reference = tower.Position;
                    back = Normalize(ctx.Front - reference, -forward);
                    break;
                }
                case FireSupportPolicy.InterceptPredict:
                {
                    var intel = world.Intel.Peek(_team);
                    EnemyGroup? best = null;
                    if (intel != null)
                        foreach (var g in intel.EnemyGroups)
                            if (!g.Air && g.Confidence >= Tun.FireSupport.InterceptConfidence && (best == null || g.Strength > best.Value.Strength)) best = g;
                    if (best is not { } quarry) goto default;
                    reference = quarry.Centre + quarry.Velocity * Tun.FireSupport.PredictSeconds;
                    back = Normalize(ctx.Front - reference, -forward);
                    break;
                }
                default:
                    // FrontLogical: the enemy in front of the line when there is contact, else a little ahead of the front.
                    reference = ctx.Contact && ctx.EnemyCentre is { } enemy && Vector2.Distance(enemy, ctx.Front) < range * 1.5f
                        ? enemy
                        : ctx.Front + forward * MathF.Min(Vector2.Distance(ctx.Front, ctx.Objective), 25f);
                    back = -forward;
                    break;
            }
            return (reference, back, approach);
        }

        private static Vector2 Normalize(Vector2 v, Vector2 fallback) => v.LengthSquared() > 0.01f ? Vector2.Normalize(v) : fallback;

        private bool Convoy(SimWorld world, out Vector2 centre, out Vector2 heading)
        {
            centre = default;
            heading = Vector2.UnitY;
            if (world.ConvoySafeZone == null) return false;
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var p in world.ConvoySafeZone())
            {
                sum += p;
                n++;
            }
            if (n == 0) return false;
            centre = sum / n;
            // The convoy's way: its vehicles' mean heading (the escort's trucks; any of the side's escorted vehicles).
            var h = Vector2.Zero;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _team && v.IsMoving && Vector2.Distance(v.Position, centre) < 12f) h += SimMath.Forward(v.Heading);
            heading = Normalize(h, heading);
            return true;
        }

        private Vehicle? NearestBoss(SimWorld world, Vector2 from)
        {
            Vehicle? best = null;
            var bestD = float.MaxValue;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || !v.Def.Boss || v.Team == _team || !v.IsVisibleTo(_team)) continue;
                var d = Vector2.DistanceSquared(v.Position, from);
                if (d < bestD)
                {
                    bestD = d;
                    best = v;
                }
            }
            return best;
        }

        private Vehicle? NearestDefence(SimWorld world, Vector2 from, float within)
        {
            Vehicle? best = null;
            var bestD = within * within;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || !v.Def.Static || v.Team == _team || v.Team < 0 || v.Def.Weapon.Damage <= 0f || !v.IsVisibleTo(_team)) continue;
                var d = Vector2.DistanceSquared(v.Position, from);
                if (d < bestD)
                {
                    bestD = d;
                    best = v;
                }
            }
            return best;
        }

        // ------------------------------------------------------------------------------------------------ triggers

        /// <summary>Null: keep the anchor; else the reposition trigger that fired (or "new").</summary>
        private string? Trigger(SimWorld world, ModeDoctrine d, FireSupportAnchorState s, Vector2 reference, Vector2 approach, in FireSupportContext ctx)
        {
            var now = world.Time;
            var gen = world.Doctrine.Generation;
            if (s.Sets == 0) return "new";
            var tr = d.Triggers;
            // Emergencies first (no minimum hold): the phase, the ground, an anchor that cannot fire at all.
            if (s.Generation != gen)
            {
                if ((tr & RepositionTrigger.PhaseChange) != 0 || s.Policy != d.FireSupport) return "phase";
                s.Generation = gen;
            }
            if (s.GridVersion != world.Grid.Version && (tr & RepositionTrigger.TerrainChange) != 0 && !world.Grid.IsWalkable(s.Point)) return "terrain";
            var dist = Vector2.Distance(s.Point, reference);
            var (bandMin, bandMax) = ModeCombatDoctrine.Band(s.Class);
            if (dist > s.Range || dist < s.MinRange + 2f)
                return (tr & (RepositionTrigger.RangeBandLost | RepositionTrigger.FrontMoved | RepositionTrigger.ObjectiveUncovered)) != 0 ? "rangeBandLost" : null;
            var intel = world.Intel.Peek(_team);
            if ((tr & RepositionTrigger.CounterBattery) != 0 && intel != null && intel.ThreatAt(ThreatKind.Artillery, s.Point) > 0f && CounterBatteryHit(world, s))
                return "counterbattery";
            if (now - s.Since < Tun.FireSupport.MinHoldSeconds) return null;
            if ((tr & (RepositionTrigger.FrontMoved | RepositionTrigger.ObjectiveUncovered | RepositionTrigger.RangeBandLost)) != 0 &&
                dist > s.Range * (bandMax + Tun.FireSupport.BandSlack))
                return (tr & RepositionTrigger.ObjectiveUncovered) != 0 ? "objectiveUncovered" : "frontMoved";
            if ((tr & RepositionTrigger.PocketCompromised) != 0 && intel != null && intel.ThreatAt(ThreatKind.AntiTank, s.Point) > 0f) return "pocketCompromised";
            if ((tr & RepositionTrigger.WaveDirection) != 0 && s.Approach.LengthSquared() > 0.5f && Vector2.Dot(s.Approach, approach) < 0.7f) return "waveDirection";
            if ((tr & RepositionTrigger.Rotation) != 0 && d.Rotate && now - s.Since >= Tun.ModeDoctrine.RotateSeconds) return "rotation";
            if ((tr & RepositionTrigger.Utilization) != 0 && ctx.Contact)
            {
                var last = double.NegativeInfinity;
                foreach (var p in _class) last = Math.Max(last, p.LastFiredAt);
                s.LastFired = last;
                if (now - last >= Tun.FireSupport.UtilizationSeconds && now - s.Since >= Tun.FireSupport.UtilizationSeconds) return "utilization";
            }
            return null;
        }

        /// <summary>A piece of the class lost health standing at the anchor since the last look (counter-battery fire found it).</summary>
        private bool CounterBatteryHit(SimWorld world, FireSupportAnchorState s)
        {
            var hp = 0f;
            foreach (var p in _class) hp += p.Hp;
            var hit = s.Hp >= 0f && hp < s.Hp - 1f;
            s.Hp = hp;
            return hit || world.Doctrine.For(_team).ShootAndScoot && ShotsSince(s) >= 3;
        }

        private int ShotsSince(FireSupportAnchorState s)
        {
            var n = 0;
            foreach (var p in _class)
                if (p.LastFiredAt > s.Since) n += 1;
            // Every piece of the class fired since the anchor was set (three salvos of a battery): scoot.
            return n >= _class.Count && _class.Count > 0 ? 3 : 0;
        }

        // ------------------------------------------------------------------------------------------------ setting

        private void Set(SimWorld world, ModeDoctrine d, FireSupportAnchorState s, Vector2 reference, Vector2 back, Vector2 approach,
            in FireSupportContext ctx, string reason)
        {
            var (bandMin, bandMax) = ModeCombatDoctrine.Band(s.Class);
            var bias = world.Doctrine.Stage switch
            {
                ShowdownStage.Early => 1f,
                ShowdownStage.Mid => 0.5f,
                ShowdownStage.Final => 0f,
                _ => d.BandBias,
            };
            var wanted = bandMin + (bandMax - bandMin) * Math.Clamp(bias, 0f, 1f);
            var side = new Vector2(back.Y, -back.X);
            var avoid = reason is "utilization" or "counterbattery" or "pocketCompromised" or "rotation" ? s.Point : (Vector2?)null;
            var candidates = new List<(Vector2 p, float score)>();
            var fractions = new[] { bandMin, wanted, bandMax };
            var lateral = Math.Max(0, Tun.FireSupport.LateralSamples);
            foreach (var f in fractions)
                for (var k = -lateral; k <= lateral; k++)
                {
                    var p = world.Map.Clamp(reference + back * (s.Range * f) + side * (k * Tun.FireSupport.LateralStep), 6f);
                    if (!Valid(world, p, ctx)) continue;
                    var score = Score(world, d, s, p, reference, approach, ctx) - MathF.Abs(f - wanted) * 2f;
                    if (avoid is { } old && Vector2.Distance(old, p) < 15f) score -= 2f;
                    candidates.Add((p, score));
                }
            Vector2 point;
            if (candidates.Count == 0)
            {
                // Nothing valid on the band: the old standoff (behind the front), off the lanes.
                point = world.Lanes.OffLane(world.Map.Clamp(ctx.Front + back * 18f, 6f), 10f);
            }
            else
            {
                candidates.Sort((a, b) => b.score.CompareTo(a.score));
                point = candidates[0].p;
                if (d.Rotate && d.FireSupport == FireSupportPolicy.PreparedPockets)
                {
                    // I6 / I16: 2-3 prepared pockets, distinct; a rotation steps to the next one.
                    s.Pockets.Clear();
                    foreach (var c in candidates)
                    {
                        var far = true;
                        foreach (var q in s.Pockets)
                            if (Vector2.Distance(q, c.p) < 20f) far = false;
                        if (far) s.Pockets.Add(c.p);
                        if (s.Pockets.Count >= Math.Max(1, Tun.ModeDoctrine.Pockets)) break;
                    }
                    s.Pocket = reason == "rotation" ? (s.Pocket + 1) % s.Pockets.Count : 0;
                    point = s.Pockets[s.Pocket];
                }
            }
            s.Point = point;
            s.Reference = reference;
            s.Approach = approach;
            s.Since = world.Time;
            s.Reason = reason;
            s.Policy = d.FireSupport;
            s.Generation = world.Doctrine.Generation;
            s.GridVersion = world.Grid.Version;
            s.Sets++;
            s.Hp = -1f;
            // Map spec BW 7 (lane W1-A): count every anchor, and any in a forbidden transit zone (the telemetry only reads).
            if (SimTunables.Maps.Topology.Telemetry)
                world.MapTelemetry.AnchorSet(point, !world.GameplayTopology.ParkingAllowed(point) || world.GameplayTopology.TransitConflict(point) >= 1f);
            var first = _class.Count > 0 ? _class[0] : null;
            if (first != null)
                P2Reasons.Unit(world, first, DecisionKind.Action, reason == "counterbattery" ? P2Reasons.ArtilleryCounterbatteryScoot : P2Reasons.ArtilleryAnchorSet,
                    $"{s.Class} {d.FireSupport} {reason} ({point.X:0},{point.Y:0}) ref ({reference.X:0},{reference.Y:0})");
        }

        private static bool Valid(SimWorld world, Vector2 p, in FireSupportContext ctx)
        {
            // Map spec F (lane W1-A): the gameplay topology's parking rule (open ground, no doorway or its mouths).
            if (!world.GameplayTopology.ParkingAllowed(p)) return false;
            if (ctx.Exposed != null && ctx.Exposed(p)) return false;
            return true;
        }

        /// <summary>Part J AnchorScore.</summary>
        private float Score(SimWorld world, ModeDoctrine d, FireSupportAnchorState s, Vector2 p, Vector2 reference, Vector2 approach, in FireSupportContext ctx)
        {
            var w = Tun.FireSupport.Weights;
            float W(int i) => i < w.Length ? w[i] : 0f;
            var intel = world.Intel.Peek(_team);
            float Covers(Vector2 at)
            {
                var dd = Vector2.Distance(p, at);
                if (dd < s.MinRange + 3f) return 0f;
                return dd <= s.Range * 0.95f ? 1f : MathF.Max(0f, 1f - (dd - s.Range * 0.95f) / MathF.Max(1f, s.Range * 0.25f));
            }
            var objective = Covers(ctx.Objective);
            var enemyApproach = Covers(ctx.EnemyCentre ?? reference + approach * 20f);
            var front = Covers(ctx.Front + ctx.Forward * 15f);
            var aa = 0f;
            var congestion = 0;
            var hq = false;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team) continue;
                var dd = Vector2.DistanceSquared(v.Position, p);
                if (!v.Flying && v.Def.Class == UnitClass.AntiAir && dd < 30f * 30f && !world.Components.Of(v).RadarLost) aa = 1f;
                if (!v.Flying && !v.Def.Static && !v.HasPath && dd < 7f * 7f && !_class.Contains(v)) congestion++;
                if (v.Def.Static && dd < Tun.FireSupport.HqSeparation * Tun.FireSupport.HqSeparation) hq = true;
            }
            var topology = world.GameplayTopology;
            var escape = topology.EscapeRoutes(p, 12f);
            var cb = intel == null ? 1f : 1f - MathF.Min(1f, intel.ThreatAt(ThreatKind.Artillery, p) / 5f);
            var threat = intel == null ? 0f : MathF.Min(1f, (intel.ThreatAt(ThreatKind.AntiTank, p) + intel.ThreatAt(ThreatKind.Splash, p)) / 5f);
            var minRange = Vector2.Distance(p, reference) < s.MinRange + 3f ? 1f : 0f;
            var traffic = topology.TransitConflict(p);
            if (world.TryGetRally(_team, out var spawn) && Vector2.Distance(spawn, p) < 12f) traffic = 1f;
            if (hq && s.Class is FireClass.Mlrs or FireClass.LongRange) traffic += 0.5f;
            return W(0) * objective + W(1) * enemyApproach + W(2) * front + W(3) * aa + W(4) * escape / 8f + W(5) * cb
                   - W(6) * threat - W(7) * MathF.Min(1f, congestion / 3f) - W(8) * minRange - W(9) * traffic
                   + TerrainTopology.ConcealmentTerm(world, p);
        }

        private Vector2 Slot(SimWorld world, FireSupportAnchorState s, Vehicle piece)
        {
            var index = _class.IndexOf(piece);
            if (index < 0) index = 0;
            var back = s.Reference - s.Point;
            back = back.LengthSquared() > 0.01f ? -Vector2.Normalize(back) : Vector2.UnitY;
            var side = new Vector2(back.Y, -back.X);
            var spacing = Tun.FireSupport.SlotSpacing;
            var row = index / 5;
            var col = index % 5;
            var lateral = ((col + 1) / 2) * (col % 2 == 0 ? 1f : -1f) * spacing;
            var p = world.Map.Clamp(s.Point + side * lateral + back * (row * spacing), 6f);
            p = world.Lanes.OffLane(p, 10f);
            return world.Grid.IsWalkable(p) ? p : s.Point;
        }
    }
}
