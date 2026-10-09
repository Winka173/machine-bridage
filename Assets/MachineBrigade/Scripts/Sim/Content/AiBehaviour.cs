#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.AI;

namespace MachineBrigade.Sim.Content
{
    /// <summary>A squad state's row of the sheet "Trạng thái đội": its priority (1 low - 3 high) and minimum commitment.</summary>
    public readonly struct SquadStateDef
    {
        public SquadStateDef(int priority, float commit)
        {
            Priority = priority;
            Commit = commit;
        }

        public int Priority { get; }
        public float Commit { get; }
    }

    /// <summary>What a role does when overwhelmed (D.3: a short move in the fight, never a retreat on health).</summary>
    public enum OverwhelmedMove
    {
        Hold,
        Cover,
        Shift,
        Scoot,
        Smoke,
        Rearm,
    }

    /// <summary>A role of the sheet "Vai trò": engagement distance as a share of the weapon's reach, and its overwhelmed move.</summary>
    public sealed class RoleDef
    {
        public string Id { get; internal set; } = "";

        /// <summary>0 when the role has no band (artillery fires on spotting; support does not engage).</summary>
        public float EngageMin { get; internal set; }
        public float EngageMax { get; internal set; }
        public OverwhelmedMove Overwhelmed { get; internal set; }
    }

    /// <summary>A squad's fire stance (prompt 28 H.9).</summary>
    public enum FireStance
    {
        Free,
        Confirmed,
        HoldFire,
    }

    /// <summary>
    /// The shared behaviour modules a tactic turns on, off or tunes (prompt 28 H.1); 1 or false is the standard, so
    /// Balanced (no modules) plays the standard thresholds. Read from the sheet's "Tác động lên AI" by the generator.
    /// </summary>
    public sealed class TacticModules
    {
        /// <summary>Attack readiness: own/enemy strength to open an attack window; null: the parameter's.</summary>
        public float? AttackThreshold { get; internal set; }

        /// <summary>Squad cohesion: 1 fast vehicles wait for slow ones, 0 they do not.</summary>
        public float Cohesion { get; internal set; } = 1f;
        public float Flank { get; internal set; } = 1f;
        public bool Pincer { get; internal set; }
        public float Focus { get; internal set; } = 1f;

        /// <summary>Share of the army on the main effort; null: the parameter's.</summary>
        public float? MainEffort { get; internal set; }

        /// <summary>Multiplies the spread-out distance before splash.</summary>
        public float Spread { get; internal set; } = 1f;

        /// <summary>Holding fire until the enemy is inside this share of the reach (0: no hold).</summary>
        public float HoldFire { get; internal set; }
        public FireStance Stance { get; internal set; } = FireStance.Free;

        /// <summary>Engagement band as a share of reach (0: the role's).</summary>
        public float EngageMin { get; internal set; }
        public float EngageMax { get; internal set; }

        /// <summary>Back off when the enemy comes inside this share of the reach (0: never).</summary>
        public float Kite { get; internal set; }
        public int ArtilleryPrep { get; internal set; }

        /// <summary>Fall back to the line behind below this own/enemy ratio (0: no lines).</summary>
        public float Fallback { get; internal set; }
        public float Counterattack { get; internal set; }

        /// <summary>Advance pace (bounding overwatch moves about 30 % slower).</summary>
        public float Pace { get; internal set; } = 1f;
        public bool Bounding { get; internal set; }
        public bool Hold { get; internal set; }
        public bool HoldBase { get; internal set; }
        public bool WaitAir { get; internal set; }
        public bool CpSaving { get; internal set; }
        public bool Together { get; internal set; }
        public bool Standoff { get; internal set; }
        public bool HeavyLead { get; internal set; }
        public bool DropSecondary { get; internal set; }
        public bool SeadCards { get; internal set; }
        public bool MassSupport { get; internal set; }
        public IReadOnlyList<ForceGroup> Targets { get; internal set; } = Array.Empty<ForceGroup>();
        public string? TowerMode { get; internal set; }
    }

    /// <summary>One of the 16 tactics of the sheet "Chiến thuật".</summary>
    public sealed class TacticDef
    {
        public string Id { get; internal set; } = "";

        /// <summary>The sheet's (Vietnamese) name; the game's words are in the text tables.</summary>
        public string SheetName { get; internal set; } = "";

        /// <summary>Target share of CP spent per <see cref="ForceGroup"/> (sums to 1).</summary>
        public float[] Cp { get; internal set; } = new float[8];
        public IReadOnlyList<string> Prefer { get; internal set; } = Array.Empty<string>();
        public int Chapter { get; internal set; }
        public int Interlude { get; internal set; }
        public IReadOnlyList<string> Commanders { get; internal set; } = Array.Empty<string>();

        /// <summary>The tactic the sheet asks to check this one against for a merge (H.3); "" none.</summary>
        public string CheckWith { get; internal set; } = "";
        public TacticModules Modules { get; internal set; } = new();

