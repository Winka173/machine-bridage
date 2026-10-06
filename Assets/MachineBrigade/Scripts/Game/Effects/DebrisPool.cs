using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Solid chunks thrown by blasts, destroyed vehicles and props: earth, rubble and wreckage.
    /// They fly on simple ballistic arcs, bounce and skid, settle lying flat, then shrink away.
    /// Burning chunks trail fire and smoke while they fly (<see cref="ChunkTrails"/>) and keep
    /// burning where they land. No physics engine is involved (PhysX stepping dozens of bodies
    /// cost up to 15 ms a frame on the device), and all pieces are drawn with GPU instancing: one
    /// draw call per kind of chunk however many are flying.
    /// </summary>
    internal sealed class DebrisPool
    {
        private const float ShrinkSeconds = 0.6f;
        private const float Gravity = 18f;

        private struct Piece
        {
            public Mesh Mesh;
            public Material[] Materials;
            public Vector3 Position, Velocity, Spin, Scale;
            public Quaternion Rotation;
            public float Rest, Expires, BurnUntil, FlameDebt, SmokeDebt;
            public int Bounces;
            public bool Settled, Fuel;
        }

        private readonly Piece[] _pieces;
        private readonly Dictionary<(Mesh, int, Material), List<Matrix4x4>> _batches = new();
        private readonly List<Matrix4x4[]> _arrays = new();
        private int _count;

        public DebrisPool(int capacity)
        {
            _pieces = new Piece[Mathf.Max(1, capacity)];
        }

        /// <summary>Fire and smoke behind burning chunks; null: they burn unseen.</summary>
        public ChunkTrails Trails { get; set; }

        public int Capacity => _pieces.Length;

        /// <summary>Pieces flying or lying on the ground now.</summary>
        public int Active
        {
            get
            {
                var n = 0;
                for (var i = 0; i < _count; i++)
                    if (_pieces[i].Mesh != null) n++;
                return n;
            }
        }

        private int _thrown;

        /// <summary>A chunk thrown away from <paramref name="blastOrigin"/> (props falling apart, crashes).</summary>
        public void Throw(ChunkModel chunk, Vector3 position, Quaternion rotation, Vector3 blastOrigin, float force, float now)
        {
            // MVA W2-B (spec part BS): Reduced effects throws every other chunk.
            if (MachineBrigade.Game.Match.MatchSettings.ReducedEffects && (++_thrown & 1) == 0) return;
            var away = position - blastOrigin;
            away.y = 0f;
            var direction = (away.normalized + Vector3.up * Random.Range(0.8f, 1.6f)).normalized;
            Launch(chunk, position, rotation, direction * Random.Range(force * 0.5f, force), Vector3.one, now, Random.Range(5f, 8f));
        }

        /// <summary>
        /// A chunk flying off at <paramref name="velocity"/>, scaled by <paramref name="scale"/>,
        /// gone after <paramref name="life"/> seconds. A burning one trails fire and smoke for
        /// <paramref name="burn"/> seconds (flight and ground together); <paramref name="fuel"/>
        /// marks a gob of burning fuel (napalm), which lands as a bigger fire.
        /// </summary>
        public void Launch(ChunkModel chunk, Vector3 position, Quaternion rotation, Vector3 velocity, Vector3 scale, float now, float life,
            float burn = 0f, bool fuel = false)
        {
            var index = Acquire();
            var bounds = chunk.Mesh.bounds;
            _pieces[index] = new Piece
            {
                Mesh = chunk.Mesh,
                Materials = chunk.Materials,
                Position = position,
                Velocity = velocity,
                Spin = Random.insideUnitSphere * Random.Range(250f, 600f),
                Scale = scale,
                Rotation = rotation,
                // In flight it tumbles; it lands on its broadest side (see Settle).
                Rest = Mathf.Max(0.02f, Mathf.Min(bounds.extents.x * scale.x, Mathf.Min(bounds.extents.y * scale.y, bounds.extents.z * scale.z))),
                Expires = now + life,
                BurnUntil = burn > 0f ? now + burn : 0f,
                Fuel = fuel,
            };
        }

        public void Tick(float now, float dt)
        {
            var trails = Trails;
            for (var i = 0; i < _count; i++)
            {
                ref var p = ref _pieces[i];
                if (p.Mesh == null) continue;
                if (now >= p.Expires)
                {
                    p.Mesh = null;
                    continue;
                }
                var burning = now < p.BurnUntil;
                if (p.Settled)
                {
                    if (burning && trails != null) trails.Smoulder(ref p.SmokeDebt, p.Position, dt);
                    continue;
                }
                p.Velocity.y -= Gravity * dt;
                p.Position += p.Velocity * dt;
                // Renormalised each frame: the product drifts off unit length and TRS then asserts.
                p.Rotation = Quaternion.Normalize(Quaternion.Euler(p.Spin * dt) * p.Rotation);
                if (burning && trails != null) trails.Fly(ref p.FlameDebt, ref p.SmokeDebt, p.Position, p.Fuel, dt);
                if (p.Position.y > p.Rest || p.Velocity.y > 0f) continue;
                p.Position.y = p.Rest;
                if (p.Velocity.y < -3f && p.Bounces < 3)
                {
                    // Bounce and skid on, losing most of the energy.
                    p.Bounces++;
                    p.Velocity = new Vector3(p.Velocity.x * 0.55f, -p.Velocity.y * 0.3f, p.Velocity.z * 0.55f);
                    p.Spin *= 0.5f;
                    if (burning && trails != null) trails.Impact(p.Position);
                }
                else
                {
                    Settle(ref p);
                    if (burning && trails != null) trails.Land(p.Position, p.BurnUntil - now, p.Fuel, now);
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
                var shrink = remaining < ShrinkSeconds ? Mathf.Max(0.01f, remaining / ShrinkSeconds) : 1f;
                var matrix = Matrix4x4.TRS(p.Position, p.Rotation, p.Scale * shrink);
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

        /// <summary>Comes to rest lying on its broadest side, keeping its heading.</summary>
        private static void Settle(ref Piece p)
        {
            p.Settled = true;
            var e = Vector3.Scale(p.Mesh.bounds.extents, p.Scale);
            var thin = e.x <= e.y && e.x <= e.z ? Vector3.right : e.y <= e.z ? Vector3.up : Vector3.forward;
            var axis = p.Rotation * thin;
            var up = Vector3.Dot(axis, Vector3.up) >= 0f ? Vector3.up : Vector3.down;
            p.Rotation = Quaternion.FromToRotation(axis, up) * p.Rotation;
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
