#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Prompt 20 (DECISIONS 19E): the new bosses' runtime state.</summary>
    public sealed partial class Vehicle
    {
        /// <summary>The share of its pod bays still standing (Daedalus's three): fewer, slower drops.</summary>
        internal float PodShare = 1f;

        /// <summary>Its workshop doors: every one broken (it builds no more), and the share standing.</summary>
        internal bool FactoryOff;

        internal float FactoryShare = 1f;
        internal double FactoryNext = double.PositiveInfinity;
        internal double FactoryStart;
        internal int FactoryBuilt;

        /// <summary>The vehicles its workshop built (the cap counts those alive).</summary>
        internal readonly List<EntityId> Built = new();

        /// <summary>Its crusher broken (Kronos's bucket wheel).</summary>
        internal bool CrushOff;
        internal double DebrisNext;

        /// <summary>Its fire-direction radar broken (Argus): its side's artillery scatters as usual.</summary>
        internal bool SpotOff;

        /// <summary>Its own route (the battlefield's, by name) and the waypoint it drives to.</summary>
        internal IReadOnlyList<Vector2>? OwnRoute;

        internal int OwnRouteAt;
        internal double RouteDriven = double.NegativeInfinity;

        /// <summary>Its body takes no damage now, only its parts (a submarine up for a launch: only the doors show).</summary>
        internal bool BodyShut;

        /// <summary>A diving boss stays under at least until then.</summary>
        internal double BurrowUntil;

        /// <summary>Prompt 20 J.2: a charge under way (Ixion's): along the line from its start to its end, until then.</summary>
        internal bool Charging;

        internal Vector2 ChargeFrom, ChargeTo;
        internal double ChargeStart, ChargeEnd;
        internal readonly HashSet<EntityId> ChargeHit = new();

        /// <summary>A skimmer's pass (Caspian): in along the near lane until then, then away.</summary>
        internal double PassUntil;

        internal bool PassIn = true;

        /// <summary>Prompt 20 E.5: this is a mini boss (its rank), for the HUD and the rewards.</summary>
        public bool IsMiniBoss => Def.MiniBoss;

        /// <summary>A charge under way (the view leans it forward and throws dust).</summary>
        public bool IsCharging => Charging;
    }
}
