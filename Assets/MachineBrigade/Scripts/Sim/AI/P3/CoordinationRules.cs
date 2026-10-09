#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 149: the four internal stances.</summary>
    public enum UnitStance : byte
    {
        HoldFire,
        ReturnFire,
        Defend,
        AttackAnything,
    }

    /// <summary>Spec 136: a squad's part in an attack package.</summary>
    public enum PackageRole : byte
    {
        None,
        Main,
        Fix,
        Flank,
        Wave,
        Scout,
    }

    /// <summary>Spec 148 / 223: why a pursuit goes on or stops.</summary>
    public enum PursuitVerdict : byte
    {
        Continue,
        TargetGone,
        TimeOut,
        Leash,
        NotMissionRelevant,
    }

    /// <summary>Spec 125 / 219: tactical confidence, a mechanical 0-1 squad value (NOT morale; nothing reads health here).</summary>
    public static class TacticalConfidence
    {
        /// <summary>own / (own + enemy) style normalisation: even 0.5, 2:1 0.67, no enemy 1.</summary>
        public static float NormalizeForceRatio(float own, float enemy)
        {
            if (enemy <= 0f) return 1f;
            var r = MathF.Max(0f, own) / enemy;
            return r / (1f + r);
        }

        /// <summary>The spec's weighted sum, clamped 0-1 (weights from ai.confidence.weights).</summary>
        public static float Compute(float localRatio, float roleCoverage, float support, float position, float urgency, float intel)
        {
            var w = Tun.Confidence.Weights;
            float W(int i, float d) => i < w.Length ? w[i] : d;
            return Math.Clamp(W(0, global::MachineBrigade.Sim.Content.SimTunables.Ai.TacticalConfidence.ComputeD) * localRatio + W(1, global::MachineBrigade.Sim.Content.SimTunables.Ai.TacticalConfidence.ComputeD2) * roleCoverage + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.TacticalConfidence.ComputeI, global::MachineBrigade.Sim.Content.SimTunables.Ai.TacticalConfidence.ComputeD3) * support + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.TacticalConfidence.ComputeI2, global::MachineBrigade.Sim.Content.SimTunables.Ai.TacticalConfidence.ComputeD4) * position +
                              W(4, 0.10f) * urgency + W(5, 0.10f) * intel, 0f, 1f);
        }

        /// <summary>Spec 125 bands: aggressive / normal / cautious / no fresh commitment.</summary>
        public static string Band(float c) =>
            c >= Tun.Confidence.Aggressive ? "aggressive" : c >= Tun.Confidence.Cautious ? "normal" : c >= Tun.Confidence.NoCommit ? "cautious" : "noCommit";

        /// <summary>Under the no-commit band a squad takes no fresh commitment unless the objective is an emergency.</summary>
        public static bool MayCommit(float c, bool emergencyObjective) => emergencyObjective || c >= Tun.Confidence.NoCommit;
    }

    /// <summary>Spec 127: PathCost = Distance + Threat + Congestion x 0.8 + FriendlyRouteOccupancy x 0.5 + RecentLosses x 0.7 + UnknownRisk (+ repeat penalty).</summary>
    public static class RouteDiversity
    {
        public static float Cost(float distance, float threat, float congestion, int occupancy, float recentLosses, float unknownRisk, float repeatPenalty = 0f) =>
            distance / MathF.Max(1f, Tun.Routes.DistanceScale) + threat + congestion * Tun.Routes.CongestionWeight + occupancy * Tun.Routes.OccupancyWeight +
            recentLosses * Tun.Routes.LossWeight + unknownRisk + repeatPenalty;

        /// <summary>
        /// The cheapest of the routes for <paramref name="squad"/> with the occupancy of the side's other bookings added
        /// (ties: the lower index). A clearly best route is still taken twice: occupancy is a cost, not a ban.
        /// </summary>
        public static int Choose(IReadOnlyList<float> baseCosts, IReadOnlyList<Vector2> mids, RouteBook book, int squad, double now)
        {
            var best = -1;
            var bestCost = float.MaxValue;
            for (var i = 0; i < baseCosts.Count; i++)
            {
                var c = baseCosts[i] + book.Occupancy(mids[i], squad, now) * Tun.Routes.OccupancyWeight;
                if (c < bestCost - 1e-5f)
                {
                    bestCost = c;
                    best = i;
                }
            }
            return best;
        }
    }

    /// <summary>Spec 135 / 220: synchronized attack timing.</summary>
    public static class SyncPlanner
    {
        /// <summary>ETA over <paramref name="distance"/> at <paramref name="speed"/> with the path detour.</summary>
        public static float Eta(float distance, float speed) => MathF.Max(0f, distance) * Tun.AttackSync.Detour / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.SyncPlanner.EtaSpeedFloor, speed);

        /// <summary>Seconds from now to the package's execute time: the latest ETA, the artillery prep lead and the air cover.</summary>
        public static float ExecuteDelay(IReadOnlyList<float> groundEtas, float prepEta = 0f, float airEta = 0f)
        {
            var t = 0f;
            foreach (var e in groundEtas) t = MathF.Max(t, e);
            if (prepEta > 0f) t = MathF.Max(t, prepEta + Tun.AttackSync.ArtilleryPrepLeadS);
            if (airEta > 0f) t = MathF.Max(t, airEta - Tun.AttackSync.AirToleranceS);
            return MathF.Min(t, MathF.Max(0f, Tun.AttackSync.MaxStageS) + MathF.Max(0f, MinEta(groundEtas)));
        }

        private static float MinEta(IReadOnlyList<float> etas)
        {
            var m = float.MaxValue;
            foreach (var e in etas) m = MathF.Min(m, e);
            return m == float.MaxValue ? 0f : m;
        }

        /// <summary>How long a squad with <paramref name="eta"/> stages (overwatch) before moving: none inside the ground tolerance.</summary>
        public static float StageSeconds(float executeDelay, float eta)
        {
            var wait = executeDelay - eta;
            return wait > Tun.AttackSync.GroundToleranceS ? MathF.Min(wait, Tun.AttackSync.MaxStageS) : 0f;
        }

        /// <summary>The spread of contact times once every squad stages as planned (spec 224: within 3 s).</summary>
        public static float ContactDelta(IReadOnlyList<float> etas, float executeDelay)
        {
            float lo = float.MaxValue, hi = float.MinValue;
            foreach (var e in etas)
            {
                var arrive = e + StageSeconds(executeDelay, e);
                lo = MathF.Min(lo, arrive);
                hi = MathF.Max(hi, arrive);
            }
            return etas.Count == 0 ? 0f : hi - lo;
        }
    }

    /// <summary>Spec 136: the commander's package; the squads carry it out.</summary>
    public sealed class AttackPackage
    {
        public int Main;
        public int? Fix;
        public int? Flank;
        public int? Reserve;
        public int? Scout;
        public int FlankSide;
        public bool ArtilleryPrep;
        public bool AirCover;
        public Vector2 Target;
        public Vector2 Staging;
        public double CreatedAt;
        public double ExecuteAt;
        public double ScoutUntil = double.NegativeInfinity;
        public readonly List<int> Members = new();

        public override string ToString() =>
            $"main {Main}{(Fix.HasValue ? $" fix {Fix}" : "")}{(Flank.HasValue ? $" flank {Flank}" : "")}{(Reserve.HasValue ? $" reserve {Reserve}" : "")}" +
            $"{(Scout.HasValue ? $" scout {Scout}" : "")} -> ({Target.X:0},{Target.Y:0}) at {ExecuteAt:0.0}";
    }

    /// <summary>Spec 131: send a scout before the main force commits into high uncertainty (never wait forever).</summary>
    public static class ScoutPlanner
    {
        public static bool Needed(float unknownShare, float deathDanger, float urgency, bool shortTimer) =>
            !shortTimer && urgency < Tun.Pursuit.UrgencyDrop &&
            (unknownShare >= Tun.AttackSync.ScoutUnknownShare || deathDanger >= Tun.AttackSync.ScoutDeathDanger);

        /// <summary>The wait the main force accepts: the scout's ETA, clamped to 2 .. scoutMaxWaitS.</summary>
        public static float Wait(float scoutEta) => Math.Clamp(scoutEta, MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.ScoutPlanner.WaitScoutMaxWaitSCap, Tun.AttackSync.ScoutMaxWaitS), Tun.AttackSync.ScoutMaxWaitS);
    }

    /// <summary>Spec 134: fix-and-flank needs a stable enemy cluster, two access routes and enough power.</summary>
    public static class FixAndFlank
    {
        public static bool Viable(bool stableCluster, int accessRoutes, float ownPower, float enemyPower, float threshold) =>
            stableCluster && accessRoutes >= global::MachineBrigade.Sim.Content.SimTunables.Ai.FixAndFlank.ViableAccessRoutesMin && enemyPower > 0f && ownPower >= enemyPower * threshold * global::MachineBrigade.Sim.Content.SimTunables.Ai.FixAndFlank.ViableEnemyPowerScale;

        /// <summary>The Fix squad's goal: never closer than its envelope share of its reach (no suicide).</summary>
        public static Vector2 FixGoal(Vector2 from, Vector2 target, Vector2 goal, float reach)
        {
            var keep = reach * Tun.AttackSync.FixEnvelope;
            if (Vector2.Distance(goal, target) >= keep) return goal;
            return target - FrontlineModel.Dir(from, target) * keep;
        }
    }

    /// <summary>Spec 146-148, 206, 223: pursuit discipline, interception and cutoff.</summary>
    public static class PursuitDiscipline
    {
        /// <summary>Spec 223 ShouldContinuePursuit.</summary>
        public static PursuitVerdict Check(bool targetAlive, double now, double pursuitStart, float maxSeconds, Vector2 targetPos, Vector2 anchor,
            float maxDistance, float urgency, bool threatensObjective)
        {
            if (!targetAlive) return PursuitVerdict.TargetGone;
            if (now - pursuitStart > maxSeconds) return PursuitVerdict.TimeOut;
            if (Vector2.Distance(targetPos, anchor) > maxDistance) return PursuitVerdict.Leash;
            if (urgency > Tun.Pursuit.UrgencyDrop && !threatensObjective) return PursuitVerdict.NotMissionRelevant;
            return PursuitVerdict.Continue;
        }

        /// <summary>Spec 206: recent losses round the chase shrink the leash (never under baitLeashMin): emergent anti-bait.</summary>
        public static float BaitLeash(float leash, float deathDanger) =>
            leash * Math.Clamp(1f - Tun.Pursuit.BaitDangerScale * MathF.Max(0f, deathDanger), Tun.Pursuit.BaitLeashMin, 1f);

        /// <summary>
        /// Spec 146: the earliest t in (0, horizon] with |target + vel t - self| = speed t; the point at the horizon if none.
        /// <paramref name="age"/> (seconds since last seen) shortens the horizon: a hidden target's extrapolation fades.
        /// </summary>
        public static Vector2 Intercept(Vector2 self, float speed, Vector2 target, Vector2 velocity, float horizon, float age, out float t)
        {
            var h = horizon * Math.Clamp(1f - age / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.PursuitDiscipline.InterceptAgeFadeSFloor, Tun.Pursuit.AgeFadeS), 0f, 1f);
            var d = target - self;
            float a = Vector2.Dot(velocity, velocity) - speed * speed, b = global::MachineBrigade.Sim.Content.SimTunables.Ai.PursuitDiscipline.InterceptDotScale * Vector2.Dot(d, velocity), c = Vector2.Dot(d, d);
            t = h;
            if (MathF.Abs(a) < 1e-4f)
            {
                if (MathF.Abs(b) > 1e-4f && -c / b > 0f) t = MathF.Min(h, -c / b);
            }
            else
            {
                var disc = b * b - 4f * a * c;
                if (disc >= 0f)
                {
                    var sq = MathF.Sqrt(disc);
                    float t1 = (-b - sq) / (2f * a), t2 = (-b + sq) / (2f * a);
                    var best = float.MaxValue;
                    if (t1 > 0f) best = t1;
                    if (t2 > 0f && t2 < best) best = t2;
                    if (best < float.MaxValue) t = MathF.Min(h, best);
                }
            }
            return target + velocity * t;
        }

        /// <summary>Spec 147: cut off at a choke only when we get there first and sooner than a direct pursuit would catch it.</summary>
        public static bool CutoffBetter(float ourEtaToChoke, float theirEtaToChoke, float directInterceptEta) =>
            ourEtaToChoke < theirEtaToChoke && ourEtaToChoke < directInterceptEta;
    }

    /// <summary>Spec 170: a reason to commit the reserve: rank 1 HQ / boss critical, 2 breakthrough, 3 primary collapse, 4 exploit, 5 secondary.</summary>
    public readonly struct ReserveCandidate
    {
        public ReserveCandidate(int rank, Vector2 at, float own, float enemy, string code)
        {
            Rank = rank;
            At = at;
            Own = own;
            Enemy = enemy;
            Code = code;
        }

        public int Rank { get; }
        public Vector2 At { get; }
        public float Own { get; }
        public float Enemy { get; }
        public string Code { get; }
    }

    public static class ReserveLogic
    {
        /// <summary>The fight there is clearly won (or empty): no reserve goes in.</summary>
        public static bool Won(float own, float enemy) => enemy <= 0f || own / enemy >= Tun.ReserveRelease.WonRatio;

        /// <summary>The best release (lowest rank, then list order), skipping fights already won; -1: keep the reserve.</summary>
        public static int Pick(IReadOnlyList<ReserveCandidate> candidates)
        {
            var best = -1;
            for (var i = 0; i < candidates.Count; i++)
            {
                var c = candidates[i];
                if (Won(c.Own, c.Enemy)) continue;
                if (best < 0 || c.Rank < candidates[best].Rank) best = i;
            }
            return best;
        }
    }

    /// <summary>Spec 171, 172, 207, 211: objective-level rules.</summary>
    public static class ObjectiveRules
    {
        /// <summary>Spec 207: an ETA past the deadline (x slack) is useless for that objective; no deadline: always useful.</summary>
        public static bool DeadlineUseful(float eta, float deadline) =>
            float.IsInfinity(deadline) || deadline <= 0f || eta <= deadline * Tun.Objectives.DeadlineSlack;

        /// <summary>Spec 172: ExpectedRecoveryCost &gt; ObjectiveFutureValue: stop sending reinforcements there.</summary>
        public static bool SunkCostReset(float expectedRecoveryCost, float futureValue) => expectedRecoveryCost > futureValue;

        /// <summary>Spec 172: recovery cost from the decayed losses there and the odds now.</summary>
        public static float RecoveryCost(float lostThere, float own, float enemy) =>
            lostThere * Math.Clamp(enemy / MathF.Max(1f, own), global::MachineBrigade.Sim.Content.SimTunables.Ai.ObjectiveRules.RecoveryCostEnemyMin, global::MachineBrigade.Sim.Content.SimTunables.Ai.ObjectiveRules.RecoveryCostEnemyMax);

        /// <summary>Spec 171: what a secondary needs: enough to delay / screen / contest, capped by the share of the army.</summary>
        public static float SecondaryNeed(float enemyThere, float total) =>
            MathF.Min(enemyThere * Tun.Objectives.EconomyDelayShare, total * Tun.Objectives.EconomyMaxShare);

        /// <summary>Spec 211: hold lines from the objective back towards home.</summary>
        public static Vector2[] DepthLines(Vector2 objective, Vector2 home, int lines, float step)
        {
            var n = Math.Max(1, lines);
            var result = new Vector2[n];
            for (var i = 0; i < n; i++) result[i] = Vector2.Lerp(objective, home, Math.Clamp(i * step, 0f, global::MachineBrigade.Sim.Content.SimTunables.Ai.ObjectiveRules.DepthLinesIMax));
            return result;
        }
    }

    /// <summary>Spec 151: preferred range bands off the exact max / min (no oscillation at the limit).</summary>
    public static class RangeBands
    {
        public static float MarginShare(WeaponDef w)
        {
            if (w.MinRange > 0f || w.Lofted) return Tun.RangeMargin.Artillery;
            if (w.Guided && w.CanTarget(true) && !w.CanTarget(false)) return Tun.RangeMargin.AaMissile;
            if (w.Guided) return Tun.RangeMargin.Atgm;
            return Tun.RangeMargin.Direct;
        }

        public static float PreferredMax(WeaponDef w) => w.Range * (1f - MarginShare(w));

        public static float PreferredMin(WeaponDef w) => w.MinRange > 0f ? w.MinRange + w.Range * MarginShare(w) : 0f;
    }

    /// <summary>Spec 149: the stance mapping (ambush / recon hold or return fire, fragile support defends, assault attacks anything).</summary>
    public static class StanceRules
    {
        public static UnitStance For(DoctrineRole role, SquadAction action, bool ambushHolding, bool quiet)
        {
            if (ambushHolding) return UnitStance.HoldFire;
            if (role == DoctrineRole.Recon) return quiet || action is SquadAction.Hold or SquadAction.Overwatch ? UnitStance.ReturnFire : UnitStance.Defend;
            if (role is DoctrineRole.Support or DoctrineRole.FireSupport or DoctrineRole.Screen) return UnitStance.Defend;
            return action is SquadAction.Attack or SquadAction.FlankLeft or SquadAction.FlankRight or SquadAction.Support
                ? UnitStance.AttackAnything
                : UnitStance.Defend;
        }

        /// <summary>ReturnFire: only on what shoots at the side, or freely just after being hit.</summary>
        public static bool ReturnFireAllows(bool targetShootsAtUs, double now, double lastHit) =>
            targetShootsAtUs || now - lastHit <= Tun.Stance.ReturnFireSeconds;
    }

    /// <summary>Spec 145: shoot-and-scoot numbers per gun (deterministic by id).</summary>
    public static class ShootAndScoot
    {
        public static int Salvos(int gunId)
        {
            var s = Tun.FireMissions.ScootSalvos;
            int lo = s.Length > 0 ? s[0] : global::MachineBrigade.Sim.Content.SimTunables.Ai.ShootAndScoot.SalvosLengthFalse, hi = s.Length > 1 ? s[1] : lo;
            return lo + Math.Abs(gunId) % Math.Max(1, hi - lo + 1);
        }

        public static float Distance(int gunId)
        {
            var d = Tun.FireMissions.ScootDistance;
            float lo = d.Length > 0 ? d[0] : global::MachineBrigade.Sim.Content.SimTunables.Ai.ShootAndScoot.DistanceLengthFalse, hi = d.Length > 1 ? d[1] : lo;
            return lo + (Math.Abs(gunId * global::MachineBrigade.Sim.Content.SimTunables.Ai.ShootAndScoot.DistanceGunIdScale) % global::MachineBrigade.Sim.Content.SimTunables.Ai.ShootAndScoot.DistanceAbsMod) / 100f * (hi - lo);
        }

        /// <summary>Scoot after the gun's salvo count, or at once (one salvo fired) under a counter-battery threat.</summary>
        public static bool Due(int salvosFired, int gunId, bool counterBatteryThreat, bool enemyArtilleryKnown) =>
            (counterBatteryThreat && salvosFired > 0) || (enemyArtilleryKnown && salvosFired >= Salvos(gunId));
    }

    /// <summary>Spec 199: mass fire only on a high threat, a boss part, a near kill or a strategic unit; otherwise spread.</summary>
    public static class FocusRules
    {
        public static bool Strong(bool highThreat, bool bossPart, float hpShare, bool strategic) =>
            highThreat || bossPart || hpShare <= Tun.Board.NearKillShare || strategic;
    }
}
