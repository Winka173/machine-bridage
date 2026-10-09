#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>AI MASTER P4 spec 154: the commander's candidate plans (A attack now, B wait artillery, C flank, D split / hold).</summary>
    public enum PlanKind
    {
        AttackNow,
        WaitArtillery,
        Flank,
        SplitHold,
    }

    /// <summary>
    /// Spec 152 / 222: one side of a fight as the forecast sees it: what it can take (hit points), what it deals to the other
    /// side's mix (damage a second with armour / penetration already applied), its reach, its speed, its splash share and
    /// its support. Built by the commander from its own units and its known contacts only (fog-fair).
    /// </summary>
    public struct ForceEstimate
    {
        public float Hp;
        public float Strength;
        public float DpsGround;
        public float DpsAir;
        public float AirShare;
        public float Reach;
        public float Speed;
        public float SplashShare;
        public int Count;
        public float RepairPerS;
        public float SupportDps;

        public bool Empty => Hp <= 0f || Count <= 0;

        /// <summary>This force times <paramref name="k"/> (an uncertainty margin, a share of it).</summary>
        public ForceEstimate Scaled(float k)
        {
            var e = this;
            e.Hp *= k;
            e.Strength *= k;
            e.DpsGround *= k;
            e.DpsAir *= k;
            e.SupportDps *= k;
            e.RepairPerS *= k;
            return e;
        }

        /// <summary>Two forces as one (reinforcements joining).</summary>
        public static ForceEstimate Join(in ForceEstimate a, in ForceEstimate b)
        {
            if (b.Empty) return a;
            if (a.Empty) return b;
            var hp = a.Hp + b.Hp;
            return new ForceEstimate
            {
                Hp = hp,
                Strength = a.Strength + b.Strength,
                DpsGround = a.DpsGround + b.DpsGround,
                DpsAir = a.DpsAir + b.DpsAir,
                AirShare = (a.AirShare * a.Hp + b.AirShare * b.Hp) / hp,
                Reach = (a.Reach * a.Hp + b.Reach * b.Hp) / hp,
                Speed = MathF.Min(a.Speed, b.Speed),
                SplashShare = (a.SplashShare * a.Hp + b.SplashShare * b.Hp) / hp,
                Count = a.Count + b.Count,
                RepairPerS = a.RepairPerS + b.RepairPerS,
                SupportDps = a.SupportDps + b.SupportDps,
            };
        }
    }

    /// <summary>Spec 152 output: expected losses (hit points), the powers left after the horizon (0-1) and a breakthrough chance.</summary>
    public readonly struct CombatForecast
    {
        public CombatForecast(float friendlyLoss, float enemyLoss, float friendlyAfter, float enemyAfter, float breakthrough)
        {
            FriendlyLoss = friendlyLoss;
            EnemyLoss = enemyLoss;
            FriendlyPowerAfter = friendlyAfter;
            EnemyPowerAfter = enemyAfter;
            Breakthrough = breakthrough;
        }

        public float FriendlyLoss { get; }
        public float EnemyLoss { get; }
        public float FriendlyPowerAfter { get; }
        public float EnemyPowerAfter { get; }
        public float Breakthrough { get; }

        /// <summary>No contact: nothing lost on either side (plan D).</summary>
        public static CombatForecast None => new(0f, 0f, 1f, 1f, 0f);

        public override string ToString() => $"own {FriendlyPowerAfter:0%} enemy {EnemyPowerAfter:0%} break {Breakthrough:0%}";
    }

    /// <summary>
    /// Spec 152 / 222: the short-horizon combat forecast: a lightweight attrition estimate over 4-8 s in two half-steps (each
    /// side's damage shrinks with what it lost in the first half), with range uptime (the side out of reach closes first),
    /// splash density, support (guns in reach, repair) and the target mix (air / ground). No projectile physics, no search.
    /// </summary>
    public static class CombatForecaster
    {
        /// <summary>Share of the horizon a side's guns bear: none until the distance is closed to its reach at <paramref name="closing"/> m/s.</summary>
        public static float Uptime(float distance, float reach, float closing, float horizon)
        {
            if (horizon <= 0f) return 0f;
            var t = MathF.Max(0f, distance - reach) / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.CombatForecaster.UptimeClosingFloor, closing);
            return Math.Clamp((horizon - t) / horizon, Tun.Forecast.UptimeFloor, 1f);
        }

        /// <summary>The damage a second <paramref name="shooter"/> puts on <paramref name="target"/>'s mix (air share, splash on clusters).</summary>
        public static float EffectiveDps(in ForceEstimate shooter, in ForceEstimate target, float uptime, float scale = 1f)
        {
            if (shooter.Empty || target.Empty) return 0f;
            var mix = shooter.DpsGround * (1f - target.AirShare) + shooter.DpsAir * target.AirShare;
            var aoe = 1f + shooter.SplashShare * MathF.Min(Tun.Forecast.AoeMax, Tun.Forecast.AoeClusterBonus * MathF.Max(0, target.Count - 1));
            return mix * aoe * uptime * scale + shooter.SupportDps;
        }

        /// <summary>
        /// The forecast of <paramref name="friendly"/> going into <paramref name="enemy"/> from <paramref name="distance"/> m over
        /// <paramref name="horizon"/> s. <paramref name="friendlyScale"/> multiplies the own damage (side armour on a flank),
        /// <paramref name="enemyUptimeScale"/> the share of the enemy's guns that bear (a flank), <paramref name="enemyPreLoss"/>
        /// hit points the enemy lost before contact (an artillery prep).
        /// </summary>
        public static CombatForecast Forecast(in ForceEstimate friendly, in ForceEstimate enemy, float horizon, float distance,
            float friendlyScale = 1f, float enemyUptimeScale = 1f, float enemyPreLoss = 0f)
        {
            if (friendly.Empty) return new CombatForecast(0f, 0f, 0f, 1f, 0f);
            if (enemy.Empty) return new CombatForecast(0f, 0f, 1f, 0f, 1f);
            var uptimeF = Uptime(distance, friendly.Reach, friendly.Speed, horizon);
            var uptimeE = Uptime(distance, enemy.Reach, friendly.Speed, horizon) * Math.Clamp(enemyUptimeScale, 0f, 1f);
            var fHp = friendly.Hp;
            var eHp = MathF.Max(0f, enemy.Hp - MathF.Max(0f, enemyPreLoss));
            float fLeft = fHp, eLeft = eHp;
            var half = horizon * 0.5f;
            for (var step = 0; step < 2 && fLeft > 0f && eLeft > 0f; step++)
            {
                var fdps = EffectiveDps(friendly, enemy, uptimeF, friendlyScale) * (fLeft / fHp);
                var edps = EffectiveDps(enemy, friendly, uptimeE) * (eLeft / MathF.Max(1f, enemy.Hp));
                var eLoss = MathF.Min(eLeft, fdps * half);
                var fLoss = MathF.Min(fLeft, MathF.Max(0f, edps - friendly.RepairPerS) * half);
                eLeft -= eLoss;
                fLeft -= fLoss;
            }
            var fAfter = fHp > 0f ? fLeft / fHp : 0f;
            var eAfter = enemy.Hp > 0f ? eLeft / enemy.Hp : 0f;
            return new CombatForecast(fHp - fLeft, enemy.Hp - eLeft, fAfter, eAfter, Breakthrough(friendly.Strength * fAfter, enemy.Strength * eAfter));
        }

        /// <summary>
        /// Depth 2 (spec 154, Hard and up): after the first horizon the enemy's known reinforcements within reach join the
        /// survivors for a shorter second step. Still one forecast per plan, no branching.
        /// </summary>
        public static CombatForecast Deepen(in CombatForecast first, in ForceEstimate friendly, in ForceEstimate enemy, in ForceEstimate reinforcement, float horizon)
        {
            if (reinforcement.Empty || first.FriendlyPowerAfter <= 0f) return first;
            var f = friendly.Scaled(first.FriendlyPowerAfter);
            var e = ForceEstimate.Join(enemy.Scaled(first.EnemyPowerAfter), reinforcement);
            var second = Forecast(f, e, horizon * Tun.Forecast.DepthTwoShare, 0f);
            var fAfter = first.FriendlyPowerAfter * second.FriendlyPowerAfter;
            var eLeft = e.Hp * second.EnemyPowerAfter;
            var eAll = enemy.Hp + reinforcement.Hp;
            var eAfter = eAll > 0f ? eLeft / eAll : 0f;
            return new CombatForecast(friendly.Hp * (1f - fAfter), eAll - eLeft, fAfter, eAfter,
                Breakthrough(friendly.Strength * fAfter, (enemy.Strength + reinforcement.Strength) * eAfter));
        }

        /// <summary>Own share of the power left on the ground (0.5: an even fight).</summary>
        public static float Breakthrough(float own, float enemy) => own + enemy <= 0f ? 0f : Math.Clamp(own / (own + enemy), 0f, 1f);

        /// <summary>
        /// P0-B open item (section 18): the force is enough to stop buying: own power at least <c>enoughRatio</c> x the known
        /// enemy's, the forecast leaves the enemy weak and the own force mostly whole; never on too few known enemies.
        /// </summary>
        public static bool Enough(float ownStrength, float enemyStrength, int knownEnemies, in CombatForecast f) =>
            knownEnemies >= Tun.Forecast.EnoughMinKnown && enemyStrength > 0f &&
            ownStrength >= enemyStrength * Tun.Forecast.EnoughRatio &&
            f.EnemyPowerAfter <= Tun.Forecast.EnoughEnemyAfter && f.FriendlyPowerAfter >= 0.5f;
    }

    /// <summary>Spec 154: one candidate plan with the terms of its utility.</summary>
    public struct PlanCandidate
    {
        public PlanKind Kind;
        public bool Valid;
        public CombatForecast Forecast;
        public float ObjectiveGain, EnemyLossValue, FriendlyLossValue, DelayCost, CongestionCost, UncertaintyRisk, OpportunityGain;
        public float RepeatPenalty;
        public float DelaySeconds;
        public int FlankSide;
        public float Utility;

        public override string ToString() =>
            $"{Kind}{(FlankSide != 0 ? FlankSide < 0 ? " L" : " R" : "")} U {Utility:0.0} ({Forecast}; gain {ObjectiveGain:0} + {EnemyLossValue:0} - {FriendlyLossValue:0} - delay {DelayCost:0.0}" +
            $"{(OpportunityGain > 0f ? $" + window {OpportunityGain:0}" : "")}{(RepeatPenalty > 0f ? $", repeat -{RepeatPenalty:0%}" : "")}){(Valid ? "" : " invalid")}";
    }

    /// <summary>
    /// Spec 154: shallow counterfactual planning. Each candidate is one forecast (depth 1, or 2 with the enemy's known
    /// reinforcements) scored PlanUtility = ObjectiveGain + EnemyLossValue - FriendlyLossValue - DelayCost - CongestionCost -
    /// UncertaintyRisk (+ an opportunity window's gain); a plan that just failed carries spec 158's penalty. No deep search.
    /// </summary>
    public static class ShallowPlanner
    {
        private static readonly PlanKind[] Order = { PlanKind.AttackNow, PlanKind.Flank, PlanKind.WaitArtillery, PlanKind.SplitHold };

        /// <summary>Spec 216: the plans a difficulty weighs (Easy: attack now only; Normal: + flank; Hard: + wait artillery; Very Hard: all four).</summary>
        public static int Count(int level) => Math.Clamp(DifficultyGate.Plans(level), 1, Order.Length);

        public static PlanKind Kind(int index) => Order[Math.Clamp(index, 0, Order.Length - 1)];

        /// <summary>Fills a candidate's utility terms from its forecast and costs.</summary>
        public static PlanCandidate Score(PlanKind kind, in CombatForecast f, float ownStrength, float enemyStrength, float delaySeconds,
            float urgency, float congestion, float unknownShare, float opportunity, float repeatPenalty, bool valid = true, int flankSide = 0)
        {
            var c = new PlanCandidate
            {
                Kind = kind,
                Valid = valid,
                Forecast = f,
                FlankSide = flankSide,
                DelaySeconds = delaySeconds,
                ObjectiveGain = kind == PlanKind.SplitHold ? 0f : Tun.Planning.ObjectiveGain * f.Breakthrough,
                EnemyLossValue = enemyStrength * (1f - f.EnemyPowerAfter) * Tun.Planning.EnemyLossWeight,
                FriendlyLossValue = ownStrength * (1f - f.FriendlyPowerAfter) * Tun.Planning.FriendlyLossWeight,
                DelayCost = MathF.Max(0f, delaySeconds) * Tun.Planning.DelayCostPerS * (1f + Math.Clamp(urgency, 0f, 1f)),
                CongestionCost = MathF.Max(0f, congestion) * Tun.Planning.CongestionWeight,
                UncertaintyRisk = Math.Clamp(unknownShare, 0f, 1f) * Tun.Planning.UncertaintyWeight,
                OpportunityGain = MathF.Max(0f, opportunity),
                RepeatPenalty = Math.Clamp(repeatPenalty, 0f, global::MachineBrigade.Sim.Content.SimTunables.Ai.ShallowPlanner.ScoreRepeatPenaltyMax),
            };
            c.Utility = Utility(c);
            return c;
        }

        /// <summary>PlanUtility (spec 154) with the anti-repetition penalty (spec 158: lowers a good score, deepens a bad one).</summary>
        public static float Utility(in PlanCandidate c)
        {
            var raw = c.ObjectiveGain + c.OpportunityGain + c.EnemyLossValue - c.FriendlyLossValue - c.DelayCost - c.CongestionCost - c.UncertaintyRisk;
            return raw >= 0f ? raw * (1f - c.RepeatPenalty) : raw * (1f + c.RepeatPenalty);
        }

        /// <summary>
        /// The plan to follow: the best valid one; the current one stays unless the best beats it by the switch margin; an
        /// attack plan that leaves less than <c>holdPowerFloor</c> of the own force loses to a valid hold (pre-contact only).
        /// Ties go to the plan order (A, C, B, D), so a replay picks the same. -1: no valid plan.
        /// </summary>
        public static int Pick(IReadOnlyList<PlanCandidate> plans, int current = -1)
        {
            var best = -1;
            for (var i = 0; i < plans.Count; i++)
            {
                var p = plans[i];
                if (!p.Valid) continue;
                if (best < 0 || Better(p, plans[best])) best = i;
            }
            if (best < 0) return -1;
            if (current >= 0 && current < plans.Count && current != best && plans[current].Valid)
            {
                var cu = plans[current].Utility;
                var margin = MathF.Abs(cu) * Tun.Planning.SwitchMargin;
                if (plans[best].Utility < cu + margin) best = current;
            }
            return best;
        }

        private static bool Better(in PlanCandidate a, in PlanCandidate b)
        {
            var aWeak = a.Kind != PlanKind.SplitHold && a.Forecast.FriendlyPowerAfter < Tun.Planning.HoldPowerFloor;
            var bWeak = b.Kind != PlanKind.SplitHold && b.Forecast.FriendlyPowerAfter < Tun.Planning.HoldPowerFloor;
            if (a.Kind == PlanKind.SplitHold && bWeak) return true;
            if (b.Kind == PlanKind.SplitHold && aWeak) return false;
            return a.Utility > b.Utility + 1e-4f;
        }
    }

    /// <summary>
    /// Spec 183: what an attack package was planned on (route version, objective version, target-cluster version, support
    /// availability). <see cref="Broken"/> names the dependency that changed enough to matter, or null: small changes never
    /// invalidate a plan.
    /// </summary>
    public readonly struct PlanDependencies
    {
        public PlanDependencies(int routeVersion, int objectiveVersion, Vector2 clusterCentre, float clusterStrength, bool artillery, bool air)
        {
            RouteVersion = routeVersion;
            ObjectiveVersion = objectiveVersion;
            ClusterCentre = clusterCentre;
            ClusterStrength = clusterStrength;
            Artillery = artillery;
            Air = air;
        }

        public int RouteVersion { get; }
        public int ObjectiveVersion { get; }
        public Vector2 ClusterCentre { get; }
        public float ClusterStrength { get; }
        public bool Artillery { get; }
        public bool Air { get; }

        /// <summary>A hash of the versions (the cluster in 25 m cells, the strength in x1.5 steps) for the log.</summary>
        public int Hash
        {
            get
            {
                unchecked
                {
                    var h = RouteVersion * 397 ^ ObjectiveVersion;
                    h = h * 397 ^ (int)MathF.Floor(ClusterCentre.X / 25f);
                    h = h * 397 ^ (int)MathF.Floor(ClusterCentre.Y / 25f);
                    h = h * 397 ^ (ClusterStrength > 0f ? (int)MathF.Floor(MathF.Log(ClusterStrength + 1f) / MathF.Log(1.5f)) : -1);
                    return h * 397 ^ (Artillery ? 1 : 0) ^ (Air ? 2 : 0);
                }
            }
        }

        /// <summary>The important dependency that changed (a reason code), or null.</summary>
        public static string? Broken(in PlanDependencies made, in PlanDependencies now, PlanKind kind)
        {
            if (now.RouteVersion != made.RouteVersion) return P4Reasons.DepRoute;
            if (now.ObjectiveVersion != made.ObjectiveVersion) return P4Reasons.DepObjective;
            if (made.ClusterStrength > 0f && now.ClusterStrength >= made.ClusterStrength * Tun.PackageAbort.EnemyRise) return P4Reasons.DepEnemyRise;
            if (made.ClusterStrength > 0f && now.ClusterStrength > 0f && Vector2.Distance(made.ClusterCentre, now.ClusterCentre) > Tun.PackageAbort.ClusterShift)
                return P4Reasons.DepCluster;
            if (kind == PlanKind.WaitArtillery && made.Artillery && !now.Artillery) return P4Reasons.DepSupport;
            return null;
        }
    }

    /// <summary>Spec 182: what may interrupt a plan (small changes never do).</summary>
    public enum ReplanTrigger
    {
        None,
        TargetDead,
        RouteBlocked,
        LethalWarning,
        SupportLost,
        ObjectiveChanged,
    }

    /// <summary>
    /// Spec 155: abort an attack package before contact when its assumptions broke: route invalidated, the primary squad
    /// lost before it arrived, the flank blocked, the objective changed, the enemy estimate rose strongly, the support mission
    /// failed. There is deliberately no input for a unit's health: one damaged unit never aborts a package.
    /// </summary>
    public static class AbortRules
    {
        public static string? Check(bool beforeContact, string? brokenDependency, bool mainLost, bool flankBlocked, bool supportFailed)
        {
            if (!beforeContact) return null;
            if (mainLost) return P4Reasons.AbortMainLost;
            if (flankBlocked) return P4Reasons.AbortFlankBlocked;
            if (supportFailed) return P4Reasons.AbortSupportFailed;
            return brokenDependency;
        }

        /// <summary>Spec 182: a trigger worth a replan (re-scoring the plans now, inside the commitment window).</summary>
        public static bool Replan(ReplanTrigger t) => t != ReplanTrigger.None;
    }

    /// <summary>
    /// Spec 158: anti-repetition. A plan that just failed (plan kind at a target cell) gets a 25-50 % penalty by how badly it
    /// failed, halving every <c>repeatHalfLifeS</c>. Never random: it only lowers the score of what just proved bad.
    /// </summary>
    public sealed class RepetitionMemory
    {
        private readonly Dictionary<long, (float penalty, double at)> _failed = new();

        public static long Key(PlanKind kind, Vector2 target) =>
            ((long)MathF.Floor(target.X / 30f) * 100003L + (long)MathF.Floor(target.Y / 30f)) * 8L + (long)kind;

        public void Fail(long key, float severity, double now)
        {
            var range = Tun.Planning.RepeatPenalty;
            var p = range.Length >= global::MachineBrigade.Sim.Content.SimTunables.Ai.RepetitionMemory.FailLengthMin ? range[0] + (range[1] - range[0]) * Math.Clamp(severity, 0f, 1f) : global::MachineBrigade.Sim.Content.SimTunables.Ai.RepetitionMemory.FailLengthFalse;
            _failed[key] = (MathF.Max(p, Penalty(key, now)), now);
        }

        public float Penalty(long key, double now)
        {
            if (!_failed.TryGetValue(key, out var f)) return 0f;
            var age = (float)(now - f.at);
            return age < 0f ? f.penalty : f.penalty * MathF.Pow(global::MachineBrigade.Sim.Content.SimTunables.Ai.RepetitionMemory.PenaltyAgeExponent, age / MathF.Max(1f, Tun.Planning.RepeatHalfLifeS));
        }

        public void Prune(double now)
        {
            if (_failed.Count < global::MachineBrigade.Sim.Content.SimTunables.Ai.RepetitionMemory.PruneCountMax) return;
            var old = new List<long>();
            foreach (var kv in _failed)
                if (Penalty(kv.Key, now) < global::MachineBrigade.Sim.Content.SimTunables.Ai.RepetitionMemory.PrunePenaltyMax) old.Add(kv.Key);
            foreach (var k in old) _failed.Remove(k);
        }
    }

    /// <summary>Spec 132: what a probe found.</summary>
    public enum ProbeOutcome
    {
        Pending,
        Exploit,
        Threat,
        Blocked,
        Inconclusive,
    }

    /// <summary>Spec 132: probe-and-exploit rules (a small force, 8-15 % of the power, never a suicide).</summary>
    public static class ProbeRules
    {
        public static bool ShareFits(float squadStrength, float armyStrength)
        {
            if (armyStrength <= 0f || squadStrength <= 0f) return false;
            var share = squadStrength / armyStrength;
            var r = Tun.Probe.PowerShare;
            return share >= r[0] - 1e-4f && share <= r[1] + 1e-4f;
        }

        /// <summary>
        /// The verdict on a lane: blocked (no progress) first; high anti-tank / ambush (threat per probe strength over
        /// <c>atThreat</c>, or a third of the probe lost); low resistance once there or at the time limit (seen enemy / probe
        /// strength under <c>lowResistance</c>): an exploit window; else inconclusive at the time limit.
        /// </summary>
        public static ProbeOutcome Judge(float seenEnemy, float antiTankThreat, float probeStrength, float lossShare, bool blocked, bool arrived, bool timeUp)
        {
            if (blocked) return ProbeOutcome.Blocked;
            var p = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProbeRules.JudgeProbeStrengthFloor, probeStrength);
            if (antiTankThreat / p >= Tun.Probe.AtThreat || lossShare >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProbeRules.JudgeLossShareMin) return ProbeOutcome.Threat;
            if ((arrived || timeUp) && seenEnemy / p < Tun.Probe.LowResistance) return ProbeOutcome.Exploit;
            return timeUp ? ProbeOutcome.Inconclusive : ProbeOutcome.Pending;
        }

        /// <summary>A probe / feint goal: never closer than <c>envelope</c> x reach to the nearest known enemy (it keeps its way back).</summary>
        public static Vector2 EnvelopeGoal(Vector2 from, Vector2? enemy, Vector2 goal, float reach)
        {
            if (enemy is not { } e) return goal;
            var keep = Tun.Probe.Envelope * MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProbeRules.EnvelopeGoalReachFloor, reach);
            if (Vector2.Distance(goal, e) >= keep) return goal;
            var away = goal - e;
            if (away.LengthSquared() < 0.01f) away = from - e;
            if (away.LengthSquared() < 0.01f) return goal;
            return e + Vector2.Normalize(away) * keep;
        }
    }

    /// <summary>
    /// Spec 133: the conditional feint. It needs a tactical utility of its own (contest a secondary point, force spotting,
    /// threaten a flank, pin a turret arc); Hard / Very Hard or a tactic that plays it (pincer / flank-heavy), never on Easy,
    /// never under an objective emergency (226). It counts as a success only when the enemy is SEEN redeploying.
    /// </summary>
    public static class FeintRules
    {
        public static float Utility(bool contestsSecondary, float unknownShare, bool threatensFlank, bool pinsArc)
        {
            var w = Tun.Feint.Weights;
            float W(int i) => i < w.Length ? w[i] : 0f;
            return (contestsSecondary ? W(0) : 0f) + Math.Clamp(unknownShare, 0f, 1f) * W(1) + (threatensFlank ? W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FeintRules.UtilityI) : 0f) + (pinsArc ? W(global::MachineBrigade.Sim.Content.SimTunables.Ai.FeintRules.UtilityI2) : 0f);
        }

        public static bool Allowed(int level, bool tacticFits, float urgency, float utility) =>
            DifficultyGate.Feint(level, tacticFits) && urgency < Tun.Pursuit.UrgencyDrop && utility >= Tun.Feint.MinUtility;

        /// <summary>Success from what was seen: the seen enemy at the main objective fell by the redeploy share while more was seen at the feint.</summary>
        public static bool Succeeded(float seenAtMainBefore, float seenAtMainNow, float seenAtFeintBefore, float seenAtFeintNow) =>
            seenAtMainBefore > 0f && (seenAtMainBefore - seenAtMainNow) / seenAtMainBefore >= Tun.Feint.RedeployShare && seenAtFeintNow > seenAtFeintBefore + 0.01f;
    }

    /// <summary>Spec 156: the kinds of opportunity windows.</summary>
    public enum OpportunityKind
    {
        AntiAirDown,
        BossPartDown,
        ArtilleryExposed,
        DefendersRedeploy,
        GateOpen,
        MainForceFar,
        ProbeExploit,
        FeintSuccess,
    }

    /// <summary>Spec 156: the roles an opportunity needs.</summary>
    [Flags]
    public enum OpportunityRoles
    {
        None = 0,
        Ground = 1,
        Fast = 2,
        Air = 4,
        Artillery = 8,
    }

    /// <summary>Spec 156: an opportunity / exploit window: location, confidence, expiry, required roles.</summary>
    public sealed class OpportunityWindow
    {
        public OpportunityWindow(OpportunityKind kind, Vector2 centre, float radius, float confidence, double expires, OpportunityRoles roles, int subject = 0)
        {
            Kind = kind;
            Centre = centre;
            Radius = radius;
            Confidence = confidence;
            Expires = expires;
            Roles = roles;
            Subject = subject;
        }

        public OpportunityKind Kind { get; }
        public Vector2 Centre { get; }
        public float Radius { get; }
        public float Confidence { get; }
        public double Expires { get; internal set; }
        public OpportunityRoles Roles { get; }

        /// <summary>The entity or lane it is about (0: none): one window per subject and kind.</summary>
        public int Subject { get; }

        public bool Covers(Vector2 p, float extra = 0f) => Vector2.Distance(Centre, p) <= Radius + extra;

        public override string ToString() => $"{Kind} ({Centre.X:0},{Centre.Y:0}) r{Radius:0} c{Confidence:0.00} {Roles}";
    }

    /// <summary>
    /// Spec 181: escape-sector reservation under a telegraphed area attack. 3-5 sectors round the ring (exits a margin
    /// outside it); blocked ones (off the map, another ring, unwalkable) are dropped; each member takes the cheapest sector
    /// with room (capacity = ceil(n / open sectors)), so a squad never runs to one point. A learnt pattern (spec 214) adds a
    /// cost to the sectors its follow-up zones covered. Deterministic: members in the given order.
    /// </summary>
    public static class EscapeSectors
    {
        /// <summary>
        /// The sector of each member (-1: none open; the caller falls back to the radial way out) and the exit points.
        /// <paramref name="axis"/> orients sector 0 (the boss-to-ring direction, so a pattern is learnt in the boss's frame).
        /// </summary>
        public static int[] Assign(Vector2 centre, float radius, IReadOnlyList<Vector2> members, int sectors, Vector2 axis,
            Func<Vector2, bool>? blocked, float[]? extraCost, out Vector2[] exits)
        {
            sectors = Math.Clamp(sectors, 1, global::MachineBrigade.Sim.Content.SimTunables.Ai.EscapeSectors.AssignSectorsMax);
            var n = members.Count;
            var result = new int[n];
            exits = new Vector2[n];
            var dirs = new Vector2[sectors];
            var points = new Vector2[sectors];
            var open = new bool[sectors];
            var openCount = 0;
            var a0 = axis.LengthSquared() > 1e-4f ? MathF.Atan2(axis.Y, axis.X) : 0f;
            var reachOut = radius + Tun.BossTactics.SectorMargin;
            for (var k = 0; k < sectors; k++)
            {
                var a = a0 + k * MathF.PI * 2f / sectors;
                dirs[k] = new Vector2(MathF.Cos(a), MathF.Sin(a));
                points[k] = centre + dirs[k] * reachOut;
                open[k] = blocked == null || !blocked(points[k]);
                if (open[k]) openCount++;
            }
            if (openCount == 0)
            {
                for (var i = 0; i < n; i++) result[i] = -1;
                return result;
            }
            var capacity = (int)MathF.Ceiling(n / (float)openCount);
            var used = new int[sectors];
            for (var i = 0; i < n; i++)
            {
                var best = -1;
                var bestCost = float.MaxValue;
                for (var k = 0; k < sectors; k++)
                {
                    if (!open[k] || used[k] >= capacity) continue;
                    var cost = Vector2.Distance(members[i], points[k]) + (extraCost != null && k < extraCost.Length ? extraCost[k] : 0f);
                    if (cost < bestCost - 1e-4f)
                    {
                        best = k;
                        bestCost = cost;
                    }
                }
                result[i] = best;
                if (best < 0) continue;
                // Members of one sector stand side by side along the ring (4 m apart), never on one point.
                var lateral = new Vector2(-dirs[best].Y, dirs[best].X);
                var slot = used[best];
                var offset = slot == 0 ? 0f : ((slot + 1) / 2) * global::MachineBrigade.Sim.Content.SimTunables.Ai.EscapeSectors.AssignSlotScale * (slot % 2 == 1 ? 1f : -1f);
                exits[i] = points[best] + lateral * offset;
                used[best]++;
            }
            return result;
        }

        /// <summary>The sector (0..sectors-1) a point lies in, in the frame of <paramref name="axis"/>.</summary>
        public static int SectorOf(Vector2 centre, Vector2 axis, Vector2 p, int sectors)
        {
            var d = p - centre;
            if (d.LengthSquared() < 1e-4f) return 0;
            var a0 = axis.LengthSquared() > 1e-4f ? MathF.Atan2(axis.Y, axis.X) : 0f;
            var a = MathF.Atan2(d.Y, d.X) - a0;
            var step = MathF.PI * 2f / sectors;
            var k = (int)MathF.Floor((a + step * 0.5f) / step);
            return ((k % sectors) + sectors) % sectors;
        }
    }

    /// <summary>
    /// Spec 214: within-encounter pattern learning. When a boss's telegraphed attack is followed (inside the pattern window)
    /// by another zone of the same boss, the follow-up's bearing (in the boss-to-first-zone frame, 8 bins) is counted; the
    /// next time the same attack shows, escape sectors that way cost more. Only telegraphs that were seen; no hidden future.
    /// Reset with the match (it lives in the side's planning state).
    /// </summary>
    public sealed class PatternMemory
    {
        public const int Bins = 8;
        private readonly Dictionary<int, (int seen, int[] hits)> _patterns = new();

        /// <summary>A pattern key: the boss and the ring's size class.</summary>
        public static int Signature(int source, float radius) => unchecked(source * global::MachineBrigade.Sim.Content.SimTunables.Ai.PatternMemory.SignatureSourceScale + (int)MathF.Round(radius / global::MachineBrigade.Sim.Content.SimTunables.Ai.PatternMemory.SignatureRadiusDivisor));

        public void Seen(int signature)
        {
            if (!_patterns.TryGetValue(signature, out var p)) p = (0, new int[Bins]);
            _patterns[signature] = (p.seen + 1, p.hits);
        }

        public void FollowUp(int signature, Vector2 centre, Vector2 axis, Vector2 followCentre)
        {
            if (!_patterns.TryGetValue(signature, out var p)) p = (1, new int[Bins]);
            p.hits[EscapeSectors.SectorOf(centre, axis, followCentre, Bins)]++;
            _patterns[signature] = p;
        }

        /// <summary>How often a follow-up came down towards <paramref name="direction"/> (0-1 per seen attack).</summary>
        public float Risk(int signature, Vector2 axis, Vector2 direction)
        {
            if (!_patterns.TryGetValue(signature, out var p) || p.seen <= 0) return 0f;
            var bin = EscapeSectors.SectorOf(Vector2.Zero, axis, direction, Bins);
            return Math.Clamp(p.hits[bin] / (float)p.seen, 0f, 1f);
        }

        public int Count => _patterns.Count;
    }

    /// <summary>
    /// Spec 204: the pressure budget. With <c>pressureBudget</c> dangerous actions already active (a bomb warning, a missile
    /// volley, an artillery strike), a non-critical one waits <c>pressureDelayS</c>, at most <c>pressureMaxDelayS</c> in all;
    /// the cooldown after it is shortened by the wait, so the damage over the fight is unchanged (pacing, not a nerf). A
    /// scripted / critical action never waits (226).
    /// </summary>
    public static class PressureBudget
    {
        public static bool Defer(int activeDangerous, bool critical, float deferredSoFar) =>
            !critical && activeDangerous >= Tun.BossTactics.PressureBudget && deferredSoFar + 1e-4f < Tun.BossTactics.PressureMaxDelayS;

        public static float Wait(float deferredSoFar) => MathF.Min(Tun.BossTactics.PressureDelayS, MathF.Max(0f, Tun.BossTactics.PressureMaxDelayS - deferredSoFar));

        public static float NextCooldown(float cooldown, float deferred, float minimum) => MathF.Max(minimum, cooldown - MathF.Max(0f, deferred));
    }

    /// <summary>
    /// Spec 179: a boss part's worth to an AI shooter: the damage a second it would silence, a utility part (APS / shield /
    /// radar / jammer), its phase utility (it carries the big attack or the lock) and kill progress (nearly broken). The
    /// parts' functions are game rules shown to the player, not hidden intel.
    /// </summary>
    public static class WeakpointUtility
    {
        public static float Score(float disabledDps, bool utilityPart, float phaseUtility, float healthShareLeft, float distance)
        {
            var w = Tun.BossTactics.WeakpointWeights;
            float W(int i) => i < w.Length ? w[i] : 0f;
            return W(0) * MathF.Max(0f, disabledDps) + (utilityPart ? W(1) : 0f) + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.WeakpointUtility.ScoreI) * Math.Clamp(phaseUtility, 0f, 1f) +
                   W(global::MachineBrigade.Sim.Content.SimTunables.Ai.WeakpointUtility.ScoreI2) * (1f - Math.Clamp(healthShareLeft, 0f, 1f)) - distance * global::MachineBrigade.Sim.Content.SimTunables.Ai.WeakpointUtility.ScoreDistanceScale;
        }

        /// <summary>A part kind that names an APS, shield, radar, jammer or sensor.</summary>
        public static bool IsUtilityKind(string kind)
        {
            var k = kind.ToLowerInvariant();
            return k.Contains("aps") || k.Contains("shield") || k.Contains("radar") || k.Contains("jammer") || k.Contains("sensor") || k.Contains("dome");
        }
    }

    /// <summary>Spec 184: commitment windows (a deterministic length inside the range per subject).</summary>
    public static class CommitmentWindows
    {
        public static float Seconds(float[] range, int subject, int salt = 0)
        {
            if (range.Length == 0) return 0f;
            if (range.Length == 1) return range[0];
            return range[0] + (range[1] - range[0]) * HumanStagger.Unit(subject, salt);
        }

        /// <summary>Still inside the window (emergency safety breaks it).</summary>
        public static bool Holds(double since, double now, float seconds, bool emergency) => !emergency && now - since < seconds;
    }

    /// <summary>Spec 217: deterministic human-like stagger: delay = window min + hash(unit, event) % window (never Random).</summary>
    public static class HumanStagger
    {
        public static uint Hash(int a, int b)
        {
            unchecked
            {
                var h = (uint)a * 0x9E3779B1u ^ (uint)b * 0x85EBCA77u ^ 0x27D4EB2Fu;
                h ^= h >> 15;
                h *= 0x2C1B3C6Du;
                h ^= h >> 12;
                h *= 0x297A2D39u;
                h ^= h >> 15;
                return h;
            }
        }

        /// <summary>0-1 from the hash.</summary>
        public static float Unit(int a, int b) => (Hash(a, b) % 1000u) / 999f;

        public static float Delay(int unitId, int eventId)
        {
            var w = Tun.Stagger.Window;
            if (w.Length < global::MachineBrigade.Sim.Content.SimTunables.Ai.HumanStagger.DelayLengthMax) return w.Length == 1 ? w[0] : 0f;
            var ms = (int)MathF.Round((w[1] - w[0]) * 1000f);
            return w[0] + (ms > 0 ? Hash(unitId, eventId) % (uint)(ms + 1) : 0u) / 1000f;
        }
    }

    /// <summary>Spec 216: advanced difficulty gating (levels 0 Easy, 1 Normal, 2 Hard, 3 Very Hard; still fog-fair at every level).</summary>
    public static class DifficultyGate
    {
        private static int At(int[] a, int level) => a.Length == 0 ? 1 : a[Math.Clamp(level, 0, a.Length - 1)];

        public static int Plans(int level) => At(Tun.Planning.PlansByLevel, level);
        public static int Depth(int level) => At(Tun.Planning.DepthByLevel, level);
        public static int Sectors(int level) => Math.Clamp(At(Tun.BossTactics.SectorsByLevel, level), 1, global::MachineBrigade.Sim.Content.SimTunables.Ai.DifficultyGate.SectorsAtMax);
        public static bool Probe(int level) => level >= Tun.Gating.ProbeLevel;
        public static bool Feint(int level, bool tacticFits) => level >= Tun.Gating.FeintLevel || (tacticFits && level >= 1);
        public static bool Adaptation(int level) => level >= Tun.Gating.AdaptationLevel;
        public static bool Sead(int level) => level >= Tun.Gating.SeadLevel;
        public static bool Pattern(int level) => level >= Tun.Gating.PatternLevel;
        public static bool AirPackages(int level) => level >= Tun.Gating.BomberLevel;
    }

    /// <summary>Spec 174-178: air package rules (risk, handoff, bomber gate, CAP leash, patrol).</summary>
    public static class AirRules
    {
        /// <summary>Spec 175 AirRiskMap: risk of a leg = mean + half the max of the anti-air threat sampled along it.</summary>
        public static float LegRisk(Func<Vector2, float> threatAt, Vector2 a, Vector2 b, int samples)
        {
            samples = Math.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.AirRules.LegRiskSamplesFloor, samples);
            float sum = 0f, max = 0f;
            for (var i = 0; i < samples; i++)
            {
                var t = threatAt(Vector2.Lerp(a, b, (i + 0.5f) / samples));
                sum += t;
                max = MathF.Max(max, t);
            }
            return sum / samples + max * global::MachineBrigade.Sim.Content.SimTunables.Ai.AirRules.LegRiskMaxScale;
        }

        /// <summary>Spec 177: attackers on one aircraft: enough to reach the TTK goal, 1-2 (never six on one weak target).</summary>
        public static int Attackers(float targetHp, float dpsPerAttacker, float ttkGoal, int max)
        {
            if (dpsPerAttacker <= 0f) return 1;
            var need = (int)MathF.Ceiling(targetHp / MathF.Max(1e-3f, dpsPerAttacker * MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.AirRules.AttackersTtkGoalFloor, ttkGoal)));
            return Math.Clamp(need, 1, Math.Max(1, max));
        }

        public static bool SeadNeeded(float antiAirThreat, float strikeStrength) => antiAirThreat / MathF.Max(1f, strikeStrength) >= Tun.AirOps.SeadThreat;

        /// <summary>Spec 178: a bomber goes on a valuable target (or an urgent one, or after its wait), on an acceptable route, with the blast clear of friends and the SEAD window open if needed.</summary>
        public static bool BomberGo(float value, bool urgent, bool waitedOut, float risk, bool blastClear, bool seadReady) =>
            (value >= Tun.AirOps.BomberMinValue || urgent || waitedOut) && risk <= Tun.AirOps.BomberRiskMax && blastClear && seadReady;

        public static bool OutsideCap(Vector2 zone, Vector2 at) => Vector2.Distance(zone, at) > Tun.AirOps.CapRadius * Tun.AirOps.CapLeash;

        /// <summary>Spec 176: a patrol point inside the zone that turns every <c>capPatrolS</c> (a fighter's own phase).</summary>
        public static Vector2 PatrolPoint(Vector2 zone, int fighterId, double now)
        {
            var turn = (int)Math.Floor(now / Math.Max(1.0, Tun.AirOps.CapPatrolS));
            var a = HumanStagger.Unit(fighterId, 7) * MathF.PI * 2f + turn * MathF.PI * 0.5f;
            return zone + new Vector2(MathF.Cos(a), MathF.Sin(a)) * Tun.AirOps.CapRadius * global::MachineBrigade.Sim.Content.SimTunables.Ai.AirRules.PatrolPointCapRadiusScale;
        }
    }

    /// <summary>Who owns a unit's orders now (one owner at a time; a higher priority takes over, equal ones wait for expiry).</summary>
    public enum IntentOwner : byte
    {
        None,
        Tactical,
        Squad,
        FireMission,
        Scoot,
        AirPackage,
        Emergency,
    }

    /// <summary>
    /// Intent ownership: one owner orders a unit at a time. A claim holds until its expiry; another owner of equal or lower
    /// priority cannot take the unit before then; a higher one (an emergency, a fire mission over the old artillery logic)
    /// takes it over. Deterministic (dictionary by id, no time-dependent ordering).
    /// </summary>
    public sealed class IntentOwnership
    {
        private readonly Dictionary<int, (IntentOwner owner, double until)> _claims = new();

        public static int Priority(IntentOwner o) => o switch
        {
            IntentOwner.Emergency => 3,
            IntentOwner.FireMission or IntentOwner.Scoot or IntentOwner.AirPackage => 2,
            IntentOwner.Tactical or IntentOwner.Squad => 1,
            _ => 0,
        };

        public IntentOwner Owner(int unit, double now) =>
            _claims.TryGetValue(unit, out var c) && c.until > now ? c.owner : IntentOwner.None;

        public bool HeldByOther(int unit, IntentOwner owner, double now)
        {
            var o = Owner(unit, now);
            return o != IntentOwner.None && o != owner;
        }

        /// <summary>Claims (or renews) the unit; false when another owner of at least the same priority holds it.</summary>
        public bool Claim(int unit, IntentOwner owner, double until, double now)
        {
            var o = Owner(unit, now);
            if (o != IntentOwner.None && o != owner && Priority(o) >= Priority(owner)) return false;
            _claims[unit] = (owner, until);
            return true;
        }

        public void Release(int unit, IntentOwner owner)
        {
            if (_claims.TryGetValue(unit, out var c) && c.owner == owner) _claims.Remove(unit);
        }

        public void Prune(double now)
        {
            if (_claims.Count < global::MachineBrigade.Sim.Content.SimTunables.Ai.IntentOwnership.PruneCountMax) return;
            var old = new List<int>();
            foreach (var kv in _claims)
                if (kv.Value.until <= now) old.Add(kv.Key);
            foreach (var k in old) _claims.Remove(k);
        }

        public int Count => _claims.Count;
    }
}
