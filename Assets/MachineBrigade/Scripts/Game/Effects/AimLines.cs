using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 29 G1 (ASSET_DEBT "Gungnir's line warning"): a pierce shot's aiming line, from the gun to the aim, for its
    /// warning (the 3 s from the sim's FiredWith event to the slug's arrival). The big-attack outlines' look: the unlit
    /// HDR strike-warning material on a view-facing LineRenderer (never a property block), thin at first and wider and
    /// brighter as the shot comes, blinking in the last second. A small pool; the oldest line is reused. View only.
    /// </summary>
    internal sealed class AimLines
    {
        private const int Count = 4;

        private readonly List<(LineRenderer line, float start, float end)> _lines = new();
        private readonly Vector3[] _ends = new Vector3[2];

        public AimLines(MaterialLibrary materials, Transform parent)
        {
            var root = new GameObject("Aim Lines").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Count; i++)
            {
                var go = new GameObject("Aim Line");
                go.transform.SetParent(root, false);
                var line = go.AddComponent<LineRenderer>();
                line.sharedMaterial = materials.StrikeWarning;
                line.useWorldSpace = true;
                line.loop = false;
                line.positionCount = 2;
                line.alignment = LineAlignment.View;
                line.numCapVertices = 2;
                line.shadowCastingMode = ShadowCastingMode.Off;
                line.receiveShadows = false;
                line.widthMultiplier = 0.3f;
                line.enabled = false;
                _lines.Add((line, 0f, 0f));
            }
        }

        /// <summary>Draws the line from <paramref name="from"/> to <paramref name="to"/> for <paramref name="seconds"/>.</summary>
        public void Show(Vector3 from, Vector3 to, float seconds, float now)
        {
            var pick = 0;
            for (var i = 0; i < _lines.Count; i++)
            {
                if (!_lines[i].line.enabled)
                {
                    pick = i;
                    break;
                }
                if (_lines[i].end < _lines[pick].end) pick = i;
            }
            var line = _lines[pick].line;
            _ends[0] = from;
            _ends[1] = to;
            line.SetPositions(_ends);
            line.enabled = true;
            _lines[pick] = (line, now, now + Mathf.Max(0.5f, seconds));
        }

        public void Tick(float now)
        {
            for (var i = 0; i < _lines.Count; i++)
            {
                var (line, start, end) = _lines[i];
                if (!line.enabled) continue;
                if (now >= end)
                {
                    line.enabled = false;
                    continue;
                }
                var progress = Mathf.Clamp01((now - start) / Mathf.Max(0.01f, end - start));
                var left = end - now;
                // The last second: it blinks (on most of the time) so the moment reads.
                var blink = left < 1f && Mathf.Repeat(now * 8f, 1f) < 0.3f;
                line.widthMultiplier = blink ? 0.12f : Mathf.Lerp(0.25f, 0.7f, progress);
            }
        }
    }
}
