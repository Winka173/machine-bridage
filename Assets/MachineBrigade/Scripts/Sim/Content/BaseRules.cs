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
    /// A structure's place in a base loadout (balance.json vehicle "fort"): its size class (it goes
    /// into a hardpoint of that size or bigger) and what kind of hardpoint it takes.
    /// </summary>
    public sealed class FortDef
    {
        public FortDef(SlotSize size, FortKind kind)
        {
            Size = size;
            Kind = kind;
        }

        public SlotSize Size { get; }
        public FortKind Kind { get; }

        /// <summary>Whether it goes into a hardpoint of this size (small towers anywhere, large ones only into large).</summary>
        public bool Fits(SlotSize slot) => Size <= slot;

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

        private readonly List<(int small, int medium, int large, int utility)> _levels = new()
            { (3, 1, 0, 1), (4, 2, 0, 1), (4, 2, 1, 2), (5, 3, 1, 2), (6, 3, 2, 3) };
        public int MaxLevel => _levels.Count;

        /// <summary>Tower hardpoints of a size an HQ of this level (1-5) opens.</summary>
        public int Slots(int level, SlotSize size)
        {
            var l = _levels[Math.Clamp(level, 1, _levels.Count) - 1];
            return size switch { SlotSize.Small => l.small, SlotSize.Medium => l.medium, _ => l.large };
        }

        /// <summary>Utility modules an HQ of this level allows.</summary>
        public int UtilitySlots(int level) => _levels[Math.Clamp(level, 1, _levels.Count) - 1].utility;

        private readonly (int cp, float cooldown)[] _rebuild = { (2, 25f), (4, 40f), (7, 60f) };
        public float RebuildDelay { get; internal set; } = 4f;
        public int OutpostCp { get; internal set; } = 6;
        public int OutpostSlots { get; internal set; } = 2;

        /// <summary>CP to fly a destroyed tower back in, by its size.</summary>
        public int RebuildCost(VehicleDef tower) => _rebuild[(int)(tower.Fort?.Size ?? SlotSize.Small)].cp;

        /// <summary>Seconds after a tower falls (or was last called) before it can be flown back in, by its size.</summary>
        public float RebuildCooldown(VehicleDef tower) => _rebuild[(int)(tower.Fort?.Size ?? SlotSize.Small)].cooldown;

        private readonly Dictionary<string, BaseRole> _roles = new(StringComparer.OrdinalIgnoreCase);

        /// <summary>What the base is for in a mode (by the mode's name, as in GameModeKind); None when the data does not say.</summary>
        public BaseRole RoleFor(string mode) => _roles.TryGetValue(mode, out var role) ? role : BaseRole.None;

        private readonly Dictionary<string, int> _aiLevels = new(StringComparer.OrdinalIgnoreCase) { ["Easy"] = 2, ["Normal"] = 3, ["Hard"] = 5, ["VeryHard"] = 5 };

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
                foreach (var l in b.Array("levels")) rules._levels.Add((l.Int("small", 3), l.Int("medium", 1), l.Int("large", 0), l.Int("utility", 1)));
            }
            if (b.Has("rebuild"))
            {
                var r = b.Object("rebuild");
                rules.RebuildDelay = r.Float("delay", 4f);
                foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                {
                    var key = size.ToString().ToLowerInvariant();
                    if (!r.Has(key)) continue;
                    var o = r.Object(key);
                    rules._rebuild[(int)size] = (o.Int("cp", rules._rebuild[(int)size].cp), o.Float("cooldown", rules._rebuild[(int)size].cooldown));
                }
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
