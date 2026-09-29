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
            _hud.Toast(text, error: e.Team == EnemyTeam, seconds: warning ? 4f : 3f);
            if (warning) Haptics.Pulse(60, 160);
        }

        private void MissionWeather(in SimEvent e)
        {
            if (e.DefId == null || !System.Enum.TryParse<WeatherKind>(e.DefId, out var next)) return;
            ShiftWeatherTo(next, e.Value);
        }
    }
}
