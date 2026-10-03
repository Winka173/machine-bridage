using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 22 D.4: the enemy general answers the way the player fights. It watches what the player sends (aircraft,
    /// drones, artillery), what the player loses, and a boss's big attack broken in time, and at the end how fast the win
    /// came; each moment is said once a battle, a little apart, by the mission's general if they have lines for it. Which of
    /// a general's lines is said is fixed by the mission and the moment (no dice), so a replay hears the same. Presentation
    /// only: nothing here touches the battle.
    /// </summary>
    public sealed class ReactiveRadio
    {
        public const string Fast = "fast", Losses = "losses", Air = "air", Drones = "drones", Artillery = "artillery", Interrupt = "interrupt";

        /// <summary>The moments, in the order they are checked when several come at once.</summary>
        public static readonly string[] Moments = { Interrupt, Losses, Air, Drones, Artillery, Fast };

        /// <summary>At least this long between two of these lines.</summary>
        public const double Gap = 25.0;

        /// <summary>Cards sent before the mix of the army counts, and each kind's share and count to be "a lot".</summary>
        public const int MixAfter = 8;

        public const float AirShare = 0.35f, DroneShare = 0.30f, ArtilleryShare = 0.40f;
        public const int KindAtLeast = 4;

        private readonly MissionDef _mission;
        private readonly string _general;
        private readonly HashSet<string> _said = new();
        private double _last = -Gap;
        private bool _interrupted;

        public ReactiveRadio(MissionDef mission)
        {
            _mission = mission;
            _general = mission?.General is { } g && Speaks(g) ? g : null;
        }

        public int Sent { get; private set; }
        public int SentAir { get; private set; }
        public int SentDrones { get; private set; }
        public int SentArtillery { get; private set; }
        public int Lost { get; private set; }

        /// <summary>Whether a general has reactive lines.</summary>
        public static bool Speaks(string general) => System.Array.IndexOf(Narrative.ReactGenerals, general) >= 0;

        /// <summary>A drone card: a drone, or a truck or aircraft that carries them.</summary>
        public static bool IsDroneCard(VehicleDef def) =>
            def.Drone || def.Id.Contains("drone") || def.Id is "fpv_carrier" or "shahed_truck" or "swarm_carrier";

        /// <summary>The player sent a vehicle into the battle.</summary>
        public void Deployed(VehicleDef def)
        {
            if (def == null || def.Boss) return;
            Sent++;
            if (IsDroneCard(def)) SentDrones++;
            else if (def.Flying) SentAir++;
            if (def.Class == UnitClass.Artillery) SentArtillery++;
        }

        /// <summary>A vehicle of the player's was destroyed.</summary>
        public void LostOne() => Lost++;

        /// <summary>The player broke a boss's big attack in time.</summary>
        public void Interrupted() => _interrupted = true;

        /// <summary>Losses the general calls heavy: a few more than the mission's third star allows (8 when it has none).</summary>
        public int HeavyLosses => System.Math.Max(8, _mission != null && _mission.StarLosses >= 0 ? _mission.StarLosses + 2 : 8);

        /// <summary>A win the general calls fast: within 60% of the second star's time (four minutes when it has none).</summary>
        public double FastWin => _mission != null && _mission.StarTime > 0f ? _mission.StarTime * 0.6 : 240.0;

        /// <summary>The moment the battle has reached now, not said yet (null: none, or too soon after the last).</summary>
        public string Due(double time)
        {
            if (_general == null || time - _last < Gap) return null;
            foreach (var moment in Moments)
                if (moment != Fast && !_said.Contains(moment) && Reached(moment)) return moment;
            return null;
        }

        private bool Reached(string moment) => moment switch
        {
            Interrupt => _interrupted,
            Losses => Lost >= HeavyLosses,
            Air => Sent >= MixAfter && SentAir >= KindAtLeast && SentAir >= Sent * AirShare,
            Drones => Sent >= MixAfter && SentDrones >= KindAtLeast && SentDrones >= Sent * DroneShare,
            Artillery => Sent >= MixAfter && SentArtillery >= KindAtLeast && SentArtillery >= Sent * ArtilleryShare,
            _ => false,
        };

        /// <summary>The line due now (a text key), marked said; null when nothing is.</summary>
        public string Next(double time)
        {
            var moment = Due(time);
            if (moment == null) return null;
            _said.Add(moment);
            _last = time;
            return Key(_general, moment, _mission.Id);
        }

        /// <summary>At the win: the general's line for a fast one (null when the win was not fast).</summary>
        public string OnWin(double time)
        {
            if (_general == null || time > FastWin || !_said.Add(Fast)) return null;
            return Key(_general, Fast, _mission.Id);
        }

        /// <summary>Which of the general's lines for a moment a mission hears: fixed by the mission and the moment.</summary>
        public static string Key(string general, string moment, string missionId)
        {
            var hash = 2166136261u;
            foreach (var c in missionId + "/" + moment) hash = (hash ^ c) * 16777619u;
            return $"radio.{general}.react.{moment}.{hash % Narrative.ReactLines + 1}";
        }
    }
}
