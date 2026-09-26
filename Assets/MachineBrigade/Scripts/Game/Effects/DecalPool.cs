using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>Scorch marks as a ring buffer: the battlefield stays scarred, memory stays flat.</summary>
    internal sealed class DecalPool
    {
        private readonly List<Transform> _decals = new();
        private int _next;

        public DecalPool(Mesh quad, Material material, Transform parent, int capacity)
        {
            var root = new GameObject("Scorch Marks").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < capacity; i++)
            {
                var go = new GameObject("Scorch");
                go.transform.SetParent(root, false);
                go.AddComponent<MeshFilter>().sharedMesh = quad;
                var renderer = go.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                go.SetActive(false);
                _decals.Add(go.transform);
            }
        }

        public void Place(Vector3 position, float size)
        {
            var decal = _decals[_next];
            // Tiny height steps keep overlapping marks from flickering against each other.
            var lift = 0.03f + (_next % 16) * 0.002f;
            _next = (_next + 1) % _decals.Count;
            decal.SetPositionAndRotation(new Vector3(position.x, lift, position.z), Quaternion.Euler(90f, Random.Range(0f, 360f), 0f));
            decal.localScale = new Vector3(size, size, 1f);
            decal.gameObject.SetActive(true);
        }
    }
}
