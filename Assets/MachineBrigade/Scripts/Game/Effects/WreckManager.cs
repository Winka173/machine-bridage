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
            view.BecomeWreck(_materials.Wreck);
            var wreck = new Wreck { Id = view.Id, View = view, Created = now, Fire = Burn(view.Root, _materials) };
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
            var filter = turret.GetComponent<MeshFilter>();
            var collider = turret.gameObject.AddComponent<BoxCollider>();
            if (filter != null)
            {
                collider.center = filter.sharedMesh.bounds.center;
                collider.size = filter.sharedMesh.bounds.size;
            }
            var body = turret.gameObject.AddComponent<Rigidbody>();
            body.mass = 3f;
            body.linearVelocity = new Vector3(Random.Range(-2.5f, 2.5f), Random.Range(7f, 11f), Random.Range(-2.5f, 2.5f));
            body.angularVelocity = Random.insideUnitSphere * 5f;
            wreck.TurretBody = body;
            wreck.TurretSettleAt = now + TurretSettleSeconds;
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
            PB.Basics(smoke, new Vector2(3f, 5f), new Vector2(0.2f, 0.6f), new Vector2(1.2f, 2.4f));
            PB.Colors(smoke, PB.SmokeGradient(0.14f, 0.55f));
            PB.Grow(smoke, 0.8f, 3f);
            PB.Rise(smoke, 1.5f, 2.6f);
            var smokeEmission = smoke.emission;
            smokeEmission.enabled = true;
            smokeEmission.rateOverTime = 4f;

            fire.Play(true);
            return fire;
        }
    }
}
