#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 142: why a smoke screen is laid.</summary>
    public enum SmokePurpose : byte
    {
        Crossing,
        BreakLaserLos,
        CoverRepair,
        AssaultObjective,
        ScreenSquad,
    }

    /// <summary>Spec 141: what an anti-air vehicle covers.</summary>
    public enum CoverageKind : byte
    {
        BossCover,
        MainForceCover,
        ArtilleryCover,
        ObjectiveCover,
    }

    /// <summary>Spec 142: a smoke mission: area, start, end, purpose.</summary>
    public readonly struct SmokeMission
    {
        public SmokeMission(Vector2 area, float radius, double start, double end, SmokePurpose purpose)
        {
            Area = area;
            Radius = radius;
            Start = start;
            End = end;
            Purpose = purpose;
        }

        public Vector2 Area { get; }
        public float Radius { get; }
        public double Start { get; }
        public double End { get; }
        public SmokePurpose Purpose { get; }
    }

    /// <summary>
    /// AI MASTER P3 spec 138 / 221: what the side's units are about to do, so they coordinate instead of only reacting:
    /// target -> planned damage (139, with the in-flight damage of P0-A's overkill rule), target -> repair reserved (140),
    /// anti-air -> coverage assignment (141), area -> smoke missions (142), target -> fire-mission guns (143), objective ->
    /// committed power. Choke movement reservations are the TrafficCoordinator's (P1 passages), not repeated here.
    /// Reservations expire on their own (timeout) and are released when the shot or task changes.
    /// </summary>
    public sealed class PlannedActionBoard
    {
        private readonly Dictionary<int, List<(long shooter, float amount, double until)>> _damage = new();
        private readonly Dictionary<long, int> _shooterTarget = new();
        private readonly Dictionary<int, List<(int engineer, float amount, double until)>> _repair = new();
        private readonly Dictionary<int, int> _engineerTarget = new();
        private readonly Dictionary<int, (CoverageKind kind, Vector2 asset)> _coverage = new();
        private readonly List<SmokeMission> _smoke = new();
        private readonly Dictionary<int, (List<int> guns, double until)> _missions = new();
        private readonly Dictionary<long, float> _committed = new();

        private static long ShooterKey(EntityId shooter, int mount) => (long)shooter.Value * 16 + mount;

        // ------------------------------------------------------------------------------------------------ 139

        /// <summary>Spec 139: reserves <paramref name="amount"/> of damage from a shooter's mount on a target (one target per mount).</summary>
        public void ReserveDamage(EntityId target, EntityId shooter, int mount, float amount, double until)
        {
            ReleaseDamage(shooter, mount);
            if (!target.IsValid || amount <= 0f) return;
            var key = ShooterKey(shooter, mount);
            if (!_damage.TryGetValue(target.Value, out var list)) _damage[target.Value] = list = new List<(long, float, double)>();
            list.Add((key, amount, until));
            _shooterTarget[key] = target.Value;
        }

        /// <summary>Spec 139: the shot was cancelled, the target changed or became invalid.</summary>
        public void ReleaseDamage(EntityId shooter, int mount)
        {
            var key = ShooterKey(shooter, mount);
            if (!_shooterTarget.TryGetValue(key, out var target)) return;
            _shooterTarget.Remove(key);
            if (_damage.TryGetValue(target, out var list)) list.RemoveAll(r => r.shooter == key);
        }

        /// <summary>Planned damage on <paramref name="target"/> by every shooter but <paramref name="except"/> (still valid at <paramref name="now"/>).</summary>
        public float PlannedDamage(EntityId target, EntityId except, double now)
        {
            if (!_damage.TryGetValue(target.Value, out var list)) return 0f;
            var sum = 0f;
            foreach (var r in list)
                if (r.until > now && r.shooter / 16 != except.Value) sum += r.amount;
            return sum;
        }

        /// <summary>Spec 139 rule: planned + committed over the target's effective health x 1.15: a shooter that has not fired picks another.</summary>
        public static bool Overkill(float planned, float committed, float effectiveHp) =>
            planned + committed > MathF.Max(1f, effectiveHp) * Tun.Board.PlannedOverkillShare;

        // ------------------------------------------------------------------------------------------------ 140

        /// <summary>Spec 140: an engineer reserves repairing <paramref name="amount"/> on a target (one target per engineer).</summary>
        public void ReserveRepair(EntityId target, EntityId engineer, float amount, double until)
        {
            ReleaseRepair(engineer);
            var list = _repair.TryGetValue(target.Value, out var l) ? l : _repair[target.Value] = new List<(int, float, double)>();
            list.Add((engineer.Value, amount, until));
            _engineerTarget[engineer.Value] = target.Value;
        }

        public void ReleaseRepair(EntityId engineer)
        {
            if (!_engineerTarget.TryGetValue(engineer.Value, out var target)) return;
            _engineerTarget.Remove(engineer.Value);
            if (_repair.TryGetValue(target, out var list)) list.RemoveAll(r => r.engineer == engineer.Value);
        }

        /// <summary>Repair already reserved on a target by engineers other than <paramref name="except"/>.</summary>
        public float RepairReserved(EntityId target, EntityId except, double now)
        {
            if (!_repair.TryGetValue(target.Value, out var list)) return 0f;
            var sum = 0f;
            foreach (var r in list)
                if (r.until > now && r.engineer != except.Value) sum += r.amount;
            return sum;
        }

        /// <summary>Spec 140: assign another engineer only while the need is not covered.</summary>
        public static bool RepairDeficit(float need, float reserved) => need - reserved > 0.5f;

        // ------------------------------------------------------------------------------------------------ 141

        public void Cover(EntityId aa, CoverageKind kind, Vector2 asset) => _coverage[aa.Value] = (kind, asset);

        public void Uncover(EntityId aa) => _coverage.Remove(aa.Value);

        public bool CoverageOf(EntityId aa, out CoverageKind kind, out Vector2 asset)
        {
            if (_coverage.TryGetValue(aa.Value, out var c))
            {
                kind = c.kind;
                asset = c.asset;
                return true;
            }
            kind = default;
            asset = default;
            return false;
        }

        /// <summary>How many anti-air vehicles cover this kind of asset now.</summary>
        public int Covering(CoverageKind kind)
        {
            var n = 0;
            foreach (var c in _coverage.Values)
                if (c.kind == kind) n++;
            return n;
        }

        // ------------------------------------------------------------------------------------------------ 142

        public IReadOnlyList<SmokeMission> Smoke => _smoke;

        /// <summary>Spec 142: a running or planned smoke (or a cloud on the field) already covers <paramref name="p"/>.</summary>
        public bool SmokeCovered(Vector2 p, double now, IEnumerable<(Vector2 centre, float radius)>? clouds = null)
        {
            var spacing = Tun.Board.SmokeSpacing;
            foreach (var m in _smoke)
                if (m.End > now && Vector2.Distance(m.Area, p) <= m.Radius + spacing) return true;
            if (clouds != null)
                foreach (var (c, r) in clouds)
                    if (Vector2.Distance(c, p) <= r + spacing) return true;
            return false;
        }

        public void PlanSmoke(SmokeMission m)
        {
            if (_smoke.Count >= 16) _smoke.RemoveAt(0);
            _smoke.Add(m);
        }

        // ------------------------------------------------------------------------------------------------ 143

        /// <summary>Spec 143: guns on a fire mission at <paramref name="target"/> now.</summary>
        public int MissionGuns(int target, double now) => _missions.TryGetValue(target, out var m) && m.until > now ? m.guns.Count : 0;

        public bool OnMission(int target, EntityId gun, double now) => _missions.TryGetValue(target, out var m) && m.until > now && m.guns.Contains(gun.Value);

        public void AssignMission(int target, EntityId gun, double until)
        {
            if (!_missions.TryGetValue(target, out var m) || m.until <= until - 30.0) m = (new List<int>(), until);
            if (!m.guns.Contains(gun.Value)) m.guns.Add(gun.Value);
            _missions[target] = (m.guns, Math.Max(m.until, until));
        }

        // ------------------------------------------------------------------------------------------------ objectives

        public void SetCommitted(long objective, float power) => _committed[objective] = power;

        public float Committed(long objective) => _committed.TryGetValue(objective, out var p) ? p : 0f;

        internal void Prune(double now)
        {
            if (_damage.Count > 256)
            {
                var empty = new List<int>();
                foreach (var kv in _damage)
                {
                    kv.Value.RemoveAll(r => r.until <= now);
                    if (kv.Value.Count == 0) empty.Add(kv.Key);
                }
                foreach (var k in empty) _damage.Remove(k);
                if (_shooterTarget.Count > 2048) _shooterTarget.Clear();
            }
            _smoke.RemoveAll(m => m.End <= now);
            if (_missions.Count > 64)
            {
                var old = new List<int>();
                foreach (var kv in _missions)
                    if (kv.Value.until <= now) old.Add(kv.Key);
                foreach (var k in old) _missions.Remove(k);
            }
        }
    }
}
