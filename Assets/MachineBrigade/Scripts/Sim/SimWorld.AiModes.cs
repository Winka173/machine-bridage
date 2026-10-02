#nullable enable
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// Prompt 28 appendix B: the battle's AI profile (<see cref="AiModeProfile"/>) from its mode tag and mission goal, the
    /// mission's alarm and phase that switch it, and the ceasefire factions no fire may hurt.
    /// </summary>
    public sealed partial class SimWorld
    {
        private AiModeProfile? _aiProfile;
        private string? _missionGoal;
        private readonly List<string> _profileFlags = new();

        /// <summary>The campaign mission's goal (MissionDef.MissionGoal's name); null outside the campaign.</summary>
        public string? MissionGoal
        {
            get => _missionGoal;
            set
            {
                _missionGoal = value;
                _aiProfile = null;
            }
        }

        /// <summary>The fixed deck's special-rule flags on top of the mission type's profile (prompt 31).</summary>
        public void AddProfileFlags(IEnumerable<string> flags)
        {
            _profileFlags.AddRange(flags);
            _aiProfile = null;
        }

        /// <summary>The recon / infiltration alarm: the enemy knows; profiles switch by their "alert" phase override.</summary>
        public bool Alarm { get; private set; }

        /// <summary>The mode's current named phase ("step:build", "phase:2"), for phase overrides; null: none.</summary>
        public string? AiPhase { get; private set; }

        public void RaiseAlarm()
        {
            if (Alarm) return;
            Alarm = true;
            _aiProfile = null;
            AiLog.Add(new AI.DecisionEntry(Time, -1, AI.AiLayer.Commander, 0, AI.DecisionKind.Plan, "alarm"));
        }

        public void SetAiPhase(string? phase)
        {
            if (AiPhase == phase) return;
            AiPhase = phase;
            _aiProfile = null;
        }

        /// <summary>The profile the AI plays now: the mode's (or mission type's), then the alarm's override.</summary>
        public AiModeProfile AiProfile
        {
            get
            {
                if (_aiProfile != null) return _aiProfile;
                var profiles = Catalog.AiModes;
                var p = profiles.For(ModeTag, MissionGoal);
                if (Alarm)
                    foreach (var o in p.PhaseOverrides)
                        if (o.When == "alert" && o.Profile != null && profiles.Profiles.TryGetValue(o.Profile, out var next))
                        {
                            p = next;
                            break;
                        }
                if (_profileFlags.Count > 0) p = p.WithFlags(_profileFlags);
                return _aiProfile = p;
            }
        }

        /// <summary>The stall policy now: the profile's, or its override for the current phase.</summary>
        public StallPolicy Stall
        {
            get
            {
                var p = AiProfile;
                if (AiPhase != null)
                    foreach (var o in p.PhaseOverrides)
                        if (o.When == AiPhase && o.Stall is { } s) return s;
                return p.Stall == StallPolicy.Inherit ? StallPolicy.Both : p.Stall;
            }
        }

        /// <summary>The team that holds (never pushed off by stall pressure), or null when both attack.</summary>
        public int? DefenderTeam => AiProfile.Defender switch { "ai" => 1, "player" => 0, _ => null };

        /// <summary>Whether a side may call fire support now (supportPolicy: none before the alarm on recon).</summary>
        public bool SupportAllowed => AiProfile.Support != SupportPolicy.DisabledUntilAlert || Alarm;

        // ------------------------------------------------------------------------------------------------ ceasefire

        private readonly HashSet<int> _ceasefire = new();

        /// <summary>The ceasefire factions: no other team's fire, strike or splash hurts them (DamageSystem.Apply).</summary>
        public IReadOnlyCollection<int> CeasefireTeams => _ceasefire;

        public void SetCeasefire(int team, bool on)
        {
            if (on) _ceasefire.Add(team);
            else _ceasefire.Remove(team);
        }

        /// <summary>Whether damage from <paramref name="sourceTeam"/> to <paramref name="targetTeam"/> is held by a ceasefire.</summary>
        public bool Ceasefire(int sourceTeam, int targetTeam) => targetTeam != sourceTeam && _ceasefire.Contains(targetTeam);

        // ------------------------------------------------------------------------------------------------ escort

        /// <summary>Escort / evacuation: where the convoy's trucks are, for the safe zone auto support keeps clear of.</summary>
        public System.Func<IEnumerable<System.Numerics.Vector2>>? ConvoySafeZone { get; set; }

        /// <summary>Whether a blast of <paramref name="radius"/> at <paramref name="at"/> would reach the convoy's safe zone.</summary>
        public bool InConvoySafeZone(System.Numerics.Vector2 at, float radius)
        {
            if (ConvoySafeZone == null || AiProfile.Escort is not { } escort) return false;
            var reach = radius + escort.SafeZoneRadius;
            foreach (var p in ConvoySafeZone())
                if (System.Numerics.Vector2.DistanceSquared(p, at) <= reach * reach) return true;
            return false;
        }
    }
}
