using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Chunks thrown by destroyed props and crashing aircraft. They fly on simple ballistic arcs,
    /// bounce once or twice and settle, then shrink away. No physics engine is involved (PhysX
    /// stepping dozens of bodies cost up to 15 ms a frame on the device), and all pieces are drawn
    /// with GPU instancing, a handful of draw calls however many are flying.
    /// </summary>
    internal sealed class DebrisPool
    {
        private const float ShrinkSeconds = 0.6f;
        private const float Gravity = 18f;

        private struct Piece
        {
            public Mesh Mesh;
            public Material[] Materials;
            public Vector3 Position, Velocity, Spin;
            public Quaternion Rotation;
            public float Rest, Expires;
            public bool Settled;
        }

        private readonly Piece[] _pieces;
        private readonly Dictionary<(Mesh, int, Material), List<Matrix4x4>> _batches = new();
        private readonly List<Matrix4x4[]> _arrays = new();
        private int _count;

        public DebrisPool(int capacity)
        {
            _pieces = new Piece[Mathf.Max(1, capacity)];
        }

        public void Throw(ChunkModel chunk, Vector3 position, Quaternion rotation, Vector3 blastOrigin, float force, float now)
        {
            var index = Acquire();
            var away = position - blastOrigin;
            away.y = 0f;
            var direction = (away.normalized + Vector3.up * Random.Range(0.8f, 1.6f)).normalized;
            _pieces[index] = new Piece
            {
                Mesh = chunk.Mesh,
                Materials = chunk.Materials,
                Position = position,
                Velocity = direction * Random.Range(force * 0.5f, force),
                Spin = Random.insideUnitSphere * 400f,
                Rotation = rotation,
                // Rest with the mesh's lowest point on the ground.
                Rest = Mathf.Max(0.02f, -chunk.Mesh.bounds.min.y * 0.8f),
                Expires = now + Random.Range(5f, 8f),
            };
        }

        public void Tick(float now, float dt)
        {
            for (var i = 0; i < _count; i++)
            {
                ref var p = ref _pieces[i];
                if (p.Mesh == null) continue;
                if (now >= p.Expires)
                {
                    p.Mesh = null;
                    continue;
                }
                if (p.Settled) continue;
                p.Velocity.y -= Gravity * dt;
                p.Position += p.Velocity * dt;
                p.Rotation = Quaternion.Euler(p.Spin * dt) * p.Rotation;
                if (p.Position.y > p.Rest || p.Velocity.y > 0f) continue;
                p.Position.y = p.Rest;
                if (p.Velocity.y < -3f)
                {
                    // Bounce, losing most of the energy.
                    p.Velocity = new Vector3(p.Velocity.x * 0.5f, -p.Velocity.y * 0.3f, p.Velocity.z * 0.5f);
                    p.Spin *= 0.5f;
                }
                else
                {
                    p.Settled = true;
                }
            }
        }

        public void Draw(float now)
        {
            foreach (var list in _batches.Values) list.Clear();
            for (var i = 0; i < _count; i++)
            {
                ref var p = ref _pieces[i];
                if (p.Mesh == null) continue;
                var remaining = p.Expires - now;
                var scale = remaining < ShrinkSeconds ? Mathf.Max(0.01f, remaining / ShrinkSeconds) : 1f;
                var matrix = Matrix4x4.TRS(p.Position, p.Rotation, Vector3.one * scale);
                for (var sub = 0; sub < p.Mesh.subMeshCount && sub < p.Materials.Length; sub++)
                {
                    var key = (p.Mesh, sub, p.Materials[sub]);
                    if (!_batches.TryGetValue(key, out var list)) _batches[key] = list = new List<Matrix4x4>();
                    list.Add(matrix);
                }
            }

            var arrayIndex = 0;
            foreach (var ((mesh, sub, material), list) in _batches)
            {
                if (list.Count == 0) continue;
                if (arrayIndex >= _arrays.Count) _arrays.Add(new Matrix4x4[_pieces.Length]);
                var array = _arrays[arrayIndex++];
                list.CopyTo(array);
                var parameters = new RenderParams(material)
                {
                    shadowCastingMode = ShadowCastingMode.Off,
                    receiveShadows = true,
                    worldBounds = new Bounds(Vector3.zero, Vector3.one * 2000f),
                };
                Graphics.RenderMeshInstanced(parameters, mesh, sub, array, list.Count);
            }
        }

        public void Clear()
        {
            for (var i = 0; i < _pieces.Length; i++) _pieces[i].Mesh = null;
            _count = 0;
        }

        private int Acquire()
        {
            var oldest = 0;
            for (var i = 0; i < _count; i++)
            {
                if (_pieces[i].Mesh == null) return i;
                if (_pieces[i].Expires < _pieces[oldest].Expires) oldest = i;
            }
            return _count < _pieces.Length ? _count++ : oldest;
        }
    }
}
