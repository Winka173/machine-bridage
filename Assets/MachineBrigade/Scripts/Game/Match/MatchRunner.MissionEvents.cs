using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 23 A-D: what the Game shows of a mission's events for now: each event notice through the existing notice call
    /// (its countdown and direction in the words), and the weather an event turns, rolled in over the event's seconds. The
    /// lines come as Radio events (with their priority) through the radio. F.1's restyled queue, F.2's arrows (the sim's
    /// <see cref="MachineBrigade.Sim.Modes.EventState.Arrows"/>) and F.3's side-objective bar come in a later pass.
    /// Kept apart from MatchRunner.cs so the two change independently.
    /// </summary>
    public sealed partial class MatchRunner
    {
        private void MissionEventNotice(in SimEvent e)
        {
            if (e.DefId == null) return;
            var bearing = e.NoticeBearing;
            var dir = bearing switch
            {
                0 => Strings.Get("event.dir.front"),
                1 => Strings.Get("event.dir.left"),
                2 => Strings.Get("event.dir.right"),
                3 => Strings.Get("event.dir.rear"),
                _ => "",
            };
            var text = Strings.Format(e.DefId, ("seconds", UnityEngine.Mathf.CeilToInt(e.Value)), ("dir", dir));
            var warning = e.Priority <= LinePriority.Warning;
            // Prompt 23 F.1-F.2: the notice's icon by the event's kind, and its direction for the arrows (none: no arrow).
            var way = e.NoticeDirection;
            _hud.Toast(text, error: e.Team == EnemyTeam, seconds: warning ? 4f : 3f, kind: NoticeKindOf(e.DefId),
                direction: way.LengthSquared() > 0.01f ? way : (System.Numerics.Vector2?)null);
            if (warning) Haptics.Pulse(60, 160);
        }

        /// <summary>An event notice's icon, from its text key (event.&lt;group&gt;.&lt;...&gt;).</summary>
        private static NoticeKind NoticeKindOf(string key)
        {
            var group = key.StartsWith("event.") ? key.Substring(6).Split('.')[0] : "";
            return group switch
            {
                "enemy" or "ally" => NoticeKind.Reinforce,
                "air" => NoticeKind.AirRaid,
                "barrage" or "counter" => NoticeKind.Strike,
                "general" or "mini" => NoticeKind.Boss,
                "side" or "plan" => NoticeKind.Objective,
                "loot" or "supply" or "neutral" => NoticeKind.Crate,
                "weather" => NoticeKind.Weather,
                "blackout" or "intel" => NoticeKind.Area,
                _ => NoticeKind.Info,
            };
        }

        private void MissionWeather(in SimEvent e)
        {
            if (e.DefId == null || !System.Enum.TryParse<WeatherKind>(e.DefId, out var next)) return;
            ShiftWeatherTo(next, e.Value);
        }
    }
}
