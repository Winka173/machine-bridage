#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Play-test 8 A (DECISIONS 22Q): bombs fall. An unguided bomb leaves the aircraft with its forward speed and drops;
    /// it lands where its drop point and its fall put it (a little scatter round that), never on the target it was meant
    /// for: a target that drives on is missed. A bomber lets its stick go one bomb after another as it passes over, so the
    /// bombs come down spaced along its track, and it lets go when the stick will straddle the target. A steered bomb (the
    /// SDB, the JDAM: <see cref="WeaponDef.GuidedBomb"/>) glides onto its target as before. The fire supports' airstrikes
    /// already lay their bombs along the line they fly (<see cref="Strikes.StrikeSystem"/>); their views fall the same way.
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>
        /// The pull on a falling bomb, m/s². The battlefields are drawn small (a bomber flies at 42 m): at the true 9.8 a
        /// bomb from there would carry 60 to 90 m past its drop point, past any fight on the map, so the fall runs at the
        /// maps' own scale (1.1 to 1.5 s from 30 to 46 m). The bomb keeps the aircraft's forward speed all the way down.
        /// </summary>
        internal const float BombGravity = 40f;

        /// <summary>A free-falling bomb's scatter round the point its fall puts it, as a share of the weapon's spread.</summary>
        internal const float FreeFallScatter = 0.5f;

        /// <summary>A bomb that falls free: unguided, dropped from an aircraft.</summary>
        /// <para>The bomb-run fix, pass 2: not a boss's bomb bay (<see cref="BayStick"/>), which lays its stick round its aim.</para>
        internal static bool FreeFall(Vehicle shooter, WeaponDef weapon) =>
            weapon.Projectile == ProjectileKind.Bomb && shooter.Flying && !weapon.GuidedBomb && !BayStick(weapon);

        /// <summary>
        /// The bomb-run fix, pass 2: a boss's bomb bay (stick.drop BAY): unguided bombs laid as a stick round the aim (the boss
        /// stands off, its bay ripples at the stick's interval), each bomb on its own point, no longer one shell salvo on a point.
        /// </summary>
        internal static bool BayStick(WeaponDef weapon) =>
            weapon.Projectile == ProjectileKind.Bomb && !weapon.GuidedBomb && weapon.Stick is { Laid: true, Drop: StickDrop.Bay };

        /// <summary>The bomb-run fix, pass 2: this shooter lays this weapon's bombs on a stick (a free-falling stick or a boss bay).</summary>
        internal static bool Sticks(Vehicle shooter, WeaponDef weapon) => weapon.LaysStick && (FreeFall(shooter, weapon) || BayStick(weapon));

        /// <summary>Seconds a bomb takes to fall from the aircraft's height.</summary>
        internal static float BombFall(Vehicle shooter) => MathF.Sqrt(2f * MathF.Max(4f, shooter.Height) / BombGravity);

        /// <summary>Where a bomb let go now comes down (before its scatter): ahead of the aircraft by its speed over the fall.</summary>
        internal static Vector2 BombImpact(Vehicle shooter) =>
            shooter.Position + SimMath.Forward(shooter.Heading) * (shooter.Speed * BombFall(shooter));

        /// <summary>How far along the ground a stick of <paramref name="bombs"/> reaches from its first bomb to its last.</summary>
        /// <para>The bomb-run fix, pass 2: a stick weapon's is its data spacing ((n - 1) x spacing), whatever the aircraft's speed.</para>
        internal static float StickLength(Vehicle shooter, WeaponDef weapon, int bombs) =>
            weapon.Stick is { Laid: true } s ? Math.Max(0, bombs - 1) * s.Spacing : Math.Max(0, bombs - 1) * weapon.BurstInterval * shooter.Speed;

        /// <summary>The bombs the next pull lets go: the salvo, or what is left of an aircraft's stores.</summary>
        private static int StickBombs(Vehicle v, int index)
        {
            var weapon = v.Arms[index];
            var state = v.Weapons[index];
            return state.Load > 0 ? Math.Min(weapon.Burst, Math.Max(1, state.Ammo)) : weapon.Burst;
        }

        /// <summary>A free-falling bomb's reach for picking targets: as far ahead as the middle of its stick comes down, and a blast more.</summary>
        private static float BombReach(Vehicle v, WeaponDef weapon) =>
            v.Speed * BombFall(v) + StickLength(v, weapon, weapon.Burst) * 0.5f + weapon.SplashRadius;

        /// <summary>
        /// The moment to let the stick go: it will straddle the target. The target lies on the track no further to the
        /// side than a bomb's blast, and along it between just short of where the first bomb falls and the middle of the
        /// stick, so the first bombs land before it and the last beyond it.
        /// </summary>
        /// <para>The bomb-run fix, pass 2: a stick anchored at its START lets go when the target is where the first bomb falls;
        /// one anchored at its CENTER (the default) when the target is under the middle of the stick it will drop.</para>
        /// <para>Play-test 13 (lane C): a CENTER stick lets go when the middle of the stick it will drop comes over the best
        /// centre for the target group (<see cref="BestStickCentre"/>: the target inside the stick, as many enemies under it
        /// as the stick can reach), so a lone target falls mid-stick (bombs 1-2-3 round it, not 2-3-4 past it) and a row is
        /// covered from its first vehicle. Its window still closes once the target would fall behind the first bomb.</para>
        private bool StickStraddles(Vehicle v, int index, IDamageable target)
        {
            var weapon = v.Arms[index];
            var forward = SimMath.Forward(v.Heading);
            var offset = target.Position - v.Position;
            var along = Vector2.Dot(offset, forward);
            var across = MathF.Abs(offset.X * forward.Y - offset.Y * forward.X);
            var fall = v.Speed * BombFall(v);
            var bombs = StickBombs(v, index, target);
            var stick = StickLength(v, weapon, bombs);
            var blast = weapon.SplashRadius + target.Radius;
            if (across > blast || along < fall - blast * 0.5f) return false;
            if (weapon.Stick is { Laid: true, Anchor: StickAnchor.Start }) return along <= fall + blast * 0.5f;
            var centre = GroupCentre(v, weapon, target, forward, bombs);
            return Vector2.Dot(centre - v.Position, forward) <= fall + stick * 0.5f;
        }

        /// <summary>Play-test 13 (lane C): the best centre along <paramref name="dir"/> for a stick of <paramref name="bombs"/> over <paramref name="target"/>'s group.</summary>
        private Vector2 GroupCentre(Vehicle v, WeaponDef weapon, IDamageable target, Vector2 dir, int bombs)
        {
            var length = StickLength(v, weapon, bombs);
            var spacing = bombs > 1 ? length / (bombs - 1) : 0f;
            StickTargets(v, target.Position, length * 0.5f + weapon.SplashRadius + weapon.WarnRadius, out _);
            return BestStickCentre(target.Position, dir, bombs, spacing, weapon.SplashRadius, 0f, _stickPoints, out _);
        }

        /// <summary>
        /// Play-test 13 (lane C): where a stick's middle goes so it hits the most of <paramref name="points"/> (an enemy within
        /// <paramref name="blast"/> of any bomb counts once), the target always inside the stick: centres from half a stick
        /// before the target to half a stick past it along <paramref name="dir"/>, half a spacing apart, and up to
        /// <paramref name="lateral"/> to either side. Ties: the stick that also hits the target, then the one nearest the target,
        /// then the first tried. Deterministic: the same points in the same order give the same centre.
        /// </summary>
        internal static Vector2 BestStickCentre(Vector2 target, Vector2 dir, int bombs, float spacing, float blast, float lateral,
            IReadOnlyList<Vector2> points, out int hits)
        {
            var side = new Vector2(-dir.Y, dir.X);
            var length = Math.Max(0, bombs - 1) * spacing;
            var step = MathF.Max(1f, spacing * 0.5f);
            var alongSteps = length > 0f ? (int)MathF.Floor(length * 0.5f / step + 1e-4f) : 0;
            var sideSteps = lateral > 0f ? 2 : 0;
            var best = target;
            var bestScore = -1;
            var bestCost = float.MaxValue;
            hits = 0;
            var reach = blast * blast;
            for (var ai = -alongSteps; ai <= alongSteps; ai++)
                for (var si = -sideSteps; si <= sideSteps; si++)
                {
                    var a = ai * step;
                    var b = sideSteps > 0 ? si * lateral / sideSteps : 0f;
                    var centre = target + dir * a + side * b;
                    var count = 0;
                    for (var p = 0; p < points.Count; p++)
                        if (UnderStick(points[p], centre, dir, bombs, spacing, reach)) count++;
                    var score = count * 2 + (UnderStick(target, centre, dir, bombs, spacing, reach) ? 1 : 0);
                    var cost = MathF.Abs(a) + MathF.Abs(b);
                    if (score < bestScore || (score == bestScore && cost >= bestCost - 1e-4f)) continue;
                    bestScore = score;
                    bestCost = cost;
                    best = centre;
                    hits = count;
                }
            return best;
        }

        /// <summary>Whether <paramref name="point"/> lies within a bomb's blast (squared: <paramref name="reach"/>) of the stick centred on <paramref name="centre"/>.</summary>
        private static bool UnderStick(Vector2 point, Vector2 centre, Vector2 dir, int bombs, float spacing, float reach)
        {
            for (var k = 0; k < bombs; k++)
                if (Vector2.DistanceSquared(point, centre + dir * ((k - (bombs - 1) * 0.5f) * spacing)) <= reach) return true;
            return false;
        }

        /// <summary>A friendly ground vehicle where the stick would come down (no bombs on friends).</summary>
        private bool StickNearOwn(Vehicle v, int index)
        {
            var weapon = v.Arms[index];
            var stick = StickLength(v, weapon, StickBombs(v, index));
            var middle = BombImpact(v) + SimMath.Forward(v.Heading) * (stick * 0.5f);
            return OwnNear(v.Team, middle, weapon.SplashRadius + stick * 0.5f + 3f);
        }

        // ------------------------------------------------------------------------------------------------ the bomb-run fix, pass 2

        /// <summary>The cosine of 45 degrees: a cluster axis further off the approach than this lays the stick on the approach.</summary>
        internal const float AxisCone = 0.70710678f;

        /// <summary>A cluster whose long spread is under this many times its short one has no main axis (a blob, not a line).</summary>
        internal static float AxisRatio => global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.AxisRatio;

        /// <summary>
        /// The way a stick runs (a unit vector): the main axis of <paramref name="points"/> (the 2 x 2 covariance's major
        /// eigenvector, signed to point along the approach) when the points have one and it lies within 45 degrees of
        /// <paramref name="approach"/>; else the approach. Deterministic: the same points in the same order give the same way.
        /// </summary>
        internal static Vector2 StickDirection(Vector2 approach, IReadOnlyList<Vector2> points)
        {
            var way = approach.LengthSquared() > 1e-6f ? Vector2.Normalize(approach) : new Vector2(0f, 1f);
            if (points.Count < 2) return way;
            var mean = Vector2.Zero;
            for (var i = 0; i < points.Count; i++) mean += points[i];
            mean /= points.Count;
            float cxx = 0f, cyy = 0f, cxy = 0f;
            for (var i = 0; i < points.Count; i++)
            {
                var d = points[i] - mean;
                cxx += d.X * d.X;
                cyy += d.Y * d.Y;
                cxy += d.X * d.Y;
            }
            cxx /= points.Count;
            cyy /= points.Count;
            cxy /= points.Count;
            var half = 0.5f * (cxx - cyy);
            var gap = MathF.Sqrt(half * half + cxy * cxy);
            var mid = 0.5f * (cxx + cyy);
            var major = mid + gap;
            var minor = MathF.Max(0f, mid - gap);
            if (major < 1f || major < AxisRatio * minor) return way;
            var angle = 0.5f * MathF.Atan2(2f * cxy, cxx - cyy);
            var axis = new Vector2(MathF.Cos(angle), MathF.Sin(angle));
            var dot = Vector2.Dot(axis, way);
            if (dot < 0f)
            {
                axis = -axis;
                dot = -dot;
            }
            return dot >= AxisCone ? axis : way;
        }

        /// <summary>Where bomb <paramref name="i"/> of a stick lands before its jitter: the start plus i spacings along the stick.</summary>
        internal static Vector2 StickPoint(Vector2 start, Vector2 dir, float spacing, int i) => start + dir * (i * spacing);

        /// <summary>The enemy ground units (vehicles and structures) round a point, in list order: the cluster a stick is laid on.</summary>
        private readonly List<Vector2> _stickPoints = new();

        /// <summary>Fills <see cref="_stickPoints"/> with the enemy ground units within <paramref name="reach"/> of <paramref name="centre"/>; their count.</summary>
        private int StickTargets(Vehicle v, Vector2 centre, float reach, out int structures)
        {
            _stickPoints.Clear();
            structures = 0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Invulnerable || e.Def.Untargetable) continue;
                var r = reach + e.Radius;
                if (Vector2.DistanceSquared(e.Position, centre) > r * r) continue;
                _stickPoints.Add(e.Position);
                if (e.Def.Static) structures++;
            }
            return _stickPoints.Count;
        }

        /// <summary>
        /// The bombs a stick drops on <paramref name="target"/> out of <paramref name="salvo"/>: all of them on at least its
        /// minimum targets (or a row of two structures) round the stick, else max(2, ceil(n / 3)) (stick.minTargets).
        /// </summary>
        private int StickCount(Vehicle v, int index, IDamageable target, int salvo)
        {
            var weapon = v.Arms[index];
            if (!Sticks(v, weapon) || weapon.Stick is not { } s || s.MinTargets <= 0 || salvo <= s.Reduced) return salvo;
            var count = StickTargets(v, target.Position, StickLength(v, weapon, s.Bombs) * 0.5f + weapon.WarnRadius, out var structures);
            return count >= s.MinTargets || structures >= 2 ? salvo : Math.Min(salvo, s.Reduced);
        }

        /// <summary>The bombs the next pull lets go on <paramref name="target"/>: the stores' salvo, cut to the few-target count.</summary>
        private int StickBombs(Vehicle v, int index, IDamageable target) => StickCount(v, index, target, StickBombs(v, index));

        /// <summary>
        /// The line a stick of <paramref name="bombs"/> is laid on: a free-falling stick runs along the aircraft's track from
        /// where its first bomb's fall puts it (the aircraft's position plus its speed over the fall: the lead); a boss bay's
        /// is centred on (or starts at) its aim and runs along the cluster's axis or the boss's line to the aim.
        /// </summary>
        private void StickLine(Vehicle v, WeaponDef weapon, Vector2 aim, int bombs, out Vector2 start, out Vector2 dir)
        {
            var s = weapon.Stick!;
            if (!BayStick(weapon))
            {
                dir = SimMath.Forward(v.Heading);
                start = BombImpact(v);
                return;
            }
            var length = Math.Max(0, bombs - 1) * s.Spacing;
            var approach = aim - v.Position;
            if (approach.LengthSquared() < 1e-4f) approach = SimMath.Forward(v.Heading);
            dir = s.Heading == StickHeading.Axis
                ? AxisAt(v, weapon, aim, length, approach)
                : Vector2.Normalize(approach);
            // Play-test 13 (lane C): a CENTER bay stick is centred on the best centre for the group round its aim (the aim inside it).
            if (s.Anchor == StickAnchor.Center)
            {
                StickTargets(v, aim, length * 0.5f + weapon.SplashRadius + weapon.WarnRadius, out _);
                var centre = BestStickCentre(aim, dir, bombs, s.Spacing, weapon.SplashRadius, weapon.SplashRadius * 0.5f, _stickPoints, out _);
                start = centre - dir * (length * 0.5f);
            }
            else start = aim;
        }

        /// <summary>The cluster's axis round <paramref name="aim"/> (within 45 degrees of <paramref name="approach"/>), else the approach.</summary>
        private Vector2 AxisAt(Vehicle v, WeaponDef weapon, Vector2 aim, float length, Vector2 approach)
        {
            StickTargets(v, aim, length * 0.5f + weapon.WarnRadius, out _);
            return StickDirection(approach, _stickPoints);
        }

        /// <summary>
        /// The stick's first bomb: fixes its line in the mount's state (every later bomb lands on its own point along it, never
        /// on a shared aim) and, for a free-falling stick, holds the aircraft straight and level for its straight-flight time.
        /// </summary>
        private void PlanStick(Vehicle v, int index, WeaponDef weapon, Vector2 aim)
        {
            var state = v.Weapons[index];
            var s = weapon.Stick!;
            var bombs = state.StickBombs > 0 ? state.StickBombs : s.Bombs;
            StickLine(v, weapon, aim, bombs, out var start, out var dir);
            state.StickStart = start;
            state.StickDir = dir;
            state.StickNext = 0;
            state.StickBombs = bombs;
            if (BayStick(weapon) || s.StraightTime <= 0f) return;
            v.StickStraightUntil = _world.Time + s.StraightTime;
            v.StraightHeading = v.Heading;
        }

        /// <summary>Every bomb of the stick would come down by friends (no bomb is dropped there; a stick with one safe bomb goes).</summary>
        private bool StickAllUnsafe(Vehicle v, int index, IDamageable target)
        {
            var weapon = v.Arms[index];
            var s = weapon.Stick!;
            var bombs = StickBombs(v, index, target);
            StickLine(v, weapon, target.Position, bombs, out var start, out var dir);
            for (var i = 0; i < bombs; i++)
                if (!OwnNear(v.Team, StickPoint(start, dir, s.Spacing, i), s.Safety)) return false;
            return true;
        }

        /// <summary>
        /// The pause after a stick: the data's cooldown less the time its longer release interval added to the salvo, so the
        /// cycle from one stick's first bomb to the next stays what it was (the fix changes where bombs land, not how often).
        /// </summary>
        private static float StickCooldown(WeaponDef weapon, WeaponState state) =>
            weapon.Stick is { Laid: true } s
                ? MathF.Max(0f, weapon.Cooldown - Math.Max(0, state.StickBombs - 1) * (s.Interval - weapon.BurstInterval))
                : weapon.Cooldown;

        /// <summary>
        /// A stick bomber's run in along the target cluster's axis (stick.heading AXIS): while it is still far out, it flies for
        /// a point behind the target on the axis (lead, half the stick and a turn back), then at the target, so it comes over
        /// the cluster along its line. <paramref name="goal"/> unchanged otherwise (on the axis already, close, no cluster).
        /// </summary>
        internal Vector2 StickEntry(Vehicle v, IDamageable target, Vector2 goal, float turnRadius)
        {
            if (v.Arms.Length == 0 || v.Weapons.Length == 0) return goal;
            var weapon = v.Arms[0];
            if (weapon.Stick is not { Laid: true, Heading: StickHeading.Axis } s || !FreeFall(v, weapon) || v.Weapons[0].Ammo == 0) return goal;
            var offset = target.Position - v.Position;
            var distance = offset.Length();
            var length = StickLength(v, weapon, s.Bombs);
            var back = v.Speed * BombFall(v) + length * 0.5f + turnRadius;
            if (distance < 1e-3f || distance <= back + turnRadius * 2f) return goal;
            var dir = AxisAt(v, weapon, target.Position, length, offset);
            if (Vector2.Dot(dir, offset / distance) > 0.996f) return goal;
            // Play-test 13 (lane C): the run lines up on the best centre for the group (up to half a blast to the side of the
            // target), not on the target itself; the release then waits for the stick's middle to come over it (StickStraddles).
            var centre = BestStickCentre(target.Position, dir, s.Bombs, s.Spacing, weapon.SplashRadius, weapon.SplashRadius * 0.5f, _stickPoints, out _);
            return _world.ClampToMap(centre - dir * back);
        }
    }
}
