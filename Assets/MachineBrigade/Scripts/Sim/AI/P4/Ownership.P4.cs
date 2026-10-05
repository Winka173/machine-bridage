#nullable enable
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P4, P3 leftover (a): one owner orders a gun at a time. A P3 fire mission or scoot claims the gun on the
    /// side's intent ownership; TacticalAi.DirectArtillery then runs only its safety branches (a threat inside the minimum
    /// range) for it, and claims the guns it ordered itself, so the fire mission's stale-target drop never cancels them.
    /// </summary>
    public sealed partial class AiCommander
    {
        /// <summary>Claims <paramref name="gun"/> for <paramref name="owner"/> (true with P4 off: P3 behaviour).</summary>
        private bool ClaimGunP4(SimWorld world, Vehicle gun, IntentOwner owner, float seconds)
        {
            if (PlanningP4 is not { } tp) return true;
            var now = world.Time;
            if (tp.Ownership.Claim(gun.Id.Value, owner, now + seconds, now)) return true;
            tp.Metrics.GunOwnershipBlocks++;
            if (LogDue(0x6000 + (gun.Id.Value & 0xfff), 10.0))
                P4Reasons.Unit(world, gun, DecisionKind.Target, P4Reasons.GunOwned, $"{tp.Ownership.Owner(gun.Id.Value, now)} holds it; {owner} waits");
            return false;
        }

        private bool GunHeldByOtherP4(SimWorld world, Vehicle gun, IntentOwner owner) =>
            PlanningP4 is { } tp && tp.Ownership.HeldByOther(gun.Id.Value, owner, world.Time);
    }

    public sealed partial class TacticalAi
    {
        private TeamPlanning? PlanningP4(SimWorld world) =>
            Tun.Planning.Enabled && Tun.Coordination.Enabled ? world.CoordinationIfAny?.Peek(_team)?.PlanningIfAny : null;

        /// <summary>A P3 fire mission / scoot owns the gun now (DirectArtillery keeps to its safety branches).</summary>
        private bool MissionOwnsGunP4(SimWorld world, Vehicle gun)
        {
            if (PlanningP4(world) is not { } tp) return false;
            var o = tp.Ownership.Owner(gun.Id.Value, world.Time);
            return o == IntentOwner.FireMission || o == IntentOwner.Scoot;
        }

        /// <summary>DirectArtillery gave the gun an order: it owns it a moment (the fire mission's stale drop leaves it).</summary>
        private void ClaimGunP4(SimWorld world, Vehicle gun)
        {
            if (PlanningP4(world) is not { } tp) return;
            var now = world.Time;
            tp.Ownership.Claim(gun.Id.Value, IntentOwner.Tactical, now + 2.0, now);
        }
    }
}
