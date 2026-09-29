#nullable enable
using System;
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
        internal static bool FreeFall(Vehicle shooter, WeaponDef weapon) =>
            weapon.Projectile == ProjectileKind.Bomb && shooter.Flying && !weapon.GuidedBomb;

        /// <summary>Seconds a bomb takes to fall from the aircraft's height.</summary>
        internal static float BombFall(Vehicle shooter) => MathF.Sqrt(2f * MathF.Max(4f, shooter.Height) / BombGravity);

        /// <summary>Where a bomb let go now comes down (before its scatter): ahead of the aircraft by its speed over the fall.</summary>
        internal static Vector2 BombImpact(Vehicle shooter) =>
            shooter.Position + SimMath.Forward(shooter.Heading) * (shooter.Speed * BombFall(shooter));

        /// <summary>How far along the ground a stick of <paramref name="bombs"/> reaches from its first bomb to its last.</summary>
        internal static float StickLength(Vehicle shooter, WeaponDef weapon, int bombs) =>
            Math.Max(0, bombs - 1) * weapon.BurstInterval * shooter.Speed;

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
        private bool StickStraddles(Vehicle v, int index, IDamageable target)
        {
            var weapon = v.Arms[index];
            var forward = SimMath.Forward(v.Heading);
            var offset = target.Position - v.Position;
            var along = Vector2.Dot(offset, forward);
            var across = MathF.Abs(offset.X * forward.Y - offset.Y * forward.X);
            var fall = v.Speed * BombFall(v);
            var stick = StickLength(v, weapon, StickBombs(v, index));
            var blast = weapon.SplashRadius + target.Radius;
            return across <= blast && along >= fall - blast * 0.5f && along <= fall + stick * 0.5f + 2f;
        }

        /// <summary>A friendly ground vehicle where the stick would come down (no bombs on friends).</summary>
        private bool StickNearOwn(Vehicle v, int index)
        {
            var weapon = v.Arms[index];
            var stick = StickLength(v, weapon, StickBombs(v, index));
            var middle = BombImpact(v) + SimMath.Forward(v.Heading) * (stick * 0.5f);
            return OwnNear(v.Team, middle, weapon.SplashRadius + stick * 0.5f + 3f);
        }
    }
}
