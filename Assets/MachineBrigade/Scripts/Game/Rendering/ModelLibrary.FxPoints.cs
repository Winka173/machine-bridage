using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    public sealed partial class ModelLibrary
    {
        /// <summary>
        /// Prompt 29 5.5: the effect points on a model's flare dispensers (`Flares`, Tools/blender/mb_p29_details.py
        /// flare_tubes) and APS cassettes (`Aps_cluster`): one empty per side and row, at the middle of its tubes, made on
        /// the template before its meshes merge (the part's origin is its parent's pivot, so the node itself says nothing
        /// of where the tubes are). A flare point looks down and out (the way the flares leave); an APS point up and out.
        /// The view finds them by these names (<c>VehicleView.FlarePoints</c>, <c>ApsPoints</c>).
        /// </summary>
        public const string FlarePointName = "FxPoint_flares", ApsPointName = "FxPoint_aps";

        /// <summary>
        /// Fix prompt L4: the empties a model's flares leave from (Tools/blender/flare_mounts.py): Mount_Flare_L / _R on the rear
        /// fuselage or tail boom, Mount_Flare_TL / _TR at the tail root, a big aircraft's second row _L2 / _R2. Never a bare
        /// `Mount_Flare`: <see cref="MountPattern"/> (`Mount_&lt;letters&gt;`) would read it as a weapon mount's yaw pivot; the
        /// suffix keeps these out of it, out of the muzzle and part patterns and out of MuzzleGeometryAudit's groups.
        /// </summary>
        public const string FlareMountPrefix = "Mount_Flare_";

        /// <summary>A Mount_Flare_* empty (Blender's .001 suffixes too).</summary>
        public static bool IsFlareMount(string name) => name != null && name.StartsWith(FlareMountPrefix, StringComparison.Ordinal);

        /// <summary>Tubes closer than this along the hull (model metres) are one row; farther apart, two (a big aircraft's).</summary>
        private const float EffectRowGap = 0.15f;

        private static readonly Regex NumberSuffix = new(@"\.\d+$");

        private static void AddEffectPoints(Transform root)
        {
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null || !filter.sharedMesh.isReadable) continue;
                var name = NumberSuffix.Replace(filter.name, string.Empty);
                var flares = string.Equals(name, "Flares", StringComparison.OrdinalIgnoreCase);
                var aps = string.Equals(name, "Aps_cluster", StringComparison.OrdinalIgnoreCase);
                if (!flares && !aps) continue;
                var vertices = filter.sharedMesh.vertices;
                if (vertices.Length == 0) continue;
                // Left and right of the centre line, in the model's space (x across, z along, y up).
                var left = new List<Vector3>();
                var right = new List<Vector3>();
                foreach (var v in vertices)
                {
                    var p = root.InverseTransformPoint(filter.transform.TransformPoint(v));
                    (p.x < 0f ? left : right).Add(p);
                }
                AddPoints(root, filter.transform, left, -1f, flares);
                AddPoints(root, filter.transform, right, 1f, flares);
            }
        }

        /// <summary>One side's points: its vertices split into rows along the hull, an empty at each row's middle.</summary>
        private static void AddPoints(Transform root, Transform part, List<Vector3> side, float sign, bool flares)
        {
            if (side.Count == 0) return;
            side.Sort((a, b) => a.z.CompareTo(b.z));
            var start = 0;
            for (var i = 1; i <= side.Count; i++)
            {
                if (i < side.Count && side[i].z - side[i - 1].z < EffectRowGap) continue;
                var mean = Vector3.zero;
                for (var j = start; j < i; j++) mean += side[j];
                mean /= i - start;
                start = i;
                var point = new GameObject(flares ? FlarePointName : ApsPointName).transform;
                point.SetParent(part, false);
                point.position = root.TransformPoint(mean);
                var look = flares ? new Vector3(sign, -1.2f, -0.3f) : new Vector3(sign * 0.4f, 1f, 0.5f);
                point.rotation = Quaternion.LookRotation(root.TransformDirection(look.normalized), root.up);
            }
        }
    }
}
