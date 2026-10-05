#nullable enable
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>AI MASTER P3 spec 149: the internal stance its squad gives it (AttackAnything when not in a squad).</summary>
        internal UnitStance P3Stance = UnitStance.AttackAnything;

        /// <summary>AI MASTER P3 spec 200: a target handed to this vehicle (better suited) and one handed away, until <see cref="P3HandoffUntil"/>.</summary>
        internal EntityId P3Prefer, P3Avoid;
        internal double P3HandoffUntil = double.NegativeInfinity;

        /// <summary>AI MASTER P3 spec 141: the asset an anti-air vehicle covers (null: none assigned).</summary>
        internal Vector2? P3CoverAt;
        internal float P3CoverRadius;
    }
}
