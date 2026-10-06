#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using Tun = MachineBrigade.Sim.Content.SimTunables.Maps.Topology;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Map / visual / audio W2-A (spec O "enables Breacher AI; Siege target priority"): the breach metadata of
    /// <see cref="GameplayTopology.Breaches"/> as a ranking term for the breachers' pick (TacticalAi.DirectBreachers). Lower ranks
    /// first (the pick's score is metres): a segment whose fall opens the way to a target (or shortens it by a quarter) ranks
    /// <c>maps.topology.breachObjectiveBonus</c> nearer, each metre of path it saves (capped at 80) <c>breachSavingWeight</c>
    /// nearer, each defence covering it <c>breachTowerPenalty</c> farther. Off (<c>maps.topology.aiBreachPriority</c> false):
    /// the pick is exactly as before. Map knowledge only (the walls are drawn on the map): fog-fair, deterministic.
    /// </summary>
    public static class BreachTopology
    {
        public static bool Enabled => Tun.AiBreachPriority;

        /// <summary>The ranking change (m) for attacking <paramref name="structure"/> (0: not a wall segment with breach data).</summary>
        public static float Ranking(SimWorld world, Vehicle structure)
        {
            if (!world.HasWalls || world.Walls.SegmentOf(structure.Id) == null) return 0f;
            var info = At(world.GameplayTopology, structure.Position);
            if (info == null) return 0f;
            var r = 0f;
            if (info.ObjectiveAccessGained) r -= Tun.BreachObjectiveBonus;
            r -= MathF.Min(80f, info.PathCostReductionOnDestroy) * Tun.BreachSavingWeight;
            r += info.DefensiveTowerCoverage * Tun.BreachTowerPenalty;
            return r;
        }

        /// <summary>The breach record of the segment centred at <paramref name="p"/> (within 1.5 m; null: none).</summary>
        public static BreachInfo? At(GameplayTopology topology, Vector2 p)
        {
            BreachInfo? best = null;
            var bestD = 1.5f * 1.5f;
            foreach (var b in topology.Breaches)
            {
                var d = Vector2.DistanceSquared(b.Centre, p);
                if (d > bestD) continue;
                bestD = d;
                best = b;
            }
            return best;
        }
    }

    /// <summary>
    /// Map / visual / audio W2-A (spec I / H "AI attack-package staging"): the topology's staging area for an attack package's
    /// objective, offered to Commander.P3's StagingP3 as one more candidate (maps.topology.aiStagingCandidate, off by default).
    /// The candidate keeps StagingP3's own rules (outside the known reach, reachable, off chokes, passages and spawn exits) and
    /// competes on its threat score; the map-static area adds ground the five bearings round the target may miss.
    /// </summary>
    public static class StagingTopology
    {
        public static bool Enabled => Tun.AiStagingCandidate;

        /// <summary>The staging area centre for <paramref name="team"/> attacking the objective at <paramref name="target"/> (null: none).</summary>
        public static Vector2? For(SimWorld world, int team, Vector2 target)
        {
            var topology = world.GameplayTopology;
            var objective = topology.ObjectiveAt(target, 6f);
            if (objective == null) return null;
            foreach (var s in topology.StagingAreas)
                if (s.Team == team && s.Objective == objective.Id) return s.Centre;
            return null;
        }
    }

    /// <summary>
    /// Map / visual / audio W2-A (spec P "AI positioning"): the terrain semantics' concealment as a fire-support anchor term
    /// (FireSupportAnchor.Score + maps.topology.aiConcealmentWeight x concealment). Weight 0 (the default): no change.
    /// </summary>
    public static class TerrainTopology
    {
        public static float ConcealmentTerm(SimWorld world, Vector2 p)
        {
            var w = Tun.AiConcealmentWeight;
            if (w == 0f) return 0f;
            return w * GameplayTopology.SemanticsOf(world.Grid.TerrainAt(p)).Concealment;
        }
    }
}