        /// <summary>The tactics this one counters, and those that counter it (the sheet's columns; behaviour, not stats).</summary>
        public IReadOnlyList<string> Counters { get; internal set; } = Array.Empty<string>();
        public IReadOnlyList<string> CounteredBy { get; internal set; } = Array.Empty<string>();

        /// <summary>Set when the fingerprint measure merged it (H.3): the tactic it plays as.</summary>
        public string? MergedInto { get; internal set; }
    }

    /// <summary>A tower's default targeting mode and the ones a player may switch to (sheet "Công trình").</summary>
    public sealed class TowerModeDef
    {
        public TowerMode Mode { get; internal set; }
        public IReadOnlyList<TowerMode> Modes { get; internal set; } = Array.Empty<TowerMode>();
    }

    /// <summary>balance.json "aiBehaviour": squad states, roles, units, tactics, generals, tower modes, boss behaviour types.</summary>
    public sealed class AiBehaviour
    {
        private readonly Dictionary<string, TacticDef> _tactics = new(StringComparer.Ordinal);

        public SquadStateDef[] States { get; } = new SquadStateDef[7];
        public Dictionary<string, RoleDef> Roles { get; } = new(StringComparer.Ordinal);

        /// <summary>Vehicle id -> role id (sheet "Phương tiện").</summary>
        public Dictionary<string, string> Units { get; } = new(StringComparer.Ordinal);

        /// <summary>The tactics in the sheet's order.</summary>
        public List<TacticDef> Tactics { get; } = new();
        public Dictionary<string, string> Generals { get; } = new(StringComparer.Ordinal);
        public Dictionary<string, TowerModeDef> Towers { get; } = new(StringComparer.Ordinal);
        public Dictionary<string, IReadOnlyList<BossBehaviour>> Bosses { get; } = new(StringComparer.Ordinal);

        /// <summary>A tactic by id, following a merge (H.3); Balanced (or an empty one) for an unknown id.</summary>
        public TacticDef Tactic(string? id)
        {
            for (var depth = 0; depth < 4 && id != null && _tactics.TryGetValue(id, out var t); depth++)
            {
                if (t.MergedInto == null) return t;
                id = t.MergedInto;
            }
            return _tactics.TryGetValue("balanced", out var b) ? b : Balanced;
        }

        public bool HasTactic(string id) => _tactics.ContainsKey(id);

        /// <summary>A general's preferred tactic (H.7): by general id with or without "gen.", else the default.</summary>
        public string GeneralTactic(string? general)
        {
            var key = general == null ? "default" : general.StartsWith("gen.", StringComparison.Ordinal) ? general.Substring(4) : general;
            return Generals.TryGetValue(key, out var t) ? t : Generals.TryGetValue("default", out var d) ? d : "balanced";
        }

        /// <summary>H.11: open from chapter 1 (Balanced, Defence in depth, Base defence), else at its chapter or interlude.</summary>
        public static bool Unlocked(TacticDef t, int chapterReached, int interludesReached) =>
            t.Chapter <= 1 && t.Interlude == 0 || (t.Chapter > 0 && chapterReached >= t.Chapter) || (t.Interlude > 0 && interludesReached >= t.Interlude);

        /// <summary>H.12: the 1-2 tactics that suit a commander (the sheet's "Hợp chỉ huy"), in the sheet's order.</summary>
        public List<TacticDef> SuitedTo(string commanderId)
        {
            var list = new List<TacticDef>();
            foreach (var t in Tactics)
                if (t.MergedInto == null && list.Count < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiBehaviour.SuitedToCountMax)
                    foreach (var c in t.Commanders)
                        if (c == commanderId)
                        {
                            list.Add(t);
                            break;
                        }
            return list;
        }

        public RoleDef? RoleOf(string unitId) => Units.TryGetValue(unitId, out var r) && Roles.TryGetValue(r, out var role) ? role : null;

        private static readonly TacticDef Balanced = new() { Id = "balanced", Cp = new[] { 0.25f, 0.2f, 0.12f, 0.12f, 0.1f, 0.08f, 0.05f, 0.08f } };

