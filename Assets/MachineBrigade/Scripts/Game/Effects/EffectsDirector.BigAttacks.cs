using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Entities;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 18 A.3: a boss charging its big attack shows it on the part that fires it: a hot pulse there twice a
    /// second (the coils brightening, the launcher opening), growing as the moment nears. The zones are
    /// <see cref="BigAttackZones"/>. View only; the model's own charge animations are asset debt.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private readonly BigAttackZones _bigZones;
        private float _bigPulse;

        private void TickBigCharge(ViewRegistry views, float now)
        {
            if (now < _bigPulse) return;
            _bigPulse = now + 0.5f;
            var all = views.All;
            for (var v = 0; v < all.Count; v++)
            {
                var sim = all[v].Sim;
                if (sim?.BigAttack is not { Stage: BigStage.Charging } big || !sim.IsAlive || all[v].IsWreck) continue;
                var near = Mathf.Clamp01(1f - big.WarnLeft / Mathf.Max(0.5f, big.Def.Warn));
                foreach (var i in big.Parts)
                {
                    if (sim.IsPartBroken(i)) continue;
                    var part = sim.Def.Parts[i];
                    var at = sim.PartPosition(i);
                    var point = new Vector3(at.X, part.Height * sim.Def.Scale + (sim.Flying ? sim.Height : 0f), at.Y);
                    Ring(point, Mathf.Max(3f, part.Radius * 2.2f) * (1f + near), new Color(2.8f, 0.9f + near, 0.3f, 0.9f));
                }
            }
        }
    }
}
