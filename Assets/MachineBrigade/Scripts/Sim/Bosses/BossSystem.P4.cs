#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// AI MASTER P4 (lane A), the boss side of the advanced planning: the weakpoint utility an AI side's shooters aim by
    /// (spec 179: silenced DPS share, APS / shield / radar parts, phase utility, kill progress; the parts' functions are game
    /// rules, not hidden intel) and the boss pressure budget (spec 204: a non-critical big attack waits a moment while the
    /// side already has dangerous actions active; the wait comes off the next cooldown, so the damage is unchanged; a
    /// scripted boss never waits, spec 226).
    /// </summary>
    internal sealed partial class BossSystem
    {
        private readonly List<(int team, Vector2 point, float radius, double lands)> _p4Strikes = new();

        /// <summary>The shooter's side has an AI planning layer (players keep the old part choice).</summary>
        internal bool WeakpointsForP4(Vehicle shooter) =>
            Tun.Planning.Enabled && Tun.Coordination.Enabled && _world.CoordinationIfAny?.Peek(shooter.Team)?.PlanningIfAny != null;

        /// <summary>Spec 179 for part <paramref name="i"/> (plus a quarter of the old shooter-specific danger, so anti-air still hunts the anti-air parts).</summary>
        internal float WeakpointP4(Vehicle shooter, Vehicle boss, int i, float distance) => WeakpointBase(boss, i, distance) + Danger(shooter, boss, i) * global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.WeakpointP4DangerScale;

        private float WeakpointBase(Vehicle boss, int i, float distance)
        {
            var part = boss.Def.Parts[i];
            float total = 0f, mine = 0f;
            for (var k = 0; k < boss.Arms.Length; k++)
                if (boss.Arms[k].Damage > 0f) total += Firepower(boss.Arms[k]);
            foreach (var m in part.Mounts)
                if (m >= 0 && m < boss.Arms.Length && boss.Arms[m].Damage > 0f) mine += Firepower(boss.Arms[m]);
            var utilityPart = WeakpointUtility.IsUtilityKind(part.Kind);
            foreach (var skill in part.Skills)
                if (WeakpointUtility.IsUtilityKind(skill)) utilityPart = true;
            var phase = 0f;
            if (boss.BigAttack is { } big && big.Def.UsesPart(part.Id)) phase = big.Stage == BigStage.Charging ? 1f : 0.3f;
            else if (boss.Def.PartLock is { } lockDef && lockDef.Kind == part.Kind) phase = 0.6f;
            else if (part.Skills.Count > 0) phase = global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.WeakpointBasePhase2;
            return WeakpointUtility.Score(total > 0f ? mine / total : 0f, utilityPart, phase, boss.PartShare(i), distance);
        }

        /// <summary>The part with the best utility for a side (for the commander's log), -1 when none is left.</summary>
        internal int BestWeakpointP4(Vehicle boss, out float score)
        {
            score = float.MinValue;
            var best = -1;
            for (var i = 0; i < boss.PartCount; i++)
            {
                if (boss.IsPartBroken(i)) continue;
                var s = WeakpointBase(boss, i, 0f);
                if (s > score + 1e-4f)
                {
                    score = s;
                    best = i;
                }
            }
            return best;
        }

        /// <summary>Spec 204: dangerous actions of the boss's side active now (other big attacks charging, its strikes on the way).</summary>
        private int DangerousActiveP4(Vehicle boss, double now)
        {
            var n = 0;
            foreach (var v in _world.VehicleList)
                if (v != boss && v.IsAlive && v.Team == boss.Team && v.BigAttack is { Stage: BigStage.Charging }) n++;
            _p4Strikes.Clear();
            _world.Strikes.Incoming(_p4Strikes);
            foreach (var s in _p4Strikes)
                if (s.team == boss.Team && s.lands >= now) n++;
            return n;
        }

        private bool PressureDeferP4(Vehicle v, BigAttackState s, double now)
        {
            if (!Tun.Planning.Enabled)
            {
                s.P4Deferred = 0f;
                return false;
            }
            var critical = v.Scripted;
            var active = DangerousActiveP4(v, now);
            if (!PressureBudget.Defer(active, critical, s.P4Deferred)) return false;
            var wait = PressureBudget.Wait(s.P4Deferred);
            if (wait <= 0f) return false;
            s.P4Deferred += wait;
            s.Next = now + wait;
            _world.AiLog.Add(new DecisionEntry(now, v.Team, AiLayer.Unit, v.Id.Value, DecisionKind.Action,
                $"{P4Reasons.PressureDefer} {s.Def.Id} {active} active: +{wait:0.0} s"));
            return true;
        }

        /// <summary>The next cast time after a start: the wait it had comes off the cooldown (never under the warning + 1 s).</summary>
        private double PressureNextP4(BigAttackState s, double now, float warn)
        {
            var deferred = s.P4Deferred;
            s.P4Deferred = 0f;
            if (deferred <= 0f) return s.Next;
            return now + PressureBudget.NextCooldown((float)(s.Next - now), deferred, warn + 1f);
        }
    }
}
