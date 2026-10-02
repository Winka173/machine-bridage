using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Glowing shells flying from muzzle to impact over the simulated travel time, so what
    /// the player sees lines up with when damage lands. Artillery shells fly an arc, and heavy
    /// shells leave a smoke trail behind them.
    /// </summary>
    internal sealed class TracerPool
    {
        private const float TrailSpacing = 0.45f; // metres between smoke puffs

        /// <summary>How much of its length a streak shows on its first frame, reaching out of the muzzle.</summary>
        private const float FirstShare = 0.4f;

        private sealed class Tracer
        {
            public Transform Transform;
            public Vector3 From, To;
            public float Start, Duration, Arc, Trail, PuffT, PuffStep, Thickness, Length;

            /// <summary>A beam: one bar centred on its line (a round's streak trails its round instead).</summary>
            public bool Centred;
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

        /// <param name="delay">Seconds before the shell appears; staggers machine-gun bursts.</param>
        /// <param name="trail">Smoke puff size left behind in flight; 0 for none.</param>
        public void Launch(Vector3 from, Vector3 to, float duration, float arc, float thickness, float length, float now,
            float delay = 0f, float trail = 0f) =>
            Start(from, to, duration, arc, thickness, length, now, delay, trail, false);

        private void Start(Vector3 from, Vector3 to, float duration, float arc, float thickness, float length, float now,
            float delay, float trail, bool centred)
        {
            // A free slot if there is one, so a shell in flight is not snatched away.
            var tracer = _tracers[_next];
            for (var k = 0; k < _tracers.Count && tracer.Active; k++)
            {
                _next = (_next + 1) % _tracers.Count;
                tracer = _tracers[_next];
            }
            _next = (_next + 1) % _tracers.Count;
            tracer.From = from;
            tracer.To = to;
            // Fix prompt L4: on the shot clock, so it lands on the Sim tick its damage does (ShotClock).
            tracer.Start = ShotClock.Map(now) + delay;
            tracer.Duration = Mathf.Max(0.03f, duration);
            tracer.Arc = arc;
            tracer.Trail = trail;
            tracer.PuffT = 0f;
            tracer.PuffStep = TrailSpacing / Mathf.Max(1f, Vector3.Distance(from, to) + arc);
            tracer.Active = true;
            tracer.Thickness = thickness;
            tracer.Length = length;
            tracer.Centred = centred;
            tracer.Transform.localScale = new Vector3(thickness, thickness, length);
            tracer.Transform.gameObject.SetActive(delay <= 0f);
            Place(tracer, 0f);
        }

        /// <summary>A laser: one straight bar from muzzle to target, held for <paramref name="duration"/> seconds.</summary>
        public void Beam(Vector3 from, Vector3 to, float duration, float thickness, float now, float delay = 0f)
        {
            var direction = to - from;
            var length = direction.magnitude;
            if (length < 0.1f) return;
            var mid = (from + to) * 0.5f;
            // A tracer that barely moves: centred on the middle of the line, as long as the line.
            Start(mid, mid + direction / length * 0.01f, duration, 0f, thickness, length, now, delay, 0f, true);
        }

        public void Tick(float now, Emitters emitters)
        {
            now = ShotClock.Map(now);
            foreach (var tracer in _tracers)
            {
                if (!tracer.Active) continue;
                if (now < tracer.Start) continue;
                if (!tracer.Transform.gameObject.activeSelf) tracer.Transform.gameObject.SetActive(true);
                var t = (now - tracer.Start) / tracer.Duration;
                if (t >= 1f)
                {
                    tracer.Active = false;
                    tracer.Transform.gameObject.SetActive(false);
                    continue;
                }
                Place(tracer, t);
                if (tracer.Trail <= 0f) continue;
                // Fill the path covered since the last frame so the trail stays continuous.
                while (tracer.PuffT + tracer.PuffStep <= t)
                {
                    tracer.PuffT += tracer.PuffStep;
                    emitters.Trail(PositionAt(tracer, tracer.PuffT), tracer.Trail);
                }
            }
        }

        private static Vector3 PositionAt(Tracer tracer, float t) =>
            Vector3.Lerp(tracer.From, tracer.To, t) + Vector3.up * (tracer.Arc * 4f * t * (1f - t));

        private static void Place(Tracer tracer, float t)
        {
            if (tracer.Centred)
            {
                var direction = tracer.To - tracer.From + Vector3.up * (tracer.Arc * 4f * (1f - 2f * t));
                tracer.Transform.position = PositionAt(tracer, t);
                if (direction.sqrMagnitude > 1e-6f) tracer.Transform.rotation = Quaternion.LookRotation(direction);
                return;
            }
            // The round is the head of its streak and the glow trails behind it, never back past the
            // muzzle: on its first frame the streak reaches out of the barrel's tip, then runs its
            // full length behind the round and ends on the target as it lands.
            var path = Mathf.Max(0.01f, Vector3.Distance(tracer.From, tracer.To) + tracer.Arc);
            var share = Mathf.Min(1f, tracer.Length / path);
            var head = Mathf.Min(1f, Mathf.Max(t, share * FirstShare));
            var tail = Mathf.Max(0f, head - share);
            var back = PositionAt(tracer, tail);
            var front = PositionAt(tracer, head);
            var along = front - back;
            var length = along.magnitude;
            if (length < 1e-4f) along = tracer.To - tracer.From;
            tracer.Transform.position = (back + front) * 0.5f;
            if (along.sqrMagnitude > 1e-6f) tracer.Transform.rotation = Quaternion.LookRotation(along);
            tracer.Transform.localScale = new Vector3(tracer.Thickness, tracer.Thickness, Mathf.Max(0.02f, length));
        }

        /// <summary>Tests: the back and front ends of the drawn streaks (or beams) now in flight.</summary>
        internal IEnumerable<(Vector3 back, Vector3 front)> Streaks()
        {
            foreach (var tracer in _tracers)
            {
                if (!tracer.Active || !tracer.Transform.gameObject.activeSelf) continue;
                var half = tracer.Transform.forward * (tracer.Transform.localScale.z * 0.5f);
                yield return (tracer.Transform.position - half, tracer.Transform.position + half);
            }
        }
    }
}
