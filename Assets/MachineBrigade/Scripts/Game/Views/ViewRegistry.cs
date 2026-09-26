using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Views
{
    /// <summary>Owns the views of living vehicles and answers screen-space picking.</summary>
    public sealed class ViewRegistry : IDisposable
    {
        private readonly Dictionary<EntityId, VehicleView> _views = new();
        private readonly List<VehicleView> _list = new();
        private readonly ModelLibrary _models;
        private readonly MeshLibrary _meshes;
        private readonly MaterialLibrary _materials;
        private readonly Transform _parent;
        private readonly int _playerTeam;

        public ViewRegistry(ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Transform parent, int playerTeam)
        {
            _models = models;
            _meshes = meshes;
            _materials = materials;
            _parent = new GameObject("Vehicles").transform;
            _parent.SetParent(parent, false);
            _playerTeam = playerTeam;
        }

        public IReadOnlyList<VehicleView> All => _list;

        public VehicleView Add(Vehicle vehicle)
        {
            if (_views.TryGetValue(vehicle.Id, out var existing)) return existing;
            var view = new VehicleView(vehicle, _models, _meshes, _materials, _parent, _playerTeam);
            _views.Add(vehicle.Id, view);
            _list.Add(view);
            return view;
        }

        public bool TryGet(EntityId id, out VehicleView view) => _views.TryGetValue(id, out view);

        /// <summary>Stops tracking a view (it becomes a wreck owned by the effects).</summary>
        public VehicleView Detach(EntityId id)
        {
            if (!_views.Remove(id, out var view)) return null;
            _list.Remove(view);
            return view;
        }

        public void SnapshotAll()
        {
            foreach (var view in _list) view.Snapshot();
        }

        public void Render(float alpha, Quaternion cameraRotation)
        {
            foreach (var view in _list) view.Render(alpha, cameraRotation);
        }

        /// <summary>
        /// Nearest vehicle to a screen point, allowing its on-screen size plus a finger-sized
        /// margin, so small vehicles stay easy to tap without stealing neighbours (V2 R01).
        /// </summary>
        public VehicleView Pick(Vector2 screen, Camera camera, float marginPixels)
        {
            VehicleView best = null;
            var bestDistance = float.MaxValue;
            foreach (var view in _list)
            {
                var centre = view.Position + Vector3.up * 1f;
                var sp = camera.WorldToScreenPoint(centre);
                if (sp.z <= 0f) continue;
                var edge = camera.WorldToScreenPoint(centre + camera.transform.right * view.Sim.Radius);
                var allowance = Vector2.Distance(sp, edge) + marginPixels;
                var distance = Vector2.Distance(screen, sp);
                if (distance > allowance || distance >= bestDistance) continue;
                best = view;
                bestDistance = distance;
            }
            return best;
        }

        public void Dispose()
        {
            if (_parent != null) Object.Destroy(_parent.gameObject);
            _views.Clear();
            _list.Clear();
        }
    }
}
