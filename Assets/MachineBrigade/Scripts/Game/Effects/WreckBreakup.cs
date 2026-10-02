using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L7 (DECISIONS "Prompt 34 L5/L6/L7"): the pieces a wreck sheds by its class, its own model's parts
    /// (Part_wheel, Part_wing, Rotor, Tail_rotor ...; Tools/blender/mb_p34_parts.py): torn off the hull, thrown with a spin,
    /// trailing fire and smoke when burning, bouncing to rest on the ground, then sinking away. View only, simple kinematics
    /// (no physics engine), like the blown-off turret.
    /// </summary>
    internal sealed class WreckBreakup
    {
        private const float Gravity = 18f;

        private sealed class Piece
        {
            public Transform Part, Owner;
            public Vector3 Velocity, Spin;
            public bool Burning, Resting;
            public float Rest, Flame, Smoke, Until, SinkFrom = -1f;
        }

        private readonly List<Piece> _pieces = new();

        /// <summary>
        /// Pieces gone from view whose wreck is still drawn: hidden, not destroyed, because the wreck's view still holds their
        /// renderers (its detail levels and tint); destroyed once the wreck is.
        /// </summary>
        private readonly List<(Transform part, Transform owner)> _parked = new();
        private readonly Transform _root;
        private readonly ChunkThrower _chunks;
        private readonly FireSpots _fires;

        /// <summary>Pieces in the air or on the ground (tests, the budget log).</summary>
        public int Count => _pieces.Count;

        /// <summary>At most this many pieces at once; the oldest goes first.</summary>
        public const int Most = 48;

        public WreckBreakup(Transform parent, ChunkThrower chunks, FireSpots fires)
        {
            _root = new GameObject("Wreck Pieces").transform;
            _root.SetParent(parent, false);
            _chunks = chunks;
            _fires = fires;
        }

        /// <summary>
        /// Tears <paramref name="part"/> off its wreck and throws it: <paramref name="velocity"/> (m/s), <paramref name="spin"/>
        /// (degrees a second), trailing flame when <paramref name="burning"/>; it lies at <paramref name="rest"/> m above the
        /// ground once down and goes after <paramref name="life"/> s.
        /// </summary>
        public void Throw(Transform part, Transform owner, Vector3 velocity, Vector3 spin, bool burning, float rest, float life, float now)
        {
            if (part == null) return;
            if (_pieces.Count >= Most) Drop(0);
            part.SetParent(_root, true);
            _pieces.Add(new Piece
            {
                Part = part, Owner = owner, Velocity = velocity, Spin = spin, Burning = burning, Rest = rest, Until = now + life,
            });
        }

        public void Tick(float now, float dt)
        {
            for (var i = _parked.Count - 1; i >= 0; i--)
            {
                if (_parked[i].owner != null) continue;
                if (_parked[i].part != null) Object.Destroy(_parked[i].part.gameObject);
                _parked.RemoveAt(i);
            }
            for (var i = _pieces.Count - 1; i >= 0; i--)
            {
                var p = _pieces[i];
                if (p.Part == null)
                {
                    _pieces.RemoveAt(i);
                    continue;
                }
                if (p.SinkFrom >= 0f)
                {
                    var k = (now - p.SinkFrom) / 2f;
                    if (k >= 1f)
                    {
                        Drop(i);
                        continue;
                    }
                    var at = p.Part.position;
                    p.Part.position = new Vector3(at.x, p.Rest - 1.5f * k * k, at.z);
                    continue;
                }
                if (now >= p.Until && p.Resting)
                {
                    p.SinkFrom = now;
                    continue;
                }
                if (p.Resting) continue;
                p.Velocity.y -= Gravity * dt;
                var position = p.Part.position + p.Velocity * dt;
                p.Part.rotation = Quaternion.Euler(p.Spin * dt) * p.Part.rotation;
                _chunks?.Trails.Fly(ref p.Flame, ref p.Smoke, position, p.Burning, dt);
                if (position.y <= p.Rest && p.Velocity.y < 0f)
                {
                    position.y = p.Rest;
                    if (p.Velocity.y < -4f)
                    {
                        // Bounces, slower each time.
                        p.Velocity = new Vector3(p.Velocity.x * 0.45f, -p.Velocity.y * 0.25f, p.Velocity.z * 0.45f);
                        p.Spin *= 0.35f;
                        _chunks?.Trails.Impact(position);
                    }
                    else
                    {
                        p.Resting = true;
                        _chunks?.Trails.Land(position, 0f, p.Burning, now);
                        if (p.Burning) _fires?.Ignite(new Vector3(position.x, 0.3f, position.z), 0.45f, Random.Range(6f, 10f), now);
                    }
                }
                p.Part.position = position;
            }
        }

        public void Clear()
        {
            foreach (var p in _pieces)
                if (p.Part != null) Object.Destroy(p.Part.gameObject);
            _pieces.Clear();
            foreach (var (part, _) in _parked)
                if (part != null) Object.Destroy(part.gameObject);
            _parked.Clear();
        }

        private void Drop(int i)
        {
            var p = _pieces[i];
            _pieces.RemoveAt(i);
            if (p.Part == null) return;
            if (p.Owner == null)
            {
                Object.Destroy(p.Part.gameObject);
                return;
            }
            p.Part.gameObject.SetActive(false);
            _parked.Add((p.Part, p.Owner));
        }
    }
}
