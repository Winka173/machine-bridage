using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Scorch marks as a ring buffer: the battlefield stays scarred, memory stays flat. Each mark
    /// is one of four blast patterns (a charred crater with soot rays thrown out around it, see
    /// Resources/Textures/Fx/fx_scorch), turned at random; one instanced material per pattern.
    /// Fix prompt L6: a mark may have a life (the size band's, <see cref="EffectLife"/>); it then closes and goes.
    /// </summary>
    internal sealed class DecalPool
    {
        private readonly List<Transform> _decals = new();
        private readonly List<MeshRenderer> _renderers = new();

        /// <summary>Fix prompt L6: each mark's size as placed, when it was placed and how long it lasts (infinity: until the pool wraps round).</summary>
        private readonly List<(float size, float born, float life)> _ages = new();

        /// <summary>Fix prompt L6: a mark with a life closes over its last share of it (it does not blink out), at least this long (s).</summary>
        private const float CloseShare = 0.25f, ShortestClose = 2f;

        private float _now;
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
                _ages.Add((0f, 0f, float.PositiveInfinity));
            }
        }

        /// <param name="life">
        /// Fix prompt L6: how long the mark lasts (s; the size band's, EffectLife: 10 s for 20-40 mm up to 60 s for 406 mm);
        /// infinity keeps it until the pool wraps round (a wreck's burn mark). 0 or less places nothing.
        /// </param>
        public void Place(Vector3 position, float size, float life = float.PositiveInfinity)
        {
            if (life <= 0f) return;
            _ages[_next] = (size * 1.35f, _now, life);
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

        /// <summary>
        /// Fix prompt L6: marks with a life close over their last quarter (they shrink into the ground's dust, the shared
        /// instanced material has no fade of its own) and go when it is up. Every frame.
        /// </summary>
        public void Tick(float now)
        {
            _now = now;
            for (var i = 0; i < _decals.Count; i++)
            {
                var (size, born, life) = _ages[i];
                if (float.IsPositiveInfinity(life) || !_decals[i].gameObject.activeSelf) continue;
                var left = born + life - now;
                if (left <= 0f)
                {
                    _decals[i].gameObject.SetActive(false);
                    _ages[i] = (size, born, float.PositiveInfinity);
                    continue;
                }
                var close = Mathf.Max(ShortestClose, life * CloseShare);
                if (left >= close) continue;
                var k = Mathf.Clamp01(left / close);
                var drawn = size * (0.35f + 0.65f * k * k * (3f - 2f * k));
                _decals[i].localScale = new Vector3(drawn, drawn, 1f);
            }
        }
    }
}
