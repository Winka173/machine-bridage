using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Draws one vehicle. It reads the simulation after each fixed step and interpolates between
    /// the last two steps every frame. On top of that it adds life the simulation does not need:
    /// barrel recoil, hull pitch when accelerating or braking, a light bounce on the move, turning
    /// weapon mounts, spinning rotors, and flight (altitude, banking) for aircraft.
    /// </summary>
    public sealed class VehicleView
    {
        private const float BarWidth = 2.4f;
        private const float BarHeight = 0.2f;
        private const float RecoilSeconds = 0.35f;
        private const float TakeOffSeconds = 2.2f;

        private static readonly int TintId = Shader.PropertyToID("_Tint");

        private readonly ModelInstance _model;
        private readonly Transform _body;
        private readonly GroundMark _ring;
        private readonly GroundMark _shadowRing;
        private readonly Transform _bar;
        private readonly Transform _barFill;
        private readonly Vector3[] _recoilRest;
        private readonly float _recoilDistance;
        private readonly Transform[] _mounts;
        private readonly Transform[] _muzzles;
        private readonly float[] _previousMount, _currentMount;
        private readonly float _spawnTime;
        private Vector3 _previousPosition, _currentPosition;
        private float _previousHeading, _currentHeading, _previousTurret, _currentTurret;
        private float _previousSpeed, _currentSpeed;
        private float _recoilTime = -10f;
        private float _pitch, _bank;
        private float _bouncePhase;
        private float _spin;
        private float _crashStart = -1f;
        private float _crashHeight;
        private Vector3 _crashDrift;
        private bool _wreck;

        public VehicleView(Vehicle vehicle, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials,
            Transform parent, int playerTeam)
        {
            Sim = vehicle;
            Def = vehicle.Def;
            Root = new GameObject($"{vehicle.Def.Id} {vehicle.Id}").transform;
            Root.SetParent(parent, false);
            _body = new GameObject("Body").transform;
            _body.SetParent(Root, false);
            _model = models.Spawn(vehicle.Def.Model, vehicle.Team, _body);
            _spawnTime = Time.time;

            _recoilRest = new Vector3[_model.RecoilParts.Count];
            for (var i = 0; i < _recoilRest.Length; i++) _recoilRest[i] = _model.RecoilParts[i].localPosition;
            _recoilDistance = Mathf.Clamp(vehicle.Radius * 0.18f, 0.12f, 0.45f);

            var mounts = Def.Mounts;
            _mounts = new Transform[mounts.Count];
            _muzzles = new Transform[mounts.Count];
            _previousMount = new float[mounts.Count];
            _currentMount = new float[mounts.Count];
            for (var i = 0; i < mounts.Count; i++)
            {
                _model.Mounts.TryGetValue(mounts[i].Slot, out _mounts[i]);
                _model.Muzzles.TryGetValue(mounts[i].Slot, out _muzzles[i]);
            }

            _ring = new GroundMark("Selection", Root, meshes, materials, GroundMark.Style.Selection);
            _ring.Transform.localPosition = new Vector3(0f, 0.07f, 0f);
            _ring.Transform.localScale = Vector3.one * (vehicle.Radius + 0.9f);
            _ring.Set(new Color(0.55f, 1.7f, 1.15f, 1f), Color.white);
            _ring.Visible = false;
            if (vehicle.Def.Flying)
            {
                // Aircraft show where they are over the ground (and whose they are) with a faint ring.
                _shadowRing = new GroundMark("Air Ring", Root, meshes, materials, GroundMark.Style.Aircraft);
                _shadowRing.Transform.localScale = Vector3.one * (vehicle.Radius + 1.2f);
                var colour = (Color)TeamColors.Ui(vehicle.Team == playerTeam ? 0 : 1) * 1.2f;
                colour.a = 0.75f;
                _shadowRing.Set(colour, Color.white);
            }

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
        public VehicleDef Def { get; }
        public EntityId Id => Sim.Id;
        public int Team => Sim.Team;
        public string DefId => Def.Id;
        public Transform Root { get; }
        public Transform Turret => _model.Turret;
        public Vector3 Position => Root.position;
        public bool Selected { get; set; }
        public bool Flying => Def.Flying;

        /// <summary>World-space main muzzle, for tracers and flashes.</summary>
        public Vector3 MuzzleWorld => _body.TransformPoint(_model.Muzzle);

        public float MuzzleHeight => _model.Muzzle.y;

        /// <summary>Latest simulated ground speed in m/s.</summary>
        public float Speed => _currentSpeed;

        /// <summary>Next time tread dust may be kicked up; owned by the effects layer.</summary>
        public float DustAt { get; set; }

        /// <summary>Current flight height (0 on the ground).</summary>
        public float Altitude { get; private set; }

        /// <summary>
        /// World position of the muzzle of weapon mount <paramref name="index"/>. Models without that
        /// muzzle fall back to a sensible spot: a coaxial gun beside the main gun, roof weapons on top.
        /// </summary>
        public Vector3 MuzzleOf(int index)
        {
            if (index < _muzzles.Length && _muzzles[index] != null) return _muzzles[index].position;
            if (index == 0) return MuzzleWorld;
            var slot = Def.Mounts[index].Slot;
            var pivot = _mounts[index] != null ? _mounts[index] : _model.Turret != null ? _model.Turret : _body;
            if (slot == "coax") return _body.TransformPoint(_model.Muzzle) + pivot.right * 0.35f - pivot.forward * 0.6f;
            var top = pivot.position + Vector3.up * (pivot == _body ? MuzzleHeight + 0.6f : 0.8f);
            return top + DirectionOf(index) * 0.8f;
        }

        /// <summary>World-space direction weapon mount <paramref name="index"/> points in.</summary>
        public Vector3 DirectionOf(int index)
        {
            var heading = index < _currentMount.Length ? _currentMount[index] : _currentTurret;
            return Quaternion.Euler(0f, heading, 0f) * Vector3.forward;
        }

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
            for (var i = 0; i < _currentMount.Length; i++)
            {
                _previousMount[i] = _currentMount[i];
                _currentMount[i] = Sim.MountHeading(i) * Mathf.Rad2Deg;
            }
        }

        /// <summary>Starts the barrel kick; called when the simulation reports a main-gun shot.</summary>
        public void Recoil() => _recoilTime = Time.time;

        public void Render(float alpha, Quaternion cameraRotation)
        {
            if (_wreck)
            {
                RenderWreck();
                return;
            }

            var hull = Mathf.LerpAngle(_previousHeading, _currentHeading, alpha);
            var position = Vector3.Lerp(_previousPosition, _currentPosition, alpha);
            var acceleration = (_currentSpeed - _previousSpeed) * 20f;
            var ease = 1f - Mathf.Exp(-Time.deltaTime * 6f);

            if (Flying)
            {
                // Climb after spawning, hover with a slow bob, nose down when speeding up and bank into turns.
                var climb = Mathf.SmoothStep(0f, 1f, (Time.time - _spawnTime) / TakeOffSeconds);
                Altitude = Def.Altitude * climb + Mathf.Sin(Time.time * 1.3f + Id.Value) * 0.25f * climb;
                var turn = Mathf.DeltaAngle(_previousHeading, _currentHeading) * 20f;
                if (Def.FixedWing)
                {
                    // Aeroplanes fly level and bank hard into their turns.
                    _pitch = Mathf.Lerp(_pitch, Mathf.Clamp(acceleration * 0.5f, -4f, 4f), ease);
                    _bank = Mathf.Lerp(_bank, Mathf.Clamp(-turn * 0.45f, -50f, 50f), ease);
                }
                else
                {
                    _pitch = Mathf.Lerp(_pitch, Mathf.Clamp(_currentSpeed * 0.9f + acceleration * 1.5f, -8f, 16f), ease);
                    _bank = Mathf.Lerp(_bank, Mathf.Clamp(-turn * 0.12f, -20f, 20f), ease);
                }
                position.y = Altitude;
                _body.localPosition = Vector3.zero;
                _body.localRotation = Quaternion.Euler(_pitch, 0f, _bank);
            }
            else
            {
                // Hull pitch follows acceleration (nose dips when braking) and eases back.
                _pitch = Mathf.Lerp(_pitch, Mathf.Clamp(-acceleration * 0.9f, -4f, 4f), ease);
                _bouncePhase += Time.deltaTime * (4f + _currentSpeed * 1.4f);
                var bounce = Mathf.Sin(_bouncePhase) * 0.012f * Mathf.Clamp01(_currentSpeed / 4f);
                _body.localPosition = new Vector3(0f, bounce, 0f);
                _body.localRotation = Quaternion.Euler(_pitch, 0f, 0f);
            }
            Root.position = position;
            Root.rotation = Quaternion.Euler(0f, hull, 0f);

            if (_model.Turret != null && !Match.DebugFlags.Has("-mb-no-turret"))
            {
                var turret = Mathf.LerpAngle(_previousTurret, _currentTurret, alpha);
                _model.Turret.localRotation = Quaternion.Euler(0f, Mathf.DeltaAngle(hull, turret), 0f);
                var t = (Time.time - _recoilTime) / RecoilSeconds;
                var kick = t is >= 0f and < 1f ? (1f - t) * (1f - t) * _recoilDistance : 0f;
                for (var i = 0; i < _recoilRest.Length; i++)
                    _model.RecoilParts[i].localPosition = _recoilRest[i] + Vector3.back * kick;
            }

            // Free weapon mounts turn on their own; their parent may be the turret or the hull.
            for (var i = 1; i < _mounts.Length; i++)
            {
                var mount = _mounts[i];
                if (mount == null || Def.Mounts[i].Aim != MountAim.Free) continue;
                var heading = Mathf.LerpAngle(_previousMount[i], _currentMount[i], alpha);
                var parentYaw = mount.parent != null ? mount.parent.eulerAngles.y : 0f;
                mount.localRotation = Quaternion.Euler(0f, Mathf.DeltaAngle(parentYaw, heading), 0f);
            }

            Spin(1f);

            _ring.Visible = Selected;
            if (_shadowRing != null)
            {
                // Keep the air ring on the ground under the aircraft, level whatever it is doing.
                _shadowRing.Transform.position = new Vector3(Root.position.x, 0.08f, Root.position.z);
                _shadowRing.Transform.rotation = Quaternion.identity;
            }
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
            if (!Match.DebugFlags.Has("-mb-no-tint"))
            {
                var block = new MaterialPropertyBlock();
                block.SetColor(TintId, new Color(0.16f, 0.14f, 0.13f));
                foreach (var r in _model.Renderers) r.SetPropertyBlock(block);
            }
            _ring.Visible = false;
            if (_shadowRing != null) _shadowRing.Visible = false;
            _bar.gameObject.SetActive(false);
            Selected = false;
            _wreck = true;
            if (Flying)
            {
                // Keep some of the momentum it had when it was hit.
                _crashStart = Time.time;
                _crashHeight = Root.position.y;
                _crashDrift = (_currentPosition - _previousPosition) * 20f * 0.8f;
                _crashDrift.y = 0f;
                return;
            }
            _body.localRotation = Quaternion.Euler(Random.Range(-3f, 3f), 0f, Random.Range(-4f, 4f));
        }

        /// <summary>True while a shot-down aircraft is still falling.</summary>
        public bool Falling => _crashStart >= 0f && Root.position.y > 0.05f;

        /// <summary>Animates a wreck that is still settling (a shot-down aircraft falling).</summary>
        public void AnimateWreck() => RenderWreck();

        private void RenderWreck()
        {
            if (!Flying || _crashStart < 0f || Root.position.y <= 0f) return;
            // Out of control: it drifts on with its momentum, spins faster and faster as the tail
            // goes, tips over and drops, the rotor winding down, until it hits the ground.
            var t = Time.time - _crashStart;
            if (Def.FixedWing)
            {
                // An aeroplane dives in nose first, rolling, trailing fire.
                var dive = Mathf.Max(0f, _crashHeight - 0.5f * 11f * t * t);
                var glide = _crashDrift * Mathf.Clamp01(1f - t * 0.35f) * Time.deltaTime;
                var q = Root.position + glide;
                Root.position = new Vector3(q.x, dive, q.z);
                _body.localRotation = Quaternion.Euler(Mathf.Min(40f, t * 30f), 0f, t * 140f);
                Spin(1f);
                return;
            }
            var height = Mathf.Max(0f, _crashHeight - 0.5f * 7f * t * t);
            var drift = _crashDrift * Mathf.Clamp01(1f - t * 0.5f) * Time.deltaTime;
            var p = Root.position + drift;
            Root.position = new Vector3(p.x, height, p.z);
            Root.rotation *= Quaternion.Euler(0f, Mathf.Lerp(150f, 560f, Mathf.Clamp01(t / 1.4f)) * Time.deltaTime, 0f);
            _body.localRotation = Quaternion.Euler(Mathf.Min(28f, t * 24f), 0f, Mathf.Min(40f, t * 34f));
            Spin(Mathf.Clamp01(1f - t * 0.6f));
        }

        private void Spin(float speed)
        {
            var spinners = _model.Spinners;
            if (spinners.Count == 0) return;
            _spin += Time.deltaTime * speed;
            for (var i = 0; i < spinners.Count; i++)
                spinners[i].Transform.localRotation = spinners[i].Rest * Quaternion.AngleAxis(_spin * spinners[i].DegreesPerSecond, spinners[i].Axis);
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
