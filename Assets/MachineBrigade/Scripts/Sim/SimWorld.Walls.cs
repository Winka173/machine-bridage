#nullable enable
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Sim
{
    /// <summary>Prompt 32 L3: the bases' walls (<see cref="WallSystem"/>), made on first use.</summary>
    public sealed partial class SimWorld
    {
        private WallSystem? _walls;

        public WallSystem Walls => _walls ??= new WallSystem(this);

        /// <summary>Whether any wall line was built (the slow-aura pass and the AI look only then).</summary>
        public bool HasWalls => _walls != null && _walls.Lines.Count > 0;

        /// <summary>Prompt 32 L7: Showdown's catch-up is income only (no kill pay by the odds, no free reinforcement).</summary>
        public bool CatchUpIncomeOnly { get; set; }

        /// <summary>Prompt 32 L7: Showdown's escalation at minute 6: the CP relays stop paying.</summary>
        public bool RelaysOff { get; set; }

        /// <summary>
        /// Prompt 32 L7: Showdown's anti-snipe and its sudden-death count: a hook on the damage an HQ takes (target, the hit,
        /// the damage after every other rule) returning what it takes; null: none.
        /// </summary>
        internal System.Func<Entities.Vehicle, Combat.HitInfo, float, float>? HqDamageRule { get; set; }
    }
}
