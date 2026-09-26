using System.Collections.Generic;
using MachineBrigade.Game.Views;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Burnt-out hulks: they burn, cook off now and then, smoulder, and after a while sink into
    /// the ground and disappear (sooner when there are more than the budget allows). Turrets can
    /// be blown off, and shot-down aircraft fall burning and blow up when they hit the ground.
    /// Everything moves on simple kinematics; no physics engine is involved.
    /// </summary>
    internal sealed class WreckManager
    {
        private const float BurnSeconds = 45f;
        private const float LifeSeconds = 75f;
        private const float SinkSeconds = 5f;
        private const float SinkDepth = 2.2f;
        private const float Gravity = 18f;

        private sealed class Wreck
        {
            public EntityId Id;
            public VehicleView View;
            public float Created, Expires;
            public float SinkStart = -1f;
            public float NextPop;
            public int PopsLeft;
            public bool WasFalling;
            public Transform Turret;
            public Vector3 TurretVelocity, TurretSpin;
            public bool TurretFlying;
            public int Fire;
        }

        private readonly List<Wreck> _wrecks = new();
        private readonly List<(Vector3 position, float size)> _crashes = new();
        private readonly FireSpots _fires;
        private readonly int _capacity;

        public WreckManager(FireSpots fires, int capacity)
        {
            _fires = fires;
            _capacity = capacity;
        }

        public void Add(VehicleView view, float now)
        {
            view.BecomeWreck();
            var wreck = new Wreck
            {
                Id = view.Id, View = view, Created = now, Expires = now + LifeSeconds * Random.Range(0.85f, 1.15f),
                NextPop = now + Random.Range(1.5f, 4f), PopsLeft = Random.Range(2, 6), WasFalling = view.Falling,
            };
            _wrecks.Add(wreck);
            // A shot-down aircraft burns all the way down; a ground hulk burns where it stopped.
            var size = Mathf.Clamp(view.Sim.Radius / 1.6f, 0.75f, 1.6f);
            wreck.Fire = _fires.Ignite(view.Root.position + Vector3.up * 0.9f, size, BurnSeconds * Random.Range(0.85f, 1.15f), now,
                view.Flying ? view.Root : null);

            var living = 0;
            foreach (var w in _wrecks)
                if (w.SinkStart < 0f) living++;
            if (living <= _capacity) return;
            foreach (var w in _wrecks)
            {
                if (w.SinkStart >= 0f) continue;
                Sink(w, now);
                break;
            }
        }

        /// <summary>A falling or fallen aircraft wreck: where it is now (its death blast goes off there).</summary>
        public bool TryGetAircraftWreck(EntityId id, out Vector3 position)
        {
            foreach (var w in _wrecks)
            {
                if (w.Id != id || !w.View.Flying) continue;
                position = w.View.Root.position;
                return true;
            }
            position = default;
            return false;
        }

        private void Sink(Wreck w, float now)
        {
            w.SinkStart = now;
            // No flames over empty ground once the hulk has gone.
            _fires.Extinguish(w.Fire, now);
        }

        /// <summary>Throws the turret of a freshly destroyed vehicle into the air.</summary>
        public void TossTurret(EntityId id, float now)
        {
            Wreck wreck = null;
            foreach (var w in _wrecks)
                if (w.Id == id) wreck = w;
            if (wreck == null || wreck.Turret != null || wreck.View.Turret == null || wreck.View.Flying) return;
            wreck.Turret = wreck.View.Turret;
            wreck.Turret.SetParent(wreck.View.Root, true);
            wreck.TurretVelocity = new Vector3(Random.Range(-2.5f, 2.5f), Random.Range(8f, 12f), Random.Range(-2.5f, 2.5f));
            wreck.TurretSpin = Random.insideUnitSphere * 300f;
            wreck.TurretFlying = true;
        }

        /// <summary>
        /// Ammunition cooking off inside a burning hulk: returns one wreck position that is due a
        /// secondary pop, a few times per wreck while it burns.
        /// </summary>
        public bool TryCookOff(float now, out Vector3 position)
        {
            foreach (var w in _wrecks)
            {
                if (now - w.Created > BurnSeconds || w.SinkStart >= 0f || w.WasFalling || w.PopsLeft <= 0 || now < w.NextPop) continue;
                w.PopsLeft--;
                w.NextPop = now + Random.Range(2f, 6f);
                position = w.View.Root.position + new Vector3(Random.Range(-0.6f, 0.6f), 1.2f, Random.Range(-0.6f, 0.6f));
                return true;
            }
            position = default;
            return false;
        }

        /// <summary>A falling aircraft that has just hit the ground: where, and how big it was.</summary>
        public bool TryCrash(out Vector3 position, out float size)
        {
            if (_crashes.Count == 0)
            {
                position = default;
                size = 0f;
                return false;
            }
            (position, size) = _crashes[_crashes.Count - 1];
            _crashes.RemoveAt(_crashes.Count - 1);
            return true;
        }

        public void Tick(float now, float dt)
        {
            for (var i = _wrecks.Count - 1; i >= 0; i--)
            {
                var w = _wrecks[i];
                if (w.SinkStart < 0f)
                {
                    w.View.AnimateWreck();
                    if (w.WasFalling && !w.View.Falling)
                    {
                        w.WasFalling = false;
                        _crashes.Add((w.View.Root.position, w.View.Sim.Radius));
                    }
                    if (now >= w.Expires) Sink(w, now);
                }
                if (w.TurretFlying) FlyTurret(w, dt);

                if (w.SinkStart < 0f) continue;
                var t = (now - w.SinkStart) / SinkSeconds;
                if (t >= 1f)
                {
                    Object.Destroy(w.View.Root.gameObject);
                    _wrecks.RemoveAt(i);
                    continue;
                }
                var p = w.View.Root.position;
                w.View.Root.position = new Vector3(p.x, -SinkDepth * t * t, p.z);
            }
        }

        public void Clear()
        {
            foreach (var w in _wrecks)
                if (w.View.Root != null) Object.Destroy(w.View.Root.gameObject);
            _wrecks.Clear();
            _crashes.Clear();
        }

        /// <summary>The blown-off turret tumbles through the air and comes to rest on the ground.</summary>
        private static void FlyTurret(Wreck w, float dt)
        {
            var turret = w.Turret;
            if (turret == null)
            {
                w.TurretFlying = false;
                return;
            }
            w.TurretVelocity.y -= Gravity * dt;
            var position = turret.position + w.TurretVelocity * dt;
            turret.rotation = Quaternion.Euler(w.TurretSpin * dt) * turret.rotation;
            const float rest = 0.35f;
            if (position.y <= rest && w.TurretVelocity.y < 0f)
            {
                position.y = rest;
                if (w.TurretVelocity.y < -4f)
                {
                    w.TurretVelocity = new Vector3(w.TurretVelocity.x * 0.4f, -w.TurretVelocity.y * 0.25f, w.TurretVelocity.z * 0.4f);
                    w.TurretSpin *= 0.3f;
                }
                else
                {
                    w.TurretFlying = false;
                    // Settle upright or upside down, whichever is nearer.
                    var up = Vector3.Dot(turret.up, Vector3.up) >= 0f ? Vector3.up : Vector3.down;
                    turret.rotation = Quaternion.FromToRotation(turret.up, up) * turret.rotation;
                }
            }
            turret.position = position;
        }
    }
}
