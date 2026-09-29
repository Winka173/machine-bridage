using System.Collections.Generic;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Burnt-out hulks: they burn, cook off now and then, smoulder, and after a while sink into
    /// the ground and disappear (sooner when there are more than the budget allows). A vehicle's
    /// death explosion tears pieces off it, bucks the hull and can blow the turret high into the
    /// air trailing fire; big vehicles then cook off in a quick chain of blasts, and some shoot a
    /// fountain of flame out of the turret ring. Shot-down aircraft fall burning and blow up
    /// when they hit the ground. Everything moves on simple kinematics; no physics engine.
    /// </summary>
    internal sealed class WreckManager
    {
        // Explode, burn, go: a hulk burns for a quarter of a minute and is gone soon after, so
        // the field shows the current fight rather than a scrapyard of old ones.
        private const float BurnSeconds = 12f;
        private const float LifeSeconds = 17f;
        private const float SinkSeconds = 3f;
        private const float SinkDepth = 2.2f;
        private const float Gravity = 18f;

        /// <summary>How long a destroyed defence burns before it only smoulders.</summary>
        private const float StaticBurnSeconds = 45f;

        private sealed class Wreck
        {
            public EntityId Id;
            public VehicleView View;
            public float Created, Expires;
            public float SinkStart = -1f;
            public float NextPop;
            public int PopsLeft;
            public int ChainLeft;
            public float NextChain;
            public bool WasFalling;
            public bool Blown;
            public Transform Turret;
            public Vector3 TurretVelocity, TurretSpin;
            public bool TurretFlying;
            public float TurretFlame, TurretSmoke;
            public float JetFrom, JetUntil, JetDebt;
            public float HopVelocity, HopHeight;
            public int Fire;
        }

        private readonly List<Wreck> _wrecks = new();
        private readonly List<(Vector3 position, float size)> _crashes = new();
        private readonly FireSpots _fires;
        private readonly ChunkThrower _chunks;
        private readonly int _capacity;

        public WreckManager(FireSpots fires, ChunkThrower chunks, int capacity)
        {
            _fires = fires;
            _chunks = chunks;
            _capacity = capacity;
        }

        public void Add(VehicleView view, float now)
        {
            view.BecomeWreck();
            var wreck = new Wreck
            {
                Id = view.Id, View = view, Created = now, Expires = now + LifeSeconds * Random.Range(0.85f, 1.15f),
                NextPop = now + Random.Range(3f, 5f), PopsLeft = Random.Range(1, 3), WasFalling = view.Falling,
            };
            _wrecks.Add(wreck);
            if (view.Def.Static)
            {
                // A tower, bunker or gun: its ruin stays for the rest of the battle. It burns hard
                // from the top and at its foot, its ammunition goes up in a chain, then pops now and
                // then while it burns, and it smoulders on after.
                wreck.Expires = float.MaxValue;
                wreck.ChainLeft = Random.Range(4, 7);
                wreck.NextChain = now + Random.Range(0.3f, 0.5f);
                wreck.PopsLeft = Random.Range(4, 7);
                wreck.NextPop = now + Random.Range(4f, 6f);
                var blaze = Mathf.Clamp(view.Sim.Radius / 1.4f, 1f, 2f);
                // DECISIONS 20Y: a boss's ruin burns as hard but shorter, under its thinner death smoke.
                var boss = view.Def.Boss;
                var burn = boss ? StaticBurnSeconds * 0.45f : StaticBurnSeconds;
                var smoke = boss ? FireSpots.BossSmoke : 1f;
                wreck.Fire = _fires.Ignite(view.Root.position + Vector3.up * view.Top * 0.7f, blaze, burn, now, smoke: smoke);
                _fires.Ignite(view.Root.position + Vector3.up * 0.5f + Random.insideUnitSphere * 0.8f, blaze * 0.7f, burn * 1.6f, now, smoke: smoke);
                return;
            }
            // A shot-down aircraft burns all the way down; a ground hulk burns where it stopped.
            var size = Mathf.Clamp(view.Sim.Radius / 1.6f, 0.75f, 1.6f);
            wreck.Fire = _fires.Ignite(view.Root.position + Vector3.up * 0.9f, size, BurnSeconds * Random.Range(0.85f, 1.15f), now,
                view.Flying ? view.Root : null, smoke: view.Def.Boss ? FireSpots.BossSmoke : 1f);

            // Ruins of fixed defences stay; only vehicle hulks make room for new ones.
            var living = 0;
            foreach (var w in _wrecks)
                if (w.SinkStart < 0f && !w.View.Def.Static) living++;
            if (living <= _capacity) return;
            foreach (var w in _wrecks)
            {
                if (w.SinkStart >= 0f || w.View.Def.Static) continue;
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
            w.JetUntil = 0f;
            // No flames over empty ground once the hulk has gone.
            _fires.Extinguish(w.Fire, now);
        }

        /// <summary>
        /// The death explosion of a freshly destroyed ground vehicle: pieces of it fly off (some
        /// burning, some in its colours), the hull bucks, the turret is thrown into the air, and a
        /// big vehicle's ammunition starts cooking off. Once per wreck; aircraft are left to fall.
        /// </summary>
        public void Blow(EntityId id, float now)
        {
            Wreck wreck = null;
            foreach (var w in _wrecks)
                if (w.Id == id) wreck = w;
            if (wreck == null || wreck.Blown || wreck.View.Flying) return;
            wreck.Blown = true;
            var view = wreck.View;
            var radius = view.Sim.Radius;
            _chunks?.Wreck(view.Root.position, radius, view.Team, true, now);
            // A hull bucks in the blast; a concrete defence does not.
            wreck.HopVelocity = view.Def.Static ? 0f : Random.Range(3f, 4.5f);

            // Ammunition going up: a quick chain of small pops around the hull after the big blast.
            if (radius >= 1.1f)
            {
                wreck.ChainLeft = radius >= 1.8f ? Random.Range(3, 5) : Random.Range(2, 4);
                wreck.NextChain = now + Random.Range(0.35f, 0.6f);
            }
            if (radius >= 1.8f)
            {
                // ...and in some hulls a roaring jet of flame out of the turret ring.
                if (view.Turret != null && Random.value < 0.55f)
                {
                    wreck.JetFrom = now + Random.Range(0.25f, 0.8f);
                    wreck.JetUntil = wreck.JetFrom + Random.Range(1.4f, 2.6f);
                }
            }
            TossTurret(wreck);
        }

        /// <summary>Throws the turret of a freshly destroyed vehicle high into the air.</summary>
        private static void TossTurret(Wreck wreck)
        {
            if (wreck.Turret != null || wreck.View.Turret == null || wreck.View.Flying) return;
            wreck.Turret = wreck.View.Turret;
            wreck.Turret.SetParent(wreck.View.Root, true);
            wreck.TurretVelocity = new Vector3(Random.Range(-3.5f, 3.5f), Random.Range(11f, 16f), Random.Range(-3.5f, 3.5f));
            wreck.TurretSpin = Random.insideUnitSphere * 420f;
            wreck.TurretFlying = true;
        }

        /// <summary>
        /// Ammunition cooking off inside a burning hulk: returns one wreck position that is due a
        /// secondary explosion, and whether it is a pop (a small fireball) or only a spray of
        /// sparks: first a quick chain of pops scattered round the hull right after the big
        /// blast, then a few while it burns. Never another big blast on the same spot.
        /// </summary>
        public bool TryCookOff(float now, out Vector3 position, out bool pop)
        {
            foreach (var w in _wrecks)
            {
                if (w.SinkStart >= 0f || w.WasFalling) continue;
                var high = w.View.Def.Static ? w.View.Top * 0.6f : 0.8f;
                if (w.ChainLeft > 0 && now >= w.NextChain)
                {
                    w.ChainLeft--;
                    w.NextChain = now + Random.Range(0.22f, 0.5f);
                    pop = true;
                    position = Around(w, high, w.View.Sim.Radius * 1.4f);
                    return true;
                }
                if (now - w.Created > (w.View.Def.Static ? StaticBurnSeconds : BurnSeconds) || w.PopsLeft <= 0 || now < w.NextPop) continue;
                w.PopsLeft--;
                w.NextPop = now + Random.Range(2f, 4f);
                pop = Random.value < 0.5f;
                position = Around(w, w.View.Def.Static ? high : 1.2f, 0.7f);
                return true;
            }
            position = default;
            pop = false;
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
                    Hop(w, dt);
                    if (now >= w.JetFrom && now < w.JetUntil)
                    {
                        // The fountain surges, then gutters out.
                        var t = (now - w.JetFrom) / Mathf.Max(0.1f, w.JetUntil - w.JetFrom);
                        var strength = Mathf.Lerp(1.15f, 0.6f, t) * Mathf.Clamp(w.View.Sim.Radius / 2.2f, 0.8f, 1.4f);
                        _fires.Jet(w.View.Root.position + Vector3.up * 1.6f, strength, ref w.JetDebt, dt);
                    }
                }
                if (w.TurretFlying) FlyTurret(w, now, dt);

                if (w.SinkStart < 0f) continue;
                var k = (now - w.SinkStart) / SinkSeconds;
                if (k >= 1f)
                {
                    Object.Destroy(w.View.Root.gameObject);
                    _wrecks.RemoveAt(i);
                    continue;
                }
                var p = w.View.Root.position;
                w.View.Root.position = new Vector3(p.x, -SinkDepth * k * k, p.z);
            }
        }

        public void Clear()
        {
            foreach (var w in _wrecks)
                if (w.View.Root != null) Object.Destroy(w.View.Root.gameObject);
            _wrecks.Clear();
            _crashes.Clear();
        }

        private static Vector3 Around(Wreck w, float height, float reach) =>
            w.View.Root.position + new Vector3(Random.Range(-reach, reach), height, Random.Range(-reach, reach));

        /// <summary>The hull thrown up by its death explosion, landing back with a thud.</summary>
        private static void Hop(Wreck w, float dt)
        {
            if (w.HopVelocity == 0f && w.HopHeight == 0f) return;
            w.HopVelocity -= Gravity * dt;
            w.HopHeight += w.HopVelocity * dt;
            if (w.HopHeight <= 0f)
            {
                w.HopHeight = 0f;
                w.HopVelocity = 0f;
            }
            var p = w.View.Root.position;
            w.View.Root.position = new Vector3(p.x, w.HopHeight, p.z);
        }

        /// <summary>The blown-off turret tumbles through the air trailing fire and smoke, and comes to rest burning.</summary>
        private void FlyTurret(Wreck w, float now, float dt)
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
            _chunks?.Trails.Fly(ref w.TurretFlame, ref w.TurretSmoke, position, true, dt);
            const float rest = 0.35f;
            if (position.y <= rest && w.TurretVelocity.y < 0f)
            {
                position.y = rest;
                if (w.TurretVelocity.y < -4f)
                {
                    w.TurretVelocity = new Vector3(w.TurretVelocity.x * 0.4f, -w.TurretVelocity.y * 0.25f, w.TurretVelocity.z * 0.4f);
                    w.TurretSpin *= 0.3f;
                    _chunks?.Trails.Impact(position);
                }
                else
                {
                    w.TurretFlying = false;
                    // Settle upright or upside down, whichever is nearer.
                    var up = Vector3.Dot(turret.up, Vector3.up) >= 0f ? Vector3.up : Vector3.down;
                    turret.rotation = Quaternion.FromToRotation(turret.up, up) * turret.rotation;
                    _chunks?.Trails.Land(position, 0f, true, now);
                    _fires.Ignite(new Vector3(position.x, 0.3f, position.z), 0.55f, Random.Range(8f, 12f), now);
                }
            }
            turret.position = position;
        }
    }
}
