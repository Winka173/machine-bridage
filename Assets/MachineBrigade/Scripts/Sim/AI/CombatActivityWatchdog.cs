#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>What the watchdog asks a side's tactical AI to do for one unit (Part C1 step 5 / 7, C2 recovery).</summary>
    public enum WatchdogRequestKind : byte
    {
        /// <summary>A local firing-position correction: drive a few metres to <see cref="WatchdogRequest.Point"/>.</summary>
        Sidestep,

        /// <summary>Unexplained idle with a reachable enemy in sight: attack-move to <see cref="WatchdogRequest.Point"/>.</summary>
        Push,
    }

    public readonly struct WatchdogRequest
    {
        public WatchdogRequest(EntityId unit, WatchdogRequestKind kind, Vector2 point)
        {
            Unit = unit;
            Kind = kind;
            Point = point;
        }

        public EntityId Unit { get; }
        public WatchdogRequestKind Kind { get; }
        public Vector2 Point { get; }
    }

    /// <summary>
    /// AI MASTER P0-A, Part C (mandatory): the combat activity watchdog, separate from the movement anti-stuck. Every armed
    /// unit is looked at <see cref="SimTunables.Ai.CombatWatchdog.EvaluateEveryTicks"/> steps apart (staggered by entity id,
    /// so the cost is spread), and carries the Part C record (last acquire / aim progress / fire / damage attempt, valid
    /// target, firing solution, weapon ready, blocked by arc / line / minimum range / friend / movement, explicit hold).
    /// <para>
    /// C1 COMBAT_ANOMALY: target + firing solution + ready weapon + no hold, yet no shot for the expected aim time plus
    /// <see cref="SimTunables.Ai.CombatWatchdog.AnomalyGraceSeconds"/>. Recovery: (1) validate the target, (2) recompute the
    /// mount's bearing (a hull-laid weapon turns its hull to it), (3) clear the stale aim state and look again at once,
    /// (4) recompute the line of fire, (5) a local firing-position correction (an AI unit's sidestep), (6) the second time,
    /// leave that target alone for a moment so another is taken, (7) escalate to the side's tactical AI, (8) log the cause.
    /// </para>
    /// <para>
    /// C2 no-idle-armed-unit invariant: an armed unit standing without firing has a reason code (<see cref="ReasonOf"/>);
    /// one with none (<see cref="CombatIdleReason.Unexplained"/>) for <see cref="SimTunables.Ai.CombatWatchdog.IdleReasonSeconds"/>
    /// is counted, logged and recovered (a fresh target look, and for an AI side a push at the enemy it can reach).
    /// </para>
    /// Deterministic: the world's vehicle order and clock, no randomness; the player's units are only diagnosed and have
    /// their aim state reset, never given orders.
    /// </summary>
    public sealed class CombatActivityWatchdog
    {
        /// <summary>Part C's per-unit record.</summary>
        public sealed class Record
        {
            public double LastTargetAcquireTime = double.NegativeInfinity;
            public double LastAimProgressTime = double.NegativeInfinity;
            public double LastFireTime = double.NegativeInfinity;
            public double LastDamageAttemptTime = double.NegativeInfinity;
            public bool HasValidTarget, HasFiringSolution, WeaponReady;
            public bool BlockedByArc, BlockedByLos, BlockedByMinRange, BlockedByFriendly, BlockedByMovementState;
            public CombatIdleReason ExplicitHoldReason;
            public double ExplicitUntil = double.NegativeInfinity;

            /// <summary>The reason code at the last look.</summary>
            public CombatIdleReason Reason { get; internal set; }

            /// <summary>Since when the unit has stood without firing (NaN: it is active).</summary>
            public double IdleSince { get; internal set; } = double.NaN;

            /// <summary>Since when the C1 anomaly condition has held (NaN: it does not).</summary>
            public double AnomalySince { get; internal set; } = double.NaN;

            /// <summary>Recoveries in a row without a shot in between.</summary>
            public int Recoveries { get; internal set; }

            internal EntityId LastTarget;
            internal float AimAtStart;
            internal float LastAimOff = float.NaN;
            internal CombatIdleReason Logged;
            internal EntityId LastDropped;
            internal EntityId LastBreach;
        }

        private readonly SimWorld _world;
        private readonly Dictionary<EntityId, Record> _records = new();
        private readonly HashSet<int> _aiTeams = new();
        private readonly SortedDictionary<int, WatchdogRequest> _requests = new();
        private readonly List<EntityId> _gone = new();

        public CombatActivityWatchdog(SimWorld world) => _world = world;

        /// <summary>C1 anomalies found and recovered, C2 unexplained idles found (the AI health measures and tests read them).</summary>
        public int Anomalies { get; private set; }
        public int Unexplained { get; private set; }
        public int Escalations { get; private set; }
        public int Dropped { get; private set; }

        /// <summary>P0 wiring: targets behind a breakable wall or gate turned into "breach first" (not dropped).</summary>
        public int Breaches { get; private set; }

        /// <summary>The unit's Part C record (null: not an armed unit, or not looked at yet).</summary>
        public Record? RecordOf(EntityId unit) => _records.TryGetValue(unit, out var r) ? r : null;

        /// <summary>The unit's reason code at the last look (<see cref="CombatIdleReason.Active"/> when unknown).</summary>
        public CombatIdleReason ReasonOf(EntityId unit) => _records.TryGetValue(unit, out var r) ? r.Reason : CombatIdleReason.Active;

        /// <summary>The unit's Part O code ("COMBAT_IDLE_RELOADING" ...).</summary>
        public string CodeOf(EntityId unit) => CombatReasons.Code(ReasonOf(unit));

        /// <summary>A side whose units the watchdog may give orders to (its tactical AI calls this every decision).</summary>
        public void MarkAiTeam(int team) => _aiTeams.Add(team);

        public bool IsAiTeam(int team) => _aiTeams.Contains(team);

        /// <summary>
        /// An AI layer's explicit reason for holding a unit (an objective hold, a formation wait, a fire mission it waits for),
        /// valid for <paramref name="seconds"/> (default <see cref="SimTunables.Ai.CombatWatchdog.ExplainSeconds"/>) unless renewed.
        /// </summary>
        public void Explain(EntityId unit, CombatIdleReason reason, float seconds = -1f)
        {
            if (!_records.TryGetValue(unit, out var r)) _records[unit] = r = new Record();
            r.ExplicitHoldReason = reason;
            r.ExplicitUntil = _world.Time + (seconds > 0f ? seconds : SimTunables.Ai.CombatWatchdog.ExplainSeconds);
        }

        /// <summary>The side's pending requests, in unit id order (the side's tactical AI takes them and acts).</summary>
        public void TakeRequests(int team, List<WatchdogRequest> into)
        {
            _gone.Clear();
            foreach (var kv in _requests)
                if (_world.TryGetVehicle(kv.Value.Unit, out var v) && v.Team == team)
                {
                    into.Add(kv.Value);
                    _gone.Add(kv.Value.Unit);
                }
                else if (!_world.TryGetVehicle(kv.Value.Unit, out _)) _gone.Add(kv.Value.Unit);
            foreach (var id in _gone) _requests.Remove(id.Value);
        }

        /// <summary>Spec 47: a unit dropped a target it cannot get a firing solution on (logged once per target).</summary>
        public void NoteDropped(Vehicle v, Vehicle target)
        {
            if (!_records.TryGetValue(v.Id, out var r)) _records[v.Id] = r = new Record();
            if (r.LastDropped == target.Id) return;
            r.LastDropped = target.Id;
            Dropped++;
            CombatReasons.Log(_world, v, DecisionKind.Target, CombatReasons.TargetUnreachableDropped, CombatReasons.Name(target.Id));
        }

        /// <summary>
        /// P0 wiring (Part B / H): a unit sent at a target behind a breakable wall or gate attacks the blocking structure first
        /// (logged once per structure).
        /// </summary>
        public void NoteBreach(Vehicle v, IDamageable target, IDamageable blocker)
        {
            if (!_records.TryGetValue(v.Id, out var r)) _records[v.Id] = r = new Record();
            if (r.LastBreach == blocker.Id) return;
            r.LastBreach = blocker.Id;
            Breaches++;
            CombatReasons.Log(_world, v, DecisionKind.Target, CombatReasons.TargetBreachFirst,
                CombatReasons.Name(blocker.Id) + " for " + CombatReasons.Name(target.Id));
        }

        // ------------------------------------------------------------------------------------------------ the step

        public void Step()
        {
            var every = Math.Max(1, SimTunables.Ai.CombatWatchdog.EvaluateEveryTicks);
            var tick = _world.Tick;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                if ((v.Id.Value + tick) % every != 0) continue;
                if (!Armed(v)) continue;
                Evaluate(v);
            }
            // Records of vehicles gone, now and then.
            if (tick % 200 == 0)
            {
                _gone.Clear();
                foreach (var id in _records.Keys)
                    if (!_world.TryGetVehicle(id, out var v) || !v.IsAlive) _gone.Add(id);
                foreach (var id in _gone) _records.Remove(id);
            }
        }

        /// <summary>A unit with a damaging weapon of its own (not a wall, minefield, range dummy or wingman's escort slot).</summary>
        private static bool Armed(Vehicle v) => !v.Def.Passive && !v.Dummy && !v.Def.Obstacle && v.Team >= 0;

        private void Evaluate(Vehicle v)
        {
            var now = _world.Time;
            if (!_records.TryGetValue(v.Id, out var r)) _records[v.Id] = r = new Record();
            if (v.LastFiredAt > r.LastFireTime)
            {
                r.LastFireTime = v.LastFiredAt;
                r.LastDamageAttemptTime = v.LastFiredAt;
                r.AnomalySince = double.NaN;
                r.Recoveries = 0;
            }
            if (v.Target != r.LastTarget)
            {
                r.LastTarget = v.Target;
                r.LastAimOff = float.NaN;
                if (v.Target.IsValid) r.LastTargetAcquireTime = now;
            }
            var main = CombatSystem.MainMount(v);
            var reason = Classify(v, main, r, out var check, out var enemy);
            r.Reason = reason;
            r.HasValidTarget = v.Target.IsValid;
            r.HasFiringSolution = check.HasSolution && (v.Target.IsValid || enemy != null);
            r.WeaponReady = check.Ready;
            r.BlockedByArc = reason == CombatIdleReason.BlockedByArc;
            r.BlockedByLos = reason == CombatIdleReason.BlockedByLos;
            r.BlockedByMinRange = reason == CombatIdleReason.WaitingMinRange;
            r.BlockedByFriendly = reason == CombatIdleReason.BlockedByFriend;
            r.BlockedByMovementState = reason == CombatIdleReason.Moving && v.Target.IsValid && !check.Ready;
            // Aim progress: the mount came closer to bearing on the target since the last look.
            if (v.Target.IsValid)
            {
                var off = check.AimSeconds;
                // (Laid on and still not firing is no progress: that is the anomaly itself.)
                if (float.IsNaN(r.LastAimOff) || off < r.LastAimOff - 1e-3f) r.LastAimProgressTime = now;
                r.LastAimOff = off;
            }

            var idle = reason is not (CombatIdleReason.Active or CombatIdleReason.Firing or CombatIdleReason.Moving);
            if (!idle) r.IdleSince = double.NaN;
            else if (double.IsNaN(r.IdleSince)) r.IdleSince = now;

            // C1: the anomaly and its recovery.
            // The window is the aim time expected when it began plus the grace, and the mount must have stopped closing on the
            // target for the grace as well (a slow turret still slewing round is not stalled).
            if (reason == CombatIdleReason.StaleAim)
            {
                var grace = SimTunables.Ai.CombatWatchdog.AnomalyGraceSeconds;
                if (double.IsNaN(r.AnomalySince))
                {
                    r.AnomalySince = now;
                    r.AimAtStart = check.AimSeconds;
                }
                else if (now - r.AnomalySince >= r.AimAtStart + grace && now - r.LastAimProgressTime >= grace)
                    RecoverAnomaly(v, main, r, check, enemy);
            }
            else r.AnomalySince = double.NaN;

            if (!idle || now - r.IdleSince < SimTunables.Ai.CombatWatchdog.IdleReasonSeconds) return;
            // C2: no reason is a state-machine bug: count it, log it, recover it.
            if (reason == CombatIdleReason.Unexplained)
            {
                RecoverUnexplained(v, r, enemy);
                return;
            }
            // A friend in the line for a while: an AI unit steps aside (Part R1 / R6) rather than idling behind it.
            // AI MASTER P2 Part E: the E2 ladder (wait, sidestep, equivalent slot, another target, the idle blocker steps aside).
            if (reason == CombatIdleReason.BlockedByFriend && CanOrder(v) && _world.TryGetTarget(v.Target, out var aimed))
            {
                switch (_world.FiringLanes.Resolve(v, aimed.Position, out var point, out var blocker))
                {
                    case LaneResolution.Sidestep:
                    case LaneResolution.AlternateSlot:
                        Request(v, WatchdogRequestKind.Sidestep, point);
                        break;
                    case LaneResolution.Retarget:
                        _world.Combat.ResetAim(v, true, now + SimTunables.Ai.CombatWatchdog.SuppressSeconds);
                        break;
                    case LaneResolution.MoveBlocker:
                        if (blocker != null && CanOrder(blocker)) Request(blocker, WatchdogRequestKind.Sidestep, point);
                        break;
                    case LaneResolution.None:
                        Request(v, WatchdogRequestKind.Sidestep, SidestepPoint(v, aimed.Position, r.Recoveries));
                        break;
                }
                r.IdleSince = now;
            }
            if (reason != r.Logged && Notable(reason))
            {
                r.Logged = reason;
                CombatReasons.Log(_world, v, DecisionKind.State, CombatReasons.Code(reason));
            }
        }

        /// <summary>Reasons worth a log line when they last (the routine ones are read off <see cref="ReasonOf"/>).</summary>
        private static bool Notable(CombatIdleReason reason) => reason is CombatIdleReason.NoReachableTarget or CombatIdleReason.WaitingMinRange or
            CombatIdleReason.BlockedByFriend or CombatIdleReason.BlockedByLos or CombatIdleReason.BlockedByArc or CombatIdleReason.DisabledMainWeapon;

        // ------------------------------------------------------------------------------------------------ classifying

        /// <summary>Part C2: the reason this unit is not shooting (or that it is active).</summary>
        private CombatIdleReason Classify(Vehicle v, int main, Record r, out FiringCheck check, out Vehicle? enemy)
        {
            check = default;
            enemy = null;
            var now = _world.Time;
            if (v.Stunned || v.Lowered || v.Burrowed || v.Tier == AltitudeTier.Orbit) return CombatIdleReason.Disabled;
            if (!AnyWorkingWeapon(v)) return CombatIdleReason.DisabledMainWeapon;
            if (v.DeployBusy) return CombatIdleReason.Deploying;
            var state = v.Weapons[main];
            var weapon = v.Arms[main];
            if (now - v.LastFiredAt < MathF.Max(SimTunables.Ai.CombatWatchdog.FiredRecentlySeconds, weapon.Cooldown + 0.5f)) return CombatIdleReason.Firing;
            if (v.HoldFire) return CombatIdleReason.HoldFireOrder;
            if (v.AiHoldFire) return CombatIdleReason.HoldFireAmbush;
            // A mount the boss system lays and fires (lane P0-C's).
            if (weapon.Laid || !v.MountWorks(main)) return v.Def.Boss ? CombatIdleReason.BossControlled : CombatIdleReason.DisabledMainWeapon;
            if (v.IsMoving || v.HasPath || v.PathQueued || v.Relocating) return CombatIdleReason.Moving;
            if (state.ReloadLeft > 0f || state.BurstLeft > 0) return CombatIdleReason.Reloading;
            if (state.Ammo == 0) return state.Load > 0 ? CombatIdleReason.WaitingResupply : CombatIdleReason.Reloading;
            if (state.ChargeLeft > 0f) return CombatIdleReason.Aiming;
            var hold = r.ExplicitUntil > now ? r.ExplicitHoldReason : CombatIdleReason.Active;
            var combat = _world.Combat;

            if (_world.TryGetTarget(v.Target, out var target) && target.IsAlive)
            {
                check = combat.Check(v, main, target);
                switch (check.Reject)
                {
                    case TargetReject.None:
                        if (check.FriendInLine) return CombatIdleReason.BlockedByFriend;
                        if (!check.Ready) return CombatIdleReason.Reloading;
                        // Target, solution, a ready weapon and no hold: it should be firing (C1).
                        return CombatIdleReason.StaleAim;
                    case TargetReject.MinRange:
                        return CombatIdleReason.WaitingMinRange;
                    case TargetReject.NoLineOfFire:
                        return CombatIdleReason.BlockedByLos;
                    case TargetReject.OutsideArc:
                    case TargetReject.AimTooLong:
                        return CombatIdleReason.BlockedByArc;
                    case TargetReject.OutOfReach:
                        if (hold != CombatIdleReason.Active) return hold;
                        return target is Vehicle tv && !_world.TargetAccess.CanInfluence(v, tv.Position, tv.Flying, tv.Radius)
                            ? CombatIdleReason.NoReachableTarget
                            : OutOfReach(v, target is Vehicle ov ? ov : null, weapon);
                    default:
                        return hold != CombatIdleReason.Active ? hold : CombatIdleReason.NoValidWeaponTarget;
                }
            }

            enemy = combat.NearestEngageable(v, main, out var why);
            if (enemy == null) return hold != CombatIdleReason.Active ? hold : CombatIdleReason.NoValidWeaponTarget;
            check = combat.Check(v, main, enemy);
            switch (why)
            {
                case TargetReject.None:
                    // A solution on something the weapon cannot hurt is no target at all.
                    if (_world.Damage.Estimate(weapon, v, enemy) <= 0f) return hold != CombatIdleReason.Active ? hold : CombatIdleReason.NoValidWeaponTarget;
                    if (check.FriendInLine) return CombatIdleReason.BlockedByFriend;
                    if (!check.Ready) return CombatIdleReason.Reloading;
                    return CombatIdleReason.StaleAim;
                case TargetReject.MinRange:
                    return CombatIdleReason.WaitingMinRange;
                case TargetReject.NoLineOfFire:
                    return hold != CombatIdleReason.Active ? hold : CombatIdleReason.BlockedByLos;
                case TargetReject.OutsideArc:
                case TargetReject.AimTooLong:
                    return hold != CombatIdleReason.Active ? hold : CombatIdleReason.BlockedByArc;
                default:
                    if (hold != CombatIdleReason.Active) return hold;
                    if (!_world.TargetAccess.CanInfluence(v, enemy.Position, enemy.Flying, enemy.Radius)) return CombatIdleReason.NoReachableTarget;
                    return OutOfReach(v, enemy, weapon);
            }
        }

        /// <summary>The enemy in sight is out of reach but reachable: why the unit may still stand, or Unexplained.</summary>
        private CombatIdleReason OutOfReach(Vehicle v, Vehicle? enemy, WeaponDef weapon)
        {
            if (v.Def.Static || v.Def.Speed <= 0f || v.Deploy == DeployState.Deployed) return CombatIdleReason.NoReachableTarget;
            // A ground unit never drives after an aircraft unless it is anti-aircraft (MovementSystem.HuntsAircraft).
            if (enemy != null && enemy.Flying && !v.Flying && !CombatSystem.IsAntiAir(v.Def.Weapon)) return CombatIdleReason.NoReachableTarget;
            if (weapon.MinRange > 0f) return CombatIdleReason.WaitingFireMission;
            // A role with no engagement band (the sheet's recon, artillery, support rows) stands off by design.
            if (_world.Catalog.AiData.RoleOf(v.Def.Id) is { EngageMax: <= 0f }) return weapon.Indirect ? CombatIdleReason.WaitingFireMission : CombatIdleReason.Spotting;
            if (!CanOrder(v) || v.PostRadius > 0f) return CombatIdleReason.GuardPost;
            var profile = _world.AiProfile;
            if (profile.NoChase || _world.DefenderTeam == v.Team) return CombatIdleReason.ObjectiveHold;
            // Seen by the side but beyond the unit's own sight: the commander's to send it, not a local stall.
            if (enemy != null && Vector2.Distance(v.Position, enemy.Position) > v.Def.VisionRange) return CombatIdleReason.NoValidWeaponTarget;
            return CombatIdleReason.Unexplained;
        }

        private static bool AnyWorkingWeapon(Vehicle v)
        {
            for (var i = 0; i < v.Arms.Length; i++)
                if (v.Arms[i].Damage > 0f && v.MountWorks(i)) return true;
            return false;
        }

        /// <summary>The watchdog may ask the side's AI to move this unit (an AI side, not the player's hand on it).</summary>
        private bool CanOrder(Vehicle v) => _aiTeams.Contains(v.Team) && !v.UnderPlayerControl(_world.Time) && !v.Def.Static && v.Def.Speed > 0f;

        // ------------------------------------------------------------------------------------------------ recovering

        private void RecoverAnomaly(Vehicle v, int main, Record r, FiringCheck check, Vehicle? enemy)
        {
            var now = _world.Time;
            Anomalies++;
            r.Recoveries++;
            r.AnomalySince = now;
            r.AimAtStart = 0f;
            var aimedAt = _world.TryGetTarget(v.Target, out var t) ? t : enemy;
            // (1) validate the target, (3) clear the stale aim state, (6) the second time: leave this target for a moment.
            _world.Combat.ResetAim(v, r.Recoveries >= 2, now + SimTunables.Ai.CombatWatchdog.SuppressSeconds);
            // (2) recompute the bearing: a hull-laid weapon (or a traverse-limited turret) turns the hull to the target.
            var mount = v.Def.Mounts[main];
            if (aimedAt != null && !v.Flying && !v.Def.Static && (mount.Aim == MountAim.Hull || v.Def.TurretArc > 0f))
                v.FaceHeading = SimMath.HeadingOf(aimedAt.Position - v.Position);
            CombatReasons.Log(_world, v, DecisionKind.Emergency, CombatReasons.WatchdogCombatAnomaly,
                $"{CombatReasons.Code(CombatIdleReason.StaleAim)} target {(aimedAt != null ? CombatReasons.Name(aimedAt.Id) : "-")} aim {check.AimSeconds:0.0}s ready {check.Ready} try {r.Recoveries}");
            // (4)-(5), (7): the second time running, an AI unit corrects its firing position and the side's AI is told.
            if (r.Recoveries >= 2 && aimedAt != null && CanOrder(v))
            {
                Escalations++;
                Request(v, WatchdogRequestKind.Sidestep, SidestepPoint(v, aimedAt.Position, r.Recoveries));
                CombatReasons.Log(_world, v, DecisionKind.Emergency, CombatReasons.WatchdogRecoveryEscalated, "sidestep");
            }
        }

        private void RecoverUnexplained(Vehicle v, Record r, Vehicle? enemy)
        {
            Unexplained++;
            r.IdleSince = _world.Time;
            _world.Combat.ResetAim(v, false, 0.0);
            CombatReasons.Log(_world, v, DecisionKind.Emergency, CombatReasons.WatchdogIdleUnexplained,
                enemy != null ? "enemy " + CombatReasons.Name(enemy.Id) : "");
            if (enemy != null && CanOrder(v))
            {
                Escalations++;
                Request(v, WatchdogRequestKind.Push, enemy.Position);
            }
        }

        private void Request(Vehicle v, WatchdogRequestKind kind, Vector2 point) => _requests[v.Id.Value] = new WatchdogRequest(v.Id, kind, point);

        /// <summary>
        /// C1 step 5: a few metres square to the line to the target, the side set by the entity id and the attempt (no
        /// randomness), the other side when that ground is closed, else a step back.
        /// </summary>
        private Vector2 SidestepPoint(Vehicle v, Vector2 target, int attempt)
        {
            var to = target - v.Position;
            var dir = to.LengthSquared() > 1e-4f ? Vector2.Normalize(to) : SimMath.Forward(v.Heading);
            var side = new Vector2(dir.Y, -dir.X);
            var metres = SimTunables.Ai.CombatWatchdog.SidestepMetres;
            var first = ((v.Id.Value + attempt) & 1) == 0 ? 1f : -1f;
            var grid = _world.Grid;
            var a = v.Position + side * first * metres;
            if (grid.IsWalkable(a)) return a;
            var b = v.Position - side * first * metres;
            if (grid.IsWalkable(b)) return b;
            return v.Position - dir * metres;
        }
    }
}
