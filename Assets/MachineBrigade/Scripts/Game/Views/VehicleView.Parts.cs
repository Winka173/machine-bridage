using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 8's moving parts on a vehicle's view: the armoured bulldozer's blade (a stroke each
    /// time it rams), a boss's destructible parts (hidden, a wreck piece put in at their origin when
    /// they break), the models a boss carries along (the supergun's tractors) and a boring boss sinking
    /// into the ground. Kept apart from VehicleView.cs so the two change independently.
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform _blade;
        private Quaternion _bladeRest;
        private float _bladeStrokeAt = -10f;

        /// <summary>How long one ram of the blade takes (up, then down on the target).</summary>
        private const float BladeSeconds = 0.55f;

        private void InitParts(ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials)
        {
            foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
                if (t.name == "Blade")
                {
                    _blade = t;
                    _bladeRest = t.localRotation;
                    break;
                }
            InitBossParts(models);
        }

        /// <summary>The blade rams: a quick lift and a slam down on what is in front (the sim's blow lands with it).</summary>
        public void BladeStroke() => _bladeStrokeAt = Time.time;

        private void AnimatePrompt8Parts()
        {
            if (_blade != null)
            {
                var t = (Time.time - _bladeStrokeAt) / BladeSeconds;
                // Lift to 14 degrees in the first third, slam down a little past rest, settle.
                var pitch = t < 0f || t >= 1f ? 0f : t < 0.33f ? -14f * (t / 0.33f) : Mathf.Lerp(-14f, 3f, (t - 0.33f) / 0.4f) * (t > 0.73f ? (1f - t) / 0.27f : 1f);
                _blade.localRotation = _bladeRest * Quaternion.Euler(pitch, 0f, 0f);
            }
            AnimateBossParts();
        }

        // Filled in by the boss parts (see InitBossParts / AnimateBossParts below).
        private readonly List<(int index, Transform node)> _partNodes = new();
    }
}
