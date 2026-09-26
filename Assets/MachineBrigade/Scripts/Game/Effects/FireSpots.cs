using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fires that keep burning where fuel tanks blew up, barrels burst and buildings collapsed.
    /// Pooled: when every spot is busy the oldest is moved, so a long battle never piles up
    /// particle systems.
    /// </summary>
    internal sealed class FireSpots
    {
        private sealed class Spot
        {
            public Transform Root;
            public ParticleSystem Fire;
            public ParticleSystem Smoke;
            public float Until;
            public float StartedAt = -1000f;
            public bool Burning;
        }

        private readonly List<Spot> _spots = new();

        public FireSpots(MaterialLibrary m, Transform parent, int capacity)
        {
            var root = new GameObject("Fire Spots").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < capacity; i++) _spots.Add(Create(m, root));
        }

        public void Ignite(Vector3 position, float size, float seconds, float now)
        {
            Spot spot = null;
            foreach (var s in _spots)
            {
                if (!s.Burning && (spot == null || s.StartedAt < spot.StartedAt)) spot = s;
            }
            if (spot == null)
            {
                foreach (var s in _spots)
                    if (spot == null || s.StartedAt < spot.StartedAt) spot = s;
            }
            spot.Root.position = position;
            spot.Root.localScale = Vector3.one * size;
            spot.Until = now + seconds;
            spot.StartedAt = now;
            spot.Burning = true;
            var emission = spot.Fire.emission;
            emission.enabled = true;
            var smoke = spot.Smoke.emission;
            smoke.enabled = true;
            spot.Fire.Play(true);
        }

        public void Tick(float now)
        {
            foreach (var spot in _spots)
            {
                if (!spot.Burning || now < spot.Until) continue;
                spot.Burning = false;
                var emission = spot.Fire.emission;
                emission.enabled = false;
                var smoke = spot.Smoke.emission;
                smoke.enabled = false;
            }
        }

        private static Spot Create(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Fire").transform;
            root.SetParent(parent, false);
            var fire = PB.Create(root, "Flames", m.Fire);
            var main = fire.main;
            main.loop = true;
            main.duration = 2f;
            main.scalingMode = ParticleSystemScalingMode.Hierarchy;
            PB.Basics(fire, new Vector2(0.5f, 1f), new Vector2(1.2f, 2.6f), new Vector2(0.9f, 1.8f));
            var shape = fire.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 15f;
            shape.radius = 0.9f;
            shape.rotation = new Vector3(-90f, 0f, 0f);
            PB.Colors(fire, PB.FireGradient);
            PB.Grow(fire, 1f, 0.3f);
            var emission = fire.emission;
            emission.enabled = false;
            emission.rateOverTime = 18f;

            var smoke = PB.Create(fire.transform, "Smoke", m.Smoke);
            var smokeMain = smoke.main;
            smokeMain.loop = true;
            smokeMain.duration = 3f;
            smokeMain.scalingMode = ParticleSystemScalingMode.Hierarchy;
            PB.Basics(smoke, new Vector2(2.6f, 4.2f), new Vector2(0.2f, 0.5f), new Vector2(1f, 1.9f));
            PB.Colors(smoke, PB.Plume(0.14f, 0.45f, 0.32f));
            PB.Grow(smoke, 0.7f, 2.4f);
            PB.Rise(smoke, 1.8f, 2.8f);
            var smokeEmission = smoke.emission;
            smokeEmission.enabled = false;
            smokeEmission.rateOverTime = 5f;

            return new Spot { Root = root, Fire = fire, Smoke = smoke };
        }
    }
}
