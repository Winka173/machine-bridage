using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Draws one vehicle. It reads the simulation after each fixed step and interpolates between
    /// the last two steps every frame. On top of that it adds life the simulation does not need:
    /// barrel recoil, hull pitch when accelerating or braking, and a light bounce on the move.
    /// </summary>
    public sealed class VehicleView
    {
        private const float BarWidth = 2.4f;
        private const float BarHeight = 0.2f;
        private const float RecoilSeconds = 0.35f;

        private static readonly int TintId = Shader.PropertyToID("_Tint");

        private readonly ModelInstance _model;
        private readonly Transform _body;
        private readonly GameObject _ring;
        private readonly Transform _bar;
        private readonly Transform _barFill;
        private readonly Vector3[] _recoilRest;
        private readonly float _recoilDistance;
        private Vector3 _previousPosition, _currentPosition;
        private float _previousHeading, _currentHeading, _previousTurret, _currentTurret;
        private float _previousSpeed, _currentSpeed;
        private float _recoilTime = -10f;
        private float _pitch;
        private float _bouncePhase;

        public VehicleView(Vehicle vehicle, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials,
            Transform parent, int playerTeam)
        {
            Sim = vehicle;
            Root = new GameObject($"{vehicle.Def.Id} {vehicle.Id}").transform;
            Root.SetParent(parent, false);
            _body = new GameObject("Body").transform;
            _body.SetParent(Root, false);
            _model = models.Spawn(vehicle.Def.Id, vehicle.Team, _body);

            _recoilRest = new Vector3[_model.RecoilParts.Count];
            for (var i = 0; i < _recoilRest.Length; i++) _recoilRest[i] = _model.RecoilParts[i].localPosition;
            _recoilDistance = Mathf.Clamp(vehicle.Radius * 0.18f, 0.12f, 0.45f);

            var ring = CreateMesh("Selection", Root, meshes.Ring, materials.SelectionRing, false);
            ring.localPosition = new Vector3(0f, 0.05f, 0f);
            ring.localScale = Vector3.one * (vehicle.Radius + 0.8f);
            _ring = ring.gameObject;
            _ring.SetActive(false);

            _bar = new GameObject("HealthBar").transform;
            _bar.SetParent(Root, false);
            _bar.localPosition = new Vector3(0f, _model.Muzzle.y + 1.9f, 0f);
            var back = CreateMesh("Back", _bar, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(BarWidth + 0.14f, BarHeight + 0.14f, 1f);
            _barFill = CreateMesh("Fill", _bar, meshes.Quad, vehicle.Team == playerTeam ? materials.BarAlly : materials.BarEnemy,
                false);
            _barFill.localPosition = new Vector3(0f, 0f, -0.02f);
            _bar.gameObject.SetActive(false);

            Snapshot();
            Snapshot(); // previous == current, so the first frame does not interpolate from the origin
            Render(1f, Quaternion.identity);
        }

        public Vehicle Sim { get; }
        public EntityId Id => Sim.Id;
        public int Team => Sim.Team;
        public string DefId => Sim.Def.Id;
        public Transform Root { get; }
        public Transform Turret => _model.Turret;
        public Vector3 Position => Root.position;
        public bool Selected { get; set; }

        /// <summary>World-space muzzle, for tracers and flashes.</summary>
        public Vector3 MuzzleWorld => _body.TransformPoint(_model.Muzzle);

        public float MuzzleHeight => _model.Muzzle.y;

        /// <summary>Latest simulated ground speed in m/s.</summary>
        public float Speed => _currentSpeed;

        /// <summary>Next time tread dust may be kicked up; owned by the effects layer.</summary>
        public float DustAt { get; set; }

        public void Snapshot()
        {
            _previousPosition = _currentPosition;
            _previousHeading = _currentHeading;
            _previousTurret = _currentTurret;
            _previousSpeed = _currentSpeed;
            _currentPosition = new Vector3(Sim.Position.X, 0f, Sim.Position.Y);
            _currentHeading = Sim.Heading * Mathf.Rad2Deg;
            _currentTurret = Sim.TurretHeading * Mathf.Rad2Deg;
            _currentSpeed = Sim.Speed;
        }

        /// <summary>Starts the barrel kick; called when the simulation reports a shot.</summary>
        public void Recoil() => _recoilTime = Time.time;

        public void Render(float alpha, Quaternion cameraRotation)
        {
            Root.position = Vector3.Lerp(_previousPosition, _currentPosition, alpha);
            var hull = Mathf.LerpAngle(_previousHeading, _currentHeading, alpha);
            Root.rotation = Quaternion.Euler(0f, hull, 0f);

            // Hull pitch follows acceleration (nose dips when braking) and eases back.
            var acceleration = (_currentSpeed - _previousSpeed) * 20f;
            _pitch = Mathf.Lerp(_pitch, Mathf.Clamp(-acceleration * 0.9f, -4f, 4f), 1f - Mathf.Exp(-Time.deltaTime * 6f));
            _bouncePhase += Time.deltaTime * (4f + _currentSpeed * 1.4f);
            var bounce = Mathf.Sin(_bouncePhase) * 0.012f * Mathf.Clamp01(_currentSpeed / 4f);
            _body.localPosition = new Vector3(0f, bounce, 0f);
            _body.localRotation = Quaternion.Euler(_pitch, 0f, 0f);

            if (_model.Turret != null)
            {
                var turret = Mathf.LerpAngle(_previousTurret, _currentTurret, alpha);
                _model.Turret.localRotation = Quaternion.Euler(0f, Mathf.DeltaAngle(hull, turret), 0f);
                var t = (Time.time - _recoilTime) / RecoilSeconds;
                var kick = t is >= 0f and < 1f ? (1f - t) * (1f - t) * _recoilDistance : 0f;
                for (var i = 0; i < _recoilRest.Length; i++)
                    _model.RecoilParts[i].localPosition = _recoilRest[i] + Vector3.back * kick;
            }

            if (_ring.activeSelf != Selected) _ring.SetActive(Selected);
            var health = Mathf.Clamp01(Sim.Hp / Sim.MaxHp);
            var showBar = Selected || health < 0.999f;
            if (_bar.gameObject.activeSelf != showBar) _bar.gameObject.SetActive(showBar);
            if (!showBar) return;
            _bar.rotation = cameraRotation;
            _barFill.localScale = new Vector3(BarWidth * health, BarHeight, 1f);
            _barFill.localPosition = new Vector3(-BarWidth * (1f - health) * 0.5f, 0f, -0.02f);
        }

        /// <summary>Freezes the view as a burnt-out hulk; the simulation entity is gone.</summary>
        public void BecomeWreck()
        {
            var block = new MaterialPropertyBlock();
            block.SetColor(TintId, new Color(0.16f, 0.14f, 0.13f));
            foreach (var r in _model.Renderers) r.SetPropertyBlock(block);
            _body.localRotation = Quaternion.Euler(Random.Range(-3f, 3f), 0f, Random.Range(-4f, 4f));
            _ring.SetActive(false);
            _bar.gameObject.SetActive(false);
            Selected = false;
        }

        internal static Transform CreateMesh(string name, Transform parent, Mesh mesh, Material material, bool castShadows)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            renderer.receiveShadows = castShadows;
            return go.transform;
        }
    }
}
