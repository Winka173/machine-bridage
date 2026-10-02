using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    public sealed partial class MatchRunner
    {
        /// <summary>
        /// Prompt 34 L3: a boss's T4+ round (203 mm and up, the Smerch, the 400 kg bombs) marks its fall point's edge on the minimap
        /// for its flight, so a warning off the screen is still seen. The ring on the ground is the effects' (EscapeWarnings).
        /// </summary>
        private void EscapeMark(SimEvent e)
        {
            if (e.DefId == null || !_world.TryGetVehicle(e.Entity, out var shooter) || !shooter.Def.Boss) return;
            var mounts = shooter.Def.Mounts;
            if (e.Mount < 0 || e.Mount >= mounts.Count) return;
            var round = e.Round != null && _world.Catalog.Weapons.TryGetValue(e.Round, out var r) ? r : mounts[e.Mount].Weapon;
            if (round.WarnSeconds <= 0f || round.Guided || round.Laid) return;
            _warnings.Add((new Vector2(e.Target.X, e.Target.Y), round.WarnRadius, Time.time + Mathf.Max(0.05f, e.Value) + 0.2f));
        }
    }
}
