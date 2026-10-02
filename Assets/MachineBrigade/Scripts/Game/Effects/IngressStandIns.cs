using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 33 L2, the ingress contract's picture: a scripted reinforcement announced by the simulation
    /// (<see cref="SimEventKind.Ingress"/>) is drawn as a stand-in driving up its gate's approach from beyond the play area, so
    /// that it reaches the gate's spot at the entry tick, when the real vehicle appears there and the stand-in is removed. It
    /// has no logic: no collider, not a target, not seen by anyone, never read back by the simulation; it drives at most at
    /// the vehicle's own speed, so it starts nearer the gate when the warning is short. Written blind (no Unity run).
    /// </summary>
    internal sealed class IngressStandIns
    {
        private sealed class StandIn
        {
            public GameObject Model;
            public Vector3 From, To;
            public float Start, Arrive;
        }

        private readonly Catalog _catalog;
        private readonly ModelLibrary _models;
        private readonly Transform _root;
        private readonly List<StandIn> _list = new();

        /// <summary>Fewer than this many seconds to go: nothing is drawn (the vehicle is as good as there).</summary>
        private const float MinLead = 0.3f;

        /// <summary>At most this many stand-ins at once (a big wave announces a row at a time anyway).</summary>
        private const int Budget = 24;

        public IngressStandIns(Catalog catalog, ModelLibrary models, Transform parent)
        {
            _catalog = catalog;
            _models = models;
            _root = new GameObject("Ingress Stand-ins").transform;
            _root.SetParent(parent, false);
        }

        public void Queue(SimEvent e, float now)
        {
            if (e.Value < MinLead || _list.Count >= Budget || e.DefId == null || !_catalog.Vehicles.TryGetValue(e.DefId, out var def) || def.Flying) return;
            var inward = new Vector3(e.Target.X, 0f, e.Target.Y);
            if (inward.sqrMagnitude < 0.01f) return;
            inward.Normalize();
            var to = new Vector3(e.Position.X, 0f, e.Position.Y);
            // Up the approach no faster than it drives, and never from further out than the gate's approach is long.
            var reach = Mathf.Min(Mathf.Max(0f, e.Offset.X), Mathf.Max(1f, def.Speed) * e.Value);
            if (reach < 1f) return;
            var model = _models.Spawn(Match.BranchArt.Model(def, _models), e.Team, _root, castShadows: false);
            model.Root.transform.localScale = Vector3.one * MachineBrigade.Game.Views.VehicleView.DrawScaleOf(def, model.Root);
            model.Root.transform.SetPositionAndRotation(to - inward * reach, Quaternion.LookRotation(inward));
            _list.Add(new StandIn { Model = model.Root, From = to - inward * reach, To = to, Start = now, Arrive = now + e.Value });
        }

        public void Tick(float now)
        {
            for (var i = _list.Count - 1; i >= 0; i--)
            {
                var s = _list[i];
                if (s.Model == null || now >= s.Arrive)
                {
                    // The real vehicle takes over at the gate this moment.
                    if (s.Model != null) Object.Destroy(s.Model);
                    _list.RemoveAt(i);
                    continue;
                }
                var t = Mathf.Clamp01((now - s.Start) / Mathf.Max(0.01f, s.Arrive - s.Start));
                s.Model.transform.position = Vector3.Lerp(s.From, s.To, t);
            }
        }

        public void Clear()
        {
            foreach (var s in _list)
                if (s.Model != null) Object.Destroy(s.Model);
            _list.Clear();
        }
    }
}
