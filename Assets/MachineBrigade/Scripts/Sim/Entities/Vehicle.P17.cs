#nullable enable
using System;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Prompt 17 C: a deploying vehicle's state (the bunker vehicle).</summary>
    public enum DeployState
    {
        /// <summary>On its tracks: it drives, and its turret keeps to the front arc.</summary>
        Mobile,

        /// <summary>Digging in: it neither drives nor fires, and keeps its moving armour.</summary>
        Deploying,

        /// <summary>Dug in: thicker front, longer reach, turret all round; it cannot drive.</summary>
        Deployed,

        /// <summary>Packing up: it neither drives nor fires, and has its moving armour again.</summary>
        Packing,
    }

    public sealed partial class Vehicle
    {
        // ------------------------------------------------------------------ shield dome

        /// <summary>The dome's hit points left (its emitter's; see <see cref="DomeDef"/>).</summary>
        internal float DomeHp;

        /// <summary>When the dome last took a hit or broke: it is back at full <see cref="DomeDef.Recharge"/> seconds later.</summary>
        internal double DomeHitAt = double.NegativeInfinity;

        /// <summary>Its dome has been filled for the first time (a unit arrives with its dome up).</summary>
        internal bool DomeInit;

        /// <summary>The emitter's dome is up (it has hit points left and the emitter is alive and not stunned).</summary>
        public bool DomeUp => Def.Dome != null && IsAlive && DomeHp > 0f && !Stunned;

        /// <summary>The dome's hit points left over its full hit points (0 when down).</summary>
        public float DomeShare => DomeUp ? Math.Clamp(DomeHp / MathF.Max(1f, Abilities.DomeSystem.Full(this)), 0f, 1f) : 0f;

        // ------------------------------------------------------------------ deploying

        /// <summary>Whether it is on its tracks, digging in, dug in or packing up.</summary>
        public DeployState Deploy { get; internal set; }

        /// <summary>When it began digging in or packing up, and when that will be done.</summary>
        internal double DeployFrom, DeployUntil;

        /// <summary>Play-test 5 (DECISIONS 20W): a jet on an enemy jet's tail with its nose on it (its cannon streams on).</summary>
        public bool OnTail { get; internal set; }

        /// <summary>
        /// Play-test 6 (DECISIONS 21F): a jet in a dogfight that came out of the merge the worse placed (the enemy jet
        /// hunting it is further astern of it than it is of the enemy): it runs out, jinking, instead of turning with it.
        /// </summary>
        public bool Defending { get; internal set; }

        /// <summary>Play-test 6: a jet low on health breaking off a dogfight (it flies away from the enemy jet).</summary>
        public bool BreakingOff { get; internal set; }

        /// <summary>Play-test 5: since when a sieged tank has had enemies inside its mortar's minimum reach and nothing to shell (NaN: not).</summary>
        internal double SiegeCrowdedSince = double.NaN;

        /// <summary>The share of digging in or packing up done (1 dug in or mobile).</summary>
        public float DeployProgress(double now) =>
            Deploy is DeployState.Deploying or DeployState.Packing && DeployUntil > DeployFrom
                ? (float)Math.Clamp((now - DeployFrom) / (DeployUntil - DeployFrom), 0.0, 1.0) : 1f;

        /// <summary>Digging in, dug in or packing up: it cannot drive.</summary>
        internal bool DeployHolds => Def.Deploy != null && Deploy != DeployState.Mobile;

        /// <summary>Digging in or packing up: it cannot fire either.</summary>
        internal bool DeployBusy => Deploy is DeployState.Deploying or DeployState.Packing;

        // ------------------------------------------------------------------ wingman

        /// <summary>The manned aircraft this wingman escorts (none: it patrols the front).</summary>
        public EntityId WingLeader { get; internal set; }

        /// <summary>When the wingman looks for its leader again.</summary>
        internal double WingCheckAt;
    }
}
