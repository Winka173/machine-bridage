#nullable enable

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>
        /// Prompt 32 L4: a Garrison HQ's reaction squad. It counts against its side's army cap and entity budget, but
        /// never in the army value supply reads; destroying it pays no CP to anyone and scores no Deathmatch points;
        /// it keeps to the base region (its post) and the side's AI leaves it alone.
        /// </summary>
        public bool Garrison { get; internal set; }

        /// <summary>Prompt 32 L4: a Shield HQ's point defence reloads at this pace (its HQ level's share of a medium C-RAM's).</summary>
        internal float ApsRate = 1f;
    }
}
