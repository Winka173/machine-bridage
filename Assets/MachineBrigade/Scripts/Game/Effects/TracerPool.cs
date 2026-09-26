using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Glowing shells flying from muzzle to impact over the simulated travel time, so what
    /// the player sees lines up with when damage lands. Artillery shells fly an arc.
    /// </summary>
    internal sealed class TracerPool
    {
        private sealed class Tracer
        {
            public Transform Transform;
            public Vector3 From, To;
            public float Start, Duration, Arc;
            public bool Active;
        }

        private readonly List<Tracer> _tracers = new();
        private int _next;

        public TracerPool(Mesh mesh, Material material, Transform parent, int capacity)
        {
            var root = new GameObject("Tracers").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < capacity; i++)
            {
                var go = new GameObject("Tracer");
                go.transform.SetParent(root, false);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var renderer = go.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                go.SetActive(false);
                _tracers.Add(new Tracer { Transform = go.transform });
            }
        }

        public void Launch(Vector3 from, Vector3 to, float duration, float arc, float thickness, float length, float now)
        {
            var tracer = _tracers[_next];
            _next = (_next + 1) % _tracers.Count;
            tracer.From = from;
            tracer.To = to;
            tracer.Start = now;
            tracer.Duration = Mathf.Max(0.03f, duration);
            tracer.Arc = arc;
            tracer.Active = true;
            tracer.Transform.localScale = new Vector3(thickness, thickness, length);
            tracer.Transform.gameObject.SetActive(true);
            Place(tracer, 0f);
        }

        public void Tick(float now)
        {
            foreach (var tracer in _tracers)
            {
                if (!tracer.Active) continue;
                var t = (now - tracer.Start) / tracer.Duration;
                if (t >= 1f)
                {
                    tracer.Active = false;
                    tracer.Transform.gameObject.SetActive(false);
                    continue;
                }
                Place(tracer, t);
            }
        }

        private static void Place(Tracer tracer, float t)
        {
            var position = Vector3.Lerp(tracer.From, tracer.To, t) + Vector3.up * (tracer.Arc * 4f * t * (1f - t));
            var direction = tracer.To - tracer.From + Vector3.up * (tracer.Arc * 4f * (1f - 2f * t));
            tracer.Transform.position = position;
            if (direction.sqrMagnitude > 1e-6f) tracer.Transform.rotation = Quaternion.LookRotation(direction);
        }
    }
}