        internal static AiBehaviour Parse(JsonObject o)
        {
            var b = new AiBehaviour();
            for (var i = 0; i < b.States.Length; i++) b.States[i] = new SquadStateDef(global::MachineBrigade.Sim.Content.SimTunables.Ai.AiBehaviour.ParsePriority, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiBehaviour.ParseCommit);
            if (o.Has("states"))
                foreach (var kv in o.Object("states").Raw)
                    if (Enum.TryParse<SquadState>(kv.Key, true, out var s))
                    {
                        var e = new JsonObject(kv.Value, "aiBehaviour.states." + kv.Key);
                        b.States[(int)s] = new SquadStateDef(e.Int("priority", 2), e.Float("commit", 4f));
                    }
            if (o.Has("roles"))
                foreach (var kv in o.Object("roles").Raw)
                {
                    var e = new JsonObject(kv.Value, "aiBehaviour.roles." + kv.Key);
                    var band = e.FloatArray("engage");
                    b.Roles[kv.Key] = new RoleDef
                    {
                        Id = kv.Key, EngageMin = band.Count == 2 ? band[0] : 0f, EngageMax = band.Count == 2 ? band[1] : 0f,
                        Overwhelmed = e.Enum("overwhelmed", OverwhelmedMove.Hold),
                    };
                }
            if (o.Has("units"))
                foreach (var kv in o.Object("units").Raw)
                    if (kv.Value is string role) b.Units[kv.Key] = role;
            if (o.Has("tactics"))
                foreach (var t in o.Array("tactics"))
                {
                    var cp = t.FloatArray("cp");
                    if (cp.Count != 8) throw new FormatException($"{t.Path}: cp needs the 8 force groups.");
                    var def = new TacticDef
                    {
                        Id = t.String("id"), SheetName = t.OptionalString("name") ?? "", Cp = new float[8],
                        Prefer = t.Has("prefer") ? t.StringArray("prefer") : Array.Empty<string>(),
                        Chapter = t.Int("chapter", 0), Interlude = t.Int("interlude", 0),
                        Commanders = t.Has("commanders") ? t.StringArray("commanders") : Array.Empty<string>(),
                        CheckWith = t.OptionalString("checkWith") ?? "",
                        Counters = t.Has("counters") ? t.StringArray("counters") : Array.Empty<string>(),
                        CounteredBy = t.Has("counteredBy") ? t.StringArray("counteredBy") : Array.Empty<string>(),
                        Modules = t.Has("modules") ? Modules(t.Object("modules")) : new TacticModules(),
                    };
                    for (var i = 0; i < 8; i++) def.Cp[i] = cp[i];
                    b.Tactics.Add(def);
                    b._tactics[def.Id] = def;
                }
            if (o.Has("generals"))
                foreach (var kv in o.Object("generals").Raw)
                    if (kv.Value is string t) b.Generals[kv.Key] = t;
            if (o.Has("towers"))
                foreach (var kv in o.Object("towers").Raw)
                {
                    var e = new JsonObject(kv.Value, "aiBehaviour.towers." + kv.Key);
                    var modes = new List<TowerMode>();
                    if (e.Has("modes"))
                        foreach (var m in e.StringArray("modes"))
                            if (Enum.TryParse<TowerMode>(m, out var mode)) modes.Add(mode);
                    b.Towers[kv.Key] = new TowerModeDef { Mode = e.Enum("mode", TowerMode.Nearest), Modes = modes };
                }
            if (o.Has("bosses"))
                foreach (var kv in o.Object("bosses").Raw)
                {
                    var kinds = new List<BossBehaviour>();
                    if (kv.Value is List<object?> list)
                        foreach (var item in list)
                            if (item is string s && Enum.TryParse<BossBehaviour>(s, out var k)) kinds.Add(k);
                    b.Bosses[kv.Key] = kinds;
                }
            return b;
        }

        private static TacticModules Modules(JsonObject m)
        {
            var engage = m.Has("engage") ? m.FloatArray("engage") : Array.Empty<float>();
            var targets = new List<ForceGroup>();
            if (m.Has("targets"))
                foreach (var g in m.StringArray("targets"))
                    if (Enum.TryParse<ForceGroup>(g, out var group)) targets.Add(group);
            return new TacticModules
            {
                AttackThreshold = m.Has("attackThreshold") ? m.Float("attackThreshold") : null,
                Cohesion = m.Float("cohesion", 1f), Flank = m.Float("flank", 1f), Pincer = m.Float("pincer", 0f) > 0f,
                Focus = m.Float("focus", 1f), MainEffort = m.Has("mainEffort") ? m.Float("mainEffort") : null,
                Spread = m.Float("spread", 1f), HoldFire = m.Float("holdFire", 0f), Stance = m.Enum("stance", FireStance.Free),
                EngageMin = engage.Count == 2 ? engage[0] : 0f, EngageMax = engage.Count == 2 ? engage[1] : 0f,
                Kite = m.Float("kite", 0f), ArtilleryPrep = (int)m.Float("artilleryPrep", 0f), Fallback = m.Float("fallback", 0f),
                Counterattack = m.Float("counterattack", 0f), Pace = m.Float("pace", 1f), Bounding = m.Float("bounding", 0f) > 0f,
                Hold = m.Float("hold", 0f) > 0f, HoldBase = m.Float("holdBase", 0f) > 0f, WaitAir = m.Float("waitAir", 0f) > 0f,
                CpSaving = m.Float("cpSaving", 0f) > 0f, Together = m.Float("together", 0f) > 0f, Standoff = m.Float("standoff", 0f) > 0f,
                HeavyLead = m.Float("heavyLead", 0f) > 0f, DropSecondary = m.Float("dropSecondary", 0f) > 0f,
                SeadCards = m.Float("seadCards", 0f) > 0f, MassSupport = m.Float("massSupport", 0f) > 0f,
                Targets = targets, TowerMode = m.OptionalString("towerMode"),
            };
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>The behaviour data of prompt 28 (balance.json "aiBehaviour").</summary>
        public AiBehaviour AiData { get; internal set; } = new();
    }
}
