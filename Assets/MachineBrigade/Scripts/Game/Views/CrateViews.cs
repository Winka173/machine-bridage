using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Supply crates from battle events: each one sways down under its parachute, lands with the
    /// canopy gone, and disappears once a side claims it (or it expires).
    /// </summary>
    internal sealed class CrateViews
    {
        private const float FallHeight = 45f;
        private const float FallSeconds = 5f;

        private readonly ModelLibrary _models;
        private readonly Transform _root;
        private readonly Dictionary<EntityId, (GameObject body, Transform chute)> _views = new();
        private readonly List<EntityId> _gone = new();
        private readonly string _model;

        public CrateViews(ModelLibrary models, Transform root)
        {
            _models = models;
            _root = root;
            _model = models.Has("supply_crate") ? "supply_crate" : models.Has("ammo_crate") ? "ammo_crate" : null;
        }

        public void Update(SimWorld world)
        {
            if (_model == null) return;
            var now = (float)world.Time;
            foreach (var crate in world.Crates)
            {
                if (!_views.TryGetValue(crate.Id, out var view))
                {
                    var body = _models.Spawn(_model, -1, _root).Root;
                    view = (body, FindChute(body.transform));
                    _views[crate.Id] = view;
                }
                var left = Mathf.Max(0f, (float)crate.LandsAt - now);
                var t = left / FallSeconds;
                var height = FallHeight * t * t;
                // A gentle pendulum sway under the canopy while it falls.
                var sway = Mathf.Sin(now * 1.7f + crate.Id.Value) * 6f * t;
                view.body.transform.SetPositionAndRotation(new Vector3(crate.Position.X, height, crate.Position.Y),
                    Quaternion.Euler(sway, crate.Id.Value * 47f, 0f));
                if (view.chute != null && view.chute.gameObject.activeSelf != left > 0f) view.chute.gameObject.SetActive(left > 0f);
            }

            _gone.Clear();
            foreach (var (id, view) in _views)
            {
                var alive = false;
                foreach (var crate in world.Crates)
                    if (crate.Id == id) { alive = true; break; }
                if (alive) continue;
                Object.Destroy(view.body);
                _gone.Add(id);
            }
            foreach (var id in _gone) _views.Remove(id);
        }

        private static Transform FindChute(Transform root)
        {
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (t.name.StartsWith("Parachute")) return t;
            return null;
        }
    }
}
