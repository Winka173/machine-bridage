#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 30 L6: one neutral site of a map ("neutrals": kind, x, z); its building is a prop of the map.</summary>
    public readonly struct NeutralSiteDef
    {
        public NeutralSiteDef(string kind, Vector2 at)
        {
            Kind = kind;
            At = at;
        }

        public string Kind { get; }
        public Vector2 At { get; }

        internal static IReadOnlyList<NeutralSiteDef> ParseAll(JsonObject root)
        {
            if (!root.Has("neutrals")) return Array.Empty<NeutralSiteDef>();
            var list = new List<NeutralSiteDef>();
            foreach (var n in root.Array("neutrals")) list.Add(new NeutralSiteDef(n.String("kind"), new Vector2(n.Float("x"), n.Float("z"))));
            return list;
        }
    }

    /// <summary>
    /// Prompt 30 L6 (sheet "Trung lập", the V1 rows): the neutral sites' numbers and which kinds each mode switches on
    /// (balance.json "neutrals"). Weather and night are the environment's, not neutral sites.
    /// </summary>
    public sealed class NeutralRules
    {
        private readonly Dictionary<string, float> _numbers = new();
        private readonly Dictionary<string, IReadOnlyList<string>> _modes = new();

        public float Get(string key, float fallback) => _numbers.TryGetValue(key, out var v) ? v : fallback;

        /// <summary>The kinds a mode tag switches on (none for a mode the data does not list).</summary>
        public IReadOnlyList<string> KindsFor(string? mode) =>
            mode != null && _modes.TryGetValue(mode, out var k) ? k : Array.Empty<string>();

        internal static NeutralRules Parse(JsonObject o)
        {
            var r = new NeutralRules();
            if (o.Has("numbers"))
            {
                var n = o.Object("numbers");
                foreach (var k in n.Keys) r._numbers[k] = n.Float(k);
            }
            if (o.Has("modes"))
            {
                var m = o.Object("modes");
                foreach (var k in m.Keys) r._modes[k] = m.StringArray(k);
            }
            return r;
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>Prompt 30 L6: balance.json "neutrals".</summary>
        public NeutralRules Neutrals { get; internal set; } = new();
    }
}
