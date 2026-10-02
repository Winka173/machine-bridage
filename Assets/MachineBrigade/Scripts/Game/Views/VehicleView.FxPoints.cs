using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 29 5.5: where the flare and APS effects leave from: the points <see cref="ModelLibrary"/> put on the model's
    /// `Flares` and `Aps_cluster` nodes (empty on a model without them; the effects then fall back to the hull).
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform[] _flarePoints, _apsPoints;

        /// <summary>
        /// The flare dispensers' points: fix prompt L4, the model's own Mount_Flare_* empties (rear fuselage, both sides, tail
        /// root; <see cref="ModelLibrary.FlareMountPrefix"/>), else one per side and row of its `Flares` tubes.
        /// </summary>
        public IReadOnlyList<Transform> FlarePoints => _flarePoints ??= FlareMounts() ?? FxPoints(ModelLibrary.FlarePointName);

        /// <summary>The model's Mount_Flare_* empties, or null when it has none.</summary>
        private Transform[] FlareMounts()
        {
            if (_model?.Root == null) return null;
            List<Transform> list = null;
            foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
                if (ModelLibrary.IsFlareMount(t.name)) (list ??= new List<Transform>()).Add(t);
            return list?.ToArray();
        }

        /// <summary>The APS cassettes' points (one per side).</summary>
        public IReadOnlyList<Transform> ApsPoints => _apsPoints ??= FxPoints(ModelLibrary.ApsPointName);

        private Transform[] FxPoints(string name)
        {
            var list = new List<Transform>();
            if (_model?.Root != null)
                foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
                    if (t.name == name) list.Add(t);
            return list.ToArray();
        }
    }
}
