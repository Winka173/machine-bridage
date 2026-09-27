using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// The detail page's "In action" tab: a small battle of its own in which the vehicle shoots
    /// at targets that cannot fire back or die: the real simulation, the real models and effects,
    /// seen by the preview camera. It runs only while the tab is open, when the lobby battle is
    /// resting, and everything in it lives on the preview camera's layer, so the two never mix.
    /// </summary>
    public sealed class FiringRange : IDisposable
    {
        private const float Step = 0.05f;

        private readonly SimWorld _world;
        private readonly ViewRegistry _views;
        private readonly EffectsDirector _effects;
        private readonly Transform _root;
        private readonly Camera _camera;
        private readonly int _layer;
        private Vehicle _shooter;
        private readonly string _id;
        private readonly Vector2 _start;
        private float _goneFor;
        private readonly List<Vehicle> _targets = new();
        private float _accumulator;
        private float _layerAt;
        private Vector3 _look;
        private float _reach;

        public FiringRange(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Camera camera, int layer,
            string vehicleId)
        {
            _camera = camera;
            _layer = layer;
            _root = new GameObject("Firing Range").transform;
            var map = new MapDefinition("range", 90f,
                new[] { new TeamStart(0, new Vector2(0f, -70f)), new TeamStart(1, new Vector2(0f, 70f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            _world = new SimWorld(catalog, map, seed: 11);
            _world.EnableEconomy(new TeamEconomy(0));
            _world.EnableEconomy(new TeamEconomy(1));
            _views = new ViewRegistry(models, meshes, materials, _root, 0);
            // The effects need a battlefield camera for culling and the view's focus; this one only
            // wraps the preview camera, which is put back the way the preview wants it below.
            var rts = new RtsCamera(camera, 90f, Vector3.zero);
            camera.orthographic = false;
            camera.fieldOfView = 36f;
            camera.nearClipPlane = 0.5f;
            camera.farClipPlane = 400f;
            _effects = new EffectsDirector(catalog, materials, meshes, models, rts, _root, EffectBudget.Eco);

            var ground = VehicleView.CreateMesh("Ground", _root, meshes.GroundQuad, materials.Ground, false);
            ground.localScale = new Vector3(260f, 1f, 260f);
            ground.localPosition = new Vector3(0f, -0.02f, 0f);

            var def = catalog.Vehicles[vehicleId];
            var distance = TargetDistance(def);
            _id = vehicleId;
            _start = new Vector2(0f, -distance * 0.5f);
            _shooter = _world.SpawnVehicle(vehicleId, 0, _start, 0f);
            var ground_ = HitsGround(def);
            var air = HitsAir(def);
            var far = new Vector2(0f, distance * 0.5f);
            if (ground_)
            {
                Target("main_battle_tank", far + new Vector2(-4f, 0f));
                Target("apc", far + new Vector2(5f, 3f));
                Target("heavy_tank", far + new Vector2(0f, 9f));
            }
            if (air) Target("attack_helicopter", far + new Vector2(ground_ ? 10f : 0f, ground_ ? -6f : 0f));
            _reach = distance;
            SetLayer(_root);
        }

        /// <summary>Far enough for artillery's minimum range, near enough to see the vehicle and its targets in one frame.</summary>
        private static float TargetDistance(VehicleDef def)
        {
            var reach = float.MaxValue;
            var minimum = 0f;
            foreach (var m in def.Mounts)
            {
                if (m.Weapon.Damage <= 0f) continue;
                reach = Mathf.Min(reach, m.Weapon.Range);
                minimum = Mathf.Max(minimum, m.Weapon.MinRange);
            }
            if (reach == float.MaxValue) reach = 20f;
            var d = Mathf.Clamp(reach * 0.7f, 10f, 42f);
            return Mathf.Max(d, minimum + 6f);
        }

        private static bool HitsGround(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.CanTarget(false) && m.Weapon.Damage > 0f) return true;
            return false;
        }

        private static bool HitsAir(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.CanTarget(true) && m.Weapon.Damage > 0f) return true;
            return false;
        }

        private void Target(string id, Vector2 at)
        {
            var target = _world.SpawnVehicle(id, 1, at, MathF.PI);
            _world.MakeDummy(target);
            _targets.Add(target);
        }

        /// <summary>Per frame: steps the little battle, keeps the vehicle on its targets and the camera on the scene.</summary>
        public void Tick(float dt)
        {
            _accumulator = Mathf.Min(_accumulator + dt, Step * 4f);
            while (_accumulator >= Step)
            {
                _accumulator -= Step;
                Order();
                _world.Step(Step);
                _views.SnapshotAll();
                foreach (var e in _world.Events)
                    if (e.Kind == Sim.Events.SimEventKind.VehicleSpawned && _world.TryGetVehicle(e.Entity, out var spawned))
                        _views.Add(spawned);
                _effects.Consume(_world.Events, _views, null);
                _world.ClearEvents();
            }
            // A car bomb (or anything knocked out) comes back for another go.
            _goneFor = _shooter.IsAlive ? 0f : _goneFor + dt;
            if (_goneFor > 2.5f)
            {
                _goneFor = 0f;
                _shooter = _world.SpawnVehicle(_id, 0, _start, 0f);
            }
            _effects.Tick(_views);
            Frame(dt);
            _views.Render(_accumulator / Step, _camera.transform.rotation);
            // New effects and views are made on the default layer: move them onto the preview's.
            if (Time.unscaledTime >= _layerAt)
            {
                _layerAt = Time.unscaledTime + 0.3f;
                SetLayer(_root);
            }
        }

        /// <summary>Keeps the vehicle attacking the nearest target it can hit (a car bomb goes round again: it is rebuilt).</summary>
        private void Order()
        {
            if (!_shooter.IsAlive || _world.Tick % 20 != 1) return;
            Vehicle best = null;
            var bestDistance = float.MaxValue;
            foreach (var t in _targets)
            {
                if (!t.IsAlive || !_shooter.Def.Weapon.CanTarget(t.Flying)) continue;
                var d = Vector2.Distance(t.Position, _shooter.Position);
                if (d < bestDistance)
                {
                    best = t;
                    bestDistance = d;
                }
            }
            if (best != null && _shooter.Order.Target != best.Id)
                _world.Submit(new Command(CommandType.Attack, 0, new[] { _shooter.Id }, default, best.Id));
        }

        /// <summary>From beside and a little behind the vehicle, high enough to see the rounds land.</summary>
        private void Frame(float dt)
        {
            var from = _views.TryGet(_shooter.Id, out var view) ? view.Position : new Vector3(0f, 0f, -_reach * 0.5f);
            var to = new Vector3(0f, 0f, _reach * 0.5f);
            var centre = (from + to) * 0.5f + Vector3.up * 1.5f;
            _look = _look == Vector3.zero ? centre : Vector3.Lerp(_look, centre, 1f - Mathf.Exp(-dt * 3f));
            var span = Mathf.Max(Vector3.Distance(from, to) * 0.5f + 8f, 14f);
            var distance = span / Mathf.Tan(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad) * 0.95f;
            _camera.transform.position = _look + new Vector3(0.95f, 0.75f, -0.45f).normalized * distance;
            _camera.transform.LookAt(_look);
        }

        private void SetLayer(Transform t)
        {
            t.gameObject.layer = _layer;
            foreach (Transform child in t) SetLayer(child);
        }

        public void Dispose()
        {
            _effects.Dispose();
            _views.Dispose();
            if (_root != null) UnityEngine.Object.Destroy(_root.gameObject);
        }
    }
}
