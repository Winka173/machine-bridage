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

        // Prompt 17 B.4: a long battlefield's layered base opens more (balance.json "longLevels").
        private readonly List<(int small, int medium, int large, int utility)> _longLevels = new()
            { (4, 1, 0, 1), (5, 2, 1, 1), (6, 3, 1, 2), (7, 4, 2, 3), (8, 5, 3, 4) };
        public int MaxLevel => _levels.Count;

        /// <summary>Tower hardpoints of a size an HQ of this level (1-5) opens (<paramref name="layered"/>: on a long battlefield's layered base).</summary>
        public int Slots(int level, SlotSize size, bool layered = false)
        {
            var table = layered ? _longLevels : _levels;
            var l = table[Math.Clamp(level, 1, table.Count) - 1];
            return size switch { SlotSize.Small => l.small, SlotSize.Medium => l.medium, _ => l.large };
        }

        /// <summary>Utility modules an HQ of this level allows (<paramref name="layered"/>: on a layered base).</summary>
        public int UtilitySlots(int level, bool layered = false)
        {
            var table = layered ? _longLevels : _levels;
            return table[Math.Clamp(level, 1, table.Count) - 1].utility;
        }

        /// <summary>A layered base's forward strongpoints of a size (balance.json "longForward"): the loadout's towers over again.</summary>
        public int ForwardSlots(SlotSize size) => size switch { SlotSize.Small => LongForwardSmall, SlotSize.Medium => LongForwardMedium, _ => 0 };

        public int LongForwardSmall { get; internal set; } = 6;
        public int LongForwardMedium { get; internal set; } = 2;

        private readonly List<string> _roster = new();

        /// <summary>Prompt 32 L1: the player's tower cards, in the data's order ("base.roster"); empty: every tower def is a card.</summary>
        public IReadOnlyList<string> Roster => _roster;

        private readonly (int cp, float cooldown)[] _rebuild = { (2, 25f), (4, 40f), (7, 60f) };

        /// <summary>The air drop's fall when a size names none ("rebuild.delay").</summary>
        public float RebuildDelay { get; internal set; } = 4f;

        // Prompt 32 L2: the drop's fall by size ("rebuild.<size>.drop": 2.5 / 3.5 / 5 s); NaN: the delay above.
        private readonly float[] _drop = { float.NaN, float.NaN, float.NaN };

        /// <summary>Prompt 32 L2: no tower is flown back in while an enemy stands this close to its slot ("rebuild.enemyRadius").</summary>
        public float RebuildEnemyRadius { get; internal set; } = 20f;

        /// <summary>Prompt 32 L2: seconds into a Showdown match after which no tower is flown back in ("rebuild.showdownCutoff").</summary>
        public float ShowdownRebuildCutoff { get; internal set; } = 600f;

        /// <summary>Prompt 32 L2: the HQ's health share at which a side's cheapest fallen small or medium tower comes back free, once ("rebuild.hqRescue").</summary>
        public float HqRescueShare { get; internal set; } = 0.25f;
        public int OutpostCp { get; internal set; } = 6;
        public int OutpostSlots { get; internal set; } = 2;

        /// <summary>
        /// CP to fly a destroyed tower back in: its baseRebuildCP (prompt 32 L2, "rebuildCp", from Tools/balance/p32_tower_prices.py),
        /// else its size's. The balance value: every calculation reads it; what a side pays is <c>BaseSystem.RuntimeCostOf</c>.
        /// </summary>
        public int RebuildCost(VehicleDef tower) => tower.BaseRebuildCp > 0 ? tower.BaseRebuildCp : _rebuild[(int)(tower.Fort?.Size ?? SlotSize.Small)].cp;

        /// <summary>Prompt 32 L2: seconds a rebuilt tower's air drop takes to land, by its size.</summary>
        public float RebuildDrop(VehicleDef tower)
        {
            var d = _drop[(int)(tower.Fort?.Size ?? SlotSize.Small)];
            return float.IsNaN(d) ? RebuildDelay : d;
        }

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
            if (b.Has("longLevels"))
            {
                rules._longLevels.Clear();
                foreach (var l in b.Array("longLevels")) rules._longLevels.Add((l.Int("small", 4), l.Int("medium", 1), l.Int("large", 0), l.Int("utility", 1)));
                while (rules._longLevels.Count < rules._levels.Count) rules._longLevels.Add(rules._longLevels[rules._longLevels.Count - 1]);
            }
            if (b.Has("longForward"))
            {
                var f = b.Object("longForward");
                rules.LongForwardSmall = f.Int("small", 6);
                rules.LongForwardMedium = f.Int("medium", 2);
            }
            if (b.Has("roster")) rules._roster.AddRange(b.StringArray("roster"));
            if (b.Has("rebuild"))
            {
                var r = b.Object("rebuild");
                rules.RebuildDelay = r.Float("delay", 4f);
                rules.RebuildEnemyRadius = Math.Max(0f, r.Float("enemyRadius", 20f));
                rules.ShowdownRebuildCutoff = Math.Max(0f, r.Float("showdownCutoff", 600f));
                rules.HqRescueShare = Math.Clamp(r.Float("hqRescue", 0.25f), 0f, 1f);
                foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                {
                    var key = size.ToString().ToLowerInvariant();
                    if (!r.Has(key)) continue;
                    var o = r.Object(key);
                    rules._rebuild[(int)size] = (o.Int("cp", rules._rebuild[(int)size].cp), o.Float("cooldown", rules._rebuild[(int)size].cooldown));
                    if (o.Has("drop")) rules._drop[(int)size] = Math.Max(0.1f, o.Float("drop", 4f));
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
