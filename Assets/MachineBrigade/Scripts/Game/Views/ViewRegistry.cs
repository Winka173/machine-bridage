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
            if (VehicleLod.Enabled) _impostors = new ImpostorAtlas(materials);
        }

        private readonly ImpostorAtlas _impostors;

        /// <summary>The atlas of far-away cards; null with -mb-no-lod.</summary>
        public ImpostorAtlas Impostors => _impostors;

        /// <summary>The camera whose zoom picks the vehicles' detail levels (the main camera unless set).</summary>
        public Camera LodCamera { get; set; }

        public IReadOnlyList<VehicleView> All => _list;

        /// <summary>The player's side (views colour shields, bars and rings by it).</summary>
        public int PlayerTeam => _playerTeam;

        public VehicleView Add(Vehicle vehicle)
        {
            if (_views.TryGetValue(vehicle.Id, out var existing)) return existing;
            var view = new VehicleView(vehicle, _models, _meshes, _materials, _parent, _playerTeam) { Registry = this };
            // Play-test 14 lane K: the impostor pages are baked in army paint; a vehicle in its own livery stays a model.
            if (_impostors != null && view.Livery == null) view.Impostor = _impostors.Request(view.Lod, vehicle.Team);
            _views.Add(vehicle.Id, view);
            _list.Add(view);
            return view;
        }

        public bool TryGet(EntityId id, out VehicleView view) => _views.TryGetValue(id, out view);

        /// <summary>Draws a vehicle again from scratch (it changed sides: new colours, new markings).</summary>
        public VehicleView Rebuild(Vehicle vehicle)
        {
            var old = Detach(vehicle.Id);
            if (old != null) Object.Destroy(old.Root.gameObject);
            return Add(vehicle);
        }

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
            if (LodCamera == null) LodCamera = Camera.main;
            var ppm = VehicleLod.PixelsPerMetreOf(LodCamera);
            VehicleLod.PixelsPerMetre = ppm;
            _impostors?.BakePending(cameraRotation);
            _impostors?.Begin();
            _cards = 0;
            foreach (var view in _list)
            {
                view.UpdateLod(ppm);
                view.Render(alpha, cameraRotation);
                if (_impostors == null || view.Level != VehicleLod.Impostor || !OnScreen(view)) continue;
                _impostors.Add(view.Impostor, view.ImpostorCentre, view.DrawScale, view.Root.eulerAngles.y, view.ImpostorTint);
                _cards++;
            }
            // Only in the battle camera (not a menu turntable's).
            _impostors?.Flush(LodCamera);
            // Cards cast no shadows: with shadows on, a soft disc stands in under each one.
            // Play-test 14 (lane L, owner 04/10: "bóng của máy bay có 1 vòng tròn bóng khác lồng lên nhau, xóa vòng tròn đó"):
            // lane K's disc under every aircraft whatever the setting is gone; with shadows on an aircraft (a full model) has
            // its sun shadow alone, one shadow each. The disc stands in only where no real shadow is drawn: shadows Off
            // (BlobShadows) and the far cards.
            if (BlobShadows || _cards > 0) DrawBlobs(!BlobShadows);
        }

        private int _cards;

        /// <summary>An aircraft's disc (shadows Off, or a card) sits above the water mesh (0.04 m) and under the ground marks (0.07-0.08 m).</summary>
        private const float AirDiscHeight = 0.06f;

        /// <summary>How many vehicles are at each detail level and how many cards were drawn in how many draws (for -mb-perf).</summary>
        public string LodSummary()
        {
            int full = 0, simple = 0, cards = 0;
            foreach (var view in _list)
                switch (view.Level)
                {
                    case VehicleLod.Full: full++; break;
                    case VehicleLod.Simple: simple++; break;
                    default: cards++; break;
                }
            return _impostors == null ? $"lod=off({full})"
                : $"lod={full}/{simple}/{cards} cards={_impostors.LastDrawn} in {_impostors.LastDraws} pages={_impostors.Pages.Count} ppm={VehicleLod.PixelsPerMetre:0.0}";
        }

        /// <summary>Whether a vehicle's card may be on screen (its middle within the view, with room for its size).</summary>
        private bool OnScreen(VehicleView view)
        {
            if (LodCamera == null) return true;
            var p = LodCamera.WorldToViewportPoint(view.ImpostorCentre);
            var margin = view.LodSize * VehicleLod.PixelsPerMetre / Mathf.Max(1f, LodCamera.pixelHeight) + 0.02f;
            return p.x > -margin && p.x < 1f + margin && p.y > -margin && p.y < 1f + margin;
        }

        /// <summary>
        /// With shadows off, a soft dark disc under every vehicle keeps it on the ground; an
        /// aircraft's disc falls away from it along the sun, which also shows its height.
        /// </summary>
        public bool BlobShadows { get; set; }

        private readonly List<Matrix4x4> _blobs = new();
        private RenderParams _blobParams;
        private Vector3 _sunDirection;
        private bool _blobReady;

        private void DrawBlobs(bool cardsOnly = false)
        {
            if (!_blobReady)
            {
                _blobReady = true;
                _sunDirection = new Vector3(0.35f, -0.8f, 0.45f).normalized;
                foreach (var light in Object.FindObjectsByType<Light>())
                    if (light.type == LightType.Directional) _sunDirection = light.transform.forward;
                _blobParams = new RenderParams(_materials.Scorch)
                {
                    shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off,
                    receiveShadows = false,
                    worldBounds = new Bounds(Vector3.zero, Vector3.one * 1000f),
                };
            }
            _blobs.Clear();
            var slide = new Vector3(_sunDirection.x, 0f, _sunDirection.z) / Mathf.Max(0.2f, -_sunDirection.y);
            foreach (var view in _list)
            {
                if (!view.Root.gameObject.activeInHierarchy || (cardsOnly && view.Level != VehicleLod.Impostor)) continue;
                var p = view.Root.position;
                var size = view.Sim.Radius * 2.3f;
                var ground = new Vector3(p.x, 0.04f, p.z);
                if (view.Flying)
                {
                    ground.y = AirDiscHeight;
                    ground += slide * p.y;
                    size *= 1f + p.y * 0.015f;
                }
                _blobs.Add(Matrix4x4.TRS(ground, Quaternion.Euler(90f, 0f, 0f), new Vector3(size, size, 1f)));
            }
            // Play-test 14 lane K: on the views' own layer, so a preview range's discs show in its camera, not the lobby's.
            _blobParams.layer = _parent.gameObject.layer;
            if (_blobs.Count > 0) Graphics.RenderMeshInstanced(_blobParams, _meshes.ScorchQuad, 0, _blobs);
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
            _impostors?.Dispose();
            if (_parent != null) Object.Destroy(_parent.gameObject);
            _views.Clear();
            _list.Clear();
        }
    }
}
