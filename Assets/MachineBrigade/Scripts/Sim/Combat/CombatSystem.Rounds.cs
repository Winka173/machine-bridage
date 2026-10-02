#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Prompt 25 G (DECISIONS 25G): second rounds. A gun with a second round loads, for the target it has picked, the round
    /// whose rule suits that target (the first in the data's order), else its own. Changing takes the gun's reload (at least
    /// 0.5 s, <see cref="WeaponDef.SwitchSeconds"/>), during which the mount fires nothing; a round once in stays in at
    /// least 2 s (<see cref="WeaponDef.RoundHoldSeconds"/>), so a unit whose target changes at every 0.5 s re-check
    /// (play-test 8 A) never flickers between rounds. No random draw is made and the state lives on the mount
    /// (<see cref="WeaponState.Round"/>), in the checkpoint's fingerprint (<see cref="SimWorld.StateHash"/>).
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>The round in a mount's gun now (its own when it has no second round).</summary>
        internal static WeaponDef Loaded(Vehicle v, int index)
        {
            var gun = v.Arms[index];
            return gun.HasRounds ? gun.RoundAt(v.Weapons[index].Round) : gun;
        }

        /// <summary>The index of the round the gun would load for this target: 0 its own, k its k-th second round.</summary>
        internal int RoundIndexFor(Vehicle v, WeaponDef gun, IDamageable target)
        {
            var rounds = gun.Rounds;
            var tiered = target is Vehicle { Tier: not AltitudeTier.None };
            var flying = tiered || IsFlying(target);
            for (var k = 0; k < rounds.Count; k++)
            {
                var r = rounds[k];
                if (!r.CarriedBy(v.Def) || (!tiered && !r.Round.CanTarget(flying))) continue;
                if (Suits(r, target, flying)) return k + 1;
            }
            return 0;
        }

        /// <summary>The round the gun would load for this target (for scoring targets: what it would hit it with).</summary>
        internal WeaponDef RoundAgainst(Vehicle v, WeaponDef gun, IDamageable target) =>
            gun.HasRounds ? gun.RoundAt(RoundIndexFor(v, gun, target)) : gun;

        /// <summary>
        /// The round a gun's rule gives a target, for a carrier without elite-only rounds (prompt 17 D.6's check, the tables):
        /// the mount itself loads by <see cref="KeepRound"/>, with its switch time and hold.
        /// </summary>
        internal WeaponDef RoundFor(WeaponDef gun, EntityId target, IDamageable? aimTarget)
        {
            if (!gun.HasRounds) return gun;
            var aimed = aimTarget;
            if (aimed == null && target.IsValid && _world.TryGetTarget(target, out var found)) aimed = found;
            if (aimed == null) return gun;
            var tiered = aimed is Vehicle { Tier: not AltitudeTier.None };
            var flying = tiered || IsFlying(aimed);
            foreach (var r in gun.Rounds)
                if (!r.EliteOnly && (tiered || r.Round.CanTarget(flying)) && Suits(r, aimed, flying)) return r.Round;
            return gun;
        }

        /// <summary>Whether a round's rule takes this target.</summary>
        private bool Suits(SecondRound r, IDamageable target, bool flying)
        {
            var use = r.Use;
            if (flying) return (use & RoundUse.Air) != 0;
            if ((use & RoundUse.Ground) != 0) return true;
            var vehicle = target as Vehicle;
            var structure = vehicle == null || vehicle.Def.Static || target.Armor == ArmorClass.Structure;
            if (structure) return (use & RoundUse.Structure) != 0;
            var front = target.Armour.Front;
            if ((use & RoundUse.Armour) != 0 && front > WeaponDef.HeArmourMax) return true;
            if ((use & RoundUse.Light) != 0 && front <= WeaponDef.HeArmourMax) return true;
            return (use & RoundUse.Cluster) != 0 && Clustered(vehicle!, r.Round);
        }

        /// <summary>Two more ground vehicles of the target's side inside the round's blast (4 m at least) round it.</summary>
        private bool Clustered(Vehicle target, WeaponDef round)
        {
            var reach = System.MathF.Max(4f, round.SplashRadius);
            var r2 = reach * reach;
            var near = 0;
            foreach (var other in _world.VehicleList)
            {
                if (other == target || !other.IsAlive || other.Team != target.Team || other.Flying) continue;
                if (Vector2.DistanceSquared(other.Position, target.Position) > r2) continue;
                if (++near >= 2) return true;
            }
            return false;
        }

        /// <summary>
        /// Keeps a mount's round for its target: a change due by now is finished (a magazine gun's new magazine is full);
        /// a target wanting another round starts a change once the round in has been in 2 s and no salvo or charge is under
        /// way. False while a change is under way: the mount fires nothing.
        /// </summary>
        private bool KeepRound(Vehicle v, int index, IDamageable? target)
        {
            var gun = v.Arms[index];
            if (!gun.HasRounds) return true;
            var s = v.Weapons[index];
            var now = _world.Time;
            if (s.Loading >= 0)
            {
                if (now < s.SwitchDoneAt) return false;
                s.Round = s.Loading;
                s.Loading = -1;
                s.LoadedAt = now;
                if (gun.Clip > 0) s.ClipLeft = gun.Clip;
            }
            if (target == null || s.BurstLeft > 0 || s.ChargeLeft > 0f) return true;
            var want = RoundIndexFor(v, gun, target);
            if (want == s.Round || now - s.LoadedAt < WeaponDef.RoundHoldSeconds) return true;
            var seconds = gun.SwitchSeconds(want > 0 ? gun.Rounds[want - 1] : null);
            s.Loading = want;
            s.SwitchDoneAt = now + seconds;
            _world.Emit(SimEvent.RoundSwitch(v, index, gun.RoundAt(want), seconds));
            return false;
        }

        /// <summary>The round in the gun can hit this target's layer (a flak round is for aircraft only, the AP round for the ground).</summary>
        private static bool LoadedReaches(Vehicle v, int index, IDamageable target)
        {
            if (!v.Arms[index].HasRounds || target is Vehicle { Tier: not AltitudeTier.None }) return true;
            return Loaded(v, index).CanTarget(IsFlying(target));
        }

        /// <summary>Prompt 25 G: the loaded rounds for the checkpoint's fingerprint (mounts with second rounds only).</summary>
        internal static void MixRounds(Vehicle v, System.Action<long> mix)
        {
            for (var i = 0; i < v.Weapons.Length && i < v.Arms.Length; i++)
            {
                if (!v.Arms[i].HasRounds) continue;
                var s = v.Weapons[i];
                mix(s.Round * 64 + s.Loading + 1);
            }
        }
    }
}
