#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>A Sandbox battle run to its end without a screen (prompt 21 F.2-F.5).</summary>
    public sealed class SandboxRunResult
    {
        /// <summary>0 or 1; -1 a draw; -2 undecided (the time ran out with no limit to call it).</summary>
        public int Winner = -2;

        public double Seconds;
        public float[] HealthLeft = new float[2];
        public float[] Dealt = new float[2];
        public int[] Lost = new int[2];
        public int[] Alive = new int[2];
        public int StuckEpisodes;
        public ulong Hash;
        public SandboxStats Stats = new();
        public int Steps;
    }

    /// <summary>How the two sides face each other at the start of a quick duel (F.5).</summary>
    public enum DuelFacing
    {
        /// <summary>Front to front.</summary>
        Front,

        /// <summary>The first side sees the second's flank.</summary>
        Side,

        /// <summary>The first side comes up behind the second.</summary>
        Rear,
    }

    /// <summary>
    /// The Sandbox's measuring bench (prompt 21 F): a scenario run headless to its end (the automatic tests and the
    /// combat-value measure run saved scenarios this way), pass conditions checked on the result, a quick duel
    /// between two units or two groups with the win rate over many seeds, and one scenario run under two
    /// configurations side by side (A/B).
    /// </summary>
    public static class SandboxLab
    {
        public const float Step = 0.05f;

        /// <summary>
        /// Builds and runs the scenario for at most <paramref name="seconds"/> (its own limit first), with its
        /// journal of controls if given. The same scenario, seed and journal give the same result (the hash too).
        /// </summary>
        public static SandboxRunResult Run(Catalog catalog, MapDefinition map, SandboxScenario scenario, float seconds,
            Func<SandboxUnit, VehicleDef, VehicleBoost?>? boost = null, IEnumerable<(long tick, SandboxOp op)>? journal = null,
            Action<SimWorld, SandboxBattle>? each = null)
        {
            var world = new SimWorld(catalog, map, scenario.Seed);
            var battle = new SandboxBattle(scenario, boost);
            battle.Setup(world);
            if (journal != null) battle.Replay(journal);
            var steps = (int)MathF.Ceiling(seconds / Step);
            var result = new SandboxRunResult { Stats = battle.Stats };
            for (var i = 0; i < steps && battle.Result == null; i++)
            {
                battle.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                each?.Invoke(world, battle);
                result.Steps++;
            }
            battle.Stats.Step(world);
            result.Winner = battle.Result is { } r ? r.WinningTeam : -2;
            result.Seconds = battle.Result != null ? battle.EndedAt : world.Time;
            for (var team = 0; team < 2; team++)
            {
                result.HealthLeft[team] = SandboxBattle.HealthShare(world, team);
                (result.Dealt[team], result.Lost[team]) = battle.Stats.Side(team);
                result.Alive[team] = world.CountAlive(team);
            }
            result.StuckEpisodes = battle.Stuck?.CountOver(battle.Stuck.Threshold) ?? 0;
            result.Hash = world.StateHash();
            return result;
        }

        /// <summary>The scenario's pass conditions against a run (F.2); empty when every one holds. Each failure in plain words.</summary>
        public static List<string> Evaluate(IReadOnlyList<SandboxCheck> checks, SandboxRunResult r)
        {
            var failed = new List<string>();
            foreach (var c in checks)
                switch (c.Kind)
                {
                    case "win":
                        if (r.Winner != c.Team || r.Seconds > c.Seconds) failed.Add($"side {c.Team} should win within {c.Seconds:0} s (winner {r.Winner}, {r.Seconds:0.0} s)");
                        break;
                    case "noStuck":
                        if (r.StuckEpisodes > 0) failed.Add($"{r.StuckEpisodes} vehicle(s) stuck");
                        break;
                    case "survive":
                        if (r.Alive[Math.Clamp(c.Team, 0, 1)] == 0) failed.Add($"side {c.Team} should still have units");
                        break;
                    default:
                        failed.Add("unknown check '" + c.Kind + "'");
                        break;
                }
            return failed;
        }

        /// <summary>How long a scenario's checks need it to run: the longest "win within" (60 s when none says).</summary>
        public static float CheckSeconds(SandboxScenario s)
        {
            var longest = s.Limit > 0f ? s.Limit : 0f;
            foreach (var c in s.Checks)
                if (c.Kind == "win") longest = MathF.Max(longest, c.Seconds + 1f);
            return longest > 0f ? longest : 60f;
        }

        // ================================================================== quick duels (F.5)

        /// <summary>
        /// A duel on the flat test range: <paramref name="a"/> (side 0) and <paramref name="b"/> (side 1), each a
        /// list of unit kinds side by side, <paramref name="distance"/> metres apart, facing as <paramref name="facing"/>
        /// says, both fighting AI, called after <paramref name="limit"/> seconds by health left.
        /// </summary>
        public static SandboxScenario DuelScenario(Catalog catalog, IReadOnlyList<string> a, IReadOnlyList<string> b, float distance, DuelFacing facing, int seed,
            float limit = 90f)
        {
            var s = new SandboxScenario { Name = "duel", Map = SandboxMaps.FlatId, Seed = seed, Fog = false, Limit = limit };
            s.Sides[0].Ai = SandboxAi.Combat;
            s.Sides[1].Ai = SandboxAi.Combat;
            void Group(IReadOnlyList<string> ids, int team, Vector2 centre, float heading)
            {
                var spacing = 0f;
                foreach (var id in ids)
                    if (catalog.Vehicles.TryGetValue(id, out var def)) spacing = MathF.Max(spacing, SandboxRules.Spacing(def));
                var spots = SandboxRules.Formation(SandboxFormation.Line, ids.Count, centre, heading, spacing);
                for (var i = 0; i < ids.Count; i++)
                    s.Units.Add(new SandboxUnit { Def = ids[i], Team = team, Heading = SandboxRules.Normalise(heading), Position = spots[i] });
            }
            var half = distance * 0.5f;
            Group(a, 0, new Vector2(0f, -half), 0f);
            Group(b, 1, new Vector2(0f, half), facing switch { DuelFacing.Side => 90f, DuelFacing.Rear => 0f, _ => 180f });
            return s;
        }

        public readonly struct DuelResult
        {
            public DuelResult(int winner, double seconds, float hpA, float hpB)
            {
                Winner = winner;
                Seconds = seconds;
                HealthA = hpA;
                HealthB = hpB;
            }

            /// <summary>0 the first side, 1 the second, -1 a draw.</summary>
            public int Winner { get; }

            public double Seconds { get; }
            public float HealthA { get; }
            public float HealthB { get; }
        }

        public static DuelResult Duel(Catalog catalog, IReadOnlyList<string> a, IReadOnlyList<string> b, float distance, DuelFacing facing, int seed,
            float limit = 90f, Func<SandboxUnit, VehicleDef, VehicleBoost?>? boost = null)
        {
            var s = DuelScenario(catalog, a, b, distance, facing, seed, limit);
            var r = Run(catalog, SandboxMaps.Flat(), s, limit + 1f, boost);
            return new DuelResult(r.Winner < -1 ? -1 : r.Winner, r.Seconds, r.HealthLeft[0], r.HealthLeft[1]);
        }

        /// <summary>The duel over <paramref name="seeds"/> seeds from <paramref name="firstSeed"/>: the first side's wins, the second's, draws.</summary>
        public static (int a, int b, int draws) WinRate(Catalog catalog, IReadOnlyList<string> a, IReadOnlyList<string> b, float distance, DuelFacing facing,
            int seeds, int firstSeed = 1, float limit = 90f, Func<SandboxUnit, VehicleDef, VehicleBoost?>? boost = null)
        {
            var (wa, wb, draws) = (0, 0, 0);
            for (var i = 0; i < seeds; i++)
            {
                var r = Duel(catalog, a, b, distance, facing, firstSeed + i, limit, boost);
                if (r.Winner == 0) wa++;
                else if (r.Winner == 1) wb++;
                else draws++;
            }
            return (wa, wb, draws);
        }

        // ================================================================== A/B (F.3)

        /// <summary>
        /// The same scenario and seed under two configurations (two catalogs, the data before and after a change;
        /// or two equipment rules), the results side by side.
        /// </summary>
        public static (SandboxRunResult a, SandboxRunResult b) Compare(MapDefinition map, SandboxScenario scenario, float seconds,
            Catalog catalogA, Func<SandboxUnit, VehicleDef, VehicleBoost?>? boostA, Catalog catalogB, Func<SandboxUnit, VehicleDef, VehicleBoost?>? boostB) =>
            (Run(catalogA, map, scenario, seconds, boostA), Run(catalogB, map, scenario, seconds, boostB));
    }
}
