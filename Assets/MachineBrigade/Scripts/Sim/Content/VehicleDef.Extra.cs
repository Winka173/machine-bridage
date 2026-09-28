#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 8's vehicle data: the equipment branch, the breacher's and the SP gun's mechanisms, the
    /// elite's army cost, and the new bosses' parts, lock, boring, landings, emplacements and attached
    /// models. Kept apart from Definitions.cs so the two grow without stepping on each other.
    /// </summary>
    public sealed partial class VehicleDef
    {
        /// <summary>The army branch whose equipment loadout it wears (see <see cref="ArmyBranch"/>).</summary>
        public ArmyBranch Branch { get; internal set; }

        /// <summary>Share of a mine's blast that gets through (the armoured bulldozer's belly plate: 0.5).</summary>
        public float MineArmor { get; internal set; } = 1f;

        /// <summary>
        /// A breacher (the armoured bulldozer): it rams and ploughs structures down (its main weapon is
        /// the blade), flattens dragon's teeth it is sent at, and the commander sends it ahead of the
        /// line into an enemy base.
        /// </summary>
        public bool Breacher { get; internal set; }

        /// <summary>Shoot-and-scoot (the SP howitzer), or null.</summary>
        public ScootDef? Scoot { get; internal set; }

        /// <summary>
        /// Its main weapon's spread against a target its side has marked (a laser designator's mark, a
        /// counter-battery radar's reveal, a UAV scan over it) is multiplied by this (1: no change).
        /// </summary>
        public float MarkedSpread { get; internal set; } = 1f;

        /// <summary>A multi-part boss's parts (empty: none).</summary>
        public IReadOnlyList<BossPartDef> Parts { get; internal set; } = Array.Empty<BossPartDef>();

        /// <summary>The body is shut to damage until enough of one kind of part has broken, or null.</summary>
        public PartLockDef? PartLock { get; internal set; }

        /// <summary>A boring boss, or null.</summary>
        public BurrowDef? Burrow { get; internal set; }

        /// <summary>A landing-craft boss, or null.</summary>
        public LandingDef? Landing { get; internal set; }

        /// <summary>Emplacements it arrives with.</summary>
        public IReadOnlyList<GuardDef> Guards { get; internal set; } = Array.Empty<GuardDef>();

        /// <summary>Extra models drawn fixed to it (view only).</summary>
        public IReadOnlyList<AttachmentDef> Attachments { get; internal set; } = Array.Empty<AttachmentDef>();

        /// <summary>Its general's radio line (a text key) when it arrives, or null.</summary>
        public string? RadioSpawn { get; internal set; }

        /// <summary>The index of a part by id, or -1.</summary>
        public int PartIndex(string id)
        {
            for (var i = 0; i < Parts.Count; i++)
                if (Parts[i].Id == id) return i;
            return -1;
        }
    }
}
