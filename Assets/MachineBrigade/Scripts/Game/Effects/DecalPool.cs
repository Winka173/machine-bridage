using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Scorch marks as a ring buffer: the battlefield stays scarred, memory stays flat. Each mark
    /// is one of four blast patterns (a charred crater with soot rays thrown out around it, see
    /// Resources/Textures/Fx/fx_scorch), turned at random; one instanced material per pattern.
    /// </summary>
    internal sealed class DecalPool
    {
        private readonly List<Transform> _decals = new();
        private readonly List<MeshRenderer> _renderers = new();
        private readonly Material[] _patterns;
        private int _next;

        public DecalPool(Mesh quad, Transform parent, int capacity)
        {
            _patterns = FxMaterials.Shared.Scorch;
            var root = new GameObject("Scorch Marks").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < capacity; i++)
            {
                var go = new GameObject("Scorch");
                go.transform.SetParent(root, false);
                go.AddComponent<MeshFilter>().sharedMesh = quad;
                var renderer = go.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = _patterns[i % _patterns.Length];
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                go.SetActive(false);
                _decals.Add(go.transform);
                _renderers.Add(renderer);
            }
        }

        public void Place(Vector3 position, float size)
        {
            var decal = _decals[_next];
            _renderers[_next].sharedMaterial = _patterns[Random.Range(0, _patterns.Length)];
            // Tiny height steps keep overlapping marks from flickering against each other.
            var lift = 0.03f + (_next % 16) * 0.002f;
            _next = (_next + 1) % _decals.Count;
            decal.SetPositionAndRotation(new Vector3(position.x, lift, position.z), Quaternion.Euler(90f, Random.Range(0f, 360f), 0f));
            // The pattern's rays reach past the crater itself.
            var s = size * 1.35f;
            decal.localScale = new Vector3(s, s, 1f);
            decal.gameObject.SetActive(true);
        }
    }
}
