#nullable enable

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>
        /// AI MASTER P0-C (spec 48): a moving boss's brain (mission anchor, hull vs turrets, naval steering, escorts, cadence);
        /// null for every other vehicle and for a fixed boss. Made by <see cref="Bosses.BossSystem.Joined"/>.
        /// </summary>
        internal Bosses.BossBrain? Brain;

        /// <summary>AI MASTER P0-C: the boss brain's debug and log state (section 96); null for a vehicle without a brain.</summary>
        public Bosses.BossBrain? BossBrain => Brain;
    }
}
