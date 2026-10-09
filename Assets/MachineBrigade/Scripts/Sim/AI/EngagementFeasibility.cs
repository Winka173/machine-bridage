#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.AI
{
    /// <summary>What a target is to a weapon: ground vehicles and structures, ships at sea, aircraft.</summary>
    public enum TargetLayer
    {
        Ground,
        Naval,
        Air,
    }

    /// <summary>
    /// AI MASTER section 8: a unit's reach against one layer: the longest reach and the least range of its weapons that do
    /// damage there (0 / 0: none can).
    /// </summary>
    public readonly struct WeaponEnvelope
    {
        public WeaponEnvelope(float minRange, float maxRange)
        {
            MinRange = minRange;
            MaxRange = maxRange;
        }

        public float MinRange { get; }
        public float MaxRange { get; }
        public bool Armed => MaxRange > 0f;

        /// <summary>The unit's envelope against <paramref name="layer"/> (a ship-only gun reaches ships only).</summary>
        public static WeaponEnvelope Of(VehicleDef def, TargetLayer layer)
        {
            if (def.NavalOnly && layer != TargetLayer.Naval) return default;
            var air = layer == TargetLayer.Air;
            float max = 0f, min = float.MaxValue;
            foreach (var m in def.Mounts)
            {
                var w = m.Weapon;
                if (w.Damage <= 0f || !w.CanTarget(air)) continue;
                max = MathF.Max(max, w.Range);
                min = MathF.Min(min, w.MinRange);
            }
            return max > 0f ? new WeaponEnvelope(min == float.MaxValue ? 0f : min, max) : default;
        }

        public override string ToString() => Armed ? $"{MinRange:0}-{MaxRange:0} m" : "unarmed";
    }

    /// <summary>
    /// AI MASTER sections 6-8: one place a unit might matter: an enemy (where it was seen; a ship also by the stretch of
    /// lane it patrols, <see cref="Samples"/>) or an objective (a point to take or hold, a mission goal).
    /// </summary>
    public readonly struct FeasibilityTarget
    {
        public FeasibilityTarget(string key, Vector2 centre, float radius, TargetLayer layer, float value, bool objective,
            IReadOnlyList<Vector2>? samples = null, bool capture = false)
        {
            Key = key;
            Centre = centre;
            Radius = radius;
            Layer = layer;
            Value = value;
            Objective = objective;
            Samples = samples;
            Capture = capture;
        }

        public string Key { get; }
        public Vector2 Centre { get; }
        public float Radius { get; }
        public TargetLayer Layer { get; }

        /// <summary>Its weight in coverage and target shares (CP for an enemy; a point's worth).</summary>
        public float Value { get; }

        /// <summary>An objective: reaching it is influence even with nothing to shoot there.</summary>
        public bool Objective { get; }

        /// <summary>A capture point (vehicles that capture are what takes it).</summary>
        public bool Capture { get; }

        /// <summary>Where the target will be (a ship's lane), or null for <see cref="Centre"/> only.</summary>
        public IReadOnlyList<Vector2>? Samples { get; }
    }

    /// <summary>The side, where its deliveries land, and the targets and objectives it knows (observed intel only).</summary>
    public sealed class FeasibilityContext
    {
        public FeasibilityContext(int team, Vector2 deployAt)
        {
            Team = team;
            DeployAt = deployAt;
        }

        public int Team { get; }
        public Vector2 DeployAt { get; set; }
        public List<FeasibilityTarget> Targets { get; } = new();
    }

    /// <summary>AI MASTER sections 6 and 100: what a unit can do on this map from where it deploys.</summary>
    public readonly struct InfluenceResult
    {
        public InfluenceResult(bool canDeploy, bool canReachObjective, bool canReachEnemy, bool canFireFromReachableRegion,
            float coverage, float travelSeconds, float usefulTargetShare, string reason, bool noTargets = false,
            float objectiveCoverage = 0f)
        {
            CanDeploy = canDeploy;
            CanReachObjective = canReachObjective;
            CanReachEnemy = canReachEnemy;
            CanFireFromReachableRegion = canFireFromReachableRegion;
            Coverage = coverage;
            TravelSeconds = travelSeconds;
            UsefulTargetShare = usefulTargetShare;
            Reason = reason;
            NoTargets = noTargets;
            ObjectiveCoverage = objectiveCoverage;
        }

        public bool CanDeploy { get; }
        public bool CanReachObjective { get; }
        public bool CanReachEnemy { get; }
        public bool CanFireFromReachableRegion { get; }

        /// <summary>0-1: the value-weighted share of targets and objectives it can reach or fire on (a ship's lane by stretch).</summary>
        public float Coverage { get; }

        /// <summary>Seconds of driving to the nearest place it matters from (+inf: none).</summary>
        public float TravelSeconds { get; }

        /// <summary>0-1: the value-weighted share of known enemies it can both hurt and engage (reach or fire on).</summary>
        public float UsefulTargetShare { get; }

        /// <summary>0-1: the share of objectives it can reach or fire on.</summary>
        public float ObjectiveCoverage { get; }

        /// <summary>Nothing known to weigh it against (no enemy seen, no objective): never a reason to reject (unknown is not useless).</summary>
        public bool NoTargets { get; }

        /// <summary>reachable-fire, reachable-objective, reachable-enemy, no-map-influence, deployment-unreachable, no-targets-known.</summary>
        public string Reason { get; }

        /// <summary>Section 100: it can deploy and influence the battle somewhere.</summary>
        public bool Useful => CanDeploy && (NoTargets || CanReachObjective || CanReachEnemy || CanFireFromReachableRegion || UsefulTargetShare > 0f);

        public override string ToString() =>
            $"{Reason} deploy={CanDeploy} obj={CanReachObjective} enemy={CanReachEnemy} fire={CanFireFromReachableRegion} cov={Coverage:0.00} travel={TravelSeconds:0}s share={UsefulTargetShare:0.00}";
    }

    /// <summary>
    /// AI MASTER sections 6-8, 67 and 100 (lane P0-B): reachability ("can it get there") is not firing reach ("can it shoot
    /// there from ground it can get to"). A unit's reachable cells are its domain's cells connected to where it deploys; the
    /// firing band round a target is the ring between its weapons' least range and longest reach (plus the target's radius,
    /// as the combat system measures); a unit can fire on the target when the two meet. Firing checks are cached by
    /// (domain, source cell, weapon envelope, target cell, radius) for the topology's life. Deterministic, reads only.
    /// </summary>
    public sealed class EngagementFeasibility
    {
        private readonly SimWorld _world;
        private readonly Dictionary<(int domain, int source, int min, int max, int target, int radius), int> _fire = new();

        public EngagementFeasibility(SimWorld world, MapTopology map)
        {
            _world = world;
            Map = map;
        }

        public MapTopology Map { get; }

        /// <summary>Cached firing-band checks so far (tests, the performance report).</summary>
        public int CachedFiringChecks => _fire.Count;

        /// <summary>Whether a vehicle of <paramref name="def"/> can hurt targets of <paramref name="layer"/> at all.</summary>
        public static bool CanHit(VehicleDef def, TargetLayer layer) => WeaponEnvelope.Of(def, layer).Armed;

        /// <summary>The layer a vehicle is to the other side's weapons.</summary>
        public static TargetLayer LayerOf(SimWorld world, Vehicle v) =>
            v.Flying ? TargetLayer.Air
            : v.Def.Naval != null || (world.Map.Sea is { } sea && sea.IsSea(v.Position)) ? TargetLayer.Naval
            : TargetLayer.Ground;

        /// <summary>
        /// Section 6: what <paramref name="def"/> can do on this map for the side of <paramref name="ctx"/>, delivered at
        /// <see cref="FeasibilityContext.DeployAt"/>.
        /// </summary>
        public InfluenceResult Evaluate(VehicleDef def, FeasibilityContext ctx) => Evaluate(def, ctx.DeployAt, ctx.Targets);

        public InfluenceResult Evaluate(VehicleDef def, Vector2 deployAt, IReadOnlyList<FeasibilityTarget> targets)
        {
            var domain = MapTopology.DomainOf(def);
            var speed = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.EvaluateSpeedFloor, def.Speed);
            var detour = SimTunables.Ai.Feasibility.TravelDetour;
            if (targets.Count == 0)
                return new InfluenceResult(CanDeploy(domain, deployAt), false, false, false, 0f, 0f, 0f,
                    CanDeploy(domain, deployAt) ? "no-targets-known" : "deployment-unreachable", noTargets: true);

            int source;
            int[]? dist = null;
            DomainGraph? graph = null;
            if (domain is MobilityDomain.Air or MobilityDomain.Static) source = Map.CellIndex(deployAt);
            else
            {
                graph = Map.For(domain)!;
                source = graph.NearestPassableCell(deployAt, SimTunables.Ai.Topology.NearestRings);
                if (source < 0)
                    return new InfluenceResult(false, false, false, false, 0f, float.PositiveInfinity, 0f, "deployment-unreachable");
                dist = graph.DistancesFrom(source);
            }

            bool reachObjective = false, reachEnemy = false, fire = false;
            float coverSum = 0f, valueSum = 0f, usefulValue = 0f, enemyValue = 0f, objectiveCover = 0f;
            var objectives = 0;
            var bestSteps = float.PositiveInfinity;
            var from = Map.CellCentre(Math.Max(0, source));
            foreach (var t in targets)
            {
                var env = WeaponEnvelope.Of(def, t.Layer);
                var value = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.EvaluateValueFloor, t.Value);
                float reach = 0f, cover = 0f;
                // Getting there: aircraft fly anywhere; fixed defences stay; the rest by their domain's cells.
                float steps;
                if (domain == MobilityDomain.Air) steps = Vector2.Distance(from, t.Centre) / Map.Cell;
                else if (domain == MobilityDomain.Static) steps = Vector2.Distance(deployAt, t.Centre) <= t.Radius ? 0f : float.PositiveInfinity;
                else steps = StepsInto(dist!, t.Centre, t.Radius + def.Radius);
                var reached = !float.IsPositiveInfinity(steps);
                // Map spec D1 (lane W1-A, maps.topology.sizeClassFeasibility, off by default): the unit's size class must fit the route.
                if (reached && domain == MobilityDomain.Ground && SimTunables.Maps.Topology.SizeClassFeasibility &&
                    !_world.GameplayTopology.SizeClassReaches(def, deployAt, t.Centre, t.Radius + def.Radius))
                    reached = false;
                if (reached && (t.Objective || env.Armed))
                {
                    reach = 1f;
                    bestSteps = MathF.Min(bestSteps, steps);
                }
                // Firing on it from ground it can get to, by the stretch of its lane for a ship.
                if (env.Armed)
                {
                    var samples = t.Samples;
                    var count = samples != null && samples.Count > 0 ? samples.Count : 1;
                    var hits = 0;
                    for (var k = 0; k < count; k++)
                    {
                        var at = samples != null && samples.Count > 0 ? samples[k] : t.Centre;
                        float s;
                        if (domain == MobilityDomain.Air) s = MathF.Max(0f, Vector2.Distance(from, at) - env.MaxRange) / Map.Cell;
                        else if (domain == MobilityDomain.Static)
                        {
                            var d = Vector2.Distance(deployAt, at);
                            s = d - t.Radius <= env.MaxRange && d >= env.MinRange ? 0f : float.PositiveInfinity;
                        }
                        else s = FiringSteps(domain, source, dist!, at, t.Radius, env);
                        if (float.IsPositiveInfinity(s)) continue;
                        hits++;
                        bestSteps = MathF.Min(bestSteps, s);
                    }
                    cover = hits / (float)count;
                    // Section 7: "fire from a reachable region" is firing on an enemy (a ship from the shore); shelling a point's
                    // ground is objective coverage, not that (Test C: a tank serves a land point yet cannot touch the ship).
                    if (hits > 0 && !t.Objective) fire = true;
                }
                var engaged = MathF.Max(reach, cover);
                coverSum += engaged * value;
                valueSum += value;
                if (t.Objective)
                {
                    objectives++;
                    objectiveCover += engaged;
                    if (reach > 0f) reachObjective = true;
                }
                else
                {
                    enemyValue += value;
                    if (reach > 0f && env.Armed) reachEnemy = true;
                    if (env.Armed && engaged > 0f) usefulValue += value;
                }
            }
            var travel = float.IsPositiveInfinity(bestSteps) ? float.PositiveInfinity : bestSteps * Map.Cell * detour / speed;
            var reason = fire ? "reachable-fire" : reachObjective ? "reachable-objective" : reachEnemy ? "reachable-enemy" : "no-map-influence";
            return new InfluenceResult(true, reachObjective, reachEnemy, fire,
                valueSum > 0f ? coverSum / valueSum : 0f, travel, enemyValue > 0f ? usefulValue / enemyValue : 0f, reason,
                objectiveCoverage: objectives > 0 ? objectiveCover / objectives : 0f);
        }

        /// <summary>Whether a unit of the domain can be put down at (or within a few cells of) a point.</summary>
        public bool CanDeploy(MobilityDomain domain, Vector2 at) =>
            domain is MobilityDomain.Air or MobilityDomain.Static ||
            Map.For(domain)!.NearestPassableCell(at, SimTunables.Ai.Topology.NearestRings) >= 0;

        /// <summary>Whether a unit of <paramref name="def"/> standing at <paramref name="from"/> can drive (sail, fly) to within <paramref name="radius"/> of <paramref name="to"/>.</summary>
        public bool CanReach(VehicleDef def, Vector2 from, Vector2 to, float? radius = null) =>
            !float.IsPositiveInfinity(TravelSeconds(def, from, to, (radius ?? global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.CanReachRadius)));

        /// <summary>Seconds of travel from one point to within <paramref name="radius"/> of another (+inf: cannot get there).</summary>
        public float TravelSeconds(VehicleDef def, Vector2 from, Vector2 to, float? radius = null)
        {
            var domain = MapTopology.DomainOf(def);
            var speed = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.TravelSecondsSpeedFloor, def.Speed);
            if (domain == MobilityDomain.Air) return Vector2.Distance(from, to) / speed;
            if (domain == MobilityDomain.Static) return Vector2.Distance(from, to) <= (radius ?? global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.TravelSecondsRadius) ? 0f : float.PositiveInfinity;
            var graph = Map.For(domain)!;
            var source = graph.NearestPassableCell(from, SimTunables.Ai.Topology.NearestRings);
            if (source < 0) return float.PositiveInfinity;
            var steps = StepsInto(graph.DistancesFrom(source), to, (radius ?? global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.TravelSecondsRadius));
            return float.IsPositiveInfinity(steps) ? steps : steps * Map.Cell * SimTunables.Ai.Feasibility.TravelDetour / speed;
        }

        /// <summary>
        /// Section 8: whether a unit of <paramref name="def"/> that starts at <paramref name="from"/> can reach a cell from
        /// which a weapon fires on a target of <paramref name="radius"/> at <paramref name="target"/> (the API the targeting
        /// lane calls: unreachable targets are dropped, never chased).
        /// </summary>
        public bool HasReachableFiringPosition(VehicleDef def, Vector2 from, Vector2 target, float radius, TargetLayer layer)
        {
            var env = WeaponEnvelope.Of(def, layer);
            if (!env.Armed) return false;
            var domain = MapTopology.DomainOf(def);
            if (domain == MobilityDomain.Air) return true;
            if (domain == MobilityDomain.Static)
            {
                var d = Vector2.Distance(from, target);
                return d - radius <= env.MaxRange && d >= env.MinRange;
            }
            var graph = Map.For(domain)!;
            var source = graph.NearestPassableCell(from, SimTunables.Ai.Topology.NearestRings);
            return source >= 0 && !float.IsPositiveInfinity(FiringSteps(domain, source, graph.DistancesFrom(source), target, radius, env));
        }

        /// <summary>
        /// Sections 7-8 for the targeting lane (P0 wiring, <see cref="TargetAccessCache.Resolver"/>): whether some cell of
        /// <paramref name="component"/> of <paramref name="domain"/>'s graph lies in the firing band round a target at
        /// <paramref name="target"/> (of <paramref name="radius"/>): distance - radius &lt;= <paramref name="maxRange"/> and
        /// distance &gt;= <paramref name="minRange"/>, as the combat system measures. A component test (no travel distances):
        /// every cell of a component is reachable from every other, so it answers for any unit standing in it. Air and fixed
        /// domains have no graph: true (their reach is judged where they are).
        /// </summary>
        public bool CanFireFromComponent(MobilityDomain domain, int component, Vector2 target, float radius, float minRange, float maxRange)
        {
            if (Map.For(domain) is not { } graph || component <= 0) return true;
            var outer = maxRange + radius;
            var outerSq = outer * outer;
            var minSq = minRange * minRange;
            var (x0, y0) = Map.CellXY(target - new Vector2(outer));
            var (x1, y1) = Map.CellXY(target + new Vector2(outer));
            for (var y = Math.Max(0, y0); y <= Math.Min(Map.Rows - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(Map.Columns - 1, x1); x++)
            {
                var i = y * Map.Columns + x;
                if (graph.ComponentOfCell(i) != component) continue;
                var d2 = Vector2.DistanceSquared(Map.CellCentre(i), target);
                if (d2 <= outerSq && d2 >= minSq) return true;
            }
            return false;
        }

        /// <summary>
        /// Section 67: whether a boss's workshop or escort wave should put a <paramref name="def"/> down at
        /// <paramref name="at"/> for <paramref name="team"/>: it must be able to stand there and reach the other side's camp,
        /// a capture point, or fire on a known enemy. Aircraft and ships pass (their own systems place them).
        /// </summary>
        public bool SpawnUseful(VehicleDef def, int team, Vector2 at, out string reason)
        {
            var domain = MapTopology.DomainOf(def);
            if (domain is MobilityDomain.Air or MobilityDomain.Static or MobilityDomain.Naval)
            {
                reason = "own-placement";
                return true;
            }
            var ctx = new FeasibilityContext(team, at);
            foreach (var p in _world.Map.Points) ctx.Targets.Add(new FeasibilityTarget("point_" + p.Id, p.Position, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.SpawnUsefulRadiusFloor, p.Radius), TargetLayer.Ground, 1f, true, capture: true));
            foreach (var start in _world.Map.Teams)
                if (start.Team != team) ctx.Targets.Add(new FeasibilityTarget("rally_" + start.Team, start.Rally, 8f, TargetLayer.Ground, 1f, true));
            var result = Evaluate(def, ctx);
            reason = result.Reason;
            return result.Useful;
        }

        /// <summary>Steps from the source (in <paramref name="dist"/>) to the nearest reached cell within <paramref name="radius"/> of a point.</summary>
        private float StepsInto(int[] dist, Vector2 centre, float radius)
        {
            var r = MathF.Max(radius, Map.Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.StepsIntoCellScale);
            var (x0, y0) = Map.CellXY(centre - new Vector2(r));
            var (x1, y1) = Map.CellXY(centre + new Vector2(r));
            var best = int.MaxValue;
            var r2 = (r + Map.Cell * 0.5f) * (r + Map.Cell * 0.5f);
            for (var y = Math.Max(0, y0); y <= Math.Min(Map.Rows - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(Map.Columns - 1, x1); x++)
            {
                var i = y * Map.Columns + x;
                if (dist[i] < 0 || dist[i] >= best) continue;
                if (Vector2.DistanceSquared(Map.CellCentre(i), centre) > r2) continue;
                best = dist[i];
            }
            return best == int.MaxValue ? float.PositiveInfinity : best;
        }

        /// <summary>
        /// Section 8: the steps to the nearest reachable cell of the firing band round a target (+inf: the band and the
        /// reachable ground do not meet). Cached per (domain, source, envelope, target cell, radius).
        /// </summary>
        private float FiringSteps(MobilityDomain domain, int source, int[] dist, Vector2 target, float radius, WeaponEnvelope env)
        {
            // Targets are snapped to a coarse cell (SnapCells x SnapCells grid cells) so a moving enemy keeps hitting the
            // cache; the band is widened by the snap's half diagonal, so the snap never turns a reachable target into a reject.
            var (tx, ty) = Map.CellXY(target);
            tx = Math.Clamp(tx, 0, Map.Columns - 1) / SnapCells * SnapCells;
            ty = Math.Clamp(ty, 0, Map.Rows - 1) / SnapCells * SnapCells;
            var snapped = Map.Origin + new Vector2((tx + SnapCells * 0.5f) * Map.Cell, (ty + SnapCells * 0.5f) * Map.Cell);
            var slack = SnapCells * Map.Cell * 0.7072f;
            var key = ((int)domain, source, (int)MathF.Round(env.MinRange), (int)MathF.Round(env.MaxRange), ty * Map.Columns + tx, (int)MathF.Round(radius));
            if (_fire.TryGetValue(key, out var cached)) return cached < 0 ? float.PositiveInfinity : cached;
            if (_fire.Count >= CacheLimit) _fire.Clear();
            var reach = env.MaxRange + radius + slack;
            var (x0, y0) = Map.CellXY(snapped - new Vector2(reach));
            var (x1, y1) = Map.CellXY(snapped + new Vector2(reach));
            var best = int.MaxValue;
            var max2 = reach * reach;
            var least = MathF.Max(0f, env.MinRange - slack);
            var min2 = least * least;
            for (var y = Math.Max(0, y0); y <= Math.Min(Map.Rows - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(Map.Columns - 1, x1); x++)
            {
                var i = y * Map.Columns + x;
                var d = dist[i];
                if (d < 0 || d >= best) continue;
                var d2 = Vector2.DistanceSquared(Map.CellCentre(i), snapped);
                if (d2 > max2 || d2 < min2) continue;
                best = d;
            }
            var result = best == int.MaxValue ? -1 : best;
            _fire[key] = result;
            return result < 0 ? float.PositiveInfinity : result;
        }

        /// <summary>Grid cells per side of the coarse cell targets snap to (2 m cells: 8 m).</summary>
        private const int SnapCells = 4;

        /// <summary>Cached firing checks kept before the cache is cleared.</summary>
        private static int CacheLimit => global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.CacheLimit;

        /// <summary>
        /// The targets a side knows (fog-fair): the enemies in <paramref name="known"/> (what it has seen), a ship also by the
        /// stretch of its lane; the capture points it does not hold; the mission's goal; the other side's camp when it has a
        /// base. Used by the buying AI; other layers can build their own.
        /// </summary>
        /// <summary>Enemies within this many metres of the first of a group are judged as one target.</summary>
        public static float ClusterReach => global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.ClusterReach;

        public static FeasibilityContext Observed(SimWorld world, int team, Vector2 deployAt, IReadOnlyList<Vehicle> known,
            Modes.IObjectiveMode? mode, Vector2? goal, Vector2? defendPoint)
        {
            var ctx = new FeasibilityContext(team, deployAt);
            var samples = Math.Max(1, (int)SimTunables.Ai.Feasibility.LaneSamples);
            // Enemies seen close together (same layer, within ClusterReach) are one target: fewer firing checks.
            var used = new bool[known.Count];
            for (var i = 0; i < known.Count; i++)
            {
                var e = known[i];
                if (used[i] || !e.IsAlive || e.Team == team) continue;
                var layer = LayerOf(world, e);
                var value = 0f;
                var sum = Vector2.Zero;
                var members = 0;
                var lead = e;
                for (var j = i; j < known.Count; j++)
                {
                    var o = known[j];
                    if (used[j] || !o.IsAlive || o.Team == team || LayerOf(world, o) != layer) continue;
                    if (Vector2.DistanceSquared(o.Position, e.Position) > ClusterReach * ClusterReach) continue;
                    used[j] = true;
                    var w = o.Def.Boss ? global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.ObservedBossTrue : MathF.Max(1f, o.Def.CpCost);
                    value += w;
                    sum += o.Position * w;
                    members++;
                    if (o.Radius > lead.Radius) lead = o;
                }
                var centre = members > 1 ? sum / value : e.Position;
                var radius = members > 1 ? lead.Radius + ClusterReach * global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.ObservedClusterReachScale : e.Radius;
                IReadOnlyList<Vector2>? lane = null;
                // A ship patrols: the stretch of the lane nearest where it was seen (map spec K / L, the gameplay topology's rule).
                if (layer == TargetLayer.Naval && world.Map.Sea is { } sea) lane = GameplayTopology.LaneStretch(sea, centre, lead.Radius, samples);
                ctx.Targets.Add(new FeasibilityTarget("enemy_" + e.Id.Value, centre, radius, layer, value, false, lane));
            }
            if (mode != null)
                foreach (var p in mode.Points)
                {
                    // Points to take, and our own while they are contested (held ground the enemy is on).
                    if (p.Locked || (p.Owner == team && !p.Contested)) continue;
                    ctx.Targets.Add(new FeasibilityTarget("point_" + p.Def.Id, p.Def.Position, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.ObservedRadiusFloor, p.Def.Radius), TargetLayer.Ground, global::MachineBrigade.Sim.Content.SimTunables.Ai.EngagementFeasibility.ObservedValue, true, capture: true));
                }
            if (goal is { } g)
            {
                var layer = world.Map.Sea is { } sea && sea.IsSea(g) ? TargetLayer.Naval : TargetLayer.Ground;
                ctx.Targets.Add(new FeasibilityTarget("goal", g, 6f, layer, 6f, true));
            }
            if (defendPoint is { } d) ctx.Targets.Add(new FeasibilityTarget("defend", d, 10f, TargetLayer.Ground, 4f, true));
            // The other side's camp (map knowledge) when it has a base to attack.
            foreach (var start in world.Map.Teams)
                if (start.Team != team && world.Bases.Of(start.Team) != null)
                {
                    var layer = world.Map.Sea is { } sea && sea.IsSea(start.Rally) ? TargetLayer.Naval : TargetLayer.Ground;
                    ctx.Targets.Add(new FeasibilityTarget("camp_" + start.Team, start.Rally, 10f, layer, 4f, true));
                }
            return ctx;
        }
    }
}
