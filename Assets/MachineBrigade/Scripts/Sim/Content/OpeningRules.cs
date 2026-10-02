#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 32 L6: the starting CP's scale (balance.json "economy.startCp": every listed mode's starting CP x the scale,
    /// rounded half up, for the new prices) and the opening squads ("openingSquads"): a commander's (or an enemy
    /// general's) roles, each filled at tick 0 by the deck's cheapest card of the role (baseCP, then id), dropped as
    /// bought vehicles, their baseCP taken from the starting CP up to a share of it.
    /// </summary>
    public sealed class OpeningRules
    {
        /// <summary>The starting CP's factor in the modes listed (1: unchanged).</summary>
        public float StartCpScale { get; internal set; } = 1f;

        private readonly HashSet<string> _startCpModes = new(StringComparer.OrdinalIgnoreCase);

        /// <summary>The most of the starting CP an opening squad takes.</summary>
        public float Share { get; internal set; } = 0.6f;

        private readonly HashSet<string> _modes = new(StringComparer.OrdinalIgnoreCase);
        private readonly HashSet<string> _enemyModes = new(StringComparer.OrdinalIgnoreCase);

        /// <summary>A role's candidates: ids (in the data's order), or every card at most <c>MaxCp</c> baseCP (0: ids only).</summary>
        public sealed class Role
        {
            public IReadOnlyList<string> Ids { get; internal set; } = Array.Empty<string>();
            public int MaxCp { get; internal set; }
        }

        private readonly Dictionary<string, Role> _roles = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, IReadOnlyList<string>> _commanders = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, IReadOnlyList<string>> _generals = new(StringComparer.OrdinalIgnoreCase);

        public IReadOnlyDictionary<string, Role> Roles => _roles;
        public IReadOnlyDictionary<string, IReadOnlyList<string>> Commanders => _commanders;
        public IReadOnlyDictionary<string, IReadOnlyList<string>> Generals => _generals;

        /// <summary>The starting CP of a side in <paramref name="mode"/>: scaled and rounded half up where the mode is listed.</summary>
        public float StartCp(string? mode, float cp) =>
            mode != null && cp > 0f && StartCpScale != 1f && _startCpModes.Contains(mode) ? SimMath.RoundHalfUp(cp * (double)StartCpScale) : cp;

        /// <summary>Whether the player's side gets its commander's opening squad in a mode (by name, as GameModeKind).</summary>
        public bool AppliesTo(string? mode) => mode != null && _modes.Contains(mode);

        /// <summary>Whether the enemy's commander gets its general's opening squad in a mode.</summary>
        public bool EnemyAppliesTo(string? mode) => mode != null && _enemyModes.Contains(mode);

        /// <summary>A commander's roles (empty: none, or a commander the table does not name).</summary>
        public IReadOnlyList<string> CommanderRoles(string? commander) =>
            commander != null && _commanders.TryGetValue(commander, out var r) ? r : Array.Empty<string>();

        /// <summary>An enemy general's roles (by id or base style), else the table's "default".</summary>
        public IReadOnlyList<string> GeneralRoles(string? general) =>
            general != null && _generals.TryGetValue(general, out var r) ? r : _generals.TryGetValue("default", out var d) ? d : Array.Empty<string>();

        internal static OpeningRules Parse(JsonObject root)
        {
            var o = new OpeningRules();
            if (root.Has("economy") && root.Object("economy").Has("startCp"))
            {
                var s = root.Object("economy").Object("startCp");
                o.StartCpScale = Math.Max(0.1f, s.Float("scale", 1f));
                if (s.Has("modes")) foreach (var m in s.StringArray("modes")) o._startCpModes.Add(m);
            }
            if (!root.Has("openingSquads")) return o;
            var q = root.Object("openingSquads");
            o.Share = Math.Clamp(q.Float("share", 0.6f), 0f, 1f);
            if (q.Has("modes")) foreach (var m in q.StringArray("modes")) o._modes.Add(m);
            if (q.Has("enemyModes")) foreach (var m in q.StringArray("enemyModes")) o._enemyModes.Add(m);
            if (q.Has("roles"))
            {
                var roles = q.Object("roles");
                foreach (var key in roles.Keys)
                {
                    var role = new Role();
                    if (roles.IsArray(key)) role.Ids = roles.StringArray(key);
                    else role.MaxCp = Math.Max(0, roles.Object(key).Int("maxCp", 0));
                    o._roles[key] = role;
                }
            }
            void Table(string key, Dictionary<string, IReadOnlyList<string>> into)
            {
                if (!q.Has(key)) return;
                var t = q.Object(key);
                foreach (var id in t.Keys)
                {
                    var list = t.StringArray(id);
                    foreach (var r in list)
                        if (!o._roles.ContainsKey(r)) throw new FormatException($"openingSquads.{key}.{id}: unknown role '{r}'.");
                    into[id] = list;
                }
            }
            Table("commanders", o._commanders);
            Table("generals", o._generals);
            return o;
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>Prompt 32 L6: the starting CP's scale and the opening squads.</summary>
        public OpeningRules Opening { get; internal set; } = new();
    }
}
