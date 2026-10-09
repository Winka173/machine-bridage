#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Bosses.BossBrain;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// AI MASTER P0-C (spec 48 "BossWeaponDirector", 202-203, Part E3/F5): the boss's weapons as a whole.
    /// <list type="bullet">
    /// <item>Mount samples (arc, side, DPS, reach, layers) of its working mounts only: a broken part's mounts drop out, so the
    /// broadside recomputes when a battery is lost (Part F5, regression R5).</item>
    /// <item>Active-DPS bearing (spec 202): the share of the DPS with something in reach that bears now
    /// (<see cref="BossBrain.ActiveDpsFraction"/>); the naval broadside keeps it near 0.65 when the route allows.</item>
    /// <item>Each mount's own target (section 96 "TurretTargets[]"): CombatSystem picks them mount by mount; one blocked
    /// turret never stops the others (Part E3).</item>
    /// <item>Fire cadence (spec 203): two different heavy weapons (main gun, rockets, missiles, secondary: not machine guns,
    /// streams, point defence or AA) do not open fire in the same instant: the second waits the cadence gap (0.35 s, never
    /// more than a sixth of a cycle shared by the heavy mounts, so the long-run rate is kept). A salvo the data fires together
    /// (simultaneous barrels, a twin pair, the naval salvo and the big attacks, which are the boss systems') stays together.</item>
    /// </list>
    /// </summary>
    internal static class BossWeaponDirector
    {
        /// <summary>The working mounts of <paramref name="v"/> as the broadside controller sees them.</summary>
        internal static void Samples(Vehicle v, List<MountSample> into)
        {
            into.Clear();
            var mounts = v.Def.Mounts;
            for (var i = 0; i < mounts.Count && i < v.Arms.Length; i++)
            {
                if (!v.MountWorks(i)) continue;
                var w = v.Arms[i];
                if (w.Damage <= 0f || w.InterceptOnly) continue;
                var m = mounts[i];
                into.Add(new MountSample(m.Aim, m.ArcCentre, m.ArcHalf, w.SustainedDps, w.MinRange, w.Range, w.CanTarget(true), w.CanTarget(false)));
            }
        }

        /// <summary>The enemies its side can see within its longest reach (+ a margin), nearest first (at most 16; deterministic).</summary>
        internal static void Targets(SimWorld world, Vehicle v, List<MountSample> mounts, List<TargetSample> into, List<(float d, int id, TargetSample t)> scratch)
        {
            into.Clear();
            scratch.Clear();
            var reach = 0f;
            foreach (var m in mounts) reach = MathF.Max(reach, m.Range);
            if (reach <= 0f) return;
            reach += global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossWeaponDirector.TargetsReach;
            foreach (var e in world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Invulnerable || !e.IsVisibleTo(v.Team)) continue;
                var d = Vector2.Distance(e.Position, v.Position);
                if (d > reach + e.Radius) continue;
                scratch.Add((d, e.Id.Value, new TargetSample(e.Position, e.Radius, e.Flying)));
            }
            scratch.Sort((a, b) => a.d != b.d ? a.d.CompareTo(b.d) : a.id.CompareTo(b.id));
            for (var i = 0; i < scratch.Count && i < global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossWeaponDirector.TargetsIMax; i++) into.Add(scratch[i].t);
        }

        /// <summary>Section 96: the main mount's target and every mount's.</summary>
        internal static void NoteTargets(Vehicle v, BossBrain b)
        {
            b.TargetId = v.Target;
            b._turretTargets.Clear();
            for (var i = 0; i < v.Weapons.Length; i++) b._turretTargets.Add(i == 0 ? v.Target : v.Weapons[i].Target);
        }

        // ================================================================== fire groups (boss design 09/10, sheet 12)

        internal enum FireGroup : byte { Main, Secondary, Ciws, Suppress }

        /// <summary>The group of mount <paramref name="i"/>: the data's "group", else sorted by what its weapon is.</summary>
        internal static FireGroup GroupOf(Vehicle v, int i)
        {
            var m = v.Def.Mounts[i];
            switch (m.GroupName)
            {
                case "main": return FireGroup.Main;
                case "secondary": return FireGroup.Secondary;
                case "ciws": return FireGroup.Ciws;
                case "suppress": return FireGroup.Suppress;
            }
            var w = v.Arms[i];
            // Air defence: it cannot hit the ground at all, or it is a light quick gun that can reach the air (a CIWS, a flak mount).
            if (w.InterceptOnly || !w.CanTarget(false)) return FireGroup.Ciws;
            if (w.CanTarget(true) && w.Damage < 120f && w.Cooldown < 1.5f) return FireGroup.Ciws;
            if (w.Cooldown >= 2.5f && w.Damage >= 250f) return FireGroup.Main;
            if (w.Cooldown < 1f || w.Clip > 0) return FireGroup.Suppress;
            return FireGroup.Secondary;
        }

        /// <summary>A heavy blast weapon: a bomb stick or a big shell, the ones that must not stack.</summary>
        internal static bool HeavyAoe(WeaponDef w, FireGroupRules rules) =>
            w.Damage > 0f && !w.InterceptOnly && w.CanTarget(false) && (w.LaysStick || (w.SplashRadius >= rules.HeavyAoeRadius && w.Damage >= 250f));

        private static EntityId TargetOf(Vehicle v, int i) => i == 0 ? v.Target : v.Weapons[i].Target;

        /// <summary>
        /// Whether mount <paramref name="index"/> may open fire now: no other group mount opened within its own stagger gap, fewer than
        /// the group's cap of mounts on its target, and, for a heavy blast, no other heavy blast of the boss within the shared gap
        /// nor its big attack under way.
        /// </summary>
        internal static bool GroupAllows(Vehicle v, int index, double now, FireGroupRules rules)
        {
            var w = v.Arms[index];
            if (HeavyAoe(w, rules))
            {
                if (v.BigAttack is { Stage: not BigStage.Ready }) return false;
                for (var j = 0; j < v.Arms.Length; j++)
                    if (j != index && HeavyAoe(v.Arms[j], rules) && now - v.Weapons[j].OpenedAt < rules.HeavyAoeGap) return false;
            }
            var g = GroupOf(v, index);
            var rule = g switch { FireGroup.Main => rules.Main, FireGroup.Secondary => rules.Secondary, FireGroup.Suppress => rules.Suppress, _ => rules.Ciws };
            if (rule.Free) return true;
            var gap = rule.GapLo + (rule.GapHi - rule.GapLo) * (index * 0.618034f % 1f);
            var target = TargetOf(v, index);
            var active = 0;
            for (var j = 0; j < v.Arms.Length; j++)
            {
                if (j == index || GroupOf(v, j) != g) continue;
                var s = v.Weapons[j];
                if (now - s.OpenedAt < gap) return false;
                if (target.IsValid && TargetOf(v, j) == target && now - s.FiredAt < rule.Window) active++;
            }
            return active < rule.MaxAtTarget;
        }

        // ================================================================== cadence (spec 203)

        /// <summary>A heavy weapon for the cadence director: slow, not a stream, not a machine gun, able to hit the ground.</summary>
        internal static bool Heavy(WeaponDef w) =>
            w.Cooldown >= Tun.CadenceHeavyCooldown && w.Clip <= 0 && w.CanTarget(false) && !w.InterceptOnly && w.Damage > 0f;

        /// <summary>
        /// Spec 203: whether mount <paramref name="index"/> of a boss may open fire now: no other heavy weapon of a different
        /// kind opened fire within the gap. True for everything else (and for any vehicle without a brain).
        /// </summary>
        internal static bool CadenceAllows(Vehicle v, int index, double now, FireGroupRules? groups = null)
        {
            if (v.Brain == null || index < 0 || index >= v.Arms.Length) return true;
            // Boss design 09/10: fire groups and the shared heavy-blast gap (a boss with many mounts only).
            if (groups != null && v.Arms.Length >= groups.MinMounts && !GroupAllows(v, index, now, groups)) return false;
            var w = v.Arms[index];
            if (!Heavy(w) || w.Simultaneous) return true;
            var heavy = 0;
            for (var j = 0; j < v.Arms.Length; j++)
                if (Heavy(v.Arms[j])) heavy++;
            if (heavy < global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossWeaponDirector.CadenceAllowsHeavyMax) return true;
            var gap = MathF.Min(Tun.CadenceGap, w.Cooldown / (global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossWeaponDirector.CadenceAllowsHeavyScale * heavy));
            for (var j = 0; j < v.Arms.Length; j++)
            {
                if (j == index || !Heavy(v.Arms[j])) continue;
                // A twin pair keeps its own offset (CombatSystem.TwinOffset); the same weapon is one battery.
                if (v.Arms[j].Id == w.Id) continue;
                if (now - v.Weapons[j].FiredAt < gap) return false;
            }
            return true;
        }
    }

    /// <summary>
    /// AI MASTER P0-C (spec 65): the boss's target worth on top of its behaviour types (prompt 28 F.2, CombatSystem.BossWorth):
    /// ThreatToBossPart, ThreatToEscort, ThreatToMission, CanWeaponBear, TimeToAim and TargetPersistence (overkill is the
    /// combat lane's planned-damage rule, P0-A). The hull is never turned for a target: a mount that cannot bear now makes its
    /// target worth less, so the turrets pick what they can shoot instead of asking the hull to come round.
    /// </summary>
    internal static class BossTargetDirector
    {
        internal static float Worth(SimWorld world, Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (v.Brain is not { } b) return 1f;
            var worth = 1f;
            // ThreatToBossPart: it is shooting at the boss (and reaches it).
            if (other.Target == v.Id && Vector2.Distance(other.Position, v.Position) - v.Radius <= other.Def.Weapon.Range) worth *= global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthWorth;
            // ThreatToEscort: it is shooting at one of the boss's escorts.
            if (other.Target.IsValid && world.TryGetVehicle(other.Target, out var victim) && victim.EscortOf == v.Id) worth *= 1.15f;
            // ThreatToMission: it stands on the boss's way (near its anchor).
            if (b.AnchorKind != MissionAnchorKind.None && Vector2.Distance(other.Position, b.Anchor) < global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthDistanceMax) worth *= global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthWorth2;
            // CanWeaponBear / TimeToAim: the mounts carrying this weapon, now, as the hull lies.
            var bears = false;
            var aim = float.MaxValue;
            var mounts = v.Def.Mounts;
            for (var i = 0; i < mounts.Count && i < v.Arms.Length; i++)
            {
                if (!ReferenceEquals(v.Arms[i], weapon) && v.Arms[i].Id != weapon.Id) continue;
                if (!v.MountWorks(i)) continue;
                var m = mounts[i];
                var sample = new MountSample(m.Aim, m.ArcCentre, m.ArcHalf, 1f, 0f, float.MaxValue, true, true);
                if (!NavalBossMovementController.CanBear(sample, v.Position, v.Heading, other.Position)) continue;
                bears = true;
                var rate = m.Aim == MountAim.Turret ? MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthTurretTurnRateFloor, v.Def.TurretTurnRate) : SimMath.DegToRad(global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthDegrees);
                var off = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(other.Position - v.Position) - v.MountHeading(i)));
                aim = MathF.Min(aim, off / rate);
            }
            if (!bears) worth *= 0.6f;
            else worth /= 1f + global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthMinScale * MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthAimCap, aim);
            // TargetPersistence: what it is already shooting.
            if (other.Id == v.Target) worth *= 1.15f;
            return Math.Clamp(worth, global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthWorthMin, global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossTargetDirector.WorthWorthMax);
        }
    }

    /// <summary>
    /// AI MASTER P0-C (spec 66): the escorts' rings round the boss. Nobody's station is inside the boss's radius + 4 m; the
    /// screen (guards, raiders: "screen", "strike") keeps the ring + 10-18 m, the support (anti-air cover, jammers, spotters,
    /// smoke: "AA", "EW", "spot") + 18-30 m, a further rank further out; closing in after a new phase (prompt 28 F.5) takes
    /// the ring's inner edge instead of half the distance. A repairer stays on the screen ring's inner edge, inside its repair
    /// reach (escortRules.repairReach: the support ring would end its repairs).
    /// </summary>
    internal static class BossEscortCoordinator
    {
        internal static bool Support(EscortRole role) => role is EscortRole.Cover or EscortRole.Jam or EscortRole.Spot or EscortRole.Smoke;

        /// <summary>The distance of a station from the boss's middle (<paramref name="bossRadius"/>: its bound).</summary>
        internal static float Ring(EscortRole role, int rank, float bossRadius, bool close, float repairReach)
        {
            var t = close ? 0f : SimMath.Clamp01(rank / global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossEscortCoordinator.RingRankDivisor);
            float extra;
            if (role == EscortRole.Repair) extra = MathF.Min(Tun.EscortScreenMin, MathF.Max(Tun.EscortInnerGap + 1f, repairReach - global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossEscortCoordinator.RingRepairReachSub));
            else if (Support(role)) extra = Tun.EscortSupportMin + (Tun.EscortSupportMax - Tun.EscortSupportMin) * t;
            else extra = Tun.EscortScreenMin + (Tun.EscortScreenMax - Tun.EscortScreenMin) * t;
            return bossRadius + MathF.Max(Tun.EscortInnerGap + 1f, extra);
        }

        /// <summary>The forbidden ring: no station closer to the boss's middle than this.</summary>
        internal static float Inner(float bossRadius) => bossRadius + Tun.EscortInnerGap;
    }
}
