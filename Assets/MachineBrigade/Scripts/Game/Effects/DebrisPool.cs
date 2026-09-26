using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Voxel chunks thrown by destroyed props. Physics here is purely cosmetic; the pool
    /// caps how many pieces exist, and each shrinks away after a few seconds.
    /// </summary>
    internal sealed class DebrisPool
    {
        private const float ShrinkSeconds = 0.6f;

        private sealed class Piece
        {
            public GameObject GameObject;
            public MeshFilter Filter;
            public MeshRenderer Renderer;
            public BoxCollider Collider;
            public Rigidbody Body;
            public float Expires;
            public bool Active;
        }

        private readonly List<Piece> _pieces = new();

        public DebrisPool(Transform parent, int capacity)
        {
            var root = new GameObject("Debris").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < capacity; i++)
            {
                var go = new GameObject("Chunk");
                go.transform.SetParent(root, false);
                var piece = new Piece
                {
                    GameObject = go,
                    Filter = go.AddComponent<MeshFilter>(),
                    Renderer = go.AddComponent<MeshRenderer>(),
                    Collider = go.AddComponent<BoxCollider>(),
                    Body = go.AddComponent<Rigidbody>(),
                };
                piece.Renderer.shadowCastingMode = ShadowCastingMode.On;
                piece.Body.mass = 2f;
                piece.Body.angularDamping = 0.5f;
                go.SetActive(false);
                _pieces.Add(piece);
            }
        }

        public void Throw(ChunkModel chunk, Vector3 position, Quaternion rotation, Vector3 blastOrigin, float force, float now)
        {
            var piece = Acquire();
            piece.Filter.sharedMesh = chunk.Mesh;
            piece.Renderer.sharedMaterials = chunk.Materials;
            piece.Collider.center = chunk.Mesh.bounds.center;
            piece.Collider.size = chunk.Mesh.bounds.size;
            piece.GameObject.transform.SetPositionAndRotation(position, rotation);
            piece.GameObject.transform.localScale = Vector3.one;
            piece.GameObject.SetActive(true);

            var away = position - blastOrigin;
            away.y = 0f;
            var direction = (away.normalized + Vector3.up * Random.Range(0.8f, 1.6f)).normalized;
            piece.Body.linearVelocity = direction * Random.Range(force * 0.5f, force);
            piece.Body.angularVelocity = Random.insideUnitSphere * 7f;
            piece.Expires = now + Random.Range(4f, 6f);
            piece.Active = true;
        }

        public void Tick(float now)
        {
            foreach (var piece in _pieces)
            {
                if (!piece.Active) continue;
                var remaining = piece.Expires - now;
                if (remaining <= 0f)
                {
                    piece.Active = false;
                    piece.GameObject.SetActive(false);
                }
                else if (remaining < ShrinkSeconds)
                {
                    piece.GameObject.transform.localScale = Vector3.one * (remaining / ShrinkSeconds);
                }
            }
        }

        private Piece Acquire()
        {
            Piece oldest = null;
            foreach (var piece in _pieces)
            {
                if (!piece.Active) return piece;
                if (oldest == null || piece.Expires < oldest.Expires) oldest = piece;
            }
            return oldest;
        }
    }
}
