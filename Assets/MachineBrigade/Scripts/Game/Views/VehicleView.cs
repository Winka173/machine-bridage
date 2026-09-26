using MachineBrigade.Game.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Draws one vehicle. It reads the simulation after each fixed step and interpolates
    /// between the last two steps every frame, so motion stays smooth at any frame rate.
    /// </summary>
    public sealed class VehicleView
    {
        private const float BarWidth = 2.4f;
        private const float BarHeight = 0.22f;

        private readonly Transform _turret;
        private readonly GameObject _ring;
        private readonly Transform _bar;
        private readonly Transform _barFill;
        private readonly MeshRenderer[] _renderers;
        private Vector3 _previousPosition, _currentPosition;
        private float _previousHeading, _currentHeading, _previousTurret, _currentTurret;

        public VehicleView(Vehicle vehicle, MeshLibrary meshes, MaterialLibrary materials, Transform parent, int playerTeam)
        {
            Sim = vehicle;
            Meshes = meshes.Vehicle(vehicle.Def.Id, vehicle.Team);
            Root = new GameObject($"{vehicle.Def.Id} {vehicle.Id}").transform;
            Root.SetParent(parent, false);

            var hull = CreateMesh("Hull", Root, Meshes.Hull, materials.Voxel, true);
            _turret = CreateMesh("Turret", hull, Meshes.Turret, materials.Voxel, true);
            _turret.localPosition = Meshes.TurretOffset;
            _renderers = new[] { hull.GetComponent<MeshRenderer>(), _turret.GetComponent<MeshRenderer>() };

            var ring = CreateMesh("Selection", Root, meshes.Ring, materials.SelectionRing, false);
            ring.localPosition = new Vector3(0f, 0.06f, 0f);
            ring.localScale = Vector3.one * (vehicle.Radius + 0.7f);
            _ring = ring.gameObject;
            _ring.SetActive(false);

            _bar = new GameObject("HealthBar").transform;
            _bar.SetParent(Root, false);
            _bar.localPosition = new Vector3(0f, Meshes.MuzzleHeight + 1.6f, 0f);
            var back = CreateMesh("Back", _bar, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(BarWidth + 0.12f, BarHeight + 0.12f, 1f);
            _barFill = CreateMesh("Fill", _bar, meshes.Quad, vehicle.Team == playerTeam ? materials.BarAlly : materials.BarEnemy, false);
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
        public VehicleMeshes Meshes { get; }
        public Transform Root { get; }
        public Transform Turret => _turret;
        public Vector3 Position => Root.position;
        public bool Selected { get; set; }

        public void Snapshot()
        {
            _previousPosition = _currentPosition;
            _previousHeading = _currentHeading;
            _previousTurret = _currentTurret;
            _currentPosition = new Vector3(Sim.Position.X, 0f, Sim.Position.Y);
            _currentHeading = Sim.Heading * Mathf.Rad2Deg;
            _currentTurret = Sim.TurretHeading * Mathf.Rad2Deg;
        }

        public void Render(float alpha, Quaternion cameraRotation)
        {
            Root.position = Vector3.Lerp(_previousPosition, _currentPosition, alpha);
            var hull = Mathf.LerpAngle(_previousHeading, _currentHeading, alpha);
            Root.rotation = Quaternion.Euler(0f, hull, 0f);
            var turret = Mathf.LerpAngle(_previousTurret, _currentTurret, alpha);
            _turret.localRotation = Quaternion.Euler(0f, Mathf.DeltaAngle(hull, turret), 0f);

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
        public void BecomeWreck(Material wreck)
        {
            foreach (var r in _renderers) r.sharedMaterial = wreck;
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
