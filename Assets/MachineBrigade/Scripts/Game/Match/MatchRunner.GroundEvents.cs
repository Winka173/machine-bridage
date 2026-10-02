using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 31 L3 (written blind; the lead compiles): the minimap marks of the events that change the battlefield. While such
    /// an event is warned (its 8-12 s) and while it runs, each of its places (<see cref="EventState.Marks"/>: the gate that
    /// shuts, the half the sandstorm rolls over, the towers the blackout shuts down, the pods' landing sites, the allied
    /// columns about to turn) is a warning ring on the minimap; the notice itself comes through the event notices.
    /// </summary>
    public sealed partial class MatchRunner
    {
        private void MinimapEventMarks(Minimap minimap)
        {
            foreach (var system in _world.MissionEvents)
                foreach (var s in system.States)
                {
                    if (s.Marks.Count == 0 || (s.Phase != EventPhase.Warned && s.Phase != EventPhase.Running)) continue;
                    if (!MissionEventSystem.ChangesGround(s.Def.Kind)) continue;
                    foreach (var (at, radius) in s.Marks) minimap.Warning(new UnityEngine.Vector2(at.X, at.Y), radius);
                }
        }
    }
}
