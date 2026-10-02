using MachineBrigade.Game.Hud;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 33 L5 (written blind; the lead compiles): the rails' warnings on the minimap. The stretch of line a train will
    /// cover in the next few seconds (a support train announced at the gate from 5.5 s before it comes in) and every level
    /// crossing that is not open are warning rings (<see cref="MachineBrigade.Sim.Movement.RailSystem.Dangers"/>); a boss
    /// train bearing down on a crossing also sounds the siren with its notice (a fortress alarm, "toast.railBoss").
    /// </summary>
    public sealed partial class MatchRunner
    {
        private void MinimapRailMarks(Minimap minimap)
        {
            var dangers = _world.Rails.Dangers;
            for (var i = 0; i < dangers.Count; i++)
            {
                var (centre, radius, _) = dangers[i];
                minimap.Warning(new UnityEngine.Vector2(centre.X, centre.Y), radius);
            }
        }
    }
}
