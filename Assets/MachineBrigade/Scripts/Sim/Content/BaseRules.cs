#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>What a side's base is for in a mode (balance.json "base.roles").</summary>
    public enum BaseRole
    {
        /// <summary>No base (Survival, Boss Rush).</summary>
        None,

        /// <summary>The HQ cannot fall: a camp to lean on (Conquest, King of the Hill, Deathmatch).</summary>
        Anchor,

        /// <summary>The enemy's base is the objective (Assault, Siege): it can be shelled and destroyed.</summary>
        Target,

        /// <summary>The side loses when its HQ falls (Defend, Endless).</summary>
        Defend,
    }

    /// <summary>What a fortification is in a base loadout.</summary>
    public enum FortKind
    {
        Tower,
        Utility,
        Hq,
    }

    /// <summary>
    /// A structure's place in a base loadout (balance.json vehicle "fort"): what it costs in
    /// fortification points, its weight class (light 1-2, medium 3, heavy 4-5), and what kind of
    /// hardpoint it takes. Tower tiers and branches are a later step: <see cref="Tier"/> is kept for them.
    /// </summary>
    public sealed class FortDef
    {
        public FortDef(int points, string weight, FortKind kind)
        {
            Points = points;
            Weight = weight;
            Kind = kind;
        }

        public int Points { get; }
        public string Weight { get; }
        public FortKind Kind { get; }

        /// <summary>The tower's tier (1-10), for the tier system to come; 1 until then.</summary>
        public int Tier { get; internal set; } = 1;
    }

    /// <summary>
    /// The base rules (balance.json "base"): the HQ, what each HQ level allows, how a destroyed
    /// tower is flown back in, outposts, what the base is for in each mode, and how the AI picks
    /// its own base.
    /// </summary>
    public sealed class BaseRules
    {
        public string HqId { get; internal set; } = "headquarters";

        private readonly List<(int points, int utility)> _levels = new() { (6, 1), (8, 1), (10, 2), (12, 2), (14, 3) };
        public int MaxLevel => _levels.Count;

        /// <summary>Fortification points an HQ of this level (1-5) allows.</summary>
        public int Points(int level) => _levels[Math.Clamp(level, 1, _levels.Count) - 1].points;

        /// <summary>Utility modules an HQ of this level allows.</summary>
        public int UtilitySlots(int level) => _levels[Math.Clamp(level, 1, _levels.Count) - 1].utility;

        public float CpPerPoint { get; internal set; } = 1f;
        public float RebuildCooldown { get; internal set; } = 45f;
        public float RebuildDelay { get; internal set; } = 4f;
        public int OutpostCp { get; internal set; } = 6;
        public int OutpostSlots { get; internal set; } = 2;

        /// <summary>CP to fly a destroyed tower back in: its points times <see cref="CpPerPoint"/>, at least 1.</summary>
        public int RebuildCost(VehicleDef tower) => Math.Max(1, (int)MathF.Ceiling((tower.Fort?.Points ?? 1) * CpPerPoint));

        private readonly Dictionary<string, BaseRole> _roles = new(StringComparer.OrdinalIgnoreCase);

        /// <summary>What the base is for in a mode (by the mode's name, as in GameModeKind); None when the data does not say.</summary>
        public BaseRole RoleFor(string mode) => _roles.TryGetValue(mode, out var role) ? role : BaseRole.None;

        private readonly Dictionary<string, int> _aiLevels = new(StringComparer.OrdinalIgnoreCase) { ["Easy"] = 2, ["Normal"] = 3, ["Hard"] = 5 };

        /// <summary>The AI's HQ level at a difficulty (by name: Easy, Normal, Hard).</summary>
        public int AiLevel(string difficulty) => _aiLevels.TryGetValue(difficulty, out var level) ? level : 3;

        private readonly Dictionary<string, Dictionary<string, float>> _styles = new(StringComparer.OrdinalIgnoreCase);

        /// <summary>An AI base style: preference weights by tower id (a commander personality names its own).</summary>
        public IReadOnlyDictionary<string, float> Style(string name) =>
            _styles.TryGetValue(name, out var style) ? style : _styles.TryGetValue("default", out var fallback) ? fallback : new Dictionary<string, float>();

        public IEnumerable<string> StyleNames => _styles.Keys;

        internal static BaseRules Parse(JsonObject b)
        {
            var rules = new BaseRules();
            if (b.Has("hq")) rules.HqId = b.String("hq");
            if (b.Has("levels"))
            {
                rules._levels.Clear();
                foreach (var l in b.Array("levels")) rules._levels.Add((l.Int("points", 6), l.Int("utility", 1)));
            }
            if (b.Has("rebuild"))
            {
                var r = b.Object("rebuild");
                rules.CpPerPoint = r.Float("cpPerPoint", 1f);
                rules.RebuildCooldown = r.Float("cooldown", 45f);
                rules.RebuildDelay = r.Float("delay", 4f);
            }
            if (b.Has("outpost"))
            {
                var o = b.Object("outpost");
                rules.OutpostCp = o.Int("cp", 6);
                rules.OutpostSlots = o.Int("slots", 2);
            }
            if (b.Has("roles"))
            {
                var roles = b.Object("roles");
                foreach (var mode in roles.Keys) rules._roles[mode] = (BaseRole)Enum.Parse(typeof(BaseRole), roles.String(mode), true);
            }
            if (b.Has("ai"))
            {
                var ai = b.Object("ai");
                if (ai.Has("levels"))
                {
                    var levels = ai.Object("levels");
                    foreach (var key in levels.Keys) rules._aiLevels[key] = levels.Int(key, 3);
                }
                if (ai.Has("styles"))
                {
                    var styles = ai.Object("styles");
                    foreach (var name in styles.Keys)
                    {
                        var weights = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase);
                        var s = styles.Object(name);
                        foreach (var id in s.Keys) weights[id] = s.Float(id, 1f);
                        rules._styles[name] = weights;
                    }
                }
            }
            return rules;
        }
    }
}
