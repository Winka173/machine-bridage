using System.Collections.Generic;
using MachineBrigade.Game.Views;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// A ship going down (prompt 16 B.5): it lists further and further to one side; the big flagship then
    /// breaks its back (a second copy of it is the stern half: the bow half rears up bow first, the stern
    /// half stern first, each sinking below the water, which hides whatever of it is under), smaller ships
    /// just roll over and go under. The fires and smoke of its broken parts (prompt 9) and its magazines
    /// cooking off (the sim's blasts along the hull) play meanwhile. No physics: simple kinematics.
    /// </summary>
    internal sealed class ShipSinking
    {
        private sealed class Sinker
        {
            public Transform Bow, Stern;
            public Vector3 Start;
            public Quaternion Rotation;
            public float Born, Length, Height, Side;
            public bool Breaks;
        }

        private readonly List<Sinker> _ships = new();

        /// <summary>Prompt 34 L7: a ship at least this long (m) breaks in two; a shorter one rolls over and goes under.</summary>
        internal const float BreakFrom = 24f;

        public int Count => _ships.Count;

        /// <summary>Takes a destroyed ship's view over: it sinks, then is removed.</summary>
        public void Add(VehicleView view, float now)
        {
            var root = view.Root;
            var def = view.Def;
            var length = def.Length > 0f ? def.Length : def.Radius * 2f;
            var sinker = new Sinker
            {
                Bow = root, Start = root.position, Rotation = root.rotation, Born = now, Length = length,
                Height = Mathf.Max(4f, length * 0.25f), Side = (_ships.Count & 1) == 0 ? 1f : -1f,
                // Only the big ships break their backs (prompt 34 L7: the corvettes and cruisers too, from 24 m; boats roll over).
                Breaks = length >= BreakFrom,
            };
            if (sinker.Breaks)
            {
                sinker.Stern = Object.Instantiate(root.gameObject, root.parent).transform;
                sinker.Stern.name = root.name + " (stern)";
            }
            _ships.Add(sinker);
        }

        public void Tick(float now)
        {
            for (var i = _ships.Count - 1; i >= 0; i--)
            {
                var s = _ships[i];
                var t = now - s.Born;
                // 0-5 s: it lists; then it breaks (or rolls) and goes under by 18 s.
                var list = Mathf.Lerp(0f, 14f, Mathf.Clamp01(t / 5f)) * s.Side;
                var down = Mathf.Clamp01((t - 4f) / 14f);
                var depth = s.Height * down * down;
                if (s.Breaks)
                {
                    var rear = Mathf.Lerp(0f, 26f, Mathf.Clamp01((t - 4f) / 6f));
                    var forward = s.Rotation * Vector3.forward;
                    // Each half pivots at the break amidships: the bow half's stern end goes down, and so on.
                    Place(s.Bow, s.Start + forward * (s.Length * 0.05f) + Vector3.down * depth, s.Rotation * Quaternion.Euler(-rear, 0f, list));
                    Place(s.Stern, s.Start - forward * (s.Length * 0.05f) + Vector3.down * depth, s.Rotation * Quaternion.Euler(rear, 0f, list));
                }
                else
                {
                    var roll = Mathf.Lerp(list, 70f * s.Side, down);
                    Place(s.Bow, s.Start + Vector3.down * depth, s.Rotation * Quaternion.Euler(0f, 0f, roll));
                }
                if (t < 20f) continue;
                if (s.Bow != null) Object.Destroy(s.Bow.gameObject);
                if (s.Stern != null) Object.Destroy(s.Stern.gameObject);
                _ships.RemoveAt(i);
            }
        }

        private static void Place(Transform t, Vector3 at, Quaternion rotation)
        {
            if (t == null) return;
            t.SetPositionAndRotation(at, rotation);
        }
    }
}
