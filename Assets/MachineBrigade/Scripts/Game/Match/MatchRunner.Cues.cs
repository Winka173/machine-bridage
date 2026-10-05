using MachineBrigade.Game.Hud;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// AI MASTER P5 (spec 215): the AI's tactical communication cues the planner records (SimWorld.CuesOf) shown as short radio
    /// notices, so the AI's coordination is visible. An allied AI's cues are all shown; of an enemy AI's only the coordinated
    /// attack's "go" (radio chatter heard as it starts), never its probes, feints or flanks (that would give its plan away).
    /// Presentation only: nothing here reaches the simulation. Kept apart from MatchRunner.cs.
    /// </summary>
    public sealed partial class MatchRunner
    {
        private readonly double[] _cueSeen = { double.NegativeInfinity, double.NegativeInfinity, double.NegativeInfinity };

        private void ShowCuesP5()
        {
            if (_menu || _world == null || _hud == null) return;
            for (var team = 0; team < _cueSeen.Length; team++)
            {
                var cues = _world.CuesOf(team);
                if (cues.Count == 0) continue;
                var ally = team == PlayerTeam;
                foreach (var cue in cues)
                {
                    if (cue.Time <= _cueSeen[team]) continue;
                    _cueSeen[team] = cue.Time;
                    var key = (ally ? "cue.ally." : "cue.enemy.") + cue.Kind;
                    if (!Strings.Has(key)) continue;
                    _hud.Toast(Strings.Get(key), error: !ally, seconds: 2.5f, kind: NoticeKind.Info);
                }
            }
        }
    }
}
