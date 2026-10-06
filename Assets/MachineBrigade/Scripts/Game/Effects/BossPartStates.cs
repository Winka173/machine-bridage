using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>MVA W2-B (spec part Y): a breakable boss part's damage state.</summary>
    public enum PartDamageState
    {
        Healthy,
        Damaged,
        Critical,
        Destroyed,
    }

    /// <summary>
    /// MVA W2-B (spec parts Y, AH, AN; DECISIONS "Map/visual/audio W2 (lane B)"): the boss part damage-state contract, one
    /// place for the thresholds the part effects already used (prompt 9 C) and the states' looks:
    /// <list type="table">
    /// <item><term>Healthy</term><description>at or above <see cref="DamagedBelow"/> of its health: as built.</description></item>
    /// <item><term>Damaged</term><description>under half: the part's own renderers sooted (<see cref="Tint"/>), thin smoke
    /// and sparks (EffectsDirector.Puffs).</description></item>
    /// <item><term>Critical</term><description>under a quarter: scorched dark with a hot cast, thick smoke, a fire point
    /// on it, sparks; its audio cue (a strained-metal hit at Boss priority, once on entering).</description></item>
    /// <item><term>Destroyed</term><description>broken: its nodes hidden and its broken piece in place (VehicleView), the
    /// blast by what it is, fire and a smoke column, the HUD icon crossed out.</description></item>
    /// </list>
    /// The material state is on the model itself (tinted shared copies, MaterialLibrary.Tinted: never a property block on
    /// MachineBrigade/Lit), so a part's state stays readable on the Low preset (which halves the smoke) and when its effects
    /// are culled (spec part AN: never remove boss weakpoint state). Cosmetic props need none of this (spec part Y).
    /// </summary>
    public static class BossPartStates
    {
        public const float DamagedBelow = 0.5f;
        public const float CriticalBelow = 0.25f;

        public static PartDamageState Of(float share, bool broken) =>
            broken ? PartDamageState.Destroyed
            : share < CriticalBelow ? PartDamageState.Critical
            : share < DamagedBelow ? PartDamageState.Damaged
            : PartDamageState.Healthy;

        /// <summary>The multiply a state puts on the part's own renderers (over the hull's tint).</summary>
        public static Vector3 Tint(PartDamageState state) => state switch
        {
            PartDamageState.Damaged => new Vector3(0.8f, 0.78f, 0.76f),
            PartDamageState.Critical => new Vector3(0.7f, 0.55f, 0.48f),
            _ => Vector3.one,
        };
    }
}
