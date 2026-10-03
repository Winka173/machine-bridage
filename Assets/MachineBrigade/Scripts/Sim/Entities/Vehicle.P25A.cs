#nullable enable
using System.Numerics;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// Prompt 25 F2 batch A (DECISIONS 25F2-A): the runtime state of the new units and structures (run by
    /// Abilities.FieldWorksSystem and CombatSystem.P25A).
    /// </summary>
    public sealed partial class Vehicle
    {
        /// <summary>An inflatable decoy: the sides that have found it out (a bit per team); they no longer shoot at it.</summary>
        public int DecoyExposedMask { get; internal set; }

        /// <summary>Whether <paramref name="team"/> knows this decoy for what it is.</summary>
        public bool DecoyExposedTo(int team) => team is >= 0 and < 31 && (DecoyExposedMask & (1 << team)) != 0;

        /// <summary>A tower linked by a fire-control centre this step: it hits harder by <see cref="LinkDamage"/> and gangs up with the others.</summary>
        public bool FireLinked { get; internal set; }

        /// <summary>A linked tower's damage multiplier (1: not linked).</summary>
        internal float LinkDamage = 1f;

        /// <summary>Play-test 14: the side's base aura buildings' lifts on this unit (1: none), set each step by FieldWorksSystem.</summary>
        internal float AuraDamage = 1f, AuraSpeed = 1f, AuraHp = 1f, AuraRange = 1f;

        /// <summary>The weapons' ranges before the range aura (taken the first time it applies).</summary>
        internal float[]? AuraBaseRange;
        /// <summary>Play-test 14: since when a launcher's erector has been coming up, and when it last had a target.</summary>
        internal double ErectFrom = double.NegativeInfinity, ErectLast = double.NegativeInfinity;

        /// <summary>Play-test 14 session 5: the same for a side ATGM box's erector (<see cref="Content.VehicleDef.SideErectSeconds"/>).</summary>
        internal double SideErectFrom = double.NegativeInfinity, SideErectLast = double.NegativeInfinity;

        /// <summary>A microwave's next pulse, a flare tower's next flare.</summary>
        internal double WorksNextAt;

        /// <summary>A reconnaissance jet's run: its heading once set, and its next strip of reveal.</summary>
        internal bool PassStarted;

        internal float PassHeading;
        internal double PassNextScan;

        /// <summary>A multiple-rounds-simultaneous-impact salvo: when its first round lands (every round of the salvo lands then).</summary>
        internal double MrsiLands = double.NegativeInfinity;

        /// <summary>A stand-off bomber turning away from its target after the release (until it is out beyond its reach).</summary>
        internal bool GlideTurning;

        /// <summary>Where a falling paradrop stand-in will land its vehicle (see <see cref="IsPod"/>).</summary>
        internal Vector2 DropAt;

        internal string? DropUnit;

        /// <summary>When it joined the battle.</summary>
        internal double SpawnedAt;
    }
}
