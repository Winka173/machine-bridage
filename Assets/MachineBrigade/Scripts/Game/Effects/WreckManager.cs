using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Burnt-out hulks that keep burning, then smoulder. Turrets can be blown off by the
    /// cook-off. Capped so the oldest wreck fades out when a new one arrives.
    /// </summary>
    internal sealed class WreckManager
    {
        private const float BurnSeconds = 25f;
        private const float FadeSeconds = 1.5f;
        private const float TurretSettleSeconds = 6f;

        private sealed class Wreck
        {
            public EntityId Id;
            public VehicleView View;
            public ParticleSystem Fire;
            public float Created;
            public bool FireOut;
            public Rigidbody TurretBody;
            public float TurretSettleAt;
            public float FadeStart = -1f;
            public float NextPop;
            public int PopsLeft;
        }

        private readonly List<Wreck> _wrecks = new();
        private readonly MaterialLibrary _materials;
        private readonly int _capacity;

        public WreckManager(MaterialLibrary materials, int capacity)
        {
            _materials = materials;
            _capacity = capacity;
        }

        public void Add(VehicleView view, float now)
        {
            view.BecomeWreck();
            var wreck = new Wreck
            {
                Id = view.Id, View = view, Created = now, Fire = Burn(view.Root, _materials),
                NextPop = now + Random.Range(1.5f, 4f), PopsLeft = Random.Range(2, 6),
            };
            _wrecks.Add(wreck);

            var living = 0;
            foreach (var w in _wrecks)
                if (w.FadeStart < 0f) living++;
            if (living <= _capacity) return;
            foreach (var w in _wrecks)
            {
                if (w.FadeStart >= 0f) continue;
                w.FadeStart = now;
                break;
            }
        }

        /// <summary>Throws the turret of a freshly destroyed vehicle into the air.</summary>
        public void TossTurret(EntityId id, float now)
        {
            var wreck = _wrecks.Find(w => w.Id == id);
            if (wreck == null || wreck.TurretBody != null) return;
            var turret = wreck.View.Turret;
            if (turret == null) return;
            var collider = turret.gameObject.AddComponent<BoxCollider>();
            var bounds = LocalBounds(turret);
            collider.center = bounds.center;
            collider.size = Vector3.Max(bounds.size, Vector3.one * 0.3f);
            var body = turret.gameObject.AddComponent<Rigidbody>();
            body.mass = 3f;
            body.linearVelocity = new Vector3(Random.Range(-2.5f, 2.5f), Random.Range(7f, 11f), Random.Range(-2.5f, 2.5f));
            body.angularVelocity = Random.insideUnitSphere * 5f;
            wreck.TurretBody = body;
            wreck.TurretSettleAt = now + TurretSettleSeconds;
        }

        /// <summary>
        /// Ammunition cooking off inside a burning hulk: returns one wreck position that is due a
        /// secondary pop, a few times per wreck while it burns.
        /// </summary>
        public bool TryCookOff(float now, out Vector3 position)
        {
            foreach (var w in _wrecks)
            {
                if (w.FireOut || w.FadeStart >= 0f || w.PopsLeft <= 0 || now < w.NextPop) continue;
                w.PopsLeft--;
                w.NextPop = now + Random.Range(2f, 6f);
                position = w.View.Root.position + new Vector3(Random.Range(-0.6f, 0.6f), 1.2f, Random.Range(-0.6f, 0.6f));
                return true;
            }
            position = default;
            return false;
        }

        public void Tick(float now)
        {
            for (var i = _wrecks.Count - 1; i >= 0; i--)
            {
                var w = _wrecks[i];
                if (!w.FireOut && now - w.Created > BurnSeconds)
                {
                    var emission = w.Fire.emission;
                    emission.enabled = false;
                    w.FireOut = true;
                }

                if (w.TurretBody != null && now > w.TurretSettleAt)
                {
                    Object.Destroy(w.TurretBody);
                    Object.Destroy(w.TurretBody.GetComponent<BoxCollider>());
                    w.TurretBody = null;
                    w.TurretSettleAt = float.MaxValue;
                }

                if (w.FadeStart < 0f) continue;
                var t = (now - w.FadeStart) / FadeSeconds;
                if (t >= 1f)
                {
                    Object.Destroy(w.View.Root.gameObject);
                    _wrecks.RemoveAt(i);
                }
                else
                {
                    w.View.Root.localScale = Vector3.one * (1f - t);
                }
            }
        }

        public void Clear()
        {
            foreach (var w in _wrecks)
                if (w.View.Root != null) Object.Destroy(w.View.Root.gameObject);
            _wrecks.Clear();
        }

        /// <summary>Bounds of every mesh under a transform, in that transform's space.</summary>
        private static Bounds LocalBounds(Transform root)
        {
            var bounds = new Bounds(Vector3.zero, Vector3.zero);
            var first = true;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>())
            {
                if (filter.sharedMesh == null) continue;
                var b = filter.sharedMesh.bounds;
                for (var i = 0; i < 8; i++)
                {
                    var corner = new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y,
                        (i & 4) == 0 ? b.min.z : b.max.z);
                    var p = root.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    if (first) { bounds = new Bounds(p, Vector3.zero); first = false; }
                    else bounds.Encapsulate(p);
                }
            }
            return bounds;
        }

        /// <summary>Looping flames plus a slow smoke column, attached to the hulk.</summary>
        private static ParticleSystem Burn(Transform parent, MaterialLibrary m)
        {
            var fire = PB.Create(parent, "Wreck Fire", m.Fire);
            fire.transform.localPosition = new Vector3(0f, 1f, 0f);
            var main = fire.main;
            main.loop = true;
            main.duration = 2f;
            PB.Basics(fire, new Vector2(0.4f, 0.8f), new Vector2(1f, 2.2f), new Vector2(0.8f, 1.6f));
            var shape = fire.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 12f;
            shape.radius = 0.6f;
            shape.rotation = new Vector3(-90f, 0f, 0f);
            PB.Colors(fire, PB.FireGradient);
            PB.Grow(fire, 1f, 0.3f);
            var emission = fire.emission;
            emission.enabled = true;
            emission.rateOverTime = 14f;

            var smoke = PB.Create(fire.transform, "Wreck Smoke", m.Smoke);
            var smokeMain = smoke.main;
            smokeMain.loop = true;
            smokeMain.duration = 3f;
            PB.Basics(smoke, new Vector2(2.4f, 4f), new Vector2(0.2f, 0.5f), new Vector2(1f, 1.8f));
            PB.Colors(smoke, PB.Plume(0.12f, 0.42f, 0.42f));
            PB.Grow(smoke, 0.7f, 2.3f);
            PB.Rise(smoke, 1.6f, 2.6f);
            var smokeEmission = smoke.emission;
            smokeEmission.enabled = true;
            smokeEmission.rateOverTime = 4f;

            fire.Play(true);
            return fire;
        }
    }
}
