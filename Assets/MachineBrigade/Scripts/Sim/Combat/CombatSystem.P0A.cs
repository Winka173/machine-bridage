#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>What the watchdog needs to know about one weapon and one target (AI MASTER P0-A, Part C).</summary>
    internal readonly struct FiringCheck
    {
        public FiringCheck(TargetReject reject, bool ready, bool friendInLine, float aimSeconds, bool aimed)
        {
            Reject = reject;
            Ready = ready;
            FriendInLine = friendInLine;
            AimSeconds = aimSeconds;
            Aimed = aimed;
        }

        /// <summary>The hard feasibility result (None: the weapon has a firing solution).</summary>
        public TargetReject Reject { get; }

        /// <summary>The weapon could fire now: cooled down, loaded, its mount working, not mid-reload.</summary>
        public bool Ready { get; }

        /// <summary>A friendly hull stands in the direct line of fire (Part E, G.4).</summary>
        public bool FriendInLine { get; }

        /// <summary>Seconds to bring the mount onto the target from where it points now (spec 89).</summary>
        public float AimSeconds { get; }

        /// <summary>The mount points at the target within its firing tolerance.</summary>
        public bool Aimed { get; }

        public bool HasSolution => Reject == TargetReject.None;
    }

    /// <summary>
    /// AI MASTER P0-A (lane A, DECISIONS "AI MASTER P0-A"): the master spec's targeting rules on top of the existing target
    /// score, which stays the B1 product it already was (weapon effect x finishing x worth x threat x focus x distance x the
    /// prompt-17/25/26/28 worths). Added here:
    /// <list type="bullet">
    /// <item>spec 42/105 hard feasibility before scoring (<see cref="Feasibility"/>): the old checks plus the mount's bearing
    /// (a traverse-limited turret or a fixed hull that cannot turn: no solution) and the aim time;</item>
    /// <item>spec 44/106 overkill control 1.15 with its exceptions (boss part focus, Executioner, a forced order, an extremely
    /// dangerous target);</item>
    /// <item>spec 45 stickiness +15 % for 1.5 s after acquiring;</item>
    /// <item>spec 46 + Part H ThreatToObjective, mode-aware (capture, convoy, defended walls, the siege breach);</item>
    /// <item>spec 88/89 the firing arc and AimPenalty = exp(-AimSeconds / 4);</item>
    /// <item>Part B B2 breacher and B3 siege doctrine rows (R2, R3).</item>
    /// </list>
    /// Deterministic: sim state and clock only.
    /// </summary>
    internal sealed partial class CombatSystem
    {
        private static float StickSeconds => SimTunables.Ai.Targeting.TargetStickSeconds;
        private static float StickBonus => SimTunables.Ai.Targeting.TargetStickBonus;
        private static float OverkillShare => SimTunables.Ai.Targeting.OverkillShare;
        private static float OverkillFloor => SimTunables.Ai.Targeting.OverkillFloor;
        private static float AimTau => SimTunables.Ai.Targeting.AimTimeConstant;
        private static float MaxAimSeconds => SimTunables.Ai.Targeting.MaxAimSeconds;

        /// <summary>Per vehicle: the step it was last asked whether a valuable structure is in its reach, and the answer.</summary>
        private readonly Dictionary<EntityId, (long tick, bool any)> _structureNear = new();

        // ------------------------------------------------------------------------------------------------ feasibility

        /// <summary>The mount that carries <paramref name="weapon"/> (the first one; 0 when none does).</summary>
        internal static int MountOf(Vehicle v, WeaponDef weapon)
        {
            for (var i = 0; i < v.Arms.Length; i++)
                if (ReferenceEquals(v.Arms[i], weapon)) return i;
            return 0;
        }

        /// <summary>
        /// Spec 42 / 105: the hard filter every candidate passes before it is scored: alive and targetable, inside the weapon's
        /// target mask (layer, altitude tier, a coastal battery's ships), legally known (fog), in reach and beyond the minimum
        /// reach, a clear line for direct fire, inside the mount's arc, and brought to bear within <see cref="MaxAimSeconds"/>.
        /// </summary>
        internal TargetReject Feasibility(Vehicle v, WeaponDef weapon, Vehicle target, int arcMount = -1)
        {
            if (!target.IsAlive || target.Invulnerable || target.Def.Untargetable || target.Truce || target.Team == v.Team ||
                _world.Ceasefire(v.Team, target.Team)) return TargetReject.Invalid;
            // Prompt 16: a coastal battery's guns fire on ships only.
            if (v.Def.NavalOnly && target.Def.Naval == null) return TargetReject.WrongWeaponDomain;
            if (!target.IsVisibleTo(v.Team)) return TargetReject.NotVisible;
            if (!InReach(v, target, weapon))
            {
                var domain = target.Tier != AltitudeTier.None ? TierRules.Reaches(weapon, v.Def, target.Tier, true) : weapon.CanEngage(target.Flying, v.Def);
                if (!domain) return TargetReject.WrongWeaponDomain;
                return InsideMinimum(v, target, weapon) ? TargetReject.MinRange : TargetReject.OutOfReach;
            }
            if (!HasLineOfFire(v, target, weapon)) return TargetReject.NoLineOfFire;
            if (arcMount >= 0 && !InArc(v, arcMount, target.Position)) return TargetReject.OutsideArc;
            var index = arcMount >= 0 ? arcMount : MountOf(v, weapon);
            if (!CanBear(v, index, target.Position)) return TargetReject.OutsideArc;
            // Spec 88: a target the weapon cannot bear on in acceptable time scores 0. Fixed defences and aircraft are left to
            // their own laying (a structure's slow data turret, an aircraft's run).
            if (!v.Def.Static && !v.Flying && AimSeconds(v, index, target.Position) > MaxAimSeconds) return TargetReject.AimTooLong;
            return TargetReject.None;
        }

        /// <summary>The target is inside one of the weapon's minimum reaches (the min-range trap of spec 42).</summary>
        private static bool InsideMinimum(Vehicle v, IDamageable target, WeaponDef weapon)
        {
            var distance = Vector2.Distance(v.Position, target.Position);
            if (distance < weapon.MinRange) return true;
            if (weapon.MinReach > 0f && distance - target.Radius < weapon.MinReach) return true;
            return weapon.GroundMinReach > 0f && !IsFlying(target) && distance - target.Radius < weapon.GroundMinReach;
        }

        /// <summary>
        /// Spec 88: whether the mount can bear on the point at all: a traverse-limited turret (a towed gun's arc, prompt 25)
        /// or a hull-fixed weapon on a hull that cannot turn (a fixed defence, a dug-in vehicle) must already face it.
        /// </summary>
        private static bool CanBear(Vehicle v, int index, Vector2 at)
        {
            if (v.Flying || index >= v.Def.Mounts.Count) return true;
            var mount = v.Def.Mounts[index];
            var hullTurns = !v.Def.Static && v.Def.Speed > 0f && v.Deploy != DeployState.Deployed && !v.Def.HoldsToFire;
            if (hullTurns) return true;
            var bearing = SimMath.HeadingOf(at - v.Position);
            if (mount.Aim == MountAim.Hull) return MathF.Abs(SimMath.WrapAngle(bearing - v.Heading)) <= HullTolerance;
            if (mount.Aim == MountAim.Turret && index == 0 && v.Def.TurretArc > 0f)
                return MathF.Abs(SimMath.WrapAngle(bearing - v.Heading)) <= v.Def.TurretArc + TurretTolerance;
            return true;
        }

        /// <summary>
        /// Spec 89: seconds to bring mount <paramref name="index"/> onto a point: the angle off its current heading over its
        /// traverse (a turret's, plus the hull's when the hull can turn as well; a fixed weapon by the hull's turn; a free or
        /// side mount by its own fast mount). Aircraft manoeuvre onto their targets: 0.
        /// </summary>
        internal static float AimSeconds(Vehicle v, int index, Vector2 at)
        {
            if (v.Flying || index >= v.Def.Mounts.Count) return 0f;
            var mount = v.Def.Mounts[index];
            var bearing = SimMath.HeadingOf(at - v.Position);
            var off = MathF.Abs(SimMath.WrapAngle(bearing - v.MountHeading(index)));
            var hull = !v.Def.Static && v.Def.Speed > 0f && v.Deploy != DeployState.Deployed && !v.Def.HoldsToFire
                ? v.Def.TurnRate * v.TurnFactor
                : 0f;
            float rate;
            switch (mount.Aim)
            {
                case MountAim.Turret:
                    rate = v.Def.LaysOwnTurret ? MathF.Max(hull, FreeMainLeast) : v.Def.TurretTurnRate * v.TurretFactor + hull;
                    off = MathF.Max(0f, off - TurretTolerance);
                    break;
                case MountAim.Hull:
                    rate = hull;
                    off = MathF.Max(0f, off - HullTolerance);
                    break;
                default:
                    rate = index == 0 && mount.Aim == MountAim.Free ? MathF.Max(FreeMainLeast, v.Def.TurretTurnRate * v.TurretFactor) : FreeMountTurnRate;
                    // A broadside or arc mount: inside its arc its own mount lays it; outside, the hull must turn.
                    if (IsSide(mount) && !InArc(v, index, at))
                    {
                        off = MathF.Abs(SimMath.WrapAngle(bearing - SideCentre(v, index))) - ArcOf(v, index);
                        rate = hull;
                    }
                    else off = MathF.Max(0f, off - FreeTolerance);
                    break;
            }
            if (off <= 0f) return 0f;
            return rate > 1e-4f ? off / rate : float.MaxValue;
        }

        // ------------------------------------------------------------------------------------------------ scoring

        /// <summary>
        /// The master spec's factors on the existing score (see the class summary): aim time, stickiness, objective threat,
        /// doctrine, a suppressed target (the watchdog's step 6) and overkill. 1: no change.
        /// </summary>
        internal float P0AWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            var index = MountOf(v, weapon);
            var now = _world.Time;
            var worth = 1f;
            // Spec 89: AimPenalty = exp(-AimSeconds / 4).
            var aim = AimSeconds(v, index, other.Position);
            if (aim > 0f) worth *= MathF.Exp(-aim / MathF.Max(0.1f, AimTau));
            // Spec 45: the current target +15 % for 1.5 s after it was acquired.
            var state = v.Weapons[index];
            if (state.Target == other.Id && now - state.AcquiredAt < StickSeconds) worth *= 1f + StickBonus;
            // Spec 46 + Part H: ThreatToObjective, weighted against ThreatToSelf (the old score's threat factors).
            var objective = ThreatToObjective(v, other);
            if (objective > 0f)
                worth *= 1f + objective * SimTunables.Ai.Targeting.ThreatToObjectiveWeight / MathF.Max(0.01f, SimTunables.Ai.Targeting.ThreatToSelfWeight);
            // Part B B2 / B3.
            // AI MASTER P2: Part B B4-B13 role ladders (via DoctrineWorth) and Part I mode target weights.
            worth *= DoctrineWorth(v, other, weapon) * P2ModeWorth(v, other, weapon);
            // Part C1 step 6: the target the watchdog gave up on is the last resort for a moment.
            if (other.Id == v.SuppressedTarget && now < v.SuppressedUntil) worth *= OverkillFloor;
            // Spec 44: overkill: with more than 1.15 x its health already on the way, another target if there is one.
            if (Overkilled(v, other)) worth *= OverkillFloor;
            return worth;
        }

        /// <summary>Spec 44: the expected damage on its way to a target (rounds in flight).</summary>
        internal float Committed(EntityId target) => _incoming.TryGetValue(target, out var d) ? d : 0f;

        /// <summary>
        /// Spec 44 / 139: damage committed to a target by something other than a round in flight (a planned strike; the tests'
        /// overkill set-up). It stays until rounds landing on the target take it off, like any other.
        /// </summary>
        internal void NoteIncoming(EntityId target, float damage) => _incoming[target] = Committed(target) + damage;

        /// <summary>Spec 44 / 106: the damage in flight at the target exceeds 1.15 x its health, and no exception applies.</summary>
        internal bool Overkilled(Vehicle v, Vehicle other)
        {
            if (!_incoming.TryGetValue(other.Id, out var committed)) return false;
            if (committed <= MathF.Max(1f, other.Hp) * OverkillShare) return false;
            return !OverkillExempt(v, other);
        }

        /// <summary>
        /// Spec 44's exceptions: a boss part the side was ordered onto (prompt 9), an Executioner finishing a target under
        /// 30 %, a forced target (the player's order, the squad's focus), an extremely dangerous target (a boss, or worth
        /// <see cref="SimTunables.Ai.Targeting.OverkillDangerWorth"/> CP or more).
        /// </summary>
        internal bool OverkillExempt(Vehicle v, Vehicle other)
        {
            if (other.HasParts && _world.Bosses.IsFocused(v.Team, other.Id)) return true;
            if (v.Gear != null && v.Gear.Has(TraitId.Executioner) && other.Hp < other.MaxHp * 0.3f) return true;
            if (v.ManualOrder && v.Order.Kind == OrderKind.Attack && v.Order.Target == other.Id) return true;
            if (other.Def.Boss || Worth(other) >= SimTunables.Ai.Targeting.OverkillDangerWorth) return true;
            return false;
        }

        // ------------------------------------------------------------------------------------------------ Part H

        /// <summary>
        /// Part H: how much <paramref name="other"/> threatens <paramref name="v"/>'s side's objective, 0-1: capturing or
        /// contesting a point (ours: 1), shooting at the convoy (1) or standing with it in reach (0.5), an enemy breacher at our
        /// walls when we defend (1), a defence shooting at our assault on a structure (1) or covering the structure we are
        /// breaching (0.8), anything shooting at one of our structures (0.6). BossRush part focus stays the prompt-9 order.
        /// </summary>
        internal float ThreatToObjective(Vehicle v, Vehicle other)
        {
            var threat = 0f;
            // Conquest: a unit actively capturing a critical point.
            if (!other.Flying && other.Def.CaptureRate > 0f && _world.Intel.Objectives is { } objectives)
                foreach (var point in objectives.Points)
                {
                    if (point.Owner == other.Team) continue;
                    var reach = point.Def.Radius + other.Radius;
                    if (Vector2.DistanceSquared(point.Def.Position, other.Position) > reach * reach) continue;
                    threat = MathF.Max(threat, point.Owner == v.Team ? 1f : 0.7f);
                }
            var shotAt = _world.TryGetVehicle(other.Target, out var victim) && victim.Team == v.Team ? victim : null;
            // Escort: the unit damaging the convoy outranks a distant heavy.
            if (_world.ConvoySafeZone != null && other.Def.Weapon.Damage > 0f)
                foreach (var truck in _world.ConvoySafeZone())
                {
                    if (shotAt != null && Vector2.DistanceSquared(shotAt.Position, truck) < 9f) return 1f;
                    var reach = other.Def.Weapon.Range + 2f;
                    if (Vector2.DistanceSquared(truck, other.Position) <= reach * reach) threat = MathF.Max(threat, 0.5f);
                }
            // Defend: a breacher threatening the gate or wall rises sharply.
            if ((other.Def.Breacher || other.Def.WallBreaker) && _world.HasWalls)
            {
                var near = SimTunables.Ai.Targeting.DefendBreachReach;
                foreach (var line in _world.Walls.Lines)
                {
                    if (line.Team != v.Team || line.Standing == 0) continue;
                    var half = line.Def.Radius + near;
                    var d = other.Position - line.Hq;
                    if (MathF.Max(MathF.Abs(d.X), MathF.Abs(d.Y)) < half) return 1f;
                }
            }
            if (other.Def.Static && other.Def.Weapon.Damage > 0f)
            {
                // Siege: a defence shooting at our assault on a structure, or covering the structure we are breaching.
                if (shotAt != null && shotAt.Order.Kind == OrderKind.Attack && _world.TryGetVehicle(shotAt.Order.Target, out var breached) && breached.Def.Static)
                    return 1f;
                if (v.Order.Kind == OrderKind.Attack && v.Order.Target != other.Id && _world.TryGetVehicle(v.Order.Target, out var mine) && mine.Def.Static &&
                    Vector2.Distance(mine.Position, other.Position) <= other.Def.Weapon.Range + mine.Radius)
                    threat = MathF.Max(threat, 0.8f);
            }
            // Anything shooting at one of our structures (a base, a wall, a defence).
            if (shotAt != null && shotAt.Def.Static) threat = MathF.Max(threat, 0.6f);
            return threat;
        }

        // ------------------------------------------------------------------------------------------------ Part B

        /// <summary>A breacher (Part B B2): the armoured bulldozer, an engineer breach vehicle, a wall breaker.</summary>
        internal static bool IsBreacher(Vehicle v) => v.Def.Breacher || v.Def.WallBreaker;

        /// <summary>A siege platform (Part B B3): the AI role "Siege", or a vehicle that deploys into siege mode.</summary>
        internal bool IsSiegePlatform(Vehicle v) =>
            v.Def.Deploy is { Siege: true } || _world.Catalog.AiData.RoleOf(v.Def.Id)?.Id == "Siege";

        /// <summary>A structure that blocks a way (a wall segment, a gate, an obstacle).</summary>
        internal static bool IsBlockingStructure(Vehicle target) => target.Def.Wall || target.Def.Obstacle;

        /// <summary>
        /// B2/B5: an immediate survival threat to <paramref name="v"/>: it is aiming at this vehicle, its weapon can hit it,
        /// and it is within its reach of it.
        /// </summary>
        internal bool ImmediateSurvivalThreat(Vehicle v, Vehicle other)
        {
            if (other.Target != v.Id || !other.IsAlive) return false;
            var weapon = other.Def.Weapon;
            if (weapon.Damage <= 0f || !weapon.CanTarget(v.Flying)) return false;
            return Vector2.Distance(other.Position, v.Position) - v.Radius <= weapon.Range;
        }

        /// <summary>
        /// B2: a blocking structure in the breacher's mission corridor: the one it was ordered onto, or one within
        /// <see cref="SimTunables.Ai.Targeting.BreachCorridorWidth"/> of its straight way to its order's point.
        /// </summary>
        private bool InBreachCorridor(Vehicle v, Vehicle structure)
        {
            if (v.Order.Kind == OrderKind.Attack) return v.Order.Target == structure.Id;
            if (v.Order.Kind is not (OrderKind.AttackMove or OrderKind.Move)) return false;
            var from = v.Position;
            var to = v.Order.Point;
            var d = to - from;
            var length = d.Length();
            if (length < 1f) return false;
            var dir = d / length;
            var rel = structure.Position - from;
            var along = Vector2.Dot(rel, dir);
            if (along < -structure.Radius || along > length + structure.Radius) return false;
            var across = MathF.Abs(rel.X * dir.Y - rel.Y * dir.X);
            return across <= SimTunables.Ai.Targeting.BreachCorridorWidth + structure.Radius;
        }

        /// <summary>Part B B2 / B3 role factors on a candidate; every other role's ladder is lane P2's <see cref="P2RoleWorth"/>.</summary>
        private float DoctrineWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (IsBreacher(v))
            {
                // 1-2, 4: the blocking wall, gate or obstacle on the mission corridor (only those: walls are not globally high).
                if (IsBlockingStructure(other)) return InBreachCorridor(v, other) ? SimTunables.Ai.Targeting.BreachStructureBonus : 1f;
                // 3: a tower directly defending the breach point.
                if (other.Def.Static && other.Def.Weapon.Damage > 0f) return 1f;
                // 5-6: a combat unit only as an immediate threat; otherwise it does not pull the breacher off its task.
                return ImmediateSurvivalThreat(v, other) ? 1f : SimTunables.Ai.Targeting.BreacherDistraction;
            }
            if (IsSiegePlatform(v))
            {
                if (other.Def.Static && !IsBlockingStructure(other))
                {
                    if (other.Def.Weapon.Damage <= 0f) return SimTunables.Ai.Targeting.SiegeStructureBonus;
                    // 1: currently damaging the assault; 2: a defensive tower.
                    var engaged = _world.TryGetVehicle(other.Target, out var victim) && victim.Team == v.Team;
                    return SimTunables.Ai.Targeting.SiegeTowerBonus * (engaged ? SimTunables.Ai.Targeting.SiegeEngagedTowerBonus : 1f);
                }
                // 7: light targets only when no valuable structure remains, or in self-defence.
                if (!other.Def.Static && other.Armor == ArmorClass.Light && !ImmediateSurvivalThreat(v, other) && StructureInReach(v, weapon))
                    return SimTunables.Ai.Targeting.SiegeLightPenalty;
            }
            // AI MASTER P2: every other role's Part B ladder.
            return P2RoleWorth(v, other, weapon);
        }

        /// <summary>A valuable enemy structure (not a wall or obstacle) the weapon could shoot now; once per vehicle per step.</summary>
        private bool StructureInReach(Vehicle v, WeaponDef weapon)
        {
            var tick = _world.Tick;
            if (_structureNear.TryGetValue(v.Id, out var known) && known.tick == tick) return known.any;
            var any = false;
            foreach (var o in _world.VehicleList)
            {
                if (!o.Def.Static || IsBlockingStructure(o) || o.Team == v.Team || o.Team < 0) continue;
                if (!IsValidAutoTarget(v, o, weapon)) continue;
                any = true;
                break;
            }
            if (_structureNear.Count > 4096) _structureNear.Clear();
            _structureNear[v.Id] = (tick, any);
            return any;
        }

        /// <summary>
        /// Part B B2 (regression R2): an ordered breach holds: a breacher (or any unit the AI sent at a wall segment) on a
        /// blocking structure gives way only to an immediate survival threat, or (an anti-air weapon, as before) to an aircraft.
        /// </summary>
        internal bool BreachHeld(Vehicle v, WeaponDef weapon, IDamageable ordered, Vehicle best)
        {
            if (ordered is not Vehicle structure || !IsBlockingStructure(structure)) return false;
            if (!IsBreacher(v) && !structure.Def.Wall) return false;
            if (IsAntiAir(weapon) && best.Flying) return false;
            return !ImmediateSurvivalThreat(v, best);
        }

        // ------------------------------------------------------------------------------------------------ the watchdog's view

        /// <summary>The main weapon's mount this step (a siege tank on its tracks lays its tank-mode gun).</summary>
        internal static int MainMount(Vehicle v) =>
            v.Def.Deploy is { Siege: true } siege && v.Deploy != DeployState.Deployed && siege.TankMount < v.Def.Mounts.Count ? siege.TankMount : 0;

        /// <summary>Part C: the firing picture of mount <paramref name="index"/> against <paramref name="target"/>.</summary>
        internal FiringCheck Check(Vehicle v, int index, IDamageable target)
        {
            var weapon = v.Arms[index];
            TargetReject reject;
            if (target is Vehicle vehicle) reject = Feasibility(v, weapon, vehicle, IsSide(v.Def.Mounts[index]) ? index : -1);
            else if (!target.IsAlive) reject = TargetReject.Invalid;
            else if (!InReach(v, target, weapon)) reject = InsideMinimum(v, target, weapon) ? TargetReject.MinRange : TargetReject.OutOfReach;
            else if (!HasLineOfFire(v, target, weapon)) reject = TargetReject.NoLineOfFire;
            else reject = TargetReject.None;
            var state = v.Weapons[index];
            var ready = state.Cooldown <= 0f && state.Ammo != 0 && state.ReloadLeft <= 0f && v.MountWorks(index);
            var friend = target is Vehicle t && !v.Flying && weapon.MinRange <= 0f && weapon.Projectile != ProjectileKind.Bomb && FriendInLine(v, t);
            var aimSeconds = AimSeconds(v, index, target.Position);
            return new FiringCheck(reject, ready, friend, aimSeconds, aimSeconds <= 0f);
        }

        /// <summary>
        /// Part C2: the visible enemy the main weapon could engage (its layer and tier) that is nearest, and why it is not
        /// being shot (None: it has a firing solution). Null when nothing visible is in the weapon's domain.
        /// </summary>
        internal Vehicle? NearestEngageable(Vehicle v, int index, out TargetReject why)
        {
            why = TargetReject.Invalid;
            var weapon = v.Arms[index];
            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            var bestWhy = TargetReject.Invalid;
            foreach (var o in _world.VehicleList)
            {
                if (!o.IsAlive || o.Team == v.Team || o.Team < 0 || o.Def.Untargetable || o.Truce || !o.IsVisibleTo(v.Team)) continue;
                if (o.Def.Passive && IsBlockingStructure(o)) continue;
                var r = Feasibility(v, weapon, o, IsSide(v.Def.Mounts[index]) ? index : -1);
                if (r is TargetReject.Invalid or TargetReject.WrongWeaponDomain or TargetReject.NotVisible) continue;
                // A solution beats any distance; otherwise the nearest.
                var d = Vector2.DistanceSquared(v.Position, o.Position) - (r == TargetReject.None ? 1e9f : 0f);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = o;
                bestWhy = r;
            }
            why = bestWhy;
            return best;
        }

        /// <summary>
        /// Part C1 steps 1-3 and 6: validate the held target, drop stale aim state and look again at once; with
        /// <paramref name="suppress"/>, the held target is also left alone for a moment so another is chosen.
        /// </summary>
        internal void ResetAim(Vehicle v, bool suppress, double suppressUntil)
        {
            if (suppress && v.Target.IsValid)
            {
                v.SuppressedTarget = v.Target;
                v.SuppressedUntil = suppressUntil;
            }
            v.Target = EntityId.None;
            v.RetargetAt = double.NegativeInfinity;
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var s = v.Weapons[i];
                s.RetargetAt = double.NegativeInfinity;
                if (s.ChargeLeft <= 0f && s.BurstLeft <= 0 && !_world.TryGetTarget(s.Target, out _)) s.Target = EntityId.None;
            }
        }

        /// <summary>Spec 45: the acquisition clock of a mount (stamped when its target changes).</summary>
        private void Acquire(Vehicle v, int index, EntityId next)
        {
            var state = v.Weapons[index];
            if (state.Target != next) state.AcquiredAt = _world.Time;
        }
    }
}
