using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// MVA W1-B (spec part W, DECISIONS "Map/visual/audio W1-B (lane B)"): the runtime node contract, the C# twin of
    /// Tools/assets/runtime_nodes.py. Gameplay looks a model's nodes up by name: <c>Muzzle_&lt;slot&gt;</c>,
    /// <c>Mount_&lt;slot&gt;</c> and <c>Part_&lt;name&gt;</c> are indexed (the k-th mount of a slot in the data is the k-th node of
    /// the slot in canonical order; a boss part names its node in the data). Stable names carry a semantic tag, never a
    /// Blender duplicate suffix:
    /// <code>&lt;Kind&gt;_&lt;slot&gt;[_&lt;tag&gt;[_&lt;tag&gt;]]   tag = L | C | R | fore | mid | aft | 01..99</code>
    /// e.g. Muzzle_rocket + Muzzle_rocket_L, Mount_mg + Mount_mg_02 + Mount_mg_03. Tags are case-sensitive (Part_aa_l and
    /// Muzzle_door_l are older lower-case names, not tags); a tagged Mount_Flare_* is a flare point, never a weapon mount.
    /// Canonical order in a slot: the plain name, then by tag (fore &lt; mid &lt; aft, L &lt; C &lt; R, 01 &lt; 02), then a
    /// legacy ".NNN" by number, which for legacy names alone is the old ordinal order: a GLB not yet renamed resolves
    /// exactly as before (the resolver keeps old GLBs working until they are rebuilt).
    /// </summary>
    public static class RuntimeNodes
    {
        /// <summary>One or two semantic tags (case-sensitive inside the otherwise case-blind patterns).</summary>
        public const string Tag = @"(?-i:(?:_(?:L|R|C|fore|mid|aft|\d{2})){1,2})";

        /// <summary>The muzzle slots the runtime knows (VehicleView's mounts name one of these).</summary>
        public const string MuzzleSlots = "main|coax|mg|missile|rocket|gun|aam|door_l|door_r|ramp|agl_l|agl_r|mortar";

        /// <summary>Muzzle_&lt;slot&gt;[tags][.NNN]: group 1 the slot, 2 the tags, 3 a legacy suffix.</summary>
        public static readonly Regex Muzzle = new(@"^Muzzle_(" + MuzzleSlots + ")(" + Tag + @")?(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>Mount_&lt;slot&gt;[tags][.NNN]; Mount_Flare_* (flare points) never.</summary>
        public static readonly Regex Mount = new(@"^Mount_(?!flare_)([a-z]+)(" + Tag + @")?(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>Part_&lt;name&gt;[tags][.NNN] (a boss's breakable part, a crash piece).</summary>
        public static readonly Regex Part = new(@"^Part_([a-z]+)(" + Tag + @")?(\.\d+)?$", RegexOptions.IgnoreCase);

        private static readonly Regex Legacy = new(@"\.\d+$");

        public enum Kind
        {
            None,
            Muzzle,
            Mount,
            Part,
        }

        /// <summary>An indexed runtime node's name taken apart.</summary>
        public readonly struct Name
        {
            public Name(Kind kind, string slot, string[] tags, int suffix)
            {
                Kind = kind;
                Slot = slot;
                Tags = tags;
                Suffix = suffix;
            }

            public Kind Kind { get; }

            /// <summary>Lower-case slot (mg, gun, engine ...).</summary>
            public string Slot { get; }

            public string[] Tags { get; }

            /// <summary>The legacy Blender suffix's number (Muzzle_mg.002: 2), -1 without one.</summary>
            public int Suffix { get; }

            public bool Valid => Kind != Kind.None;
            public bool Plain => Tags.Length == 0 && Suffix < 0;
            public bool LegacySuffixed => Suffix >= 0;
        }

        public static Name Parse(string name)
        {
            if (string.IsNullOrEmpty(name)) return default;
            if (TryParse(Muzzle, Kind.Muzzle, name, out var n) || TryParse(Mount, Kind.Mount, name, out n) || TryParse(Part, Kind.Part, name, out n))
                return n;
            return new Name(Kind.None, null, Array.Empty<string>(), -1);
        }

        private static bool TryParse(Regex pattern, Kind kind, string name, out Name parsed)
        {
            var m = pattern.Match(name);
            if (!m.Success)
            {
                parsed = default;
                return false;
            }
            var tags = m.Groups[2].Success ? m.Groups[2].Value.Split(new[] { '_' }, StringSplitOptions.RemoveEmptyEntries) : Array.Empty<string>();
            var suffix = m.Groups[3].Success ? int.Parse(m.Groups[3].Value.Substring(1)) : -1;
            parsed = new Name(kind, m.Groups[1].Value.ToLowerInvariant(), tags, suffix);
            return true;
        }

        /// <summary>Whether a runtime lookup would depend on a Blender suffix here (an indexed node named Muzzle_mg.001).</summary>
        public static bool IsLegacySuffixed(string name) => Parse(name).LegacySuffixed;

        /// <summary>A tag's place: (class, value); position before side before index.</summary>
        private static (int cls, int value) TagRank(string tag) => tag switch
        {
            "fore" => (0, 0),
            "mid" => (0, 1),
            "aft" => (0, 2),
            "L" => (1, 0),
            "C" => (1, 1),
            "R" => (1, 2),
            _ => (2, int.TryParse(tag, out var i) ? i : 99),
        };

        /// <summary>Canonical order of two nodes of one slot (the plain name first, tags, then a legacy suffix; see the class).</summary>
        public static int Compare(string a, string b)
        {
            var x = Parse(a);
            var y = Parse(b);
            if (!x.Valid || !y.Valid) return string.CompareOrdinal(a, b);
            var n = Math.Min(x.Tags.Length, y.Tags.Length);
            for (var i = 0; i < n; i++)
            {
                var (xc, xv) = TagRank(x.Tags[i]);
                var (yc, yv) = TagRank(y.Tags[i]);
                if (xc != yc) return xc.CompareTo(yc);
                if (xv != yv) return xv.CompareTo(yv);
            }
            if (x.Tags.Length != y.Tags.Length) return x.Tags.Length.CompareTo(y.Tags.Length);
            if (x.Suffix != y.Suffix) return x.Suffix.CompareTo(y.Suffix);
            return string.CompareOrdinal(a, b);
        }

        /// <summary>Sorts a slot's nodes into canonical order (the k-th is the data's k-th mount of the slot).</summary>
        public static void Sort(List<Transform> nodes) => nodes.Sort((a, b) => Compare(a.name, b.name));

        /// <summary>
        /// Whether <paramref name="name"/> is one of the nodes a lookup of <paramref name="wanted"/> stands for: the name
        /// itself, a tagged or legacy-suffixed node of the same plain runtime name (Part_wheel: Part_wheel_L, Part_wheel.001),
        /// or any other node with Blender's suffix (Rotor: Rotor.001), as the older lookups took.
        /// </summary>
        public static bool Matches(string name, string wanted)
        {
            if (name == null || wanted == null) return false;
            if (name == wanted) return true;
            var w = Parse(wanted);
            if (w.Valid && w.Plain)
            {
                var n = Parse(name);
                return n.Valid && n.Kind == w.Kind && n.Slot == w.Slot && string.Equals(Stem(name), Stem(wanted), StringComparison.OrdinalIgnoreCase);
            }
            return name.StartsWith(wanted + ".", StringComparison.Ordinal) && Legacy.IsMatch(name);
        }

        /// <summary>The name without tags and suffix (Muzzle_mg_R.001: Muzzle_mg).</summary>
        private static string Stem(string name)
        {
            var bare = Legacy.Replace(name, string.Empty);
            return Regex.Replace(bare, Tag + "$", string.Empty);
        }

        /// <summary>
        /// The first node under <paramref name="root"/> a lookup of <paramref name="wanted"/> stands for (see <see cref="Matches"/>),
        /// in canonical order: the plain name when the model has it. Null when none.
        /// </summary>
        public static Transform Find(Transform root, string wanted)
        {
            if (root == null) return null;
            Transform best = null;
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (t == root || !Matches(t.name, wanted)) continue;
                if (t.name == wanted) return t;
                if (best == null || Compare(t.name, best.name) < 0) best = t;
            }
            return best;
        }
    }
}
