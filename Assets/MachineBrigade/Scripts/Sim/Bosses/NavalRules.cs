#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>A coastal battery as the modes and the view see it (prompt 16 A.3).</summary>
    public readonly struct BatteryState
    {
        public BatteryState(string id, Vector2 at, int team, float progress, int progressTeam, EntityId gun)
        {
            Id = id;
            At = at;
            Team = team;
            Progress = progress;
            ProgressTeam = progressTeam;
            Gun = gun;
        }

        public string Id { get; }
        public Vector2 At { get; }

        /// <summary>Its holder, or -1 while it stands abandoned.</summary>
        public int Team { get; }

        /// <summary>How far a side has got taking it (0-1), and which side.</summary>
        public float Progress { get; }
        public int ProgressTeam { get; }

        /// <summary>The battery's gun (a fixed defence), or none while it is being rebuilt.</summary>
        public EntityId Gun { get; }
    }

    /// <summary>
    /// The sea's rules for one battle (prompt 16): what the modes and mutators set (the fleet's size, the
    /// sea's visibility) and what they read (the coastal batteries, who holds the lighthouse).
    /// </summary>
    public sealed class NavalRules
    {
        /// <summary>Vision out onto the sea (the "Sea storm" mutator: 0.55); 1 by default.</summary>
        public float SeaSight { get; set; } = 1f;

        /// <summary>More escorts and attack boats with a flagship (the "Fleet" mutator).</summary>
        public int ExtraEscorts { get; set; }
        public int ExtraRaiders { get; set; }

        /// <summary>The share of its fleet a flagship brings (Boss Rush: fewer, so the fight stays short).</summary>
        public float FleetShare { get; set; } = 1f;

        /// <summary>Seconds a side's ground vehicles must hold a battery alone to take it.</summary>
        public float CaptureSeconds { get; set; } = 10f;

        /// <summary>Seconds before a destroyed battery stands abandoned again.</summary>
        public float RebuildSeconds { get; set; } = 60f;

        internal readonly List<BatteryState> BatteryList = new();

        public IReadOnlyList<BatteryState> Batteries => BatteryList;

        /// <summary>Who holds the lighthouse (-1: nobody): its holder watches the sea and sees the ships' parts.</summary>
        public int LighthouseOwner { get; internal set; } = -1;

        /// <summary>The flagship on the sea now (Leviathan), or none.</summary>
        public EntityId Flagship { get; internal set; }

        /// <summary>Flagships that got away over the edge this battle.</summary>
        public int Escapes { get; internal set; }
    }
}
