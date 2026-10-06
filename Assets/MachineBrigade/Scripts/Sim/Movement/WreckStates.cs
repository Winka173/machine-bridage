#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// MVA W1-B (spec part AO, DECISIONS "Map/visual/audio W1-B (lane B)"): a destroyed vehicle's wreck state, shared by the
    /// Sim (<see cref="WreckField"/>: what blocks movement) and the view (WreckManager: what is drawn), so a visible solid
    /// wreck always blocks and an invisible one never does.
    /// </summary>
    public enum WreckState
    {
        /// <summary>Not destroyed (or never left a wreck).</summary>
        Alive,

        /// <summary>The first seconds: the death blast, the hull bucking, a turret thrown; already solid in the Sim.</summary>
        DestroyedAnimating,

        /// <summary>A burning or smouldering hulk: solid (drivers steer round it, routes pay it as a wall).</summary>
        BlockingWreck,

        /// <summary>Sinking into the ground or gone under, a burn mark: passable, never blocks.</summary>
        PassableRubble,

        /// <summary>Nothing left (the view object destroyed, the Sim entry gone).</summary>
        Removed,
    }

    /// <summary>What each wreck state has (spec part AO: collider, nav obstacle, visual mesh, fire/smoke, salvage).</summary>
    public readonly struct WreckStateContract
    {
        public WreckStateContract(WreckState state, bool collider, bool navObstacle, bool visualMesh, bool fireSmoke, bool salvage)
        {
            State = state;
            Collider = collider;
            NavObstacle = navObstacle;
            VisualMesh = visualMesh;
            FireSmoke = fireSmoke;
            Salvage = salvage;
        }

        public WreckState State { get; }

        /// <summary>Pushes vehicles out (MovementSystem.Separate) and stops a drive into it.</summary>
        public bool Collider { get; }

        /// <summary>Paid as a wall by planned routes (UnitCostField) and steered round.</summary>
        public bool NavObstacle { get; }

        /// <summary>The hulk is drawn (full or simplified, never hidden while solid).</summary>
        public bool VisualMesh { get; }

        /// <summary>May burn or smoke (a simplified far hulk may be out).</summary>
        public bool FireSmoke { get; }

        /// <summary>The game has no salvage yet; kept for the contract (always false).</summary>
        public bool Salvage { get; }
    }

    public static class WreckStates
    {
        /// <summary>How long a wreck counts as freshly destroyed (its death show) before it is a plain hulk, s.</summary>
        public const double AnimatingSeconds = 2.5;

        private static readonly WreckStateContract[] Table =
        {
            new(WreckState.Alive, false, false, false, false, false),
            new(WreckState.DestroyedAnimating, true, true, true, true, false),
            new(WreckState.BlockingWreck, true, true, true, true, false),
            new(WreckState.PassableRubble, false, false, true, false, false),
            new(WreckState.Removed, false, false, false, false, false),
        };

        public static WreckStateContract Contract(WreckState state) => Table[(int)state];

        /// <summary>Whether the Sim blocks in this state (collider or nav obstacle).</summary>
        public static bool Blocks(WreckState state) => Contract(state).Collider || Contract(state).NavObstacle;

        /// <summary>
        /// The view and Sim agree: a solid Sim wreck is drawn (never "invisible but blocking"), and a drawn solid-looking hulk
        /// (not sinking) is solid in the Sim unless it never blocks at all (aircraft, defences, walls: WreckField.Leaves).
        /// </summary>
        public static bool InSync(WreckState sim, WreckState view, bool leavesSolidWreck)
        {
            if (Blocks(sim) && !Contract(view).VisualMesh) return false;
            if (leavesSolidWreck && Blocks(view) && !Blocks(sim)) return false;
            return true;
        }

        /// <summary>A wreck's state in the Sim at <paramref name="now"/>: in the field (animating, then blocking), else rubble or gone.</summary>
        public static WreckState Of(WreckField field, EntityId id, double now, bool destroyed)
        {
            if (!destroyed) return WreckState.Alive;
            var list = field.List;
            for (var i = 0; i < list.Count; i++)
            {
                if (list[i].Id != id) continue;
                return !double.IsNaN(list[i].Since) && now - list[i].Since < AnimatingSeconds ? WreckState.DestroyedAnimating : WreckState.BlockingWreck;
            }
            return WreckState.PassableRubble;
        }
    }
}
