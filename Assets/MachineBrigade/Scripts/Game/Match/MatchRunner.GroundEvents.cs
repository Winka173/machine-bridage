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
        private bool _stormSeen;

        /// <summary>
        /// Prompt 31 L5 (written blind): the sandstorm that rolls over one half of the map (SandstormTurn) covers only that half
        /// in the view: while the camera looks at the other half the weather's presence is low (the dust thins, the look eases
        /// back to the weather it replaced); once the storm has passed, a sandstorm that replaced another weather thins out
        /// everywhere. Any other weather, or a map in a sandstorm of its own with no storm turning, is shown whole.
        /// </summary>
        private float StormPresence()
        {
            if (_weatherKind != WeatherKind.Sandstorm) return 1f;
            if (_world.StormActive)
            {
                _stormSeen = true;
                var focus = _camera.Focus;
                return _world.InStorm(new System.Numerics.Vector2(focus.x, focus.z)) ? 1f : 0.15f;
            }
            return _stormSeen && _weather.Replaced ? 0.15f : 1f;
        }

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
